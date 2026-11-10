# Source Map — Textiles_Fabric / Sewing machine

slug `sewing_machine` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_an-antique-cast-iron-treadle-sewing-machine-tabl_20260708_092552_203468_a491cf01` — picture/Textiles_Fabric/Sewing machine/001.png
- `rec_a-white-compact-household-sewing-machine-brother_20260708_092052_578006_396304d9` — picture/Textiles_Fabric/Sewing machine/002.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_sewing_machine_var_base_freearm` | base_freearm | PASS | 7 | 1 |
| `rec_sewing_machine_var_mechanism_handcrank` | mechanism_handcrank | PASS | 7 | 1 |
| `rec_sewing_machine_var_mechanism_takeup` | mechanism_takeup | PASS | 7 | 1 |
| `rec_sewing_machine_var_n2` | n2 | PASS | 6 | 1 |
| `rec_sewing_machine_var_n6` | n6 | PASS | 10 | 1 |
| `rec_sewing_machine_var_skeleton_industrial` | skeleton_industrial | PASS | 3 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Textiles_Fabric / Sewing machine

slug `sewing_machine` · pattern **mixed** (C-shaped head casting [bed/pillar/arm/nose] with an
articulated needle stroke + rotary drive; hosted on either a treadle cabinet+stand or a flat bench
bed; drawer multiplicity on the cabinet variant).

Richness band: **rich (low end)** — 18 candidate anchors (12 origin + 6 fork). Coverage-first, no padding.

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Sewing machine
  core_identity: >
    A machine that forms stitches in fabric: a C-shaped head (bed + pillar + arm + head/nose)
    carrying a reciprocating needle bar over a stitch/needle plate, driven through a balance
    handwheel, with thread-handling controls (tension, take-up) and a presser foot.
  must_keep:
    - C-shaped head with overhanging arm and a needle bar above a stitch plate
    - a real rotary drive (balance handwheel / band wheel / crank / belt) — at least one non-fixed joint
    - a reciprocating needle mechanism (needle_stroke prismatic) and a stitch/needle plate
  must_not_become:
    - serger / overlocker (thread-cone rack + loopers, no single lockstitch head)
    - multi-needle embroidery machine
    - plain table / workbench / cabinet with no machine head
    - a bare hand tool (crank, wheel) with no sewing head
  image_evidence:
    - "001: antique cast-iron treadle table — spoked band drive wheel + foot treadle lattice + pitman
       rod; ornate iron stand; oak cabinet with carved-medallion drawers both sides; black-japanned
       gold-decal C head with balance handwheel, needle bar, stitch plate, hand crank knob."
    - "002: white compact Brother LX3817 — molded C body (pillar+arm+head), side handwheel, fluted
       stitch-selector dial + reverse lever + tension dial on the front, chrome needle bar + presser
       foot over a silver needle plate, spool pin/bobbin winder on top, blue paisley art panel."
  parent_evidence:
    - "A (treadle): parts treadle_stand, table (+add_cabinet), machine_head, handwheel[continuous],
       needle_bar[prismatic], band_wheel[continuous], treadle_pedal[revolute + pitman eye],
       3 drawers[prismatic] via add_drawer helper."
    - "B (compact): parts bed, body[C casting], handwheel[continuous], stitch_dial[revolute],
       reverse_lever[prismatic], tension_dial[revolute], needle_bar[prismatic], presser_foot[prismatic]."
