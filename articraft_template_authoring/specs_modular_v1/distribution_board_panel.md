# Modular Spec — distribution_board_panel

## 元信息
| 项 | 值 |
|---|---|
| slug | `distribution_board_panel` |
| template path | `agent/templates/distribution_board_panel.py` |
| test path (optional) | `tests/agent/test_distribution_board_panel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (enclosure = grounded chassis; breaker field / mains bay / door(s) / toggles all parent to it) + `multiplicity` (breaker field is a loop-emitted N grid) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (2 origins + 5 forks) |
| source_index_policy | only adopted module sources are indexed below |

Read in full:
- **S1** `rec_use-...164631_232036_c548199a` — grey US-style load-center: single hinged front door (authored **baked-open** — grandfather anti-pattern, NOT copied), two vertical breaker banks (2 columns × 12 rows = 24), copper bus + neutral/earth terminal bars, warning labels, top conduit glands, 2 real toggles. `model.py` L88-L234.
- **S2** `rec_use-...164631_229630_4cb00767` — wide light-grey two-bay board: `enclosure` shell + `breaker_bank` (FIXED, 3 stacked DIN rails × 14 MCBs = 42 via `_add_breaker_row(count=N)`) + `left_devices` (FIXED, full power bay: 2 main MCCBs + 4 phase busbars + aux breaker + meter) + `left_door`/`right_door` (REVOLUTE, **closed rest pose** — the adopted convention) + 4 real `breaker_toggle_i` (REVOLUTE, parented to breaker_bank at `articulated_slots`). `model.py` L169-L379.
- **fork open_backplate@S2** — removes both doors + hinges; `enclosure`→`backplate` (flat plate + bent flanges, no walls); breaker toggles remain the only moving joints. `model.py` L169-L303.
- **fork single_din_rail@S2** — `_add_right_breaker_bank` collapses the 3 stacked rails to ONE `single_row` DIN rail. `model.py` L211-L232.
- **fork eight_way@S1 / eighteen_way@S1** — parameterize S1's two-column field count via `ROWS_PER_BANK` (2×4=8, 2×9=18), recomputing well/rail/board height from the count. `model.py` L23-L152.
- **fork mcb_only_subboard@S1** — drops the copper bus / main assembly, keeps only neutral+earth bars + a sub-feed terminal block. `model.py` L123-L135.

## 核心身份

An electrical **distribution board / load-center / panelboard**: a grounded sheet-metal enclosure (or open backplate) presenting a **breaker FIELD** — DIN rails or vertical columns of loop-emitted MCB modules of which a few carry a real revolute toggle and the rest are decorative — plus a **mains assembly** (main breaker + busbars + metering, or bus bars only, or an MCB-only sub-board). Default mature domain: 6–42 breaker ways, one or two hinged deadfront doors, copper busbar + brass terminal bars.

Neighbor boundary: NOT a single `Electrical_Wiring_Circuit_breaker` (this is the enclosure of MANY breakers); NOT a `Electrical_Wiring_Junction_box` (it has an articulated breaker field + busbars, not a bare cable-splice box).

## 槽位 + 候选模块表

### Slot A：form_module — ③ 主体形态家族 / Primary Form Family + door count (主轴)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| `single_door` | forked_anchor | S1 (`c548199a`) | L88-L218 | eligible if compatible | 单腔上翻/侧铰柜 + 一扇前门（REVOLUTE 竖轴），deadfront。**Volumetric Envelope Form**（紧凑直立单腔盒） |
| `two_door` | forked_anchor | S2 (`4cb00767`) | L169-L363 | eligible if compatible | 双腔柜 + center mullion + 左右两扇门（两 REVOLUTE 竖轴）。**Volumetric Envelope Form**（更宽双开口带中挺） |
| `open_backplate` | forked_anchor | open_backplate@S2 | L169-L303 | eligible if compatible | 无墙无门的平板底盘 + 四边折边，breaker toggles 是唯一 moving joint。**Planar Boundary Form**（平面安装板，无包络门） |

3 个可识别主体形态原型（单腔柜 / 双腔柜 / 开放平板），每个 form_subtype 明确 → 满足形态主导类的 ③ slot 要求。门是否透明窗折入涂装（⑥）+ ⑤，不单列。

### Slot B：topology_module — breaker 场拓扑

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `stacked_din_rails` | forked_anchor | S2 (`4cb00767`) | L211-L214 (`_add_breaker_row` ×3) | eligible if compatible | `rail_count`∈{2,3} 条水平 DIN 轨堆叠，每轨 `_add_breaker_run(count)` 沿 X 排 MCB。2D 网格 = rail×count |
| `single_din_rail` | forked_anchor | single_din_rail@S2 | L211-L232 | eligible if compatible | 单条水平 DIN 轨（照明/子板）。1×count |
| `two_vertical_columns` | forked_anchor | S1 (`c548199a`) | L112-L121 | eligible if compatible | 2 条竖直立柱，每柱 `_add_breaker_run(count)` 沿 Z 堆叠 breaker。2 columns × per-col count |

同一 loop-emit helper `_add_breaker_run(orientation, count, articulated_slots)`（X 向=DIN 轨，Z 向=立柱），只换朝向 + 组数；`rail_count` 折入 topology 标签（`stacked_din_rails_2`/`_3`）。

### Slot D：mains_module — 主开关/母排装配

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `full_main_bay` | forked_anchor | S2 `_add_left_power_devices` | L107-L166 | eligible if compatible | 左侧独立功率仓：2 主 MCCB 壳 + 4 相 copper/brass 母排 + aux 三极 + meter。板加宽出左仓 |
| `bus_bars_only` | forked_anchor | S1 | L124-L130 | eligible if compatible | 水平 copper bus + neutral + earth 铜/黄铜排 + standoff/screw，无独立功率仓 |
| `mcb_only_subboard` | forked_anchor | mcb_only_subboard@S1 | L123-L135 | eligible if compatible | 去主开关/copper bus，仅 neutral+earth 排 + sub-feed 进线端子块 |

3 个候选，结构（part 组成 / 母排数量 / 有无独立仓）明显不同。

## 槽位图（slot graph）

pattern: parallel_children + multiplicity

```
enclosure(root, Slot A form)
  ├─[FIXED  origin@shell-interior]────────> breaker_bank (Slot B topo + Slot C count grid)
  │                                            └─[REVOLUTE axis=+X @module face]─> breaker_toggle_i  (real toggles at articulated_slots)
  ├─[FIXED  origin@shell-interior]────────> mains (Slot D)
  └─[REVOLUTE axis=±Z @front jamb knuckle]─> front_door | left_door,right_door   (absent for open_backplate)
