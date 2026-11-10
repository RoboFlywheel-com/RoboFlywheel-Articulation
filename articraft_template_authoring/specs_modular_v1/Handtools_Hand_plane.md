# hand_plane (bench / block hand plane) — Modular Spec

> 来源小类：`picture/Handtools/Hand plane`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Hand_plane.md`。
> **"Hand plane" 在此 = 手用刨（cast-iron bench / block hand plane，Stanley/Bailey 风格平刨、低角度块刨、肩刨/裁口刨），不是凿子 chisel、不是电动砂光机 sander、也不是刮刀 spokeshave。**
> 结构家族 = 铸铁刨：一只 `plane_body`（root，铸铁 sole + 整体 `frog` 斜床）上**FIXED 床定**一片 `cutting_iron`（刀片+断屑器）于刨口；刀上一套**夹刃机构**（lever-cap 翻凸轮 / 横压条+拇指螺钉 / 螺纹柱+帽螺母，决定 PRIMARY 关节类型）；刀面一根 `lateral_lever`（REVOLUTE 绕 BED_NORMAL，横向校准）；床后一只 `depth_wheel`（CONTINUOUS 绕 BED_UP，进刀深度）；sole 上用户握把（前 knob + 后 D-tote / 前 horn + 闭环 tote / 单 palm-hump）。
>
> **同步状态**：本 spec 引用的 **7 个 5 星样本（1 个 parent + 6 个 fork 槽位变体）已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对，全文读完）。引用以 part / joint / helper **名字** 为准（`plane_body`/`cutting_iron`/`lever_cap`/`cam_lever`/`clamp_bar`/`thumbscrew`/`cap_nut`/`lateral_lever`/`depth_wheel`/`front_knob`/`rear_tote`/`front_horn`/`palm_rest` part；`lever_cap_cam`/`thumbscrew`/`cap_nut_spin`/`lateral_adjust`/`depth_adjust`/`body_to_*` joint；`_bed_pt`/`_tilt_back`/`_bench_plane_body`/`_block_plane_body`/`_rabbet_plane_body`/`_frog`/`_front_horn_geom`/`_palm_rest`/`_clamp_boss` 等），行号仅作定位。
>
> **坐标约定（全 7 样本一致，模板直接沿用）**：刨沿 **+X**（toe/趾在 +X、heel/跟在 −X），sole 底面坐 **z=0**，宽沿 **Y**。床面斜角 `BED_DEG`（45° bench/rabbet、20° block）。共享 helper `_bed_pt(u, m)` 把"沿床向上 u、沿床外法向 m"映射回 body 坐标；`BED_NORMAL=(SQ,0,SQ)`（lateral lever / thumbscrew / cap_nut 轴）、`BED_UP=(-SQ,0,SQ)`（depth wheel 轴），其中 SQ 随 BED_DEG 取（45° 用 √0.5，20° 用 sin/cos）。`_tilt_back` 把平放部件绕 +Y 旋转 BED_DEG 成床姿。所有 fixed 件 mesh 在 body-world 直接建（identity part origin），活动件按 pivot 在 local origin 建、joint origin 落 body-world。

## 元信息
| 项 | 值 |
|---|---|
| slug | `hand_plane` |
| template path | `agent/templates/Handtools_Hand_plane.py` |
| test path (optional) | `tests/agent/test_hand_plane_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `plane_body`；三个并行替换层：body_silhouette / blade_clamp / grip 各自挂 body；clamp 与 grip 的活动件挂 body 或 cap；body_silhouette 只换 body+frog mesh + 床角）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 7 个样本）**：`plane_body`（root，铸铁 sole + `sole_edge` 亮钢边 visual + 整体 `_frog` 斜床 visual + `_depth_stud` visual + 夹刃硬件 visual）+ `cutting_iron`（刀+断屑器，**FIXED 床定** `body_to_cutting_iron`）。三根非 fixed 关节在每个变体里复现：**PRIMARY** = 夹刃 actuator（joint 类型/名随 Slot B 变）、**SECONDARY** = `lateral_adjust`（`lateral_lever` REVOLUTE 绕 `BED_NORMAL`，lower/upper ±0.35，骑刀面）、**TERTIARY** = `depth_adjust`（`depth_wheel` CONTINUOUS 绕 `BED_UP`，captured 在 `depth_stud` 上）。`lateral_lever` / `depth_wheel` 在 7 样本里几乎逐字相同（仅尺寸微调）→ 共享 fixed-spine，不入 slot。
- **body_silhouette 轴**（Slot A）：是 body mesh + frog mesh + 床角 + iron 宽度的形态变化（part 树 / joint 拓扑不变，仍是 `plane_body` root + `cutting_iron` FIXED child）。solid_block_45（parent，solid 中央 casting、全宽闭口、45° frog）/ low_block_trough（blocksole，短矮 sole + 两道低 sidewall = 开顶 trough、20° 整体床、`WALL_HEIGHT`）/ narrow_open_cheek（rabbet，窄体 −Y 全高 cheek + +Y 仅 3mm `OPEN_CHEEK_HEIGHT` lip、iron 跑满全宽）。
- **blade_clamp 轴**（Slot B）：是 PRIMARY 关节的**类型 / parent / part 数**真正变化（InterfaceSpec 的 consumer-joint 字段差异点）。
  - levercap_flipcam（parent）：`lever_cap` FIXED part + `cam_lever` 独立 part，`lever_cap_cam` **REVOLUTE 绕 −Y**，**parent=lever_cap（两级挂载）**；`cap_screw` body inline visual。→ +2 part（cap+cam）+1 REVOLUTE，cam 挂 cap。
  - crossbar_thumbscrew（clampbar）：`clamp_bar` FIXED part（钉在两 `clamp_boss_{i}` body visual 上，`for i in range(2)`）+ `thumbscrew` 独立 part，`thumbscrew` joint **REVOLUTE 绕 `BED_NORMAL`**，**parent=body**；`thumbscrew_stud` body inline visual。→ +2 part（bar+screw）+1 REVOLUTE，screw 挂 body。
  - capnut_post（screwcap）：`cap_post` body inline visual + `cap_nut`（KnobGeometry 滚花黄铜）独立 part，`cap_nut_spin` **CONTINUOUS 绕 `BED_NORMAL`**，**parent=body**；iron 带 `post_hole`。→ +1 part（nut）+1 CONTINUOUS，nut 挂 body。
- **grip 轴**（Slot C）：是 grip part 数 / 形态变化（全 FIXED，无活动语义，但 part 树差异真实）。knob_plus_Dtote（parent，`front_knob` 旋转 mushroom + `rear_tote` 开 D 形 extrude+椭圆窗，**2 个 FIXED part**）/ horn_plus_ringtote（closedtote，`front_horn` section_loft 前冲弯角 + `rear_tote` 闭环全包窗，**2 个 FIXED part**，horn 用 `mesh_from_geometry`）/ single_palm_hump（palmgrip，`palm_rest` 旋转 dome ∩ box + 指槽，**1 个 FIXED part，删掉前 knob**，heel boss 加宽)。
- **multiplicity**：无可变结构复制轴（见 §8）。唯一循环发射是 `depth_wheel` 滚花 `for i in range(24)`、`thumbscrew` 滚花 `for i in range(24)`、`cap_nut` 的 KnobGrip count=24、clampbar 的两端 `clamp_boss_{i}` / pin-hole `for i in range(2)`——都是装饰/对称硬件 module-local 固定阵列，非可参数化结构数量轴。

## 核心身份

