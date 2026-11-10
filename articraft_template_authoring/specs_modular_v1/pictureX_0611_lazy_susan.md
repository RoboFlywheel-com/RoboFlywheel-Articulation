# pictureX_0611_lazy_susan — Modular Spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_lazy_susan` |
| template path | `agent/templates/pictureX_0611_lazy_susan.py` |
| function stem | `picturex_0611_lazy_susan` (per `cli/template.py:114` TEMPLATE_REGISTRY) |
| test path (optional) | — (not authored; sweep + blocker audit is the authoritative signal) |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed` (linear_chain base→bearing→platter + multiplicity + parallel hardware visuals) |

历史说明：本 spec 取代此前的 *"Source Replay Transitional Spec"* 占位文件（30 行，无 slot/candidate/source-line 表，
无 §7.5/§8/§8.5/§9/§10）。旧文件不是本 schema 的 spec，只是一个 3-source replay 的登记条。

## Category Binding
category_slug: lazy_susan · template_slug: pictureX_0611_lazy_susan · mechanism_profile: vertical_axis_turntable_bearing · export_namespace: lazy_susan
diversity_profile: `rich` · diversity_profile_reason: 四根真实离散轴全部 source-backed 且可自由重组 —
base_form(5) × bearing_style(5) × platter_form(6) × spin_joint(2) = 300 raw core，compatibility gate 后
**实测 260** 可达 core 组合（`slot_choices_for_seed` over seeds 0-999，去掉 ④⑥ 与 N）；13 个 5 星样本里同时
出现了 5 种承载底座、5 种轴承硬件、6 种主体形态原型和 2 种旋转关节类型，不是靠 N 或涂装撑。

**实测多样性**（`slot_choices_for_seed`，重写前后对比）：

| 指标 | 重写前（source replay） | 重写后 |
|---|---:|---:|
| distinct tuples / 200 seeds | **3** | **199** |
| distinct tuples / 1000 seeds | 3 | **963** |
| core (①②③+N，去 ④⑥) / 1000 | 3 | **527** |
| core (①②③ only) / 1000 = gated core domain | 3 | **260** |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | all 13 records in `data/index/subcat/0611__lazy_susan.jsonl`（全部读 `revisions/rev_000001/model.py`，无抽样） |
| source_index_policy | only adopted module sources are indexed below（13/13 均被采纳到至少一个 module） |

> 注：`record.json` / `revision.json` 里 `rating` 字段为 `null`（13/13）。任务单声明该池已按 rating=5 同步；
> 磁盘上无 rating 证据，本 spec 按任务单声明处理，不修改上游。

### Source Index

| id | record_id | 行数 | parts/joints | 结构要点 |
|---|---|---:|---|---|
| S1 | `rec_picturex_0611__lazy_susan__001__png_84d342859ad6436ebbd9b2e40cd55644` | 330 | 2/1 REVOLUTE±π | 扁平圆盘底座 + LatheGeometry 石板 + 瓷砖缝/脉纹 |
| S2 | `rec_picturex_0611__lazy_susan__002__png_34d73e1312d84c3a872e9ce87f698a3a` | 387 | 2/1 REVOLUTE±π | cadquery loft 基座圆桌 + 平面 race 对 + cq 石盘 |
| S3 | `rec_picturex0611_supp_lazy_susan_var_two_tier_round` | 473 | 2/1 REVOLUTE | S1 + 三柱/中央桅 + 上层 Lathe 托盘 |
| S4 | `rec_picturex0611_supp_lazy_susan_var_segmented_wedge_trays` | 494 | 2/1 REVOLUTE | S2 + 环形唇 + 6 条径向隔板（N 轴） |
| S5 | `rec_picturex0611_supp_lazy_susan_var_bearing_ring_exposed` | 455 | 2/1 REVOLUTE | S2 + 上下 race + 24 颗外露滚珠（N 轴） |
| S6 | `rec_picturex0611_supp_lazy_susan_var_rectangular_cabinet_spinner` | 311 | 2/1 REVOLUTE | S1 底座 + cq 圆角矩形托盘 + 护栏 + 4 角柱 |
| S7 | `rec_picturex0611_supp_lazy_susan_var_pull_out_swivel_corner` | 555 | 5/4 PRISMATIC+REVOLUTE+FIXED+REVOLUTE | 橱柜抽拉 + 摆臂 + S1 底座/转盘 |
| S8 | `rec_use-...-_20260712_093026_380093_a4b69753` | 239 | 2/1 CONTINUOUS | 隐藏式 puck 底座 + cq 倒角石盘 + 螺钉/徽章 |
| S9 | `rec_use-...-_20260712_093216_489164_9abfe7cb` | 338 | 2/1 CONTINUOUS | 电动底座（马达舱/接线/电缆样条/插头）+ Torus 边圈木盘 |
| S10 | `rec_use-...-_20260712_100645_100347_a4b69753` | 250 | 2/1 CONTINUOUS | 低 puck + **重 cq 布尔 cut 脉纹**（编译超时来源） |
| S11 | `rec_use-...-_20260712_100645_100756_a4b69753` | 256 | 2/1 CONTINUOUS | cq soft_disc puck + thrust_pad/race/center_axle + rotor_hub |
| S12 | `rec_use-...-_20260712_100932_868786_9abfe7cb` | 352 | 2/1 CONTINUOUS | 电动底座 + 3 只承载滚轮（N 轴）+ 分层木盘 |
| S13 | `rec_use-...-_20260712_100941_355392_9abfe7cb` | 299 | 2/1 REVOLUTE±π | cq 倒角底盘 + 12 颗 Sphere 滚珠（N 轴）+ 单板木盘/嵌线环 |

## 核心身份

Lazy Susan = **绕单一竖直轴（+z）自由回转的托盘/转盘，坐落在一套可见的回转轴承硬件上，轴承下方是一个静止的
承载底座**。物理功能：把桌面/柜内物品转到取用者面前。成熟域三要素缺一不可：
(a) 静止承载底座（桌面圆盘 / 落地基座圆桌 / 隐藏 puck / 电动机座 / 橱柜抽拉摆臂）；
(b) 竖直轴回转轴承（隐藏盖 / 平面 race 对 / 外露滚珠环 / 滚轮组 / 主轴止推）；
(c) 回转托盘主体（石板 / 木盘 / 双层 / 分格 / 圆角矩形托盘）。

回转关节的轴恒为 (0,0,1) 且过硬件对称中心线；这是本类别的身份约束，不是可采样项。

## 与相邻类别的边界

- 不该混入：**turntable / 唱盘（record player）**（理由：唱盘由马达驱动定速旋转并带唱臂/拾音器这条第二运动链；
  lazy susan 是手推自由回转的取餐面，没有唱臂 slot。S9/S12 的电动底座只是隐藏减速驱动，仍无第二运动链。）
- 不该混入：**旋转餐桌整桌 / 圆桌本体（round dining table）**（理由：S2/S4/S5 的基座圆桌是 lazy susan 的
  *承载底座*，转的是嵌在桌面里的石盘；若整张桌面旋转、或桌子没有独立回转盘，就是桌子不是 lazy susan。
  身份判据：platter_diameter / table_diameter ∈ [0.50, 0.62]，见 S2 L282-290。）
- 不该混入：**旋转刀架 / 调料架（carousel organizer with vertical tiers）**（理由：那类的多层托盘各自独立
  回转（每层一个关节）；本类别 S3 的双层是**同一个回转子件上的两层**，只有一个关节。多关节多层 → 另一小类。）
- 不该混入：**bearing / 转盘轴承零件本身（slewing ring）**（理由：S5 的外露滚珠环是本模板的 bearing_style
  候选之一，但必须承载一个可识别的托盘主体；只有轴承没有托盘 = 零件，不是 lazy susan。）
- 不该混入：**橱柜（cabinet）**（理由：S7 的橱柜抽拉底座只提供承载与出柜行程，柜体本身不建模；
  若出现柜门/柜体隔板/多抽屉 → 属 Cabinet_with_doors 等小类。）

## 槽位 + 候选模块表

### Slot A：base_form（① 骨架图 + ③ 主体形态家族；静止承载底座）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_disk_base` | forked_anchor | S1 | `model.py:L70-L99` | eligible if compatible | 1 part；非滑垫 Cylinder + 承载圆盘 Cylinder；桌面放置型；deck = 圆盘上表面 |
| `pedestal_table` | forked_anchor | S2 | `model.py:L28-L51`, `L99-L134` | eligible if compatible | 1 part；cadquery loft 基座（foot/lower_flare/column/upper_flare union）+ fillet 圆桌面 + 下承载盘；落地 |
| `concealed_puck` | forked_anchor | S8, S11 | S8 `model.py:L54-L80`；S11 `model.py:L55-L88` | eligible if compatible | 1 part；cq annulus 橡胶垫 + cq soft_disc 本体；低矮隐藏（deck_r < platter_r） |
| `powered_console` | forked_anchor | S12, S9 | S12 `model.py:L43-L179`；S9 `model.py:L44-L179` | eligible if compatible | 1 part；机壳 + 轴承台 + 马达罩 + 控制舱/观察窗/黄铜接线柱/接线螺钉 + 电缆密封套 + `tube_from_spline_points` 电源线 + 插头/插片 |
| `cabinet_pullout` | forked_anchor | S7 | `model.py:L77-L155`, `L282-L320` | eligible if compatible | **3 parts + 2 内部关节**：`cabinet_mount`(安装板/后法兰/双导轨) −PRISMATIC(+x)→ `carriage`(抽拉臂/摆轭/摆轴凸台) −REVOLUTE(z)→ `swivel_arm`(枢轴板/偏置桥/承载垫)；deck = 承载垫上表面 |

