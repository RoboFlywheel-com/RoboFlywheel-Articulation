# folding_screen — Modular Spec

> 来源小类：`picture/Other/Folding screen`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Folding_screen.md`。
> **folding screen = 多扇铰接式屏风 / 房间隔断**（N hinged panels），不是折叠门、不是级联路障栅栏。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 个 parent + 8 个 fork 槽位/multiplicity 变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字**为准（`_fret_lattice` / `_shoji_grid` / `_arched_crown` / `_base_foot_shape` / `_add_panel` / `_add_barrel_hardware` / `_add_knuckle_hardware` / `panel_{i}` / `hinge_{i-1}_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_screen` |
| template path | `agent/templates/Other_Folding_screen.py` |
| test path (optional) | `tests/agent/test_folding_screen_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（参数化 panel 模块 = panel_infill × frame_detail 属性轴，**外加** `panel_count` 变长手风琴链 multiplicity 轴，核心）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 变体；均 converged、compile success、≥1 非 fixed REVOLUTE joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **parent（N=3 三扇中式屏风，`89fc1fef`）**：`center_panel`（root，居中固定）+ `wing_panel_0` / `wing_panel_1`（两 wing），两个 `wing_hinge_{i}` 竖直 REVOLUTE 各挂在 center 两侧 seam 上（**parallel_children**，star 拓扑）。每扇是 frame（bottom_rail + top_rail + 双 stile）+ 黑底 `lattice_field` + 金色 `fretwork` 浮雕。`_add_panel` 是共享的单扇发射 helper；wing 上额外发射 `_add_wing_hinge_hardware`（barrel + web + leaf），center 发射 `hinge_knuckle_{side}_{idx}_{k}` 捕获 wing barrel（piano-hinge captured-pin）。
- **panel_infill 轴（Slot A）**：fret_lattice（parent，CadQuery 金色冰裂格 mesh，浮雕于黑底）/ solid_painted_panel（`4466e1a5`，实心薄画板 box，凹入框内）/ shoji_paper_grid（`c59458fc`，`_shoji_grid` 循环 muntins + 半透明纸面 box）/ louvered_slats（`8707f11c`，`for i in range(N_SLATS)` 倾斜百叶 board 循环）。**这四者只换扇面填充子件 + 装饰材质，frame / hinge / part 树 / joint 拓扑完全一致** → infill 是单 panel 模块的填充属性轴，不改铰链拓扑。
- **frame_detail 轴（Slot B）**：flat_top（parent，平顶横档 `top_rail` box）/ arched_crown_top（`073d817a`，`_arched_crown` lathe/threePointArc mesh 替换 top_rail，峰高 1.75m）/ base_feet（`63c52429`，`_base_foot_shape` 加宽底脚 mesh 加在 bottom_rail 下）。**三者只改框的顶冠 / 底脚装饰 box/mesh，part 树 / hinge 拓扑不变** → frame_detail 也是单 panel 模块的边框属性轴。
- **panel_count 轴（Slot C 多重性，核心）**：N=2（`5e7c8b58`，`for i in range(PANEL_COUNT)`，wing 全挂 panel_0 parallel，**1 hinge**）/ N=3（parent，center + 2 wing parallel，**2 hinge**）/ N=4（`40969f37`，`for i in range(N_PANELS)` **linear_chain**，panel_i 铰接 panel_{i-1}，**3 hinge** 交替折向手风琴）/ N=6（`98759298`，同 linear_chain，**5 hinge**）。**N≥4 变体已把母资产的 star 拓扑循环化为 linear_chain**，是 multiplicity 的正确 copy-logic 源。

> **建模注记（重要）**：panel_infill 与 frame_detail 物理上**不是两个串联 slot**——它们都是同一扇 panel 模块的属性（infill 与 frame_detail 随每扇一起发射，共用同一个 `_add_panel`），无法共享 mating face。正确结构是**一个参数化 panel 模块 `panel(panel_infill, frame_detail)`，沿手风琴链复制 N 次**（variable-multiplicity chain）。下面把它们列为"模块轴"以对齐 schema 的候选表格式；它们的笛卡尔积 × N 共同构成拓扑多样性。multiplicity（panel_count）才是真正改 part 数 / joint count / chain depth 的轴。

## 核心身份

