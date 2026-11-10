# Fence / Cascade — Modular Spec

> 来源小类：`picture/Fence/Cascade fences (MORE THAN 1)`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Fence__Cascade_fences.md`。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自 7 个 workbench-only 五星样本，目前在 `articraft_data` 仓库。进入 SPEC_ONLY 阅读 / 实现前，需先把这 7 个 record 目录 + 物化缓存同步进本仓库 `data/records/` 并批量 `rating=5`（FORK_VARIANTS §7）。行号按本仓库同步后的 `revisions/rev_000001/model.py` 计。

## 元信息
| 项 | 值 |
|---|---|
| slug | `fence_cascade` |
| template path | `agent/templates/Fence_Cascade_fences_MORE_THAN_1.py` |
| test path (optional) | `tests/agent/test_fence_cascade_template.py`（不写，sweep 为唯一验收） |
| stage | `IMPLEMENTED`（模板已实现并注册 `TEMPLATE_REGISTRY["fence_cascade"]="fence_cascade"`） |
| status | `sweep_pass`（`sweep-pipeline` verdict=pass，50/50，见审核记录） |
| __modular__ | `True` |
| pattern | `mixed`（参数化 panel 模块 + 变长 multiplicity 链） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（2 parent + 5 fork 变体，全部 converged，workbench-only）|
| read_count | 5（parent `1b7c235f` 全文 + mesh / solid_half / flat_feet / n4 变体的改动段与装配段）|
| read_scope | 提供模块来源的样本全部读；重复格子样本（parent2 `87cb6f73`、n6 `eac791d6`）按 source map 判定为冗余，未单独读其 `model.py` |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表 |

冗余说明：
- `87cb6f73`（002.png parent）与 `1b7c235f` 同属 picket_tubular + bridge_feet 格子，source map 标为对照样本，不提供新模块。
- `eac791d6`（n6）的 copy-logic 与 `fc8fd294`（n4）的 `panel_{i}` 循环同构，N=6 不是新拓扑模块，只是 multiplicity 采样域中的一个取值。

## 核心身份

可级联的人群控制 / 路障栅栏（crowd-control / cascade barrier）：每块 panel 是一个圆角管框 + 内填充（竖 picket / 焊接网格 / 半实心板），由两只脚自立于地面；panel 的 +X 端有两个竖直 coupler **眼**（上/下），-X 端有两个竖直 coupler **销**。级联时后一块的销落入前一块的眼，形成**竖直轴 REVOLUTE** 铰链，整条栅栏由 N 块 panel 经 N−1 个这种铰链串成。默认成熟域：2–100 块 panel 的直墙链；活动语义是"每块 panel 绕其上游 coupler 线水平摆动"。

不该混入：单扇折叠屏风 / 折叠门（无 coupler 销眼级联机构、不是自立路障）、固定装饰围栏（无活动关节）、闸机 barrier gate（升降杆机构，已有 `barrier_gate_*` 模板）。

## 槽位 + 候选模块表

> **建模注记（重要）**：物理上 panel_style 与 feet_style **不是两个串联 slot**——它们都是同一块 panel 模块的属性（feet 随每块 panel 一起发射），无法共享 mating face。正确结构是**一个参数化 panel 模块 `panel(panel_style, feet_style)`，沿链复制 N 次**（variable-multiplicity chain）。下面把它们列为"模块轴"以对齐 schema 的候选表格式；它们的笛卡尔积 + N 共同构成拓扑多样性。

### Slot A：panel_style（panel 主体填充——被复制并铰接的主体）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| picket_tubular | rec_..._1b7c235f | `_infill_solid` L131-169 | eligible if compatible | 上下内轨 + `N_PICKETS` 根竖 picket 循环发射（管框基线）|
| mesh_infill | rec_..._849ff922 | `_infill_solid` L133-195 | eligible if compatible | 上下内轨 + 横 wire×Z间距 + 竖 wire×X间距 焊接网格（双循环）|
| solid_half_panel | rec_..._5333dc9b | `_lower_plate_solid` L136-176 + `_upper_pickets_solid` L178-217 | eligible if compatible | 下半实心钣金板（底轨+中轨+板）+ 上半短 picket 行（顶轨）|

### Slot B：feet_style（自立支撑脚）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bridge_feet | rec_..._1b7c235f | `_feet_solid` L209-228 | eligible if compatible | 每柱下一组 splayed A 字撑管（Y 向双腿 + X 向稳定管），管面贴地 |
| flat_feet | rec_..._862eeff1 | `_feet_solid` L210-242 | eligible if compatible | 每柱下一块矩形配重平板（`PLATE_LEN_X/Y`）+ 短竖 stub 接底轨 |


### 共享 helper（非 slot，所有 module 公用，来源 parent `1b7c235f`）

| helper | model.py:Lx-Ly | 用途 |
|---|---|---|
| `_strut` / `_tube_chain` | L67-92 | 直管 / 折线管链原语 |
| `_frame_solid` | L95-128 | 圆角管框（底轨+双柱+顶部圆角弧）|
| `_eye_solid` / `_pin_solid` | L172-206 | coupler 眼环+颈 / 销+颈 |
| `_build_panel` / `_add_panel_visuals` | L231-274 | 单 panel 装配 + 视觉挂载 |

## 槽位图（slot graph）

pattern: mixed（参数化模块 + 变长链 multiplicity）

```
panel_0(panel_style, feet_style)
   └──[hinge_0_1: REVOLUTE z, origin=seam_x@panel_0]──> panel_1(同参数)
        └──[hinge_1_2: REVOLUTE z, origin=2*seam_x@panel_1]──> panel_2
             └── ... ──> panel_{N-1}      (i≥2 的关节原点恒为 2*seam_x)
