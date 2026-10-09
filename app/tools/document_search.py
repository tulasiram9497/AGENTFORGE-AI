from __future__ import annotations

from pathlib import Path


def document_search_tool(query: str, path: str | None = None) -> dict:
    base_dir = Path(path) if path else Path("data")
    if not base_dir.exists():
        return {"ok": True, "matches": [], "source": str(base_dir)}
    query_lower = query.lower()
    matches = []
    for file_path in base_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md"}:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            if query_lower in text.lower():
                matches.append({
                    "path": str(file_path),
                    "snippet": text[:200],
                })
    return {"ok": True, "matches": matches, "source": str(base_dir)}
