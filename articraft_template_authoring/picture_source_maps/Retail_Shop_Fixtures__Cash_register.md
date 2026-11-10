# Source Map — Retail_Shop Fixtures / Cash register

slug `cash_register` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_a-white-electronic-cash-register-with-a-tiered-c_20260708_092701_345704_546084bd` — picture/Retail_Shop Fixtures/Cash register/001.png
- `rec_a-dark-charcoal-electronic-cash-register-sitting_20260708_092443_475966_7fc07459` — picture/Retail_Shop Fixtures/Cash register/002.png

## Variants generated this batch (4 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_cash_register_var_body_flat_pos` | body_flat_pos | PASS | 25 | 1 |
| `rec_cash_register_var_body_tiered_tower` | body_tiered_tower | PASS | 62 | 2 |
| `rec_cash_register_var_n_bill7` | n_bill7 | PASS | 65 | 1 |
| `rec_cash_register_var_n_coin8` | n_coin8 | PASS | 62 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Retail_Shop Fixtures / Cash register

slug `cash_register` · pattern **mixed** (single drawer-base root → FIXED register head + PRISMATIC sliding cash drawer + REVOLUTE displays/covers/clips/lock + PRISMATIC keypad grid + coin/bill multiplicity)

richness band: **rich** · candidate anchors (origins + forks): **19** · fork jobs emitted: **4**

## subcategory_contract
```yaml
subcategory_contract:
  category: Retail_Shop Fixtures
  subcategory: Cash register
  core_identity: a counter-top electronic cash register — a drawer-base body carrying a keypad/receipt-printer/display head, with a sliding lockable cash drawer holding a coin/bill till
  must_keep:
    - sliding cash drawer with a bill/coin till (prismatic drawer joint)
    - pressable keypad and an operator/customer display
    - receipt-printer/paper feature on a fixed register head
    - at least one real non-fixed joint (drawer slide, key press, display tilt/swivel, cover/clip hinge, lock rotate)
  must_not_become:
    - bare POS computer / monitor / tablet stand / self-checkout kiosk
    - antique brass hand-crank mechanical register / desk calculator
    - vending machine / ticket dispenser / safe or lockbox
  image_evidence:
    - 001 white ECR: smooth wedge body, sloped multi-color keypad, top LCD pod, front receipt slot + hinged printer cover, sliding drawer open showing a single row of ~5 coin compartments, chrome key lock on the drawer front
    - 002 charcoal Sharp ER-A347: wedge body, twin open paper rolls, tiltable rear operator LCD, pole-mounted swiveling customer digit display, drawer till with 5 bill slots + hinged bill clips + 6 coin compartments, drawer lock cylinder
  parent_evidence:
    - A (white): root cabinet + FIXED console; _prism_mesh lofted wedge (rear_housing/keyboard_deck/display_pod); fixed display pod (LCD, no tilt); hinged printer_cover (revolute); 59 prismatic keys; cabinet_to_drawer prismatic; single-row till with coin_divider_{0..3} = 5 compartments; drawer_to_lock revolute
    - B (charcoal): root drawer_housing + FIXED register_body (cadquery _register_shell); twin paper rolls (open wells, no cover); lcd_display lcd_tilt revolute; customer_display_head display_head_yaw revolute; drawer_slide prismatic; _till_insert with 5 bill slots + 6 coin compartments; bill_clip_{0..4} revolute hinges; 55 prismatic keys; static lock_cylinder
```

