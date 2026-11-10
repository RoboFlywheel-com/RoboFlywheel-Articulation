# container_primer_bottle (cosmetic primer bottle — slim body + applicator closure) — Modular Spec

> 来源小类：`picture/Container/Primer bottle`（articraft_data 上游 single-parent 小类：black airless cosmetic primer pump bottle + 9 个 qwen fork 变体）。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template/data/records/<id>/revisions/rev_000001/model.py`，以 part / joint / helper **名字** 为准（`_body_solid` / `_rounded_prism` / `_cylinder` / `_elliptical_prism` / `_pump_solid` / `pump_press` / `lever_swing` / `body_to_cap` / `dropper_lift` / `spray_press` / `cap_hinge` 等），行号仅作定位。
> **5 星样本充足**：1 parent + 9 fork 变体 = 10 个 record，全部读完 model.py（≥5，不触发 STOP）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_primer_bottle` |
| template path | `agent/templates/Container_Primer_bottle.py` |
| test path (optional) | `tests/agent/test_container_primer_bottle_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots：body_form + closure_mechanism；closure part 挂到共同 root `body`；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 parent + 9 fork 变体；single-parent 小类，全部 converged 5★）|
| read_count | 10（全部 model.py 全文读完）|
| read_scope | all 5-star samples in this category（parent + 全部 `rec_container_primer_bottle_var_*`）|
| source_index_policy | only adopted module sources are indexed below（§14）|

读取的 10 个 record：
- parent `rec_black-airless-cosmetic-primer-pump-bottle-with-a_..._ec0caf66`（cushion squircle body + airless 顶压泵）
- `rec_container_primer_bottle_var_square_body`（方棱 body，复用 airless 泵）
- `rec_container_primer_bottle_var_round_body`（圆柱 body，复用 airless 泵）
- `rec_container_primer_bottle_var_oval_body`（椭圆截面 body，复用 airless 泵）
- `rec_container_primer_bottle_var_lever_pump`（cushion body + 侧杆泵 REVOLUTE）
- `rec_container_primer_bottle_var_twist_cap`（cushion body + 旋盖 REVOLUTE +Z）
- `rec_container_primer_bottle_var_dropper_cap`（cushion body + 滴管 PRISMATIC +Z 抽出）
- `rec_container_primer_bottle_var_spray_atomizer`（cushion body + 雾化喷头 + 侧出 nozzle，PRISMATIC +Z）
- `rec_container_primer_bottle_var_flip_top`（cushion body + 翻盖 REVOLUTE +X）
- `rec_container_primer_bottle_var_treatment_spout`（cushion body + 长弯颈乳液泵 PRISMATIC +Z）

冗余/分流说明：
- 4 个 body 变体（cushion/square/round/oval）只换横截面族，都复用 parent 的 airless 顶压泵机构——归并为 Slot A `body_form` 候选，泵机构不重复列。
- 6 个 closure 变体（lever/twist/dropper/spray/flip/treatment）都复用 parent 的 cushion body——归并为 Slot B `closure_mechanism` 候选，body 不重复列。
- 真实命名修正（源 map 名 → 代码实名）：`twist_cap`/`cap_unscrew` 的实际 part/joint 是 `screw_cap`/`body_to_cap`（REVOLUTE z）；`pump_lever`/`lever_pivot` 实为 `lever`/`lever_swing`（REVOLUTE，axis=(-1,0,0)）；`atomizer_cap`/`nozzle_spout` 实为 part `spray_head` + 单 visual `atomizer_head`（侧 nozzle 内联其中），joint `spray_press`；`flip_lid`/`flip_hinge` 实为 `flip_cap`/`cap_hinge`（REVOLUTE +X）。下表按实名。

## 核心身份

小号**化妆品打底/妆前乳（primer）瓶**：一只直立、**细长**（slim：footprint 任一边 < 0.045 m，body 高 > 0.07 m，高度显著大于横截面）的中空小瓶，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。`body`（root）由 CadQuery `extrude`/`loft`/`revolve` 发射为一只 fused 实心 shell：主体 + 收肩 shoulder（loft）+ 短颈 collar（`neck`，泵/盖坐其上）。body 上内联两条固定装饰 visual：`gold_band`（半身高金色环带 visual，z≈0.050）+ `label_plate`（前 +Y 面凸起标牌 visual，代表 "PRIMER" 印字块）——均为 parent visual，无独立 joint。

瓶口上方一只**涂抹/分配机构**按某种动作开合或分配（**主活动语义**）：
- airless 顶压泵（`pump_press` PRISMATIC −Z，下压 ~6mm 回弹，flat puck actuator + 顶部 orifice）
- 侧杆治疗泵（`lever_swing` REVOLUTE +X，curved 杆臂绕 neck-top fork pivot 下摆 ~60°，tip 出料 nozzle）
- 旋盖（`body_to_cap` REVOLUTE +Z，threaded cylindrical 盖绕 +Z 旋开，外周 16 条 `grip_rib_i`）
- 滴管（`dropper_lift` PRISMATIC +Z，screw collar + rubber `squeeze_bulb` + glass `glass_pipette` 整组直抽出 ~45mm）
- 雾化喷头（`spray_press` PRISMATIC −Z，finger-pad head + **侧伸 nozzle 喷口** 向 +Y 出，下压回弹）
- 翻盖（`cap_hinge` REVOLUTE +X，圆 flip disc 绕 cap 后缘水平轴上翻 ~103°，露 orifice；cap base 为 body-inline 固定 visual）
- 长弯颈乳液泵（`pump_press` PRISMATIC −Z，collar + stem + 长 gooseneck spout 弯出向下 nozzle tip，下压回弹）

颜色 / 材质 / 纯尺寸（更高/更矮/更宽/更扁）**不作为结构轴**——颜色折入 `palette_style` palette 参数（§7），尺寸折入连续 scale。默认成熟域：单瓶单 closure（无嵌套 / 无 multiplicity）。

不该混入（详见 §11）：精华液瓶 `container_bottle_serum`、按压泵分装瓶 `container_dispenser`、玻璃瓶 `container_glass_bottle`。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 root `body` 的 mesh 属性（一次 `_body_solid(body_form)` 发射 shell + shoulder + neck collar + 内联 gold_band/label_plate visual），不是独立串联 slot。`closure_mechanism` 各候选挂到 `body`（parallel children），其中 flip / lever 另有 **body-inline 固定 visual**（cap_base / pump_housing+fork_post）。两轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_form（瓶身横截面 / 足迹族——root `body` 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cushion_squircle（基线）| rec_..._ec0caf66（parent）| `_body_solid` L69-87 + `_rounded_prism(BODY_FILLET=0.008)` L54-66 | eligible if compatible | 重圆角 squircle 横截面（cushion）：filleted-rect extrude（`edges("|Z").fillet`）+ rect loft 收肩 + rect neck collar；圆润竖边 |
| square_prism | rec_..._var_square_body | `_body_solid` L70-91 + `_rounded_prism(BODY_FILLET=0.0008)` L55-67 | eligible if compatible | 近 sharp 角矩形棱柱（fillet→0.0008）：crisp 竖边，shoulder base 近满 footprint；run_tests 断言 dx/dy 接近 nominal rect（区分 cushion）|
| round_cylinder | rec_..._var_round_body | `_body_solid` L58-76 + `_cylinder` L48-55 | eligible if compatible | 真圆柱 body：`circle().extrude()` + 圆锥 shoulder loft（circle→circle）+ 圆 neck；run_tests 断言 X≈Y 圆 footprint |
| oval_section | rec_..._var_oval_body | `_body_solid` L78-102 + `_elliptical_prism` L54-61 | eligible if compatible | 扁椭圆截面：`ellipse(rx,ry).extrude()`（rx>ry，宽 X 浅 Y）+ ellipse loft shoulder + ellipse neck + 底 rim 唇；run_tests 断言 X>Y（区分圆/squircle）|

硬约束记录：body_form 4 candidate（达 3-6 目标）。全部为 fused 实心 shell（extrude 主体 + loft shoulder + neck collar），共享 `gold_band`/`label_plate` 固定 visual 内联模式，只换横截面 primitive（filleted-rect / near-sharp rect / circle / ellipse）+ 收肩 loft 截面族。pump bore（closure 侧）需按 body_form 派生（rect/circle/ellipse bore，见 §9 compat）。

### Slot B：closure_mechanism（**主开合/分配机构槽**——瓶口涂抹件动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| airless_press_pump（基线）| rec_..._ec0caf66（parent）| part `pump_top` + `_pump_solid` L115-143 + `pump_press` PRISMATIC L189-201 | eligible if compatible | flat airless actuator（rounded-rect puck + 顶 orifice + hollow skirt bore 罩 neck）；`pump_press` PRISMATIC axis +Z，lower=−PUMP_TRAVEL(0.006) upper=0，下压回弹；1 part 1 joint |
| side_lever_pump | rec_..._var_lever_pump | part `lever` + `_lever_solid` L154-190 + `lever_swing` REVOLUTE L256-269；body-inline `_pump_housing_solid` L133-140 + `_fork_post_solid` L143-151 | eligible if compatible | curved 杆臂（hub + 上翘 arm loft + tip nozzle）绕 neck-top fork pivot 下摆；`lever_swing` REVOLUTE **axis=(−1,0,0)**（正 q 摆 +Y 臂向 −Z），lower=0 upper≈1.05；body 内联固定 visual `pump_housing` + `fork_post_0/1`（fork pair） |
| screw_twist_cap | rec_..._var_twist_cap | part `screw_cap` + `_cap_shell_solid` L117-177 + `_grip_rib_solid` L180-200 + `body_to_cap` REVOLUTE L261-271 | eligible if compatible | threaded cylindrical 盖（外圆壳 + 内 rect bore + thread ridge ring + 顶 boss + 16 条 `grip_rib_i` 周向 for-i visual）；`body_to_cap` REVOLUTE axis +Z origin NECK_TOP_Z，lower=0 upper=2π，旋开（无 lift）|
| dropper_cap | rec_..._var_dropper_cap | part `dropper`（`collar_ring` L151-161 + `thread_ridge_i` L90-101 + `squeeze_bulb` LatheGeometry L164-183 + `glass_pipette` L186-214）+ `dropper_lift` PRISMATIC L295-307 | eligible if compatible | 滴管整组：screw collar + 3 thread ridge for-i + rubber bulb（lathe profile）+ slim glass pipette（tube + 锥 tip，下穿 neck 入 body）；`dropper_lift` PRISMATIC axis +Z lower=0 upper=0.045，整组直抽出 |
| spray_atomizer | rec_..._var_spray_atomizer | part `spray_head` + `_spray_head_solid` L118-177（含侧 nozzle）+ `spray_press` PRISMATIC L223-235 | eligible if compatible | fine-mist 喷头：cylinder actuator + 顶 dome finger-pad + hollow skirt bore + **向前 +Y 侧伸 nozzle 喷口**（`translate` 出 head 前面，orifice bore）；`spray_press` PRISMATIC axis +Z lower=−0.006 upper=0；区分点=侧出 nozzle（run_tests 断言 head y_max > body y_max）|
| flip_top_disc | rec_..._var_flip_top | part `flip_cap` + `_flip_disc_solid` L146-181 + `cap_hinge` REVOLUTE L234-245；body-inline `_cap_base_solid` L116-143 | eligible if compatible | 翻盖 disc：圆 flip disc + 前缘 thumb tab + 底 sealing plug，绕 cap 后缘水平轴上翻；`cap_hinge` REVOLUTE **axis=(1,0,0)** origin=(0,−CAP_RADIUS,CAP_TOP_Z)，lower=0 upper≈1.8（~103°）；cap base 为 body-inline 固定 visual `cap_base`（low cylinder shell + 顶 orifice well）|
| treatment_spout_pump | rec_..._var_treatment_spout | part `pump_head` + `_pump_head_solid` L121-201（collar+stem+gooseneck sweep+nozzle）+ `pump_press` PRISMATIC L247-257 | eligible if compatible | 长弯颈乳液泵：actuator collar + 垂直 stem + `func_sweep` spline gooseneck spout 弯出 +X 向下 nozzle tip + orifice；`pump_press` PRISMATIC axis +Z lower=−0.006 upper=0；区分点=独立长弯颈 spout（run_tests 断言 pump X span > 0.028、height > 0.030）|

硬约束记录：closure_mechanism 7 candidate（**达 §5 实务上限**，化妆品 primer 瓶真实闭合机构词汇表边界）。joint 拓扑覆盖：PRISMATIC −Z 顶压（airless / spray / treatment，三者由 actuator 几何 + 侧/弯 spout 区分）/ PRISMATIC +Z 抽出（dropper）/ REVOLUTE +X 横轴（lever 摆臂 / flip 翻盖，两者由 摆臂 vs disc + pivot 位置区分）/ REVOLUTE +Z 立轴（twist 旋盖）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。lever / flip 额外发射 body-inline 固定 visual（fork+housing / cap_base）。

> 区分依据（避免“只是更高的 actuator”被当独立 candidate）：airless（flat puck，顶 orifice）/ spray（侧出 nozzle part 几何）/ treatment（独立长弯颈 sweep spout part）三者**同为 PRISMATIC −Z 顶压但 part 几何拓扑不同**（顶孔 vs 侧管 vs 弯颈），故各列；纯加高的 actuator（无独立喷口几何）不另列，折入 airless 的连续 scale。

## 槽位图（slot graph）

pattern: parallel_children（root `body` 承载 closure；无 multiplicity）

```
body(body_form：cushion_squircle / square_prism / round_cylinder / oval_section)   [ROOT, 坐地 z=0]
   │  visual: body_shell(matte) + gold_band(gold, z≈0.050) + label_plate(gold, 前 +Y)  ← 全固定 parent visual
   │  geometry: 主体 extrude + shoulder loft + neck collar(rect/circle/ellipse 按 body_form)
   │
   ├── closure = airless_press_pump:
   │     body --[pump_press: PRISMATIC +Z @ frame origin, lower=−0.006 upper=0]--> pump_top
   │
   ├── closure = side_lever_pump:
   │     body(+inline pump_housing + fork_post_0/1 固定 visual @ neck top)
   │     body --[lever_swing: REVOLUTE axis=(−1,0,0) @ (0,0,PIVOT_Z) fork pivot, lower=0 upper≈1.05]--> lever
   │
   ├── closure = screw_twist_cap:
   │     body --[body_to_cap: REVOLUTE +Z @ (0,0,NECK_TOP_Z), lower=0 upper=2π]--> screw_cap(+grip_rib_0..15)
   │
   ├── closure = dropper_cap:
   │     body --[dropper_lift: PRISMATIC +Z @ frame origin, lower=0 upper=0.045]--> dropper(collar+bulb+pipette+thread_ridge_i)
   │
   ├── closure = spray_atomizer:
   │     body --[spray_press: PRISMATIC +Z @ frame origin, lower=−0.006 upper=0]--> spray_head(atomizer_head + 侧 nozzle)
   │
   ├── closure = flip_top_disc:
   │     body(+inline cap_base 固定 visual @ neck top)
   │     body --[cap_hinge: REVOLUTE axis=(1,0,0) @ (0,−CAP_RADIUS,CAP_TOP_Z) 后缘, lower=0 upper≈1.8]--> flip_cap
   │
   └── closure = treatment_spout_pump:
         body --[pump_press: PRISMATIC +Z @ frame origin, lower=−0.006 upper=0]--> pump_head(collar+stem+gooseneck+nozzle)
