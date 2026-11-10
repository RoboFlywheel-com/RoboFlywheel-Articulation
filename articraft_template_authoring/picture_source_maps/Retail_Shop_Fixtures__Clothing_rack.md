# Source Map — Retail_Shop Fixtures / Clothing rack

slug `clothing_rack` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_retail_shop_fixtures__clothing_rack__001_png_8164d3a19cd3438f918e0b2aa92357a1` — picture/Retail_Shop Fixtures/Clothing rack/001.png
- `rec_retail_shop_fixtures__clothing_rack__002_png_fd3af89368ea4e9e93d75f404754c26e` — picture/Retail_Shop Fixtures/Clothing rack/002.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_clothing_rack_var_feetbase` | feetbase | PASS | 8 | 1 |
| `rec_clothing_rack_var_fold` | fold | PASS | 12 | 1 |
| `rec_clothing_rack_var_n_hangers` | n_hangers | PASS | 16 | 1 |
| `rec_clothing_rack_var_railextend` | railextend | PASS | 13 | 1 |
| `rec_clothing_rack_var_round` | round | PASS | 15 | 1 |
| `rec_clothing_rack_var_skeleton_arch` | skeleton_arch | PASS | 12 | 1 |
| `rec_clothing_rack_var_topshelf` | topshelf | PASS | 12 | 1 |
| `rec_clothing_rack_var_twotier` | twotier | PASS | 19 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Retail_Shop Fixtures / Clothing rack

slug `clothing_rack` · pattern **mixed** (base_frame root → PRISMATIC telescoping upper_frame carrying a horizontal hanging rail with a loop of REVOLUTE-swinging hangers + 4 CONTINUOUS caster wheels; hanger/shelf-rod/caster multiplicity)

richness band: **normal (low end)** · candidate anchors (origins + forks): **10** · fork jobs emitted: **8**

## subcategory_contract
```yaml
subcategory_contract:
  category: Retail_Shop Fixtures
  subcategory: Clothing rack
  core_identity: a free-standing garment rack — one or more elevated horizontal hanging rails held up by uprights on a floor base, used to hang clothes on hangers
  must_keep:
    - at least one elevated horizontal hanging rail carried by uprights on a base
    - hangers/garment capacity along the rail (hangers hook over the rail)
    - a floor-standing support base (wheeled casters or footed)
    - at least one real non-fixed joint (telescoping height prismatic, hanger swing revolute, caster spin continuous, fold/extend joints)
  must_not_become:
    - coat/hat tree or valet stand (vertical pegs, no horizontal hanging span)
    - shelving unit / bookcase / wardrobe cabinet (solid shelves/panels dominate)
    - clothes-horse / accordion drying airer, drying-rack ladder
    - curtain rod / wall track, mannequin/display bust, umbrella stand, carousel turntable
  image_evidence:
    - 001 (A): brushed-gold rolling rack, DOUBLE parallel rails (tall telescoping rear top rail + front hanging rail), 2-tier lower shoe/storage shelf of round rods, bent-tube rounded base side hoops, side accessory hooks, adjustment collars/knobs, 4 casters, many wooden hangers on both rails
    - 002 (B): black powder-coated SINGLE-rail rolling rack, straight top hanging rail on two uprights, telescoping height clamp collars + spring buttons, rounded welded corner elbows, low rear brace, red-ball-cap accessory side hooks, no shelf, 4 casters, ~7 wooden hangers
  parent_evidence:
    - A: base_frame root; front_hanging_rail + telescoping top_rail (base_to_top_rail PRISMATIC); front_hanger_{0..5}/upper_hanger_{0..4} with *_swing REVOLUTE (±0.35); lower/upper shelf_rod_{j} loops (2 tiers × 5) + side rails; base_side_hoop bent tubes; adjust_collar/clamp_knob/side_hook; 4 caster_{i} CONTINUOUS wheels (WheelGeometry/TireGeometry meshes)
    - B: base_frame + upper_frame; top_hanging_rail on upper_post_{i}; height_slide PRISMATIC with lower_sleeve_{i}/sliding_bushing_{i}/clamp_collar_{i}; top_hanger_{0..6} with top_hanger_{idx}_swing REVOLUTE (±0.35); rounded_corner_{i} spheres; low_rear_brace; upright_side_hook/side_hook + red ball caps; 4 wheel_{i} wheel_spin_{i} CONTINUOUS
```

