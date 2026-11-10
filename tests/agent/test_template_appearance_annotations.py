# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import ast
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "agent" / "templates"


def _visual_calls() -> list[tuple[Path, ast.Call]]:
    rows: list[tuple[Path, ast.Call]] = []
    for path in sorted(TEMPLATE_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        rows.extend(
            (path, node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "visual"
        )
    return rows


def test_full_template_fleet_has_strict_visual_annotation_xor() -> None:
    rows = _visual_calls()
    physical = 0
    appearance_only = 0
    findings: list[str] = []

    for path, node in rows:
        keywords = {keyword.arg: keyword.value for keyword in node.keywords if keyword.arg}
        has_class = "material_class_id" in keywords
        has_appearance = "appearance_only" in keywords
        if has_class == has_appearance:
            findings.append(
                f"{path.name}:{node.lineno}: expected exactly one of "
                "material_class_id or appearance_only"
            )
            continue
        if has_class:
            physical += 1
            class_expression = keywords["material_class_id"]
            if isinstance(class_expression, (ast.List, ast.Tuple, ast.Set)):
                findings.append(f"{path.name}:{node.lineno}: material_class_id must be scalar")
        else:
            appearance_only += 1
            expression = keywords["appearance_only"]
            if not (
                isinstance(expression, ast.Call)
                and isinstance(expression.func, ast.Name)
                and expression.func.id == "AppearanceOnlySpec"
            ):
                findings.append(
                    f"{path.name}:{node.lineno}: appearance_only must construct AppearanceOnlySpec"
                )

    assert not findings, "\n".join(findings)
    assert rows
    assert physical > 0
    assert appearance_only > 0
    assert physical + appearance_only == len(rows)


def test_full_template_fleet_appearance_spec_imports_are_used() -> None:
    findings: list[str] = []
    for path in sorted(TEMPLATE_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "sdk"
            and any(alias.name == "AppearanceOnlySpec" for alias in node.names)
            for node in tree.body
        )
        used = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "AppearanceOnlySpec"
            for node in ast.walk(tree)
        )
        if imported != used:
            findings.append(f"{path.name}: AppearanceOnlySpec imported={imported}, used={used}")

    assert not findings, "\n".join(findings)