可折叠的多扇屏风 / 房间隔断（folding screen / room divider）：N 块同构装饰 panel（每块 = 木/漆框 bottom_rail + top_rail + 双 stile + 扇面填充 infill），沿 X 等距经**竖直轴 REVOLUTE 铰链**串成手风琴链，相邻 panel 交替折向（accordion zigzag）。每块 panel 满高站立于地面（z=0..~1.70m）。活动语义 = **每块 panel 绕其上游 seam 的竖直铰链水平折摆**（rest pose 为照片式 ~35° 折角，铰链行程约 ±150° from coplanar 使其可几乎对折）。默认成熟域：panel_infill × frame_detail × panel_count N∈[2,12] 的自立式装饰屏风。

铰链构造统一为 piano-hinge captured-pin：child panel 发射 `barrel` 套筒（在 seam 轴上），parent panel 发射 `knuckle` 捕获套筒（销绕共享竖直轴旋转，barrel 在轴上 → 嵌入 pose-invariant）。

不该混入：
- **级联路障栅栏（fence / cascade barrier，已有 `fence_cascade` 模板）**——那是自立 coupler 销眼级联机构、每块自带脚、平移不变直墙链；屏风是装饰扇面 + 满高 frame + 手风琴折叠，无 coupler 销眼级联，rest pose 是折角而非共线。
- **折叠门 / 折叠屏风门**——若带门框轨道 / 顶部滑轨 / 锁闭机构则出类，本类是自立无轨屏风。
- **折叠椅 / 折叠桌等折叠家具**——主运动 spine 与承重语义不同（已有各自 slug）。

## 槽位 + 候选模块表

### Slot A：panel_infill（扇面填充——被复制的单 panel 模块的填充属性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fret_lattice（基线）| rec_..._89fc1fef | `_fret_lattice` L50-92 + 装配 `_add_panel` 内 `lattice_field`/`fretwork` L134-147 | eligible if compatible | CadQuery 金色冰裂格 mesh（border ring + 三 motif cluster + connector bar，`union` 融合），浮雕于黑底 `lattice_field` box；frame/hinge 树不变 |
| solid_painted_panel | rec_variant-...-solid-painted-panel_...4466e1a5 | `_add_panel` 内 `painted_panel` box L90-95（薄板 `PAINTED_PANEL_T=0.012`）| eligible if compatible | 实心薄画板 box 凹入框内（比框薄、recessed inset board），无 mesh / 循环；frame/hinge 树不变 |
| shoji_paper_grid | rec_variant-...-shoji-paper-grid_...c59458fc | `_shoji_grid` L57-86（`for i in range(SHOJI_COLS+1)` 竖 muntin + `for i in range(SHOJI_ROWS+1)` 横 muntin）+ `shoji_paper`/`shoji_grid` 装配 L129-142 | eligible if compatible | 障子方格 wood grid mesh（规则 muntin 双循环）+ 半透明纸面 box 背衬；frame/hinge 树不变 |
| louvered_slats | rec_variant-...-louvered-slats_...8707f11c | `_louver_slat_geometry` L50-55 + slat 循环 `for i in range(N_SLATS)` L107-116（黑底 `louver_field` L98-103）| eligible if compatible | 横向百叶 board 循环（`N_SLATS=20` 倾斜 `SLAT_TILT≈35°` 等距），黑底 field 背衬；frame/hinge 树不变 |

### Slot B：frame_detail（边框 / 顶冠 / 底脚——被复制的单 panel 模块的边框属性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_top（基线）| rec_..._89fc1fef | `_add_panel` 内 `top_rail` box L119-124（`TOP_RAIL_H=0.05` 平顶横档）| eligible if compatible | 平顶横档 box，扇高峰 = PANEL_H=1.70m；frame/hinge 树不变 |
| arched_crown_top | rec_variant-...-arched-crown-top_...073d817a | `_arched_crown` L98-114（threePointArc 弧形 profile extrude）+ `crown_arch` 装配 L143-151 | eligible if compatible | 弧形顶冠 mesh 替换 top_rail（base@1.65m，peak@1.75m 高出 stile）；frame/hinge 树不变 |
| base_feet | rec_variant-...-base-feet_...63c52429 | `_base_foot_shape` L100-107（加宽 chamfered box mesh）+ `base_foot` 装配 L132-137 | eligible if compatible | bottom_rail 下加宽底脚 shoe mesh（`FOOT_W=PANEL_W+0.04`，`FOOT_H=0.045` 满铺地面）；frame/hinge 树不变 |

