# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SOURCE_REPO = Path(
    os.environ.get(
        "PICTUREX_0611_SOURCE_REPO",
        "pictureX_0611_selected_categories_records_no_urdf_mesh_20260711",
    )
)
TEMPLATE_REPO = Path(os.environ.get("ARTI_TEMPLATE_REPO", "arti-template"))


@dataclass(frozen=True)
class Variant:
    record_id: str
    category: str
    subcategory: str
    picture: str
    parent_record_id: str
    family: str
    variant: str
    palette: str
    count: int
    axis: str
    title: str
    note: str


PARENTS = {
    "wringer": "rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b",
    "hole1": "rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d",
    "hole2": "rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff",
    "hutch": "rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba",
    "jack": "rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14",
    "jack_b": "rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae",
    "jack1": "rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613",
    "jack1_b": "rec_picturex_0611__hydraulic_jack1__002__png_343b03cbe8414658969055f2ca9c7a13",
    "jack2": "rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0",
}


VARIANTS: list[Variant] = [
    Variant("rec_picturex0611_wringer_var_table_clamp", "0611", "Hand-crank_clothes_wringer", "pictureX/0611/Hand-crank_clothes_wringer/001.png", PARENTS["wringer"], "requested", "table_clamp", "painted_blue", 2, "support_mount", "table-clamp wringer", "bench clamp support while preserving twin rollers and crank"),
    Variant("rec_picturex0611_wringer_var_freestanding_frame", "0611", "Hand-crank_clothes_wringer", "pictureX/0611/Hand-crank_clothes_wringer/001.png", PARENTS["wringer"], "requested", "freestanding_frame", "zinc_black", 2, "support_skeleton", "freestanding wringer frame", "upright support frame while preserving roller mechanism"),
    Variant("rec_picturex0611_wringer_var_wide_twin_gear", "0611", "Hand-crank_clothes_wringer", "pictureX/0611/Hand-crank_clothes_wringer/001.png", PARENTS["wringer"], "requested", "wide_twin_gear", "painted_red", 3, "gear_side_detail", "wide twin-gear wringer", "side gear/bearing vocabulary and three-roll count probe"),
    Variant("rec_picturex0611_hole_punch_var_desktop_n3", "0611", "Hole_punch", "pictureX/0611/Hole_punch/001.png", PARENTS["hole1"], "hole_punch", "desktop_pivot_n3", "office_blue", 3, "multiplicity", "desktop three-hole punch", "three punch/die stations on desktop base"),
    Variant("rec_picturex0611_hole_punch_var_plunger", "0611", "Hole_punch", "pictureX/0611/Hole_punch/001.png", PARENTS["hole1"], "hole_punch", "desktop_plunger", "graphite", 1, "mechanism", "vertical plunger hole punch", "straight-down prismatic plunger mechanism"),
    Variant("rec_picturex0611_hole_punch_var_lever_carriage", "0611", "Hole_punch", "pictureX/0611/Hole_punch/002.png", PARENTS["hole2"], "hole_punch", "lever_carriage", "office_red", 4, "compound_mechanism", "lever-carriage four-hole punch", "revolute lever driving prismatic carriage"),
    Variant("rec_picturex0611_hole_punch_var_cloop", "0611", "Hole_punch", "pictureX/0611/Hole_punch/002.png", PARENTS["hole2"], "hole_punch", "cloop_handheld", "chrome", 1, "body_skeleton", "C-loop handheld punch", "spring C-loop handheld skeleton"),
    Variant("rec_picturex0611_hutch_var_glass_doors", "0611", "Hutch_Cabinet", "pictureX/0611/Hutch_Cabinet/001.png", PARENTS["hutch"], "requested", "glass_doors", "warm_oak", 3, "door_front", "glass-door hutch", "paired hinged glass upper doors"),
    Variant("rec_picturex0611_hutch_var_open_shelves", "0611", "Hutch_Cabinet", "pictureX/0611/Hutch_Cabinet/001.png", PARENTS["hutch"], "requested", "open_shelves", "painted_white", 4, "open_storage", "open shelf hutch", "open shelf count and no upper doors"),
    Variant("rec_picturex0611_hutch_var_drawer_base", "0611", "Hutch_Cabinet", "pictureX/0611/Hutch_Cabinet/001.png", PARENTS["hutch"], "requested", "drawer_base", "zinc_black", 3, "lower_storage", "drawer-base hutch", "lower prismatic drawer bank with upper hutch"),
    Variant("rec_picturex0611_hydraulic_jack_var_bottle", "0611", "hydraulic_jack", "pictureX/0611/hydraulic_jack/001.png", PARENTS["jack"], "requested", "bottle_jack", "painted_red", 2, "body_family", "bottle hydraulic jack", "compact vertical bottle jack family"),
    Variant("rec_picturex0611_hydraulic_jack_var_floor_trolley", "0611", "hydraulic_jack", "pictureX/0611/hydraulic_jack/002.png", PARENTS["jack_b"], "requested", "floor_trolley", "painted_blue", 4, "rolling_base", "floor trolley jack", "long rolling chassis with pump handle"),
    Variant("rec_picturex0611_hydraulic_jack_var_lift_table", "0611", "hydraulic_jack", "pictureX/0611/hydraulic_jack/001.png", PARENTS["jack"], "requested", "hydraulic_table", "zinc_black", 4, "lift_topology", "hydraulic lift table", "scissor/lift-platform topology probe"),
    Variant("rec_picturex0611_hydraulic_jack1_var_bottle", "0611", "hydraulic_jack1", "pictureX/0611/hydraulic_jack1/001.png", PARENTS["jack1"], "requested", "bottle_jack", "painted_blue", 2, "body_family", "jack1 bottle form", "bottle jack candidate for jack1"),
    Variant("rec_picturex0611_hydraulic_jack1_var_floor", "0611", "hydraulic_jack1", "pictureX/0611/hydraulic_jack1/002.png", PARENTS["jack1_b"], "requested", "floor_trolley", "painted_red", 4, "rolling_base", "jack1 trolley form", "floor trolley candidate for jack1"),
    Variant("rec_picturex0611_hydraulic_jack1_var_table", "0611", "hydraulic_jack1", "pictureX/0611/hydraulic_jack1/001.png", PARENTS["jack1"], "requested", "hydraulic_table", "zinc_black", 4, "lift_topology", "jack1 lift table form", "hydraulic table compatibility probe for jack1"),
    Variant("rec_picturex0611_hydraulic_jack2_var_table", "0611", "hydraulic_jack2", "pictureX/0611/hydraulic_jack2/001.png", PARENTS["jack2"], "requested", "hydraulic_table", "painted_blue", 4, "lift_topology", "jack2 lift table form", "table-lift structure preserving hydraulic identity"),
    Variant("rec_picturex0611_hydraulic_jack2_var_floor", "0611", "hydraulic_jack2", "pictureX/0611/hydraulic_jack2/001.png", PARENTS["jack2"], "requested", "floor_trolley", "painted_red", 4, "rolling_base", "jack2 floor trolley form", "rolling floor jack compatibility candidate"),
    Variant("rec_picturex0611_hydraulic_jack2_var_bottle", "0611", "hydraulic_jack2", "pictureX/0611/hydraulic_jack2/001.png", PARENTS["jack2"], "requested", "bottle_jack", "zinc_black", 2, "body_family", "jack2 bottle form", "compact bottle-jack compatibility candidate"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def model_source(v: Variant) -> str:
    template_path = TEMPLATE_REPO.as_posix()
    if v.family == "hole_punch":
        mapping = {
            "desktop_pivot_n3": ("desktop_base", "pivot_lever", 3, v.palette),
            "desktop_plunger": ("desktop_base", "plunger", 1, v.palette),
            "lever_carriage": ("desktop_base", "lever_carriage", 4, v.palette),
            "cloop_handheld": ("cloop_frame", "pivot_lever", 1, v.palette),
        }
        skeleton, mechanism, n_holes, palette = mapping[v.variant]
        return f'''from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, {template_path!r})

from agent.templates.hole_punch import (
    HOLE_PUNCH_PALETTE_PRESETS,
    HolePunchConfig,
    build_hole_punch,
    run_hole_punch_tests,
)

CONFIG = HolePunchConfig(
    skeleton={skeleton!r},
    mechanism={mechanism!r},
    n_holes={n_holes},
    palette_theme={palette!r},
    palette=dict(HOLE_PUNCH_PALETTE_PRESETS[{palette!r}]),
)


def build_object_model():
    model = build_hole_punch(CONFIG)
    model.meta["source_image"] = {v.picture!r}
    model.meta["parent_record_id"] = {v.parent_record_id!r}
    model.meta["variant_axis"] = {v.axis!r}
    model.meta["local_fork_record_id"] = {v.record_id!r}
    return model


def run_tests():
    return run_hole_punch_tests(object_model, CONFIG)


object_model = build_object_model()
'''

    category = {
        "Hand-crank_clothes_wringer": "hand_crank_clothes_wringer",
        "Hutch_Cabinet": "hutch_cabinet",
        "hydraulic_jack": "hydraulic_jack",
        "hydraulic_jack1": "hydraulic_jack",
        "hydraulic_jack2": "hydraulic_jack",
    }[v.subcategory]
    return f'''from __future__ import annotations

import sys

sys.path.insert(0, {template_path!r})

from agent.templates.pictureX_0611_common_requested import (
    Requested0611Config,
    build_requested_0611,
    run_requested_0611_tests,
)

CONFIG = Requested0611Config(
    category={category!r},
    variant={v.variant!r},
    palette={v.palette!r},
    count={v.count},
    width_scale=1.0,
    height_scale=1.0,
    travel_scale=1.0,
)


def build_object_model():
    model = build_requested_0611(CONFIG)
    model.meta["source_image"] = {v.picture!r}
    model.meta["picture_subcategory"] = {v.subcategory!r}
    model.meta["parent_record_id"] = {v.parent_record_id!r}
    model.meta["variant_axis"] = {v.axis!r}
    model.meta["local_fork_record_id"] = {v.record_id!r}
    return model


def run_tests():
    return run_requested_0611_tests(object_model, CONFIG)


object_model = build_object_model()
'''


def create_variant(v: Variant) -> None:
    record_dir = SOURCE_REPO / "data" / "records" / v.record_id
    rev_dir = record_dir / "revisions" / "rev_000001"
    now = utc_now()
    prompt = (
        f"Local workbench fork for {v.picture}. Parent: {v.parent_record_id}. "
        f"Primary structural axis: {v.axis}. Target variant: {v.title}. "
        f"Keep category identity and change only this structural axis: {v.note}."
    )
    model_py = model_source(v)
    write_json(
        record_dir / "record.json",
        {
            "schema_version": 3,
            "record_id": v.record_id,
            "created_at": now,
            "updated_at": now,
            "rating": None,
            "secondary_rating": None,
            "author": "codex-local",
            "rated_by": None,
            "secondary_rated_by": None,
            "kind": "generated_model",
            "prompt_kind": "single_prompt",
            "category_slug": f"picturex_0611__{v.subcategory.lower()}__variant__{v.axis}",
            "source": {
                "run_id": "local_picturex_0611_gate2_variants_20260712",
                "prompt_batch_id": None,
                "batch_spec_id": "local_picturex_0611_gate2_variants_20260712",
                "row_id": v.record_id,
                "prompt_index": None,
            },
            "sdk_package": "sdk",
            "provider": "local",
            "model_id": "codex-local-fork",
            "display": {
                "title": f"{v.picture} - {v.title}",
                "prompt_preview": prompt[:180],
            },
            "artifacts": {
                "prompt_txt": "revisions/rev_000001/prompt.txt",
                "prompt_series_json": None,
                "model_py": "revisions/rev_000001/model.py",
                "provenance_json": "revisions/rev_000001/provenance.json",
                "cost_json": None,
                "inputs_dir": "revisions/rev_000001/inputs",
                "traces_dir": "revisions/rev_000001/traces",
            },
            "hashes": {
                "prompt_sha256": sha256_text(prompt),
                "model_py_sha256": sha256_text(model_py),
            },
            "collections": ["workbench"],
            "active_revision_id": "rev_000001",
            "lineage": {
                "origin_record_id": v.parent_record_id,
                "parent_record_id": v.parent_record_id,
                "parent_revision_id": "rev_000001",
                "edit_mode": "local_structural_fork",
            },
        },
    )
    write_json(record_dir / "collections" / "workbench.json", {"record_id": v.record_id, "collection": "workbench", "created_at": now})
    write_json(record_dir / "picture.json", {"category": v.category, "subcategory": v.subcategory, "source": "explicit", "path": v.picture})
    write_json(
        rev_dir / "revision.json",
        {
            "schema_version": 1,
            "record_id": v.record_id,
            "revision_id": "rev_000001",
            "created_at": now,
            "prompt_kind": "single_prompt",
            "prompt_sha256": sha256_text(prompt),
            "source": {
                "run_id": "local_picturex_0611_gate2_variants_20260712",
                "prompt_batch_id": None,
                "batch_spec_id": "local_picturex_0611_gate2_variants_20260712",
                "row_id": v.record_id,
                "prompt_index": None,
            },
            "generation": {
                "provider": "local",
                "model_id": "codex-local-fork",
                "thinking_level": "n/a",
                "max_turns": None,
                "max_cost_usd": 0,
            },
            "artifacts": {
                "prompt_txt": "revisions/rev_000001/prompt.txt",
                "prompt_series_json": None,
                "model_py": "revisions/rev_000001/model.py",
                "provenance_json": "revisions/rev_000001/provenance.json",
                "cost_json": None,
                "inputs_dir": "revisions/rev_000001/inputs",
                "traces_dir": "revisions/rev_000001/traces",
            },
            "hashes": {
                "prompt_sha256": sha256_text(prompt),
                "model_py_sha256": sha256_text(model_py),
            },
            "run_summary": {
                "turn_count": 0,
                "tool_call_count": 0,
                "compile_attempt_count": 0,
                "final_status": "local_fork_created",
            },
            "parent": {
                "record_id": v.parent_record_id,
                "revision_id": "rev_000001",
                "variant_axis": v.axis,
            },
            "seed": None,
            "inherited_inputs": [],
        },
    )
    write_json(
        rev_dir / "provenance.json",
        {
            "schema_version": 2,
            "record_id": v.record_id,
            "generation": {
                "provider": "local",
                "model_id": "codex-local-fork",
                "thinking_level": "n/a",
                "max_turns": None,
                "max_cost_usd": 0,
            },
            "prompting": {
                "source_parent_record_id": v.parent_record_id,
                "variant_axis": v.axis,
                "variant_note": v.note,
            },
            "sdk": {
                "sdk_package": "sdk",
                "sdk_version": "workspace",
                "sdk_fingerprint": None,
            },
            "environment": {
                "python_version": "3.12",
                "platform": "linux",
                "git_commit": None,
                "uv_lock_sha256": None,
            },
            "run_summary": {
                "turn_count": 0,
                "tool_call_count": 0,
                "compile_attempt_count": 0,
                "final_status": "local_fork_created",
            },
        },
    )
    (rev_dir / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    (rev_dir / "model.py").write_text(model_py, encoding="utf-8")


def main() -> int:
    for variant in VARIANTS:
        create_variant(variant)
        print(variant.record_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
