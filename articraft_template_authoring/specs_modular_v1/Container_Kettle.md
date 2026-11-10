# Container kettle (teapot / electric kettle / stovetop whistler — body + spout + handle + lid + base) — Modular Spec

> 来源小类：`picture/Container/Kettle`（articraft_data 上游 Container/Kettle fork-variant pool）。
> 2 个 fork 母资产（P_electric 电热水壶 / P_stovetop 炉灶鸣笛壶）+ 7 个 qwen 收敛变体，全部逐一读取 `revisions/rev_000001/model.py`。
> 引用 `model.py:Lx-Ly` 来自各 record 当前 `revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`_body_shell` / `_body_solid` / `_loft` / `_loft_z` / `_spout` / `_spout_solid` / `_spout_root_fairing` / `_handle` / `_bail_mesh` / `_carry_loop_solid` / `_leg_mesh` / `_lid_solid` / `_lid_mesh` / `_twist_cap_body` / `_lid_dome_solid` / `_shutter_plate_solid` / `_base_solid` / `_trivet_ring_mesh` / `body_lift` / `lid_hinge` / `body_to_lid` / `spout_to_cap` / `body_to_handle` / `loop_pivot` / `body_to_legs` / `legs_to_grip` / `cap_twist` / `body_to_shutter` / `trivet_to_body` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_kettle` |
| template path | `agent/templates/Container_Kettle.py` |
| test path (optional) | `tests/agent/test_container_kettle_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + handle + lid_closure + base_heating；handle / lid / base 件挂到 kettle body 共同 parent；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 2 parent（电热 `d04a456a` / 炉灶 `89ab783c`）+ 7 qwen converged 变体（gooseneck_body / squat_round_body / folding_bail / side_loop_handle / screw_cap_lid / sliding_pour_lid / trivet_stand）= 9 |
| read_count | 9（全部逐一读 `model.py` 全文，含 build_object_model + run_tests）|
| read_scope | all 9 retained kettle records（2 parent + 7 fork variant），无抽样 |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表与 §14 |

关键结构发现（驱动 slot / 兼容矩阵设计）：
- **两条不兼容的运动 spine / root 家族**，是本类目最强的结构事实：
  - **Electric 家族**（root = `power_base`，body 经 `body_lift` PRISMATIC 自底座抬起；spout 是 collar 上一只 fixed 喇叭口 `_spout`，无 whistle cap；handle 默认是 fixed C-handle）：`d04a456a` / `squat_round_body` / `side_loop_handle` / `screw_cap_lid`。
  - **Stovetop 家族**（root = `body`，body 直接坐地或坐 trivet；spout 是穿壁 hollow tube `_spout_solid` + `_spout_root_fairing` + 鸣笛 `whistle_cap` REVOLUTE；handle 默认 swing bail）：`89ab783c` / `gooseneck_body` / `folding_bail` / `sliding_pour_lid` / `trivet_stand`。
- 这两条 spine 的 **root 坐标系、body 抬升语义、spout 类型、是否有 whistle cap** 都不同。spec 把 base_heating 槽（flat_stovetop / cordless_power_base / trivet_stand）作为决定 root 的轴，handle / lid 候选标注 family 亲和度，兼容矩阵据此 gate（见 §9）。
- body 一律 lathe / loft 中空开口壳（`_loft` / `_loft_z` 圆截面叠环），底坐 z=0（stovetop）或经底座（electric），中心轴 +Z，spout 出 +X，handle 出 -X 或侧后象限。
- spout 是 body 的 **fixed visual**（非独立 slot）：electric 家族 `_spout`（collar 喇叭口），stovetop 家族 `_spout_solid`+`_spout_root_fairing`（穿壁锥管，可选 `whistle_cap` REVOLUTE）。spout/cap 随 body_form 家族派生，不单列 slot。
- handle 候选含 0~2 个活动件：fixed_c_handle（0 joint，body fixed visual）/ swing_bail（1 REVOLUTE）/ side_loop_handle（1 REVOLUTE 绕竖直 Z）/ folding_bail（2 串联 REVOLUTE：legs + grip）。
- lid_closure 候选含 1 活动件 4 种 joint 拓扑：liftoff_knob（PRISMATIC +Z）/ rear_flip_hinge（REVOLUTE +X/−Y 后铰）/ screw_cap（REVOLUTE +Z 拧）/ sliding_pour_lid（fixed dome + shutter PRISMATIC +Y）。

## 核心身份

一只直立中空的**水壶 / 茶壶 / 烧水壶**（kettle）：body 壳沿 +Z 立轴，由 CadQuery `loft` / `revolve` 发射为厚壁中空开口壳（真实可装水腔体），形态可为收腰直筒（electric barrel）/ 钟形宽底窄颈（stovetop bell）/ 低宽梨形（gooseneck pour）/ 矮胖鼓肚卵形（squat pot-belly）。body 前方（+X）必有一只**出水口 spout**（壶嘴：collar 喇叭口或穿壁锥管，可带鸣笛 whistle cap）——这是水壶区别于杯 / 罐的核心身份件。body 上挂一只**握持机构 handle**（提梁 / C 把 / 侧环 / 折叠提梁，主活动语义之一）和一只**开盖机构 lid**（提钮盖 / 后铰翻盖 / 旋拧盖 / 滑动挡板，主活动语义之二）。底部为**支撑 / 加热形式 base_heating**（平底坐炉 / 独立电源底座 / 带足 trivet 托架）。默认成熟域：单壶单嘴单盖（无 multiplicity / 无嵌套）。

不该混入：无嘴的饮水杯（`container_cup`，有 handle 但无 spout、无 lid 开盖机构）、宽口储物 / 化妆罐（`container_jar`，无 spout 倒水嘴、body 宽口）、细颈瓶 / 酒瓶（`container_bottle`，长颈、无 handle / 无 spout）、咖啡 / 茶滤压壶（french press，柱塞下压，不在此池）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 kettle body 的 mesh 属性（一次 `_body_mesh(body_form)` 发射 shell + spout[ + whistle_cap]），其 root 归属由 `base_heating` 决定（electric→power_base root + body_lift；stovetop→body 即 root；trivet→trivet_stand root + trivet_to_body）。`handle` / `lid_closure` 各自挂到 body 共同 parent（parallel children）。四轴笛卡尔积（受 family gate 约束）构成拓扑多样性（见 §9）。

### Slot A：body_form（壳体轮廓家族 / lathe profile + spout 形态——root 归 body 或 base 链）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_barrel（electric 基线）| rec_…_d04a456a | `_body_shell` L62-83 + `_spout` L86-115 + `_pour_cut` L118-128 + collar L267-277 | eligible if compatible | 收腰直筒高壳（`_loft` 圆截面，BODY_R≈0.066，高 0.196），collar 黑环 + 前 +X 短上扬喇叭口 `_spout`，无 whistle cap；electric 家族 |
| bell_lathe（stovetop 基线）| rec_…_89ab783c | `_body_solid` L80-104 + `_spout_solid` L142-156 + `_spout_root_fairing` L158-172 + `_loft_z` L67-77 | eligible if compatible | 钟形（宽底 R≈0.090→窄颈 R≈0.058），穿壁锥管 spout `_spout_solid` + saddle `_spout_root_fairing` + 鸣笛 cap；stovetop 家族 |
| gooseneck_pour | rec_container_kettle_var_gooseneck_body | `_body_solid` L75-102 + `_pour_spout_mesh` L133-143 + `_spout_root_fairing` L146-166 + SPOUT_POINTS L46-52 | eligible if compatible | 低宽梨形宽肩壶身（wider-than-tall），短顺肩 spline pour spout（不高拱），+ 鸣笛 cap；stovetop 家族 |
| squat_round | rec_container_kettle_var_squat_round_body | `_body_shell` L94-109 + `_OUTER_PROFILE` L52-62 + `_body_r` L65-77 + `_spout` L112-141 | eligible if compatible | 矮胖鼓肚卵形（BELLY_R≈0.095 中段最宽，wider-than-tall），collar 喇叭口 spout，无 whistle cap；electric 家族 |

硬约束记录：body_form 4 candidate（达 3-6 目标下半区）。2 圆筒高壳（electric, collar 喇叭口 spout）+ 2 矮宽壳（1 stovetop 梨形穿壁 spout + 1 electric 鼓肚 collar spout）。全部 `_loft`/`_loft_z` 圆截面中空开口壳，只换 footprint / 高宽比 / spout 形态（collar 喇叭口 vs 穿壁锥管），属真实形态差异（非纯尺寸）。

### Slot B：handle（握持机构槽——主机构槽之一）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| swing_bail（stovetop 基线）| rec_…_89ab783c | `_bail_mesh` L188-208 + `body_to_handle` REVOLUTE axis=(0,1,0) L336-346 + `mount_lug_{0,1}` L240-245 | eligible if compatible | 拱形提梁 `bail_handle` 绕肩部两 lug 的 Y 轴 REVOLUTE 摆落（q=0 拱起 / 正 q 落侧）；1 活动件 1 joint |
| fixed_c_handle（electric 基线）| rec_…_d04a456a | `_handle` L131-164 + `_strut` L167-182（body.visual `handle` L291，无独立 joint）| eligible if compatible | 后置（-X）刚性 C 把：grip + upper/lower strut，挂 body 为 **fixed visual 无 joint**；0 活动件 |
| folding_bail | rec_container_kettle_var_folding_bail | `_leg_mesh` L195-210 + `_grip_arch_mesh` L213-229 + `body_to_legs` REVOLUTE L375-385 + `legs_to_grip` REVOLUTE L398-408 | eligible if compatible | 两段折叠提梁：`bail_legs`（绕肩 lug Y 轴 REV）+ `bail_grip`（绕中部 knuckle Y 轴 REV，串联挂 legs）；2 活动件 2 串联 joint |
| side_loop_handle | rec_container_kettle_var_side_loop_handle | `_carry_loop_solid` L179-230 + `_lug_solid` L153-176 + `loop_pivot` REVOLUTE axis=(0,0,1) origin 后象限 L415-429 | eligible if compatible | 侧后象限（135° +Y）D 形提环 `carry_loop` 绕竖直 Z 轴 REVOLUTE 翻起（q=0 贴身 / 正 q 外展）；1 活动件 1 joint（竖直轴，区别于 bail 的水平轴）；electric 家族 |

硬约束记录：handle 4 candidate（达 3-6 目标）。含 0 joint（fixed C 把）/ 1 REVOLUTE 水平轴（swing bail）/ 1 REVOLUTE 竖直轴（side loop）/ 2 串联 REVOLUTE（folding bail）四种拓扑。fixed_c_handle 是唯一 0-joint 候选——保留作降级理由：electric 家族真实形态就是刚性后把，body 上至少有 lid / base 的活动件保证整模 ≥1 non-fixed joint（不违反"每模 ≥1 活动机构"——活动语义由 lid/base 承担）。

### Slot C：lid_closure（开盖 / 封口机构槽——主机构槽之二）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| liftoff_knob（stovetop 基线）| rec_…_89ab783c | `_lid_mesh` L175-185 + `body_to_lid` PRISMATIC axis=(0,0,1) L268-276 + knob `stem`/`knob` L257-262 | eligible if compatible | 带钮圆顶盖 `lid` 沿 +Z PRISMATIC 直提脱离 rim（q=0 坐 rim / 正 q 抬离 0.04）；1 PRISMATIC |
| rear_flip_hinge（electric 基线）| rec_…_d04a456a | `_lid_solid` L204-222 + `lid_hinge` REVOLUTE axis=(0,-1,0) origin 后 rim L328-337 + `hinge_knuckle` L318-321 | eligible if compatible | 后铰翻盖 `lid`：盘盖绕后 rim 水平轴 REVOLUTE，q=0 闭合 / 正 q 前缘上翻后摆（~70°）；1 REVOLUTE +X 向后铰 |
| screw_cap | rec_container_kettle_var_screw_cap_lid | `_twist_cap_body` L208-262 + `cap_twist` REVOLUTE axis=(0,0,1) L397-406 + `_twist_cap_lug` L265-280 | eligible if compatible | 旋拧 / 卡口盖 `cap`：domed 螺纹塞盖坐 collar，绕竖直 Z 轴 REVOLUTE 拧紧（q=0→正 q 拧，高度不变）；1 REVOLUTE +Z；electric 家族 |
| sliding_pour_lid | rec_container_kettle_var_sliding_pour_lid | `_lid_dome_solid` L192-213（fixed body visual）+ `_shutter_plate_solid` L216-241 + `body_to_shutter` PRISMATIC axis=(0,1,0) L358-369 + track_rail L333-338 | eligible if compatible | 固定圆顶盖（body visual，带 pour 开口 + track rail + 固定 knob）+ 月牙挡板 `shutter` 沿 +Y PRISMATIC 横滑开闭 pour 口；1 PRISMATIC +Y（盖本身 fixed）；stovetop 家族 |

硬约束记录：lid_closure 4 candidate（达 3-6 目标）。含 PRISMATIC +Z（liftoff）/ REVOLUTE 水平后铰（flip）/ REVOLUTE +Z（screw）/ PRISMATIC +Y（shutter）四种不同 joint 拓扑 + 不同 part 组（liftoff/flip/screw=独立活动盖 part；sliding=fixed dome visual + 独立 shutter part）。每个 candidate **≥1 non-fixed joint**。

### Slot D：base_heating（支撑 / 加热形式槽——决定 root 与 body 抬升语义）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| flat_stovetop（stovetop 基线）| rec_…_89ab783c | `_body_solid`（平底直接坐地 z=0，无独立 base part）L80-104；body 即 root | eligible if compatible | 平底坐炉：body 是 root，底面 z=0 坐地，无 base part / 无 body_lift joint；stovetop 家族 |
| cordless_power_base（electric 基线）| rec_…_d04a456a | `_base_solid` L185-201（power_base root）+ `body_lift` PRISMATIC axis=(0,0,1) L299-307 + control_pad/power_button L237-250 | eligible if compatible | 独立圆形黑电源座 `power_base`（root，含 control pad + button），body 经 `body_lift` PRISMATIC +Z 直提脱离座（q=0 坐座 / 正 q 抬离 0.04）；electric 家族 |
| trivet_stand | rec_container_kettle_var_trivet_stand | `_trivet_ring_mesh` L188-197 + `_trivet_leg_geometry` L200-204（trivet_stand root, 4 leg loop L259-268）+ `trivet_to_body` PRISMATIC axis=(0,0,1) L313-321 | eligible if compatible | 带足 cast-iron trivet 环托架 `trivet_stand`（root，环 + 4 足 loop），body 坐环上经 `trivet_to_body` PRISMATIC +Z 可提起（q=0 坐环 / 正 q 抬离 0.06）；stovetop 家族（坐式底座）|

硬约束记录：base_heating 3 candidate（达下限 3）。flat_stovetop 无独立 base（body=root，0 base joint）；cordless_power_base / trivet_stand 各引入 1 PRISMATIC body-lift joint + 独立 root part。这是**决定 root 坐标系与 family 的轴**：flat_stovetop/trivet→stovetop spine；cordless→electric spine（见 §9 兼容矩阵）。

## 槽位图（slot graph）

pattern: parallel_children（base_heating 决定 root；body 为壳；handle / lid 挂到 body 共同 parent；无 multiplicity）

```
base_heating 决定 ROOT 与 body 抬升语义：
 ── flat_stovetop:    body(body_form)  [body 即 ROOT, 平底坐地 z=0]
 ── cordless_power_base:
       power_base [ROOT, 坐地] --[body_lift: PRISMATIC +Z @ base 顶]--> body(body_form)
 ── trivet_stand:
       trivet_stand [ROOT, 坐地] --[trivet_to_body: PRISMATIC +Z @ ring 顶]--> body(body_form)

