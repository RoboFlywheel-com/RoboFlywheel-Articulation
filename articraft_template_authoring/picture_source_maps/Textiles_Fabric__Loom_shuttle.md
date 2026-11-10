# Source Map — Textiles_Fabric / Loom shuttle

slug `loom_shuttle` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019` — picture/Textiles_Fabric/Loom shuttle/002.png
- `rec_textiles_fabric__loom_shuttle__001_png_79eba550708c492a92fffab2ac4d9bd4` — picture/Textiles_Fabric/Loom shuttle/001.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_loom_shuttle_var_form_ski` | form_ski | PASS | 1 | 0 |
| `rec_loom_shuttle_var_mechanism_end_delivery` | mechanism_end_delivery | PASS | 1 | 1 |
| `rec_loom_shuttle_var_mechanism_roller` | mechanism_roller | PASS | 3 | 0 |
| `rec_loom_shuttle_var_mechanism_spindle_arm` | mechanism_spindle_arm | PASS | 2 | 1 |
| `rec_loom_shuttle_var_n_rollers4` | n_rollers4 | PASS | 5 | 0 |
| `rec_loom_shuttle_var_skeleton_flat_open` | skeleton_flat_open | PASS | 1 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Textiles_Fabric / Loom shuttle — variant plan

slug `loom_shuttle` · pattern **linear_chain (body → single revolute bobbin)**, with an optional
**multiplicity** bogie (underside rollers) introduced by a fork. Richness band: **simple** (low end).

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Loom shuttle
  core_identity: >
    A handheld weaving shuttle that carries the weft: an elongated wooden shuttle body with
    pointed/tapered ends and a weft package (bobbin/pirn) held in/on the body so thread pays off
    as the shuttle passes through the shed.
  must_keep:
    - elongated shuttle body with tapered/pointed ends (length >> width, low height)
    - a weft package (bobbin/pirn/wound yarn) carried by the body
    - at least one real articulation carrying/spinning the weft package (revolute bobbin) unless a
      genuinely static figure-8 stick type is explicitly modeled
  must_not_become:
    - netting shuttle / tatting shuttle (net- and lace-making, not weaving)
    - spinning-wheel bobbin or bare sewing-machine bobbin (weft package alone, no shuttle body)
    - canoe / boat / ski / sled / letter-opener (pointed-wood visual neighbors)
  image_evidence:
    - 001.png: two boat shuttles, pointed wooden hulls, open top cavity, a pale bobbin on a spindle
      spanning the cavity, cream weft wound on it, exposed and free to spin; loose thread tail.
    - 002.png: Pilkington's boat shuttle, carved deep bay, cotton pirn on an axle between metal
      bearing eyelets, metal cone nose tips, brand stamp, small drilled holes, red thread end.
  parent_evidence:
    - both parents: part `body` (carved boat hull + `cavity_floor`) + part `bobbin`, one
      `body_to_bobbin` REVOLUTE about long X axis; bobbin = `bobbin_core`/axle + wound
      `cotton_thread`/`thread_core` + two flanges; end bearings support the axle; metal nose tips.
    - both origins are the SAME skeleton+mechanism (boat hull + through-axle revolute bobbin);
      they differ only in ④/⑤/⑥ (wood tone, size, tips, decoration), not in structure.
