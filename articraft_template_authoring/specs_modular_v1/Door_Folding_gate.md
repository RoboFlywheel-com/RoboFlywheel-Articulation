# folding_gate — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_gate` |
| template path | `agent/templates/Door_Folding_gate.py` |
| test path (optional) | `tests/agent/test_folding_gate_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: lattice_pattern + kinematics + endpost_lock + guide_track；外加 1 根 multiplicity 轴 N = 折叠 cell 数 / picket 数） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (1 parent + 6 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读结论（全部 7 个 5★ 样本 `model.py` 已逐行读取）：

- **rec_door_folding_gate（parent / 基线）** L575：固定矩形钢框 `frame`（`stile_a`/`stile_b`/`head_rail`/`sill_rail`/`top_track`/`bottom_track`/`latch_plate`/`latch_knob`，L137-193）作为 root。10 个剪式 cell 的折叠格栅由单一 `fold` REVOLUTE 主驱动（L270-274），其余全部 mimic 耦合：每 cell 一条 1:-2:1 lambda 链（`lam_up_{c}` → `lam_elbow_{c}`(-2q) → `lam_dn_{c}`，L259-330），保证 picket 在任意折叠角始终竖直且水平（pitch 按 `2*S_HALF*cos(THETA0+q)` 精确收缩）。4 band × 2 row 装饰菱形 strap（`asc_{c}_{ri}`/`desc_{c}_{ri}` 各绕自己的 picket rivet ±1 mimic 摆动，L335-417）。共享 helper `lam_bar()`（L249-257）发射 lambda 半杆。`q=0` = 完全展开 hero pose，正向折叠收向左 stile。
- **rec_folding_gate_var_picket_pantograph** L585：去掉菱形装饰 strap，每 cell 改为裸两杆 pantograph X（4 row `xup_{c}_{ri}`/`xdn_{c}_{ri}`，全长交叉 bar，L348-424）；驱动行仍是同一条 lambda 链 + 共享 helper `_lambda_bar()`(L238-250) 与 `_crossed_bar()`(L252-274)。运动学（fold + lambda 1:-2:1）与 parent 完全相同 → 仅 Slot A 拓扑不同。
- **rec_folding_gate_var_accordion_panels** L435：整片实心 Box leaf 取代菱形 mesh（`panel_{i}`，helper `_add_panel_visuals()` L85-141），且把线性剪式伸缩换成沿竖轴 `(0,0,1)` 的 piano-hinge zigzag：单 `fold` 驱动（L242-253）+ `hinge_{i}` 交替 ±2 mimic（L263-280）。**这是一格双覆盖样本：同时承载 Slot A=solid_panels 与 Slot B=accordion_hinge**（见兼容矩阵）。
- **rec_folding_gate_var_dropbolt_post** L796：在 parent 基础上加前导高 `end_post`（绕 clip 固定到 last picket，L460-493）+ 竖向 `drop_bolt` PRISMATIC `bolt_slide`（沿 z 落入 frame 上的 `floor_socket`，L496-532；socket L194-207）。仅 Slot C 不同（lattice/kinematics/track 与 parent 相同）。
- **rec_folding_gate_var_top_track_only** L594：frame 只发射 `head_rail` + `top_track`（L156-169），去掉 `sill_rail`/`bottom_track`；`OPEN_Z0=0.0`(L66)、`PICKET_Z0=0.025`(L97) → ceiling-hung 吊挂、picket 离地悬空。仅 Slot D 不同。
- **rec_folding_gate_var_ncells5** L575 / **rec_folding_gate_var_ncells16** L575：纯 multiplicity 变体。ncells5 仅改 `N_CELLS=10→5`(L66) + 放宽两条 span 断言阈值；ncells16 改 `N_CELLS=10→16`(L66) + `FRAME_W=1.20→1.86`(L52) 加宽框 + 改 frame 尺寸断言。两者证明 multiplicity 轴只需改 `N_CELLS` 常量即由现有 `for c in range(N_CELLS)` / `for i in range(N_VERTS)` loop 重新发射。

## 核心身份

folding_gate = **伸缩 / 手风琴折叠安全门（concertina / accordion trellis security gate，又称剪式 scissor gate）**。物理含义：一面固定矩形钢框（root，落地或吊挂）跨在门洞上，框内携带一条可整体展开 / 收拢的折叠格栅或折叠 leaf 列；整门由**单一驱动关节**带动，其余关节全部 mimic 耦合，像手风琴一样沿门洞水平方向伸缩，收拢时叠成一摞贴向一侧立柱。

默认成熟域：

- root = 固定矩形钢框（两 stile + head/sill rail + guide track + 可选 latch / lock）。
- 折叠机构 = N 个同构 cell / panel 的链，**单驱动 + 全 mimic**（剪式 1:-2:1 lambda 链，或 piano-hinge 交替 ±2）。
- `q=0` = 完全展开 hero pose（跨满门洞），正向 q 折叠收向左 stile。
- 颜色 / 材质（terracotta-salmon、镀锌、黑铁等）只是叠加在结构之上的 palette，不构成结构轴。

不该混入的相邻类别见第 11 节。

## 槽位 + 候选模块表

### Slot A：lattice_pattern（格栅 cell 填充样式 —— 视觉/拓扑槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_diamond（基线） | rec_door_folding_gate | helper `lam_bar` L249-257；strap loop L335-417（`asc_{c}_{ri}` L338-344 / `desc_{c}_{ri}` L367-373 / `cross_rivet` L347-353 / pivot joints L354-385） | eligible if compatible | 每 cell 4 band×2 row 交叉 strap，banded 菱形 trellis；asc 走前面 desc 走后面，各绕自己 picket rivet ±1 mimic 摆动 |
| bare_pantograph | rec_folding_gate_var_picket_pantograph | helper `_crossed_bar` L252-274；non-drive crossed-bar loop L348-424（`xup_{c}_{ri}` L356-369 / `xdn_{c}_{ri}` L372-385） | eligible if compatible | 去掉菱形装饰，每 cell 4 row 仅裸两杆 pantograph X（全长交叉 bar），无 band/无 diamond infill |
| solid_panels | rec_folding_gate_var_accordion_panels | helper `_add_panel_visuals` L85-141（`leaf` Box L104-109）；panel loop L221-229 | eligible if compatible（**与 Slot B 联动 —— 见兼容矩阵**） | 每 cell 一块整片实心 Box leaf（+ top/bottom edge rail），隐私折叠，取代菱形 mesh；无 scissor strap/lambda 链 |

> 三候选结构互异（diamond strap mesh ↔ bare X bar ↔ solid leaf），均有 5★ 来源，满足 ≥3。

### Slot B：kinematics（折叠运动学 —— 主机构槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| linear_concertina（基线） | rec_door_folding_gate | `fold` REVOLUTE L270-274；lambda 链 L259-330（`lam_elbow_{c}` -2q L291-300 / `lam_dn_{c}_to_picket_{c+1}` L302-311）；FIXED frame→picket_0 L230-236 | eligible if compatible | 剪式 pantograph 沿轨道线性伸缩；1:-2:1 lambda mimic 链使 picket 始终竖直水平，pitch=`2*S_HALF*cos(THETA0+q)` |
| accordion_hinge | rec_folding_gate_var_accordion_panels | `fold` REVOLUTE 竖轴 L242-253；交替 ±2 mimic `hinge_{i}` loop L263-280；FIXED frame→panel_0 L232-238 | eligible if compatible（**与 Slot A=solid_panels 联动**） | 刚性 leaf 沿竖轴 `(0,0,1)` piano-hinge zigzag 折叠成平叠；单驱动 + 交替 ±2 multiplier mimic，绝对角在 +q/-q 间交替 |

> 两候选拓扑根本不同（serial 剪式 X-链 + lambda elbow ↔ 直接 panel↔panel piano-hinge zigzag，轴向也不同：lambda 绕 ±Y vs hinge 绕 +Z）。样本池只产出这两种合法主机构家族，故 Slot B 取 2 候选；满足 ≥2，无需降级（每候选均有真实 5★ 源 + 清晰 articulation 语义）。

### Slot C：endpost_lock（端柱 / 锁定样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| mid_latch_knob（基线） | rec_door_folding_gate | `latch_plate` L179-184 + `latch_knob` L185-193（frame 上静态 parent visual） | eligible if compatible | 右 stile 中部静态 keeper plate + 凸起 catch knob；无活动件，纯 frame visual |
| drop_bolt | rec_folding_gate_var_dropbolt_post | `end_post` L460-493（post_body L462-467 / clip_{ci} L469-481 / FIXED→last picket L483-493）；`drop_bolt` + `bolt_slide` PRISMATIC L496-532；`floor_socket` L194-207 | eligible if compatible | 前导高 end-post（FIXED 到 last picket）+ 竖向 drop-bolt PRISMATIC 沿 z 落入 frame 地面 socket 锁定；含活动 PRISMATIC 子件 |

> 两候选结构互异（静态 keeper visual ↔ 活动 PRISMATIC drop-bolt + end-post + socket）。样本池只产出这两种端锁家族，取 2 候选；满足 ≥2，无需降级。

### Slot D：guide_track（导轨样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| dual_track（基线） | rec_door_folding_gate | `sill_rail` L156-161 + `top_track` L162-167 + `bottom_track` L168-173（`head_rail` L150-155 两候选共有） | eligible if compatible | 上下双导轨 + sill rail，落地式；picket 底贴近 bottom track（`PICKET_Z0=0.082`），`OPEN_Z0=RAIL_H` |
| top_track_only | rec_folding_gate_var_top_track_only | frame 仅发射 `head_rail` L156-161 + `top_track` L164-169（无 sill_rail / bottom_track）；`OPEN_Z0=0.0` L66；`PICKET_Z0=0.025` L97 | eligible if compatible | 去 sill rail + 地轨，顶轨吊挂 ceiling-hung，picket 离地悬空到楼板 |

> 两候选结构互异（落地双轨 + sill ↔ 吊挂单顶轨、改 `OPEN_Z0`/`PICKET_Z0`），均有 5★ 源；取 2 候选，满足 ≥2，无需降级。

## 槽位图（slot graph）

pattern: **mixed** — 固定 named slots（A/B/C/D）+ 1 根 multiplicity 轴（E: cell_count N）。

```
                            [frame] (root, FIXED ground @ z=0)
                              |  Slot D 决定 frame 发射哪些 track/rail
                              |  Slot C 决定 frame 上是否加 floor_socket（drop_bolt）
                              |
            FIXED frame_to_picket_0 @ (LEAD_X,0,LOAD_Z)   [linear_concertina]
              或 FIXED frame_to_panel_0 @ (LEAD_X,0,PANEL_CZ) [accordion_hinge]
                              |
                              v
        ┌──────── Slot B kinematics（驱动 spine，决定 cell↔cell 关节家族）────────┐
        │ linear_concertina:                                                     │
        │   picket_c --REV fold/lam_up_pivot(+q, axis -Y)--> lam_up_c            │
        │     --REV lam_elbow_c(-2q, axis +Y)--> lam_dn_c                        │
        │     --REV lam_dn->picket(+q, axis -Y)--> picket_{c+1}   (1:-2:1 mimic) │
        │   Slot A 装饰挂在 picket_c 上（asc/desc 或 xup/xdn，±1 mimic to fold） │
        │ accordion_hinge:                                                       │
        │   panel_c --REV fold/hinge_c(±2q, axis +Z)--> panel_{c+1}             │
        │   （Slot A 必为 solid_panels：leaf 即 panel 本体，无独立装饰子件）     │
        └──────────────────────────────────────────────────────────────────────┘
                              |
                              v
        Slot C endpost_lock 挂在 trailing 端：
          mid_latch_knob → frame 上静态 plate+knob（不接 spine）
          drop_bolt → end_post FIXED→last picket，drop_bolt PRISMATIC bolt_slide(axis +Z)
                       落入 frame.floor_socket