```

接口点位与 joint 语义：
- **顶压接口（airless / spray / treatment）**：closure geometry 在绝对 body-frame 坐标系发射（actuator 已坐在 neck 上方），故 `pump_press`/`spray_press` origin 落在 frame origin `(0,0,0)`，axis +Z PRISMATIC，**lower=−TRAVEL(0.006) upper=0**（rest q=0 坐下、负 q 下压回弹）。actuator hollow skirt bore（rect/circle/ellipse 按 body_form neck 派生）罩 over neck collar 是 captured / 友配（故意小重叠）。
- **抽出接口（dropper）**：`dropper_lift` origin frame origin，axis +Z PRISMATIC，**lower=0 upper=0.045**（rest q=0 插入、正 q 整组直抽出，pipette 离 neck）。pipette 下穿 neck 入 body 为 captured allow_overlap。
- **立轴旋盖接口（twist）**：`body_to_cap` origin neck rim top `(0,0,NECK_TOP_Z)`，axis +Z REVOLUTE，lower=0 upper=2π（旋开无 lift；cap 保持坐 over neck）。
- **横轴接口（lever / flip）**：`lever_swing` origin 在 neck-top fork pivot `(0,0,PIVOT_Z)`，axis **(−1,0,0)**（正 q 摆臂 +Y 向 −Z 下摆 ~60°）；`cap_hinge` origin 在 cap 后缘 `(0,−CAP_RADIUS,CAP_TOP_Z)`，axis **(1,0,0)**（正 q disc 上翻 ~103°）。两者 origin 落在真实硬件（fork post / cap 后缘）。
- **mating policy**：closure skirt / collar / cap 罩 over neck rim 是 captured / 友配（壁与 neck 几何故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 neck rim / fork pivot / cap 后缘）+ element-scoped `allow_overlap`（closure↔body_shell 的 skirt↔shell；lever hub↔fork_post；dropper pipette↔body_shell；flip plug↔cap_base）守 overlap。
- **rest pose**：所有 closure q=0 闭合 / 坐下（airless/spray/treatment 坐下、dropper 插入、twist 旋紧、flip disc 盖合、lever 臂在 +Y rest）。下压 / 抽出 / 旋开 / 翻起 / 下摆为 viewer 目检的活动语义。
- **互斥 / 可选**：closure 各候选互斥（一次只一种机构）。body-inline 固定 visual（pump_housing+fork_post / cap_base）仅在对应 closure（lever / flip）发射。

## 每槽位 Module Emits / Interfaces

### Slot A / body（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual：`body_shell` matte shell + `gold_band` gold 环带 + `label_plate` gold 前牌）| parent `_body_solid` L69-87 / `_gold_band_solid` L90-99 / `_label_plate_solid` L102-112 |
| internal joints | 无（root 瓶体本身无活动件；neck collar fused 入 shell）| — |
| upstream interface | 坐地 z=0（root）；inertial Box/Cylinder @ body 中心 | parent L170-174 |
| downstream interface | neck collar top 中心 `(0,0,NECK_TOP_Z)`（closure joint 的 parent 接口）+ neck bore 截面（rect/circle/ellipse 按 body_form，供 closure skirt 派生）| parent NECK 常量 L38-41 / round L36-37 / oval L38-40 |

### Slot B / closure_mechanism（每候选发射对应活动件 + 可选 body-inline 固定 visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_top` / `lever`(+body-inline `pump_housing`,`fork_post_i`) / `screw_cap`(+`grip_rib_i`) / `dropper`(`collar_ring`+`squeeze_bulb`+`glass_pipette`+`thread_ridge_i`) / `spray_head`(`atomizer_head`+侧nozzle) / `flip_cap`(+body-inline `cap_base`) / `pump_head`(gooseneck) | 各 closure 源（§4 表）|
| internal joints | `pump_press` PRISMATIC +Z(−travel) / `lever_swing` REVOLUTE (−1,0,0) / `body_to_cap` REVOLUTE +Z / `dropper_lift` PRISMATIC +Z(+lift) / `spray_press` PRISMATIC +Z(−travel) / `cap_hinge` REVOLUTE (1,0,0) / `pump_press` PRISMATIC +Z(−travel) | parent L189-201 / lever L256-269 / twist L261-271 / dropper L295-307 / spray L223-235 / flip L234-245 / treatment L247-257 |
| upstream interface | parent=`body`；joint origin frame origin（顶压/抽出）或 neck rim / fork pivot / cap 后缘（旋/摆/翻）| 各源 origin |
| downstream interface | closure 末端 orifice / nozzle / pipette tip（dispense 出口，纯几何无下游 joint）| 各源 |

