# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from articraft.appearance import (
    GENERATOR_CLASS_ANNOTATION_POLICY,
    GENERATOR_CLASS_PROPOSALS_SCHEMA,
)
from articraft.appearance.pool_runtime import (
    POINTER_SCHEMA,
    POOL_INDEX_SCHEMA,
)
from scripts import build_generator_material_class_annotations as target


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _formal_library(tmp_path: Path) -> Path:
    library = tmp_path / "library"
    logical_sha = "1" * 64
    snapshot = library / "snapshots" / logical_sha
    manifest = snapshot / "manifest.json"
    pool_index = snapshot / "pools" / "index.json"
    physics_index = snapshot / "physics" / "index.json"
    _write_json(manifest, {"logical_snapshot_sha256": logical_sha})
    _write_json(
        pool_index,
        {
            "schema_version": POOL_INDEX_SCHEMA,
            "logical_snapshot_sha256": logical_sha,
            "material_count": 3,
            "class_count": 2,
            "nonempty_class_count": 2,
            "empty_class_count": 0,
            "pools": [
                {
                    "material_class_id": "plastic.opaque_generic",
                    "material_count": 1,
                },
                {
                    "material_class_id": "wood.natural_generic",
                    "material_count": 2,
                },
            ],
        },
    )
    _write_json(physics_index, {"material_count": 3})
    pointer = library / "latest.json"
    _write_json(
        pointer,
        {
            "schema_version": POINTER_SCHEMA,
            "logical_snapshot_sha256": logical_sha,
            "snapshot_path": f"snapshots/{logical_sha}",
            "manifest_path": f"snapshots/{logical_sha}/manifest.json",
            "manifest_sha256": _sha(manifest),
            "pool_index_path": f"snapshots/{logical_sha}/pools/index.json",
            "pool_index_sha256": _sha(pool_index),
            "physics_index_path": f"snapshots/{logical_sha}/physics/index.json",
            "physics_index_sha256": _sha(physics_index),
        },
    )
    return pointer


def _template(tmp_path: Path) -> Path:
    path = tmp_path / "fixture.py"
    path.write_text(
        """\
def build(model, r, color):
    part = model.part("body")
    part.visual(object(), name="body")
    part.visual(object(), name=f"marker_{r.kind}", material=color)
""",
        encoding="utf-8",
    )
    return path


def _proposals(template: Path, library_sha: str) -> dict:
    source_sha, callsites = target.inventory_visual_callsites(template)
    by_name = {name: callsite_id for callsite_id, name in callsites.items()}
    return {
        "schema_version": GENERATOR_CLASS_PROPOSALS_SCHEMA,
        "policy_version": GENERATOR_CLASS_ANNOTATION_POLICY,
        "library_snapshot_sha256": library_sha,
        "template_slug": "fixture",
        "template_source_sha256": source_sha,
        "callsites": [
            {
                "callsite_id": by_name["body"],
                "visual_name": "body",
                "decision": "material_class",
                "config_expression": "r.kind",
                "config_domain": ["wood", "plastic"],
                "proposals": [
                    {
                        "config_values": ["wood"],
                        "material_class_id": "wood.natural_generic",
                        "priority": 100,
                        "rationale": "explicit wood branch",
                    },
                    {
                        "config_values": ["plastic"],
                        "material_class_id": "plastic.opaque_generic",
                        "priority": 90,
                        "rationale": "explicit plastic branch",
                    },
                ],
            },
            {
                "callsite_id": by_name["f'marker_{r.kind}'"],
                "visual_name": "f'marker_{r.kind}'",
                "decision": "flat_color",
            },
        ],
    }


def test_build_and_validate_bind_v3_library_source_and_all_callsites(tmp_path: Path) -> None:
    library = _formal_library(tmp_path)
    template = _template(tmp_path)
    logical_sha, class_ids = target.load_formal_class_ids(library)
    assert logical_sha == "1" * 64
    assert class_ids == {"wood.natural_generic", "plastic.opaque_generic"}

    proposals_path = tmp_path / "proposals.json"
    output_path = tmp_path / "annotations.json"
    _write_json(proposals_path, _proposals(template, logical_sha))

    built = target.build_file(
        proposals_path=proposals_path,
        template_path=template,
        library_path=library,
        output_path=output_path,
    )
    validated = target.validate_file(
        annotations_path=output_path,
        template_path=template,
        library_path=library,
    )

    assert built == validated
    assert len(built["callsites"]) == 2
    assert output_path.is_file()


def test_cli_contract_rejects_old_library_and_stale_or_incomplete_input(tmp_path: Path) -> None:
    library = _formal_library(tmp_path)
    template = _template(tmp_path)
    pointer = json.loads(library.read_text(encoding="utf-8"))
    pointer["schema_version"] = "articraft-pbr-material-library-pointer/v1"
    _write_json(library, pointer)
    with pytest.raises(ValueError, match="unified material-physics"):
        target.load_formal_class_ids(library)

    library = _formal_library(tmp_path)
    logical_sha, _ = target.load_formal_class_ids(library)
    proposals = _proposals(template, logical_sha)
    proposals["callsites"].pop()
    proposals_path = tmp_path / "incomplete.json"
    _write_json(proposals_path, proposals)
    with pytest.raises(ValueError, match="callsite coverage mismatch"):
        target.build_file(
            proposals_path=proposals_path,
            template_path=template,
            library_path=library,
            output_path=tmp_path / "unused.json",
        )
