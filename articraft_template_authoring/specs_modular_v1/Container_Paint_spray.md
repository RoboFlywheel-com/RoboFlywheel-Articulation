# container_paint_spray (aerosol spray-paint can) — Modular Spec

> 来源小类：`picture/Container/Paint spray`（articraft_data 上游 Container/Paint spray fork-variant pool）。
> source map：`articraft_data/picture_expansion/template_source_maps/Container__Paint_spray.md`。
> 引用 `model.py:Lx-Ly` 来自各样本当前 `arti-template/data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`_can_body_solid` / `_nozzle_solid` / `_dust_cap_solid` / `cap_lift` / `cap_hinge` / `cap_unscrew` / `cap_carrier` / `tab_slide` / `nozzle_press` / `trigger_squeeze` / `grip_mount` / `trigger_pull` / `fan_cap_press` / `fan_cap_twist` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_paint_spray` |
| template path | `agent/templates/Container_Paint_spray.py` |
| test path (optional) | `tests/agent/test_container_paint_spray_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: closure_cap + actuator + body_section；cap / actuator 各自挂到 can_body 共同 root，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 8 fork 变体（cap×3 补 + actuator×3 补 + body×2 补，parent 各填一格）= 9 records |
| read_count | 9（全部读完整 `model.py`：parent + flip_top + screw_cap + no_cap_collar + trigger_lever + pistol_grip + fan_spin_cap + waisted_body + oval_section）|
| read_scope | all 5-star samples in this category（parallel_children fork pool，每变体只改一个 slot off parent；逐一全读，不抽样）|
| source_index_policy | only adopted module sources are indexed below（§14）|

阅读关键发现（影响 slot 设计）：
- **三轴互相正交**：每个 fork 变体只改一个 slot，其余两 slot 保持 parent 形态 → cap / actuator / body 是独立 slot。trigger_lever / pistol_grip / fan_spin_cap **仍保留 `cap_lift` dust cap**（actuator 换了但 cap 不变），证明 actuator ⟂ closure_cap；只有 no_cap_collar 主动去掉 cap（capless 设计，归 closure_cap 的一个候选）。
- **closure_cap joint 拓扑差异真实**：`cap_lift` PRISMATIC +Z（parent，L195-203）/ `cap_hinge` REVOLUTE +X（flip，L248-258）/ `cap_unscrew` CONTINUOUS +Z + `cap_lift` PRISMATIC +Z 经 massless `cap_carrier`（screw，L283-315，**source map 写的 "REVOLUTE about +Z" 是简化，实际是 CONTINUOUS+PRISMATIC 双关节 + carrier**）/ `tab_slide` PRISMATIC -Y 无 cap part（no_cap_collar，L279-287）。
- **actuator joint 拓扑差异真实**：`nozzle_press` PRISMATIC -Z 单关节（parent，L173-181）/ `trigger_squeeze` REVOLUTE +Y + 固定 `trigger_housing` 内联 visual（trigger，L243-251）/ `grip_mount` FIXED + `trigger_pull` REVOLUTE +Y 的 body→grip→trigger 两段链（pistol，L398-431）/ `fan_cap_press` PRISMATIC -Z + `fan_cap_twist` REVOLUTE +Z 的 body→stem→head 两段链（fan，L212-243）。
- **body_section 建模手法差异真实**：straight = union/extrude + loft 圆截面（parent `_can_body_solid` L42-80）/ waisted = `revolve` of 闭合 XZ spline 半profile（waisted L43-101）/ oval = `loft` of ellipse 截面序列（oval `_can_body_solid` L54-87）。三者发射 root `can_body` 的 mesh 形态不同。
- 共享不变量：can 轴 +Z、底坐地 z=0、居中 (0,0)、`CAN_R≈0.0325`、`BODY_TOP≈0.150`、`DOME_TOP≈0.176`、中心 valve stem `circle(0.006)` 到 `VALVE_TOP≈0.182`、splatter label_band sleeve、`nozzle_press upper=0.004`、`cap_lift upper=0.090`。

## 核心身份

气雾喷漆罐（aerosol spray-paint can）：一只直立细高金属罐，中心轴沿 +Z，底坐地 z=0，居中 (x=0,y=0)，高 ~0.18–0.21 m、直径 ~0.065 m（高宽比 >2，**细高**）。罐体由直/收腰/扁椭三种截面发射为 root `can_body`：straight = union + loft 圆截面、waisted = revolve XZ spline 半profile、oval = loft ellipse 截面，顶端统一收成 **crimped dome**（卷边肩穹）+ 中心 **valve stem boss**（`circle(0.006)` 短柱）。罐肩之上挂两个互相独立的功能层：

1. **actuator（喷头/扳机机构，主活动语义）**：press-down 按钮（`nozzle_press` PRISMATIC -Z ~0.004 m 压 valve）/ Montana 风指扳手（`trigger_squeeze` REVOLUTE +Y 摆压 valve）/ 夹扣枪柄（`grip_mount` FIXED 抱罐 + `trigger_pull` REVOLUTE +Y 指扳机）/ 宽扇帽（`fan_cap_press` PRISMATIC -Z 压 + `fan_cap_twist` REVOLUTE +Z 转换扇形）。
2. **closure_cap（上盖闭合机构）**：lift-off 防尘帽（`cap_lift` PRISMATIC +Z 大行程 ~0.09 m 抬离）/ 后铰翻盖（`cap_hinge` REVOLUTE +X）/ 螺纹旋盖（`cap_unscrew` CONTINUOUS +Z + `cap_lift` PRISMATIC +Z 经 massless `cap_carrier`，附 `threaded_collar` 内联 visual）/ 无帽安全领（`tab_slide` PRISMATIC -Y 滑动锁舌 + collar/grip_ridge 固定 visual，无 cap part）。

第三轴 **body_section** 改 root `can_body` 截面形态（straight / waisted / oval），不引入新活动件。默认成熟域：单罐，无 multiplicity（喷漆罐没有 N 个同构子件）。颜色 / 标签图案 / 高度 / 直径是连续参数与 `palette_style`，不入 slot。

不该混入：食品/饮料易拉罐（`container_can`，无喷头无防尘帽、有易拉环开口）、大型阀门气瓶/钢瓶（`container_gas_cylinder`，矮胖大罐 + 大手轮阀 + 压力表，非细高喷漆罐）、按压泵瓶/乳液泵（`container_pump`，泵头长吸管 + 螺纹泵颈，非 crimped 气雾阀 + 防尘帽）。

## 槽位 + 候选模块表

> **建模注记**：`body_section` 是 root `can_body` 的 mesh 属性（一次发射对应截面 + crimped dome + valve stem boss），不是独立串联 slot。`actuator` / `closure_cap` 各自挂到 `can_body`（parallel children）。三轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：closure_cap（上盖闭合机构槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| lift_off_cap（基线）| rec_aerosol-spray-paint-can-with-a-lift-off-dust-cap_..._5eaf6974（parent）| `_dust_cap_solid` L104-133 + `cap_lift` PRISMATIC +Z L195-203 | eligible if compatible | 防尘帽：中空圆穹壳套在罐肩外，`cap_lift` 单 PRISMATIC +Z 大行程（0.090 m）直抬离露喷头；1 part 1 joint |
| flip_top_cap | rec_container_paint_spray_var_flip_top | `_flip_cap_solid` L120-161 + `_hinge_ear_solid` L164-172（×2 body visual loop L205-212）+ `cap_hinge` REVOLUTE +X L248-258 | eligible if compatible | 后铰翻盖：一体盖绕后肩水平 +X 轴 REVOLUTE（q=0 闭合扣 rim，正 q 上翻 ~2.6 rad），body 上 2 个 hinge_ear 固定 visual 作铰座；1 part 1 joint |
| screw_cap | rec_container_paint_spray_var_screw_cap | `_screw_cap_solid` L173-220 + `_collar_solid` L143-170（内联 `threaded_collar` visual L249-254）+ `cap_unscrew` CONTINUOUS +Z L298-306 + `cap_lift` PRISMATIC +Z L307-315 经 massless `cap_carrier` L284-285 | eligible if compatible | 螺纹旋盖：盖经 massless `cap_carrier` 解耦 `cap_unscrew`(CONTINUOUS +Z 旋)→`cap_lift`(PRISMATIC +Z 抬)；body 上 `threaded_collar` 螺纹领固定 visual；2 part(cap+carrier) 2 joint |
| no_cap_collar | rec_container_paint_spray_var_no_cap_collar | `_collar_ring_solid` L120-138 + `_lock_tab_solid` L151-182 + `_grip_ridge_solid`/`_place_grip_ridge` L141-195（×6 body visual loop L229-235）+ `tab_slide` PRISMATIC -Y L279-287 | eligible if compatible | 无帽安全领：**无 cap part**，喷头外露；low collar + 6 grip_ridge 固定 visual + 红色 `lock_tab` 滑舌（`tab_slide` PRISMATIC -Y 锁/解锁，滑入喷头下挡压）；1 part(tab) 1 joint |

硬约束记录：closure_cap 4 candidate（达 3-6 目标）。含 PRISMATIC(lift)/REVOLUTE(flip +X)/CONTINUOUS+PRISMATIC(screw 双关节+carrier)/PRISMATIC(tab 横滑)四种 joint 拓扑 + 不同 part count（cap=1、flip=1、screw=2、no_cap=1+collar/ridge 固定 visual）。每个 candidate **≥1 non-fixed joint**。no_cap_collar 是唯一无 cap part 的候选（capless 真实形态）。

### Slot B：actuator（喷头/扳机机构槽——主活动语义）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| press_button（基线）| rec_aerosol-spray-paint-can-with-a-lift-off-dust-cap_..._5eaf6974（parent）| `_nozzle_solid` L83-101 + `nozzle_press` PRISMATIC -Z L173-181 | eligible if compatible | 指压按钮：小圆角块坐 valve stem，前面 spray hole；`nozzle_press` 单 PRISMATIC -Z（0→0.004 m）直压；1 part 1 joint |
| trigger_lever | rec_container_paint_spray_var_trigger_lever | `_trigger_lever_solid` L109-159 + `_trigger_housing_solid` L87-106（内联 `trigger_housing` visual L219-224）+ `trigger_squeeze` REVOLUTE +Y L243-251 | eligible if compatible | Montana 风指扳手：固定 `trigger_housing` 罩 + `trigger_lever` 绕 +Y 水平轴 REVOLUTE（squeeze 内摆 + 下压 valve，0→0.45 rad）；1 part 1 joint + 1 固定 visual |
| pistol_grip | rec_container_paint_spray_var_pistol_grip | `_pistol_grip_solid` L150-289 + `_trigger_solid` L319-339 + `_grip_rib_solid`(×4 L386-392) + `grip_mount` FIXED L398-404 + `trigger_pull` REVOLUTE +Y L418-431 | eligible if compatible | 夹扣枪柄：`pistol_grip` 经 `grip_mount`(FIXED) 抱罐上身（C 形 clamp + 把手 + 联动臂 + plunger 压 valve），`trigger` 经 `trigger_pull`(REVOLUTE +Y) 挂 grip（**body→grip→trigger 两段链**）；2 part 2 joint（1 FIXED + 1 REVOLUTE）|
| fan_spin_cap | rec_container_paint_spray_var_fan_spin_cap | `_fan_cap_stem_solid` L87-111 + `_fan_cap_head_solid` L114-140 + `fan_cap_press` PRISMATIC -Z L212-220 + `fan_cap_twist` REVOLUTE +Z L234-243 | eligible if compatible | 宽扇帽：`fan_cap_stem` 经 `fan_cap_press`(PRISMATIC -Z 压 valve) 挂 body，`fan_cap`(宽椭圆 head + 顶 spray slot) 经 `fan_cap_twist`(REVOLUTE +Z 0→π/2 换扇形) 挂 stem（**body→stem→head 两段链**）；2 part 2 joint |

硬约束记录：actuator 4 candidate（达 3-6 目标）。含 PRISMATIC(press)/REVOLUTE +Y(trigger 单 + pistol 链尾)/FIXED+REVOLUTE(pistol 两段链)/PRISMATIC+REVOLUTE(fan 两段链)四种 joint 拓扑 + 不同 part count（press=1、trigger=1+housing、pistol=2、fan=2）。每个 candidate **≥1 non-fixed joint**（pistol 含 FIXED + REVOLUTE，REVOLUTE 是活动件）。

### Slot C：body_section（罐体截面形态——root `can_body` 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_cylinder（基线）| rec_aerosol-spray-paint-can-with-a-lift-off-dust-cap_..._5eaf6974（parent）| `_can_body_solid` L42-80（circle extrude wall + loft dome + valve stem）| eligible if compatible | 直筒：常 `CAN_R` 圆截面直壁（extrude）+ crimped dome（loft 收 inward）+ 中心 valve stem boss；完美等径圆柱 |
| waisted_body | rec_container_paint_spray_var_waisted_body | `_can_body_solid` L43-101（闭合 XZ spline 半profile `.revolve(360,…)`）| eligible if compatible | 收腰：lathe revolve 半profile，下身全径 → 上三分之一凹腰 spline 收到 `SHOULDER_R` → dome 收 cup rim → valve stem；明显腰部过渡，cap 配窄肩 |
| oval_section | rec_container_paint_spray_var_oval_section | `_can_body_solid` L54-87（ellipse 截面序列 `.loft(ruled=False)`）+ `_oval_profile` L43-51 helper | eligible if compatible | 扁椭：椭圆水平截面（`CAN_RX=0.035` × `CAN_RY=0.020`，X 宽 Y 窄 ~1.75:1）loft 直壁 → crimp ring 收 → 圆 mounting cup；扁平 oval can，dust cap rim 也跟椭圆 |

硬约束记录：body_section 3 candidate（达下限 3）。三者发射手法不同（extrude+loft / revolve XZ spline / loft ellipse），footprint 不同（圆等径 / 圆收腰 / 椭圆扁平），是真实截面族差异，不只换尺寸。主多样性由 closure_cap × actuator 提供（见 §9）。

## 槽位图（slot graph）

pattern: parallel_children（`can_body` 为 root 坐地 z=0；closure_cap / actuator 各自挂它；无 multiplicity）

```
can_body(body_section)  [ROOT, 坐地 z=0, 中心轴 +Z, crimped dome + valve stem boss]
   │  (closure_cap / actuator 的固定 visual 也挂 can_body: threaded_collar / collar_ring+grip_ridge / hinge_ear / trigger_housing)
   │
   ├── actuator = press_button:
   │     can_body --[nozzle_press: PRISMATIC -Z @ (0,0,NOZZLE_SEAT_Z=0.176)]--> spray_nozzle
   │
   ├── actuator = trigger_lever:
   │     can_body[+trigger_housing 固定 visual @ DOME_TOP]
   │     can_body --[trigger_squeeze: REVOLUTE +Y @ (0,0,TRIGGER_PIVOT_Z=0.200)]--> trigger_lever
   │
   ├── actuator = pistol_grip:                      [两段链]
   │     can_body --[grip_mount: FIXED @ (0,0,GRIP_CENTER_Z=0.120)]--> pistol_grip(C-clamp+handle+linkage+plunger)
   │             pistol_grip --[trigger_pull: REVOLUTE +Y @ grip-local pivot]--> trigger
   │
   ├── actuator = fan_spin_cap:                     [两段链]
   │     can_body --[fan_cap_press: PRISMATIC -Z @ (0,0,STEM_SEAT_Z=0.176)]--> fan_cap_stem
   │             fan_cap_stem --[fan_cap_twist: REVOLUTE +Z @ (0,0,STEM_HEIGHT)]--> fan_cap(oval head)
   │
   ├── closure_cap = lift_off_cap:
   │     can_body --[cap_lift: PRISMATIC +Z @ (0,0,CAP_BOTTOM=0.150)]--> dust_cap
   │
   ├── closure_cap = flip_top_cap:
   │     can_body[+hinge_ear_0/1 固定 visual @ 后 rim]
   │     can_body --[cap_hinge: REVOLUTE +X @ (0,HINGE_Y=-(CAN_R+0.005),HINGE_Z=BODY_TOP)]--> flip_cap
   │
   ├── closure_cap = screw_cap:                     [双关节 + massless carrier]
   │     can_body[+threaded_collar 固定 visual @ shoulder]
   │     can_body --[cap_unscrew: CONTINUOUS +Z @ (0,0,CAP_BOTTOM)]--> cap_carrier(massless,无 visual)
   │             cap_carrier --[cap_lift: PRISMATIC +Z]--> screw_cap
   │
   └── closure_cap = no_cap_collar:                 [无 cap part]
         can_body[+collar_ring + grip_ridge_0..5 固定 visual @ DOME 下]
         can_body --[tab_slide: PRISMATIC -Y @ (0,TAB_ORIGIN_Y,TAB_BASE_Z)]--> lock_tab
