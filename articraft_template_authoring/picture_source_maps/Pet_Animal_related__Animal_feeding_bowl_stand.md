# Source Map — Pet_Animal related / Animal feeding bowl stand

slug `animal_feeding_bowl_stand` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__animal_feeding_bowl_stand__001_png_6e6b108d8ba649f49ff73b129507d7a7` — picture/Pet_Animal related/Animal feeding bowl stand/001.png
- `rec_pet_animal_related__animal_feeding_bowl_stand__002_png_e69950e2deab410ab84b65c09610c323` — picture/Pet_Animal related/Animal feeding bowl stand/002.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_animal_feeding_bowl_stand_var_base_disc` | base_disc | PASS | 1 | 1 |
| `rec_animal_feeding_bowl_stand_var_base_fold` | base_fold | PASS | 5 | 1 |
| `rec_animal_feeding_bowl_stand_var_base_tripod` | base_tripod | PASS | 1 | 1 |
| `rec_animal_feeding_bowl_stand_var_bowl_tilt` | bowl_tilt | PASS | 2 | 1 |
| `rec_animal_feeding_bowl_stand_var_bowls_n3` | bowls_n3 | PASS | 3 | 2 |
| `rec_animal_feeding_bowl_stand_var_diner_platform` | diner_platform | PASS | 2 | 1 |
| `rec_animal_feeding_bowl_stand_var_probe_twin_tilt` | probe_twin_tilt | PASS | 5 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Pet_Animal related / Animal feeding bowl stand

slug: `animal_feeding_bowl_stand`
pattern: **mixed** (linear-chain height column with side-by-side bowl multiplicity (A); central pedestal with radial leg/clip multiplicity (B))
richness band: **simple** (8–12 candidate anchors)
budget decision: **8 candidate anchors** (2 origins + 6 forks) at the LOW end; 1 compatibility_probe (not counted). Coverage-first, no padding.

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Animal feeding bowl stand
  core_identity: an elevated stand/frame that raises one or more open pet feeding bowls off the floor to a comfortable eating height
  must_keep:
    - one or more open feeding bowls held in a support ring / seat
    - a base that lifts the bowl(s) above the floor (legs / pedestal / raised frame)
    - at least one real non-fixed joint (height slide, bowl lift-out, tilt, or fold) unless static_only
  must_not_become:
    - low non-elevated twin-bowl mat / tray / placemat (not raised)
    - cage-/crate-mounted clamp-on bowl holder (mounts to an enclosure, not a floor stand)
    - camera/mic tripod, floor lamp, plant stand, cake stand (host must retain bowl + holder)
    - automatic/gravity food dispenser or fountain (no reservoir/pump mechanism)
  image_evidence:
    - "001: black powder-coated H-skid frame, square upright post, sliding collar with two circular holder rings, two stainless bowls side-by-side, thumb-screw clamp knob for height lock"
    - "002: graphite X cross-base with 4 splayed feet + central hub, telescoping round pedestal tube, single stainless bowl (blue enamel band + white panda/paw print) captured by 4 radial molded clips on a ribbed support ring"
  parent_evidence:
    - "A (001): base_frame (2 feet + crossbar + upright_post + 4 rubber pads); height_carriage (square collar + 2 torus holder rings + welded tabs + clamp_backbone); PRISMATIC base_to_carriage; 2 FIXED bowls (loop); 2 CONTINUOUS clamp knobs"
    - "B (002): base (4 radial capsule feet loop + toe pads + central_hub + hollow_pedestal_sleeve + 3 collars); bowl_holder (sliding_inner_post + top_socket + ribbed_support_ring + 4 radial brackets/clips loop); PRISMATIC height_slide; 1 FIXED bowl"
