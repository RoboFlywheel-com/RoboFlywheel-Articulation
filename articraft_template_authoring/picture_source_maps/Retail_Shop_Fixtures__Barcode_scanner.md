# Source Map — Retail_Shop Fixtures / Barcode scanner

slug `barcode_scanner` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_handheld-pistol-grip-barcode-scanner-black-plast_20260708_082438_119506_b32f70d1` — picture/Retail_Shop Fixtures/Barcode scanner/002.png
- `rec_wireless-handheld-barcode-scanner-pistol-grip-st_20260708_082427_891584_6c8ecc24` — picture/Retail_Shop Fixtures/Barcode scanner/001.png

## Variants generated this batch (5 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_barcode_scanner_var_base_cradle` | base_cradle | PASS | 1 | 1 |
| `rec_barcode_scanner_var_mechanism_button` | mechanism_button | PASS | 2 | 1 |
| `rec_barcode_scanner_var_probe_fixedmount_tilt` | probe_fixedmount_tilt | PASS | 1 | 1 |
| `rec_barcode_scanner_var_skeleton_presentation` | skeleton_presentation | PASS | 1 | 1 |
| `rec_barcode_scanner_var_skeleton_wand` | skeleton_wand | PASS | 1 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Retail_Shop Fixtures / Barcode scanner

slug `barcode_scanner` · richness band **simple** · pattern **linear_chain** (single `scanner_body` root + one articulated trigger child; optional static support/base module)

## 1. Subcategory Contract
```yaml
subcategory_contract:
  category: Retail_Shop Fixtures
  subcategory: Barcode scanner
  core_identity: a handheld/countertop optical barcode reader with a scan head carrying a recessed scan window (laser line or area imager) and a user-actuated scan control
  must_keep:
    - a scan head with a recessed dark scan window aimed forward
    - a visible scan cue (red laser line or imager aperture)
    - at least one real user control mechanism (squeeze trigger revolute, or a scan/pair button)
    - a defined support: freestanding grip base, weighted stand, dock cradle, or mount foot
  must_not_become:
    - POS terminal / cash register / checkout stand
    - weighing scale, label printer, or receipt printer
    - stylus/pen, flashlight, security camera, or generic sensor housing
  image_evidence:
    - "002.png: black gun-style pistol grip, wide rounded scan head, recessed dark window with red laser line, blue rubber squeeze trigger on front of raked grip, white spec label under head, coiled corded cable from grip base"
    - "001.png: charcoal + orange wireless pistol grip, flat scan head with recessed area-imager window in orange bezel, orange top panel with blue illuminated ring button, orange rubber grip inserts, hanging squeeze trigger, separate USB dongle accessory (cordless)"
  parent_evidence:
    - "A (corded): parts scanner_body{grip_shell, scan_head, scan_window, laser_line, spec_label, cable_coil} + trigger{trigger_pad}; grip_to_trigger REVOLUTE squeeze; grip loft of elliptical sections; head tilted, front pocket recess"
    - "B (wireless): parts scanner_body{grip_shell, grip_insert_wrap, head_shell, window_bezel, scan_window, top_panel, ring_light, ring_button} + trigger{trigger_blade}; trigger_pivot REVOLUTE; head loft, pitched; recessed 2D imager window in orange bezel; static top ring button"
```

## 2. Slot / Candidate Grid
| slot | candidate | axis | source_type | evidence / record |
|---|---|---|---|---|
| body_form / skeleton | pistol_grip_handheld | ① | origin_anchor | A, B |
| body_form / skeleton | presentation_tower (upright neck + weighted base, hands-free) | ① | forked_anchor | var_skeleton_presentation (fork B) |
| body_form / skeleton | inline_wand (single straight barrel, nose window) | ① | forked_anchor | var_skeleton_wand (fork A) |
| body_form / skeleton | fixed_mount_box | ①(+②) | compatibility_probe | var_probe_fixedmount_tilt (fork A) |
| body_form / skeleton | wearable_ring (finger scanner) | ① | blocked | thin/borderline drift |
| support_or_base | grip_base_freestanding | ① | origin_anchor | A, B (flared grip base) |
| support_or_base | charging_cradle_dock (scanner seated in dock) | ① | forked_anchor | var_base_cradle (fork B) |
| support_or_base | weighted_stand_base | ① | forked_anchor | ridealong of presentation_tower |
| support_or_base | mount_foot_bracket | probe | compatibility_probe | ridealong of fixedmount probe |
| opening_or_motion / mechanism | squeeze_trigger_revolute | ② | origin_anchor | A (grip_to_trigger), B (trigger_pivot) |
| opening_or_motion / mechanism | top_scan_button_prismatic | ② | forked_anchor | var_mechanism_button (fork B) |
| opening_or_motion / mechanism | bracket_tilt_revolute | ② | compatibility_probe | var_probe_fixedmount_tilt |
| scan_window / imager | laser_line_1D | ④ | record_only | A |
| scan_window / imager | area_imager_2D | ④ | record_only | B |
| cable / interface | coiled_corded | ④/⑤ | record_only | A (cable_coil) |
| cable / interface | wireless_no_cable (+ USB dongle) | ④ | record_only | B |

