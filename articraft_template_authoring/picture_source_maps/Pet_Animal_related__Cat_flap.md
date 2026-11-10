# Source Map — Pet_Animal related / Cat flap

slug `cat_flap` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__cat_flap__002_png_ce5bd540abfd475c80de66a1475b90ac` — picture/Pet_Animal related/Cat flap/002.png
- `rec_pet_animal_related__cat_flap__001_png_bc9eca847b4f4feba5eab6c1d837b845` — picture/Pet_Animal related/Cat flap/001.png

## Variants generated this batch (5 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_cat_flap_var_form_round` | form_round | PASS | 1 | 1 |
| `rec_cat_flap_var_mechanism_slider` | mechanism_slider | PASS | 2 | 1 |
| `rec_cat_flap_var_n2_dualflap` | n2_dualflap | PASS | 2 | 0 |
| `rec_cat_flap_var_skeleton_microchip` | skeleton_microchip | PASS | 2 | 1 |
| `rec_cat_flap_var_skeleton_tunnel` | skeleton_tunnel | PASS | 1 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Pet_Animal related / Cat flap (`cat_flap`)

pattern: **mixed** (single `panel_frame` host root carrying one top-hinge revolute `flap`; add-on modules = tunnel liner / sliding lock / electronic housing; flap-count multiplicity)
richness band: **simple** (8–12 candidate anchors) — cat flap is a low-vocabulary object.
parents (both origins, fully accounted):
- P002 `rec_pet_animal_related__cat_flap__002_png_ce5bd540abfd475c80de66a1475b90ac` — pic `picture/Pet_Animal related/Cat flap/002.png` — white flap in a glass patio door; rounded-rect trim, short tunnel sleeve (tunnel_side/top/sill), 6 screws, smoky swing flap, magnet catch. cadquery `_rounded_ring`/`_rounded_panel` helpers.
- P001 `rec_pet_animal_related__cat_flap__001_png_bc9eca847b4f4feba5eab6c1d837b845` — pic `picture/Pet_Animal related/Cat flap/001.png` — flap in a wooden door; `BezelGeometry` rounded-rect front_trim + inner_seal, 4 screws, frosted swing flap, magnet catch.

Both origins demonstrate the SAME structural configuration: door-mount thin panel, rounded-rect opening, single rigid **top-hinge swing flap (revolute `frame_to_flap`)**, manual bottom **magnet latch**. They differ only in host (glass vs wood), trim helper, screw count (④/⑤/⑥ + host), not in structure.

---

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Cat flap
  core_identity: A framed pet-sized opening mounted in a host panel/door/wall, closed by a movable flap the animal pushes through.
  must_keep:
    - a real through-opening sized for a cat, framed by a trim/bezel
    - at least one movable closure (swing flap on a top hinge) with a real non-fixed joint
    - mounting context (door panel, wall, or tunnel) that carries the frame
  must_not_become:
    - window / porthole / vent / air duct (no pet passage)
    - mail slot / letterbox
    - cabinet door / plain hinged panel with no framed pet opening
    - doorbell / intercom / security camera / smart-lock panel
  image_evidence:
    - rectangular white/dark bezel with rounded corners set into a door or glass (002, 001)
    - single translucent flap hanging in the opening, hinged at the top, swinging out as the cat passes (both)
    - screw heads at the trim corners; magnet catch at the flap bottom
    - 001 shows a wooden-door mount; 002 shows a glass-door mount with a short tunnel/sleeve
  parent_evidence:
    - parts: panel_frame (host + trim + seal + screws + hinge hardware + frame magnet), flap (panel + hinge barrel/sleeve + magnet keeper + lips/seals)
    - joint: frame_to_flap REVOLUTE about top X axis, limits ~±1.05 (002) / (-0.85,0.60) (001)
    - helpers: _rounded_ring/_rounded_panel (002), BezelGeometry + _flap_origin (001)
    - 002 already has a short tunnel: tunnel_side_0/1, tunnel_top, tunnel_sill
    - screw multiplicity loop: 6 (002) / 4 (001)
