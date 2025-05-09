from typing import List
from pydantic import BaseModel
from commons.models import ErrorCategory, TextIssue


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
                f"\t- {issue.message} (Category: {issue.category.label}, Severity: {issue.category.severity}, Rule issue type: {issue.rule_issue_type}, Location: {issue.start_offset}-{issue.end_offset}, Word: {issue.original_text[issue.start_offset:issue.end_offset]})"
                for issue in self.issues
            ]
        )
        breakdown_str = "\n".join(
            [
                f"\t- {breakdown.category.label}: {breakdown.count} issues, Penalty: {breakdown.penalty}"
                for breakdown in self.breakdown
            ]
        )
        return (
            "\n"
            + "-" * 8
            + " Correctness Score: "
            + str(self.score)
            + " "
            + "-" * 8
            + "\n\n"
            f"\tWord count: {self.word_count}\n"
            f"\tNormalized penalty: {self.normalized_penalty}\n"
            "\tIssues:\n" + issues_str + "\n"
            "\tCategory breakdown:\n" + breakdown_str
        )
