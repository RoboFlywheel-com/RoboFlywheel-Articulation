# wooden_tongs (one-piece sprung wooden serving / cooking tongs) — Modular Spec

> 来源小类：`picture/Handtools/wooden tongs`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Handtools_wooden_tongs.md`。
> **"wooden tongs" 在此 = 厨房 / 上菜用的一体弹性木夹（两条长扁木臂，顶端弹簧夹合，捏合闭口夹食物）。不是台钳 / 螺旋夹（clamp，已有独立 slug）、不是钳子 / 老虎钳（pliers）、不是筷子（chopsticks，无铰接闭合机构）。**
> 结构家族 = 两条对称木臂 + 一个把两臂合到一起的闭合机构（顶端金属弹簧夹 / 中段 scissor 销 / 弹簧夹 + 滑动锁环 / 一体弯木弹簧）。**核心运动 = `pivot` REVOLUTE：两臂绕 +Z（垂直于扁臂平面）相对转动，q=0 是松弛张开的 "V"，upper 是捏合闭口。**
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 parent + 2 原始变体 + 6 个新补 gap 变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行读完整、核对）。引用以 part / joint / helper **名字** 为准（`fixed_arm`/`moving_arm`/`arm_{i}` part；`pivot` REVOLUTE / `slide` PRISMATIC joint；`_arm_solid`/`_arm_dowel`/`_arm_with_scoop`/`_clip_solid`/`_pin_solid`/`_ring_solid`/`_bend_solid`/`_grip_nub`/`_finger_scallop` helper；`spring_clip`/`pivot_pin`/`ring_band`/`wood_bend`/`scallop_{i}` visual），行号仅作定位。
>
> **坐标约定（全 9 样本一致，模板直接沿用）**：扁臂躺在 XY 平面（扁面法线 = Z），臂沿 **+X** 从 pivot（x≈0）伸到 tip（x≈ARM_LENGTH=0.300）；两臂在 pivot 处沿 **±Z** 堆叠（fixed 在 −Z、moving 在 +Z，小 clearance gap）；splay 半角 `HALF_SPLAY`(≈7-8.5°) 由 visual / joint 的 `rpy=(0,0,±HALF_SPLAY)` 施加（臂本身建直）；`pivot` REVOLUTE **axis=(0,0,1)**，origin 在堆叠接触面 / clip / pin / bend 处，**lower≈−0.04 / upper≈0.18-0.28**（q=0 张开、upper 闭合、小负 q 更张）。lock_ring 的 `slide` PRISMATIC **axis=(1,0,0)**（沿臂向 tip 滑、锁闭）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `wooden_tongs` |
| template path | `agent/templates/Handtools_wooden_tongs.py` |
| test path (optional) | `tests/agent/test_wooden_tongs_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定根臂 `fixed_arm`/`arm_0`；`moving_arm`/`arm_1` 经 `pivot` REVOLUTE 挂根臂；close_mechanism 决定连接硬件 + 可选 `slide_ring` PRISMATIC 并列挂根臂；arm_shape / grip_detail 是改写两臂 mesh / 装饰层，arm 数恒为 2 经共享 helper 发射，**非 multiplicity 轴**）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 2 原始变体 + 6 新补 gap 变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 9 个样本）**：两条对称扁木 / 圆木臂 + 一个 `pivot` REVOLUTE（axis=(0,0,1)）把两臂铰接到一起；q=0 松弛张开 "V"、upper 捏合闭口。所有样本的 `run_tests` 都验同一套：pivot is revolute、axis Z（`abs(ax[2])>0.99` 且 x/y≈0）、两臂 ~0.30m 长扁条、tips 张开在 ±Y、upper 闭 / lower 张、`expect_origin_distance(两臂, xy, max≈0.012-0.020)`。
- **Slot A close_mechanism 轴**：是连接硬件 part / joint 数 / joint 拓扑变化（**真正的拓扑轴之一**）。
  - onepiece_spring_clip（parent）：`fixed_arm`(root) + `moving_arm`(child)，根臂带 `spring_clip` 金属 box visual 桥接两臂顶端（parent L142-147），`pivot` REVOLUTE origin 在堆叠面（L167-179）。**1 REVOLUTE，金属 clip = 根臂 visual 无独立 joint。**
  - scissor_pin：`arm_0`/`arm_1`（`for i in range(2)` 循环发射，L128-136）于 **中段** 交叉，根臂带 `pivot_pin` 圆柱 visual（`_pin_solid` L98-105）竖直穿两臂；`pivot` REVOLUTE origin=(0,0,0) 在交叉面（L152-162），臂两侧分短把手段 / 长 tip 段（`HANDLE_LENGTH=0.110` / `TIP_REACH=0.190`）；销穿臂 `allow_overlap(pivot_pin, strip_1)`（L175-179）。**1 REVOLUTE，pin 在中段（非顶端）。**
  - spring_clip_with_lock_ring：parent 拓扑（spring_clip + `pivot` REVOLUTE）**外加** `slide_ring` 独立 part（`_ring_solid` 矩形 bore 套两臂，L132-154）+ `slide` PRISMATIC axis=(1,0,0)（L271-281，lower=0 / upper=RING_TRAVEL=0.100）滑向 tip 锁闭；ring 外环 4 个 cardinal `grip_{i}` 凸脊（`_grip_nub` helper + `for i in range(N_GRIPS=4)` L255-266）；ring bore 锁紧 `allow_overlap(ring_band, *_arm_strip)`（L460-469）。**1 REVOLUTE + 1 PRISMATIC（+1 独立 part），是唯一带 2 个非 fixed joint 的候选。**
  - onepiece_bend：**无金属件** —— 顶端是一体弯木 U / 发夹弯（`_bend_solid` 矩形截面绕 +Y revolve 180°，半环 torus，L94-131），`wood_bend` 作根臂 visual，弯折处即弹簧；`pivot` REVOLUTE origin=(0,0,BEND_RADIUS)（L193-206）；`run_tests` **显式断言无金属材质、无 `spring_clip` visual**（L285-304）+ 弯木 −X 外弯（L279-283）；junction `allow_overlap(wood_bend, arm_strip_1)`（L340-345）。**1 REVOLUTE，无金属，弯木 = 根臂 visual。**
- **Slot B arm_shape 轴**：是两臂 **mesh-profile / 截面 / tip 形态** 变化（不改 part / joint 拓扑，两臂仍各一 part + 1 REVOLUTE）。
  - flat_paddle（parent 基线）：`_arm_solid` 扁条 polyline 外扩到宽圆 paddle 头（`TIP_WIDTH=0.030`，L54-98）。
  - round_dowel：`_arm_dowel` 圆截面 dowel（`_circle_section` + `section_loft` 经 `mesh_from_geometry`，需多 import `section_loft`/`mesh_from_geometry` L31-32；profile 半径 DOWEL_ROOT/SHAFT/TIP_R，L77-100）；run_tests 验 dowel Z 跨 ~直径而非扁厚（L248-261）；clip 桥接 `allow_overlap(spring_clip, arm_1_dowel)`（L313-318）。
  - straight_slat：`_arm_solid` 用 `cq.rect(ARM_LENGTH, ARM_WIDTH)` 等宽矩形（L65-70，无 paddle 外扩）；run_tests 验等宽 / 窄 slat 比例（L217-253）。
  - spoon_ends：`_arm_with_scoop` shaft + 加厚加宽 bowl（`_bowl_half_profile` 正弦凸 L81-112）union 后用 `sphere` cut 凹勺（dish，L121-184）；**`dish_up` 标志**让两臂凹面相对（fixed dish_up=True、moving dish_up=False，L218/L237）；run_tests 验 bowl 比 shaft 厚 / 宽（L315-338）。
  - square_ends：`_arm_solid` 同 flat_paddle 但 tip 段保持满宽到方头平切（无收尾圆角，L54-102，hold full TIP_WIDTH to L82）；run_tests 验 tip 满宽方切（L260-276）。