```

## Slots and Candidates
| slot | candidates | notes |
|---|---|---|
| mount_form (①) | treadle_cabinet_table(A) · compact_benchtop(B) · industrial_power_table(fork) | ≥2 met |
| drive_mechanism (②) | foot_treadle+band_wheel(A) · internal_electric_handwheel(B) · external_hand_crank(fork) · underslung_motor+v_belt(fork, rides on industrial) | ≥2 met |
| head_controls (②) | needle_bar/needle_stroke(A,B) · presser_foot lift(B) · stitch_selector dial(B) · tension dial(B) · reverse lever(B) · thread take_up_lever(fork) | ≥2 met |
| support_base (③) | cabinet_with_drawers(A) · flat_solid_bed(B) · free_arm_cylinder(fork) | ≥2 met |
| multiplicity — cabinet drawers (N) | N=2(fork) · N=3(A, origin) · N=6(fork) | 3 N samples |

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | treadle cabinet+stand(A) / compact bench body(B) / industrial K-leg power table(fork) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | continuous handwheel & band wheel; revolute treadle, stitch dial, tension dial; prismatic needle bar, presser foot, reverse lever, drawers; fork adds external hand-crank grip (continuous) and oscillating take-up lever (revolute) |
| ③ primary form family | source-backed (origin + forked_anchor) | drawered cabinet base(A) / flat solid bench bed(B) / cantilevered free-arm cylinder + removable tray(fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | gold japanned decals & carved drawer medallions(A); blue paisley art panel + printed stitch-selector dial face & brand text(B); host-conformal only |
| ⑤ proportion / size / travel | record_only | full table ~0.92×0.46×1.06 m(A) vs compact ~0.40×0.17×0.30 m(B); needle travel ~0.008–0.011; drawer travel ~0.20; may ride along as companion on structural forks |
| ⑥ material / palette / finish | record_only | black cast iron + oak/dark wood + nickel + gold(A); white ABS + steel/chrome + pale blue(B); industrial grey/green enamel; may ride as companion |

## Multiplicity / Copy Logic
- count_param: number of cabinet accessory drawers (`add_drawer` calls under `add_cabinet`).
- N samples: **2 (fork), 3 (origin A), 6 (fork)**.
- suggested N_range: [2, 6].
- copied object: one dovetailed drawer (front_panel + medallion/knob + bottom + side_walls + back_wall).
- naming: indexed `drawer_0..drawer_N` (or `left_drawer_i` / `right_drawer_i`).
- placement: one-per-pedestal (N=2) → vertically stacked bank per pedestal (N=6), uniform spacing.
- joint policy: each drawer an independent `table_to_<drawer>` PRISMATIC, axis -Y (front pull-out), shared helper/loop, no body-family or joint-type change.

## Budget Decision
- Origin candidate anchors (counted, no fork): 12 — mount_form ×2 (A,B), drive_mechanism ×2 (treadle+bandwheel A, handwheel B), head_controls ×5 (needle_bar, presser lift, stitch dial, tension dial, reverse lever — all B; needle_bar also in A), support_base ×2 (cabinet A, flat bed B), multiplicity N=3 (A).
- Fork candidate anchors (counted): 6 — handcrank(②), industrial_table(①), free_arm(③), take_up_lever(②), drawers N=2, drawers N=6.
- Total candidate anchors: **18** (rich, low end). No ④/⑤/⑥-only or scale-only variants counted.
- No compatibility probes needed: all fork interfaces (crank-on-wheel, belt-to-wheel, tray-on-arm, drawer-in-cabinet) are single-axis and low-risk.

## Blocked / Gated
- **serger / overlocker form (③ + thread-cone multiplicity)**: gated — same broad domain but drifts to a
  neighbor archetype (multi-cone rack + loopers, no single lockstitch head). Not emitted; revisit only
  if the subcategory is explicitly widened to overlockers.
- **embroidery multi-needle head**: blocked — neighbor category (multi-needle bar array), out of scope.
- **external electronic foot pedal / knee lift as its own object**: blocked — a separate accessory, not
  part of the machine skeleton.

## Variant Cards (forks only)
```yaml
- variant_id: rec_sewing_machine_var_mechanism_handcrank
  source_type: forked_anchor
  parent_record_id: rec_a-white-compact-household-sewing-machine-brother_20260708_092052_578006_396304d9
  positioning: {product_archetype: portable hand-crank domestic machine, why_same_subcategory: same C head + needle bar + stitch plate, only manual power input differs}
  primary_axis: {slot: drive_mechanism, diversity_axis: ②, target_candidate: external_hand_crank}
  structural_delta:
    change: [crank_arm fixed to handwheel rim at offset, free-spinning crank_grip on a pin]
    keep_parts: [bed, body, handwheel, handwheel_spin, needle_bar, needle_stroke, presser_foot, stitch_dial]
    joint_policy: keep handwheel_spin continuous; add one revolute/continuous grip on the crank arm
    interface_policy: crank offset from axle, clears the pillar face through full rotation
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [black-japanned+gold palette], forbidden: [treadle/motor add, base-form change]}
  acceptance_focus: [crank_grip orbits wheel axle, no pillar collision, wheel still continuous]

- variant_id: rec_sewing_machine_var_skeleton_industrial
  source_type: forked_anchor
  parent_record_id: rec_an-antique-cast-iron-treadle-sewing-machine-tabl_20260708_092552_203468_a491cf01
  positioning: {product_archetype: industrial flatbed lockstitch on a K-leg power table, why_same_subcategory: same head + needle bar + handwheel, power table replaces treadle stand}
  primary_axis: {slot: mount_form, diversity_axis: ①, target_candidate: industrial_power_table}
  structural_delta:
    change: [replace cast legs/band wheel/pitman/treadle with steel K-frame + flat table, add motor_box + v_belt + motor_pulley]
    keep_parts: [machine_head, bed, arm, pillar, nose, needle_bar, head_to_needle_bar, handwheel, head_to_handwheel, stitch_plate, presser_bar, presser_foot, table]
    joint_policy: keep handwheel continuous + needle prismatic; add motor_pulley continuous belt drive (defines the power table)
    interface_policy: bedplate flush in table cutout; belt loops pulley to balance wheel
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [grey/green enamel, larger bed], forbidden: [keep treadle/cabinet, drawer N change]}
  acceptance_focus: [table legs reach floor, belt spans pulley-to-wheel, head over table cutout]

