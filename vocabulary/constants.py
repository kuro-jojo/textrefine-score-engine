# weights for each component
LEXICAL_DIVERSITY_WEIGHT = 0.3  # lexical diversity
SOPHISTICATION_WEIGHT = 0.35  # word sophistication
PRECISION_WEIGHT = 0.35  # word precision

# weights for each word type
RARE_WORDS_WEIGHT = 1.5  # words that are very rare
MID_WORDS_WEIGHT = 1.0  # words that are not rare but not common
COMMON_WORDS_WEIGHT = 0.5  # common words
UNKNOWN_WORDS_WEIGHT = -0.2  # words that are not in the dictionary
MAX_SOPHISTICATION = 1.5  # cap based on expected range

# thresholds for each word type
COMMON_WORDS_THRESHOLD = 5.0
MID_WORDS_THRESHOLD = 3.5
