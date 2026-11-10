# pilers_tongue_groove_pliers — Modular Spec

> Source subcategory: `pictureX/0611/Pilers_tongue_groove_pliers` (articraft_data upstream 5★ pool).
> Object identity: a manual **tongue-and-groove / water-pump pliers** — a two-shank forged plier where a **slotted_shank** carries a straight toothed **through-slot** (the "groove" row) and a **tongue_shank** carries a **solid engaging tongue** that seats against one of N groove positions along that slot; the carriage/pivot rides captured in the slot along a slanted `slot_axis` and the tongue_shank rotates about the pivot to open/close the jaws.
> Upstream source map: `picture_expansion/template_source_maps/0611__Pilers_tongue_groove_pliers.md`.
> Sync state: 10 × 5★ records synced under `data/records/rec_0611_pilers_tongue_groove_pliers_*` + 1 origin `rec_picturex_0611__pilers_tongue_groove_pliers__001__png_798a9eeaa0c746c8bb3955b5e25fc589`.
> Baseline skeleton: 3-part / 2-joint chain — `slotted_shank` (ROOT, carries slot + jaw + grip), `pivot_carriage` (captured hardware), `tongue_shank` (mating tongue + jaw + grip). `slot_setting` PRISMATIC axis=(slot_axis[0], 0, slot_axis[1]) slides carriage along slot; `jaw_pivot` REVOLUTE axis=+Y rotates tongue_shank about carriage. push_button_carriage adjustment adds a `push_button` part + `button_press` PRISMATIC axis=-Y (4-part / 3-joint).

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_tongue_groove_pliers` |
| template path | `agent/templates/pilers_tongue_groove_pliers.py` |
| test path (optional) | 无（sweep-pipeline 唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（linear_chain slotted_shank→carriage→tongue_shank；push_button adjustment 追加 carriage→button 分支；groove_positions 是 slotted_shank 内 tooth 数量的 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 (+1 origin) |
| read_count | 11 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

Samples and adoption:
- **P0 origin_anchor** (`rec_picturex_0611__pilers_tongue_groove_pliers__001__png_798a9eeaa0c746c8bb3955b5e25fc589`): 3-part skeleton — `slotted_shank` (root, forged polyline + slanted `slot_cutter` through-slot + 8 tooth cuts + straight serration + blue grip), `pivot_carriage` (round rivet: shaft + two heads), `tongue_shank` (mirrored forged polyline + pivot boss + engaging_tongue + serration + blue grip). PRISMATIC `slot_setting` (slotted_shank→carriage, axis=slot_axis, `[0, 0.036]`) + REVOLUTE `jaw_pivot` (carriage→tongue_shank, axis=+Y, `[-1.05, +0.42]`). Baseline: straight_serrated jaw + slotted_rivet_carriage + 8_position + standard_dipped handle.
- **V-P1 groove_positions=3** (`rec_..._var_groove_positions_3`): `GROOVE_POSITIONS=3`; slot tooth cut count = 3 along same 0.058m slot; joint ranges unchanged. Slot C source (3).
- **V-P2 groove_positions=5**: `GROOVE_COUNT=5`, `GROOVE_PITCH=0.008`, `GROOVE_TRAVEL=0.032`, prismatic upper=GROOVE_TRAVEL. Slot C source (5).
- **V-P3 groove_positions=7**: 7 tooth cuts, upper=0.036 (baseline slot length). Slot C source (7).
- **V-J1 deep_v_pipe_jaw** (`rec_..._var_jaw_form_deep_v_pipe_jaw`): both shanks' jaw faces replaced with a `_deep_v_pipe_jaw` insert — two angled serrated V-faces meeting at a vertex offset `v_depth=0.016` into the jaw body, `tooth_count_per_face=5`. Diamond pipe cavity when opposing. Slot A source (deep V pipe).
- **V-J2 replaceable_smooth_pads**: jaw_face replaced with a flat rect insert (`_smooth_jaw_pad`); no teeth. `jaw_face_style="replaceable_smooth_pad"`. Slot A source.
- **V-J3 narrow_offset_jaw**: jaw_face polyline narrowed and offset toward one side; retains straight serration but on a narrower face. Slot A source.
- **V-A1 adjustment_box_joint**: same 3-part / 2-joint skeleton; `slotted_shank`'s forging widened at the pivot region with a rectangular box-joint opening (visual + wider slot region + metadata `variant=box_joint`); carriage unchanged. Slot B source (box_joint_opening).
- **V-A2 adjustment_push_button_carriage**: adds `push_button` part + PRISMATIC `button_press` (carriage→button, axis=-Y, `[0, 0.004]`). Carriage body becomes rectangular block with pivot bore + button bore. 4-part / 3-joint. Slot B source (push_button_carriage).
- **V-H1 handle_extended_leverage_handle**: both shanks' `blue_handle_grip` polylines extended in -Y direction (reach below -0.290); jaw_pivot effort reduced (240→180). Slot D source.
- **V-H2 handle_guarded_grip**: both shanks' grip polylines gain a finger-guard flange on the outboard face; adds member↔member allow_overlap `finger guard flange near opposing shank`. Slot D source.

Redundancy: all 10 fork variants share the 3-part / 2-joint core; only push_button_carriage changes chain topology (+1 part / +1 joint). Others are `_jaw_face` / `_grip` polyline swaps or slot tooth count.

## 核心身份

A manual **tongue-and-groove (water-pump) pliers**: two crossed forged shanks joined by a captured pivot that slides in a toothed through-slot on the slotted_shank. Adjusting the pivot's position along the slot re-seats the tongue_shank's solid tongue against a different tooth pair, changing the effective jaw opening. Both shanks carry a jaw face (straight serration / deep-V pipe jaw / smooth pad / narrow offset) and a vinyl blue handle grip.

Object lies in the XZ plane with the pliers axis along -Z (jaws toward +Z, handles toward -Z). `slot_axis = (-0.342, -0.940)` (unit vector) with prismatic travel `[0, 0.036]` along that axis. Y is the plier thickness direction; `jaw_pivot` axis is +Y.

Default mature domain: real hand-tool scale (overall length ~0.28–0.34 m, forging thickness ~0.008 m). jaw_form ∈ {straight_serrated / deep_v_pipe_jaw / replaceable_smooth_pads / narrow_offset_jaw}; adjustment ∈ {slotted_rivet_carriage / box_joint_opening / push_button_carriage}; groove_positions ∈ {3, 5, 7, 8}; handle_form ∈ {standard_dipped / extended_leverage_handle / guarded_grip}.

Not to be confused with: **slip_joint_pliers**（同族但仅 2 detent, 无 groove tooth 阵列）；**needle_nose / linesman / cutting_pliers**（固定 pivot）；scissors / shears; wrench; tweezers.

## 槽位 + 候选模块表

> Structural note: the tongue_groove skeleton is 3-part / 2-joint (slotted_shank as ROOT / pivot_carriage / tongue_shank). **Slot B (adjustment)** decides chain topology (slotted_rivet_carriage / box_joint_opening keep 3-part; push_button_carriage adds +1 part +1 PRISMATIC). **Slot A (jaw_form)** swaps both shanks' `jaw_face` visual. **Slot C (groove_positions)** is a multiplicity axis on the slotted_shank's tooth cuts and does NOT change joint topology (the slot length stays 0.058 m; tooth count varies). **Slot D (handle_form)** swaps both shanks' `blue_handle_grip` polyline.

### Slot A：jaw_form (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| straight_serrated (baseline) | origin_anchor | P0 | `_serration_strip` L64-101, roots L187-200 / L345-358 | eligible if compatible | Planar Boundary Form | 9 齿平锯齿列沿 jaw face 平面；`jaw_face_style="straight_opposing_serration_row"` |
| deep_v_pipe_jaw | forked_anchor | V-J1 | `_deep_v_pipe_jaw` L107-176, root_v_jaw L263-277 / tongue_v_jaw L420-433 | eligible if compatible | Volumetric Envelope Form | 深 V 形 pipe-gripping 双面锯齿槽,`v_depth=0.016`, `tooth_count_per_face=5`；两颚合形成菱形管夹腔 |
| replaceable_smooth_pads | forked_anchor | V-J2 | `_smooth_jaw_pad` L104-137 | eligible if compatible | Planar Boundary Form | 平面无齿光垫（rect thin extrude）代替齿列；`jaw_face_style="replaceable_smooth_pad"` |
| narrow_offset_jaw | forked_anchor | V-J3 | `_serration_strip` narrowed L188 (count=7) | eligible if compatible | Planar Boundary Form | 窄 offset 齿列（7 齿而非 9）；`jaw_face_style="straight_opposing_serration_row"` 且 `jaw_tooth_count=7` |

> 4 candidates（达到目标 3-6）。Planar Boundary Form × 3 + Volumetric Envelope Form × 1。

### Slot B：adjustment (② joint / mechanism)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| slotted_rivet_carriage (baseline) | origin_anchor | P0 | rivet_shaft L228-233, rear_head/front_head L234-245, slot_setting L384-401, jaw_pivot L402-419 | eligible if compatible | 圆柱铆钉 pivot 铁件（shaft + 前后 heads）; `slot_setting` PRISMATIC axis=slot_axis; `jaw_pivot` REVOLUTE axis=+Y；3-part / 2-joint |
| box_joint_opening | forked_anchor | V-A1 | box-slot forged shank L108-215 | eligible if compatible | 同 3-part / 2-joint；slotted_shank 前板增加一段矩形 box-joint 敞口（wider region 保 pivot 通过）；carriage 保持不变 |
| push_button_carriage | forked_anchor | V-A2 | pivot_carriage rect block L222-285, push_button part L287-323, button_press PRISMATIC L474-490 | eligible if compatible | 追加 `push_button` part（stem + cap + grip_ring, red）+ PRISMATIC `button_press` carriage→button axis=-Y range `[0, 0.004]`；carriage body 改为 rect block with pivot bore + button bore；4-part / 3-joint |

> 3 candidates（达到目标 3-6）。slotted_rivet_carriage / box_joint_opening 保 3-part；push_button_carriage +1 part +1 joint。

### Slot C：groove_positions (① multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| 3_position | forked_anchor | V-P1 | `GROOVE_POSITIONS=3` L17, tooth cut loop L219-238 | eligible if compatible | slotted_shank 上 3 个 tooth 切槽 |
| 5_position | forked_anchor | V-P2 | `GROOVE_COUNT=5` L18, PITCH=0.008, TRAVEL=0.032 | eligible if compatible | 5 tooth 切槽; PRISMATIC upper=0.032 |
| 7_position | forked_anchor | V-P3 | `slot_tooth_count=7` L131 | eligible if compatible | 7 tooth 切槽; PRISMATIC upper=0.036 |
| 8_position (baseline) | origin_anchor | P0 | 8 tooth cut loop L169-178 | eligible if compatible | 8 tooth 切槽（origin baseline），PRISMATIC upper=0.036 |

> 4 candidates. groove positions ∈ {3, 5, 7, 8}。Weight `[3, 3, 2, 2]` (small N slightly more common).

### Slot D：handle_form (③ / Planar Boundary Form)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| standard_dipped (baseline) | origin_anchor | P0 | root_grip_profile L202-213, tongue_grip_profile L360-378 | eligible if compatible | Planar Boundary Form | 短直筒 blue vinyl grip；y-range ~[-0.245, -0.088] |
| extended_leverage_handle | forked_anchor | V-H1 | root_grip_profile / tongue_grip_profile extended | eligible if compatible | Planar Boundary Form | 更长手柄（y 下探到 -0.290 以下）;jaw_pivot effort 降低 |
| guarded_grip | forked_anchor | V-H2 | root_grip_profile + finger_guard flange | eligible if compatible | Planar Boundary Form | 手柄外侧加护指 flange；`allow_overlap` finger guard 靠近对侧 shank |

> 3 candidates（达到目标下限）。

## 槽位图（slot graph）

```
pattern: mixed（3-part linear chain + optional push_button branch）

  ── Slot B = slotted_rivet_carriage / box_joint_opening（3-part / 2-joint）──
    slotted_shank (root)
      carries: forged polyline + slot_cutter through-slot（along slot_axis）+ N groove tooth cuts + jaw_face(Slot A) + blue_grip(Slot D)
        │
        │ [PRISMATIC slot_setting, axis=(slot_axis[0], 0, slot_axis[1]), origin=Origin(), range [0, 0.036]]
        ↓
    pivot_carriage
      carries: round rivet (shaft + rear_head + front_head) OR rect block for push_button
        │
        │ [REVOLUTE jaw_pivot, axis=(0,1,0), origin=Origin(), range [-1.05, +0.42]]
        ↓
    tongue_shank
      carries: mirrored forged polyline + pivot_boss + engaging_tongue + jaw_face(Slot A, mirrored) + blue_grip(Slot D, mirrored)

  ── Slot B = push_button_carriage（4-part / 3-joint）──
    pivot_carriage ── [PRISMATIC button_press, axis=(0,-1,0), origin=(0, 0.009, -0.004), range [0, 0.004]] ──> push_button
