import unittest
from correctness.parser import parse_languagetool_issues
from correctness.types import ErrorCategory

class TestParser(unittest.TestCase):
    def test_error_category_mapping(self):
        # Test mapping for each category group
        test_cases = [
            ("Grammar", ErrorCategory.GRAMMAR_RULES),
            ("Punctuation", ErrorCategory.MECHANICS),
            ("Spelling", ErrorCategory.SPELLING_TYPING),
            ("Commonly Confused Words", ErrorCategory.WORD_USAGE),
            ("Semantics", ErrorCategory.MEANING_LOGIC),
            ("Style", ErrorCategory.STYLISTIC_ISSUES),
            ("Academic Writing", ErrorCategory.CONTEXTUAL_STYLE),
            ("Unknown Category", ErrorCategory.STYLISTIC_ISSUES),  # Fallback case
        ]

        for category, expected in test_cases:
            with self.subTest(category=category):
                result = ErrorCategory.from_language_tool_category(category)
                self.assertEqual(result, expected)

    def test_parse_languagetool_issues(self):
        # Test data with multiple issues
        json_data = [
            {
                "message": 'Consider using the plural verb form for the plural noun "errors".',
                "replacements": [{"value": "Here are"}],
                "sentence": "Here is a lot of errors.",
                "context": {
                    "text": "A long text with a lot of errors. Here is a lot of errors. Ik am a bot.",
                    "offset": 34,
                    "length": 7,
                },
                "rule": {
                    "id": "THERE_IS_A_LOT_OF",
                    "issueType": "grammar",
                    "category": {"name": "Grammar"},
                },
            },
            {
                "message": 'Consider using "I" instead of "Ik".',
                "replacements": [{"value": "I"}],
                "sentence": "Ik am a bot.",
                "context": {
                    "text": "A long text with a lot of errors. Here is a lot of errors. Ik am a bot.",
                    "offset": 59,
                    "length": 2,
                },
                "rule": {
                    "id": "EN_IC",
                    "issueType": "grammar",
                    "category": {"name": "Spelling"},
                },
            },
        ]

        # Parse issues
        issues = parse_languagetool_issues(json_data)

        # Verify results
        self.assertEqual(len(issues), 2)

        # Verify first issue
        first_issue = issues[0]
        self.assertEqual(
            first_issue.message,
            'Consider using the plural verb form for the plural noun "errors".',
        )
        self.assertEqual(first_issue.replacements[0].value, "Here are")
        self.assertEqual(first_issue.sentence, "Here is a lot of errors.")
        self.assertEqual(first_issue.error_text, "Here is")
        self.assertEqual(first_issue.start_offset, 34)
        self.assertEqual(first_issue.issue_type, "grammar")
        self.assertEqual(first_issue.category, ErrorCategory.GRAMMAR_RULES)
        self.assertEqual(first_issue.rule_id, "THERE_IS_A_LOT_OF")
        self.assertEqual(first_issue.end_offset, 41)

        # Verify second issue
        second_issue = issues[1]
        self.assertEqual(second_issue.message, 'Consider using "I" instead of "Ik".')
        self.assertEqual(second_issue.replacements[0].value, "I")
        self.assertEqual(second_issue.sentence, "Ik am a bot.")
        self.assertEqual(second_issue.error_text, "Ik")
        self.assertEqual(second_issue.start_offset, 59)
        self.assertEqual(second_issue.issue_type, "grammar")
        self.assertEqual(second_issue.category, ErrorCategory.SPELLING_TYPING)
        self.assertEqual(second_issue.rule_id, "EN_IC")
        self.assertEqual(second_issue.end_offset, 61)

    def test_parse_empty_list(self):
        issues = parse_languagetool_issues([])
        self.assertEqual(len(issues), 0)

    def test_parse_invalid_data(self):
        # Test with invalid JSON structure
        invalid_data = [
            {
                "message": "Test message",
                "replacements": [],  # Missing value field
                "sentence": "Test sentence",
                "context": {"text": "Test text", "offset": 0, "length": 5},
                "rule": {
                    "id": "TEST_RULE",
                    "issueType": "test",
                    "category": {"name": "Test"},
                },
            }
        ]

        issues = parse_languagetool_issues(invalid_data)
        self.assertEqual(len(issues), 1)  # Should still create an issue
        self.assertEqual(issues[0].replacements, [])  # Empty replacements list


if __name__ == "__main__":
    unittest.main()
