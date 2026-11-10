# cabinet — Modular Spec

> 来源小类：`picture/Other/Cabinet`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Cabinet.md`。
> **"Cabinet" 在此 = 立式储物柜家具**：一只中空箱体 carcass（钢皮储物柜 / 木质斗柜 / 床头柜）坐在底座/支撑上，正面是 1..N 个可开合的储物机构（铰门 / 抽屉 / 滑门 / 翻盖门 / 组合）。**不是**电视柜里的电视、不是椅子、不是嵌入式烤箱（见 §边界）。
>
> **同步状态**：本 spec 引用的 5 星样本（2 parent + 全部 fork 槽位/计数/底座变体）已同步进本仓库 `data/records/`，rating=5（25/25 核对为 5★）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（逐一核对）。引用以 part / joint / helper **名字** 为准（`cabinet_body` / `carcass` / `_build_drawer` / `_build_door` / `door_{i}_hinge` / `carcass_to_{name}` / `_slide_door_solid` / `carcass_to_flap_door` / `_caster_fork_solid` / `_plinth_solid` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `cabinet` |
| template path | `agent/templates/Other_Cabinet.py` |
| test path (optional) | `tests/agent/test_cabinet_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named root slot: carcass shell + 2 个可替换槽 storage_mechanism / base_support，**外加** `door_count` / `drawer_count` 两根多重性轴；门/抽屉数轴互斥，由 storage 槽派生）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 25（2 parent + 23 fork 变体；全部 compile success、workbench-only、≥1 非 fixed joint）|
| read_count | 25（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方槽位表与 §14；**7 个样本因身份漂移未采纳**（见下"未采纳/排除"），符合 spec only-adopted policy |

阅读要点（用于槽位分解）：

- **两个 parent 是两个不同坐标族，但同一类别身份**（中空箱体 carcass + 底座 + 正面开合机构）：
  - **P1 钢皮储物柜**（`rec_model-a-vintage-...-steel-locker-...76107d7e`，516 行）：root part `cabinet_body`，**前面朝 +Y**，宽沿 X。中空薄壁碳钢 carcass（side/back/bottom/top panel + front rails + stiles + 顶盖 + 铆钉）坐于 4 条 `_leg_solid` splayed 腿。正面 4 门，`for i, (hinge_x, sign, leaf_mat) in enumerate(door_specs)` 循环（L253）发射 `door_{i}` part（含 leaf 带 vent slot + hinge_barrel + vent_lines），每门 `door_{i}_hinge` **REVOLUTE**（轴 ±Z，0..110°）；每门带 `latch_knob_{i}` 子件 + `latch_{i}` **REVOLUTE**（轴 +Y 90° quarter-turn）。
  - **P2 黑木双斗柜**（`rec_model-a-wide-black-wooden-dresser-...58f0953c`，504 行）：root part `carcass`，**前面朝 +X**，宽沿 Y。中空木 carcass（side/back panel + bottom/top board + front rails/stiles + dust panels + 雕花角柱 + 银顶板）坐于 4 条 square `leg_{tag}`。正面 8 抽屉，`_build_drawer` helper（L98-167）发射 hollow open-top tray + front_panel + knob_ball/stem；`for name, d, cy, cz in drawers` 循环发射 `carcass_to_{name}` **PRISMATIC**（轴 +X，0..0.40 m）。
  - 两族**part 树拓扑同构**（root carcass shell → 复制 N 个 storage child，各自独立 joint），只是坐标轴朝向与 mesh 细节不同。storage_mechanism 与 base_support 是真正改 part 数/joint 拓扑的轴；footprint/坐标族折入 carcass-aware mesh helper（见 §模板实现备注）。

- **storage_mechanism 轴（Slot A，主机构槽）**——真正的 joint 拓扑变化：
  - hinged_doors（P1）：N×REVOLUTE 立轴铰门 + N×latch REVOLUTE。
  - drawers（P2）：N×PRISMATIC +X 抽屉。
  - sliding_doors（`...503dd3bb`，514 行）：2 个 bypass 滑门，`door_{i}_slide` **PRISMATIC**（轴 ±X，0..0.75 m），双 track + bypass Y 间隙；门数固定 2，无 latch。
  - door_over_drawers（`...73ab06e1`，605 行）：上 2 铰门（`carcass_to_door_{i}` REVOLUTE 立轴）+ 下 2 抽屉（`carcass_to_drawer_{i}` PRISMATIC），`_build_door` + `_build_drawer` 两 helper，中间 divider_rail 分隔。
  - flap_door（drop-down，`...2bf8cef6`，300 行）：单 `flap_door` part，`carcass_to_flap_door` **REVOLUTE 卧轴 Y**（底前缘铰，0..1.50 rad 前倾下翻）；床头柜 footprint。
  - hinged_single_door（`...02643395`，317 行）：单 `door` part，`carcass_to_door` REVOLUTE 立轴 Z（侧边铰，0..1.50 rad），内含 interior_shelf；床头柜 footprint，`for i in range(1)` uniform loop policy。
  - niche_over_drawer（`...bd3941ca`，367 行）：上半固定 open display niche（**无 joint**，纯 carcass visual）+ 下半单 PRISMATIC drawer；床头柜 footprint。

