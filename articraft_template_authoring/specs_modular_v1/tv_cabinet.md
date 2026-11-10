# tv_cabinet — Modular Spec

> 来源小类：`picture/0611/TV_cabinet`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/0611__TV_cabinet.md`。
> **"TV cabinet" 在此 = 立式/矮式电视机柜家具**：一只低矮宽体箱式 carcass（painted / walnut / oak / cherry laminate wood），坐在腿/踢脚/悬挂支架上，正面呈 1..N 个可开合的储物机构（侧铰门 / 下翻 flap 门 / bifold 双叶折门 / tambour 卷帘门 / 抽屉行 / 开放格）。**不是**电视机本身、不是普通桌子、不是开放式陈列架（见 §边界）。
>
> **同步状态**：本 spec 引用的 5 星样本（7 parent + 11 fork 变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计。

## 元信息
| 项 | 值 |
|---|---|
| slug | `tv_cabinet` |
| template path | `agent/templates/tv_cabinet.py` |
| test path (optional) | 不写，sweep 为唯一验收 |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named root `carcass` + 三根槽位：`body_form` (③) / `closure` (①/②) / `support` (①) + 一根 multiplicity `storage_count` (①) 由 closure 派生）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 18（7 parent + 11 fork 变体，all `rating=5`）|
| read_count | 18（**parent 7 个全部读完整 `model.py`**；variant 11 个每个读结构 / 关键 helper / joint 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方槽位表 |

**阅读要点**（源类别身份不变，都是低宽矮 carcass + 前部一或多个可开合机构 + 底部支撑）：

- **P1 warm painted wood, 6 抽 + 2 门**（`rec_picturex_0611__tv_cabinet__007__png_...`，562 行）：`carcass` root，前面朝 +Y，宽沿 X。painted wood carcass（back_panel/bottom_slab/side_panels/dividers/top_slab from `_top_slab` cadquery + `_bun_foot_geometry` LatheGeometry × 4 + bail handle mesh）。正面 2×3 抽屉网格 `for bank_idx, x in enumerate(DRAWER_CENTERS_X): for row_idx, z in enumerate(DRAWER_CENTERS_Z)` 循环发射 `drawer_{i}` PRISMATIC（axis +Y, 0..0.280 m, L329-343）与中央 2 门 `carcass_to_door_{i}` REVOLUTE（axis ±Z, 0..1.75 rad, L393-407）。
- **P2 walnut 双门 tall**（`rec_picturex_0611__tv_cabinet__001__png_...`，437 行）：`carcass` root，painted / laminate double-hinged 门。`_rounded_box` + `_tapered_foot` cadquery helpers；`_build_door_visuals` L62-190 每门发射 hinge_stile/meeting_stile/lower_rail/upper_rail/center_field/plank_joint/hinge_leaf/hinge_barrel/pull_stem/round_pull；`carcass_to_door_{0,1}` REVOLUTE 立轴 Z 双向 outward hinge（0..1.72 rad, L297-318）。
- **P3 oak 4 门 flush slab**（`rec_picturex_0611__tv_cabinet__002__png_...`，457 行）：`carcass` root，`DOOR_COUNT=4` 铰门等距 alternating `door_directions=(1,-1,1,-1)`，`_add_door_grain` L39-62 + `_add_concealed_hinges` L65-89 hinge cup + arm；4×REVOLUTE `carcass_to_door_{i}` 立轴（0..1.65 rad, L285-303）。
- **P4 oak 双门+双抽 mid**（`rec_picturex_0611__tv_cabinet__003__png_...`，633 行）：`carcass` root，`_add_drawer` L98-189 hollow tray + `_add_pull` bar + `_add_front_grain`，`_tapered_leg` mesh_from_cadquery loft leg。2 抽屉 PRISMATIC axis -Y（0..0.280 m, L173-188）+ 2 门 REVOLUTE 立轴 Z（0..1.745 rad, L259-274）。
- **P5 walnut 双门+4 抽 tall**（`rec_picturex_0611__tv_cabinet__004__png_...`，616 行）：`carcass` root，plinth+toe_kick base，`_add_door` L77-149 + `_add_drawer` L152-234；2 门 REVOLUTE + 4 抽 PRISMATIC。
- **P6 walnut 低宽 4 push-flap**（`rec_picturex_0611__tv_cabinet__005__png_...`，591 行）：`cabinet` root，低宽 console with matte_black top slab + open shelf + `DOOR_COUNT=4` push-to-open flap doors, hinge axis (1,0,0), `_rounded_box_mesh` + `_hinge_tube_mesh` cadquery, `cabinet_to_door_{i}` REVOLUTE X 轴（0..1.45 rad, L334-351）。
- **P7 cherry hutch**（`rec_picturex_0611__tv_cabinet__006__png_...`，462 行）：`cabinet` root，有 middle_deck + hutch stage 上部 2 抽 hutch, glass doors 侧铰门, 中央 3 lower drawers, 2 hutch drawers。
- **variant forks**（body_form_corner, body_form_bowed_front, closure_paired_bifold_doors, closure_drop_front_media_flap, closure_tambour, storage_count_3_drawers/3_doors/3_open_cubbies, support_floating_wall_mount, support_solid_plinth, support_powder_coated_sled_base）— 每个 fork 保留 anchor 的 carcass root + closure/support 变化，joint 拓扑与代码 helper 全部延续 anchor。

Root 都是单一 carcass shell、正前方 (+Y or -Y 方向) 摆放 movable fronts、下部或后部支撑；part 树拓扑同构（root carcass → 复制 N 个 front child，各自独立 joint），只是 closure/form/support 三根轴换法。

## 核心身份

矮而宽的 TV cabinet：宽 1.0–2.4 m、高 0.4–1.0 m、深 0.35–0.55 m 的 laminated/painted wood carcass。前面必含至少一个 non-FIXED 活动储物机构（门/抽屉/flap/bifold/tambour），下部有可见支撑接口（腿/踢脚/plinth/sled/wall-mount）。作为"电视柜"是**主观身份**——TV 本身不建；用途就是给电视/媒体设备提供放置台面与储物。

**排除**：普通桌/写字台（无 front closures 或抽屉）、开放式陈列架（无 door、无实体 carcass）、床头柜（footprint 太小/高度太高）、书柜（前面全部开放/敞开）、CRT 电视机本身。

## 槽位 + 候选模块表

### Slot A：body_form（③ Primary Form Family，登记进 slot_choices）

TV cabinet 是 form-dominated 类别（视觉 identity 主导轴）。每个 candidate 保持同一 part tree、同一 primitive family (Box + cadquery rounded / grain visuals)、同一 interface (前面 mounts closures, 下部 mounts support)，只改变主体 planar boundary 或 volumetric envelope。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rectangular_low_wide` | forked_anchor | `rec_picturex_0611__tv_cabinet__007__png_...` (P1) | L132-256 (carcass build) | eligible if compatible | Planar Boundary Form: 直方 rectangular envelope，宽:高:深 ≈ 3.4:1.6:1；扁平 top slab，正矩形正立面 |
| `rectangular_tall` | forked_anchor | `rec_picturex_0611__tv_cabinet__001__png_...` (P2) | L214-274 (carcass build) | eligible if compatible | Planar Boundary Form: 直方但比例更高（宽:高:深 ≈ 1.2:1:0.5），近方形正立面 |
| `low_wide_console` | forked_anchor | `rec_picturex_0611__tv_cabinet__005__png_...` (P6) | L127-253 | eligible if compatible | Volumetric Envelope Form: 极扁 (2.4×0.46 m, ratio 5:1)，overhanging thin top slab + open shelf；正立面窄条形 |
| `bowed_front` | forked_anchor | `rec_0611_tv_cabinet_var_body_form_bowed_front` | derived _bowed_front_slab + _bow_offset | eligible if compatible | Macro Surface Construction: 正面沿 X 中央外凸 bulged front reveal，front visual has slight bow 曲率 (bow=8-12mm) |
| `corner_wedge` | forked_anchor | `rec_0611_tv_cabinet_var_body_form_corner` | carcass Y+X 截去后角 | eligible if compatible | Planar Boundary Form: 深度方向后角削去 45°切角 (chamfer_depth ≈ 0.10 m)，plan view 变为不规则 pentagon 便于放置房间角落 |
| `stepped_hutch` | forked_anchor | `rec_picturex_0611__tv_cabinet__006__png_...` (P7) | L62-140 | eligible if compatible | Volumetric Envelope Form: 中央有二阶 stepped hutch，正立面读法：low_wide base + 上方缩窄 hutch upper stage |

