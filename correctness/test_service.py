import pytest
from unittest.mock import patch, MagicMock

from correctness import CorrectnessService
from correctness.models import TextIssue, ErrorCategory
from language_tool_python import Match

@pytest.fixture
def service():
    return CorrectnessService()

@pytest.fixture
def test_text():
    return "This are a test text with some errrors."

@pytest.fixture
def test_match():
    return Match(
        attrib={
            "offset": 8,
            "length": 4,
            "context": {"text": "This are noot okay. ", "offset": 8, "length": 4},
            "message": "Possible spelling mistake found.",
            "sentence": "This are a test text with some errors.",
            "replacements": [
                {"value": "newt"},
                {"value": "not"},
            ],
            "rule": {
                "id": "MORFOLOGIK_RULE_EN_US",
                "issueType": "misspelling",
                "category": {"id": "TYPOS", "name": "Possible Typo"},
            },
        },
        text="This are a test text with some errors.",
    )

def test_compute_score_cache(service, test_text, test_match):
    """Test that the score computation is cached"""
    with patch("language_tool.service.language_tool_service.check") as mock_check:
        mock_check.return_value = [test_match]

        # First call should compute
        result1 = service.analyze(test_text)
        assert result1 is not None
        assert mock_check.call_count == 1
        assert mock_check.call_args[0][0] == test_text

        # Second call should use cache
        result2 = service.analyze(test_text)
        assert result1 == result2
        assert mock_check.call_count == 1  # Still only called once

        # Verify cache content
        assert result1.score == result2.score
        assert result1.issues == result2.issues
        assert result1.breakdown == result2.breakdown

        # Verify cache eviction
        # Create a text that will exceed the cache size
        cache_size = 128
        texts = [f"Text {i}" for i in range(cache_size + 1)]
        for text in texts:
            service.analyze(text)

        # The first text should no longer be in cache
        mock_check.reset_mock()
        mock_check.return_value = []  # Return empty for no issues
        result3 = service.analyze(test_text)
        assert mock_check.call_count == 1  # Cache was evicted
        assert result3.score == 1.0  # No issues means perfect score

def test_compute_score_no_issues(service, test_text):
    """Test score computation with no issues"""
    with patch("language_tool.service.language_tool_service.check") as mock_check:
        mock_check.return_value = []

        result = service.analyze(test_text)
        assert result is not None
        assert result.score == 1.0
        assert result.normalized_penalty == 0
        assert len(result.issues) == 0
        assert len(result.breakdown) == 0

@pytest.fixture
def mock_matches():
    return [
        Match(
            attrib={
                "offset": 0,
                "length": 1,
                "rule": {
                    "id": "GRAMMAR_RULE",
                    "issueType": "grammar",
                    "category": {"id": "GRAMMAR"},
                },
                "context": {"text": "test", "offset": 0, "length": 1},
                "message": "Possible grammar error.",
                "replacements": [
                    {"value": "correct"},
                ],
            },
            text="test",
        ),
        Match(
            attrib={
                "offset": 16,
                "length": 1,
                "rule": {
                    "id": "SPELLING_RULE",
                    "issueType": "misspelling",
                    "category": {"id": "TYPOS"},
                },
                "context": {"text": "test", "offset": 16, "length": 1},
                "message": "Possible spelling error.",
                "replacements": [
                    {"value": "correct"},
                ],
            },
            text="test",
        ),
    ]

def test_compute_score_with_issues(service, test_text, mock_matches):
    """Test score computation with multiple issues"""
    with patch("language_tool.service.language_tool_service.check") as mock_check:
        mock_check.return_value = mock_matches

        result = service.analyze(test_text)
        assert result is not None

        # Verify issues are converted correctly
        assert len(result.issues) == 2
        assert result.issues[0].category == ErrorCategory.GRAMMAR_RULES
        assert result.issues[1].category == ErrorCategory.SPELLING_TYPING

        # Verify breakdown
        assert len(result.breakdown) == 2
        grammar_breakdown = next(
            bd
            for bd in result.breakdown
            if bd.category == ErrorCategory.GRAMMAR_RULES
        )
        assert grammar_breakdown.count == 1
        assert grammar_breakdown.penalty == 5  # Grammar rules have severity 5

        spelling_breakdown = next(
            bd
            for bd in result.breakdown
            if bd.category == ErrorCategory.SPELLING_TYPING
        )
        assert spelling_breakdown.count == 1
        assert spelling_breakdown.penalty == 4  # Spelling errors have severity 4

def test_compute_score_error_handling(service, test_text):
    """Test error handling in compute_score"""
    with patch("language_tool.service.language_tool_service.check") as mock_check:
        mock_check.side_effect = Exception("Mocked LanguageTool error")

        with pytest.raises(Exception):
            service.analyze(test_text)

@pytest.fixture
def test_issue():
    return TextIssue(
        message="Possible spelling error.",
        replacements=["issue"],
        original_text="Ththere is an error",
        error_text="Ththere is an error",
        start_offset=0,
        error_length=4,
        category=ErrorCategory.SPELLING_TYPING,
        rule_issue_type="TYPOS",
    )

def test_score_normalization(service, test_issue):
    """Test that scores are normalized based on word count"""
    short_text = "This is a short text"
    long_text = "This is a long text with many words"
    
    # Short text (5 words)
    short_result = service._score_text_issues(short_text, [test_issue])
    # Long text (100 words)
    long_result = service._score_text_issues(long_text, [test_issue])

    # Short text should have higher penalty and lower score
    assert short_result.normalized_penalty > long_result.normalized_penalty
    assert short_result.score < long_result.score

@pytest.fixture
def test_issues():
    return [
        TextIssue(
            message="Possible spelling error.",
            replacements=["issue"],
            original_text="Ththere is an error",
            error_text="Ththere is an error",
            start_offset=0,
            error_length=4,
            category=ErrorCategory.SPELLING_TYPING,
            rule_issue_type="TYPOS",
        ),
        TextIssue(
            message="Possible grammar error.",
            replacements=["issue"],
            original_text="Ththere is an error",
            error_text="Ththere is an error",
            start_offset=0,
            error_length=4,
            category=ErrorCategory.GRAMMAR_RULES,
            rule_issue_type="GRAMMAR",
        ),
    ]

def test_score_breakdown(service, test_text, test_issues):
    """Test that score breakdown is calculated correctly"""
    result = service._score_text_issues(test_text, test_issues)

    # Verify breakdown
    assert len(result.breakdown) == 2
    grammar_breakdown = next(
        bd for bd in result.breakdown if bd.category == ErrorCategory.GRAMMAR_RULES
    )
    assert grammar_breakdown.count == 1
    assert grammar_breakdown.penalty == 5

    spelling_breakdown = next(
        bd
        for bd in result.breakdown
        if bd.category == ErrorCategory.SPELLING_TYPING
    )
    assert spelling_breakdown.count == 1
    assert spelling_breakdown.penalty == 4