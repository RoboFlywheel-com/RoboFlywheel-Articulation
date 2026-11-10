# hair_dryer — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `hair_dryer` |
| 大类 / 小类 | `Bathroom` / `Hair dryer` |
| picture 小类目录 | `picture/Bathroom/Hair dryer/` (articraft_data) |
| source map | `articraft_data/picture_expansion/template_source_maps/Bathroom__Hair dryer.md` |
| parent record_id | `rec_pink-compact-hair-dryer-with-a-detachable-rotata_20260605_144857_361026_8f70ba30` |
| parent picture | `picture/Bathroom/Hair dryer/001.png` |
| template path | `agent/templates/Bathroom_Hair_dryer.py` |
| test path (optional) | `tests/agent/test_hair_dryer_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：三个 slot 都挂到同一根 `body`（barrel + handle 壳体）这个共同 root（`parallel_children`），但 Slot B 的 `folding_travel_handle` 候选会把 handle 从 root 里拆出来变成一个独立 REVOLUTE 子件并把 switches/cord 改父到 handle（`linear_chain` 局部）。没有模板级同构 multiplicity（fingers/teeth/ribs 是 slot 内部局部重复 visual）。

---

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (1 parent + 7 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

### 共同结构（全部 8 个样本）
- 坐标系：barrel 轴沿 +X（前/喷嘴在 +X，后/进风在 −X），barrel 中心线 z=0，handle 朝下 −Z。
- root part `body`：`_barrel_solid()`（outer loft − inner loft 的中空开口壳）∪ `_handle_solid()`（XY workplane 多段 rect loft 的渐缩握把）。barrel section 半径 0.037→0.042→0.040→0.033→0.030，front lip 在 x≈0.175。
  - 来源：parent `_barrel_solid` model.py:L52-L73、`_handle_solid` L76-L88；7 个变体逐字相同（如 comb L52-L88、twist L52-L88、hinged L52-L88、wide L52-L88、loop L66-L118 handle 重写、folding L57-L101 handle 重写）。
- 前喷嘴：单个 part，CONTINUOUS 关节 `barrel_to_nozzle`（或 `barrel_to_diffuser`），axis=(1,0,0)，origin=(NOZZLE_MOUNT_X=0.163,0,0)，effort=0.5/velocity=6.0；back rim 故意 overlap barrel front lip（`expect_overlap axes="x" min_overlap=0.006`）。
- 两个滑动开关 power/heat：PRISMATIC，axis=(1,0,0)，lower/upper=∓0.007，origin 在 handle +Y 面的 switch housing 上（parent origin (0.060,0.0205,sz)）。
- 电源线 + 插头：单根 `tube_from_spline_points` 下垂软管 + strain-relief sleeve + plug box + 两根 pin，FIXED 关节到 body（folding 变体改 FIXED 到 handle）。
- 三种材质恒定：`shell_pink`(0.96,0.71,0.78)、`dark_gray`(0.24,0.24,0.26)、`switch_gray`(0.32,0.32,0.34)。

### 各样本差异（真正的拓扑/接口轴）
- **Slot A 喷嘴**：concentrator(parent)=圆背→扁矩形 slot 中空；diffuser=碗形壳+穿孔面板+10 根 capsule finger 局部循环；comb=短圆领→窄 slit duct + lip rail + 11 颗 tooth 局部循环；wide_smoothing=圆领→很宽扁 slit + 四条 lip 框边。四者共享同一 CONTINUOUS spin 接口，只换喷嘴 part 的 mesh 与局部重复 visual。
- **Slot B 握把**：pistol(parent)=固定握把（switches/cord 直接挂 body，handle 是 body 壳的一部分）；folding=**新增 `handle` part + REVOLUTE `body_to_handle` 铰链**（axis=(0,−1,0)，lower=0 locked-open，upper=1.5），switches 改父到 handle（`handle_to_*`），cord 改 FIXED 到 handle，body 上多了 hinge_barrel + lock_tab visual；open_loop=body 融合的开环框握把（椭圆 cutout）+ 独立 switch_shelf 面板，switches 仍挂 body。
- **Slot C 后进风**：radial_fixed_grille(parent)=body 上的固定 cap+三圈 torus 肋（纯 visual，无关节）；twist_ring=**新增 `rear_grille` part + REVOLUTE `body_to_rear_grille`**（bayonet 旋拧，axis=(1,0,0)，lower=0 upper=1.05）+ body 上 `bayonet_ring` 接收环 visual；hinged_lint_screen=**新增 `lint_screen` part + REVOLUTE `body_to_lint_screen`**（flip-open，axis=(0,1,0)，lower=0 upper=1.5）+ body 上两个 `hinge_knuckle_i` visual。

---

## 核心身份

紧凑型手持电吹风（hand-held hair dryer）。物理本体 = 一根沿轴向气流的 **barrel 风筒**（前端出风口、后端进风格栅）+ 一个从 barrel 下方伸出的 **握把**（带两个风量/温度滑钮）+ 一根 **电源线和插头**。默认成熟域：barrel 长 ≈0.175m、握把高 ≈0.06–0.12m 的桌面级小家电比例。三个可替换功能层：**前喷嘴附件**（concentrator / diffuser / comb / smoothing）、**握把形态**（pistol / folding / open-loop）、**后进风/滤网**（fixed grille / twist-ring / hinged screen）。

唯一一定存在的运动语义：前喷嘴绕 barrel 轴 CONTINUOUS 旋转 + 两个 PRISMATIC 滑钮。Slot B/C 的某些候选额外引入 REVOLUTE 铰链。

不该混入：纯造型/配色/比例变化（不构成 slot）、台式/壁挂吹风机支架、风扇/暖风机等无握把无喷嘴附件的送风设备。

---

## 槽位 + 候选模块表

### Slot A：nozzle_attachment（barrel 前端出风附件，CONTINUOUS spin）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| concentrator_nozzle | rec_pink-compact-hair-dryer-with-a-detachable-rotata_20260605_144857_361026_8f70ba30 | L91-L109 (`_nozzle_mesh`) + L146-L160 (part+joint) | eligible if compatible | 圆背→扁矩形 slot 的中空集风嘴（outer loft − inner loft）；rest 时 slot 横向（dy>dz）；单 visual `nozzle_shell`，无局部重复 |
| diffuser_nozzle | rec_hair_dryer_var_diffuser_nozzle | L101-L168 (`_diffuser_bowl_solid`+`_finger_mesh`) + L205-L235 (part+joint) | eligible if compatible | 圆碗壳 + 穿孔面板 + `N_FINGERS=10` 根 capsule finger（局部循环 `finger_{i}`，环形 FINGER_RING_R=0.036）；bowl 近圆（dy≈dz） |
| comb_pick_nozzle | rec_hair_dryer_var_comb_nozzle | L91-L129 (`_comb_nozzle_body`+`_comb_lip_rail`+`_make_tooth`) + L165-L196 (part+joint) | eligible if compatible | 短圆领→窄 slit duct + lip rail + `num_teeth=11` 颗向下圆柱 tooth（局部循环 `tooth_{i}`，沿 Y 等距 −0.021..0.021） |
| wide_smoothing_nozzle | rec_hair_dryer_var_wide_smoothing_nozzle | L91-L154 (`_nozzle_mesh`+`_slit_lip_mesh`) + L191-L206 (part+joint) | eligible if compatible | 圆领→很宽很扁 slit（outlet_w=0.104, outlet_h=0.018）+ 四条 box lip 框边（圆角）；rest 时 dy>0.095 且 dy>1.5·dz |

### Slot B：handle_grip（barrel 下方握把结构 + 开关承载）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pistol_handle | rec_pink-compact-hair-dryer-with-a-detachable-rotata_20260605_144857_361026_8f70ba30 | L76-L88 (`_handle_solid`) + L119-L140 (body fuse + switch_housing) + L162-L180 (switches on body) | eligible if compatible | 固定手枪握把，与 barrel 壳融合在 `body` 里；switch_housing 在 +Y 面；两滑钮 PRISMATIC 直接挂 body；cord FIXED 挂 body。无额外活动件 |
| folding_travel_handle | rec_hair_dryer_var_folding_handle | L80-L101 (`_handle_solid` 带 hinge ear) + L210-L242 (`handle` part + `body_to_handle` REVOLUTE) + L185-L204 (body hinge_barrel+lock_tab) + L260-L298 (switches+cord 改父 handle) | eligible if compatible | **拓扑变化**：handle 拆成独立 part，REVOLUTE 铰链 axis=(0,−1,0) lower=0(locked-open) upper=1.5；body 上 hinge_barrel+lock_tab visual；switches→`handle_to_*`、cord→FIXED handle |
| open_loop_grip | rec_hair_dryer_var_loop_grip_handle | L90-L118 (`_handle_solid` 带椭圆 cutout) + L121-L123 (`_switch_nub`) + L177-L185 (`switch_shelf`) + L207-L231 (shelf 上 switch_0/1) | eligible if compatible | body 融合的开环框握把，椭圆 hand cutout（XZ ellipse 0.014×0.022 贯穿 Y）+ 独立 `switch_shelf` dark 面板；switches 仍挂 body（命名 `switch_0/1`）；body Z extent>0.12 |

### Slot C：rear_intake_filter（barrel 后端进风/滤网）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| radial_fixed_grille | rec_pink-compact-hair-dryer-with-a-detachable-rotata_20260605_144857_361026_8f70ba30 | L125-L132 (`rear_filter` cap+三圈 torus 肋) | eligible if compatible | body 上的固定后盖：CylinderGeometry cap + 3 圈 TorusGeometry 同心肋；纯 parent visual，**无关节**（degrade 见 §8/§9） |
| twist_ring_filter | rec_hair_dryer_var_twist_rear_filter | L91-L134 (`_bayonet_ring_cq`+`_grille_mesh`：8 ribs+3 tabs+twist ring) + L171-L177 (body `bayonet_ring`) + L207-L226 (`rear_grille` part + `body_to_rear_grille` REVOLUTE) | eligible if compatible | **拓扑变化**：可拆 `rear_grille` part，bayonet REVOLUTE axis=(1,0,0) lower=0 upper=1.05；body 上 `bayonet_ring` 接收环；grille=torus 旋拧环+hub+8 radial rib(局部循环)+3 bayonet tab(局部循环) |
| hinged_lint_screen | rec_hair_dryer_var_hinged_rear_filter | L91-L124 (`_perforated_disc` 25 孔 + `_hinge_knuckle`) + L162-L168 (body 两 knuckle) + L182-L203 (`lint_screen` part + `body_to_lint_screen` REVOLUTE) | eligible if compatible | **拓扑变化**：flip-open `lint_screen` part，REVOLUTE axis=(0,1,0) lower=0 upper=1.5；穿孔 disc(3 圈 hole pushPoints) + hinge_tab；body 上两个 `hinge_knuckle_i` visual |

硬约束满足：每个 slot ≥2 candidate，Slot A=4、Slot B=3、Slot C=3；无单候选 slot；每个 candidate 有真实 `model.py:Lx-Ly`，全部 `eligible if compatible`，候选间均有结构（part tree / joint / mesh 拓扑）差异，非纯换色换尺寸。

---

## 槽位图（slot graph）

pattern: `mixed`（parallel_children 为主，Slot B folding 与 Slot C twist/hinged 局部 linear_chain）

```
                      root: body (barrel_shell ∪ handle_shell* + switch mount + rear mount visuals)
                       |
   [front lip x≈0.163, barrel axis +X]
   body --barrel_to_nozzle (CONTINUOUS, axis +X)--> Slot A: nozzle_attachment part
                       |
   [handle +Y face]
   body --body_to_power/heat (PRISMATIC, axis +X)--> 2× switch part   (pistol / open_loop)
                       |
   [rear face x≈0, barrel axis +X]
   body --(Slot C joint)--> Slot C: rear_intake_filter part

   * Slot B = folding_travel_handle 时，handle 不再融进 body 而是独立 part：
     body --body_to_handle (REVOLUTE, axis −Y, lower=0 locked-open, upper=1.5)--> handle
     handle --handle_to_power/heat (PRISMATIC, axis +X)--> 2× switch part
     handle --handle_to_cord (FIXED)--> power_cord
