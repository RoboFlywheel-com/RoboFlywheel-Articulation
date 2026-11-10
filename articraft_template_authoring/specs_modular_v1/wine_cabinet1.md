# wine_cabinet1 — Modular Spec v2

> Canonical source map: `articraft_data/picture_expansion/template_source_maps/0611__wine_cabinet1.md`. The user approved all 4 origins and 15 variants. This spec therefore keeps the rectangular wine-cabinet families and the quarter-round service-cabinet family in one category-bound template, but only behind explicit mechanism/profile gates.

## 元信息

| item | value |
|---|---|
| slug | `wine_cabinet1` |
| template | `agent/templates/wine_cabinet1.py` |
| `authoring_status` | `implementation_ready` |
| `__modular__` | `True` |
| canonical category | `wine_cabinet1` |
| source category | `picture/0611/wine_cabinet1` |
| source-map | `articraft_data/picture_expansion/template_source_maps/0611__wine_cabinet1.md` |
| accepted pool | 19/19 records read; S1–S19 in the source map |

## Category Binding

```yaml
category_binding:
  canonical_category: wine_cabinet1
  template_slug: wine_cabinet1
  mechanism_profile: mixed_gated_wine_storage
  export_namespace: wine_cabinet1
  legacy_cli_slugs: [wine_cabinet1]
```

Suggested registry entry (do not edit the shared registry in this change):

```json
{
  "canonical_category": "wine_cabinet1",
  "template_slug": "wine_cabinet1",
  "mechanism_profile": "mixed_gated_wine_storage",
  "export_namespace": "wine_cabinet1",
  "legacy_cli_slugs": ["wine_cabinet1"],
  "profile": "constrained",
  "structural_axes": ["body_form", "door_motion", "rack_style", "service_module"],
  "multiplicity_axes": ["door_count", "rack_count"],
  "visual_risk": ["curved_fit", "hidden_slide", "multi_joint"]
}
```

## Core identity

A grounded wine-storage/display cabinet with a complete carcass or quarter-round service shell, wine-specific horizontal/cubby/stem storage, and a mechanically supported front or service mechanism. It is not a generic cupboard, open wine rack, drawer chest, or a collection of floating door fronts. Rectangular and curved families share category identity but not attachment envelopes.

## Slots and provenance

| slot | candidates | exact accepted source |
|---|---|---|
| `body_form` (③ complete FormFamily) | `glass_front_cabinet`, `white_display_hutch`, `tall_cooler`, `low_sideboard`, `narrow_tower`, `quarter_round_corner` | S2 `L116-L388`; S3 `L146-L458`; S4 `L116-L398`; S6 `L241-L430`; S7 `L146-L363`; S1 `L151-L610` + S8 `L21-L52,L176-L590` |
| `door_motion` (②) | `hinged`, `sliding`, `bifold` | S1–S4/S9–S11; S13 `L281-L387`; S12 `L280-L489` |
| `rack_style` | `horizontal_shelves`, `cubby_grid` | S2 `L208-L278`; S4 `L187-L255`; S3 `L296-L398`; S6 `L302-L424`; S7 `L211-L283` |
| `service_module` | `fixed_storage`, `fold_out_counter`, `pull_out_shelves`, `rotating_shelves`, `hanging_stem_rack` | S1/S8; S5 `L377-L488`; S18 `L36-L48,L379-L452`; S19 `L157-L204,L390-L443`; S14 `L120-L158,L249-L267,L582-L591` |
| `door_count` | `0..3`, conditional | S9/S10/S11 `L272-L648` |
| `rack_count` | quarter-round capacity `4..12`; rectangular source-fixed rows/cells `6`, `7`, `18`, `24`; moving-shelf-fixed `3` | S15/S16/S17; S2/S7; S6/S3; S18/S19 |
| `palette_style` (④ only) | five material palettes | host-conformal appearance only; excluded from structural count |

## Form Dependency Contracts

| master profile | consumers that must derive from it | validator |
|---|---|---|
| rectangular inner envelope `(W,D,H,front_y)` | side/back/top/bottom panels, reveals, door opening, hinge origins, slide tracks, rack/cubby bounds | every consumer remains inside the same resolved opening; minimum door width and rack pitch; closed/mid/max collision |
| `quarter_round_profile(W,D,bow)` | bottom/top/intermediate decks, diagonal side shell, bowed `front_y`, face rails/stiles, curved door/service boundary, pull-out shelf profile | every front consumer uses the profile's actual maximum-Y envelope; no rectangular shelf/front is attached to the curved shell; all consumers clear the shell over full travel |
| wine-storage occupancy | shelf/cubby supports, bottle row positions, stem rack and complete glass geometry | every horizontal bottle maps to one support row/cell; every upright bottle stands on base/lower/upper shelf; hanging glasses have foot+stem+lathed bowl captured by bilateral rails |
| bifold opening envelope | cabinet pivot pin, two finite-thickness leaves, short inter-leaf knuckles, fold range | pin/knuckles coaxial; leaves do not occupy the same plane; closed/mid/max sampled collision |
| pull-out guide envelope | paired parent guides, paired child runners, front uprights/ties, shelf profile, prismatic axis/range | both runners remain engaged for `q∈[0,0.16]`; no central fake rail; no shell sweep intersection |
| rotating spindle envelope | grounded continuous spindle, support pads, bored shelf disks/bearings, coaxial continuous joints | every rotation axis equals spindle axis; 360-degree sweep clears shell |

