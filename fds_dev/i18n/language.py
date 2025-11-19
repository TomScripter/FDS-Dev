from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class LanguageDetectionResult:
    language: str
    script: str
    confidence: float
    samples: List[str] = field(default_factory=list)


class LanguageDetector:
    URL_PATTERN = re.compile(r"https?://\S+")
    CODE_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\(\)")
    CONSTANT_PATTERN = re.compile(r"\b[A-Z0-9_]{2,}\b")

    def detect(self, text: str) -> LanguageDetectionResult:
        cleaned = self._clean_text(text)
        if not cleaned:
            return LanguageDetectionResult(language="en", script="latin", confidence=0.0, samples=[])
        script, script_confidence = self._detect_script(cleaned)
        language, language_confidence = self._detect_language(cleaned, script)
        samples = self._extract_samples(cleaned, language)
        confidence = max(script_confidence, language_confidence)
        return LanguageDetectionResult(language=language, script=script, confidence=confidence, samples=samples)

    def detect_batch(self, texts: List[str]) -> Dict[str, LanguageDetectionResult]:
        return {text: self.detect(text) for text in texts}

    def is_english(self, text: str, threshold: float = 0.7) -> bool:
        cleaned = self._clean_text(text)
        letters = [char for char in cleaned if char.isalpha()]
        if not letters:
            return False
        latin_ratio = sum(1 for char in letters if char.isascii()) / len(letters)
        return latin_ratio >= threshold

    def _clean_text(self, text: str) -> str:
        cleaned = self.URL_PATTERN.sub("", text)
        cleaned = self.CODE_PATTERN.sub("", cleaned)
        cleaned = self.CONSTANT_PATTERN.sub("", cleaned)
        return cleaned.strip()

    def _detect_script(self, text: str) -> Tuple[str, float]:
        if self._contains_range(text, 0xAC00, 0xD7AF):
            return "hangul", 0.92
        if self._contains_range(text, 0x3040, 0x309F):
            return "hiragana", 0.85
        if self._contains_range(text, 0x30A0, 0x30FF):
            return "katakana", 0.82
        if self._contains_range(text, 0x4E00, 0x9FFF):
            return "hanzi", 0.80
        ascii_letters = [c for c in text if c.isalpha() and c.isascii()]
        if ascii_letters:
            return "latin", 0.65
        return "latin", 0.45

    def _detect_language(self, text: str, script: str) -> Tuple[str, float]:
        if script == "hangul":
            return "ko", 0.9
        if script in {"hiragana", "katakana"}:
            return "ja", 0.8
        if script == "hanzi":
            return "zh", 0.82
        if script == "latin":
            if self.is_english(text, threshold=0.5):
                return "en", 0.7
            return "en", 0.5
        return "en", 0.4

    def _extract_samples(self, text: str, language: str) -> List[str]:
        sentences = re.split(r"[.!?]\s*", text)
        samples = [sentence.strip() for sentence in sentences if len(sentence.strip()) > 10]
        return samples[:5]

    def _contains_range(self, text: str, start: int, end: int) -> bool:
        return any(start <= ord(char) <= end for char in text)
