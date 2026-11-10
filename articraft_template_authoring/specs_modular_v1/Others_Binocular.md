# Binocular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `binocular` |
| template path | `agent/templates/Others_Binocular.py` |
| test path (optional) | `tests/agent/test_binocular_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：根 `hinge_bridge`（中央铰链桥）下挂 `left_barrel` / `right_barrel`（平行 fold 子件，恒为 ×2）+ 中央 `focus_wheel`（平行子件）；diopter ring / individual focus ring / twist-up eyecup collar 为 barrel 上的链式子件。固定 named slots（无模板级复制数量轴；barrel 恒为 BI-noculars 的定义而非可变 N）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | all 5-star samples in this category: `model.py` 全文 + `record.json` rating 字段已读 |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

6 个 5★ 样本（1 parent + 5 variants，全部 rating=5，全部 compile=success、workbench-only、≥1 非 fixed joint、仍明确读作双筒望远镜）逐条阅读摘要：

- **P1 `rec_model-a-pair-of-classic-porro-prism-binoculars-2_...a1874ba2`** — Porro 基线（**全批 fork 母资产**）。根 `hinge_bridge`（中央 +X 轴 axle + 前后 cap，L204-222）；`_add_barrel(model, name, side, sleeve_xs, mats)`（L108-187）以 `side=±1` 镜像发射左右筒：宽阶梯 objective tube 轴外侧（`OBJ_Y=0.065`）、slim eyepiece 轴内侧（`EYE_Y=0.032`，IPD≈64 mm），`_housing_mesh` 阶梯棱镜罩跨接两轴；hinge lug（sleeve + arm）经 `zip(...)` 循环发射且经 `allow_overlap` 捕获在 axle 上。4 个非 fixed joint：`bridge_to_left/right_barrel`（REVOLUTE +X，±25° 对向折叠 fold，L228-248）、`bridge_to_focus_wheel`（CONTINUOUS +X，中央调焦轮，L250-272）、`right_barrel_to_diopter_ring`（REVOLUTE +X，±60° 右目镜屈光度环，L274-300）。run_tests 验证 fold IPD 收窄/eyecup 下沉、focus wheel 在轴心 continuous、diopter ±60°、lens 凹陷、hinge lug 捕获。这是 ★★★★★ 可读性契约样板：helper 镜像发射 + zip 循环 + 凹陷 lens + 显式 captured-pin allow_overlap。

- **`rec_binocular_var_roof_prism`** — 现代直筒 roof-prism 双筒。关键差异在 Slot A：`_barrel_body_mesh`（L63-91）是**单段等径直筒** lathe（objective 与 eyepiece **同轴**，无横向阶梯步进），`IPD_HALF=0.032` 两筒近距平行；`_add_barrel`（L113-196）不再发射 `prism_housing`，objective lens / eyepiece ring / eyecup / ocular lens 全部坐落在同一 `barrel_y=side*IPD_HALF` 轴上。保留 4 关节拓扑（fold×2 + focus wheel + diopter），bridge axle 缩短（`AXLE_LEN=0.082`，L60/218-240）。run_tests 显式断言 objective 与 eyecup 同 Y/同 Z（直筒身份），IPD≈64 mm，紧凑宽度 ~0.12 m。结构干净，是 roof_straight 候选的权威源。

- **`rec_binocular_var_reverse_porro`** — 紧凑 reverse-Porro 双筒。Slot A 反置：`OBJ_Y=0.026`（objective 轴**内移 INBOARD**）、`EYE_Y=0.038`（eyepiece 轴**外展 OUTBOARD**，L46-47），`_objective_tube_mesh` 短粗、`_housing_mesh`（L107-119，`housing_cy=(OBJ_Y+EYE_Y)/2`）反向跨接；整体收小（envelope ~0.13–0.16 × 0.10–0.14 × 0.04–0.06 m，`HINGE_Z=0.025`）。保留 4 关节拓扑。run_tests 断言 `side*eye_cy > side*obj_cy`（eyepiece 比 objective 更外侧），objective≈±26 mm inboard、eyepiece≈±38 mm outboard。这是 reverse_porro_compact 候选源，也是 overall_size_scale 收小子域的参照。

- **`rec_binocular_var_individual_focus`** — 海军式独立调焦（IF）。Slot B 候选：**删除中央 focus_wheel 与 diopter_ring**，改为左右目镜各一 `focus_ring_{i}`（`for i in range(2)` 循环，L266-295），`_focus_ring_mesh`（L108-121）是带 `KnobBore(style="round", diameter=0.028)` 中孔的 knurled 环；`barrel_to_focus_ring_{i}`（REVOLUTE +X，±60°）父为各自 barrel。run_tests 显式断言 `"focus_wheel" not in part_names`（L484-490）、两环父分别为 left/right barrel（L492-502）。这是 individual_focus 候选源，确立"目镜端 REVOLUTE 调焦环"拓扑。

- **`rec_binocular_var_fixed_focus`** — 免调焦/密封定焦（marine-style）。Slot B 候选：**完全无 focus_wheel / 无 diopter_ring**（part 与 joint 皆删，L187-246 仅 bridge + 2 barrel + 2 fold joint）；唯一 articulation 是中央 fold hinge。run_tests 显式断言无 focus_wheel/diopter part 与 joint、恰好 3 parts、恰好 2 articulations、目镜无 diopter visual（L258-290）。这是 fixed_focus 候选源，是"最少非 fixed joint = 仅 fold×2"的下界拓扑。

- **`rec_binocular_var_twist_eyecup`** — 旋升/伸缩眼罩（戴镜者用）。Slot C 候选：保留 4 关节（fold×2 + focus wheel + diopter），并在目镜端追加 `eyecup_collar_{i}`（`enumerate(barrel_objs)` 循环，L328-351），`_twist_up_eyecup_collar_mesh`（L91-120）是带 helical 槽的刚性 lathe 收筒；`{left,right}_barrel_to_eyecup_collar_{i}`（**PRISMATIC**，axis=(-1,0,0)，0→`EYECUP_TRAVEL=0.008` m，沿视轴外伸）。注意：本样本把软橡胶 eyecup 替换成刚性 collar，eyepiece 增加 `eyepiece_body` 支撑（L179-184）。run_tests 断言 prismatic 类型/轴/行程、collar 在视轴、伸出时 X 更负且仍捕获 ring（L555-645）。这是 twist_up 候选源，确立"目镜端 PRISMATIC 伸缩眼罩"拓扑。

跨样本观察：所有 6 样本共享 `hinge_bridge` 根 + `_add_barrel` 镜像 helper + `ROT_Z_TO_PX/NX` 视轴映射 + captured-pin `allow_overlap` 契约 + 凹陷 lens 检查 + fold IPD/drop 检查。差异严格落在三个轴上：**(A) barrel/prism 光学排布**、**(B) 调焦机构**、**(C) 眼罩形态**。配色高度一致（matte-black rubber armor + dark-gray hinge metal + amber objective lens + dark ocular glass + black knurl），为 §7 `palette_style` 提供基线 + 可派生 colorway。

## 核心身份

双筒望远镜（binocular）：**两支镜像光学筒**经**中央铰链桥**连接，可绕纵向（视轴方向 +X）铰链轴做 interpupillary fold（瞳距调节）。世界系约定：+X 为视向（objective 面 +X，eyecup 面 -X），+Z 向上，物体以 objective 筒近 z=0 着地，中央 hinge axle 沿 X 在 y=0、z=`HINGE_Z`。

成熟域：经典 20×50 中央铰链双筒（Porro 或 roof-prism），含两支等价光学筒（objective tube + prism housing/直筒 + eyepiece + eyecup + recessed lens 两端）、中央 fold hinge×2，以及可选的调焦机构（中央轮 + 屈光度环 / 左右独立环 / 无）与可选的伸缩眼罩。身份强约束：

- **必须**有恰好 2 支镜像光学筒（不是 1 支、不是 3 支）。
- **必须**有中央铰链桥 + 两个 REVOLUTE fold joint（绕同一 +X 纵轴对向折叠）。
- **必须**两端凹陷 lens（objective amber / ocular dark），objective 在前（+X）、eyecup 在后（-X）。
- 调焦/眼罩机构可变（即 Slot B / Slot C），但 fold 与双筒身份不可缺。

边界（不该混入）：

- 不混入 `astronomical_telescope_on_tripod`（单 OTA + tripod/equatorial/altaz 指向 mount；双筒无 tripod、无 az/alt 指向链、是双光学轴）。
- 不混入 `camera_lens` / `camcorder`（消费摄影光学，无双筒铰链、无 fold、无双轴）。
- 不混入 monocular / spotting scope（单筒；缺第二支镜像光学筒与中央铰链）。

## 槽位 + 候选模块表

### Slot A：barrel_prism_layout（主 footprint 槽——光学筒 / 棱镜排布；决定两支镜像 barrel 的 part 树 + 光学轴排布）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `porro_offset`（基线） | P1 `rec_model-a-pair-of-classic-porro-prism-binoculars-2_...a1874ba2` | `model.py:L63-L79`(objective mesh)、`L101-L105`(housing mesh)、`L108-L187`(`_add_barrel`)、`L37-L48`(offset 常量) | eligible if compatible | 经典阶梯偏置 Porro：objective 轴外侧 `OBJ_Y=0.065`、eyepiece 轴内侧 `EYE_Y=0.032`，`prism_housing` 跨接两轴；宽 W 形（width≈0.19 m）。barrel part 含 objective_tube / objective_lens / prism_housing / eyepiece_tube / eyepiece_ring / eyecup / ocular_lens + hinge lugs。 |
| `roof_straight` | `rec_binocular_var_roof_prism` | `model.py:L63-L91`(`_barrel_body_mesh`)、`L113-L196`(`_add_barrel`)、`L36-L60`(IPD/length 常量) | eligible if compatible | 现代直筒 roof-prism：objective 与 eyepiece **同轴**单段等径筒（无 prism_housing、无横向阶梯），两筒近距平行 `IPD_HALF=0.032`；窄长形（width≈0.12 m）。barrel part 含 barrel_body / objective_lens / eyepiece_ring / eyecup / ocular_lens + hinge lugs。**part 树拓扑不同**（无 housing part）。 |
| `reverse_porro_compact` | `rec_binocular_var_reverse_porro` | `model.py:L69-L85`(objective mesh)、`L107-L119`(housing mesh)、`L122-L208`(`_add_barrel`)、`L43-L53`(offset 常量) | eligible if compatible | 紧凑 reverse-Porro：objective 轴**内移** `OBJ_Y=0.026`、eyepiece 轴**外展** `EYE_Y=0.038`（与 `porro_offset` 横向偏置反置），`_housing_mesh` 反向跨接；整体收小（envelope ~0.13–0.16 m）。barrel part 树与 `porro_offset` 同名但偏置/朝向反转。 |

> Slot A 三候选结构差异充分：`porro_offset` vs `reverse_porro_compact` 是横向 OBJ/EYE 偏置反置（不同的 housing 跨接方向 + footprint），`roof_straight` 是**删除 prism_housing part 的单轴直筒**（part 树拓扑变化）。三者不只是尺寸/颜色差异。

### Slot B：focus_mechanism（主机构槽——调焦机构；决定中央/目镜端的 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `center_wheel_diopter`（基线） | P1 `rec_model-a-pair-of-classic-porro-prism-binoculars-2_...a1874ba2` | `model.py:L250-L272`(focus_wheel part + `bridge_to_focus_wheel` CONTINUOUS)、`L274-L300`(diopter_ring part + `right_barrel_to_diopter_ring` REVOLUTE) | eligible if compatible | 中央调焦轮（`focus_wheel` knurled KnobGeometry，**CONTINUOUS** +X，捕获在中央 axle）+ 右目镜屈光度环（`diopter_ring`，**REVOLUTE** +X ±60°，捕获在右 eyepiece tube）。两个独立调焦件，joint 拓扑 = CONTINUOUS + REVOLUTE。 |
| `individual_focus` | `rec_binocular_var_individual_focus` | `model.py:L108-L121`(`_focus_ring_mesh`)、`L266-L295`(`focus_ring_{i}` `for i in range(2)` + `barrel_to_focus_ring_{i}` REVOLUTE)、断言 `L484-L502` | eligible if compatible | 海军式独立调焦：**无中央轮、无 diopter**；左右目镜各一 `focus_ring_{i}`（knurled + `KnobBore` 中孔），`barrel_to_focus_ring_{i}` **REVOLUTE** +X ±60°，父为各自 barrel。joint 拓扑 = 2× REVOLUTE（目镜端）。 |
| `fixed_focus` | `rec_binocular_var_fixed_focus` | `model.py:L187-L246`(仅 bridge + 2 barrel + 2 fold joint，无 focus/diopter part 或 joint)、断言 `L258-L290` | eligible if compatible | 免调焦/密封定焦（marine-style）：**完全无 focus_wheel / 无 diopter_ring** part 或 joint；唯一非 fixed articulation 是中央 fold hinge×2。joint 拓扑 = 无调焦件（恰好 3 parts / 2 joints）。 |

> Slot B 三候选跨 **CONTINUOUS+REVOLUTE / 2×REVOLUTE / 无** 三种 joint 拓扑，是本模板拓扑多样性的主驱动槽。

### Slot C：eyecup_style（目镜罩形态；决定眼罩 part 是否为活动件 + joint 类型）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rubber_fold`（基线） | P1 `rec_model-a-pair-of-classic-porro-prism-binoculars-2_...a1874ba2` | `model.py:L82-L98`(`_eyecup_mesh`)、`L157-L162`(barrel 内 eyecup visual 发射，无 joint) | eligible if compatible | 固定折叠软橡胶眼罩：`_eyecup_mesh` lathe 软罩作为 **barrel visual（无独立 part、无 joint）**，沿 -X 朝向。眼罩不活动。 |
| `twist_up` | `rec_binocular_var_twist_eyecup` | `model.py:L91-L120`(`_twist_up_eyecup_collar_mesh`)、`L328-L351`(`eyecup_collar_{i}` 循环 + `{left,right}_barrel_to_eyecup_collar_{i}` PRISMATIC) | eligible if compatible | 旋升/伸缩刚性眼罩：左右各一 `eyecup_collar_{i}` **独立 part**（带 helical 槽刚性 lathe collar），`{barrel}_to_eyecup_collar_{i}` **PRISMATIC** axis=(-1,0,0)，0→0.008 m 沿视轴外伸；目镜增 `eyepiece_body` 支撑。眼罩为活动 PRISMATIC 子件。 |

