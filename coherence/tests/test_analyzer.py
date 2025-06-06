"""Tests for coherence analyzer."""
from json import JSONDecodeError
import pytest
from unittest.mock import MagicMock, patch
from coherence import CoherenceAnalyzer, CoherenceResult


@pytest.fixture
def sample_text():
    """Return a sample text for testing."""
    return """
    The quick brown fox jumps over the lazy dog. This is a test sentence.
    Another sentence to test the coherence analysis functionality.
    """


@pytest.fixture
def mock_coherence_result():
    """Create a mock CoherenceResult instance."""
    return CoherenceResult(
        text_coherence=0.8,
        topic_coherence=0.9,
        score=0.85,
        feedback="Good coherence",
        suggestions=["Add more transitions between paragraphs"],
        confidence=0.95
    )


@pytest.fixture
def coherence_analyzer():
    """Create a CoherenceAnalyzer instance with a mock client."""
    with patch('coherence.coherence_analyzer.genai') as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_models = MagicMock()
        mock_client.models = mock_models
        mock_models.generate_content.return_value = MagicMock(
            text='{"text_coherence": 0.8, "topic_coherence": 0.9, "score": 0.85, "feedback": "Good", "suggestions": ["Add transitions"], "confidence": 0.95}'
        )
        yield CoherenceAnalyzer(
            model="gemini-2.0-flash-lite",
            api_key="test_api_key",
        )


def test_analyzer_initialization():
    """Test CoherenceAnalyzer initialization."""
    with patch('coherence.coherence_analyzer.genai') as mock_genai:
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        
        analyzer = CoherenceAnalyzer(
            model="gemini-2.0-flash-lite",
            api_key="test_api_key",
        )
        
        assert analyzer.model == "gemini-2.0-flash-lite"
        assert analyzer.client == mock_client


def test_analyze_text(coherence_analyzer: CoherenceAnalyzer, sample_text):
    """Test analyze_text method with mock response."""
    # Mock the client's generate_content method
    mock_response = MagicMock()
    mock_response.text = '{"text_coherence": 0.8, "topic_coherence": 0.9, "score": 0.85, "feedback": "Good", "suggestions": ["Add transitions"], "confidence": 0.95}'
    coherence_analyzer.client.models.generate_content.return_value = mock_response
    
    # Call the method
    result = coherence_analyzer.analyze_text(sample_text)
    
    # Assertions
    assert isinstance(result, CoherenceResult)
    assert result.text_coherence == 0.8
    assert result.topic_coherence == 0.9
    assert result.score == 0.85
    assert result.feedback == "Good"
    assert result.suggestions == ["Add transitions"]
    assert result.confidence == 0.95


def test_analyze_text_with_topic(coherence_analyzer: CoherenceAnalyzer, sample_text):
    """Test analyze_text with topic parameter."""
    with patch.object(coherence_analyzer.client.models, 'generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = '{"text_coherence": 0.8, "topic_coherence": 0.9, "score": 0.85, "feedback": "Good", "suggestions": ["Add transitions"], "confidence": 0.95}'
        mock_generate.return_value = mock_response
        
        result = coherence_analyzer.analyze_text(sample_text, topic="test topic")
        
        assert isinstance(result, CoherenceResult)
        assert result.text_coherence == 0.8
        assert result.topic_coherence == 0.9
        assert result.score == 0.85
        assert result.feedback == "Good"
        assert result.suggestions == ["Add transitions"]
        assert result.confidence == 0.95
        # Verify the topic was included in the prompt
        assert "test topic" in mock_generate.call_args[1]["contents"][0].parts[0].text


def test_analyze_text_invalid_response(coherence_analyzer: CoherenceAnalyzer, sample_text):
    """Test analyze_text with invalid response from API."""
    with patch.object(coherence_analyzer.client.models, 'generate_content') as mock_generate:
        mock_response = MagicMock()
        mock_response.text = 'invalid json'
        mock_generate.return_value = mock_response
        
        with pytest.raises(JSONDecodeError, match="Expecting value: \\w"):
            coherence_analyzer.analyze_text(sample_text)


def test_analyze_text_empty_input(coherence_analyzer: CoherenceAnalyzer):
    """Test analyze_text with empty input."""
    result = coherence_analyzer.analyze_text("")
    assert result.score == 0
    assert result.text_coherence == 0
    assert result.topic_coherence == 0
    assert result.feedback == ""
    assert result.suggestions == [""]
    assert result.confidence == 1
