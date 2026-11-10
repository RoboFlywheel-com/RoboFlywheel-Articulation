# Source Map — Mechanical Components_Drivetrain / Automotive differential_Differential gear

slug `automotive_differential_differential_gear` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_mechanical_components_drivetrain__automotive_differential_differential_gear__001_png_aeabd1e9b136406aa0eebf9bf43ee47e` — picture/Mechanical Components_Drivetrain/Automotive differential_Differential gear/001.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_automotive_differential_differential_gear_var_carrier_closed` | carrier_closed | PASS | 5 | 2 |
| `rec_automotive_differential_differential_gear_var_locker` | locker | PASS | 6 | 2 |
| `rec_automotive_differential_differential_gear_var_lsd_clutch` | lsd_clutch | PASS | 5 | 2 |
| `rec_automotive_differential_differential_gear_var_lsd_viscous` | lsd_viscous | PASS | 3 | 2 |
| `rec_automotive_differential_differential_gear_var_pinions4` | pinions4 | PASS | 7 | 1 |
| `rec_automotive_differential_differential_gear_var_ring_bevel` | ring_bevel | PASS | 5 | 2 |
| `rec_automotive_differential_differential_gear_var_torsen` | torsen | PASS | 9 | 2 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Mechanical Components_Drivetrain / Automotive differential_Differential gear

slug `automotive_differential_differential_gear` · pattern **mixed** (single `carrier_cage` root with
independently articulated children: `ring_gear` FIXED, two `side_gear_*` CONTINUOUS, two
`spider_gear_*` CONTINUOUS, one `drive_pinion` CONTINUOUS; loop multiplicity on bolts, spider teeth,
and spider pinion count).

Origin parent (single anchor — every fork forks from this):
- `rec_mechanical_components_drivetrain__automotive_differential_differential_gear__001_png_aeabd1e9b136406aa0eebf9bf43ee47e`
  · picture `picture/Mechanical Components_Drivetrain/Automotive differential_Differential gear/001.png`
  · built form: open automotive differential — cast open cage carrier, large helical spur ring gear
  bolted on (10-bolt circle), 2 opposed bevel spider pinions on a cross shaft, 2 bevel side gears
  with coaxial axle outputs + bearing journals, and a mounted bevel drive pinion in a bearing snout.

---

## subcategory_contract
```yaml
subcategory_contract:
  category: Mechanical Components_Drivetrain
  subcategory: Automotive differential_Differential gear
  core_identity: >
    An automotive differential gear set — a carrier that spins about the axle axis, carries a
    final-drive ring/crown gear driven by an input pinion, and splits torque to two coaxial output
    (side/axle) gears through internal differential gearing, allowing the two outputs to turn at
    different speeds.
  must_keep:
    - final-drive input: a ring/crown gear driven by a mounted input pinion (carrier_to_ring + drive_pinion)
    - a carrier that rotates about the axle centerline and houses the differential gearing
    - exactly two coaxial output side gears with axle outputs (side_gear_0/side_gear_1, CONTINUOUS about X)
    - internal differential gearing (spider/planet/helical) that lets the two outputs differ in speed
    - at least one real non-fixed joint on side gears / internal gears
  must_not_become:
    - a plain gearbox / transmission / speed reducer (no coaxial paired axle outputs)
    - a standalone spur/bevel gear pair or single gear (no carrier, no two-output split)
    - a planetary/epicyclic reduction unit used as a reducer (sun+ring+carrier reducer, not axle split)
    - a spool / solid locked axle (no differential action at all — loses independent-output identity)
  image_evidence:
    - open box-window cast carrier cage with rounded cheeks
    - bolted flange on the ring-gear side with a full bolt circle
    - polished cross shaft crossing the open center
    - opposed bevel spider pinions meshing with two large bevel side gears
    - coaxial axle stub outputs exiting both sides
  parent_evidence:
    - carrier_cage root (helper _carrier_cage_geometry): annular cheeks, 4 window bridges, axle collars,
      ring-gear flange+shoulder, input-pinion bearing snout, cross_shaft visual
    - ring_gear (SpurGear module 0.006, 46 teeth, helix 18°) FIXED via carrier_to_ring
    - side_gear_0/1 (BevelGear 18T) + axle_output + bearing_journal, CONTINUOUS carrier_to_side_* about X
    - spider_gear_0/1 (pinion_hub + 12 radial Box teeth loop), CONTINUOUS carrier_to_spider_* about Y
    - drive_pinion (BevelGear 14T) + pinion_shaft, CONTINUOUS carrier_to_pinion about Y
    - loops: 10 bolts (bolt_i + bolt_shank_i), 12 spider teeth per spider, 2 side + 2 spider gears
```

