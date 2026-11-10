# Container barrel (lidded plastic storage drum / ribbed barrel keg) — Modular Spec

> 来源小类：`picture/Container/Barrel`（articraft_data 上游 Container/Barrel fork-variant pool）。
> 本小类样本池 = 2 parent（蓝色开口储料桶 drum + 蓝色多棱 keg）+ 5 个 converged fork 变体（flip-top / conical / stepped-waisted / scalloped-lobed / top-swing-bail）。全部 5★，逐一读取 `model.py`。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template` 当前 `revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`_barrel_solid` / `_barrel_body` / `_body_mesh` / `_profile_loft` / `_lid_mesh` / `_lid_geometry` / `_lid_disk_geometry` / `lid_lift` / `lid_rotate` / `lid_slide` / `lid_hinge` / `lid_carrier` / `clasp_base` / `ring_swing` / `bail_swing` / `_lug_solid` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_barrel` |
| template path | `agent/templates/Container_Barrel.py` |
| test path (optional) | `tests/agent/test_container_barrel_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + closure + grip；lid / grip 机构挂到 barrel_body 共同 parent；rib/lobe 纹理为模板侧 body-visual 缩放轴，不新增独立关节）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（2 parent + 5 converged fork 变体）|
| read_count | 7（全文逐一读取 model.py：drum parent 372 行 / keg parent 308 行 / flip_top 336 行 / conical 390 行 / clamp_ring→stepped_waisted 271 行 / side_swing→scalloped_lobed 405 行 / top_swing_bail 410 行）|
| read_scope | all 5-star samples in this category（无抽样）|
| source_index_policy | only adopted module sources are indexed below（见 §14）|

各样本贡献：
- **drum parent**（`4e3a36bf`）：`tall_cylindrical_ribbed` body 基线（`_profile_loft` 圆截面 loft + shell + 4 道 rib 环 + rolled rim lip），`lift_off_lid` closure 基线（`lid_lift` PRISMATIC +Z），`swing_buckle_clasp_front` grip 基线（FIXED `clasp_base` + REVOLUTE `ring_swing` U 形锁线）。
- **keg parent**（`b410e9f1`）：`bulged_belly_ribbed` body 基线（`_barrel_body` LatheGeometry 鼓腹 + 7 道 rib tori + threaded neck），`screw_cap` closure 基线（massless `lid_carrier` 解耦 `lid_rotate` CONTINUOUS +Z + `lid_slide` PRISMATIC +Z），`no_grip_flat_badge` grip 基线（无可动 grip，badge/label 内联 body visual）。
- **flip_top**（`flip_top_hinged_lid`）：`flip_top_hinged_lid` closure 候选（`lid_hinge` REVOLUTE +X，后铰翻盖绕 neck 后缘横轴掀开，含 hinge lug ears + pin + 前 latch catch）。
- **conical**（`conical_tapered_body`）：`conical_tapered_body` body 候选（`_taper_r` 线性锥度 + `_barrel_solid` 底宽顶窄 loft，rib 带顺锥面），沿用 drum 的 lift-off lid + swing clasp。
- **clamp_ring**（实为 stepped_waisted）：`stepped_waisted_body` body 候选（`_barrel_solid` 阶梯宽 rib 带 + 中部收腰 waist + `recessed_panel_i` 深色竖向凹纹面板 PANEL_COUNT=8），沿用 lift-off lid；原 clamp/lever 低质量关节已移除。
- **side_swing**（实为 scalloped_lobed）：`scalloped_lobed_body` body 候选（一体化 `_barrel_body` MeshGeometry：`_outer_radius` 用 `cos(LOBE_COUNT·θ)` 调制半径生成圆润竖向波瓣 + 浅凹槽 + `_rib_bump` 融合横向加强带），沿用 keg 的 screw-cap；原侧提梁低质量关节已移除。
- **top_swing_bail**（`top_swing_bail_handle`）：`top_swing_bail_handle` grip 候选（`bail_swing` REVOLUTE +X 单道顶部拱形提梁 `_bail_mesh` + 两侧 `_lug_solid` 钻孔 lug bosses），沿用 drum 的 lift-off lid。

## 核心身份

带盖的塑料储料桶 / 多棱桶（lidded storage drum / barrel keg）：一只直立中空桶体，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)，**明显高于宽**（taller-than-wide，桶身高 ~0.35 m、belly 直径 ~0.25 m）。桶体由 CadQuery `loft`/`shell` 或 SDK `LatheGeometry`/手写 `MeshGeometry` 发射为厚壁中空开口 shell（真实带底封闭、内腔 hollow、顶部可见开口 mouth + threaded/rolled rim），桶身带横向加强环 rib（molded drum stiffening rings）。形态可为近直筒微鼓腹 ribbed drum / 鼓腹 lathe keg / 锥形底宽顶窄 / 阶梯收腰带凹纹面板 / 一体化波瓣 scalloped。桶口上方一只盖按某种机构开合（**主活动语义**）：直提脱卸 lift-off 盖（纯 PRISMATIC +Z）/ 圆形螺旋盖（CONTINUOUS rotate + PRISMATIC slide 经 massless carrier 解耦）/ 后铰翻盖（REVOLUTE +X 绕 neck 后缘）。可选提握机构 grip：前缘 swing-buckle 扣具（FIXED 卡座 + REVOLUTE U 形摆动锁线）/ 顶部 swing bail 提梁（REVOLUTE +X 跨盖摆起摆落）/ 无可动 grip（前贴 badge/label）。默认成熟域：单桶单盖（无嵌套 / 无堆叠 / multiplicity 仅作 body-visual 纹理密度）。

