# pictureX_0611_centrifuge_machine2 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_centrifuge_machine2` |
| template path | `agent/templates/pictureX_0611_centrifuge_machine2.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_centrifuge_machine2_template.py`（batch-authoring 期间跳过） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed`（support/body/input 并联挂 root + rotor 载具 multiplicity + 串联 drive_shaft 链） |

## Category Binding
category_slug: pictureX_0611_centrifuge_machine2 · template_slug: pictureX_0611_centrifuge_machine2 ·
mechanism_profile: `hand_driven_vertical_rotor`（水平 CONTINUOUS 手动输入 → 垂直 CONTINUOUS 转子 → 径向试管载具） · export_namespace: pictureX_0611
diversity_profile: `standard` ·
profile_reason: 诚实核心词汇 = 21 个 gate 合法的 support×body×drive 组合 × 3 载具机构 = 63 个 core 组合，高于 standard 下限 48、低于 compositional 120。core 只计 ①/②/③ 与真实功能 module；`bucket_count` N、palette、④装饰与连续 scale 均不计入。

> 注：本 slug 尚未登记进 `category_template_registry.json`（全库仅 3 个模板已登记，该机制尚在推广中），因此 `combo-audit` 目前对本 slug 报 "no category binding"。上表即待登记内容；登记属 registry 推广工作，不阻断本模板的机械验收（GATE P4）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 origin + 6 confirmed forks，rated_by picturex_0611_centrifuge_to_drafting_variant_confirmed_20260714） |
| read_count | 8 |
| read_scope | all 5-star samples in this category（全部 `revisions/rev_000001/model.py` 全文精读，无抽样） |
| source_index_policy | only adopted module sources are indexed below |

来源（record id → 采纳结构）：
- S1 `rec_picturex_0611__centrifuge_machine2__001__png__airflex_batch_20260710_2c7344d0f3134c2d9af35a0e17f56002`（ORIGIN，pedestal crank）— 铸铁踏座 + 肩部齿箱 + 锥形立柱、侧面偏置曲柄 + 自转木纹柄套、四位十字盘载具（真布尔通孔）+ 玻璃摆管、rotor mimic 曲柄 ×4。
- S2 `rec_picturex_0611__centrifuge_machine2__002__png__airflex_batch_20260710_da960e4e06e9474ab7021f26f44fe43a`（ORIGIN，table-clamp crank）— 圆盘齿箱 + crown/neck + 整体 C 型台钳（clamp_screw PRISMATIC）、正面样条管曲柄 + 木握柄、独立 drive_shaft 链、横杆-叉耳载具 + 金属吊杯。
- S3 `rec_picturex0611_centrifuge_machine2_fork_bucket_n2_20260714`（fork of 002）— N=2 对置摆桶（单横杆）。
- S4 `rec_picturex0611_centrifuge_machine2_fork_bucket_n6_20260714`（fork of 001）— N=6 星形盘载具（60° 循环发射臂/孔/槽）。
- S5 `rec_picturex0611_centrifuge_machine2_fork_enclosed_gearcase_20260714`（fork of 001）— ③ 全包圆润齿箱体（5 剖面椭圆放样）+ 盖板/缝线/紧固件/铸肋装饰。
- S6 `rec_picturex0611_centrifuge_machine2_fork_tripod_base_20260714`（fork of 002）— ① 台式三脚支撑（立柱+配重毂+3 径向脚+胶垫），无台钳。
- S7 `rec_picturex0611_centrifuge_machine2_fork_handwheel_drive_20260714`（fork of 001）— ② 轮缘手轮输入（torus 轮缘+5 辐条 cadquery）+ 自转轮缘滚套。
- S8 `rec_picturex0611_centrifuge_machine2_fork_rigid_tube_carrier_20260714`（fork of 001）— ② 固定角管套载具（35° 倾斜臂+套管 rotor 视觉，无摆桶 part）。

8 个样本全部被采纳为 module source（无排除项；见 §14 索引）。

## 核心身份

手摇实验室离心机（manually cranked laboratory hand centrifuge）：一个**裸露（无罩盖）的立式转子**由**手动输入（曲柄或手轮）**经齿轮驱动；转子携带**摆出式吊管/吊杯**（swing-out shields/buckets）或**固定角管套**；机器由配重踏座、台钳或三脚架支撑。默认成熟域 = 0.15–0.35 m 足迹、0.30–0.55 m 高的早 20 世纪教学/诊所手摇离心机；珐琅/镀镍铸件 + 抛光钢 + 玻璃/金属管 + 木/胶握柄。

必须保留（must_keep）：手动输入关节（CONTINUOUS 水平轴曲柄/手轮，无电机）；裸露立式 `rotor_spin` CONTINUOUS z；试管载具（摆桶 REVOLUTE 或固定角套管）；载具吊管在静止位竖直下垂、离心位外摆。

不该混入（must_not_become）：centrifuge_machine1（带盖电动台式离心机——本类**无罩盖、无电机、无 lid 关节**）；食品搅拌器/打蛋器（无试管位）；风扇/钻床（无吊管载具）；powered enclosed appliances（source map 明确排除）。转子必须平衡（对称 N 位）、吊管必须有支撑（pivot 捕获或套管坐实）。

## 槽位 + 候选模块表

### Slot A：support_base（① 骨架 —— 机器如何立住；root `body` 下段 + 可选 clamp_screw part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `weighted_pedestal` | forked_anchor (origin) | S1 001 origin | L34-L40（圆角矩形踏座）+ L196-L209（4 胶脚） | eligible if compatible | 圆角矩形铸座（cadquery rect+fillet）+ 4 嵌入橡胶脚视觉；body_mount_z≈0.014；无新增 part/joint。 |
| `table_clamp` | forked_anchor (origin) | S2 002 origin | L47-L64（C 钳 spine/jaws/boss 铸入）+ L199-L204（jaw pad）+ L363-L405（clamp_screw part + PRISMATIC） | eligible if compatible | C 型台钳铸件（spine+上下颚+螺纹 boss，布尔钻孔）；**新增 `clamp_screw` part + `clamp_adjustment` PRISMATIC z**（tommy bar+压盘）；body_mount_z≈0.150。 |
| `bench_tripod` | forked_anchor | S6 tripod fork | L46-L68（立柱+配重毂）+ L203-L227（3 径向脚+胶垫 120°循环） | eligible if compatible | 中央立柱 + 配重毂盘 + 3 径向 `tripod_foot_{i}` + `foot_pad_{i}`（body 视觉循环发射）；无 clamp part；body_mount_z≈0.150。 |

结构差异：table_clamp 增加 1 part + 1 PRISMATIC 关节（①+②）；tripod/pedestal 改变支撑骨架形态与视觉复制数（3 脚 vs 4 垫）。

### Slot B：body_form（③ 主体形态家族 / Primary Form Family —— 齿箱/立柱主体，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| `open_shoulder_mast` | forked_anchor (origin) | S1 001 origin | L41-L72（椭圆肩部 3 剖面放样 + 锥形方立柱放样 + 顶轴承 + 侧曲柄 boss） | Volumetric Envelope Form | 紧凑开放铸件：鼓肩齿箱低置 + 细锥立柱高耸；曲柄口在 −x 侧肩部；rotor 直接挂 body（mimic 输入 ×4）。 |
| `enclosed_rounded_gearcase` | forked_anchor | S5 enclosed fork | L41-L91（5 剖面椭圆放样全包齿箱 + neck + 短立柱）+ L251-L308（盖板/缝线/紧固件/铸肋 ④） | Volumetric Envelope Form | 圆润全包齿箱体量（大腹放样）替换开放肩部；同 part tree/接口；附盖板+缝线+4 紧固件+3 铸肋 host-conformal 装饰。 |
| `drum_gearbox_crown` | forked_anchor (origin) | S2 002 origin | L26-L45（XZ 圆盘齿箱+crown+neck）+ L181-L222（gearbox_cover/maker plate/cover fasteners）+ L237-L259（drive_shaft part + shaft_rotation） | Volumetric Envelope Form | 立圆盘齿鼓（法向 y）+ 圆柱 crown/neck；曲柄口在 −y 正面盘心；**新增 `drive_shaft` part（CONTINUOUS z）**，rotor 挂 shaft（独立 CONTINUOUS，无 mimic）。 |

三个可识别主体形态原型（低鼓肩+高立柱 / 大腹全包 / 立盘鼓+crown），全部 source-backed cadquery loft/体量（无 Box 降级）。**本类兼具形态与机构多样性，③ slot ≥3 达标。** drum 候选同时命中 ①（新增 drive_shaft part）与 ②（rotor 独立 spin vs mimic）——各记一笔（§8.5）。

### Slot C：drive_input（② 机构 —— 手动输入）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `offset_crank` | forked_anchor (origin) | S1 001 origin | L239-L316（crank part：shaft+hub+arm+handle_pin；`crank_spin` CONTINUOUS；`crank_knob` part 12 肋自转柄套 + `crank_knob_spin` CONTINUOUS） | eligible if compatible | 短偏置曲柄 + **自转柄套 part**（2 part 2 CONTINUOUS）。 |
| `spline_crank` | forked_anchor (origin) | S2 002 origin | L99-L144（tube_from_spline_points 弯臂 + 木柄 + 球端）+ L224-L235（`crank_rotation` CONTINUOUS） | eligible if compatible（gated，见兼容矩阵） | 长样条弯臂曲柄 + 固定木握柄（1 part 1 CONTINUOUS，无柄套 part —— part 数结构差异）。 |
| `rim_handwheel` | forked_anchor | S7 handwheel fork | L158-L199（torus 轮缘+5 辐条+毂 cadquery）+ L289-L357（`handwheel_spin` CONTINUOUS + `rim_grip` part 滚套 + `grip_spin` CONTINUOUS） | eligible if compatible | 辐条手轮 + **轮缘自转滚套 part**（2 part 2 CONTINUOUS，滚套轴切向）。 |

输入口（位置+轴向）由 Slot B body_form 输出：open/enclosed → −x 侧、轴 x；drum → −y 正面、轴 y。输入模块在局部 x 轴约定下作图，由 joint origin yaw 映射（002 的 y 轴曲柄即旋转后的同构）。

### Slot D：rotor_carrier（②+multiplicity —— 试管载具）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plate_swing_carrier`（N∈{4,6}） | forked_anchor (origin+fork) | S1 001 origin（N=4 十字盘）；S4 n6 fork（N=6 星盘） | 001 L75-L152（真布尔通孔盘+外 boss+摆槽）+ L318-L402（LatheGeometry 玻璃吊管 + N×`bucket_swing_{i}` REVOLUTE [0,1.05]）；n6 L75-L131（60° 循环臂/孔/槽） | eligible if compatible | cadquery 盘式载具（臂/通孔/摆槽循环发射）+ N 个 `bucket_{i}` part（pivot_pin+collar+玻璃 lathe 管）+ N 个 REVOLUTE（径向切轴）。 |
| `bar_fork_swing_carrier`（N∈{2,4}） | forked_anchor (origin+fork) | S2 002 origin（N=4 十字杆）；S3 n2 fork（N=2 单杆） | 002 L261-L361（crossbar+叉耳+销 + cadquery 空心锥杯吊桶 + N×REVOLUTE [0,72°]）；n2 L261-L354（单 crossbar_x） | eligible if compatible | 横杆载具（杆+2N 叉耳+N 销视觉）+ N 个金属吊杯 part（cadquery loft 空心杯+吊桥+套筒）+ N 个 REVOLUTE。 |
| `fixed_sleeve_carrier`（N∈{4,6}） | forked_anchor | S8 rigid fork | L83-L121（35° 倾斜臂+管座 boss cadquery 循环）+ L124-L137（平移 lathe 管套）+ L334-L352（`tube_holder_{i}`/`tube_sleeve_{i}` rotor 视觉，无 bucket part） | eligible if compatible | 固定角载具：倾斜臂+boss+套管全为 rotor 视觉（**减少 N 个 part 和 N 条边** —— ① 骨架差异）；`rotor_spin` 仍 CONTINUOUS。 |