```

接口点位与策略：
- **Slot A 上游接口**：barrel front lip（x≈0.175 外缘 r≈0.030），nozzle back sleeve 在 x≈−0.006..0.010 处 r≈0.030–0.033 套住 lip。joint origin=(0.163,0,0)，CONTINUOUS axis=+X，无 limit。`expect_overlap axes="x" min_overlap=0.006` + `allow_overlap(nozzle_shell, body_shell)`。
- **Slot B 接口**：pistol/open_loop = handle 融进 body 壳（无跨 part 关节，switches/cord 直接挂 body）。folding = handle pivot 在 barrel 底面 (HINGE_X=0.063, HINGE_Z=−0.041)，REVOLUTE axis=(0,−1,0)；hinge_barrel(body)↔hinge_ear(handle) 和 barrel_shell↔handle_shell 故意 overlap（captured pin）。
- **Slot C 接口**：fixed = body rear cap visual（无关节）。twist = bayonet_ring(body, x≈−0.006)↔grille tabs 旋拧，REVOLUTE axis=+X，`allow_overlap(grille_disc, bayonet_ring)`+`expect_contact`。hinged = barrel 后顶 (x≈0, z≈0.037) 两 knuckle↔hinge_tab，REVOLUTE axis=(0,1,0)，`allow_overlap(hinge_knuckle_i, hinge_tab)`+`expect_contact(screen_disc, body_shell)`。
- **互斥/派生**：switches/cord 的 parent（body vs handle）和关节命名（`body_to_*` vs `handle_to_*`）由 Slot B 选择派生 —— 选 folding 时整组 switch/cord 重父到 handle。三个 slot 几何上互不接触（前 / 中下 / 后），无跨 slot 碰撞，可任意组合（见 §9 兼容矩阵）。

---

## 每槽位 Module Emits / Interfaces

### Slot A / concentrator_nozzle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nozzle`（visual `nozzle_shell`：圆背→扁矩形 slot 中空 mesh） | parent/model.py:L146-L148 |
| internal joints | 无（自身刚体） | — |
| upstream interface | back rim 套 barrel front lip；`barrel_to_nozzle` CONTINUOUS origin=(0.163,0,0) axis=+X | parent/model.py:L152-L160 |
| downstream interface | 无（链末端，前端出风口） | — |

