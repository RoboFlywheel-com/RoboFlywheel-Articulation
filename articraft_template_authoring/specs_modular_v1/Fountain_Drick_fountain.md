# drinking_fountain — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `drinking_fountain` |
| 大类 / 小类 (picture) | `Fountain` / `Drick fountain` |
| source map | `<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Fountain__Drick_fountain.md` |
| parent record_id | `rec_build-a-realistic-articulated-3d-model-of-a-dric_20260609_215049_780247_b6678542` |
| parent picture | `picture/Fountain/Drick fountain/001.png` |
| template path | `agent/templates/Fountain_Drick_fountain.py` |
| test path (optional) | `tests/agent/test_drinking_fountain_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（optional fountain-unit layout multiplicity + per-unit serial chain body→basin→outlet/actuator + per-unit push-button multiplicity）|

> 备注：slug 从图片小类名 “Drick fountain” 重命名为 `drinking_fountain`（更可读、ASCII-safe）。本头部用于把 `Fountain_Drick_fountain.md` 回溯到图片小类 `Fountain/Drick fountain` 与 5★ 源记录。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category（1 parent + 6 converged variants）|
| source_index_policy | only adopted module sources are indexed below |

**共享骨架（全部 7 个样本一致）**：所有样本共用同一套坐标约定（+Z 向上，使用者面向 +Y 前方），同一组 mesh helper（`_unit` / `_cross` / `_combine_mesh_geometries` / `_hollow_tube_mesh_from_path` / `_annular_cylinder_mesh`），同一组材质（teal-blue 漆钢 body、brushed stainless 盆、polished chrome 按钮）。共享的结构链是：**body（root）→ 顶部 catch basin（开口接水盘）+ gooseneck 出水嘴 → 前面板 faceplate（带刻字水瓶图标 + 按钮安装 boss）→ 侧面 valve_fitting + 下方悬挑 perforated bottle-rest grille shelf → 主动件 actuator（push button / foot pedal）**。核心运动恒为出水阀门主动件（push-button PRISMATIC 柱塞，或 foot-pedal REVOLUTE 踏板）。faceplate / fitting / grille 都是 FIXED 装饰/承载子件；basin/spout 也 FIXED 在 body 顶。

**逐样本差异（真正拓扑/接口变化轴）**：
- **parent（pedestal_body + parent_basin_spout + single_push_button）**：root 是高瘦弧形 teal 立柱 `pylon_body`（`_build_pylon` 用 loft 弧形 swoosh，底部 foot pad 落地 z≈0，PYLON_H≈1.02 m）。盆是矩形开口盘 `catch_basin`（`_build_basin` rect box），盆上短 gooseneck 饮水嘴 `_build_spout`。1 个 chrome 柱塞按钮 `push_button`，PRISMATIC 沿 -Y 内压。
- **wall_mounted_body**：root 改为薄壁 stainless `mounting_plate`（背面贴墙 y≈0，PLATE_Z_CENTER≈0.9 m，四角螺孔），紧凑 `body` 壳体 FIXED 在 plate 前（`plate_to_body`），其余 basin/faceplate/actuator 链挂到 `body` 而非 pylon。这改变 root part、root 坐标 spine、以及上游 mating face（墙面 vs 落地）。
- **round_basin**：盆改为圆碗 `_build_basin`（cylinder + 圆角底 + rim ring），盆 inertial 用 `Cylinder` 而非 `Box`；spout 后壁挂点用 `-BASIN_R` 而非 `-BASIN_Y/2`。AABB 测试改为“X/Y 近似相等（圆形）”。
- **bubbler_spout**：盆仍是矩形，但出水嘴 `_build_spout` 改为经典向上喷的 bubbler：用新增 helper `_hollow_variable_tube_mesh_from_path`（变半径管）做平滑收口的上喷 nozzle，apex 高于盆沿。这是 spout 模块内部几何 + 一个额外 helper 的变化。
- **bottle_filler**：盆 + 饮水短 spout 都保留，**额外**新增一个独立 part `bottle_filler_arch`（`_build_bottle_filler_arch` 高 gooseneck，FILLER_RISE≈0.26 m 远高于盆沿，带下垂 nozzle），FIXED 在 basin 上（`basin_to_filler`）。这是真正多一个 part + 一条 FIXED joint 的拓扑变化。
- **foot_pedal**：actuator 改为 chrome 踏板 `foot_pedal`（`_build_foot_pedal` 带 pivot barrel + 防滑筋），**REVOLUTE** 绕 X 轴铰接在 pylon 底前（`pylon_to_pedal`，PEDAL_PRESS≈0.30 rad）；pylon `_build_pylon` 额外长一个 pivot boss。改变 joint type（REVOLUTE vs PRISMATIC）、axis（X vs Y）、parent（pylon/base vs faceplate）。前面板上不再有 push_button part。
- **dual_push_buttons**：actuator 改为循环复制 `button_{i}`（`NUM_BUTTONS=2`，`BTN_SPACING≈0.044`），各自独立 PRISMATIC joint `faceplate_to_button_{i}`，共用同一 `_build_button` 几何。这是 multiplicity 轴（N 个同构按钮）的证据来源。

## 核心身份

drinking_fountain 是**公共饮水器/接水台**：一个落地或壁挂的主体，顶部一个开口的接水盆，盆上一个出水嘴（短饮水 gooseneck / 上喷 bubbler / 高瓶填充 arch），以及一个**用户操作的出水阀门主动件**（按下式 chrome 柱塞按钮，或脚踏式踏板）。前面板通常带刻字水瓶图标，下方常有悬挑的 perforated 瓶托格栅。它的身份核心是：**“有真实接水盆 + 出水嘴 + 至少一个真实活动的取水阀门主动件”** 的取水设施。默认成熟域是单按钮落地立柱式（parent 形态），但同样涵盖壁挂、圆盆、bubbler、瓶填充、脚踏与双按钮等已收敛变体；模板域允许把多台同构饮水器建成一个共享基座/背板/中心管线的 drinking fountain station（直线一排或环形一圈），但不能退化成无连接的场景摆放。

不该混入：装饰性园林喷泉/水景（无接水阀门主动件、以水景循环为主）；水龙头/水槽（属厨卫管件，无独立接水盆+立柱身份）；饮水机/桶装水机（封闭家电外壳 + 龙头，不是公共取水台结构）。

## 槽位 + 候选模块表

### Slot L：layout / unit arrangement（饮水器单元布局）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_unit | parent + all adopted samples | by-construction wrapper preserves existing single fountain chain | default / always eligible | 单台饮水器；不增加共享 rail/core，直接发射一个 unit。 |
| linear_bank | by-construction extension | implement via `for i in range(unit_count)` emitting `fountain_unit_{i}` transforms along X + shared back rail/base | eligible for pedestal_body and wall_mounted_body; foot_pedal allowed only with pedestal units | 一排公共饮水位，`unit_count` 台同构或同配置饮水器沿 X 等距排布，挂在共享 floor base rail 或 wall backplate 上；每个 unit 保留自己的 basin/spout/actuator。 |
| radial_ring | by-construction extension | implement via `for i in range(unit_count)` with yaw `2*pi*i/N` around shared central plumbing core | eligible for pedestal_body only; reject wall_mounted_body and foot_pedal unless implemented with clear outward floor clearance | 环形饮水岛，N 台 pedestal unit 绕 Z 轴等分，默认朝外，中心有共享 plumbing core / circular base；每个 unit 的 actuator 独立活动。 |

> Slot L 是本轮人工设计新增的 layout multiplicity 轴，5★ 样本未实证一排/一圈；实现阶段必须标记为 by-construction extension，并用共享 rail/core 把多台 unit 连成一个设施，而不是多个独立对象散放。

### Slot A：body / mounting（主体与安装）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pedestal_body | rec_build-a-realistic-articulated-3d-model-of-a-dric_20260609_215049_780247_b6678542 (parent) | `_build_pylon` L282-L308；root part `pylon_body` + inertial L566-L572 | eligible if compatible | 落地高瘦弧形 teal 立柱：loft swoosh 侧profile（front_pts/back_pts），hollow 钢壳 + 底部 foot pad 落地 z≈0，PYLON_H≈1.02 m。是 root，所有上层子件挂在它上。 |
| wall_mounted_body | rec_drick_fountain_var_wall_mounted_body | `_build_mounting_plate` L237-L261 + `_build_body` L264-L288；parts+joint `mounting_plate`/`body`/`plate_to_body` L511-L534 | eligible if compatible | 壁挂：薄壁 stainless 背板 root（贴墙 y≈0、PLATE_Z_CENTER≈0.9 m、四角螺孔）+ 紧凑 filleted 漆钢 body 壳 FIXED 在背板前。两段链（plate→body），后续盆/面板挂到 body。 |

### Slot B：basin / water-outlet module（接水盆与出水嘴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| parent_basin_spout | rec_build-a-realistic-articulated-3d-model-of-a-dric_20260609_215049_780247_b6678542 (parent) | `_build_basin`（rect）L311-L343 + `_build_spout`（短饮水 gooseneck）L346-L377；`pylon_to_basin` joint L585-L591；inertial `Box` L580-584 | eligible if compatible | 矩形开口接水盘 + 后壁升起短 gooseneck 前弯饮水嘴。盆 inertial 用 `Box`。基准盆模块。 |
| round_basin | rec_drick_fountain_var_round_basin | `_build_basin`（圆碗 + rim ring + 圆角底）L312-L356 + `_build_spout` L359-L390；`pylon_to_basin` joint L598-L604；inertial `Cylinder` L593-597 | eligible if compatible | 圆碗接水盆（cylinder 壳 + 顶 rim 环 + 圆角碗底 + 中心排水孔），spout 后壁挂点用 `-BASIN_R`；盆 inertial 用 `Cylinder`。X/Y 近似等径。 |
| bubbler_spout | rec_drick_fountain_var_bubbler_spout | `_build_spout`（上喷 bubbler，变半径收口）L361-L427 + 额外 helper `_hollow_variable_tube_mesh_from_path` L145-L215；盆沿用 parent rect `_build_basin` L326-L358 | eligible if compatible | 矩形盆 + 经典上喷 bubbler 出水嘴：平滑弧升到 apex（高于盆沿），用变半径管收口出一个朝上 nozzle，配 nozzle 底部 annular flange。 |
| bottle_filler | rec_drick_fountain_var_bottle_filler | `_build_bottle_filler_arch` L387-L435（FILLER_R/RISE/REACH L92-94）+ 额外 part/joint `bottle_filler_arch`/`basin_to_filler` L651-L669；并保留 rect 盆 `_build_basin` L318-L350 与饮水短 spout `_build_spout` L353-385（仍 emit，见 L636-637） | eligible if compatible | 矩形盆 + 饮水短 spout **再加**一个独立高 gooseneck 瓶填充 arch（FILLER_RISE≈0.26 m，下垂 nozzle），FIXED 在盆上。多 1 个 part + 1 条 FIXED joint。 |

### Slot C：actuator controls（出水主动件 / 控制）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_push_button | rec_build-a-realistic-articulated-3d-model-of-a-dric_20260609_215049_780247_b6678542 (parent) | `_build_button` L447-L468；part `push_button` + `faceplate_to_button` PRISMATIC joint L659-L681；常量 BTN_* L71-78 | eligible if compatible | 单个 chrome 柱塞 cap + 后伸 stem（captured 在 faceplate boss）；PRISMATIC 沿 -Y 内压，行程 BTN_TRAVEL≈0.008 m。 |
| dual_push_buttons | rec_drick_fountain_var_dual_push_buttons | actuator 复制循环 L666-L696（`NUM_BUTTONS=2` L75、`BTN_SPACING≈0.044` L76）；共用 `_build_button` L454-477 | eligible if compatible | 多个并排 `button_{i}`，等距 BTN_SPACING，各自独立 PRISMATIC joint `faceplate_to_button_{i}`，相互不联动。**multiplicity 轴的来源**（N=2 实证）。 |
| foot_pedal | rec_drick_fountain_var_foot_pedal | `_build_foot_pedal` L457-L537 + pylon pivot boss L312-L321；part `foot_pedal` + `pylon_to_pedal` REVOLUTE joint L727-L749；常量 PEDAL_* L80-86 | eligible if compatible | chrome 踏板（pivot barrel + 端盖 + 防滑筋 + 前唇），REVOLUTE 绕 -X 铰接在 pylon 底前 boss，PEDAL_PRESS≈0.30 rad 下压；不在 faceplate 上放 push_button。 |

> 说明：Slot B 的 `parent_basin_spout` 与 `round_basin` 是**盆形**变体；`bubbler_spout` 与 `bottle_filler` 是**出水嘴**变体（前者改 spout 内部几何，后者在保留盆+饮水嘴的基础上加一个 filler arch part）。模板可把“盆形 × 出水嘴附件”表达为 Slot B 的 4 个已收敛组合候选（见 §9 兼容矩阵），也可拆成两个 sub-axis；本 spec 先以 4 个收敛 candidate 表达，避免发明未实证的组合。

## 槽位图（slot graph）

pattern: `mixed`（layout 可复制整台 unit；unit 内 body 起串行链；actuator 上有 push-button multiplicity）

```
[Slot L layout]
  single_unit:   fountain_unit_0
  linear_bank:   fountain_unit_{i} (i=0..unit_count-1) --[FIXED transform on shared rail/backplate]--> bank_base / bank_backplate
  radial_ring:   fountain_unit_{i} (i=0..unit_count-1, yaw=2*pi*i/N) --[FIXED transform on central_core/circular_base]--> drinking_station_core

