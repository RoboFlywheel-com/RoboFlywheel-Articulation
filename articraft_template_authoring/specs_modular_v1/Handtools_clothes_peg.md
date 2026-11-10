# clothes_peg (wooden spring clothespin / clothes peg) — Modular Spec

> 来源小类：`picture/Handtools/clothes peg`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Handtools_clothes_peg.md`。
> **"clothes_peg" 在此 = 弹簧木夹 / 衣夹（spring clothespin / clothes peg），不是 binder clip / 文具弹簧夹（已有独立 slug `clip`）、也不是螺旋夹 clamp（已有独立 slug `clamp`）。**
> 结构家族 = 弹簧衣夹：两块**镜像木腿**（`lower_half` root + `upper_half` moving）绕**单个 REVOLUTE `pivot`** 对开，由一个**弹簧件**（`spring` / `leaf_spring`）通过 `lower_to_spring` FIXED 固定到 root、偏置 pivot 使前颚常闭。两块木腿共用一个 `_wood_half()` CadQuery solid（一份几何 helper、放两次）。
>
> **同步状态**：本 spec 引用的 6 个 5 星样本（1 个 parent + 5 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对，已读完整 model.py）。引用以 part / joint / helper **名字** 为准（`lower_half`/`upper_half`/`spring`/`leaf_spring` part；`pivot`/`lower_to_spring` joint；`_wood_half`/`_spring_mesh`/`_leaf_spring_arm`/`_leaf_spring_bend`/`_cut_serrated_teeth` helper），行号仅作定位。
>
> **坐标约定（全部 6 样本一致，模板直接沿用）**：peg "躺平在侧面"——peg frame 长轴 = world X，两腿沿 world Y 并排（lower_half 在 +Y、upper_half 在 −Y），宽度沿 world Z（0=地面 → HALF_W）。`pivot` REVOLUTE origin=(PIVOT_X, 0, HALF_W/2)、rpy=(π/2,0,0)、axis=(0,−1,0)（joint frame 内 −Y = world 竖直）；正 q 开前颚、后尾相互挤压；q=0 为闭合 rest pose。`lower_to_spring` FIXED origin=(0,0,0)。**全样本完全共享此 spine——无需 rebase。**

## 元信息
| 项 | 值 |
|---|---|
| slug | `clothes_peg` |
| template path | `agent/templates/Handtools_clothes_peg.py` |
| test path (optional) | `tests/agent/test_clothes_peg_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `lower_half` + REVOLUTE `upper_half` + FIXED `spring`；三个可替换层 spring/jaw/tail 都改写共享 `_wood_half()` solid 或 spring 件，不增删 joint）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（1 parent + 5 fork 槽位变体；均 converged、compile success、恰好 1 个非 fixed joint（`pivot` REVOLUTE）+ `lower_to_spring` FIXED、workbench-only，rating=5）|
| read_count | 6（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 6/6 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 6 个样本）**：`lower_half`（root，躺地）+ `upper_half`（moving，绕 `pivot` REVOLUTE 对开）+ 一个 spring 件（FIXED 到 root via `lower_to_spring`）。`pivot` REVOLUTE axis=(0,−1,0)、lower=0/upper=PIVOT_MAX 是**所有候选共享的唯一活动关节**。两块木腿共用一个 `_wood_half()` solid（parent L87-154），因角色不同（root vs revolute child）是两份具名 part，**不是复制循环**——除 rounded_jaw 用 `for i in range(2)` 发射 `half_{i}` 作风格化外（拓扑等价）。spring 件与碗壁的 captured 过盈用 `allow_overlap(spring, lower)` + `allow_overlap(spring, upper)` 守（parent L303-312）。
- **Slot A spring / pivot mechanism 轴**：是 **spring part 几何 / helper / seat 形态**变化（不改 joint 拓扑，仍是 1 REVOLUTE + 1 FIXED）。
  - torsion_coil（parent）：`spring` part，`_spring_mesh()`（`tube_from_spline_points` ~2 圈一体扫掠管 = coil + 2 直腿，parent L157-204），木腿用**圆 `SEAT_R` barrel seat**（`circle(SEAT_R).extrude` cut，parent L145-152）。
  - leaf_spring（leaf_spring 变体）：`leaf_spring` part，`arm_0`/`arm_1`/`bend` visual，helper `_leaf_spring_arm(sign)`（L148-162）+ `_leaf_spring_bend()`（L165-170），两臂 `for i in range(2)` 发射（L220-228）；木腿用**矩形 `SEAT_L×SEAT_W×SEAT_D` box seat**（`box(...).translate` cut，L138-143）。
- **Slot B jaw / 前端 gripping-tip 轴**：是 `_wood_half()` 前端 profile（pivot 前）形态变化。
  - flat_notched（parent）：平行平颚面（pts 到 `NOSE_X`，parent L101-112）+ `NOSE_X-0.009` 处半圆 `groove` cut（parent L131-139）。
  - rounded_barrel（rounded_jaw 变体）：`BARREL_R` 半圆弧 nose（`arc_pts` 循环 L110-133），**无 groove cut**，两半闭合成全圆柱 head。
  - toothed_serrated（toothed_jaw 变体）：`_cut_serrated_teeth()`（`for i in range(_N_TEETH)` V 槽棱柱 L172-196）在平颚面上锯齿；常数 `TOOTH_PITCH`/`TOOTH_DEPTH`/`TEETH_START_X`/`TEETH_END_X`（L165-169）。
- **Slot C tail / 后端 grip-end 轴**：是 `_wood_half()` 后端 profile（pivot 后）形态变化。
  - flared_pad（parent）：外翻平指垫，z_back=0.0095（parent L95）+ 后端 profile 收尾在 flared pad（L110-112）。
  - dished_thumb（dished_tail 变体）：抬高 pressing pad（`PAD_BULGE` L91、profile L116-128）+ 球形 `dish_sphere` 凹坑 cut（`DISH_R`/`DISH_DEPTH` L89-90、cut L170-183）。
  - square_stub（square_tail 变体）：钝平方 stub，z_back=0.0075（L95）+ 后端 profile 直接收尾（L101-111），无 flare / pad。