```

接口点位说明：

- **frame → spine 首件**：FIXED joint，origin `(LEAD_X, 0, LOAD_Z)`（concertina）或 `(LEAD_X, 0, PANEL_CZ)`（accordion）。leading picket/panel 含 `mount_bracket` 嵌入左 stile（contact plane = stile 内侧面）。
- **cell↔cell（Slot B）**：concertina 用 REVOLUTE pivot 链，pivot 点在 picket 局部原点（=LOAD_Z 高度的 rivet）；elbow pivot 在 `(S_HALF,0,0)` bar 交叉处；axis ±Y。accordion 用 REVOLUTE 在 `(PANEL_W,0,0)` panel 右缘，axis +Z。
- **Slot A 装饰 → picket**：每根 strap/bar 绕 picket 上自己的 rivet（origin `(0, Y_FRONT/Y_BACK, z_bot/z_top - LOAD_Z)`）REVOLUTE，±1 mimic to `fold`。
- **Slot C → spine**：drop_bolt 的 end_post FIXED 到 last picket（origin `(PICKET_CX*0.5+END_POST_CX*0.5,0,0)`），drop_bolt PRISMATIC `bolt_slide`（axis +Z）落入 frame.floor_socket（socket 在 frame，contact = bolt tip seats in socket recess）。mid_latch_knob 不接 spine，纯 frame visual。
- **Slot D**：只改 frame 发射哪些 track/rail visual + `OPEN_Z0` / `PICKET_Z0`，不引入新 joint。

互斥 / 派生 / 可选：

- **Slot A=solid_panels ⟺ Slot B=accordion_hinge**（强绑定，见兼容矩阵）：solid_panels 的 panel 既是装饰也是运动件，只能用 accordion piano-hinge spine；反之 accordion_hinge spine 没有独立 picket 链可挂菱形/裸杆，只能用 solid_panels。
- **Slot A∈{single_diamond, bare_pantograph} ⟺ Slot B=linear_concertina**：菱形 strap 与裸杆 X 都挂在 picket 上、随 lambda 链 ±1 mimic，只能用剪式 spine。
- Slot C / Slot D 与 Slot A/B 选择正交（可任意组合），但 drop_bolt 在 accordion spine 下需 FIXED 到 last panel 而非 last picket（实现时按 spine 解析 trailing link 名）。
- 单 fold REVOLUTE 永远是唯一显式驱动；其余关节 100% mimic 耦合（hard invariant）。

## 每槽位 Module Emits / Interfaces

### Slot A / module single_diamond
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 cell × 每 band-row：`asc_{c}_{ri}`（front 面斜杆 + cross_rivet）、`desc_{c}_{ri}`（back 面斜杆） | rec_door_folding_gate / L338-373 |
| internal joints | `asc_{c}_{ri}_pivot`(REV, axis -Y, +1 mimic)、`desc_{c}_{ri}_pivot`(REV, axis +Y, +1 mimic) | L354-385 |
| upstream interface | 每 strap 绕 picket_c 上自己 rivet（origin `(0, ±Y_FRONT, z_bot/z_top-LOAD_Z)`） | L359-364 / L379-384 |
| downstream interface | far end lap 到 picket_{c+1} 面（slotted-rivet 滑移，allow_overlap） | L387-417 |

### Slot A / module bare_pantograph
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 cell × 每非驱动 row：`xup_{c}_{ri}`（+ cross_rivet）、`xdn_{c}_{ri}` 全长交叉 bar | rec_folding_gate_var_picket_pantograph / L356-385 |
| internal joints | `xup_{c}_{ri}_pivot`(REV, axis -Y, +1 mimic)、`xdn_{c}_{ri}_pivot`(REV, axis +Y, +1 mimic) | L357-385 |
| upstream interface | 绕 picket_c rivet（origin `(0,0,z_bot/z_top-LOAD_Z)`） | L362-365 / L378-381 |
| downstream interface | far end slide past picket_{c+1}（allow_overlap） | L401-410 |

### Slot A+B / module solid_panels + accordion_hinge（联动）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_{i}`：`leaf`(Box) + `top_rail` + `bottom_rail` + `hinge_barrel`（除末件）+ 首件 `mount_bracket` | rec_folding_gate_var_accordion_panels / L104-141 |
| internal joints | `fold`(REV +Z, drive, panel_0→panel_1) + `hinge_{i}`(REV +Z, 交替 ±2 mimic) | L242-280 |
| upstream interface | FIXED frame→panel_0 @ `(LEAD_X,0,PANEL_CZ)`；mount_bracket 嵌左 stile | L232-238 / L132-141 |
| downstream interface | hinge_barrel 在 `(PANEL_W,0,0)` 接 panel_{i+1}；trailing panel = Slot C 挂点 | L124-131 / L263-280 |