不该混入：细颈高瓶 / 酒瓶（tall narrow neck bottle，归 `container_glass_bottle` / `container_primer_bottle`）、宽口带盖储物罐（wider-than-tall 化妆 / 厨储罐，归 `container_jar`）、金属易拉罐 / 喷雾罐（薄壁拉伸罐，归 `container_can` / `container_paint_spray`）、加压气瓶（带阀门接口，归 `container_gas_cylinder`）、敞口无盖篓筐 / 网格篮（无盖机构 + 透空壁面，归 `container_basket`）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 barrel_body（root）的 mesh 属性（一次发射 shell + rib 环 + neck/rim），不是独立串联 slot。`closure`（盖机构）/ `grip`（提握机构）各自挂到 barrel_body（parallel children）。三轴笛卡尔积构成拓扑多样性（见 §9）。rib/lobe 纹理密度（rib_count / lobe_count）是 body-visual 内联缩放轴，不新增独立关节（见 §8）。

### Slot A：body_form（桶体形态 / 足迹——root barrel_body 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tall_cylindrical_ribbed（基线-drum）| rec_blue-plastic-open-top-storage-drum-with-a-lift-o_…_4e3a36bf | `_profile_loft` L57-67 + `_barrel_solid` L70-111（loft+`faces(">Z").shell(-0.012)`+4 rib 环 L91-99+rolled lip L103-110）| eligible if compatible | 近直筒微鼓腹 loft shell，4 道等距加强环，rolled top rim lip，open-top 中空 |
| bulged_belly_ribbed（基线-keg）| rec_blue-ribbed-plastic-barrel-keg-with-a-round-scre_…_b410e9f1 | `_barrel_body` LatheGeometry L46-74 + `_body_mesh` L77-99（7 道 rib tori L81-93 + 3 道 thread 环 L95-98）| eligible if compatible | 鼓腹 LatheGeometry 桶身（closed=True 含底 + 内腔 + 可见 mouth），7 道横向 rib tori，threaded neck |
| conical_tapered_body | rec_container_barrel_var_conical_tapered_body | `_taper_r` L49-51 + `_barrel_solid` L79-117（loft 底 BASE_R=0.145→顶 TOP_R=0.105 + 4 道顺锥面 rib L96-105）| eligible if compatible | 锥形 loft：底宽顶窄线性锥度，rib 带半径顺锥面递减，lift-off 友配 |
| stepped_waisted_body | rec_container_barrel_var_clamp_ring_lid | `_barrel_solid` L68-116（11 段 loft 阶梯轮廓 + 中部 WAIST_R=0.112 收腰 L78 + 6 道宽窄交替 rib 带 L89-105）+ `recessed_panel_i` 竖向凹纹面板 L149-161（PANEL_COUNT=8 L43）| eligible if compatible | 阶梯式宽 rib 带 + 中部明显收腰 waist + 8 道深色竖向 recessed 面板（固定 body visual，环向复制）|
| scalloped_lobed_body | rec_container_barrel_var_side_swing_bail_handles | `_outer_radius` L97-102 + `_barrel_body` 一体化 MeshGeometry L111-186 + `_lobe_amp` L91-95 + `_rib_bump` L74-89（LOBE_COUNT=10 L48）| eligible if compatible | 一体化非轴对称 mesh：`cos(LOBE_COUNT·θ)` 半径调制生成圆润竖向波瓣 + 浅凹槽 + 融合横向加强带，无贴片棍条 |

硬约束记录：body_form 5 candidate（达 3-6 目标）。全部 loft/lathe/mesh 中空开口腔，taller-than-wide，共享 rib 加强环 + rolled/threaded rim 词汇，只换 footprint / 锥度 / 收腰 / 波瓣调制 / rib 排布。drum 与 keg 各自带不同建模管线（CadQuery loft+shell vs SDK Lathe/手写 mesh），是真实结构家族差异。

### Slot B：closure（**主开合机构槽**——桶盖动作；joint 拓扑差异最大）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| lift_off_lid（基线-drum）| rec_blue-plastic-open-top-storage-drum-with-a-lift-o_…_4e3a36bf | `_lid_mesh` L114-139（domed disc + 下垂 skirt 罩 rim）+ `lid_lift` PRISMATIC L216-224（axis +Z, lower=0 upper=0.05）| eligible if compatible | 直提脱卸盖：单 `lid_lift` PRISMATIC +Z（无旋），下垂裙边从外侧扣住卷边 rim，q=0 坐下 / 正 q 直抬离 |
| screw_cap（基线-keg）| rec_blue-ribbed-plastic-barrel-keg-with-a-round-scre_…_b410e9f1 | `_lid_geometry` L102-119（knurled 螺纹盖 + off-axis molded key）+ massless `lid_carrier` L141-142 + `lid_rotate` CONTINUOUS L160-168 + `lid_slide` PRISMATIC L169-182 | eligible if compatible | 圆形螺旋盖：经 massless `lid_carrier`（无 visual，1e-4 mass），`lid_rotate` CONTINUOUS +Z（旋）+ `lid_slide` PRISMATIC +Z（抬离 neck）；2 joint + 1 massless carrier part；默认 pose 抬起露出 mouth |
| flip_top_hinged_lid | rec_container_barrel_var_flip_top_hinged_lid | `_lid_disk_geometry` L134-172（disk + 后 hinge knuckle + 前 latch tab + 下 seal 环）+ `lid_hinge` REVOLUTE L207-220（axis=(1,0,0) origin=后 rim, lower=0 upper=2.6）；body 侧 hinge lug ears+pin+latch catch L105-129 | eligible if compatible | 后铰翻盖：盖绕 neck 后缘水平 +X 轴 REVOLUTE，q=0 闭合盖座盖 mouth，正 q 上翻 ~149°；非旋脱 |