```

接口点位与 joint 语义：
- **接口**：上游 panel 的 +X coupler 线（眼，`eye_top`/`eye_bottom`，世界 x≈`seam_x`）↔ 下游 panel 的 -X coupler 线（销，`pin_top`/`pin_bottom`，建在下游 part 原点 local x=0）。
- **joint type / axis**：全部 REVOLUTE、竖直 +Z 轴。**origin 锚在 parent 的底部 coupler 眼（真实铰链硬件）上**，不是地面点——这是为通过 baseline `fail_if_articulation_origin_far_from_geometry`（绝对 0.015）必须的。实现：root panel 按绝对 z 建（脚在 z=0），origin=`(seam_x, 0, coupler_bot_z)`；linked panel 几何额外 z 平移 `-coupler_bot_z`（使其底销落在 part 原点 (0,0,0)，且 frame 原点落在 world z=coupler_bot_z，z 平移与 origin 抵消、脚仍贴地），其 origin=`(2*seam_x, 0, 0)`。竖直轴上 origin 的 z 不影响运动学。
- **mating policy**：销穿眼是 captured-pin，几何不是两个轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在眼/销几何上）+ 逐铰链 element-scoped `allow_overlap(eye↔pin)` 守 overlap。
- **rest pose**：所有 hinge=0 → 直墙共线展开（panel 沿 +X 顺序排开，相邻 panel 框不重叠，仅 coupler 眼/销重叠）。此布局平移不变 → 小 N 通过即任意 N 通过。

## 每槽位 Module Emits / Interfaces

### panel 模块（panel_style=picket_tubular 为例，其余 panel_style 仅换 infill 子件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_{i}`（visuals: `frame`/`infill`[/`infill_upper`]/`feet`/`eye_top`/`eye_bottom`/`pin_top`/`pin_bottom`）| 1b7c235f L231-274 |
| internal joints | 无（单 panel 内部无活动件；feet/眼/销/框均为同一 part 的 visual）| — |
| upstream interface | -X coupler 销线，建在 part 原点 local x=0（法向 X 分量=0，满足 chain joint 契约）| 1b7c235f `_pin_solid` L193-206 |
| downstream interface | +X coupler 眼线，local x=`seam_x`（root）/ `2*seam_x`（linked）| 1b7c235f `_eye_solid` L172-190 |

