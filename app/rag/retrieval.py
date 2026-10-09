from __future__ import annotations

from dataclasses import dataclass

from app.rag.embeddings import SimpleEmbeddingModel
from app.schemas.models import RetrievedChunk


@dataclass
class RetrievalHit:
    document_id: str
    source_name: str
    chunk_id: str
    text: str
    metadata: dict
    score: float


class RetrievalIndex:
    def __init__(self, embedder: SimpleEmbeddingModel | None = None):
        self.embedder = embedder or SimpleEmbeddingModel()
        self.documents: dict[str, dict] = {}
        self.chunks: list[RetrievedChunk] = []

    def add_document(self, document_id: str, source_name: str, text: str, metadata: dict | None = None) -> None:
        self.documents[document_id] = {"source_name": source_name, "text": text, "metadata": metadata or {}}
        chunks = [text[i : i + 180] for i in range(0, max(len(text), 1), 180)]
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            self.chunks.append(
                RetrievedChunk(
                    document_id=document_id,
                    source_name=source_name,
                    chunk_id=f"{document_id}-chunk-{idx}",
                    text=chunk,
                    metadata={"source_name": source_name, **(metadata or {})},
                    score=0.0,
                )
            )

    def search(self, query: str, top_k: int = 3) -> list[RetrievalHit]:
        query_vector = self.embedder.embed(query)
        hits: list[RetrievalHit] = []
        for chunk in self.chunks:
            chunk_vector = self.embedder.embed(chunk.text)
            score = self._cosine_similarity(query_vector, chunk_vector)
            if score > 0:
                hits.append(
                    RetrievalHit(
                        document_id=chunk.document_id,
                        source_name=chunk.source_name,
                        chunk_id=chunk.chunk_id,
                        text=chunk.text,
                        metadata=chunk.metadata,
                        score=score,
                    )
                )
        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        shorter = min(len(a), len(b))
        if shorter == 0:
            return 0.0
        dot = sum(x * y for x, y in zip(a[:shorter], b[:shorter]))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(x * x for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


retrieval_index = RetrievalIndex()
