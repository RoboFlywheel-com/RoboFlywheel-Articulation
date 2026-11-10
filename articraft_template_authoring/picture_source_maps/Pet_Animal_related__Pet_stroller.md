# Source Map — Pet_Animal related / Pet stroller

slug `pet_stroller` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d` — picture/Pet_Animal related/Pet stroller/001.png
- `rec_pet_animal_related__pet_stroller__002_png_f746b67563c44f6f8a732e97a638d7ff` — picture/Pet_Animal related/Pet stroller/002.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_pet_stroller_var_form_enclosed_dome` | form_enclosed_dome | PASS | 5 | 1 |
| `rec_pet_stroller_var_form_rigid_carrier` | form_rigid_carrier | PASS | 6 | 2 |
| `rec_pet_stroller_var_mechanism_front_door` | mechanism_front_door | PASS | 7 | 1 |
| `rec_pet_stroller_var_mechanism_reversible_handle` | mechanism_reversible_handle | PASS | 5 | 1 |
| `rec_pet_stroller_var_mechanism_swivel_caster` | mechanism_swivel_caster | PASS | 8 | 1 |
| `rec_pet_stroller_var_mechanism_telescoping_handle` | mechanism_telescoping_handle | PASS | 6 | 1 |
| `rec_pet_stroller_var_skeleton_double_cabin` | skeleton_double_cabin | PASS | 6 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Pet_Animal related / Pet stroller — variant plan

pattern: **mixed** (single frame/base root carrying independent revolute canopy + revolute/prismatic handle + N continuous wheel spins; wheel-count and cabin-count multiplicity)
richness band: **normal (low end, coverage-complete)** — 9 candidate anchors (2 origins + 7 forks)
parents (both origin_anchor, fork sources):
- A `rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d` — pic `picture/Pet_Animal related/Pet stroller/001.png`
- B `rec_pet_animal_related__pet_stroller__002_png_f746b67563c44f6f8a732e97a638d7ff` — pic `picture/Pet_Animal related/Pet stroller/002.png`

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Pet stroller
  core_identity: a wheeled, human-pushed carriage whose main body is a fabric or rigid pet cabin/bassinet, with a push handle and a fold-back canopy, rolling on 3-4 ground wheels.
  must_keep:
    - enclosed/semi-enclosed pet cabin (basket or pod) mounted on a rolling frame
    - a push handle the human grips from behind
    - a folding/opening canopy or top for pet access
    - >=3 ground wheels each on a real continuous spin joint
    - at least the canopy and handle as real non-fixed articulations
  must_not_become:
    - Pet carrier (standalone handheld/backpack, no wheeled push frame)
    - baby/child stroller (human-infant seat with 5-point harness styling)
    - dog crate / Bird cage (static caged enclosure, no push frame)
    - pet wagon / hand-truck / shopping cart (open flatbed tub or utility cart)
    - pet playpen (floor pen, no wheels)
  image_evidence:
    - "001: gold tubular frame, black fabric cabin with side+front mesh windows, fold-back mesh canopy, U-shape leather-wrapped push handle, lower mesh storage basket, cup holder, 4 wheels = 2 larger rear + 2 small front swivel casters with red shock springs"
    - "002: navy fabric jogger, arched mesh-front canopy, single fold swing handle with foam grip, lower mesh storage basket, 3 wheels = 2 large pneumatic spoked rear + 1 front wheel on a fork"
  parent_evidence:
    - "A parts: frame (fabric cabin: basket_floor/side_wall_0-1/front_lip/rear_panel + perforated mesh_window/front_mesh_window + champagne top_rim/side_rail + lower storage_base + tubular loops + front_fork/front_spring/fender), canopy (revolute canopy_hinge), handle (revolute handle_hinge, U-tube + grip), rear_wheel_0/1 + front_wheel_0/1 each continuous *_spin; helper _add_wheel/_tube/_canopy_shell_from_side_path"
    - "B parts: base (navy cabin side/front/rear panels + seat_floor + perforated storage + tubular rails/uprights/folding_strut + front_fork_leg_0/1 + hinge collars/bars), handle (revolute base_to_handle), canopy (revolute base_to_canopy, bezier fabric+mesh), rear_wheel_0/1 (continuous, Mimic-linked) + single front_wheel (continuous); helper _add_tube/_curved_fabric_panel/_bezier"
