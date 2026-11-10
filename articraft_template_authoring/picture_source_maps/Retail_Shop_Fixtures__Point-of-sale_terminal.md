# Source Map — Retail_Shop Fixtures / Point-of-sale terminal

slug `point_of_sale_terminal` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_a-silver-handheld-wireless-point-of-sale-payment_20260708_092652_294276_074f8840` — picture/Retail_Shop Fixtures/Point-of-sale terminal/002.png
- `rec_a-gray-handheld-point-of-sale-payment-terminal-w_20260708_091455_488779_4430a86e` — picture/Retail_Shop Fixtures/Point-of-sale terminal/001.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_point_of_sale_terminal_var_base_dock_tilt` | base_dock_tilt | PASS | 22 | 1 |
| `rec_point_of_sale_terminal_var_base_pole_swivel` | base_pole_swivel | PASS | 22 | 1 |
| `rec_point_of_sale_terminal_var_body_touchscreen` | body_touchscreen | PASS | 4 | 1 |
| `rec_point_of_sale_terminal_var_display_tilt` | display_tilt | PASS | 22 | 1 |
| `rec_point_of_sale_terminal_var_softkeys_n2` | softkeys_n2 | PASS | 19 | 1 |
| `rec_point_of_sale_terminal_var_softkeys_n6` | softkeys_n6 | PASS | 23 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Retail_Shop Fixtures / Point-of-sale terminal

slug: `point_of_sale_terminal`
pattern: **parallel_children + multiplicity** (single housing root carries independent revolute printer cover, continuous/static paper roll, prismatic sliding card, and a keypad field of prismatic keys; soft/menu key row is loop-multiplicity)
richness band: **normal** (target low end)
parents (both origins, free anchors):
- A `rec_a-silver-handheld-wireless-point-of-sale-payment_20260708_092652_294276_074f8840` — picture `Retail_Shop Fixtures/Point-of-sale terminal/002.png`
- B `rec_a-gray-handheld-point-of-sale-payment-terminal-w_20260708_091455_488779_4430a86e` — picture `Retail_Shop Fixtures/Point-of-sale terminal/001.png`

---

## subcategory_contract
```yaml
subcategory_contract:
  category: Retail_Shop Fixtures
  subcategory: Point-of-sale terminal
  core_identity: A self-contained electronic payment terminal that reads cards and takes a PIN/entry, with a display and card/receipt I/O.
  must_keep:
    - a display (screen + bezel) as the primary output
    - some payment entry input (physical keypad OR touchscreen soft keys)
    - at least one real card/payment interface (chip slot, magstripe swipe groove, or inserted card) and/or receipt printer
    - at least one real non-fixed joint (key press, printer cover hinge, paper roll spindle, card slide, or a mount/tilt/swivel)
  must_not_become:
    - cash register / full POS system with cash drawer
    - tablet or smartphone
    - self-checkout kiosk / floor-standing terminal tower
    - barcode scanner or handheld scanner
    - calculator
    - bare mobile card-reader dongle (mPOS, no display/keypad/printer)
  image_evidence:
    - "002/A: silver wedge with angled color screen showing AMOUNT + NFC glyph, 4 soft keys, 12 numeric keys, red/yellow/green command keys, rear receipt printer bulge, rounded sides"
    - "001/B: gray wedge, framed LCD, 4 soft keys under display, 3x4 numeric keypad (F/0/dot), red X / yellow / green O command row, rear flip printer deck, magstripe groove on right side, dimple grip texture"
  parent_evidence:
    - "A: wedge housing (side profile extruded + filleted), sloped display via _on_slope/SLOPE_PITCH, menu_strip + 4 menu_key prismatic presses, 12 numeric + 3 colored command prismatic keys, printer_cover REVOLUTE hinge, paper_roll CONTINUOUS spindle + axle, static chip_slot_liner + swipe_slot_liner, 4 rubber feet"
    - "B: wedge housing (YZ wedge intersect rounded footprint), keypad_plate, display_bezel+screen, 4 function_key + 3x4 numeric + 3 command prismatic keys, paper_cover REVOLUTE hinge with knuckles/bosses, static paper_roll in bay, bank_card PRISMATIC slide in chip slot, magstripe groove, 4 rubber feet"
```

---

## Slots and Candidates
Typical layers: body_form, display_mount, receipt_printer, card_interface, support_or_base, soft_key_row (N), numeric_keypad (N, standardized).

