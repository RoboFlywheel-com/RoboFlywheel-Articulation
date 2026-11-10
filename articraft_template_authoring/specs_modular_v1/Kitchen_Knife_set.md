# knife_set (kitchen knife block set) — Modular Spec

> 来源小类：`picture/Kitchen/Knife set`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Knife_set.md`。
> **"knife_set" 在此 = 厨房刀座套装（kitchen knife BLOCK set，一只持刀 block / holder + N 把刀 + 一把厨剪），不是单把厨刀、不是折叠 / 伸缩美工刀、不是通用工具 / 餐具收纳筒。**
> 结构家族 = 一只持刀 `knife_block` root（block_shell + 四个 `foot_{i}` 或独立 base 支撑 + `logo_seal`/`logo_text` 装饰），持有 **N 把刀，每把刀是一个独立 PRISMATIC 滑出件**（`knife_{i}` + `knife_{i}_slide`），外加一把两段式厨剪：`shears_inner_half` / `shears_outer_half`，沿 `shears_slide` PRISMATIC 滑出 + `shears_pivot` REVOLUTE 在中央铆钉处张开。block 形态、持刀机构、base/stand 是三个独立结构槽；**刀数 knife_count 是多重性主轴**。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 parent + 7 fork 槽位 / multiplicity 变体）已同步进 `articraft_data/data/records/`，rating=5（按上游 curation）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（逐一核对、**8/8 全文读完**）。引用以 part / joint / helper **名字** 为准（`knife_block`/`block_shell`/`holder_shell`/`housing_shell`、`foot_{i}`、`logo_seal`/`logo_text`/`logo_panel`、`knife_{i}`/`knife_{i}_steel`/`knife_{i}_grip`/`knife_{i}_rivet_{j}`/`knife_{i}_slide`、`_knife_steel`/`_knife_grip`/`_knife_rivet_x`/`_grip_loft`、`_build_block_solid`/`_build_holder_solid`/`_build_housing`/`_tilted_box`/`_make_slot_cutter`、`bristle_{i}`/`FIXED_KNIVES`/`chef_slide`、`pedestal`/`pedestal_column`/`base_pad_{i}`/`pedestal_to_block`、`cast_metal_stand`/`stand_frame`/`stand_front_lip`/`stand_to_block`、`shears_inner_half`/`shears_outer_half`/`shears_slide`/`shears_pivot`/`shears_pivot_rivet` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `knife_set` |
| template path | `agent/templates/Kitchen_Knife_set.py` |
| test path (optional) | `tests/agent/test_knife_set_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity`（主轴 = `knife_count` 刀数 N 复制；外加固定 named slots: block_form + holding_mechanism + base_stand 在 root 上 parallel children；effectively mixed，但唯一可变 count 轴是 knife_count → 归 `multiplicity`，对齐 tool_cart）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 变体：2 block_form 槽位 + 1 holding_mechanism 槽位 + 2 base_stand 槽位 + 2 knife_count N 样本；均 converged，compile success、含 N×PRISMATIC + shears PRISMATIC + shears REVOLUTE 非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests 的 allow_isolated_part / allow_overlap / expect_* 段）|
| read_scope | all 5-star samples in this category（parent 母资产 001.png 覆盖 slanted_block × angled_prismatic_slots × rubber_feet × N=6 基线；变体为 fork 子，单轴变化；count_4/count_8 是 multiplicity 对）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本（注：单刀类 `rec_knife_var_*` / `rec_retractable_utility_knife_*` 是相邻小类「single knife」的样本，**不属于本 source map，未读、未采纳**）|

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **8 个样本共享同一拓扑骨架**：root `knife_block`（block_shell + 四 `foot_{i}`(或独立 base) + `logo_seal`/`logo_text`）+ N 个 `knife_{i}` PRISMATIC 刀 + 两段式厨剪（`shears_inner_half` PRISMATIC `shears_slide` + `shears_outer_half` REVOLUTE `shears_pivot`）。非 fixed joint 计数 = N(刀) + 2(剪) → 跨样本 6..10，**永不为 0**。**刀数是身份的主多重性轴**；shears 的 slide+pivot 是每个样本都保留的第二个非 fixed-joint 锚。
- **刀拷贝逻辑（multiplicity 主轴，3 个 N 样本逐一核对）**：count_4（`NUM_KNIVES=4`、`KNIFE_SPECS` list L56-65、loop `for i in range(NUM_KNIVES)` L305 调 `_build_knife_part` L219-257）/ parent（6：**手写 `KNIVES` dict** L53-66、`for kname, spec in KNIVES.items()` L265）/ count_8（`N_KNIVES=8`、`KNIFE_SPECS` list L57-76、`BLOCK_WIDTH=0.175` 加宽 L41、loop `for i in range(N_KNIVES)` L316 调 `_build_knife` L188-226）。每刀 = `knife_{i}` part（`knife_{i}_steel` 锥形刀身+bolster `_knife_steel` L143-154 / `knife_{i}_grip` lofted walnut 把 `_knife_grip` L157-165 / 两个 `knife_{i}_rivet_{j}` Cylinder）+ `knife_{i}_slide` PRISMATIC axis=(0,0,1)（joint rpy 把局部 +Z 转到抽出方向）`MotionLimits(effort=20, velocity=0.5, lower=0, upper=spec["travel"]≈0.10-0.18)`。**count_4/count_8 是 copy-logic 源**（`for i in range(N)` + `knife_{i}` + 共享 `_knife_steel`/`_knife_grip` helper + 统一 PRISMATIC policy）；parent / base_metal_stand 用 dict 形（hand-named），**模板必须重构成 index loop**（见顶部注记 / §8）。
- **Slot A block_form**（block 形态 / 轮廓 + slot 轴）：
  - **slanted_block**（parent 基线）：后仰 12° 橡木 block（`_build_block_solid` L101-129 用 XZ wedge 外形 + `_tilted_box` L90-98 切角度 slot），刀沿 block 轴向角度 slot 抽出；`knife_{i}_slide` PRISMATIC axis=(0,0,1) `rpy=(0,-TILT,0)`(12°)；前 pocket 藏厨剪。
  - **upright_block**（block_upright 变体）：竖直 axis-aligned `box(BLOCK_D,BLOCK_W,BLOCK_H)`（`_build_block_solid` L69-101），垂直 slot 直抽；`knife_{i}_slide` PRISMATIC axis=(0,0,1) **无 tilt**；shears 从前面横向 slot 滑出（`shears_slide` axis=(1,0,0)，剪 mesh `_shears_steel_h` 旋 90° L191-198）。
  - **horizontal_bar**（block_horizontal_bar 变体）：长低 countertop bar（~0.46×0.22 m，`holder`/`holder_shell` 长 YZ wedge `extrude(HALF_L, both)` L113-138，15° slot 经 `_make_slot_cutter` L95-110）；刀以浅 15° 平躺单行；`knife_{i}_slide` PRISMATIC axis=(0,0,1) `rpy=(JOINT_ROLL≈75°,0,0)` L39；`_knife_x(i)` L91-92 沿 X 等距。
- **Slot B holding_mechanism**（block 内部持刀方式）：
  - **angled_prismatic_slots**（parent 基线）：实心 block 逐刀铣 `_tilted_box(slot_w, SLOT_THICK, ...)` 一刀一矩形 slot（parent L122-128）；刀靠 clearance fit + 重力坐入；每 `knife_{i}_slide` PRISMATIC（**全 N 刀都是独立 slide**）。
  - **bristle_insert**（mech_bristle 变体）：通用刷毛 block —— `knife_block` = `housing_shell`（中空 smoked-acrylic，`_build_housing` L84-97 + `_build_front_pocket` L100-113）+ `bristle_{i}` 密集软杆栅格（loop `for i in range(N_BRISTLES)` L251-261，`Cylinder` 杆，N_BX×N_BY 自动算 L43-45），刀身插入杆间；**只有 1 把 `chef_knife` 是独立 part `chef_slide` PRISMATIC** L292-329，其余 5 把是 `FIXED_KNIVES` L60-66 inline FIXED block visuals（`{name}_steel`/`{name}_grip` L264-287）→ **bristle_insert 不携带完整 per-N PRISMATIC 复制逻辑**（见 §排除项 / §9 兼容矩阵）。
- **Slot C base_stand**（block 坐在什么上）：
  - **rubber_feet**（parent 基线）：四个深色橡胶脚直接坐 block 底（`foot_{i}` Cylinder visuals loop `for i,(fx,fy) in enumerate(foot_xy)` parent L240-246），**block 即 root，无独立 base part**，坐地 z≈0。
  - **sculptural_pedestal**（base_pedestal 变体）：block FIXED-mount 在一根高 turned 青铜柱顶 —— `pedestal` part（root）/ `pedestal_column`（`_build_pedestal` L138-191 CadQuery `revolve(360)`：base plinth→entasis shaft→capital）+ `base_pad_{i}`(`for i in range(4)` L304-314) / `pedestal_to_block` FIXED origin z=PEDESTAL_TOP=0.130 L352-358；抬高整套 ~0.13 m。
  - **cast_metal_stand**（base_metal_stand 变体）：block 卡在一个重铸金属角架里 —— `cast_metal_stand` part（root）/ `stand_frame`（`_build_stand` L134-199：filleted base plate + 倾斜 `left`/`right` 侧壁 + 倾斜 `back` 支撑 + 铸 `gusset` 肋 `for y_sign... for x_off...`）+ `stand_front_lip` L308-313 / `stand_to_block` FIXED origin z=0.012 L351-357；run_tests 用 `expect_contact(foot_{i}, stand_frame)` L520-526 守落座。
- **palette**：全样本主体同色族（`oak=(0.80,0.64,0.42)` block / `engraved_oak=(0.42,0.28,0.15)` logo / `walnut=(0.32,0.19,0.11)` 把 / `stainless_steel=(0.78,0.79,0.82)` 刀 / `rubber=(0.08,0.08,0.08)` 脚）；bristle_insert 引入 `smoked_acrylic=(0.30,0.33,0.38,0.75)` + `bristle_rod=(0.12,0.12,0.13)`；pedestal 引入 `bronze=(0.28,0.24,0.19)`；metal_stand 引入 `cast_iron=(0.22,0.22,0.24)`。→ 4-6 套 colorway（见 §7 palette_style）。

## 核心身份

一只**厨房刀座套装（kitchen knife block set）**：一只持刀 block（root，可以是后仰橡木 wedge、竖直方块、或长低 countertop bar，或中空 smoked-acrylic 刷毛 housing），表面 1-2 行 slot 持 **N 把厨刀**（chef/bread/santoku/utility/paring…，刀身渐变：chef 最大 → paring 最小，`KNIFE_SPECS` 携带 blade_len/blade_w/travel/grip_len/slot_w），每把刀是一个**独立 PRISMATIC 滑出件**（沿各自 slot 轴抽出，行程 ~0.10-0.18 m），外加一把**两段式厨剪**（沿 `shears_slide` PRISMATIC 滑出宽前 pocket + `shears_pivot` REVOLUTE 在中央铆钉张开 ~40°）。block 底部可以是四橡胶脚直接坐地、或 FIXED-mount 在 turned 青铜 pedestal 柱顶、或卡在铸金属角架里。活动语义恒为：**每把刀沿其 slot 轴 PRISMATIC 抽出**（多重性主轴）+ **厨剪 PRISMATIC 滑出 + REVOLUTE 张开**（第二非 fixed-joint 锚）。默认成熟域：block_form × holding_mechanism × base_stand × 刀数 N∈[3,8] 笛卡尔积的单座厨房刀座。

不该混入：
- **单把厨刀（single knife）**——只是一把刀（blade + handle + bolster），没有 block / holder、没有 N 把刀的多重性、没有厨剪、主体不是「持刀座」；本类核心身份是**一座 block 持 N 把刀 + 一把剪**，缺 block + 多刀 + 剪即出类（相邻小类 `single knife` 的样本 `rec_knife_var_*` 即此，已排除）。
- **折叠 / 伸缩美工刀（folding / retractable utility knife）**——单件、刀片绕枢轴折叠或沿握把伸缩，是单把刀的机构变体，不是刀座套装（相邻小类 `rec_retractable_utility_knife_*` 即此）。
- **通用工具 / 餐具收纳筒（utensil holder / tool crock / cutlery caddy）**——一只敞口筒随意插各种器具，无逐件 slot、无逐刀 PRISMATIC、无渐变刀组 + 厨剪的刀座身份；本类是**专门持厨刀组**的 block，每刀有专属 slot 与独立 slide。
- **磁吸刀条 / 墙挂刀架（magnetic knife bar / wall rack）**——壁挂磁条吸刀，无 block 体、无坐地 base、无逐刀机械 slot；本类是台面坐地的 block/holder。

## 槽位 + 候选模块表

> **建模注记**：knife_set 是 **root `knife_block`/`holder`/`housing`（dispatch block_form 主壳几何 + holding_mechanism 内部 slot/刷毛 + base_stand）+ N 个刀（PRISMATIC，multiplicity 主轴）+ 一把厨剪（PRISMATIC slide + REVOLUTE pivot，固定 2 段，非多重性）parallel children**。
> - **Slot A（block_form）改 block 主壳几何 + slot 轴朝向**：slanted_block（后仰 wedge，slot 轴 12° tilt）/ upright_block（竖直方块，垂直 slot）/ horizontal_bar（长低 bar，浅 15° 单行 slot）。它决定刀 `*_slide` 的 origin rpy（tilt / 无 / roll）与 row 布局（两行 vs 单行）。
> - **Slot B（holding_mechanism）改 block 内部持刀方式 + 是否全 N 刀都 PRISMATIC**：angled_prismatic_slots（实心 block 逐刀铣 slot，**全 N 刀独立 PRISMATIC**）/ bristle_insert（中空刷毛栅格，**仅 1 把 chef PRISMATIC + 其余 FIXED inline**）。
> - **Slot C（base_stand）改 root part 树 + 是否多一个 FIXED 子关节**：rubber_feet（无独立 base，block 即 root，inline `foot_{i}` visual）/ sculptural_pedestal（root=pedestal，block FIXED on top）/ cast_metal_stand（root=stand，block FIXED in cradle）。
> - **knife_count（N）是 multiplicity 主轴**：angled_prismatic_slots 下随 N 展开全 [3,8]（每刀一独立 PRISMATIC）；bristle_insert 下 N 只控制 inline FIXED 刀的视觉数量（1 slide + N-1 fixed），不展开 N 个 slide（见 §8 / §9 兼容矩阵）。

### Slot A：block_form（block 形态 / 轮廓 + slot 轴朝向 —— root 主壳几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slanted_block（基线） | parent rec_..._1d3b3a0e | `_build_block_solid` L101-129 / `_tilted_box` L90-98 / `_top_point` L73-78 + `BACK_ROW_M`/`FRONT_ROW_M` L81-82 / knife slide rpy=(0,-TILT,0) L295 / `TILT=12°` L28 | eligible if compatible | 后仰 12° 橡木 wedge（XZ 多段线 extrude both）+ 前 pocket panel/cheeks/floor；刀沿 block 轴向角度 slot 抽出（`knife_{i}_slide` PRISMATIC axis=(0,0,1) `rpy=(0,-TILT,0)`）；两行 slot（back/front row mouth points `_top_point(0.70)`/`_top_point(0.26)` + per-knife y）|
| upright_block | rec_knife_set_var_block_upright | `_build_block_solid`（axis-aligned）L69-101 / `BLOCK_W/D/H` L32-34 / `KNIFE_POSITIONS` L53-56 / 垂直 slot cut L81-90 / knife slide origin=(kx,ky,TOP_Z) **no tilt** L286 / shears_slide axis=(1,0,0) L344-355 / `_shears_steel_h` 旋 90° L191-198 | eligible if compatible | 竖直 axis-aligned `box(BLOCK_D,BLOCK_W,BLOCK_H)`，刀直抽（`knife_{i}_slide` PRISMATIC axis=(0,0,1) 无 tilt）；shears 从前面横向 slot 滑出（axis=(1,0,0)）；两行 slot（KNIFE_POSITIONS 前后两 X 排）|
| horizontal_bar | rec_knife_set_var_block_horizontal_bar | `_build_holder_solid` L113-138 / `_make_slot_cutter` L95-110 / `_knife_x(i)` L91-92 / `JOINT_ROLL≈75°` L39 / `_z_top` 楔面高 L81-84 / knife slide rpy=(JOINT_ROLL,0,0) L315-316 / `SLOT_ANGLE=15°` L30-31 | eligible if compatible | 长低 countertop bar（~0.46×0.22 m，YZ wedge `extrude(HALF_L,both)`，后 0.065→前 0.040 m 高）；刀浅 15° 平躺**单行**（`_knife_x(i)` 沿 X 等距）；`knife_{i}_slide` PRISMATIC axis=(0,0,1) `rpy=(JOINT_ROLL,0,0)`(75° roll)；part 名 `holder`/`holder_shell`（模板统一为 `knife_block`/`block_shell`）|

### Slot B：holding_mechanism（block 内部持刀方式 —— 决定是否全 N 刀都 PRISMATIC）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| angled_prismatic_slots（基线） | parent rec_..._1d3b3a0e | `_build_block_solid` 逐刀 `block.cut(_tilted_box(slot_w,SLOT_THICK,clen,center))` L122-128 / `SLOT_THICK=0.0066` L49 / knife loop + 每 `knife_{i}_slide` PRISMATIC L290-299 | eligible if compatible | 实心 block 逐刀铣一矩形 slot（一刀一 slot），刀靠 clearance fit + 重力坐入；**全 N 刀每把都是独立 PRISMATIC slide**（携带完整 per-N 复制逻辑）；run_tests `allow_isolated_part` 每刀（gravity-seated clearance fit）|
| bristle_insert | rec_knife_set_var_mech_bristle | `_build_housing` L84-97 + `_build_front_pocket` L100-113 / `bristle_{i}` grid loop L251-261（`N_BRISTLES=N_BX*N_BY` L43-45）/ `FIXED_KNIVES` inline L60-66, L264-287 / 单 `chef_knife` part + `chef_slide` PRISMATIC L292-329 / `allow_overlap(housing_shell,chef_steel)` L419-423 | eligible if compatible（仅 N=可见刀数，**joint 维度退化**：1 slide + N-1 FIXED visual）| 中空 smoked-acrylic housing + 密集软杆栅格（`bristle_{i}`，blades 插杆间）；**只有 1 把 chef 是独立 part `chef_slide` PRISMATIC**（≥1 非 fixed joint 底线），其余刀 inline FIXED block visual（松散软杆无法各自锚一个独立 prismatic 子件）；shears 仍 slide+pivot |

### Slot C：base_stand（block 坐在什么上 —— 决定 root part 树 + 是否多一 FIXED 子关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| rubber_feet（基线） | parent rec_..._1d3b3a0e | `foot_{i}` Cylinder visuals loop `for i,(fx,fy) in enumerate(foot_xy)` L239-246 / block 即 root（block_shell origin z=LIFT=0.008）L230-236 | eligible if compatible | 四个深色橡胶脚直接坐 block 底（inline FIXED visual on root，**无独立 base part、无独立 joint，Rule 1**）；block 是 root，坐地 z≈0 |
| sculptural_pedestal | rec_knife_set_var_base_pedestal | `pedestal` part(root) L296-301 / `pedestal_column`(`_build_pedestal` `revolve(360)`) L138-191 / `base_pad_{i}` `for i in range(4)` L304-314 / `pedestal_to_block` FIXED origin z=PEDESTAL_TOP=0.130 L352-358 | eligible if compatible | block FIXED-mount 在 turned 青铜柱顶（base plinth→entasis shaft→capital，`revolve`）；新增 1 个 FIXED 子关节 `pedestal_to_block`；抬高 ~0.13 m；root=pedestal |
| cast_metal_stand | rec_knife_set_var_base_metal_stand | `cast_metal_stand` part(root) L301-306 / `stand_frame`(`_build_stand`: plate+侧壁+back+gusset) L134-199 / `stand_front_lip` L308-313 / `stand_to_block` FIXED origin z=0.012 L351-357 / `expect_contact(stand_frame,foot_{i})` L520-526 | eligible if compatible | block 卡在重铸金属角架里（filleted base plate + 倾斜侧壁 + back 支撑 + 铸 gusset 肋）；新增 1 个 FIXED 子关节 `stand_to_block`；block 橡胶脚落座 plate；root=stand |

## 槽位图（slot graph）

pattern: multiplicity（root `knife_block`（或 pedestal/stand 为 root、block FIXED 其上）持有 block_form 主壳 + holding_mechanism 内部 slot/刷毛；N 个 `knife_{i}`（PRISMATIC，**多重性主轴**）+ 一把厨剪（PRISMATIC slide + REVOLUTE pivot）挂到 block）

```
[base_stand slot]  (决定 root 与是否多一 FIXED 子关节)
  ├─ rubber_feet         : knife_block 即 root（坐地）；foot_{i} inline FIXED visual（无 joint, Rule 1）
  ├─ sculptural_pedestal : pedestal(root) ──[pedestal_to_block: FIXED, origin=(0,0,PEDESTAL_TOP=0.130)]── knife_block
  └─ cast_metal_stand    : cast_metal_stand(root) ──[stand_to_block: FIXED, origin=(0,0,0.012)]── knife_block

