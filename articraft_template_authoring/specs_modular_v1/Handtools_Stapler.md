# stapler (desktop / hand stapler) — Modular Spec

> 来源小类：`picture/Handtools/Stapler`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Stapler.md`。
> **"Stapler" 在此 = 桌面 / 手用订书机（desktop / hand stapler），一只下身弹仓托 + 后铰翻起的上臂磁仓盖驱动器，不是打孔机 hole-punch、也不是文具夹 clip / binder clip。**
> 结构家族 = 后铰翻盖订书机：一只 `base`（root，下身托 / 弹仓 + 前 anvil 压钉板 + 后铰硬件）+ 一只 `top_arm`（磁仓盖 / 手柄臂，含 carrier_rail + driver_blade）通过单 `base_to_arm` REVOLUTE 后铰翻起。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位变体）已同步进本仓库 `data/records/<id>/`，rating=5（同步脚本批量写 rating；本仓库 record.json/workbench.json 的 rating 字段在拷贝中可能未回填，但 source map 标全部 converged + compile success + 1 个非 fixed joint）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对）。引用以 part / joint / helper **名字** 为准（`base`/`top_arm` part；`base_to_arm` joint；`_base_body`/`_base_grip`/`_arm_shell`/`_hinge_knuckles`/`_hinge_pin`/`_rear_housing`/`_torsion_spring_mesh`/`_single_grip_rib`/`_foot_pad`/`_rubber_foot`/`_staple_crown`/`_anvil_plate`/`_carrier_rail`/`_driver_blade` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `stapler` |
| template path | `agent/templates/Handtools_Stapler.py` |
| test path (optional) | `tests/agent/test_stapler_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定共同 root `base` + 固定 child `top_arm`，单 `base_to_arm` REVOLUTE；三个独立结构层 body_type / hinge_mechanism / top_cap 分别决定 base/arm 的 mesh、后铰硬件与盖形）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint base_to_arm、workbench-only，rating=5）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、for-i 复制循环与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本（小类内另有 ~20 个 `desktop_stapler_with_hinged_top_arm_*` 记录，但 source map 只采纳 parent + 7 个命名变体作 module 源，不列入）|

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 8 个样本）**：`base`（root，坐地于 z=0；下身托 / 弹仓 + 前 `anvil_plate`（双 clinch 槽）+ 后铰硬件）+ `top_arm`（child，磁仓盖 hump + `carrier_rail` 弹仓轨 + `driver_blade` 驱动刀 + 后铰下伸结构）。`base_to_arm` REVOLUTE 是**所有候选共享的唯一非 fixed joint**：`origin=(HINGE_X, 0, HINGE_Z)`、`axis=(0,-1,0)`、`lower=0`（闭合）/ `upper≈0.52-0.55`（开），正 q 抬升 driver_blade 开订书机（parent L300-308 / compact L312-322）。arm 在子帧中以 pivot 为局部原点、盖沿 +X 延伸。
- **Slot A body_type 轴**：是 base mesh + 锚高 + 内置复制件的变化（part 树仍 `base`/`top_arm`，joint 拓扑不变；plier 例外见下）。
  - half_strip_tray（parent）：`_base_body` 后跟 lofted XZ 侧 profile（rear heel + 低 deck + 圆 toe）、`_base_heel_pads` 单块脚（parent L84-124），TOTAL_LEN=0.158。anvil 坐前 deck（`ANVIL_SEAT_Z=DECK_FRONT_Z+0.0005>0`，parent L67）。
  - compact_stubby：`_base_body` 短 profile（TOTAL_LEN=0.092），blunt toe，`_foot_pad_shape`×2 + `_knuckle_shape`×2 复制循环（compact L81-115, L271-287），wall/length>0.24（compact run_tests L342-351）。
  - full_strip_tray：`_base_body` 长平 deck（TOTAL_LEN=0.280）+ `_tray_liner`（fullstrip L167-181）+ `_rubber_foot`×4（L143-149, L318-355）+ `_staple_crown`×12 复制（弹仓内可见钉条，挂 arm，L306-312, L364-373），run_tests 断言 base_dx≥0.25、rail_dx≥0.20（L422-479）。
  - plier_grip：`_base_grip`（swept 椭圆截面沿 XZ spline path，向下弯到 pivot 下方做手squeeze 握把，L86-130）+ `anvil_platform`（前端平台 union 进 grip，L120-125）+ `_grip_texture_ridges`×5（沿 path 的 ergonomic 凸点，L133-173, L334-341）。**anvil 座面下移**：`ANVIL_SEAT_Z=-0.008+0.006+0.0005`（坐 anvil_platform 顶，负 Z 区，plier L69）；run_tests 断言 anvil_min_z∈(-0.012,0.005)、grip_min_z<HINGE_Z-0.020（L455-487）。
- **Slot B hinge_mechanism 轴**：是后铰硬件 part 数 / mesh 与 arm 后端下伸结构的变化（跨 base + arm，**boxed 改变 arm rear 几何**）。
  - exposed_knuckle_pin（parent）：base `_hinge_knuckles`（双 bored ring + skirt，axis +Y，parent L209-227）+ arm `_hinge_pin`（横销，parent L230-239）+ arm_shell 后两 `cheek`（内侧下伸夹在 knuckle 之间，parent L186-205）。captured-pin 过盈 `allow_overlap(pin↔knuckles, arm_shell↔knuckles)`（parent L424-437）。
  - boxed_housing：base `_rear_housing`（U-channel 高箱壳，HOUSING_W=0.046 宽于 arm 让 arm 跨骑，HOUSING_H=0.042，boxed L140-176）+ arm_shell 后**单中央 tongue**（替换双 cheek，tongue_w=0.020，boxed L227-248）。**删除 `_hinge_knuckles` 与 `_hinge_pin`**（run_tests 显式断言无 hinge_knuckles / hinge_pin，boxed L412-429）。`allow_overlap(arm_shell↔rear_housing)`（boxed L521-530）。pivot 仍 (HINGE_X,0,HINGE_Z)。
  - torsion_spring：base `_hinge_knuckles` + arm `_hinge_pin`（同 parent）**外加** base `_torsion_spring_mesh`（`tube_from_spline_points` helix，base tang + N=4 圈线圈 + arm tang，绕 pivot 轴 +Y，spring L245-294）。arm tang 故意接触 arm_shell rear cheek 提供回位力（`allow_overlap(spring↔arm_shell)` + `expect_contact`，spring L519-534）。run_tests 断言 spring 中心近 pivot、Y 跨在 knuckle 内、Z 跨>0.005（spring L419-543）。
