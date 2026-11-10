# pictureX_0611_compass — modular spec

## 元信息

| 项 | 值 |
|---|---|
| slug | `pictureX_0611_compass` |
| template path | `agent/templates/pictureX_0611_compass.py` |
| test path (optional) | — (sweep-pipeline 为验收信号，暂不写 pytest) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## Category Binding

category_slug: pictureX_0611_compass · template_slug: pictureX_0611_compass ·
mechanism_profile: magnetic_capsule_rotating_indicator_with_hinged_lid ·
export_namespace: pictureX_0611_compass
diversity_profile: `constrained` ·
profile_reason: 磁性罗盘的身份脊柱是**固定的**——同轴 bezel + 中央枢轴上自由旋转的磁性
指示件 + 后铰链盖，三者恒在且不可替换（换掉任何一个就不再是罗盘）。诚实核心词汇 =
4 载体形态 × 3 指示机构 × 家族匹配盖 = **30 个 gate 后合法组合**（笛卡尔 60，gate 拒 30），
由已确认的 8 条记录池（1 origin + 7 单轴 fork）界定，不虚增。无 multiplicity 轴：
tick/grip 是宿主共形装饰（§8）。已登记到 `category_template_registry.json`
（`combo-audit` 实测 core legal=30 ≥ constrained 下限 16，floor_met=true）。

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (rated_by=picturex_0611_centrifuge_to_drafting_variant_confirmed_20260714) |
| source_index_policy | only adopted module sources are indexed below；全部 8 条样本均被采纳为 module source（无排除） |

阅读清单（全部 `revisions/rev_000001/model.py` 全文读毕）：

1. `rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c`（origin，round pocket）
2. `rec_picturex0611_compass_fork_rectangular_baseplate_20260714`
3. `rec_picturex0611_compass_fork_square_lensatic_case_20260714`
4. `rec_picturex0611_compass_fork_full_dial_card_20260714`
5. `rec_picturex0611_compass_fork_liquid_damped_capsule_20260714`
6. `rec_picturex0611_compass_fork_mirror_sighting_cover_20260714`
7. `rec_picturex0611_compass_fork_sight_wire_cover_20260714`
8. `rec_picturex0611_compass_fork_wrist_mount_cradle_20260714`

## 核心身份

便携**磁性方向罗盘**（口袋/野战/徒步导航仪）：一个带刻度盘（degree ticks + N/E/S/W 基
点字母）的浅圆形罗盘胶囊，中央枢轴上有**真实自由旋转的磁性指示件**（双色磁针或整张
旋转罗盘卡），上方是可绕 z 轴整圈旋转的 bezel（含透明玻璃镜片），一侧由**真实铰链**
连接保护盖（家族内每个 case 都有盖）。载体形态从圆形口袋壳、方形野战壳、透明徒步底
板到腕带托架。全部关节均为 REVOLUTE：bezel/indicator/hanging-ring 绕 z，盖绕 x 铰链。

**身份护栏**：永远是磁性方向罗盘 —— 不是制图圆规（drawing compass）、不是手表/时钟、
不是仪表 gauge、不是 GPS、不是化妆粉盒。必须有：可读的刻度盘 + 自由旋转（±π）的磁性
指示件 + 真实铰链盖。小件尺度（外径 ~80mm、壁厚 1-3mm），接触公差按亚毫米设计。

## 槽位 + 候选模块表

### Slot A：case_platform（根部件；③ 主体形态家族 + ① 骨架）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| round_pocket_case | forked_anchor | rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c | L27-L44（lathe revolve 壳）, L130-L247（dial deck/ticks/cardinals/hinge/latch/lug）, L311-L316+L360-L373（hanging_ring 部件+joint） | eligible | 冲压阶梯圆壳（cq revolve profile），凹陷 dial deck，后缘铰链塔，前缘 ring lug + 独立 hanging_ring 部件（REVOLUTE z ±75°）；form_subtype=Volumetric Envelope Form |
| square_lensatic_case | forked_anchor | rec_picturex0611_compass_fork_square_lensatic_case_20260714 | L39-L56（rounded-square 壳+圆形 well）, L124-L269（corner screws/hinge/latch/lug）, L337-L343+L380-L391（hanging_ring） | eligible | 圆角方形野战壳挖圆形胶囊井，四角螺钉装饰，保留 hanging_ring；form_subtype=Planar Boundary Form |
| rectangular_baseplate | forked_anchor | rec_picturex0611_compass_fork_rectangular_baseplate_20260714 | L41-L68（透明底板+capsule wall/floor）, L136-L294（dial/ruler ticks/direction arrow/hinge on capsule rim） | eligible | 矩形透明徒步底板 + 中央圆柱胶囊墙；无 hanging_ring；边缘 ruler 刻度 + 红色行进方向箭头（host-conformal 装饰）；form_subtype=Planar Boundary Form |
| wrist_cradle_case | forked_anchor | rec_picturex0611_compass_fork_wrist_mount_cradle_20260714 | L79-L109（curved wrist cradle）, L112-L127（strap band）, L272-L326（cradle/lugs/spring bars/straps 全为 case 融合 visuals） | eligible | 圆壳 + 腕托曲面板 + 两侧表耳/弹簧杆/橡胶腕带（不动件全部 fused 进 case visual，Rule 1）；无 hanging_ring；form_subtype=Macro Surface Construction（腕带载体改变整体读法） |

> hanging_ring 不是独立 slot：它是 round_pocket_case / square_lensatic_case 两个 case
> module 的内部 emission（part+joint 由 case module 派生），rectangular_baseplate /
> wrist_cradle_case 无此部件 —— ① 骨架差异记录在 §8.5。