### body-inline 固定 visual（≠独立 part）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：lever 的 `pump_housing`+`fork_post_0/1`、flip 的 `cap_base` 均为 `body` 的固定 visual（无 joint）| lever `_pump_housing_solid` L133-140 / `_fork_post_solid` L143-151；flip `_cap_base_solid` L116-143 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | cushion_squircle / square_prism / round_cylinder / oval_section | cushion_squircle | choice | deterministic procedural sampler 选 | module table |
| closure_mechanism | enum | airless_press_pump / side_lever_pump / screw_twist_cap / dropper_cap / spray_atomizer / flip_top_disc / treatment_spout_pump | airless_press_pump | choice | sampler 选 | module table |
| palette_style | enum | matte_black_gold / frosted_glass_gold / clear_gloss_glass_silver / soft_touch_taupe / brushed_metallic_champagne / pearlescent_blush_rosegold / opaque_white_gold / amber_apothecary / two_tone_sage_gold | matte_black_gold | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice` 采（≥3，本表 **9 个 colorway × 显式 material-finish 维度**，源自 5★ matte_black+gold_accent 基线 + glass_pale/collar_gold 实测 + 化妆品 primer 真实配色族）| palette（见下）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 BODY_H → NECK_TOP_Z → closure mount 高度，clamp | resolve clamp |
| body_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 BODY_W / BODY_RADIUS / BODY_RX（横向半宽/半径），clamp（保 slim：footprint < 0.045）| resolve clamp |
| neck_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK = base · neck_scale`；closure skirt/collar bore 半径派生跟随（保罩配合）| resolve clamp |
| closure_size_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 closure actuator/cap/dropper 高度 / skirt 深，clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 PUMP_TRAVEL / DROPPER_LIFT / hinge·lever limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | slim 约束：`body_W·width_scale < 0.045` 且 `body_H·height_scale > body_W·width_scale + 0.030`，违反按比例回缩 width/height | run_tests slim 断言 |
| (—) | constraint | — | — | inequality | 罩配合：`closure_skirt_bore_R ≥ NECK_R + clearance` 且 `closure_outer ≤ body footprint + proud`，违反回缩 closure_size/neck scale | 接口 / clearance |

