# api/endpoints/evaluation.py
from fastapi import APIRouter, HTTPException
from models import MIN_WORD_COUNT, GlobalScore, TextInput
from correctness import CorrectnessService
from vocabulary import VocabularyService
import spacy

router = APIRouter()

nlp = spacy.load("en_core_web_sm")
correctness_service = CorrectnessService()
vocabulary_service = VocabularyService(nlp=nlp)

@router.post("/evaluate", response_model=GlobalScore)
def evaluate_all(input: TextInput):
    word_count = len(input.text.split())

    if word_count < MIN_WORD_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"Text is too short for evaluation (minimum {MIN_WORD_COUNT} words required).",
        )

    correctness = correctness_service.analyze(input.text)

    if(not correctness):
        raise HTTPException(
            status_code=500,
            detail="Error computing correctness score, please try again.",
        )
    # Get replacement words from correctness result
    replacement_words = correctness_service.get_replacement_words(
        input.text, correctness.issues
    )

    vocabulary = vocabulary_service.analyze(input.text, replacement_words)

    return GlobalScore(
        vocabulary=vocabulary,
        correctness=correctness,
    )