## Slots & Candidates
| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| rail_topology ①③ | single_straight_rail | ①③ | origin_anchor | B (top_hanging_rail) | converged |
| rail_topology ①③ | double_parallel_rail | ①③ | origin_anchor | A (front_hanging_rail + top_rail) | converged |
| rail_topology ①③ | arched_inverted_U_rail | ③ | forked_anchor | rec_clothing_rack_var_skeleton_arch (from B) | planned |
| rail_topology ① | two_tier_stacked_double_hang | ① | forked_anchor | rec_clothing_rack_var_twotier (from B) | planned |
| rail_topology ① | round_hoop_rounder_rail | ① | forked_anchor | rec_clothing_rack_var_round (from B) | planned |
| support_base ① | rolling_caster_base | ① | origin_anchor | A, B (4 casters) | converged |
| support_base ① | static_leveling_feet_base | ① | forked_anchor | rec_clothing_rack_var_feetbase (from B) | planned |
| internal_structure ① | lower_storage_shelf | ① | origin_anchor | A (2-tier shelf_rod loops) | converged |
| internal_structure ① | no_shelf | ① | origin_anchor | B | converged |
| internal_structure ① | overhead_top_storage_shelf | ① | forked_anchor | rec_clothing_rack_var_topshelf (from B) | planned |
| height/motion ② | telescoping_height_prismatic | ② | origin_anchor | A, B (prismatic + sleeves) | converged |
| height/motion ② | hanger_swing_revolute | ② | origin_anchor | A, B (*_swing) | converged |
| height/motion ② | caster_spin_continuous | ② | origin_anchor | A, B (wheel spin) | converged |
| height/motion ② | folding_scissor_frame | ② | forked_anchor | rec_clothing_rack_var_fold (from B) | planned |
| height/motion ② | horizontal_rail_extension_prismatic | ② | forked_anchor | rec_clothing_rack_var_railextend (from B) | planned |
| multiplicity N | hangers N=7 (and A's 6/5) | N | origin_anchor | B (top_hanger_{0..6}), A | converged |
| multiplicity N | hangers N=11 (dense) | N | forked_anchor | rec_clothing_rack_var_n_hangers (from B) | planned |

Supported slots each reach ≥2 structurally distinct candidates from the origins alone (rail_topology 2, support_base 1→+feet, internal_structure 2, mechanism 3, multiplicity 2). Forks add new ③ arched form, round/two-tier/top-shelf/feet ① topologies, fold/extend ② mechanisms, and a wider N sample.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed | single-rail (B), double-parallel-rail (A), footed vs caster base; forks add arched inverted-U, two-tier stacked, round hoop, overhead top shelf, and static leveling-feet base |
| ② joint / mechanism | source-backed | telescoping height PRISMATIC (A,B), hanger swing REVOLUTE (A,B), caster spin CONTINUOUS (A,B); forks add fold/scissor REVOLUTE and horizontal rail-extension PRISMATIC |
| ③ primary form family | source-backed (fork) | straight tubular frame (A,B) → single curved/arched tube envelope (fork arch); round hoop rail (fork round) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | rail end caps/finials, red plastic ball caps (B), adjustment collars + clamp knobs/screws, spring buttons, hanger stops, side accessory hooks; extrapolate host-conformal only, no dedicated variant |
| ⑤ proportion / size / travel | record_only | width ~1.5–1.65 m; height ~1.7–1.85 m; telescoping travel 0.14 (B) / 0.22 (A) m; hanger swing ±0.35 rad; caster continuous; rod/tube radii ~0.014–0.023 |
| ⑥ material / palette / finish | record_only | brushed gold brass (A), gloss-black powder-coated steel (B); extrapolate chrome, matte white, rose-gold; pale-wood/silver hangers, dark-rubber tires, red caps |

## Multiplicity / Copy Logic
- **hangers** — count_param on the `for idx, x in enumerate(...)` hanger loop → `_create_hanger`. N samples {5 (A upper), 6 (A front), 7 (B top)} origin-backed + {11 (fork n_hangers)}; N_range [3,14]; copied object = one hanger assembly (hook + vertical_neck + hanger_body), even x-spacing along the rail, one `*_swing` REVOLUTE (±0.35) per hanger, indexed `*_hanger_{idx}`.
- **shelf rods** — A: `lower/upper_shelf_rod_{j}` loops (2 tiers × 5 rods) + side rails; count_param on rod loop; FIXED slats; used in the top-shelf fork as `shelf_rod_{i}` even-spaced FIXED slats (shelf detail, not the primary N axis).
- **casters** — always 4, `wheel_{i}`/`wheel_spin_{i}` CONTINUOUS + fork/stem hardware, loop-emitted; fixed count (not an N-sweep; base-type change is a ① slot, not N).

## Budget Decision
Two content-rich origins already back the two rail topologies, both shelf states, the caster base, and all three core mechanisms (~7 anchors across the grid). Forks add only genuinely new structural vocabulary and no padding: 1 new ③ arched form, 3 new ① topologies (two-tier, round, overhead shelf) + 1 new ① base family (feet), 2 new ② mechanisms (fold, rail-extend), and 1 wider N sample. Total = 2 origins + 8 forks = **10 candidate anchors** (normal band, low end). Structural vocabulary for a clothing rack is genuinely moderate — coverage-first, no ④/⑤/⑥/scale/material/color standalone variants. No compatibility probes: each fork reuses existing mating faces (sleeve insertion, rail hook-over, caster mounts) on a single axis.

## Variant Cards
```yaml
- variant_id: rec_clothing_rack_var_skeleton_arch
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: arch/bow-top boutique rolling garment rack, why_same_subcategory: elevated horizontal hanging span with swinging hangers on a wheeled base}
  primary_axis: {slot: rail_topology, diversity_axis: ③, target_candidate: arched_inverted_U_rail}
  structural_delta:
    change: [replace straight top_hanging_rail + upright posts/tees with one continuous arched mesh tube (tube_from_spline_points) rising from each lower sleeve and curving over the crown]
    keep_parts: [base_frame, upper_frame, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, top_hanger_{idx}, top_hanger_{idx}_swing, wheel_{i}, wheel_spin_{i}]
    joint_policy: preserve all joints; only the rail/upright form family changes
    interface_policy: arch legs telescope into lower_sleeve_{i}; hangers hook over the level crown segment
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [chrome/matte-white finish], forbidden: [base change, shelf add, coat-tree/arch/trellis drift]}
  acceptance_focus: [arched crown rail present as curved tube, hangers still swing, telescoping + casters intact, still a clothing rack]

- variant_id: rec_clothing_rack_var_twotier
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: double-hang garment rack (two stacked rails), why_same_subcategory: two horizontal hanging rails, still a clothing rack}
  primary_axis: {slot: rail_topology, diversity_axis: ①, target_candidate: two_tier_stacked_double_hang}
  structural_delta:
    change: [add a lower_hanging_rail between the two upper_post_{i} at ~half height with its own looped hangers]
    keep_parts: [base_frame, upper_frame, upper_post_{i}, top_hanging_rail, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, top_hanger_{idx}, top_hanger_{idx}_swing, wheel_{i}, wheel_spin_{i}]
    joint_policy: add lower_hanger_{idx}_swing REVOLUTE loop (same ±0.35); preserve all others
    interface_policy: lower rail tied to posts; new hangers hook over it via _create_hanger
  multiplicity: {applies: true, target_n: null, copied_object: hanger assembly on new rail, placement_rule: even x-spacing}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [solid shelves/panels, base/mechanism change, shelving-unit drift]}
  acceptance_focus: [second lower rail + swinging hangers present, top rail unchanged, telescoping/casters intact]

- variant_id: rec_clothing_rack_var_topshelf
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: garment rack with overhead storage shelf, why_same_subcategory: hanging rail stays dominant with a shelf above}
  primary_axis: {slot: internal_structure, diversity_axis: ①, target_candidate: overhead_top_storage_shelf}
  structural_delta:
    change: [extend upper_post_{i} upward, add horizontal top_storage_shelf of looped shelf_rod_{i} slats on side rails above the hanging rail]
    keep_parts: [base_frame, upper_frame, upper_post_{i}, top_hanging_rail, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, top_hanger_{idx}, top_hanger_{idx}_swing, wheel_{i}, wheel_spin_{i}]
    joint_policy: shelf slats FIXED to upper_frame; preserve all joints
    interface_policy: shelf spans between extended posts; rail + hangers unchanged below
  multiplicity: {applies: true, target_n: null, copied_object: shelf_rod slat, placement_rule: even spacing (for-i loop)}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [solid cabinet panels, rail removal, base/mechanism change, shelving-unit drift]}
  acceptance_focus: [overhead slatted shelf present, hanging rail dominant, hangers swing, casters/telescoping intact]

- variant_id: rec_clothing_rack_var_feetbase
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: stationary (non-rolling) footed garment rack, why_same_subcategory: same hanging rail on uprights, only the base family changes}
  primary_axis: {slot: support_base, diversity_axis: ①, target_candidate: static_leveling_feet_base}
  structural_delta:
    change: [remove caster wheel_{i}/fork/stem hardware; add two foot_rail cross-tubes and four foot_{i} glides at corners]
    keep_parts: [base_frame, upper_frame, upper_post_{i}, top_hanging_rail, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, top_hanger_{idx}, top_hanger_{idx}_swing]
    joint_policy: casters removed; telescoping PRISMATIC + hanger REVOLUTE retained (real non-fixed joints remain)
    interface_policy: feet FIXED under base_frame corners; rack rests flat
  multiplicity: {applies: true, target_n: 4, copied_object: foot glide, placement_rule: one per corner (for-i loop)}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [re-add wheels, rail/topology change, valet-stand/coat-tree drift]}
  acceptance_focus: [no casters + footed base present, telescoping still works, hangers swing, same subcategory]

- variant_id: rec_clothing_rack_var_round
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: retail round rack / rounder with circular rail on central mast, why_same_subcategory: closed circular horizontal hanging rail at garment height on a wheeled base}
  primary_axis: {slot: rail_topology, diversity_axis: ①, target_candidate: round_hoop_rounder_rail}
  structural_delta:
    change: [replace straight rail + twin posts with a central mast + horizontal round_rail hoop (mesh circle) on radial spoke arms; hangers loop radially]
    keep_parts: [base_frame, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, wheel_{i}, wheel_spin_{i}, _create_hanger + *_swing REVOLUTE]
    joint_policy: hanger *_swing REVOLUTE per hanger; mast telescopes; casters continuous; NO added rotation joint
    interface_policy: mast telescopes into a central lower_sleeve on a spider base; hangers hook over the hoop
  multiplicity: {applies: true, target_n: null, copied_object: hanger assembly, placement_rule: radial even-angle around hoop}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [coat-tree/umbrella-stand/carousel drift, adding a turntable rotation joint, base change]}
  acceptance_focus: [circular hanging rail at garment height, radial swinging hangers, telescoping mast + casters intact]

- variant_id: rec_clothing_rack_var_fold
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: portable collapsible X-frame folding garment rack, why_same_subcategory: elevated hanging rail with hangers on a wheeled base that folds}
  primary_axis: {slot: height/motion, diversity_axis: ②, target_candidate: folding_scissor_frame}
  structural_delta:
    change: [rebuild each end support as crossing legs with a central pivot; add a fold_joint REVOLUTE so the frame scissors open/closed]
    keep_parts: [base_frame, upper_frame, top_hanging_rail, top_hanger_{idx}, top_hanger_{idx}_swing, wheel_{i}, wheel_spin_{i}]
    joint_policy: add fold_joint REVOLUTE (limits ~0..0.9); telescoping height may be dropped for the fold; hanger REVOLUTE + caster CONTINUOUS retained
    interface_policy: scissor legs pivot at a real crossing hub; rail rides the moving leg pair; casters under legs
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [folding-chair/clothes-horse/sawhorse drift, rail-topology change]}
  acceptance_focus: [fold_joint revolute folds the frame flat, hanging rail with hangers dominant, casters intact]

- variant_id: rec_clothing_rack_var_railextend
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: expandable/adjustable-width garment rack, why_same_subcategory: wheeled rack whose horizontal rail extends to hold more clothes}
  primary_axis: {slot: height/motion, diversity_axis: ②, target_candidate: horizontal_rail_extension_prismatic}
  structural_delta:
    change: [split top_hanging_rail into rail_outer sleeve + captured rail_inner tube; add rail_extend PRISMATIC along rail X]
    keep_parts: [base_frame, upper_frame, upper_post_{i}, top_hanging_rail, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, top_hanger_{idx}, top_hanger_{idx}_swing, wheel_{i}, wheel_spin_{i}]
    joint_policy: add rail_extend PRISMATIC (limits ~0..0.25); keep independent vertical height_slide PRISMATIC
    interface_policy: rail_inner stays captured inside rail_outer at both extremes; a subset of hangers hang from rail_inner
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [curtain-rod/wall-track drift, base or rail-count change]}
  acceptance_focus: [rail_inner slides out on rail_extend prismatic while captured, height_slide still works, hangers swing]

- variant_id: rec_clothing_rack_var_n_hangers
  source_type: forked_anchor
  parent_record_id: rec_retail_shop_fixtures__clothing_rack__002... (B)
  positioning: {product_archetype: fully-loaded packed retail rack, why_same_subcategory: identical rack, higher hanger density}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 11 hangers}
  structural_delta:
    change: [hanger loop count 7 -> 11 via same _create_hanger helper, even x-spacing]
    keep_parts: [base_frame, upper_frame, upper_post_{i}, top_hanging_rail, height_slide, lower_sleeve_{i}, sliding_bushing_{i}, wheel_{i}, wheel_spin_{i}]
    joint_policy: one top_hanger_{idx}_swing REVOLUTE (±0.35) per hanger; no other joint change
    interface_policy: hangers evenly spaced along top_hanging_rail, indexed top_hanger_0..10
  multiplicity: {applies: true, target_n: 11, copied_object: hanger assembly (hook + vertical_neck + hanger_body), placement_rule: even x-spacing}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [rail/base/telescoping/geometry change, second rail]}
  acceptance_focus: [11 hangers count test, each swings, rail/base/telescoping unchanged]
```

## Blocked / Excluded
- ②-only "spinner rotation" turntable — a rotating round rack combines ① round topology + ② rotation; kept as single-axis ① round (rounder) only, rotation excluded to avoid bundling axes and carousel/turntable drift.
- material/palette/finish variants (gold/black/chrome/white), scale-only and end-cap/finial decoration — recorded as ④/⑤/⑥ ranges only, never standalone anchors (no padding).
- caster N-sweep — caster count is fixed at 4 across both origins; base family change is captured as the ① feet-base slot, not an N axis.
```