Each fountain_unit_i contains:
[Slot A body/mount]
  pedestal_body:    pylon_body(root, foot@z≈0)
  wall_mounted_body: mounting_plate(root, 贴墙 y≈0) --[FIXED: plate front face]--> body

        |  (上游 mounting parent = pylon_body 或 wall body 的顶面/前面)
        v
[Slot B basin/outlet]
  catch_basin  --[FIXED pylon_to_basin / body_to_basin, origin@顶面前移 BASIN_CY, z=顶]--> 挂在 body
  spout/bubbler  --[FIXED, basin-local（与 basin 同 part 的第二 visual 或 basin 子件）]
  (bottle_filler 时)bottle_filler_arch --[FIXED basin_to_filler, basin-local origin(0,0,0)]--> 挂在 basin
        |
        v
[front_faceplate]  --[FIXED pylon_to_faceplate / body_to_faceplate, origin@body 前面、z=面板中心]--> 挂在 body
        |  faceplate 前面提供 button boss / fitting boss / grille bracket 三个 mating 接口
        +--[FIXED faceplate_to_fitting]--> valve_fitting（侧面装饰阀件）
        +--[FIXED faceplate_to_grille]--> bottle_grille（下方悬挑瓶托格栅）
        |
        v
[Slot C actuator]  (核心运动；二选一互斥，push-button 上有 multiplicity)
  single_push_button:  push_button --[PRISMATIC faceplate_to_button, axis=(0,-1,0), [0, BTN_TRAVEL]]--> faceplate boss
  dual_push_buttons:   button_{i} (i=0..N-1) --[PRISMATIC faceplate_to_button_{i}, 同轴, 等距 BTN_SPACING]--> faceplate boss
  foot_pedal:          foot_pedal --[REVOLUTE pylon_to_pedal, axis=(-1,0,0), [0, PEDAL_PRESS]]--> pylon 底前 boss
