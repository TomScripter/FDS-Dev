"""
Tests for i18n translation engine module.
"""

import pytest
from fds_dev.i18n import TranslationEngine, TechnicalTermDatabase


class TestTechnicalTermDatabase:
    """Test suite for TechnicalTermDatabase class."""

    def test_should_preserve_technical_term(self):
        """Test that technical terms are marked for preservation."""
        assert TechnicalTermDatabase.should_preserve('function') is True
        assert TechnicalTermDatabase.should_preserve('class') is True
        assert TechnicalTermDatabase.should_preserve('API') is True

    def test_should_preserve_acronyms(self):
        """Test that ACRONYMS are preserved."""
        assert TechnicalTermDatabase.should_preserve('HTTP') is True
        assert TechnicalTermDatabase.should_preserve('JSON') is True
        assert TechnicalTermDatabase.should_preserve('SQL') is True

    def test_should_not_preserve_common_words(self):
        """Test that common words are not preserved."""
        assert TechnicalTermDatabase.should_preserve('hello') is False
        assert TechnicalTermDatabase.should_preserve('world') is False

    def test_get_standard_translation_korean(self):
        """Test Korean standard translation lookup."""
        result = TechnicalTermDatabase.get_standard_translation('함수', 'ko')
        assert result == 'function'

        result = TechnicalTermDatabase.get_standard_translation('클래스', 'ko')
        assert result == 'class'

    def test_get_standard_translation_japanese(self):
        """Test Japanese standard translation lookup."""
        result = TechnicalTermDatabase.get_standard_translation('関数', 'ja')
        assert result == 'function'

    def test_get_standard_translation_chinese(self):
        """Test Chinese standard translation lookup."""
        result = TechnicalTermDatabase.get_standard_translation('函数', 'zh')
        assert result == 'function'

    def test_get_standard_translation_missing(self):
        """Test lookup of non-existent term returns None."""
        result = TechnicalTermDatabase.get_standard_translation('unknown', 'ko')
        assert result is None


class TestTranslationEngine:
    """Test suite for TranslationEngine class."""

    @pytest.fixture
    def engine_rule_based(self):
        """Create a rule-based translation engine."""
        return TranslationEngine(mode='rule_based', api_key=None)

    def test_initialization_rule_based(self, engine_rule_based):
        """Test engine initializes in rule-based mode."""
        assert engine_rule_based.mode == 'rule_based'
        assert engine_rule_based.api_key is None

    def test_translate_korean_to_english_simple(self, engine_rule_based):
        """Test simple Korean to English translation."""
        result = engine_rule_based.translate(
            "함수를 호출합니다",
            source_lang='ko',
            target_lang='en'
        )

        assert result.original == "함수를 호출합니다"
        assert 'function' in result.translated.lower()
        assert result.source_lang == 'ko'
        assert result.target_lang == 'en'
        assert result.confidence > 0.0
        assert result.method == 'rule_based'

    def test_translate_preserves_technical_terms(self, engine_rule_based):
        """Test that technical terms are preserved in translation."""
        result = engine_rule_based.translate(
            "CamelCase 변수를 사용합니다",
            source_lang='ko',
            target_lang='en'
        )

        # CamelCase should be preserved
        assert 'CamelCase' in result.translated
        assert 'variable' in result.translated.lower()

    def test_extract_preservable_terms_camelcase(self, engine_rule_based):
        """Test extraction of CamelCase terms."""
        text = "Use MyClassName and AnotherClass here"
        terms = engine_rule_based._extract_preservable_terms(text)

        assert 'MyClassName' in terms
        assert 'AnotherClass' in terms

    def test_extract_preservable_terms_snake_case(self, engine_rule_based):
        """Test extraction of snake_case terms."""
        text = "Use my_function and another_variable here"
        terms = engine_rule_based._extract_preservable_terms(text)

        assert 'my_function' in terms
        assert 'another_variable' in terms

    def test_extract_preservable_terms_upper_case(self, engine_rule_based):
        """Test extraction of UPPER_CASE terms."""
        text = "Set CONSTANT_VALUE and MAX_SIZE here"
        terms = engine_rule_based._extract_preservable_terms(text)

        assert 'CONSTANT_VALUE' in terms
        assert 'MAX_SIZE' in terms

    def test_extract_preservable_terms_from_database(self, engine_rule_based):
        """Test extraction using term database."""
        text = "Call the function with API parameter"
        terms = engine_rule_based._extract_preservable_terms(text)

        assert 'function' in terms
        assert 'API' in terms

    def test_rule_based_translation_korean_markers(self, engine_rule_based):
        """Test that Korean sentence markers are transformed."""
        result = engine_rule_based.translate(
            "테스트입니다",
            source_lang='ko',
            target_lang='en'
        )

        # "입니다" should be converted to "."
        assert result.translated.endswith('.')

    def test_translation_caching(self, engine_rule_based):
        """Test that translations are cached."""
        text = "테스트 문장"

        # First translation
        result1 = engine_rule_based.translate(text, 'ko', 'en')

        # Second translation (should use cache)
        result2 = engine_rule_based.translate(text, 'ko', 'en')

        assert result1.translated == result2.translated
        assert len(engine_rule_based.translation_cache) > 0

    def test_translate_batch(self, engine_rule_based):
        """Test batch translation of multiple texts."""
        texts = [
            "첫 번째 문장",
            "두 번째 문장",
            "세 번째 문장"
        ]

        results = engine_rule_based.translate_batch(texts, 'ko', 'en')

        assert len(results) == 3
        assert all(r.source_lang == 'ko' for r in results)
        assert all(r.target_lang == 'en' for r in results)

    def test_simulate_ai_translation(self, engine_rule_based):
        """Test AI translation simulation."""
        result = engine_rule_based._simulate_ai_translation(
            "함수를 호출하다",
            source_lang='ko'
        )

        # Should apply improvements from simulated AI
        assert isinstance(result, str)
        assert len(result) > 0

    def test_translation_result_structure(self, engine_rule_based):
        """Test that TranslationResult has correct structure."""
        result = engine_rule_based.translate("테스트", 'ko', 'en')

        # Verify all required fields exist
        assert hasattr(result, 'original')
        assert hasattr(result, 'translated')
        assert hasattr(result, 'source_lang')
        assert hasattr(result, 'target_lang')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'method')
        assert hasattr(result, 'preserved_terms')
        assert hasattr(result, 'metadata')

    def test_confidence_score_range(self, engine_rule_based):
        """Test that confidence scores are in valid range."""
        result = engine_rule_based.translate("테스트", 'ko', 'en')

        assert 0.0 <= result.confidence <= 1.0

    def test_preserved_terms_in_result(self, engine_rule_based):
        """Test that preserved terms are tracked in result."""
        result = engine_rule_based.translate(
            "Use CamelCase and snake_case",
            'en',
            'en'  # English to English (no translation needed)
        )

        # Should track preserved terms
        assert isinstance(result.preserved_terms, list)
