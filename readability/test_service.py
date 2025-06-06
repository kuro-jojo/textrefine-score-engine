"""
Tests for the readability service.
"""

import pytest

from readability.models import EducationLevel, ReadingEase
from readability.service import ReadabilityService


class TestReadabilityService:
    @pytest.fixture
    def service(self):
        return ReadabilityService()

    def test_analyze_simple_text(self, service: ReadabilityService):
        """Test analyzing simple text."""
        text = "This is a simple sentence. It has two parts."
        result = service.analyze(text)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 1
        assert result.flesch_reading_ease > 0
        assert result.flesch_kincaid_grade > 0

    def test_analyze_empty_text(self, service: ReadabilityService):
        """Test analyzing empty text."""
        result = service.analyze("")
        assert result.score == 0
        assert "Empty text provided" in result.issues

    def test_analyze_complex_text(self, service: ReadabilityService):
        """Test analyzing more complex text."""
        text = """
        The concept of readability is often considered in terms of the ease with which 
        individuals can read and understand a piece of text. Various factors contribute 
        to readability, including sentence length, word complexity, and the overall 
        structure of the text. Readability metrics attempt to quantify these factors 
        to provide an objective measure of how difficult a text is to understand.
        """
        result = service.analyze(text)

        assert isinstance(result.score, float)
        assert 0 <= result.score <= 1
        assert result.flesch_reading_ease > 0
        assert result.flesch_kincaid_grade > 0

        # Complex text should have a lower score than simple text
        simple_text = "This is a simple sentence. It has two parts."
        simple_result = service.analyze(simple_text)
        assert result.score < simple_result.score

    def test_reading_ease_interpretation(self, service: ReadabilityService):
        """Test the reading ease interpretation."""
        # Very easy text
        text = "The cat sat on the mat. It was happy."
        result = service.analyze(text)
        assert result.flesch_reading_ease_level == ReadingEase.VERY_EASY.value

        # More complex text
        text = "The feline positioned itself upon the horizontal surface designed for wiping one's feet."
        result = service.analyze(text)
        assert result.flesch_reading_ease_level == ReadingEase.DIFFICULT.value

    def test_grade_level_interpretation(self, service: ReadabilityService):
        """Test the grade level interpretation."""
        # Simple text should have a low grade level
        text = "The cat sat on the mat. It was happy."
        result = service.analyze(text)
        assert result.overall_grade_level == EducationLevel.BASIC_LITERACY.display_name

        # Complex text should have a higher grade level
        text = """
        The concept of readability is often considered in terms of the ease with which 
        individuals can read and understand a piece of text. Various factors contribute 
        to readability, including sentence length, word complexity, and the overall 
        structure of the text.
        """
        result = service.analyze(text)
        assert result.overall_grade_level == EducationLevel.GRADUATE_LEVEL.display_name
