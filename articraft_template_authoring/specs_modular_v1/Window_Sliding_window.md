# sliding_window — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `sliding_window` |
| template path | `agent/templates/Window_Sliding_window.py` |
| test path (optional) | `tests/agent/test_sliding_window_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：核心是 `parallel_children`（一个静态 `frame` root 上挂 N 个 panel，其中 S 个是可动 **PRISMATIC** sash、其余是 FIXED lite，叠加固定 muntin/glass parent visual），叠加 **两条 multiplicity 轴**（panel/sash 数 N、divided-light 网格 N）。orientation（A，horizontal ±X / vertical ±Z）与 sash_hardware（E）是固定 named-slot 选择轴，不复制。sliding_sash_count（C，S∈{1,2}）是 gating choice，决定 N 个 panel 中哪几个挂 PRISMATIC。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 93 |
| read_count | 93（3 parent 完整逐行读 model.py + 90 forks 按家族代表性抽样聚类全部 8 条结构变化轴，逐条回溯 model.py:Lx-Ly 证据） |
| read_scope | all 5-star samples in this category（3 distinct originals + 90 forks at rating 5；3 母体逐行全读，90 forks 按 3 家族 ×30 抽样 v01/v05/v10/v15/v20/v25/v30 + 发散点 spot-check，识别每条结构轴的 distinct value + 来源 id） |
| source_index_policy | only adopted module sources are indexed below |

要点（3 母体全读，90 forks 聚类）：

- **统一坐标系**：所有样本一致 — +Z 向上、宽沿 X、frame depth / 玻璃厚 / slide-normal 沿 Y、玻璃面在 X-Z 平面、sill 底约 z=0、窗站立。
- **统一根装配**：每个样本一个 **静态 root `frame`**，CadQuery「实心 slab 切出开口」做成真正周边 ring（two-panel 切单一大开口 L132-136；three-panel 切三 lite 开口留两 mullion L132-142；double-hung 切中央开口 + jamb side-track 槽 L100-140）。可动 sash 是独立 part 经 articulation 挂上去；固定 lite / muntin / glass / 五金一律 parent visual。
- **类别身份 = PRISMATIC 滑动**：sash 在 PRISMATIC 轴上的平移是 category-defining motion。horizontal（axis ±X，沿头/底 track）、vertical double-hung（axis ±Z，沿 jamb 竖轨）。**无任何 REVOLUTE swing sash**（区别 casement/awning/hopper，那属 `window` 小类）。唯一 REVOLUTE 是可选小五金（revolute_latch 拨杆，001_v25 `sash_to_latch` L350-358）。
- **proud-sash 错位合约**：可动滑扇必须 proud（+Y 偏移）于固定 lite/对扇，使其滑动时从前/后掠过而非互穿。two-panel FIXED_SASH_Y=-0.028 / SLIDE_SASH_Y=+0.044 L64-65；three-panel FIXED_LITE_Y=-0.020 / SLIDE_SASH_Y=+0.052 L71-72；double-hung LOWER_SASH_Y=-gap / UPPER_SASH_Y=+gap L63-65；横滑双滑 002_v10 rear/front Y 错位。
- **玻璃合约**：所有玻璃 rebate 在 sash/frame lip 下（REBATE≈0.005），靠 `allow_overlap(elem_a=glass, elem_b=vinyl/frame)` 声明 captured 而非漂浮；sash ring 搭 frame 开口 lip / track 也 element-scoped allow_overlap。
- **retained-insertion 合约**：sliding sash 在 full travel 仍 overlap 静态 frame（头/底 track 或 jamb 竖轨），`expect_overlap(sash, frame, axes=...)` 断言不脱轨（two-panel L415-418；three-panel L469-474；double-hung L436-453）。
- **multiplicity 母体**：muntin 网格（three-panel `for c in range(1,GRILLE_COLS)` + `for r in range(1,GRILLE_ROWS)` L172-191；double-hung 嵌套 `for ci in range(N_COLS): for ri in range(N_ROWS)` L182-193；fork 003_v15 2×3 / 001_v25 4×5 同型 loop）；panel 数（two/three-panel 沿 X bay、double-hung 沿 Z stack）。
- **手写 / 无 loop**：two-panel 母体单光无 muntin（无网格 loop，`_add_sash` 各调用一次）；五金（latch/lock/pull）单个手写 singleton（非复制子件，不触发 loop-emission 合约）。所有派生 grid multiplicity 变体均 fork 自已 PASS loop-emission 母体（three-panel / double-hung）。

## 核心身份

一扇 **滑动建筑窗**：一个静态外框（`frame` 周边 ring + 头/底 track 或 jamb 竖轨）容纳 N 个 panel，其中 **至少一个 panel 是经 PRISMATIC 滑轨开启的可动 sash（category-defining sliding motion）**，其余为 FIXED lite。成熟域 = 住宅 patio-slider（2 扇横滑）、3 扇横滑（XOX，中扇滑）、4 扇横滑（XOOX/OXXO）、vertical double-hung / single-hung（上下竖滑），矩形轮廓，可有 colonial muntin 分格、cam latch / sash lock / pull-cup / pull-handle 五金、roller block、insect screen 等真实硬件。

不该混入的相邻类别见 §与相邻类别的边界。**特别注意**：本小类 Slot A **仅 PRISMATIC 滑动**（horizontal ±X 或 vertical ±Z）；任何 REVOLUTE swing sash（侧铰 casement、顶铰 awning、底铰 hopper、center-pivot porthole）属 `window` 小类，不在此（避免出类目）。

## 槽位 + 候选模块表

### Slot A：orientation_drive（主滑动机构槽 — sash 平移方向 / PRISMATIC 轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| horizontal_slide（基线） | rec_two-panel-...5d4512bc | L127-L257 (frame 单开口 L127-136, `_build_sash_shape` L139-152, `_add_sash` L167-179, FIXED 左 L235-241, **PRISMATIC axis (-1,0,0)** L249-257) | eligible if compatible | sash 沿头/底 track 左右平移；FIXED lite 在后(FIXED_SASH_Y -0.028)，sliding sash proud +Y(SLIDE_SASH_Y +0.044)从前滑过；joint origin 在 seated center，axis ±X，upper≈one-sash-width |
| vertical_double_hung | rec_double-hung-...6c54f6e4 | L100-L321 (frame+jamb side-track L100-140, `_build_sash_frame_shape` L147-195, `_add_sash` L236-247, lower **PRISMATIC axis (0,0,1)** L298-308, upper **PRISMATIC axis (0,0,-1)** L311-321) | eligible if compatible | sash 沿 jamb 竖轨上下升降；两扇 offset Y 平面(LOWER -gap / UPPER +gap, SASH_Y_GAP 0.016)错开互不穿；meeting rail 重叠一 rail；lower 升 upper 降 |

降级说明：2 候选，无降级。滑窗仅此 2 个 category-defining 滑动方向（左右 / 上下）；每个改变 PRISMATIC 轴、root track primitive（头/底 track vs jamb 竖轨）、sash 局部坐标朝向 → 拓扑等价类。≥2 已过 slot 成立硬约束。

### Slot B：panel_layout（panel/sash 数多重度 — N panels 沿滑动轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| two_panel_2（1 fixed + 1 slide,基线） | rec_two-panel-...5d4512bc | L88-103 (SASH_OPENING_W = (INNER_W+MEETING_OVERLAP)/2) + L229-257 (fixed_sash FIXED + sliding_sash PRISMATIC) | eligible if compatible | 横滑 2 格，中央 meeting stile 重叠(MEETING_OVERLAP 0.040，无固定 mullion)；fixed 左 + slide 右 |
| three_panel_3（2 fixed + 1 center slide） | rec_three-panel-...860f2131 | L91-103 (三 lite + 两 mullion layout) + L256-297 (left/right_lite FIXED + center_sash PRISMATIC) | eligible if compatible | 横滑 3 格(XOX)，两侧固定 lite + 中扇滑，两 mullion(MULLION_FACE 0.060)分隔 |
| stacked_2（vertical double-hung 上下两扇） | rec_double-hung-...6c54f6e4 | L54-71 (SASH_H、LOWER/UPPER_BOTTOM_Z、MEETING_OVERLAP stack 布局) + L270-321 (lower/upper sash) | eligible if compatible | 竖向 2 扇沿 Z 堆叠，meeting rail 重叠一 rail(MEETING_OVERLAP=SASH_RAIL)；offset Y 平面 |
| four_panel_4（XOOX / OXXO bank） | rec_three-panel-...860f2131(母体,扩 NUM_PANELS=4) | L91-103 (lite/mullion layout 可参数化为 N) + L208-259 (`_add_lite` loop 化) | eligible if compatible (planned) | 横滑 4 格 + 3 mullion，外两固定、内两滑(OXXO) 或 XOOX；由 three-panel 母体线性 loop 扩 N |

降级说明：4 候选，无降级。distinct N 覆盖 {2, 3, 4, 2-stacked}。B 是 multiplicity 轴：横滑沿 X 用 mullion 分隔 bay，竖滑沿 Z stack。four_panel 由 three-panel 母体线性 loop 化扩 N（已 PASS loop-emission）。

### Slot C：sliding_sash_count（可动滑扇数 S∈{1,2}）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_slider_1（基线） | rec_two-panel-...5d4512bc / rec_three-panel-...860f2131 | two-panel L235-257 (1 FIXED + 1 PRISMATIC) / three-panel L268-297 (2 FIXED + 1 PRISMATIC) | eligible if compatible | N 个 panel 中仅 1 扇挂 PRISMATIC，其余 FIXED lite |
| dual_slider_2 | rec_double-hung-...6c54f6e4 (上下都动) / rec_qwen_sliding_window_002_v10 (横滑双滑) | double-hung L298-321 (lower axis(0,0,1) + upper axis(0,0,-1)) / 002_v10 L243-265 (rear axis(1,0,0) + front axis(-1,0,0)) | eligible if compatible | 两扇皆 PRISMATIC，**对向轴**；横滑 rear/front 对向 ±X，竖滑 lower/upper 对向 ±Z；两扇 offset Y 平面 |

降级说明：2 候选，无降级。C 是 gating choice（非连续复制轴）：决定 panel_layout 的 N 个 panel 中哪几个是 PRISMATIC sash、其余 FIXED。S=2 必须对向轴 + offset Y 平面（否则两滑扇互穿）。≥2 已过 slot 成立硬约束。

### Slot D：divided_light_grid（muntin 分格多重度 — N panes per sash）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| no_muntin（单光,N=1,基线） | rec_two-panel-...5d4512bc | L155-160 (`_build_sash_glass_shape` 单 pane，无 muntin) | eligible if compatible | 单整玻璃光，patio-slider 风；多数 2-panel 横滑采此 |
| colonial_3x2_6 | rec_double-hung-...6c54f6e4 | L73-76 (N_COLS=3,N_ROWS=2) + L182-193 (嵌套 lite 切格 loop) + L217-228 (pane 嵌套 loop) | eligible if compatible | 每扇 3×2=6 格；横宽格 |
| colonial_2x3_6（竖长格取向） | rec_qwen_sliding_window_003_v15 | L81-82 (N_COLS=2,N_ROWS=3) + L202-213 (嵌套切格 loop) + L237-248 (pane loop) | eligible if compatible | 每扇 2×3=6 格；竖长格(landscape 框) |
| colonial_3x3_9 | rec_qwen_sliding_window_001_v05 | GRILLE_COLS=3,GRILLE_ROWS=3 + 竖 muntin loop + 横 muntin loop（three-panel 型） | eligible if compatible | 每扇 3×3=9 格 |
| colonial_4x5_20 | rec_three-panel-...860f2131 / rec_qwen_sliding_window_001_v25 | L65-66 (GRILLE_COLS=4,GRILLE_ROWS=5) + L172-180 (竖 muntin `for c in range(1,GRILLE_COLS)`) + L183-191 (横 muntin `for r in range(1,GRILLE_ROWS)`) | eligible if compatible | 每扇 4×5=20 格 colonial 细网格 |

降级说明：5 候选（含 N=1 degenerate）。distinct N 覆盖 {1, 6, 9, 20}。D 是 multiplicity 轴：模板用规则网格 cols×rows loop 发射 muntin 条 + pane，N=cols×rows，per sash 复制。母体均 loop-emitted PASS。

### Slot E：sash_hardware（滑扇五金 — latch / lock / pull）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cam_latch（基线,静态） | rec_two-panel-...5d4512bc | L182-208 (`_add_latch`：Box keeper plate L194-199 + Cylinder thumb lever L203-208) | eligible if compatible | meeting stile 上 keeper plate + thumb-turn cam lever；静态 visual on sash |
| revolute_latch（可动小拨杆） | rec_qwen_sliding_window_001_v25 | L225 (`_build_latch_shape`) + L301 (latch part) + L350-358 (`sash_to_latch` REVOLUTE axis(0,0,1)) | eligible if compatible | center sash meeting rail 上可动 REVOLUTE 拨杆；唯一活动五金 |
| sash_lock（meeting rail cam lock,静态） | rec_double-hung-...6c54f6e4 | L82-83 (LOCK_BODY/LOCK_LEVER) + L279-290 (lower_sash_lock_body Box + lower_sash_lock_lever Box) | eligible if compatible | double-hung meeting rail 中央 cam-action sash lock；静态 visual |
| pull_cup（嵌入式凹杯,静态） | rec_qwen_sliding_window_003_v05 | `_build_pull_cup_shape`（环形 rim + back plate，下扇底 rail 圆凹杯 grip） | eligible if compatible | 下扇/滑扇底 rail 圆形嵌入凹杯 grip |
| pull_handle（meeting stile 立把手,静态） | rec_qwen_sliding_window_003_v15 | L85-86 (HANDLE_BODY/HANDLE_GRIP) + Box 立把手 | eligible if compatible | sliding sash meeting stile 立面把手 bar，mid-height |

降级说明：5 候选，无降级。每个改变 sash 上五金 part 的 primitive/joint 语义（cam_latch=Box+Cyl 静态，revolute_latch=多一个 REVOLUTE joint，sash_lock=双 Box 静态，pull_cup=环形凹杯，pull_handle=Box bar）。仅 revolute_latch 增 joint topology（其余静态 visual），故 E 改变 part tree / joint count → 拓扑等价类。

## 槽位图（slot graph）

pattern: mixed（parallel_children 固定 named slots + 两条 multiplicity 轴 + sliding-count gating）

```
                     orientation_drive (Slot A)
                            │ 决定 root track primitive（头/底 track ±X  /  jamb 竖轨 ±Z）+ sash PRISMATIC 轴
                            ▼
   [root: frame] ──parent visual──> {fixed glass, fixed lite(s), muntin grid (Slot D),
       (静态 root part)               head/sill track / jamb side-track (Slot A),
                                      mullion(横滑 N≥3) }
       │
       │  per panel p (Slot B, multiplicity N_B)  ×  sliding gate (Slot C, S∈{1,2})
       │    ├─[PRISMATIC axis(A) + retained-insertion track]─> sash_{p}（可动,共 S 个,proud +Y）
       │    │        └─ sash_{p} 内含 Slot D muntin grid（随 sash 滑动，无独立 joint）
       │    │        └─ sash_{p} 内含 Slot E 五金（cam_latch/sash_lock/pull = parent visual；
       │    │                                       revolute_latch = 多一 REVOLUTE sash_to_latch）
       │    └─ 其余 panel = fixed_lite_{p}（FIXED-as-visual，挂 root，不动，rear -Y）