```

Interface points:
- **slotted_shank → pivot_carriage (`slot_setting`)**: mating = pivot_rivet shaft with slot through-hole; joint = PRISMATIC, axis=(slot_axis[0], 0, slot_axis[1]), origin=Origin(), range `[0, 0.036]`. MatingContract omitted (captured-pin grandfathered); expressed via `allow_overlap(pivot_carriage, slotted_shank, elem_a="pivot_rivet", elem_b="slotted_forging")` + `expect_overlap`.
- **pivot_carriage → tongue_shank (`jaw_pivot`)**: mating = rivet shaft with tongue_shank's pivot_bore; joint = REVOLUTE, axis=(0,1,0), origin=Origin(), range `[-1.05, +0.42]`. MatingContract omitted (captured-pin); `allow_overlap(pivot_carriage, tongue_shank, elem_a="pivot_rivet", elem_b="tongue_forging")` + `expect_contact`.
- **pivot_carriage → push_button (Slot B = push_button_carriage)**: mating = button stem with carriage's button bore; joint = PRISMATIC axis=(0,-1,0), origin=(0, 0.009, -0.004), range `[0, 0.004]`. `allow_overlap` covers.
- **engaging_tongue vs slotted_forging**: `allow_overlap` (`reason="tongue seats against slot tooth wall"`) + `expect_overlap` for retained insertion.
- **jaw_teeth / grip / decorative markers**: inline visuals of the parent part (FIXED), not independent parts.
- **Mutually exclusive / optional**: push_button_carriage adjustment adds `push_button` part + PRISMATIC. Other slots orthogonal.

## 每槽位 Module Emits / Interfaces

### Slot A / straight_serrated
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on each shank: `straight_jaw_serrations` mesh — `_serration_strip` polyline extrude at jaw face | P0 / L187-200, L345-358 |

### Slot A / deep_v_pipe_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on each shank: `deep_v_pipe_jaw` mesh — 2 angled serration faces + vertex bridge | V-J1 / L107-176 |

### Slot A / replaceable_smooth_pads
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on each shank: `smooth_jaw_pad` rect thin extrude | V-J2 |

### Slot A / narrow_offset_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on each shank: `straight_jaw_serrations` with count=7 and narrower width | V-J3 |

### Slot B / slotted_rivet_carriage
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_carriage.pivot_rivet` = cylinder shaft + 2 circular rivet heads | P0 / L228-245 |
| joints | `slot_setting` PRISMATIC + `jaw_pivot` REVOLUTE | P0 |

