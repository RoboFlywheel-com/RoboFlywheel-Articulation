# Modular Spec — ironing_board

## 元信息
| 项 | 值 |
|---|---|
| slug | `ironing_board` |
| template path | `agent/templates/ironing_board.py` |
| test path (optional) | `tests/agent/test_ironing_board_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (single `board` root carrying folding leg children + a prismatic height mechanism + an optional FIXED under-shelf; iron-rest / notch-teeth / cover-dots are loop-emitted host visuals) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

Read: `rec_...__002` (double-pivot X + prismatic latch + notch rail + wire-loop rest), `rec_...__001`
(sliding-pivot X on translating slider + tubular rack rest), `rec_ironing_board_var_form_rounded_oval`
(oval planform fork of 001), `rec_ironing_board_var_skeleton_tabletop` (short fold-flat legs, fixed height),
`rec_ironing_board_var_shelf_linen_rack` (FIXED lower wire shelf, N=6 rungs), `rec_ironing_board_var_shelf_rack_n10`
(same shelf, N=10). All 6 are adopted.

## 核心身份

一块细长、逐渐收窄的软垫（织物包覆）熨衣面板，架在一副可折叠的支腿上。核心功能：提供可调高度、可收折的熨烫工作面。
must_keep：细长织物包覆熨面（多孔金属底板 + 软垫布罩）；把面板抬起并可收折的折叠腿架（真实非-FIXED 腿铰）；高度/收折机构（腿 revolute + 在锯齿导轨上滑动的 prismatic 高度锁）。
不该混入：折叠桌 / 边桌、晾衣架 / 挂衣架、工作台、切菜板、袖板（sleeve board）。这些要么没有细长收窄熨面，要么没有折叠腿+高度机构。

## 槽位 + 候选模块表

### Slot A：leg_skeleton（腿骨架 + 内建高度机构，① + ②）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `double_pivot_X` | forked_anchor | rec_...__002 | L258-L327 | eligible if compatible | 两副腿对（rear/front）各自 REVOLUTE 直接铰在 board 上（双铰 X 交叉）；额外 `height_latch` part 走 PRISMATIC 沿 board 底面锯齿导轨；part 树 = board + rear_leg_pair + front_leg_pair + height_latch |
| `sliding_pivot_X` | forked_anchor | rec_...__001 | L384-L506 | eligible if compatible | 前腿 REVOLUTE 铰在 board，后腿 REVOLUTE 铰在一个沿 board 平移的 `height_slider`（PRISMATIC）上（滑动铰 X）；part 树 = board + height_slider + front_leg + rear_leg，链 board→slider→rear_leg |
| `tabletop` | forked_anchor | rec_ironing_board_var_skeleton_tabletop | L273-L330 | eligible if compatible | 两副短腿各自 REVOLUTE 铰在 board，收折时与 board 底面共面平贴；**无** prismatic 高度机构（固定矮桌面高度）；part 树 = board + rear_leg_pair + front_leg_pair |

### Slot B：board_planform（熨面平面形态，③ Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| `pointed_taper` | forked_anchor | rec_...__002 | L27-L91 | eligible if compatible | 尖鼻收窄 + 圆钝尾的经典熨板轮廓；`_half_width_at_x` sin^0.56 律 + 椭圆尾帽。**form_subtype = Planar Boundary Form** |
| `rounded_oval` | forked_anchor | rec_ironing_board_var_form_rounded_oval | L32-L84 | eligible if compatible | 两端圆角、近平行侧的 stadium / discorectangle 轮廓（端弧半径 R）。**form_subtype = Planar Boundary Form** |

同一 part 树、同一 extrusion primitive 家族（`MeshGeometry` 闭合放样）、同一 interface（board 顶面/底面 + 铰点 x），只改变平面边界离散形态 → 合法 ③ 结构差异（AUTHORING §A Rule 3 / §B）。

### Slot C：iron_rest（后端熨斗托，附件层 — 非关节，融入 board part 的 host visual）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `wire_loop` | forked_anchor | rec_...__002 | L158-L164 | eligible if compatible | 后尾一圈细钢丝托环（`_wire_rest_mesh`，两条 spline tube），嵌进 board 尾部 |
| `tubular_rack` | forked_anchor | rec_...__001 | L291-L336 | eligible if compatible | 后端焊接黑管托架：外环 rail + 3 根 crossbar + 托盘板 `rear_rest_plate` + 2 根支撑柱 |

两者均为非-articulating 结构（Rule 1 → `board.visual(...)`，不作独立 FIXED part），但网格拓扑/part-count 明显不同 → 合法结构候选。

### Slot D：under_shelf（下层收纳网架，① 增量结构 + N multiplicity）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor (default) | rec_...__001 | (无 shelf part) | eligible if compatible | 无下层网架（默认，001 形态） |
| `linen_shelf` | forked_anchor | rec_ironing_board_var_shelf_linen_rack | L158-L212, L386-L411 | eligible if leg_skeleton∈{double_pivot_X, sliding_pivot_X} | 独立 `linen_shelf` part，FIXED 铰在 board；周边钢丝框 + N 根纵向 `rung_{i}`（loop-emitted）+ 可见 drop_supports 吊到 board 底架 |

`none` 与 `linen_shelf` 在 part 树上真实不同（多一个 FIXED part + N 复制件），是合法 ① 增量结构槽。`linen_shelf` 需要满高腿的悬挂空间，故 gated：仅当腿骨架不是 tabletop。

> height_adjust 不单列为 slot：它由 leg_skeleton 决定（double_pivot_X→`height_latch`；sliding_pivot_X→`height_slider`；tabletop→无）。source map 只有一个真实来源机构，摩擦夹/固定高度替代无来源支撑（record_only），故折入 leg_skeleton 而非做单-candidate 槽。

## 槽位图（slot graph）

pattern: mixed（parallel children + serial sub-chain on slider + fixed accessory）

```
board (root)
 ├─[REVOLUTE axis=±y, origin=board 底面铰线] rear_leg_pair / front_leg_pair        (double_pivot_X, tabletop)
 ├─[PRISMATIC axis=+x, origin=board 底面导轨] height_latch                          (double_pivot_X)
 ├─[PRISMATIC axis=+x] height_slider ─[REVOLUTE axis=-y]→ rear_leg                  (sliding_pivot_X)
 ├─[REVOLUTE axis=+y] front_leg                                                     (sliding_pivot_X)
 ├─[FIXED, drop_supports 触 board 底架] linen_shelf {rung_0..N}                     (under_shelf=linen_shelf)
 └─ board.visual: cover mesh(planform) + metal plate + cover_dots + underside_holes
              + iron_rest(wire_loop|tubular_rack) + notch_rail(+notch teeth)
              + hinge/slider guide brackets
