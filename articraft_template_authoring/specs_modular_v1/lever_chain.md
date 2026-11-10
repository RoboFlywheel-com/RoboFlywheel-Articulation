# Modular Template Spec: lever_chain

## Review Header

- category_slug: `lever_chain`
- dataset_path: `data`
- mode: `SPEC_ONLY`
- reviewer_status: `approved`
- five_star_sample_count: 35
- required_files_read: `model.py`, `revision.json`, `record.json`, `prompt.txt`, `collections/dataset.json`
- template_scope: serial and coupled lever linkages with visible pivots, lever plates, and output tab/lever.

## Core Identity

A valid `lever_chain` is a grounded mechanical linkage made from levers or rocker plates connected by revolute pivots. It must read as a chain of force-transmitting levers, not a generic robot arm: flat plates, dogbone/capsule links, clevis brackets, pins, washers, bushings, guide slots, or coupler rods should make the lever mechanism explicit.

Required invariants:

- A grounded base/bracket supports the first pivot.
- At least two moving lever parts are connected by revolute joints; common 5-star samples use three or four main moving levers.
- Revolute pivots are visibly represented by pins, holes, washers, bushings, clevis cheeks, or bearing bosses.
- Main motion is a planar lever/rocker chain with joint axes parallel to the sampled axis.
- The final lever/output tab visibly moves when upstream joints are actuated.

## Slot Graph

```text
S0 ground_support
  -> S1 pivot_axis_family
      -> S2 lever_count
          -> S3 lever_profile[i]
              -> S4 pivot_hardware[i]
                  -> S5 output_module
  -> S6 auxiliary_couplers

Main chain:
ground --REVOLUTE--> lever_0 --REVOLUTE--> lever_1
  [--REVOLUTE--> lever_2 ...] --REVOLUTE--> output_lever/tab

Optional coupled study:
ground --REVOLUTE--> rocker_i
rocker_i outboard pin --coupler visual/prismatic guide--> rocker_{i+1}
```

## Candidate Module Table

| Slot | Candidate | Source sample and lines | Structural / functional difference |
| --- | --- | --- | --- |
| S0 ground_support | `compact_pedestal_root_bracket` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L88-L124` | Small base plate, pedestal block, fixed pivot pin, and mount bolts; first lever can be grounded into bracket. |
| S0 ground_support | `offset_clevis_mount` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L121-L170` | Open clevis with cheek plates, rear bridge, pin, pin head/clip, and base bolts. |
| S0 ground_support | `long_bench_yoke_frame` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L143-L198` | Long base rail with four fabricated yoke brackets, bushings, stop pads, slots, and standoffs. |
| S0 ground_support | `slotted_frame_with_clevis_brackets` | `rec_lever_chain_fd488d5ed66c4154845d3f2525eb46cb/revisions/rev_000001/model.py:L200-L240` | Large slotted base plate with rails, center bridge, and multiple clevis brackets for a complex lever train. |
| S1 pivot_axis_family | `vertical_z_plate_stack` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L101-L117`, joints implied by pin stack at `L126-L220` | Flat horizontal plate linkage with vertical pins and alternating top/bottom layers. |
| S1 pivot_axis_family | `horizontal_y_bench_linkage` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L60-L78`, parts `L172-L240` | Side-view dogbone plates with through-bores and Y-axis pins. |
| S1 pivot_axis_family | `staggered_y_axis_rocker_array` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L116-L142`, yoke brackets `L154-L176` | Multiple grounded rocker pivots laid out across a long bench, connected by couplers. |
| S2 lever_count | `three_moving_levers` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L126-L220` | Three serial moving lever links plus a grounded root link. |
| S2 lever_count | `two_levers_plus_terminal_tab` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L172-L240` | Two dogbone lever plates and a compact terminal tab. |
| S2 lever_count | `four_station_rocker_chain` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L232-L240` and pivots `L118-L142` | Four named rocker/input/output levers on separate pivot stations. |
| S3 lever_profile | `cadquery_capsule_plate` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L27-L72`, used at `L103-L220` | Rounded capsule plate with optional start/end holes and alternating layers. |
| S3 lever_profile | `extruded_dogbone_plate` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L40-L78`, used at `L172-L240` | Mesh dogbone/capsule lever with two through holes and Y-axis bore. |
| S3 lever_profile | `slotted_multi_hole_rocker` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L40-L78`, used at `L200-L235` | Dogbone plate with multiple holes plus central lightening/adjustment slot. |
| S3 lever_profile | `coupled_rocker_and_coupler` | `rec_lever_chain_fd488d5ed66c4154845d3f2525eb46cb/revisions/rev_000001/model.py:L126-L197`, coupler start `L237-L240` | Rockers and separate dogbone couplers with follower pins and spacers. |
| S4 pivot_hardware | `pin_spacer_washer_stack` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L136-L159`, `L171-L194`, `L206-L220` | Pin, bearing spacer, upper washer, and lower washer on each moving lever. |
| S4 pivot_hardware | `clevis_pin_head_clip` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L146-L163`, lever hardware `L178-L233` | Clevis root pin plus bushing, pin head, and clip. |
| S4 pivot_hardware | `yoke_bushing_stop_pad` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L154-L192` | Open yoke brackets with bronze bushings, bore shadows, bolts, and stop pads. |
| S5 output_module | `short_terminal_tab` | `rec_lever_chain_43090f1387254e78afb12f622f07a31d/revisions/rev_000001/model.py:L235-L240` | Compact output member distinct from long lever plate. |
| S5 output_module | `last_capsule_tab` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L196-L220` | Small final capsule/tab with output hole. |
| S5 output_module | `output_lever_with_guide_pin` | `rec_lever_chain_fd488d5ed66c4154845d3f2525eb46cb/revisions/rev_000001/model.py:L51-L83`, output/guide constants and radius | Output lever includes a guide/follower point for constrained motion. |
| S6 auxiliary_couplers | `none_serial_only` | `rec_lever_chain_58d921d460024bffa6c383ddc6c67c86/revisions/rev_000001/model.py:L275-L330` | Pure serial lever chain with no separate coupler rods. |
| S6 auxiliary_couplers | `front_dogbone_couplers` | `rec_lever_chain_0003/revisions/rev_000001/model.py:L136-L142`, `L237-L240` | Couplers connect outboard pins across grounded rocker stations. |
| S6 auxiliary_couplers | `slotted_guided_couplers` | `rec_lever_chain_fd488d5ed66c4154845d3f2525eb46cb/revisions/rev_000001/model.py:L149-L188` | Slots, secondary pin hardware, pivot hardware, and bridge spacers add guided lever-chain function. |