Any world-knowledge form extrapolation must add all consumers to one bundle. A new part tree, joint graph, or interface semantic is not ③ and requires a newly accepted upstream variant.

## Slot graph / Module Emits / Interfaces

```text
cabinet_body (grounded root)
├── rectangular profile
│   ├── door_i -- REVOLUTE Z or PRISMATIC X
│   └── inline horizontal/cubby storage
└── quarter_round profile
    ├── door_i -- REVOLUTE Z              [fixed/hanging only]
    ├── fold_out_counter -- REVOLUTE X    [door_count=0]
    ├── pull_out_shelf_i -- PRISMATIC Y   [door_count=0, bilateral guides]
    └── rotating_shelf_i -- CONTINUOUS Z  [door_count=0, central spindle]
```

- Rectangular body modules emit one grounded, connected carcass with base, side/back/top/bottom boundaries and a derived front opening.
- Hinged doors emit complete framed leaves, handles and hinge barrels; parent hinge mounts physically reach the barrel.
- Sliding emits one complete leaf plus top/bottom tracks that bridge the body and remain engaged throughout travel.
- Bifold emits two thin framed leaves, a body pivot pin and two short inter-leaf hinge knuckles. The main leaf opens 72° outward; the second leaf uses a bounded 45° reverse mimic so finite solids never collapse into the same plane.
- Pull-out emits three complete curved shelves, each with bilateral longitudinal runners and guides, plus grounded guide uprights/ties.
- Rotating emits three bored circular shelves around one grounded continuous spindle; joint origins are coaxial with that spindle.
- Fold-out emits a complete counter leaf, a full hinge knuckle, two end lugs/backplate and a center mullion tying that carrier into the fixed curved decks.
- Hanging-stem storage emits fixed plate/bilateral capture rails and three complete inverted glasses (foot, stem and lathed bowl) on the grounded body, not an invented articulation.
- Glass-front/narrow-tower horizontal storage emits two full-depth compartments with respectively `6×4` and `7×3` bottles per compartment. White-hutch/low-sideboard cubbies emit respectively `6×4` and `6×3` supported cells. Tall-cooler-style rails emit three supported bottles per level.

## Mechanism structure and swept-clearance

| mechanism | origin / axis / range | required support/capture | accepted poses |
|---|---|---|---|
| hinged door | front side hinge / `±Z` / `0..resolved_open` | two cabinet mounts + door barrels | closed, mid, max |
| sliding door | track datum / `X` / bounded lateral travel | top and bottom body tracks | closed, mid, max |
| bifold | body pivot `-Z`, fold pivot `Z` with reverse mimic | cabinet pin/barrel + two short fold knuckles/stiles | closed-unfolded, mid, open-V-fold |
| fold-out | front service hinge / `X` / `0..85°` | grounded backplate/end lugs + full knuckle | stowed, mid, deployed |
| pull-out | shelf center / `Y` / `0..0.16m` | two same-side guide/runner pairs per shelf | closed, mid, max |
| rotating | central spindle / `Z` / continuous | grounded spindle + support/bearing | 0°, 90°, 180°, 270° |

Zero tolerance blockers: floating mechanism geometry; false crossbars/central rails; a curved front without matching body/deck/support consumers; a joint origin inside the wrong solid; motion that enters the shell; broad overlap allowances.

## Element-scoped allowance table

| exact element pair | physical reason | poses |
|---|---|---|
| door hinge barrel ↔ its cabinet mount | captured hinge barrel | all hinged poses |
| door top/bottom rail ↔ matching body track | captured sliding rail | all sliding poses |
| bifold body barrel/frame bore ↔ cabinet pivot pin | real pivot pin through bored frame | all bifold poses |
| matching fold knuckles / knuckle ↔ bored fold stile | real inter-leaf hinge | all bifold poses |
| shelf runner ↔ same-index/same-side guide | captured bilateral slide | full pull-out travel |
| shelf bearing/bored disk ↔ spindle/support | coaxial shaft/bearing contact | full rotation |
| counter knuckle ↔ its two end lugs | captured counter hinge | full fold-out travel |

No whole-part `allow_overlap` is permitted for any pair. Any new allowance is a blocker until this table, the template and the allowance audit agree.

## Compatibility Gates