### Slot palette_style（⑥ 涂装，非结构，登记进 slot_choices 做覆盖）

`mint_enamel`（S1 薄荷珐琅+玻璃）/ `aged_nickel_wood`（S2 镀镍+木柄）/ `black_japanned_brass` / `cream_lab_enamel` / `hammertone_green` —— 后三组为 record 材质大类（enamel/metal/wood/rubber/glass）内的世界知识配色扩展（⑥ 零几何）。

## 槽位图（slot graph）

pattern: mixed（parallel children 挂 root + drum 家族一段串联链 + carrier multiplicity）

```
body (root = Slot A support + Slot B body_form 视觉融合, 单根 part)
 │
 ├─[crank_spin / handwheel_spin CONTINUOUS, 水平轴 x|y @ body 输入口]──> crank|handwheel (Slot C)
 │        └─[crank_knob_spin / grip_spin CONTINUOUS]──> crank_knob | rim_grip（offset/rim 才有）
 │
 ├─(open/enclosed body) [rotor_spin CONTINUOUS z @ 顶轴承, mimic 输入×4]──> rotor (Slot D)
 ├─(drum body) [shaft_rotation CONTINUOUS z @ crown 顶]──> drive_shaft ──[rotor_spin CONTINUOUS z]──> rotor
 │
 │       rotor ──[bucket_swing_i REVOLUTE 切向轴 ×N]──> bucket_i（仅 swing 载具）
 │
 └─(table_clamp) [clamp_adjustment PRISMATIC z @ 螺纹 boss]──> clamp_screw
```