### Slot A / diffuser_nozzle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `diffuser`（visual `bowl_shell` + 局部循环 `finger_{i}`×10） | diffuser/model.py:L206-L223 |
| internal joints | 无（fingers 是局部重复 visual，非关节） | diffuser/model.py:L213-L223 |
| upstream interface | sleeve 套 barrel front lip；`barrel_to_diffuser` CONTINUOUS origin=(0.163,0,0) axis=+X | diffuser/model.py:L227-L235 |
| downstream interface | 无 | — |

### Slot A / comb_pick_nozzle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nozzle`（visual `nozzle_body` + `comb_lip_rail` + 局部循环 `tooth_{i}`×11） | comb/model.py:L166-L183 |
| internal joints | 无（teeth 是局部重复 visual） | comb/model.py:L175-L183 |
| upstream interface | 圆领套 barrel front lip；`barrel_to_nozzle` CONTINUOUS origin=(0.163,0,0) axis=+X | comb/model.py:L188-L196 |
| downstream interface | 无 | — |

### Slot A / wide_smoothing_nozzle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nozzle`（visual `nozzle_shell` 宽扁 slit + `slit_lip` 四条框边） | wide/model.py:L192-L194 |
| internal joints | 无 | — |
| upstream interface | 圆领套 barrel front lip；`barrel_to_nozzle` CONTINUOUS origin=(0.163,0,0) axis=+X | wide/model.py:L198-L206 |
| downstream interface | 无 | — |

