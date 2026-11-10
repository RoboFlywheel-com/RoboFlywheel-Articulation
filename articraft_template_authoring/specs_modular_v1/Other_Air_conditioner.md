# air_conditioner (wall-mounted mini-split indoor unit) — Modular Spec

> 来源小类：`picture/Other/Air conditioner`（articraft_data 上游 Other/Air conditioner fork-variant pool）。
> 源 source map：`articraft_data/picture_expansion/template_source_maps/Other__Air_conditioner.md`。
> 1 母资产 + 10 个 converged fork 变体，全部完整读 `model.py`（见 §5 摘要）。引用的 `model.py:Lx-Ly`
> 来自各样本 `arti-template/data/records/<id>/revisions/rev_000001/model.py`，以 part / joint / helper
> **名字** 为准（`housing` / `housing_shell` / `plenum_liner` / `filter_frame` / `filter_mesh` /
> `front_panel` / `panel_plate` / `hinge_knuckle_{idx}` / `front_panel_hinge` / `{label}_louver_vane` /
> `{label}_louver_pivot` / `louver_vane_{i}` / `louver_pivot_{i}` / `deflector` / `deflector_pivot` /
> `vertical_vane_{i}` / `vane_pivot_{i}` / `outlet_door` / `outlet_door_hinge` / `panel_{i}` /
> `panel_{i}_hinge` / `_arc_point` / `_face_point` / `_top_arc_point` / `_housing_shape` /
> `_front_panel_shape` / `_deflector_shape` / `_outlet_door_shape` / `_vertical_vane_blade_shape` 等），
> 行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `air_conditioner` |
| template path | `agent/templates/Other_Air_conditioner.py` |
| test path (optional) | `tests/agent/test_air_conditioner_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots：body_form + airflow_mechanism(主机构) + service_panel；外加 `vane_count` 一根 multiplicity 轴——横向导风叶数 × N，**仅当 airflow_mechanism == three_independent_slim_vanes 时激活**）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 10 converged fork 变体 = 11 |
| read_count | 11（全部读 `model.py` 全文，含 build helpers / part tree / articulation / run_tests）|
| read_scope | all 5-star samples in this category（combinatorial fork pool：parent 全读 + 每变体逐层读其差异层 body_form / airflow / service_panel / vane_count）|
| source_index_policy | only adopted module sources are indexed below（§4 / §14）|

逐样本要点（采纳归属）：
- **P1 parent**（`rec_model-a-wall-mounted-mini-split-air-conditioner-_..._e9cc92a3`）：壁挂分体式室内机基线。root `housing`（`_housing_shape` L91-144：YZ 侧剖面下前 quarter-round `_arc_point` + 前倾面，extrude 全宽；再 boolean cut 出 panel 凹座 / 顶部进风框 / filter pocket / 圆柱 plenum / 三道 louver slot）；`housing_shell` mesh + `plenum_liner` 暗色 Cylinder（L186-191）+ `filter_frame`/`filter_mesh` Box（L194-205）为 housing 固定 visual；`front_panel` REVOLUTE 顶掀检修盖（`front_panel_hinge` axis +X，0..60° L223-236）；3 片 `{label}_louver_vane` 各自 `{label}_louver_pivot` REVOLUTE +X（±45° L258-272，`for label, theta in VANE_SPECS` 循环）。**采纳为 root housing 共享件 + body_form=rounded_bottom_curve 基线 + airflow=three_independent_slim_vanes 基线 + service_panel=top_hinge_lift 基线 + vane_count 基线 N=3**。
- **body_form=boxy_rectangular**（`rec_variant-body-form-boxy-rectangular-..._6caa9319`）：`_housing_shape`（L89-153）改为 YZ 直角箱截面 + 前脸 panel-recess 台阶边（非 boolean，clean profile edge），平下前脸 `VANE_Z_CENTERS=(0.040,0.080,0.120)` 三道横 slot；louver pivot origin 落在平前面 `(0, BODY_D, VANE_Z_CENTERS[i])`（L275-285）。**采纳为 body_form=boxy_rectangular**。
- **body_form=raked_wedge**（`rec_variant-body-form-raked-wedge-..._072b1710`）：`_housing_shape`（L112-193）改为楔形四边形侧剖面（`WEDGE_LO_Y=0.26` 底前 far-forward → `WEDGE_HI_Y=0.10` 顶前 receded），`_face_point(fraction)`（L56-61）+ `FACE_NORMAL_ANGLE`（L53）参数化倾斜面；panel-hinge / louver-pivot origin 全部带 `rpy=(FACE_NORMAL_ANGLE,0,0)` 对齐斜面法向（L280-283 / L319-322）。**采纳为 body_form=raked_wedge**。
- **body_form=full_bullnose_capsule**（`rec_variant-body-form-full-bullnose-capsule-..._4b99b445`）：`_housing_shape`（L110-177）上下前沿同 `BULLNOSE_R=0.09` 双圆角胶囊剖面，`_arc_point`（底弧 L94-97）+ `_top_arc_point`（顶弧 L100-107）双 threePointArc；plenum/liner 半径缩小（PLENUM_R=0.06 / LINER_R=0.055），panel 更矮更低（PANEL_H=0.115 / hinge z=0.210）。**采纳为 body_form=full_bullnose_capsule**。
- **airflow=single_wide_deflector**（`rec_variant-airflow-mechanism-single-wide-deflector-..._4f557258`）：出风口改为一个宽 outlet cut（`OUTLET_THETA_MID` L68，`_housing_shape` L139-149）+ 单片全宽 `deflector` part（`_deflector_shape` L173-191 带 return lip）；`deflector_pivot` REVOLUTE +X（HINGE_THETA≈80°，limits −10°..60° L282-302）。run_tests 断言"无残留 louver joint、deflector_pivot 是唯一 airflow 关节"（L480-490）。**采纳为 airflow=single_wide_deflector**。
- **airflow=vertical_vane_bank**（`rec_variant-airflow-mechanism-vertical-vane-bank-..._148eace8`）：一道宽横 outlet slot（`OUTLET_THETA` L70）内 `N_VERTICAL_VANES=12`（L69）片竖直 deflector，`_vane_center_x(i)` 等距（L96-99），每片 `vertical_vane_{i}` = 薄板 `_vertical_vane_blade_shape`（L102-109）+ 竖 `vane_shaft_{i}` Cylinder；`vane_pivot_{i}` REVOLUTE **+Z 竖轴**（±45° L278-292，`for i in range(N_VERTICAL_VANES)` 循环）。**采纳为 airflow=vertical_vane_bank**（唯一 +Z 竖轴 airflow 候选，与横导风轴正交）。
- **airflow=closing_outlet_door**（`rec_variant-airflow-mechanism-closing-outlet-door-..._97104f78`）：整面 outlet 开口（弧形 `_outlet_opening_cut` L91-121）+ 弧形闭合 `outlet_door` part（`_outlet_door_shape` L194-248 沿弧截面 loft + 顶 grab lip + 端 `door_pivot_pin_{idx}`）；`outlet_door_hinge` REVOLUTE **axis (−1,0,0)** 下沿铰（0..75° L339-353，关停齐平闭合、开时下翻露 plenum）。**采纳为 airflow=closing_outlet_door**。
- **service_panel=two_leaf_clamshell**（`rec_variant-service-panel-two-leaf-clamshell-..._3fe5a919`）：检修盖拆为左右两窄叶 `panel_{i}`（`NUM_LEAVES=2` L62，`LEAF_W`/`LEAF_CX` L64-68，`_front_panel_shape(leaf_w)` L157-175），各自 `panel_{i}_hinge` REVOLUTE +X 独立上掀（`for i in range(NUM_LEAVES)` 循环 L221-250）；run_tests 断言"开 leaf0 时 leaf1 保持闭合"独立性（L404-419）。**采纳为 service_panel=two_leaf_clamshell**。
- **service_panel=bottom_hinge_drop_front**（`rec_variant-service-panel-bottom-hinge-drop-front-..._fd012151`）：检修盖改底沿铰前翻，`_front_panel_shape`（L148-165）改为 plate 沿 **+Z rise**（本地 frame 在底边）；`front_panel_hinge` REVOLUTE **axis (−1,0,0)**（hinge z=`PANEL_HINGE_Z=0.1435` 落在 panel-zone 底 L57 / L224-237，0..60° 前下翻露 filter）。**采纳为 service_panel=bottom_hinge_drop_front**。
- **vane_count N=2**（`rec_variant-vane-count-2-..._62841830`）：`VANE_COUNT=2`（L67），`VANE_THETAS` 由 `_VANE_THETA_MIN=35°..MAX=75°` 均分（L68-73），`for i in range(VANE_COUNT)` 发射 `louver_vane_{i}`/`louver_pivot_{i}`（L242-276），slot cut 同数（L138-146）。**采纳为 vane_count multiplicity 的 range(N) 复制契约（N=2 端）**。
- **vane_count N=5**（`rec_variant-vane-count-5-..._ce97feaa`）：`NUM_VANES=5`（L67），`VANE_THETAS` 由 `VANE_THETA_LO=25°..HI=75°` 均分（L72-75），共享助手 `_add_louver_vane(model, housing, i, theta)`（L178-216）在 `for i in range(NUM_VANES)` 循环发射（L293-294），统一 joint policy 断言（L466-477）。**采纳为 vane_count multiplicity 的 range(N) 复制契约（N=5 端）+ `_add_louver_vane` 共享 factory 蓝本**。

冗余/分流说明：三个 body_form 变体只重写 `_housing_shape` 侧剖面与 louver/panel 落点求解器（不增减 joint），airflow / service_panel / filter / plenum 语义不变；三个 airflow 变体只换出风机构（body / panel / filter 不变）；两个 service_panel 变体只换检修盖机构（body / airflow / filter 不变）。纯尺寸/颜色差异（如各变体的 SLOT_OPEN / PLENUM_R 微调）不另列 candidate，收进 §7 连续 scale。

## 核心身份

壁挂分体式空调**室内机**（wall-mounted mini-split indoor unit）：一具水平细长的光泽白色壳体（~0.90 m 宽 × ~0.22 m 深 × ~0.30 m 高），**背面平贴墙面（y=0）、底部坐 z=0**、出风朝下前方。root `housing` 由 CadQuery YZ 侧剖面 extrude 成型（侧剖面家族即 body_form），内部 boolean 掏出：① 下前脸的**出风口 / louver 开口**、② 顶部浅进风格栅框、③ 检修盖后方的浅**滤网腔（filter cavity）**（内含 `filter_frame`+`filter_mesh` 固定 visual）、④ 出风口后的**中空暗色 cross-flow 风机腔（plenum）**（内嵌暗色 `plenum_liner` 圆柱，透过 louver 开口读作黑洞般的送风腔）。前面板是一块大边框检修盖（service cover），按某种铰链机构开合露出滤网（**主活动语义之一**）；下前脸出风口按某种导风机构动作（**主活动语义之二**）。

三层主活动/形态语义：
- **body_form（③ 主体形态家族）**：壳体侧剖面家族——rounded_bottom_curve（下前圆角）/ boxy_rectangular（方角箱体平前脸）/ raked_wedge（强前倾楔形）/ full_bullnose_capsule（上下双圆角胶囊）。改 mesh 母线与出风/panel 落点，不增减 joint。
- **airflow_mechanism（主机构）**：three_independent_slim_vanes（N 片独立横导风叶 REVOLUTE +X）/ single_wide_deflector（1 片全宽偏导板 REVOLUTE +X）/ vertical_vane_bank（~12 片竖导风叶 REVOLUTE +Z）/ closing_outlet_door（1 面下沿铰出风门 REVOLUTE −X）。
- **service_panel（检修盖机构）**：top_hinge_lift（顶铰上掀 REVOLUTE +X）/ two_leaf_clamshell（双叶顶铰 REVOLUTE +X ×2）/ bottom_hinge_drop_front（底铰前翻 REVOLUTE −X）。

默认成熟域：0.90×0.22×0.30 m 白色光泽壳体，背贴墙坐地；一套出风机构 + 一块（或两叶）检修盖 + 暗色 plenum + 浅滤网腔。每个 airflow/panel 机构 ≥1 non-fixed joint。palette_style 4–6 套写实配色（见 §配色板）。

不该混入（详见 §11）：**空气净化器 / 塔扇 / 落地箱扇**（立式圆/柱身，非壁挂水平壳体、无墙面贴合/plenum/检修盖 louver 语义）、**排气扇 / 换气口**（薄墙嵌入格栅、无壳体机身）、**分体式空调室外机（Facade/AC outdoor unit）**（带大轴流风扇栅 + 压缩机箱 + 冷凝器盘管，朝外散热，非室内送风白壳）。

## 槽位 + 候选模块表

> **建模注记**：`housing` 是 root 共享件（`housing_shell` mesh + `plenum_liner` + `filter_frame`/`filter_mesh` 固定 visual）。body_form 决定 root `_housing_shape` 的侧剖面 mesh 与派生落点求解器（`_arc_point` / `_face_point` / `_top_arc_point`），并把出风口 / louver slot / panel-hinge 的 origin 与法向角送给下游两个机构 slot；它**不新增 joint**。airflow_mechanism 与 service_panel 作为 root housing 的**并行子层**各自挂活动件。`vane_count` 是 multiplicity 轴，**仅在 airflow=three_independent_slim_vanes 时激活**（复制横导风叶）。三 slot 笛卡尔积 × vane_count 构成拓扑多样性（§9）。所有 body_form 候选都提供 `_arc_point`/`_face_point` 风格的"给 theta/fraction 返回下前脸 (y,z) 点 + 该点外法向角"接口，使 airflow / service_panel 机构可与任一 body_form 装配。

### Slot A：body_form（**③ 主体形态家族 slot**——壳体侧剖面 mesh 家族，连续尺寸由模板缩放，这里列结构不同的剖面原型）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 关键 helper·结构特征 |
|---|---|---|---|---|---|---|
| rounded_bottom_curve（基线）| forked_anchor | rec_model-a-...-e9cc92a3（P1）| `_arc_point` L86-88；`_housing_shape` L91-144（YZ moveTo→threePointArc quarter-round→前倾 FRONT_LO/HI→TOP_FRONT）| Volumetric Envelope Form | eligible if compatible | 仅下前沿 quarter-round（ARC_CY/CZ/R=0.085/0.13/0.13）+ 近垂直前倾面；louver 沿弧 `_arc_point(theta)` |
| boxy_rectangular | forked_anchor | rec_variant-body-form-boxy-rectangular-..._6caa9319 | `_housing_shape` L89-153（YZ 直角箱截面 + 前脸 recess 台阶边）；louver origin 平前面 L275-285 | Planar Boundary Form | eligible if compatible | 棱角箱体、平直垂直前脸（AABB≈精确 box，run_tests L334-345 断言 sharp edges）；louver 沿平前面 `VANE_Z_CENTERS` |
| raked_wedge | forked_anchor | rec_variant-body-form-raked-wedge-..._072b1710 | `_face_point` L56-61；`FACE_NORMAL_ANGLE` L53；`_housing_shape` L112-193（楔形四边形 + 斜面 recess/slot）| Planar Boundary Form | eligible if compatible | 强前倾楔形（WEDGE_LO_Y=0.26 底前 far-forward → HI_Y=0.10 顶前 receded）；louver/panel origin 带 `rpy=FACE_NORMAL_ANGLE` |
| full_bullnose_capsule | forked_anchor | rec_variant-body-form-full-bullnose-capsule-..._4b99b445 | `_arc_point` L94-97 + `_top_arc_point` L100-107；`_housing_shape` L110-177（上下双 threePointArc，BULLNOSE_R=0.09）| Volumetric Envelope Form | eligible if compatible | 上下前沿同半径双圆角胶囊剖面；plenum/liner 半径缩小；panel 更矮更低 |

硬约束记录：body_form 4 candidate（达 3-6 目标），全为 `forked_anchor`。四者是**真实 Primary Form Family 原型差异**（换 planar boundary / volumetric envelope 侧剖面母线），非纯缩放/换色——rounded=quarter-round 体量包络、boxy=方角平面边界、wedge=倾斜平面边界、bullnose=双圆角体量包络。part tree / interface（下前脸出风带 + 顶进风 + 检修盖凹座 + plenum）四者一致，只改 `_housing_shape` mesh 与落点求解器，不增减 joint（符合 Rule 3）。**这是本小类登记进 `slot_choices` 的 ③ Primary Form Family slot。**

### Slot B：airflow_mechanism（**主机构槽**——出风导向动作，挂 root housing 下前脸出风口）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·joint·helper 名 / 结构特征 |
|---|---|---|---|---|---|
| three_independent_slim_vanes（基线）| forked_anchor | rec_model-a-...-e9cc92a3（P1）| `{label}_louver_vane` part L239-256；`{label}_louver_pivot` REVOLUTE axis=(1,0,0) origin=弧点+`rpy=(theta−π/2,0,0)` L258-272；slot cut L134-143 | eligible if compatible | N 片独立横导风叶（薄 Box blade + 两端 `{label}_pivot_pin`），各绕 **X 宽度轴** ±45°；N 由 vane_count multiplicity 控（见 §8）；N REVOLUTE +X / 单元 |
| single_wide_deflector | forked_anchor | rec_variant-airflow-mechanism-single-wide-deflector-..._4f557258 | `_deflector_shape` L173-191；`deflector` part L266-279；`deflector_pivot` REVOLUTE axis=(1,0,0) origin=`_arc_point(HINGE_THETA≈80°)`+`rpy` L282-302；outlet cut L139-149 | eligible if compatible | 一片全宽偏导板（`_deflector_shape` 带 return lip + 两端 `pivot_pin`）绕 **X 轴**（−10°..60°）；单 REVOLUTE +X，无 louver |
| vertical_vane_bank | forked_anchor | rec_variant-airflow-mechanism-vertical-vane-bank-..._148eace8 | `_vane_center_x` L96-99；`_vertical_vane_blade_shape` L102-109；`vertical_vane_{i}`(+`vane_shaft_{i}`) part L260-276；`vane_pivot_{i}` REVOLUTE **axis=(0,0,1)** origin=`(vx, ay, az)` L278-292 | eligible if compatible | ~12 片竖导风叶等距横排（薄板 + 竖 shaft，`for i in range(N_VERTICAL_VANES)`），各绕 **Z 竖轴** ±45° 左右摆；~N_V REVOLUTE +Z（固定 12，不进 vane_count） |
| closing_outlet_door | forked_anchor | rec_variant-airflow-mechanism-closing-outlet-door-..._97104f78 | `_outlet_opening_cut` L91-121；`_outlet_door_shape` L194-248；`outlet_door` part L323-336；`outlet_door_hinge` REVOLUTE **axis=(−1,0,0)** origin=`_arc_point(DOOR_THETA_LOW=15°)` L339-353 | eligible if compatible | 整面弧形出风门 + 顶 grab lip + 两端 `door_pivot_pin`，绕 **X 轴（−1,0,0）下沿铰** 0..75° 下翻/齐平闭合；单 REVOLUTE −X |

硬约束记录：airflow_mechanism 4 candidate（达 3-6 目标），全为 `forked_anchor`。跨真实 joint 拓扑：横导风叶 N×REVOLUTE +X（含 vane_count multiplicity）/ 单偏导板 1×REVOLUTE +X / 竖叶组 ~12×REVOLUTE **+Z 竖轴** / 出风门 1×REVOLUTE **−X 下铰**——覆盖 +X / +Z / −X 三种轴向（① 骨架图 + ② 关节类型双轴差异）。每 candidate ≥1 non-fixed joint。

### Slot C：service_panel（前面板/检修盖机构——挂 root housing 检修盖凹座）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·joint 名 / 结构特征 |
|---|---|---|---|---|---|
| top_hinge_lift（基线）| forked_anchor | rec_model-a-...-e9cc92a3（P1）| `_front_panel_shape` L147-164（plate 沿 −Z hang）；`front_panel` part L208-222；`front_panel_hinge` REVOLUTE axis=(1,0,0) origin=`(0, PANEL_HINGE_Y, PANEL_HINGE_Z=0.290)` L223-236 | eligible if compatible | 顶沿铰单叶检修盖上掀（0..60°），plate 本地 −Z hang + 两 `hinge_knuckle`；1 REVOLUTE +X |
| two_leaf_clamshell | forked_anchor | rec_variant-service-panel-two-leaf-clamshell-..._3fe5a919 | `NUM_LEAVES=2`/`LEAF_W`/`LEAF_CX` L62-68；`_front_panel_shape(leaf_w)` L157-175；`panel_{i}`(+`panel_{i}_hinge_knuckle_{k}`) part + `panel_{i}_hinge` REVOLUTE axis=(1,0,0) L221-250 | eligible if compatible | 左右两窄叶各顶铰独立上掀（`for i in range(NUM_LEAVES)`），各 REVOLUTE +X；2 REVOLUTE +X，独立开合（run_tests L404-419） |
| bottom_hinge_drop_front | forked_anchor | rec_variant-service-panel-bottom-hinge-drop-front-..._fd012151 | `_front_panel_shape` L148-165（plate 沿 **+Z rise**，本地 frame 在底边）；`front_panel` part L209-223；`front_panel_hinge` REVOLUTE **axis=(−1,0,0)** origin=`(0, PANEL_HINGE_Y=0.2145, PANEL_HINGE_Z=0.1435)` L224-237 | eligible if compatible | 底沿铰单叶前翻检修盖（0..60°，顶自由边前下翻露 filter），plate 本地 +Z rise + 底边 `hinge_knuckle`；1 REVOLUTE −X |

硬约束记录：service_panel 3 candidate（达下限 3），全为 `forked_anchor`。跨真实差异：顶铰单叶 REVOLUTE +X / 顶铰双叶 REVOLUTE +X ×2（① 骨架图 part-joint count 差 + 独立开合语义）/ 底铰单叶 REVOLUTE **−X**（② 关节类型/轴向差 + plate 本地母线上下翻转）。每 candidate ≥1 non-fixed joint。

## 槽位图（slot graph）

pattern: mixed（`housing` 为 root；airflow_mechanism 与 service_panel 为并行子层各挂活动件；body_form 重写 root mesh 与落点；`vane_count` 一根 multiplicity 轴，gated to three_independent_slim_vanes）

```
housing [ROOT, 背贴墙 y=0, 坐地 z=0, 居中 x=0]
  │  housing_shell (mesh, 侧剖面 = body_form)  + plenum_liner(暗圆柱) + filter_frame + filter_mesh (固定 visual)
  │  body_form 重写 _housing_shape mesh、_arc_point/_face_point/_top_arc_point 落点求解器与外法向角
  │  （不新增 joint；把"下前脸出风带落点+法向"与"检修盖凹座 origin+法向"送给下游两 slot）
  │
  ├── airflow_mechanism (主机构; 挂下前脸出风口):
  │     three_independent_slim_vanes:
  │       housing --[{label|i}_louver_pivot: REVOLUTE +X @ 弧点, rpy=面法向]--> {label|i}_louver_vane   (×vane_count)   ← multiplicity 轴
  │     single_wide_deflector:
  │       housing --[deflector_pivot: REVOLUTE +X @ _arc_point(HINGE_THETA), rpy=面法向, −10°..60°]--> deflector
  │     vertical_vane_bank:
  │       housing --[vane_pivot_{i}: REVOLUTE +Z(竖轴) @ (vx, outlet 弧点)]--> vertical_vane_{i}        (×~12 固定)
  │     closing_outlet_door:
  │       housing --[outlet_door_hinge: REVOLUTE −X(下铰) @ _arc_point(DOOR_THETA_LOW), 0..75°]--> outlet_door
  │
  └── service_panel (检修盖机构; 挂检修盖凹座):
        top_hinge_lift:
          housing --[front_panel_hinge: REVOLUTE +X @ (0, HINGE_Y, HINGE_Z=top), 0..60°]--> front_panel
        two_leaf_clamshell:
          housing --[panel_{i}_hinge: REVOLUTE +X @ (LEAF_CX[i], HINGE_Y, HINGE_Z=top), 0..60°]--> panel_{i}   (×2)
        bottom_hinge_drop_front:
          housing --[front_panel_hinge: REVOLUTE −X @ (0, HINGE_Y, HINGE_Z=bottom), 0..60°]--> front_panel