- **Slot C top_cap 轴**：是 arm_shell mesh-profile 的变化（part / joint 拓扑不变），ribbed 额外带 module-local 复制循环。
  - rounded_hump（parent）：`_arm_shell` 曲线 XZ 侧 silhouette（crown fillet 0.010 / nose / hollow / 后 cheek，parent L142-206），软 pebble dome。
  - slab_cap：`_arm_shell` 近矩形 profile + `|X and >Z` chamfer（slabcap L146-212，ARM_SIDE_CHAMFER/ARM_CORNER_CHAMFER），平顶矩形板 + 棱倒角；run_tests 断言 slab_dx≥0.80·ARM_LEN、slab_dy≈WIDTH、slab_dz>0.024、crown≈HINGE_Z+ARM_MAX_H（slabcap L366-403）。
  - ribbed_cap：`_arm_shell`（同 rounded hump）+ `_single_grip_rib`×5（`for i in range(GRIP_RIB_COUNT=5)` 横向 finger-grip 凸脊等距沿 crown，共享 helper，ribbedcap L269-333）；run_tests 断言每 rib 凸出 crown 之上、等距（ribbedcap L462-496）。

## 核心身份

一只**桌面 / 手用订书机**（desktop / hand stapler）：一只坐地 `base`（炭灰塑料下身托 / 弹仓，前端有亮金属 `anvil_plate` 压钉板带两条 clinch 槽用于折弯钉脚，后端有铰链硬件），一只 `top_arm`（磁仓盖 / 手柄臂大圆 hump，内有金属 `carrier_rail` 弹仓推钉轨 + `driver_blade` 前端驱动刀 + 后端下伸到 pivot 的铰接结构），二者用单 `base_to_arm` REVOLUTE 后铰相连：`lower=0` 闭合（盖盖在托上、driver 悬于 anvil 上方），正 q≈0.52 抬升盖前端 driver 开订书机（装钉 / 复位）。默认成熟域：body_type(4) × hinge_mechanism(3, 受兼容矩阵剪枝) × top_cap(3) 的小型订书机，整机长 ~0.09-0.28 m（compact ~0.092 / half-strip ~0.158 / full-strip ~0.280 / plier ~0.158 但下身下弯成握把）。活动语义 = **上臂绕后铰翻起 / 压下**（单 REVOLUTE，全候选共享，无第二非 fixed joint）。

不该混入：
- **打孔机 / 钻孔器（hole punch）**——虽同为后铰压下台面工具，但 hole punch 是冲头穿纸 + 圆 confetti 接屑盒，无 anvil clinch 槽 / 无弹仓推钉轨 / 无 staple 钉条；身份不同（如需可作单独 slug）。
- **文具夹 / 长尾夹 / binder clip（clip）**——弹簧 / 杠杆张力夹纸，无后铰翻盖弹仓、无 anvil、无 driver；已有独立 slug `clip`（主运动 spine 不同）。
- **去钉器 / 起钉器（staple remover）**——双爪夹钳起钉，无弹仓 / anvil / driver，主运动是双爪绕 pivot 对咬。
- **重型 / 电动订书机以外的台式手用机**——本类是单铰手压机，不含电机 / 长行程驱动滑块（若需可作单独 slug）。

## 槽位 + 候选模块表

> **建模注记**：三个 slot 都挂在固定的 `base`(root) + `top_arm`(child) 上，共享同一 `base_to_arm` REVOLUTE（part 树 / joint 数对全部组合恒定 = 2 part + 1 joint）。`top_cap`（Slot C）是 `top_arm` 同一 `arm_shell` 的 mesh-profile 维度（圆 hump / 平板 / 带脊），不改 part/joint 拓扑。`body_type`（Slot A）是 `base` mesh + 内部复制件 + anvil 锚高维度（plier 把 anvil 座面下移、且把 base 实体换成握把扫掠，但仍是单 `base` part）。`hinge_mechanism`（Slot B）才是真正改**后铰硬件 part 集合 + arm rear 下伸几何**的轴（exposed=knuckles+pin+双 cheek / boxed=housing+中央 tongue 且删 knuckles/pin / spring=knuckles+pin+coil+双 cheek）；三轴的笛卡尔积（经兼容矩阵剪枝）共同撑开多样性（见 §9）。所有 slot 的差异都进 `slot_choices_for_seed` 的 tuple。

### Slot A：body_type（下身 / 弹仓托足迹 —— `base` root 几何 + anvil 座高 + 内部复制件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| half_strip_tray（基线）| rec_build-...-stap_..._3c83c7d2（parent）| `_base_body` lofted XZ profile L84-113 / `_base_heel_pads` L116-124 / `_anvil_plate` L127-139 / base 装配 L281-285 | eligible if compatible | 经典半条桌面托（TOTAL_LEN=0.158）：rear heel + 低 deck + 圆 toe；单块后脚；anvil 坐前 deck（`ANVIL_SEAT_Z>0`，L67）|
| compact_stubby | rec_stapler_var_compactbody | `_base_body` 短 profile L121-140 / `_foot_pad_shape` L81-87 + `for i` ×2 L271-278 / `_knuckle_shape` L90-115 + `for i` ×2 L280-287 | eligible if compatible | 迷你机（TOTAL_LEN=0.092）：blunt 圆 toe、tall wall/length>0.24；2 脚 + 2 knuckle 复制循环；anvil 座前 deck |
| full_strip_tray | rec_stapler_var_fullstrip | `_base_body` 长平 deck L111-140 / `_tray_liner` L167-181 / `_rubber_foot` L143-149 + `for i` ×4 L318-355 / `_staple_crown` L306-312 + `for i` ×12 L364-373 | eligible if compatible | 全条办公托（TOTAL_LEN=0.280）：长平 deck + 金属 tray_liner 弹仓槽 + 4 脚复制 + 弹仓内 12 钉条复制（钉条挂 arm）；anvil 座前 deck |
| plier_grip | rec_stapler_var_plierbody | `_base_grip` 椭圆截面 sweep 沿 XZ spline L86-130 / `anvil_platform` union L120-125 / `_grip_texture_ridges` ×5 L133-173, L334-341 | eligible if compatible | 手squeeze 握把（替换平托）：下身向下弯到 pivot 下方成握把；前端 `anvil_platform` 平台承 anvil（**`ANVIL_SEAT_Z` 下移到负 Z**，L69）；5 凸脊沿握把；run_tests 断言 grip_min_z<HINGE_Z-0.020（L483-487）|

### Slot B：hinge_mechanism（后铰机构 —— base 后铰硬件 + arm 后端下伸结构，跨 base/arm）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|
| exposed_knuckle_pin（基线）| rec_build-...-stap_..._3c83c7d2（parent）| base `_hinge_knuckles` L209-227 / arm `_hinge_pin` L230-239 / arm_shell 双 `cheek` L186-205 / allow_overlap L424-437 | eligible if compatible | 暴露 interleaved 双 knuckle ring（base，bored + skirt，axis +Y）+ 横销 `hinge_pin`（arm）+ arm_shell 后两内侧 cheek 交错；captured-pin 过盈（pin↔knuckles、arm_shell↔knuckles allow_overlap）|
| boxed_housing | rec_stapler_var_boxedhinge | base `_rear_housing` U-channel L140-176 / arm_shell 中央 `tongue` L227-248 / 断言无 knuckles/pin L412-429 / allow_overlap L521-530 | eligible if compatible | 高箱塑壳 `rear_housing`（base，宽于 arm 让 arm 跨骑，藏 pivot）+ arm_shell 后**单中央 tongue** 下伸进腔（替换双 cheek）；**删除 `hinge_knuckles` 与 `hinge_pin`**；arm tongue 在腔内 pivot（`allow_overlap(arm_shell↔rear_housing)`）|
| torsion_spring | rec_stapler_var_springhinge | base `_hinge_knuckles` L212-230 + arm `_hinge_pin` L233-242 + base `_torsion_spring_mesh` L245-294 / allow_overlap L505-527 | eligible if compatible（**仅兼容暴露 knuckle/cheek 几何，与 boxed_housing 互斥**，见 §9）| 同 exposed 的暴露 knuckle + pin + arm cheek，**外加** `torsion_spring`（base，`tube_from_spline_points` helix：base tang + 4 圈线圈绕 pivot 轴 +Y + arm tang）；arm tang 故意接触 arm_shell cheek 做回位力（`allow_overlap(spring↔arm_shell)` + `expect_contact`）|