> **Slot C 仅 2 候选（理由）**：眼罩的真实结构词汇表本质就是「固定折叠软罩」vs「旋升伸缩刚性 collar」两族——翼形/卷边只是折叠族的外观微变（同一 `rubber_fold` 拓扑 + 不同 mesh profile），**不是新 part 树 / 新 joint 拓扑**，按 `SPEC_TEMPLATE.md §4`「样本池不足时可降到 2 并说明理由」处置。差异已足够：`rubber_fold` 是无 joint 的 barrel visual，`twist_up` 是 PRISMATIC 活动 part。下游若要第 3 候选可加 `winged_fold`（仍属折叠族，需新增 5★ 源）。

## 槽位图（slot graph）

pattern = `mixed`（parallel children + per-barrel side branches）

```
[hinge_bridge]  (root：中央 axle 沿 +X，y=0，z=HINGE_Z；前后 cap)
   |
   |-- [Slot A: left_barrel ]  --REVOLUTE bridge_to_left_barrel (axis +X, origin (0,0,HINGE_Z), ±25°)-->
   |-- [Slot A: right_barrel]  --REVOLUTE bridge_to_right_barrel(axis +X, origin (0,0,HINGE_Z), ±25°)-->
   |        (两支镜像 barrel；side=±1；hinge lug sleeve 捕获在中央 axle 上)
   |
   |-- [Slot B 中央分支: focus_wheel]  --CONTINUOUS bridge_to_focus_wheel (axis +X, origin (FOCUS_WHEEL_X,0,HINGE_Z))-->
   |        (仅 center_wheel_diopter 启用；捕获在中央 axle)
   |
   +-- [Slot B 目镜分支] / [Slot C 目镜分支]：挂在 barrel 上的链式子件
            · center_wheel_diopter: right_barrel --REVOLUTE right_barrel_to_diopter_ring (axis +X, origin (DIOPTER_X,-EYE_Y,0), ±60°)--> diopter_ring
            · individual_focus:     barrel_{i}   --REVOLUTE barrel_to_focus_ring_{i} (axis +X, origin (FOCUS_RING_X, side*EYE_Y,0), ±60°)--> focus_ring_{i}
            · fixed_focus:          (无目镜端调焦子件)
            · twist_up:             barrel_{i}   --PRISMATIC {barrel}_to_eyecup_collar_{i} (axis -X, origin (EYECUP_MOUNT_X, side*EYE_Y,0), 0→0.008)--> eyecup_collar_{i}
```