knife_block  (持刀体；由 block_form 决定主壳 mesh + slot 轴朝向，由 holding_mechanism 决定内部持刀)
  │   block_form: slanted_block(后仰12° wedge) / upright_block(竖直方块) / horizontal_bar(长低 bar)
  │   holding_mechanism: angled_prismatic_slots(实心铣slot) / bristle_insert(中空刷毛+1 chef slide)
  │
  ├── [knife_count multiplicity 轴]  knife_{i} / knife_{i}_steel / knife_{i}_grip / knife_{i}_rivet_{j}   i∈range(N)
  │     ──[knife_{i}_slide: PRISMATIC axis=(0,0,1), origin=(slot mouth x,y,z),
  │        rpy = slanted:(0,-TILT,0) / upright:(0,0,0) / horizontal:(JOINT_ROLL≈75°,0,0),
  │        lower=0 upper=spec["travel"]≈0.10-0.18]
  │       per-knife (x,y) slot center 由 N + block_form 解析（slanted/upright 两行；horizontal 单行 _knife_x(i)）
  │       N 范围 [3,8]；angled_prismatic_slots → 全 N 独立 slide；bristle_insert → 1 chef slide + N-1 FIXED inline visual
  │
  └── [shears]  (固定 2 段总成，非多重性轴；每个样本都有 → 第二非 fixed-joint 锚)
        shears_inner_half ──[shears_slide: PRISMATIC axis=(0,0,1)(slanted/horizontal rpy=tilt/roll) 或 (1,0,0)(upright),
        │                     origin=pocket mouth, lower=0 upper=SHEARS_TRAVEL=0.10]
        shears_outer_half ─[shears_pivot: REVOLUTE axis=(1,0,0)(slanted/horizontal) 或 (0,0,1)(upright),
                             parent=shears_inner_half, origin=(0,0,PIVOT_Z=0.006), lower=0 upper=SHEARS_OPEN=0.70]
