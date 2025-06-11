from json import JSONDecodeError
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from google.genai.errors import ClientError
from ..models import APIRequest
from ..limiter import get_limiter
from models import MIN_WORD_COUNT, GlobalScore
from logging_config import setup_logging

from language_tool_python.utils import LanguageToolError
import spacy
import time

from correctness import CorrectnessService
from vocabulary import VocabularyService
from readability import ReadabilityService
from coherence import CoherenceService
from dotenv import load_dotenv

load_dotenv()
logger = setup_logging()

router = APIRouter()

nlp = spacy.load("en_core_web_sm")
correctness_service = CorrectnessService(nlp=nlp)
vocabulary_service = VocabularyService(nlp=nlp)
readability_service = ReadabilityService()
coherence_service = CoherenceService()

LIMIT = os.getenv("EVALUATION_LIMIT", "5")
logger.info(f"Endpoint /evaluation limit set to {LIMIT} requests per minute.")

@router.post("/evaluation", response_model=GlobalScore)
@get_limiter().limit(
    f"{LIMIT}/minute",
    error_message=f"Limit set to {LIMIT} requests per minute. Please try again later.",
)
def evaluate_all(request: Request, input: APIRequest):
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

        logger.info("Analyzing text correctness...")
        correctness = correctness_service.analyze(input.text)

        logger.info("Analyzing text vocabulary...")
        vocabulary = vocabulary_service.analyze(input.text, correctness.issues)

        logger.info("Analyzing text readability...")
        readability = readability_service.analyze(input.text, audience=input.audience)

        logger.info("Analyzing text coherence...")
        coherence = coherence_service.analyze(input.text, topic=input.topic)

        logger.info("Creating global score...")
        result = GlobalScore(
            coherence=coherence,
            correctness=correctness,
            readability=readability,
            vocabulary=vocabulary,
        )

        logger.info(f"Evaluation completed. Global score: {result.score_in_percent}%.")
        logger.info(f"Evaluation duration: {time.time() - start_time:.2f} seconds.")
        return result

    except LanguageToolError as e:
        logger.error("Error calling LanguageTool API: %s", str(e))
        raise HTTPException(
            status_code=408,
            detail=f"Server timeout. Please try again.",
        )
    except JSONDecodeError as e:
        logger.error("Error decoding JSON response: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again.",
        )
    except (TypeError, ValueError, ValidationError) as e:
        logger.error(f"Invalid response format: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again.",
        )
    except ClientError as e:
        logger.error("Error calling Gemini API: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again.",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error, please try again. {str(e)}",
        )