```

- **enclosure ↔ breaker_bank / mains**：FIXED，`mount_fixed`，origin 落在 enclosure 内壁背板真实几何上；`MatingContract`(back_sheet −y ↔ 子件 back rib +y)。
- **enclosure ↔ door**：REVOLUTE 竖轴，origin 落在前门框 jamb 立柱上的真实 hinge knuckle（door 局部原点=铰边，`hinge_barrel` 跨局部 (0,0,0)，`MatingContract`(jamb −y ↔ hinge_barrel +y)）。`open_backplate` 无此 joint。
- **breaker_bank ↔ breaker_toggle_i**：REVOLUTE axis=+X（rocker），origin 落在 MCB 模块前面上；captured-rocker → 省 mating（grandfather）+ element-scoped `allow_overlap`。
- 互斥/派生：`open_backplate` ⇒ 无 door part/joint（toggles 仍是 moving joint，满足 ≥1 非-fixed）。`full_main_bay` ⇒ enclosure 派生一个左功率仓（`has_left_bay`），板宽增加。

## 每槽位 Module Emits / Interfaces

### Slot A / module single_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `enclosure`(root) + `front_door` | S1 L88-L218 |
| internal joints | `door_hinge` REVOLUTE axis=(0,0,±1) range [0, ~1.7] 关门=0 | S1 L214-L218（轴/范围采用 utility_box 闭门约定，非 baked-open） |
| upstream interface | root：无 upstream（parallel chassis） | — |
| downstream interface | shell 前开口内壁（door mate）+ 内壁背板（bank/mains mate） | S1 L88-L104 |

### Slot A / module two_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `enclosure` + `left_door` + `right_door` + center mullion(visual) | S2 L169-L363 |
| internal joints | `left_door_hinge` / `right_door_hinge` REVOLUTE 竖轴，向 −Y 外开 | S2 L341-L363 |

### Slot A / module open_backplate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `enclosure`(平板 backplate，无门) | open_backplate@S2 L169-L208 |
| internal joints | 无 door joint（toggles 保留为 moving joint） | open_backplate@S2 L289-L303 |

### Slot B / module _add_breaker_run（stacked/single/columns 共用）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `breaker_bank`(FIXED child) | S2 L319-L327 |
| visuals | 每 group：din_rail/well + upper_body + lower_body + center_step + label_strip + end_terminal；每 module：seam + terminal screw + 装饰 toggle（`articulated_slots` 处省略给真 toggle） | S2 `_add_breaker_row` L80-L104 |
| internal joints | 无（field 本体全 visual）；真 toggle 在 Slot 交叉见下 | — |

### Slot C（multiplicity）/ breaker_toggle_i
| emits | 描述 | 来源 |
|---|---|---|
| parts | `breaker_toggle_i`（i<n_toggles，取中间 group 的 articulated_slots） | S2 L366-L379 |
| internal joints | `toggle_pivot_i` REVOLUTE axis=(1,0,0) range [-0.42,0.42] | S2 L370-L379 |
| upstream interface | 模块前面（pivot boss，joint origin 落其上） | S2 L375 |

### Slot D / module mains（full_main_bay / bus_bars_only / mcb_only_subboard）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mains`(FIXED child) | S2 L329-L337 |
| visuals | full：main MCCB×2 + phase busbar×4 + aux + meter；bus：copper bus + neutral + earth + standoff/screw；mcb：neutral+earth + sub_feed_terminal | S2 L107-L166 / S1 L124-L130 / mcb L123-L135 |

