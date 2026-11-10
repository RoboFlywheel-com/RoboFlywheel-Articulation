# wine_cabinet2 — modular authoring spec

```yaml
metadata:
  slug: wine_cabinet2
  template_path: agent/templates/wine_cabinet2.py
  source_map: ../articraft_data/picture_expansion/template_source_maps/0611__wine_cabinet2.md
  authoring_status: implementation_ready
  modular: true
  pattern: parallel_children
  compile_budget_seconds_per_seed: 20
```

## Category Binding

| field | value |
|---|---|
| canonical category | `wine_cabinet2` |
| template slug | `wine_cabinet2` |
| mechanism profile | `mixed_cabinet_fronts` |
| export namespace | `wine_cabinet2` |
| binding rule | one stable category/template identity; swing, bypass, pocket, drawer and service motions remain gated modules inside it |

Suggested registry entry is documented at handoff; this authoring pass does not
modify the shared registry.

## Source Review

- five-star/reviewed records: 19 of 19 origins, redo records and variants.
- canonical evidence: exact record/revision/line ranges are in
  `articraft_data/picture_expansion/template_source_maps/0611__wine_cabinet2.md`.
- body candidates: four actual cabinet envelopes from origins/redo records.
- reclassified suffix records: `arched_hutch`, `compact_freestanding` and
  `full_wall` do not alter the cabinet envelope. They cannot inflate ③.
- no world-knowledge structure enters this spec. Decoration alone may be
  host-conformal world-knowledge extrapolation.

## Category Identity

`wine_cabinet2` is an upright, enclosing wine-storage cabinet with a grounded
panel carcass, at least one operable front, a wine-specific storage/display
insert, and complete moving cabinetry. Bottles are visible fixed contents.

It is not a bare wine rack, open shelving unit, sideboard without wine storage,
or refrigerator. The cooler-style glass leaf remains ordinary cabinetry: no
compressor, gasketed cold cavity or appliance identity.

## Structural Axes and Candidates

| axis / slot | candidates | source status |
|---|---|---|
| ③ `body_form` | `contemporary_bookcase`, `freestanding_hutch`, `modular_light_wood`, `built_in_wall` | four origin/redo anchors |
| ② `door_mechanism` | `swing_glass`, `swing_divided_glass`, `swing_paneled`, `swing_cooler`, `sliding_glass`, `pocket_glass` | four origin swing anchors + two accepted motion variants |
| ① `rack_topology` | `glass_shelf_bay`, `diamond_lattice`, `horizontal_bar_rack`, `vertical_peg_rack`, `hybrid_display_rack` | source-backed; hybrid preserves the N=20 source's 4 upright + 9 diamond + 7 cooler support bundle; peg support is corrected to retain real bottles |
| ② `service_motion` | `none`, `pull_out_tasting_shelf` | source-backed variant |
| N `door_count` | `{1,2,3,4}` | all values observed |
| N `drawer_count` | `{0,2,3,4}` | 2/3/4 observed; 0 observed |
| N fixed contents | bottle_count integer 6–20 | 12 and 20 anchors plus capacity-bounded interpolation; N=20 is reachable only on the source-matched modular hybrid |
| ⑥ `palette_style` | six whole-object palettes | finish-only; not counted as structure |

### Slot graph

```text
cabinet (grounded root; shell, rack supports, jambs/tracks, drawer rails)
├── door_0..N-1                 REVOLUTE or PRISMATIC, gated by one profile
├── drawer_0..N-1               PRISMATIC +Y, complete retained containers
├── tasting_shelf               optional PRISMATIC +Y service member
└── bottle/glassware children   FIXED contents seated on real supports
```

Every non-moving board, rail, jamb, track and bracket is a visual of
`cabinet`; it is not emitted as a decorative fixed child.

## InterfaceSpec and MatingContract