```

接口点位与 joint 语义：
- **knife_count 接口（multiplicity 主轴）**：每个 `knife_{i}` 是 `knife_block` 的 PRISMATIC child，axis=(0,0,1)（局部 +Z=抽出），origin=该刀 slot mouth 点 `(mx, spec["y"], mz + LIFT)`（slanted: `BACK_ROW_M`/`FRONT_ROW_M` + per-knife y；upright: `KNIFE_POSITIONS[i]`；horizontal: `(_knife_x(i), SLOT_MOUTH_Y, mzw)`），joint `rpy` 把局部 +Z 旋到该 block_form 的抽出方向。刀身 captured 在 block slot 内（loose clearance fit，`allow_isolated_part` per knife，照搬 parent L385-392；horizontal_bar 另用 `allow_overlap(holder_shell, knife_{i}_steel/_grip)` solid-proxy sleeve L414-432）。rest pose q=0（刀坐入 slot，把柄露出 block 顶）。
- **block_form 接口（root，互斥三选一）**：决定 root 主壳 mesh（wedge / box / 长 bar）与刀 slot 轴朝向（slide origin rpy）。slanted/upright 两行布局，horizontal 单行 `_knife_x(i)`（单行 vs 两行是 N 与 block_form 的函数，authoring helper 决定，见 §排除项）。
- **holding_mechanism 接口（root 内部，互斥二选一）**：angled_prismatic_slots = 实心 block 逐刀 `block.cut(_tilted_box(...))`，全 N 刀独立 PRISMATIC；bristle_insert = 中空 housing + `bristle_{i}` 栅格 + 1 chef PRISMATIC + N-1 FIXED inline。两者改 part/joint 数（全 N slide vs 1 slide + N-1 visual）。
- **base_stand 接口（root，互斥三选一）**：rubber_feet = block 即 root（`foot_{i}` inline FIXED visual，无 joint，Rule 1）；sculptural_pedestal = `pedestal`(root) + `pedestal_to_block` FIXED origin z=0.130；cast_metal_stand = `cast_metal_stand`(root) + `stand_to_block` FIXED origin z=0.012 + `expect_contact(stand_frame, foot_{i})`。base FIXED origin 落在 base 顶面真实接触面（`fail_if_articulation_origin_far_from_geometry` 守）。
- **shears 接口（固定 2 段，非多重性）**：`shears_inner_half` 是 block 的 PRISMATIC child（`shears_slide` 滑出前 pocket）；`shears_outer_half` 是 inner 的 REVOLUTE child（`shears_pivot` 绕中央 `shears_pivot_rivet` 张开，outer 半边有 clearance hole 套铆钉）。两段各有 grip rivets（`shears_*_rivet_{j}` 经 `for j,(...)` emit）。剪坐前 pocket（`allow_isolated_part` inner/outer + `expect_within`/`expect_overlap` 守座入）。
- **mating policy**：所有刀 / 剪是 blade-in-slot / blade-in-pocket captured-slide（PRISMATIC），剪 pivot 是 pin-in-clearance-hole captured-pin（REVOLUTE），base 是 block-on-base FIXED。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_isolated_part`/`allow_overlap`/`expect_contact` 守 captured overlap / clearance（照搬各样本 run_tests 段）。
- **rest pose**：所有刀 q=0 坐入 slot（把柄露出顶）；剪 slide q=0 收入 pocket、pivot q=0 闭合；base FIXED 无姿态。
- **互斥 / 可选 / 派生**：block_form 三选一互斥；holding_mechanism 二选一互斥（bristle_insert 时 N 退化为 1 slide + N-1 FIXED）；base_stand 三选一互斥；knife_count N 是 multiplicity 主轴，与 holding_mechanism 联动（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / block_form — slanted_block（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knife_block`（root 或 base 的 FIXED child；visual: `block_shell` 后仰 wedge + 前 pocket panel/cheeks/floor）| `_build_block_solid` L101-129 / `_tilted_box` L90-98 |
| internal joints | 无（block 本体；刀 / 剪 / base 关节在下面各槽）| — |
| upstream interface | rubber_feet 下坐地（root, z≈LIFT），或被 base FIXED 抬起 | L230-236 |
| downstream interface | 顶面两行角度 slot mouth（供刀 PRISMATIC）+ 前 pocket（供剪）+ 底 foot/ base 接口 | L122-128, L302 |

### Slot A / block_form — upright_block
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knife_block`（visual `block_shell` 竖直 `box(BLOCK_D,BLOCK_W,BLOCK_H)` + 垂直刀 slot + 横向 shears slot）| `_build_block_solid` L69-101 |
| internal joints | 无 | — |
| downstream interface | 顶面两行垂直 slot（刀直抽，slide 无 tilt）+ 前面横向 shears slot（`shears_slide` axis=(1,0,0)）| L77-99, L344-355 |