```

---

## Slot / Candidate Grid
Each supported slot reaches ≥2 structurally distinct candidates.

| slot | candidate | axis | source_type | evidence / record | key parts/joints | status |
|---|---|---|---|---|---|---|
| A host_mount / body_form | door_mount_thin_panel | ① | origin_anchor | P001, P002 | panel_frame, door_panel, front_trim | converged |
| A host_mount / body_form | wall_tunnel_liner | ① | forked_anchor | rec_cat_flap_var_skeleton_tunnel (from P002) | extend tunnel_* + add rear_frame | planned |
| B opening_form | rounded_rectangular | ③ | origin_anchor | P001, P002 | front_trim (rounded_rect) | converged |
| B opening_form | circular_disc | ③ | forked_anchor | rec_cat_flap_var_form_round (from P001) | round bezel + round flap disc | planned |
| C closure_mechanism | swing_flap_revolute | ② | origin_anchor | P001, P002 | flap, frame_to_flap (revolute) | converged |
| C closure_mechanism | sliding_4way_lock (added prismatic) | ② | forked_anchor | rec_cat_flap_var_mechanism_slider (from P001) | lock_slider, guide_rail_i, frame_to_lock_slider (prismatic) | planned |
| D flap_multiplicity | single_flap | N | origin_anchor | P001, P002 | flap ×1 | converged |
| D flap_multiplicity | double_flap (N=2 in series) | N | forked_anchor | rec_cat_flap_var_n2_dualflap (from P002) | flap + rear flap, frame_to_flap + frame_to_rear_flap | planned |
| E control_module | manual_magnet_latch | ① | origin_anchor | P001, P002 | bottom_magnet / frame_magnet + keeper | converged |
| E control_module | electronic_microchip_housing | ① | forked_anchor | rec_cat_flap_var_skeleton_microchip (from P001) | sensor_housing, battery_cover, antenna_ring, mode_button | planned |
| F fastener_multiplicity | screws N=4 / N=6 | N | origin_anchor | P001 (4), P002 (6) | screw_head_i / screw_i loop | converged (no fork) |

---

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton/topology | source-backed (origin + 3 forks) | door_mount panel (origin) / wall_tunnel liner + rear frame (fork) / electronic housing module (fork); flap-count topology via double-flap (fork) |
| ② joint/mechanism | source-backed (origin + 1 fork) | top-hinge REVOLUTE swing flap (origin, both) + added PRISMATIC 4-way lock slider (fork); microchip mode_button optional small control |
| ③ primary form family | source-backed (origin + 1 fork) | rounded-rectangular opening/flap (origin) vs circular disc opening/flap (fork) |
| ④ surface decoration | record_only / companion | screw heads + slots, gasket/seal strips, magnet strips, brand/LED decals (microchip); host texture (wood grain / glass); host-conformal only |
| ⑤ proportion / size / travel | record_only | opening ~0.23×0.30 (rect) / Ø~0.26 (round); flap swing limits ~-1.05..+1.05 (002) / -0.85..+0.60 (001); slider travel ~0.30; tunnel depth ~0.15–0.30 |
| ⑥ material / palette / finish | record_only | warm-white / charcoal / brushed-metal trim; frosted / smoky translucent flap; black rubber seal; masonry-grey liner (tunnel); no standalone variant |

---

## Multiplicity / Copy Logic
- **flap count (Slot D, structural):** count_param `n_flaps`; source-backed N samples {1 (P001,P002), 2 (fork rec_cat_flap_var_n2_dualflap)}; suggested N_range [1,2]; copied object = flap panel + hinge barrel + magnet keeper; placement = in series along tunnel depth (+Y); naming `flap` / `rear_flap` (indexed); joint policy = each flap keeps its own top-edge revolute hinge + magnet. Built with a shared flap-builder helper.
- **fasteners (Slot F, cosmetic multiplicity, no fork):** count_param `n_screws`; N samples {4 (P001), 6 (P002)} both origin-shown; N_range [4,8]; copied object = screw head + slot; placement = trim corners/edges (loop-emitted); joint policy = FIXED decorative. No fork emitted — both N already source-backed and screws are ④-class fasteners.
- **lock rails (probe-free):** guide_rail_0/1 loop-emitted in the slider fork, FIXED; not a standalone N axis.

---

## Budget Decision
- Candidate anchors (origins + converged forks; probes/baselines/④⑤⑥ not counted):
  - origin-backed: door_mount, rounded_rect, swing_flap_revolute, single_flap, manual_magnet, screws_N4, screws_N6 = **7**
  - fork-backed: wall_tunnel_liner (①), circular_disc (③), sliding_4way_lock (②), double_flap N=2 (N), electronic_microchip_housing (①) = **5**
  - **total ≈ 12 candidate anchors** → top of the **simple** band. Coverage-first, no padding.
- Fork jobs emitted: **5** (one per new candidate not already shown by an origin).
- underfilled_reason: none — every real functional slot reaches ≥2 structurally distinct source-backed candidates; further growth (e.g. roll-up closure, sliding-glass-track insert, N≥3 louvered flaps) would drift toward window/vent neighbors, so intentionally stopped at the simple-band top.

---

## Variant Cards

```yaml
variant_card:
  variant_id: rec_cat_flap_var_skeleton_tunnel
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__cat_flap__002_png_ce5bd540abfd475c80de66a1475b90ac
  positioning: {product_archetype: wall-mount cat flap with through-wall tunnel/liner, why_same_subcategory: same pet opening + top-hinge swing flap; only through-wall depth structure added}
  primary_axis: {slot: host_mount/body_form, diversity_axis: ①, target_candidate: wall_tunnel_liner}
  structural_delta:
    change: [extend short tunnel_* sleeve into full 4-wall tunnel depth ~0.15-0.30, add rear_frame flange bonded to tunnel far end]
    keep_parts: [panel_frame, front_trim, flap, flap_panel, moving_hinge_barrel, frame_to_flap, bottom_magnet]
    joint_policy: preserve the single revolute frame_to_flap; tunnel walls + rear_frame FIXED
    interface_policy: tunnel walls loop-emitted, indexed, rigidly joining front_trim to rear_frame
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [masonry-grey/white liner palette], forbidden: [vent/duct/mail-slot drift, electronics, circular opening, second flap, sliding lock]}
  acceptance_focus: [flap still swings freely inside tunnel, rear_frame not floating, single non-fixed joint remains]