---

## Slots and Candidates
| slot | candidate | diversity_axis | source_type | evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| internal_mechanism | open 2-pinion bevel spider | ① / N=2 | origin_anchor | origin | spider_gear_0/1, carrier_to_spider_* | converged |
| internal_mechanism | 4-pinion bevel spider (spider cross) | ① / N=4 | forked_anchor | var_pinions4 | spider_gear_0..3 loop, carrier_to_spider_* | planned |
| internal_mechanism | clutch-pack limited-slip (LSD) | ① | forked_anchor | var_lsd_clutch | clutch_plate_* stacks on side hubs | planned |
| internal_mechanism | viscous-coupling limited-slip | ① | forked_anchor | var_lsd_viscous | viscous_drum + interleaved plate loop | planned |
| internal_mechanism | geared / Torsen helical torque-bias | ① / ③ | forked_anchor | var_torsen | helical worm side+planet gears in pockets | planned |
| internal_mechanism | selectable locking differential | ② | forked_anchor | var_locker | dog_collar PRISMATIC engage travel | planned |
| ring_gear_form | helical spur ring gear (disc) | ③ | origin_anchor | origin | ring_gear/toothed_ring | converged |
| ring_gear_form | bevel crown-wheel ring gear | ③ | forked_anchor | var_ring_bevel | ring_gear as BevelGear + repositioned drive_pinion | planned |
| carrier_form | open window cage | ① | origin_anchor | origin | carrier_cage / open_cage | converged |
| carrier_form | closed solid carrier (small ports) | ① | forked_anchor | var_carrier_closed | carrier_cage solid shell + inspection windows | planned |
| output_side_gears | two coaxial bevel side gears | core (fixed=2) | origin_anchor | origin | side_gear_0/1 | converged (invariant) |

Side-gear count is fixed at 2 by the definition of an automotive differential (two axle outputs); it is
NOT a multiplicity axis. Multiplicity lives on the spider/pinion count and on decorative loops.

---

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forks) | internal_mechanism {open-2p, open-4p, clutch-LSD, viscous-LSD, geared/Torsen, locker}; carrier_form {open-cage, closed-solid} |
| ② joint / mechanism | source-backed | origin: FIXED ring, CONTINUOUS side/spider/pinion. Forks add: locker dog-collar PRISMATIC engagement; clutch/viscous plate stacks (record as static or minimal travel). |
| ③ primary form family | source-backed + world_knowledge | ring_gear_form: helical spur disc (origin) vs conical bevel crown-wheel (fork); geared-LSD helical worm gear family |
| ④ surface decoration | record_only / world_knowledge_extrapolation | cast-iron pebble texture, machined ring flank facets, blackened bolt heads, part number/cast rib decals — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only | ring teeth 40–48, module ~0.006; bolt circle 8–12; spider teeth 10–14; side gear 16–20T; carrier Ø ~0.18; side/spider CONTINUOUS; locker travel ~0.01–0.02 |
| ⑥ material / palette / finish | record_only | dark_cast_iron / machined_steel / oiled_gear_steel / bright_tooth_faces / blackened_bolts; alt: nodular grey iron, phosphate-black ring, bronze worm gears (Torsen) |

①②③ and multiplicity N=4 are candidate-anchor axes and are source-backed by origin or a converged fork.
④⑤⑥ are record_only / companion only — never standalone variants and never used to reach the budget.

---

## Multiplicity / Copy Logic
- count_param: `n_spider` (spider/planet pinion count).
  - N samples: 2 (origin, opposed pair on a cross shaft) and 4 (fork var_pinions4, four pinions on a
    4-arm spider cross at 90°).
  - suggested N_range: [2, 4] (2 and 4 are the standard automotive counts; odd counts are not used).
  - copied object: `spider_gear_{i}` part (pinion_hub + 12-tooth loop); naming `spider_gear_{i}`,
    joints `carrier_to_spider_{i}`; placement radial about the axle axis on the spider cross; joint
    policy CONTINUOUS about each pinion's radial axis.
- Existing decorative loops (record_only, `count=`-style, not forks): flange bolts `bolt_{i}` /
  `bolt_shank_{i}` (N=10, range 8–12); spider teeth `tooth_{j}` (N=12, range 10–14); viscous plate
  stack loop for var_lsd_viscous.

---

