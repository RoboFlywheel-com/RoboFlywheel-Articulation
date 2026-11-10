# piano — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `piano` |
| 大类/小类 | `Bar/Piano` |
| source map | `<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Bar__Piano.md` |
| parent A (grand) | `rec_a-glossy-black-grand-piano-with-its-curved-wing-_20260605_132149_762624_be39da53` ← `picture/Bar/Piano/001.png` |
| parent B (upright) | `rec_a-glossy-black-upright-piano-standing-tall-again_20260605_132213_191152_c63fde85` ← `picture/Bar/Piano/002.png` |
| template path | `agent/templates/Bar_Piano.py` |
| test path (optional) | `tests/agent/test_piano_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children case→{lid, fallboard, keyboard, pedals, music-support} + multiplicity on pedals + grand visible string rows) |

`pattern = mixed`: a single rigid case/cabinet root is the common parent; the lid leaf/leaves, the fallboard, the full keyboard, the pedal bank, and the music-support layer all hang off it as parallel children. The pedal layer carries the functional multiplicity axis (`pedal_count`), and grand-family cases additionally carry a visual/topological multiplicity axis (`visible_string_count`) for the exposed string rows under the lid. There is no serial kinematic chain — every moving child mounts directly on the case root.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 parents + 6 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

**Shared structure across all 8 samples.** Every piano is one rigid root part (`case` for grand-family, `body` for upright-family) that carries five functional layers as direct children of that root:
1. **A case/cabinet body** that establishes footprint and playing height (keybed/key-shelf top ≈ 0.696–0.720 m floor-referenced).
2. **A top lid** that opens upward on a REVOLUTE hinge.
3. **A fallboard / keyboard cover** that exposes or covers the keys (REVOLUTE fold or PRISMATIC slide).
4. **A full 52-white-key keyboard** (52 white PRISMATIC + 36 black PRISMATIC keys, identical across every sample: `WHITE_PITCH=0.0234`, `WHITE_KEY_W=0.0218`, `black_after={0,1,3,4,5}`, each key axis `(0,0,-1)`, travel ≈0.009/0.007 m). This layer is structurally invariant and is NOT a slot — it is a module-local fixed sub-structure of the case.
5. **A pedal bank** of brass pedals on a pedal box near the floor, each a REVOLUTE press (axis `(1,0,0)`, lower 0, upper 0.18).

**Two case families (the primary topology fork).**
- **Grand family** (`grand`, `baby_grand`, `split_top_lid`, `four_pedals`, `fold_down_music_desk`): `case` root built from a Catmull-Rom *bentside* spline outline → hollow extruded rim wall + bottom board + wood soundboard + gold cast-iron plate + steel/copper strings, on **3 tapered legs + brass casters**, with a hanging **lyre + pedal box**, and a music desk standing in front of the strings. Top lid is a wing-shaped extruded panel hinged on the **spine (left long edge), axis `(0,-1,0)`**. Fallboard is **REVOLUTE** hinged at the front shelf, axis `(1,0,0)`.
- **Upright family** (`upright`, `spinet`, `sliding_fallboard`): `body` root = vertical cabinet (back panel + two side panels + plinth) + upper front panel + kickboard + protruding key shelf + pedal mount block. Top lid is a flat board hinged at the **rear top edge, axis `(-1,0,0)`**. Fallboard is **PRISMATIC**, slides forward over the keys, axis `(0,-1,0)`.

Grand-family samples expose steel/copper string rows over the soundboard/plate. The observed parent loop emits 26 visible rows; the template may vary this as `visible_string_count` for open-lid visual density. This is only a visible-row density axis, not an attempt to model the full acoustic string count of an 88-note piano. Upright-family strings remain hidden behind the cabinet and do not expose this axis.

**Per-source differences that define candidates.**
- `baby_grand` = grand with compact footprint: `TAIL_Y=1.50` (vs 1.86), shorter bentside control points, tail-back-left spine corner at 1.22 (vs 1.52), legs/hitch-rail pulled forward. **Fallboard hinge lowered to z=0.796** (grand parent uses 0.800) so the folded fallboard seats on the nameboard — see implementation note.
- `spinet` = upright with `SHELL_TOP_Z=0.940` (vs 1.190), short upper front panel (height 0.110 vs 0.340), top rail at 0.918.
- `split_top_lid` = grand whose single lid is replaced by **two leaves** `lid_front`/`lid_rear`, each its own REVOLUTE spine hinge, each with a visible brass `PianoHingeGeometry` knuckle strip; split at `SPLIT_Y=1.00`.
- `sliding_fallboard` = upright whose PRISMATIC fallboard gains side `slide_track_l/r` guide rails and a front `fallboard_handle` grip, with longer travel (0.20 vs 0.12).
- `four_pedals` = grand whose 3-pedal bank becomes a 4-pedal loop (`pedal_x_offsets` centered, `pedal_{i}` naming, identical revolute policy). This is the multiplicity evidence.
- `fold_down_music_desk` = grand whose **fixed** music-desk panel is replaced by an articulated `music_rest` part (rest_panel + rest_lip) on a `case_to_music_rest` REVOLUTE hinge (axis `(1,0,0)`, upper 1.40 rad), keeping the fixed `music_desk_base` rail.

Note: grand-family `four_pedals`/`split_top_lid`/`fold_down_music_desk` all use the *flat-rest, fold-up* fallboard pose (panel at z=0.010 flat, `upper=2.4`), whereas the grand/baby_grand parents use the *vertical-rest, fold-down* fallboard pose (`rpy=(π/2,…)`, `upper=π/2`). Both are the same REVOLUTE fallboard joint at the same hinge; the template's `standard_lid_fallboard` module should pick one consistent grand fallboard convention (the flat-rest fold-up pose is the more general / collision-safe one and is recommended).

## 核心身份

A **piano** is a keyboard musical instrument: a large rigid case or cabinet that houses a full 88-note keyboard (modeled as 52 white + 36 black keys), with an upward-opening **top lid**, a **fallboard** (key cover) that exposes or covers the keys, a bank of **foot pedals** near the floor, and a **music-support** surface. The defining, always-present identity geometry is: (a) the long horizontal black-and-white keyboard with each key independently pressable downward; (b) at least one upward-opening lid; (c) a fallboard over the keys; (d) brass foot pedals. Two mature body archetypes exist and must both be supported: the **grand** (horizontal curved wing case on legs, strings/plate visible under a wing lid hinged on the spine) and the **upright** (tall vertical cabinet, lid hinged at the rear top, fallboard sliding or folding). Default mature domain = a glossy black instrument with the full keyboard exposed, lid closed or propped, fallboard open, three pedals.

Not part of this category: electronic keyboards / synthesizers on stands (no acoustic case, no lid, no pedals-on-lyre), harpsichords/clavichords (different plucked action, no cast-iron plate, but visually close — excluded by the lid+pedal+legs grand identity), and organ consoles (multiple manuals + stops, no single keyboard case). See §11.

## 槽位 + 候选模块表

### Slot A：case / cabinet body

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| grand_case | rec_a-glossy-black-grand-piano-with-its-curved-wing-_…_be39da53 (parent A) | build L85-L269 (outline `_piano_outline` L51-L69; rim/board/soundboard/plate L106-L146; strings L162-L180; keybed/blocks/nameboard/shelf/keyslip L182-L217; legs+casters L219-L239; lyre+pedal_box L241-L255; music desk L257-L269) | eligible if compatible | grand `case` root: hollow bentside-spline rim wall (`ExtrudeWithHolesGeometry`), wood soundboard, gold cast-iron plate, loop-emitted visible steel/copper strings (observed N=26), 3 tapered legs on brass casters, hanging lyre+pedal box; full grand footprint `TAIL_Y=1.86` |
| upright_case | rec_a-glossy-black-upright-piano-standing-tall-again_…_c63fde85 (parent B) | build L42-L135 (shell back+sides L53-L66; plinth L68-L74; upper panel+top rail L76-L89; kickboard L91-L97; key shelf+blocks+ledge+nameboard L99-L127; pedal mount block L129-L135) | eligible if compatible | upright `body` root: vertical cabinet (back + two side panels + plinth), tall upper front panel + kickboard, protruding key shelf, fallboard ledge, pedal mount block; `SHELL_TOP_Z=1.190` |
| baby_grand_case | rec_piano_var_baby_grand_body | build L85-L269 (compact outline `_piano_outline` L51-L69 with `TAIL_Y=1.50`, tail-back-left 1.22; legs/hitch-rail pulled forward L155-L160, L220) | eligible if compatible | grand `case` with compact wing footprint (`TAIL_Y=1.50` < 1.60), shorter bentside spline; same rim/plate/strings/legs/lyre structure as grand_case |
| spinet_upright_case | rec_piano_var_spinet_upright_body | build L43-L136 (`SHELL_TOP_Z=0.940` L26; short upper panel height 0.110 + top rail at 0.918 L77-L90) | eligible if compatible | upright `body` shortened to spinet height (`SHELL_TOP_Z=0.940`), short upper front panel; same back/sides/plinth/key-shelf/pedal-mount structure as upright_case |

### Slot B：lid / fallboard mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| standard_lid_fallboard | parents A & B | grand: lid REVOLUTE L271-L295 + fallboard REVOLUTE L301-L320 (parent A); upright: lid REVOLUTE L137-L157 + fallboard PRISMATIC L159-L178 (parent B) | eligible if compatible | one-piece top lid + fallboard matched to the case family: grand → wing lid hinged on spine `(0,-1,0)` + REVOLUTE fallboard `(1,0,0)`; upright → flat lid hinged at rear `(-1,0,0)` + PRISMATIC fallboard slide `(0,-1,0)` |
| split_top_lid | rec_piano_var_split_top_lid | two-leaf lid L274-L375 (split-curve intersection L280-L299; front/rear leaf outlines L301-L317; per-leaf part+`PianoHingeGeometry` strip+REVOLUTE joint loop L319-L375); fallboard REVOLUTE L377-L399 | eligible if compatible (grand family only) | grand single lid replaced by **two parts** `lid_front`/`lid_rear`, each own REVOLUTE spine hinge `(0,-1,0)`, each with brass `PianoHingeGeometry` knuckle strip; split at `SPLIT_Y=1.00`. Distinct part tree (2 lid parts + 2 joints vs 1) |
| sliding_fallboard | rec_piano_var_sliding_fallboard | slide tracks L121-L128 + lid REVOLUTE L145-L165 + fallboard PRISMATIC L167-L193 (`fallboard_handle` L179-L184, travel upper=0.20) | eligible if compatible (upright family only) | upright lid (rear hinge) + PRISMATIC fallboard slide that adds side `slide_track_l/r` guide-rail visuals and a front `fallboard_handle` grip; longer travel than standard upright fallboard. Distinct part visuals + child interface |

### Slot C：pedal / music support layer

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| three_pedals | parents A & B | grand: pedal loop L370-L393 (`(-0.052,0.0,0.052)`, parent A); upright: pedal loop L224-L246 (`(-0.055,0.0,0.055)`, parent B) | eligible if compatible | conventional 3-pedal bank; each pedal a REVOLUTE press `(1,0,0)` lower 0 upper 0.18 on the pedal box front; fixed music-desk panel is a parent visual (not articulated) |
| four_pedals | rec_piano_var_four_pedals | pedal multiplicity loop L369-L399 (`n_pedals=4`, centered `pedal_x_offsets` L380-L382, `pedal_{i}` naming + REVOLUTE joint L383-L399) | eligible if compatible | pedal bank emitted as a centered loop of N=4 `pedal_{i}` copies with identical REVOLUTE press policy; this is the `pedal_count` multiplicity evidence. Adds 1 part+joint vs three_pedals |
| fold_down_music_desk | rec_piano_var_fold_down_music_desk | articulated music rest L257-L294 (fixed `music_desk_base` rail L257-L263; `music_rest` part = rest_panel+rest_lip L270-L285; `case_to_music_rest` REVOLUTE L286-L294) | eligible if compatible (grand family only) | replaces the **fixed** music-desk panel with an articulated `music_rest` part (panel + lower lip) on a REVOLUTE hinge `(1,0,0)` upper 1.40 rad over the fixed base rail; adds 1 moving part+joint. Pedal bank independent (defaults to three_pedals) |

Slot C carries two orthogonal sub-structures: the **pedal count** (three_pedals vs four_pedals = the functional multiplicity axis, §8) and the **music-support articulation** (fixed desk vs fold_down_music_desk). Grand-family Slot A additionally owns the **visible string row count** (`visible_string_count`, §8) because those repeated string visuals live on the case/soundboard, not in Slot C. `fold_down_music_desk` is the candidate that turns the otherwise-fixed music desk into a moving part; it composes with whichever pedal count is chosen. No single-candidate slot: Slot C has 3 structurally distinct candidates.

## 槽位图（slot graph）

pattern: `mixed` (parallel_children + multiplicity)

```
                         ┌─[REVOLUTE spine (0,-1,0) | rear (-1,0,0)]──> Slot B: top lid (1 leaf | 2 leaves)
                         │
