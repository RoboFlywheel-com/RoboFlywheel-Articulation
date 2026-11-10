# Modular Template Spec: multisegment_foldout_arm

## Review Header

- category_slug: `multisegment_foldout_arm`
- dataset_path: `data`
- mode: `SPEC_ONLY`
- reviewer_status: `approved`
- five_star_sample_count: 33
- required_files_read: `model.py`, `revision.json`, `record.json`, `prompt.txt`, `collections/dataset.json`
- template_scope: fold-out articulated arms with three or more serial segments, visible hinges, and a terminal carried by the final segment.

## Core Identity

A valid `multisegment_foldout_arm` is a compact arm that unfolds through a serial chain of revolute hinge stations. It must include a grounded base or bracket, multiple arm segments that nest or fold over one another, and a terminal module at the end. The category identity is the deployable multi-segment fold-out topology: repeated hinged links, stowed/deployed motion, and visible pivot hardware.

Required invariants:

- A grounded base supports the first hinge.
- At least three moving serial fold-out segments or two moving segments plus a functional terminal bracket; richer samples use four or five moving serial elements.
- Main fold-out joints are revolute.
- Hinges must be visible as eyes, clevises, barrels, side plates, pins, bushings, or trunnions.
- A deployed pose extends the terminal away from the base.
- A folded pose must remain coherent and not erase the arm identity.

## Slot Graph

```text
S0 base_anchor
  -> S1 axis_family
      -> S2 segment_count
          -> S3 segment_profile[i]
              -> S4 hinge_interface[i]
                  -> S5 terminal_module
  -> S6 auxiliary_fold_lock

Main chain:
base_anchor --REVOLUTE--> segment_0 --REVOLUTE--> segment_1
  --REVOLUTE--> segment_2 [--REVOLUTE--> segment_3 ...] --REVOLUTE--> terminal

Optional aux:
base_anchor --REVOLUTE/FIXED--> toggle/latch/cover
```

## Candidate Module Table

