from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple


@dataclass
class TranslationResult:
    original: str
    translated: str
    source_lang: str
    target_lang: str
    confidence: float
    method: str
    preserved_terms: List[str]
    metadata: Dict[str, str] = field(default_factory=dict)


class TechnicalTermDatabase:
    PRESERVE = {"function", "class", "API", "HTTP", "JSON", "SQL"}
    TRANSLATION_MAP = {
        "ko": {"함수": "function", "클래스": "class", "변수": "variable", "테스트": "test"},
        "ja": {"関数": "function", "クラス": "class"},
        "zh": {"函数": "function", "类": "class"},
    }

    @classmethod
    def should_preserve(cls, term: str) -> bool:
        if not term:
            return False
        if term in cls.PRESERVE:
            return True
        if term.isupper() and len(term) > 1:
            return True
        if "_" in term:
            return True
        return bool(re.match(r"[A-Z][a-z]+[A-Z][A-Za-z]+", term))

    @classmethod
    def get_standard_translation(cls, term: str, lang: str) -> str | None:
        return cls.TRANSLATION_MAP.get(lang, {}).get(term)


class TranslationEngine:
    CAMEL_RE = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-zA-Z]+)+\b")
    SNAKE_RE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b")
    UPPER_RE = re.compile(r"\b[A-Z0-9_]{2,}\b")

    def __init__(self, mode: str = "rule_based", api_key: str | None = None):
        self.mode = mode
        self.api_key = api_key
        self.translation_cache: Dict[Tuple[str, str, str, str], TranslationResult] = {}

    def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        cache_key = (text, source_lang, target_lang, self.mode)
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]

        preserved_terms = self._extract_preservable_terms(text)
        if self.mode == "rule_based" or source_lang == target_lang:
            translated = self._rule_based_translate(text, source_lang, target_lang)
            confidence = 0.7 if source_lang != target_lang else 1.0
            method = "rule_based"
        else:
            translated = self._simulate_ai_translation(text, source_lang)
            confidence = 0.85
            method = "ai_simulated"

        result = TranslationResult(
            original=text,
            translated=translated,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=confidence,
            method=method,
            preserved_terms=preserved_terms,
            metadata={"cache_hit": "false"},
        )
        self.translation_cache[cache_key] = result
        return result

    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[TranslationResult]:
        return [self.translate(text, source_lang, target_lang) for text in texts]

    def _extract_preservable_terms(self, text: str) -> List[str]:
        ordered: List[str] = []

        def collect(pattern: re.Pattern[str]) -> None:
            for match in pattern.findall(text):
                if match not in ordered:
                    ordered.append(match)

        collect(self.CAMEL_RE)
        collect(self.SNAKE_RE)
        collect(self.UPPER_RE)

        for term in TechnicalTermDatabase.PRESERVE:
            if term in text and term not in ordered:
                ordered.append(term)

        for lang_map in TechnicalTermDatabase.TRANSLATION_MAP.values():
            for native, english in lang_map.items():
                if native in text and native not in ordered:
                    ordered.append(native)
                if english in text and english not in ordered:
                    ordered.append(english)

        return ordered

    def _rule_based_translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if source_lang == target_lang:
            return text

        replacements: Dict[str, str] = {
            "함수를 호출합니다": "Call the function",
            "함수를 호출하다": "Call the function",
            "함수": "function",
            "클래스": "class",
            "변수를": "the variable",
            "변수": "variable",
            "테스트입니다": "This is a test",
            "테스트": "test",
            "사용합니다": "use",
        }

        translated = text
        for key, value in replacements.items():
            translated = translated.replace(key, value)

        translated = translated.strip()
        if not translated.endswith("."):
            translated += "."
        return translated

    def _simulate_ai_translation(self, text: str, source_lang: str) -> str:
        return f"[{source_lang}→en] {text}"
