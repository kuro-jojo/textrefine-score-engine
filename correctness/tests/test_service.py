import unittest
from unittest.mock import patch

from correctness.service import CorrectnessService
from correctness.models import TextIssue, ErrorCategory
from language_tool_python import Match


class TestCorrectnessService(unittest.TestCase):
    def setUp(self):
        """Setup test environment"""
        self.service = CorrectnessService()
        self.test_text = "This are a test text with some errrors."
        self.test_match = Match(
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

    def test_compute_score_cache(self):
        """Test that the score computation is cached"""
        with patch("language_tool.service.language_tool_service.check") as mock_check:
            mock_check.return_value = [self.test_match]

            # First call should compute
            result1 = self.service.compute_score(self.test_text)
            self.assertIsNotNone(result1)
            self.assertEqual(mock_check.call_count, 1)
            self.assertEqual(mock_check.call_args[0][0], self.test_text)

            # Second call should use cache
            result2 = self.service.compute_score(self.test_text)
            self.assertEqual(result1, result2)
            self.assertEqual(mock_check.call_count, 1)  # Still only called once

            # Verify cache content
            self.assertEqual(result1.score, result2.score)
            self.assertEqual(result1.issues, result2.issues)
            self.assertEqual(result1.breakdown, result2.breakdown)

            # Verify cache eviction
            # Create a text that will exceed the cache size
            cache_size = 128
            texts = [f"Text {i}" for i in range(cache_size + 1)]
            for text in texts:
                self.service.compute_score(text)

            # The first text should no longer be in cache
            mock_check.reset_mock()
            mock_check.return_value = []  # Return empty for no issues
            result3 = self.service.compute_score(self.test_text)
            self.assertEqual(mock_check.call_count, 1)  # Cache was evicted
            self.assertEqual(result3.score, 1.0)  # No issues means perfect score

    def test_compute_score_no_issues(self):
        """Test score computation with no issues"""
        with patch("language_tool.service.language_tool_service.check") as mock_check:
            mock_check.return_value = []

            result = self.service.compute_score(self.test_text)
            self.assertIsNotNone(result)
            self.assertEqual(result.score, 1.0)
            self.assertEqual(result.normalized_penalty, 0)
            self.assertEqual(len(result.issues), 0)
            self.assertEqual(len(result.breakdown), 0)

    def test_compute_score_with_issues(self):
        """Test score computation with multiple issues"""
        mock_matches = [
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

        with patch("language_tool.service.language_tool_service.check") as mock_check:
            mock_check.return_value = mock_matches

            result = self.service.compute_score(self.test_text)
            self.assertIsNotNone(result)

            # Verify issues are converted correctly
            self.assertEqual(len(result.issues), 2)
            self.assertEqual(result.issues[0].category, ErrorCategory.GRAMMAR_RULES)
            self.assertEqual(result.issues[1].category, ErrorCategory.SPELLING_TYPING)

            # Verify breakdown
            self.assertEqual(len(result.breakdown), 2)
            grammar_breakdown = next(
                bd
                for bd in result.breakdown
                if bd.category == ErrorCategory.GRAMMAR_RULES
            )
            self.assertEqual(grammar_breakdown.count, 1)
            self.assertEqual(
                grammar_breakdown.penalty, 4
            )  # Grammar rules have severity 4

            spelling_breakdown = next(
                bd
                for bd in result.breakdown
                if bd.category == ErrorCategory.SPELLING_TYPING
            )
            self.assertEqual(spelling_breakdown.count, 1)
            self.assertEqual(
                spelling_breakdown.penalty, 2
            )  # Spelling errors have severity 3

    def test_compute_score_error_handling(self):
        """Test error handling in compute_score"""
        with patch("language_tool.service.language_tool_service.check") as mock_check:
            mock_check.side_effect = Exception("Mocked LanguageTool error")

            result = self.service.compute_score(self.test_text)
            self.assertIsNone(result)

    def test_score_normalization(self):
        """Test that scores are normalized based on word count"""
        # Create test issues
        issue = TextIssue(
            message="Possible spelling error.",
            replacements=["issue"],
            original_text="Ththere is an error",
            error_text="Ththere is an error",
            start_offset=0,
            error_length=4,
            category=ErrorCategory.SPELLING_TYPING,
            rule_issue_type="TYPOS",
        )

        # Short text (5 words)
        short_result = self.service._score_text_issues(5, [issue])
        # Long text (100 words)
        long_result = self.service._score_text_issues(100, [issue])

        # Short text should have higher penalty and lower score
        self.assertGreater(
            short_result.normalized_penalty, long_result.normalized_penalty
        )
        self.assertLess(short_result.score, long_result.score)

    def test_score_breakdown(self):
        """Test that score breakdown is calculated correctly"""
        issues = [
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

        result = self.service._score_text_issues(10, issues)

        # Verify breakdown
        self.assertEqual(len(result.breakdown), 2)
        grammar_breakdown = next(
            bd for bd in result.breakdown if bd.category == ErrorCategory.GRAMMAR_RULES
        )
        self.assertEqual(grammar_breakdown.count, 1)
        self.assertEqual(grammar_breakdown.penalty, 4)

        spelling_breakdown = next(
            bd
            for bd in result.breakdown
            if bd.category == ErrorCategory.SPELLING_TYPING
        )
        self.assertEqual(spelling_breakdown.count, 1)
        self.assertEqual(spelling_breakdown.penalty, 2)


if __name__ == "__main__":
    unittest.main()
