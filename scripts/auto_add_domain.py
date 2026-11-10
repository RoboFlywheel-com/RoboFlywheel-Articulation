# SPDX-License-Identifier: Apache-2.0

"""Auto-insert TEMPLATE_DOMAIN into templates that lack one.

Usage: uv run python scripts/auto_add_domain.py [--dry-run] [--slug <slug>]
"""
from __future__ import annotations

import dataclasses
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FAILING_SLUGS = [
    "Container_Shipping_container", "Door_Gate", "Door_wooden_plank_door_with_a_ring_pull",
    "Headwear_Racing_helmet", "Healthcare_Wheelchair", "Industrial_Drill_press_table",
    "Other_Cabinet", "Other_Folding_screen", "Science_Dental_setup",
    "Sports_Bike", "Sports_Roller_scates", "Structure_Elevator", "Urban_Environment_utility_box",
    "barrier_gate_boom", "barrier_gate_leaf_gate", "bell_tower_with_swinging_bell",
    "bicycle_crankset_and_pedal_assembly", "blender_countertop", "box_fan_with_control_knob",
    "camera_lens", "candy_vending_machine", "cantilever_articulated_arm",
    "casino_machine", "coaxial_rotary_stack", "crane_tower", "desktop_pc_tower",
    "display_freezer_with_sliding_glass_lids", "elevator_shaft",
    "graphics_card_with_cooling_fans", "mechanical_metronome_with_pendulum",
    "paper_cutter_guillotine", "platform_cart", "refrigerator_with_hinged_doors",
    "revolving_door", "shelving_unit_with_adjustable_shelves", "simple_aframe_step_ladder",
    "singleleaf_drawbridge", "stand_mixer", "studio_lamp",
    "studio_spotlight_on_yoke", "turntable", "tv_wall_mount", "twojoint_revolute_chain",
    "wind_turbine", "wrench_set",
]

SKIP_FIELDS = {"name"}
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "agent" / "templates"


def analyze_slug(slug: str) -> dict | None:
    """Analyze a template and return its varying discrete config fields."""
    try:
        mod = importlib.import_module(f"agent.templates.{slug}")
    except Exception as e:
        return None

    cfg_fn = getattr(mod, "config_from_seed", None)
    if not cfg_fn:
        return None

    if hasattr(mod, "TEMPLATE_DOMAIN") and mod.TEMPLATE_DOMAIN is not None:
        return None  # already has one

    field_values: dict[str, set] = {}
    field_types: dict[str, set] = {}
    for seed in range(200):
        try:
            cfg = cfg_fn(seed)
        except Exception:
            continue
        for f in dataclasses.fields(cfg):
            v = getattr(cfg, f.name)
            if f.name in SKIP_FIELDS:
                continue
            try:
                field_values.setdefault(f.name, set()).add(v)
                field_types.setdefault(f.name, set()).add(type(v).__name__)
            except TypeError:
                continue

    slots = {}
    for name, vals in field_values.items():
        if len(vals) <= 1:
            continue
        types = field_types.get(name, set())
        if types == {"float"} and len(vals) > 15:
            continue
        if types <= {"str", "int", "bool"}:
            slots[name] = sorted(vals, key=str)
        elif types == {"tuple"} and len(vals) <= 6:
            if all(all(isinstance(x, (int, float)) for x in v) for v in vals):
                slots[name] = sorted(vals, key=str)

    if not slots:
        return None
    return {"slug": slug, "slots": slots}


def generate_domain_code(slots: dict[str, list]) -> str:
    """Generate the TEMPLATE_DOMAIN code block to insert."""
    lines = []
    # Variable declarations for slot values
    for name, values in slots.items():
        var_name = f"_{name.upper()}_VALUES"
        vals_str = ", ".join(repr(v) for v in values)
        lines.append(f"{var_name} = ({vals_str},)")
    lines.append("")
    lines.append("TEMPLATE_DOMAIN = TemplateDomain(")
    lines.append("    (")
    for name in slots:
        var_name = f"_{name.upper()}_VALUES"
        lines.append(f'        component_slot("{name}", {var_name}),')
    lines.append("    )")
    lines.append(")")
    return "\n".join(lines)