variant_card:
  variant_id: rec_cat_flap_var_form_round
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__cat_flap__001_png_bc9eca847b4f4feba5eab6c1d837b845
  positioning: {product_archetype: round porthole cat door insert, why_same_subcategory: framed pet opening closed by a top-hinged swing flap; only opening/flap form family becomes circular}
  primary_axis: {slot: opening_form, diversity_axis: ③, target_candidate: circular_disc}
  structural_delta:
    change: [front_trim + door_panel cutout + inner_seal to circular bore Ø~0.26, rectangular translucent_panel to round flap disc]
    keep_parts: [panel_frame, door_panel, front_trim, inner_seal, flap, hinge_sleeve, translucent_panel, flap_magnet, frame_magnet, hinge_pin, frame_to_flap]
    joint_policy: preserve single top-hinge revolute frame_to_flap
    interface_policy: hinge chord across top of the circle; disc flap carried by hinge_sleeve
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [flap tint / edge-ring material], forbidden: [porthole-window/vent drift, remove flap, electronics, second flap, sliding lock]}
  acceptance_focus: [round flap fits and clears round bore, magnet catch aligns at bottom, one non-fixed joint]

variant_card:
  variant_id: rec_cat_flap_var_mechanism_slider
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__cat_flap__001_png_bc9eca847b4f4feba5eab6c1d837b845
  positioning: {product_archetype: lockable cat flap with manual 4-way slide lock, why_same_subcategory: same opening + swing flap; adds a sliding lock closure real to manual pet doors}
  primary_axis: {slot: closure_mechanism, diversity_axis: ②, target_candidate: sliding_4way_lock}
  structural_delta:
    change: [add lock_slider rigid closure panel captured in guide_rail_0/1 on front_trim, prismatic frame_to_lock_slider travel ~0.30 across the opening]
    keep_parts: [panel_frame, front_trim, flap, translucent_panel, frame_to_flap, magnet_mount, screw_head_i]
    joint_policy: add exactly one new PRISMATIC joint (frame_to_lock_slider); keep revolute frame_to_flap unchanged
    interface_policy: slider rides in two side rails just outside the opening; retracted = flap free, extended = flap blocked
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: rails loop-emitted}
  companion_variations: {allowed_④⑤⑥: [slider color/finish], forbidden: [sliding-window/letterbox drift, replacing swing flap with slider, electronics, second flap, circular opening]}
  acceptance_focus: [prismatic slider translates in track without floating, flap still swings, two distinct non-fixed joints]

