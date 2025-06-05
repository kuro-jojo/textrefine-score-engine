"""
Readability analysis service for the score engine.

This module provides a service for analyzing text readability using various metrics
including Flesch-Kincaid, SMOG, Gunning Fog, and others.
"""

import logging
import readtime
from functools import lru_cache
from typing import List, Tuple

from textstat import textstat
from commons.utils import round_score

from .models import ReadabilityMetric, ReadabilityResult

logger = logging.getLogger(__name__)


class ReadabilityService:
    """
    Service for analyzing text readability using various metrics.
    """

    def __init__(self, lang: str = "en"):
        """
        Initialize the ReadabilityService.

        Args:
            lang: Language code (default: 'en')
        """
        self.lang = lang

        # Configure textstat
        textstat.set_lang(lang)

        # Cache the analyze method for better performance
        self._analyze = lru_cache(maxsize=128)(self._analyze_impl)

    def analyze(self, text: str) -> ReadabilityResult:
        """
        Analyze the text for readability.

        Args:
            text: The text to analyze

        Returns:
            ReadabilityResult object containing the score and issues
        """
        return self._analyze(text)

    def _cap_metric(self, metric: ReadabilityMetric) -> ReadabilityMetric:
        """
        Cap metric values to a maximum value.

        Args:
            metric: ReadabilityMetric object to cap

        Returns:
            Capped ReadabilityMetric object
        """
        metric.flesch_reading_ease = max(0, min(100, metric.flesch_reading_ease))
        metric.flesch_kincaid_grade = max(0, min(20, metric.flesch_kincaid_grade))
        metric.smog_index = max(0, min(20, metric.smog_index))
        metric.gunning_fog = max(0, min(20, metric.gunning_fog))
        metric.automated_readability_index = max(
            0, min(20, metric.automated_readability_index)
        )
        metric.coleman_liau_index = max(0, min(20, metric.coleman_liau_index))
        metric.dale_chall_score = max(0, min(10, metric.dale_chall_score))

        return metric

    def _calculate_metrics(self, text: str) -> ReadabilityMetric:
        """
        Calculate all readability metrics.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing all readability metrics
        """

        return self._cap_metric(
            ReadabilityMetric(
                flesch_reading_ease=textstat.flesch_reading_ease(text),
                flesch_kincaid_grade=textstat.flesch_kincaid_grade(text),
                smog_index=textstat.smog_index(text),
                gunning_fog=textstat.gunning_fog(text),
                automated_readability_index=textstat.automated_readability_index(text),
                coleman_liau_index=textstat.coleman_liau_index(text),
                dale_chall_score=textstat.dale_chall_readability_score(text),
            )
        )

    def _generate_issues_and_suggestions(
        self, metrics: ReadabilityMetric
    ) -> Tuple[List[str], List[str]]:
        """
        Generate issues and suggestions based on readability metrics.

        Args:
            metrics: Readability metrics

        Returns:
            Tuple of (issues, suggestions) lists
        """
        issues = []
        suggestions = []

        # Check reading level
        if metrics.flesch_reading_ease < 30:
            issues.append("Very difficult to read")
            suggestions.append(
                "The text is very difficult to read. Consider simplifying sentence structure and vocabulary."
            )
        elif metrics.flesch_reading_ease < 50:
            issues.append("Difficult to read")
            suggestions.append(
                "The text may be challenging for many readers. Consider simplifying some complex sentences."
            )

        # Check for high grade level
        avg_grade = (
            metrics.flesch_kincaid_grade
            + metrics.smog_index
            + metrics.gunning_fog
            + metrics.automated_readability_index
            + metrics.coleman_liau_index
        ) / 5

        if avg_grade > 16:
            issues.append("Highly specialized language")
            suggestions.append(
                "The text uses highly specialized language suitable for experts. Consider if this level of complexity is necessary for your audience."
            )

        # Check Dale-Chall score for difficult vocabulary
        if metrics.dale_chall_score > 0.8:
            issues.append("Complex vocabulary")
            suggestions.append(
                "The text contains many words that may be unfamiliar to general readers. Consider using more common alternatives where possible."
            )

        return issues, suggestions

    def _normalize_metric(self, metric: ReadabilityMetric) -> float:
        """
        Normalize different metrics to a 0-1 scale where 0 is best and 1 is worst.

        Args:
            metric: ReadabilityMetric object

        Returns:
            Normalized value between 0 and 1
        """
        metric.flesch_reading_ease = max(
            0, min(1, 1 - (metric.flesch_reading_ease / 100))
        )
        metric.flesch_kincaid_grade = max(0, min(1, metric.flesch_kincaid_grade / 20.0))
        metric.smog_index = max(0, min(1, metric.smog_index / 20.0))
        metric.gunning_fog = max(0, min(1, metric.gunning_fog / 20.0))
        metric.automated_readability_index = max(
            0, min(1, metric.automated_readability_index / 20.0)
        )
        metric.coleman_liau_index = max(0, min(1, metric.coleman_liau_index / 20.0))
        metric.dale_chall_score = max(
            0, min(1, (metric.dale_chall_score - 4.9) / (10.6 - 4.9))
        )

        return metric

    def _calculate_composite_score(self, metrics: ReadabilityMetric) -> float:
        """
        Calculate a composite readability score (0-1) where higher is better.

        Args:
            metrics: ReadabilityMetric object

        Returns:
            Composite score between 0 and 1 where 1 is most readable
        """
        m = self._cap_metric(metrics).model_copy()
        # Normalize all metrics to 0-1 scale where 0 is best and 1 is worst
        normalized = self._normalize_metric(m)

        # Weighted average - adjust weights as needed
        weights = {
            "flesch_reading_ease": 0.25,
            "flesch_kincaid_grade": 0.15,
            "smog_index": 0.15,
            "gunning_fog": 0.15,
            "automated_readability_index": 0.1,
            "coleman_liau_index": 0.1,
            "dale_chall_score": 0.1,
        }

        # Calculate weighted sum (lower is better)
        weighted_sum = sum(
            weight * normalized.__getattribute__(metric)
            for metric, weight in weights.items()
        )

        # Return inverted score so higher is better
        return 1.0 - weighted_sum

    def _analyze_impl(self, text: str) -> ReadabilityResult:
        """
        Analyze text for readability (implementation).

        Args:
            text: Text to analyze

        Returns:
            ReadabilityResult object with analysis
        """
        if not text.strip():
            return ReadabilityResult(
                flesch_reading_ease=0,
                flesch_kincaid_grade=0,
                smog_index=0,
                gunning_fog=0,
                automated_readability_index=0,
                coleman_liau_index=0,
                dale_chall_score=0,
                score=0,
                issues=["Empty text provided"],
                suggestions=["Provide some text to analyze"],
                estimated_reading_time=0,
            )

        # Calculate metrics
        metrics = self._calculate_metrics(text)

        # Generate issues and suggestions
        issues, suggestions = self._generate_issues_and_suggestions(metrics)

        # Calculate composite score
        score = self._calculate_composite_score(metrics)

        # Calculate estimated reading time
        estimated_reading_time = readtime.of_html(text).seconds

        # Create and return result
        return ReadabilityResult(
            flesch_reading_ease=round_score(metrics.flesch_reading_ease),
            flesch_kincaid_grade=round_score(metrics.flesch_kincaid_grade),
            smog_index=round_score(metrics.smog_index),
            gunning_fog=round_score(metrics.gunning_fog),
            automated_readability_index=round_score(
                metrics.automated_readability_index
            ),
            coleman_liau_index=round_score(metrics.coleman_liau_index),
            dale_chall_score=round_score(metrics.dale_chall_score),
            score=round_score(score),
            issues=issues,
            suggestions=suggestions,
            estimated_reading_time=estimated_reading_time,
        )