不动细节（label / seam / screw head / gland / knockout / standoff）一律 parent.visual，不作独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `form_module` | enum | single_door / two_door / open_backplate | single_door | choice | deterministic sampler | Slot A |
| `topology_module` | enum | stacked_din_rails / single_din_rail / two_vertical_columns | stacked_din_rails | choice | sampler；two_door+single_din_rail→bump stacked | Slot B |
| `mains_module` | enum | full_main_bay / bus_bars_only / mcb_only_subboard | bus_bars_only | choice | sampler | Slot D |
| `rail_count` | int(mult) | {2,3} | 3 | conditional | 仅 stacked_din_rails 生效；single=1；columns=2 columns | S2 L212 |
| `breaker_per_group` | int(mult) | [4,16]（DIN clamp[6,16]，columns clamp[4,12]） | 12 | conditional | 上限随 topology；`groups×per_group ≤ 42` | S2 L214 / S1 L117 |
| `palette_style` | enum | 5 colorways（见 §8.5 ⑥） | industrial_grey | choice | `rng.choice(PALETTE_STYLES)` | S1/S2 materials |
| `width_scale` | float | [0.92,1.08] | 1.0 | independent | clamp | ⑤ |
| `height_scale` | float | [0.92,1.10] | 1.0 | independent | clamp | ⑤ |
| `depth_scale` | float | [0.92,1.10] | 1.0 | independent | clamp | ⑤ |
| (—) | constraint | — | — | inequality | `board_w = wall*2 + (left_bay_w if has_left_bay) + field_w(topo,count) + margins`；`board_h = wall*2 + field_h(topo,count) + bar_zone`：板尺寸由 field 足迹派生，不独立乱采 | 接口/clearance |
| (—) | constraint | — | — | inequality | `n_toggles = min(3, per_group)`（限 moving-joint 数，控 motion_qc 组合） | motion budget |

连续尺寸契约：先采 3 个 independent scale → 由 topology+count 方程派生 field 足迹与 board 尺寸 → inequality 把总 breaker 数 clamp 到 ≤42、per_group clamp 到 topology 上下限 → conditional 解析 rail_count/per_group 范围。

## 7.5 编译预算 / compile budget（必填）

**每-seed 预算：≤ 12s**（依据：全 Box+Cylinder，无 cadquery、无 mesh_from_geometry 放样线束——线束 = 断连岛+编译重风险，故 §排除项 明确 DROP）。最大 seed（two_door + stacked_din_rails_3 + full_main_bay + per_group=14，总 ~42 breaker）估 visual ~180（field spanning box/group + 每 module seam+toggle+1 screw；enclosure ~24；mains ~24；doors ~7×2）。tessellation：所有小螺丝/端子用 Box 头（不用 cylinder）以省三角面；prominent 硬件（top gland/knockout/round_lock）用 cylinder，全模型 cylinder < 40。N 个同构 MCB 复用同一 helper。motion_qc `max_pose_samples=32`（doors≤2 + toggles≤3 ⇒ ≤5 非-fixed joint）。sweep `--compile-timeout 120`（3× watchdog）。