> `cabinet_pullout` 对 S7 的**唯一偏离**：S7 用 `FIXED` 关节 `swivel_arm_to_support`（L314-320）把 S1 的 `support`
> part 挂到摆臂上。按 AUTHORING Rule 1（不动就不是 part），本模板把 `support` 的可视件融进 `swivel_arm`
> （`support_pad` 即 deck），删掉该 FIXED 关节。part tree 语义、关节图（两条运动边）、primitive 家族均保留。

### Slot B：bearing_style（① 骨架图（硬件存在性）+ ③；竖直轴回转轴承）

静止半边发到 deck part，回转半边发到 platter part；两半由同一个 `_BearingBuild` 描述符派生（单真源）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `concealed_cap` | forked_anchor | S1 | `model.py:L84-L94`（静止）+ `L119-L124`（回转 carrier_plate） | eligible if compatible | 隐藏式：bearing_mount Cylinder + bearing_cap Cylinder；回转侧 carrier_plate 圆盘落在 cap 上 |
| `flat_race_pair` | forked_anchor | S2, S13 | S2 `model.py:L123-L134`；S13 `model.py:L77-L81`, `L115-L118` | eligible if compatible | cq 环形上下 race 对 + upper_carrier；平面对平面承载 |
| `exposed_ball_ring` | forked_anchor | S5, S13 | S5 `model.py:L136-L156`（24 颗）；S13 `model.py:L91-L100`（12 颗，`Sphere` 原语） | eligible if compatible | 固定 race + **N 颗外露滚珠**（`Sphere`）+ 回转 race；N 轴见 §8 |
| `roller_set` | forked_anchor | S12 | `model.py:L75-L89` | eligible if compatible | **N 只承载滚轮** Cylinder（竖轴、平顶承载面）+ 滚轮轴；回转侧 drive_pad；N 轴见 §8 |
| `spindle_thrust` | forked_anchor | S11 | `model.py:L71-L88`（thrust_pad/bearing_race/center_axle）+ `L112-L117`（rotor_hub） | eligible if compatible | 主轴止推：thrust_pad + 环形 race + center_axle 穿过回转 rotor_hub 内孔（捕获销，径向留隙） |

### Slot C：platter_form（③ 主体形态家族 / Primary Form Family；回转托盘主体）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `lathe_stone_slab` | forked_anchor | S1 | `model.py:L103-L129` | Volumetric Envelope Form | eligible if compatible | `LatheGeometry` 8 点母线（缓边/倒角周缘）→ `mesh_from_geometry` |
| `chamfered_stone_disk` | forked_anchor | S8, S11 | S8 `model.py:L88-L94`；S11 `model.py:L31-L34`, `L92-L104` | Volumetric Envelope Form | eligible if compatible | cq `circle().extrude().edges().chamfer()` + 抛光边环 |
| `veneered_wood_disk` | forked_anchor | S13, S9 | S13 `model.py:L126-L148`；S9 `model.py:L182-L205` | Macro Surface Construction | eligible if compatible | cq 倒角芯盘 + top_veneer + cq annulus edge_band + cq annulus 嵌线环（分层单板读法） |
| `two_tier_round` | forked_anchor | S3 | `model.py:L192-L246` | Macro Surface Construction | eligible if compatible | 下层 Lathe 石板 + **N 根立柱** + 中央桅 + upper_carrier + 上层 Lathe 托盘（同一回转 part） |
| `segmented_wedge` | forked_anchor | S4 | `model.py:L64-L87`, `L188-L212` | Macro Surface Construction | eligible if compatible | 芯盘 + cq 环形唇 + **N 条径向隔板**（楔形分格） |
| `rounded_rect_tray` | forked_anchor | S6 | `model.py:L30-L61`, `L114-L165` | **Planar Boundary Form** | eligible if compatible | cq 圆角矩形底 + `outer.cut(inner)` 护栏环 + 防滑衬垫 + 4 角柱；**投影轮廓由圆变圆角矩形** |

### Slot D：spin_joint（② 关节类型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `revolute_bounded` | forked_anchor | S1, S2, S13 | S1 `model.py:L193-L209`；S13 `model.py:L179-L194` | eligible if compatible | `REVOLUTE`，axis (0,0,1)，`MotionLimits(lower=-π, upper=+π)` |
| `continuous_free` | forked_anchor | S8, S9, S11, S12 | S8 `model.py:L145-L155`；S12 `model.py:L246-L256` | eligible if compatible | `CONTINUOUS`，axis (0,0,1)，无角度上下界（整圈） |

### Slot E：surface_style（④ 表面装饰；登记进 `slot_choices` 仅为覆盖证明，**不计入 core_domain**）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `marble_veins` | record_only | S1, S2 | S1 `model.py:L166-L185`；S2 `model.py:L157-L205` | eligible if host-conformal | 非对称浅脉纹（薄 Box 条），由宿主最终顶面逐角派生长度 |
| `tile_grout` | record_only | S1 | `model.py:L139-L162` | eligible if host-conformal | 正交瓷砖缝网格 + 脉纹 |
| `radial_inlay` | record_only | S12, S9 | S12 `model.py:L218-L233`；S9 `model.py:L214-L227` | eligible if host-conformal | 4 条径向黄铜嵌条 + 制造商徽牌 |
| `veneer_seams` | record_only | S13 | `model.py:L152-L162` | eligible if host-conformal | 8 条径向单板拼缝 |
| `plain_polished` | record_only | S1, S8 | S1 `model.py:L132-L137`（polished_face）；S8 `model.py:L138-L143` | eligible if host-conformal | 仅抛光面 + 定位徽章 |

> ④ 全部写成宿主 part 的 `visual(...)`，不新建 part、不新建 joint、不改主体 primitive/N。
> 每个 seed 无条件额外发一个 `orientation_mark`（S8 L138-143 `maker_medallion` / S13 L166-171 / S12 L228-233
> `maker_badge`）：它是 ⑤ 运动语义测试用的**非对称基准**（圆形轮廓下证明回转的唯一可见手段）。

### Slot F：palette_style（⑥ 涂装；登记进 `slot_choices` 仅为覆盖证明，**不计入 core_domain**）

见 §8.5 ⑥ 行与 §参数范围汇总。6 个配色全部取自样本 `model.material(...)` 实测 rgba。

硬约束自检：

- Slot A=5、B=5、C=6、D=2、E=5、F=6 candidate，均 ≥2；A/B/C ≥3 ✓。
- 无单 candidate slot ✓。
- multiplicity（§8）挂在 B/C 的具体 candidate 上，不单独成 slot，不计入 candidate 数下限 ✓。
- ①/② 每个 candidate 均有 accepted record + 精确 `model.py:Lx-Ly` ✓；无 `analogous`/`derived`/`n/a` ✓。
- ③ 6 个 candidate **全部 direct source-backed**（无受控外推）→ Form Dependency Contracts 无外推条目。

## Form Dependency Contracts

**无受控外推③。** Slot C 的 6 个 candidate 全部是 direct source-backed（各自 record + 精确行号见 Slot C 表），
因此不适用 `world_knowledge_extrapolation(受控③)`，本节无外推条目。

唯一需要耦合派生的是 `rounded_rect_tray` 的 Planar Boundary（圆 → 圆角矩形）：其**所有**依赖消费者
（护栏内孔、防滑衬垫、4 角柱位置、④ 装饰的逐角可用半径）都从同一个 master 描述符 `_PlatterSurface`
派生，不各自重新抽形状。这不是外推（S6 已给出完整资产），故按普通 source-backed candidate 处理，
但派生纪律同受控③：