- variant_id: rec_sewing_machine_var_base_freearm
  source_type: forked_anchor
  parent_record_id: rec_a-white-compact-household-sewing-machine-brother_20260708_092052_578006_396304d9
  positioning: {product_archetype: portable free-arm household machine, why_same_subcategory: same C body + needle bar, bed reshaped to a free arm}
  primary_axis: {slot: support_base, diversity_axis: ③, target_candidate: free_arm_cylinder}
  structural_delta:
    change: [reshape bed into cantilevered rounded free-arm sleeve, add removable accessory_tray sliding off the arm]
    keep_parts: [body, body_shell, handwheel, needle_bar, needle_stroke, presser_foot, stitch_dial, needle_plate, feed_dog]
    joint_policy: keep needle_stroke prismatic; add one prismatic accessory_tray slide (the free-arm reveal)
    interface_policy: tray wraps arm, slides off toward front; needle plate on arm upper end
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [white/pastel ABS], forbidden: [drive change, treadle/industrial base]}
  acceptance_focus: [needle over plate on arm end, tray slides off to expose free arm]

- variant_id: rec_sewing_machine_var_mechanism_takeup
  source_type: forked_anchor
  parent_record_id: rec_a-white-compact-household-sewing-machine-brother_20260708_092052_578006_396304d9
  positioning: {product_archetype: mechanical lockstitch thread take-up lever, why_same_subcategory: standard visible head mechanism on the same machine}
  primary_axis: {slot: head_controls, diversity_axis: ②, target_candidate: oscillating_take_up_lever}
  structural_delta:
    change: [add hooked take_up_lever pivoting on a head-front boss, thread eye at free end sweeping through takeup_slot]
    keep_parts: [body, body_shell, takeup_slot, needle_bar, needle_stroke, handwheel, presser_foot, stitch_dial, tension_dial]
    joint_policy: add exactly one revolute joint (lever about +X); do not add a full linkage
    interface_policy: pivot on a visible boss on the head; eye travels within takeup_slot, no float
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [chrome vs black lever], forbidden: [base-form or drive change, looper]}
  acceptance_focus: [lever pivots on boss, eye sweeps up/down, no floating link]

- variant_id: rec_sewing_machine_var_n2
  source_type: forked_anchor
  parent_record_id: rec_an-antique-cast-iron-treadle-sewing-machine-tabl_20260708_092552_203468_a491cf01
  positioning: {product_archetype: two-drawer treadle cabinet, why_same_subcategory: identical machine, drawer count only}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: N=2}
  structural_delta:
    change: [emit 2 drawers via shared helper, one per side cabinet]
    keep_parts: [treadle_stand, table, machine_head, handwheel, needle_bar, band_wheel, treadle_pedal, add_cabinet, add_drawer]
    joint_policy: each drawer independent prismatic (axis -Y); no joint-type change
    interface_policy: single drawer opening per cabinet; loop-emitted, indexed names
  multiplicity: {applies: true, target_n: 2, copied_object: drawer, placement_rule: one-per-pedestal}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [head/drive/base change, hand-written drawers]}
  acceptance_focus: [exactly 2 drawers, each pulls out front, loop-emitted indexed names]

- variant_id: rec_sewing_machine_var_n6
  source_type: forked_anchor
  parent_record_id: rec_an-antique-cast-iron-treadle-sewing-machine-tabl_20260708_092552_203468_a491cf01
  positioning: {product_archetype: six-drawer treadle cabinet, why_same_subcategory: identical machine, drawer count only}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: N=6}
  structural_delta:
    change: [emit 6 drawers via shared helper, three stacked per side cabinet]
    keep_parts: [treadle_stand, table, machine_head, handwheel, needle_bar, band_wheel, treadle_pedal, add_cabinet, add_drawer]
    joint_policy: each drawer independent prismatic (axis -Y); no joint-type change
    interface_policy: three uniform drawer openings per cabinet; loop-emitted, indexed names
  multiplicity: {applies: true, target_n: 6, copied_object: drawer, placement_rule: stacked-bank-per-pedestal, spacing: uniform}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [head/drive/base change, hand-written drawers]}
  acceptance_focus: [exactly 6 drawers, uniform stacking, each pulls out front]
```

## Fork jobs emitted: 6
- rec_sewing_machine_var_mechanism_handcrank (② drive) ← parent B
- rec_sewing_machine_var_skeleton_industrial (① mount) ← parent A
- rec_sewing_machine_var_base_freearm (③ base) ← parent B
- rec_sewing_machine_var_mechanism_takeup (② head control) ← parent B
- rec_sewing_machine_var_n2 (N=2 drawers) ← parent A
- rec_sewing_machine_var_n6 (N=6 drawers) ← parent A
