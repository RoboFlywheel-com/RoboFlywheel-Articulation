# window — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `window` |
| template path | `agent/templates/Window_Window.py` |
| test path (optional) | `tests/agent/test_window_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：核心是 `parallel_children`（一个静态 `frame`/`surround` root 上挂可动 sash 子件 + 固定 glass/muntin visual），叠加 **两条 multiplicity 轴**（divided-light 网格条数 C、sash/unit 数 D）。机构（A）与轮廓（B）是固定 named-slot 选择轴，不复制。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | all 5-star samples in this category（9 parents + 7 variants），逐文件读 model.py |
| source_index_policy | only adopted module sources are indexed below |

要点（全部 16 个均完整读取）：

- **统一坐标系**：所有样本一致 — +Z 向上、宽沿 X、frame depth / 玻璃厚 / swing-normal 沿 Y、玻璃面在 X-Z 平面、sill 底部约 z=0、窗站立。round-porthole 是唯一的整圆变体，但仍是 X-Z 立面圆盘。
- **统一根装配**：每个样本都有一个 **静态 root part**（`frame` 或 `surround`），用 CadQuery「实心 slab 切出开口」做成真正的周边 ring（不是带洞的盒子），可动 sash 是独立 part 经 articulation 挂上去。固定玻璃 / muntin / 拱顶石 / fanlight 一律是 root 或 sash 的 **parent visual**，不是独立 part。
- **机构是类别身份**：可动 sash 在其铰链上的运动是 category-defining motion。side-hung（竖轴 REVOLUTE）、awning（顶铰横轴 REVOLUTE）、hopper（底铰横轴 REVOLUTE）、single-hung（竖向 PRISMATIC，**下扇**动而上扇 FIXED）、porthole center-pivot（横轴 REVOLUTE）、fixed_picture（主光 FIXED + 单个 vent 翻板 REVOLUTE）。
- **玻璃合约**：所有样本的玻璃都 rebate（嵌入）在 sash/frame lip 下，靠 `allow_overlap(elem_a=glass, elem_b=frame/ring)` 声明为 captured 而非漂浮。铰链 / 把手 / stay / pivot-pin 也用 element-scoped allow_overlap 声明 mount 嵌入。
- **mount 嵌入是普遍模式**：sash top/bottom rail 在 frame head/sill lip 下被「捕获」(`HINGE_CAPTURE`)，或 sash rebate 搭在 jamb lip 上 — 这是真实铰接路径，须 frame↔sash allow_overlap。
- **multiplicity 母体**：muntin 网格（arched 3×5 + radial fan 7；muntin_grid_2x2/3x3 共享 `_muntin_bar` helper + 嵌套 col×row pane loop）；bank 网格（bank 3×2、bank_2x2 嵌套 `for col / for row` + `_lite_bounds`）；多扇（twin/double `_add_sash(sign/mirror)` ×2；triple_mullion `for i in range(NUM_SASHES)` 单一参数驱动）。
- **手写 / 无 loop 母体**（不可直接做 multiplicity 母体）：single-hung（上下两扇手写，无 for-loop）、porthole（pivot_pin 手写 `_{tag}` 两个）、awningalu / awningsteel（无 for-loop；awningsteel 固定 lites 用闭包逐个手写）。结论同 source-map：所有派生 multiplicity 变体都 fork 自已 PASS loop-emission 的母体（sidehung / doublecase / bank）。

## 核心身份

一扇 **建筑窗户**：一个静态外框（frame / 周边 ring + 可选 sill / 石材 surround / mullion / transom）容纳一个或多个 **glazed sash（带框玻璃光）**，至少一个 sash 经铰链或竖向滑轨成为可动开启扇（category-defining motion）。成熟域 = 单扇到 bank 多单元的住宅 / 工业 / 建筑窗，矩形 / 拱顶 / 圆形 porthole / segmental 弧头轮廓，可有 colonial muntin 分格、venetian 百叶、把手、stay bar、铰链等真实五金。

不该混入的相邻类别见 §与相邻类别的边界。**特别注意**：滑动 sash（左右平移）属于另一个 `sliding_window` 小类 — 本 spec 的 Slot A **不含 sliding**，single-hung 的竖向升降（PRISMATIC，up-slide）是允许的因为它是上下窗的标准机构而非左右滑窗 identity。

## 槽位 + 候选模块表

### Slot A：opening_mechanism（主机构槽 — 开启方式 / sash 运动类型）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| side_hung_casement（基线） | rec_side-hung-...4f1abc4d | L107-L279 (frame L107-128, sash L138-171, BarrelHinge+stay L212-261, REVOLUTE axis z L269-277) | eligible if compatible | 侧铰立轴外开；`frame_shell` + `sash_frame`/`sash_glass` + `hinge_{i}`(L228-235) + `stay_bar`/`stay_pivot`；REVOLUTE axis (0,0,1)，free 边外摆 +Y |
| awning_top_hung | rec_aluminium-awning-...0b523c52 | L98-L222 (frame L98-115, sash ring/glass hinge-local L118-152, handle L187-208, REVOLUTE axis x L214-221) | eligible if compatible | 顶铰横轴；sash body 沿 local -Z 悬挂，axis (1,0,0)，底缘外踢 +Y；`handle_base`/`handle_lever` 在底 rail |
| single_hung_vertical | rec_single-hung-...d91f35ac | L102-L265 (frame+side-track L102-137, `_add_sash` L178-189, cam lock L216-240, FIXED upper L245-251 + PRISMATIC lower L255-265) | eligible if compatible | 上扇 FIXED + 下扇竖向 PRISMATIC up-slide，axis (0,0,1)；`frame_shell`/`upper_sash`/`lower_sash` + `lower_sash_cam_lever`；**注：source 无 for-loop（上下两扇手写）** |
| fixed_picture_light | rec_window_var_fixed_picture | L100-L298 (frame L100-120, fixed sash+vent-slot cut L123-156, vent recess L175-189, vent flap part L237-264 + knuckle loop L271-283, REVOLUTE vent axis x L290-298) | eligible if compatible | 主光冻结为 frame 上的固定 picture light（无 swing）；唯一可动 = 顶 rail trickle-vent 翻板（REVOLUTE axis x，底缘外翻 +Y） |
| hopper_bottom_hung | rec_window_var_hopper | L99-L224 (frame L99-116, sash bottom-hinge-local L119-153, top-rail handle L191-209, REVOLUTE axis x L216-223) | eligible if compatible | 底铰横轴；sash body 沿 local +Z 上伸，axis (1,0,0)，顶缘内倾 -Y；`handle_base`/`handle_lever` 在顶 rail |

降级说明：5 候选，无降级。**round center-pivot**（porthole）作为机构本可列第 6，但它与 round_porthole 轮廓强耦合（圆盘 sash 绕横直径自转），故归入 Slot B round_porthole 的 module-local 机构（见兼容矩阵），不单列为 Slot A 通用机构以避免非圆轮廓上出现裸 center-pivot。

### Slot B：frame_outline（外框 / 扇轮廓形状）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular（基线） | rec_side-hung-...4f1abc4d | L107-L128 (`_build_outer_frame_shape` slab.cut 矩形开口) | eligible if compatible | 直角矩形开口；slab 切矩形 opening 成周边 ring；sash `_build_sash_frame_shape` L138-155 同矩形 |
| arched_top（拱顶 + fanlight） | rec_arched-top-...6cbe185b | L132-L182 (`_build_wood_frame_shape` 矩形+半圆 threePointArc) + L185-227 (`_build_fanlight_shape` radial+arc) + L259-275 (keystone) | eligible if compatible | 圆拱顶（threePointArc 半圆 head）+ 上方 radial fanlight + stone surround/keystone/corbel；sash 跟随拱底矩形部分 |
| round_porthole | rec_round-porthole-...30a4c378 | L81-L130 (`_ring_shape` lathe extrude-along-Y L81-92, `_disc_shape` L95-101, `_build_outer_frame_shape` bezel+collar L104-120, `_build_sash_ring_shape` L123-125) | eligible if compatible | 整圆环框（XZ workplane circle 旋出环）+ 圆盘玻璃；center-pivot sash 绕横直径 REVOLUTE axis (1,0,0)，pivot_pin L175-181 |
| segmental_arch | rec_window_var_outline_segmental_arch | L127-L163 (`_arch_solid` threePointArc 平底+弧顶) + L170-177 frame + L189-209 sash arch ring/glass | eligible if compatible | 平底圆顶 segmental 开口（concentric arc center，弧头非矩形顶 rail）；jamb 直、head 弧；sash 顶 rail 跟随同 arc |

降级说明：4 候选，无降级。每个轮廓改变 frame/sash 的 part primitive（box-cut vs threePointArc vs lathe-ring vs segmental-arc）即拓扑等价类。

### Slot C：divided_light_grid（muntin 分格多重度 — N panes）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| no_muntin（单光，N=1，基线） | rec_aluminium-awning-...0b523c52 | L118-L152 (`_sash_ring_shape` + `_sash_glass_shape` 单 pane，无 muntin) | eligible if compatible | 单一整玻璃光，无 muntin 条；awning/single-hung/twin/double 等多数样本采此（degenerate C=1） |
| colonial_2x2_4 | rec_window_var_muntin_grid_2x2 | L164-172 (`_muntin_bar` 共享 helper) + L213-232 (vertical/horizontal muntin loops) + L235-248 (`pane_{row}_{col}` 嵌套 loop) | eligible if compatible | 2×2 = 4 格；`vertical_muntin_{i}`/`horizontal_muntin_{i}` + `pane_{row}_{col}` |
| colonial_3x3_9 | rec_window_var_muntin_grid_3x3 | L176-185 (`_muntin_bar(orientation)`) + L188-190 (`_glass_pane`) + L221-232 (`pane_{j}_{k}` 嵌套) + L236-253 (`vmuntin_{i}`/`hmuntin_{i}` loops) | eligible if compatible | 3×3 = 9 格；共享 `_muntin_bar` + `_glass_pane` helper，col×row 全 loop 发射 |
| bank_grid（fixed-lite 网格，N=6 母体 3×2 / N=4 fork 2×2） | rec_bank-...478f6f0c | L99-105 (`_lite_bounds`) + L112-132 (frame web 嵌套切格 loop) + L135-145 (`_build_fixed_glass_shape`) + L280-290 (`fixed_glass_{col}_{row}` 嵌套发射) | eligible if compatible | 整框被 mullion/transom 切成 col×row lite 网格，每格固定玻璃 `fixed_glass_{col}_{row}`（兼作 Slot D unit 网格，见兼容矩阵） |
| arched_radial_fan（拱顶专用，扇形 7 + 殖民 3×5=15） | rec_arched-top-...6cbe185b | L185-227 (`_build_fanlight_shape` radial loop `for i in range(FAN_RADIAL_COUNT)` L197-210 + arc band L213-225) + L364-380 (sash muntin col/row loop) | eligible if compatible | 半圆 fanlight 放射 7 条 + 下扇 3×5 殖民网格；仅在 arched_top 轮廓下合法 |

降级说明：5 候选（含 N=1 degenerate）。distinct N 覆盖 {1, 4, 6/3×2, 9, 15/(7+3×5)}。C 是 multiplicity 轴：模板用规则网格 cols×rows loop 发射 muntin 条 + pane，N=cols×rows。

### Slot D：sash_unit_count（sash / 单元数多重度）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_1（基线） | rec_side-hung-...4f1abc4d | L193-204 (单 `sash` part) + L269-277 (单 REVOLUTE joint) | eligible if compatible | 1 扇；awning/porthole/awningsteel/single-hung 同属 N=1（单可动扇） |
| twin_double_2 | rec_twin-...16e9934d (L256-295 `_add_sash(sign)` + L325-326 两次) / rec_double-...039f0c0a (L215-270 `_add_sash(mirror_x)` + L295-296 两次, hinge loop L262-270) | eligible if compatible | 2 扇 mirror（X-mirror NOT yaw）；`sash_left`/`sash_right` 各自 REVOLUTE，free 边在中央 mullion 相对 |
| triple_mullion_3 | rec_window_var_triple_mullion | L103-121 (bay/mullion layout helper) + L127-175 (frame bay-cut loop) + L236-290 (`_add_sash` + hinge loop L282-290) + L316-344 (`for i in range(NUM_SASHES)` 建 sash + joint) | eligible if compatible | 3 扇 + 2 中梃；**单参数 NUM_SASHES 驱动**的线性 loop；per-unit hinge policy `_is_left_hung(i)` |
| bank_2x2_4 | rec_window_var_bank_2x2 | L97-103 (`_lite_bounds`) + L110-130 (frame web N_COLS×N_ROWS 切格) + L278-294 (fixed glass + 1 operable sash) + L305-313 (REVOLUTE) | eligible if compatible | 2×2 = 4 单元，1 扇可开其余 fixed lite |
| bank_3x2_6 | rec_bank-...478f6f0c | L49-61 (N_COLS=3,N_ROWS=2) + L112-132 (frame web 嵌套) + L276-302 (fixed glass + 2 operable) + L304-341 (两 REVOLUTE) | eligible if compatible | 3×2 = 6 单元，2 扇可开其余 fixed lite |

降级说明：5 候选。distinct N 覆盖 {1, 2, 3, 4, 6}。D 是 multiplicity 轴：linear（沿框宽 mullion 分隔）或 grid（cols×rows lite 网格）两种 placement。

## 槽位图（slot graph）

pattern: mixed（parallel_children 固定 named slots + 两条 multiplicity 轴）

```
                         frame_outline (Slot B)
                                │ 决定 root 周边 ring 的 primitive（box-cut / arch / lathe-ring / segmental）
                                ▼
   [root: frame / surround]  ──parent visual──> {fixed glass, muntin grid (Slot C),
        (静态 root part)                          fixed lites (Slot D 非可动 unit),
                                                  sill / stone surround / keystone / fanlight /
                                                  mullion / transom}
        │
        │  per operable unit r (Slot D, multiplicity N_D)
        │    ├─[REVOLUTE / PRISMATIC + interface (见下)]─> sash_{r}（可动 part）
        │    │        └─ sash_{r} 内含 Slot C 的 muntin grid（随 sash 运动，无独立 joint）
        │    │        └─ sash_{r} 内含 handle / hinge / stay (parent visual on sash)
        │    └─ 其余 unit = fixed_glass_{col}_{row}（FIXED-as-visual，挂 root，不动）
