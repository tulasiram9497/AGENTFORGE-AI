from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.orchestrator import AgentOrchestrator

router = APIRouter()
_orchestrator = AgentOrchestrator()


@router.get("/health")
def health():
    return {"status": "ok", "service": "AgentForge AI"}


@router.get("/ready")
def ready():
    return {"status": "ready", "database": "ok", "rag": "ok"}


@router.post("/api/v1/runs")
def create_run(payload: dict):
    goal = payload.get("goal", "")
    if not goal:
        raise HTTPException(status_code=400, detail="Goal is required")
    result = _orchestrator.create_run(goal, payload.get("tool_names", ["calculator", "knowledge_search"]))
    run_id = result["run_id"]
    _orchestrator.execute_run(run_id, goal, payload.get("tool_names", ["calculator", "knowledge_search"]))
    return result


@router.get("/api/v1/runs/{run_id}")
def get_run(run_id: str):
    return _orchestrator.get_run(run_id)


@router.get("/api/v1/runs/{run_id}/plan")
def get_plan(run_id: str):
    return _orchestrator.get_plan(run_id)


@router.get("/api/v1/runs/{run_id}/events")
def get_events(run_id: str):
    return _orchestrator.get_events(run_id)


@router.get("/api/v1/runs/{run_id}/report")
def get_report(run_id: str):
    return _orchestrator.get_report(run_id)


@router.post("/api/v1/knowledge/documents")
def ingest_document(payload: dict):
    name = payload.get("name", "document")
    content = payload.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Document content is required")
    from app.rag.retrieval import retrieval_index
    document_id = f"doc-{len(retrieval_index.documents) + 1}"
    retrieval_index.add_document(document_id, name, content)
    return {"document_id": document_id, "status": "stored"}


@router.post("/api/v1/knowledge/search")
def search_document(payload: dict):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    from app.rag.retrieval import retrieval_index
    return {"hits": [hit.__dict__ for hit in retrieval_index.search(query)]}


@router.get("/api/v1/tools")
def get_tools():
    return {"tools": _orchestrator.registry.names()}


@router.post("/api/v1/runs/{run_id}/approve")
def approve_run(run_id: str, payload: dict):
    return _orchestrator.approve_run(run_id, payload)


@router.post("/api/v1/runs/{run_id}/cancel")
def cancel_run(run_id: str):
    return _orchestrator.cancel_run(run_id)
