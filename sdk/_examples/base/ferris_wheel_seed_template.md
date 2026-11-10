# Seeded Ferris Wheel Template

This example shows the low-token Ferris wheel generation pattern: keep the
mechanical contract fixed, and change only a seed or a small config.

```python
from __future__ import annotations

from agent.templates.ferris_wheel import (
    FerrisWheelConfig,
    build_ferris_wheel,
    config_from_seed,
    run_ferris_wheel_tests,
)
from sdk import AssetContext


ASSETS = AssetContext.from_script(__file__)

# Option A: deterministic procedural variant.
CONFIG = config_from_seed(42)

# Option B: explicit config.
# CONFIG = FerrisWheelConfig(
#     num_gondolas=20,
#     spoke_count=40,
#     gondola_style="glass_capsule",
#     rim_radius=None,
#     inner_rim_radius=None,
#     axle_z=None,
# )


def build_object_model():
    return build_ferris_wheel(CONFIG, assets=ASSETS)


def run_tests():
    return run_ferris_wheel_tests(object_model, CONFIG)


object_model = build_object_model()
```

Batch-generate many seeded variants without LLM calls:

```bash
uv run articraft template batch ferris_wheel --seeds 1-20 --dry-run
uv run articraft template batch ferris_wheel --seeds 1-20
uv run articraft template batch ferris_wheel --seeds 1-20 --category-slug ferris_wheel
```

The template preserves these articulation names and ranges:

- `wheel_rotation`: `0.0` to `6.28`
- `gondola_pivot_1..N`: `-3.14` to `3.14`

`num_gondolas` may be any integer from `4` to `20`, including odd counts such as
`5`, `7`, or `9`. `config_from_seed()` also randomizes `rim_radius` in
`0.78..1.10`, `wheel_half_width`, `support_style`, and `rim_style`.
`resolve_config()` may raise `rim_radius` and `axle_z` further for dense layouts
to avoid gondola collisions, and scales the support platform with large wheels.