## 核心身份

一只**弹簧木衣夹**（spring clothespin / clothes peg，~72 mm 长、~8.5 mm 宽、pivot 处 ~13 mm 高）：两块**镜像木腿**——`lower_half`（root，躺平在侧面，坐地于 z≈0）与 `upper_half`（moving）——绕一个**单 REVOLUTE `pivot`**（spring-barrel 轴 / fulcrum，world 竖直）对开。一个**弹簧件**（扭簧 coil 或板簧 leaf strip）经 `lower_to_spring` FIXED 刚性挂在 root 上、其腿 / 臂压在两腿 relieved 内尾面上，**rest（q=0）时把前颚压闭、后指尾被 TAIL_ANGLE relief 撑开**；用户挤压后尾即开前颚。木腿前端是**夹线颚**（平颚 + 半圆夹线 groove / 圆头 barrel / 锯齿），后端是**指尾握端**（外翻平垫 / 凹拇指坑 / 钝方 stub）。默认成熟域：spring(2) × jaw(3) × tail(3) 笛卡尔积的小型躺平木夹。活动语义 = **upper_half 绕 pivot 对开夹紧**（唯一 REVOLUTE，全候选共享）；弹簧件为偏置件（FIXED，非可动 joint）。

不该混入：
- **binder clip / 文具弹簧夹 / 鳄鱼夹（clip）**——金属杠杆 / 长把手弹簧夹纸，无木腿、无 barrel-seat 扭簧 / 板簧、夹持比例与材质完全不同；已有独立 slug `clip`。
- **螺旋夹 / C 形 / G 形 hand clamp（clamp）**——螺杆 PRISMATIC 进给 + C 形 frame，主运动 spine 是直线进给而非两臂对开 REVOLUTE；已有独立 slug `clamp`。
- **钳子 / 老虎钳（pliers）**——双臂绕中心 pivot 剪切，虽同为对开 REVOLUTE，但无偏置弹簧件、无 relieved 尾面常闭机构、是金属工具非木夹。
- **塑料活铰一体夹（living-hinge clip）**——一体注塑、用塑料薄铰回弹无独立弹簧件，会改 `pivot`/`lower_to_spring` 拓扑结构；不在本批样本池（见 §A 降级注 + §13）。

## 槽位 + 候选模块表

> **建模注记**：本类三轴全部改写**同一组共享几何**（spring 件 + `_wood_half()` 前 / 后端 profile），**都不增删 joint**——拓扑等价类始终是「1 REVOLUTE `pivot` + 1 FIXED `lower_to_spring`」。多样性来自 spring 件几何 / seat 形态（Slot A）、前端颚 profile（Slot B）、后端尾 profile（Slot C）的笛卡尔积（B×C 撑到 9、× A 到 18，见 §9）。两块木腿共用一个 `_wood_half()` solid（一份 helper 放两次，**非复制循环**）；锯齿 teeth 是 module-internal `for` 循环（V 槽阵列，非 multiplicity 轴）。

### Slot A：spring / pivot mechanism（FIXED 到 root 偏置 pivot 的弹簧件 + 对应木腿 seat 形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| torsion_coil（基线）| rec_build-...-clot_...add41790（parent）| `spring` part L255-263 + `_spring_mesh()`（`tube_from_spline_points` ~2 圈 coil + 2 直腿）L157-204 + 圆 `SEAT_R` barrel seat（`circle(SEAT_R).extrude`）L145-152 + FIXED `lower_to_spring` L266-272 | eligible if compatible | 钢扭簧：一根一体扫掠 wire tube（coil 绕 pivot 轴 + 两条直腿），coil 圆心精确在 pivot 轴上、captured 进圆 barrel seat；腿压在两腿 relieved 内尾面。spring 为 `model.part("spring")` 单 visual（无内循环），木腿 seat 是**圆截面** cut |
| leaf_spring | rec_clothes_peg_var_leaf_spring | `leaf_spring` part L211-237（`arm_0`/`arm_1` `for i in range(2)` L220-228 + `bend` L231-237）+ `_leaf_spring_arm(sign)` L148-162 + `_leaf_spring_bend()` L165-170 + 矩形 `SEAT_L×SEAT_W×SEAT_D` box seat L138-143 + FIXED `lower_to_spring` L241-247 | eligible if compatible | 弯钢板簧：两片倾斜 box 臂（`STRIP_T×STRIP_W×ARM_LEN`，按 ±TAIL_ANGLE 倾贴尾面）+ 一段短 `bend` 连接，**无 coil**；两臂 `for i in range(2)` + 共享 `_leaf_spring_arm(sign)` helper、对称 placement；木腿 seat 是**矩形** box cut |

> **降级理由（Slot A 仅 2 candidate，本批最薄的一槽）**：满足每槽 ≥2 的底线。**真实世界 clothes peg 弹簧词汇表本身就只有「扭簧（torsion coil）/ 板簧（leaf spring）」两种结构家族**——其余 peg 弹簧差异都是尺寸 / 材质 / 圈数 / 线径的连续参数（不入 slot），不是独立拓扑。组合数已由 B(3)×C(3)=9、× A(2)=18 撑到 ≥10。若下游模板要加厚 Slot A，唯一现实第三候选是**塑料一体活铰（living-hinge，无独立弹簧件）**——但它会改动 `pivot`/`lower_to_spring` 关节结构（去掉 spring part 与 FIXED joint、pivot 由薄铰回弹替代），需单独 fork 验证后再入池，**不在模板侧虚构**。审核如需扩容应回 fork 池补造该 living-hinge 候选。