```

- 所有 slot 的 part 都以 `board` 为直接或（滑块链）间接 parent；board 是唯一 root。
- 跨 slot 接口点位：腿铰 = board 底面铰线（x∈[-0.35,+0.45], z≈-0.055）；滑块 = board 底面锯齿导轨 (x 方向 prismatic)；后腿 = 滑块上的横铰销；shelf = board 底架 rail（drop_supports 触点）。
- 互斥/gating：`height_latch`/`height_slider` 二选一由 leg_skeleton 决定；`tabletop` 无高度件、无 notch rail；`linen_shelf` 仅在满高腿骨架下出现。

## 每槽位 Module Emits / Interfaces

### Slot A / module double_pivot_X
| emits | 描述 | 来源 |
|---|---|---|
| parts | rear_leg_pair, front_leg_pair, height_latch | 002 / L258-L299 |
| internal joints | board_to_rear_leg REVOLUTE axis(0,1,0) [0,1.18]; board_to_front_leg REVOLUTE axis(0,-1,0) [0,1.18]; board_to_height_latch PRISMATIC axis(1,0,0) [0,0.11] | 002 / L301-L327 |
| upstream interface | 铰在 board 底面 (x=+0.42 rear, x=-0.32 front, z=-0.055)；board 侧 hinge_bracket visuals 锚定 | 002 / L242-L256 |
| downstream interface | 无（leg/latch 是末端子件） | — |

### Slot A / module sliding_pivot_X
| emits | 描述 | 来源 |
|---|---|---|
| parts | height_slider, front_leg, rear_leg | 001 / L384-L478 |
| internal joints | board_to_height_slider PRISMATIC axis(1,0,0) [0,0.12]; board_to_front_leg REVOLUTE axis(0,1,0) [0,1.05]; slider_to_rear_leg REVOLUTE axis(0,-1,0) [0,0.82] | 001 / L480-L506 |
| upstream interface | board 底面：front hinge (x=+0.30,z=-0.060)、slider guide rail (x=-0.20,z=-0.060)；board 侧 front_hinge_bracket / slider_guide_bracket visuals | 001 / L359-L382 |
| downstream interface | slider 提供 rear-leg 横铰销 `sliding_hinge_pin` | 001 / L384-L390 |

### Slot A / module tabletop
| emits | 描述 | 来源 |
|---|---|---|
| parts | rear_leg_pair, front_leg_pair | var_skeleton_tabletop / L273-L306 |
| internal joints | board_to_rear_leg REVOLUTE axis(0,1,0) [0,1.62]; board_to_front_leg REVOLUTE axis(0,-1,0) [0,1.62]（收折共面平贴） | var_skeleton_tabletop / L313-L330 |
| upstream interface | board 底面短铰线 (x=±0.22/0.28, z=-0.048)；board 侧短 hinge_bracket visuals | var_skeleton_tabletop / L256-L270 |
| downstream interface | 无 | — |

### Slot B / module pointed_taper · rounded_oval
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（改写 board 的 fabric_cover / metal_plate mesh + host-conformal cover_dots/holes） | 002 L190-L235 / oval L224-L242 |
| internal joints | 无 | — |
| interface | 提供 `half_width_at(x)` 供铰点 x、iron_rest、shelf、cover-dot 采样宿主面宽度 | 002 L27-L40 / oval L87-L95 |

### Slot C / module wire_loop · tubular_rack
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（board.visual 后端托架网格） | 002 L158-L164 / 001 L291-L336 |
| internal joints | 无（Rule 1：非-articulating → host visual） | — |
| interface | 坐在 board 尾部上方 (x≈0.6-0.9)，随 planform 尾宽贴合 | 002 / 001 |

### Slot D / module linen_shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | linen_shelf（perimeter + drop_supports + rung_0..N-1） | var_shelf_linen_rack / L386-L403 |
| internal joints | board_to_linen_shelf FIXED（drop_supports 触 board 底架 rail） | var_shelf_linen_rack / L405-L411 |
| upstream interface | drop_supports 顶端触 board underside_braces（expect_contact） | var_shelf_linen_rack / L195-L212 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| leg_skeleton | enum | double_pivot_X / sliding_pivot_X / tabletop | — | choice | procedural sampler | Slot A |
| board_planform | enum | pointed_taper / rounded_oval | — | choice | procedural sampler | Slot B |
| iron_rest | enum | wire_loop / tubular_rack | — | choice | procedural sampler | Slot C |
| under_shelf | enum | none / linen_shelf | none | choice + conditional | `linen_shelf` 仅当 leg_skeleton≠tabletop，否则回退 none | Slot D |
| n_shelf_rungs | int | [4,14]（小档偏多） | 6 | conditional | 仅 under_shelf=linen_shelf 生效；均匀跨 shelf 宽 | var_shelf_rack_n10 |
| n_notch_teeth | int | [4,12] | 6 | conditional | 仅 leg_skeleton∈{double_pivot_X,sliding_pivot_X}（有 notch rail）生效 | 002=6 / 001=7 |
| board_length_scale | float | [0.94,1.08] | 1.0 | conditional | 满高腿：full L≈1.45×scale；tabletop：compact L≈0.86×scale | 002/001/tabletop ⑤ |
| leg_reach_scale | float | [0.95,1.06] | 1.0 | independent | 腿 foot_x/foot_z 等比缩放，clamp | leg meshes |
| height_open | float | derived | ~0.80 | equation | `= leg_foot_z_world`（腿铰 z + foot reach），随 leg_reach_scale 派生 | leg meshes |
| material_style | enum | navy_dot / warm_white_palm / dark_frame | navy_dot | choice | 配色+框架材质大类 | 002/001 ⑥ |
| (—) | constraint | — | — | inequality | 腿铰 x 必须落在 board 顶面轮廓内：`|hinge_x| < 0.5·L − 0.10`；违反按比例回缩铰点 | 接口 |
| (—) | constraint | — | — | inequality | shelf 悬挂 z < board 底架 − 0.15（仅满高腿满足）→ gating 已保证 | var_shelf |

**采样契约**：先采 independent（leg_reach_scale）；按 equation 派生 height_open；conditional（board_length_scale 分档、n_shelf_rungs、n_notch_teeth）按上游 enum 解析；inequality 在 `resolve_config` 内把铰点 x 投影回可行域。所有 clamp/派生在 `resolve_config`。

### 7.5 编译预算 / compile budget
每-seed 预算 **≤20s**（依据：板体 2 张闭合放样 extrusion + 数条 spline tube + 少量 Box/Cylinder；无重布尔雕刻）。分档 tessellation：outline 42 采样点、tube `radial_segments≤18`、`samples_per_segment≤6`。N 根 rung/dot 复用同一 `_tube`/`Cylinder` helper。sweep `--compile-timeout 60`。

## Multiplicity / Copy Logic

两根独立 multiplicity 轴：

- **n_shelf_rungs** — count_param `n_shelf_rungs`；N_range 产品域 `[4,14]`（测试偏小端，sweep 上限 14）；采样档：小 N 高频、大 N 稀有；copied object = 纵向钢丝 `rung_{i}`，loop-emitted，跨 shelf 宽均匀间隔，共享 `_shelf_rung_mesh` helper；joint policy：shelf 整体 FIXED 挂在 board（rung 无独立关节）；source/gating：var_shelf_linen_rack(N=6) / var_shelf_rack_n10(N=10)；仅 under_shelf=linen_shelf 生效。
- **n_notch_teeth** — count_param `n_notch_teeth`；N_range `[4,12]`；copied object = 锯齿 V-notch，作为一条连续弯杆的 riser（002 风格 `_notch_rail_mesh`）或独立 tooth box（001 风格），loop-emitted 沿 board 底面导轨均匀间隔，FIXED host visual；source/gating：002=6 / 001=7；仅有 notch rail 的腿骨架（double_pivot_X / sliding_pivot_X）生效。

cover_dot / underside_hole 穿孔点为 ④ cosmetic copy logic（record_only），由 `half_width_at(x)` 逐-x 派生，不作候选锚点。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | double_pivot_X（2 腿铰+1 prismatic latch, 002）/ sliding_pivot_X（front 铰+slider prismatic+rear 铰 on slider, 001）/ tabletop（2 短腿铰, 无 prismatic, fork）；under_shelf 增一个 FIXED shelf part（fork）。全部 forked_anchor / source-backed |
| └ multiplicity | 同构件 ×N | 有 | n_shelf_rungs [4,14]、n_notch_teeth [4,12]；见 §8 |
| ② 关节类型 | 图不变换 type/轴 | 有 | REVOLUTE（腿铰 axis=±y）/ PRISMATIC（height_latch & height_slider axis=+x）/ FIXED（linen_shelf, 融入 board 的装饰）。每种都在 sweep 出现。source-backed（002/001/fork） |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | Planar Boundary Form：pointed_taper（尖鼻收窄，001&002）vs rounded_oval（两端圆角 stadium，fork）。登记进 `slot_choices`（board_planform）。source-backed |
| ④ 表面装饰 | 叠加表面细节/改装饰数 | 有(record_only) | cover_dot 点阵（navy 点印/warm-white palm）、underside 排气孔、iron_rest 后托、notch 齿；host-conformal：dot/hole 由 `half_width_at(x)` 逐-x 派生、随 ③/⑤ 共形（派生顺序 ③→⑤→④）。record_only + world_knowledge naming |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | board_length full≈1.45 / compact≈0.86（×[0.94,1.08]）；leg_reach ×[0.95,1.06]；开高 ~0.78–0.86；关节运动包络：leg REVOLUTE axis±y 开方向=腿脚上摆贴向 board，[闭合0, 可行上界 1.18（double）/1.05&0.82（sliding）/1.62（tabletop 共面）]；height PRISMATIC axis+x [0,0.11]（latch）/[0,0.12]（slider）。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` + 每机构 targeted `ctx.pose`：腿折叠脚上抬、latch/slider 沿 x 平移。continuous 无。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：fabric（navy/warm-white）+ metal（galvanized 银 / black powder-coat 黑）+ rubber 脚 + zinc 五金；配色档 ≥3（navy_dot / warm_white_palm / dark_frame），材质大类覆盖 ≥ ceil(0.5×3)=2 |

