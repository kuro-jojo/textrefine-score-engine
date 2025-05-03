from typing import List
from correctness.types import CorrectnessResult, TextIssue, CorrectnessScoreBreakdown
from correctness.parser import parse_languagetool_issues
import requests

LANGUAGE_TOOL = "http://localhost:8081/v2/check?language=en-US"

MAX_SCORE = 100

WORD_COUNT_NORMALIZATION = 100


def compute_score(text: str) -> CorrectnessResult:
    # 1. Make a request to LanguageTool
    response = requests.post(LANGUAGE_TOOL, data={"text": text})
    json_response = response.json()

    # 2. Parse the response
    issues = parse_languagetool_issues(json_response["matches"])

    # 3. Compute the score of the issues
    return score_text_issues(len(text.split()), issues)


def score_text_issues(word_count: int, issues: List[TextIssue]) -> CorrectnessResult:
    """
    Score text issues by category and type.

    Args:
        word_count: Number of words in the text
        issues: List of TextIssue objects

    Returns:
        Dictionary containing:
        - total_issues: Total number of issues
        - by_category: Dictionary of issues by category
        - by_type: Dictionary of issues by type
    """
    categories = {}
    # Count issues by category and type
    total_penalty = 0
    for issue in issues:
        # Update category count
        if issue.category in categories:
            categories[issue.category].count += 1
            categories[issue.category].penalty += issue.penalty
        else:
            categories[issue.category] = CorrectnessScoreBreakdown(
                category=issue.category,
                count=1,
                penalty=issue.penalty,
            )
        total_penalty += issue.penalty

    normalized_penalty = total_penalty / (word_count / WORD_COUNT_NORMALIZATION)
    score = max(0, MAX_SCORE - normalized_penalty)
    
    return CorrectnessResult(
        score=score,
        word_count=word_count,
        normalized_penalty=normalized_penalty,
        issues=issues,
        breakdown=list(categories.values()),
    )