接口点位与装配说明：

- **bridge → barrel（fold）**：joint origin 在中央 axle 轴 `(0,0,HINGE_Z)`，axis=+X；barrel part 帧坐落在该轴上，绕自身 +X 折叠。hinge lug `*_hinge_sleeve` 捕获在 `hinge_axle` 上（element-scoped `allow_overlap`），`*_hinge_arm` 伸进 barrel 本体。左右 sleeve 沿 axle 交错排布（`LEFT_SLEEVE_XS` / `RIGHT_SLEEVE_XS`）。
- **bridge → focus_wheel（仅 B=center_wheel_diopter）**：joint origin `(FOCUS_WHEEL_X,0,HINGE_Z)`，CONTINUOUS +X；wheel 捕获在中央 axle。
- **barrel → 目镜端子件**：joint origin 在该 barrel 的 eyepiece 视轴 `(*_X, side*EYE_Y, 0)`，REVOLUTE +X（diopter / focus ring）或 PRISMATIC -X（twist-up collar）；子件捕获在 `eyepiece_tube` / `eyepiece_ring`（element-scoped `allow_overlap`）。
- **互斥 / 派生关系**：Slot B 三模块互斥（决定 focus_wheel/diopter/focus_ring 是否存在）。Slot C 决定 eyecup 是 barrel visual（rubber_fold）还是独立 PRISMATIC part（twist_up）。`EYE_Y` 的取值（内/外侧）由 Slot A 派生，目镜端所有子件（diopter/focus_ring/collar）的 joint origin Y 必须随 Slot A 的 `EYE_Y` 派生（接口一致性）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `porro_offset`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_barrel` / `right_barrel`（各含 objective_tube / objective_lens / prism_housing / eyepiece_tube / eyepiece_ring / eyecup / ocular_lens + front/rear hinge sleeve+arm） | P1 / model.py:L108-L187 |
| internal joints | 无（barrel 内部为 visual 组；hinge lug 为 visual） | P1 / model.py:L170-L185 |
| upstream interface | barrel 帧坐落于中央 hinge 轴 `(0,0,HINGE_Z)`；hinge sleeve 捕获在 `hinge_axle`（element allow_overlap） | P1 / model.py:L173-L185, L319-L327 |
| downstream interface | eyepiece 视轴 `(*, side*EYE_Y, 0)` 供 Slot B/C 目镜端子件挂接；`eyepiece_tube` / `eyepiece_ring` 为捕获面 | P1 / model.py:L145-L156 |

### Slot A / module `roof_straight`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_barrel` / `right_barrel`（各含 barrel_body 单段直筒 / objective_lens / eyepiece_ring / eyecup / ocular_lens + hinge sleeve+arm；**无 prism_housing**） | `rec_binocular_var_roof_prism` / model.py:L113-L196 |
| internal joints | 无 | — |
| upstream interface | barrel 帧坐落于中央 hinge 轴；hinge sleeve 捕获在缩短的 `hinge_axle`（`AXLE_LEN=0.082`） | model.py:L177-L194, L218-L240 |
| downstream interface | objective 与 eyepiece 同轴 `side*IPD_HALF`；diopter/ring 捕获面为 `barrel_body`（无独立 eyepiece_tube） | model.py:L150-L155, L352-L357 |

