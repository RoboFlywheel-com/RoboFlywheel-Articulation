# mailbox — Modular Template Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `mailbox` |
| template path | `agent/templates/Urban_Environment_Mailbox.py` |
| test path (optional) | `tests/agent/test_mailbox_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots：body_form + mount + door_mechanism + signal_flag；door/flag 两根 REVOLUTE 真关节挂在 body 上） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category（3 parents + 8 converged variants，列在 /tmp/urb_ids_mailbox.txt）|
| source_index_policy | only adopted module sources are indexed below |

阅读要点（across all 11）：

- **三种 body 主结构均为真 HOLLOW 壳**，绝非实心块。tunnel 用 outer+inner `_arch_skin` 双拱皮 + `_arch_mouth_ring` + 后壁 `_door_plate`（P_TUNNEL L69-L139, L199-L241）；pillar 用六面薄铸铁墙 + `interior_back_liner` + `_half_cyl_top` 圆顶盖（P_PILLAR L71-L106, L122-L195, L261-L280）；slant 用六面薄钢墙 + `interior_back_liner` + 斜顶 `slanted_top` + gable posts（P_SLANT L105-L212）；rounded streetbox 用 CadQuery `_build_shell` lathe-style 拱肩曲面 outer.cut(inner) + 投递口 cutter（streetbox L65-L102）。每个壳都用 `interior_back_liner` / 深拱腔，并附 deep-cavity 测试（depth>0.25/0.30）证明真空腔。
- **门机构是定义性 REVOLUTE**：基线 pull_down_flap 全部为底铰（hinge origin 在开口底边、`axis=(0,1,0)`、`upper≈1.3-1.65`，正 q 把自由顶边翻出 +X 并下落）——P_TUNNEL `body_to_door` L340-L348、P_PILLAR `body_to_flap` L323-L331、P_SLANT `body_to_door` L257-L265。side_hinge_swing 是侧立铰（hinge origin 在左 jamb、`axis=(0,0,-1)` 竖轴、有 captured hinge barrels + straps + strike_plate）——sidedoor `body_to_door` L365-L373，captured-pin allow_overlap + expect_contact L398-L431。
- **mount 是第二可替换层**：single_post（方钢柱 + base_plate + collar，P_SLANT L82-L103 / singlepost L157-L205）、two_legs_scroll（双腿 + 卷铁花饰 + crossbar，P_TUNNEL L155-L197）、two_legs_plain（`_add_leg_assembly` for-loop 双腿 + foot pads + cross_member，twolegs L78-L131）、ground_pedestal（`rounded_rect_profile`+`ExtrudeGeometry` 三段阶梯裙座 for-loop，pedestal L102-L125）、wall_bracket（平背 plate + 4 角 bolt_boss for-loop，body 悬于 MOUNT_Z，无落地，wall L140-L171, `plate_to_body` FIXED L338-L346）。
- **signal_flag = 第二真 REVOLUTE（present/absent）**：L 形 semaphore 旗（pivot_boss 短圆柱穿过侧壁 + flag_arm 竖臂 + flag_panel），`axis=(0,1,0)` 水平销，q=0 举起（臂竖直），正 q 下落——P_TUNNEL `body_to_flag` L303-L327, L355-L363；flag variant L251-L293, `body_to_flag` L320-L330，附 boss-against-side_wall expect_contact L500-L505。pillar / slant 基线 absent。

## 核心身份

mailbox = **邮件收集箱**：一个 **HOLLOW 投递腔体（box/tunnel/pillar/round）** + **可开启投递门/翻盖（REVOLUTE，定义性关节）** + **支撑/安装（单柱 / 双腿 / 裙座 / 墙挂）**，residential 款另有 **侧信号旗（REVOLUTE，present/absent）**。覆盖两大现实族：
- **residential 路边邮箱**：拱形 tunnel 或矩形小箱，举高在装饰柱/腿上，前翻盖 + 红色信号旗（举/降表示有出件）。
- **street letter collection box**：直立 pillar box（铸铁 "LETTERS"）或斜顶 cabinet，落地或举高在柱上，pull-down hopper 投递口或侧摆门，通常**无旗**。

默认成熟域：壳体真空（开门见深腔到 dark back liner，非实心）；门关闭姿态贴合开口（小 seam）；门开启自由边外翻 +X 并下落（底铰）或侧摆（竖铰）；旗 q=0 举起、正 q 下落；落地件 base z≈0，墙挂件悬于 MOUNT_Z。

## 与相邻类别的边界

- 不该混入：**utility_box / electrical_cabinet**（理由：utility box 是密封无信号旗、门常为大平开柜门且**无 hopper 投递口语义**，也不举在装饰邮筒柱上；mailbox 必须读作"投信/取信"——pull-down 投递口或 LETTERS 头带 + 可选信号旗才是身份）。
- 不该混入：**cabinet / 床头柜**（理由：cabinet 是室内多门多抽屉储物，落地或台面；mailbox 是户外单投递腔 + 单一投递门 + post/leg/pedestal/wall 邮政安装，且 hollow chute + 旗语 = 不可混淆的邮政身份）。
- 不该混入：**post_box 风格的纯邮筒柱 / 路牌 sign**（理由：sign 无 hollow 投递腔与可动门；mailbox 的柱只是 mount 子层，主体身份在投递腔 + 门）。

## 槽位 + 候选模块表

### Slot A：body_form（主投递腔体 —— 主结构轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tunnel_arched | P_TUNNEL = rec_classic-curbside-us-tunnel-shaped-residential-ma_20260612_132256_365232_809bed2b | L69-L139（helpers）, L199-L241（壳） | eligible if compatible | 半圆拱 outer skin + inner skin（reverse winding）双皮真空壳 + `_arch_mouth_ring` 前唇环 + box_floor + D 形 back_wall；`MeshGeometry` 自建；身份=residential tunnel；唯一天然带 flag 基线 |
| boxy_pillar | P_PILLAR = rec_vintage-blue-cast-iron-us-mail-letter-collection_20260612_132251_186263_ed61e0ab | L71-L106（cap helper）, L122-L195（六墙壳）, L261-L280（圆顶盖） | eligible if compatible | 直立矩形薄铸铁六面壳（back/2 side/floor/top_lid/分段 front）+ `interior_back_liner` + `_half_cyl_top` 圆管顶盖（FIXED）+ base_skirt + LETTERS 头带；天然落地（base z≈0），无旗基线 |
| slanted_cabinet | P_SLANT = rec_curbside-blue-street-collection-box-on-a-single-_20260612_132234_578811_4565f031 | L105-L212 | eligible if compatible | 斜顶矩形薄钢六面壳 + `interior_back_liner` + `slanted_top`（rpy pitch wedge）+ 两侧三角 gable_post + sill/header/jambs 框开口；street collection；无旗基线 |
| rounded_streetbox | rec_mailbox_var_streetbox | L65-L102（`_build_shell`）, L105-L112（`_build_cap_finial`）, L132-L245 | eligible if compatible | CadQuery 圆肩连续曲面：前竖墙 threePointArc 过顶到后墙的 outer.cut(inner) 中空壳 + 前面 box cutter 切投递口 + 顶 cap_ridge（FIXED）；`mesh_from_cadquery`；落地 base_skirt |

### Slot B：mount（支撑/安装 —— 第二结构轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_post | P_SLANT（L82-L103）/ rec_mailbox_var_singlepost（L157-L205） | P_SLANT L82-L103；singlepost L59-L64, L157-L205 | eligible if compatible | 单方钢柱 `post_column/post_shaft` + 地脚 `base_plate` + 顶 `post_collar`（与 body floor expect_contact）；root=post，`post_to_body` FIXED |
| two_legs_scroll | P_TUNNEL = …_809bed2b | L155-L197 | eligible if compatible | 两方腿（for-loop `enumerate((-s/2,s/2))`）+ foot pads + `post_crossbar` + 叠层卷铁花饰 scroll rings（`for k in range(n_scroll)`×`for s,sgn`）；root=post |
| two_legs_plain | rec_mailbox_var_twolegs | L44-L97（dims+`_add_leg_assembly`）, L114-L131 | eligible if compatible | `_add_leg_assembly` for-loop 双方管腿 + foot_pad + 单 `cross_member` 横梁，无卷铁；root=frame，`body` FIXED on frame |
| ground_pedestal | rec_mailbox_var_pedestal | L50-L67（dims）, L102-L125 | eligible if compatible | 三段阶梯裙座（base flange/step/skirt，`rounded_rect_profile`+`ExtrudeGeometry.from_z0` for-loop），宽于 body 落地直立；root=pedestal |
| wall_bracket | rec_mailbox_var_wall | L62-L89（dims）, L140-L171（plate+bolt boss）, L338-L346（`plate_to_body`） | eligible if compatible | 平背矩形 plate（宽/高超 body）+ 4 角 `bolt_boss` for-loop（rpy 横置穿墙）；body 悬于 MOUNT_Z=1.0（无落地 floor）；root=back_plate，`plate_to_body` FIXED |

### Slot C：door_mechanism（投递口机构 —— 真关节，定义性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pull_down_flap | P_PILLAR / P_SLANT / P_TUNNEL | P_PILLAR L282-L309 + `body_to_flap` L323-L331；P_SLANT L214-L243 + `body_to_door` L257-L265；P_TUNNEL L275-L297 + `body_to_door` L340-L348 | eligible if compatible | 底铰 hopper：hinge origin 在开口底边外侧、`axis=(0,1,0)`、panel 自 hinge +Z 延伸、`upper≈1.3-1.65`；正 q 顶边外翻 +X 并下落；含 flap_top_rim + brass 拉手 |
| side_hinge_swing | rec_mailbox_var_sidedoor | L217-L241（barrels/strike）, L313-L352（door + straps）, L365-L373（`body_to_door`） | eligible if compatible | 侧立铰柜门：hinge origin 在左 jamb（HINGE_Y=-DOOR_W/2）、`axis=(0,0,-1)` 竖轴、panel 自 hinge +Y 延伸；body 侧 hinge_barrels（竖销）+ door hinge_straps captured-pin + strike_plate；正 q 自由边侧摆出 +X |

> door_mechanism 暂为 2 candidate（满足 slot ≥2 硬约束）。front_pull_door / drawer 第三候选 reserved（源图未发射结构），暂不进采样域；说明见 §dropped。

### Slot D：signal_flag（信号旗 —— 真关节，present/absent）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flag_present | P_TUNNEL / rec_mailbox_var_flag | P_TUNNEL L299-L327（flag part）+ `body_to_flag` L355-L363；flag var L251-L293 + `body_to_flag` L320-L330 + boss contact L500-L505 | eligible if compatible | L 形侧 semaphore：`pivot_boss` 短圆柱（rpy 横置）穿侧壁 + `flag_arm` 竖臂 + `flag_panel`；`axis=(0,1,0)` 水平销、q=0 举起、正 q 下落（`upper≈π/2..1.9`）；boss 对侧壁 captured-pin |
| flag_absent | P_PILLAR / P_SLANT | P_PILLAR（无 flag part，body+cap+flap only）；P_SLANT（无 flag part） | eligible if compatible | 无信号旗 part / 无 `body_to_flag` 关节；street collection box 现实款 |

## 槽位图（slot graph）

pattern: `mixed`

```
mount (root: post/frame/pedestal/back_plate)
  --[mount_to_body FIXED @ body 底面接触 (collar/cross_member top 与 floor 共面；wall: plate front 与 back_wall 外面共面)]-->
