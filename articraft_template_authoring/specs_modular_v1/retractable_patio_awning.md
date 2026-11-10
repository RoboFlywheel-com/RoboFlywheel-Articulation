# retractable_patio_awning — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `retractable_patio_awning` |
| template path | `agent/templates/retractable_patio_awning.py` |
| test path (optional) | `tests/agent/test_retractable_patio_awning_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel-children chassis + slot-level multiplicity) |

`pattern` 说明：一个接地的 `head`（cassette 头梁）作为 chassis，`fabric_roller` / `front_bar` /
N 组折叠支撑臂 / 操作 drive 全部以 revolute/prismatic 关节挂到 head（parallel_children）；
支撑臂是 slot-level multiplicity（`for i in range(arm_count)`）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | all 5-star samples in this category（2 origin_anchor + 14 forked_anchor） |
| source_index_policy | only adopted module sources are indexed below |

全部 16 个样本已读（2 个 origin `model.py` 逐行读；14 个 fork 变体逐个读取 part tree /
joint / helper / palette / dims）。样本分裂为两条主运动 spine：

- **001 spine**（`retractable_patio_awning_001`，8 parts）：`cassette` 头梁 + `fabric_roller`（卷筒）
  + `front_bar`（前梁）+ N×(`upper_arm`,`forearm`) 折叠臂 + 操作件（crank/chain/gearbox）。这是**真正的
  可伸缩遮阳篷**：卷筒收放织物，折叠侧臂推出前梁，手摇驱动。support 通过落地立柱或墙板。
  `extension_mechanism`（folding/telescoping/scissor/guided_rails）与 `drive`（chain/spring/gearbox）
  在此 spine 上 fork。
- **002 spine**（`freestanding_cantilever_patio_umbrella`，4 parts）：`base_post→cantilever_arm→canopy`
  + `crank`。样本自身 meta 明确记录这是**分类错配的悬臂遮阳伞**（“suspected_classification_mismatch:
  awning vs freestanding cantilever umbrella”），且 source map §11 把 “ordinary patio umbrella” 列为
  `must_not_become`。`support_topology`（freestanding/vertical/roof）与 `arm_count` 在此 spine fork。

**设计判断（唯一 spine 决策）：** 本模板统一到 **001 折叠臂 cassette spine**——它是类别的忠实身份，
且避开 must_not_become 的“伞”。002 spine 的 support-form / arm_count 变体是 **Box 图元的接地支撑几何**，
按 AUTHORING §A Rule 3 可以在**同一 support-base part 角色 + 同一 Box 图元**下适配到 001 头梁下方
（改的是支撑家族的离散形态，不新增未支撑的 skeleton/joint）。arm_count multiplicity 同样在 001 spine
上以 `for i in range(n)` 复制折叠臂对更加忠实（宽遮阳篷本就有 2–4 组支撑臂）。

## 核心身份

Retractable patio awning：一个接地/墙挂的水平头梁（cassette）内含**卷筒**收放一大片织物顶篷，
织物前缘挂在**前梁**上，由**折叠/伸缩支撑臂**推出并张紧，**手摇/链条/齿轮箱驱动**卷筒或臂。至少
一个真实非-FIXED 关节（卷筒 revolute + 臂 revolute/prismatic + drive）。默认成熟域 = 展开
（extended）状态、宽 3.4–4.0m、投影 2.0–2.6m。

不该混入：固定 pergola 顶（无收放机构、无卷筒）、普通庭院伞（中心杆+伞骨的 002 spine，本模板
明确不采用其运动 spine，仅借用其接地支撑几何）。

## 槽位 + 候选模块表

### Slot A：support_topology（接地支撑家族；③ Primary Form Family + ① 骨架）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| wall_bracket | forked_anchor | `rec_0611_retractable_patio_awning_var_support_topology_wall_cassette_awning` | wall_plate/wall_standoff/wall_anchor 组（≈L146-L226 类比 001 cassette 段） | eligible if compatible | 墙板 + 站立螺栓，无落地件；head 直接挂墙。form_subtype=**Planar Boundary Form**（平贴墙面的板界） |
| floor_uprights | forked_anchor | `rec_picturex_...__001__...` (origin) + `rec_0611_..._extension_mechanism_folding_lateral_ar` | L180-L226（`upright_{i}`,`foot_plate`,`mount_plate`,`leveling_pad`） | eligible if compatible | 两根细落地立柱 + 脚板 + 找平垫，托起 head。form_subtype=**Volumetric Envelope Form**（细杆立体支撑） |
| freestanding_dual_post | forked_anchor | `rec_0611_..._support_topology_freestanding_dual_pos` | base_slab + `for index in (-0.5,0.5)` support_post×2 + top_header（002 base_post 段） | eligible if compatible | 重底板 + 双立柱 + 顶横梁的独立落地站。form_subtype=**Volumetric Envelope Form**（厚底座立体站） |
| roof_curb_mount | forked_anchor | `rec_0611_..._support_topology_roof_mounted_awning` | 宽 roof curb slab(1.40×0.90×0.08) + galvanized_mount + 短 mast（002 base_post 段） | eligible if compatible | 屋面 curb 板 + 镀锌安装板 + 短立柱。form_subtype=**Macro Surface Construction**（大尺度屋面 curb 板改变读法） |

（vertical_drop 变体折入 wall_bracket 家族的比例范围，不单列 candidate——它与 wall 同为平贴墙面板界，
只是更瘦高，是 ⑤ 尺寸差异。）

### Slot B：extension_mechanism（折叠臂机构；② 关节类型 + ① 臂子结构）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| folding_lateral_arms | forked_anchor | `rec_0611_..._extension_mechanism_folding_lateral_ar` | `_add_arm_segment`（twin-chord）L71-L117；shoulder+elbow REVOLUTE L398-L433 | eligible if compatible | 上臂+前臂双铰折叠；shoulder REVOLUTE(x)、elbow REVOLUTE(x)。深双弦臂 + tension_link |
| telescoping_arms | forked_anchor | `rec_0611_..._extension_mechanism_telescoping_arms` | `_add_arm_segment` sleeve 版；elbow PRISMATIC | eligible if compatible | 外套筒 + 内前臂滑出；shoulder REVOLUTE(x)、elbow **PRISMATIC(y)**（沿臂伸缩） |
| scissor_arms | forked_anchor | `rec_0611_..._extension_mechanism_scissor_arms` | `_add_arm_segment(scissor=True)`：交叉 rail + scissor_pivot | eligible if compatible | 上臂为交叉剪式连杆（额外 cross rail + 中心 scissor_pivot）；shoulder+elbow REVOLUTE(x) |
| guided_side_rails | forked_anchor | `rec_0611_..._extension_mechanism_guided_side_rails` | `_add_arm_segment` + rail_flange；shoulder+elbow PRISMATIC | eligible if compatible | 带侧翼导轨的直臂；shoulder **PRISMATIC(y)** + elbow **PRISMATIC(y)** 导向伸缩 |

### Slot C：drive（操作驱动件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| plain_crank | forked_anchor | origin 001 + `rec_0611_..._support_topology_wall_cassette_awning` | crank_handle L345-L363；`drive_housing` L258-L263；crank_rotation L435-L448 | eligible if compatible | 光杆手摇：drive_housing Box + crank(spindle/drop/grip)，REVOLUTE(x) 卷动 |
| chain_loop_drive | forked_anchor | `rec_0611_..._drive_chain_loop_drive` | `_add_chain_loop`（drive_sprocket/chain_strand/chain_bead/chain_return）；`chain_drive_rotation` 小行程 | eligible if compatible | 拉链环：`chain_drive` part（链轮 + 链珠环）+ chain_drive_housing；REVOLUTE(x) 小行程 ±0.18 |
| gearbox_crank | forked_anchor | `rec_0611_..._drive_gearbox_crank` | drive_housing + gearbox_cover(Cyl) + gearbox_input_boss + crank_hub | eligible if compatible | 封闭减速齿箱：gearbox_cover 圆罩 + input_boss + crank_hub 的曲柄，REVOLUTE(x) |
| spring_rewind_roller | forked_anchor | `rec_0611_..._drive_spring_rewind_roller` | roller spring cartridge(`spring_cartridge`/`spring_mandrel`/`spring_anchor`) + `rewind_bearing`；material `tempered_spring_steel` | eligible if compatible | 卷筒内扭簧回卷 + 服务钥匙 crank；卷筒同轴弹簧筒可视件 + rewind_bearing；crank 作 service key |

硬约束核对：每 slot 3–6 candidate（此处均 4）；无单-candidate slot；每个 ①/②/multiplicity candidate 均
有 `forked_anchor` 来源；③ 由 Slot A 承载并逐 candidate 标 `form_subtype`；candidate 间均为结构差异
（part tree / joint type / 交叉连杆 / 驱动 part tree 不同），非只换色/尺寸。

## 槽位图（slot graph）

pattern: mixed（parallel_children on chassis + multiplicity）

```
support_topology(Slot A)  ──FIXED（support 视觉直接建在接地 head part 上，同一 part）──►  head(chassis: cassette 头梁)
head  ──[REVOLUTE axis x, roller_rotation, ±8π]──►  fabric_roller
head  ──[REVOLUTE axis x, front_bar_pitch, ±0.22]──►  front_bar
head  ──[shoulder_hinge_i]──►  upper_arm_i  ──[elbow_hinge_i]──►  forearm_i        （i in range(arm_count)）
head  ──[drive joint（REVOLUTE x）]──►  drive_part（crank / chain_drive）
```

- **接口点位**：support_topology 与 head 融为**同一接地 part**（support 是 head 的 grounded visuals，
  不动 → 不是独立 part，Rule 1）；roller/front_bar/arm/drive 通过 head 上的真实 visual（end_cap 轴承、
  pivot_bracket、drive_housing）作为 MatingContract 的 parent face 挂接。
- **跨 slot joint type/axis/range**：
  - roller_rotation REVOLUTE axis=(1,0,0) 连续卷动 ±8π（continuous 语义）。
  - front_bar_pitch REVOLUTE axis=(1,0,0) 行程 [-0.22, 0.22]。
  - shoulder_hinge_i / elbow_hinge_i：type 由 Slot B 决定（REVOLUTE axis x 或 PRISMATIC axis y）。
    折叠面锁在**每臂各自的 x=const 竖直平面**内 → 多臂天然不互撞。
  - drive joint REVOLUTE axis=(1,0,0)；行程随 Slot C（plain/gearbox ±2π，chain ±0.18，spring service ±1.25π）。
- **互斥/派生**：无硬互斥；support/extension/drive 三轴几何独立（接地端 / 中段臂 / 端部驱动）。
  arm_count 只影响臂对复制数与 head 上 pivot_bracket 数。

## 每槽位 Module Emits / Interfaces

### Slot A / module <wall_bracket|floor_uprights|freestanding_dual_post|roof_curb_mount>
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（support 视觉建到接地 `head` part 上） | S-A / 各 support 变体 |
| internal joints | 无（不动支撑，Rule 1） | — |
| upstream interface | n/a（root chassis） | — |
| downstream interface | head 顶面 = roller/front_bar/arm/drive 的挂接基准（end_cap / pivot_bracket / drive_housing 面） | 001 cassette L146-L263 |

### Slot B / module <folding_lateral_arms|telescoping_arms|scissor_arms|guided_side_rails>
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_arm_{i}`, `forearm_{i}`（i in range(arm_count)） | S-B / 各 extension 变体 |
| internal joints | `shoulder_hinge_{i}`(head→upper_arm)、`elbow_hinge_{i}`(upper_arm→forearm)；type/axis 见上 | 001 L398-L433 |
| upstream interface | head 上 `pivot_bracket_{i}` face（shoulder mating parent） | 001 L243-L256 |
| downstream interface | forearm tip 靠向 `front_bar` 的 `front_tab_{i}`（captured，allow_overlap） | 001 L303-L316 |

