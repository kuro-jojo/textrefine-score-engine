# TextRefine Score Engine

TextRefine Score Engine is a comprehensive text analysis and scoring system that evaluates writing quality across multiple dimensions. The engine provides quantitative scores and qualitative feedback to help identify areas for improvement in written content.

## Key Features

- **Multi-dimensional Analysis**: Evaluates text across four key dimensions
- **Detailed Feedback**: Provides specific, actionable suggestions for improvement
- **RESTful API**: Easy integration with other applications
- **Docker Support**: Simple deployment with containerization
- **Extensible Architecture**: Modular design for adding new analysis components

## Scoring Components

TextRefine's scoring engine evaluates text across four key dimensions:

### 1. Correctness (35%)
- Grammar accuracy and syntax
- Spelling and typo detection
- Punctuation and mechanics
- Word usage and style
- Semantic and logical coherence
- Contextual appropriateness

### 2. Vocabulary (25%)
- Lexical diversity and richness
- Word choice precision
- Domain-specific terminology
- Register and tone consistency
- Sophistication of language

### 3. Readability (15%)
- Sentence structure complexity
- Readability metrics (Flesch-Kincaid, etc.)
- Information density
- Text organization
- Visual presentation

### 4. Coherence (25%)
- Paragraph structure
- Topic flow and transitions
- Logical progression of ideas
- Overall text cohesion
- Contextual relevance

## Project Structure

```
scoreEngine/
├── api/                    # FastAPI application and endpoints
├── coherence/              # Coherence analysis module
├── commons/                # Shared utilities and models
├── correctness/            # Grammar and correctness scoring
├── language_tool/          # LanguageTool integration
├── readability/            # Readability analysis
├── vocabulary/             # Vocabulary analysis
├── .github/               # GitHub workflows and templates
├── tests/                  # Test suite
├── Dockerfile             # Container configuration
├── main.py                # Application entry point
├── models.py              # Core data models
├── requirements.txt       # Python dependencies
└── logging_config.py      # Logging configuration
```

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- LanguageTool server (can be run in a container)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/TextRefine.git
   cd TextRefine/scoreEngine
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t textrefine-scoreengine .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 textrefine-scoreengine
   ```

## API Documentation

Once the service is running, you can access:
- API documentation: `http://localhost:8000/docs`
- Alternative documentation: `http://localhost:8000/redoc`

### Running Tests

```bash
pytest -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue in the repository.

