# table_with_doors_and_drawers — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `table_with_doors_and_drawers` |
| template path | `agent/templates/table_with_doors_and_drawers.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 (2 origin anchors + 12 slot-fork variants, source map ★) |
| read_count | 14 (all fully read: origins S1/S2 + variants for drawer_count 2/3/5, door_count 2/3, closure sliding/roll_top/drop_front, support four_legs/twin_pedestal, worktop_form corner_return, secondary_motion keyboard_tray) |
| read_scope | all 5-star records under `data/records/rec_0611_table_with_doors_and_drawers_*` and `rec_picturex_0611__table_with_doors_and_drawers__00{1,2}__png_*` |
| source_index_policy | only adopted module sources indexed below |

Structure family distribution (from origin reads):

| family | evidence | notes |
|---|---|---|
| asymmetric knee desk: shallow top drawer + right-hinged door + upper cubby | S1 (001) | 1 PRISMATIC (-Y) top drawer + 1 REVOLUTE (+Z) right-hinged door + fixed upper open cubby |
| twin-pedestal desk: door pedestal (left) + drawer stack (right) | S2 (002) | 1 REVOLUTE (-Z) left cupboard door + 3 PRISMATIC (-Y) drawers with independent joints |
| variant: closure axis swap (sliding_door / roll_top / drop_front) | closure_* variants | replaces revolute door with PRISMATIC along −X (slide) / +Z (tambour) / REVOLUTE about +X (drop-front) |
| variant: support form (four_legs / twin_pedestal / corner_return) | support_* / worktop_form variants | swaps carcass support form; adds L-return worktop |
| variant: multiplicity (drawer_count 2/3/5; door_count 2/3) | count variants | procedural N repeats of drawer / door module |

## 核心身份

A **work table (desk) that combines BOTH storage doors AND storage drawers** in
a single grounded carcass. Must retain simultaneously:

1. a raised work surface (~0.72–0.78 m) that reads as a desktop, not a cabinet
   lid;
2. **≥1 real drawer** (PRISMATIC front, guided by rail/slides);
3. **≥1 real door / hinged front / closure** (REVOLUTE, PRISMATIC-slide, or
   PRISMATIC-tambour) enclosing a compartment;
4. a grounded support (pedestal, plinth, or four legs) landing the work surface
   at desk height.

Neighbors that MUST be excluded:

- Plain **desk** (drawer only, no door → belongs to
  `table_with_drawers_no_door`).
- **Filing cabinet / drawer_cabinet_with_sliding_drawers** (no raised work
  surface).
- **TV cabinet / round cabinet** (media console; storage-only without desk
  identity).
- **Roll-top secretary desk with tambour only over full compartment** — retained
  here as a `closure=roll_top` variant of a doors+drawers desk, not as an
  independent slug.
- **Office table with only doors OR only drawers** (that lives in
  `office_table_with_doors_or_drawers` when the fork is one or the other; our
  slug always emits ≥1 of each).

## 槽位 + 候选模块表

### Slot A：`worktop_form` (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `rectangular` | forked_anchor | S1 (`rec_picturex_...001`) + S2 (`rec_picturex_...002`) | S1:L79-L84, S2:L52-L57 | Planar Boundary Form | eligible | 单一矩形工作台，无返弯；S1 略窄 (0.96×0.50)，S2 更宽 (1.25×0.56) |
| `corner_return` | forked_anchor | var `worktop_form_corner_return` (`rec_0611_table_..._corner_return`) | corner_return:L37-L75, L151-L159 | Planar Boundary Form | eligible | L 形返弯工作台；主台 + 侧返翼；返翼有辅助腿或支撑桥；forked_anchor L-shape from cadquery workplane |
| `wide_rectangular` | world_knowledge_extrapolation | anchor: S2 拉宽 | (n/a; derived) | Planar Boundary Form | eligible if compatible | 同 rectangular part tree，只加宽 desk_width；标注 world_knowledge_extrapolation with same primitives + interface |

### Slot B：`closure` (② joint type / mechanism swap on the door front)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_door` | forked_anchor | S1 (001, right-hinged) + S2 (002, left-hinged) | S1:L258-L325 (door_hinge REVOLUTE +Z), S2:L154-L216 (carcass_to_cupboard_door REVOLUTE -Z) | eligible | 单-枢转门板；轴 (0,0,±1)；panel + pull + 2 hinge knuckles/leaves；opens outward toward −Y |
| `sliding_door` | forked_anchor | var `closure_sliding_door` | sliding_door:L165-L176 (tracks), L293-L301 (guide shoes), L320-L335 (door_slide PRISMATIC −X) | eligible | 水平滑门；PRISMATIC 沿 ±X；上下 2 条 track rail + 门板 top/bottom guide shoes；track sits at front face inboard of the divider |
| `roll_top` | forked_anchor | var `closure_roll_top` | roll_top:L177-L198 (tracks + housing), L288-L338 (slats + canvas + pull), L358-L374 (door_slide PRISMATIC +Z) | eligible | 垂直卷帘；PRISMATIC 沿 +Z；N 条水平 slat（visuals inside door part）+ canvas backing + 侧 track；slat 数量固定 ≥8（不做 multiplicity 变量） |
| `drop_front` | forked_anchor | var `closure_drop_front` | drop_front:L151-L158 (hinge_rail), L163-L229 (door with top_lip + bottom hinge_knuckle/leaves), L231-L243 (carcass_to_cupboard_door REVOLUTE +X) | eligible | 前倾写字板；REVOLUTE 绕 +X 轴（水平轴，位于门底部）；hinge_rail 上方 |

