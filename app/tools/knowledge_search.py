from __future__ import annotations

from app.rag.retrieval import retrieval_index


def knowledge_search_tool(query: str) -> dict:
    hits = retrieval_index.search(query)
    results = [
        {
            "document_id": hit.document_id,
            "source_name": hit.source_name,
            "chunk_id": hit.chunk_id,
            "text": hit.text,
            "score": hit.score,
        }
        for hit in hits
    ]
    return {"ok": True, "hits": results, "count": len(results)}
