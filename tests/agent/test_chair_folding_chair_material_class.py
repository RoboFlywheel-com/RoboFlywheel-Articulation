# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates import Chair_Folding_chair as target
from sdk import ArticulatedObject, Box


@pytest.mark.parametrize(
    ("frame_style", "expected_material_class_id"),
    [
        ("tubular_steel", "metal.paint_coated"),
        ("wood_side_frame", "wood.natural_generic"),
    ],
)
def test_cross_bar_material_class_uses_frame_config_not_radius_parameter(
    monkeypatch: pytest.MonkeyPatch,
    frame_style: str,
    expected_material_class_id: str,
) -> None:
    resolved = target.resolve_config(target.FoldingChairConfig(frame_style=frame_style))
    kit = target._FrameKit(resolved)
    model = ArticulatedObject(name="folding_chair_cross_bar")
    material = model.material("frame", rgba=(0.2, 0.2, 0.2, 1.0))
    part = model.part("rear_frame")
    monkeypatch.setattr(target, "_cross_tube", lambda *args: Box((0.1, 0.2, 0.1)))

    kit.cross_bar(
        part,
        x=0.0,
        z=0.4,
        half_w=0.2,
        r=resolved.tube_r,
        material=material,
        name="back_rail_top",
    )

    assert part.visuals[0].material_class_id == expected_material_class_id
