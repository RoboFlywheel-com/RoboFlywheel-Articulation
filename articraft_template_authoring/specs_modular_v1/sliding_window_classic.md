# sliding_window_classic — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `sliding_window_classic` |
| template path | `agent/templates/sliding_window_classic.py` |
| test path (optional) | `tests/agent/test_sliding_window_classic_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：核心是 `parallel_children`（一个静态 `frame`(周边 ring + sill + 双/三轨道) root 上挂一个可动 `sliding_sash`(PRISMATIC 横滑) + 一个 `fixed_lite`(FIXED 或烘焙进 frame)），叠加 **关节承载的 named-slot 选择轴**（fixed_glazing 拓扑 A、track/carriage 样式 B、lock 关节 C、handle 样式 D）+ **一条轻 multiplicity 轴**（sash_count {1,2} / meeting-muntin 分隔条 N）。横滑 PRISMATIC 是 category-defining motion。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 48 (curated DATASET 池 54 条中 rating≥5 的 48 条) |
| read_count | ~24 完整读取 + 全部 54 经分簇审计覆盖 |
| read_scope | 代表性 sample across all structural clusters of the 54-record curated pool (NOT single-parent forks) |
| source_index_policy | only adopted module sources are indexed below |

要点（已完整读 rec_sliding_window_0001..0005 + ~19 个 hex 代表，跨全部 54 条分簇）：

- **统一坐标系**：所有样本一致 — +Z 向上、宽沿 X、frame depth / 玻璃厚 / 滑动法向无关、玻璃面在 X-Z 立面、sill 在底、窗站立。
- **统一根装配**：每样本一个**静态 `frame` root part**（周边 jamb/head/sill + 双(或三)轨道槽 + lip 唇），一个可动 sash 经 **PRISMATIC** 横滑挂上。固定玻璃光要么是**独立 `fixed_lite`/`fixed_segment` part（FIXED joint）**，要么**烘焙进 frame 作 visual**，要么**无固定光**（单玻璃舱口 / 标定 / 安全窗）。
- **机构是类别身份**：可动 sash 沿框宽 **PRISMATIC** 平移（axis (±1,0,0)）= category-defining motion。53/54 沿 ±X（多数 -X 向左开，部分 +X 向右开），1 条 dd9f8469 沿 ±Y（rating2 边角），645606 双向中停（lower=-travel/2）。**无任何竖向双悬 ±Z 滑窗。无 2-sliding-sash。**
- **共享 sash 工厂**：0004 `_build_sash(meeting_left, moving)` L90-263、0005 `_add_glazed_sash(meeting_side)` L49-229、0001 `_add_glazed_panel` L51-147 — 同一 helper 双面复用建 fixed 与 sliding 两扇（含 stile/rail/glass-rebate/gasket/interlock-fin）。
- **承载 hardware**：rollers(`roller_*` Cylinder)/glides(`bottom_glide_*`)/top-guides 在 sash 上，run 在 frame 轨道 lip 间；通过 `expect_contact`/`expect_gap` 断言 roller-on-runner、top-guide-captured。glass rebate 嵌入 stile/rail lip 下。
- **lock 关节谱**：多数无 articulated 锁（passive keeper / interlock fin）；0005/02310a01 真 REVOLUTE 拇指扳手（独立 latch part，axis(0,1,0)）；43f22f89 crescent cam REVOLUTE + keeper plate；b5bb4681 PRISMATIC lift-out 锁定销（axis(0,0,1)）。a9564b40/dc83a7ca 还有 REVOLUTE 维修盖（field-service 边角）。
- **multiplicity 母体**：sash_count 与 muntin 分隔的 loop-emission 母体取 0004 / 0005（共享 sash 工厂 + fastener/runner for-loop 已 PASS）；roller/glide/track-rib/bolt 等同构 hardware 一律 for-loop 发射（0004 L48-69/L176-201、a9564b40 L886-999、f0621fda L646-674）。0001/0003 的 rollers 手写需改 for-loop；dd9f8469 muntin 手写需改 for-loop。

## 核心身份

一扇 **建筑横滑窗（sliding window）**：一个静态外框（`frame` = 周边 jamb/head/sill ring + 双或三轨道槽 + 上下 lip 唇）容纳至少一个 **glazed sash**，其中**一个 sash 经横向 PRISMATIC 滑轨**沿框宽平移成为可动开启扇（category-defining motion），常配一个固定玻璃光（fixed lite，独立 FIXED part 或烘焙进 frame）。sash 底/顶配 roller / glide / top-guide 在轨道 lip 间承载，meeting stile 处有 interlock fin + seal，可有 pull / flush-recess / finger 把手、passive keeper 或 articulated 拇指/月牙锁。成熟域 = 住宅 / 工业 / 标定 / 安全 / retrofit 横滑窗，铝 / 白 vinyl / 深阳极氧化 / 木-黄铜等饰面。

不该混入的相邻类别见 §与相邻类别的边界。**特别注意**：本 slug 是 sibling slug `sliding_window`（建自另一 qwen fork pool）的**并行/替代模板**，identity 重叠（都是横滑 PRISMATIC），两者可共存；本 slug 建自 54 条 curated DATASET 池。铰链外摆（REVOLUTE 主开启）的 casement / awning / fixed picture 属 `window` 小类，不在本 Slot A 机构内。

## 槽位 + 候选模块表

### Slot A：fixed_glazing_topology（固定玻璃光的承载拓扑 — 关节承载主槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| separate_fixed_part（基线） | rec_sliding_window_0004 | L422-455 (`fixed_lite` part L422-434 + `frame_to_fixed_lite` FIXED L449-455 + `frame_to_sliding_sash` PRISMATIC L456-469) | eligible if compatible | 固定光是独立 part 经 **FIXED** joint 挂 frame；3-link tree(frame + fixed_lite + sliding_sash)；共享 `_build_sash` 工厂 L90-263 |
| separate_fixed_part(latch 变体) | rec_sliding_window_0005 | L340-453 (`fixed_sash` FIXED L419-425, `moving_sash` PRISMATIC L426-439) | eligible if compatible | 同 separate 但 fixed 是 `fixed_sash`；`_add_glazed_sash(meeting_side)` L49-229；为 Slot C thumbturn 提供共生母体 |
| baked_into_frame | rec_sliding_window_0001 | L235-251 (`fixed_panel_*` visuals on frame) + L301-314 (单 PRISMATIC) ；亦 rec_sliding_window_0002 L177-206 / 0003 L224-321 | eligible if compatible | 固定光烘焙进 `frame` part 作 visual(`fixed_glass`/`fixed_meeting_stile`/`fixed_mullion`)；2-link tree(frame + sliding_sash) |
| sash_only_no_fixed | rec_sliding_window_b5bb4681 | sash-only(无 `fixed_*`，frame 仅周边 ring，sash 占满开口) ；亦 rec_sliding_window_cbfa0ab2 / 168d233e / 56eeb897 | eligible if compatible | 无固定光；单 sliding sash 占满开口(service hatch / 标定 / 安全 / 单玻璃舱口) |

降级说明：4 候选(前两个同属 separate-fixed 家族但一个共生 thumbturn 母体)。每个候选改变 part tree(3-link vs 2-link vs sash-only) 与 joint count(FIXED+PRISMATIC vs 仅 PRISMATIC)，即拓扑等价类。

### Slot B：track_carriage_style（滑轨 / 承载方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| lipped_dual_channel（基线） | rec_sliding_window_0004 | L334-370 (`rear_runner`/`front_runner`/`*_head_guide` L334-348 + `*_outer_lip`/`*_center_lip` 三 lip loop L350-370) + sash glide L176-201 | eligible if compatible | frame 双(三)槽 box 轨道 + 上下 lip 唇 + sash `bottom_glide_*`/`top_guide_*` 滑块；box 唇槽内滑动(无圆轮) |
| roller_truck_cylinders | rec_sliding_window_7404a1 | `roller_0/1` **Cylinder** + brackets L114-127 + 钢轨 track_bed L37-50 ；亦 0002 L319-330 / 0003 L436-453 / f0907748 | eligible if compatible | sash `roller_*` 圆柱尼龙轮(横轴 Cylinder) + `roller_housing`/`carriage_block`，滚在 frame 钢轨上(roller-truck) |
| triple_rib_guide | rec_sliding_window_f0621fda | back/separator/front 3 肋 `for` loop L646-674 ；亦 06ab752a L178-212 / 66a60f L158-180 | eligible if compatible | 三道导轨肋(rear/center/front) 分隔前(固定光)/后(滑扇)道，嵌套 loop 发射 |
| cadquery_hollow_channel | rec_sliding_window_645606 | `_build_frame` CadQuery slab.cut 轨道 + drain-slot loop L56-64 ；亦 bdc4eb7a / eb85aa07 | eligible if compatible | 实心 slab CadQuery boolean 切空 frame/sash shell + 切出轨道槽 + drain slots(非 box 拼装) |

降级说明：4 候选。每个改变 frame 轨道 primitive(box-lip vs Cylinder-roller vs 三肋 loop vs CadQuery-cut) 与 sash 承载件(glide-shoe vs roller-cylinder)，即拓扑等价类。

### Slot C：lock_articulation（锁五金 — 关节承载主槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none_passive_visual（基线） | rec_sliding_window_0001 | `latch_thumbturn` visual L283 (无 joint) ；亦 0002 `keeper_latch` / 0003 / 多数样本 | eligible if compatible | 锁/keeper 仅 visual，无独立 joint；或纯 interlock fin + seal；无 articulated 锁 |
| thumbturn_revolute | rec_sliding_window_0005 | `latch` part L388-417 + `moving_sash_to_latch` **REVOLUTE axis(0,1,0)** L440-453 ；亦 02310a01 `sash_to_latch` REVOLUTE | eligible if compatible | 独立 `latch` part(escutcheon+pivot_boss+thumbturn+thumb_pad) 绕 Y 轴翻转的拇指扳手锁 |
| crescent_cam_revolute | rec_sliding_window_43f22f89 | `latch_pivot` **REVOLUTE axis(0,1,0)** L247-256 (`pivot_hub`+`latch_bar`) + jamb `keeper_plate` | eligible if compatible | 月牙 / quarter-turn 凸轮锁绕 Y 转入对面 keeper plate |
| lockout_pin_prismatic | rec_sliding_window_b5bb4681 | `frame_to_lock_pin` **PRISMATIC axis(0,0,1)** (lift-out red T-handle `lock_pin` part) | eligible if compatible | 工业 lift-out 锁定销：独立 `lock_pin` part 竖向 PRISMATIC 升降锁住 sash |

降级说明：4 候选。none 改 0 joint，thumbturn/crescent 各加 1 REVOLUTE(独立 latch part)，lockout-pin 加 1 PRISMATIC(独立 pin part)；joint count/type 不同即拓扑等价类。round/安全/标定边角的额外 REVOLUTE 维修盖(a9564b40/dc83a7ca) 与 CONTINUOUS 标定旋钮(cbfa0ab2) **不进首版 seed domain**(主题外、收敛风险高)，作为 reviewer 可选扩展记录在 §模板实现备注。

### Slot D：handle_style（把手样式 — parallel visual slot）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pull_bar（基线） | rec_sliding_window_0002 | `pull_base`/`pull_grip` L344-355 ；亦 0003 `pull_plate`+`pull_grip` L475-490 / 0004 `pull_handle`/`handle_rib` L220-238 | eligible if compatible | 凸出拉杆 / D-bar(base + grip 两段) |
| flush_recess | rec_sliding_window_02310a01 | `flush_pull_recess`+`pull_lip` L234-245 ；亦 0001 `flush_pull` / 0f5d4168 | eligible if compatible | 嵌入式凹槽拉手(recess + lip + shadow slot)，不凸出 |
| finger_pull | rec_sliding_window_43f22f89 | `finger_pull` L203-208 ；亦 56eeb897 Cylinder L119-127 / 5e1f21 `pull_lip` / b801112c | eligible if compatible | 小指拉条 / 指洞，极简窄条 |
| molded_grip_ribs | rec_sliding_window_7404a1 | `grip_rib_{idx}` **for-loop** L93-94 | eligible if compatible | 模塑防滑横肋(for-loop 发射 N 条)，rugged 抓握面 |
| d_pull_plate | rec_sliding_window_a9564b40 | `pull_handle` bar + 2 mounts L956-958 ；亦 cc24515a spline-tube L983-1003 / 80a9c9 | eligible if compatible | 重型 D 把手装在外凸 mount/plate 上(field-service) |

降级说明：5 候选。handle 是 parallel visual slot(挂 sliding sash 的 parent visual，随 sash 运动，无独立 joint)，但 5 个样式 primitive 不同(box-bar vs recess-cut vs finger-cylinder vs rib-loop vs D-bar-on-mount)，作 module-local variant 影响 sash 表面 part 集。

## 槽位图（slot graph）

pattern: mixed（parallel_children 固定 named slots + 一条轻 multiplicity 轴）

```
                         track_carriage_style (Slot B)
                                │ 决定 frame 轨道 primitive 与 sash 承载件(glide/roller)
                                ▼
   [root: frame]  ──parent visual──> {jamb/head/sill ring, 双/三轨道槽 + lip,
     (静态 root part)                  (Slot A=baked 时) fixed_glass/fixed_meeting_stile/mullion,
                                       drain/weep, fasteners(for-loop), corner plates(for-loop)}
        │
        │  Slot A=separate_fixed_part:
        │    └─[FIXED + interface: fixed glide on rear runner / fixed stile on jamb]─> fixed_lite (静态 part)
        │
        │  always (category-defining):
        │    └─[PRISMATIC axis(±1,0,0) + interface: sash glide/roller on front runner,
        │       top-guide captured under head lip, meeting interlock fin vs fixed]─> sliding_sash (可动 part)
        │            ├─ sliding_sash 内含 Slot D handle (parent visual on sash)
        │            ├─ sliding_sash 内含 rollers/glides/top-guides (for-loop, parent visual)
        │            └─ sliding_sash 内含 meeting/muntin bar (Slot 轻 multiplicity, parent visual)
        │
        │  Slot C=thumbturn / crescent:
        │    └─[REVOLUTE axis(0,1,0) on sliding_sash meeting stile]─> latch (可动小 part)
        │  Slot C=lockout_pin:
        │    └─[PRISMATIC axis(0,0,1) on frame jamb/head]─> lock_pin (可动小 part)
        │  Slot C=none: 仅 keeper/interlock visual(无 joint)
