# Modular Template Spec: shoulderelbowwrist_arm

## Review Header

- category_slug: `shoulderelbowwrist_arm`
- dataset_path: `data`
- mode: `SPEC_ONLY`
- reviewer_status: `approved`
- five_star_sample_count: 34
- required_files_read: `model.py`, `revision.json`, `record.json`, `prompt.txt`, `collections/dataset.json`
- template_scope: serial industrial arm with shoulder, elbow, and wrist joints.

## Core Identity

A valid `shoulderelbowwrist_arm` is a fixed-base articulated robot arm with a shoulder joint, an elbow joint, and a wrist/tool joint arranged in a serial kinematic chain. It must have visible shoulder support, upper arm, forearm, and wrist/tool module, with joint axes and joint origins placed at physical bearings, collars, clevises, drums, or cartridges. The category identity is kinematic and structural: shoulder-elbow-wrist motion, not merely a stack of decorative beams.

Required invariants:

- A base/foundation part anchors the arm.
- The moving chain includes upper arm, forearm, and wrist/tool module.
- At least three named functional joints are represented across shoulder, elbow, and wrist; optional fixed adapter joints may appear when a pedestal/yaw head is modeled separately.
- Shoulder, elbow, and wrist axes must match the sampled layout and be visually supported by bearings or hinge geometry.
- The elbow must change forearm pose; the wrist must change terminal/tool pose.
- The wrist terminal must include a functional interface: tool flange, gripper, camera pod, nozzle, pad, or equivalent.

## Slot Graph

```text
S0 foundation_base
  -> S1 shoulder_kinematic_stack
      -> S2 upper_arm_link
          -> S3 elbow_interface
              -> S4 forearm_link
                  -> S5 wrist_module
                      -> S6 terminal_tool

Joint graph examples:
base --REVOLUTE_Z shoulder_yaw--> shoulder_head --FIXED/PITCH--> upper_arm
upper_arm --REVOLUTE_Y elbow_pitch--> forearm --REVOLUTE_Y or REVOLUTE_X wrist--> terminal

or:
base --REVOLUTE_Y shoulder_pitch--> upper_arm --REVOLUTE_Y elbow_pitch--> forearm --REVOLUTE_Y wrist_pitch--> terminal
```

## Candidate Module Table