```

接口点位与 joint 语义：
- **body_form → 下游接口**：每个 body_form 候选提供"给下前脸参数（arc theta 或 face fraction）返回 `(y,z)` 落点 + 该点外法向角"的求解器（rounded/bullnose 用 `_arc_point`（θ 弧角，法向角 `theta−π/2`）；boxy 用平前面直落（`(BODY_D, VANE_Z_CENTERS[i])`，法向沿 +Y=0 角）；wedge 用 `_face_point(fraction)` + 常量 `FACE_NORMAL_ANGLE`）。airflow / service_panel 机构消费该接口把 joint origin 与 `rpy` 对齐到当前壳体表面法向。这是 body_form 与两机构 slot 装配的唯一契约。
- **airflow 接口**：three_independent 横导风叶 `{label|i}_louver_pivot` origin 落在下前脸弧/面点，`axis=(1,0,0)`（+X 宽度轴），`rpy` 对齐面法向使 q=0 blade 贴合表面切向；两端 `pivot_pin` 有意嵌入 slot 端壁 → element-scoped `allow_overlap(vane↔housing, pin↔housing_shell)`。single_deflector `deflector_pivot` origin=`_arc_point(HINGE_THETA)`，`axis=(1,0,0)`（−10°..60°），blade 沿 −Z hang、正 q 外摆 +Y 下导流。vertical_vane_bank `vane_pivot_{i}` origin=`(vx, outlet 弧点)`，`axis=(0,0,1)`（竖轴 ±45°），竖 `vane_shaft_{i}` 有意嵌入 outlet 上壁 → `allow_overlap(vane↔housing, shaft↔housing_shell)`。closing_outlet_door `outlet_door_hinge` origin=`_arc_point(DOOR_THETA_LOW=15°)`，`axis=(−1,0,0)`（下沿铰 0..75°），弧形门外表面与壳体弧齐平（seated fit）→ `allow_overlap(door↔housing, door_panel↔housing_shell + door_pivot_pin↔housing_shell)`。
- **service_panel 接口**：top_hinge_lift / two_leaf_clamshell 的 hinge origin 落在检修盖凹座**顶沿**（`(0|LEAF_CX[i], PANEL_HINGE_Y, PANEL_HINGE_Z=顶)`），`axis=(1,0,0)`（q=0 闭合盖住前脸、正 q 上掀 0..60°）；plate 本地 −Z hang。bottom_hinge_drop_front hinge origin 落在凹座**底沿**（`(0, PANEL_HINGE_Y, PANEL_HINGE_Z=底)`），`axis=(−1,0,0)`（正 q 前下翻），plate 本地 +Z rise。`hinge_knuckle_*` 有意嵌入凹座壁 → `allow_overlap(panel↔housing, hinge_knuckle↔housing_shell)`；关时 panel plate 覆盖前脸 → `expect_overlap(panel, housing, axes="xz")`。检修盖 origin 需随 body_form 顶前沿位置（rounded/bullnose/wedge/boxy 的 PANEL_HINGE_Y/Z 不同）适配。
- **multiplicity 接口**：`vane_count` **仅在 airflow=three_independent_slim_vanes 时激活**，沿下前脸弧/面等角（等分数）分布 N 片横导风叶 + N 道 slot cut，`for i in range(vane_count)` 单循环发射 `louver_vane_{i}` / `louver_pivot_{i}`，每片独立 REVOLUTE +X。其余三种 airflow 不暴露 vane_count（deflector=1、vertical_bank 固定 ~12、door=1）。
- **rest pose**：所有活动件 q=0 闭合——louver/deflector/vertical vane 贴合表面（q=0 覆盖 slot），outlet_door 齐平闭合，service_panel 盖住前脸。出风叶摆动 / 偏导板外摆 / 竖叶左右扫 / 出风门下翻 / 检修盖开合为 viewer 目检的活动语义；`plenum_liner` / `filter_*` 固定。
- **mating policy**：pivot pin / shaft / knuckle / 齐平门 的 seated 重叠为 captured / 友配（有意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实弧点 / outlet / 凹座沿）+ element-scoped `allow_overlap`（迁移各样本 run_tests 的 `ctx.allow_overlap` + `ctx.expect_contact`）。
- **互斥 / 可选**：airflow_mechanism 各候选互斥（一机一种出风机构）；service_panel 各候选互斥；body_form 各候选互斥；vane_count 仅在 three_independent_slim_vanes 下有意义（gated）。

## 每槽位 Module Emits / Interfaces

### root / housing（共享件，body_form 重写其 mesh）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（root，visual：`housing_shell` mesh + `plenum_liner` 暗圆柱 + `filter_frame`/`filter_mesh` Box）| P1 L178-205 |
| internal joints | 无（root 本身无活动件）| — |
| upstream interface | 背贴墙 y=0、坐地 z=0、居中 x=0；由 body_form `_housing_shape` 定侧剖面 | P1 `_housing_shape` L91-144 / `run_tests` grounding L306-310 |
| downstream interface | 下前脸出风带落点+法向（送 airflow）+ 检修盖凹座 origin+法向（送 service_panel）+ plenum 后腔 | P1 `_arc_point` L86-88；PANEL_HINGE_Y/Z L55-56；PANEL_RECESS_Y/ZONE L48-49 |

### Slot A / body_form（重写 root mesh + 落点求解器，不发射独立 part/joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（改 root `housing_shell` mesh 与 plenum/filter 落点）| P1 L91-144 / boxy L89-153 / wedge L112-193 / bullnose L110-177 |
| internal joints | 无 | — |
| downstream interface | 下前脸落点求解器（`_arc_point`/`_face_point`/`_top_arc_point`）+ 检修盖凹座位姿 | rounded `_arc_point` L86-88 / boxy `VANE_Z_CENTERS` L61 / wedge `_face_point` L56-61 / bullnose `_arc_point`+`_top_arc_point` L94-107 |

### Slot B / airflow_mechanism（每候选发射对应活动出风件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{label|i}_louver_vane`(×vane_count) / `deflector` / `vertical_vane_{i}`(×~12) / `outlet_door` | P1 L239-256 / deflector L266-279 / vertical L260-276 / door L323-336 |
| internal joints | `{label|i}_louver_pivot` REVOLUTE +X（×N）/ `deflector_pivot` REVOLUTE +X / `vane_pivot_{i}` REVOLUTE +Z（×~12）/ `outlet_door_hinge` REVOLUTE −X | P1 L258-272 / deflector L282-302 / vertical L278-292 / door L339-353 |
| upstream interface | 挂 root housing 下前脸出风口（origin=body_form 落点，rpy=面法向）| P1 L263-267 / deflector L291-294 / vertical L283 / door L344-349 |

