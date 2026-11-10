# Source Map — Pet_Animal related / Pet carrier

slug `pet_carrier` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_soft-sided-airline-pet-carrier-purple-fabric-rou_20260708_082416_982083_6d7f454b` — picture/Pet_Animal related/Pet carrier/001.png
- `rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe_20260708_082415_848209_61cc686d` — picture/Pet_Animal related/Pet carrier/002.png

## Variants generated this batch (10 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_pet_carrier_var_backpack` | backpack | PASS | 2 | 0 |
| `rec_pet_carrier_var_basket` | basket | PASS | 1 | 1 |
| `rec_pet_carrier_var_expandable` | expandable | PASS | 3 | 1 |
| `rec_pet_carrier_var_grate_n4` | grate_n4 | PASS | 1 | 1 |
| `rec_pet_carrier_var_grate_n9` | grate_n9 | PASS | 1 | 1 |
| `rec_pet_carrier_var_probe_double_door` | probe_double_door | PASS | 2 | 1 |
| `rec_pet_carrier_var_rolling` | rolling | PASS | 6 | 1 |
| `rec_pet_carrier_var_slide_tray` | slide_tray | PASS | 2 | 1 |
| `rec_pet_carrier_var_topload` | topload | PASS | 1 | 1 |
| `rec_pet_carrier_var_wire_cage` | wire_cage | PASS | 1 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Pet_Animal related / Pet carrier — variant plan

slug `pet_carrier` · pattern **mixed** (single body root + independently articulated access panels; multiplicity on wire-grate bars / vents / wheels)

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Pet carrier
  core_identity: a portable, fully-enclosing container that holds one (or one small) pet for travel, with at least one openable access panel/door and a way to carry it (handle/strap/wheels).
  must_keep:
    - encloses a single pet in a defined cabin with ventilation
    - at least one real openable access (door/hatch/lid) with a working joint
    - a carry means (top handle, shoulder strap, trolley handle, or backpack harness)
  must_not_become:
    - stationary animal cage / birdcage / aviary / kennel furniture (non-portable)
    - rolling luggage / suitcase / utility cart / pet stroller
    - laundry basket / storage bin / cooler / toolbox / drawer unit
    - human backpack / rucksack / sling / baby carrier
  image_evidence:
    - 001 soft duffel: purple fabric body, domed grey-mesh vented top, swing-up top mesh hatch, fold-down front mesh door, large side mesh window, grey webbing straps + arched top handle, blue pet pad inside
    - 002 hard kennel: tan tapered upper shell with oval vent-hole rows, black lower tub, side-hinged black wire-grate front door, molded top carry handle, rim-flange latch clips
  parent_evidence:
    - A (soft): carrier_body root; top_hatch REVOLUTE swing-up (axis Y); front_door REVOLUTE fold-down (bottom hinge, axis Y); section_loft dome + boolean_difference hatch cut; tube_from_spline carry_handle_loop; looped straps/windows; pet_pad
    - B (hard): kennel_body root (cadquery lofted+shelled upper shell & tub fused into one body); wire_door REVOLUTE side-swing (axis Z, tilted to shell slope); molded handle (base+risers+grip); loop-emitted oval vents (rows 7/6/5), side_latch_clip_{i}_{j}, wire grate N_VBARS=6 / N_HBARS=3
```

## Origins (full account, 2/2 anchored)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_soft-sided-airline-pet-carrier-purple-fabric-rou_20260708_082416_982083_6d7f454b` | 001 | soft-sided fabric duffel; domed mesh top; two revolute openings (top hatch + front door); webbing handle + shoulder strap; soft floor | body=soft_fabric_envelope / open=top_hatch+front_fold_door / support=soft_floor / handle=webbing_top+shoulder_strap |
| B `rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe_20260708_082415_848209_61cc686d` | 002 | rigid molded two-shell clamshell (tan upper + black tub, rim flange, latch clips); side-swing wire-grate door; molded top handle; rigid tub floor | body=rigid_clamshell / open=side_swing_grate_door / support=rigid_tub / handle=molded_rigid / N=grate_bars,vents,clips |

