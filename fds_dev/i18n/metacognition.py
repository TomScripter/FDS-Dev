from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class TranslationQualityTensor:
    semantic_fidelity: float
    technical_accuracy: float
    fluency: float
    consistency: float
    context_awareness: float

    def compute_omega(self) -> float:
        weights = [0.30, 0.25, 0.20, 0.15, 0.10]
        values = [
            self.semantic_fidelity,
            self.technical_accuracy,
            self.fluency,
            self.consistency,
            self.context_awareness,
        ]
        return sum(weight * value for weight, value in zip(weights, values))


@dataclass
class EvaluationResult:
    omega_score: float
    tensor: TranslationQualityTensor
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    should_retranslate: bool = False
    confidence: float = 0.0


class TranslationQualityOracle:
    def __init__(self, strict_threshold: float = 0.85):
        self.strict_threshold = strict_threshold
        self.evaluation_history: List[EvaluationResult] = []

    def evaluate(
        self,
        original: str,
        translated: str,
        source_lang: str,
        preserved_terms: Optional[List[str]] = None,
    ) -> EvaluationResult:
        preserved = preserved_terms or []
        tensor = TranslationQualityTensor(
            semantic_fidelity=self._score_semantic(original, translated),
            technical_accuracy=self._score_technical(preserved, translated),
            fluency=self._score_fluency(translated),
            consistency=self._score_consistency(preserved),
            context_awareness=self._score_context(original),
        )
        omega = tensor.compute_omega()
        issues: List[str] = []
        recommendations: List[str] = []
        should_retranslate = omega < self.strict_threshold
        if should_retranslate:
            issues.append("Ω score below strict threshold.")
            recommendations.append("Improve clarity and preserve critical terminology.")
        else:
            recommendations.append("Maintain translation consistency.")

        confidence = min(1.0, omega * 1.1)
        result = EvaluationResult(
            omega_score=omega,
            tensor=tensor,
            issues=issues,
            recommendations=recommendations,
            should_retranslate=should_retranslate,
            confidence=confidence,
        )
        self.evaluation_history.append(result)
        return result

    def _score_semantic(self, original: str, translated: str) -> float:
        original_tokens = self._normalize(original)
        translated_tokens = self._normalize(translated)
        if not original_tokens:
            return 0.0
        overlap = len(original_tokens & translated_tokens)
        return min(1.0, overlap / max(len(original_tokens), 1))

    def _score_technical(self, preserved: List[str], translated: str) -> float:
        if not preserved:
            return 0.5
        hits = sum(1 for term in preserved if term in translated)
        if hits == 0:
            return 0.2
        return min(1.0, 0.8 + hits * 0.05)

    def _score_fluency(self, translated: str) -> float:
        word_count = len(translated.split())
        if word_count < 3:
            return 0.5
        return min(1.0, 0.75 + word_count * 0.01)

    def _score_consistency(self, preserved: List[str]) -> float:
        if not preserved:
            return 0.8
        return min(1.0, 0.85 + len(set(preserved)) * 0.05)

    def _score_context(self, original: str) -> float:
        word_count = len(original.split())
        return min(1.0, 0.7 + word_count * 0.01)

    def _normalize(self, text: str) -> Set[str]:
        return set(re.findall(r"\b\w+\b", text.lower()))


class ConsistencyChecker:
    CAMEL_RE = re.compile(r"\b[A-Z][a-z]+[A-Z][a-zA-Z]*\b")
    SNAKE_RE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b")
    UPPER_RE = re.compile(r"\b[A-Z0-9_]{2,}\b")

    def __init__(self) -> None:
        self.term_map: Dict[str, Set[str]] = {}
        self.violations: List[str] = []

    def register_translation(self, term: str, translation: str) -> None:
        self.term_map.setdefault(term, set()).add(translation)

    def check_consistency(self, term: str, translation: str) -> Tuple[bool, List[str]]:
        translations = self.term_map.setdefault(term, set())
        translations.add(translation)
        if len(translations) > 1:
            message = f"Inconsistent translation for '{term}'."
            self.violations.append(message)
            return False, [message]
        return True, []

    def _extract_terms(self, text: str) -> Set[str]:
        terms = set(self.CAMEL_RE.findall(text))
        terms.update(self.SNAKE_RE.findall(text))
        terms.update(self.UPPER_RE.findall(text))
        return terms

    def get_consistency_score(self) -> float:
        if not self.term_map:
            return 1.0
        consistent_terms = sum(1 for translations in self.term_map.values() if len(translations) == 1)
        return consistent_terms / len(self.term_map)


class ContextAnalyzer:
    TECH_WORDS = {"function", "parameter", "class", "method", "variable", "return"}

    def analyze_context(self, text: str, node_type: Optional[str] = None) -> Dict[str, object]:
        words = re.findall(r"\b\w+\b", text.lower())
        config = {
            "inline_comment": ("code_comment", "concise", "technical", 1.2),
            "docstring": ("docstring", "detailed", "professional", 1.5),
        }
        context_type, style, tone, multiplier = config.get(node_type, ("error_message", "precise", "neutral", 1.0))
        has_code_terms = bool(self._detect_code_terms(text))
        has_technical_words = any(word in self.TECH_WORDS for word in words)
        max_length = int(max(len(words), 1) * multiplier)
        recommended = self._recommendation(node_type)
        return {
            "context_type": context_type,
            "style": style,
            "tone": tone,
            "has_code_terms": has_code_terms,
            "has_technical_words": has_technical_words,
            "max_length": max_length,
            "recommended_approach": recommended,
        }

    def _detect_code_terms(self, text: str) -> bool:
        return bool(re.search(r"[A-Za-z_]+\(.*?\)", text) or re.search(r"[A-Z][a-z]+[A-Z]", text))

    def _recommendation(self, node_type: Optional[str]) -> str:
        if node_type == "inline_comment":
            return "Maintain a technical, concise tone while preserving vocabulary."
        if node_type == "docstring":
            return "Adopt a professional narrative with clear technical details."
        return "Describe the issue precisely with actionable guidance."