每个 form_subtype 都保持相同 slot graph（front mounts closure, bottom mounts support）；只影响 carcass shell 几何生成。

### Slot B：closure（①/② 主运动机构，登记进 slot_choices）

正面开合机构。每个 candidate 有不同 part 数 / joint 类型 / 轴。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `side_hinged_doors` | forked_anchor | `rec_picturex_0611__tv_cabinet__002__png_...` (P3, DOOR_COUNT=4 alternating) | L237-303 | eligible if compatible | N 个立轴 REVOLUTE 侧铰门（`carcass_to_door_{i}`，axis ±Z, 0..1.7 rad），对称 hinge sides；N ∈ {2, 3, 4}，涵盖 P2/P3/P5/`storage_count_3_doors` |
| `drop_front_flap` | forked_anchor | `rec_0611_tv_cabinet_var_closure_drop_front_media_flap` | derived from P2 doors, axis 改 X | eligible if compatible | 2 个下翻卧轴 REVOLUTE 门（axis ±X, 底铰 0..1.45 rad），门顶向前下方翻转露出 media 舱 |
| `push_flap_row` | forked_anchor | `rec_picturex_0611__tv_cabinet__005__png_...` (P6) | L255-351 (door loop) | eligible if compatible | N 个 X 轴卧轴 REVOLUTE 下翻 push-to-open flap（`cabinet_to_door_{i}`, axis (1,0,0), 0..1.45 rad），无 pull handles；N ∈ {3, 4} |
| `bifold_doors` | forked_anchor | `rec_0611_tv_cabinet_var_closure_paired_bifold_doors` | outer + inner leaf helper | eligible if compatible | 2 对 4 叶 bifold：outer leaf carcass hinged (REVOLUTE ±Z) + inner leaf outer-hinged (REVOLUTE ±Z)，共 4 门 8 joints |
| `drawer_bank` | forked_anchor | `rec_0611_tv_cabinet_var_storage_count_3_drawers` + P1 6 抽 grid | L98-189 (_add_drawer) | eligible if compatible | N 个水平堆叠 PRISMATIC 抽屉（`carcass_to_drawer_{i}`, axis ±Y, 0..0.28 m），N ∈ {3, 4, 6} |
| `open_cubbies` | forked_anchor | `rec_0611_tv_cabinet_var_storage_count_3_open_cubbies` | 静态 cubby dividers, no joints | eligible if compatible | N 个开放 cubby 隔断（**无 joint**，纯 carcass visuals）+ 至少 1 个额外 side door / drawer 保 identity；N ∈ {3, 4} |