body(body_form)  [挂 spout fixed visual( + whistle_cap REVOLUTE 若 stovetop spout)]
   │
   ├── handle = swing_bail:
   │     body --[body_to_handle: REVOLUTE +Y @ 肩 mount line]--> bail_handle
   │
   ├── handle = fixed_c_handle:
   │     body.visual(handle)  [无 joint, 后置 -X 刚性 visual]
   │
   ├── handle = folding_bail:
   │     body --[body_to_legs: REVOLUTE +Y @ 肩 mount]--> bail_legs
   │            bail_legs --[legs_to_grip: REVOLUTE +Y @ 中部 knuckle]--> bail_grip
   │
   ├── handle = side_loop_handle:
   │     body --[loop_pivot: REVOLUTE +Z @ 后象限 lug line(rpy yaw=π/4)]--> carry_loop
   │
   ├── lid_closure = liftoff_knob:
   │     body --[body_to_lid: PRISMATIC +Z @ rim 顶]--> lid
   │
   ├── lid_closure = rear_flip_hinge:
   │     body --[lid_hinge: REVOLUTE +X向后铰(axis=(0,-1,0)) @ 后 rim 边]--> lid
   │
   ├── lid_closure = screw_cap:
   │     body --[cap_twist: REVOLUTE +Z @ collar 顶 seat]--> cap
   │
   └── lid_closure = sliding_pour_lid:
         body.visual(lid_dome + pour_lip + knob + track_rail)  [固定圆顶盖, 无 joint]
         body --[body_to_shutter: PRISMATIC +Y @ pour 口 dome 面]--> shutter