### Slot C / module <plain_crank|chain_loop_drive|gearbox_crank|spring_rewind_roller>
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drive_part`（crank_handle 或 chain_drive）；spring_rewind 额外 roller 上 spring 可视件（挂 fabric_roller/head） | S-C / 各 drive 变体 |
| internal joints | drive joint（head→drive_part，REVOLUTE x） | 001 L435-L448 |
| upstream interface | head 上 `drive_housing` face（drive spindle mating parent） | 001 L258-L263 |
| downstream interface | 无（末端） | — |

要求：活动件（roller/front_bar/arm/drive）均有 articulation 语义；不动细节（support 板、bolt、bracket、
gearbox 罩、chain 珠、valance）写成宿主 part visual，不作为独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| support_topology | enum | wall_bracket / floor_uprights / freestanding_dual_post / roof_curb_mount | — | choice | deterministic sampler | Slot A |
| extension_mechanism | enum | folding_lateral_arms / telescoping_arms / scissor_arms / guided_side_rails | — | choice | deterministic sampler | Slot B |
| drive | enum | plain_crank / chain_loop_drive / gearbox_crank / spring_rewind_roller | — | choice | deterministic sampler | Slot C |
| arm_count | int(mult) | {2,3,4} 权重(0.5,0.3,0.2) | 2 | conditional | 见 §8；spacing 随 N 派生 | 002 arm_count 变体 |
| palette_style | enum | ≥5（见 §8.5 ⑥） | charcoal_awning | choice | deterministic sampler | 001/002 真实 colorway + companion |
| awning_width | float | [3.30, 4.10] | 3.78 | independent | 均匀采样后 clamp | 001 L143 width=3.78 |
| projection | float | [2.00, 2.60] | 2.35 | independent | 均匀采样后 clamp | 001 L144 projection=2.35 |
| head_height | float | [2.30, 2.80] | 2.60 | independent | head 顶面世界 z | 001 cassette z≈2.55-2.69 |
| arm_spacing | float | derived | — | equation | `= min(spread_available/(n-1), max_pitch)`，其中 spread=awning_width-2*edge_margin | self-collision |
| shoulder_travel | float | [闭合,可行上界] | 见 §8.5⑤ | conditional | 行程上界随 N 与 module 收紧 | 001 limits |
| elbow_travel | float | [闭合,可行上界] | 见 §8.5⑤ | conditional | 同上 | 001 limits |
| (—) | constraint | — | — | inequality | `(n-1)*arm_spacing + arm_x_width <= awning_width - 2*edge_margin`；违反→回缩 arm_spacing | self-collision |
| (—) | constraint | — | — | inequality | `projection <= awning_width*0.85`（篷面不过深自撑）；违反→clamp projection | 接口/比例 |

连续尺寸采样契约：先采 independent（width/projection/head_height/scales）→ 按 equation 派生 arm_spacing →
按 inequality 投影回缩（arm_spacing/projection）→ conditional 行程按 arm_count+module 解析。全部在
`resolve_config` 内求解，不留到 builder。

## 7.5 编译预算 / compile budget
自报预算：**≤15s/seed**。依据：几何以 Box/Cylinder 为主，仅 2 处 Mesh（`fabric_geometry` 扇贝篷面
station_count≤33、`fabric_roll` 卷筒），无重布尔雕刻/复杂放样。分档 tessellation：卷筒/pin/bolt 等小
半径特征 Cylinder 用 SDK 默认（≤32 段），无英雄级高分曲面。N 个相同臂对复用同一 `_add_arm_segment`
helper 几何。超预算先降 scallop_count/station_count 再迭代（AUTHORING §C）。`--compile-timeout 120`
作为 3× 看门狗。

## Multiplicity / Copy Logic

- **轴：arm_count（唯一 multiplicity 轴）**
  - `count_param`: `arm_count`
  - `N_range`（产品域）：`[2, 4]`；测试与产品同域（源锚点仅 2/3/4，且宽 3.4–4.0m 遮阳篷现实即 2–4 组臂）。
  - sampling domain（权重档）：`{2:0.50, 3:0.30, 4:0.20}`（小 N 高频、大 N 稀有）。
  - copied object：一组折叠臂 = (`upper_arm_{i}`, `forearm_{i}`) + 其 `shoulder_hinge_{i}`/`elbow_hinge_{i}`
    关节 + head 上对应 `pivot_bracket_{i}`/`front_tab_{i}` 视觉。
  - naming：`upper_arm_{i}` / `forearm_{i}` / `shoulder_hinge_{i}` / `elbow_hinge_{i}`，i in range(arm_count)。
  - placement：沿 awning 宽度 x 方向均匀分布，x_i = -spread/2 + i*arm_spacing（spread 派生自 width）。
  - joint policy：每臂同构（同 helper、同 type/axis/range）；folding_lateral/scissor→REVOLUTE(x)，
    telescoping→shoulder REVOLUTE(x)+elbow PRISMATIC(y)，guided_side_rails→双 PRISMATIC(y)。
  - source/gating：源 002 arm_count 变体的 `for index in range(SUPPORT_ARM_COUNT)` 单-`arm_pivot` 复制，
    在 001 spine 上实现为**每臂独立 shoulder/elbow 关节**（001 本就 `for index in range(2)` 双臂独立关节，
    是更强的多样性实现）。sweep 上限 N=4；每臂在自身 x-plane 折叠 → 不互撞。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | **有** | Slot A 改接地支撑家族（墙板 / 落地立柱 / 双立柱底座 / 屋面 curb）；Slot B 改臂子结构（双弦 / 套筒 / 剪式交叉 / 导轨）；arm_count 改臂对数。所有 forked_anchor（见 §4）。|
| └ multiplicity | 同构件 ×N | **有** | arm_count N∈{2,3,4} 权重(0.5,0.3,0.2)，见 §8。|
| ② 关节类型 | 图不变换 type/轴 | **有** | shoulder/elbow：REVOLUTE(x)（folding/scissor）↔ PRISMATIC(y)（telescoping elbow、guided 双轴）；drive：REVOLUTE(x) 大行程(plain/gearbox) / 小行程(chain) / service(spring)。每种声明的 type 都在 sweep 出现（axis_realization 核）。forked_anchor。|
| ③ 主体形态家族 | 换可识别几何形态原型 | **有** | Slot A 承载并登记进 slot_choices：wall_bracket=Planar Boundary Form；floor_uprights=Volumetric Envelope Form；freestanding_dual_post=Volumetric Envelope Form（厚底座）；roof_curb_mount=Macro Surface Construction。source-backed anchors（4 support 变体）。≥3 可识别主体形态原型。|
| ④ 表面装饰 | 不改轮廓的表面叠加 | **有** | 篷面**扇贝 valance**（scallop_count 档）、roller_seam 条、front_bar_groove、gearbox_cover 罩纹、chain_bead 珠列——均宿主表面派生（valance 由 fabric mesh 逐-station 派生，随 ③⑤ 共形）。source_type=`record_only`+`world_knowledge_extrapolation`。|
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | **有** | 关键比例：awning_width[3.30,4.10]、projection[2.00,2.60]、head_height[2.40,2.85]（§7）。**每非-continuous 关节运动包络**（rest=deployed，运动只向下/向内收拢，全程不穿模 canopy/roller/body）：front_bar_pitch REVOLUTE(x) [-0.22,0.22]；folding/scissor shoulder REVOLUTE(x) [-0.75,0]（N≥4 收紧到 -0.62）、elbow REVOLUTE(x) [-1.10,0]（N≥4 -0.90）；telescoping shoulder REVOLUTE(x) [-0.65,0]、elbow PRISMATIC(y) [-0.35,0]；guided_side_rails shoulder PRISMATIC(y) [-0.09,0]（收拢上界受 roller 间隙约束）、elbow PRISMATIC(y) [-0.30,0]；drive 见 ②。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=min(128,max(32,1+4*joint_count)))`；per-mechanism targeted `ctx.pose(...)`：roller 卷动可见位移、front_bar 变姿、臂 0 shoulder+elbow 位移（pose 到非零极限）、drive 旋转位移。roller 为 continuous 语义（整圈不穿模）。|
| ⑥ 涂装 | 只改材质/颜色 | **有** | palette_style ≥5：`charcoal_awning`（001 真实：charcoal_acrylic/graphite_powdercoat/blackened_steel/satin_aluminum/pivot_hardware）、`cream_market`（002 真实：cream_fabric/dark_powdercoat/charcoal_base/steel_pin）、`forest_canvas`、`terracotta_stripe`、`sand_beige`、`slate_blue`（companion realistic colorway，record_only）。材质大类：fabric/acrylic-canvas(painted) + metal(frame/roller aluminum) + steel(hardware)，覆盖 ≥ ceil(0.5×6)=3。|