- **base_support 轴（Slot B）**——底座/支撑层，多数为 carcass 子 visual（fixed），casters 例外带 joint：
  - splayed_legs（P1 / `...65751baf` 床头柜版）：4 条 splayed/tapered 锥腿（`_leg_solid` / `_make_leg_mesh` LatheGeometry，外撇）。
  - square_legs（P2）：4 条直方腿 `leg_{tag}`（front 腿续雕花角柱）。
  - plinth_toe_kick（`...0c11ba6d`，547 行）：`_plinth_solid`（L117）倒角实心踢脚基座，前面后退 toe-kick 落地。
  - solid_toe_kick_box（`...6dddcda5`，395 行）：`base_upper` + `base_toekick` 两块炭灰基座 box，前下缘开 toe-kick 凹槽落地。
  - hairpin_legs（`...dcdcb159`，433 行）：4 条 `_build_hairpin_leg_mesh` 弯钢发卡腿 + `mount_plate_{i}` 安装板。
  - casters（`...8bf476d7`，651 行）：4 个 swivel caster，`_caster_fork_solid` 叉架（fixed body visual）+ `caster_wheel_{i}` part + `caster_{i}_axle` **CONTINUOUS**（轴 X）——底座层带自己的活动轮子。

- **door_count 轴（多重性，源 P1 钢柜）**：N=2(`...b094b80c`，`N_DOORS=2`)/4(P1)/6(`...1a090052`，range(6)) 已有真实样本；整门 + latch_knob 循环复制，`door_{i}`/`latch_{i}` 沿 X 等距、左右铰对称。
- **drawer_count 轴（多重性，源 P2 斗柜 + 床头柜抽屉族）**：N=1(`...b8d0c6c4`，`DRAWER_COUNT=1`)/3(`...50c223fe`，`N_DRAWERS=3`)/4(`...8a365012`，dresser `N_ROWS=2`×2)/6(`...9830b46f`，3 行×2)/8(P2) 已有真实样本；N=2/5/7 由同一单列堆叠 helper 派生并经模板测试验证。`_build_drawer` helper 复制 hollow tray+front+knobs，行/行列网格布局，各自独立 PRISMATIC。

**未采纳/排除（7 个 5★ 但身份漂移，不进槽位表）**——这些 fork 把 base/form prompt 套到了**别的类别**，几何已不是 cabinet：
- `rec_variant-base-support-four-wood-legs-...78b0bb00`（IKEA Markus 办公**椅** `markus_wood_leg_chair`）
- `rec_variant-base-support-cantilever-sled-...549d8992`（悬臂雪橇**椅** `markus_sled_chair`）
- `rec_variant-base-support-splayed-console-legs-...f3c0f936`（CRT **电视** console `..._console_television`）
- `rec_variant-base-support-swivel-base-...397aff58`（CRT **电视** swivel `..._crt_television_swivel`）
- `rec_variant-cabinet-form-portable-with-handle-...cb7ecf95`（CRT **电视** `vintage_samsung_crt_television`）
- `rec_variant-cabinet-form-rounded-space-age-pod-...1a475b57`（CRT **电视** pod `..._crt_television_pod`）
- `rec_variant-door-count-2-make-it-a-double-wall-oven-...3d0a0f67`（嵌入式双**烤箱** `built_in_double_wall_oven`）

它们对未来 `tv` / `armchair` / `built_in_oven` 模板有用，但不属于 cabinet identity，按 §2.4 不采纳。

## 核心身份

一只**立式储物柜家具**：一只接地的中空箱体 **carcass**（薄壁钢皮柜 / 厚板木斗柜 / 漆面床头柜，含 side/back/bottom/top panel + 正面框 rails/stiles，可有顶板/顶盖/雕花角柱等 parent visual），坐在 **base_support**（短锥腿 / 方腿 / 发卡腿 / 实心踢脚基座 / 脚轮）上落地（z_min≈0），正面是一组**储物开合机构 storage_mechanism**：1..N 个铰门（立轴 REVOLUTE，含可选 quarter-turn latch）、1..N 个抽屉（PRISMATIC 前抽）、2 个 bypass 滑门（PRISMATIC 横移）、单翻盖门（卧轴 REVOLUTE 前倾）或上门下抽/上龛下抽的组合。活动语义 = **正面开合**（门转开 / 抽屉抽出 / 滑门横移 / 翻盖前翻），可选 base 上的脚轮 CONTINUOUS 旋转。默认成熟域：storage_mechanism × base_support × door_count/drawer_count 的中大型立式储物柜。

不该混入：
- **电视/电视柜里的电视机**（CRT/显示器）——cabinet 的正面是开合储物机构，不是屏幕/旋钮面板；电视身份在玻璃屏 + 调谐旋钮，缺这套即出类。
- **椅子/凳子**（座面 + 靠背 + 腿，或雪橇/气压柱底座）——无中空储物箱体、无门/抽屉开合机构。
- **嵌入式烤箱/壁挂烤箱**（玻璃门 + 控制面板 + 加热腔，下翻烤箱门）——虽有下翻门，但烤箱身份在加热腔 + 面板 + 双腔堆叠，且通常嵌墙无独立底座；cabinet 是独立落地储物家具。
- **保险箱/壁挂保险柜**（单厚门 + 转盘锁，嵌墙）——已有 `wall_safe_*` 模板；cabinet 强调多门/多抽 + 落地底座。
- **行李箱/工具箱/宝箱**（顶翻盖箱体）——卧式、提手、非落地立式储物家具。

## 槽位 + 候选模块表

> **建模注记**：root part `carcass`（中空箱体 shell + 正面框）是**固定 named root**，不是可替换槽——它由 carcass-aware mesh helper 按所选 storage_mechanism 决定 footprint 坐标族（钢柜族 front=+Y / 木柜族 front=+X）与正面框布局（单大开口 / 多门 pocket / 抽屉 zone / 上下分区），并发射 base_support 的 fixed 子件。可替换的真正拓扑轴是 **storage_mechanism**（Slot A，改 child part 数 + joint 类型/轴）与 **base_support**（Slot B，改底座结构 + 可选 caster joint）；door_count / drawer_count 是挂在 storage 槽上的多重性轴（§8）。

