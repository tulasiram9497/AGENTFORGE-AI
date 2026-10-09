from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.db.repository import add_event, add_tool_call, add_verification, create_run, get_run_with_details, save_plan, save_report, update_run_status
from app.llm.mock import MockLLMProvider
from app.planner import Planner
from app.policies.engine import PolicyEngine
from app.reporting.generator import ReportGenerator
from app.rag.retrieval import retrieval_index
from app.state_machine import StateMachine
from app.tools.registry import ToolRegistry
from app.verification.engine import VerificationEngine

logger = get_logger(__name__)


class AgentOrchestrator:
    def __init__(self):
        self.registry = ToolRegistry()
        self.policy = PolicyEngine(allowlist=set(self.registry.names()))
        self.planner = Planner(max_tasks=settings.DEFAULT_TASK_LIMIT)
        self.state_machine = StateMachine()
        self.llm = MockLLMProvider()
        self.verification = VerificationEngine()
        self.reporter = ReportGenerator()
        self.runs: dict[str, dict[str, Any]] = {}

    def create_run(self, goal: str, tool_names: list[str] | None = None) -> dict[str, Any]:
        run_id = f"run-{uuid.uuid4().hex[:8]}"
        correlation_id = f"corr-{uuid.uuid4().hex[:8]}"
        create_run(goal, run_id, correlation_id)
        add_event(run_id, "created", f"Run created for goal: {goal}")
        self.runs[run_id] = {"goal": goal, "status": "PENDING", "tool_names": tool_names or ["calculator", "knowledge_search"]}
        return {"run_id": run_id, "correlation_id": correlation_id, "status": "PENDING"}

    def generate_plan(self, run_id: str, goal: str, tool_names: list[str] | None = None) -> dict[str, Any]:
        tool_names = tool_names or self.runs.get(run_id, {}).get("tool_names", ["calculator", "knowledge_search"])
        plan = self.planner.create_plan(goal=goal, tool_names=tool_names)
        self.runs[run_id]["plan"] = plan.model_dump()
        save_plan(run_id, plan.model_dump())
        update_run_status(run_id, "PLANNED")
        add_event(run_id, "planned", f"Plan generated: {plan.plan_id}")
        return plan.model_dump()

    def execute_run(self, run_id: str, goal: str, tool_names: list[str] | None = None) -> dict[str, Any]:
        tool_names = tool_names or self.runs.get(run_id, {}).get("tool_names", ["calculator", "knowledge_search"])
        plan = self.generate_plan(run_id, goal, tool_names)
        evidence: list[dict[str, Any]] = []
        tool_calls: list[dict[str, Any]] = []
        verification_results: list[dict[str, Any]] = []
        self.runs[run_id]["status"] = "RUNNING"
        update_run_status(run_id, "RUNNING")

        for task in plan.get("tasks", []):
            capability = task.get("required_capabilities") or []
            task_result: dict[str, Any] = {"ok": True, "result": "Task completed"}
            if "knowledge_search" in capability:
                query = task.get("description", goal)
                decision = self.policy.authorize_tool_call("knowledge_search", {"query": query}, run_id)
                if not decision.allowed:
                    task_result = {"ok": False, "error": decision.reason}
                else:
                    tool_response = self.registry.dispatch("knowledge_search", {"query": query})
                    task_result = tool_response
                    results = tool_response.get("hits", [])
                    for hit in results:
                        evidence.append({
                            "document_id": hit.get("document_id"),
                            "source_name": hit.get("source_name"),
                            "chunk_id": hit.get("chunk_id"),
                            "text": hit.get("text"),
                            "score": hit.get("score"),
                        })
                    add_tool_call(run_id, "knowledge_search", {"query": query}, tool_response, "success" if tool_response.get("ok") else "failure")
            if "calculator" in capability:
                expression = "2 + 3 * 4"
                decision = self.policy.authorize_tool_call("calculator", {"expression": expression}, run_id)
                if not decision.allowed:
                    task_result = {"ok": False, "error": decision.reason}
                else:
                    tool_response = self.registry.dispatch("calculator", {"expression": expression})
                    task_result = tool_response
                    add_tool_call(run_id, "calculator", {"expression": expression}, tool_response, "success" if tool_response.get("ok") else "failure")
            verification = self.verification.check_task(task["task_id"], task_result, ["result available"])
            verification_results.append(verification.model_dump())
            add_verification(run_id, verification.check_name, verification.status, verification.evidence, verification.failure_reason)
            task_calls = [
                {"status": "success" if task_result.get("ok") else "failure", "tool_name": "knowledge_search" if "knowledge_search" in capability else "calculator"}
            ]
            tool_calls.extend(task_calls)

        verification_summary = self.verification.validate_citations(evidence)
        verification_results.append(verification_summary.model_dump())
        add_verification(run_id, verification_summary.check_name, verification_summary.status, verification_summary.evidence, verification_summary.failure_reason)

        final_findings = "The workflow completed with evidence-based findings and no critical policy violations were observed." if evidence else "No relevant evidence was found; the system noted the limitation."
        report_payload = self.reporter.generate(goal, plan, tool_calls, evidence, verification_results, final_findings, "SUCCEEDED")
        save_report(run_id, report_payload["title"], report_payload["markdown"], report_payload)
        self.runs[run_id]["report"] = report_payload
        self.runs[run_id]["status"] = "SUCCEEDED"
        update_run_status(run_id, "SUCCEEDED")
        add_event(run_id, "completed", "Execution finished successfully.")
        return {"run_id": run_id, "status": "SUCCEEDED", "report": report_payload}

    def get_run(self, run_id: str) -> dict[str, Any]:
        return get_run_with_details(run_id)

    def get_plan(self, run_id: str) -> dict[str, Any]:
        run = get_run_with_details(run_id)
        return run.get("plan") or {}

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        run = get_run_with_details(run_id)
        return run.get("events", [])

    def get_report(self, run_id: str) -> dict[str, Any]:
        run = get_run_with_details(run_id)
        return run.get("report") or {}

    def approve_run(self, run_id: str, approval: dict[str, Any]) -> dict[str, Any]:
        if approval.get("approved") is not True:
            return {"ok": False, "error": "Approval denied."}
        update_run_status(run_id, "RUNNING")
        return {"ok": True, "message": f"Approval accepted for {run_id}."}

    def cancel_run(self, run_id: str) -> dict[str, Any]:
        update_run_status(run_id, "CANCELLED")
        add_event(run_id, "cancelled", "Run cancelled by operator.")
        return {"ok": True, "status": "CANCELLED"}
