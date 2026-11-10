# Binder clip — Modular Spec

> 来源小类：`picture/Stationary/Clip`（articraft_data 上游小类样本池；对象身份为 binder clip / foldback clip / bulldog clip，本 spec slug 取规范拼写 `clip`）。
> 上游 source map：建议回填 `picture_expansion/template_source_maps/Stationary__Clip.md`（当前尚未建立；本 spec 已逐一内联全部 record_id + module 来源，source map 缺失不影响来源完整性）。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 个 parent + 8 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 9 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（FORK_VARIANTS §7：收敛即入池——9 个样本均 compile rc=0、均含 ≥1 非 fixed joint、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_build_body_mesh` / `_band_profile` / `_dome_centerline` / `_knuckle_eyelet` / `_build_paddle_cq` / `_build_serration_tooth` / `_handle_points` / `_handle_strand_points` / `handle_{i}_pivot` / `front_handle_pivot` / `rear_handle_pivot` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `clip` |
| template path | `agent/templates/Stationary_Clip.py` |
| test path (optional) | `tests/agent/test_clip_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| __modular__ | `True` |
| pattern | `mixed`（root `clip_body` 前夹片 + REVOLUTE `moving_jaw` 后夹片 + parallel-handle-children 槽位：body_form + lip_bearing + handle_style + mouth_grip，**外加** handle 的 1/2 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 单轴 fork 变体；均 converged，compile rc=0、均有 ≥1 非 fixed joint、workbench-only）|
| read_count | 9（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests + prompt.txt）|
| read_scope | all 5-star samples in this category（小类只有这 9 个，无抽样）|
| source_index_policy | only adopted module sources are indexed below（9 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_build-a-realistic-articulated-3d-model-of-a-clip_20260609_200026_653659_6a1d52ff`）：折叠三角棱柱 spring-steel body（`_band_profile` 折线 + 两端 rolled-lip barrel），两根 U 形 wire 手柄各绕 lip Y 轴 REVOLUTE。**全批基线**：提供 body band 壳、连续 barrel lip、wire-U 手柄、双 REVOLUTE 装配。
- **S1 flat_lever**（`rec_clip_var_flat_lever_handles`）：把 wire 手柄换成 stamped 扁平 paddle lever（C 形 hook root 抱住 barrel + 平板 blade），`for i, cfg in HANDLE_CONFIGS` 循环发射，统一 joint policy。**handle_style=flat_paddle_lever 槽位来源 + 循环范式**。
- **S2 eyelet**（`rec_clip_var_eyelet_knuckle_pivot`）：lip 由连续 barrel 改为 N_KNUCKLES 个离散 pierced 短管 eyelet（`_knuckle_eyelet` + `_knuckle_y_positions` 循环 union 进 body）。**lip_bearing=knuckle_eyelets 槽位来源**。
- **S3 double_wire**（`rec_clip_var_double_wire_handles`）：每根手柄改成 STRAND_COUNT 根并排 wire strand（共享 hook root + tip，Y 偏移分开），`_handle_strand_points` 共享 helper。**handle_style=double_wire_strand 槽位来源**。
- **S4 serrated**（`rec_clip_var_serrated_mouth`）：两条 mouth 边各加 N_TEETH_PER_EDGE 个三角 serration 齿，作为 **body visual**（`_build_serration_tooth` 循环 add 到 body，不建独立 part）。**mouth_grip=serrated_teeth 槽位来源**。
- **S5 round_back**（`rec_clip_var_round_back_body`）：body 截面由折叠三角改成 soft folded roof（`_dome_centerline` + `_offset_curve` + spline），单一光滑 dome ridge。**body_form=rounded_dome 槽位来源**（footprint 截面成对变化）。
- **S6 single_handle**（`rec_clip_var_single_handle`）：只在 front lip 挂 1 根手柄，rear lip barrel 留空；`NUM_HANDLES=1` + `for i in range(NUM_HANDLES)` 循环。**handle multiplicity=1 来源**。
- **S7 wide_mouth**（`rec_clip_var_wide_mouth_footprint`）：DEPTH 0.026→0.044、APEX_Z 0.018→0.026、HANDLE_LEN 0.030→0.044，宽口 clamp。**controlled local scale（mouth_scale/apex_scale/handle_reach_scale）来源**。
- **S8 round_loop**（`rec_clip_var_round_loop_handles`）：手柄改成平滑 teardrop 闭环 wire loop（barrel 处窄、中段鼓出、尖端收窄，~17 控制点 spline）。**handle_style=teardrop_wire_loop 槽位来源**。

冗余说明：S0/S2/S4/S5/S6/S7/S8 的手柄均为 wire-U 基线（同一 `_handle_points`），只有 S1=paddle、S3=double、S8=teardrop 改 handle_style；S0/S1/S3/S4/S5/S6/S7/S8 的 lip 均为连续 barrel，只有 S2 改 knuckle。9 个 fork 各自只改 1 根结构轴，其余层与 parent 同构——这正是 fork 池"单轴控制变量"设计，diff 干净。

## 核心身份

桌面文具夹（binder clip / foldback clip / bulldog clip）：一片折叠 spring-steel 薄板（sheet ~0.0010 m）弯成大致三角棱柱的 body（长轴沿 X 前后、宽轴沿 Y、apex 在上、平底 mouth 在 z=0），body 两条底边卷成 rolled lip（barrel/eyelet）跨满 clip 宽度；夹体本身拆成前夹片 `clip_body` 与后夹片 `moving_jaw`，后夹片绕顶部 spring fold / apex 轴 **REVOLUTE** 打开 mouth；两根（或一根）钢丝/钢片 lever 手柄穿过 / 钩住对应 lip，各自绕 lip 的 **Y 轴 REVOLUTE**。**主用户机构 = 夹体 jaw opening + 手柄绕 lip 的 REVOLUTE 杠杆**（jaw range `[0, 0.55]` rad；每柄 range `[0, 0.18]` rad、axis 沿 lip Y）。

默认成熟域：一片折叠三角 / 圆顶 body 被 apex hinge 拆成前后两片 jaw，连续 barrel 或离散 knuckle eyelet 承轴，1 或 2 根 wire-U / paddle / teardrop / double-strand lever 手柄，可选 mouth serration 齿，body 宽口程度由 mouth_scale 连续缩放。活动语义包含"后夹片绕 apex 打开 mouth"与"手柄绕 lip Y 轴抬起"。serration 齿、lip 承轴恒为 jaw 几何（union 进 `front_jaw_shell` / `rear_jaw_shell` visual，不建 FIXED part）。

不该混入：clothespin / 衣夹（两片 + 弹簧枢轴在中段，非 rolled-lip wire 杠杆）、paper clip / 回形针（纯弯丝无活动件、无 body 壳与杠杆）、bull-dog clip 之外的 spring clamp / 工具夹钳（带螺纹/齿条/棘轮等额外机构，出文具语义）、hair clip / bobby pin（发夹身份）、clamp/G-clamp（带螺杆，非杠杆弹簧）。Stationary 大类内也区别于 Calculator / Folder / Pen 等无 rolled-lip 杠杆机构的文具。

## 槽位 + 候选模块表

> **建模注记（重要）**：clip 是 **root `clip_body` 前夹片 + `moving_jaw` 后夹片 + 一组 parallel handle children**——后夹片绕 apex `jaw_open_hinge` 打开，front handle 挂 `clip_body` 的 front lip，rear handle 挂 `moving_jaw` 的 rear lip。**这些 handle 不串成链**，各自独立绕对应 lip REVOLUTE。下面 body_form / lip_bearing / handle_style / mouth_grip 4 个 slot 都是 jaw 几何的并联可替换层；handle 的根数（1/2）由 §8 多重性轴描述。serration 齿与 lip 承轴均 union 进 jaw 几何，不单列 part。handle 的几何形态由 handle_style 决定，与 body_form 解耦（任何 body 都能配任何 handle）。

### Slot A：body_form（壳体截面族）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| folded_triangular（基线） | rec_..._6a1d52ff（S0；S1/S2/S3/S4/S6/S7/S8 同形） | `_band_profile` L69-83 + `_build_body_mesh` band L86-123 | eligible if compatible | 折线截面（front lip→apex→rear lip），sharp folded ridge，`polyline`+`close`+`extrude` 成 band |
| rounded_dome | rec_..._round_back_body（S5） | `_dome_centerline` L75-88 + `_offset_curve` L91-108 + `_build_body_mesh` spline L111-138 | eligible if compatible | soft folded roof 截面（直面板 + 轻微圆角 ridge），polyline 分片成 jaw |

> 降级理由（2 candidate）：本小类单 parent，body_form 仅 parent 折叠三角 + S5 圆顶两个真实收敛截面；现实 binder clip 形态词汇表本身窄（折叠三角 / 圆顶）。审核如需扩容应回 fork 池补造，不在模板侧虚构。

### Slot B：lip_bearing（卷边承轴形式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| continuous_barrel（基线） | rec_..._6a1d52ff（S0；多数样本） | `_build_body_mesh` 内 `lip()` L129-151 + union L153 | eligible if compatible | 跨满宽度的连续 hollow 卷管（outer−inner tube，沿 Y extrude），手柄穿管 |
| knuckle_eyelets | rec_..._eyelet_knuckle_pivot（S2） | `_knuckle_eyelet` L98-121 + `_knuckle_y_positions` L124-129 + union 循环 L177-180 | eligible if compatible | 一排 N_KNUCKLES 个离散 pierced 短管 eyelet（沿 Y 均布），手柄穿 eyelet |

> 降级理由（2 candidate）：optional-style 承轴槽，candidate 为 {连续 barrel, 离散 eyelet 排} 两个真实收敛形态；两者拓扑等价（手柄数/joint 数不变），但 body 几何 union 数量与外观显著不同。

### Slot C：handle_style（手柄形态/几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| wire_u_loop（基线） | rec_..._6a1d52ff（S0；多数样本） | `_handle_points` L157-195 + `tube_from_spline_points` L212-218 | eligible if compatible | U 形闭合钢丝环（两腿 + 弧尖），hook root 抱 barrel，单 `loop` visual |
| flat_paddle_lever | rec_..._flat_lever_handles（S1） | `_hook_profile` L155-179 + `_build_paddle_cq`（C-hook + blade）L182-227 | eligible if compatible | stamped 扁平 paddle：C 形 hook root（环形扇区 extrude）+ 平板 blade，单 `paddle` visual |
| teardrop_wire_loop | rec_..._round_loop_handles（S8） | `_handle_points`（teardrop 宽度剖面）L159-229 | eligible if compatible | 平滑泪滴闭环：barrel 处窄、中段鼓出（TEARDROP_MAX_HW）、尖端收窄，~17 控制点 spline，单 `loop` visual |
| double_wire_strand | rec_..._double_wire_handles（S3） | `_handle_strand_points` L161-201 + `for i in range(STRAND_COUNT)` 发射 L237-253 | eligible if compatible | 每柄 STRAND_COUNT 根并排 wire strand（共享 hook+tip，Y 偏移分开），多 `strand_{i}` visual |

> 4 candidate（达标 ≥3）：本小类 handle_style 是最富的轴，4 个真实收敛手柄形态各自来自不同 fork，几何与 visual 计数显著不同（paddle 单平板 vs wire 单环 vs teardrop 鼓环 vs double 双股）。

### Slot D：mouth_grip（咬合面齿；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain（基线） | rec_..._6a1d52ff（S0；多数样本） | （无 tooth；body 仅 band+lip）| eligible if compatible | 平滑 mouth（baseline 缺省）|
| serrated_teeth | rec_..._serrated_mouth（S4） | `_build_serration_tooth` L206-246 + 两边循环 add body visual L264-280 | eligible if compatible | 两条 mouth 边各 N_TEETH_PER_EDGE 个三角下指齿，作为 **body visual** union 进 body（不建独立 part）|

> 降级理由（含 plain 共 2 candidate）：optional 装饰/功能槽，candidate 为 {缺省, 1 个真实 serration 齿排}。`plain` 是 parent 基线合法取值。齿恒为 body 几何，不违反"不动装饰不建独立 part"。

## 槽位图（slot graph）

```
pattern: mixed（root chassis + parallel handle children + handle multiplicity）

                     clip_body (root/front jaw, body_form ∈ {folded_triangular, rounded_dome})
                      │   坐标：mouth 平底 z=0，apex 朝 +Z，宽轴 Y，深轴 X（front lip −X）
                      │   lip_bearing / mouth_grip union 进 front_jaw_shell
        ┌─────────────┴───────────────────────┐
        │                                      │
   handle_0 (front lip, 恒存在)          moving_jaw (rear jaw)
        │                                      │
   handle_style 几何                         REVOLUTE jaw_open_hinge
   REVOLUTE 绕 lip Y 轴                       绕 apex Y 轴 range [0,0.55]
   axis (0,+1,0) range [0,0.18]               │
                                              │ lip_bearing / mouth_grip union 进 rear_jaw_shell
                                         handle_1 (rear lip, 仅 n_handles==2)
                                              │
                                         同 handle_0（镜像 reach_dir/axis）
                                         REVOLUTE 绕 lip Y 轴
                                         axis (0,−1,0) range [0,0.18]