### Slot A：storage_mechanism（开合机构 —— **主机构槽**，决定正面 child part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| hinged_doors（基线 P1） | rec_model-a-vintage-...steel-locker...76107d7e | door_specs+loop L245-339（`_door_solid` L78-96 / `_hinge_barrel_solid` L99-111） | eligible if compatible | N×立轴铰门：`door_{i}` part（leaf+vent slot+hinge_barrel）`door_{i}_hinge` REVOLUTE 轴 ±Z 0..110°；每门 `latch_knob_{i}` + `latch_{i}` REVOLUTE 轴 +Y quarter-turn。钢柜 footprint(front +Y)。**驱动 door_count 轴** |
| drawers（基线 P2） | rec_model-a-wide-black-wooden-dresser...58f0953c | `_build_drawer` L98-167 / drawers loop L311-335 | eligible if compatible | N×PRISMATIC 前抽：`_build_drawer` 发射 front_panel + hollow open-top tray(bottom/back/side/front wall) + knob_ball/stem；`carcass_to_{name}` PRISMATIC 轴 +X 0..0.40 m。木柜 footprint(front +X)，行/行列网格。**驱动 drawer_count 轴** |
| sliding_doors | rec_variant-storage-mechanism-sliding-doors...503dd3bb | `_slide_door_solid` L93-105 / door loop L260-320 | eligible if compatible | 2 个 bypass 滑门：`door_{i}` part(leaf+vent+grip)；`door_{i}_slide` PRISMATIC 轴 ±X 0..0.75 m；双 track rail + bypass Y 深度差。门数固定 2，无 latch。钢柜 footprint |
| door_over_drawers | rec_variant-storage-mechanism-door-over-drawers...73ab06e1 | `_build_drawer` L95-162 / `_build_door` L165-207 / 装配 L354-396 | eligible if compatible | 上 2 铰门(REVOLUTE 立轴 Z 0..1.4)+下 2 抽屉(PRISMATIC +X)；divider_rail 分区；混合 REVOLUTE+PRISMATIC 拓扑。木柜 footprint |
| flap_door | rec_variant-storage-mechanism-drop-down-flap...2bf8cef6 | `_add_chrome_bar_handle` L64-80 / flap 装配 L154-189 | eligible if compatible | 单翻盖门：`flap_door` part(door_slab+handle)；`carcass_to_flap_door` REVOLUTE **卧轴 +Y**（底前缘铰 0..1.50 rad 前倾下翻）；gallery-lip carcass。床头柜 footprint |
| hinged_single_door | rec_variant-storage-mechanism-hinged-cabinet-door...02643395 | `_build_door` L60-100 / 装配 L179-195 | eligible if compatible | 单铰门：`door` part(door_panel+handle)；`carcass_to_door` REVOLUTE 立轴 +Z（侧边铰 0..1.50 rad）；含 interior_shelf。床头柜 footprint，`for i in range(1)` |
| niche_over_drawer | rec_variant-storage-mechanism-open-niche-over-drawer...bd3941ca | `_build_drawer` L70-142 / 装配 L145-240 | eligible if compatible | 上半固定 open display niche(divider_shelf+runner，**无 joint**)+下半单 PRISMATIC drawer 0..0.36 m；床头柜 footprint。最少活动件 |

### Slot B：base_support（底座/支撑 —— 多为 carcass fixed 子件，casters 例外带 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| splayed_legs（基线） | rec_model-a-vintage-...76107d7e（`_leg_solid` L114-126 / 装配 L226-239）；床头柜版 `...65751baf`（`_make_leg_mesh` L78-110 LatheGeometry）| see source | eligible if compatible | 4 条外撇锥腿；P1 用 cadquery loft，床头柜版用 LatheGeometry 外撇旋转；fixed carcass 子 visual `leg_{i}` |
| square_legs | rec_model-a-wide-black-wooden-dresser...58f0953c | leg loop L294-303 | eligible if compatible | 4 条直方腿 `leg_{tag}`（front 腿续雕花角柱），fixed carcass 子 visual |
| plinth_toe_kick | rec_variant-base-support-plinth-toe-kick...0c11ba6d | `_plinth_solid` L117-134 | eligible if compatible | 倒角实心踢脚基座，前面后退 0.07 m toe-kick 落地，全宽接地；fixed |
| solid_toe_kick_box | rec_variant-base-support-solid-toe-kick-box...6dddcda5 | base 装配 L155-175（`BASE_H` L39 / `base_upper` / `base_toekick`）| eligible if compatible | 炭灰实心基座 box(`base_upper`)+前下缘 toe-kick 凹槽(`base_toekick`)落地；fixed 双 box |
| hairpin_legs | rec_variant-base-support-hairpin-metal-legs...dcdcb159 | `_build_hairpin_leg_mesh` L74-... / 装配 L199-210 | eligible if compatible | 4 条弯钢发卡腿 `hairpin_leg_{i}`+`mount_plate_{i}` 安装板；fixed carcass 子 visual |
| casters | rec_variant-base-support-casters...8bf476d7 | `_caster_fork_solid` L129-... / `_caster_wheel_mesh` L176-... / 装配 L286-326 | eligible if compatible | 4 个 swivel caster：`caster_fork_{i}`(fixed)+`caster_wheel_{i}` part+`caster_{i}_axle` **CONTINUOUS** 轴 X；**唯一带 joint 的 base 模块**（+4 CONTINUOUS） |

## 槽位图（slot graph）

pattern: `mixed`（parallel_children + 两根 multiplicity；坐标族由 storage 选择派生）