### Slot B：indicator（② 关节/机构层）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| two_color_needle | forked_anchor | rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c | L73-L77（needle half 多边形挤出）, L273-L292（north/south pointer + hub）, L332-L345（case_to_needle REVOLUTE z ±π） | eligible | 双色三角磁针（cq polyline extrude）+ 钢 hub，坐于中央 pivot pin 顶面，自由 ±π |
| full_dial_card | forked_anchor | rec_picturex0611_compass_fork_full_dial_card_20260714 | L73-L98（card disk + north triangle）, L254-L326（card ticks/cardinals/hub）, L366-L379（case_to_card REVOLUTE z ±π） | eligible | 整张旋转罗盘卡：黑色薄盘 + 36 tick + 4 基点字母 + 夜光北向三角随卡旋转；case 侧不再印刻度 |
| liquid_damped_needle | forked_anchor | rec_picturex0611_compass_fork_liquid_damped_capsule_20260714 | L79-L99（sealed capsule bowl）, L102-L107（damping vane）, L232-L254（bowl/fluid/gasket case visuals）, L331-L368（vane+luminous tip needle visuals） | eligible | two_color_needle + 密封透明液阻胶囊罩（case visual）+ 阻尼叶片/夜光尖（needle visual）+ 垫圈环；针长缩短以贴合扁平 bowl 包络 |

### Slot C：cover（③ 盖体形态家族 + ② 铰链）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| domed_lid | forked_anchor | rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c | L47-L64（球冠薄壳+卷边 rim+铰链叶）, L294-L309（cover 部件）, L346-L359（hinge joint） | eligible if case ∈ {round_pocket, wrist_cradle} | 冲压空心球冠盖（sphere 布尔壳），rim annulus；form_subtype=Volumetric Envelope Form |
| mirror_sighting_lid | forked_anchor | rec_picturex0611_compass_fork_mirror_sighting_cover_20260714 | L47-L92（framed panel+sight slot+notch）, L94-L117（sight line + mirror face）, L348-L375（cover 部件） | eligible if case ∈ {round_pocket, wrist_cradle, square_lensatic} | 平板照准盖：圆角矩形板中央开照准槽 + 远端观察缺口 + 内侧镜面 + 蚀刻准线；form_subtype=Planar Boundary Form |
| sight_wire_lid | forked_anchor | rec_picturex0611_compass_fork_sight_wire_cover_20260714 | L47-L61（防护环 frame+横梁+铰链叶）, L64-L80（sight wire + 夜光 dot）, L312-L339（cover 部件） | eligible if case ∈ {round_pocket, wrist_cradle, square_lensatic} | 开放式准星丝盖：环形框 + 横梁 + 照准丝 + 夜光点（丝改为盖平面内跨越开口，消除闭合戳穿玻璃——见 Reject #6）；form_subtype=Macro Surface Construction |
| square_flat_lid | forked_anchor | rec_picturex0611_compass_fork_square_lensatic_case_20260714 | L58-L69（rounded-square 平盖+铰链叶）, L322-L335（cover 部件） | eligible if case == square_lensatic | 与方壳同轮廓的圆角方形平盖；form_subtype=Planar Boundary Form |
| flat_clear_lid | forked_anchor | rec_picturex0611_compass_fork_rectangular_baseplate_20260714 | L85-L94（透明圆盘盖+铰链 tab）, L352-L369（cover 部件） | eligible if case == rectangular_baseplate | 透明亚克力平圆盘盖，铰接于胶囊墙后缘 |

硬约束核对：3 个 slot；每 slot 3-5 candidates；每个 candidate 都有 forked_anchor 的
`model.py:Lx-Ly` 来源；无 world_knowledge_extrapolation candidate（8 条 5 星源已覆盖
主体形态空间）。bezel（含玻璃镜片、防滑齿）是每个 case module 的固定内部子结构
（module-local fixed structure，全 8 条源同构：origin L67-L70+L249-L271），不单列 slot。

## Form Dependency Contracts

本 spec **无受控外推③ candidate**：Slot A 的 4 个 case 原型与 Slot C 的 5 个 cover 原型
全部 source-backed（每个都有 accepted origin/fork record + 精确 `model.py:Lx-Ly`，见
§4 槽位表），因此不需要 world_knowledge_extrapolation 的 master-descriptor 契约。

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| （无外推③） | — | — | — | — | — | n/a — 全部 ③ 为 direct source-backed |

尽管无外推，**耦合派生纪律仍然适用**（③→⑤→④，禁止"镜片换六边形而镜框仍矩形"）：

| 主体形态 | 单一真源 | 必须共同派生的消费者 | validator |
|---|---|---|---|
| case 顶面 `case_top_z` | `resolve_config` 单点派生（round/square/wrist=壳唇；baseplate=`plate_th+cap_h` 胶囊墙顶） | bezel 座 `bez_z`、`lens_bottom_z`、`bezel_top_z`、side_latch 高度、hinge tower 立柱 | `expect_gap(bezel_ring ↓ case_top_visual)`；`fail_if_isolated_parts` |
| bezel 环径向带 | `bez_ring_in/out` 随 case 原型派生：round/square/wrist 跨壳唇；baseplate 跨胶囊墙顶面 `[cap_in, cap_out]` | glass_lens/seat/grips 半径、`bezel_swept_r`、`hinge_y` | ring 必须压在 case 顶面上（否则 bezel 成孤立件） |
| 罗盘栈顶 `stack_top_z` | `max(bezel_top_z, bowl_apex_z)`（液阻 seed 时 dome 最高） | `hinge_z` → cover 闭合姿态净空 | 闭合姿态 `ctx.pose` + sampled collision |
| capsule dome 包络 | `bowl_r` / `bowl_sphere_r` / `bowl_base_z` | 透明窗归属（见 Reject #8 决议）、`stack_top_z`、fluid/vane 包络、gasket 环 | `bowl_r < bez_seat_in < bez_ring_in`；`expect_within(capsule_bowl ⊂ bezel_ring)` |

