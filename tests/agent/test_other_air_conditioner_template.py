# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math

from agent.templates.Other_Air_conditioner import (
    _resolve_body_geom,
    build_air_conditioner,
    config_from_seed,
    resolve_config,
)


def test_raked_wedge_service_panel_hinge_uses_sloped_front_face_frame() -> None:
    config = config_from_seed(5)
    resolved = resolve_config(config)
    _, geom = _resolve_body_geom(
        resolved.body_form,
        resolved.body_width_scale,
        resolved.body_height_scale,
        resolved.body_depth_scale,
    )
    model = build_air_conditioner(config)
    hinge = model.get_articulation("front_panel_hinge")

    assert resolved.body_form == "raked_wedge"
    assert resolved.service_panel == "bottom_hinge_drop_front"

    hinge_y, _hinge_z = hinge.origin.xyz[1], hinge.origin.xyz[2]
    surface_y, _surface_z = geom["arc_point"](geom["drop_front_hinge_z"] / geom["body_h"])
    assert hinge_y >= surface_y
    assert math.isclose(hinge.origin.rpy[0], geom["face_normal_angle"], abs_tol=1e-6)


def test_raked_wedge_top_service_panel_hinges_also_follow_sloped_front_face() -> None:
    config = config_from_seed(5)
    resolved = resolve_config(config)
    _, geom = _resolve_body_geom(
        resolved.body_form,
        resolved.body_width_scale,
        resolved.body_height_scale,
        resolved.body_depth_scale,
    )
    top_surface_y, _top_surface_z = geom["arc_point"](geom["top_hinge_z"] / geom["body_h"])

    assert geom["top_hinge_y"] >= top_surface_y
    assert math.isclose(geom["panel_rpy_x"], geom["face_normal_angle"], abs_tol=1e-6)