### Slot A / module `reverse_porro_compact`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_barrel` / `right_barrel`（objective_tube INBOARD / objective_lens / prism_housing 反向跨接 / eyepiece_tube OUTBOARD / eyepiece_ring / eyecup / ocular_lens + hinge lugs） | `rec_binocular_var_reverse_porro` / model.py:L122-L208 |
| internal joints | 无 | — |
| upstream interface | barrel 帧坐落于中央 hinge 轴（`HINGE_Z=0.025`） | model.py:L194-L206 |
| downstream interface | eyepiece 视轴外展 `side*EYE_Y`（`EYE_Y=0.038`）；捕获面 `eyepiece_tube` | model.py:L166-L177 |

### Slot B / module `center_wheel_diopter`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `focus_wheel`（中央 knurled 轮）+ `diopter_ring`（右目镜 knurled 环） | P1 / model.py:L251-L263, L275-L287 |
| internal joints | `bridge_to_focus_wheel`（CONTINUOUS +X）、`right_barrel_to_diopter_ring`（REVOLUTE +X ±60°） | P1 / model.py:L264-L272, L288-L300 |
| upstream interface | focus_wheel 捕获在中央 `hinge_axle`；diopter 捕获在右 `eyepiece_tube`（element allow_overlap） | P1 / model.py:L328-L341 |
| downstream interface | 无（终端活动件） | — |

