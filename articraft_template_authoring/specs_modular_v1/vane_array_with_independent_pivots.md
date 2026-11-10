# Modular Spec — vane_array_with_independent_pivots

## 元信息
| 项 | 值 |
|---|---|
| slug | `vane_array_with_independent_pivots` |
| template path | `agent/templates/vane_array_with_independent_pivots.py` |
| test path (optional) | `tests/agent/test_vane_array_with_independent_pivots_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` |

`multiplicity`：核心拓扑是 `frame_support --N × vane_pivot(REVOLUTE)--> vane_i`，frame 作为公共 parent 通过 N 个独立 REVOLUTE 关节挂 N 个等距独立 vane；frame_support / vane_shape / pivot_endcap 形成三轴枚举，N 是模板级 multiplicity，决定 vane 数量与 pivot joint 数量。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 42 |
| read_count | 42 |
| read_scope | all 5-star samples in this category（`model.py` / `revision.json` / `record.json` / `prompt.txt` / category metadata 全量精读，分 4 批并行 Explore，未抽样） |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构族分布（42 个样本）：

| 轴 | 观察到的真实结构变体 | 样本计数 |
|---|---|---|
| frame_support | rectangular_perimeter_frame / side_rail_pair / side_wall_housing / rear_backplate_frame / fork_backed_rail / top_support_rail (under-slung) | 16 / 8 / 4 / 2 / 4 / 2，6 perimeter_with_backplate 折入相邻族 |
| vane_shape | flat_rectangular_box / thickened_blade_with_chamfer / lathe_or_lofted_airfoil / sheet_metal_thin | 12 / 4 / 17 / 9 |
| pivot_endcap | two_end_stub_pins / single_thru_shaft / end_lugs_with_separate_shaft / hidden_endcap_bosses | 13 / 9 / 12 / 8 |
| vane_count N | {4, 5, 6, 7, 8, 11} 主流，中位 N=6；少数 4 与 7-11 | 4: 2 / 5: 12 / 6: 18 / 7: 7 / 8: 1 / 11: 1 |
| pivot axis | horizontal x (most), vertical z (under-slung / vertical louver) | x: 39 / z: 3 |
| joint range | 多为 ±0.45 ~ ±1.05；少数单向（0..1.25 rec_0cd6 / 0..1.57 rec_bb30）或不对称（-0.45..+0.75 rec_db1a） | 全部 |
| primitive | cadquery (threePointArc/ellipse/box) / pure Box+Cylinder / ExtrudeGeometry / MeshGeometry / TorusGeometry / rounded_rect_profile | 30 cadquery 之类 / 12 pure box+cyl |
| 配件细节（不构成 slot） | 闭合姿态预设角 (REST_PITCH) / blue 调节 tab / stop_tabs / feet / 螺帽细节 | 散落出现 |

## 核心身份

`vane_array_with_independent_pivots` 的不变身份：**一个固定外框（perimeter 或 side rails 或 wall-backed 或 fork-backed 或 top-supported）支撑 N≥3 片独立旋转的窄长 vane / louver / slat / shutter，每片 vane 通过 frame 内壁的 pivot landing（boss / bushing / drilled hole / fork lug）由 REVOLUTE 关节（恒水平 x 轴；少数 under-slung 变体竖直 z 轴）独立铰接到 frame；N 片 vane 拓扑相同（同形 helper 复用）、姿态独立可调；vane 之间不通过 tie-rod 联动（独立 = independent pivots）。**

最小合法体 = 一个 frame + N 个 vane（N≥3）+ N 个独立 pivot REVOLUTE joint；frame 与 vane 之间是 1:N parent-children 拓扑（parallel children，frame 是公共 parent）。

默认成熟域：airflow louver / inspection shutter / service vent / panel louver bank / 实验室 / 通风栅格 / 调光百叶 / 风口控制阀。无 tie-rod、无联动 linkage、无 motor 驱动，每片 vane 由独立 hinge 控制（手动或外控）。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：frame_support（固定外框 / 支撑，frame 拓扑决定 vane 铰接接口位置）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular_perimeter_frame | rec_vane_array_with_independent_pivots_5c0752059fc0423fbee48adeba6edd01 | L51-L80 | eligible if compatible | 4 个矩形条 Box: 左/右 side_rail + 上/下 top/bottom_rail 组成 closed perimeter；frame inner face 上 N 个 pivot_boss landing |
| side_rail_pair | rec_vane_array_with_independent_pivots_0001 | L35-L53 | eligible if compatible | 仅左/右 2 条 SIDE_RAIL（无 top/bottom rail），可选 1 条 top_bar；frame 仅供 vane 端 pivot 铰接，前后开放 |
| side_wall_housing | rec_vane_array_with_independent_pivots_35e8b0abd3b24946ad156748f6cb3d41 | L71-L143 | eligible if compatible | perimeter + 前/后 flange（C-channel 或 box-section），含 SUPPORT_PAD landing；像 HVAC 风口外壳 |
| rear_backplate_frame | rec_vane_array_with_independent_pivots_0ff0a1e556e1411b9ba770d781cbbb48 | L60-L116 | eligible if compatible | 背板 back_panel + 顶/底/侧 rail；wall-backed louver bank，pivot_pad 在背板前面 |
| fork_backed_rail | rec_vane_array_with_independent_pivots_b9e39931875040e4b52f585a88e0b901 | L75-L142 | eligible if compatible | 主 frame + 后置 fork supports / bridges，bushing 嵌在 fork cheek 之间 |
| top_support_rail | rec_vane_array_with_independent_pivots_81ee50c95f4e4dd18ad348594bf5e6a2 | L60-L84 | eligible if compatible | 仅 top_rail 横梁（无侧/底 rail），vane 从上方铰接、向下垂挂；pivot 轴竖直 z（under-slung） |

