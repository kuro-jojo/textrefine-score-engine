from pydantic import BaseModel, computed_field
from correctness.models import CorrectnessResult

# from clarity import ClarityResult
# from coherence import CoherenceResult
from vocabulary.models import VocabularyResult

CORRECTNESS_WEIGHT: float = 0.5  # TODO : just for now
CLARITY_WEIGHT: float = 0.25
VOCABULARY_WEIGHT: float = 0.5  # TODO : just for now
COHERENCE_WEIGHT: float = 0.3
MIN_WORD_COUNT: int = 100


class GlobalScore(BaseModel):
    """
    Represents the global score of a text.

    Attributes:
        score: Overall score of the text
        vocabulary: VocabularyResult object containing the vocabulary score
        correctness: CorrectnessResult object containing the correctness score
        # clarity: ClarityResult object containing the clarity score
        # coherence: CoherenceResult object containing the coherence score
    """

    vocabulary: VocabularyResult
    correctness: CorrectnessResult

    @computed_field
    @property
    def score(self) -> float:
        return self._compute_score()

    def _compute_score(self) -> float:
        return (CORRECTNESS_WEIGHT * self.correctness.score) + (
            VOCABULARY_WEIGHT * self.vocabulary.score
        )  # TODO: Add clarity and coherence weights

    @computed_field
    @property
    def score_in_percent(self) -> float:
        return round(self.score * 100, 2)

    def __str__(self) -> str:
        return (
            "\n"
            + "-" * 8
            + " Global Score: "
            + str(self.score_in_percent())
            + " % "
            + "-" * 8
            + "\n"
            f"\t{self.correctness}"
            f"\t{self.vocabulary}"
        )


class TextInput(BaseModel):
    text: str