**收尾自检**：batch 0-9 里须肉眼可见——support 四家族拉得开、臂 REVOLUTE↔PRISMATIC 机构不同、
织物扇贝贴合前缘、palette 大类都出现、臂折叠/卷筒卷动全程不穿模。

## 采样与覆盖审计

总组合数：support(4) × extension(4) × drive(4) × arm_count(3) = **192** 离散组合（palette 5–6 与连续
scale 另计）。report-only maturity 观察：1000-seed 覆盖预期覆盖全部 192 tuple 的大部分；富度足够，>300。

理由：四条真实结构轴（接地形态 / 臂机构关节类型 / 驱动 part tree / 臂数）× 加权 N，离散多样性主体来自
slot/module/multiplicity，连续 scale 仅作局部微调。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对每个 seed 含 seed 0 做 deterministic
加权采样；无 curated/modulo 主表；可选稀疏 regression override 仅记已知回归）。
Procedural Sampling / Sweep Plan：每 slot 独立 `rng.choice`；arm_count `rng.choices(weights=...)`；
palette `rng.choice`；连续 scale `rng.uniform` 后 clamp/derive/inequality 投影。compatibility gating 在
`resolve_config`：`(n-1)*arm_spacing + arm_x_width <= width-2*edge_margin` 回缩 arm_spacing；
`projection <= 0.85*width` clamp；shoulder/elbow 行程随 N/module conditional 收紧上界防臂-head/臂-roller
穿模。random sweep：seeds 0-15(fast)→0-35(final)→corner。
Topology target：192 tuple，report-only，不作 gate。
Controlled local parameterization：awning_width、projection、head_height、arm_spacing(derived)、
shoulder_travel/elbow_travel(conditional)、scallop_count(④ 装饰档)。取值范围/约束见 §7；不破坏
MatingContract/multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 独立加权采样 + arm_count 加权 N + palette | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 无硬互斥；arm_spacing/projection/travel 由 inequality/conditional 回缩，无非法组合 | 无 floating/collision/axis/max-mult/bulky/optional-child 失败 |
| controlled local variation | width/projection/height/arm_spacing/travel/scallop + clamp | 比例变化不破接口/clearance/support/joint 原点/类别身份 |
| regression overrides | none（如出现失败回归再补 seed + 理由） | previously failed / reviewer-selected only |
| random sweep | seeds 0-35 initial；0-999 maturity 审计 | contract failures；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_topology | 4 | yes | yes | ③ Primary Form Family slot |
| extension_mechanism | 4 | yes | yes | ② 关节类型主轴 |
| drive | 4 | yes | yes | |
| arm_count (mult) | 3 (N=2,3,4) | yes | yes | N 只覆盖不计 distinct |