注：perimeter_frame_with_backplate (rec_0007 L97-L178 / rec_e798b L131-L178 / rec_f486 L103-L117) 是 rear_backplate_frame + 全 perimeter 的组合变体，折入 rear_backplate_frame 与 side_wall_housing 内部 module-local scale variant，不单列；rec_249e 的 perimeter + bottom_rail 是 rectangular_perimeter_frame 的 narrow variant。硬约束：每 slot ≥3 candidate，本 slot 6 个；均有真实 5 星 source。

### Slot B：vane_shape（vane / blade / slat 主体几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_rectangular_box | rec_vane_array_with_independent_pivots_5c0752059fc0423fbee48adeba6edd01 | L109-L114 | eligible if compatible | 单一 Box vane body；chord × thickness × length；最简且最常见 |
| thickened_blade_with_chamfer | rec_vane_array_with_independent_pivots_46de95e7b856425b997422d4e45e27a7 | L28-L64 | eligible if compatible | 主体 Box / Extrude + leading/trailing edge chamfer 或 cambered profile；MeshGeometry 自定义截面 |
| lathe_or_lofted_airfoil | rec_vane_array_with_independent_pivots_0001 | L63-L88 | eligible if compatible | cadquery threePointArc 对称 airfoil profile + extrude，or ellipse extrude；最丰富、声学/HVAC 风格 |
| sheet_metal_thin | rec_vane_array_with_independent_pivots_e798b5780b4b4ad1a1a5092e9a5b4db2 | L74-L113 | eligible if compatible | 薄板 vane (mesh 或 ellipse extrude) + rolled lip / edge fold，sheet-metal-like 视觉 |

硬约束：每 slot 4 个 candidate，均有真实 5 星 source；primitive complexity 不可降级（airfoil / sheet_metal 必须保留 cadquery 或 Mesh 主体）。

### Slot C：pivot_endcap（vane 端铰接结构，决定 vane 端 vs frame 接口几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| two_end_stub_pins | rec_vane_array_with_independent_pivots_0001 | L80-L88 | eligible if compatible | 每片 vane 两端各 1 个 Cylinder pin（stub_pin），插入 frame inner face 的 boss / drilled hole |
| single_thru_shaft | rec_vane_array_with_independent_pivots_0002 | L64-L80 | eligible if compatible | 单根 Cylinder 长 shaft 贯穿 vane 整个 chord 方向，两端伸出 vane 体，sleeve into frame |
| end_lugs_with_separate_shaft | rec_vane_array_with_independent_pivots_a7c7ef5f1c1e4ba59e1a8123ff3ee74c | L93-L104 | eligible if compatible | vane 两端 lugs / journals（含 Cylinder collar + Cylinder pin）+ 独立 axle shaft；最复杂 |
| hidden_endcap_bosses | rec_vane_array_with_independent_pivots_e798b5780b4b4ad1a1a5092e9a5b4db2 | L219-L234 | eligible if compatible | vane 端 Cylinder boss 嵌入 vane 体内、半隐藏；frame 侧 bearing_sleeve 接 boss；干净低 profile |

## 槽位图（slot graph）

pattern: multiplicity

```
[Slot A frame_support]（rectangular_perimeter / side_rail_pair / side_wall_housing / rear_backplate / fork_backed / top_support）
   │
   ├─ N × [vane_pivot_i; REVOLUTE; axis=(1,0,0) 主，少数 (0,0,1) (top_support); range≈[lower, upper]∈([-1.0,-0.20], [0.40,1.30])]
   │      │
   │      ▼
   │   [Slot B vane_shape × Slot C pivot_endcap]（独立 vane_i，i=0..N-1，每个 vane 同形 helper 实现）
   │
   ├─ frame 内壁 / 上沿 / 背面 / fork 侧 N 个 pivot_landing（受 frame_support × pivot_endcap 派生）
   └─ frame 静态装饰（feet / flanges / fasteners / stop_tabs，全部 parent.visual(...)，不动作）
```

接口点位与跨 slot joint：

