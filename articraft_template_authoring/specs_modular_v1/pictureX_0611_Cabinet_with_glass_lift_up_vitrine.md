# pictureX_0611_Cabinet_with_glass_lift_up_vitrine — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Cabinet_with_glass_lift_up_vitrine` |
| template path | `agent/templates/pictureX_0611_Cabinet_with_glass_lift_up_vitrine.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Cabinet_with_glass_lift_up_vitrine_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (opening panels + shelves are children/visuals of the single glazed carcass) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in this subcategory (2 origins + 10 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：两个 origin 结构互异——001 是四腿蜜橡木矮柜，正面两扇近无框玻璃 lift-up 板（revolute，轴 -X，upper≈1.22），一块玻璃层板 + 铜夹；002 是墙挂三仓白漆柜，铝框顶掀玻璃 flap（revolute，轴 +X），四块玻璃层板。两 origin 均已 loop-emit 腿/隔板/层板。10 个 fork 覆盖：机制（top_lid_single / sliding_glass / gullwing_top）、body（tower / tabletop）、frame（frameless）、base（plinth）、shelf_2/3，外加 frameless×sliding 兼容 probe。所有 fork 保持“玻璃展示柜 + 一个真实非固定 lift-up/slide 关节 + 可见 hinge/rail 接口 + 内部玻璃层板”的身份。

## 核心身份
一个**玻璃展示柜（vitrine）**，主功能是通过一个 **LIFT-UP（掀起）开口**取放展品：掀起的可以是正面铰接玻璃板、顶部铰接玻璃盖/flap、gull-wing 双盖，或横向滑移的玻璃板。柜体四周（侧/后/顶或前）为透明玻璃围合，内部有 1–4 块玻璃展示层板。定义性特征是 **opening_mechanism ②**：无论何种形态，必须保留一个**真实的非固定关节**（铰接盖用 REVOLUTE，滑移/升降板用 PRISMATIC），且在 carcass 与运动玻璃子件之间有**可见的 hinge barrel 或导轨接口** + MatingContract。

不该混入：实心木门/不透明门柜（must_not_become：solid-panel door cabinet）、抽屉柜（drawer chest）、开放层架（open shelf）、无盖密封玻璃缸（aquarium/tank，缺少可开启关节）。

## 槽位 + 候选模块表

### Slot A：body_form（③ 主体形态家族 / Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| low_case | origin_anchor | rec_...__001__... | L236-L456 | eligible if compatible | 矮宽玻璃柜 W≈1.10 D≈0.42，抬起玻璃围合体，四腿或封闭底座；Planar Boundary Form（矮长方开口） |
| tower | forked_anchor | var_tower | L249-L400 | eligible if compatible | 高窄塔形 W≈0.55，OVERALL≈1.75，细长玻璃围合；Volumetric Envelope Form（竖长体量） |
| tabletop | forked_anchor | var_tabletop_case | L241-L400 | eligible if compatible | 桌面小柜 W≈0.35 D≈0.22，矮，底板直接坐面；Volumetric Envelope Form（小立方体量） |
| wall_mount | origin_anchor | rec_...__002__... | L183-L335 | eligible if compatible | 墙挂宽柜 W≈1.60 D≈0.32 case_h≈0.58，后置 wall_cleat + base_plinth；Planar Boundary Form（水平墙板） |

### Slot B：opening_mechanism（② 关节类型，**定义性槽位**，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| front_dual_panes | origin_anchor | rec_...__001__... | L58-L170 | eligible if compatible | 正面两扇玻璃板；REVOLUTE 轴 -X（top-front 铰接，向上/外掀）；可见 hinge_barrel_i；upper≈1.2 |
| front_single_flap | origin_anchor | rec_...__002__... | L40-L122, L373-L390 | eligible if compatible | 正面一扇金属框玻璃 flap；REVOLUTE 轴 +X（top 铰接，awning 掀起）；hinge_boss；upper≈1.05 |
| top_single_lid | forked_anchor | var_top_lid_single | L347-L429 | eligible if compatible | 顶部整幅后铰盖；REVOLUTE 轴 -X（rear-hinge，前缘抬起）；连续 hinge_barrel；upper≈1.30 |
| top_gullwing | forked_anchor | var_gullwing_top | L382-L470 | eligible if compatible | 顶部沿中脊双盖；两个 REVOLUTE 轴 ±X（gull-wing）；central_ridge + hinge_boss |
| front_slider | forked_anchor | var_sliding_glass | L66-L187 | eligible if compatible | 正面滑移玻璃板；PRISMATIC 轴 +X（沿导轨横移半个开口）；top_guide_rail + bottom_track |

open-face 约束：`front_*` 打开正面（顶为固定玻璃 + 框），`top_*` 打开顶面（正面为固定玻璃）。互斥由 open_face 决定，见槽位图。

### Slot C：frame_construction（① 骨架，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wood | origin_anchor | rec_...__001__... | L279-L396 | eligible if compatible | 蜜橡木四角立柱 + 顶框 rails + 玻璃 beads；part/visual 数多 |
| metal | origin_anchor | rec_...__002__... | L224-L252 | eligible if compatible | 缎面铝薄框 + edge band；立柱换细铝 |
| frameless | forked_anchor | var_frameless_glass | L276-L470 | eligible if compatible | 无立柱/无 beads，边粘全玻璃 + 不锈钢 hinge only；结构件减少（visual 数下降） |

### Slot D：base_style（① 支撑子结构，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| legs | origin_anchor | rec_...__001__... | L279-L289 | eligible if body∈{low_case,tower} | 四条内嵌方腿 + 底板 deck |
| plinth | forked_anchor | var_plinth_base | L21-L40, build | eligible if body∈{low_case,tower,tabletop} | 连续封闭 plinth box（含 toe-kick）在底板下；静态底座 |
| wall_cleat | origin_anchor | rec_...__002__... | L253-L264 | forced if body==wall_mount | 后置墙挂 cleat + 浅 base_plinth 条 |

### Slot E：shelf_count（N multiplicity，见 §8）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| glass_shelf ×N (N∈1..4) | origin_anchor + forked | 001 L398-L415 / var_shelf_2 / var_shelf_3 / 002 L268-L286 | eligible | 一块 clear-glass 层板 + 四个角夹，Z 向均布；静态 fixed visual（无关节） |

硬约束满足：A=4, B=5, C=3, D=3 candidate，均 ≥2 且 source-backed；无单 candidate 槽位。

## 槽位图（slot graph）

pattern: parallel_children

```
             carcass (root, body_form ③ + frame_construction ① + base_style ①)
                │  (all static frame/glass/shelf geometry are carcass visuals)
   ┌────────────┼─────────────────────────┐
   │            │                          │
 base_style   shelf_count ×N            opening_mechanism ②
 (visual)     (static visuals+clips)    (moving glazed child part(s))
                                            │
                        REVOLUTE (front_dual_panes/front_single_flap/top_single_lid/top_gullwing)
                         or PRISMATIC (front_slider)
                          child = glass panel/lid/slider
