from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AgentRunDB(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    correlation_id: Mapped[str] = mapped_column(String(64), default="")
    plan_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    events: Mapped[list[ExecutionEventDB]] = relationship(back_populates="run")
    tool_calls: Mapped[list[ToolCallDB]] = relationship(back_populates="run")
    verifications: Mapped[list[VerificationResultDB]] = relationship(back_populates="run")


class ExecutionEventDB(Base):
    __tablename__ = "execution_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"))
    event_type: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    run: Mapped[AgentRunDB] = relationship(back_populates="events")


class ToolCallDB(Base):
    __tablename__ = "tool_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"))
    tool_name: Mapped[str] = mapped_column(String(128))
    arguments_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    run: Mapped[AgentRunDB] = relationship(back_populates="tool_calls")


class VerificationResultDB(Base):
    __tablename__ = "verification_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"))
    check_name: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pass")
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    run: Mapped[AgentRunDB] = relationship(back_populates="verifications")


class KnowledgeDocumentDB(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(64))
    metadata_json: Mapped[str | None] = mapped_column(JSON, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class RetrievedChunkDB(Base):
    __tablename__ = "retrieved_chunks"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64))
    chunk_id: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(JSON, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)


class FinalReportDB(Base):
    __tablename__ = "final_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(255))
    markdown: Mapped[str] = mapped_column(Text)
    json_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