- **A→N × (B,C)（vane_pivot_i，恒存在 N 次）**：REVOLUTE，axis 默认 (1,0,0)（horizontal x，沿 vane chord 方向）；top_support_rail 变体下 axis = (0,0,1)（vertical z，under-slung）。接口=frame 的 pivot_landing 第 i 个位置（沿 vane array 方向等距分布；e.g. side rails inner face 高度 i 处的 boss）↔ vane 端 pivot_endcap（pin / shaft / lug / boss）captured 关系。pivot origin 落 vane chord 中线两端 pivot landing 连线中点（vane chord center 与 frame inner face 之间）。range 由 `vane_tilt_lower` / `vane_tilt_upper` 派生。
- **vane 间接口**：无（独立 pivot，无 tie-rod，无 gear coupling）；相邻 vane 之间的 closed-pose overlap 由 frame_pitch 与 vane chord 决定。
- **frame 内部**：rectangular_perimeter 是 4 条 rail 围成 closed loop，side_rail_pair 仅 2 条 rail，rear_backplate 是 panel 主体 + rail 边框，fork_backed 是 frame + 后置 fork bridges，top_support 仅 1 条横梁。每种 frame 内部不带独立 joint（frame 内 visual all parent.visual(...)）。

互斥/可选/派生：

- `top_support_rail` ⇒ pivot axis = (0,0,1)，vane 从 top_rail 垂挂；其他 frame ⇒ pivot axis = (1,0,0)（水平）。
- `top_support_rail` ⇒ pivot_endcap ∈ {two_end_stub_pins, single_thru_shaft, hidden_endcap_bosses}（end_lugs 需要双侧 frame landing，under-slung 只有顶单侧 landing 因此禁用）。
- `side_rail_pair` 与 `rectangular_perimeter_frame` 兼容所有 vane_shape × 所有 pivot_endcap。
- `rear_backplate_frame` ⇒ pivot_endcap ∈ {two_end_stub_pins, end_lugs_with_separate_shaft, hidden_endcap_bosses}（single_thru_shaft 需穿透背板不实际，禁用）。
- `fork_backed_rail` 兼容所有 pivot_endcap，重点是 fork lug ↔ pin 捕获。
- `side_wall_housing` 兼容所有 pivot_endcap。
- `lathe_or_lofted_airfoil` 与 `sheet_metal_thin` 优先配 single_thru_shaft / hidden_endcap_bosses（airfoil 截面便于穿轴 / 嵌入 boss）；与 two_end_stub_pins / end_lugs 也兼容但视觉清洁度降。
- `flat_rectangular_box` 兼容所有 pivot_endcap（最简）。
- `thickened_blade_with_chamfer` 优先 end_lugs / hidden_bosses（chamfer 与 stub_pin 视觉冲突）。

## 每槽位 Module Emits / Interfaces

### Slot A / module rectangular_perimeter_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（单 part：左 side_rail + 右 side_rail + 上 top_rail + 下 bottom_rail，全 Box visual） | rec_…_5c0752 / L51-L80；rec_…_a8425d L72-L111 |
| downstream interface | side_rail inner face 上 N 个等距 pivot_boss 或 drilled hole；pivot origin = (0, side_pad_y_i, side_pad_z_i) | rec_…_5c0752 / L99-L114 |
| 静态装饰 | 螺帽 / fastener heads / feet（parent visual） | rec_…_db1a L31-L55 |

### Slot A / module side_rail_pair
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（仅 左/右 2 条 SIDE_RAIL + 可选 top_bar 拉结，无 top/bottom 完整 rail） | rec_…_0001 / L35-L53；rec_…_c36b L17-L39；rec_…_3cda L39-L63 |
| downstream interface | side_rail inner face N 个 bearing_pad 或 boss 等距 | rec_…_0001 / L99-L132 |

### Slot A / module side_wall_housing
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（perimeter + 前/后 flange / C-channel + SUPPORT_PAD landing） | rec_…_35e8 / L71-L143；rec_…_a7c7 L123-L149；rec_…_e83b L42-L99；rec_…_8976 L63-L90 |
| internal helpers | 前后 flange 用 Box / rounded_rect_profile ExtrudeGeometry | rec_…_8976 L37-L42 |
| downstream interface | SUPPORT_PAD / socket / bushing N 个 | rec_…_35e8 L147-L158 |

### Slot A / module rear_backplate_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（back_panel Box 主体 + 顶/底/侧 rail 包边 + N 个 pivot_pad） | rec_…_0ff0 / L60-L116 |
| downstream interface | pivot_pad 在 back_panel 前面，N 个等距 | rec_…_0ff0 / L93-L116 |

### Slot A / module fork_backed_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（perimeter + 后置 fork bridges / cross-bars，bushing 嵌 fork cheek） | rec_…_b9e3 / L75-L142；rec_…_339f L71-L96；rec_…_6b0e L58-L108；rec_…_f2c4 L135-L162 |
| downstream interface | fork_cheek 之间的 pivot_bushing（左/右各 N 个） | rec_…_b9e3 / L124-L142；rec_…_339f L85-L96 |

### Slot A / module top_support_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame（仅 1 条 top_rail 横梁 + 可选 mounting flanges；无侧 / 底 rail） | rec_…_81ee / L60-L84；rec_…_f486 L103-L117 |
| downstream interface | top_rail 下沿 N 个等距 bearing_washer / 套环 landing | rec_…_81ee / L65-L84 |
| 派生 | pivot axis 必须 (0,0,1)（竖直），vane 从 top 垂挂 | rec_…_f486 |

### Slot B / module flat_rectangular_box
| emits | 描述 | 来源 |
|---|---|---|
| visuals | vane 主体 Box（chord × thickness × span_length） | rec_…_5c0752 / L109-L114；rec_…_c36b L50-L52；rec_…_db1a L87-L89 |