```

## Slots and Candidates (each supported slot reaches >=2 structurally distinct candidates)
| slot | candidate | diversity_axis | source_type | evidence / record | status |
|---|---|---|---|---|---|
| chassis / wheel-config | 4-wheel dual-front-caster | ① / N=4 | origin_anchor | A | converged |
| chassis / wheel-config | 3-wheel jogger single-front | ① / N=3 | origin_anchor | B | converged |
| chassis / cabin-count | double / two-tier cabin (N=2) | ① multiplicity | forked_anchor | rec_pet_stroller_var_skeleton_double_cabin (from A) | planned |
| front-wheel mechanism | fixed fork (jogger) | ② | origin_anchor | B (front_fork_leg_0/1) | converged |
| front-wheel mechanism | swivel caster (steer revolute + spin) | ② | forked_anchor | rec_pet_stroller_var_mechanism_swivel_caster (from A) | planned |
| cabin body form | soft fabric sewn cabin | ③ planar/fabric | origin_anchor | A, B | converged |
| cabin body form | rigid detachable hard-shell carrier pod | ③ volumetric | forked_anchor | rec_pet_stroller_var_form_rigid_carrier (from A) | planned |
| cabin body form | fully enclosed zip-around mesh dome | ③ volumetric envelope | forked_anchor | rec_pet_stroller_var_form_enclosed_dome (from B) | planned |
| cabin access / opening | fold-back canopy (revolute) | ② | origin_anchor | A canopy_hinge, B base_to_canopy | converged |
| cabin access / opening | front drop-down entry door flap (revolute) | ② | forked_anchor | rec_pet_stroller_var_mechanism_front_door (from A) | planned |
| push handle | U-shape fold handle (revolute) | ② | origin_anchor | A handle_hinge | converged |
| push handle | swing-bar fold handle (revolute) | ②/① | origin_anchor | B base_to_handle | converged |
| push handle | telescoping height-adjust (prismatic) | ② | forked_anchor | rec_pet_stroller_var_mechanism_telescoping_handle (from A) | planned |
| push handle | reversible swing-over handle (wide revolute) | ② | forked_anchor | rec_pet_stroller_var_mechanism_reversible_handle (from B) | planned |
| lower storage | mesh storage basket | — | record_only | A storage_base, B storage_floor_mesh | recorded (single-candidate low-value slot) |

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | wheel-config 4-wheel(A) / 3-wheel(B); cabin-count single(A,B) / double-tier(fork). |
| ② joint / mechanism | source-backed (origin + forked_anchor) | canopy revolute + handle revolute + wheel continuous (both origins); rear-wheel Mimic (B); NEW: front swivel-caster revolute, front-door revolute flap, telescoping prismatic handle, reversible wide-arc handle revolute. |
| ③ primary form family | source-backed (origin + forked_anchor) | soft fabric sewn cabin (A,B) / rigid hard-shell carrier pod (fork) / fully enclosed mesh dome (fork). |
| ④ surface decoration | record_only / world_knowledge_extrapolation | perforated side/front mesh windows, stitched trim, badges/logo decal, cup-holder accessory, canopy mesh pattern. Not a standalone variant. |
| ⑤ proportion / size / travel | record_only | rear tire radius 0.145-0.19 vs front 0.096-0.13; canopy revolute ~[-0.2,1.05]; handle fold [0,0.95]; telescoping travel ~0.18 m (companion only). |
| ⑥ material / palette / finish | record_only / companion | champagne-gold frame + black fabric (A) vs navy fabric + black/silver + white rims (B); EVA solid vs pneumatic spoked tire; carrier pod rigid plastic palette (companion on rigid_carrier). |

## Multiplicity / Copy Logic
- **wheels**: count_param = ground-wheel count; N samples {3 (B), 4 (A)} — both origin-backed, no extra fork. copied_object = wheel part (`_add_wheel` tire+rim+hub) + its continuous `*_spin` joint; naming rear_wheel_{i}/front_wheel_{i}; placement = front axle pair + rear axle pair (or single front on fork); joint_policy = one continuous spin per wheel (B mirrors rear pair via Mimic). suggested N_range {3,4}.
- **cabin tiers**: count_param = cabin count; N samples {1 (A,B), 2 (fork skeleton_double_cabin)}; copied_object = fabric cabin box (floor+4 walls+mesh windows) via shared helper, indexed cabin_{idx}_*; placement = stacked along +Z with a shelf divider; joint_policy = both cabins FIXED to frame. N_range {1,2} (no >2 tiers).
- Repeated wheels/casters/cabins must be loop-emitted with shared helpers and stable indexed names (parents already do this for wheels).

## Variant Cards (one per fork)
```yaml
- variant_id: rec_pet_stroller_var_mechanism_swivel_caster
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d
  positioning: {product_archetype: urban 4-wheel stroller with 360deg front swivel casters, why_same_subcategory: fabric cabin + canopy + handle + wheels all retained}
  primary_axis: {slot: front-wheel mechanism, diversity_axis: ②, target_candidate: swivel caster (steer revolute + spin)}
  structural_delta:
    change: [add caster_yoke child per front wheel on a vertical revolute steering joint, front wheel spins about horizontal axle as child of yoke, trailing king-pin offset]
    keep_parts: [frame, canopy, canopy_hinge, handle, handle_hinge, rear_wheel_0, rear_wheel_1, rear_wheel_spin_0, rear_wheel_spin_1]
    joint_policy: add one revolute steering joint per front caster; keep continuous spin
    interface_policy: yoke fork straddles wheel, steering axis above contact patch with trail offset
  multiplicity: {applies: true, target_n: 2, copied_object: front caster (yoke+wheel), placement_rule: front axle pair}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [wheel-count change, cabin/canopy/handle change, articulated suspension]}
  acceptance_focus: [two front swivel revolute joints, front wheels still contact ground and spin, no float]
