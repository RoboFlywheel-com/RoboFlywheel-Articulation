## 元信息

| 项 | 值 |
|---|---|
| slug | `simple_drying_rack` |
| template path | `agent/templates/simple_drying_rack.py` |
| test path (optional) | `tests/agent/test_simple_drying_rack_template.py` |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 35 |
| read_count | 35 |
| read_scope | 类别内全部 35 个 5 星样本；每条均读取 `record.json`、`revision.json`、`prompt.txt`、`model.py` |
| source_index_policy | 仅索引下方采纳 module source |

结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| Classic 四部件（central + 2 wings + lower support） | 10 | 3–4 revolute；canonical 主导簇 |
| Base + 2 wings（无下框） | 4 | 固定中央/底框 + 双侧翼 |
| Central + lower（翼在 loop 内） | 5 | 命名 central/support；翼动态创建 |
| Inverted deck + 折叠支撑腿 | 2 | 非侧翼架构（`0001`, `f992`） |
| Industrial trestle + lockout/link | 2 | 安全锁止/对角撑杆 |
| Accordion A-frame + spreader | 3 | 侧段 + 撑杆 |
| Hinge-link stay（独立撑杆件） | 3 | `hinge_link_*` 对角支撑 |
| Wire mesh / CadQuery 一体网格 | 11 | `wire_from_points` 或 cadquery |

## 核心身份

**家用/轻型晾干架**：中央（或顶部）固定晾架框承载水平 **挂杆（hanging rails）**；**两个可折叠侧翼（foldable wings）** 通过 `REVOLUTE` 铰链展开/收拢；多数样本另有 **较低的下支撑框（lower support）** 提供展开止挡与第三层挂杆。挂杆为部件内固定几何（jointless），非独立滑动关节。

Canonical 四部件：`central_frame` + `left_wing` + `right_wing` + `lower_support_frame`，3–4 个 `REVOLUTE`。

边界：
- 不是 `closet_rod` 固定墙杆（无可折叠翼）。
- 不是 `laundry_drying_cabinet` 封闭柜体。
- 不是 `playground_swing` 单摆座椅。

## 槽位 + 候选模块表

### Slot A：central_frame

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `classic_rect_deck` | rec_simple_drying_rack_125ad58c389349db85f340c626c41e12 | L141-L210 | eligible if compatible | 矩形管框 + top_cap + 中央挂杆 |
| `tube_leg_tower` | rec_simple_drying_rack_dec84d2587474928b76cd6e7a840bc15 | L43-L92 | eligible if compatible | 精简 central 管框 + 斜撑 |
| `wire_base_deck` | rec_simple_drying_rack_f8f4f693f5c1410690b273c367081ad3 | L123-L220 | eligible if compatible | wire mesh 底座 + serpentine deck |
| `industrial_trestle` | rec_simple_drying_rack_fa4ae4ed55e9444a8f189b537e957b0c | L27-L138 | eligible if compatible | 焊接 trestle `base_frame` |
| `inverted_top_grate` | rec_simple_drying_rack_0001 | L115-L163 | eligible if compatible | 单 `rack_deck` 顶格 + 无侧翼 |
| `accordion_a_center` | rec_simple_drying_rack_b2cef7cb0d114494b25c576a7ce31486 | L75-L141 | eligible if compatible | A 架中心 ridge + 侧段接口 |

### Slot B：wing_frame

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `tube_panel_wing` | rec_simple_drying_rack_125ad58c389349db85f340c626c41e12 | L77-L131 | eligible if compatible | Cylinder 管翼 + 4 挂杆 |
| `wire_serpentine_wing` | rec_simple_drying_rack_f8f4f693f5c1410690b273c367081ad3 | L41-L115 | eligible if compatible | `wire_from_points` 蛇形翼网格 |
| `box_industrial_wing` | rec_simple_drying_rack_fa4ae4ed55e9444a8f189b537e957b0c | L140-L223 | eligible if compatible | Box 翼 + 6 挂杆 + guard |
| `premium_tube_wing` | rec_simple_drying_rack_e2af1c3dabb14ad984c3855349f1dffb | L142-L212 | eligible if compatible | 管翼 + stop pad |
| `cadquery_mesh_wing` | rec_simple_drying_rack_b857c949ff10467abd3561b1246b2781 | L24-L50 | eligible if compatible | cadquery 一体网格翼 |