### Slot B / pistol_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | handle 融进 root `body`（visual `body_shell` 含 barrel∪handle）+ `switch_housing` visual；2×`power/heat_switch`（visual `*_nub`）；`power_cord` | parent/model.py:L122-L140,L162-L171,L203-L204 |
| internal joints | `body_to_power_switch`/`body_to_heat_switch` PRISMATIC axis=+X lower/upper=∓0.007；`body_to_cord` FIXED | parent/model.py:L172-L180,L206-L212 |
| upstream interface | handle 与 barrel 壳同体（root，无父关节） | parent/model.py:L122 |
| downstream interface | +Y 面 switch_housing 承载滑钮 origin=(0.060,0.0205,sz) | parent/model.py:L134-L140,L177 |

### Slot B / folding_travel_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | 独立 `handle`（visual `handle_shell` 带 hinge ear + `switch_housing`）；body 上 `hinge_barrel`+`lock_tab` visual；2×switch（改父 handle）；`power_cord`（改父 handle） | folding/model.py:L185-L204,L210-L229,L260-L290 |
| internal joints | `body_to_handle` REVOLUTE axis=(0,−1,0) origin=(0.063,0,−0.041) lower=0 upper=1.5；`handle_to_power/heat_switch` PRISMATIC；`handle_to_cord` FIXED | folding/model.py:L234-L242,L272-L298 |
| upstream interface | hinge ear(handle) 抱住 hinge_barrel(body) at (0.063,0,−0.041)；captured-pin overlap | folding/model.py:L94-L100,L186-L196,L324-L338 |
| downstream interface | handle +Y 面承载滑钮；handle 底承载 cord | folding/model.py:L220-L225,L277 |

### Slot B / open_loop_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | handle 融进 `body`（visual `body_shell` 含椭圆 cutout 开环框）+ 独立 `switch_shelf` 面板；2×`switch_0/1`（挂 body）；`power_cord` | loop/model.py:L155-L185,L207-L231,L257 |
| internal joints | `body_to_switch_0/1` PRISMATIC axis=+X lower/upper=∓0.007；`body_to_cord` FIXED | loop/model.py:L221-L231,L262-L268 |
| upstream interface | 开环框与 barrel 壳同体（root，无父关节） | loop/model.py:L157 |
| downstream interface | switch_shelf 面板（FACE_PLATE_Y_CENTER=0.021）承载滑钮 origin=(0.060,0.023,sz) | loop/model.py:L177-L185,L226 |

### Slot C / radial_fixed_grille
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part —— body 上 `rear_filter` visual（cap + 3 圈 torus 肋） | parent/model.py:L125-L132 |
| internal joints | 无（固定，无关节） | — |
| upstream interface | body rear 面 x≈−0.004（barrel 后端） | parent/model.py:L126-L127 |
| downstream interface | 无 | — |

