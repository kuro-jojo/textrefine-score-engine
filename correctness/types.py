from enum import Enum
from dataclasses import dataclass
from typing import List

from enum import Enum
from pydantic import BaseModel


class ErrorCategory(Enum):
    GRAMMAR_RULES = ("Grammar Rules", 3)
    MECHANICS = ("Mechanics", 2)
    SPELLING_TYPING = ("Spelling & Typos", 1)
    WORD_USAGE = ("Word Usage", 2)
    MEANING_LOGIC = ("Meaning & Logic", 4)
    STYLISTIC_ISSUES = ("Stylistic Issues", 1)
    CONTEXTUAL_STYLE = ("Contextual Style", 1)

    def __init__(self, label: str, severity: int):
        self.label = label
        self.severity = severity  # 1 (low impact) to 5 (high impact)

    @classmethod
    def from_language_tool_category(cls, category: str) -> "ErrorCategory":
        """Map LanguageTool category to TextRefine group."""
        category = category.lower()

        if category in {"grammar", "capitalization", "upper/lowercase"}:
            return cls.GRAMMAR_RULES

        if category in {
            "punctuation",
            "compounding",
            "orthographic errors",
            "typography",
        }:
            return cls.MECHANICS

        if category in {"spelling", "possible typo", "nonstandard phrases"}:
            return cls.SPELLING_TYPING

        if category in {"commonly confused words", "collocations", "redundant phrases"}:
            return cls.WORD_USAGE

        if category in {"semantics", "text analysis"}:
            return cls.MEANING_LOGIC

        if category in {
            "style",
            "repetitions (style)",
            "stylistic hints",
            "plain english",
            "miscellaneous",
        }:
            return cls.STYLISTIC_ISSUES

        if category in {"academic writing", "creative writing", "wikipedia"}:
            return cls.CONTEXTUAL_STYLE

        return cls.STYLISTIC_ISSUES


@dataclass
class Replacement:
    value: str


class TextIssue(BaseModel):
    message: str
    replacements: List[Replacement]
    sentence: str
    error_text: str
    start_offset: int
    issue_type: str
    category: ErrorCategory
    rule_id: str

    @property
    def end_offset(self) -> int:
        return self.start_offset + len(self.error_text)

    @property
    def penalty(self) -> int:
        return self.category.severity

    def __str__(self) -> str:
        return (
            f"Error: {self.message}\n"
            f"Type: {self.issue_type}\n"
            f"Category: {self.category.label}\n"
            f"Rule: {self.rule_id}\n"
            f"Replacements: {[r.value for r in self.replacements]}\n"
            f"Sentence: {self.sentence}\n"
            f"Error text: {self.error_text}\n"
            f"Start offset: {self.start_offset}\n"
            f"End offset: {self.end_offset}\n"
            f"Penalty: {self.penalty}\n"
        )


class CorrectnessScoreBreakdown(BaseModel):
    """
    Breakdown of correctness issues by category.

    Attributes:
        category: ErrorCategory of the issues
        count: Number of issues in the category
        penalty: Penalty of the issues in the category
    """

    category: ErrorCategory
    count: int
    penalty: float


class CorrectnessResult(BaseModel):
    """
    Represents the result of a correctness check.

    Attributes:
        score: Overall score of the text
        word_count: Number of words in the text
        normalized_penalty: Overall penalty of the issues in the text
        issues: List of all issues found in the text
        breakdown: Breakdown of issues by category
    """

    score: float
    word_count: int
    normalized_penalty: float
    issues: List[TextIssue]
    breakdown: List[CorrectnessScoreBreakdown]

    def __str__(self) -> str:
        issues_str = "\n".join(
            [
                f"- {issue.message} (Category: {issue.category.label}, Severity: {issue.category.severity})"
                for issue in self.issues
            ]
        )
        breakdown_str = "\n".join(
            [
                f"- {breakdown.category.label}: {breakdown.count} issues, Penalty: {breakdown.penalty}"
                for breakdown in self.breakdown
            ]
        )
        return (
            "\nScore breakdown:\n"
            f"Score: {self.score}\n"
            f"Word count: {self.word_count}\n"
            f"Normalized penalty: {self.normalized_penalty}\n"
            "\nIssues:\n"
            "\nCategory breakdown:\n" + issues_str + "\n" + breakdown_str
        )
