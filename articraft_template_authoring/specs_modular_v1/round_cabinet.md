# round_cabinet — modular spec

```yaml
authoring_status: blocked
category_binding:
  canonical_category: Round_cabinet
  template_slug: round_cabinet
  mechanism_profile: partitioned_curved_storage
  export_namespace: Round_cabinet
source_map: ../../articraft_data/picture_expansion/template_source_maps/0611__round_cabinet.md
template_path: agent/templates/round_cabinet.py
diversity_profile: standard
```

## Category Binding

The canonical category is `Round_cabinet`; the stable CLI/template slug is `round_cabinet`, the mechanism profile is `partitioned_curved_storage`, and formal exports remain under `seed_exports/Round_cabinet`.

## Category identity

A free-standing curved storage cabinet with a D-shaped, cylindrical or oval-drum carcass. The authored source family has a partitioned facade: a curved closure occupies one quadrant while a complete curved drawer bank occupies the other. The paired-curved-door profile is structurally different and replaces the drawer bank. A plain rectangular cabinet, an open rack, a facade-only drawer or a full-width door superimposed on full-width drawers is out of category.

## Source contract

The canonical source map is `articraft_data/picture_expansion/template_source_maps/0611__round_cabinet.md`. The user approved its origin and variant records. Every ①/②/③/N candidate has exact `record/revision/model.py:Lx-Ly` evidence there. No unlisted record may enter the sampler.

## Structural slots

| slot | kind | values | source/derivation |
|---|---|---|---|
| `body_form` | ③ complete FormFamily | `d_shape`, `full_cylinder`, `oval_drum` | accepted body-form variants |
| `facade_profile` | ①+② mechanism bundle | `hinged_side_door_drawers`, `arc_slide_side_door_drawers`, `tambour_side_door_drawers`, `paired_curved_doors` | origin + accepted closure variants |
| `base_profile` | ①+② | `tapered_legs`, `rotating_pedestal` | origin + accepted pedestal variant |
| `handedness` | ③ complete mirrored bundle | `door_left`, `door_right` | accepted layout and exact host-conformal mirror |
| `drawer_count` | N | integers 2–4; forced to 0 for paired doors | observed N=2,3,4 |
| `shelf_count` | N | integers 2–6 | observed N=2,4,6; bounded interpolation N=3,5 |
| `palette_style` | ⑥ | five palettes | does not count toward structural domain |

## Slot graph and mechanism profiles

```text
carcass (grounded curved host)
├── optional pedestal CONTINUOUS about +Z
├── facade profile
│   ├── one hinged curved side door REVOLUTE + drawer_0..N PRISMATIC, or
│   ├── one annular-carrier arc-slide REVOLUTE + drawer_0..N PRISMATIC, or
│   ├── one annular-carrier tambour REVOLUTE + drawer_0..N PRISMATIC, or
│   └── two opposed curved doors REVOLUTE; no drawers
└── fixed shelves and named guides generated from the active profile
```

The curved arc-slide uses a curvature-centre REVOLUTE coordinate because a rigid curved shell changes orientation while following a concentric track. It is not represented as a tangent PRISMATIC shortcut. A real annular carrier, carrier bracket, authored top slot and lower guide make that coordinate mechanically observable without a fake central spoke.

## Form dependency contracts

| master | required consumers | blocking rule |
|---|---|---|
| footprint `{outer_r, ry_scale}` | top/base, rear shell, door shell, drawer front/bottom/sides/rear, rails, tracks and pedestal | changing a circular body to oval while leaving circular doors, frames or rails is forbidden |
| handed facade profile | closure arc, drawer arc, edge/center stiles, drawer axes, bilateral rails and guide slot | mirroring only a door or only a drawer is forbidden |
| guided closure profile | shell, annular carrier, bracket, top slot and lower guide | missing any consumer or intersecting it at closed/mid/max blocks the combination |
| drawer row profile | front, bottom, rear, both sides, two parent rails and radial joint | facade-only drawer, transverse shelf-bar or central fake guide blocks export |

## InterfaceSpec and MatingContract