### Slot C / twist_ring_filter
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_grille`（visual `grille_disc`：torus 环+hub+8 rib+3 tab）；body 上 `bayonet_ring` visual | twist/model.py:L172-L177,L208-L214 |
| internal joints | `body_to_rear_grille` REVOLUTE axis=(1,0,0) origin=(0,0,0) lower=0 upper=1.05 | twist/model.py:L218-L226 |
| upstream interface | bayonet tabs(grille) 旋入 bayonet_ring(body, x≈−0.006)；`allow_overlap`+`expect_contact` | twist/model.py:L337-L357 |
| downstream interface | 无 | — |

### Slot C / hinged_lint_screen
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lint_screen`（visual `screen_disc` 穿孔 disc + `hinge_tab`）；body 上 2×`hinge_knuckle_i` visual | hinged/model.py:L162-L168,L183-L194 |
| internal joints | `body_to_lint_screen` REVOLUTE axis=(0,1,0) origin=(0,0,0.037) lower=0 upper=1.5 | hinged/model.py:L195-L203 |
| upstream interface | hinge_tab 与 barrel 后顶 (x≈0,z≈0.037) 两 knuckle 交错；`allow_overlap`+`expect_contact(screen_disc,body_shell)` | hinged/model.py:L295-L312 |
| downstream interface | 无 | — |

---

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `nozzle_attachment` | enum | concentrator / diffuser / comb / wide_smoothing | — | choice | deterministic procedural sampler 选择（加权见 §9） | Slot A 表 |
| `handle_grip` | enum | pistol / folding / open_loop | — | choice | sampler 选择；决定 switch/cord 的 parent 与关节命名 | Slot B 表 |
| `rear_intake_filter` | enum | radial_fixed_grille / twist_ring / hinged_lint_screen | — | choice | sampler 选择 | Slot C 表 |
| `palette_style` | enum | salon_pink / matte_black / travel_white / chrome_teal / rose_gold | salon_pink | choice | 每 seed 采样一套配色（见下表） | 全样本材质 + 真实成熟域 |
| `barrel_length_scale` | float | [0.90, 1.12] | 1.0 | independent | 缩放 barrel 全长（loft section x），clamp 后 NOZZLE_MOUNT_X、front lip、rear 面随动派生 | parent/model.py:L52-L73 |
| `barrel_radius_scale` | float | [0.92, 1.08] | 1.0 | independent | 缩放 barrel 截面半径（loft section r），nozzle sleeve/grille/bayonet r 随动 | parent/model.py:L52-L73 |
| `handle_length_scale` | float | [0.90, 1.15] | 1.0 | independent | 缩放 handle −Z 高度；folding 时同步铰链 lower grip 段 | parent/model.py:L76-L88 |
| `nozzle_mount_x` | float | derived | 0.163 | equation | `= 0.163 · barrel_length_scale`（喷嘴始终套在 front lip） | parent/model.py:L32,L157 |
| `nozzle_sleeve_r` | float | derived | 0.033 | equation | `= barrel_front_r(0.030)·barrel_radius_scale + 0.003`（套住派生后的 front lip） | Slot A 各 `_*_mesh` 圆背 r |
| `n_fingers` (diffuser) | int | [8, 12] | 10 | independent | 局部重复数；环形等距，仅 diffuser 候选 | diffuser/model.py:L42,L213 |
| `n_teeth` (comb) | int | [9, 13] | 11 | independent | 局部重复数；沿 Y 等距，仅 comb 候选 | comb/model.py:L171-L177 |
| `n_ribs` (twist grille) | int | [6, 10] | 8 | independent | 局部重复数；环形等距，仅 twist 候选 | twist/model.py:L118 |
| `fold_upper` (folding) | float | [1.2, 1.6] | 1.5 | conditional | 仅 folding_travel_handle 存在；REVOLUTE upper limit，lower 恒=0 | folding/model.py:L241 |
| `twist_upper` (twist) | float | [0.9, 1.2] | 1.05 | conditional | 仅 twist_ring_filter 存在；bayonet REVOLUTE upper | twist/model.py:L225 |
| (—) | constraint | — | — | inequality | nozzle back sleeve 与 barrel front lip 沿 X 重叠 ≥0.006：`nozzle_mount_x ∈ [front_lip_x − 0.018, front_lip_x − 0.006]`；违反则回缩 mount_x | parent/model.py:L241-L243 接口 |
| (—) | constraint | — | — | inequality | folding handle 在 fold pose 不撞 nozzle：`handle 顶段半宽 + hinge_z 余量` 投影后不进入 nozzle 包络；违反则缩 handle_length_scale 或降 fold_upper | folding hinge↔nozzle 几何 |
| (—) | constraint | — | — | inequality | switch nub 内面贴合 switch_housing/shelf 外面（不悬浮不穿模）：`switch_mount_y = face_plate_outer_y`，nub 半厚加在 origin 之上 | loop/model.py:L40-L44,L216 |

**连续尺寸采样契约**（写进 `config_from_seed`/`resolve_config`）：先采 independent 主尺度（barrel_length/radius_scale、handle_length_scale、各 n_*、各 *_upper）→ 按 equation 派生 nozzle_mount_x / nozzle_sleeve_r → 用 inequality 把 mount_x 与 fold/switch 余量投影回可行域（否则回缩 scale）→ conditional 的 fold_upper/twist_upper/n_* 在采样前按所选 enum 解析（未选对应 module 时不采样该参数）。所有连续 scale 在 `resolve_config` 内 clamp，主多样性来自 §9 的 slot/module 组合。

