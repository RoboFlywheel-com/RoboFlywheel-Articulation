# Source Map — Pet_Animal related / Aquarium

slug `aquarium` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__aquarium__001_png_c0bba02ab6f04b8caf4724481d67d630` — picture/Pet_Animal related/Aquarium/001.png
- `rec_pet_animal_related__aquarium__002_png_a9a75dd3247a4ab4b658d4912f1550b0` — picture/Pet_Animal related/Aquarium/002.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_aquarium_var_bowfront` | bowfront | PASS | 2 | 0 |
| `rec_aquarium_var_cylinder` | cylinder | PASS | 2 | 1 |
| `rec_aquarium_var_filter_canister` | filter_canister | PASS | 2 | 1 |
| `rec_aquarium_var_hexagon` | hexagon | PASS | 2 | 1 |
| `rec_aquarium_var_lid_bifold` | lid_bifold | PASS | 2 | 1 |
| `rec_aquarium_var_lid_sliding` | lid_sliding | PASS | 1 | 0 |
| `rec_aquarium_var_plants_n2` | plants_n2 | PASS | 2 | 0 |
| `rec_aquarium_var_plants_n7` | plants_n7 | PASS | 2 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Pet_Animal related / Aquarium

slug `aquarium` · pattern **mixed** (single `tank` root; independently hinged `hood` revolute + nested `feed_flap` revolute; static aquascape contents; plant-cluster multiplicity)

Richness band: **normal** (12–18). Total candidate anchors: **16** (8 origin-backed + 8 forks). Fork jobs emitted: **8**.

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Aquarium
  core_identity: A transparent water-holding glass/acrylic tank for keeping aquatic life, with a rim frame, a top hood/lid (usually with a feed opening), filtration equipment, a substrate/gravel bed, and rooted aquascape contents.
  must_keep:
    - transparent hollow glass basin (separate held panes, not a solid block) that reads as water-tight
    - a top lid/hood covering the opening (hinged, sliding, or split) OR explicit rim-access top
    - internal aquarium hardware and aquascape: filter, gravel bed, plants/rocks
    - at least one real non-fixed joint (hood/lid or flap) unless explicitly static
  must_not_become: [Fish_bowl (open round bowl, no frame/lid/equipment), Terrarium/Vivarium (dry, reptile), Aquarium_stand/Cabinet (furniture), Display_case/Vitrine, Water_tank/Vase]
  image_evidence:
    - "001: rectangular glass tank, black molded hood with dark display/logo panel, hang-on-back filter with intake tube on right side, tan gravel bed, plastic plants + driftwood + rock, angelfish"
    - "002: soft rounded-corner bow tank, black domed hood with pull handle + latch, blue gravel, submerged internal filter, dense plants, rockwork"
  parent_evidence:
    - "A (001) rect: Box glass panes (front/rear/side/bottom), black base+top rails, 4 corner_post loop, rear_hinge_knuckle loop, substrate gravel_bed + gravel_ridge loop, HOB filter (filter_housing/rim_hanger/intake_tube/strainer/outlet_elbow), molded hood_shell (CadQuery, chamfer + feed aperture cut), light_diffuser, control_panel + 3 status_button loop, hood revolute (tank_to_hood), nested feed_flap revolute (hood_to_feed_flap)"
    - "B (002) rounded: CadQuery _rounded_plate glass panes, dark_marble base_plinth, black top_rim ring, water_volume, gravel_bed, internal filter_housing + filter_intake, front_rock/center_rock, 4-plant loop (stem cylinder + 2 leaf boxes), rounded hood_shell w/ cutout, led_light_lens, hood revolute (tank_to_hood), nested flap revolute (hood_to_flap)"