### Slot B / box_joint_opening
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on slotted_shank: same forging with a wider rectangular box-joint window around the pivot region (visual only) | V-A1 |
| joints | same as slotted_rivet_carriage (3-part/2-joint) | V-A1 |

### Slot B / push_button_carriage
| emits | 描述 | 来源 |
|---|---|---|
| parts | new `push_button` part (stem + cap + grip_ring, red) | V-A2 / L287-323 |
| visuals | `pivot_carriage.carriage_body` = rect block with pivot bore + button bore; `push_button.button_geom` | V-A2 |
| joints | adds `button_press` PRISMATIC axis=-Y range `[0, 0.004]` (4-part / 3-joint chain) | V-A2 / L474-490 |

### Slot C / 3_position / 5_position / 7_position / 8_position
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on slotted_shank: N tooth cuts along slot_axis (`for i in range(N): cut tooth`) | V-P1/2/3 + P0 |
| joints | slot_setting upper unchanged (0.036) | P0 |

### Slot D / standard_dipped / extended_leverage_handle / guarded_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | on each shank: `blue_handle_grip` polyline (extended or with finger-guard flange) | P0 / V-H1 / V-H2 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_form | enum | {straight_serrated, deep_v_pipe_jaw, replaceable_smooth_pads, narrow_offset_jaw} | straight_serrated | choice | procedural sampler | Slot A |
| adjustment | enum | {slotted_rivet_carriage, box_joint_opening, push_button_carriage} | slotted_rivet_carriage | choice | procedural sampler; decides 3-part vs 4-part | Slot B |
| groove_positions | int (multiplicity) | {3, 5, 7, 8} | 8 | choice | procedural sampler; N tooth cuts | Slot C |
| handle_form | enum | {standard_dipped, extended_leverage_handle, guarded_grip} | standard_dipped | choice | procedural sampler | Slot D |
| palette_style | enum | {steel_blue, gunmetal_red, chrome_dark_blue, black_yellow, industrial_green, brushed_steel_orange} | steel_blue | palette | **palette only, no slot_choice, no topology** | P0 + world knowledge |
| overall_len_scale | float | [0.92, 1.10] | 1.0 | independent | overall body y-scale; clamp | P0 length ~0.325 |
| jaw_face_scale | float | [0.92, 1.08] | 1.0 | independent | scales serration/pad footprint | P0 jaw face |
| grip_girth_scale | float | [0.92, 1.08] | 1.0 | independent | scales grip x half-width | P0 grip |
| open_angle_scale | float | [0.85, 1.15] | 1.0 | independent | scales REVOLUTE ranges; clamp | P0 `[-1.05, +0.42]` |
| (—) | constraint | — | — | inequality | pivot_rivet shaft stays captured within slot (slot_length ≥ prismatic upper + 2*shaft_r + margin) | captured-pin |
| (—) | constraint | — | — | inequality | groove tooth cuts must fit within slot_length: `N * tooth_pitch ≤ slot_length - 2*margin` | Slot C ×  slot geom |