1. `sliding|bifold` ⇒ `body_form=tall_cooler`; all other forms reject those mechanisms.
2. Non-quarter forms ⇒ `service_module=fixed_storage`.
3. `quarter_round_corner` ⇒ `door_motion=hinged` and curved consumers only.
4. `fold_out_counter|pull_out_shelves|rotating_shelves` ⇒ `door_count=0`; doors and service swept envelopes are not sampled together.
5. `fixed_storage|hanging_stem_rack` on quarter-round ⇒ `door_count∈{1,2,3}`.
6. `tall_cooler` ⇒ `door_count=1`; `narrow_tower` ⇒ `door_count=2`; remaining rectangular hinged forms ⇒ `door_count∈{1,2}`.
7. `cubby_grid` is allowed only on `{glass_front_cabinet,white_display_hutch,low_sideboard,narrow_tower}` through the common rectangular inner-envelope contract.
8. `pull_out_shelves|rotating_shelves` ⇒ `rack_count=3`; low-sideboard cubby ⇒ `18`; other admitted rectangular cubbies ⇒ `24`; glass-front horizontal ⇒ six rows; narrow-tower horizontal ⇒ seven rows; quarter-round fixed/fold/hanging and generic rail storage on white-hutch/low-sideboard/tall-cooler admit integer `4..12` only through their source-backed support/spacing equations.
9. Invalid overrides are resolved/gated before build; the builder must never rely on collision allowances to legalize a rejected tuple.

## Multiplicity

- `door_count`: accepted anchors `1/2/3`; `0` is the explicit no-door service state. Naming and hinge placement are deterministic. Each door remains a complete moving leaf.
- `rack_count`: S15/S16/S17 anchor quarter-round values at `4/8/12`; S15 applies N independently to several content zones, whereas S16/S17 define total bottle capacity. The production contract explicitly normalizes to the S16/S17 total-capacity semantics: each integer drives exactly N supported upper/base/lower-shelf positions and within-row spacing, while S15 contributes the accepted lower value/layout only. The rectangular FormFamilies retain their accepted counts (`6` or `7` shelf rows; `18` or `24` cubby cells), and each row/cell deterministically emits its source density of bottles. `N=3` is mechanism-fixed for the three accepted moving-shelf entities. Free scattered copies, decoration and continuous scale do not count as N diversity.

## Combination Domain

Structural counting excludes palette, ④ decoration and continuous dimensions. After gates, the core functional tuples are:

- glass-front: hinged × {horizontal,cubby} = 2
- white hutch: hinged × {horizontal,cubby} = 2
- low sideboard: hinged × {horizontal,cubby} = 2
- narrow tower: hinged × {horizontal,cubby} = 2
- tall cooler: {hinged,sliding,bifold} × horizontal = 3
- quarter-round: five service modules × hinged/curved family = 5

Core gated profile count = **16** (`constrained` floor met). Multiplicity expands the raw structural domain through legal door counts and integer rack N; the exact CLI audit remains authoritative. No rejected Cartesian tuple contributes to either count.

## Visual Risk

`curved_fit`, `hidden_slide`, `multi_joint`. Coverage-driven visual QA must include: white-hutch 24-cell and low-sideboard 18-cell cubbies; glass-front 6-row and narrow-tower 7-row compartments; tall-cooler paired rails; sliding closed/mid/max; bifold closed/mid/max close-up; quarter-round 3-door; fold-out carrier; pull-out guide close-up; rotating spindle close-up; hanging-stem rack and lathed bowls; quarter-round N boundaries 4/12.

## Parameters and compile budget

- body scales: width `[0.85,1.15]`, height `[0.90,1.10]`; door-open scale `[0.70,1.00]`, all resolved before build.
- Door width, rack pitch, guide engagement and shell clearance are inequalities, not free decoration.
- Per-seed target `<20s`; geometry uses bounded boxes/cylinders, shared bottle mesh and low-complexity extrusions. Watchdog `120s`.

## Validators / reject criteria

Required: model validity; mesh readiness; grounded/connected parts; no part-internal islands; no current or sampled-pose overlap except tabled exact contacts; joint mating; source metadata; category identity; body/service gate assertions; door and rack N realization; joint axis/range and non-zero motion; no broad allowance.

Reject: rectangular/curved consumer mismatch; sliding door without tracks; bifold leaves collapsing into one another; pull-out without two guides; eccentric rotating shelf; incomplete door/counter/shelf; whole-part allowance; source-map mismatch; stale visual approval.

## Agent self-review

| check | status |
|---|---|
| exact ①②③/N source evidence | pass — S1–S19 |
| ④ is the only unsourced extrapolation axis | pass |
| form consumers share master profiles | pass |
| mechanism supports and full-travel envelopes declared | pass |
| compatibility gates prohibit unverified Cartesian product | pass |
| allowances are exact element pairs only | pass |
| category binding stable | pass; shared registry entry suggested above |
| implementation status | `implementation_ready`; human visual QA still required before formal export |