```

## Slots and Candidate Grid
| slot | candidate | axis | source_type | record / evidence | status |
|---|---|---|---|---|---|
| body_form | rectangular box | ③ | origin_anchor | A `..._001_...` | converged |
| body_form | soft rounded-corner | ③ | origin_anchor | B `..._002_...` | converged |
| body_form | bow-front curved panel | ③ | forked_anchor | rec_aquarium_var_bowfront (fork@A) | planned |
| body_form | cylindrical column | ③ | forked_anchor | rec_aquarium_var_cylinder (fork@A) | planned |
| body_form | hexagonal prism | ③ | forked_anchor | rec_aquarium_var_hexagon (fork@A) | planned |
| lid / opening | rear-hinged molded hood (revolute) | ② | origin_anchor | A, B (tank_to_hood) | converged |
| lid / opening | nested feed flap (revolute) | ② | origin_anchor | A, B (hood_to_feed_flap) | converged |
| lid / opening | sliding glass cover (prismatic) | ② | forked_anchor | rec_aquarium_var_lid_sliding (fork@A) | planned |
| lid / opening | split twin-leaf canopy (2× revolute) | ② | forked_anchor | rec_aquarium_var_lid_bifold (fork@A) | planned |
| filtration | hang-on-back (HOB) filter | ① | origin_anchor | A (filter_housing/intake_tube) | converged |
| filtration | submerged internal filter | ① | origin_anchor | B (filter_housing/filter_intake) | converged |
| filtration | external canister + hoses | ① | forked_anchor | rec_aquarium_var_filter_canister (fork@A) | planned |
| aquascape multiplicity | plants N=4 | N | origin_anchor | B (4-plant loop) | converged |
| aquascape multiplicity | plants N=2 (sparse) | N | forked_anchor | rec_aquarium_var_plants_n2 (fork@B) | planned |
| aquascape multiplicity | plants N=7 (dense) | N | forked_anchor | rec_aquarium_var_plants_n7 (fork@B) | planned |
| support/base | integrated rim frame + base trim/plinth | support | origin_anchor | A (base rails/corner posts), B (base_plinth) | converged (single candidate) |

Slot coverage (≥2 structurally distinct candidates where object allows):
- body_form: **5** (rect, rounded, bow-front, cylinder, hexagon)
- lid/opening: **4** (hinged hood, feed flap, sliding, split twin-leaf)
- filtration: **3** (HOB, internal, canister)
- aquascape multiplicity: **3** N-samples (2, 4, 7)
- support/base: **1** candidate (integrated rim/base only; a tall cabinet stand is a furniture neighbor → blocked, see below)

## Six-Axis Diversity Audit
| axis | candidate-anchor status | treatment | values / range |
|---|---|---|---|
| ① skeleton / topology | candidate-anchor | source-backed | filtration subassembly: HOB(A) / internal(B) / canister+hose loop(fork). Hood-present vs rim-only top. |
| ② joint / mechanism | candidate-anchor | source-backed | hood revolute(A,B); feed-flap revolute(A,B); sliding lid prismatic(fork); split twin-leaf revolute×2(fork) |
| ③ primary form family | candidate-anchor | source-backed + fork | rect box(A), soft-rounded(B), bow-front(fork), cylinder(fork), hexagon(fork) |
| ④ surface decoration | not standalone | record_only / world_knowledge_extrapolation | hood brand logo/decal (001 "Jumbl Pet"), dark display graphic on control_panel, gravel texture, driftwood/rockwork, plant leaf shapes; extrapolatable: printed background film, tank-lip trim striping |
| ⑤ proportion / size / travel | not candidate-anchor | record_only (may ride as companion) | footprint ~0.52–0.56 × 0.32 m; glass height 0.285–0.36; hood open ~1.25 rad, flap ~1.35 rad; nano-cube vs long-tank proportions; slide travel ~0.12–0.20 m |
| ⑥ material / palette | not candidate-anchor | record_only (may ride as companion) | clear vs slightly-blue glass (0.32 alpha); black/satin plastic frame; gravel tan(A) vs blue(B); marble base(B); plant greens + magenta; LED warm(A) vs aqua(B) |

## Multiplicity / Copy Logic
- **count_param**: `n_plants` (rooted plant clusters) — B's `for i in enumerate([...])` loop.
- **copied_object**: one plant cluster = 1 stem `Cylinder` (`plant_stem_{i}`) + 2 leaf `Box`es (`plant_leaf_{i}_0`, `plant_leaf_{i}_1`).
- **N samples**: 2 (rec_aquarium_var_plants_n2), 4 (origin B), 7 (rec_aquarium_var_plants_n7).
- **suggested N_range**: [1, 10].
- **naming**: stable indexed `plant_stem_{i}` / `plant_leaf_{i}_{j}`.
- **placement**: irregular positions on `gravel_bed`, base embedded in substrate; distributed to avoid rocks/filter, kept within `water_volume` footprint.
- **joint policy**: FIXED (static rooted decoration; no articulation). Multiplicity fork changes plant count ONLY.
- Secondary multiplicities (record_only, not forked): 4 corner_posts (A), 3 status_buttons (A), 4 gravel_ridges (A), hexagon 6-panel loop (rides on the ③ hexagon fork, not a standalone N sweep).

## Budget Decision
Normal band (12–18); chose **16** candidate anchors, coverage-first. Body_form and lid slots carry the richest honest structural vocabulary for this class; filtration gives a clean ① axis; plants give the multiplicity axis. No ④/⑤/⑥-only or scale-only variants used to hit the count. Not underfilled.

## Blocked / Excluded
- **Aquarium cabinet/stand (tall furniture base)** — blocked: drifts into furniture (Aquarium_stand) neighbor; support slot kept to integrated rim/base trim only.
- **Open-top rimless tank (no lid)** — excluded as a standalone fork: removing the hood strips all non-fixed joints (would be static_only) and weakens lid-mechanism coverage already carried by 4 candidates; recorded as a ⑤ proportion/record note only.
- **Fish bowl / spherical bowl** — out of subcategory (must_not_become).
- **Nano cube tank** — treated as ⑤ proportion variation (record_only), not a distinct ③ form family.
- **Heater / airstone equipment** — record_only; filtration slot already has 3 distinct candidates, no padding.

## Variant Cards (one per fork)
```yaml
- variant_id: rec_aquarium_var_bowfront
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  positioning: {product_archetype: bow-front panoramic display tank, why_same_subcategory: still a framed transparent water basin with hood/filter/aquascape}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: convex curved front glass}
  structural_delta:
    change: [replace flat front_glass with CadQuery convex bowed front panel, blend front rails/posts to curved footprint]
    keep_parts: [tank_frame, rear_glass, side_glass_*, bottom_glass, hood, feed_flap, tank_to_hood, hood_to_feed_flap]
    joint_policy: preserve (no joint change)
    interface_policy: curved front edge mates to base/top front rails
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [front glass tint], forbidden: [hood mechanism, filter type, plant count]}
  acceptance_focus: [glass reads hollow, hood still opens upward, no floating panel]