body_form (HOLLOW 投递腔，提供 front 开口平面 FRONT_X、侧壁 ±Y、底面/MOUNT_Z)
  |
  +--[body_to_door REVOLUTE  (定义性)]--> door_mechanism
  |       pull_down_flap: pivot @ (FRONT_X+t/2, 0, open_bot)  axis=(0,1,0)  lower=0 upper∈[1.3,1.65]
  |       side_hinge_swing: pivot @ (FRONT_X+t/2, -DOOR_W/2, mid_z)  axis=(0,0,-1)  lower=0 upper≈1.4
  |
  +--[body_to_flag REVOLUTE  (定义性, present 时才发射)]--> signal_flag
          flag_present: pivot @ (front_inset, +/-side_y, body_z*0.6) axis=(0,1,0) lower=0 upper∈[π/2,1.9]
          flag_absent : 不发射 flag part / flag joint
```

接口点位与装配规则：

- **mount→body（FIXED）**：post/leg/pedestal 顶面（collar 或 cross_member 顶）与 body `floor` 下表面共面接触（`expect_contact` collar↔floor，tol 0.005）；落地 mount 把 body 抬到 `BOX_FLOOR_Z`/`PED_TOTAL_H`/`LEG_TOP_Z`（body min_z>0.45）。wall_bracket：plate 前面与 body `back_wall` 外面共面，body 悬于 MOUNT_Z（无 floor 落地，post_aabb 检查不适用→改 plate 落 z 检查见 reject）。
- **body→door（REVOLUTE，定义性）**：door 是 body 的子；pivot origin 落在真实可见前开口边（底边或左 jamb），非发明的毫米 pad。pull_down 与 side_hinge 互斥（同一开口只一种门）。
- **body→flag（REVOLUTE，定义性，可选）**：flag 仅在 flag_present 时挂为 body 子，pivot_boss captured 在侧壁（`expect_contact` boss↔side wall）。
- mount 与 door / flag 正交：任一 body_form 可配任一 mount + 任一 door + flag present/absent（兼容矩阵见 §9 例外）。

## 每槽位 Module Emits / Interfaces

### Slot A / module tunnel_arched
| emits | 描述 | 来源 |
|---|---|---|
| parts | body：arched_shell(outer)/arched_inner/front_rim/box_floor/back_wall + decal stripes/canton（parent visual） | P_TUNNEL L199-L273 |
| internal joints | 无（壳为单 part 多 visual） | — |
| upstream interface | body floor 下表面 @ z=BOX_FLOOR_Z，接 mount 顶（FIXED） | P_TUNNEL L228-L233, L331-L336 |
| downstream interface | 前开口 D 形 mouth @ FRONT_X（接 door）；+Y/-Y 侧壳面（接 flag boss） | P_TUNNEL L219-L225, L354 |

### Slot A / module boxy_pillar
| emits | 描述 | 来源 |
|---|---|---|
| parts | body：back/side×2/floor/top_lid/front_lower/front_upper/jamb×2/base_skirt/back_rib×3/letters_band + interior_back_liner；cap：cap_shell/cap_ridge（FIXED 子） | P_PILLAR L122-L259, L261-L280 |
| internal joints | body_to_cap FIXED | P_PILLAR L312-L318 |
| upstream interface | base_skirt/floor @ z≈0（天然落地）或 floor 下面接 mount 顶 | P_PILLAR L164-L170 |
| downstream interface | 前开口（front_lower/upper/jamb 框出）@ FRONT_X（接 flap）；+Y 侧壁（接 flag） | P_PILLAR L180-L209 |

### Slot A / module slanted_cabinet
| emits | 描述 | 来源 |
|---|---|---|
| parts | body：back/2 side/floor/front_sill/front_header/jamb×2/slanted_top/gable_post×2 + interior_back_liner | P_SLANT L105-L212 |
| internal joints | 无 | — |
| upstream interface | floor 下面 @ BOX_BOT_Z 接 mount 顶（FIXED） | P_SLANT L140-L145, L246-L252 |
| downstream interface | 前开口（sill/header/jamb 框）@ FRONT_X（接门）；侧壁（接 flag） | P_SLANT L150-L183 |

### Slot A / module rounded_streetbox
| emits | 描述 | 来源 |
|---|---|---|
| parts | body：body_shell(cadquery hollow)/interior_back_liner/interior_floor/base_skirt/jamb×2/letters_band/back_rib×3 + cap_ridge（FIXED 子） | streetbox L132-L245 |
| internal joints | body_to_cap FIXED | streetbox L272-L278 |
| upstream interface | base_skirt @ z≈0 落地或 floor 面接 mount | streetbox L161-L166 |
| downstream interface | 前壳投递口（cutter 切出）@ FRONT_X（接 flap）；侧壳（接 flag） | streetbox L93-L101 |

### Slot B / module single_post / two_legs_scroll / two_legs_plain / ground_pedestal
| emits | 描述 | 来源 |
|---|---|---|
| parts | post/frame/pedestal：柱或腿×2 + foot/base_plate + collar/cross_member/scroll/pedestal sections | 见 Slot B 表行 |
| internal joints | 无（root part 多 visual） | — |
| upstream interface | 地脚 @ z≈0（落地） | post_aabb min_z<0.01 测试 |
| downstream interface | 顶面（collar/cross_member top）接 body floor（FIXED，expect_contact） | P_SLANT L319-L322 |

### Slot B / module wall_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | back_plate：plate_panel + bolt_boss×4 | wall L143-L171 |
| internal joints | 无 | — |
| upstream interface | plate 背面 @ x=PLATE_BACK_X（贴墙，无落地 floor） | wall L69, L147-L152 |
| downstream interface | plate 前面接 body back_wall 外面（`plate_to_body` FIXED）；body 抬到 MOUNT_Z | wall L338-L346 |

### Slot C / module pull_down_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | flap/door：flap_panel + flap_top_rim + brass flap_handle | P_PILLAR L286-L309 |
| internal joints | body_to_door/flap REVOLUTE axis=(0,1,0) 底铰 | P_PILLAR L323-L331 |
| upstream interface | 接 body 前开口底边（pivot @ FRONT_X+t/2, 0, open_bot） | P_PILLAR L328 |
| downstream interface | 关闭覆盖开口（expect_overlap yz）+ 小 seam（expect_gap x）；开启外翻下落 | P_PILLAR L414-L454 |

### Slot C / module side_hinge_swing
| emits | 描述 | 来源 |
|---|---|---|
| parts | door：door_panel + door_frame_rim + brass handle + hinge_strap×2；body 侧加 hinge_barrel×2 + strike_plate | sidedoor L217-L241, L317-L351 |
| internal joints | body_to_door REVOLUTE axis=(0,0,-1) 竖铰 | sidedoor L365-L373 |
| upstream interface | 接左 jamb（pivot @ FRONT_X+t/2, HINGE_Y=-DOOR_W/2, mid_z）；captured hinge barrels↔straps | sidedoor L370, L398-L431 |
| downstream interface | 关闭覆盖开口 + 小 seam；开启侧摆出 +X、自由边 -Y 方向移动 | sidedoor L492-L535 |

### Slot D / module flag_present
| emits | 描述 | 来源 |
|---|---|---|
| parts | flag：pivot_boss（穿侧壁）+ flag_arm（竖臂）+ flag_panel（红） | flag var L266-L293 |
| internal joints | body_to_flag REVOLUTE axis=(0,1,0) 水平销 | flag var L320-L330 |
| upstream interface | boss captured 在 body 侧壁（expect_contact boss↔side_wall） | flag var L500-L505 |
| downstream interface | q=0 举起（flag_top>pivot_z+0.10）；正 q 下落 | flag var L469-L489 |

### Slot D / module flag_absent
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无 flag part | P_PILLAR / P_SLANT（无 flag） |
| internal joints | 无 body_to_flag | — |
| upstream/downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | tunnel_arched / boxy_pillar / slanted_cabinet / rounded_streetbox | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| mount | enum | single_post / two_legs_scroll / two_legs_plain / ground_pedestal / wall_bracket | — | choice | sampler 选择 | Slot B 表 |
| door_mechanism | enum | pull_down_flap / side_hinge_swing | — | choice | sampler 选择 | Slot C 表 |
| signal_flag | enum | flag_present / flag_absent | — | choice | sampler 选择 | Slot D 表 |
| palette_style | enum | postal_silver / federal_blue / pillar_red / royal_green / cast_iron_black / weathered_copper | — | choice | per-seed 采样；仅改 material rgba，不改拓扑 | 见 §palette |
| body_width_scale | float | [0.85, 1.18] | 1.0 | independent | clamp；缩 body Y 宽（BODY_W/BOX_W/2R）；门宽派生 | P_PILLAR BODY_W L46 / P_SLANT BOX_W L49 |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩立式 body 高（BODY_H）或拱半径；门/头带 zone 派生 | P_PILLAR BODY_H L48 / streetbox Z_CROWN L48 |
| body_depth_scale | float | [0.9, 1.15] | 1.0 | independent | clamp；缩 X 深（BODY_D/BOX_D/BOX_LEN）；腔深须仍 >0.25 | P_PILLAR BODY_D L47 |
| mount_height_scale | float | [0.85, 1.15] | 1.0 | conditional | clamp；缩柱/腿/裙座高；wall_bracket=MOUNT_Z 缩放；落地 mount body min_z 派生跟随 | P_SLANT POST_HEIGHT L45 / pedestal PED_*_H L52-L67 |
| door_open_scale | float | [0.7, 1.0] | 1.0 | independent | clamp；门 REVOLUTE upper = base_upper·scale（不超几何 clear） | P_SLANT door upper L264 |
| flag_raise_scale | float | [0.7, 1.0] | 1.0 | conditional | flag_present 时有效；旗 REVOLUTE upper = base·scale | flag var upper L327-L329 |
| leg_count | int | {2}（two_legs_* 固定 2） | 2 | conditional | two_legs_scroll/plain 时为 2，单柱/裙座/墙挂不适用 | twolegs L117 |
| scroll_ring_count | int | [2, 4] | 3 | conditional | two_legs_scroll 时有效；卷铁环叠层数 | P_TUNNEL n_scroll L184 |
| decal_stripe_count | int | [3, 5] | 4 | conditional | tunnel_arched 旗帜贴纸条数（parent visual） | P_TUNNEL n_stripe L250 |
| back_rib_count | int | [3, 5] | 3 | conditional | boxy_pillar / rounded_streetbox 背肋数 | P_PILLAR L172 |
| (—) | constraint | — | — | conditional | wall_bracket ⟹ 无落地 floor 检查；落地 mount ⟹ body min_z>0.45 且 base z≈0 | 接口 |
| (—) | constraint | — | — | inequality | `腔深 = BODY_D·depth_scale − wall − liner ≥ 0.25`；违反回缩 depth_scale | 腔深测试 |
| (—) | constraint | — | — | inequality | `门宽 = 开口净宽（body_width 派生）`；关闭门覆盖 expect_overlap yz≥0.10 不破 | 开口 / clearance |
| (—) | constraint | — | — | inequality | `门 open swing ≤ 可用 +X clearance`（door_open_scale 投影回缩） | clearance |

连续尺寸采样契约：先采 independent（body_width/height/depth_scale、door_open_scale）→ 按 conditional 解析 mount_height/flag_raise/各 count 的合法范围（依 mount/body/door/flag 选择）→ 用 inequality 把腔深、门宽、swing clearance 投影/回缩，无法满足则拒绝重采。

## palette_style 颜色方案（per-seed 采样，≥3，目标 4-6，源自 5★ 样本 material）

| palette_style | 主体 carcass/shell | 门/翻盖 | 顶/trim/cap | 五金/handle | 旗（present 时） | 来源样本 material |
|---|---|---|---|---|---|---|
| postal_silver | 镀锌钢 (0.42,0.45,0.50) | 钢灰门 (0.46,0.52,0.60) | 钢 trim | chrome handle (0.72,0.74,0.78) | 红旗 (0.74,0.10,0.13) | P_SLANT steel/door_blue/chrome + P_TUNNEL flag_red |
| federal_blue | 联邦蓝 (0.34,0.42,0.52) | 蓝门 (0.40,0.46,0.55) | cap_blue (0.31,0.39,0.49) | brass (0.62,0.55,0.32) | 红旗 | P_PILLAR blue/cap_blue/brass |
| pillar_red | 邮政红 (0.66,0.13,0.14) | 深红门 (0.55,0.10,0.12) | 红 cap | brass | 黑旗杆 (0.16,0.16,0.17) | 基于 5★ 结构 + 邮政红现实重映射（英式 pillar box）|
| royal_green | 邮政绿 (0.16,0.34,0.24) | 深绿门 (0.12,0.28,0.20) | 绿 cap | brass | 红旗 | 基于 5★ 结构 + 邮政绿现实重映射 |
| cast_iron_black | 铸铁黑 (0.13,0.13,0.14) | 黑缎门 (0.16,0.16,0.17) | 黑 cap | iron (0.13,0.13,0.14) | 红旗 (0.74,0.10,0.13) | P_TUNNEL black/black_satin/iron/flag_red |
| weathered_copper | 锈铜蓝 (0.30,0.42,0.55) | 锈门 (0.45,0.31,0.22) | rust cap (0.55,0.40,0.30) | brass | 红旗 | streetbox blue/rust/rust_dk/brass |

palette_style 仅改 material rgba，不改拓扑（按 §7 choice 类型 per-seed 采样）。pillar_red / royal_green 为基于 5★ 结构 + 既有邮政色域的现实重映射，凑足 4-6 档真实邮箱配色（银/蓝/红/绿/黑/铜）。

## Multiplicity / Copy Logic

本模板有**多根低基数 multiplicity 轴**，均为装饰/腿性同构复制，joint policy 全 FIXED（随 body 或 mount 的 parent visual）。

### 轴 1：leg_count（two_legs_scroll / two_legs_plain）
- `count_param`: leg_count
- `N_range`: **固定 2**（路边邮箱双腿现实即 2；不暴露为可变采样轴，仅作结构常量）
- sampling domain: 不采样（恒 2）
- copied object: 单方管腿 + foot_pad（`_add_leg_assembly` for-loop）
- naming: `leg_{i}` / `foot_pad_{i}`（i=0,1）
- placement: 对称 ±LEG_SPREAD/2（Y 轴），脚垫落地 z≈0
- joint policy: FIXED（属 frame/post root part visual）
- source/gating: twolegs L78-L131；仅 two_legs_* mount 时存在

### 轴 2：scroll_ring_count（two_legs_scroll）
- `count_param`: scroll_ring_count
- `N_range`: [2, 4]（测试偏小 2-3，产品 2-4）；权重档：N=3 高频，N=2/4 次之
- copied object: 一对卷铁环（`for k in range(n_scroll)` × `for s,sgn` 两 C 形）
- naming: `scroll_{k}_{s}`
- placement: 沿 Z 规则栈（z0..z1 均布），±0.04 Y 对偶
- joint policy: FIXED（post 装饰 visual）
- source/gating: P_TUNNEL L184-L197；仅 two_legs_scroll mount

### 轴 3：decal_stripe_count（tunnel_arched）
- `count_param`: decal_stripe_count
- `N_range`: [3, 5]；权重 N=4 高频
- copied object: 单贴纸条（`for i in range(n_stripe)`）
- naming: `decal_stripe_{i}`
- placement: 沿上拱规则栈，吸附壳面（y_surf 派生，无浮空）
- joint policy: FIXED（body 装饰 visual）
- source/gating: P_TUNNEL L250-L262；仅 tunnel_arched body

### 轴 4：back_rib_count（boxy_pillar / rounded_streetbox）
- `count_param`: back_rib_count
- `N_range`: [3, 5]；权重 N=3 高频
- copied object: 单背肋（`for i,yy in enumerate(...)`）
- naming: `back_rib_{i}`
- placement: 后面 Y 规则均布
- joint policy: FIXED（body 装饰 visual）
- source/gating: P_PILLAR L172-L178 / streetbox L230-L236；仅 pillar / streetbox body

## 拓扑多样性审计

总组合数（仅 slot 拓扑，不含 N / palette / scale）：
body_form 4 × mount 5 × door_mechanism 2 × signal_flag 2 = **80 distinct configs**。
计入 multiplicity 轴（leg/scroll/stripe/rib 各 2-4 档，按 body/mount 条件激活）后采样空间远大于 80。

理由：80 个纯 slot 组合 ≥ 10；即便扣掉少量兼容性弱降级（见矩阵），仍 ≥ 60 合法组合，每个改变 part tree / joint topology / root part；远超机械门槛。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng` 对四个 slot enum 各做加权采样（body_form/mount 近均匀；door_mechanism pull_down_flap 偏多~0.7（street + residential 主流）side_hinge~0.3；signal_flag present/absent ~0.5/0.5），再按 conditional 解析激活的 multiplicity count（各自加权采样小 N 偏多）与连续 scale，最后兼容矩阵合法化。`seed=0` 不特殊。无主体 curated/modulo 表；仅在已知失败回归时加 sparse regression override（首版预留 none）。

