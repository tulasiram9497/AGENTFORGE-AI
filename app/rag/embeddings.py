from __future__ import annotations

import math
from collections import Counter


class SimpleEmbeddingModel:
    def embed(self, text: str) -> list[float]:
        tokens = [token.lower() for token in text.replace("\n", " ").split() if token]
        counts = Counter(tokens)
        norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
        vector = [float(value) / norm for value in counts.values()]
        return vector