## 槽位图（slot graph）

pattern: parallel_children

```
case_platform (root, Slot A)
 ├─[REVOLUTE z ±π  @ case 顶面中心；MatingContract: case 顶面(positive_z) ↔ bezel_ring 底面(negative_z)]→ bezel（case module 内部固定子结构）
 ├─[REVOLUTE z ±π  @ pivot_pin 顶面；MatingContract: pivot_pin(positive_z) ↔ indicator hub(negative_z)]→ indicator (Slot B)
 ├─[REVOLUTE −x hinge @ 后缘铰链轴；captured-pin（销穿套）→ 按 Rule 2 grandfather，省略 mating，配 expect_contact + 元素级 allow_overlap]→ cover (Slot C)
 └─[REVOLUTE z ±75° @ 前缘 ring_pin；captured-pin（环套销）→ grandfather，同上]→ hanging_ring（仅 round_pocket / square_lensatic 由 Slot A module 派生）
```

- 所有活动件的 parent 都是 case_platform 根部件（parallel_children）。
- 接口点位：bezel 座 = case 顶面平面接触；indicator = pivot_pin 顶面平面接触（由源的
  "hub 包销" 改为 "hub 坐销顶"，保持部件树/primitive 不变、消除 captured 过盈，使该
  joint 可携带真实 MatingContract）；cover = 铰链轴（knuckles+pin+cover knuckle）；
  ring = 销轴。
- 互斥/派生：cover candidate 由 case choice 门控（见 §9 compatibility matrix）；
  hanging_ring 由 case choice 派生；liquid_damped_needle 在 case 上追加 bowl/fluid/
  gasket visuals（跨 slot 写入 case part，属 indicator module 的声明行为）。

## 每槽位 Module Emits / Interfaces

### Slot A / round_pocket_case（其余 case candidates 同构，仅几何不同）

| emits | 描述 | 来源 |
|---|---|---|
| parts | `case`（root：壳+dial deck+ticks/cardinals+north_index+pivot_pin+铰链塔+latch+ring lug/pin）、`bezel`（ring+glass_lens+grips）、`hanging_ring`（仅 round/square） | origin model.py:L130-L316 |
| internal joints | `case_to_bezel` REVOLUTE z ±π；`case_to_ring` REVOLUTE z ±75°（仅 round/square） | origin L318-L331, L360-L373 |
| upstream interface | —（root） | — |
| downstream interface | dial deck 中心 pivot_pin 顶面（供 indicator）；后缘铰链轴 hinge_y/hinge_z（供 cover）；case 顶面（供 bezel MatingContract） | origin L191-L217 |

### Slot B / two_color_needle（full_dial_card / liquid_damped_needle 同构）

| emits | 描述 | 来源 |
|---|---|---|
| parts | `magnetic_needle`（或 `dial_card`）：pointers/hub（或 card disk+ticks+cardinals+triangle+hub）；liquid 变体另将 bowl/fluid/gasket 追加为 case visuals | origin L273-L292；card L254-L326；liquid L232-L254+L331-L368 |
| internal joints | `case_to_indicator` REVOLUTE z ±π（源名 case_to_needle / case_to_card，模板统一 joint 名 `case_to_indicator`） | origin L332-L345 |
| upstream interface | hub 底面 negative_z 坐于 pivot_pin 顶面（MatingContract） | origin L286-L291（改编：包销→坐销顶） |
| downstream interface | 无 | — |

### Slot C / domed_lid（其余 cover candidates 同构）

| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`：盖体 mesh（闭合坐标系建模 + visual rpy=(−open,0,0) 呈开盖姿态）+ cover_knuckle 圆柱 | origin L294-L309 |
| internal joints | `case_to_cover` REVOLUTE 轴 (−1,0,0)，range [−open_angle, +8°]（0=开盖参考姿态） | origin L346-L359 |
| upstream interface | cover_knuckle 同轴套在 case hinge_pin 上（captured-pin，grandfather + expect_contact + 元素级 allow_overlap） | origin L304-L309, L509-L523 |
| downstream interface | 无 | — |

不动细节全部为 parent visual：ticks/cardinals/ruler 刻度/箭头/screws/cradle/straps/
mirror_face/sight_line/夜光点等（Rule 1，与 8 条源一致）。

## 活动机构与运动净空契约

四个 non-FIXED module 全部为 REVOLUTE，全部是完整实体（无 facade / 无测试投机几何）：

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| `bezel`（case_to_bezel） | 完整环：`bezel_ring`(cq annulus+seat 一体) + `glass_lens`(非液阻 seed) + N×`bezel_grip_i`；ring↔seat 径向重叠保证单一连通实体（不依赖 lens） | 环底面**整周压在 case 顶面**（round/square/wrist=壳唇；baseplate=胶囊墙顶面 `[cap_in,cap_out]`，环带 `[cap_in-0.0045, cap_out+0.0008]` 完全覆盖该面） | **真实 MatingContract**：case 顶面(positive_z) ↔ `bezel_ring` 底面(negative_z) | origin=(0,0,`bez_z`)；axis=(0,0,1)；范围 ±π（整圈 continuous 语义，以 REVOLUTE ±π 表达，源 L318-L331） | 整圈旋转：绕 z 的回转体，扫掠包络 = 自身；`hinge_y = bezel_swept_r + _KNUCKLE_R + 0.0003` 保证 grips 整圈不刮铰链塔（最小净空 0.3mm） | 无（真实面接触，非过盈） | `expect_gap(bezel_ring↓case_top_visual, [-0.0005,0.002])`；`fail_if_joint_mating_has_gap`；sampled poses |
| `indicator`（case_to_indicator） | `magnetic_needle`：`north_pointer`+`south_pointer`(cq polyline extrude)+`needle_hub`(+液阻: `damping_vane`+`luminous_north_tip`)；或 `dial_card`：`card_disk`+36×`card_tick_i`+4 基点+`north_triangle`+`card_hub` | hub 底面**坐在 `pivot_pin` 顶面**（源为"hub 包销"过盈，本模板改编为坐销顶 → 可携带真实 MatingContract、消除过盈） | **真实 MatingContract**：`pivot_pin`(positive_z) ↔ hub(negative_z) | origin=(0,0,`pivot_top_z`)；axis=(0,0,1)；范围 ±π | 整圈：指示件扫掠半径 < 窗口内径；液阻 seed 针长缩短至 0.0245·s 以贴合扁平 bowl 内包络 | 液阻 seed：`fluid_fill` × {`damping_vane`,`north_pointer`,`south_pointer`,`needle_hub`,`luminous_north_tip`} —— 磁针总成**浸没**于密封阻尼液（源 L622-L638 声明 `fluid_fill×damping_vane` 同类）；逐 element pair，无 whole-part | `expect_contact(pivot_pin,hub)`；`ctx.pose` 旋 90° 证位移；sampled poses |
| `cover`（case_to_cover） | 完整盖体（5 原型之一，全部 cq 实体：球冠薄壳/照准平板/环框+丝/方平盖/透明圆盘）+ `cover_knuckle` 圆柱 + 2×hinge leaf tab（tab 深 5.8mm，嵌入盖体 ≥2.4mm 并咬住 knuckle，源 leaf 深 7mm） | `cover_knuckle` 同轴**套在 case `hinge_pin` 上**，两侧由 `hinge_knuckle_0/1` 夹持 | captured-pin（销穿套）：几何上不存在两张轴对齐接触面 → 按 AUTHORING Rule 2 **grandfather 省略 `mating=`**，改以 `expect_contact` + element-scoped allowance 钉住 | origin=(0,`hinge_y`,`hinge_z`)；axis=(−1,0,0)；范围 [−`open_rad`, +8°]，**0 = 开盖参考姿态**，lower = 闭合 | closed/mid/max 全覆盖：`hinge_z = stack_top_z + cover_under_drop + 0.0007`，其中 `stack_top_z = max(bezel_top_z, bowl_apex_z)` —— 闭合时盖底面必然高于**罗盘栈真实顶点**（含液阻 dome），最小净空 0.7mm | `hinge_pin` × `cover_knuckle`（钢销**故意**被盖套捕获，源 L509-L515 同款） | `ctx.pose(closed)`：盖覆盖 dial 且中心 y/z 下降；`expect_contact(hinge_pin,cover_knuckle)`；sampled poses |
| `hanging_ring`（case_to_ring，仅 round/square） | `ring_loop`：large ring + eye + bridge 一体 cq union | eye 环**套在 `ring_pin` 上**，`ring_pin_head` 压帽防脱（head 由 `_ring_pin_top_z()` 单一真源派生，嵌入 0.2mm） | captured-pin（环套销）→ 同上 grandfather | origin=(0,`ring_pin_y`,`ring_z`)；axis=(0,0,1)；范围 ±75° | ±75° 摆动全程 eye 保持套住销（`expect_within(ring_pin ⊂ ring_loop, margin 0.0022)` @ ±60°） | 无 whole-part；ring/pin 为间隙配合 | `ctx.pose(±60°)` expect_within；sampled poses |

- 全部 intentional overlap **只列 exact element pair**（6 条，见 §模板实现备注），
  **零 whole-part allowance**、零 sampled-clearance exemption（Rule 5/7）。
- `run_tests` 调 `ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`
  （4 关节 → 1+4·4=17 ≤ 64 ≤ 128，符合 C′ 约定）+ 每机构 targeted `ctx.pose(...)`。
  sweep `motion_test_audit` 实测 `status=pass`（sampled + targeted 均覆盖，无 exemption）。

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_style | enum | 4 个 Slot A candidates | — | choice | deterministic procedural sampler | module table |
| indicator_style | enum | 3 个 Slot B candidates | — | choice | 同上 | module table |
| cover_style | enum | 5 个 Slot C candidates | — | conditional | 合法域由 case_style 门控（§9 矩阵）；非法时回退该 case 首选 cover | module table |
| palette_style | enum | nickel_silver / olive_field / black_polymer / antique_brass | — | choice | 同上 | §8.5 ⑥ |
| dial_tick_count | enum(④) | 24 / 36 | 36 | choice | 装饰数量档（major 每 3 根加长） | origin L149-L164 |
| bezel_grip_count | enum(④) | 16 / 24 | 24 | choice | 装饰数量档 | origin L261-L271 |
| radial_scale (s) | float | [0.92, 1.12] | 1.0 | independent | 均匀采样后 clamp；主径向尺度 | origin L27-L44 |
| height_scale (h) | float | [0.90, 1.15] | 1.0 | independent | 均匀采样后 clamp；主轴向尺度 | origin L27-L44 |
| open_angle_deg | float | [95, 120] | 112 | independent | 盖开角；joint range=[−open, +8°] | origin L20 |
| indicator_rest_deg | float | [−60, 60] | 24 | independent | 指示件静息朝向（纯姿态参数） | origin L274 |
| plate_length | float | [0.120, 0.148] | 0.130 | conditional+inequality | 仅 rectangular_baseplate；`plate_length ≥ 2.55·capsule_outer_r`，违反时向上 clamp | rect L22-L34 |
| plate_width | float | [0.052, 0.066] | 0.058 | conditional | 仅 rectangular_baseplate | rect L22-L34 |
| strap_length_scale | float | [0.90, 1.15] | 1.0 | conditional | 仅 wrist_cradle_case | wrist L112-L127 |
| bezel 几何 | float | derived | — | equation | ring_in/seat/glass_r/grip_r = 源常数 × s；**baseplate 变体 `ring_out = cap_out + 0.0008`**——环带必须跨到胶囊墙顶面 `[cap_in, cap_out]` 上（源 fork 把环留在内孔 → bezel 悬空孤立件，实测 gap 0.487mm，已修） | origin L67-L70；rect L71-L76 |
| bez_z / bezel_top_z | float | derived | — | equation | `bez_z = case_top_z`（环底面直接压在 case 顶面，全 4 case 同规则）；`bezel_top_z = bez_z + lens_top_local`（单一 helper）。**曾有的 baseplate `−0.0004` 偏移已删除**——它是无来源的 tuned constant（Contract 3e），只掩盖了"环带在内孔"的真缺陷 | origin L318-L325 |
| stack_top_z | float | derived | — | equation | `stack_top_z = max(bezel_top_z, bowl_apex_z)`——罗盘栈**真实顶点**单一真源（液阻 seed 时密封 dome 最高，非镜片） | 新增（Contract 3c） |
| hinge_z | float | derived | — | equation | `hinge_z = stack_top_z + cover_under_drop + 0.0007`——闭合姿态盖底面必然高于栈顶（Reject #1；液阻 seed 也不会撞 dome） | 改编（源 L346-L359 为常数） |
| pivot_top_z / needle 尺寸 | float | derived | — | equation | 针长/卡半径 = 源常数 × s；liquid 变体针长缩短至 0.0245s 以贴合扁平 bowl 内包络 | origin L273-L292；liquid L331-L368 |
| has_glass_lens | bool | derived | — | conditional | `= indicator_style != "liquid_damped_needle"`。**透明窗二选一**：液阻 seed 由密封 dome 充当唯一窗，bezel 平镜片不发射（见 Reject #8 决议） | liquid L79-L99 |
| capsule bowl 包络 | float | derived | — | inequality | `bowl_r < bez_seat_in < bez_ring_in`——dome 穿过 bezel 内孔且径向留净空（实测 bowl_r 0.0316 < seat_in 0.0334 < ring_in 0.0344）；fluid/vane 包络随 bowl 派生 | liquid L79-L99 |
| ring_pin_head z | float | derived | — | equation | `= _ring_pin_top_z(r) − 0.0002 + head_th/2`，`_ring_pin_top_z = ring_z + (0.0060·h)/2` 为**单一真源**。原实现 head 硬写 `ring_z + 0.0034·h`，与销顶仅在 h==1 时重合，h>1 即裂开 `0.0004·(h−1)` 成孤岛（Contract 3c，已修） | origin L236-L247 |
| (—) | constraint | — | — | inequality | 指示件扫掠半径 < glass_r − 0.002；cover 跨度 ≥ dial 半径（闭合覆盖 dial）；均在 resolve_config 内以 equation 派生保证，不留到 builder | 接口/clearance |

连续尺寸采样契约：先采 independent（s、h、open_angle、rest、plate、strap）→ equation
派生全部堆叠 z / 半径 → inequality 投影（plate_length clamp、bowl apex clamp）→
conditional 参数按 case_style 解析。全部在 `resolve_config` 完成。

## 编译预算 / compile budget

**25s/seed**。依据：8 条源 record 每条含 6-12 个 cadquery 布尔/revolve/text 实体（与
本模板单 seed 用量同量级），在库内实测属"典型模板 5-20s"档；text 字形（4 个基点字母）
与球冠布尔略重，取 25s 上限。分档 tessellation：cardinal text tol=1.2e-4、小件
（bezel/ring/needle）tol≤2e-4、主体壳 tol=2.5e-4-3e-4；ticks/grips 用 Box primitive
不走 mesh。无 N 复制大件，无 Mesh 复用需求。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达，不暴露 `*_count` 结构轴，也不通过
  循环复制模板级 part/joint。dial ticks / bezel grips / ruler 刻度 / strap 孔均为
  loop-emitted **宿主 visual 装饰**（④ 装饰数量档：dial_tick_count∈{24,36}、
  bezel_grip_count∈{16,24}），不产生独立 part 或 joint，不进结构 ① 轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 3-4 活动件两档：{bezel, indicator, cover, hanging_ring}（round_pocket / square_lensatic）vs {bezel, indicator, cover}（rectangular_baseplate / wrist_cradle）；全部 forked_anchor（origin L318-L373；rect L374-L419；wrist L392-L433） |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：无结构复制轴；tick/grip 计数属 ④ |
| ② 关节类型 | 边换 type/轴 | 有 | 全 REVOLUTE 但轴系/行程三型：z 整圈 ±π（bezel、indicator）、−x 铰链 [−open, +8°]（cover）、z 摆动 ±75°（hanging_ring）；forked_anchor（origin L318-L373）。indicator 内部再分针/卡/液阻三种机构读法（Slot B）。每型每 seed 都出现（bezel+indicator+cover 恒在；ring 在 round/square seeds 出现） |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | **登记进 slot_choices 的 ③ slot = Slot A（case）+ Slot C（cover）**。case 4 原型：round revolve 壳（Volumetric Envelope）/ rounded-square 壳（Planar Boundary）/ 矩形透明底板+胶囊（Planar Boundary）/ 腕带托架壳（Macro Surface Construction）。cover 5 原型：球冠壳（Volumetric Envelope）/ 照准镜平板（Planar Boundary）/ 环形准星丝框（Macro Surface Construction）/ 方平盖（Planar Boundary）/ 透明圆盘（Planar Boundary）。全部 forked_anchor（见 slot 表） |
| ④ 表面装饰 | 原型不变叠加细节 | 有 | dial ticks（24/36 档，major/minor 分级，半径由 dial_r 派生）、cardinal 字母（text mesh 贴 dial 面）、north_index、bezel grips（16/24 档，半径由 ring 派生）、ruler 刻度+红色行进箭头（仅 baseplate，位置由 plate L/W 派生）、四角螺钉（square）、夜光点/尖（sight_wire/liquid）、strap 孔与 keeper（wrist）。全部由宿主最终表面逐坐标派生（③→⑤→④），record_only + forked_anchor 来源 |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | s∈[0.92,1.12]、h∈[0.90,1.15]、plate L/W、strap scale、open_angle∈[95°,120°]。运动包络：`case_to_cover` 轴(−1,0,0)、开向 +z 后仰、[closed=−open_angle, +8°]，0=开盖参考姿态；`case_to_ring` 轴 z、[−75°,+75°]；`case_to_bezel`/`case_to_indicator` 轴 z、±π 整圈。motion_test_plan：run_tests 调 `ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`（无 exemption）+ targeted `ctx.pose`：cover 闭合姿态覆盖 dial 且下降、indicator 旋 90° AABB 位移、bezel 旋 90° grip 位移、ring ±60° 保持套销。无需 qc_samples 覆写（默认 {0,lower,upper,mid} 已含全部关键姿态） |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 4 palettes：nickel_silver（金属拉丝银）/ olive_field（军绿涂装金属）/ black_polymer（黑色聚合物+钢件）/ antique_brass(黄铜)。材质大类：metal、painted metal、plastic（聚合物壳+透明亚克力）、glass（镜片/胶囊）≥ ceil(0.5×4)=2 覆盖达标；dial 恒黑+白刻度，针恒 ivory/green（液阻加夜光绿） |

收尾自检：0-9 seed 渲染须肉眼可见 ≥3 种 case 原型、≥3 种 cover 原型、≥2 种 indicator、
≥3 palette；ticks 贴 dial 面不悬空；盖全程开合不穿模。

## 采样与覆盖审计

总组合数：case-cover 合法对 (2 round-family × 3) + (1 square × 3) + (1 baseplate × 1) = 10；
× indicator 3 = **30 个 slot choice tuple**；× tick 2 × grip 2 × palette 4 = 480 个离散
可见变体，连续尺度另计。

理由：真实类别空间就是"4 种载体 × 3 种指示机构 × 家族匹配的盖"；30 个拓扑组合已覆盖
8 条 5 星源锚点的全部主体形态边界，不虚增未被源支撑的组合。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
加权采样：case（round 0.34 / square 0.24 / baseplate 0.22 / wrist 0.20）→ cover 在该
case 合法域内均匀采样 → indicator（needle 0.40 / card 0.32 / liquid 0.28）→ palette /
tick / grip / 连续尺度。无 regression overrides。compatibility 由 `_COVERS_BY_CASE`
矩阵 + resolve_config 回退实现（非法 cover→该 case 首选 cover）。random sweep：
sweep-pipeline 0-35 + corner 阶段；viewer 目检 seeds 0-9。
Topology target：30 tuple 全可达（1000-seed 期望全覆盖）；<300 由真实组合空间上限
（源锚点 8 条、家族门控）解释，report-only。
Controlled local parameterization：radial_scale、height_scale、open_angle_deg、
indicator_rest_deg、plate_length/width、strap_length_scale；全部在 resolve_config
clamp；堆叠 z（bezel_z→bezel_top_z→hinge_z）、bowl 包络、针长、盖跨度均为 equation
派生，保证 InterfaceSpec/MatingContract 与闭合姿态在任意采样组合下成立。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | case→cover(gated)→indicator→palette→④档→连续尺度，全加权确定性 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | `_COVERS_BY_CASE`：round/wrist→{domed,mirror,sight_wire}；square→{square_flat,mirror,sight_wire}；baseplate→{flat_clear}；hanging_ring 由 case 派生 | 无悬空盖/盖-壳错配；ring 只在有 lug 的 case 出现 |
| controlled local variation | s/h/open/plate/strap 连续尺度 + clamp + 派生堆叠 | 比例变化不破坏 bezel 座接触、pivot 座接触、铰链闭合间隙、类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-15 fast → 0-35 final + corner；viewer 0-9 | contract failures；axis_realization 确认 4 case/5 cover/3 indicator/4 palette 都实现 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_platform | 4 | yes | yes | ③+① 主轴 |
| indicator | 3 | yes | yes | ② 机构轴 |
| cover | 5 | yes | yes | ③ 盖形态轴（按 case 门控后每 case 仍 ≥1，round/square 家族 ≥3） |

## Compatibility Gates

逐条 deny（已登记进 `category_template_registry.json`，`combo-audit` 实测三条 gate 分别
拒 12 / 6 / 12 = 30 条非法组合，60 → 30）。模板侧由 `_COVERS_BY_CASE` 矩阵 +
`resolve_config` 回退实现（非法 cover → 该 case 首选 cover），非法组合不可能到达 builder：

| gate id | action | when | reason |
|---|---|---|---|
| `round_family_takes_only_round_family_lids` | deny | case ∈ {round_pocket, wrist_cradle} × cover ∈ {square_flat_lid, flat_clear_lid} | 方平盖按方壳外轮廓建模、透明圆盘盖铰接于底板胶囊墙；二者都没有 round 壳的 accepted anchor |
| `square_shell_takes_square_or_sighting_lids` | deny | case = square_lensatic × cover ∈ {domed_lid, flat_clear_lid} | 冲压球冠按圆壳卷边定径；透明圆盘属底板胶囊；方壳的 accepted 盖是圆角方板 |
| `baseplate_takes_only_clear_disc_lid` | deny | case = rectangular_baseplate × cover ∈ {domed_lid, mirror_sighting_lid, sight_wire_lid, square_flat_lid} | 底板的盖铰接在胶囊墙缘，其唯一 accepted anchor 是透明亚克力圆盘；壳缘盖无底板来源 |

派生（非 gate）：`hanging_ring` part + `case_to_ring` joint 只由 round_pocket /
square_lensatic 两个 case module 发射（① 骨架 3 vs 4 活动件）；`glass_lens` 只在
非液阻 seed 发射（见 Reject #8 决议 —— 液阻 seed 由密封 dome 充当唯一透明窗）。

## Combination Domain

- diversity_profile / reason: `constrained` —— 磁性罗盘的身份脊柱固定（同轴 bezel +
  自由旋转磁性指示件 + 后铰链盖恒在且不可替换）；诚实核心词汇由 8 条确认记录
  （1 origin + 7 单轴 fork）界定，不靠 N 或涂装膨胀。
- core axes / cartesian count / gate-filtered legal count:
  `case_platform(4) × indicator(3) × cover(5)` = **60 笛卡尔 → 30 gate 后合法**
  （`combo-audit` 实测 `core_domain.legal_combination_count=30`，`floor_met=true`）。
- multiplicity axes / admitted integers / reachable integers / min-mid-max boundaries:
  **无 multiplicity 轴**（`multiplicity_axis_names=[]`）；tick/grip 计数是 ④ 装饰档，
  不计入 core 也不计入 raw。
- raw cartesian count / gate-filtered legal count: **60 → 30**（无 N，故 raw ≡ core）。
- excluded: palette(4)、材质、宿主共形装饰(dial_tick_count 2 档 / bezel_grip_count 2 档)、
  连续尺寸(s/h/open_angle/plate/strap/rest) —— 均按 counting_policy 不计入。
- profile floor / recommended target / exception: floor=16、target=16、
  **30 ≥ 16 且 ≥ target，无需 hash-bound 人工例外**。

## Visual Risk

- `curved_fit`（选自标准清单）：球冠盖薄壳 / 液阻密封 dome / 腕托曲面板 / 透明圆盘盖
  与圆形壳唇、胶囊墙的曲面贴合；曲面件闭合姿态最易穿模。
- `multi_joint`（选自标准清单）：单 case 根上并联 3-4 个 REVOLUTE（bezel / indicator /
  cover / ring），组合姿态需 sampled collision 覆盖。
- 类别特有风险：
  1. **双透明窗叠层**（本类别最险）—— 液阻 dome 与 bezel 平镜片是两个窗，源 fork 让
     dome 直接戳穿镜片；必须由 `has_glass_lens` 二选一解决，不得用 allowance 掩盖
     （Reject #8，已在实现中修复并加 "exactly one transparent dial window" 身份守卫）。
  2. **薄件孤岛**（毫米级类别通病）—— tick/grip/leaf tab/cross bar/pin head 等亚毫米
     附件必须由宿主表面派生并**嵌入**，任何"刚好贴到"的常数都会随 s/h 采样裂开
     （已修 3 处：`ring_pin_head`、sight frame cross bar、leaf tabs）。
  3. **bezel 悬空** —— bezel 环带必须真正压在 case 顶面上；底板变体环带若留在胶囊
     内孔（源 fork 的做法）则 bezel 成孤立件（已修）。
- 不适用：`drawer` / `wheel_caster` / `hidden_slide` / `telescopic` —— 本类别无抽屉、
  无滚轮、无隐藏滑轨、无伸缩件（全部机构为 REVOLUTE）。

## Validator

- slot_choices_for_seed returns implemented module names（case/cover/indicator/palette + ④ 档）
- config_from_seed 对所有普通 seed（含 0）走 deterministic procedural sampling
- `_COVERS_BY_CASE` gating 阻止非法 case×cover；resolve_config 回退可见于 slot_choices
- 无 regression overrides、无 curated/modulo 主表
- s/h/open/plate/strap 全 clamp；bezel 座、pivot 座、hinge_z、bowl 包络为 equation 派生，
  不可能因采样破坏 MatingContract / 闭合间隙
- 跨部件依赖（bezel_top→hinge_z、lens_bottom→bowl_apex、capsule_outer→plate_length）
  全部在 resolve_config 求解
- 关键 MatingContract：case_to_bezel（case 顶面↔bezel_ring 底面）、case_to_indicator
  （pivot_pin 顶↔hub 底）；case_to_cover / case_to_ring 为 captured-pin grandfather
  （销穿套/环套销，几何上不存在两张轴对齐接触面），以 expect_contact + 元素级
  allow_overlap 兜底
- 关键 joint 类型/轴/行程：bezel z ±π、indicator z ±π、cover (−1,0,0) [−open,+8°]、
  ring z ±75°
- 装饰 loop 命名 `dial_tick_i`/`bezel_grip_i`/`ruler_left_i` 等随宿主派生放置

## Reject cases

1. 闭合姿态盖体与 bezel 叠层相交（hinge_z 必须由 bezel_top_z 派生，禁止常数）。
2. 类别漂移成制图圆规/表/仪表/粉盒（无磁针/无刻度盘/无自由 ±π 指示件即拒绝）。
3. indicator 无真实 REVOLUTE ±π 关节（冻结成贴花）。
4. ticks/cardinals/ruler 装饰悬空脱离宿主面（z 未从宿主表面派生）。
5. hanging_ring 摆动时脱离 ring_pin 捕获（±60° 姿态 expect_within 失败）。
6. sight wire 沿盖法线建模，闭合时戳穿玻璃/表盘（丝必须位于盖平面内跨越开口）。
7. baseplate 胶囊超出板长可容纳范围（plate_length 不等式未 clamp）。
8. **液阻胶囊 bowl 顶破玻璃镜片。** 实现阶段实测：源 fork 本身就有此缺陷（它从 origin
   继承了 bezel 平镜片、又叠加了密封 dome = **两个透明窗**），dome 在全部非底板液阻
   seed 上戳穿镜片约 2.5mm（15/48 seed）。**决议 = 几何解决，不是 allowance**：
   dome 无法缩到镜片之下（镜片下净空仅 ~2.9mm，小于 dome 必须容纳的磁针栈），故
   **镜片才是冗余件** —— 液阻 seed 只发射 dome 作为唯一透明窗（真实液阻罗盘正是如此），
   dome 穿过 bezel 内孔且径向留净空。配套：`stack_top_z` 改由 `max(bezel_top_z,
   bowl_apex_z)` 派生使闭合盖不撞 dome；新增 "exactly one transparent dial window
   (flat lens xor sealed capsule dome)" 身份守卫。**禁止**用
   `allow_overlap(capsule_bowl × glass_lens)` 掩盖（AUTHORING §C：不得用 allowance
   消音真实穿模）——该 allowance 已从模板删除。
9. 薄件孤岛：亚毫米附件"刚好贴到"宿主而非嵌入，随 s/h 采样裂开（实现阶段修复 3 处：
   `ring_pin_head` 随 h>1 脱销、sight frame cross bar 距 rim 内壁 0.5mm、hinge leaf
   tab 深度不足 2.5mm 够不到任何盖体近缘 −0.00393）。
10. bezel 悬空：环带留在胶囊内孔而未压在 case 顶面上（源 baseplate fork 的做法）。

## 与相邻类别的边界

- 不该混入：drawing compass 制图圆规（0611 同目录邻类；双腿+针尖+铅笔，无磁针/刻度盘）。
- 不该混入：手表/时钟/秒表（有表冠/表链/时分针机构，指针不是自由磁针）。
- 不该混入：化妆粉盒 Container_Cosmetic（有镜有盖但无刻度盘/磁针；mirror_sighting_lid
  必须保留照准槽+准线+罗盘胶囊才不读成粉盒）。
- 不该混入：GPS/电子罗盘（屏幕+按键，无机械指针）。
- 不该混入：压力表/温度计 gauge(指针受机构驱动非自由旋转，表盘语义不同)。

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_THEN_TEMPLATE 连续模式：spec 写毕直接实现模板 |

## 模板实现备注（可选）

- 共享 helpers：`_annulus`、`_cardinal_text`、`_emit_dial_deck`（dial face+ticks+
  cardinals+north_index+pivot_pin，card 变体关闭 case 侧刻度）、`_emit_bezel`、
  `_emit_hinge_tower`（knuckles+pin+riser posts，posts 高度由 hinge_z−case_top 派生）、
  `_emit_hanging_ring`。
- captured-pin 元素级 allow_overlap 清单：hinge_pin×cover_knuckle、hinge_pin×盖体
  mesh（盖根部贴轴）、hinge_knuckle_i×盖体 mesh（平板盖全宽根部扫过 knuckle 圆柱）、
  ring_pin×ring_loop（eye 环套销，留 0.3mm 径隙）、fluid_fill×damping_vane（液阻浸没）。
- 盖体统一在"闭合坐标系"建模（铰链缘 y≈0、向 −y 延伸、厚度 +z），visual
  rpy=(−open,0,0) 呈开盖参考姿态；joint 0=开、lower=−open=闭合、upper=+8°。
- indicator hub 坐 pivot_pin 顶面（非包销）以携带真实 MatingContract；ring 保持环套
  销 grandfather。
- 暂不进入 seed domain 的组合：无（30 tuple 全可达）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | round_pocket_case / two_color_needle / domed_lid | rec_picturex_0611__compass__001__png__airflex_batch_20260710_5dc1d1be20f148ab990f9a9c4b4f551c | L27-L64, L130-L373, L509-L589 | 壳/针/球冠盖几何 + 4 joint 拓扑 + captured-pin 测试模式 |
| S2 | A | rectangular_baseplate | rec_picturex0611_compass_fork_rectangular_baseplate_20260714 | L22-L94, L136-L419 | 底板+胶囊几何、ruler/箭头装饰、3-joint 骨架 |
| S3 | A | square_lensatic_case + square_flat_lid | rec_picturex0611_compass_fork_square_lensatic_case_20260714 | L39-L69, L124-L391 | 方壳/方盖几何、四角螺钉装饰 |
| S4 | B | full_dial_card | rec_picturex0611_compass_fork_full_dial_card_20260714 | L73-L98, L254-L326, L366-L379, L528-L539 | 罗盘卡几何 + 卡侧刻度迁移 + 旋转证明测试 |
| S5 | B | liquid_damped_needle | rec_picturex0611_compass_fork_liquid_damped_capsule_20260714 | L79-L107, L232-L254, L331-L368, L622-L718 | 液阻胶囊/叶片/垫圈 + 浸没 allowance 模式 |
| S6 | C | mirror_sighting_lid | rec_picturex0611_compass_fork_mirror_sighting_cover_20260714 | L47-L117, L348-L375, L656-L693 | 照准镜平板盖几何 + 变体测试 |
| S7 | C | sight_wire_lid | rec_picturex0611_compass_fork_sight_wire_cover_20260714 | L47-L80, L312-L339, L608-L634 | 准星丝框盖几何（丝取向改为盖平面内） |
| S8 | A | wrist_cradle_case | rec_picturex0611_compass_fork_wrist_mount_cradle_20260714 | L79-L127, L272-L326, L545-L568 | 腕托/腕带融合 visual 几何 + 托架测试 |