### Slot B：jaw / gripping-tip shape（`_wood_half()` 前端 = pivot 之前，front nose profile）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_notched（基线）| rec_build-...-clot_...add41790（parent）| `_wood_half()` 平 parting face profile（pts 到 `NOSE_X`）L101-112 + 半圆 `groove` cut（`NOSE_X-0.009`, `circle(0.0022)`）L131-139 | eligible if compatible | 平行平颚面，一道夹线 groove 半圆槽刻在 nose 后；平 tip pad 闭合时与镜像 twin 相触、groove 夹线 |
| rounded_barrel | rec_clothes_peg_var_rounded_jaw | `_wood_half()` `BARREL_R` 半圆弧 nose（`arc_pts` 循环 −90°→+90°）L110-133（常数 `BARREL_R` L85）；**无 groove cut**（圆 SEAT_R seat 仍在 L152-159）| eligible if compatible | 光滑半圆 barrel-head 颚；两半闭合成完整圆柱夹头；nose profile 由弧点替换平 tip + groove |
| toothed_serrated | rec_clothes_peg_var_toothed_jaw | `_wood_half()` + `_cut_serrated_teeth()`（`for i in range(_N_TEETH)` V 槽三角棱柱 cut）L172-196；常数 `TOOTH_PITCH`/`TOOTH_DEPTH`/`TEETH_START_X`/`TEETH_END_X`/`_N_TEETH` L165-169；在 `_wood_half()` 末尾调用 L159 | eligible if compatible | 平颚面上一排浅 V 槽锯齿（pivot 前、夹线 groove 前止），凸起齿咬线；teeth 是 module-internal `for` 循环阵列（非 multiplicity 轴，随 module 固定按 pitch 算 N） |

### Slot C：tail / grip-end shape（`_wood_half()` 后端 = pivot 之后，back finger profile）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flared_pad（基线）| rec_build-...-clot_...add41790（parent）| `_wood_half()` 后端 profile 收尾在 flared `z_back=0.0095` 指垫（L95 常数 + L110-112 profile 点）| eligible if compatible | 圆润外翻平指垫在尾端；back profile 点序在 `BACK_X` 处给出 flared pad |
| dished_thumb | rec_clothes_peg_var_dished_tail | `_wood_half()` 抬高 pressing pad（`PAD_BULGE` L91 + profile L116-128）+ 球形 `dish_sphere` 凹坑 cut（`sphere(DISH_R).cut`）L170-183；常数 `Z_BACK`/`PAD_BULGE`/`DISH_R`/`DISH_DEPTH` L85-91 | eligible if compatible | 抬起的 pressing pad + 外面碗形球凹拇指坑；back profile 改成抬高 pad + 球 cut，给拇指凹面按压 |
| square_stub | rec_clothes_peg_var_square_tail | `_wood_half()` 后端 profile 直接钝收尾 `z_back=0.0075`（L95 常数 + L101-111 profile 点，无 L110-112 的 flare 点）| eligible if compatible | 朴素钝方指 stub，无 flare / pad；back profile 点序在 `BACK_X` 给出平顶 stub |

## 槽位图（slot graph）

pattern: parallel_children（固定 root `lower_half`；`upper_half` 绕 `pivot` REVOLUTE 挂 root；`spring`/`leaf_spring` 经 `lower_to_spring` FIXED 挂 root；三个 slot 都改写共享 `_wood_half()` solid 或 spring 件几何，不增删 joint）

```
lower_half (root, 躺地 z≈0; 由 _wood_half() solid 构建，含 jaw 前端 + tail 后端 + spring seat)
  │
  ├── upper_half ──[pivot: REVOLUTE axis=(0,−1,0), origin=(PIVOT_X,0,HALF_W/2), rpy=(π/2,0,0), lower=0/upper=PIVOT_MAX]
  │        （镜像同一 _wood_half() solid，role=revolute child；正 q 开前颚、后尾挤压；q=0 闭合）
  │
  └── spring / leaf_spring ──[lower_to_spring: FIXED, origin=(0,0,0)]   ← Slot A 决定弹簧件几何 + 木腿 seat 形态
           （coil/leaf 圆心/bend 精确在 pivot 轴上、captured 进木腿 seat；腿/臂压两腿 relieved 内尾面偏置 pivot）

  [Slot B jaw]  改写 _wood_half() 前端（pivot 之前）：flat_notched(平面+groove) / rounded_barrel(半圆弧) / toothed_serrated(V槽阵列)
  [Slot C tail] 改写 _wood_half() 后端（pivot 之后）：flared_pad(外翻平垫) / dished_thumb(球凹坑) / square_stub(钝方)
```