```

机构（Slot A）决定每个可动 sash 的 joint type / axis / origin / limits：

- **horizontal_slide**：interface = sash 顶/底 rail tuck 进 frame 头/底 track（retained insertion）。joint = PRISMATIC，axis (±1,0,0)，origin 在 seated（closed）center (SLIDE_OPEN_CX, SLIDE_SASH_Y, MID_CZ)，lower=0 upper≈one-sash-opening-width×0.9。sliding sash proud +Y 从前掠过 fixed lite。源：two-panel L249-257 / three-panel L289-297。
- **vertical_double_hung**：interface = sash stile 在 jamb 内侧 side-track 槽（retained insertion）。lower joint = PRISMATIC，axis (0,0,1)，origin (0, LOWER_SASH_Y, LOWER_BOTTOM_Z)，upper=SASH_H×0.42（升）；upper joint = PRISMATIC，axis (0,0,-1)，origin (0, UPPER_SASH_Y, UPPER_BOTTOM_Z)，upper=SASH_H×0.42（降）。两扇 offset Y 平面错开。源：double-hung L298-321。

互斥 / 派生关系：
- Slot C dual_slider_2 + horizontal_slide → rear/front 两扇 **对向 ±X 轴** + offset Y（002_v10）。
- Slot C dual_slider_2 + vertical_double_hung → lower/upper 两扇 **对向 ±Z 轴** + offset Y（double-hung parent）。
- vertical_double_hung → panel_layout 限 stacked_2（竖滑天然 2 扇堆叠，不进 horizontal 的 three/four_panel）。
- horizontal_slide → panel_layout ∈ {two_panel, three_panel, four_panel}。
- revolute_latch（Slot E）→ 必 anchor 在可动 sash meeting rail 实体面（多一 REVOLUTE joint）；其余五金为静态 parent visual。

## 每槽位 Module Emits / Interfaces

### Slot A / module horizontal_slide
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_sash`（可动,proud +Y）；root `frame_shell`(含头/底 track) + FIXED `fixed_sash`/`*_lite` | two-panel / model.py:L221-232 |
| internal joints | 无（sash 内五金随 sash） | — |
| upstream interface | sash 顶/底 rail tuck 进 frame 头/底 track（retained insertion，`expect_overlap` axes=z） | two-panel / model.py:L284-297, L415-418 |
| downstream interface | PRISMATIC axis (±1,0,0) origin (SLIDE_OPEN_CX, SLIDE_SASH_Y, MID_CZ)，upper≈sash_w×0.9 | two-panel / model.py:L249-257 |
| parent visual on sash | `{name}_vinyl`/`{name}_glass` + Slot D muntin + Slot E 五金 | two-panel / model.py:L167-208 |

