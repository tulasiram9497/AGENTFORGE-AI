from __future__ import annotations

import ast
import operator
from typing import Any

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported calculator expression: {ast.dump(node)}")


def calculator_tool(expression: str) -> dict[str, Any]:
    if not isinstance(expression, str):
        raise ValueError("Expression must be a string")
    if not expression.strip():
        raise ValueError("Expression cannot be empty")
    tree = ast.parse(expression, mode="eval")
    result = _safe_eval(tree.body)
    return {"ok": True, "result": result, "metadata": {"expression": expression}}
