#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Measure finite discrete sampling spaces for every agent template.

The formal path is exact: TemplateDomain.audit() defines core/raw domain sizes.
For legacy templates, the only supported sampling surface is used, and its
finite categorical axes are measured over a deterministic dense probe.  The
reported ``*_theoretical`` fields are the Cartesian product of the measured
finite axes; ``reachable_discrete_combos`` is retained separately because a
legacy sampler may correlate axes.
"""

from __future__ import annotations

import csv
import importlib
import json
import math
import os
import pathlib
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any


HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[1]
TEMPLATE_DIR = REPO / "agent" / "templates"
OUT_DIR = REPO / "reports" / "discrete_space"
PROBE_SEEDS = 2000
PROBE_PATIENCE = 300


def _stable(value: Any) -> str:
    return f"{type(value).__name__}:{value!r}"


def _normalize_choices(raw: Any) -> tuple[tuple[str, str], ...]:
    items = raw.items() if isinstance(raw, dict) else raw
    result = []
    for item in items:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError(f"invalid slot item: {item!r}")
        result.append((str(item[0]), str(item[1])))
    if not result:
        raise ValueError("empty slot choice")
    return tuple(result)


def _is_palette_key(key: str) -> bool:
    leaf = key.rsplit(".", 1)[-1].lower()
    return any(
        token in leaf
        for token in ("palette", "colorway", "colourway", "material", "finish", "texture")
    )


def _is_multiplicity_key(key: str, values: set[str]) -> bool:
    leaf = key.rsplit(".", 1)[-1].lower()
    if re.search(r"(^|_)(count|num|number|quantity|multiplicity)(_|$)", leaf):
        return True
    if any(re.fullmatch(r"n\d+", value.lower()) for value in values):
        return True
    # A bare component name such as ``wheel_style`` or ``controller`` is not
    # multiplicity.  Only explicit count-like suffixes are promoted here.
    return bool(re.search(r"(^|_)(segments|arms|links|shelves|drawers|rollers|spokes|wheels|fingers|stages|joints|buttons|controls|legs|blades|teeth|panels|plates|sides)(_|$)", leaf))


def _categorical_axis_rows(values_by_key: dict[str, set[str]]) -> tuple[list[dict[str, Any]], int, int]:
    axes: list[dict[str, Any]] = []
    core = raw = 1
    for key in sorted(values_by_key):
        values = values_by_key[key]
        if not values or _is_palette_key(key):
            continue
        kind = "multiplicity" if _is_multiplicity_key(key, values) else "component"
        count = len(values)
        axes.append({"name": key, "kind": kind, "value_count": count, "values": sorted(values)})
        raw *= count
        if kind == "component":
            core *= count
    return axes, core, raw


def _measure_legacy(slug: str) -> dict[str, Any]:
    sys.path.insert(0, str(REPO))
    module = importlib.import_module(f"agent.templates.{slug}")
    slot_fn = getattr(module, "slot_choices_for_seed", None)
    values_by_key: dict[str, set[str]] = defaultdict(set)
    combos: set[tuple[tuple[str, str], ...]] = set()
    errors = 0
    since_new = 0
    used = 0
    saturated = False

    if callable(slot_fn):
        for seed in range(PROBE_SEEDS):
            used = seed + 1
            try:
                choices = _normalize_choices(slot_fn(seed))
            except Exception:
                errors += 1
                continue
            for key, value in choices:
                values_by_key[key].add(value)
            if choices in combos:
                since_new += 1
            else:
                combos.add(choices)
                since_new = 0
            if since_new >= PROBE_PATIENCE:
                saturated = True
                break
        source = "legacy_slot_probe"
    else:
        # A small legacy tail predates slot_choices_for_seed.  Extract only
        # finite categorical/count fields from config_from_seed; continuous
        # numeric fields are deliberately excluded.
        config_fn = getattr(module, "config_from_seed")
        raw_discrete: dict[str, set[str]] = defaultdict(set)
        config_signatures: set[tuple[tuple[str, str], ...]] = set()
        for seed in range(PROBE_SEEDS):
            used = seed + 1
            try:
                cfg = config_fn(seed)
            except Exception:
                errors += 1
                continue
            flat = _flatten(cfg)
            sig: list[tuple[str, str]] = []
            for key, value in flat.items():
                leaf = key.rsplit(".", 1)[-1].lower()
                if leaf in {"seed", "name"} or _is_palette_key(key):
                    continue
                if isinstance(value, (str, bool)):
                    raw_discrete[key].add(str(value))
                    sig.append((key, str(value)))
                elif isinstance(value, int) and not isinstance(value, bool) and _is_multiplicity_key(key, {str(value)}):
                    raw_discrete[key].add(str(value))
                    sig.append((key, str(value)))
            signature = tuple(sorted(sig))
            if signature in config_signatures:
                since_new += 1
            else:
                config_signatures.add(signature)
                since_new = 0
            if since_new >= PROBE_PATIENCE:
                saturated = True
                break
        values_by_key = raw_discrete
        combos = config_signatures
        source = "legacy_config_probe"

    axes, core, raw = _categorical_axis_rows(values_by_key)
    return {
        "slug": slug,
        "status": "ok",
        "method": source,
        "domain_status": "legacy",
        "core_domain_theoretical": core,
        "raw_domain_theoretical": raw,
        "reachable_discrete_combos": len(combos),
        "probe_seeds_used": used,
        "probe_errors": errors,
        "probe_saturated": saturated,
        "axes": axes,
    }


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if hasattr(value, "__dataclass_fields__"):
        value = {name: getattr(value, name) for name in value.__dataclass_fields__}
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, child in value.items():
            child_key = f"{prefix}.{key}" if prefix else str(key)
            result.update(_flatten(child, child_key))
        return result
    if isinstance(value, (list, tuple, set, frozenset)):
        return {f"{prefix}#len": len(value)} if prefix else {}
    return {prefix: value} if prefix else {}


def _measure_one(slug: str) -> dict[str, Any]:
    sys.path.insert(0, str(REPO))
    try:
        module = importlib.import_module(f"agent.templates.{slug}")
        domain = getattr(module, "TEMPLATE_DOMAIN", None)
        if domain is not None and hasattr(domain, "audit"):
            audit = domain.audit()
            axes = []
            for slot in domain.slots:
                axes.append(
                    {
                        "name": slot.name,
                        "kind": slot.kind,
                        "value_count": len(slot.values),
                        "values": [repr(v) for v in slot.values],
                    }
                )
            return {
                "slug": slug,
                "status": "ok",
                "method": "template_domain_audit",
                "domain_status": "declared",
                "core_domain_theoretical": int(audit["core_domain"]),
                "raw_domain_theoretical": int(audit["raw_domain"]),
                "reachable_discrete_combos": int(audit["raw_domain"]),
                "probe_seeds_used": 0,
                "probe_errors": 0,
                "probe_saturated": True,
                "axes": axes,
            }
        return _measure_legacy(slug)
    except Exception as exc:  # keep the full fleet auditable
        return {
            "slug": slug,
            "status": "error",
            "method": "error",
            "domain_status": "unknown",
            "core_domain_theoretical": 0,
            "raw_domain_theoretical": 0,
            "reachable_discrete_combos": 0,
            "probe_seeds_used": 0,
            "probe_errors": 0,
            "probe_saturated": False,
            "axes": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def _prefix_group(slug: str) -> str:
    broad = {
        "Art_Drawing_Models": "art_and_models",
        "Astronomy": "astronomy_and_space",
        "Bag_Suitcase": "bags_and_luggage",
        "Bar": "music_and_audio",
        "Bathroom": "household_and_utilities",
        "Bench": "furniture_and_storage",
        "Chair": "furniture_and_storage",
        "Container": "containers_and_storage",
        "Curtain": "doors_gates_and_access",
        "Door": "doors_gates_and_access",
        "Electrical_Wiring": "electronics_and_equipment",
        "Equipment": "electronics_and_equipment",
        "Facade_Element": "buildings_and_infrastructure",
        "Fence": "buildings_and_infrastructure",
        "Fountain": "outdoor_and_recreation",
        "Handtools": "tools_and_workshop",
        "Headwear": "sports_and_mobility",
        "Healthcare": "science_and_healthcare",
        "Household": "household_and_utilities",
        "Household_Laundry": "household_and_utilities",
        "Industrial": "industrial_and_machinery",
        "Kitchen": "household_and_utilities",
        "Light": "electronics_and_equipment",
        "Machinery": "industrial_and_machinery",
        "Military": "military_and_defense",
        "Music": "music_and_audio",
        "Other": "household_and_utilities",
        "Others": "household_and_utilities",
        "Parts": "tools_and_workshop",
        "pictureX_0611": "pictureX_0611",
        "Pilers": "tools_and_workshop",
        "Playground": "outdoor_and_recreation",
        "Powertools": "tools_and_workshop",
        "Science": "science_and_healthcare",
        "Sign": "buildings_and_infrastructure",
        "Sports": "sports_and_mobility",
        "Stairs": "buildings_and_infrastructure",
        "Stationary": "tools_and_workshop",
        "Structure": "buildings_and_infrastructure",
        "Technology": "electronics_and_equipment",
        "Urban_Environment": "urban_infrastructure",
        "Vehicle": "vehicles_and_mobility",
        "Window": "doors_gates_and_access",
    }
    for prefix, group in broad.items():
        if slug.casefold() == prefix.casefold() or slug.casefold().startswith(prefix.casefold() + "_"):
            return group
    # Most unprefixed filenames are still recognizable category names.  Keep
    # this fallback deterministic and coarse enough to form useful long-tail
    # groups instead of one group per isolated filename prefix.
    name = slug.casefold()
    keyword_groups = (
        ("furniture_and_storage", ("cabinet", "shelf", "shelving", "table", "desk", "bench", "dresser", "storage", "wine_rack", "office")),
        ("electronics_and_equipment", ("monitor", "camera", "camcorder", "scanner", "projector", "graphics_card", "laptop", "barcode", "cctv", "watch", "light", "display", "projector")),
        ("tools_and_workshop", ("pilers", "grinder", "drill", "cutter", "grinder", "grinder", "wrench", "pulley", "ratchet", "rivet", "grip", "clamp", "mill", "pepper", "nutcracker", "pasta_maker", "pipe_bender", "tube_cutter", "turnbuckle")),
        ("doors_gates_and_access", ("door", "gate", "turnstile", "window", "shutter", "elevator_shaft", "awning", "greenhouse_vent", "cat_flap", "blind")),
        ("vehicles_and_mobility", ("bicycle", "wheelbarrow", "tractor", "tricycle", "ferris", "hamster_wheel", "differential", "cart", "stretcher", "telescope_on_tripod")),
        ("outdoor_and_recreation", ("aquarium", "bird_cage", "camp", "pet_", "rabbit", "seed", "sprinkler", "sailboat", "trekking", "camping", "feeding_bowl", "hutch")),
        ("music_and_audio", ("piano", "trombone", "trumpet", "music_stand", "microphone")),
        ("science_and_healthcare", ("makeup", "microscope", "syringe", "defibrillator", "health", "medical", "dental")),
        ("industrial_and_machinery", ("machine", "conveyor", "harvester", "watermill", "actuator", "harmonic_drive", "roller_conveyor")),
        ("mounts_and_positioning", ("arm", "tripod", "telescope", "protractor", "pulley", "projector")),
    )
    for group, keywords in keyword_groups:
        if any(keyword in name for keyword in keywords):
            return group
    return "unprefixed_misc"


def _load_big_category_map() -> dict[str, str]:
    data = json.loads((REPO / "data" / "supercategories.json").read_text())
    result: dict[str, str] = {}
    for group in data.get("supercategories", []):
        for category in group.get("category_slugs", []):
            result[str(category).lower()] = str(group["slug"])
    return result


def _attach_category(row: dict[str, Any], registry: dict[str, str], supermap: dict[str, str]) -> None:
    slug = row["slug"]
    stem = registry.get(slug, slug)
    exact = supermap.get(str(stem).lower())
    row["registry_stem"] = stem
    row["big_category"] = exact or _prefix_group(slug)
    row["category_basis"] = "supercategory_manifest" if exact else "filename_prefix_fallback"
    row["axis_count"] = len(row.get("axes", []))
    row["axis_summary"] = "; ".join(
        f"{axis['name']}[{axis['kind']}:{axis['value_count']}]" for axis in row.get("axes", [])
    )


def _write_csv(path: pathlib.Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def _make_plot(rows: list[dict[str, Any]], summary: list[dict[str, Any]]) -> None:
    import matplotlib.pyplot as plt

    ordered_groups = sorted(summary, key=lambda row: row["raw_domain_sum"], reverse=True)
    labels = [row["big_category"] for row in ordered_groups]
    values = [row["raw_domain_sum"] for row in ordered_groups]
    cumulative = []
    running = 0
    total = sum(values) or 1
    for value in values:
        running += value
        cumulative.append(running / total * 100)

    ordered_templates = sorted(rows, key=lambda row: row["raw_domain_theoretical"], reverse=True)
    template_values = [row["raw_domain_theoretical"] for row in ordered_templates]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9), gridspec_kw={"width_ratios": [1.25, 1]})
    x = list(range(len(labels)))
    ax1.bar(x, values, color="#276FBF", alpha=0.9)
    ax1.set_yscale("log")
    ax1.set_title("Category-summed discrete-space long tail")
    ax1.set_ylabel("Raw theoretical sample count (log scale)")
    ax1.set_xticks(x, labels, rotation=65, ha="right", fontsize=8)
    ax1.grid(axis="y", which="both", alpha=0.2)
    ax1b = ax1.twinx()
    ax1b.plot(x, cumulative, color="#D1495B", marker="o", linewidth=1.5, markersize=3)
    ax1b.set_ylim(0, 105)
    ax1b.set_ylabel("Cumulative share (%)", color="#D1495B")
    ax1b.tick_params(axis="y", colors="#D1495B")

    tx = list(range(1, len(template_values) + 1))
    ax2.scatter(tx, template_values, s=10, alpha=0.55, color="#2A9D8F")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("Per-template ranked discrete-space tail")
    ax2.set_xlabel("Template rank (descending, log scale)")
    ax2.set_ylabel("Raw theoretical sample count (log scale)")
    ax2.grid(which="both", alpha=0.2)
    fig.suptitle("Articraft template discrete-space statistics", fontsize=15)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "long_tail_distribution.png", dpi=180, bbox_inches="tight")
    fig.savefig(OUT_DIR / "long_tail_distribution.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(REPO))
    from agent.template_registry import TEMPLATE_REGISTRY

    slugs = sorted(p.stem for p in TEMPLATE_DIR.glob("*.py") if not p.name.startswith("_"))
    rows: list[dict[str, Any]] = []
    workers = min(8, max(1, os.cpu_count() or 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_measure_one, slug): slug for slug in slugs}
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: row["slug"])
    supermap = _load_big_category_map()
    for row in rows:
        _attach_category(row, TEMPLATE_REGISTRY, supermap)

    detail_fields = [
        "slug", "registry_stem", "big_category", "category_basis", "status", "domain_status", "method",
        "core_domain_theoretical", "raw_domain_theoretical", "reachable_discrete_combos",
        "probe_seeds_used", "probe_errors", "probe_saturated", "axis_count", "axis_summary", "error",
    ]
    _write_csv(OUT_DIR / "template_discrete_space.csv", rows, detail_fields)
    axis_rows = []
    for row in rows:
        for axis in row.get("axes", []):
            axis_rows.append({
                "slug": row["slug"], "big_category": row["big_category"], "domain_status": row["domain_status"],
                "method": row["method"], "axis_name": axis["name"], "axis_kind": axis["kind"],
                "value_count": axis["value_count"], "values": "|".join(axis["values"]),
            })
    _write_csv(OUT_DIR / "template_discrete_axes.csv", axis_rows,
               ["slug", "big_category", "domain_status", "method", "axis_name", "axis_kind", "value_count", "values"])

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["big_category"]].append(row)
    summary: list[dict[str, Any]] = []
    for group, members in grouped.items():
        cores = [int(row["core_domain_theoretical"]) for row in members]
        raws = [int(row["raw_domain_theoretical"]) for row in members]
        summary.append({
            "big_category": group,
            "template_count": len(members),
            "core_domain_sum": sum(cores),
            "raw_domain_sum": sum(raws),
            "max_raw_domain": max(raws),
            "median_raw_domain": sorted(raws)[len(raws) // 2],
            "declared_template_count": sum(row["domain_status"] == "declared" for row in members),
            "legacy_template_count": sum(row["domain_status"] == "legacy" for row in members),
            "error_template_count": sum(row["status"] != "ok" for row in members),
        })
    summary.sort(key=lambda row: row["raw_domain_sum"], reverse=True)
    _write_csv(OUT_DIR / "category_discrete_space_summary.csv", summary,
               ["big_category", "template_count", "core_domain_sum", "raw_domain_sum", "max_raw_domain",
                "median_raw_domain", "declared_template_count", "legacy_template_count", "error_template_count"])
    _make_plot(rows, summary)

    total_core = sum(int(row["core_domain_theoretical"]) for row in rows)
    total_raw = sum(int(row["raw_domain_theoretical"]) for row in rows)
    errors = [row for row in rows if row["status"] != "ok"]
    report = f"""# 模板离散空间统计