一只**手用刨**（cast-iron hand plane）：一只铸铁 `plane_body`（root，黑漆 japanned 机身 + 亮钢机削 sole 边 `sole_edge`，坐地于 sole 底 z=0），机身整体一道 `frog` 斜床（45° bench/rabbet 或 20° block），床上**FIXED 床定**一片钢 `cutting_iron`（blade + chipbreaker）于刨口（mouth，sole 上一道窄通槽，刀刃从此露出）；刀片用一套**夹刃机构**压紧（polished 钢 lever-cap + 翻凸轮 / 钢横压条 + 滚花黄铜拇指螺钉 / 螺纹柱 + 滚花黄铜帽螺母），刀面有一根小 `lateral_lever`（横向校准刀片），床后藏一只滚花黄铜 `depth_wheel`（进刀深度）；sole 上有用户握把（趾端转制 `front_knob` + 跟端直立开 D 形 `rear_tote` / 前冲 `front_horn` + 闭环 ring tote / 单只低 `palm_rest`）。默认成熟域：body_silhouette(3) × blade_clamp(3) × grip(3) 笛卡尔积的小型手持刨（机身长 155/200/245 mm、宽 30/52/62 mm、床角 20°/45°，随 Slot A 取值）。活动语义 = **夹刃 actuator**（PRIMARY：翻凸轮 REVOLUTE / 拇指螺钉 REVOLUTE / 帽螺母 CONTINUOUS，随 Slot B 变）+ **lateral_adjust**（REVOLUTE 绕 BED_NORMAL，横移校刀）+ **depth_adjust**（CONTINUOUS 绕 BED_UP，进刀）。

不该混入：
- **凿子 / 木工凿（chisel）**——单根带柄刀片、无铸铁机身 / 无斜床 / 无夹刃机构 / 无深度轮；本类核心是 body+frog+iron+clamp 四件套。
- **电动砂光机 / 电刨（power planer / sander）**——带电机外壳、旋转刀鼓 / 砂带、扳机开关；本类是纯手用、刀片 FIXED 床定、无电机。
- **刮刀 / 刮鸟（spokeshave / scraper）**——双手柄横握短体、无 sole 长机身 / 无 depth wheel / 无 lever cap；运动 spine 与握持完全不同。
- **木工锉 / rasp**——纯单体齿面工具，无任何活动件、无装配。

## 槽位 + 候选模块表

> **建模注记**：`body_silhouette`（Slot A）是 `plane_body` part **同一铸铁 body+frog 的 mesh 足迹 / 床角 / iron 宽度形态**（solid 高 casting / 矮 trough / 窄开 cheek），由 body+frog mesh helper 一次决定，**不改 part 树 / joint 拓扑**（仍 `plane_body` root + `cutting_iron` FIXED child + 三非 fixed joint）；列为候选轴以对齐 schema，与 blade_clamp × grip 笛卡尔积共同撑开多样性（见 §9）。`blade_clamp`（Slot B）才是改 PRIMARY 关节类型 / parent / part 数的真正拓扑轴；`grip`（Slot C）改 grip part 数 / 形态。

### Slot A：body_silhouette（sole / body 轮廓 + frog 床 + 床角 + iron 宽度 —— mesh+尺寸维度，不改拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| solid_block_45（基线）| rec_build-a-realistic-articulated-3d-model-of-a-hand_..._d722d7db（parent）| `_bench_plane_body` L115-183（solid 中央 block + 45° iron slot + spine relief）/ `_frog` L186-200（45° 12.5mm 床板）/ `_cutting_iron` L230-260（blade_w=BODY_WIDTH−0.020）/ BED_DEG=45 L61 / `_tilt_back` L106-112 | eligible if compatible | 经典 Bailey 平刨机身：BODY_LEN=0.245 / BODY_WIDTH=0.062 / 实心中央铸块（CHEEK_HEIGHT=0.040）、全宽闭口 throat、陡 45° frog；趾/跟 `toe_boss`/`heel_boss` 供握把 bolt |
| low_block_trough | rec_hand_plane_var_blocksole | `_block_plane_body` L119-183（短 sole + 两道 `left_wall`/`right_wall` 低 sidewall = 开顶 trough，无高 casting）/ `_frog` L186-200（薄 20° 床）/ `_cutting_iron` L235-263（blade_w=0.038）/ BED_DEG=20 L58 / WALL_HEIGHT=0.020 L52 | eligible if compatible | 短矮低角块刨：BODY_LEN=0.155 / BODY_WIDTH=0.052 / 无高中央 casting，仅两道低 sidewall 间开顶 trough、20° 整体床；body 矮（run_tests 断言 x_extent<0.170、max_z<WALL_TOP_Z+0.008 L623-634）|
| narrow_open_cheek | rec_hand_plane_var_rabbet | `_rabbet_plane_body` L105-183（−Y 全高 cheek + +Y `OPEN_CHEEK_HEIGHT`=0.003 lip + open_cut L125-132，全宽 iron slot）/ `_frog` L186-195 / 全宽 `_cutting_iron` L224-249（blade_w=BODY_WIDTH−0.002 跑满全宽）/ BED_DEG=45 L63 | eligible if compatible | 窄裁口/肩刨机身：BODY_LEN=0.200 / BODY_WIDTH=0.030 / 一侧 cheek 开口使 iron 跑满全宽做齐边切；run_tests 断言 body_width<0.045、iron 跑到两侧边 L596-619 |

### Slot B：blade_clamp（夹刃机构 —— **主机构槽**，决定 PRIMARY 关节类型 / parent 部件 / part 数）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| levercap_flipcam（基线）| rec_..._d722d7db（parent）| `_lever_cap` L263-292 + `lever_cap`(FIXED) `body_to_lever_cap` L533-546 / `_cam_lever` L295-318 + `cam_lever` part + `lever_cap_cam` **REVOLUTE axis=(0,−1,0)，parent=cap** L548-571 / `_cap_screw` L210-227（body inline visual L479-483）| eligible if compatible | polished 钢 lever cap 压刀（FIXED part），弹簧翻凸轮 `cam_lever`（独立 part）绕 **−Y REVOLUTE**（lower=0/upper=1.5）翻起释放；**cam 两级挂载 parent=lever_cap**；`cap_screw` 杆作 body visual。→ +2 part +1 REVOLUTE |
| crossbar_thumbscrew | rec_hand_plane_var_clampbar | `_clamp_bar` L279-322 + `clamp_bar`(FIXED) `body_to_clamp_bar` L586-599 / `_clamp_boss` L220-243 + body `for i in range(2)` `clamp_boss_{i}` L531-537 / `_thumbscrew_stud` L206-217（body visual L524-528）/ `_thumbscrew` L325-363 + `thumbscrew` part + `thumbscrew` joint **REVOLUTE axis=`BED_NORMAL`，parent=body** L601-622 | eligible if compatible | 平钢横压条（FIXED part）由两道铸 boss（body visual）+ 端 pin 钉住；滚花黄铜拇指螺钉 `thumbscrew`（独立 part）绕 **BED_NORMAL REVOLUTE**（lower=0/upper=6.28）在 `thumbscrew_stud` 上拧紧压条；**screw parent=body**。→ +2 part +1 REVOLUTE |
| capnut_post | rec_hand_plane_var_screwcap | `_cap_post` L222-239（body inline visual L452-458）/ `cap_nut`(KnobGeometry/KnobGrip/KnobBore) part L516-533 + `cap_nut_spin` **CONTINUOUS axis=`BED_NORMAL`，parent=body** L534-544 / iron `post_hole` L268-273 | eligible if compatible | 螺纹柱 `cap_post`（body visual）从 frog 穿出过 iron；滚花黄铜帽螺母 `cap_nut`（KnobGeometry 独立 part）绕 **BED_NORMAL CONTINUOUS** 旋下夹紧刀叠；**nut parent=body**，iron 有 `post_hole`。→ +1 part +1 CONTINUOUS |

