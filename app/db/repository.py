from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base, AgentRunDB, ExecutionEventDB, FinalReportDB, KnowledgeDocumentDB, RetrievedChunkDB, ToolCallDB, VerificationResultDB

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine)


def serialize(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, default=str)


def create_run(goal: str, run_id: str, correlation_id: str) -> AgentRunDB:
    with SessionLocal() as session:
        record = AgentRunDB(id=run_id, goal=goal, status="PENDING", correlation_id=correlation_id)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def update_run_status(run_id: str, status: str) -> None:
    with SessionLocal() as session:
        record = session.get(AgentRunDB, run_id)
        if record:
            record.status = status
            record.updated_at = datetime.now(UTC)
            session.commit()


def save_plan(run_id: str, plan: Any) -> None:
    with SessionLocal() as session:
        record = session.get(AgentRunDB, run_id)
        if record:
            record.plan_json = serialize(plan)
            record.updated_at = datetime.now(UTC)
            session.commit()


def add_event(run_id: str, event_type: str, message: str) -> None:
    with SessionLocal() as session:
        event = ExecutionEventDB(run_id=run_id, event_type=event_type, message=message)
        session.add(event)
        session.commit()


def add_tool_call(run_id: str, tool_name: str, arguments: dict[str, Any], result: dict[str, Any], status: str) -> None:
    with SessionLocal() as session:
        record = ToolCallDB(
            run_id=run_id,
            tool_name=tool_name,
            arguments_json=serialize(arguments),
            result_json=serialize(result),
            status=status,
        )
        session.add(record)
        session.commit()


def add_verification(run_id: str, check_name: str, status: str, evidence: str, failure_reason: str | None = None) -> None:
    with SessionLocal() as session:
        record = VerificationResultDB(
            run_id=run_id,
            check_name=check_name,
            status=status,
            evidence=evidence,
            failure_reason=failure_reason,
        )
        session.add(record)
        session.commit()


def get_run(run_id: str) -> AgentRunDB | None:
    with SessionLocal() as session:
        return session.get(AgentRunDB, run_id)


def get_run_with_details(run_id: str) -> dict[str, Any]:
    with SessionLocal() as session:
        run = session.get(AgentRunDB, run_id)
        if not run:
            return {}
        return {
            "run_id": run.id,
            "goal": run.goal,
            "status": run.status,
            "correlation_id": run.correlation_id,
            "plan": json.loads(run.plan_json) if run.plan_json else None,
            "report": json.loads(run.report_json) if run.report_json else None,
            "events": [
                {"event_type": event.event_type, "message": event.message, "timestamp": event.timestamp.isoformat()}
                for event in run.events
            ],
            "tool_calls": [
                {"tool_name": call.tool_name, "arguments": json.loads(call.arguments_json or "{}"), "result": json.loads(call.result_json or "{}"), "status": call.status}
                for call in run.tool_calls
            ],
            "verification": [
                {"check_name": item.check_name, "status": item.status, "evidence": item.evidence, "failure_reason": item.failure_reason}
                for item in run.verifications
            ],
        }


def save_report(run_id: str, title: str, markdown: str, payload: dict[str, Any]) -> None:
    with SessionLocal() as session:
        record = FinalReportDB(
            id=f"report-{run_id}",
            run_id=run_id,
            title=title,
            markdown=markdown,
            json_data=serialize(payload),
        )
        session.add(record)
        run = session.get(AgentRunDB, run_id)
        if run:
            run.report_json = serialize(payload)
            run.updated_at = datetime.now(UTC)
        session.commit()


def save_knowledge_document(document_id: str, name: str, source_type: str, metadata: dict[str, Any], content: str) -> None:
    with SessionLocal() as session:
        session.add(
            KnowledgeDocumentDB(
                id=document_id,
                name=name,
                source_type=source_type,
                metadata_json=serialize(metadata),
                content=content,
            )
        )
        session.commit()


def save_chunk(document_id: str, chunk_id: str, text: str, metadata: dict[str, Any], score: float | None = None) -> None:
    with SessionLocal() as session:
        session.add(
            RetrievedChunkDB(
                id=f"{document_id}-{chunk_id}",
                document_id=document_id,
                chunk_id=chunk_id,
                text=text,
                metadata_json=serialize(metadata),
                score=score,
            )
        )
        session.commit()