Slot A: case/body  ──────┼─[REVOLUTE (1,0,0) fold | PRISMATIC (0,-1,0) slide]──> Slot B: fallboard
   (root, fixed) ────────┤
                         ├─[52× PRISMATIC (0,0,-1)]──> keyboard (module-local fixed layer, NOT a slot)
                         │
                         ├─[M× fixed visual rows]──> grand visible string rows (grand only, multiplicity = visible_string_count)
                         │
                         ├─[N× REVOLUTE (1,0,0)]──> Slot C: pedal_{i} bank  (multiplicity = pedal_count)
                         │
                         └─[REVOLUTE (1,0,0) fold OR fixed visual]──> Slot C: music-support
```

- **Root**: Slot A is the single rigid root link (`case` for grand-family, `body` for upright-family). Every other layer is a direct child of this root — no serial chains.
- **Slot A → Slot B (top lid)**: REVOLUTE hinge mounted on the case top edge. Grand: hinge on the left long *spine* edge at `xyz≈(-HALF_W, 0.70, RIM_TOP_Z+LID_THK/2)`, axis `(0,-1,0)`, opens the free bentside edge upward (upper ≈0.95). Upright: hinge at the *rear top* edge `xyz=(0, DEPTH_BACK_Y, SHELL_TOP_Z+LID_THK/2)`, axis `(-1,0,0)`, lifts the front edge upward (upper ≈1.2). For `split_top_lid` (grand only) the single hinge becomes two parallel spine hinges, one per leaf, split at `SPLIT_Y=1.00`.
- **Slot A → Slot B (fallboard)**: mounted on the front shelf / ledge above the keyboard. Grand: REVOLUTE, hinge at `xyz≈(0, 0.002, 0.800)` (0.796 for baby_grand — see note), axis `(1,0,0)`, folds over/back the keys. Upright: PRISMATIC, origin at `xyz=(0, 0.015, LEDGE_TOP_Z)`, axis `(0,-1,0)`, slides forward over the keys; `sliding_fallboard` adds guide-rail contact surfaces (`slide_track_l/r`).
- **Slot A → keyboard (fixed layer)**: 52 white + 36 black keys, each a PRISMATIC joint on the keybed/key-shelf top, axis `(0,0,-1)`. This layer is identical across all 8 samples and is module-local fixed structure of Slot A, not a slot.
- **Slot A → grand visible strings (fixed visual multiplicity)**: grand-family cases loop-emit `string_{i}` visible rows over the soundboard/cast-iron plate. `visible_string_count` varies the exposed row density under the lid; upright-family cases keep strings hidden and do not expose this parameter.
- **Slot A → Slot C (pedals)**: N pedals on the pedal box / pedal mount block, each REVOLUTE axis `(1,0,0)`, looped `pedal_{i}` (see §8). `pedal_count` is the functional multiplicity axis.
- **Slot A → Slot C (music support)**: either a fixed parent visual (default) or, for `fold_down_music_desk` (grand only), an articulated `music_rest` REVOLUTE child on the fixed `music_desk_base` rail, axis `(1,0,0)`.
- **Mutual exclusion / gating (see §9 compatibility matrix)**: Slot B candidates are body-family-typed — `split_top_lid` requires a grand-family Slot A (it needs the spline rim + spine hinge), `sliding_fallboard` requires an upright-family Slot A (it needs the protruding key shelf + ledge). `standard_lid_fallboard` works with either family. `fold_down_music_desk` is grand-family only (uprights have no front-of-strings music desk surface). `visible_string_count` is also grand-family only because upright strings are cabinet-internal and not exposed as visible exterior rows.

## 每槽位 Module Emits / Interfaces

### Slot A / module grand_case (also baby_grand_case)
| emits | 描述 | 来源 |
|---|---|---|
| parts | one root part `case`; visuals: `rim_wall`, `bottom_board`, `soundboard`, `cast_iron_plate`, `pinblock`, `hitch_rail`, `string_0..visible_string_count-1`, `keybed`, `key_block_l/r`, `nameboard`, `front_shelf`, `keyslip`, `leg_0..2`+`leg_collar`+`caster`, `lyre_post_l/r`, `pedal_box`, `music_desk_panel`/`music_desk_base` | grand A / model.py:L103-L269 (baby_grand: same with `TAIL_Y=1.50`) |
| internal joints | none on the case root itself (case is rigid) | grand A / model.py:L103-L269 |
| upstream interface | floor at z=0; legs/casters set body height so keybed top = `KEY_BED_TOP_Z=0.695` | grand A / model.py:L219-L239 |
| downstream interface | rim top ring (`RIM_TOP_Z=1.000`) = lid hinge plane; front shelf top (z≈0.800) = fallboard hinge; keybed top = keyboard prismatic origins; pedal box front face = pedal hinge plane | grand A / model.py:L182-L255 |

### Slot A / module upright_case (also spinet_upright_case)
| emits | 描述 | 来源 |
|---|---|---|
| parts | one root part `body`; visuals: `back_panel`, `side_panel_l/r`, `plinth`, `upper_front_panel`, `top_front_rail`, `lower_front_board`, `key_shelf`, `key_block_l/r`, `fallboard_ledge`, `nameboard`, `pedal_box` | upright B / model.py:L51-L135 (spinet: `SHELL_TOP_Z=0.940`, short panel) |
| internal joints | none on the body root itself (body is rigid) | upright B / model.py:L51-L135 |
| upstream interface | floor at z=0; plinth/shell bottom at `SHELL_BOTTOM_Z=0.050`; key shelf sets keybed top = `KEYBED_TOP_Z=0.696` | upright B / model.py:L68-L105 |
| downstream interface | shell top (`SHELL_TOP_Z`) = rear lid hinge plane; fallboard ledge top (`LEDGE_TOP_Z=0.740`) = fallboard slide origin; pedal mount block front = pedal hinge plane | upright B / model.py:L99-L135 |

### Slot B / module standard_lid_fallboard
| emits | 描述 | 来源 |
|---|---|---|
| parts | `top_lid` (1 part, `lid_panel` visual); `fallboard` (1 part, `fallboard_panel` visual) | grand A / model.py:L280-L309; upright B / model.py:L142-L169 |
| internal joints | `*_to_top_lid` REVOLUTE; `*_to_fallboard` REVOLUTE (grand) or PRISMATIC (upright) | grand A / model.py:L287-L320; upright B / model.py:L149-L178 |
| upstream interface | lid hinge on case top edge (spine for grand, rear for upright); fallboard hinge/slide at front shelf/ledge | grand A / model.py:L287-L295; upright B / model.py:L149-L157 |
| downstream interface | closed lid rests on rim/shell top; fallboard at rest exposes keys, actuated covers them | grand A / model.py:L317-L320; upright B / model.py:L170-L178 |

### Slot B / module split_top_lid (grand family only)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_front`, `lid_rear` (2 parts; each `*_panel` + `*_hinge_strip` brass `PianoHingeGeometry` visual); plus `fallboard` | split / model.py:L319-L375; L381-L388 |
| internal joints | `case_to_lid_front` REVOLUTE + `case_to_lid_rear` REVOLUTE (both axis `(0,-1,0)` on spine); `case_to_fallboard` REVOLUTE | split / model.py:L364-L374; L389-L399 |
| upstream interface | two parallel spine hinges at `xyz=(-HALF_W, hinge_y_leaf, RIM_TOP_Z+LID_THK/2)`, split at `SPLIT_Y=1.00`; hinge strips along each leaf's spine edge | split / model.py:L277-L375 |
| downstream interface | both leaves close down onto rim top ring (each clears the strings); free edges lift upward when opened | split / model.py:L364-L374 |

