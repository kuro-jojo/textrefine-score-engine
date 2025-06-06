from logging_config import setup_logging
import asyncio
from typing import List, Optional
from language_tool_python import LanguageTool, Match
from collections import OrderedDict
from language_tool_python.utils import LanguageToolError
from commons.models import ErrorCategory, TextIssue

# Get logger for this module
logger = setup_logging()


class LanguageToolService:
    """
    Singleton service for managing the LanguageTool instance.
    """

    _instance: Optional["LanguageToolService"] = None
    tool: LanguageTool
    _language: str = "en-US"
    _cache: OrderedDict = OrderedDict()
    _cache_size: int = 1000

    @classmethod
    def set_language(cls, language: str) -> None:
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
            self.tool = LanguageTool(
                self._language,
                config={
                    "cacheSize": 5000,
                    "pipelineCaching": True,
                    "timeoutRequestLimit": 5000,
                },
            )

            # Perform a warm-up check
            try:
                # Check if the tool is ready by processing a simple text
                test_text = "This is a test sentence."
                self.tool.check(test_text)
                logger.info("LanguageTool warm-up successful")
            except Exception as warm_up_error:
                logger.warning(f"LanguageTool warm-up check failed: {warm_up_error}")
                # Still continue even if warm-up fails, as we want to start the service

            logger.info(
                f"LanguageTool initialized successfully for language : {self._language}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize LanguageTool: {e}")
            raise RuntimeError(
                f"Failed to initialize LanguageTool for language {self._language}. Is the LanguageTool server running?"
            )

    async def check(self, text: str) -> List[Match]:
        """
        Check text for language issues using LanguageTool.
        """
        try:
            if not text:
                return []

            # Run LanguageTool check in a separate thread using asyncio
            # This is important because:
            # 1. LanguageTool is a CPU-bound operation that can block the main thread
            # 2. asyncio.to_thread() runs it in a separate thread to keep the main thread responsive
            # 3. asyncio.wait_for() provides timeout handling to prevent hanging
            # 4. asyncio.shield() prevents the operation from being cancelled prematurely
            matches = await asyncio.shield(
                asyncio.wait_for(asyncio.to_thread(self.tool.check, text), timeout=10)
            )
            return matches

        except asyncio.TimeoutError:
            logger.warning("LanguageTool check timed out")
            raise LanguageToolError("LanguageTool check timed out")
        except Exception as e:
            logger.error(f"Error checking text: {e}")
            raise e

    def get_text_issues(self, text: str) -> List[TextIssue]:
        """
        Get text issues from LanguageTool.

        Args:
            text: The text to analyze

        Returns:
            List of TextIssue objects
        Raises:
            LanguageToolError: If LanguageTool check fails
            Exception: For other errors
        """
        matches = asyncio.run(self.check(text))
        return [
            TextIssue(
                message=match.message,
                replacements=[rep for rep in match.replacements[:3]],
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
