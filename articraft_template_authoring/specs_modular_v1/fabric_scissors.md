# Modular Spec — fabric_scissors (Textiles_Fabric / Fabric scissors)

## 元信息
| 项 | 值 |
|---|---|
| slug | `fabric_scissors` |
| template path | `agent/templates/fabric_scissors.py` |
| test path (optional) | (none — acceptance is `sweep-pipeline`) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (two blade parts crossing at one pivot; the handle slot adds grip visuals onto both blade parts) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 origins + 8 forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

一把裁缝布剪 / tailor shears：两片锻钢刀身在**单个 pivot screw** 处交叉，绕该螺钉做
**单一 REVOLUTE** 开合，两条 honed 磨刃在 shear line 相剪；刀身尾端有手指握环（grip）。
手持裁缝尺度（overall ~0.15–0.32 m）。**结构极简且诚实：每一个 5 星样本都恰好是两个 part
+ 一个 pivot revolute**；刃口纹理、握环、弹簧轭都是不动的 `parent.visual(...)`（Rule 1），不是独立
part。模板忠实保留该骨架。

不该混入：花园修枝剪 / secateurs、厨房或禽类剪、理发/打薄剪、白铁剪、纸张切纸机、
电动/旋转裁布刀（有电机、无剪刀 pivot）。

## 槽位 + 候选模块表

本类别是**形态主导**类：可动骨架恒为「两臂 + 一 pivot」，主多样性来自 ③ 主体形态家族
（刃体 + 刃口）与 ② 握把拓扑。因此登记 **一个 ③ 主体形态家族 slot（承载主多样性）** 与
**一个 ② 握把拓扑 slot**。刃口（honed/pinking/scallop/serrated）与刃体（pointed/duckbill/curved）
共享同一 blade_plate part、无独立 mating 面，故按 `AUTHORING.md` §B「不能共享 mating 面的两根轴
是同一 slot 的替代 module」合并为一个 ③ slot 的 6 个具名候选（每个 = 一对 body×edge 原型）。

### Slot A：blade_form（③ 主体形态家族 / Primary Form Family，ROOT，主多样性 slot）

一个候选构建**两片刀身 part（`upper_shear`/`lower_shear`）+ pivot REVOLUTE + 两条磨刃 bevel**，
按 `(body_style, edge_style)` 决定刀体轮廓/翘曲与刃口处理。

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| pointed_honed | origin_anchor | rec_...__001 / rec_...__002 | 001 L124-L336 / 002 L45-L253 | Planar Boundary Form | eligible | 尖头直刃 + 光滑 honed bevel（两 origin 共同锚定） |
| pinking_zigzag | forked_anchor | rec_fabric_scissors_var_pinking_n9 / _n15 | pinking_n9 L70-L113,L197-L255 | Planar Boundary Form + ①multiplicity | eligible | 尖刃 + N 个 loop-emitted 三角锯齿，两刃半-pitch 交错啮合 |
| scalloping_wave | forked_anchor | rec_fabric_scissors_var_scalloping | scalloping L75-L189 | Planar Boundary Form + multiplicity | eligible | 尖刃 + N 个圆弧扇贝波（loop-emitted，两刃相位交错） |
| micro_serrated | forked_anchor | rec_fabric_scissors_var_serrated | serrated L160-L257 | Macro Surface Construction | eligible | 尖刃 + 下刃 only 细微锯齿（防滑，直线切；上刃保持光滑） |
| duckbill_paddle | forked_anchor | rec_fabric_scissors_var_duckbill | duckbill L275-L352 | Volumetric Envelope Form | eligible | 下刃换成宽阔钝圆鸭嘴 paddle；上刃保持尖头 |
| curved_trimming | forked_anchor | rec_fabric_scissors_var_curved | curved L30-L142,L171-L200 | Macro Surface Construction | eligible | 两刃沿浅弧向上翘（trimming 剪），逐-顶点 z 翘曲 |

### Slot B：handle_style（② 握把 / 骨架拓扑）