```

接口点位与 joint 语义：
- **actuator 接口**：所有 actuator 的 mount origin 落在罐顶真实硬件——press/fan 在 valve seat `(0,0,0.176)`、trigger 在 dome 上 housing 顶 `(0,0,0.200)`、pistol 在上身直壁 clamp 中心 `(0,0,0.120)`。press/fan 压 valve(-Z)，trigger/pistol 绕 +Y 水平轴摆。pistol/fan 是两段链（FIXED/PRISMATIC 后再接 REVOLUTE）。
- **closure_cap 接口**：cap mount origin 落在罐肩 / rim 真实硬件——lift/screw 在 cap seat `(0,0,0.150)` 沿 +Z，flip 在后 rim 边 `(0,-(CAN_R+0.005),BODY_TOP)` 沿 +X，no_cap 的 tab 在 collar 口 `(0,TAB_ORIGIN_Y,TAB_BASE_Z)` 沿 -Y。screw 经 massless `cap_carrier`（1e-4 mass Box，无 visual）解耦 CONTINUOUS 旋 + PRISMATIC 抬。
- **固定 visual（挂 can_body，无独立 joint）**：screw 的 `threaded_collar`、no_cap 的 `collar_ring`+6 `grip_ridge`、flip 的 2 `hinge_ear`、trigger 的 `trigger_housing`。这些是对应 closure/actuator module 一并发射的 parent visual（铰座 / 螺纹领 / 安全领 / 扳机罩）。
- **mating policy**：cap skirt 罩 over rim / clamp 抱罐 / tab 嵌 collar 槽 / nozzle 坐 valve stem 都是 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 overlap（见各 record run_tests 的 `ctx.allow_overlap`，如 parent L240-246 nozzle↔valve、L260-266 cap↔body；screw L380-386 cap↔collar；no_cap L379-391 tab↔collar；pistol L511-531 grip↔body；trigger L325-336 lever↔housing）。
- **rest pose**：所有 cap q=0 闭合/坐下（no_cap 无 cap）；nozzle/fan/trigger/pistol-trigger q=0 未压；lock_tab q=0 解锁（让出喷头）；fan q=0 横扇。cap 抬升/翻起/旋升、actuator 压下/摆动为 viewer 目检活动语义。
- **互斥 / 可选**：closure_cap 各候选互斥（一次一种盖机构）；actuator 各候选互斥（一次一种喷头）；no_cap_collar 是唯一无 cap part 候选；massless `cap_carrier` 仅 screw_cap 发射。

## 每槽位 Module Emits / Interfaces

### Slot C / can_body（body_section，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `can_body`（visual: `can_body` mesh + `label_band` splatter sleeve[ + closure/actuator 的固定 visual]）| parent `_can_body_solid` L42-80 / waisted `.revolve` L43-101 / oval `.loft(ellipse)` L54-87 |
| internal joints | 无（root 罐体本身无活动件）| — |
| upstream interface | 坐地 z=0（root, base rim）| parent L47-51 BODY_BOTTOM |
| downstream interface | valve stem seat `(0,0,0.176)` + cap seat `(0,0,0.150)` + 后 rim `(0,-CAN_R,BODY_TOP)`（actuator/cap joint 的 parent 接口）| parent NOZZLE_SEAT_Z L36 / CAP_BOTTOM L38 |

### Slot B / actuator（每候选发射对应活动喷头）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spray_nozzle` / `trigger_lever`(+`trigger_housing` 固定 visual) / `pistol_grip`+`trigger` / `fan_cap_stem`+`fan_cap` | 各 actuator 源 |
| internal joints | `nozzle_press` PRISMATIC -Z（press）/ `trigger_squeeze` REVOLUTE +Y（trigger）/ `grip_mount` FIXED + `trigger_pull` REVOLUTE +Y（pistol）/ `fan_cap_press` PRISMATIC -Z + `fan_cap_twist` REVOLUTE +Z（fan）| parent L173-181 / trigger L243-251 / pistol L398-431 / fan L212-243 |
| upstream interface | valve seat / dome housing / 上身 clamp（挂 can_body）| 各 origin |
| downstream interface | 无（actuator 是末端活动件；fan/pistol 的二级 child 挂一级 actuator）| 各源 |