### Slot C / service_panel（每候选发射活动检修盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_panel`(+`hinge_knuckle_{idx}`) / `panel_{i}`(+`panel_{i}_hinge_knuckle_{k}`, ×2) / `front_panel`(底铰, plate +Z rise) | P1 L208-222 / clamshell L221-236 / drop_front L209-223 |
| internal joints | `front_panel_hinge` REVOLUTE +X（top）/ `panel_{i}_hinge` REVOLUTE +X（×2）/ `front_panel_hinge` REVOLUTE −X（bottom）| P1 L223-236 / clamshell L237-250 / drop_front L224-237 |
| upstream interface | 挂 root housing 检修盖凹座（origin 顶沿 / 底沿，随 body_form 顶前沿位置适配）| P1 PANEL_HINGE_Y/Z L55-56 / drop_front L57 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | rounded_bottom_curve / boxy_rectangular / raked_wedge / full_bullnose_capsule | rounded_bottom_curve | choice | deterministic procedural sampler 选 | Slot A 表 |
| airflow_mechanism | enum | three_independent_slim_vanes / single_wide_deflector / vertical_vane_bank / closing_outlet_door | three_independent_slim_vanes | choice | sampler 选 | Slot B 表 |
| service_panel | enum | top_hinge_lift / two_leaf_clamshell / bottom_hinge_drop_front | top_hinge_lift | choice | sampler 选 | Slot C 表 |
| vane_count | int (multiplicity) | [2, 6] | 3 | conditional | 仅 airflow=three_independent_slim_vanes 激活；加权采样（小 N 偏多），见 §8 | source map Multiplicity / vane-count-2·5 |
| palette_style | enum | glossy_white_classic / warm_cream / graphite_dark / champagne_gold / matte_silver / sky_soft_blue（**6 配色**，见 §配色板）| glossy_white_classic | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)` | 各样本 `model.material(...)`（见 §配色板，锚 5★ RGBA）|
| body_width_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 BODY_W → louver SLOT_LEN / VANE_LEN / pivot_pin X / plenum LINER 半长 / panel PANEL_W 同步派生，clamp | P1 BODY_W L37 |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_H → panel-zone / hinge z / top-arc（bullnose）同步，clamp | P1 BODY_H L39 |
| body_depth_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 BODY_D / 弧半径 / 楔形前伸 → plenum 深度 / outlet cut 深度同步，clamp | P1 BODY_D L38 / wedge WEDGE_LO_Y L42 |
| louver_len_scale | float | derived | 1.0 | equation | `VANE_LEN = SLOT_LEN·k`、`SLOT_LEN = BODY_W·body_width_scale − 2·slot_end_margin`，不独立采样 | P1 SLOT_LEN/VANE_LEN L71-74 |
| panel_width_scale | float | derived | 1.0 | equation | `PANEL_W = BODY_W·body_width_scale − 2·panel_side_gap`（clamshell 时 `LEAF_W=(PANEL_W−LEAF_GAP)/2`），不独立采样 | P1 PANEL_W L52 / clamshell L64 |
| vane_swing | float (rad) | [30°, 55°] | 45° | independent | 缩放横导风叶 / 竖叶 pivot ±swing，clamp | P1 VANE_SWING L77 |
| deflector_swing_hi | float (rad) | [45°, 70°] | 60° | conditional | 仅 single_wide_deflector 生效；upper limit clamp（下限固定 −10°）| deflector L77-78 |
| door_open_max | float (rad) | [60°, 80°] | 75° | conditional | 仅 closing_outlet_door 生效；outlet_door upper limit clamp | door DOOR_OPEN_MAX L71 |
| panel_open_max | float (rad) | [50°, 65°] | 60° | independent | 缩放检修盖 hinge upper limit，clamp ≤65° 防大幅越界 | P1 PANEL_OPEN_MAX L58 |
| (—) | constraint | — | — | inequality | vane_count 弧带容量：`vane_count · (SLOT_OPEN + min_vane_gap) ≤ 可用下前脸弧长`（叶太多则回缩 vane_count 或减 SLOT_OPEN；仅 three_independent 时求解）| P1 `_arc_point` 弧带 + vane-count-5 均分 L72-75 |
| (—) | constraint | — | — | inequality | 检修盖不挡出风口：`panel plate 底沿 z ≥ 出风带顶沿 z + clearance`（检修盖闭合姿态不覆盖 airflow 出风口；bottom_hinge_drop_front 尤须，其铰在低 z）| drop_front PANEL_HINGE_Z=0.1435 vs 出风带 L57 |
| (—) | constraint | — | — | inequality | closing_outlet_door 全开不撞地/墙：`outlet_door 下翻末端 z ≥ 0` 且不越 y=0（door_open_max 投影约束，仅 closing_outlet_door 时求解）| door open QC L513-529 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`louver_len_scale` / `panel_width_scale` 为 equation（跟随 body_width_scale）。`deflector_swing_hi` / `door_open_max` 为 conditional（各仅对应 airflow 候选生效）。vane_count 弧带容量 / 检修盖不挡出风 / 出风门不撞地 三条 inequality 在 resolve 内投影 / 回缩。scale 只动安全比例 / clearance / 行程 / 角度，绝不改 body_form / airflow / service_panel 拓扑或 vane_count multiplicity 语义。

## 配色板 / Palette（palette_style，6 套写实配色）

> **palette only**：`palette_style` 是颜色/材质换皮轴，**不计入 slot_choice**、不改任何 slot/candidate/multiplicity/joint/dimension/topology。每 seed 单次 `rng.choice(PALETTE_STYLES)` 选一套，整机统一应用。每套解析下列 `mats[...]` key：`shell`（`shell_white` 壳体）/ `panel`（`panel_white` 检修盖 & 出风叶/偏导板/门，即 `vane_white`/`deflector_white`/`door_white` 统一）/ `cavity`（`cavity_dark` 暗色 plenum liner）/ `filter_frame`（`filter_gray` 滤网框）/ `filter_mesh`（`mesh_gray` 滤网网面）。锚定 5★ 样本 RGBA（`shell_white` 0.93/0.94/0.95、`panel_white` 0.96/0.965/0.97、`vane_white` 0.88/0.895/0.91、`deflector_white` 0.88/0.895/0.91、`door_white` 0.91/0.92/0.935、`cavity_dark` 0.07/0.07/0.08、`filter_gray` 0.80/0.81/0.82、`mesh_gray` 0.30/0.32/0.34），其余为写实推断色（家电写实区间，非霓虹）。

| # | palette_style | `mats["shell"]` 壳体 | `mats["panel"]` 盖/出风件 | `mats["cavity"]` plenum | `mats["filter_frame"]` | `mats["filter_mesh"]` | 锚定 / 说明 |
|---|---|---|---|---|---|---|---|
| 1 | `glossy_white_classic`（基线/默认）| (0.93, 0.94, 0.95, 1.0) | (0.96, 0.965, 0.97, 1.0) | (0.07, 0.07, 0.08, 1.0) | (0.80, 0.81, 0.82, 1.0) | (0.30, 0.32, 0.34, 1.0) | 直接锚 5★ 全套；经典光泽纯白室内机 |
| 2 | `warm_cream` | (0.95, 0.93, 0.87, 1.0) | (0.97, 0.955, 0.90, 1.0) | (0.09, 0.08, 0.07, 1.0) | (0.82, 0.79, 0.72, 1.0) | (0.34, 0.32, 0.28, 1.0) | 暖米白/象牙壳体（老式/居家风）；cavity/filter 取暖灰 |
| 3 | `graphite_dark` | (0.24, 0.25, 0.27, 1.0) | (0.30, 0.31, 0.33, 1.0) | (0.05, 0.05, 0.06, 1.0) | (0.34, 0.35, 0.37, 1.0) | (0.16, 0.17, 0.18, 1.0) | 深石墨灰/黑机身（现代高端设计款）；出风件略浅深灰 |
| 4 | `champagne_gold` | (0.86, 0.82, 0.72, 1.0) | (0.90, 0.86, 0.75, 1.0) | (0.08, 0.07, 0.06, 1.0) | (0.72, 0.66, 0.54, 1.0) | (0.40, 0.36, 0.28, 1.0) | 香槟金/浅金属米色（旗舰装饰款）；写实低饱和 |
| 5 | `matte_silver` | (0.78, 0.79, 0.80, 1.0) | (0.84, 0.85, 0.86, 1.0) | (0.07, 0.07, 0.08, 1.0) | (0.62, 0.64, 0.66, 1.0) | (0.28, 0.30, 0.32, 1.0) | 哑光银/浅灰金属机身（商用/工业风）；锚 `filter_gray`→银灰 |
| 6 | `sky_soft_blue` | (0.90, 0.93, 0.95, 1.0) | (0.86, 0.91, 0.95, 1.0) | (0.07, 0.08, 0.09, 1.0) | (0.76, 0.80, 0.84, 1.0) | (0.28, 0.32, 0.36, 1.0) | 极浅天蓝/冷白壳体（清凉主题款）；写实浅冷色 |

> 6 套均落在家电写实区间（无饱和霓虹），每套保持 shell/panel 亮、cavity 暗、filter 中灰的功能对比（透过 louver 仍读作暗色送风腔）。materials 大类跨 painted-plastic（1/2/6）与 metal（3 石墨 / 4 香槟金 / 5 哑光银），材质大类覆盖 ≥ ceil(0.5×6)=3。palette-only，仅换 `model.material` 的 rgba + 材质语义注释，不增 part/joint/几何。

## Multiplicity / Copy Logic

本小类有 **1 根 multiplicity 轴**（gated）：

- `count_param`：`vane_count`（下前脸横向导风叶数）
- `N_range`：`[2, 6]`（室内机出风口现实叶片数有限；样本覆盖 N∈{2, 3(parent), 5}，模板采样域略大于样本覆盖正常）
- sampling domain（权重档）：小 N 高频、大 N 稀有。建议 `2:0.22, 3:0.34, 4:0.24, 5:0.14, 6:0.06`（归一化，3 为 parent 基线偏多）；sweep 测试偏小（N≤4 多采），产品全程 [2,6] 都合法（沿弧均分 `range(N)` 复制天然安全，受 §7 弧带容量 inequality 守）。
- copied object：单片横向导风叶 = 薄 Box `blade`（`VANE_LEN×VANE_T×VANE_CHORD`）+ 两端 `pivot_pin` Cylinder；每片一道 `SLOT_LEN×SLOT_DEPTH×SLOT_OPEN` slot cut 在 root housing 下前脸。
- naming：`louver_vane_{i}`（part）/ `vane_blade_{i}` + `pivot_pin_{i}_{idx}`（或 `vane_pivot_pin_{i}_{idx}`，visual）/ `louver_pivot_{i}`（joint），`for i in range(vane_count)`（沿 vane-count-5 的 `_add_louver_vane(model, housing, i, theta)` 共享 factory 蓝本，L178-216）。
- placement：沿下前脸弧/面等角（等分数）分布，`VANE_THETAS = tuple(θ_lo + i·(θ_hi−θ_lo)/(N−1) for i in range(N))`（或样本 N=2 的 `θ_min + step·(i+1)` 边距变体），θ 范围随 body_form 取该壳体下前脸的可用弧段。
- joint policy：每片**独立活动** REVOLUTE（axis (1,0,0) +X 宽度轴，±vane_swing），origin 落该叶弧/面点、`rpy` 对齐面法向；统一策略（vane-count-5 run_tests L466-477 断言 uniform policy）。
- source/gating：**仅当 airflow_mechanism == three_independent_slim_vanes 时激活**——其余三种 airflow（single_wide_deflector=1 片、vertical_vane_bank 固定 ~12 竖叶、closing_outlet_door=1 门）**不暴露 vane_count**；模板 sampler 先采 airflow，若非 three_independent 则 vane_count 归一为 n/a（不进 slot_choices 计数、不复制）。vertical_vane_bank 的 12 片竖叶是该 candidate 内部固定 count（不是 vane_count multiplicity 轴，见 §8.5 ①-multiplicity）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | 三根登记 slot 都改运动学图：**airflow_mechanism** = three_independent_slim_vanes（N 片 louver part + N REVOLUTE）/ single_wide_deflector（1 deflector part + 1 REVOLUTE）/ vertical_vane_bank（~12 竖叶 part + ~12 REVOLUTE）/ closing_outlet_door（1 门 part + 1 REVOLUTE）——part/joint count 与图形态皆不同；**service_panel** = top_hinge_lift（1 panel + 1 边）/ two_leaf_clamshell（2 panel + 2 边）/ bottom_hinge_drop_front（1 panel + 1 边）。全 `forked_anchor`（见 §4 各 record + `model.py:Lx-Ly`）。 |
| └ multiplicity | 同构件 ×N | **有** | `vane_count` N∈[2,6]（gated to three_independent_slim_vanes），权重档见 §8。N 只覆盖不计结构 distinct。（vertical_vane_bank 的 12 竖叶为该 candidate 内部固定 count，非 multiplicity 轴。） |
| ② 关节类型 | 图不变，某条边换 type/轴 | **有** | 全 REVOLUTE，但**轴向**分三种、须都在 sweep 出现：airflow +X（louver/deflector）、airflow **+Z 竖轴**（vertical_vane_bank）、airflow **−X 下铰**（closing_outlet_door）；service_panel +X（top/clamshell）、service_panel **−X**（bottom_hinge_drop_front）。均 `forked_anchor`（§4）。声明的每种轴向都由对应 candidate 保证出现。 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | **body_form slot（登记进 slot_choices，本类的 ③ Primary Form Family slot）**：rounded_bottom_curve（Volumetric Envelope Form，下前 quarter-round 体量包络）/ boxy_rectangular（Planar Boundary Form，方角平面边界）/ raked_wedge（Planar Boundary Form，倾斜平面边界）/ full_bullnose_capsule（Volumetric Envelope Form，上下双圆角体量包络）。全 `forked_anchor`（§4 各 record + line span）；同 part tree / interface，只改 `_housing_shape` 侧剖面 mesh。≥3 可识别主体形态原型达标。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **无** | 样本装饰仅顶部浅进风格栅框（`_housing_shape` cut）+ 检修盖 border frame recess + louver blade 本身——这些是 body_form / service_panel / airflow part 的内在结构或宿主 visual，非可换的装饰 style，也无装饰数量档。无独立 ④ 轴；不为凑轴发明贴花/条纹。plenum liner / filter mesh 属 ⑥ 涂装对比，不属 ④。 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | **有** | 关键比例（见 §7）：body_width_scale [0.85,1.15] / body_height_scale [0.90,1.12] / body_depth_scale [0.90,1.10]（louver_len/panel_width equation 派生）；关节行程范围 vane_swing [30°,55°]、panel_open_max [50°,65°]、deflector_swing_hi [45°,70°]（cond）、door_open_max [60°,80°]（cond）。**运动包络 + motion_test_plan**：① 横导风叶/竖叶/偏导板 pivot：轴 +X 或 +Z，[−swing, +swing] 或 [闭合0, 可行上界]，须跑 sampled collision + targeted `ctx.pose({pivot:±swing})`（迁移各样本 blade-tilt / vane-sweep 决定性检查）；② closing_outlet_door：轴 −X，[0, door_open_max]，targeted `ctx.pose({door:open})` 断言下翻末端不撞地/墙（§7 inequality）；③ service_panel hinge：轴 ±X，[0, panel_open_max]，targeted `ctx.pose({hinge:open})` 断言开时露 filter 且闭合姿态不挡出风口（§7 inequality）；clamshell 加"开 leaf0 时 leaf1 保持闭合"独立性 pose。全程不得穿模；关节数≤6，`max_pose_samples` 96（含 vertical_vane_bank 12 竖叶时降 32）。 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 材质大类：painted-plastic（glossy_white_classic / warm_cream / sky_soft_blue）+ metal（graphite_dark / champagne_gold / matte_silver）；配色 6 套（见 §配色板）。材质大类覆盖 2 ≥ ceil(0.5×… )，配色 6 ∈ [3,6]。每套保持 shell 亮 / cavity 暗 / filter 中灰的功能对比。 |

**收尾自检**：body_form 四原型（圆角/方角/楔形/胶囊）在 batch 0-9 拉得开；airflow 三轴向（+X 横/+Z 竖/−X 门）+ service_panel 两轴向（+X/−X）都出现；6 配色（3 塑料 + 3 金属大类）都出现；关节开合全程不穿模、检修盖开露 filter、出风门下翻不撞地——做到即达标。④ 声明"无"已给理由（无可换装饰 style / 无装饰数量档）。

## 拓扑多样性审计

总组合数：body_form(4) × airflow_mechanism(4) × service_panel(3) = **48**，再叠 vane_count multiplicity（N∈[2,6]=5，仅 three_independent_slim_vanes 下有效）。
（vane_count 仅在 4 个 airflow 中的 1 个下激活：three_independent 时 4×1×3×5=60 组合含 N；其余 3 个 airflow×body×panel=36 组合无 N。合计离散 slot 组合 48，含 vane_count 展开后 = 36 + 4×3×5 = 96；无论按哪种口径都 ≫ 逐 slot key 覆盖下限。）

理由：三根登记 slot 各 ≥2 distinct（body_form 4 / airflow_mechanism 4 / service_panel 3），reachable（无 gate 让某 slot 完全不可达）；vane_count 只覆盖（N 采 ≥2 个不同值即可）不计数。airflow 跨 +X/+Z/−X 三轴向 + 不同 part/joint count，service_panel 跨 +X/−X + 单叶/双叶，body_form 换四种 planar/volumetric 侧剖面——都是 part tree / joint topology / mesh 母线的真实差异，非纯尺寸/颜色。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 依次 (1) `rng.choice` body_form，(2) `rng.choice` airflow_mechanism，(3) `rng.choice` service_panel，(4) 若 airflow==three_independent_slim_vanes 则 `rng.choices` 加权采 vane_count（小 N 偏多）否则 vane_count=n/a，(5) uniform 各连续 scale + `rng.choice` palette_style，(6) `resolve_config` 派生 equation + 投影 inequality（弧带容量 / 检修盖不挡出风 / 出风门不撞地）+ conditional 范围。compatibility matrix 排除/降级下述组合。无 regression overrides（首版纯 procedural）。random sweep seeds 0-4 → 0-19 → 0-49 分阶段；viewer 目检 seeds 0-9（覆盖各 body_form × airflow 轴向 × service_panel 轴向 × 小/大 vane_count）。

Topology target：1000-seed slot choice tuple distinct 预计 = body(4) × airflow(4) × panel(3) = 48 离散 slot 组合 + vane_count 展开档 ≈ 60-96 realized topology（低于 300 属正常：本小类真实结构词汇就是 4×4×3 + N，是该类目合理域，不强行注水）。低于 300 的原因即 service_panel(3) 与 vane_count gated 收窄了理论积；48 slot 组合 + N 覆盖已充分拉开视觉多样性（③ 形态 4 + ①② airflow/panel 轴向）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §7 连续 scale（body_width/height/depth_scale → louver_len/panel_width equation 派生；vane_swing / panel_open_max independent；deflector_swing_hi / door_open_max conditional）。全部 `resolve_config` clamp + 每 build 统一应用；弧带容量 / 检修盖不挡出风 / 出风门不撞地三条 inequality 在 resolve 内投影/回缩，不留到 builder。这些 scale 不破坏 airflow joint origin（下前脸弧/面点）、检修盖 hinge origin（凹座沿）、坐地/贴墙、类别身份，也不改 vane_count multiplicity 语义或 body_form 原型。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` body_form/airflow/service_panel → 条件加权采 vane_count（仅 three_independent）→ uniform scale + palette | slot_choices_for_seed 含 (body_form, airflow_mechanism, service_panel[, vane_count]) 且与 build 一致 |
| compatibility matrix | (1) **vane_count gated**：仅 airflow=three_independent_slim_vanes 激活；其余 airflow 下 vane_count=n/a 不复制不计数。(2) body_form × airflow 正交：每个 body_form 提供落点求解器 + 面法向，任一 airflow 消费之（origin/rpy 适配）。(3) **body_form × service_panel 位姿适配**：检修盖 hinge origin(顶/底沿)随 body_form 顶前沿位置(rounded/bullnose 弧顶 vs boxy/wedge 顶前)在 resolve 派生，不 gate-out。(4) **airflow × service_panel clearance**（潜在不兼容）：closing_outlet_door（出风门下沿铰、占满下前脸）与 bottom_hinge_drop_front（检修盖底沿铰在低 z、前翻）都在下前脸低区活动——resolve 用 §7"检修盖不挡出风 / 门开不撞地"两条 inequality 保二者铰点与行程分区（门铰在出风带底 DOOR_THETA_LOW≈15°、panel 底铰在 panel-zone 底 z≈0.144，二者 z 分离 + 各自向 +Y 外翻）；若数值回缩后仍冲突则降级 panel 到 top_hinge_lift（fallback，非硬 gate-out）。其余组合全合法。(5) 各 slot 候选组内互斥。| 无 floating / collision / joint 轴/origin 漂移 / 检修盖挡出风 / 门撞地墙 / 双低铰干涉 |
| controlled local variation | 3 主 scale + 2 equation 派生 + 2 conditional swing + panel_open_max，每 build clamp 统一；弧带容量/不挡出风/不撞地三 inequality 投影 | 比例变化不破坏 airflow/panel joint origin / 坐地贴墙 / 类别身份 / vane_count |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-4 初轮 / 0-19 / 0-49 分阶段；0-999 成熟审计 | （逐 slot key 覆盖）+ 关节动作 / 坐地贴墙 / overlap / airflow×panel clearance |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form（③ Primary Form Family）| 4 | yes | yes | rounded(Vol) / boxy(Planar) / wedge(Planar) / bullnose(Vol)；换侧剖面 mesh，不增 joint |
| airflow_mechanism（主机构）| 4 | yes | yes | 3-slim-vanes(N×REV +X) / deflector(1×REV +X) / vertical(~12×REV +Z) / outlet_door(1×REV −X) |
| service_panel | 3 | yes | yes | top_lift(REV +X) / clamshell(REV +X ×2) / drop_front(REV −X) |
| vane_count (multiplicity, gated) | N∈[2,6] | yes | yes | 加权采样，小 N 偏多；仅 three_independent_slim_vanes；range(N) 复制契约 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, airflow_mechanism, service_panel) 三轴 + 条件 vane_count（仅 three_independent 时含）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（三 slot rng.choice + 条件加权 vane_count）；seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；louver_len / panel_width equation 跟随 body_width/height；deflector_swing_hi / door_open_max conditional 仅对应 airflow；弧带容量 / 检修盖不挡出风 / 出风门不撞地三 inequality 在 resolve 投影/回缩
- compatibility matrix / gating：vane_count 仅 three_independent_slim_vanes 激活；body_form 落点求解器 + 面法向送两机构 slot；检修盖 hinge origin 随 body_form 顶前沿派生；closing_outlet_door × bottom_hinge_drop_front 低区 clearance 由 inequality 分区（回缩仍冲突则 fallback top_hinge_lift）
- 连续 scale clamp 后不破坏 airflow joint origin（下前脸弧/面点）/ 检修盖 hinge origin（凹座沿）/ 坐地贴墙 / 类别身份 / vane_count multiplicity
- 关键 joint：three_independent `{i}_louver_pivot` REVOLUTE +X (abs(axis[0])>0.99, origin 在弧点)；single_wide_deflector `deflector_pivot` REVOLUTE +X；vertical_vane_bank `vane_pivot_{i}` REVOLUTE **+Z** (abs(axis[2])>0.99)；closing_outlet_door `outlet_door_hinge` REVOLUTE **−X** (axis≈(−1,0,0))；service top/clamshell `*_hinge` REVOLUTE +X；service drop_front `front_panel_hinge` REVOLUTE **−X**
- multiplicity：vane 复制用 `for i in range(vane_count)` 单循环（沿 `_add_louver_vane` 蓝本），弧/面等角均分
- captured-fit：element-scoped `allow_overlap(vane↔housing, pivot_pin↔housing_shell)` / `allow_overlap(vane↔housing, vane_shaft↔housing_shell)`（vertical）/ `allow_overlap(door↔housing, door_panel/door_pivot_pin↔housing_shell)`（outlet_door）/ `allow_overlap(panel↔housing, hinge_knuckle↔housing_shell)`；`expect_overlap(panel, housing, axes="xz")` 关时盖前脸；`expect_contact` 迁移各样本
- grandfather：pin/shaft/knuckle/齐平门 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- targeted `ctx.pose(...)`：airflow blade/vane/deflector/door 开合决定性检查（blade z-extent/depth 变、vertical vane X-extent 变、door 下翻 min-z 降）+ service_panel 开露 filter + clamshell 独立性 + 闭合姿态不挡出风（迁移各样本 run_tests）