### Slot B / module thickened_blade_with_chamfer
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 主体 Box / Extrude（含 cambered profile）+ leading/trailing edge chamfer | rec_…_46de / L28-L64；rec_…_66909 L98-L119；rec_…_e798 L74-L113；rec_…_b9e3 L43-L48 |
| internal helpers | MeshGeometry cambered profile / rounded edge Box | rec_…_46de L28-L64 |

### Slot B / module lathe_or_lofted_airfoil
| emits | 描述 | 来源 |
|---|---|---|
| visuals | cadquery threePointArc 对称 airfoil profile + extrude（或 ellipse extrude） | rec_…_0001 / L63-L88；rec_…_0002 L63-L80；rec_…_35e8 L53-L61；rec_…_8976 L37-L42；rec_…_98572 L78-L85；rec_…_249e L47-L66；rec_…_d91a L29-L49 |
| internal helpers | cadquery / ExtrudeGeometry / rounded_rect_profile | 同上 |

### Slot B / module sheet_metal_thin
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 薄 ellipse / box extrude vane body + rolled edges（Cylinder edge bar）+ optional 折边 | rec_…_e798 / L74-L113；rec_…_f486 L76-L89；rec_…_6b0e L111-L158；rec_…_543b L111-L164；rec_…_40f5 L92-L147 |

### Slot C / module two_end_stub_pins
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 每 vane 两端各 1 个 Cylinder stub_pin（pin radius ~0.004-0.008，length ~0.012-0.020） | rec_…_0001 / L80-L88；rec_…_0ff0 L129-L178；rec_…_c36b L56-L59；rec_…_98572 L113-L130；rec_…_b9e3 L58-L60 |

### Slot C / module single_thru_shaft
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 单根 Cylinder（radius ~0.0045-0.008，length = vane span + 2 × frame_thickness）贯穿 vane | rec_…_0002 / L64-L80；rec_…_277b L180-L192；rec_…_a076 L125-L130；rec_…_d91a L137-L141；rec_…_883a L181-L197；rec_…_f2c4 L113-L124 |

### Slot C / module end_lugs_with_separate_shaft
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 每 vane 两端 lug 组合：collar（Cylinder）+ journal（Cylinder）+ 独立 axle shaft；最复杂 | rec_…_a7c7 / L93-L104；rec_…_9ed0 L70-L77；rec_…_a8425 L49-L61；rec_…_5c0752 L115-L132；rec_…_543b L131-L142；rec_…_66909 L106-L114；rec_…_db1a L93-L96 |

### Slot C / module hidden_endcap_bosses
| emits | 描述 | 来源 |
|---|---|---|
| visuals | vane 端内嵌 Cylinder boss（半隐藏在 vane 体内）+ frame 侧 bearing_sleeve 接 boss | rec_…_e798 / L219-L234；rec_…_8976 L126-L135；rec_…_6b0e L145-L156；rec_…_f486 L117-L122 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| frame_support (A) | enum | rectangular_perimeter_frame / side_rail_pair / side_wall_housing / rear_backplate_frame / fork_backed_rail / top_support_rail | sampled | deterministic procedural sampler | Slot A |
| vane_shape (B) | enum | flat_rectangular_box / thickened_blade_with_chamfer / lathe_or_lofted_airfoil / sheet_metal_thin | sampled | 受 frame gating（弱） | Slot B |
| pivot_endcap (C) | enum | two_end_stub_pins / single_thru_shaft / end_lugs_with_separate_shaft / hidden_endcap_bosses | sampled | 受 frame gating（top_support / rear_backplate 限制 single_thru_shaft / end_lugs） | Slot C |
| vane_count | int (multiplicity) | {3,4,5,6,7,8,9,10,11,12} | 6 | deterministic procedural sampler | 全样本 N 分布 |
| pivot_axis | enum | x_horizontal / z_vertical | x_horizontal | 由 frame_support 派生（top_support → z_vertical，其他 → x_horizontal） | rec_…_81ee / c2eef / f486 |
| vane_tilt_lower | float | [-1.10, -0.20] | -0.65 | vane pivot lower limit (rad) | 全样本 |
| vane_tilt_upper | float | [0.40, 1.30] | 0.85 | vane pivot upper limit (rad) | 全样本 |
| vane_rest_pitch | float | [-0.35, 0.50] | 0.0 | rest pose (vane closed-pose) angle | rec_…_277b VANE_ROLL=-0.28；rec_…_66909 REST_PITCH=-0.49；rec_…_543b BLADE_REST_ANGLE=0.48 |
| frame_width | float | [0.24, 0.62] | 0.42 | frame 横向（vane span 方向）宽度 | 全样本 |
| frame_height | float | [0.18, 0.55] | 0.32 | frame 纵向（vane array 排列方向）高度 | 全样本 |
| frame_depth | float | [0.018, 0.080] | 0.038 | frame rail/wall 厚度 | 全样本 |
| vane_chord | float | [0.030, 0.090] | 0.050 | vane chord 长度（vane 沿气流方向的宽度） | 全样本 |
| vane_thickness | float | [0.004, 0.018] | 0.008 | vane 厚度 | 全样本 |
| vane_pitch_spacing | float | [0.025, 0.085] | 0.045 | 相邻 vane 中心距 | 全样本派生 frame_height/(N+1) |
| pivot_pin_radius | float | [0.0035, 0.0085] | 0.005 | pivot pin / shaft radius | 全样本 |
| vane_chord_scale | float | [0.90, 1.10] | 1.0 | vane chord 安全缩放 | resolve_config clamp |
| vane_thickness_scale | float | [0.90, 1.15] | 1.0 | vane 厚度安全缩放 | resolve_config clamp |
| frame_thickness_scale | float | [0.90, 1.15] | 1.0 | frame rail 厚度安全缩放 | resolve_config clamp |
| pivot_clearance_scale | float | [0.95, 1.15] | 1.0 | pivot 周围 clearance（避免 vane 与 frame 干涉） | resolve_config clamp |
| material_style | enum | painted_sheet / brushed_aluminum / industrial_galvanized / matte_black_louver / warm_anodized | sampled | 调色板 | 全样本 |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette 与 module-local variant；未实现拓扑（tie-rod linkage / motor drive / asymmetric vane multiplicity / non-parallel pivot axes）不进 enum。

