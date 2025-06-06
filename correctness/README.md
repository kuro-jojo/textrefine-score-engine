# TextRefine Correctness Module

The Correctness module is a core component of TextRefine that evaluates the grammatical, mechanical, and stylistic correctness of text. It leverages LanguageTool as its backend service to identify and score various types of issues in text, providing detailed feedback and suggestions for improvement.

## Features

- **Comprehensive Grammar Checking**: Identifies grammatical errors and suggests corrections
- **Advanced Spell Checking**: Detects spelling mistakes and suggests corrections
- **Mechanical Analysis**: Evaluates punctuation, capitalization, and typography
- **Semantic Analysis**: Identifies issues with meaning and logical flow
- **Style Evaluation**: Provides feedback on writing style and consistency
- **Context-Aware**: Considers context for more accurate suggestions
- **Detailed Feedback**: Provides specific, actionable suggestions for each issue

## Error Categories and Severity

Each issue is categorized and assigned a severity level that affects the scoring:

### 1. Grammar Rules (Severity: 3)
- Subject-verb agreement
- Verb tense consistency
- Sentence structure
- Pronoun reference
- Modifier placement

### 2. Mechanics (Severity: 2)
- Punctuation errors
- Capitalization issues
- Compound word errors
- Orthographic inconsistencies
- Typography problems

### 3. Spelling & Typos (Severity: 1)
- Misspelled words
- Common typos
- Nonstandard word forms
- Homophone confusion

### 4. Word Usage (Severity: 2)
- Commonly confused words (their/there/they're)
- Incorrect collocations
- Redundant phrases
- Wordiness
- Register mismatch

### 5. Meaning & Logic (Severity: 4)
- Logical inconsistencies
- Contradictions
- Ambiguous references
- Unclear antecedents
- Semantic errors

### 6. Stylistic Issues (Severity: 1)
- Wordy or awkward phrasing
- Overused words or phrases
- Passive voice overuse
- Jargon or technical language
- Inconsistent style

### 7. Contextual Style (Severity: 1)
- Formality level
- Tone consistency
- Audience appropriateness
- Genre conventions

## Scoring System

The correctness score is calculated using a sophisticated algorithm that considers both the number and severity of issues found in the text.

### Key Components:
- **Base Score**: 100 (perfect score)
- **Word Normalization**: Scores are normalized per 100 words
- **Severity Weights**: Different issue types have different impacts on the score

### Penalty Calculation:
1. Each issue is assigned a base penalty based on its severity
2. Penalties are adjusted based on context and issue type
3. The total penalty is normalized by word count
4. Final score = 100 - (total_normalized_penalty * 100)

### Score Interpretation:
- **90-100**: Excellent - Minimal to no issues
- **80-89**: Good - Some minor issues
- **70-79**: Fair - Several issues that need attention
- **60-69**: Needs Work - Significant issues affecting clarity
- **Below 60**: Poor - Extensive issues requiring major revision

## Usage

### Basic Usage

```python
from correctness.service import CorrectnessService

# Initialize the service
service = CorrectnessService()

# Analyze text
result = service.compute_score("Your text to analyze here")


# Access basic results
print(f"Overall Score: {result.score}/100")
print(f"Word count: {result.word_count}")
print(f"Total issues found: {len(result.issues)}")

# View detailed issue breakdown
print("\nIssue Breakdown by Category:")
for category in result.breakdown:
    print(f"- {category.category}: {category.count} issues (Penalty: {category.penalty:.2f})")

# Access individual issues
print("\nSample Issues:")
for issue in result.issues[:3]:  # Show first 3 issues
    print(f"\n- Type: {issue.issue_type}")
    print(f"  Context: {issue.context}")
    print(f"  Message: {issue.message}")
    if issue.replacements:
        print(f"  Suggestion: {issue.replacements[0]}")
```

### Advanced Configuration

```python
from correctness.service import CorrectnessService
from correctness.models import AnalysisConfig

# Custom configuration
config = AnalysisConfig(
    language="en-US",
    enabled_categories={"GRAMMAR", "SPELLING", "PUNCTUATION"},
    max_suggestions=3,
    disabled_rules={"UPPERCASE_SENTENCE_START"}
)

# Initialize with custom config
service = CorrectnessService(config=config)
```

## API Reference

### `CorrectnessService`

Main service class for text correctness analysis.

**Methods:**

#### `compute_score(text: str) -> CorrectnessResult`
Analyzes the given text and returns a `CorrectnessResult` object.

**Parameters:**
- `text`: The text to analyze (str)

**Returns:**
- `CorrectnessResult`: Object containing analysis results

### Models

#### `CorrectnessResult`
- `score` (float): Overall correctness score (0-100)
- `word_count` (int): Number of words in the analyzed text
- `issues` (List[TextIssue]): List of all issues found
- `breakdown` (List[CategoryBreakdown]): Summary of issues by category
- `metadata` (Dict): Additional analysis metadata

#### `TextIssue`
- `issue_type` (str): Type of issue (e.g., "GRAMMAR", "SPELLING")
- `message` (str): Description of the issue
- `context` (str): The text context where the issue was found
- `offset` (int): Character offset of the issue in the text
- `length` (int): Length of the issue in characters
- `replacements` (List[str]): Suggested corrections
- `severity` (str): Issue severity (INFO, WARNING, ERROR)

## Dependencies

- Python 3.8+
- LanguageTool server (v5.0+ recommended)
- Python packages (see `requirements.txt`):
  - requests
  - pydantic
  - python-dotenv

## Setup

1. **Local LanguageTool Server** (Recommended for Development):
   ```bash
   # Using Docker (recommended)
   docker run -d -p 8010:8010 silviof/docker-languagetool:6.4
   
   # Or download and run locally
   # https://languagetool.org/download/
   ```

2. **Configuration**
   Set the LanguageTool server URL:
   ```bash
   # In your environment
   export LANGUAGE_TOOL_URL="http://localhost:8010/v2/check"
   
   # Or in a .env file
   echo "LANGUAGE_TOOL_URL=http://localhost:8010/v2/check" > .env
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Testing

The module includes a comprehensive test suite. To run tests:

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=correctness tests/

# Generate HTML coverage report
pytest --cov=correctness --cov-report=html tests/
```

## Performance

For optimal performance:
- Use a local LanguageTool server
- Batch process large documents in chunks
- Cache results for repeated analysis of similar texts
- Consider using async methods for high-throughput scenarios

## Contributing

Contributions are welcome! Please follow the project's coding standards and include tests with your pull requests.

## License

This module is part of the TextRefine project and is available under the MIT License.
