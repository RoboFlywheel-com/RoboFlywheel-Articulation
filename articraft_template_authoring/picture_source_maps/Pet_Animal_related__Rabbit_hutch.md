# Source Map — Pet_Animal related / Rabbit hutch

slug `rabbit_hutch` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_pet_animal_related__rabbit_hutch__001_png_0830d110919048908b3bdc3a6594964f` — picture/Pet_Animal related/Rabbit hutch/001.png
- `rec_pet_animal_related__rabbit_hutch__002_png_f70eb66ad04c43f49b8068585dd59cf3` — picture/Pet_Animal related/Rabbit hutch/002.png

## Variants generated this batch (5 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_rabbit_hutch_var_mechanism_slide_door` | mechanism_slide_door | PASS | 11 | 1 |
| `rec_rabbit_hutch_var_n1` | n1 | PASS | 7 | 2 |
| `rec_rabbit_hutch_var_n2` | n2 | PASS | 13 | 2 |
| `rec_rabbit_hutch_var_probe_cabinet_run` | probe_cabinet_run | PASS | 22 | 2 |
| `rec_rabbit_hutch_var_skeleton_aframe` | skeleton_aframe | PASS | 3 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Rabbit hutch — variant plan

slug `rabbit_hutch` · Category `Pet_Animal related` / Subcategory `Rabbit hutch`
pattern: **mixed** (parallel articulated children off one `hutch_frame` root: hinged doors + top-hinged lid + drop ramp + slide-out tray + rolling casters + revolute latch hasps; door-grid multiplicity)
richness band: **normal** · candidate anchors (origins + forked_anchor) = **17** · fork jobs emitted = **5** (4 forked_anchor + 1 compatibility_probe)

## subcategory_contract
```yaml
subcategory_contract:
  category: Pet_Animal related
  subcategory: Rabbit hutch
  core_identity: A raised outdoor housing for pet rabbits with one or more enclosed sleeping/shelter compartments, wire-mesh ventilated fronts, human access doors, and usually a wire run and/or slide-out cleaning tray.
  must_keep: [enclosed sheltered compartment(s), wire-mesh ventilation on at least one face, at least one human-access door or lid that opens, raised off ground on legs/casters, slide-out or removable cleaning tray when present]
  must_not_become: [dog kennel/crate, chicken coop / hen house, bird aviary, guinea-pig floor cage without shelter, garden storage cabinet, greenhouse/cold frame]
  image_evidence:
    - "001: compact grey-and-white two-compartment hutch — enclosed left box (upper acrylic-window door + lower mesh door), open wire run on the right, hinged roof lid over the run, fold-down front ramp, black slide-out tray, four swivel casters, internal ramp to an upper platform."
    - "002: large natural-pine 3x3 grid cabinet on short legs — nine hinged doors alternating solid plank / narrow-mesh / wide-mesh columns, each with a black barrel hinge + latch hasp, sloped overhanging plank roof, one full-width slide-out galvanized tray, no wheels."
  parent_evidence:
    - "A (001) hutch_frame + parts: upper_door(acrylic revolute), lower_door(mesh revolute), run_door(large mesh revolute), roof_lid(top-hinge revolute), front_ramp(drop-down revolute), floor_tray(prismatic), 4x caster_wheel_i(continuous); fixed internal_ramp_board + run_upper_platform; _front_mesh/_side_mesh wire-grid loop helpers; _door_frame helper."
    - "B (002) hutch_frame + loop over row_bottoms x columns(solid/mesh_narrow/mesh_wide) -> {kind}_door_{row} revolute + {name}_latch revolute hasp; cleaning_tray(prismatic); leg_ix_iy, front_stile_i, front_rail_i, compartment_floor_i; sloped_roof_panel; _mesh_door_geometry loop-emitted square mesh."
```

## Slot / candidate grid
Each supported slot reaches >=2 structurally distinct candidates.

| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| body_form / tier_topology | wheeled two-compartment hutch+run | ① | origin_anchor | A `hutch_frame` | converged |
| body_form / tier_topology | enclosed multi-tier grid cabinet | ① | origin_anchor | B `hutch_frame` grid | converged |
| body_form / tier_topology | triangular A-frame (ark) hutch | ③ | forked_anchor | rec_rabbit_hutch_var_skeleton_aframe (from A) | planned |
| mobility / base | four swivel casters (continuous) | ①② | origin_anchor | A `caster_wheel_i`, `fork_to_caster_wheel_i` | converged |
| mobility / base | fixed legs | ① | origin_anchor | B `leg_ix_iy` | converged |
| access_motion | side-hinged compartment door (revolute) | ② | origin_anchor | A `upper/lower/run_door`, B `{kind}_door_{row}` | converged |
| access_motion | top-hinged roof lid (revolute) | ② | origin_anchor | A `roof_lid`, `frame_to_roof_lid` | converged |
| access_motion | drop-down front ramp door (revolute) | ② | origin_anchor | A `front_ramp`, `frame_to_front_ramp` | converged |
| access_motion | slide-out cleaning tray (prismatic) | ② | origin_anchor | A `floor_tray`, B `cleaning_tray` | converged |
| access_motion | latch hasp bar (revolute) | ② | origin_anchor | B `{name}_latch`, `{name}_to_latch` | converged |
| access_motion | vertical slide guillotine pop-hole (prismatic door) | ② | forked_anchor | rec_rabbit_hutch_var_mechanism_slide_door (from A) | planned |
| run_attachment | integrated open wire run beside hutch | ① | origin_anchor | A run bay + `run_door` + `_side_mesh` | converged |
| run_attachment | no run — fully enclosed cabinet | ① | origin_anchor | B enclosed grid | converged |
| internal_structure | fixed internal ramp to upper platform | — | origin_anchor | A `internal_ramp_board`, `run_upper_platform` | converged (single candidate; see underfill note) |
| door_infill (surface) | solid plank / wire mesh / clear acrylic | ④ | record_only | A acrylic+mesh, B solid+mesh | not forked |
| multiplicity (n_tiers) | N=3 tier grid | N | origin_anchor | B `row_bottoms` (3) x columns | converged |
| multiplicity (n_tiers) | N=2 tier grid | N | forked_anchor | rec_rabbit_hutch_var_n2 (from B) | planned |
| multiplicity (n_tiers) | N=1 single-tier row | N | forked_anchor | rec_rabbit_hutch_var_n1 (from B) | planned |

Compatibility probe (not counted in budget): enclosed cabinet (B) + attached open wire run — `rec_rabbit_hutch_var_probe_cabinet_run`.

## Mandatory 6-axis diversity audit
| axis | candidate-anchor status | treatment | values |
|---|---|---|---|
| ① skeleton / topology | candidate-anchor | source-backed | wheeled hutch+run (A) / multi-tier grid cabinet (B) / A-frame ark (fork); + run-attachment integrated-run (A) vs no-run (B) |
| ② joint / mechanism | candidate-anchor | source-backed | revolute door (A,B), top-hinge lid (A), drop-ramp revolute (A), prismatic tray (A,B), revolute latch hasp (B), continuous casters (A); + prismatic vertical pop-hole (fork) |
| ③ primary form family | candidate-anchor | source-backed | rectangular post-and-rail box envelope (A,B) vs triangular A-frame envelope (fork) |
| ④ surface decoration | NOT anchor | record_only / world_knowledge_extrapolation | door infill solid plank / wire-mesh grid / clear acrylic window; plank-seam grain, face screws, latch plates; roof felt cap |
| ⑤ proportion / size / travel | NOT anchor | record_only (may ride companion) | compact ~1.2 m wheeled (A) vs ~1.9 m tall 3-tier (B); tray travel 0.32–0.34; door swing 0–1.35 rad; lid 0–1.2; ramp drop; pop-hole lift; tier count 1–4 |
| ⑥ material / palette | NOT anchor | record_only (may ride companion) | warm-white painted + grey trim (A) / natural warm pine + dark endgrain (B); galvanized vs black plastic tray; dark wire mesh; black latch hardware |