## Reject cases

- 用立式圆/柱身占位体当室内机，或丢掉背贴墙 y=0 / 坐地 z=0 / 水平 0.9m 壳体 → 失类别身份；室内机必须是壁挂水平白壳 + 下前脸出风 + 检修盖 + 暗 plenum。
- airflow / service_panel joint origin 放在 housing 任意点而非下前脸弧/面点 / 检修盖凹座沿真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 把 vane_count 暴露给非 three_independent airflow（给 deflector/vertical_bank/outlet_door 也复制横导风叶），或 vane_count 计入结构 distinct → gating / multiplicity 契约违规。
- 出风叶 / 偏导板 / 竖叶 / 出风门 / 检修盖 rest pose 设成张开而非 q=0 闭合（贴表面 / 齐平 / 盖前脸）→ current-pose 与 viewer 目检不符。
- 关节轴错：vertical_vane_bank 用 +X 而非 +Z 竖轴、closing_outlet_door / drop_front 用 +X 而非 −X 下/底铰 → 轴检查 FAIL、开合方向反。
- closing_outlet_door 全开撞地/穿墙，或 bottom_hinge_drop_front 检修盖闭合姿态挡住下前脸出风口 → 出风门不撞地 / 检修盖不挡出风 inequality FAIL。
- body_form 换剖面时未同步 louver/panel 落点与面法向（origin/rpy 不随 mesh 更新）→ 出风叶悬空/穿壳、检修盖错位。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；scale 归 ⑤）。