- **Slot C grip_detail 轴**：是臂表面 **module-internal 装饰层**（不改 part / joint 拓扑；脊作 part visual 无独立 joint）。
  - plain（parent 基线）：光臂，仅周边 fillet（`_arm_solid` L95 的 `edges("|Z").fillet`）。
  - scalloped_grip：握持段一排 scalloped 手指凹槽脊 —— `_finger_scallop`（半圆柱凸脊沿 Y，L126-144）+ `_finger_scallop_inverted`（下面反向，L147-160），`for i in range(N_SCALLOPS=6)` 在 **两臂的上下两面** 等距发射（`scallop_{i}`/`scallop_bot_{i}`，spacing=0.016，L213-250）；均为 part visual（无独立 joint，Rule 1）；run_tests 验每脊存在 + 在握持段 + 等距（L372-422）。

## 核心身份

一只**一体弹性木质上菜 / 厨房夹**（sprung wooden serving / cooking tongs）：两条长（~0.30m）对称的扁 / 圆木**臂**，从一端的闭合机构伸出、splay 成松弛张开的 "V"，另一端是稍宽的 paddle / 圆头 / 方头 / 勺斗 tip 用来夹食物；捏合两臂绕顶端 / 中段 **pivot** 转动，把两 tip 合到一起夹住食物。闭合机构有四类：顶端金属**弹簧夹**（spring clip 桥接两臂，捏合即回弹）/ 中段 **scissor 销**（两臂交叉过一根圆销，短把手 + 长 tip 在销两侧）/ 弹簧夹 + **滑动锁环**（额外一只木 collar 沿臂 PRISMATIC 滑向 tip 把张开的臂锁死）/ 一体**弯木**（顶端连续 U / 发夹弯本身即弹簧，无金属件）。臂形有 paddle / dowel / 等宽直条 / 方头 / 勺斗五种；握持段可光面或刻 scalloped 指槽。默认成熟域：close_mechanism(4) × arm_shape(5) × grip_detail(2) 的笛卡尔积。活动语义 = **两臂绕 +Z 相对转动开合**（核心 REVOLUTE `pivot`，全候选共享）+ 仅 lock_ring 时的 **锁环 PRISMATIC `slide`**（沿 +X 滑向 tip）。

不该混入：
- **螺旋驱动手用夹 / C 形夹 / 台钳（clamp / vise）**——靠螺杆竖直 PRISMATIC 进给夹工件、有 C 形 frame，主运动 spine 完全不同；已有独立 slug `clamp`。
- **钳子 / 老虎钳 / 剪刀（pliers / scissors）**——双臂绕中心 pivot 剪切金属 / 切割，是金属工具且把手在销另一侧成对称剪式；本类是木质食物夹（scissor_pin 候选虽中段销，但仍是松弛张开夹食的木夹，非金属剪切工具）。
- **筷子（chopsticks）**——两根独立无铰接的木棍，没有把两根连到一起的闭合机构 / 弹簧 / 销 / 弯木，无 `pivot` REVOLUTE；缺这套即出类。
- **kitchen / serving 金属夹（metal kitchen tongs）的硅胶头 / 锁扣环**——本类是**木**夹（材质 / palette 是木 + 少量金属 clip / pin）；金属厨房夹的不锈钢臂 + 硅胶头 + 端部锁扣是另一形态家族（如需可作单独 slug）。

## 槽位 + 候选模块表

> **建模注记**：`arm_shape`（Slot B）是两臂**同一对 mesh 的截面 / tip 足迹形态**（flat-paddle / dowel / 直条 / 方头 / 勺斗），由 arm mesh helper 一次决定、两臂共用同一 helper、**不改 part 树 / joint 拓扑**（两臂仍各一 part + 单 `pivot` REVOLUTE）。`grip_detail`（Slot C）是臂表面 module-internal 装饰层（光面 / scalloped 脊，脊作 part visual 无独立 joint），也不改拓扑。**`close_mechanism`（Slot A）才是改连接硬件 part 数 / joint 数 / joint 拓扑的主轴**（金属 clip visual / 中段 pin visual / +独立 `slide_ring` part + PRISMATIC / 弯木 visual 无金属）。三轴共同撑开多样性（见 §9）。

### Slot A：close_mechanism（闭合机构 / pivot —— **主机构槽**，决定两臂如何连接 + part / joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| onepiece_spring_clip（基线）| rec_build-...-wood_...c58cac31（parent）| `fixed_arm`/`moving_arm` part L130-159 + `_clip_solid` L101-116 + `spring_clip` visual L142-147 + `pivot` **REVOLUTE** axis=(0,0,1) L167-179 | eligible if compatible | 顶端金属弹簧夹：根臂 `fixed_arm` 带 `spring_clip` 金属 box visual（桥接两臂顶端 x≈0，跨两臂 Z 堆叠），`moving_arm` 经 `pivot` REVOLUTE（origin 堆叠面 `(0,0,arm_stack)`，rpy −HALF_SPLAY）铰接；**1 REVOLUTE，clip 是根臂 visual 无独立 joint**；q=0 张开 / upper 闭 |
| scissor_pin | rec_wooden_tongs_var_scissor_pin | `arm_{i}` `for i in range(2)` part L128-136 + `_pin_solid` 圆柱 L98-105 + `pivot_pin` visual L140-145 + `pivot` **REVOLUTE** origin=(0,0,0) L152-162 | eligible if compatible | 中段交叉销：两臂在 **partway**（非顶端）交叉，根臂 `arm_0` 带 `pivot_pin` 圆柱竖直穿两臂；臂被销分短把手段（`HANDLE_LENGTH=0.110`，−X）+ 长 tip 段（`TIP_REACH=0.190`，+X）；**1 REVOLUTE**；销穿 moving 臂 `allow_overlap(pivot_pin, strip_1)` L175-179；run_tests 验销在中段（handle_side>0.05 且 tip_side>0.05）L225-235 + 销圆截面 L237-244 |
| spring_clip_with_lock_ring | rec_wooden_tongs_var_lock_ring | parent 拓扑 + `slide_ring` part L237-266 + `_ring_solid` L132-154 + `slide` **PRISMATIC** axis=(1,0,0) L271-281 + `_grip_nub`+`grip_{i}` `for i in range(4)` L157-167, L255-266 | eligible if compatible | 弹簧夹 + 滑动锁环：parent（spring_clip + `pivot` REVOLUTE）**外加** `slide_ring` 独立木 collar（矩形 bore 套两臂）沿 **+X PRISMATIC** 滑向 tip 锁闭（lower=0 / upper=RING_TRAVEL=0.100）；ring 外环 4 个 cardinal `grip_{i}` 凸脊（共享 `_grip_nub`）；**1 REVOLUTE + 1 PRISMATIC + 1 独立 part**；ring 锁紧 `allow_overlap(ring_band, fixed/moving_arm_strip)` L460-469 |
| onepiece_bend | rec_wooden_tongs_var_onepiece_bend | `_bend_solid` revolve 半环 L94-131 + `wood_bend` 根臂 visual L181-186 + `pivot` **REVOLUTE** origin=(0,0,BEND_RADIUS) L193-206；**无金属材质 / 无 spring_clip** | eligible if compatible | 一体弯木：顶端连续 U / 发夹弯（矩形截面绕 +Y revolve 180°，向 −X 外弯）作根臂 `wood_bend` visual，弯折即弹簧，**无任何金属件**；`pivot` REVOLUTE（弯木与 moving 臂 junction）；run_tests **显式断言无 metal 材质（L285-294）+ 两臂均无 `spring_clip` visual（L296-304）+ 弯木 −X 外弯（L279-283）**；junction `allow_overlap(wood_bend, arm_strip_1)` L340-345 |

