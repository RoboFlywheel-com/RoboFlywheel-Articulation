# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.ferris_wheel import (
    CABIN_PALETTES,
    DEFAULT_WHEEL_HALF_WIDTH,
    FRAME_PALETTES,
    GLASS_TINTS,
    GONDOLA_PALETTES,
    LEVELING_ARM_LENGTH,
    SCALE_MODE_SEED_RANGES,
    SEED_RIM_RADIUS_MAX,
    SEED_RIM_RADIUS_MIN,
    FerrisWheelConfig,
    build_ferris_wheel,
    config_from_seed,
    gondola_collision_profile,
    hub_geometry,
    resolve_config,
    run_ferris_wheel_tests,
    support_scale_for_radius,
)


def test_config_requires_minimum_gondola_count() -> None:
    with pytest.raises(ValueError, match="must be at least 4"):
        resolve_config(FerrisWheelConfig(num_gondolas=3, spoke_count=6))


def test_odd_gondola_count_is_supported() -> None:
    resolved = resolve_config(
        FerrisWheelConfig(num_gondolas=7, spoke_count=14, gondola_style="open_basket")
    )
    model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=7, spoke_count=14, gondola_style="open_basket")
    )

    assert resolved.num_gondolas == 7
    gondola_parts = [part for part in model.parts if part.name.startswith("gondola_")]
    assert len(gondola_parts) == 7
    assert model.get_articulation("gondola_pivot_7") is not None


def test_seed_config_can_pick_odd_gondola_counts() -> None:
    odd_counts = {config_from_seed(seed).num_gondolas for seed in range(200)}
    assert any(count % 2 == 1 for count in odd_counts)


def test_config_requires_enough_spokes() -> None:
    with pytest.raises(ValueError, match="spoke_count"):
        resolve_config(FerrisWheelConfig(num_gondolas=12, spoke_count=10))


def test_between_rims_hanger_requires_twin_ring_rim() -> None:
    with pytest.raises(ValueError, match="between_rims"):
        resolve_config(FerrisWheelConfig(hanger_style="between_rims", rim_style="single_torus"))


def test_railing_enabled_must_be_bool() -> None:
    with pytest.raises(ValueError, match="railing_enabled"):
        resolve_config(FerrisWheelConfig(railing_enabled=1))  # type: ignore[arg-type]


def test_dense_config_auto_scales_radius_and_axle_height() -> None:
    resolved = resolve_config(
        FerrisWheelConfig(
            num_gondolas=20,
            spoke_count=40,
            gondola_style="glass_capsule",
            rim_radius=None,
            inner_rim_radius=None,
            axle_z=None,
        )
    )

    assert resolved.rim_radius > 0.78
    assert resolved.inner_rim_radius == pytest.approx(resolved.rim_radius * 0.74)
    assert resolved.axle_z > resolved.rim_radius + 0.40


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(42) == config_from_seed(42)
    assert config_from_seed(42) != config_from_seed(43)


def test_seed_config_randomizes_rim_radius_in_range() -> None:
    configs = [config_from_seed(seed) for seed in range(200)]
    rim_radii = [config.rim_radius for config in configs]
    wheel_half_widths = [config.wheel_half_width for config in configs]

    assert all(config.rim_radius is not None for config in configs)
    for config in configs:
        mode_min, mode_max = SCALE_MODE_SEED_RANGES[config.scale_mode]
        assert mode_min <= config.rim_radius <= mode_max
    assert len(set(rim_radii)) > 20
    assert min(rim_radii) < SEED_RIM_RADIUS_MIN
    assert max(rim_radii) > SEED_RIM_RADIUS_MAX
    assert len(set(config.scale_mode for config in configs)) == 3
    assert min(wheel_half_widths) < 0.095
    assert max(wheel_half_widths) > 0.125