### Slot C：grip（用户握把 —— 决定 grip part 数 / 形态，全 FIXED）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| knob_plus_Dtote（基线）| rec_..._d722d7db（parent）| `_front_knob` L380-400（XZ 旋转 mushroom revolve）+ `front_knob` part + `body_to_front_knob`(FIXED) L485-500 / `_rear_tote` L403-439（XZ polyline extrude + 椭圆 `hole` cut，开 D 形）+ `rear_tote` part + `body_to_rear_tote`(FIXED) L502-516 | eligible if compatible | 传统两件握把：趾 boss 上转制 `front_knob` + 跟 boss 上直立**开 D 形** `rear_tote`（一侧开口窗）；**2 个 FIXED part** |
| horn_plus_ringtote | rec_hand_plane_var_closedtote | `_front_horn_geom` L384-423（`section_loft`/`SectionLoftSpec`/`LoftSection` 前冲弯角 horn）+ `front_horn` part（`mesh_from_geometry`）+ `body_to_front_horn`(FIXED) L514-529 / `_rear_tote` L426-468（闭环 outer polyline + 全包 oval `hole`）+ `rear_tote` part + `body_to_rear_tote`(FIXED) L531-545 | eligible if compatible | 前冲弯 lofted 前 horn（section_loft 曲面）+ **闭环全包窗** ring tote（grip 窗四周全包，区别于开 D）；**2 个 FIXED part**；run_tests 断言 horn 前于其基座 L711-715、tote 闭环 L721-725 |
| single_palm_hump | rec_hand_plane_var_palmgrip | `_palm_rest` L373-419（XZ 四分椭圆 revolve dome ∩ box footprint，YZ `groove` 半圆指槽 cut）+ `palm_rest` part + `body_to_palm_rest`(FIXED) L465-481 / body `heel_boss` 加宽 L153-157（无 toe boss）| eligible if compatible | 单手低 palm-hump 后掌托 + 纵向指槽（dome∩box+groove），**删掉前 knob**（heel boss 加宽至 0.068×0.048）；**1 个 FIXED part**；run_tests 断言 rest 在机尾 cx<0、低 profile z-extent<0.035 L632-648 |

## 槽位图（slot graph）

pattern: parallel_children（固定 root `plane_body`；`cutting_iron` FIXED 床定挂 body；blade_clamp 与 grip 的部件按候选挂 body 或 cap；lateral_lever / depth_wheel 是共享活动 spine 挂 body；body_silhouette 只换 body+frog mesh + 床角）

```
plane_body (root, 坐地 z=0; 由 body_silhouette 决定 sole+block/trough/cheek mesh + frog 床 mesh + BED_DEG + iron 宽 + 趾/跟 boss)
  │  （body visual：casting + sole_edge + frog + depth_stud + 夹刃硬件 inline visual：随 Slot B 取 cap_screw / thumbscrew_stud+clamp_boss_{i} / cap_post）
  │
  ├── cutting_iron ──[body_to_cutting_iron: FIXED]   ← 全候选共享，床定于刨口；iron 是否带 post_hole 随 Slot B
  │
  ├── [blade_clamp slot]  (互斥三选一；PRIMARY 关节类型/parent/part 数随候选变)
  │     ├─ levercap_flipcam : lever_cap(FIXED part) ──[body_to_lever_cap: FIXED]
  │     │                     cam_lever(独立 part) ──[lever_cap_cam: REVOLUTE axis=(0,−1,0), parent=lever_cap, origin=CAM_PIVOT]  (两级挂载)
  │     │                     cap_screw = body visual (无 joint)
  │     ├─ crossbar_thumbscrew : clamp_bar(FIXED part) ──[body_to_clamp_bar: FIXED]
  │     │                        thumbscrew(独立 part) ──[thumbscrew: REVOLUTE axis=BED_NORMAL, parent=body, origin=_bed_pt(BAR_U,BAR_M_TOP)]
  │     │                        clamp_boss_{i} i∈range(2) + thumbscrew_stud = body visual (无 joint)
  │     └─ capnut_post : cap_nut(KnobGeometry 独立 part) ──[cap_nut_spin: CONTINUOUS axis=BED_NORMAL, parent=body, origin=_bed_pt(POST_U,CAP_NUT_M)]
  │                      cap_post = body visual (无 joint); iron 带 post_hole
  │
  ├── [grip slot]  (互斥三选一，全 FIXED)
  │     ├─ knob_plus_Dtote   : front_knob ──[body_to_front_knob: FIXED]; rear_tote(开 D) ──[body_to_rear_tote: FIXED]
  │     ├─ horn_plus_ringtote: front_horn ──[body_to_front_horn: FIXED]; rear_tote(闭环) ──[body_to_rear_tote: FIXED]
  │     └─ single_palm_hump  : palm_rest ──[body_to_palm_rest: FIXED]  (无前 knob)
  │
  └── [共享活动 spine，全候选恒有，挂 body]
        ├─ lateral_lever ──[lateral_adjust: REVOLUTE axis=BED_NORMAL, parent=body, origin=LAT_PIVOT, ±0.35]  (骑刀面)
        └─ depth_wheel   ──[depth_adjust: CONTINUOUS axis=BED_UP, parent=body, origin=DEPTH_CENTER]  (captured 在 depth_stud)
```

接口点位与 joint 语义：
- **body → cutting_iron（全候选共享）**：mating = frog 床面。FIXED `body_to_cutting_iron`，iron mesh 在 body-world 直接建（`_tilt_back` 到 BED_DEG，刀刃落 `_bed_pt(0, m)` 在 mouth）。iron 床定于 frog（`allow_overlap(iron, body, elem_b="frog")` + `expect_contact(iron, body, 0.002)`，全样本统一）。
- **blade_clamp → PRIMARY actuator（互斥，consumer-joint 字段随候选）**：
  - levercap_flipcam：`lever_cap` FIXED 压在 chipbreaker 上（`_bed_pt(0.0018, 0.0068)` 坐 m=0.0068）；`cam_lever` boss captured 在 cap pin、finger 平铺 spine。`lever_cap_cam` **REVOLUTE axis=(0,−1,0)，parent=lever_cap**，origin=CAM_PIVOT=`_bed_pt(0.094, 0.0238)`（落 spine 顶端 pin），lower=0（夹紧平铺）/upper=1.5（翻起释放）。
  - crossbar_thumbscrew：`clamp_bar` FIXED 坐 chipbreaker top（`_bed_pt(BAR_U, BAR_M_BOT)`），两端 pin-hole captured 在 `clamp_boss_{i}` pin；`thumbscrew` 绕 `thumbscrew_stud`。`thumbscrew` joint **REVOLUTE axis=BED_NORMAL，parent=body**，origin=`_bed_pt(BAR_U, BAR_M_TOP)`（压条顶面），lower=0/upper=6.28（拧紧不平移，run_tests 断言旋后高度不变 L861-865）。
  - capnut_post：`cap_post` body visual 从 frog 穿出过 iron `post_hole`；`cap_nut`（KnobGeometry，mounting face z=0、轴 +Z，visual origin pitch +45° 对齐 BED_NORMAL）。`cap_nut_spin` **CONTINUOUS axis=BED_NORMAL，parent=body**，origin=`_bed_pt(POST_U, CAP_NUT_M)`（chipbreaker top），旋转不平移（run_tests 断言 spun 后 center 不动 L771-780）。