## Multiplicity / copy logic
- count_param: `n_tiers` (rows of the compartment-door grid; B loops `row_bottoms` x `columns`).
- copied object: one compartment cell = `{kind}_door_{row}` (revolute hinge) + `{name}_latch` (revolute hasp child); columns pattern fixed (solid / mesh_narrow / mesh_wide).
- N samples: N=3 (origin B) / N=2 (fork n2) / N=1 (fork n1).
- suggested N_range: tiers [1, 4]; columns [2, 4] (columns recorded, not swept — one N axis only).
- placement rule: vertical stack, row spacing = door_h + rail; regenerate `front_rail`/`compartment_floor`/wall/roof z-lines from n_tiers.
- joint policy: each copied door keeps its own `frame_to_{name}` revolute + `{name}_to_latch` revolute; loop-emitted, stable indexed names — no hand-written rows.
- secondary multiplicity (record_only, not forked): 4x casters (A, per-wheel continuous); mesh wires via `_front_mesh`/`_side_mesh` loops (decorative, not a template N).

## Budget decision
Normal band (12–18); coverage-first, no padding. 17 candidate anchors = 13 origin_anchor + 4 forked_anchor. All ①/②/③/N forks are source-backed (A-frame and pop-hole are world-knowledge form/mechanism forked onto parent functional layers; N samples driven by B's existing loop). ④/⑤/⑥ recorded only. 1 compatibility_probe not counted.

underfilled_reason: the `internal_structure` slot holds a single honest candidate (fixed internal ramp, A only) — no second structurally distinct internal member is credible without drifting into the run/ramp slots already covered, so it is left at 1 rather than padded.

## Variant cards
```yaml
- variant_id: rec_rabbit_hutch_var_skeleton_aframe
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__rabbit_hutch__001_png_0830d110919048908b3bdc3a6594964f
  positioning: {product_archetype: triangular A-frame rabbit ark, why_same_subcategory: enclosed nest box + wire run + access door + ramp, raised outdoor rabbit housing}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: triangular A-frame envelope}
  structural_delta:
    change: [ridge beam + two pitched side-plane frames + triangular gables replace box posts/rails, sloped mesh run faces, enclosed apex nest box, sloped-face run door]
    keep_parts: [hutch_frame, front_ramp, frame_to_front_ramp, run_door, frame_to_run_door, floor_tray, frame_to_floor_tray, _front_mesh, _side_mesh]
    joint_policy: preserve revolute run door + drop ramp + prismatic tray; no new mechanism type
    interface_policy: nest box floor meets ramp hinge; sloped faces host mesh; tray under nest box
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [ridge height/pitch, timber vs painted palette], forbidden: [add wheels, change door mechanism, fully enclose the run]}
  acceptance_focus: [A-frame reads as ark not box, run door swings clear, ramp drops to ground, tray slides out]

- variant_id: rec_rabbit_hutch_var_mechanism_slide_door
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__rabbit_hutch__001_png_0830d110919048908b3bdc3a6594964f
  positioning: {product_archetype: guillotine pop-hole slide door between hutch and run, why_same_subcategory: standard multi-compartment hutch pass-through feature}
  primary_axis: {slot: access_motion, diversity_axis: ②, target_candidate: vertical prismatic slide door}
  structural_delta:
    change: [pop-hole opening in divider_mesh, plank/acrylic slide panel, two vertical guide rails, PRISMATIC +Z joint, pull knob]
    keep_parts: [hutch_frame, divider_mesh, run_upper_platform, upper_door, lower_door, frame_to_upper_door, floor_tray, caster_wheel_i]
    joint_policy: add exactly one new prismatic slide door; keep all existing revolute/prismatic/continuous joints
    interface_policy: panel captured between guide rails, travel bracketed so it never floats
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [acrylic vs plank panel, pop-hole size/lift travel], forbidden: [exterior barn slider, add compartment/wheels, change body topology]}
  acceptance_focus: [prismatic panel lifts along +Z, guide rails visible, pop-hole aligns hutch<->run]

- variant_id: rec_rabbit_hutch_var_n2
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__rabbit_hutch__002_png_f70eb66ad04c43f49b8068585dd59cf3
  positioning: {product_archetype: two-tier stacked wooden hutch (2x3 grid), why_same_subcategory: same enclosed multi-compartment hutch, fewer rows}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_tiers=2}
  structural_delta:
    change: [n_tiers=2 drives row_bottoms/front_rail/compartment_floor/wall/roof z-lines, 6 doors emitted]
    keep_parts: [hutch_frame, columns tuple, solid_door/mesh_narrow_door/mesh_wide_door, "{name}_latch", "frame_to_{name}", "{name}_to_latch", cleaning_tray, front_rail_i, front_stile_i, compartment_floor_i, leg_ix_iy]
    joint_policy: each copied door keeps revolute hinge + child latch; loop-emitted
    interface_policy: vertical stack spacing = door_h + rail; column pattern unchanged
  multiplicity: {applies: true, target_n: 2, copied_object: "{kind}_door_{row} + {name}_latch", placement_rule: vertical grid rows}
  companion_variations: {allowed_④⑤⑥: [shorter body height], forbidden: [wheels/run, change door mechanism or column count, hand-written rows]}
  acceptance_focus: [exactly 6 doors from loop, indexed names, per-door hinge+latch, tray still slides]

- variant_id: rec_rabbit_hutch_var_n1
  source_type: forked_anchor
  parent_record_id: rec_pet_animal_related__rabbit_hutch__002_png_f70eb66ad04c43f49b8068585dd59cf3
  positioning: {product_archetype: single-story wooden hutch on legs (1x3 row), why_same_subcategory: same enclosed multi-compartment hutch, one row}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_tiers=1}
  structural_delta:
    change: [n_tiers=1 drives row_bottoms/rails/floors/wall/roof/leg height, 3 doors emitted, single tier raised on legs]
    keep_parts: [hutch_frame, columns tuple, solid_door/mesh_narrow_door/mesh_wide_door, "{name}_latch", "frame_to_{name}", "{name}_to_latch", cleaning_tray, front_rail_i, front_stile_i, compartment_floor_i, leg_ix_iy]
    joint_policy: 3 column doors each revolute + child latch; loop-emitted
    interface_policy: single tier on legs, tray beneath
  multiplicity: {applies: true, target_n: 1, copied_object: "{kind}_door_{row} + {name}_latch", placement_rule: single row of 3 columns}
  companion_variations: {allowed_④⑤⑥: [taller legs for stance], forbidden: [wheels/run, change door mechanism or column count, hand-written row]}
  acceptance_focus: [exactly 3 doors row=0, per-door hinge+latch, tray slides, single-tier stance credible]

- variant_id: rec_rabbit_hutch_var_probe_cabinet_run
  source_type: compatibility_probe
  parent_record_id: rec_pet_animal_related__rabbit_hutch__002_png_f70eb66ad04c43f49b8068585dd59cf3
  positioning: {product_archetype: enclosed hutch cabinet with attached exercise run, why_same_subcategory: enclosed sleeping compartments + wire run + access + tray}
  primary_axis: {slot: run_attachment, diversity_axis: compatibility_probe, target_candidate: enclosed cabinet + integrated open run}
  structural_delta:
    change: [side open post-and-rail run bay clad in loop-emitted mesh, hinged mesh run door, pop-hole + short ramp interface from lowest compartment to run floor]
    keep_parts: [hutch_frame, solid_door, mesh_wide_door, "frame_to_{name}", "{name}_latch", cleaning_tray, leg_ix_iy, sloped_roof_panel]
    joint_policy: add one revolute run door; keep cabinet doors/latches/tray
    interface_policy: shared leg/base line, side-wall pop-hole meets run floor, run door swing clears cabinet corner
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [run size, mesh spacing], forbidden: [open-pen only, change tier count or cabinet door mechanisms]}
  acceptance_focus: [enclosed cabinet + run both read as one hutch, no clearance collision at side interface, run door clears corner]
```

## Blocked / excluded
- door-infill (solid / mesh / acrylic) as standalone variants: excluded — ④ surface only, all values already origin-backed; recorded, not forked.
- flat-roof vs gable-roof as a variant: excluded — ⑤ roof-shape, both already origin-backed (A flat, B sloped).
- n_tiers=4: excluded — beyond realistic rabbit-hutch height; N{1,2,3} already exposes copy logic.
- column-count N-sweep: excluded — one multiplicity axis (n_tiers) is enough; column count recorded as N_range only.