```
                      carcass (root part, 固定; carcass-aware mesh helper
                      按 storage 选 footprint 坐标族 front=+Y/+X + 正面框布局)
                       │
        ┌──────────────┼──────────────────────────────┐
        │ [parent-child fixed support: base 子件嵌入 carcass 底面] │
        ▼                                              ▼
  Slot B: base_support                          Slot A: storage_mechanism
  (legs/plinth/toekick = fixed carcass visual;  (REVOLUTE 门 / PRISMATIC 抽 /
   casters = +N CONTINUOUS 轮 child)             PRISMATIC 滑门 / 卧轴翻盖 /
        │                                        混合门+抽 / 龛+抽)
        │ caster: body --[CONTINUOUS axis X]--> caster_wheel_{i}
        │
   storage child 复制（multiplicity，挂 carcass）:
     hinged_doors  : carcass --[REVOLUTE axis ±Z @ front opening edge]--> door_{i}
                     door_{i} --[REVOLUTE axis +Y]--> latch_knob_{i}
     drawers       : carcass --[PRISMATIC axis +X @ front slab plane]--> drawer_{i}
     sliding_doors : carcass --[PRISMATIC axis ±X @ track]--> door_{i}（固定 2，bypass Y 错位）
     flap_door     : carcass --[REVOLUTE axis +Y @ bottom front edge]--> flap_door（固定 1）
     door_over_drawers: 上 door_{i}(REVOLUTE Z) + 下 drawer_{i}(PRISMATIC X)（各 2）
     niche_over_drawer: niche=fixed carcass visual（无 joint）+ drawer(PRISMATIC X，1)
```

接口点位说明：
- **carcass↔storage child**：mating face = carcass 正面开口平面（钢柜族 front_y=+CAB_D/2；木柜族 front_x=BD）。门铰 pivot 在开口左/右竖边（REVOLUTE 立轴 ±Z）或底前缘（flap 卧轴 +Y）；抽屉 rail/slider 沿 +X（PRISMATIC）；滑门 track 沿 ±X。joint origin 落在开口边/前 slab 面，closed pose 门/前板与 carcass 正面齐平（flush）或微凸（proud）。
- **carcass↔base**：contact plane = carcass 底面（z=LEG_H/BASE_H）；legs/plinth/toekick 顶端嵌入 carcass 底 2 mm（fixed support，no joint）；caster fork plate 贴 carcass 底，`caster_{i}_axle` CONTINUOUS pivot 在轮轴心（轴 X）。
- **互斥/派生**：door_count 仅对 storage∈{hinged_doors} 有效（sliding_doors 固定 2、flap/single 固定 1、door_over_drawers 固定 2 门）；drawer_count 仅对 storage∈{drawers} 有效（door_over_drawers/niche_over_drawer 固定抽屉数）。latch 仅 hinged_doors 携带。casters 是唯一向模型新增 joint 的 base。

## 每槽位 Module Emits / Interfaces

### Slot A / module hinged_doors（基线 P1）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}`(leaf + vent_backing + vent_line_{j} + hinge_barrel)、`latch_knob_{i}`(backplate/boss/handle_bar/handle_tip) | P1 / model.py:L253-339 |
| internal joints | `door_{i}_hinge` REVOLUTE 轴(0,0,sign) 0..110°；`latch_{i}` REVOLUTE 轴(0,1,0) 0..90° | P1 / model.py:L286-339 |
| upstream interface | parent=`cabinet_body`，hinge origin=(hinge_x, FRONT_Y, DOOR_ZC) 落开口竖边 | P1 / model.py:L286-298 |
| downstream interface | latch parent=door，origin=门前面 mid-height；闭合时 leaf 前面与 FRONT_Y flush | P1 / model.py:L328-339,L408-415 |

### Slot A / module drawers（基线 P2）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `*_drawer_{i}`(front_panel + tray_bottom/back/side/front_wall + knob_stem/ball_{k}) | P2 / model.py:L98-167 |
| internal joints | `carcass_to_{name}` PRISMATIC 轴(1,0,0) 0..0.40 m | P2 / model.py:L325-335 |
| upstream interface | parent=`carcass`，joint origin=(JOINT_X=前 slab 面, cy, cz) | P2 / model.py:L325-331 |
| downstream interface | 闭合 tray 嵌入 carcass、front_panel 微凸 carcass 前面、knob 凸出 front | P2 / model.py:L440-462 |

### Slot A / module sliding_doors
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}`(leaf + vent_backing + vent_line + grip_recess/bar)；body 加 top/bottom_track + lip | S3 / model.py:L196-306 |
| internal joints | `door_{i}_slide` PRISMATIC 轴(±1,0,0) 0..0.75 m（bypass：door_0 前 track door_1 后 track Y 错位）| S3 / model.py:L310-320 |
| upstream interface | parent=body，origin=(rest_x, rest_y, DOOR_ZC)；2 门 bypass，Y 间隙≥2 mm | S3 / model.py:L310-320,L440-453 |
| downstream interface | 闭合双门覆盖整开口、X 重叠 bypass、各 leaf 嵌 track ≤2 mm（element-scoped allow_overlap）| S3 / model.py:L331-343 |

### Slot A / module door_over_drawers
| emits | 描述 | 来源 |
|---|---|---|
| parts | 上 `door_{i}`(panel+back_panel+knob)、下 `drawer_{i}`(front+tray+knobs)；carcass 加 divider_rail | S4 / model.py:L165-396 |
| internal joints | `carcass_to_door_{i}` REVOLUTE 轴(0,0,±1) 0..1.4；`carcass_to_drawer_{i}` PRISMATIC 轴(1,0,0) 0..0.40 | S4 / model.py:L366-396 |
| upstream interface | 门 hinge origin=(JOINT_X, ±OPEN_HW, DOOR_CZ)；抽 origin=(JOINT_X, cy, CZ_BOT) | S4 / model.py:L369-395 |
| downstream interface | 门上抽下、divider 分隔；门中央对开 thin reveal、闭合 flush | S4 / model.py:L490-528 |

### Slot A / module flap_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flap_door`(door_slab + handle_post_{i} + handle_bar)；carcass=gallery-lip shell | S5 / model.py:L154-189 |
| internal joints | `carcass_to_flap_door` REVOLUTE **卧轴 (0,1,0)** 0..1.50 rad（底前缘铰，前倾下翻）| S5 / model.py:L180-189 |
| upstream interface | parent=carcass，origin=(HINGE_X=D, 0, HINGE_Z=BODY_BOT_Z) 底前缘 | S5 / model.py:L185-189 |
| downstream interface | 闭合门竖直 flush 正面；开 pose 门顶前移+下落 | S5 / model.py:L248-295 |

