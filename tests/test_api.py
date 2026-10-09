from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_run_creation_and_report_retrieval():
    payload = {"goal": "Assess launch readiness using local evidence.", "tool_names": ["calculator", "knowledge_search"]}
    response = client.post("/api/v1/runs", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "run_id" in body
    run_id = body["run_id"]

    plan_response = client.get(f"/api/v1/runs/{run_id}/plan")
    assert plan_response.status_code == 200
    assert len(plan_response.json()["tasks"]) >= 2

    doc_response = client.post("/api/v1/knowledge/documents", json={"name": "launch.md", "content": "The launch is approved after QA sign-off and release checks."})
    assert doc_response.status_code == 200
    search_response = client.post("/api/v1/knowledge/search", json={"query": "QA sign-off"})
    assert search_response.status_code == 200
    assert len(search_response.json()["hits"]) >= 1

    report_response = client.get(f"/api/v1/runs/{run_id}/report")
    assert report_response.status_code == 200
    assert "markdown" in report_response.json()