接口点位与 joint 语义：
- **lower_half → upper_half（全候选共享主活动关节）**：mating = pivot fulcrum / spring barrel 轴。`pivot` REVOLUTE axis=(0,−1,0)（joint frame 内，= world 竖直），origin=(PIVOT_X, 0, HALF_W/2)、rpy=(π/2,0,0)，lower=0/upper=PIVOT_MAX（torsion_coil/rounded/toothed/dished/square PIVOT_MAX=0.16；leaf_spring PIVOT_MAX=0.10——见 §7 PIVOT_MAX 表）。q=0 闭合（前颚近触），正 q 开前颚 / 挤后尾。upper_half 是镜像同一 `_wood_half()` solid，visual origin=(−PIVOT_X,0,GAP/2)（把 mesh 放回 peg origin、parting face 在 +GAP/2）。
- **lower_half → spring（全候选共享，Slot A 决定件几何）**：mating = pivot barrel seat（木腿 parting 面刻入的 seat）。`lower_to_spring` FIXED origin=(0,0,0)。spring 件 visual origin=(0,0,HALF_W/2)、rpy=(π/2,0,0)。spring coil/leaf 圆心 / bend 精确在 pivot 轴 X=PIVOT_X 上、captured 进木腿 seat（torsion_coil→圆 SEAT_R seat；leaf_spring→矩形 box seat），腿 / 臂沿 −X 压在两腿 relieved 内尾面（TAIL_ANGLE 偏置）。
- **mating policy**：spring 与两木腿是 captured 过盈（coil/leaf 嵌入木腿 seat，**两轴非对齐面对接**）→ **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 pivot/FIXED origin + element-scoped `allow_overlap(spring, lower)` / `allow_overlap(spring, upper)` 守 captured overlap（照搬各样本 run_tests，parent L303-312、leaf_spring L278-287）。pivot 处两木腿 parting face 近触：`expect_gap(lower/upper, axis="y", max_gap≈0.004, max_penetration≤0.0002)`（闭合 pose，parent L385-392）。
- **rest pose**：所有样本 q=0 闭合（前颚近触、后尾被 relief 撑开），spring 件偏置使其常闭。peg 躺地 z_min≈0。
- **互斥 / 可选 / 派生**：Slot A 两候选互斥（一次只一种弹簧件，决定 spring 件几何 + 木腿 seat 形态）；Slot B 三候选互斥（一种前端 profile）；Slot C 三候选互斥（一种后端 profile）。三轴在几何上彼此正交（前端 jaw / 后端 tail / 中部 spring seat 互不干涉，无接口冲突），任意 2×3×3 组合合法（见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / spring — torsion_coil（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spring`（visual：一根 `_spring_mesh()` 一体钢扭簧管 = coil + 2 直腿，单 visual）| parent `_spring_mesh` L157-204 / `spring` part L255-263 |
| internal joints | `lower_to_spring` FIXED origin=(0,0,0)（spring 刚挂 root，非可动）| parent L266-272 |
| upstream interface | coil 圆心在 pivot 轴 X=PIVOT_X，captured 进木腿圆 `SEAT_R` barrel seat（`circle(SEAT_R).extrude` cut L145-152）；`allow_overlap(spring, lower/upper)` | parent L145-152, L303-312 |
| downstream interface | 无（spring 是叶 part；其腿压两腿 relieved 内尾面偏置 pivot）| — |

### Slot A / spring — leaf_spring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `leaf_spring`（visual：`arm_0`/`arm_1`（`for i in range(2)` + `_leaf_spring_arm(sign)`）+ `bend`）| leaf_spring L211-237 |
| internal joints | `lower_to_spring` FIXED origin=(0,0,0)| leaf_spring L241-247 |
| upstream interface | bend 在 pivot 轴 X=PIVOT_X，两臂 captured 进木腿矩形 `SEAT_L×SEAT_W×SEAT_D` box seat（`box(...).cut` L138-143）；`allow_overlap(leaf_spring, lower/upper)` | leaf_spring L138-143, L278-287 |
| downstream interface | 无（叶 part；两臂按 ±TAIL_ANGLE 倾贴尾面偏置 pivot）| — |

### Slot B / jaw — flat_notched（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（前端 profile 改写共享 `_wood_half()` solid，发射为 `lower_half`/`upper_half` visual）| parent `_wood_half` L87-154 |
| internal joints | 无（jaw 是 module-local mesh 维度）| — |
| interface | 平 parting face（pts→`NOSE_X` L101-112）+ 半圆夹线 `groove` cut（`NOSE_X-0.009`, `circle(0.0022).extrude` L131-139）| parent L101-112, L131-139 |

### Slot B / jaw — rounded_barrel
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（前端 profile 改 `BARREL_R` 弧点）| rounded_jaw `_wood_half` L93-161 |
| internal joints | 无 | — |
| interface | `arc_pts` 半圆弧（−90°→+90°，`BARREL_R` L85）替换平 tip，**无 groove**；两半闭合成圆柱头 | rounded_jaw L110-133 |

### Slot B / jaw — toothed_serrated
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（前端平颚 + V 槽阵列 cut，改写 `_wood_half()`）| toothed_jaw `_wood_half` L87-161 |
| internal joints | 无 | — |
| interface | `_cut_serrated_teeth()`（`for i in range(_N_TEETH)` V 槽三角棱柱 cut，`TOOTH_PITCH`/`TOOTH_DEPTH`/`TEETH_START_X`/`TEETH_END_X` L165-169）在平颚面上锯齿；teeth 为 module-internal 循环阵列 | toothed_jaw L159, L172-196 |

### Slot C / tail — flared_pad（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（后端 profile 改写共享 `_wood_half()` solid）| parent `_wood_half` L87-154 |
| internal joints | 无 | — |
| interface | 后端 profile 点序收尾在 flared `z_back=0.0095` 外翻平指垫（L95 + L110-112）| parent L95, L110-112 |

### Slot C / tail — dished_thumb
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（后端抬高 pad + 球凹 cut，改写 `_wood_half()`）| dished_tail `_wood_half` L99-185 |
| internal joints | 无 | — |
| interface | 抬高 pressing pad（`PAD_BULGE` L91 + profile L116-128）+ 球形 `dish_sphere`（`sphere(DISH_R).translate.cut`，`DISH_R`/`DISH_DEPTH` L89-90）凹拇指坑 cut L170-183 | dished_tail L116-128, L170-183 |

### Slot C / tail — square_stub
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（后端 profile 钝收尾，改写 `_wood_half()`）| square_tail `_wood_half` L87-153 |
| internal joints | 无 | — |
| interface | 后端 profile 点序在 `BACK_X` 直接钝平顶收尾 `z_back=0.0075`（L95 + L101-111，无 flare 点）| square_tail L95, L101-111 |

### 两木腿共享 solid + 锯齿内循环（固定多份 visual，非 multiplicity 轴）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_half`（root visual）+ `upper_half`（revolute child visual），**共用一个 `_wood_half()` solid**（一份 helper 放两次，因角色不同是两份具名 part，非复制循环）| parent L213, L225-250 |
| joints | `pivot` REVOLUTE（lower↔upper）；spring 件 FIXED；**无其它 joint** | parent L274-287 |
| 固定阵列 visual | rounded_barrel 的 `half_{i}`（`for i in range(2)` 风格化发射两腿，拓扑等价两份具名 part，rounded_jaw L238-250）；toothed_serrated 的 V 槽 teeth（`for i in range(_N_TEETH)`，module-internal 装饰阵列，随 module 按 pitch 固定 N，不暴露为可变 count 轴）| rounded_jaw L238-250 / toothed_jaw L172-196 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| spring_mechanism | enum | torsion_coil / leaf_spring | torsion_coil | choice | 由 deterministic procedural sampler 选；决定 spring 件几何 helper + 木腿 seat 形态（圆 SEAT_R / 矩形 box）| Slot A 表 |
| jaw_shape | enum | flat_notched / rounded_barrel / toothed_serrated | flat_notched | choice | sampler 选；改写 `_wood_half()` 前端 profile（互斥）| Slot B 表 |
| tail_shape | enum | flared_pad / dished_thumb / square_stub | flared_pad | choice | sampler 选；改写 `_wood_half()` 后端 profile（互斥）| Slot C 表 |
| palette_style | enum | natural_wood / painted_wood / colored_plastic / steel_spring_classic / colored_spring_pop | natural_wood | palette | palette only，**不计入 slot_choice**；每 seed 采一套（木 / 漆 / 塑料体色 + 钢 / 彩弹簧，见下表）| 各样本材质（parent L210-211 等）|
| leg_len_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 `LEG_LEN`（全峰长）→ 联动 `NOSE_X`/`BACK_X`/PIVOT_X、spring 腿长、teeth 区间，clamp | parent L62 |
| half_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 `HALF_W`（单腿宽 / 世界 Z 厚）→ 联动 seat 通宽 / spring `STRIP_W` / lift HALF_W/2，clamp | parent L63 |
| pivot_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 pivot bulge 高 `z_pivot`（保 ≥ SEAT_R 上桥接），clamp | parent L97 (`z_pivot`) |
| spring_radius_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 torsion_coil 有效；缩放 `SPRING_R`/`WIRE_R`/`SEAT_R`（保 coil captured 进 seat 过盈带），clamp | parent L77-79 |
| leaf_strip_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 leaf_spring 有效；缩放 `STRIP_T`/`STRIP_W`/`ARM_LEN`/`SEAT_L/W/D`（保臂 captured 进矩形 seat），clamp | leaf_spring L73-80 |
| pivot_open_scale | float | [0.80, 1.10] | 1.0 | independent | 缩放 `pivot` `motion_limits.upper`（PIVOT_MAX）；clamp 到 ≤ tail-contact 角（约 0.176-0.180，见 PIVOT_MAX 表）保两腿全程不穿模 | parent L84 / leaf_spring L85 |
| barrel_radius_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 jaw=rounded_barrel 有效；缩放 `BARREL_R`（保 nose 圆头读作 barrel），clamp | rounded_jaw L85 |
| tooth_pitch_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 jaw=toothed_serrated 有效；缩放 `TOOTH_PITCH`（`_N_TEETH` 随之派生，保 ≥4 齿），clamp | toothed_jaw L165-169 |
| dish_depth_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 tail=dished_thumb 有效；缩放 `DISH_DEPTH`/`PAD_BULGE`（保凹坑不切穿木腿、pad 不撞 spring），clamp | dished_tail L89-91 |
| (—) | constraint | — | — | inequality | spring captured 过盈带：`seat_r/seat_box ≥ coil_outer/strip_extent − embed`，embed∈[0.0004,0.0008]；违反则同步放大 seat 保 coil/leaf captured（圆 SEAT_R 随 SPRING_R、矩形 box 随 STRIP）| parent L145-152 / leaf_spring L138-143 |
| (—) | constraint | — | — | inequality | pivot 上限不致两腿穿模：`PIVOT_MAX·pivot_open_scale ≤ asin(2·tan(TAIL_ANGLE)+GAP/(PIVOT_X−BACK_X)) − margin`（约 0.176-0.180 减 margin）；违反按比例缩 PIVOT_MAX | parent L81-84 / leaf_spring L82-85 |
| (—) | constraint | — | — | inequality | pivot bulge 桥接 seat：`z_pivot·pivot_height_scale ≥ SEAT_R(或 box 深)·spring_*_scale + wood_bridge_min`（约 0.001）；保木腿在 seat 上方仍有壁桥过 spring barrel；违反抬高 z_pivot | parent L141-152 |
| (—) | constraint | — | — | inequality | 闭合前颚近触：q=0 时两腿 parting face Y 向 `max_gap≈0.004`、`max_penetration≤0.0002`；违反调 GAP / parting profile（照搬样本 expect_gap）| parent L385-392 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**；跨样本观察 + 真实 clothes peg 材质 / 色集合理外推）：
| palette_style | 木腿 / 体 | 弹簧 | 备注 / 来源 |
|---|---|---|---|
| natural_wood（默认）| worn_wood (0.42,0.29,0.17) | dark_steel (0.16,0.16,0.18) | parent / rounded / toothed / dished / square 5 样本配色 |
| painted_wood | 漆面木（白 / 红 / 蓝彩漆覆木纹）| dark_steel | 真实彩漆木夹外推（体色 + 同款暗钢扭簧）|
| colored_plastic | 彩色塑料体（鲜红 / 蓝 / 绿 / 黄高饱和）| spring_steel (0.35,0.38,0.42) | 塑料衣夹外推（亮色塑料 + 亮钢弹簧；leaf_spring 的 `spring_steel` L177 复用）|
| steel_spring_classic | worn_wood | spring_steel (0.35,0.38,0.42) | 木腿 + 亮钢板 / 扭簧（leaf_spring 样本 `spring_steel` 配色）|
| colored_spring_pop | natural_wood 或浅木 | 彩色喷漆弹簧（金 / 铜 / 彩钢）| 弹簧着色外推（保木 / 弹簧材质对比）|

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / 过盈带 / clearance，**绝不改变 spring_mechanism / jaw_shape / tail_shape 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（spring_mechanism / jaw_shape / tail_shape，外加 root `lower_half` + revolute `upper_half` + fixed spring 三块件）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 形成结构差异轴。source map 已确认无 multiplicity 轴。
- **两块木腿共用一个 `_wood_half()` solid（非复制循环）**：因角色不同（`lower_half` root / `upper_half` revolute child）是两份具名 part，**正确**——不是 `× N 同构子件`。rounded_barrel 样本用 `for i in range(2)` 发射 `half_{i}`（rounded_jaw L238-250），但这是**风格化的两份具名腿发射**，拓扑等价（仍是 root + revolute child 两份），非可变 multiplicity；模板可统一写两份具名 part 或 range(2)，结果等价。
- **存在固定 N 的对称 / 阵列 visual（非可变轴，不进 slot_choice）**：
  - leaf_spring 的 `arm_0`/`arm_1`：源用 `for i in range(2)` + 共享 `_leaf_spring_arm(sign)` helper、对称 placement、统一 visual-on-part policy（leaf_spring L220-228），固定 N=2（两臂）。
  - toothed_serrated 的 V 槽 teeth：源用 `for i in range(_N_TEETH)`（`_N_TEETH` 按 `(TEETH_END_X−TEETH_START_X)/TOOTH_PITCH` 算，toothed_jaw L169, L180-194）；这是 **module-local 装饰阵列**（FIXED 语义 visual cut，非可变产品域）——随 toothed_serrated module 由 pitch 派生 N（≥4），不暴露为可变 count 轴。`tooth_pitch_scale`（§7 conditional）只缩 pitch、N 随派生，不作 multiplicity 轴。
  - torsion_coil 的 coil：源是一根 `tube_from_spline_points` 一体扫掠管（coil + 两条腿），**无需循环**（parent L197-203）。
