# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import random

import pytest

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    _validate_pair,
    assemble,
    fit_to_upstream,
)
from sdk import ArticulatedObject, Box, Origin


def _empty_module(name: str):
    def _factory(_ctx) -> ModuleBuild:
        return ModuleBuild(module_name=name, parts_emitted=[])

    return _factory


def test_assemble_seed_zero_uses_procedural_selection_by_default() -> None:
    slot = SlotSpec(
        slot_name="body",
        candidates={"anchor": _empty_module("anchor"), "sampled": _empty_module("sampled")},
        anchor_choice="anchor",
    )

    result = assemble(
        ArticulatedObject(name="procedural_default"),
        slots=[slot],
        rng=random.Random(0),
        palette={},
        config=object(),
        seed=0,
    )

    assert result.slot_choices == [("body", "sampled")]


def test_assemble_can_explicitly_consume_pinned_anchor_choices() -> None:
    slot = SlotSpec(
        slot_name="body",
        candidates={"anchor": _empty_module("anchor"), "sampled": _empty_module("sampled")},
        anchor_choice="anchor",
    )

    result = assemble(
        ArticulatedObject(name="pinned_choices"),
        slots=[slot],
        rng=random.Random(0),
        palette={},
        config=object(),
        seed=0,
        selection_mode="anchor_choices",
    )

    assert result.slot_choices == [("body", "anchor")]


# --------------------------------------------------------------------------- #
# iface_key: interface identity / combination legality
# --------------------------------------------------------------------------- #


def _iface(side: str, *, key: str | None = None, part: str = "p") -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream" if side.startswith("positive") else "upstream",
        part_name=part,
        visual_name="face",
        face_side=side,
        anchor_local=(0.0, 0.0, 0.0),
        iface_key=key,
    )


def test_validate_pair_rejects_mismatched_iface_keys() -> None:
    with pytest.raises(ValueError, match="interface keys incompatible"):
        _validate_pair(
            _iface("positive_z", key="neck_28mm", part="body"),
            _iface("negative_z", key="neck_35mm", part="cap"),
            slot_name="closure",
        )


def test_validate_pair_allows_matching_or_undeclared_keys() -> None:
    # Both declared and equal.
    _validate_pair(
        _iface("positive_z", key="deck_top"),
        _iface("negative_z", key="deck_top"),
        slot_name="tray",
    )
    # One-sided declaration skips the check (incremental adoption).
    _validate_pair(
        _iface("positive_z", key="deck_top"),
        _iface("negative_z"),
        slot_name="tray",
    )
    # Fully undeclared = legacy behavior.
    _validate_pair(_iface("positive_z"), _iface("negative_z"), slot_name="tray")


def _body_factory(ctx: ModuleBuildContext) -> ModuleBuild:
    body = ctx.model.part("body")
    body.visual(Box((0.4, 0.3, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="body_top")
    return ModuleBuild(
        module_name="body",
        parts_emitted=["body"],
        interfaces={
            "downstream": InterfaceSpec(
                interface_name="downstream",
                part_name="body",
                visual_name="body_top",
                face_side="positive_z",
                anchor_local=(0.0, 0.0, 0.1),
                face_extents_uv=(0.4, 0.3),
                iface_key="deck_top",
            )
        },
    )


def _lid_factory(key: str, captured: list[tuple[float, float]]):
    def _factory(ctx: ModuleBuildContext) -> ModuleBuild:
        u, v = fit_to_upstream(ctx, inset=0.02)
        captured.append((u, v))
        lid = ctx.model.part("lid")
        lid.visual(Box((u, v, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.01)), name="lid_bottom")
        return ModuleBuild(
            module_name="lid",
            parts_emitted=["lid"],
            interfaces={
                "upstream": InterfaceSpec(
                    interface_name="upstream",
                    part_name="lid",
                    visual_name="lid_bottom",
                    face_side="negative_z",
                    anchor_local=(0.0, 0.0, 0.0),
                    iface_key=key,
                )
            },
        )

    return _factory


def _chain_slots(lid_key: str, captured: list[tuple[float, float]]) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="body", candidates={"box": _body_factory}, anchor_choice="box"),
        SlotSpec(
            slot_name="lid",
            candidates={"flat": _lid_factory(lid_key, captured)},
            anchor_choice="flat",
        ),
    ]


def test_assemble_chains_matching_keys_and_derives_child_footprint() -> None:
    captured: list[tuple[float, float]] = []
    model = ArticulatedObject(name="keyed_chain")
    result = assemble(
        model,
        slots=_chain_slots("deck_top", captured),
        rng=random.Random(0),
        palette={},
        config=object(),
        seed=0,
    )
    assert result.slot_choices == [("body", "box"), ("lid", "flat")]
    # Footprint derived from the parent face (0.4, 0.3) minus 0.02 per side.
    assert captured == [(pytest.approx(0.36), pytest.approx(0.26))]
    assert [a.name for a in model.articulations] == ["body_to_lid"]


def test_assemble_rejects_mismatched_keys_at_chain_time() -> None:
    with pytest.raises(ValueError, match="interface keys incompatible"):
        assemble(
            ArticulatedObject(name="keyed_chain_bad"),
            slots=_chain_slots("hinged_rim", []),
            rng=random.Random(0),
            palette={},
            config=object(),
            seed=0,
        )


# --------------------------------------------------------------------------- #
# fit_to_upstream: footprint derivation
# --------------------------------------------------------------------------- #


def _ctx(upstream: InterfaceSpec | None) -> ModuleBuildContext:
    return ModuleBuildContext(
        model=ArticulatedObject(name="ctx"),
        palette={},
        rng=random.Random(0),
        config=object(),
        slot_name="lid",
        module_name="flat",
        upstream_interface=upstream,
    )


def _sized_iface(extents: tuple[float, float]) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="body",
        visual_name="body_top",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.1),
        face_extents_uv=extents,
    )


def test_fit_to_upstream_scales_insets_and_clamps() -> None:
    ctx = _ctx(_sized_iface((0.4, 0.3)))
    assert fit_to_upstream(ctx) == (pytest.approx(0.4), pytest.approx(0.3))
    assert fit_to_upstream(ctx, scale=(0.5, 1.0), inset=0.02) == (
        pytest.approx(0.16),
        pytest.approx(0.26),
    )
    assert fit_to_upstream(ctx, inset=(0.0, 0.05)) == (pytest.approx(0.4), pytest.approx(0.2))
    assert fit_to_upstream(ctx, min_uv=(0.45, 0.0)) == (pytest.approx(0.45), pytest.approx(0.3))
    assert fit_to_upstream(ctx, max_uv=(0.3, 0.25)) == (pytest.approx(0.3), pytest.approx(0.25))


def test_fit_to_upstream_requires_an_upstream_interface() -> None:
    with pytest.raises(ValueError, match="no upstream interface"):
        fit_to_upstream(_ctx(None))


def test_fit_to_upstream_requires_declared_face_extents() -> None:
    with pytest.raises(ValueError, match="face_extents_uv"):
        fit_to_upstream(_ctx(_sized_iface((0.0, 0.0))))


def test_fit_to_upstream_rejects_degenerate_footprint() -> None:
    with pytest.raises(ValueError, match="degenerate"):
        fit_to_upstream(_ctx(_sized_iface((0.4, 0.3))), inset=0.2)