一个候选往两片已存在的刀身 part 上**加 tang + grip visuals**（parallel_children，无新 joint —
剪刀握把不 articulate；spring 轭的“回弹”是运动包络，非新关节）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| offset_asymmetric_bent | origin_anchor | rec_...__001 / rec_...__002 | 001 L186-L230,L338-L400 / 002 L173-L188 | eligible | 大 finger loop（下）+ 小 thumb loop（上），偏轴 bent，两环尺寸不等 |
| symmetric_inline_bows | forked_anchor | rec_fabric_scissors_var_symmetric_bow | symmetric_bow L103-L139,L232-L363 | eligible | 两个等大圆 bow 居于刃轴（y=0），直 tang，无偏置 crank |
| spring_squeeze_yoke | forked_anchor | rec_fabric_scissors_var_spring_snips | spring_snips L148-L189,L256-L294 | eligible | 用一条 U 型 leaf-spring 轭桥接两臂替代握环；pivot 仍是 revolute，回弹开位 rest（非负 squeeze 行程） |

硬约束核对：每个 slot 都有 ≥3 个结构不同、source-backed 的候选；无 1-候选 slot；无只换尺寸/涂装的伪候选。

## 槽位图（slot graph）

pattern: parallel_children

```
Slot A blade_form (ROOT)
  ├─ builds upper_shear (blade_plate + cutting_bevel + [edge teeth] + pivot_boss + screw hardware)
  ├─ builds lower_shear (blade_plate + cutting_bevel + [edge teeth] + pivot_boss)
  └─ emits pivot_screw: REVOLUTE(parent=upper_shear, child=lower_shear, origin=(0,0,0), axis=+z)

Slot B handle_style  --[FUSED VISUALS onto upper_shear & lower_shear, no new joint]-->
  adds handle_neck + handle_loop  (offset / inline)  或  spring_yoke + yoke_tang + yoke_rivet
```

- 跨 slot 连接点位：Slot B 的 tang/neck visual 在 pivot shoulder 区（x≈0.01–0.03）与各自刀身
  `blade_plate` 重叠（同一 part 内 support），从而把 grip 挂到刀身；无跨 slot articulation。
- 唯一 joint 是 Slot A 内部的 `pivot_screw` REVOLUTE，axis=+z，origin 在螺钉轴（=各 pivot_boss/
  screw 的对称中心线 → 过 origin-honesty 检查）。
- 上/下 part 的物理连接：parent-side `screw_shank` 贯穿两刃 bore（captured pin，element-scoped
  allow_overlap；无 MatingContract — 属 Rule 2 grandfathered captured-pin）。
- z 分层：upper part 恒在 z≳+0.001，lower part 恒在 z≲−0.001（除螺钉与 spring 轭）→ 全行程刃身互不穿模。

## 每槽位 Module Emits / Interfaces

### Slot A / blade_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_shear`, `lower_shear` | 001 L120-L121 / 002 L152,L235 |
| visuals/part | `blade_plate`(ExtrudeWithHoles mesh, 带 pivot 孔), `cutting_bevel`(Extrude mesh), `edge_tooth_i`(pinking/scallop/serrated 时 loop-emitted), `pivot_boss`(Cylinder); upper 另有 `screw_head/screw_shank/screw_slot` | 001 L135-L273 / 002 L153-L286 |
| internal joints | `pivot_screw` REVOLUTE axis=+z，limits 依 handle：loop=[-0.30,0.55]，yoke=[0,0.40] | 001 L402-L412 / spring_snips L302-L310 |
| upstream interface | ROOT，无 | — |
| downstream interface | 两刀身 part（供 Slot B 挂 grip；按已知 part 名 parallel-children） | — |

### Slot B / handle_style
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part（grip 不 articulate → 融入刀身 visual，Rule 1） | 001/002 loops 皆为 part visual |
| visuals | offset/inline: `handle_neck`(Extrude), `handle_loop`(ring-extrude); yoke: `spring_yoke`(Extrude), `yoke_tang`(Extrude), `yoke_rivet`(Cylinder) | 001 L186-L230 / symmetric_bow L232-L363 / spring_snips L148-L294 |
| internal joints | 无 | — |
| interfaces | 读上游刀身 part 名，visual 在 pivot shoulder 与刀身重叠支撑 | — |