| ③ candidate | master descriptor | dependent consumers | derivation rule | validator |
|---|---|---|---|---|
| `rounded_rect_tray` | `_PlatterSurface(kind="rect", half_w, half_d, corner_r, top_z)` | 护栏环 outer/inner、`grip_liner`、`corner_post_{0..3}` 位置、④ 装饰长度/位置、`orientation_mark` 半径 | `inner = offset(outer, −wall)`；`liner = offset(outer, −0.026·min(hw,hd))`；角柱 = `(±(hw−cr), ±(hd−cr))`；装饰逐角可用半径 = `_PlatterSurface.extent_at(angle)` | 装饰全部落在 `extent_at(θ)·0.94` 内；4 角柱与护栏共形接触；sampled-pose 无穿模 |

## 槽位图（slot graph）

pattern: `mixed`

```
[Slot A base_form]
   flat_disk_base | pedestal_table | concealed_puck | powered_console   → 1 part `base`,  deck = base
   cabinet_pullout → `cabinet_mount` --[PRISMATIC +x, [0, pull_travel]]--> `carriage`
                                     --[REVOLUTE  z,  [-1.22, +1.22]]--> `swivel_arm`,  deck = swivel_arm
        |
        |  deck part 上表面 = deck_top_z（deck 局部帧）
        v
[Slot B bearing_style]  静止半边 → deck part 的 visual（Rule 1：不动 ⇒ 不是 part）
        |               回转半边 → platter part 的 visual，底面锚在 platter 局部 z=0
        |
        |  --[Slot D spin_joint: REVOLUTE|CONTINUOUS, axis (0,0,1), origin z = _bearing_top_z]-->
        |    MatingContract: parent = <bearing top land visual> (+z) ↔ child = <rotor mating visual> (−z)
        v
[Slot C platter_form]   → 1 part `platter`（含 Slot E ④ 装饰 visual）
```

- **slot 顺序**：A → B → C 串联；D 是 B/C 之间那条 platter 边的**标签**（② 轴），不新增 part。
- **接口点位**：
  - A→B：deck part 的上表面平面 `z = deck_top_z`（接触平面，同 part 内叠放，非关节）。
  - B→C：`_bearing_top_z = deck_top_z + _bearing_stack_height`，**唯一的跨 part spin 关节**。
    接口 = 轴承顶承载面（land）↔ 回转 rotor 底面；axis (0,0,1) 过硬件对称中心线。
  - A 内部：`mounting_plate(+z)` ↔ `pullout_arm(−z)`（prismatic 导轨面）；`swivel_boss(+z)` ↔ `pivot_plate(−z)`（枢轴面）。
- **跨 slot joint type/axis/range**：见 §6.5。
- **互斥/可选/派生**：
  - Slot B 的 `spindle_thrust` 与 Slot A 的 `pedestal_table` 互斥（§Compatibility Gates G3）。
  - Slot C 的 `rounded_rect_tray` 与 Slot A 的 `pedestal_table` / `powered_console` 互斥（G1/G2）。
  - deck 半径 `deck_r` **由 Slot B 的 `_bearing_outer_radius` 派生**（不是独立采样）——见 §7 `equation` 行。
  - `cabinet_pullout` 的全部尺寸（swing_offset / pull_travel / 安装板 / 后法兰 / 导轨）**均由 `platter_radius` 派生**。

## 每槽位 Module Emits / Interfaces

### Slot A / module `flat_disk_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`：`non_slip_pad`(Cylinder), `support_disk`(Cylinder) | S1 / `model.py:L70-L87` |
| internal joints | 无 | S1 |
| upstream interface | 无（root，接地） | S1 |
| downstream interface | `support_disk` +z 面，`deck_top_z = pad_t + disk_t` | S1 / `model.py:L77-L82` |

### Slot A / module `pedestal_table`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`：`pedestal`(cq loft union → mesh), `tabletop`(cq fillet → mesh), `lower_support_disk`(Cylinder) | S2 / `model.py:L28-L51`, `L106-L122` |
| internal joints | 无 | S2 |
| upstream interface | 无（root，落地 foot） | S2 / `model.py:L33` |
| downstream interface | `lower_support_disk` +z 面，`deck_top_z = table_h + tabletop_t + disk_t` | S2 / `model.py:L117-L122` |

### Slot A / module `concealed_puck`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`：`rubber_pad`(cq annulus → mesh), `base_body`(cq soft_disc → mesh) | S8 `L54-L59`；S11 `L57-L69` |
| internal joints | 无 | — |
| upstream interface | 无（root，接地） | S11 / `model.py:L57` |
| downstream interface | `base_body` +z 面，`deck_top_z = pad_t + body_t` | S11 / `model.py:L57-L62` |

### Slot A / module `powered_console`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`：`base_housing`, `rubber_pad`, `bearing_support`, `motor_cover`, `control_pod`, `inspection_window`, `brass_terminal_{0,1}`, `terminal_screw_{0,1}`, `cable_gland`, `strain_relief`, `power_cord`(spline tube → mesh), `power_plug`, `plug_blade_{0,1}`, `warning_label` | S12 / `model.py:L49-L179` |
| internal joints | 无（服务硬件全部为 parent visual，Rule 1） | S12 |
| upstream interface | 无（root，接地 rubber_pad） | S12 / `model.py:L55-L60` |
| downstream interface | `bearing_support` +z 面，`deck_top_z = housing_t + support_t` | S12 / `model.py:L61-L66` |

> **对 S12 的修正**：S12 L61-66 的 `bearing_support`（z 0.056–0.078）悬在 `base_housing`（z 0.004–0.048）
> 上方 8 mm，是一个 disconnected island（Contract 3 违反）。本模板把 `bearing_support` 底面派生为
> `= housing 顶面`，实体落座。

### Slot A / module `cabinet_pullout`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_mount`：`mounting_plate`(Box), `rear_flange`(Box), `guide_rail_{0,1}`(Box)；`carriage`：`pullout_arm`(Box), `swivel_yoke`(Box), `swivel_boss`(Cylinder)；`swivel_arm`：`pivot_plate`(Cylinder), `offset_bridge`(Box), `support_pad`(Cylinder) | S7 / `model.py:L77-L96`, `L103-L123`, `L132-L150` |
| internal joints | `mount_to_carriage` PRISMATIC axis (1,0,0) `[0, pull_travel]`；`carriage_to_swivel_arm` REVOLUTE axis (0,0,1) `[-1.22, +1.22]` | S7 / `model.py:L282-L312` |
| upstream interface | 无（root，`mounting_plate` 为柜内固定面） | S7 / `model.py:L78-L83` |
| downstream interface | `support_pad` +z 面，`deck_top_z = pad_t`（swivel_arm 局部帧） | S7 / `model.py:L145-L150` |

### Slot B / module `concealed_cap`
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck += `bearing_mount`(Cylinder), `bearing_cap`(Cylinder)；platter += `carrier_plate`(Cylinder) | S1 / `model.py:L88-L94`, `L119-L124` |
| internal joints | 无 | — |
| upstream interface | `bearing_mount` −z 落在 deck 上表面 | S1 / `model.py:L89-L93` |
| downstream interface | `bearing_cap` +z land；`_bearing_top_z = deck_top_z + mount_t + cap_t` | S1 / `model.py:L94-L99` |

### Slot B / module `flat_race_pair`
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck += `fixed_bearing_race`(cq annulus → mesh)；platter += `rotating_bearing_race`(cq annulus → mesh), `upper_carrier`(Cylinder) | S2 `L123-L134`, `L144-L149`；S13 `L77-L81`, `L115-L124` |
| internal joints | 无 | — |
| upstream interface | `fixed_bearing_race` −z 落在 deck 上表面 | S2 / `model.py:L129-L134` |
| downstream interface | `fixed_bearing_race` +z land；`_bearing_top_z = deck_top_z + race_t` | S2 / `model.py:L123-L128` |

### Slot B / module `exposed_ball_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck += `fixed_bearing_race`(cq annulus → mesh), `bearing_ball_{0..N-1}`(`Sphere`)；platter += `rotating_bearing_race`(cq annulus → mesh), `upper_carrier`(Cylinder) | S5 `L136-L156`, `L166-L191`；S13 `L91-L100`, `L115-L118` |
| internal joints | 无（滚珠为 deck part 的 visual，Rule 1） | — |
| upstream interface | `fixed_bearing_race` −z 落在 deck 上表面 | S5 / `model.py:L136-L145` |
| downstream interface | `bearing_ball_0` +z（滚珠顶点承载面）；`_bearing_top_z = deck_top_z + race_t + 1.55·ball_r + running_clearance` | S5 / `model.py:L146-L156`；S13 `L91-L100` |