接口点位：
- `rotor_spin`：**MatingContract** —— parent `bearing_cap`（open/enclosed，positive_z）或 `shaft`（drum，positive_z）↔ child rotor `spindle`/`rotor_hub`（negative_z）；axis (0,0,1)。
- `shaft_rotation`（drum）：**MatingContract** —— body `top_bearing` positive_z ↔ `shaft` negative_z。
- `crank_spin`/`handwheel_spin`：曲柄轴销穿轴承套（pin-through-sleeve）→ 按 §A Rule 2 豁免 mating（grandfathered）+ element-scoped allow_overlap + expect-contact 语义由 targeted pose 测试背书；joint origin 落在 crank_bearing 硬件上。
- `crank_knob_spin`/`grip_spin`：柄套/滚套包裹销/轮缘（captured sleeve）→ 豁免 mating + allow_overlap。
- `bucket_swing_i`：横销被载具耳/叉耳捕获（captured pin）→ 豁免 mating + allow_overlap(carrier, pivot_pin)；origin 在销硬件上。
- `clamp_adjustment`：螺杆捕获于螺纹 boss（prismatic，origin 检查豁免）→ 豁免 mating + allow_overlap(screw_shank, body)。

互斥/派生（兼容矩阵，`resolve_config` gating）：
- `drum_gearbox_crown` ⊗ `weighted_pedestal` **非法**（源族中鼓盘从不落地踏座；低置盘心使曲柄扫掠贴地/扫底座）。其余 support×body 8 组合法（挂接经归一化 mount 平面：support 报 body_mount_z，body 在其上作图且底部截面覆盖 support 顶面足迹）。
- `spline_crank`（扫掠半径≈0.223 m）仅当 `support==table_clamp`（源族：悬于台沿，允许下探，S2/S6 原行为）或 `support==bench_tripod 且 body≠drum`（曲柄口 z≈0.239，地面净空≥0.012）→ 其余组合非法（pedestal 低口会扫地）。
- `bucket_count` 域随 carrier：plate {4,6}、bar {2,4}、sleeve {4,6}。
- drive/carrier 其余组合全部合法（手轮/曲柄平面与载具吊摆包络已按源常数核算，见 §9 拓扑审计）。

## 每槽位 Module Emits / Interfaces

