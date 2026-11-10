# Controlled Morphology Capability Matrix

This matrix records generator capabilities from source code, not from the asset corpus under
`/data`. Ranges describe `resolve_config()` behavior in the task-owned copies.

## Intervention Semantics

"One variable at a time" applies to the explicit intervention, not to every resulting mesh
dimension. For example, changing `carcass_width_m` deterministically changes the opening, door
panel, shelf, handle position, and door sweep radius. This is an accepted controlled slice as long
as the upstream intervention is explicit, unrelated inputs remain fixed, and all descendants are
recorded. Each generated `parameters.json` therefore contains both the requested/resolved Config
and a compact `morphology` section with task-relevant derived measurements.

The machine-readable version of this contract is emitted by each generator's `variable_space()`
and can be inspected with:

```bash
.venv/bin/python -m controlled_morphology.pipeline \
  --describe-generator single_door_cabinet
```

## Active Generators

| Family | Task generator | Source template | Canonical motion |
|---|---|---|---|
| Single side-hinged cabinet | `generators/single_door_cabinet.py` | `agent/templates/pictureX_0611_Cabinet_with_doors.py` | one revolute joint about `+Z` |
| Single drawer cabinet | `generators/single_drawer_cabinet.py` | `agent/templates/pictureX_0611_kitchen_cabinet.py` | one prismatic joint along `-Y` |
| Multi side-hinged cabinet | `generators/multi_door_cabinet.py` | `agent/templates/pictureX_0611_Cabinet_with_doors.py` | 1–4 revolute joints about `+Z` |
| Multi drawer cabinet | `generators/multi_drawer_cabinet.py` | `agent/templates/drawer_cabinet_with_sliding_drawers.py` | 1–6 prismatic joints along `-Y` |
| Matched kitchen access | `generators/kitchen_cabinet_access.py` | `agent/templates/pictureX_0611_kitchen_cabinet.py` | one `+Z` side hinge or one `+X` top hinge |

The source templates remain unchanged. Task-facing builders reject configurations that would
change the canonical joint type or movable-part count.

## Single Door Controls

| Variable | Type / resolved range | Intervention mode | Coupling or constraint |
|---|---|---|---|
| `hinge_side` | `left`, `right` | Exact | Mirrors hinge, leaf extension, handle location, joint limits, and opening sign as one coherent handedness change. |
| `handle_type` | `bar`, `knob` | Exact | Orientation and length are inactive for a knob. |
| `handle_orientation_rad` | `[0, pi)` | Exact inside range | A bar line is pi-periodic; out-of-range input is normalized and therefore rejected by strict controlled specs. |
| `handle_length_m` | nominal `[0.040, 0.320]` | Exact when it fits | Upper bound decreases with leaf dimensions, orientation, and handle thickness. |
| `handle_thickness_m` | nominal `[0.006, 0.040]` | Exact when it fits | Upper bound also depends on leaf size. |
| `handle_clearance_m` | `[0.010, 0.080]` | Exact inside range | Defined as the net gap from the front envelope to the nearest grip surface. |
| `handle_hinge_distance_ratio` | geometry-dependent subset of `[0, 1]` | Exact when it fits | Ratio uses distances projected along the leaf-width direction; projected bar extent must stay on the leaf. |
| `handle_vertical_position_ratio` | geometry-dependent subset of `[0, 1]` | Exact when it fits | Projected bar extent must stay between leaf bottom and top. |
| `carcass_width_m` | rect box `[0.66, 1.50]` m | Direct upstream | Changes opening, leaf and shelf width, absolute handle position, aspect ratio, and sweep radius. |
| `carcass_depth_m` | rect box `[0.34, 0.50]` m | Exact inside range | Does not change the controlled door topology. |
| `carcass_height_m` | rect box `[0.92, 1.80]` m | Direct upstream | Changes opening and leaf height, aspect ratio, absolute handle position, and handle-fit bounds. |
| `slab_t_m` | `[0.016, 0.032]` m | Exact for `flush_slab` | Other door styles use their authored thickness. |
| `door_swing_rad` | `[1.40, 1.92]` rad | Exact inside range | Left hinge opens at the negative limit; right hinge opens at the positive limit. |

Canonical fixed fields are `rect_box`, `flush_slab`, `revolute_swing`, `recessed_plinth`, one
door, one shelf, and palette 0. The first pilot varies handle orientation, normalized
hinge distance, and carcass width.

For a canonical single door, metadata also records resolved panel width/height/thickness, both
explicit aspect-ratio conventions, hinge-to-free-edge distance, panel XY envelope sweep radius,
projected handle hinge distance, and handle-centre sweep radius. Width and height are currently
derived from the carcass/opening layout rather than exposed as unrelated floating panels; this is
intentional structural coupling.

## Single Drawer Controls