硬约束记录：closure 3 candidate（达下限 3）。含 PRISMATIC（lift-off）/ CONTINUOUS+PRISMATIC（screw=2 joint + massless carrier）/ REVOLUTE +X（flip）三种不同 joint 拓扑 + 不同 part count（lift-off 1 / screw 2+carrier / flip 1）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。降级理由不适用（已达 3）。

### Slot C：grip（提握 / 把手机构——固定 visual 或活动机构或无）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| no_grip_flat_badge（基线-keg）| rec_blue-ribbed-plastic-barrel-keg-with-a-round-scre_…_b410e9f1 | （前面 badge/label 内联为 body visual，无独立 part/joint；body=`_body_mesh` L77-99 不发射 grip 件）| eligible if compatible | 无可动 grip，前贴标牌（空机构，不发射 grip part）|
| swing_buckle_clasp_front（基线-drum）| rec_blue-plastic-open-top-storage-drum-with-a-lift-o_…_4e3a36bf | `_clasp_base_mesh` L142-159（lever plate + cam block）+ `clasp_mount` FIXED L236-242 + `_clasp_ring_mesh` L162-184（U 形 catch wire）+ `ring_swing` REVOLUTE L254-264（axis +X, lower=0 upper=120°）| eligible if compatible | 前缘扣具：FIXED `clasp_base` 静态卡座 bolt 到前 +Y rim + REVOLUTE `ring_swing` 摆动 U 形锁线（only ring moves，body 不动）；2 part + 1 FIXED + 1 REVOLUTE |
| top_swing_bail_handle | rec_container_barrel_var_top_swing_bail_handle | `_bail_mesh` L175-239（U 形拱形提梁 wire）+ `_lug_solid` L121-146（±X 两侧钻孔 lug bosses，环向复制 inline body visual）+ `bail_swing` REVOLUTE L300-310（axis +X, lower=0 upper=π）| eligible if compatible | 顶部 swing bail：单道拱形提梁绕 ±X 侧 lug 横轴 REVOLUTE，q=0 垂挂桶侧 / 正 q 摆起跨盖 over lid；2 lug visual（inline body）+ 1 REVOLUTE bail part |

硬约束记录：grip 3 candidate（达下限 3）。`no_grip_flat_badge` 是空机构（不发射 grip part）；`swing_buckle_clasp_front` = FIXED+REVOLUTE 复合（front +Y rim）；`top_swing_bail_handle` = REVOLUTE +X（顶部跨盖）。两个活动 grip 的 pivot 位置 / 轴语义 / part tree 不同（front clasp vs top bail），是真实结构差异。

## 槽位图（slot graph）

pattern: parallel_children（barrel_body 为 root，closure / grip 各自挂到它；无 multiplicity 轴，rib/lobe 为 body-visual 纹理）

```
barrel_body(body_form)  [ROOT, 坐地 z=0, taller-than-wide]
   │  (rib 环 / lobe 调制 / recessed_panel_i / badge 均内联为 body visual，无独立 joint)
   │
   ├── closure = lift_off_lid:
   │     barrel_body --[lid_lift: PRISMATIC +Z @ rim top, lower=0 upper=0.05]--> lid
   │
   ├── closure = screw_cap:
   │     barrel_body --[lid_rotate: CONTINUOUS +Z @ neck rim top]--> lid_carrier(massless,无 visual)
   │              lid_carrier --[lid_slide: PRISMATIC +Z, lower=-clearance upper=lid_h]--> lid
   │
   ├── closure = flip_top_hinged_lid:
   │     barrel_body --[lid_hinge: REVOLUTE +X @ 后 rim 边 (0,-NECK_R,NECK_TOP_Z), lower=0 upper=2.6]--> lid
   │
   ├── grip = no_grip_flat_badge:
   │     （空机构：badge/label 内联 barrel_body visual，无 part / 无 joint）
   │
   ├── grip = swing_buckle_clasp_front:
   │     barrel_body --[clasp_mount: FIXED @ 前 +Y rim (0,+R,CLASP_Z)]--> clasp_base
   │              clasp_base --[ring_swing: REVOLUTE +X @ cam block, lower=0 upper=120°]--> clasp_ring
   │
   └── grip = top_swing_bail_handle:
         barrel_body --[bail_swing: REVOLUTE +X @ ±X lug pivot (0,0,LUG_Z), lower=0 upper=π]--> bail_handle
              （±X lug bosses _lug_solid 内联 barrel_body visual）
```