```

接口点位与 joint 语义：
- **root / base 接口**：cordless 的 `body_lift` origin 在 base 顶面中心 `(0,0,BASE_H+0.005)`，axis +Z PRISMATIC；trivet 的 `trivet_to_body` origin 在 ring 顶 `(0,0,TRIVET_TOP_Z)`，axis +Z PRISMATIC；flat_stovetop 无此 joint（body 即 root，底面坐 z=0）。base 与 body 的接触：`base_collar`/`body_shell` 底坐 base_disc/trivet_ring（`expect_contact` + `allow_overlap` 坐位过盈）。
- **handle 接口**：swing_bail / folding_bail 的 `body_to_handle`/`body_to_legs` origin 在肩 mount line `(MOUNT_X,0,MOUNT_Z)`，axis +Y（两 lug 连线），REVOLUTE 摆落；folding 的 `legs_to_grip` origin 在 legs-local knuckle `(KNUCKLE_X,0,KNUCKLE_Z)`，axis +Y。side_loop 的 `loop_pivot` origin 在后象限 lug 外面 `(PIVOT_X,PIVOT_Y,PIVOT_Z)` 带 rpy yaw=π/4，axis +Z（竖直），REVOLUTE 外展。fixed_c_handle 无 joint（body fixed visual，挂 -X）。
- **lid 接口**：liftoff `body_to_lid` origin 在 rim 顶中心 `(0,0,RIM_Z)`，axis +Z PRISMATIC；flip `lid_hinge` origin 在后 rim 硬件 `(HINGE_X,0,HINGE_Z)`，axis (0,-1,0) REVOLUTE（lid 盘前伸 +X，−Y 抬前缘）；screw `cap_twist` origin 在 collar 顶 `(0,0,CAP_SEAT_Z)`，axis +Z REVOLUTE（拧，高度不变）；sliding `body_to_shutter` origin 在 pour 口 dome 面 `(0,POUR_OPEN_Y,RIM_Z+DOME_TOP_Z)`，axis +Y PRISMATIC（shutter 横滑；dome 本身 fixed visual）。
- **spout 接口**：spout 是 body fixed visual（随 body_form 家族派生），electric 家族 collar 喇叭口 `_spout`（无 cap），stovetop 家族穿壁锥管 `_spout_solid`+`_spout_root_fairing`（带 `whistle_cap` REVOLUTE 绕 spout 嘴上沿 hinge 轴 (0,-1,0) 翻起）。spout/cap 不单列 slot，随 body_form 决定。
- **mating policy**：盖 / 提梁 / 提环 / shutter 与 body / lug / spout 的配合都是 captured / 友配（盖 skirt 罩 rim、bail 腿端坐 lug、shutter 坐 dome、cap 塞插 collar bore），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 rim / hinge / lug / collar 硬件）+ element-scoped `allow_overlap`（各 record run_tests 的 `ctx.allow_overlap`）守 overlap。
- **rest pose**：所有盖 q=0 闭合 / 坐下；bail / loop q=0 拱起 / 贴身；shutter q=0 盖 pour 口；body q=0 坐 base / trivet（electric/trivet）。lid 提升 / flip / 拧、handle 摆落、body 抬离为 viewer 目检的活动语义。
- **互斥 / 可选**：base_heating 各候选决定 root 与 family，与 handle/lid 的 family 亲和度做兼容 gate（见 §9）；handle 各候选互斥，lid_closure 各候选互斥；`whistle_cap` 仅在 stovetop spout（bell_lathe / gooseneck_pour body_form）发射；`power_base`/`trivet_stand` 独立 root part 仅在对应 base 候选发射。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form（kettle body + spout，可能是 ROOT 或 base 的 child）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（electric 家族叫 `kettle_body`）：visual `body_shell` 中空壳 + collar/heel（electric）+ spout fixed visual | d04a456a `_body_shell` L62-83 / 89ab783c `_body_solid` L80-104 |
| spout visual | electric: `_spout` collar 喇叭口（L86-115）；stovetop: `_spout_solid`+`_spout_root_fairing`（L142-172）穿壁锥管 | 各 body 源 |
| internal joints（可选）| stovetop 家族派生 `whistle_cap` part + `spout_to_cap` REVOLUTE（axis=(0,-1,0) @ spout 嘴上沿）| 89ab783c L307-316 / gooseneck L309-318 |
| upstream interface | flat_stovetop 时底面坐地 z=0（root）；cordless/trivet 时作 body_lift/trivet_to_body 的 child（origin base 顶）| 各 base 源 |
| downstream interface | rim 顶中心（lid joint parent）/ 肩 mount line（handle joint parent）/ collar 顶（screw seat）| 各源 RIM_Z / MOUNT_Z / CAP_SEAT_Z |

### Slot B / handle（每候选发射对应握持件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bail_handle` / body.visual `handle`（fixed）/ `bail_legs`+`bail_grip` / `carry_loop`(+body lug visual) | 各 handle 源 |
| internal joints | `body_to_handle` REVOLUTE +Y（bail）/ 无（C 把）/ `body_to_legs`+`legs_to_grip` REVOLUTE +Y（folding）/ `loop_pivot` REVOLUTE +Z（side loop）| 89ab783c L336-346 / d04a456a（无）/ folding L375-408 / side_loop L415-429 |

