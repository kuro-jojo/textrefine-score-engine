from typing import List, Optional
from functools import lru_cache

from language_tool_python import Match
from correctness.models import CorrectnessResult, TextIssue, CorrectnessScoreBreakdown
from language_tool.models import ErrorCategory
from language_tool.service import language_tool_service
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_SCORE = 100
WORD_COUNT_NORMALIZATION = 100


class CorrectnessService:
    """
    Service for computing text correctness scores.
    """

    def __init__(self):
        self._compute_score = lru_cache(maxsize=128)(self._compute_score_impl)

    def compute_score(self, text: str) -> Optional[CorrectnessResult]:
        return self._compute_score(text)

    def _compute_score_impl(self, text: str) -> Optional[CorrectnessResult]:
        """
        Compute the correctness score for the given text using LanguageTool.

        Args:
            text: The text to analyze

        Returns:
            CorrectnessResult object containing the score and issues, or None if error occurs
        """
        try:
            # Get matches from LanguageTool
            matches: List[Match] = language_tool_service.check(text)
            logger.info(f"Found {len(matches)} matches for text: {text[:10]}...")
            # Convert matches to TextIssue objects
            issues = [
                TextIssue(
                    message=match.message,
                    replacements=[rep for rep in match.replacements],
                    error_text=match.context,
                    error_length=match.errorLength,
                    start_offset=match.offset,
                    category=ErrorCategory.from_language_tool_category(match.category),
                    rule_issue_type=f"{match.category} - {match.ruleIssueType}",
                )
                for match in matches
            ]

            # Compute the score
            result = self._score_text_issues(len(text.split()), issues)
            logger.info(f"Computed score: {result.score} for text: {text[:10]}...")
            return result

        except Exception as e:
            logger.error(f"Error computing score: {e}")
            return None

    def _score_text_issues(
        self, word_count: int, issues: List[TextIssue]
    ) -> CorrectnessResult:
        """
        Score text issues by category and type.

        Args:
            word_count: Number of words in the text
            issues: List of TextIssue objects

        Returns:
            CorrectnessResult object with score and breakdown
        """
        categories = {}
        total_penalty = 0

        # Count issues by category and type
        for issue in issues:
            if issue.category in categories:
                categories[issue.category].count += 1
                categories[issue.category].penalty += issue.penalty
            else:
                categories[issue.category] = CorrectnessScoreBreakdown(
                    category=issue.category,
                    count=1,
                    penalty=issue.penalty,
                )
            total_penalty += issue.penalty

        normalized_penalty = total_penalty / (word_count / WORD_COUNT_NORMALIZATION)
        score = max(0, MAX_SCORE - normalized_penalty)

        return CorrectnessResult(
            score=score,
            word_count=word_count,
            normalized_penalty=normalized_penalty,
            issues=issues,
            breakdown=list(categories.values()),
        )