```

跨 slot 连接（carcass → moving child）：
- 接口点位：`front_*` = carcass 前上沿 hinge_barrel / top_guide_rail 面；`top_*` = carcass 顶后沿或 central_ridge 上 hinge_barrel 面。
- joint type/axis/range：见 Slot B 表；每个 non-fixed joint 声明 MatingContract（parent = 可见 hinge barrel/guide rail visual，child = 运动玻璃件的 top/edge 接口 visual）。
- open_face 决定顶/前哪面是固定玻璃、哪面被运动件覆盖，互斥；shelves 与 base 恒为 carcass 静态 visual，不与开口机制冲突。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form（在 carcass 上发射静态包络）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（全部 carcass visual） | 001/002/var_tower/var_tabletop |
| internal joints | 无 | — |
| upstream interface | 无（root） | — |
| downstream interface | 开口面（前或顶）的 hinge/rail 安装面，供 Slot B 消费 | 001 L419-451 |

### Slot B / opening_mechanism（唯一活动件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `glass_panel_0/1`(front_dual) / `flap`(front_single) / `lid`(top_single) / `left_lid`,`right_lid`(gullwing) / `slider`(front_slider) | 各 variant |
| internal joints | `panel_lift_i` REV -X / `flap_lift` REV +X / `lid_lift` REV -X / `gullwing_lift_i` REV ±X / `slide` PRIS +X | 各 variant |
| upstream interface | 运动件 top/edge 接口 box（positive_z 或对应面），mate 到 carcass hinge_barrel/guide_rail | 001 L154-169 |
| downstream interface | 无（叶子） | — |

### Slot C/D（frame / base：carcass 静态 visual，无关节）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part | 各 variant |
| internal joints | 无 | — |

### Slot E / shelf_count（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（carcass visual：`glass_shelf_{s}` + `shelf_clip_{s}_{ix}_{iy}`） | 001 L398-415 |
| internal joints | 无（静态） | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | low_case/tower/tabletop/wall_mount | low_case | choice | 由 procedural sampler 选 | Slot A |
| opening_mechanism | enum | front_dual_panes/front_single_flap/top_single_lid/top_gullwing/front_slider | front_dual_panes | choice | sampler 选；决定 open_face | Slot B |
| frame_construction | enum | wood/metal/frameless | wood | choice | sampler 选 | Slot C |
| base_style | enum | legs/plinth/wall_cleat | legs | conditional | body==wall_mount→wall_cleat；tabletop→plinth；否则 legs/plinth | Slot D |
| shelf_count | int | [1,4] | 1 | independent | 小 N 偏多；clamp[1,4] | Slot E |
| palette_style | enum | oak/painted/industrial/walnut | oak | choice | ⑥ 涂装，per-seed | common PALETTES |
| width | float | body-dependent [min,max] | per body | conditional | 由 body_form 定名义值，±jitter 后 clamp | 各 variant WIDTH |
| depth | float | [0.20,0.46] | per body | independent | clamp | 各 variant DEPTH |
| case_height | float | body-dependent | per body | conditional | 由 body_form 定，clamp | 各 variant |
| open_travel | float | REV [0.9,1.35] / PRIS [0.4·opening,…] | per mech | equation | REV=固定上界；PRIS = opening − panel_width（求解） | 各 variant motion_limits |
| (—) | constraint | — | — | inequality | panel_width < front_opening；slider travel ≤ opening−panel；lid ≤ opening 尺寸 − clearance | clearance |

连续尺寸采样契约：先采 width/depth/case_height 名义（由 body_form 条件解析）+ 小 jitter → 派生 opening/panel 尺寸（equation）→ 用 inequality 把 panel/travel 回缩到开口内 → clamp。全部在 `resolve_config` 求解。

### 7.5 编译预算 / compile budget
每-seed 预算 **≤ 10s**（依据：几何全为 Box + 少量 Cylinder，无布尔/放样/mesh，典型简单模板 5–10s）。分档：hinge barrel/clip 等小 Cylinder ≤24 段；无英雄曲面。N 块层板复用同一 Box 构造循环。`--compile-timeout 120` 仅作看门狗。

## Multiplicity / Copy Logic
- count_param: `shelf_count`
- N_range（产品域）：[1,4]；sampling domain：加权偏小（1–2 高频，3–4 稀有），测试全程 1..4 都出现
- copied object：一块 clear-glass 层板 + 四个角夹（bronze/metal clip）
- naming：`glass_shelf_{s}`，`shelf_clip_{s}_{ix}_{iy}`
- placement：在 opening_bottom 与 case_top 之间 Z 向均布，位于玻璃围合内、避开运动件行程
- joint policy：层板为静态 fixed carcass visual（无 articulation）；唯一非固定关节是开口机制
- source/gating：001（N=1）/ var_shelf_2（N=2）/ var_shelf_3（N=3）/ 002（N≈4）

## 视觉多样性 6 轴考察
| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame_construction：wood 立柱+rails+beads(001) / metal 铝薄框(002) / frameless 边粘全玻璃无立柱(var_frameless)；base_style：legs(001)/plinth(var_plinth)/wall_cleat(002)。均 forked_anchor/source-backed |
| └ multiplicity | 同构件 ×N | 有 | shelf_count N∈[1,4]，见 §8（小 N 偏多） |
| ② 关节类型 | 图不变换 type/轴 | 有 | REVOLUTE 轴 -X(front_dual/top_single) / 轴 +X(front_single_flap) / 轴 ±X(gullwing) + PRISMATIC 轴 +X(front_slider)。5 种均 source-backed，sweep 里都出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | body_form：low_case / tower / tabletop / wall_mount，登记进 slot_choices；form_subtype：low_case=Planar Boundary、tower=Volumetric Envelope、tabletop=Volumetric Envelope、wall_mount=Planar Boundary。source-backed(001/002/var_tower/var_tabletop) |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | 玻璃 beads / edge caps / finger pull / dark edge seals / gaskets；host-conformal 写成 carcass 或运动件 visual，随 ③⑤ 尺寸派生；无独立 variant |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | width：low_case[0.95,1.25] tower[0.48,0.62] tabletop[0.30,0.42] wall_mount[1.40,1.80]；case_height 随 body；关节包络见下 motion_test_plan；关节全程不穿模 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 glass+wood+metal(+painted)；配色 4 档 oak/painted/industrial/walnut（common PALETTES），材质大类覆盖 ≥ ceil(0.5×4)=2 |

motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)`；每种机制加 targeted `ctx.pose`：
- 前掀（front_dual/front_single）：轴 ±X，[0, upper≈1.0–1.2]，验证前缘 up+out（-Y & +Z）不撞侧玻璃。
- 顶盖（top_single/gullwing）：轴 ∓X，[0,1.3]，验证前缘/半盖抬起（+Z）不撞后玻璃。
- 滑移（front_slider）：轴 +X，[0, opening−panel]，验证横移（+X）保持同 Z、不越出开口、rail 咬合（allow_overlap）。

