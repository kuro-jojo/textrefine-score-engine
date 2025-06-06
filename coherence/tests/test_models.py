"""Tests for coherence models."""

import pytest
from coherence import CoherenceResult


def test_coherence_result_initialization():
    """Test CoherenceResult initialization and properties."""
    result = CoherenceResult(
        score=0.8,
        text_coherence=0.85,
        topic_coherence=0.75,
        feedback="Good coherence",
        suggestions=["Add transitions"],
        confidence=0.9,
    )

    assert result.score == 0.8
    assert result.text_coherence == 0.85
    assert result.topic_coherence == 0.75
    assert result.feedback == "Good coherence"
    assert result.suggestions == ["Add transitions"]
    assert result.confidence == 0.9


def test_coherence_result_optional_topic():
    """Test CoherenceResult with no topic coherence."""
    result = CoherenceResult(
        score=0.8,
        text_coherence=0.85,
        topic_coherence=None,
        feedback="Good coherence",
        suggestions=[],
        confidence=0.9,
    )

    assert result.topic_coherence is None


def test_coherence_result_validation():
    """Test CoherenceResult validation."""
    # Test score validation
    with pytest.raises(ValueError):
        CoherenceResult(
            score=1.5,  # Invalid, should be <= 1.0
            text_coherence=0.85,
            topic_coherence=0.75,
            feedback="Test",
            suggestions=[],
            confidence=0.9,
        )

    # Test text_coherence validation
    with pytest.raises(ValueError):
        CoherenceResult(
            score=0.8,
            text_coherence=1.5,  # Invalid
            topic_coherence=0.75,
            feedback="Test",
            suggestions=[],
            confidence=0.9,
        )

    # Test confidence validation
    with pytest.raises(ValueError):
        CoherenceResult(
            score=0.8,
            text_coherence=0.85,
            topic_coherence=0.75,
            feedback="Test",
            suggestions=[],
            confidence=1.1,  # Invalid
        )


def test_coherence_result_str_representation():
    """Test string representation of CoherenceResult."""
    result = CoherenceResult(
        score=0.8,
        text_coherence=0.85,
        topic_coherence=0.75,
        feedback="Good coherence",
        suggestions=["Add transitions"],
        confidence=0.9,
    )

    str_rep = str(result)
    assert "Coherence Score: 0.80" in str_rep
    assert "Text Coherence: 0.85" in str_rep
    assert "Topic Coherence: 0.75" in str_rep
    assert "Confidence: 0.90" in str_rep
    assert "Good coherence" in str_rep
    assert "Add transitions" in str_rep
