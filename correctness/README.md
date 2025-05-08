# TextRefine Correctness Module

The Correctness module is a component of TextRefine that evaluates the grammatical and stylistic correctness of text. It leverages LanguageTool as its backend service to identify and score various types of issues in text.

## Features

- Grammar checking
- Spelling and typo detection
- Mechanics (punctuation, capitalization)
- Word usage analysis
- Meaning and logic analysis
- Stylistic issue detection
- Contextual style evaluation

## Error Categories

The module categorizes text issues into several main categories, each with a severity level:

1. **Grammar Rules** (Severity: 3)
   - Grammar rules
   - Capitalization
   - Upper/lowercase

2. **Mechanics** (Severity: 2)
   - Punctuation
   - Compounding
   - Orthographic errors
   - Typography

3. **Spelling & Typos** (Severity: 1)
   - Spelling errors
   - Possible typos
   - Nonstandard phrases

4. **Word Usage** (Severity: 2)
   - Commonly confused words
   - Collocations
   - Redundant phrases

5. **Meaning & Logic** (Severity: 4)
   - Semantics
   - Text analysis

6. **Stylistic Issues** (Severity: 1)
   - Style
   - Repetitions
   - Stylistic hints
   - Plain English

7. **Contextual Style** (Severity: 1)
   - Context-specific style issues

## Scoring System

- Maximum score: 100
- Score is normalized based on word count
- Penalty is calculated per word (100 words normalization factor)
- Each issue has a severity-based penalty
- Final score = MAX_SCORE - normalized_penalty

## Usage

```python
from correctness.service import CorrectnessService

# Example usage
result = CorrectnessService().compute_score("Your text to analyze here")

# Access results
print(f"Score: {result.score}")
print(f"Word count: {result.word_count}")
print(f"Normalized penalty: {result.normalized_penalty}")

# View issue breakdown by category
for breakdown in result.breakdown:
    print(f"Category: {breakdown.category}")
    print(f"Issue count: {breakdown.count}")
    print(f"Penalty: {breakdown.penalty}")
```

## Dependencies

- LanguageTool service (can be running locally or remotely)
- Python 3.x
- Required Python packages:
  - requests
  - pydantic

## Setup

1. Configure the LanguageTool service URL in your environment:
   - Set the `LANGUAGE_TOOL` environment variable to point to your LanguageTool instance
   - Default: `http://localhost:8081/v2/check?language=en-US`
2. Install required Python packages:
   ```bash
   pip install requests pydantic
   ```

## Testing

The module includes a comprehensive test suite in `tests/test_textissue.py` that verifies the correctness of issue detection and scoring.