### Slot B / module `individual_focus`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `focus_ring_0` / `focus_ring_1`（`for i in range(2)`，knurled + `KnobBore` 中孔） | `rec_binocular_var_individual_focus` / model.py:L271-L280 |
| internal joints | `barrel_to_focus_ring_{i}`（REVOLUTE +X ±60°，父为各自 barrel） | model.py:L281-L295 |
| upstream interface | ring 捕获在各 barrel `eyepiece_tube` / 坐 `eyepiece_ring`（element allow_overlap） | model.py:L324-L340 |
| downstream interface | 无；显式断言无 `focus_wheel`、两环父为 left/right barrel | model.py:L484-L502 |

### Slot B / module `fixed_focus`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（不发射任何调焦 part） | `rec_binocular_var_fixed_focus` / model.py:L187-L246 |
| internal joints | 无（仅 fold×2，属 bridge↔barrel 接口，不归本 module） | — |
| upstream interface | 无 | — |
| downstream interface | 无；显式断言无 focus_wheel/diopter part 与 joint、恰好 3 parts / 2 joints | model.py:L258-L290 |

### Slot C / module `rubber_fold`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`eyecup` 为 barrel 的 visual（软橡胶 lathe，朝 -X） | P1 / model.py:L82-L98, L157-L162 |
| internal joints | 无（眼罩不活动） | — |
| upstream interface | eyecup visual 坐落于 barrel eyepiece 视轴末端（`-0.071, side*EYE_Y`） | P1 / model.py:L157-L162 |
| downstream interface | 无 | — |

### Slot C / module `twist_up`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `eyecup_collar_0` / `eyecup_collar_1`（带 helical 槽刚性 lathe collar） | `rec_binocular_var_twist_eyecup` / model.py:L329-L337 |
| internal joints | `{left,right}_barrel_to_eyecup_collar_{i}`（PRISMATIC axis=(-1,0,0)，0→0.008 m） | model.py:L341-L351 |
| upstream interface | collar bore 捕获 `eyepiece_ring`（element allow_overlap，sliding fit）；目镜增 `eyepiece_body` 支撑 | model.py:L179-L184, L398-L406 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `barrel_prism_layout` | enum | `porro_offset` / `roof_straight` / `reverse_porro_compact` | `porro_offset` | choice | 由 deterministic procedural sampler 选择；决定 Slot A part 树 + OBJ_Y/EYE_Y 偏置 | Slot A 表 |
| `focus_mechanism` | enum | `center_wheel_diopter` / `individual_focus` / `fixed_focus` | `center_wheel_diopter` | choice | sampler 选择；决定中央/目镜端调焦 joint 拓扑 | Slot B 表 |
| `eyecup_style` | enum | `rubber_fold` / `twist_up` | `rubber_fold` | choice | sampler 选择；决定眼罩是否为 PRISMATIC 活动件 | Slot C 表 |
| `palette_style` | enum | `matte_black_armor` / `dark_graphite_metal` / `olive_green_rubber` / `sand_tan_armor` / `two_tone_graphite` / `amber_coated_optics` | `matte_black_armor` | choice | 每 seed 采样 colorway；仅改 material rgba，不改拓扑/尺寸/接口 | P1 mats L193-L200（+ 跨 5★ 配色观察派生） |
| `overall_size_scale` | float | [0.78, 1.12] | 1.0 | independent | 各向同性整体尺度；clamp 到范围。`reverse_porro_compact` 偏小、标准 Porro/roof 偏大（中心偏向 1.0） | P1 envelope L343-L361；reverse L359-L382 |
| `barrel_length_scale` | float | [0.85, 1.15] | 1.0 | independent | 沿视轴 barrel 体长缩放（objective→eyepiece 站位等比）；clamp | roof `BARREL_LENGTH` L42；P1 站位 L120-L168 |
| `objective_radius_scale` | float | [0.85, 1.18] | 1.0 | independent | objective bell 外径缩放；clamp | P1 `OBJ_TUBE_R` L42；roof `OBJ_BELL_R` L41 |
| `ipd_scale`（eye spacing） | float | [0.88, 1.12] | 1.0 | independent | 目镜横向偏置 `EYE_Y` 整体缩放（瞳距）；clamp | P1 `EYE_Y` L41；roof `IPD_HALF` L39 |
| `fold_limit_deg` | float | [18, 30] | 25 | independent | 两 fold REVOLUTE 的 ±limit；clamp | P1 `FOLD_LIMIT` L44 |
| `eyepiece_offset_y` | float | derived | — | equation | `= side * EYE_Y_base * ipd_scale`（Slot A 决定 `EYE_Y_base`；roof 内侧、reverse 外展）；不独立采样 | Slot A `EYE_Y` 常量 |
| `objective_offset_y` | float | derived | — | equation | `= side * OBJ_Y_base`（由 Slot A 决定：porro 外、reverse 内；roof = `EYE_Y` 同轴）；不独立采样 | Slot A `OBJ_Y` 常量 |
| `target_join_origin_y` | float | derived | — | equation | 目镜端子件（diopter/focus_ring/collar）joint origin Y `= eyepiece_offset_y`（随 `ipd_scale` 与 Slot A 派生，保接口一致） | §槽位图接口说明 |
| (—) | constraint | — | — | inequality | **fold 闭合 clearance**：在 `q = -fold_limit / +fold_limit` 全折叠位，左右 prism_housing（或 roof barrel_body）Y 向 gap ≥ 0.001 m。违反时回缩 `objective_radius_scale` 与/或抬高 `ipd_scale` 下限重采。 | P1 fold gap L510-L518；roof L535-L542 |
| (—) | constraint | — | — | inequality | **目镜端轴向 clearance（B=individual_focus × C=twist_up）**：REVOLUTE focus_ring 与 PRISMATIC eyecup_collar 同在目镜视轴，全行程（collar `+0.008`）下两者 X 向不得贯穿——focus_ring 站位 `FOCUS_RING_X` 须比 collar 全伸出端更靠 objective 侧，X 间隙 ≥ 0.002 m。违反时把 focus_ring 前移或缩短 collar travel；无法满足则该组合降级（见 §9 compatibility matrix）。 | IF L287；twist L346-L351 |
| (—) | constraint | — | — | inequality | **着地**：缩放后 `min_z` ∈ [-0.004, 0.006]，物体以 barrel 近 z=0 着地。违反时按 `overall_size_scale` 回缩。 | P1 L362-L366 |