```

机构（Slot A）决定每个可动 sash 的 joint type / axis / origin / limits：

- **side_hung_casement**：interface = 竖直 hinge line（jamb 或 mullion 的 vertical edge）。joint = REVOLUTE，axis (0,0,±1)，origin 在 hinge 边 (HINGE_X, 0, sash_bottom_z)，limits lower=0 upper≈1.5。sash local x=0 在 hinge 边，body 沿 ±X 伸；free 边外摆 ±Y（sign 选定方向）。源：side-hung L269-277。
- **awning_top_hung**：interface = sash 顶 rail tuck 进 frame head lip（HINGE_CAPTURE）。joint = REVOLUTE，axis (1,0,0)，origin 在顶 rail (SASH_CX, SASH_Y, SASH_Z1)，limits upper≈0.85。sash body 沿 local -Z 悬挂，底缘外踢 +Y。源：awning L214-221。
- **hopper_bottom_hung**：interface = sash 底 rail tuck 进 frame sill lip。joint = REVOLUTE，axis (1,0,0)，origin 在底 rail (SASH_CX, SASH_Y, SASH_Z0)，limits upper≈0.85。sash body 沿 local +Z 上伸，顶缘内倾 -Y。源：hopper L216-223。
- **single_hung_vertical**：interface = jamb 内侧 side-track 槽（retained insertion）。下扇 joint = PRISMATIC，axis (0,0,1)，origin 在 seated 位 (0, LOWER_SASH_Y, LOWER_BOTTOM_Z)，limits upper = LOWER_SASH_H*0.45；上扇 joint = FIXED。源：single-hung L245-265。
- **fixed_picture_light**：主 sash = root 上的 FIXED visual（无 swing）。唯一 joint = trickle-vent 翻板 REVOLUTE，axis (1,0,0)，origin 在 vent slot 顶边 (0, SASH_DEPTH/2, VENT_HINGE_Z)，limits upper≈0.8。源：fixed_picture L290-298。
- **round_porthole center-pivot**（Slot B round 派生）：interface = 两 pivot_pin 沿横直径捕获 sash 到 outer ring bore。joint = REVOLUTE，axis (1,0,0)，origin 在圆心 (0,0,CENTER_Z)，limits lower=-0.8 upper=0.8。源：porthole L189-197。

互斥 / 派生关系：
- round_porthole 轮廓 → 强制 center-pivot 机构 + C=no_muntin（radial/concentric only，见兼容矩阵）。
- arched_top → 若 C=arched_radial_fan 则 fanlight 上 + 下扇 muntin 网格；Slot A 限 side_hung（拱底矩形开口侧铰）。
- bank（Slot D = bank_2x2/3x2）→ 每个 lite 重复 unit，只有部分 lite 是可动 sash（统一 REVOLUTE side-hung），其余 FIXED-as-visual fixed glass。

## 每槽位 Module Emits / Interfaces

### Slot A / module side_hung_casement
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sash`（可动）；root 上 `frame_shell` | side-hung / model.py:L186-204 |
| internal joints | 无（sash 内五金随 sash） | — |
| upstream interface | hinge line = jamb vertical edge；frame head/sill/jamb lip 捕获 sash rebate | side-hung / model.py:L264-277 |
| downstream interface | REVOLUTE axis (0,0,±1) origin (HINGE_X,0,SASH_BOTTOM_Z)；free 边外摆 ±Y | side-hung / model.py:L269-277 |
| parent visual on sash | `sash_frame`/`sash_glass` + `hinge_{i}`(L228-235) + `stay_bar`/`stay_pivot`(L242-261) | side-hung / model.py:L195-261 |