### Slot B / module linear_concertina
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 cell `lam_up_{c}` / `lam_dn_{c}`（+ elbow_rivet）；`picket_{i}`（picket_bar + rivets + 首件 mount_bracket） | rec_door_folding_gate / L249-330, L199-228 |
| internal joints | `fold`(REV -Y, drive) / `lam_up_{c}_pivot`(+1) / `lam_elbow_{c}`(REV +Y, -2 mimic) / `lam_dn_{c}_to_picket_{c+1}`(+1) | L270-311 |
| upstream interface | FIXED frame→picket_0 @ `(LEAD_X,0,LOAD_Z)` | L230-236 |
| downstream interface | picket_{c+1} 局部原点（=LOAD_Z rivet）继续接下一 cell；last picket = Slot C 挂点 | L302-311 |

### Slot C / module mid_latch_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame visual `latch_plate`(Box) + `latch_knob`(Cylinder) | rec_door_folding_gate / L179-193 |
| internal joints | 无（静态 parent visual） | — |
| upstream interface | 挂在 frame 右 stile 中部 `(FRAME_W-STILE_W*0.5, 0, latch_z=1.0)` | L177-184 |
| downstream interface | 无（keeper，与折叠门接触为目检视觉） | — |

### Slot C / module drop_bolt
| emits | 描述 | 来源 |
|---|---|---|
| parts | `end_post`(post_body + clip_{0,1}) + `drop_bolt`(bolt_rod + bolt_handle + bolt_tip) + frame `floor_socket` + `floor_socket_rim` | rec_folding_gate_var_dropbolt_post / L460-517, L194-207 |
| internal joints | FIXED picket_last→end_post；`bolt_slide`(PRISMATIC +Z, lower=0 seated, upper=BOLT_RETRACT) | L483-532 |
| upstream interface | end_post FIXED 到 trailing link（last picket/panel）@ `(PICKET_CX*0.5+END_POST_CX*0.5,0,0)` | L485-493 |
| downstream interface | drop_bolt tip seats into frame.floor_socket（allow_overlap drop_bolt↔frame） | L519-532, L774-791 |