| Slot | Candidate | Source sample and lines | Structural / functional difference |
| --- | --- | --- | --- |
| S0 foundation_base | `round_pedestal_with_anchor_cuts` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L36-L58`, instantiated at `L161-L166` | Cylindrical floor pedestal with base plate, column, shoulder head, and anchor holes. |
| S0 foundation_base | `bench_plate_plinth_bearing_ring` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L51-L93`, instantiated at `L245-L251` | Rectangular bench plate, plinth, bearing ring, and access panel. |
| S0 foundation_base | `box_column_with_braced_access_panels` | `rec_shoulderelbowwrist_arm_0003/revisions/rev_000001/model.py:L228-L284` | Box column with cut-out interior, side braces, access cover, and anchor bolts. |
| S0 foundation_base | `turntable_bench_with_separate_pedestal` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L27-L98` | Base plate with bearing ring and a separate yaw pedestal/turntable disk. |
| S1 shoulder_kinematic_stack | `vertical_yaw_then_pitch` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L189-L215` | Shoulder yaw around Z, then elbow/wrist pitch axes; classic industrial arm. |
| S1 shoulder_kinematic_stack | `yaw_head_with_fixed_upper_mount` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L310-L343` | Yaw pedestal is separate, upper arm fixed to pedestal, elbow pitch, wrist roll along forearm. |
| S1 shoulder_kinematic_stack | `bench_yaw_fixed_mount_roll_wrist` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L244-L277` | Separate fixed upper mount plus elbow pitch and X-axis wrist roll. |
| S2 upper_arm_link | `profile_extruded_upper_arm` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L61-L85`, part at `L168-L173` | CADQuery extruded side profile with shoulder turret and elbow end. |
| S2 upper_arm_link | `cast_box_beam_with_elbow_barrel` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L126-L171`, part at `L277-L283` | Cast/blocky beam with mount flange, shoulder block, service boss, elbow plate, and barrel. |
| S2 upper_arm_link | `hollow_service_beam` | `rec_shoulderelbowwrist_arm_0003/revisions/rev_000001/model.py:L143-L225`, upper use `L317-L330` | Hollow beam with cutouts, top cover, side panel, and fasteners. |
| S2 upper_arm_link | `twin_side_rail_upper_arm` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L100-L160` | Twin side rails and distal ears around a recessed web. |
| S3 elbow_interface | `integrated_elbow_collar` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L78-L112`, joint at `L198-L206` | Upper/forearm have matching collar geometry and pitch origin at arm end. |
| S3 elbow_interface | `wide_clevis_with_annular_bushings` | `rec_shoulderelbowwrist_arm_0003/revisions/rev_000001/model.py:L403-L444` | Deep elbow clevis with side plates, ties, ribs, bore cut, annular faces, and fasteners. |
| S3 elbow_interface | `fork_captures_central_lug` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L137-L168`, contact checks `L325-L346` | Upper arm distal ears capture a forearm elbow lug. |
| S4 forearm_link | `profile_extruded_forearm` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L88-L112`, part at `L175-L180` | Tapered profile forearm with elbow and wrist collars. |
| S4 forearm_link | `cast_forearm_with_wrist_barrel` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L174-L212`, part at `L285-L291` | Beam forearm with elbow plate/barrel and wrist plate/barrel. |
| S4 forearm_link | `hollow_forearm_service_beam` | `rec_shoulderelbowwrist_arm_0003/revisions/rev_000001/model.py:L481-L514` | Hollow beam with top/side service covers and support webs. |
| S4 forearm_link | `rail_spine_forearm` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L162-L204` | Forearm has central spine, top cover, side rails, and wrist bearing. |
| S5 wrist_module | `pitch_wrist_flange_shell` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L115-L144`, part at `L182-L187` | Pitching wrist link with collar, adapter, flange disk, pilot ring, bore, and bolt pattern. |
| S5 wrist_module | `roll_cartridge_with_tool_flange` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L215-L234`, part at `L293-L308` | Cylindrical wrist cartridge with a separate tool flange. |
| S5 wrist_module | `x_axis_roll_cartridge` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L206-L242`, joint at `L269-L277` | Wrist rolls along forearm axis and carries a bolted flange face. |
| S6 terminal_tool | `tool_flange` | `rec_shoulderelbowwrist_arm_c38010c773464573b66062600dffee98/revisions/rev_000001/model.py:L129-L143` | Bolt-pattern tool flange and pilot ring. |
| S6 terminal_tool | `flange_with_projecting_register` | `rec_shoulderelbowwrist_arm_6f209d86c4ca453eba044c155c992d61/revisions/rev_000001/model.py:L223-L234` | Flange disk with pilot, bolt cuts, and nose register. |
| S6 terminal_tool | `service_bolted_face` | `rec_shoulderelbowwrist_arm_e4d07bdde69c4c00903903be7ec50006/revisions/rev_000001/model.py:L219-L242` | Large service/tool flange with six bolt heads around the face. |

## Interface Points

| Interface | Required frame | Contract |
| --- | --- | --- |
| `base.shoulder_axis` | World/base shoulder origin; +Z for yaw or +Y for pitch depending layout | Foundation must visually include bearing/column/turntable around this origin. |
| `shoulder.out` | At shoulder head or fixed upper mount | Upper arm root must contact or be intentionally nested in shoulder hardware. |
| `upper.elbow_out` | Local X at elbow bearing center | Must expose collar, clevis, fork ears, or boss for forearm input. |
| `forearm.elbow_in` | Local origin at matching elbow bearing | Child origin must align with upper elbow out and share axis. |
| `forearm.wrist_out` | Local X at wrist bearing center | Wrist module attaches with visible cartridge/collar/flange support. |
| `wrist.tool_face` | Distal face normal +X | Terminal module/tool must project beyond forearm and remain visible through motion. |

## Multiplicity / Copy Logic

- Joint multiplicity is fixed to the semantic shoulder-elbow-wrist set. A separate yaw pedestal plus fixed upper mount may add one fixed articulation but cannot remove shoulder/elbow/wrist functionality.
- Link multiplicity is one upper arm, one forearm, one wrist terminal. Do not duplicate parallel arms in this category.
- Auxiliary details such as caps, bushings, bolts, covers, and rails may repeat per joint station; these are local detail copies, not slot candidates unless they represent the sourced hardware module.
- Wrist terminal tools sample one at a time; do not combine gripper/nozzle/camera/flange unless the selected source module includes such a combined assembly.

## Compatibility Matrix

| Combination | round pedestal | bench plinth | braced column | turntable bench | profile beams | cast beams | hollow service beams | twin rails | pitch wrist | roll cartridge |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `vertical_yaw_then_pitch` | yes | yes | yes | yes | yes | yes | yes | yes | yes | limited |
| `yaw_head_with_fixed_upper_mount` | limited | yes | yes | yes | limited | yes | yes | yes | limited | yes |
| `bench_yaw_fixed_mount_roll_wrist` | no | yes | limited | yes | no | limited | no | yes | no | yes |
| `wide_clevis_with_annular_bushings` | limited | yes | yes | limited | no | limited | yes | no | yes | limited |
| `fork_captures_central_lug` | no | limited | no | yes | no | no | limited | yes | no | yes |

Rules:

- `roll_cartridge` requires wrist axis `(1, 0, 0)` and a forearm nose bearing aligned on +X.
- `pitch_wrist_flange_shell` requires a Y-axis wrist pitch and a collar at the forearm end.
- `twin_side_rail_upper_arm` must pair with central forearm lug or compatible barrel geometry.
- `hollow_service_beam` may not be replaced by a plain rectangular box; its cutouts/covers/fasteners are structural cues.

## Topology Diversity Audit

Covered topological differences:

- Foundation: round pedestal, bench plinth, braced column, separate turntable pedestal.
- Kinematic layout: Z-yaw plus pitch joints, fixed upper mount with yaw head, X-axis wrist roll.
- Arm links: profile-extruded shells, cast box beams, hollow service beams, twin side rail arms.
- Elbow interfaces: collar, wide clevis, fork/lug capture.
- Wrist/terminal: pitch flange shell, roll cartridge, bolt-pattern tool face.

Not accepted as topology:

- Pure color/material changes.
- Changing only reach or link width with unchanged part tree.
- Bolts used only as decoration without supporting an interface or terminal module.

## Procedural Sampling / Sweep Plan

Use deterministic `random.Random(seed)` with no `seed=0` special case.

1. Sample kinematic layout first.
2. Sample foundation compatible with layout.
3. Sample upper link and elbow interface compatible with layout and foundation scale.
4. Sample forearm link and wrist module compatible with elbow and wrist axis.
5. Sample terminal tool from implemented compatible terminals.
6. Sample controlled dimensions: reach, upper/forearm split, shoulder height, link width, joint radii, motion-limit scale.
7. Reject unsupported combinations before build; `slot_choices_for_seed` reports only real implemented candidates.

Sweep plan:

- Run `uv run articraft template sweep-pipeline shoulderelbowwrist_arm`.
- Require 50/50 or at least threshold pass with no systematic failure cluster.
- Module topology diversity must show distinct layout/base/link/wrist/tool outcomes.

## Controlled Local Parameterization

Allowed ranges:

- `reach`: 0.46-1.24 m.
- `upper_ratio`: 0.44-0.62 of non-wrist reach.
- `shoulder_z`: 0.12-0.42 m.
- `link_width`: 0.038-0.088 m.
- `link_height`: proportional to link width, at least 0.036 m.
- `joint_limit_scale`: 0.70-1.30.
- Joint barrels/rings/collars scale with link width and must remain visibly larger than link wall thickness.

Parameterization may scale and proportion the module, but it cannot delete bearing/collar interfaces, flatten the wrist into the forearm, or alter sampled joint axes.

## Validator

The template validator must check:

- Parts include base/foundation, upper arm, forearm, wrist/tool.
- Shoulder, elbow, and wrist semantic joints exist; optional fixed adapter allowed.
- Required semantic joints are revolute.
- Joint axes match sampled layout exactly or within tolerance.
- Joint origins are near visible bearings/collars/forks.
- Upper and forearm contact/seat at elbow; wrist contacts/seats at forearm nose.
- Terminal/tool face projects beyond forearm.
- Representative poses for shoulder/elbow/wrist move expected child parts and avoid broad body collisions.
- Mesh assets are ready for CADQuery candidates.

## Reject Cases

Reject outputs that:

- Are only a generic two-link lever without a wrist module.
- Omit the foundation or collapse base and upper arm into one unarticulated part.
- Use only decorative cylinders as joints while articulation origins float elsewhere.
- Replace CADQuery shells, hollow beams, clevises, or bolt-pattern flanges with plain boxes/cylinders.
- Sample a wrist roll module but give it a pitch axis, or sample a pitch wrist with an X-roll axis.
- Use colors/materials as candidates.
- Use curated seed tables or modulo-only selection instead of procedural sampling.