Continuous scales default independent; inequalities clamp in `resolve_config`. `palette_style` swaps material rgba only.

### 7.5 编译预算 / compile budget

Self-declared per-seed budget **~15-25 s**. Justification: 3-4 parts, each with polyline extrude + slot_cutter cut + N tooth polyline cuts (dominant CQ cost is `_serration_strip` or `_deep_v_pipe_jaw` union — moderate polyline count, no lofts). Tessellation: default tolerance 0.00025-0.0004; slot_cutter thickness 0.030 (wider than shank thickness 0.008 for full cut-through).

## Multiplicity / Copy Logic

- `count_param`: `groove_positions_count` (Slot C)
- `N_range`: {3, 5, 7, 8}
- sampling domain: weighted `[3, 3, 2, 2]` (small N slightly more common)
- copied object: `slotted_shank` tooth cut polyline (via CQ `.cut` in a for-loop; not an independent part)
- naming: no visual name per tooth; teeth are subtractive on `slotted_forging` visual
- placement: `v0 = 0.009 + i * pitch` along slot_axis in local shank frame; pitch = min(0.0056, (slot_length - 0.020) / max(N-1, 1))
- joint policy: no independent joint (subtractive geometry only)
- source / gating: {3, 5, 7, 8} all sourced

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B adjustment: slotted_rivet_carriage / box_joint_opening (3-part/2-joint) vs push_button_carriage (4-part/3-joint, +PRISMATIC button_press); source_type=forked_anchor (V-A2) |
| └ multiplicity | 同构件 ×N | 有 | Slot C groove_positions ∈ {3, 5, 7, 8}; source_type=origin_anchor + forked_anchor (V-P1/2/3) |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | baseline = 1 PRISMATIC (slanted axis) + 1 REVOLUTE (+Y); push_button_carriage adds 1 PRISMATIC (-Y); source_type=forked_anchor (V-A2) |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot A jaw_form: straight_serrated (Planar Boundary Form), deep_v_pipe_jaw (Volumetric Envelope Form), replaceable_smooth_pads (Planar Boundary Form), narrow_offset_jaw (Planar Boundary Form); Slot D handle_form: standard_dipped / extended_leverage_handle / guarded_grip (all Planar Boundary Form 变体); source_type=forked_anchor (V-J1/2/3, V-H1/2) + origin_anchor (P0) |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | slot tooth cut count (Slot C — 3/5/7/8 subtractive marks); box_joint_opening visual widening; push_button red cap; guarded_grip finger flange; all host-conformal; source_type=record_only |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | overall_len_scale [0.92,1.10], jaw_face_scale [0.92,1.08], grip_girth_scale [0.92,1.08], open_angle_scale [0.85,1.15]; motion envelopes: slot_setting PRISMATIC axis=(slot_axis[0], 0, slot_axis[1]) upper=0.036; jaw_pivot REVOLUTE axis=+Y `[-1.05, +0.42]`; button_press PRISMATIC axis=-Y `[0, 0.004]` (push_button branch); motion_test_plan: sampled collision + targeted `ctx.pose(...)` for slot_setting=upper (carriage slides), jaw_pivot=lower (jaws open); rest-vs-open grip AABB comparison |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | palette_style 6 档: steel_blue / gunmetal_red / chrome_dark_blue / black_yellow / industrial_green / brushed_steel_orange; metal (3) + vinyl/rubber (3) ≥ ceil(0.5×6)=3 |