## Slots and Candidates
- **body_form (③)**: soft_fabric_envelope(A) / rigid_molded_clamshell(B) / open_wire_cage_lattice(fork wire_cage) / woven_wicker_basket(fork basket) — 4 candidates
- **opening_or_motion (②)**: top_hatch_swing_up(A) / front_fold_down_door(A) / side_swing_grate_door(B) / rear_hinged_top_load(fork topload) / slide_out_bottom_tray(fork slide_tray, PRISMATIC) / expandable_side_pod(fork expandable, PRISMATIC) — 6 candidates
- **support_or_base**: soft_floor(A) / rigid_tub(B) / wheeled_rolling_base(fork rolling, casters + telescoping handle) — 3 candidates
- **handle_or_grip**: webbing_top+shoulder_strap(A) / molded_rigid(B) / telescoping_trolley(rides with rolling) / backpack_harness(fork backpack) — 4 candidates
- **multiplicity (N)**: wire-grate bar count — N=6(B origin) / N=4 coarse(fork grate_n4) / N=9 dense(fork grate_n9) — 3 samples

Each supported slot reaches >=2 structurally distinct candidates.

## Six-Axis Diversity Audit
| axis | status | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | box+dome monocoque w/ 2 lids (A); clamshell 2-shell fused + door (B); open wire lattice frame (wire_cage); woven basket envelope + lid (basket); rolling base+wheels+telescoping (rolling); rear-harness back-worn (backpack) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | revolute top-hinge (A), revolute bottom-hinge fold-down (A), revolute vertical-axis side door (B), revolute rear top-load lid (topload), PRISMATIC slide tray (slide_tray), PRISMATIC expandable pod (expandable), PRISMATIC telescoping handle + CONTINUOUS wheel spin (rolling) |
| ③ primary form family | source-backed (origin + forked_anchor) | soft fabric envelope / rigid molded clamshell / open wire lattice / woven basket — 4 anchors |
| ④ surface decoration | record_only / world_knowledge_extrapolation (companion) | mesh windows, oval vent-hole rows, wire-grate pattern, piping, logo/brand patches; extrapolate weave pattern, printed decals — never standalone |
| ⑤ proportion / size / travel | record_only (companion) | carrier length ~0.45–0.65 m; door swing 1.5–1.6 rad; top hatch 0–2.4 rad; top-lid ~1.9 rad; tray travel ~0.18 m; pod travel ~0.12 m; trolley handle ~0.25 m |
| ⑥ material / palette / finish | record_only (companion) | purple fabric+grey mesh (A); tan/black plastic (B); black/chrome wire; natural rattan; grey/blue pad; strap greys |

## Multiplicity / Copy Logic
- **count_param (primary N axis):** `N_VBARS` / `N_HBARS` on `wire_door` (B). Loop-emitted `door_wire_vertical_{i}` / `door_wire_horizontal_{i}` cylinders, even spacing between border wires, FIXED decoration on the `wire_door` part.
- **N samples:** 6 (B origin) / 4 coarse (grate_n4) / 9 dense (grate_n9) → 3 samples expose copy logic.
- **suggested N_range:** vertical [3,12], horizontal [2,6].
- **secondary count params (record_only, not swept):** `side_latch_clip_{i}_{j}` (3 per side + rear + 2 front); oval vent rows (7/6/5); `caster_wheel_{i}` fixed 4-corner copies on the rolling fork (fixed count, not an N-sweep).

## Budget decision
Richness band: **normal (low end)** — 11 candidate anchors (2 origins + 9 forks). Honest structural vocabulary for a pet carrier is moderate: 4 real form families, 6 access mechanisms across revolute/prismatic/continuous, 3 support modes, and one clean loop-based multiplicity. Coverage-first, no ④/⑤/⑥ padding. One compatibility_probe (double_door) is emitted but not counted toward budget.

## Variant cards (one per fork)
```yaml
- variant_id: rec_pet_carrier_var_wire_cage
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: collapsible all-metal wire travel crate, why_same_subcategory: enclosed single-pet cabin, one latched swing door, top handle}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: open_wire_cage_lattice}
  structural_delta:
    change: [replace molded upper_shell+tub with welded-wire cage frame + loop-emitted bars + floor pan]
    keep_parts: [kennel_body, wire_door, body_to_door, door_latch_grip, handle_grip_bar]
    joint_policy: preserve the single door revolute
    interface_policy: door hinges on the front cage frame; bars welded to corner posts/rails
  multiplicity: {applies: true, target_n: null, copied_object: cage_bar_v/h, placement_rule: regular grid on walls/roof}
  companion_variations: {allowed_④⑤⑥: [black/chrome wire palette], forbidden: [category drift to birdcage/aviary]}
  acceptance_focus: [door still swings and clears, cage reads portable with handle]

- variant_id: rec_pet_carrier_var_basket
  source_type: forked_anchor
  parent_record_id: rec_soft-sided-airline-pet-carrier-purple-fabric-rou...
  positioning: {product_archetype: wicker/rattan pet basket with hinged domed lid, why_same_subcategory: enclosed woven body, top-opening lid, carry handle}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: woven_wicker_basket}
  structural_delta:
    change: [replace fabric walls + lofted dome with woven basket shell + weave bands/stakes + domed woven lid]
    keep_parts: [carrier_body, top_hatch, body_to_top_hatch, carry_handle_loop, pet_pad]
    joint_policy: preserve the top_hatch revolute
    interface_policy: lid hinges on rear basket rim; handle arches over lid
  multiplicity: {applies: true, target_n: null, copied_object: weave_band/stake, placement_rule: horizontal courses / vertical stakes}
  companion_variations: {allowed_④⑤⑥: [natural rattan palette, weave texture], forbidden: [laundry/picnic basket drift]}
  acceptance_focus: [lid opens over full opening, basket reads enclosed]

- variant_id: rec_pet_carrier_var_topload
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: top-loading hard travel kennel, why_same_subcategory: rigid tub + hinged hard cover + handle}
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: rear_hinged_top_load_lid}
  structural_delta:
    change: [upper shell becomes top_shell_lid child; new rear-hinge body_to_top_lid revolute; remove front door]
    keep_parts: [kennel_body, lower_tub, tub_rim_flange, handle_base_plate, handle_riser, handle_grip_bar, side_latch_clip]
    joint_policy: replace the front side-swing revolute with a rear top-load revolute (one primary axis)
    interface_policy: lid seats on rear rim hinge; front latch clips become lid catch
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [keep vent decoration], forbidden: [bin/cooler drift, wheels, wire/fabric shell]}
  acceptance_focus: [lid rises to ~1.9 rad and clears, closed lid seats without penetration]

- variant_id: rec_pet_carrier_var_slide_tray
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: hard kennel with slide-out cleaning tray, why_same_subcategory: same enclosed shell + removable floor tray}
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: slide_out_bottom_tray (prismatic)}
  structural_delta:
    change: [tub becomes open shell w/ inner rails; add slide_out_tray child on new body_to_tray prismatic (+X ~0.18 m)]
    keep_parts: [kennel_body, lower_tub, kennel_upper_shell, wire_door, body_to_door, tub_rim_flange]
    joint_policy: add exactly one prismatic (tray); keep the door revolute
    interface_policy: tray rides on molded tub rails through a base slot
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [tray palette], forbidden: [drawer/cart/litter-furniture drift]}
  acceptance_focus: [tray slides out on prismatic, closed tray flush with base]

- variant_id: rec_pet_carrier_var_expandable
  source_type: forked_anchor
  parent_record_id: rec_soft-sided-airline-pet-carrier-purple-fabric-rou...
  positioning: {product_archetype: airline expandable soft carrier w/ pop-out mesh side, why_same_subcategory: same duffel body + one expanding side pod}
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: expandable_side_pod (prismatic)}
  structural_delta:
    change: [replace left_side_wall + left_window_mesh with expandable_side_pod child on new body_to_side_pod prismatic (+Y ~0.12 m)]
    keep_parts: [carrier_body, top_hatch, body_to_top_hatch, front_door, body_to_front_door, carry_handle_loop, right_window_mesh]
    joint_policy: add exactly one prismatic (pod); keep both door revolutes
    interface_policy: pod seats flush stowed, mesh/trim ride with it
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [expanded vs stowed width], forbidden: [tent/popup crate/luggage drift, wheels, rigid shell]}
  acceptance_focus: [pod translates out and back, flush closed pose]

- variant_id: rec_pet_carrier_var_rolling
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: wheeled rolling pet carrier / trolley, why_same_subcategory: same enclosed shell that rolls instead of hand-carry}
  primary_axis: {slot: support_or_base, diversity_axis: ②, target_candidate: wheeled_rolling_base + telescoping handle}
  structural_delta:
    change: [add wheel_base_frame + 4 caster_wheel_{i} on continuous wheel_spin_{i}; add trolley_handle on prismatic body_to_trolley_handle (~0.25 m)]
    keep_parts: [kennel_body, lower_tub, kennel_upper_shell, wire_door, body_to_door]
    joint_policy: add one coherent rolling-base module (4 continuous wheels + 1 prismatic handle); keep the door revolute
    interface_policy: casters at frame corners; handle telescopes up rear wall
  multiplicity: {applies: true, target_n: 4, copied_object: caster_wheel, placement_rule: 4-corner grid (fixed count)}
  companion_variations: {allowed_④⑤⑥: [wheel/handle palette], forbidden: [suitcase/cart/stroller drift, wire/fabric shell]}
  acceptance_focus: [wheels spin, handle telescopes, enclosure identity retained]

- variant_id: rec_pet_carrier_var_backpack
  source_type: forked_anchor
  parent_record_id: rec_soft-sided-airline-pet-carrier-purple-fabric-rou...
  positioning: {product_archetype: wearable pet backpack carrier, why_same_subcategory: enclosed single-pet cabin, mesh vents, real zip door, worn on back}
  primary_axis: {slot: handle_or_grip, diversity_axis: ①, target_candidate: backpack_harness}
  structural_delta:
    change: [replace carry_handle_loop + shoulder straps with semi-rigid back_panel + 2 shoulder_strap_{i} + sternum_clip + top grab_handle]
    keep_parts: [carrier_body, top_hatch, body_to_top_hatch, front_door, body_to_front_door, left_window_mesh, right_window_mesh, pet_pad]
    joint_policy: preserve both door revolutes (harness parts static); not static_only
    interface_policy: back_panel bonded to rear_end_wall; straps sweep panel top->base
  multiplicity: {applies: true, target_n: 2, copied_object: shoulder_strap, placement_rule: mirrored pair}
  companion_variations: {allowed_④⑤⑥: [strap/panel palette, padding proportion], forbidden: [human backpack/sling/baby-carrier drift]}
  acceptance_focus: [doors still articulate, harness reads wearable, cabin stays enclosed]

- variant_id: rec_pet_carrier_var_grate_n4
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: wide-bar coarse-grate kennel, why_same_subcategory: same carrier, coarser door grate}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: N_VBARS=4/N_HBARS=2}
  structural_delta:
    change: [change only wire-grate copy counts to coarse grid]
    keep_parts: [kennel_body, wire_door, body_to_door, door_border_vertical, door_border_horizontal, door_wire_vertical, door_wire_horizontal]
    joint_policy: preserve the door revolute
    interface_policy: bars even-spaced between border wires
  multiplicity: {applies: true, target_n: 4, copied_object: door_wire_vertical/horizontal, placement_rule: even spacing}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any other slot change]}
  acceptance_focus: [loop-emitted bars, count changed only, tests pass]

- variant_id: rec_pet_carrier_var_grate_n9
  source_type: forked_anchor
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: fine-grate small-pet kennel, why_same_subcategory: same carrier, denser door grate}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: N_VBARS=9/N_HBARS=5}
  structural_delta:
    change: [change only wire-grate copy counts to dense grid]
    keep_parts: [kennel_body, wire_door, body_to_door, door_border_vertical, door_border_horizontal, door_wire_vertical, door_wire_horizontal]
    joint_policy: preserve the door revolute
    interface_policy: bars even-spaced between border wires
  multiplicity: {applies: true, target_n: 9, copied_object: door_wire_vertical/horizontal, placement_rule: even spacing}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any other slot change]}
  acceptance_focus: [loop-emitted bars, count changed only, tests pass]

- variant_id: rec_pet_carrier_var_probe_double_door
  source_type: compatibility_probe
  parent_record_id: rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe...
  positioning: {product_archetype: dual-access hard kennel (front door + top lid), why_same_subcategory: single pet enclosure with two openings}
  primary_axis: {slot: opening_or_motion, diversity_axis: probe, target_candidate: front_door + top_load_lid combined}
  structural_delta:
    change: [keep front wire_door revolute; add top_load_lid child on rear-hinge body_to_top_lid revolute]
    keep_parts: [kennel_body, lower_tub, kennel_upper_shell, wire_door, body_to_door, side_latch_clip, tub_rim_flange]
    joint_policy: two revolutes coexisting (probe)
    interface_policy: front-door cut + top-lid cut share the front flange corner
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [storage-crate drift, wheels, wire/fabric shell]}
  acceptance_focus: [both panels seat closed without collision at shared corner; latch clearance]
```

## Fork job summary
- Emitted 10 fork jobs: 9 candidate-anchor forks + 1 compatibility_probe.
- origin_anchor (no fork): A (soft), B (hard) — already demonstrate soft/rigid form, 3 revolute mechanisms, both handle types, grate N=6.

## Blocked / gated
- `pet_stroller` (four-wheel push stroller with mesh pod): borderline neighbor to Pet carrier; excluded to avoid category drift — covered functionally enough by `rolling`.
- `backpack` is included but gated: keep the enclosed pet cabin + mesh vents + real pet door so it does not drift into a human backpack.
- No ④/⑤/⑥-only jobs emitted (recorded as companion/record_only per audit).

underfilled_reason: none for the low-normal target; pool intentionally sized to honest structural vocabulary (coverage-first, no padding).