def insert_domain(slug: str, domain_code: str, dry_run: bool = False) -> bool:
    """Insert TEMPLATE_DOMAIN into the template file."""
    filepath = TEMPLATE_DIR / f"{slug}.py"
    if not filepath.exists():
        print(f"  ERROR: {filepath} not found")
        return False

    content = filepath.read_text()

    # Check if already has TEMPLATE_DOMAIN
    if "TEMPLATE_DOMAIN" in content:
        print(f"  SKIP: already has TEMPLATE_DOMAIN")
        return False

    # Find the import section and add TemplateDomain import
    # Look for the last 'from sdk import' or 'from sdk import (' line
    import_line = None
    lines = content.split("\n")
    last_sdk_import_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("from sdk import") or line.strip().startswith("from sdk._core"):
            last_sdk_import_idx = i

    if last_sdk_import_idx == -1:
        print(f"  ERROR: no sdk import found")
        return False

    # Check if TemplateDomain is already imported
    has_domain_import = "TemplateDomain" in content[:content.find("TEMPLATE_DOMAIN") if "TEMPLATE_DOMAIN" in content else len(content)]

    # Find the insertion point: after the imports, before the first class/function
    # Look for the first '@dataclass' or 'class ' or 'def config_from_seed'
    insert_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("@dataclass") or stripped.startswith("class ") or stripped.startswith("def config_from_seed"):
            insert_idx = i
            break

    if insert_idx == -1:
        print(f"  ERROR: could not find insertion point")
        return False

    # Build the new content
    # 1. Add TemplateDomain to sdk imports if not already there
    sdk_import_line = lines[last_sdk_import_idx]
    if "TemplateDomain" not in sdk_import_line:
        if sdk_import_line.strip().startswith("from sdk import ("):
            # Multi-line import - find the closing paren
            for j in range(last_sdk_import_idx, len(lines)):
                if ")" in lines[j]:
                    # Insert before the closing paren
                    lines[j] = lines[j].rstrip()
                    if lines[j].strip() == ")":
                        lines.insert(j, "    TemplateDomain,")
                        lines.insert(j + 1, "    component_slot,")
                    else:
                        # Same line has content and )
                        lines[j] = lines[j].replace(")", "    TemplateDomain,\n    component_slot,\n)")
                    insert_idx += 2  # adjust for inserted lines
                    break
        elif sdk_import_line.strip().startswith("from sdk import"):
            # Single-line import
            if "(" in sdk_import_line:
                lines[last_sdk_import_idx] = sdk_import_line.rstrip() + ", TemplateDomain, component_slot"
            else:
                lines[last_sdk_import_idx] = sdk_import_line.rstrip() + ", TemplateDomain, component_slot"

    # 2. Insert the domain code before the first class/function
    domain_lines = ["", domain_code, ""]
    for j, dl in enumerate(domain_lines):
        lines.insert(insert_idx + j, dl)

    new_content = "\n".join(lines)

    if dry_run:
        print(f"  DRY-RUN: would insert at line {insert_idx}")
        return True

    filepath.write_text(new_content)
    print(f"  OK: inserted TEMPLATE_DOMAIN at line {insert_idx}")
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    target_slug = None
    for i, arg in enumerate(sys.argv):
        if arg == "--slug" and i + 1 < len(sys.argv):
            target_slug = sys.argv[i + 1]

    slugs = [target_slug] if target_slug else FAILING_SLUGS

    success = 0
    skipped = 0
    failed = 0

    for slug in slugs:
        print(f"\n{'='*60}")
        print(f"Processing: {slug}")
        analysis = analyze_slug(slug)
        if analysis is None:
            print(f"  SKIP: no varying discrete fields or already has domain")
            skipped += 1
            continue

        slots = analysis["slots"]
        print(f"  Found {len(slots)} slots:")
        for name, vals in slots.items():
            print(f"    {name}: {len(vals)} values")

        domain_code = generate_domain_code(slots)
        if insert_domain(slug, domain_code, dry_run=dry_run):
            success += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Summary: {success} done, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