### Slot B / module `roller_set`
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck += `roller_axle_{i}`(Cylinder), `support_roller_{i}`(Cylinder)；platter += `drive_pad`(Cylinder) | S12 / `model.py:L75-L89`, `L186-L191` |
| internal joints | 无 | — |
| upstream interface | `roller_axle_{i}` −z 埋入 deck 上表面 | S12 / `model.py:L84-L89` |
| downstream interface | `support_roller_0` +z（滚轮平顶承载面）；`_bearing_top_z = deck_top_z + axle_stick + roller_t` | S12 / `model.py:L78-L83` |

### Slot B / module `spindle_thrust`
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck += `thrust_pad`(Cylinder), `bearing_race`(cq annulus → mesh), `center_axle`(Cylinder)；platter += `rotor_hub`(cq annulus → mesh), `backing_plate`(Cylinder) | S11 / `model.py:L71-L88`, `L106-L117` |
| internal joints | 无 | — |
| upstream interface | `thrust_pad` −z 落在 deck 上表面 | S11 / `model.py:L71-L76` |
| downstream interface | `thrust_pad` +z land；`_bearing_top_z = deck_top_z + pad_t`；`center_axle` 穿过 `rotor_hub` 内孔（径向留隙 0.8 mm） | S11 / `model.py:L77-L88`, `L112-L117` |

### Slot C / module `lathe_stone_slab`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `top_stone`(`LatheGeometry` 8 点母线 → `mesh_from_geometry`), `polished_face`(Cylinder) | S1 / `model.py:L103-L137` |
| internal joints | 无 | — |
| upstream interface | rotor 底面（由 Slot B 发）在 platter 局部 z=0 | S1 / `model.py:L119-L124` |
| downstream interface | `_PlatterSurface(kind="round", radius, top_z)`（供 ④ 装饰派生） | S1 / `model.py:L132-L137` |

### Slot C / module `chamfered_stone_disk`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `marble_slab`(cq chamfer → mesh), `polished_edge`(cq annulus → mesh) | S8 `L88-L94`；S11 `L92-L104` |
| internal joints | 无 | — |
| upstream interface | 同上 | — |
| downstream interface | `_PlatterSurface(kind="round", ...)` | S11 / `model.py:L92-L97` |

### Slot C / module `veneered_wood_disk`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `platter_core`(cq chamfer → mesh), `top_veneer`(Cylinder), `edge_band`(cq annulus → mesh), `top_inlay_ring`(cq annulus → mesh) | S13 / `model.py:L126-L148` |
| internal joints | 无 | — |
| upstream interface | 同上 | — |
| downstream interface | `_PlatterSurface(kind="round", ...)` | S13 / `model.py:L131-L136` |

### Slot C / module `two_tier_round`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `top_stone`+`polished_face`（下层，同 `lathe_stone_slab`）, `upper_post_{0..N-1}`(Cylinder), `central_support`(Cylinder), `upper_carrier_plate`(Cylinder), `upper_tray`(`LatheGeometry` → mesh), `upper_polished_face`(Cylinder) | S3 / `model.py:L192-L246` |
| internal joints | 无（两层同属一个回转 part，只有一个 spin 关节） | S3 / `model.py:L192-L195` |
| upstream interface | 同上 | — |
| downstream interface | `_PlatterSurface(kind="round", radius=upper_r, top_z=upper_top)`（装饰落在**上层**最终顶面） | S3 / `model.py:L222-L246` |

### Slot C / module `segmented_wedge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `marble_slab`(cq chamfer → mesh), `compartment_rim`(cq annulus → mesh), `compartment_divider_{0..N-1}`（**同一个 mesh 复用 N 次**，rpy 均布） | S4 / `model.py:L64-L87`, `L188-L212` |
| internal joints | 无 | — |
| upstream interface | 同上 | — |
| downstream interface | `_PlatterSurface(kind="round", radius=platter_r − rim_w, top_z=slab_top)` | S4 / `model.py:L64-L71` |

### Slot C / module `rounded_rect_tray`
| emits | 描述 | 来源 |
|---|---|---|
| parts | platter += `organizer_tray`(cq rounded box floor ∪ (outer.cut(inner)) 护栏 → mesh), `grip_liner`(cq rounded box → mesh), `corner_post_{0..3}`(Cylinder) | S6 / `model.py:L30-L61`, `L114-L165` |
| internal joints | 无 | — |
| upstream interface | 同上 | — |
| downstream interface | `_PlatterSurface(kind="rect", half_w, half_d, corner_r, top_z=floor_top)` | S6 / `model.py:L40-L61` |

### Slot D / module `revolute_bounded` · `continuous_free`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（只给 spin 边贴标签） | — |
| internal joints | `spin` REVOLUTE `[-π, +π]` / CONTINUOUS（整圈），axis (0,0,1)，origin `z=_bearing_top_z` | S1 `L193-L209`；S8 `L145-L155` |
| upstream interface | `<bearing top land>` (+z) | 见 Slot B |
| downstream interface | `<rotor mating visual>` (−z) @ platter 局部 z=0 | 见 Slot B |

## 活动机构与运动净空契约

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| `spin`（全部 seed） | `platter` = rotor 半边(承载) + 主体形态实体 + ④ 装饰，完整回转实体 | deck part 的轴承静止半边（`bearing_cap`/`fixed_bearing_race`/滚珠环/滚轮组/`thrust_pad`）为可见承载面 | `MatingContract(parent=<bearing top land>, +z ↔ child=<rotor mating visual>, −z, contact_tol=0.0015)` | origin `(0,0,_bearing_top_z)`（deck 帧）；axis (0,0,1)；REVOLUTE `[-π,+π]` 或 CONTINUOUS 整圈 | 回转体绕自身对称轴转 → 包络恒定；`_bearing_outer_radius + 0.010 ≤ platter_radius` 保证托盘全程覆盖轴承；最小净空 = `running_clearance` 0.5 mm（仅 ball ring）或平面精确接触 0 mm | **无**（无 intentional overlap；`center_axle`↔`rotor_hub` 径向留隙 0.8 mm，是间隙不是过盈） | `fail_if_parts_overlap_in_sampled_poses`；targeted `ctx.pose({spin: π/2})` 断言 `orientation_mark` 的 **element AABB 中心**在 xy 位移显著且 z 不变；CONTINUOUS 额外覆盖 0/π/2、π、3π/2 整圈 |
| `mount_to_carriage`（仅 `cabinet_pullout`） | `carriage` = `pullout_arm` + `swivel_yoke` + `swivel_boss`（开放式抽拉五金臂，非抽屉盒——S7 L103-105 明示） | `cabinet_mount` 的 `mounting_plate` 承载面 + **双侧** `guide_rail_{0,1}` 纵向导轨 | `MatingContract(parent=mounting_plate, +z ↔ child=pullout_arm, −z)` | origin `(0,0,plate_t)`；axis (1,0,0)；`[0, pull_travel]`，`pull_travel = 0.571·platter_radius` | 全程 `pullout_arm` 底面贴 `mounting_plate`；`swivel_yoke` 半宽 `0.179R` < 导轨内缘 `0.188R` → 侧向净空 `0.009R`；导轨与臂无 y 重叠 | **无** | targeted `ctx.pose({pullout: upper})` 用 `part_world_position(carriage)` 断言 +x 平移（PRISMATIC 用 part frame 合法）；sampled poses |
| `carriage_to_swivel_arm`（仅 `cabinet_pullout`） | `swivel_arm` = `pivot_plate` + `offset_bridge` + `support_pad`（承载整个轴承+托盘） | `carriage` 的 `swivel_boss` 可见枢轴凸台 | `MatingContract(parent=swivel_boss, +z ↔ child=pivot_plate, −z)` | origin `(0,0,yoke_t+boss_t)`；axis (0,0,1)；`[-1.22, +1.22]`（S7 L305-310） | 托盘中心绕枢轴摆到 `x_min = 0.147R − R = −0.853R`；`rear_flange` 在 `x ≈ −1.215R` → 恒余 `0.36R` 净空（全部由 `platter_radius` 派生，任意 R 恒成立）；`support_pad`(z≈0.026–0.029·R/0.42) 与导轨无 z 重叠 | **无** | targeted `ctx.pose({pullout: upper, swivel: 1.22})` 断言托盘 element AABB 中心绕枢轴摆动位移显著；sampled poses |

- 无 drawer / wheel_caster 机构：`cabinet_pullout` 是**开放五金臂 + 双侧导轨**（S7 L103-105 显式声明 "deliberately an
  open hardware arm rather than a drawer box"），不套用 drawer 的前板/底板/侧板/后挡要求；滚轮组 `roller_set` 是
  **承载滚轮**（竖轴、平顶承载面，S12 L78-83），不是行走轮，不套用 tire/fork/yoke 要求。