`open_cubbies` 单独作为无 joint 变体时需额外配 1 door，避免整个 template 无非-FIXED joint（违反 Rule 5 覆盖）。

### Slot C：support（① 支撑接口，登记进 slot_choices）

底部/后部支撑层。除 `wall_mount` 外均为 carcass 子 visual (fixed)。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bun_feet` | forked_anchor | `rec_picturex_0611__tv_cabinet__007__png_...` (P1) | L60-76 (_bun_foot_geometry) + L241-255 | eligible if compatible | 4 条 turned bun feet (LatheGeometry Lathe profile) + 直筒 foot_neck cylinder |
| `tapered_legs` | forked_anchor | `rec_picturex_0611__tv_cabinet__003__png_...` (P4) | L47-56 (_tapered_leg) + L361-375 | eligible if compatible | 4 条 tapered square legs（cadquery loft 上宽下窄, 高 0.10-0.16 m） |
| `splayed_wood_legs` | forked_anchor | `rec_picturex_0611__tv_cabinet__002__png_...` (P3) | L195-214 (legs loop) | eligible if compatible | 4 条 solid oak 稍外撇 legs (Box + rpy tilt ≈ 0.065 rad), 直方截面 |
| `solid_plinth` | forked_anchor | `rec_0611_tv_cabinet_var_support_solid_plinth` + `rec_picturex_0611__tv_cabinet__005__png_...` | recessed_plinth pattern | eligible if compatible | 单块 recessed base plinth Box（比 carcass 深浅收 20mm）+ 底面直接接地 |
| `powder_coated_sled` | forked_anchor | `rec_0611_tv_cabinet_var_support_powder_coated_sled_base` | sled_frame_0/1 | eligible if compatible | 2 条黑色 U 形 powder-coated steel sled 侧框（Box + Cylinder 连接），底面着地 |
| `wall_mount` | forked_anchor | `rec_0611_tv_cabinet_var_support_floating_wall_mount` | wall_rail + cleat_plate_i | eligible if compatible | 后部 French-cleat 铁架（wall_rail + wall_lip + 3 cleat_plates）+ bottom_closure；carcass 悬空，不带腿；离地 0.30-0.40 m |

Compatibility matrix：`wall_mount` **不兼容** heavy `stepped_hutch`（太重悬挂不合理，spec 层排除，采样降级为 `low_wide_console`）；`powder_coated_sled` **不兼容** `wall_mount`（互斥支撑）；`corner_wedge` **不兼容** `wall_mount` + `powder_coated_sled`（角柜通常落地腿）。

## 槽位图（slot graph）

pattern: `mixed` (parallel_children + multiplicity)

```
carcass (root, body_form defines shell geometry)
  ├── downstream face: front (±Y plane) → closure module (N × PRISMATIC or REVOLUTE joints, parented to carcass)
  └── downstream face: bottom (z=0 plane) → support module (FIXED visuals attached to carcass, OR wall_mount visuals at back plane)
