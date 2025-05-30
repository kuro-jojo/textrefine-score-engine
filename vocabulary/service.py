from typing import List
from spacy.language import Language
from commons.models import TextIssue
from vocabulary.evaluator import VocabularyEvaluator
from vocabulary.models import VocabularyResult


class VocabularyService:
    def __init__(self, nlp: Language, lang: str = "en-US"):
        self.evaluator = VocabularyEvaluator(nlp=nlp, lang=lang)

    def analyze(
        self, text: str, issues: List[TextIssue] = []
    ) -> VocabularyResult:
        """
        Analyze the text for vocabulary sophistication and precision.

        Args:
            text: The text to be analyzed.
            issues: List of TextIssue objects

        Returns:
            VocabularyResult: Combined result of sophistication and precision.
        """
        return self.evaluator.evaluate(text, issues)
