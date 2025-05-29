# api/endpoints/evaluation.py
from fastapi import APIRouter, HTTPException
from models import MIN_WORD_COUNT, GlobalScore, TextInput
from correctness import CorrectnessService
from vocabulary import VocabularyService
import spacy
from logging_config import setup_logging

logger = setup_logging()

router = APIRouter()

nlp = spacy.load("en_core_web_sm")
correctness_service = CorrectnessService()
vocabulary_service = VocabularyService(nlp=nlp)

@router.post("/evaluate", response_model=GlobalScore)
def evaluate_all(input: TextInput):
    try:
        logger.info(f"Starting evaluation for text: {input.text[:100]}...")
        word_count = len(input.text.split())

        if word_count < MIN_WORD_COUNT:
            logger.warning(f"Text too short for evaluation (word count: {word_count})")
            raise HTTPException(
                status_code=400,
                detail=f"Text is too short for evaluation (minimum {MIN_WORD_COUNT} words required).",
            )

        logger.info("Analyzing correctness...")
        correctness = correctness_service.analyze(input.text)

        if not correctness:
            logger.error("Failed to compute correctness score")
            raise HTTPException(
                status_code=500,
                detail="Error computing correctness score, please try again.",
            )

        logger.info("Getting replacement words...")
        replacement_words = correctness_service.get_replacement_words(
            input.text, correctness.issues
        )

        logger.info("Analyzing vocabulary...")
        vocabulary = vocabulary_service.analyze(input.text, replacement_words)

        logger.info("Creating global score...")
        result = GlobalScore(
            vocabulary=vocabulary,
            correctness=correctness,
        )
        logger.info(f"Evaluation completed. Score: {result.score_in_percent}%")
        return result

    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