- **grip → body（互斥，全 FIXED）**：所有 grip part 用 `body.part()` + visual origin=`Origin(xyz=(GRIP_X, 0, SOLE_TOP_Z))` 坐 boss + `body_to_<grip>` FIXED（identity origin）。knob_plus_Dtote / horn_plus_ringtote 各 2 个 FIXED part（前+后）；single_palm_hump 仅 1 个（无前 knob，heel boss 加宽）。
- **共享活动 spine → body（全候选恒有）**：`lateral_adjust` REVOLUTE axis=BED_NORMAL，parent=body，origin=LAT_PIVOT=`_bed_pt(~0.075-0.105, 0.003)`（刀面 boss riveted），±0.35 横移；`depth_adjust` CONTINUOUS axis=BED_UP，parent=body，origin=DEPTH_CENTER=`_bed_pt(~0.035-0.085, -0.0085)`（床后 stud 上），captured 在 `depth_stud`。
- **mating policy**：所有 captured 接口（iron-on-frog 床定、cap/bar/nut 压刀、cam-boss-on-cap-pin、bar-end-on-boss-pin、thumbscrew/cap_nut-bore-on-stud/post、lateral-boss-riveted-in-iron、wheel-bore-on-stud）是 captured-fit / 床定贴合，**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：cam q=0 平铺夹紧 / thumbscrew q=0 拧紧 / cap_nut q=0 旋下；lateral q=0 不偏；depth wheel q=0。所有夹刃 actuator rest 为**夹紧姿态**（与 viewer 目检一致）。
- **互斥 / 可选 / 派生**：blade_clamp 三候选互斥（一次只一种夹刃）；grip 三候选互斥；single_palm_hump 删前 knob（只 1 part）；body_silhouette 与 clamp/grip 正交（任意组合合法，仅尺寸联动，见 §9）；iron `post_hole` 仅 capnut_post 候选才挖。

## 每槽位 Module Emits / Interfaces

### Slot A / body_silhouette（以 solid_block_45 为例；low_block_trough / narrow_open_cheek 仅换 body+frog mesh + BED_DEG + iron 宽 + boss）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plane_body`（root，visual：`casting` body mesh + `sole_edge` 亮钢边 + `frog` 床 + `depth_stud` + 夹刃硬件 inline visual）| parent `_bench_plane_body` L115-183 + assembly L452-483 / blocksole L119-200 / rabbet L105-195 |
| internal joints | 无（plane_body 是 root）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | frog 床面（供 cutting_iron FIXED 接入）+ 刀面（供 lateral/clamp 接入）+ 床后 stud（供 depth wheel）+ 趾/跟 boss（供 grip）| parent L186-200, L153-164 |

### Slot A / cutting_iron（共享 child，宽度随 body_silhouette）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cutting_iron`（visual `iron`：blade + chipbreaker `cap` + 校刀 slot；narrow_open_cheek 全宽、capnut_post 带 post_hole）| parent `_cutting_iron` L230-260 / rabbet L224-249 / screwcap `post_hole` L268-273 |
| internal joints | `body_to_cutting_iron` FIXED，origin=Origin()（iron mesh 已在 body-world）| parent L525-531 |
| upstream interface | 床定 frog（`expect_contact(iron, body, 0.002)`，`allow_overlap(iron, body, elem_b="frog")`）| parent L719-722, L777 |

### Slot B / blade_clamp — levercap_flipcam
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_cap`（FIXED part，visual `cap`）+ `cam_lever`（活动 part，visual `cam`：boss+finger）；`cap_screw` 作 body visual | parent `_lever_cap` L263-292 / `_cam_lever` L295-318 / `_cap_screw` L210-227 |
| internal joints | `body_to_lever_cap` FIXED L540-546 + `lever_cap_cam` **REVOLUTE axis=(0,−1,0)，parent=cap**，origin=CAM_PIVOT，lower=0/upper=1.5 | parent L560-571 |
| upstream interface | cap 坐 chipbreaker（`allow_overlap(cap,iron)`）；cam boss captured 在 cap pin（`allow_overlap(cam,cap)`，翻起仍 `expect_contact(cam,cap)`）| parent L731-738, L798-801 |

### Slot B / blade_clamp — crossbar_thumbscrew
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_bar`（FIXED part，visual `bar`）+ `thumbscrew`（活动 part，visual `screw` 滚花 disc）；`clamp_boss_{i}`×2 + `thumbscrew_stud` 作 body visual | clampbar `_clamp_bar` L279-322 / `_thumbscrew` L325-363 / `_clamp_boss` L220-243 |
| internal joints | `body_to_clamp_bar` FIXED L593-599 + `thumbscrew` **REVOLUTE axis=BED_NORMAL，parent=body**，origin=`_bed_pt(BAR_U,BAR_M_TOP)`，lower=0/upper=6.28 | clampbar L613-622 |
| upstream interface | bar 端 pin-hole captured 在 `clamp_boss_{i}` pin（`allow_overlap(bar,body,elem_b="clamp_boss_*")`）；screw bore 骑 stud（`allow_overlap(screw,body,elem_b="thumbscrew_stud")`，旋后高度不变）| clampbar L797-812, L853-865 |

### Slot B / blade_clamp — capnut_post
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap_nut`（活动 part，KnobGeometry 滚花黄铜，visual `nut`）；`cap_post` 作 body visual；iron 挖 `post_hole` | screwcap `cap_nut` L516-533 / `_cap_post` L222-239 / iron post_hole L268-273 |
| internal joints | `cap_nut_spin` **CONTINUOUS axis=BED_NORMAL，parent=body**，origin=`_bed_pt(POST_U,CAP_NUT_M)`，visual origin rpy=(0,π/4,0) | screwcap L534-544 |
| upstream interface | nut bore captured 在 cap_post（`allow_overlap(cap_nut,body,elem_b="cap_post")`）；nut 底面压 chipbreaker（`allow_overlap(cap_nut,iron)`，旋转不平移）| screwcap L703-714, L762-780 |

### Slot C / grip — knob_plus_Dtote
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_knob`（FIXED part，旋转 mushroom）+ `rear_tote`（FIXED part，开 D 形 extrude+椭圆窗）| parent `_front_knob` L380-400 / `_rear_tote` L403-439 |
| internal joints | `body_to_front_knob` FIXED L494-500 + `body_to_rear_tote` FIXED L510-516（均 identity origin，visual origin 落 boss）| parent L485-516 |
| upstream interface | knob 坐 toe_boss、tote 坐 heel_boss（`allow_overlap(knob/tote,body,elem_b="casting")` + `expect_contact 0.004`）| parent L759-766, L774-775 |