- 这些都是 **module-local 固定多份 / 一体 visual**（两臂 / V 槽 / 一体扫掠），按 module 而非 multiplicity 轴声明——不存在「任意 N 个弹簧 / N 个颚」的真实产品域。copied object 用共享 helper 发射、对称 / 等距 placement，无独立 joint（FIXED / cut 装饰，Rule 1）。

## 拓扑多样性审计

总组合数：spring_mechanism(2) × jaw_shape(3) × tail_shape(3) = **18**（全部正交合法，见 §9 兼容矩阵——三轴几何正交，无非法组合需 gate）。

仅 jaw(3) × tail(3) = **9**（已接近机械门控）；叠 spring(2) → 18 ≥ 10 稳过。所有 18 组合共享同一 joint 拓扑等价类「1 REVOLUTE `pivot` + 1 FIXED `lower_to_spring`」——distinct 来自 spring 件几何 / seat 形态、前端颚 profile、后端尾 profile 的笛卡尔积（part 树名 + 关键 helper / mesh 形态不同），**编入 `slot_choices_for_seed` 的 tuple**（`("spring_mechanism", m)`、`("jaw_shape", m)`、`("tail_shape", m)`）即天然 18 distinct。


seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（spring_mechanism / jaw_shape / tail_shape），经兼容矩阵合法化（本类三轴正交，无非法组合需排除，仅做 conditional scale 解析），再 uniform 各 independent 连续 scale + 解析 conditional scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看闭合姿态前颚近触 + 开 pose 不穿模 + leaf vs coil 弹簧形态 + 三种 jaw / tail 形态）。