### Slot C：top_cap（上臂盖形 —— `top_arm` 的 `arm_shell` mesh-profile，不改拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_hump（基线）| rec_build-...-stap_..._3c83c7d2（parent）| `_arm_shell` 曲线 XZ silhouette + crown/nose fillet + hollow + 后 cheek L142-206 | eligible if compatible | 软 pebble / dome 磁仓盖（crown fillet 0.010、nose 圆、underside 挖空）|
| slab_cap | rec_stapler_var_slabcap | `_arm_shell` 近矩形 profile + `|X and >Z` chamfer L146-212（ARM_SIDE_CHAMFER/ARM_CORNER_CHAMFER L54-55）| eligible if compatible | 平顶矩形板盖 + 侧棱 chamfer；run_tests 断言 slab_dx≥0.80·ARM_LEN、slab_dz>0.024、crown≈HINGE_Z+ARM_MAX_H（L366-403）|
| ribbed_cap | rec_stapler_var_ribbedcap | `_arm_shell`（同 hump）L142-206 + `_single_grip_rib` L280-292 + `for i in range(5)` L325-333 | eligible if compatible | 圆 hump crown 携 5 条等距横向 molded finger-grip 脊（module-local 复制，共享 helper）；ribs 随 arm（Rule 1 visual，无独立 joint）|

## 槽位图（slot graph）

pattern: parallel_children（固定 root `base` + 固定 child `top_arm`；三个独立结构层 body_type / hinge_mechanism / top_cap 分别决定 base mesh+anvil 座高 / 后铰硬件+arm rear / arm_shell 盖形；三者共享同一 `base_to_arm` REVOLUTE）

```
base (root, 坐地于 z=0; 由 body_type 决定下身托/握把 mesh + anvil_plate 座高 + 内部复制件; 由 hinge_mechanism 决定后铰 base 侧硬件)
  │   visual(共享): base_body/base_grip, anvil_plate (前, 双 clinch 槽), [body 内部复制: feet/liner/grip ridges], [hinge base 硬件: hinge_knuckles | rear_housing | knuckles+torsion_spring]
  │
  └── top_arm ──[base_to_arm: REVOLUTE axis=(0,-1,0), origin=(HINGE_X,0,HINGE_Z), lower=0/upper≈0.52, 正 q 抬 driver 开]   ← 全候选共享唯一非 fixed joint
        visual(共享): arm_shell (由 top_cap 决定 hump | slab | ribbed), carrier_rail, driver_blade
        + [hinge arm 侧下伸: 双 cheek (exposed/spring) | 中央 tongue (boxed)]
        + [hinge arm 硬件: hinge_pin (exposed/spring) | 无 (boxed)]
        + [cap 内部复制: grip_rib_{i}×5 (ribbed)]
        + [body 内部复制: staple_{i}×12 挂 arm (full_strip)]
```

接口点位与 joint 语义：
- **base → top_arm（全候选共享）**：mating = 后铰线。REVOLUTE axis=(0,-1,0)，origin=(HINGE_X, 0, HINGE_Z)（HINGE_X 近后端、HINGE_Z 在 rear heel / housing 之上，parent L55-56 / L305）；arm 子帧以 pivot 为局部原点、盖沿 +X 延伸；q=0 闭合（盖盖托、driver 悬 anvil 上方）/ q≈0.52 开（driver 上抬>0.03，parent run_tests L410-419）。
- **hinge_mechanism 接口（互斥三选一，跨 base/arm）**：
  - exposed_knuckle_pin：base 双 `hinge_knuckles`（外缘）↔ arm `hinge_pin`（横销）captured-pin；arm_shell 双 cheek（内侧）交错在 knuckle 之间。`fail_if_articulation_origin_far_from_geometry` 守 origin 落 knuckle 环心；`allow_overlap(hinge_pin↔hinge_knuckles, arm_shell↔hinge_knuckles)`（parent L424-437）。
  - boxed_housing：base `rear_housing` U-channel（宽于 arm）↔ arm_shell 中央 tongue 下伸进腔；**无 knuckles/pin**（arm tongue 在腔内 pivot）。`allow_overlap(arm_shell↔rear_housing)` + `expect_overlap(arm_shell↔rear_housing, axes=xz)`（boxed L495-530）。origin 仍 (HINGE_X,0,HINGE_Z)（落 housing 腔内）。
  - torsion_spring：同 exposed 的 knuckle+pin+cheek，**外加** `torsion_spring`（base，绕 pivot 轴 +Y 的 helix，base tang 下伸 / arm tang 前伸接触 arm cheek）。`allow_overlap(spring↔arm_shell)` + `expect_contact(spring↔arm_shell)`（spring L519-534）。spring 中心 ≈ pivot、Y 跨在 knuckle 内（spring run_tests L419-439）。
- **body_type → anvil/blade 接口（关键，body slot 决定 anvil 座面）**：anvil_plate 是 base visual，`driver_blade` 是 arm visual；闭合时 driver 悬于 anvil 正上方（`blade_min_z ≥ anvil_max_z − tol` 且 X 对位，全样本 run_tests）。**anvil 座高 `ANVIL_SEAT_Z` 由 body_type 决定**：tray 候选（half/compact/full）`ANVIL_SEAT_Z = DECK_FRONT_Z + 0.0005 > 0`（坐前 deck）；plier_grip `ANVIL_SEAT_Z < 0`（坐 anvil_platform，前端平台在 pivot 下方，plier L69）。driver_blade 在 arm 子帧的 Z 偏置（nose）随之微调，使闭合时仍 register 在 anvil 上方。
- **top_cap 接口**：top_cap 只换 arm_shell mesh-profile；carrier_rail / driver_blade / 后铰下伸结构不受影响（cap 与 hinge 正交：任意 cap 都要保留供 hinge 接入的后端下伸——hump/slab/ribbed 的 arm_shell 都含后 cheek（exposed/spring）或可改中央 tongue（boxed），见 §9 兼容）。
- **mating policy**：所有铰接接口（pin-in-knuckle captured、tongue-in-housing captured、spring-tang-on-cheek contact）是 captured-fit / 接触，**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured/contact overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：base_to_arm q=0（盖闭合、driver 悬 anvil 上方）；全部样本 lower=0 即闭合姿态。
- **互斥 / 可选 / 派生**：hinge_mechanism 三候选互斥（一次只一种后铰）；**torsion_spring 与 boxed_housing 互斥**（spring 依赖暴露 knuckle/cheek，boxed 删了它们、改中央 tongue → spring 无可接触的 cheek，见 §9）。body_type 与 top_cap 正交于 hinge（任意 body × 任意 cap），但 body=plier 重设 anvil 座高（派生）、hinge=boxed 时 arm rear 改中央 tongue（cap 的后端下伸由 hinge 决定，cap mesh 仍按所选 profile）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_type — half_strip_tray（以 parent 为例；compact/full 仅换尺寸 + 复制件，plier 换实体）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`base_body` + `base_feet`/`foot_*` + `anvil_plate` 为 `base`(root) visual）| parent `_base_body` L84-113 / `_base_heel_pads` L116-124 / `_anvil_plate` L127-139 / 装配 L281-285 |
| internal joints | 无（base 是 root）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | 后铰区（供 hinge_mechanism base 硬件 + arm 接入）+ 前 anvil 座面（`ANVIL_SEAT_Z`，供 driver register）| parent L55-56, L67 |