### Slot A / weighted_pedestal｜table_clamp｜bench_tripod
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` 下段视觉（踏座+胶脚 / C 钳铸件+jaw pad / 立柱+毂+3 脚+胶垫）；table_clamp 另发射 `clamp_screw` part（shank+压盘+tommy bar+球端） | S1 L34-40,L196-209；S2 L47-64,L363-396；S6 L46-68,L203-227 |
| internal joints | table_clamp：`clamp_adjustment` PRISMATIC z [−0.010,0.015]；其余无 | S2 L397-L405 |
| upstream interface | 无（root） | — |
| downstream interface | body_mount_z 平面（pedestal 0.014 / clamp・tripod 0.150）+ 顶面足迹，供 Slot B 齿箱落座（同 part 视觉融合，容许轻微嵌入） | 归一化自 S2 spine→盘 union（L47-L57） |

### Slot B / open_shoulder_mast｜enclosed_rounded_gearcase｜drum_gearbox_crown
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` 上段视觉（肩放样+立柱+顶轴承+曲柄 boss+crank_bearing｜全包放样+盖板/缝/钉/肋｜圆盘+crown/neck+cover/plate/钉）；drum 另发射 `drive_shaft` part（shaft+collar） | S1 L41-72,L184-237；S5 L41-91,L251-308；S2 L26-45,L181-222,L237-249 |
| internal joints | drum：`shaft_rotation` CONTINUOUS z（body→drive_shaft，**MatingContract** top_bearing↔shaft） | S2 L250-L259 |
| downstream interface | 输入口（crank mount xyz+yaw+crank_bearing 硬件）；rotor 挂点（bearing_cap 顶 z 或 shaft 顶 z）+ rotor parent 名 + mimic 策略（open/enclosed mimic×4；drum 独立） | S1 L342-L352；S2 L319-L328 |

### Slot C / offset_crank｜spline_crank｜rim_handwheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank`（shaft+hub+arm+handle_pin）+`crank_knob`（grip+12 肋）｜`crank`（spline 弯臂+木柄+2 球端）｜`handwheel`（wheel_shaft+torus/辐条 mesh）+`rim_grip`（roller+10 肋） | S1 L239-L316；S2 L99-L144；S7 L158-L199,L289-L357 |
| internal joints | `crank_spin`/`handwheel_spin` CONTINUOUS（body→输入件，轴=body 输入口轴）；`crank_knob_spin`（crank→knob）/`grip_spin`（handwheel→rim_grip，切向）CONTINUOUS | 同上 |
| upstream interface | 输入件轴销贴 body `crank_bearing`（captured pin，joint origin 在轴承硬件上） | S1 L275-L284；S2 L226-L235 |

### Slot D / plate_swing_carrier｜bar_fork_swing_carrier｜fixed_sleeve_carrier
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rotor`（spindle/hub + cadquery 载具 mesh + center_cap｜crossbar+2N 叉耳+N 销｜倾斜臂+boss+N 套管视觉）+（swing 载具）N×`bucket_{i}`（pivot_pin+collar+玻璃 lathe 管｜cadquery 空心杯） | S1 L75-152,L318-402；S4 L75-131；S2 L261-361；S3 L261-354；S8 L83-137,L307-364 |
| internal joints | N×`bucket_swing_{i}` REVOLUTE（rotor→bucket_i，切向轴，plate [0,1.05] qc[0,0.65,1.0]；bar [0,72°]）；sleeve 无 | S1 L380-L402；S2 L339-L361 |
| upstream interface | rotor `spindle`/`rotor_hub` 底面 negative_z ↔ body/shaft 顶面（**MatingContract**，rotor_spin CONTINUOUS z） | S1 L336-L352；S2 L312-L328 |

不动细节全部为宿主 part 视觉（叉耳、销、套管、盖板、缝线、紧固件、铭牌、肋、脚垫），不做 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support_base` | enum | weighted_pedestal / table_clamp / bench_tripod | weighted_pedestal | choice | deterministic procedural sampler | Slot A |
| `body_form` | enum | open_shoulder_mast / enclosed_rounded_gearcase / drum_gearbox_crown | open_shoulder_mast | conditional-choice | drum ⊗ pedestal 非法（重采/回退 open） | Slot B |
| `drive_input` | enum | offset_crank / spline_crank / rim_handwheel | offset_crank | conditional-choice | spline 仅 clamp∨(tripod∧body≠drum) | Slot C |
| `carrier` | enum | plate_swing / bar_fork_swing / fixed_sleeve | plate_swing | choice | procedural sampler | Slot D |
| `bucket_count` | int (mult) | plate{4,6} / bar{2,4} / sleeve{4,6} | 4 | conditional | 域随 carrier；小 N 高频 | S1/S2/S3/S4/S8 |
| `palette_style` | enum | 5 组（见 Slot palette） | mint_enamel | choice | procedural sampler | ⑥ |
| `input_reach_scale` | float | [0.88, 1.12] | 1.0 | independent | 均匀采样后 clamp；缩放曲柄臂长/轮缘半径 | S1 L29；S2 L122-130；S7 L29-33 |
| `carrier_radius_scale` | float | [0.94, 1.10] | 1.0 | independent | 缩放 pivot 环/横杆半长/套管尖半径 | S1 L25；S2 L281-286；S8 L34 |
| `tube_length_scale` | float | [0.90, 1.10] | 1.0 | independent | 缩放吊管/吊杯纵剖面 | S1 L140-152；S2 L67-96 |
| `gear_ratio` | float | derived | 4.0 | equation | `= 4.0`（S1/S5/S7 mimic multiplier；drum 无 mimic 时不用） | S1 L351 |
| (—) | constraint | — | — | inequality | 地面净空：非 clamp 时 `reach·s_r + grip_r ≤ crank_mount_z − 0.010`，违反→按比例回缩 `input_reach_scale`；clamp 豁免（源即下探台沿） | S2/S6 行为 |
| (—) | constraint | — | — | inequality | 吊管内缘清立柱/主轴：`R·s_c − tube_od/2 ≥ spine_half_width(body) + 0.006`，违反→上调 `carrier_radius_scale` 下限回缩 | S1 L354-L402 |
| (—) | constraint | — | — | inequality | 邻桶间距：`2·R·s_c·sin(π/N) ≥ bucket_od + 0.004`，违反→拒绝重采 N（实际域内恒满足，declared 守卫） | S4 L348 |
| `input_standoff` | float | derived | — | equation | `= max(source_standoff(body), body_half_extent_in_band(body, crank_z ± sweep_r) + input_inboard_depth + 0.004)`；曲柄 boss 长度与 `crank_bearing` collar 位置/长度均由它派生（单一真源） | S1 L28（0.064）；S2 L231（0.038）；S1 L41-L50 / S5 L41-L62（放样剖面）；S7 L176-L181,L327-L332（轮缘+滚套包络） |