variant_card:
  variant_id: rec_cat_flap_var_n2_dualflap
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__cat_flap__002_png_ce5bd540abfd475c80de66a1475b90ac
  positioning: {product_archetype: insulated double-flap (twin-flap) draught-excluder cat flap, why_same_subcategory: same opening + top-hinge swing motion; only flap count changes}
  primary_axis: {slot: flap_multiplicity, diversity_axis: N, target_candidate: two_flaps_in_series}
  structural_delta:
    change: [keep front flap on frame_to_flap, add homogeneous rear_flap on new top-hinge revolute frame_to_rear_flap at inner tunnel face]
    keep_parts: [panel_frame, front_trim, tunnel_side_0, tunnel_side_1, tunnel_top, tunnel_sill, flap, flap_panel, moving_hinge_barrel, frame_to_flap, bottom_magnet]
    joint_policy: add one revolute per added flap; each flap independent top-hinge + magnet
    interface_policy: shared flap-builder helper, flaps copied along +Y (front, rear), stable indexed names
  multiplicity: {applies: true, target_n: 2, copied_object: flap panel + hinge barrel + keeper, placement_rule: chain/series along tunnel depth Y}
  companion_variations: {allowed_④⑤⑥: [flap tint], forbidden: [double-hung-window/louver drift, N>2 louver stack, electronics, sliding lock, circular opening]}
  acceptance_focus: [both flaps swing independently without collision, rear flap supported by tunnel/hinge, two non-fixed joints]

variant_card:
  variant_id: rec_cat_flap_var_skeleton_microchip
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__cat_flap__001_png_bc9eca847b4f4feba5eab6c1d837b845
  positioning: {product_archetype: microchip / RFID selective-entry electronic cat flap, why_same_subcategory: same opening + swing flap; adds the electronic control module skeleton real microchip flaps carry}
  primary_axis: {slot: control_module, diversity_axis: ①, target_candidate: electronic_microchip_housing}
  structural_delta:
    change: [add sensor_housing box across top of front_trim, battery_cover panel, antenna_ring boss around opening, one small mode_button control]
    keep_parts: [panel_frame, door_panel, front_trim, inner_seal, flap, translucent_panel, hinge_sleeve, flap_magnet, frame_magnet, hinge_pin, screw_head_i, frame_to_flap]
    joint_policy: keep revolute frame_to_flap; housing/cover/antenna FIXED; mode_button optional small revolute/push control
    interface_policy: module sits above/around opening, does not block flap path
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [housing color, LED/label decals], forbidden: [doorbell/intercom/camera/smart-lock drift, remove flap, sliding lock, second flap, circular opening]}
  acceptance_focus: [housing not floating and not blocking flap, flap still swings, real non-fixed joint remains]
```

---

## Blocked / Excluded
- roll-up / flexible-curtain closure: thin real-world support; drifts toward vent-curtain — excluded to stay in simple band.
- sliding-glass-patio-door tall track insert: host-panel change, not a cat-flap structural axis — record_only host context, not forked.
- N≥3 flap/louver stack: would read as a louver/vent, not a pet door — blocked (must_not_become).
- screw N-sweep fork: both N=4 and N=6 already origin-shown and screws are ④-class fasteners — recorded, no fork.