### Slot C / grip — horn_plus_ringtote
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_horn`（FIXED part，section_loft 前冲弯角，`mesh_from_geometry`）+ `rear_tote`（FIXED part，闭环全包窗）| closedtote `_front_horn_geom` L384-423 / `_rear_tote` L426-468 |
| internal joints | `body_to_front_horn` FIXED L523-529 + `body_to_rear_tote` FIXED L539-545 | closedtote L514-545 |
| upstream interface | horn 坐 toe_boss、tote 坐 heel_boss（`allow_overlap(horn/tote,body,elem_b="casting")`）| closedtote L798-805 |

### Slot C / grip — single_palm_hump
| emits | 描述 | 来源 |
|---|---|---|
| parts | `palm_rest`（FIXED part，revolve dome ∩ box + 指槽 cut）；body heel_boss 加宽、无 toe_boss | palmgrip `_palm_rest` L373-419 / body L153-158 |
| internal joints | `body_to_palm_rest` FIXED L475-481 | palmgrip L465-481 |
| upstream interface | palm_rest 坐加宽 heel_boss（`allow_overlap(rest,body,elem_b="casting")` + `expect_contact 0.004`）| palmgrip L721-728, L732 |

### 共享活动 spine（lateral_lever + depth_wheel，全候选恒有，非 slot）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lateral_lever`（活动 part，boss+stem+disc）+ `depth_wheel`（活动 part，滚花 disc `for i in range(24)` + bore）| parent `_lateral_lever` L321-348 / `_depth_wheel` L351-377 |
| internal joints | `lateral_adjust` REVOLUTE axis=BED_NORMAL，parent=body，origin=LAT_PIVOT，±0.35 + `depth_adjust` CONTINUOUS axis=BED_UP，parent=body，origin=DEPTH_CENTER | parent L583-610 |
| upstream interface | lateral boss riveted 入 iron（`allow_overlap(lat,iron)`，横移仍贴刀面）；wheel bore 骑 depth_stud（`allow_overlap(wheel,body,elem_b="depth_stud")`，旋后仍接触）| parent L743-758, L805-829 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_silhouette | enum | solid_block_45 / low_block_trough / narrow_open_cheek | solid_block_45 | choice | 由 deterministic procedural sampler 选；决定 body+frog mesh + BED_DEG + iron 宽 + boss | Slot A 表 |
| blade_clamp | enum | levercap_flipcam / crossbar_thumbscrew / capnut_post | levercap_flipcam | choice | sampler 选；主机构（互斥），PRIMARY 关节类型/parent 随候选 | Slot B 表 |
| grip | enum | knob_plus_Dtote / horn_plus_ringtote / single_palm_hump | knob_plus_Dtote | choice | sampler 选；grip part 数/形态（互斥）| Slot C 表 |
| palette_style | enum | japanned_cast_iron / bare_steel_sole / brass_adjusters / boxwood_tote / nickel_modern | japanned_cast_iron | palette | palette only，**不计入 slot_choice**；每 seed 采一套（见下表）| 各样本材质 + 现实刨配色 |
| body_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_LEN（保机身比例），clamp；随 body_silhouette 基线（0.245/0.155/0.200）| parent L52 / blocksole L49 / rabbet L54 |
| body_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_WIDTH（联动 iron 宽 / cap 宽 / frog 宽），clamp | parent L53 / rabbet L55 |
| body_height_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 CHEEK_HEIGHT/WALL_HEIGHT（中央块/sidewall 高 → frog 高、夹刃硬件高），clamp | parent L55 / blocksole L52 |
| bed_angle | derived | {45° if solid_block_45/narrow_open_cheek, 20° if low_block_trough} | 45° | conditional→equation | **由 body_silhouette 决定**（非独立采样）；驱动 SQ/CQ_BED/SQ_BED、`_bed_pt`、`_tilt_back`、BED_NORMAL/BED_UP 全套 | parent L61 / blocksole L58 |
| iron_width | derived | derived | — | equation | `= BODY_WIDTH·body_width_scale − inset`（solid/block: −0.020；narrow_open_cheek: −0.002 跑满全宽），不独立采样 | parent L233 / blocksole L238 / rabbet L227 |
| cam_open_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 blade_clamp=levercap_flipcam 有效；缩放 `lever_cap_cam` upper（保 ≤π·0.95）| parent L570 |
| screw_turn_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 blade_clamp=crossbar_thumbscrew 有效；缩放 `thumbscrew` upper（≤2π，转角行程）| clampbar L621 |
| lateral_range_scale | float | [0.80, 1.10] | 1.0 | independent | 缩放 `lateral_adjust` lower/upper（保 |q|≤0.40），全候选共享 | parent L590 |
| knob_height_scale | float | [0.85, 1.15] | 1.0 | conditional | grip=knob_plus_Dtote/horn_plus_ringtote 时缩放 front knob/horn 高（保 >0.035 读作握把）| parent L380-400 / closedtote L395-402 |
| tote_height_scale | float | [0.85, 1.15] | 1.0 | conditional | grip 含 tote 时缩放 rear tote 高（保 >0.07 读作直立把手）；palm_hump 无效 | parent L403-439 / rabbet L675 |
| (—) | constraint | — | — | inequality | iron 床定不超 frog：iron 床长 ≤ frog 床长 + chipbreaker 露头；违反按比例缩 blade_len 或缩 body_len | parent `_frog` L186-200 vs `_cutting_iron` L230-260 |
| (—) | constraint | — | — | inequality | 夹刃 actuator 落在刀叠上：clamp 部件 m 位（cap m=0.0068 / bar m=0.007 / nut m=0.007）+ actuator origin 必落 iron+chipbreaker 实体面；违反抬/降 m 或拒绝重采 | parent L291 / clampbar L88-89 / screwcap L100 |
| (—) | constraint | — | — | inequality | narrow_open_cheek × crossbar_thumbscrew：BAR_Y_HALF 跨距须随 body_width 缩（源按 62mm 写死 0.022）；30mm 体宽时缩到 ≤(body_width/2 − margin)，否则压条悬出窄体 | clampbar L90 / rabbet L55 |
| (—) | constraint | — | — | inequality | low_block_trough × 含 tote 候选（非 palm）：tote 高（~0.12）远高于矮机身（WALL_HEIGHT~0.02），须复核比例或限 tote_height_scale 下界；现实块刨多配 palm_hump | source map 排除项 / blocksole L52 vs parent L403-439 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 7★ 样本观察的真实材质 / 色集 + 现实刨配色）：
| palette_style | body(casting) | sole_edge | iron/blade | clamp(cap/bar/nut) | adjusters(wheel/screw) | grip(knob/tote/horn/palm) | 来源样本 |
|---|---|---|---|---|---|---|---|
| japanned_cast_iron（默认）| 黑漆铸铁 (0.10,0.10,0.11) | 亮钢 (0.78,0.79,0.82) | blade 钢 (0.70,0.71,0.74) | polished 钢 (0.78,0.79,0.82) | 黄铜 (0.80,0.62,0.22) | 玫瑰木 rosewood (0.40,0.16,0.10) | 全 7 样本基线 |
| bare_steel_sole | 黑漆铸铁 | 抛光裸钢 sole（更亮 0.84,0.85,0.88）| blade 钢 | polished 钢 | 黄铜 | rosewood | parent `bright_steel` 外推（裸钢 sole） |
| brass_adjusters | 黑漆铸铁 | 亮钢 | blade 钢 | 黄铜 lever cap（黄铜面 cap 变体）| 黄铜 wheel+screw（强调黄铜调节件）| rosewood | clampbar/screwcap 黄铜 thumbscrew/cap_nut 外推到 cap |
| boxwood_tote | 深灰铸铁 (0.13,0.13,0.14) | 亮钢 | blade 钢 | polished 钢 | 黄铜 | 浅黄杨木 boxwood/beech (0.72,0.58,0.32) | rosewood→浅木把手外推（现实刨常见山毛榉/黄杨把手）|
| nickel_modern | 黑漆铸铁 | 镍亮 sole (0.86,0.87,0.89) | blade 钢 | 镍镀 cap (0.84,0.85,0.87) | 镍镀 wheel+screw | 黑胶木/染黑木 (0.18,0.16,0.15) | 现代镍镀刨配色外推（Lie-Nielsen/现代 No.4）|

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。bed_angle 与 iron_width 是**派生量**（bed_angle 由 body_silhouette 定、iron_width 由 body_width·scale 定），不独立采样。scale 只动安全比例 / 行程 / 角度，**绝不改变 body_silhouette / blade_clamp / grip 的拓扑或 PRIMARY 关节类型**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（body_silhouette / blade_clamp / grip）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 形成结构差异轴。clamp 真实产品域里没有"任意 N 个刀片 / N 个把手 / N 个深度轮"的轴。
- **存在固定 N 的对称 / 阵列 / 滚花 visual（非可变轴，不进 slot_choice）**：
  - `depth_wheel` 滚花：全样本用 `for i in range(24)`（n=24，parent L360 / blocksole L372 用 n_knurls=24 / rabbet n_knurls=20）发射等角凹槽 cut（**内嵌 cut，非独立 part，合规**），随 module 固定。
  - `thumbscrew` 滚花（crossbar_thumbscrew）：`for i in range(24)`（clampbar L339）发射等角凹槽 cut，module-local 固定 N。
  - `cap_nut` 滚花（capnut_post）：KnobGeometry 的 `KnobGrip(count=24)`（screwcap L524）由 SDK 内部发射，module-local 固定。
  - `clamp_boss_{i}`（crossbar_thumbscrew）：body `for i in range(2)`（clampbar L531-537，y_sign=1−2i）发射两道对称 boss + pin；`clamp_bar` 端 pin-hole 也 `for i in range(2)`（clampbar L309-317）。**正确的 copy-loop 写法**，固定 N=2 对称对。
