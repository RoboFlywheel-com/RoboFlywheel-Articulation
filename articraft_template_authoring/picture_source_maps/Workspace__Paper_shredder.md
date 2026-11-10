# Source Map — Workspace / Paper shredder

slug `paper_shredder` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__paper_shredder__002_png_4cfd02243bfe466d982a6f4f86962dd4` — picture/Workspace/Paper shredder/002.png
- `rec_workspace__paper_shredder__001_png_5c69ea488a624fe097dc271bc6ea56a0` — picture/Workspace/Paper shredder/001.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_paper_shredder_var_autofeed_lid` | autofeed_lid | PASS | 10 | 1 |
| `rec_paper_shredder_var_controls_n5` | controls_n5 | PASS | 11 | 1 |
| `rec_paper_shredder_var_cutter_shafts` | cutter_shafts | PASS | 10 | 1 |
| `rec_paper_shredder_var_desk_feet` | desk_feet | PASS | 4 | 0 |
| `rec_paper_shredder_var_door` | door | PASS | 9 | 1 |
| `rec_paper_shredder_var_probe_round_liftoff` | probe_round_liftoff | PASS | 4 | 0 |
| `rec_paper_shredder_var_round_bin` | round_bin | PASS | 8 | 1 |
| `rec_paper_shredder_var_tilt_head` | tilt_head | PASS | 10 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Workspace / Paper shredder — variant plan

slug `paper_shredder` · pattern **mixed** (single cabinet/body root; prismatic pull-out bin + press-buttons + slide switch + 4 continuous casters; button multiplicity loop).

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Paper shredder
  core_identity: A powered cutting head with a feed slot mounted over a shred receptacle; paper enters the top slot and shreds collect in a bin below.
  must_keep: [top shredder head with feed slot + cutter throat, a shred receptacle/bin, at least one real access or control articulation]
  must_not_become: [filing cabinet, storage cabinet, kitchen trash can / open bin without cutter head, printer/scanner/copier, pasta roller / wringer / mangle]
  image_evidence:
    - Boxy black plastic cabinet, wider rounded shredder head overhanging the bin (001, 002).
    - Long narrow top feed slot with an icon/control strip and small buttons + slider (002); silver top plate + control cluster (001).
    - Pull-out front waste basket partially withdrawn, with a smoked viewing window and a front grip (both).
    - Loose shredded paper filling the basket (both); side smoked window on the shell (001).
    - Four swivel-style caster wheels at the base corners (both).
  parent_evidence:
    - Root part shell/body; PRISMATIC pull-out basket (shell_to_basket / body_to_basket).
    - Feed slot, control panel/recess, front badge, indicator dots as top surface features.
    - PRISMATIC push buttons (loop N=2 in 002, N=3 in 001) + PRISMATIC slide switch (control_switch / mode_switch).
    - 4 CONTINUOUS caster wheels (shell_to_caster_i / body_to_caster_wheel_i).
    - 002 exposes static cutter_roller_0/1 visuals under the throat; 001 adds a connected paper_fill mesh.
