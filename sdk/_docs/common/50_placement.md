# Placement Helpers

## Purpose

Use these helpers when one thing needs to be aligned, mounted, or wrapped
relative to another.

## Import

```python
from sdk import (
    ArticulationType,
    AxisInterface,
    PlaneInterface,
    align_centers,
    mate_axes,
    mate_planes,
    place_on_surface,
    place_on_face,
    place_on_face_uv,
    proud_for_flush_mount,
    surface_frame,
    register_interface_mate,
    wrap_mesh_onto_surface,
    wrap_profile_onto_surface,
)
```

## Recommended APIs

| Intent | Helper |
| --- | --- |
| Align centers along selected axes | `align_centers(...)` |
| Mate two component mounting planes | `PlaneInterface`, `mate_planes(...)` |
| Mate shafts, wheels, or hinges coaxially | `AxisInterface`, `mate_axes(...)` |
| Mount a rigid child onto a target surface | `place_on_surface(...)` |
| Mount on a box-like face | `place_on_face(...)`, `place_on_face_uv(...)` |
| Compute flush-mount offset | `proud_for_flush_mount(...)` |
| Query a surface point and tangent frame | `surface_frame(...)` |
| Wrap existing mesh geometry onto curvature | `wrap_mesh_onto_surface(...)` |
| Wrap a 2D profile with thickness onto curvature | `wrap_profile_onto_surface(...)` |

## Subject Conventions

These helpers use a few shared input conventions:

- `Part`: uses the union of its visuals by default
- `Visual`: uses that visual only
- `Box`, `Cylinder`, `Sphere`, `Mesh`: uses the geometry directly
- `MeshGeometry`: accepted by wrapping helpers

`place_on_face(...)` and `proud_for_flush_mount(...)` require a `Part`.

## Alignment

### `align_centers(...)`

```python
align_centers(
    child_aabb,
    parent_aabb,
    *,
    axes=("x", "y", "z"),
) -> Origin
```

- `child_aabb`, `parent_aabb`: `(min_xyz, max_xyz)` AABB pairs.
- `axes`: one axis, a compact string such as `"xy"`, or an iterable of axis
  names.
- Returns an `Origin` whose translation aligns the chosen center coordinates.

## Face-Based Mounting

### `place_on_face(...)`

```python
place_on_face(
    parent_link: Part,
    face: str,
    *,
    face_pos: tuple[float, float] = (0.0, 0.0),
    proud: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> Origin
```

- `parent_link`: box-like parent part.
- `face`: one of `"+x"`, `"-x"`, `"+y"`, `"-y"`, `"+z"`, `"-z"`.
- `face_pos`: local face-plane offset in meters.
- `proud`: offset outward from the chosen face normal.
- Returns a rigid `Origin`.

`face_pos` is expressed in parent-face tangent coordinates, while the returned
child frame uses a deterministic right-handed basis per face:

| Face | `face_pos` axes | Child `+X` | Child `+Y` | Child `+Z` |
| --- | --- | --- | --- | --- |
| `+x` | `(parent +Y, parent +Z)` | `parent -Z` | `parent +Y` | `parent +X` |
| `-x` | `(parent +Y, parent +Z)` | `parent +Z` | `parent +Y` | `parent -X` |
| `+y` | `(parent +X, parent +Z)` | `parent +X` | `parent -Z` | `parent +Y` |
| `-y` | `(parent +X, parent +Z)` | `parent +X` | `parent +Z` | `parent -Y` |
| `+z` | `(parent +X, parent +Y)` | `parent +X` | `parent +Y` | `parent +Z` |
| `-z` | `(parent +X, parent +Y)` | `parent +X` | `parent -Y` | `parent -Z` |

### `place_on_face_uv(...)`

```python
place_on_face_uv(
    parent_link: Part,
    face: str,
    *,
    uv: tuple[float, float] = (0.5, 0.5),
    uv_margin: float | tuple[float, float] = 0.0,
    proud: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> Origin
```

- `uv`: normalized face coordinates in `[0, 1]`.
- `uv_margin`: inward margin, either one float or per-axis pair.
- `uv` follows the same face tangent axes as `face_pos`.
- Returns a rigid `Origin`.

### `proud_for_flush_mount(...)`

```python
proud_for_flush_mount(
    child_link: Part,
    *,
    axis: str = "z",
    clearance: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = True,
) -> float
```

- Returns the outward offset that keeps a centered child flush instead of
  half-embedded when used with `place_on_face(...)`.
- `axis`: child local thickness axis, one of `"x"`, `"y"`, or `"z"`.
- `clearance`: extra positive stand-off in meters.

## Surface Queries

### `surface_frame(...)`

```python
surface_frame(
    target,
    *,
    point_hint=None,
    direction=None,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> SurfaceFrame
```

```python
SurfaceFrame(
    point: tuple[float, float, float],
    normal: tuple[float, float, float],
    tangent_u: tuple[float, float, float],
    tangent_v: tuple[float, float, float],
)
```

- Provide exactly one of `point_hint` or `direction`.
- `point_hint`: world-space point near the target region of interest.
- `direction`: outward direction from the target's rough center.
- `up_hint`: preferred world-space up direction used when building tangents.
- Returns the hit point, normal, and tangent basis.

## Rigid Surface Mounting

### `place_on_surface(...)`

```python
place_on_surface(
    child,
    target,
    *,
    point_hint=None,
    direction=None,
    child_axis: str = "+z",
    clearance: float = 0.0,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    child_prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> Origin
```

- `child_axis`: child local axis that should point outward from the target
  surface, for example `"+z"` or `"-y"`.
- `clearance`: extra stand-off along the surface normal in meters.
- `spin`: extra rotation around the surface normal in radians.
- Returns a rigid `Origin`.

