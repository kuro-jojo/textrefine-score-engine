# TextRefine

TextRefine is an AI-powered text analysis and scoring engine designed to evaluate text quality across multiple dimensions. The engine provides detailed scores and feedback to help improve writing quality.

## Scoring Components

TextRefine's scoring engine evaluates text across four key dimensions:

1. **Correctness (25%)**
   - Grammar accuracy
   - Spelling and typos
   - Mechanics (punctuation, capitalization)
   - Word usage
   - Meaning and logic
   - Stylistic issues
   - Contextual style

2. **Vocabulary (20%)**
   - Word choice and variety
   - Lexical richness
   - Domain-specific terminology
   - Register and tone

3. **Clarity (25%)**
   - Sentence structure
   - Readability
   - Coherence within sentences
   - Information hierarchy

4. **Coherence (30%)**
   - Paragraph organization
   - Topic flow
   - Logical progression
   - Contextual relevance

## Project Structure

```
scoreEngine/
├── correctness/           # Grammar and correctness scoring
│   ├── scorer.py         # Main scoring implementation
│   ├── types.py          # Data structures and enums
│   └── parser.py         # LanguageTool response parsing
├── vocabulary/           # Vocabulary analysis
├── clarity/              # Clarity scoring
├── coherence/            # Coherence analysis
└── main.py              # Main entry point
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure LanguageTool service:
   - Set the `LANGUAGE_TOOL` environment variable to point to your LanguageTool instance
   - Default: `http://localhost:8081/v2/check?language=en-US`

## Usage

```python
from scoreEngine import TextRefine

text = "Your text to analyze here"
analyzer = TextRefine()

# Get comprehensive analysis
results = analyzer.analyze(text)

# Access individual scores
print(f"Correctness: {results.correctness.score}")
print(f"Vocabulary: {results.vocabulary.score}")
print(f"Clarity: {results.clarity.score}")
print(f"Coherence: {results.coherence.score}")

# Get overall score
print(f"Overall Score: {results.overall_score}")
```

## Development

The project follows a modular architecture, with each scoring component implemented as a separate module. Each module includes:

- Scoring implementation
- Data structures
- Test suite
- Documentation

### Running Tests

```bash
python -m unittest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Write tests
5. Submit a pull request

## License


## Contact