def test_seed_rim_radius_respects_collision_floor() -> None:
    sparse_config = FerrisWheelConfig(num_gondolas=4, spoke_count=8, rim_radius=0.95)
    dense_config = FerrisWheelConfig(
        num_gondolas=20,
        spoke_count=40,
        gondola_style="glass_capsule",
        rim_radius=0.80,
    )

    sparse_resolved = resolve_config(sparse_config)
    dense_resolved = resolve_config(dense_config)

    assert sparse_resolved.rim_radius == pytest.approx(0.95)
    assert dense_resolved.rim_radius > 0.80


def test_scale_mode_changes_auto_radius_floor() -> None:
    compact = resolve_config(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="box_cabin",
            scale_mode="compact",
            rim_radius=None,
        )
    )
    normal = resolve_config(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="box_cabin",
            scale_mode="normal",
            rim_radius=None,
        )
    )
    landmark = resolve_config(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="box_cabin",
            scale_mode="landmark",
            rim_radius=None,
        )
    )

    assert compact.rim_radius < normal.rim_radius < landmark.rim_radius


def test_scale_mode_does_not_override_explicit_radius() -> None:
    resolved = resolve_config(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            scale_mode="landmark",
            rim_radius=0.92,
        )
    )
    assert resolved.rim_radius == pytest.approx(0.92)


def test_hub_geometry_stays_within_wheel_width() -> None:
    for wheel_half_width in (0.095, DEFAULT_WHEEL_HALF_WIDTH, 0.125):
        hub_length, hub_cap_x, hub_cap_radius, _central_hub_radius = hub_geometry(wheel_half_width)
        assert hub_length <= 2.0 * wheel_half_width + 1e-6
        assert hub_cap_x <= wheel_half_width + 1e-6
        assert hub_cap_x + hub_cap_radius * 0.25 <= wheel_half_width + 0.015


def test_gondola_collision_profiles_differ_by_style() -> None:
    box = gondola_collision_profile("box_cabin")
    basket = gondola_collision_profile("open_basket")
    capsule = gondola_collision_profile("glass_capsule")
    bucket = gondola_collision_profile("bucket_seat")
    pod = gondola_collision_profile("rounded_pod")

    assert basket.width_y >= box.width_y
    assert capsule.lowest_point_below_pivot < box.lowest_point_below_pivot
    assert bucket.lowest_point_below_pivot > basket.lowest_point_below_pivot
    assert pod.width_y >= box.width_y


def test_support_and_rim_styles_change_geometry() -> None:
    base = FerrisWheelConfig(num_gondolas=8, spoke_count=16, gondola_style="open_basket")
    a_frame = build_ferris_wheel(base)
    truss = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="open_basket",
            support_style="truss_tower",
        )
    )
    single_rim = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="open_basket",
            rim_style="single_torus",
        )
    )
    inclined = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="open_basket",
            support_style="inclined_legs",
        )
    )
    twin_rings = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            gondola_style="open_basket",
            rim_style="twin_rings",
        )
    )

    assert "left_front_a_leg" in {
        visual.name for visual in a_frame.get_part("support_frame").visuals
    }
    assert "left_center_tower_post" in {
        visual.name for visual in truss.get_part("support_frame").visuals
    }
    assert "left_front_inclined_leg" in {
        visual.name for visual in inclined.get_part("support_frame").visuals
    }
    wheel_visuals = {visual.name for visual in single_rim.get_part("wheel").visuals}
    assert "left_outer_rim" in wheel_visuals
    assert "left_inner_rim" not in wheel_visuals
    twin_visuals = {visual.name for visual in twin_rings.get_part("wheel").visuals}
    assert any(name.startswith("left_outer_rim_segment_") for name in twin_visuals)
    # rim cross-bridges were removed from the gondola swing corridor (they
    # collided with cabin floors); twin rims are now tied through the hangers.
    assert not any(name.startswith("rim_bridge_") for name in twin_visuals)
    assert any(name.startswith("left_inner_rim_segment_") for name in twin_visuals)


def test_base_styles_change_geometry() -> None:
    base = build_ferris_wheel(
        FerrisWheelConfig(base_style="platform", num_gondolas=8, spoke_count=16)
    )
    visuals = {v.name for v in base.get_part("support_frame").visuals}
    assert "platform_slab" in visuals
    assert "front_curbstone" in visuals
    assert "rear_curbstone" in visuals