```

## Slots and candidates
| slot | candidate | axis | source_type | evidence |
|---|---|---|---|---|
| **opening_or_access** | pull_out_basket drawer (prismatic) | ② | origin_anchor | 001, 002 (`*_to_basket`) |
| | hinged front cabinet door (revolute z) | ② | forked_anchor | rec_paper_shredder_var_door |
| | tilt-up / lift-off head (revolute x) | ② | forked_anchor | rec_paper_shredder_var_tilt_head |
| **feed_mechanism** | open manual feed slot | ② | origin_anchor | 001, 002 (`feed_slot`) |
| | hinged auto-feed top lid (revolute x) | ② | forked_anchor | rec_paper_shredder_var_autofeed_lid |
| **body_form** | rectangular boxy cabinet | ③ | origin_anchor | 001, 002 |
| | cylindrical rounded drum bin | ③ | forked_anchor | rec_paper_shredder_var_round_bin |
| **cutting_mechanism** | static cutter rollers (visual) | ② | record_only/origin | 002 (`cutter_roller_0/1`) |
| | counter-rotating cutter shafts (2× continuous) | ② | forked_anchor | rec_paper_shredder_var_cutter_shafts |
| **support_or_base** | four continuous caster wheels | ① | origin_anchor | 001, 002 |
| | fixed desktop rubber feet | ① | forked_anchor | rec_paper_shredder_var_desk_feet |
| **multiplicity (buttons)** | N=2 buttons | N | origin_anchor | 002 |
| | N=3 buttons | N | origin_anchor | 001 |
| | N=5 control array | N | forked_anchor | rec_paper_shredder_var_controls_n5 |

Every supported slot reaches ≥2 structurally distinct candidates.

## Six-Axis Diversity Audit
| axis | treatment | values / range |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | support base: 4-caster rolling vs fixed desktop feet; cabinet-drawer vs door vs lift-off-head access topology |
| ② joint / mechanism | source-backed (origin + forked_anchor) | prismatic drawer, prismatic buttons, prismatic slide switch, continuous casters (origins); + revolute door, revolute tilt head, revolute auto-feed lid, paired continuous cutter shafts (forks) |
| ③ primary form family | source-backed (origin + forked_anchor) | rectangular boxy volumetric cabinet (origins) vs cylindrical drum bin (fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | badge/oval logo, icon strip + indicator dots, cross-cut vs strip-cut throat pattern, control-panel iconography, smoked side/front windows — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only (companion only) | basket travel lower/upper ~[-0.07,0.13]; button press ~0.004; switch ~±0.011–0.022; caster continuous; head/drum footprint scale — may ride along on round_bin / desk_feet |
| ⑥ material / palette / finish | record_only (companion only) | matte/charcoal/gloss black plastic, brushed-silver top plate, smoked translucent window, black rubber casters/feet, pale indicator marks — never standalone |

## Multiplicity / Copy Logic
- count_param: number of top push buttons (`button_i`, prismatic `*_to_button_i`).
- N samples: N=2 (origin 002), N=3 (origin 001), N=5 (fork controls_n5).
- suggested N_range: [1, 6].
- copied object: single `button` part with a `button_cap` cylinder; naming `button_0..N`; placement linear even spacing along `control_panel` x; joint policy one prismatic press joint per button (axis -z, shared limits).
- casters are fixed at N=4 in both origins (no sweep); button count is the honest multiplicity axis.

## Budget decision
- Richness band: **simple (8–12)**. Candidate anchors total = **9** (2 origins + 7 forked_anchors).
- compatibility_probe (not counted): 1 (round bin + lift-off head).
- Coverage first, no padding: paper shredders have a moderate but bounded structural vocabulary; 9 honest anchors cover all supported slots ≥2. No ④/⑤/⑥-only variants emitted.

## Variant cards
```yaml
- variant_id: rec_paper_shredder_var_door
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__001 (body/lower_shell cavity is cleanest)
  positioning: {product_archetype: office console shredder w/ swing door, why_same_subcategory: head+feed slot+cutter retained}
  primary_axis: {slot: opening_or_access, diversity_axis: ②, target_candidate: hinged front door}
  structural_delta:
    change: [replace body_to_basket prismatic with revolute body_to_door on z jamb; new door part w/ front_window + pull_handle_recess]
    keep_parts: [body, lower_shell, top_panel, feed_slot, control_panel, guide_0/1, basket, caster_wheel_0..3]
    joint_policy: replace one primary mechanism (prismatic drawer -> revolute door)
    interface_policy: front-jamb hinge barrel pivot; interior basket becomes fixed bin
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [filing cabinet, body-form/support/control changes]}
  acceptance_focus: [door swings ~100° clearing head; bin behind stays retained]