### Slot D / module dual_track
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame visual `sill_rail` + `top_track` + `bottom_track`（+ 共有 `head_rail`） | rec_door_folding_gate / L156-173 |
| internal joints | 无 | — |
| upstream interface | 全部挂 frame；`OPEN_Z0=RAIL_H`、`PICKET_Z0=0.082`（落地） | L58-61, L91 |
| downstream interface | 上下轨为 picket 顶 / 底滑移导引（视觉 + 高度约束） | L498-503 |

### Slot D / module top_track_only
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame 仅 `head_rail` + `top_track`（无 sill_rail / bottom_track） | rec_folding_gate_var_top_track_only / L156-169 |
| internal joints | 无 | — |
| upstream interface | `OPEN_Z0=0.0`、`PICKET_Z0=0.025`（ceiling-hung，离地悬空） | L66, L97 |
| downstream interface | 顶轨吊挂导引 picket 顶 | L164-169 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `lattice_pattern` | enum | single_diamond / bare_pantograph / solid_panels | — | choice | deterministic procedural sampler；solid_panels 强制 kinematics=accordion_hinge | Slot A 表 |
| `kinematics` | enum | linear_concertina / accordion_hinge | — | choice | accordion_hinge 强制 lattice_pattern=solid_panels；否则 linear_concertina | Slot B 表 |
| `endpost_lock` | enum | mid_latch_knob / drop_bolt | — | choice | drop_bolt 在 accordion spine 下 FIXED 到 last panel | Slot C 表 |
| `guide_track` | enum | dual_track / top_track_only | — | choice | top_track_only ⇒ `OPEN_Z0=0.0` & `PICKET_Z0` 抬高 | Slot D 表 |
| `palette_style` | enum | terracotta_salmon / galvanized_steel / black_iron / forest_green / powder_white | terracotta_salmon | choice | 仅改 material rgba，不改结构；见下「palette」 | parent L132-134 |
| `cell_count` (N) | int | [4, 20]（轴 E，见第 8 节加权） | 10 | choice | 加权采样小 N 偏多；clamp 到 [4,20] | rec_*_ncells5/16 L66 |
| `frame_width_scale` | float | [0.85, 1.25] | 1.0 | independent | 缩放 FRAME_W；door 高度/depth 不随之 | parent L52 / ncells16 L52 |
| `frame_height_scale` | float | [0.90, 1.15] | 1.0 | independent | 缩放 FRAME_H；OPEN_Z1 / picket 高随之派生 | parent L53 |
| `pitch_open` | float | derived | 0.105 | equation | `= clamp((FRAME_W*frame_width_scale - 2*STILE_W) / N, PITCH_CLOSED+0.01, 0.16)`；展开节距由可用洞宽 / N 派生 | parent L69 |
| `v_rise` | float | [0.035, 0.055] | 0.045 | independent | 菱形/X 半高；影响 S_HALF / THETA0 / FOLD_ANGLE | parent L73 |
| `picket_cross` | float | [0.010, 0.018] | 0.013 | independent | picket 截面宽（保形细节） | parent L89 |
| `fold_upper`(accordion) | float | [0.9, 1.25] | 1.1 | independent | accordion panel 折叠极限角（仅 accordion spine 用） | accordion_panels L77 |
| (—) | constraint | — | — | inequality | `pitch_open*0.5 > PITCH_CLOSED*0.5` 且 `pitch_open*0.5 ≤ S_HALF`，否则 `FOLD_ANGLE=acos(...)−THETA0` 无解 → 回缩 pitch_open / 重采 | parent L85-87 |
| (—) | constraint | — | — | inequality | `LEAD_X + N*pitch_open ≤ OPEN_X1`（展开格栅不得越出右 stile）；违反则回缩 pitch_open 或拒绝 | parent L194, test L484 |
| (—) | constraint | — | — | conditional | `OPEN_Z0 = 0.0 if guide_track==top_track_only else RAIL_H`；`PICKET_Z0` 随之 | top_track_only L66/L97 |