### Slot A / body_type — full_strip_tray（含两条复制：feet ×4 + staple ×12）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`base_body` 长平 deck + `tray_liner` + `foot_{i}`×4 为 base visual；`staple_{i}`×12 为 **arm** visual，弹仓内可见钉条）| fullstrip `_base_body` L111-140 / `_tray_liner` L167-181 / `foot_{i}` L348-355 / `staple_{i}` L364-373 |
| internal joints | 无（feet/staples 非移动件，Rule 1）| — |
| upstream interface | root；钉条挂 arm 随盖动 | fullstrip L364-373 |
| downstream interface | 后铰区 + 前 anvil 座面（同 tray 基线）| fullstrip L61-73 |

### Slot A / body_type — plier_grip（anvil 座面下移）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`base_grip` 扫掠握把 + `anvil_platform` union + `grip_ridge_{i}`×5 + `anvil_plate` 为 base visual）| plier `_base_grip` L86-130 / `_grip_texture_ridges` L133-173 / 装配 L330-344 |
| internal joints | 无（握把脊非移动件，Rule 1）| — |
| upstream interface | root（握把下弯到 pivot 下方）| plier L96-104 |
| downstream interface | 后铰区 + 前 `anvil_platform` 平台（`ANVIL_SEAT_Z<0`，anvil 座面下移，driver_blade Z 偏置随之重算）| plier L69, L120-125 |

### Slot B / hinge_mechanism — exposed_knuckle_pin
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（base `hinge_knuckles` + arm `hinge_pin` + arm_shell 双 cheek 为各自宿主 visual）| parent `_hinge_knuckles` L209-227 / `_hinge_pin` L230-239 / cheek L186-205 |
| internal joints | 无额外 joint（共享 base_to_arm）| — |
| upstream interface | base 双 knuckle ring（外缘，bored + skirt 到 heel）| parent L209-227 |
| downstream interface | arm hinge_pin 横销 + arm_shell 双 cheek 交错入 knuckle（captured-pin，`allow_overlap` pin↔knuckles / arm_shell↔knuckles）| parent L424-437 |

### Slot B / hinge_mechanism — boxed_housing
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（base `rear_housing` U-channel + arm_shell 中央 tongue 为各自宿主 visual）；**删除 `hinge_knuckles` 与 `hinge_pin`** | boxed `_rear_housing` L140-176 / arm tongue L227-248 |
| internal joints | 无额外 joint（共享 base_to_arm）| — |
| upstream interface | base `rear_housing`（宽于 arm 让 arm 跨骑，腔藏 pivot；箱顶高于 pivot、箱底到 base 脚）| boxed L140-176, L431-457 |
| downstream interface | arm_shell 中央 tongue 下伸进腔 pivot（`allow_overlap(arm_shell↔rear_housing)` + `expect_overlap` axes=xz）| boxed L495-530 |

### Slot B / hinge_mechanism — torsion_spring（与 boxed_housing 互斥）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（base `hinge_knuckles` + arm `hinge_pin` + arm cheek + base `torsion_spring` 为各自宿主 visual）| spring `_hinge_knuckles` L212-230 / `_hinge_pin` L233-242 / `_torsion_spring_mesh` L281-294 |
| internal joints | 无额外 joint（共享 base_to_arm；spring 是装饰 / 回位 visual，非活动件）| — |
| upstream interface | base 双 knuckle（同 exposed）+ `torsion_spring` helix 绕 pivot 轴 +Y（base tang 下伸 / 4 圈线圈，中心≈pivot、Y 跨在 knuckle 内）| spring L245-294, L419-439 |
| downstream interface | arm hinge_pin + arm cheek（同 exposed）+ spring arm tang 前伸接触 arm_shell cheek（`allow_overlap(spring↔arm_shell)` + `expect_contact`）| spring L519-534 |

### Slot C / top_cap — rounded_hump / slab_cap / ribbed_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`arm_shell` 为 `top_arm` visual；ribbed 额外 `grip_rib_{i}`×5 为 arm visual）| parent `_arm_shell` L142-206 / slab L146-212 / ribbed `_single_grip_rib` L280-292 + L325-333 |
| internal joints | 无（cap / ribs 随 arm 动，Rule 1）| — |
| upstream interface | arm_shell 后端下伸结构（双 cheek 或中央 tongue，由 hinge 决定）接入后铰 | parent L186-205 / boxed L227-248 |
| downstream interface | 盖上表面（hump dome / slab 平顶 / ribbed 脊纹）；内挖空容 carrier_rail | parent L169-185 |