活动件语义：仅 pivot_screw；不动细节全为 parent visual。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| blade_form | enum | 6 candidates（见 Slot A） | pointed_honed | choice | deterministic sampler | module table |
| handle_style | enum | 3 candidates（见 Slot B） | offset_asymmetric_bent | choice | deterministic sampler | module table |
| palette_theme | enum | brushed_steel_black / blued_black_brass / chrome_red / gold_ivory | brushed_steel_black | choice | ⑥ 涂装 | 001/002 材质 |
| n_edge_teeth | int | pinking [6,18] / scallop [6,12] / else 0 | 0 | conditional | 合法域随 edge_style；小 N 高频加权采样 | pinking_n9/n15, scalloping |
| size_scale | float | [0.85, 1.15] | 1.0 | independent | 均匀采样后 clamp；均匀缩放所有 xy 坐标/半径，保持全部 overlap 比例 | ⑤ 尺寸 |
| loop_scale | float | [0.85, 1.18] | 1.0 | independent | 只缩放握环 outer/inner；clamp | ⑤ 环径 |
| (—) | constraint | — | — | conditional | pivot limits = f(handle_style): yoke→[0,0.40]、其余→[-0.30,0.55]（在 resolve_config 求解） | spring_snips 行程 |

连续尺寸采样契约：先采 independent（size_scale, loop_scale）→ conditional（n_edge_teeth、pivot
limits 依上游 enum 解析）→ 均匀 xy 缩放天然满足接口/clearance，无需 inequality 回缩。

### 7.5 编译预算 / compile budget
自报 **≤ 8 s/seed**（实测 1.1–2.5 s：纯 python 挤出多边形 mesh，仅 blade 一个 pivot 孔用到布尔；
无 cadquery/OCC 重雕刻）。分档 tessellation：pivot 孔 28 段，握环 ≤44 段，齿为 ≤18 个复用同一
共享 `Mesh`。超预算先降段数再迭代。

## Multiplicity / Copy Logic

- **底座对象无重复同构件**：一把剪刀恰有两片刀身 —— base 不做 N-sweep。
- 复制数量逻辑**只出现在刃口齿行**（pinking / scalloping）：
  - `count_param`: `n_edge_teeth`
  - `N_range`: pinking `[6,18]`（样本 9/15），scalloping `[6,12]`
  - sampling domain（权重档，小 N 高频、细齿稀有）：pinking `(7,9,11,13,15,18) w=(.24,.24,.20,.14,.10,.08)`；
    scallop `(7,8,9,10,12) w=(.26,.24,.22,.16,.12)`
  - copied object / naming：`edge_tooth_i`，沿约 0.20 m 磨刃等距 loop-emit，`edge_tooth_0..{n-1}`；
    两刃 half-pitch 交错以啮合；每齿 root 嵌入 bevel strip（连接），齿不加 joint。
  - micro_serrated：固定 `SERR_COUNT=18` 细齿，**仅下刃**（上刃保持光滑），是 edge 家族的
    multiplicity 定值项。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | 恒为「两臂 + 单 pivot revolute」；spring_squeeze_yoke 用 U 轭替换握环改变握持骨架读法（forked_anchor spring_snips）。base 无同构件复制。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：刃口齿 `n_edge_teeth`（pinking [6,18]/scallop [6,12]），serrated 定值 18；base 无 N。 |