### Slot A / module awning_top_hung
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sash`（可动）；root `frame_shell` | awning / model.py:L167-185 |
| internal joints | 无 | — |
| upstream interface | sash 顶 rail tuck 进 frame head lip（HINGE_CAPTURE，contact） | awning / model.py:L252-258 |
| downstream interface | REVOLUTE axis (1,0,0) origin (SASH_CX,SASH_Y,SASH_Z1)；底缘踢 +Y | awning / model.py:L214-221 |
| parent visual on sash | `sash_ring`/`sash_glass` + `handle_base`/`handle_lever`(底 rail) | awning / model.py:L176-208 |

### Slot A / module hopper_bottom_hung
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sash`（可动）；root `frame_shell` | hopper / model.py:L168-186 |
| internal joints | 无 | — |
| upstream interface | sash 底 rail tuck 进 frame sill lip | hopper / model.py:L255-260 |
| downstream interface | REVOLUTE axis (1,0,0) origin (SASH_CX,SASH_Y,SASH_Z0)；顶缘倾 -Y | hopper / model.py:L216-223 |
| parent visual on sash | `sash_ring`/`sash_glass` + `handle_base`/`handle_lever`(顶 rail) | hopper / model.py:L176-209 |

### Slot A / module single_hung_vertical
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_sash`(FIXED)、`lower_sash`(PRISMATIC)；root `frame_shell` | single-hung / model.py:L204-215 |
| internal joints | upper FIXED + lower PRISMATIC | single-hung / model.py:L245-265 |
| upstream interface | jamb 内侧 side-track 槽（retained insertion，`allow_overlap` frame↔sash） | single-hung / model.py:L121-137, L290-301 |
| downstream interface | lower PRISMATIC axis (0,0,1) origin (0,LOWER_SASH_Y,LOWER_BOTTOM_Z)，upper=LOWER_SASH_H*0.45 | single-hung / model.py:L255-265 |
| parent visual on sash | `lower_sash_lock_base`/`lower_sash_cam`/`lower_sash_cam_lever`(meeting rail) | single-hung / model.py:L216-240 |

### Slot A / module fixed_picture_light
| emits | 描述 | 来源 |
|---|---|---|
| parts | `vent`（可动小翻板）；root `frame` 含固定 `sash_frame`/`sash_glass`/`vent_recess` | fixed_picture / model.py:L205-234, L237 |
| internal joints | 无 | — |
| upstream interface | 主 sash FIXED-as-visual 嵌 frame rebate；vent hinge 在 sash 顶 rail vent-slot 顶边 | fixed_picture / model.py:L290-298 |
| downstream interface | REVOLUTE axis (1,0,0) origin (0,SASH_DEPTH/2,VENT_HINGE_Z)，upper≈0.8 | fixed_picture / model.py:L290-298 |
| parent visual on vent | `vent_flap` + `vent_catch` + `vent_knuckle_{i}`(L271-283) | fixed_picture / model.py:L243-283 |

### Slot A / module round_porthole_center_pivot（Slot B round 派生）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sash`（可动圆盘）；root `frame`(bezel+collar ring) | porthole / model.py:L144-167 |
| internal joints | 无 | — |
| upstream interface | 两 pivot_pin 沿横直径捕获 sash 到 outer ring bore（contact + allow_overlap） | porthole / model.py:L169-181, L228-238 |
| downstream interface | REVOLUTE axis (1,0,0) origin (0,0,CENTER_Z)，lower=-0.8 upper=0.8 | porthole / model.py:L189-197 |
| parent visual on sash | `sash_ring`/`sash_glass` + `pivot_pin_{tag}` | porthole / model.py:L157-181 |

