from correctness import compute_score

CORRECTNESS_WEIGHT = 0.25
CLARITY_WEIGHT = 0.25
VOCABULARY_WEIGHT = 0.20
COHERENCE_WEIGHT = 0.3


def get_correctness_score(text: str):
    return compute_score(text)


def get_clarity_score(text: str):
    return 100


def get_vocabulary_score(text: str):
    return 100


def get_coherence_score(text: str):
    return 100


def compute_global_score(
    correctness_score: float,
    clarity_score: float,
    vocabulary_score: float,
    coherence_score: float,
):

    return (
        (CORRECTNESS_WEIGHT * correctness_score)
        + (CLARITY_WEIGHT * clarity_score)
        + (VOCABULARY_WEIGHT * vocabulary_score)
        + (COHERENCE_WEIGHT * coherence_score)
    )


if __name__ == "__main__":
    text = """
    This are not a text with many different typez of errors. 
    First, there's a spelling error in 'typez'. 
    Second, there's a grammar error: 'Here is a lot of errors'. 
    Third, there's a capitaelizatioagagn error: 'i am a bot'. 
    Fourth, there's a punctduation error: missing comma after 'errors'. 
    Fifth, there's a style error: using 'a lot' instead of 'many'. 
    Finally, there's a sentenced strucsture error: 'Hesre is a lot of errors too'.
    """

    score = get_correctness_score(text)
    print(score)
    print(
        compute_global_score(
            score.score,
            get_clarity_score(text),
            get_vocabulary_score(text),
            get_coherence_score(text),
        )
    )