```

## Slot / Candidate grid
| slot | candidate | diversity_axis | source_type | evidence |
|---|---|---|---|---|
| base_skeleton (①) | H-skid twin-foot frame + square upright post | ① | origin_anchor | A `base_frame` |
| base_skeleton (①) | X cross-base, 4 radial legs + central pedestal | ① | origin_anchor | B `base` |
| base_skeleton (①) | tubular 3-leg splayed tripod pedestal | ① | forked_anchor | fork@B `base_tripod` |
| base_skeleton (①) | solid round weighted disc pedestal | ① | forked_anchor | fork@B `base_disc` |
| base_skeleton (①) | fixed raised "diner" frame, bowls dropped into tabletop cutouts | ① | forked_anchor | fork@A `diner_platform` |
| height_mechanism (②) | PRISMATIC height slide (square post / telescoping tube) | ② | origin_anchor | A `base_to_carriage`, B `height_slide` |
| height_lock (②) | CONTINUOUS rotary thumb-screw clamp knob | ② | origin_anchor | A `carriage_to_knob_{0,1}` |
| bowl_motion (②) | REVOLUTE tilt of bowl holder (angled feeder) | ② | forked_anchor | fork@B `bowl_tilt` |
| base_motion (②) | REVOLUTE fold-flat collapsible legs (storage) | ② | forked_anchor | fork@B `base_fold` |
| bowl_holder | side-by-side torus rings + welded tabs | slot | origin_anchor | A `ring_{i}` / `tab_{i}` |
| bowl_holder | ribbed circular support ring + radial capture clips | slot | origin_anchor | B `ribbed_support_ring` / `upright_clip_{i}` |
| bowl_multiplicity (N) | N=1 bowl | N | origin_anchor | B (single bowl) |
| bowl_multiplicity (N) | N=2 side-by-side bowls | N | origin_anchor | A (loop over 2) |
| bowl_multiplicity (N) | N=3 side-by-side bowls | N | forked_anchor | fork@A `bowls_n3` |

Every supported structural slot reaches ≥2 distinct candidates: base_skeleton 5, height/bowl mechanism ② 4, bowl_holder 2, bowl_multiplicity 3.

## Six-Axis Diversity Audit
| axis | candidate-anchor? | treatment | values |
|---|---|---|---|
| ① skeleton / topology | yes (source-backed) | origin_anchor + forked_anchor | H-skid frame (A) / X cross-pedestal (B) / tripod (fork) / disc pedestal (fork) / raised diner frame (fork) |
| ② joint / mechanism | yes (source-backed) | origin_anchor + forked_anchor | prismatic height slide (A,B) / continuous clamp-knob lock (A) / revolute bowl tilt (fork) / revolute fold legs (fork) / prismatic bowl lift-out (fork@diner) |
| ③ primary form family | yes (source-backed) | origin_anchor | column-on-frame chain (A, box/extrude) vs pedestal-column (B, cylinder/lathe); bowl = open lathe shell (both). No new ③ fork honest → covered by origins |
| ④ surface decoration | not standalone | record_only + world_knowledge_extrapolation | ribbed grip ring (B), lobed knurled clamp knobs (A), rolled rim (A), printed panda/paw marks (B); extrapolate bone/fish/brand emboss (host-conformal only) |
| ⑤ proportion / size / travel | not standalone | record_only | height travel A ≈ 0.19 m (−0.110…0.080), B ≈ 0.09 m (0…0.090); bowl Ø ≈ 0.19–0.30; base footprint span ≈ 0.5 (A) / 0.54 dia (B); tilt limit ~0–25° (fork); may ride as companion on structural forks |
| ⑥ material / palette / finish | not standalone | record_only | powder-coat hammertone black (A), black textured plastic (B), brushed/mirror stainless bowls, blue enamel band (B); palette black/graphite/white/chrome/copper; companion-only |

③: origins already expose the two body-form families (planar box-frame chain vs volumetric pedestal-column); no additional ③ candidate is honestly source-backable without drifting, so ③ is anchored by origins and not separately forked.

## Multiplicity / Copy Logic
- **count_param:** `n_bowls` — side-by-side seats on the H-frame carriage.
  - copied object: bowl (cup+rim+flat_bottom) + `bowl_holder_ring` (torus) + welded `tab` + supporting foot/rubber-pad set.
  - N samples: **1** (B, different base), **2** (A origin, loop), **3** (fork@A `bowls_n3`). suggested N_range **[1,4]**.
  - placement_rule: linear along x, even center-to-center spacing ≈ 0.30–0.34 m; base_crossbar widened per N.
  - naming: `bowl_{idx}`, `ring_{idx}`, `tab_{idx}`, joint `carriage_to_bowl_{idx}`.
  - joint_policy: each bowl FIXED to shared carriage (or short PRISMATIC lift-out in the diner fork); one shared PRISMATIC height slide raises all.
- **secondary loops (not a separate N-sweep):** B's radial feet (count=4) and capture clips (count=4) are loop-emitted; leg count is the ① base-skeleton axis (tripod=3, disc=0), so it is covered by skeleton forks, not a standalone N variant.

## Budget decision
Honest structural vocabulary yields **8 candidate anchors** (2 origins + 6 forks): 3 new ① skeletons, 2 new ② mechanisms, 1 new N sample. This is the LOW end of the simple band and is coverage-complete (every supported slot ≥2 candidates; ②/①/N all source-backed). No ④/⑤/⑥/scale/color padding added.
`underfilled_reason`: object is structurally shallow (base + adjustable holder + open bowl). Further ideas were pruned — see Blocked. One compatibility_probe added for a genuine tilt×N=2 interface risk (not counted toward budget).

## Variant Cards
```yaml
- variant_id: rec_animal_feeding_bowl_stand_var_base_tripod
  source_type: forked_anchor
  parent_record_id: B (002)
  positioning: {product_archetype: tubular tripod raised feeder, why_same_subcategory: still lifts one bowl to feeding height}
  primary_axis: {slot: base_skeleton, diversity_axis: ①, target_candidate: 3-leg splayed tripod pedestal}
  structural_delta: {change: [replace 4 radial capsule feet with 3 tubular legs at 120° on central_hub], keep_parts: [base, central_hub, hollow_pedestal_sleeve, bowl_holder, ribbed_support_ring, bowl, height_slide], joint_policy: preserve prismatic height_slide, interface_policy: legs meet shared central hub carrying pedestal sleeve}
  multiplicity: {applies: true, target_n: 3 legs, copied_object: leg, placement_rule: radial 120°}
  companion_variations: {allowed: [⑥ tube finish], forbidden: [bowl count, holder type, slide add/remove]}
  acceptance_focus: [3-point stability, prismatic joint intact, single bowl seated]

