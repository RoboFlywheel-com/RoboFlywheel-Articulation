# Trashcan2 — modular spec (Urban Environment / public-street swing-lid trash can)

## 元信息
| 项 | 值 |
|---|---|
| slug | `trashcan2` |
| template path | `agent/templates/Urban_Environment_Trashcan2.py` |
| test path (optional) | `tests/agent/test_trashcan2_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`parallel_children`：`body` 是 root / chassis。四个固定 named slot 的 part 挂到 body：lid_mechanism（主机构，SWING REVOLUTE flap/door）、mount（落地/post/wall）、inner_liner（可选 PRISMATIC 内胆）。body_shape 决定 root 几何形态本身。无模板级 multiplicity 轴（hex 6 面 / liner grip tab 等都是 module-local 固定循环）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category（3 parents + 8 converged variants） |
| source_index_policy | only adopted module sources are indexed below |

读取结论：所有 11 个样本共享同一个身份骨架——一个**中空开口桶身（body, root）** + 一个**盖该口的 SWING 机构（REVOLUTE 主关节）**，且每个样本都显式保证「投放口在 flap 背后是真实开放空腔」。真正的拓扑变化轴是四条：
1. **body_shape**：round LatheGeometry shell / rectangular four-wall mesh / square CadQuery box / round_drum mesh / hexagonal 6-Box panels。part tree 与 primitive 家族不同。
2. **lid_mechanism（主关节）**：teardrop dome rocker / square gable rocker / pyramidal-hood push flap / dome circular push flap / front swing door（top-hinge）/ open hood + swing flap。joint 命名、axis、range、parent（lid/roof/hood/body/drum）不同；其中 front_swing_door 是独立的 hatch-hinge 拓扑。
3. **mount**：free_standing（直接落地 / 4 feet）/ post_mounted（pole + base plate + cradle bracket，body 悬空 FIXED 提起）/ wall_hoop（wall plate + hoop ring + arms，body 离墙 FIXED）。mount 引入 FIXED root 上游 part 与新 part tree。
4. **inner_liner**：none / removable_liner（嵌套内桶 + 竖直 PRISMATIC 提拉，**第二个 joint**，使对象成为 double-articulated）。

只换 color/material/纯 scale 的差异不计为 candidate（见 dropped axes）。

## 核心身份

Trashcan2 是**公共 / 街道废物桶**，物理含义：一个落地（或挂柱 / 挂墙）的中空容器，桶口被一个**摆动盖板（swing flap / swing door / push flap）**遮蔽，使用者推动盖板即可投放垃圾，盖板靠重力回弹复位。**defining joint 是这个 SWING 主关节（REVOLUTE）**——它是用户面向的唯一核心 articulation，所有变体必须保留它并继续读作街道/公共桶。

成熟域：桶身高度 0.25 m（小型街桶/室内桶）到 0.85 m（落地街桶）；body 直径/边长 0.21–0.40 m。盖板行程必须能开过 ~60°（多数样本 ±1.2–1.75 rad）以读作真实开合。

**关键不可违反约束（mouth-must-stay-open）**：swing flap 背后的投放口必须是**真实开放的空腔**，绝不能被封死。三种封口反模式都在样本里被显式规避（见 validator + reject）。

## 槽位 + 候选模块表

### Slot A：lid_mechanism（主机构槽 —— SWING 开合，REVOLUTE 主关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| teardrop_dome_rocker | rec_small-cylindrical-black-plastic-swing-lid-trash-_…_d5a40ab1 | dome `_lid_mesh` L95-L157；flap `_flap_mesh` L160-L213；joint `lid_to_flap` L278-L288 | eligible if compatible | 银色穹顶盖（fixed 于 body）+ 中央 teardrop rocker flap；REVOLUTE axis Y，range ±1.6；穹顶 teardrop 孔无端盖，skirt `CylinderGeometry(...closed=False)` L154 不封口 |
| square_gable_rocker | rec_blue-rectangular-swing-flap-trash-bin-with-a-gra_…_6e382be6 | roof `_roof_mesh` L111-L203；flap `_flap_mesh` L206-L218；joint `roof_to_flap` L296-L306 | eligible if compatible | gable 坡顶（fixed）+ +X 坡面 square rocker flap；REVOLUTE axis Y（roof ridge），range ±1.4；+X 面只画 4 条 border strip（含反向 4 条），**绝不**整块 back quad L170-L184 |
| pyramidal_hood_push_flap | rec_square-green-painted-steel-street-trash-can-with_…_e7cea0e6 | hood `_hood_shell` L125-L210；flap `_flap_geometry` L292-L310；frame `_flap_frame` L261-L289；joint `body_to_push_flap` L357-L365 | eligible if compatible | 金字塔 hood 顶 + 前 -Y 面 push flap（顶边铰）；REVOLUTE axis X，range 0–~1.3（75°）；hood 前面 `if i==0: continue` 跳过 outer+inner 面 L129-L138，留实洞 |
| dome_circular_push_flap | rec_trashcan2_var_liddomepush | dome `_lid_mesh` L96-L174；flap `_flap_mesh` L177-L232；joint `lid_to_flap` L296-L306 | eligible if compatible | 圆顶 crown 中央嵌圆 push flap rocker；REVOLUTE axis Y，range ±1.2；穹顶圆孔 outer/inner lip 连接但 L141-L147 **无 cap face**，skirt closed=False |
| front_swing_door | rec_trashcan2_var_lidfrontdoor | body+cutout `_body_cq` L105-L166（door void L152-L164）；door `_door_cq` L170-L240；joint `body_to_door` L344-L354 | eligible if compatible | 上前壁矩形 hatch door，**TOP-hinge 外掀**；REVOLUTE axis -Y，range 0–1.75（~100°）；前壁 box-cut 真实开洞 L152-L164；hinge boss 只加厚洞上方；door 直接挂 body（无 fixed lid 中介） |
| open_hooded_top | rec_trashcan2_var_lidopenhood | hood `_hood_cq` L98-L140（aperture cut L118-L124）+ mounting plate `_mounting_plate_mesh` L143-L180；joint `hood_to_flap` L268-L278 | eligible if compatible | 固定 hood/canopy 留前 aperture + 盖该口的 swing flap（顶边铰外掀）；REVOLUTE axis -Y，range 0–1.3（75°）；hood 前壁 box-cut aperture 真实开洞 L118-L124，flap 带 4 mm clearance 不封死 |

降级说明：无单 candidate slot——6 个候选远超 3-6 目标，含两种 joint 拓扑（中介 lid/hood/roof 上的 rocker；以及直接挂 body 的 front_swing_door hatch）。

### Slot B：body_shape（体形 / root 几何家族）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_lathe | rec_small-cylindrical-black-plastic-swing-lid-trash-_…_d5a40ab1 | `_body_shell` L60-L83 | eligible if compatible | 锥度圆柱中空 shell，`LatheGeometry.from_shell_profiles` + 底盘 disc；开口 top |
| rectangular_mesh | rec_blue-rectangular-swing-flap-trash-bin-with-a-gra_…_6e382be6 | `_tapered_shell` L62-L108 | eligible if compatible | 锥度矩形四壁（手写 `quad()` 12 面 + rim）+ floor slab；开口 top |
| square_cadquery | rec_square-green-painted-steel-street-trash-can-with_…_e7cea0e6 | `_body_panels` L78-L92 | eligible if compatible | CadQuery `.box().cut()` 中空方体；开口 top |
| round_drum_mesh | rec_trashcan2_var_bodydrumdoor | `_drum_shell` L91-L216（front opening band 跳面 L126-L128, L138-L140；throat walls L171-L214） | eligible if compatible | 直壁圆桶 drum mesh，前壁留矩形 opening band（door 用），带 throat 内壁 |
| hexagonal_panels | rec_trashcan2_var_bodyhex | 6×`Box` panel loop L113-L119 + hex floor ExtrudeGeometry L122-L129；profile `_hex_profile` L60-L66 | eligible if compatible | 六棱柱 6 面板（`for i in range(6)`）+ hex 底盘；hood plate ExtrudeWithHolesGeometry 真实穿孔 |

降级说明：5 个候选，覆盖 round/rect/square/drum/hex；drum 与 round_lathe 虽都圆但 part tree（drum 直壁 + 前 opening band vs lathe 锥度 + 顶口）不同，计为独立 candidate。

### Slot C：mount（落地 / 安装方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| free_standing | rec_small-cylindrical-black-plastic-swing-lid-trash-_…_d5a40ab1（无腿落地）/ rec_square-…_e7cea0e6（带 4 corner_post + 4 feet） | 无腿：body z=0 落地（root 即 body）；带腿：`_corner_post` L214-L234 + `_foot` L237-L247，corner loop L326-L328（4×） | eligible if compatible | body 直接落地；可选 4 corner posts + 4 feet（each post 内含 7 rivet `for k in range(n_riv)` L223-L233） |
| post_mounted | rec_trashcan2_var_postmount | post `CylinderGeometry` L360-L366；base plate `Box` L379-L384；bracket arms+bands `_bracket_arm_mesh` L274-L282 / `_clamp_band_mesh` L285-L338（emit loop L403-L423）；joint `post_to_body` FIXED L437-L443 | eligible if compatible | 立柱 pole + 地面 base plate + cradle bracket（2 arm + 2 band）托起 body；body 悬空 `CAN_BOTTOM_Z=0.55`；4 bolts loop L393-L400 |
| wall_hoop | rec_trashcan2_var_wallhoop | wall plate `BoxGeometry` L288-L289；hoop `TorusGeometry` L297-L299；arms `_support_arm_geo` L263-L267（loop L307-L315, 2×）；joint `plate_to_body` FIXED L352-L358 | eligible if compatible | 墙面平板 + 环箍 hoop ring 抱桶 + 2 support arm；body 离墙 FIXED；4 bolts loop L324-L332 |

降级说明：3 个候选。post_mounted / wall_hoop 引入 FIXED root 上游 part（post / wall_plate 作 root，body 变 FIXED child），改变 part tree 与 root coordinate；free_standing body 自身即 root。

### Slot D：inner_liner（内胆机构 —— 可选第二关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none | parent1/2/3（无内胆） | —（body 无嵌套子桶） | eligible if compatible | 无内胆；仅 swing flap 单关节 |
| removable_liner | rec_trashcan2_var_innerliner | shell `_liner_shell` L252-L275；rim `_liner_rim_mesh` L278-L298；grip tabs `_grip_tab_mesh` L301-L337（loop L441-L457, 4×）；joint `body_to_liner` PRISMATIC L461-L471 | eligible if compatible | 嵌套内桶，竖直 PRISMATIC 提拉取出（axis +Z，range [0, 0.32]）；外桶保留 swing flap REVOLUTE → **double-articulated** |

降级说明：2 个候选（none / removable_liner）。样本池仅 1 个 liner 实现，liner 形态家族单一，故此 slot 2 candidate；none 为绝大多数权重（见采样计划）。

## 槽位图（slot graph）

pattern: `parallel_children`

```
                                    body (root, body_shape ∈ Slot B)
                                      │  open-top hollow shell（mouth = real void）
        ┌─────────────────────────────┼──────────────────────────────┬─────────────────────────┐
        │ FIXED (lid/roof/hood 中介)    │ REVOLUTE (front_swing_door   │ PRISMATIC (removable_     │ FIXED (post_mounted /
        │  ＋ REVOLUTE flap             │  / push_flap 直挂 body)       │  liner，可选)             │  wall_hoop：mount 作 root)
        ▼                              ▼                              ▼                          ▼
   lid_mechanism (Slot A)        lid_mechanism (Slot A,            inner_liner (Slot D)      mount (Slot C)
   rocker/dome 中介盖→flap        front_door/push 直挂 body)        liner 提拉子桶            post / wall_plate