`palette_style` colorway 取值（rgba 仅作示意，下游模板落实；全部源自 5★ 观察的 matte-black armor / dark-gray metal / amber lens / dark ocular 基线及其现实变体）：
- `matte_black_armor`：armor (0.10,0.10,0.105)、metal (0.30,0.31,0.33)、amber lens (0.52,0.16,0.08)、ocular (0.11,0.08,0.07)（= P1 基线）。
- `dark_graphite_metal`：armor 深炭灰 (0.16,0.16,0.18)、metal 亮银灰 (0.45,0.46,0.49)、amber、ocular。
- `olive_green_rubber`：armor 军绿 (0.18,0.22,0.12)、metal、amber、ocular。
- `sand_tan_armor`：armor 沙褐 (0.55,0.47,0.34)、metal 深灰、amber、ocular。
- `two_tone_graphite`：armor 深石墨 (0.12,0.12,0.14) + 棱镜罩区域亮灰嵌条 (0.38,0.39,0.42)、amber、ocular。
- `amber_coated_optics`：armor 黑、metal 灰，objective lens 强琥珀镀膜 (0.62,0.22,0.06)、ocular 蓝绿镀膜微调 (0.08,0.12,0.13)。

## Multiplicity / Copy Logic

- **无模板级复制数量逻辑（无 `*_count`）**：核心结构由固定 named slots 表达。**barrel 恒为 ×2**（双筒 = BI-noculars 的定义），不是可变 N；不暴露任何 `barrel_count` / `*_count` 参数，也不通过模板级循环复制可变数量的 visual/part/joint。
- **module-local 固定循环（非模板轴，固定 2，左右各一）**：
  - 每筒 hinge sleeve/arm 经 `zip(sleeve_xs, sleeve_names, arm_names)`（P1 L173）/ `for i in range(len(sleeve_xs))`（roof L181）循环发射（固定 2 个 lug，不暴露为参数）。
  - `individual_focus` 的 `focus_ring_{i}`（`for i in range(2)`，IF L271）与 `twist_up` 的 `eyecup_collar_{i}`（`enumerate(barrel_objs)`，twist L329）均为**固定 `range(2)` 循环**（左右各一，共享 helper + 统一 joint policy），**不暴露为模板 count 参数**。
- **N_range**：无（barrel count 固定 2）。
- copied object / naming / placement / joint policy（供下游实现，不构成可变 multiplicity 轴）：
  - copied object：左右对称 barrel（经 `_add_barrel(model, name, side, ...)`，side=±1 镜像）；以及 `focus_ring_{i}` / `eyecup_collar_{i}`。
  - naming：`left_barrel` / `right_barrel`；循环子件 `focus_ring_{i}` / `eyecup_collar_{i}`（i∈0..1）。
  - placement：沿 ±Y 镜像偏置（`side*offset`），视轴沿 +X。
  - joint policy：fold = 2× REVOLUTE 绕中央 +X hinge 轴（对向折叠 ±fold_limit）；focus ring = REVOLUTE 绕各自视轴；eyecup collar = PRISMATIC 沿视轴。

## 拓扑多样性审计

总组合数：A × B × C = 3 × 3 × 2 = **18**（无 multiplicity 轴；barrel 恒为 2 不计入组合）。