- variant_id: rec_animal_feeding_bowl_stand_var_base_disc
  source_type: forked_anchor
  parent_record_id: B (002)
  positioning: {product_archetype: weighted round-disc pedestal feeder, why_same_subcategory: elevated single bowl}
  primary_axis: {slot: base_skeleton, diversity_axis: ①, target_candidate: solid round weighted disc base}
  structural_delta: {change: [replace radial legs with one low cylindrical weighted disc], keep_parts: [base, central_hub, hollow_pedestal_sleeve, bowl_holder, ribbed_support_ring, bowl, height_slide], joint_policy: preserve prismatic height_slide, interface_policy: pedestal rises from disc center}
  multiplicity: {applies: false, target_n: null}
  companion_variations: {allowed: [⑤ disc diameter], forbidden: [bowl count, holder type, slide add/remove]}
  acceptance_focus: [low-CG stability, prismatic joint intact]

- variant_id: rec_animal_feeding_bowl_stand_var_diner_platform
  source_type: forked_anchor
  parent_record_id: A (001)
  positioning: {product_archetype: elevated twin-bowl diner frame, why_same_subcategory: fixed-height raised feeding stand}
  primary_axis: {slot: base_skeleton, diversity_axis: ①, target_candidate: rigid raised frame with bowl cutouts}
  structural_delta: {change: [remove prismatic column + upright_post, add rigid 4-leg raised top panel with 2 cutouts, seat bowls via short prismatic lift-out], keep_parts: [bowl_0, bowl_1, cup, rim, flat_bottom], joint_policy: replace carriage_to_bowl FIXED with vertical PRISMATIC lift-out (retains non-fixed joint), interface_policy: bowl rim seats in circular tabletop cutout}
  multiplicity: {applies: true, target_n: 2, copied_object: bowl+cutout, placement_rule: linear side-by-side}
  companion_variations: {allowed: [], forbidden: [re-adding height column, non-elevated tray]}
  acceptance_focus: [top panel elevated, bowls drop into cutouts, lift-out prismatic works]

- variant_id: rec_animal_feeding_bowl_stand_var_bowl_tilt
  source_type: forked_anchor
  parent_record_id: B (002)
  positioning: {product_archetype: angle-adjustable slanted feeder, why_same_subcategory: elevated single bowl}
  primary_axis: {slot: bowl_motion, diversity_axis: ②, target_candidate: revolute tilt joint}
  structural_delta: {change: [add yoke/trunnion between top_socket and bowl, replace holder_to_bowl FIXED with REVOLUTE tilt 0–25°], keep_parts: [base, hollow_pedestal_sleeve, bowl_holder, top_socket, ribbed_support_ring, bowl, height_slide], joint_policy: add exactly one revolute tilt, interface_policy: horizontal pivot on yoke}
  multiplicity: {applies: false, target_n: null}
  companion_variations: {allowed: [⑤ tilt limit], forbidden: [lazy-susan spin, base change, bowl count]}
  acceptance_focus: [tilt range no-spill, prismatic slide intact, no self-collision]