接口点位与 joint 语义：
- **lift-off 接口**：`lid_lift` origin 落在 rim top 中心 `(0,0,LID_Z≈RIM_Z-0.002)`，axis +Z PRISMATIC（无旋），q=0 盖坐 rim / 正 q 直抬离 ~0.05。盖 skirt 从外侧罩卷边 rim 是 captured / 友配。
- **screw 接口**：`lid_rotate` origin 落在 neck rim top 中心 `(0,0,RIM_TOP_Z)`，axis +Z（CONTINUOUS）；`lid_slide` 经 massless `lid_carrier`（无 visual），axis +Z（PRISMATIC，q=0 在 LID_REST_CLEARANCE 抬起露 mouth，下滑罩 neck）。carrier 解耦旋转 / 平移共享 +Z。
- **flip 接口**：`lid_hinge` origin 在 neck 后缘 `(0, -NECK_RADIUS, NECK_TOP_Z)`，axis +X，REVOLUTE 闭合 q=0 盖座 / 上翻正 q ~149°；body 侧需发射 hinge lug ears + pin + 前 latch catch（inline body visual）。
- **clasp 接口**：`clasp_mount` FIXED origin 在前 +Y rim 桶面（`(0, +body_R_at_z, CLASP_PIVOT_Z)`，随 body_form 半径派生）；`ring_swing` REVOLUTE origin 在 cam block 内（clasp-local），axis +X，U 形 wire 摆起（only ring moves，clasp_base 静止）。
- **bail 接口**：`bail_swing` REVOLUTE origin 在 ±X 两侧 lug pivot 连线中点 `(0,0,LUG_Z≈RIM_Z-0.044)`，axis +X，q=0 提梁垂挂桶侧 / 正 q 摆起跨盖 over lid；±X lug bosses（`_lug_solid` 钻孔）inline body visual。
- **mating policy**：盖 skirt 罩 over rim / 盖 hinge knuckle 抱 pin / bail wire 入 lug bore / clasp ring leg 入 cam block 均为 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 rim / hinge / lug 硬件）+ element-scoped `allow_overlap` 守 overlap（见各 parent/变体 run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有盖 q=0 闭合 / 坐下（screw 盖例外：默认抬起 LID_REST_CLEARANCE 露 mouth，配 `allow_isolated_part`）；clasp ring / bail 提梁 q=0 垂挂。lid 抬升 / 旋转 / 翻起、ring / bail 摆起为 viewer 目检的活动语义。
- **互斥 / 可选**：`grip=no_grip_flat_badge` 是空机构（不发射 grip part）；closure 各候选互斥（一次只一种盖）；grip 各候选互斥（一次只一种提握）。`lid_carrier` massless part 仅在 screw_cap 候选发射。

## 每槽位 Module Emits / Interfaces

### Slot A / barrel_body（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_body`(root visual: `barrel_shell` open-top 中空 shell + rib 环 + neck/rolled rim[ + recessed_panel_i / badge / lug bosses 内联 visual]) | drum `_barrel_solid` L70-111 / keg `_barrel_body`+`_body_mesh` L46-99 / conical `_barrel_solid` L79-117 / stepped `_barrel_solid`+panel L68-161 / scalloped `_barrel_body` L111-186 |
| internal joints | 无（root 桶体本身无活动件；rib/lobe/panel/badge 全内联 visual）| — |
| upstream interface | 坐地 z=0（root）| — |
| downstream interface | rim top 中心 `(0,0,RIM_Z/RIM_TOP_Z)`（closure joint 的 parent 接口）+ neck 后缘（flip hinge）+ 前 +Y rim 桶面（clasp）+ ±X lug（bail）| drum RIM_Z L40 / keg RIM_TOP_Z L36 |

### Slot B / closure（每候选发射对应活动盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（lift-off / flip）/ `lid`+`lid_carrier`(massless)（screw）| drum `_lid_mesh` L114-139 / keg `_lid_geometry`+carrier L102-142 / flip `_lid_disk_geometry` L134-172 |
| internal joints | `lid_lift` PRISMATIC +Z（lift-off）/ `lid_rotate` CONTINUOUS +Z + `lid_slide` PRISMATIC +Z（screw）/ `lid_hinge` REVOLUTE +X（flip）| drum L216-224 / keg L160-182 / flip L207-220 |
| upstream interface | rim top 中心（lift-off/screw）/ neck 后缘 hinge（flip）| 各 closure 源 |
| downstream interface | 无（盖为链末端活动件）| — |

### Slot C / grip（≠no_grip 时发射 grip 机构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（no_grip）/ `clasp_base`+`clasp_ring`（front clasp）/ `bail_handle`(+ ±X lug 内联 body visual)（top bail）| clasp `_clasp_base_mesh`+`_clasp_ring_mesh` L142-184 / bail `_bail_mesh`+`_lug_solid` L121-239 |
| internal joints | 无（no_grip）/ `clasp_mount` FIXED + `ring_swing` REVOLUTE +X（front clasp）/ `bail_swing` REVOLUTE +X（top bail）| clasp L236-264 / bail L300-310 |
| upstream interface | 前 +Y rim 桶面（clasp）/ ±X lug pivot（bail）| 各 grip 源 |
| downstream interface | 无（grip 为链末端活动件）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | tall_cylindrical_ribbed / bulged_belly_ribbed / conical_tapered_body / stepped_waisted_body / scalloped_lobed_body | tall_cylindrical_ribbed | choice | deterministic procedural sampler 选 | module table |
| closure | enum | lift_off_lid / screw_cap / flip_top_hinged_lid | lift_off_lid | choice | sampler 选 | module table |
| grip | enum | no_grip_flat_badge / swing_buckle_clasp_front / top_swing_bail_handle | no_grip_flat_badge | choice | sampler 选；含空机构 | module table |
| palette_style | enum | 见 §palette_style（9 个 colorway，各含显式 finish）| industrial_blue_black | palette | palette only（含 finish 维度），**不计入 slot_choice** | palette |
| rib_count | int | [3, 16] | 7 | independent(N) | body rib 环 / 加强带数量，整数采样后 clamp；body visual 内联 | §8 |
| lobe_count | int | [8, 14] | 10 | conditional(N) | 仅 `scalloped_lobed_body` 用；`_outer_radius` 的 `cos(N·θ)` 调制；其它 body 忽略 | §8 / scalloped L48 |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放桶高 BARREL_H → RIM_Z/RIM_TOP_Z → lid mount 高度，clamp（保 taller-than-wide）| resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放桶半径 / belly R → neck R / rim R 同比，clamp（保盖罩 / hinge / lug 配合）| resolve clamp |
| neck_radius_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；lid bore / cap skirt / hinge_Y 半径派生跟随 | resolve clamp |
| lid_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放盖高 / skirt 深 / disc 厚，clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lid_lift / lid_slide 行程 + hinge / ring_swing / bail_swing limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`lid_skirt_R ≥ rim_R + clearance` 且 `lid_skirt_R ≤ body_R + proud`；clasp/bail/hinge 硬件 origin 落在缩放后 body 表面；违反按比例回缩 lid_height/neck/radius scale 或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 高宽比保形：`BARREL_H·height_scale > belly_diameter·radius_scale + 0.05`（保桶 taller-than-wide 类别身份），违反时回缩 radius_scale | 类别 identity |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（lid bore / cap skirt / flip hinge_Y 半径跟随 neck 半径，保盖罩 / 翻盖配合不破）。`rib_count` 为 independent 整数 N，`lobe_count` 为 conditional 整数 N（仅 scalloped 解析）。scale / N 只动安全比例 / clearance / 纹理密度，绝不改 body_form / closure / grip 的拓扑。

