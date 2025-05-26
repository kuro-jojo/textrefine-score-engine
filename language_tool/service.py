from typing import List, Optional
from language_tool_python import LanguageTool, Match
import logging

from commons.models import ErrorCategory, TextIssue

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LanguageToolService:
    """
    Singleton service for managing the LanguageTool instance.
    """

    _instance: Optional["LanguageToolService"] = None
    tool: LanguageTool
    _language: str = "en-US"  # Default language

    @classmethod
    def set_language(cls, language: str) -> None:
        """
        Set the language for LanguageTool.

        Args:
            language: Language code (e.g., "en-US", "fr-FR", "es-ES")
        """
        cls._language = language
        if cls._instance and cls._language != cls._instance._language:
            cls._instance._initialize_tool()

    def __new__(cls) -> "LanguageToolService":
        if cls._instance is None:
            cls._instance = super(LanguageToolService, cls).__new__(cls)
            cls._instance._initialize_tool()
        return cls._instance

    def _initialize_tool(self) -> None:
        """Initialize the LanguageTool instance."""
        try:
            self.tool = LanguageTool(self._language, config={ 'cacheSize': 1000, 'pipelineCaching': True })
            logger.info(
                f"LanguageTool initialized successfully for language: {self._language}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize LanguageTool: {e}")
            raise RuntimeError(
                f"Failed to initialize LanguageTool for language {self._language}. Is the LanguageTool server running?"
            )

    def check(self, text: str) -> List[Match]:
        """
        Check text for language issues using LanguageTool.

        Args:
            text: The text to analyze

        Returns:
            List of Match objects from LanguageTool
        """
        return self.tool.check(text)

    def get_text_issues(self, text: str) -> List[TextIssue]:
        """
        Get text issues from LanguageTool.

        Args:
            text: The text to analyze

        Returns:
            List of TextIssue objects
        """
        matches = self.check(text)
        return [
            TextIssue(
                message=match.message,
                replacements=[rep for rep in match.replacements],
                error_text=match.context,
                error_length=match.errorLength,
                start_offset=match.offset,
                original_text=text,
                category=ErrorCategory.from_language_tool_category(match.category),
                rule_issue_type=f"{match.category} - {match.ruleIssueType}",
            )
            for match in matches
        ]


# Create singleton instance
language_tool_service: LanguageToolService = LanguageToolService()
