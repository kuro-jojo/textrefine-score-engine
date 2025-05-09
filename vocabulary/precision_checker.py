from collections import defaultdict
from language_tool.service import language_tool_service
from vocabulary.models import PrecisionResult, PrecisionScoreBreakdown
from commons.models import ErrorCategory
from spacy.language import Language
from spacy.tokens import Doc


class PrecisionChecker:
    """
    Evaluates the precision of words in a text.

    The evaluation is based on the detection of word usage and stylistic issues in
    the text, using the LanguageTool service. The precision score is a value between
    0 and 1, where 0 is a text with many issues and 1 is a text with no issues.
    """

    def __init__(self, nlp: Language, lang: str = "en-US"):
        """
        Initializes the precision checker.

        :param lang: The language to use for the evaluation
        """
        self.nlp = nlp
        self.language_tool = language_tool_service
        self.language_tool.set_language(lang)

        # Relevant categories for precision
        self.precision_categories = {
            ErrorCategory.WORD_USAGE,
            ErrorCategory.STYLISTIC_ISSUES,
        }

    def evaluate(self, text: str) -> PrecisionResult:
        """
        Evaluates the precision of a text.

        :param text: The input text
        :return: A PrecisionResult object containing the precision score, word count,
                 normalized penalty, and a list of relevant issues
        """
        issues_raw = self.language_tool.get_text_issues(text)

        relevant_issues = []
        category_counts = defaultdict(int)
        category_penalties = defaultdict(float)

        for issue in issues_raw:

            if issue.category in self.precision_categories:
                relevant_issues.append(issue)
                category_counts[issue.category] += 1
                category_penalties[issue.category] += issue.category.severity

        doc: Doc = self.nlp(text)
        word_count = len([_ for _ in doc if _.is_alpha])

        if word_count == 0:
            return PrecisionResult(
                score=0, word_count=0, normalized_penalty=0, issues=[], breakdown=[]
            )

        total_penalty = sum(category_penalties.values())
        normalized_penalty = round(total_penalty / max(word_count, 1), 4)
        score = round(1.0 - normalized_penalty, 4)

        breakdown = [
            PrecisionScoreBreakdown(
                category=cat,
                count=category_counts[cat],
                penalty=round(category_penalties[cat], 2),
            )
            for cat in category_counts
        ]

        return PrecisionResult(
            score=score,
            word_count=word_count,
            normalized_penalty=normalized_penalty,
            issues=relevant_issues,
            breakdown=breakdown,
        )
