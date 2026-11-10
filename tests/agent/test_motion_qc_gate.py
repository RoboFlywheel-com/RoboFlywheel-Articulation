# SPDX-License-Identifier: Apache-2.0

"""Harness-owned motion QC gate (sampled-pose overlap) fault-injection tests.

The model under test is a door on a round hinge post: a knuckle sleeve on the
door captures the post (declared via an element-scoped allow_overlap), and the
panel stays clear of the post while sweeping over the slab. With a wall in the
swing arc the model is clean in the rest pose but penetrates the wall as the
joint opens; the legacy current-pose baseline must accept it, the motion QC
gate must reject it, and the allowance-covered captured-pin contact must stay
legal at every sampled pose.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agent import compiler as compiler_module
from agent.compiler import compile_urdf_report, compile_urdf_report_maybe_timeout


def _write_swinging_door_model_script(script_path: Path, *, with_wall: bool) -> None:
    wall_lines = (
        [
            "base.visual(",
            "    Box((0.4, 0.02, 0.2)),",
            "    origin=Origin(xyz=(0.1, 0.12, 0.1)),",
            "    name='wall',",
            ")",
        ]
        if with_wall
        else []
    )
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "from sdk import (",
                "    ArticulatedObject,",
                "    ArticulationType,",
                "    Box,",
                "    Cylinder,",
                "    MotionLimits,",
                "    Origin,",
                "    TestContext,",
                ")",
                "",
                "object_model = ArticulatedObject(name='swinging_door')",
                "base = object_model.part('base')",
                "base.visual(",
                "    Box((0.5, 0.5, 0.02)),",
                "    origin=Origin(xyz=(0.1, 0.05, -0.01)),",
                "    name='slab',",
                ")",
                "base.visual(",
                "    Cylinder(0.012, 0.2),",
                "    origin=Origin(xyz=(0.0, 0.0, 0.1)),",
                "    name='hinge_post',",
                ")",
                *wall_lines,
                "door = object_model.part('door')",
                "# Knuckle sleeves the post (captured pin, allowance below); the panel",
                "# clears the post by 2mm and its bottom rides flush on the slab plane.",
                "door.visual(",
                "    Cylinder(0.016, 0.04),",
                "    origin=Origin(xyz=(0.0, 0.0, 0.0)),",
                "    name='knuckle',",
                ")",
                "door.visual(",
                "    Box((0.18, 0.02, 0.16)),",
                "    origin=Origin(xyz=(0.104, 0.0, -0.02)),",
                "    name='panel',",
                ")",
                "object_model.articulation(",
                "    'base_to_door',",
                "    ArticulationType.REVOLUTE,",
                "    parent=base,",
                "    child=door,",
                "    axis=(0.0, 0.0, 1.0),",
                "    origin=Origin(xyz=(0.0, 0.0, 0.1)),",
                "    motion_limits=MotionLimits(",
                "        effort=1.0, velocity=1.0, lower=0.0, upper=1.5708",
                "    ),",
                ")",
                "",
                "def run_tests():",
                "    ctx = TestContext(object_model)",
                "    ctx.allow_overlap(",
                "        object_model.get_part('base'),",
                "        object_model.get_part('door'),",
                "        elem_a='hinge_post',",
                "        elem_b='knuckle',",
                "        reason='door knuckle sleeves the hinge post (captured pin)',",
                "    )",
                "    return ctx.report()",
            ]
        ),
        encoding="utf-8",
    )


def test_swept_door_passes_current_pose_baseline_without_motion_qc(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    _write_swinging_door_model_script(script_path, with_wall=True)

    report = compile_urdf_report(script_path, run_checks=True, target="full")

    assert "<robot" in report.urdf_xml


def test_swept_door_fails_motion_qc_gate(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    _write_swinging_door_model_script(script_path, with_wall=True)

    with pytest.raises(RuntimeError, match="harness_motion_qc") as captured:
        compile_urdf_report(script_path, run_checks=True, target="full", motion_qc=True)

    actual = captured.value.motion_qc_report
    assert actual["status"] == "fail"
    assert actual["collision_free"] is False
    assert actual["missing_pose_ids"] == []
    assert actual["missing_edges"] == []


def test_clean_door_with_allowed_captured_pin_passes_motion_qc_gate(tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    _write_swinging_door_model_script(script_path, with_wall=False)

    report = compile_urdf_report(script_path, run_checks=True, target="full", motion_qc=True)

    assert "<robot" in report.urdf_xml
    assert report.motion_qc_report is not None
    assert report.motion_qc_report["status"] == "pass"
    assert report.motion_qc_report["missing_pose_ids"] == []
    assert report.motion_qc_report["missing_edges"] == []
    assert report.motion_qc_report["joints"] == [
        {
            "joint": "base_to_door",
            "joint_type": "revolute",
            "required_edges": ["lower", "upper"],
            "covered_edges": ["lower", "upper"],
        }
    ]


def test_motion_qc_report_survives_timeout_worker_transport(monkeypatch, tmp_path: Path) -> None:
    script_path = tmp_path / "model.py"
    _write_swinging_door_model_script(script_path, with_wall=False)
    monkeypatch.setenv("URDF_COMPILE_TIMEOUT_SECONDS", "30")

    report = compile_urdf_report_maybe_timeout(
        script_path,
        run_checks=True,
        target="full",
        motion_qc=True,
    )

    assert report.motion_qc_report is not None
    assert report.motion_qc_report["status"] == "pass"
    assert report.motion_qc_report["missing_pose_ids"] == []


def test_compiler_owned_motion_qc_uses_generated_script_seed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    script_path = tmp_path / "model.py"
    _write_swinging_door_model_script(script_path, with_wall=False)
    source = script_path.read_text(encoding="utf-8")
    script_path.write_text(
        source.replace(
            "from __future__ import annotations\n",
            "from __future__ import annotations\nSEED = 17\n",
            1,
        ),
        encoding="utf-8",
    )
    captured: dict[str, int] = {}

    def fake_motion_qc(ctx: object, _model: object) -> dict[str, object]:
        captured["seed"] = int(getattr(ctx, "seed"))
        return {
            "schema_version": 2,
            "status": "pass",
            "collision_free": True,
            "required_pose_ids": [],
            "executed_pose_ids": [],
            "missing_pose_ids": [],
            "required_edges": [],
            "covered_edges": [],
            "missing_edges": [],
            "joints": [],
            "required_pose_kind_counts": {},
            "executed_pose_kind_counts": {},
            "poses": [],
        }

    monkeypatch.setattr(compiler_module, "_run_motion_qc_pose_overlap_check", fake_motion_qc)

    compile_urdf_report(script_path, run_checks=True, target="full", motion_qc=True)

    assert captured == {"seed": 17}