| slot | candidate | axis | source_type | evidence / record | key parts/joints | status |
|---|---|---|---|---|---|---|
| body_form | wedge handheld/countertop block | ③ | origin_anchor | A, B housing | housing (wedge profile) | converged |
| body_form | touchscreen smart terminal (screen-dominant) | ③ | forked_anchor | rec_..._var_body_touchscreen (fork B) | enlarged display_screen, side hard buttons | planned |
| display_mount | fixed sloped display face | ②/① | origin_anchor | A, B | display_bezel/display_screen on slope | converged |
| display_mount | tilting display head (revolute) | ② | forked_anchor | rec_..._var_display_tilt (fork A) | display_head + housing_to_display_head revolute | planned |
| receipt_printer | flip-cover hinge + paper roll | ② | origin_anchor | A, B | printer_cover + hinge revolute | converged |
| receipt_printer | continuous paper-roll spindle | ② | origin_anchor | A | paper_roll + paper_roll_spindle continuous | converged (A shows; B static) |
| card_interface | static chip slot + magstripe groove | ②(static) | origin_anchor/record | A (+B groove) | chip_slot_liner, swipe_slot_liner | converged |
| card_interface | inserted sliding chip card (prismatic) | ② | origin_anchor | B | bank_card + housing_to_bank_card prismatic | converged |
| support_or_base | flat rubber feet on counter | ① | origin_anchor | A, B | foot_0..3 | converged (baseline support) |
| support_or_base | countertop tilt dock/cradle base + recline neck | ① | forked_anchor | rec_..._var_base_dock_tilt (fork A) | dock_base root + base_to_body revolute (pitch) | planned |
| support_or_base | checkout swivel pedestal stand | ① | forked_anchor | rec_..._var_base_pole_swivel (fork A) | stand_base + stand_pole + stand_to_body revolute (yaw) | planned |
| soft_key_row | N=4 soft/menu keys | N | origin_anchor | A (menu_key), B (function_key) | menu_key_{i} prismatic loop | converged |
| soft_key_row | N=2 soft keys | N | forked_anchor | rec_..._var_softkeys_n2 (fork A) | menu_key_0..1 loop | planned |
| soft_key_row | N=6 soft keys | N | forked_anchor | rec_..._var_softkeys_n6 (fork A) | menu_key_0..5 loop | planned |
| numeric_keypad | 12-key numeric grid (3x4) | N | origin_anchor/record | A, B | key_1..key_hash prismatic | converged (standardized 12; no N-sweep) |

Each supported functional slot reaches >=2 structurally distinct candidates: body_form (2), display_mount (2), card_interface (2 + static), receipt_printer (2 mechanisms), support_or_base (3), soft_key_row (3 N samples).

---

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked) | flat-footed monobody (A,B); + tilt-dock base->body recline; + swivel pedestal stand->body yaw; touchscreen removes keypad sub-tree |
| ② joint / mechanism | source-backed (origin + forked) | key PRISMATIC press (A,B); printer_cover REVOLUTE (A,B); paper_roll CONTINUOUS spindle (A); bank_card PRISMATIC slide (B); + display-tilt REVOLUTE; + dock recline REVOLUTE; + pedestal yaw REVOLUTE |
| ③ primary form family | source-backed (origin + forked) | keypad wedge block (A,B) vs screen-dominant touchscreen slab (fork B) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | screen graphics (AMOUNT, NFC contactless glyph, status bar), key legends (1QZ/2ABC digits, F, dot, X/O), dimple grip texture (B), serrated tear bar, card logo/band; extrapolate brand badge decal — companion only, never standalone |
| ⑤ proportion / size / travel | record_only | body ~0.18 m long x 0.082 wide; key travel 0.0015-0.0022; cover open 0..~1.85 rad; card slide 0..0.018; roll continuous; feet ~0.006 r — may ride along as companion |
| ⑥ material / palette / finish | record_only | silver plastic (A) / gray plastic (B); charcoal keypad plate; black keys; red/amber/green command keys; blue/pale screen; white paper; blue bank card — companion only |

①②③ and N are candidate-anchor axes and source-backed. ④⑤⑥ are record_only/companion; none used to hit the budget.

---

