from enum import Enum
from typing import List
from pydantic import BaseModel


class ErrorCategory(Enum):
    GRAMMAR_RULES = ("Grammar Rules", 4)
    MECHANICS = ("Mechanics", 2)
    SPELLING_TYPING = ("Spelling & Typos", 2)
    WORD_USAGE = ("Word Usage", 3)
    MEANING_LOGIC = ("Meaning & Logic", 5)
    STYLISTIC_ISSUES = ("Stylistic Issues", 2)
    CONTEXTUAL_STYLE = ("Contextual Style", 1)

    def __init__(self, label: str, severity: int):
        self.label = label
        self.severity = severity  # 1 (low impact) to 5 (high impact)

    @classmethod
    def from_language_tool_category(cls, category: str) -> "ErrorCategory":
        category = category.upper()

        # Map actual LanguageTool categories to TextRefine's internal groups
        if category in {"GRAMMAR", "CASING"}:
            return cls.GRAMMAR_RULES

        if category in {"PUNCTUATION", "TYPOGRAPHY", "COMPOUNDING"}:
            return cls.MECHANICS

        if category in {"TYPOS"}:
            return cls.SPELLING_TYPING

        if category in {"CONFUSED_WORDS", "COLLOQUIALISMS", "REDUNDANCY"}:
            return cls.WORD_USAGE

        if category in {"FALSE_FRIENDS", "REGIONALISMS"}:
            return cls.MEANING_LOGIC

        if category in {
            "STYLE",
            "REPETITIONS_STYLE",
            "REPETITIONS",
            "PLAIN_ENGLISH",
            "MISC",
        }:
            return cls.STYLISTIC_ISSUES

        if category in {"WIKIPEDIA", "GENDER_NEUTRALITY"}:
            return cls.CONTEXTUAL_STYLE

        return cls.STYLISTIC_ISSUES


class TextIssue(BaseModel):
    """
    Represents a single issue found in a text.

    Attributes:
        message: The message of the issue
        replacements: List of possible replacements for the issue
        error_text: The text that contains the issue
        error_length: The length of the error
        start_offset: The start offset of the issue in the text
        category: The category of the issue
        rule_issue_type: The rule issue type of the issue (e.g. grammar, spelling)
    """

    message: str
    replacements: List[str]
    error_text: str
    error_length: int
    start_offset: int
    category: ErrorCategory
    rule_issue_type: str

    @property
    def end_offset(self) -> int:
        """The end offset of the issue in the text (exclusive)."""
        return self.start_offset + self.error_length

    @property
    def penalty(self) -> int:
        """The penalty of the issue."""
        return self.category.severity

    def __str__(self) -> str:
        return (
            f"Error: {self.message}\n"
            f"Category: {self.category.label}\n"
            f"Rule issue type: {self.rule_issue_type}\n"
            f"Replacements: {self.replacements}\n"
            f"Error text: {self.error_text}\n"
            f"Start offset: {self.start_offset}\n"
            f"End offset: {self.end_offset}\n"
            f"Penalty: {self.penalty}\n"
        )