### Slot A / module hinged_single_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`(door_panel + handle_post/bar)；carcass 含 interior_shelf | S6 / model.py:L60-195 |
| internal joints | `carcass_to_door` REVOLUTE 立轴 (0,0,1) 0..1.50 rad（侧边铰）| S6 / model.py:L184-195 |
| upstream interface | origin=(D, HINGE_Y=INNER_W/2, DOOR_CZ) 侧竖边 | S6 / model.py:L186-195 |
| downstream interface | 闭合门覆盖整开口 flush；shelf 在门后不重叠 | S6 / model.py:L255-296 |

### Slot A / module niche_over_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | 上 niche=carcass divider_shelf+top_shelf（**fixed，无 part/joint**）；下 `drawer`(front+tray+handle) | S7 / model.py:L145-240 |
| internal joints | `carcass_to_drawer` PRISMATIC 轴(1,0,0) 0..0.36 m（仅 1 个）| S7 / model.py:L231-240 |
| upstream interface | drawer origin=(D, 0, CZ_DRAWER)；niche 为 carcass visual | S7 / model.py:L231-240 |
| downstream interface | 抽屉在 divider 下、闭合 flush；niche 开抽时不动 | S7 / model.py:L312-362 |

### Slot B / base_support（各模块 emits）
| module | emits（parts / joints / interface） | 来源 |
|---|---|---|
| splayed_legs | 4×`leg_{i}` fixed carcass visual（loft/lathe 外撇锥腿），顶嵌 carcass 底 2 mm，无 joint | P1 L114-239 / `...65751baf` L78-110 |
| square_legs | 4×`leg_{tag}` fixed 直方腿（front 续角柱），无 joint | P2 L294-303 |
| plinth_toe_kick | 1×`plinth` fixed 倒角实心基座（`_plinth_solid`），前退 toe-kick，无 joint | `...0c11ba6d` L117-134 |
| solid_toe_kick_box | `base_upper`+`base_toekick` fixed 双 box，前下凹槽，无 joint | `...6dddcda5` L155-175 |
| hairpin_legs | 4×`hairpin_leg_{i}`+`mount_plate_{i}` fixed 弯钢腿，无 joint | `...dcdcb159` L74-210 |
| casters | 4×`caster_fork_{i}`(fixed)+4×`caster_wheel_{i}` part；4×`caster_{i}_axle` **CONTINUOUS** 轴(1,0,0) | `...8bf476d7` L129-326 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| storage_mechanism | enum | hinged_doors / drawers / sliding_doors / door_over_drawers / flap_door / hinged_single_door / niche_over_drawer | — | choice | deterministic procedural sampler 或 regression override；决定 footprint 坐标族 | Slot A 表 |
| base_support | enum | splayed_legs / square_legs / plinth_toe_kick / solid_toe_kick_box / hairpin_legs / casters | — | choice | sampler；与 footprint 坐标族兼容性 gate（见 §9 matrix）| Slot B 表 |
| door_count | int | [2, 8]（产品域），测试 {2,4,6} | 4 | conditional | 仅 storage=hinged_doors 生效；否则固定（sliding=2/flap=1/single=1/door_over=2）| §8 / P1,`...b094b80c`,`...1a090052` |
| drawer_count | int | [1, 8]（产品域），测试 {1,2,3,4,5,6,7,8} | 由 storage 派生 | conditional | 仅 storage=drawers 生效；door_over/niche 固定抽屉数 | §8 / `...b8d0c6c4`,`...50c223fe`,`...8a365012`,`...9830b46f`,P2 + procedural N=2/5/7 |
| palette_style | enum | industrial_steel / matte_black_wood / lacquered_gray / warm_oak / charcoal_satin | — | choice | per-seed 采样；改 material rgba，不改拓扑 | 见 §palette |
| carcass_width_scale | float | [0.85, 1.15] | 1.0 | independent | clamp；缩 carcass W，门/抽屉宽派生跟随 | P1 CAB_W / P2 W_TOTAL |
| carcass_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩 carcass H；门/抽屉 zone 高派生 | P1 CAB_TOP / P2 H_TOTAL |
| door_open_scale | float | [0.7, 1.0] | 1.0 | independent | clamp；门 REVOLUTE upper = base_angle·scale（不超几何 clear）| P1 DOOR_OPEN |
| drawer_travel_scale | float | [0.7, 1.0] | 1.0 | independent | clamp；PRISMATIC upper = travel·scale，保证 tray 余量留存 | P2 TRAVEL |
| (—) | constraint | — | — | conditional | door_count/drawer_count 合法范围 = storage 选择派生（见上两行）| 接口 |
| (—) | constraint | — | — | inequality | `每门/抽屉宽 = 开口净宽/N ≥ min_leaf`；N 过大时 clamp N 上限或回缩 reveal | 开口 / clearance |
| (—) | constraint | — | — | inequality | `closed door swing/抽屉行程 ≤ 可用 clearance`；door_open/travel 投影到可行域 | clearance |