Supported structural slots each reach ≥2 distinct candidates: body_form (3 anchored forms + probe), support_or_base (grip base / cradle / stand), mechanism (trigger revolute / button prismatic).

## 3. Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | pistol_grip(A,B); presentation_tower(fork); inline_wand(fork); charging_cradle support(fork); fixed_mount_box(probe) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | squeeze_trigger REVOLUTE(A,B); top_scan_button PRISMATIC(fork); bracket_tilt REVOLUTE(probe) |
| ③ primary form family | source-backed | volumetric envelope head + grip loft (origins); tower/base envelope; straight-barrel envelope; box envelope — all covered by the ① skeleton forks, no separate ③-only fork needed |
| ④ surface decoration | record_only | scan window type: laser line (A) vs 2D area imager in bezel (B); spec label; illuminated ring; grip rubber inserts; "Do Not Stare Into Beam" print — host-conformal only |
| ⑤ proportion / size / travel | record_only | handheld ~0.20 m tall; trigger squeeze 0.22–0.30 rad; head tilt ~0.20–0.30 rad; button prismatic ~2–3 mm; no standalone scale fork |
| ⑥ material / palette / finish | record_only | black plastic + blue trigger (A); charcoal + orange rubber + blue ring (B); template palette: black, charcoal, safety-orange, retail white/gray — no standalone palette fork |

## 4. Multiplicity / Copy Logic
No strong repeated-homogeneous-part axis in this subcategory. The trigger, scan window, and scan button are singletons; buttons do not appear in a regular loop-copied cluster in either origin. `underfilled_reason` (multiplicity): barcode scanners expose no source-backed repeated-part family (no louvers/keys/ribs/shelves); a multi-key programming pad is thin and not shown by either origin, so no N samples are planned.

## 5. Budget Decision
- Band: **simple (8–12)**. Counted candidate anchors (origins + converged forks) = **6** (2 origins + 4 forked_anchor). Probes/④⑤⑥ not counted.
- `underfilled_reason`: A barcode scanner is a structurally simple handheld electronic tool. Honest structural vocabulary is limited to a few skeleton families (pistol-grip, presentation tower, inline wand) plus a dock/base support, one dominant mechanism (squeeze-trigger revolute), and one alternate control (top prismatic button). Fixed-mount and wearable-ring forms are borderline/risky and are captured as a `compatibility_probe` / `blocked` respectively rather than padded in. Padding via laser-vs-imager window (④), corded-vs-wireless interface (④), color (⑥) or size (⑤) is disallowed by §6–§8, so the pool sits just under the simple band's 8 by design (coverage first, no padding).

## 6. Variant Cards

