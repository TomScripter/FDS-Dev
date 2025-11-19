"""
Tests for i18n metacognition (quality validation) module.
"""

import pytest
from fds_dev.i18n import (
    TranslationQualityOracle,
    TranslationQualityTensor,
    ConsistencyChecker,
    ContextAnalyzer
)


class TestTranslationQualityTensor:
    """Test suite for TranslationQualityTensor class."""

    def test_compute_omega_perfect_scores(self):
        """Test omega calculation with perfect scores."""
        tensor = TranslationQualityTensor(
            semantic_fidelity=1.0,
            technical_accuracy=1.0,
            fluency=1.0,
            consistency=1.0,
            context_awareness=1.0
        )

        omega = tensor.compute_omega()
        assert omega == 1.0

    def test_compute_omega_zero_scores(self):
        """Test omega calculation with zero scores."""
        tensor = TranslationQualityTensor(
            semantic_fidelity=0.0,
            technical_accuracy=0.0,
            fluency=0.0,
            consistency=0.0,
            context_awareness=0.0
        )

        omega = tensor.compute_omega()
        assert omega == 0.0

    def test_compute_omega_weighted_average(self):
        """Test that omega uses weighted average."""
        tensor = TranslationQualityTensor(
            semantic_fidelity=0.8,  # 30% weight
            technical_accuracy=0.9,  # 25% weight
            fluency=0.7,            # 20% weight
            consistency=0.85,        # 15% weight
            context_awareness=0.75   # 10% weight
        )

        omega = tensor.compute_omega()

        # Manual calculation
        expected = 0.8*0.30 + 0.9*0.25 + 0.7*0.20 + 0.85*0.15 + 0.75*0.10
        assert abs(omega - expected) < 0.001


