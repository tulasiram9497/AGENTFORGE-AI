from __future__ import annotations

from app.schemas.models import StateName

VALID_TRANSITIONS = {
    "PENDING": {"PLANNING", "CANCELLED"},
    "PLANNING": {"PLANNED", "FAILED", "CANCELLED"},
    "PLANNED": {"RUNNING", "WAITING_FOR_APPROVAL", "FAILED", "CANCELLED"},
    "RUNNING": {"VERIFYING", "WAITING_FOR_APPROVAL", "SUCCEEDED", "FAILED", "CANCELLED"},
    "WAITING_FOR_APPROVAL": {"RUNNING", "FAILED", "CANCELLED"},
    "VERIFYING": {"SUCCEEDED", "FAILED", "CANCELLED"},
    "SUCCEEDED": set(),
    "FAILED": set(),
    "CANCELLED": set(),
}


class StateMachine:
    def __init__(self, initial_state: StateName = "PENDING"):
        self.current = initial_state

    def transition(self, new_state: StateName) -> StateName:
        allowed = VALID_TRANSITIONS.get(self.current, set())
        if new_state not in allowed:
            raise ValueError(f"Invalid state transition from {self.current} to {new_state}")
        self.current = new_state
        return self.current

    def is_terminal(self) -> bool:
        return self.current in {"SUCCEEDED", "FAILED", "CANCELLED"}