### body 内部复制 / cap 内部复制（module-local，non-moving visual）
| emits | 描述 | 来源 |
|---|---|---|
| feet（compact ×2 / full ×4）| `foot_pad_{i}` / `foot_{i}`，共享 helper `_foot_pad_shape` / `_rubber_foot`，绝对式对称/等距 placement，FIXED 随 base | compact L271-278 / fullstrip L318-355 |
| knuckles 复制（compact ×2）| `hinge_knuckle_{i}`，共享 `_knuckle_shape`，对称 Y 置（exposed hinge 的复制式发射）| compact L280-287 |
| staples（full ×12）| `staple_{i}`，共享 `_staple_crown`，沿 X 等距，挂 arm（弹仓内钉条）| fullstrip L364-373 |
| grip ridges（plier ×5）| `grip_ridge_{i}`，沿握把 path | plier L334-341 |
| grip ribs（ribbed cap ×5）| `grip_rib_{i}`，共享 `_single_grip_rib`，沿 crown 等距 | ribbed L325-333 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_type | enum | half_strip_tray / compact_stubby / full_strip_tray / plier_grip | half_strip_tray | choice | 由 deterministic procedural sampler 选；决定 base mesh + anvil 座高 + 内部复制件 | Slot A 表 |
| hinge_mechanism | enum | exposed_knuckle_pin / boxed_housing / torsion_spring | exposed_knuckle_pin | choice | sampler 选；互斥；**torsion_spring 与 boxed_housing 互斥**（兼容矩阵剪枝，见 §9）| Slot B 表 |
| top_cap | enum | rounded_hump / slab_cap / ribbed_cap | rounded_hump | choice | sampler 选；只换 arm_shell mesh-profile | Slot C 表 |
| palette_style | enum | charcoal_steel / black_red / black_blue / chrome_arm / pastel_office / industrial_zinc | charcoal_steel | palette | palette only，**不计入 slot_choice**；每 seed 采一套（材质 / 色，见下表）| 各样本材质 |
| body_len_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 base TOTAL_LEN/BASE_LEN + ARM_LEN（保盖覆盖托），clamp | parent L37/L43/L50 |
| body_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 WIDTH（base + arm + 铰宽），clamp | parent L38 |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 deck / heel / HINGE_Z（联动 anvil 座高、arm bottom 间隙），clamp | parent L44-58 |
| cap_crown_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 ARM_MAX_H（盖 crown 高），clamp（保盖顶高于 base 顶 + margin）| parent L51 |
| open_angle_scale | float | [0.80, 1.10] | 1.0 | independent | 缩放 base_to_arm `motion_limits.upper`（≤π·0.40 安全开角），clamp | parent L307 |
| feet_count (N_feet) | int | {0, 2, 4} | 随 body（half=隐含 1 块/2 / compact=2 / full=4） | conditional→module-local | feet 数随 body_type 派生（**非顶层可变轴**，见 §8），编 module 内部 | compact L272 / fullstrip L318-323 |
| rib_count (N_rib) | int | 声明域 [3, 8]；sweep 采样域 [3, 8]（偏小加权：5 标称、3/4/6 常见、7/8 长尾）| 5 | conditional@ribbed→slot_choice | **仅 top_cap=ribbed_cap 有效**；编入 slot_choice 为 `r{N}`（见 §8/§9）| ribbed L270, L325 |
| staple_count (N_staple) | int | 声明域 [0, 24]；sweep 采样域 [0, 24]（偏小：0/8/12 常见、24 长尾）| 12（full）/ 0（其余 body）| conditional@full_strip→module-local | **仅 body_type=full_strip_tray 有效**；弹仓内钉条数（module-local visual，**非顶层 slot 维度**，见 §8）| fullstrip L91, L366 |
| (—) | constraint | — | — | conditional | **anvil 座高随 body_type**：plier_grip → `ANVIL_SEAT_Z<0`（坐 anvil_platform）；tray 候选 → `ANVIL_SEAT_Z=DECK_FRONT_Z+0.0005>0`；driver_blade nose Z 偏置随之重算保闭合 register | plier L69 / parent L67 |
| (—) | constraint | — | — | conditional | **arm rear 下伸结构随 hinge**：exposed/spring → 双 cheek；boxed → 中央 tongue（cap mesh 不变，只换后端下伸）| boxed L227-248 / parent L186-205 |
| (—) | constraint | — | — | inequality | 闭合盖覆盖托足迹：closed arm_shell 与 base XY 重叠 ≥0.02（compact 窄机）/ ≥0.03（其余）；违反则按比例缩 ARM_LEN 或抬 body_len_scale | 全样本 expect_overlap |
| (—) | constraint | — | — | inequality | 闭合盖顶高于 base 顶：`arm_shell_top > base_top + (0.020 compact / 0.025 其余)`；违反抬 cap_crown_scale / HINGE_Z | 全样本 run_tests |
| (—) | constraint | — | — | inequality | 开角抬升 driver：`upper·open_angle_scale` 使 open driver_min_z > closed + (0.020 compact / 0.03 其余)；保 upper≤π·0.40 | parent L413-419 |
| (—) | constraint | — | — | inequality | rib 排布不超 crown：`N_rib` 沿 `[GRIP_RIB_X_START, GRIP_RIB_X_END]` 等距，`rib_span/(N_rib-1) ≥ GRIP_RIB_THICK+gap`；违反缩 rib_count 或扩 crown 平台 | ribbed L274-276, L324-327 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**；charcoal 为全样本观察的真实材质，其余为色集外推符合订书机现实配色）：
| palette_style | body | arm cap | anvil/rail/blade | 铰硬件 / spring | 来源样本 |
|---|---|---|---|---|---|
| charcoal_steel（默认）| 炭灰塑料 (0.20,0.21,0.22) | 浅炭灰 (0.235,0.245,0.255) | 亮钢 (0.78,0.79,0.80) | 暗钢 (0.42,0.43,0.45) | parent / 全样本基线 |
| black_red | 黑塑 (0.08,0.08,0.09) | 红盖 (0.80,0.12,0.10) | 亮钢 | 暗钢 | 配色外推（经典办公红）|
| black_blue | 黑塑 | 蓝盖 (0.13,0.32,0.72) | 亮钢 | 暗钢 | 配色外推 |
| chrome_arm | 炭灰塑料 | 镀铬亮臂 (0.82,0.84,0.86) | 亮钢 | 暗钢 | 配色外推（金属臂高端机）|
| pastel_office | 米白塑 (0.92,0.90,0.86) | 薄荷 / 粉盖 (0.62,0.84,0.74) | 亮钢 | 暗钢 | 配色外推（家用彩色机）|
| industrial_zinc | 镀锌灰 (0.72,0.73,0.74) | 镀锌灰 | 钢 | 锌 + spring steel (0.72,0.72,0.68) | fullstrip `COL_ZINC`/`COL_LINER` + spring `COL_SPRING` 外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 body_type / hinge_mechanism / top_cap / N_rib 的拓扑**。

## Multiplicity / Copy Logic

**1 根可变 multiplicity 轴（编入 slot_choice）：`rib_count`（ribbed_cap 的 grip rib 数）**；另有 2 类**随 module 派生的固定 / 半固定复制件**（feet、staples）声明为 module-local，不作顶层可变轴。

**可变轴 — rib_count（仅 top_cap=ribbed_cap）：**
- **count_param**：`rib_count`（模板变量 N_rib / GRIP_RIB_COUNT；arm crown 上等距 finger-grip 脊数）。
- **N_range**：声明产品域 **[3, 8]**（订书机盖脊纹现实范围；source map 建议 [3,8]）。`config_from_seed` 的 sweep 采样域 **[3, 8]**（偏小加权：5 标称高频、3/4/6 常见、7/8 长尾）。仅当 top_cap=ribbed_cap 时解析；其他 cap 无 rib（N_rib 不适用）。
- **sampling domain**：top_cap=ribbed_cap 时 `rng.choices(range(3,9), weights=偏小)`；`resolve_config` 把 N_rib clamp 到 [3,8]。
- **copied object**：单条 grip rib——`grip_rib_{i}`，共享 helper `_single_grip_rib`（rounded `box` + 倒角，ribbed L280-292），N 个 visual 复用同一几何对象。
- **naming**：`grip_rib_{i}`，`for i in range(N_rib)`（ribbed L325 已用此结构，可直接作 copy-logic 源）。
- **placement**：沿 X **绝对式**等距——`rib_x = GRIP_RIB_X_START + (i/(N_rib-1))·(GRIP_RIB_X_END − GRIP_RIB_X_START)`（ribbed L326-327），以 crown 平台区间端点解析，不累加漂移（N-不变前提）。
- **joint policy**：grip rib 是**非移动件**（Rule 1）→ inline 为 arm visual，**不发射独立 joint**；活动关节仅 base_to_arm。
- **source/gating**：copy-logic 源取 ribbed L325-333 的 `for i in range(GRIP_RIB_COUNT)`。仅 top_cap=ribbed_cap 进 slot_choice `("rib_count", f"r{N}")`；其他 cap 不编此 tuple（见 §9）。