```

## Slots and candidates
| slot | candidate | axis | source_type | evidence / record |
|---|---|---|---|---|
| body_form | boat hollow bay (deep enclosed cavity, pointed) | ③ | origin_anchor | 001, 002 |
| body_form | flat plank, full-length open slot, notched ends | ①/③ | forked_anchor | rec_loom_shuttle_var_skeleton_flat_open |
| body_form | ski / upswept-tip, shallow open channel | ③ | forked_anchor | rec_loom_shuttle_var_form_ski |
| bobbin_mechanism | through-axle revolute spool on two fixed bearings | ② | origin_anchor | 001, 002 |
| bobbin_mechanism | hinged pivoting spindle arm (load/latch) + pirn spin | ② | forked_anchor | rec_loom_shuttle_var_mechanism_spindle_arm |
| bobbin_mechanism | end-delivery pirn on fixed cantilever spindle + tension gate | ② | forked_anchor | rec_loom_shuttle_var_mechanism_end_delivery |
| glide/underside | none — slides directly on race | — | origin_anchor (baseline) | 001, 002 |
| glide/underside | underside roller bogie (continuous rollers) | ② + N | forked_anchor | rec_loom_shuttle_var_mechanism_roller |
| multiplicity (rollers) | N=2 / N=4 rollers | N | forked_anchor | roller (N2) / rec_loom_shuttle_var_n_rollers4 |

Each supported structural slot reaches ≥2 distinct candidates. `handle_or_grip`,
`support_or_base` and `surface_construction` are not real functional slots for this class (a shuttle
is grip-free, base-free solid wood), so they are intentionally not expanded.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forks) | boat hollow bay (origin); flat plank + open slot (fork); ski open channel (fork); +roller bogie subtree (fork) |
| ② joint / mechanism | source-backed (origin + forks) | through-axle revolute bobbin (origin); hinged spindle arm + pirn spin (fork); end-delivery cantilever pirn spin (fork); underside continuous rollers (fork) |
| ③ primary form family | source-backed (origin + forks) | pointed enclosed boat trough (origin); flat rectangular plank (fork); slender upswept ski (fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | brand stamp (Pilkington's), drilled top holes, side eyelets, wood-grain streaks, wear lines, red thread end — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only | length ~0.30–0.42, width ~0.045–0.075, height <0.055, L/W >4; cavity depth; bobbin revolute ±π; may ride as companion on structural forks |
| ⑥ material / palette / finish | record_only | honey / oiled-brown / pale worn wood; cream/aged-cotton weft; red thread tail; steel/brass tips, bearings, spindle, rollers — companion only |

## Multiplicity / Copy Logic
- **count_param:** `n_rollers` on the underside roller bogie (only repeated homogeneous part in this
  class; the shuttle body + single bobbin/pirn are inherently singular — no drawers/spokes/keys).
- **N samples (source-backed via fork):** 2 (rec_loom_shuttle_var_mechanism_roller), 4
  (rec_loom_shuttle_var_n_rollers4).
- **suggested N_range:** [2, 6].
- **copied object:** `roller_{i}` + `roller_axle_{i}`, loop-emitted via a shared helper.
- **naming:** stable indexed `roller_{i}`.
- **placement:** equal spacing along the keel centerline (X), crown just proud of the keel.
- **joint policy:** each roller its own `roller_{i}_spin` continuous joint about transverse Y.
- Multiplicity is otherwise weak for this subcategory; only the (world-knowledge→forked) roller
  bogie exposes copy logic. Decorative repeats (thread bands, drilled holes) are ④, not multiplicity.

## Budget decision
- Candidate anchors (origins + forks, ④/⑤/⑥ and baselines not counted): **7**
  - boat_hollow+revolute_bobbin (origin, both parents) ×1 structural cell
  - flat_plank_open (fork)
  - ski_upswept (fork)
  - spindle_arm mechanism (fork)
  - end_delivery mechanism (fork)
  - roller bogie N=2 (fork)
  - roller bogie N=4 (fork)
- Band **simple (8–12), targeting the LOW end**; landed at 7.
- `underfilled_reason`: a loom shuttle is structurally minimal — one solid elongated body carrying one
  weft package. Honest structural vocabulary is body-form (3), bobbin-mounting mechanism (3), and an
  optional roller bogie with 2 N-samples. There is no genuine second body-subassembly, no handle, no
  base, and no other repeated-part family. Rather than pad with ④/⑤/⑥/scale/material variants, the
  pool stops at 7 source-backed anchors.

## Blocked / Excluded
- **netting shuttle / tatting shuttle** — net/lace tool with a central tongue, not a weaving weft
  carrier; out of subcategory. `blocked`.
- **double-bobbin / two-shuttle body** — not a real single loom shuttle; would drift toward a loom
  assembly. `blocked`.
- **leaf-spring top-loaded pirn holder** — real but structurally near-duplicate of the end-delivery
  mechanism; excluded to avoid ②-axis over-splitting/padding.
- **static figure-8 stick shuttle (no moving part)** — legitimate type but `static_only`; excluded in
  favor of the flat-plank-open variant which keeps a real revolute bobbin (avoids a jointless anchor).
- **roller N=6** — excluded; N{2,4} already exposes the copy logic.

## Variant cards
```yaml
- variant_id: rec_loom_shuttle_var_skeleton_flat_open
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: flat rigid-heddle stick/boat shuttle with open slot, why_same_subcategory: still an elongated shuttle body carrying a spinning weft bobbin}
  primary_axis: {slot: body_form, diversity_axis: ①, target_candidate: flat plank + full-length open slot}
  structural_delta:
    change: [replace carved boat hull + deep slot cavity with thin flat rectangular plank + shallow open slot + notched ends, raise bearings so bobbin is exposed]
    keep_parts: [body, bobbin, body_to_bobbin, bobbin_core, cotton_thread, front_flange, rear_flange, front_bearing, rear_bearing]
    joint_policy: preserve the single body_to_bobbin revolute
    interface_policy: bearing saddles at plank top surface support the axle in an open channel
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [pale plank finish, longer/thinner proportion], forbidden: [rollers, hinged spindle, category drift to ruler/stick]}
  acceptance_focus: [flat low-profile body, exposed spinning bobbin retained in slot, single revolute joint]