### Slot B：arm_shape（臂截面 / 端头形态 —— mesh-profile 维度，不改 part / joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_paddle（基线）| rec_build-...-wood_...c58cac31（parent）| `_arm_solid` 扁条 polyline + paddle 外扩 L54-98 | eligible if compatible | 扁 tapered 木条，外扩到宽圆 paddle 头（`TIP_WIDTH=0.030`，圆角收尾）；扁厚 `ARM_THICKNESS=0.0045`；默认形态 |
| round_dowel | rec_wooden_tongs_var_round_dowel | `_circle_section` L63-74 + `_arm_dowel` `section_loft` L77-100（`mesh_from_geometry`/`section_loft` import L31-32）| eligible if compatible | 圆木 dowel 截面（圆形 cross-section loft，半径 DOWEL_ROOT_R=0.005→SHAFT=0.006→TIP=0.008），端头圆头；run_tests 验 dowel Z 跨 ~直径而非扁厚 L248-261；clip 桥接 `allow_overlap(spring_clip, arm_1_dowel)` + `expect_contact` L313-324 |
| straight_slat | rec_wooden_tongs_var_straight_slat | `_arm_solid` `cq.rect(ARM_LENGTH, ARM_WIDTH)` L65-70 | eligible if compatible | 全长等宽直扁条（`ARM_WIDTH=0.022`，无 paddle 外扩、无 taper），方头平切微圆角；run_tests 验等宽 / 窄 slat 比例（y_span<0.25·len）L217-253 |
| spoon_ends | rec_wooden_tongs_var_spoon_ends | `_shaft_half_profile` L67-78 + `_bowl_half_profile` L81-112 + `_arm_with_scoop` `sphere` cut L121-184 | eligible if compatible | 沙拉夹式凹勺 / 铲斗 tip：shaft + 加厚加宽 bowl（`BOWL_THICK=0.008`/`BOWL_WIDTH=0.040`）union 后用 `sphere` cut 凹 dish（`DISH_DEPTH=0.004`）；**`dish_up` 标志**让两臂凹面相对（fixed=True/moving=False）；run_tests 验 bowl 比 shaft 厚 / 宽 L315-338 + clip overlap L397-420 |
| square_ends | rec_wooden_tongs_var_square_ends | `_arm_solid` tip 满宽方切 L54-102（hold full TIP_WIDTH to L82，极小 fillet 0.0006）| eligible if compatible | 方头平切 paddle：tip 外扩到满 `TIP_WIDTH` 后保持满宽到方头平切端（无收尾圆角 / 钝端）；run_tests 验 tip 满宽（>=TIP_WIDTH·0.85）L260-276 |

### Slot C：grip_detail（握持段表面装饰 —— module-internal 层，不改 part / joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain（基线）| rec_build-...-wood_...c58cac31（parent）| `_arm_solid` 仅周边 `edges("|Z").fillet(0.0010)` L93-97 | eligible if compatible | 光滑木臂，无握持脊 / 槽，仅扁面周边小 fillet 读作磨损木；所有 parent / 多数变体的退化情形 |
| scalloped_grip | rec_wooden_tongs_var_scalloped_grip | `_finger_scallop` L126-144 + `_finger_scallop_inverted` L147-160 + `for i in range(N_SCALLOPS=6)` `scallop_{i}`/`scallop_bot_{i}` 两臂上下面 L213-250 | eligible if compatible | 握持段一排 scalloped 指槽脊：半圆柱凸脊（沿 Y，`RIDGE_R=0.0020`，跨 ~72% 臂宽）+ 反向脊，`for i in range(6)`（spacing=0.016，从 GRIP_START_X=0.085 起）在**两臂上下两面**等距发射，均为 **part visual（无独立 joint，module-internal for-loop，Rule 1）**；run_tests 验每脊存在 + 在握持段 + 等距 L372-422 |

> 降级理由（Slot C 仅 2 candidate）：fork 池握持装饰只有 parent 的 plain 光面 + scalloped_grip 指槽两个真实收敛形态；现实木夹握持装饰词汇表本身窄（光面 / 指槽脊为主，少量品牌 logo 烙印 / 滚花属纯纹理非结构）。grip_detail 是 mesh / visual 装饰维度（非改拓扑轴），2 candidate 已满足 schema ≥2 硬约束。审核如需扩容应回 fork 池补造真实结构形态（如交叉 cross-hatch 滚花脊、纵向指沟槽、烙印 brand panel），不在模板侧虚构。Slot A(4) × Slot B(5) 已提供主拓扑 / mesh 多样性，Slot C ×2 充裕（见 §9）。

## 槽位图（slot graph）

pattern: parallel_children（固定根臂 `fixed_arm`/`arm_0`；`moving_arm`/`arm_1` 经 `pivot` REVOLUTE 挂根臂；close_mechanism 决定连接硬件 visual + pivot origin + 可选 `slide_ring` PRISMATIC 并列挂根臂；arm_shape 换两臂 mesh helper；grip_detail 在两臂上加 module-internal 脊 visual）

```
fixed_arm / arm_0 (root, 坐 pivot 端; 由 close_mechanism 决定连接硬件 visual + 由 arm_shape 决定臂 mesh + 由 grip_detail 加脊)
  │
  ├── moving_arm / arm_1 ──[pivot: REVOLUTE axis=(0,0,1), origin=堆叠面/clip/pin/bend 处, rpy=(0,0,−HALF_SPLAY)]  ← 全候选共享主开合运动
  │      （q=0 松弛张开 "V"、upper 捏合闭口、小负 q 更张；两臂 ±Z 堆叠 + ±HALF_SPLAY 反向 splay）
  │
  ├── [close_mechanism slot 的连接硬件]  (四选一，决定 pivot 接口 + 是否多 part/joint)
  │     ├─ onepiece_spring_clip : spring_clip = 根臂金属 box visual（桥接两臂顶端 x≈0），pivot origin=(0,0,arm_stack)
  │     ├─ scissor_pin          : pivot_pin = 根臂圆柱 visual（中段竖直穿两臂），pivot origin=(0,0,0) 交叉面；臂分短把手+长 tip
  │     ├─ spring_clip_with_lock_ring : spring_clip（同上）+ slide_ring(独立 part) ──[slide: PRISMATIC axis=(1,0,0), origin=(RING_REST_X,0,0)]
  │     └─ onepiece_bend        : wood_bend = 根臂木弯 visual（无金属，−X 外弯），pivot origin=(0,0,BEND_RADIUS)
  │
  ├── [arm_shape slot 换两臂 mesh helper]  (五选一，两臂共用同一 helper)
  │     └─ flat_paddle(_arm_solid 扩) / round_dowel(_arm_dowel section_loft) / straight_slat(_arm_solid rect)
  │        / spoon_ends(_arm_with_scoop sphere-cut, dish_up 标志) / square_ends(_arm_solid 满宽方切)
  │
  └── [grip_detail slot 加握持脊 visual]  (二选一)
        ├─ plain          : 无脊（仅周边 fillet）
        └─ scalloped_grip : scallop_{i}/scallop_bot_{i} i∈range(N_SCALLOPS=6) 在两臂上下面（part visual, 无 joint, Rule 1）
```