## Slots & Candidates
| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| body_form ③ | classic_ecr_wedge | ③ | origin_anchor | A, B (lofted wedge body) | converged |
| body_form ③ | flat_pos_base | ③ | forked_anchor | rec_cash_register_var_body_flat_pos (from B) | planned |
| body_form ③ | tiered_tower (stacked tiers) | ③ | forked_anchor | rec_cash_register_var_body_tiered_tower (from A) | planned |
| display_mount ①② | fixed_display_pod | ①② | origin_anchor | A (display_pod, no joint) | converged |
| display_mount ①② | tilting_operator_lcd | ② | origin_anchor | B (lcd_tilt revolute) | converged |
| display_mount ①② | pole_swivel_customer_display | ①② | origin_anchor | B (display_head_yaw revolute) | converged |
| receipt_printer ② | hinged_printer_cover | ② | origin_anchor | A (console_to_printer_cover revolute) | converged |
| receipt_printer ② | open_twin_paper_wells | ① | origin_anchor | B (two roll wells, no cover) | converged |
| drawer_till ① | coin_only_single_row_till | ① | origin_anchor | A (coin_divider loop, no bills) | converged |
| drawer_till ① | bill_and_coin_till_with_clips | ① | origin_anchor | B (_till_insert bills+coins + bill_clips) | converged |
| drawer_motion/security ② | sliding_cash_drawer | ② | origin_anchor | A, B (prismatic drawer) — core | converged |
| drawer_motion/security ② | rotating_key_lock | ② | origin_anchor | A (drawer_to_lock revolute) | converged |
| drawer_till ② | hinged_bill_clips | ② | origin_anchor | B (bill_clip_{i}_hinge revolute) | converged |
| keypad ② | pressable_keys | ② | origin_anchor | A, B (per-key prismatic) | converged |
| multiplicity N | coin_compartments N=5 | N | origin_anchor | A (4 dividers → 5) | converged |
| multiplicity N | coin_compartments N=6 | N | origin_anchor | B (6 coin cells) | converged |
| multiplicity N | coin_compartments N=8 | N | forked_anchor | rec_cash_register_var_n_coin8 (from A) | planned |
| multiplicity N | bill_slots/clips N=5 | N | origin_anchor | B (5 bill slots + 5 clips) | converged |
| multiplicity N | bill_slots/clips N=7 | N | forked_anchor | rec_cash_register_var_n_bill7 (from B) | planned |