Controlled local parameterization：见 §参数表的 leg_len_scale / half_width_scale / pivot_height_scale / pivot_open_scale（independent）+ spring_radius_scale（@torsion_coil）/ leaf_strip_scale（@leaf_spring）/ barrel_radius_scale（@rounded_barrel）/ tooth_pitch_scale（@toothed_serrated）/ dish_depth_scale（@dished_thumb）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：spring_radius 仅 torsion_coil、leaf_strip 仅 leaf_spring、barrel_radius 仅 rounded_barrel、tooth_pitch 仅 toothed_serrated、dish_depth 仅 dished_thumb）→ 采 independent 峰长 / 腿宽 / pivot 高 / 开角 scale → 派生（NOSE_X/BACK_X 随 LEG_LEN、seat 随 spring scale、`_N_TEETH` 随 tooth_pitch、lift HALF_W/2 随 half_width）→ 用四条 inequality（spring 过盈带、pivot 上限不穿模、pivot bulge 桥接 seat、闭合前颚近触）投影 / 回缩。跨部件依赖（seat vs coil/leaf、PIVOT_MAX vs tail relief、z_pivot vs SEAT_R）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 pivot/FIXED joint origin、spring captured 接口、共享 `_wood_half()` solid 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（spring_mechanism/jaw_shape/tail_shape），再解析 conditional scale，再 uniform 各 independent scale，采 palette_style | slot_choices_for_seed 含 `("spring_mechanism",m)`/`("jaw_shape",m)`/`("tail_shape",m)` 且与 build 一致 |
| compatibility matrix | **三轴正交，全 18 组合合法**——前端 jaw / 后端 tail / 中部 spring seat 几何互不干涉，无非法组合需 gate。仅 conditional 解析：(1) spring_radius_scale 仅 torsion_coil 生效；(2) leaf_strip_scale 仅 leaf_spring 生效；(3) barrel_radius_scale 仅 rounded_barrel 生效；(4) tooth_pitch_scale 仅 toothed_serrated 生效（`_N_TEETH` 派生 ≥4）；(5) dish_depth_scale 仅 dished_thumb 生效；(6) leaf_spring 的 PIVOT_MAX 基线偏小（0.10 vs coil 0.16），pivot_open_scale clamp 上限随 spring_mechanism 解析 | 无 floating / 两腿穿模 / spring 不进 seat / 前颚不闭合 / 凹坑切穿 / 开角超 tail-contact |
| controlled local variation | 4 independent + 5 conditional clamped scale，每 build 统一；conditional 随 slot 解析 | 比例变化不破坏 pivot/FIXED origin、spring captured、闭合前颚、共享 solid、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 spring/jaw/tail 机构 QC（coil vs leaf / 三 jaw / 三 tail / 闭合 + 开 pose）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| spring_mechanism (A) | 2 | yes | no | torsion_coil / leaf_spring（**最薄一槽**；降级理由见 Slot A 注：真实 peg 弹簧词汇表仅扭簧 / 板簧两类，B×C=9 已撑组合）|
| jaw_shape (B) | 3 | yes | yes | flat_notched / rounded_barrel / toothed_serrated（前端 profile）|
| tail_shape (C) | 3 | yes | yes | flared_pad / dished_thumb / square_stub（后端 profile）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("spring_mechanism",m)`/`("jaw_shape",m)`/`("tail_shape",m)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；spring_radius/leaf_strip/barrel_radius/tooth_pitch/dish_depth 为 conditional 随 spring/jaw/tail 解析；四条 inequality（spring 过盈带、pivot 上限不穿模、pivot bulge 桥接 seat、闭合前颚近触）在 resolve 内投影 / 回缩
- compatibility matrix 三轴正交无非法组合；conditional scale 仅在对应 module 生效（不在 torsion_coil 上设 leaf_strip、不在非圆头 jaw 上设 barrel_radius 等）
- 连续 scale clamp 后不破坏 pivot/FIXED joint origin、spring captured 接口、共享 `_wood_half()` solid、闭合前颚、类别身份
- 关键 joint：`pivot` REVOLUTE axis≈(0,−1,0)（`round(axis)==(0,−1,0)`，abs(axis[1])>0.99，全候选共享唯一 REVOLUTE）；`lower_to_spring` FIXED（全候选共享）；恰好 1 个非 fixed joint
- spring captured 过盈：element-scoped `allow_overlap(spring/leaf_spring, lower)` + `allow_overlap(spring/leaf_spring, upper)`，照搬各样本 run_tests 段（parent L303-312、leaf_spring L278-287）
- 共享 solid：`lower_half` / `upper_half` 用同一 `_wood_half()` solid 放两次（root vs revolute child 两份具名 part，非复制循环）；rounded_barrel 的 `half_{i}` range(2) 拓扑等价
- 固定阵列 visual 遵循 `arm_{i}`（leaf 两臂）/ V 槽 teeth（toothed）命名 + 共享 helper + 对称 / 等距 placement + Rule 1（无独立 joint）
- 闭合 pose：q=0 两腿 parting face Y 向近触 `expect_gap(max_gap≈0.004, max_penetration≤0.0002)`；开 pose q=PIVOT_MAX 不真实穿模（照搬样本 expect_gap 的 Y 投影 penetration 容差）
- grandfather：spring captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- peg 躺地：`lower` z_min≈0（abs<0.0005）

