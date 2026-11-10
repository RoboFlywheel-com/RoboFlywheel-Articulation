# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Procedural template: FURNISHED PUBLIC TOILET.
#
# A composite of the two existing templates: a `public_toilet` cabin block (N
# stalls, each with a swinging door) with a full ceramic `toilet` fixture dropped
# into each stall, FIXED-mounted to the cabin floor and facing its door.
#
# It reuses, verbatim:
#   - public_toilet.build_public_toilet  -> the block shell + per-stall doors
#   - toilet.build_toilet_fixture        -> a prefixed bowl/tank + seat/lid +
#                                           flush hardware, FIXED to the block
# so every axis of both parents is available: roof/walls/utility/door/stall-count
# + footprint scale on the shell, and body/flush/seat/palette/scale per fixture
# (each stall gets its own toilet variant).
#
# Conventions (meters, Z-up): stalls tile along +Y; each toilet sits at the back
# (-X) wall facing the door (+X). The block is the grounded root.

import random
from dataclasses import dataclass, replace

from agent.templates import Urban_Environment_Public_toilet as pt
from agent.templates import Bathroom_toilet as tl
from agent.templates.Urban_Environment_Public_toilet import (
    DOOR_MODULES,
    PALETTE_THEMES,
    PublicToiletConfig,
    ResolvedPublicToiletConfig,
    ROOF_MODULES,
    UTILITY_MODULES,
    WALLS_MODULES,
    build_public_toilet,
)
from agent.templates.Bathroom_toilet import ToiletConfig
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

STALL_MIN, STALL_MAX = 1, 15

_FLUSH_PART = {
    "dual_button": "flush_button",
    "side_lever": "flush_lever",
    "pull_chain": "pull_handle",
}


@dataclass(frozen=True)
class FurnishedPublicToiletConfig:
    shell: PublicToiletConfig
    fixture_seed: int


@dataclass(frozen=True)
class ResolvedFurnishedPublicToiletConfig:
    shell: ResolvedPublicToiletConfig
    fixtures: tuple[ToiletConfig, ...]  # one toilet config per stall


def config_from_seed(seed: int) -> FurnishedPublicToiletConfig:
    rng = random.Random(seed)
    shell = PublicToiletConfig(
        roof_module=rng.choice(ROOF_MODULES),
        walls_module=rng.choice(WALLS_MODULES),
        utility_module=rng.choice(UTILITY_MODULES),
        door_module=rng.choice(DOOR_MODULES),
        palette_theme=rng.choice(PALETTE_THEMES),
        cabin_count=rng.randint(STALL_MIN, STALL_MAX),
        # wider/taller than a bare cabin so a fixture always fits comfortably
        width_scale=round(rng.uniform(1.08, 1.40), 4),
        height_scale=round(rng.uniform(0.96, 1.10), 4),
    )
    return FurnishedPublicToiletConfig(shell=shell, fixture_seed=seed)


def resolve_config(config: FurnishedPublicToiletConfig) -> ResolvedFurnishedPublicToiletConfig:
    shell_r = pt.resolve_config(config.shell)
    fixtures = []
    for i in range(shell_r.cabin_count):
        tcfg = tl.config_from_seed(config.fixture_seed * 1000 + i * 37)
        # clamp the fixture footprint so it stays clear of the stall walls
        tcfg = replace(tcfg, width_scale=min(tcfg.width_scale, 1.05))
        fixtures.append(tcfg)
    return ResolvedFurnishedPublicToiletConfig(shell=shell_r, fixtures=tuple(fixtures))


