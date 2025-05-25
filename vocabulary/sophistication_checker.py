"""
This module provides a class for evaluating the sophistication of words in a text.

The evaluation is based on the frequency of words in the language, with words that are
more rare being considered more sophisticated. The sophistication score is a value
between 0 and 1, where 0 is a text with only very common words and 1 is a text with
only very rare words.

The class also provides a method for computing the sophistication score of a text.
"""

import math
from typing import Literal, Set
from spacy.language import Language
from spacy.tokens import Doc
from wordfreq import zipf_frequency
from vocabulary.models import (
    SophisticationLevel,
    SophisticationResult,
    SophisticationScoreBreakdown,
    WordFrequencyGroup,
)
from vocabulary.constants import (
    COMMON_WORDS_THRESHOLD,
    MID_WORDS_THRESHOLD,
    RARE_WORDS_WEIGHT,
    MID_WORDS_WEIGHT,
    COMMON_WORDS_WEIGHT,
    UNKNOWN_WORDS_WEIGHT,
)


class SophisticationChecker:
    """
    Evaluates the sophistication of words in a text.

    The sophistication score is a value between 0 and 1, where 0 is a text with only
    very common words and 1 is a text with only very rare words.
    """

    def __init__(self, nlp: Language):
        """
        Initializes the evaluator.

        :param nlp: The spaCy language model
        """
        self.nlp = nlp

    def evaluate(
        self, text: str = "", replacement_words: Set[tuple[str, str]] = set()
    ) -> SophisticationResult:
        """
        Evaluates the sophistication of a text.

        :param text: The input text
        :param replacement_words: Set of replacement words to include in the sophistication check.
        :return: A SophisticationResult object containing the sophistication score,
                 counts of common, mid and rare words, and the total word count
        """
        if not text and not replacement_words:
            return SophisticationResult(
                score=0,
                common_count=0,
                mid_count=0,
                rare_count=0,
                unknown_count=0,
                word_count=0,
                level=SophisticationLevel.BASIC,
                breakdown=[],
            )

        doc: Doc = self.nlp(text)
        words = [
            token.text.lower() for token in doc if token.is_alpha and not token.is_stop
        ]

        word_count = len(words)

        if word_count == 0:
            return SophisticationResult(
                score=0,
                common_count=0,
                mid_count=0,
                rare_count=0,
                unknown_count=0,
                word_count=0,
                level=SophisticationLevel.BASIC,
                breakdown=[],
            )

        sophistication_words = {
            "common": [],
            "mid": [],
            "rare": [],
            "unknown": [],
        }

        # Process meaningful words only
        for word in words:
            if any(
                word == replacement_word for replacement_word, _ in replacement_words
            ):
                for replacement_word, original_word in replacement_words:
                    if word == replacement_word:
                        word = original_word
                        break
            zipf_value = zipf_frequency(word, minimum=0, lang=self.nlp.lang)
            if zipf_value >= COMMON_WORDS_THRESHOLD:
                sophistication_words["common"].append(word)
            elif MID_WORDS_THRESHOLD <= zipf_value < COMMON_WORDS_THRESHOLD:
                sophistication_words["mid"].append(word)
            elif zipf_value > 0:
                sophistication_words["rare"].append(word)
            else:
                sophistication_words["unknown"].append(word)
        # Calculate sophistication score with length adjustment
        sophistication_score, sophistication_level = self.compute_sophistication_score(
            sophistication_words, word_count
        )

        return SophisticationResult(
            score=sophistication_score,
            common_count=len(sophistication_words["common"]),
            mid_count=len(sophistication_words["mid"]),
            rare_count=len(sophistication_words["rare"]),
            unknown_count=len(sophistication_words["unknown"]),
            word_count=word_count,
            level=sophistication_level,
            breakdown=[
                SophisticationScoreBreakdown(
                    group=WordFrequencyGroup.COMMON,
                    words=sophistication_words["common"],
                ),
                SophisticationScoreBreakdown(
                    group=WordFrequencyGroup.MID,
                    words=sophistication_words["mid"],
                ),
                SophisticationScoreBreakdown(
                    group=WordFrequencyGroup.RARE,
                    words=sophistication_words["rare"],
                ),
                SophisticationScoreBreakdown(
                    group=WordFrequencyGroup.UNKNOWN,
                    words=sophistication_words["unknown"],
                ),
            ],
        )

    def compute_sophistication_score(
        self,
        words: dict,
        word_count: int,
        method: Literal["linear", "sigmoid"] = "linear",
    ) -> tuple[float, SophisticationLevel]:
        """
        Computes the sophistication score of a text, taking into account the ratio of meaningful words.

        The score is calculated as a weighted average of word sophistication levels,
        adjusted by the proportion of meaningful words to total words.

        :param words: A dictionary with the counts of common, mid and rare words
        :param word_count: Total number of words (excluding punctuation)
        :param method: The scoring method to use. Either "linear" or "sigmoid".
        :return: The sophistication score (0.0 to 1.0) and sophistication level
        """

        # Calculate weighted sum of sophistication levels
        weighted_score = (
            len(words["common"]) * COMMON_WORDS_WEIGHT
            + len(words["mid"]) * MID_WORDS_WEIGHT
            + len(words["rare"]) * RARE_WORDS_WEIGHT
            + len(words["unknown"]) * UNKNOWN_WORDS_WEIGHT
        ) / word_count

        meaningful_ratio = (len(words["rare"]) + len(words["mid"])) / word_count

        normalized_score: float

        if method == "linear":
            normalized_score = self._compute_with_linear(
                meaningful_ratio, weighted_score
            )
        elif method == "sigmoid":
            normalized_score = self._compute_with_sigmoid(
                meaningful_ratio, weighted_score
            )

        sophistication_level = SophisticationLevel.get_level(normalized_score)

        return normalized_score, sophistication_level

    def _compute_with_sigmoid(
        self, meaningful_ratio: float, weighted_score: float
    ) -> float:
        """
        Computes the sophistication score with a sigmoid adjustment based on the ratio of meaningful words.

        The score is calculated as a weighted sum of word sophistication levels,
        adjusted by a sigmoid function based on the proportion of meaningful words to total words,
        and clamped to 0.0 to 1.0.

        :param meaningful_ratio: The proportion of meaningful words to total words
        :param weighted_score: The weighted sum of word sophistication levels
        :return: The normalized sophistication score
        """
        ratio_adjustment = 1 / (1 + math.exp(-5 * (meaningful_ratio - 0.4)))
        adjusted_score = weighted_score * ratio_adjustment

        normalized_score = round(min(1.0, math.sqrt(adjusted_score)), 4)

        return normalized_score

    def _compute_with_linear(
        self, meaningful_ratio: float, weighted_score: float
    ) -> float:
        """
        Computes the sophistication score with a linear adjustment based on the ratio of meaningful words.

        The score is calculated as a weighted sum of word sophistication levels,
        adjusted by the proportion of meaningful words to total words, and clamped to 0.0 to 1.0.

        :param meaningful_ratio: The proportion of meaningful words to total words
        :param weighted_score: The weighted sum of word sophistication levels
        :return: The normalized sophistication score
        """
        ratio_adjustment = 0.5 + (meaningful_ratio * 0.5)

        adjusted_score = weighted_score * ratio_adjustment

        # normalized_score = round(min(1.0, adjusted_score / MAX_SOPHISTICATION), 4) # cap based on expected range
        normalized_score = round(min(1.0, adjusted_score), 4)

        return normalized_score