## Interface Points

| Interface | Required frame | Contract |
| --- | --- | --- |
| `ground.root_pivot` | Pivot center, axis sampled from `pivot_axis_family` | Base must visibly surround root pivot with bracket/clevis/yoke hardware. |
| `lever.in` | Local pivot center | Child lever root hole/pin must align with parent output pivot. |
| `lever.out` | Distal pin center | Nonterminal lever exposes a pin/hole for next lever or coupler. |
| `output.in` | Final pivot center | Output tab/lever mates to previous lever and remains visible. |
| `coupler.attach` | Outboard pin centers on rockers | Optional couplers attach to secondary holes/pins, not to empty space. |

## Multiplicity / Copy Logic

- `lever_count` samples 2-4 main moving levers. Root support may include a grounded lever plate but it does not count as a moving lever.
- Serial mode copies the selected lever profile for each moving link with length taper and alternating layer/offset.
- Coupled mode creates multiple grounded rockers plus visual/optional articulated couplers. Couplers are auxiliary and must not replace the main lever identity.
- Every lever copy must have one local input pivot and either an output pivot or terminal function.

## Compatibility Matrix

| Combination | compact bracket | offset clevis | bench yoke | slotted frame | capsule plate | dogbone plate | slotted rocker | terminal tab | couplers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `vertical_z_plate_stack` | yes | limited | no | no | yes | limited | no | yes | no |
| `horizontal_y_bench_linkage` | limited | yes | yes | yes | limited | yes | yes | yes | yes |
| `three_moving_levers` | yes | yes | limited | limited | yes | yes | limited | yes | no |
| `four_station_rocker_chain` | no | limited | yes | yes | no | yes | yes | yes | yes |
| `slotted_guided_couplers` | no | limited | yes | yes | no | limited | yes | limited | yes |

## Topology Diversity Audit

Covered topology:

- Ground support: compact bracket, clevis, bench yoke frame, slotted frame.
- Axis family: vertical plate stack and horizontal Y-axis bench linkage.
- Lever profile: capsule plates, dogbone plates, slotted rockers, coupled rockers.
- Pivot hardware: washer stacks, clevis pins, yoke bushings/stops.
- Output: terminal tab, last capsule, guided output lever.
- Auxiliary: no coupler, dogbone couplers, slotted/guided couplers.

Rejected as topology:

- Color/material changes.
- Pure lever length scaling without changed part tree or interface.
- Decorative bolt heads unconnected to support, pivot, or guide function.

## Procedural Sampling / Sweep Plan

Use deterministic `random.Random(seed)` with no `seed=0` special case.

1. Sample axis family.
2. Sample compatible base.
3. Sample lever count 2-4.
4. Sample lever profile and pivot hardware.
5. Sample output module.
6. Sample auxiliary couplers only when base/profile support them.
7. Sample lengths, offsets, plate width, layer spacing, pin radii, and joint limits.
8. Reject unimplemented combinations before building; `slot_choices_for_seed` only reports implemented modules.

## Controlled Local Parameterization

- `lever_count`: 2-4.
- `link_length`: 0.08-0.32 m.
- `plate_width`: 0.018-0.075 m.
- `plate_thickness`: 0.004-0.020 m.
- `pin_radius`: 0.0035-0.014 m.
- `layer_offset`: enough to visually separate stacked plates while keeping hinge contact.
- `joint_upper/lower`: about +/-0.4 to +/-1.6 rad, sampled per layout.

Parameterization cannot remove pivot holes, washers/bushings, clevis cheeks, or coupler/slot features selected by the module.

## Validator

The validator must check:

- At least two moving lever/output parts exist.
- Main joints are revolute.
- Joint axes match the sampled axis family.
- Joint origins lie at visible pin/hole hardware.
- Adjacent lever interfaces overlap/contact at hinge stations without broad body collision.
- Output part moves under representative joint pose.
- Couplers, if present, attach to visible outboard pins.
- Mesh assets are ready for CADQuery/mesh candidates.

## Reject Cases

Reject outputs that:

- Are generic robotic arms rather than flat lever/linkage chains.
- Use prismatic joints as the main lever-chain joints.
- Omit visible pivot holes/pins/washers/bushings.
- Collapse all levers into one rigid part.
- Replace complex dogbone/slotted/coupled structures with plain boxes only.
- Treat colors, scale-only changes, or decorative bolts as candidates.
- Sample unsupported coupler/guide combinations.
