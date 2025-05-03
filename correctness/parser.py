from typing import List, Dict, Any
from correctness.types import TextIssue, Replacement, ErrorCategory


def from_json_to_textissue(data: Dict[str, Any]) -> TextIssue:
    replacements = [Replacement(value=r["value"]) for r in data.get("replacements", [])]
    context_data = data.get("context", {})
    text = context_data.get("text", "")
    offset = context_data.get("offset", 0)
    length = context_data.get("length", 0)
    error_text = text[offset : offset + length] if text else ""

    category_name = data.get("rule", {}).get("category", {}).get("name", "")
    category = ErrorCategory.from_language_tool_category(category_name)

    return TextIssue(
        message=data.get("message", ""),
        replacements=replacements,
        sentence=data.get("sentence", ""),
        error_text=error_text,
        start_offset=offset,
        issue_type=data.get("rule", {}).get("issueType", ""),
        category=category,
        rule_id=data.get("rule", {}).get("id", ""),
    )


def parse_languagetool_issues(json_data: List[Dict[str, Any]]) -> List[TextIssue]:
    """
    Parse a list of JSON error objects into TextIssue objects.

    Args:
        json_data: List of JSON error objects from LanguageTool

    Returns:
        List of TextIssue objects
    """
    issues = []
    for issue in json_data:
        text_issue = from_json_to_textissue(issue)
        issues.append(text_issue)

    return issues