palette_style **9 个 coordinated colorway × 显式 material-finish 维度**（rgba 取自 5★ 实测 + primer 真实配色族；material name 复用 `matte_black`/`gold_accent`/`pump_black` 等槽位，仅换 rgba + finish hint；玻璃/雾面带 alpha，金属不 neon）。每 colorway = **body + closure/pump/cap + collar/gold-band/label accent + finish**。`finish` 维度是一条显式 material-finish 注记（matte / frosted-translucent / clear-gloss-translucent / soft-touch / metallic / pearlescent / opaque / amber-translucent / two-tone），由 builder 折成 rgba（含 alpha）+（可选）材质 name 后缀，**不新增几何**。

| colorway | finish（material-finish 维度）| body rgba | closure/pump/cap rgba | collar / gold-band / label accent rgba | 锚 |
|---|---|---|---|---|---|
| `matte_black_gold`（基线）| matte（哑光不透明）| matte_black (0.08,0.08,0.09,1.0) | pump_black (0.05,0.05,0.06,1.0) | gold_accent (0.80,0.62,0.22,1.0) | 全部 10 个 5★ 实测（parent + 全 fork）|
| `frosted_glass_gold` | frosted-translucent（磨砂半透，带 alpha）| 雾白磨砂 (0.92,0.91,0.88,0.78) | 暖金 cap (0.78,0.60,0.24,1.0) | gold_accent (0.80,0.62,0.22,1.0) | 5★ glass_pale (0.88,0.88,0.85) 推浅 + alpha |
| `clear_gloss_glass_silver` | clear-gloss-translucent（透亮高光，带 alpha）| 透亮玻璃 (0.85,0.88,0.90,0.55) | silver closure (0.78,0.80,0.82,1.0) | silver band (0.75,0.76,0.78,1.0) | clear glass + silver（玻璃 alpha<1）|
| `soft_touch_taupe` | soft-touch（橡胶哑光不透明）| 灰褐 soft-touch (0.55,0.50,0.46,1.0) | charcoal closure (0.10,0.10,0.12,1.0) | gold_accent (0.80,0.62,0.22,1.0) | 5★ cap_charcoal (0.10,0.10,0.12) closure 锚 |
| `brushed_metallic_champagne` | metallic（拉丝金属，不 neon）| 香槟拉丝金属 (0.72,0.66,0.52,1.0) | 深香槟 closure (0.58,0.52,0.40,1.0) | bright gold band (0.84,0.66,0.26,1.0) | gold_accent 同族提亮（金属非 neon）|
| `pearlescent_blush_rosegold` | pearlescent（珠光不透明）| 珠光裸粉 (0.95,0.82,0.80,1.0) | rosegold closure (0.78,0.55,0.45,1.0) | rosegold band (0.80,0.58,0.48,1.0) | 玫瑰金族（珠光 highlight）|
| `opaque_white_gold` | opaque（纯不透明白）| 不透明纯白 (0.95,0.95,0.93,1.0) | 暖金 cap (0.80,0.62,0.22,1.0) | gold_accent (0.80,0.62,0.22,1.0) | 不透明白 + 金（区别于 frosted 半透）|
| `amber_apothecary` | amber-translucent（琥珀半透，带 alpha）| 琥珀棕半透 (0.45,0.30,0.18,0.72) | 暗铜 dropper/closure (0.30,0.22,0.14,1.0) | brushed gold band (0.78,0.60,0.24,1.0) | 琥珀药瓶族（amber alpha<1）|
| `two_tone_sage_gold` | two-tone（双色不透明：哑光 body + 亮金 accent）| 鼠尾草绿 matte (0.62,0.68,0.58,1.0) | dark green closure (0.30,0.36,0.30,1.0) | bright gold band + label (0.84,0.66,0.26,1.0) | sage matte body / 亮金双色对比 |

