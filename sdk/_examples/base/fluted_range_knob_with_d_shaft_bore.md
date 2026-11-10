---
title: 'Fluted Range Knob with D-Shaft Bore'
description: 'Base SDK example showing a skirted appliance knob with fluted grip detail, engraved pointer line, and a D-shaft bore using KnobGeometry.'
tags:
  - sdk
  - base sdk
  - knob
  - range knob
  - appliance knob
  - fluted knob
  - skirted knob
  - d shaft
  - control knob
  - mesh geometry
---
# Fluted Range Knob with D-Shaft Bore

This base-SDK example is a compact reference for `KnobGeometry` with the most
common real-world detail stack: skirt, fluted side grip, engraved indicator,
and D-shaft bore. It is useful for queries such as `range knob`, `appliance knob`,
`fluted knob`, `KnobGeometry`, and `D-shaft`.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    Inertial,
    KnobBore,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

SKIRT_DIAMETER = 0.052
TOTAL_HEIGHT = 0.030


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="fluted_range_knob")
    finish = model.material("range_knob_black", rgba=(0.12, 0.12, 0.13, 1.0))

    knob = model.part("knob")
    knob.visual(
        mesh_from_geometry(
            KnobGeometry(
                0.042,
                0.024,
                body_style="skirted",
                top_diameter=0.034,
                skirt=KnobSkirt(SKIRT_DIAMETER, 0.006, flare=0.08),
                grip=KnobGrip(style="fluted", count=18, depth=0.0014),
                indicator=KnobIndicator(
                    style="line",
                    mode="engraved",
                    depth=0.0008,
                    angle_deg=18.0,
                ),
                bore=KnobBore(style="d_shaft", diameter=0.006, flat_depth=0.001),
            ),
            "fluted_range_knob",
        ),
        material=finish,
        name="knob_shell",
    )
    knob.inertial = Inertial.from_geometry(
        Box((SKIRT_DIAMETER, SKIRT_DIAMETER, TOTAL_HEIGHT)),
        mass=0.10,
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    knob = object_model.get_part("knob")
    ctx.check("knob_part_present", knob is not None, "Expected a knob part.")
    if knob is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(knob)
    ctx.check("knob_aabb_present", aabb is not None, "Expected a world AABB for the knob.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    ctx.check("knob_diameter", 0.048 <= max(size[0], size[1]) <= 0.056, f"size={size!r}")
    ctx.check("knob_height", 0.027 <= size[2] <= 0.033, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
