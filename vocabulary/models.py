from enum import Enum
from pydantic import BaseModel
from typing import List
from commons.models import ErrorCategory, TextIssue


class LexicalDiversityResult(BaseModel):
    ttr: float
    word_count: int
    unique_count: int

    def __str__(self) -> str:
        return (
            "\nLexical Diversity Breakdown:\n"
            f"\tTTR: {self.ttr}\n"
            f"\tWord count: {self.word_count}\n"
            f"\tUnique count: {self.unique_count}\n"
        )


class SophisticationLevel(Enum):
    BASIC = "Basic Vocabulary"
    CONVERSATIONAL = "Conversational Range"
    ACADEMIC = "Academic Range"
    ADVANCED = "Advanced Vocabulary"
    ERUDITE = "Erudite and Specialized"

    @classmethod
    def get_level(cls, score: float):
        if score < 0.2:
            return SophisticationLevel.BASIC
        elif score < 0.45:
            return SophisticationLevel.CONVERSATIONAL
        elif score < 0.6:
            return SophisticationLevel.ACADEMIC
        elif score < 0.95:
            return SophisticationLevel.ADVANCED
        else:
            return SophisticationLevel.ERUDITE


class SophisticationResult(BaseModel):
    """
    Represents sophistication analysis of vocabulary.

    Attributes:
        score: Final sophistication score [0-1]
        word_count: Total words analyzed
        common_count: Words with high frequency
        mid_count: Medium-frequency words
        rare_count: Rare/advanced words
        level: Sophistication level
    """

    score: float
    word_count: int
    common_count: int
    mid_count: int
    rare_count: int
    level: SophisticationLevel

    def __str__(self) -> str:
        return (
            "\nSophistication Breakdown:\n"
            f"\tScore: {self.score}\n"
            f"\tWord count: {self.word_count}\n"
            f"\tCommon: {self.common_count}, Mid: {self.mid_count}, Rare: {self.rare_count}\n"
            f"\tLevel: {self.level.value}\n"
        )


class PrecisionScoreBreakdown(BaseModel):
    """
    Breakdown of precision issues by category.

    Attributes:
        category: ErrorCategory (limited to WORD_USAGE, STYLISTIC_ISSUES)
        count: Number of issues in that category
        penalty: Penalty based on severity
    """

    category: ErrorCategory
    count: int
    penalty: float


class PrecisionResult(BaseModel):
    """
    Represents the result of a vocabulary precision check.

    Attributes:
        score: Normalized precision penalty score [0 - 1]
        word_count: Total words in the input text
        normalized_penalty: Total normalized penalty
        issues: List of relevant TextIssues
        breakdown: Per-category count and penalty
    """

    score: float
    word_count: int
    normalized_penalty: float
    issues: List[TextIssue]
    breakdown: List[PrecisionScoreBreakdown]

    def __str__(self) -> str:
        issues_str = "\n".join(
            f"\t- {issue.message} (Category: {issue.category.label}, Severity: {issue.category.severity}, Rule issue type: {issue.rule_issue_type}, Location: {issue.start_offset}-{issue.end_offset}, Word: {issue.original_text[issue.start_offset:issue.end_offset]})"
            for issue in self.issues
        )
        breakdown_str = "\n".join(
            f"\t- {b.category.label}: {b.count} issues, Penalty: {b.penalty}"
            for b in self.breakdown
        )
        return (
            "\nPrecision Breakdown:\n"
            f"\tScore: {self.score}\n"
            f"\tWord count: {self.word_count}\n"
            f"\tNormalized penalty: {self.normalized_penalty}\n\n"
            f"\tIssues:\n{issues_str}\n\n\tBreakdown:\n{breakdown_str}\n"
        )


class VocabularyResult(BaseModel):
    """
    Aggregated vocabulary score including lexical diversity, sophistication and precision.
    """

    score: float  # Final vocabulary score [0-1]
    sophistication: SophisticationResult
    precision: PrecisionResult
    lexical_diversity: LexicalDiversityResult

    def __str__(self) -> str:
        return (
            "\n"
            + "-" * 8
            + " Vocabulary Score: "
            + str(self.score)
            + " "
            + "-" * 8
            + "\n"
            f"\t{self.lexical_diversity}\n"
            f"\t{self.sophistication}\n"
            f"\t{self.precision}"
        )