硬约束记录：frame_detail 仅 3 candidate（≥3 满足门槛）。flat_top 与 arched_crown_top 互斥（替换 top_rail），base_feet 是**叠加性**装饰（加底脚，可与 flat_top / arched_crown_top 任一顶冠共存）——见 §9 兼容矩阵把 frame_detail 拆为 top_style{flat, arched} × feet{none, base_feet} 的合法子集，仍以候选表三项作为采样枚举的最小集（top 二选一 + 可选底脚），保持 schema 对齐。

### 共享 helper（非 slot，所有 module 公用）

| helper | model.py:Lx-Ly（参考 N=6 `98759298`）| 用途 |
|---|---|---|
| `_add_panel` | parent L95-147 / N=4 L96-143 / N=6 L89-139 | 单扇装配（bottom_rail + top_rail/crown + 双 stile + infill），按 `(x0,x1,dz)` 发射，dz 把楼面高度移入 part 帧 |
| `_add_barrel_hardware` | N=4 L146-170 / N=6 L142-165 | child panel 在 seam 轴发射 `barrel_{idx}` + `web_{idx}` + `barrel_leaf_{idx}`（captured-pin 公销侧）|
| `_add_knuckle_hardware` | N=4 L173-190 / N=6 L167-188 | parent panel 在 seam 右侧发射 `knuckle_{idx}_{k}` + `knuckle_leaf_{idx}`（captured-pin 捕获侧）|

## 槽位图（slot graph）

pattern: mixed（参数化单 panel 模块 + 变长手风琴链 multiplicity）

```
panel_0(panel_infill, frame_detail)            ← root，居中站地，发射右侧 knuckle
   └──[hinge_0_1: REVOLUTE z, origin=ROOT_HINGE_X@panel_0, baked -FOLD_ANGLE]──> panel_1(同参数)
        └──[hinge_1_2: REVOLUTE z, origin=CHAIN_HINGE_X@panel_1, baked +FOLD_ANGLE]──> panel_2
             └── ... ──> panel_{N-1}     (i≥2 关节原点恒为 CHAIN_HINGE_X@parent，折向交替)
```

接口点位与 joint 语义：
- **接口**：parent panel 的右 seam knuckle 线（`knuckle_{idx}_{k}`，i=1 在 `ROOT_HINGE_X=0.313`@panel_0；i≥2 在 `CHAIN_HINGE_X=0.626`@parent）↔ child panel 的左 seam barrel 线（`barrel_{idx}`，建在 child part 原点 local x=0）。
- **joint type / axis**：全部 REVOLUTE、竖直 `axis=(0,0,-1)`。**origin 锚在 parent 的 seam knuckle 硬件上**（真实铰线），不是地面点——通过 baseline `fail_if_articulation_origin_far_from_geometry`（0.015）必须。i=1 时 `hinge_z=HINGE_HEIGHTS[0]=0.35`，i≥2 时 `hinge_z=0`（dz 已把 child part 帧抬到 0.35，origin 在 parent 局部帧）。竖直轴上 origin 的 z 不影响运动学。
- **rest pose / 交替折向**：`origin.rpy=(0,0,baked)`，奇 hinge `baked=-FOLD_ANGLE`（前折 -Y）、偶 hinge `baked=+FOLD_ANGLE`（后折 +Y），产生手风琴 zigzag；motion_limits 随折向取 `lower/upper`（奇：`-(RANGE+ANGLE)`..`RANGE-ANGLE`；偶：`-(RANGE-ANGLE)`..`RANGE+ANGLE`），来源 N=4 L241-250 / N=6 L228-238。
- **mating policy**：barrel 落入 knuckle 是 captured-pin，几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + 逐铰链 element-scoped `allow_overlap(barrel_{idx}↔knuckle_{idx}_{k})` 守 overlap（来源 N=4 run_tests L343-365）。
- **placement 绝对式**：root 在 X=0（居中），chain panel 几何从 `x=SEAM_GAP` 延伸（barrel 落 part 原点 local x=0），关节 origin=`ROOT_HINGE_X`(i=1) / `CHAIN_HINGE_X`(i≥2)。chain panel 几何全等（只算一份复用）。**绝对式（关节 origin 恒定、非累加）是 N-不变前提**。