- variant_id: rec_aquarium_var_cylinder
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: cylindrical column shell}
  structural_delta:
    change: [replace 4 flat panes with hollow cylindrical glass wall, round bottom/base ring/top ring, round hood disc lid]
    keep_parts: [bottom_glass, filter, hood, feed_flap, tank_to_hood, hood_to_feed_flap]
    joint_policy: preserve
    interface_policy: circular rim carries round lid on existing rear revolute
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [glass tint], forbidden: [hood mechanism, filter type, plant count]}
  acceptance_focus: [not a fish bowl (keeps lid/frame/filter), hood opens]

- variant_id: rec_aquarium_var_hexagon
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: six-panel hexagonal prism}
  structural_delta:
    change: [6 glass side panels via shared helper loop (wall_glass_0..5, corner_post_0..5), hex bottom/rings/gravel, hex hood lid]
    keep_parts: [bottom_glass, filter, hood, feed_flap, tank_to_hood, hood_to_feed_flap]
    joint_policy: preserve
    interface_policy: hex rim carries hex lid on existing rear revolute
  multiplicity: {applies: true, target_n: 6, copied_object: side panel/corner post, placement_rule: radial hexagon}
  companion_variations: {allowed_④⑤⑥: [glass tint], forbidden: [hood mechanism, filter type, plant count]}
  acceptance_focus: [6 panels loop-emitted, hollow, hood opens]