### Slot C：`support_form` (① skeleton — how the carcass reaches the ground)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pedestal_plinth` | forked_anchor | S1 (right pedestal + plinth), S2 (twin plinths under sides) | S1:L104-L116 (cabinet_plinth + front_plinth), S2:L99-L110 (left/right plinths) | eligible | 侧面下方的 recessed graphite/wood plinth (低承台) 直接接地；主 side_panel 从台面延伸到 plinth 顶部 |
| `twin_pedestal` | forked_anchor | var `support_twin_pedestal` | twin_pedestal:L94-L119 (symmetric dividers + twin plinths) | eligible | 左右对称双柜脚 + 中央 knee 空间；对称 divider 与 plinth；用于 door+drawer 分开的 layout |
| `four_legs` | forked_anchor | var `support_four_legs` | four_legs:L99-L118 (4 rectangular corner legs, 0.048×0.048×0.705) | eligible | 四方立腿 (corner legs) 替代 plinth；每条腿 Box 从地面到 desktop 底部 |

### Slot D：`drawer_count` (multiplicity, N ∈ [1, 5])

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `1_drawer` / `2_drawers` / `3_drawers` / `4_drawers` / `5_drawers` | forked_anchor | S1 (1), S2 (3), var `drawer_count_2` (2), var `drawer_count_3` (3), var `drawer_count_5` (5) | eligible when drawer bank is present (always in this slug: ≥1 required by identity) | N 个 PRISMATIC 抽屉沿 −Y 垂直堆叠，各带独立 joint (drawer_slide_{i}); 每个抽屉 = front panel + box (bottom/sides/back) + pull |

### Slot E：`door_count` (multiplicity, M ∈ [1, 3])

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `1_door` / `2_doors` / `3_doors` | forked_anchor | S1 (1), S2 (1), var `door_count_2` (2), var `door_count_3` (3) | eligible only when `closure ∈ {hinged_door, drop_front}`; degrade to 1 for sliding_door / roll_top | M 个 REVOLUTE 门板并列（hinged）或单一大门（sliding/roll_top）；face_frame_stile 分割 M ≥ 2 时 |

### Slot F：`palette_style` (⑥)

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `light_maple` | forked_anchor | S1 palette (light maple laminate + edge band + satin aluminum pulls + dark cubby shadow) | eligible | maple veneer body, satin aluminum hardware, dark cubby recess |
| `beech_graphite` | forked_anchor | S2 palette (beech laminate + graphite panels + blackened metal + satin nickel lock) | eligible | 深色 graphite 主体 + 米色米面板 + 黑色金属把手 |
| `walnut_brass` | world_knowledge_extrapolation | recolor of S1 palette family | eligible | 深胡桃木身 + 抛光黄铜把手（record_only material swap） |
| `industrial_metal` | world_knowledge_extrapolation | recolor of S2 hardware family | eligible | 冷灰漆面 + 亚光钢工作台 + 黑色手柄（record_only + 世界知识扩展） |
| `pale_oak_ivory` | world_knowledge_extrapolation | anchor: S2 + palette adaptation of pale_oak family | eligible | 浅橡木身 + 象牙面板 + brushed nickel（record_only material swap） |