```

接口/互斥说明：
- **L→unit 接口**：single 时 unit root 可直接作为 model root；linear_bank 必须有共享 `bank_base`/`bank_backplate`，每台 unit 通过 FIXED transform 挂到共享件；radial_ring 必须有共享 `drinking_station_core`/`circular_base`，每台 unit 绕 Z 等分并朝外。多 unit 的所有 actuator joint 保持独立，不允许用一个 joint 驱动整排/整圈。
- **A→B 接口**：basin/faceplate 的 mounting parent 由 Slot A 决定——pedestal 时 parent=`pylon_body`、basin joint origin 用 `(0, BASIN_CY, PYLON_H)`；wall 时 parent=`body`、origin 用 body-local 顶面坐标。模板需按所选 A 切换 parent 与 origin 派生（mating face = body 顶面 + 前面）。
- **B 内部**：`bottle_filler` 额外的 `bottle_filler_arch` 与 basin 是 basin-local FIXED（origin (0,0,0)）；其它盆/嘴变体不增 part。
- **C 互斥**：push-button 路线（single/dual）的 actuator parent=`faceplate`、PRISMATIC、轴 Y；foot_pedal 路线 parent=`pylon_body`/base、REVOLUTE、轴 X，且不放 push_button。三者中**任一时刻只取一条**（foot_pedal vs push-button 互斥；single vs dual 是 push-button 路线内的 N 取值）。
- **派生**：所有 faceplate/fitting/grille FIXED 子件位置由 Slot A 的 body 顶/前面与 faceplate 几何派生，不独立采样。

## 每槽位 Module Emits / Interfaces

### Slot A / module pedestal_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pylon_body`（弧形 hollow teal 立柱 + foot pad，落地 z≈0）；root part | parent / model.py:L282-L308, L566-L572 |
| internal joints | 无（单体 root，无内部活动件） | parent / model.py:L566-L572 |
| upstream interface | root；foot pad 底面 = 地面 contact plane（z≈0） | parent / model.py:L300-L308 |
| downstream interface | 立柱顶面（z=PYLON_H）+ 前面（swoosh front_y）供 basin/faceplate FIXED 挂载；foot_pedal 时底前 pivot boss | parent / model.py:L585-L591, L616-L622 |