## Multiplicity / Copy Logic

本类别核心是模板级 multiplicity（每片 vane 都是独立 part + 独立 REVOLUTE joint）：

**(1) vane_count（核心模板级 multiplicity）**
- count_param：`vane_count`
- N_range：{3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
- sampling domain：deterministic procedural sampler 选 N ∈ 上述 10 值；weight 偏 5-7（样本中位 6）
- copied object：vane_i（每片 vane 是独立 Part；Slot B vane_shape + Slot C pivot_endcap 同形 helper 复用）
- naming：`vane_0` .. `vane_{N-1}`；joint `frame_to_vane_0` .. `frame_to_vane_{N-1}`（或 `frame_to_slat_i` / `frame_to_blade_i` 等同义命名，初版统一 `frame_to_vane_i`）
- placement：frame 内 vane array 方向（pivot_axis ⊥ 方向）等距分布；pitch_spacing = frame_height / (N+1)，pivot origin 沿 frame 内壁中线
- joint policy：每 vane 一个 REVOLUTE，parent=frame，child=vane_i，axis=(1,0,0)（或 (0,0,1) for top_support），range=[`vane_tilt_lower`, `vane_tilt_upper`]
- source/gating：rec_…_5c0752 N=5 / rec_…_6bb2d N=11 / rec_…_3dc4 N=8 / rec_…_339f N=7

**(2) frame_internal copies（module-local，固定，不暴露）**
- rectangular_perimeter_frame：4 条 rail 固定；side_rail_pair：2 条 side_rail 固定；fork_backed_rail：fork cheek 数对应 N（每 vane 两侧 cheek）
- 不作为 template-level multiplicity 暴露

**(3) pivot_landing copies（per-vane × per-end，固定 2）**
- 每 vane 在 frame 两端各 1 个 pivot_landing（boss / hole / pad）；total = 2 × N
- 对 top_support_rail：每 vane 仅 1 个顶部 landing（top end）
- 不作为 template-level multiplicity 暴露

**(4) frame static decorations（fasteners、stop_tabs、feet）**
- module-local 随 frame_support 内部固定数量；不暴露独立 count

## 拓扑多样性审计

总组合数（合法化前）：A(6) × B(4) × C(4) × N(10) × pivot_axis(派生) = 960。compatibility matrix 裁剪后估算合法组合：

- 5 horizontal frame × 4 vane_shape × 4 pivot_endcap × N(10) ≈ 5 × 4 × 4 × 10 = 800
- top_support_rail × 4 vane_shape × 3 pivot_endcap（no end_lugs）× N(10) ≈ 1 × 4 × 3 × 10 = 120
- rear_backplate gating（no single_thru_shaft）扣除 ≈ -40
- 合计合法组合 **≈ 880**，再叠加 vane_rest_pitch / asymmetric tilt range / palette / frame dims → 远超门槛。

理由：仅 A(6) × B(4) × C(4) 已 96 个 distinct enum 组合，再乘以 vane_count（10 个值）→ ≥800 合法 distinct slot_choice tuple。1000-seed 内必采到 ≥150 distinct。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed deterministic procedural sampling —— rng 先选 frame_support → 受 compatibility matrix gate 选 vane_shape / pivot_endcap → 选 vane_count（weighted 偏 5-7）→ 派生 pivot_axis（top_support→z，其他→x）→ 采样 vane_tilt_lower/upper / vane_rest_pitch / 连续 scale / palette。`seed=0` 不特殊。所有非法组合由 compatibility matrix + `resolve_config` clamp 拦截。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 A×B×C×N 家族至少 1 例。重点：

- pivot origin 落 frame inner face 与 vane chord 中线交点；不在空中
- N 个 vane 在 frame 内等距分布，相邻 vane 在 rest pose 不互穿
- vane chord × thickness 不超 frame inner clearance
- closed-pose（rest_pitch）下 vane 不超 frame envelope
- top_support 变体下 vane 从 top_rail 垂挂，pivot axis 竖直，vane 不穿地（vane bottom > floor）
- rear_backplate 变体下 vane 与 backplate 之间有 chord clearance（vane rotate full range 不撞 backplate）
- fork_backed 变体下 fork cheek 抱住 pivot endcap，captured-pin overlap 必须 element-scoped 声明
- pivot_endcap × vane_shape 几何对齐（airfoil + single_thru_shaft 沿 chord centerline；flat_box + two_end_stub_pins 各端中点）

Topology target：1000-seed slot choice tuple distinct 建议 ≥150；本类别合法组合 ≥880，预期可达。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
regression overrides：初版默认 none；若 sweep 暴露特定组合失败（如 thickened_blade + two_end_stub_pins + N=12 vane 过密相撞）再以稀疏、显式 + 失败回归理由加入，不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入 `frame_width [0.24, 0.62]`、`frame_height [0.18, 0.55]`、`frame_depth [0.018, 0.080]`、`vane_chord [0.030, 0.090]`、`vane_thickness [0.004, 0.018]`、`vane_pitch_spacing [0.025, 0.085]`、`pivot_pin_radius [0.0035, 0.0085]`、`vane_tilt_lower / vane_tilt_upper`、`vane_rest_pitch [-0.35, 0.50]`、`vane_chord_scale / vane_thickness_scale / frame_thickness_scale / pivot_clearance_scale`。全部在 `resolve_config` clamp / 派生，受 frame envelope / vane pitch spacing / pivot landing 几何 / closed-pose envelope 约束；不改变 frame_support / vane_shape / pivot_endcap / vane_count 等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A→B→C→N 顺序选择 + 每步 compatibility gate；weighted（rectangular_perimeter 高、side_rail_pair 中、rear_backplate/fork/top_support 中-低；vane_shape 平均；pivot_endcap 平均） | slot_choices_for_seed matches build choices |
| compatibility matrix | top_support↔pivot_axis=z；top_support↔!end_lugs；rear_backplate↔!single_thru_shaft；airfoil/sheet_metal↔preferred thru_shaft/hidden_bosses（soft）；vane_count 全 A/B/C 兼容 | no floating（vane 不漂浮）、collision（相邻 vane 不互穿、vane 不撞 frame）、axis（pivot 水平 x 或 under-slung 竖直 z）、max multiplicity（N≤12）、closed pose（rest_pitch 不超 frame envelope）、optional gating（top_support 限 endcap） |
| controlled local variation | frame_width / frame_height / frame_depth / vane_chord / vane_thickness / vane_pitch_spacing / pivot_pin_radius / vane_tilt_range / vane_rest_pitch / 各 scale，全 clamp | 比例变化不破坏 pivot 捕获、frame inner clearance、相邻 vane spacing、rest pose envelope、joint origin、类别 identity |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/captured-pin/axis/closed pose） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_support | 6 | yes | yes | rectangular / side_rail_pair / side_wall_housing / rear_backplate / fork_backed / top_support |
| B vane_shape | 4 | yes | yes | flat_box / thickened_blade / lathe_airfoil / sheet_metal |
| C pivot_endcap | 4 | yes | yes | two_stub_pins / single_thru_shaft / end_lugs / hidden_bosses |
| N vane_count | 10 | yes | yes | {3..12}，模板级 multiplicity |

兼容矩阵（合法 / 互斥 / fallback）：

- `top_support_rail` ⇒ pivot axis = (0,0,1)（必须）；其他 frame ⇒ pivot axis = (1,0,0)。
- `top_support_rail` ⇒ pivot_endcap ∈ {two_end_stub_pins, single_thru_shaft, hidden_endcap_bosses}（end_lugs 需双侧 frame landing，互斥）。
- `rear_backplate_frame` ⇒ pivot_endcap ∈ {two_end_stub_pins, end_lugs_with_separate_shaft, hidden_endcap_bosses}（single_thru_shaft 不能穿透 back panel）。
- `fork_backed_rail` ⇒ pivot_endcap ∈ {two_end_stub_pins, single_thru_shaft, end_lugs_with_separate_shaft}（fork cheek 抱 pin / shaft / lug；hidden_bosses 与 fork lug 视觉冲突，降级权重低）。
- 其他 frame 兼容所有 pivot_endcap。
- vane_count 受 frame_height / vane_pitch_spacing clearance 约束：N × vane_pitch_spacing ≤ frame_height × 0.92，否则 clamp N 或 clamp vane_pitch_spacing。
- vane_shape × pivot_endcap soft preferences（不强制 gating，由 module factory 调整 endcap 位置 / 视觉调和）：airfoil ↔ thru_shaft / hidden_bosses；sheet_metal ↔ stub_pins / end_lugs；flat_box ↔ 任意；thickened_blade ↔ end_lugs / hidden_bosses。
- vane_tilt range 受 vane_chord 与 vane_pitch_spacing 派生：tilt 全 range 时 vane 转角不撞相邻 vane。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C 三元组 + vane_count + pivot_axis 派生 + vane_rest_pitch / tilt range / palette 可选）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（top_support↔z 轴 & !end_lugs；rear_backplate↔!single_thru_shaft；fork_backed↔preferred pin/shaft/lug；vane_count × pitch_spacing ≤ frame_height clearance）
- optional regression overrides are sparse and justified（初版 none）
- controlled local scale params (frame_width/height/depth, vane_chord/thickness/pitch_spacing, pivot_pin_radius, tilt range, rest_pitch, 各 scale) clamped；不破坏 pivot 捕获、frame inner clearance、相邻 vane spacing、rest pose envelope、joint origin、类别 identity
- critical InterfaceSpec / MatingContract points exist：frame 内壁 pivot_landing ↔ vane 端 pivot_endcap（captured pin / shaft，element-scoped allow_overlap）；frame 4-rail（perimeter）/ 2-rail（side_rail_pair）/ flange / fork cheek / backplate 等结构件互相支撑；vane 全 part 必须 frame-captured（无悬空）
- key joints have expected type/axis/range：每个 `frame_to_vane_i` REVOLUTE axis = (1,0,0) 主，top_support 时 (0,0,1)；range 全 vane 一致（共 vane_tilt_lower/upper）；origin 落 frame inner face 与 vane chord 中线交点
- vane geometry：每个 vane 含 vane_shape 主体 + pivot_endcap 端结构；primitive 不得从 cadquery / mesh / lathe 降级成 single Box+Cylinder（airfoil / sheet_metal / thickened_blade 必须保留对应 helper）
- multiplicity：N 个 vane 等距排列、命名 `vane_0..N-1`、joint 命名 `frame_to_vane_0..N-1` 严格对齐
- closed pose：rest_pitch 下 N 个 vane 不互穿、不超 frame envelope（rect/side/wall/backplate/fork/top）
- pivot origin 落 frame inner face 与 vane chord 中线交点，不在空中（参 [[project_sweep_only_rest_pose]]）

## Reject cases

- N=0 或 N=1（不构成 array；spec 必须 N≥3）。
- vane 与 frame 之间无 pivot 关节（变成静态 visual 装饰）。
- tie-rod 联动 / gear coupling / motor drive 使 vane 不再 independent（违反 identity）。
- pivot axis 不一致（部分 vane x、部分 z）或不水平 / 不竖直（轴向错误）。
- vane 漂浮于 frame 外（pivot 未捕获）。
- 相邻 vane 在 rest pose 互穿、或 closed pose 全开 vane 撞 frame envelope。
- N 个 vane 沿 frame 排列方向重叠 / 等距错位。
- frame 退化成 single Box / 无 inner face landing → 失去 frame identity。
- vane_shape 退化成简单 Box 而 spec 指定 airfoil / sheet_metal / thickened_blade（违反 primitive 保真，[[feedback_mesh_profile_origin_pitfall]]）。
- top_support_rail 变体下 vane 不垂挂、pivot 轴不竖直，或 vane 穿地。
- rear_backplate 变体下 vane 旋转撞 backplate（封闭 envelope）。
- fork_backed 变体下 pin 脱出 fork cheek（不 captured）。
- pivot endcap 与 vane_shape 几何不对齐（airfoil chord 偏离 thru_shaft 中线 / end_lugs 不在 vane 端）。
- 拿 multiplicity 件（fasteners / stop_tabs / feet 数量）当成 slot 拓扑差异（[[feedback_multiplicity_includes_jointless]]）。
- 仅 rest pose 验 vane → 改 tilt range 必须 pose 到 upper / lower 实测 AABB（[[project_sweep_only_rest_pose]]）。
- 包形外壳把 vane 完全藏起（违反 vane 可见 identity，[[feedback_enclosed_mechanism_open_front]]）。

## 与相邻类别的边界

- 不该混入：`louvered_shutter_assembly` —— 那是 **联动百叶**（tie-rod 串联，N 个 vane 同步动），本类别是 **独立 pivot**（无联动）。
- 不该混入：`box_fan_with_control_knob` / `ceiling_fan` —— 是 **旋转风扇**（rotor + blade radial 周向旋转），不是 vane array louver 平行排列轴向旋转。
- 不该混入：`vent_grille` / `perforated_panel`（静态格栅）—— 无 pivot articulation，vane 不动。
- 不该混入：`turnstile_gates` / `revolving_door` —— vane 数量少（3-4 片）且共享 hub 中心轴 radial 旋转，本类别是 N 个 parallel 独立轴。
- 不该混入：`graphics_card_with_cooling_fans` —— rotor blade 不是 louver vane。
- 不该混入：`barrier_gate_leaf_gate` —— 单 vane（leaf）门，不是 N 片 array。
- 不该混入：`sliding_window` / `dishwasher_with_sliding_racks` —— prismatic 滑动 vs revolute 翻转，运动语义不同。
- 不该混入：`paper_cutter_guillotine` —— 单刃片切割，无 array。
- 不该混入：`gear_assemblies` / `branching_tree_*` —— 不是结构性 array。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | A | rectangular_perimeter_frame | rec_vane_array_with_independent_pivots_5c0752059fc0423fbee48adeba6edd01 | L51-L80 | 4-bar perimeter frame + pivot_boss landing |
| S-A2 | A | side_rail_pair | rec_vane_array_with_independent_pivots_0001 | L35-L53 | 仅左右 2 rail + bearing_pad |
| S-A3 | A | side_wall_housing | rec_vane_array_with_independent_pivots_35e8b0abd3b24946ad156748f6cb3d41 | L71-L143 | perimeter + 前后 flange + SUPPORT_PAD |
| S-A4 | A | rear_backplate_frame | rec_vane_array_with_independent_pivots_0ff0a1e556e1411b9ba770d781cbbb48 | L60-L116 | 背板 + 4 边 rail + pivot_pad |
| S-A5 | A | fork_backed_rail | rec_vane_array_with_independent_pivots_b9e39931875040e4b52f585a88e0b901 | L75-L142 | perimeter + 后置 fork bridges + bushing |
| S-A6 | A | top_support_rail | rec_vane_array_with_independent_pivots_81ee50c95f4e4dd18ad348594bf5e6a2 | L60-L84 | 仅 1 条 top_rail，vane 垂挂 z 轴 |
| S-B1 | B | flat_rectangular_box | rec_vane_array_with_independent_pivots_5c0752059fc0423fbee48adeba6edd01 | L109-L114 | 单 Box vane body |
| S-B2 | B | thickened_blade_with_chamfer | rec_vane_array_with_independent_pivots_46de95e7b856425b997422d4e45e27a7 | L28-L64 | cambered MeshGeometry + chamfer |
| S-B3 | B | lathe_or_lofted_airfoil | rec_vane_array_with_independent_pivots_0001 | L63-L88 | cadquery threePointArc 对称 airfoil |
| S-B4 | B | sheet_metal_thin | rec_vane_array_with_independent_pivots_e798b5780b4b4ad1a1a5092e9a5b4db2 | L74-L113 | 薄 mesh / ellipse + rolled lip |
| S-C1 | C | two_end_stub_pins | rec_vane_array_with_independent_pivots_0001 | L80-L88 | 两端 2 Cylinder stub_pin |
| S-C2 | C | single_thru_shaft | rec_vane_array_with_independent_pivots_0002 | L64-L80 | 单根 Cylinder 贯穿 vane |
| S-C3 | C | end_lugs_with_separate_shaft | rec_vane_array_with_independent_pivots_a7c7ef5f1c1e4ba59e1a8123ff3ee74c | L93-L104 | collar + journal + 独立 axle |
| S-C4 | C | hidden_endcap_bosses | rec_vane_array_with_independent_pivots_e798b5780b4b4ad1a1a5092e9a5b4db2 | L219-L234 | vane 端内嵌 Cylinder boss + frame bearing_sleeve |

## 模板实现备注（可选）

- 共享 helper：`_vane_shape(style, r)` 4-branch primitive 分支不可降级；`_pivot_endcap(style, r)` 4-branch；`_frame_support(style, r)` 6-branch；`_vane_pitch_axis(r) -> List[Vec3]` 沿 frame_height 等距 N 个 pivot origin；`_vane_factory(i, shape, endcap, r)` 同形复用。
- 重点 InterfaceSpec / MatingContract：frame 内壁 pivot_landing↔vane 端 pivot_endcap captured pin（element-scoped allow_overlap，参 rec_…_0001 frame_to_vane / rec_…_b9e3 bushing↔pin / rec_…_e798 sleeve↔boss）；frame 内 rail 互相支撑接触；vane 端 endcap 必须落 frame 内 inner face / fork cheek / sleeve socket 内。
- captured-pin overlap：vane stub_pin / thru_shaft / collar / journal / hidden_boss 嵌入 frame inner boss / drilled hole / bushing / sleeve / fork cheek 处，需 element-scoped `allow_overlap`，仅对真实意图穿插声明；rect/side/wall/backplate/fork/top 各 frame 类型的 pivot_landing 元素名要在 allow list 全覆盖。
- 暂不进入 seed domain（待审核或后续启用）：tie-rod 联动 variant（rec 中实际无 5 星样本含联动；联动属于 louvered_shutter_assembly 类别）；motor drive；asymmetric vane multiplicity（不同 vane 不同 shape）；非 parallel pivot axes（部分 x / 部分 z 混合）。
- N=12 高密度 vane 数量上限：当 N=12 时 frame_height 必须 ≥ 0.32m 且 vane_pitch_spacing clamp 到 ≤ frame_height / 13；否则降到 N=11 或 N=10。
- rest_pitch 默认为 0（vane 闭合朝外），但样本中 ~30% 含 non-zero rest_pitch (-0.35 to 0.48)；采样时 rest_pitch ∈ [-0.35, 0.50] uniform，clamp 后小于 vane_tilt_lower/upper 中心绝对值。
- vane_shape × pivot_endcap soft preferences 通过 module factory 内部 endcap 位置 / 大小微调实现，不需要硬性 gating。
- closed-pose（pose=rest_pitch 而非 pose=0）下检查相邻 vane / vane vs frame 不互穿；sweep 仅 rest pose 风险（[[project_sweep_only_rest_pose]]）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全 42 个 5 星样本（rec_vane_array_with_independent_pivots_*）逐文件读取 model.py / revision.json / record.json / prompt / category metadata，分 4 批并行 Explore；candidate module 与 N multiplicity 都锚定 `model.py:Lx-Ly`。结构家族：6 frame × 4 vane_shape × 4 pivot_endcap × N {3..12}，纯 multiplicity 模式（无 auxiliary slot），合法组合 ≥800。等待人工审核。 |