## Reject cases

- 把 spring / jaw / tail 当独立活动 part 加 joint（除 `pivot` REVOLUTE + `lower_to_spring` FIXED 外的非 fixed joint）→ 违反本类「单 pivot 对开 + 偏置弹簧」拓扑（所有样本恰好 1 REVOLUTE）。
- 把弹簧件做成可动 joint（spring 应 FIXED 偏置件，不是 actuated joint）→ 违反 `lower_to_spring` FIXED 语义。
- spring rest pose 设成 jaws 张开（q=upper）而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本 rest 闭合，前颚近触、后尾被 relief 撑开）。
- `pivot` origin 放在峰中心或任意点而非 fulcrum / spring barrel 轴（PIVOT_X, 0, HALF_W/2）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- PIVOT_MAX / pivot_open_scale 过大致两木腿穿模（超 tail-contact 角约 0.176-0.180）→ §7 第二条 inequality FAIL；须按比例缩 PIVOT_MAX 留 margin。
- spring seat 开得比 coil/leaf 大（无过盈）致弹簧件漂浮在 seat 内 → captured 不接触，`allow_overlap` 失去意义 / spring 漂浮 FAIL；seat 须比 coil/leaf 紧 embed∈[0.0004,0.0008]。
- pivot bulge `z_pivot` 缩到 < SEAT_R 致木腿在 spring barrel 上方无壁桥接（seat 切穿到顶）→ §7 第三条 inequality FAIL；保 z_pivot ≥ SEAT_R + bridge。
- dished_thumb 的 `DISH_DEPTH` 过深切穿木腿或撞 spring → §7 dish 约束 FAIL；clamp 凹坑深 + 抬 pad。
- 给 spring captured 过盈接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把两木腿做成复制循环 `for i in range(2)` 但用同一 root/joint role → 两腿角色不同（root vs revolute child），应是两份具名 part（rounded_jaw 的 `half_{i}` 是风格化拓扑等价，可接受；但不可把它当可变 multiplicity 轴）。
- 把连续尺寸 / 颜色 / 材质（palette_style / 峰长 / barrel 半径 / 齿距）当新 candidate 塞进 slot → 不是结构差异。
- 把 binder clip / clamp / pliers / living-hinge 语义混入（金属杠杆夹 / 螺杆进给 / 双臂剪 / 无独立弹簧件活铰）→ 出类，本类是木腿单 pivot 对开弹簧夹。

## 与相邻类别的边界

- 不该混入：**binder clip / 文具弹簧夹 / 鳄鱼夹（clip）**——金属杠杆 / 长把手弹簧夹纸，无木腿 / 无 barrel-seat 扭簧 / 板簧；已有独立 slug `clip`。
- 不该混入：**螺旋夹 / C 形 / G 形手夹（clamp）**——螺杆 PRISMATIC 进给 + C 形 frame，主运动 spine 是直线进给非两臂对开 REVOLUTE；已有独立 slug `clamp`。
- 不该混入：**钳子 / 老虎钳（pliers）**——双臂绕中心 pivot 剪切，虽同为对开 REVOLUTE，但无偏置弹簧件 / 无 relieved 尾面常闭机构、是金属工具。
- 不该混入：**塑料活铰一体夹（living-hinge clip）**——一体注塑、塑料薄铰回弹无独立弹簧件，会改 `pivot`/`lower_to_spring` 拓扑结构；如需可作 Slot A 第三候选但须先回 fork 池补造验证（见 Slot A 降级注 + §13）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **Slot A 仅 2 candidate（torsion_coil / leaf_spring）** 的降级理由是否接受（真实 peg 弹簧词汇表仅扭簧 / 板簧两类，B×C=9 已撑组合到 18），还是要求回 fork 池补造 living-hinge 一体活铰作第三候选（须 fork 验证拓扑变更）；(2) 两木腿共用 `_wood_half()` solid = 两份具名 part（非复制循环），rounded_barrel 的 `half_{i}` range(2) 视为拓扑等价是否接受；(3) 全 18 组合共享单 pivot 对开 joint 拓扑类（无 joint 数 / 类型差异，是本小类真实特征），Topology target 18<300 的说明是否接受；(4) palette_style 5 套（natural_wood 为样本配色，painted_wood/colored_plastic/colored_spring_pop 为真实 peg 材质合理外推）是否合适；(5) leaf_spring 的 PIVOT_MAX 基线偏小（0.10 vs coil 0.16），pivot_open_scale clamp 上限随 spring_mechanism conditional 解析是否正确；(6) spring captured 过盈 grandfather + allow_overlap、无 multiplicity 轴是否符合期望）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **坐标统一**：全部 6 样本完全共享同一 spine（peg 躺平、长轴 X、两腿沿 Y、pivot axis=(0,−1,0)、origin=(PIVOT_X,0,HALF_W/2)+rpy=(π/2,0,0)、lower_to_spring FIXED）——**无需 rebase**，模板直接沿用。
- **共享 helper**：
  - `_wood_half(jaw_shape, tail_shape)`：按 Slot B 切前端 profile（flat+groove / barrel 弧 / 平颚+`_cut_serrated_teeth()`）、按 Slot C 切后端 profile（flared pad / 抬 pad+`dish_sphere` / 钝 stub）、按 Slot A 切 spring seat（圆 `SEAT_R` / 矩形 `SEAT_L×W×D` box）。这是模板核心——一份参数化 solid helper 覆盖 B×C×(A 的 seat) 全组合，放两次发射 `lower_half`/`upper_half`。
  - `_spring_mesh()`（torsion_coil 的一体 `tube_from_spline_points` 扫掠管，parent L157-204）/ `_leaf_spring_arm(sign)` + `_leaf_spring_bend()`（leaf_spring 的两臂循环 + bend，leaf_spring L148-170）：按 Slot A 切弹簧件 helper。
  - `_cut_serrated_teeth(leg)`（toothed_serrated 的 V 槽 `for i in range(_N_TEETH)` 阵列，toothed_jaw L172-196）：仅 jaw=toothed_serrated 调用。