### Slot B / module sliding_fallboard (upright family only)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `top_lid` (rear-hinged); `fallboard` (`fallboard_panel` + `fallboard_handle`); on body: `slide_track_l/r` guide-rail visuals | sliding / model.py:L121-L128; L150-L184 |
| internal joints | `body_to_top_lid` REVOLUTE; `body_to_fallboard` PRISMATIC axis `(0,-1,0)`, travel upper=0.20 | sliding / model.py:L157-L193 |
| upstream interface | slide origin at `xyz=(0, 0.015, LEDGE_TOP_Z)`; guide rails on body at `z=LEDGE_TOP_Z+0.009` flank the cover | sliding / model.py:L121-L193 |
| downstream interface | cover retracted exposes keys; slid forward covers keyboard footprint, stays level above `WHITE_KEY_TOP_Z` | sliding / model.py:L185-L193 |

### Slot C / module three_pedals (also four_pedals — multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedal_0..N-1` (N parts, each `pedal` brass visual) | grand A / model.py:L376-L384; four / model.py:L383-L392 |
| internal joints | `*_to_pedal_{i}` REVOLUTE, axis `(1,0,0)`, lower 0 upper 0.18 | grand A / model.py:L385-L393; four / model.py:L393-L399 |
| upstream interface | mounted on pedal box / pedal mount block front face; centered `pedal_x_offsets` lateral spacing | four / model.py:L379-L382 |
| downstream interface | pedal front edge depresses below rest when actuated | grand A / model.py:L481-L487 (test) |

