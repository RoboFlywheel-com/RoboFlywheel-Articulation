---
title: 'Squirrel-Cage Blower Wheel'
description: 'Base SDK example showing a radial blower wheel with exposed vane passages and an open inner cavity using BlowerWheelGeometry.'
tags:
  - sdk
  - base sdk
  - blower
  - blower wheel
  - squirrel cage
  - radial fan
  - hvac blower
  - blowerwheelgeometry
  - mesh geometry
---
# Squirrel-Cage Blower Wheel

This base-SDK example is a compact reference for `BlowerWheelGeometry`. It is
useful when the object should read as a real radial blower cage with open vane
passages into the inner cavity.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    BlowerWheelGeometry,
    Box,
    Inertial,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

OUTER_RADIUS = 0.080
WIDTH = 0.050


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="squirrel_cage_blower")
    finish = model.material("blower_gray", rgba=(0.62, 0.65, 0.69, 1.0))

    blower_wheel = model.part("blower_wheel")
    blower_wheel.visual(
        mesh_from_geometry(
            BlowerWheelGeometry(
                OUTER_RADIUS,
                0.040,
                WIDTH,
                18,
                blade_thickness=0.004,
                blade_sweep_deg=25.0,
            ),
            "blower_wheel",
        ),
        material=finish,
        name="blower_wheel",
    )
    blower_wheel.inertial = Inertial.from_geometry(Box((0.16, 0.16, WIDTH)), mass=0.22)
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    blower_wheel = object_model.get_part("blower_wheel")
    ctx.check("blower_wheel_present", blower_wheel is not None, "Expected a blower_wheel part.")
    if blower_wheel is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(blower_wheel)
    ctx.check("blower_wheel_aabb_present", aabb is not None, "Expected a world AABB for the blower wheel.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    diameter = max(size[0], size[1])
    ctx.check("blower_wheel_diameter", abs(diameter - OUTER_RADIUS * 2.0) <= 0.008, f"size={size!r}")
    ctx.check("blower_wheel_width", abs(size[2] - WIDTH) <= 0.004, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