连续尺寸采样契约：先采 3 个 independent scale（均匀）→ 派生 `gear_ratio`（equation）→ 投影 inequality（地面净空回缩 reach、立柱净空回缩 carrier radius）→ conditional 域（body/drive/bucket_count 随上游 enum）在采样前解析。全部在 `resolve_config` 求解，builder 不再失败。

## 7.5 编译预算 / compile budget

**自报预算：≤ 20 s/seed。** 依据：与实测通过的同族模板 centrifuge_machine1 同级（cadquery 放样壳 + 布尔载具盘）；本模板分档 tessellation——载具/齿箱 mesh tolerance 0.0008–0.0014（源用 0.0005–0.0008，刻意放宽）、lathe segments 40–48（小半径特征 ≤32 段语义：管/环剖面点少）、N 个相同吊管/吊杯**复用同一个 Mesh**（S2 已示范 `bucket_mesh` 单次构建）。超预算先降 tolerance/segments 再迭代。sweep watchdog 用默认 60 s（3× 预算）。

## Multiplicity / Copy Logic

**唯一轴：`bucket_count`（载具位数 N）**
- `count_param`: `bucket_count`；源锚点 N=2（S3 单横杆）、N=4（S1/S2 十字）、N=6（S4 星盘）。source map 建议产品域 2-8；本模板按 carrier 的 source-backed 布局取 **plate{4,6} / bar{2,4} / sleeve{4,6}**（并集 {2,4,6}），测试偏小（4 高频）。sampling domain 权重：每 carrier 内小 N 3 : 大 N 2。
- copied object：plate = 载具孔/槽/boss 簇（mesh 内循环）+ `bucket_{i}` part（pivot_pin+collar+tube_shell）；bar = 叉耳对+销视觉 + `bucket_{i}` part（bucket_shell）；sleeve = `tube_holder_{i}`+`tube_sleeve_{i}` rotor 视觉（无 part）。
- naming：稳定后缀 `_{i}`；placement：径向 `angle = i·tau/N` 等分、共享 pivot 半径 `R·s_c`；joint policy：swing 载具**每桶 1 个 REVOLUTE**（`bucket_swing_{i}`，切向轴，plate [0,1.05]/bar [0,1.257]），sleeve **不新增关节**（`rotor_spin` 唯一）。
- source/gating：S1(4)/S3(2)/S4(6)/S8(loop)；N 域 gated by carrier（conditional）。
- 无第二根 multiplicity 轴（脚数 3/4、辐条 5、肋 12 为 module-local 固定常数，不暴露 `*_count`）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | (a) table_clamp 增 `clamp_screw` part+PRISMATIC（S2）；(b) drum body 增 `drive_shaft` part+CONTINUOUS 串联链（S2）；(c) swing 载具 N×bucket part+REVOLUTE vs sleeve 载具零子 part（S8）；(d) offset/rim 输入带自转柄套/滚套 part vs spline 单 part（S1/S2/S7）。全部 forked_anchor source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：单轴 `bucket_count`，N∈{2,4,6}（域随 carrier），小 N 高频。 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 输入 CONTINUOUS 水平轴（x 侧装 S1 / y 正面装 S2——同边换轴向）；rotor CONTINUOUS z **mimic ×4**（S1/S5/S7）vs **独立**（S2 链）；bucket REVOLUTE 切向 [0,1.05]/[0,72°]；clamp PRISMATIC z；knob/grip 自转 CONTINUOUS。每种在 sweep 出现（axis_realization 复核）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | body_form 3 原型全 source-backed（Volumetric Envelope Form ×3：低鼓肩+锥立柱 S1 / 大腹全包齿箱 S5 / 立盘鼓+crown S2），登记进 slot_choices。载具三形（盘/杆/斜臂）亦为形态可辨但记在 Slot D（①②主导）。 |
| ④ 表面装饰 | 原型不变叠加细节 | 有(record_only) | 铭牌+红蓝标（S1 L211-228）、maker plate+盖钉（S2 L205-222）、盖板/缝线/4 钉/3 铸肋（S5 L251-308）、柄套 12 肋（S1）、滚套 10 肋（S7）。全为宿主视觉、由宿主面位派生（③→⑤→④：装饰坐标从所选 body 放样剖面/盖面派生，肋贴放样面），不悬空、不做独立 part。装饰数量档固定（source 常数）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `input_reach_scale`[0.88,1.12]、`carrier_radius_scale`[0.94,1.10]、`tube_length_scale`[0.90,1.10]（§7）。运动包络（非 continuous 关节逐条）：`bucket_swing_i` 轴=切向、开向=径向外+上、[闭合 0, plate 1.05 / bar 1.257]，qc_samples [0,0.65,1.0]（S1）；`clamp_adjustment` 轴 +z、开向=压盘上行、[−0.010,0.015]。continuous（crank/wheel/knob/grip/shaft/rotor）整圈不穿模。`motion_test_plan`：run_tests 调 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32–72 按关节数, ignore_fixed=True)` + targeted `ctx.pose`：输入 90° 柄/轮可见位移；knob/grip 自转肋位移；rotor 受 mimic（open/enclosed pose crank 0.3 → 桶位移）或直接 pose（drum）；每 N 桶 upper 外摆（径向+z 增量）；clamp 压盘行程闭合。无 sampled-pose exemption。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette（mint_enamel / aged_nickel_wood / black_japanned_brass / cream_lab_enamel / hammertone_green）；材质大类 painted-enamel + metal + glass（plate 吊管）+ wood（spline/柄）+ rubber（脚/滚套）≥ ceil(0.5×5)=3 覆盖。 |

**收尾自检**：batch 0-9 渲染须肉眼见：三种支撑（踏座/台钳/三脚）、三种齿箱形态拉得开、曲柄/样条柄/手轮可辨、盘/杆/斜臂载具与 2/4/6 位不同、玻璃 vs 金属管、配色变化、摆桶全程外摆不穿模。

## 采样与覆盖审计

总组合数：support×body 合法对 8（pedestal×2 + clamp×3 + tripod×3）；drive 合法域（pedestal 组合 2 drive、clamp 组合 3、tripod×drum 2、tripod×非drum 3）→ Σ = 2·2 + 3·3 + 1·2 + 2·3 = **21** support×body×drive；× carrier-N 6（3 carrier × 各 2 N 档）× palette 5 = **630**（未计连续 scale）。>300 ✓。

理由：主多样性来自离散 slot（支撑骨架、齿箱形态+传动链、输入机构、载具机构+N），连续 scale 仅微调比例。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)` 加权离散采样 + 均匀连续采样；seed=0 不特殊；无 curated/modulo 主表；无 regression overrides。
Topology target：1000-seed slot tuple 覆盖 report-only；离散空间 630、gating 少，预期覆盖 >300。
Procedural Sampling / Sweep Plan：采样顺序 support → body（domain gated by support）→ drive（gated by support/body）→ carrier → N（gated by carrier）→ palette → scales；全部 gate 在 `resolve_config` 内先解析再落 config；random sweep 0-15 fast / 16-35 final + corner；viewer 目检 0-9。
Controlled local parameterization：`input_reach_scale` / `carrier_radius_scale` / `tube_length_scale`（§7 范围），全部 clamp+inequality 回缩，不破坏 rotor/shaft MatingContract、captured-pin 捕获、multiplicity 等分布局。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权 choices（support 2:2:1；body drum 偏 clamp/tripod；drive offset 2:spline 2:wheel 1 域内；carrier 2:2:1；N 小偏多；palette 均匀） | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | drum⊗pedestal 非法；spline 仅 clamp∨(tripod∧非drum)；N 域随 carrier；地面净空/立柱净空 inequality 回缩 | 无漂浮/穿模/贴地扫掠/桶越界 |
| controlled local variation | 3 scale clamp + 回缩 | 比例变化不破接口、净空、joint origin、类别 identity |
| regression overrides | none | — |
| random sweep | 0-15 fast, 16-35 final, + corner | contract failures; axis_realization 每 slot 值都出现; viewer 0-9 |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 3 | yes | yes | ①（clamp 带 PRISMATIC part） |
| body_form | 3 | yes | yes | ③ 主体形态家族（drum 兼 ①②） |
| drive_input | 3 | yes | yes | ②（part 数 1/2 各异） |
| rotor_carrier | 3 (+N) | yes | yes | ②+multiplicity（sleeve 为 ① 减边） |
| palette | 5 | yes | yes | ⑥ |

