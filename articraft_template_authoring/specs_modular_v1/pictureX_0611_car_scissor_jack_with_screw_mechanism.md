# pictureX_0611_car_scissor_jack_with_screw_mechanism — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_car_scissor_jack_with_screw_mechanism` |
| template path | `agent/templates/pictureX_0611_car_scissor_jack_with_screw_mechanism.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_car_scissor_jack_with_screw_mechanism_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (monolithic coupled scissor spine + feature variation + N multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 (1 origin + 12 forked/probe variants) |
| read_count | 13 |
| read_scope | all 5-star samples in this subcategory |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

自动化 **剪式（pantograph）千斤顶**：若干刚性冲压臂在角点用横向销轴铰接成一个（或堆叠多个）
闭合菱形连杆，一根**水平丝杠**穿过对置角点的螺母；摇动丝杠改变端块间距，使菱形升 / 降。
顶部承载鞍座，底部接地底盘，丝杠右端为摇柄接口。

核心运动学是一个 **1-DOF 耦合闭环**：URDF 不能直接表达闭环，故用一条**开链丝杠杆**表达菱形轮廓
（base→lower_arm→end_block→upper_arm→saddle→upper_arm→end_block→lower_arm），把丝杠回转
（`lead_screw` REVOLUTE，多圈）作为**唯一自由驱动关节**，所有臂铰接（REVOLUTE about y）以 `Mimic`
**耦合**到丝杠标量——这即"solved relation"：等臂菱形的臂角是丝杠行程的线性函数，故 mimic 乘子恰为 ±k
（k = 每丝杠弧度的臂角增量）。闭合姿态 = 全关节 0 = 装配菱形；驱动丝杠正向 = 升高。

不该混入：液压/瓶式(bottle/hydraulic)、望远式(telescopic)、地滚/trolley(带轮)千斤顶，及无丝杠的一般 pantograph 升降台。

## 槽位 + 候选模块表

> 本类别是**形态/机构一体的单体剪式千斤顶**，不用 `assemble()` 线性链；一个自定义 builder 按
> `config` 选每根特征轴，`slot_choices_for_seed` 汇报所选（与 rack_and_pinion_slider 同构）。

### Slot A：base_form（③ 主体形态家族 — 底盘）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| stamped_tray | origin_anchor | 001.png origin | `rec_picturex_..._001` L109-L142 | eligible if compatible | 浅冲压托盘+侧唇+中央铰接支架；Planar Boundary Form |
| wide_plate | forked_anchor | var_wide_plate_base | L109-L161 | eligible if compatible | 宽平接地板+支架；Planar Boundary Form（更宽轮廓）|
| dual_rail | forked_anchor | var_dual_rail_base | L109-L160 | eligible if compatible | ±y 双轨滑撬+桥接+支架；Macro Surface Construction |

### Slot B：linkage_topology（① 骨架 + N 级数）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_diamond | origin_anchor | 001.png origin | `rec_picturex_..._001` L221-L488 | eligible if compatible | 单菱形 4 臂 / 7 臂铰 + 2 端块；part tree 最简 |
| double_stage | forked_anchor | var_double_stage | L227-L500 (stage loop L357-L417) | eligible if compatible | 2 堆叠菱形 + mid_block 交叉铰；8 臂 + 4 端块 + mid_block（拓扑 & joint count 变、N=2）|

Slot B 降到 2 candidate 的 degrade reason：**exact 线性 mimic 闭环只对等臂对称菱形成立**（臂角是丝杠行程的
线性函数，乘子恰 ±k）。source map 的 "wide trapezoid frame" 若做成异臂/不对称锚点，臂角对驱动量变**非线性**，
线性 mimic 无法保持闭环→漂移/穿模。故 trapezoid 不作独立 mimic 拓扑，改由 ⑤ `base_span_scale` /
`arm_length_scale` / `closed_angle` 表达其加宽/梯形侧影（保持等臂菱形闭环）。合法降级（机构约束不足以再产结构不同 candidate）。

### Slot C：load_saddle（③ 主体形态 / ② 承载面）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| notched_yoke | origin_anchor | 001.png origin | `rec_picturex_..._001` L151-L171 | eligible if compatible | 齿槽鞍(tooth_a/b+center_ridge)；Macro Surface Construction |
| flat_plate | forked_anchor | var_flat_plate_saddle | L151-L215 | eligible if compatible | 平承载板；Planar Boundary Form |
| beam | forked_anchor | var_beam_saddle | L151-L234 | eligible if compatible | 宽倒-U 横梁鞍；Volumetric Envelope Form |

### Slot D：screw_drive（② 关节 / 螺母配置）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_nut | origin_anchor | 001.png origin | `rec_picturex_..._001` L174-L218,L463-L486 | eligible if compatible | 单固定螺母(左端块 FIXED)+旋转丝杠 |
| dual_nut | forked_anchor | var_dual_nut_screw / var_probe_trapezoid_dualnut | L174-L237 / L161-L300 | eligible if compatible | 对置螺纹双螺母(两端块各 1 FIXED 螺母，镜像螺纹)|

### Slot E：crank_interface（② 驱动接口）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| crank_eye | origin_anchor | 001.png origin | `rec_picturex_..._001` L200-L208 | eligible if compatible | 穿孔摇柄环眼(丝杠 visual，无新关节)|
| hex_socket | forked_anchor | var_hex_drive_socket | L174-L223 | eligible if compatible | 同轴六角驱动头+凹六角孔(丝杠 visual，无新关节)|
| folding_handle | forked_anchor | var_folding_crank_handle | L212-L262,L450-L470,L551 | eligible if compatible | 折出摇柄新 part `crank_handle`+REVOLUTE `lead_screw_to_crank_handle`(新增 1 关节)|

## 槽位图（slot graph）

pattern: `mixed`（单体耦合剪式脊 + 平行特征）

```
base(root, base_form ③)
  └─REVOLUTE(y, MatingContract lap @ base pin)──> lower_arm_0 (+y lane)
        └─REVOLUTE(y, lap)──> end_block_0 ──REVOLUTE(y, lap)──> upper_arm_0 (-y lane)
              └─REVOLUTE(y, lap)──> saddle(load_saddle ③) ──REVOLUTE(y, lap)──> upper_arm_1 (+y lane)
                    └─REVOLUTE(y, lap)──> end_block_1 ──REVOLUTE(y, lap)──> lower_arm_1 (-y lane, 自由尖端闭合回 base pin)