```

- carcass 为 root part。所有 closure 子件（doors / drawers / flaps / bifold leaves）**直接 parent 到 carcass**（parallel_children pattern）。
- support 除 wall_mount 均为 carcass visual（fixed），不 emit part。
- closure 内可能有二级链：`bifold_doors` 中的 inner leaf parent 到 outer leaf（linear_chain sub-graph），共两级 REVOLUTE。
- 每个跨 slot connection：
  - carcass → closure_child：REVOLUTE 立轴 Z（side_hinged, bifold outer）/ REVOLUTE 卧轴 X（drop_front, push_flap）/ PRISMATIC axis ±Y（drawer_bank）
  - bifold outer_leaf → inner_leaf：REVOLUTE 立轴 Z（parent-relative）
- `open_cubbies` 无 joint 时 template 强制附加至少 1 个 side door（用于保 Rule 5 覆盖）。

## 每槽位 Module Emits / Interfaces

### Slot A / module rectangular_low_wide
| emits | 描述 | 来源 |
|---|---|---|
| parts | carcass root only | P1 L132 (`model.part("carcass"...)`) |
| internal joints | none | — |
| visual anchors | back_panel + bottom_slab + side_panels + dividers + top_slab (cadquery) + bun_feet 是 support 而非 body_form | P1 L138-249 |
| upstream interface | root (no parent) | P1 |
| downstream interface (front) | y=−carcass_depth/2 plane, face_extents_uv=(W, H_zone) | P1 L336 (door hinge origin `Origin(xyz=(x, HINGE_Y, DOOR_CENTER_Z))`) |
| downstream interface (bottom) | z=0 plane | P1 L248 |

### Slot A / module rectangular_tall
| emits | 描述 | 来源 |
|---|---|---|
| parts | carcass root | P2 L214 |
| visual anchors | side_panel_0/1 + back_panel + bottom_deck + shelf_0/1 + top_slab + top_lip + front_post + front_header + front_sill + base_plinth (all Box) | P2 L214-232 |
| downstream front | same as A/rectangular_low_wide, taller z zone | P2 L302-315 |

### Slot A / module low_wide_console
| emits | parts | 来源 |
|---|---|---|
| parts | cabinet root | P6 L127 |
| visual anchors | matte_black `top_slab` (`_rounded_box_mesh` + fillet edges "|Z") + side_cheeks + base_panel + back_panel + shelf_slab + recessed_plinth | P6 L136-191 |
| downstream front | y=-carcass_depth/2 plane, low H_zone (< 0.25 m), N seams | P6 L338-351 |

### Slot A / module bowed_front
| emits | parts | 来源 |
|---|---|---|
| parts | carcass root with bowed front slab | `rec_0611_tv_cabinet_var_body_form_bowed_front` |
| visual anchors | 同 rectangular_low_wide 但前面 face 是 `_bowed_front_slab` cadquery loft (bow=8-12mm) | fork _bowed_front_slab |
| downstream front | y=front_plane(x) offset by _bow_offset(x_world) | fork _bow_offset |

### Slot A / module corner_wedge
| emits | parts | 来源 |
|---|---|---|
| parts | carcass root with 45° back corner chamfer | `rec_0611_tv_cabinet_var_body_form_corner` |
| visual anchors | carcass body with back-corner Box removed (chamfer_depth 0.10 m) via extra chamfer_cut visuals | fork corner geometry |
| downstream front | 保持正面 y-plane，depth 从中央到边缘线性变化 | fork |

### Slot A / module stepped_hutch
| emits | parts | 来源 |
|---|---|---|
| parts | cabinet root with base stage + hutch stage | P7 L62-140 |
| visual anchors | bottom_plinth + front_apron + side_panels + lower_dividers + shelves + middle_deck + hutch_sides + hutch_center + upper_top | P7 |
| downstream front | y=-carcass_depth/2 plane，覆盖 lower stage 与 hutch stage 两个 z zone | P7 |

### Slot B / module side_hinged_doors (N × REVOLUTE Z)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}` for i in range(N) | P3 L242, P1 L348, P2 L276, P4 L206 |
| internal joints | none | — |
| upstream interface | connects to carcass front face at hinge_x, y=front_plane, z=door_zc | P3 L285-303 |
| joint type | REVOLUTE axis=(0,0,±1), 0..1.65-1.75 rad | P3 L293 |
| visual anchors | door_panel (Box or `_rounded_box`) + hinge_barrel + hinge_leaf + pull/knob + optional grain | P2 L83-190, P3 L249-282 |