| Slot | Candidate | Source sample and lines | Structural / functional difference |
| --- | --- | --- | --- |
| S0 base_anchor | `offset_base_foot_with_integral_pin` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L96-L153`, instantiated at `L167-L181` | Foot, heel, toe, vertical support plate, gusset, pivot pad, and pin for offset rocker. |
| S0 base_anchor | `nested_bracket_foot_yoke` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L86-L140` | Dense grounded foot with base plate, pads, bolts, pedestal, clevis cheeks, and pin lobes. |
| S0 base_anchor | `cadquery_sideplate_base_with_pawl` | `rec_multisegment_foldout_arm_436d66fcea5347379babad577f85deb5/revisions/rev_000001/model.py:L247-L287` | CADQuery side-plate base with cheek plates, bridge blocks, pawl, detent, and lightened plate geometry. |
| S0 base_anchor | `flat_frame_with_aux_pivots` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L287-L342`, instantiated at `L368-L379` | Flat base frame with side slots, cross members, main arm pivot, toggle pivot, latch pivot, and pin cylinders. |
| S1 axis_family | `parallel_pitch_foldout` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L275-L330` | All serial arm joints share `(0,-1,0)` pitch axis in an XZ folding plane. |
| S1 axis_family | `parallel_pin_sideplate_chain` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L232-L267`, tests `L276-L286` | All joints share a side-plate pin axis `(0,1,0)` and alternating link offsets. |
| S1 axis_family | `auxiliary_fold_lock_pitch` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L525-L558` | Main chain uses pitch joints but base also carries latch/toggle revolutes. |
| S2 segment_count | `three_link_plus_terminal` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L141-L230`, joints `L232-L267` | Long-short-long serial links ending in a bracket/tray. |
| S2 segment_count | `four_serial_links` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L183-L273`, joints `L275-L330` | Rocker, elbow, forearm, and tip link form four moving serial links. |
| S2 segment_count | `three_primary_links_plus_end_fork_and_aux` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L393-L524` | Primary/secondary/tertiary arms, end fork, plus separate latch/toggle and access cover. |
| S3 segment_profile | `offset_eye_plate_link` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L52-L93`, used at `L183-L273` | CADQuery XZ profile links with root/tip eyes, pivot holes, and offset `dx/dz`. |
| S3 segment_profile | `paired_side_plate_link` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L25-L74`, used at `L141-L178` | Two side plates with lobes, caps, and cross spacer. |
| S3 segment_profile | `lightened_cadquery_sideplate_pair` | `rec_multisegment_foldout_arm_436d66fcea5347379babad577f85deb5/revisions/rev_000001/model.py:L65-L211`, used at `L290-L371` | Two sculpted plates with lugs, lightening slots, emboss ribs, pin heads, and bridge blocks. |
| S3 segment_profile | `slotted_keeper_link` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L123-L214`, used at `L393-L493` | Slotted side plates with rings, guide slot, keeper tabs, braces, and terminal trunnion option. |
| S4 hinge_interface | `eye_hole_pin_overlap` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L86-L93`, joint checks `L392-L395` | Adjacent links contact through cut eye holes and overlapping pivot pins. |
| S4 hinge_interface | `sideplate_lobe_pin_cap` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L44-L64` | Each side plate has near/far lobes and pin caps. |
| S4 hinge_interface | `ring_trunnion_sideplate` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L161-L209` | Ring barrels and optional distal trunnions are built into side plates. |
| S5 terminal_module | `plain_tip_link` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L252-L273` | Final link is a smaller eye-plate tip, preserving serial fold-out form. |
| S5 terminal_module | `tray_end_bracket` | `rec_multisegment_foldout_arm_bb2c3bcd2e1447eab28adcf9b7a544f2/revisions/rev_000001/model.py:L180-L230` | End bracket/tray with ears, pivot lobes, floor, side lips, front lip, and rear bridge. |
| S5 terminal_module | `small_cadquery_tray` | `rec_multisegment_foldout_arm_436d66fcea5347379babad577f85deb5/revisions/rev_000001/model.py:L374-L387` | Compact tray integrated from cylinder, floor, lips, ears, and small support blocks. |
| S5 terminal_module | `end_fork` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L474-L499` | Short fork shell carried after tertiary arm. |
| S6 auxiliary_fold_lock | `none_main_chain_only` | `rec_multisegment_foldout_arm_f81849398dc54726a31523708b8078cd/revisions/rev_000001/model.py:L275-L330` | Pure serial fold-out chain without auxiliary latches. |
| S6 auxiliary_fold_lock | `toggle_and_latch_pair` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L217-L284`, instantiated at `L501-L524`, joints `L532-L548` | Separate toggle and latch revolute links tied to base for folded state/readability. |
| S6 auxiliary_fold_lock | `access_cover_fixed_panel` | `rec_multisegment_foldout_arm_0003/revisions/rev_000001/model.py:L345-L357`, fixed joint `L525-L531` | Fixed cover panel on the base frame. |

## Interface Points

| Interface | Required frame | Contract |
| --- | --- | --- |
| `base.root_pivot` | Origin at first hinge; +X initial deployment direction; axis from `axis_family` | Base must include clevis/eye/pin geometry surrounding root pivot. |
| `segment.in` | Local root hinge center | Accepts previous segment's distal eye/trunnion/fork. |
| `segment.out` | Local distal hinge center, usually `(length,0,offset_z)` | Required on every non-terminal segment. |
| `terminal.in` | Local hinge center at final link | Must mate to last segment out and move with final revolute. |
| `aux.base_pivot` | Base-local pivot for latch/toggle | Optional; must not replace main fold-out chain. |

## Multiplicity / Copy Logic

- `segment_count` samples 3-5 for the main serial arm. Terminal module is separate when it is a tray/fork/pad; a plain tip link may count as the final moving segment.
- Each segment copy receives a generated local length, width, hinge radius, and distal offset while preserving the selected profile's part tree.
- Distal joint origin of segment `i` becomes the parent frame for segment `i+1`.
- Auxiliary latch/toggle modules may add 0-2 extra revolute joints plus fixed covers, but these are not counted as main segment multiplicity.
- Segment names must be indexed and stable: `segment_0`, `segment_1`, ..., `terminal`, with auxiliary names distinct.

## Compatibility Matrix