| module | emits | consumes / mating interface | active joint |
|---|---|---|---|
| swing door | framed leaf, panel/glass, pull, two barrel knuckles and straps | two cabinet hinge stations: segmented jamb, rear spine, paired fixed knuckles and coaxial axle | REVOLUTE about cabinet Z; `open_toward=(0,+Y,0)` |
| bypass glass | centered framed leaf and upper/lower shoes | matching lane's upper/lower longitudinal tracks | PRISMATIC ±X; real track-shoe mating |
| pocket glass | centered framed leaf, flush pull and shoes | matching side well, cheek/partition and full-width upper/lower rails | PRISMATIC ±X; full leaf remains inside the admitted pocket envelope |
| drawer | front, bottom, two sides, back, pull and two moving glides | individual bay, bilateral longitudinal rails/brackets and small rear/top closed stop | PRISMATIC +Y; front seats on named stop |
| tasting shelf | deck, front lip and two moving glides | bilateral tracks/brackets in modular service bay | PRISMATIC +Y; front lip seats on named stop |
| rack contents | complete upright/horizontal wine bottles | glass shelf, full-depth lattice V, paired peg saddle, two-bar seat, or the hybrid's source-matched glass/diamond/cooler supports | FIXED; diamond N is allocated into per-cell 2/3-bottle inverted-pyramid stacks with bottom bottle on both boards |

Swing capture intentionally has no fictitious planar jamb mating contract. The
coaxial hardware and sweep are the mechanism evidence. Sliding doors, drawers
and tasting shelf retain named face mating contracts.

## Mechanism Structure and Swept Clearance

| mechanism | closed / mid / max acceptance | blocking defect |
|---|---|---|
| swing | barrel remains coaxial with axle; leaf clears cabinet, segmented jamb, fixed knuckles, sibling leaves, racks and contents | solid jamb through barrel; hinge knuckle through stile; sibling collision |
| bypass | both shoes remain on their lane; leaves remain separated in Y; travel reveals opening | one shared fake rail, missing upper/lower capture, leaves crossing lanes |
| pocket | side well exceeds travel; leaf clears cheek/partition and is captured above/below at max | pocket leaf combined with solid/no-pocket carcass |
| drawer | two cabinet rails and two moving glides stay engaged; complete container clears bay walls through max | transverse cavity bar, central rail, missing back/bottom/side, broad carcass allowance |
| tasting shelf | two glides remain on two tracks; board and lip clear front at max | floating board, one central rail, collision with pocket/drawers |

Acceptance poses are closed, 50% and maximum plus sampled multi-joint corners.
N=3/4 paneled leaves belong only to the built-in wall's lower cupboard bank
and use a proven 0.80-rad maximum because interior leaves share neighboring
sweep boundaries. They never cover the upper wine rack.

## Form Dependency Contracts

| master profile | dependent consumers | validator |
|---|---|---|
| resolved W/D/H + body family | shell, front opening, rack region, jambs/tracks, drawer bays, pocket wells | every consumer is recomputed from the same resolved values |
| resolved door band + door N | leaf width, hinge/track stations, rails, pockets, joint origins and ranges | no independently scaled panel/frame/opening; every count emits equal supports and joints |
| built-in paneled zoning | lower paneled bank, shallow drawer band, upper rack support deck and rack boundary | one source-backed Z stack enforces `door_top < drawer_band < rack_min`; no paneled leaf may cover the lattice/display bay |
| pocket central opening | both leaves, both wells, rail length and travel | `pocket_width > admitted_travel + clearance` |
| drawer bay W/D/H + drawer N | all five container walls, two glides, two rails, brackets, bay walls and stop | count equality and full-travel clearance |
| rack family | support boards/pegs/shelves, bottle type and every bottle origin | diamond crossed boards extend from back panel to rack mouth; no forward saddle/arm is allowed; emitted bottle count equals resolved N and selected cells form bottom-1/top-2 V stacks |

Any future curved/polygonal front is a complete FormFamily bundle. Changing a
panel outline without synchronizing frame, opening, tracks/supports and swept
proxy is rejected.

## Compatibility Gates