### Slot B / frame_outline emits（影响 root + sash primitive）
| emits | 描述 | 来源 |
|---|---|---|
| rectangular | slab.cut 矩形 opening → 周边 ring；sash box ring | side-hung / model.py:L107-128, L138-155 |
| arched_top | threePointArc 半圆 head 周边 + spring transom + center mullion + stone surround/keystone/corbel/fanlight | arched / model.py:L132-182, L230-316 |
| round_porthole | lathe `_ring_shape`（XZ circle extrude-Y）bezel+collar + disc glass | porthole / model.py:L81-130 |
| segmental_arch | `_arch_solid`（平底+弧顶 threePointArc，concentric arc center）frame + sash | segmental / model.py:L127-209 |

### Slot C / divided_light_grid emits（sash 内 parent visual，随 sash 运动）
| emits | 描述 | 来源 |
|---|---|---|
| muntin bars | `vertical_muntin_{i}`/`horizontal_muntin_{i}`（2x2）或 `vmuntin_{i}`/`hmuntin_{i}`（3x3）共享 `_muntin_bar` helper | muntin_2x2 / model.py:L164-172, L213-232; muntin_3x3 / model.py:L176-185, L236-253 |
| panes | `pane_{row}_{col}` 嵌套 col×row loop 发射 | muntin_2x2 / model.py:L235-248; muntin_3x3 / model.py:L221-232 |
| fanlight (arched only) | radial `for i in range(FAN_RADIAL_COUNT)` + arc band | arched / model.py:L197-225 |
| bank fixed-lite grid | `fixed_glass_{col}_{row}` 嵌套发射（兼 Slot D） | bank / model.py:L280-290 |
| internal joints / interface | 无独立 joint；muntin/pane 随所属 sash 的 REVOLUTE（单扇）或随 root（fixed lite） | — |