**module-local 派生复制件（非顶层可变轴，不进 slot_choice）：**
- **feet（随 body_type 派生）**：half_strip→1 块后脚（`_base_heel_pads`，parent L116-124，固定）；compact→`foot_pad_{i}`×2（compact L271-278）；full_strip→`foot_{i}`×4（fullstrip L318-355）；plier→无脚（握把直接落地）。feet 数由 body module 决定（FIXED 装饰 visual），不暴露为可变 count 轴——clamp 不存在"任意 N 个脚"的真实产品域；copied object 共享 helper、绝对式对称 placement、无独立 joint（Rule 1）。
- **staples（仅 full_strip_tray）**：`staple_{i}`×12（fullstrip L364-373，弹仓内可见钉条，挂 arm）。声明域 [0,24]，但**仅 full_strip body 渲染钉条**（其他 body 弹仓不可见钉条 → N_staple=0）。视为 module-local 装饰 multiplicity（随 full_strip body 派生），可选编 slot_choice 但 source map 标其为局部参数非 slot 维度 → 本 spec 取**不编入顶层 slot_choice**（避免与 body_type 维度重复；钉条数变化不改拓扑等价类），仅作 full_strip 内部连续装饰参数。
- **compact 的 hinge_knuckle 复制**：compact 把 exposed hinge 的双 knuckle 写成 `hinge_knuckle_{i}`×2 循环（compact L280-287），parent 则单块 `_hinge_knuckles` 含左右两环。模板侧应统一为 `for i in range(2)` 共享 `_knuckle_shape` 发射（固定 N=2，随 exposed/spring hinge module，非可变轴）。

## 拓扑多样性审计

总组合数（笛卡尔积）：body_type(4) × hinge_mechanism(3) × top_cap(3) = **36**。
经兼容矩阵剪枝（torsion_spring 与 boxed_housing 互斥 → 不存在该组合，但 spring 与其他 hinge 不冲突；剪枝只发生在 hinge slot 内部——spring 只是少了与 boxed 并存的需求，spring 本身仍是合法第三候选）：hinge slot 仍提供 3 个互斥候选，互斥规则是"不能同时选 spring 与 boxed"——因 hinge 是单选 enum，**本就只选一个**，故 36 组合全部合法（互斥语义体现在：若未来允许复合 hinge 才需 gate；单选下 36 全可行）。叠 rib_count 采样数（仅 ribbed cap 分裂为 r3..r8 共 6 档，其余 cap 各 1 档）：distinct slot_choice ≈ body(4) × hinge(3) × [hump(1)+slab(1)+ribbed(6)] = 4×3×8 = **96**。