| ② 关节类型 | 换 type/轴 | 有(轴恒定) | 单一 pivot_screw REVOLUTE axis=+z 全体一致；②多样性体现在**握把拓扑**（offset↔inline↔spring 轭，source-backed）与 spring 轭的运动包络（rest 开位、非负 squeeze 行程）。 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有(主轴) | blade_form 6 候选，登记进 `slot_choices`：pointed/pinking/scallop/serrated/duckbill/curved；form_subtype ∈ {Planar Boundary, Volumetric Envelope, Macro Surface}（见 Slot A 表）。全部 source-backed。 |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | honed bevel / floral etch / 螺钉槽 / 涂层图案；均为宿主刀面派生的 host-conformal visual（bevel 随 ③ 刃体轮廓与 curved 翘曲共形，齿 root 嵌入 bevel），无独立 fork、无新 module/joint。source_type=record_only + world_knowledge_extrapolation。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | size_scale [0.85,1.15]、loop_scale [0.85,1.18]；pivot 运动包络：loop shears axis+z [-0.30,0.55]，spring 轭 [0,0.40]（rest 开位）。**motion_test_plan**：跑 `fail_if_parts_overlap_in_sampled_poses`(48) + 一条 targeted `ctx.pose` 验开合（closed/open span 分离），无需 qc_samples 覆盖默认 {0,lower,upper,mid} 已足；spring 轭 bend contact 用 element-scoped allow_overlap，非 broad exemption。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 4 主题：brushed_steel/blued/chrome/gold 刃 + black/red/ivory 塑料环 + steel/brass/chrome/gold 螺钉。材质大类：金属(steel/blued/chrome/gold) + 塑料(black/red/ivory) ≥ ceil(0.5×4)=2 覆盖。 |

收尾自检：0-9 seed 渲染里 6 个刃体家族拉得开、金属/塑料两大类都出现、bevel/齿贴合刀面不悬空、
pivot 全行程不穿模 —— 由 sweep 的 axis_realization（6 blade_form + 3 handle 全实现）+ sampled-pose
gate（pass）+ 待人工目检 batch 预览确认。

## 采样与覆盖审计

总组合数：blade_form(6) × handle(3)，其中 pinking(6 个 N) / scallop(5 个 N) 展开 edge_multiplicity
token → distinct (blade_form,edge_mult) = 1+6+5+1+1+1 = 15，× handle(3) = **45** 可达 slot-choice tuple。

理由：形态诚实词汇偏 edge-geometry-heavy + 少量刃体/握把/骨架候选，全部覆盖，落在 simple band。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 全程 deterministic 采样，seed 0 不特殊）。
Procedural Sampling / Sweep Plan：每 seed 依次 `rng.choice` blade_form、handle_style、palette，
再按 edge_style 条件加权采 n_edge_teeth，再采 size/loop scale；无 regression override；无非法组合
（所有 blade_form × handle 组合几何合法，见 compatibility matrix）。random sweep 0-35 初验，0-999
成熟度观察。
Topology target：1000-seed distinct slot tuple = **45**（saturated，= 全可达空间）；本类真实组合空间
即 45（simple 类，源锚点有限），report-only。0-35 realized distinct = 21。
Controlled local parameterization：size_scale / loop_scale（均匀 xy 缩放，clamp，不破坏 interface/
clearance/joint origin —— 因均匀缩放保持全部 overlap 比例）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 blade_form→handle→palette→n_edge_teeth(conditional)→scales | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全部 6×3 组合合法；n_edge_teeth 合法域随 edge_style 解析；pivot limits 随 handle 解析 | 无 floating/collision/axis/range 失败 |
| controlled local variation | size_scale∈[0.85,1.15], loop_scale∈[0.85,1.18]，均匀缩放 clamp | 比例变化不破坏接口/clearance/joint origin/类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-35 初验，0-999 成熟度 | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A blade_form | 6 | yes | yes | ③ 主多样性 slot |
| B handle_style | 3 | yes | yes | ② 握把拓扑 |

## Validator

- slot_choices_for_seed 返回已实现 module 名（blade_form / handle_style / edge_multiplicity）
- config_from_seed 对所有 seed（含 0）用 deterministic 采样
- compatibility：全组合合法；n_edge_teeth 与 pivot limits 在 resolve_config 依上游解析
- 无 regression override；无 curated/modulo 主 seed 表
- size/loop scale 在 resolve_config clamp，不破坏接口/clearance/joint origin/身份
- 关键关节：单一 pivot_screw REVOLUTE axis=+z；捕获销用 element-scoped allow_overlap，无 broad allowance
- 复制件 `edge_tooth_i` 命名/等距/两刃啮合；micro_serrated 仅下刃

## Reject cases