### Slot A / block_form — horizontal_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knife_block`（visual `block_shell`；源名 `holder`/`holder_shell`，长低 YZ wedge bar）| `_build_holder_solid` L113-138 |
| internal joints | 无 | — |
| downstream interface | 顶面单行浅 15° slot（`_knife_x(i)` 沿 X 等距，slide rpy=(JOINT_ROLL,0,0)）+ 端 shears slot | L95-110, L128-133, L281-320 |

### Slot B / holding_mechanism — angled_prismatic_slots（基线 + multiplicity 载体）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 实心 block（逐刀铣矩形 slot）；N 个 `knife_{i}`（`knife_{i}_steel` 锥刀身+bolster + `knife_{i}_grip` walnut 把 + 两 `knife_{i}_rivet_{j}`）| `_build_block_solid` cut L122-128 / `_knife_steel` L143-154 / `_knife_grip` L157-165 |
| internal joints | N 个 `knife_{i}_slide` PRISMATIC axis=(0,0,1) origin=slot mouth rpy=block_form-tilt lower=0 upper=spec["travel"] | parent L290-299 / count_4 L248-257 / count_8 L217-226 |
| upstream interface | 刀身坐 block slot（gravity clearance fit，`allow_isolated_part` per knife）| parent L385-392 |

### Slot B / holding_mechanism — bristle_insert
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knife_block`=`housing_shell`（中空 acrylic + 前 pocket）+ `bristle_{i}` 软杆栅格（inline visual loop）+ N-1 把 `FIXED_KNIVES` inline FIXED block visual（`{name}_steel`/`{name}_grip`/`{name}_rivet_{j}`）+ 1 把 `chef_knife` part | `_build_housing` L84-97 / bristle loop L251-261 / FIXED_KNIVES L264-287 / chef L292-315 |
| internal joints | 仅 1 个 `chef_slide` PRISMATIC axis=(0,0,1) origin=(0,0,INSERT_Z) lower=0 upper=CHEF_TRAVEL=0.20；**其余刀无 joint（FIXED inline，Rule 1）**；`bristle_{i}` 无 joint（inline visual，Rule 1）| chef L318-329 |
| upstream interface | chef blade 插入刷毛腔（`allow_overlap housing_shell↔chef_steel` L419-423）；FIXED 刀 inline | L419-434 |

### Slot C / base_stand — rubber_feet（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 base part；四 `foot_{i}` Cylinder 为 `knife_block` 的 inline visual（block 即 root）| `foot_{i}` loop L239-246 |
| internal joints | 无（脚是 inline FIXED visual，Rule 1）| — |
| upstream interface | block 坐地 z≈0（block_shell origin z=LIFT=0.008，脚 1mm 嵌入底）| L230-246 |

### Slot C / base_stand — sculptural_pedestal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedestal`（root，visual `pedestal_column` turned 青铜柱 + `base_pad_{i}` `for i in range(4)`）| `_build_pedestal` L138-191 / pads L304-314 |
| internal joints | `pedestal_to_block` FIXED parent=pedestal child=knife_block origin=(0,0,PEDESTAL_TOP=0.130)；block 上仍持 N 刀 PRISMATIC + 剪 | L352-358 |
| upstream interface | pedestal 坐地（base plinth z≈0，`base_pad_{i}` 防滑）| L296-314 |
| downstream interface | 柱顶 plate（block 脚落座，FIXED origin z=0.130）| L182-183 |