### Slot C / module fold_down_music_desk (grand family only)
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed `music_desk_base` rail (parent visual on case); `music_rest` part (`rest_panel` + `rest_lip` visuals) | fold / model.py:L257-L285 |
| internal joints | `case_to_music_rest` REVOLUTE, axis `(1,0,0)`, lower 0 upper 1.40, hinge at `xyz=(0,0.140,0.815)` | fold / model.py:L286-L294 |
| upstream interface | hinged at the bottom rear edge on the fixed `music_desk_base` rail, in front of the strings behind the fallboard | fold / model.py:L286-L294 |
| downstream interface | q=0 upright playing position; positive q folds rest forward; rest_lip supported near desk base | fold / model.py:L272-L294 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_module | enum | {grand_case, upright_case, baby_grand_case, spinet_upright_case} | — | choice | deterministic procedural sampler; sets body family (grand vs upright) | Slot A table |
| lid_fallboard_module | enum | {standard_lid_fallboard, split_top_lid, sliding_fallboard} | — | choice | conditional: split_top_lid⇒grand family, sliding_fallboard⇒upright family (see compat matrix) | Slot B table |
| music_support_module | enum | {fixed_music_desk, fold_down_music_desk} | fixed_music_desk | choice | conditional: fold_down_music_desk⇒grand family only | Slot C table |
| pedal_count | int (multiplicity) | product [2,4], test {3,4} | 3 | conditional | weighted draw; loop-emit `pedal_{i}` (see §8) | four / L374-L399 |
| body_width_scale | float | [0.94, 1.06] | 1.0 | independent | scales case width / `HALF_W`; keyboard `WHITE_PITCH×52` must still fit between key blocks | grand A / L28; upright B / L21 |
| case_depth_scale (grand) | float | [0.92, 1.10] | 1.0 | independent | scales bentside `TAIL_Y` / case length; baby_grand is the low end of this same scale | grand A / L30; baby / L30 |
| cabinet_height_scale (upright) | float | [0.78, 1.06] | 1.0 | independent | scales upright `SHELL_TOP_Z` + upper panel height; spinet is the low end | upright B / L26; spinet / L26 |
| lid_open_angle | float | grand [0,0.95], upright [0,1.2], split leaves [0,0.95] | 0.0 (closed) | conditional | range depends on lid module/family; rest pose closed | grand A / L294; upright B / L156 |
| fallboard_q | float | grand fold [0,2.4], upright slide [0,0.20] | 0.0 (open) | conditional | range/type depends on fallboard module (REVOLUTE rad vs PRISMATIC m) | grand A / L319; sliding / L192 |
| pedal_spacing | float | [0.038, 0.046] | 0.042 | independent | lateral pedal pitch; clamp so bank width ≤ pedal box width | four / L377 |
| visible_string_count | int (multiplicity) | grand product [20,32], test {24,26,30}; upright hidden/fixed | 26 | conditional | grand-family only; loop-emits visible `string_{i}` rows across the soundboard/cast-iron plate; not the real acoustic string count | grand A / L162-L180; baby same |
| (—) | constraint | — | — | inequality | `pedal_count × pedal_spacing ≤ pedal_box_width − 2×pedal_half_width`; violate ⇒ shrink pedal_spacing then reject | four / L375-L382 |
| (—) | constraint | — | — | inequality | grand visible string rows must remain inside the rim/soundboard footprint, above the soundboard, and below closed-lid clearance; endpoints recomputed after case scaling | grand A / L162-L180 |
| (—) | constraint | — | — | inequality | grand fallboard hinge_z derived so folded fallboard seats on nameboard (`= front_shelf_top` for grand, `0.796` for baby_grand-proportioned case); never floats | baby / L317 (see note) |
| palette_style | enum | {black_gloss, mahogany, walnut, white_polished, ebony_satin} | black_gloss | choice | per-seed colorway; see §palette below | all samples L88-L97 |

