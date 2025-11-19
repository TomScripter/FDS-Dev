"""
Tests for i18n language detection module.
"""

import pytest
from fds_dev.i18n import LanguageDetector


class TestLanguageDetector:
    """Test suite for LanguageDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a LanguageDetector instance."""
        return LanguageDetector()

    def test_detect_korean_hangul(self, detector):
        """Test detection of Korean text with Hangul script."""
        text = "이것은 한국어 테스트입니다"
        result = detector.detect(text)

        assert result.language == 'ko'
        assert result.script == 'hangul'
        assert result.confidence > 0.7
        assert len(result.samples) > 0

    def test_detect_japanese_hiragana(self, detector):
        """Test detection of Japanese text with Hiragana."""
        text = "これはテストです"
        result = detector.detect(text)

        assert result.language == 'ja'
        assert result.script in ['hiragana', 'katakana', 'kanji']
        assert result.confidence > 0.6

    def test_detect_chinese(self, detector):
        """Test detection of Chinese text."""
        text = "这是一个测试"
        result = detector.detect(text)

        assert result.language == 'zh'
        assert result.script in ['hanzi', 'kanji']
        assert result.confidence > 0.6

    def test_detect_english(self, detector):
        """Test detection of English text."""
        text = "This is a test with common English words"
        result = detector.detect(text)

        assert result.language == 'en'
        assert result.script == 'latin'
        assert result.confidence > 0.3

    def test_detect_empty_string(self, detector):
        """Test detection with empty string."""
        result = detector.detect("")

        assert result.language == 'en'  # Default
        assert result.confidence == 0.0
        assert result.samples == []

    def test_detect_technical_content(self, detector):
        """Test detection with technical content (code-like)."""
        text = "함수를 호출하다 function_call() returns value"
        result = detector.detect(text)

        # Should detect Korean despite mixed content
        assert result.language == 'ko'
        assert result.confidence > 0.5

    def test_is_english_true(self, detector):
        """Test is_english quick check with English text."""
        text = "This is a clear English sentence with common words"
        assert detector.is_english(text) is True

    def test_is_english_false_korean(self, detector):
        """Test is_english quick check with Korean text."""
        text = "한국어 텍스트입니다"
        assert detector.is_english(text) is False

    def test_is_english_false_japanese(self, detector):
        """Test is_english quick check with Japanese text."""
        text = "これは日本語です"
        assert detector.is_english(text) is False

    def test_is_english_with_threshold(self, detector):
        """Test is_english with custom threshold."""
        text = "Short text"  # Ambiguous
        # With high threshold, may fail
        result = detector.is_english(text, threshold=0.9)
        assert isinstance(result, bool)

    def test_detect_batch(self, detector):
        """Test batch detection of multiple texts."""
        texts = [
            "한국어 텍스트",
            "English text",
            "日本語のテキスト"
        ]

        results = detector.detect_batch(texts)

        assert len(results) == 3
        assert results[texts[0]].language == 'ko'
        assert results[texts[1]].language == 'en'
        assert results[texts[2]].language == 'ja'

    def test_clean_text_removes_urls(self, detector):
        """Test that _clean_text removes URLs."""
        text = "Visit https://example.com for more info 방문하세요"
        cleaned = detector._clean_text(text)

        assert 'https://' not in cleaned
        assert '방문하세요' in cleaned

    def test_clean_text_removes_code_patterns(self, detector):
        """Test that _clean_text removes code-like patterns."""
        text = "call_function() with CONSTANT_VALUE in code"
        cleaned = detector._clean_text(text)

        # Should remove function calls and CONSTANTS
        assert 'call_function()' not in cleaned
        assert 'CONSTANT_VALUE' not in cleaned

    def test_script_detection_accuracy(self, detector):
        """Test script detection returns correct confidence."""
        # Pure Hangul text
        hangul_text = "가나다라마바사"
        script, confidence = detector._detect_script(hangul_text)

        assert script == 'hangul'
        assert confidence > 0.8

    def test_language_markers_korean(self, detector):
        """Test Korean language markers detection."""
        text = "이것은 테스트입니다"
        script = 'hangul'
        lang, confidence = detector._detect_language(text, script)

        assert lang == 'ko'
        assert confidence > 0.6

    def test_extract_samples_korean(self, detector):
        """Test extraction of Korean sample sentences."""
        text = "첫 번째 문장입니다. 두 번째 문장도 있습니다. 짧음."
        samples = detector._extract_samples(text, 'ko')

        # Should extract meaningful sentences
        assert len(samples) > 0
        assert all(len(s) > 10 for s in samples)