## Conformal Surface Wrapping

### `wrap_mesh_onto_surface(...)`

```python
wrap_mesh_onto_surface(
    mesh,
    target,
    *,
    point_hint=None,
    direction=None,
    child_axis: str = "+z",
    visible_relief: float = 0.0,
    mapping: str = "auto",
    surface_max_edge: float | None = None,
    max_edge: float | None = None,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> MeshGeometry
```

- `mesh`: `MeshGeometry` or `Mesh`.
- `target`: wrap target.
- `visible_relief`: offset the visible face outward from the target in meters.
- `mapping`:
  - `"auto"`: prefer intrinsic sphere/cylinder wrapping, else nearest-surface
  - `"intrinsic"`: require intrinsic sphere/cylinder wrapping
  - `"nearest"`: always use nearest-surface projection
- `surface_max_edge` / `max_edge`: optional pre-wrap subdivision target. Use
  only one name.

Returns baked `MeshGeometry`.

### `wrap_profile_onto_surface(...)`

```python
wrap_profile_onto_surface(
    profile,
    target,
    *,
    thickness: float,
    hole_profiles=(),
    point_hint=None,
    direction=None,
    visible_relief: float = 0.0,
    mapping: str = "auto",
    surface_max_edge: float | None = None,
    max_edge: float | None = None,
    spin: float = 0.0,
    asset_root=None,
    prefer_collisions: bool = False,
    up_hint=(0.0, 0.0, 1.0),
) -> MeshGeometry
```

- `profile`: 2D outer loop in local XY.
- `thickness`: positive thickness in meters.
- `hole_profiles`: optional 2D through-cut loops.
- The visible face is treated as local `z=0`; thickness extends inward along
  local `-z`.

Returns baked `MeshGeometry`.

## Lightweight Component Interfaces

Use interfaces when both components expose an explicit assembly boundary. They
are small local-coordinate declarations, not component manifests or an
assembly solver.

### Planar interfaces

```python
host = PlaneInterface(
    name="housing.sloped_face",
    point=(0.0, -0.03, 0.01),
    normal=(0.0, -0.95, -0.31),
    tangent_u=(1.0, 0.0, 0.0),
    extent=(0.12, 0.10),
)
dial = PlaneInterface(
    name="dial.back",
    normal=(0.0, 1.0, 0.0),
    tangent_u=(1.0, 0.0, 0.0),
    extent=(0.07, 0.07),
)
mount = mate_planes(host, dial, gap=0.0002)
```

`mate_planes` aligns the consumer plane against the provider plane, including
inclined faces. When both extents are declared it also rejects a footprint that
does not fit the host.

### Axis interfaces

```python
fork_axis = AxisInterface(
    name="fork.axle",
    point=(0.0, 0.0, 0.04),
    axis=(1.0, 0.0, 0.0),
    radius=0.006,
)
wheel_axis = AxisInterface(
    name="wheel.spin",
    axis=(1.0, 0.0, 0.0),
    radius=0.004,
)
mount = mate_axes(
    fork_axis,
    wheel_axis,
    require_fit=True,
    radial_clearance=0.0005,
)
joint = model.articulation(
    "wheel_spin",
    ArticulationType.CONTINUOUS,
    fork,
    wheel,
    origin=mount.origin,
    axis=mount.axis,
)
register_interface_mate(model, joint.name, mount)
```

For revolute or continuous motion, the consumer axis line must pass through the
child-frame origin. Put the wheel/shaft geometry around that origin instead of
placing the joint axis on its visible surface. Registration lets baseline QC
verify both the solved origin and the actual joint axis.

## Advice

### Understanding wrapping controls

- `child_axis` says which local axis is the visible outward-facing direction.
- `mapping="intrinsic"` is appropriate when you care about shape preservation on
  spheres or cylinder sidewalls.
- Lower `surface_max_edge` when a wrapped result is visibly cutting chords
  through a curved surface.
- `visible_relief` is for small stand-off, not large rigid spacing.
- Use `place_on_surface` when the host surface is discovered from geometry;
  use `PlaneInterface`/`mate_planes` when both component boundaries are known.
- `mate_axes` establishes coaxial placement; motion sweep collision checks are
  still responsible for proving that the surrounding fork, housing, or slot
  leaves enough clearance.

## Examples

### Face mount

```python
origin = place_on_face_uv(
    panel,
    "+z",
    uv=(0.75, 0.5),
    proud=proud_for_flush_mount(button, axis="z", clearance=0.0005),
    asset_root=HERE,
)
```

### Rigid surface mount

```python
origin = place_on_surface(
    child=button,
    target=panel,
    point_hint=(0.12, 0.0, 0.04),
    child_axis="+z",
    clearance=0.0005,
    spin=0.2,
    asset_root=HERE,
)
```

### Conformal wrap

```python
wrapped = wrap_profile_onto_surface(
    profile,
    Sphere(radius=0.09),
    thickness=0.0015,
    direction=(1.0, 0.2, 0.1),
    mapping="intrinsic",
    visible_relief=0.00005,
    surface_max_edge=0.006,
)
```

## See Also

- `20_core_types.md` for geometry descriptors and `Origin`
- `40_mesh_geometry.md` for `MeshGeometry`

## Clarifications for agent usage

- `up_hint` does more than break ties: it defines the zero-spin tangent basis by projecting the hint into the surface tangent plane. Changing `up_hint` changes what `spin=0` means.
- Angle inputs are radians and follow the right-hand rule.
- Intrinsic wrapping support is intentionally narrow: use it for spheres and cylinder sidewalls, not arbitrary cylindrical end caps or general meshes.