```

接口点位（每条 body→handle 连接）：
- **clip_body → moving_jaw**：mating = apex spring fold（`origin=(0, 0, apex_z)`），joint = REVOLUTE，axis `(0, −1, 0)`，range `[0, 0.55]`；正 q 把 rear lip 朝 +X 外摆，打开 mouth。
- **clip_body → handle_0**：mating = front lip 中心（`origin=(front_lip_x, 0, 0)`，落在真实 barrel/eyelet 几何上），joint = REVOLUTE，axis `(0, +1, 0)`，range `[0, 0.18]`。
- **moving_jaw → handle_1**（仅 `n_handles==2`）：mating = rear lip 在 moving-jaw 局部坐标中的中心（`origin=(rear_lip_x, 0, -apex_z)`），joint = REVOLUTE，axis `(0, −1, 0)`，range `[0, 0.18]`。
- Handle MatingContract = hook root 抱住 lip barrel（穿管/钩管的捕获过盈，broad allow_overlap）。
- **互斥/可选/派生**：handle_style 决定 handle 几何（与 body_form 无关）；mouth_grip / lip_bearing 派生进 body 几何；n_handles 决定挂几根 handle（1=仅 front，2=front+rear）。body_form 与 lip_bearing / handle_style / mouth_grip / n_handles 全部可自由组合（无互斥）。

## 每槽位 Module Emits / Interfaces

### Slot A / module folded_triangular
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip_body`（root/front jaw，`front_jaw_shell` visual）+ `moving_jaw`（rear jaw，`rear_jaw_shell` visual）| S0 / `_band_profile` L69-83、模板改进后的 `_jaw_centerlines` / `_build_jaw_mesh` |
| internal joints | `jaw_open_hinge` REVOLUTE，axis (0,−1,0)，range [0,0.55] | 模板改进 |
| downstream interface | front lip 中心线供 `handle_0` 锚定；rear lip 中心线在 `moving_jaw` 局部坐标供 `handle_1` 锚定 | S0 / lip L129-151 |

