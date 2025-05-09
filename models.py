from correctness.models import CorrectnessResult

# from clarity import ClarityResult
# from coherence import CoherenceResult
from vocabulary.models import VocabularyResult

CORRECTNESS_WEIGHT: float = 0.25
CLARITY_WEIGHT: float = 0.25
VOCABULARY_WEIGHT: float = 0.20
COHERENCE_WEIGHT: float = 0.3


class GlobalScore:
    score: float
    vocabulary: VocabularyResult
    correctness: CorrectnessResult
    # clarity: ClarityResult
    # coherence: CoherenceResult

    def __init__(self, vocabulary: VocabularyResult, correctness: CorrectnessResult):
        self.vocabulary = vocabulary
        self.correctness = correctness
        self.score = self._compute_score()

    def _compute_score(self):
        return round(
            (CORRECTNESS_WEIGHT * self.correctness.score)
            + (VOCABULARY_WEIGHT * self.vocabulary.score),
            4,
        )  # TODO: Add clarity and coherence weights

    def score_in_percent(self):
        return self.score * 100

    def __str__(self) -> str:
        return (
            "\n"
            + "-" * 8
            + " Global Score: "
            + str(self.score_in_percent())
            + " % "
            + "-" * 8
            + "\n"
            f"\t{self.vocabulary}"
            f"\t{self.correctness}"
        )
