from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.models import VerificationResult


class VerificationEngine:
    def __init__(self):
        self.results: list[VerificationResult] = []

    def check_task(self, task_name: str, result: dict, required_evidence: list[str] | None = None) -> VerificationResult:
        passed = bool(result.get("ok", False))
        evidence = ", ".join(required_evidence or [])
        if not passed:
            return VerificationResult(
                check_name=task_name,
                status="fail",
                evidence=evidence,
                failure_reason=result.get("error") or "Task did not complete successfully.",
                timestamp=datetime.now(UTC).isoformat(),
            )
        return VerificationResult(
            check_name=task_name,
            status="pass",
            evidence=evidence or str(result),
            timestamp=datetime.now(UTC).isoformat(),
        )

    def validate_citations(self, evidence: list[dict]) -> VerificationResult:
        valid = all(item.get("text") for item in evidence)
        if valid:
            return VerificationResult(
                check_name="citations",
                status="pass",
                evidence=f"{len(evidence)} citations verified.",
                timestamp=datetime.now(UTC).isoformat(),
            )
        return VerificationResult(
            check_name="citations",
            status="fail",
            evidence="",
            failure_reason="Citation list is incomplete or has missing text.",
            timestamp=datetime.now(UTC).isoformat(),
        )
