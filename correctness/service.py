"""
Module for computing text correctness scores using LanguageTool.

This module provides services for analyzing text for grammatical and stylistic issues,
computing correctness scores, and generating detailed breakdowns of potential issues.
"""

import logging
from typing import List, Optional
from functools import lru_cache

from language_tool_python.utils import LanguageToolError

from commons.models import TextIssue
from correctness.models import CorrectnessResult, CorrectnessScoreBreakdown
from language_tool.service import language_tool_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CorrectnessService:
    """
    Service for computing text correctness scores.
    """

    def __init__(self, language: str = "en-US"):
        self._compute_score = lru_cache(maxsize=128)(self._compute_score_impl)
        self._language_tool_service = language_tool_service
        self._language_tool_service.set_language(language)

    def compute_score(self, text: str) -> Optional[CorrectnessResult]:
        """
        Compute the correctness score for the given text.

        Args:
            text: The text to analyze

        Returns:
            CorrectnessResult object containing the score and issues,
            or None if error occurs
        """
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
            issues = self._language_tool_service.get_text_issues(text)
            result = self._score_text_issues(len(text.split()), issues)
            # logger.info(
            #     f"Computed correctness score: {result.score} for text: {text[:30]}..."
            # )
            return result

        except LanguageToolError as e:
            logger.error("Error calling LanguageTool API: %s", str(e))
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error computing correctness score: %s", str(e))
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

        normalized_penalty = round(total_penalty / max(1, word_count), 4)
        score = round(1 / (1 + normalized_penalty), 4)  # Use sigmoid like function

        return CorrectnessResult(
            score=score,
            word_count=word_count,
            normalized_penalty=normalized_penalty,
            issues=issues,
            breakdown=list(categories.values()),
        )
