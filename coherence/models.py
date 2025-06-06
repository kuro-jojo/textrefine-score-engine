"""
Models for coherence analysis results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CoherenceResult(BaseModel):
    """
    Represents the result of a coherence analysis.

    Attributes:
        score: Overall coherence score (0-1)
        text_coherence: Text coherence score (0-1)
        topic_coherence: Topic coherence score (0-1) or None if no topic provided
        feedback: Human-readable feedback about the coherence
        suggestions: List of suggestions for improvement
        confidence: Confidence in the analysis (0-1)
    """

    score: float = Field(..., ge=0, le=1)
    text_coherence: float = Field(..., ge=0, le=1)
    topic_coherence: Optional[float] = Field(default=None, ge=0, le=1)
    feedback: str
    suggestions: List[str]
    confidence: float = Field(..., ge=0, le=1)

    def __str__(self) -> str:
        return (
            f"Coherence Score: {self.score:.2f}\n"
            f"Text Coherence: {self.text_coherence:.2f}\n"
            f"Topic Coherence: {self.topic_coherence or 'N/A'}\n"
            f"Confidence: {self.confidence:.2f}\n"
            f"Feedback: {self.feedback}\n"
            f"Suggestions: {', '.join(self.suggestions)}"
        )
