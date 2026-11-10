# Source Map — Pet_Animal related / Hamster wheel

slug `hamster_wheel` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__hamster_wheel__002_png_cd4d4b4b20814cf8b1aa9f9068edbd6b` — picture/Pet_Animal related/Hamster wheel/002.png
- `rec_pet_animal_related__hamster_wheel__001_png_0b33af11f7df4e8e9dd52cc774223f12` — picture/Pet_Animal related/Hamster wheel/001.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_hamster_wheel_var_body_mesh` | body_mesh | PASS | 1 | 2 |
| `rec_hamster_wheel_var_body_open_ring` | body_open_ring | PASS | 1 | 1 |
| `rec_hamster_wheel_var_mount_clamp` | mount_clamp | PASS | 1 | 0 |
| `rec_hamster_wheel_var_skeleton_saucer` | skeleton_saucer | PASS | 1 | 1 |
| `rec_hamster_wheel_var_spoke_n3` | spoke_n3 | PASS | 1 | 1 |
| `rec_hamster_wheel_var_spoke_n8` | spoke_n8 | PASS | 1 | 1 |
| `rec_hamster_wheel_var_tread_n16` | tread_n16 | PASS | 1 | 1 |
| `rec_hamster_wheel_var_tread_n48` | tread_n48 | PASS | 1 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Pet_Animal related / Hamster wheel (slug `hamster_wheel`)

pattern: **mixed** (single `stand` root → one revolute-spun `wheel` child; wheel carries
multiplicity families: running-surface rungs/treads, hub spokes, rim ribs, rear-panel vents).

## Origins (full reconciliation, 2/2 anchored)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_pet_animal_related__hamster_wheel__001_png_0b33af11f7df4e8e9dd52cc774223f12` | 001.png | transparent blue **solid drum** wheel: thin annular `drum_wall`, front/rear torus rims, closed `rear_disk`, `wheel_hub` sleeve, 5 fan `spoke_{i}`, 32 axial grip `tread_{i}`; on a **solid acrylic block stand** (rounded `base_plate` + 2 `support_post` + `bearing_crossbar` + `axle_shaft`); revolute Y `stand_to_wheel` | body=solid_drum / stand=acrylic_block / N: tread=32, spoke=5 |
| B `rec_pet_animal_related__hamster_wheel__002_png_cd4d4b4b20814cf8b1aa9f9068edbd6b` | 002.png | translucent green **solid drum** wheel with closed rear panel (5 pinwheel petal vents) + hub ring + 18 external `rim_rib_{i}`; on a **bent-wire metal stand** (`base_loop` spline + 2 `side_support` yokes + `axle_shaft`/`rear_bearing`); revolute X `stand_to_wheel` | body=solid_drum(vented) / stand=bent_wire / N: rim_rib=18, petal_vent=5 |

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Hamster wheel
  core_identity: a single continuous running wheel that spins freely on a fixed axle carried by a stand/mount
  must_keep:
    - one running wheel (drum / ring / disc) that a small animal runs on
    - a fixed axle carried by a stand or mount, wheel supported (not floating)
    - exactly one primary revolute/continuous spin joint (stand_to_wheel)
  must_not_become:
    - Ferris wheel / water wheel / paddle wheel (ride or fluid machine)
    - fan / turbine / gear / pulley / spinning top
    - bird cage / cage panel; plate / bowl / dish (kitchenware)
  image_evidence:
    - translucent plastic running drum with thick rounded rim
    - open front, closed vented rear panel with pinwheel/petal spokes
    - central hub cap on a fixed axle; low freestanding stand (acrylic block or bent wire)
  parent_evidence:
    - stand(part) + wheel(part), single revolute stand_to_wheel joint (axis Y in A, X in B)
    - loop-emitted multiplicity: tread_{i}(32), spoke_{i}(5) in A; rim_rib_{i}(18) + 5 petal vents in B
    - helpers annular_cylinder_y / add_y_cylinder / add_radial_cylinder (A); _make_wheel_body / tube_from_spline_points (B)
