from typing import Set
from spacy.language import Language
from vocabulary.evaluator import VocabularyEvaluator
from vocabulary.models import VocabularyResult


class VocabularyService:
    def __init__(self, nlp: Language, lang: str = "en-US"):
        self.evaluator = VocabularyEvaluator(nlp=nlp, lang=lang)

    def analyze(
        self, text: str, replacement_words: Set[tuple[str, str]] = set()
    ) -> VocabularyResult:
        """
        Analyze the text for vocabulary sophistication and precision.

        Args:
            text: The text to be analyzed.
            replacement_words: Set of replacement words

        Returns:
            VocabularyResult: Combined result of sophistication and precision.
        """
        return self.evaluator.evaluate(text, replacement_words)
