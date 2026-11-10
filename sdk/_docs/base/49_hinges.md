# Hinges

## Purpose

Use these helpers for exposed utility hinges that should show real leaves,
knuckles, and pin geometry.

## Import

```python
from sdk import (
    BarrelHingeGeometry,
    PianoHingeGeometry,
    HingeHolePattern,
    HingePinStyle,
    hinged_panel,
    mesh_from_geometry,
)
```

## Recommended APIs

| Shape intent | Helper |
| --- | --- |
| Exposed two-leaf utility hinge | `BarrelHingeGeometry` |
| Continuous hinge strip | `PianoHingeGeometry` |
| Leaf hole pattern | `HingeHolePattern` |
| Visible pin-end detail | `HingePinStyle` |
| Safe revolute panel motion | `hinged_panel` |

## API Reference

### `BarrelHingeGeometry`

```python
BarrelHingeGeometry(
    length,
    *,
    leaf_width_a,
    leaf_width_b=None,
    leaf_thickness,
    pin_diameter,
    knuckle_outer_diameter=None,
    knuckle_count: int = 5,
    clearance: float = 0.0005,
    open_angle_deg: float = 180.0,
    holes_a: HingeHolePattern | None = None,
    holes_b: HingeHolePattern | None = None,
    pin: HingePinStyle | None = None,
    center: bool = True,
)
```

- Builds an exposed two-leaf barrel hinge around a local `Z` pin axis.
- `center=False` places the lower end on `z=0`.
- Use `HingeHolePattern` for round or slotted leaf holes and `HingePinStyle`
  for visible pin-head variants.

### `PianoHingeGeometry`

```python
PianoHingeGeometry(
    length,
    *,
    leaf_width_a,
    leaf_width_b=None,
    leaf_thickness,
    pin_diameter,
    knuckle_pitch,
    clearance: float = 0.0005,
    open_angle_deg: float = 180.0,
    holes_a: HingeHolePattern | None = None,
    holes_b: HingeHolePattern | None = None,
    pin: HingePinStyle | None = None,
    center: bool = True,
)
```

- Builds a continuous hinge strip around a local `Z` pin axis.
- `knuckle_pitch` controls the repeating hinge pattern along the strip.
- `center=False` places the lower end on `z=0`.

### `hinged_panel`

```python
hinged_panel(
    model,
    *,
    joint_name,
    parent,
    panel,
    hinge_origin,
    axis,
    open_toward,
    max_open=math.radians(110),
    margin=0.008,
    keepout=None,
    allowed_pairs=None,
    solve_clearance=True,
)
```

- Creates the revolute articulation after the panel geometry exists.
- Rejects a hinge axis whose positive motion does not move the panel toward
  the declared world-frame `open_toward` direction.
- Uses the SDK clearance solver to reduce `max_open` when surrounding geometry
  limits the safe swept range.
- This helper controls kinematics only; visible leaves, knuckles, pins, and
  category-specific panel geometry remain the template's responsibility.

## Advice

- Use the geometry helpers only for visible utility hinges. `hinged_panel`
  also applies to concealed hinges because it governs motion, not appearance.
  Model custom multi-link hinge geometry directly.
- Preserve real knuckle/pin logic. Do not replace a visible hinge with two flat
  plates and a decorative cylinder.

## Examples

```python
barrel_hinge = BarrelHingeGeometry(
    0.090,
    leaf_width_a=0.024,
    leaf_width_b=0.020,
    leaf_thickness=0.0024,
    pin_diameter=0.003,
    holes_a=HingeHolePattern(style="round", count=3, diameter=0.0032, edge_margin=0.010),
    holes_b=HingeHolePattern(style="slotted", count=2, slot_size=(0.007, 0.003), edge_margin=0.012),
)
barrel_hinge_mesh = mesh_from_geometry(barrel_hinge, "barrel_hinge")
```

```python
piano_hinge = PianoHingeGeometry(
    0.180,
    leaf_width_a=0.016,
    leaf_width_b=0.014,
    leaf_thickness=0.0018,
    pin_diameter=0.0025,
    knuckle_pitch=0.012,
)
piano_hinge_mesh = mesh_from_geometry(piano_hinge, "piano_hinge")
```

## See Also

- `40_mesh_geometry.md` for lower-level mesh construction helpers
