"""
This module provides a class for evaluating the sophistication of words in a text.

The evaluation is based on the frequency of words in the language, with words that are
more rare being considered more sophisticated. The sophistication score is a value
between 0 and 1, where 0 is a text with only very common words and 1 is a text with
only very rare words.

The class also provides a method for computing the sophistication score of a text.
"""

import math
from typing import Literal
from spacy.language import Language
from spacy.tokens import Doc
from wordfreq import zipf_frequency
from vocabulary.models import SophisticationLevel, SophisticationResult

COMMON_THRESHOLD = 5.0
MID_THRESHOLD = 3.5

RARE_WEIGHT = 3.0
MID_WEIGHT = 1.5
COMMON_WEIGHT = 1.0


class SophisticationChecker:
    """
    Evaluates the sophistication of words in a text.

    The sophistication score is a value between 0 and 1, where 0 is a text with only
    very common words and 1 is a text with only very rare words.
    """

    def __init__(self, nlp: Language, exclude_stopwords: bool = True):
        """
        Initializes the evaluator.

        :param nlp: The spaCy language model
        :param exclude_stopwords: If True, exclude stopwords from the calculation
        """
        self.nlp = nlp
        self.exclude_stopwords = exclude_stopwords

    def evaluate(self, text: str) -> SophisticationResult:
        """
        Evaluates the sophistication of a text.

        :param text: The input text
        :return: A SophisticationResult object containing the sophistication score,
                 counts of common, mid and rare words, and the total word count
        """
        doc: Doc = self.nlp(text)

        # Get total word count (including stopwords)
        total_words = len([token for token in doc if not token.is_punct])

        sophistication_counts = {"common": 0, "mid": 0, "rare": 0}

        # Process meaningful words only
        for token in doc:
            if not (token.is_stop or token.is_punct or token.is_space):
                zipf_value = zipf_frequency(
                    token.text.lower(), minimum=0, lang=self.nlp.lang
                )
                if zipf_value >= COMMON_THRESHOLD:
                    sophistication_counts["common"] += 1
                elif MID_THRESHOLD <= zipf_value < COMMON_THRESHOLD:
                    sophistication_counts["mid"] += 1
                else:
                    sophistication_counts["rare"] += 1

        # Calculate sophistication score with length adjustment
        sophistication_score, sophistication_level = self.compute_sophistication_score(
            sophistication_counts, total_words
        )

        return SophisticationResult(
            score=sophistication_score,
            common_count=sophistication_counts["common"],
            mid_count=sophistication_counts["mid"],
            rare_count=sophistication_counts["rare"],
            word_count=total_words,
            level=sophistication_level,
        )

    def compute_sophistication_score(
        self,
        counts: dict,
        total_words: int,
        method: Literal["linear", "sigmoid"] = "linear",
    ) -> tuple[float, SophisticationLevel]:
        """
        Computes the sophistication score of a text, taking into account the ratio of meaningful words.

        The score is calculated as a weighted average of word sophistication levels,
        adjusted by the proportion of meaningful words to total words.

        :param counts: A dictionary with the counts of common, mid and rare words
        :param total_words: Total number of words (excluding punctuation)
        :param method: The scoring method to use. Either "linear" or "sigmoid".
        :return: The sophistication score (0.0 to 1.0) and sophistication level
        """

        # Calculate weighted sum of sophistication levels
        weighted_score = (
            counts["common"] * COMMON_WEIGHT
            + counts["mid"] * MID_WEIGHT
            + counts["rare"] * RARE_WEIGHT
        ) / total_words

        meaningful_ratio = (counts["rare"] + counts["mid"]) / total_words

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

        normalized_score = round(min(1.0, adjusted_score), 4)

        return normalized_score
