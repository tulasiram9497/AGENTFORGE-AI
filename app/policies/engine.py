from __future__ import annotations

from typing import Any

from app.schemas.models import PolicyDecision


class PolicyEngine:
    def __init__(self, allowlist: set[str] | None = None):
        self.allowlist = allowlist or set()

    def set_allowlist(self, names: set[str]) -> None:
        self.allowlist = set(names)

    def authorize_tool_call(self, tool_name: str, args: dict[str, Any], run_id: str | None = None) -> PolicyDecision:
        if tool_name not in self.allowlist:
            return PolicyDecision(
                allowed=False,
                reason=f"Tool '{tool_name}' is not registered or allowed for run {run_id or 'unknown'}.",
            )
        if not isinstance(args, dict):
            return PolicyDecision(allowed=False, reason="Tool arguments must be a dictionary.")
        sanitized = self._sanitize_args(args)
        if any(k in str(value).lower() for value in sanitized.values() for k in ("../", "bash -c", "eval(", "exec(", "import os", "subprocess")):
            return PolicyDecision(allowed=False, reason="Dangerous content detected in tool arguments.")
        if tool_name in {"calculator"}:
            return PolicyDecision(allowed=True, reason="Calculator invocation allowed.", sanitized_args=sanitized)
        return PolicyDecision(allowed=True, reason="Tool invocation authorized.", sanitized_args=sanitized)

    def _sanitize_args(self, args: dict[str, Any]) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}
        for key, value in args.items():
            if isinstance(value, str):
                cleaned = value.replace("\n", " ").strip()
                sanitized[key] = cleaned[:500]
            else:
                sanitized[key] = value
        return sanitized

    def validate_task_count(self, task_count: int) -> bool:
        return task_count <= 5