| requested combination | resolver result |
|---|---|
| horizontal bars on freestanding hutch | keep |
| horizontal bars on other body | rewrite rack to glass shelves |
| diamond/vertical pegs on modular or built-in body | keep |
| diamond/vertical pegs on contemporary/hutch body | rewrite rack to glass shelves |
| hybrid display on modular body | keep; source-matched capacity 20; force service motion to `none` |
| hybrid display on another body | rewrite rack to glass shelves |
| cooler swing with any N | force N=1 |
| bypass/pocket with any N | force N=2 |
| pocket on hutch | rewrite to bypass |
| pocket with drawers | force drawers=0 |
| paneled swing N=3/4 on built-in | keep as lower cupboard bank; cap range to 0.80 rad and derive drawer/rack Z zones from the same stack |
| paneled swing on another host, or N=1/2 on built-in | rewrite to that host's source-backed glass facade / reject from registered domain |
| N=3/4 on another door/body pair | force N=2 pending compatibility probe |
| drawers on contemporary or built-in | keep N in `{0,2,3,4}` |
| drawers on hutch/modular | force 0 |
| tasting shelf on modular, non-pocket host | keep; force drawers=0 |
| tasting shelf elsewhere or with pocket | rewrite service motion to `none` |

The registered combination domain treats a request above a body's rack
capacity as denied, not as another legal tuple. Direct regression configs are
projected to a safe capacity for robustness, but `slot_choices` records
`bottle_count_requested`, resolved `bottle_count`, and `rack_capacity`, while
ordinary procedural seeds sample only inside the resolved capacity.

### Body × rack capacity gate

| admitted body | admitted rack | capacity | supported bottle construction |
|---|---|---:|---|
| `contemporary_bookcase` | `glass_shelf_bay` | 12 | upright bottles seated on glass shelves |
| `freestanding_hutch` | `glass_shelf_bay` | 8 | upright bottles seated on glass shelves |
| `freestanding_hutch` | `horizontal_bar_rack` | 12 | horizontal bottles on paired bars and saddles |
| `modular_light_wood` | `glass_shelf_bay` | 10 | upright bottles seated on glass shelves |
| `modular_light_wood` / `built_in_wall` | `diamond_lattice` | 20 | horizontal bottles distributed across nine full-depth V cells; each active cell has 2 or 3 bottles, with one apex bottle and up to two bottles above along the boards |
| `modular_light_wood` / `built_in_wall` | `vertical_peg_rack` | 12 | horizontal bottles on a 4×3 paired peg-and-saddle grid |
| `built_in_wall` | `glass_shelf_bay` | 12 | upright bottles seated on glass shelves |
| `modular_light_wood` | `hybrid_display_rack` | 20 | source-matched 4 upright glass-shelf + 9 diamond-saddle + 7 cooler-shelf bottles |

All other body×rack tuples are gated before capacity lookup. A rack emitter
must expose exactly its table capacity and must emit exactly resolved N; no
`supports[:N]` truncation may make the model disagree with its slot report.

Resolver rewrites are deterministic and persisted in `slot_choices`. Rejected
raw requests do not count as distinct legal configurations.

## Combination Domain

```yaml
combination_domain:
  counted_axes:
    - body_form
    - door_mechanism
    - rack_topology
    - service_motion
    - door_count
    - drawer_count
  excluded_axes:
    - palette_style
    - continuous_dimensions
    - bottle_finish
    - pure_decoration
  exact_unique_resolved_core_configs: 63
  registry_compatibility_gated_raw_tuples: 8840
  diversity_profile: standard
  minimum_core_required: 48
  status: pass
  counting_method: enumerate all declared discrete inputs, run resolve_config, deduplicate body_form/door_mechanism/rack_topology/service_motion for core; report door/drawer N separately
```

Door, drawer and bottle N add validated multiplicity coverage but never inflate
the 63 core configurations. Illegal/re-written raw tuples and finish-only
differences never inflate the count.

## Parameter Bounds

