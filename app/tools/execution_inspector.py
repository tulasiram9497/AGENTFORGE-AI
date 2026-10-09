from __future__ import annotations


def execution_inspector_tool(run_id: str) -> dict:
    return {
        "ok": True,
        "run_id": run_id,
        "status": "PLANNED",
        "task_count": 3,
        "events": [{"type": "created", "run_id": run_id}],
    }