def build_furnished_public_toilet(
    config: FurnishedPublicToiletConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    sr = r.shell
    # 1) the cabin block + doors (reuses public_toilet verbatim)
    model = build_public_toilet(config.shell, assets=assets)
    block = model.get_part("block")
    # 2) one toilet fixture per stall, at the back wall, facing the door
    cys = [i * sr.d for i in range(sr.cabin_count)]
    mount_x = -sr.w * 0.5 + 0.465  # tank rear ~3cm off the back wall, scales with w
    for i, cy in enumerate(cys):
        tl.build_toilet_fixture(
            model,
            r.fixtures[i],
            prefix=f"c{i}_",
            mount_parent=block,
            mount_origin=Origin(xyz=(mount_x, cy, pt.FLOOR_H)),
        )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_furnished_public_toilet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_furnished_public_toilet(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedFurnishedPublicToiletConfig) -> list[tuple[str, str]]:
    sr = r.shell
    f0 = tl.resolve_config(r.fixtures[0])
    return [
        ("roof", sr.roof_module),
        ("walls", sr.walls_module),
        ("utility", sr.utility_module),
        ("door", sr.door_module),
        ("stalls", f"n{sr.cabin_count}"),
        ("fixture_body", f0.body_module),
        ("fixture_flush", f0.flush_module),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_furnished_public_toilet_tests(
    object_model: ArticulatedObject, config: FurnishedPublicToiletConfig
) -> TestReport:
    r = resolve_config(config)
    sr = r.shell
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    block = object_model.get_part("block")
    ctx.check("block_present", "block" in names, "missing block")
    n = sr.cabin_count
    ctx.check("door_per_stall", sum(1 for nm in names if nm.startswith("door_")) == n, f"expected {n} doors")
    ctx.check("toilet_per_stall", sum(1 for nm in names if nm.endswith("_body")) == n, f"expected {n} toilets")

    for i in range(n):
        p = f"c{i}_"
        tr = tl.resolve_config(r.fixtures[i])
        ctx.check(f"{p}body_present", f"{p}body" in names, f"stall {i} toilet body missing")
        # door seats in the cabin front frame when closed
        ctx.allow_overlap(object_model.get_part(f"door_{i}"), block, reason=f"Closed stall {i} door seats in the cabin front frame.")
        # toilet is bolted to the cabin floor
        mnt = object_model.get_articulation(f"{p}mount")
        ctx.check(f"{p}mount_fixed", mnt.articulation_type == ArticulationType.FIXED, f"stall {i} toilet must be FIXED-mounted")
        tbody = object_model.get_part(f"{p}body")
        ctx.allow_overlap(tbody, block, reason=f"Stall {i} toilet is bolted to the cabin floor pan (FIXED mount); base seats on the floor.")
        # seat ring is a lateral revolute opening from closed
        srj = object_model.get_articulation(f"{p}body_to_seat_ring")
        ctx.check(
            f"{p}seat_revolute",
            srj.articulation_type == ArticulationType.REVOLUTE and abs(srj.axis[1]) > 0.99 and abs(srj.motion_limits.lower) < 1e-9,
            f"stall {i} seat ring must be a lateral revolute from closed",
        )
        # replicate the fixture's own internal overlap allowances (prefixed)
        ctx.allow_overlap(object_model.get_part(f"{p}seat_ring"), tbody, reason="Seat ring rear rides the bowl-rim hinge barrel/boss; pose-invariant.")
        if tr.seat_module == "ring_lid":
            lid = object_model.get_part(f"{p}seat_lid")
            ctx.allow_overlap(lid, tbody, reason="Closed lid rests on the rim/hinge barrel; pose-invariant.")
            ctx.allow_overlap(lid, object_model.get_part(f"{p}seat_ring"), reason="Closed lid stacks flush on the seat ring.")
        flush_part = object_model.get_part(f"{p}{_FLUSH_PART[tr.flush_module]}")
        ctx.allow_overlap(flush_part, tbody, reason="Flush hardware seats into the tank recess/guide; on the actuation axis.")

    return ctx.report()


__all__ = [
    "FurnishedPublicToiletConfig",
    "ResolvedFurnishedPublicToiletConfig",
    "config_from_seed",
    "resolve_config",
    "build_furnished_public_toilet",
    "build_seeded_furnished_public_toilet",
    "slot_choices_for_seed",
    "run_furnished_public_toilet_tests",
]
