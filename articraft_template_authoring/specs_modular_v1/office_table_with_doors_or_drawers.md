# office_table_with_doors_or_drawers — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `office_table_with_doors_or_drawers` |
| template path | `agent/templates/office_table_with_doors_or_drawers.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 (source map ★) |
| read_count | 3 origin anchors (001/002/003) fully read; 10 variant records inspected for slot mapping |
| read_scope | picture-derived origin models 001/002/003 (`rec_picturex_0611__office_table_with_doors_or_drawers__00{1,2,3}__png_*`) + 10 slot-fork variants |
| source_index_policy | only adopted module sources indexed below |

Structure family distribution (from origin reads):

| family | evidence | notes |
|---|---|---|
| L-shape worktop + drawer pedestal + hinged door | 003 (S3) | 3 PRISMATIC drawers + 1 REVOLUTE cabinet_door |
| straight-front carcass + wide drawer + swinging door(s) | 001 (S1) | 1 PRISMATIC wide drawer + 3 REVOLUTE doors |
| L-shape + 3-drawer pedestal + single door pedestal | 002 (S2) | 3 PRISMATIC drawers + 1 REVOLUTE cabinet_door |

## 核心身份

An office/executive **table**: a raised **work surface (worktop)** supported by
a grounded **storage carcass**. The carcass hosts at least one non-FIXED joint
(PRISMATIC drawer or REVOLUTE door). Must retain: a visible work surface at
desk height (~0.72–0.78 m), a supporting pedestal / body, and ≥1 movable front.

不该混入：
- plain cabinet (无 worktop 面) — 见 `Other_Cabinet` / `drawer_cabinet_with_sliding_drawers`.
- dining/office table without storage (无门无抽屉) — regular table.
- roll-top secretary desk with tambour — 复杂多铰机构，独立类别。

## 槽位 + 候选模块表

### Slot A：`worktop_form` (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `straight` | forked_anchor | S3 (rec_picturex 003) + var `worktop_form_straight` | S3:L38-L100 | Planar Boundary Form | eligible | 单一矩形工作台，无返弯；简化 002/003 的主台 |
| `compact_corner` | forked_anchor | S1 (rec_picturex 001) + var `worktop_form_compact_corner` | S1:L142-L153 | Planar Boundary Form | eligible | L 型（主台 + 短返台）；返台较窄 |
| `u_return` | forked_anchor | S2 (rec_picturex 002) + var `worktop_form_u_return` | S2:L30-L48 | Planar Boundary Form | eligible | L 型带更宽返翼，返台方向 +Y |

### Slot B：`storage_topology` (①)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `drawer_pedestal` | forked_anchor | S2 (rec_picturex 002) + var `storage_topology_drawer_pedestal` | S2:L164-L275 | eligible | 单一 pedestal 承载 3–5 抽屉栈 |
| `paired_door_pedestal` | forked_anchor | S3 (rec_picturex 003) + var `paired_door_pedestal` | S3:L102-L221 | eligible | 一个铰接门柜 + 一个短抽屉栈 |
| `drawer_plus_door` | forked_anchor | S1 (rec_picturex 001) + var `open_equipment_bay` | S1:L51-L80, S1:L246-L360 | eligible | 抽屉 + 门 混合 (drawer stack + swing door on opposite side) |

### Slot C：`drawer_count` (multiplicity, N)

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `2_drawers`, `3_drawers`, `4_drawers`, `5_drawers` | forked_anchor | S3 (3), var `drawer_count_3` (3), var `drawer_count_5` (5) | eligible when `storage_topology` in {drawer_pedestal, drawer_plus_door} | N ∈ [2,5] 个 PRISMATIC 抽屉 |

### Slot D：`material_palette` (⑥)

| module_name | source_type | source evidence | eligibility | 结构特征 |
|---|---|---|---|---|
| `warm_oak` | forked_anchor | S3 (rec_picturex 003) | eligible | oak veneer + white worktop inlay + dark hardware (anchor) |
| `ivory_burgundy` | forked_anchor | S1 (rec_picturex 001) | eligible | ivory laminate carcass + burgundy doors + brushed aluminum |
| `pale_oak_white` | forked_anchor | S2 (rec_picturex 002) | eligible | pale oak worktop + warm white laminate + graphite |
| `walnut_dark` | world_knowledge_extrapolation (record_only material swap) | palette adaptation of S3 hardware | eligible | dark walnut carcass + brushed metal (record_only recolor of S3) |

### Slot E：`has_return_worktop` (③ complement, boolean derived from Slot A)

- `worktop_form == straight` ⇒ `has_return_worktop = False`; else `True`.

## 槽位图（slot graph）

pattern = `mixed`（parallel-children + multiplicity + optional door）

```
[body]  (grounded root; carcass + plinth + worktop slab(s))
  ├── PRISMATIC +X drawer_i  (i in 0..N-1)      # from Slot C
  └── REVOLUTE +Z cabinet_door  (optional)      # from Slot B when door present