连续尺寸采样契约：先采 independent（width/height/open/travel scale），由 storage 选择派生 door/drawer count 合法域（conditional）并加权采 N，再用 inequality 投影（leaf 最小宽、行程余量），违反则回缩 scale 或 clamp N。

## Multiplicity / Copy Logic

本类有 **2 根互斥多重性轴**，由 storage_mechanism 选择激活其一（其余 storage 模块为固定数量，不暴露 count）。

- **count_param 1: `door_count`**（铰门数，源 P1 钢皮储物柜）
  - `N_range`：产品域 **[2, 8]**；测试偏小 {2, 4, 6}（已有真实样本 N=2 `...b094b80c`、N=4 P1、N=6 `...1a090052`）。
  - sampling domain（加权）：N∈{2,3,4} 高频（~70%），{5,6} 中频，{7,8} 稀有尾部。
  - copied object：整门 `door_{i}`（leaf+vent+hinge_barrel）+ 各自 `latch_knob_{i}`。
  - naming：`door_{i}` / `door_{i}_hinge` / `latch_knob_{i}` / `latch_{i}`（母资产已 `for i, (...) in enumerate(door_specs)` 循环）。
  - placement：沿 carcass 宽(X)等距分门 pocket；左半左铰、右半右铰（sign 镜像），free edge 朝中央。
  - joint policy：每门独立 REVOLUTE 立轴 ±Z 0..(110°·open_scale)；每门各自 latch REVOLUTE 轴 +Y quarter-turn。
  - source/gating：仅 storage=hinged_doors；门宽 = 开口净宽/N，clamp `门宽 ≥ ~0.18 m` 决定 N 上限。

- **count_param 2: `drawer_count`**（抽屉数，源 P2 斗柜 + 床头柜抽屉族）
  - `N_range`：产品域 **[1, 8]**；测试 {1, 2, 3, 4, 5, 6, 7, 8}（已有真实样本 N=1 `...b8d0c6c4`、N=3 `...50c223fe`、N=4 dresser `...8a365012`、N=6 `...9830b46f`、N=8 P2；N=2/5/7 由同一堆叠布局派生验证）。
  - sampling domain（加权）：N∈{1,2,3} 高频，{4,6} 中频，{8} 稀有；偶数大 N 走斗柜行列网格、小 N 走床头柜单列堆叠。
  - copied object：`_build_drawer` helper（front_panel + hollow open-top tray + knob_ball/stem）。
  - naming：床头柜族 `drawer_{i}`、斗柜族 `top_drawer_{i}`/`{row}_drawer_{i}`/`drawer_{i}_{j}`（行列）。
  - placement：单列等高堆叠（床头柜）或行列网格（斗柜，宽抽双 knob、小抽单 knob）。
  - joint policy：每抽屉独立 PRISMATIC 轴 +X 0..(0.40·travel_scale)；rear 保持插入。
  - source/gating：仅 storage=drawers；抽屉前高 = zone 高/行数，clamp 最小前高决定 N 上限。

- **固定数量 storage（无可调 count）**：sliding_doors 固定 2 bypass、flap_door 固定 1、hinged_single_door 固定 1、door_over_drawers 固定 2 门+2 抽、niche_over_drawer 固定 1 抽。这些模块不暴露 `*_count`，由 named 结构表达。

## 拓扑多样性审计

总组合数（不含连续 scale）：
- storage_mechanism = 7（其中 hinged_doors 展开 door_count {2..8}=7 档；drawers 展开 drawer_count {1..8}=8 档；其余 5 个各 1 档）
- storage 拓扑等价类计数：hinged_doors(7) + drawers(8) + sliding_doors(1) + door_over_drawers(1) + flap_door(1) + hinged_single_door(1) + niche_over_drawer(1) = **20** 个 storage-side distinct 拓扑
- base_support = 6（其中 casters 额外引入 +4 CONTINUOUS joint，是独立拓扑类）
- 总 = 20 × 6 = **120** 个 distinct (storage×count×base) 拓扑组合（远超 multiplicity 门槛；含连续 scale 后 1000-seed distinct 预计 >200）

理由：仅 storage×base 笛卡尔积已 ≥120 个 part-tree/joint 拓扑不同的组合；joint 谱含 REVOLUTE 立轴(铰门/单门)、REVOLUTE 卧轴(翻盖)、PRISMATIC X(抽屉/滑门)、CONTINUOUS(脚轮)、混合(门+抽)，外加两根多重性轴改 child 数 → distinct 充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed deterministic 采样：①先 storage_mechanism（7 选 1，加权），②若 storage 有 count 轴则按权重采 N（小 N 偏多、尾部稀有），③base_support（6 选 1，过 compatibility gate），④采 4 个连续 scale 并 clamp/投影。footprint 坐标族由 storage 派生（钢柜族 / 木柜族 / 床头柜族），base 与该族的安装面绑定。`seed=0` 不特殊。random sweep 0-49 初轮、0-999 成熟审计；viewer 目检覆盖各 storage×base 闭合姿态 + 开合姿态。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类结构上 ≥120 基础组合，低于 300 时记录离散空间或采样权重原因。
若使用 regression overrides：none（首版不需要 curated 表）。