### Slot A / module vertical_double_hung
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_sash`(PRISMATIC +Z)、`upper_sash`(PRISMATIC -Z)；root `frame_shell`(含 jamb side-track) | double-hung / model.py:L262-272 |
| internal joints | lower PRISMATIC + upper PRISMATIC（对向轴） | double-hung / model.py:L298-321 |
| upstream interface | sash stile 在 jamb 内侧 side-track 槽（`allow_overlap` frame↔sash）；两扇 offset Y 平面 | double-hung / model.py:L127-140, L349-356 |
| downstream interface | lower axis (0,0,1) origin (0,LOWER_SASH_Y,LOWER_BOTTOM_Z)；upper axis (0,0,-1) origin (0,UPPER_SASH_Y,UPPER_BOTTOM_Z)，各 upper=SASH_H×0.42 | double-hung / model.py:L298-321 |
| parent visual on sash | `{name}_frame`/`{name}_glass` + Slot D muntin + Slot E sash_lock | double-hung / model.py:L236-290 |

### Slot B / panel_layout emits（multiplicity 复制 panel 单元）
| emits | 描述 | 来源 |
|---|---|---|
| panel parts | `sash_{p}`（可动 S 个）/ `fixed_lite_{p}`（FIXED 其余）；横滑 N bay / 竖滑 2 stack | three-panel L257-259, L268-297 / double-hung L270-321 |
| mullion | 横滑 N≥3 的 mullion（frame slab 切多开口残留） | three-panel / model.py:L91-142 |
| per-panel joints | S 个 PRISMATIC（Slot A 轴）+ 余 FIXED；S 由 Slot C gate | three-panel / model.py:L268-297 |

### Slot D / divided_light_grid emits（sash 内 parent visual，随 sash 滑动）
| emits | 描述 | 来源 |
|---|---|---|
| muntin bars | 竖 `for c in range(1,cols)` + 横 `for r in range(1,rows)`（three-panel 型）或嵌套 `for ci/for ri` 切格（double-hung 型） | three-panel L172-191 / double-hung L182-193 |
| panes | `{sash}_pane_{ci}_{ri}` 嵌套 col×row loop 发射 | double-hung / model.py:L217-228 |
| internal joints / interface | 无独立 joint；muntin/pane 随所属 sash 的 PRISMATIC（或随 root 的 fixed lite） | — |

### Slot E / sash_hardware emits（sash 上五金）
| emits | 描述 | 来源 |
|---|---|---|
| cam_latch | `{sash}_latch_plate`(Box) + `{sash}_latch_lever`(Cylinder)，meeting stile 静态 | two-panel / model.py:L182-208 |
| revolute_latch | `latch_body` part + `sash_to_latch`(REVOLUTE axis(0,0,1)) | 001_v25 / model.py:L225, L350-358 |
| sash_lock | `{sash}_lock_body`(Box) + `{sash}_lock_lever`(Box)，meeting rail 静态 | double-hung / model.py:L279-290 |
| pull_cup | 环形 rim + back plate，底 rail 凹杯静态 | 003_v05 / model.py:`_build_pull_cup_shape` |
| pull_handle | HANDLE_BODY/GRIP Box，meeting stile 立把手静态 | 003_v15 / model.py:L85-86 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| orientation_drive | enum | horizontal_slide / vertical_double_hung | — | choice | 由 deterministic procedural sampler 选择；决定 PRISMATIC 轴 + track primitive + Slot B gating | Slot A table |
| panel_layout | enum | two_panel_2 / three_panel_3 / four_panel_4 / stacked_2 | — | choice | conditional：horizontal ⇒ {two/three/four}；vertical ⇒ stacked_2 | Slot B table |
| sliding_sash_count | enum | single_slider_1 / dual_slider_2 | — | choice | conditional：S≤N_panel；S=2 强制对向轴 + offset Y | Slot C table |
| divided_light_grid | enum | no_muntin / colonial_3x2 / colonial_2x3 / colonial_3x3 / colonial_4x5 | — | choice | conditional：受 cell-size inequality 约束 | Slot D table |
| sash_hardware | enum | cam_latch / revolute_latch / sash_lock / pull_cup / pull_handle | — | choice | conditional：revolute_latch 增 REVOLUTE joint；其余静态 visual | Slot E table |
| muntin_cols | int (count_param D) | [1, 5]（产品全程；测试偏小，见 §multiplicity） | 1 | independent | 加权采样；与 muntin_rows 共同给出 N=cols×rows | three-panel GRILLE_COLS / double-hung N_COLS |
| muntin_rows | int (count_param D) | [1, 6] | 1 | independent | 同上 | three-panel GRILLE_ROWS / double-hung N_ROWS |
| panel_count | int (count_param B) | [2, 6]（horizontal）；vertical 固定 2 stacked | 2 | conditional | linear bay 数（横滑）；竖滑固定 2 | three-panel lite-count / four_panel |
| win_width_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 TOTAL_W / WIN_W / LITE_W 等宽度尺度 | 各 frame TOTAL_W/WIN_W |
| win_height_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 TOTAL_H / WIN_H / SASH_H | 各 frame TOTAL_H/WIN_H |
| frame_face_scale | float | [0.8, 1.3] | 1.0 | independent | clamp；缩放 FRAME_FACE / MULLION_FACE | 各 frame FRAME_FACE |
| sash_open_frac | float | [0.0, 1.0] | 0.0 | independent | 映射 joint q（rest 闭合）；× motion_limits.upper | 各机构 motion_limits |
| palette_style | enum | white_vinyl / brushed_aluminium / anodized_aluminium_dark / black_aluminium / warm_wood / bronze_aluminium | white_vinyl | choice | 每 seed 抽一组 (frame/sash/glass/hardware) rgba；不改拓扑 | 见下 palette 来源 |
| (—) | constraint | — | — | inequality | `Σ panel_bay_W + (N-1)·MULLION_FACE + 2·FRAME_FACE = TOTAL_W`（横滑）；超 envelope 时按比例回缩 panel_bay_W 或拒绝重采 | three-panel L233-239 assert |
| (—) | constraint | — | — | inequality | `muntin grid cell_w/cell_h ≥ MIN_CELL(≈0.05)`；cols×rows 过大时下调 N 或拒绝 | double-hung INNER/N_COLS 推导 |
| (—) | constraint | — | — | inequality | `proud sash Y gap ≥ SASH_DEPTH`：S=2 两滑扇 / sliding↔fixed 必须 offset Y ≥ 一 sash 深，否则滑动互穿，回缩或拒绝 | two-panel L64-70 / double-hung L63-65 |
| (—) | constraint | — | — | inequality | `sash retained at full travel`：travel ≤ panel_opening_W（横滑）/ SASH_H×0.45（竖滑），sash AABB 不出 frame X/Z span | two-panel L408-414 / double-hung L426 |

palette_style 来源（≥3，目标 4-6，全部观测自 5★ 源）：
- **white_vinyl**：VINYL (0.94,0.95,0.96,1.0) / GLASS (0.52,0.60,0.66,0.30) / METAL latch (0.74,0.76,0.79) — two-panel L109-110, L81。
- **brushed_aluminium**：ALUMINUM (0.72,0.74,0.76,1.0) / GLASS (0.50,0.58,0.64,0.32) / track liner (0.30,0.32,0.35) — 001_v25 L110-111。
- **anodized_aluminium_dark**：FRAME (0.68,0.71,0.74,1.0) / SASH (0.72,0.75,0.78,1.0) / GLASS (0.26,0.32,0.38,0.32) dark tint / HANDLE (0.22,0.23,0.25) — 003_v15 L92-95。
- **white_painted_frame**：FRAME (0.945,0.945,0.945,1.0) / SASH (0.965,0.965,0.965,1.0) / GLASS (0.30,0.36,0.42,0.34) dark-tint / LOCK (0.86,0.87,0.89) — double-hung L90-93。
- **anodized_aluminium_blue**：FRAME (0.68,0.71,0.74,1.0) / SASH (0.72,0.75,0.78,1.0) / GLASS (0.28,0.34,0.40,0.32) / handle dark — 003_v05 L89-91。
- **bronze_aluminium**（warm 派生，frame 偏暖灰金）：FRAME (0.46,0.40,0.32,1.0) / SASH (0.50,0.44,0.36,1.0) / GLASS (0.40,0.42,0.40,0.32) / handle (0.30,0.27,0.22) — 由 003 anodized 家族暖偏移派生（人工审核确认色值）。

连续尺寸采样契约：先采 independent 主尺度（win_width_scale / win_height_scale / frame_face_scale，均匀采样后 clamp）→ 按 equation 派生从属（sash 尺寸 = opening − clearance；panel_bay_W = (inner − mullions)/N）→ 用 inequality 把 panel_total / muntin cell / proud-Y-gap / retained-travel 投影回缩或拒绝重采 → conditional 范围（panel_count 仅 horizontal；S≤N）在采样前按 Slot A/B/C choice 解析。

## Multiplicity / Copy Logic

**两条独立 multiplicity 轴**（per-axis 各做一次加权采样，各自 clamp，各自 sweep 上限）：

### 轴 D — divided_light_grid（muntin 分格）
- `count_param`：`(muntin_cols, muntin_rows)`，N_D = muntin_cols × muntin_rows。
- `N_range`（本轴产品域）：cols ∈ [1,5]、rows ∈ [1,6]，N_D ∈ [1, 30]。样本已覆盖 distinct {1, 6, 9, 20}。
- sampling domain（权重档）：N_D=1（no_muntin）高频（patio-slider 多单光）；3×2 / 2×3 / 3×3 中频；4×5 及以上稀有尾部下调。测试偏小（cols,rows ≤ 3），产品全程但大 N 稀疏采样 + cell-size inequality 兜底。
- copied object：sash 内框均分网格的 muntin 条（竖 loop `for c in range(1,cols)` + 横 loop `for r in range(1,rows)`）+ 对应玻璃格（嵌套 `for ci in range(cols): for ri in range(rows)`），per sash 复制。
- naming：`{sash}_vmuntin_{i}` / `{sash}_hmuntin_{i}` + `{sash}_pane_{ci}_{ri}`。
- placement：sash 内框（in_x0..in_x1 × in_z0..in_z1）规则均分网格，cell_w/cell_h 派生。
- joint policy：muntin 与 pane 随所属 sash 的 PRISMATIC（fixed lite 网格随 root，FIXED-as-visual），无独立 joint。
- source/gating：母体 three-panel（GRILLE_COLS×GRILLE_ROWS loop L172-191）、double-hung（嵌套 N_COLS×N_ROWS loop L182-193），均已 PASS loop-emission。

### 轴 B — panel_layout（panel/sash 数）
- `count_param`：horizontal 模式 `panel_count`（N bay 沿 X）；vertical 模式固定 2 stacked。
- `N_range`（本轴产品域）：horizontal panel_count ∈ [2, 6]；vertical 固定 2。样本已覆盖 distinct {2, 3, 4, 2-stacked}。
- sampling domain（权重档）：N=2（two-panel patio）高频；3（XOX）中频；4（XOOX/OXXO）中低频；>4 稀有尾部下调（住宅滑窗少见多扇 bank）。
- copied object：每 panel 的 sash/lite 框 + 玻璃 + muntin（轴 D）+（若滑）五金（轴 E）；横滑额外发射 mullion 分隔。
- naming：横滑 `sash_{p}`（可动）/ `fixed_lite_{p}`（固定）+ `mullion_{m}`；竖滑 `lower_sash`/`upper_sash`。
- placement：横滑沿 X 规则偏移（panel_bay_W 均分，mullion 分隔）；竖滑沿 Z stack（meeting rail 重叠）。
- joint policy：S 个 panel 挂 PRISMATIC（Slot A 轴，S=2 对向轴），其余 FIXED lite；S 由 Slot C gate（S≤N）。
- source/gating：横滑母体 three-panel（线性扩 N，loop 化 `_add_lite`）；竖滑母体 double-hung（固定 2 stack）。均已 PASS loop-emission。

机构（Slot A orientation）与五金（Slot E）为固定 named slot，**非复制轴**（不暴露 `*_count`，不循环复制模板级机构 / 五金；五金是 singleton）。Slot C sliding_sash_count 是 gating choice（非连续 N，仅 1/2）。

## 拓扑多样性审计

总组合数（slot 笛卡尔，未含连续 N）：A × B × C × D × E = 2 × 4 × 2 × 5 × 5 = **400**（conditional gating 后合法组合约 ~200，仍远超机械门槛；即便仅 A×B×C = 16 ≥ 10 已单独过闸）。
把 multiplicity N 计入：D distinct N {1,6,9,20,...} + B distinct N {2,3,4,...} 远超机械门槛。

理由：仅 A×B×C（机构 × panel 数 × sliding 数）已给 ~12 个 gating 后合法的拓扑不同组合（每个改变 PRISMATIC 轴数 / part tree / joint count）；叠加 D、E 后 1000-seed slot choice tuple distinct 预计按 ≥300 富类别口径观察（每个 (A, N_B, S, N_D, E) 在 part/joint count 上都是不同 equivalence class，revolute_latch 还额外加一个 REVOLUTE joint 维度）。

seed_domain_policy：procedural_first（`seed=0` 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 先抽 Slot A orientation（决定 track primitive + Slot B/C gating），再抽 panel_layout（horizontal⇒{2,3,4}/vertical⇒stacked），再抽 sliding_sash_count S（gate S≤N），再加权抽 D 的 muntin N（小 N 偏多、大 N 尾部下调），再抽 E 五金，最后采连续 scale 并 clamp / 投影回可行域。compatibility matrix 在 `resolve_config` 内 gating 排除非法组合（见下）。少量 regression overrides 仅用于已知失败回归（dual_slider 两扇 Y 互穿、revolute_latch anchor 漂浮、panel_4 mullion 穿模）。random sweep：seeds 0-49 初轮、0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only），本类别 A×B×C×D×E 组合空间足够支撑。
Controlled local parameterization：win_width_scale [0.85,1.20]、win_height_scale [0.85,1.20]、frame_face_scale [0.8,1.3]、sash_open_frac [0,1]（映射 joint q）。全部在 `resolve_config` clamp / 派生：sash 尺寸 = opening − clearance（equation）；panel_bay_W、muntin cell-size、proud-Y-gap、retained-travel 用 inequality 投影回缩或拒绝。这些 scale 不改变拓扑等价类、不破坏 InterfaceSpec（PRISMATIC track / jamb side-track / proud-Y offset）/ MatingContract / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽序 A→B(gated by A)→C(gated S≤N)→D(加权 N)→E→连续 scale；slot_choices_for_seed 仅记录改变拓扑等价类的 enum 与 N（含 S、revolute_latch 增 joint） | slot_choices_for_seed matches build choices |
| compatibility matrix | vertical_double_hung ⇒ panel_layout=stacked_2、S∈{1,2}（lower-only 或 both）；horizontal_slide ⇒ panel ∈ {two/three/four}；S=2 ⇒ 对向轴 + offset Y ≥ sash_depth（横滑 rear/front ±X、竖滑 lower/upper ±Z）；S ≤ N_panel；revolute_latch 仅装可动 sash meeting rail 实体面（非薄不可见面）；no_muntin 与所有 panel 兼容，colonial_4x5 仅当 panel_opening 足够大（cell-size inequality） | no floating, collision, axis, max multiplicity, bulky module, optional child failures |
| controlled local variation | win_width/height_scale、frame_face_scale、sash_open_frac，全部 clamp + 派生 sash/opening/cell/bay，违反 inequality 投影回缩 | proportions vary without breaking PRISMATIC track / proud-Y offset / clearance / joint origin / identity |
| regression overrides | none（首版）/ 仅 dual_slider Y 互穿、revolute_latch anchor 漂浮、panel_4 mullion 穿模、retained-insertion 脱轨（如出现）按 seed 记录原因 | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A orientation_drive | 2 | yes | no | horizontal_slide / vertical_double_hung（滑窗仅此 2 滑动方向，结构互斥 root track；降级理由见 Slot A） |
| B panel_layout | 4 | yes | yes | two/three/four_panel/stacked_2（multiplicity 轴 distinct N {2,3,4,2-stacked}） |
| C sliding_sash_count | 2 | yes | no | single_slider/dual_slider（S∈{1,2} gating choice；S=2 对向轴；降级理由见 Slot C） |
| D divided_light_grid | 5 | yes | yes | no_muntin/3x2/2x3/3x3/4x5（multiplicity 轴 distinct N {1,6,9,20}） |
| E sash_hardware | 5 | yes | yes | cam_latch/revolute_latch/sash_lock/pull_cup/pull_handle |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D/E enum + 改变拓扑的 N + revolute_latch joint 标记）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（`seed=0` 不特殊）
- compatibility matrix / gating prevents illegal module combinations（vertical↔stacked；horizontal↔{2,3,4}；S≤N；S=2 对向轴 + offset Y；revolute_latch 仅可动 sash 实体面）
- optional regression overrides are sparse and justified（仅 dual-slider Y 互穿 / revolute_latch anchor / panel_4 mullion / retained 脱轨 已知风险）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (win_width/height_scale, frame_face_scale, sash_open_frac) are clamped and cannot break PRISMATIC track / jamb side-track / proud-Y offset / clearance / joint origin / multiplicity
- cross-part scale dependencies (sash=opening−clearance equation；panel_total / cell-size / proud-Y-gap / retained-travel inequality；panel_count/S conditional) resolved in `resolve_config`, not in builder
- critical InterfaceSpec / MatingContract points exist：head/sill PRISMATIC track（横滑）、jamb side-track 槽（竖滑）、proud-Y offset gap、mullion 分隔（横滑 N≥3）、meeting-rail 五金 mount
- key joints have expected type/axis/range：horizontal sliding sash PRISMATIC axis (±1,0,0)；vertical lower PRISMATIC (0,0,1) + upper PRISMATIC (0,0,-1)；revolute_latch REVOLUTE (0,0,1)；fixed lite FIXED；**无任何 swing REVOLUTE sash**
- copied objects follow naming and placement policy：`sash_{p}`/`fixed_lite_{p}`/`mullion_{m}`/`{sash}_pane_{ci}_{ri}`/`{sash}_vmuntin_{i}`/`{sash}_hmuntin_{i}`
- 每个可动滑扇 rest pose（q=0）闭合、coplanar；open pose 沿 PRISMATIC 轴平移（横滑 ±X / 竖滑 ±Z），full travel 仍 retained（overlap frame track，不脱轨）；纯平移无垂直轴漂移

## Reject cases

- swing sash 作为 identity（侧铰 / 顶铰 / 底铰 / center-pivot REVOLUTE 开启）— 属 `window` 小类，必拒（本小类仅 PRISMATIC 滑动）。
- 玻璃 / muntin / fixed-lite / 五金漂浮（未 rebate、未 allow_overlap captured）。
- sliding sash 在 q=0 不闭合 / 不 coplanar，或 open pose 平移轴错（横滑沿 Z 漂、竖滑沿 X 漂）。
- dual_slider 两滑扇 Y 平面未 offset（≥ sash_depth）→ 滑动时 sash ring 互穿；或 S=2 同向轴（应对向）。
- sliding sash full travel 脱轨（AABB 出 frame X/Z span，不再 overlap 头/底 track 或 jamb 竖轨）。
- revolute_latch anchor 在不可见薄面（非可动 sash meeting rail 实体面）→ joint-origin 漂浮；或把静态五金错配 joint。
- 横滑 panel N≥3 相邻滑扇 / 滑扇↔固定 lite 无 mullion 分隔而穿模；或 vertical 强配 three/four_panel（应仅 stacked_2）。
- muntin N 超 envelope（cell 退化为 sliver，cell_w/cell_h < MIN_CELL），未 clamp / 投影 / 拒绝。
- frame 不站立（sill 不在 z≈0）、不高于 / 宽于单扇、深度 > 高度（躺倒）。

## 与相邻类别的边界

- 不该混入：**Window（普通窗 / casement / awning / hopper / porthole）** — 那些是 REVOLUTE swing sash（侧铰立轴、顶/底铰横轴、center-pivot）；本小类仅 PRISMATIC 滑动 sash（横滑 ±X / 竖滑 ±Z）。single-hung / double-hung 的竖向 PRISMATIC up/down-slide 属本小类（上下滑窗），左右滑同属本小类。
- 不该混入：**Sliding door** — 门落地（sill 至地面）、人通行整扇、铰/滑在落地平面、无窗台之上立面 + 无多光分格 bank + 无 glazed-sash-in-frame 上窗台语义；窗站在窗台之上、以采光分格 / 多扇 bank / 小尺度单窗为身份。sliding_door 整扇玻璃门板尺度远大、底缘落地。
- 不该混入：**Curtain wall / Facade element（幕墙 / 立面构件）** — 幕墙是大面积无开启扇的固定玻璃格栅；本小类必须至少一个 category-defining 可动 PRISMATIC sliding sash，且尺度为单窗而非整面立面。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；93/93 五星样本（3 母体逐行全读 + 90 forks 聚类全 8 轴）已读，每候选解析真实 model.py:Lx-Ly；orientation(2)/panel_layout(4)/sliding_count(2)/grid(5)/hardware(5) 五槽 + 两条 multiplicity 轴 + sliding-count gating + compatibility matrix + palette 6 色已写；total combos 400（gated ~200），可过（理由见审计）；A、C 仅 2 候选已附结构互斥降级理由。等待人工审核后再进入 TEMPLATE_AFTER_REVIEW。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | horizontal_slide / two_panel_2 / single_slider / no_muntin / cam_latch | rec_two-panel-...5d4512bc | L88-L257 | 横滑基线母体：1 FIXED + 1 PRISMATIC(±X) + proud-Y + cam latch + retained-insertion |
| S2 | A/B/D | horizontal_slide / three_panel_3 / colonial_4x5_20 | rec_three-panel-...860f2131 | L91-L297 | 横滑 3 扇(XOX) + 中扇滑 + GRILLE_COLS×GRILLE_ROWS muntin loop（grid + panel multiplicity 母体） |
| S3 | A/B/C/D/E | vertical_double_hung / stacked_2 / dual_slider / colonial_3x2_6 / sash_lock | rec_double-hung-...6c54f6e4 | L54-L321 | 竖滑母体：lower/upper 对向 PRISMATIC(±Z) + jamb side-track + 嵌套 N_COLS×N_ROWS muntin loop + sash_lock（dual_slider + grid 母体） |
| S4 | C/E | dual_slider_2(horizontal) / cam_latch + roller | rec_qwen_sliding_window_002_v10 | L243-265 (rear axis(1,0,0) + front axis(-1,0,0)) + roller `_add_rollers` L274-289 | 横滑双滑对向轴 + roller block 对 loop |
| S5 | D/E | colonial_4x5_20 / revolute_latch | rec_qwen_sliding_window_001_v25 | L65-66, L172-191 (4×5 muntin loop) + L225, L350-358 (`sash_to_latch` REVOLUTE) | 4×5 细网格 + 可动 REVOLUTE 拨杆（唯一活动五金） |
| S6 | D/E | colonial_2x3_6 / pull_handle | rec_qwen_sliding_window_003_v15 | L81-82, L202-213 (2×3 muntin loop) + L85-86 (HANDLE_BODY/GRIP) | 2×3 竖长格网格 + 立面 pull handle |
| S7 | D/E | colonial_3x3_9 / pull_cup | rec_qwen_sliding_window_001_v05, rec_qwen_sliding_window_003_v05 | 3×3 GRILLE loop / `_build_pull_cup_shape` 环形凹杯 | 3×3 网格 + 嵌入式凹杯 grip |

## 模板实现备注（可选）

- Slot D muntin loop 与 Slot B panel loop 共享网格均分逻辑（`_lite_bounds` 风格 helper）；首版可各自实现，待第二个 multiplicity 模板出现再抽共享 helper。
- captured-pin / mount overlap 须 element-scoped allow_overlap：glass↔vinyl/frame、sash_ring↔frame 开口 lip、sash_rail↔head/sill track、stile↔jamb side-track、muntin↔sash_frame、latch/lock/pull↔sash、roller↔sash。复合 multiplicity 时须对每个 `sash_{p}` / `{sash}_pane_{ci}_{ri}` 重复声明（参 three-panel L317-368、double-hung L341-368）。
- **proud-Y offset 是滑窗核心收敛点**：sliding sash 与 fixed lite（及 dual_slider 两滑扇）必须 offset Y ≥ sash_depth（two-panel ~12mm L66-70 / three-panel ~17mm L73-75 / double-hung SASH_Y_GAP×2=32mm L63-65），否则滑动 sweep 时 sash ring 互穿。run_tests 须断言「sliding sash proud of fixed」+「dual sliders 在 offset Y 平面」（参 two-panel L346-353、double-hung L411-418）。
- **retained-insertion 是第二收敛点**：full travel 时 `expect_overlap(sliding_sash, frame, axes=z（横滑）/x（竖滑）)` + sash AABB 不出 frame span，断言不脱轨（two-panel L408-418、three-panel L463-474、double-hung L436-453）。
- dual_slider 与 revolute_latch 是已知收敛风险：run_tests 须分别断言「两滑扇对向轴 + offset Y 不互穿」与「revolute_latch joint type=REVOLUTE + anchor 在 sash 实体 meeting rail」（参 001_v25 L501）；panel_4 须断言相邻滑扇有 mullion 分隔不穿模。