- variant_id: rec_paper_shredder_var_tilt_head
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__001
  positioning: {product_archetype: consumer shredder w/ tilt-up head, why_same_subcategory: cutter head + feed slot retained}
  primary_axis: {slot: opening_or_access, diversity_axis: ②, target_candidate: rear-hinged lift-up head}
  structural_delta:
    change: [split head out of _body_shell into head part; add revolute body_to_head at rear (x)]
    keep_parts: [body, lower_shell, feed_slot, top_panel, control_panel, basket, runner_0/1, guide_0/1, caster_wheel_0..3]
    joint_policy: add one revolute head hinge; keep prismatic basket
    interface_policy: rear hinge barrel; lower-shell top rim is seat
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [open bin without cutter, body-form/support changes]}
  acceptance_focus: [head pivots 0–80° w/o collision; bin still slides]

- variant_id: rec_paper_shredder_var_autofeed_lid
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__001
  positioning: {product_archetype: auto-feed shredder w/ hinged stack lid, why_same_subcategory: same cutter/bin path}
  primary_axis: {slot: feed_mechanism, diversity_axis: ②, target_candidate: hinged auto-feed top lid}
  structural_delta:
    change: [add feed housing + feed_lid part; revolute body_to_feed_lid at rear (x); stack_tray recess over feed_slot]
    keep_parts: [body, lower_shell, top_panel, feed_slot, control_panel, basket, runner_0/1, guide_0/1, caster_wheel_0..3, mode_switch]
    joint_policy: add one revolute lid; keep prismatic basket/buttons
    interface_policy: head-rim hinge barrel
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [printer/scanner lid, body-form/support/drawer changes]}
  acceptance_focus: [lid opens 0–95° revealing tray; feed slot below preserved]

- variant_id: rec_paper_shredder_var_round_bin
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__002
  positioning: {product_archetype: rounded drum-bin shredder, why_same_subcategory: same head/feed/cutter on curved bin}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: cylindrical drum envelope}
  structural_delta:
    change: [replace box side/rear/plinth frame with cylindrical curved-wall shell; curved-front basket segment]
    keep_parts: [shell, top_head, feed_slot, shredder_throat, cutter_roller_0/1, basket, front_panel, view_window, caster_0..3, button_0/1, control_switch, shell_to_basket]
    joint_policy: preserve prismatic basket + continuous casters
    interface_policy: curved top rim seats head; casters under round base
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [drum diameter proportion (⑤)], forbidden: [kitchen bin, opening/support/cutter changes]}
  acceptance_focus: [head seats on curved rim; drawer still slides on curved front]

- variant_id: rec_paper_shredder_var_desk_feet
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__002
  positioning: {product_archetype: compact personal desktop shredder, why_same_subcategory: head+feed+bin retained, controls stay live}
  primary_axis: {slot: support_or_base, diversity_axis: ①, target_candidate: fixed rubber feet}
  structural_delta:
    change: [remove caster yokes + continuous shell_to_caster joints; add 4 fixed foot pads under bottom_plinth]
    keep_parts: [shell, top_head, feed_slot, shredder_throat, cutter_roller_0/1, basket, front_panel, button_0/1, control_switch, shell_to_basket]
    joint_policy: remove caster joints; keep prismatic basket + buttons (real non-fixed joints remain)
    interface_policy: plinth underside mounts feet
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [smaller footprint (⑤)], forbidden: [countertop bin, body-form/opening/cutter changes, removing all articulation]}
  acceptance_focus: [no floating casters; basket + buttons still articulate]