- variant_id: rec_pet_stroller_var_form_rigid_carrier
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d
  positioning: {product_archetype: travel-system stroller with removable hard-shell carrier pod, why_same_subcategory: pod seats on wheeled push frame under a canopy}
  primary_axis: {slot: cabin body form, diversity_axis: ③, target_candidate: rigid detachable hard-shell carrier pod}
  structural_delta:
    change: [replace planar fabric wall/floor boxes with one hollow rounded-rect plastic tub + vent grilles, add frame cradle/clip saddle interface]
    keep_parts: [frame, top_rim, storage_base, canopy, canopy_hinge, handle, handle_hinge, front_wheel_0, front_wheel_1, rear_wheel_0, rear_wheel_1]
    joint_policy: preserve; pod is fixed-seated (detachable read via mating face)
    interface_policy: two saddle brackets at top_rim height cradle the pod
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [rigid plastic pod material/palette], forbidden: [category drift to standalone Pet carrier, wheel/handle/canopy change]}
  acceptance_focus: [pod reads as one detachable rigid shell with clear cradle face, canopy still hinges to frame]
- variant_id: rec_pet_stroller_var_mechanism_front_door
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d
  positioning: {product_archetype: front-entry pet stroller with drop-down mesh door, why_same_subcategory: cabin/canopy/handle/wheels retained}
  primary_axis: {slot: cabin access, diversity_axis: ②, target_candidate: front entry door flap (revolute)}
  structural_delta:
    change: [front panel becomes separate door part with fabric frame + mesh, revolute along lower edge dropping open, latch boss at top]
    keep_parts: [frame, basket_floor, side_wall_0, side_wall_1, rear_panel, mesh_window_0, mesh_window_1, canopy, canopy_hinge, handle, handle_hinge, wheels+spins]
    joint_policy: add one revolute door joint (lower 0 upper ~1.3)
    interface_policy: lower-edge hinge line + top-edge clip boss on frame
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [wheel/body/canopy/handle change, rigid-carrier conversion]}
  acceptance_focus: [door swings open on revolute, covers front opening when closed, not floating]
- variant_id: rec_pet_stroller_var_mechanism_telescoping_handle
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d
  positioning: {product_archetype: height-adjustable telescoping-handle stroller, why_same_subcategory: cabin/canopy/wheels retained, handle still the push grip}
  primary_axis: {slot: push handle, diversity_axis: ②, target_candidate: telescoping prismatic handle}
  structural_delta:
    change: [replace handle_hinge revolute with prismatic joint along rear uprights, add two fixed telescope outer sleeves, handle U-tube slides inside]
    keep_parts: [frame, rear_upright_+1, rear_upright_-1, handle, handle_tube, handle_grip, canopy, canopy_hinge, wheels]
    joint_policy: replace the single handle mechanism (revolute -> prismatic), no second joint
    interface_policy: handle side tubes captured inside outer sleeves (local overlap)
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [handle/sleeve length proportion], forbidden: [keep a fold revolute, wheel/cabin/canopy change]}
  acceptance_focus: [one prismatic handle joint with real travel, handle nests in sleeves, no float]