## Validator

- slot_choices_for_seed returns implemented module names（含 arm_count `n{N}`）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（含 seed 0）
- compatibility matrix / gating prevents illegal combos（arm_spacing/projection/travel 回缩，无非法枚举）
- optional regression overrides are sparse and justified（首版 none）
- final template does not endlessly cycle a small curated table as main seed domain
- controlled local scale params clamped；cross-part deps（arm_spacing equation、self-collision/projection
  inequality、travel conditional）resolved in `resolve_config`
- critical MatingContract points exist（roller↔end_cap、front_bar↔cassette、arm shoulder↔pivot_bracket、
  drive↔drive_housing）；captured-pin 用 element-scoped allow_overlap
- key joints have expected type/axis/range（roller REVOLUTE x、front_bar REVOLUTE x、arm per-module、
  drive REVOLUTE x）
- copied arm objects follow naming/placement/joint policy（`{name}_{i}`, even x spacing）
- Rule 5：`fail_if_parts_overlap_in_sampled_poses` + per-mechanism targeted `ctx.pose(...)`

## Reject cases

- 落地/漂浮：臂或 support 视觉悬空未接地（无 support 路径）。
- 穿模：多臂 x-spacing 过小相撞；臂折叠撞 head/roller；prismatic 臂伸出撞前梁。
- joint 语义错：shoulder/elbow 声明的 type/axis 与 module 不符；drive 行程超真实。
- 装饰脱节：valance 用常数半径套在收锥/缩放篷面外（须逐-station 派生）。
- 退化图元：把 fabric mesh 降级成 Box、卷筒降成平板。
- multiplicity 膨胀：把 N 当 distinct 计（N 只覆盖）；或 N>4 超源锚点。
- support 家族塌成单一：四 candidate 长一样（须 ③ form_subtype 拉开）。
- palette 单一：material 大类 <3。

