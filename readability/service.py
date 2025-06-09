"""
Readability analysis service for the score engine.

This module provides a service for analyzing text readability using various metrics
including Flesch-Kincaid, SMOG, Gunning Fog, and others.
"""

import readtime
from functools import lru_cache
from typing import List, Tuple, Optional

from textstat import textstat
from commons.utils import round_score

from .models import ReadabilityMetric, ReadabilityResult

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

    def analyze(self, text: str, audience: Optional[str] = None) -> ReadabilityResult:
        """
        Analyze the text for readability.

        Args:
            text: The text to analyze
            audience: Optional target audience for evaluation

        Returns:
            ReadabilityResult object containing the score and issues
        """
        # Create a cache key that includes both text and audience
        cache_key = (text, audience)

        # Check if we have a cached result
        if hasattr(self, "_analyze_cache") and cache_key in self._analyze_cache:
            return self._analyze_cache[cache_key]

        # Call the implementation and cache the result
        result = self._analyze_impl(text)

        # Apply audience evaluation if needed
        if audience:
            result.evaluate_for_audience(audience)

        # Initialize cache if it doesn't exist
        if not hasattr(self, "_analyze_cache"):
            self._analyze_cache = {}

        # Cache the result with the combined key
        self._analyze_cache[cache_key] = result
        return result

    def _cap_metric(self, metric: ReadabilityMetric) -> ReadabilityMetric:
        """
        Ensure metric values are within valid ranges.

        Args:
            metric: ReadabilityMetric object to validate

        Returns:
            Validated ReadabilityMetric object
        """
        metric.flesch_reading_ease = max(0, min(100, metric.flesch_reading_ease))
        metric.dale_chall_score = max(0, min(10, metric.dale_chall_score))
        metric.avg_words_per_sentence = max(0, metric.avg_words_per_sentence)
        return metric

    def _calculate_metrics(self, text: str) -> ReadabilityMetric:
        """
        Calculate essential readability metrics.

        Args:
            text: Input text to analyze

        Returns:
            ReadabilityMetric object containing the calculated metrics
        """
        # Skip empty or whitespace-only text
        if not text or not text.strip():
            return ReadabilityMetric(
                flesch_reading_ease=100.0,  # Perfect score for empty text
                dale_chall_score=0.0,  # Easiest possible score
                avg_words_per_sentence=0.0,  # No sentences
            )

        # Calculate essential metrics
        flesch = textstat.flesch_reading_ease(text)
        dale_chall = textstat.dale_chall_readability_score(text)

        # Calculate average words per sentence
        words = textstat.lexicon_count(text, removepunct=True)
        sentences = textstat.sentence_count(text)
        avg_words = words / max(1, sentences)  # Avoid division by zero

        metrics = ReadabilityMetric(
            flesch_reading_ease=flesch,
            dale_chall_score=dale_chall,
            avg_words_per_sentence=avg_words,
        )

        return self._cap_metric(metrics)

    def _generate_issues_and_suggestions(
        self, metrics: ReadabilityMetric
    ) -> Tuple[List[str], List[str]]:
        """
        Generate issues and suggestions based on readability metrics.

        Note: Audience-specific issues are handled in the model's evaluate_for_audience method.
        This method focuses on general readability issues that aren't audience-specific.

        Args:
            metrics: Readability metrics

        Returns:
            Tuple of (issues, suggestions) lists
        """
        issues = []
        suggestions = []

        # Check for extremely low readability that might indicate issues regardless of audience
        if metrics.flesch_reading_ease < 20:
            issues.append("Extremely difficult to read")
            suggestions.append(
                "The text is very difficult to read. Consider simplifying the language, "
                "breaking up long sentences, and explaining technical terms. Aim for shorter "
                "sentences and more common words where possible."
            )
        elif metrics.flesch_reading_ease < 30:
            issues.append("Very difficult to read")
            suggestions.append(
                "The text is quite challenging to read. Consider simplifying some of the "
                "language and sentence structures to improve readability. Shorter sentences "
                "and more common words can help."
            )
        elif metrics.flesch_reading_ease < 50:
            issues.append("Difficult to read")
            suggestions.append(
                "The text may be challenging for some readers. Consider simplifying some "
                "of the more complex language and breaking up longer sentences."
            )

        # Check vocabulary difficulty using Dale-Chall score
        if metrics.dale_chall_score >= 9.0:
            issues.append("Very difficult vocabulary")
            suggestions.append(
                "The vocabulary is very advanced, similar to academic or technical writing. "
                "Consider defining technical terms or using more common alternatives where possible."
            )
        elif metrics.dale_chall_score >= 7.0:
            issues.append("Advanced vocabulary")
            suggestions.append(
                "The text uses some advanced vocabulary. Consider whether all technical terms "
                "are necessary or if they could be explained in simpler terms for better clarity."
            )

        # Check sentence length
        if metrics.avg_words_per_sentence > 25:
            issues.append(
                f"Long average sentence length ({metrics.avg_words_per_sentence:.1f} words)"
            )
            suggestions.append(
                "The average sentence length is quite long, which can make the text harder to read. "
                "Aim for an average of 15-20 words per sentence for better readability. Try breaking "
                "up long sentences into shorter, clearer ones."
            )
        elif metrics.avg_words_per_sentence > 20:
            issues.append(
                f"Slightly long average sentence length ({metrics.avg_words_per_sentence:.1f} words)"
            )
            suggestions.append(
                "Some sentences are quite long. Consider breaking up the longest ones "
                "to improve readability. Aim for an average of 15-20 words per sentence."
            )

        # Check for very short sentences that might make the text choppy
        if metrics.avg_words_per_sentence < 10:
            issues.append(
                f"Short, choppy sentences ({metrics.avg_words_per_sentence:.1f} words on average)"
            )
            suggestions.append(
                "The text contains many very short sentences which can make it feel choppy. "
                "Consider combining some related ideas into more complex sentences for better flow. "
                "Aim for a mix of sentence lengths."
            )

        return issues, suggestions

    def _normalize_metric(
        self, fre: float, dale_chall: float, avg_words: float
    ) -> ReadabilityMetric:
        """
        Normalize different metrics to a 0-1 scale where 0 is best and 1 is worst.

        Args:
            fre: Flesch Reading Ease score
            dale_chall: Dale-Chall score
            avg_words: Average words per sentence

        Returns:
            Normalized ReadabilityMetric with all metrics scaled 0-1
        """
        # Flesch Reading Ease: 90-100 (very easy) to 0-30 (very difficult)
        # Normalize to 0-1 where 0 is best (very easy)
        fre = max(0, min(1, fre / 100.0))

        # Dale-Chall: 4.9 or below (easy) to 10 (difficult)
        # Normalize to 0-1 where 0 is best (easiest)
        dale_chall_min = 4.9
        dale_chall_max = 10.0
        dale_chall = max(
            0,
            min(
                1,
                1 - ((dale_chall - dale_chall_min) / (dale_chall_max - dale_chall_min)),
            ),
        )

        # Sentence length: Ideal is around 15-20 words
        # Normalize to 0-1 where 0 is best (ideal length)
        ideal_length = 17.5
        max_deviation = 30  # Max deviation from ideal we'll consider
        length_deviation = abs(avg_words - ideal_length)
        avg_words = min(1.0, length_deviation / max_deviation)

        return ReadabilityMetric(
            flesch_reading_ease=fre,
            dale_chall_score=dale_chall,
            avg_words_per_sentence=avg_words,
        )

    def _calculate_composite_score(
        self, fre: float, dale_chall: float, avg_words: float
    ) -> float:
        """
        Calculate a composite score from 0-1 based on key readability metrics.

        Args:
            fre: Flesch Reading Ease score
            dale_chall: Dale-Chall score
            avg_words: Average words per sentence

        Returns:
            Composite score from 0-1 where 1 is most readable
        """
        m = self._normalize_metric(fre, dale_chall, avg_words)


        # Sentence length factor (penalize very long sentences)
        # Ideal is around 15-20 words per sentence
        if m.avg_words_per_sentence <= 15:
            sentence_score = 1.0
        elif m.avg_words_per_sentence <= 25:
            # Linear decrease from 15-25 words
            sentence_score = 1.0 - ((m.avg_words_per_sentence - 15) * 0.1)
        else:
            # More severe penalty for very long sentences
            sentence_score = max(0.1, 1.0 - (m.avg_words_per_sentence - 25) * 0.05)

        # Calculate base score as weighted average
        # Flesch Reading Ease is the most important factor (60%)
        # Dale-Chall score is second most important (20%)
        # Sentence length accounts for remaining 20%

        base_score = min(
            1.0,
            ((0.6 * m.flesch_reading_ease) + (0.2 * m.dale_chall_score) + (0.2 * sentence_score))
            * 1.2,
        )
        # Apply adjustments based on text difficulty
        # For very difficult texts (FRE < 30), apply additional penalty
        if m.flesch_reading_ease < 30:
            difficulty_penalty = 0.2 * (1.0 - (m.flesch_reading_ease / 30.0))
            base_score = max(0.1, base_score - difficulty_penalty)

        # Ensure score is within bounds
        return max(0.0, min(1.0, base_score))

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
                flesch_reading_ease=100.0,  # Perfect score for empty text
                dale_chall_score=0.0,  # Easiest possible score
                avg_words_per_sentence=0.0,  # No sentences
                score=1.0,  # Perfect score
                issues=["Empty text provided"],
                suggestions=["Provide some text to analyze"],
                estimated_reading_time=0,
                target_audience=None,
                audience_appropriate=None,
                audience_issues=[],
            )

        # Calculate metrics
        metrics = self._calculate_metrics(text)

        # Generate issues and suggestions
        issues, suggestions = self._generate_issues_and_suggestions(metrics)

        # Calculate composite score
        score = self._calculate_composite_score(
            metrics.flesch_reading_ease,
            metrics.dale_chall_score,
            metrics.avg_words_per_sentence,
        )

        # Calculate estimated reading time
        estimated_reading_time = readtime.of_html(text).seconds

        # Create and return result with simplified metrics
        return ReadabilityResult(
            flesch_reading_ease=round_score(metrics.flesch_reading_ease),
            dale_chall_score=round_score(metrics.dale_chall_score),
            avg_words_per_sentence=round(metrics.avg_words_per_sentence),
            score=round_score(score),
            issues=issues,
            suggestions=suggestions,
            estimated_reading_time=estimated_reading_time,
        )