### Slot B / module drop_front_flap (2 × REVOLUTE X)
| emits | parts | 来源 |
|---|---|---|
| parts | `door_0`, `door_1` (drop-front media flaps) | `rec_0611_tv_cabinet_var_closure_drop_front_media_flap` |
| joint type | REVOLUTE axis=(±1,0,0)，底铰 z_bottom, 0..1.45 rad | fork L297-318 (adapted from P2 hinge) |
| visual anchors | door_panel Box + hinge_barrel + pull | fork |

### Slot B / module push_flap_row (N × REVOLUTE X)
| emits | parts | 来源 |
|---|---|---|
| parts | `door_{i}` for i in range(N) | P6 L296-332 |
| joint type | REVOLUTE axis=(1,0,0)，底铰 hinge_z ≈ 0.06, 0..1.45 rad | P6 L334-351 |
| visual anchors | rounded panel + hinge_barrel + hinge_strap + no pull handles | P6 L303-332 |

### Slot B / module bifold_doors (2 pairs × 2 REVOLUTE Z levels)
| emits | parts | 来源 |
|---|---|---|
| parts | `left_outer_door`, `left_inner_door`, `right_outer_door`, `right_inner_door` | `rec_0611_tv_cabinet_var_closure_paired_bifold_doors` |
| joint type | outer: REVOLUTE ±Z on carcass, inner: REVOLUTE ±Z on outer leaf | fork |
| visual anchors | 4 leaves 各带 panel + hinge_barrel + narrow width | fork |

### Slot B / module drawer_bank (N × PRISMATIC Y)
| emits | parts | 来源 |
|---|---|---|
| parts | `drawer_{i}` for i in range(N) | `rec_0611_tv_cabinet_var_storage_count_3_drawers`, P4 L98-189, P1 L261 |
| joint type | PRISMATIC axis=(0,±1,0), 0..0.28 m | P4 L173-188 |
| visual anchors | front_panel (`_rounded_box` mesh) + drawer_bottom + drawer_sides + drawer_back + pull bar | P4 L110-171 |

### Slot B / module open_cubbies (N cubby dividers + 1 fixed guard door)
| emits | parts | 来源 |
|---|---|---|
| parts | `guard_door` (single side door 保 Rule 5 compliance) + N-1 fixed cubby dividers as carcass visuals | `rec_0611_tv_cabinet_var_storage_count_3_open_cubbies` |
| joint type | REVOLUTE Z (single guard door) | fork |
| visual anchors | dividers + optional grain + guard_door on far end | fork |

### Slot C / module bun_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (all carcass visuals) | — |
| visual anchors | 4× `bun_foot_{i}` mesh_from_geometry(LatheGeometry([...])) + 4× `foot_neck_{i}` Cylinder | P1 L129, L241-255 |

### Slot C / module tapered_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visual anchors | 4× `leg_{i}` mesh_from_cadquery loft (upper 0.046² → lower 0.030²) | P4 L47-56, L361-375 |

### Slot C / module splayed_wood_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visual anchors | 4× `leg_{i}` Box with slight rpy tilt (±0.065, ∓0.090, 0) | P3 L195-214 |

### Slot C / module solid_plinth
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visual anchors | 单块 `plinth` Box (recessed) + optional `toe_kick` Box | `rec_0611_tv_cabinet_var_support_solid_plinth` + P6 L186-191 |

### Slot C / module powder_coated_sled
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visual anchors | 2× `sled_frame_{i}` U-shape (Box + Cylinder joints) black hardware material | `rec_0611_tv_cabinet_var_support_powder_coated_sled_base` |