**收尾自检**: All "有" values must be visible in the 0-9 seed batch renders — 4 jaw_form spread, 3 adjustments visible (incl. push_button 4-part chain), 4 groove_position counts visible, 3 handle_forms visible, all 6 palettes covering metal + vinyl.

## 采样与覆盖审计

Total combinatorial: jaw_form(4) × adjustment(3) × groove_positions(4) × handle_form(3) = **144** topology-equivalence classes.

Reasoning: discrete slots alone give 144; mature enough coverage. Slot C multiplicity axis is factored in.

seed_domain_policy: `procedural_first`.
Procedural Sampling / Sweep Plan: `config_from_seed(seed)` does deterministic procedural sampling — weighted picks for jaw_form / adjustment / groove_positions / handle_form + continuous scales; `resolve_config` clamps. `seed=0` not special. No regression overrides in v1 (add sparsely if sweep exposes a failure).
Topology target: 1000-seed slot choice tuple distinct target = 144 (report-only).
Controlled local parameterization: `overall_len_scale`, `jaw_face_scale`, `grip_girth_scale`, `open_angle_scale`, all clamped.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | order: jaw_form → adjustment → groove_positions → handle_form → scales → palette; weighted | slot_choices_for_seed matches build choices |
| compatibility matrix | (1) all slots orthogonal. (2) pivot_rivet stays captured within slot: `(slot_length - 0.020) ≥ slot_setting.upper`. (3) push_button_carriage branch adds part + PRISMATIC; other slots unaffected. (4) captured-pin overlap covered by allow_overlap. (5) engaging_tongue-vs-slotted_forging seated overlap covered. | no floating / collision (except allowed captured-pin) / joint range violation |
| controlled local variation | 4 clamped scales | proportions vary without breaking interfaces, clearance, joint origin, or category identity |
| regression overrides | none | only add if sweep exposes failed seed |
| random sweep | 0-35 initial, 0-999 maturity audit | captured-pin overlap; jaw teeth meet without float; grip not intersecting opposing shank; push_button 4-part assembly; deep_v_pipe_jaw diamond cavity |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A jaw_form | 4 | yes | yes | straight_serrated / deep_v_pipe_jaw / replaceable_smooth_pads / narrow_offset_jaw |
| B adjustment | 3 | yes | yes | slotted_rivet_carriage / box_joint_opening / push_button_carriage(+1 part +1 PRISMATIC) |
| C groove_positions | 4 | yes | yes | 3 / 5 / 7 / 8 |
| D handle_form | 3 | yes | yes | standard_dipped / extended_leverage_handle / guarded_grip |

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating: all slots orthogonal; captured-pin overlap covered
- optional regression overrides initially empty
- controlled local scales all clamped
- critical captured-pin overlap: `allow_overlap(pivot_carriage, slotted_shank, elem_a="pivot_rivet", elem_b="slotted_forging")` + `allow_overlap(pivot_carriage, tongue_shank, elem_a="pivot_rivet", elem_b="tongue_forging")` + `allow_overlap(tongue_shank, slotted_shank, elem_a="engaging_tongue", elem_b="slotted_forging")`; two shanks share z-lap at pivot region → `allow_overlap(slotted_shank, tongue_shank, elem_a="slotted_forging", elem_b="tongue_forging")`
- key joints: `slot_setting` PRISMATIC axis=(slot_axis[0], 0, slot_axis[1]) range `[0, 0.036 × scale]`; `jaw_pivot` REVOLUTE axis=(0,1,0) range `[-1.05, +0.42] × open_angle_scale`; `button_press` PRISMATIC axis=(0,-1,0) range `[0, 0.004]` (push_button branch)
- open-close test: `pose jaw_pivot=-0.5` opens jaws (grip AABB moves outward)
- slide test: `pose slot_setting=upper` moves pivot_carriage along -X and -Z (slanted axis)
- push_button branch: `pose button_press=0.004` moves button along -Y
- palette_style swaps only rgba
- all `.visual(material=mats[...])` reference `mats` dict