## 与相邻类别的边界

- 不该混入：**空气净化器 / 塔扇 / 落地箱扇**——理由：立式圆柱/塔身或方箱落地机身，进出风为整柱格栅或顶排风，无壁挂水平壳体、无墙面贴合 y=0、无 cross-flow plenum + 检修盖 louver 送风语义；本类是横长壁挂白壳室内机。
- 不该混入：**排气扇 / 换气口 / 通风格栅**——理由：薄墙嵌入式格栅框 + 单轴流小风扇，无独立机身壳体 / 滤网腔 / 出风导向叶机构；本类有完整 0.9m 壳体 + 可动导风机构 + 检修盖。
- 不该混入：**分体式空调室外机（Facade / AC outdoor unit）**——理由：室外机是朝外散热的方箱（大轴流风扇栅 + 压缩机 + 冷凝盘管 + 支架），非室内送风白壳、无检修盖 louver / 横导风叶 / 暗 plenum 送风口；本类是**室内机**（indoor unit）。
- 不该混入：**通用暖气片 / 电暖器 / 除湿机**——理由：它们是散热片阵列或独立立式家电，无水平壁挂壳体 + 可动出风导向机构 + 检修滤网盖的组合语义。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT（REDO：旧 spec 已删，上游 seed/10 变体/source map 仍在并已同步）。读全 11 样本（1 parent + 10 变体）全文，均 forked_anchor，每 candidate 带真实 `model.py:Lx-Ly`。3 登记 slot：body_form(4, ③ Primary Form Family：rounded/boxy/wedge/bullnose，Planar/Volumetric 混) × airflow_mechanism(4 主机构：3-slim-vanes/deflector/vertical-bank/outlet-door，跨 +X/+Z/−X 三轴向) × service_panel(3：top-lift/clamshell/drop-front，跨 +X/−X)= **48**；叠 vane_count N[2,6] multiplicity（**gated to three_independent_slim_vanes**）后展开 ≈ 60-96 realized topology。§8.5 六轴：①有(含 gated multiplicity)、②有(REVOLUTE 三轴向)、③有(body_form 登记 slot)、④无(无可换装饰 style + 理由)、⑤有(3 主 scale + 关节行程 + 运动包络/motion_test_plan)、⑥有(6 配色, painted-plastic + metal 两大类)。palette_style 6 套写实配色(glossy_white_classic/warm_cream/graphite_dark/champagne_gold/matte_silver/sky_soft_blue)，解析 mats[shell/panel/cavity/filter_frame/filter_mesh]，锚 5★ RGBA，palette-only 不计 slot_choice。已编 compatibility gate：vane_count↔three_independent、body_form 落点求解器送两机构、检修盖 hinge origin 随 body_form 顶前沿派生、closing_outlet_door × bottom_hinge_drop_front 低区 clearance 用两条 inequality 分区(回缩仍冲突则 fallback top_hinge_lift)。**未写任何模板代码**。待人工审核。开放问题见下。|
| open questions | (1) vane_count 上界 6 是否合理（现实室内机横导风叶多为 1-4 大叶；若审核偏好可收 [2,5]）。(2) closing_outlet_door × bottom_hinge_drop_front 是否直接硬 gate-out（更保守）而非 inequality 分区 + fallback（现方案更全组合但 resolve 更复杂）。(3) 是否需要第 4 个 service_panel candidate（样本池仅 3，达下限；如需 3-6 目标更足可补 world_knowledge_extrapolation，但 §4 硬约束允许 3）。|