### palette_style（colorway，9 个，6 源自 5★ 实测材质 + 3 realistic-for-the-class 推断）

每 colorway = 一组协调配色（body + lid/cap + grip/accent[ + recessed_panel/label]）**外加一个 finish 描述子**。`finish` 是 palette 内显式材质-表面维度（**非独立 slot / 非 slot_choice**），决定模板侧 material 的 metallic / roughness / 漆面外观；取值域 `{satin_molded_plastic, glossy_molded_plastic, matte_molded_plastic, food_grade_hdpe, painted_steel_drum, galvanized_steel, weathered}`。颜色键沿用各源 `model.py` 实测 material 名 / rgba；新增 3 色族为该类目（工业储桶 / painted-steel 钢桶 / 食品级 HDPE）realistic-for-the-class 推断，保持物理可信（塑料不荧光、金属镀锌 / 漆面真实）。

| palette_style | finish | body | lid / cap | grip / accent | 来源样本 |
|---|---|---|---|---|---|
| industrial_blue_black（基线）| satin_molded_plastic | `drum_blue` (0.16,0.36,0.72) | `lid_black` (0.09,0.09,0.10) | `clasp_black` (0.12,0.12,0.13) | drum parent L190-192 |
| keg_blue_black | glossy_molded_plastic | `barrel_blue` (0.16,0.34,0.78) | `cap_black` (0.10,0.10,0.11) | — | keg parent L130-131 |
| stepped_two_tone_blue | satin_molded_plastic | `drum_blue` (0.15,0.34,0.70) | `lid_black` (0.09,0.09,0.10) | `recessed_panel_blue` (0.08,0.20,0.46) 深色凹纹 | stepped L136-138 |
| scalloped_deep_blue | glossy_molded_plastic | `barrel_blue` (0.14,0.32,0.74) | `cap_black` (0.10,0.10,0.11) | — | scalloped L225-226 |
| zinc_bail_blue | satin_molded_plastic | `drum_blue` (0.16,0.36,0.72) | `lid_black` (0.09,0.09,0.10) | `bail_zinc` (0.55,0.55,0.52) 镀锌提梁 | top_bail L247-249 |
| green_drum_black（变体色族，工业储桶常见）| matte_molded_plastic | green (0.18,0.45,0.24) | `lid_black` (0.09,0.09,0.10) | `clasp_black` (0.12,0.12,0.13) | 排除项列出的 color 轴（蓝/黑/绿/锈）→ 模板侧 palette；以 blue 族为主、green 族为 minority |
| food_grade_hdpe_blue（推断：食品级 HDPE 储料桶）| food_grade_hdpe | `hdpe_blue` (0.20,0.42,0.78) 亮蓝食品级 HDPE | `cap_white` (0.90,0.90,0.88) 白螺旋盖 | `clasp_blue` (0.16,0.34,0.70) 同色扣具 | inferred-for-class（蓝族延伸；食品级桶常见亮蓝桶身 + 白盖）|
| safety_red_drum（推断：painted-steel 警示红钢桶）| painted_steel_drum | `drum_red` (0.62,0.13,0.11) 漆面红钢 | `lid_red` (0.55,0.11,0.10) 同漆深红盖 | `ring_zinc` (0.55,0.55,0.52) 镀锌锁环 / 扣具 | inferred-for-class（工业 painted-steel 危化 / 油桶警示红，金属漆面）|
| galvanized_steel_keg（推断：裸镀锌钢桶 / keg）| galvanized_steel | `steel_zinc` (0.66,0.67,0.64) 镀锌钢桶身 | `cap_steel` (0.58,0.59,0.57) 钢盖 | `bail_zinc` (0.55,0.55,0.52) 镀锌提梁 | inferred-for-class（裸金属镀锌钢桶 spangle 灰，无漆）|

> palette_style 每 seed 采样（`rng.choice(PALETTE_STYLES)`），保证 swept 输出 color-diverse；**仍为 palette-only，不计入 slot_choice、不改任何 slot / candidate / multiplicity / joint / dimension / topology**。`finish` 仅作 palette 内显式材质-表面维度（驱动模板侧 material 的 metallic/roughness/漆面外观），不引入新关节 / 新件 / 新拓扑等价类。zinc_bail / galvanized 的 `bail_zinc` 仅在 grip=top_swing_bail_handle 时 accent 生效，safety_red 的 `ring_zinc` 仅在 grip 发射锁环 / 扣具时生效，stepped_two_tone 的 `recessed_panel_blue` 仅在 body=stepped_waisted_body 时生效（其它 body / grip 该色键不发射，无副作用）。painted_steel_drum / galvanized_steel / food_grade_hdpe 的金属 / HDPE finish 仅改材质外观，桶身仍为既有 loft/lathe/mesh shell 几何（不改 body_form 拓扑、不破 taller-than-wide 身份）。