Topology target：1000-seed slot choice tuple distinct 建议 ≥ 80（受 4×5×2×2=80 slot 上限约束，本类别天然封顶；count 轴在 slot_choices 不计为拓扑等价类，故 distinct 上限即 80，低于富类别建议 300 是类别组合域有限所致，已说明）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版含 body_width_scale / body_height_scale / body_depth_scale / mount_height_scale / door_open_scale / flag_raise_scale（范围见 §7），均在 `resolve_config` clamp/派生；body_depth_scale 受腔深 ≥0.25 inequality 约束；门宽随 body_width 派生（equation/inequality），不破 InterfaceSpec（mount→body floor 接触、body→door pivot、boss captured contact）/ multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 body_form→mount→door→flag→counts→scales→palette；加权 choice；rng-only | slot_choices_for_seed matches build choices |
| compatibility matrix | 见下兼容例外；非法组合 fallback 降级 | no floating, collision, axis, captured-pin, optional flag child failures |
| controlled local variation | 6 个连续 scale + 4 个 count，全 clamp/derive | 比例变化不破腔深/门覆盖/接触/joint origin/identity |
| regression overrides | none（首版） | 仅已知失败回归用 |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

兼容矩阵关键例外（gating，优先排除易坏组合）：

- **wall_bracket × signal_flag**：允许但 flag 必须挂在**非贴墙侧**（+Y 或 -Y，远离 plate -X）；默认降权（residential 墙挂带旗少见，pull_down + absent 偏多）。validator 检查 boss 不与 plate 穿模。
- **wall_bracket 落地检查互斥**：wall ⟹ 不跑 "base z≈0 / body min_z>0.45 on post" 测试，改 "body 悬于 MOUNT_Z 且 plate 背面贴墙平面" 检查。
- **side_hinge_swing**：captured hinge barrels（body 侧）+ straps（door 侧）必须 element-scoped allow_overlap + boss↔door expect_contact；axis 必须竖直 Z（与 pull_down 的 Y 互斥）。
- **flag_present pivot**：boss captured 在所选 body_form 的真实侧壳/侧壁面（tunnel=arched_shell+arched_inner，pillar/slant/street=side_wall）——allow_overlap 必须按所选 body 的侧元素名声明（见实现备注）。
- **腔深/门覆盖**：任一 body × 任一 door，关闭门 expect_overlap yz≥0.10 + 小 seam expect_gap；body_depth_scale 回缩保 depth>0.25。
- **两腿/卷铁 count 仅对应 mount/body 激活**：scroll_ring 仅 two_legs_scroll；decal_stripe 仅 tunnel；back_rib 仅 pillar/street；非激活组合不发射该轴 part。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 4 | yes | yes | |
| B mount | 5 | yes | yes | |
| C door_mechanism | 2 | yes | no | 已说明：front_pull/drawer reserved 未发射；2 满足硬约束 |
| D signal_flag | 2 | yes | no | present/absent 二元真关节轴，本质 2 态 |

