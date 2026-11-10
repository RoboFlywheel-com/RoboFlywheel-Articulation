# SPDX-License-Identifier: Apache-2.0

"""Auto-generate TEMPLATE_DOMAIN for templates that lack one."""
import dataclasses
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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

# Fields to always skip
SKIP_FIELDS = {"name"}

def analyze_slug(slug: str) -> dict | None:
    """Analyze a template and return its varying discrete config fields."""
    try:
        mod = importlib.import_module(f"agent.templates.{slug}")
    except Exception as e:
        return {"slug": slug, "error": f"import failed: {e}"}

    cfg_fn = getattr(mod, "config_from_seed", None)
    if not cfg_fn:
        return {"slug": slug, "error": "no config_from_seed"}

    # Check if already has TEMPLATE_DOMAIN
    if hasattr(mod, "TEMPLATE_DOMAIN") and mod.TEMPLATE_DOMAIN is not None:
        return {"slug": slug, "error": "already has TEMPLATE_DOMAIN"}

    # Collect values over 200 seeds
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
            # Skip unhashable types (dicts, lists)
            try:
                field_values.setdefault(f.name, set()).add(v)
            except TypeError:
                continue
            field_types.setdefault(f.name, set()).add(type(v).__name__)

    # Find varying discrete fields
    slots = {}
    for name, vals in field_values.items():
        if len(vals) <= 1:
            continue
        types = field_types[name]
        # Skip continuous floats (many distinct values)
        if types == {"float"} and len(vals) > 15:
            continue
        # Only include str, int, bool, or small tuples
        if types <= {"str", "int", "bool"}:
            slots[name] = sorted(vals, key=str)
        elif types == {"tuple"} and len(vals) <= 10:
            # Small tuple sets (like elevation ranges) - include if all ints
            if all(all(isinstance(x, (int, float)) for x in v) for v in vals):
                if len(vals) <= 6:
                    slots[name] = sorted(vals, key=str)

    if not slots:
        return {"slug": slug, "error": "no varying discrete fields found"}

    return {"slug": slug, "slots": slots}


def generate_domain_code(analysis: dict) -> str:
    """Generate the TEMPLATE_DOMAIN code block."""
    slug = analysis["slug"]
    slots = analysis["slots"]

    lines = []
    lines.append("from sdk import TemplateDomain, component_slot")
    lines.append("")
    lines.append("")

    # Generate slot tuples
    slot_names = []
    for name, values in slots.items():
        var_name = f"_{name.upper()}_VALUES"
        vals_str = ", ".join(repr(v) for v in values)
        lines.append(f"{var_name} = ({vals_str},)")
        slot_names.append((name, var_name))

    lines.append("")
    lines.append("TEMPLATE_DOMAIN = TemplateDomain(")
    lines.append("    (")
    for name, var_name in slot_names:
        lines.append(f"        component_slot(\"{name}\", {var_name}),")
    lines.append("    )")
    lines.append(")")
    lines.append("")

    return "\n".join(lines)


def main():
    results = []
    for slug in FAILING_SLUGS:
        analysis = analyze_slug(slug)
        if analysis and "error" in analysis:
            results.append(f"SKIP {slug}: {analysis['error']}")
            continue
        if analysis:
            results.append(f"OK {slug}: {len(analysis['slots'])} slots")
            for name, vals in analysis["slots"].items():
                results.append(f"    {name}: {vals}")
    print("\n".join(results))


if __name__ == "__main__":
    main()
