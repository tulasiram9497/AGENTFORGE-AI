from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


StateName = Literal[
    "PENDING",
    "PLANNING",
    "PLANNED",
    "RUNNING",
    "WAITING_FOR_APPROVAL",
    "VERIFYING",
    "SUCCEEDED",
    "FAILED",
    "CANCELLED",
]


class PlanTask(BaseModel):
    task_id: str
    description: str
    required_capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    expected_output: str
    risk_level: str = "low"
    verification_criteria: list[str] = Field(default_factory=list)
    status: str = "pending"


class ExecutionPlan(BaseModel):
    plan_id: str
    goal: str
    tasks: list[PlanTask]
    estimated_task_count: int = 0
    summary: str = ""


class ToolResult(BaseModel):
    ok: bool
    tool: str
    result: Any = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    run_id: str | None = None


class PolicyDecision(BaseModel):
    allowed: bool
    reason: str
    requires_approval: bool = False
    sanitized_args: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    check_name: str
    status: Literal["pass", "fail", "warning"]
    evidence: str = ""
    failure_reason: str | None = None
    timestamp: str


class RetrievedChunk(BaseModel):
    document_id: str
    source_name: str
    chunk_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None


class FinalReport(BaseModel):
    title: str
    goal: str
    summary: str = ""
    markdown: str = ""
    status: str = "draft"
    verified_facts: list[str] = Field(default_factory=list)
    evidence: list[RetrievedChunk] = Field(default_factory=list)
    interpretations: list[str] = Field(default_factory=list)


class AgentRunRecord(BaseModel):
    run_id: str
    goal: str
    status: StateName = "PENDING"
    correlation_id: str
    plan: ExecutionPlan | None = None
    report: FinalReport | None = None
    output: dict[str, Any] = Field(default_factory=dict)
