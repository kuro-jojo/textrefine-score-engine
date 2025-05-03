import unittest
from unittest.mock import patch
from correctness.scorer import compute_score, score_text_issues
from correctness.types import CorrectnessResult, TextIssue, ErrorCategory


class TestScorer(unittest.TestCase):
    def setUp(self):
        self.test_text = (
            "Here is a lot of errors. Ik am a bot. I am using informal words."
        )
        self.test_issues = [
            TextIssue(
                message='Consider using the plural verb form for the plural noun "errors".',
                replacements=[{"value": "Here are"}],
                sentence="Here is a lot of errors.",
                error_text="Here is",
                start_offset=0,
                issue_type="grammar",
                category=ErrorCategory.GRAMMAR_RULES,
                rule_id="THERE_IS_A_LOT_OF",
            ),
            TextIssue(
                message='Consider using "I" instead of "Ik".',
                replacements=[{"value": "I"}],
                sentence="Ik am a bot.",
                error_text="Ik",
                start_offset=27,
                issue_type="grammar",
                category=ErrorCategory.SPELLING_TYPING,
                rule_id="EN_IC",
            ),
            TextIssue(
                message="Consider using a more formal word.",
                replacements=[{"value": "formal"}],
                sentence="I am using informal words.",
                error_text="informal",
                start_offset=42,
                issue_type="style",
                category=ErrorCategory.STYLISTIC_ISSUES,
                rule_id="FORMAL_STYLE",
            ),
        ]

    def test_score_text_issues(self):
        result = score_text_issues(len(self.test_text.split()), self.test_issues)

        # Verify basic properties
        self.assertIsInstance(result, CorrectnessResult)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)
        self.assertEqual(result.word_count, len(self.test_text.split()))

        # Verify breakdown
        breakdown = {bd.category: bd for bd in result.breakdown}
        self.assertEqual(len(breakdown), 3)

        # Verify penalties
        self.assertGreater(result.normalized_penalty, 0)

        # Verify categories
        self.assertIn(ErrorCategory.GRAMMAR_RULES, breakdown)
        self.assertIn(ErrorCategory.SPELLING_TYPING, breakdown)
        self.assertIn(ErrorCategory.STYLISTIC_ISSUES, breakdown)

    def test_compute_score(self):
        with patch(
            "correctness.scorer.parse_languagetool_issues",
            return_value=self.test_issues,
        ):
            result = compute_score(self.test_text)

            self.assertIsInstance(result, CorrectnessResult)
            self.assertGreaterEqual(result.score, 0)
            self.assertLessEqual(result.score, 100)
            self.assertEqual(result.word_count, len(self.test_text.split()))

            # Verify issues are preserved
            self.assertEqual(len(result.issues), len(self.test_issues))

            # Verify breakdown consistency
            breakdown = {bd.category: bd for bd in result.breakdown}
            self.assertEqual(len(breakdown), 3)

    def test_score_no_issues(self):
        result = score_text_issues(10, [])
        self.assertEqual(result.score, 100)
        self.assertEqual(result.normalized_penalty, 0)
        self.assertEqual(len(result.breakdown), 0)

    def test_score_same_category(self):
        issues = [
            TextIssue(
                message="Test issue 1",
                replacements=[{"value": "replacement"}],
                sentence="Test sentence",
                error_text="error",
                start_offset=0,
                issue_type="grammar",
                category=ErrorCategory.GRAMMAR_RULES,
                rule_id="TEST_RULE_1",
            ),
            TextIssue(
                message="Test issue 2",
                replacements=[{"value": "replacement"}],
                sentence="Test sentence",
                error_text="error",
                start_offset=5,
                issue_type="grammar",
                category=ErrorCategory.GRAMMAR_RULES,
                rule_id="TEST_RULE_2",
            ),
        ]
        result = score_text_issues(10, issues)

        self.assertEqual(len(result.breakdown), 1)
        self.assertEqual(result.breakdown[0].category, ErrorCategory.GRAMMAR_RULES)
        self.assertEqual(result.breakdown[0].count, 2)

    def test_score_normalization(self):
        # Test with different word counts
        issues = [
            TextIssue(
                message="Test issue",
                replacements=[{"value": "replacement"}],
                sentence="Test sentence",
                error_text="error",
                start_offset=0,
                issue_type="grammar",
                category=ErrorCategory.GRAMMAR_RULES,
                rule_id="TEST_RULE",
            )
        ]

        # Short text (should have higher penalty)
        short_result = score_text_issues(5, issues)
        # Long text (should have lower penalty)
        long_result = score_text_issues(100, issues)

        self.assertGreater(
            short_result.normalized_penalty, long_result.normalized_penalty
        )
        self.assertGreater(long_result.score, short_result.score)


if __name__ == "__main__":
    unittest.main()