## Validator

- slot_choices_for_seed returns implemented module names（body_form/mount/door_mechanism/signal_flag）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（wall×flag 穿模、axis 混淆、captured-pin、落地检查互斥）
- optional regression overrides sparse / none（首版）
- 不 endlessly cycle 小 curated 表
- controlled local scale params clamped；腔深/门宽/swing/接触不被 scale 破坏
- cross-part scale deps（门宽=body_width 派生、腔深≥0.25）resolved in `resolve_config`
- critical interfaces exist：mount→body floor contact（落地 mount）/ plate→body flush（wall）；body→door pivot at 真实开口边；flag boss captured at side wall
- key joints：body_to_door REVOLUTE（pull_down axis=Y / side_hinge axis=Z）；body_to_flag REVOLUTE axis=Y（present 时）；mount_to_body FIXED
- copied objects follow naming/placement（leg_{i}/scroll_{k}_{s}/decal_stripe_{i}/back_rib_{i}）
- door 关闭覆盖开口（expect_overlap yz）+ 小 seam（expect_gap x）；门开启外翻/侧摆 + 自由边位移
- flag q=0 举起、正 q 下落；落地 mount base z≈0、body 抬高；wall body 悬于 MOUNT_Z

## Reject cases

- 实心块 body（无 inner skin / interior_back_liner / 腔深 ≤0.25）—— 失去 hollow chute 邮政身份。
- 门用 FIXED 或 PRISMATIC 代替 REVOLUTE，或 pull_down 用错轴（非 Y）/ side_hinge 用错轴（非 Z）。
- 门 pivot 发明毫米级 anchor pad 而非落在真实可见开口边（底边 / 左 jamb）。
- 关闭门浮在开口外（无 yz overlap）或大缝（seam 超容差）；或开启不外翻/不下落（pull_down）、不侧摆（side_hinge）。
- flag_present 但旗 q=0 不举起、正 q 不下落，或 boss 不 captured 在侧壁（浮空旗）；wall_bracket 时 flag 穿 plate。
- wall_bracket body 落到地面（未悬于 MOUNT_Z）或仍跑 "post base z≈0" 测试；落地 mount body 未抬高（min_z≤0.45）。
- 把 cap_profile / color / material / 纯 scale 当独立 slot 或新 candidate（违反结构差异要求）。
- tunnel 的 inner skin/mouth ring/back wall（或 pillar/street 的 interior liner、wall 的 plate-body flush、side_hinge 的 captured barrels）未在变体里一并复制 allow_overlap → 误报碰撞。