```yaml
variant_card:
  variant_id: rec_barcode_scanner_var_skeleton_presentation
  source_type: forked_anchor
  parent_record_id: rec_wireless-handheld-barcode-scanner-pistol-grip-st (B)
  positioning: {product_archetype: countertop hands-free presentation scanner, why_same_subcategory: keeps imager head + recessed window + squeeze trigger; only lower support skeleton changes}
  primary_axis: {slot: body_form, diversity_axis: ①, target_candidate: presentation_tower_on_weighted_base}
  structural_delta:
    change: [grip loft -> vertical neck column lofted into wide flat weighted base plate; head kept on top pitched to aim at presented items]
    keep_parts: [scanner_body, head_shell, window_bezel, scan_window, top_panel, ring_light, ring_button, trigger, trigger_blade, trigger_pivot]
    joint_policy: preserve trigger_pivot revolute only
    interface_policy: base bottom face flat on ground (z=0) as new support interface
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [neutral base palette], forbidden: [category drift to POS/scale, trigger joint change, imager change]}
  acceptance_focus: [freestanding base non-floating, head aims forward/down, trigger still swings clear]
```
```yaml
variant_card:
  variant_id: rec_barcode_scanner_var_skeleton_wand
  source_type: forked_anchor
  parent_record_id: rec_handheld-pistol-grip-barcode-scanner-black-plast (A)
  positioning: {product_archetype: inline CCD / linear-imager wand scanner, why_same_subcategory: keeps scan window + red laser + trigger; body collapses to one straight barrel}
  primary_axis: {slot: body_form, diversity_axis: ①, target_candidate: inline_straight_barrel}
  structural_delta:
    change: [scan_head + raked grip -> single slim rounded-rect/cylindrical barrel; window+laser to front nose; grip = rear of same barrel]
    keep_parts: [scanner_body, scan_window, laser_line, spec_label, cable_coil, trigger, trigger_pad, grip_to_trigger]
    joint_policy: preserve grip_to_trigger revolute as a small side/thumb trigger
    interface_policy: cable exits rear end cap
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [single-color barrel], forbidden: [drift to pen/flashlight, trigger joint change, remove window/laser]}
  acceptance_focus: [single-mass barrel silhouette, window/laser on nose, trigger revolute preserved]
```
```yaml
variant_card:
  variant_id: rec_barcode_scanner_var_base_cradle
  source_type: forked_anchor
  parent_record_id: rec_wireless-handheld-barcode-scanner-pistol-grip-st (B)
  positioning: {product_archetype: cordless scanner docked in charging/presentation cradle, why_same_subcategory: handheld scanner unchanged; adds a dock support module}
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: charging_cradle_dock}
  structural_delta:
    change: [add static cradle_base part = weighted foot + upright saddle/cup cradling grip front and head nose; scanner rests nose-up in dock]
    keep_parts: [scanner_body, grip_shell, grip_insert_wrap, head_shell, window_bezel, scan_window, top_panel, ring_light, ring_button, trigger, trigger_blade, trigger_pivot]
    joint_policy: preserve trigger_pivot revolute; cradle static
    interface_policy: cradle foot bottom = ground; grip seats against saddle (local allowed overlap)
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [neutral cradle color], forbidden: [drift to phone dock/lamp, scanner joint/imager change]}
  acceptance_focus: [scanner seats stably in cradle, cradle non-floating, scanner joint intact]
```
```yaml
variant_card:
  variant_id: rec_barcode_scanner_var_mechanism_button
  source_type: forked_anchor
  parent_record_id: rec_wireless-handheld-barcode-scanner-pistol-grip-st (B)
  positioning: {product_archetype: pistol-grip scanner with pressable top scan/pair button, why_same_subcategory: same grip/head/imager/trigger; adds one real second mechanism}
  primary_axis: {slot: opening_or_motion, diversity_axis: ②, target_candidate: top_scan_button_prismatic}
  structural_delta:
    change: [split top ring_button disc into own part on a PRISMATIC joint (~2-3 mm travel) into a recessed well in top_panel; ring_light stays as fixed bezel]
    keep_parts: [scanner_body, grip_shell, grip_insert_wrap, head_shell, window_bezel, scan_window, top_panel, trigger, trigger_blade, trigger_pivot]
    joint_policy: add exactly one prismatic mechanism; keep trigger revolute unchanged
    interface_policy: button rides in a shallow top_panel well
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [button cap color], forbidden: [skeleton change, trigger joint change, extra buttons]}
  acceptance_focus: [button travels vertically in well, both trigger revolute and button prismatic present, no floating cap]
```
```yaml
variant_card:
  variant_id: rec_barcode_scanner_var_probe_fixedmount_tilt
  source_type: compatibility_probe
  parent_record_id: rec_handheld-pistol-grip-barcode-scanner-black-plast (A)
  positioning: {product_archetype: fixed-mount industrial scanner on adjustable tilt bracket, why_same_subcategory: keeps scan window + laser aimed forward; probe bundles box skeleton + bracket joint}
  primary_axis: {slot: body_form+opening_or_motion, diversity_axis: compatibility_probe, target_candidate: fixed_mount_box + bracket_tilt_revolute}
  structural_delta:
    change: [grip+head -> compact box housing window+laser on front; add two-arm bracket on foot; bracket_hinge REVOLUTE replaces grip_to_trigger]
    keep_parts: [scanner_body, scan_window, laser_line, spec_label, cable_coil]
    joint_policy: replace trigger revolute with a single bracket-tilt revolute
    interface_policy: foot bottom = ground; box tilts on bracket
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [industrial gray], forbidden: [drift to camera/floodlight, adding pistol grip or trigger]}
  acceptance_focus: [box clears bracket arms through tilt travel, assembly stable/non-floating, exactly one non-fixed joint]
```

## 7. Blocked / Excluded
- `wearable_ring` (finger-worn scanner): borderline miniature form with thin structural vocabulary and real risk of drifting toward "wearable device"; excluded rather than forked.
- `bioptic_in_counter` grocery scanner: too large / built-in-fixture, out of the handheld/countertop scope of the origins.
- ④ laser-vs-imager, ④/⑤ corded-vs-wireless, ⑥ palette, ⑤ size: recorded only, never standalone variants.

## Emitted Jobs
5 fork jobs (4 counted forked_anchor + 1 compatibility_probe). Manifest: `/tmp/jobs/barcode_scanner.jobs.txt`. Axis files: `/tmp/axis/barcode_scanner_var_*.txt`.
