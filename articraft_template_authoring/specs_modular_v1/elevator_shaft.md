# Modular Spec — elevator_shaft (freestanding shaft/car elevator)

## 元信息
| 项 | 值 |
|---|---|
| slug | `elevator_shaft` |
| template path | `agent/templates/elevator_shaft.py` |
| test path (optional) | `tests/agent/test_elevator_shaft_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：主链是 `hoist_structure --PRISMATIC z--> car --(slide/swing)--> portal` 的线性升降链；在 hoist 与 car 上挂若干 **parallel optional children**（counterweight、sheave wheel、safety accessory），并带 multiplicity（门扇数、缆绳数、guide shoe 对数、landing door 层数）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 39 |
| read_count | 39 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

读取方式：全部 39 个 5 星样本的 `model.py` / `prompt.txt` / `record.json`（rating=5）逐个完整阅读，未抽样。类别评分分布：5★=39、4★=10、2★=1（共 50 条 retained record）。下表只索引被采纳的 module source；已阅读但未采纳的样本不进入 source 表。

## 核心身份

elevator 的不变身份：**一个沿竖直轴 (axis=(0,0,1)) 做 PRISMATIC 升降的轿厢/平台（car / cage / platform），被一个固定的导向/井道结构（hoist structure）约束并支撑；轿厢通过 guide shoe 与 hoist 的 guide rail 持续接触；通常带一个可开启的门/闸（portal），可选地带配重（counterweight）、驱动可视件（sheave/ropes、hydraulic ram、lead screw、rack）与安全副自由度（折叠扶手/护膝板/安全臂/安全爪）。**

最小合法 elevator = `hoist_structure` (fixed root) + `car` (PRISMATIC vertical child) + 至少 1 个可动 portal **或** 1 个安全副自由度（platform 型无门时必须有护膝板/安全臂等 1 个 REVOLUTE 件，避免退化成纯单 DOF 升降台）。

默认成熟域：建筑/工业升降设备 —— 客梯、医用担架梯、住宅家用梯、观光玻璃梯、货梯/平台货梯、矿井提升 cage、单柱无障碍/车辆举升平台、dumbwaiter。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：hoist_structure（固定根，井道/导向结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| enclosed_walled_shaft | rec_elevator_0002 | L65-L150 | eligible if compatible | 3 面实心墙(left/right/back) + pit floor + top slab + front header + 2 guide rail + machine beam，封闭井道；前面开门洞 |
| open_post_frame | rec_elevator_656f095480b4445ab40f6b044b3630f1 | L56-L122 | eligible if compatible | 4 角柱 + 4 top beam + base slab + 2 guide rail，无墙开放框架；前后左右通透 |
| single_column_mast | rec_elevator_bd64f5d6eda042a5ad6efc9f309646f1 | L26-L58 | eligible if compatible | 单根中柱 post + 单 guide rail + top cap + anchor bolt，悬臂单柱（无障碍/车辆/平台举升） |
| rear_column_mast | rec_elevator_b61417793eaa416683a0230851623741 | L104-L200 | eligible if compatible | 后置立柱塔（2 角柱 + 多层横撑 + 2 guide rail + machine head），轿厢沿后柱上行；适配货梯/螺杆/齿条 |
| cylindrical_glass_tower | rec_elevator_fd6c0a3686814c919aba13762eb2db68 | L148-L216 | eligible if compatible | 圆形玻璃塔：annular glass tube(_annular_tube mesh) + 2 clamp ring + head cap + 6 mullion(60°) + 2 guide rail |

### Slot B：drive_suspension（驱动/悬挂可视件，挂在 hoist 上；部分含可动 counterweight/sheave 子件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| traction_sheave_ropes | rec_elevator_0002 | L114-L150 | eligible if compatible | machine beam + drive sheave(Cylinder) + N 根 rope(Cylinder loop) + counterweight block + 2 counterweight rail，曳引可视组 |
| traction_with_counterweight_part | rec_elevator_fb7c46fd8170425bba69b8ce31e400c8 | frame L61-L72 + counterweight part L108-L115 | eligible if compatible | head sheave + axle + 独立 `counterweight` part（自带 4 guide shoe），走单独 PRISMATIC（与 car 反向 / mimic） |
| revolute_sheave_wheel | rec_elevator_75a6c8b0f9a44cf3a37fb522285ceeab | sheave part L122-L145 + axle joint L164-L172 | eligible if compatible | 头架可见 grooved sheave wheel（WheelGeometry），独立 part，REVOLUTE axle (axis=(1,0,0)) 连续旋转 |
| hydraulic_ram | rec_elevator_7fd47ce89862490a8f9b3b3f35a2859a | jack sleeve L185-L251 + ram L290-L291 | eligible if compatible | 车下 hydraulic jack sleeve(hollow) + piston ram(Cylinder)，液压顶升，无 counterweight |
| lead_screw_drive | rec_elevator_c6b984673c6a4088aacbc72b92dc53f7 | screw mesh L146-L155 + nut block L233-L240 | eligible if compatible | tower 旁可见 lead screw（_lead_screw_mesh 螺旋）+ car 上 drive nut block，螺杆驱动 |
| rack_and_pinion | rec_elevator_035bb14ec86b429cb8bbd9a147918e7c | rack teeth L78-L86 + pinion cover L180-L187 | eligible if compatible | 后柱 rack spine + N 齿(loop) + car 上 pinion cover，齿条驱动 |
| implicit_none | rec_elevator_9b38667c118b423390acce9ee5f0e974 | (无驱动可视件；frame L26-L54) | eligible if compatible | 不建模驱动件，仅 PRISMATIC 升降语义（住宅/观光常见）；作为 fallback |

### Slot C：car_body（被升降的可动主件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| enclosed_rectangular_cab | rec_elevator_0002 | L152-L254 | eligible if compatible | 实心 floor/roof/3 wall + 门框(jamb/header/threshold/top track) + 4 guide shoe + handrail，客梯封闭轿厢 |
| glass_cab_rectangular | rec_elevator_2f2b5d4786fa4a0ab086fd0cb2f28465 | L141-L248 | eligible if compatible | 钢框 + 3 面玻璃墙 + 门框 + 4 guide shoe，矩形观光轿厢 |
| glass_cab_curved | rec_elevator_5ef65550be264a2a90f25346b9b8f927 | L161-L286 | eligible if compatible | 圆/弧形 floor pan + curved glass(_curved_panel_mesh/section_loft) + jamb/track + 4 guide shoe，弧形观光轿厢 |
| open_cage | rec_elevator_f9dee4aff1164cbe8333571ee72728cd | L84-L142 | eligible if compatible | floor + 4 角柱 + 周边 rail + wire-mesh 面(loop) + 4 guide shoe，开放钢笼（矿井/工业货） |
| flat_platform | rec_elevator_bd64f5d6eda042a5ad6efc9f309646f1 | L60-L151 | eligible if compatible | 开放 deck + nonskid + 边沿 lip + carriage frame + guide shoe，无墙无顶平台（无障碍/车辆/平台货） |

### Slot D：portal（门/闸，car 或 shaft 的可动子件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| center_opening_slide | rec_elevator_0002 | doors L256-L292 + joints L308-L335 | eligible if compatible | 双扇对开 PRISMATIC，axis=(±1,0,0)；hanger 挂 top track + guide 落 threshold；闭合中缝相接 |
| single_panel_slide | rec_elevator_2f2b5d4786fa4a0ab086fd0cb2f28465 | door L265-L301 + joint L302-L315 | eligible if compatible | 单扇侧滑 PRISMATIC；玻璃/钢门扇 + hanger + guide |
| swing_hinged_leaves | rec_elevator_6e47f388da8448d5aa185fda8cb7dff5 | leaves L244-L282 + joints L284-L301 | eligible if compatible | 单/双扇外摆 REVOLUTE，axis=(0,0,±1)，hinge barrel 在门框边；bifold 变体见 c6b98467 L265-L344 |
| sliding_cage_gate | rec_elevator_9e2b821a72f74750bfc76801bca3bc72 | gate L78-L96 + joint L107-L115 | eligible if compatible | 笼门单闸横滑 PRISMATIC，axis=(1,0,0)，top/bottom roller track；工业开放笼 |
| swing_cage_gate | rec_elevator_f9dee4aff1164cbe8333571ee72728cd | gate L152-L180 + joint L191-L199 | eligible if compatible | 笼门 REVOLUTE 外摆，hinge knuckle 贯穿 pin；wire-mesh/栅栏门扇 |
| folding_leaf_gate | rec_elevator_fb7c46fd8170425bba69b8ce31e400c8 | leaves L116-L127 + joints L149-L166 | eligible if compatible | 双叶折叠闸 REVOLUTE，axis=(0,0,±1)，中缝相接；货梯平台常见（_build_gate_leaf helper） |

注：landing/hatch 型门（挂在 **shaft** 而非 car，按楼层 N 复制）属 swing_hinged_leaves 的 placement 变体，见 Multiplicity 节（rec_7fd47ce8 lobby door L293-L322 + L338-L365；rec_8b3ff680/ba879bf8 hatch）。

### Slot E：safety_accessory（可选副自由度，car/platform 的 REVOLUTE 子件；默认 none）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none | — | — | eligible if compatible | 不挂副自由度（多数封闭客梯/观光梯） |
| folding_handrail | rec_elevator_656f095480b4445ab40f6b044b3630f1 | rails L282-L330 + joints L346-L373 | eligible if compatible | car 内壁折叠扶手，REVOLUTE，axis=(0,0,±1)，pin 落 handrail post；弧形版见 5ef65550 L322-L405 |
| knee_guard_or_lip | rec_elevator_bd64f5d6eda042a5ad6efc9f309646f1 | guard L153-L189 + joint L200-L208 | eligible if compatible | platform 前缘折叠护膝板 / 门槛安全 lip，REVOLUTE，axis=(±1,0,0)；lip 变体见 2f2b5d47 L317-L349 |
| folding_safety_arms | rec_elevator_0cad93cce14144738c41a62c21273d10 | arms L291-L321 + joints L345-L372 | eligible if compatible | platform 两侧折叠安全臂，2× REVOLUTE，axis=(±1,0,0)，0→~π/2 立起 |
| safety_pawl | rec_elevator_035bb14ec86b429cb8bbd9a147918e7c | arm L227-L245 + joint L275-L288 | eligible if compatible | 安全爪/catch arm，REVOLUTE，axis=(0,-1,0) 小角度；矿井 cage 也用（5d3e5690 L132-L145） |

硬约束确认：每个 slot ≥3 候选（E 含 none 共 5）。所有 candidate 均有真实 5 星 `model.py:Lx-Ly` 来源；candidate 间是 part tree / joint 拓扑 / primitive / interface 差异，非颜色/尺寸/材质差异。

## 槽位图（slot graph）

pattern: mixed

```
[Slot A] hoist_structure (fixed root)
   │
   ├─[PRISMATIC car_lift; axis=(0,0,1); origin=car_rest; guide_shoe⇄guide_rail contact; range 0..car_travel]
   │      ▼
   │   [Slot C] car_body
   │      │
   │      ├─[Slot D portal; PRISMATIC(±1,0,0)/REVOLUTE(0,0,±1) ; hanger⇄top_track + guide⇄threshold | hinge barrel⇄jamb]
   │      │      ▼  portal panel(s)  (×door_panel_count)
   │      │
   │      └─[Slot E accessory; REVOLUTE; pin⇄post / hinge⇄edge]  (optional)
   │             ▼  safety_accessory  (optional)
   │
   ├─[PRISMATIC counterweight_lift; axis=(0,0,-1) or mimic(car); cw guide_shoe⇄cw rail]   (optional, drive-gated)
   │      ▼
   │   counterweight part
   │
   ├─[REVOLUTE sheave_axle; axis=(1,0,0); -π..π]   (optional, drive-gated)
   │      ▼
   │   sheave_wheel part
   │
   └─[REVOLUTE/FIXED landing_door × N_floors; mounted on hoist (shaft)]   (optional, see Multiplicity)
          ▼
       landing_door part(s)