> finish 维度落地：`frosted` / `clear-gloss` / `amber-translucent` 三档 body rgba **alpha<1**（半透），其余不透明 alpha=1.0；`metallic`（champagne）/`pearlescent`（blush）/`soft-touch`（taupe）/`two-tone`（sage）/`opaque`（white）均 alpha=1.0，靠 rgba 色相 + finish 注记区分质感（金属不取 neon 高饱和值）。每 colorway 三组件（body / closure / accent）协调成套。

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_scale` 为 equation（closure skirt/collar bore 半径跟随 neck，保罩配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / closure_mechanism 拓扑。palette_style 只换 rgba（+ finish 注记 → alpha / 材质质感），不改几何、不计 slot_choice。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + closure_mechanism）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单瓶单 closure。
- 注：twist 的 `grip_rib_i`(16)、dropper 的 `thread_ridge_i`(3)、lever 的 `fork_post_i`(2) 是 **module-local 固定装饰复制**（同一 part 上的 for-i visual，count 在各 closure module 内固定，非模板级 multiplicity 轴），不进 `slot_choices`，不暴露为 `*_count` 采样参数。

## 拓扑多样性审计

总组合数：body_form(4) × closure_mechanism(7) = **28**。

理由：body_form(4) × closure_mechanism(7) = 28 distinct ≫ 10。closure_mechanism 引入 5 种 joint 拓扑（PRISMATIC −Z 顶压 ×3 由 part 几何区分 / PRISMATIC +Z 抽出 / REVOLUTE +X 横轴 ×2 由摆臂vs翻盖区分 / REVOLUTE +Z 立轴），且 part count / body-inline 固定 visual 不同（lever +fork+housing、flip +cap_base、dropper 4 子 visual、twist +16 grip rib），是真实结构差异。body_form 在 filleted-rect / near-sharp rect / circle / ellipse 间换主体 primitive + 收肩 loft 截面族 + neck bore 截面，是真实横截面拓扑差异。slot_choices 编入两轴 `(body_form, closure_mechanism)`。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（28 组合近全合法，少量 gating 见下表），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除非法组合 / 派生适配尺寸（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 28（28 组合是该小类真实结构词汇上限：4 横截面族 × 7 闭合机构）。低于 300 的原因：primer bottle 真实结构词汇就是 body × closure 两轴 28 组合，是该类目的合理上限（化妆品 primer 瓶无第 3 结构轴——经核验 neck/collar 形态无真实变体，body 为简单短颈瓶，无 wand/brush applicator），不强行注水；多样性叠加 9 个 palette_style colorway（带显式 material-finish 维度）给视觉变化，但 palette 不计 topology。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_width / neck / closure_size / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_scale` 为 equation（closure skirt/collar bore 半径派生跟随）。slim 不等式 + 罩配合不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（frame origin / neck rim / fork pivot / cap 后缘）、罩 neck 配合、装饰 visual 位置或类别身份（slim 细瓶）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含两轴且与 build 一致 |
| compatibility matrix | (1) closure skirt/collar/cap **bore 截面按 body_form neck 派生**：square/cushion → rect bore，round → circle bore，oval → ellipse bore（避免穿模 / 配合错）。closure module 用 `neck_bore_section(body_form)` helper 选 bore primitive。(2) dropper pipette 下穿 neck 入 body → captured allow_overlap（不视为穿模）。(3) spray 侧 nozzle / treatment gooseneck 侧伸超出 body footprint 是预期（run_tests 断言 > body 前面 / X span），不 gate。(4) 各 closure 互斥；body-inline 固定 visual 仅对应 closure 发射。(5) 无硬 gate-out（28 组合全合法，只在 resolve/helper 派生 bore 截面适配）| 无 floating / collision / closure 穿瓶 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_scale equation 驱动 closure bore | 比例变化不破坏 closure joint origin / 罩配合 / 坐地 slim / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | cushion squircle / near-sharp square / round cylinder / oval ellipse |
| closure_mechanism | 7 | yes | yes | airless(PRIS−Z) / lever(REV X 摆) / twist(REV Z) / dropper(PRIS+Z) / spray(PRIS−Z 侧nozzle) / flip(REV X 翻) / treatment(PRIS−Z 弯颈) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, closure_mechanism) 两轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`）；seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；neck_scale equation 驱动 closure bore；slim + 罩配合不等式在 resolve 内投影 / 回缩（不留到 builder）
- compatibility matrix / gating：28 组合全合法（无硬 gate-out），closure bore 截面按 body_form neck 在 resolve/helper 派生（rect/circle/ellipse）
- 连续 scale clamp 后不破坏 closure joint origin / 罩配合 / 坐地 slim / 类别身份
- palette_style 每 seed `rng.choice` 采，仅换 rgba，不改几何、不计 slot_choice
- 关键 joint：airless/spray/treatment `pump_press`/`spray_press` PRISMATIC +Z (abs(axis[2])>0.99) lower<0 upper=0；dropper `dropper_lift` PRISMATIC +Z lower=0 upper>0；twist `body_to_cap` REVOLUTE +Z (abs(axis[2])>0.99)；lever `lever_swing` REVOLUTE +X (abs(axis[0])>0.99) 摆臂下落；flip `cap_hinge` REVOLUTE +X (abs(axis[0])>0.9) disc 上翻
- body slim：footprint 任一边 < 0.045、height > 0.07 且 > footprint + 0.030（所有 body_form 复用 parent slim 断言）
- captured-fit：element-scoped allow_overlap（closure skirt ↔ body_shell；lever hub ↔ fork_post_i；dropper pipette ↔ body_shell；flip plug ↔ cap_base）
- grandfather：closure 罩 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- spray 侧 nozzle 断言 head y_max > body y_max；treatment gooseneck 断言 pump X span > 0.028 且 height > 0.030（保区分于 airless flat puck）

## Reject cases

- 用 boxy 占位体当圆/椭圆 body → 失横截面身份；round 用 `circle().extrude()`/revolve、oval 用 `ellipse().extrude()`、cushion 用 filleted-rect、square 用 near-sharp(fillet≈0.0008) rect。
- body 做成矮胖（footprint ≥ 0.045 或 height ≤ footprint+0.030）→ 失 primer slim 身份（变 jar / 化妆罐）；slim 不等式 FAIL。
- closure joint origin 放在瓶底 / 任意点而非 frame origin（顶压/抽出）/ neck rim（旋）/ fork pivot（摆）/ cap 后缘（翻）真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- airless/spray/treatment 把 `pump_press` 设成 lower=0 upper>0（上抬）而非 lower=−travel upper=0（下压回弹）→ rest pose / 动作语义错。
- dropper 把 `dropper_lift` 设成 lower<0（下插）→ 应 lower=0 upper>0 抽出；pipette 不穿 neck 入 body → 失滴管语义。
- lever 用 axis=(1,0,0) 或正 q 上摆 → 应 axis=(−1,0,0) 正 q 下摆（出料动作）；flip 用 +Z/PRISMATIC → 应 REVOLUTE +X disc 上翻。
- spray 不发射侧出 nozzle（head y_max ≤ body y_max）/ treatment 不发射独立长弯颈 spout（X span ≤ 0.028）→ 退化成 airless flat puck，失区分（candidate 坍缩）。
- 把颜色 / 材质 / 纯尺寸当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；尺寸是连续 scale）。
- closure skirt bore 截面不按 body_form 派生（如 round body 配 rect bore）→ 罩配合穿模 / 间隙，配合不等式 FAIL。
- 把 grip_rib_i / thread_ridge_i / fork_post_i 复制数暴露为模板级 `*_count` 采样轴 → 它们是 module-local 固定装饰，非 multiplicity 轴。

## 与相邻类别的边界

- 不该混入：**container_bottle_serum 精华液瓶**——理由：serum 瓶身材质是**玻璃 shell（厚壁中空真实 bore，读作可装液玻璃容器）**+ 中段 `label_band` 环带，closure 是**精华液专用小型封口/分配**；primer bottle 身份是**不透明/哑光小瓶（matte_black 基线）+ gold_band + label_plate 印字牌**，closure 词汇是 airless/lever/twist/dropper/spray/flip/treatment 化妆品 primer 机构族。两者 closure 词汇虽部分重叠（dropper），但 primer 的身份锚是 slim matte 瓶 + 金带 + 7 机构闭合谱，serum 锚是玻璃瓶 + label_band。
- 不该混入：**container_dispenser 按压泵分装瓶**——理由：dispenser 是**大号透明瓶 + 内 `liquid_fill`/`dip_tube` + 螺纹颈旋 ribbed `collar`（FIXED）+ 外露 `pump_head`（`pump_press` PRISMATIC ~18mm 长行程 + `spout_swivel` REVOLUTE 水平回转 spout）**，**无瓶盖闭合件**；primer 是 slim 小瓶（行程 ~6mm 短）+ 多种闭合（含 twist 盖 / flip 翻盖 / dropper），有真实盖闭合语义，非单一长行程泵 + 回转 spout。
- 不该混入：**container_glass_bottle 玻璃瓶（饮料/酒/油）**——理由：glass_bottle 核心身份是**半透明玻璃 shell（rgba alpha < 1）+ 高瘦长颈 / 葡萄酒 / steinie / hip_flask 等瓶型 + 软木塞/皇冠盖/螺旋瓶盖**，是饮用/盛装 vessel；primer 是不透明哑光小化妆瓶 + 涂抹/分配机构（泵/滴管/喷头），尺度与材质身份均不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。1 parent + 9 fork 变体 = 10 个 5★ record 全读。2 slots：body_form(4) × closure_mechanism(7) = 28 combos ≫ 10， 可过。closure 覆盖 PRISMATIC−Z×3(airless/spray/treatment by part geom)/PRISMATIC+Z(dropper)/REVOLUTE+X×2(lever 摆/flip 翻)/REVOLUTE+Z(twist)。palette_style 9 个 coordinated colorway × 显式 material-finish 维度（5★ matte_black_gold 基线 + glass_pale/collar_gold/cap_charcoal 实测锚 + 8 个 primer 真实配色族：frosted/clear-gloss/soft-touch/metallic/pearlescent/opaque/amber/two-tone finish），仅换 rgba(+alpha)/finish 注记，不计 slot_choice。无 multiplicity 轴（grip_rib/thread_ridge/fork_post 为 module-local 固定装饰）。源 map 名 → 代码实名已修正（screw_cap/body_to_cap、lever/lever_swing、spray_head、flip_cap/cap_hinge）。待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_body_solid(body_form)` 分派 `_rounded_prism`(cushion/square)/`_cylinder`(round)/`_elliptical_prism`(oval) + shoulder loft + neck collar；`_gold_band_solid`/`_label_plate_solid`（按 body_form 截面跟随）全 body_form 公用。`neck_bore_section(body_form)` helper 供 closure 选 skirt/collar bore primitive（rect/circle/ellipse）。
- closure module 各自 factory：airless/spray/treatment 同 `pump_press` PRISMATIC(lower=−travel,upper=0)，仅 actuator 几何不同（flat puck / 侧 nozzle / 弯颈 sweep）；treatment gooseneck 用 `cadquery.func` 的 `spline`+`sweep`（需 `from cadquery.func import circle, face, spline, sweep`）。
- captured-fit overlap：`run_container_primer_bottle_tests` 里按 closure 分支声明 element-scoped `ctx.allow_overlap`（closure↔body_shell skirt 罩 neck；lever hub↔fork_post_i；dropper glass_pipette↔body_shell 穿 neck；flip flip_disc plug↔cap_base）。
- neck_scale equation：`resolve_config` 派生 `closure_bore_R = NECK_R + clearance`、`closure_outer ≤ body_footprint + proud`，罩配合不等式 + slim 不等式在 resolve 投影 / 回缩。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类、parallel_children + 固定 named slots + body×closure 笛卡尔积 + captured-fit allow_overlap + element-scoped grandfather + 多 closure joint 分支骨架）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig dataclass + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` 报 topology family 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | cushion_squircle + airless_press_pump | rec_..._ec0caf66（parent）| `_body_solid` L69-87 / `_rounded_prism` L54-66 / `_gold_band_solid` L90-99 / `_label_plate_solid` L102-112 / `_pump_solid` L115-143 / `pump_press` L189-201 | cushion body 基线 + airless 顶压泵机构 + 金带/标牌固定 visual |
| S2 | A | square_prism | rec_..._var_square_body | `_body_solid` L70-91（fillet=0.0008 near-sharp）| 近 sharp 角方棱 body |
| S3 | A | round_cylinder | rec_..._var_round_body | `_body_solid` L58-76 / `_cylinder` L48-55 | 真圆柱 body（circle extrude + 圆锥 shoulder）|
| S4 | A | oval_section | rec_..._var_oval_body | `_body_solid` L78-102 / `_elliptical_prism` L54-61 | 扁椭圆截面 body（ellipse extrude，宽X浅Y）|
| S5 | B | side_lever_pump | rec_..._var_lever_pump | `_lever_solid` L154-190 / `lever_swing` REVOLUTE (−1,0,0) L256-269 / `_pump_housing_solid` L133-140 / `_fork_post_solid` L143-151 | 侧杆泵（摆臂 + neck-top fork pivot + body-inline housing/fork）|
| S6 | B | screw_twist_cap | rec_..._var_twist_cap | `_cap_shell_solid` L117-177 / `_grip_rib_solid` L180-200 / `body_to_cap` REVOLUTE +Z L261-271 | 旋盖（threaded cylindrical + 16 grip rib）|
| S7 | B | dropper_cap | rec_..._var_dropper_cap | `_collar_solid` L151-161 / `_bulb_lathe_profile` L164-183 / `_pipette_solid` L186-214 / `_thread_ridge_solid` L90-101 / `dropper_lift` PRISMATIC +Z L295-307 | 滴管（collar+bulb+pipette，整组直抽出）|
| S8 | B | spray_atomizer | rec_..._var_spray_atomizer | `_spray_head_solid` L118-177（含侧 nozzle）/ `spray_press` PRISMATIC L223-235 | 雾化喷头（finger-pad head + 侧出 nozzle 喷口）|
| S9 | B | flip_top_disc | rec_..._var_flip_top | `_cap_base_solid` L116-143 / `_flip_disc_solid` L146-181 / `cap_hinge` REVOLUTE (1,0,0) L234-245 | 翻盖（disc + thumb tab + plug，绕 cap 后缘上翻；body-inline cap_base）|
| S10 | B | treatment_spout_pump | rec_..._var_treatment_spout | `_pump_head_solid` L121-201（collar+stem+gooseneck sweep+nozzle）/ `pump_press` PRISMATIC L247-257 | 长弯颈乳液泵（collar+stem + func_sweep spline gooseneck + 下向 nozzle）|