## Budget decision
- Richness band: **simple** (target 8–12). Chosen total = **8 candidate anchors** (low end).
- Candidate anchors = 1 origin_anchor + 7 forked_anchors.
- underfilled_reason: Differential gear is a narrow, tightly-constrained mechanical subcategory. Core
  identity fixes the output count at exactly 2 side gears and mandates a carrier + ring + input pinion,
  so most vocabulary lives on the internal-mechanism family (open / clutch-LSD / viscous-LSD /
  geared-Torsen / locker), one meaningful ring-form family switch, one carrier-form switch, and one
  spider multiplicity sample. Beyond these the remaining variety is ④⑤⑥ (teeth counts, module,
  finish) which are record_only. No filler added; the 5 canonical differential families plus the 2
  structural sub-variants and the N=4 sample are the honest structural coverage.

---

## Variant cards

```yaml
- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_pinions4
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: heavy-duty 4-pinion open differential (truck/off-road axle), why_same_subcategory: still a carrier-borne ring + two side gears split by bevel spider pinions}
    primary_axis: {slot: internal_mechanism, diversity_axis: "① / N", target_candidate: 4 spider pinions}
    structural_delta:
      change: [replace cross_shaft with a 4-arm spider cross, loop spider_gear_{i} i in range(4) at 90° radial, add carrier_to_spider_{i}]
      keep_parts: [carrier_cage, ring_gear, side_gear_0, side_gear_1, drive_pinion, carrier_to_ring, carrier_to_side_0, carrier_to_side_1, carrier_to_pinion]
      joint_policy: preserve CONTINUOUS side/pinion joints; N=4 spider joints CONTINUOUS about radial axes
      interface_policy: spider pinions mesh with both side gears; hubs captured on spider-cross arms
    multiplicity: {applies: true, target_n: 4, copied_object: spider_gear, placement_rule: radial 90°}
    companion_variations: {allowed_④⑤⑥: [spider tooth count], forbidden: [ring form change, LSD clutch, category drift]}
    acceptance_focus: [4 spider CONTINUOUS joints exist, spiders equally spaced, meshes with both side gears]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_lsd_clutch
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: clutch-type limited-slip differential (LSD), why_same_subcategory: open diff gearing plus friction clutch packs biasing the two side gears — still two axle outputs}
    primary_axis: {slot: internal_mechanism, diversity_axis: "①", target_candidate: clutch-pack LSD}
    structural_delta:
      change: [add stacked clutch_plate_{i} rings between each side gear hub and the carrier cheeks via a loop]
      keep_parts: [carrier_cage, ring_gear, side_gear_0, side_gear_1, spider_gear_0, spider_gear_1, drive_pinion, all carrier_to_* joints]
      joint_policy: preserve all CONTINUOUS gear joints; clutch plates ride with side gears (no new primary joint)
      interface_policy: clutch plate stack seated between side-gear hub and carrier cheek face
    multiplicity: {applies: true, target_n: 6, copied_object: clutch_plate, placement_rule: axial stack}
    companion_variations: {allowed_④⑤⑥: [plate finish], forbidden: [ring form, spider count, category drift]}
    acceptance_focus: [clutch plate stack loop present beside each side gear, side gears still CONTINUOUS]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_lsd_viscous
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: viscous-coupling limited-slip differential, why_same_subcategory: open diff with a sealed interleaved-plate viscous unit coupling the outputs — two axle outputs kept}
    primary_axis: {slot: internal_mechanism, diversity_axis: "①", target_candidate: viscous coupling LSD}
    structural_delta:
      change: [replace open center exposure with a sealed viscous_drum housing enclosing an interleaved plate stack loop coupling the two side hubs]
      keep_parts: [carrier_cage, ring_gear, side_gear_0, side_gear_1, drive_pinion, carrier_to_ring, carrier_to_side_*, carrier_to_pinion]
      joint_policy: preserve CONTINUOUS side/pinion joints; viscous plates ride with side gears
      interface_policy: drum concentric on axle axis, plates alternately keyed to each side hub
    multiplicity: {applies: true, target_n: 8, copied_object: viscous_plate, placement_rule: axial interleave}
    companion_variations: {allowed_④⑤⑥: [drum finish], forbidden: [ring form, category drift]}
    acceptance_focus: [sealed viscous drum + interleaved plate loop present, side gears still CONTINUOUS]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_torsen
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: Torsen / geared torque-biasing helical LSD, why_same_subcategory: carrier + ring + two side gears, but the bevel spider set is replaced by helical worm/planet gearing}
    primary_axis: {slot: internal_mechanism, diversity_axis: "① / ③", target_candidate: geared helical torque-bias}
    structural_delta:
      change: [replace bevel spider_gear_* + bevel side_gear_* with helical worm side gears + paired helical planet worms in carrier pockets]
      keep_parts: [carrier_cage, ring_gear, drive_pinion, carrier_to_ring, carrier_to_side_0, carrier_to_side_1, carrier_to_pinion]
      joint_policy: side worm gears CONTINUOUS about X; planet worms CONTINUOUS about their pocket axes
      interface_policy: helical side worms mesh planet worms in axial pockets
    multiplicity: {applies: true, target_n: 3, copied_object: planet_worm_pair, placement_rule: radial around axle}
    companion_variations: {allowed_④⑤⑥: [bronze worm palette], forbidden: [ring form, category drift]}
    acceptance_focus: [helical worm gears replace bevel spiders, side gears still CONTINUOUS about X]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_locker
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: selectable locking differential (diff-lock), why_same_subcategory: open diff plus a sliding dog collar that can lock one side gear to the carrier}
    primary_axis: {slot: internal_mechanism, diversity_axis: "②", target_candidate: dog-clutch engagement collar}
    structural_delta:
      change: [add a splined dog_collar between side_gear_0 hub and carrier with a PRISMATIC engage joint]
      keep_parts: [carrier_cage, ring_gear, side_gear_0, side_gear_1, spider_gear_0, spider_gear_1, drive_pinion, carrier_to_ring, carrier_to_side_*, carrier_to_spider_*, carrier_to_pinion]
      joint_policy: add exactly one PRISMATIC carrier_to_lockcollar; keep all CONTINUOUS gear joints
      interface_policy: collar slides axially on splines between side-gear dog teeth and carrier dog teeth
    multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
    companion_variations: {allowed_④⑤⑥: [shift-fork groove], forbidden: [ring form, spider count, category drift]}
    acceptance_focus: [one PRISMATIC locker joint with real axial travel, gear joints preserved]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_ring_bevel
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: spiral-bevel crown-wheel final drive (classic rear axle), why_same_subcategory: same carrier + differential gearing, ring gear is a conical crown wheel driven by a bevel pinion}
    primary_axis: {slot: ring_gear_form, diversity_axis: "③", target_candidate: bevel crown wheel}
    structural_delta:
      change: [rebuild ring_gear as a conical BevelGear crown wheel and reposition drive_pinion to mesh at its cone]
      keep_parts: [carrier_cage, side_gear_0, side_gear_1, spider_gear_0, spider_gear_1, carrier_to_ring, carrier_to_side_*, carrier_to_spider_*, carrier_to_pinion, drive_pinion]
      joint_policy: ring still FIXED to carrier; drive_pinion CONTINUOUS repositioned to bevel mesh
      interface_policy: bevel pinion cone meshes crown-wheel cone at the ring perimeter
    multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
    companion_variations: {allowed_④⑤⑥: [hypoid pinion offset, spiral tooth finish], forbidden: [internal mechanism change, spider count, category drift]}
    acceptance_focus: [ring gear is bevel crown-wheel geometry, still FIXED, pinion meshes at cone]

- variant_card:
    variant_id: rec_automotive_differential_differential_gear_var_carrier_closed
    source_type: forked_anchor
    parent_record_id: rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e
    positioning: {product_archetype: closed / solid one-piece differential case, why_same_subcategory: same ring + side + spider gearing inside a closed cast case instead of an open window cage}
    primary_axis: {slot: carrier_form, diversity_axis: "①", target_candidate: closed solid carrier}
    structural_delta:
      change: [rebuild _carrier_cage_geometry as a closed solid shell with small inspection ports instead of large open windows]
      keep_parts: [ring_gear, side_gear_0, side_gear_1, spider_gear_0, spider_gear_1, drive_pinion, cross_shaft, all carrier_to_* joints]
      joint_policy: preserve all joints unchanged
      interface_policy: closed shell keeps axle collars, ring flange, and pinion snout as real anchor faces
    multiplicity: {applies: true, target_n: 4, copied_object: inspection_port, placement_rule: radial}
    companion_variations: {allowed_④⑤⑥: [cast texture], forbidden: [internal mechanism change, ring form, category drift]}
    acceptance_focus: [carrier is a closed solid shell with ports, all internal gears still articulate]
```

## Blocked / Excluded
- spool / mini-spool (solid locked axle): fixes both side gears to the carrier, eliminating differential
  action — violates core_identity (independent output speeds). Blocked, out-of-category.
- odd spider counts (N=3 bevel): not used in real automotive differentials; excluded from N sweep
  (helical planet-worm triples belong to the Torsen fork, not the bevel N sweep).
- ④/⑤/⑥-only variants (teeth-count / module / finish / palette sweeps): record_only, no fork emitted.