### palette_style 配色集（≥3，本表 5 套）
| palette_style | shell（barrel+handle） | dark accent（nozzle/grille/cord/plug） | switch | 来源依据 |
|---|---|---|---|---|
| salon_pink | (0.96,0.71,0.78) 粉 | (0.24,0.24,0.26) 深灰 | (0.32,0.32,0.34) | 全 8 样本原配色 / parent picture 001.png |
| matte_black | (0.13,0.13,0.14) 哑黑 | (0.05,0.05,0.06) 炭黑 | (0.40,0.40,0.42) 灰钮 | 沙龙级专业吹风常见配色 |
| travel_white | (0.94,0.94,0.95) 白 | (0.20,0.22,0.26) 深蓝灰 | (0.55,0.57,0.60) | 旅行/家用白机 |
| chrome_teal | (0.10,0.45,0.46) 青绿 | (0.78,0.80,0.83) 镀铬亮面 | (0.20,0.22,0.24) | 撞色家电 |
| rose_gold | (0.86,0.62,0.55) 玫瑰金 | (0.30,0.28,0.27) 暖棕灰 | (0.45,0.42,0.40) | 高端美妆吹风 |

---

## Multiplicity / Copy Logic

- **无模板级同构 multiplicity 轴**：核心结构由固定 named slots（nozzle_attachment / handle_grip / rear_intake_filter）表达，不暴露任何 `*_count` 改变 part tree / joint topology / chain depth 的模板级复制。
- 存在的 **slot 内局部重复 visual**（非拓扑 multiplicity，不进 `slot_choices`、不算 topology distinct）：
  - `finger_{i}`（diffuser）：`n_fingers∈[8,12]` 标称 10，环形等距（angle=2πi/N，FINGER_RING_R），capsule mesh，无关节，纯 diffuser part visual。来源 diffuser/model.py:L213-L223。
  - `tooth_{i}`（comb）：`n_teeth∈[9,13]` 标称 11，沿 Y 等距（−0.021..0.021），圆柱 mesh，无关节。来源 comb/model.py:L171-L183。
  - `rib_{i}`（twist grille）：`n_ribs∈[6,10]` 标称 8，环形等距 box，merge 进单个 `grille_disc` mesh，无关节。来源 twist/model.py:L118-L123。
- copied object / naming / placement / joint policy：局部重复一律 `for i in range(n)` + 共享 geometry helper + `name_i` 命名 + 规则角度/线性 placement + 统一无关节（merge 进所属 part visual 或作为同 part 的多个 visual）。这些 count 是 candidate-local 连续/整数参数，**不**作为 topology-level multiplicity，sweep 不为其单设 N 上限轴。

---

## 拓扑多样性审计

总组合数：Slot A(4) × Slot B(3) × Slot C(3) = **36** 个 slot/module 组合（≥10 ✓）。
（局部 n_fingers/n_teeth/n_ribs 不计入 topology distinct；palette_style 与连续 scale 也不计入拓扑等价类。）

理由：36 个组合彼此在 part tree / joint 拓扑上可区分 ——
- handle_grip 直接改变 part 数与关节：pistol/open_loop = handle 融 body（switch/cord 挂 body，`body_to_*`）；folding = 多 1 个 `handle` part + 1 个 REVOLUTE，switch/cord 改父 handle（`handle_to_*`）。
- rear_intake_filter 直接改变 part 数与关节：fixed = 0 后置关节；twist = +1 `rear_grille` part + REVOLUTE(+X)；hinged = +1 `lint_screen` part + REVOLUTE(+Y)。
- nozzle_attachment 改前置 part 的 visual 拓扑（含/不含局部循环 finger/tooth）。
joint 计数本身就有多档：part 数 ∈ {pistol/open_loop+fixed: 4–5 parts/3–4 joints} … {folding+twist 或 hinged: 6 parts/5–6 joints}，远超 10 distinct。即便只看 (handle_grip × rear_intake_filter) 的关节拓扑就有 3×3=9 个明显不同骨架，再叠 4 个 nozzle 与连续 scale，1000-seed distinct 预计 ≥36（拓扑），实际渲染多样性远高。

seed_domain_policy：`procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng` 对三个 slot 各做加权 choice（权重见下），再采 palette_style 与连续 scale；`seed=0` 不特殊。所有组合默认合法（§兼容矩阵全绿），无需 regression overrides。`slot_choices_for_seed` 返回 `[("nozzle_attachment",X),("handle_grip",Y),("rear_intake_filter",Z)]`，与 build 选择一致。random sweep seeds 0-49 初轮 / 0-999 成熟审计 + viewer 目检。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别拓扑等价类上限=36（slot 组合），低于 300 的原因是类别本身只有 3 个三/四选 slot、无模板级 multiplicity——这是类别结构上限，符合"低于 300 需说明类别/兼容约束原因"。≥10 机械门槛远超。