Controlled local parameterization：carcass_width_scale [0.85,1.15]、carcass_height_scale [0.85,1.20]、door_open_scale [0.7,1.0]、drawer_travel_scale [0.7,1.0]。全部 independent 采样后 clamp；door/drawer 宽高由 carcass scale **equation 派生**（保持开口净宽/N ≥ min_leaf）；door_open/travel 经 **inequality** 投影到 clearance 可行域。这些 scale 只改安全比例/行程，不改 storage/base 拓扑、不改 multiplicity、不破坏 joint origin 与 footprint 安装面。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | storage→(count 加权)→base→scales 顺序；compatibility gate 阻非法 storage×base | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 见下"兼容矩阵"；坐标族-base 绑定、count-storage 派生、casters 唯一加 joint | no floating leg/base、no 抽屉/门穿模、joint 轴正确、closed flush、N 上限 clamp、bypass Y 间隙 |
| controlled local variation | 4 个 scale，clamp+派生+投影 | 比例变化不破开口/clearance/支撑/joint origin/类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮、0-999 成熟审计 | 与 contract failures |

兼容矩阵 / gating：
- **坐标族-base 绑定**：钢柜族 storage(hinged_doors/sliding_doors, front +Y) → base∈{splayed_legs, plinth_toe_kick, casters}；木柜/床头柜族 storage(drawers/door_over_drawers/flap_door/hinged_single_door/niche_over_drawer, front +X) → base∈{square_legs, splayed_legs, hairpin_legs, solid_toe_kick_box, plinth_toe_kick}。splayed_legs/plinth 两族通用。casters 仅大型立柜（钢柜/斗柜），不挂床头柜（避免 floating 比例失真）。
- **count-storage 派生**：door_count 仅 hinged_doors；drawer_count 仅 drawers；其余 storage 固定数量（gate 掉非法 count 暴露）。
- **N 上限 clamp**：door_count 上限由门宽 ≥0.18 m 决定；drawer_count 上限由抽屉前高最小值决定；超限拒绝重采或 clamp。
- **casters joint**：唯一向模型加 joint 的 base，需声明 caster fork/plate 与 carcass 底的 fixed-support overlap 及轮-叉 element-scoped allow_overlap。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A storage_mechanism | 7 | yes | yes | 2 基线范式 + 5 fork 拓扑 |
| B base_support | 6 | yes | yes | 5 fixed + casters(带 joint) |
| multiplicity door_count | N∈{2,4,6} 真实样本 | yes | yes | 产品域 [2,8] |
| multiplicity drawer_count | N∈{1,3,4,6,8} 真实样本；N∈{2,5,7} 派生验证 | yes | yes | 产品域 [1,8] |

## Validator

- slot_choices_for_seed returns implemented module names（storage_mechanism + base_support + 激活的 count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（坐标族-base 绑定、count-storage 派生、casters 不挂床头柜、N 上限 clamp）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (width/height/open/travel) clamped；cross-part 依赖（开口净宽/N、行程余量）在 resolve_config 求解，不留到 builder
- critical InterfaceSpec / MatingContract points exist：carcass 正面开口面↔storage joint origin、carcass 底面↔base fixed support、caster axle pivot
- key joints have expected type / axis / range：铰门 REVOLUTE ±Z、翻盖 REVOLUTE +Y、抽屉/滑门 PRISMATIC ±X、脚轮 CONTINUOUS X、latch REVOLUTE +Y
- copied objects follow naming and placement policy：`door_{i}`/`latch_{i}`/`*_drawer_{i}` 等距/网格、左右铰镜像
- closed pose：所有门/前板与 carcass 正面 flush 或微凸、base 接地 z_min≈0、无悬空

## Reject cases

- storage child 悬空：门/抽屉 joint origin 未落在 carcass 正面开口面或前 slab 面，闭合不 flush。
- footprint 坐标族与 base 不匹配（钢柜 front +Y 却用木柜 +X 安装腿）→ base floating 或穿模。
- door_count/drawer_count 暴露给固定数量 storage（sliding/flap/single/door_over/niche）。
- N 过大未 clamp：门宽/抽屉前高低于最小值 → 门/抽屉退化或相邻穿模。
- 翻盖门用立轴 Z 或抽屉用 REVOLUTE（joint 类型/轴错）。
- bypass 滑门无 Y 间隙 → 两门 3D 互穿（须 expect_gap Y + expect_overlap X）。
- casters 缺 fork/plate 与 carcass 底的 allow_overlap，或轮无 CONTINUOUS joint（变纯装饰）。
- base 不接地（z_min≠0）或 carcass 比例 scale 越界破坏开口 clearance。
- 误把电视/椅子/烤箱 reskin 样本当 candidate（身份漂移，已在 §阅读摘要排除）。

## 与相邻类别的边界

- 不该混入：**tv / 电视**（CRT/显示器）——正面是屏幕+旋钮非储物开合；6 个漂移样本归 tv 模板。
- 不该混入：**armchair / 椅子**——座面+靠背+腿，无中空储物箱体；2 个漂移样本归 armchair。
- 不该混入：**built_in_oven / 嵌入式烤箱**——加热腔+控制面板+双腔堆叠，嵌墙；1 个漂移样本归 built_in_oven。
- 不该混入：**wall_safe / 保险箱**——单厚门+转盘锁嵌墙，已有专门模板。
- 不该混入：**bag/suitcase/box/treasure_chest**——卧式顶翻盖箱，非落地立式储物家具。
- 不该混入：**drawer_cabinet_with_sliding_drawers**（已有模板）——若与该模板的抽屉子域大量重叠，实现时复核是否需收窄 cabinet 的 drawers 子域（见 §模板实现备注）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。重点复核：(1) 钢柜(front+Y) vs 木柜/床头柜(front+X)两坐标族是否在单一 slug 内可控（carcass-aware mesh helper），还是应拆 slug；(2) 7 个漂移样本排除是否认可；(3) door_count/drawer_count 互斥派生逻辑；(4) 与既有 `drawer_cabinet_with_sliding_drawers` 模板的子域重叠是否需收窄。|