**连续尺寸采样契约**：先采 independent（frame_width_scale / frame_height_scale / v_rise / picket_cross / fold_upper）→ 按 equation 派生 pitch_open（依赖 frame_width_scale 与 N）→ 用 inequality 把 (pitch_open, S_HALF, FOLD_ANGLE 可解性、格栅不越右 stile) 投影/回缩，无法满足则拒绝重采 → 按 conditional 解析 OPEN_Z0/PICKET_Z0。所有求解在 `resolve_config` 完成。

**palette（palette_style，≥3，目标 4-6 realistic colorways）**——每个仅替换 frame/strap/leaf 与 rivet 的 material rgba，不改任何几何或拓扑：

| palette_style | 主体 (salmon→) | 暗部 (salmon_dk→) | rivet / accent | 现实依据 |
|---|---|---|---|---|
| terracotta_salmon（默认） | (0.87,0.66,0.59) | (0.73,0.52,0.46) | (0.46,0.42,0.42) | parent 参考照片 terracotta-salmon |
| galvanized_steel | (0.74,0.76,0.78) | (0.55,0.57,0.60) | (0.40,0.41,0.43) | 镀锌亮银伸缩门 |
| black_iron | (0.16,0.16,0.18) | (0.10,0.10,0.12) | (0.30,0.30,0.32) | 黑铁安全门 |
| forest_green | (0.18,0.34,0.24) | (0.12,0.24,0.17) | (0.35,0.35,0.33) | 户外深绿粉末喷涂门 |
| powder_white | (0.92,0.92,0.90) | (0.78,0.78,0.76) | (0.55,0.55,0.55) | 白色粉末喷涂室内折叠门 |