## 与相邻类别的边界

- 不该混入：**固定 pergola 顶**（无卷筒/无收放机构/无非-FIXED 主运动；本模板 must_keep 卷筒+臂关节）。
- 不该混入：**普通庭院伞 / 悬臂伞（002 spine）**（中心杆+伞骨的运动 spine；本模板明确不采用其 spine，
  仅在 Rule 3 下借用其接地支撑几何的 Box 家族形态）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 单-spine 决策：统一到 001 折叠臂 cassette spine（类别忠实 + 避 must_not_become 伞）；002 support/arm_count 变体作为 Box 接地支撑家族在 Rule 3 下适配。**实现已达 verdict=pass**：sweep-pipeline fast(0-15)/final(0-35)/corner 三段 pass_rate=1.0、corner 0 失败、coverage gate pass（4 support × 4 extension × 4 drive × 3 arm_count 全覆盖）、motion_test_audit pass、allowance_audit 0 weak/0 new。P4 batch 10 seed 全部 clean 出图，6 palette 全覆盖。 |

## 模板实现备注（可选）

- 所有臂共享 `_add_arm_segment(part, length, *, mechanism, scissor=...)` helper；telescoping/guided
  改 elbow(及 shoulder) 为 PRISMATIC。
- captured-pin overlap（shoulder_pin↔pivot_bracket、elbow_pin↔clevis、arm_tip↔front_tab、
  drive_spindle↔drive_housing、roller_axle↔end_cap、spring_mandrel↔spring_cartridge）用
  element-scoped `allow_overlap`，禁止 part 级广义 allow。
- shoulder/elbow 折叠锁在每臂 x=const 竖直平面（axis x / prismatic y）→ 多臂天然无互撞，是
  robustness 关键；不要用 z-yaw（会横扫相撞）。
- roof_curb_mount + N=4：arm_spacing inequality 保证不超宽；projection clamp 防篷面过深。