### Slot C：lower_support

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `slanted_rail_frame` | rec_simple_drying_rack_125ad58c389349db85f340c626c41e12 | L218-L270 | eligible if compatible | 斜腿下框 + 3 挂杆 |
| `minimal_slant_support` | rec_simple_drying_rack_dec84d2587474928b76cd6e7a840bc15 | L111-L144 | eligible if compatible | 极简斜撑下框 |
| `wire_mesh_support` | rec_simple_drying_rack_da39b4897695482caeec2c1ddb18c74e | L248-L323 | eligible if compatible | wire mesh 下框 |
| `rect_tube_support` | rec_simple_drying_rack_7cc9165dc0454d9aa5147531e9a8d691 | L110-L127 | eligible if compatible | 矩形下框 + 4 挂杆 |
| `none_fixed_base_only` | rec_simple_drying_rack_f8f4f693f5c1410690b273c367081ad3 | — | eligible if compatible | 无独立 lower part；翼直接铰于 base |

### Slot D：wing_hinge_mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `top_cap_x_hinge` | rec_simple_drying_rack_125ad58c389349db85f340c626c41e12 | L272-L290 | eligible if compatible | 翼原点 @ central 侧 rail；axis `(±1,0,0)` |
| `sleeve_on_side_rail` | rec_simple_drying_rack_7cc9165dc0454d9aa5147531e9a8d691 | L100-L108 | eligible if compatible | `hinge_tube` 套在 side_rail |
| `hinge_link_stay` | rec_simple_drying_rack_e2af1c3dabb14ad984c3855349f1dffb | L83-L141, L408-L439 | eligible if compatible | 独立 `hinge_link` FIXED→翼 REV |
| `molded_clip_barrel` | rec_simple_drying_rack_f8f4f693f5c1410690b273c367081ad3 | L231-L248 | eligible if compatible | 塑料 clip block + barrel Y 轴 |
| `pin_barrel_y_hinge` | rec_simple_drying_rack_fa4ae4ed55e9444a8f189b537e957b0c | L292-L309 | eligible if compatible | base pin + wing barrel；Y 轴 |

### Slot E：hanging_rail_density（jointless multiplicity）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `3_rails_per_region` | rec_simple_drying_rack_dec84d2587474928b76cd6e7a840bc15 | L251-L261 | eligible if compatible | central/wing/lower 各 3 杆量级 |
| `4_rails_per_region` | rec_simple_drying_rack_125ad58c389349db85f340c626c41e12 | L191-L200, L112-L120 | eligible if compatible | wing 4 / central 6 |
| `5_rails_central` | rec_simple_drying_rack_7cc9165dc0454d9aa5147531e9a8d691 | L191-L200 | eligible if compatible | central 5 杆 |
| `6_rails_wing` | rec_simple_drying_rack_fa4ae4ed55e9444a8f189b537e957b0c | L180-L186 | eligible if compatible | industrial 翼 6 杆 |

## 槽位图（slot graph）

pattern: `mixed`

```text
[central_frame] (grounded)
    |-- REVOLUTE (×2, mirrored) --> [left_wing_frame]
    |-- REVOLUTE (×2, mirrored) --> [right_wing_frame]
    |-- REVOLUTE --> [lower_support_frame]   (optional; none_fixed_base_only 跳过)
[hinge_link_stay] (optional FIXED/REV chain per wing_hinge_mechanism)
```

- `wing_multiplicity` 固定 **2 个 foldable wings**（镜像）。
- `hanging_rail_density` 为 jointless 复制：在 central/wing/lower 区域内循环生成挂杆 visual。
- `inverted_top_grate` / `accordion_a_center` 与 canonical wing+lower 互斥（extension gating）。

## 每槽位 Module Emits / Interfaces

### Slot A / central_frame

| module | emits | 描述 | 来源 |
|---|---|---|
| `classic_rect_deck` | parts | `central_frame`；side/top rails、top_cap、feet | 125ad58c / L141-L210 |
| `classic_rect_deck` | downstream | left/right hinge origins @ side rail Y | 125ad58c / L272-L290 |
| `wire_base_deck` | parts | `base_frame` + serpentine `deck_wire` | f8f4f693 / L123-L220 |
| `industrial_trestle` | parts | welded trestle + pin seats | fa4ae4ed / L27-L138 |

### Slot B / wing_frame

| module | emits | 描述 | 来源 |
|---|---|---|
| `tube_panel_wing` | parts | `left_wing`/`right_wing`；outer_rail、hanging_rails | 125ad58c / L77-L131 |
| `wire_serpentine_wing` | parts | wire mesh wing | f8f4f693 / L41-L115 |
| `cadquery_mesh_wing` | parts | cq mesh wing panel | b857c949 / L24-L50 |

### Slot C / lower_support

| module | emits | 描述 | 来源 |
|---|---|---|
| `slanted_rail_frame` | parts + joint | `lower_support`；斜腿框 | 125ad58c / L218-L270 |
| `slanted_rail_frame` | joint | `central_to_lower_support` REVOLUTE @ 底缘 | 125ad58c / L291-L299 |
| `none_fixed_base_only` | — | 无 lower part | f8f4f693 |

### Slot D / wing_hinge_mechanism