## Multiplicity / Copy Logic

本小类有 **2 根 body-visual 纹理 N 轴**（均内联为 body mesh，不新增独立 part / joint），无独立活动件 multiplicity：

**轴 1：rib_count（横向加强环 / 加强带数量）**
- `count_param`: `rib_count`
- `N_range`: [3, 16]（产品域；测试偏小 N=3-7，产品全程到 16）
- sampling domain: 加权（小 N 高频：N∈[4,8] ~70%；大 N∈[9,16] 稀有 ~30%）；drum=4 环 / keg=7 tori / stepped=6 带覆盖中段
- copied object: 横向 rib 环 / tori / 融合加强带（drum `cq` ring union L91-99 / keg `TorusGeometry` rib L81-93 / stepped rib 带 L89-105 / scalloped `_rib_bump` L74-89）
- naming: rib 内联 body mesh，不暴露独立 visual 名（merge/union 进 `barrel_shell`）
- placement: 沿桶身 z 等距 / 按 body_form 轮廓半径贴合（每环半径跟随 `_profile_radius`/`_taper_r`）
- joint policy: 全部内联 body visual，**不新增独立关节**
- source/gating: 全 body_form 适用；环数只改 body mesh 纹理密度，不改拓扑等价类（不进 slot_choices 的 topology family，仅作连续 N）

**轴 2：lobe_count（一体化波瓣调制阶数）**
- `count_param`: `lobe_count`
- `N_range`: [8, 14]（产品域；scalloped 基线 N=10）
- sampling domain: 加权（N∈[8,12] 高频，N∈[13,14] 稀有）
- copied object: 无实体复制；`_outer_radius` 的 `cos(LOBE_COUNT·θ)` 半径调制阶数（scalloped L97-102, L48）
- naming: 内联 body mesh，无独立名
- placement: 环向调制（θ ∈ [0,2π)），envelope 限定 belly 段（`_lobe_amp` L91-95）
- joint policy: 无关节
- source/gating: **conditional**——仅 `body_form=scalloped_lobed_body` 时生效；其它 body 忽略 lobe_count（resolve 前按上游 body choice 解析）

> 原 `side_handle_count` 已删除（避免为低质量 handle 关节铺 N）。两 N 轴均不进 `slot_choices` 的 topology distinct 计数（它们只改 body mesh 纹理密度，不改拓扑等价类）；主多样性由 body_form × closure × grip 提供（见 §9）。

## 拓扑多样性审计

总组合数：body_form(5) × closure(3) × grip(3) = **45**（rib_count / lobe_count 为 body-visual 纹理 N，不计入 topology distinct）。

仅 body_form × closure = **15 ≥ 10** 已可过门控；叠 grip 后充裕（45）。

理由：本类拓扑多样性来源充裕——body_form(5) × closure(3) 的笛卡尔积即 15 distinct，远超 10；closure 引入 PRISMATIC（lift-off 1 joint）/ CONTINUOUS+PRISMATIC（screw 2 joint + massless carrier）/ REVOLUTE +X（flip 1 joint）三种不同 joint 拓扑 + 不同 part count；grip 引入空机构（no_grip）/ FIXED+REVOLUTE（front clasp 2 part）/ REVOLUTE +X（top bail 1 part + ±X lug）三种不同提握拓扑。三轴 part tree / joint count / chain depth 真实不同。叠加后 45 distinct，slot_choices 编入三轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 gating 见下），再加权采样 rib_count / lobe_count（conditional）、uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 派生非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 45（45 组合的采样空间足够覆盖）。低于 300 的原因：本小类真实结构词汇就是 5 body × 3 closure × 3 grip = 45，是该类目（带盖塑料储桶，盖机构 3 种、提握 3 种）的合理上限，不强行注水；rib/lobe N 在 body-visual 层另提供连续视觉多样性但不改拓扑等价类。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / neck_radius / lid_height / joint_travel）+ 2 个 N（rib_count / lobe_count）。全部 `resolve_config` clamp / 派生 + 每 build 统一应用。`neck_radius_scale` 为 equation（lid bore / cap skirt / flip hinge_Y 半径派生跟随）。盖罩配合 + 高宽比保形不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale / N 不破坏 closure joint origin（rim top / neck 后缘 hinge）、grip 硬件 origin（前 rim clasp / ±X lug）、盖罩配合、taller-than-wide 类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），再加权 rib_count / lobe_count(conditional) + uniform 各 scale + palette_style | slot_choices_for_seed 含三轴且与 build 一致 |
| compatibility matrix | (1) `flip_top_hinged_lid` + `top_swing_bail_handle` 共存时：bail 摆起跨盖 over lid，hinge 在 neck 后缘——两者 pivot 不同侧（bail ±X / hinge -Y），正交可共存，但 resolve 派生 bail GRIP_REACH 避开翻起的盖；不 gate-out。(2) `swing_buckle_clasp_front` 在 +Y rim、`flip_top_hinged_lid` hinge 在 -Y rim、latch 在 +Y rim——clasp 与 flip latch 同在 +Y，resolve 把 clasp 下移到 belly（CLASP_PIVOT_Z 低于 latch）避让；不 gate-out。(3) `lobe_count` 仅 `scalloped_lobed_body` 解析，其它 body 忽略（conditional）。(4) `screw_cap` 默认抬起露 mouth → 配 `allow_isolated_part(lid)`。(5) 各 closure 互斥、各 grip 互斥。(6) clasp 在前 +Y 桶面，origin Y 随 body_form 半径在 resolve 派生（drum 0.118 / conical `_taper_r(CLASP_Z)` / 各 body 表面），避免悬空。无硬 gate-out（45 组合全合法，只在 resolve 派生尺寸 / 位置适配）| 无 floating / collision / lid 穿桶 / grip 漂移 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale + 2 个 clamped N，每 build 统一；neck_radius equation 驱动 lid bore / hinge_Y | 比例 / 纹理变化不破坏 closure/grip joint origin / 盖罩配合 / 坐地 / taller-than-wide 身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | lid 动作 / grip 摆动 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 5 | yes | yes | loft/lathe/mesh 桶体五族（直筒 / 鼓腹 / 锥形 / 收腰带凹纹 / 波瓣）|
| closure | 3 | yes | yes | lift-off(PRIS) / screw(CONT+PRIS+carrier) / flip(REV X) |
| grip | 3 | yes | yes | no_grip 空 / front clasp(FIXED+REV) / top bail(REV X) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, closure, grip) 三轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 lid bore / cap skirt / flip hinge_Y；盖罩配合 + 高宽比保形不等式在 resolve 内投影 / 回缩；rib_count clamp 到 [3,16]；lobe_count conditional 仅 scalloped 解析 clamp 到 [8,14]
- compatibility matrix / gating：45 组合全合法（无硬 gate-out），clasp Y / bail GRIP_REACH / flip latch 位置按 body_form 半径在 resolve 派生避让
- 连续 scale / N clamp 后不破坏 closure/grip joint origin / 盖罩配合 / 坐地 / taller-than-wide 身份
- 关键 joint：lift-off `lid_lift` PRISMATIC +Z (abs(axis[2])>0.99)；screw `lid_rotate` CONTINUOUS +Z + `lid_slide` PRISMATIC +Z + massless `lid_carrier`（无 visual）；flip `lid_hinge` REVOLUTE +X (abs(axis[0])>0.99) origin 在 neck 后缘 (y<-NECK_R+ε, z≈NECK_TOP_Z)；front clasp `clasp_mount` FIXED + `ring_swing` REVOLUTE +X（only ring moves，clasp_base 静止）；top bail `bail_swing` REVOLUTE +X origin 在 ±X lug 连线中点
- captured-fit：element-scoped `allow_overlap`——lift-off/flip lid skirt/knuckle ↔ barrel_shell（罩 rim / 抱 pin）；screw cap skirt ↔ barrel_shell（罩 neck，配 `allow_isolated_part`）；clasp_base ↔ barrel_shell（riveted 前壁）+ clasp_ring ↔ clasp_base（legs 入 cam block）；bail_wire ↔ lug_i（legs 入 bore）
- grandfather：所有 captured-fit 省略 MatingContract，由 `fail_if_articulation_origin_far_from_geometry`（origin 落真实 rim/hinge/lug 硬件）+ allow_overlap 守