### Slot G：`secondary_motion` (① optional child)

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | forked_anchor | S1, S2 (no keyboard tray) | eligible | 无副机构 (default) |
| `keyboard_tray` | forked_anchor | var `secondary_motion_keyboard_tray` | eligible when `closure ∈ {hinged_door, drop_front}` and `drawer_count ≤ 3` (tray occupies drawer bay slot) | 1 额外 PRISMATIC 抽屉状 tray 挂在 top drawer bay 下面；沿 −Y 滑出 |

## 槽位图（slot graph）

pattern = `mixed`（parallel-children + multiplicity + optional child; closure swap gates joint type）

```
[carcass]  (grounded root; support form + worktop slab + carcass panels + cubby)
  ├── PRISMATIC (0,-1,0) drawer_i          (i in 0..N-1, always ≥1)     # from Slot D + closure interior
  ├── {REVOLUTE (0,0,±1) | PRISMATIC (±1,0,0) | PRISMATIC (0,0,+1) | REVOLUTE (+1,0,0)} door_j
  │                                        (j in 0..M-1, always ≥1)     # from Slot B + Slot E, closure decides joint type
  └── PRISMATIC (0,-1,0) keyboard_tray     (optional)                    # from Slot G
```

- Joint origins:
  - `drawer_slide_{i}`: origin at front carcass face (Y = −depth/2) at
    `drawer_center_z[i]`; axis `(0,-1,0)`; range `[0, drawer_travel]`.
  - `door_hinge_{j}` (closure=hinged_door): origin at front hinge stile on the
    door pedestal (X = hinge_x[j], Y = −depth/2, Z = door_center_z); axis
    `(0,0,±1)`; range `[0, door_open_angle]`.
  - `door_slide_{j}` (closure=sliding_door): origin at track top-left inboard
    corner; axis `(-1,0,0)`; range `[0, door_travel]`.
  - `door_slide_{j}` (closure=roll_top): origin at tambour lower rest; axis
    `(0,0,1)`; range `[0, tambour_rise]`.
  - `door_hinge_{j}` (closure=drop_front): origin at bottom hinge rail; axis
    `(+1,0,0)`; range `[0, drop_front_angle]`.
  - `keyboard_tray_slide`: origin at underside of desktop below top drawer;
    axis `(0,-1,0)`; range `[0, tray_travel]`.
- Support form (`Slot C`) is expressed entirely as `carcass.visual(...)` calls
  (Rule 1); no articulation for it.
- Worktop form (`Slot A`) is expressed entirely as `carcass.visual(...)`; the L
  return produces an extra `return_worktop` slab and `return_leg` support brace.

## 每槽位 Module Emits / Interfaces

### Slot A / worktop_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part；worktop slab / return slab / return_leg + brace 为 `carcass` visuals | S1:L79-L84 (rounded_desk_top), corner_return:L37-L75 (L-shape mesh) |
| internal joints | 无 | — |
| upstream interface | none (root) | — |
| downstream interface | 顶面 face at `desk_height` for user identity | — |

### Slot B / closure = hinged_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | door_{j} × M | S1:L258-L292, S2:L154-L205 |
| internal joints | door_hinge_{j} REVOLUTE ±Z parent=carcass | S1:L310-L325, S2:L206-L216 |
| upstream interface | front hinge stile face (carcass visual `door_hinge_stile_{j}`) | S1:L166-L169 |
| downstream interface | free swing arc; MatingContract to hinge_leaf on door panel edge | — |

### Slot B / closure = sliding_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | door_{j} (single) with top/bottom guide shoes | sliding_door:L259-L301 |
| internal joints | door_slide PRISMATIC −X parent=carcass | sliding_door:L320-L335 |
| upstream interface | sliding tracks on carcass (`sliding_track_top` + `sliding_track_bottom`) | sliding_door:L165-L176 |
| downstream interface | none (translational; captured by tracks via allow_overlap) | — |

### Slot B / closure = roll_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | door (single, N slats as inline visuals + canvas + pull) | roll_top:L278-L338 |
| internal joints | door_slide PRISMATIC +Z parent=carcass | roll_top:L358-L374 |
| upstream interface | tambour tracks (`tambour_track_left/right`) on carcass | roll_top:L177-L188 |
| downstream interface | none (captured by tracks via allow_overlap on all slats) | — |

