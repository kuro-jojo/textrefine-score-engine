from enum import Enum

class ErrorCategory(Enum):
    GRAMMAR_RULES = ("Grammar Rules", 4)
    MECHANICS = ("Mechanics", 2)
    SPELLING_TYPING = ("Spelling & Typos", 3)
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