### Slot C / lid_closure（每候选发射对应开盖件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（liftoff/flip）/ `cap`（screw）/ body.visual `lid_dome`+`shutter` part（sliding）| 各 lid 源 |
| internal joints | `body_to_lid` PRISMATIC +Z / `lid_hinge` REVOLUTE 后铰 / `cap_twist` REVOLUTE +Z / `body_to_shutter` PRISMATIC +Y | 89ab783c L268-276 / d04a456a L328-337 / screw L397-406 / sliding L358-369 |

### Slot D / base_heating（决定 root；≠flat 时发射独立 root part + body-lift joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（flat：body=root）/ `power_base`(+control_pad+button) / `trivet_stand`(+4 leg) | d04a456a `_base_solid` L185-201 / trivet `_trivet_ring_mesh` L188-204 |
| internal joints | 无（flat）/ `body_lift` PRISMATIC +Z（cordless）/ `trivet_to_body` PRISMATIC +Z（trivet）| d04a456a L299-307 / trivet L313-321 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | straight_barrel / bell_lathe / gooseneck_pour / squat_round | bell_lathe | choice | deterministic procedural sampler 选 | module table |
| handle | enum | swing_bail / fixed_c_handle / folding_bail / side_loop_handle | swing_bail | choice | sampler 选；family-gated（见 §9）| module table |
| lid_closure | enum | liftoff_knob / rear_flip_hinge / screw_cap / sliding_pour_lid | liftoff_knob | choice | sampler 选；family-gated（见 §9）| module table |
| base_heating | enum | flat_stovetop / cordless_power_base / trivet_stand | flat_stovetop | choice | sampler 选；决定 root 与 family | module table |
| palette_style | enum | brushed_steel / polished_stainless / matte_black_electric / copper_stovetop / enamel_pastel / enamel_red / glossy_ceramic_white / cast_iron_trivet / two_tone_cream_steel | brushed_steel | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)`；含显式 finish 维（见下表 finish 列）| palette（见下）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 body 高 H → RIM_Z / COLLAR_Z / mount / hinge 高度同比，clamp | resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 body 半径 / 半宽 → 同比 spout root / collar / rim 半径，clamp | resolve clamp |
| spout_reach_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 spout 前伸长度（+X）+ tip 高，clamp（保不穿 body / 不过短）| resolve clamp |
| handle_offset_scale | float | [0.90, 1.12] | 1.0 | equation | `handle 外伸 / lug 跨距 = base · body_radius_scale · handle_offset_scale`（跟随 body 半径，保 grip 离 body 净空）| resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lid lift / shutter slide / body_lift 行程 + hinge / bail / loop limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖 / 提梁配合：`lid_bore_R ≥ rim_R + clearance`、`bail_clear = handle_offset − body_R ≥ grip_min`、`spout_max_x ≤ reach_cap`，违反按比例回缩 | 接口 / clearance |
| (—) | constraint | — | — | conditional | `whistle_cap` 仅当 body_form ∈ {bell_lathe, gooseneck_pour}（stovetop spout）发射；spout 类型随 body_form family 解析 | family / 接口 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`handle_offset_scale` 为 equation（lug 跨距 / grip 外伸跟随 body 半径，保 grip 与 body 净空）。`whistle_cap` 发射为 conditional（随 body_form family）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / handle / lid_closure / base_heating 的拓扑。

**palette_style 配色（9 colorway，每 seed `rng.choice(PALETTE_STYLES)` 采样；锚定 5★ 源 RGBA，其余真实域内派生）**

每个 colorway = body 壳 + handle/grip + lid·spout + base/accent 四组件色 + **显式 finish 维**（material-finish dimension）。finish 列是本次新增的显式维度（决定壶的视觉表面质感：拉丝/抛光/亮面珐琅/抛光铜/哑光黑电热/铸铁/亮釉陶瓷/双色/缎面粉末涂层），与具体配色绑定但独立于结构 family。所有 colorway 对 electric / stovetop 两 family 与任意 slot 组合**正交合法**（颜色/质感不绑定结构 family；trivet/electric 颜色对任意 body 都成立）。

| palette_style | body 壳 | handle/grip | lid·spout | base/accent | **finish** | 锚 / 来源 |
|---|---|---|---|---|---|---|
| `brushed_steel` | 钢 (0.78,0.79,0.81) | 黑 grip (0.12,0.12,0.13) | 钢 lid / 钢 spout + 暗钢影 (0.66,0.67,0.69) rim/cap | 钢 base / 暗钢 accent | **brushed stainless（拉丝不锈钢）** | 89ab783c（stovetop / 通用基线）|
| `polished_stainless` | 亮钢 (0.85,0.86,0.88) | 黑 grip (0.12,0.12,0.13) | 亮钢 lid / 亮钢 spout + 钢镜面 (0.80,0.81,0.83) rim/cap | 亮钢 base / 钢镜面 accent | **polished stainless（镜面抛光不锈钢）** | 派生（拉丝基线提亮的抛光版）|
| `matte_black_electric` | 黑塑 (0.10,0.10,0.11) | 暗灰 (0.18,0.18,0.20) grip | 暗灰 lid (0.18,0.18,0.20) / 钢 spout (0.66,0.67,0.69) | 黑 base + 蓝玻璃水位窗 (0.30,0.40,0.48,0.85) | **matte black electric（哑光黑电热塑壳）** | d04a456a（electric power-base 基线）|
| `copper_stovetop` | 钢 (0.78,0.79,0.81) | 黑 grip (0.12,0.12,0.13) | 钢 lid / 铜 spout 嘴 + 铜 cap/pour lip 铜 accent (0.72,0.45,0.20) | 钢 base / 铜 accent | **polished copper accent（抛光铜口件）** | gooseneck / sliding（copper_accent）|
| `enamel_pastel` | 浅珐琅薄荷/天蓝壳 (0.62,0.80,0.78) | 黑 grip (0.12,0.12,0.13) | 同色珐琅 lid / 钢 spout + 钢影 (0.66,0.67,0.69) rim | 钢 base / 暗钢 accent | **enamel gloss pastel（亮面珐琅·柔彩）** | 派生（真实搪瓷壶柔彩域）|
| `enamel_red` | 珐琅正红壳 (0.74,0.12,0.10) | 黑 grip (0.12,0.12,0.13) | 红珐琅 lid / 钢 spout + 钢影 (0.66,0.67,0.69) rim | 钢 base / 黑 accent | **enamel gloss red（亮面珐琅·正红）** | 派生（经典红搪瓷烧水壶）|
| `glossy_ceramic_white` | 亮釉象牙白壳 (0.93,0.92,0.89) | 暗灰 (0.20,0.20,0.22) grip | 白釉 lid / 暗灰 spout + 暗灰 (0.20,0.20,0.22) rim | 暗灰 base / 暗灰 accent | **glossy ceramic（亮釉陶瓷）** | 派生（陶瓷茶壶域）|
| `cast_iron_trivet` | 钢壶身 (0.78,0.79,0.81) | 黑 grip (0.12,0.12,0.13) | 钢 lid / 钢 spout + 暗钢影 (0.66,0.67,0.69) rim | 铸铁 base/trivet (0.22,0.22,0.24) | **cast iron（铸铁托架/底座）** | trivet_stand（cast_iron）|
| `two_tone_cream_steel` | 奶油米色上壳 (0.90,0.86,0.78) | 黑 grip (0.12,0.12,0.13) | 钢 lid / 钢 spout + 暗钢影 (0.66,0.67,0.69) rim·collar | 钢 base / 暗钢 accent | **two-tone（米色珐琅壳 + 拉丝钢件）** | 派生（米色+钢双色复古壶）|

> 备选 / 派生说明：以上 9 colorway 覆盖 electric + stovetop 两族的真实质感谱（brushed/polished stainless、enamel gloss pastel/red、polished copper、matte black electric、cast iron、glossy ceramic、two-tone）。若实现侧需要第 10 个 colorway，加 `satin_powder_coat`（缎面粉末涂层：哑光雾灰/橄榄壳 (0.42,0.44,0.42) + 黑 grip + 钢 spout/rim + satin powder-coat finish），同样 palette-only、family-正交。
>
> finish 维落地建议：每个 colorway 的 finish 字符串作为 colorway dict 的一个 key（如 `{"finish": "polished_stainless", ...}`），仅影响 material 命名 / RGBA 选择（可叠加 specular/roughness 提示到 material name），**不发射任何新 part / joint / 不改任何尺寸或拓扑**。

palette_style 是 palette-only，不计入 `slot_choice`，不改拓扑；与所有 slot 组合正交（任一 colorway × 任一 body_form/handle/lid/base_heating 合法；颜色/finish 不绑定 electric/stovetop 结构 family）。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + handle + lid_closure + base_heating）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单壶单嘴单盖。
  - 注：`trivet_stand` 的 4 足（`for i in range(4)` 发射 `trivet_leg_{i}`，trivet L259-268）、`folding_bail` 的 2 腿对（`leg_{i}`）、`screw_cap` 的 3 bayonet lug（`cap_lug_{i}`，screw L382-389）、`side_loop` 的 2 lug 在各自候选内用 for 循环发射，但**数量固定属该候选的内部装饰 / 对称件**，不是跨样本的多重性轴；source map 不把它当 multiplicity slot，不暴露 `*_count` 参数。

## 拓扑多样性审计

总组合数（笛卡尔积上界）：body_form(4) × handle(4) × lid_closure(4) × base_heating(3) = **192**。
受 family 兼容 gate 后的合法组合数（见兼容矩阵）：约 **60-90**（保守估计 ≥60，远超门控）。

仅 handle(4) × lid_closure(4) = **16 ≥ 10** 已可过门控；叠 body_form × base_heating 后充裕。

理由：本类拓扑多样性来源充裕——handle(4) × lid_closure(4) 的笛卡尔积即 16 distinct 不同 joint 拓扑组合（handle: 0/1-水平/1-竖直/2-串联 joint；lid: PRISMATIC+Z / REVOLUTE-后铰 / REVOLUTE+Z / PRISMATIC+Y），远超 10；再叠 body_form(4) 不同壳 + spout 类型 + base_heating(3) 决定 root 链（无 base joint / power_base+PRISMATIC / trivet+PRISMATIC）。每轴均 ≥3（base_heating 恰 3），主机构轴 handle/lid 各 4。是真实结构差异（非纯尺寸 / 颜色）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` base_heating（决定 family / root），再按 family 亲和加权 `rng.choice` body_form / handle / lid_closure（compatibility matrix gate 见下），再 uniform 各连续 scale + `rng.choice` palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 60-90（受 family gate 约束的真实合法组合域）。低于 300 的原因：本小类真实结构词汇是 4 body × 4 handle × 4 lid × 3 base 受两条 spine family 亲和约束后的合法子集（约 60-90），是该类目的合理上限，不强行注水跨 family 的不真实组合。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / spout_reach / handle_offset / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`handle_offset_scale` 为 equation（lug 跨距 / grip 外伸跟随 body 半径）。盖 / 提梁配合不等式 + spout reach cap 在 resolve 内投影 / 回缩，不留到 builder。`whistle_cap` conditional（随 body_form family）。这些 scale 不破坏 lid/handle/base joint origin（rim 顶 / 后 rim hinge / collar seat / 肩 mount / 后象限 lug / base 顶）、盖罩 / 提梁配合、spout 不穿 body 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` base_heating（定 family/root），按 family 亲和加权 `rng.choice` body_form/handle/lid，再 uniform scale + palette | slot_choices_for_seed 含四轴且与 build 一致 |
| compatibility matrix | **family gate（核心）**：base_heating=cordless_power_base → electric spine（body_form 偏 electric 壳 straight_barrel/squat_round，handle 偏 fixed_c_handle/side_loop_handle，lid 偏 rear_flip_hinge/screw_cap，spout 无 whistle cap）；base_heating ∈ {flat_stovetop, trivet_stand} → stovetop spine（body_form 偏 bell_lathe/gooseneck_pour，handle 偏 swing_bail/folding_bail，lid 偏 liftoff_knob/sliding_pour_lid，spout 带 whistle cap）。跨 family 组合 **大部分合法但降级采样权重**（如 electric body + swing_bail 是真实存在的，但 fixed_c_handle 不能配 stovetop 无座 spout family 的 whistle 逻辑——whistle_cap 仅随 body_form 派生，不随 handle）。**硬 gate-out**：(1) `whistle_cap` 仅当 body_form∈{bell_lathe,gooseneck_pour} 发射（electric collar spout 无 cap，conditional 派生）；(2) screw_cap / side_loop 的竖直 Z 轴 REVOLUTE 与 spout 方位错开（lug offset 60° / loop 135° 避 +X spout，origin 在真实硬件）；(3) sliding_pour_lid 的 shutter 行程不穿 dome rim（resolve clamp SHUTTER_SLIDE）；(4) 各 handle 互斥、各 lid 互斥、base 决定唯一 root。无其他硬 gate（family 主要靠加权，多数跨配合法）| 无 floating / collision / lid 穿壶 / spout 穿 body / joint 轴或 origin 错位 / root 多重 |
| controlled local variation | 5 个 clamped scale，每 build 统一；handle_offset equation 跟随 body 半径；spout reach cap + 盖配合不等式 resolve 投影 | 比例变化不破坏 joint origin / 盖 / 提梁配合 / 坐地 / spout 不穿 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | lid/handle/body 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | electric 直筒 / stovetop 钟形 / 梨形 pour / 鼓肚卵形 |
| handle | 4 | yes | yes | swing bail(REV +Y) / fixed C(0 joint) / folding(2 串联 REV) / side loop(REV +Z) |
| lid_closure | 4 | yes | yes | liftoff(PRIS +Z) / flip(REV 后铰) / screw(REV +Z) / sliding shutter(PRIS +Y) |
| base_heating | 3 | yes | yes | flat 坐地(body=root) / power base(PRIS lift) / trivet(PRIS lift) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, handle, lid_closure, base_heating) 四轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（先 base_heating 定 family/root，再 family-加权选其余轴）
- `resolve_config` 各 scale clamp 到声明范围；handle_offset equation 跟随 body 半径；spout reach cap + 盖/提梁配合不等式在 resolve 内投影 / 回缩；`whistle_cap` conditional 随 body_form family
- compatibility matrix / gating：family gate 主要靠加权，硬 gate-out 仅 (1) whistle_cap 随 stovetop body_form 派生、(2) 竖直轴 lid/handle 避 +X spout、(3) shutter 不穿 rim、(4) 各 handle/lid 互斥 + base 唯一 root
- 连续 scale clamp 后不破坏 joint origin / 盖 / 提梁配合 / 坐地 / spout 不穿 body / 类别身份
- 关键 joint：cordless `body_lift` PRISMATIC +Z / trivet `trivet_to_body` PRISMATIC +Z（base 抬升，flat 无）；swing/folding bail `body_to_handle`/`body_to_legs` REVOLUTE +Y(abs(axis[1])>0.99) + folding `legs_to_grip` REVOLUTE +Y；side_loop `loop_pivot` REVOLUTE +Z(abs(axis[2])>0.99)；fixed_c_handle 无 joint（body visual）；liftoff `body_to_lid` PRISMATIC +Z；flip `lid_hinge` REVOLUTE(axis≈(0,-1,0))；screw `cap_twist` REVOLUTE +Z；sliding `body_to_shutter` PRISMATIC +Y；stovetop body_form 的 `spout_to_cap` REVOLUTE
- captured-fit：element-scoped `allow_overlap`（lid skirt↔rim、bail/leg 端↔mount lug、carry_loop pin↔lug、cap plug↔collar、shutter↔dome/knob_stem、spout_root_fairing↔body_shell、base_collar↔base_disc/trivet_ring）
- grandfather：盖 / 提梁 / shutter / cap captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- root 唯一性：base_heating 决定唯一 root（flat→body / cordless→power_base / trivet→trivet_stand），不并存两 root

## Reject cases

- 用 boxy 占位体（纯 Box）当圆壶 body → 失类别身份；body 必须 `_loft`/`_loft_z` 圆截面中空开口壳。
- body 无 spout 出水口 → 退化成 cup/jar，失水壶身份；body_form 必带 spout fixed visual（collar 喇叭口或穿壁锥管）。
- lid / handle / base joint origin 放在壶底 / 任意点而非 rim 顶 / 后 rim hinge / collar seat / 肩 mount / 后象限 lug / base 顶真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 跨 family 乱配产出非物理体（如 cordless power_base + stovetop 穿壁 whistle spout 又坐地、或两 root 并存）→ family gate / root 唯一性 FAIL；whistle_cap 只随 stovetop body_form 派生。
- lid_closure / handle rest pose 设成张开 / 抬起 / 折下而非 q=0 闭合 / 拱起 / 贴身 → current-pose 与 viewer 目检不符。
- 给盖罩 / 提梁 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- screw_cap / side_loop 的竖直 Z 轴 REVOLUTE 与 +X spout 干涉（lug / loop 没避开 spout 象限）→ 穿模；lug offset 60° / loop 135° 避 +X。
- sliding shutter 行程穿出 dome rim 或 fixed dome 误发射成活动盖 → shutter clamp + dome 为 body fixed visual。
- spout 前伸 scale 过大穿出 body 反侧 / 过短不成嘴，或 handle_offset 过小 grip 贴 body 无净空 → reach cap / 配合不等式 resolve 回缩。

## 与相邻类别的边界

- 不该混入：**container_cup 饮水杯 / 马克杯**（有 handle 但**无 spout 出水嘴、无 lid 开盖机构**）——理由：kettle 的核心身份是出水口 spout + 开盖机构，cup 是敞口单握把容器。
- 不该混入：**container_jar 宽口储物 / 化妆罐**（宽口、无倒水 spout，盖是封口而非烧水壶口）——理由：jar 无 pour spout、body 宽口直壁，kettle 必有壶嘴 + 提梁。
- 不该混入：**container_bottle 细颈瓶 / 酒瓶**（长颈、无 handle、无 spout）——理由：bottle 是细长瓶身 + 长颈，kettle 是宽身 + 侧出壶嘴 + 提梁 + 顶盖。
- 不该混入：**French press / 滤压咖啡壶**（柱塞下压机构，不在本 fork 池）——理由：kettle 是烧水 / 倒水壶，不含滤网柱塞下压 spine。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。读全 9 record（2 parent + 7 variant）。4 slot：body_form(4) × handle(4) × lid_closure(4) × base_heating(3) = 192 上界，family gate 后约 60-90 合法；handle×lid=16 即过 。两条 spine family（electric power_base root + body_lift / fixed C 把 / collar spout 无 cap；stovetop body root 坐地或 trivet / swing bail / 穿壁 spout + whistle cap），base_heating 轴决定 root。handle 含 0-joint(fixed C)/1-水平 REV(bail)/1-竖直 REV(side loop)/2-串联 REV(folding)；lid 含 PRIS+Z(liftoff)/REV-后铰(flip)/REV+Z(screw)/PRIS+Y(shutter)。palette_style 扩为 9 colorway + 显式 finish 维（brushed_steel / polished_stainless / matte_black_electric / copper_stovetop / enamel_pastel / enamel_red / glossy_ceramic_white / cast_iron_trivet / two_tone_cream_steel；finish 谱：brushed/polished stainless · enamel gloss pastel/red · polished copper · matte black electric · cast iron · glossy ceramic · two-tone，外加可选 satin_powder_coat 第 10 个），仍 palette-only、不计 slot_choice、family-正交（每组件 body+handle+lid·spout+base/accent 配色 + finish，锚定 5★ RGBA，余真实派生）。无 multiplicity。待人工审核 family gate 是否做硬拆分（若 electric/stovetop 不收敛建议拆两 slug）。|

## 模板实现备注（可选）

- 共享 helper：`_loft(sections)` / `_loft_z(sections)`（圆截面叠环 body，全 body_form 公用）+ `_spout_solid`/`_spout_root_fairing`（stovetop 穿壁锥管）+ `_spout`（electric collar 喇叭口）+ `_bail_mesh`/`_leg_mesh`/`_grip_arch_mesh`（提梁族）+ `_carry_loop_solid`（D 环）+ `_lid_mesh`/`_lid_solid`/`_twist_cap_body`/`_lid_dome_solid`+`_shutter_plate_solid`（lid 族）+ `_base_solid`/`_trivet_ring_mesh`（base 族）。
- **family / root 分支**：base_heating 决定 root 与 body 的 parent 链——flat_stovetop：body=root（无 base part / 无 body-lift joint）；cordless_power_base：power_base=root，`body_lift` PRISMATIC；trivet_stand：trivet_stand=root，`trivet_to_body` PRISMATIC。spout 类型随 body_form family（electric collar `_spout` 无 cap / stovetop `_spout_solid` + `whistle_cap`）。务必保证唯一 root。
- captured-fit overlap：`run_container_kettle_tests` 里复刻各 record 的 `ctx.allow_overlap`（lid↔rim/collar、bail/leg↔mount_lug、carry_loop d_ring↔lug、cap_body↔top_collar、shutter↔lid_dome/knob_stem、spout↔spout_root_fairing↔body_shell、base_collar↔base_disc/trivet_ring）。
- handle_offset equation：`resolve_config` 派生 lug 跨距 / grip 外伸 = base · body_radius_scale · handle_offset_scale；spout reach cap 不等式 + 盖配合不等式在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（同 parallel_children + 多 lid 机构分支 + captured-fit allow_overlap + element-scoped grandfather 骨架，最近邻）；若 family 拆分则参考 composite/两-spine 模板。
- whistle_cap 为 conditional 派生：仅 body_form∈{bell_lathe, gooseneck_pour} 发射 `whistle_cap` part + `spout_to_cap` REVOLUTE；electric collar spout 不发 cap。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | straight_barrel + fixed_c_handle + rear_flip_hinge + cordless_power_base | rec_…_d04a456a | `_body_shell` L62-83 / `_spout` L86-115 / `_handle` L131-164 / `_lid_solid` L204-222 / `lid_hinge` L328-337 / `_base_solid` L185-201 / `body_lift` L299-307 | electric 直筒 body + collar 喇叭口 spout + 后置 C 把 + 后铰翻盖 + 圆电源座（electric spine 基线）|
| S2 | A/B/C/D | bell_lathe + swing_bail + liftoff_knob + flat_stovetop | rec_…_89ab783c | `_body_solid` L80-104 / `_spout_solid` L142-156 / `_spout_root_fairing` L158-172 / `_bail_mesh` L188-208 / `body_to_handle` L336-346 / `_lid_mesh` L175-185 / `body_to_lid` L268-276 / `spout_to_cap` L307-316 | stovetop 钟形 body + 穿壁 spout + whistle cap + 摆动提梁 + 提钮盖 + 平底坐炉（stovetop spine 基线）|
| S3 | A | gooseneck_pour | rec_container_kettle_var_gooseneck_body | `_body_solid` L75-102 / `_pour_spout_mesh` L133-143 / SPOUT_POINTS L46-52 | 低宽梨形宽肩 body + 短顺肩 spline pour spout（stovetop family）|
| S4 | A | squat_round | rec_container_kettle_var_squat_round_body | `_body_shell` L94-109 / `_OUTER_PROFILE` L52-62 / `_body_r` L65-77 | 矮胖鼓肚卵形 body（electric family, collar spout）|
| S5 | B | folding_bail | rec_container_kettle_var_folding_bail | `_leg_mesh` L195-210 / `_grip_arch_mesh` L213-229 / `body_to_legs` L375-385 / `legs_to_grip` L398-408 | 两段折叠提梁（2 串联 REVOLUTE）|
| S6 | B | side_loop_handle | rec_container_kettle_var_side_loop_handle | `_carry_loop_solid` L179-230 / `_lug_solid` L153-176 / `loop_pivot` L415-429 | 侧后象限 D 环提把（绕竖直 Z REVOLUTE）|
| S7 | C | screw_cap | rec_container_kettle_var_screw_cap_lid | `_twist_cap_body` L208-262 / `_twist_cap_lug` L265-280 / `cap_twist` L397-406 | 旋拧 / 卡口盖（绕竖直 Z REVOLUTE 拧）|
| S8 | C | sliding_pour_lid | rec_container_kettle_var_sliding_pour_lid | `_lid_dome_solid` L192-213 / `_shutter_plate_solid` L216-241 / `body_to_shutter` L358-369 | 固定圆顶盖 + 月牙挡板横滑（PRISMATIC +Y）|
| S9 | D | trivet_stand | rec_container_kettle_var_trivet_stand | `_trivet_ring_mesh` L188-197 / `_trivet_leg_geometry` L200-204 / `trivet_to_body` L313-321 | 带足铸铁 trivet 托架 root + body 直提（PRISMATIC +Z）|
