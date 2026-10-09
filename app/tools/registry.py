from __future__ import annotations

from typing import Any, Callable

from app.tools.calculator import calculator_tool
from app.tools.document_search import document_search_tool
from app.tools.execution_inspector import execution_inspector_tool
from app.tools.knowledge_search import knowledge_search_tool


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        permission_level: str,
        timeout: int,
        requires_approval: bool,
        function: Callable[..., Any],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.permission_level = permission_level
        self.timeout = timeout
        self.requires_approval = requires_approval
        self.function = function


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register(
            ToolDefinition(
                name="calculator",
                description="Safely evaluate arithmetic expressions.",
                input_schema={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
                permission_level="read",
                timeout=5,
                requires_approval=False,
                function=calculator_tool,
            )
        )
        self.register(
            ToolDefinition(
                name="document_search",
                description="Search approved local files for relevant snippets.",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string"}}, "required": ["query"]},
                permission_level="read",
                timeout=10,
                requires_approval=False,
                function=document_search_tool,
            )
        )
        self.register(
            ToolDefinition(
                name="knowledge_search",
                description="Search the local knowledge base for grounded evidence.",
                input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
                permission_level="read",
                timeout=10,
                requires_approval=False,
                function=knowledge_search_tool,
            )
        )
        self.register(
            ToolDefinition(
                name="execution_inspector",
                description="Inspect run status and recent events.",
                input_schema={"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]},
                permission_level="read",
                timeout=5,
                requires_approval=False,
                function=execution_inspector_tool,
            )
        )

    def register(self, definition: ToolDefinition) -> None:
        self.tools[definition.name] = definition

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self.tools.get(name)

    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self.get_tool(name)
        if tool is None:
            return {"ok": False, "error": f"Tool '{name}' is not registered."}
        try:
            result = tool.function(**arguments)
            if isinstance(result, dict):
                return {"ok": True, **result}
            return {"ok": True, "result": result}
        except Exception as exc:  # pragma: no cover - defensive guard
            return {"ok": False, "error": str(exc)}

    def names(self) -> list[str]:
        return sorted(self.tools.keys())