### Slot A / module wall_mounted_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mounting_plate`（薄背板 root，贴墙 y≈0、四角螺孔）+ `body`（紧凑 filleted 漆钢壳） | rec_drick_fountain_var_wall_mounted_body / model.py:L237-L288, L511-L526 |
| internal joints | `plate_to_body`（FIXED，body 背面贴 plate 前面 y=PLATE_T、底 BODY_BOT_Z） | …/model.py:L528-L534 |
| upstream interface | mounting_plate 背面 = 墙面 contact plane（y≈0，z 居中≈0.9 m） | …/model.py:L237-L246, L652-L676 |
| downstream interface | body 顶面（BODY_TOP_Z）+ 前面（BODY_FRONT_Y）供 basin/faceplate 挂载 | …/model.py:L546-L552, L574-L580 |

### Slot B / module parent_basin_spout
| emits | 描述 | 来源 |
|---|---|---|
| parts | `catch_basin`（矩形开口盘，盆 + 第二 visual `spout` 短饮水 gooseneck） | parent / model.py:L311-L377, L574-L584 |
| internal joints | 无（spout 是 basin part 的第二 visual，FIXED 同 part） | parent / model.py:L578-L579 |
| upstream interface | 盆底中心 = body 顶面挂点（`pylon_to_basin` origin (0,BASIN_CY,PYLON_H)） | parent / model.py:L585-L591 |
| downstream interface | 盆沿 + 前面无活动下游（faceplate 挂 body，不挂 basin） | parent / model.py:L585-L591 |

### Slot B / module round_basin
| emits | 描述 | 来源 |
|---|---|---|
| parts | `catch_basin`（圆碗 + rim ring + 圆角碗底 + `spout`），inertial 用 `Cylinder` | rec_drick_fountain_var_round_basin / model.py:L312-L390, L588-L597 |
| internal joints | 无（spout 同 part 第二 visual） | …/model.py:L591-L592 |
| upstream interface | 圆碗底中心 = body 顶面挂点（`pylon_to_basin` (0,BASIN_CY,BASIN_Z)） | …/model.py:L598-L604 |
| downstream interface | 圆盆沿；无活动下游 | …/model.py:L598-L604 |

### Slot B / module bubbler_spout
| emits | 描述 | 来源 |
|---|---|---|
| parts | `catch_basin`（矩形盆）+ 第二 visual `spout` = 上喷 bubbler（变半径收口管 + 朝上 nozzle + flange） | rec_drick_fountain_var_bubbler_spout / model.py:L326-L427, L625-L637 |
| internal joints | 无（bubbler 同 basin part 第二 visual） | …/model.py:L633-L634 |
| upstream interface | 盆底中心 = body 顶面挂点（`pylon_to_basin`） | …/model.py:L639-L647 |
| downstream interface | 盆沿；bubbler apex 高于盆沿（朝上出水）；无活动下游 | …/model.py:L639-L647 |

### Slot B / module bottle_filler
| emits | 描述 | 来源 |
|---|---|---|
| parts | `catch_basin`（矩形盆 + 饮水短 `spout`）**加** 独立 part `bottle_filler_arch`（高 gooseneck + 下垂 nozzle） | rec_drick_fountain_var_bottle_filler / model.py:L318-L385, L633-L661 |
| internal joints | `basin_to_filler`（FIXED，basin-local origin (0,0,0)，把 filler arch 固定到盆） | …/model.py:L663-L669 |
| upstream interface | 盆底中心 = body 顶面挂点（`pylon_to_basin`）；filler arch base flange 坐 basin 后壁/底 | …/model.py:L643-L669 |
| downstream interface | 盆沿 + filler arch nozzle（高于盆沿前伸）；无活动下游 | …/model.py:L663-L669 |

### Slot C / module single_push_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_button`（chrome cap + 后伸 stem） | parent / model.py:L447-L468, L659-L666 |
| internal joints | `faceplate_to_button`（PRISMATIC，axis=(0,-1,0)，limits [0, BTN_TRAVEL≈0.008]） | parent / model.py:L671-L681 |
| upstream interface | faceplate 前面 button boss（cap 坐 boss 外端 y=FACE_T+BTN_BOSS_LEN；stem captured 在 boss/pylon） | parent / model.py:L412-L413, L671-L681 |
| downstream interface | 无（末端主动件） | parent / model.py:L671-L681 |

### Slot C / module dual_push_buttons（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `button_{i}`（i=0..N-1，共用 `_build_button` 几何，等距 BTN_SPACING） | rec_drick_fountain_var_dual_push_buttons / model.py:L454-L477, L666-L675 |
| internal joints | `faceplate_to_button_{i}`（各自独立 PRISMATIC，同轴 (0,-1,0)，limits [0, BTN_TRAVEL]，互不联动） | …/model.py:L684-L696 |
| upstream interface | faceplate 前面 button boss 区；每个 i 的 x = (i-0.5*(N-1))*BTN_SPACING | …/model.py:L670-L691 |
| downstream interface | 无 | …/model.py:L684-L696 |

### Slot C / module foot_pedal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `foot_pedal`（chrome treadle：pivot barrel + 端盖 + 防滑筋 + 前唇）；pylon 额外长 pivot boss | rec_drick_fountain_var_foot_pedal / model.py:L312-L321, L457-L537, L728-L729 |
| internal joints | `pylon_to_pedal`（REVOLUTE，axis=(-1,0,0)，limits [0, PEDAL_PRESS≈0.30]） | …/model.py:L739-L749 |
| upstream interface | pylon 底前 pivot boss（origin (0, BASE_FRONT_Y+0.010, PEDAL_PIVOT_Z)，离地约 0.042 m） | …/model.py:L312-L321, L738-L744 |
| downstream interface | 无 | …/model.py:L739-L749 |