## Reject cases

- pivot pin FIXED or `slot_setting` PRISMATIC missing (tongue-groove requires slidable pivot)
- pivot_rivet not captured in slot (island / floating)
- captured-pin `allow_overlap` missing → collision fail
- Slot B=push_button_carriage missing push_button part or button_press PRISMATIC
- Slot A=deep_v_pipe_jaw's V groove z越出 shank thickness
- engaging_tongue doesn't overlap slotted_forging at rest → no functional seating
- jaws don't visibly open at `jaw_pivot=lower`
- boxy placeholders in place of real forged shank polylines

## 与相邻类别的边界

- **slip_joint_pliers**: only 2 detent positions and no toothed groove array; slot_guide is separate root piece
- **needle_nose / linesman / cutting_pliers**: fixed pivot only; no sliding adjustment
- **scissors / shears**: no slip pivot; single hinge
- **wrench / spanner**: no crossed shanks
- **tweezers**: no pivot

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | first implementation; awaits sweep-pipeline `verdict=pass` |

## 模板实现备注

- Shared helpers: `_xz_prism`, `_slot_cutter`, `_serration_strip`, `_deep_v_pipe_jaw`, `_smooth_jaw_pad`, `_grip` (Slot D dispatch).
- Captured-pin: `slot_setting` and `jaw_pivot` — MatingContract omitted (grandfathered); use `allow_overlap` + `expect_overlap` / `expect_contact`.
- Slot C groove_positions changes tooth cut count; slot_length constant.
- Push_button branch: guard the extra part/joint with `r.adjustment == "push_button_carriage"`.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P0 | A/B/C/D | straight_serrated / slotted_rivet_carriage / 8_position / standard_dipped | rec_picturex_0611__pilers_tongue_groove_pliers__001__png_798a9eeaa0c746c8bb3955b5e25fc589 | full model.py | 3-part / 2-joint baseline + slot geometry |
| V-P1 | C | 3_position | rec_0611_pilers_tongue_groove_pliers_var_groove_positions_3 | L219-238 | 3 tooth pattern |
| V-P2 | C | 5_position | rec_0611_pilers_tongue_groove_pliers_var_groove_positions_5 | L175-180 | 5 tooth pattern |
| V-P3 | C | 7_position | rec_0611_pilers_tongue_groove_pliers_var_groove_positions_7 | L131 | 7 tooth pattern |
| V-J1 | A | deep_v_pipe_jaw | rec_0611_pilers_tongue_groove_pliers_var_jaw_form_deep_v_pipe_jaw | `_deep_v_pipe_jaw` L107-176 | V pipe jaw |
| V-J2 | A | replaceable_smooth_pads | rec_0611_pilers_tongue_groove_pliers_var_jaw_form_replaceable_smooth_pads | `_smooth_jaw_pad` L104-137 | smooth pad |
| V-J3 | A | narrow_offset_jaw | rec_0611_pilers_tongue_groove_pliers_var_jaw_form_narrow_offset_jaw | narrowed serration L188 | narrow offset |
| V-A1 | B | box_joint_opening | rec_0611_pilers_tongue_groove_pliers_var_adjustment_box_joint | slotted forging widened L108-215 | box joint window |
| V-A2 | B | push_button_carriage | rec_0611_pilers_tongue_groove_pliers_var_adjustment_push_button_carriage | rect carriage body L222-285, push_button part L287-323, button_press PRISMATIC L474-490 | push button branch |
| V-H1 | D | extended_leverage_handle | rec_0611_pilers_tongue_groove_pliers_var_handle_extended_leverage_handle | extended grip polylines | longer grip |
| V-H2 | D | guarded_grip | rec_0611_pilers_tongue_groove_pliers_var_handle_guarded_grip | grip + finger guard | guarded grip |
