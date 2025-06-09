"""
Models for readability analysis results.
"""

from enum import Enum
from typing import List, Optional
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


# Audience to expected grade level mapping (min_grade, max_grade)
AUDIENCE_GRADE_LEVELS = {
    "children": (1, 6),  # Elementary school
    "teenagers": (7, 12),  # Middle to High school
    "young_adults": (11, 14),  # High school to early college
    "general": (6, 12),  # Standard reading level
    "business": (10, 14),  # Professional but accessible
    "professional": (12, 16),  # Technical/professional content
    "academic": (14, 20),  # Academic/research level
}


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
    """Represents essential readability metrics.

    Attributes:
        flesch_reading_ease: Score from 0-100 indicating how easy the text is to read.
            Higher values indicate easier reading. Scores below 30 are very difficult.
        dale_chall_score: Score from 0-10 indicating vocabulary difficulty.
            Lower scores (4.9 or below) indicate easier vocabulary.
        avg_words_per_sentence: Average number of words per sentence.
    """

    flesch_reading_ease: float
    dale_chall_score: float
    avg_words_per_sentence: float 


class ReadabilityResult(BaseModel):
    """Represents the result of a readability analysis.

    Attributes:
        flesch_reading_ease: Score from 0-100 indicating how easy the text is to read.
            Higher values indicate easier reading. Scores below 30 are very difficult.
            - 90-100: Very Easy (5th grade)
            - 80-89: Easy (6th grade)
            - 70-79: Fairly Easy (7th grade)
            - 60-69: Standard (8th-9th grade)
            - 50-59: Fairly Difficult (10th-12th grade)
            - 30-49: Difficult (College level)
            - 0-29: Very Difficult (College graduate level)

        dale_chall_score: Score from 0-10 indicating vocabulary difficulty.
            - 4.9 or lower: Easily understood by an average 4th-grade student
            - 5.0-5.9: Easily understood by an average 5th or 6th-grade student
            - 6.0-6.9: Easily understood by an average 7th or 8th-grade student
            - 7.0-7.9: Easily understood by an average 9th or 10th-grade student
            - 8.0-8.9: Easily understood by an average 11th or 12th-grade student
            - 9.0-9.9: Easily understood by an average college student
            - 10.0: Easily understood by a college graduate

        avg_words_per_sentence: Average number of words per sentence.
            - < 15: Very short sentences
            - 15-20: Average length
            - > 20: Long sentences (may affect readability)

        estimated_reading_time: Estimated reading time in seconds.
        target_audience: The intended audience for the text (if specified).
        score: Composite score from 0-1 where higher is more readable.
        issues: List of identified readability issues.
        suggestions: List of suggestions to improve readability.
        audience_appropriate: Whether the text's reading level matches the target audience.
        audience_issues: List of issues related to audience appropriateness.
    """

    # Core metrics
    flesch_reading_ease: float = Field(..., ge=0, le=100)
    dale_chall_score: float = Field(..., ge=0, le=10)
    avg_words_per_sentence: float = Field(..., ge=0)

    # Additional information
    estimated_reading_time: int = Field(..., ge=0)
    target_audience: Optional[str] = None

    # Analysis results
    score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Base readability score (0-1), higher is more readable",
    )
    audience_adjusted_score: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Score adjusted for target audience (0-1), higher is better for the target audience",
    )
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    audience_appropriate: Optional[bool] = None
    audience_issues: List[str] = Field(default_factory=list)

    @computed_field
    @property
    def overall_grade_level(self) -> str:
        """Return an overall grade level based on Dale-Chall and Flesch scores.

        Returns:
            str: Professional category that best describes the text's reading level.
        """
        # Use Dale-Chall score as primary indicator of grade level
        return EducationLevel.from_grade(self.dale_chall_score).display_name

    def evaluate_for_audience(self, audience: Optional[str] = None) -> None:
        """Evaluate the text's readability for a specific target audience.

        Args:
            audience: The target audience for the text. Can be one of: children, teenagers,
                    young_adults, general, business, professional, academic
        """
        if not audience:
            return

        self.target_audience = audience

        # Get the expected grade level range for the target audience
        min_grade, max_grade = AUDIENCE_GRADE_LEVELS.get(
            audience.lower(), (6, 12)  # Default to general audience
        )

        # Reset audience-related fields
        self.audience_appropriate = True
        self.audience_adjusted_score = self.score
        self.audience_issues = []

        # Determine text difficulty based on Dale-Chall score
        # Map Dale-Chall score to approximate grade level (simplified)
        if self.dale_chall_score <= 4.9:
            text_grade = 4
        elif self.dale_chall_score <= 5.9:
            text_grade = 6
        elif self.dale_chall_score <= 6.9:
            text_grade = 8
        elif self.dale_chall_score <= 7.9:
            text_grade = 10
        elif self.dale_chall_score <= 8.9:
            text_grade = 12
        elif self.dale_chall_score <= 9.9:
            text_grade = 14  # College
        else:
            text_grade = 16  # Graduate


        # Check if the text's grade level is appropriate for the audience
        if text_grade < min_grade:
            self.audience_appropriate = False
            if audience in ["professional", "academic"]:
                self.audience_issues.append(
                    "The text may be too basic for the target academic/professional audience. "
                    "Consider using more precise terminology and complex sentence structures."
                )
            else:
                self.audience_issues.append(
                    f"The text may be too simple for the target {audience} audience. "
                    f"Consider using more sophisticated language and complex sentence structures."
                )
        elif text_grade > max_grade:
            # For academic/professional audiences, complex text is often expected
            if audience in ["professional", "academic"]:
                self.audience_issues.append(
                    "The text uses appropriately complex language for an academic/professional audience."
                )
                # Apply a boost for appropriate complexity
                complexity_boost = min(0.2, (text_grade - max_grade) * 0.03)
                self.audience_adjusted_score = min(1.0, self.score + complexity_boost)
            else:
                self.audience_appropriate = False
                if text_grade >= 14:  # College level or above
                    self.audience_issues.append(
                        "The text uses highly specialized language typically found in academic or "
                        "expert-level content. Consider if this level of complexity is necessary "
                        f"for your {audience} audience, or provide additional explanations."
                    )
                else:
                    self.audience_issues.append(
                        f"The text may be too complex for the target {audience} audience. "
                        "Consider simplifying the language or providing additional explanations "
                        "for technical terms."
                    )
                # Apply a penalty for inappropriate complexity
                penalty = min(0.3, (text_grade - max_grade) * 0.05)
                self.audience_adjusted_score = max(0.1, self.score - penalty)
        else:
            # Text is within the appropriate range for the audience
            self.audience_appropriate = True
            self.audience_adjusted_score = self.score

            # For academic/professional audiences, give a small boost for more complex text
            boost = 0.2
            if audience in ["professional", "academic"] and text_grade > (
                min_grade + 2
            ):
                boost = 0.4
            boost = min(boost, (text_grade - min_grade) * 0.02)
            self.audience_adjusted_score = min(1.0, self.score + boost)

        # If we haven't set an adjusted score yet (shouldn't happen, but just in case)
        if not hasattr(self, "audience_adjusted_score"):
            self.audience_adjusted_score = self.score

        # Add a message if the text is well-matched for professional/academic audiences
        if audience in ["professional", "academic"] and self.audience_appropriate:
            self.audience_issues.append(
                f"Text complexity is well-matched for {audience} audiences. "
                "Audience-adjusted score has been slightly increased."
            )

    @computed_field
    @property
    def flesch_reading_ease_level(self) -> str:
        """Return a human-readable interpretation of the Flesch Reading Ease score."""
        return ReadingEase.from_score(self.flesch_reading_ease).value

    def __str__(self) -> str:
        """Return a formatted string representation of the readability result."""
        result = [
            "\n=== Readability Analysis ===",
            f"Flesch Reading Ease: {self.flesch_reading_ease:.1f} ({self.flesch_reading_ease_level})",
            f"Dale-Chall Score: {self.dale_chall_score:.1f} ({self.overall_grade_level})",
            f"Avg. Words per Sentence: {self.avg_words_per_sentence:.1f}",
            f"Estimated Reading Time: {self.estimated_reading_time // 60} minutes {self.estimated_reading_time % 60} seconds",
            f"Readability Score: {self.score:.2f}/1.00",
        ]

        if self.audience_adjusted_score is not None:
            result.append(
                f"Audience-Adjusted Score: {self.audience_adjusted_score:.2f}/1.00"
            )

        if self.issues:
            result.extend(["\nIssues:", *[f"- {issue}" for issue in self.issues]])

        if self.suggestions:
            result.extend(
                [
                    "\nSuggestions:",
                    *[f"- {suggestion}" for suggestion in self.suggestions],
                ]
            )

        if self.audience_issues:
            result.extend(
                [
                    "\nAudience Feedback:",
                    *[f"- {issue}" for issue in self.audience_issues],
                ]
            )

        return "\n".join(result)