- variant_id: rec_animal_feeding_bowl_stand_var_base_fold
  source_type: forked_anchor
  parent_record_id: B (002)
  positioning: {product_archetype: collapsible travel feeder, why_same_subcategory: elevated single bowl when deployed}
  primary_axis: {slot: base_motion, diversity_axis: ②, target_candidate: revolute fold-flat legs}
  structural_delta: {change: [attach each of 4 legs to central_hub via REVOLUTE hinge, deployed↔folded], keep_parts: [base, central_hub, hollow_pedestal_sleeve, bowl_holder, ribbed_support_ring, bowl, height_slide, holder_to_bowl], joint_policy: add revolute fold hinge per leg (only new mechanism), interface_policy: hinge at hub}
  multiplicity: {applies: true, target_n: 4 legs, copied_object: leg, placement_rule: radial, joint hub_to_leg_{idx}}
  companion_variations: {allowed: [], forbidden: [leg-count change as primary axis, slide removal]}
  acceptance_focus: [deployed vs folded poses, stand upright when deployed, prismatic slide intact]

- variant_id: rec_animal_feeding_bowl_stand_var_bowls_n3
  source_type: forked_anchor
  parent_record_id: A (001)
  positioning: {product_archetype: triple-bowl raised feeder (food+water+supplement), why_same_subcategory: multi-bowl elevated stand}
  primary_axis: {slot: bowl_multiplicity, diversity_axis: N, target_candidate: N=3}
  structural_delta: {change: [extend bowl/ring/tab loop 2→3, widen crossbar, add 3rd foot/pad], keep_parts: [base_frame, upright_post, height_carriage, collar_front, cup, rim, flat_bottom, base_to_carriage, clamp_knob_0, clamp_knob_1], joint_policy: each bowl FIXED via carriage_to_bowl_{idx}, one shared prismatic slide, interface_policy: bowl rim over holder ring}
  multiplicity: {applies: true, target_n: 3, copied_object: bowl+ring+tab+support, placement_rule: linear even spacing ~0.30–0.34}
  companion_variations: {allowed: [], forbidden: [vertical stacking, base family change, holder change]}
  acceptance_focus: [3 bowls loop-emitted, base spans 3 seats, prismatic raises all]

- variant_id: rec_animal_feeding_bowl_stand_var_probe_twin_tilt   # compatibility_probe (NOT counted)
  source_type: compatibility_probe
  parent_record_id: A (001)
  positioning: {product_archetype: double slanted diner, why_same_subcategory: twin-bowl elevated stand}
  primary_axis: {slot: bowl_motion×multiplicity, diversity_axis: probe, target_candidate: ② tilt on N=2}
  structural_delta: {change: [replace both carriage_to_bowl FIXED with independent REVOLUTE tilts on yokes], keep_parts: [base_frame, upright_post, height_carriage, ring_0, ring_1, tab_0, tab_1, base_to_carriage], joint_policy: two independent revolute tilts, interface_policy: per-bowl yoke pivot}
  multiplicity: {applies: true, target_n: 2}
  companion_variations: {allowed: [], forbidden: [base change, bowl count change, coupling the two tilts]}
  acceptance_focus: [inter-bowl clearance across tilt range, each bowl clears its own ring + carriage]
```

## Blocked / Excluded
- **cage/crate-mounted clamp bowl holder** — neighbor subcategory (mounts to an enclosure, not a floor stand); listed in must_not_become.
- **automatic gravity feeder / water fountain** — out of category (adds reservoir/pump, not a stand).
- **N=4+ side-by-side bowls** — N∈{1,2,3} already exposes the copy logic; higher N is padding.
- **additional ③ body-form fork** — origins already cover the two honest form families (box-frame chain vs pedestal-column); no further ③ candidate without category drift.
- **pin-detent vs friction height lock as a standalone ②** — mechanically near-identical articulation to existing prismatic slide + clamp knob; folded into ⑤/record_only rather than a fork.

## Emitted jobs
7 jobs total → `/tmp/jobs/animal_feeding_bowl_stand.jobs.txt` (6 candidate-anchor forks + 1 compatibility_probe). Axis files under `/tmp/axis/animal_feeding_bowl_stand_var_*.txt`.