### Slot D / sash_unit_count emits（multiplicity 复制可动单元）
| emits | 描述 | 来源 |
|---|---|---|
| sash parts | `sash_{i}`（linear）或 operable lite sash（grid）+ per-unit `{name}_hinge_{i}`/`{name}_handle_*` | triple_mullion / model.py:L236-290, L316-344; bank / model.py:L191-252 |
| fixed units | `fixed_glass_{col}_{row}`（grid 中非可动 unit，FIXED-as-visual 挂 root） | bank / model.py:L276-290 |
| mullion / transom | linear bay 分隔 mullion（frame slab 切格残留）/ grid transom | triple_mullion / model.py:L127-175; bank / model.py:L112-132 |
| per-unit joints / interface | 每可动 unit 一个 REVOLUTE（统一 side-hung）；hinge policy `_is_left_hung(i)`(linear) 或 operable-set(grid) | triple_mullion / model.py:L317-344; bank / model.py:L304-341 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| opening_mechanism | enum | side_hung / awning / hopper / single_hung / fixed_picture（+ round-derived center_pivot） | — | choice | 由 deterministic procedural sampler 选择；受 Slot B 兼容矩阵 gating | Slot A table |
| frame_outline | enum | rectangular / arched_top / round_porthole / segmental_arch | — | choice | 由 sampler 选择；round/arched 触发机构 gating | Slot B table |
| divided_light_grid | enum | no_muntin / colonial_2x2 / colonial_3x3 / bank_grid / arched_radial_fan | — | choice | conditional：受轮廓与 unit 兼容矩阵约束 | Slot C table |
| sash_unit_count | enum | single_1 / twin_double_2 / triple_mullion_3 / bank_2x2_4 / bank_3x2_6 | — | choice | conditional：受机构与轮廓兼容矩阵约束 | Slot D table |
| muntin_cols | int (count_param C) | [1, 6]（产品全程；测试偏小，见 §multiplicity） | 1 | independent | 加权采样；与 muntin_rows 共同给出 N=cols×rows | muntin_2x2/3x3 GRID_COLS |
| muntin_rows | int (count_param C) | [1, 6] | 1 | independent | 同上 | muntin_2x2/3x3 GRID_ROWS |
| unit_cols | int (count_param D) | [1, 4]（grid 模式） | 1 | independent | 与 unit_rows 给 N=cols×rows；linear 模式用 sash_count | bank N_COLS |
| unit_rows | int (count_param D) | [1, 3]（grid 模式） | 1 | independent | 同上 | bank N_ROWS |
| sash_count | int (count_param D) | [1, 12]（linear 模式 NUM_SASHES） | 1 | independent | linear bay 数；与 grid 互斥（由 unit module 决定哪种 placement） | triple_mullion NUM_SASHES |
| win_width_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 WIN_W / TOTAL_W / LITE_W 等宽度尺度 | 各 frame WIN_W/TOTAL_W |
| win_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 WIN_H / TOTAL_H / SASH_H | 各 frame WIN_H/TOTAL_H |
| frame_face_scale | float | [0.8, 1.3] | 1.0 | independent | clamp；缩放 FRAME_FACE / FRAME_W | 各 frame FRAME_FACE |
| sash_open_frac | float | [0.0, 1.0] | 0.0 | independent | 映射到 joint q（rest 闭合）；× motion_limits.upper | 各机构 motion_limits |
| arch_rise_scale | float | [0.7, 1.3] | 1.0 | conditional | 仅 arched/segmental 轮廓有效；clamp，arc center 重算 | arched ARCH_R / segmental ARCH_RISE |
| palette_style | enum | warm_stained_wood / anthracite_aluminium / sage_grey / industrial_white_steel / glossy_black_porthole / grey_aluminium_blue_glass | warm_stained_wood | choice | 每 seed 抽一组 (frame/sash/glass/hardware) rgba；不改拓扑 | 见下 palette 来源 |
| (—) | constraint | — | — | inequality | `sash_total_W = Σ unit_bay_W + (N-1)·MULLION_W + 2·FRAME_FACE`；超 envelope 时按比例回缩 unit_bay_W 或拒绝重采 | triple_mullion L84-88 |
| (—) | constraint | — | — | inequality | `muntin grid cell_w/cell_h ≥ MIN_CELL(≈0.06)`；cols×rows 过大时下调 N 或拒绝 | muntin CELL_W/CELL_H |
| (—) | constraint | — | — | inequality | `sash inside opening`：SASH_W ≤ OPENING_W − 2·SASH_CLEAR；frame_face_scale 增大时回缩 sash | 各 frame OPENING/SASH 推导 |