### Slot A / module rounded_dome
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip_body` front jaw + `moving_jaw` rear jaw（正弦 dome band 分片 + lip + 可选齿）| S5 / `_dome_centerline` L75-88、模板改进后的 `_jaw_centerlines` / `_build_jaw_mesh` |
| downstream interface | 同上，front lip 在 root，rear lip 在 `moving_jaw` 局部 z=`-apex_z` | S5 / lip L144-162 |

### Slot B / module continuous_barrel
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：连续 hollow 卷管 union 进 body | S0 / `lip()` L129-151 |
| upstream interface | 卷管表面（手柄 hook 抱管捕获）| S0 / L129-151 |

### Slot B / module knuckle_eyelets
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：N_KNUCKLES 个离散 eyelet 短管 union 进 body | S2 / `_knuckle_eyelet` L98-121、循环 L177-180 |
| upstream interface | eyelet 孔（手柄 hook 穿孔捕获）| S2 / L98-129 |

### Slot C / module wire_u_loop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（单 `loop` wire visual）| S0 / `_handle_points` L157-195 |
| internal joints | `handle_{i}_pivot` REVOLUTE，axis (0,±1,0)，range [0,0.18] | S0 / L243-261 + 模板改进 |
| upstream interface | hook root 抱 lip barrel（z=0 处含 joint origin）| S0 / hook L185-194 |

### Slot C / module flat_paddle_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（单 `paddle` 平板 visual：C-hook + blade）| S1 / `_build_paddle_cq` L182-227 |
| internal joints | `handle_{i}_pivot` REVOLUTE，axis (0,±1,0)，range [0,0.18] | S1 / L258-268 + 模板改进 |
| upstream interface | C 形 hook 抱 lip barrel（gap 朝外，捕获过盈）| S1 / `_hook_profile` L155-179 |

### Slot C / module teardrop_wire_loop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（单 `loop` teardrop wire visual）| S8 / `_handle_points` L159-229 |
| internal joints | `handle_{i}_pivot` REVOLUTE，axis (0,±1,0)，range [0,0.18] | S8 / L276-294 + 模板改进 |
| upstream interface | hook root 抱 lip barrel | S8 / hook L179-180 |

### Slot C / module double_wire_strand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（多 `strand_{k}` 并排 wire visual × STRAND_COUNT）| S3 / `_handle_strand_points` L161-201、循环 L237-253 |
| internal joints | `handle_{i}_pivot` REVOLUTE（整柄一个 joint），axis (0,±1,0)，range [0,0.18] | S3 / L258-276 + 模板改进 |
| upstream interface | 共享 hook root 抱 lip barrel | S3 / hook L191-200 |

### Slot D / module serrated_teeth
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：两边各 N_TEETH_PER_EDGE 个三角齿 union/add 进 body visual | S4 / `_build_serration_tooth` L206-246、循环 L264-280 |
| upstream interface | 齿基嵌入 mouth 边 body 壁（连通），齿尖朝 mouth 中心下指 | S4 / L260-280 |

### handle multiplicity / module handle_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（形态由 Slot C 决定）× n_handles | S6 循环 L231-258 / S0 双柄 |
| internal joints | `handle_{i}_pivot` REVOLUTE，axis (0,±1,0)，range [0,0.18] × n_handles | S6 L247-257 + 模板改进 |
| upstream interface | 各 lip 中心线（front 必有，rear 仅 n_handles==2）| S6 L75-83 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | {folded_triangular, rounded_dome} | folded_triangular | choice | deterministic procedural sampler 选择 | Slot A 表 |
| lip_bearing | enum | {continuous_barrel, knuckle_eyelets} | continuous_barrel | choice | sampler 选择 | Slot B 表 |
| handle_style | enum | {wire_u_loop, flat_paddle_lever, teardrop_wire_loop, double_wire_strand} | wire_u_loop | choice | sampler 选择 | Slot C 表 |
| mouth_grip | enum | {plain, serrated_teeth} | plain | choice | sampler 选择；optional | Slot D 表 |
| n_handles | int | [1, 2] | 2 | independent | 加权采样（2 偏多）后 clamp | §8 / S6 NUM_HANDLES |
| material_style | enum | {orange_steel, black_steel, silver_steel} | orange_steel | choice | sampler 选择（仅 palette）| 全样本 Material |
| mouth_scale | float | [0.92, 1.65] | 1.0 | independent | 缩放 DEPTH（mouth 深 X）；clamp 保宽口不退化 | S7 DEPTH L48 |
| apex_scale | float | [0.90, 1.18] | 1.0 | conditional | apex_z = clamp(APEX_Z·(0.5+0.5·mouth_scale)·apex_scale, 0.012, 0.040)；apex 随深度微长再缩放 | S7 APEX_Z L50 |
| handle_reach_scale | float | [0.90, 1.15] | 1.0 | conditional | handle_len = clamp(HANDLE_LEN·mouth_scale·handle_reach_scale, 0.018, 0.060)；杠杆随深度变长，clamp 防内塌 | S7 HANDLE_LEN L58 |
| (—) | constraint | — | — | inequality | handle hook 必含 joint origin (lip_x,0,0)：hook root 几何置于 z≈0 处使 part AABB 覆盖 origin（≤0.015 m baseline）| 接口 / 捕获 |

连续 scale 默认独立采样 mouth_scale → 由它派生 apex_z / handle_len（conditional，跟深度联动再各自 clamp）→ inequality 保证 hook 几何含 joint origin。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

handle 是唯一多重性来源，含 **1 根 count 轴**：

- `count_param`: **`n_handles`**（lever 手柄根数）
- `N_range`: `n_handles ∈ [1, 2]`（产品域；1=单柄变体 S6、2=标准双柄 parent）。真实 binder clip 恒为 1 或 2 柄，N>2 出类目，故上限锁 2。
- sampling domain（权重档）：2 柄高频（weights=[3,7]），1 柄稀有（单柄变体长尾）
- copied object: 单根手柄 part `handle_{i}`（形态由 handle_style 决定）+ 其 REVOLUTE 杠杆 joint；几何由共享 helper 按 handle_style 生成
- naming: `handle_{i}` / `handle_{i}_pivot`，`for i, spec in enumerate(_handle_specs(r))`（front 在 i=0，rear 在 i=1）
- placement: front lip（−half_d, 0, 0）必挂；rear lip（+half_d, 0, 0）仅 n_handles==2 挂
- joint policy: 每柄**独立** REVOLUTE，axis (0,±1,0)（front +Y / rear −Y），统一 range [0, 0.18]、统一 effort/velocity；front 挂 `clip_body`，rear 挂 `moving_jaw`；hook 捕获在 lip 上
- source/gating: 循环范式 S6 L231-258（NUM_HANDLES）/ S0 双柄；handle_style 内部若是 double_wire_strand 再做一层 strand 循环（S3），但那是单柄内的 visual 复制，不增 joint

## 拓扑多样性审计

总组合数（离散槽）：body_form(2) × lip_bearing(2) × handle_style(4) × mouth_grip(2) × n_handles(2) = **64**
（material_style 仅 palette，不计拓扑）。其中 handle_style 与 n_handles 改变 part/joint 计数或 visual 计数 = 真实拓扑等价类；body_form/lip_bearing/mouth_grip 改变 body 几何形态。
→ **64 distinct 拓扑**（实测 reachable_topology=63 saturated，仅 1 个组合采样未命中）。

理由：64 个离散组合即 >>10；handle_style(4)×n_handles(2) 单独就 8，再乘 body/lip/grip。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——加权选 4 个离散 slot（dome/eyelet/exotic-handle/serration 偏稀有，2 柄偏多）、采连续 scale（mouth_scale 宽域 [0.92,1.65]），经 `resolve_config` 的 conditional 把 apex/handle_len 跟 mouth 联动并 clamp。无非法组合（全 slot 自由组合），无需 compatibility 排除。`seed=0` 不特殊。无 regression overrides（初版 50 seeds pass_rate=1.0，无失败回归）。
Topology target：1000-seed slot choice tuple distinct 目标 >=60（本类上界 64；实测 50-seed 已 31 distinct、63/64 reachable saturated）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：初版含 `mouth_scale`（独立）/ `apex_scale` / `handle_reach_scale`（conditional，跟 mouth 联动），全部 clamp/派生，受 hook-含-origin、宽口不退化约束，不改变拓扑、杠杆 REVOLUTE 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：body→lip→handle→grip→n_handles→scales；加权（exotic 偏稀有、2 柄偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 全 slot 自由组合（无互斥）；n_handles∈[1,2]；scale clamp 保宽口与 hook-含-origin | 无穿模/悬空/越界、handle hook 抱 lip、抬手柄真升、serration 齿连 body |
| controlled local variation | mouth_scale / apex_scale / handle_reach_scale + clamp | 比例变化不破坏 hook 捕获、joint origin、宽口身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 overlap/origin 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 2 | yes | no | 单 parent 小类，折叠三角+圆顶两个真实截面；扩容须回 fork 池 |
| B lip_bearing | 2 | yes | no | 连续 barrel / 离散 eyelet 排 |
| C handle_style | 4 | yes | yes | wire-U / paddle / teardrop / double-strand，4 个真实形态 |
| D mouth_grip | 2 | yes | no | optional：{plain, serrated_teeth} |
| (mult) handle | n_handles[1-2] | — | — | 多重性轴，1 或 2 柄 |

## Validator

- slot_choices_for_seed returns implemented module names（body_form / lip_bearing / handle_style / mouth_grip + handles_{n}）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- 全 slot 自由组合，无互斥 gating；n_handles clamp 到 [1,2]
- optional regression overrides 初版为空
- controlled local scale params 全部 clamp，且不破坏 hook 捕获 / joint origin / 宽口身份
- cross-part scale 依赖（apex/handle_len vs mouth_scale、hook 含 origin）在 `resolve_config` 内 conditional/inequality 求解，不留到 builder 失败
- critical MatingContract 存在（grandfathered）：handle hook 抱 lip barrel/eyelet 捕获，broad allow_overlap(body, handle)
- jaw joint：`jaw_open_hinge` REVOLUTE axis (0,−1,0) range [0,0.55]
- handle joints：每柄 REVOLUTE axis (0,±1,0) range [0,0.18]
- copied objects 遵循 `handle_{i}` 命名 + front/rear lip placement + 统一 joint policy
- serration 齿、lip 承轴恒为 body 几何（不建 FIXED 装饰 part）

## Reject cases

- 把 serration 齿 / lip 承轴做成 FIXED-joint 独立 part（违反"不动几何 union 进 body"）。
- handle hook 不抱 lip：joint origin (lip_x,0,0) 落在空中（hook root 未置于 z≈0 使 part AABB 覆盖 origin）→ 触发 0.015 m articulation-origin baseline 失败。
- handle 悬浮不接触 body（未做 broad allow_overlap，或 hook 离 lip 太远）→ isolated/overlap 失败。
- 抬手柄方向错误（front 用 −Y / rear 用 +Y，导致外伸端往下而非往上）。
- 宽口 mouth_scale 把 handle_len 缩到内塌（未 clamp）或 apex 退化（未跟深度联动）。
- 用连续 enum/尺寸冒充拓扑：只改 mouth_scale/material 而不换 body_form/lip/handle/grip/n_handles 就当作新拓扑。
- handle 用手写命名的 1-2 个 handle 代替 `for i in range(n_handles)` 循环发射（多重性退化）。
- config_from_seed 采样到 n_handles>2（出类目）或非法 handle_style。

## 与相邻类别的边界

- 不该混入：clothespin / 衣夹（两片对称 + 中段弹簧枢轴，非 rolled-lip 单 body + 外挂 wire 杠杆）。
- 不该混入：paper clip / 回形针（纯弯丝、无 body 壳、无活动杠杆）。
- 不该混入：spring clamp / G-clamp / 工具夹钳（带螺杆/齿条/棘轮，非弹簧杠杆文具夹）。
- 不该混入：hair clip / bobby pin / 发夹（发饰身份，非桌面文具）。
- Stationary 大类内：区别于 Calculator / Folder / Pen / Scissors 等无 rolled-lip 杠杆机构的文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 模板已实现 `agent/templates/Stationary_Clip.py`（注册于 `cli/template.py` TEMPLATE_REGISTRY），`uv run articraft template sweep-pipeline clip` 分阶段 1/5/20/50 seeds 全 pass_rate=1.0，verdict=pass， distinct=31，reachable_topology=63/64 saturated。待审核问题：① body_form / lip_bearing / mouth_grip 各 2 candidate 的降级是否接受（单 parent 小类），还是要求回 fork 池补到；② n_handles ∈ [1,2] 上限锁 2 是否认可（真实 binder clip 恒 1/2 柄）；③ handle_style 与 body_form 完全解耦（任意 body 配任意 handle）是否符合现实约束。剩余：viewer 目检（人工）。|

## 模板实现备注（可选）

- 共享 helper：`_band_solid`（按 body_form 分折线/spline 两路）、`_add_lip`（按 lip_bearing 分 barrel/eyelet）、`_build_handle_visuals`（按 handle_style 分 wire-U/paddle/teardrop/double）、`_handle_specs`（按 n_handles 生成 front[+rear] 的 (lip_x,reach_dir,axis_y)）。
- MatingContract 注意点：handle joint omit MatingContract（captured-pin，grandfathered）；对每根 handle 声明 **broad** `allow_overlap(body, handle, reason=...)`（hook 抱 lip 的过盈捕获，参考 S0 L357-366，无法 element-scope 因 wire/barrel 接触面非轴对齐）。
- 派生与门控集中在 `resolve_config`：apex_z / handle_len（依赖 mouth_scale）、scale clamp。
- 每根 handle 几何在 lip-local frame 创作（origin 在 lip 中心），hook root 置于 z≈0 / 钩到 barrel 后方使 part AABB 覆盖 joint origin（满足 0.015 m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/mult | folded_triangular / continuous_barrel / wire_u_loop / 双柄基线 | rec_..._6a1d52ff | `_band_profile` L69-83、`_build_body_mesh` L86-154、`_handle_points` L157-195、双 REVOLUTE L243-261 | 折叠三角壳 + 连续 barrel + wire-U 手柄 + 双 REVOLUTE 装配基线 |
| S1 | C | flat_paddle_lever | rec_clip_var_flat_lever_handles | `_hook_profile` L155-179、`_build_paddle_cq` L182-227、`for cfg in HANDLE_CONFIGS` L246-268 | 扁平 paddle 手柄 + C-hook 捕获 + 循环范式 |
| S2 | B | knuckle_eyelets | rec_clip_var_eyelet_knuckle_pivot | `_knuckle_eyelet` L98-121、`_knuckle_y_positions` L124-129、union 循环 L177-180 | 离散 eyelet 承轴 |
| S3 | C | double_wire_strand | rec_clip_var_double_wire_handles | `_handle_strand_points` L161-201、`for i in range(STRAND_COUNT)` L237-253 | 双股并排 wire 手柄 + strand 循环 |
| S4 | D | serrated_teeth | rec_clip_var_serrated_mouth | `_build_serration_tooth` L206-246、两边循环 add body visual L264-280 | mouth serration 齿（body visual）|
| S5 | A | rounded_dome | rec_clip_var_round_back_body | `_dome_centerline` L75-88、`_offset_curve` L91-108、spline band L111-138 | soft folded roof 分片 jaw |
| S6 | mult | n_handles=1 | rec_clip_var_single_handle | `NUM_HANDLES` L71、`HANDLE_CONFIGS` L75-83、`for i in range(NUM_HANDLES)` L231-258 | 单柄多重性 + 循环范式 |
| S7 | scale | mouth/apex/handle_reach scale | rec_clip_var_wide_mouth_footprint | DEPTH L48、APEX_Z L50、HANDLE_LEN L58、宽口比例检查 L254-281 | 宽口连续缩放（mouth/apex/handle reach）|
| S8 | C | teardrop_wire_loop | rec_clip_var_round_loop_handles | `_handle_points`（teardrop 剖面）L159-229、宽度检查 L375-389 | 泪滴鼓环 wire 手柄 |