```

跨 slot 接口点位：

- **frame → sliding_sash（category-defining PRISMATIC）**：interface = sash 底 glide/roller 坐在 frame **front runner / track lip** 上(`expect_contact` roller-on-runner)，sash 顶 top-guide 被 **head lip / ceiling** 捕获(`expect_gap` captured)，meeting interlock fin 对 fixed meeting stile(`expect_overlap`/`expect_gap` seal break)。joint = PRISMATIC，axis (±1,0,0)，origin 在闭合位 sash 边 (SASH_CLOSED_X, FRONT_TRACK_Y, SASH_BASE_Z)，motion_limits lower/upper = 净开口宽(0..-travel 或 0..+travel；645606 双向 ±travel/2)。来源 0004 L456-469 / 0005 L426-439 / 0003 L492-505。
- **frame → fixed_lite（Slot A=separate）**：interface = fixed glide 坐 rear runner、fixed outer stile 抵 left jamb。joint = FIXED，origin (FIXED_X, REAR_TRACK_Y, ...)。来源 0004 L449-455 / 0005 L419-425。
- **sliding_sash → latch（Slot C=thumbturn/crescent）**：interface = latch escutcheon 贴 sash meeting stile。joint = REVOLUTE，axis (0,1,0)，origin 在 meeting stile 外面 (LATCH_X, -SASH_DEPTH/2, LATCH_Z)，limits 约 [-1.05, 0.15]。来源 0005 L440-453 / 43f22f89 L247-256。
- **frame → lock_pin（Slot C=lockout_pin）**：interface = pin 滑入 sash 上的孔/keeper。joint = PRISMATIC，axis (0,0,1)，竖向升降。来源 b5bb4681。

互斥 / 派生关系：

- Slot A=sash_only ⇒ 无 fixed_lite part；Slot C lockout_pin 仍可(锁 sash 到 frame)；thumbturn/crescent 的 keeper 改为 frame jamb 而非 fixed stile。
- Slot A=baked_into_frame ⇒ 固定光是 frame visual，无独立 FIXED part；2-link tree。
- Slot B=cadquery_hollow ⇒ frame/sash 用 CadQuery boolean，segments 须 ≤56 防退化(参 MEMORY roller-skate)。
- Slot C 的 thumbturn/crescent latch 须 anchor 在 sliding_sash 的可见 meeting stile 实体面(非薄不可见框边) → 否则 joint-origin 漂浮。

## 每槽位 Module Emits / Interfaces

### Slot A / module separate_fixed_part
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_lite`/`fixed_sash`(静态)；`sliding_sash`(可动)；root `frame` | 0004 / model.py:L422-447 |
| internal joints | `frame_to_fixed_lite` FIXED + `frame_to_sliding_sash` PRISMATIC | 0004 / model.py:L449-469 |
| upstream interface | fixed glide 坐 rear runner、fixed outer stile 抵 jamb | 0004 / model.py:L504-545 |
| downstream interface | PRISMATIC axis(±1,0,0) origin 闭合位 sash 边；travel = 净开口宽 | 0004 / model.py:L456-469 |