- variant_id: rec_pet_stroller_var_skeleton_double_cabin
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__001_png_58f3cf9b4b654ac0ad4a0a8d4e46cb2d
  positioning: {product_archetype: double/twin two-compartment pet stroller, why_same_subcategory: same frame/canopy/handle/wheels, two fabric pet cabins}
  primary_axis: {slot: chassis cabin-count, diversity_axis: ① multiplicity N=2, target_candidate: two stacked fabric cabins}
  structural_delta:
    change: [refactor cabin box into shared helper emitted twice (cabin_{idx}), stacked upper+lower tiers with shelf divider, raise frame/top_rim]
    keep_parts: [frame, top_rim, side_rail_0, side_rail_1, canopy, canopy_hinge, handle, handle_hinge, wheels+spins]
    joint_policy: both cabins FIXED to frame; single canopy over top tier
    interface_policy: shelf divider between tiers, shared upright frame
  multiplicity: {applies: true, target_n: 2, copied_object: fabric cabin box, placement_rule: two tiers stacked along +Z}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [wheel/front-mech/handle/canopy change, cabin body-family change, >2 tiers]}
  acceptance_focus: [two loop-emitted indexed cabins, single canopy, frame carries both]
- variant_id: rec_pet_stroller_var_form_enclosed_dome
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__002_png_f746b67563c44f6f8a732e97a638d7ff
  positioning: {product_archetype: fully enclosed escape-proof mesh-dome pet stroller, why_same_subcategory: wheeled base/handle/storage retained, top still opens}
  primary_axis: {slot: cabin body form, diversity_axis: ③, target_candidate: fully enclosed zip-around mesh dome}
  structural_delta:
    change: [extend canopy into a closed dome shell wrapping front/top/sides to cabin rim, add vertical mesh side walls closing the gap]
    keep_parts: [base, seat_floor, side_panel_0, side_panel_1, rear_fabric_panel, front_fabric_panel, handle, base_to_handle, front_wheel, rear_wheel_0, rear_wheel_1, all wheel joints]
    joint_policy: retain base_to_canopy revolute (widen upper limit) as the top-open access
    interface_policy: dome seats onto cabin rim seam, hinges at canopy_hinge_bar
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [translucent dome mesh finish], forbidden: [wheel/chassis change, rigid shell, remove top-open revolute]}
  acceptance_focus: [enclosure reads as continuous dome, still lifts open on revolute]
- variant_id: rec_pet_stroller_var_mechanism_reversible_handle
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__pet_stroller__002_png_f746b67563c44f6f8a732e97a638d7ff
  positioning: {product_archetype: reversible swing-over handle stroller (push front or back), why_same_subcategory: same jogger frame/cabin/canopy/3 wheels}
  primary_axis: {slot: push handle, diversity_axis: ②, target_candidate: reversible wide-arc revolute handle}
  structural_delta:
    change: [relocate handle pivot to high transverse hinge on side rails, widen base_to_handle revolute to ~[-1.4,1.4], lengthen arms to clear canopy, add two end-position detent bosses]
    keep_parts: [base, seat_floor, canopy, base_to_canopy, handle, handle_arm_0, handle_arm_1, foam_grip, front_wheel, rear_wheel_0, rear_wheel_1, all wheel joints]
    joint_policy: keep one revolute handle joint, widen range only (no prismatic, no second joint)
    interface_policy: transverse hinge barrel high on frame, detent locks at both ends
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [second handle joint, telescoping, wheel/cabin/canopy change]}
  acceptance_focus: [handle sweeps rear-to-front over canopy on one revolute, grip clears top, no collision]
```

## Compatibility Probes
None emitted. The only genuinely risky interface (rigid pod clamp vs frame) is already exercised by `form_rigid_carrier` on parent A; re-testing it on the jogger frame would be marginal, so no probe is added (coverage first, no padding).

## Blocked / Excluded
- reclining backrest mechanism: pet cabins are flat bassinets; a reclining seat-back reads as a baby/child stroller feature -> would drift toward the baby-stroller neighbor. Blocked.
- open-top flatbed / no-canopy pet wagon: drifts to the pet wagon / utility cart neighbor. Blocked.
- 6+ wheel / side-by-side twin-frame: not a real pet-stroller archetype; double-pet need already covered by stacked `skeleton_double_cabin`. Excluded.
- foot-brake pedal, cup-holder/tray accessory, tire tread/pneumatic-vs-EVA, fabric color: ④/⑤/⑥ only — recorded, not forked.

## underfilled_reason
Honest structural vocabulary for pet strollers converges at 9 candidate anchors (2 origins + 7 forks), the low end of the normal band. Every supported slot already has >=2 structurally distinct candidates; remaining variation is either ④/⑤/⑥ (tire type, fabric palette, mesh pattern, accessories) or drifts into neighbor subcategories (recline -> baby stroller, open flatbed -> pet wagon). No filler variants added.
