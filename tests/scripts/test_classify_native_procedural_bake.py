# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import _bpy_native_bake_scan_worker as worker
from scripts import classify_native_procedural_bake as target


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _catalog(
    root: Path,
    *,
    material_ids: tuple[str, ...] = ("native-a", "native-b"),
) -> tuple[Path, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for material_id in material_ids:
        package = root / "packages" / "metal" / material_id / "material.blend"
        package.parent.mkdir(parents=True, exist_ok=True)
        package.write_bytes(f"blend:{material_id}".encode())
        rows.append(
            {
                "material_id": material_id,
                "display_name": material_id,
                "category_slug": "metal",
                "material_profile": "native_procedural",
                "normalized_blend_path": package.relative_to(root).as_posix(),
                "sha256": _sha256(package),
                "texture_size_m": 1.0,
                "node_qa": {"status": "pass"},
                "displacement_policy": {"source_output_link_count": 0},
                "optical_policy": None,
            }
        )
    catalog = root / "catalogs" / ("a" * 64) / "materials.jsonl"
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    return catalog, rows


def _job(**updates: object) -> dict[str, object]:
    row: dict[str, object] = {
        "node_qa_status": "pass",
        "texture_size_m": 1.0,
        "source_true_displacement_link_count": 0,
        "optical_policy_present": False,
        "source_animated": False,
    }
    row.update(updates)
    return row


def _evidence(**updates: object) -> dict[str, object]:
    row: dict[str, object] = {
        "active_output_count": 1,
        "connected_surface_output_count": 1,
        "surface_terminal_types": ["BSDF_PRINCIPLED"],
        "principled_terminal_count": 1,
        "linked_node_types": ["BSDF_PRINCIPLED", "TEX_IMAGE"],
        "procedural_texture_node_count": 0,
        "image_texture_count": 1,
        "unpacked_image_count": 0,
        "nonflat_image_projection_count": 0,
        "nonrepeat_image_extension_count": 0,
        "unsupported_image_source_count": 0,
        "coordinate_sources": ["image_unlinked"],
        "unsupported_principled_inputs": [],
        "volume_link_count": 0,
        "displacement_link_count": 0,
        "has_animation_or_drivers": False,
    }
    row.update(updates)
    return row


@pytest.mark.parametrize(
    ("evidence", "expected_reason"),
    (
        (
            _evidence(
                linked_node_types=["BSDF_PRINCIPLED", "TEX_NOISE"],
                procedural_texture_node_count=1,
                image_texture_count=0,
                coordinate_sources=["uv"],
            ),
            "procedural_texture_not_proven_periodic",
        ),
        (
            _evidence(coordinate_sources=["texture_coordinate:object"]),
            "non_uv_coordinate_dependency",
        ),
        (
            _evidence(linked_node_types=["BSDF_PRINCIPLED", "GEOMETRY"]),
            "component_dependent_node",
        ),
        (
            _evidence(unsupported_principled_inputs=["Coat Weight"]),
            "nonstandard_principled_lobe",
        ),
        (
            _evidence(unsupported_principled_inputs=["IOR:linked"]),
            "nonstandard_principled_lobe",
        ),
        (
            _evidence(nonrepeat_image_extension_count=1),
            "image_extension_not_repeat",
        ),
        (
            _evidence(unsupported_image_source_count=1),
            "image_source_not_static_file_or_tiled",
        ),
        (
            _evidence(has_animation_or_drivers=True),
            "animated_or_driven_graph",
        ),
        (
            _evidence(linked_node_types=["BSDF_PRINCIPLED", "NEW_GEOMETRY"]),
            "component_dependent_node",
        ),
        (
            _evidence(unsupported_principled_inputs=["IOR:linked"]),
            "nonstandard_principled_lobe",
        ),
        (
            _evidence(nonrepeat_image_extension_count=1),
            "image_extension_not_repeat",
        ),
        (
            _evidence(unsupported_image_source_count=1),
            "image_source_not_static_file_or_tiled",
        ),
    ),
)
def test_non_reusable_graphs_are_never_safe(
    evidence: dict[str, object], expected_reason: str
) -> None:
    decision, reasons = worker.classify_evidence(_job(), evidence)

    assert decision == "component_bake_only"
    assert expected_reason in reasons


def test_image_only_and_constant_standard_pbr_are_reusable() -> None:
    image_decision, _ = worker.classify_evidence(_job(), _evidence())
    constant_decision, _ = worker.classify_evidence(
        _job(),
        _evidence(
            linked_node_types=["BSDF_PRINCIPLED"],
            image_texture_count=0,
            coordinate_sources=[],
        ),
    )

    assert image_decision == target.SAFE_DECISION
    assert constant_decision == target.SAFE_DECISION


@pytest.mark.parametrize(
    ("job", "evidence", "reason"),
    (
        (_job(optical_policy_present=True), _evidence(), "optical_material"),
        (
            _job(),
            _evidence(
                linked_node_types=["BSDF_GLASS"],
                surface_terminal_types=["BSDF_GLASS"],
                principled_terminal_count=0,
            ),
            "irreducible_surface_closure",
        ),
        (
            _job(),
            _evidence(unsupported_principled_inputs=["Transmission Weight"]),
            "transmissive_surface",
        ),
    ),
)
def test_optical_and_view_dependent_graphs_stay_native(
    job: dict[str, object], evidence: dict[str, object], reason: str
) -> None:
    decision, reasons = worker.classify_evidence(job, evidence)

    assert decision == "keep_native"
    assert reason in reasons


def test_source_displacement_qa_and_tile_size_are_hard_safe_exclusions() -> None:
    decision, reasons = worker.classify_evidence(
        _job(
            node_qa_status="warn",
            texture_size_m=None,
            source_true_displacement_link_count=1,
            source_animated=True,
        ),
        _evidence(),
    )

    assert decision == "component_bake_only"
    assert {
        "normalized_node_qa_not_pass",
        "texture_size_m_missing",
        "source_true_displacement",
        "source_declared_animated",
    }.issubset(reasons)


def test_provider_declared_animation_is_not_reusable() -> None:
    decision, reasons = worker.classify_evidence(
        _job(source_animated=True),
        _evidence(),
    )

    assert decision == "component_bake_only"
    assert "source_declared_animated" in reasons


def test_load_native_jobs_freezes_catalog_and_package_hashes_without_absolute_path(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "one" / "normalized"
    second_root = tmp_path / "two" / "normalized"
    first_catalog, _ = _catalog(first_root, material_ids=("native-a",))
    second_catalog, _ = _catalog(second_root, material_ids=("native-a",))

    first_catalog_sha, first_jobs = target.load_native_jobs(first_catalog, first_root)
    second_catalog_sha, second_jobs = target.load_native_jobs(second_catalog, second_root)

    assert first_catalog_sha == second_catalog_sha
    assert first_jobs[0]["package_sha256"] == second_jobs[0]["package_sha256"]
    assert first_jobs[0]["input_sha256"] == second_jobs[0]["input_sha256"]
    assert first_jobs[0]["package_path"] != second_jobs[0]["package_path"]


def test_load_native_jobs_rejects_package_hash_mismatch(tmp_path: Path) -> None:
    root = tmp_path / "normalized"
    catalog, rows = _catalog(root, material_ids=("native-a",))
    rows[0]["sha256"] = "0" * 64
    catalog.write_text(json.dumps(rows[0], sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="package SHA mismatch"):
        target.load_native_jobs(catalog, root)


def _fake_result(job: dict[str, object], decision: str) -> dict[str, object]:
    return {
        "schema_version": target.RESULT_SCHEMA,
        "classifier_version": target.CLASSIFIER_VERSION,
        "material_id": job["material_id"],
        "catalog_sha256": job["catalog_sha256"],
        "package_sha256": job["package_sha256"],
        "input_sha256": job["input_sha256"],
        "decision": decision,
        "reason_codes": ["test"],
        "evidence": {},
    }


def test_classify_resume_only_scans_missing_jobs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "normalized"
    catalog, _ = _catalog(root, material_ids=("native-a", "native-b"))
    _, first_jobs = target.load_native_jobs(catalog, root)
    output = root / "reports" / "resume"

    monkeypatch.setattr(
        target,
        "_run_worker_batch",
        lambda rows, **_kwargs: [_fake_result(row, target.SAFE_DECISION) for row in rows],
    )
    target.classify(
        first_jobs[:1],
        output_dir=output,
        bpy_python=Path(__file__),
        worker=Path(__file__),
        workers=1,
        batch_size=10,
        timeout_seconds=1,
        resume=False,
    )
    observed_batches: list[list[str]] = []

    def resume_worker(rows: list[dict[str, object]], **_kwargs: object) -> list[dict[str, object]]:
        observed_batches.append([str(row["material_id"]) for row in rows])
        return [_fake_result(row, "component_bake_only") for row in rows]

    monkeypatch.setattr(target, "_run_worker_batch", resume_worker)
    results = target.classify(
        first_jobs,
        output_dir=output,
        bpy_python=Path(__file__),
        worker=Path(__file__),
        workers=1,
        batch_size=10,
        timeout_seconds=1,
        resume=True,
    )

    assert observed_batches == [["native-b"]]
    assert [row["decision"] for row in results] == [
        target.SAFE_DECISION,
        "component_bake_only",
    ]


def test_dry_run_writes_nothing_and_execute_publishes_safe_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "normalized"
    catalog, _ = _catalog(root)

    assert target.main(["--catalog", str(catalog), "--library-root", str(root)]) == 0
    dry_run = json.loads(capsys.readouterr().out)
    assert dry_run["mode"] == "dry_run"
    assert dry_run["writes_catalog_or_packages"] is False
    assert not (root / "reports").exists()

    def fake_worker(rows: list[dict[str, object]], **_kwargs: object) -> list[dict[str, object]]:
        return [
            _fake_result(
                row,
                target.SAFE_DECISION if row["material_id"] == "native-a" else "keep_native",
            )
            for row in rows
        ]

    monkeypatch.setattr(target, "_run_worker_batch", fake_worker)
    assert (
        target.main(
            [
                "--catalog",
                str(catalog),
                "--library-root",
                str(root),
                "--bpy-python",
                str(Path(__file__)),
                "--worker",
                str(Path(__file__)),
                "--execute",
            ]
        )
        == 0
    )
    summary = json.loads(capsys.readouterr().out)
    output = root / summary["output_dir"]
    safe_rows = [
        json.loads(line) for line in (output / "safe_materials.jsonl").read_text().splitlines()
    ]

    assert summary["safe_count"] == 1
    assert summary["safe_material_ids"] == ["native-a"]
    assert "excluded_material_ids" not in summary
    assert "decision_counts" not in summary
    assert [row["material_id"] for row in safe_rows] == ["native-a"]
    assert len((output / "scan_results.jsonl").read_text().splitlines()) == 2