> **拓扑统一注记**：母资产 N=3 是 star（两 wing 都挂 center），N=2 也是 wing-on-root parallel；但 N≥4 变体已循环化为 **linear_chain**（panel_i 挂 panel_{i-1}）。模板侧**统一采用 linear_chain**（N=4/N=6 的 `for i in range(N)` 是 copy-logic 源），N=2/N=3 退化为链的短情形（N=2 → 1 hinge，N=3 → 2 hinge），不复用 parent 的手写 star 装配。

## 每槽位 Module Emits / Interfaces

### panel 模块（panel_infill=fret_lattice / frame_detail=flat_top 为基线；其余 infill 仅换扇面子件、其余 frame_detail 仅换顶冠/底脚）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_{i}`（visuals: `bottom_rail`/`top_rail`(或 `crown_arch`)/`stile_0`/`stile_1` + infill 子件[`lattice_field`+`fretwork` / `painted_panel` / `shoji_paper`+`shoji_grid` / `louver_field`+`slat_{j}` 循环] + 可选 `base_foot` + hinge 硬件）| parent `_add_panel` L95-147 |
| internal joints | 无（单 panel 内部无活动件；infill/frame_detail/底脚/barrel/knuckle 均为同一 part 的 visual，Rule 1）| — |
| upstream interface | 左 seam barrel 线（`barrel_{idx}`，建在 child part 原点 local x=0，法向 X 分量=0，满足 chain joint 契约）| N=4 `_add_barrel_hardware` L146-170 |
| downstream interface | 右 seam knuckle 线（`knuckle_{idx}_{k}`，local x=`ROOT_HINGE_X`(root)/`CHAIN_HINGE_X`(chain)）；末扇不发 knuckle | N=4 `_add_knuckle_hardware` L173-190 |

### Slot A infill 子件（panel 模块内，按 panel_infill 切换；仅换扇面，不改 part/joint 树）
| module | emits | 来源 |
|---|---|---|
| fret_lattice | `lattice_field` 黑底 box + `fretwork` 金色 mesh（浮雕前凸）| parent L134-147 / `_fret_lattice` L50-92 |
| solid_painted_panel | `painted_panel` 实心薄 box（凹入框内）| painted L90-95 |
| shoji_paper_grid | `shoji_paper` 半透明纸 box + `shoji_grid` 木格 mesh（规则 muntin 双循环）| shoji `_shoji_grid` L57-86 / 装配 L129-142 |
| louvered_slats | `louver_field` 黑底 box + `slat_{j}` 倾斜百叶 board 循环（`for j in range(N_SLATS)`）| louvered L98-116 |

### Slot B frame_detail 子件（panel 模块内，按 frame_detail 切换；仅换顶冠/加底脚，不改 part/joint 树）
| module | emits | 来源 |
|---|---|---|
| flat_top | `top_rail` 平顶横档 box | parent L119-124 |
| arched_crown_top | `crown_arch` 弧形顶冠 mesh（替换 top_rail，峰高出 stile）| arched `_arched_crown` L98-114 / 装配 L143-151 |
| base_feet | `base_foot` 加宽底脚 shoe mesh（加在 bottom_rail 下，叠加性）| base_feet `_base_foot_shape` L100-107 / 装配 L132-137 |

