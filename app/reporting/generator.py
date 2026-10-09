from __future__ import annotations

from datetime import UTC, datetime


class ReportGenerator:
    def __init__(self):
        pass

    def generate(self, goal: str, plan: dict, tool_calls: list[dict], evidence: list[dict], verification: list[dict], findings: str, status: str) -> dict:
        markdown_lines = [
            "# AgentForge AI Report",
            f"**Goal:** {goal}",
            f"**Generated:** {datetime.now(UTC).isoformat()}",
            f"**Final Status:** {status}",
            "",
            "## Approved Execution Plan",
        ]
        for task in plan.get("tasks", []):
            markdown_lines.append(f"- {task['task_id']}: {task['description']}")
        markdown_lines.append("")
        markdown_lines.append("## Tool Calls")
        for call in tool_calls:
            markdown_lines.append(f"- {call.get('tool_name')}: {call.get('status')}")
        markdown_lines.append("")
        markdown_lines.append("## Evidence")
        for chunk in evidence:
            markdown_lines.append(f"- {chunk.get('source_name', 'source')}: {chunk.get('text', '')}")
        markdown_lines.append("")
        markdown_lines.append("## Verification Results")
        for check in verification:
            markdown_lines.append(f"- {check.get('check_name')}: {check.get('status')}")
        markdown_lines.append("")
        markdown_lines.append("## Final Findings")
        markdown_lines.append(findings)
        return {
            "title": "AgentForge AI Report",
            "goal": goal,
            "markdown": "\n".join(markdown_lines),
            "status": status,
            "verified_facts": [item.get("evidence", "") for item in verification if item.get("status") == "pass"],
            "evidence": evidence,
            "interpretations": [findings],
        }