| parameter | production range | constraint |
|---|---|---|
| width scale | 0.88–1.15 | shared consumer recomputation |
| height scale | 0.88–1.15 | shelf spacing must clear upright contents |
| depth scale | 0.90–1.12 | guide length and pocket capacity recomputed |
| swing request scale | 0.85–1.05 | clearance solver; N≥3 capped at 0.80 rad |
| drawer travel scale | 0.80–1.05 | travel ≤ 0.68 drawer-box depth |
| tasting travel | ≤0.30 m | depth-bounded and two-guide engagement |
| bottle count | 6–20 | sampler draws inside resolved `(body_form,rack_topology)` capacity; direct over-cap requests are projected and explicitly reported |

Compile budget is 20 seconds/seed. Boxes/cylinders provide mechanism collision
proxies; shared CadQuery meshes are limited to small decoration assets.

## Element Allowance Table

| part pair | exact elements | reason | valid poses |
|---|---|---|---|
| `door_i` ↔ `cabinet` | `hinge_barrel_k` ↔ `hinge_axle_i_k` | real coaxial axle passes through captured door barrel | entire swing range |

No other allowance is approved. In particular, door↔cabinet,
drawer↔cabinet, tasting-shelf↔cabinet, bottle↔rack and sibling moving-part
whole-pair allowances are blockers. Exact hinge exemptions must not suppress
socket/stile, leaf/jamb or any sibling collision.

## Validator and Test Requirements

- deterministic seed/config/slot-choice agreement;
- canonical part and joint counts equal the resolved N values;
- exact bottle part count equals resolved bottle N, the capacity contract is in
  object metadata/slot choices, and procedural seeds never request above the
  resolved body×rack capacity;
- each drawer contains front, bottom, two sides, back and two glides, while the
  cabinet contains two rails per drawer;
- swing door hardware has two named axle/barrel stations per door;
- target pose proves first door motion; first drawer and tasting shelf prove
  positive-Y translation when present;
- `check_model_valid`, mesh readiness, no isolated active parts, mating gap,
  joint-origin proximity, current-pose collision and sampled-pose collision;
- allowance audit rejects missing element names, new allowances and broad
  part-pair exemptions;
- targeted coverage includes all six door families, all five rack families,
  N door `{1,2,3,4}`, drawer `{0,2,3,4}`, bottle `{6,13,20}` plus every
  body×rack capacity boundary, and service `{none,pull_out}`;
- smoke seeds precede full sweep; full sweep remains mechanical and network-free.

## Reject Cases

- fake transverse bar through a drawer, central fake guide, incomplete drawer;
- pocket door installed on a solid cabinet with no pocket well;
- bypass leaves without distinct upper/lower capture lanes;
- solid jamb/hinge geometry occupying the rotation envelope;
- peg-shaped objects replacing wine bottles;
- bottle embedded deeply in diamond boards or back panel; shallow X applique,
  forward saddle/support arms, or a per-cell pile not summing exactly to resolved N;
- unverified N=3/4 door family, unchecked Cartesian product, or category drift;
- any whole-part `allow_overlap` or decoration added to trick motion/AABB tests.

## Visual Risk

```yaml
visual_risk:
  - drawer
  - hidden_slide
  - pocket
  - multi_joint
  - rack_content_fit
required_views:
  - closed front three-quarter
  - mid mechanism pose
  - maximum mechanism pose
  - drawer guide close-up
  - pocket/bypass track close-up
  - hinge close-up
  - diamond/peg bottle support close-up
visual_qa_status: pending
```

Visual smoke/final reports are local evidence only and cannot approve the
template. Final seed export requires a full mechanical sweep, fresh hash-bound
visual QA, and human approval.

## Agent Self-Review

| check | result |
|---|---|
| source lines precise and pseudo-body variants reclassified | pass |
| category binding stable | pass |
| mechanism, dependency, compatibility and allowance tables present | pass |
| exact standard core combination domain ≥48 | pass: 63; the exact registry-gated raw domain is 8840 and all multiplicity axes remain separately reachable |
| broad allowances absent | pass |
| authoring status | `implementation_ready` |
| formal completion | blocked on full sweep + visual/human gate |
