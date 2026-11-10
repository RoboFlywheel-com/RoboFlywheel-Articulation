# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from agent.templates.ferris_wheel import (
    FerrisWheelConfig,
    build_ferris_wheel,
    config_from_seed,
    resolve_config,
)
from sdk import AssetContext
from sdk.v0._urdf_export import compile_object_to_urdf_xml

REPO = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO / "ferris_wheel_variant_exports"

VARIANTS: list[tuple[str, object]] = [
    (
        "01_a_frame_single_torus_open_basket",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="open_basket",
            support_style="a_frame",
            rim_style="single_torus",
            name="preview_01",
        ),
    ),
    (
        "02_truss_tower_single_torus_open_basket",
        FerrisWheelConfig(
            num_gondolas=10,
            spoke_count=20,
            gondola_style="open_basket",
            support_style="truss_tower",
            rim_style="single_torus",
            name="preview_02",
        ),
    ),
    (
        "03_truss_tower_box_cabin_double",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="box_cabin",
            support_style="truss_tower",
            rim_style="double_torus",
            name="preview_03",
        ),
    ),
    (
        "04_truss_tower_glass_capsule_double",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="glass_capsule",
            support_style="truss_tower",
            rim_style="double_torus",
            name="preview_04",
        ),
    ),
    (
        "05_a_frame_single_torus_box_cabin",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="box_cabin",
            support_style="a_frame",
            rim_style="single_torus",
            name="preview_05",
        ),
    ),
    (
        "06_a_frame_single_torus_glass_capsule",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="glass_capsule",
            support_style="a_frame",
            rim_style="single_torus",
            name="preview_06",
        ),
    ),
    (
        "07_dense_20_gondolas_glass_capsule",
        FerrisWheelConfig(
            num_gondolas=20,
            spoke_count=40,
            gondola_style="glass_capsule",
            support_style="a_frame",
            rim_style="double_torus",
            name="preview_07",
        ),
    ),
    (
        "08_sparse_4_gondolas_open_basket",
        FerrisWheelConfig(
            num_gondolas=4,
            spoke_count=8,
            gondola_style="open_basket",
            support_style="a_frame",
            rim_style="double_torus",
            name="preview_08",
        ),
    ),
    (
        "09_large_radius_110_open_basket",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="open_basket",
            support_style="a_frame",
            rim_style="double_torus",
            rim_radius=1.10,
            name="preview_09",
        ),
    ),
    (
        "10_odd_7_box_cabin",
        FerrisWheelConfig(
            num_gondolas=7,
            spoke_count=14,
            gondola_style="box_cabin",
            support_style="a_frame",
            rim_style="double_torus",
            name="preview_10",
        ),
    ),
    (
        "11_odd_7_glass_capsule",
        FerrisWheelConfig(
            num_gondolas=7,
            spoke_count=14,
            gondola_style="glass_capsule",
            support_style="a_frame",
            rim_style="double_torus",
            name="preview_11",
        ),
    ),
    (
        "12_truss_tower_fixed_open_basket",
        FerrisWheelConfig(
            num_gondolas=10,
            spoke_count=20,
            gondola_style="open_basket",
            support_style="truss_tower",
            rim_style="double_torus",
            rim_radius=0.92,
            name="preview_12",
        ),
    ),
    (
        "13_wheel_thin_095",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="open_basket",
            wheel_half_width=0.095,
            name="preview_13",
        ),
    ),
    (
        "14_wheel_thick_125",
        FerrisWheelConfig(
            num_gondolas=12,
            spoke_count=24,
            gondola_style="open_basket",
            wheel_half_width=0.125,
            name="preview_14",
        ),
    ),
    ("15_seed_42", config_from_seed(42)),
    ("16_seed_1", config_from_seed(1)),
    ("17_seed_99", config_from_seed(99)),
]

MODEL_TEMPLATE = textwrap.dedent(
    """
    from __future__ import annotations

    from agent.templates.ferris_wheel import (
        FerrisWheelConfig,
        build_ferris_wheel,
        config_from_seed,
        run_ferris_wheel_tests,
    )
    from sdk import AssetContext

    CONFIG = {config_expr}
    ASSETS = AssetContext.from_script(__file__)


    def build_object_model():
        return build_ferris_wheel(CONFIG, assets=ASSETS)


    def run_tests():
        return run_ferris_wheel_tests(object_model, CONFIG)


    object_model = build_object_model()
    """
).strip()


def _config_expr(config: FerrisWheelConfig) -> str:
    fields = []
    for key in (
        "num_gondolas",
        "spoke_count",
        "gondola_style",
        "support_style",
        "rim_style",
        "scale_mode",
        "base_style",
        "hanger_style",
        "gondola_motion_mode",
        "railing_enabled",
        "rim_radius",
        "inner_rim_radius",
        "wheel_half_width",
        "axle_z",
        "name",
    ):
        value = getattr(config, key)
        if value is None and key in {"rim_radius", "inner_rim_radius", "axle_z"}:
            continue
        if isinstance(value, str):
            fields.append(f'{key}="{value}"')
        else:
            fields.append(f"{key}={value!r}")
    return f"FerrisWheelConfig({', '.join(fields)})"


def main() -> int:
    manifest: list[dict[str, object]] = []
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    for slug, config in VARIANTS:
        variant_dir = OUT_ROOT / slug
        variant_dir.mkdir(parents=True, exist_ok=True)
        model_path = variant_dir / "model.py"
        urdf_path = variant_dir / "model.urdf"
        model_path.write_text(
            MODEL_TEMPLATE.format(config_expr=_config_expr(config)), encoding="utf-8"
        )

        assets = AssetContext(variant_dir)
        model = build_ferris_wheel(config, assets=assets)
        urdf_xml = compile_object_to_urdf_xml(
            model,
            asset_root=variant_dir,
            include_physical_collisions=False,
            validate=False,
        )
        urdf_path.write_text(urdf_xml, encoding="utf-8")
        resolved = resolve_config(config)
        manifest.append(
            {
                "slug": slug,
                "urdf": str(urdf_path),
                "model_py": str(model_path),
                "assets_dir": str(variant_dir / "assets" / "meshes"),
                "num_gondolas": resolved.num_gondolas,
                "gondola_style": resolved.gondola_style,
                "support_style": resolved.support_style,
                "rim_style": resolved.rim_style,
                "scale_mode": resolved.scale_mode,
                "base_style": resolved.base_style,
                "hanger_style": resolved.hanger_style,
                "gondola_motion_mode": resolved.gondola_motion_mode,
                "railing_enabled": resolved.railing_enabled,
                "rim_radius": round(resolved.rim_radius, 4),
                "axle_z": round(resolved.axle_z, 4),
                "wheel_half_width": resolved.wheel_half_width,
            }
        )
        print(urdf_path)

    (OUT_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nWrote {len(manifest)} URDF files under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