- 这些都是 **module-local 固定阵列 / 滚花**（depth wheel / thumbscrew / cap_nut 凹槽 = 共享 helper 内 `for i in range(n)` 等角发射的内嵌 cut；clampbar 两端 boss/pin = `for i in range(2)` 对称发射），按 module 而非 multiplicity 轴声明，无独立 joint（FIXED 装饰，inline 到承载 part/body visual，Rule 1）。

## 拓扑多样性审计

总组合数：body_silhouette(3) × blade_clamp(3) × grip(3) = **27**（全部正交合法，见 §9 兼容矩阵——无硬非法组合需 gate，仅 2 条"比例需 controlled-param 收口"项）。

仅 blade_clamp(3) × grip(3) = **9 ≥**（接近门控）；其中 PRIMARY joint 拓扑差异来自 blade_clamp 的 {REVOLUTE flip（cam parent=cap，两级）/ REVOLUTE spin（screw parent=body）/ CONTINUOUS spin（nut parent=body）} 三类真实关节拓扑（类型 × parent 部件 × part 数都不同）；叠 body_silhouette(3) → 27 ≥ 10，充裕。

理由：blade_clamp 单独提供 3 种真正不同的 PRIMARY 关节拓扑（REVOLUTE/REVOLUTE/CONTINUOUS × parent=cap/body/body × part 数 +2/+2/+1），grip 提供 2-part / 2-part / 1-part 的 part 树差异，body_silhouette 提供 45°/20°/45° 床角 + 三种 body mesh + iron 宽度。三轴自然进 `slot_choices_for_seed` 的 tuple（`("body_silhouette",m)`、`("blade_clamp",m)`、`("grip",m)`），27 distinct 远超 ≥10。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（body_silhouette / blade_clamp / grip），经兼容矩阵合法化（本类三轴正交，无硬非法组合，仅做 conditional scale + 比例收口解析），再派生 bed_angle / iron_width，再 uniform 各连续 scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看三种夹刃机构 actuate：cam 翻起 / thumbscrew 旋 / cap_nut 旋 + lateral 横移 + depth wheel 旋 + 三种 grip 形态 + 20°/45° 床角）。


Controlled local parameterization：见 §参数表的 body_len_scale / body_width_scale / body_height_scale / lateral_range_scale（independent）+ bed_angle / iron_width（equation/conditional 派生）+ cam_open_scale（@levercap）/ screw_turn_scale（@thumbscrew）/ knob_height_scale·tote_height_scale（@含 tote/knob grip）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：cam_open 仅 levercap、screw_turn 仅 thumbscrew、knob/tote_height 仅含相应 grip）→ 由 body_silhouette 派生 bed_angle（45/20）→ 采 independent 机身 scale → 派生 iron_width（随 body_width·scale + 候选 inset）→ 用四条 inequality（iron 不超 frog、actuator 落刀叠、bar 跨距随窄体、矮机身配高 tote 比例）投影 / 回缩。跨部件依赖（iron 长 vs frog、bar 跨距 vs body_width、tote 高 vs 机身高）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 iron-on-frog 床定 / cam-on-cap / nut-on-post captured 接口、三 actuator joint origin、固定阵列 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（body_silhouette/blade_clamp/grip），派生 bed_angle/iron_width，再解析 conditional scale，再 uniform 各 independent scale，采 palette_style | slot_choices_for_seed 含 `("body_silhouette",m)`/`("blade_clamp",m)`/`("grip",m)` 且与 build 一致 |
| compatibility matrix | **三轴正交，全 27 组合结构合法**——无硬非法组合需 gate。两条"比例收口"conditional（非排除）：(1) **narrow_open_cheek × crossbar_thumbscrew**：BAR_Y_HALF 跨距须缩到随 30mm 体宽（源 0.022 按 62mm 写死），否则压条悬出窄体 → 缩 bar 跨距至 ≤(body_width/2−margin)；(2) **low_block_trough × {knob_plus_Dtote, horn_plus_ringtote}**：高 tote/horn 配矮块刨机身比例失真 → 限 tote_height_scale 下界或复核（不排除组合，现实块刨多配 palm 但 knob+矮体也存在）。conditional scale 仅在对应 module 生效：cam_open@levercap、screw_turn@thumbscrew、knob/tote_height@含相应 grip。iron `post_hole` 仅 capnut_post 挖。 | 无 floating / collision / 压条悬出窄体 / actuator 落空 / iron 超 frog / tote 比例失真 |
| controlled local variation | 4 independent + 2 派生 + 4 conditional clamped scale，每 build 统一；conditional 随 slot 解析 | 比例变化不破坏 iron-on-frog 床定、cam/screw/nut captured、三 actuator origin、夹紧 rest 姿态、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐夹刃机构 QC（cam 翻起 / thumbscrew 旋不平移 / cap_nut 旋不平移 + lateral 横移 + depth 旋 + 20°/45° 床角）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_silhouette | 3 | yes | yes | solid_block_45（45°高 casting）/ low_block_trough（20°矮 trough）/ narrow_open_cheek（45°窄开 cheek）；mesh+床角+iron 宽维度 |
| blade_clamp | 3 | yes | yes | levercap_flipcam（REVOLUTE flip，cam@cap，+2 part）/ crossbar_thumbscrew（REVOLUTE spin，screw@body，+2 part）/ capnut_post（CONTINUOUS spin，nut@body，+1 part）|
| grip | 3 | yes | yes | knob_plus_Dtote（2 part）/ horn_plus_ringtote（2 part，section_loft）/ single_palm_hump（1 part，无前 knob）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("body_silhouette",m)`/`("blade_clamp",m)`/`("grip",m)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；bed_angle 由 body_silhouette 派生（45/20）、iron_width 由 body_width·scale+inset 派生；cam_open/screw_turn/knob_height/tote_height 为 conditional 随 blade_clamp/grip 解析；四条 inequality（iron 不超 frog、actuator 落刀叠、bar 跨距随窄体、矮体配高 tote 比例）在 resolve 内投影 / 回缩
- compatibility matrix 三轴正交无硬非法组合；conditional scale 仅在对应 module 生效（不在无 cam 的候选上设 cam_open）；iron post_hole 仅 capnut_post 挖
- 连续 scale clamp 后不破坏 iron-on-frog 床定 / cam-on-cap / nut-on-post / bar-on-boss captured 接口、三 actuator joint origin、夹紧 rest 姿态、固定阵列 visual
- 关键 joint：`body_to_cutting_iron` FIXED（全候选共享）；blade_clamp=levercap_flipcam 时 `lever_cap_cam` REVOLUTE axis≈(0,−1,0)（abs(axis[1])>0.99、abs(axis[0])<0.01）**parent=lever_cap**；=crossbar_thumbscrew 时 `thumbscrew` REVOLUTE axis≈BED_NORMAL（axis[0]>0.5、axis[2]>0.5、abs(axis[1])<0.01）parent=body；=capnut_post 时 `cap_nut_spin` CONTINUOUS axis≈BED_NORMAL parent=body；`lateral_adjust` REVOLUTE axis≈BED_NORMAL（全候选共享）；`depth_adjust` CONTINUOUS axis≈BED_UP（全候选共享）
- captured 接口：element-scoped `allow_overlap`（`iron`↔`frog`；clamp 部件↔`iron`；`cam`↔`cap`；`bar`↔`clamp_boss_{i}`；`screw`↔`thumbscrew_stud`；`cap_nut`↔`cap_post`；`lever`↔`iron`；`wheel`↔`depth_stud`/`iron`/`frog`；grip↔`casting`），照搬各样本 run_tests 的 allow_overlap 段
- 固定阵列 / 滚花 visual 遵循 `depth_wheel`/`thumbscrew` `for i in range(24)` 凹槽 + `clamp_boss_{i}` `for i in range(2)` 对称 + Rule 1（无独立 joint）
- 夹紧 rest pose：cam q=0 平铺 / thumbscrew q=0 拧紧（旋后高度不变）/ cap_nut q=0（旋后 center 不动）；lateral q=0
- grandfather：所有 captured / 床定接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- blade_clamp ∈ {crossbar_thumbscrew, capnut_post} 时断言无 `lever_cap_cam` joint、无 `cam_lever`/`lever_cap` part；=levercap_flipcam 时断言无 `thumbscrew`/`cap_nut_spin` joint
- grip=single_palm_hump 时断言无 `front_knob`/`front_horn`/`rear_tote` part（仅 `palm_rest`）