## Multiplicity / Copy Logic

本模板有 **1 根 multiplicity 轴**（cell_count N）。

- `count_param`: **`cell_count`**（实现内 `N_CELLS`；`N_VERTS = N_CELLS + 1` picket / panel 数随之；strap/lambda/xbar/panel 全部随 loop 重发射）
- `N_range`: **[4, 20]**（现实伸缩门 cell 数；测试偏小 N，产品全程）。盘上已覆盖 distinct N = {5, 10, 16}（ncells5 / parent / ncells16）。
- sampling domain（权重档，小 N 高频、大 N 稀有）：
  - N∈[4,6]: ~35%；N∈[7,10]: ~35%；N∈[11,14]: ~20%；N∈[15,20]: ~10%
  - 标称基线 N=10。大 N 不必铺样本——`pitch = 2*S_HALF*cos(THETA0+q)` 与 `for` 重发射使任意 N 几何安全构造。
- copied object: 一个 **scissor cell**（concertina：`lam_up_{c}` + `lam_dn_{c}` + 该 cell 全部 band-row `asc_{c}_{ri}`/`desc_{c}_{ri}`（single_diamond）或 `xup_{c}_{ri}`/`xdn_{c}_{ri}`（bare_pantograph））；accordion spine 下 copied object 为一块 `panel_{i}`（leaf + rails + hinge_barrel）。共享 helper：concertina 用 `lam_bar()`（parent L249-257）/ `_crossed_bar()`（pantograph L252-274）；accordion 用 `_add_panel_visuals()`（L85-141）。
- naming: concertina → `picket_{i}`(i∈[0,N])、`lam_up_{c}`/`lam_dn_{c}`/`asc_{c}_{ri}`/`desc_{c}_{ri}`/`xup_{c}_{ri}`/`xdn_{c}_{ri}`(c∈[0,N)，ri∈row index)，全部 `for c in range(N_CELLS)` / `for i in range(N_VERTS)`；accordion → `panel_{i}`/`hinge_{i}`。
- placement: 沿 X 等距——展开 PITCH_OPEN（concertina）/ PANEL_W（accordion）；折叠按 `2*S_HALF*cos(THETA0+q)`（concertina）或 `PANEL_W*cos(fold)`（accordion）规则收缩。joint origin 规则放置（每 cell `(S_HALF,0,0)` / 每 panel `(PANEL_W,0,0)`）。
- joint policy: **单 fold REVOLUTE 主驱动 + 全 mimic**。concertina：1:-2:1 lambda（`lam_up`+1、`lam_elbow`-2、`lam_dn`+1）+ 装饰 strap ±1。accordion：`hinge_{i}` 交替 ±2 multiplier。整门一动。
- source/gating: ncells5/ncells16 已证只改 `N_CELLS` 即由现有 loop 重发射；sweep 对 N 单独设上限 20。

## 拓扑多样性审计

总组合数（合法组合，已扣除互斥）：

- linear_concertina spine：lattice_pattern ∈ {single_diamond, bare_pantograph}（solid_panels 互斥）= 2 × endpost_lock 2 × guide_track 2 = **8**
- accordion_hinge spine：lattice_pattern 必为 solid_panels = 1 × endpost_lock 2 × guide_track 2 = **4**
- 槽位组合合计 = **12 distinct slot combos**
- 叠 multiplicity：每 combo × distinct N（采样域 [4,20] ⇒ ≥10 distinct N 易得）。即便保守只取 distinct N=3（{5,10,16}）：12 × 3 = **36 ≫ 10 ✓**；产品域 N 全程 ⇒ 12 × 17 = 204。

理由：单 12 个 slot combos（含剪式 REVOLUTE-scissor ↔ 交替 ±2 REVOLUTE-accordion ↔ PRISMATIC drop-bolt 三种关节拓扑差异）已 >10；叠 N 后远超。