接口点位与 joint 语义：
- **fixed_arm → moving_arm（pivot，全候选共享）**：mating = 两臂在 pivot 端的堆叠接触面 / 连接硬件。REVOLUTE **axis=(0,0,1)**（扁臂平面法线），origin 由 close_mechanism 决定（spring_clip / lock_ring：`(0,0,arm_stack)` 堆叠面；scissor_pin：`(0,0,0)` 交叉面；bend：`(0,0,BEND_RADIUS)` 弯木顶），rpy=(0,0,−HALF_SPLAY) 使 q=0 即成松弛张开 "V"。**motion_limits lower≈−0.04 / upper≈0.18（spring_clip 族）或 0.28（scissor）**（q=0 张开、upper 闭合、小负 q 更张）。两臂 `expect_origin_distance(fixed, moving, xy, max≈0.012-0.020)`（铰接共原点）。
- **close_mechanism 连接硬件 → 根臂**：硬件作根臂 visual（captured / inline）。
  - onepiece_spring_clip：`spring_clip` 金属 box 跨两臂 Z 堆叠（桥接 x≈0），是根臂 visual 无独立 joint。
  - scissor_pin：`pivot_pin` 圆柱竖直穿两臂中段，是根臂 visual；销穿 moving 臂 `allow_overlap(pivot_pin, strip_1)` + `expect_overlap`（xy）+ `expect_gap`（两臂 strip 在 Z 分离 0.0005-0.005）。
  - onepiece_bend：`wood_bend` 半环 torus 是根臂 visual（无金属）；junction `allow_overlap(wood_bend, arm_strip_1)` + `expect_overlap`（Y 共享 junction 宽）。
- **slide_ring → 根臂（仅 spring_clip_with_lock_ring）**：mating = ring 矩形 bore 套两臂。PRISMATIC **axis=(1,0,0)**，origin=(RING_REST_X=0.040, 0, 0)（近 pivot），lower=0 / upper=RING_TRAVEL=0.100（滑向 tip 锁闭）；ring bore 套两臂 `expect_overlap(arm_strip, ring_band, yz, min=0.004)`（rest 与 upper 均套住）+ 锁紧 `allow_overlap(ring_band, fixed/moving_arm_strip)`；4 个 `grip_{i}` 凸脊是 ring visual（无 joint）。其余 close_mechanism **无此 part / joint**。
- **arm_shape → 两臂**：两臂共用同一 mesh helper（round_dowel 经 `mesh_from_geometry`+`section_loft`，其余经 `mesh_from_cadquery`）；spoon_ends 用 `dish_up` 标志让两臂凹面相对（不改 part / joint）。
- **grip_detail → 两臂**：scalloped_grip 的脊作两臂 part visual，`for i in range(6)` module-internal，无独立 joint（Rule 1）。
- **mating policy**：所有连接接口（clip 桥接、pin 穿臂、bend junction、ring bore 套臂）是 captured / bridging（销 / 杆 / 弯 / 环嵌入或桥接），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 pivot / slide origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：`pivot` q=0（张开 "V"，tips 在 ±Y）；`slide` q=0（ring 近 pivot 松弛）。
- **互斥 / 可选 / 派生**：close_mechanism 四候选互斥（一次一种闭合机构）；scissor_pin 与 onepiece_bend 是同 Slot A 的不同顶 / 中机构，天然互斥（Slot A 单选，见 §排除项）；spring_clip_with_lock_ring 独有 `slide_ring` part + `slide` PRISMATIC（其余无）；onepiece_bend 独有"无金属"约束（其余有金属 clip / pin）。arm_shape 与 grip_detail 与 close_mechanism 正交（任意组合合法，仅尺寸 / 接口联动，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / close_mechanism — onepiece_spring_clip（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_arm`(root, visual: arm strip + `spring_clip` 金属 box) + `moving_arm`(child, visual: arm strip) | parent L130-159 |
| internal joints | `pivot` REVOLUTE axis=(0,0,1)，origin=(0,0,arm_stack) rpy=(0,0,−HALF_SPLAY)，lower=−0.04 / upper=0.18 | parent L167-179 |
| upstream interface | root（坐 pivot 端，无父）| — |
| downstream interface | 堆叠接触面 + `spring_clip` 桥接（供 moving_arm REVOLUTE + lock_ring slide_ring 接入）| parent L142-147 |

### Slot A / close_mechanism — scissor_pin
| emits | 描述 | 来源 |
|---|---|---|
| parts | `arm_0`(root, `for i in range(2)` 发射 + `pivot_pin` 圆柱 visual) + `arm_1`(child) | scissor L128-145 |
| internal joints | `pivot` REVOLUTE axis=(0,0,1)，origin=(0,0,0) 交叉面，lower=−0.05 / upper=0.28 | scissor L152-162 |
| upstream interface | `pivot_pin` 中段竖直穿两臂（captured，`allow_overlap(pivot_pin, strip_1)` + `expect_gap` 两臂 Z 分离）| scissor L140-145, L175-194 |

### Slot A / close_mechanism — spring_clip_with_lock_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | parent 两臂 + `spring_clip` + `slide_ring`(独立 part, visual: `ring_band` + `grip_{i}`×4) | lock_ring L130-266 |
| internal joints | `pivot` REVOLUTE（同 parent）+ `slide` PRISMATIC axis=(1,0,0)，origin=(0.040,0,0)，lower=0 / upper=0.100 | lock_ring L218-230, L271-281 |
| upstream interface | ring 矩形 bore 套两臂（`expect_overlap(arm_strip, ring_band, yz)` rest+upper；`allow_overlap(ring_band, *_arm_strip)` 锁紧）| lock_ring L426-483 |

### Slot A / close_mechanism — onepiece_bend
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_arm`(root, visual: arm strip + `wood_bend` 半环, **无金属**) + `moving_arm`(child) | bend L162-186 |
| internal joints | `pivot` REVOLUTE axis=(0,0,1)，origin=(0,0,BEND_RADIUS)，lower=−0.04 / upper=0.18 | bend L193-206 |
| upstream interface | 弯木 junction（moving 臂 seat 入弯，`allow_overlap(wood_bend, arm_strip_1)`）；**断言无 metal 材质 / 无 spring_clip visual** | bend L285-304, L340-345 |

### Slot B / arm_shape（以 flat_paddle 为例；其余仅换 mesh helper，两臂共用）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 两臂 strip mesh（无独立 part，arm mesh 作两臂 visual）| parent `_arm_solid` L54-98 / dowel `_arm_dowel` L77-100 / slat rect L65-70 / spoon `_arm_with_scoop` L121-184 / square L54-102 |
| internal joints | 无（arm_shape 不改 joint）| — |
| upstream interface | 两臂 mesh 共用同一 helper；round_dowel 经 `mesh_from_geometry`+`section_loft`，其余 `mesh_from_cadquery`；spoon `dish_up` 标志两臂凹面相对 | dowel L31-32, L136 / spoon L218, L237 |