### Slot C / base_stand — cast_metal_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cast_metal_stand`（root，visual `stand_frame`: filleted plate + 倾斜侧壁 + back 支撑 + 铸 gusset 肋 + `stand_front_lip`）| `_build_stand` L134-199 / lip L308-313 |
| internal joints | `stand_to_block` FIXED parent=cast_metal_stand child=knife_block origin=(0,0,0.012)；block 上仍持 N 刀 + 剪 | L351-357 |
| upstream interface | stand plate 坐地 z=0 | L139-145 |
| downstream interface | plate 顶面（block 橡胶脚落座，`expect_contact(stand_frame, foot_{i})`，FIXED origin z=0.012）| L509-526 |

### knife_count multiplicity（刀复制；PRISMATIC 移动件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | N 个 `knife_{i}` part（`knife_{i}_steel`/`knife_{i}_grip`/`knife_{i}_rivet_{j}`），共享 `_knife_steel`/`_knife_grip`/`_knife_rivet_x` helper | count_4 `_build_knife_part` L219-257 / count_8 `_build_knife` L188-226 |
| joints | N 个 `knife_{i}_slide` PRISMATIC（angled_prismatic_slots）；或 1 个 `chef_slide` + N-1 FIXED inline（bristle_insert）| count_4 L248-257 / count_8 L217-226 / bristle L318-329 |
| placement | `for i in range(N)`，per-knife (x,y) slot center 由 N + block_form 解析（slanted/upright 两行；horizontal 单行 `_knife_x(i)`）；blade_len/width 沿 set 渐变（chef→paring，`KNIFE_SPECS`）| count_4 L305-306 / count_8 L316-317 / upright L248-292 / horizontal L281-320 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| block_form | enum | slanted_block / upright_block / horizontal_bar | slanted_block | choice | deterministic procedural sampler 选；决定 root 主壳 mesh + 刀 slide origin rpy + row 布局（互斥）| Slot A 表 |
| holding_mechanism | enum | angled_prismatic_slots / bristle_insert | angled_prismatic_slots | choice | sampler 选；决定是否全 N 刀 PRISMATIC（互斥）| Slot B 表 |
| base_stand | enum | rubber_feet / sculptural_pedestal / cast_metal_stand | rubber_feet | choice | sampler 选；决定 root part 树 + 是否多一 FIXED 子关节（互斥）| Slot C 表 |
| knife_count (N) | int | 声明产品域 **[3,8]**；sweep 采样域 [3,8]（偏小加权：N=4/5/6 高频、3/7 常见、8 长尾）| 6 | conditional→slot_choice | **multiplicity 主轴**；编入 slot_choice 为 `("knife_count", f"n{N}")`（拓扑维度）；bristle_insert 时 N 控制可见刀数（1 slide + N-1 FIXED）（见下 conditional + §8/§9）| parent(6) / count_4 / count_8 |
| palette_style | enum | natural_oak_walnut / dark_acrylic_steel / bamboo_blond / brushed_steel_black / bronze_pedestal_oak | natural_oak_walnut | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| block_width_scale | float | [0.90, 1.18] | 1.0 | conditional | 缩放 block 主壳宽（容纳 N 刀的 Y / 单行长 X）；clamp 使 N 刀 slot 不互撞（见下不等式）；count_8 已示范 `BLOCK_WIDTH 0.130→0.175` 容纳更多刀 | count_8 L41 / parent L41 |
| block_depth_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 block 深（X，slanted/upright）或 bar 深（Y，horizontal）；clamp；连带刀 slot 深 / pocket 派生 | parent L37-40 |
| block_height_scale | float | [0.90, 1.12] | 1.0 | conditional | 缩放 block 高（slanted/upright，~0.24；horizontal bar 低 ~0.065）；clamp ≥ 最长刀 blade_len+slot 余量 | parent L39-40 / horizontal L48-54 |
| knife_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放每刀 PRISMATIC upper（基 spec["travel"]≈0.10-0.18）；clamp ≤ 该刀完全抽出 slot 所需且 ≤ blade_len | parent L297-298 |
| shears_open_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 `shears_pivot` REVOLUTE upper（基 SHEARS_OPEN=0.70）；clamp ≤ 0.95·(π/2) 不过开 | parent L367 |
| tilt_angle_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 slanted_block 有效；缩放后仰角（基 TILT=12°）；clamp ∈[8°,16°]；连带 slide origin rpy + slot cutter 角 | slanted L28 |
| (—) | constraint | — | — | inequality | N 刀 slot 不互撞 / 不超 block 宽：`(per-row 刀数)·(max slot_w + gap) ≤ block_width·block_width_scale − 2·margin`；违反则升 block_width_scale（如 count_8 BLOCK_WIDTH=0.175）或按比例缩 slot_w / 拒绝重采 | count_8 L41,L125-127 / 接口 clearance |
| (—) | constraint | — | — | inequality | 刀完全坐入 slot 不穿底：`max(blade_len)·1.0 ≤ block_height·block_height_scale − slot_mouth_clearance`（slanted/upright）；horizontal bar 刀躺浅 slot 时 slot 深 ≥ blade_len；违反升 block_height / 缩 blade_len | parent L124, L130-134 |
| (—) | constraint | — | — | inequality | 刀抽出不脱轨且露出 slot mouth：`knife_travel·knife_travel_scale ≤ blade_len`（drawn blade zmin > mouth − ε）；违反回缩 travel | parent L471-487 |
| (—) | constraint | — | — | conditional | holding_mechanism=bristle_insert 时：N 解析为 1 个 `chef_slide` PRISMATIC + (N-1) 个 FIXED inline 刀 visual + `bristle_{i}` 栅格（非 N 个独立 slide）；angled_prismatic_slots 时全 N 独立 PRISMATIC（见 §8/§9）| bristle L264-329 |
| (—) | constraint | — | — | conditional | base_stand=sculptural_pedestal/cast_metal_stand 时新增 1 个 FIXED `*_to_block` 子关节、root 改为 base part、block 抬高（pedestal z+0.130 / stand z+0.012）；rubber_feet 时 block 即 root 坐地 | pedestal L352-358 / stand L351-357 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 block_form / holding_mechanism / base_stand / knife_count 的拓扑**。

**palette_style colorway（5 套，来自 8 个 5★ 源材质）**：
- `natural_oak_walnut`（基线 / 默认）：oak block (0.80,0.64,0.42) + walnut 把 (0.32,0.19,0.11) + stainless steel 刀 (0.78,0.79,0.82) + engraved_oak logo (0.42,0.28,0.15) + rubber 脚 (0.08,0.08,0.08)（parent / 多数样本原色）。
- `dark_acrylic_steel`：smoked_acrylic block (0.30,0.33,0.38,0.75) + bristle_rod (0.12,0.12,0.13) + steel 刀 + walnut 把 + logo_dark (0.18,0.20,0.22)（bristle_insert 源族；现代深色刀座身份）。
- `bamboo_blond`：浅竹 block (0.85,0.74,0.52) + 深竹纹 logo + steel 刀 + 浅木把 + black 脚；明亮厨房身份。
- `brushed_steel_black`：拉丝不锈钢 block (0.66,0.67,0.70) + black 把 (0.10,0.10,0.11) + steel 刀 + black 脚；专业不锈钢刀座身份。
- `bronze_pedestal_oak`：oak block + bronze pedestal/stand (0.28,0.24,0.19)（base_pedestal）/ cast_iron stand (0.22,0.22,0.24)（base_metal_stand）+ steel 刀 + walnut 把；雕塑底座 / 重金属架身份（仅 base≠rubber_feet 时此 colorway 最贴）。

## Multiplicity / Copy Logic

**1 根小类级 multiplicity 主轴**（刀数 —— 本类的支配性多重性轴）：