## Reject cases

- 用 boxy 占位体（纯 Box）当圆桶 body → 失类别身份；圆 body 必须 loft/lathe/调制 mesh，禁止裸 Box。
- 桶做成 wider-than-tall（矮胖）→ 出 jar 语义；必须保 taller-than-wide（高宽比不等式 FAIL 时回缩 radius_scale）。
- 桶做成细颈高瓶（tall narrow neck，neck 占主体）→ 出 bottle 语义；barrel 是宽桶身 + 短 neck/rim。
- closure joint origin 放在桶底 / 任意点而非 rim top / neck 后缘 hinge 真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- screw 盖不用 massless carrier 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 lid 单 part → 旋转与抬升耦合错误（应 body→carrier→lid 两 joint）。
- front clasp 把 clasp_base 也设成活动（应只有 ring_swing 动，clasp_base FIXED 静止）→ 与 parent 语义不符。
- grip / closure rest pose 设成张开 / 抬起而非 q=0 闭合（screw 默认抬起露 mouth 除外，需配 allow_isolated_part）→ current-pose 与 viewer 目检不符。
- 给盖罩 / hinge knuckle / bail bore / clasp captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把 color/material / 纯尺寸缩放 / rib 密度当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，rib_count/lobe_count 是 body-visual N，均不计 slot_choice）。
- 把透明展示桶 / 网格篓筐壁面 / 底部排液阀 spigot 塞回 body_form → 超出 Barrel 实心封闭桶真实形态 / 未排格（按排除项不立轴）。
- lid 抬升 / flip / bail 摆起时穿桶壁 / origin 漂移 → 盖罩配合 / 高宽比不等式或 origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_glass_bottle / container_primer_bottle 细颈瓶**（tall narrow neck，neck 占主体）——理由：bottle 是细长瓶身 + 长颈倒料，barrel 是宽桶身 + 短 rim 开口储料。
- 不该混入：**container_jar 宽口储物罐**（wider-than-tall 化妆 / 厨储罐）——理由：jar 矮胖宽口，barrel 高瘦带 rib 加强环，是工业储桶身。
- 不该混入：**container_can / container_paint_spray 金属罐 / 喷雾罐**（薄壁拉伸金属罐 + 喷头）——理由：barrel 是厚壁塑料储桶 + 可开合盖，无喷头 / 拉环。
- 不该混入：**container_gas_cylinder 加压气瓶**（带阀门 / 调压接口）——理由：barrel 顶部是储料桶盖机构，非阀门。
- 不该混入：**container_basket 敞口篓筐 / 网格篮**（无盖机构 + 透空壁面 + 提把）——理由：barrel 是带盖封闭实心桶身。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。7 个 5★ 全读（2 parent + 5 变体）。5 body × 3 closure × 3 grip = 45 combos；body×closure=15 clears 。closure 三种 joint 拓扑（lift-off PRIS / screw CONT+PRIS+carrier / flip REV X）；grip 三种（no_grip 空 / front clasp FIXED+REV / top bail REV X）；rib_count[3,16] + lobe_count[8,14](conditional) 为 body-visual N 不计 topology；palette_style 9 色族（6 源自 5★ 实测 + 3 realistic-for-class 推断：food_grade_hdpe_blue / safety_red_drum / galvanized_steel_keg；蓝塑料族为主 + green/red/galvanized 变体），各 colorway 含显式 finish 维度（satin/glossy/matte molded plastic / food_grade_hdpe / painted_steel_drum / galvanized_steel / weathered），palette-only 不计 slot_choice / 不改 slot / joint / dimension / topology。无活动件 multiplicity 轴。低质量 side_handle / clamp-lever 关节已在上游移除。|