### 链（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_0..panel_{N-1}`，root shift=0、linked shift=`seam_x`（linked 几何全等，只算一次复用）| n4 L290-306 |
| joints | `hinge_{i-1}_{i}` REVOLUTE z，i=1..N-1，origin 见 slot graph | n4 L303-320 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| panel_style | enum | picket_tubular / mesh_infill / solid_half_panel | sampled | 由 procedural sampler 选 | module table |
| feet_style | enum | bridge_feet / flat_feet | sampled | 由 procedural sampler 选 | module table |
| panel_count (N) | int | 声明域 [2, 100]；**sweep 采样域 [2, 8]** | sampled | 编入 slot_choice 为 `n{N}`（拓扑维度）| n4 multiplicity |
| material_style | enum | painted_blue / galvanized / safety_orange / anthracite | sampled | palette only，**不计入 slot_choice** | palette |
| panel_len_scale | float | [0.90, 1.12] | 1.0 | 缩放 PANEL_LEN→half→`seam_x`（链 origin 随之派生，保持一致）| resolve clamp |
| panel_height_scale | float | [0.90, 1.15] | 1.0 | 缩放 PANEL_HEIGHT→FRAME_TOP_Z→coupler 高度 | resolve clamp |
| infill_density_scale | float | [0.85, 1.20] | 1.0 | picket: `N_PICKETS`∈[16,26]；mesh: 反比 spacing | resolve clamp |
| foot_spread_scale | float | [0.85, 1.15] | 1.0 | bridge: FOOT_SPREAD；flat: PLATE_LEN_Y | resolve clamp |
| joint_limit_scale | float | [0.80, 1.10] | 1.0 | 每 hinge `motion_limits`（基线 ±1.6 rad）| resolve clamp |

所有连续 scale 在 `resolve_config` 中 clamp；**每个 build 解析一次，全部 panel 统一使用**（保证链上 panel 全等 → N-不变）。scale 只动安全比例 / clearance / 细节尺寸，绝不改变 panel_style / feet_style / N 的拓扑。

## Multiplicity / Copy Logic

- **count_param**：`panel_count`（模板内变量 N_PANELS）。
- **N_range**：声明产品域 **[2, 100]**；`config_from_seed` 的 **sweep 采样域 [2, 8]**（偏小加权），以控编译时长。两者差异是有意的（见 §9 N-不变论证）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2..8), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [2, 100]。
- **copied object**：整块 panel（框 + infill + 脚 + 4 个 coupler 件）。
- **naming**：`panel_{i}`，`for i in range(N)`；铰链 `hinge_{i-1}_{i}`。
- **placement**：沿 +X **绝对式**等距——root 在 X=0，linked panel 几何 shift=`seam_x`（-X 销线落 part 原点），关节 origin=`seam_x`(i=1) / `2*seam_x`(i≥2)。**绝对式（非累加）是 N-不变的前提**。
- **joint policy**：每个铰链统一 REVOLUTE +Z、同限位、grandfather（无 mating）、eye↔pin captured-pin allow_overlap。
- **source/gating**：copy-logic 源取 n4 `fc8fd294` L290-320（循环链），**不取 parent**（parent 是手写 `barrier_panel`/`linked_panel` 的 N=2，未循环化）。

## 拓扑多样性审计

总组合数：panel_style(3) × feet_style(2) × N采样数(7，即 {2,3,4,5,6,7,8}) = **42**。