理由：18 个 slot 组合，每个都改变 part 树或 joint 拓扑——Slot B 跨 **CONTINUOUS+REVOLUTE（center_wheel_diopter）/ 2×REVOLUTE（individual_focus）/ 无调焦件（fixed_focus）** 三种 joint 拓扑，Slot C 含 **PRISMATIC（twist_up）vs 无 joint（rubber_fold）**，Slot A 改 part 树（roof_straight 无 prism_housing）与光学轴排布。即便 `palette_style` 与连续 scale 不计入 topology 等价类，单 slot 组合即达 18 distinct，远超 10 门槛。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 `ctx.rng`（或 seed 派生 RNG）独立加权采样三个 slot enum（A 3 选 1、B 3 选 1、C 2 选 1，默认近均匀，可对 `porro_offset` / `center_wheel_diopter` / `rubber_fold` 经典基线略加权），再采样 `palette_style` 与所有 `independent` 连续 scale，按 `equation` 派生 `eyepiece_offset_y` 等，最后用 §7 三条 `inequality`（fold 闭合 clearance、目镜端轴向 clearance、着地）投影/回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定的 `[(barrel_prism_layout, …), (focus_mechanism, …), (eyecup_style, …)]`（连续 scale 不进 slot_choices，除非改变拓扑等价类——本模板不会）。compatibility matrix 见下表，gating 在 `resolve_config` 解析（不留到 builder 失败）。`seed=0` 不特殊。无需 regression overrides（5 格全部一次收敛，5★ 源齐全）；若 sweep 暴露特定坏组合再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别约束封顶在 18（slot 组合上限）。本类别 slot 池小（双筒结构词汇表本身有限：A 3 + B 3 + C 2），18 <300 是**类别固有约束**而非建模缺陷——多样性由 18 个拓扑组合 × `palette_style`（6 colorway）× 连续 scale 谱共同提供视觉/比例多样性，topology 等价类不可能超过 slot 组合上限。这与源 map 组合数预审一致。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization（初版模板应含的关键连续 scale）：`overall_size_scale [0.78,1.12] independent`、`barrel_length_scale [0.85,1.15] independent`、`objective_radius_scale [0.85,1.18] independent`、`ipd_scale [0.88,1.12] independent`、`fold_limit_deg [18,30] independent`；派生 `eyepiece_offset_y = side*EYE_Y_base*ipd_scale`、`objective_offset_y`（Slot A 决定）、`target_join_origin_y = eyepiece_offset_y`（equation）。遵循连续尺寸采样契约：先采 independent → 派生 equation → 用三条 inequality（fold clearance / 目镜端 clearance / 着地）投影回缩。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（barrel 帧坐落 hinge 轴、目镜端子件 origin 随 EYE_Y 派生）、MatingContract（hinge sleeve 捕获 axle、目镜端子件捕获 eyepiece tube/ring）或 multiplicity（barrel 恒 2）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C，独立加权 enum 采样 + palette + 连续 scale；compatibility gate 在 resolve_config | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | A×B×C 全 18 组合**默认全合法**（双筒身份不冲突）。唯一需 clearance gate 的组合：**B=individual_focus × C=twist_up**（目镜端 REVOLUTE focus ring 与 PRISMATIC eyecup collar 同轴，需 §7 第 2 条 inequality 保轴向间隙；若几何不可行则该组合采样时 fallback 到 `rubber_fold`）。其余组合无互斥。 | 无 floating / 无穿模 / fold 闭合不自碰 / 目镜端轴向不贯穿 / 着地 / 双筒恰 2 筒 |
| controlled local variation | 5 个 independent scale + 派生 EYE_Y/OBJ_Y/joint origin；全部 clamp + 三条 inequality 回缩 | 比例随机但 IPD/objective 在轴心、hinge 捕获、目镜端 origin、着地、双筒身份不破 |
| regression overrides | none（5 格全部一次收敛，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（fold/目镜端 clearance + 着地） |、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A barrel_prism_layout | 3 | yes | yes | porro / roof / reverse |
| B focus_mechanism | 3 | yes | yes | wheel+diopter / IF / fixed |
| C eyecup_style | 2 | yes | no | 降到 2 已说明理由（眼罩二族） |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{porro_offset, roof_straight, reverse_porro_compact}、B∈{center_wheel_diopter, individual_focus, fixed_focus}、C∈{rubber_fold, twist_up}）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：B=individual_focus × C=twist_up 通过 clearance gate 或 fallback 到 rubber_fold。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（overall_size/barrel_length/objective_radius/ipd/fold_limit）在 `resolve_config` clamp/派生；三条 inequality（fold 闭合 clearance、目镜端轴向 clearance、着地）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：barrel hinge sleeve 捕获中央 `hinge_axle`（element allow_overlap，X 向 overlap ≥0.010）；focus_wheel 捕获 axle（B=center）；目镜端子件（diopter/focus_ring/collar）捕获 `eyepiece_tube`/`eyepiece_ring`/`barrel_body`。
- 关键 joint type/axis/range：fold×2 = REVOLUTE +X ±fold_limit；focus_wheel = CONTINUOUS +X（B=center）；diopter / focus_ring = REVOLUTE +X ±60°；eyecup_collar = PRISMATIC -X 0→0.008（C=twist_up）。
- copied object 命名/placement：`left_barrel`/`right_barrel`（side=±1 镜像）、`focus_ring_{i}`/`eyecup_collar_{i}`（i∈0..1）；目镜端子件 origin Y 随 Slot A 的 EYE_Y 与 ipd_scale 派生。
- 双筒身份不变量：恰好 2 支镜像 barrel；objective 在前（+X）、eyecup 在后（-X）；两端 lens 凹陷；fold 时 IPD 收窄 + eyecup 下沉。
- B=fixed_focus：断言无 focus_wheel/diopter part 与 joint；B=individual_focus：断言无 center focus_wheel、两 focus_ring 父分别为 left/right barrel。

