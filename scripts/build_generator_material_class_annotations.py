#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Build or validate strict max2 generator material-class annotations."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from articraft.appearance.generator_annotations import (
    GENERATOR_CLASS_ANNOTATION_POLICY,
    build_generator_class_annotations,
    validate_generator_class_annotations,
)
from articraft.appearance.pool_runtime import (
    POINTER_SCHEMA,
    POOL_INDEX_SCHEMA,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = REPO_ROOT / "pbr_material_library" / "latest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _contained(root: Path, value: object, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{field} must be relative")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"{field} escapes the formal material library")
    return resolved


def load_formal_class_ids(pointer_path: Path) -> tuple[str, frozenset[str]]:
    """Read only v3 control files and return the non-empty exact classes."""

    pointer = pointer_path.resolve(strict=True)
    library_root = pointer.parent
    value = _json_object(pointer)
    expected_pointer_fields = {
        "schema_version",
        "logical_snapshot_sha256",
        "snapshot_path",
        "manifest_path",
        "manifest_sha256",
        "pool_index_path",
        "pool_index_sha256",
        "physics_index_path",
        "physics_index_sha256",
    }
    if set(value) != expected_pointer_fields:
        raise ValueError("formal material library pointer fields do not match v3")
    if value.get("schema_version") != POINTER_SCHEMA:
        raise ValueError("only the unified material-physics library v3 is supported")
    logical_sha = value.get("logical_snapshot_sha256")
    if not isinstance(logical_sha, str) or len(logical_sha) != 64:
        raise ValueError("formal material library logical snapshot SHA is invalid")

    snapshot_path = _contained(library_root, value.get("snapshot_path"), field="snapshot_path")
    if snapshot_path.name != logical_sha or not snapshot_path.is_dir():
        raise ValueError("formal material library snapshot identity mismatch")
    manifest_path = _contained(library_root, value.get("manifest_path"), field="manifest_path")
    pool_index_path = _contained(
        library_root,
        value.get("pool_index_path"),
        field="pool_index_path",
    )
    physics_index_path = _contained(
        library_root,
        value.get("physics_index_path"),
        field="physics_index_path",
    )
    if _sha256(manifest_path) != value.get("manifest_sha256"):
        raise ValueError("formal material library manifest SHA mismatch")
    if _sha256(pool_index_path) != value.get("pool_index_sha256"):
        raise ValueError("formal material library pool index SHA mismatch")
    if _sha256(physics_index_path) != value.get("physics_index_sha256"):
        raise ValueError("formal material library physics index SHA mismatch")

    pool_index = _json_object(pool_index_path)
    if pool_index.get("schema_version") != POOL_INDEX_SCHEMA:
        raise ValueError("formal material class pool index must use v3")
    if pool_index.get("logical_snapshot_sha256") != logical_sha:
        raise ValueError("formal material class pool index snapshot mismatch")
    if pool_index.get("empty_class_count") != 0:
        raise ValueError("formal material library must not contain empty classes")
    raw_pools = pool_index.get("pools")
    if not isinstance(raw_pools, list) or not raw_pools:
        raise ValueError("formal material library pool index is empty")
    class_ids: list[str] = []
    for index, raw in enumerate(raw_pools):
        if not isinstance(raw, Mapping):
            raise ValueError(f"pools[{index}] must be an object")
        class_id = raw.get("material_class_id")
        count = raw.get("material_count")
        if not isinstance(class_id, str) or not class_id:
            raise ValueError(f"pools[{index}].material_class_id is invalid")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"formal material pool {class_id!r} must be non-empty")
        class_ids.append(class_id)
    if len(class_ids) != len(set(class_ids)):
        raise ValueError("formal material library repeats a material class")
    if pool_index.get("class_count") != len(class_ids):
        raise ValueError("formal material library class count mismatch")
    if pool_index.get("nonempty_class_count") != len(class_ids):
        raise ValueError("formal material library non-empty class count mismatch")
    return logical_sha, frozenset(class_ids)


def inventory_visual_callsites(template_path: Path) -> tuple[str, dict[str, str]]:
    """Return the source SHA and every static ``.visual()`` callsite."""

    source_path = template_path.resolve(strict=True)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    slug = source_path.stem
    callsites: dict[str, str] = {}
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "visual"
        ):
            continue
        name_keyword = next((item for item in node.keywords if item.arg == "name"), None)
        if name_keyword is None:
            raise ValueError(f"{source_path}:{node.lineno} visual call has no explicit name")
        if isinstance(name_keyword.value, ast.Constant) and isinstance(
            name_keyword.value.value, str
        ):
            visual_name = name_keyword.value.value
        else:
            visual_name = ast.unparse(name_keyword.value)
        callsite_id = f"{slug}:{node.lineno}:{node.col_offset}"
        if callsite_id in callsites:
            raise ValueError(f"duplicate visual callsite ID: {callsite_id}")
        callsites[callsite_id] = visual_name
    if not callsites:
        raise ValueError(f"template has no static visual callsites: {source_path}")
    return hashlib.sha256(source.encode("utf-8")).hexdigest(), callsites


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    destination = path.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    tmp_path = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, destination)
    finally:
        tmp_path.unlink(missing_ok=True)


def build_file(
    *,
    proposals_path: Path,
    template_path: Path,
    library_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    library_sha, class_ids = load_formal_class_ids(library_path)
    source_sha, callsites = inventory_visual_callsites(template_path)
    proposals = _json_object(proposals_path.resolve(strict=True))
    if proposals.get("template_slug") != template_path.stem:
        raise ValueError("proposal template slug does not match --template")
    annotations = build_generator_class_annotations(
        proposals,
        available_material_class_ids=class_ids,
        expected_library_snapshot_sha256=library_sha,
        expected_template_source_sha256=source_sha,
        expected_callsites=callsites,
    )
    _atomic_json(output_path, annotations)
    return annotations


def validate_file(
    *,
    annotations_path: Path,
    template_path: Path,
    library_path: Path,
) -> dict[str, Any]:
    library_sha, class_ids = load_formal_class_ids(library_path)
    source_sha, callsites = inventory_visual_callsites(template_path)
    annotations = _json_object(annotations_path.resolve(strict=True))
    if annotations.get("template_slug") != template_path.stem:
        raise ValueError("annotation template slug does not match --template")
    return validate_generator_class_annotations(
        annotations,
        available_material_class_ids=class_ids,
        expected_library_snapshot_sha256=library_sha,
        expected_template_source_sha256=source_sha,
        expected_callsites=callsites,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build or validate scalar generator material-class annotations. "
            "Each visual is exact for a resolved seed and may span at most two "
            "classes across its explicit Config domain."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="compress strict Qwen proposals to max2")
    build.add_argument("--proposals", type=Path, required=True)
    build.add_argument("--template", type=Path, required=True)
    build.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    build.add_argument("--output", type=Path, required=True)
    validate = subparsers.add_parser("validate", help="validate a final max2 annotation")
    validate.add_argument("--annotations", type=Path, required=True)
    validate.add_argument("--template", type=Path, required=True)
    validate.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "build":
        result = build_file(
            proposals_path=args.proposals,
            template_path=args.template,
            library_path=args.library,
            output_path=args.output,
        )
    else:
        result = validate_file(
            annotations_path=args.annotations,
            template_path=args.template,
            library_path=args.library,
        )
    print(
        json.dumps(
            {
                "schema_version": result["schema_version"],
                "policy_version": GENERATOR_CLASS_ANNOTATION_POLICY,
                "template_slug": result["template_slug"],
                "callsite_count": len(result["callsites"]),
                "status": "valid",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
