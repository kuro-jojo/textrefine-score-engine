from models import GlobalScore


def get_correctness_score(text: str):
    from correctness import CorrectnessService

    correctness_service = CorrectnessService()
    score = correctness_service.compute_score(text)

    return score


def get_clarity_score(text: str):
    return 100


def get_vocabulary_score(text: str):
    from vocabulary import VocabularyService
    import spacy

    nlp = spacy.load("en_core_web_sm")
    vocabulary_service = VocabularyService(nlp=nlp)
    score = vocabulary_service.analyze(text)
    return score


def get_coherence_score(text: str):
    return 100


def compute_global_score(text: str):
    vocabulary_score = get_vocabulary_score(text)
    correctness_score = get_correctness_score(text)
    return GlobalScore(vocabulary_score, correctness_score)


if __name__ == "__main__":

    text = "Quantums computinng is is a multidisciplinary field comprising aspects of computer science, physics, and mathematics that utilizes quantum mechanics to solve complex problems faster than on classical computers. The field of quantum computing includes hardware research and application development. Quantum computers are able to solve certain types of problems faster than classical computers by taking advantage of quantum mechanical effects, such as superposition and quantum interference. Some applications where quantum computers can provide such a speed boost include machine learning (ML), optimization, and simulation of physical systems. Eventual use cases could be portfolio optimization in finance or the simulation of chemical systems, solving problems that are currently impossible for even the most powerful supercomputers on the market."
    text1 = "This is a multi-disciplinary field with a simple sentence with some repeated repeated words. "

    print(compute_global_score(text1))
