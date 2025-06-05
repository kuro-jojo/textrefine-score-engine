from fastapi import APIRouter, HTTPException, Request
from language_tool_python.utils import LanguageToolError
from models import MIN_WORD_COUNT, GlobalScore, TextInput
from correctness import CorrectnessService
from vocabulary import VocabularyService
from readability import ReadabilityService
import spacy
from logging_config import setup_logging
from ..limiter import get_limiter
import time

logger = setup_logging()

router = APIRouter()

nlp = spacy.load("en_core_web_sm")
correctness_service = CorrectnessService(nlp=nlp)
vocabulary_service = VocabularyService(nlp=nlp)
readability_service = ReadabilityService()


@router.post("/evaluation", response_model=GlobalScore)
@get_limiter().limit(
    "5/minute",
    error_message="Limit set to 5 requests per minute. Please try again later.",
)
def evaluate_all(request: Request, input: TextInput):
    try:
        start_time = time.time()
        logger.info(f"Starting evaluation for text: {input.text[:10]}...")
        word_count = len(input.text.split())

        if word_count < MIN_WORD_COUNT:
            logger.warning(f"Text too short for evaluation (word count: {word_count})")
            raise HTTPException(
                status_code=400,
                detail=f"Text is too short for evaluation (minimum {MIN_WORD_COUNT} words required).",
            )

        logger.info("Analyzing correctness...")
        correctness = correctness_service.analyze(input.text)

        logger.info("Analyzing vocabulary (diversity, sophistication, precision)...")
        vocabulary = vocabulary_service.analyze(input.text, correctness.issues)

        logger.info("Analyzing readability...")
        readability = readability_service.analyze(input.text)

        logger.info("Creating global score...")
        result = GlobalScore(
            vocabulary=vocabulary,
            correctness=correctness,
            readability=readability,
        )

        logger.info(f"Evaluation completed. Score: {result.score_in_percent}%.")
        logger.info(f"Response time: {time.time() - start_time:.2f} seconds.")
        return result

    except LanguageToolError as e:
        logger.error("Error calling LanguageTool API: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again.",
        )

    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again. {str(e)}",
        )