```

## Slots and Candidates
- **body_form (③ primary form family / macro surface construction)**
  - solid_drum shell — A, B (origin_anchor)
  - open_rung_ring (discrete running rails between two open rims, open sides) — fork `body_open_ring`
  - wire_mesh_band (crossing-wire grid running surface) — fork `body_mesh`
- **skeleton / running-axis topology (①)**
  - upright drum on horizontal axle — A, B (origin_anchor)
  - tilted flying-saucer disc on inclined axle — fork `skeleton_saucer`
- **support_or_base / mount (①)**
  - solid acrylic block stand (base plate + 2 posts + crossbar) — A (origin_anchor)
  - bent-wire metal floor stand (loop + 2 yokes) — B (origin_anchor)
  - cage-clamp cantilever bracket — fork `mount_clamp`
- **multiplicity — running-surface rungs (`tread_{i}`)**: A N=32; forks n16, n48
- **multiplicity — hub spokes / internal web (`spoke_{i}`)**: A N=5; forks n3, n8
- **internal_structure (rear web)**: solid vented petal panel (B, 5 vents) vs open spoke fan (A) — covered by origins; petal-vent count recorded, not forked (avoid padding)

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origins + forked_anchor) | upright drum on horizontal axle (A,B); tilted saucer disc on inclined axle (`skeleton_saucer`); support topology acrylic-block (A) / bent-wire (B) / cage-clamp cantilever (`mount_clamp`) |
| ② joint / mechanism | source-backed | single revolute spin `stand_to_wheel` (A axis Y, B axis X); saucer reorients axis along inclined axle (intrinsic to ① skeleton, not a separate mechanism). continuous-vs-revolute is trivial → not forked |
| ③ primary form family | source-backed (forked_anchor) | solid_drum shell (A,B); open_rung_ring lattice (`body_open_ring`); wire_mesh_band (`body_mesh`) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | rim grip ribs, molded rim striations, rear petal vents, printed brand ring; host-conformal only, no dedicated variant |
| ⑤ proportion / size / travel | record_only / companion | wheel Ø ~0.16–0.30 m (dwarf ~0.16, syrian ~0.28), drum width 0.06–0.11 m; spin range revolute ±π … ±2π or continuous |
| ⑥ material / palette / finish | record_only / companion | clear/blue translucent plastic (A), green translucent (B); pink/purple/amber plastics, white metal, steel-mesh finish |

## Multiplicity / Copy Logic
- **Running-surface rungs** — count_param `n_tread` (A helper `add_y_cylinder` in `for i in range(32)`); copied object = axial grip cylinder `tread_{i}` at drum inner radius, even angular spacing `2*pi*i/N`, FIXED to `wheel`; N samples {16, 32(A), 48}; suggested N_range [12, 56].
- **Hub spokes** — count_param `n_spoke` (A helper `add_radial_cylinder` in `for i in range(5)`); copied object = radial cylinder `spoke_{i}` hub→rim, even spacing `18 + i*(360/N)`, FIXED to `wheel`; N samples {3, 5(A), 8}; suggested N_range [3, 12].
- **Rim ribs** (B `rim_rib_{i}` N=18) and **rear petal vents** (B, 5 pinwheel slots) — record_only; already loop-emitted in B, not swept (single family suffices per copy-logic goal; no padding).

## Budget decision
Richness band: **simple** (8–12 candidate anchors). Object is structurally lean (one wheel + one stand
+ one spin joint); honest structural vocabulary = 2 body-form forks, 1 skeleton fork, 1 mount fork,
2 running-rung N samples, 2 spoke N samples. **Total candidate anchors = 10** (2 origins + 8 forks).
Coverage-first, no padding — every fork is a distinct source-backed ①/③/N candidate. No ④/⑤/⑥-only
variants. No probes (all cross-slot combos are low interface risk).

## Variant Cards (one per fork)
```yaml
- variant_id: rec_hamster_wheel_var_body_open_ring
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: open_rung_ring}
  structural_delta: {change: [remove solid drum_wall; add N running rails rung_{i} between front_rim/rear_rim; open sides], keep_parts: [stand, front_rim, rear_rim, wheel_hub, spoke_{i}, axle_shaft, stand_to_wheel], joint_policy: preserve revolute Y, interface_policy: rungs FIXED at wheel radius, hub-on-axle coaxial}
  multiplicity: {applies: false, note: default ~20 rungs, not the sweep}

- variant_id: rec_hamster_wheel_var_body_mesh
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: wire_mesh_band}
  structural_delta: {change: [replace drum_wall with axial mesh_bar_{i} x circumferential mesh_hoop_{j} grid], keep_parts: [stand, front_rim, rear_rim, wheel_hub, spoke_{i}, stand_to_wheel], joint_policy: preserve revolute Y, interface_policy: mesh FIXED to wheel, rims as edge frame}
  multiplicity: {applies: false, note: mesh cell density record_only}

- variant_id: rec_hamster_wheel_var_skeleton_saucer
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: skeleton, diversity_axis: ①, target_candidate: tilted_flying_saucer_disc}
  structural_delta: {change: [replace upright running_drum with shallow angled saucer disc; incline axle ~30-40deg], keep_parts: [stand, base_loop, side_support_{idx}, axle_shaft, rear_bearing, stand_to_wheel], joint_policy: preserve revolute, reorient axis along inclined axle, interface_policy: hub bore coaxial on inclined axle}
  multiplicity: {applies: false}

- variant_id: rec_hamster_wheel_var_mount_clamp
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: cage_clamp_cantilever}
  structural_delta: {change: [remove base_loop + side_support yokes; add clamp_plate + clamp jaws + cantilever mount_arm carrying axle_shaft/rear_bearing], keep_parts: [wheel, running_drum, rim_rib_{i}, axle_shaft, front_axle_cap, rear_bearing, stand_to_wheel], joint_policy: preserve revolute X, interface_policy: single cantilever axle through hub, wheel fully supported}
  multiplicity: {applies: false}

- variant_id: rec_hamster_wheel_var_tread_n16
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_tread=16}
  multiplicity: {applies: true, target_n: 16, copied_object: tread_{i}, placement_rule: radial even angular spacing, joint_policy: FIXED to wheel}

- variant_id: rec_hamster_wheel_var_tread_n48
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_tread=48}
  multiplicity: {applies: true, target_n: 48, copied_object: tread_{i}, placement_rule: radial even angular spacing, joint_policy: FIXED to wheel}

- variant_id: rec_hamster_wheel_var_spoke_n3
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_spoke=3}
  multiplicity: {applies: true, target_n: 3, copied_object: spoke_{i}, placement_rule: radial even angular spacing, joint_policy: FIXED to wheel}

- variant_id: rec_hamster_wheel_var_spoke_n8
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_spoke=8}
  multiplicity: {applies: true, target_n: 8, copied_object: spoke_{i}, placement_rule: radial even angular spacing, joint_policy: FIXED to wheel}
```

## Blocked / Excluded
- continuous-vs-revolute joint swap — trivial ②, not forked (both origins already spin freely).
- rim-rib N-sweep and rear petal-vent N-sweep (B) — record_only; single running-rung + spoke families
  already expose copy logic; sweeping more would be padding.
- fully-enclosed ball / exercise sphere — different subcategory (rolling ball, no stand), blocked.
```
