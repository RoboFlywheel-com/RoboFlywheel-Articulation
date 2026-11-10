# Brackets and Mounts

## Purpose

Use these helpers for bracket-like members with a clear mounting logic:
clevises, forks, and yokes with real thickness, openings, and pin/trunnion
supports.

## Import

```python
from sdk import (
    ClevisBracketGeometry,
    PivotForkGeometry,
    TrunnionYokeGeometry,
    mesh_from_geometry,
)
```

## Recommended APIs

| Shape intent | Helper |
| --- | --- |
| Pinned end bracket with two cheeks and a base | `ClevisBracketGeometry` |
| Open-front fork that needs front insertion clearance | `PivotForkGeometry` |
| Yoke that cradles a rotating trunnion or barrel | `TrunnionYokeGeometry` |

## API Reference

### `ClevisBracketGeometry`

```python
ClevisBracketGeometry(
    overall_size,
    *,
    gap_width,
    bore_diameter,
    bore_center_z,
    base_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- Builds a U-shaped clevis with a bottom base and a transverse bore.
- `overall_size`: `(width_x, depth_y, height_z)`.
- `gap_width` is the clear spacing between the cheeks.
- `bore_center_z` is measured upward from the bottom face.
- `center=False` places the bottom mounting face on `z=0`.

### `PivotForkGeometry`

```python
PivotForkGeometry(
    overall_size,
    *,
    gap_width,
    bore_diameter,
    bore_center_z,
    bridge_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- Builds an open-front fork with two tines and a rear bridge.
- `overall_size`: `(width_x, depth_y, height_z)`.
- `gap_width` is the clear spacing between the tines.
- `bridge_thickness` is the rear connecting bridge thickness along local `Y`.
- `bore_center_z` is measured upward from the bottom face.

### `TrunnionYokeGeometry`

```python
TrunnionYokeGeometry(
    overall_size,
    *,
    span_width,
    trunnion_diameter,
    trunnion_center_z,
    base_thickness,
    corner_radius: float = 0.0,
    center: bool = True,
)
```

- Builds a trunnion support yoke with cheek-mounted trunnion bores.
- `overall_size`: `(width_x, depth_y, height_z)`.
- `span_width` is the clear opening between the cheeks.
- `trunnion_center_z` is measured upward from the bottom face.
- `center=False` places the base on `z=0`.

## Advice

- Use these helpers when the bracket should read as one real member with
  usable mounting geometry, not a decorative placeholder.
- Preserve actual insertion and swing clearance. Do not close a fork or yoke
  just because a box is easier to author.
- If the feature is really a flat bent plate without a cheeked opening, use the
  lower-level mesh tools instead.

## Examples

```python
clevis = ClevisBracketGeometry(
    (0.08, 0.04, 0.06),
    gap_width=0.032,
    bore_diameter=0.012,
    bore_center_z=0.038,
    base_thickness=0.012,
)
clevis_mesh = mesh_from_geometry(clevis, "clevis")
```

```python
pivot_fork = PivotForkGeometry(
    (0.08, 0.05, 0.05),
    gap_width=0.034,
    bore_diameter=0.010,
    bore_center_z=0.028,
    bridge_thickness=0.012,
)
pivot_fork_mesh = mesh_from_geometry(pivot_fork, "pivot_fork")
```

```python
trunnion_yoke = TrunnionYokeGeometry(
    (0.12, 0.05, 0.08),
    span_width=0.060,
    trunnion_diameter=0.016,
    trunnion_center_z=0.050,
    base_thickness=0.014,
)
trunnion_yoke_mesh = mesh_from_geometry(trunnion_yoke, "trunnion_yoke")
```

## See Also

- `40_mesh_geometry.md` for lower-level extrudes and profile helpers
- `50_placement.md` for mounting bracket-backed parts onto parent bodies