**palette_style colorways** (≥3 required; 5 provided, observed black + realistic instrument-finish families):
- **black_gloss** (observed in all 8 samples): case `(0.045,0.045,0.055,1)`, satin accents `(0.075,…)`, keys ivory `(0.945,0.935,0.900)` / ebony `(0.060,0.060,0.070)`, brass pedals/casters `(0.815,0.625,0.205)`, gold plate `(0.720,0.555,0.230)`, soundboard wood `(0.760,0.560,0.330)`.
- **mahogany**: warm red-brown case ≈`(0.36,0.16,0.11,1)`, darker satin trim, ivory/ebony keys unchanged, brass hardware, gold plate, wood soundboard.
- **walnut**: mid-brown case ≈`(0.30,0.21,0.14,1)`, satin trim, keys/brass/plate unchanged.
- **white_polished**: bright white case ≈`(0.92,0.92,0.93,1)`, light-grey satin trim, ebony keys + ivory keys, brass or chrome pedals.
- **ebony_satin**: deep matte black case ≈`(0.05,0.05,0.05,1)` with non-gloss satin everywhere; keys/brass unchanged.

Keyboard ivory/ebony, brass hardware, gold cast-iron plate and wood soundboard stay materially consistent across colorways (only the case/cabinet shell + satin trim shift); this keeps the instrument readable as a piano in every palette.

## Multiplicity / Copy Logic

**Two multiplicity axes:**

### Axis 1: `pedal_count` — functional pedal bank