- captured 接口 allow_overlap：`run_clothes_peg_tests` 里逐 spring module 补 element-scoped `allow_overlap(spring/leaf_spring, lower)` + `allow_overlap(spring/leaf_spring, upper)`，照搬样本 run_tests 段（parent L303-312、leaf_spring L278-287）。
- conditional 范围解析顺序：先采 spring_mechanism / jaw_shape / tail_shape → 解析 spring_radius（仅 coil）/ leaf_strip（仅 leaf）/ barrel_radius（仅 rounded）/ tooth_pitch（仅 toothed，派生 `_N_TEETH`）/ dish_depth（仅 dished）/ PIVOT_MAX 基线（随 spring_mechanism：coil 0.16、leaf 0.10）→ 采 independent 峰长 / 腿宽 / pivot 高 / 开角 scale → 派生 NOSE_X/BACK_X/PIVOT_X、seat、lift → 投影四条 inequality（过盈带、pivot 不穿模、bulge 桥接 seat、闭合近触）。
- 两腿发射注记：源 parent 用两份具名 part（`lower_half` root + `upper_half` revolute child，parent L225-250），rounded_jaw 用 `for i in range(2)` 发射 `half_{i}`（rounded_jaw L238-250）——拓扑等价；模板可统一写两份具名 part（更清晰角色区分）或 range(2)，注意 lower 是 root（origin=(0,GAP/2,HALF_W/2),rpy=(−π/2,0,0)）、upper 是 revolute child（visual origin=(−PIVOT_X,0,GAP/2)）。
- 参考模板：选运动拓扑相近的——root + 单 REVOLUTE child + FIXED 偏置件 + 共享几何 helper（cushion 的 base + lid REVOLUTE / clamp 的 frame + 可选 screw_to_pad REVOLUTE）；clothes_peg 的 lower_half→upper_half REVOLUTE + lower_to_spring FIXED 与之同构，但更简（单 REVOLUTE、三轴全改写共享 `_wood_half()` solid、无 multiplicity）。clothes_peg 尺度极小（peg ~0.072m、HALF_W ~0.0085m、seat ~0.005m），joint origin 与 captured seat 须精确落真实硬件面（≤0.015m baseline；spring 过盈 embed ~0.0004-0.0008m）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| torsion_coil + flat_notched + flared_pad | rec_build-...-clot_...add41790 | `_wood_half` L87-154（flat parting + groove L131-139 + 圆 SEAT_R seat L145-152 + flared pad L95,L110-112）/ `_spring_mesh` 扭簧 L157-204 / `pivot` REVOLUTE L274-287 / `lower_to_spring` FIXED L266-272 / allow_overlap L303-312 / 材质 L210-211 | 基线 spine 坐标约定 + 扭簧（圆 seat）+ 平颚+夹线 groove + 外翻平指垫 + captured spring 范式 + natural_wood palette |
| S2 | A | leaf_spring | rec_clothes_peg_var_leaf_spring | `leaf_spring` part L211-237（`arm_{i}` for range(2) L220-228 + bend L231-237）/ `_leaf_spring_arm(sign)` L148-162 / `_leaf_spring_bend` L165-170 / 矩形 box seat L138-143 / FIXED L241-247 / allow_overlap L278-287 / PIVOT_MAX=0.10 L85 / `spring_steel` 材质 L177 | 板簧（两臂循环 + bend + 矩形 seat）+ leaf PIVOT_MAX 基线 + spring_steel palette |
| S3 | B | rounded_barrel | rec_clothes_peg_var_rounded_jaw | `_wood_half` 半圆弧 nose（`arc_pts` 循环 L110-133，`BARREL_R` L85，无 groove）/ `half_{i}` for range(2) L238-250 | 圆头 barrel 颚 profile（拓扑等价两腿 range(2) 发射范式）|
| S4 | B | toothed_serrated | rec_clothes_peg_var_toothed_jaw | `_cut_serrated_teeth` V 槽 `for i in range(_N_TEETH)` L172-196 / 齿常数 `TOOTH_PITCH`/`TOOTH_DEPTH`/`TEETH_START_X`/`TEETH_END_X`/`_N_TEETH` L165-169 / 调用 L159 | 锯齿颚（module-internal V 槽阵列循环）|
| S5 | C | dished_thumb | rec_clothes_peg_var_dished_tail | `_wood_half` 抬 pad profile L116-128（`PAD_BULGE`/`Z_BACK` L85,L91）+ `dish_sphere` 球凹 cut L170-183（`DISH_R`/`DISH_DEPTH` L89-90）| 凹拇指坑 pressing pad 后端 profile |
| S6 | C | square_stub | rec_clothes_peg_var_square_tail | `_wood_half` 钝平顶 stub 后端 profile L101-111（`z_back=0.0075` L95，无 flare 点）/ 后端 stub 断言 L434-460 | 钝方指 stub 后端 profile |