> 不动的细节（valve_fitting、bottle_grille、bottle_pictogram、foot pad、boss）作为对应 part 的 parent visual / 第二 visual，不作为独立活动 part；它们的 FIXED 安装在 §9 的 allow_overlap / expect_contact 清单中声明。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `layout_mode` (Slot L) | enum | {single_unit, linear_bank, radial_ring} | single_unit | choice | sampler 选择；决定是否复制整台 fountain unit | by-construction layout axis |
| `unit_count` (Slot L mult.) | int | single=1；linear_bank `[2,6]`；radial_ring `[3,8]` | 1 | conditional | 仅 layout_mode≠single_unit 时有效；控制复制的整台饮水器数量 | by-construction layout axis |
| `unit_spacing` | float | linear `[0.38,0.62]` | 0.48 | conditional | 仅 linear_bank；相邻 unit X 间距 | by-construction layout axis |
| `ring_radius` | float | radial `[0.42,0.85]` | derived | conditional/equation | 仅 radial_ring；由 unit footprint 与 N 推导最小半径，再 clamp 到真实饮水岛尺度 | by-construction layout axis |
| `body_module` (Slot A) | enum | {pedestal_body, wall_mounted_body} | pedestal_body | choice | deterministic procedural sampler 选择 | Slot A table |
| `basin_module` (Slot B) | enum | {parent_basin_spout, round_basin, bubbler_spout, bottle_filler} | parent_basin_spout | choice | sampler 选择；决定盆形/出水嘴/是否加 filler arch | Slot B table |
| `actuator_module` (Slot C) | enum | {single_push_button, dual_push_buttons, foot_pedal} | single_push_button | choice | sampler 选择；push-button 路线再取 button_count | Slot C table |
| `button_count` (Slot C mult.) | int | [1, 2]（产品域 [1, 3]，见 §8） | 1 | conditional | 仅当 actuator∈{single/dual push-button} 有效；foot_pedal 时不适用 | dual src L75-76, L666-696 |
| `palette_style` | enum | {teal_steel, stainless_minimal, slate_grey, bronze_park, hospital_white}（≥3，见 §palette） | teal_steel | choice | 每 seed 抽一组配色，仅改材质 rgba，不改拓扑 | §palette / 全样本材质 |
| `pylon_height_scale` | float | [0.95, 1.06] | 1.0 | independent | 仅 pedestal_body；clamp 后保证 0.95<PYLON_H<1.10（测试要求 ~1 m） | parent L41, test L709-718 |
| `body_width_scale` | float | [0.92, 1.10] | 1.0 | independent | wall body 宽度/紧凑度；clamp 保证 body 仍宽>深、0.20<H<0.50 | wall src L53-62, test L683-697 |
| `basin_size_scale` | float | [0.9, 1.12] | 1.0 | independent | 盆 X/Y/R 等比；round_basin 时保证 0.14<直径<0.24 | round src L55-58, test L756-760 |
| `basin_cantilever_y` | float | derived | — | equation | `= 0.5*basin_depth + margin`，保证盆前伸（basin_cy>0.03）不悬空 | parent L60-61, test L734-739 |
| `btn_spacing` | float | [0.038, 0.050] | 0.044 | conditional | 仅 button_count≥2；上限随 faceplate 宽 FACE_X 派生（见不等式行） | dual src L76 |
| `btn_travel` | float | [0.006, 0.010] | 0.008 | independent | PRISMATIC 行程；clamp 到测试域 0.003<upper<0.020 | parent L78, test L810-816 |
| `pedal_press` | float | [0.22, 0.34] | 0.30 | independent | foot_pedal REVOLUTE 上限角；保证踏板下压可见且不穿地 | pedal src L86, test L877-888 |
| (—) | constraint | — | — | inequality | `button_count * btn_spacing ≤ FACE_X - 2*BTN_BOSS_R`（多按钮不超出面板宽）；违反则回缩 btn_spacing 或拒绝该 N | faceplate FACE_X parent L63, boss L76 |
| (—) | constraint | — | — | inequality | linear_bank 中 `unit_spacing ≥ unit_width + clearance_margin`；共享 rail/backplate 覆盖首尾 unit 外缘 | by-construction layout axis |
| (—) | constraint | — | — | inequality | radial_ring 中 `2*pi*ring_radius/unit_count ≥ unit_width + clearance_margin`，所有 unit yaw 朝外且 basin/actuator 不互穿 | by-construction layout axis |
| (—) | constraint | — | — | inequality | `bottle_filler arch peak ≤ 合理上限`且`filler nozzle 前伸 ≤ basin 前沿+margin`，避免高 arch 越界穿模 | filler src L92-94, L406-416 |
| (—) | constraint | — | — | inequality | foot_pedal 时 `actuator parent=pylon_body`，要求 body_module=pedestal_body；radial_ring 初版强制 pedestal_body 且建议排除 foot_pedal，除非踏板朝外且有地面 clearance | pedal src L739-744 + layout gate |

> 只表达语义选择、关键尺寸、行程/角度、multiplicity 数量与 palette。所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解；连续 scale 先采 independent、再派生 equation、再 inequality 投影回缩、最后按上游 choice 解析 conditional。

### palette_style 配色集（≥3，实测 + 合理近缘）
| palette_style | body（漆钢） | basin/grille（盆/格栅） | actuator/fitting（chrome 件） | engraving | 来源/依据 |
|---|---|---|---|---|---|
| teal_steel（默认，实测）| teal-blue `(0.06,0.45,0.62,1)` | brushed stainless `(0.74,0.76,0.78,1)` | polished chrome `(0.86,0.88,0.90,1)` | dark `(0.20,0.22,0.24,1)` | 全 7 样本实测 BLUE/STEEL/CHROME/DARK |
| stainless_minimal | 全 stainless `(0.74,0.76,0.78,1)` body | stainless 盆 | chrome | dark | 公共不锈钢饮水台常见；由实测 STEEL/CHROME 组合 |
| slate_grey | 灰漆 `(0.32,0.34,0.36,1)` | stainless | chrome | dark | grey 喷漆公共饮水器常见近缘 |
| bronze_park | 古铜 `(0.36,0.26,0.16,1)` | stainless | 暗铜 fitting `(0.45,0.34,0.22,1)` | dark | 公园铜质饮水台近缘配色 |
| hospital_white | 白漆 `(0.90,0.91,0.92,1)` | stainless | chrome | mid-grey `(0.45,0.47,0.50,1)` | 室内/医院白色饮水器近缘 |

