import pytest
from spacy.lang.en import English
from vocabulary.constants import (
    LEXICAL_DIVERSITY_WEIGHT,
    PRECISION_WEIGHT,
    SOPHISTICATION_WEIGHT,
)
from vocabulary.sophistication_checker import (
    SophisticationChecker,
    SophisticationResult,
)
from vocabulary.evaluator import VocabularyEvaluator
from vocabulary.models import SophisticationLevel


@pytest.fixture
def nlp():
    return English()


@pytest.fixture
def sophistication_checker(nlp):
    return SophisticationChecker(nlp)


@pytest.fixture
def vocabulary_evaluator(nlp):
    return VocabularyEvaluator(nlp)


def test_sophistication_checker_evaluate(sophistication_checker):
    # Test with a mix of common and sophisticated words
    text = "The quick brown fox jumps over the lazy dog"
    result = sophistication_checker.evaluate(text)

    assert isinstance(result, SophisticationResult)
    assert 0 <= result.score <= 1
    assert result.word_count > 0
    assert result.common_count >= 0
    assert result.mid_count >= 0
    assert result.rare_count >= 0
    assert result.level in SophisticationLevel


def test_sophistication_checker_compute_score(sophistication_checker):
    # Test with different word count distributions
    words = {
        "common": ["the", "and", "is", "in", "of", "to", "a", "that", "it", "with"],
        "mid": ["quick", "brown", "fox", "jumps", "over", "lazy", "dog"],
        "rare": ["jumps", "over", "lazy", "dog"],
        "unknown": ["ffa"],
    }
    score, level = sophistication_checker.compute_sophistication_score(
        words, len(words)
    )

    assert 0 <= score <= 1
    assert level in SophisticationLevel


def test_vocabulary_evaluator_evaluate(vocabulary_evaluator):
    # Test with a sample text
    text = "The quick brown fox jumps over the lazy dog"
    result = vocabulary_evaluator.evaluate(text)

    assert 0 <= result.score <= 1
    assert 0 <= result.lexical_diversity.ttr <= 1
    assert 0 <= result.sophistication.score <= 1
    assert 0 <= result.precision.score <= 1


def test_vocabulary_evaluator_with_empty_text(vocabulary_evaluator):
    # Test with empty text
    text = ""
    result = vocabulary_evaluator.evaluate(text)

    assert result.score == 0
    assert result.lexical_diversity.ttr == 0
    assert result.sophistication.score == 0
    assert result.precision.score == 0


def test_vocabulary_evaluator_with_single_word(vocabulary_evaluator):
    # Test with a single word
    text = "The"
    result = vocabulary_evaluator.evaluate(text)

    assert (
        result.score
        == LEXICAL_DIVERSITY_WEIGHT * 0
        + SOPHISTICATION_WEIGHT * 0
        + PRECISION_WEIGHT * 1
    )
    assert result.lexical_diversity.ttr == 0
    assert result.sophistication.score == 0
    assert result.precision.score == 1