## 8. Multiplicity / Copy Logic

**轴 1 — `breaker_per_group`（每 rail/column 的 MCB 数，主 N 轴）**
- `count_param`=`breaker_per_group`；`N_range`（产品域）=[4,16]，DIN clamp [6,16] / columns clamp [4,12]；sampling domain 加权：小 N 高频（8-12 峰），大 N 稀有（16 尾部）。
- copied object：一个 MCB 模块（seam + terminal screw head + 装饰 toggle box），`_add_breaker_run` 内 `for i in range(count)` + `f"{group}_module_{i}"` 命名，等距 pitch=0.034(X)/0.040(Z)，统一 policy；`articulated_slots` 处省装饰 toggle 让真 toggle part 就位。
- joint policy：module 本体全 visual（无 joint）；`articulated_slots`（中间 group 的少数 index）→ 真 `breaker_toggle_i` REVOLUTE。
- source/gating：S2 `_add_breaker_row(count=14)` L80-L104；`groups*per_group ≤ 42` clamp。

**轴 2 — `rail_count`（DIN 轨/立柱组数，次 N 轴，折入 topology 标签）**
- `count_param`=`rail_count`；`N_range`={2,3}（stacked_din_rails），single=1，columns=2 columns；加权 stacked(0.55,0.45)。
- copied object：一整条 rail-run（`_add_breaker_run` 一次），`f"rail_{r}"`/`f"col_{c}"` 命名，Z(轨)/X(柱) 等距，统一 FIXED-on-enclosure（field 属 breaker_bank）。
- source/gating：S2 3 轨 L212 / S1 2 柱 L113。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 门数 = {1门, 2门, 0门}（single_door/two_door/open_backplate，Slot A，forked_anchor S1/S2/open_backplate@S2）改变 door part+hinge joint 数；toggle 数 = §8 multiplicity。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：breaker_per_group [4,16] + rail_count{1,2,3}；total 6-42。 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | door=REVOLUTE 竖轴(±Z)；toggle=REVOLUTE 横轴(+X)；bank/mains=FIXED。声明的三型都在 sweep 出现（forked_anchor S1/S2）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何形态原型 | 有 | Slot A 3 原型：single_door=Volumetric Envelope(单腔柜)、two_door=Volumetric Envelope(双腔带中挺)、open_backplate=Planar Boundary(平板)。均 forked_anchor。form_subtype 已在 Slot A 表标注。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | 警示/回路 label 带、DIN 轨 label_strip、module seam、terminal screw head、门 nameplate/barcode——全 host-derived（贴 enclosure/door/module 前面，随 ⑤ 尺寸 + ③ 形态派生 z/x 位置，派生序 ③→⑤→④）。`record_only`+`world_knowledge_extrapolation`（S1/S2 labels）。装饰密度随 per_group 变。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | width/height/depth_scale ∈[0.92,1.10]；board_w/h 由 topo+count 派生 → 紧凑 0.55 到宽 1.1+。运动包络：door REVOLUTE 竖轴，向 −Y 外开 [闭0, 可行~1.5rad]，`motion_test_plan`=sampled collision + targeted `ctx.pose({door:open})` 验 AABB 向 −Y 移；toggle REVOLUTE 横轴 [−0.42,0.42]，targeted `ctx.pose({toggle:0.4})` 验 paddle 位移。跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)`。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 = painted/powder-coated sheet metal + exposed copper + brass terminal + molded white/black plastic + 彩色相绝缘。配色 5：industrial_grey / light_grey_powder / municipal_beige / graphite_dark / safety_blue。材质大类覆盖 ≥ ceil(0.5×5)=3（metal+plastic+copper 恒现）。 |

**收尾自检**：`template batch` 0-9 seed 里三门形态拉得开、灰/浅灰/米/深灰/蓝配色都现、label 贴面不悬空、门开合全程 + toggle rocker 不穿模。

## 9. 拓扑多样性审计

总组合数：A(3) × B(3, rail_count 折 2 档→~4 有效) × D(3) = 27~36 离散拓扑；× multiplicity(per_group ~8 有效档) ≈ 250+ combos。


seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次加权采 form/topology/mains，采 rail_count/breaker_per_group（加权小 N），采 palette_style 与 3 个 scale。`resolve_config` 内 gate：`two_door + single_din_rail → stacked_din_rails`；`has_left_bay = (mains==full_main_bay)`；clamp per_group 到 topology 上下限并保证 `groups*per_group ≤ 42`；`n_toggles=min(3,per_group)`。无 curated/modulo 主表；无 regression override（首版）。Topology target：1000-seed distinct 期望 按 ≥300 report-only 口径观察（27+ 拓扑 × 尺寸/count）。random sweep 0-35 初验，corner stage 探未实现极值。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权 choice(form/topology/mains) + 加权小 N(per_group,rail_count) + scale/palette | slot_choices_for_seed == build choices |
| compatibility matrix | 合法：全组合；gate：two_door×single_din_rail→stacked；derive：full_main_bay⇒has_left_bay 板加宽 | 无 floating/collision/axis/max-mult/bulky/optional-child fail |
| controlled local variation | width/height/depth_scale∈[0.92,1.10] clamp；board 尺寸 equation 派生自 topo+count | 比例变而不破 interface/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-15 fast, 16-35 final, corner | contract fail；axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A form | 3 | yes | yes | |
| B topology | 3 | yes | yes | rail_count 折入标签 |
| D mains | 3 | yes | yes | |

## Validator

- slot_choices_for_seed returns implemented module names (form/topology/mains + count/rail labels)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds incl. seed 0
- gate prevents two_door × single_din_rail; has_left_bay derived from full_main_bay
- breaker_per_group clamped to topology band; groups*per_group ≤ 42
- board_w/board_h derived from topology+count (single-sourced helper), never free-sampled
- every door hinge is REVOLUTE vertical axis with hinge_barrel containing local (0,0,0) + MatingContract to a real front jamb; open_backplate has no door part/joint
- every toggle is REVOLUTE +X axis; n_toggles=min(3,per_group); joint origin on module face; captured-rocker allow_overlap declared
- fail_if_parts_overlap_in_sampled_poses + targeted ctx.pose per door + per toggle
- palette_style drives EVERY .visual(material=...) off mats[...]

## Reject cases

- 门被 baked-open 建模（S1 反模式）——必须闭门 rest 位、hinge 0=关。
- breaker field 逐块复制粘贴（非 `_add_breaker_run` loop）。
- door hinge origin 落在门中缝/空气里而非 jamb knuckle 上（>15mm anchor fail）。
- toggle/breaker 用 Box 冒充 DIN 轨结构却丢掉 loop 网格身份。
- open_backplate 仍留 door part 或 door_hinge joint。
- full_main_bay 板没加宽导致左仓与 field 重叠。
- 线束 mesh 端点悬空成 disconnected island（本模板不产线束）。
- palette_style 不驱动 material → sweep 输出单色。

## 与相邻类别的边界

- 不该混入：`Electrical_Wiring_Circuit_breaker`（单个断路器；本类是**多**断路器的配电箱，有 enclosure+door+field+busbar）。
- 不该混入：`Electrical_Wiring_Junction_box`（裸接线盒，无 breaker field / busbar / 铰链 deadfront 门）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | spec 每候选均 forked_anchor + Lx-Ly；无单候选 slot；拓扑审计+编译预算齐备（GATE P3）。门采 S2 闭门约定，线束 DROP 控编译/岛风险。 |

## 模板实现备注（可选）

- 共享 helper：`_add_breaker_run(part, group_name, *, count, orientation, x0, z0, articulated_slots)` 供三 topology 复用；`_build_door_leaf` 采 utility_box 铰边-局部原点 + hinge_barrel 跨 (0,0,0) 约定。
- `mount_fixed` 挂 breaker_bank / mains 到 enclosure 内壁背板（单一 placement 源）。
- captured-rocker：`allow_overlap(breaker_toggle_i, breaker_bank, elem pivot↔module_body)` element-scoped。
- door：`allow_overlap(door, enclosure, hinge_barrel↔jamb/side_wall/mullion)` + 闭门 leaf↔lip。
- full_main_bay 左仓 + field 右仓由 `has_left_bay` 单点派生，mullion 全高防浮岛。