理由：body_type × hinge_mechanism 单独即 4×3 = **12 distinct 组合**，含真实结构差异（base mesh 4 形态 × 后铰硬件 3 套：暴露 knuckle+pin+双cheek / 箱壳+中央tongue（删 knuckle/pin）/ knuckle+pin+coil+双cheek）。boxed_housing 改变 arm rear part 集合（中央 tongue vs 双 cheek）+ 删 base 硬件（knuckles/pin）→ 真正的 part 集合差异；torsion_spring 加一个 helix mesh + 接触语义。叠 top_cap(3，其中 ribbed 又分 6 档 rib_count) → 96 distinct slot_choice。**所有 slot 与 rib_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("body_type",m)`、`("hinge_mechanism",m)`、`("top_cap",m)`、ribbed 时 `("rib_count",f"r{N}")`），否则损失维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（body_type / hinge_mechanism / top_cap），经兼容矩阵合法化（hinge 单选 enum，spring×boxed 互斥在单选下自然满足；body=plier 解析 anvil 座高；hinge=boxed 解析 arm rear=中央 tongue），再 `rng.choices` 加权 rib_count（仅 ribbed cap）+ feet/staple 派生数（随 body），再 uniform 各连续 scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 boxed 箱壳 arm 跨骑 + torsion spring 绕 pivot + plier 握把下弯 + 各 cap 闭合 / 开角）。


Controlled local parameterization：见 §参数表的 body_len_scale / body_width_scale / body_height_scale / cap_crown_scale / open_angle_scale（independent）+ rib_count（conditional@ribbed）/ staple_count（conditional@full_strip）/ feet_count（conditional 随 body）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采三 named slot + rib_count（解析 conditional 范围：rib_count 仅 ribbed、staple 仅 full_strip、feet 随 body、anvil 座高随 body、arm rear 随 hinge）→ 采 independent body/cap/angle scale → 派生（ARM_LEN 随 body_len_scale、HINGE_Z 随 body_height_scale、anvil 座高随 body type、driver_blade Z 偏置随 anvil 座高）→ 用 4 条 clearance/motion inequality（盖覆盖托、盖顶高于 base 顶、开角抬 driver、rib 不超 crown）投影 / 回缩。跨部件依赖（盖覆盖 vs body 长、driver vs anvil 座高、rib 排布 vs crown 平台）显式落在 §7，在 `resolve_config` 内求解。这些 scale 不破坏 base_to_arm origin、captured-pin/tongue/spring 接口、复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（body/hinge/cap），解析兼容矩阵 + conditional（anvil 座高随 body、arm rear 随 hinge、rib 仅 ribbed、staple/feet 随 body），再 `rng.choices` rib_count（@ribbed），再 uniform 各 scale，采 palette_style | slot_choices_for_seed 含 `("body_type",m)`/`("hinge_mechanism",m)`/`("top_cap",m)` + ribbed 时 `("rib_count",f"r{N}")`，且与 build 一致 |
| compatibility matrix | (1) **torsion_spring × boxed_housing 互斥**：spring 依赖暴露 knuckle + arm cheek 做回位接触，boxed 删了 knuckles/pin 且把 arm rear 改中央 tongue（无 cheek 可接触）→ spring 无承载几何；hinge 为单选 enum，单选下二者本就不并存，sampler 直接在 hinge 三选一即满足（**若审核改为复合 hinge 才需显式 gate**）。 (2) **body=plier_grip 重设 anvil 座高**：plier 的 anvil 坐 anvil_platform（`ANVIL_SEAT_Z<0`），与 tray 候选（`>0`）不同 → resolve 按 body 选择重算 anvil 座面 + driver_blade nose Z，保闭合 register。 (3) **hinge=boxed_housing 改 arm rear**：所有 cap（hump/slab/ribbed）的 arm_shell 后端在 boxed 时换成中央 tongue（删双 cheek），cap mesh 仍按所选 profile（cap 与 hinge 正交，仅后端下伸由 hinge 决定）。 (4) body × cap 正交（任意 body 配任意 cap）；hinge × cap 正交（cap 只换上表面 profile）。 (5) **rib_count 仅 ribbed_cap**、**staple_count 仅 full_strip**、**feet 随 body** —— 非对应 module 上忽略。 | 无 floating / collision / spring 无 cheek 可接触 / 箱壳 arm 不跨骑 / anvil 座高错致 driver 穿模或悬空 / 盖不覆盖托 / 开角不抬 driver |
| controlled local variation | 5 independent + 3 conditional clamped scale，每 build 统一；rib_count/staple/feet 随 module 解析 | 比例变化不破坏 base_to_arm origin、captured-pin/tongue/spring 接口、盖覆盖、anvil register、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 hinge / body / cap 机构 QC（boxed 跨骑 / spring coil / plier 握把 / 各 cap 开合）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_type | 4 | yes | yes | half_strip(parent) / compact / full_strip / plier_grip |
| hinge_mechanism | 3 | yes | yes | exposed_knuckle_pin / boxed_housing / torsion_spring（spring×boxed 互斥）|
| top_cap | 3 | yes | yes | rounded_hump(parent) / slab_cap / ribbed_cap（ribbed 带 rib_count 多重性）|
| rib_count (N_rib) | 6（采样域 {3..8}，5 高频 / 8 长尾）| yes | yes | 仅 ribbed_cap；拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("body_type",m)`/`("hinge_mechanism",m)`/`("top_cap",m)`，且 top_cap=ribbed_cap 时含 `("rib_count",f"r{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；rib_count/staple/feet 为 conditional 随 top_cap/body_type 解析（rib_count⊆[3,8]、staple⊆[0,24]）；4 条 inequality（盖覆盖、盖顶高于 base、开角抬 driver、rib 不超 crown）在 resolve 内投影 / 回缩
- compatibility matrix / gating：torsion_spring 不与 boxed_housing 并存（单选 enum 自然满足）；body=plier 重设 anvil 座高（`ANVIL_SEAT_Z<0`）+ driver Z；hinge=boxed 把 arm rear 改中央 tongue 并删 hinge_knuckles/hinge_pin
- 连续 scale clamp 后不破坏 base_to_arm origin / captured-pin/tongue/spring 接口 / 盖覆盖 / anvil register / 复制逻辑
- 关键 joint：`base_to_arm` REVOLUTE axis≈(0,-1,0)（abs(axis[1])>0.99、x/z≈0，全候选共享）；origin=(HINGE_X,0,HINGE_Z) 落后铰硬件（knuckle 环心 / housing 腔），`fail_if_articulation_origin_far_from_geometry`（0.015）；lower=0 / upper>0.3 且 ≤π·0.40
- captured / contact 接口：element-scoped `allow_overlap`——exposed/spring：`hinge_pin`↔`hinge_knuckles`、`arm_shell`↔`hinge_knuckles`；boxed：`arm_shell`↔`rear_housing`；spring：`torsion_spring`↔`arm_shell`，照搬各样本 run_tests 的 allow_overlap 段（parent L424-437 / boxed L521-530 / spring L505-527）
- hinge=boxed_housing 时断言无 `hinge_knuckles`（base）与无 `hinge_pin`（arm）（照搬 boxed L412-429）
- copied object 遵循 `grip_rib_{i}` / `foot_{i}` / `foot_pad_{i}` / `staple_{i}` / `hinge_knuckle_{i}` 命名 + 绝对式等距/对称 placement + Rule 1（无独立 joint）
- 闭合 rest pose q=0（盖盖托、driver 悬 anvil 上方）；开角 q=upper 时 driver_min_z 抬升
- grandfather：所有 captured/contact 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 rib_count 当普通 int 参数、不进 slot_choice（ribbed cap 时）→ 不同 rib 数 slot_choice 同形，损失拓扑维度。
- torsion_spring 与 boxed_housing 同时发射 → spring 依赖暴露 knuckle/cheek，boxed 删了它们 + 改中央 tongue，spring arm tang 无 cheek 可接触（`expect_contact` FAIL）；二者互斥（单选 enum 下不并存）。
- hinge=boxed_housing 仍发射 `hinge_knuckles` / `hinge_pin`，或不把 arm rear 改成中央 tongue（仍用双 cheek 但箱壳挡住）→ 违反 boxed 拓扑（boxed run_tests 显式断言无 knuckles/pin、arm tongue 在腔内）。
- body=plier_grip 仍把 anvil 座在前 deck（`ANVIL_SEAT_Z>0`）而非 anvil_platform（`<0`）→ anvil 悬空或穿握把；plier 必须下移 anvil 座高 + 重算 driver nose Z（plier run_tests 断言 anvil_min_z∈(-0.012,0.005)、grip_min_z<HINGE_Z-0.020）。
- 把 grip rib / 脚 / 钉条 / knuckle 复制当独立活动 part 加 joint → 违反 Rule 1（固定装饰复制，应 inline 为宿主 part visual）。
- base_to_arm rest pose 设成张开角而非 q=0 闭合 → current-pose 与 viewer 目检不符（全样本 lower=0 闭合）。
- base_to_arm origin 放在托中心或任意点而非后铰硬件（knuckle 环心 / housing 腔）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 开角 upper 过大（>π·0.40）致盖翻过头 / 自碰，或过小不抬 driver → §7 motion inequality FAIL；clamp upper。
- 盖不覆盖托足迹（ARM_LEN 缩太短 / body 加太长）→ §7 覆盖 inequality FAIL；缩 body_len 或扩 ARM_LEN。
- 给 captured-pin / tongue / spring-contact 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"打孔机 / 去钉器 / binder clip"语义混入（冲头 / 双爪 / 弹簧夹）→ 出类，本类是单铰翻盖弹仓订书机。

## 与相邻类别的边界

- 不该混入：**打孔机 / 钻孔器（hole punch）**——后铰压下台面工具但用冲头穿纸 + confetti 接屑盒，无 anvil clinch 槽 / 弹仓推钉轨 / staple 钉条；运动语义不同（如需可作单独 slug）。
- 不该混入：**文具夹 / 长尾夹 / binder clip（clip）**——弹簧 / 杠杆张力夹纸，无后铰翻盖弹仓 / anvil / driver；已有独立 slug `clip`（主运动 spine 不同）。
- 不该混入：**去钉器 / 起钉器（staple remover）**——双爪绕 pivot 对咬起钉，无弹仓 / anvil / driver。
- 不该混入：**电动 / 重型长行程订书机**——含电机 / 驱动滑块 / 长行程，本类是单铰手压机（如需可作单独 slug）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **torsion_spring × boxed_housing 互斥**——因 hinge 是单选 enum，单选下二者本就不并存，是否需要任何显式 gate，还是只在 spec 标记互斥语义即可（本 spec 取后者）；(2) **rib_count 编入 slot_choice 为拓扑维度**（[3,8] 偏小加权）是否接受，还是降为纯 module-local 连续装饰（与 staple_count 同处理）；(3) **staple_count 不编顶层 slot_choice**（仅 full_strip body 派生的 module-local 装饰，[0,24]）是否接受，还是要编 `("staple_count",f"s{N}")`；(4) body=plier_grip 的 anvil 座高下移 + driver Z 重算（conditional）作为派生约束是否充分，还是要拆 plier 为单独 slug（plier 是 squeeze 握把、anvil 在 pivot 下方，与 tray 候选锚高不同但仍单 base part + 单 base_to_arm REVOLUTE，故保留为 body candidate）；(5) Topology target 96<300 的说明是否接受（本小类真实结构上限）；(6) palette_style 6 套（charcoal 为样本基线，其余配色外推）是否合适；(7) boxed_housing 跨 base/arm 接口（删 base knuckles/pin + 改 arm 中央 tongue）由 hinge slot 同时拥有 base 与 arm 侧结构，是否接受此跨 part 的 hinge slot 语义。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **共享 helper**：`_base_body`（按 body_type 切 half/compact/full 的 lofted XZ profile + 尺寸；plier 用 `_base_grip` 椭圆 sweep）、`_anvil_plate`（共享，座高 `ANVIL_SEAT_Z` 按 body 解析）、`_arm_shell`（按 top_cap 切 hump fillet / slab chamfer / ribbed hump；后端下伸按 hinge 切双 cheek / 中央 tongue）、`_hinge_knuckles` + `_hinge_pin`（exposed/spring 共享）、`_rear_housing`（boxed）、`_torsion_spring_mesh`（spring，`tube_from_spline_points`）、`_single_grip_rib`（ribbed rib 循环）、`_foot_pad_shape`/`_rubber_foot`（feet）、`_staple_crown`（full_strip 钉条）、`_carrier_rail`/`_driver_blade`（全候选共享，driver nose Z 随 anvil 座高微调）。
- **arm rear 由 hinge 决定**：`_arm_shell` 需参数化后端下伸——exposed/spring 用 parent 的双 `cheek`（L186-205），boxed 用中央 `tongue`（L227-248）。cap mesh-profile（hump/slab/ribbed）与后端下伸正交，二者在 `_arm_shell` 内组合。
- **anvil 座高 conditional**：tray 候选 `ANVIL_SEAT_Z = DECK_FRONT_Z + 0.0005`；plier `ANVIL_SEAT_Z < 0`（坐 anvil_platform）。driver_blade 在 arm 子帧的 nose Z 偏置随 anvil 座高重算，使闭合时 `blade_min_z ≥ anvil_max_z − tol` 且 X 对位（全样本 run_tests 范式）。
- captured/contact 接口 allow_overlap：`run_stapler_tests` 里逐 hinge 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（exposed parent L424-437 / boxed L521-530 / spring L505-527）。
- conditional 范围解析顺序：先采 body_type / hinge_mechanism / top_cap + rib_count → 解析 anvil 座高（随 body）/ arm rear 下伸（随 hinge）/ rib_count（仅 ribbed）/ staple/feet（随 body）→ 采 independent body/cap/angle scale → 派生 ARM_LEN/HINGE_Z/driver Z → 投影 4 条 clearance/motion inequality。
- 参考模板：选运动拓扑相近的——root chassis + 单 REVOLUTE 翻盖 child + 互斥结构层（`agent/templates/Accessories_Cushion.py` 的 base + lid REVOLUTE + interior 互斥 / shopping_bucket 的翻盖 REVOLUTE + 兼容矩阵 gating + captured-pin allow_overlap 骨架）；stapler 的 base→top_arm 单 REVOLUTE + hinge 互斥（含跨 base/arm 的 boxed tongue）与之同构。stapler 尺度小（base ~0.09-0.28 m、hinge 硬件 mm 级），joint origin 须精确落后铰硬件（≤0.015 m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| half_strip_tray + exposed_knuckle_pin + rounded_hump | rec_build-...-stap_..._3c83c7d2 | `_base_body` L84-113 / `_base_heel_pads` L116-124 / `_anvil_plate` L127-139 / `_arm_shell` L142-206 / `_hinge_knuckles` L209-227 / `_hinge_pin` L230-239 / `_carrier_rail` L242-255 / `_driver_blade` L258-266 / `base_to_arm` REVOLUTE L300-308 / allow_overlap L424-437 | 全类基线坐标约定 + 共享 base/arm/joint + 暴露 knuckle-pin hinge + 圆 hump cap + anvil/rail/driver captured-pin 范式 |
| S2 | A | compact_stubby | rec_stapler_var_compactbody | `_base_body` 短 L121-140 / `_foot_pad_shape` L81-87 + ×2 L271-278 / `_knuckle_shape` L90-115 + ×2 L280-287 / run_tests 比例断言 L342-351 / allow_overlap loop L464-475 | 迷你短托 body（blunt toe、tall wall）+ feet/knuckle for-i 复制范式 |
| S3 | A | full_strip_tray | rec_stapler_var_fullstrip | `_base_body` 长 L111-140 / `_tray_liner` L167-181 / `_rubber_foot` L143-149 + ×4 L318-355 / `_staple_crown` L306-312 + ×12 L364-373 / run_tests L422-479 | 全条长托 body + tray_liner + feet ×4 + staple ×12 弹仓钉条复制 |
| S4 | A | plier_grip | rec_stapler_var_plierbody | `_base_grip` 椭圆 sweep L86-130 / `anvil_platform` L120-125 / `_grip_texture_ridges` ×5 L133-173, L334-341 / anvil 座高 L69 / run_tests L455-487 | 手squeeze 握把 body（anvil 座面下移负 Z + driver Z 重算）+ grip ridge 复制 |
| S5 | B | boxed_housing | rec_stapler_var_boxedhinge | `_rear_housing` U-channel L140-176 / arm_shell 中央 tongue L227-248 / 断言无 knuckles/pin L412-429 / allow_overlap L521-530 | 箱壳 hinge（base housing + arm 中央 tongue，删 knuckles/pin，跨 base/arm）|
| S6 | B | torsion_spring | rec_stapler_var_springhinge | `_torsion_spring_path` L245-278 / `_torsion_spring_mesh` L281-294（`tube_from_spline_points`）/ allow_overlap spring↔arm_shell L519-527 / expect_contact L531-534 / spring 几何断言 L419-543 | 扭簧 hinge（暴露 knuckle+pin+cheek + helix coil 回位接触，**与 boxed 互斥**）|
| S7 | C | slab_cap | rec_stapler_var_slabcap | `_arm_shell` 矩形 + chamfer L146-212 / ARM_SIDE_CHAMFER/ARM_CORNER_CHAMFER L54-55 / slab 几何断言 L366-403 | 平顶矩形板盖（侧棱 chamfer，arm_shell mesh-profile）|
| S8 | C | ribbed_cap（+ rib_count 多重性）| rec_stapler_var_ribbedcap | `_arm_shell` hump L142-206 / `_single_grip_rib` L280-292 / `for i in range(5)` L325-333 / rib 断言 L462-496 | 带脊圆盖 + grip rib for-i 复制（rib_count copy-logic 源）|