### Slot B / closure = drop_front
| emits | 描述 | 来源 |
|---|---|---|
| parts | door with top_lip + 2 bottom hinge_knuckle_i / hinge_leaf_i | drop_front:L163-L229 |
| internal joints | door_hinge REVOLUTE +X parent=carcass | drop_front:L231-L243 |
| upstream interface | `dropfront_hinge_rail` visual on front carcass bottom | drop_front:L151-L158 |
| downstream interface | panel drops forward; MatingContract to hinge_leaf | — |

### Slot D / drawer_count (multiplicity, per drawer)
| emits | 描述 | 来源 |
|---|---|---|
| parts | drawer_{i}: front + bottom + 2 sides + back + 2 runners + pull | S1:L194-L256 (single drawer), drawer_count_5:L35-L101 (shared helper `_add_drawer_geometry`) |
| internal joints | drawer_slide_{i} PRISMATIC −Y parent=carcass | S1:L293-L308, drawer_count_5:L289-L308 |
| upstream interface | carcass `drawer_slide_rail_{i}` (horizontal thin box in front stile) | S1:L146-L158 (drawer_guide_0/1), drawer_count_5:L262-L269 (per-drawer rails) |
| downstream interface | drawer front (outer face) | — |

### Slot G / secondary_motion = keyboard_tray
| emits | 描述 | 来源 |
|---|---|---|
| parts | keyboard_tray (slim slide-out shelf under top drawer) | keyboard_tray record |
| internal joints | keyboard_tray_slide PRISMATIC −Y | keyboard_tray record |
| upstream interface | tray_rail_{0,1} visuals on carcass underside | — |
| downstream interface | tray front (visible when extended) | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `worktop_form` | enum | rectangular / corner_return / wide_rectangular | rectangular | choice | procedural sampler | Slot A |
| `closure` | enum | hinged_door / sliding_door / roll_top / drop_front | hinged_door | choice | sampler | Slot B |
| `support_form` | enum | pedestal_plinth / twin_pedestal / four_legs | pedestal_plinth | choice | sampler | Slot C |
| `drawer_count` | int | [1, 5] | 2 | independent | uniform int; clamp; ≥1 required by identity | Slot D |
| `door_count` | int | [1, 3] | 1 | conditional | closure ∈ {hinged_door, drop_front} → uniform [1,3]; closure ∈ {sliding_door, roll_top} → force 1 | Slot E |
| `palette_style` | enum | light_maple / beech_graphite / walnut_brass / industrial_metal / pale_oak_ivory | light_maple | choice | sampler | Slot F |
| `secondary_motion` | enum | none / keyboard_tray | none | conditional | keyboard_tray only if closure ∈ {hinged_door, drop_front} and drawer_count ≤ 3 | Slot G |
| `desk_width` | float | [1.10, 1.90] | 1.35 | independent | m | S1/S2 body span (S1=0.96, S2=1.25) |
| `desk_depth` | float | [0.48, 0.72] | 0.56 | independent | m | S1/S2 (0.50 / 0.56) |
| `desk_height` | float | [0.72, 0.78] | 0.755 | independent | m; work-surface height | S1=0.77, S2=0.75 |
| `pedestal_width` | float | derived | 0.42 | equation | `pedestal_width = clamp(desk_width * 0.30, 0.30, 0.52)` | S1 pedestal ≈ 0.365 |
| `drawer_travel` | float | [0.20, 0.30] | 0.26 | inequality | ≤ pedestal_depth − 0.05 | S1:L303 (0.285), S2:L324 (0.315) |
| `door_open_angle` | float | radians, [1.55, 1.85] | 1.72 | independent | door REVOLUTE upper limit | S1:L322 (1.85), S2:L213 (1.72) |
| `door_slide_travel` | float | [0.20, 0.32] | 0.28 | inequality | ≤ desk_width − pedestal_width − 0.10 for sliding_door | sliding_door:L328-L335 |
| `tambour_rise` | float | [0.18, 0.30] | 0.22 | inequality | ≤ door_panel_height − 0.10 for roll_top | roll_top:L370 (0.22) |
| `drop_front_angle` | float | radians, [1.25, 1.55] | 1.45 | independent | drop-front REVOLUTE upper limit | drop_front:L240 (1.55) |
| `tray_travel` | float | [0.20, 0.30] | 0.25 | inequality | ≤ pedestal_depth − 0.05 | keyboard_tray record |
| (—) | constraint | — | — | inequality | drawer_count × drawer_pitch ≤ pedestal_usable_height; door pedestal + drawer pedestal side-by-side fit ≤ desk_width | mating / clearance |

