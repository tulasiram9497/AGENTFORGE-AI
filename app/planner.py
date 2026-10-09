from __future__ import annotations

import uuid
from collections import defaultdict

from app.schemas.models import ExecutionPlan, PlanTask


class Planner:
    def __init__(self, max_tasks: int = 5):
        self.max_tasks = max_tasks

    def create_plan(self, goal: str, tool_names: list[str] | None = None) -> ExecutionPlan:
        tool_names = tool_names or ["knowledge_search", "calculator"]
        tasks = [
            PlanTask(
                task_id="t1",
                description="Gather relevant evidence and identify the key facts required for the goal.",
                required_capabilities=[name for name in tool_names if name in {"knowledge_search", "document_search"}],
                dependencies=[],
                expected_output="Evidence-backed summary of relevant facts.",
                risk_level="low",
                verification_criteria=["Relevant evidence found", "No unsupported claim without source"],
            ),
            PlanTask(
                task_id="t2",
                description="Perform the necessary quantitative or comparative analysis needed for the decision.",
                required_capabilities=[name for name in tool_names if name == "calculator"],
                dependencies=["t1"],
                expected_output="Calculated or evaluated result.",
                risk_level="low",
                verification_criteria=["Calculation produced a valid result"],
            ),
            PlanTask(
                task_id="t3",
                description="Synthesize the final outcome and document limitations or open questions.",
                required_capabilities=["knowledge_search"],
                dependencies=["t1", "t2"],
                expected_output="Structured final answer with evidence and caveats.",
                risk_level="low",
                verification_criteria=["Report includes evidence and final findings"],
            ),
        ]
        if not self.validate_tasks([task.model_dump() for task in tasks]):
            raise ValueError("Generated plan is invalid")
        return ExecutionPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:8]}",
            goal=goal,
            tasks=tasks,
            estimated_task_count=len(tasks),
            summary=f"Plan for: {goal}",
        )

    def validate_tasks(self, tasks: list[dict] | list[PlanTask]) -> bool:
        if len(tasks) > self.max_tasks:
            return False
        seen_ids: set[str] = set()
        task_map: dict[str, dict] = {}
        for task in tasks:
            task_data = task.model_dump() if hasattr(task, "model_dump") else dict(task)
            task_id = task_data.get("task_id")
            if not task_id or task_id in seen_ids:
                return False
            seen_ids.add(task_id)
            task_map[task_id] = task_data
        for task in tasks:
            task_data = task.model_dump() if hasattr(task, "model_dump") else dict(task)
            dependencies = task_data.get("dependencies", [])
            for dep in dependencies:
                if dep not in task_map:
                    return False
        if self._has_cycle(task_map):
            return False
        return True

    def _has_cycle(self, tasks: dict[str, dict]) -> bool:
        graph = defaultdict(list)
        for task_id, task in tasks.items():
            for dep in task.get("dependencies", []):
                graph[dep].append(task_id)
        visited: set[str] = set()
        active: set[str] = set()

        def visit(node: str) -> bool:
            if node in active:
                return True
            if node in visited:
                return False
            visited.add(node)
            active.add(node)
            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True
            active.remove(node)
            return False

        for task_id in tasks:
            if visit(task_id):
                return True
        return False