拓扑审计（跨族组合核算，源 map "source-family gated until downstream spec review" 在此裁决）：
- 归一化 mount 平面（support 报 body_mount_z；body 底截面覆盖 support 顶足迹并容许同 part 轻微嵌入，仿 S2 spine∪盘）使 8 个 support×body 组合几何安全；drum⊗pedestal 排除（见兼容矩阵）。
- 输入口由 body 输出（S1 侧 x / S2 正面 y），输入模块 yaw 映射——跨族（如 handwheel 装 drum 正面）为同接口换装，轴销/轴承硬件随口移动，origin honesty 保持。
- 曲柄/手轮扫掠平面与载具吊摆包络按源常数核算：侧装扫掠平面 |x|≈0.07 在立柱/三脚柱外；正面扫掠平面 y≈−0.05 在盘体/桶群 y 包络外（S2 源即此行为）；地面净空 inequality 兜底。

## Form Dependency Contracts

本模板**无受控外推③**：3 个 `body_form` 与 3 个 `carrier` 形态全部 direct source-backed（各自 accepted record/revision + 精确行号见 §4 / §14），主体放样母线与其配套 bearing/boss/mast/开口边界共源自同一份样本，不存在「只换主体不换容纳边界」的风险面。故 §4.1 契约表不适用。

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| (none — 无 `world_knowledge_extrapolation` ③ candidate) | — | — | — | — | — | n/a |

## Compatibility Gates