- **本模板 0 条 `allow_overlap`**：所有配合面要么精确接触（平面 land），要么留真实运行间隙
  （ball ring 0.5 mm 轴向；`center_axle`↔`rotor_hub` 0.8 mm 径向）。spec 中不出现 whole-part allowance。

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_form` | enum | flat_disk_base / pedestal_table / concealed_puck / powered_console / cabinet_pullout | flat_disk_base | choice | deterministic procedural sampler | Slot A 表 |
| `bearing_style` | enum | concealed_cap / flat_race_pair / exposed_ball_ring / roller_set / spindle_thrust | concealed_cap | choice | sampler + `_gate_bearing` | Slot B 表 |
| `platter_form` | enum | lathe_stone_slab / chamfered_stone_disk / veneered_wood_disk / two_tier_round / segmented_wedge / rounded_rect_tray | lathe_stone_slab | choice | sampler + `_gate_platter` | Slot C 表 |
| `spin_joint` | enum | revolute_bounded / continuous_free | revolute_bounded | choice | sampler | Slot D 表 |
| `surface_style` | enum | marble_veins / tile_grout / radial_inlay / veneer_seams / plain_polished | marble_veins | choice | sampler | Slot E 表 |
| `palette_style` | enum | warm_marble_charcoal / rose_marble_walnut / walnut_brass_steel / warm_wood_brass / white_marble_steel / powdercoat_bronze | warm_marble_charcoal | choice | sampler | §8.5 ⑥ |
| `platter_radius` | float | [0.16, 0.68] | 0.42 | independent | 采样后 clamp；`cabinet_pullout` 再 clamp 到 ≤0.40 | S1 `L21`(0.420) / S2 `L23`(0.660) / S11 `L92`(0.275) |
| `platter_thickness` | float | [0.016, 0.036] | 0.022 | independent | clamp | S1 `L22`(0.017) / S2 `L24`(0.026) / S13 `L126`(0.032) |
| `bearing_span_ratio` | float | [0.20, 0.46] | 0.30 | independent | clamp | S1 `L92`(0.074/0.420=0.176→下界取 0.20) / S5 `L26`(0.305/0.660=0.462) |
| `base_span_ratio` | float | [0.42, 0.95] | 0.88 | independent | clamp；`concealed_puck` 再 clamp 到 [0.42,0.60] | S1 `L79`(0.370/0.420=0.881) / S8 `L61`(0.180/0.365=0.493) / S12 `L50`(0.355/0.560=0.634) |
| `table_height` | float | [0.62, 0.76] | 0.70 | conditional | 仅 `pedestal_table`；真实餐桌高 | S2 `L21`(0.700) |
| `tier_gap_ratio` | float | [0.40, 0.58] | 0.47 | conditional | 仅 `two_tier_round` | S3 `L25`((0.220−0.022)/0.420=0.471) |
| `tray_aspect` | float | [0.62, 0.92] | 0.74 | conditional | 仅 `rounded_rect_tray`；`half_d/half_w` | S6 `L22-L23`(0.560/0.760=0.737) |
| `ball_count` | int | [10, 28] | 16 | conditional | 仅 `exposed_ball_ring`；见 §8 | S5 `L28`(24) / S13 `L91`(12) |
| `roller_count` | int | [3, 6] | 3 | conditional | 仅 `roller_set`；见 §8 | S12 `L75`(3) |
| `divider_count` | int | [4, 8] | 6 | conditional | 仅 `segmented_wedge`；见 §8 | S4 `L26`(6) |
| `tier_post_count` | int | [3, 5] | 3 | conditional | 仅 `two_tier_round`；见 §8 | S3 `L198`(3) |
| `deck_radius` | float | derived | — | equation | `= max(platter_radius·base_span_ratio, _bearing_outer_radius(r) + 0.010)`；`cabinet_pullout` 时 `= _bearing_outer_radius(r) + 0.010` | S7 `L147`(0.110) ≈ S1 `L89`(0.112) bearing_mount |
| `bearing_pitch_radius` | float | derived | — | equation | `= platter_radius · bearing_span_ratio` | S5 `L26` |
| `race_half_width` | float | derived | — | equation | `= max(0.008, 0.164 · bearing_pitch_radius)` | S2 `L123-L127`：(0.355−0.255)/2 / 0.305 = 0.164 |
| `_bearing_top_z` | float | derived | — | equation | `= deck_top_z + _bearing_stack_height(style)`（spin joint 原点 z） | Slot B 表 |
| `swing_offset` | float | derived | — | equation | `= 0.43 · platter_radius`（仅 cabinet_pullout） | S7 `L24`(0.180/0.420=0.4286) |
| `pull_travel` | float | derived | — | equation | `= 0.571 · platter_radius`（仅 cabinet_pullout） | S7 `L25`(0.240/0.420=0.5714) |
| `table_radius` | float | derived | — | equation | `= 1.78 · platter_radius`（仅 pedestal_table；保 §核心身份 直径比 0.50–0.62） | S2 `L20,L23`(1.175/0.660=1.780) |
| (—) | constraint | — | — | inequality | `_bearing_outer_radius(r) + 0.010 ≤ platter_radius`（托盘必须覆盖轴承）；违反时按比例回缩 `bearing_span_ratio` | 接口 / clearance |
| (—) | constraint | — | — | inequality | `cabinet_pullout` ⇒ `platter_radius ≤ 0.40`（柜内包络）；违反时 clamp | S7 `L21`(0.420)；摆臂净空 |
| (—) | constraint | — | — | inequality | `two_tier_round` ⇒ `upper_r = 0.714·platter_radius`，`post_ring_r = 0.536·platter_radius`（立柱须落在上下两盘公共投影内） | S3 `L24,L28` |

**连续尺寸采样契约**（`config_from_seed` → `resolve_config`）：
1. 先采 `platter_radius` / `platter_thickness` / `bearing_span_ratio` / `base_span_ratio` 等全部 `independent` 主尺度。
2. 按 `equation` 派生 `bearing_pitch_radius` → `race_half_width` → `_bearing_outer_radius` → `deck_radius` →
   `deck_top_z` → `_bearing_top_z`；`cabinet_pullout` 的 `swing_offset`/`pull_travel`/安装板/法兰/导轨全部从
   `platter_radius` 派生（因此摆臂净空 `0.36R` 对任意 R 恒成立）。
3. 用 `inequality` 回缩：`bearing_span_ratio` 回缩到使 `_bearing_outer_radius + 0.010 ≤ platter_radius`；
   `cabinet_pullout` clamp `platter_radius ≤ 0.40`。
4. `conditional` 范围（`table_height` / `tier_gap_ratio` / `tray_aspect` / 各 N 轴）在采样前按上游 enum 解析。

全部 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解，builder 不再失败。

## 7.5 编译预算 / compile budget

**自报预算：≤ 12 s/seed**（sweep `--compile-timeout 120` 仅作 hang-guard，≈10×，非质量条）。

依据：最重 seed = `pedestal_table`(2 个 cq `loft` + `union` + tabletop `fillet`) × `rounded_rect_tray`
(3 个 rounded box `fillet` + `union` + `cut`) ≈ 4–6 s；其余组合 1–3 s。库内实测参考带（典型 5–20 s）内偏低。

分档 tessellation（第一版即按此写，不做后期优化）：
- `LatheGeometry` 主体英雄面 `segments=64`（S1 L114 原为 128 → 减半；母线仅 8 点，64 段已无可见棱）。
- cadquery 主体 `tolerance=0.0015`，`angular_tolerance=0.10`；小半径特征（annulus/race/liner）`tolerance=0.0008`。
- 滚珠用 SDK `Sphere` **原语**（S13 L91-100 的做法），不走 cq sphere → N=28 时零 mesh 成本
  （S5 L69-71/L152 每颗滚珠都 `mesh_from_cadquery` 一次，是 24 次 tessellation，本模板不复制该做法）。
- **N 个相同子件复用同一个 `Mesh`**：`compartment_divider_{i}` / `upper_post_{i}` / `support_roller_{i}` /
  `corner_post_{i}` 各只生成一次 mesh/primitive，按 `Origin(rpy=...)` 重复引用。

**明确不采纳的重几何**：S10 `model.py:L26-L67` 的 `_vein_prism` 多段 `polyline().extrude()` → `union` → `intersect`
→ `blank.cut(gray_fill).cut(warm_fill)` 布尔雕刻脉纹。旧 spec 的 "Excluded Sources" 已记录该记录导致
compile timeout。本模板改用 S1 `L26-L46` 的薄 `Box` 条 `_add_surface_line` 表达同一 ④ 语义（视觉等价、成本≈0）。
S10 的**底座**（`L88-L118`）仍被 `concealed_puck` 采纳——被排除的是它的脉纹做法，不是这条记录。

## Multiplicity / Copy Logic

本模板有 **4 根独立 multiplicity 轴**，各自挂在一个真实 candidate 上，各自采样/clamp/编进 `slot_choices`。
N 计入 `raw_domain`，**不乘入 `core_domain`**。

### 轴 1：`ball_count`（Slot B `exposed_ball_ring`）
- `count_param`: `ball_count`；`observed_N`: **{12, 24}**（S13 `model.py:L91`；S5 `model.py:L28`）
- `derived_N_range`: **[10, 28]**；sampling domain: `rng.choices((10,12,14,16,18,20,24,28), weights=(2,5,4,5,3,3,4,2))`（小 N 高频、尾部稀有）
- accepted source evidence：重复单元 = S13 `L91-L100`（`Sphere(radius=...)` + `2πi/N` 均布 + `bearing_ball_{i}` 索引命名 + 无 joint，全部 deck part visual）；copy/layout helper = S5 `L146-L156`（`angle = 2πi/N`，`pitch_radius·cos/sin`）
- interpolation range/rule：观测 {12, 24} 之间的全部整数由同一个参数化 helper 生成，无需逐 N 造资产
- extrapolation range/gate：扩到 [10, 28] 的证明 —— packing：相邻滚珠弧距 `2π·pitch/N ≥ 2.2·ball_r`
  （由 `ball_r = min(0.0148·platter_radius, 0.35·2π·pitch/N)` 派生保证，N=28 最紧时自动缩珠）；
  host envelope：滚珠环恒在 `fixed_bearing_race` 的 `[pitch−race_half_width, pitch+race_half_width]` 带内；
  interface：`_bearing_top_z` 只依赖 `ball_r` 不依赖 N；category identity：滚珠环仍是 slewing race；
  joint count：恒为 0（visual）；compile budget：`Sphere` 原语，N 无 tessellation 成本；
  swept clearance：滚珠随 deck 静止，回转 race 与滚珠顶恒留 `running_clearance` 0.5 mm
- capacity/spacing formula：`angle_i = 2πi/N`，`(x,y) = pitch·(cos,sin)`，`z = deck_top_z + race_t + 0.55·ball_r`
- `validation_counts`: **{10, 12, 16, 24, 28}**（min / 观测锚点 12 / mid / 观测锚点 24 / 外推上界）
- copied object / naming / placement / joint policy：`Sphere` / `bearing_ball_{i}` / 极坐标均布 / 无 joint（deck part visual）

### 轴 2：`roller_count`（Slot B `roller_set`）
- `count_param`: `roller_count`；`observed_N`: **{3}**（S12 `model.py:L75`）
- `derived_N_range`: **[3, 6]**；sampling domain: `rng.choices((3,4,5,6), weights=(6,4,3,2))`
- accepted source evidence：重复单元 = S12 `L78-L89`（`support_roller_{i}` Cylinder + `roller_axle_{i}` Cylinder，`2πi/3` 均布，索引命名，无 joint）
- interpolation range/rule：观测仅 {3}，无内插区间
- extrapolation range/gate：扩到 [3,6] 的证明 —— packing：`2π·pitch/N ≥ 2.4·roller_r`（`roller_r` 由该式派生上限）；
  host envelope：滚轮恒在 deck 顶面上（`deck_radius ≥ pitch + roller_r + 0.010`，由 `deck_radius` equation 保证）；
  interface：`_bearing_top_z` 只依赖 `roller_t` 不依赖 N；identity：3–6 只承载滚轮仍是 roller turntable base
  （工业转盘 3/4/6 轮均为常规）；joint count：0；compile budget：Cylinder 原语无 mesh；
  swept clearance：`drive_pad` 平贴滚轮顶面（精确接触），N 不影响
- capacity/spacing formula：`angle_i = 2πi/N`，`(x,y) = pitch·(cos,sin)`
- `validation_counts`: **{3, 4, 6}**（min=观测锚点 / mid / 外推上界）
- copied object / naming / placement / joint policy：Cylinder / `support_roller_{i}` + `roller_axle_{i}` / 极坐标均布 / 无 joint

### 轴 3：`divider_count`（Slot C `segmented_wedge`）
- `count_param`: `divider_count`；`observed_N`: **{6}**（S4 `model.py:L26`）
- `derived_N_range`: **[4, 8]**；sampling domain: `rng.choices((4,5,6,7,8), weights=(3,3,6,3,2))`
- accepted source evidence：重复单元 = S4 `L74-L87`（`_radial_divider_shape()`：`box(divider_length, 0.020, h, centered=(False,True,False)).edges("|Z").fillet(0.004)`）；copy/layout helper = S4 `L199-L212`（`rpy=(0,0,2πi/N)`，`compartment_divider_{i}` 索引命名，无 joint）
- interpolation range/rule：观测仅 {6}，无内插区间
- extrapolation range/gate：扩到 [4,8] 的证明 —— packing：外缘扇区弧宽 `2π·(platter_r−rim_w)/N ≥ 3·divider_w`
  （`divider_w = min(0.030·platter_radius, 0.28·弧宽)` 派生保证，N=8 最紧时自动收窄）；
  host envelope：隔板长度 `= platter_radius − rim_w − 0.027·platter_radius`（S4 L75 的 `PLATTER_RADIUS − 0.018` 比例化），恒落在唇内；
  interface：不触碰轴承/关节；identity：4–8 格楔形分餐盘均为常规；joint count：0；
  compile budget：**一个 divider mesh 复用 N 次**；swept clearance：随托盘刚性回转，包络恒定
- capacity/spacing formula：`rpy_z_i = 2πi/N`；`divider_length = platter_radius − rim_w − 0.027·platter_radius`
- `validation_counts`: **{4, 6, 8}**（min / 观测锚点 / max）
- copied object / naming / placement / joint policy：cq mesh（复用）/ `compartment_divider_{i}` / `Origin(rpy=(0,0,2πi/N))` / 无 joint

### 轴 4：`tier_post_count`（Slot C `two_tier_round`）
- `count_param`: `tier_post_count`；`observed_N`: **{3}**（S3 `model.py:L198`）
- `derived_N_range`: **[3, 5]**；sampling domain: `rng.choices((3,4,5), weights=(6,3,2))`
- accepted source evidence：重复单元 = S3 `L198-L207`（`Cylinder(radius=POST_RADIUS, length=post_height)`，`2πi/3` 均布，`upper_post_{i}` 索引命名，无 joint，全部回转 part visual）
- interpolation range/rule：观测仅 {3}，无内插区间
- extrapolation range/gate：扩到 [3,5] 的证明 —— packing：`2π·post_ring_r/N ≥ 4·post_r`；
  host envelope：`post_ring_r = 0.536·platter_radius < upper_r = 0.714·platter_radius`（立柱恒在上下两盘的公共
  投影内，两端都有落座面）；interface：立柱不触碰轴承；identity：3–5 柱双层餐盘均为常规；joint count：0；
  compile budget：Cylinder 原语；swept clearance：与托盘同刚体
- capacity/spacing formula：`angle_i = 2πi/N`，`(x,y) = post_ring_r·(cos,sin)`，`post_height = tier_gap`
- `validation_counts`: **{3, 4, 5}**（min=观测锚点 / mid / max）
- copied object / naming / placement / joint policy：Cylinder / `upper_post_{i}` / 极坐标均布 / 无 joint（同 part visual）

### 非 multiplicity 的固定复制
`rounded_rect_tray` 的 `corner_post_{0..3}` **恒为 4**：它由圆角矩形的 4 个角**派生**（`(±(hw−cr), ±(hd−cr))`，
S6 `L155-L165`），不是自由 N 轴，不进 `slot_choices`，不计入 raw domain。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | 2 种运动学图，均 forked_anchor：(a) `base −spin→ platter`（2 parts / 1 边），来源 S1 `L193-L209`、S2 `L207-L225`、S8 `L145-L155` 等 12 个记录；(b) `cabinet_mount −PRISMATIC→ carriage −REVOLUTE→ swivel_arm −spin→ platter`（4 parts / 3 边），来源 S7 `L282-L338`。另外 Slot B 改变 deck/platter 上**可见轴承硬件的存在性**（滚珠环/滚轮组/主轴 vs 隐藏盖），Slot A 改变底座硬件存在性（马达舱/接线/电缆 vs 无）——同属①但不新增边 |
| └ multiplicity | 同构件 ×N | **有** | 4 根轴，见 §8：`ball_count` obs{12,24}→[10,28]；`roller_count` obs{3}→[3,6]；`divider_count` obs{6}→[4,8]；`tier_post_count` obs{3}→[3,5]。各有重复单元/copy-rule 精确来源 + 插值/外推 gate + validation_counts |
| ② 关节类型 | 图不变，某条边换 type/轴 | **有** | spin 边：`REVOLUTE`(axis (0,0,1), `[-π,+π]`) — S1 `L193-L209`、S2 `L207-L225`、S13 `L179-L194`；`CONTINUOUS`(axis (0,0,1), 整圈) — S8 `L145-L155`、S9 `L229-L239`、S11 `L148-L158`、S12 `L246-L256`。均 forked_anchor。`cabinet_pullout` 额外引入 `PRISMATIC`(axis (1,0,0)) — S7 `L282-L296`。**声明的 3 种类型都必须在 sweep 的 `axis_realization` 里出现** |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | 6 个 candidate 全部 **direct source-backed**（无外推），各自登记进 `slot_choices` 并标 `form_subtype`：`lathe_stone_slab`=Volumetric Envelope Form(S1 `L103-L129`)；`chamfered_stone_disk`=Volumetric Envelope Form(S8 `L88-L94`/S11 `L92-L104`)；`veneered_wood_disk`=Macro Surface Construction(S13 `L126-L148`)；`two_tier_round`=Macro Surface Construction(S3 `L192-L246`)；`segmented_wedge`=Macro Surface Construction(S4 `L64-L87`)；`rounded_rect_tray`=**Planar Boundary Form**(S6 `L30-L61`，投影轮廓圆→圆角矩形)。另 Slot A 的 5 个底座本身也是③（扁平盘/loft 基座桌/低 puck/机壳/柜内摆臂） |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | 5 个 style（Slot E 表，全部 `record_only`）：`marble_veins`(S1 `L166-L185`)、`tile_grout`(S1 `L139-L162`)、`radial_inlay`(S12 `L218-L233`)、`veneer_seams`(S13 `L152-L162`)、`plain_polished`(S1 `L132-L137`)。装饰数量档随 style 固定（veins 7 / grout 4+7 / inlay 4+1 / seams 8 / plain 0）+ 恒定 1 个 `orientation_mark`。**共形嵌入**：全部由 `_PlatterSurface.extent_at(θ)` 逐角派生长度/位置、由 `_PlatterSurface.top_z` 派生高度 → 派生顺序 ③(platter_form) → ⑤(platter_radius/thickness) → ④(装饰最后生成，读最终顶面)。`rounded_rect_tray` 下 `extent_at(θ)` 返回圆角矩形边界（非常数半径），装饰随之变短/改向——即 Container_Tube `label_band` 反例的正解 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | **有** | 关键比例见 §7：`platter_radius` [0.16,0.68]（4.25×）、`platter_thickness` [0.016,0.036]（2.25×）、`bearing_span_ratio` [0.20,0.46]、`base_span_ratio` [0.42,0.95]、`tray_aspect` [0.62,0.92]、`tier_gap_ratio` [0.40,0.58]、`table_height` [0.62,0.76]。**运动包络**：`spin` axis (0,0,1)，开启方向 = 俯视逆时针为正，`[-π, +π]`（REVOLUTE）/ 整圈（CONTINUOUS）；`mount_to_carriage` axis (1,0,0)，开启方向 +x（出柜），`[0, 0.571·platter_radius]`；`carriage_to_swivel_arm` axis (0,0,1)，`[-1.22, +1.22]`。`motion_test_plan` 见 §6.5 validator 列：全部跑 `fail_if_parts_overlap_in_sampled_poses`，CONTINUOUS 覆盖 0/π/2/π/3π/2 整圈，无 broad allowance / 无 exemption |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 6 个配色，rgba 全部实测自样本：`warm_marble_charcoal`(S1 `L59-L66`)、`rose_marble_walnut`(S2 `L91-L97`)、`walnut_brass_steel`(S9 `L22-L31`)、`warm_wood_brass`(S13 `L51-L59`)、`white_marble_steel`(S10 `L80-L86`)、`powdercoat_bronze`(S6 `L74-L79`)。材质大类 5 类：**stone**(1,2,5)、**wood**(2,3,4)、**metal**(全部 bearing/brass/bronze)、**painted**(6 powder coat)、**rubber/plastic**(3,4,5) ≥ `ceil(0.5×6)=3` ✓ |

**收尾自检**：§9 的 set-cover 用 `slot_choices_for_seed` 选种，覆盖 A/B/C/D 全部离散值、E/F 全部值、
4 根 N 轴各自的 `validation_counts`（observed anchors + derived min/max + 外推边界）。

## 采样与覆盖审计

core theoretical：A × B × C × D = 5 × 5 × 6 × 2 = **300**（不含 N、不含 ④⑥）
raw theoretical：gated core × 各 candidate 条件下的 N 档乘积（`ball_count` 8 档 / `roller_count` 4 档 /
`divider_count` 5 档 / `tier_post_count` 3 档）；`multiplicity_coverage` 单列，见 §8。

实际合法组合域：由 MatingContract（bearing land ↔ rotor 面）、尺寸不等式
（`_bearing_outer_radius + 0.010 ≤ platter_radius`；`cabinet_pullout ⇒ platter_radius ≤ 0.40`）、
类别身份（§核心身份 直径比 0.50–0.62；竖直轴过对称中心线）和 swept-clearance validator 定义。
跨来源 module 可自由重组（例：S12 的 `roller_set` + S6 的 `rounded_rect_tray` + S8 的 `concealed_puck` 是
样本池中不存在的新资产），不要求共同来源；但 `## Compatibility Gates` 的 3 条 deny 行未通过验证，不开放。