### 链（panel_count multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_0..panel_{N-1}`，root 居中（shift 0），chain panel 几何从 `x=SEAM_GAP` 延伸（全等，只算一份复用）| N=4 L210-229 / N=6 L202-217 |
| joints | `hinge_{i-1}_{i}`（或变体的 `hinge_{i}`）REVOLUTE z，i=1..N-1，交替折向 baked，origin 见 slot graph | N=4 L231-265 / N=6 L219-248 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| panel_infill | enum | fret_lattice / solid_painted_panel / shoji_paper_grid / louvered_slats | fret_lattice | choice | 由 deterministic procedural sampler 选；决定扇面子件，**进 slot_choice** | module table |
| frame_top | enum | flat_top / arched_crown_top | flat_top | choice | sampler 选（替换 top_rail，互斥），**进 slot_choice** | module table |
| has_base_feet | bool | {false, true} | false | choice | sampler 选（叠加底脚，可与任一 frame_top 共存），**进 slot_choice** | module table |
| panel_count (N) | int | 声明域 **[2, 12]**；**sweep 采样域 [2, 8]**（偏小加权）| 3 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；N≥1 hinge 链 | N=4/N=6 multiplicity |
| palette_style | enum | chinese_lacquer / shoji_natural / black_lacquer_gold / ivory_painted / bamboo_louver | chinese_lacquer | palette | palette only，**不计入 slot_choice**；与 infill 弱关联（见下 conditional）| 各样本材质 |
| panel_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 PANEL_W→OPEN_W→`ROOT_HINGE_X`/`CHAIN_HINGE_X`（链 origin 随之派生，保持一致），clamp | resolve clamp |
| panel_height_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 PANEL_H→OPEN_H→OPEN_ZC→HINGE_HEIGHTS（铰高随之），clamp | resolve clamp |
| infill_density_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 shoji/louvered 有效：shoji `SHOJI_ROWS/COLS`、louvered `N_SLATS`∈[14,26]；fret/painted 无效 | resolve clamp |
| fold_rest_angle_scale | float | [0.80, 1.10] | 1.0 | independent | 缩放 FOLD_ANGLE（rest 折角）；不改 joint range 上下界拓扑 | resolve clamp |
| joint_limit_scale | float | [0.85, 1.10] | 1.0 | independent | 每 hinge `motion_limits`（基线 ±150° from coplanar）| resolve clamp |
| (—) | constraint | — | — | inequality | rest pose 折叠后相邻扇不互穿：手风琴 zigzag 在 FOLD_ANGLE·scale 下相邻 panel 不重叠（仅 barrel↔knuckle captured 重叠允许）；违反时回缩 fold_rest_angle_scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | palette_style 与 panel_infill 弱关联：shoji_natural 偏好 shoji_paper_grid、bamboo_louver 偏好 louvered_slats、black_lacquer_gold/chinese_lacquer 偏好 fret_lattice、ivory_painted 偏好 solid_painted_panel；不强制（任意组合合法），仅采样加权 | palette |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；**每个 build 解析一次，全部 panel 统一使用**（保证链上 panel 全等 → N-不变）。scale 只动安全比例 / clearance / 折角 / 细节密度，绝不改变 panel_infill / frame_top / has_base_feet / N 的拓扑。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（折扇数 = 链长）：

- **count_param**：`panel_count`（模板内变量 N_PANELS / PANEL_COUNT）。
- **N_range**：声明产品域 **[2, 12]**（屏风折扇数现实可达 6-12，sweep 友好；source map 建议 [2,12]）。`config_from_seed` 的 **sweep 采样域 [2, 8]**（偏小加权：N=2/3/4 高频、N=5-8 稀疏），以控编译时长。两者差异是有意的（见 §9 N-不变论证）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,4,5,6,7,8), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [2, 12]。
- **copied object**：整扇 panel（frame[bottom_rail + top_rail/crown + 双 stile] + infill 子件 + 可选 base_foot + barrel/knuckle 硬件），由共享 `_add_panel` + `_add_barrel_hardware` + `_add_knuckle_hardware` 发射；chain panel 几何全等，复用同一 fret/grid/foot mesh 对象。
- **naming**：`panel_{i}`，`for i in range(N)`；铰链 `hinge_{i-1}_{i}`（统一命名；变体用过 `hinge_{i}`，模板取 `hinge_{i-1}_{i}` 对齐 fence_cascade）。
- **placement**：沿 +X **绝对式**——root 居中（X=0），chain panel 几何从 `x=SEAM_GAP` 延伸（barrel 落 part 原点 local x=0），关节 origin=`ROOT_HINGE_X`(i=1) / `CHAIN_HINGE_X`(i≥2)。**绝对式（关节 origin 恒定、非累加）是 N-不变前提**。
- **joint policy**：每个铰链统一 REVOLUTE 竖直 `axis=(0,0,-1)`、交替折向（奇前偶后 baked±FOLD_ANGLE + 对应 lower/upper）、grandfather（无 mating）、barrel↔knuckle captured-pin allow_overlap。
- **source/gating**：copy-logic 源取 N=4 `40969f37` L210-265（循环链 + 交替折向 + captured allow_overlap）与 N=6 `98759298` L202-248（同构 5-hinge 链），**不取 parent / N=2**（parent N=3 是手写 star 的 center+wing；N=2 是 wing-on-root parallel，均未链式循环化）。N=2/N=3 在模板里走链的短情形（range(2)/range(3)）。

