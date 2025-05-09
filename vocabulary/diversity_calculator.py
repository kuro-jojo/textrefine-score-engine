# TTR, MTLD or HD-D calculation logic

from spacy.language import Language
from spacy.tokens import Doc
from vocabulary.models import LexicalDiversityResult


class LexicalDiversityCalculator:
    """
    Computes lexical diversity score for the given text.

    :param nlp: The spaCy language model
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp

    def compute(self, text: str) -> LexicalDiversityResult:
        """
        Compute lexical diversity score for the given text.

        :param text: The input text
        :return: LexicalDiversityScore object containing TTR, word count and unique count
        """
        doc: Doc = self.nlp(text)

        tokens = [
            token.text.lower() for token in doc if token.is_alpha and not token.is_stop
        ]

        total = len(tokens)
        unique = len(set(tokens))

        if total == 0:
            return LexicalDiversityResult(ttr=0.0, word_count=0, unique_count=0)

        ttr = unique / total

        return LexicalDiversityResult(
            ttr=round(ttr, 4), word_count=total, unique_count=unique
        )
