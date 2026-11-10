# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.pictureX_0611_Industrial_rolling_work_table import _local_origin
from sdk import ArticulatedObject, Box, Origin


def test_local_origin_keeps_true_part_visual_material_class_id() -> None:
    model = ArticulatedObject(name="local_origin_direct_visual")
    part = model.part("host")

    part.visual(
        Box((0.1, 0.2, 0.3)),
        origin=_local_origin(
            Origin(xyz=(1.5, 2.25, 3.75)),
            (1.0, 2.0, 3.0),
        ),
        material="steel",
        name="panel",
        material_class_id="metal.stainless_matte",
    )

    visual = part.visuals[0]
    assert visual.origin.xyz == (0.5, 0.25, 0.75)
    assert visual.material_class_id == "metal.stainless_matte"