## 拓扑多样性审计

总组合数：panel_infill(4) × frame_top(2) × has_base_feet(2) × panel_count 采样数(7，即 {2,3,4,5,6,7,8}) = **112**。

理由：panel_infill(4) × frame_top(2) × has_base_feet(2) = 16 ≥ 10，**单靠这三 panel 属性轴已过门控**；叠加 **N 编入 `slot_choices_for_seed` 的 tuple**（`("panel_count", f"n{N}")`，对齐 fence_cascade/cushion）把 distinct 撑到 112。N 进 slot_choice 是硬要求——否则 N=2 与 N=8 在 slot_choice 上同形，损失整根 multiplicity 拓扑维度（且 infill×frame 也会因 N 不区分而压缩）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

**N-不变论证（为什么 sweep 只测小 N、声明域却到 12）**：
1. 几何 helper 与 i 无关，chain panel 全等；placement 绝对式（关节 origin 恒为 CHAIN_HINGE_X）；joint policy 统一（折向只依 i 的奇偶）→ 第 i 对 panel 与第 2 对**全等**（奇偶两类各全等）。
2. 故所有**逐对** QC（current-pose overlap、articulation-origin、mating-gap[grandfathered]、per-pair allow_overlap、每扇满高站地）小 N（含一奇一偶 hinge）通过即任意 N 通过。
3. rest pose 手风琴 zigzag 平移不变（相邻扇折角恒定）→ 大 N 在 rest 仍不自交（已由 §7 inequality 守相邻扇不互穿）。`fail_if_parts_overlap_in_current_pose` 是自动 baseline，每个 swept seed 都跑。
4. **不 opt-in** `fail_if_parts_overlap_in_sampled_poses`（作动多姿态 overlap 随 N 指数爆炸、成本不值）；只保 rest pose 干净 + viewer 目检。
5. 大 N 抽检：建议 sweep 外手动 compile N=12 一次，只看 current-pose + 目检，证伪"绝对式 placement 漏写成累加 / 折向奇偶漏写"这类破坏 N-不变的 bug；不进自动 sweep。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` panel_infill（4 选 1）→ `rng.choice` frame_top（2 选 1）→ `rng.random()<p` 决定 has_base_feet → `rng.choices` 加权 N∈[2,8] → palette_style 按 infill 弱加权抽 → uniform 各连续 scale。compatibility matrix 全正交（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 112 组合上限。屏风是结构收敛的小词汇类别，真实形态就是 infill(4) × 顶冠(2) × 底脚(2) × 折扇数这些等价类；低于 300 的原因是源支持的离散结构空间封顶在 112。report-only，不设门。

Controlled local parameterization：见 §参数表的 panel_width_scale / panel_height_scale / infill_density_scale（conditional@shoji,louvered）/ fold_rest_angle_scale / joint_limit_scale。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional：infill_density 仅 shoji/louvered、palette 弱关联 infill）→ 采 independent width/height/fold/limit scale → 派生（`ROOT_HINGE_X`/`CHAIN_HINGE_X` 随 width scale 等比、HINGE_HEIGHTS 随 height scale）→ 用 rest-pose inequality（相邻扇 zigzag 不互穿）投影 / 回缩 fold_rest_angle_scale。这些 scale 不破坏 hinge origin、captured-pin 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` panel_infill/frame_top + bool has_base_feet（笛卡尔积全合法），再 `rng.choices` 加权 N∈[2,8]，再 palette 弱加权 + uniform 各 scale | slot_choices_for_seed 含 `("panel_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | panel_infill × frame_top × has_base_feet 全正交合法（任一扇面配任一顶冠 / 底脚无干涉）。底脚与顶冠正交（一在底一在顶）。无互斥；排除项空。palette_style 与 infill 仅采样加权（任意组合仍合法）。 | 无 floating / collision / 出类目 / 相邻扇互穿 |
| controlled local variation | 5 个 clamped scale（width/height/infill_density@shoji&louvered/fold_rest_angle/joint_limit），每 build 统一 | 比例变化不破坏 hinge origin / captured 接口 / 满高站地 / 相邻扇 clearance / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐对 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| panel_infill | 4 | yes | yes | fret/painted/shoji/louvered |
| frame_top | 2 | yes | no | flat/arched（互斥换顶冠）；与 has_base_feet 共同构成 frame_detail，合并≥3 |
| has_base_feet | 2 | yes | no | bool 叠加底脚；与 frame_top 正交，frame_detail 候选合计 4 distinct |
| panel_count (N) | 7（采样域 {2..8}）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("panel_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [2,8]
- `resolve_config` 把 panel_count clamp 到 [2,12]，各 scale clamp 到声明范围；infill_density 为 conditional（仅 shoji/louvered 解析）；rest-pose inequality 在 resolve 内投影 / 回缩
- panel_infill × frame_top × has_base_feet 笛卡尔积全合法，无非法组合
- 连续 scale clamp 后不破坏 hinge origin / captured 接口 / 满高站地 / 相邻扇 clearance / N 复制
- 关键 joint：N−1 个 `hinge_{i-1}_{i}`，全部 REVOLUTE、竖直 `axis≈(0,0,-1)`（abs(axis[2])>0.99）、grandfather（无 mating）、交替折向 baked
- captured-pin：逐铰链 element-scoped `allow_overlap(barrel_{idx}↔knuckle_{idx}_{k})`，照搬 N=4 run_tests L343-365
- copied object 遵循 `panel_{i}` 命名 + 绝对式等距 placement + 统一交替折向 joint policy
- rest pose（手风琴 zigzag）current-pose overlap 仅 barrel↔knuckle（已 allow），相邻扇不互穿，无其它重叠

## Reject cases

- 用 parent N=3 的手写 `center_panel`/`wing_panel_{i}` star 装配作 multiplicity 源 → 无法机械读出 linear_chain copy-logic；应取 N=4/N=6 的 `for i in range(N)` 链。
- placement 写成累加（`prev + pitch`）而非绝对式（关节 origin 恒为 CHAIN_HINGE_X）→ 大 N 浮点漂移破坏 N-不变。
- 漏写折向奇偶（全部同向折）→ rest pose 非手风琴 zigzag，相邻扇互穿或单向倒。
- 给 barrel↔knuckle 补 MatingContract 硬对接 → captured-pin 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- hinge origin 放在地面或腔中心而非 parent seam knuckle 硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 把连续尺寸 / 颜色 / 材质（palette_style / *_scale）当新 candidate 塞进 infill / frame slot → 不是结构差异。
- fold_rest_angle_scale 过大致相邻扇 rest 互穿 → §7 inequality FAIL；须回缩。
- chain panel 每块重算 fret/grid mesh（不复用）→ 大 N 编译极慢。
- opt-in 大 N 的 `fail_if_parts_overlap_in_sampled_poses` → 姿态积爆炸、sweep 超时 / 作动自碰 FAIL。

## 与相邻类别的边界

- 不该混入：**fence / cascade barrier（已有 `fence_cascade` 模板）**——coupler 销眼级联 + 自立脚 + 平移不变直墙；屏风是装饰扇面 + 满高 frame + 手风琴折叠 rest 折角，无 coupler 级联机构。
- 不该混入：**折叠门 / 带轨道屏风门**——顶部滑轨 / 锁闭机构 / 门框，主运动是滑 / 升降；本类是自立无轨手风琴折叠。
- 不该混入：**折叠椅 / 折叠桌等折叠家具**——承重 + 座面 / 桌面语义不同，主运动 spine 不同（已有各自 slug）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) panel_infill / frame_detail 建模为单 panel 模块属性（非串联 slot）+ N 进 slot_choice 的方案；(2) frame_detail 拆为 frame_top{flat,arched} × has_base_feet{no,yes}（底脚为叠加性，与顶冠正交）是否接受，或保持 source map 原 3 候选枚举；(3) 模板侧统一 linear_chain（取 N=4/N=6 源）、放弃 parent star 装配；(4) N_range [2,12] 声明 / sweep [2,8] 的取舍；(5) palette_style 5 色与 infill 弱关联采样是否符合期望；(6) Topology target 112 是否接受为本小类真实结构上限）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_add_panel`（按 panel_infill / frame_top / has_base_feet 切换扇面与边框子件）、`_fret_lattice` / `_shoji_grid` / `_arched_crown` / `_base_foot_shape`（mesh，N 复制复用同一对象）、`_add_barrel_hardware` / `_add_knuckle_hardware`（captured-pin 硬件）。chain panel 几何只算一份（shift = SEAM_GAP）跨 N 个 part 复用。
- captured-pin overlap：`run_folding_screen_tests` 里 `for i in range(1, N): for idx in range(len(HINGE_HEIGHTS)): for k in range(2): ctx.allow_overlap(panel_{i}, panel_{i-1}, elem_a=f"barrel_{idx}", elem_b=f"knuckle_{idx}_{k}", ...)`，照搬 N=4 L343-365。
- 不调 `ctx.fail_if_parts_overlap_in_sampled_poses`；保留自动 baseline 的 `fail_if_parts_overlap_in_current_pose`。
- chain joint 契约：chain panel 的左 seam barrel 线必须建在 part 原点 local x=0（法向 X 分量=0），否则 origin 检查失败。
- 交替折向：奇 hinge baked=-FOLD_ANGLE + lower=-(RANGE+ANGLE)/upper=RANGE-ANGLE；偶 hinge baked=+FOLD_ANGLE + lower=-(RANGE-ANGLE)/upper=RANGE+ANGLE（来源 N=4 L241-250）。
- 参考模板：`agent/templates/Fence_Cascade_fences_MORE_THAN_1.py`（同为 mixed：参数化 panel 模块 + 变长 multiplicity 链 + `("panel_count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + captured-pin allow_overlap 骨架，本类可同构改编，差异仅 rest 折角 + 交替折向 + infill/frame 属性轴）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（parent 基线）| fret_lattice + flat_top + N=3 | rec_..._89fc1fef | `_fret_lattice` L50-92 / `_add_panel` L95-147 / `_add_wing_hinge_hardware` L150-176 / hinge 装配 L179-250 / allow_overlap L304-313 | fret 扇面 + flat 顶 + 共享 panel helper + captured-pin 范式 |
| S2 | A | solid_painted_panel | rec_variant-...-solid-painted-panel_...4466e1a5 | `painted_panel` box L90-95 | 实心画板填充 |
| S3 | A | shoji_paper_grid | rec_variant-...-shoji-paper-grid_...c59458fc | `_shoji_grid` L57-86 / 装配 L129-142 | 障子方格 mesh + 纸面（循环 muntin）|
| S4 | A | louvered_slats | rec_variant-...-louvered-slats_...8707f11c | `_louver_slat_geometry` L50-55 / slat 循环 L107-116 / 黑底 L98-103 | 横向百叶（board 循环）|
| S5 | B | arched_crown_top | rec_variant-...-arched-crown-top_...073d817a | `_arched_crown` L98-114 / `crown_arch` 装配 L143-151 | 弧形顶冠 mesh 替换 top_rail |
| S6 | B | base_feet | rec_variant-...-base-feet_...63c52429 | `_base_foot_shape` L100-107 / `base_foot` 装配 L132-137 | 加宽底脚 shoe（叠加性）|
| S7 | C（multiplicity）| panel_count N=2 | rec_variant-...-panel-count-2_...5e7c8b58 | `for i in range(PANEL_COUNT)` wing-on-root L218-251 | N=2 退化情形（1 hinge）|
| S8 | C（multiplicity）| panel_count N=4 | rec_variant-...-panel-count-4_...40969f37 | `_add_barrel_hardware` L146-170 / `_add_knuckle_hardware` L173-190 / `for i in range(N_PANELS)` 链 L210-229 / 交替折向 hinge L231-265 / allow_overlap L343-365 | **linear_chain copy-logic 主源**（交替折向 + captured allow_overlap）|
| S9 | C（multiplicity）| panel_count N=6 | rec_variant-...-panel-count-6_...98759298 | `for i in range(N_PANELS)` 链 L202-217 / 交替折向 hinge L219-248 | 5-hinge 链确证（N-不变同构）|