理由：gate 后 core = **260**（实测 `slot_choices_for_seed` over seeds 0-999，去 ④⑥/N），≥ `rich` floor 120，且 ≥ 非阻断 target 200。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对每个普通 seed
（**包括 seed 0，无特判**）独立采样 A/B/C/D/E/F 六个 enum + 全部连续 scale + 各 N 轴，然后过
`_gate_bearing` / `_gate_platter` compatibility gate（非法组合**降级到声明的 fallback**，不是拒绝重采，
保证 `slot_choices_for_seed` 与实际 build 一致），再进 `resolve_config` 做 clamp/派生/回缩。
无 regression overrides。random sweep：`0-15`(fast) → `0-35`(final) → corner(自动选边界 seed)。
viewer 目检范围：§8.5 收尾自检的 set-cover 选种。

Combination Domain：core 只计 A/B/C/D（①②③ + 真实功能 module）= 260（实测）；raw 再加入 4 根有界 N；
multiplicity 单列可达值和边界（§8 `validation_counts`）；profile floors=16/48/120/120，rich target=200 非阻断。
`palette_style`(⑥) / `surface_style`(④) / 材质 / 连续尺寸**不膨胀 core**（虽登记进 `slot_choices` 做覆盖证明）。

Controlled local parameterization：`platter_radius`、`platter_thickness`、`bearing_span_ratio`、
`base_span_ratio`、`table_height`、`tier_gap_ratio`、`tray_aspect`。全部在 `resolve_config` 内 clamp/派生，
按 §7 的 `约束类型` 声明函数依赖并遵循连续尺寸采样契约（先 independent → equation 派生 → inequality 回缩
→ conditional 解析）。跨部件依赖（`deck_radius` ← `_bearing_outer_radius`；cabinet 全套 ← `platter_radius`）
显式声明为 `equation`，不当作互相独立的自由变量各抽各的。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→D→E→F 独立提出 choice，再过 `_gate_bearing`/`_gate_platter` 条件 gate；N 轴按 candidate 条件加权采样（小 N 高频） | `slot_choices_for_seed` == build 实际 choices（`model.meta["slot_choices"]`，由 `run_tests` 逐 key 断言） |
| compatibility matrix | 见 `## Compatibility Gates` | interface/dimension/identity/swept-clearance 全通过；不开放未验证笛卡尔积 |
| controlled local variation | 7 个连续 scale + clamp/派生（§7） | 比例变化不破坏 interface、clearance、支撑、joint origin、类别身份 |
| regression overrides | none | — |
| random sweep | 0-15 → 0-35 → corner；成熟审计 0-999 | 契约失败；`axis_realization`；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A base_form | 5 | yes | yes | |
| B bearing_style | 5 | yes | yes | |
| C platter_form | 6 | yes | yes | ③ 主体形态家族 slot |
| D spin_joint | 2 | yes | no | ② 只有 REVOLUTE/CONTINUOUS 两种真实取值；池内无第三种竖直回转关节语义，无法凑 3 |
| E surface_style | 5 | yes | yes | ④，不计 core |
| F palette_style | 6 | yes | yes | ⑥，不计 core |