## 采样与覆盖审计

总组合数：leg_skeleton(3) × board_planform(2) × iron_rest(2) × under_shelf(2, gated) = 24 基础组合
（含 gating：tabletop 强制 under_shelf=none → 合法 = 2×2×2×2 满高 + 1×2×2×1 tabletop = 16 + 8 = 24）；
再乘 n_shelf_rungs(≈6 档) 与 n_notch_teeth(≈5 档) multiplicity → 数百个可辨 tuple。

理由：熨衣板结构词汇本就“简单档”（细长软垫面 + 折叠 X 腿 + 高度齿档），24 离散组合 + 两根 N 轴已覆盖真实产品域，不注水。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 先加权选 leg_skeleton（三者近均等）、board_planform、iron_rest、under_shelf；再按 gating 把 tabletop×linen_shelf 回退为 none；再采两根 N 轴与连续 scale。`resolve_config` 把铰点 x 投影回 board 轮廓可行域、按 leg_skeleton 分档 board 长度、clamp scale。无 curated/modulo 主表；无 regression override（初版）。seed 0 不特殊。
Topology target：1000-seed slot-choice-tuple 覆盖 report-only；真实组合空间数百，简单类合理。
Controlled local parameterization：board_length_scale [0.94,1.08]（conditional 分档）、leg_reach_scale [0.95,1.06]（independent）；均在 `resolve_config` clamp/派生，不破坏铰接口/悬挂 gating/关节行程/类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 槽加权 choice + 2 N 轴加权 + gating 回退 | slot_choices_for_seed matches build choices |
| compatibility matrix | tabletop→under_shelf=none 强制；notch teeth 仅满 notch-rail 腿；iron_rest/planform 全兼容 | no floating shelf, no leg 穿模, notch/latch 行程内不穿模 |
| controlled local variation | board_length/leg_reach scale，clamp + 铰点投影 | 比例变化不破坏铰接口/clearance/支撑/joint origin/类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass；0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| leg_skeleton | 3 | yes | yes | ①+② 主结构轴 |
| board_planform | 2 | yes | no | ③ Planar Boundary Form；样本池仅 2 个真实平面形态锚点 |
| iron_rest | 2 | yes | no | 附件层，非关节 host visual |
| under_shelf | 2 | yes | no | ① 增量结构 + N 轴 |