| Combination | offset foot | nested yoke | sideplate pawl base | flat frame | offset eye links | paired side plates | slotted keeper | tray | fork | aux latch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `parallel_pitch_foldout` | yes | yes | yes | yes | yes | yes | yes | yes | yes | limited |
| `parallel_pin_sideplate_chain` | limited | yes | yes | limited | limited | yes | yes | yes | limited | no |
| `auxiliary_fold_lock_pitch` | no | limited | limited | yes | no | limited | yes | no | yes | yes |
| `tray_end_bracket` | limited | yes | yes | no | limited | yes | limited | yes | no | no |
| `end_fork` | limited | limited | no | yes | limited | limited | yes | no | yes | yes |

Rules:

- `toggle_and_latch_pair` requires a base with explicit aux pivots and enough side clearance.
- `slotted_keeper_link` requires CADQuery side-plate implementation; do not degrade to a plain box.
- Tray modules require the final hinge to remain level enough that the tray reads as carried payload support.
- Mixed axis families must preserve mating orientation; unsupported mixed pitch/yaw combinations must be rejected before build.

## Topology Diversity Audit

Covered topology:

- Bases: offset foot, nested yoke, sideplate pawl base, flat frame with aux pivots.
- Main segment count: 3, 4, 5.
- Link topology: offset eye plate, paired side plates, lightened sculpted CADQuery plates, slotted keeper links.
- Hinge topology: eye-hole pin, lobe pin caps, ring/trunnion side plates.
- Terminal topology: plain tip, tray, compact tray, end fork.
- Auxiliary topology: none, fixed cover, toggle/latch revolutes.

Non-topological variation:

- Colors/materials alone.
- Uniform scaling of the same link graph.
- Decorative bolt heads without hinge, base, or terminal interface function.

## Procedural Sampling / Sweep Plan

Sampling must use deterministic `random.Random(seed)` and must not special-case `seed=0`.

1. Sample `segment_count` from 3-5.
2. Sample base and axis family.
3. Sample segment profile compatible with base and axis family.
4. Generate a decreasing or alternating length sequence, with optional `dz` offsets.
5. Sample hinge interface and terminal module compatible with segment profile.
6. Sample auxiliary fold-lock only if base supports aux pivots.
7. Sample controlled parameters after topology: reach, first segment ratio, width, height, hinge clearance, joint limits.
8. Reject unsupported module combinations before model construction.

Sweep:

- Run `uv run articraft template sweep-pipeline multisegment_foldout_arm`.
- Inspect representative seeds for stowed/deployed identity and terminal visibility.

## Controlled Local Parameterization

Allowed ranges:

- `reach`: 0.54-1.34 m.
- `segment_count`: 3-5.
- `link_width`: 0.036-0.078 m.
- `link_height`: at least 0.032 m and proportional to width.
- `hinge_clearance`: 0.0035-0.012 m.
- `first_segment_ratio`: 0.82-1.26.
- Joint limits: sampled by scale 0.72-1.28 while preserving fold-out deployment.
- Segment lengths may taper by about 0.8-0.95 per segment, but the final terminal must remain functional and visible.

Parameterization cannot remove side plates, slots, eyes, trunnions, tray lips, or auxiliary latch geometry when those modules are selected.

## Validator

The template validator must check:

- Main serial chain has `segment_count` revolute joints or an equivalent terminal-bracket final joint.
- All main joints are revolute.
- Axes match sampled axis family.
- Joint origins align with visible hinge geometry.
- Adjacent segments contact or are within small hinge clearance without broad body overlap.
- Deployed pose moves terminal away from base by a meaningful distance.
- Folded/stowed pose stays coherent and does not collide catastrophically.
- Auxiliary latch/toggle joints, if present, do not count as main chain joints but must remain valid.
- CADQuery mesh assets are ready for CADQuery candidates.

## Reject Cases

Reject outputs that:

- Have fewer than three fold-out moving segments unless a sourced terminal bracket supplies the final fold-out joint.
- Are a generic robotic arm without fold-out/nesting hinge identity.
- Replace complex side plates, slots, rings, latches, or trays with undifferentiated boxes.
- Use prismatic joints for the main chain.
- Place articulation origins away from visible hinges.
- Treat color, material, or size-only changes as candidates.
- Sample aux latch/toggle modules without implementing and testing their joints.
- Use curated or modulo-only seed tables rather than deterministic procedural sampling.
