from typing import List, Optional
from language_tool_python import LanguageTool, Match
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LanguageToolService:
    """
    Singleton service for managing the LanguageTool instance.
    """

    _instance: Optional["LanguageToolService"] = None
    tool: LanguageTool

    def __new__(cls) -> "LanguageToolService":
        if cls._instance is None:
            cls._instance = super(LanguageToolService, cls).__new__(cls)
            try:
                cls._instance.tool = LanguageTool("en-US")
                logger.info("LanguageTool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize LanguageTool: {e}")
                raise RuntimeError(
                    "Failed to initialize LanguageTool. Is the LanguageTool server running?"
                )
        return cls._instance

    def check(self, text: str) -> List[Match]:
        """
        Check text for language issues using LanguageTool.

        Args:
            text: The text to analyze

        Returns:
            List of Match objects from LanguageTool
        """
        return self.tool.check(text)


# Create singleton instance
language_tool_service: LanguageToolService = LanguageToolService()
