"""
Coherence analysis service for the score engine.

This module provides services for analyzing text coherence using various metrics
including text coherence and topic coherence.
"""

from functools import lru_cache
from typing import Optional
from .config import get_gemini_api_key, get_gemini_model
from .coherence_analyzer import CoherenceAnalyzer
from .models import CoherenceResult


class CoherenceService:
    """
    Service for analyzing text coherence.
    """

    def __init__(self):
        api_key = get_gemini_api_key()
        if not api_key:
            self.skip = True
            return
        self.skip = False
        self.analyzer = CoherenceAnalyzer(api_key=api_key, model=get_gemini_model())
        self._analyze = lru_cache(maxsize=128)(self._analyze_impl)

    def analyze(
        self, text: str, topic: Optional[str] = None
    ) -> Optional[CoherenceResult]:
        """
        Analyze the text for coherence.

        Args:
            text: The text to analyze
            topic: Optional topic to analyze coherence against

        Returns:
            CoherenceResult object containing the score and analysis
        """
        if self.skip == True:
            return None

        if not text.strip():
            return CoherenceResult(
                score=0,
                text_coherence=0,
                topic_coherence=0 if topic is not None else None,
                feedback="Empty text provided for analysis",
                suggestions=["Provide a valid text for coherence analysis"],
                confidence=1,
            )
        return self._analyze(text, topic)

    def _analyze_impl(self, text: str, topic: Optional[str] = None) -> CoherenceResult:
        """
        Internal implementation of analyze with caching.
        """
        return self.analyzer.analyze_text(text, topic)
