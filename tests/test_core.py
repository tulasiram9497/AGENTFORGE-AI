from app.planner import Planner
from app.policies.engine import PolicyEngine
from app.tools.registry import ToolRegistry
from app.rag.embeddings import SimpleEmbeddingModel
from app.rag.retrieval import RetrievalIndex


def test_planner_generates_plan():
    planner = Planner()
    plan = planner.create_plan(
        goal="Summarize the latest product updates and answer whether the team should ship.",
        tool_names=["calculator", "knowledge_search"],
    )
    assert plan.goal
    assert len(plan.tasks) >= 2
    assert plan.tasks[0].task_id


def test_invalid_plan_rejected_for_cycle():
    planner = Planner()
    tasks = [
        {
            "task_id": "t1",
            "description": "first",
            "required_capabilities": ["calculator"],
            "dependencies": ["t2"],
            "expected_output": "A",
            "verification_criteria": ["done"],
            "risk_level": "low",
        },
        {
            "task_id": "t2",
            "description": "second",
            "required_capabilities": ["calculator"],
            "dependencies": ["t1"],
            "expected_output": "B",
            "verification_criteria": ["done"],
            "risk_level": "low",
        },
    ]
    result = planner.validate_tasks(tasks)
    assert result is False


def test_policy_engine_rejects_unknown_tool():
    engine = PolicyEngine()
    decision = engine.authorize_tool_call("unknown_tool", {"x": 1}, run_id="run-1")
    assert decision.allowed is False
    assert "not registered" in decision.reason.lower()


def test_tool_registry_dispatches():
    registry = ToolRegistry()
    tool = registry.get_tool("calculator")
    result = registry.dispatch("calculator", {"expression": "2 + 3 * 4"})
    assert result["ok"] is True
    assert result["result"] == 14
    assert tool is not None


def test_rag_retrieval_works():
    embedding_model = SimpleEmbeddingModel()
    index = RetrievalIndex(embedding_model)
    index.add_document("doc-1", "Product launch plan", "The launch will be on Friday and requires QA approval.")
    index.add_document("doc-2", "Support notes", "The support team says downtime is risky before launch.")
    hits = index.search("launch approval risk")
    assert len(hits) > 0
    assert hits[0].document_id in {"doc-1", "doc-2"}
