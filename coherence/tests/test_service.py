"""Tests for coherence service."""

import pytest
from unittest.mock import patch, MagicMock
from coherence.service import CoherenceService, CoherenceResult, CoherenceAnalyzer


@pytest.fixture
def sample_text():
    """Return a sample text for testing."""
    return """
    The quick brown fox jumps over the lazy dog. This is a test sentence.
    Another sentence to test the coherence analysis functionality.
    """


@pytest.fixture
def coherence_analyzer():
    """Create a CoherenceAnalyzer instance with a mock client."""
    with patch("coherence.coherence_analyzer.genai") as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_models = MagicMock()
        mock_client.models = mock_models
        mock_models.generate_content.return_value = MagicMock(
            text='{"text_coherence": 0.8, "topic_coherence": 0.9, "score": 0.85, "feedback": "Good", "suggestions": ["Add transitions"], "confidence": 0.95}'
        )
        yield CoherenceAnalyzer()


def test_service_initialization():
    """Test CoherenceService initialization."""
    with patch("coherence.service.get_gemini_api_key") as mock_api_key:
        mock_api_key.return_value = "test_api_key"
        service = CoherenceService()
        assert hasattr(service, "analyzer")
        assert hasattr(service, "_analyze")


@patch("coherence.service.CoherenceAnalyzer")
def test_analyze_success(mock_analyzer_class, sample_text):
    """Test successful analysis."""
    with patch("coherence.service.get_gemini_api_key") as mock_api_key:
        mock_api_key.return_value = "test_api_key"
        # Setup
        service = CoherenceService()
        mock_analyzer = mock_analyzer_class.return_value

    # Mock the analyzer's analyze_text method
    mock_analysis = CoherenceResult(
        text_coherence=0.8,
        topic_coherence=0.9,
        score=0.85,
        feedback="Good coherence",
        suggestions=["Add transitions"],
        confidence=0.95,
    )
    mock_analyzer.analyze_text.return_value = mock_analysis

    # Test
    result = service.analyze(sample_text, topic=None)

    # Verify
    mock_analyzer.analyze_text.assert_called_once_with(sample_text, None)
    assert isinstance(result, CoherenceResult)
    assert result.score == 0.85
    assert result.text_coherence == 0.8
    assert result.topic_coherence == 0.9
    assert result.feedback == "Good coherence"
    assert result.suggestions == ["Add transitions"]
    assert result.confidence == 0.95


@patch("coherence.service.CoherenceAnalyzer")
def test_analyze_with_topic(mock_analyzer_class, sample_text):
    """Test analysis with topic parameter."""
    with patch("coherence.service.get_gemini_api_key") as mock_api_key:
        mock_api_key.return_value = "test_api_key"
        service = CoherenceService()
        mock_analyzer = mock_analyzer_class.return_value

    mock_analysis = CoherenceResult(
        text_coherence=0.8,
        topic_coherence=0.9,
        score=0.85,
        feedback="Good coherence",
        suggestions=[],
        confidence=0.95,
    )
    mock_analyzer.analyze_text.return_value = mock_analysis

    # Test with topic
    topic = "test topic"
    result = service.analyze(sample_text, topic)

    # Verify topic was passed to analyzer
    mock_analyzer.analyze_text.assert_called_once_with(sample_text, topic)
    assert result.score == 0.85


def test_analyze_empty_text():
    """Test analysis with empty text."""
    with patch("coherence.service.get_gemini_api_key") as mock_api_key:
        mock_api_key.return_value = "test_api_key"
        service = CoherenceService()
        result = service.analyze("")

    assert result.score == 0.0
    assert result.text_coherence == 0.0
    assert result.feedback == "Empty text provided for analysis"
    assert result.suggestions == ["Provide a valid text for coherence analysis"]
    assert result.confidence == 1.0


@patch("coherence.service.CoherenceAnalyzer")
def test_analyze_error_handling(mock_analyzer_class, sample_text):
    """Test error propagation during analysis."""
    with patch("coherence.service.get_gemini_api_key") as mock_api_key:
        mock_api_key.return_value = "test_api_key"
        service = CoherenceService()
        mock_analyzer = mock_analyzer_class.return_value
        mock_analyzer.analyze_text.side_effect = Exception("API error")

    # Test that the exception is propagated
    with pytest.raises(Exception, match="API error"):
        service.analyze(sample_text)

    # Verify the method was called correctly
    mock_analyzer.analyze_text.assert_called_once_with(sample_text, None)


def test_analyze_caching(sample_text):
    """Test that analysis results are cached."""
    with patch("coherence.service.CoherenceAnalyzer") as mock_analyzer_class:
        mock_analyzer = mock_analyzer_class.return_value
        with patch("coherence.service.get_gemini_api_key") as mock_api_key:
            mock_api_key.return_value = "test_api_key"
            mock_analysis = CoherenceResult(
                text_coherence=0.8,
                topic_coherence=0.9,
                score=0.85,
                feedback="Test",
                suggestions=[],
                confidence=0.9,
            )
            mock_analyzer.analyze_text.return_value = mock_analysis

            service = CoherenceService()
            service.analyzer = mock_analyzer

            # First call
            result1 = service.analyze(sample_text)
            # Second call with same text
            result2 = service.analyze(sample_text)

            # Should only call analyze_text once due to caching
            assert mock_analyzer.analyze_text.call_count == 1