- 出现 >1 个非-FIXED joint，或 pivot 非 REVOLUTE / 轴非 +z → 非布剪骨架
- 握环/弹簧轭做成独立 FIXED part（违反 Rule 1）
- 刃口齿/bevel 悬空不嵌宿主面（part-internal island）
- 两刃身在任一开合 pose 真实穿模（非 captured-pin/yoke-bend 的 allowed 重叠）
- pivot 开合不产生 shear line 分离（open_span 未显著大于 closed_span）
- 变成修枝剪/厨房剪/理发剪/白铁剪/电动裁布刀（尺度、双刃单 pivot、握环缺失等偏离）
- 用连续 scale 或涂装冒充主多样性（主多样性必须来自 blade_form/handle 离散 slot）

## 与相邻类别的边界

- 不该混入：园艺修枝剪 / secateurs（弹簧回位 + 弯钩厚刃 + 无手指环，功能是剪枝）
- 不该混入：厨房 / 禽类剪（带开瓶/夹骨齿的重型双轴）
- 不该混入：理发 / 打薄剪（细长等长刃 + 打薄梳齿排，非裁布 offset 握把）
- 不该混入：白铁剪 / 切纸机（杠杆增力或直线导轨切割，非单 pivot 手持剪）
- 不该混入：电动 / 旋转裁布刀（有电机、旋刀，无剪刀 pivot）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | sweep-pipeline verdict=pass（pass_rate 1.0 on 0-35，corner clean，motion_test_audit pass）；6 blade_form + 3 handle + 多个 N 值全实现。待人工目检 batch 预览（0-2）确认刃体家族拉开、握把拓扑可辨、curved 翘曲与 duckbill paddle 形态忠实。 |

## 模板实现备注（可选）

- 共享 helper：`_ring_geometry`/`_oval_profile`（握环+bow）、`_plate_geometry`/`_bevel_geometry`
  （随 body_style 决定 pointed/duckbill 轮廓与 curved 逐-顶点翘曲）、`_emit_edge_teeth`
  （pinking/scallop/serrated 共用，复用同一齿 `Mesh`）。
- captured-pin：`allow_overlap(screw_shank↔blade_plate / screw_shank↔pivot_boss / pivot_boss↔pivot_boss)`；
  spring 轭另有 `allow_overlap(spring_yoke↔spring_yoke)`（bend apex 连续 U 簧）。
- z 分层是核心安全属性：upper part z≳+0.001、lower part z≲−0.001；yoke_tang 按 arm 在 z 上错开
  （±0.004）以免两 tang 在 y=0 附近同面碰撞。
- pivot 无 MatingContract（captured-pin，Rule 2 grandfathered）；origin 落在螺钉/boss 对称中心线。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | pointed_honed + offset | rec_...__001 | L124-L412 | 刃身 part 树 / honed bevel / 偏置握环 / pivot revolute |
| S2 | A/B | pointed_honed + offset | rec_...__002 | L45-L263 | 同骨架第二锚（brushed steel / 尺寸档） |
| S3 | A | pinking_zigzag | rec_fabric_scissors_var_pinking_n9/_n15 | L70-L113 | loop-emitted 三角锯齿 + N multiplicity |
| S4 | A | scalloping_wave | rec_fabric_scissors_var_scalloping | L75-L189 | 圆弧扇贝波刃口 |
| S5 | A | micro_serrated | rec_fabric_scissors_var_serrated | L160-L257 | 下刃 only 细锯齿 |
| S6 | A | duckbill_paddle | rec_fabric_scissors_var_duckbill | L275-L352 | 宽鸭嘴 paddle 下刃 |
| S7 | A | curved_trimming | rec_fabric_scissors_var_curved | L30-L200 | 逐-顶点 z 弧翘曲刃体 |
| S8 | B | symmetric_inline_bows | rec_fabric_scissors_var_symmetric_bow | L103-L363 | 居轴等大圆 bow + 直 tang |
| S9 | B | spring_squeeze_yoke | rec_fabric_scissors_var_spring_snips | L148-L294 | U leaf-spring 轭 + rivet + 回弹行程 |