## Multiplicity / Copy Logic
- **soft/menu key row** — `count_param`: length of `MENU_KEYS_Y` (menu_key_{i} loop, A) / function-key loop (B). N samples: {4 (A,B origin), 2 (fork), 6 (fork)}. suggested N_range [2,6]. copied_object: menu keycap (shared `menu_mesh`). naming: `menu_key_{i}`. placement: evenly spaced across `menu_strip` width. joint_policy: each an independent PRISMATIC press (parent `menu_limits`), no other change.
- **numeric keypad** — `count_param`: 12 fixed (KEY_ROWS_X x KEY_COLS_Y = 4x3). Standardized dial-pad; loop-emitted (`grid_names` zip) but NOT a fork-worthy N-sweep. record_only. naming `key_1..key_9/key_star/key_0/key_hash` (A) or `key_f/key_dot` (B).
- **command keys** — 3 colored keys (cancel/clear/enter), fixed semantic triad; not an N-sweep.
- **rubber feet** — 4, `foot_{i}` loop; migrate to base underside in dock/pedestal forks; not an N-sweep.

---

## Budget Decision
Counted candidate anchors (origin_anchor + converged forked_anchor; probes/baseline/④⑤⑥ excluded):
1. wedge block body ③ (A,B)
2. touchscreen slab body ③ (fork)
3. printer flip-cover revolute ② (A,B)
4. continuous paper-roll spindle ② (A)
5. sliding inserted chip card prismatic ② (B)
6. tilting display head revolute ② (fork)
7. numeric keypad N=12 prismatic (A,B)
8. soft-key row N=4 (A,B)
9. soft-key row N=2 (fork)
10. soft-key row N=6 (fork)
11. flat rubber-feet support ① (A,B)
12. tilt dock/cradle base ① (fork)
13. swivel pedestal stand ① (fork)

**Total candidate anchors: 13** (normal band 12-18, low end — coverage first, no padding). **Fork jobs emitted: 6.** Origins already supply 7 candidate anchors needing no fork.

underfilled_reason: n/a for a small handheld electronic; deliberately kept at the low end. Rejected filler to avoid neighbor drift (see Blocked).

---

## Variant Cards (one per planned fork)
```yaml
- variant_id: rec_point_of_sale_terminal_var_body_touchscreen
  source_type: forked_anchor
  parent_record_id: rec_a-gray-handheld-point-of-sale-payment-terminal-w_...4430a86e
  positioning: {product_archetype: Android smart POS (Clover/PAX A920/Square), why_same_subcategory: keeps printer + chip slot + magstripe + NFC and reads/takes payment}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: screen-dominant touchscreen slab}
  structural_delta:
    change: [delete 3x4 numeric + command keys and their prismatic joints, enlarge display to cover top face, add 1-2 side hard buttons]
    keep_parts: [housing, display_bezel, display_screen, paper_cover, housing_to_paper_cover, paper_roll, bank_card, housing_to_bank_card, foot_0..3]
    joint_policy: replace keypad prismatic field with 1-2 side-button prismatic joints (>=1 non-fixed joint remains)
    interface_policy: retain chip slot floor + magstripe groove + printer bay
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [NFC glyph + status bar screen graphic, dark glass finish], forbidden: [remove payment I/O, become tablet/register]}
  acceptance_focus: [compile/tests pass, printer cover + card slide still articulate, screen dominates top face]

- variant_id: rec_point_of_sale_terminal_var_display_tilt
  source_type: forked_anchor
  parent_record_id: rec_a-silver-handheld-wireless-point-of-sale-payment_...074f8840
  positioning: {product_archetype: adjustable-angle countertop PIN pad (Verifone MX), why_same_subcategory: same terminal, screen articulated}
  primary_axis: {slot: display_mount, diversity_axis: ②, target_candidate: tilting display head revolute}
  structural_delta:
    change: [move display_bezel+display_screen onto new display_head link, add housing_to_display_head revolute (Y axis) at rear-top edge, add visible hinge boss]
    keep_parts: [body, menu_strip, menu_key_0..3, key_1..key_hash, cancel_key/clear_key/enter_key + *_press, printer_cover, printer_cover_hinge, paper_roll, paper_roll_spindle, foot_0..3]
    joint_policy: add exactly one revolute display-tilt hinge
    interface_policy: hinge barrel/boss contacts housing so head is supported
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [bezel color, screen graphic], forbidden: [keypad count, printer mechanism, adding a base]}
  acceptance_focus: [head tilts up about Y, not floating, keypad/printer unchanged]

- variant_id: rec_point_of_sale_terminal_var_base_dock_tilt
  source_type: forked_anchor
  parent_record_id: rec_a-silver-handheld-wireless-point-of-sale-payment_...074f8840
  positioning: {product_archetype: countertop charging cradle/dock, why_same_subcategory: same terminal seated in its dock}
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: tilt dock/cradle base + recline neck}
  structural_delta:
    change: [add dock_base root cradle tray, move foot_0..3 to base underside, add base_to_body revolute (Y pitch) recline 0..0.35]
    keep_parts: [body + all its keys/cover/roll joints]
    joint_policy: add one revolute recline neck; body becomes child of dock_base
    interface_policy: cradle floor/upstand contacts terminal underside/rear
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [dock color, contact-pad detail], forbidden: [pole/swivel, form family, keypad, printer]}
  acceptance_focus: [terminal reclines on cradle, supported, internal joints intact]

- variant_id: rec_point_of_sale_terminal_var_base_pole_swivel
  source_type: forked_anchor
  parent_record_id: rec_a-silver-handheld-wireless-point-of-sale-payment_...074f8840
  positioning: {product_archetype: retail checkout swivel-pedestal PIN pad, why_same_subcategory: same terminal on a shop-fixture stand}
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: swivel pedestal stand}
  structural_delta:
    change: [add stand_base disk + stand_pole column, move feet to base, add stand_to_body revolute (Z yaw) +/-1.4]
    keep_parts: [body + all its keys/cover/roll joints]
    joint_policy: add one revolute vertical yaw swivel; body becomes child of stand
    interface_policy: pole top cradles terminal underside so supported
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [stand finish, base weight-ring], forbidden: [tilt hinge, form family, keypad, printer]}
  acceptance_focus: [terminal yaws on pole, supported, distinct from dock-tilt]

- variant_id: rec_point_of_sale_terminal_var_softkeys_n2
  source_type: forked_anchor
  parent_record_id: rec_a-silver-handheld-wireless-point-of-sale-payment_...074f8840
  positioning: {product_archetype: minimal 2 soft-key menu row, why_same_subcategory: same terminal, fewer soft keys}
  primary_axis: {slot: soft_key_row, diversity_axis: N, target_candidate: N=2}
  structural_delta:
    change: [re-parameterize MENU_KEYS_Y to 2 columns, loop-generate menu_key_0..1]
    keep_parts: [body, menu_strip, numeric grid, command keys, printer_cover/hinge, paper_roll/spindle, foot_0..3]
    joint_policy: preserve prismatic menu press; count only changes
    interface_policy: evenly spaced on menu_strip
  multiplicity: {applies: true, target_n: 2, copied_object: menu keycap, placement_rule: even spacing across strip}
  companion_variations: {allowed_④⑤⑥: [menu key color], forbidden: [numeric grid, form, printer, joint types]}
  acceptance_focus: [exactly 2 loop-emitted menu keys, each presses]

- variant_id: rec_point_of_sale_terminal_var_softkeys_n6
  source_type: forked_anchor
  parent_record_id: rec_a-silver-handheld-wireless-point-of-sale-payment_...074f8840
  positioning: {product_archetype: dense 6 soft-key menu row, why_same_subcategory: same terminal, more soft keys}
  primary_axis: {slot: soft_key_row, diversity_axis: N, target_candidate: N=6}
  structural_delta:
    change: [re-parameterize MENU_KEYS_Y to 6 columns (widen strip if needed), loop-generate menu_key_0..5]
    keep_parts: [body, menu_strip, numeric grid, command keys, printer_cover/hinge, paper_roll/spindle, foot_0..3]
    joint_policy: preserve prismatic menu press; count only changes
    interface_policy: evenly spaced on menu_strip within deck
  multiplicity: {applies: true, target_n: 6, copied_object: menu keycap, placement_rule: even spacing across strip}
  companion_variations: {allowed_④⑤⑥: [menu key color], forbidden: [numeric grid, form, printer, joint types]}
  acceptance_focus: [exactly 6 loop-emitted menu keys within deck, each presses]
```

---

## Blocked / Excluded (no jobs emitted)
- **numeric keypad N-sweep** (e.g. N=9/N=15): blocked — payment dial pads are standardized at 12 (0-9 + two symbols); varying it is unfaithful, not a real product axis. record_only.
- **command-key count sweep**: blocked — red/yellow/green cancel/clear/enter is a fixed semantic triad, not homogeneous multiplicity.
- **no-printer / bare card-reader dongle (mPOS)**: blocked — removing display + keypad + printer drifts to the mobile-reader neighbor listed in must_not_become.
- **cash-register / drawer integration, self-checkout kiosk**: blocked — neighbor categories.
- **stylus/signature-pen tether**: excluded — minor ④ accessory, not a structural anchor.
```