Every supported slot reaches ≥2 structurally distinct candidates from the two origins alone; forks add two new ③ form families and additional multiplicity samples.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed | cabinet→FIXED head→drawer chain (A,B); open paper wells vs boxed printer bay; single-row coin till vs bill+coin till; forks add stacked-tier tower and flat-base+upright-screen skeletons |
| ② joint / mechanism | source-backed | prismatic drawer (A,B); prismatic keys (A,B); revolute printer cover (A); revolute drawer lock (A); revolute operator LCD tilt (B); revolute customer-display yaw (B); revolute bill clips (B). Fully covered by origins — no ②-only fork needed |
| ③ primary form family | source-backed (forks) | classic ECR wedge (A,B) → flat POS base (fork) + tiered tower (fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | brand plaque/model label (A), digit band + SHARP badge (B), color-coded key legends; extrapolate host-conformal decals only |
| ⑤ proportion / size / travel | record_only | body ~0.40-0.44 W; drawer travel A=0.245 / B=0.30; key travel ~0.0025-0.0028; LCD tilt ±0.40; yaw ±1.6; cover 0→1.35 |
| ⑥ material / palette / finish | record_only | white/cream ECR (A) vs charcoal/woodgrain (B); multi-color keycaps; chrome lock; teal/blue LCD; green VFD digits |

## Multiplicity / Copy Logic
- **coin compartments** — count_param on `coin_divider_{i}` (A) / coin-cut loop (B). N samples {5 (A), 6 (B), 8 (fork)}; N_range [4,10]; copied object = divider box / cut; even x-spacing along tray width; FIXED decoration on cash_drawer.
- **bill slots + bill clips** — count_param shared by `_till_insert` bill cuts and `bill_clip_{i}` loop (B). N samples {5 (B), 7 (fork)}; N_range [3,8]; copied object = bill slot cut + hinged clip; even x-spacing; one `bill_clip_{i}_hinge` REVOLUTE per clip; indexed names bill_clip_0..N-1.
- **keypad** — heterogeneous multi-block grid (function/department/numeric/mode/payment); loop-emitted per block but not a single clean count_param, so NOT used as an N sample axis.

## Budget Decision
Two content-rich origins already back ~15 candidate anchors across 6 slots (all major mechanisms + both till families + both display treatments). Forks add only genuinely new structural vocabulary: 2 new ③ body-form families (flat POS, tiered tower) and 2 extra multiplicity samples (coin N=8, bill N=7). Total 19 anchors = rich band, coverage-first, no ④/⑤/⑥/scale/material padding. No compatibility probes needed (interfaces reuse existing mating faces). No blocked candidates.

## Variant Cards
```yaml
- variant_id: rec_cash_register_var_body_flat_pos
  source_type: forked_anchor
  parent_record_id: rec_a-dark-charcoal-electronic-cash-register-sitting_...7fc07459 (B)
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: flat_pos_base}
  structural_delta:
    change: [replace lofted wedge _register_shell with a shallow flat control deck on the drawer_housing top, raise lcd_display onto an upright neck via lcd_tilt, relocate keypad onto the flat deck]
    keep_parts: [drawer_housing, housing_to_body, cash_drawer, till, drawer_slide, lcd_display, lcd_tilt, customer_display_head, display_head_yaw]
    joint_policy: preserve all joints; only the body envelope form changes
    interface_policy: register head still FIXED-seated on housing top; keypad/display keep existing mounts
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [lighter POS palette], forbidden: [count change, joint-graph change, category drift to POS computer/kiosk]}
  acceptance_focus: [drawer still slides + retains, keypad keys still press, LCD tilts upright, stays same subcategory]

- variant_id: rec_cash_register_var_body_tiered_tower
  source_type: forked_anchor
  parent_record_id: rec_a-white-electronic-cash-register-with-a-tiered-c_...546084bd (A)
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: tiered_tower}
  structural_delta:
    change: [rebuild console head as 3 stacked box tiers (keyboard / printer / display crown) replacing the single lofted wedge]
    keep_parts: [cabinet, cabinet_to_console, console, printer_cover, console_to_printer_cover, cash_drawer, cabinet_to_drawer, drawer_lock, drawer_to_lock, keypad helpers, coin_divider loop]
    joint_policy: preserve all joints; keys on lower tier, cover on mid tier, screen on crown
    interface_policy: tiers stack on the FIXED console; keys still through-seat into keyboard tier
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [retro cream/black palette], forbidden: [count change, mechanical/antique drift, calculator/kiosk drift]}
  acceptance_focus: [keys press, printer cover hinges, drawer slides, LCD present, same subcategory]

- variant_id: rec_cash_register_var_n_coin8
  source_type: forked_anchor
  parent_record_id: rec_a-white-electronic-cash-register-with-a-tiered-c_...546084bd (A)
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 8 coin compartments}
  structural_delta:
    change: [coin_divider count_param 4→7 dividers → 8 compartments]
    keep_parts: [cash_drawer, tray_floor, tray walls, cabinet_to_drawer, drawer_lock, keypad, printer_cover]
    joint_policy: no joint change; dividers FIXED decoration
    interface_policy: dividers evenly spaced inside tray_floor, indexed coin_divider_0..6
  multiplicity: {applies: true, target_n: 8, copied_object: coin_divider box, placement_rule: even x-spacing}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [add bills, change drawer travel or body]}
  acceptance_focus: [8 compartments count test, drawer slides, single-row coin till preserved]

- variant_id: rec_cash_register_var_n_bill7
  source_type: forked_anchor
  parent_record_id: rec_a-dark-charcoal-electronic-cash-register-sitting_...7fc07459 (B)
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 7 bill slots + 7 clips}
  structural_delta:
    change: [bill-slot count_param 5→7 in _till_insert cuts and bill_clip loop]
    keep_parts: [drawer_housing, register_body, cash_drawer, till, drawer_slide, _till_insert, _bill_clip, coin compartments, keypad, lcd_display, customer_display_head]
    joint_policy: one bill_clip_{i}_hinge REVOLUTE per clip, N=7
    interface_policy: clips evenly spaced across rear till width, hinge tubes captured in till rear wall, bill_clip_0..6
  multiplicity: {applies: true, target_n: 7, copied_object: bill slot cut + hinged clip, placement_rule: even x-spacing}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [change coin count, drawer travel, body, displays]}
  acceptance_focus: [7 bill clips count test, clips lift, coin compartments unchanged, drawer slides]
```

## Blocked / Excluded
- keypad N-sweep — keypad is a heterogeneous multi-block grid, not a single clean count_param; excluded as an N axis (kept as loop-emitted per-block reference only).
- ②-only mechanism fork — all major mechanisms (drawer prismatic, key prismatic, cover revolute, lock revolute, LCD tilt, display yaw, bill-clip hinge) are already origin-backed; no honest new mechanism to add, so none forked (no padding).
- compatibility_probe — none; forks reuse existing mating faces/joints with no risky new interface combination.