> palette 只改材质 rgba，不改任何几何/拓扑/接口；每 seed 抽一组以保证 sweep 输出配色多样。

## Multiplicity / Copy Logic

本类别有 **2 根 multiplicity 轴**：整台饮水器单元数量 + 每台 unit 内的 push-button 数量。两根轴层级不同，不要混用。

### Axis 1：fountain unit layout multiplicity

- `count_param`: `unit_count`
- paired selector: `layout_mode`
- `N_range`: `single_unit=1`；`linear_bank` 测试域 `[2,4]`、产品域 `[2,6]`；`radial_ring` 测试域 `[3,6]`、产品域 `[3,8]`。
- sampling domain（权重档）：`single_unit` 高频（≈0.55）；`linear_bank` 中频（≈0.30，N=2/3/4 优先）；`radial_ring` 低频（≈0.15，N=3/4/6 优先，N=5/7/8 稀疏）。
- copied object：`fountain_unit_{i}`，即一整套 Slot A/B/C 生成结果（body/mount + basin/outlet + faceplate/fitting/grille + actuator）。每个 unit 内部保持完整结构和独立 actuator joint。
- naming：layout 层外壳使用 `fountain_unit_{i}` scope；实现若必须展平 part 名称，使用 `unit_{i}_pylon_body`、`unit_{i}_catch_basin`、`unit_{i}_button_{j}`、`unit_{i}_faceplate_to_button_{j}` 等前缀，避免多 unit 名称碰撞。
- placement：
  - `single_unit`: 原点处一台，沿用单台坐标。
  - `linear_bank`: 沿 X 等距，`x_i = (i - 0.5*(N-1))*unit_spacing`，朝向一致，挂到共享 `bank_base`（落地）或 `bank_backplate`（壁挂）。
  - `radial_ring`: 绕 Z 等分，`theta_i = 2*pi*i/N`，unit origin 位于 `ring_radius*(cos theta_i, sin theta_i, 0)`，yaw 使盆/使用面默认朝外；中心发射 `drinking_station_core` 与 `circular_base`。
- joint policy：layout 复制只用 FIXED transforms/parent joints 把 unit 固定到共享 rail/core；每台 unit 内的 push-button/foot-pedal joint 独立存在，互不联动。
- gating：`radial_ring` 初版仅允许 `pedestal_body`；`linear_bank` 可允许 pedestal 或 wall，但 wall 模式必须共享 backplate；`foot_pedal` 仍需 pedestal，radial_ring 中建议初版排除或强制朝外 clearance 检查。
- source/gating note：该轴是 by-construction extension，非 5★ 实证；审核时看它是否仍是一个整体 drinking fountain station，而不是多个 object 拼场景。

### Axis 2：per-unit push-button multiplicity

- `count_param`: `button_count`
- `N_range`: 测试域 `[1, 2]`（已实证：single=1、dual=2）；产品域建议 `[1, 3]`（双按钮常见冷/热或两档，偶见三按钮，但 5★ 只实证到 2，故采样权重压在 1–2）。
- sampling domain（权重档）：`N=1` 高频（≈0.6）、`N=2` 中频（≈0.35）、`N=3` 稀有（≈0.05，靠 by-construction 安全，sweep 稀疏覆盖）。仅当 `actuator_module ∈ {single_push_button, dual_push_buttons}` 时该轴有效；`single_push_button` ⇒ N=1，`dual_push_buttons` ⇒ N≥2。`foot_pedal` 时本轴不适用（pedal 始终 1 个，不暴露 count）。
- copied object：`button_{i}` part（共用 `_build_button` 几何）+ 各自 `faceplate_to_button_{i}` PRISMATIC joint。
- naming：`button_{i}`（i=0..N-1）；joint `faceplate_to_button_{i}`。N=1 时模板可沿用 parent 的 `push_button` / `faceplate_to_button` 命名（不带下标）以匹配 single 实证，或统一用 `button_0`——以审核为准，建议 N≥2 用 `button_{i}`、N=1 用 `push_button`。
- placement：沿 faceplate 前面水平等距 `bx = (i - 0.5*(N-1)) * BTN_SPACING`，与 button boss 同高 BTN_Z；居中对称。
- joint policy：每个按钮独立 PRISMATIC，axis=(0,-1,0)，limits [0, BTN_TRAVEL]，互不联动（dual 样本 L859-864 已断言 button_0 不带动 button_1）。
- source/gating：dual src `NUM_BUTTONS` L75 + loop L666-696；clamp `N ≤ floor((FACE_X-2*BTN_BOSS_R)/BTN_SPACING)`，越界回缩 spacing 或拒该 N。

## 拓扑多样性审计

总组合数（含 multiplicity）：
- 单台内部 Slot A × Slot B × Slot C(actuator kind) = 2 × 4 × 3 = **24** 个基本拓扑组合。
- push-button 路线再乘 button_count：single(N=1) 与 dual(N∈{2,3}) 共 1+2 = 3 种 N 形态；foot_pedal 无 N。
- 单台内部计入 button multiplicity 的拓扑等价类 ≈ 2(A) × 4(B) × [single(1) + dual(2 个 N) + foot_pedal(1)] = 2 × 4 × 4 = **32** 个 distinct 拓扑。
- layout multiplicity 再提供 `single_unit` + `linear_bank` 多个 N + `radial_ring` 多个 N 的整体设施拓扑；保守按测试域 `single(1) + linear(N=2,3,4) + radial(N=3,4,6)` 计 **7** 种 layout 形态。与内部 32 组合正交前理论上限很大，实际受 gating 后仍远超门槛。