| gate | 条件 | deny / 投影 | 理由 |
|---|---|---|---|
| G1 `drum ⊗ pedestal` | `body_form=drum_gearbox_crown ∧ support_base=weighted_pedestal` | **deny**（采样期回退 open_shoulder） | 立盘鼓齿箱是 002 台钳/三脚族的铸件；坐到 001 矮踏座上会把曲柄口压到踏座平面以下，且源池无此组合的支撑证据。 |
| G2 spline 输入域 | `drive_input=spline_crank ∧ ¬(clamp ∨ (tripod ∧ body≠drum))` | **deny**（回退 offset/handwheel 加权采样） | 002 样条曲柄扫掠半径 ≈0.25 m；只有台钳（悬台沿）或高位侧装齿箱（三脚+非鼓）才有真实地面净空，否则曲柄扫地。 |
| G3 N 域随 carrier | `bucket_count ∉ CARRIER_COUNTS[carrier]` | **deny**（域按 carrier 解析：plate{4,6} / bar{2,4} / sleeve{4,6}） | 每个 N 都必须有 source-backed 布局（S1=4 / S3=2 / S4=6 / S8=loop）；不开放无资产整数。 |
| G4 地面净空 | `reach·s_r + grip_r > crank_mount_z − 0.010`（非 clamp 族） | **投影**：按比例回缩 `input_reach_scale` | Rule 5：手动输入整圈扫掠不得触地。 |
| G5 立柱净空 | `R·s_c − tube_od/2 < spine_half_width(body) + 0.006` | **投影**：上调 `carrier_radius_scale` | 吊管内缘须清立柱/主轴。 |
| G6 邻桶间距 | `2·R·s_c·sin(π/N) < bucket_od + 0.004` | **投影/拒绝重采** | 相邻吊桶 closed/mid/max 全程不穿模（实际域内恒满足，declared 守卫）。 |
| G7 输入 boss 净空 | `input_standoff < body_half_extent_in_swept_band + input_inboard_depth + 0.004` | **投影**：按该不等式抬升 `input_standoff`（曲柄 boss 加长，bearing collar 随动） | 手轮轮缘/滚套与其安装面共面，会扫进比 001 开放肩部更宽的齿箱（enclosed 半宽 0.066 / drum 盖面 0.031）。详见 §13。 |

跨来源重组说明：源 map 的 "support/input/carrier families remain source-family gated until downstream spec review" 由本节裁决——8/9 个 support×body 与 21/27 个 support×body×drive 组合经 mount 平面归一化、输入口接口量与 G4/G5/G7 净空证明后放行；其余按 G1/G2 排除。**不开放未验证笛卡尔积**。

## Combination Domain

- diversity_profile / reason: **`standard`** — 诚实核心词汇 = 3 支撑骨架（含 clamp 的 PRISMATIC 子件）× 3 齿箱形态（含 drum 的 drive_shaft 串联链）× 3 手动输入机构（1-part vs 2-part）× 3 载具机构（2 摆桶 + 1 零-part 刚性套筒），经 G1/G2 gate 后 = 63。未虚构轴、未靠 N 抬高。
- core axes / cartesian count / gate-filtered legal count: `support × body × drive × carrier` = 3×3×3×3 = 81 raw cartesian → **gate-filtered legal = 63**（支撑×齿箱合法对 8；再按 G2 展开 drive：pedestal×2 body×2 drive=4、clamp×3×3=9、tripod×非drum 2×3=6、tripod×drum 1×2=2 → 21 个 support×body×drive；×3 carrier = **63**）
- multiplicity axes / admitted integers / reachable integers / min-mid-max boundaries: 1 根轴 `bucket_count`；admitted = 观测锚点 `{2,4,6}`（域随 carrier，G3）；reachable = 全部 3 个（sweep `axis_realization` 实测 2:13 / 4:23 / 6:12）；min=2 / mid=4 / max=6。本模板**不外推** N（7/8 无 source-backed 布局，故未开放）。
- raw cartesian count / gate-filtered legal count: 21 support×body×drive × (3 carrier × 各 2 个 N) = **126** / gate-filtered legal = **126**
- excluded: palette（5 档）、材质大类、host-conformal ④装饰、连续尺寸（3 个 scale）——均**不计入** core 与 raw。（旧稿 "630" 把 palette ×5 乘进总数，属计数口径错误，此处纠正。）
- profile floor / recommended target / exception: standard 硬下限 **48**；实际 core = **63 ≥ 48** ✓ → **无需 hash-bound 人工例外**。

## Visual Risk

- **`multi_joint`（主风险）**：最多 13 个非-FIXED 关节（N=6 桶 + 输入 2 + rotor 1 + drive_shaft 1 + clamp 1）；sampled-pose 预算用 `max_pose_samples=32–72`（按关节数）控制，N 个桶全程互不穿模由 G6 守卫。
- **`curved_fit`**：`LatheGeometry` 玻璃吊管、cadquery loft 中空吊杯、torus revolve 轮缘均为曲面配合；禁止降级为 Box/Cylinder（Rule 3）。
- **类别特有 1 — 捕获销**：crank/knob/grip/bucket/clamp 均为 captured-pin，豁免 `mating=` 但必须 element-scoped `allow_overlap` + origin 落硬件；**零 whole-part allowance**（sweep `allowance_audit` 实测 46 条全部 element-scoped、suspicious=[]）。
- **类别特有 2 — mimic 随动**：001 族 `rotor_spin` 为 `Mimic(input, ×4)` 受迫关节，sampled-pose 只采自由关节，必须用 targeted `ctx.pose({input:0.3})` 证明转子随动。
- **类别特有 3 — 输入扫掠贴地/穿箱**：G4（地面）+ G7（齿箱）两条净空不等式；G7 是跨族重组（手轮装宽齿箱）的专属风险面，源池从未构建该组合。
- **类别特有 4 — 悬空**：`fixed_sleeve` 的套筒与三脚胶垫为宿主 visual，必须与斜臂 boss / 脚外端实体相交，否则触发 part-internal island。

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（support_base、body_form、drive_input、carrier、bucket_count、palette_style）。
- `config_from_seed` 对所有普通 seed（含 0）deterministic procedural sampling；无 curated 主表、无 override。
- compatibility gating 在 `resolve_config`：drum⊗pedestal、spline 域、N 域、两条 inequality 回缩。
- 3 个连续 scale 均 clamp，不破接口/净空/joint origin/multiplicity。
- 关键 MatingContract：`rotor_spin`（bearing_cap|shaft ↔ spindle|rotor_hub）、`shaft_rotation`（top_bearing ↔ shaft）存在且过 gap 检查；captured-pin 关节（crank/knob/grip/bucket/clamp）豁免 mating 但有 element-scoped allow_overlap + origin 落硬件。
- 关键关节 type/axis/range：输入 CONTINUOUS 水平轴（x|y 随 body）；`rotor_spin` CONTINUOUS (0,0,1)（mimic ×4 或独立随 body）；`bucket_swing_i` REVOLUTE 切向 [0, 1.05|1.257]；`clamp_adjustment` PRISMATIC z [−0.010,0.015]。
- copied objects 遵循 `_{i}` 命名 + `i·tau/N` 径向放置 + 共享 Mesh。
- 专项：无 lid/电机件；swing 桶数=config.bucket_count；sleeve 配置无 bucket_* part/joint；手动输入件存在且可动。