## 模板实现备注（可选）

- **坐标族风险（最重要）**：本类 5★ 样本横跨 2 个坐标族（钢柜 front=+Y 宽沿 X；木/床头柜 front=+X 宽沿 Y）。首版建议 carcass-aware mesh helper 统一为**一个内部规范坐标**（如 front=+X），把两族 footprint/正面框/base 安装面都映射进去；storage/base 模块工厂只消费规范坐标。若实现中发现两族主运动 spine 不兼容，按 README TEMPLATE_AFTER_REVIEW 优先**拆 slug**（如 `cabinet_hinged_locker` / `cabinet_dresser`），首版 config_from_seed 只采样已实现且测试覆盖的稳定子族。
- **共享 helper**：`_build_drawer`（drawers / door_over_drawers / niche_over_drawer 三模块共用）；`_build_door`（hinged_single_door / door_over_drawers 共用）；门 latch 仅 hinged_doors。
- **element-scoped allow_overlap**：piano-hinge `hinge_barrel` 与 carcass 框边（P1 模式）、滑门 leaf 嵌 track ≤2 mm、caster fork/plate 嵌 carcass 底、leg/plinth 顶嵌 carcass 底 2 mm —— 均需局部 allow_overlap 声明。
- **暂不进 seed domain（首版可选）**：casters×床头柜组合先 gate 掉（比例失真）；door_count/drawer_count 尾部（>6）首轮 sweep 可降权，成熟审计再放开到产品域上限。
- **与 drawer_cabinet 模板**：若 reviewer 认为 drawers 子域与既有 `drawer_cabinet_with_sliding_drawers` 重复，可在 cabinet 中收窄 drawers 为"斗柜/床头柜外形"，把纯滑轨抽屉柜留给既有模板。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A storage | hinged_doors（基线）| rec_model-a-vintage-...76107d7e | L78-339 | 铰门 part 树 + REVOLUTE 立轴 + latch + door_count 轴 |
| S2 | A storage | drawers（基线）| rec_model-a-wide-black-...58f0953c | L98-335 | 抽屉 `_build_drawer` + PRISMATIC + drawer_count 轴 |
| S3 | A storage | sliding_doors | ...503dd3bb | L93-320 | bypass 滑门 PRISMATIC + track |
| S4 | A storage | door_over_drawers | ...73ab06e1 | L95-396 | 上门下抽混合拓扑 |
| S5 | A storage | flap_door | ...2bf8cef6 | L64-189 | 翻盖门卧轴 REVOLUTE +Y |
| S6 | A storage | hinged_single_door | ...02643395 | L60-195 | 单铰门立轴 + interior_shelf |
| S7 | A storage | niche_over_drawer | ...bd3941ca | L70-240 | 固定龛 + 单抽屉 |
| S8 | B base | splayed_legs（基线）| 76107d7e / ...65751baf | L114-239 / L78-110 | 外撇锥腿 fixed |
| S9 | B base | square_legs | ...58f0953c | L294-303 | 直方腿 fixed |
| S10 | B base | plinth_toe_kick | ...0c11ba6d | L117-134 | 实心踢脚基座 |
| S11 | B base | solid_toe_kick_box | ...6dddcda5 | L155-175 | 双 box 踢脚基座 |
| S12 | B base | hairpin_legs | ...dcdcb159 | L74-210 | 弯钢发卡腿 |
| S13 | B base | casters | ...8bf476d7 | L129-326 | swivel 脚轮 + CONTINUOUS 轮 |
| MX1 | mult | door_count | ...b094b80c(2) / 76107d7e(4) / ...1a090052(6) | — | 门数轴样本 |
| MX2 | mult | drawer_count | ...b8d0c6c4(1)/...50c223fe(3)/...8a365012(4)/...9830b46f(6)/58f0953c(8); procedural verified (2,5,7) | — | 抽屉数轴样本 |

## palette_style 颜色方案（per-seed 采样，≥3 目标 4-6，源自 5★ 样本 material）

| palette_style | 主体 carcass | 门/前板 | 顶/trim | 五金/knob | 来源样本 material |
|---|---|---|---|---|---|
| industrial_steel | 刷面钢灰 (0.60,0.61,0.63) | 钢灰 a/b (0.55/0.50) | trim (0.46,0.47,0.49) | 暗钢 knob (0.18,0.18,0.20) | P1 steel_body/door/trim/knob |
| matte_black_wood | 哑光黑木 (0.075,0.075,0.08) | 黑木 deep (0.055) | 银灰顶板 (0.72,0.73,0.75) | 抛光银球 (0.90,0.91,0.93) | P2 matte_black_wood/silver_top/polished_silver |
| lacquered_gray | 漆面中灰 (0.50,0.52,0.55) | 浅缎面 (0.85,0.87,0.88) | 灰 | 抛光铬 (0.80,0.82,0.85) | 床头柜族 carcass_gray/front_pale_satin/polished_chrome |
| warm_oak | 暖橡木 (0.62,0.46,0.30) | 橡木浅 (0.70,0.54,0.38) | 木顶 | 黄铜 (0.72,0.60,0.32) | 派生自木柜族（暖色重映射 P2/床头柜结构）|
| charcoal_satin | 炭灰缎面 (0.27,0.28,0.30) | 炭灰浅 (0.40,0.42,0.45) | 深灰 trim | 哑黑五金 (0.14,0.14,0.16) | solid_toe_kick base 炭灰 + 床头柜 plinth_gray |

palette_style 仅改 material rgba，不改拓扑（按 §7 choice 类型 per-seed 采样）。warm_oak / charcoal_satin 为基于 5★ 结构 + 既有色域的现实重映射，凑足 4-6 档真实柜体配色。