```

接口点位与 joint policy：
- **body → lid_mechanism**（主关节，必有）：
  - rocker 型（teardrop_dome / square_gable / dome_circular / open_hooded）：body 先 FIXED 一个中介盖 part（lid/roof/hood，坐在 body rim mating face，`body_to_lid|roof|hood` FIXED origin=()），再在盖上以 REVOLUTE 挂 flap，pivot 在盖面 hole 边界（如 `pivot_z=_dome_z(...)−0.001` L274 / `_flap_frame` 坡面 pitch L221-L237 / hood lintel `AP_TOP_Z`）。axis Y（dome/gable/hood-flap）或 X（pyramidal push）。
  - hatch 型（front_swing_door）：body 前壁 box-cut 出 hatch void，door 以 REVOLUTE **直接挂 body**（无中介 lid），hinge 在洞顶边缘（`HINGE_Z=DOOR_TOP_Z`，axis -Y，range 0–1.75）。
- **root → mount**（Slot C）：free_standing 时 body 自身即 root（mount 退化为 0 或 4 feet visual+post，FIXED）；post_mounted / wall_hoop 时 **post / wall_plate 成为 root**，body 经 FIXED（`post_to_body` / `plate_to_body`，origin 抬高 `CAN_BOTTOM_Z≈0.55`）挂到 cradle/hoop mating contact。
- **body → inner_liner**（Slot D，可选）：liner 经 PRISMATIC（`body_to_liner` axis +Z，range [0, LINER_LIFT≈0.32]）嵌入 body 内腔，rim 落在 body rim 上方 standoff；grip tabs 为 module-local visual。liner 与 lid flap 互不依赖（double-articulated 并联）。
- 互斥/派生：front_swing_door 与 round_drum_mesh body 天然配（drum 前 opening band 即 door 的洞）；rocker/dome 盖与 round/rect/square/hex body 配。front_swing_door + 非 drum body 需 body 侧前壁切洞（见 compatibility matrix gating）。

## 每槽位 Module Emits / Interfaces

### Slot A / module teardrop_dome_rocker
| emits | 描述 | 来源 |
|---|---|---|
| parts | lid（dome，fixed visual）、flap（teardrop cap） | S1 / L237-L262 |
| internal joints | `lid_to_flap` REVOLUTE axis Y range ±1.6 | S1 / L278-L288 |
| upstream interface | dome skirt sleeves over body rim（mating face = body top rim，FIXED `body_to_lid`） | S1 / L248-L254 |
| downstream interface | flap pivot at dome hole boundary `pivot_z=_dome_z(FLAP_WID/2)−0.001`；hole 无 cap，skirt closed=False | S1 / L154, L274 |

### Slot A / module square_gable_rocker
| emits | 描述 | 来源 |
|---|---|---|
| parts | roof（gable，fixed）、flap（square panel + 指扣 lip） | S2 / L262-L290 |
| internal joints | `roof_to_flap` REVOLUTE axis Y range ±1.4 | S2 / L296-L306 |
| upstream interface | roof eave skirt drops over body rim（FIXED `body_to_roof`） | S2 / L273-L279 |
| downstream interface | flap on +X slope face，pivot `_flap_frame` pitch=ROOF_SLOPE；border strips only（无 full back quad） | S2 / L221-L237, L170-L184 |

### Slot A / module pyramidal_hood_push_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | hood（pyramidal，含前面开洞）、flap | S3 / hood `_hood_shell` L125-L210 |
| internal joints | `body_to_push_flap` REVOLUTE axis X range 0–~1.3 | S3 / L357-L365 |
| upstream interface | hood 坐 body rim（与 corner posts 共 body） | S3 / L320-L328 |
| downstream interface | 前 -Y 面 `if i==0: continue` 跳 outer+inner 面留实洞 | S3 / L129-L138 |

### Slot A / module dome_circular_push_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | lid（圆顶 dome）、push_flap（圆 cap） | S4 / L256-L286 |
| internal joints | `lid_to_flap` REVOLUTE axis Y range ±1.2 | S4 / L296-L306 |
| upstream interface | dome FIXED 于 body（`body_to_lid` origin=()） | S4 / L267-L273 |
| downstream interface | dome 圆孔 outer/inner lip 连接 **无 cap face**；skirt closed=False | S4 / L141-L147, L170-L173 |

### Slot A / module front_swing_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | door（弧面 hatch + handle + door-side knuckles）；body 前壁切洞 + hinge boss | S5 / `_door_cq` L170-L240 |
| internal joints | `body_to_door` REVOLUTE axis -Y range 0–1.75（直挂 body，无中介 lid） | S5 / L344-L354 |
| upstream interface | hinge boss 仅加厚洞上方；body-side knuckles even i loop L281-L292 | S5 / L140-L150, L281-L292 |
| downstream interface | 前壁 box-cut 真实 void `cut_x_depth=WALL_T+BOSS_EXTRA_R+0.02` | S5 / L152-L164 |

### Slot A / module open_hooded_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | hood（canopy 留前 aperture）、mounting_plate、flap、rivets(6) | S6 / L207-L266 |
| internal joints | `hood_to_flap` REVOLUTE axis -Y range 0–1.3 | S6 / L268-L278 |
| upstream interface | mounting_plate 环形桥接 body rim → hood 壁（FIXED `body_to_hood`） | S6 / `_mounting_plate_mesh` L143-L180, L237-L243 |
| downstream interface | hood 前壁 box-cut aperture 真实 void；flap 带 4 mm clearance 不封死 | S6 / L118-L124, L57 |

### Slot B / module round_lathe（rectangular_mesh / square_cadquery / round_drum_mesh / hexagonal_panels 同构 emits）
| emits | 描述 | 来源 |
|---|---|---|
| parts | body（root，中空开口 shell） | S1 `_body_shell` L60-L83 / S2 `_tapered_shell` L62-L108 / S3 `_body_panels` L78-L92 / drum `_drum_shell` L91-L216 / hex panel loop L113-L129 |
| internal joints | 无（body 为 root chassis） | — |
| upstream interface | free_standing 时 root；post/wall 时 FIXED child（origin 抬高） | mount source |
| downstream interface | top rim mating face（承 lid/roof/hood）；内腔（承 liner PRISMATIC）；前壁可切洞（承 front_door） | 各 body source |

### Slot C / module post_mounted（wall_hoop / free_standing 类同）
| emits | 描述 | 来源 |
|---|---|---|
| parts | post / base_plate / bracket arms+bands（或 wall_plate / hoop / arms）；4 bolts | S_post L360-L423 / S_wall L288-L332 |
| internal joints | `post_to_body` / `plate_to_body` FIXED（body 抬高悬空） | S_post L437-L443 / S_wall L352-L358 |
| upstream interface | base_plate 落地 z=0 / wall_plate 贴墙 y 面 | S_post L379-L384 / S_wall L288-L289 |
| downstream interface | cradle band / hoop ring 抱 body（allow_overlap + expect_contact） | S_post L403-L423 / S_wall L297-L315 |

### Slot D / module removable_liner
| emits | 描述 | 来源 |
|---|---|---|
| parts | liner（嵌套子桶）、liner_rim、grip_tabs(4) | S_liner L252-L337 |
| internal joints | `body_to_liner` PRISMATIC axis +Z range [0, 0.32] | S_liner L461-L471 |
| upstream interface | liner 嵌入 body 内腔，rim 落 body rim 上方 standoff | S_liner L612-L622 |
| downstream interface | 提拉时清出 body rim（mouth 仍开放）；与 flap 并联无依赖 | S_liner L657-L662 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| lid_mechanism | enum | {teardrop_dome_rocker, square_gable_rocker, pyramidal_hood_push_flap, dome_circular_push_flap, front_swing_door, open_hooded_top} | — | choice | deterministic procedural sampler；受 body_shape 兼容门控 | Slot A table |
| body_shape | enum | {round_lathe, rectangular_mesh, square_cadquery, round_drum_mesh, hexagonal_panels} | — | choice | sampler；front_swing_door 优先配 round_drum_mesh | Slot B table |
| mount | enum | {free_standing, post_mounted, wall_hoop} | — | choice | sampler | Slot C table |
| inner_liner | enum | {none, removable_liner} | — | choice | sampler；removable_liner 低权重 | Slot D table |
| palette_style | enum | {street_green, civic_blue, plastic_black, galvanized_steel, drum_charcoal, brushed_silver} | — | choice | 见 palette；与 material 名映射 | 各 source materials |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 BODY_H（街桶 0.25–0.85 m 区间内） | S1 L44 / S4 L body |
| body_radius_scale | float | [0.90, 1.15] | 1.0 | independent | clamp；缩放 R_TOP/R_BOTTOM 或边长 | S1 L42-L43 |
| flap_size_scale | float | derived | 1.0 | equation | `= f(body_radius_scale)`：flap 须 ≤ 桶口开洞，按 body_radius_scale 同比缩 | S2 L54 / S3 flap |
| lid_pivot_z | float | derived | — | equation | `= dome_z/roof slope/aperture lintel(body_height_scale)`；pivot 随盖面重算 | S1 L274 / S2 L221-L237 |
| flap_open_range | float | [1.05, 1.75] rad | 见各 module | independent | clamp 至 ≥1.05（>60° 开合可读） | S1 L285-L287 等 |
| liner_lift | float | derived | 0.32 | equation | `= body_height·k`，须 ≥ 0.9·body_inner_height（提拉能清出 rim） | S_liner L468-L470 |
| post/plate_lift_z | float | derived | 0.55 | equation | `= ground/wall standoff + body_height·k`；body 悬空高度随 mount | S_post L64 / S_wall L56 |
| (—) | constraint | — | — | inequality | `flap_footprint ≤ mouth_opening`（flap 不得大于投放口，否则封口）；违反则回缩 flap_size_scale | mouth-open invariant |
| (—) | constraint | — | — | inequality | `liner_lift ≥ 0.9·body_inner_height`（提拉须清 rim）；违反回缩或拒绝 | S_liner L657-L662 |
| (—) | constraint | — | — | conditional | front_swing_door 时 body 须有前壁洞：drum 自带；round/rect/square/hex 须 body 侧切洞，否则 gate 掉该组合 | compatibility matrix |

连续尺寸采样契约：先采 independent（body_height_scale、body_radius_scale、flap_open_range）→ equation 派生（flap_size_scale、lid_pivot_z、liner_lift、post/plate_lift_z）→ inequality 投影回缩（flap≤mouth、liner_lift≥clear）→ conditional 解析（front_swing_door 的 body-洞 兼容）。

## Multiplicity / Copy Logic

- 无模板级复制数量轴：核心结构由 4 个固定 named slot 表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 制造多样性。
- 存在的循环都是 **module-local 固定常数**，不进 `slot_choices`、不参与加权采样：
  - hexagonal_panels：`for i in range(6)` 六面板（hex 固定 6）+ hex floor。
  - free_standing(square)：4 corner posts + 4 feet（`for sx,sy,nm in (...)` 4×），每 post 内 7 rivet（`for k in range(n_riv)` 固定 7）。
  - post_mounted：4 bolts loop；2 bracket arm + 2 clamp band。
  - wall_hoop：4 bolts loop；2 support arm。
  - front_swing_door：5 hinge knuckle（even body-side 3 / odd door-side 2）+ 6 frame rivet。
  - open_hooded_top / round_drum_mesh：6 lintel rivet / 3 banding hoop + 5 hinge knuckle。
  - removable_liner：4 grip tab loop（`NUM_GRIPS=4`）。
- 这些数量是 module identity 的一部分（hex 必 6 面，feet 必 4），非可采样自由变量；若日后要做 hoop/bolt 计数变化，需新增显式 multiplicity 轴并按 SPEC_TEMPLATE 第 8 节声明。

## 拓扑多样性审计

总组合数：A(6) × B(5) × C(3) × D(2) = **180 distinct cells**（未计兼容门控削减）。
仅 A×B = **30 ≥ 10** ✓。

理由：A 6 候选每个改 part tree / joint axis / parent 中介；B 5 候选改 root primitive 家族；C 3 候选改 root 与 FIXED 上游；D 2 候选加/不加 PRISMATIC 第二关节。即便兼容门控削掉约 1/3 非法组合，distinct 拓扑仍 按 ≥300 report-only 口径观察。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个 seed 做 deterministic 加权抽取：先抽 body_shape（5 等概，drum 略低因仅配 front_door 时最自然），再抽 lid_mechanism（受 body 门控），再 mount，再 inner_liner（none ≈0.75 / removable_liner ≈0.25），再 palette_style。连续 scale 按采样契约解析。`seed=0` 不特殊。无 curated/modulo 主表。少量 regression overrides 仅用于已知失败回归（初始为 none）。random sweep：seeds 0-4 → 0-19 → 0-49（首过），0-999（成熟审计）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别凭 180 cell × 多 scale 容易达成，无须降标。

Controlled local parameterization：初版应含 body_height_scale [0.85,1.20]、body_radius_scale [0.90,1.15]、flap_open_range [1.05,1.75]（independent）；flap_size_scale、lid_pivot_z、liner_lift、post/plate_lift_z（equation 派生）。全部在 `resolve_config` clamp/派生，受 mouth-open inequality（flap≤mouth）、liner-clear inequality、front_door-body-洞 conditional 约束，不破坏 InterfaceSpec / MatingContract / 主关节语义。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body→lid→mount→liner→palette 加权抽，compatibility gate 过滤非法 body×lid | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | front_swing_door 优先 round_drum_mesh；配其他 body 须 body 切前壁洞，否则 gate；rocker/dome/hood 盖配 round/rect/square/hex；post_mounted/wall_hoop 与任意 body+lid 可组；removable_liner 与任意组合可组（PRISMATIC 并联） | 无 floating / 穿模 / 封口 / axis 错 / liner 卡 rim |
| controlled local variation | body_height_scale / body_radius_scale / flap_open_range + 派生项，clamp + inequality 回缩 | 比例变化不破坏 flap≤mouth、pivot 落盖面、liner 清 rim、mount 抬升、身份 |
| regression overrides | none（初版） | 仅已知失败回归 |
| random sweep | seeds 0-49 首过，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A lid_mechanism | 6 | yes | yes | 含 rocker / hatch / push 三类 joint 拓扑 |
| B body_shape | 5 | yes | yes | round/rect/square/drum/hex |
| C mount | 3 | yes | yes | free/post/wall（含 FIXED 上游 root） |
| D inner_liner | 2 | yes | no | none / removable_liner；池仅 1 liner，none 高权重 |

## Validator

- slot_choices_for_seed 返回已实现 module 名（A/B/C/D 四槽 + palette_style）。
- config_from_seed 对普通 seed 用 deterministic procedural sampling；seed=0 不特殊。
- compatibility matrix / gating 阻止非法组合：front_swing_door 仅在 body 有前壁洞时合法（drum 自带 / 其他 body 显式切洞），否则 gate。
- optional regression overrides 稀少且有理由（初版 none）。
- final 模板不得把小 curated 表当主 seed domain。
- 受控 scale（body_height/radius/flap_open）clamp；派生（flap_size/pivot/liner_lift/lift_z）在 resolve_config 求解，不留到 builder 失败。
- 跨部件依赖（flap≤mouth、liner_lift≥clear、front_door body-洞）在 resolve_config 解算。
- critical InterfaceSpec / MatingContract 存在：body rim ↔ lid/roof/hood FIXED；body 内腔 ↔ liner PRISMATIC；root ↔ body FIXED（post/wall）。
- key joints type/axis/range：主 SWING flap REVOLUTE（axis Y 或 X，range ≥~1.05 rad）；liner PRISMATIC（axis +Z，range [0,~0.32]）；mount FIXED。
- copied objects 遵守命名/placement（hex 6 面 name_i、bolts/knuckles/grip name_i + shared helper）。
- **【mouth-must-stay-open 检查（强制）】**：swing flap 背后的投放口必须是真实开放空腔。validator 须断言：
  1. flap/door 处于 closed pose 时，**flap_footprint ≤ mouth_opening**（flap 不大于投放口），否则视为封口失败。
  2. 投放口几何**不得**含封口面：rocker/dome 盖的 hole 必须无 cap disc（skirt `closed=False`，hole 边界仅 outer/inner lip 连接，无 cap face）；坡面/平面 flap 开口只画 border strip，**无 full back-face quad**；frustum/hood 面在 flap 那侧 **跳过/切掉** outer+inner 面（`if i==0: continue` / box-cut aperture）。
  3. flap 打开后（pose 至 ~open）leading edge 须显著移离 closed 位（dome 下沉 / door 外掀），证明背后确是空腔而非实心（参考各 run_tests：S1 L399-L402、S3「genuine open mouth」、S5 L416-L424/door-covers-void、drum「opening is a real void」L509-L519）。
  4. removable_liner 提拉至全程时须清出 body rim（mouth 仍开放），liner 不得封住投放口。

## Reject cases

- swing flap 在 closed pose 把投放口封死（flap_footprint ≥ mouth，或盖上加了 cap disc / full back quad / 未跳过的 frustum 面）——**核心身份失败**。
- 主 SWING flap 用了 FIXED 或 PRISMATIC 而非 REVOLUTE（失去 defining joint）。
- flap 行程 < ~60°（open 不可读为真实开合）。
- front_swing_door 配了无前壁洞的 body 而未切洞（门挂在实壁上，无 void）。
- post_mounted / wall_hoop 的 body 仍落地 z=0（未被 cradle/hoop 抬起悬空，mount 失效）或与 post/wall 间有可见漂浮 gap（cradle 不接触 body）。
- removable_liner 与 body 内腔不同轴 / 提拉 axis 非 +Z / 提拉行程不足以清 rim / liner 反封 mouth。
- hex body 用了 ≠6 面，或 feet ≠4，破坏 module identity（数量是固定 identity 非自由采样）。
- 把 color/material/纯 scale 当独立 candidate（不构成新拓扑）。
- mount FIXED root（post/wall_plate）缺失或 body 直接当 root 却又声称 post/wall——root coordinate 不一致。

## 与相邻类别的边界

- 不该混入：**Trashcan1（galvanized loose-lid cans）**——Trashcan1 是松扣/可整体掀起的桶盖（lid 整体抬离或 latch），不是绕固定铰链摆动的 swing flap；其 defining 动作不是 REVOLUTE swing flap。Trashcan2 必须保留绕铰摆动且口长开的 swing 主关节。
- 不该混入：**Garbage_bin（dumpster）**——大型工业 dumpster（侧开大门 / 顶盖整体翻、叉车口、滚轮），尺度与机构（tipping / fork pockets）超出街桶 identity；不纳入 tipping/wheeled。
- 不该混入：**Large_Trashcan（wheelie bin）**——带轮可推家用大桶（顶盖整体 hinge-lid + 两轮 + 推杆），其 defining 是 wheel + 整体翻盖，非街桶 swing flap；排除 wheel/pedal/tipping 机构以保持 swing-lid 身份纯净。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | teardrop_dome_rocker / round_lathe / free_standing(无腿) | rec_small-cylindrical-black-plastic-swing-lid-trash-_…_d5a40ab1 | L60-L83 body；L95-L213 lid+flap；L278-L288 joint | round body + dome rocker baseline；mouth-open skirt closed=False |
| S2 | A/B | square_gable_rocker / rectangular_mesh | rec_blue-rectangular-swing-flap-trash-bin-with-a-gra_…_6e382be6 | L62-L108 body；L111-L218 roof+flap；L296-L306 joint | rect body + gable rocker；border-strip-only no back quad |
| S3 | A/B/C | pyramidal_hood_push_flap / square_cadquery / free_standing(4 feet) | rec_square-green-painted-steel-street-trash-can-with_…_e7cea0e6 | L78-L92 body；L125-L310 hood+flap；L214-L247 posts/feet；L357-L365 joint | square body + push flap；`if i==0: continue` open face；corner posts |
| S4 | A | dome_circular_push_flap | rec_trashcan2_var_liddomepush | L96-L174 dome；L177-L232 flap；L296-L306 joint | dome circular push；hole 无 cap face |
| S5 | A | front_swing_door | rec_trashcan2_var_lidfrontdoor | L105-L166 body+cut；L170-L240 door；L344-L354 joint | hatch door 直挂 body（无中介 lid）；前壁 box-cut void |
| S6 | A | open_hooded_top | rec_trashcan2_var_lidopenhood | L98-L180 hood+plate；L268-L278 joint | hood aperture + swing flap；box-cut aperture void |
| S_drum | B | round_drum_mesh | rec_trashcan2_var_bodydrumdoor | L91-L216 drum（opening band 跳面 L126-L128） | drum body 前 opening band；天然配 front_swing_door |
| S_hex | B | hexagonal_panels | rec_trashcan2_var_bodyhex | L113-L129 6 panel loop + hex floor | hex 6 面 body；ExtrudeWithHoles 真实穿孔 |
| S_post | C | post_mounted | rec_trashcan2_var_postmount | L360-L423 post/base/bracket；L437-L443 FIXED | pole + cradle 悬空 body；FIXED root |
| S_wall | C | wall_hoop | rec_trashcan2_var_wallhoop | L288-L332 plate/hoop/arms；L352-L358 FIXED | wall plate + hoop 抱桶；FIXED root |
| S_liner | D | removable_liner | rec_trashcan2_var_innerliner | L252-L337 liner/rim/grips；L461-L471 PRISMATIC | 嵌套内桶 +Z 提拉；double-articulated |

## 模板实现备注（可选）

- palette_style 取 6 colorways（来自 sources）：street_green (0.55,0.60,0.20) / civic_blue (0.10,0.52,0.78) / plastic_black (0.10,0.10,0.11) / galvanized_steel (0.62,0.64,0.66) / drum_charcoal (0.11,0.11,0.12) / brushed_silver (0.74,0.76,0.79)；每 colorway 配 body/lid/flap/accent 四档明暗（见各 source materials 行：S1 L219-L221、S2 L243-L245、S3 L316-L319、S_drum L330-L339）。
- 共享 helper：所有 lathe body（S1/S4/S_post/S_wall/S_liner）共用 `_body_shell`-类；rocker flap mesh（S1/S4）共用 teardrop/dome cap helper；mount FIXED 抬升逻辑（S_post/S_wall）共用 standoff 计算。
- captured-pin overlap：lid skirt sleeve over body rim、flap seam in recess、cradle band 抱 body、liner-in-body、hinge knuckle interleave 均需 element-scoped `allow_overlap` + `expect_contact`（复刻各 source 的 allow_overlap 注释）。
- 暂不进 seed domain 的组合：front_swing_door × 非-drum body 若实现成本高，可先只在 round_drum_mesh 下采样 front_swing_door，其余 body 走 body-切洞 路径（reviewer 决定）。