## 模板实现备注（可选）

- 共享 helper：`_housing_shape_for(body_form, cfg)` 分派四种侧剖面 + 统一 boolean（进风框 / filter pocket / plenum / outlet/louver cut）；`_front_face_point(body_form, param)` 返回 `(y, z, normal_angle)` 供 airflow / service_panel 消费；`_add_louver_vane(model, housing, i, theta, cfg)`（沿 vane-count-5 蓝本 L178-216）；airflow 各一个 factory（`_make_slim_vanes` / `_make_deflector` / `_make_vertical_bank` / `_make_outlet_door`），service_panel 各一个（`_make_top_lift` / `_make_clamshell` / `_make_drop_front`）。
- body_form 落点适配：rounded/bullnose 用 `_arc_point(theta)`+法向 `theta−π/2`；boxy 用平前面直落 `(BODY_D, z)`+法向 0；wedge 用 `_face_point(fraction)`+常量 `FACE_NORMAL_ANGLE`。airflow/panel joint 的 `rpy` 统一从该法向角取。
- vane_count gating：`resolve_config` 内 `if airflow != "three_independent_slim_vanes": vane_count = None`（不进 slot_choices、不复制）。vertical_vane_bank 的 12 竖叶是 candidate 内部 `N_VERTICAL_VANES` 常量，非 multiplicity 轴。
- captured-fit overlap：`run_air_conditioner_tests` 里迁移各样本 `ctx.allow_overlap` + `ctx.expect_contact`（pivot_pin↔housing_shell / vane_shaft↔housing_shell / door_panel↔housing_shell / hinge_knuckle↔housing_shell）+ `expect_overlap(panel, housing, axes="xz")` 关盖 + 各 targeted `ctx.pose` 开合决定性检查（blade tilt / vertical sweep / door 下翻 / panel 开露 filter / clamshell 独立）。
- 参考模板：`container_locker.py`（mixed pattern + 主机构 slot + multiplicity + palette_style + config_from_seed/resolve_config clamp + slot_choices + run_tests allow_overlap 骨架，slot graph / gating 结构与本 AC 高度同构）；`binocular.py`（gated multiplicity + 直接 build 风格）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root/A/B/C/mult | housing(共享) + body_form=rounded_bottom_curve + airflow=three_independent_slim_vanes + service_panel=top_hinge_lift + vane_count=3 | rec_model-a-...-e9cc92a3（P1）| `_arc_point` L86-88 / `_housing_shape` L91-144 / housing visuals L178-205 / `front_panel_hinge` L223-236 / `{label}_louver_pivot` L258-272 | root housing 共享件 + 圆角剖面基线 + 横导风叶基线 + 顶掀盖基线 + vane_count 基线 |
| S2 | A | boxy_rectangular | rec_variant-body-form-boxy-rectangular-..._6caa9319 | `_housing_shape` L89-153 / louver origin 平前面 L275-285 | 方角箱体平前脸侧剖面 |
| S3 | A | raked_wedge | rec_variant-body-form-raked-wedge-..._072b1710 | `_face_point` L56-61 / `FACE_NORMAL_ANGLE` L53 / `_housing_shape` L112-193 / origin rpy L280-283,L319-322 | 强前倾楔形侧剖面 + 斜面法向落点 |
| S4 | A | full_bullnose_capsule | rec_variant-body-form-full-bullnose-capsule-..._4b99b445 | `_arc_point` L94-97 / `_top_arc_point` L100-107 / `_housing_shape` L110-177 | 上下双圆角胶囊侧剖面 |
| S5 | B | single_wide_deflector | rec_variant-airflow-mechanism-single-wide-deflector-..._4f557258 | `_deflector_shape` L173-191 / `deflector_pivot` REVOLUTE +X L282-302 / outlet cut L139-149 | 单片全宽偏导板 −10°..60° |
| S6 | B | vertical_vane_bank | rec_variant-airflow-mechanism-vertical-vane-bank-..._148eace8 | `_vane_center_x` L96-99 / `_vertical_vane_blade_shape` L102-109 / `vane_pivot_{i}` REVOLUTE +Z L278-292 | ~12 竖导风叶绕 +Z 竖轴左右扫 |
| S7 | B | closing_outlet_door | rec_variant-airflow-mechanism-closing-outlet-door-..._97104f78 | `_outlet_opening_cut` L91-121 / `_outlet_door_shape` L194-248 / `outlet_door_hinge` REVOLUTE −X L339-353 | 整面出风门下沿铰 0..75° 下翻 |
| S8 | C | two_leaf_clamshell | rec_variant-service-panel-two-leaf-clamshell-..._3fe5a919 | `NUM_LEAVES`/`LEAF_W`/`LEAF_CX` L62-68 / `panel_{i}_hinge` REVOLUTE +X L237-250 / 独立性 L404-419 | 双叶顶铰独立上掀 |
| S9 | C | bottom_hinge_drop_front | rec_variant-service-panel-bottom-hinge-drop-front-..._fd012151 | `_front_panel_shape`(+Z rise) L148-165 / `front_panel_hinge` REVOLUTE −X L224-237 | 底沿铰前翻检修盖 |
| S10 | mult | vane_count (N=2/5 range 循环 + 共享 factory) | rec_variant-vane-count-2-..._62841830 / rec_variant-vane-count-5-..._ce97feaa | N=2：`VANE_COUNT`/`VANE_THETAS` L67-73 + `for i in range(VANE_COUNT)` L242-276；N=5：`NUM_VANES`/`VANE_THETAS` L67-75 + `_add_louver_vane` L178-216 + `for i in range(NUM_VANES)` L293-294 | multiplicity range(N) 复制契约 + 弧均分 + 共享 factory 蓝本 + uniform joint policy |
