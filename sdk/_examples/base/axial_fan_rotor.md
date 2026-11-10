---
title: 'Axial Fan Rotor'
description: 'Base SDK example showing a compact axial rotor with pitched blades and a central hub using FanRotorGeometry.'
tags:
  - sdk
  - base sdk
  - fan
  - axial fan
  - fan rotor
  - impeller
  - cooling fan
  - fanrotorgeometry
  - mesh geometry
---
# Axial Fan Rotor

This base-SDK example is a minimal reference for `FanRotorGeometry`. It is
useful for compact cooling fans, appliance rotors, and any exposed axial
impeller where the blades should read as real geometry rather than embossed
texture.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    FanRotorGeometry,
    Inertial,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

OUTER_RADIUS = 0.070
THICKNESS = 0.010


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="axial_fan_rotor")
    finish = model.material("fan_black", rgba=(0.08, 0.08, 0.09, 1.0))

    fan_rotor = model.part("fan_rotor")
    fan_rotor.visual(
        mesh_from_geometry(
            FanRotorGeometry(
                OUTER_RADIUS,
                0.020,
                5,
                thickness=THICKNESS,
                blade_pitch_deg=24.0,
                blade_sweep_deg=14.0,
            ),
            "fan_rotor",
        ),
        material=finish,
        name="fan_rotor",
    )
    fan_rotor.inertial = Inertial.from_geometry(Box((0.14, 0.14, 0.012)), mass=0.12)
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    fan_rotor = object_model.get_part("fan_rotor")
    ctx.check("fan_rotor_present", fan_rotor is not None, "Expected a fan_rotor part.")
    if fan_rotor is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(fan_rotor)
    ctx.check("fan_rotor_aabb_present", aabb is not None, "Expected a world AABB for the fan rotor.")
    if aabb is None:
        return ctx.report()

    mins, maxs = aabb
    size = tuple(float(maxs[i] - mins[i]) for i in range(3))
    diameter = max(size[0], size[1])
    ctx.check("fan_rotor_diameter", abs(diameter - OUTER_RADIUS * 2.0) <= 0.012, f"size={size!r}")
    ctx.check("fan_rotor_thickness", 0.008 <= size[2] <= 0.014, f"size={size!r}")
    return ctx.report()


object_model = build_object_model()
```
