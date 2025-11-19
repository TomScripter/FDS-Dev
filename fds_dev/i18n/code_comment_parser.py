from __future__ import annotations

import ast
import codecs
import os
import tokenize
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass
class CommentNode:
    node_type: str
    content: str
    line_number: int
    column_offset: int
    context: str
    raw_fragment: str
    start_offset: int
    end_offset: int
    translated: str = ""


@dataclass
class ParsedCodeFile:
    file_path: str
    encoding: str
    original_lines: List[str]
    comments: List[CommentNode] = field(default_factory=list)
    docstrings: List[CommentNode] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.original_text = "".join(self.original_lines)

    def get_all_translatable(self) -> List[CommentNode]:
        return self.comments + self.docstrings

    def total_nodes(self) -> int:
        return len(self.get_all_translatable())

    def reconstruct_file(self) -> str:
        updated = self.original_text
        nodes = [node for node in self.get_all_translatable() if node.translated]
        nodes.sort(key=lambda node: node.start_offset, reverse=True)
        for node in nodes:
            replacement = self._render_fragment(node)
            if node.start_offset < 0 or node.end_offset > len(updated):
                continue
            updated = updated[: node.start_offset] + replacement + updated[node.end_offset :]
        return updated

    @staticmethod
    def _render_fragment(node: CommentNode) -> str:
        if not node.translated:
            return node.raw_fragment
        if node.content:
            return node.raw_fragment.replace(node.content, node.translated, 1)
        return node.translated


class _DocstringCollector(ast.NodeVisitor):
    def __init__(self, text: str, line_offsets: List[int]) -> None:
        self.text = text
        self.line_offsets = line_offsets
        self.docstrings: List[CommentNode] = []

    def visit_Module(self, node: ast.Module) -> None:
        self._capture_docstring(node, "module")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._capture_docstring(node, "function")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._capture_docstring(node, "function")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._capture_docstring(node, "class")
        self.generic_visit(node)

    def _capture_docstring(self, node: ast.AST, context: str) -> None:
        body = getattr(node, "body", None)
        if not body:
            return
        first = body[0]
        if not isinstance(first, ast.Expr):
            return
        value = first.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            return
        lineno = getattr(first, "lineno", 1)
        col_offset = getattr(first, "col_offset", 0)
        end_lineno = getattr(value, "end_lineno", lineno)
        end_col = getattr(value, "end_col_offset", col_offset)
        start_idx = self._safe_offset(lineno, col_offset)
        end_idx = self._safe_offset(end_lineno, end_col)
        fragment = self.text[start_idx:end_idx]
        node_record = CommentNode(
            node_type="docstring",
            content=value.value,
            line_number=lineno,
            column_offset=col_offset,
            context=context,
            raw_fragment=fragment,
            start_offset=start_idx,
            end_offset=end_idx,
        )
        self.docstrings.append(node_record)

    def _safe_offset(self, lineno: int, col: int) -> int:
        if lineno - 1 >= len(self.line_offsets):
            return len(self.text)
        return self.line_offsets[lineno - 1] + col


class CodeCommentParser:
    MARKDOWN_EXT = {".md", ".markdown"}
    PYTHON_EXT = {".py"}

    def parse_file(self, path: str) -> ParsedCodeFile:
        target = Path(path)
        if not target.exists():
            raise FileNotFoundError(path)
        raw = target.read_bytes()
        encoding = "utf-8-sig" if raw.startswith(codecs.BOM_UTF8) else "utf-8"
        text = raw.decode(encoding, errors="ignore")
        lines = text.splitlines(keepends=True)
        if not lines:
            lines = [""]
        line_offsets = self._line_offsets(lines)
        ext = target.suffix.lower()
        if ext in self.PYTHON_EXT:
            comments = self._parse_python_comments(text, lines, line_offsets)
            docstrings = self._parse_docstrings(text, line_offsets)
        elif ext in self.MARKDOWN_EXT:
            comments = []
            docstrings = self._parse_markdown_paragraphs(lines, line_offsets, text)
        else:
            comments = []
            docstrings = []
        return ParsedCodeFile(
            file_path=str(target),
            encoding=encoding,
            original_lines=lines,
            comments=comments,
            docstrings=docstrings,
        )

    def parse_directory(self, directory: str, recursive: bool = True) -> Dict[str, ParsedCodeFile]:
        root = Path(directory)
        if not root.is_dir():
            raise NotADirectoryError(directory)
        results: Dict[str, ParsedCodeFile] = {}
        walker: Iterable[Tuple[str, List[str], List[str]]] = os.walk(root)
        for current, dirs, files in walker:
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                file_path = Path(current) / name
                if file_path.suffix.lower() not in (self.PYTHON_EXT | self.MARKDOWN_EXT):
                    continue
                try:
                    results[str(file_path)] = self.parse_file(str(file_path))
                except Exception:
                    continue
            if not recursive:
                break
        return results

    def reconstruct_file(self, parsed: ParsedCodeFile) -> str:
        return parsed.reconstruct_file()

    def _parse_python_comments(
        self, text: str, lines: List[str], line_offsets: List[int]
    ) -> List[CommentNode]:
        nodes: List[CommentNode] = []
        reader = StringIO(text).readline
        try:
            token_stream = tokenize.generate_tokens(reader)
            for token in token_stream:
                if token.type != tokenize.COMMENT:
                    continue
                (line_no, column) = token.start
                if line_no - 1 >= len(lines):
                    continue
                raw_line = lines[line_no - 1].rstrip("\n")
                start_offset = line_offsets[line_no - 1] + column
                end_offset = line_offsets[line_no - 1] + len(raw_line)
                comment_body = token.string.lstrip("#").strip()
                node = CommentNode(
                    node_type="comment",
                    content=comment_body,
                    line_number=line_no,
                    column_offset=column,
                    context="inline comment",
                    raw_fragment=raw_line[column:],
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
                nodes.append(node)
        except tokenize.TokenError:
            return nodes
        return nodes

    def _parse_docstrings(self, text: str, line_offsets: List[int]) -> List[CommentNode]:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []
        collector = _DocstringCollector(text, line_offsets)
        collector.visit(tree)
        return collector.docstrings

    def _parse_markdown_paragraphs(
        self, lines: List[str], line_offsets: List[int], text: str
    ) -> List[CommentNode]:
        nodes: List[CommentNode] = []
        paragraph: List[str] = []
        start_idx = 0
        for idx, line in enumerate(lines):
            if line.strip():
                if not paragraph:
                    start_idx = idx
                paragraph.append(line)
            else:
                if paragraph:
                    nodes.append(
                        self._mk_markdown_node(paragraph, start_idx, idx - 1, line_offsets, text)
                    )
                    paragraph = []
        if paragraph:
            nodes.append(self._mk_markdown_node(paragraph, start_idx, len(lines) - 1, line_offsets, text))
        return nodes

    def _mk_markdown_node(
        self,
        block: List[str],
        start_idx: int,
        end_idx: int,
        line_offsets: List[int],
        text: str,
    ) -> CommentNode:
        if end_idx < start_idx:
            end_idx = start_idx
        start_offset = line_offsets[start_idx]
        end_offset = line_offsets[end_idx] + len(block[-1])
        fragment = text[start_offset:end_offset]
        return CommentNode(
            node_type="markdown",
            content="".join(block).strip(),
            line_number=start_idx + 1,
            column_offset=0,
            context="markdown paragraph",
            raw_fragment=fragment,
            start_offset=start_offset,
            end_offset=end_offset,
        )

    @staticmethod
    def _line_offsets(lines: List[str]) -> List[int]:
        offsets: List[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line)
        return offsets