Sampling contract:

1. Sample `independent` scales first (`desk_width`, `desk_depth`, `desk_height`,
   `drawer_travel`, `door_open_angle`, …).
2. Derive `pedestal_width = clamp(desk_width * 0.30, 0.30, 0.52)`; derive
   drawer pitch = `usable_h / drawer_count`.
3. Apply inequality projections (drawer_travel ≤ pedestal_depth − 0.05;
   door_slide_travel bounded by desk_width; tambour_rise bounded by panel
   height).
4. Apply conditional gates (`door_count`, `secondary_motion` per closure /
   drawer_count).

## 编译预算 / compile budget

- 目标 8–20 s / seed. 主体几乎全部是 `Box` 视觉，大约 40–120 visuals 总数。
  仅 `worktop_form=corner_return` 用 cadquery L-shape workplane（1 boolean），
  `roll_top` 生成 8–12 slat visuals；`hinged_door` 只有 M×1 door_panel Box。
  Tessellation 保持默认；无 Cylinder 高段数。Watchdog `--compile-timeout 120`.

## Multiplicity / Copy Logic

Two multiplicity axes (§7 acknowledged):

| 项 | drawer_count (N) | door_count (M) |
|---|---|---|
| joint-bearing | yes (PRISMATIC per drawer) | yes when closure ∈ {hinged_door} — one REVOLUTE per door |
| `count_param` | `drawer_count` | `door_count` |
| `N_range` | [1, 5] | [1, 3] |
| sampling domain | uniform int (both) | uniform int; forced to 1 for sliding_door / roll_top / drop_front |
| copied object | drawer_{i} (shared helper `_build_drawer`) | door_{j} (shared helper `_build_hinged_door`) |
| naming | `drawer_{i}`, joint `drawer_slide_{i}` | `door_{j}`, joint `door_hinge_{j}` |
| placement | drawer_center_z[i] uniform vertical stack in the drawer pedestal | door_x[j] uniform horizontal split across door pedestal front |
| joint policy | PRISMATIC axis (0,-1,0), lower=0, upper=drawer_travel | REVOLUTE axis (0,0,±1), lower=0, upper=door_open_angle |
| source/gating | ≥1 required by category identity; M+N ≥ 2 | ≥1 required by category identity; forced 1 for sliding/roll_top/drop_front |

## 视觉多样性 6 轴考察

| 轴 | 判断 | 有/无 | 说明 |
|---|---|---|---|
| ① 骨架图 | 加/减 part | 有 | support_form (Slot C: pedestal_plinth / twin_pedestal / four_legs) 决定支撑 part 组；secondary_motion (Slot G) 可选择 keyboard_tray 增加 part；均 forked_anchor |
| └ multiplicity | N drawer + M door | 有 | drawer_count ∈ [1,5]，door_count ∈ [1,3]；forked_anchor (records exist for 2/3/5 drawers and 2/3 doors) |
| ② 关节类型 | joint type | 有 | closure Slot B 直接切换 joint type：REVOLUTE (hinged_door / drop_front) vs PRISMATIC (sliding_door / roll_top)；4 种 closure 都在 sweep 中出现；forked_anchor 全部有变体记录 |
| ③ 主体形态家族 | 主 part 形态 | 有 | worktop_form: rectangular / corner_return / wide_rectangular；Planar Boundary Form；corner_return 变体 forked_anchor (cadquery L-shape mesh)；wide_rectangular 标 world_knowledge_extrapolation 但同 part tree + primitives |
| ④ 表面装饰 | 装饰 | 有 | grain 条纹 (S1/S2)、edge banding (`top_grain_i`, `side_grain_i`, `door_grain_i`)、drawer_lock / lock_keyway (S2)；host-conformal visuals；`record_only` |
| ⑤ 尺寸/行程 | 连续 | 有 | desk_width/depth/height, drawer_travel, door_open_angle, door_slide_travel, tambour_rise, drop_front_angle, tray_travel；motion envelopes: drawer PRISMATIC [0, drawer_travel], door_hinge REVOLUTE [0, door_open_angle], door_slide PRISMATIC [0, door_slide_travel] / [0, tambour_rise], drop_front REVOLUTE [0, drop_front_angle], tray PRISMATIC [0, tray_travel]；motion_test_plan = broad sampled collision via `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` + targeted `ctx.pose` per mechanism |
| ⑥ 涂装 | palette | 有 | 5 palettes: light_maple (S1 forked_anchor), beech_graphite (S2 forked_anchor), walnut_brass / industrial_metal / pale_oak_ivory (world_knowledge_extrapolation); 覆盖 wood + laminate + painted metal + industrial 大类 |

