---
title: 'Wall Vent with Register Grille'
description: 'Base SDK example showing a wall vent with a true open grille shell, angled slats, shallow rear sleeve, and visible mounting screws using VentGrilleGeometry.'
tags:
  - sdk
  - base sdk
  - wall vent
  - vent grille
  - register
  - hvac vent
  - grille
  - slotted face
  - ventgrillegeometry
  - mesh geometry
---
# Wall Vent with Register Grille

This base-SDK example is a clean reference for `VentGrilleGeometry` used as a
full vent shell rather than a decorative face plate. It keeps the grille open,
adds a shallow rear sleeve, and layers in simple mounting screws.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    Cylinder,
    Inertial,
    Origin,
    TestContext,
    TestReport,
    VentGrilleGeometry,
    mesh_from_geometry,
)

WIDTH = 0.18
HEIGHT = 0.10
FACE_THICKNESS = 0.004
DUCT_DEPTH = 0.026
SCREW_RADIUS = 0.002
SCREW_LENGTH = 0.002
SCREW_OFFSET_X = WIDTH / 2.0 - 0.006
SCREW_OFFSET_Y = HEIGHT / 2.0 - 0.006
TOTAL_DEPTH = 0.032


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(name="wall_vent")

    plastic_white = model.material("plastic_white", color=(0.9, 0.9, 0.9))
    metal_silver = model.material("metal_silver", color=(0.7, 0.7, 0.7))

    vent_body = model.part("vent_body")
    vent_body.visual(
        mesh_from_geometry(
            VentGrilleGeometry(
                (WIDTH, HEIGHT),
                frame=0.012,
                face_thickness=FACE_THICKNESS,
                duct_depth=DUCT_DEPTH,
                duct_wall=0.003,
                slat_pitch=0.018,
                slat_width=0.009,
                slat_angle_deg=35.0,
                corner_radius=0.006,
            ),
            "vent_shell",
        ),
        origin=Origin(),
        material=plastic_white,
        name="vent_shell",
    )

    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
        vent_body.visual(
            Cylinder(radius=SCREW_RADIUS, length=SCREW_LENGTH),
            origin=Origin(xyz=(sx * SCREW_OFFSET_X, sy * SCREW_OFFSET_Y, 0.004)),
            material=metal_silver,
            name=f"screw_{i}",
        )

    vent_body.inertial = Inertial.from_geometry(
        Box((WIDTH, HEIGHT, TOTAL_DEPTH)),
        mass=0.20,
        origin=Origin(xyz=(0.0, 0.0, -0.011)),
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    vent_body = object_model.get_part("vent_body")
    ctx.check("vent_body_present", vent_body is not None, "Expected a vent_body part.")
    if vent_body is None:
        return ctx.report()

    aabb = ctx.part_world_aabb(vent_body)
    ctx.check("vent_aabb_present", aabb is not None, "Expected a world AABB for the vent.")
    if aabb is None:
        return ctx.report()

    min_pt, max_pt = aabb
    dx = float(max_pt[0] - min_pt[0])
    dy = float(max_pt[1] - min_pt[1])
    dz = float(max_pt[2] - min_pt[2])
    ctx.check("vent_width_matches", abs(dx - WIDTH) < 0.001, details=f"width={dx}")
    ctx.check("vent_height_matches", abs(dy - HEIGHT) < 0.001, details=f"height={dy}")
    ctx.check("vent_depth_matches", abs(dz - TOTAL_DEPTH) < 0.004, details=f"depth={dz}")
    return ctx.report()


object_model = build_object_model()
```