palette_style 来源（≥3，目标 4-6，全部观测自 5★ 源）：
- **warm_stained_wood**：WOOD (0.255,0.145,0.075) / GLASS (0.16,0.17,0.22,0.38) / BRASS (0.80,0.62,0.22) — side-hung L98-100。
- **anthracite_aluminium**：ANTHRACITE (0.13,0.135,0.145) / WHITE_SILL (0.92,0.92,0.93) / GLASS (0.55,0.62,0.68,0.28) / SLAT (0.85,0.86,0.87) — twin L93-97。
- **sage_grey**：FRAME (0.74,0.74,0.68) / SASH (0.76,0.76,0.70) / GLASS (0.62,0.70,0.74,0.26) / LOCK (0.80,0.81,0.83) — single-hung L92-95。
- **industrial_white_steel**：STEEL (0.86,0.85,0.82) / GLASS (0.46,0.52,0.57,0.32) — awningsteel L62-63。
- **glossy_black_porthole**：BLACK (0.045,0.045,0.050) / GLASS (0.05,0.06,0.09,0.45) / PIN (0.30,0.31,0.33) — porthole L65-67。
- **grey_aluminium_blue_glass**：ALU (0.62,0.64,0.66) / SASH (0.66,0.68,0.70) / GLASS (0.62,0.78,0.84,0.34) / HANDLE (0.30,0.31,0.33) — bank L87-91。

连续尺寸采样契约：先采 independent 主尺度（win_width_scale / win_height_scale / frame_face_scale 等，均匀采样后 clamp）→ 按 equation 派生从属（sash 尺寸由 opening − clearance 推导）→ 用 inequality 把 unit_total / muntin cell / sash-inside-opening 投影回缩或拒绝重采 → conditional 范围（arch_rise_scale 仅拱形有效）在采样前按 Slot B choice 解析。

## Multiplicity / Copy Logic

**两条独立 multiplicity 轴**（per-axis 各做一次加权采样，各自 clamp，各自 sweep 上限）：

### 轴 C — divided_light_grid（muntin 分格）
- `count_param`：`(muntin_cols, muntin_rows)`，N_C = muntin_cols × muntin_rows。
- `N_range`（本轴产品域）：cols ∈ [1,6]、rows ∈ [1,6]，N_C ∈ [1, 36]。样本已覆盖 distinct {1, 4, 6, 9, 15}。
- sampling domain（权重档）：N_C=1（no_muntin）高频（多数真实窗单光）；2×2/2×3/3×3 中频；>16 稀有尾部下调。测试偏小（cols,rows ≤ 3），产品全程但大 N 稀疏采样 + cell-size inequality 兜底。
- copied object：内框均分网格的 muntin 条（竖 loop `for i in range(cols-1)` + 横 loop `for i in range(rows-1)`）+ 对应玻璃格。
- naming：`vertical_muntin_{i}` / `horizontal_muntin_{i}`（或 `vmuntin_{i}` / `hmuntin_{i}`）+ `pane_{row}_{col}`。
- placement：sash 内框（INNER_X0..INNER_X1 × INNER_Z0..INNER_Z1）规则均分网格，cell_w/cell_h 派生。
- joint policy：muntin 与 pane 随所属 sash 运动（单扇随该 sash 的 REVOLUTE，无独立 joint）；fixed-lite 网格随 root（FIXED-as-visual）。
- source/gating：母体 muntin_grid_2x2/3x3（fork ← sidehung，已 PASS loop-emission）；arched 专用 radial_fan 仅 arched_top 轮廓；round_porthole 轮廓强制 N_C=1。

### 轴 D — sash_unit_count（sash / 单元数）
- `count_param`：linear 模式 `sash_count`（NUM_SASHES）；grid 模式 `(unit_cols, unit_rows)`，N_D = unit_cols × unit_rows。
- `N_range`（本轴产品域）：linear sash_count ∈ [1, 12]；grid cols ∈ [1,4]、rows ∈ [1,3]（N_D ∈ [1,12]）。样本已覆盖 distinct {1, 2, 3, 4, 6}。
- sampling domain（权重档）：N_D=1（单扇）高频；2（twin/double）中频；3-6 中低频；>6 稀有尾部下调（住宅窗少见多扇 bank）。
- copied object：可动 sash 扇 + 其 sash_frame/ring、玻璃、铰链、把手；grid 模式额外发射非可动 `fixed_glass_{col}_{row}`。
- naming：linear `sash_{i}` + `{name}_hinge_{h}` + `{name}_handle_*`；grid operable sash + `fixed_glass_{col}_{row}`。
- placement：linear 沿框宽规则偏移（`_bay_left(i)` / `_mullion_center(i)`），以 mullion 分隔；grid 用 `_lite_bounds(col,row)` 嵌套网格，以 mullion+transom 分隔。
- joint policy：每可动扇统一 REVOLUTE side-hung（linear hinge policy `_is_left_hung(i)`：sash 0..N-2 左铰、末扇右铰；grid 中仅指定 operable lite 是可动 sash，其余 FIXED-as-visual fixed glass）。
- source/gating：linear 母体 triple_mullion（fork ← doublecase，单参数 NUM_SASHES loop）；grid 母体 bank_2x2/bank_3x2（fork ← bank，嵌套 col×row loop）；均已 PASS loop-emission。

机构（Slot A）与轮廓（Slot B）为固定 named slot，**非复制轴**（不暴露 `*_count`，不循环复制模板级机构 / 轮廓）。

## 拓扑多样性审计

总组合数（slot 笛卡尔，未含连续 N）：A × B × C × D = 5 × 4 × 5 × 5 = **500**（即便仅 A×B = 20 ≥ 10 已单独过闸）。
把 multiplicity N 计入：C distinct N {1,4,6,9,15,...} + D distinct N {1,2,3,4,6,...} 远超机械门槛。

理由：仅 Slot A×B（机构 × 轮廓）已给 20 个拓扑不同组合，每个改变 part tree / joint type / axis / primitive；叠加 C、D 两条 multiplicity 轴后 1000-seed slot choice tuple distinct 预计按 ≥300 富类别口径观察（每个 (N_C, N_D, A, B) 在 part/joint count 上都是不同 equivalence class）。