加权采样（小 N 偏多原则不适用——无 N 轴；改为按真实出现频率/稳健性加权）：
- nozzle_attachment：concentrator 0.34（parent 主型）/ wide_smoothing 0.24 / diffuser 0.22 / comb 0.20。
- handle_grip：pistol 0.50（parent 主型、最稳）/ open_loop 0.28 / folding 0.22（带额外铰链）。
- rear_intake_filter：radial_fixed_grille 0.44（parent 主型）/ twist_ring 0.30 / hinged_lint_screen 0.26。

Controlled local parameterization：初版应含 `barrel_length_scale`[0.90,1.12]、`barrel_radius_scale`[0.92,1.08]、`handle_length_scale`[0.90,1.15] 三个 independent 主尺度；`nozzle_mount_x`/`nozzle_sleeve_r` 为 equation 派生（保喷嘴套接）；`fold_upper`/`twist_upper`/`n_fingers`/`n_teeth`/`n_ribs` 为 conditional（依所选 module）。全部在 `resolve_config` clamp/派生，遵循 §7 采样契约（independent→equation→inequality 投影→conditional 解析）。这些 scale 只改安全比例与 clearance，不改 slot 拓扑、关节语义或 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C 加权 choice + palette + 连续 scale；`ctx.rng` 决定性 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 36 cell 全合法（三 slot 几何分区互不接触）；folding/twist/hinged 的额外 REVOLUTE 各居一端，互不冲突 | 无 floating / 穿模 / 轴冲突 / closed-pose / bulky 失败 |
| controlled local variation | barrel/handle scale + 各 n_* + *_upper，全 clamp/派生 | 比例变化不破坏 nozzle 套接、铰链 origin、switch 贴合、类别身份 |
| regression overrides | none | —（全组合默认合法，无需 override） |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A nozzle_attachment | 4 | yes | yes | concentrator/diffuser/comb/wide_smoothing |
| B handle_grip | 3 | yes | yes | pistol/folding(拓扑+铰链)/open_loop |
| C rear_intake_filter | 3 | yes | yes | fixed(无关节,degrade 见下)/twist/hinged |

`radial_fixed_grille` 单候选降级说明：它本身无关节（纯 body visual），但它**不是** "单候选 slot"——Slot C 共 3 个 candidate，其中 twist/hinged 提供真实 REVOLUTE，fixed 是结构上合法的"无活动滤网"成熟域成员（真实廉价吹风机即如此），保留为 candidate 而非折叠。模板每个 seed 必有 nozzle CONTINUOUS + 2 个 switch PRISMATIC 的真实关节，即使 Slot C=fixed 也满足"至少一个非固定关节"。

---

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C 三元组）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（`seed=0` 不特殊）
- compatibility matrix / gating prevents illegal module combinations（本类别 36 cell 全合法，gating 仅做参数解析）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain（procedural 加权 choice 为主）
- controlled local scale params are clamped and cannot break interfaces（barrel/handle scale、n_*、*_upper 全在 resolve_config clamp/派生）
- cross-part scale dependencies resolved in `resolve_config`（nozzle_mount_x/sleeve_r equation、套接 inequality、fold/switch clearance inequality）
- critical InterfaceSpec / MatingContract points exist：barrel_to_nozzle 套接、folding hinge captured-pin、twist bayonet 接触、hinged knuckle 交错、switch nub 贴合
- key joints have expected type / axis / range：`barrel_to_nozzle` CONTINUOUS +X；`body_to_*_switch`/`handle_to_*_switch` PRISMATIC +X ∓0.007；`body_to_handle` REVOLUTE −Y [0,1.5]；`body_to_rear_grille` REVOLUTE +X [0,1.05]；`body_to_lint_screen` REVOLUTE +Y [0,1.5]
- copied objects follow naming and placement policy：`finger_{i}`/`tooth_{i}`/`rib_{i}` 共享 helper + 规则 placement

## Reject cases
- nozzle 不套 barrel front lip（沿 X overlap <0.006）→ 喷嘴漂浮/脱节。
- folding handle 选中却没拆出独立 `handle` part 或没有 `body_to_handle` REVOLUTE（lower 必须=0 locked-open）→ 拓扑未生效。
- switch/cord 在 folding 下仍挂 body（未改父 handle、命名仍 `body_to_*`）→ 折叠时开关/线脱离握把。
- twist/hinged 选中却没拆出 `rear_grille`/`lint_screen` part 或后置关节缺失/错轴（twist 必 +X、hinged 必 +Y）。
- switch nub 悬浮于 housing/shelf 外（未把 mount_y 设到 face-plate 外表面 / 未在 origin 上加 nub 半厚）→ 悬空或穿模。
- 把 finger/tooth/rib 局部 count 当模板级 multiplicity 暴露 `*_count` 轴 → 错误拓扑膨胀。
- 连续 scale 让 nozzle_mount_x 落出 [front_lip−0.018, front_lip−0.006] → 套接断裂；必须在 resolve_config 回缩。
- 任一 seed 没有产出至少一个非固定关节（nozzle CONTINUOUS + 2 switch PRISMATIC 恒在）→ 不合格。

