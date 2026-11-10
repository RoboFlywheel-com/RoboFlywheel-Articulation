# pictureX / 0611 / Chain_separator — modular spec

> Supersedes the 2026-07-14 `status: pending` draft. That draft's engineering findings (bench-fork
> double-offset defect, capture-interference bands, guide slot length, turret rib overlap) are retained
> verbatim in §13 / Reject cases. What changed: the draft kept S1's diagonal spindle axis for the planar
> frames and S2's vertical axis for the bench frame — two incompatible root frames in one slug — and
> then had to gate away 53 of 72 combinations (core domain 19). This version adopts S2's convention as
> the single canonical body frame, which **dissolves** those gates by construction (core domain 72, zero
> deny rows) and removes the double-offset defect class at its root.

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Chain_separator` |
| template path | `agent/templates/pictureX_0611_Chain_separator.py` |
| test path (optional) | — (sweep-pipeline is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed` (serial drive chain `frame→driver_carriage→head→handle` + parallel children `anvil_turret` / `guide_carriage` on the `frame` root) |

## Category Binding

category_slug: pictureX_0611_Chain_separator · template_slug: pictureX_0611_Chain_separator ·
mechanism_profile: `aligned_driver_press` (a rigid reaction frame carrying ONE driver that advances
along ONE working axis into a chain cradle; leverage hardware varies) · export_namespace: pictureX_0611_Chain_separator
diversity_profile: `standard` ·
profile_reason: honest core vocabulary = 4 reaction-frame skeletons × 3 leverage/drive mechanisms ×
3 chain-cradle forms × 2 guide options = 72 gate-legal core combos. Above the standard floor (48),
below compositional (120): the subcategory contract ("every candidate must preserve an aligned driver
and a visible reaction path through the chain cradle") caps how many structurally distinct skeletons and
mechanisms can exist without leaving the category, so reaching 120 would require inventing ①/②
candidates the 8-record pool does not contain — forbidden by AUTHORING Rule 3.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this subcategory (1 picture origin + 7 single-axis forks), read in full from `data/records/<id>/revisions/rev_000001/model.py` |
| source_index_policy | only adopted module sources are indexed below (§14); 8/8 adopted, none excluded |

Reading notes (what the pool actually contains):

- **All 8 share one drivetrain skeleton**: a root `frame` casting with a spindle bore, a
  `driver_carriage` on a PRISMATIC `driver_feed` joint along the working axis, and leverage hardware on
  the carriage's rear end. Each fork changes exactly one axis and holds the rest at the S1 baseline.
- **S2 (bench C-frame) is the coordinate authority.** S2 re-poses the identical drive helpers
  (`_spindle_carriage_shape` / `_blue_spindle_hub_shape` / `_blue_slide_bar_shape` — byte-identical to
  S1's except for the axis constants) onto `SPINDLE_AXIS=(0,0,-1)`, `BAR_AXIS=(0,1,0)`. This is the
  pool's own proof that the drive module is **axis-portable**: drive geometry is a pure function of
  `(spindle_axis, spindle_rear, bar_axis)`. The template adopts S2's convention as the single canonical
  body frame (§13) and re-bases S1/S3/S5/S6/S7/S8's in-plane casting profiles into it by one rigid
  rotation. No primitive, part, joint or proportion changes under that re-basing.
- **S1's diagonal spindle axis is a photo-matching pose, not structure.** S1 L19-L43 rotates the source
  axis by −45° purely to match the product photograph; S1's own test (L420-L427) checks the rotation, not
  a mechanism. Re-basing S1's profile so its spindle lands on −Z maps S1's `BAR_AXIS=(0,0,1)` (the casting
  normal) onto world `(0,1,0)` — **exactly S2's `BAR_AXIS`**. The two records reconcile to one frame.
- **Every fork keeps the aligned driver + visible reaction path** (map's Blocked/Excluded contract).
- **The pool leans on `allow_isolated_part`** (S1 L483-L496, L536-L542; S2 L606-L642) because the
  carriage/hub/t-bar are clearance-fit in bores. That is a **record-level** allowance, FORBIDDEN for
  production templates (AUTHORING Rule 7 / §B). The template replaces it with deliberate capture
  interference (§13 band table) so `fail_if_isolated_parts` passes on real contact.
- **Two source defects must NOT be copied** (found by reading, retained from the prior draft): S2's
  drive geometry is authored in world coordinates *and* the joint origin repeats `SPINDLE_REAR`, so the
  carriage AABB floats ~0.15 m off the frame (§13); S7's guide slot is shorter than its own travel.

## 核心身份

A **chain separator (chain breaker / chain pin press)**: a hand or bench tool that pushes a rivet pin out
of a roller-chain link. Its physical content is exactly three things, and all three must be present in
every seed:

1. a **rigid reaction frame** carrying the load in a closed path;
2. an **aligned driver** — one pin-pusher advancing along a single working axis (PRISMATIC `driver_feed`);
3. a **chain cradle / anvil** on that same axis, so the reaction path visibly closes
   `driver → chain → cradle → frame → driver`.

Leverage (T-bar screw / ratchet / compound toggle) and mounting (handheld grip, bench foot, bolt flange)
are the parameterized layers. The mature domain is the 60–200 mm hand/bench tool scale seen across all 8
records. Anything that breaks the single-driver / single-reaction-path reading is out of category:
no opposed flat jaws, no shear edge, no tensioning arm around a sprocket — the driver **pushes a pin**,
it does not clamp or cut.

## 槽位 + 候选模块表

### Slot A：`frame_form` — reaction-frame skeleton + primary envelope (① 骨架 + ③ 主体形态家族，双记账)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `compact_cast_handheld` | origin_anchor | S1 `rec_picturex_0611__chain_separator__001__png_21cece9ed04f4870b0d43f804d878f13` | L65-L158 (`_frame_shape`: handle polygon+2×`threePointArc` L68-L79, cast head polygon L82-L95, oval hanging hole L99-L102, open cradle cut L106-L110, sleeve L126-L133, spindle bore L138-L145, stiffener rib L149-L157) | eligible if compatible | ③ **Planar Boundary Form**. One continuous casting: sculpted 2D silhouette extruded to a flat 16 mm body; integral grip with an oval hanging hole; U-throat entered from one edge. Handheld, no ground contact. |
| `bench_c_frame` | forked_anchor | S2 `rec_picturex0611_chain_separator_fork_bench_c_frame_20260714` | L26-L56 (canonical axis + layout constants), L78-L221 (`_frame_shape`: column L81-L86, upper arm L89-L95, lower arm L98-L104, bolting foot L107-L112, gussets L117-L135, 4 bolt holes L138-L151, spindle bore L154-L160, sleeve boss L163-L170) | eligible if compatible | ③ **Volumetric Envelope Form**. Deep-throat C: tall back column + two forward arms + flat bolting foot; boxed volumes, not a flat silhouette. Grounded on the foot. Same part tree; new envelope and support. |
| `twin_cheek_plates` | forked_anchor | S3 `rec_picturex0611_chain_separator_fork_twin_plate_bridge_20260714` | L45-L54 (plate layout constants), L76-L151 (`_cheek_plate_shape`), L154-L212 (`_build_spacers`: transition rib L163-L169, 2 bridge pins L173-L179, spindle sleeve tube L184-L194, 2 anvil bridge blocks L197-L210), L331-L347 (visual emission) | eligible if compatible | ③ **Macro Surface Construction**. The solid casting becomes TWO thin parallel cheek plates + a discrete spacer set bridging an open chain channel. Same part tree (all `frame` visuals, Rule 1) but the body reads as an assembled plate-and-post skeleton. |
| `flanged_bench_pedestal` | forked_anchor | S8 `rec_picturex0611_chain_separator_fork_mounting_flange_20260714` | L65-L157 (shared S1 casting), L159-L216 (flange plate L163-L176, 4 bolt holes L178-L194, 2 cast gussets L196-L215), L323-L346 (frame meta) | eligible if compatible | ③ **Planar Boundary Form + grounded pedestal**. S1's silhouette with a broad grounded foot plate fused below the head, four drilled bolt holes, two cast gussets. Grounded but flat-bodied — distinct from S2's boxed C envelope. |

Slot A candidate count = **4** (≥3 ✓). All source-backed with exact line ranges. **形态主导声明**: this
category's ③ Primary Form Family slot is `frame_form` — it is registered in `slot_choices` and each
candidate carries a `form_subtype` tag. It simultaneously scores ① (the source map's six-axis record marks
these as skeleton changes); a module hitting several axes is recorded once per axis (§8.5).

### Slot B：`drive_form` — leverage / actuation mechanism (② 关节类型, + ① for the toggle branch)

Every candidate emits exactly **3 parts + 3 joints** and keeps the PRISMATIC `driver_feed` on the shared
working axis; they differ in what the edges below it *are*.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `screw_tbar` | origin_anchor | S1 | L161-L182 (`_spindle_carriage_shape`: tenon, shaft, 7 thread crests L173-L177, thrust collar, guide neck, cone pin), L185-L221 (`_blue_spindle_hub_shape`, drilled twice), L224-L243 (`_blue_slide_bar_shape` + 2 end balls), L328-L370 (`driver_feed` PRISMATIC L328-L337, `spindle_turn` REVOLUTE ±2π L338-L352, `t_bar_slide` PRISMATIC ±30 mm L353-L370). Axis-portable restatement: S2 L224-L309 + L405-L447 | eligible if compatible | Screw feed, chain **P→R→P**: `driver_carriage` (threaded spindle) → `spindle_hub` REVOLUTE about the spindle axis → `t_bar` PRISMATIC through a drilled transverse bore, retained by enlarged end balls. |
| `ratchet_socket` | forked_anchor | S4 `rec_picturex0611_chain_separator_fork_ratchet_socket_drive_20260714` | L49-L68 (pivot/handle constants), L176-L194 (carriage, shared), L200-L260 (`_ratchet_head_shape`: body, knurl ring L213-L219, pivot boss L221-L229, selector nub L231-L241, axial bore, pivot hole L252-L258), L266-L295 (`_handle_steel_shape`), L298-L309 (`_handle_grip_shape`), L411-L450 (`ratchet_fold` REVOLUTE 0..1.8 L436-L450), L608-L654 (capture allowance idioms) | eligible if compatible | Ratchet drive, chain **P→R→R**: `driver_carriage` → `ratchet_head` REVOLUTE about the spindle axis → `ratchet_handle` REVOLUTE **fold** about the body normal (steel bar + rubber overmold grip). Replaces the T-bar's sliding DOF with a folding one — the ② definition (same graph position, different edge label/axis). |
| `compound_toggle` | forked_anchor | S5 `rec_picturex0611_chain_separator_fork_toggle_lever_drive_20260714` | L46-L91 (linkage layout + derivation formulas), L205-L214 (frame pivot boss), L222-L273 (`_driver_carriage_shape`: smooth rod + toggle pin), L275-L314 (`_toggle_lever_shape`: arm, toggle boss L299-L305, pivot hole L309-L310), L321-L352 (`_toggle_link_shape`, pin holes both ends), L444-L488 (`driver_feed` L444-L453, `lever_pivot` REVOLUTE 0..1.0 on the **frame** boss L457-L471, `toggle_joint` REVOLUTE −0.4..0.6 L474-L488), L644-L680 (pivot clearance idioms) | eligible if compatible | Toggle linkage, **① re-root**: the carriage becomes a smooth rod with a toggle pin; `toggle_lever` is a REVOLUTE child of the **frame** (not the carriage); `toggle_link` is a REVOLUTE child of the lever. The frame gains a second branch — a genuinely different kinematic graph, not only a relabelled edge. Open-chain expression (no closed loop; URDF-legal). |

Slot B candidate count = **3** (≥3 ✓).

### Slot C：`cradle_form` — chain cradle / anvil (①/②/③)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `stepped_ledge_anvil` | origin_anchor | S1 | L106-L110 (open throat cut: rect + rounded root L109-L110), L112-L123 (stepped ledges: `upper_ledge` 10×5 mm, `lower_ledge` 13×6 mm) | eligible if compatible | ③ **Planar Boundary**. Static: an open U-throat with a rounded root plus two asymmetric stepped ledges projecting locally into the throat. Emitted as `frame` visuals (Rule 1 — they do not articulate). **0 extra parts.** |
| `grooved_pad_anvil` | forked_anchor | S2 | L172-L209 (groove cut L180-L185, cylindrical rounded root L188-L194, 2 raised anvil pads spanning the full arm width L197-L209) | eligible if compatible | ③ **Macro Surface Construction**. Static but a different seat construction: a narrow seating **groove** milled into the throat floor with a cylindrical rounded root, flanked by two raised pads spanning the full body width. Emitted as `frame` visuals. **0 extra parts.** |
| `rotating_seat_turret` | forked_anchor | S6 `rec_picturex0611_chain_separator_fork_rotating_anvil_turret_20260714` | L45-L60 (turret constants + `TURRET_NOTCH_SPECS`: 3 seats @120° = 1/8″ / 3/32″ / 11-speed), L82-L109 (`_v_notch_solid` shared pocket/seat helper), L159-L197 (frame pocket + web + pivot pin + tie ribs), L235-L264 (`_anvil_turret_disk_shape`: disk + central bore + 3 V-notch pockets), L267-L281 (`_seat_insert_shape` press-fit inserts), L453-L478 (part + visuals), L523-L541 (`turret_index` REVOLUTE 0..2π) | eligible if compatible | ① + ②. Adds a real articulated part: `anvil_turret`, a bored disk indexing about the body normal on a frame pivot pin, carrying 3 press-fit V-seat inserts as host visuals. **+1 part, +1 REVOLUTE joint.** |

Slot C candidate count = **3** (≥3 ✓). Both static candidates are ③ Primary-Form distinctions of the same
functional layer — legal per `SPEC_TEMPLATE.md` §4 ("换不同 planar boundary / macro surface construction
做 candidate 是合法的结构差异") and `VISUAL_DIVERSITY_MODEL.md` §4.

### Slot D：`chain_guide` — chain-width guide (①/②)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | origin_anchor | S1 (+ S2 / S8 baseline) — the pool's default: 7 of 8 records have no guide | S1 L246-L371 (complete `build_object_model`: frame + drive only, no guide part); S2 L312-L448; S8 L305-L436 | eligible if compatible | No guide layer; the chain is located by the cradle alone. **0 extra parts.** |
| `sliding_cheek_guide` | forked_anchor | S7 `rec_picturex0611_chain_separator_fork_adjustable_chain_guide_20260714` | L44-L52 (`TRANSVERSE_AXIS` derivation + `GUIDE_ORIGIN`), L121-L130 (frame transverse rail slot cut), L244-L306 (`_guide_carriage_shape`: base plate L264-L268, rail tongue L271-L275, 2 straddling cheeks L277-L288, lock knob L291-L296), L372-L383 (part + `guide_body` visual), L473-L490 (`guide_slide` PRISMATIC ±8 mm transverse) | eligible if compatible | ① + ②. Adds `guide_carriage`: a complete plate + rail tongue riding a transverse frame slot, two parallel cheeks straddling the chain channel, and a lock knob. **+1 part, +1 PRISMATIC joint** on an axis **perpendicular** to the driver. |

Slot D candidate count = **2**. **Degrade reason (documented, per §4 硬约束):** the 8-record pool contains
exactly ONE guide design (S7). A second *structurally distinct* guide (pivoting gate, screw adjuster)
exists in neither the origin nor any fork; inventing one would violate AUTHORING Rule 3 (①/② candidates
must be source-backed) and `VISUAL_DIVERSITY_MODEL.md` §6 (①/② may not be world-knowledge-extrapolated).
The slot is kept at 2 with `none` as the pool-majority default rather than folded into `cradle_form`,
because the guide is a physically separate functional layer with its own joint, its own frame interface,
and its own attachment station — folding it in would make Slot C six half-overlapping candidates and
couple two independent attachment points. Precedent: `tube_cutter.secondary` (`none`/`fold_out_reamer`),
`rivet_squeeze.return_spring_style` (`torsion_coil`/`leaf`/`none`).

## Form Dependency Contracts

None. **No ③ candidate in this spec is a controlled world-knowledge extrapolation** — all four
`frame_form` values and all three `cradle_form` values are direct `origin_anchor` / `forked_anchor`
source-backed forms with exact line ranges (§4). §4.1 therefore has no rows to fill.

The one shape-coupling that *does* exist is handled as a plain single-sourced derivation (Contract 3c),
not as an extrapolation contract: `cradle_channel_w` is owned by the resolved `frame_form` and consumed by
`rotating_seat_turret` (turret thickness) and `sliding_cheek_guide` (cheek gap). See §7 / §13.

## 槽位图（slot graph）

pattern: `mixed`

```text
                                     ┌─[REVOLUTE turret_index, axis=b=(0,1,0), iface: frame
                                     │   `turret_pivot_pin` ↔ turret central bore (capture),
                                     │   0..2π]────────> anvil_turret        (Slot C: rotating_seat_turret only)
                                     │
frame (root, Slot A) ────────────────┤
  · owns working axis a=(0,0,-1)     ├─[PRISMATIC guide_slide, axis=(1,0,0), iface: frame
  · owns body normal   b=(0,1,0)     │   `guide_rail_slot` face ↔ guide `rail_tongue` face
  · owns cradle_top_z / channel_w    │   (REAL MatingContract), ±8mm]──> guide_carriage
  · owns nut_boss / pivot anchors    │                                    (Slot D: sliding_cheek_guide only)
                                     │
                                     ├─[PRISMATIC driver_feed, axis=a, iface: frame `spindle_nut_boss`
                                     │   tapped bore ↔ carriage thread crests (0.4mm interference),
                                     │   -5..+12mm]───> driver_carriage      (Slot B: all)
                                     │                        │
                                     │                        ├─[REVOLUTE spindle_turn, axis=(0,0,1),
                                     │                        │   ±2π]──> spindle_hub | ratchet_head
                                     │                        │                 │
                                     │                        │   screw_tbar:   └─[PRISMATIC t_bar_slide,
                                     │                        │                     axis=b, ±30mm]──> t_bar
                                     │                        │   ratchet_socket:└─[REVOLUTE ratchet_fold,
                                     │                        │                     axis=b, 0..1.8]──> ratchet_handle
                                     │                        │
                                     │                        └─(compound_toggle: carriage is a smooth rod;
                                     │                           no child on the carriage)
                                     │
                                     └─[REVOLUTE lever_pivot, axis=-b=(0,-1,0), iface: frame
                                         `lever_pivot_boss` ↔ lever pivot hole, 0..1.0]──> toggle_lever
                                                                             │        (Slot B: compound_toggle)
                                                                             └─[REVOLUTE toggle_joint, axis=-b,
                                                                                 -0.4..0.6, iface: lever
                                                                                 `toggle_boss` ↔ link pin hole]
                                                                                 ──> toggle_link
```

- **Slot order / parenthood.** `frame_form` is the root, resolved first; it publishes the shared anchor
  set (§13). Slots B/C/D attach to `frame` (parallel children); Slot B additionally builds a serial chain
  of depth 2 below `driver_carriage` (or, for `compound_toggle`, a second frame branch of depth 2 below
  `toggle_lever`).
- **Interface basis (frame layout triple).** working axis `a=(0,0,-1)`, body normal `b=(0,1,0)`,
  transverse `h=a×b=(1,0,0)`. Identical for **all four** frame_forms — this is the whole point of the
  canonical body frame (§13) and is what makes the compatibility matrix empty.
- **Interface points.** driver: the frame's tapped `spindle_nut_boss` bore, coaxial with `a` (thread
  flank contact plane). turret: the frame's `turret_pivot_pin` (pin-through-bore). guide: the frame's
  `guide_rail_slot` face (rail/tongue, axis-aligned → real `MatingContract`). lever: the frame's
  `lever_pivot_boss` (pin-through-hole).
- **Capture policy.** Every cross-slot joint except `guide_slide` is a captured fit (pin-in-hole /
  rod-in-sleeve / disk-in-pocket). Per AUTHORING Rule 2 they omit `mating=` (grandfather) and instead
  establish real contact via a deliberate 0.1–0.4 mm interference band (§13), proved by element-scoped
  `allow_overlap` + `expect_overlap` (idioms migrated from the source records' tests).
- **Mutual exclusion / derivation.** `anvil_turret` exists only for `rotating_seat_turret`;
  `guide_carriage` only for `sliding_cheek_guide`; static cradle candidates emit host visuals only.
  `t_bar` vs `ratchet_handle` are mutually exclusive (same station). Turret thickness and guide cheek gap
  are **derived from** Slot A's `cradle_channel_w` — Slot A → C/D is a one-way derivation edge.

## 每槽位 Module Emits / Interfaces

### Slot A / module `compact_cast_handheld`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root). visuals: `frame_casting` (mesh_from_cadquery: silhouette polygon + 2 `threePointArc`, hanging hole cut, throat cut, spindle bore cut), `spindle_nut_boss` (tapped sleeve — a **separate named visual**, not fused, so the thread contact is element-scoped), `stiffener_rib` | S1 / L65-L158, L264-L283 |
| internal joints | none (one continuous casting; grip / rib / hole are fused visuals — Rule 1) | S1 / L96-L157 |
| upstream interface | none (root; handheld, no ground-contact requirement) | S1 / L264-L283 |
| downstream interface | `spindle_nut_boss` tapped bore (coaxial with `a`) → `driver_feed`; `cradle_reaction_z` → cradle; `lever_pivot_boss` → toggle lever; `guide_rail_slot` face → guide; `turret_pivot_pin` → turret | S1 / L126-L145 |

### Slot A / module `bench_c_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root). visuals: `frame_casting` (column + arms + foot + gussets, bolt holes cut, spindle bore cut), `spindle_nut_boss` (underside sleeve boss), `cast_rib_{0..2}` | S2 / L78-L221, L331-L355 |
| internal joints | none (single casting) | S2 / L114-L135 |
| upstream interface | ground contact plane at z=0 (foot underside) | S2 / L107-L112 |
| downstream interface | the same five anchors, re-derived from the C-frame layout constants | S2 / L26-L56, L154-L170 |

### Slot A / module `twin_cheek_plates`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root). visuals: `cheek_plate_0`, `cheek_plate_1` (mirrored thin plates), `spacer_transition`, `spacer_pin_0`, `spacer_pin_1`, `spindle_nut_boss` (= S3's `spacer_sleeve` role), `spacer_anvil_upper`, `spacer_anvil_lower` | S3 / L45-L54, L76-L212, L331-L347 |
| internal joints | none — every plate and spacer is a `frame` visual (Rule 1) | S3 / L331-L347 |
| upstream interface | none (handheld) | S3 / L312-L330 |
| downstream interface | `spindle_nut_boss` bore → `driver_feed`; **the inter-plate gap IS `cradle_channel_w`** | S3 / L45-L54, L184-L194 |

### Slot A / module `flanged_bench_pedestal`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root). visuals: `frame_casting` (S1 silhouette + flange plate + 4 bolt holes + 2 gussets), `spindle_nut_boss`, `stiffener_rib` | S8 / L65-L217, L323-L346 |
| internal joints | none | S8 / L163-L215 |
| upstream interface | ground contact plane at the flange underside | S8 / L163-L176 |
| downstream interface | the same five anchors | S8 / L126-L145 |

### Slot B / module `screw_tbar`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `driver_carriage` (`spindle_shaft`, `spindle_thread`, `thrust_collar`, `guide_neck`, `pin_cone`), `spindle_hub` (`hub_body`, drilled twice), `t_bar` (`bar_shaft`, `bar_stop_0`, `bar_stop_1`) | S1 / L161-L243, L284-L326 |
| internal joints | `driver_feed` PRISMATIC axis `a` [-0.005, +0.012]; `spindle_turn` REVOLUTE axis `a` [-2π, 2π]; `t_bar_slide` PRISMATIC axis `b` [-0.030, 0.030] | S1 / L328-L370; S2 / L405-L447 |
| upstream interface | carriage thread crests inside the frame's `spindle_nut_boss` tapped bore, 0.4 mm interference ⇒ real thread-flank contact. **Geometry authored in the joint-local frame** (from local 0 along `a`) — fixes S2's double-offset defect (§13) | S1 / L138-L145 + L173-L177 |
| downstream interface | hub axial bore around the carriage tenon; hub transverse bore around the bar; cone tip aimed at the cradle centerline | S1 / L179-L181, L185-L221 |

### Slot B / module `ratchet_socket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `driver_carriage` (same 5 visuals, shared helper), `ratchet_head` (`head_body`, `knurl_ring`, `pivot_boss`, `selector_nub`), `ratchet_handle` (`handle_bar`, `handle_grip`) | S4 / L176-L309, L358-L408 |
| internal joints | `driver_feed` PRISMATIC `a`; `spindle_turn` REVOLUTE `a` [-2π, 2π]; `ratchet_fold` REVOLUTE axis `-b` [0, solved] (candidate 1.8; `clamp_joint_limits` solves the realized upper against the head's fold clevis) | S4 / L411-L450 |
| upstream interface | same tapped-bore thread contact | S4 / L155-L159 |
| downstream interface | head `pivot_boss` + drilled pivot hole ↔ handle rounded pivot end; cone tip as above | S4 / L190-L193, L221-L229, L252-L258 |

### Slot B / module `compound_toggle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `driver_carriage` (`driver_rod`, `toggle_pin`), `toggle_lever` (`lever_arm`, `toggle_boss`), `toggle_link` (`link_rod`) | S5 / L222-L352, L402-L439 |
| internal joints | `driver_feed` PRISMATIC `a` [-0.003, +0.010]; `lever_pivot` REVOLUTE **parent=frame** axis `-b` [0, 1.0]; `toggle_joint` REVOLUTE parent=lever axis `-b` [-0.4, 0.6] | S5 / L444-L488 |
| upstream interface | rod in the frame bore (0.2 mm guide-ring interference); lever pivot hole over the frame's `lever_pivot_boss` | S5 / L205-L214, L249-L261, L307-L310 |
| downstream interface | lever `toggle_boss` (r=0.003) ↔ link pin hole (r=0.0035); cone tip as above | S5 / L236-L245, L299-L305, L337-L339 |

### Slot C / module `stepped_ledge_anvil`
| emits | 描述 | 来源 |
|---|---|---|
| parts | none — `frame` visuals `anvil_ledge_upper`, `anvil_ledge_lower` | S1 / L112-L123 |
| internal joints | none (static — Rule 1) | S1 / L112-L123 |
| upstream interface | fused into the frame throat walls | S1 / L123 |
| downstream interface | reaction face at `cradle_reaction_z`, on the working axis | S1 / L106-L123 |

### Slot C / module `grooved_pad_anvil`
| emits | 描述 | 来源 |
|---|---|---|
| parts | none — `frame` throat-floor groove cut + rounded root + visuals `anvil_pad_0`, `anvil_pad_1` | S2 / L172-L209 |
| internal joints | none (static) | S2 / L197-L209 |
| upstream interface | groove milled into the frame throat floor; pads span the full body width so they stay fused to the arm | S2 / L199-L202 |
| downstream interface | reaction face at the groove root, on the working axis | S2 / L188-L194 |

### Slot C / module `rotating_seat_turret`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `anvil_turret` (`turret_disk` + `seat_insert_{0,1,2}`); the frame additionally emits a `turret_pivot_pin` visual + pocket | S6 / L159-L197, L235-L281, L453-L478 |
| internal joints | `turret_index` REVOLUTE axis `b` [0, 2π], origin at the frame turret pocket center; `qc_sample_values` = the three index angles | S6 / L523-L541 |
| upstream interface | turret central bore over the frame `turret_pivot_pin` (0.3 mm interference ⇒ contact). Disk thinned to `cradle_channel_w − 0.0012` and the frame tie-webs kept off the rotation envelope — fixes S6's rib/disk constant overlap (§13) | S6 / L50-L51, L250-L257 |
| downstream interface | the seat facing the throat at q=0 presents the reaction V-notch on the working axis | S6 / L54-L60 |

### Slot D / module `sliding_cheek_guide`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `guide_carriage` (`guide_base`, `rail_tongue`, `guide_cheek_0`, `guide_cheek_1`, `lock_knob`) | S7 / L244-L306, L372-L383 |
| internal joints | `guide_slide` PRISMATIC axis `h=(1,0,0)` [-0.008, +0.008] | S7 / L473-L490 |
| upstream interface | `rail_tongue` top face ↔ frame `guide_rail_slot` bottom face — **axis-aligned ⇒ real `MatingContract`** (+`tangential_containment=True`). Slot length derived (§7), fixing S7's too-short slot (§13) | S7 / L121-L130, L271-L275 |
| downstream interface | none (terminal); the two cheeks center the chain channel on the cradle | S7 / L277-L289 |

### Slot D / module `none`
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | S1 / L246-L371 |
| internal joints | none | S1 / L328-L370 |
| upstream interface | none | — |
| downstream interface | none | — |

## 活动机构与运动净空契约

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| `driver_carriage` (all Slot B) | full threaded spindle: tenon + shaft + 7-crest thread collar + thrust collar + guide neck + cone pin (S1 L161-L182); toggle variant: rod + rear stop disk + toggle pin + guide rings (S5 L222-L273). Not a facade. | frame `spindle_nut_boss` tapped bore, coaxial, wrapping the crest collar over its full length | thread flanks — crest r 0.0095 vs **nut-boss bore r 0.0082** (`_NUT_BORE_R`) ⇒ **+1.3 mm interference** ⇒ real contact, NO `allow_isolated_part`. (The casting's own clearance bore is `_ARM_BORE_R = crest + 0.0005 = 0.0100` and deliberately does NOT touch the crests.) `compound_toggle` instead engages via two guide rings at `_NUT_BORE_R + 0.0003` | origin = `spindle_rear` on axis `a`; axis `a=(0,0,-1)`; [-0.005, +0.012·s] (S1 L335 / S2 L412); toggle [-0.003, +0.010] (S5 L451) | closed q=-0.005: cone tip ≥ 4 mm above `cradle_reaction_z`; max q=+0.012: tip enters the throat toward the seat, still ≥ 1 mm clear (inequality §7) | `spindle_nut_boss` ↔ `spindle_thread` (thread flank) | `fail_if_parts_overlap_in_sampled_poses`; targeted `ctx.pose({driver_feed: upper})` asserts displacement along `a` only |
| `spindle_hub` / `ratchet_head` | drilled hub: body + (ratchet: knurl ring + pivot boss + selector nub); two real bores | carriage tenon inside the hub axial bore (pin-in-sleeve) | captured pin — **omits `MatingContract`** (Rule 2 grandfather: pin-through-sleeve is not two axis-aligned faces). tenon r 0.0050 vs bore r 0.0047 (+0.3 mm) | origin (0,0,0) in carriage frame; axis `a`; [-2π, 2π] (S1 L345-L350); `qc_sample_values=[-π/2,0,π/2,π]` (default ±2π sampling degenerates) | full ±2π: the hub is a body of revolution about its own joint axis ⇒ swept envelope = the hub itself; the T-bar/handle child is checked separately | `spindle_thread`/`spindle_shaft` ↔ `hub_body` / `head_body` (concentric capture; mirrors S1 L497-L512) | sampled poses + `ctx.pose({spindle_turn: π})` asserts the child rotates about `a` with no origin drift |
| `t_bar` (`screw_tbar`) | full bar: shaft + two enlarged end-stop balls that cannot pass the bore (S1 L238-L242, L456-L463) | hub transverse drilled bore around the bar | captured pin-in-bore — omits `MatingContract`. bar r 0.0055 vs bore r 0.0052 (+0.3 mm) | origin (0,0,0) in hub frame; axis `b=(0,1,0)`; [-0.030·s, +0.030·s] (S1 L358-L364) | at ±0.030 one end ball is 38 mm out; the opposite stop stays inside the bore ⇒ retained. Bar sits above the frame body; min clearance ≥ 3 mm across all `spindle_turn` × `t_bar_slide` combos (solver-clamped) | `hub_body` ↔ `bar_shaft` (bore capture) | `clamp_joint_limits('t_bar_slide', keepout=['frame'])`; `ctx.pose({t_bar_slide: upper})` asserts pure `+b` translation |
| `ratchet_handle` (`ratchet_socket`) | steel bar with rounded drilled pivot end + rubber overmold grip (S4 L266-L309) | ratchet head `pivot_boss` through the handle pivot hole | captured pin — omits `MatingContract` (+0.2 mm band) | origin = `PIVOT_LOCAL_XYZ` on the head; axis `b`; [0, 1.8] (S4 L443-L445) | folded q=0: handle lies clear of the frame; q=1.8: handle swings up/over, ≥ 3 mm clear of the frame body (solver-clamped) | `pivot_boss` ↔ `handle_bar` (pin-through-lug) | `clamp_joint_limits('ratchet_fold', keepout=['ratchet_head'], margin < clevis running clearance)`; `ctx.pose({ratchet_fold: solved upper})` asserts the handle's AABB centre rises (stows away from the cradle) — read the AABB centre, NOT `part_world_position`, which returns the frame origin on the joint axis and cannot move under a revolute |
| `toggle_lever` (`compound_toggle`) | full lever: profiled arm with a widened grip end + arc tip + toggle boss + drilled pivot hole (S5 L275-L314) | frame `lever_pivot_boss` through the lever pivot hole | captured pin — omits `MatingContract` (+0.2 mm band) | origin = `lever_pivot_xz` on the frame head; axis `-b=(0,-1,0)`; [0, 1.0] (S5 L462-L469) | q=0 rest (lever out); q=1.0 closed: grip end ≥ 4 mm clear of the frame grip/body (solver-clamped inequality §7) | `lever_pivot_boss` ↔ `lever_arm` (pin-through-hole) | `clamp_joint_limits('lever_pivot', keepout=['frame'])`; `ctx.pose({lever_pivot: upper})` asserts grip-end displacement > 15 mm |
| `toggle_link` (`compound_toggle`) | short connecting rod, arc ends, pin holes both ends (S5 L321-L352) | lever `toggle_boss` (r 0.003) inside the link hole (r 0.0035) | captured pin — omits `MatingContract` (+0.2 mm band) | origin = `TOGGLE_JOINT_IN_LEVER`; axis `-b`; [-0.4, 0.6] (S5 L481-L486) | full range × full `lever_pivot` range: the link stays in the offset plane beside the carriage, ≥ 2 mm clear of the frame | `toggle_boss` ↔ `link_rod` (pin-through-hole) | sampled poses over the `lever_pivot × toggle_joint` product; `ctx.pose` asserts the link tracks the lever |
| `anvil_turret` (`rotating_seat_turret`) | bored disk + 3 press-fit V-seat inserts; a real indexing body, not a marker (S6 L235-L281) | frame `turret_pivot_pin` through the turret central bore; disk seated in a frame pocket (S6 L159-L197) | captured pin — omits `MatingContract`. pin r 0.0036 vs bore r 0.0033 (+0.3 mm) | origin = turret pocket center; axis `b`; [0, 2π] (S6 L529-L534); `qc_sample_values=[0, 2π/3, 4π/3]` | full turn: the disk is a body of revolution about its own axis ⇒ each seat indexes to the throat with ≥ 1 mm clearance to the driver cone at `driver_feed=0`; thickness derived from `cradle_channel_w` so it never binds the channel walls | `turret_pivot_pin` ↔ `turret_disk` (pin-in-bore); `turret_disk` ↔ `seat_insert_i` are same-part visuals (press fit — no cross-part allowance needed) | `ctx.pose({turret_index: 2π/3})` asserts seat 1 indexes to the throat; sampled poses |
| `guide_carriage` (`sliding_cheek_guide`) | complete plate: base + rail tongue + two straddling cheeks + lock knob (S7 L244-L306) | frame `guide_rail_slot` — a real transverse slot the `rail_tongue` rides in (bilateral slot walls) | **real `MatingContract`**: parent `guide_rail_slot` `negative_z` face ↔ child `rail_tongue` `positive_z` face (axis-aligned) + `tangential_containment=True`; base embedded 0.2 mm into the slot floor | origin = `guide_seat_z` on the frame; axis `h=(1,0,0)`; [-0.008·s, +0.008·s] (S7 L483-L484) | ±8 mm: the tongue stays inside the slot's X length (inequality §7: slot_len derived as `base_len + 2·travel + margin`, fixing S7's defect); cheeks stay clear of the driver cone at all `driver_feed` values | `guide_rail_slot` ↔ `rail_tongue` (close-fit rail contact) | `fail_if_joint_mating_has_gap` + `tangential_containment`; `ctx.pose({guide_slide: ±upper})` asserts pure ±`h` translation |

**No whole-part `allow_overlap` and no `allow_isolated_part` appears anywhere in this spec** (contrast:
the source records use both — §2 reading notes; Reject case 1).

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | `compact_cast_handheld` / `bench_c_frame` / `twin_cheek_plates` / `flanged_bench_pedestal` | `compact_cast_handheld` | choice | deterministic procedural sampler `rng.choices`, weights 5/4/4/3 | §4 Slot A |
| `drive_form` | enum | `screw_tbar` / `ratchet_socket` / `compound_toggle` | `screw_tbar` | choice | deterministic procedural sampler, weights 5/4/4 | §4 Slot B |
| `cradle_form` | enum | `stepped_ledge_anvil` / `grooved_pad_anvil` / `rotating_seat_turret` | `stepped_ledge_anvil` | choice | deterministic procedural sampler, weights 5/4/4 | §4 Slot C |
| `chain_guide` | enum | `none` / `sliding_cheek_guide` | `none` | choice | deterministic procedural sampler, weights 5/3 (pool ratio 7:1, without starving the guide) | §4 Slot D |
| `palette_style` | enum | `black_blue_enamel` / `blue_enamel_bench` / `forged_steel_natural` / `zinc_hardware` / `black_rubber_shop` | `black_blue_enamel` | choice | `rng.choice(PALETTE_STYLES)`; resolves to a `mats[...]` dict driving EVERY `.visual(material=...)` | §8.5 ⑥ |
| `overall_scale` | float | [0.88, 1.14] | 1.0 | independent | uniform sample, clamp | S1 L65-L158 / S2 L30-L56 (tool envelope 60–200 mm) |
| `body_thickness_scale` | float | [0.88, 1.18] | 1.0 | independent | uniform sample, clamp | S1 L66 `thickness=0.016`; S2 L34 `COLUMN_DEPTH` |
| `throat_depth_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform sample, clamp | S1 L106-L110; S2 L37 `ARM_LENGTH` |
| `handle_len_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform sample, clamp | S1 L227 (bar half-length 0.068); S4 L62 `HANDLE_LENGTH`; S5 L56 `LEVER_LENGTH` |
| `feed_travel_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform sample, clamp | S1 L335; S2 L412 |
| `body_half_y` | float | derived | — | equation | `= 0.008 · body_thickness_scale · overall_scale` (S1 `thickness/2`) | S1 L66 |
| `cradle_channel_w` | float | derived | — | equation | `= f(frame_form)`: solid frames → `2·body_half_y` (through-slot); `twin_cheek_plates` → `PLATE_GAP·body_thickness_scale`; `bench_c_frame` → `0.010·body_thickness_scale`. **Single source of truth** — consumed by turret thickness and guide cheek gap | S1 L106 / S2 L176 / S3 L47 |
| `turret_thickness` | float | derived | — | equation | `= cradle_channel_w − 0.0012` (running clearance); never sampled independently | S6 L48 (`TURRET_THICKNESS=0.016` = S1's full body thickness) |
| `guide_cheek_gap` | float | derived | — | equation | `= cradle_channel_w` (the cheeks straddle the same channel) | S7 L259 (`cheek_gap=0.010`) |
| `guide_slot_len` | float | derived | — | equation | `= guide_base_len + 2·guide_travel + 0.003·overall_scale` (fixes S7's slot < travel defect) | S7 L121-L130, L251-L275 |
| `feed_travel` | float | derived | — | equation | upper `= 0.012 · feed_travel_scale · overall_scale`; lower `= -0.005 · overall_scale`; `compound_toggle` clamps upper ≤ 0.010 (open-chain toggle geometry). Further bounded by the three inequalities below — every bound is a relation to the cradle the pin drives into, never a tuned literal | S1 L335 / S2 L412 / S5 L451 |
| `tip_rest_clear` | float | derived | — | equation | `= chain_stack_h + chain_load_clear = 0.0071 + 0.0030`. The retracted pin must clear a chain laid on the seat or the tool cannot be loaded; 0.0071 m is a 1/2"-pitch roller-chain plate height (ANSI #41). Fixes `spindle_rear_z`, hence the whole driver stack | real chain dimension |
| `shaft_core_len` | float | derived | — | equation | `= _C_NECK_T − _C_SHAFT_T = 0.078` — the core shaft ends where the guide neck begins, so the neck→cone step is the only thing entering the cradle. S1 L169's literal 0.100 runs the 8.4 mm core to 1 mm from the tip and buries the thrust collar/neck/cone inside it; harmless in S1 only because S1's spindle misses its own anvil by ~31 mm | S1 L169-L181 + §13 correction |
| `thread_band_t` | float | derived | — | equation | `= _C_THRUST_T − 0.004 − _C_THREAD_L = 0.055` — the crest band sits just behind the thrust collar so it lands inside the arm-fused nut boss. S1 L173 stations it 0.018 from the spindle rear because S1's sleeve sits there; on the canonical centreline that puts the crests ~30 mm above the arm | S1 L173-L177 |
| `nut_boss_z0/z1` | float | derived | — | equation | `z0 = throat_z1` (fused through the realized upper arm, never hanging into the throat); `z1 = thread_band_z1 − feed_lower + 0.004` (still houses the band at full retract). Replaces the literal `_NUT_T0/_NUT_T1 = 0.030/0.077`, which let the boss drift off the arm it must be fused to | S1 L126-L133 |
| `arm_bore_r` | float | derived | — | equation | `= _C_CREST_R + 0.0005 = 0.0100` — the casting's clearance bore must CLEAR the crests; only the tapped boss engages them. S1 L139 bore 0.0091 vs S1 L176 crest 0.0086 is exactly this +0.5 mm relation; this template raised the crest to 0.0095 for the nut fit, so a copied 0.0091 made the crests bite the casting | S1 L139 vs L176 |
| `turret_center_z` | float | derived | — | equation | `= cradle_z − turret_radius`, i.e. the disk's **crown sits on the cradle seat plane**, like every other cradle_form's seat surface. A literal `−0.006` put the crown 7 mm above the datum — above the retracted pin — so the driver was buried in the anvil before the joint moved | Contract 3c |
| `guide_seat_x` | float | derived | — | equation | `= clamp(cradle_outboard_x + guide_base_len/2 + guide_travel + 0.0015, …, lower_arm_x1 − …)`, where `cradle_outboard_x` is the realized cradle's +x anvil extent (ledges / pads / turret pocket). The literal `0.0365` was annotated "clear of the anvil" but grooved_pad_anvil's pad reaches x=0.022 | S7 L121-L130 |
| pin/bore capture fits | float | derived | — | equation | every captured pin derives from its bore: `_ROD_RING_R = _NUT_BORE_R + 0.0003`, `_TURRET_PIN_R = _TURRET_BORE_R + 0.0003`, `_LEVER_PIVOT_R = _LEVER_HOLE_R + 0.0003`, `_TOGGLE_BOSS_R = _LINK_HOLE_R + 0.0003`. Stating a pin radius independently of its bore is what left the toggle rod (−1.0 mm), the lever (−1.5 mm) and the link (−0.5 mm) floating free of the frame | Rule 7 / Contract 3e |
| `t_bar_travel` | float | derived | — | equation | `= 0.030 · handle_len_scale · overall_scale` | S1 L363-L364 |
| `guide_travel` | float | derived | — | equation | `= 0.008 · overall_scale` | S7 L483-L484 |
| `carriage_reach` | float | derived | — | equation | `R = |spindle_rear − cradle_reaction_z| − 0.006`; cone tip / guide neck / thrust collar positioned relative to the tip, thread crests relative to the tail | S1 L161-L182 / S2 L49-L50 |
| (—) | constraint | — | — | inequality | **driver stroke / relief**: only the cone pin may enter the frame's pin-relief bore; the guide neck behind it (r `_C_NECK_R`) is wider than the bore (`_PIN_RELIEF_R`), so `feed_upper ≤ neck_rest_z − relief_mouth_z − 0.001`. Violation ⇒ shrink `feed_upper` | §6.5 |
| (—) | constraint | — | — | conditional | **driver stroke / rotating anvil**: a `rotating_seat_turret` sweeps SOLID through the throat at every index angle and has no through-relief, so it — not the frame's relief bore — is the reaction surface: `feed_upper ≤ tip_rest_clear − 0.0012`, i.e. the pin stops just above the anvil crown, as a real chain tool's pin stops on the anvil face once the rivet is pressed out into the seat notch. This is why the turret is NOT gated against any drive_form | §6.5 / S6 |
| (—) | constraint | — | — | inequality | **thread engagement**: the crest band must still be inside the nut boss at full feed: `feed_upper ≤ band_bottom_rest_z − throat_z1` | S1 L126-L145 |
| (—) | constraint | — | — | inequality | **guide stroke**: `guide_travel ≤ (guide_slot_len − rail_tongue_len)/2 − 0.0005` — the tongue never leaves its slot. Violation ⇒ shrink `guide_travel` | S7 L251-L275 |
| (—) | constraint | — | — | inequality | **turret fit**: `turret_radius + 0.0015 ≤ throat_half_x` and `turret_thickness ≤ cradle_channel_w − 0.001`. Violation ⇒ shrink `turret_radius` | S6 L47-L49 |
| (—) | constraint | — | — | inequality | **T-bar swing clearance (bench frame)**: `spindle_rear_z ≥ column_top·s + bar_stop_r + hub_offset + feed_upper + 0.003` — solved in the layout function so the `spindle_turn` sweep cannot clip the column top. Constructively satisfied | S2 L31-L50 + swing analysis |
| (—) | constraint | — | — | inequality | **lever clearance**: closed `lever_pivot` upper solved by `clamp_joint_limits(..., keepout=['frame'])` so the grip end stays ≥ 4 mm off the frame | S5 L462-L469 |
| (—) | constraint | — | — | inequality | **capture interference band**: thread-crest/nut-bore +1.3 mm, and every other captured pin derived as bore + `_CAPTURE_FIT` (+0.3 mm): tenon/hub-bore, T-bar/hub-bore, turret-pin/turret-bore, rod-ring/nut-bore, lever-pin/lever-hole, toggle-boss/link-hole; guide base embed +0.2 mm — all ≪ the 5 mm `overlap_tol`, constant across travel; guaranteed by construction from the constants | S1/S4/S5/S6/S7 capture fits |
| (—) | constraint | — | — | conditional | `cradle_channel_w`'s formula, `spindle_rear_z`, `nut_boss_z`, `cradle_top_z`, `cradle_reaction_z`, `throat_half_x`, `lever_pivot_xz`, `guide_seat_z` and the ground-contact policy all resolve **from the chosen `frame_form`** before any dependent geometry is built | §13 |

All `equation` / `inequality` / `conditional` constraints are solved inside `resolve_config` (plus the
three `clamp_joint_limits` calls at build time, which mutate only joint limits, never geometry).

## 7.5 编译预算 / compile budget

**Declared budget: ≤ 18 s per seed** (sweep `--compile-timeout 120` ⇒ ~6× watchdog, per AUTHORING §C's
"~3× for heavy categories" as a hang guard, never a quality bar).

Basis: each seed builds 1 sculpted cadquery frame casting (≈8–12 boolean ops: silhouette union, hanging
hole cut, throat cut, bore cut, sleeve/rib/pad unions, optional flange + 4 bolt-hole cuts + 2 gussets)
plus 3–5 small revolved/extruded solids (carriage ≈12 fused primitives, hub 1 cylinder − 2 bores, bar
1 cylinder + 2 spheres, optional turret disk − 3 pockets, optional guide 5 boxes). The 8 source records
compile in this envelope today at `tolerance=0.00035`/`0.00022`; the template is the same geometric order
with one frame casting per seed instead of one per record.

Banded tessellation:
- frame casting (hero surface): `tolerance=0.0006` — coarser than the source's 0.00035 because the
  silhouette is read at tool scale. A tessellation choice, **not** a primitive downgrade
  (`mesh_from_cadquery` is preserved everywhere the source used it — Rule 3).
- small hardware (carriage / hub / bar / turret / links / guide): `tolerance=0.0004`.
- small-radius features (bolt holes, pins, thread crests) resolve to ≤32 segments at these tolerances;
  the frame silhouette arcs to ≤64.
- Shared meshes: the 3 turret `seat_insert_i` share one `_v_notch_solid` helper; the 2 twin-plate cheeks
  share one `_cheek_plate_shape` call per z-center; the 2 bar end-stops share one sphere primitive; the
  threaded carriage mesh is shared by `screw_tbar` and `ratchet_socket`.

If a seed exceeds 18 s, drop the frame tolerance to 0.0009 before touching structure (AUTHORING §C).

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots 表达，不暴露 `*_count`，也不通过循环复制模板级
  visual/part/joint。

This honors the source map's explicit contract: *"No honest articulated N axis exists. Turret seats and
mounting holes are repeated host visuals, not separate articulated parts or template multiplicity
anchors."*

Fixed-count repeated **host visuals** that are NOT multiplicity axes (counts frozen at the source value,
never sampled): 3 turret `seat_insert_i` (S6 L56-L60 — the count encodes the three real chain gauges
1/8″ / 3/32″ / 11-speed, not a free integer); 4 flange bolt holes (S8 L181-L186) / 4 foot bolt holes
(S2 L138-L143); 3 `cast_rib_i` (S2 L212-L219); 2 `spacer_pin_i` (S3 L173-L179); 2 `anvil_pad_i`
(S2 L203-L209); 2 `guide_cheek_i` (S7 L279-L288); 2 `bar_stop_i` (S1 L240-L242); 7 thread crests
(S1 L174-L177).

`raw_domain` therefore equals `core_domain` (72); `multiplicity_coverage` is empty.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | Part-joint kinematic graph varies on three registered slots. `cradle_form=rotating_seat_turret` **adds** the `anvil_turret` part + `turret_index` edge (forked_anchor S6 L453-L478, L523-L541). `chain_guide=sliding_cheek_guide` **adds** the `guide_carriage` part + `guide_slide` edge (forked_anchor S7 L372-L383, L473-L490). `drive_form=compound_toggle` **re-roots** a branch: the lever hangs off the **frame**, not the carriage, giving the frame 2–4 children instead of 1–3 (forked_anchor S5 L457-L471). Realized part counts 4→6, joints 3→5. The reaction skeleton itself varies across 4 source-backed forms (§4 Slot A; the source map marks these ①). All forked_anchor / origin_anchor — none extrapolated. |
| └ multiplicity | 同构件 ×N | **无** | See §8. The source map explicitly rules out an honest N axis; turret seats / bolt holes / ribs / spacer pins / cheek plates / thread crests are fixed-count host visuals, not articulated repeats. No `*_count` parameter is exposed. |
| ② 关节类型 | 图不变，某条边换 type/轴 | **有** | The edge below `spindle_turn` changes label+axis at the same graph position: `screw_tbar` → **PRISMATIC** `t_bar_slide` axis `b` ±30 mm (S1 L353-L370) vs `ratchet_socket` → **REVOLUTE** `ratchet_fold` axis `b` 0..1.8 (S4 L436-L450). Types realized template-wide: **PRISMATIC** (`driver_feed` axis `a`, `t_bar_slide` axis `b`, `guide_slide` axis `h`) and **REVOLUTE** (`spindle_turn` ±2π, `ratchet_fold` 0..1.8, `lever_pivot` 0..1.0, `toggle_joint` −0.4..0.6, `turret_index` 0..2π). Both declared types appear in every sweep (set-cover, §9 weights guarantee reachability). All forked_anchor / origin_anchor. No CONTINUOUS and **no FIXED articulation** is declared (Rule 1: static detail is host visuals). |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | Registered in `slot_choices` on **two** slots; all direct source-backed ⇒ §4.1 has no rows. `frame_form` (the 形态主导 slot): `compact_cast_handheld` = **Planar Boundary Form** (sculpted flat silhouette, polygon + `threePointArc`, S1 L65-L158); `bench_c_frame` = **Volumetric Envelope Form** (boxed column+arms+foot, S2 L78-L221); `twin_cheek_plates` = **Macro Surface Construction** (solid body → 2 thin plates + discrete spacer set across an open channel, S3 L76-L212); `flanged_bench_pedestal` = **Planar Boundary Form + grounded pedestal** (S8 L159-L216). `cradle_form`: `stepped_ledge_anvil` = **Planar Boundary** (S1 L106-L123); `grooved_pad_anvil` = **Macro Surface Construction** (S2 L172-L209); `rotating_seat_turret` = **Volumetric Envelope** (S6 L235-L281). Each candidate carries a `form_subtype` tag in the template. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | `record_only`, all host-conformal, all emitted as `parent.visual(...)`/fused host geometry derived from the host's **final** surface (derive order ③→⑤→④, Rule 4): oval hanging hole (S1 L99-L102), stiffener wedge rib (S1 L149-L157), 7 thread crests (S1 L173-L177), 3 cast column ribs (S2 L212-L219), 4+4 bolt holes (S2 L138-L151 / S8 L178-L194), 2 cast gussets (S8 L196-L215), knurled ratchet grip ring + direction-selector nub (S4 L213-L241), rubber overmold grip (S4 L298-L309), zinc bridge spacers (S3 L154-L212), guide lock knob (S7 L291-L296). Each rides on its host frame_form's realized surface — bolt-hole ring positions, rib z-spans and pad widths are read from the resolved frame dimensions and scale with `plan`/`overall_scale`, never a constant laid over a scaled face. No decoration adds a part, a joint, an interface, or changes the primary primitive. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | **有** | Key ratios (§7): `overall_scale` [0.88,1.14], `body_thickness_scale` [0.88,1.18], `throat_depth_scale` [0.90,1.15], `handle_len_scale` [0.90,1.15], `feed_travel_scale` [0.85,1.15]. **Motion envelopes (axis / opening direction / [closed, feasible-upper])**: `driver_feed` — `a=(0,0,-1)`, advances **down into the cradle**, [-0.005·s, +0.012·s] (toggle [-0.003, +0.010]); `spindle_turn` — `a`, bidirectional, [-2π, +2π]; `t_bar_slide` — `b=(0,1,0)`, slides **through** the hub bore, [-0.030·k, +0.030·k]; `ratchet_fold` — `-b` (NOT `+b`: with `+b` a positive fold swings the handle DOWN into the spindle and frame), stows the handle **back along the spindle rear, away from the cradle**, [0, solved] — candidate 1.8, realized value solved per seed by `clamp_joint_limits` against the head's milled fold clevis; `lever_pivot` — `-b`, swings **toward the frame grip**, [0, 1.0] (solver-clamped); `toggle_joint` — `-b`, follower, [-0.4, +0.6]; `turret_index` — `b`, indexes seats to the throat, [0, +2π]; `guide_slide` — `h=(1,0,0)`, traverses **across** the driver axis, [-0.008·s, +0.008·s]. **motion_test_plan**: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` covers `{0, lower, upper, mid}` per joint plus combos (≤5 non-FIXED joints ⇒ the C′ budget `min(128, max(32, 1+4·5))=32`, raised to 48 for `lever_pivot × toggle_joint` combo depth); **No joint overrides pose sampling.** Earlier drafts set `qc_sample_values` on `spindle_turn` and `turret_index`; the harness rejects that on scalar movable joints (it neuters the motion gate, and is legitimate only on FLOATING joints). Both were removed and the geometry fixed instead: the default `{0, lower, upper, mid}` sweep of `turret_index` over 0..2π samples θ=π, which is NOT an indexed seat position — that is exactly the pose that exposed the anvil crown driving into the driver pin, and it is now clean by construction (`turret_center_z`, §7). Plus one targeted `ctx.pose(...)` per mechanism asserting direction + reachable endpoint (§6.5 validator column). The bench T-bar swing clearance is constructively satisfied by the §7 `spindle_rear_z` inequality. No broad allowance and no sampled-clearance exemption is used. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | **5 colorways**, each a `mats[...]` dict driving EVERY `.visual(material=...)`. Material 大类 realized: **painted** (black cast enamel / blue enamel), **metal** (machined steel, forged steel, zinc), **rubber/plastic** (ratchet overmold grip) ⇒ 3 大类 ≥ `ceil(0.5×5)=3` ✓ (painted+metal appear in every seed; rubber rides `ratchet_socket`). Colorways: `black_blue_enamel` (S1 L260-L262: black_cast + bright_blue_steel + machined_steel), `blue_enamel_bench` (blue body + black accents, S2 L327-L329), `forged_steel_natural` (bare machined/forged, S4 L332-L334), `zinc_hardware` (S3 L307-L310, zinc_spacer-led), `black_rubber_shop` (S5 L374-L376 lever_dark + S4 L334 rubber_grip). All `record_only` (⑥ is recorded, never forked — `VISUAL_DIVERSITY_MODEL.md` §6). |

**收尾自检**: every discrete value above is set-cover selected by `slot_choices_for_seed` (§9) and is
eyeball-verifiable in the final visual QA: ≥3 frame prototypes, all 3 drives, turret + guide each at
least once, ≥3 colorways, the driver cone always pointing at the cradle, and no 穿模 across full travel.
No multiplicity anchors to cover (§8 declares none).

## 采样与覆盖审计

core theoretical：`frame_form(4) × drive_form(3) × cradle_form(3) × chain_guide(2) = 72`
raw theoretical：`72 × (no N axes) = 72`

实际合法组合域：**72 — zero deny rows** (see `## Compatibility Gates`). Legality is proved by
construction rather than by exclusion: all four frame_forms publish the **same anchor contract** on the
**same canonical body frame** (§13), and the two shape-coupled consumers (turret thickness, guide cheek
gap) **derive** from the frame's `cradle_channel_w` instead of restating it — so the combinations that
would otherwise need a deny row (a 16 mm turret inside a 10 mm twin-plate channel) are unconstructible
rather than merely forbidden.

理由：the pool's 7 forks are single-axis by construction — each changed exactly one of
{frame, drive, cradle, guide} while holding the rest at the S1 baseline. That is direct evidence the four
axes are mutually orthogonal at the interface level: every fork **is** a realized cross-combination of its
own axis with the S1 default on the other three, so 8 of the 72 cells are literally the source pool. The
remaining 64 recombine modules from different sources, which AUTHORING §A Rule 3 explicitly permits
("Modules backed by different sources may be recombined and may generate an asset absent from the source
pool; co-occurrence is not required"), subject to interface/dimension/identity/swept-clearance proof —
supplied per-combination by the §7 derivation rules and the §10 validators. This spec **is** the
"downstream interface review" the source map's `Compatibility Probes: None` line defers to; its finding
is that one canonical body frame makes the review vacuous.

seed_domain_policy：`procedural_first`

**Procedural Sampling / Sweep Plan**: `config_from_seed(seed)` builds `random.Random(seed)` and samples,
in order: `frame_form` (weights 5/4/4/3, the origin form slightly favored), `drive_form` (5/4/4),
`cradle_form` (5/4/4), `chain_guide` (5/3), `palette_style` (`rng.choice`, uniform over 5), then the five
continuous scales via `rng.uniform`. **`seed=0` is not special** — identical path (Contract 4). No
compatibility gate can reject a draw (empty deny set), so the sampler needs no retry loop;
`resolve_config` is the single legalization entry and performs only enum validation, clamping, and the §7
derivations/inequality shrinks. No regression overrides. Sweep: `0-15` fast → `16-35` final (36
cumulative) → corner stage.

**Combination Domain**: `core_domain` counts only ①/②/③ and genuine functional modules (the four slots);
`raw_domain` adds bounded integer N — there are none (§8) — so `raw_domain == core_domain == 72`.
`multiplicity_coverage` is empty by declaration. palette (⑥), material 大类, ④ decoration and continuous
⑤ dimensions are excluded from both domains.

**Controlled local parameterization**: `overall_scale`, `body_thickness_scale`, `throat_depth_scale`,
`handle_len_scale`, `feed_travel_scale` (ranges + clamps in §7). All are `independent` draws; every
cross-part quantity they touch (`body_half_y`, `cradle_channel_w`, `turret_thickness`, `guide_cheek_gap`,
`guide_slot_len`, `feed_travel`, `t_bar_travel`, `guide_travel`, `carriage_reach`) is an `equation`
derivation from them, and the six `inequality` rows project the result back into the feasible region
inside `resolve_config`. They cannot break InterfaceSpec/MatingContract (the guide's rail contract derives
from the same `guide_seat_z`), clearance (solver-clamped joints + constructive interference bands), joint
origin (all origins are anchor-derived), or category identity (the aligned driver + cradle reaction path
are structural, not scaled away). No multiplicity to preserve.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order frame→drive→cradle→guide→palette→scales; weighted `rng.choices`; no gates ⇒ no rejection/retry | `slot_choices_for_seed` matches build choices (asserted in `run_tests` via `model.meta["slot_choices"]`) |
| compatibility matrix | **no deny rows**; legality is structural — one canonical body frame, one anchor contract across all frame_forms; turret/guide derive from `cradle_channel_w`; 8 of 72 cells are the source records themselves | interface/dimension/identity/swept-clearance all pass; no unchecked Cartesian product (the product IS the checked domain) |
| controlled local variation | 5 continuous scales, clamped + derived per §7; capture interference bands constant across travel | proportions vary without breaking capture fits, swing clearance, support, joint origin, or category identity |
| regression overrides | none | — |
| random sweep | seeds 0-15 (fast) → 0-35 (final) → corner stage; 0-999 for a later maturity audit | `failure_clusters`; `axis_realization` slot_value_counts confirm every slot value appears; viewer focus = turret indexing + toggle closing + T-bar slide |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 4 | yes | yes | ①+③ 双记账; 4 distinct form prototypes, all source-backed |
| drive_form | 3 | yes | yes | ② edge relabel + ① re-root |
| cradle_form | 3 | yes | yes | 2 static ③ forms + 1 articulated turret |
| chain_guide | 2 | yes | **no** | degrade reason documented in §4 Slot D (pool contains exactly one guide design; ①/② may not be extrapolated) |

## Compatibility Gates

**No deny rows.** All 72 core combinations are admitted. The structural argument is in §9. The three
couplings that would otherwise require gates are dissolved by derivation instead of exclusion:

1. `twin_cheek_plates` × `rotating_seat_turret` — would collide (S6's 16 mm turret vs S3's 10 mm channel).
   **Dissolved**: `turret_thickness = cradle_channel_w − 0.0012` (§7 equation), so the turret is a thin
   indexing disk between the plates with its pivot pin through both cheeks. Derived, not gated.
2. `twin_cheek_plates` / `bench_c_frame` × `sliding_cheek_guide` — the guide's cheek gap must match the
   host channel. **Dissolved**: `guide_cheek_gap = cradle_channel_w` (§7 equation).
3. `bench_c_frame` × `compound_toggle` — the lever needs a pivot boss. **Dissolved**: `lever_pivot_xz` is
   part of the mandatory anchor contract every `frame_form` publishes (§13), so the boss exists on all
   four frames; its realized position is frame_form-conditional (§7 `conditional` row).

Any combination a future sweep proves unbuildable is added here as an explicit deny row with a one-line
reason and removed from `config_from_seed` — never silently dropped (§12).

## Combination Domain

- diversity_profile / reason: `standard` — the honest core vocabulary is 72 gate-legal combos, above the
  standard floor (48) and below compositional (120). The subcategory contract ("every candidate must
  preserve an aligned driver and a visible reaction path through the chain cradle") caps how many
  structurally distinct skeletons/mechanisms can exist without leaving the category; reaching 120 would
  require inventing ①/② candidates the 8-record pool does not contain, which Rule 3 forbids.
- core axes / cartesian count / gate-filtered legal count: `frame_form(4) × drive_form(3) ×
  cradle_form(3) × chain_guide(2)` = **72 / 72** (no deny rows).
- multiplicity axes / admitted integers / reachable integers / min-mid-max boundaries: **none** (§8 — the
  source map rules out an honest N axis; no `*_count` is exposed).
- raw cartesian count / gate-filtered legal count: **72 / 72** (raw == core; no N axes).
- excluded: palette (⑥, 5 values), material 大类, host-conformal decoration (④), continuous dimensions (⑤).
- profile floor / recommended target / exception: floor **48** (standard) — met at 72 with 24 to spare.
  No hash-bound human exception required.

## Visual Risk

- `hidden_slide` — `driver_feed` runs the carriage inside the frame's tapped nut boss; a wrong bore/crest
  radius relation either floats the carriage (isolated part) or buries it. Watch the closed pose and the
  thread-flank contact element pair.
- `multi_joint` — `compound_toggle` + `rotating_seat_turret` + `sliding_cheek_guide` realizes 5 non-FIXED
  joints; the `lever_pivot × toggle_joint` product is the highest-risk swept region.
- `curved_fit` — the frame silhouette is polygon + `threePointArc`; ④ decoration (hanging hole, ribs,
  gussets, pads) must ride the realized curved/scaled surface, not a constant radius (Rule 4).
- Category-specific **reaction-path legibility** — at `driver_feed=upper` the cone pin must visibly
  approach the cradle seat on the same axis, with the frame closing the loop behind it. A seed where the
  driver misses the seat (turret indexed to a blank sector, guide traversed under the pin) is a visual
  blocker even if every geometric gate passes. Covered by the §9 viewer focus and the §6.5 targeted poses.

## Validator

- `slot_choices_for_seed` returns implemented module names for all four slots and matches
  `model.meta["slot_choices"]` produced by the build
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special
- compatibility matrix / gating prevents illegal module combinations (here: legality is structural — the
  derivation rules make would-be-illegal combos unconstructible; zero deny rows)
- no regression overrides exist; no curated / modulo table is used as the main seed domain
- controlled local scale params are clamped in `resolve_config` and cannot break interfaces, clearance,
  joint origin, or category identity
- cross-part scale dependencies (`cradle_channel_w` → `turret_thickness` / `guide_cheek_gap`;
  `guide_slot_len`; `feed_travel`, `carriage_reach`, `spindle_rear_z` inequalities) are resolved in
  `resolve_config` / the layout function, not left to fail in the builder
- every separate moving child keeps a deliberate 0.1–0.4 mm capture interference with its host, so
  `fail_if_isolated_parts` passes with **no part-level exemption**
- captured joints omit `mating=` per the Rule 2 grandfather and each carries a code comment naming the
  captured geometry; `guide_slide` declares a real `MatingContract` + `tangential_containment=True`
- key joints have expected type / axis / range per the §8.5 ⑤ envelope table; `spindle_turn` and
  `turret_index` carry `qc_sample_values`
- driver–cradle coaxiality: the working line passes through the cradle region (template identity check)
- host visuals (anvil ledges/pads, flange, ribs, bosses, pocket pin, bolt heads) are fused/host geometry —
  **no FIXED-jointed decoration parts**
- every moving module is a complete solid with visible support/guide and closed/mid/max clearance
  (`fail_if_parts_overlap_in_sampled_poses` + per-mechanism targeted `ctx.pose(...)`)
- **no whole-part overlap allowance and no `allow_isolated_part`**; every intentional contact names an
  exact element pair with a physical reason (§6.5 column 7)
- `frame` is the sole hierarchy root; part count == 4 + (turret?) + (guide?)

## Reject cases

1. **`allow_isolated_part` on the carriage/hub/t-bar** (the source records' pattern, S1 L483-L496,
   L536-L542). The fits must be real capture contacts with element-scoped allowances, or the parts float.
2. **Capture fit left as pure clearance with no interference** → `fail_if_isolated_parts` fails
   (contact tolerance is effectively exact) and the whole drive subtree detaches.
3. **Copying S2's world-coordinate drive geometry** — S2 builds the drive with world-space starts
   (`_point_along(axis, d, SPINDLE_REAR)`) *and* repeats `SPINDLE_REAR` as the joint origin, double-
   offsetting it: the measured `driver_carriage` AABB floats at z≈0.203–0.307 while the frame ends at
   z≤0.155. The template must author drive geometry in the **joint-local frame** (from local 0 along `a`),
   as S1 does.
4. **Downgrading the frame silhouette to `Box`/`Cylinder`** — S1/S3/S5/S6/S7/S8 all use
   `mesh_from_cadquery` over a polygon + `threePointArc` profile. Rule 3 blocker.
5. **Restating `cradle_channel_w` in the turret or guide factory** instead of reading the frame's
   published anchor — Contract 3c drift; produces a 16 mm turret jammed in a 10 mm twin-plate channel.
6. **Keeping S1's diagonal spindle axis for some frame_forms and S2's vertical axis for others** — two
   incompatible root frames in one slug; every cross-slot anchor then needs two code paths, the
   `MatingContract` face sides become unstateable, and the domain collapses to 19 gated combos (this is
   exactly what the superseded draft did).
7. **Emitting anvil ledges / pads / flange / ribs / gussets / bolt heads as FIXED-jointed parts** —
   Rule 1 blocker; they must be `frame.visual(...)` or fused host geometry.
8. **Copying S7's guide slot length (0.030) verbatim** — shorter than its own travel demand ⇒ the tongue
   exits the slot and 穿模 at the stroke ends. `guide_slot_len` must be derived (§7).
9. **Copying S6's full-thickness turret tie ribs** — constant rib/disk overlap; the ribs must be thin
   top/bottom webs kept off the rotation envelope and the disk thinned to `cradle_channel_w − 0.0012`.
10. **Sampling `turret_index` full 2π without checking the driver cone** — at `driver_feed=upper` the pin
    is inside the throat; an unclamped turret sweeps the pin. Must be covered by sampled poses.
11. **A constant-radius bolt-hole ring or rib band laid over a scaled/curved frame face** — Rule 4
    (④ conformality) blocker, the `Container_Tube label_band` failure mode.
12. **Driver not collinear with the cradle** (drive line falling outside the throat) → category identity
    failure.
13. **Copying S1's core-shaft length (0.100) onto the canonical centreline** — S1's core runs from
    t=0.016 to t=0.116, i.e. to within 1 mm of the tip, so the thrust collar, guide neck and the whole
    cone pin sit *inside* it and S1's spindle has no exposed pin at all. S1 gets away with it only
    because its spindle line misses its own anvil by ~31 mm (§13 correction). Once the driver is on the
    cradle centreline the core length is a **relation**: it must end at the guide neck
    (`_C_SHAFT_L = _C_NECK_T − _C_SHAFT_T`), or the 8.4–15 mm core rams the anvil/lower arm at full feed.
14. **Stating a captured pin's radius independently of the bore it sits in** — the generalisation of
    Reject case 2, and the single most productive bug family in this slug: rod guide rings 1.0 mm *under*
    the nut bore, the lever pin 1.5 mm under its hole, the toggle boss 0.5 mm under its hole. Each reads
    as a plausible literal and each silently detaches its subtree. Every pin must derive as
    `bore + _CAPTURE_FIT`.
15. **Boring the driver passage through a `twin_cheek_plates` cheek** — a ~3 mm plate is thinner than the
    bore, so a through-bore does not make a hole, it **severs** the plate: the relief bore cuts the lower
    arm off the back column and the arm bore cuts the upper arm. The plate gap IS the pin relief here
    (S3 L47 `PLATE_GAP`), so `_cut_working_bores(..., relief=False)`; the arm bore stays (the driver is
    wider than the channel) and the arm-fused nut boss bridges the two halves it separates.
16. **A full-width pedestal column under the toggle lever** — the lever's hub is a rounded tail of radius
    `_LEVER_W/2` swept about the pivot, wider than the pin it captures, so any column spanning the
    lever's own swing plane sits permanently inside that swept circle. The pedestal must be a **yoke**:
    two cheeks straddling the lever with a running gap, pin through both.
17. **Overriding pose sampling via `meta['qc_sample_values']` on a scalar movable joint** — the harness
    rejects it outright (legitimate only on FLOATING joints) and it neuters the motion gate. Earlier
    drafts used it on `spindle_turn` and `turret_index` to dodge exactly the θ=π anvil-vs-pin collision
    that Reject case 10 predicts. Fix the geometry (§7 `turret_center_z`), never the sampler.

## 与相邻类别的边界

- 不该混入：**chain tensioner / chain puller**（张紧钩拉链条两端；本类是把销轴压出，没有对齐驱动器
  经摇篮闭合的反力路径——违反 source map 的 subcategory contract）。
- 不该混入：**pipe cutter / tube cutter**（`tube_cutter` 是独立 slug：绕工件旋转的 CONTINUOUS 切轮 +
  滚轮环抱喉口；本类无切削刃，运动 spine 是单一对齐直线驱动器）。
- 不该混入：**generic C-clamp / vise**（有螺杆和 C 框但没有 chain cradle / anvil seat；对置平口夹持
  而非顶销，缺类别身份第三要素）。
- 不该混入：**rivet gun / rivet squeezer**（`rivet_squeeze` 是独立 slug：对置双模具挤压铆钉，反力路径
  是 die↔die，不经过 chain cradle）。
- 不该混入：**pliers / chain pliers**（双柄剪刀运动学；本类驱动是 PRISMATIC 顶进，不是对捏）。
- 不该混入：**press brake / arbor press / powered & hydraulic presses**（无链条摇篮，工作面是平口压板；
  动力缸与机架比例完全不同；source map Blocked 列表明确排除）。

## Authoring 自检记录
| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| self-check notes | All 8 five-star samples read in full (§2). Every ①/② candidate carries an accepted record + exact `model.py:Lx-Ly` (§4, §14) — **no module traces to the single origin alone**: Slot A draws on S1/S2/S3/S8, Slot B on S1/S4/S5, Slot C on S1/S2/S6, Slot D on S1(+S2/S8 baseline)/S7. §4.1 empty and justified (no extrapolated ③). §7.5 budget declared (≤18 s/seed) with banded tessellation. §8 declares no multiplicity, honoring the source map. §8.5 all six axes examined, none blank. §9 core=72 ≥ standard floor 48, zero deny rows with a structural argument. §1.1 Category Binding present. The four machine-checked headings (`## Form Dependency Contracts`, `## Compatibility Gates`, `## Combination Domain`, `## Visual Risk`) are present. `palette_style` = 5 realistic colorways covering 3 material 大类 ≥ ceil(0.5×5). Slot D at 2 candidates with a written degrade reason. Map's Blocked/Excluded honored in §11. Risks carried into implementation: the sources rely on `allow_isolated_part` (replace with capture interference, Reject 1/2); S2's double-offset (Reject 3); S7's short slot (Reject 8); S6's rib overlap (Reject 9). |

## 模板实现备注（可选）

- **Canonical body frame — the single most important implementation decision.** All frame_forms and all
  drive_forms are authored in S2's convention: working axis `a` = world **(0,0,-1)**, body normal `b` =
  **(0,1,0)**, transverse `h = a×b` = **(1,0,0)**, cradle seat near **z≈0**. S1/S3/S5/S6/S7/S8's in-plane
  casting profiles are re-based by one rigid rotation
  `α = -π/2 - atan2(SPINDLE_AXIS[1], SPINDLE_AXIS[0])` applied to their 2D profile points, then built on
  cadquery's `"XZ"` workplane (local (u,v) → world (u,0,v), extrude ±Y). This maps S1's
  `BAR_AXIS=(0,0,1)` onto world `(0,1,0)` — identical to S2 — and preserves every polygon vertex, arc
  control point, primitive and proportion. Shared helper: `_rebase_xy(pt)`.
- **Anchor contract (Contract 3c).** `_frame_anchors(r) -> FrameAnchors` is the ONLY place that states
  `spindle_rear_z`, `nut_boss_z`, `cradle_top_z`, `cradle_reaction_z`, `cradle_channel_w`,
  `throat_half_x`, `lever_pivot_xz`, `guide_seat_z`, `body_half_y`, `grounded`. Every drive/cradle/guide
  factory reads it; none restates a value.
- **Capture interference bands** (`fail_if_isolated_parts` needs contact; `overlap_tol` is 5 mm, so these
  are safe): thread crest r 0.0095 vs bore r 0.0091 (**+0.4 mm**, thread engagement); hub tenon r 0.0050
  vs bore r 0.0047 (**+0.3**); t_bar r 0.0055 vs transverse bore r 0.0052 (**+0.3**); turret pin r 0.0036
  vs disk bore r 0.0033 (**+0.3**); toggle pins/holes (**+0.2** band); guide base embedded 0.2 mm into the
  slot floor; toggle smooth-rod variant uses a reduced bore r 0.0070 + guide ring r 0.0072. All constant
  across travel and guaranteed by the constants, not by tuning.
- **Shared helpers**: `_rebase_xy`, `_frame_anchors`, `_silhouette_profile` (S1's polygon+arcs — shared by
  `compact_cast_handheld` / `flanged_bench_pedestal` / `twin_cheek_plates`), `_carriage_shape` (threaded
  version shared by `screw_tbar` / `ratchet_socket`; `compound_toggle` uses `_driver_rod_shape`),
  `_v_notch_solid` (turret pockets AND seat inserts, S6 L82-L109), `_fuse_all`, `_point_along`.
- **MatingContract attention**: only `guide_slide` has two axis-aligned faces in contact and declares a
  real contract (+`tangential_containment=True`). `driver_feed`, `spindle_turn`, `t_bar_slide`,
  `ratchet_fold`, `lever_pivot`, `toggle_joint`, `turret_index` are pin-through-sleeve / pin-through-lug
  geometry and OMIT `mating=` under the AUTHORING Rule 2 grandfather — each must carry a code comment
  naming the captured geometry. This mirrors both reference templates (`rivet_squeeze` omits on all
  joints; `tube_cutter` omits on its roller/wheel pivots).
- **Element-scoped allowances required** (exact pairs, never whole-part):
  `frame:spindle_nut_boss ↔ driver_carriage:spindle_thread` (thread flank);
  `driver_carriage:spindle_shaft ↔ spindle_hub:hub_body` / `ratchet_head:head_body` (concentric capture,
  mirrors S1 L497-L512); `spindle_hub:hub_body ↔ t_bar:bar_shaft` (bore capture);
  `ratchet_head:pivot_boss ↔ ratchet_handle:handle_bar`; `frame:lever_pivot_boss ↔ toggle_lever:lever_arm`;
  `toggle_lever:toggle_boss ↔ toggle_link:link_rod`; `frame:turret_pivot_pin ↔ anvil_turret:turret_disk`;
  `frame:guide_rail_slot ↔ guide_carriage:rail_tongue` (close-fit rail).
- **Clearance solver (Contract 3d)**: `clamp_joint_limits(model, 'ratchet_fold' | 'lever_pivot' |
  't_bar_slide', margin=..., keepout=['frame'])` after geometry is emitted — do not hand-derive the
  closing trig.
- **Deferred**: nothing. All 72 combos enter the seed domain from the first version.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / D | `compact_cast_handheld`, `screw_tbar`, `stepped_ledge_anvil`, `chain_guide=none` | `rec_picturex_0611__chain_separator__001__png_21cece9ed04f4870b0d43f804d878f13` | L19-L43, L65-L158, L161-L243, L246-L371, L497-L555 | frame silhouette + hanging hole + sleeve/bore; screw drivetrain part tree + 3 joints; stepped-ledge cradle; no-guide baseline; canonical proportions; capture-test idioms |
| S2 | A / C | `bench_c_frame`, `grooved_pad_anvil` | `rec_picturex0611_chain_separator_fork_bench_c_frame_20260714` | L26-L56, L78-L221, L224-L309, L405-L447 | **canonical body-frame convention** (axes L26-L28); C-frame envelope + foot + gussets + ribs + bolt holes; grooved anvil seat + full-width pads; axis-portability proof for the drive |
| S3 | A | `twin_cheek_plates` | `rec_picturex0611_chain_separator_fork_twin_plate_bridge_20260714` | L45-L54, L76-L212, L310, L331-L347 | twin-plate macro-surface construction; bridge spacer set; `PLATE_GAP` = `cradle_channel_w` source; zinc material |
| S4 | B | `ratchet_socket` | `rec_picturex0611_chain_separator_fork_ratchet_socket_drive_20260714` | L49-L68, L176-L309, L411-L450, L608-L654 | ratchet head part tree (knurl ring / pivot boss / selector nub); folding handle + rubber grip; `ratchet_fold` REVOLUTE policy; capture idioms |
| S5 | B | `compound_toggle` | `rec_picturex0611_chain_separator_fork_toggle_lever_drive_20260714` | L46-L91, L205-L214, L222-L352, L444-L488, L644-L680 | toggle linkage pivot geometry + derivation formulas; lever + link part tree; frame-rooted `lever_pivot` + `toggle_joint` policy; smooth driver rod |
| S6 | C | `rotating_seat_turret` | `rec_picturex0611_chain_separator_fork_rotating_anvil_turret_20260714` | L45-L60, L82-L109, L159-L197, L235-L281, L453-L478, L523-L541, L728-L791 | turret disk + central bore + 3 V-notch pockets; `_v_notch_solid` helper; press-fit seat inserts; frame pocket/pin/web; `turret_index` REVOLUTE 0..2π policy |
| S7 | D | `sliding_cheek_guide` | `rec_picturex0611_chain_separator_fork_adjustable_chain_guide_20260714` | L44-L52, L121-L130, L244-L306, L372-L383, L473-L490, L679-L757 | guide carriage complete solid (base/tongue/2 cheeks/knob); transverse rail slot interface; `guide_slide` PRISMATIC policy; `cheek_gap` source; traverse semantics idioms |
| S8 | A | `flanged_bench_pedestal` | `rec_picturex0611_chain_separator_fork_mounting_flange_20260714` | L65-L157, L159-L216, L323-L346 | grounded flange plate; 4 bolt holes; 2 cast gussets; flanged-pedestal envelope |
</content>