## Reject cases

- 出现罩盖/lid 关节或电机外观（混入 centrifuge_machine1）→ reject。
- 输入关节缺失或退化为 FIXED/REVOLUTE 限位（手摇身份丢失）→ reject。
- `rotor_spin` 不是 CONTINUOUS z，或 drum 链缺 drive_shaft → reject。
- 桶/套管数与 `bucket_count` 不符，或非等分布置（转子不平衡）→ reject。
- 摆桶静止不竖直/上摆方向反/upper 处穿载具或邻桶 → reject。
- 曲柄/手轮扫掠穿支撑（非 clamp 族贴地）→ reject（inequality 失守）。
- 载具盘/齿箱放样降级为 Box、玻璃 lathe 管降级为 Cylinder → reject（违 Rule 3）。
- 装饰（铭牌/盖板/肋/钉）做成独立 FIXED part 或悬空不贴宿主面 → reject（违 Rule 1/4）。
- clamp_screw 无捕获（悬空）或行程穿上颚 → reject。

## 与相邻类别的边界

- 不该混入 centrifuge_machine1（powered benchtop）：machine2 无罩盖、无 lid 关节、无电机；驱动必须是曲柄/手轮 + 裸露转子。
- 不该混入 hand mixer / egg beater：mixer 无试管载具、无立式吊管；machine2 转子带对称试管位。
- 不该混入 drill press / bench grinder：这些无吊摆试管且主轴水平/带刀具。
- 不该混入 spinning fan：fan 是叶片，无吊管载具、无手摇齿箱。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_THEN_TEMPLATE 连续通道（无审核停点）。源 map 的 "source-family gated until downstream spec review" 在 §9 拓扑审计裁决：8/9 support×body 合法、drum⊗pedestal 与 spline 低口组合排除。8/8 样本全采纳。 |

## 模板实现备注（可选）

- 输入模块统一 x 轴局部约定作图，joint origin yaw 映射到 body 输入口（drum 正面 y）；spline 源点做 rotZ(−90°) 预变换。
- 共享量单源化：SUPPORT_MOUNT_Z / 输入口 (xyz,yaw) / rotor 挂点 z / crank_bearing 位置全部由 support/body 模块函数返回，不许两处手写。
- captured-pin allow_overlap 全部 element-scoped（rotor_carrier×pivot_pin、grip×handle_pin、grip_roller×wheel_body、wheel_body×body_shell、screw_shank×body、shaft/spindle×bearing）。
- N 个吊管/吊杯共享一个 Mesh（每 seed 只构建一次 cadquery/lathe 几何）。
- drum×handwheel / clamp×plate_swing 等跨族组合是新实现面，sweep corner 重点观察。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | pedestal+shoulder+offset_crank+plate carrier | rec_..._001__png__airflex_..._2c7344d0f313... | L25-L402 | 001 家族全部共享几何 + mimic 传动 + 玻璃吊管 |
| S2 | A/B/C/D | clamp+drum+spline_crank+bar carrier | rec_..._002__png__airflex_..._da960e4e06e9... | L24-L405 | 002 家族全部共享几何 + drive_shaft 链 + clamp PRISMATIC |
| S3 | D | bar_fork_swing N=2 | rec_picturex0611_centrifuge_machine2_fork_bucket_n2_20260714 | L261-L354 | 单横杆 2 桶布局 |
| S4 | D | plate_swing N=6 | rec_picturex0611_centrifuge_machine2_fork_bucket_n6_20260714 | L75-L131,L348-L396 | 星盘 60° 循环发射 |
| S5 | B | enclosed_rounded_gearcase | rec_picturex0611_centrifuge_machine2_fork_enclosed_gearcase_20260714 | L41-L91,L251-L308 | ③ 全包齿箱 + ④ 盖板/缝/钉/肋 |
| S6 | A | bench_tripod | rec_picturex0611_centrifuge_machine2_fork_tripod_base_20260714 | L46-L68,L203-L227 | 立柱+毂+3 脚支撑 |
| S7 | C | rim_handwheel | rec_picturex0611_centrifuge_machine2_fork_handwheel_drive_20260714 | L158-L199,L289-L357 | torus 轮缘手轮 + 自转滚套 |
| S8 | D | fixed_sleeve_carrier | rec_picturex0611_centrifuge_machine2_fork_rigid_tube_carrier_20260714 | L29-L37,L83-L137,L307-L364 | 35° 固定角臂+套管视觉载具 |