seed_domain_policy：procedural_first（`seed=0` 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 先抽 Slot B 轮廓（决定 primitive 与机构 gating），再抽 Slot A 机构（经兼容矩阵过滤），再各自加权抽 C、D 的 N（小 N 偏多、大 N 尾部下调），最后采连续 scale 并 clamp / 投影回可行域。compatibility matrix 在 `resolve_config` 内 gating 排除非法组合（见下）。少量 regression overrides 仅用于已知失败回归（fixed_picture vent-anchor 漂浮、segmental 弧头退化成 boxy）。random sweep：seeds 0-49 初轮、0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only），本类别 A×B×C×D 组合空间足够支撑。
Controlled local parameterization：win_width_scale [0.85,1.20]、win_height_scale [0.85,1.20]、frame_face_scale [0.8,1.3]、arch_rise_scale [0.7,1.3]（conditional 仅拱形）、sash_open_frac [0,1]（映射 joint q）。全部在 `resolve_config` clamp / 派生：sash 尺寸 = opening − clearance（equation）；unit_total_W、muntin cell-size、sash-inside-opening 用 inequality 投影回缩或拒绝；arch_rise 改变时 arc center 重算（不破坏 segmental/arched 的 lathe/arc 几何与 sash 顶 rail 跟随）。这些 scale 不改变拓扑等价类、不破坏 InterfaceSpec（hinge line / rail-capture / pivot-pin）/ MatingContract / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽序 B→A→(C,D 加权 N)→连续 scale；slot_choices_for_seed 仅记录改变拓扑等价类的 enum 与 N | slot_choices_for_seed matches build choices |
| compatibility matrix | round_porthole ⇒ center_pivot 机构 + C=no_muntin（radial/concentric only），D=single_1（圆盘单扇）；arched_top ⇒ A=side_hung，C ∈ {no_muntin, arched_radial_fan, colonial}；segmental_arch ⇒ A=side_hung/awning；single_hung/fixed_picture ⇒ D=single（不进 bank/triple）；bank grid (D≥4) ⇒ A=side_hung 统一、仅部分 lite 可动其余 FIXED；fixed_picture vent 必须 anchor 在可见 sash 顶 rail 实体面（非薄不可见框顶） | no floating, collision, axis, max multiplicity, bulky module, optional child failures |
| controlled local variation | win_width/height_scale、frame_face_scale、arch_rise_scale(conditional)、sash_open_frac，全部 clamp + 派生 sash/opening/cell，违反 inequality 投影回缩 | proportions vary without breaking interfaces, clearance, support, joint origin, identity |
| regression overrides | none（首版）/ 仅 fixed_picture vent-anchor 漂浮、segmental 弧头退化、porthole pivot-pin AABB（如出现）按 seed 记录原因 | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A opening_mechanism | 5 | yes | yes | side_hung/awning/hopper/single_hung/fixed_picture（+round-derived center_pivot） |
| B frame_outline | 4 | yes | yes | rectangular/arched_top/round_porthole/segmental_arch |
| C divided_light_grid | 5 | yes | yes | no_muntin/2x2/3x3/bank_grid/arched_radial_fan（multiplicity 轴 distinct N {1,4,6,9,15}） |
| D sash_unit_count | 5 | yes | yes | single/twin_double/triple_mullion/bank_2x2/bank_3x2（multiplicity 轴 distinct N {1,2,3,4,6}） |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D enum + 改变拓扑的 N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（`seed=0` 不特殊）
- compatibility matrix / gating prevents illegal module combinations（porthole↔center_pivot↔no_muntin↔single；arched↔side_hung；bank↔统一 side_hung；single_hung/fixed_picture↔single）
- optional regression overrides are sparse and justified（仅 vent-anchor / segmental / pivot-pin 已知风险）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (win_width/height_scale, frame_face_scale, arch_rise_scale, sash_open_frac) are clamped and cannot break hinge line / rail-capture / pivot-pin interfaces, clearance, joint origin, or multiplicity
- cross-part scale dependencies (sash=opening−clearance equation；unit_total / cell-size / sash-inside-opening inequality；arch_rise conditional) resolved in `resolve_config`, not in builder
- critical InterfaceSpec / MatingContract points exist：hinge line (vertical/horizontal)、rail-under-head/sill capture、jamb side-track、pivot-pin-to-bore、vent-slot-top-edge
- key joints have expected type/axis/range：side_hung REVOLUTE z；awning/hopper/porthole/vent REVOLUTE x；single_hung lower PRISMATIC z + upper FIXED；fixed_picture 主光 FIXED + 单 vent REVOLUTE
- copied objects follow naming and placement policy：`sash_{i}`/`{name}_hinge_{h}`/`fixed_glass_{col}_{row}`/`pane_{row}_{col}`/`*muntin_{i}`
- 每个可动扇 rest pose（q=0）闭合、coplanar；open pose 自由边外摆 / 内倾 / 升降，hinge 边 / 底 rail / 顶 rail 不动（按机构）

## Reject cases

- sliding sash 作为 identity（左右平移开启）— 属 `sliding_window` 小类，必拒（single_hung 竖向 up-slide 允许，左右滑动不允许）。
- 玻璃 / muntin / fixed-lite 漂浮（未 rebate、未 allow_overlap captured）。
- sash 在 q=0 不闭合 / 不 coplanar，或 open pose 自由边方向错（如 awning 顶缘动、hopper 底缘动）。
- joint origin 不在可见 hinge line 上（fixed_picture vent anchor 在不可见框顶薄面 → joint-origin 漂浮）。
- round_porthole 配 colonial 矩形 muntin 网格（应 radial/concentric only），或非圆轮廓裸 center-pivot。
- bank / triple multiplicity 扇相互穿模（无 mullion/transom 分隔），或所有 lite 都做可动 sash（应仅部分可动其余 fixed）。
- segmental / arched 弧头用 boxy 矩形近似（违反 threePointArc/lathe/arc 几何要求）。
- multiplicity N 超 envelope（unit_total_W > frame envelope，muntin cell 退化为 sliver），未 clamp / 投影 / 拒绝。
- frame 不站立（sill 不在 z≈0）、不高于 / 宽于单扇、深度 > 高度（躺倒）。