## 模板实现备注（可选）
- 共享 helper：`_profile_loft(sections)`（CadQuery 圆截面 loft）+ `_lathe_body(profile)`（SDK LatheGeometry）+ `_scalloped_mesh(lobe_count, rib_count)`（手写调制 MeshGeometry）三套 body 管线按 body_form 分发；`_rolled_rim_lip` / `_thread_rings` / `_rib_ring(z,r)` 公用。drum/conical/stepped 用 CadQuery loft+shell；keg 用 LatheGeometry；scalloped 用手写 mesh radius 调制。
- screw_cap：必须经 massless `lid_carrier`（无 visual，1e-4 mass Box inertial）解耦 `lid_rotate`(CONTINUOUS +Z)→`lid_slide`(PRISMATIC +Z)；默认 pose lid 抬起 LID_REST_CLEARANCE 露 mouth，配 `ctx.allow_isolated_part(lid)`。
- flip_top：body 侧需发射 hinge lug ears + pin + 前 latch catch（inline body visual，L105-129 drum-keg 复用 keg 轮廓）；`lid_hinge` origin 在 `(0, -NECK_R, NECK_TOP_Z)`。
- front clasp：`clasp_base` FIXED（不动），仅 `clasp_ring` 经 `ring_swing` REVOLUTE +X 动；clasp_mount origin Y 随 body_form 表面半径在 resolve 派生。
- top bail：±X `_lug_solid` 钻孔 lug 内联 body visual；`bail_swing` origin 在 lug 连线中点；GRIP_REACH 在 resolve 按 belly 半径 + 翻盖避让派生。
- captured-fit overlap：`run_container_barrel_tests` 里逐 closure/grip 声明 element-scoped `allow_overlap`（lid skirt↔barrel_shell / hinge knuckle↔barrel_shell / cap skirt↔barrel_shell / clasp_base↔barrel_shell / clasp_ring↔clasp_base / bail_wire↔lug_i），见各源 run_tests。
- neck_radius equation：`resolve_config` 派生 `lid_bore_R = NECK_R + clearance`、`cap_skirt_R = rim_R + proud`、`hinge_Y = -NECK_R`，盖罩 / 翻盖配合不等式在 resolve 投影；高宽比保形不等式守 taller-than-wide。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类、parallel_children、body × closure × seal 三轴、massless carrier screw-cap、captured-fit allow_overlap + grandfather 骨架——最近相邻参考）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | tall_cylindrical_ribbed + lift_off_lid + swing_buckle_clasp_front | rec_…_4e3a36bf（drum parent）| `_profile_loft` L57-67 / `_barrel_solid` L70-111 / `_lid_mesh` L114-139 / `lid_lift` L216-224 / `_clasp_base_mesh` L142-159 / `clasp_mount` L236-242 / `_clasp_ring_mesh` L162-184 / `ring_swing` L254-264 | 直筒 ribbed body 基线 + lift-off PRISMATIC 盖 + 前缘 FIXED+REVOLUTE 扣具 |
| S2 | A/B/C | bulged_belly_ribbed + screw_cap + no_grip_flat_badge | rec_…_b410e9f1（keg parent）| `_barrel_body` LatheGeometry L46-74 / `_body_mesh` L77-99 / `_lid_geometry` L102-119 / `lid_carrier` L141-142 / `lid_rotate` L160-168 / `lid_slide` L169-182 | 鼓腹 lathe body + massless carrier screw-cap + 无 grip badge 基线 |
| S3 | B | flip_top_hinged_lid | rec_container_barrel_var_flip_top_hinged_lid | `_lid_disk_geometry` L134-172 / `lid_hinge` REVOLUTE axis=(1,0,0) L207-220 / hinge lug+pin+latch L105-129 | 后铰翻盖（REVOLUTE +X @ neck 后缘）|
| S4 | A | conical_tapered_body | rec_container_barrel_var_conical_tapered_body | `_taper_r` L49-51 / `_barrel_solid`(taper) L79-117 | 锥形底宽顶窄 body |
| S5 | A | stepped_waisted_body | rec_container_barrel_var_clamp_ring_lid | `_barrel_solid`(stepped waist) L68-116 / `recessed_panel_i` L149-161 / PANEL_COUNT L43 | 阶梯收腰 body + 竖向 recessed 凹纹面板 |
| S6 | A | scalloped_lobed_body | rec_container_barrel_var_side_swing_bail_handles | `_outer_radius` L97-102 / `_barrel_body`(一体化 mesh) L111-186 / `_lobe_amp` L91-95 / `_rib_bump` L74-89 / LOBE_COUNT L48 | 一体化波瓣调制 body（cos(N·θ) 半径调制）|
| S7 | C | top_swing_bail_handle | rec_container_barrel_var_top_swing_bail_handle | `_bail_mesh` L175-239 / `_lug_solid` L121-146 / `bail_swing` REVOLUTE axis=(1,0,0) L300-310 | 顶部拱形提梁（REVOLUTE +X @ ±X lug）+ 钻孔 lug bosses |
