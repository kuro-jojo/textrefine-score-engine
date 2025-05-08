from typing import List
from pydantic import BaseModel
from language_tool.models import ErrorCategory


class TextIssue(BaseModel):
    """
    Represents a single issue found in a text.

    Attributes:
        message: The message of the issue
        replacements: List of possible replacements for the issue
        error_text: The text that contains the issue
        error_length: The length of the error
        start_offset: The start offset of the issue in the text
        category: The category of the issue
        rule_issue_type: The rule issue type of the issue (e.g. grammar, spelling)
    """

    message: str
    replacements: List[str]
    error_text: str
    error_length: int
    start_offset: int
    category: ErrorCategory
    rule_issue_type: str

    @property
    def end_offset(self) -> int:
        """The end offset of the issue in the text (exclusive)."""
        return self.start_offset + self.error_length

    @property
    def penalty(self) -> int:
        """The penalty of the issue."""
        return self.category.severity

    def __str__(self) -> str:
        return (
            f"Error: {self.message}\n"
            f"Category: {self.category.label}\n"
            f"Rule issue type: {self.rule_issue_type}\n"
            f"Replacements: {self.replacements}\n"
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
                f"- {issue.message} (Category: {issue.category.label}, Severity: {issue.category.severity}, Rule issue type: {issue.rule_issue_type})"
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