## 与相邻类别的边界

- 不该混入：**Sliding window（独立小类，已排除）** — 滑动 sash 左右平移是该小类 identity；本小类 Slot A 不含 sliding，single_hung 的竖向 PRISMATIC up-slide 是上下窗标准机构而非左右滑窗，不越界。
- 不该混入：**Door** — 门是落地（sill 至地面）人通行的整扇，铰在落地竖轴、无 glazed-sash-in-frame 的 sill-above-floor 立面窗台 + 多光分格语义；窗站在窗台之上、以采光分格 / 多扇 bank 为身份。
- 不该混入：**Curtain / Facade element（幕墙 / 立面构件）** — 幕墙是大面积无开启扇的固定玻璃格栅或装饰立面板；本小类必须至少有一个 category-defining 可动 sash（或 fixed_picture 的小 vent 翻板），且尺度为单窗而非整面立面。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；16/16 五星样本全读，每候选已解析真实 model.py:Lx-Ly；两条 multiplicity 轴 + 兼容矩阵 + palette 6 色已写；等待人工审核后再进入 TEMPLATE_AFTER_REVIEW。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | side_hung_casement / rectangular / no_muntin / single_1 | rec_side-hung-...4f1abc4d | L107-L279 | 基线机构 + 矩形框 + 单扇 + REVOLUTE z；fork 母体 |
| S2 | A/D | awning_top_hung / single | rec_aluminium-awning-...0b523c52 | L98-L222 | 顶铰横轴 REVOLUTE x（hopper fork 母体） |
| S3 | A | single_hung_vertical | rec_single-hung-...d91f35ac | L102-L265 | 上扇 FIXED + 下扇 PRISMATIC up-slide |
| S4 | B/A | round_porthole / center_pivot | rec_round-porthole-...30a4c378 | L81-L197 | lathe 圆环框 + 圆盘 sash center-pivot REVOLUTE x |
| S5 | A/D | side_hung / twin_double_2 | rec_double-casement-...039f0c0a | L106-L330 | 多腔框 + 两 mirror sash + hinge loop（triple fork 母体） |
| S6 | C/D | bank_grid / bank_3x2_6 | rec_bank-...478f6f0c | L99-L341 | col×row lite 网格 + 部分可动扇（bank fork 母体） |
| S7 | A/D | side_hung / twin_2 (venetian) | rec_twin-sash-...16e9934d | L104-L361 | 两 mirror sash + venetian slat loop |
| S8 | B/C | arched_top / radial_fan_15 | rec_arched-top-...6cbe185b | L132-L489 | 拱顶 + fanlight radial loop + 下扇 3×5 muntin + stone surround |
| S9 | A | awning_top_hung (steel, fixed lites) | rec_weathered-...steel...3dabb144 | L108-L252 | 工业钢 awning + 手写固定 lites（industrial_white_steel palette） |
| S10 | A | fixed_picture_light | rec_window_var_fixed_picture | L100-L298 | 主光 FIXED + trickle-vent 翻板 REVOLUTE x |
| S11 | A | hopper_bottom_hung | rec_window_var_hopper | L99-L224 | 底铰横轴 REVOLUTE x，顶缘内倾 |
| S12 | B | segmental_arch | rec_window_var_outline_segmental_arch | L127-L209 | 平底弧顶 `_arch_solid` frame + sash |
| S13 | C | colonial_2x2_4 | rec_window_var_muntin_grid_2x2 | L164-L248 | `_muntin_bar` helper + pane 嵌套 loop（4 格） |
| S14 | C | colonial_3x3_9 | rec_window_var_muntin_grid_3x3 | L176-L253 | 共享 `_muntin_bar`/`_glass_pane` + col×row loop（9 格） |
| S15 | D | triple_mullion_3 | rec_window_var_triple_mullion | L103-L344 | 单参数 NUM_SASHES 线性 loop + per-unit hinge policy |
| S16 | D | bank_2x2_4 | rec_window_var_bank_2x2 | L97-L313 | 2×2 网格 + 1 可动扇 3 fixed lite |

## 模板实现备注（可选）

- Slot C/D 的 muntin loop 与 bank loop 共享网格均分逻辑（`_lite_bounds` 风格 helper）；首版可各自实现，待第二个 multiplicity 模板出现再抽共享 helper（按 §multiplicity 注）。
- captured-pin / mount overlap 须 element-scoped allow_overlap：glass↔frame、hinge↔sash、pivot_pin↔(sash,frame)、sash_rail↔frame_head/sill、fixed_glass↔frame_web、muntin↔sash_frame、handle/stay↔sash。复合 multiplicity 时须对每个 `sash_{i}` / `fixed_glass_{col}_{row}` 重复声明（见 triple_mullion L361-391、bank L359-406）。
- round_porthole + center_pivot 与其余矩形机构 root coordinate 兼容（同 X-Z 立面），但其 C/D 强制 degenerate（no_muntin / single）；若 sweep 显示 porthole pivot-pin AABB 自转检查脆弱，按 regression override 记录（参 MEMORY knob-spin 教训：轴对称件 AABB 自转难判 → 用 off-axis pivot tab 或断言 Y-depth 增长而非 AABB 旋转）。
- fixed_picture vent flap 与 segmental 弧头是已知收敛风险：run_tests 须分别断言「主光 FIXED + 仅 1 个 vent REVOLUTE」（fixed_picture L384-448）与「frame 弧头非矩形顶 rail、crown 高于 spring line」（segmental L383-399）。
