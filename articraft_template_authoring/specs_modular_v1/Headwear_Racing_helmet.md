# Modular Spec — racing_helmet

## 元信息
| 项 | 值 |
|---|---|
| slug | `racing_helmet` |
| 大类 / 小类 | `Headwear/Racing helmet` |
| source map | `articraft_data/picture_expansion/template_source_maps/Headwear__Racing_helmet.md` |
| parent record_id | `rec_build-a-realistic-articulated-3d-model-of-a-raci_20260609_215058_284953_f750bd51` |
| parent picture | `picture/Headwear/Racing helmet/001.png` |
| template path | `agent/templates/Headwear_Racing_helmet.py` |
| test path (optional) | `tests/agent/test_racing_helmet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern` 说明：核心 root 是头盔 shell（ellipsoid 壳体）。视镜/下巴杆（Slot B）以 revolute 挂在 shell 的 temple/jaw pivot 上；进气/气动层（Slot C）以 shell-inline visual（或 loop 复制的 visual）挂回同一 root。两个功能层都是 shell 的并行 child，不构成串链，故 `parallel_children`。

---

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (1 parent + 6 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

**共享骨架（所有 7 个样本一致）**：

- 坐标系：head-centered，`+X` 前（脸），`+Z` 上。`HEAD_CZ = -NECK_Z` 把整个头盔抬起，使颈圈落在地面 `z≈0`。
- shell：`_full_ellipsoid(HEAD_RX=0.125, HEAD_RY=0.100, HEAD_RZ=0.110)` 外壳减去 `SHELL_WALL=0.012` 内壳得到薄壁，`NECK_Z=-0.085` 平面切掉颈口；前壁开 eye-port 窗。
- visor 主机构（核心身份）：`visor` part 是 REVOLUTE，轴 `(0,-1,0)`（左右 Y），origin `(PIVOT_X=0.055, 0, PIVOT_Z=0.055 + HEAD_CZ)`，行程 `0..radians(95)`，正 q 把视镜往上翻、卷到头顶后方。visual origin `(-PIVOT_X, 0, -PIVOT_Z)` 抵消 pivot 偏移使 q=0 落在闭合姿态。
- side pivot studs：恒为 2 个（left/right），FIXED 关节，inner end 嵌进 shell 壁作 hinge boss（`STUD_Y_CENTER=0.0775`）。视镜侧臂 `_build_visor_arm` 骑在 stud 上做 hinge capture（element-scoped `allow_overlap`）。

**逐样本差异（真正的拓扑变化轴）**：

1. **parent** `f750bd51`：full-face shell（eye-port 窗 + 黑色 chin_trim 带），单 outer visor，无额外气动件。
2. **half_open_face**：shell 去掉 chin bar，front 开大口（brow 线以下整块挖空 `FACE_CUT_*`），`chin_trim` 换成 `face_rim` padding 框；visor 更高（覆盖大开口）。→ Slot A 的第二候选。
3. **dual_sun_visor**：在 parent shell 上**多加一个 part `sun_visor`**（内层熏黑遮阳镜），REVOLUTE 轴 `(0,1,0)`，origin 在外 visor pivot 上方偏后 `(SUN_PIVOT_X=0.042, 0, SUN_PIVOT_Z=0.062)`，行程 `0..0.85`，从壳内收起位下放遮上半 eye-port。→ Slot B 增加一条独立 revolute 关节链。
4. **modular_chin_bar**：shell 多挖 chin 开口；**多加一个 part `chin_bar`**（黑色下巴护罩），REVOLUTE 轴 `(0,1,0)`，origin 在 jaw 位 `(CHIN_PIVOT_X=0.045, 0, CHIN_PIVOT_Z=-0.040)`，行程 `0..radians(65)`，向下翻开露出下脸；外加 2 个 chin pivot studs（FIXED）。视镜机构同 parent。→ Slot B 的第三候选（独立第二 revolute）。
5. **peak_visor（rear_detail_mesh）**：在 parent shell 上加**纯 shell visual**——`rear_occipital_panel`（暗色后脑嵌板）+ `rear_vent_slit_{i}`（loop ×6 横向气槽）+ `rear_chevron_ridge_{i}`（×2 镜像斜脊）。无新关节。→ Slot C 候选。
6. **aero_rear_spoiler**：在 parent shell 上加单个 `rear_spoiler` shell visual（后上方锥形尾翼鳍）。无新关节。→ Slot C 候选。
7. **top_air_vents**：在 parent shell 上加 `top_vent_{i}`（loop ×3 顶部进气勺）+ `rear_exhaust_{i}`（×2 后排气勺）shell visual。无新关节。→ Slot C 候选（含 multiplicity 轴）。

结论：3 个结构轴 = (A) shell/face opening 形态、(B) visor/chin 关节配置、(C) 气动/通风 visual 层。

---

## 核心身份
赛车/卡丁头盔（racing helmet）：一个**薄壁 ellipsoid 头盔壳体**，前壁开 eye-port，颈口开放、平颈圈落地；核心可动机构是一块**绕左右(Y)轴翻起的护目镜（visor）**，通过两侧 temple pivot studs 铰接、翻起时卷到头顶后方。下巴杆（chin bar）或内层遮阳镜（sun visor）是同族的第二级 revolute 机构。默认成熟域：full-face 或 open-face 单壳、≥1 个真实 revolute（视镜或下巴杆）、左右各 1 个 pivot（共 2）。

**不该混入**：自行车/滑雪等无 visor 翻镜机构的软帽或开放头盔（无核心 revolute）；摩托整体式头盔若把 visor 退化成固定挡片（失去核心关节）；面具/护目镜单品（无完整壳体）。

---

## 槽位 + 候选模块表

### Slot A：shell / face opening（头盔壳体 + 面部开口形态，root）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| full_face_shell | parent `rec_build-a-realistic-articulated-3d-model-of-a-raci_20260609_215058_284953_f750bd51` | shell L120-L153；chin_trim L156-L178 | eligible if compatible | 薄壁 ellipsoid，前壁仅开有界 eye-port 窗（`PORT_*`），下前方保留 chin bar + 黑色 `chin_trim` 带；颈口下切。emits root part `shell`。 |
| half_open_face | `rec_racing_helmet_var_half_open_face` | shell L94-L126；face_rim L129-L176 | eligible if compatible | 同壳体但 brow 线以下整块前壁挖空（`FACE_CUT_*`，无 chin bar），侧壁/后壁保留；`chin_trim` 换成沿开口边的 `face_rim` 软垫框。emits root part `shell`（更大开口）。 |

> Slot A 仅 2 候选：5★ 池里只有 full-face 与 open-face 两种壳体拓扑，已覆盖真实赛车头盔的两大壳型，达到 §4「样本不足可降到 2」的硬约束下限并说明理由（无第三种结构性壳型样本，不发明）。

### Slot B：visor / chin articulation（核心翻镜/下巴关节配置）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| outer_clear_visor | parent `rec_build-a-realistic-articulated-3d-model-of-a-raci_20260609_215058_284953_f750bd51` | visor L181-L215；trim L269-L287；arms L230-L266；2×pivot studs L318-L343；hinge L383-L393 | eligible if compatible | 基线：单块外层透明 visor，1 条 REVOLUTE（轴 -Y）+ 2 个 temple pivot studs（FIXED）。这是核心身份关节，所有组合都含。 |
| dual_sun_visor | `rec_racing_helmet_var_dual_sun_visor` | sun_visor L304-L334；sun part+hinge L443-L478 | eligible if compatible | 在 outer_clear_visor 之上**再加一个 part `sun_visor`**（内层熏黑遮阳镜）+ 第二条 REVOLUTE（轴 +Y，origin 在外 visor pivot 上方偏后，行程 0..0.85，壳内下放）。两条独立 revolute。 |
| modular_chin_bar | `rec_racing_helmet_var_modular_chin_bar` | shell w/ chin cut L122-L167；chin_bar body L261-L287；arm L290-L315；assemble L322-L329；2×chin studs L376-L395；chin hinge L456-L466 | eligible if compatible | 保留 outer visor 关节，**再加一个 part `chin_bar`**（黑色下巴护罩）+ 第二条 REVOLUTE（轴 +Y，jaw origin，行程 0..radians(65)，向下翻）+ 2 个 chin pivot studs（FIXED）。shell 需 chin 开口。 |

> Slot B 三候选都保留核心 outer_clear_visor revolute（保证 ≥1 真实关节）；`dual_sun_visor` 与 `modular_chin_bar` 各自再叠一条独立 revolute（不同轴/origin/行程），是真正的关节拓扑差异，非装饰。

### Slot C：aero / ventilation layer（气动/通风附件层，shell-inline visual）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| parent_venting | parent `rec_build-a-realistic-articulated-3d-model-of-a-raci_20260609_215058_284953_f750bd51` | （无独立气动 visual；shell L120-L153 即继承层） | eligible if compatible | 退化档：仅继承壳体本身的 trim/窗，不加额外气动 visual。作为 Slot C 的「空」基线，保证 Slot C 与其他三档形成对比。 |
| rear_detail_mesh | `rec_racing_helmet_var_peak_visor`（slug 为 legacy） | rear_occipital_panel L321-L347；vent_slit L350-L357（loop emit L420-L431）；chevron_ridge L360-L385（emit L432-L439） | eligible if compatible | 后脑细节网格：暗色嵌板 `rear_occipital_panel` + loop ×6 `rear_vent_slit_{i}`（竖排横气槽）+ ×2 镜像 `rear_chevron_ridge_{i}`。全部为 shell-inline visual，无新关节。 |
| aero_rear_spoiler | `rec_racing_helmet_var_aero_rear_spoiler` | rear_spoiler L290-L341（emit L367-L372） | eligible if compatible | 单块 `rear_spoiler`：后上方锥形尾翼鳍，前缘嵌进壳壁、向后突出。shell-inline visual，无新关节。 |
| top_air_vents | `rec_racing_helmet_var_top_air_vents` | top_vent L269-L311（loop emit L398-L404）；rear_exhaust L314-L347（emit L407-L413） | eligible if compatible | 顶部进气勺 `top_vent_{i}`（loop ×N，本小类样本 N=3，center/left/right）+ ×2 `rear_exhaust_{i}` 后排气勺。shell-inline visual，含 multiplicity 轴 `vent_count`。 |

> Slot C 四候选都是 shell-inline 装饰/气动 visual（不改 visor/chin 机构）。`parent_venting` 是显式空档（degrade），其余三档结构不同（后脑网格 / 尾翼鳍 / 顶部勺+排气）。

---

## 槽位图（slot graph）

pattern: `parallel_children`

```
                    shell (root, Slot A: full_face_shell | half_open_face)
                   /        |                                  \
   [Slot C visuals]   [Slot B core]                      [Slot B optional 2nd]
   shell-inline       outer_clear_visor                  dual_sun_visor  XOR  modular_chin_bar
   (parent_venting/   = REVOLUTE axis -Y                 = REVOLUTE axis +Y  | = REVOLUTE axis +Y
    rear_detail_mesh/   @ temple pivot (PIVOT_X,PIVOT_Z)   @ inner-upper       @ jaw
    aero_rear_spoiler/  + 2× temple studs (FIXED)          (SUN_PIVOT_*)       (CHIN_PIVOT_*)
    top_air_vents)                                         壳内遮阳            + 2× chin studs (FIXED)
```

接口点位说明：

- **Slot A → Slot B（core visor）**：interface = temple pivot 点 `(PIVOT_X=0.055, ±STUD_Y_CENTER=0.0775, PIVOT_Z=0.055)+HEAD_CZ`。2 个 FIXED pivot studs 把 hinge 线钉在 shell 壁上；visor 经 REVOLUTE（轴 -Y）挂上去；visor 侧臂 `_build_visor_arm` 骑在 stud 上构成 captured-pin（element-scoped allow_overlap）。core visor 在所有组合恒存在。
- **Slot A → Slot B（dual_sun_visor 第二关节）**：interface = inner-upper pivot `(SUN_PIVOT_X=0.042, 0, SUN_PIVOT_Z=0.062)+HEAD_CZ`，在壳腔内、外 visor pivot 上方偏后。REVOLUTE 轴 +Y，sun_visor 直接挂 shell（与 core visor 并列，不串接）。
- **Slot A → Slot B（modular_chin_bar 第二关节）**：interface = jaw pivot `(CHIN_PIVOT_X=0.045, ±CHIN_STUD_Y_CENTER=0.080, CHIN_PIVOT_Z=-0.040)+HEAD_CZ`，低于 visor pivot。2 个 FIXED chin studs + chin_bar REVOLUTE 轴 +Y（向下翻）。要求 shell 含 chin 开口（见兼容矩阵）。
- **Slot A → Slot C**：interface = shell 外表面（贴 ellipsoid 曲面）。Slot C 的 visual 直接以 `mesh_from_cadquery(...)` 加进 root `shell` part（`origin=(0,0,HEAD_CZ)`），前缘嵌入壳壁求连通，**不引入新 part / 新 joint**。

跨 slot joint / 互斥 / 派生：

- 跨 slot joint type：core visor 与 sun/chin 均为 REVOLUTE；Slot C 全为 FIXED-into-shell visual（无 joint）。
- 互斥：`dual_sun_visor` 与 `modular_chin_bar` 各自占用「第二 revolute」语义层，但锚点不同（壳内 vs jaw），可独立存在但**不同时取**（Slot B 单选 enum）。
- 派生：`modular_chin_bar` 要求 Slot A 提供 chin 开口；当 Slot A=`half_open_face`（已大开口、无 chin bar）时 chin_bar 的护罩语义无意义且与开口冲突 → 见兼容矩阵 gating。

---

## 每槽位 Module Emits / Interfaces

### Slot A / module full_face_shell
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `shell`（visual `shell_dome` + `chin_trim`） | parent / model.py:L298-L311 |
| internal joints | 无（root 不动） | — |
| upstream interface | root；`HEAD_CZ` 抬升使颈圈落地 | parent / model.py:L52-L53 |
| downstream interface | 提供 eye-port 窗（`PORT_*`）+ temple pivot 锚点供 Slot B；外曲面供 Slot C | parent / model.py:L57-L70 |

### Slot A / module half_open_face
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `shell`（visual `shell_dome` + `face_rim`） | half_open_face / model.py:L278-L290 |
| internal joints | 无 | — |
| upstream interface | root；`HEAD_CZ` 抬升 | half_open_face / model.py:L47-L48 |
| downstream interface | 提供大 face 开口（`FACE_CUT_*`）+ temple pivot 锚点；与 chin bar 互斥 | half_open_face / model.py:L60-L63 |

### Slot B / module outer_clear_visor（core，恒存在）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `visor`（visual `visor_panel`+`visor_trim`+`visor_pivot_arms`）；`pivot_stud_left`/`pivot_stud_right` | parent / model.py:L345-L373, L318-L343 |
| internal joints | `shell_to_visor` REVOLUTE 轴 (0,-1,0) origin (PIVOT_X,0,PIVOT_Z+HEAD_CZ) 行程 0..rad(95)；`shell_to_pivot_{l,r}` FIXED | parent / model.py:L383-L393, L337-L343 |
| upstream interface | 经 2 个 temple pivot studs 钉在 shell 壁（hinge boss，allow_overlap stud↔shell） | parent / model.py:L409-L418 |
| downstream interface | visor 侧臂 captured 在 studs 上（allow_overlap stud↔visor），闭合覆盖 eye-port | parent / model.py:L421-L430 |

### Slot B / module dual_sun_visor（= core + 内遮阳）
| emits | 描述 | 来源 |
|---|---|---|
| parts | core visor 全部 + `sun_visor`（visual `sun_visor_panel`） | dual_sun_visor / model.py:L447-L461 |
| internal joints | core `shell_to_visor` + `shell_to_sun_visor` REVOLUTE 轴 (0,1,0) origin (SUN_PIVOT_X,0,SUN_PIVOT_Z+HEAD_CZ) 行程 0..0.85 | dual_sun_visor / model.py:L468-L478 |
| upstream interface | sun_visor 直挂 shell（壳内层）；retracted 时在外 visor crown 线之上 | dual_sun_visor / model.py:L304-L334 |
| downstream interface | deployed 时下放覆盖上半 eye-port；与 studs 允许内壳重叠（allow_overlap sun↔stud） | dual_sun_visor / model.py:L521-L530 |

### Slot B / module modular_chin_bar（= core + 下巴杆）
| emits | 描述 | 来源 |
|---|---|---|
| parts | core visor 全部 + `chin_bar`（visual `chin_bar_shell`）；`chin_pivot_left`/`chin_pivot_right` | modular_chin_bar / model.py:L438-L451, L376-L395 |
| internal joints | core `shell_to_visor` + `shell_to_chin_bar` REVOLUTE 轴 (0,1,0) origin (CHIN_PIVOT_X,0,CHIN_PIVOT_Z+HEAD_CZ) 行程 0..rad(65)；2×`shell_to_chin_pivot` FIXED | modular_chin_bar / model.py:L456-L466, L387-L395 |
| upstream interface | 2 个 jaw chin studs 钉在 shell 壁；chin_bar 臂 captured 在 studs（allow_overlap） | modular_chin_bar / model.py:L504-L516 |
| downstream interface | 闭合覆盖下脸开口；下翻露出下脸；chin 臂穿壳到外置 stud（allow_overlap chin_bar↔shell） | modular_chin_bar / model.py:L519-L523 |

### Slot C / module parent_venting（degrade 空档）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无额外 visual（仅继承 shell 本体 trim/窗） | parent / model.py:L298-L311 |
| internal joints | 无 | — |
| interface | 不向 shell 添加任何气动 visual | — |

### Slot C / module rear_detail_mesh
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell visual：`rear_occipital_panel` + `rear_vent_slit_{i}`(×6 loop) + `rear_chevron_ridge_{i}`(×2 镜像) | rear_detail_mesh / model.py:L414-L439 |
| internal joints | 无（shell-inline visual） | — |
| interface | 贴后脑(-X)曲面，slit 经 `_rear_surface_x` 座在壳面外侧 | rear_detail_mesh / model.py:L310-L318 |

### Slot C / module aero_rear_spoiler
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell visual：`rear_spoiler`（后上方锥形鳍） | aero_rear_spoiler / model.py:L367-L372 |
| internal joints | 无 | — |
| interface | 前缘 blend 进壳壁(-X 后上方)，向后突出 prot 0.020→0.008 | aero_rear_spoiler / model.py:L290-L341 |

### Slot C / module top_air_vents
| emits | 描述 | 来源 |
|---|---|---|
| parts | shell visual：`top_vent_{i}`(×N loop) + `rear_exhaust_{i}`(×2) | top_air_vents / model.py:L398-L413 |
| internal joints | 无 | — |
| interface | 顶部 proud ellipsoid 勺嵌入壳壁求连通；rear_exhaust 后上方 | top_air_vents / model.py:L269-L311, L314-L347 |

---

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `shell_module` (Slot A) | enum | `full_face_shell` / `half_open_face` | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `visor_module` (Slot B) | enum | `outer_clear_visor` / `dual_sun_visor` / `modular_chin_bar` | — | choice | sampler 选择；受 Slot A gating（见兼容矩阵） | Slot B 表 |
| `aero_module` (Slot C) | enum | `parent_venting` / `rear_detail_mesh` / `aero_rear_spoiler` / `top_air_vents` | — | choice | sampler 选择 | Slot C 表 |
| `palette_style` | enum | 见下「palette_style 候选」≥4 colorway | — | choice | 按 seed 加权采样，决定 shell/trim/visor/stud/accent 材质 | 跨样本材质 |
| `vent_count` (Slot C, top_air_vents 时) | int | `[2, 5]`（本小类样本=3） | 3 | conditional | 仅 `aero_module=top_air_vents` 有效；加权采样小 N 偏多；`vent_{i}` loop 横向均匀分布 | top_air_vents / L398-L404 |
| `head_rz_scale` | float | `[0.92, 1.08]` | 1.0 | independent | 仅缩 `HEAD_RZ`(crown 高)，clamp；不动 pivot 语义 | parent / L47 |
| `visor_open_angle` | float | `radians([88, 100])` | `radians(95)` | independent | core visor 行程上限，clamp ≥ rad(80) 保证翻起测试过 | parent / L390-L392 |
| `chin_open_angle` | float | `radians([55, 70])` | `radians(65)` | conditional | 仅 `modular_chin_bar`；下翻行程 | modular_chin_bar / L463-L465 |
| `sun_deploy_angle` | float | `[0.75, 0.95]` | 0.85 | conditional | 仅 `dual_sun_visor`；遮阳下放行程 | dual_sun_visor / L475-L477 |
| `spoiler_prot_scale` | float | `[0.85, 1.15]` | 1.0 | conditional | 仅 `aero_rear_spoiler`；尾翼突出量，clamp 防穿地/过长 | aero_rear_spoiler / L311-L313 |
| (—) | constraint | — | — | inequality | `pivot_z*+HEAD_CZ` 与 `head_rz_scale·HEAD_RZ` 联立：pivot 必须落在缩放后壳面内（违反则回缩 head_rz_scale） | 接口 / clearance |
| (—) | constraint | — | — | conditional | `visor_module=modular_chin_bar` ⟹ `shell_module=full_face_shell`（chin bar 需 chin 开口；open-face 已无下巴区） | 兼容矩阵 |

**palette_style 候选（≥4 colorway，全部取自 5★ 样本观察到的材质，逐 seed 采样）**：

| colorway | shell | trim/chin/face_rim | visor | stud/accent | 来源 |
|---|---|---|---|---|---|
| `ferrari_red`（标称基线） | red_gloss `(0.78,0.05,0.06,1)` | trim_black `(0.06,0.06,0.07,1)` | visor_clear `(0.12,0.13,0.16,0.45)` | stud_black `(0.10,0.10,0.11,1)` | parent / L293-L296 |
| `carbon_black` | shell→trim_black 系深色 `(0.06,0.06,0.07,1)` | gunmetal `(0.18,0.18,0.20,1)` | sun_smoke `(0.04,0.04,0.06,0.72)` | hinge_gunmetal `(0.18,0.18,0.20,1)` | modular_chin_bar / L339；dual_sun_visor / L344 |
| `arctic_white` | white `(0.92,0.92,0.94,1)`（由 red_gloss 改色） | trim_black | visor_clear | stud_black | 由样本材质族改色（保形不改拓扑） |
| `livery_blue` | racing blue `(0.10,0.22,0.62,1)` | trim_black | visor_clear（轻熏） | rear_gunmetal `(0.08,0.085,0.095,1)` accent | rear_detail_mesh / L395 accent；蓝为常见赛车 livery |
| `gunmetal_gray` | spoiler_dark/vent_gray 系 `(0.18,0.18,0.20,1)` | trim_black | sun_smoke 深熏 | stud_black | aero_rear_spoiler / L351；top_air_vents / L395 |

> 注：`arctic_white` 与 `livery_blue` 的主壳色是对 5★ 材质族（同一 rgba 槽位语义：glossy shell / black trim / tinted visor / dark accent）做保形改色，不改任何几何或拓扑，仅满足「输出颜色多样」要求；其余三档主壳色直接来自样本实测 rgba。

---

## Multiplicity / Copy Logic

本模板有 **2 类固定复制 + 1 根可变 multiplicity 轴**：

**固定复制（非 multiplicity 轴，恒 2，不暴露 count）**：

- **side pivot studs**：core visor 恒 2 个（left/right），命名 `pivot_stud_left`/`pivot_stud_right`，FIXED，镜像 `±STUD_Y_CENTER`。source: parent L318-L343。**side pivot count 固定 2**（源 map 明确要求），不暴露 `*_count`。
- **chin pivot studs**（仅 `modular_chin_bar`）：恒 2，`chin_pivot_left`/`chin_pivot_right`，FIXED，镜像 `±CHIN_STUD_Y_CENTER`。source: modular_chin_bar L376-L395。
- **rear_exhaust**（仅 `top_air_vents`）/ **rear_chevron_ridge**（仅 `rear_detail_mesh`）：恒 2，镜像左右，不暴露 count。

**可变 multiplicity 轴 — `vent_count`（顶部进气勺，slot-local）**：

- `count_param`：`vent_count`（仅当 `aero_module=top_air_vents` 生效，slot-local）
- `N_range`：产品域 `[2, 5]`；测试偏小（sweep 取 2-3）；本小类样本实测 N=3（center+left+right）。
- sampling domain：加权——N=3 最高频（样本档），N=2 次之，N=4/5 稀有尾部。
- copied object：`top_vent_{i}` 进气勺 shell visual（`_build_top_vent`，源用 index→y_offset 表，模板改为按 N 均匀分布的 `vent_{i}` loop）。
- naming：`vent_{i}`（i=0..N-1），中心对称分布。
- placement：crown 上沿 Y 轴均匀间隔（`y_offset` 由 N 对称生成），cx=0.01、cz=HEAD_RZ-0.010。
- joint policy：无 joint（shell-inline visual），FIXED-into-shell（嵌壳求连通）。
- source/gating：top_air_vents / L269-L311, L398-L404；仅 Slot C=top_air_vents 时存在，其余 aero_module 不进入该轴。

> `rear_vent_slit_{i}`（rear_detail_mesh 内 ×6）是该 candidate 的固定细节密度，**不**升为模板级 multiplicity 轴（源里是定值 6，无多 N 样本），保持 candidate-local 固定循环。

---

## 拓扑多样性审计

总组合数：Slot A(2) × Slot B(3) × Slot C(4) = **24**（未计 `vent_count` 采样）。
计入兼容性 gating：`modular_chin_bar` 仅与 `full_face_shell` 合法 → 去掉 (half_open_face × modular_chin_bar × 4) = 4 个非法组合 → **合法组合 20**。
计入 `vent_count`（top_air_vents 时 N∈{2,3,4,5}）：拓扑 distinct 进一步上升（每个含 top_air_vents 的合法组合 × 4 个 N 档，但 N 仅改复制数不改 slot 等价类，按拓扑等价类仍以 20 计为下限，含 N 则远超）。

理由：合法组合 20 ≥ 10，且每个组合的 part-tree / joint 集合都不同（Slot B 三档分别给 1 / 2 / 2 条 revolute 且第二关节 part 不同；Slot C 四档分别给 0 / 8(panel+6slit+2chevron) / 1 / (N+2) 个 shell visual；Slot A 两档 root 形态不同）。即使忽略连续 scale 与 vent_count，slot/module 选择本身已产生 ≥20 个不同拓扑等价类。

seed_domain_policy：`procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic procedural sampling：先抽 Slot A（full_face 偏多），再抽 Slot B（outer_clear_visor 偏多、dual_sun_visor / modular_chin_bar 次之），再抽 Slot C（四档近均，parent_venting 稍高作基线）；Slot B 抽到 `modular_chin_bar` 时若 Slot A=half_open_face 则按兼容矩阵回退 Slot A→full_face_shell（或重抽 Slot B）。`vent_count` 仅在 Slot C=top_air_vents 时加权抽 [2,5]。随后抽 `palette_style`（ferrari_red 偏多）与少量连续 scale（head_rz_scale / visor_open_angle / 条件 scale），在 `resolve_config` clamp/派生。viewer 目检 seeds 0-19。
Topology target：1000-seed slot choice tuple distinct 目标 ≥ 20（受类别约束：slot/module 组合上限 20，已说明原因——5★ 池仅支撑 2×3×4 结构轴，非 ≥300 富类别观察模板）。低于 300 的原因即此：racing helmet 是中等结构多样度类别，主多样性来自 3 个有限离散轴 + vent_count + palette。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
若使用 regression overrides：none（首版不需要；如后续某组合 sweep 失败再按 seed 记录）。
Controlled local parameterization：初版应含 `head_rz_scale [0.92,1.08]`（independent，clamp，且与 pivot 落点 inequality 联立回缩）、`visor_open_angle`（independent，clamp ≥ rad(80) 保翻起测试）、`chin_open_angle`/`sun_deploy_angle`/`spoiler_prot_scale`（conditional，按所选 module 解析范围）。全部在 `resolve_config` 求解，遵循「先 independent → 派生 equation → 投影/回缩 inequality → 解析 conditional」契约；pivot 锚点依赖 head_rz_scale 的跨部件关系已显式落 inequality，不当独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | Slot A→B→C 加权选择；Slot B 抽 chin_bar 触发 Slot A gating 回退；vent_count 仅 top_air_vents 时抽 | `slot_choices_for_seed` 与 build 选择一致 |
| compatibility matrix | `modular_chin_bar` 仅合 `full_face_shell`；Slot B 单选（sun vs chin 互斥）；Slot C 任意 module 与任意 A/B 合法 | no floating, no shell-penetration of accents, chin/visor axis & range, closed-pose coverage |
| controlled local variation | head_rz_scale / *_angle / spoiler_prot_scale，全 clamp/conditional | 比例变化不破 pivot origin / 接口 / clearance / 翻镜测试 |
| regression overrides | none | — |
| random sweep | seeds 0-49 初版，0-999 成熟度审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A | 2 | yes | no | 5★ 池仅 2 种壳型拓扑，已说明降级理由 |
| B | 3 | yes | yes | 三档关节配置（1/2/2 revolute） |
| C | 4 | yes | yes | 含 1 个 degrade 空档 parent_venting + 3 个结构档 |

---

## Validator

- slot_choices_for_seed returns implemented module names（shell_module / visor_module / aero_module，含 vent_count 当 top_air_vents）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（modular_chin_bar × half_open_face 被 gate）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped（head_rz_scale / *_angle / spoiler_prot_scale）且不破接口/clearance/joint origin/category multiplicity（side pivot 恒 2）
- cross-part scale dependencies 在 `resolve_config` 求解（pivot 落点 ↔ head_rz_scale inequality；chin/sun/spoiler 的 conditional 范围）
- critical InterfaceSpec / MatingContract points exist：temple pivot（2 studs captured visor 臂）、jaw pivot（chin）、inner-upper pivot（sun）、shell 外曲面（aero visual 嵌壳连通）
- key joints have expected type / axis / range：`shell_to_visor` REVOLUTE 轴 Y 行程 0..~rad(95)；`shell_to_chin_bar` REVOLUTE 轴 +Y 行程 0..rad(65)；`shell_to_sun_visor` REVOLUTE 轴 +Y 行程 0..0.85；pivot studs FIXED
- copied objects follow naming and placement policy：`pivot_stud_{left,right}` / `chin_pivot_{left,right}` / `vent_{i}` / `rear_exhaust_{i}` / `rear_chevron_ridge_{i}`

## Reject cases

- core visor 不是 REVOLUTE 或轴不在 Y（失去核心身份关节）。
- side pivot studs 数量 ≠ 2，或 left/right 不镜像、不贴 shell（hinge boss 悬空）。
- `modular_chin_bar` 与 `half_open_face` 同出（下巴区已开口，护罩语义冲突 / 穿模）。
- Slot C 气动 visual 不嵌壳、形成漂浮 island（top_vent/spoiler/rear panel 与 shell 不连通）。
- 闭合 visor 不覆盖 eye-port，或翻起后不上移/不回卷过头顶（翻镜运动语义错）。
- chin_bar 翻开时上扫穿过头盔壳（应向下翻）。
- sun_visor deployed 不下放、或 retracted 不在外 visor crown 线之上（内层语义错）。
- vent_count 超出 [2,5]，或 `vent_{i}` 不对称分布。
- palette_style 把 visor 做成不透明（失去护目镜透明语义）。

---

## 与相邻类别的边界

- 不该混入：**Bicycle/Ski helmet（无翻镜机构的开放头盔）**——缺核心 visor revolute，本类身份是绕 Y 翻起的护目镜。
- 不该混入：**Goggles / Face shield（单品护目镜）**——无完整 ellipsoid 壳体与颈口，仅是 Slot B 的一部分。
- 不该混入：**Motorcycle full-face（visor 退化为固定挡片）**——若 visor 不可动则失去核心关节，降为静态摆件。
- 不该混入：**Welding / industrial helmet（翻面罩绕水平前后轴或整面上翻）**——关节轴/语义与赛车 visor 的左右 Y 翻镜不同。

---

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot A 仅 2 候选（5★ 池只有 full-face/open-face 两种壳型拓扑，已记降级理由，不发明第三种）。Slot C 含 1 个 degrade 空档 parent_venting（与其余三结构档对比）。side pivot 恒 2、vent_count 为唯一可变 multiplicity 轴 [2,5]。core visor revolute 在所有组合恒存在以保 ≥1 真实关节。modular_chin_bar × half_open_face 经兼容矩阵 gate。 |

## 模板实现备注（可选）

- 共享 helper：`_full_ellipsoid` / `_cut_visor_side_relief` / `_build_visor_arm` 在全部样本一致，可直接抽为模板级共享。
- captured-pin overlap 需 element-scoped allow_overlap：stud↔shell、stud↔visor 臂（core）；chin stud↔shell、chin stud↔chin_bar、chin_bar↔shell（modular_chin_bar）；sun↔stud（dual_sun_visor）。每个组合各自声明。
- Slot C 的所有气动 visual 必须嵌壳（proud ellipsoid ∩ footprint，inner_cut 进壳壁）以保证与 shell_dome 连通、不成漂浮 island。
- `modular_chin_bar` 需 Slot A shell 额外挖 chin 开口（`CHIN_CUT_*`）——gating 保证仅 full_face_shell 走此分支。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A | full_face_shell | parent f750bd51 | shell L120-L153；chin_trim L156-L178 | root shell + eye-port + chin bar |
| S2 | Slot A | half_open_face | rec_racing_helmet_var_half_open_face | shell L94-L126；face_rim L129-L176 | 大开口壳 + face_rim |
| S3 | Slot B | outer_clear_visor | parent f750bd51 | visor L181-L215；arms L230-L266；studs L318-L343；hinge L383-L393 | core 翻镜 revolute + 2 studs |
| S4 | Slot B | dual_sun_visor | rec_racing_helmet_var_dual_sun_visor | sun_visor L304-L334；part+hinge L443-L478 | 第二 revolute（内遮阳） |
| S5 | Slot B | modular_chin_bar | rec_racing_helmet_var_modular_chin_bar | chin_bar L261-L329；chin studs L376-L395；hinge L456-L466 | 第二 revolute（下巴杆）+ 2 chin studs |
| S6 | Slot C | rear_detail_mesh | rec_racing_helmet_var_peak_visor | panel L321-L347；slit L350-L357；chevron L360-L385；emit L414-L439 | 后脑网格 visual（含 ×6/×2 loop） |
| S7 | Slot C | aero_rear_spoiler | rec_racing_helmet_var_aero_rear_spoiler | spoiler L290-L341；emit L367-L372 | 尾翼鳍 visual |
| S8 | Slot C | top_air_vents | rec_racing_helmet_var_top_air_vents | top_vent L269-L311；rear_exhaust L314-L347；emit L398-L413 | 顶部进气勺(vent_count loop)+排气 |
</content>
</invoke>