seed_domain_policy：**procedural_first**

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng`/seed 派生 deterministic sampler：(1) 加权采样 N∈[4,20]；(2) 先采 kinematics（按权重 linear_concertina ~75% / accordion_hinge ~25%）→ 由 kinematics 解析 lattice_pattern 合法集（concertina ⇒ {single_diamond, bare_pantograph} 等概；accordion ⇒ solid_panels 固定）；(3) 独立采 endpost_lock / guide_track / palette_style；(4) 采连续 scale，按第 7 节契约 resolve。compatibility matrix 在 `resolve_config` 中硬性 gate solid_panels⟺accordion_hinge，并把 drop_bolt 的 trailing 挂点按 spine 解析。`slot_choices_for_seed` 返回 `(slot, module)` + N，与 build 实际一致。少量 regression overrides 仅用于已知失败回归（见下，初版可为空）。random sweep：seeds 0-49 初轮、0-999 成熟审计；viewer 目检 hero pose（展开跨满洞）+ 半折 + 全折姿态、palette、N=4 / N=20 端值。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本类别合法 slot combos 仅 12，叠 N（[4,20]=17 distinct）⇒ 理论上限 204；实际 1000-seed 因加权会偏小 N 与 concertina，distinct 预计 ~120-180。低于 300 时说明为 accordion 子域 combos 少（仅 4）与类别兼容约束。

Controlled local parameterization：初版应含 `frame_width_scale`[0.85,1.25] / `frame_height_scale`[0.90,1.15] / `v_rise`[0.035,0.055] / `picket_cross`[0.010,0.018] / `fold_upper`[0.9,1.25]（accordion）+ derived `pitch_open`。依赖关系：pitch_open = equation（依赖 frame_width_scale × N）；pitch_open vs S_HALF/FOLD_ANGLE 可解性、格栅不越右 stile = inequality；OPEN_Z0/PICKET_Z0 = conditional（依赖 guide_track）。全部在 `resolve_config` clamp/派生/投影，不破坏 FIXED 接地、mimic 链、单驱动 invariant、N multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | spine→lattice 派生→正交采 C/D/palette→加权 N→连续 scale；deterministic over seed | slot_choices_for_seed matches build choices（含 N） |
| compatibility matrix | solid_panels⟺accordion_hinge 强绑定；其余正交；drop_bolt trailing 挂点按 spine 解析；单 fold drive 唯一 | no floating（FIXED 接地）、no collision、mimic 轴/range 正确、closed pose 不越洞、N≤20、drop_bolt PRISMATIC seated、可选 child 不失败 |
| controlled local variation | frame_*_scale / v_rise / picket_cross / fold_upper + derived pitch_open，clamp+投影 | 比例变化不破坏 interface / clearance / FIXED support / joint origin / category identity |
| regression overrides | none（初版；若 sweep 暴露失败再加 seed+理由） | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | & contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A lattice_pattern | 3 | yes | yes | single_diamond / bare_pantograph / solid_panels |
| B kinematics | 2 | yes | no | 样本池仅两种合法主机构家族 |
| C endpost_lock | 2 | yes | no | 样本池仅两种端锁家族 |
| D guide_track | 2 | yes | no | 样本池仅两种导轨家族 |
| E cell_count (N) | [4,20] | yes(distinct ≥3) | — | multiplicity 轴 |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D + N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（尤其 solid_panels 必配 accordion_hinge，反之亦然；非法组合永不进 sampler）
- optional regression overrides are sparse and justified（初版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped；pitch_open(equation)/可解性 & 不越右 stile(inequality)/OPEN_Z0(conditional) 均在 resolve_config 求解，不留到 builder 失败
- critical InterfaceSpec/MatingContract 存在：FIXED frame→首件接地、cell↔cell REVOLUTE 链、drop_bolt PRISMATIC seats in floor_socket
- key joints 类型/轴/range：`fold` REVOLUTE 唯一驱动；concertina lambda 1:-2:1 mimic（axis ±Y）；accordion hinge 交替 ±2（axis +Z）；bolt_slide PRISMATIC（axis +Z, lower=0 seated）
- copied objects follow naming/placement：`picket_{i}`/`lam_*_{c}`/`asc|desc|xup|xdn_{c}_{ri}`/`panel_{i}`/`hinge_{i}`，规则 pitch 放置
- 展开 hero pose（q=0）跨满洞、半折/全折 picket 始终竖直水平、折叠后不越 head rail / 右 stile

## Reject cases

- 折叠门有 >1 个显式驱动关节（违反单 fold + 全 mimic invariant），或 mimic 链断裂导致 picket 折叠时倾斜/不水平。
- solid_panels 配 linear_concertina，或 single_diamond/bare_pantograph 配 accordion_hinge（互斥组合未被 gate 拦截）。
- 展开格栅越出右 stile（`LEAD_X + N*pitch_open > OPEN_X1`），或折叠后 strap/panel 顶越过 head rail / 底穿楼板。
- `pitch_open*0.5 > S_HALF` 致 `FOLD_ANGLE=acos(...)−THETA0` 无解（NaN），未在 resolve_config 回缩/拒绝。
- frame 不接地（FIXED frame→首件缺失或 z-min≠0）或首件 mount_bracket 未嵌 stile → 整门漂浮。
- top_track_only 仍发射 sill_rail/bottom_track，或 dual_track 缺 sill_rail；guide_track 与 OPEN_Z0/PICKET_Z0 conditional 不一致。
- drop_bolt 的 bolt_slide 非 PRISMATIC、seated pose（q=0）bolt tip 未落入 floor_socket，或 end_post 未 FIXED 到 trailing 件。
- N 越界（<4 或 >20）未 clamp，或大 N 由非循环硬编码而非 `for c in range(N_CELLS)` 重发射。
- 把 palette_style / 整体 scale / picket 截面当作独立结构 candidate（纯尺寸/颜色不构成 slot 候选）。

## 与相邻类别的边界

- 不该混入：**实心折叠门叶 / bi-fold door leaves（Door / Folding door）**——那是少数大块刚性门扇沿铰链对折、无 N 个同构格栅 cell、无剪式伸缩、通常无固定外框 + guide track（注：本类的 accordion_hinge+solid_panels 仍是 N 个等宽窄 panel 的 concertina security gate，含固定钢框与单驱动 mimic 折叠，区别于少数宽门扇的 bi-fold door）。
- 不该混入：**卷帘门 / roller shutter（Door / Rolling shutter）**——卷帘是 PRISMATIC 沿竖直方向卷起的连续帘片，运动轴与 spine 完全不同，无水平剪式伸缩、无 picket 链。
- 不该混入：**推拉栅栏门 / sliding fence gate / barrier gate**——平移或绕单铰旋转开合，不折叠收拢、无手风琴 mimic 链；barrier gate（rec_barrier_gate_*）是单根抬杆 REVOLUTE，与折叠格栅无结构关系。
- 不该混入：**固定栅栏 / fence panel**——无任何 articulation（纯静态格栅），folding_gate 必须有单 fold 驱动 + 全 mimic 折叠运动。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：concertina 直接改编 parent `lam_bar()`（L249-257）；bare_pantograph 用 `_crossed_bar()`（L252-274）；accordion 用 `_add_panel_visuals()`（L85-141）。跨 spine 的 picket vs panel 命名差异需在 trailing-link 解析处统一（drop_bolt 挂点）。
- InterfaceSpec / MatingContract 重点：FIXED frame→首件接地（z-min=0 invariant）；cell↔cell REVOLUTE 链的 1:-2:1 mimic 必须保证 picket 在任意 q 竖直 + 水平（parent test L507-523 是金标准）；drop_bolt PRISMATIC seated pose 的 bolt-in-socket contact。
- captured-pin / lap overlap 需 element-scoped allow_overlap：所有 rivet-lap（strap↔picket、lambda 半杆↔picket↔elbow、相邻 cell 同族 strap 共享 picket rivet、accordion hinge_barrel seam、drop_bolt↔frame socket、end_post↔last picket/strap 末端）。parent `lap_pairs` 列表（L245-441）+ dropbolt 追加（L535-570）+ accordion `overlap_pairs`（L258-287）是完整清单模板。
- 暂不进入 seed domain：curved-track 转角门（运动学需非线性轨道求解，超出单层结构，源 map 已 drop）。
- accordion 子域 slot combos 仅 4，是 topology distinct 偏低的唯一来源；如成熟审计需更高 distinct，可在 P2+ 补纯 solid_panels（保留线性剪式）/ 纯 accordion（保留菱形 leaf）的 A/B 解耦候选，本批不要求。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | single_diamond + linear_concertina + mid_latch_knob + dual_track（基线） | rec_door_folding_gate | frame L137-193 / lam_bar L249-257 / lambda 链 L259-330 / strap L335-417 | root frame + 剪式 spine + 菱形 lattice + 静态 latch + 双轨 |
| S2 | A | bare_pantograph | rec_folding_gate_var_picket_pantograph | `_crossed_bar` L252-274 / xbar loop L348-424 | 裸两杆 X lattice |
| S3 | A+B | solid_panels + accordion_hinge | rec_folding_gate_var_accordion_panels | `_add_panel_visuals` L85-141 / panel loop L221-229 / fold L242-253 / hinge ±2 L263-280 | 实心 leaf + piano-hinge zigzag spine |
| S4 | C | drop_bolt | rec_folding_gate_var_dropbolt_post | end_post L460-493 / drop_bolt+bolt_slide L496-532 / floor_socket L194-207 | 端柱 + PRISMATIC 落地锁 |
| S5 | D | top_track_only | rec_folding_gate_var_top_track_only | frame L156-169 / OPEN_Z0 L66 / PICKET_Z0 L97 | 吊挂单顶轨 |
| S6 | E | cell_count N | rec_folding_gate_var_ncells5 / rec_folding_gate_var_ncells16 | `N_CELLS` L66（ncells16 +FRAME_W L52） | multiplicity 轴端值 |
