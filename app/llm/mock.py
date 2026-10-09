from __future__ import annotations

from app.llm.base import BaseLLMProvider
from app.planner import Planner


class MockLLMProvider(BaseLLMProvider):
    def generate_plan(self, goal: str, tool_names: list[str]):
        plan = Planner().create_plan(goal=goal, tool_names=tool_names)
        return plan.model_dump()

    def generate_report(self, goal: str, plan: dict, evidence: list[dict], findings: str):
        markdown = [
            "# AgentForge Summary",
            f"**Goal:** {goal}",
            "",
            "## Evidence",
        ]
        for chunk in evidence:
            markdown.append(f"- {chunk.get('source_name', 'unknown')}: {chunk.get('text', '')}")
        markdown.extend(["", "## Findings", findings])
        return {"title": "AgentForge Summary", "markdown": "\n".join(markdown), "summary": findings}
