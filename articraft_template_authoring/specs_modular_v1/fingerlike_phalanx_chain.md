# Modular Template Spec: fingerlike_phalanx_chain

## Review Header

- category_slug: `fingerlike_phalanx_chain`
- dataset_path: `data`
- mode: `SPEC_ONLY`
- reviewer_status: `approved`
- five_star_sample_count: 38
- required_files_read: `model.py`, `revision.json`, `record.json`, `prompt.txt`, `collections/dataset.json`
- template_scope: serial fingerlike phalanx chains with parallel knuckle revolute joints and fingertip/coupler endings.

## Core Identity

A valid `fingerlike_phalanx_chain` is a compact articulated digit: a fixed palm/base/root support, two to five serial phalanx or link parts, and one revolute knuckle between each adjacent pair. The visible identity comes from repeated hinge barrels, clevis/fork ears or bushing bosses, decreasing link scale toward the tip, and planar curl motion around parallel local Y axes. It may be a biomimetic single finger, a robotic gripper finger, or a small bank of parallel fingers, but it must remain a fingerlike chain rather than a generic linkage.

Non-negotiable invariants:

- At least one fixed base/root part supports the proximal knuckle.
- At least two moving phalanx/link parts are arranged in serial order.
- Every joint between base and distal tip is `REVOLUTE` with a parallel Y-axis knuckle.
- Positive motion curls the distal portion inward/palmward with shorter forward reach.
- Link scale tapers or steps down toward the distal end.
- Each implemented candidate must preserve real hinge interface geometry: fork ears, barrels, bosses, sockets, bushings, or equivalent paired contact features.

## Slot Graph

```text
S0 foundation_mount
  -> S1 chain_multiplicity
      -> S2 proximal_interface
          -> S3 repeated_phalanx_body[i]
              -> S4 distal_terminal
  -> S5 auxiliary_guidance

Joint graph per chain:
foundation_mount --REVOLUTE_Y--> phalanx_0 --REVOLUTE_Y--> phalanx_1
  [--REVOLUTE_Y--> phalanx_2 ...] --REVOLUTE_Y--> terminal/link_tip
```

## Candidate Module Table