### Slot A / closure_cap（每候选发射对应盖机构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dust_cap`（lift）/ `flip_cap`（flip）/ `screw_cap`+`cap_carrier`(massless)（screw）/ `lock_tab`（no_cap，无 cap part）| 各 cap 源 |
| internal joints | `cap_lift` PRISMATIC +Z（lift）/ `cap_hinge` REVOLUTE +X（flip）/ `cap_unscrew` CONTINUOUS +Z + `cap_lift` PRISMATIC +Z（screw）/ `tab_slide` PRISMATIC -Y（no_cap）| parent L195-203 / flip L248-258 / screw L298-315 / no_cap L279-287 |
| fixed visuals on can_body | flip: `hinge_ear_0/1`；screw: `threaded_collar`；no_cap: `collar_ring`+`grip_ridge_0..5` | flip L205-212 / screw L249-254 / no_cap L220-235 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure_cap | enum | lift_off_cap / flip_top_cap / screw_cap / no_cap_collar | lift_off_cap | choice | deterministic procedural sampler 选 | module table |
| actuator | enum | press_button / trigger_lever / pistol_grip / fan_spin_cap | press_button | choice | sampler 选 | module table |
| body_section | enum | straight_cylinder / waisted_body / oval_section | straight_cylinder | choice | sampler 选 | module table |
| palette_style | enum | classic_white_splatter / matte_black_pro / safety_red / industrial_blue / hi_vis_yellow / primer_grey / brushed_aluminum / metallic_silver_blue / two_tone_black_orange（9 colorway，各带显式 finish）| classic_white_splatter | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)` 选一 colorway（含 finish 维度）| palette（见下）|
| body_height_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放罐高 H（BODY_TOP→DOME_TOP→cap seat / valve seat 同比抬），clamp | resolve clamp |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放罐径 CAN_R（oval 同比缩 CAN_RX/CAN_RY，保 X:Y 比），clamp | resolve clamp |
| cap_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 cap 高 / skirt 深（dust/flip/screw），clamp | resolve clamp |
| cap_bore_R | float | derived | — | equation | `= body_R · body_radius_scale + cap_clearance`（cap/clamp 内径跟随罐径，保罩配合）| resolve（接口）|
| cap_lift_travel | float | [0.85, 1.10] | 1.0 | independent | 缩放 `cap_lift` / `tab_slide` / hinge upper 行程，clamp（保抬离够露喷头）| resolve clamp |
| actuator_press_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 `nozzle_press`/`fan_cap_press` upper(~0.004) + trigger/pistol REVOLUTE upper，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`cap_bore_R ≥ body_R + clearance` 且 `cap_outer_R ≤ body_R + proud`；`cap_lift_travel·base ≥ actuator_top − cap_seat_z + margin`（抬离须高过喷头顶）；违反按比例回缩 cap/lift scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | `no_cap_collar` 不发射 cap → `cap_height_scale`/`cap_bore_R` 对其无效（只作用 tab/collar）；`pistol_grip`/`fan_spin_cap` 为两段链，`actuator_press_scale` 作用其末端 REVOLUTE/PRISMATIC range | 上游 enum |

**palette_style colorway（9 个，来自 5★ 源真实配色 + 真实喷漆罐合理外推，每 seed `rng.choice(PALETTE_STYLES)` 采样一个；含显式 finish 维度）**：

> **finish 维度（material-finish）**：每个 colorway 显式声明一个表面处理语义——`glossy_print`（光面印刷标签，标准消费喷漆罐）/ `matte`（哑光低反光，专业/雾面漆）/ `brushed_aluminum`（拉丝/裸铝本色，未印刷工业罐）/ `metallic`（金属闪粉漆，body 偏冷亮金属色）/ `hi_vis_safety`（荧光高可视安全色）/ `primer_matte`（底漆灰哑面）/ `two_tone`（双色撞色 body↔label/cap）/ `industrial_stencil`（工业模板印刷，裸金属 + 单色 stencil 块）。模板将 finish 映射为 material rgba 微调（金属面提亮/哑面降饱和），**不改几何、不入 slot_choice**，仅与 colorway 绑定的 material 选择维度。

| palette_style | finish | body/metal | cap/actuator accent | label_band | 源 |
|---|---|---|---|---|---|
| classic_white_splatter（默认）| glossy_print | metal (0.78,0.80,0.83) | dark_grey_cap (0.20,0.21,0.20) / dark_nozzle (0.16,0.16,0.17) | white splatter (0.90,0.90,0.92) | parent L139-142 |
| matte_black_pro | matte | metal (0.78,0.80,0.83) | grip_black (0.10,0.10,0.12) / housing_dark (0.12,0.12,0.13) | dark splatter (0.14,0.14,0.15) | pistol L354 / trigger L200 |
| safety_red | glossy_print | metal (0.78,0.80,0.83) | trigger_red (0.78,0.14,0.10) / fan_cap_red (0.72,0.18,0.12) / red_tab (0.80,0.15,0.12) | white (0.90,0.90,0.92) | trigger L201 / fan L181 / no_cap L205 |
| industrial_blue | glossy_print | metal (0.78,0.80,0.83) | dark_cap blue (0.18,0.20,0.24) | blue (0.12,0.55,0.82) | screw L230 / oval L170 |
| hi_vis_yellow | hi_vis_safety | metal (0.78,0.80,0.83) | dark accent (0.16,0.16,0.17) | hi-vis yellow (0.95,0.82,0.10)（派生荧光暖色）| 真实喷漆罐常见（splatter 基础上换 label hue 为荧光黄）|
| primer_grey | primer_matte | metal (0.78,0.80,0.83) | collar_metal (0.70,0.73,0.77) | matte grey (0.88,0.89,0.91) | screw L229 / waisted L158 |
| brushed_aluminum | brushed_aluminum | bare alu (0.82,0.83,0.85) | collar_metal (0.70,0.73,0.77) / hinge_metal (0.65,0.67,0.70) | unprinted bare（同 body alu，无印刷）| 裸铝工业罐外推（锚 hinge L182 / collar L229）|
| metallic_silver_blue | metallic | bright metal (0.80,0.82,0.86) | trigger_steel accent (0.26,0.27,0.30) | metallic blue (0.18,0.42,0.70)（冷亮金属漆）| 金属闪粉漆外推（锚 trigger_steel pistol L355 + blue oval L170 降亮） |
| two_tone_black_orange | two_tone | metal (0.78,0.80,0.83) | gloss_black cap (0.12,0.12,0.13) / safety_orange accent (0.92,0.45,0.08) | orange-on-black two-tone (0.92,0.45,0.08 ↔ 0.12,0.12,0.13) | 撞色双色外推（锚 housing_dark trigger L200 + 荧光暖色派生）|

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`cap_bore_R` 为 equation（cap/clamp 内径跟随罐径）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 closure_cap / actuator / body_section 拓扑。`palette_style`（9 colorway × 含 finish 维度）只换 material rgba / 表面处理语义，不改几何、不入 slot_choice。finish 维度（glossy_print / matte / brushed_aluminum / metallic / hi_vis_safety / primer_matte / two_tone / industrial_stencil）与 colorway 绑定，模板将其映射为 material rgba 微调（金属面提亮、哑面降饱和、裸铝不印刷），同样不动拓扑。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（closure_cap + actuator + body_section）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。喷漆罐无 N 个同构子件（无 drawers/slats/spokes/links）。
- 注：flip 的 2 `hinge_ear`、no_cap 的 6 `grip_ridge` 是各 module 内**固定数量**的小硬件 visual（写死 2 / 6），不是模板级 multiplicity 轴，不暴露 count_param。
- N 样本已覆盖：无。模板建议 N_range：无（此小类无 multiplicity 轴）。copied object / naming / placement / joint policy：无。

## 拓扑多样性审计

总组合数：closure_cap(4) × actuator(4) × body_section(3) = **48**。

仅 closure_cap × actuator = **16 ≥ 10** 已可过门控；叠 body_section 后充裕（48）。

理由：closure_cap(4) × actuator(4) 的笛卡尔积即 16 distinct，远超 10；这两轴各引入**不同 joint 拓扑**——closure_cap：PRISMATIC(lift)/REVOLUTE +X(flip)/CONTINUOUS+PRISMATIC+massless carrier(screw)/PRISMATIC -Y(tab，无 cap part)；actuator：PRISMATIC(press)/REVOLUTE +Y(trigger)/FIXED+REVOLUTE 两段链(pistol)/PRISMATIC+REVOLUTE 两段链(fan)。不同 part count（1~2 个活动 part + 不同固定 visual 组）+ 不同 joint type/axis/chain depth 是真实结构差异，非换色换尺寸。body_section 改 root mesh 截面（圆直 / 圆收腰 / 椭圆），48 组合全合法。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 conditional 见 compatibility matrix），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除/适配少量组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-4 → 0-19 → 0-49 分阶段早停 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 48（48 组合的采样空间足够撑满；受真实词汇表约束，body_section(3) 是较窄轴，但 closure_cap(4)×actuator(4)=16 已撑开主多样性）。低于 300 的原因：本小类真实结构词汇就是 4 cap × 4 actuator × 3 body = 48，是该类目的合理上限，不强行注水（喷漆罐结构家族有限，48 已覆盖所有真实形态）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 6 个 scale（body_height / body_radius / cap_height / cap_lift_travel / actuator_press + 派生 cap_bore_R）。全部 `resolve_config` clamp + 每 build 统一应用。`cap_bore_R` 为 equation（cap/clamp 内径跟随罐径）。盖罩配合 + 抬离够露喷头不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 actuator/cap joint origin（valve seat / cap seat / 后 rim hinge / collar 口）、盖罩配合、固定 visual 位置或类别身份。按 §7 约束类型（independent / equation / inequality / conditional）声明依赖，遵循连续尺寸采样契约（先采 independent → 派生 cap_bore_R → 投影盖罩/抬离不等式 → 解析 no_cap/两段链 conditional）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含三轴且与 build 一致；palette 不入 slot_choice |
| compatibility matrix | (1) `no_cap_collar` 无 cap part → 不应用 cap_height/cap_bore，actuator 喷头外露（任意 actuator 合法，含 fan 的宽 head）。(2) `pistol_grip` clamp 抱上身直壁 → 与 waisted_body（上三分之一收腰）配时，clamp 中心 `GRIP_CENTER_Z=0.120` 落在腰下全径段（resolve 校 clamp z < waist_start，必要时下移），oval_section 时 clamp 半径取 max(CAN_RX,CAN_RY)+gap（C-clamp 适配椭圆）。(3) `flip_top_cap`/`screw_cap` 罩 over rim → oval_section 时 cap rim 跟椭圆（oval cap 源已示范），waisted 时 cap 配窄肩（waisted cap 源已示范）。(4) `cap_lift`/screw 抬离须高过所选 actuator 顶（pistol/fan/trigger 比 press 高）→ resolve 派生 cap_lift_travel ≥ actuator_top − cap_seat + margin。(5) 各 closure/actuator 互斥。无硬 gate-out（48 组合全合法，仅 resolve 派生尺寸适配）| 无 floating / collision / cap 穿喷头 / clamp 穿罐 / joint 轴或 origin 错位 |
| controlled local variation | 6 个 clamped scale，每 build 统一；cap_bore_R equation 驱动 cap/clamp 内径；抬离不等式投影 | 比例变化不破坏 actuator/cap joint origin / 盖罩配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-4 → 0-19 → 0-49 分阶段；0-999 成熟审计 | cap/actuator 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| closure_cap | 4 | yes | yes | lift(PRIS +Z) / flip(REV +X) / screw(CONT+PRIS+carrier) / no_cap(PRIS -Y tab, 无 cap part) |
| actuator | 4 | yes | yes | press(PRIS -Z) / trigger(REV +Y) / pistol(FIXED+REV 链) / fan(PRIS+REV 链) |
| body_section | 3 | yes | yes | straight(extrude+loft) / waisted(revolve spline) / oval(loft ellipse) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (closure_cap, actuator, body_section) 三轴；palette_style 不入 slot_choice
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；cap_bore_R equation 驱动 cap/clamp 内径；盖罩配合 + 抬离够露喷头不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：48 组合全合法（无硬 gate-out）；no_cap 不应用 cap scale；pistol clamp z 适配 waisted；cap rim 适配 oval / waisted
- 连续 scale clamp 后不破坏 actuator/cap joint origin / 盖罩配合 / 坐地 / 类别身份
- 关键 joint：
  - lift `cap_lift` PRISMATIC +Z (abs(axis[2])>0.99, upper≈0.090)；flip `cap_hinge` REVOLUTE +X (abs(axis[0])>0.9)；screw `cap_unscrew` CONTINUOUS +Z + `cap_lift` PRISMATIC +Z + massless `cap_carrier`（无 visual）；no_cap `tab_slide` PRISMATIC -Y (abs(axis[1])>0.9)
  - press `nozzle_press` PRISMATIC -Z (axis[2]<-0.99, upper≈0.004)；trigger `trigger_squeeze` REVOLUTE +Y (abs(axis[1])>0.9)；pistol `grip_mount` FIXED + `trigger_pull` REVOLUTE +Y（child=grip 不是 body）；fan `fan_cap_press` PRISMATIC -Z + `fan_cap_twist` REVOLUTE +Z (abs(axis[2])>0.99)
- can_body 是细高罐（height>0.16, 0.05<dia<0.10, height>dia·1.8），坐地 z=0，valve stem 居中
- captured-fit：element-scoped `allow_overlap`（nozzle↔valve / cap skirt↔body / clamp↔body / tab↔collar / hinge_ear↔flip_cap / lever↔housing），复制各 record run_tests 的声明
- grandfather：所有 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用矮胖大罐 + 大手轮阀（gas_cylinder 形态）当 body → 失类别身份；喷漆罐必须细高（height>dia·1.8）+ crimped dome + 中心 valve stem。
- 把 actuator joint origin 放在罐底 / 任意点而非 valve seat / dome housing / 上身 clamp 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- screw 盖不用 massless `cap_carrier` 解耦 rotate/lift，直接把 CONTINUOUS+PRISMATIC 串到 cap 单 part → 旋转与抬升耦合错误（应 body→carrier→cap 两 joint）。
- pistol/fan 拍平成单 joint（漏掉 grip_mount FIXED / fan_cap_press），把 trigger/head 直接挂 body → 丢两段链拓扑，与源不符。
- closure_cap rest pose 设成张开 / 抬起而非 q=0 闭合（no_cap 除外，本就无 cap）→ current-pose 与 viewer 目检不符。
- 给盖罩 / clamp / nozzle 友配补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 标签图案当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- cap 抬离行程不足以露出所选 actuator 顶（如 pistol/fan 比 press 高）→ 抬离不等式 FAIL（cap 穿喷头）；应在 resolve 派生 cap_lift_travel ≥ actuator_top − cap_seat + margin。
- no_cap_collar 误发射 cap part → 与 capless 语义不符；no_cap 只有 lock_tab + collar/grip_ridge 固定 visual，无 cap。
- 把 actuator 和 closure_cap 当同一 slot（如以为换喷头就得换盖）→ 三轴正交，trigger/fan/pistol 都保留 dust cap，只有 no_cap 去 cap。

## 与相邻类别的边界

- 不该混入：**container_can（食品/饮料易拉罐）**——理由：易拉罐是 pull-tab/stay-tab 开口、无喷头、无防尘帽、矮胖；喷漆罐是细高 + crimped 气雾阀 + 喷头 + 防尘帽。
- 不该混入：**container_gas_cylinder（大型阀门气瓶/钢瓶）**——理由：气瓶是矮胖大罐 + 大手轮/角阀 + 压力表 + 凹底环足；喷漆罐细高、阀是 crimped 中心 valve stem + 指压喷头。
- 不该混入：**container_pump（按压泵瓶/乳液泵）**——理由：泵瓶是螺纹泵颈 + 长吸管 + 旋锁泵头，body 多为塑料瓶；喷漆罐是金属罐 + crimped 气雾阀 + 防尘帽，无吸管无螺纹泵颈。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft。9 records 全读（1 parent + 8 变体，覆盖全部 11 候选格）。4 cap × 4 actuator × 3 body = 48 combos；cap×actuator=16 clears 。三轴正交（trigger/fan/pistol 保留 dust cap，仅 no_cap 去 cap）。screw=CONTINUOUS+PRISMATIC+massless carrier（source map 的 "REVOLUTE +Z" 已修正）、pistol/fan=两段链、no_cap 无 cap part。无 multiplicity 轴。**palette_style 扩到 9 colorway**（classic_white_splatter / matte_black_pro / safety_red / industrial_blue / hi_vis_yellow / primer_grey / brushed_aluminum / metallic_silver_blue / two_tone_black_orange），每个绑定**显式 finish 维度**（glossy_print / matte / brushed_aluminum / metallic / hi_vis_safety / primer_matte / two_tone；industrial_stencil 备用语义）。前 6 取自 5★ 源真实配色（parent/trigger/pistol/fan/screw/oval/waisted/no_cap/flip 的 metal/cap/label/accent rgba）；后 3 为真实喷漆罐合理外推（brushed_aluminum 锚 hinge_metal 0.65,0.67,0.70 + collar_metal 0.70,0.73,0.77 裸铝；metallic_silver_blue 锚 trigger_steel 0.26,0.27,0.30 + blue 降亮；two_tone_black_orange 锚 housing_dark 0.12,0.12,0.13 + 派生 safety_orange）。palette-only：不改任何 slot/candidate/multiplicity/joint/dimension/topology。开放问题：hi_vis_yellow / safety_orange / metallic blue 是真实喷漆罐常见色的合理外推（非源 rgba 直引），finish 维度仅作 material rgba 微调语义、不动几何。|

## 模板实现备注（可选）

- 共享 helper：`_can_body_solid(body_section)`（dispatch straight=extrude+loft / waisted=revolve XZ spline / oval=loft ellipse）+ `_valve_stem` + `_label_band(section)` 全 module 公用 root 发射。
- screw_cap：必须经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial）解耦 `cap_unscrew`(CONTINUOUS +Z)→`cap_lift`(PRISMATIC +Z)；并发射 `threaded_collar` 内联 visual。
- pistol_grip / fan_spin_cap：两段链。pistol = `grip_mount`(FIXED, child=grip) 再 `trigger_pull`(REVOLUTE +Y, parent=grip, child=trigger)；fan = `fan_cap_press`(PRISMATIC -Z, child=stem) 再 `fan_cap_twist`(REVOLUTE +Z, parent=stem, child=head)。
- 固定 visual：flip 的 `hinge_ear_0/1`（写死 2）、no_cap 的 `collar_ring`+`grip_ridge_0..5`（写死 6）、trigger 的 `trigger_housing`、screw 的 `threaded_collar` 均挂 can_body，不作独立 part。
- captured-fit overlap：`run_container_paint_spray_tests` 复制各源 record 的 element-scoped `ctx.allow_overlap`（nozzle↔valve、cap↔body、clamp↔body+label、tab↔collar、hinge_ear↔flip_cap、lever↔housing、cap dome↔fan head/stem）。
- cap_bore_R equation：`resolve_config` 派生 `cap_bore_R = body_R·body_radius_scale + clearance`、`clamp_inner_R = max(CAN_RX,CAN_RY)·scale + gap`（oval 适配）；盖罩配合 + 抬离不等式在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + captured-fit allow_overlap + massless carrier 解耦 screw 的骨架，与本 spec 的 closure_cap 多机构分支高度同构）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | lift_off_cap + press_button + straight_cylinder | rec_aerosol-spray-paint-can-..._5eaf6974（parent）| `_can_body_solid` L42-80 / `_nozzle_solid` L83-101 / `_dust_cap_solid` L104-133 / `nozzle_press` L173-181 / `cap_lift` L195-203 | 直筒 body 基线 + 指压按钮 + lift-off 防尘帽 |
| S2 | A | flip_top_cap | rec_container_paint_spray_var_flip_top | `_flip_cap_solid` L120-161 / `_hinge_ear_solid` L164-172 / `cap_hinge` REVOLUTE +X L248-258 | 后铰翻盖 + hinge_ear 铰座 |
| S3 | A | screw_cap | rec_container_paint_spray_var_screw_cap | `_screw_cap_solid` L173-220 / `_collar_solid` L143-170 / `cap_unscrew` CONTINUOUS L298-306 / `cap_lift` PRISMATIC L307-315 / massless `cap_carrier` L284-285 | 螺纹旋盖（CONTINUOUS+PRISMATIC+carrier）+ 螺纹领 |
| S4 | A | no_cap_collar | rec_container_paint_spray_var_no_cap_collar | `_collar_ring_solid` L120-138 / `_lock_tab_solid` L151-182 / `_place_grip_ridge` L185-195 / `tab_slide` PRISMATIC -Y L279-287 | 无帽安全领 + 滑动锁舌（无 cap part）|
| S5 | B | trigger_lever | rec_container_paint_spray_var_trigger_lever | `_trigger_lever_solid` L109-159 / `_trigger_housing_solid` L87-106 / `trigger_squeeze` REVOLUTE +Y L243-251 | Montana 风指扳手 + 固定罩 |
| S6 | B | pistol_grip | rec_container_paint_spray_var_pistol_grip | `_pistol_grip_solid` L150-289 / `_trigger_solid` L319-339 / `grip_mount` FIXED L398-404 / `trigger_pull` REVOLUTE +Y L418-431 | 夹扣枪柄两段链（FIXED clamp + REVOLUTE trigger）|
| S7 | B | fan_spin_cap | rec_container_paint_spray_var_fan_spin_cap | `_fan_cap_stem_solid` L87-111 / `_fan_cap_head_solid` L114-140 / `fan_cap_press` PRISMATIC L212-220 / `fan_cap_twist` REVOLUTE +Z L234-243 | 宽扇帽两段链（PRISMATIC press + REVOLUTE twist）|
| S8 | C | waisted_body | rec_container_paint_spray_var_waisted_body | `_can_body_solid` L43-101（revolve 闭合 XZ spline 半profile）| 收腰罐体（lathe revolve）|
| S9 | C | oval_section | rec_container_paint_spray_var_oval_section | `_can_body_solid` L54-87（loft ellipse 截面）/ `_oval_profile` L43-51 | 扁椭罐体（loft ellipse）|
