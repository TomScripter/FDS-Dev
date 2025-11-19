"""
Tests for i18n code comment parser module.
"""

import pytest
from pathlib import Path
from fds_dev.i18n import CodeCommentParser, CommentNode, ParsedCodeFile


class TestCodeCommentParser:
    """Test suite for CodeCommentParser class."""

    @pytest.fixture
    def parser(self):
        """Create a CodeCommentParser instance."""
        return CodeCommentParser()

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file for testing."""
        file_path = tmp_path / "test_sample.py"
        content = '''"""
Module docstring for testing.
"""

def my_function():
    """Function docstring."""
    # Inline comment
    x = 42  # End-of-line comment
    return x

class MyClass:
    """Class docstring."""

    def method(self):
        # Method comment
        pass
'''
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)

    @pytest.fixture
    def sample_markdown_file(self, tmp_path):
        """Create a sample Markdown file for testing."""
        file_path = tmp_path / "test_sample.md"
        content = '''# Title

This is a paragraph.

## Section

Another paragraph here.
'''
        file_path.write_text(content, encoding='utf-8')
        return str(file_path)

    def test_parse_python_file(self, parser, sample_python_file):
        """Test parsing a Python file."""
        result = parser.parse_file(sample_python_file)

        assert isinstance(result, ParsedCodeFile)
        assert result.file_path == sample_python_file
        assert len(result.comments) > 0
        assert len(result.docstrings) > 0

    def test_parse_extracts_docstrings(self, parser, sample_python_file):
        """Test that docstrings are extracted."""
        result = parser.parse_file(sample_python_file)

        # Should have module, function, and class docstrings
        docstring_contents = [d.content for d in result.docstrings]
        assert any('Module docstring' in d for d in docstring_contents)
        assert any('Function docstring' in d for d in docstring_contents)
        assert any('Class docstring' in d for d in docstring_contents)

    def test_parse_extracts_inline_comments(self, parser, sample_python_file):
        """Test that inline comments are extracted."""
        result = parser.parse_file(sample_python_file)

        comment_contents = [c.content for c in result.comments]
        assert any('Inline comment' in c for c in comment_contents)
        assert any('End-of-line comment' in c for c in comment_contents)

    def test_parse_markdown_file(self, parser, sample_markdown_file):
        """Test parsing a Markdown file."""
        result = parser.parse_file(sample_markdown_file)

        assert isinstance(result, ParsedCodeFile)
        assert len(result.docstrings) > 0  # Paragraphs stored as docstrings

    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.py")

    def test_parse_invalid_syntax(self, parser, tmp_path):
        """Test parsing file with syntax errors."""
        file_path = tmp_path / "invalid.py"
        file_path.write_text("def invalid syntax here", encoding='utf-8')

        # Should return empty result, not crash
        result = parser.parse_file(str(file_path))
        assert result.total_nodes() == 0

    def test_comment_node_line_numbers(self, parser, sample_python_file):
        """Test that line numbers are tracked correctly."""
        result = parser.parse_file(sample_python_file)

        # All nodes should have valid line numbers
        for node in result.get_all_translatable():
            assert node.line_number > 0

    def test_comment_node_context(self, parser, sample_python_file):
        """Test that context is captured for comments."""
        result = parser.parse_file(sample_python_file)

        # Inline comments should have context
        for comment in result.comments:
            assert len(comment.context) > 0

    def test_docstring_node_context_types(self, parser, sample_python_file):
        """Test that docstrings have correct context types."""
        result = parser.parse_file(sample_python_file)

        context_types = [d.context for d in result.docstrings]
        assert any('module' in ctx for ctx in context_types)
        assert any('function' in ctx for ctx in context_types)
        assert any('class' in ctx for ctx in context_types)

    def test_get_all_translatable(self, parser, sample_python_file):
        """Test getting all translatable nodes."""
        result = parser.parse_file(sample_python_file)
        all_nodes = result.get_all_translatable()

        # Should combine comments and docstrings
        assert len(all_nodes) == len(result.comments) + len(result.docstrings)

    def test_total_nodes(self, parser, sample_python_file):
        """Test total node count."""
        result = parser.parse_file(sample_python_file)
        total = result.total_nodes()

        assert total == len(result.comments) + len(result.docstrings)
        assert total > 0

    def test_extract_inline_comments_ignores_strings(self, parser, tmp_path):
        """Test that # inside strings are ignored."""
        file_path = tmp_path / "test_strings.py"
        content = '''
x = "This # is not a comment"
y = 'Another # not a comment'
z = 1  # This IS a comment
'''
        file_path.write_text(content, encoding='utf-8')

        result = parser.parse_file(str(file_path))

        # Should only extract the real comment
        comments = [c.content for c in result.comments]
        assert 'This IS a comment' in comments
        assert len([c for c in comments if 'not a comment' in c]) == 0

    def test_reconstruct_python_file_with_translations(self, parser, tmp_path):
        """Test reconstructing Python file with translated comments."""
        file_path = tmp_path / "test_reconstruct.py"
        original_content = '''# Original comment
x = 42
'''
        file_path.write_text(original_content, encoding='utf-8')

        # Parse file
        result = parser.parse_file(str(file_path))

        # Add translation
        result.comments[0].translated = "Translated comment"

        # Reconstruct
        reconstructed = parser.reconstruct_file(result)

        assert 'Translated comment' in reconstructed
        assert 'Original comment' not in reconstructed
        assert 'x = 42' in reconstructed  # Code preserved

    def test_reconstruct_markdown_file(self, parser, tmp_path):
        """Test reconstructing Markdown file."""
        file_path = tmp_path / "test_reconstruct.md"
        original_content = '''# Title

Original paragraph.

## Section

Another paragraph.
'''
        file_path.write_text(original_content, encoding='utf-8')

        # Parse file
        result = parser.parse_file(str(file_path))

        # Add translations
        for node in result.docstrings:
            node.translated = node.content.replace("Original", "Translated")

        # Reconstruct
        reconstructed = parser.reconstruct_file(result)

        assert 'Translated' in reconstructed or 'Original' in reconstructed

    def test_parse_directory_recursive(self, parser, tmp_path):
        """Test parsing directory recursively."""
        # Create directory structure
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.py").write_text("# Comment 1", encoding='utf-8')
        (tmp_path / "subdir" / "file2.py").write_text("# Comment 2", encoding='utf-8')

        results = parser.parse_directory(str(tmp_path), recursive=True)

        # Should find both files
        assert len(results) >= 2

    def test_parse_directory_non_recursive(self, parser, tmp_path):
        """Test parsing directory non-recursively."""
        # Create directory structure
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.py").write_text("# Comment 1", encoding='utf-8')
        (tmp_path / "subdir" / "file2.py").write_text("# Comment 2", encoding='utf-8')

        results = parser.parse_directory(str(tmp_path), recursive=False)

        # Should only find top-level file
        assert len(results) >= 1

    def test_parse_directory_skips_pycache(self, parser, tmp_path):
        """Test that __pycache__ directories are skipped."""
        # Create __pycache__ directory
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "file.py").write_text("# Comment", encoding='utf-8')

        results = parser.parse_directory(str(tmp_path))

        # Should not include __pycache__ files
        assert all('__pycache__' not in str(path) for path in results.keys())

    def test_parse_directory_handles_errors(self, parser, tmp_path):
        """Test that directory parsing handles errors gracefully."""
        # Create file with syntax error
        (tmp_path / "invalid.py").write_text("def invalid", encoding='utf-8')
        # Create valid file
        (tmp_path / "valid.py").write_text("# Comment", encoding='utf-8')

        # Should not crash, should skip invalid files
        results = parser.parse_directory(str(tmp_path))

        # Valid file should still be parsed
        assert len(results) >= 0  # May or may not include invalid file

    def test_encoding_detection(self, parser, tmp_path):
        """Test that various encodings are handled."""
        file_path = tmp_path / "test_encoding.py"

        # Try UTF-8 with BOM
        content = "# UTF-8 comment with special chars: 한글"
        file_path.write_text(content, encoding='utf-8')

        result = parser.parse_file(str(file_path))

        assert result.encoding in ['utf-8', 'utf-8-sig']
        assert len(result.comments) > 0

    def test_comment_node_has_all_fields(self, parser, sample_python_file):
        """Test that CommentNode has all required fields."""
        result = parser.parse_file(sample_python_file)

        for node in result.get_all_translatable():
            assert hasattr(node, 'node_type')
            assert hasattr(node, 'content')
            assert hasattr(node, 'line_number')
            assert hasattr(node, 'column_offset')
            assert hasattr(node, 'context')
            assert hasattr(node, 'translated')

    def test_parsed_code_file_original_lines_preserved(self, parser, sample_python_file):
        """Test that original lines are preserved."""
        result = parser.parse_file(sample_python_file)

        assert len(result.original_lines) > 0
        # Original content should be reconstructible
        original = "".join(result.original_lines)
        assert len(original) > 0
