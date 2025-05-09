import spacy
from models import GlobalScore
from correctness import CorrectnessService
from vocabulary import VocabularyService


def get_correctness_score(text_to_analyze: str):

    correctness_service = CorrectnessService()
    score = correctness_service.compute_score(text_to_analyze)

    return score


def get_clarity_score(text_to_analyze: str):
    return 100


def get_vocabulary_score(text_to_analyze: str):

    nlp = spacy.load("en_core_web_sm")
    vocabulary_service = VocabularyService(nlp=nlp)
    score = vocabulary_service.analyze(text_to_analyze)
    return score


def get_coherence_score(text_to_analyze: str):
    return 100


def compute_global_score(text_to_analyze: str):
    vocabulary_score = get_vocabulary_score(text_to_analyze)
    correctness_score = get_correctness_score(text_to_analyze)
    return GlobalScore(vocabulary_score, correctness_score)


if __name__ == "__main__":

    text = "Quantums computinng is is a multidisciplinary field comprising aspects of computer science, physics, and mathematics that utilizes quantum mechanics to solve complex problems faster than on classical computers. The field of quantum computing includes hardware research and application development. Quantum computers are able to solve certain types of problems faster than classical computers by taking advantage of quantum mechanical effects, such as superposition and quantum interference. Some applications where quantum computers can provide such a speed boost include machine learning (ML), optimization, and simulation of physical systems. Eventual use cases could be portfolio optimization in finance or the simulation of chemical systems, solving problems that are currently impossible for even the most powerful supercomputers on the market."

    text1 = "This is a multi-disciplinary to field with a simple sentence with some repeated repeated words. It is also awkwardl structured!"

    text2 = "In recent decades, the epistemological framework surrounding postmodern critical theory has undergone significant transformation, prompting scholars to reassess traditional conceptions of objectivity, authorship, and textual interpretation. The destabilization is. After completing the science project, Maria realized that her hypothesis had been correct. She documented each step in her notebook and prepared a short report explaining her findings. Though the experiment was simple, it helped her understand the scientific method more deeply and inspired her to learn more about chemistry and biology."

    print(compute_global_score(text2))