- variant_id: rec_aquarium_var_lid_sliding
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  primary_axis: {slot: lid/opening, diversity_axis: ②, target_candidate: prismatic sliding cover}
  structural_delta:
    change: [replace tank_to_hood REVOLUTE with PRISMATIC horizontal slide, flat sliding panel on top rails, drop rear knuckles + feed_flap]
    keep_parts: [tank_frame, top_*_rail, light_diffuser, control_panel, filter, substrate]
    joint_policy: replace exactly one primary mechanism (revolute -> prismatic)
    interface_policy: lid slides on top rim rails as guides, travel ~0.12-0.20 m
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [lid tint], forbidden: [tank body form, filter type, plant count]}
  acceptance_focus: [one non-fixed prismatic joint, real slide travel, no floating lid]

- variant_id: rec_aquarium_var_lid_bifold
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  primary_axis: {slot: lid/opening, diversity_axis: ②, target_candidate: split twin-leaf canopy}
  structural_delta:
    change: [two lid-leaf parts each on own rear revolute, half-opening each, drop single hood + feed_flap]
    keep_parts: [tank_frame, top_*_rail, rear_hinge_knuckle_*, filter, substrate]
    joint_policy: replace single revolute with two independent revolute leaves
    interface_policy: two rear hinge lines at top rim
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [leaf tint], forbidden: [tank body form, filter type, plant count]}
  acceptance_focus: [both leaves open upward independently, cover full top when closed]

- variant_id: rec_aquarium_var_filter_canister
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__001...
  primary_axis: {slot: filtration, diversity_axis: ①, target_candidate: external canister + over-rim hoses}
  structural_delta:
    change: [remove rim-hung filter_housing/rim_hanger, add floor-standing sealed canister + lid ports + intake lift-tube + spray-bar return + 2 swept over-rim hoses]
    keep_parts: [tank_frame, substrate, gravel_bed, hood, feed_flap, tank_to_hood, hood_to_feed_flap]
    joint_policy: preserve hood/flap; canister fixed to tank via hoses/rim clip
    interface_policy: hoses arch over top rim, in-tank strainer + return anchored to rim
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [canister body palette], forbidden: [tank body form, hood mechanism, plant count]}
  acceptance_focus: [canister + hoses not floating, hood still opens]

- variant_id: rec_aquarium_var_plants_n2
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__002...
  primary_axis: {slot: aquascape multiplicity, diversity_axis: N, target_candidate: 2 rooted plants}
  structural_delta:
    change: [reduce plant loop 4 -> 2, same helper geometry, stable indexed names]
    keep_parts: [tank, water_volume, gravel_bed, filter_housing, front_rock, center_rock, hood, feeding_flap, tank_to_hood, hood_to_flap]
    joint_policy: preserve (plants FIXED)
    interface_policy: plant bases embedded in gravel_bed
  multiplicity: {applies: true, target_n: 2, copied_object: plant cluster (stem + 2 leaves), placement_rule: irregular on gravel bed}
  companion_variations: {allowed_④⑤⑥: [plant palette], forbidden: [tank body form, hood mechanism, filter type]}
  acceptance_focus: [not an empty box, plants rooted, count == 2]

- variant_id: rec_aquarium_var_plants_n7
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__aquarium__002...
  primary_axis: {slot: aquascape multiplicity, diversity_axis: N, target_candidate: 7 rooted plants}
  structural_delta:
    change: [increase plant loop 4 -> 7, same helper geometry, stable indexed names, non-colliding spread]
    keep_parts: [tank, water_volume, gravel_bed, filter_housing, front_rock, center_rock, hood, feeding_flap, tank_to_hood, hood_to_flap]
    joint_policy: preserve (plants FIXED)
    interface_policy: plant bases embedded in gravel_bed, kept within water_volume footprint
  multiplicity: {applies: true, target_n: 7, copied_object: plant cluster (stem + 2 leaves), placement_rule: irregular non-overlapping on gravel bed}
  companion_variations: {allowed_④⑤⑥: [plant palette], forbidden: [tank body form, hood mechanism, filter type]}
  acceptance_focus: [7 plants no collision with rocks/filter, none pierce hood, count == 7]
```