## Validator

- slot_choices_for_seed returns implemented module names（4 槽 + 2 N 轴）
- config_from_seed 对所有普通 seed（含 0）用 deterministic 采样
- gating 阻止 tabletop×linen_shelf、无 notch-rail 腿×notch teeth
- 无 regression override
- board_length/leg_reach scale 在 resolve_config clamp/派生，铰点 x 投影回轮廓
- 关键 InterfaceSpec/MatingContract：腿铰 hinge_bracket↔leg_tube（captured pin，element-scoped allow_overlap）；slider_guide↔pin；shelf drop_supports↔underframe（expect_contact）
- 关节 type/axis/range 与来源一致
- 复制件 `rung_{i}` / notch 命名有序、均匀间隔

## Reject cases

- 腿骨架无真实非-FIXED 铰（把折叠腿做成 FIXED）→ 违背核心身份
- linen_shelf 悬空（drop_supports 不触 board 底架）
- tabletop 仍带 prismatic 高度件 / notch 齿（矮桌面固定高度，无高度机构）
- cover_dot/hole 用常数半径套在收窄/圆角面外（Rule 4 共形失败）
- 腿铰 x 落到 board 轮廓外 → joint origin 悬空 / 铰无锚
- 把 iron_rest / notch 齿做成独立 FIXED part（应为 host visual, Rule 1）
- leg 折叠全程穿模（sampled-pose overlap）未消除也未 element-scoped 声明

