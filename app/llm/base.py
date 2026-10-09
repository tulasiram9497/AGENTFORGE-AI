from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_plan(self, goal: str, tool_names: list[str]):
        raise NotImplementedError

    @abstractmethod
    def generate_report(self, goal: str, plan: dict, evidence: list[dict], findings: str):
        raise NotImplementedError