## Reject cases

- blade_clamp=crossbar_thumbscrew/capnut_post 仍发射 `lever_cap_cam` REVOLUTE 或 `cam_lever`/`lever_cap` part → 违反这两候选的夹刃拓扑（PRIMARY 关节应是 thumbscrew REVOLUTE@body / cap_nut CONTINUOUS@body）。
- levercap_flipcam 把 `cam_lever` 挂在 body 而非 lever_cap → 违反两级挂载（cam parent=cap，源 L562），翻起时几何脱节。
- 把 depth_wheel/thumbscrew/cap_nut 滚花凹槽或 clamp_boss 当独立活动 part 加 joint → 违反 Rule 1（module-local 固定阵列/滚花，应 inline 为 wheel/screw/body visual 内嵌 cut）。
- 夹刃 actuator rest pose 设成释放/松开（cam q=upper 翻起 / nut q≠0）而非 q=0 夹紧 → current-pose 与 viewer 目检不符（所有样本 rest 为夹紧平铺）。
- actuator origin 放在机身中心或任意点而非真实硬件面（CAM_PIVOT spine 顶 / BAR_M_TOP 压条顶 / cap_post chipbreaker top）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- body_silhouette 改了 bed_angle 但未同步 SQ/`_bed_pt`/`_tilt_back`/BED_NORMAL/BED_UP → iron/clamp/wheel 床姿与床面错位、actuator 轴算错；bed_angle 必须驱动全套床坐标。
- iron 床长超 frog 床长致刀悬空于刨口外 → §7 第一条 inequality FAIL；须缩 blade_len 或缩 body_len。
- narrow_open_cheek × crossbar_thumbscrew 不缩 BAR_Y_HALF（沿用 62mm 体宽的 0.022）→ 压条悬出 30mm 窄体；须随 body_width 缩跨距。
- 给 captured / 床定接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质 / 床角（palette_style / body scale / 45° vs 20°）当新 candidate 塞进 slot → 不是结构差异（床角是 body_silhouette 派生量，不入独立 slot）。
- 把凿子 / 电刨 / 刮刀语义混入（单刀片带柄 / 电机刀鼓 / 双手柄横握）→ 出类，本类是铸铁机身 + 斜床 + FIXED 刀片 + 夹刃机构的手用刨。

## 与相邻类别的边界