| Variable | Type / resolved range | Independent-control status | Coupling or constraint |
|---|---|---|---|
| `handle_type` | `bar`, `knob` | Exact | Orientation and length are inactive for a knob. |
| `handle_orientation_rad` | `[0, pi)` | Exact inside range | A bar line is pi-periodic. |
| `handle_length_m` | nominal `[0.040, 0.320]` | Exact when it fits | Maximum depends on front width, front height, orientation, and thickness. |
| `handle_thickness_m` | nominal `[0.008, 0.032]` | Exact when it fits | Must leave a 12 mm panel-edge margin. |
| `handle_clearance_m` | `[0.008, 0.080]` | Exact inside range | Net gap from panel plane to grip back surface. |
| `handle_horizontal_position_ratio` | geometry-dependent subset of `[0, 1]` | Exact when it fits | Centre is projected into the fit-safe interval. |
| `handle_vertical_position_ratio` | geometry-dependent subset of `[0, 1]` | Exact when it fits | Centre is projected into the fit-safe interval. |
| `carcass_width_m` | base cabinet `[0.48, 0.78]` m | Exact inside range | Plinth-deck form allows up to 0.86 m. |
| `carcass_depth_m` | `[0.50, 0.62]` m | Exact inside range | Changes physical drawer depth and therefore travel. |
| `carcass_height_m` | `[0.62, 0.82]` m | Exact inside range | Changes the single drawer-front height. |
| `drawer_travel_ratio` | `[0.34, 0.60]` | Exact ratio | Actual joint travel is this ratio times derived tray depth and is recorded explicitly. Values above 0.60 are rejected as controlled levels instead of silently producing duplicate motion. |

Canonical fixed fields are `base_cabinet`, `drawer_stack`, `flat_panel`, `laminate_worktop`,
`adjustable_legs`, one access unit, one shelf, and palette 0.

The task-facing single-drawer entry may also replace the cabinet body, face, worktop, and support
base while retaining one drawer joint. Its metadata records opening and front dimensions, front
aspect ratio, tray dimensions, requested/effective travel ratio, and absolute joint travel.

## First-Priority Coverage

| Design-table item | Current status | Intended use |
|---|---|---|
| Handle type, orientation, length, thickness, clearance | Direct controls for both active generators | P0 OAT slices; bar-only parameters are marked inactive for knobs. |
| Normalized handle-to-hinge distance | Direct fit-constrained door control | P0 door slice; absolute projected distance is derived and recorded. |
| Hinge side and opening sign | Direct handedness intervention plus derived sign/limits | P0 mirror slice. |
| Door panel width, height, thickness, aspect ratio | Thickness direct; width/height derived from explicit carcass dimensions | P0 coupled structural slice with resolved panel outcomes recorded. |
| Joint range | Direct door angle and drawer travel controls | P1 task-length slice. |
| Single/double door or movable-part count | Direct 1–4 door and 1–6 drawer controls in independent multi-target generators | P1 topology groups, separate from the single-target P0 entries. |
| Vertical side hinge / horizontal flap | Matched categorical control in the independent kitchen-access generator | P1 mechanism group; host/front/handle inputs and canonical 1.40 rad range stay fixed. |
| Material, color, texture | Out of scope | P2 is intentionally excluded from this project, now and later. |

## Other Relevant Source Generators

| Group | Templates | Why not in the first controlled slice |
|---|---|---|
| Alternative multi-drawer cabinet | `pictureX_0611_Cabinet_with_drawers.py` | The active P1 generator uses the richer explicit layouts from `drawer_cabinet_with_sliding_drawers.py`. |
| Single-drawer desk | `desk_with_drawer.py`, `pictureX_0611_Desk_with_drawers_no_door.py` | Can emit one drawer and useful pull categories, but changes the task host from cabinet to desk. |
| Explicit handed cabinet | `round_cabinet.py` | Already exposes handedness, but its side-door profile also includes several drawers. |
| Door/drawer compound | `pictureX_0611_Cabinet_with_doors_and_drawers.py`, `office_table_with_doors_or_drawers.py`, `table_with_doors_and_drawers.py` | Multiple target candidates and joint types confound a first one-variable causal slice. |
| Larger storage furniture | `tv_cabinet.py`, `wine_cabinet*.py`, `pictureX_0611_Hutch_Cabinet.py`, `storage_cart_with_drawers_on_wheels.py` | Multiple movable parts and topology-specific task semantics. |

The copied family builders implement deterministic component replacement and repeated parts.
The registry keeps P0 single-target entries separate from P1 topology entries. Multi-drawer P1
supports explicit full-width, paired-grid, and pair-over-full-width layouts; multi-door layout is
authored deterministically by the door family. Per-part parameters and mixed door/drawer layouts
remain outside the first 45-asset pilot.

## Qualification Boundary

The default generation path intentionally stays light: generator tests, compilation, and URDF /
metadata consistency. Motion QC is optional. P2 appearance variation and `appearance.json` are
permanently out of scope. The copied generators also do not author moving-link mass/inertia;
standardized physics needed by a later manipulation protocol is downstream evaluation setup, not
an asset variation axis in this pipeline.