理由：仅单台 Slot 组合就有 24，计入 button_count 达 ~32，远超 10；新增 layout multiplicity 又提供直线排布/环形排布的整机复制拓扑。各 Slot 候选都是真实结构不同（root part/joint/盆形/出水嘴 part 数/actuator joint type），layout 候选也必须有共享 rail/core 与不同 placement graph，不是纯尺寸/配色差异。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic procedural sampling，依次：(1) 抽 `layout_mode`，若非 single 再抽 `unit_count` / `unit_spacing` / `ring_radius`；(2) 抽 `body_module`（A，权重均匀偏 pedestal，radial_ring 强制 pedestal）；(3) 抽 `basin_module`（B，4 候选均匀，bottle_filler 略低因多 1 part）；(4) 抽 `actuator_module`（C），若 push-button 再按 §8 权重抽 `button_count`；(5) 经兼容矩阵合法化（foot_pedal ⇒ 强制 pedestal_body；radial_ring 初版排除 wall，建议排除 foot_pedal）；(6) 抽 `palette_style`；(7) 抽各 independent 连续 scale、派生 equation、inequality 投影回缩、conditional 解析。`seed=0` 不特殊。Topology target：1000-seed distinct 目标 ≥60（单台内部 ~32，再乘 layout 测试域若干形态；低于理论上限主要因 layout/body/actuator gating）。无需 regression overrides 作为主域；若个别 seed 回归失败再加 sparse override 并注明原因。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版应含的关键连续 scale 见 §7：`pylon_height_scale`、`body_width_scale`、`basin_size_scale`、`btn_spacing`(conditional)、`btn_travel`、`pedal_press`、`unit_spacing`/`ring_radius`(layout conditional)，以及派生 `basin_cantilever_y`。全部在 `resolve_config` clamp/派生：高度 clamp 到测试域（0.95–1.10 m）、盆径 clamp（round 0.14–0.24 m）、按钮行程 clamp（0.003–0.020）、踏板角 clamp（不穿地）、多按钮总宽不超面板（inequality）、多 unit 间距/半径不互穿。这些 scale 只改安全比例/clearance，不改 part tree、joint type/axis、multiplicity 上限或接口语义。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | L(layout+unit_count)→A→B→C(+button_count)→palette→scales 顺序加权采样 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | radial_ring⇒pedestal_body；linear_bank 可 pedestal/wall 但必须共享 base/backplate；foot_pedal⇒pedestal_body（pedal 铰接在 pylon 底前 boss，wall body 无该几何）；push-button 兼容 A 两者；basin 4 候选兼容 A 两者；single↔N=1、dual↔N≥2 | 无 floating/穿模、unit 互穿、actuator joint 轴/型/range 正确、多按钮不超面板、bottle_filler arch 不越界 |
| controlled local variation | §7 的连续 scale + clamp | 比例变化不破坏接口/clearance/支撑/joint origin/类别身份 |
| regression overrides | none（如需再 sparse 加并注明 seed+原因） | 仅已知失败回归 / 审核指定 |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| L layout | 3 | yes | yes | single unit / linear bank(unit_count) / radial ring(unit_count) |
| A body/mount | 2 | yes | no | 仅 2 个真实形态（落地 pedestal / 壁挂 wall）；样本池只此两类身份，已是该小类全部落地/壁挂主体证据，不发明第三种。 |
| B basin/outlet | 4 | yes | yes | rect盆+饮水嘴 / 圆盆 / bubbler上喷 / bottle-filler(+arch) |
| C actuator | 3 | yes | yes | single push / dual push(multiplicity) / foot pedal |

## Validator

- slot_choices_for_seed returns implemented module names（layout/unit_count + body/basin/actuator + button_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（radial_ring⇒pedestal_body；linear_bank needs shared rail/backplate；foot_pedal⇒pedestal_body；single⇒N=1、dual⇒N≥2）
- optional regression overrides are sparse and justified（默认 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；不破坏接口/clearance/joint origin/multiplicity（多按钮总宽 inequality、行程/角度 clamp、unit spacing/radius clamp）
- cross-part scale deps (equation/inequality/conditional) resolved in `resolve_config`
- 关键 InterfaceSpec/MatingContract 存在：body 顶/前面→basin/faceplate FIXED；faceplate boss→button captured；pylon 底前 boss→pedal pivot；wall plate 背面贴墙
- key joints 正确：push-button PRISMATIC axis≈(0,±1,0) range[0,BTN_TRAVEL]；foot_pedal REVOLUTE axis≈(±1,0,0) range[0,PEDAL_PRESS]；basin/faceplate/grille/fitting/filler 均 FIXED
- copied objects follow naming/placement：`fountain_unit_{i}` linear/radial placement 正确且共享 rail/core；`button_{i}` 等距、独立 joint、互不联动
- pedestal 站地 z≈0 且高瘦（h>5w）；wall plate 薄、宽>深、贴墙 y≈0、~0.9 m

## Reject cases

- actuator joint 退化为 FIXED 或无活动件（核心运动必须 ≥1 真实 joint：push-button PRISMATIC 或 foot-pedal REVOLUTE）。
- push-button 轴不沿 Y（按压方向错）、或 foot-pedal 轴不沿 X / 旋转使踏板穿地。
- foot_pedal 选到 wall_mounted_body（pedal 铰接点 pylon 底前 boss 不存在 → 悬空/无支撑）。
- radial_ring 选到 wall_mounted_body（壁挂背板无法围成自支撑饮水岛），或 ring 中 unit 没有共享中心 core/circular base。
- linear_bank / radial_ring 只是把多台无连接单体摆在一起，没有共享 rail/backplate/core/base（会退化成场景组合，不是一个 object）。
- 多 unit 间距不足导致 basin、faceplate、button、pedal 或 bottle_filler 互穿；radial_ring unit 未朝外或朝向混乱。
- basin 不开口（实心顶 / 没有接水腔）或盆不前伸（basin_cy≤0，盆悬在 body 后方）。
- 多按钮总宽超出 faceplate（button 飘出面板或互相穿模），或 button_count 联动（按一个带动另一个）。
- bottle_filler arch 高度/前伸越界，nozzle 穿盆或飘空（未与 basin FIXED）。
- round_basin 退化成方盆（X/Y 比例不近似 1）或直径超出 0.14–0.24 m 真实域。
- pylon 高度/比例失真（不站地 z≉0、或 h<5w 变成矮墩、或高度逸出 0.95–1.10 m 测试域）。
- 把纯配色/纯尺寸差异当作新 slot/candidate（palette 与 scale 不构成新拓扑）。