def test_railing_enabled_controls_rail_geometry() -> None:
    with_rails = build_ferris_wheel(
        FerrisWheelConfig(
            base_style="platform",
            railing_enabled=True,
            num_gondolas=8,
            spoke_count=16,
        )
    )
    without_rails = build_ferris_wheel(
        FerrisWheelConfig(
            base_style="platform",
            railing_enabled=False,
            num_gondolas=8,
            spoke_count=16,
        )
    )
    with_names = {v.name for v in with_rails.get_part("support_frame").visuals}
    without_names = {v.name for v in without_rails.get_part("support_frame").visuals}
    assert any(name.startswith("rail_post_") for name in with_names)
    assert not any(name.startswith("rail_post_") for name in without_names)


def test_hanger_style_and_motion_mode_contracts() -> None:
    yoke = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            rim_style="twin_rings",
            hanger_style="yoke_fork",
            gondola_motion_mode="free_swing",
        )
    )
    between = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            rim_style="twin_rings",
            hanger_style="between_rims",
            gondola_motion_mode="counter_rotate_mimic",
        )
    )
    yoke_wheel_visuals = {v.name for v in yoke.get_part("wheel").visuals}
    between_wheel_visuals = {v.name for v in between.get_part("wheel").visuals}
    assert "rear_fork_cheek_1" in yoke_wheel_visuals
    assert "gondola_pivot_bar_1" in yoke_wheel_visuals
    # between_rims hangers are boss+strut pairs (the old single hanger bridge
    # swept the cabins); counter_rotate_mimic is gated OFF for twin_rings, so
    # this combo resolves to free_swing with solver-derived limits.
    assert "front_hanger_boss_1" in between_wheel_visuals
    assert "front_hanger_strut_1" in between_wheel_visuals

    between_joint = between.get_articulation("gondola_pivot_1")
    assert between_joint.mimic is None  # twin_rings forces free_swing
    counter = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_motion_mode="counter_rotate_mimic")
    )
    counter_joint = counter.get_articulation("gondola_pivot_1")
    assert counter_joint.mimic is not None
    assert counter_joint.mimic.joint == "wheel_rotation"
    assert counter_joint.mimic.multiplier == pytest.approx(-1.0)


def test_support_scale_grows_with_large_radius() -> None:
    small = resolve_config(FerrisWheelConfig(num_gondolas=8, spoke_count=16, rim_radius=0.80))
    large = resolve_config(FerrisWheelConfig(num_gondolas=8, spoke_count=16, rim_radius=1.05))

    assert support_scale_for_radius(large.rim_radius) > support_scale_for_radius(small.rim_radius)
    assert large.support_scale > small.support_scale


def test_build_ferris_wheel_joint_contract() -> None:
    config = FerrisWheelConfig(num_gondolas=8, spoke_count=16, gondola_style="open_basket")
    model = build_ferris_wheel(config)

    wheel_joint = model.get_articulation("wheel_rotation")
    assert wheel_joint.motion_limits is not None
    assert wheel_joint.motion_limits.lower == pytest.approx(0.0)
    assert wheel_joint.motion_limits.upper == pytest.approx(6.28)

    gondola_parts = [part for part in model.parts if part.name.startswith("gondola_")]
    assert len(gondola_parts) == 8
    for index in range(1, 9):
        joint = model.get_articulation(f"gondola_pivot_{index}")
        assert joint.motion_limits is not None
        # swing limits are solver-derived (cabins must clear rim/spokes/support
        # through the whole arc), symmetric and non-trivial — not a full ±π.
        assert joint.motion_limits.lower == pytest.approx(-joint.motion_limits.upper)
        assert 0.5 <= joint.motion_limits.upper <= 3.15