### Slot C / module wall_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visual anchors | `wall_rail` Box + `wall_lip` Box + 3× `cleat_plate_{i}` Box + fastener Cylinders on back plane | `rec_0611_tv_cabinet_var_support_floating_wall_mount` L70-100 |
| grounding | carcass floats above z=0（下缘 z_floor 0.30-0.40 m），rail 后接 y=+carcass_depth/2 wall | fork |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | `rectangular_low_wide` / `rectangular_tall` / `low_wide_console` / `bowed_front` / `corner_wedge` / `stepped_hutch` | `rectangular_low_wide` | choice | deterministic sampler weighted [.28,.16,.20,.13,.10,.13] | Slot A |
| `closure` | enum | `side_hinged_doors` / `drop_front_flap` / `push_flap_row` / `bifold_doors` / `drawer_bank` / `open_cubbies` | `side_hinged_doors` | choice | sampler weighted [.30,.14,.14,.10,.22,.10] | Slot B |
| `support` | enum | `bun_feet` / `tapered_legs` / `splayed_wood_legs` / `solid_plinth` / `powder_coated_sled` / `wall_mount` | `tapered_legs` | choice | sampler + compatibility gates | Slot C |
| `palette_style` | enum | `warm_greige` / `walnut_dark` / `light_oak` / `cherry_wood` / `matte_black_wood` / `painted_white` | `light_oak` | choice | independent | palettes from P1..P7 |
| `storage_count` | int | 2..6 (weighted [.25,.30,.15,.20,.10]) | 3 | conditional | 仅在 `closure` in {side_hinged_doors, push_flap_row, drawer_bank, open_cubbies} 生效；bifold_doors 固定 4, drop_front_flap 固定 2 | `storage_count_3_*` variants + P1 6 抽 |
| `carcass_width` | float | [1.0, 2.4] m | 1.55 | conditional | wall_mount → [1.0, 1.5]；low_wide_console → [1.8, 2.4]；stepped_hutch → [1.2, 1.6] | parent widths |
| `carcass_depth` | float | [0.36, 0.52] m | 0.44 | independent | uniform, clamp | parent depths |
| `carcass_height` | float | [0.40, 1.05] m | 0.75 | conditional | rectangular_tall → [0.80, 1.05]；low_wide_console → [0.40, 0.55]；stepped_hutch → [0.90, 1.05]；其他 → [0.60, 0.85] | parent heights |
| `door_open_scale` | float | [0.70, 1.0] | 0.90 | independent | scales the upper joint limit | motion limits |
| `drawer_travel_scale` | float | [0.70, 1.0] | 0.90 | independent | scales drawer travel | P1/P4 drawer limits |
| `body_form ≠ wall_mount×stepped_hutch` | constraint | — | — | inequality | if `body_form=='stepped_hutch' and support=='wall_mount'` → support fallback to `tapered_legs` | 兼容性 |
| `body_form ≠ wall_mount×corner_wedge` | constraint | — | — | inequality | if `body_form=='corner_wedge' and support=='wall_mount'` → support fallback to `tapered_legs` | 兼容性 |
| `body_form ≠ powder_coated_sled×corner_wedge` | constraint | — | — | inequality | if `body_form=='corner_wedge' and support=='powder_coated_sled'` → support fallback to `splayed_wood_legs` | 兼容性 |

### 7.5 编译预算 / compile budget（必填）

- 目标 ≤ 20 s / seed（简单 Box + cadquery filleted 面 + LatheGeometry lathe 腿）。
- 分档 tessellation：
  - LatheGeometry bun_foot：`segments=16`（不用源 36）
  - `_rounded_box_mesh` fillet：`tolerance=0.0015, angular_tolerance=0.12`（源 0.0008 需降精度）
  - `_tapered_leg` mesh：`tolerance=0.0015, angular_tolerance=0.15`
  - 4 条同型腿/N 相同抽屉/N 相同门共用同一 `mesh_from_cadquery` 或 `mesh_from_geometry`。
- 依据：库内 mesh_from_cadquery 5-15s / mesh，本类只 3-6 个 mesh 家族，其余 Box → 预算内。
- 超预算时先降 fillet tolerance + LatheGeometry segments，再考虑砍装饰。

## Multiplicity / Copy Logic

**一根 multiplicity 轴：`storage_count`**。

- `count_param`: `storage_count`
- `N_range`: [2, 6]（inclusive）
- sampling domain：weighted `[2→.25, 3→.30, 4→.15, 5→.20, 6→.10]`（小 N 高频；6 抽 grid P1 稀有覆盖 tail）
- 生效条件：
  - `closure == side_hinged_doors` → N ∈ {2, 3, 4}（超出 clamp）
  - `closure == push_flap_row` → N ∈ {3, 4}
  - `closure == drawer_bank` → N ∈ {3, 4, 6}（6 触发 2×3 grid, sourced from P1）
  - `closure == open_cubbies` → N ∈ {3, 4}
  - `closure == bifold_doors` → 固定 4 (2×2 leaves)
  - `closure == drop_front_flap` → 固定 2