统计对象：`agent/templates` 下 {len(rows)} 个可导入 `.py` 模板。

## 口径

- `core_domain_theoretical`：不含 multiplicity/N 的结构槽位笛卡尔积。
- `raw_domain_theoretical`：结构槽位乘以 multiplicity/N 取值后的笛卡尔积。
- 调色板、颜色、材质、表面 finish/texture 和连续数值参数不计入离散空间。
- 有 `TEMPLATE_DOMAIN` 的模板使用 SDK `TemplateDomain.audit()` 的精确声明值。
- legacy 模板使用其 `slot_choices_for_seed(seed)` 采样面扫描最多 {PROBE_SEEDS} 个 seed；连续 {PROBE_PATIENCE} 个 seed 未产生新离散 tuple 时提前停止。理论值是扫描得到的有限轴取值数的笛卡尔积；`reachable_discrete_combos` 单列记录实际可达 tuple 数，便于识别 legacy 轴相关性。
- 本次 425 个 legacy 模板中有 {sum(row['probe_saturated'] is False for row in rows if row['domain_status'] == 'legacy')} 个在 {PROBE_SEEDS}-seed 上限内未达到饱和条件；这些行的理论值应视为当前探测范围内的测量值/上界候选，可由 `probe_saturated` 和 `probe_seeds_used` 复核。
- 汇总表是把明细表中每一个模板已经测出的数值按 `big_category` 求和，未从模板总量倒推。
- 大类优先使用 `data/supercategories.json` 的 category→supercategory 映射；未匹配的模板使用可复现的文件名前缀/语义关键词兜底，并在明细表中以 `category_basis` 标出。

## 总览

- 模板数：{len(rows)}
- `core_domain_theoretical` 合计：{total_core:,}
- `raw_domain_theoretical` 合计：{total_raw:,}
- 正式声明域模板：{sum(row['domain_status'] == 'declared' for row in rows)}
- legacy 推导模板：{sum(row['domain_status'] == 'legacy' for row in rows)}
- 测量错误：{len(errors)}

## 文件

- `template_discrete_space.csv`：每模板明细。
- `template_discrete_axes.csv`：每模板每个离散轴及取值。
- `category_discrete_space_summary.csv`：按大类汇总后的合计和长尾排序。
- `long_tail_distribution.png` / `.svg`：左图为大类求和长尾，右图为单模板排序长尾；纵轴均为对数轴。
"""
    (OUT_DIR / "README.md").write_text(report, encoding="utf-8")
    print(json.dumps({"templates": len(rows), "total_core": total_core, "total_raw": total_raw, "errors": len(errors), "output": str(OUT_DIR)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