def test_gondola_styles_have_distinct_visual_contracts() -> None:
    box_model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_style="box_cabin")
    )
    basket_model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_style="open_basket")
    )
    capsule_model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_style="glass_capsule")
    )
    bucket_model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_style="bucket_seat")
    )
    pod_model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=4, spoke_count=8, gondola_style="rounded_pod")
    )

    box_visuals = {visual.name for visual in box_model.get_part("gondola_1").visuals}
    basket_visuals = {visual.name for visual in basket_model.get_part("gondola_1").visuals}
    capsule_visuals = {visual.name for visual in capsule_model.get_part("gondola_1").visuals}
    bucket_visuals = {visual.name for visual in bucket_model.get_part("gondola_1").visuals}
    pod_visuals = {visual.name for visual in pod_model.get_part("gondola_1").visuals}

    assert "cabin_body" in box_visuals
    assert "basket_floor" in basket_visuals
    assert "cabin_body" not in basket_visuals
    assert "front_bench" in basket_visuals
    assert "panoramic_glass_shell" in capsule_visuals
    assert "front_round_end" in capsule_visuals
    assert "capsule_floor_ring" in capsule_visuals
    assert "cabin_body" not in capsule_visuals
    assert "bucket_floor" in bucket_visuals
    assert "bucket_back" in bucket_visuals
    assert "pod_shell" in pod_visuals
    assert "front_pod_endcap" in pod_visuals


def test_leveling_arm_extends_pivot_radius_and_axle_height() -> None:
    base = resolve_config(
        FerrisWheelConfig(num_gondolas=8, spoke_count=16, hanger_style="pivot_bar")
    )
    arm = resolve_config(
        FerrisWheelConfig(num_gondolas=8, spoke_count=16, hanger_style="leveling_arm")
    )
    # The leveling arm reserves LEVELING_ARM_LENGTH of extra clearance under the rim.
    assert arm.axle_z >= base.axle_z + LEVELING_ARM_LENGTH - 1e-6

    model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=6, spoke_count=12, hanger_style="leveling_arm")
    )
    wheel_visuals = {v.name for v in model.get_part("wheel").visuals}
    assert "rear_arm_beam_1" in wheel_visuals
    assert "front_arm_beam_1" in wheel_visuals
    assert "rear_mount_pad_1" in wheel_visuals
    # The joint origin sits radially beyond the rim by LEVELING_ARM_LENGTH.
    pivot_joint = model.get_articulation("gondola_pivot_1")
    pivot_xyz = pivot_joint.origin.xyz
    radial_offset = (pivot_xyz[1] ** 2 + pivot_xyz[2] ** 2) ** 0.5
    resolved = resolve_config(
        FerrisWheelConfig(num_gondolas=6, spoke_count=12, hanger_style="leveling_arm")
    )
    assert radial_offset == pytest.approx(resolved.rim_radius + LEVELING_ARM_LENGTH, abs=1e-6)


def test_concentric_double_rim_has_struts_and_inner_ring() -> None:
    model = build_ferris_wheel(
        FerrisWheelConfig(num_gondolas=8, spoke_count=16, rim_style="concentric_double")
    )
    wheel_visuals = {v.name for v in model.get_part("wheel").visuals}
    assert "left_outer_rim" in wheel_visuals
    assert "left_inner_rim" in wheel_visuals
    assert any(name.startswith("rear_concentric_strut_") for name in wheel_visuals)
    assert any(name.startswith("front_concentric_strut_") for name in wheel_visuals)


def test_concentric_double_rejected_with_between_rims_hanger() -> None:
    # between_rims requires rim_style='twin_rings'; concentric_double is therefore
    # rejected by the earlier hanger/rim compatibility check.
    with pytest.raises(ValueError, match="twin_rings"):
        resolve_config(
            FerrisWheelConfig(
                num_gondolas=8,
                spoke_count=16,
                rim_style="concentric_double",
                hanger_style="between_rims",
            )
        )