理由：panel_style × feet_style = 6 < 10，**单靠这两轴过不了**；**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("panel_count", f"n{N}")`），由它把 distinct 数撑到 42。这是本模板的硬依赖——若把 N 当普通 int 参数而不进 slot_choice，门控只见 6 个 distinct 直接 FAIL。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

**N-不变论证（为什么 sweep 只测小 N、声明域却到 100）**：
1. 几何 helper 与 i 无关，linked panel 全等；placement 绝对式（`origin=2*seam_x` 恒定）；joint policy 统一 → 第 i 对 panel 与第 1 对**全等**。
2. 故所有**逐对** QC（current-pose overlap、articulation-origin、mating-gap[grandfathered]、per-pair allow_overlap、每块 panel 自带脚的支撑）小 N 通过即任意 N 通过。
3. rest pose 共线展开、平移不变 → 大 N 直墙在 rest 仍不自交。`fail_if_parts_overlap_in_current_pose` 是自动 baseline、每个 swept seed 都跑，守住 rest-pose-clean。
4. **不 opt-in** `fail_if_parts_overlap_in_sampled_poses`（作动多姿态 overlap，姿态空间随 N 指数爆炸、成本不值），故非相邻作动碰撞不进门控；只保 rest pose 干净 + viewer 目检。
5. 大 N 抽检：建议 sweep 外手动 compile N=50 / N=100 各一次，只看 current-pose + 目检，证伪"绝对式 placement 漏写成累加 / 漏写 per-i 特例"这类破坏 N-不变的 bug；不进自动 sweep。

Topology target：1000-seed slot choice tuple distinct 预计 = 42（受真实结构词汇表上限约束，<300 合理：panel_style 3 + feet_style 2 是样本支持的全部真实形态，N 域 [2,8] 采样产生 7 个拓扑）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（panel_len / panel_height / infill_density / foot_spread / joint_limit）。全部 `resolve_config` clamp + 每 build 统一应用，不破坏 coupler 接口、链 origin 派生、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` panel_style/feet_style（笛卡尔积全合法），再 `rng.choices` 加权 N∈[2,8]，再 uniform 各 scale | slot_choices_for_seed 含 panel_count=n{N} 且与 build 一致 |
| compatibility matrix | panel_style × feet_style 全正交合法（网格板配平脚等无干涉），无互斥；排除项空 | 无 floating / collision / 出类目 |
| controlled local variation | 5 个 clamped scale，每 build 统一 | 比例变化不破坏 coupler 接口 / 链 origin / 脚贴地 / 类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐对 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| panel_style | 3 | yes | yes | |
| feet_style | 2 | yes | no | last-resort 下限；多样性由 multiplicity 补，见 §9 理由 |
| panel_count (N) | 7（采样域）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("panel_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [2,8]
- `resolve_config` 把 panel_count clamp 到 [2,100]，各 scale clamp 到声明范围
- panel_style × feet_style 笛卡尔积全合法，无非法组合
- 连续 scale clamp 后不破坏 coupler 接口 / 链 origin / 脚贴地 / N 复制
- 关键 joint：N−1 个 `hinge_{i-1}_{i}`，全部 REVOLUTE、竖直 +Z 轴、grandfather（无 mating）
- captured-pin eye↔pin 逐铰链 element-scoped `allow_overlap`
- copied object 遵循 `panel_{i}` 命名 + 绝对式等距 placement + 统一 joint policy
- rest pose（hinge=0）current-pose overlap 仅 eye↔pin（已 allow），无其它重叠

## Reject cases

- 用 parent 的手写 `barrier_panel`/`linked_panel`（N=2 未循环）作 multiplicity 源 → 无法机械读出 copy-logic。
- placement 写成累加（`prev + pitch`）而非绝对式 → 大 N 浮点漂移破坏 N-不变。
- 给 coupler 销眼补 MatingContract 硬对接 → captured-pin 几何对不上，mating-gap FAIL；应 grandfather。
- 把连续尺寸/颜色当新 candidate 塞进 slot → 不是结构差异。
- opt-in 大 N 的 `fail_if_parts_overlap_in_sampled_poses` → 姿态积爆炸、sweep 超时/作动自碰 FAIL。
- rest pose 默认设成折叠角而非共线 → 大 N current-pose 自碰 FAIL。
- linked panel 每块重算几何（不复用）→ 大 N 编译极慢。

## 与相邻类别的边界

- 不该混入：folding screen / 折叠门（无 coupler 销眼级联、非自立路障，运动是单铰折叠而非链式级联）。
- 不该混入：barrier gate 升降杆（已有 `barrier_gate_*` 模板，机构是单杆 pivot 抬升，非 N 块 panel 水平链）。
- 不该混入：固定装饰栏杆（无活动关节，违反 ≥1 非 fixed joint）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 panel_style/feet_style 建模为单 panel 模块属性 + N 进 slot_choice 的方案；确认 sweep N 上限 8 与声明域 100 的取舍）|

## 模板实现备注（可选）

- 共享 helper：`_strut`/`_tube_chain`/`_frame_solid`/`_eye_solid`/`_pin_solid` 全 module 公用；只算 root（shift 0）与 linked（shift `seam_x`）两份几何，各 tessellate 一次，`Mesh` 对象跨 N 个 part 复用（`part.visual` 仅存引用，复用安全）。
- captured-pin overlap：`run_fence_cascade_tests` 里 `for i in range(1, N): ctx.allow_overlap(panel_{i-1}, panel_{i}, elem_a="eye_top", elem_b="pin_top", ...)` + bottom 一份。
- 不调 `ctx.fail_if_parts_overlap_in_sampled_poses`；保留自动 baseline 的 `fail_if_parts_overlap_in_current_pose`。
- chain joint 契约：linked panel 的 -X 销线必须建在 part 原点 local x=0（法向 X 分量=0），否则 origin 检查失败。
- 参考模板：`agent/templates/n_joint_revolute_chain.py`（直接建 part + 循环发铰链 + 循环 allow_overlap 的骨架）、`monitor_mount.py`（变长 N 的 multiplicity-as-module-name）。