## Compatibility Gates

| # | rule | verdict | 理由 | fallback |
|---|---|---|---|---|
| G1 | `platter_form == rounded_rect_tray` AND `base_form == pedestal_table` | **deny** | 类别身份：基座圆桌里嵌的 lazy susan 是**圆盘**（S2 L282-290 断言 `platter_diameter/table_diameter ∈ [0.53,0.59]` 且 `expect_within(marble_disk ⊂ tabletop, axes="xy")`）；圆角矩形托盘嵌进圆桌面会破坏该内切身份约束 | → `chamfered_stone_disk` |
| G2 | `platter_form == rounded_rect_tray` AND `base_form == powered_console` | **deny** | 类别身份：电动宴会转盘（S9/S12）是圆形迎宾面，矩形托盘 + 减速驱动无真实原型；且 S12 的 `control_pod`(x=0.845·deck_r) 需被圆盘遮蔽，矩形托盘的逐角半径在对角方向外露、正交方向内缩，遮蔽关系不成立 | → `veneered_wood_disk` |
| G3 | `bearing_style == spindle_thrust` AND `base_form == pedestal_table` | **deny** | 机械不合理：S11 的主轴止推是 `pitch≈0.079`、托盘 `R=0.275` 的小型 puck 方案（跨距比 0.29，边缘无支撑）。`pedestal_table` 的托盘 `R` 可达 0.68（1.36 m 石盘）；单点主轴止推无法承托 1.36 m 石盘边缘 —— 池内无此原型，属未经验证的高风险组合 | → `flat_race_pair` |