| Slot | Candidate | Source sample and lines | Structural / functional difference |
| --- | --- | --- | --- |
| S0 foundation_mount | `rear_spine_with_root_knuckle` | `rec_fingerlike_phalanx_chain_5d1869459c1f4a0eb7418f1a998b3017/revisions/rev_000001/model.py:L196-L265`, instantiated at `L274-L275` | A long dorsal/rear spine rail with root post, rungs, and root knuckle; supports the whole finger from behind rather than a palm plate. |
| S0 foundation_mount | `cadquery_base_block_with_knuckle_bulb` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L92-L107`, used at `L208-L213` | Rounded CADQuery base block with web, rear block, and integral knuckle bulb; compact biomimetic mount. |
| S0 foundation_mount | `clevis_mount_block_with_bores` | `rec_fingerlike_phalanx_chain_0001/revisions/rev_000001/model.py:L45-L89`, part builder `L199-L210` | Machined clevis base with two ears, gussets, center bore, and mount holes; mechanically explicit support. |
| S0 foundation_mount | `wide_machine_housing_with_parallel_cheeks` | `rec_fingerlike_phalanx_chain_b72d74fd8d3e4c03800d7a26efaa9134/revisions/rev_000001/model.py:L64-L85`, instantiated at `L153-L198` | Wide housing with paired clevis cheeks, rails, pin caps, bushings, and fasteners; reads as industrial gripper root. |
| S1 chain_multiplicity | `single_serial_digit` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L202-L302` | One serial chain attached to one base. |
| S1 chain_multiplicity | `parallel_multi_digit_bank` | Existing 5-star family shows repeated chain layout in same category; representative source `rec_fingerlike_phalanx_chain_b72d74fd8d3e4c03800d7a26efaa9134/revisions/rev_000001/model.py:L167-L198` for paired root-side clevis stations and replicated side hardware | Multiple laterally spaced finger chains share one base; multiplicity changes topology by duplicating the serial chain subgraph. |
| S2 proximal_interface | `fork_ear_and_center_knuckle` | `rec_fingerlike_phalanx_chain_5d1869459c1f4a0eb7418f1a998b3017/revisions/rev_000001/model.py:L82-L193` | Box/Cylinder phalanx with rear fork ears, center gap, front neck, and outgoing knuckle. |
| S2 proximal_interface | `lofted_bulb_socket` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L110-L195` | CADQuery lofted body with proximal bulb and optional distal bulb; organic continuous shell. |
| S2 proximal_interface | `machined_clevis_with_pin_bores` | `rec_fingerlike_phalanx_chain_0001/revisions/rev_000001/model.py:L92-L158` | Clevis link with lugs, bore cuts, proximal barrel, and distal ear pair. |
| S3 repeated_phalanx_body | `box_ridge_phalanx` | `rec_fingerlike_phalanx_chain_5d1869459c1f4a0eb7418f1a998b3017/revisions/rev_000001/model.py:L109-L193` | Rectangular finger segment with dorsal ridge and necked front knuckle. |
| S3 repeated_phalanx_body | `lofted_tapered_shell` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L123-L195` | Tapered CADQuery shell built from multiple body blocks and bulb/bridge unions. |
| S3 repeated_phalanx_body | `curved_web_link` | `rec_fingerlike_phalanx_chain_b72d74fd8d3e4c03800d7a26efaa9134/revisions/rev_000001/model.py:L113-L132`, instantiated at `L247-L293` | Curved load-bearing web with offset distal fork; non-collinear link geometry. |
| S4 distal_terminal | `rounded_integrated_tip_cap` | `rec_fingerlike_phalanx_chain_5d1869459c1f4a0eb7418f1a998b3017/revisions/rev_000001/model.py:L109-L151`, distal use `L283-L290` | Distal phalanx ends in a rounded cylinder cap blended into the body. |
| S4 distal_terminal | `cadquery_spherical_tip` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L176-L186`, distal use `L255-L272` | Distal segment uses a rounded/spherical fingertip built into lofted shell. |
| S4 distal_terminal | `flat_replaceable_pad` | `rec_fingerlike_phalanx_chain_b72d74fd8d3e4c03800d7a26efaa9134/revisions/rev_000001/model.py:L295-L337` | Distal link carries a flat pad plus small screws; functional gripping surface. |
| S4 distal_terminal | `terminal_clevis_nose` | `rec_fingerlike_phalanx_chain_0001/revisions/rev_000001/model.py:L161-L196`, builder `L250-L283` | Terminal link has barrel root and tapered nose/cap instead of outgoing fork. |
| S5 auxiliary_guidance | `ladder_spine_rail` | `rec_fingerlike_phalanx_chain_5d1869459c1f4a0eb7418f1a998b3017/revisions/rev_000001/model.py:L196-L265` | Adds a dorsal guide rail and rungs behind the moving phalanxes. |
| S5 auxiliary_guidance | `pin_cap_and_bushing_faces` | `rec_fingerlike_phalanx_chain_b72d74fd8d3e4c03800d7a26efaa9134/revisions/rev_000001/model.py:L167-L198`, `L221-L245`, `L269-L293`, `L317-L337` | Adds explicit external caps/bushings/screws at hinge stations. |
| S5 auxiliary_guidance | `none_integrated_only` | `rec_fingerlike_phalanx_chain_877656b3c2c9436db5c2a8e56a95069b/revisions/rev_000001/model.py:L202-L302` | No separate guide rail or external hardware; shape itself provides hinge readability. |

## Interface Points

| Interface | Required frame | Contract |
| --- | --- | --- |
| `foundation.out[i]` | Origin at proximal knuckle center, +X along initial finger extension, +Y along hinge axis, +Z dorsal/up | Must expose enough side clearance for `phalanx_0.in`; may be single root or a lateral array. |
| `phalanx.in` | Local origin at proximal hinge center | Accepts parent fork/boss socket; must overlap/contact hinge feature but avoid body interpenetration. |
| `phalanx.out` | Local X at distal hinge center | Present on every non-terminal phalanx; feeds next `phalanx.in`. |
| `terminal.in` | Local origin at final hinge center | Uses same Y-axis revolute contract as phalanx input. |
| `aux.attach` | Base/body relative frames near hinge stations | Guidance modules may add rails, caps, bushings, fasteners, or pads without changing joint semantics. |

## Multiplicity / Copy Logic

- `chain_count` samples 1-3. For `chain_count > 1`, duplicate the whole serial chain laterally along Y with one shared foundation. Each duplicate keeps an independent revolute joint set.
- `phalanx_count` samples 2-5 per chain. The last moving part uses a terminal candidate; all earlier parts use a repeated phalanx candidate and expose `out`.
- Per-chain Y spacing must exceed maximum phalanx width plus hinge cap width so adjacent chains do not collide during curl.
- Naming must include both chain index and segment index for duplicated chains: `chain_0_phalanx_0`, `chain_1_joint_2`, etc.
- Multiplicity cannot be faked by decorative repeated screws only; it must duplicate articulated parts/joints when used.

## Compatibility Matrix

| Slot / candidate | rear_spine | compact CAD base | clevis mount | machine housing | box/ridge | lofted shell | machined clevis | curved web | rounded tip | spherical tip | flat pad | terminal nose |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rear_spine_with_root_knuckle` | yes | n/a | n/a | n/a | yes | no | limited | no | yes | no | no | limited |
| `cadquery_base_block_with_knuckle_bulb` | n/a | yes | n/a | n/a | limited | yes | limited | no | limited | yes | no | yes |
| `clevis_mount_block_with_bores` | n/a | n/a | yes | n/a | limited | limited | yes | no | limited | no | limited | yes |
| `wide_machine_housing_with_parallel_cheeks` | n/a | n/a | n/a | yes | no | limited | yes | yes | no | limited | yes | no |
| `parallel_multi_digit_bank` | limited | yes | limited | yes | yes | yes | yes | no | yes | yes | yes | yes |
| `curved_web_link` | no | no | limited | yes | no | no | limited | yes | no | no | yes | no |