- `count_param`: `pedal_count`.
- `N_range`: product domain `[2, 4]`; test domain `{3, 4}` (both samples observed). Real pianos almost always have 2 or 3 pedals; 4 is the rare "fourth pedal" / player-piano console case. Tail beyond 4 has no source evidence and is excluded.
- sampling domain (weighted, small-N heavy): `P(3)=0.62`, `P(2)=0.30`, `P(4)=0.08`. 3-pedal is the canonical mature piano; 2 is common on uprights/spinets; 4 is the rare tail.
- copied object: one `pedal` part = a brass `Box((width, depth, 0.012))` on a REVOLUTE joint.
- naming: `pedal_{i}` for `i in range(pedal_count)`; joint `*_to_pedal_{i}`.
- placement: centered lateral row on the pedal box front face — `pedal_x_offsets[i] = (i − (N−1)/2) × pedal_spacing`, all at the pedal box front Y and pedal box Z (grand z=0.200, upright z=0.120).
- joint policy: every copy identical — REVOLUTE, axis `(1,0,0)`, `MotionLimits(effort=12, velocity=2, lower=0.0, upper=0.18)`; each pedal presses its front edge downward independently.
- source/gating: `pedal_x_offsets` loop from `rec_piano_var_four_pedals` model.py:L374-L399. Bank width must satisfy `N × pedal_spacing ≤ pedal_box_width − 2×pedal_half_width` (clamp pedal_spacing down, else reject-resample). `pedal_count` is independent of case family and lid choice (four_pedals applies to the pedal layer only — never forces a case-body change, per source map exclusion).

### Axis 2: `visible_string_count` — grand-family exposed string rows

- `count_param`: `visible_string_count`.
- `N_range`: grand product domain `[20, 32]`; test domain `{24, 26, 30}`; nominal default `26` (observed parent loop emits 26 rows).
- sampling domain: center-biased around the observed count, e.g. `P(26)=0.50`, `P(24)=0.25`, `P(30)=0.25` for test draws; product draws may use integer jitter across `[20,32]` with higher weight near 26.
- copied object: one fixed visible string row visual, named `string_{i}`. Rows use steel/copper material variation consistent with the existing grand samples.
- placement: rows are distributed across the grand soundboard/cast-iron-plate span, with endpoints interpolated from bass-side to treble-side anchors. All rows stay inside the rim, above the soundboard, below closed-lid clearance, and within the plate/string field.
- joint policy: no joints; each row is a fixed visual on the grand `case` root.
- source/gating: string emission loop from grand parent `model.py:L162-L180` (baby grand uses the same structure after compact outline scaling). This axis is **grand-family only** (`grand_case`, `baby_grand_case`). Upright-family cases keep strings hidden behind the cabinet and do not expose this visible exterior multiplicity.
- semantics: `visible_string_count` is a visible-row density axis for open-lid visual diversity, not the real physical piano string count and not coupled to the 88-key keyboard.

No other template-level copy logic: the 52-white/36-black keyboard is a fixed structural layer (always identical) and is NOT exposed as a count; lid leaves are an enum (1 vs 2 via `split_top_lid`), not a free count.

## 拓扑多样性审计

总组合数（不含连续 scale，含 multiplicity 与兼容门控）：

- Slot A = 4 (grand, upright, baby_grand, spinet)
- Slot B = 3 (standard, split_top_lid, sliding_fallboard) — but family-gated
- Slot C music-support = 2 (fixed, fold_down_music_desk) — grand-family-gated
- `pedal_count` = 3 sampled values {2,3,4}
- `visible_string_count` = 3 sampled test values {24,26,30} for grand-family cases only; upright-family cases keep strings hidden/fixed

Family-aware legal count:
- grand family (grand_case, baby_grand_case) × Slot B∈{standard, split_top_lid} = 2×2 = 4
- upright family (upright_case, spinet_upright_case) × Slot B∈{standard, sliding_fallboard} = 2×2 = 4
- × music-support: grand family ×2 (fixed/fold), upright family ×1 (fixed only) = grand 4×2=8, upright 4×1=4 → 12 legal (A,B,music) topologies.
- × pedal_count {2,3,4}: grand 8×3=24, upright 4×3=12.
- × visible_string_count {24,26,30} for grand only: grand 24×3=72; upright remains 12×1=12.
- → **84 legal topology / part-count combos** (distinct part-tree/joint-count signatures even before colorways).