- copied object / naming / placement / joint policy：
  - 门/抽屉：`door_{i}` / `drawer_{i}` 沿 X 均匀 (side_hinged), 沿 Z 堆叠 (drawer stack), 或沿 X 均分 (push_flap)。
  - joint 名统一 `carcass_to_{name}` or `{root}_to_{name}`；`hinged sides alternating`（i even → left hinge / axis -Z, odd → right hinge / axis +Z）；drawer 全部同轴 (0,-1,0)。
  - 共用 helper：`_build_door_leaf` / `_build_drawer_part` / `_build_flap` 各一个函数复用。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若有列取值/范围 · 若无写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | closure enum 直接改门/抽屉/flap 数量与 topology (0 或 N 或 2 或 4 movable children)。source_type=forked_anchor，全部来自 P1-P7 + variants。support wall_mount vs 腿类不同 visual anchor 也算 ① 轻量 |
| └ multiplicity | 同构件 ×N | 有 | 见 §Multiplicity。N ∈ {2,3,4,6}, weighted sampling |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE Z (side_hinged, bifold) / REVOLUTE X (drop_front, push_flap) / PRISMATIC ±Y (drawer_bank) / 无 joint (open_cubbies 需与 guard_door 组合)。source-backed 全部来自 P1-P7。sweep 会 exercise 每种 |
| ③ 主体形态家族 | 图/关节不变，换核心 part 几何 | 有 | body_form slot 6 candidates：3 × Planar Boundary Form (`rectangular_low_wide`, `rectangular_tall`, `corner_wedge`) + 2 × Volumetric Envelope Form (`low_wide_console`, `stepped_hutch`) + 1 × Macro Surface Construction (`bowed_front`)。已登记 `slot_choices` |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | 每 candidate 都可选叠加 `wood_grain` streaks (P1-P6 都有)。装饰几何从 host visual center 派生 (Rule 4)。record_only + world_knowledge_extrapolation。少量 grain 装饰放在 top_slab + door_panel + drawer_front 上 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | carcass_width [1.0,2.4]、carcass_depth [0.36,0.52]、carcass_height [0.40,1.05]，door open range 0..(1.45~1.75)*door_open_scale，drawer travel 0..0.28*drawer_travel_scale。运动包络：REVOLUTE Z 门 open方向 -Y (前) [0, 1.45..1.75]；REVOLUTE X 门 open方向 -Y and -Z [0, 1.45]；PRISMATIC 抽屉 [0, 0.28]。motion_test_plan：走 harness_motion_qc 默认 `{0, lower, upper, mid}` 采样 + 每个 closure 类型加一次 `ctx.pose({j: upper*0.8})` 目视 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `palette_style` 6 挡：`warm_greige` (P1) / `walnut_dark` (P2/P4) / `light_oak` (P3) / `cherry_wood` (P7) / `matte_black_wood` (P6) / `painted_white` (extrapolation)；每挡有 body / front / trim / hardware / dark 5-6 色 |

## 采样与覆盖审计

**总组合数** ≈ body_form(6) × closure(6) × support(6) × palette(6) = 1296 base combos。加 storage_count(2-6, 5 挡) 与连续 scale → 名义无限。

理由：形态-闭合-支撑三根离散轴独立取值 + 兼容矩阵剪枝 → 有效组合空间充分覆盖 10k-数据集需求。1000-seed slot choice tuple 目标至少 200-300 唯一组合（不作 gate）。

seed_domain_policy：procedural_first。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 顺序采 body_form → closure → support → palette → storage_count → 连续 scale。`resolve_config` 处理兼容矩阵 (wall_mount×stepped_hutch/corner_wedge → tapered_legs；powder_coated_sled×corner_wedge → splayed_wood_legs)、clamp scale、按 body_form 限缩 carcass 尺寸。无 regression overrides。

