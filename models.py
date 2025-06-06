from pydantic import BaseModel, computed_field
from commons.utils import round_score
from correctness.models import CorrectnessResult
from readability.models import ReadabilityResult
from vocabulary.models import VocabularyResult
from coherence.models import CoherenceResult

CORRECTNESS_WEIGHT: float = 0.30
COHERENCE_WEIGHT: float = 0.25
VOCABULARY_WEIGHT: float = 0.25
READABILITY_WEIGHT: float = 0.20
MIN_WORD_COUNT: int = 20


class GlobalScore(BaseModel):
    """
    Represents the global score of a text.

    Attributes:
        score: Overall score of the text
        coherence: CoherenceResult object containing the coherence score
        correctness: CorrectnessResult object containing the correctness score
        readability: ReadabilityResult object containing the readability score
        vocabulary: VocabularyResult object containing the vocabulary score
    """

    coherence: CoherenceResult | None # None if the api_key is not set thus coherence is not computed
    correctness: CorrectnessResult
    readability: ReadabilityResult
    vocabulary: VocabularyResult

    @computed_field
    @property
    def score(self) -> float:
        return self._compute_score()

    def _compute_score(self) -> float:
        return (
            CORRECTNESS_WEIGHT * self.correctness.score
            + VOCABULARY_WEIGHT * self.vocabulary.score
            + READABILITY_WEIGHT * self.readability.score
            + COHERENCE_WEIGHT * self.coherence.score if self.coherence is not None else 0
        )

    @computed_field
    @property
    def score_in_percent(self) -> float:
        return round_score(self.score * 100)

    def __str__(self) -> str:
        return (
            "\n"
            + "-" * 8
            + " Global Score: "
            + str(self.score_in_percent())
            + " % "
            + "-" * 8
            + "\n"
            f"\t{self.coherence if self.coherence is not None else 'Coherence not computed'}"
            f"\t{self.correctness}"
            f"\t{self.readability}"
            f"\t{self.vocabulary}"
        )