理由：84 ≥ 10 with wide margin, and each combo is genuinely distinct in part tree / joint count: case-family fork changes the root part name + lid hinge axis + fallboard joint *type* (REVOLUTE fold vs PRISMATIC slide); split_top_lid adds a 2nd lid part + joint; fold_down_music_desk adds a moving part + joint; pedal_count changes the number of pedal parts+joints; grand-family visible_string_count changes the number of fixed string-row visuals on the case root. Adding 5 colorways multiplies *visual* diversity (not topology), so the 1000-seed topology-distinct rich-category guideline ≥300 (report-only) is met by 84 topology/part-count combos × seed-varied continuous scales clustering into well over 100 distinct AABB/proportion signatures.

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` (1) weighted-picks case family (grand 0.5 / upright 0.5), then case_module within family (parent vs compact variant ≈ 0.6/0.4); (2) picks Slot B compatible with that family (standard 0.55, family-special 0.45); (3) picks music_support (grand: fixed 0.6 / fold 0.4; upright: fixed 1.0); (4) weighted-draws `pedal_count` ∈{2,3,4} (0.30/0.62/0.08); (5) for grand-family cases only, draws `visible_string_count` from {24,26,30} in tests or integer-jitter [20,32] in product, biased toward 26; upright fixes this axis hidden/unexposed; (6) samples independent continuous scales (body_width_scale, case_depth_scale or cabinet_height_scale, pedal_spacing) uniformly, then clamps via the §7 inequalities in `resolve_config`. Compatibility matrix gates illegal (family, lid), (upright, fold_down), and (upright, visible string axis) combos before build. No curated/modulo seed table; `seed=0` is ordinary. random sweep seeds 0-49 for the first pass, 0-999 for the maturity audit + viewer 目检 of grand-closed, grand-open-lid with sparse/dense strings, upright-closed, upright-sliding-cover, split-both-leaves, 4-pedal, and fold-down-rest poses.
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）; feasible — 84 topology/part-count combos × continuous-scale proportion buckets clear 100.
Controlled local parameterization：`body_width_scale` [0.94,1.06] independent; `case_depth_scale` (grand) [0.92,1.10] / `cabinet_height_scale` (upright) [0.78,1.06] independent; `pedal_spacing` [0.038,0.046] independent. All clamped/derived in `resolve_config`: keyboard span (52×WHITE_PITCH) must fit between key blocks after width scale; fallboard hinge_z derived from the scaled front-shelf/nameboard top (grand) so the folded fallboard never floats; pedal-bank width inequality; grand string endpoints derived after case scaling so rows stay inside the rim/plate field. Continuous scales do not change joint topology or the InterfaceSpec/MatingContract — they only move safe proportions/clearances; the two count axes change copied part/visual counts under explicit gates. Sampling contract: independent scales first → no equation chains here → project pedal-bank + keyboard-span + fallboard-seat + grand-string-field inequalities → resolve conditional lid/fallboard/music ranges from the chosen modules.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted family→case→lid→music→pedal_count→visible_string_count(grand only) then independent scales; compatibility gates before build | slot_choices_for_seed matches build choices |
| compatibility matrix | grand⇒{standard,split}; upright⇒{standard,sliding}; fold_down_music_desk⇒grand only; visible_string_count⇒grand only; pedal_count independent of A/B | no floating lid/fallboard, no upright-spline lid, no upright music-desk, valid pedal axis, pedal-bank width ≤ box, grand strings inside rim/plate field |
| controlled local variation | body_width / case_depth(grand) / cabinet_height(upright) / pedal_spacing scales, clamped | proportions vary; keyboard still fits, fallboard seats, lid still closes on rim/shell, pedals still on box |
| regression overrides | none (sufficient procedural diversity; add only if a seed regresses) | n/a |
| random sweep | seeds 0-49 initial, 0-999 maturity | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A case/body | 4 | yes | yes | grand/upright families, each with full + compact variant |
| B lid/fallboard | 3 | yes | yes | standard + 1 grand-special + 1 upright-special (family-gated, but ≥2 always reachable per family) |
| C pedal/music | 3 | yes | yes | three_pedals, four_pedals (multiplicity), fold_down_music_desk |

## Validator

- slot_choices_for_seed returns implemented module names (case_module, lid_fallboard_module, music_support_module) + pedal_count + visible_string_count (grand only / hidden for upright)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds; seed=0 not special
- compatibility matrix prevents illegal (family,lid), (upright,fold_down_music_desk), and (upright,visible_string_count) combinations before build
- optional regression overrides are sparse/none and justified
- final template does not cycle a small curated table as the main seed domain
- controlled local scales (body_width / case_depth / cabinet_height / pedal_spacing) are clamped in resolve_config and cannot make the keyboard overflow the key blocks, the fallboard float, the lid miss the rim/shell, the pedal bank exceed the box, or grand strings escape the rim/plate field
- cross-part scale dependencies resolved in resolve_config (keyboard-span fit, fallboard-seat z, pedal-bank width, grand-string endpoints), not left to fail in builder
- InterfaceSpec/MatingContract: lid hinge on case top ring/edge; fallboard hinge/slide on front shelf/ledge; pedals on pedal box front; (grand) music_rest on music_desk_base rail
- key joints: top lid REVOLUTE (grand spine `(0,-1,0)` / upright rear `(-1,0,0)`); fallboard REVOLUTE `(1,0,0)` (grand) or PRISMATIC `(0,-1,0)` (upright); each keyboard key PRISMATIC `(0,0,-1)`; each pedal REVOLUTE `(1,0,0)`; (split) two lid leaf REVOLUTE; (fold) music_rest REVOLUTE `(1,0,0)`
- copied pedals follow `pedal_{i}` naming + centered placement policy
- grand visible string rows follow `string_{i}` naming, stay inside the rim/plate field, and are not exposed for upright-family cases

## Reject cases

- A lid that does not lift upward when opened (free edge AABB top does not rise), or a closed lid that crushes/penetrates the strings/soundboard (closed lid must clear interior).
- A fallboard that floats above the shelf/ledge, or (grand) a fallboard whose folded pose drops below `WHITE_KEY_TOP_Z` into the keys, or (upright) a slide that changes z (must stay level).
- `split_top_lid` or `fold_down_music_desk` paired with an upright case, or `sliding_fallboard` paired with a grand case (family-incompatible Slot B/C).
- A keyboard that is not 52 white + 36 black, keys that don't press straight down, or key span overflowing the key blocks after width scaling.
- Pedals that do not depress at the front, or a pedal bank wider than the pedal box (overlapping/floating pedals), or pedal_count outside [2,4].
- For grand-family cases, visible string rows must stay inside the rim/soundboard footprint, above the soundboard, below closed-lid clearance, and within the cast-iron plate/string field; visible_string_count outside [20,32] is rejected.
- Exposing `visible_string_count` as an exterior multiplicity axis on upright-family cases, or coupling it to the 88-key keyboard count.
- Missing hero identity geometry: no cast-iron plate + strings (grand), no upper front panel/cabinet (upright), no brass pedals, or no fallboard.
- Treating the fixed keyboard layer as a multiplicity axis, or exposing a `key_count`/`lid_leaf_count` free parameter. The only exposed count axes are `pedal_count` and grand-only `visible_string_count`.

## 与相邻类别的边界

- 不该混入：**电子琴 / synthesizer keyboard (Electronic keyboard)** — those are slim keyboards on a stand with no acoustic case, no upward-opening lid, no cast-iron plate/strings, and no foot-pedals-on-a-lyre. The piano identity requires the heavy case/cabinet + lid + pedals.
- 不该混入：**harpsichord / clavichord** — visually similar wing case but plucked action, no cast-iron plate, no sustain-pedal lyre, and lighter legs; excluded by the grand identity (gold plate + strings + 3 pedals) and the upright identity.
- 不该混入：**organ console / harmonium** — multiple keyboard manuals + stop knobs + a tall pipe/reed cabinet; piano has exactly one keyboard manual in a single case.
- 不该混入：**generic cabinet / sideboard (Cabinet, Bar furniture)** — an upright piano's tall black cabinet can read as furniture, but the protruding keyboard shelf + fallboard + floor pedals + top lid are required for piano identity.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。注意：(1) baby_grand 的 fallboard hinge 已修到 z=0.796 以坐在 nameboard 上 — case_module 候选必须把 fallboard 挂在 case 上且 hinge_z 随 case 比例派生，不得悬浮（见实现备注）；(2) Slot B 由 case 家族门控（grand⇒{standard,split}, upright⇒{standard,sliding}）；(3) grand fallboard 有两种 rest 约定（vertical-fold-down vs flat-fold-up），模板的 standard_lid_fallboard 取 flat-fold-up 较安全；(4) `visible_string_count` 是 grand-only 可见弦列密度轴，不是真实钢琴总弦数，也不得暴露到 upright。 |

## 模板实现备注（可选）

- **Case-footprint ↔ fallboard-mount coupling (从 baby_grand fix 提炼)**: the grand fallboard is a child of the `case` and MUST stay seated on the case's front shelf / nameboard — never a floating part. In `baby_grand`, when the case footprint shrank (`TAIL_Y` 1.86→1.50, control points pulled in), the fallboard hinge had to be lowered from z=0.800 to **z=0.796** to seat on the nameboard top. Implementation rule: derive `fallboard_hinge_z = front_shelf_top_z` (i.e. from the case's scaled nameboard/front-shelf geometry, not a hardcoded literal) so any `case_depth_scale` / `body_width_scale` keeps the folded fallboard touching the case. The fallboard panel width (1.27) tracks `body_width_scale` so it stays within the key blocks. Validator should assert the fallboard's at-rest AABB touches the shelf top (gap≈0) and its folded pose stays above `WHITE_KEY_TOP_Z`.
- The 52-white/36-black keyboard helper is identical across all samples — implement once as a shared `_emit_keyboard(case, keybed_top_z, …)` consumed by both families.
- `grand_case` and `baby_grand_case` share the `_piano_outline` / `_scale_profile` / `_centroid` helpers and the `ExtrudeWithHolesGeometry` rim; `case_depth_scale` interpolates the bentside control points between the full-grand and baby-grand sets rather than a single uniform scale (keeps the curve plausible).
- `upright_case` and `spinet_upright_case` differ only in `SHELL_TOP_Z` + upper-panel height; implement as one builder with `cabinet_height_scale`.
- `split_top_lid` needs `PianoHingeGeometry` (already imported in that source) for the brass knuckle strips; both leaves share a spine-hinge helper. Element-scoped `allow_overlap` likely needed where each hinge strip overlaps its leaf panel and where `rest_lip` overlaps `rest_panel` in `fold_down_music_desk`.
- Pedal multiplicity loop (`pedal_{i}`, centered offsets) remains the only moving-part count helper.
- Grand visible string multiplicity (`string_{i}`) should reuse the existing grand string emission loop. Derive bass/treble endpoints from the scaled grand outline/plate anchors, then interpolate `i/(N-1)` across the field. This keeps string density varied while preserving the same case interface. For baby-grand/depth-scaled cases, endpoints must be recomputed after outline scaling so strings never escape the rim. Keep this helper visual-only: no joints, no coupling to keyboard count, and no upright exterior string rows.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | grand_case | rec_a-glossy-black-grand-piano-…_be39da53 (parent A) | L51-L269 | grand `case` root: rim/soundboard/plate/visible string loop/legs/lyre + keyboard host |
| S2 | A | upright_case | rec_a-glossy-black-upright-piano-…_c63fde85 (parent B) | L42-L135 | upright `body` root: cabinet/panels/key-shelf/pedal-mount |
| S3 | A | baby_grand_case | rec_piano_var_baby_grand_body | L51-L269 | compact grand footprint (`TAIL_Y=1.50`) + fallboard-seat fix (z=0.796) |
| S4 | A | spinet_upright_case | rec_piano_var_spinet_upright_body | L26, L43-L136 | spinet-height upright (`SHELL_TOP_Z=0.940`) |
| S5 | B | standard_lid_fallboard | parents A & B | A L271-L320; B L137-L178 | one-piece lid + family fallboard (REVOLUTE fold / PRISMATIC slide) |
| S6 | B | split_top_lid | rec_piano_var_split_top_lid | L274-L399 | two-leaf lid + per-leaf PianoHinge + REVOLUTE joints |
| S7 | B | sliding_fallboard | rec_piano_var_sliding_fallboard | L121-L193 | slide tracks + handle + long PRISMATIC fallboard travel |
| S8 | C | three_pedals/four_pedals | parents + rec_piano_var_four_pedals | A L370-L393; four L369-L399 | pedal bank + `pedal_count` multiplicity loop |
| S9 | C | fold_down_music_desk | rec_piano_var_fold_down_music_desk | L257-L294 | articulated `music_rest` REVOLUTE on fixed base rail |
| S10 | A | visible_string_count | grand parent + baby grand | A L162-L180; baby same | grand-only fixed visible string-row multiplicity (`string_{i}`), observed N=26 and sampled as visible row density |