### Slot C / grip_detail — scalloped_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`scallop_{i}`/`scallop_bot_{i}` 为两臂 visual）| scalloped L210-250 |
| internal joints | 无（Rule 1，脊非移动件）| — |
| placement | `for i in range(N_SCALLOPS=6)` 在两臂上下两面等距（x=GRIP_START_X+i·SPACING；fixed 臂的脊还需 cos/sin splay 旋转对齐 L206-235）| scalloped L213-250 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| close_mechanism | enum | onepiece_spring_clip / scissor_pin / spring_clip_with_lock_ring / onepiece_bend | onepiece_spring_clip | choice | 由 deterministic procedural sampler 选；lock_ring 独带 `slide` PRISMATIC + `slide_ring` part；bend 独带"无金属"约束 | Slot A 表 |
| arm_shape | enum | flat_paddle / round_dowel / straight_slat / spoon_ends / square_ends | flat_paddle | choice | sampler 选；只换两臂 mesh helper（共用），不改 part/joint | Slot B 表 |
| grip_detail | enum | plain / scalloped_grip | plain | choice | sampler 选；scalloped 加 module-internal 脊 visual（无 joint）| Slot C 表 |
| palette_style | enum | natural_birch / walnut_stained / cherry_warm / painted_white / bamboo_blond / ebony_dark | natural_birch | palette | palette only，**不计入 slot_choice**；每 seed 采一套（木色 + 金属 clip/pin 色，见下表）| 各样本材质 |
| arm_length_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 `ARM_LENGTH`（pivot→tip 全长）→ 联动握持段 / paddle 起点、脊排布 X，clamp | parent L33 |
| arm_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放臂宽（`MID_WIDTH`/`TIP_WIDTH`/`ARM_WIDTH`/`DOWEL_*_R`/`BOWL_WIDTH`）保扁条 / dowel 比例，clamp | parent L35-37 |
| arm_thickness_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放扁厚 `ARM_THICKNESS`（dowel 不适用，见 conditional）→ 联动 Z 堆叠 offset / clip span，clamp | parent L34 |
| splay_angle_scale | float | [0.80, 1.15] | 1.0 | independent | 缩放 `HALF_SPLAY`（rest 张开 V 半角）保 tips 仍读作张开（≥5°），clamp | parent L42 |
| pivot_close_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 `pivot` REVOLUTE upper（捏合行程）保 upper 闭合后两 tip 真合拢（不穿越中线过头），clamp | parent L177 |
| dowel_radius_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 arm_shape=round_dowel 有效；缩放 dowel 半径（保 Z 堆叠 + clip span 容纳），clamp | dowel L42-44 |
| bowl_dish_scale | float | [0.80, 1.15] | 1.0 | conditional | 仅 arm_shape=spoon_ends 有效；缩放 `DISH_DEPTH`/`DISH_RADIUS`（保 dish 不切穿 bowl 厚），clamp | spoon L45-46 |
| ring_travel_scale | float | [0.80, 1.10] | 1.0 | conditional | 仅 close_mechanism=lock_ring 有效；缩放 `slide` upper（保 ring 滑到 tip 前止、不滑出臂）| lock_ring L63 |
| scallop_count | int | [4, 8]（仅 grip_detail=scalloped_grip）| 6 | conditional | 仅 scalloped 有效；握持段指槽脊数（module-internal 装饰阵列，**不计入 slot_choice**，见 §8）| scalloped L50 |
| scallop_spacing_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 scalloped 有效；缩放脊间距（保 scallop_count 排布不超握持段）| scalloped L51 |
| (—) | constraint | — | — | inequality | 闭合行程不过头：`pivot_upper·pivot_close_scale` 使 upper 时两 tip 合拢（gap≈0）但不互相穿越过中线；违反按比例缩 upper | parent L260-268 |
| (—) | constraint | — | — | inequality | scissor_pin 销在中段：销 X 中心两侧 handle_side>0.05 且 tip_side>0.05（销不退化到端）；arm_length_scale 缩放时保此带 | scissor L225-235 |
| (—) | constraint | — | — | inequality | lock_ring 不滑出：`RING_REST_X + slide_upper·ring_travel_scale ≤ ARM_LENGTH·arm_length_scale − ring_len − margin`（ring 滑到 tip 前止）；违反缩 slide upper | lock_ring L62-63 |
| (—) | constraint | — | — | inequality | ring bore 容纳两臂：`RING_BORE_Y/Z ≥ 两臂堆叠 + clearance`（width/thickness scale 缩放时保 bore 仍套住）；圆截面 dowel × ring 见 §9 兼容矩阵 | lock_ring L57-58 |
| (—) | constraint | — | — | inequality | spoon dish 不切穿：`DISH_DEPTH·bowl_dish_scale < BOWL_THICK − wall_min`（凹勺不挖穿 bowl 底）；违反缩 DISH_DEPTH | spoon L42, L166-176 |
| (—) | constraint | — | — | inequality | scallop 排布不超握持段：`scallop_count·SPACING·scallop_spacing_scale ≤ (paddle_start − GRIP_START_X)`（脊全在握持段、不撞 paddle / pivot）；违反缩 count / spacing | scalloped L214, L392-422 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，基于 5★ 样本观察的木色 + 金属 clip/pin 真实材质集 + 合理木色外推）：
| palette_style | wood（fixed 臂）| wood_dark（moving 臂）| 金属 clip/pin | ring / 装饰 | 来源样本 |
|---|---|---|---|---|---|
| natural_birch（默认）| 浅木 (0.52,0.36,0.20) | 深木 (0.42,0.28,0.15) | 锌镀 (0.72,0.74,0.78) | 浅木 ring (0.62,0.44,0.24) | parent / 多数变体 |
| walnut_stained | 深胡桃 (0.40,0.26,0.14) | 更深胡桃 (0.30,0.18,0.09) | 锌镀 | 胡桃 ring | scissor `WOOD_DARK` 外推 |
| cherry_warm | 暖樱桃 (0.58,0.40,0.22) | 深樱桃 (0.46,0.30,0.16) | 锌镀 | 暖蜜 ring | spoon `WOOD_HONEY` (0.58,0.40,0.22) |
| painted_white | 白漆木 (0.90,0.89,0.86) | 米白 (0.82,0.80,0.76) | 铬 (0.82,0.84,0.86) | 白漆 ring | 上菜夹喷漆形态外推 |
| bamboo_blond | 浅竹 (0.78,0.68,0.45) | 中竹 (0.68,0.56,0.36) | 锌镀 | 浅竹 ring | 竹夹形态外推 |
| ebony_dark | 乌木 (0.16,0.13,0.11) | 更深乌木 (0.10,0.08,0.07) | 黑铬 (0.20,0.20,0.22) | 乌木 ring | 深色木外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 close_mechanism / arm_shape / grip_detail 的拓扑**（arm 数恒为 2，joint 拓扑由 slot 选择决定）。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（close_mechanism / arm_shape / grip_detail）表达，不暴露 `*_count` 作为可变产品域；**臂数恒为 2**（双臂是本类身份的固定结构，不是可变 N）。
- **臂的对称双份是 helper-发射的固定 N=2（非 multiplicity 轴）**：
  - parent 手写 `fixed_arm`/`moving_arm` 两份（parent L130, L150）；scissor_pin / round_dowel / onepiece_bend 把对称双臂折成 `for i in range(2)` + `f"arm_{i}"` 循环发射（scissor L128-136 / dowel L145-174 / bend L162-173，对称 ±Z 堆叠 + 反向 ±HALF_SPLAY splay，其中 i=0 为 root、i=1 经 `pivot` REVOLUTE 铰接）。**模板侧统一用共享 `_emit_arm(i)` helper 发两臂（折成 range(2) 循环），固定 N=2，不暴露为可变 count 轴。**