- **count_param**：`knife_count`（模板内变量 N；sources 用 `NUM_KNIVES`(count_4) / `N_KNIVES`(count_8)；parent / base_metal_stand 用手写 `KNIVES` dict（6 entry，hand-named keys chef_knife/bread_knife/santoku_knife/utility_knife/paring_knife_0/paring_knife_1））。block 前 / 顶面的刀数；每刀是一个独立 PRISMATIC joint（angled_prismatic_slots），所以非 fixed joint 数随 N 变化（N+2，含 2 个 shears 关节）。**这是支配性轴**（改全模板 part/joint 拓扑，且是 angled_prismatic_slots 机构的主结构）。
- **N_range**：声明产品域 **[3, 8]**（小型 3 刀入门套 → 满 8 槽 block；source map 建议 [3,8]，block 宽 / row 布局由 `block_width_scale` / per-row 解析自动适配，count_8 已示范 `BLOCK_WIDTH 0.130→0.175` 容纳 8 刀（每行 4），cheeks/floor/foot 随之 respaced）。样本覆盖 {4,6,8} 仅示范 copy 逻辑，sampler 填满 [3,8] 其余 {3,5,7}。`config_from_seed` 的 sweep 采样域 **[3, 8]**（偏小加权：N=4/5/6 高频、3/7 常见、8 长尾）。每个不同 N 是一个 topology。
- **sampling domain**：`config_from_seed` 用 `rng.choices(range(3,9), weights=偏中小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [3,8]，并在 bristle_insert 候选下解析为 1 slide + N-1 FIXED inline（见 §9 兼容矩阵）。
- **copied object**：单把刀 = `knife_{i}` part（`knife_{i}_steel` 锥形 blade+bolster `_knife_steel` L143-154 + `knife_{i}_grip` lofted walnut 把 `_knife_grip` L157-165 + 两个 `knife_{i}_rivet_{j}` Cylinder + 把柄曲线 x 偏移 `_knife_rivet_x` L168-175），由共享 helper 建（count_4 包成 `_build_knife_part` L219-257；count_8 包成 `_build_knife` L188-226）。
- **naming**：`knife_{i}` part、`knife_{i}_steel`/`knife_{i}_grip`/`knife_{i}_rivet_{j}` visual、`knife_{i}_slide` joint（0-based i，按 KNIFE_SPECS 顺序 chef→paring）；`for i in range(N)`（count_4 L305 / count_8 L316 / upright L248 / horizontal L281 已用此结构，**直接作 copy-logic 源**）。**PARENT / base_metal_stand 用 `for kname, spec in KNIVES.items()` dict 形 hand-named（chef_knife/paring_knife_0…），模板必须重构成 index loop `knife_{i}`**（见顶部注记 / source map §2.0 FORK_VARIANTS）。
- **placement**：per-knife (x,y) slot center **绝对式**——由 N + block_form 解析：slanted/upright 两行（back row / front row，per-knife y 沿 Y 等距）；horizontal 单行（`_knife_x(i) = -(N-1)·spacing/2 + i·spacing` L91-92，沿 X 等距，对称）。绝对式（每个 i 的位置由 N 与中心解析，不累加漂移）是 N-不变前提。单行 vs 两行是 N 与 block_form 的函数（slanted/upright 大 N 用两行，horizontal 恒单行），由 authoring helper 决定（见 §排除项）。blade_len/width 沿 set 渐变（chef 最大 → paring 最小，`KNIFE_SPECS` 携带）。
- **joint policy**：每刀是**独立 PRISMATIC joint**，parent=`knife_block`，axis=(0,0,1)（局部 +Z=抽出，joint rpy 把它旋到该 block_form 的抽出方向：slanted `rpy=(0,-TILT,0)`、upright `rpy=(0,0,0)`、horizontal `rpy=(JOINT_ROLL≈75°,0,0)`），`MotionLimits(lower=0.0, upper=spec["travel"]≈0.10-0.18, effort=20, velocity=0.5)`，travel 随 blade_len 缩放。**不链式、不共享 hub**——每刀独立滑出自己的 slot（parent L290-299）。
- **source/gating**：copy-logic 源取 count_4 L305-306 `for i in range(NUM_KNIVES): _build_knife_part(...)` + count_8 L316-317 `for i in range(N_KNIVES): _build_knife(...)` + 共享 `_knife_steel`/`_knife_grip`/`_knife_rivet_x` helper（cross-form loop 另取 upright L248-292 / horizontal L281-320 的 inline `knife_{i}` loop）；**N=6 即 parent 基线**（dict 形，须重构为 range(6)），N=4 取 count_4，N=8 取 count_8。knife_count 与 holding_mechanism 的兼容见 §9（bristle_insert → N 控制 1 slide + N-1 FIXED inline，非 N 个 slide）。

**knife_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("knife_count", f"n{N}")`），否则不同刀数的拓扑维度损失（对齐 tool_cart drawer_count / cushion pan_count / fence_cascade 范式）。

> 注：以下是**固定 / 派生 N 的 module-local visual 复制**（非可变 count 轴本体、按 Rule 1 inline，**不暴露为独立 multiplicity 轴**）：rubber_feet 的四 `foot_{i}`（`for i,(fx,fy) in enumerate(foot_xy)`，固定 4，FIXED inline visual）；bristle_insert 的 `bristle_{i}` 软杆栅格（`for i in range(N_BRISTLES)`，N_BRISTLES 由 cavity 尺寸算，FIXED inline visual，非 jointed）；sculptural_pedestal 的 `base_pad_{i}`（`for i in range(4)`）；cast_metal_stand 的 `gusset`（嵌套 `for y_sign... for x_off...`，固定 4，FIXED inline）；每刀 / 剪的 `*_rivet_{j}`（`for j,(...)`，固定 2，FIXED inline visual）；shears 两段（`shears_inner_half`/`shears_outer_half`，固定 2-part 总成，slide+pivot，**非多重性轴**）。这些都不是模板级可变 count 轴。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity 主轴，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = block_form(3) × holding_mechanism(2) × base_stand(3) = **18** base topologies（source map combo 预审）。
- 叠 knife_count：angled_prismatic_slots（全 N 独立 slide）× N∈[3,8]（6 值）= 每个 (block_form×base_stand) 组合下 6 个 distinct joint 拓扑；bristle_insert（1 slide + N-1 FIXED visual）× N∈[3,8] = N 改可见刀数（joint 维度恒 1 chef slide，但 part 数随 N 变 → 仍按 N distinct 编 slot_choice，保守计为可区分）。
- 总合法组合（保守，按 §9 矩阵）≈ block_form(3) × base_stand(3) × [angled_prismatic_slots×N(6) + bristle_insert×N(6)] = 3 × 3 × 12 = **108**（远超 ≥10 门控；即便把 bristle×N 仅算 1 个 joint 拓扑、N 不展开，也有 3×3×(6+1)=63）。

仅 block_form(3) × holding_mechanism(2) × base_stand(3) = **18** 已含 3 种 block 几何 / slot 轴 × 2 种持刀机构（全 N PRISMATIC vs 1 slide+FIXED）× 3 种 base（无 base / pedestal FIXED / stand FIXED）的结构差异 ≥ 10 稳过；叠 knife_count 全 N → ~108 充裕。