end_block_1 ──REVOLUTE(x, 多圈, DRIVER)──> lead_screw(screw_drive ② + crank ②)
end_block_0 ──FIXED──> threaded_nut   [dual_nut: 追加 end_block_1──FIXED──>threaded_nut_1]
lead_screw ──REVOLUTE(z, folding_handle only)──> crank_handle
```

- 接口点位：每臂铰 = **lap 面接触**（臂内 y-face 贴中央体外 y-face，法向 y，MatingContract 校验 gap=0）；丝杠 = 右端块螺孔轴(x)。
- 跨 slot joint：臂铰 REVOLUTE about y（mimic 到丝杠）；丝杠 REVOLUTE about x（唯一自由驱动，多圈=有效升程）；折柄 REVOLUTE about z（可选，独立）。
- 耦合：7 臂铰全 `Mimic(lead_screw, ±k, offset=0)`；k=`d(arm_angle)/d(screw)`；double_stage 上层 4 臂同乘子耦合同一丝杠。
- 互斥/派生：double_stage 追加 mid_block+stage-1 部件；dual_nut 追加第二螺母；folding_handle 追加 crank_handle 部件+关节。

## 每槽位 Module Emits / Interfaces

### Slot B / single_diamond
| emits | 描述 | 来源 |
|---|---|---|
| parts | base, lower_arm_0/1, end_block_0/1, upper_arm_0/1, saddle, lead_screw, threaded_nut(+_1) | origin L280-L389 |
| internal joints | 7× REVOLUTE(y) 臂铰(mimic) + 1× REVOLUTE(x) 丝杠(driver) + 1(2)× FIXED 螺母 | origin L390-L486 |
| upstream iface | base 为 root，无 upstream | — |
| downstream iface | 无（单体，不进 assembler 链）| — |

### Slot B / double_stage
| emits | 追加 mid_block + stage_1 的 4 臂 + 2 端块 | var_double_stage L321-L417 |
| internal joints | 追加 7 臂铰(mimic) 连 mid_block→saddle 段 | var_double_stage build |

### Slot E / folding_handle
| emits | crank_handle part + `_crank_handle_shape` | var_folding_crank_handle L212-L262,L450 |
| internal joints | `lead_screw_to_crank_handle` REVOLUTE about z, 独立 bounded | var_folding_crank_handle L551 |

- 活动件（臂/丝杠/折柄）均有 articulation 语义；不动细节（销头、螺纹环、齿、肋、唇、桥）为宿主 part visual。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_form | enum | {stamped_tray, wide_plate, dual_rail} | stamped_tray | choice | procedural sampler | Slot A |
| linkage_topology | enum | {single_diamond, double_stage} | single_diamond | choice | procedural sampler | Slot B |
| load_saddle | enum | {notched_yoke, flat_plate, beam} | notched_yoke | choice | procedural sampler | Slot C |
| screw_drive | enum | {single_nut, dual_nut} | single_nut | choice | procedural sampler | Slot D |
| crank_interface | enum | {crank_eye, hex_socket, folding_handle} | crank_eye | choice | procedural sampler | Slot E |
| n_stages | int(N) | {1, 2} | 1 | conditional | =2 iff linkage==double_stage 否则 1 | var_double_stage |
| arm_plate | enum(N) | {single, twin} | single | choice | twin = ±y 双板 visual（不增关节）| var_twin_plate_arms |
| arm_length_scale | float | [0.88, 1.15] | 1.0 | independent | 均匀采样后 clamp | ⑤ / origin L27-L35 |
| closed_angle_deg | float | [14.0, 22.0] | 18.0 | independent | 闭合臂仰角 β0 | ⑤ |
| base_span_scale | float | [0.90, 1.12] | 1.0 | independent | 底盘/端块半宽比例（梯形侧影）| ⑤ |
| lift_turns | float | [1.5, 2.5] | 2.0 | independent | 丝杠满升程圈数（决定 k）| ⑤ |
| (—) | constraint | — | — | inequality | `β0 + k·screw_upper ≤ β_max(≈40°)`；否则回缩 lift 上界 | clearance |
| (—) | constraint | — | — | inequality | 臂-臂近端块间隙由 sampled-pose QC 定，违反回缩 driver 上界 | clearance |
| palette | enum | {black_oxide, zinc_plated, galvanized, painted_red, gunmetal_raw} | black_oxide | choice | 每 seed 采样 | ⑥ |

连续采样契约：先采 independent（arm_length_scale, closed_angle, base_span_scale, lift_turns）→ 无 equation → 用 inequality 把 driver 升程上界投影到 β_max → conditional（n_stages 随 linkage）采样前解析。

### 7.5 编译预算 / compile budget（必填）

**每-seed ≤ 20s**。依据：源 model.py 用 cadquery 布尔冲压臂 + 49-环螺纹放样属"重布尔"档，本模板把螺纹降为
**≤12 段 Cylinder/环 visual**、臂用**单次 polyline extrude(≤2 折边)复用同一 `Mesh`（4/8 臂共享 `_arm_mesh`）**、
端块/鞍/底盘用 Box + 少量 extrude。分档 tessellation：小半径销 ≤24 段，主体英雄面 ≤48 段；N 相同臂/端块复用 mesh。
单-stage 目标 8-14s，double_stage ≤20s。超预算先降螺纹环数/折边。

## Multiplicity / Copy Logic

**轴 1 — n_stages（级数）**
- count_param `n_stages` / N_range 产品域 {1,2}（真实千斤顶极少 >2 级）；权重档 1 高频、2 稀有(~30%)
- copied object：一个 stage = (base|mid)→(4 臂+2 端块)→(mid|saddle)；`_arm_mesh`、`_end_block_mesh` 复用
- naming：`lower_arm_{s}_{side}` / `upper_arm_{s}_{side}` / `end_block_{s}_{side}`，中间体 `mid_block`
- placement：垂直堆叠共享丝杠标量耦合；stage 1 骑在 mid_block 上
- joint policy：每臂 1 bounded REVOLUTE(y) mimic 到丝杠；丝杠唯一自由驱动；无固定臂
- source/gating：var_double_stage；仅 linkage==double_stage 时 N=2

**轴 2 — arm_plate（每臂板数）**
- count_param `arm_plate` ∈ {single(1), twin(2)}；单板高频、双板 ~35%
- copied object：`_arm_mesh` 在一 part 上 ±y union 两片（不增 part/joint）
- naming：同臂 part，visual `arm_plate` 或 `arm_plate_pos`+`arm_plate_neg`
- placement：±y 对称共享销孔
- source/gating：var_twin_plate_arms `_twin_arm_shape` L114-L145

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | single_diamond（7 臂铰+丝杠+螺母）vs double_stage（+mid_block +7 臂铰 +2 端块）；均 source-backed |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：n_stages{1,2}、arm_plate{single,twin} |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE(y) 臂铰(mimic 耦合)、REVOLUTE(x) 丝杠多圈驱动、FIXED 螺母(single vs dual)、可选 REVOLUTE(z) 折柄；source-backed，sweep 内都出现 |
| ③ 主体形态家族 | 换核心 part 形态原型 | 有 | base_form{stamped_tray/wide_plate/dual_rail}、load_saddle{notched_yoke/flat_plate/beam}；每 candidate 标 form_subtype；登记进 slot_choices |
| ④ 表面装饰 | 叠表面细节 | 有(record_only) | 臂冲压折边肋/销头/螺纹环/齿脊；host-conformal 随 ③⑤ 派生（臂肋沿臂长、销头沿 y-lane），非独立 module |
| ⑤ 尺寸/行程 | 只连续改 | 有 | arm_length_scale[0.88,1.15]、closed_angle[14,22]°、base_span_scale[0.90,1.12]、lift_turns[1.5,2.5]；**丝杠 REVOLUTE(x) 包络 [0, lift_turns·2π]（升高方向），mimic 臂全程不穿模；motion_test_plan：跑 sampled QC（丝杠为唯一被采样自由关节，qc_sample_values 覆盖 closed→quarter→half→full）+ targeted `ctx.pose({screw: full})` 断言鞍座 z 升高 & lower_arm_1 尖端仍闭合回 base；折柄独立 REVOLUTE(z) [0,90°] 折出，sampled 全程清洁** |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 金属大类：black_oxide / zinc_plated(镀锌银) / galvanized / painted_red / gunmetal_raw（5 配色，全 metal/painted 大类）|

## 采样与覆盖审计

总组合数（离散）：base_form(3)×linkage(2)×saddle(3)×screw(2)×crank(3)×arm_plate(2)=216，× n_stages(派生) × palette(5) → 有效 slot-tuple 空间 >300。

理由：形态+机构主导；主多样性来自离散 ③ base/saddle 家族 + ① 拓扑 + ② 螺母/柄 + N，连续 scale 只做比例微调。

seed_domain_policy：procedural_first（seed=0 不特殊）
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 加权采样每根离散轴 + 连续 scale + palette；
n_stages 由 linkage 派生；`resolve_config` 内解 inequality（升程上界投影到 β_max）。无 curated/modulo 主表；无 regression override（除非 sweep 发现具体回归再记）。
Topology target：1000-seed slot-tuple 覆盖 report-only，预期 >200 独立 tuple。
Controlled local parameterization：arm_length_scale、closed_angle_deg、base_span_scale、lift_turns（范围见 §7）；均在 resolve_config clamp/投影，不破坏 lap MatingContract、mimic 闭环、joint origin。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权离散轴 + 连续 scale + palette；n_stages 派生 | slot_choices_for_seed == build 实选 |
| compatibility matrix | dual_nut 与任意 linkage 兼容；folding_handle 追加关节需 clear；double_stage×dual_nut / double_stage×hex(=probe) 显式纳入 | 无漂浮/穿模/轴/closed-pose/长链失败 |
| controlled local variation | 4 连续 scale + clamp + 升程投影 | 比例变而不破接口/间隙/关节/identity |
| regression overrides | none | — |
| random sweep | 0-15 fast, 0-35 final, + corner | 契约失败；axis_realization；viewer 目检 |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| base_form | 3 | yes | yes | |
| linkage_topology | 2 | yes | no | degrade reason：rhombus-closure 机构约束 |
| load_saddle | 3 | yes | yes | |
| screw_drive | 2 | yes | no | 真实千斤顶单丝杠；single/dual 螺母即 ② 全域 |
| crank_interface | 3 | yes | yes | |

## Validator

- slot_choices_for_seed 返回已实现 module 名
- config_from_seed 对所有 seed（含 0）用 deterministic procedural sampling
- compatibility：n_stages 随 linkage 派生；folding_handle 追加关节；dual_nut 追加螺母
- 无 curated/modulo 主 seed 表
- 连续 scale 在 resolve_config clamp/升程投影到 β_max，不破坏 lap MatingContract、mimic 闭环、joint origin
- 每个非-FIXED 臂铰 & 丝杠都有 MatingContract（臂铰=lap 面；丝杠螺孔=captured 过盈 element-scoped overlap）
- 关键关节 type/轴/range：臂铰 REVOLUTE(y) mimic、丝杠 REVOLUTE(x) 多圈驱动
- 复制件（臂/端块）遵循命名 & y-lane 放置

## Reject cases

- 臂角对丝杠**非线性**（异臂/不对称锚点做 mimic 拓扑）→ 闭环漂移、鞍座斜移
- 独立采样臂铰（无 mimic）→ sampled-pose QC 必然自碰撞（开链断裂）
- 丝杠 range 给到 ±12π 且臂 mimic → QC 端点使臂过度旋转翻转穿模
- 交叉臂同 y-lane → 端块/base 处臂-臂穿模
- 底盘/鞍座换带轮 trolley 或液压缸 → 越界相邻类别
- lap 面不 flush → fail_if_joint_mating_has_gap
- 螺纹环 49 段 + 布尔臂全保留 → 超编译预算

## 与相邻类别的边界

- 不该混入：液压/瓶式千斤顶（无剪式连杆+丝杠，机构完全不同）
- 不该混入：地滚/trolley 千斤顶（带轮水平底盘，长臂杠杆而非剪式丝杠）
- 不该混入：无丝杠 pantograph 升降台（缺失丝杠身份，本类别 must_keep 丝杠驱动）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 机构为 1-DOF 耦合闭环，用等臂菱形 + ±k mimic 表达 solved relation；trapezoid 降级为 ⑤ 比例，已记 degrade reason。 |

## 模板实现备注（可选）

- 共享 helper：`_arm_mesh`（4/8 臂复用）、`_end_block_mesh`、`_scissor_geometry`（解菱形返回 pivot 世界坐标+joint 原点+mimic 乘子）
- lap MatingContract：每臂铰 parent/child face 见 y-lane（lower_arm_0=+y, upper_arm_0=-y, upper_arm_1=+y, lower_arm_1=-y）
- captured overlap：丝杠 threaded_shaft 穿两端块螺孔→element-scoped allow_overlap；螺母抱丝杠→allow_overlap
- 折柄折出扫掠若与端块近→element-scoped allow_overlap
- double_stage×dual_nut、double_stage×hex_socket 对应 2 probe，显式纳入 seed domain

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | B | single_diamond | rec_picturex_..._001 | L221-L488 | 脊 part tree + 臂铰 + 丝杠驱动 + 几何常数 |
| S2 | B | double_stage | var_double_stage | L321-L417 | mid_block + stage loop |
| S3 | A | dual_rail | var_dual_rail_base | L109-L160 | 双轨底盘 |
| S4 | A | wide_plate | var_wide_plate_base | L109-L161 | 宽板底盘 |
| S5 | C | flat_plate / beam | var_flat_plate_saddle / var_beam_saddle | L151-L234 | 平板/横梁鞍 |
| S6 | D | dual_nut | var_dual_nut_screw | L174-L237 | 双螺母镜像螺纹 |
| S7 | E | hex_socket / folding_handle | var_hex_drive_socket / var_folding_crank_handle | L174-L223 / L212-L262,L551 | 六角头/折柄 part+关节 |
| S8 | N | twin_plate | var_twin_plate_arms | L114-L145 | ±y 双板臂 |
</content>
