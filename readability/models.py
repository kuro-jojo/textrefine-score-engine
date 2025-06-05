"""
Models for readability analysis results.
"""

from enum import Enum
from typing import List
from pydantic import BaseModel, Field, computed_field


class ReadingEase(Enum):
    """Represents different levels of reading ease based on Flesch Reading Ease scores."""

    VERY_EASY = "Very Easy to read"
    EASY = "Easy to read"
    FAIRLY_EASY = "Fairly Easy to read"
    STANDARD = "Standard"
    FAIRLY_DIFFICULT = "Fairly Difficult to read"
    DIFFICULT = "Difficult to read"
    VERY_CONFUSING = "Very Confusing to read"

    @classmethod
    def from_score(cls, score: float) -> "ReadingEase":
        """Get the reading ease level from a Flesch Reading Ease score."""
        if score >= 90:
            return cls.VERY_EASY
        elif score >= 80:
            return cls.EASY
        elif score >= 70:
            return cls.FAIRLY_EASY
        elif score >= 60:
            return cls.STANDARD
        elif score >= 50:
            return cls.FAIRLY_DIFFICULT
        elif score >= 30:
            return cls.DIFFICULT
        else:
            return cls.VERY_CONFUSING


class EducationLevel(int, Enum):
    """Represents different education levels based on grade scores."""

    BASIC_LITERACY = 1
    GENERAL_PUBLIC = 2
    HIGH_SCHOOL_LEVEL = 3
    HIGH_SCHOOL_GRADUATE = 4
    COLLEGE_LEVEL = 5
    GRADUATE_LEVEL = 6
    PROFESSIONAL = 7

    @classmethod
    def from_grade(cls, grade: float) -> "EducationLevel":
        """Convert a grade level to the appropriate EducationLevel."""
        if grade <= 6:
            return cls.BASIC_LITERACY
        elif grade <= 8:
            return cls.GENERAL_PUBLIC
        elif grade <= 10:
            return cls.HIGH_SCHOOL_LEVEL
        elif grade <= 12:
            return cls.HIGH_SCHOOL_GRADUATE
        elif grade <= 14:
            return cls.COLLEGE_LEVEL
        elif grade <= 18:
            return cls.GRADUATE_LEVEL
        else:
            return cls.PROFESSIONAL

    @property
    def display_name(self) -> str:
        """Get the display name for the education level."""
        names = {
            self.BASIC_LITERACY: "Basic Literacy (Elementary School)",
            self.GENERAL_PUBLIC: "General Public (Middle School)",
            self.HIGH_SCHOOL_LEVEL: "High School Level",
            self.HIGH_SCHOOL_GRADUATE: "High School Graduate",
            self.COLLEGE_LEVEL: "College Level",
            self.GRADUATE_LEVEL: "Graduate Level",
            self.PROFESSIONAL: "Professional / Academic",
        }
        return names[self]


class ReadabilityMetric(BaseModel):
    """Represents a single readability metric result."""

    flesch_reading_ease: float
    flesch_kincaid_grade: float
    smog_index: float
    gunning_fog: float
    automated_readability_index: float
    coleman_liau_index: float
    dale_chall_score: float


class ReadabilityResult(BaseModel):
    """Represents the result of a readability analysis.

    Attributes:
        flesch_reading_ease: Score from 0-100 indicating how easy the text is to read.
            Higher values indicate easier reading. Scores below 30 are considered very difficult.

        flesch_kincaid_grade: Indicates the US school grade level needed to understand the text.
            For example, 8.0 means an 8th grader can understand.

        smog_index: Estimates the years of education needed to understand the text.
            Stands for 'Simple Measure of Gobbledygook'.

        gunning_fog: Estimates the years of formal education needed to understand the text.
            More weight is given to complex sentences and polysyllabic words.

        automated_readability_index: Estimates the US grade level needed to understand the text.
            Based on characters per word and words per sentence.

        coleman_liau_index: Estimates the US grade level needed to understand the text.
            Based on characters per word and sentences per 100 words.

        dale_chall_score: Score from 0-1 indicating text difficulty based on familiar words.
            Higher values indicate more difficult text.

        score: Composite score from 0-1 where higher is better.
            Combines all metrics into a single, easy-to-interpret value.

        reading_ease: Human-readable interpretation of the Flesch Reading Ease score.

        overall_grade_level: Human-readable interpretation of the overall grade level.

        estimated_reading_time: Estimated reading time in seconds.
    """

    # Core metrics with professional interpretation
    flesch_reading_ease: float = Field(..., ge=0, le=100)
    flesch_kincaid_grade: float = Field(..., ge=0, le=20)
    smog_index: float = Field(..., ge=0, le=20)
    gunning_fog: float = Field(..., ge=0, le=20)
    automated_readability_index: float = Field(..., ge=0, le=20)
    coleman_liau_index: float = Field(..., ge=0, le=20)
    dale_chall_score: float = Field(..., ge=0, le=10)
    estimated_reading_time: int = Field(..., ge=0)

    # Composite score (0-1 where higher is better)
    score: float = Field(..., ge=0, le=1)

    # Issues and suggestions
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def overall_grade_level(self) -> str:
        """Return an overall grade level and professional interpretation.

        Returns:
            str: Professional category that best describes the text's reading level.
        """
        avg_grade = (
            self.flesch_kincaid_grade
            + self.smog_index
            + self.gunning_fog
            + self.automated_readability_index
            + self.coleman_liau_index
        ) / 5

        return EducationLevel.from_grade(avg_grade).display_name

    @computed_field
    @property
    def flesch_reading_ease_level(self) -> str:
        """Return a human-readable interpretation of the Flesch Reading Ease score."""
        return ReadingEase.from_score(self.flesch_reading_ease).value

    def __str__(self) -> str:
        """Return a string representation of the readability analysis."""
        return (
            f"Readability Analysis (Score: {self.score:.2f}):\n"
            f"  • Reading Ease: {self.flesch_reading_ease:.1f} ({self.flesch_reading_ease_level})\n"
            f"  • Grade Level: ~{self.overall_grade_level} (Avg. Grade: {self.flesch_kincaid_grade:.1f})\n"
            f"  • Estimated Reading Time: {self.estimated_reading_time} seconds\n"
        )