## 与相邻类别的边界

- 不该混入：**utility_box / electrical_cabinet**（无 hopper 投递口 / 无信号旗 / 不举在邮筒柱上 / 门为大平开柜门）。
- 不该混入：**cabinet / 床头柜**（室内多门多抽屉储物；mailbox 是户外单投递腔 + 单门 + 邮政 mount + hollow chute + 旗语）。

## 模板实现备注（可选）

- 共享 helper：`_arch_skin`/`_arch_mouth_ring`/`_door_plate`（tunnel）；`_half_cyl_top`（pillar / sidedoor / wall cap）；`_build_shell`/`_build_cap_finial`（streetbox cadquery）；`_add_leg_assembly`（two_legs_plain）；`rounded_rect_profile`+`ExtrudeGeometry.from_z0`（pedestal）。
- captured-pin / element-scoped allow_overlap 必须按所选 body_form 的侧元素名声明 flag boss 接触：tunnel→(arched_shell, arched_inner)；pillar/slant/street→(side_wall_0/1)。side_hinge：(hinge_barrel_i↔door_panel, hinge_barrel_i↔door_hinge_strap_i)。
- 壳内自接触 allow_overlap 随 body_form 复制：tunnel(arched_inner↔arched_shell, front_rim↔arched_shell, back_wall↔arched_inner)；pillar/slant/street(interior_back_liner↔back_wall / body_shell)。
- door/flap 闭合 expect_gap 容差沿用父值（pull_down min_gap≈-0.005..-0.008, max≈0.012..0.025；side_hinge 沿 sidedoor 值）。
- Cylinder origin 是中心（flag boss / pivot / handle 摆放沿用 MEMORY gotcha）。
- wall_bracket 与落地 mount 的 root 测试集互斥：实现时按 mount 选择切换 validator 分支（落地：post/frame/pedestal base z≈0 + body 抬高；wall：plate 贴墙 + body @ MOUNT_Z）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |
