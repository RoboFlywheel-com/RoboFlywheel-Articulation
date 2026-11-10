# Source Map — Pet_Animal related / Bird cage

slug `bird_cage` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_use-the-attached-reference-image-picture-pet-ani_20260707_080712_140187_291ba037` — picture/Pet_Animal related/Bird cage/002.png
- `rec_pet_animal_related__bird_cage__001_png_eaa2a62a24fa41aa9bbea342d753cb52` — picture/Pet_Animal related/Bird cage/001.png

## Variants generated this batch (11 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_bird_cage_var_accessory_feedcups` | accessory_feedcups | PASS | 2 | 1 |
| `rec_bird_cage_var_mechanism_dropfront` | mechanism_dropfront | PASS | 2 | 1 |
| `rec_bird_cage_var_mechanism_slidedoor` | mechanism_slidedoor | PASS | 1 | 1 |
| `rec_bird_cage_var_mechanism_topopen` | mechanism_topopen | PASS | 3 | 1 |
| `rec_bird_cage_var_n3_perch` | n3_perch | PASS | 2 | 1 |
| `rec_bird_cage_var_n_bars_coarse` | n_bars_coarse | PASS | 2 | 2 |
| `rec_bird_cage_var_roof_gable` | roof_gable | PASS | 2 | 1 |
| `rec_bird_cage_var_skeleton_flattop` | skeleton_flattop | PASS | 2 | 1 |
| `rec_bird_cage_var_skeleton_hexagon` | skeleton_hexagon | PASS | 2 | 1 |
| `rec_bird_cage_var_support_hanging` | support_hanging | PASS | 2 | 1 |
| `rec_bird_cage_var_support_legstand` | support_legstand | PASS | 2 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Pet_Animal related / Bird cage

slug `bird_cage` · pattern **mixed** (single cage/frame root with independently articulated door + latch children; perch/bar/caster multiplicity via loops)
richness band: **normal** · candidate anchors total: **13** (2 origins + 11 forks) · fork jobs emitted: **11**

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Bird cage
  core_identity: An enclosed barred/wire cage for housing birds, with an openable access door, interior perch(es), and a bottom tray/base.
  must_keep:
    - barred/wire enclosure that visually contains a bird
    - at least one hinged or sliding access door (real non-fixed joint)
    - interior perch and a droppings tray / base pan
  must_not_become: [birdhouse/nest box (solid walls), terrarium/aquarium, hamster/rodent cage, display case/vitrine, lantern/pendant lamp]
  image_evidence:
    - "002.png: tall rectangular black cage, barrel-vault/domed arched top, arched cut-out front door with latch, front-mounted feeder cups, slide-out bottom tray on casters"
    - "001.png: small round/cylindrical brass cage, hemispherical dome roof with crown finial + top hanging hook, vertical bars on a circle, single wood perch, footed base tray"
  parent_evidence:
    - "A (box): parts cage/door/latch; door_hinge + latch_pivot revolute; box wire walls, barrel-vault roof arches (_add_arch), arched door cut-out + fixed_door_frame, 2 wood perches, slide-out tray + 4 casters, tray risers"
    - "B (round): parts base_tray/wire_frame/perch/access_door/latch; frame_to_door + door_to_latch revolute, tray_to_frame + frame_to_perch fixed; 36 radial bars on CAGE_R hoops, roof meridians to crown ring, top hook, single perch, footed lathe tray"
```

## Origins (full reconciliation, 2/2 anchored)
| id | pic | built form | mesh role |
|---|---|---|---|
| A `rec_use-the-attached-reference-image-picture-pet-ani_20260707_080712_140187_291ba037` | 002 | tall **rectangular box** + barrel-vault roof; arched cut-out front door + latch; 2 wood perches; slide-out tray on 4 casters | ③ box / ② side-hinge door / support caster-stand / N perch=2 |
| B `rec_pet_animal_related__bird_cage__001_png_eaa2a62a24fa41aa9bbea342d753cb52` | 001 | small **round cylinder** + dome roof + crown finial + top hook; cut-out door + latch; single perch; footed tray | ③ round / ② side-hinge door / support footed-tray+hook / N perch=1 |

## Slots and Candidates
- **A body_form / roof (③ primary form family)**: barrel-vault box (A) / dome round (B) / flat open-top box (fork skeleton_flattop) / gabled peaked-roof box (fork roof_gable) / hexagonal prism (fork skeleton_hexagon)
- **B opening_or_motion (② joint/mechanism)**: side-hinge revolute door (A,B) / bottom-hinge drop-front (fork mechanism_dropfront) / vertical guillotine prismatic slide (fork mechanism_slidedoor) / top hatch revolute lift (fork mechanism_topopen); latch revolute keeper (A,B)
- **C support_or_base (① skeleton/topology)**: rolling caster stand + slide-out tray (A) / footed tabletop tray + top hook (B) / four-leg detachable stand w/ lower shelf (fork support_legstand) / hanging bail, no feet (fork support_hanging)
- **D internal_structure / perches (N multiplicity)**: perch N=1 (B) / N=2 (A) / N=3 (fork n3_perch); mounted feeder cups N=2 (fork accessory_feedcups)
- **E wall bar multiplicity (N)**: dense finch spacing (A,B origins) / coarse heavy-gauge wide spacing (fork n_bars_coarse)

### Slot coverage counts (structurally distinct candidates)
- body_form/roof (③): 5 · door mechanism (②): 4 · support/base (①): 4 · perch N: 3 · feeder N: 1 · bar N: 3

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | box(A) / round(B) / hexagonal-prism(fork); support skeletons caster-stand(A) / footed-tray(B) / leg-stand(fork) / hanging-bail(fork) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | side-hinge revolute door(A,B) + latch revolute(A,B); + drop-front bottom revolute(fork), guillotine prismatic slide(fork), top-hatch revolute(fork) |
| ③ primary form family | source-backed (origin + forked_anchor) | barrel-vault box(A) / dome round(B) / flat-top box(fork) / gable-peak box(fork) / hexagonal prism(fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | bar-mesh grid density, powder-coat vs brass finish, crown finial + scrollwork feet (B), decorative gable infill; host-conformal only, no standalone variant |
| ⑤ proportion / size / travel | record_only (companion) | tall floor cage ~1.65 m (A) vs small tabletop ~0.8 m (B); door swing ±1.35, latch ±1.57; may ride along as companion, never standalone |
| ⑥ material / palette / finish | record_only (companion) | black powder-coated steel (A) / aged brass + dark bronze (B) / white / wood-trim perches; companion only |

## Multiplicity / Copy Logic
- **perches** — count_param `n_perches`; N samples {1 (B), 2 (A), 3 (fork n3_perch)}; copied object = wood perch rod; naming `perch_{i}`; placement = stacked at evenly spaced interior heights spanning cage width; joint policy = fixed (dowel ends seated through opposing side wires); suggested N_range [1,4].
- **wall vertical bars** — count_param `bar_count` (A: ~13/face + 9/side; B: 36 radial); N samples {dense (A,B origins), coarse (fork n_bars_coarse)}; loop-emitted `*_vertical_{i}`; placement = even linear spacing per face (box) or radial (round); joint policy = fixed; suggested N_range [8,40].
- **feeder cups** — count_param `n_feed_cups`; N sample {2 (fork accessory_feedcups)}; copied object = cup+bracket; naming `feed_cup_{i}`; placement = mounted on front bars at two heights; joint policy = fixed to wall.
- **casters** — N=4 (A), loop-emitted `caster_*_{ix}_{iy}`, fixed swivel modeled static; recorded, not fork-swept.

## Variant Cards (11 forks)

```yaml
- variant_id: rec_bird_cage_var_skeleton_flattop
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: body_form/roof, diversity_axis: ③, target_candidate: flat open-play top}
  structural_delta: {change: [replace barrel-vault arches+gable infill with flat top grid at spring_z, loop-emitted parallel top wires + 4 top rails], keep_parts: [cage, door, latch, walls, perches, door_hinge, latch_pivot], joint_policy: preserve, interface_policy: corner posts terminate at flat top}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette, tall proportion], forbidden: [door/base/cross-section change]}
  acceptance_focus: [flat top compiles, door still swings, box walls intact]

- variant_id: rec_bird_cage_var_roof_gable
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: body_form/roof, diversity_axis: ③, target_candidate: peaked A-frame gable roof}
  structural_delta: {change: [two-slope ridge ribs + ridge purlin + sloped roof wires + triangular gable-end infill], keep_parts: [cage, door, latch, walls, perches, door_hinge, latch_pivot], joint_policy: preserve, interface_policy: ridge apex above spring_z}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette], forbidden: [becoming solid birdhouse, base/door change]}
  acceptance_focus: [ridge geometry, gable infill closes ends]

- variant_id: rec_bird_cage_var_skeleton_hexagon
  source_type: forked_anchor
  parent_record_id: B (round)
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: hexagonal prism}
  structural_delta: {change: [circular hoops->hexagonal ring frames (6 posts+6 edge rails/level), radial bar loop->bars along 6 faces, roof meridians from 6 corners to crown], keep_parts: [base_tray, wire_frame, perch, access_door, latch, top_hook, frame_to_door, door_to_latch], joint_policy: preserve, interface_policy: door cut into one face}
  multiplicity: {applies: false}
  companion_variations: {allowed: [brass palette, hook], forbidden: [lantern drift, door/support change]}
  acceptance_focus: [6-fold symmetry, door on one face, crown closes]

- variant_id: rec_bird_cage_var_mechanism_dropfront
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: bottom-hinged drop-front door}
  structural_delta: {change: [move door_hinge to sill, horizontal X axis at door_bottom, free top edge swings out+down; latch keeper to top edge], keep_parts: [cage, door, latch, cut-out aperture, fixed_door_frame, perches, latch_pivot], joint_policy: replace one revolute axis orientation, interface_policy: bottom-edge pivot}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette], forbidden: [prismatic swap, body/base change]}
  acceptance_focus: [door folds to horizontal, single revolute]

- variant_id: rec_bird_cage_var_mechanism_slidedoor
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: vertical guillotine sliding door}
  structural_delta: {change: [revolute door_hinge -> PRISMATIC +Z, add 2 fixed side guide rails, door gains side lugs, swing latch -> stop pin/fixed catch], keep_parts: [cage, door, aperture, perches], joint_policy: replace revolute with prismatic, interface_policy: door rides in side rails}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette], forbidden: [window drift, body/base change]}
  acceptance_focus: [prismatic slide clears rails, one sliding joint]

- variant_id: rec_bird_cage_var_mechanism_topopen
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: top-opening hinged roof hatch}
  structural_delta: {change: [split top into fixed rim + hinged top-hatch panel (own part, loop-emitted wires), REVOLUTE horizontal Y hinge at rear top edge lifting up], keep_parts: [cage, door, latch, roof rails, corner_post_*, perches, door_hinge, latch_pivot], joint_policy: add one revolute (front door hinge retained), interface_policy: rear top-edge pivot}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette], forbidden: [chest drift, body/base change]}
  acceptance_focus: [hatch lifts, front door still works, two openings]

- variant_id: rec_bird_cage_var_support_legstand
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: four-leg detachable floor stand}
  structural_delta: {change: [remove casters, add stand skeleton: 4 loop-emitted legs + top apron + lower shelf grid + foot pads; cage seats on apron], keep_parts: [cage, door, latch, wire walls, roof, perches, door_hinge, latch_pivot], joint_policy: preserve, interface_policy: fixed cage-on-apron seat}
  multiplicity: {applies: false}
  companion_variations: {allowed: [black palette], forbidden: [plant-stand drift, body/door change]}
  acceptance_focus: [stand supports cage, legs loop-emitted]