## 与相邻类别的边界

- 不该混入：装饰性园林/水景喷泉（无接水阀门主动件、以水循环喷涌为景观，无 push/pedal 取水动作；本类别核心是“可操作取水阀门”）。
- 不该混入：水龙头 / 水槽 / 厨卫管件（无独立立柱+接水盆+公共取水台身份，属管件配件）。
- 不该混入：饮水机 / 桶装水机 / 制冷热饮水器（封闭家电外壳 + 出水龙头，不是公共开放式接水盆结构，运动语义与外形家族不同）。
- 不该混入：洗手台 / 洗眼器（虽有盆 + 阀，但身份是清洗/急救设施，出水嘴形态与“饮水 gooseneck/bubbler/瓶填充”不同；如出现请走各自类别）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：①新增 Slot L layout multiplicity（linear_bank / radial_ring）为 by-construction extension，需确认类别允许 drinking fountain station 而不只单台；②Slot A 仅 2 candidate（落地/壁挂）——样本池仅此两身份，已说明降级理由，确认是否接受 2；③button_count 产品域 [1,3] 但只实证到 2，N=3 靠 by-construction，确认权重；④foot_pedal⇒pedestal_body 兼容 gate 是否保留（pedal pivot boss 仅 pylon 有），radial_ring 是否初版排除 foot_pedal；⑤bottle_filler 同时保留饮水短 spout + 额外 filler arch，是否作为单一 Slot B candidate（本 spec 取此法）还是拆成“盆形 × 出水嘴附件”两 sub-axis。 |

## 模板实现备注（可选）

- 共享 helper：`_unit`/`_cross`/`_combine_mesh_geometries`/`_hollow_tube_mesh_from_path`/`_annular_cylinder_mesh` 全样本通用；bubbler 额外需 `_hollow_variable_tube_mesh_from_path`（变半径管，bubbler src L145-215）；pedestal 需 `_loft_levels`/`_side_profile`/`_build_pylon`（loft 弧形）。
- InterfaceSpec/MatingContract 重点：(1) A→B/faceplate 的 mounting parent + origin 必须随 body_module 切换（pedestal: parent=pylon_body, origin 用世界 PYLON_H/FACE_Y；wall: parent=body, origin 用 body-local）；(2) push-button captured-pin：stem 嵌入 faceplate boss 并穿入 body/pylon，需 element-scoped `allow_overlap(faceplate,button)` + `allow_overlap(button, pylon/body)` + `expect_overlap(button,faceplate,axes="xz")`；(3) foot_pedal pivot boss 与 barrel 的 captured overlap；(4) faceplate↔body、grille↔faceplate/body、fitting↔faceplate/body 的 `allow_overlap`+`expect_contact` 须按所选 A（pylon vs body）复制对应 pair。
- Layout implementation：把单台 builder 做成可带 `prefix` 和 rigid transform 的 `_emit_fountain_unit(i, transform, config)`；linear_bank 先发射共享 `bank_base`/`bank_backplate`，再循环 unit；radial_ring 先发射 `drinking_station_core`/`circular_base`，再按 `theta_i` 循环 unit。所有 unit 内 part/joint 名称必须带 unit prefix，避免 collision。
- captured-pin overlap 须 element-scoped：button↔boss、pedal barrel↔pylon boss、filler flange↔basin。
- 暂不进入 seed domain 或低权重稀疏覆盖：button_count=3（产品域内但稀有，初版可只采 1–2，N=3 留作成熟审计稀疏覆盖）；unit_count>6；foot_pedal × wall_mounted_body（兼容矩阵硬性排除）；radial_ring × wall_mounted_body（硬性排除）；radial_ring × foot_pedal（建议初版排除，除非专门实现朝外 clearance）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | pedestal_body | rec_build-a-realistic-articulated-3d-model-of-a-dric_…_b6678542 (parent) | L282-L308, L566-L572 | 落地弧形立柱 root + 落地 contact + 上层挂点 |
| S2 | A | wall_mounted_body | rec_drick_fountain_var_wall_mounted_body | L237-L288, L511-L534 | 壁挂背板 root + body 壳 + plate_to_body |
| S3 | B | parent_basin_spout | parent | L311-L377, L585-L591 | 矩形盆 + 短饮水 gooseneck |
| S4 | B | round_basin | rec_drick_fountain_var_round_basin | L312-L390, L598-L604 | 圆碗盆 + Cylinder inertial |
| S5 | B | bubbler_spout | rec_drick_fountain_var_bubbler_spout | L145-L215, L361-L427 | 上喷 bubbler 变半径管出水嘴 |
| S6 | B | bottle_filler | rec_drick_fountain_var_bottle_filler | L387-L435, L651-L669 | 额外高 gooseneck 瓶填充 arch + basin_to_filler |
| S7 | C | single_push_button | parent | L447-L468, L659-L681 | 单 chrome 柱塞 PRISMATIC |
| S8 | C | dual_push_buttons | rec_drick_fountain_var_dual_push_buttons | L454-L477, L666-L696 | button_{i} 复制循环 + 独立 PRISMATIC（multiplicity 源）|
| S9 | C | foot_pedal | rec_drick_fountain_var_foot_pedal | L312-L321, L457-L537, L727-L749 | chrome 踏板 REVOLUTE + pylon pivot boss |