### Slot A / module baked_into_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_sash`(可动)；root `frame` 含 `fixed_glass`/`fixed_meeting_stile`/`fixed_mullion` visual | 0001 / model.py:L235-251 |
| internal joints | 仅 `frame_to_sliding_sash` PRISMATIC(无 fixed joint) | 0001 / model.py:L301-314 |
| upstream interface | sliding glide 坐 sliding_track_base、top-guide 被 head_guide 捕获 | 0001 / model.py:L184-230 |
| downstream interface | PRISMATIC axis(1,0,0)；closed pose 靠右 jamb，open pose 叠在 fixed lite 后 | 0001 / model.py:L301-358 |

### Slot A / module sash_only_no_fixed
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_sash`(可动占满开口)；root `frame` 仅周边 ring | b5bb4681 / sash-only |
| internal joints | 仅 `frame_to_sash` PRISMATIC | b5bb4681 |
| upstream interface | sash 单道轨 channel lip 承载，无 meeting fin(无对扇) | b5bb4681 |
| downstream interface | PRISMATIC axis(±1,0,0)；full-bay travel | b5bb4681 |

### Slot B / track_carriage_style emits（影响 frame 轨道 + sash 承载件）
| emits | 描述 | 来源 |
|---|---|---|
| lipped_dual_channel | frame `*_runner`/`*_outer_lip`/`*_center_lip`(loop) + sash `bottom_glide_*`/`top_guide_*` | 0004 / model.py:L334-370, L176-201 |
| roller_truck_cylinders | frame 钢轨 track_bed + sash `roller_{i}` Cylinder(for-loop) + `roller_housing`/`carriage_block` | 7404a1 / model.py:L37-50, L114-127 |
| triple_rib_guide | frame back/separator/front 三肋(for-loop) + sash glide-shoe | f0621fda / model.py:L646-674 |
| cadquery_hollow_channel | frame/sash CadQuery slab.cut 开口+轨道槽(segments≤56) + drain-slot loop | 645606 / model.py:L56-64 |

### Slot C / lock_articulation emits
| emits | 描述 | 来源 |
|---|---|---|
| none_passive_visual | sash/frame 上 `keeper`/`latch_thumbturn` visual + interlock fin(无 joint) | 0001 / model.py:L283 |
| thumbturn_revolute | 独立 `latch` part(escutcheon+pivot_boss+thumbturn) + REVOLUTE axis(0,1,0) | 0005 / model.py:L388-417, L440-453 |
| crescent_cam_revolute | 独立 latch(`pivot_hub`+`latch_bar`) + REVOLUTE axis(0,1,0) + jamb keeper_plate | 43f22f89 / model.py:L247-256 |
| lockout_pin_prismatic | 独立 `lock_pin` part + PRISMATIC axis(0,0,1) 升降锁定销 | b5bb4681 |

### Slot D / handle_style emits（sliding_sash parent visual，随 sash 运动，无独立 joint）
| emits | 描述 | 来源 |
|---|---|---|
| pull_bar | `pull_base`/`pull_grip` 凸出两段 | 0002 / model.py:L344-355 |
| flush_recess | `flush_pull_recess`+`pull_lip`+shadow slot 嵌入槽 | 02310a01 / model.py:L234-245 |
| finger_pull | `finger_pull` 窄条/Cylinder 指拉 | 43f22f89 / model.py:L203-208 |
| molded_grip_ribs | `grip_rib_{i}` for-loop 发射 N 条肋 | 7404a1 / model.py:L93-94 |
| d_pull_plate | `pull_handle` bar + 2 mount 外凸座 | a9564b40 / model.py:L956-958 |

### 轻 multiplicity / sash_count & meeting-muntin emits
| emits | 描述 | 来源 |
|---|---|---|
| sash panels | `_build_sash`/`_add_glazed_sash` 工厂复用建 fixed(`fixed_*`) + sliding(`sliding_*`/`moving_*`) 两扇(N=2)，或仅 sliding(N=1) | 0004 / model.py:L90-263; 0005 / model.py:L49-229 |
| meeting/muntin bars | `meeting_stile`/`interlock_fin`(N=1) 或 `muntin_{i}` 竖/横条 for-loop(N=2) | 0004 L149-174; dc83a7ca L1928-1929 |
| hardware (for-loop) | `roller_{i}`/`*_glide_*`/`*_guide_*`/`fastener_{i}`/track-rib loop | 0004 L48-69,L176-201; a9564b40 L886-999 |
| internal joints / interface | sash panel 各一个 joint(PRISMATIC/FIXED)；muntin/hardware 随所属 sash 无独立 joint | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| fixed_glazing_topology | enum | separate_fixed_part / baked_into_frame / sash_only_no_fixed | — | choice | 由 deterministic procedural sampler 选择 | Slot A table |
| track_carriage_style | enum | lipped_dual_channel / roller_truck_cylinders / triple_rib_guide / cadquery_hollow_channel | — | choice | 由 sampler 选择 | Slot B table |
| lock_articulation | enum | none_passive_visual / thumbturn_revolute / crescent_cam_revolute / lockout_pin_prismatic | — | choice | conditional：sash_only 时 thumbturn/crescent keeper 改 jamb | Slot C table |
| handle_style | enum | pull_bar / flush_recess / finger_pull / molded_grip_ribs / d_pull_plate | — | choice | 由 sampler 选择 | Slot D table |
| window_orientation | enum | horizontal_X（实证唯一）/ [vertical_double_hung — 无源，reviewer 决定是否纳入] | horizontal_X | choice | **见 §拓扑审计降级说明**；pool 54 条全横滑，竖向双悬无源 | 全部样本 |
| open_direction | enum | left_negative_x / right_positive_x / bidirectional_center | left_negative_x | choice | 决定 PRISMATIC axis 符号与 motion_limits 区间；bidirectional lower=-travel/2 | 0002 axis(-1) / 0003 axis(1) / 645606 双向 L169-182 |
| sash_count | int (count_param) | {1 (sash_only), 2 (sliding+fixed)} | 2 | conditional | 由 fixed_glazing_topology 派生：sash_only⇒1，否则 2 | 全部样本 |
| sliding_sash_count | int | 1（实证恒 1） | 1 | constant | pool 无 2-sliding-sash；固定为 1（>1 无源，不采样） | 全部样本 |
| meeting_muntin_count | int (count_param) | [0, 2]（产品偏 0-1；2 稀有） | 0 | independent | 加权采样小 N 偏多；2 触发 `muntin_{i}` for-loop | dc83a7ca / dd9f8469 |
| grip_rib_count | int (count_param) | [2, 5]（仅 handle_style=molded_grip_ribs） | 3 | conditional | 仅 grip_ribs 时有效；`grip_rib_{i}` for-loop | 7404a1 L93-94 |
| win_width_scale | float | [0.55, 1.30] | 1.0 | independent | clamp；缩放 FRAME_W / OPEN_W / SASH_W（pool 跨 desktop 0.54 到 2.1m） | 各 frame FRAME_W |
| win_height_scale | float | [0.80, 1.30] | 1.0 | independent | clamp；缩放 FRAME_H / SASH_H（含 tall 1.5m 720dbc） | 各 frame FRAME_H |
| frame_depth_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 FRAME_D / 轨道 Y 偏移 | 各 frame FRAME_D |
| sash_open_frac | float | [0.0, 1.0] | 0.0 | independent | 映射到 PRISMATIC q（rest 闭合）；× motion_limits 行程 | 各 motion_limits |
| (—) | constraint | — | — | equation | `sliding_travel = OPEN_W - SASH_W - SASH_CLEAR`（净开口宽派生 PRISMATIC 行程） | 0004 L45-46 / 0005 L41 |
| (—) | constraint | — | — | equation | `SASH_W = (separate/baked) (OPEN_W - MEETING_OVERLAP)/2 ; (sash_only) OPEN_W - 2·SASH_CLEAR` | 0004 / b5bb4681 |
| (—) | constraint | — | — | inequality | `sash glide/roller 必须坐在 front runner 上且 top-guide 被 head lip 捕获`：缩放后保持 runner-Z / head-lip-Z 与 glide-Z 接触带（参 0003 expect_gap 0.017-0.0195） | 0003 L549-593 |
| (—) | constraint | — | — | inequality | `meeting interlock fin 与对扇 meeting stile 在 closed pose 有 seal-break gap`(0.004-0.018) 且 xz 投影 overlap≥0.045 | 0004 L562-576 / 0005 L561-575 |
| (—) | constraint | — | — | inequality | `latch/lock_pin anchor 在可见实体面`：thumbturn origin 在 sash meeting stile 外面，lockout_pin 在 frame jamb 实体；违反则回缩 anchor | 0005 L440-453 |

palette_style 来源（≥3，目标 4-6，全部观测自 curated 源）：

- **silver_aluminum**：FRAME (0.78,0.80,0.82) / SASH (0.66,0.68,0.70) / GLASS (0.71,0.82,0.88,0.28) / HARDWARE_DARK (0.24,0.25,0.27) — 0003 L81-86 / f0621fda。
- **white_vinyl**：FRAME (0.92,0.90,0.84) / GASKET_DARK (0.10,0.11,0.12) / GLASS_BLUE (0.67,0.80,0.87,0.36) — 02c4ce0e (0.92,0.90,0.84) / 0005 / 470474d8 (white powder 0.92,0.94,0.93)。
- **dark_anodized_graphite**：FRAME (0.20,0.22,0.22)/(0.31,0.35,0.33) / EPDM_BLACK (0.09,0.09,0.10) / GLASS_LOWE (0.56,0.66,0.72,0.38) / STAINLESS (0.72,0.74,0.77) — 5424dd87 (0.20,0.22,0.22) / 0002 (0.31,0.35,0.33)。
- **charcoal_black_powder**：FRAME (0.10,0.12,0.11) / SMOKED_GLASS (0.55 alpha) / NYLON_ROLLER (0.14,0.14,0.14) — 7404a1 L? (charcoal powder_coat)。
- **industrial_safety**：FRAME_GRAY (0.28,0.31,0.34)/galvanized (0.23,0.25,0.25) / SAFETY_YELLOW / LOCKOUT_RED / POLYCARBONATE — b5bb4681 / cc24515a。
- **field_service_bronze**：POWDER_BRONZE (0.09,0.075,0.055) / RED_HANDLE / YELLOW_PTFE_SHOE / GLASS — a9564b40。

（wood-brass dd9f8469 (0.55,0.27,0.07)+brass 为低 rating 边角，列为可选第 7 色但不进首版默认。）

连续尺寸采样契约：先采 independent 主尺度（win_width_scale / win_height_scale / frame_depth_scale / sash_open_frac，均匀采样后 clamp）→ 按 equation 派生从属（sliding_travel = 净开口宽；SASH_W 由 OPEN_W 与 topology 推导）→ 用 inequality 把 glide-on-runner / top-guide-captured / meeting-seal-gap / latch-anchor 投影回缩或拒绝重采 → conditional（grip_rib_count 仅 grip_ribs；sash_count 由 topology 派生）在采样前解析。

## Multiplicity / Copy Logic

**一条主轻 multiplicity 轴（sash_count）+ 弱轴（meeting/muntin bar）+ 多条必须 loop 发射的同构 hardware**（per-axis 各做一次加权采样，各自 clamp，各自 sweep 上限）：

### 轴 1 — sash_count（玻璃扇 / 单元数）
- `count_param`：`sash_count` ∈ {1, 2}。
- `N_range`（本轴产品域）：{1 (sash_only_no_fixed), 2 (1 sliding + 1 fixed)}。**pool 实证仅 1 与 2**；无 2-sliding-sash、无 3+ sash（不采样 N>2，无源）。
- sampling domain（权重档）：N=2（sliding + fixed lite，住宅标准）高频；N=1（sash_only，service/safety/calibration）中频。由 fixed_glazing_topology 直接决定（conditional，非自由抽）。
- copied object：glazed panel —`_build_sash`/`_add_glazed_sash` 工厂复用建 fixed 与 sliding 两扇（含 stile/rail/glass-rebate/gasket/interlock-fin）。
- naming：`fixed_lite`/`fixed_sash` vs `sliding_sash`/`moving_sash`。
- placement：沿框宽分两半（separate/baked），meeting stile + interlock fin 在中央；sash_only 时单扇占满开口。
- joint policy：sliding sash 一个 PRISMATIC axis(±1,0,0)；fixed lite 一个 FIXED（separate）或烘焙无 joint（baked）。
- source/gating：母体 0004（separate `_build_sash` ×2）/ 0005（separate `_add_glazed_sash` ×2）/ 0001（baked `_add_glazed_panel`）；均已 PASS loop-emission（工厂复用 + fastener/runner for-loop）。

### 轴 2 — meeting_muntin_count（分隔 / 装饰条，弱轴）
- `count_param`：`meeting_muntin_count` ∈ {0, 1, 2}。
- `N_range`：{0 (无 muntin), 1 (单 meeting/interlock divider), 2 (muntin 十字/竖条)}。pool 几乎全 0-1，仅 dc83a7ca/dd9f8469 有 muntin。
- sampling domain：0-1 高频；2 稀有尾部下调（横滑窗少见 colonial 网格）。
- copied object：`muntin_{i}` 竖/横条 via `for i in range(n)`。
- naming：`muntin_{i}` / `meeting_stile` / `interlock_fin`。
- placement：sash 内框均分；随所属 sash 运动。
- joint policy：随 sash 的 PRISMATIC，无独立 joint。
- source/gating：母体 0004/0005（共享 sash 工厂内发射）；dd9f8469 手写需改 `for i in range(n)`。

### for-loop 发射的 hardware（非独立 multiplicity 轴，但强制 loop 发射）
- rollers/glides/top-guides：`roller_{i}`(7404a1 L114-127) / `*_glide_*`/`*_guide_*`(0004 L176-201, `for side_name` 0005 L180-193)。
- fasteners/screws：`fastener_{i}`/`screw_{i}`(0004 L48-69, 0002 L208-227)。
- track ribs：back/separator/front(f0621fda L646-674, 948397 L72-91)。
- bolt grids / corner plates：`add_bolt`/`_add_bolt_grid`(a9564b40, b5bb4681, cc24515a, 80a9c9)。
- grip ribs（Slot D=grip_ribs）：`grip_rib_{i}`(7404a1 L93-94)。
- index ticks（calibration 边角）：`index_tick_{i}`(cbfa0ab2 L334-342)。

fixed_glazing(A)、track(B)、lock(C)、handle(D) 为固定 named slot，**非复制轴**（不暴露 `*_count`，不循环复制模板级 slot）。`sliding_sash_count` 实证恒 1，作 constant，不采样。

## 拓扑多样性审计

总组合数（slot 笛卡尔，未含连续/multiplicity N）：A × B × C × D = 3 × 4 × 4 × 5 = **240**（即便仅关节承载 A×C = 3×4 = 12 ≥ 10 已单独过闸）。
把 multiplicity 与 open_direction 计入：× sash_count{1,2}(由 A 派生) × open_direction{left,right,bidirectional} × meeting_muntin{0,1,2} 进一步放大。

理由：关节承载的 A(part-tree:3-link/2-link/sash-only)×C(joint:0/+REVOLUTE/+REVOLUTE/+PRISMATIC) 已给 12 个 part/joint 拓扑不同组合，每个改变 link count 与 joint type；叠加 B(轨道 primitive) 后远超 10。1000-seed slot choice tuple distinct 预计 ≥300（每个 (A,B,C,D,sash_count,open_dir) 在 part/joint count + primitive 上是不同 equivalence class），若仅靠 A×B×C×D=240 即足；连续 scale 不计入 distinct。

> **降级说明 — window_orientation**：任务要求 `window_orientation {horizontal, vertical}` 与 `sash_count (2-4)`、`sliding_sash_count (1-2)` 作 joint-bearing slots。但 **54 条 curated pool 实证仅支持 horizontal 横滑、单 sliding sash、sash_count∈{1,2}**：无竖向双悬 ±Z 滑窗、无 2-sliding-sash、无 3+ sash。为不违反「每 candidate 须有真实 model.py 来源」硬约束，本 spec 将 `window_orientation` 实现为以 horizontal 为唯一实证值（vertical 标为无源扩展，留待 reviewer 决定是否手工补 vertical-double-hung 母体；若不补则该轴退化为单值、不计入 topology），`sliding_sash_count` 固定 1，`sash_count` 限 {1,2}。**真正承载多样性的关节轴改由 A(fixed_glazing) + C(lock) 承担**（这两个才是 pool 里真实存在的 part-tree/joint 变化）。此为 reviewer 需确认的关键设计权衡（见审核记录）。

seed_domain_policy：procedural_first（`seed=0` 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 先抽 Slot A fixed_glazing(决定 part tree 与 sash_count)，再抽 B track、C lock、D handle，再抽 open_direction 与 meeting_muntin_count(加权小 N 偏多)，最后采连续 scale 并 clamp/投影回可行域。compatibility matrix 在 `resolve_config` gating（见下）。少量 regression overrides 仅用于已知失败回归（roller-on-runner AABB 脆弱、cadquery segments 退化、lockout_pin 与 sash PRISMATIC 串扰）。random sweep：seeds 0-49 初轮、0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；A×B×C×D + sash_count + open_direction 组合空间足够支撑（240 slot 组合 × N/方向变体）。
Controlled local parameterization：win_width_scale [0.55,1.30]、win_height_scale [0.80,1.30]、frame_depth_scale [0.85,1.20]、sash_open_frac [0,1]、grip_rib_count [2,5](conditional)、meeting_muntin_count [0,2]。全部在 `resolve_config` clamp/派生：sliding_travel = 净开口宽(equation)；SASH_W 由 OPEN_W 与 topology 推导(equation)；glide-on-runner / top-guide-captured / meeting-seal-gap / latch-anchor 用 inequality 投影回缩或拒绝；grip_rib/sash_count conditional 按上游 choice 解析。这些 scale 不改拓扑等价类、不破坏 PRISMATIC 行程接口 / roller-runner 接触 / meeting-seal 间隙 / latch 锚点。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽序 A(派生 sash_count)→B→C→D→open_direction→(meeting_muntin,grip_rib 加权 N)→连续 scale；slot_choices_for_seed 仅记录改变拓扑等价类的 enum 与 N | slot_choices_for_seed matches build choices |
| compatibility matrix | sash_only ⇒ sash_count=1、无 meeting fin、thumbturn/crescent keeper 改 frame jamb；baked ⇒ 无独立 fixed part(2-link)；cadquery_hollow ⇒ segments≤56;lockout_pin PRISMATIC 与 sash PRISMATIC 须不同 axis/origin 不串扰;thumbturn/crescent latch anchor 在可见 meeting stile 实体面;bidirectional open_direction 须 lower<0<upper 且两端不出框 | no floating, collision, axis, max multiplicity, bulky module, optional child failures |
| controlled local variation | win_width/height_scale、frame_depth_scale、sash_open_frac、grip_rib_count、meeting_muntin_count，全部 clamp + 派生 sash/travel/seal，违反 inequality 投影回缩 | proportions vary without breaking interfaces, clearance, support, joint origin, identity |
| regression overrides | none(首版) / 仅 roller-on-runner AABB 脆弱、cadquery segments 退化、lockout_pin 串扰(如出现)按 seed 记录 | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A fixed_glazing_topology | 4 | yes | yes | separate_fixed_part(×2 家族) / baked_into_frame / sash_only（关节承载主槽：part-tree 变化） |
| B track_carriage_style | 4 | yes | yes | lipped_dual_channel / roller_truck / triple_rib / cadquery_hollow |
| C lock_articulation | 4 | yes | yes | none / thumbturn_revolute / crescent_cam_revolute / lockout_pin_prismatic（关节承载主槽：joint 变化） |
| D handle_style | 5 | yes | yes | pull_bar / flush_recess / finger_pull / molded_grip_ribs / d_pull_plate |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D enum + open_direction + 改变拓扑的 sash_count/meeting_muntin N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（`seed=0` 不特殊）
- compatibility matrix / gating prevents illegal module combinations（sash_only↔sash_count1↔keeper-on-jamb；baked↔2-link；cadquery↔segments≤56；lockout_pin↔不串扰；latch↔可见 meeting stile anchor）
- optional regression overrides are sparse and justified（仅 roller-AABB / cadquery-segments / lockout-串扰 已知风险）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (win_width/height_scale, frame_depth_scale, sash_open_frac, grip_rib_count, meeting_muntin_count) are clamped and cannot break PRISMATIC 行程 / roller-runner 接触 / top-guide capture / meeting-seal gap / latch 锚点 / category identity
- cross-part scale dependencies (sliding_travel=净开口宽 equation；SASH_W 由 OPEN_W 派生 equation；glide-on-runner / seal-gap / latch-anchor inequality；grip_rib/sash_count conditional) resolved in `resolve_config`, not in builder
- critical InterfaceSpec / MatingContract points exist：sash-glide-on-front-runner、top-guide-captured-under-head-lip、fixed-glide-on-rear-runner(separate)、meeting-interlock-fin-vs-fixed-stile(seal break)、latch-escutcheon-on-meeting-stile / lockout-pin-in-keeper
- key joints have expected type/axis/range：sliding_sash PRISMATIC axis(±1,0,0) lower/upper=净开口宽（bidirectional ±travel/2）；fixed_lite FIXED(separate)；thumbturn/crescent latch REVOLUTE axis(0,1,0)；lockout_pin PRISMATIC axis(0,0,1)
- copied objects follow naming and placement policy：`fixed_*`/`sliding_*`/`muntin_{i}`/`roller_{i}`/`*_glide_*`/`grip_rib_{i}`/`fastener_{i}`
- sliding sash rest pose(q=0) 闭合靠 jamb / meeting stile 对接；open pose 沿 X 平移叠在 fixed lite 后（或全开），glide 始终坐 runner、top-guide 始终被 head lip 捕获、Y/Z 不漂移（参 0003 L671-685、0005 L644-652）
- sliding_sash_count 恒 1（不采样 >1，无源）

## Reject cases

- 把铰链外摆（REVOLUTE 主开启 casement/awning/hopper）作 sash 机构 — 属 `window` 小类，必拒；本 slug 主开启恒 PRISMATIC 横滑。
- 竖向双悬 ±Z 滑窗或 2-sliding-sash / 3+ sash — pool 无源，首版不采样（除非 reviewer 手补母体）。
- sliding sash 在 q=0 不闭合、不靠 jamb / meeting stile，或 open pose 飘出框 / glide 脱离 runner / top-guide 脱出 head lip / Y-Z 漂移。
- roller/glide 不坐在 front runner 上（悬空）、fixed glide 不坐 rear runner、meeting interlock fin 与对扇无 seal-break gap（穿模或脱节）。
- glass / fixed-lite / muntin 漂浮（未 rebate 嵌入 stile/rail lip、未 allow_overlap captured）。
- thumbturn/crescent latch anchor 在不可见框边薄面 → joint-origin 漂浮；lockout_pin 竖滑 PRISMATIC 与 sash 横滑 PRISMATIC 串扰（同 origin/axis 误设）。
- cadquery_hollow frame/sash 在 segments 过高时布尔退化（"Profile area must be non-zero"，参 MEMORY roller-skate ≤56）。
- sliding_travel 超净开口宽（sash 开到出框）或 < 0（无法开启），未 clamp / 派生。
- frame 不站立（sill 不在 z≈0）、深度 > 高度（躺倒）、sash 比开口大（塞不进）。
- 把 calibration 旋钮 / 维修盖 / 安全防护栅等主题外边角强行进首版 seed domain（收敛风险高，应仅作 reviewer 可选扩展）。

## 与相邻类别的边界

- 不该混入：**Window（casement / awning / hopper / fixed picture，独立小类）** — 那些以铰链 REVOLUTE 外摆 / 顶底铰 / 竖向升降为身份；本 slug Slot A 机构恒 PRISMATIC 横滑，不含铰链外开。
- 不该混入：**Sliding door** — 滑门是落地（sill 至地面）供人通行的整扇大滑板，无 glazed-sash-in-frame 的 sill-above-floor 立面 + meeting-stile / fixed-lite 采光语义；本小类是窗台之上的采光横滑窗。
- 不该混入：**Sibling slug `sliding_window`（qwen fork pool 建的并行模板）** — identity 重叠（都横滑 PRISMATIC），但本 slug 建自 54 条 curated DATASET 池、不同来源；两者作并行/替代模板共存，不互相覆盖。
- 不该混入：**Curtain / facade element（幕墙）** — 大面积无可动扇的固定玻璃格栅；本小类必须有一个 category-defining 横滑 PRISMATIC sash，尺度为单窗。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；54 条 curated pool（48 条 rating≥5）跨分簇完整覆盖，每候选已解析真实 model.py:Lx-Ly。**关键待审权衡**：任务要求的 joint-bearing slots {window_orientation horizontal/vertical, sash_count 2-4, sliding_sash_count 1-2} 在 pool 中**实证仅支持 horizontal 横滑、sash_count∈{1,2}、sliding_sash_count=1**（无竖向双悬、无 2-sliding-sash、无 3+ sash 源）。本 spec 据实将这些轴退化/限域，并把真实关节多样性改由 A(fixed_glazing 拓扑) + C(lock 关节) 承担。请 reviewer 确认：(1) 是否接受 horizontal-only + sash_count{1,2} 的实证降级，或要求手补 vertical-double-hung / 2-sliding-sash 母体；(2) field-service 维修盖 REVOLUTE / calibration 旋钮 CONTINUOUS / safety 防护栅是否纳入首版（当前列为 reviewer 可选扩展，主题外）。等待审核后再进入 TEMPLATE_AFTER_REVIEW。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/D/multiplicity | separate_fixed_part / lipped_dual_channel / pull_bar | rec_sliding_window_0004 | L48-469 | 基线 2-part(fixed+sliding) + 共享 `_build_sash` 工厂 + fastener/runner/corner for-loop + PRISMATIC axis(1,0,0) + interlock fin |
| S2 | A/C | separate_fixed_part(latch) / thumbturn_revolute | rec_sliding_window_0005 | L49-453 | separate fixed_sash + moving_sash + 独立 `latch` part REVOLUTE axis(0,1,0)；`_add_glazed_sash(meeting_side)` 工厂；scale-assert |
| S3 | A/B/D | baked_into_frame / lipped_dual_channel(双轨) / flush+pull | rec_sliding_window_0001 | L51-358 | 烘焙 fixed lite + `_add_glazed_panel` + 双轨 track_base/head_guide + roller_cover；PRISMATIC 闭合靠右 jamb / 开叠 fixed 后 |
| S4 | B/D | roller_truck_cylinders / molded_grip_ribs | rec_sliding_window_7404a1 | L37-127 | nylon `roller_{i}` Cylinder on stainless track + MotionProperties damping + `grip_rib_{i}` for-loop；charcoal palette |
| S5 | A/B/D | baked / roller-truck(Cylinder) / pull-bar | rec_sliding_window_0002 | L48-382 | rugged industrial baked fixed + `_add_screw_head` + roller Cylinder + meeting_post；dark graphite palette |
| S6 | B/D | baked / roller-truck / pull_plate | rec_sliding_window_0003 | L51-505 | premium baked fixed + front/rear 双轨 roller_rail + roller Cylinder + interlock_fin + pull_plate；silver palette |
| S7 | C | crescent_cam_revolute | rec_sliding_window_43f22f89 | L203-256 | crescent/quarter-turn `latch_pivot` REVOLUTE axis(0,1,0) + jamb keeper_plate + finger_pull |
| S8 | A/C | sash_only / lockout_pin_prismatic | rec_sliding_window_b5bb4681 | sash-only + `frame_to_lock_pin` PRISMATIC axis(0,0,1) | 工业安全 lift-out 锁定销 + guard 防护栅 loop + 无 fixed lite；galvanized+yellow+red palette |
| S9 | B/multiplicity | triple_rib_guide / track-rib loop | rec_sliding_window_f0621fda | L646-674 | back/separator/front 三轨肋 for-loop + separate fixed_panel；aluminum palette |
| S10 | B | cadquery_hollow_channel(bidirectional) | rec_sliding_window_645606 | L56-182 | CadQuery boolean frame + drain-slot loop + 双向中停 PRISMATIC lower=-travel/2；frosted glass |
| S11 | C/D | thumbturn_revolute / flush_recess | rec_sliding_window_02310a01 | L234-272 | `flush_pull_recess`+`pull_lip` + `sash_to_latch` REVOLUTE 拇指扳手 + bump stops；graphite |
| S12 | C/D | (field-service ref) d_pull_plate + REVOLUTE 维修盖 | rec_sliding_window_a9564b40 | L886-999 | REVOLUTE latch + REVOLUTE access cover + bolt/hinge/shoe for-loop；bronze palette（维修盖列 reviewer 可选扩展） |

## 模板实现备注（可选）

- A=separate_fixed_part 与 A=baked_into_frame 共享同一 glazed-panel helper（`_build_sash`/`_add_glazed_sash`/`_add_glazed_panel` 风格，参数 `meeting_side`/`moving`）；fixed 与 sliding 仅 meeting-side 与 joint 不同。首版可直接复用 0004/0005 工厂。
- captured / mount overlap 须 element-scoped allow_overlap：glass↔stile/rail(rebate)、roller/glide↔runner(承载接触)、top-guide↔head-lip(capture)、interlock-fin↔meeting-stile、latch-escutcheon↔sash-meeting-stile、lockout-pin↔keeper。复合时对每个 panel / `roller_{i}` 重复声明。
- roller-on-runner 接触断言：用 `expect_contact`/`expect_gap`（参 0003 L549-593、0004 L504-545、0005 L605-627），**不用 AABB 自转**（圆柱轮轴对称，参 MEMORY knob-spin 教训）。
- cadquery_hollow（Slot B）须 segments≤56 防布尔退化（参 MEMORY roller-skate "Profile area must be non-zero"）。
- lockout_pin PRISMATIC（Slot C，axis z）与 sliding_sash PRISMATIC（axis x）两条棱柱副须 origin/axis 分离、motion_limits 独立，sweep 各设上限不串扰。
- open_direction=bidirectional（645606）须 lower=-travel/2, upper=+travel/2 且两端不出框；其余 open_direction 单向 0..±travel。
- field-service REVOLUTE 维修盖（a9564b40/dc83a7ca）、calibration CONTINUOUS/REVOLUTE 旋钮（cbfa0ab2）、safety guard 防护栅（b5bb4681/cc24515a）作为 reviewer 可选扩展模块，首版不进 seed domain（主题外 + 收敛风险）。