## 采样与覆盖审计

总组合数：body 4 × opening 5 × frame 3 × base(有效 ~2.x) × shelf 4 ≈ 400+（乘 palette 4 ≈ 1600），远超成熟度观察阈。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)` 对每个离散槽位加权采样，连续尺寸按 body_form 条件解析名义值 + jitter，`resolve_config` clamp/派生/回缩。seed=0 不特殊。

Procedural Sampling / Sweep Plan：sampler 先选 body_form → 据此解析 base 合法集 → 选 opening（决定 open_face）→ 选 frame → 选 shelf_count（加权偏小）→ 选 palette。compatibility gating：wall_mount 强制 wall_cleat；tabletop 强制 plinth；frameless×front_slider = probe 组合（源已 converge，允许但列为风险监控）。无 curated/modulo 主表；无 regression override（如遇回归再加，注明 seed+理由）。

Topology target：1000-seed slot tuple 覆盖用于成熟度观察，report-only。

Controlled local parameterization：width/depth/case_height（body 条件）、open_travel（机制派生）、shelf spacing（N 派生）；全部 clamp/派生，不破坏 hinge/rail 接口、clearance、joint 轴、类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body→base gating→opening→frame→shelf(加权)→palette | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | wall_mount→wall_cleat；tabletop→plinth；frameless×slider 允许(probe) | 无悬空/穿模/轴/closed-pose/多层板失败 |
| controlled local variation | body 条件尺寸 + 机制行程派生 + clamp | 比例变化不破坏接口/间隙/joint 原点/身份 |
| regression overrides | none | 仅已知回归/审核样本 |
| random sweep | 0-15 fast, 0-35 final, corner stage | 契约失败；axis_realization；viewer 目检 0-9 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | ③ 主体形态家族 |
| opening_mechanism | 5 | yes | yes | ② 定义性槽位 |
| frame_construction | 3 | yes | yes | ① |
| base_style | 3 | yes | yes | ① 条件 gating |
| shelf_count | 4(N) | yes | yes | multiplicity |

## Validator
- slot_choices_for_seed 返回已实现 module 名（body_form/opening_mechanism/frame_construction/base_style/shelf_count/palette_style）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility gating 阻止非法组合（wall_mount 必 wall_cleat；tabletop 必 plinth）
- 无 curated/modulo 主 seed 域；无长期轮换小表
- controlled local scale 在 resolve_config clamp/派生，不破坏接口/clearance/joint 原点/multiplicity
- 关键 MatingContract 存在：每个非固定开口关节 parent=可见 hinge barrel/guide rail visual，child=运动件接口 visual
- 关键关节 type/axis/range：REVOLUTE(-X/+X/±X) / PRISMATIC(+X)，range 与源一致
- 复制层板遵循命名/placement policy
- run_tests 含 `fail_if_parts_overlap_in_sampled_poses` + 每机制 targeted ctx.pose

## Reject cases
- 顶开与前开同时把顶和前都做成固定玻璃 → 没有 open face，运动件无处安放（非法）
- 运动玻璃件在 closed pose 与 carcass 侧玻璃/立柱穿模（未留 clearance）
- 前掀板铰接轴方向反了 → 板向内扫进柜体（穿模）
- 滑移板行程越出开口，或未与导轨咬合（悬空/漂浮）
- 把 lift-up 关节退化成 FIXED，或做成实心不透明门（漂移到 door cabinet / 失去 identity）
- 层板数量超范围或未均布导致与运动件行程冲突
- frameless 仍保留木立柱/beads（未真正减结构件，① 无差异）

## 与相邻类别的边界
- 不该混入：solid-panel door cabinet（理由：本类必须透明玻璃围合 + lift-up 开启，不是不透明侧铰门）
- 不该混入：drawer chest / open shelf（理由：主关节是 lift-up/slide 玻璃，不是抽拉屉或无门层架）
- 不该混入：aquarium/sealed tank（理由：必须保留可开启的非固定关节，不是密封缸）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | scaffold→full spec；候选均 source-backed；GATE P3 self-check 通过，直接进模板 |