deny 规则以外的组合全部开放；其中跨来源重组（如 `powered_console`+`exposed_ball_ring`+`two_tier_round`）
由 MatingContract + 尺寸不等式 + swept-clearance validator 机械证明，不需要共同来源。
被 deny 的组合按 fallback 降级到合法候选，因此 `slot_choices_for_seed` 永远返回可 build 的组合；
精确 gated core 计数以 `combo-audit` 为准（spec 记 deny 规则，不手算）。

## Combination Domain

- profile: `rich` · reason: 4 根真实离散轴（5×5×6×2）全部 source-backed 且可跨来源重组；13 个样本覆盖
  5 底座 / 5 轴承 / 6 主体形态 / 2 关节类型 · floor: 120 · target: 200（非阻断）· exception: **none**（无需 hash-bound 例外）
- gated core count: **260**（实测 seeds 0-999；`combo-audit` 为最终权威）
- raw count: gated core × 各 candidate 条件下的 N 档乘积（`ball_count` 8 档 / `roller_count` 4 档 /
  `divider_count` 5 档 / `tier_post_count` 3 档）
- N admitted / reachable / min-mid-max：见 §8 四轴的 `derived_N_range` 与 `validation_counts`
- 排除项：`palette_style`(⑥)、`surface_style`(④)、材质大类、`corner_post_count`(=4 固定派生)、
  全部连续 ⑤ 尺度 —— 均**不计入 core**

## Visual Risk

- `multi_joint`：`cabinet_pullout` seed 有 3 条运动边（PRISMATIC + 2×REVOLUTE），组合位姿需覆盖
  retracted+swung 这个最紧包络（sampled poses 的笛卡尔积会命中）。缓解：全套柜内尺寸由 `platter_radius`
  派生，摆臂最紧净空 `0.36R` 对任意 R 恒成立（§6.5）。
- `curved_fit`：④ 装饰必须贴合 `rounded_rect_tray` 的圆角矩形边界与 `two_tier_round` 的上层面。
  缓解：`_PlatterSurface.extent_at(θ)` 单真源逐角派生（§Form Dependency Contracts 表）。
- `telescopic`：`mount_to_carriage` 是单级抽拉（非嵌套多级），行程 `0.571R` < 安装板长 `1.667R`，
  全程保持导轨啮合。
- 类别特有风险 **`bearing_stack_z_chain`**：`deck_top_z → _bearing_stack_height → _bearing_top_z → platter 局部 z=0`
  这条 z 链一旦有一处写死常量，托盘就会悬空或陷进底座（正是 Contract 3e 的高发点）。缓解：z 链每一段
  只在一个 helper 里定义，consumer 全部调用该 helper，无第二处 restate。
- **无** drawer / wheel_caster / hidden_slide 风险（见 §6.5 末尾说明）。

## Validator

- `slot_choices_for_seed` returns implemented module names（A/B/C/D/E/F 六 key + 条件 N key）
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds，**seed 0 不特殊**
- compatibility matrix / gating prevents illegal module combinations（G1–G3，降级而非 builder 失败）
- optional regression overrides are sparse and justified → **none**
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped and cannot break interfaces, clearance, joint origin, or category multiplicity
- cross-part scale dependencies (`deck_radius` ← `_bearing_outer_radius`；cabinet 全套 ← `platter_radius`)
  are resolved in `resolve_config`, not left to fail in the builder
- critical InterfaceSpec / MatingContract points exist：spin(`bearing land` ↔ `rotor`)、
  `mounting_plate`↔`pullout_arm`、`swivel_boss`↔`pivot_plate`
- key joints have expected type / axis / range：spin = REVOLUTE`[-π,+π]`|CONTINUOUS，axis (0,0,1)；
  pullout = PRISMATIC axis (1,0,0) `[0, 0.571R]`；swivel = REVOLUTE axis (0,0,1) `[-1.22,+1.22]`
- copied objects follow naming and placement policy：`bearing_ball_{i}` / `support_roller_{i}` /
  `compartment_divider_{i}` / `upper_post_{i}` / `corner_post_{i}`
- every moving module is a complete solid with visible support/guide and closed/mid/max clearance
- **no whole-part overlap allowance；本模板 0 条 `allow_overlap`**（§6.5）
- 回转语义断言**不得用 `part_world_position`**（它返回 part frame 原点，恰在 spin 轴上，revolute 下位移恒为 0）；
  必须用 `part_element_world_aabb(platter, elem="orientation_mark")` 的中心。`part_world_position` 只用于
  PRISMATIC(`carriage`) 平移断言。

## Reject cases

1. **spin 轴不过硬件对称中心线**或轴不是 (0,0,1) → 不是 lazy susan（`fail_if_articulation_origin_far_from_geometry`）。
2. **托盘悬空 / 陷入底座**：z 链 `deck_top_z → _bearing_top_z → platter z=0` 任一段写死常量而不随
   `base_form`/`bearing_style`/⑤ 尺度联动（Contract 3e）→ `fail_if_joint_mating_has_gap`。
3. **轴承露在托盘外**：`_bearing_outer_radius + 0.010 > platter_radius` → 违反 §核心身份 (b)(c) 覆盖关系。
4. **装饰脱离宿主面**：④ 用常数半径/常数长度铺在 `rounded_rect_tray` 或 `two_tier_round` 上
   （Container_Tube `label_band` 反例）→ Rule 4 blocker。
5. **用 `part_world_position` 断言回转** → 恒测得 0 位移，是假通过。
6. **把不动的轴承硬件/装饰做成 FIXED joint 的独立 part**（S7 L314-320 的 `swivel_arm_to_support` 即此形）→ Rule 1 blocker。
7. **降级 primitive**：把 `LatheGeometry`(S1 L113-116) / `mesh_from_cadquery` loft(S2 L28-51) / cq chamfer
   换成裸 `Box`/`Cylinder` → Rule 3 blocker。
8. **用 `allow_overlap` 或把 `motion_limits` 收成 `lower=upper=0` 掩盖穿模** → 直接 blocker
   （旧 replay 模板 `picturex_0611_source_replay.py:L74-L95` 正是把每个 REVOLUTE/PRISMATIC 关节钳成
   `lower=0, upper=0`，使 `harness_motion_qc` 只采到闭合位姿 —— 运动门被完全架空）。

## Authoring 自检记录
| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| self-check notes | 13/13 样本全读；A/B/C/D 四轴 candidate 均有 accepted record + 精确 `model.py:Lx-Ly`；③ 全 direct source-backed（Form Dependency Contracts 无外推条目）；4 根 N 轴均有重复单元/copy-rule 精确来源 + gate + validation_counts；§8.5 六轴逐根考察无空格；编译预算自报 ≤12 s 并已声明分档 tessellation 与"不采纳 S10 布尔脉纹"；0 条 allow_overlap；3 条 deny gate 均给理由 + fallback；`seed=0` 不特殊。**上游 source map `articraft_data/picture_expansion/template_source_maps/0611__lazy_susan.md` 在磁盘上不存在**（该目录 326 个文件中无 lazy_susan 条目），本 spec 的 slot/candidate/exclusion 表因此直接从 13 个 `model.py` 反推，未受 source map 约束——建议上游补该文件。 |