| module | emits | 描述 | 来源 |
|---|---|---|
| `top_cap_x_hinge` | joints | `central_to_left_wing` / `central_to_right_wing` REV X | 125ad58c / L272-L290 |
| `hinge_link_stay` | parts + joints | `hinge_link` FIXED @ central；翼 REV @ link | e2af1c3d / L408-L439 |
| `pin_barrel_y_hinge` | joints | Y-axis barrel hinge | fa4ae4ed / L292-L309 |

### Slot E / hanging_rail_density

| module | emits | 描述 | 来源 |
|---|---|---|
| `4_rails_per_region` | visuals | loop `hanging_rail_{i}` jointless | 125ad58c / L112-L120 |
| `5_rails_central` | visuals | central 区 5 杆 | 7cc9165 / L191-L200 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `central_frame` | enum | 6 modules | sampled | procedural | Slot A |
| `wing_frame` | enum | 5 modules | sampled | geometry backend 须匹配 | Slot B |
| `lower_support` | enum | 5 modules | sampled | `none` 与 inverted/accordion 互斥 | Slot C |
| `wing_hinge_mechanism` | enum | 5 modules | sampled | industrial 配 pin_barrel | Slot D |
| `hanging_rail_density` | enum | 3/4/5/6 rails | sampled | jointless per region | Slot E |
| `wing_multiplicity` | int | exactly `2` | `2` | 固定双侧翼 | canonical |
| `deck_width_scale` | float | [0.85, 1.20] | sampled | 派生 rail 间距 | 125ad58c |
| `wing_span_scale` | float | [0.80, 1.15] | sampled | 翼外伸 | 125ad58c / L77-L131 |

## Multiplicity / Copy Logic

- `count_param`: `wing_multiplicity`（关节承载）+ `hanging_rail_count`（jointless）
- `N_range` wings: exactly `2`；禁止 1 或 3 翼（inverted/accordion 为互斥架构变体，不计入默认翼数）。
- `hanging_rail_count` per region: 3–6；jointless visual 复制，无独立 articulation。
- copied object wings: `left_wing_frame`, `right_wing_frame`（或语义名）；镜像 `side_sign=±1`。
- naming: `left_wing_frame`/`right_wing_frame`；挂杆 `hanging_rail_{i}`、`center_hanging_rail_{i}`。
- placement: 翼铰 origin @ central 侧 rail；lower support 铰 @ central 前底缘。
- joint policy: 2× wing `REVOLUTE` + 0–1× lower `REVOLUTE`；`hinge_link` 可为 FIXED 中间件。
- source/gating: wire 翼须 wire 底座；industrial 须 `pin_barrel_y_hinge`；cadquery 翼须 cq 底座或 wing 自洽。

## 拓扑多样性审计

总组合数：6 × 5 × 5 × 5 × 4 = 3000 raw；gating 后 canonical 支系 **~27–45** 合法组合。


理由：central/wing/lower/hinge/rail 五维结构差异；35 样本覆盖 12 架构族，canonical 四部件簇 10 条高冗余但 outlier 族提供额外拓扑。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：
- 默认采样 canonical 支系：`classic_rect_deck` + `tube_panel_wing` + `slanted_rail_frame` + `top_cap_x_hinge` + rail density。
- `seed=0` 不特殊。
- extension variants（inverted、accordion、industrial）权重较低或 Phase-2 扩展。
- wire/cadquery 几何须保留源样本 mesh 路径，不得统一降级 Cylinder。
- sweep 0-49；viewer 检查展开/折叠姿态、铰链捕获、翼止挡接触。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；canonical 支系按该观察线记录，低于 300 时说明合法组合空间或采样权重原因。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | central → wing → lower → hinge → rail density | slot_choices 一致 |
| compatibility matrix | 见下表 | 无 isolated parts |
| controlled local variation | deck/wing scale | 不破坏铰链捕获 |
| regression overrides | none 初版 | — |
| random sweep | 0-49 | diversity + fold motion |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| central_frame | 6 | yes | yes | 含 inverted/accordion |
| wing_frame | 5 | yes | yes | tube/wire/box/cq |
| lower_support | 5 | yes | yes | 含 none |
| wing_hinge_mechanism | 5 | yes | yes | X/Y/link/clip/pin |
| hanging_rail_density | 4 | yes | yes | jointless |

### Compatibility matrix / gating

| central_frame | legal wing | legal lower | legal hinge | gating |
|---|---|---|---|---|
| `classic_rect_deck` | tube_panel, premium_tube | slanted, rect_tube | top_cap_x, sleeve, hinge_link | canonical 默认 |
| `wire_base_deck` | wire_serpentine | none | molded_clip | 无 lower |
| `industrial_trestle` | box_industrial | none | pin_barrel_y | 无 lower；可配 lockout extension |
| `inverted_top_grate` | — | — | leg_revolute | **互斥** canonical wings |
| `accordion_a_center` | side_section | spreader | side_y | **互斥** classic lower |