- variant_id: rec_bird_cage_var_support_hanging
  source_type: forked_anchor
  parent_record_id: B (round)
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: hanging bail cage, no floor feet}
  structural_delta: {change: [remove cast feet, flatten tray to shallow suspended catch-pan, add arched carrying bail from crown as sole support], keep_parts: [wire_frame, access_door, latch, perch, base_tray, top_hook, frame_to_door, door_to_latch], joint_policy: preserve, interface_policy: top bail is support}
  multiplicity: {applies: false}
  companion_variations: {allowed: [brass palette], forbidden: [lamp/planter drift, body/door change]}
  acceptance_focus: [no feet, bail centered support, door works]

- variant_id: rec_bird_cage_var_n3_perch
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: internal_structure, diversity_axis: N, target_candidate: 3 stacked perches}
  structural_delta: {change: [loop over 3 heights -> perch_0/1/2 vs hand-placed 2], keep_parts: [cage, door, latch, side_vertical_*, door_hinge, latch_pivot], joint_policy: preserve (fixed perches), interface_policy: dowel ends through side wires}
  multiplicity: {applies: true, target_n: 3, copied_object: wood perch rod, placement_rule: stacked evenly spaced heights}
  companion_variations: {allowed: [wood palette], forbidden: [toys, body/door/base change]}
  acceptance_focus: [3 loop-emitted perches seated, indexed names]

- variant_id: rec_bird_cage_var_accessory_feedcups
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: internal_structure, diversity_axis: N, target_candidate: 2 mounted feeder cups}
  structural_delta: {change: [loop over 2 heights -> feed_cup_{i}+feed_bracket_{i} clipped to front bars], keep_parts: [cage, door, latch, front_vertical_*, perches, door_hinge, latch_pivot], joint_policy: preserve (door/latch remain non-fixed joints; cups fixed), interface_policy: cup brackets grip front wall bars}
  multiplicity: {applies: true, target_n: 2, copied_object: cup+bracket, placement_rule: front bars at 2 heights beside door}
  companion_variations: {allowed: [neutral cup material], forbidden: [standalone dishes, body/door/base change]}
  acceptance_focus: [2 loop-emitted cups mounted, image-evidence match]

- variant_id: rec_bird_cage_var_n_bars_coarse
  source_type: forked_anchor
  parent_record_id: A (box)
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: coarse wide-spaced heavy-gauge bars}
  structural_delta: {change: [drive per-face verticals from bar_count param, ~half count, re-spaced, heavier gauge; rails re-spaced to match], keep_parts: [cage, door, latch, corner_post_*, roof, perches, door_hinge, latch_pivot], joint_policy: preserve, interface_policy: even spacing per face}
  multiplicity: {applies: true, target_n: ~half parent count/face, copied_object: vertical bar wire, placement_rule: even per-face spacing driven by bar_count}
  companion_variations: {allowed: [black palette, heavier gauge as part of spacing], forbidden: [fence/gate drift, body/roof/door/base change]}
  acceptance_focus: [fewer evenly spaced bars, loop-emitted, same silhouette]
```

## Compatibility Probes
None. No high-risk interface combinations were required; all forks change exactly one primary axis on a well-supported interface. (A top-opening hatch + drop-front combo, or hexagon + drop-front, could be probed later if template extraction reveals interface risk, but no probe is emitted now.)

## Blocked / Excluded (no jobs emitted)
- swing / ladder / mirror toys — ④/accessory padding without new structural vocabulary beyond feeder cups.
- material-only (white / brass repaint) and size-only (tall vs small) variants — ⑤/⑥ record_only, never standalone.
- extra bar-density N beyond one coarse sample — origins already show two densities; one clean same-body coarse sample suffices, avoid count enumeration.
- octagonal prism — redundant with hexagonal prism for ③ polygonal-prism family.

## Budget note
13 candidate anchors (2 origins + 11 forks) sits in the **normal** band (12–18). Coverage-first: each supported slot reaches ≥2 structurally distinct candidates; multiplicity covers 3 perch N samples + bar density + feeder cups. No ④/⑤/⑥/scale/material padding was used to reach the count.