def test_optional_platform_extras_appear_when_enabled() -> None:
    extras = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=8,
            spoke_count=16,
            boarding_bridge_enabled=True,
            loading_plinth_enabled=True,
            operator_booth_enabled=True,
            drive_house_enabled=True,
            service_deck_enabled=True,
        )
    )
    visuals = {v.name for v in extras.get_part("support_frame").visuals}
    assert "boarding_bridge" in visuals
    assert "loading_plinth" in visuals
    assert "operator_booth" in visuals
    assert "drive_house" in visuals
    assert "service_deck" in visuals

    bare = build_ferris_wheel(FerrisWheelConfig(num_gondolas=8, spoke_count=16))
    bare_visuals = {v.name for v in bare.get_part("support_frame").visuals}
    for extra in (
        "boarding_bridge",
        "loading_plinth",
        "operator_booth",
        "drive_house",
        "service_deck",
    ):
        assert extra not in bare_visuals


def test_loading_plinth_raises_axle_height_to_clear_lowest_gondola() -> None:
    base = resolve_config(FerrisWheelConfig(num_gondolas=8, spoke_count=16))
    with_plinth = resolve_config(
        FerrisWheelConfig(num_gondolas=8, spoke_count=16, loading_plinth_enabled=True)
    )
    assert with_plinth.axle_z > base.axle_z


def test_new_seeded_configs_build_and_validate() -> None:
    # Seeds exercise the new rim / hanger / base combinations introduced.
    for seed in (101, 202, 303, 404, 505):
        cfg = config_from_seed(seed)
        model = build_ferris_wheel(cfg)
        report = run_ferris_wheel_tests(model, cfg)
        assert report.passed, report.failures


def test_palette_selection_changes_materials() -> None:
    candy = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=6,
            spoke_count=12,
            frame_palette="candy_red",
            cabin_palette="navy_and_cream",
            glass_tint="rose",
        )
    )
    materials = {m.name for m in candy.materials}
    assert "frame_main_candy_red" in materials
    assert "frame_accent_candy_red" in materials
    assert "platform_panels_candy_red" in materials
    assert "cabin_body_navy_and_cream" in materials
    assert "cabin_trim_navy_and_cream" in materials
    assert "glass_rose" in materials


def test_gondola_palette_cycles_body_color_per_index() -> None:
    palette_name = "rainbow_six"
    model = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=6,
            spoke_count=12,
            gondola_style="open_basket",
            gondola_palette=palette_name,
        )
    )
    palette = GONDOLA_PALETTES[palette_name]
    assert palette  # sanity: rainbow_six is non-empty
    materials = {m.name: m.rgba for m in model.materials}
    for idx in range(len(palette)):
        key = f"gondola_palette_{palette_name}_{idx}"
        assert key in materials
        assert materials[key] == palette[idx]


def test_gondola_palette_none_falls_back_to_cabin_body_color() -> None:
    model = build_ferris_wheel(
        FerrisWheelConfig(
            num_gondolas=4,
            spoke_count=8,
            gondola_style="box_cabin",
            cabin_palette="bronze_and_black",
            gondola_palette="none",
        )
    )
    cabin_body = next(m for m in model.materials if m.name == "cabin_body_bronze_and_black")
    gondola_1 = model.get_part("gondola_1")
    body_visual = next(v for v in gondola_1.visuals if v.name == "cabin_body")
    assert body_visual.material is cabin_body


def test_invalid_palette_names_rejected() -> None:
    with pytest.raises(ValueError, match="frame_palette"):
        resolve_config(FerrisWheelConfig(frame_palette="not_a_palette"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="cabin_palette"):
        resolve_config(FerrisWheelConfig(cabin_palette="not_a_palette"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="glass_tint"):
        resolve_config(FerrisWheelConfig(glass_tint="not_a_tint"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="gondola_palette"):
        resolve_config(FerrisWheelConfig(gondola_palette="not_a_palette"))  # type: ignore[arg-type]


def test_palette_tables_define_expected_keys() -> None:
    assert "painted_white" in FRAME_PALETTES
    assert len(FRAME_PALETTES) >= 6
    assert "cream_and_white" in CABIN_PALETTES
    assert len(CABIN_PALETTES) >= 6
    assert "smoky_blue" in GLASS_TINTS
    assert "none" in GONDOLA_PALETTES
    assert GONDOLA_PALETTES["none"] == ()
