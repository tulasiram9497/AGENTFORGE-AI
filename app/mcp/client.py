from __future__ import annotations

from typing import Any

try:
    from mcp import ClientSession  # type: ignore
except Exception:  # pragma: no cover
    ClientSession = None  # type: ignore


class MockMCPServer:
    def __init__(self):
        self.tools = {
            "mcp_calculator": {
                "description": "Calculator exposed through MCP",
                "input_schema": {"expression": {"type": "string"}},
            },
            "mcp_lookup": {
                "description": "Look up local information across an MCP-backed index",
                "input_schema": {"query": {"type": "string"}},
            },
        }

    def discover_tools(self) -> dict[str, Any]:
        return self.tools

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name == "mcp_calculator":
            return {"ok": True, "result": 7}
        if name == "mcp_lookup":
            return {"ok": True, "hits": [{"text": "MCP evidence says the local context is available."}]}
        return {"ok": False, "error": f"Tool '{name}' is unavailable."}


class MCPClient:
    def __init__(self, server: MockMCPServer | None = None):
        self.server = server or MockMCPServer()
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def discover_tools(self) -> dict[str, Any]:
        return self.server.discover_tools()

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.connected:
            raise RuntimeError("MCP client is not connected")
        return self.server.call_tool(name, arguments)

    def close(self) -> None:
        self.connected = False