Rules:

- `curved_web_link` requires a wide enough foundation or an explicit distal hinge offset; reject with compact rear spine unless geometry is rescaled and tested.
- `flat_replaceable_pad` requires a broad terminal carrier, not a tiny rounded fingertip shell.
- `ladder_spine_rail` is compatible only with single-chain or sufficiently wide base; in multi-chain mode it must be copied per chain or replaced with integrated hardware.

## Topology Diversity Audit

Required topology changes covered by candidates:

- Foundation topology: spine rail, compact bulb base, machined clevis, wide housing.
- Link topology: straight box/ridge phalanx, lofted tapered shell, clevis mechanical segment, curved web link.
- Terminal topology: rounded integrated cap, spherical/organic tip, flat replaceable pad, terminal clevis/nose.
- Graph topology: variable 2-5 serial joints per chain and optional 1-3 parallel chain copies.
- Auxiliary topology: no aux, ladder rail, external caps/bushings.

Rejected as non-topological diversity:

- Color/material palettes alone.
- Uniform scale changes with the same part graph and same interfaces.
- Decorative screws without hinge/terminal/support function.

## Procedural Sampling / Sweep Plan

Sampling must be deterministic from `random.Random(seed)` and must not special-case `seed=0`.

1. Sample `chain_count` from 1-3 with enough lateral clearance.
2. Sample `phalanx_count` from 2-5.
3. Sample foundation candidate subject to compatibility with chain count.
4. Sample phalanx body candidate for all repeated links, or mix only if interface contracts are identical.
5. Sample terminal candidate subject to final link carrier width.
6. Sample auxiliary guidance from compatible candidates.
7. Sample controlled continuous parameters after topology: base width/depth, proximal length, taper ratios, hinge radius, curl upper limits, and per-link offset/drop.
8. Validator rejects unsupported sampled combinations before building; `slot_choices_for_seed` must return only implemented/tested combinations.

Sweep requirements:

- Run at least 50 seeds through `uv run articraft template sweep-pipeline fingerlike_phalanx_chain`.
- Confirm all sampled combinations create valid part trees and no unsupported slot combination appears.
- Confirm module topology diversity includes foundation, phalanx, terminal, auxiliary, count, and joint-count variation.

## Controlled Local Parameterization

Allowed local ranges:

- `base_width`: large enough for `chain_count`; otherwise 0.084-0.180 m.
- `base_depth`: 0.052-0.096 m.
- `base_height`: 0.028-0.054 m.
- `proximal_length`: 0.054-0.102 m.
- `proximal_width`: 0.022-0.046 m.
- `proximal_height`: 0.018-0.036 m.
- `length_taper`: 0.72-0.92.
- `width_taper`: 0.80-0.95.
- `hinge_radius`: proportional to segment height, clamped to preserve visible barrels/bosses.
- `curl_upper`: 0.72-1.34 rad per joint, with distal joints allowed slightly lower upper limits.

These parameters may adjust proportions, but they cannot remove hinge barrels/forks, erase the terminal function, collapse multiple phalanxes into one mesh, or change revolute semantics.

## Validator

The template validator must check:

- `len(chains) == chain_count` and each chain has `phalanx_count` moving parts.
- Total revolute joints equals `chain_count * phalanx_count`.
- Every joint type is `ArticulationType.REVOLUTE`.
- Every joint axis is parallel to `(0, 1, 0)` within tolerance.
- Joint origins coincide with visible hinge/boss geometry and are not far from child/parent geometry.
- Segment length/width generally tapers from proximal to distal.
- In a representative curl pose, distal tip moves inward/downward relative to rest.
- Adjacent phalanxes contact or nearly contact at hinge interfaces without broad body collision.
- Multi-chain spacing avoids same-pose and curled-pose collisions.
- Generated assets/meshes are present when CADQuery mesh candidates are used.

## Reject Cases

Reject generated objects that:

- Are just a generic three-bar/four-bar linkage without fingerlike taper, base, and terminal tip.
- Use prismatic, continuous, ball, or nonparallel revolute joints for the serial phalanx chain.
- Have fewer than two moving phalanx/link parts.
- Place hinge axes away from visible knuckles or inside empty space.
- Replace real sourced module geometry with plain undifferentiated boxes/cylinders where source used CADQuery lofts, clevis ears, bores, or curved webs.
- Treat material/color/scale as a slot candidate without structural or functional difference.
- Sample a module combination that the implementation does not build or test.
- Allow seed-specific curated branches or modulo-only tables instead of deterministic procedural sampling.