- **存在固定 / 装饰性 N 的 module-local 阵列（非可变产品域，不进 slot_choice）**：
  - spring_clip_with_lock_ring 的 `grip_{i}`：`for i in range(N_GRIPS=4)` 共享 `_grip_nub()` helper 在 ring 4 个 cardinal 面发射（lock_ring L255-266），固定 N=4，随 lock_ring module（FIXED 装饰 visual，无 joint）。
  - scalloped_grip 的 `scallop_{i}`/`scallop_bot_{i}`：`for i in range(N_SCALLOPS)` 共享 `_finger_scallop()` helper 在两臂上下面发射（scalloped L213-250）。**唯一可参数化的装饰数量**：`scallop_count ∈ [4,8]`（标称 6），但它是 **module-internal 装饰层数量、conditional 仅 scalloped 时有效、不改拓扑等价类**，因此**不编入 `slot_choices_for_seed`**（与 cushion 的 pan_count / fence panel 那种"改拓扑维度的真 multiplicity 轴"不同——脊数变化不产生新 joint / part 拓扑）。在 §7 作 conditional 参数声明、`resolve_config` clamp。
- 这些都是 **module-local 固定 / 装饰多份 visual**（对称双臂 / ring 凸脊 / 握持指脊），按 module 而非 multiplicity 轴声明——本类不存在"任意 N 个臂 / N 个机构"的真实产品域。copied object 用共享 helper 发射、绝对式对称 / 等距 placement，无独立 joint（FIXED 装饰，inline 为 arm / ring visual，Rule 1）。

## 拓扑多样性审计

总组合数：close_mechanism(4) × arm_shape(5) × grip_detail(2) = **40**（全部正交合法，见 §9 兼容矩阵——无完全非法组合需 gate，仅 lock_ring × round_dowel 一组接口风险需 conditional 处理）。

仅 close_mechanism(4) × arm_shape(5) = **20 ≥ 10**（已大幅超机械门控）；其中 joint 拓扑差异来自 close_mechanism 的 {1 REVOLUTE（spring_clip / bend / scissor）/ 1 REVOLUTE + 1 PRISMATIC + 独立 ring part（lock_ring）} 与连接硬件 / pivot origin 差异（顶端金属 clip / 中段圆销 / 顶端弯木无金属 / clip + 滑环）。叠 grip_detail(2) → 40，充裕。

理由：close_mechanism 提供真正的 joint 拓扑差异（3 个 1-REVOLUTE 候选各有不同连接硬件 part + pivot origin + "有 / 无金属"区分，1 个 1-REVOLUTE+1-PRISMATIC+多 1 个 `slide_ring` part 的 lock_ring）；arm_shape(5) 提供 mesh / 截面等价类（含 round_dowel 的 section_loft 圆截面 vs 扁条的不同几何分支）；叠 grip_detail(2) 后 40 distinct。**三个 named slot 的选择天然进 `slot_choices_for_seed` 的 tuple**（`("close_mechanism", m)`、`("arm_shape", m)`、`("grip_detail", m)`），lock_ring 的多 part + PRISMATIC、bend 的无金属、scissor 的中段 pin 自然区分。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（close_mechanism / arm_shape / grip_detail），经兼容矩阵合法化（仅 lock_ring × round_dowel 需 conditional 解析 ring bore / 圆截面贴合，见下表，无组合完全排除），再解析 conditional scale（dowel_radius@dowel、bowl_dish@spoon、ring_travel@lock_ring、scallop_count/spacing@scalloped），再 uniform 各 independent scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 pivot 开合闭口姿态 + lock_ring 滑动锁闭 + scissor 中段交叉 + bend 无金属弯木 + spoon 两臂凹面相对）。