class TestTranslationQualityOracle:
    """Test suite for TranslationQualityOracle class."""

    @pytest.fixture
    def oracle(self):
        """Create a TranslationQualityOracle instance."""
        return TranslationQualityOracle(strict_threshold=0.85)

    def test_initialization(self, oracle):
        """Test oracle initializes correctly."""
        assert oracle.strict_threshold == 0.85
        assert len(oracle.evaluation_history) == 0

    def test_evaluate_simple_translation(self, oracle):
        """Test evaluation of simple translation."""
        assessment = oracle.evaluate(
            original="함수를 호출합니다",
            translated="call the function.",
            source_lang='ko',
            preserved_terms=['function']
        )

        assert isinstance(assessment.omega_score, float)
        assert 0.0 <= assessment.omega_score <= 1.0
        assert isinstance(assessment.tensor, TranslationQualityTensor)
        assert isinstance(assessment.issues, list)
        assert isinstance(assessment.recommendations, list)

    def test_evaluate_semantic_fidelity_similar_length(self, oracle):
        """Test semantic fidelity with similar length texts."""
        assessment = oracle.evaluate(
            original="This is a test",
            translated="This is a test",
            source_lang='en'
        )

        # Identical texts should have high fidelity
        assert assessment.tensor.semantic_fidelity > 0.8

    def test_evaluate_semantic_fidelity_different_length(self, oracle):
        """Test semantic fidelity with very different lengths."""
        assessment = oracle.evaluate(
            original="This is a very long sentence with many words",
            translated="Short",
            source_lang='en'
        )

        # Very different lengths should have lower fidelity
        assert assessment.tensor.semantic_fidelity < 0.5

    def test_evaluate_technical_accuracy_preserved(self, oracle):
        """Test technical accuracy when terms are preserved."""
        assessment = oracle.evaluate(
            original="Use CamelCase here",
            translated="Use CamelCase here",
            source_lang='en',
            preserved_terms=['CamelCase']
        )

        # Term preserved correctly
        assert assessment.tensor.technical_accuracy > 0.8

    def test_evaluate_technical_accuracy_missing(self, oracle):
        """Test technical accuracy when terms are missing."""
        assessment = oracle.evaluate(
            original="Use CamelCase and snake_case",
            translated="Use something else",
            source_lang='en',
            preserved_terms=['CamelCase', 'snake_case']
        )

        # Terms not preserved
        assert assessment.tensor.technical_accuracy < 0.3

    def test_evaluate_fluency_short_translation(self, oracle):
        """Test fluency with very short translation."""
        assessment = oracle.evaluate(
            original="Test",
            translated="Ok",
            source_lang='en'
        )

        # Very short translations have lower fluency
        assert assessment.tensor.fluency < 0.6

    def test_evaluate_fluency_proper_english(self, oracle):
        """Test fluency with proper English sentence."""
        assessment = oracle.evaluate(
            original="테스트 문장",
            translated="This is a proper English sentence.",
            source_lang='ko'
        )

        # Well-formed English should have good fluency
        assert assessment.tensor.fluency > 0.6

    def test_evaluate_context_concise_comment(self, oracle):
        """Test context awareness for concise code comment."""
        assessment = oracle.evaluate(
            original="함수 호출",
            translated="Call the function.",
            source_lang='ko'
        )

        # Concise technical comment is appropriate
        assert assessment.tensor.context_awareness > 0.6

    def test_evaluate_context_too_long(self, oracle):
        """Test context awareness for overly long comment."""
        long_text = " ".join(["word"] * 50)
        assessment = oracle.evaluate(
            original="짧은 설명",
            translated=long_text,
            source_lang='ko'
        )

        # Overly long comments are penalized
        assert assessment.tensor.context_awareness < 0.8

    def test_evaluate_generates_issues_low_quality(self, oracle):
        """Test that low quality translations generate issues."""
        assessment = oracle.evaluate(
            original="Very long detailed explanation with many words",
            translated="x",
            source_lang='en'
        )

        # Should have issues
        assert len(assessment.issues) > 0

    def test_evaluate_generates_recommendations(self, oracle):
        """Test that poor translations get recommendations."""
        assessment = oracle.evaluate(
            original="함수를 호출하다",
            translated="z",
            source_lang='ko',
            preserved_terms=['function']
        )

        # Should have recommendations
        assert len(assessment.recommendations) > 0

    def test_should_retranslate_low_omega(self, oracle):
        """Test that low omega scores trigger retranslation flag."""
        assessment = oracle.evaluate(
            original="Good translation needed here",
            translated="Bad",
            source_lang='en'
        )

        # Omega will be low, should retranslate
        assert assessment.should_retranslate is True

    def test_should_not_retranslate_high_omega(self, oracle):
        """Test that high omega scores don't trigger retranslation."""
        assessment = oracle.evaluate(
            original="Call function",
            translated="Call the function.",
            source_lang='en'
        )

        # Omega should be high enough
        if assessment.omega_score >= oracle.strict_threshold:
            assert assessment.should_retranslate is False

    def test_evaluation_history_tracking(self, oracle):
        """Test that evaluations are tracked in history."""
        oracle.evaluate("테스트", "test", 'ko')
        oracle.evaluate("또 다른 테스트", "another test", 'ko')

        assert len(oracle.evaluation_history) == 2

    def test_confidence_based_on_omega(self, oracle):
        """Test that confidence correlates with omega score."""
        assessment = oracle.evaluate(
            original="Good test",
            translated="Good test.",
            source_lang='en'
        )

        # Confidence should be close to omega * 1.1 (capped at 1.0)
        expected_confidence = min(1.0, assessment.omega_score * 1.1)
        assert abs(assessment.confidence - expected_confidence) < 0.01