Controlled local parameterization：carcass_width / carcass_depth / carcass_height / door_open_scale / drawer_travel_scale — 全部在 `resolve_config` 内 clamp+conditional 处理。所有 scale 独立采样，不做隐式互依赖。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | deterministic per-seed rng; body_form → closure → support → palette → storage_count | slot_choices_for_seed matches build choices |
| compatibility matrix | (wall_mount, stepped_hutch/corner_wedge) fallback `tapered_legs`；(powder_coated_sled, corner_wedge) fallback `splayed_wood_legs` | no floating cabinet on unsupported base |
| controlled local variation | width/depth/height in [.85, 1.15] scale, door_open [0.7, 1.0], drawer_travel [0.7, 1.0]；clamped in resolve_config | proportions vary without breaking front layout or clearance |
| regression overrides | none | — |
| random sweep | seeds 0-15 fast, 0-35 final, appended corner | axis_realization; closure axis coverage |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 6 | yes | yes | ③ Primary Form Family slot |
| closure | 6 | yes | yes | ①/② mixed |
| support | 6 | yes | yes | ① |
| palette | 6 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed(seed)` returns implemented (slot, module) tuples for `body_form`, `closure`, `support`, `palette_style`, `storage_count`（后者以 raw N 编码）
- `config_from_seed(0)` succeeds and produces deterministic result
- `resolve_config` applies compatibility fallbacks (wall_mount× stepped_hutch/corner_wedge → tapered_legs) and clamps all scale ranges
- Regression overrides absent (main seed domain fully procedural)
- Controlled local scales clamped inside resolve_config
- Every non-FIXED joint has a `MatingContract` to real visuals on both sides (Rule 2)
- Cross-part scale dependencies (conditional height by body_form) resolved in `resolve_config`
- key joints: side_hinged_doors REVOLUTE ±Z; drop_front_flap / push_flap_row REVOLUTE ±X; drawer_bank PRISMATIC ±Y; bifold outer + inner both REVOLUTE ±Z
- copied objects: `door_{i}` / `drawer_{i}` follow uniform placement + `carcass_to_{name}` joint naming
- palette drives every `.visual(..., material=mats[key])` — no seed collapses to one colorway

## Reject cases

1. 门/抽屉在关闭姿态穿模 carcass 分隔板（分隔板必须在 closure 之间，不能与门重合）
2. wall_mount 落地 (z_floor 应 > 0.3 m)，或 wall_mount 用于 stepped_hutch （spec 强制 fallback）
3. bun_feet 高度 > 0.16 m 或 splayed leg tilt > 0.15 rad（视觉不协调）
4. drawer_bank N=6 时 grid 布局横向溢出 carcass_width（要 2×3 bank，carcass_width ≥ 1.4 m）
5. side_hinged_doors N=4 时单叶宽 < 0.20 m（叶过窄；template 要 clamp N 或缩小 carcass_width）
6. bifold_doors 时内外叶碰撞（inner leaf axis 必须匹配 outer leaf 端边，joint origin 精确到 free edge）
7. 立轴 门开到 1.75 rad 时 leaf 碰邻门（motion_qc 必然发现，控制 door_open_scale ≤ 0.85 for N ≥ 3）
8. push_flap_row 铰在错误 y 位置（应在门底缘 z=hinge_z），导致门开时向上翘

## 与相邻类别的边界

- 不该混入：CRT 电视机 / OLED 电视机（TV 本身不建，只造 cabinet 本体）
- 不该混入：普通写字台 / 学生桌（没有 front closures，也不允许无门 open shelving 单独出现）
- 不该混入：开放式陈列架（全部开放，无实体箱式 carcass）
- 不该混入：床头柜 / 小 nightstand（footprint 太小，宽度 < 0.5 m 不符合 TV cabinet 身份）
- 不该混入：书柜（front 全部开放或书排靠背 exposed，无 closures）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec 由 P3+P4 subagent 撰写；覆盖 6×6×6×6 离散轴 + 1 multiplicity + 5 连续 scale。所有 candidates 皆源自 P1-P7 或 fork variants，spec 兼容矩阵已声明。 |

## 模板实现备注（可选）

- `_build_carcass_shell(body_form, ...)`：单一函数按 body_form 分支，生成 side_panel/back_panel/bottom_slab/top_slab 差异
- `_build_hinged_door_leaf` / `_build_push_flap_leaf` / `_build_bifold_leaf` / `_build_drawer_part`：closure 内 helper
- `_build_support(support, ...)`：按 support 分支
- `PALETTES: dict[palette_style, dict[key, rgba]]` 6 挡；每档提供 body / front / trim / hardware / dark / grain 6 键
- MatingContract 关注点：
  - 门 hinge_barrel 元素 vs carcass side_panel 元素 (element-scoped allow_overlap for piano hinge)
  - 抽屉 tray 元素 vs carcass inner cavity (allow_overlap 隐藏 tray)
  - bifold inner leaf ↔ outer leaf hinge_barrel captured pin
- 采样 wall_mount + carcass 悬浮时，setattr carcass root aabb 的 z_floor 从 0（默认）改为 (0.30 + support offsets) 避免"orphan""floating cabinet" 失败——sink 是把 carcass 视觉抬起、wall_mount 视觉贴到后墙 y_wall 平面