- variant_id: rec_loom_shuttle_var_form_ski
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: slender ski-tip floor-loom shuttle, why_same_subcategory: elongated weft-carrying shuttle with a rotating bobbin}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: upswept ski + shallow open channel}
  structural_delta:
    change: [reshape hull profile to long slender ski with upturned nose/tail and shallow open groove]
    keep_parts: [body, bobbin, body_to_bobbin, carved_hull, cavity_floor, front_bearing, rear_bearing, bobbin_core, cotton_thread]
    joint_policy: preserve the single body_to_bobbin revolute
    interface_policy: end bearings support the same axle in a shallow channel
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [honey vs dark end-grain, slimmer proportion], forbidden: [second bobbin, rollers, drift to ski/sled]}
  acceptance_focus: [slender upswept profile distinct from deep boat, retained spinning bobbin]

- variant_id: rec_loom_shuttle_var_mechanism_spindle_arm
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: classic boat shuttle with sprung hinged pirn spindle, why_same_subcategory: same wooden boat shuttle, only pirn-mounting mechanism changes}
  primary_axis: {slot: bobbin_mechanism, diversity_axis: ②, target_candidate: hinged pivoting spindle arm}
  structural_delta:
    change: [add spindle_arm part hinged to body (revolute Z, swings up), re-parent bobbin onto spindle_arm (revolute about spindle axis), latch notch at front end]
    keep_parts: [body, bobbin, carved_hull, cavity_floor, rear_bearing, front_metal_tip, rear_metal_tip, bobbin_core, cotton_thread]
    joint_policy: add exactly one new primary mechanism (arm hinge); pirn spin preserved as spin about the arm
    interface_policy: arm rooted at rear_bearing, free tip latches near front_bearing
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [steel vs brass spindle], forbidden: [rollers, flat-plank body, drift to knife/latch]}
  acceptance_focus: [arm hinge swings open, pirn spins on arm, boat identity kept]

- variant_id: rec_loom_shuttle_var_mechanism_end_delivery
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: end-delivery/end-feed cotton-mill shuttle, why_same_subcategory: weft shuttle feeding thread off a spinning pirn}
  primary_axis: {slot: bobbin_mechanism, diversity_axis: ②, target_candidate: fixed cantilever spindle + tension gate}
  structural_delta:
    change: [replace two-bearing symmetric axle with one fixed cantilever spindle rooted at rear, taper the pirn, drop far flange, add nose tension gate/porcupine eyelet]
    keep_parts: [body, bobbin, carved_hull, cavity_floor, front_metal_tip, rear_metal_tip, rear_bearing, bobbin_core, cotton_thread, front_flange]
    joint_policy: preserve one revolute (pirn spin) on the cantilever spindle
    interface_policy: pirn supported at root only; thread routed through nose tension gate
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [pale pirn wood, shorter taper], forbidden: [rollers, hinged arm, flat plank, drift to spinning-wheel bobbin]}
  acceptance_focus: [single-end supported spinning pirn, nose tension gate present]

- variant_id: rec_loom_shuttle_var_mechanism_roller
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: fly-shuttle/power-loom roller shuttle, why_same_subcategory: boat shuttle carrying weft, with belly rollers for the race}
  primary_axis: {slot: glide/underside, diversity_axis: ②, target_candidate: underside roller bogie (N=2)}
  structural_delta:
    change: [add 2 loop-emitted rollers recessed into the keel, each on its own continuous joint about Y, crown proud of keel]
    keep_parts: [body, bobbin, body_to_bobbin, carved_hull, cavity_floor, front_bearing, rear_bearing, bobbin_core, cotton_thread, front_metal_tip, rear_metal_tip]
    joint_policy: add continuous roller_{i}_spin joints; keep the bobbin revolute
    interface_policy: roller axles centered below hull on keel centerline
  multiplicity: {applies: true, target_n: 2, copied_object: roller_{i}, placement_rule: equal spacing along X}
  companion_variations: {allowed_④⑤⑥: [steel vs brass roller], forbidden: [remove bobbin, fixed rollers, drift to cart/toy]}
  acceptance_focus: [2 rollers spin continuously, bobbin still spins, boat identity kept]

- variant_id: rec_loom_shuttle_var_n_rollers4
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__loom_shuttle__002_png_c079a66081a7476caabf59d4c24e4019
  positioning: {product_archetype: heavier roller shuttle with four belly rollers, why_same_subcategory: same fly-shuttle loom shuttle, denser roller bogie}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 4 rollers}
  structural_delta:
    change: [set roller count to 4 using the same loop helper and continuous Y joints]
    keep_parts: [body, bobbin, body_to_bobbin, carved_hull, cavity_floor, front_bearing, rear_bearing, bobbin_core, cotton_thread, roller_{i}, roller_axle_{i}]
    joint_policy: keep bobbin revolute + per-roller continuous joints; only count changes
    interface_policy: equal spacing along keel centerline
  multiplicity: {applies: true, target_n: 4, copied_object: roller_{i}, placement_rule: equal spacing along X}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any non-roller slot change, hull/mechanism change]}
  acceptance_focus: [4 loop-emitted rollers, only count differs from N=2 variant]
```