```

- Joint origins live on the pedestal's front opening face (`body_to_drawer_i`
  at rail-height Z on the front carcass plane) and on the door pedestal's inner
  hinge stile (`body_to_door` at rear hinge line, axis +Z or −Z).
- Worktop is a `body` visual (Rule 1) — not a joint-bearing part.

## 每槽位 Module Emits / Interfaces

### Slot A / worktop_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part；worktop slab / return slab 为 `body` 的 visuals | S3:L38-L100 |
| internal joints | 无 | — |
| upstream interface | body top face @ z=desk_height | S3 |
| downstream interface | 无 (top of desk) | — |

### Slot B / storage_topology (drawer_pedestal)
| emits | 描述 | 来源 |
|---|---|---|
| parts | body carcass visuals (pedestal outer, plinth, back, floor, front rails); N drawer parts | S2:L164-L275 |
| internal joints | body → drawer_i PRISMATIC ±Y or +X | S2:L124-L138 |
| upstream interface | body worktop face | — |
| downstream interface | none | — |

### Slot B / storage_topology (paired_door_pedestal)
| emits | 描述 | 来源 |
|---|---|---|
| parts | body carcass; cabinet_door | S3:L102-L221 |
| internal joints | body → cabinet_door REVOLUTE +Z; body → drawer_i PRISMATIC +X | S3:L207-L281 |
| upstream interface | body worktop face | — |
| downstream interface | door swings toward −Y (out of pedestal) | — |

### Slot B / storage_topology (drawer_plus_door)
| emits | 描述 | 来源 |
|---|---|---|
| parts | body carcass + door + N drawers on opposite side of pedestal | S1:L51-L80, S1:L212-L323 |
| internal joints | body → wide_drawer PRISMATIC −Y; body → front_door REVOLUTE +Z | S1:L325-L342 |
| upstream interface | body worktop face | — |
| downstream interface | door swings +Y; drawer slides −Y | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `worktop_form` | enum | straight / compact_corner / u_return | straight | choice | procedural sampler | Slot A |
| `storage_topology` | enum | drawer_pedestal / paired_door_pedestal / drawer_plus_door | drawer_pedestal | choice | sampler | Slot B |
| `drawer_count` | int | 2..5 (int) | 3 | independent | uniform, clamp; ignored when topology has no drawer bank | Slot C |
| `palette_style` | enum | warm_oak / ivory_burgundy / pale_oak_white / walnut_dark | warm_oak | choice | sampler | Slot D |
| `desk_width` | float | [1.30, 2.00] | 1.75 | independent | m, cabinet-wide | S1/S2/S3 body span |
| `desk_depth` | float | [0.60, 0.90] | 0.72 | independent | m | S3 |
| `desk_height` | float | [0.72, 0.78] | 0.745 | independent | m; work-surface height | S3 |
| `pedestal_width_scale` | float | [0.85, 1.10] | 1.0 | equation | pedestal_w = 0.42 * desk_width * scale (bounded ≥0.40) | S2 |
| `drawer_travel` | float | [0.24, 0.34] | 0.30 | inequality | ≤ pedestal_depth − 0.05 | S3:L275-L282 |
| `door_open_angle` | float | radians, [1.55, 1.85] | 1.75 | independent | door REVOLUTE upper limit | S1/S2/S3 |
| (—) | constraint | — | — | inequality | pedestal must fit within desk_width/2 for `drawer_plus_door`; door pedestal + drawer pedestal side-by-side | mating |

## 编译预算 / compile budget

- 目标 8–20 s / seed (typical modular). 主体 Box 只有几十个，无 CAD boolean 复杂
  loft/lathe。tessellation 保持默认（无 Cylinder 高段数），单个 seed compile
  budget 20s 完全可控。Watchdog `--compile-timeout 120`.

## Multiplicity / Copy Logic

| 项 | 值 |
|---|---|
| M1 `drawer_multiplicity` | joint-bearing；`drawer_count` ∈ [2,5]，仅在 topology ∈ {drawer_pedestal, drawer_plus_door} 时有效；导出 `"{N}_drawers"` |
| naming | `drawer_{i}`, joint `body_to_drawer_{i}` |
| placement | drawer_center_z[i] 等间距垂直栈；根据 pedestal_width 派生高度 |
| joint policy | PRISMATIC axis = (0,-1,0)（front-out 一致 −Y）；lower=0, upper=drawer_travel |
| door | 可选单 REVOLUTE，轴 (0,0,+1) 或 (0,0,-1)，parent=body，铰在 pedestal 内侧 rear stile |

## 视觉多样性 6 轴考察

| 轴 | 判断 | 有/无 | 说明 |
|---|---|---|---|
| ① 骨架图 | 加/减 part | 有 | topology slot 决定：drawer_pedestal (无 door) vs paired_door_pedestal (有 door) vs drawer_plus_door (二者)；forked_anchor |
| └ multiplicity | N 抽屉 | 有 | drawer_count 2..5；forked_anchor (S3=3, var=5) |
| ② 关节类型 | joint type | 有 | PRISMATIC drawer + REVOLUTE door；两种在 sweep 内都出现 |
| ③ 主体形态家族 | 主 part 形态 | 有 | worktop_form: straight / compact_corner / u_return；Planar Boundary Form；forked_anchor + 变体 |
| ④ 表面装饰 | 装饰 | 有 | worktop inlay (S3), edge banding, cable slot, pull hardware；host-conformal visuals；`record_only` |
| ⑤ 尺寸/行程 | 连续 | 有 | desk_width/depth/height, drawer_travel, door_open_angle；door REVOLUTE motion envelope [0, door_open_angle]；drawer PRISMATIC [0, drawer_travel]；motion_test_plan = broad sampled collision via `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` per mechanism |
| ⑥ 涂装 | palette | 有 | 4 palettes；每个覆盖 wood + laminate + metal 大类 |

## 采样与覆盖审计

总组合数（离散）：worktop_form (3) × storage_topology (3) × drawer_count (4, 只在有抽屉 topology 时) × palette (4) ≈ 96–120 有效组合。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：
- `config_from_seed(seed)`: `random.Random(seed)` 均匀采样每个 enum，独立采连续尺度；
  `drawer_count` 均匀 [2,5]；不使用 seed=0 特殊路径。
- Compatibility gating (in resolve_config):
  - `paired_door_pedestal` 强制 `drawer_count = 2`（配合小抽屉，door 侧空间有限）。
  - `worktop_form == straight` 时 pedestal 单侧或对齐主台。
  - `drawer_plus_door` 与 `worktop_form == u_return` 冲突则强制 topology = drawer_pedestal (u_return 返翼占用侧面)。
- Random sweep 0–35。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 均匀 enum + uniform scales | slot_choices_for_seed matches build |
| compatibility matrix | topology→drawer_count gating; worktop×topology gating | no floating / clearance / collision failures |
| controlled local variation | desk_width/depth/height, drawer_travel, door angle | proportions vary; interfaces intact |
| regression overrides | none | — |
| random sweep | seeds 0-35 | contract failures; axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| worktop_form | 3 | yes | yes | |
| storage_topology | 3 | yes | yes | |
| drawer_count (multiplicity) | 4 | yes | yes | |
| palette_style | 4 | yes | yes | |

## Validator

- `slot_choices_for_seed(seed)` returns actual chosen (worktop, topology, drawer_count, palette).
- `config_from_seed(0)` succeeds (deterministic sampling).
- Every drawer joint = PRISMATIC axis −Y, origin on front carcass plane at drawer Z; range [0, drawer_travel].
- Optional door joint = REVOLUTE +Z, origin at rear hinge stile, range [0, door_open_angle].
- MatingContract on door hinge joint (parent stile face ↔ door hinge edge).
- `fail_if_parts_overlap_in_sampled_poses` covers all non-FIXED joints; `allow_overlap` scoped to cavity where needed.

## Reject cases

- 抽屉滑动轴指向 pedestal 后方（reversed prismatic → drawer 消失进 body）
- 门铰轴反向（door 打向 pedestal 内部）
- worktop 主台悬空（未与 pedestal / return 接触）
- `paired_door_pedestal` 时 pedestal_width < door 宽（drawer 抽出后碰门位）
- palette 未覆盖所有 visual → 未上色 part

## 与相邻类别的边界

- 不该混入：`drawer_cabinet_with_sliding_drawers`（无 worktop 面）。
- 不该混入：`desk_with_drawer`（单抽屉、无 door 选项）。
- 不该混入：dining/plain table（无 storage）。

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首次实现；spec 与 template 同轮次交付；sweep 通过 verdict=pass 后再复审。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A, B, C, D | drawer_plus_door + ivory_burgundy | `rec_picturex_0611__office_table_with_doors_or_drawers__001__png_57bac13add2c40b7addfb86887d0da4c` | `L20-L360` | drawer_plus_door topology; ivory/burgundy palette; hinge/drawer joint geom |
| S2 | A, B, C, D | u_return + drawer_pedestal | `rec_picturex_0611__office_table_with_doors_or_drawers__002__png_a048366dd19d4c2cb5c7499522bfee15` | `L20-L327` | L-return worktop + 3-drawer pedestal + single door; pale-oak palette |
| S3 | A, B, D | compact_corner + paired_door_pedestal + warm_oak | `rec_picturex_0611__office_table_with_doors_or_drawers__003__png_b4b10d9eca3648049dbe8a4bf3ea11e6` | `L20-L285` | anchor: L-shape + door + 3 drawers; warm_oak palette |