| wing_frame | geometry backend | gating |
|---|---|---|
| `wire_serpentine_wing` | 必须 `wire_from_points` | 禁止纯 Cylinder 替代 |
| `cadquery_mesh_wing` | 必须 `mesh_from_cadquery` | 禁止 Box 替代 |

## Validator

- `__modular__ = True`
- 默认配置：2 foldable wings + optional lower support
- ≥2 `REVOLUTE` wing hinges；折叠姿态 AABB 变化可测
- 挂杆为 jointless visuals（除刻意 extension 的 per-rail FIXED 装配）
- hinge clamp/barrel 允许 element-scoped `allow_overlap`
- wire/cadquery 模块保留源复杂度

## Reject cases

- 无折叠关节的单杆墙架
- 仅 1 个翼或 3+ 个翼（默认 canonical）
- 挂杆做成独立 PRISMATIC 滑动（非本类）
- 仅换粉末颜色/比例的假 candidate
- wire 翼降级为 3 个 Box
- lower support 与 inverted legs 双支撑语义冲突
- 折叠姿态翼与 central 穿模（无 allow_overlap 依据）

## 与相邻类别的边界

- 不该混入：固定 `'closet_rod'` / 墙杆（无 foldable wings）。
- 不该混入：`laundry_cabinet` 封闭烘干柜。
- 不该混入：`playground_swing` 单 seat pendulum。
- 不该混入：`folding_step_ladder` 梯级踏步语义。

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 用户 2026-06-09 确认通过；进入 TEMPLATE_AFTER_REVIEW |

## 模板实现备注（可选）

- Canonical 实现优先 `125ad58c` 四部件拓扑；extension 变体（inverted/accordion/industrial）可 Phase-2 加权引入。
- `wire_serpentine_wing` / `cadquery_mesh_wing` 必须保留 mesh 路径。
- `hinge_link_stay` 需 `expect_contact` 止挡与 link 捕获测试（参考 e2af1c3d）。
- per-rail FIXED 装配（9375ef389）标为 extension，不进入初版 seed domain。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | `classic_rect_deck` | rec_…_125ad58c | L141-L210 | central frame |
| S2 | A | `tube_leg_tower` | rec_…_dec84d258 | L43-L92 | minimal central |
| S3 | A | `wire_base_deck` | rec_…_f8f4f693 | L123-L220 | wire base |
| S4 | A | `industrial_trestle` | rec_…_fa4ae4ed | L27-L138 | trestle base |
| S5 | A | `inverted_top_grate` | rec_…_0001 | L115-L163 | inverted deck |
| S6 | A | `accordion_a_center` | rec_…_b2cef7cb | L75-L141 | A-frame center |
| S7 | B | `tube_panel_wing` | rec_…_125ad58c | L77-L131 | tube wing |
| S8 | B | `wire_serpentine_wing` | rec_…_f8f4f693 | L41-L115 | wire wing |
| S9 | B | `box_industrial_wing` | rec_…_fa4ae4ed | L140-L223 | box wing |
| S10 | B | `premium_tube_wing` | rec_…_e2af1c3d | L142-L212 | premium wing |
| S11 | B | `cadquery_mesh_wing` | rec_…_b857c949 | L24-L50 | cq wing |
| S12 | C | `slanted_rail_frame` | rec_…_125ad58c | L218-L299 | lower support |
| S13 | C | `minimal_slant_support` | rec_…_dec84d258 | L111-L191 | minimal lower |
| S14 | C | `wire_mesh_support` | rec_…_da39b489 | L248-L351 | wire lower |
| S15 | C | `rect_tube_support` | rec_…_7cc9165d | L110-L127 | rect lower |
| S16 | C | `none_fixed_base_only` | rec_…_f8f4f693 | — | no lower |
| S17 | D | `top_cap_x_hinge` | rec_…_125ad58c | L272-L290 | X hinge |
| S18 | D | `sleeve_on_side_rail` | rec_…_7cc9165d | L100-L108 | sleeve hinge |
| S19 | D | `hinge_link_stay` | rec_…_e2af1c3d | L83-L141, L408-L439 | link stay |
| S20 | D | `molded_clip_barrel` | rec_…_f8f4f693 | L231-L248 | clip hinge |
| S21 | D | `pin_barrel_y_hinge` | rec_…_fa4ae4ed | L292-L309 | pin barrel |
| S22 | E | `4_rails_per_region` | rec_…_125ad58c | L112-L120, L191-L200 | rail density |
| S23 | E | `5_rails_central` | rec_…_7cc9165d | L191-L200 | 5 central rails |