Controlled local parameterization：见 §参数表的 arm_length_scale / arm_width_scale / arm_thickness_scale / splay_angle_scale / pivot_close_scale（independent）+ dowel_radius_scale（@dowel）/ bowl_dish_scale（@spoon）/ ring_travel_scale（@lock_ring）/ scallop_count + scallop_spacing_scale（@scalloped）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：dowel_radius 仅 round_dowel、bowl_dish 仅 spoon_ends、ring_travel 仅 lock_ring、scallop_* 仅 scalloped_grip）→ 采 independent 臂长 / 宽 / 厚 / splay / 闭合 scale → 派生（Z 堆叠 offset 随 thickness / dowel 半径、clip span 随堆叠、脊 X 随 arm_length）→ 用 inequality（闭合不过头、scissor 销在中段、ring 不滑出、ring bore 容纳、dish 不切穿、scallop 不超握持段）投影 / 回缩。跨部件依赖（堆叠 vs 厚 / dowel 半径、ring 行程 vs 臂长、dish 深 vs bowl 厚、scallop 排布 vs 握持段）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 clip / pin / bend / ring captured 接口、pivot / slide joint origin、固定双臂 / 阵列 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（close_mechanism/arm_shape/grip_detail），再解析 conditional scale，再 uniform 各 independent scale，采 palette_style | slot_choices_for_seed 含 `("close_mechanism",m)`/`("arm_shape",m)`/`("grip_detail",m)` 且与 build 一致 |
| compatibility matrix | **三轴基本正交，40 组合全合法**——无组合完全排除。conditional / 接口解析：(1) **lock_ring × round_dowel**：圆截面 dowel 臂与矩形 ring bore 的贴合 / 锁紧接触面与扁条不同 → ring bore（`RING_BORE_Y/Z`）与锁紧 overlap 容差按 dowel 直径重算（保 bore 仍套住两 dowel + 锁紧时 `allow_overlap(ring_band, arm_dowel)` 成立），非排除而是 conditional 重算 bore 尺寸；(2) dowel_radius_scale 仅 round_dowel 生效；(3) bowl_dish_scale 仅 spoon_ends 生效；(4) ring_travel_scale 仅 lock_ring 生效；(5) scallop_count/spacing 仅 scalloped_grip 生效；(6) scissor_pin × 任意 arm_shape 合法（pin 在中段、arm_shape 改 tip 形态不冲突）；(7) onepiece_bend × scalloped_grip 合法（弯木在顶、脊在握持段不冲突）；(8) onepiece_bend 必须断言无金属（不可与 spring_clip / pin / ring 金属件混发）。 | 无 floating / collision / 闭合穿越过头 / pin 退化到端 / ring 滑出 / ring bore 套不住 dowel / dish 切穿 bowl / scallop 撞 paddle / bend 误带金属 |
| controlled local variation | 5 independent + 5 conditional clamped scale（含 scallop_count int），每 build 统一；conditional 随 slot 解析 | 比例 / 行程 / 角度变化不破坏 clip/pin/bend/ring captured、pivot/slide origin、开合闭口、固定双臂 / 阵列 visual、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 close_mechanism 机构 QC（pivot 开合 / lock_ring 滑锁 / scissor 中段交叉 / bend 无金属 / spoon 凹面相对）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| close_mechanism | 4 | yes | yes | spring_clip(1 REVOLUTE) / scissor_pin(1 REVOLUTE 中段) / lock_ring(1 REVOLUTE + 1 PRISMATIC + 独立 ring part) / onepiece_bend(1 REVOLUTE 无金属) |
| arm_shape | 5 | yes | yes | flat_paddle / round_dowel(section_loft) / straight_slat / spoon_ends(sphere-cut) / square_ends（mesh-profile 维度）|
| grip_detail | 2 | yes | no | plain / scalloped_grip（module-internal 装饰维度；2 candidate，降级理由见 Slot C 注）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("close_mechanism",m)`/`("arm_shape",m)`/`("grip_detail",m)`（scallop_count **不进** slot_choice，是 module-internal 装饰数量非拓扑维度）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；dowel_radius/bowl_dish/ring_travel/scallop_count/scallop_spacing 为 conditional 随 close_mechanism/arm_shape/grip_detail 解析；六条 inequality（闭合不过头、scissor 销在中段、ring 不滑出、ring bore 容纳、dish 不切穿、scallop 不超握持段）在 resolve 内投影 / 回缩
- compatibility matrix 三轴正交无组合完全排除；conditional scale 仅在对应 module 生效（不在无 ring 候选上设 ring_travel、不在非 scalloped 上设 scallop_count）；lock_ring × round_dowel 重算 ring bore / 锁紧容差
- 连续 scale clamp 后不破坏 clip/pin/bend/ring captured 接口、pivot/slide joint origin、开合闭口、固定双臂 / 阵列 visual
- 关键 joint：`pivot` REVOLUTE **axis≈(0,0,1)**（`abs(axis[2])>0.99` 且 x/y≈0，全候选共享）；close_mechanism=spring_clip_with_lock_ring 时 `slide` PRISMATIC **axis≈(1,0,0)**（`abs(axis[0])>0.99` 且 y/z≈0）
- captured / bridging：element-scoped `allow_overlap`（`pivot_pin`↔`strip_1`（scissor）；`ring_band`↔`fixed/moving_arm_strip`（lock_ring）；`spring_clip`↔`arm_1_dowel`（dowel）；`wood_bend`↔`arm_strip_1`（bend）；`spring_clip`↔`moving_arm_scoop`（spoon）），照搬各样本 run_tests 的 allow_overlap 段
- onepiece_bend 断言**无 metal 材质、两臂均无 `spring_clip` visual**（照搬 bend L285-304）
- scissor_pin 断言 pin 在中段（handle_side>0.05 且 tip_side>0.05）+ pin 圆截面（照搬 scissor L225-244）
- spring_clip_with_lock_ring 断言 ring 套两臂（rest + upper，`expect_overlap` yz）+ slide 沿 +X 滑（照搬 lock_ring L426-455）
- 固定双臂 / 阵列 visual 遵循 `arm_{i}` / `grip_{i}` / `scallop_{i}` 命名 + 绝对式对称 / 等距 placement + Rule 1（无独立 joint）
- grandfather：所有 captured / bridging 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- rest pose：`pivot` q=0 张开 "V"（tips 在 ±Y）；`slide` q=0 近 pivot

## Reject cases

- 把 close_mechanism 不同候选混发（如 onepiece_bend 同时带 `spring_clip` / `pivot_pin` 金属件，或 scissor_pin 又带顶端 clip）→ Slot A 单选互斥（bend run_tests 显式断言无金属、无 spring_clip）。
- close_mechanism=onepiece_bend 仍 extend 金属材质或发 `spring_clip`/`pivot_pin` visual → 违反"一体弯木无金属"拓扑（bend L285-304 FAIL）。
- close_mechanism≠spring_clip_with_lock_ring 仍发 `slide_ring` part 或 `slide` PRISMATIC → 违反这三候选"无滑环"拓扑（仅 lock_ring 有 slide）。
- 把对称双臂当可变 multiplicity 轴暴露 `arm_count` 或编进 slot_choice → 臂数恒为 2 是固定身份结构（非 N 轴，违反 §8）。
- 把 scallop_count 编入 `slot_choices_for_seed` 当拓扑维度 → 脊数是 module-internal 装饰数量、不产生新 part/joint 拓扑（不进 slot_choice，§8）。
- 把握持脊 / ring 凸脊 / 对称双臂端帽当独立活动 part 加 joint → 违反 Rule 1（固定 / 装饰阵列，应 inline 为 arm/ring visual）。
- `pivot` rest pose 设成闭合（q=upper）而非 q=0 张开 "V" → current-pose 与 viewer 目检不符（所有样本 rest 张开、tips 在 ±Y）。
- `pivot` axis 设成非 Z（如绕 X / Y）→ 违反"绕扁臂平面法线转"（所有样本断言 `abs(ax[2])>0.99`）。
- `pivot` / `slide` origin 放在臂中心或任意点而非真实连接硬件（clip / pin / bend / ring bore）→ `fail_if_articulation_origin_far_from_geometry` FAIL。
- 闭合行程过大致两 tip 互相穿越过中线（pivot_upper 过头）→ §7 第一条 inequality FAIL；按比例缩 upper。
- scissor_pin 销退化到臂端（handle_side 或 tip_side <0.05）→ §7 第二条 inequality FAIL（销须在中段）。
- lock_ring 滑出臂端（`slide` upper 过大）或 ring bore 套不住臂（width/thickness scale 缩太小）→ §7 第三 / 四条 inequality FAIL。
- spoon_ends 的 dish 切穿 bowl 底（DISH_DEPTH 过大）→ §7 第五条 inequality FAIL；缩 dish 深。
- scallop 排布超出握持段撞 paddle / pivot → §7 第六条 inequality FAIL；缩 count / spacing。
- 给 captured / bridging 接口（clip 桥接 / pin 穿臂 / bend junction / ring bore）补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / 臂 scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 clamp / pliers / scissors / chopsticks 语义混入（螺杆进给 / 金属剪切 / 无铰接双棍）→ 出类，本类是双臂铰接闭合的木食物夹。

## 与相邻类别的边界

- 不该混入：**螺旋驱动手用夹 / C 形夹 / 台钳（clamp / vise）**——螺杆竖直 PRISMATIC 进给 + C 形 frame，主运动 spine 完全不同；已有独立 slug `clamp`。
- 不该混入：**钳子 / 老虎钳 / 剪刀（pliers / scissors）**——金属双臂绕中心 pivot 剪切 / 切割，把手成对称剪式；本类是木质张开夹食的食物夹（scissor_pin 候选虽中段销但仍是松弛张开的木夹，非金属剪切工具）。
- 不该混入：**筷子（chopsticks）**——两根独立无铰接木棍，无闭合机构 / 弹簧 / 销 / 弯木、无 `pivot` REVOLUTE。
- 不该混入：**金属厨房夹（metal kitchen tongs，不锈钢臂 + 硅胶头 + 端部锁扣）**——本类是**木**夹（palette 是木 + 少量金属 clip/pin）；金属夹的硅胶头 + 弹簧锁扣是另一形态家族（如需可作单独 slug）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **grip_detail 仅 2 candidate**（module-internal 装饰维度，降级理由见 Slot C 注）是否接受还是要求回 fork 池补造第 3 个真实结构形态（cross-hatch 滚花 / 纵向沟槽 / 烙印 panel）；(2) **scallop_count ∈ [4,8] 不进 slot_choice**（脊数是装饰数量非拓扑维度，与 cushion pan_count 的真 multiplicity 轴区分）是否符合 multiplicity 审计期望，还是要求把它当真 multiplicity 轴编入 slot_choice；(3) **臂数恒为 2、无 multiplicity 轴**是否接受（双臂是固定身份结构）；(4) **lock_ring × round_dowel** 的 ring bore / 锁紧容差按 dowel 重算（conditional，非排除）是否接受；(5) palette_style 6 套是否合适（natural_birch / walnut_stained / cherry_warm 为样本观察色，painted_white / bamboo_blond / ebony_dark 为合理木色外推）；(6) Topology target 40<300 的说明是否接受（本小类真实结构上限，臂数恒 2 无放大空间）；(7) scissor_pin 的 pivot upper=0.28（比 spring_clip 族 0.18 大）是否在模板侧按 close_mechanism 解析为不同 upper 基线。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **坐标统一**：全 9 样本约定一致（臂沿 +X、扁面法线 Z、±Z 堆叠、±HALF_SPLAY splay、`pivot` REVOLUTE axis=(0,0,1)、q=0 张开 / upper 闭），模板直接沿用，无需 rebase。
- **共享 helper**：
  - `_emit_arm(i, ...)`：发两臂（折成 `for i in range(2)`，对称 ±Z 堆叠 + 反向 ±HALF_SPLAY；i=0 root、i=1 child），arm mesh 由 arm_shape 决定（见下）。
  - arm mesh helper 按 arm_shape 切：`_arm_solid`（flat_paddle / straight_slat / square_ends 的扁条 polyline / rect，外扩 / 等宽 / 方切由 outline 切换）、`_arm_dowel`（round_dowel 的 `_circle_section` + `section_loft`，注意需 import `section_loft`/`mesh_from_geometry` 且经 `mesh_from_geometry` 而非 `mesh_from_cadquery`）、`_arm_with_scoop`（spoon_ends 的 shaft+bowl union + sphere cut，带 `dish_up` 标志两臂凹面相对）。
  - close_mechanism 连接硬件 helper：`_clip_solid`（spring_clip / lock_ring 的金属 box）、`_pin_solid`（scissor 的圆柱）、`_ring_solid`+`_grip_nub`（lock_ring 的 collar + 4 凸脊）、`_bend_solid`（bend 的半环 torus，绕 +Y revolve 180°，注意 YZ workplane 显式 polyline 避坐标系错位）。
  - grip_detail helper：`_finger_scallop`+`_finger_scallop_inverted`（scalloped 的上下半圆柱脊，`for i in range(scallop_count)` 在两臂上下面发射；fixed 臂的脊还需 cos/sin splay 旋转对齐，照搬 scalloped L206-235）。
- **captured 接口 allow_overlap**：`run_wooden_tongs_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（scissor L175-194、lock_ring L460-483、dowel L313-324、bend L340-352、spoon L397-420）。
- **conditional 范围解析顺序**：先采 close_mechanism / arm_shape / grip_detail → 解析 dowel_radius（仅 round_dowel）/ bowl_dish（仅 spoon）/ ring_travel（仅 lock_ring）/ scallop_count + spacing（仅 scalloped）/ pivot upper 基线（spring_clip 族 0.18、scissor 0.28）→ 采 independent 臂长 / 宽 / 厚 / splay / 闭合 scale → 派生 Z 堆叠 offset（随 thickness / dowel 半径）+ clip span（随堆叠）+ 脊 X（随 arm_length）→ 投影六条 inequality。
- **round_dowel 注记**：源用 `section_loft` 圆截面 + `mesh_from_geometry`（dowel L31-32, L100, L136），与扁条的 `mesh_from_cadquery` 不同分支；arm_thickness_scale 对 dowel 不适用（dowel 用 dowel_radius_scale）；clip span / Z 堆叠须按 dowel 直径（非扁厚）算（dowel L132-133）。
- **lock_ring × round_dowel 注记**：圆截面 dowel × 矩形 ring bore，ring bore（`RING_BORE_Y/Z`）须 ≥ 两 dowel 堆叠直径 + clearance，锁紧 `allow_overlap(ring_band, arm_dowel)` 容差按 dowel 重算（见 §9 兼容矩阵第 1 条）。
- **参考模板**：选运动拓扑相近的——root + 单 child REVOLUTE + 可选并列 PRISMATIC child + 互斥机构槽（`clamp` 的 frame→screw PRISMATIC + 可选 frame→lever REVOLUTE 并列挂 frame，与本类 fixed_arm→moving_arm REVOLUTE + 可选 fixed_arm→slide_ring PRISMATIC 并列同构；clamp 的 foot/handle 互斥机构槽 ≈ 本类 close_mechanism 互斥槽）。wooden_tongs 尺度小（臂 ~0.30m、clip ~0.022m、ring ~0.015m），joint origin 须精确落真实硬件面（clip / pin / bend / ring bore，baseline ≤0.015m）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| onepiece_spring_clip + flat_paddle + plain | rec_build-...-wood_...c58cac31 | `_arm_solid` L54-98 / `_clip_solid` L101-116 / `fixed_arm`+`moving_arm` L130-159 / `pivot` REVOLUTE L167-179 / `spring_clip` visual L142-147 | 基线坐标约定 + 顶端金属弹簧夹（1 REVOLUTE）+ 扁 paddle 臂 + 光臂 + 双臂堆叠 / splay / 开合范式 |
| S2 | A | scissor_pin | rec_wooden_tongs_var_scissor_pin | `arm_{i}` `for i in range(2)` L128-136 / `_pin_solid` L98-105 / `pivot_pin` visual L140-145 / `pivot` REVOLUTE 交叉面 L152-162 / allow_overlap(pin,strip_1) L175-194 / 销在中段断言 L225-244 | 中段交叉销机构（1 REVOLUTE，双臂 range(2) 循环范式 + 短把手/长 tip）|
| S3 | A | spring_clip_with_lock_ring | rec_wooden_tongs_var_lock_ring | `_ring_solid` L132-154 / `_grip_nub`+`grip_{i}` `for i in range(4)` L157-167, L255-266 / `slide_ring` part L237-266 / `slide` PRISMATIC L271-281 / allow_overlap(ring,arm) L460-483 | 弹簧夹 + 滑动锁环（1 REVOLUTE + 1 PRISMATIC + 独立 ring part + 4 凸脊 copy-logic 源）|
| S4 | A | onepiece_bend | rec_wooden_tongs_var_onepiece_bend | `_bend_solid` revolve 半环 L94-131 / `wood_bend` 根臂 visual L181-186 / `pivot` REVOLUTE origin=BEND_RADIUS L193-206 / 无金属 / 无 spring_clip 断言 L285-304 / allow_overlap(bend,strip_1) L340-352 | 一体弯木机构（1 REVOLUTE 无金属，弯木 = 弹簧 + 无金属断言范式）|
| S5 | B | round_dowel | rec_wooden_tongs_var_round_dowel | `_circle_section` L63-74 / `_arm_dowel` `section_loft` L77-100 / `mesh_from_geometry`/`section_loft` import L31-32 / arm loop L145-174 / dowel 圆截面断言 L248-261 / allow_overlap(clip,dowel)+expect_contact L313-324 | 圆木 dowel 臂截面（section_loft 圆截面，mesh_from_geometry 分支）|
| S6 | B | straight_slat | rec_wooden_tongs_var_straight_slat | `_arm_solid` `cq.rect(ARM_LENGTH, ARM_WIDTH)` L65-70 / 等宽 slat 断言 L217-253 | 全长等宽直扁条臂（无 paddle 外扩，rect 截面）|
| S7 | B | spoon_ends | rec_wooden_tongs_var_spoon_ends | `_shaft_half_profile` L67-78 / `_bowl_half_profile` L81-112 / `_arm_with_scoop` sphere cut + `dish_up` L121-184 / bowl 厚/宽断言 L315-338 / allow_overlap(clip,scoop) L397-420 | 凹勺 / 铲斗 tip 臂（shaft+bowl union + sphere-cut dish，dish_up 两臂凹面相对）|
| S8 | B | square_ends | rec_wooden_tongs_var_square_ends | `_arm_solid` tip 满宽方切 L54-102（hold full TIP_WIDTH to L82）/ tip 满宽断言 L260-276 | 方头平切 paddle 臂（满宽方切端，无收尾圆角）|
| S9 | C | scalloped_grip | rec_wooden_tongs_var_scalloped_grip | `_finger_scallop` L126-144 / `_finger_scallop_inverted` L147-160 / `scallop_{i}`/`scallop_bot_{i}` `for i in range(N_SCALLOPS=6)` 两臂上下面 L213-250 / scallop 存在+等距断言 L372-422 | 握持段 scalloped 指槽脊（半圆柱脊 module-internal for-loop，两臂上下面，无 joint，Rule 1 + scallop_count copy-logic 源）|