理由：block_form(3 种主壳几何 + slot 轴) × holding_mechanism(2 种持刀，含全 N 独立 PRISMATIC vs 1 slide+N-1 FIXED 的 joint 拓扑差异) × base_stand(3 种 root / FIXED 子关节差异) × knife_count(全 N [3,8]) 提供充裕真实结构差异。**knife_count 必须编入 slot_choices_for_seed**（`("knife_count", f"n{N}")`），否则不同刀数在 slot_choice 上不可区分，损失主多重性维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` block_form，再 `rng.choice` holding_mechanism，再 `rng.choice` base_stand，再 `rng.choices` 加权 N∈[3,8]，再 uniform 各连续 scale（解析 conditional：tilt_angle 仅 slanted_block、block_width/height 随 block_form + N、bristle N 解析为 1 slide+FIXED）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（含一个 small-N slanted、一个 large-N slanted、一个 upright、一个 horizontal、一个 bristle_insert、一个 pedestal、一个 cast_metal_stand）。


Controlled local parameterization：见 §参数表的 block_width_scale(conditional@block_form,N) / block_depth_scale / block_height_scale(conditional@block_form) / knife_travel_scale / shears_open_scale / tilt_angle_scale(conditional@slanted_block)。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（block_form→holding_mechanism→base_stand）→ 采 knife_count N（angled 加权 [3,8]；bristle 解析为 1 slide + N-1 FIXED）→ 采 independent block_depth/knife_travel/shears_open scale → 派生（block_width 随 N×per-row 刀数 + slot_w；block_height 随 max blade_len；base FIXED origin 随 base 类型）→ 解析 conditional（tilt_angle 仅 slanted；block_width/height 范围随 block_form + N）→ 用 inequality 投影 / 回缩（N 刀 slot 不互撞 ≤ block 宽否则升 block_width、刀坐入不穿底 ≤ block 高、刀抽出不脱轨 ≤ blade_len）。跨部件依赖（刀 slot 排布 vs block 宽、blade_len vs block 高、travel vs blade_len）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏刀 / 剪 / base 的 joint origin、captured 接口、刀复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` block_form / holding_mechanism / base_stand（经兼容矩阵），再 `rng.choices` 加权 N∈[3,8]，再 uniform 各 scale | slot_choices_for_seed 含 `("knife_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **bristle_insert × knife_count**：bristle 只有 1 把 chef 独立 PRISMATIC（松散软杆无法各自锚 prismatic 子件），其余 N-1 是 FIXED inline visual → bristle_insert 下 N 解析为「1 slide + N-1 FIXED」，**不**展开 N 个独立 slide（joint 维度退化但仍 ≥1 非 fixed joint + shears 2 关节）。(2) **block_form × holding_mechanism**：bristle_insert 在 3 种 block_form 上都用中空 housing（替换实心 block_shell），horizontal_bar × bristle 罕见但几何可行（长 housing）→ 默认允许；若首版收窄，可 gate bristle 仅配 slanted/upright（reviewer 决定）。(3) **block_form × base_stand**：三 base 均与三 block_form 正交（feet/pedestal/stand 只换 block 下方），任意组合允许；horizontal_bar 长低本就贴台面，配 pedestal/stand 罕见但允许。(4) **N 上限 × block_form**：N=8 需 block 加宽（block_width_scale 上探或 per-row 2 行各 4）；horizontal_bar 单行 N=8 需 bar 加长（block_width_scale 沿 X）→ inequality 守不互撞。(5) **shears 恒存在**（每个候选都保留 shears slide+pivot 作第二非 fixed-joint 锚）。 | 无 floating / collision / 刀互撞 / 刀穿 block 底 / 刀抽出脱轨 / base FIXED origin 偏离接触面 / bristle 误发 N 个 slide |
| controlled local variation | 6 个 clamped scale（block_width@form,N、block_depth、block_height@form、knife_travel、shears_open、tilt_angle@slanted），每 build 统一；block_width/height/tilt 为 conditional | 比例变化不破坏刀 / 剪 / base joint origin、captured 接口、刀坐入 / 抽出、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| block_form | 3 | yes | yes | slanted/upright/horizontal（3 种主壳几何 + slot 轴）|
| holding_mechanism | 2 | yes | no | angled_prismatic_slots / bristle_insert（2 个，**已 ≥2 满足硬约束下限**；样本池只有这两种真实持刀机构，bristle 是唯一非 milled-slot 候选；降到 2 的理由：5★ 池中 holding_mechanism 轴仅 1 个 fork（mech_bristle），实心铣 slot 是 5 个样本的共有机构 → 真实结构家族只有「实心铣 slot」与「中空刷毛」两类，无第三种有源候选）|
| base_stand | 3 | yes | yes | rubber_feet / sculptural_pedestal / cast_metal_stand（无 base / pedestal FIXED / stand FIXED）|
| knife_count (N) | 6（采样域 {3,4,5,6,7,8}，4/5/6 高频 / 8 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("knife_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [3,8]
- `resolve_config` 把 knife_count clamp 到 [3,8]，各 scale clamp 到声明范围；block_width/height / tilt_angle 为 conditional 随 block_form / N 解析；三条 clearance inequality（刀 slot 不互撞、刀坐入不穿底、刀抽出不脱轨）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（bristle_insert × N → 1 slide + N-1 FIXED inline，不发 N 个 slide；N=8 加宽 block；shears 恒存在）
- 连续 scale clamp 后不破坏刀 / 剪 / base joint origin、captured 接口、刀坐入 / 抽出、N 复制
- 关键 joint：每 `knife_{i}_slide` PRISMATIC axis≈(0,0,1)（局部）+ rpy 随 block_form（slanted pitch≈-12° / upright 无 / horizontal roll≈75°）；`shears_slide` PRISMATIC（slanted/horizontal axis≈(0,0,1)+rpy / upright axis≈(1,0,0)）；`shears_pivot` REVOLUTE（slanted/horizontal axis≈(1,0,0) / upright axis≈(0,0,1)）lower=0 upper≈0.70；base FIXED `pedestal_to_block`/`stand_to_block`（仅 pedestal/stand）
- captured 接口：element-scoped `allow_isolated_part`（每 `knife_{i}` + `shears_inner_half` + `shears_outer_half`，gravity-seated clearance fit）+ horizontal_bar 的 `allow_overlap(holder_shell, knife_{i}_steel/_grip)` solid-proxy sleeve + bristle 的 `allow_overlap(housing_shell, chef_steel)` + cast_metal_stand 的 `allow_overlap`+`expect_contact(stand_frame, foot_{i})`，照搬各样本 run_tests 段
- copied object 遵循 `knife_{i}` / `knife_{i}_steel` / `knife_{i}_slide` 命名 + 绝对式 (x,y) placement（两行 / 单行随 block_form）+ 刀身渐变（chef→paring）
- grandfather：所有刀 / 剪 captured-slide、剪 captured-pin、base FIXED 接口省略 MatingContract，由 origin 检查 + allow_* 守

## Reject cases

- 把 knife_count 当普通 int 参数、不进 slot_choice → 不同刀数 slot_choice 同形，损失主多重性维度（违反 §8/§9 硬要求）。
- **沿用 parent / base_metal_stand 的 `for kname, spec in KNIVES.items()` dict 形 hand-named（chef_knife/paring_knife_0…）而非 index loop `knife_{i}`** → 违反 source map §2.0 / FORK_VARIANTS（模板必须用 `for i in range(N): knife_{i}` + 共享 `_knife_steel`/`_knife_grip` helper）。
- bristle_insert 误发 N 个独立 PRISMATIC slide（松散软杆无法各自锚 prismatic 子件）→ 必须 gate 为 1 chef slide + N-1 FIXED inline visual（违反 §9 矩阵 (1)）。
- 把刀 / 剪当非移动 visual 不发 joint，或某候选 0 个非 fixed joint → 每候选必须 ≥1 非 fixed joint（angled: N 个 knife slide；bristle: 1 chef slide）+ shears slide+pivot（违反 ≥1 非 fixed joint 底线）。
- 刀 rest pose 设成抽出态而非 q=0 坐入 slot（把柄露出顶）→ current-pose 与 viewer 目检不符（所有样本闭合姿态 lower=0）。
- knife slide / shears / base FIXED origin 放在 block 中心或任意点而非真实 slot mouth / pocket / base 接触面 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- N 刀 slot 排布超出 block 宽 / 互撞 → §7 第一条不等式 FAIL；须升 block_width_scale（如 count_8）或缩 slot_w / 拒绝重采。
- 刀 blade_len 超 block 高致穿底 → §7 第二条不等式 FAIL；须升 block_height 或缩 blade_len。
- 给 captured-slide / captured-pin / base FIXED 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_isolated_part/allow_overlap/expect_contact。
- 把连续尺寸 / 颜色 / 材质（palette_style / block scale / tilt 角）当新 candidate 塞进 slot → 不是结构差异。
- 把「single knife / 折叠美工刀 / 餐具收纳筒」语义混入（缺 block 持 N 刀 + 剪的刀座身份）→ 出类。

## 与相邻类别的边界

- 不该混入：**单把厨刀（single knife）**——只是一把 blade+handle+bolster，无 block/holder、无 N 把刀多重性、无厨剪；本类核心是一座 block 持 N 把刀 + 一把剪（相邻小类 `rec_knife_var_*` 样本即此，已排除未采纳）。
- 不该混入：**折叠 / 伸缩美工刀（folding / retractable utility knife）**——单件刀片绕枢轴折叠或沿握把伸缩，是单把刀的机构变体，不是刀座套装（相邻小类 `rec_retractable_utility_knife_*` 即此）。
- 不该混入：**通用工具 / 餐具收纳筒（utensil holder / cutlery caddy / tool crock）**——敞口筒随意插器具，无逐件 slot、无逐刀 PRISMATIC、无渐变刀组 + 厨剪；本类每刀有专属 slot 与独立 slide。
- 不该混入：**磁吸刀条 / 墙挂刀架（magnetic knife bar / wall rack）**——壁挂磁条吸刀，无 block 体、无坐地 base、无机械 slot；本类台面坐地 block/holder。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) holding_mechanism 槽降到 2 个 candidate（angled_prismatic_slots / bristle_insert）是否接受——5★ 池真实持刀机构只有「实心铣 slot」与「中空刷毛」两类，无第三种有源候选；(2) bristle_insert × knife_count 的退化策略（1 chef slide + N-1 FIXED inline，N 仍编 slot_choice 但 joint 维度退化）是否符合 multiplicity 审计期望；(3) N_range 取 [3,8]（与 source map 一致，样本 {4,6,8}，sampler 填 3/5/7）；(4) block_form × bristle_insert 是否全 3 形都允许，还是 gate bristle 仅 slanted/upright；(5) shears 作固定 2-part 第二非 fixed-joint 锚（非多重性轴）是否符合预期；(6) Topology target ~108 接近 ≥300 的说明是否接受；(7) palette_style 5 套 colorway 是否合适）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- 共享 helper：`_knife_steel`/`_knife_grip`/`_knife_rivet_x`/`_grip_loft`（刀几何，N 复制复用同一 helper，count_4 `_build_knife_part` / count_8 `_build_knife` 包装）、`_shears_steel`/`_shears_grip`/`_shears_steel_h`(upright 横向)（剪几何）、`_build_block_solid`(slanted/upright，按 block_form 切换) / `_build_holder_solid`(horizontal) / `_build_housing`+`_build_front_pocket`(bristle)、`_tilted_box`(slanted slot/stand) / `_make_slot_cutter`(horizontal slot)、`_build_pedestal`(revolve) / `_build_stand`(plate+壁+gusset)。
- captured 接口 allow_*：`run_knife_set_tests` 里逐机构补 element-scoped allow（每刀 `allow_isolated_part`；horizontal `allow_overlap(holder_shell,knife_{i}_steel/_grip)`；bristle `allow_overlap(housing_shell,chef_steel)`；剪 inner/outer `allow_isolated_part`；cast_metal_stand `allow_overlap`+`expect_contact(stand_frame,foot_{i})`），照搬各样本 run_tests 段（parent L385-406 / horizontal L407-455 / bristle L419-448 / stand L509-526）。
- **dict→index loop 重构**：parent / base_metal_stand 用 `KNIVES` dict（hand-named）必须改写为 `KNIFE_SPECS` list + `for i in range(N): knife_{i}`（count_4/count_8 已是此形，直接参照）；base_pedestal 用 `for i, spec in enumerate(KNIFE_SPECS)` 但 part 名从 `spec["name"]` 取（仍非 index 名）→ 模板统一用 `f"knife_{i}"`。
- conditional 范围解析顺序：先采 block_form / holding_mechanism / base_stand / N → 解析 bristle 退化（1 slide + N-1 FIXED）/ tilt_angle（仅 slanted）/ block_width 范围（随 form + N）→ 采 block_depth/knife_travel/shears_open independent scale → 派生 block_width(随 N×per-row 刀数)、block_height(随 max blade_len)、base FIXED origin → 投影三条 clearance inequality。
- N 大 / 行布局：slanted/upright 大 N（≥6）用两行（back/front），小 N 可单行；horizontal_bar 恒单行 `_knife_x(i)`（N 大则 bar 沿 X 加长）；per-row 刀数与 block_width 的关系（count_8 每行 4 → BLOCK_WIDTH=0.175）由 helper 解析。
- 参考模板：`agent/templates/Handtools_Tool_cart.py`（同为 multiplicity pattern：固定 named slots + `("drawer_count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 `_drawer_mesh` helper + 兼容矩阵 gating + captured allow_overlap/allow_isolated_part 骨架 + base/root 切换 + N 自适配 band/宽，本类可同构改编——drawer_count↔knife_count、storage_module↔holding_mechanism、caster↔base_stand 的 root/FIXED 切换）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| slanted_block + angled_prismatic_slots + rubber_feet | rec_..._1d3b3a0e | `_build_block_solid` L101-129 / `_tilted_box` L90-98 / `_knife_steel` L143-154 / `_knife_grip` L157-165 / `_knife_rivet_x` L168-175 / knife dict loop+PRISMATIC L265-299 / shears slide+pivot L301-368 / `foot_{i}` L239-246 / logo L248-262 / allow_isolated_part L385-406 | slanted block + 实心铣 slot + rubber feet 基线 + 共享刀 helper + shears slide/pivot 范式 + captured clearance fit |
| S2 | multiplicity（copy-logic 源）| knife_count N=4 | rec_knife_set_var_count_4 | `KNIFE_SPECS` list L56-65 / `_build_knife_part` L219-257 / `for i in range(NUM_KNIVES)` L305-306 / N=4 检查 L440-443 | N=4 copy-logic 源（index loop + `knife_{i}` + 共享 helper 契约）|
| S3 | multiplicity（copy-logic 源）| knife_count N=8 | rec_knife_set_var_count_8 | `KNIFE_SPECS` list L57-76 / `BLOCK_WIDTH=0.175` L41 / `_build_knife` L188-226 / `for i in range(N_KNIVES)` L316-317 / 两行各 4 L525-537 | N=8 copy-logic 源（block 加宽容纳 8 刀、两行各 4 respaced）|
| S4 | A | upright_block | rec_knife_set_var_block_upright | `_build_block_solid`(box) L69-101 / `BLOCK_W/D/H` L32-34 / `KNIFE_POSITIONS` L53-56 / knife loop no-tilt L248-292 / shears_slide axis=(1,0,0) L344-368 / `_shears_steel_h` L191-198 | 竖直方块 form（垂直 slot 直抽 + 横向 shears）|
| S5 | A | horizontal_bar | rec_knife_set_var_block_horizontal_bar | `_build_holder_solid` L113-138 / `_make_slot_cutter` L95-110 / `_knife_x(i)` L91-92 / `JOINT_ROLL` L39 / knife loop roll L281-320 / allow_overlap solid-proxy L414-455 | 长低 bar form（浅 15° 单行 + 75° roll slide + solid-proxy sleeve overlap）|
| S6 | B | bristle_insert | rec_knife_set_var_mech_bristle | `_build_housing`+`_build_front_pocket` L84-113 / `bristle_{i}` grid L251-261 / `FIXED_KNIVES` inline L60-66,L264-287 / 单 `chef_slide` PRISMATIC L292-329 / allow_overlap L419-434 | 中空刷毛持刀机构（1 chef slide + N-1 FIXED inline，N 弱激励退化）|
| S7 | C | sculptural_pedestal | rec_knife_set_var_base_pedestal | `_build_pedestal`(revolve) L138-191 / pedestal part L296-301 / `base_pad_{i}` L304-314 / `pedestal_to_block` FIXED L352-358 | turned 青铜柱底座（root=pedestal + block FIXED on top）|
| S8 | C | cast_metal_stand | rec_knife_set_var_base_metal_stand | `_build_stand`(plate+壁+back+gusset) L134-199 / stand part L301-306 / `stand_front_lip` L308-313 / `stand_to_block` FIXED L351-357 / `expect_contact(stand_frame,foot_{i})` L509-526 | 铸金属角架底座（root=stand + block FIXED in cradle + 落座 contact）|