- 不该混入：**凿子 / 木工凿（chisel）**——单根带柄刀片，无铸铁机身 / 无 frog 斜床 / 无夹刃机构 / 无深度轮；本类核心是 body+frog+iron+clamp 四件套（运动 spine 与单体凿完全不同）。
- 不该混入：**电动砂光机 / 电刨（power planer / belt sander）**——带电机外壳 + 旋转刀鼓 / 砂带 + 扳机；本类纯手用、刀片 FIXED 床定、无电机驱动旋转件。
- 不该混入：**刮刀 / 刮鸟（spokeshave / cabinet scraper）**——双手柄横握短体、无 sole 长机身 / 无 depth wheel / 无 lever cap；握持与运动 spine 不同（如需可作单独 slug）。
- 不该混入：**木工锉 / rasp / file**——纯单体齿面工具，无任何活动件、无装配（缺整个 articulation 家族）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **bed_angle 建模为 body_silhouette 派生量**（45° solid/rabbet、20° block），不入独立 slot，由它驱动全套床坐标（SQ/`_bed_pt`/`_tilt_back`/BED_NORMAL/BED_UP）是否接受；(2) blade_clamp 三候选 PRIMARY 关节的 **parent 随候选变**（cam parent=cap 两级 / thumbscrew·cap_nut parent=body）+ **joint type 随候选变**（REVOLUTE flip / REVOLUTE spin / CONTINUOUS spin）是 InterfaceSpec consumer-joint 的核心差异点，模板须分支实现，确认实现策略；(3) lateral_lever + depth_wheel 作为**共享活动 spine**（全候选恒有，不入 slot）是否合适，还是要拆成可选 slot；(4) narrow_open_cheek × crossbar_thumbscrew 的 BAR_Y_HALF 随 body_width 收口、low_block_trough × 高 tote 的比例收口，两条作 conditional scale 收口（非组合排除）是否接受；(5) Topology target 27<300 的说明是否接受（本小类真实结构上限）；(6) palette_style 5 套是否合适，boxwood_tote/nickel_modern 两套为现实刨配色外推；(7) 是否需为块刨补造 wedge-clamp / wooden-body 候选以扩 Slot A/B 词汇表（当前 fork 池仅 7 样本，三槽各恰 3 候选已达门控）。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- **bed_angle 驱动**：body_silhouette 决定 BED_DEG（45/20）后，必须按角度重算 SQ（45° 用 √0.5；20° 用 sin/cos，对照 blocksole L59-61 的 CQ_BED/SQ_BED），`_bed_pt` / `_tilt_back` / BED_NORMAL / BED_UP / 各 stud/post 旋转角（blocksole 用 −(90−BED_DEG)，parent 用 ±45）随之解析。这是 Slot A 与床坐标耦合的关键收口点。
- **blade_clamp 分支挂载**：levercap_flipcam 的 `cam_lever` parent=`lever_cap`（两级，源 parent L562）；crossbar_thumbscrew 的 `thumbscrew` parent=body + bar/boss FIXED；capnut_post 的 `cap_nut` parent=body（KnobGeometry visual origin rpy=(0,π/4,0) 对齐 BED_NORMAL）+ iron 挖 post_hole。模板按 blade_clamp 选不同 part/joint 工厂；iron mesh 是否挖 post_hole 是 conditional。
- **共享 helper**：`_bed_pt`/`_tilt_back`（床坐标，按 bed_angle 解析）、body+frog mesh helper（按 body_silhouette 切 `_bench_plane_body`/`_block_plane_body`/`_rabbet_plane_body` + `_frog`）、`_cutting_iron`（按 body_width 派生 iron_width + 候选 inset；capnut_post 挖 post_hole）、`_lateral_lever`/`_depth_wheel`（共享 spine，滚花 `for i in range(24)`）、clamp 工厂（`_lever_cap`+`_cam_lever`+`_cap_screw` / `_clamp_bar`+`_thumbscrew`+`_clamp_boss`×2+`_thumbscrew_stud` / `_cap_post`+KnobGeometry nut）、grip 工厂（`_front_knob`+`_rear_tote`(开 D) / `_front_horn_geom`(section_loft)+`_rear_tote`(闭环) / `_palm_rest`）。
- captured 接口 allow_overlap：`run_hand_plane_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L719-770、blocksole L714-773、rabbet L698-757、clampbar L781-840、screwcap L699-742、closedtote L758-809、palmgrip L681-728）。
- conditional 范围解析顺序：先采 body_silhouette / blade_clamp / grip → 派生 bed_angle（随 A）→ 解析 cam_open（仅 levercap）/ screw_turn（仅 thumbscrew）/ knob_height·tote_height（仅含相应 grip）→ 采 independent 机身 scale → 派生 iron_width（随 body_width·scale + inset）→ 投影四条 inequality（iron 不超 frog、actuator 落刀叠、bar 跨距随窄体、矮体配高 tote 比例）。
- KnobGeometry 注记（capnut_post）：cap_nut 用 `KnobGeometry(0.022, 0.010, body_style="cylindrical", grip=KnobGrip(style="knurled", count=24, depth=0.001), bore=KnobBore(style="round", diameter=0.007), center=False)`（screwcap L519-528）；visual origin rpy pitch +45° 对齐 BED_NORMAL；MEMORY 注记 KnobGeometry 有 axisymmetric AABB-spin 与 BoltPattern 的 API 坑，本类 cap_nut 是轴对称旋转件、用 CONTINUOUS 且 run_tests 只断言"旋后 center 不动"（screwcap L771-780），不依赖 spin AABB 变化，规避了那类坑。
- 参考模板：选运动拓扑相近的——root chassis + parallel children + 互斥主机构 slot + 共享活动 spine（clamp 的 frame→screw PRISMATIC + 可选 REVOLUTE child / cushion 的 base + 互斥 lid_mechanism + interior）；hand_plane 的 plane_body→FIXED iron + 互斥 blade_clamp（REVOLUTE/REVOLUTE/CONTINUOUS）+ 共享 lateral/depth spine 与之同构。刨尺度小（body ~0.155-0.245m、iron ~0.09-0.12m），joint origin 须精确落真实硬件面（≤0.015m baseline），夹刃 actuator origin 用 `_bed_pt` 算到 spine 顶/压条顶/chipbreaker top。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| solid_block_45 + levercap_flipcam + knob_plus_Dtote | rec_build-...-hand_..._d722d7db | `_bench_plane_body` L115-183 / `_frog` L186-200 / `_cutting_iron` L230-260 / `_lever_cap` L263-292 + `_cam_lever` L295-318 + `lever_cap_cam` REVOLUTE parent=cap L548-571 / `_front_knob` L380-400 + `_rear_tote` L403-439 / `_lateral_lever`+`_depth_wheel` L321-377 / `lateral_adjust`+`depth_adjust` L573-610 / allow_overlap L719-770 | 45° bench 机身 + lever-cap 翻凸轮（两级挂载）+ knob+D-tote + 共享 lateral/depth spine + 床坐标 `_bed_pt` 范式 + captured/床定 allow_overlap 基线 |
| S2 | A | low_block_trough | rec_hand_plane_var_blocksole | `_block_plane_body` L119-183（sole+两 sidewall trough）/ `_frog` 20° L186-200 / BED_DEG=20 + CQ_BED/SQ_BED L58-61 / `_cutting_iron` blade_w=0.038 L235-263 / body 矮断言 L623-634 | 短矮 20° 低角块刨机身（mesh+床角维度，含 20° 床坐标重算范式）|
| S3 | A | narrow_open_cheek | rec_hand_plane_var_rabbet | `_rabbet_plane_body` L105-183（−Y 全高 cheek + +Y 3mm lip + open_cut）/ 全宽 `_cutting_iron` blade_w=BODY_WIDTH−0.002 L224-249 / body 窄+iron 全宽断言 L596-619 | 窄裁口/肩刨机身 + iron 跑满全宽（窄体维度）|
| S4 | B | crossbar_thumbscrew | rec_hand_plane_var_clampbar | `_clamp_bar` L279-322 + `body_to_clamp_bar` FIXED L586-599 / `_clamp_boss` L220-243 + `for i in range(2)` `clamp_boss_{i}` L531-537 / `_thumbscrew_stud` L206-217 / `_thumbscrew` L325-363 + `thumbscrew` REVOLUTE axis=BED_NORMAL parent=body L601-622 / allow_overlap L781-812 | 横压条 + 滚花拇指螺钉（REVOLUTE spin@body，+2 part，clamp_boss `for i in range(2)` copy-loop）|
| S5 | B | capnut_post | rec_hand_plane_var_screwcap | `_cap_post` L222-239（body visual）/ `cap_nut` KnobGeometry/KnobGrip/KnobBore L516-533 + `cap_nut_spin` CONTINUOUS axis=BED_NORMAL parent=body L534-544 / iron `post_hole` L268-273 / 旋后 center 不动断言 L771-780 / allow_overlap L699-714 | 螺纹柱 + 滚花黄铜帽螺母（CONTINUOUS spin@body，+1 part，KnobGeometry nut + iron post_hole）|
| S6 | C | horn_plus_ringtote | rec_hand_plane_var_closedtote | `_front_horn_geom` L384-423（section_loft/SectionLoftSpec/LoftSection）+ `front_horn`(mesh_from_geometry) + `body_to_front_horn` FIXED L514-529 / `_rear_tote` 闭环 L426-468 + `body_to_rear_tote` FIXED L531-545 / horn 前冲+tote 闭环断言 L699-725 | 前冲 lofted horn + 闭环 ring tote（2 part，section_loft 前 horn）|
| S7 | C | single_palm_hump | rec_hand_plane_var_palmgrip | `_palm_rest` L373-419（revolve dome ∩ box + 指槽 cut）+ `palm_rest` + `body_to_palm_rest` FIXED L465-481 / body heel_boss 加宽、无 toe_boss L153-158 / rest 在机尾+低 profile 断言 L632-648 / allow_overlap L721-728 | 单只低 palm-hump 后掌托（1 part，删前 knob，heel boss 加宽）|