| moving entity | parent accommodation | joint | limits | mating evidence |
|---|---|---|---|---|
| hinged side door | clear hinge-side boundary plus an external round thrust-bearing landing mechanically lapped into the base slab | vertical REVOLUTE | 75–108° | thrust-pad top ↔ full-height spindle bottom |
| paired doors | two clear outer hinge boundaries, recessed shelves, center seam and two external thrust-bearing landings lapped into the base slab | opposed vertical REVOLUTE | 75–108° each | each thrust-pad top ↔ its full-height spindle bottom |
| arc-slide/tambour | annular carrier slot and lower concentric guide | curvature-centre vertical REVOLUTE | arc-slide 14°; tambour 35° | lower guide ↔ curved shell plus carrier centreline |
| drawer `i` | two longitudinal side rails outside the tray wall envelope | radial PRISMATIC | 0.18–0.29 m | left rail top ↔ complete tray bottom |
| rotating pedestal | bearing plane below base slab | vertical CONTINUOUS | continuous | base underside ↔ bearing hub top |

## Swept-clearance contract

- Validate every non-FIXED joint at closed, mid and max, plus combined high-risk poses.
- Door quadrants and drawer quadrants must remain disjoint through their complete ranges.
- Drawer rails stay engaged for the full extension; the tray retains front, bottom, rear and two sides.
- The arc carrier bracket stays inside the authored top slot; its annular bearing stays above the crown without entering the rear shell or stiles.
- Shelves are generated inside the active storage quadrant and recessed from every closure envelope.
- Pedestal geometry remains below the carcass base plane for a full rotation.
- Every external hinge axis is carried by an 18 mm-radius round thrust landing.
  The axis sits 10 mm outside the nominal curved base radius, so the landing
  overlaps the structural base slab by at least 8 mm radially and 10 mm
  vertically. Mathematical tangent contact or mesh tolerance is not accepted.

## Compatibility gates

| condition | action | reason |
|---|---|---|
| `facade_profile=paired_curved_doors` | force `drawer_count=0` | accepted variant replaces the drawer bank |
| any other facade profile | require `drawer_count∈[2,4]` | accepted hybrid quadrant layout |
| `handedness` changes | regenerate every facade consumer from one master profile | prevents mismatched frame/door/drawer geometry |
| `shelf_count∈{3,5}` | allow only equal-pitch bounded interpolation | stays between approved N=2,4,6 anchors |
| any whole-part overlap allowance | reject | cannot mask moving or static penetration |

## Element allowance table

No allowance is declared. In particular, `carcass↔drawer`, `carcass↔door`, `door↔drawer`, sibling doors and `carcass↔pedestal` remain fully collision-tested. If a future real pin/bearing requires capture, it must be split into named elements and reviewed as a single exact element pair.

## Combination domain

Core structural domain:

After the oval-carrier compatibility gate, the exact core domain is
`(2 circular bodies × 4 facade profiles + 1 oval body × 2 compatible facade profiles) × 2 bases × 2 handedness = 40`.

This is below the `standard` profile floor of 48 and therefore remains blocked pending either an approved diversity exception or another mechanically valid source-backed core axis. N axes, palette and continuous dimensions do not inflate the core count. The conditional raw legal domain with drawers and shelves is 480 before palettes and continuous dimensions.

## Visual Risk

```yaml
visual_risk:
  - drawer
  - curved-fit
  - hidden-slide
  - multi-joint
required_views:
  - full closed three-quarter
  - full maximum-open three-quarter
  - door/carrier local closed-mid-max
  - drawer local closed-mid-max showing both rails and complete tray
  - paired-door local closed-mid-max
  - rotating-pedestal underside detail
```

Coverage-driven smoke must include all four facade profiles, all three body forms, both bases, both handedness values, drawer N={2,4} and shelf N={2,6}. Visual smoke/final only renders local evidence; export still requires explicit hash-bound human approval.

## Self-review and completion state

- Exact sources, category binding, FormFamily dependencies and compatibility gates: self-check complete.
- Authored sampled-collision checks: representative seeds 0–7 pass with zero overlap allowance.
- Shared-axis escalation resolved: the former 0.00004154 m tangent mesh gap was
  removed by replacing each undersized square pad with a real round thrust
  landing having ≥8 mm radial and 10 mm vertical mechanical overlap with the
  curved base slab. No allowance or category change was introduced.
- Direct authored smoke: 8/8 pass. Strict compiler smoke: 8/8 pass with no
  disconnected-island cluster. Full mechanical sweep: fast 16/16, final 36/36,
  corner 48/48 pass; no allowance, failure triage or combination triage.
- Diversity remains independently blocked: exact core 40 is below the honest
  `standard` floor 48 and still requires the user's hash-bound exception (or a
  future valid source-backed axis). Schema v3 final visual evidence and human
  approval are also pending.
- Formal seed export: blocked until all pending gates pass.
