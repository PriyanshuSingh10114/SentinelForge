import math
from collections import Counter


def calculate_shannon_entropy(data: str) -> float:
    """
    Computes Shannon entropy (bits per character) of a string.
    High entropy (e.g. > 4.5) strongly indicates randomized tokens, encrypted text, or private keys.
    """
    if not data:
        return 0.0

    counts = Counter(data)
    total = len(data)
    entropy = 0.0

    for count in counts.values():
        prob = count / total
        entropy -= prob * math.log2(prob)

    return round(entropy, 3)