## 采样与覆盖审计

总组合数（离散上界）：worktop_form (3) × closure (4) × support_form (3) ×
drawer_count (5) × door_count (3, gated) × palette (5) × secondary_motion (2, gated)
= 3 × 4 × 3 × 5 × ({3 gated=1 or [1,3]}) × 5 × 2 ≈ 900–2700 有效组合（gating 会剪掉冲突组合）。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：
- `config_from_seed(seed)`: `random.Random(seed)` 均匀采样每个 enum，独立采连续尺度；
  `drawer_count` uniform int [1,5]; `door_count` uniform int [1,3]; 不使用 seed=0 特殊路径.
- Compatibility gating (in `resolve_config`):
  - `closure ∈ {sliding_door, roll_top}` → force `door_count = 1` (single sliding/tambour panel).
  - `closure == drop_front` → force `door_count = 1` (single drop-front writing panel).
  - `secondary_motion == keyboard_tray` requires `closure ∈ {hinged_door, drop_front}` and `drawer_count ≤ 3` (tray occupies drawer bay); else degrade to `none`.
  - `support_form == four_legs` incompatible with `closure == roll_top` (tambour needs a solid side to house tracks); degrade `closure` to `hinged_door` if both selected.
  - `worktop_form == corner_return` requires `support_form ∈ {pedestal_plinth, twin_pedestal}` (return needs a support at the outer corner — for `four_legs` the outer leg would fight the return leg); degrade `worktop_form` to `rectangular` if `four_legs` + `corner_return` chosen.
  - drawer_count × drawer_pitch ≤ pedestal_usable_height ensured via drawer_pitch scaling.
- Random sweep 0–35 (fast 0–15 + final 16–35 + corner appended per pipeline).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 均匀 enum + uniform scales | `slot_choices_for_seed` matches build |
| compatibility matrix | closure gates door_count + secondary_motion; support_form × closure; worktop_form × support_form | no floating / clearance / collision failures |
| controlled local variation | desk_width/depth/height, drawer_travel, door angles, door_slide_travel, tambour_rise, drop_front_angle | proportions vary; interfaces intact |
| regression overrides | none (initial); add only if a recurring corner failure requires it | — |
| random sweep | seeds 0-35 | contract failures; axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| worktop_form | 3 | yes | yes | |
| closure | 4 | yes | yes | |
| support_form | 3 | yes | yes | |
| drawer_count (multiplicity) | 5 | yes | yes | |
| door_count (multiplicity) | 3 | yes | yes | |
| palette_style | 5 | yes | yes | |
| secondary_motion | 2 | yes | (degrade OK) | 2 candidates: none + keyboard_tray; gated |

## 拓扑多样性审计

- Registered slot keys in `slot_choices_for_seed`: worktop_form (3), closure
  (4), support_form (3), drawer_count (5), door_count (3), palette_style (5),
  secondary_motion (2). 1000-seed procedural sampling covers combinations
  well above the recommended ≥300 tuple threshold (rich combinatorial space
  driven by 4-way closure × 3-way support × 3-way worktop × 5-way multiplicity).
- Every closure candidate has ≥1 forked_anchor from the record pool; each
  support candidate has ≥1 forked_anchor.
- multiplicity axes N (drawer_count) and M (door_count) both have forked_anchor
  evidence for the endpoints and intermediate values.

## Validator

- `slot_choices_for_seed(seed)` returns actual chosen (worktop, closure,
  support, drawer_count, door_count, palette, secondary_motion).
- `config_from_seed(0)` succeeds (deterministic sampling).
- Every drawer joint = PRISMATIC axis −Y, origin on front carcass plane at
  drawer Z; range [0, drawer_travel].
- Every hinged door joint = REVOLUTE Z, origin at hinge stile; range
  [0, door_open_angle]; MatingContract on hinge_leaf ↔ hinge_stile.
- Sliding door joint = PRISMATIC ±X, origin at track; captured overlap on
  track ↔ guide shoe.
