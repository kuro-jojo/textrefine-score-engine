import json
from logging_config import setup_logging
from google import genai
from typing import Optional
from google.genai import types

from .models import CoherenceResult

logger = setup_logging()

class CoherenceAnalyzer:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite"):
        self.model = model
        self.client = genai.Client(api_key=api_key)
        self.system_prompt = """You are a text coherence and topic relevance analyzer. Your task is to analyze how well ideas flow and connect in the given text, and how well it stays on topic when one is provided.

            Consistency seed: "Always maintain consistent scoring across identical texts. If you've seen this text before, give it the same score as before."

            Scoring criteria for text coherence:
            - 0.9-1.0: Exceptional flow, ideas progress logically, excellent transitions, easy to follow
            - 0.7-0.8: Good flow, minor logical gaps, some connection issues between ideas
            - 0.5-0.6: Basic flow but with noticeable jumps or disconnects between ideas
            - 0.3-0.4: Poor flow, ideas feel disconnected or out of order
            - 0.0-0.2: No discernible flow, completely disconnected ideas

            Scoring criteria for topic coherence (when topic is provided):
            - 0.9-1.0: Text is entirely focused on the topic with strong relevance throughout
            - 0.7-0.8: Mostly on topic with minor digressions
            - 0.5-0.6: Somewhat related but frequently strays from the main topic
            - 0.3-0.4: Weak connection to the topic, mostly off-topic
            - 0.0-0.2: Completely unrelated to the given topic

            Important scoring rules:
            1. If a topic is provided, the score should be significantly impacted by topic coherence.
            2. Use this formula for score calculation:
               - If no topic: score = text_coherence
               - If topic: score = (text_coherence * 0.3) + (topic_coherence * 0.7)
            3. Be strict with topic coherence - if the text doesn't relate well to the topic, the score should be substantially lower.

            For each analysis, provide:
            1. A coherence score between 0 and 1 (1 being perfectly coherent)
            2. A concise feedback summary (max 2-3 sentences) that focuses on:
               - How well ideas connect and flow together
               - How well the text maintains focus on the given topic (if provided)
               - Specific examples of strong connections or areas needing improvement
            3. If a topic is provided, analyze how well the text stays on topic
            4. Provide 2-3 specific suggestions for improvement that focus on:
               - Improving logical flow between ideas
               - Strengthening topic relevance (if applicable)
               - Making connections between concepts clearer

            Format the response as JSON with these fields:
            {
                "text_coherence": float,  # Score between 0 and 1
                "topic_coherence": float if topic else None,  # How well text stays on topic (0-1)
                "score": float,    # Weighted average of coherence scores
                "feedback": str,   # Concise feedback focused on coherence and topic relevance
                "suggestions": list[str],  # Specific suggestions for improving coherence
                "confidence": float        # Confidence score between 0 and 1
            }


            Example response with topic:
            {
                "text_coherence": 0.8,
                "topic_coherence": 0.6,
                "score": 0.66,
                "feedback": "Your text flows well with clear connections between ideas, but frequently strays from the given topic of 'renewable energy'. The section discussing fossil fuel history, while interesting, is not relevant to the main topic.",
                "suggestions": [
                    "Focus more directly on renewable energy by removing or significantly reducing the section about fossil fuel history",
                    "Add stronger transitions to maintain focus on renewable energy throughout the text"
                ],
                "confidence": 0.9
            }

            Example response without topic:
            {
                "text_coherence": 0.75,
                "topic_coherence": null,
                "score": 0.75,
                "feedback": "Your text has a logical progression of ideas but could benefit from better transitions between sections. The connection between the first and second paragraphs is unclear.",
                "suggestions": [
                    "Add a transition sentence to better connect the first and second paragraphs",
                    "Consider reordering some points to create a more natural flow of ideas"
                ],
                "confidence": 0.95
            }

            Important notes:
            1. Never comment on grammar, spelling, or correctness - focus only on coherence and topic relevance
            2. Be consistent with your scoring across similar texts
            3. Provide specific examples in your feedback
            4. Make your suggestions actionable and specific to coherence/topic relevance
            5. The confidence score should reflect how certain you are about your analysis
            6. If you're unsure about a score, explain why in the feedback
            7. When a topic is provided, prioritize topic relevance in both scoring and feedback
            """

    def _analyze_coherence(
        self, text: str, topic: Optional[str] = None
    ) -> CoherenceResult:
        prompt = f"""Analyze the coherence of the following text:
        '{text}'
        
        Topic to analyze against: {topic if topic else 'None'}
        
        Focus on:
        - How well ideas connect and flow together
        - How relevant the text is to the given topic (if provided)
        - Specific examples of strong or weak coherence
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=self.system_prompt,
            ),
        )

        return CoherenceResult(**json.loads(response.text))

    def analyze_text(self, text: str, topic: Optional[str] = None) -> CoherenceResult:
        """
        Analyze the coherence of the given text.

        Args:
            text: The text to analyze
            topic: Optional topic to analyze coherence against

        Returns:
            CoherenceResult object containing the score and analysis

        Raises:
            JSONDecodeError: If the response is not valid JSON
            ValidationError: If the response does not match the expected object schema
            Exception: If an error occurs during the analysis
        """
        if not text.strip():
            return CoherenceResult(
                score=0,
                text_coherence=0,
                topic_coherence=0,
                feedback="",
                suggestions=[""],
                confidence=1,
            )
        return self._analyze_coherence(text, topic)