## Reject cases

- 只有 1 支 barrel（或 3 支以上）——违反双筒身份（必须恰好 2 支镜像光学筒）。
- 无中央 hinge bridge 或缺 fold REVOLUTE joint（barrel 与 bridge 之间无 ±X 折叠铰链）——读成 fixed 双筒砖块，丢失 interpupillary 语义。
- objective 与 eyecup 朝向同一方向，或 eyecup 在前 objective 在后（视轴 +X/-X 颠倒）。
- 目镜端子件 joint origin Y 未随 Slot A 的 `EYE_Y` 派生 → diopter/focus_ring/collar 悬空于错误视轴或漂浮在筒外。
- B=individual_focus × C=twist_up 未做轴向 clearance → REVOLUTE focus ring 与 PRISMATIC collar 在全行程贯穿（穿模）。
- fold 全折叠位左右 prism_housing/barrel_body Y 向 gap < 0 → 闭合姿态自碰撞（缩放过大或 ipd_scale 过小未回缩）。
- hinge sleeve 未捕获在中央 `hinge_axle`（缺 element-scoped allow_overlap）→ 误判穿模 reject，或 barrel 悬空脱离 bridge。
- 把 tripod / equatorial-altaz 指向 mount、单 OTA、或 camera barrel 混进来当 barrel（错类别）。

## 与相邻类别的边界

- 不该混入：`astronomical_telescope_on_tripod`（单 OTA + tripod + equatorial/altaz/pan-tilt 指向链；双筒无 tripod、无 az/alt 指向 DOF、是两支光学轴 + 中央 fold，运动语义完全不同）。
- 不该混入：`camera_lens` / `camcorder`（消费摄影光学：单光轴变焦/对焦镜组，无双筒铰链桥、无 interpupillary fold、无双镜像筒；调焦环虽形似 diopter ring 但缺双筒拓扑）。
- 不该混入：monocular / spotting scope（单筒观测光学：仅 1 支光学筒，缺第二支镜像筒与中央铰链桥，无 IPD fold——丢失双筒定义身份）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`hinge_bridge` 根、`_add_barrel(side=±1)` 镜像发射、`ROT_Z_TO_PX/NX` 视轴映射、captured-pin `allow_overlap` 契约在全 6 源一致，可抽公共 helper（保留 `# adopted: <source>` 注释）。Slot A 三模块各有自己的 barrel mesh helper（`_objective_tube_mesh`+`_housing_mesh` for porro/reverse；`_barrel_body_mesh` for roof），按 `barrel_prism_layout` 分派。
- captured-pin overlap 须 element-scoped `allow_overlap`：hinge sleeve↔hinge_axle（全模块）、focus_wheel↔hinge_axle（B=center）、diopter/focus_ring/collar↔eyepiece_tube/eyepiece_ring/barrel_body（按 Slot A/B/C）。参考各源 run_tests 的 `allow_overlap` 块。
- 目镜端 joint origin 的 Y 必须从 resolved `EYE_Y`（Slot A base × ipd_scale）取值，不可硬编码——Slot A 切换（porro 内侧 0.032 / reverse 外展 0.038 / roof 同轴 0.032）会改变捕获面位置。
- B=individual_focus × C=twist_up 组合：在 `resolve_config` 校验目镜端轴向 clearance（focus_ring 站位 vs collar 全伸出端），不可行则该 seed 的 C fallback 到 `rubber_fold`（compatibility matrix fallback 路径）。
- roof_straight 的 diopter/collar 捕获面是 `barrel_body`（无独立 `eyepiece_tube`），与 porro/reverse 的 `eyepiece_tube` 不同名——module 须按 Slot A 选择正确的捕获 element 名。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C | `porro_offset` / `center_wheel_diopter` / `rubber_fold` | `rec_model-a-pair-of-classic-porro-prism-binoculars-2_20260610_085123_938411_a1874ba2` | `L63-L79, L82-L98, L101-L105, L108-L187`（A）；`L250-L300`（B）；`L82-L98, L157-L162`（C）；root `L204-L222`；fold joints `L228-L248` | 三 slot 基线：barrel helper + 中央轮/diopter + 软橡胶眼罩 + hinge bridge 根 + fold 关节 |
| S2 | A | `roof_straight` | `rec_binocular_var_roof_prism` | `L63-L91, L113-L196, L36-L60, L218-L240` | 直筒 roof-prism barrel（无 prism_housing），缩短 axle |
| S3 | A | `reverse_porro_compact` | `rec_binocular_var_reverse_porro` | `L69-L85, L107-L119, L122-L208, L43-L53` | reverse-Porro barrel（objective 内移/eyepiece 外展），紧凑 envelope |
| S4 | B | `individual_focus` | `rec_binocular_var_individual_focus` | `L108-L121, L266-L295, L484-L502` | 左右独立 REVOLUTE focus ring，删中央轮/diopter |
| S5 | B | `fixed_focus` | `rec_binocular_var_fixed_focus` | `L187-L246, L258-L290` | 定焦：无调焦 part/joint，仅 fold×2 |
| S6 | C | `twist_up` | `rec_binocular_var_twist_eyecup` | `L91-L120, L328-L351, L555-L645` | PRISMATIC 旋升 eyecup collar + eyepiece_body 支撑 |
