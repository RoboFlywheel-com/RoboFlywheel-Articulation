# SPDX-License-Identifier: Apache-2.0

"""Category-neutral expression runtime shared by templates and validators.

This module deliberately lives outside ``agent.template_validators``.  Runtime
contract helpers are imported while template modules are still loading, so
depending on the validator package here would initialize the complete
validator registry and create an import cycle with runtime multiplicity checks.
"""

from __future__ import annotations

import ast
import math
from typing import Any, Mapping

SAFE_FUNCTIONS = {
    "abs": abs,
    "max": max,
    "min": min,
    "sqrt": math.sqrt,
    "radians": math.radians,
}

_ALLOWED_NODES = (
    ast.Expression,
    ast.Constant,
    ast.Name,
    ast.Load,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.Call,
    ast.IfExp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Pow,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)


def expression_names(expression: str) -> set[str]:
    tree = ast.parse(expression, mode="eval")
    _validate_tree(tree)
    return {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id not in SAFE_FUNCTIONS
    }


def evaluate(expression: str, values: Mapping[str, Any]) -> Any:
    tree = ast.parse(expression, mode="eval")
    _validate_tree(tree)
    missing = sorted(expression_names(expression) - set(values))
    if missing:
        raise ValueError(f"expression references unknown names: {', '.join(missing)}")
    return eval(  # noqa: S307 - AST and globals are strictly whitelisted above
        compile(tree, "<template-dimension-contract>", "eval"),
        {"__builtins__": {}, **SAFE_FUNCTIONS},
        dict(values),
    )


def evaluate_constraint(
    expression: str,
    values: Mapping[str, Any],
    *,
    tolerance: float = 1e-8,
) -> bool:
    """Evaluate a boolean invariant with tolerant inclusive comparisons."""

    tree = ast.parse(expression, mode="eval")
    _validate_tree(tree)
    missing = sorted(expression_names(expression) - set(values))
    if missing:
        raise ValueError(f"expression references unknown names: {', '.join(missing)}")
    if tolerance < 0:
        raise ValueError("constraint tolerance must be non-negative")
    transformed = _InclusiveComparisonTolerance(float(tolerance)).visit(tree)
    ast.fix_missing_locations(transformed)
    return bool(
        eval(  # noqa: S307 - original AST is validated; transformer inserts safe calls
            compile(transformed, "<template-derived-constraint>", "eval"),
            {
                "__builtins__": {},
                **SAFE_FUNCTIONS,
                "__template_ge": _tolerant_ge,
                "__template_le": _tolerant_le,
            },
            dict(values),
        )
    )


def _tolerant_ge(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return float(left) + tolerance >= float(right)
    return bool(left >= right)


def _tolerant_le(left: Any, right: Any, tolerance: float) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return float(left) <= float(right) + tolerance
    return bool(left <= right)


class _InclusiveComparisonTolerance(ast.NodeTransformer):
    def __init__(self, tolerance: float) -> None:
        self._tolerance = tolerance

    def visit_Compare(self, node: ast.Compare) -> ast.expr:  # noqa: N802 - ast API
        node = self.generic_visit(node)
        assert isinstance(node, ast.Compare)
        comparisons: list[ast.expr] = []
        left = node.left
        for operator, right in zip(node.ops, node.comparators, strict=True):
            helper = (
                "__template_ge"
                if isinstance(operator, ast.GtE)
                else "__template_le"
                if isinstance(operator, ast.LtE)
                else None
            )
            if helper is None:
                comparisons.append(ast.Compare(left=left, ops=[operator], comparators=[right]))
            else:
                comparisons.append(
                    ast.Call(
                        func=ast.Name(id=helper, ctx=ast.Load()),
                        args=[left, right, ast.Constant(self._tolerance)],
                        keywords=[],
                    )
                )
            left = right
        if len(comparisons) == 1:
            return comparisons[0]
        return ast.BoolOp(op=ast.And(), values=comparisons)


def _validate_tree(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError(f"unsupported expression syntax: {type(node).__name__}")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in SAFE_FUNCTIONS:
                raise ValueError("only min/max/abs/sqrt/radians calls are allowed")


__all__ = ["SAFE_FUNCTIONS", "evaluate", "evaluate_constraint", "expression_names"]