---

## 与相邻类别的边界
- 不该混入：**Fan / 暖风机 / 热风枪**（无握把滑钮 + 可换前喷嘴 + 后进风滤网的 hand-held 吹发语义；吹风机喷嘴绕轴 CONTINUOUS 旋转换风型是身份特征）。
- 不该混入：**台式/壁挂吹风机或吹风机支架**（本类别是 hand-held，握把 + 下垂电源线是身份；支架是独立家具类别）。
- 不该混入：**直发器/卷发棒/卷发筒**（夹板/加热筒接触式造型，无 barrel 气流 + 后进风格栅；它们是 hair styler 而非 hair dryer）。
- 不该混入：纯配色/比例/装饰密度变体——这些走 palette_style 与连续 scale，不构成新 slot/candidate。

---

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：(1) Slot C `radial_fixed_grille` 为无关节 candidate（已说明为合法成熟域成员，非降级单候选），确认保留；(2) palette_style 仅 salon_pink 来自样本实测，其余 4 套为真实吹风成熟域推断配色，确认可接受；(3) 局部 n_fingers/n_teeth/n_ribs 作为 candidate-local 参数而非 multiplicity 轴，确认。 |

---

## 模板实现备注（可选）
- 共享 helper：`_loft`、`_barrel_solid`、`_handle_solid`（pistol/twist/hinged/部分 nozzle 变体逐字相同）可抽公共；cord 几何 parent/comb/wide/twist/hinged 完全一致（body-mounted 版），folding 用 handle-local 版（`_cord_geom`）。
- folding_travel_handle 的 captured-pin 需 element-scoped `allow_overlap`：`(body.hinge_barrel, handle.handle_shell)` 与 `(body.barrel_shell, handle.handle_shell)`；twist 需 `(rear_grille.grille_disc, body.bayonet_ring)`；hinged 需 `(body.hinge_knuckle_i, lint_screen.hinge_tab)` ×2 与 nozzle 的 `(nozzle_shell, body_shell)` 套接。每个组合在 run_tests 中复制对应 allow_overlap。
- switch/cord 的 parent 与关节前缀（`body_` vs `handle_`）必须随 handle_grip 选择派生，是唯一的跨 slot 派生依赖。
- open_loop_grip 的 switch_shelf y 余量（FACE_PLATE_Y_OUTER=0.023 vs barrel 内壁 y≈0.034）需保留，避免滑钮硬件穿 barrel 壳。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | core | body(barrel∪handle)+switch+cord | rec_pink-compact-hair-dryer-with-a-detachable-rotata_…_8f70ba30 | L52-L88,L119-L212 | root 壳 + PRISMATIC switch + FIXED cord 基线 |
| S2 | Slot A | concentrator_nozzle | rec_pink-…_8f70ba30 | L91-L109,L146-L160 | 集风嘴 part + CONTINUOUS spin |
| S3 | Slot A | diffuser_nozzle | rec_hair_dryer_var_diffuser_nozzle | L101-L168,L205-L235 | 碗形+穿孔+finger 局部循环 |
| S4 | Slot A | comb_pick_nozzle | rec_hair_dryer_var_comb_nozzle | L91-L129,L165-L196 | slit duct + tooth 局部循环 |
| S5 | Slot A | wide_smoothing_nozzle | rec_hair_dryer_var_wide_smoothing_nozzle | L91-L154,L191-L206 | 宽扁 slit + lip 框边 |
| S6 | Slot B | pistol_handle | rec_pink-…_8f70ba30 | L76-L88,L119-L180 | 固定握把（switch/cord 挂 body） |
| S7 | Slot B | folding_travel_handle | rec_hair_dryer_var_folding_handle | L80-L101,L185-L298 | 独立 handle part + REVOLUTE 铰链 + 改父 |
| S8 | Slot B | open_loop_grip | rec_hair_dryer_var_loop_grip_handle | L90-L118,L177-L231 | 开环框 + switch_shelf |
| S9 | Slot C | radial_fixed_grille | rec_pink-…_8f70ba30 | L125-L132 | 固定后盖 visual（无关节） |
| S10 | Slot C | twist_ring_filter | rec_hair_dryer_var_twist_rear_filter | L91-L134,L171-L226 | 可拆 rear_grille + bayonet REVOLUTE |
| S11 | Slot C | hinged_lint_screen | rec_hair_dryer_var_hinged_rear_filter | L91-L124,L162-L203 | flip-open lint_screen + REVOLUTE |