## 与相邻类别的边界

- 不该混入：折叠桌 / 边桌 —— 熨板必须是细长收窄软垫面，不是矩形平桌面。
- 不该混入：晾衣架 / 挂衣架 —— 熨板主体是实心熨面而非挂杆阵列；under_shelf 只是附属收纳，不能反客为主。
- 不该混入：袖板 / 切菜板 —— 必须有折叠腿 + 高度机构，不是纯台面板。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 初版 spec→template 连续产出，driven to sweep verdict=pass on seeds 0-35 |

## 模板实现备注（可选）

- 统一坐标系：采用 002 帧（board 近原点，顶面 z≈+0.014，底面 z≈-0.032，满高腿脚 z≈-0.79）。sliding_pivot_X 来自 001 的几何整体下移 ~0.85 re-base 到此帧。
- captured-pin allow_overlap（element-scoped）：hinge_bracket↔leg_tubes（各腿）、slider_guide_bracket↔sliding_hinge_pin、sliding_hinge_pin↔rear_tube_frame、notch_rail↔slider_block/latch_nose。
- shelf drop_supports↔underside_braces/perforated_plate：element-scoped allow_overlap（焊接）+ expect_contact。
- iron_rest / notch teeth / cover dots：全部 `board.visual(...)`，非独立 part。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | leg_skeleton | double_pivot_X | rec_...__002 | L111-L327 | 双铰 X 腿 + prismatic latch + notch rail + brackets |
| S2 | leg_skeleton | sliding_pivot_X | rec_...__001 | L384-L506 | 滑动铰 X：slider(prismatic)+front/rear leg(revolute) |
| S3 | leg_skeleton | tabletop | rec_ironing_board_var_skeleton_tabletop | L117-L330 | 短腿 fold-flat 双铰，无高度机构 |
| S4 | board_planform | pointed_taper | rec_...__002 | L27-L91 | 尖鼻收窄轮廓 + 半宽律 |
| S5 | board_planform | rounded_oval | rec_ironing_board_var_form_rounded_oval | L32-L95 | stadium 轮廓 + 半宽律 |
| S6 | iron_rest | wire_loop | rec_...__002 | L158-L164 | 钢丝托环 mesh |
| S7 | iron_rest | tubular_rack | rec_...__001 | L291-L336 | 焊接黑管托架 + 托盘 |
| S8 | under_shelf | linen_shelf | rec_ironing_board_var_shelf_linen_rack | L158-L212,L386-L411 | 下层网架 perimeter+drop+rung×N，FIXED |