- Roll-top joint = PRISMATIC +Z, origin at tambour lower rest; captured
  overlap on tracks ↔ slats.
- Drop-front joint = REVOLUTE +X, origin at hinge_rail; MatingContract on
  hinge_leaf ↔ hinge_rail.
- Keyboard tray joint = PRISMATIC −Y, origin under top drawer.
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` covers all
  non-FIXED joints.
- targeted `ctx.pose(...)` per mechanism proving expected motion (drawer
  extends toward −Y, hinged door swings toward −Y, sliding door translates
  ±X, tambour rises +Z, drop-front tilts downward, tray extends −Y).

## Reject cases

- 抽屉滑动轴指向 pedestal 后方（reversed prismatic → drawer 消失进 carcass）.
- 铰接门轴反向（door 打向 carcass 内部而非外部）.
- 滑门 travel 超出 desk_width（door 冲出侧板）.
- 卷帘 tambour 与 desktop 底面碰撞（tambour_rise 超过 door_panel_height − clearance）.
- 掉盖 drop-front 铰在顶部（应在底部，写字板才会向前放下）.
- support_form=four_legs 时 leg 与 worktop_form=corner_return 的 return_leg
  重叠冲突 → gating 应拒绝.
- palette 未覆盖某一 visual → 未上色 part.
- drawer_count = 0 或 door_count = 0（违反类别核心身份，必须 ≥1 of each）.

## 与相邻类别的边界

- 不该混入：`table_with_drawers_no_door`（无 door）—— 我们始终 ≥1 door.
- 不该混入：`Container_Locker` / plain cabinet / TV cabinet（无 worktop）.
- 不该混入：`office_table_with_doors_or_drawers`（该 slug 中一个 topology 只
  有 doors 或只有 drawers；本 slug 强制 both 至少各 1）.
- 不该混入：`round_cabinet`（圆形 cabinet；非 desk）.

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首次实现；spec 与 template 同轮次交付；sweep 通过 verdict=pass 后再复审。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A, B, C, D, F | rectangular + hinged_door (right) + pedestal_plinth + 1_drawer + light_maple | `rec_picturex_0611__table_with_doors_and_drawers__001__png_1566535b936447809aee39304a3c1a95` | `L1-L537` | asymmetric knee desk origin; light_maple palette; drawer/door primitive geometry |
| S2 | A, B, C, D, E, F | rectangular + hinged_door (left) + twin_pedestal (plinths) + 3_drawers + beech_graphite | `rec_picturex_0611__table_with_doors_and_drawers__002__png_e0e1eb86adeb4fb9aaadcc61b0d45b09` | `L1-L513` | twin pedestal desk origin; beech_graphite palette; multi-drawer helper `add_drawer` |
| V1 | B | sliding_door | `rec_0611_table_with_doors_and_drawers_var_closure_sliding_door` | `L165-L335` | horizontal sliding door on track rails |
| V2 | B | roll_top | `rec_0611_table_with_doors_and_drawers_var_closure_roll_top` | `L177-L374` | tambour vertical slide with slats + tracks + housing |
| V3 | B | drop_front | `rec_0611_table_with_doors_and_drawers_var_closure_drop_front` | `L151-L243` | drop-front writing panel with bottom hinge rail |
| V4 | C | four_legs | `rec_0611_table_with_doors_and_drawers_var_support_four_legs` | `L99-L118` | 4 rectangular corner legs, no plinth |
| V5 | C | twin_pedestal | `rec_0611_table_with_doors_and_drawers_var_support_twin_pedestal` | `L94-L119` | symmetric twin plinths |
| V6 | A | corner_return | `rec_0611_table_with_doors_and_drawers_var_worktop_form_corner_return` | `L37-L75, L151-L159` | L-shape worktop via cadquery workplane |
| V7 | D | drawer_count_5 (shared drawer helper `_add_drawer_geometry`) | `rec_0611_table_with_doors_and_drawers_var_drawer_count_5` | `L35-L101, L254-L308` | per-drawer rails + shared drawer geometry |
| V8 | E | door_count_3 (shared door helper `_add_door_assembly`) | `rec_0611_table_with_doors_and_drawers_var_door_count_3` | `L48-L139, L273-L280` | per-door face_frame_stile + shared door assembly |
| V9 | G | keyboard_tray | `rec_0611_table_with_doors_and_drawers_var_secondary_motion_keyboard_tray` | (whole file) | keyboard tray replacing / supplementing drawer bay |