- variant_id: rec_paper_shredder_var_cutter_shafts
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__002
  positioning: {product_archetype: shredder w/ exposed rotating cutter cylinders, why_same_subcategory: cutter is the defining shredder mechanism}
  primary_axis: {slot: cutting_mechanism, diversity_axis: ②, target_candidate: paired counter-rotating continuous shafts}
  structural_delta:
    change: [promote cutter_roller_0/1 to cutter_shaft_0/1 parts; 2 continuous shell_to_cutter_shaft joints (x, counter-rotating)]
    keep_parts: [shell, top_head, shredder_throat, feed_slot, basket, caster_0..3, button_0/1, control_switch, shell_to_basket]
    joint_policy: add two continuous shaft joints; keep prismatic basket
    interface_policy: throat side walls bear the shafts
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [pasta roller/wringer/mangle, body-form/support/drawer changes]}
  acceptance_focus: [two shafts spin about x; captured in throat, not floating]

- variant_id: rec_paper_shredder_var_controls_n5
  source_type: forked_anchor
  parent_record_id: rec_workspace__paper_shredder__001
  positioning: {product_archetype: office console w/ fuller control panel, why_same_subcategory: only control count differs}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: N=5 buttons}
  structural_delta:
    change: [extend button loop 3 -> 5 (button_0..4), prismatic press each]
    keep_parts: [body, lower_shell, top_panel, control_panel, basket, guide_0/1, caster_wheel_0..3, mode_switch, body_to_basket]
    joint_policy: copy parent prismatic button joint per instance
    interface_policy: linear even spacing along control_panel x
  multiplicity: {applies: true, target_n: 5, copied_object: button (button_cap), placement_rule: linear-even}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [body/opening/support/cutter changes, non-button filler controls]}
  acceptance_focus: [5 buttons evenly spaced; each depresses; loop-emitted]

- variant_id: rec_paper_shredder_var_probe_round_liftoff  # compatibility_probe (not counted)
  source_type: compatibility_probe
  parent_record_id: rec_workspace__paper_shredder__002
  positioning: {product_archetype: personal round-bin shredder w/ lift-off head, why_same_subcategory: classic small-office shredder form}
  primary_axis: {slot: body_form + opening_or_access, diversity_axis: probe, target_candidate: round bin (③) + lift-off head (②)}
  structural_delta:
    change: [round volumetric bin + separate head on revolute/lift clamp to round rim; open bin replaces drawer]
    keep_parts: [shell, top_head, feed_slot, shredder_throat, cutter_roller_0/1, button_0/1, control_switch]
    joint_policy: revolute/lift head-to-bin clamp
    interface_policy: round rim ring is the mating clamp face
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [casters, pull-out drawer, bin without cutter]}
  acceptance_focus: [curved rim mates lift-off head w/o gap/collision at seam]
```

## Compatibility Probes
| probe | record_id | combined axes | risk tested |
|---|---|---|---|
| round bin + lift-off head | rec_paper_shredder_var_probe_round_liftoff | ③ cylindrical + ② lift-off head | curved rim ↔ head hinge/clamp seating; gap/collision at round seam |

## Blocked / Excluded
- caster N-sweep: excluded — both origins fixed at N=4; not a meaningful multiplicity range.
- strip-cut vs cross-cut throat, badge/logo, icon strip: ④ surface only — record_only, no dedicated variant.
- CD/credit-card secondary feed slot: thin/borderline second-slot multiplicity — excluded to avoid padding.
- wall-mount / under-desk chassis: unsupported by origins and drifts toward built-in furniture — not forked.
```

## Origins (full reconciliation, 2/2)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_workspace__paper_shredder__002_png_4cfd02243bfe466d982a6f4f86962dd4` | 002 | boxy cabinet, open-front basket bay, 2 buttons + slide switch, visible cutter rollers, 4 casters | body_form=rect / opening=drawer / support=4caster / N=2 / cutter_rollers shown |
| B `rec_workspace__paper_shredder__001_png_5c69ea488a624fe097dc271bc6ea56a0` | 001 | boxy shell w/ cut cavity + guide rails, silver top plate, 3 buttons + mode switch, paper_fill, 4 caster wheels | body_form=rect / opening=drawer / support=4caster / N=3 |
