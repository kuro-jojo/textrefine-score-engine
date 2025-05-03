import unittest
from correctness.parser import from_json_to_textissue
from correctness.types import TextIssue, Replacement, ErrorCategory


class TestTextIssue(unittest.TestCase):
    def test_textissue_creation(self):
        # Create a TextIssue directly
        replacements = [Replacement(value="corrected")]
        issue = TextIssue(
            message="Test message",
            replacements=replacements,
            sentence="Test sentence",
            error_text="error",
            start_offset=0,
            issue_type="grammar",
            category=ErrorCategory.GRAMMAR_RULES,
            rule_id="test_rule",
        )

        # Verify fields
        self.assertEqual(issue.message, "Test message")
        self.assertEqual(len(issue.replacements), 1)
        self.assertEqual(issue.replacements[0].value, "corrected")
        self.assertEqual(issue.sentence, "Test sentence")
        self.assertEqual(issue.error_text, "error")
        self.assertEqual(issue.start_offset, 0)
        self.assertEqual(issue.issue_type, "grammar")
        self.assertEqual(issue.category, ErrorCategory.GRAMMAR_RULES)
        self.assertEqual(issue.rule_id, "test_rule")

    def test_textissue_from_json(self):
        json_data = {
            "message": "Test message",
            "replacements": [{"value": "corrected"}],
            "sentence": "Test sentence",
            "context": {
                "text": "Test sentence",
                "offset": 0,
                "length": 5,
            },
            "rule": {
                "id": "test_rule",
                "issueType": "grammar",
                "category": {"name": "grammar"},
            },
        }

        # Create TextIssue from JSON
        issue = from_json_to_textissue(json_data)

        # Verify fields
        self.assertEqual(issue.message, json_data["message"])
        self.assertEqual(len(issue.replacements), 1)
        self.assertEqual(issue.replacements[0].value, "corrected")
        self.assertEqual(issue.sentence, "Test sentence")
        self.assertEqual(issue.error_text, "Test sentence"[0:5])
        self.assertEqual(issue.start_offset, 0)
        self.assertEqual(issue.issue_type, "grammar")
        self.assertEqual(issue.category, ErrorCategory.GRAMMAR_RULES)
        self.assertEqual(issue.rule_id, "test_rule")

    def test_textissue_str(self):
        # Create TextIssue
        issue = TextIssue(
            message="Test message",
            replacements=[Replacement(value="replacement")],
            sentence="Test sentence",
            error_text="error",
            start_offset=0,
            issue_type="test",
            category=ErrorCategory.GRAMMAR_RULES,
            rule_id="TEST_RULE",
        )

        # Verify string representation
        expected_str = (
            "Error: Test message\n"
            "Type: test\n"
            "Category: Grammar Rules\n"
            "Rule: TEST_RULE\n"
            "Replacements: ['replacement']\n"
            "Sentence: Test sentence\n"
            "Error text: error\n"
            "Start offset: 0\n"
            "End offset: 5\n"
            "Penalty: 3\n"
        )
        self.assertEqual(str(issue), expected_str)


if __name__ == "__main__":
    unittest.main()