```

接口点位与跨 slot joint：

- **A→C（car_lift，恒存在）**：PRISMATIC，axis=(0,0,1)。接口=car 的 `guide_shoe`（每侧上下各 1，共 4）与 hoist 的 `guide_rail` 持续 contact（`expect_contact`，全行程保持）。origin 在轿厢静止位；`range=0..car_travel`。car 在 hoist 平面内 `expect_within`（xy），顶部 `expect_gap`(car_roof ↔ top_slab) 防越界。
- **C→D（portal）**：滑动门=PRISMATIC，axis=(±1,0,0)（少量样本沿 (0,±1,0) 前向滑入 pocket，见 e1f10dac/e771c7ec）；接口=门扇 `hanger`⇄car `top_track`（顶吊）+ 门扇 `guide`⇄car `threshold/sill`（底导），闭合时双扇中缝 `expect_gap(max≈0)`。摆门=REVOLUTE，axis=(0,0,±1)，hinge barrel 贴 jamb。
- **A/C→landing_door**：挂在 **shaft**（非 car）的层门，REVOLUTE 或 FIXED，按楼层放置（见 Multiplicity）。
- **A→counterweight（drive-gated）**：PRISMATIC，axis=(0,0,-1) 或对 car_lift 做 mimic（multiplier=-1）；接口=counterweight guide shoe⇄counterweight rail。仅 traction 驱动且 hoist 侧有空间时存在。
- **A→sheave_wheel（drive-gated）**：REVOLUTE，axis=(1,0,0)，range=-π..π 连续。仅 traction（曳引/绳）。
- **C→safety_accessory（optional）**：REVOLUTE，接口=accessory pin/hinge⇄car post/edge。

互斥/可选/派生：

- counterweight、revolute_sheave_wheel 由 Slot B（traction 家族）派生；非 traction 驱动不得出现 counterweight/sheave。
- landing_door 与 car-mounted portal 互斥或叠加需谨慎：dumbwaiter/液压家用梯用 **shaft landing door**（car 本身无门）；客梯用 **car portal**。默认二选一。
- flat_platform（C5）无门框，不能配 center_opening_slide/single_panel_slide/swing_hinged_leaves；只能配 sliding_cage_gate / folding_leaf_gate / none，且必须带 Slot E（护膝板/安全臂）以保证 ≥2 DOF 且非退化。
- cylindrical_glass_tower（A4）派生 glass_cab_curved（C3）。

## 每槽位 Module Emits / Interfaces

### Slot A / module enclosed_walled_shaft
| emits | 描述 | 来源 |
|---|---|---|
| parts | pit_floor, left/right/back wall, top_slab, front_header, left/right guide_rail, (machine_beam) | rec_0002 / model.py:L65-L150 |
| internal joints | 无（固定根，单 part 多 visual） | rec_0002 / model.py:L65-L150 |
| upstream interface | root（无 parent） | rec_0002 / model.py:L65-L150 |
| downstream interface | guide_rail（左右）供 car guide shoe 接触；car_lift origin 落 pit 上方 | rec_0002 / model.py:L102-L113, L294-L307 |

### Slot A / module open_post_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | base slab, 4 corner post, 4 top beam, 2 guide_rail | rec_656f0954 / model.py:L56-L122 |
| upstream interface | root | rec_656f0954 / model.py:L56-L122 |
| downstream interface | guide_rail 供 car guide shoe；开放无墙 | rec_656f0954 / model.py:L109-L115 |

### Slot A / module single_column_mast
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor base plate, 中柱 post, 单 guide rail, top cap, 4 anchor bolt | rec_bd64f5d6 / model.py:L26-L58 |
| downstream interface | 单 guide rail 供 platform carriage 接触；axis=(0,0,1) | rec_bd64f5d6 / model.py:L39-L44, L191-L199 |

### Slot A / module rear_column_mast
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2 base beam, 2 rear corner post, 多层 crossbrace, 2 guide rail, machine head | rec_b61417793 / model.py:L104-L200 |
| downstream interface | guide_rail 供 car/cage guide shoe；machine head 供 sheave/screw/rack 安装 | rec_b61417793 / model.py:L154-L188 |

### Slot A / module cylindrical_glass_tower
| emits | 描述 | 来源 |
|---|---|---|
| parts | round plinth, annular glass tube(mesh), 2 clamp ring, head cap, 6 mullion, 2 guide rail | rec_fd6c0a36 / model.py:L148-L216 |
| internal helpers | `_annular_tube`（旋成圆环柱面） | rec_fd6c0a36 / model.py:L19-L57 |
| downstream interface | 2 guide rail（前向）供 car guide shoe | rec_fd6c0a36 / model.py:L210-L216 |

### Slot C / module enclosed_rectangular_cab
| emits | 描述 | 来源 |
|---|---|---|
| parts | car_floor, car_roof, 3 wall, left/right jamb, door_header, threshold, top_track, 4 guide_shoe, handrail | rec_0002 / model.py:L152-L254 |
| upstream interface | guide_shoe ⇄ hoist guide_rail（car_lift child） | rec_0002 / model.py:L225-L248 |
| downstream interface | top_track + threshold 供门 hanger/guide；jamb 供门闭合贴合 | rec_0002 / model.py:L183-L224 |

### Slot C / module glass_cab_rectangular
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor, roof, 4 corner stile, 3 glass wall, front header/sill, 4 guide_shoe | rec_2f2b5d47 / model.py:L141-L248 |
| downstream interface | front header/sill 供单扇滑门 track | rec_2f2b5d47 / model.py:L197-L243 |

### Slot C / module glass_cab_curved
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor pan, roof pan, rear spine, left/right jamb, top_track, sill_track, curved glass panel(mesh), handrail post | rec_5ef65550 / model.py:L161-L286 |
| internal helpers | `_curved_panel_mesh`/`section_loft` | rec_5ef65550 / model.py:L24-L99 |
| upstream interface | rear_spine ⇄ tower guide_rail（座于导轨，`expect_gap`/`expect_overlap`） | rec_5ef65550 / model.py:L181-L197 |

### Slot C / module open_cage
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor plate, 4 corner post, 周边 top/bottom rail, wire-mesh 面(loop), 4 guide shoe+web, rubber roller | rec_f9dee4af / model.py:L84-L142 |
| internal helpers | wire-mesh 由小 box/cylinder loop 生成 | rec_f9dee4af / model.py:L100-L112 |
| downstream interface | hinge mount strip + 3 fixed hinge knuckle 供 swing/sliding gate | rec_f9dee4af / model.py:L130-L142 |

### Slot C / module flat_platform
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck, nonskid top, 边沿 lip, carriage frame/cheek, underside rib, hinge knuckle+pin | rec_bd64f5d6 / model.py:L60-L151 |
| upstream interface | carriage frame ⇄ column guide rail（margin check） | rec_bd64f5d6 / model.py:L92-L108 |
| downstream interface | 前缘 hinge knuckle+pin 供 Slot E 护膝板/安全臂（**platform 必须带 E**） | rec_bd64f5d6 / model.py:L123-L151 |

### Slot D / module center_opening_slide
| emits | 描述 | 来源 |
|---|---|---|
| parts | left_door/right_door = panel + hanger + guide（×2 扇） | rec_0002 / model.py:L256-L292 |
| internal joints | car_to_left_door / car_to_right_door PRISMATIC axis=(±1,0,0) range±door_travel | rec_0002 / model.py:L308-L335 |
| upstream interface | hanger ⇄ top_track；guide ⇄ threshold；闭合中缝 panel⇄panel | rec_0002 / model.py:L262-L292 |

### Slot D / module single_panel_slide
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 door = glass/钢 pane + stiles + rails + hanger/guide | rec_2f2b5d47 / model.py:L265-L301 |
| internal joints | car_to_door PRISMATIC axis=(1,0,0)（或 y 前滑） | rec_2f2b5d47 / model.py:L302-L315 |

### Slot D / module swing_hinged_leaves
| emits | 描述 | 来源 |
|---|---|---|
| parts | 1-2 leaf = panel + hinge barrel + pull（bifold 加 inner panel） | rec_6e47f388 / model.py:L244-L282 |
| internal joints | REVOLUTE axis=(0,0,±1)；bifold 二级 REVOLUTE | rec_6e47f388 / model.py:L284-L301 |

### Slot D / module sliding_cage_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | gate = top/bottom bar + side bar + N vertical bar + hanger + shoe + roller | rec_9e2b821a / model.py:L78-L96 |
| internal joints | cage_to_gate PRISMATIC axis=(1,0,0) | rec_9e2b821a / model.py:L107-L115 |

### Slot D / module swing_cage_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | gate = hinge/latch stile + rails + wire-mesh/bar 面 + 2 hinge knuckle + pin | rec_f9dee4af / model.py:L152-L180 |
| internal joints | cage_to_gate REVOLUTE axis=(0,0,±1) | rec_f9dee4af / model.py:L191-L199 |

### Slot D / module folding_leaf_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf_0/leaf_1 = hinge stile + latch stile + rails + infill bar（_build_gate_leaf） | rec_fb7c46fd / model.py:L116-L127 |
| internal joints | platform_to_leaf_0/1 REVOLUTE axis=(0,0,±1)，中缝相接 | rec_fb7c46fd / model.py:L149-L166 |

### Slot E / module folding_handrail
| emits | 描述 | 来源 |
|---|---|---|
| parts | left/right grab rail = pin + bar | rec_656f0954 / model.py:L282-L330 |
| internal joints | car_to_grab_rail REVOLUTE axis=(0,0,±1)，pin⇄car post | rec_656f0954 / model.py:L346-L373 |

### Slot E / module knee_guard_or_lip
| emits | 描述 | 来源 |
|---|---|---|
| parts | center knuckle + guard leaf + guard panel + top bumper + side frame | rec_bd64f5d6 / model.py:L153-L189 |
| internal joints | platform_to_knee_guard REVOLUTE axis=(±1,0,0) 0..π/2 | rec_bd64f5d6 / model.py:L200-L208 |

### Slot E / module folding_safety_arms
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2× arm = hinge barrel + leaf + arm tube + end lug | rec_0cad93cc / model.py:L291-L321 |
| internal joints | platform_to_arm_0/1 REVOLUTE axis=(±1,0,0) | rec_0cad93cc / model.py:L345-L372 |

### Slot E / module safety_pawl
| emits | 描述 | 来源 |
|---|---|---|
| parts | catch arm body + tip | rec_035bb14e / model.py:L227-L245 |
| internal joints | car_to_pawl REVOLUTE axis=(0,-1,0) 小角度 | rec_035bb14e / model.py:L275-L288 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| hoist_choice (A) | enum | enclosed_walled_shaft / open_post_frame / single_column_mast / rear_column_mast / cylindrical_glass_tower | sampled | deterministic procedural sampler | Slot A table |
| drive_choice (B) | enum | traction_sheave_ropes / traction_with_counterweight_part / revolute_sheave_wheel / hydraulic_ram / lead_screw_drive / rack_and_pinion / implicit_none | sampled | 受 hoist_choice 经 compatibility matrix gating | Slot B table |
| car_choice (C) | enum | enclosed_rectangular_cab / glass_cab_rectangular / glass_cab_curved / open_cage / flat_platform | sampled | 受 hoist_choice gating | Slot C table |
| portal_choice (D) | enum | center_opening_slide / single_panel_slide / swing_hinged_leaves / sliding_cage_gate / swing_cage_gate / folding_leaf_gate / none | sampled | 受 car_choice gating | Slot D table |
| accessory_choice (E) | enum | none / folding_handrail / knee_guard_or_lip / folding_safety_arms / safety_pawl | sampled | 受 car_choice gating；platform 强制非 none | Slot E table |
| door_panel_count | int (multiplicity) | 1 或 2 | 由 portal_choice 派生 | center_opening/folding_leaf=2；single/swing/cage 多为 1 | rec_0002 L256-L292 / rec_2f2b5d47 L265 |
| rope_count | int (multiplicity) | 2-4 | 2 | 仅 traction；hoist 顶部沿 x 排布 | rec_0002 L126-L132 |
| guide_rail_count | int | 2（cage/平台 2；单柱 1） | 2 | 由 hoist_choice 派生 | rec_0002 L102-L113 |
| guide_shoe_pairs | int (multiplicity) | 每侧上下各 1 → 4 | 4 | car_lift 接口；single_column 可 2 | rec_0002 L225-L248 |
| landing_door_floors | int (multiplicity) | 0,2,3 | 0 | dumbwaiter/液压家用梯按楼层复制 shaft 门 | rec_7fd47ce8 L293-L322 |
| car_travel | float | [0.75, 8.0] | 由 hoist 高度派生 | car_lift upper；clamp≤hoist 内净高 | rec_0002 L301-L307 / rec_e452 L259-L267 |
| door_travel | float | [0.21, 0.86] | ≈门洞半宽(对开) / 门洞宽(单扇) | clamp 使开足且不出框 | rec_0002 L313-L335 |
| support_width_scale | float | [0.9, 1.15] | 1.0 | hoist/car 平面尺寸安全缩放（见受控局部参数化） | resolve_config clamp |
| car_height_scale | float | [0.92, 1.1] | 1.0 | car 高度，clamp≤hoist 净高-顶隙 | resolve_config clamp |
| rail_gauge_scale | float | [0.95, 1.1] | 1.0 | guide rail 间距，与 guide shoe 联动派生 | resolve_config clamp |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量与 palette；未实现拓扑不进 enum。

## Multiplicity / Copy Logic

elevator 含多处模板级复制逻辑：

**(1) door_panel_count**
- count_param：`door_panel_count`
- N_range：{1, 2}
- sampling domain：由 portal_choice 派生 —— center_opening_slide / folding_leaf_gate → 2；single_panel_slide / swing_cage_gate / sliding_cage_gate → 1；swing_hinged_leaves → 1 或 2（bifold 视为 2 叶）。
- copied object：门扇 part（panel + hanger/guide 或 hinge barrel）
- naming：`left_door`/`right_door` 或 `door_0`/`door_1` 或 `gate_leaf_0`/`gate_leaf_1`
- placement：对开两扇镜像于门洞中线；折叠两叶镜像
- joint policy：每扇独立 joint，axis 互为相反号（+/-）；闭合中缝 `expect_gap(max≈0)`
- source/gating：rec_0002 L256-L335；rec_fb7c46fd L116-L166；单扇 rec_2f2b5d47 L265-L315

**(2) rope_count（traction 派生）**
- count_param：`rope_count`，N_range=2..4，仅 traction_sheave_ropes
- copied object：rope Cylinder（细长）
- placement：hoist 顶 sheave 下沿 x 等距排布
- joint policy：静态可视件，无 joint
- source/gating：rec_0002 L126-L132（loop start=1 of 4）

**(3) guide_shoe_pairs / guide_rail_count**
- guide_shoe：每侧上下各 1（共 4），single_column 可降至 2
- copied object：guide shoe box（car 上），guide rail box（hoist 上）
- placement：left/right × lower/upper；与 rail_gauge 派生联动
- joint policy：通过 car_lift 接口与 rail `expect_contact`，全行程保持
- source/gating：rec_0002 L225-L248；rec_656f0954 L207-L218（nested loop）

**(4) landing_door_floors（可选）**
- count_param：`landing_door_floors`，N_range={0,2,3}
- sampling domain：仅 dumbwaiter（flat/box car 无门）或液压家用梯启用；客梯=0
- copied object：层门 part（挂 **shaft**）
- naming：`lower_lobby_door`/`upper_lobby_door` 或 `lower_hatch`/`upper_hatch`
- placement：按楼层 z（landing 高度）放置于 shaft 前面门洞
- joint policy：每层门独立 REVOLUTE（lobby）或 REVOLUTE 水平铰（hatch）；origin 在该层 hinge 边
- source/gating：rec_7fd47ce8 L293-L365；rec_ba879bf8 L108-L132；rec_8b3ff680 L297-L324

**(5) counterweight / sheave_wheel（drive 派生，非纯数量但属可选复制件）**
- counterweight：0 或 1，仅 traction 家族且 hoist 有侧向空间（enclosed_shaft / open_frame / rear_mast）
- sheave_wheel：0 或 1 REVOLUTE 件，仅 traction
- source/gating：rec_fb7c46fd L108-L166；rec_75a6c8b0 L122-L172

**(6) cage baluster / wire-mesh density（open_cage 内部）**
- open_cage 的 mesh/baluster 由 loop 生成（rec_f9dee4af L100-L112），属 module-local 受控密度，不作主多样性轴。

## 拓扑多样性审计

总组合数（先按 compatibility matrix 合法化后估算）：

- 朴素叉乘 A(5) × B(7) × C(5) × D(7) × E(5) = 6125，但绝大多数被 compatibility matrix 裁掉。
- 合法组合（按下方矩阵粗估）：
  - 客梯族：enclosed_shaft/open_frame/glass_tower × {traction*/implicit} × {rect_cab/glass_cab*} × {center_open/single_slide/swing} × {none/handrail/lip} ≈ 3×3×3×3×3 去非法 ≈ **120+**
  - 货梯/矿井族：{open_frame/enclosed_shaft/rear_mast} × {traction*/implicit} × {open_cage/flat_platform} × {cage_gate*/folding_leaf/none} × {none/arms/pawl/lip} ≈ **80+**
  - 单柱平台族：single_column_mast × {hydraulic/implicit} × flat_platform × {none/sliding} × {knee_guard/arms} ≈ **15+**
  - 螺杆/齿条 rear_mast 族：rear_mast × {lead_screw/rack} × {rect_cab/open_cage} × {swing/single_slide} × {none/handrail} ≈ **20+**

理由：仅 Slot A×C×D 三轴在合法子集内就远超 10 个 distinct 拓扑等价类（不同 part tree / joint 拓扑 / chain depth：滑门 PRISMATIC vs 摆门 REVOLUTE vs 折叠双 REVOLUTE vs 笼闸；带/不带 counterweight 第二 PRISMATIC；带/不带 sheave REVOLUTE；带/不带 accessory REVOLUTE；landing door 复制数）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 用 deterministic procedural sampling：先 `rng` 选 hoist_choice → 经 compatibility matrix 得 drive/car 的合法子集再选 → 由 car_choice 得 portal/accessory 合法子集再选 → 派生 door_panel_count / counterweight / sheave / landing_door_floors / 连续 scale。`seed=0` 不特殊。所有非法组合由 compatibility matrix + `resolve_config` clamp 拦截，sampler 只输出已实现且可装配组合。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 hoist×car×portal 家族至少 1 例（尤其闭合姿态门中缝、全行程 guide shoe 接触、counterweight 反向、platform 必带 accessory 不退化）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别合法组合估计 ≥200，预期可达。
regression overrides：初版默认 none；若 sweep 暴露特定失败组合（如某 glass_tower×swing 门 closed-pose 穿模）再以稀疏、显式 + 失败回归理由加入，不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入少量关键连续 scale —— `support_width_scale [0.9,1.15]`（hoist/car 平面）、`car_height_scale [0.92,1.1]`、`rail_gauge_scale [0.95,1.1]`（与 guide shoe 派生联动）、`car_travel`（clamp≤hoist 净高-顶隙）、`door_travel`（clamp 使开足不出框）。全部在 `resolve_config` 中 clamp / 派生，受 guide-shoe⇄rail 接触、门 hanger/threshold 接触、顶部 `expect_gap`、closed-pose 中缝约束；不改变 slot/module 选择、door_panel_count、counterweight 存在性等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | hoist→drive→car→portal→accessory 顺序选择 + 每步 compatibility gate；weighted（客梯族权重高，单柱/螺杆族低频但保留） | slot_choices_for_seed matches build choices |
| compatibility matrix | 见下“兼容矩阵”：traction↔counterweight/sheave 绑定；platform↔无门框门类禁用且强制 accessory；glass_tower↔curved_cab 绑定；hydraulic↔single_column/platform；screw/rack↔rear_mast | no floating（counterweight/sheave/accessory 不漂浮）、collision（closed door 中缝、cage gate）、axis（car_lift z、door ±x、sheave x）、max multiplicity（rope≤4、landing≤3）、bulky module（wide hospital car 不超 hoist 平面）、optional child（accessory/counterweight 缺省安全） |
| controlled local variation | support_width_scale / car_height_scale / rail_gauge_scale / car_travel / door_travel，全 clamp | 比例变化不破坏 guide-shoe 接触、门 hanger/threshold 接触、顶部隙、closed 中缝、joint origin、类别身份 |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/contact/closed-pose） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A hoist_structure | 5 | yes | yes | |
| B drive_suspension | 7 | yes | yes | 含 implicit_none fallback |
| C car_body | 5 | yes | yes | |
| D portal | 7 | yes | yes | 含 none |
| E safety_accessory | 5 | yes | yes | 含 none |

兼容矩阵（合法 / 互斥 / fallback）：

- traction_sheave_ropes / traction_with_counterweight_part / revolute_sheave_wheel ⇒ 仅当 hoist ∈ {enclosed_walled_shaft, open_post_frame, rear_column_mast}（cylindrical_glass_tower 可带轻 traction，但 counterweight 默认关）；single_column_mast 禁 counterweight/曳引。
- hydraulic_ram ⇒ hoist ∈ {single_column_mast}，car ∈ {flat_platform, enclosed_rectangular_cab(slim)}，禁 counterweight。
- lead_screw_drive / rack_and_pinion ⇒ hoist=rear_column_mast，car ∈ {enclosed_rectangular_cab, open_cage}，禁 counterweight。
- implicit_none ⇒ 任意 hoist/car 合法（fallback）。
- cylindrical_glass_tower ⇒ car=glass_cab_curved（绑定）。
- glass_cab_rectangular ⇒ hoist ∈ {open_post_frame, enclosed_walled_shaft}；portal ∈ {single_panel_slide, center_opening_slide}。
- open_cage ⇒ portal ∈ {sliding_cage_gate, swing_cage_gate, folding_leaf_gate}；accessory ∈ {none, safety_pawl}。
- flat_platform ⇒ portal ∈ {none, sliding_cage_gate, folding_leaf_gate}；**accessory 必须 ∈ {knee_guard_or_lip, folding_safety_arms}（禁 none，避免退化单 DOF）**。
- enclosed_rectangular_cab / glass_cab_* ⇒ portal ∈ {center_opening_slide, single_panel_slide, swing_hinged_leaves}；accessory ∈ {none, folding_handrail, knee_guard_or_lip}。
- landing_door_floors>0 ⇒ car portal=none 且 car ∈ {flat_platform(box)/enclosed cab}（dumbwaiter/液压家用梯）。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D/E 五元组 + 派生 count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（traction↔counterweight/sheave、platform↔门框门类禁用且强制 accessory、glass_tower↔curved_cab、hydraulic↔single_column、screw/rack↔rear_mast）
- optional regression overrides are sparse and justified（初版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (support_width_scale/car_height_scale/rail_gauge_scale/car_travel/door_travel) are clamped；不破坏 guide-shoe⇄rail 接触、门 hanger/threshold 接触、顶部隙、closed 中缝、joint origin、类别 multiplicity
- critical InterfaceSpec / MatingContract points exist：guide_shoe⇄guide_rail（全行程）、door hanger⇄top_track + guide⇄threshold、closed 双扇中缝 gap≈0、counterweight guide_shoe⇄cw rail、accessory pin/hinge⇄car post/edge
- key joints have expected type/axis/range：car_lift PRISMATIC axis=(0,0,1) range 0..car_travel；门 PRISMATIC axis=(±1,0,0) 或 REVOLUTE axis=(0,0,±1)；counterweight PRISMATIC axis=(0,0,-1)/mimic；sheave REVOLUTE axis=(1,0,0) -π..π；accessory REVOLUTE
- copied objects follow naming/placement policy（left/right 或 _0/_1 镜像；rope 等距；landing door 按楼层 z）
- platform 型至少 2 DOF（car_lift + 1 accessory），不退化为纯升降台
- 玻璃/实心轿厢前面门洞处不得被不透明壳完全封死（运动件必须可见，参 [[feedback_enclosed_mechanism_open_front]]）

## Reject cases

- 把只换尺寸/颜色/玻璃透明度的样本当独立 candidate（如把 rect-cab 调宽当“hospital cab”新 module）。
- car 沿 z 升降但缺 guide_shoe⇄guide_rail 接触，轿厢在井道里漂浮（违反 fail_if_isolated_parts）。
- 对开双扇 closed pose 中缝穿模或留大缝（缺 `expect_gap(max≈0)`）。
- counterweight/sheave 出现在非 traction 驱动，或 counterweight 无独立 guide rail 漂浮。
- flat_platform 配 center_opening_slide/single_panel_slide（无门框可挂 hanger/track）→ 门漂浮。
- flat_platform 既无门又无 accessory → 退化成单 DOF 升降台（非 articulated elevator 身份）。
- cylindrical_glass_tower 配矩形/实心轿厢（圆塔内矩形轿厢穿模/不匹配）。
- 把 sheave wheel 的 REVOLUTE 连续旋转误设为 PRISMATIC，或 car_lift 轴设成非 z。
- 第二自由度（accessory/counterweight）几何不连贯（铰点不接触、臂悬空）却靠 sweep pass 蒙混 —— 必须 viewer 目检，不连贯就砍掉退回单门 DOF（参 [[feedback_gated_aux_geometry_coherence]]）。
- 把 mesh profile（curved glass / annular tube / lead screw）沿轴摆放当作居中，导致几何多伸（参 [[feedback_mesh_profile_origin_pitfall]]）。
- 仅在 joint=0 rest pose 验门开合方向 —— 改 door/accessory axis 符号必须 pose 到 upper/lower 实测 AABB（参 [[project_sweep_only_rest_pose]]）。

## 与相邻类别的边界

- 不该混入：`crane_tower` / `telescoping_boom`（起重臂回转/伸缩，非井道内竖直升降轿厢；elevator 的载体是被导轨约束的 car/cage，主轴恒为 (0,0,1) PRISMATIC）。
- 不该混入：`standing_desk_with_synchronous_telescoping_legs`（同步伸缩腿是嵌套 PRISMATIC 链，非单一 car 在固定 hoist 内升降）。
- 不该混入：`drawer_cabinet_with_sliding_drawers`（抽屉是水平 PRISMATIC，无竖直 hoist 主轴与 guide-shoe⇄rail 接触契约）。
- 不该混入：`parabolic_dish_on_azimuth_elevation_mount` / 各类 pan-tilt（俯仰/方位 REVOLUTE 为主，无竖直行程载体）。
- 不该混入：`barrier_gate` / `turnstile_gates`（仅一个摆/转门，无升降轿厢主体）—— elevator 的门只是 portal 子件，主身份是升降。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | enclosed_walled_shaft | rec_elevator_0002 | L65-L150 | shaft part tree + guide rail downstream interface |
| S2 | A | open_post_frame | rec_elevator_656f0954…b3630f1 | L56-L122 | 4-post 开放框架 + 2 rail |
| S3 | A | single_column_mast | rec_elevator_bd64f5d6…309646f1 | L26-L58 | 单柱 + 单 rail + anchor |
| S4 | A | rear_column_mast | rec_elevator_b6141779…0851623741 | L104-L200 | 后柱塔 + machine head 安装面 |
| S5 | A | cylindrical_glass_tower | rec_elevator_fd6c0a36…62eb2db68 | L148-L216 + helper L19-L57 | 圆玻璃塔 + mullion + annular mesh |
| S6 | B | traction_sheave_ropes | rec_elevator_0002 | L114-L150 | sheave+ropes(loop)+counterweight 可视组 |
| S7 | B | traction_with_counterweight_part | rec_elevator_fb7c46fd…31e400c8 | L61-L72 + L108-L115 | head sheave + 独立 counterweight part |
| S8 | B | revolute_sheave_wheel | rec_elevator_75a6c8b0…285ceeab | L122-L145 + L164-L172 | 可见 sheave wheel + REVOLUTE axle |
| S9 | B | hydraulic_ram | rec_elevator_7fd47ce8…35a2859a | L185-L251 + L290-L291 | jack sleeve + piston ram |
| S10 | B | lead_screw_drive | rec_elevator_c6b98467…b92dc53f7 | L146-L155 + L233-L240 | lead screw mesh + drive nut |
| S11 | B | rack_and_pinion | rec_elevator_035bb14e…47918e7c | L78-L86 + L180-L187 | rack teeth(loop) + pinion cover |
| S12 | B | implicit_none | rec_elevator_9b38667c…ce9ee5f0e974 | L26-L54 | 无驱动可视件 fallback |
| S13 | C | enclosed_rectangular_cab | rec_elevator_0002 | L152-L254 | 实心轿厢 + 门框 + guide shoe |
| S14 | C | glass_cab_rectangular | rec_elevator_2f2b5d47…b086fd0cb2f28465 | L141-L248 | 矩形玻璃轿厢 |
| S15 | C | glass_cab_curved | rec_elevator_5ef65550…46b9b8f927 | L161-L286 + helper L24-L99 | 弧形玻璃轿厢 + curved mesh |
| S16 | C | open_cage | rec_elevator_f9dee4af…571ee72728cd | L84-L142 | 开放钢笼 + wire-mesh + hinge mount |
| S17 | C | flat_platform | rec_elevator_bd64f5d6…309646f1 | L60-L151 | 平台 deck + carriage + 前缘 hinge |
| S18 | D | center_opening_slide | rec_elevator_0002 | L256-L292 + L308-L335 | 双扇对开滑门 |
| S19 | D | single_panel_slide | rec_elevator_2f2b5d47…cb2f28465 | L265-L301 + L302-L315 | 单扇滑门 |
| S20 | D | swing_hinged_leaves | rec_elevator_6e47f388…8cb7dff5 | L244-L282 + L284-L301 | 摆门（bifold 见 c6b98467 L265-L344） |
| S21 | D | sliding_cage_gate | rec_elevator_9e2b821a…01bca3bc72 | L78-L96 + L107-L115 | 笼门横滑闸 |
| S22 | D | swing_cage_gate | rec_elevator_f9dee4af…72728cd | L152-L180 + L191-L199 | 笼门 REVOLUTE 闸 |
| S23 | D | folding_leaf_gate | rec_elevator_fb7c46fd…31e400c8 | L116-L127 + L149-L166 | 双叶折叠闸 |
| S24 | E | folding_handrail | rec_elevator_656f0954…b3630f1 | L282-L330 + L346-L373 | 折叠扶手（弧形版 5ef65550 L322-L405） |
| S25 | E | knee_guard_or_lip | rec_elevator_bd64f5d6…309646f1 | L153-L189 + L200-L208 | 护膝板/门槛 lip（lip 版 2f2b5d47 L317-L349） |
| S26 | E | folding_safety_arms | rec_elevator_0cad93cc…21273d10 | L291-L321 + L345-L372 | 平台两侧安全臂 |
| S27 | E | safety_pawl | rec_elevator_035bb14e…47918e7c | L227-L245 + L275-L288 | 安全爪（cage 版 5d3e5690 L132-L145） |
| S28 | mult | landing_door (shaft) | rec_elevator_7fd47ce8…35a2859a | L293-L322 + L338-L365 | 按楼层复制 shaft 层门（hatch 版 ba879bf8 L108-L132） |

## 模板实现备注（可选）

- 共享 helper：`_make_guide_rail` / `_make_guide_shoe`（A↔C 接触契约）、`_add_door_panel`（D 镜像双扇，参 rec_b0db92dc / rec_fd6c0a36 helper）、`_build_gate_leaf`（折叠闸，参 rec_fb7c46fd L116-L127）、wire-mesh loop（open_cage，参 rec_f9dee4af L100-L112）、`_annular_tube`/`_curved_panel_mesh`（glass tower/curved cab mesh）。
- 重点 InterfaceSpec / MatingContract：guide_shoe⇄guide_rail 必须全行程（0..car_travel 取若干 pose）保持 contact；门 closed pose 中缝 gap≈0 且 open pose 无 overlap；counterweight 与 car 反向时各自 guide 仍接触。
- captured-pin overlap：accessory hinge barrel / cage gate hinge pin 贯穿 knuckle 处可能需 element-scoped `allow_overlap`，仅对真实意图穿插声明。
- 暂不进入 seed domain（待实现后再开）：landing_door_floors（先实现 car portal 主路径，landing door 作为 dumbwaiter/液压家用梯子域二期）；revolute_sheave_wheel 与 lead_screw/rack 的 mesh 复杂件可在主滑门族 sweep 通过后再纳入。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核） |