class TestConsistencyChecker:
    """Test suite for ConsistencyChecker class."""

    @pytest.fixture
    def checker(self):
        """Create a ConsistencyChecker instance."""
        return ConsistencyChecker()

    def test_initialization(self, checker):
        """Test checker initializes correctly."""
        assert len(checker.term_map) == 0
        assert len(checker.violations) == 0

    def test_register_translation_simple(self, checker):
        """Test registering a simple translation."""
        checker.register_translation("함수", "function")

        # Should have extracted and stored the term
        assert len(checker.term_map) > 0

    def test_check_consistency_first_translation(self, checker):
        """Test consistency check on first translation."""
        is_consistent, violations = checker.check_consistency("함수", "function")

        # First translation is always consistent
        assert is_consistent is True
        assert len(violations) == 0

    def test_check_consistency_same_translation(self, checker):
        """Test consistency when using same translation."""
        checker.register_translation("함수", "function")

        is_consistent, violations = checker.check_consistency("함수", "function")

        assert is_consistent is True
        assert len(violations) == 0

    def test_extract_terms_camelcase(self, checker):
        """Test extraction of CamelCase terms."""
        terms = checker._extract_terms("Use MyClass and AnotherClass")

        assert 'MyClass' in terms
        assert 'AnotherClass' in terms

    def test_extract_terms_snake_case(self, checker):
        """Test extraction of snake_case terms."""
        terms = checker._extract_terms("my_function and another_var")

        assert 'my_function' in terms
        assert 'another_var' in terms

    def test_get_consistency_score_empty(self, checker):
        """Test consistency score with no terms."""
        score = checker.get_consistency_score()

        # No terms = perfect consistency
        assert score == 1.0

    def test_get_consistency_score_perfect(self, checker):
        """Test consistency score with consistent terms."""
        checker.term_map = {
            'term1': {'translation1'},
            'term2': {'translation2'}
        }

        score = checker.get_consistency_score()

        # All terms have single translation
        assert score == 1.0


class TestContextAnalyzer:
    """Test suite for ContextAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a ContextAnalyzer instance."""
        return ContextAnalyzer()

    def test_analyze_inline_comment(self, analyzer):
        """Test analysis of inline comment context."""
        result = analyzer.analyze_context(
            "Calculate the sum",
            node_type='inline_comment'
        )

        assert result['context_type'] == 'code_comment'
        assert result['style'] == 'concise'
        assert result['tone'] == 'technical'

    def test_analyze_docstring(self, analyzer):
        """Test analysis of docstring context."""
        result = analyzer.analyze_context(
            "This function calculates...",
            node_type='docstring'
        )

        assert result['context_type'] == 'docstring'
        assert result['style'] == 'detailed'
        assert result['tone'] == 'professional'

    def test_analyze_error_message(self, analyzer):
        """Test analysis of error message context."""
        result = analyzer.analyze_context(
            "Error: invalid parameter"
        )

        assert result['context_type'] == 'error_message'
        assert result['style'] == 'precise'

    def test_analyze_detects_code_terms(self, analyzer):
        """Test detection of code terms in text."""
        result = analyzer.analyze_context(
            "Use CamelCase for class names"
        )

        assert result['has_code_terms'] is True

    def test_analyze_detects_technical_words(self, analyzer):
        """Test detection of technical words."""
        result = analyzer.analyze_context(
            "The function returns a parameter"
        )

        assert result['has_technical_words'] is True

    def test_analyze_max_length_calculation(self, analyzer):
        """Test max length calculation based on context."""
        # Code comment (1.2x multiplier)
        result1 = analyzer.analyze_context(
            "Short comment",  # 2 words
            node_type='inline_comment'
        )
        assert result1['max_length'] == int(2 * 1.2)

        # Docstring (1.5x multiplier)
        result2 = analyzer.analyze_context(
            "Longer description",  # 2 words
            node_type='docstring'
        )
        assert result2['max_length'] == int(2 * 1.5)

    def test_recommend_approach_technical_concise(self, analyzer):
        """Test recommendation for technical concise content."""
        result = analyzer.analyze_context(
            "Call the function with parameter",
            node_type='inline_comment'
        )

        assert 'recommended_approach' in result
        # Should recommend preserving technical terms
        assert 'technical' in result['recommended_approach'].lower()
