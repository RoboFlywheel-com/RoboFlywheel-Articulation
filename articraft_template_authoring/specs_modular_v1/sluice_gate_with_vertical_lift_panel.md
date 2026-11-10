# Sluice Gate With Vertical Lift Panel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `sluice_gate_with_vertical_lift_panel` |
| template path | `agent/templates/sluice_gate_with_vertical_lift_panel.py` |
| test path (optional) | `tests/agent/test_sluice_gate_with_vertical_lift_panel_template.py` — 可选回归网，默认被 pytest 排除；验收以 compile-sweep 为准 |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（身份链 frame → lift_panel 单 PRISMATIC + 并列 hoist(CONTINUOUS) + 并列 gated child(REVOLUTE)；hoist 可经 FIXED 中间件 operator_housing） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 28 |
| read_count | 28 |
| read_scope | all 5-star samples in this category（按 part/articulation 层 grep + 关键 10 个按行级精读）|
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 17（结构与 S1-S11 同族，仅作为多样性交叉验证）|
| source_index_policy | 仅索引被采纳为某 slot candidate 来源的样本；rib/guide-bar/sill apron/sill seat 等不动装饰一律 visual，不拆 FIXED 装饰 part；guide_rail 当且仅当样本里是独立 FIXED part 时才进 frame 候选的 separate_rails 分支 |

## 核心身份
水利/灌溉/管道入口处的 **vertical-lift sluice gate**（也叫立式闸门）：一块 root `frame`（带 sill 底槛 + 两侧 pier/post + 顶 lintel/top_cap + 嵌入或外挂的 side guide channels）作为不动基座；一块沿 `(0,0,1)` 方向 **PRISMATIC 升降** 的 `lift_panel`（gate leaf，可能是平板、加肋板或带 profile 的成型板）在两侧 guide 内上下滑动；顶部装一台 CONTINUOUS 旋转的 `handwheel` / `crank_wheel`（可能经独立 FIXED `operator_housing` / `gearbox` / `operator_box` 转一层支座，或直接落到 frame 上），代表人手操作的提升输入；另带一个并列的 gated REVOLUTE 第二件（locking pawl、ratchet latch、inspection door/hatch、gearbox cover），是绝大多数 5 星样本都会出现的安全/检修件。身份恒为 **frame + lift_panel + 恰好一个 PRISMATIC 主升降关节（轴 (0,0,1)、行程 0.15-2.3m）** + **恰好一个 CONTINUOUS hoist 关节** + **一到两个 FIXED 装配关节**；可选 + 1 个 gated REVOLUTE 第二自由度。

边界（不该混入的相邻类别）：

- 不是 `singleleaf_drawbridge` 或 `barrier_gate`：本类 leaf 沿 **PRISMATIC 垂直平移** 升降，不绕水平铰 REVOLUTE 翻起。
- 不是 `revolving_door` / `radial_sector_gate`：本类不绕竖直轴旋转开关，扇形闸/弧形闸（绕水平轴 REVOLUTE 转出水路）属于不同类别。
- 不是 `sliding_window` / `display_freezer_with_sliding_glass_lids`：本类是带 hoist 机械传动的水工/工业闸；纯居家滑动窗/玻璃推拉门没有 handwheel/crank、没有 sill seat、没有 pier 立柱。
- 不是 `paper_cutter_guillotine` / `lever_press`：本类不是 REVOLUTE 砍/压杠杆，是直线 PRISMATIC 升降。
- 不是裸 `single_revolute_hinge`：本类的固定半永远是带 sill + 双侧 guide 的 frame。
- frame 上的 pier/sill/top_cap/seal_strip/embedded guide channel/印刷标尺/铭牌 在 baked 形态下都是 ornament `frame.visual(...)`，按 Rule 1 不拆 FIXED 装饰 part；仅当样本明确把 `guide_rail` 写成独立 `model.part(...)` + FIXED 装配时，才作为 Slot1 的 `separate_rails` 分支被允许。

## 采用源码索引（Adopted Source Index）

| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_sluice_gate_with_vertical_lift_panel_04a1da71b14c4b38a91dddff13b54326` | `data/records/rec_sluice_gate_with_vertical_lift_panel_04a1da71b14c4b38a91dddff13b54326/revisions/rev_000001/model.py:L97-L385` | 完整 7-part 范本：concrete 2-pier frame(piers+sill+top_cap+seats+head_seat) + **separate** `guide_0/1` FIXED rails(`_add_guide_rail` helper L45-L83) + ribbed lift_plate(leaf+bottom_edge+2 edge_bar+3 stiffener+yoke) + operator_housing(crossbeam+gearbox+bonnet+wheel_support+shaft_boss+pawl_bracket+pawl_bridge+service_box) + 3-spoke handwheel(`_handwheel_rim_mesh` L30-L43, rim+hub+shaft+3 spokes+grip) + locking_pawl(barrel+root+arm+tooth+neck+handle)；6 articulations：2×FIXED guide_mount + PRISMATIC plate_lift `(0,0,1)` `[0,1.85]` + FIXED housing_mount + CONTINUOUS handwheel_spin `(0,1,0)` + REVOLUTE pawl_pivot `(0,1,0)` `[-0.65, 0.45]` |
| S2 | `rec_sluice_gate_with_vertical_lift_panel_2828e1d65eb54b3bba3c91e03dbe0818` | `data/records/rec_sluice_gate_with_vertical_lift_panel_2828e1d65eb54b3bba3c91e03dbe0818/revisions/rev_000001/model.py:L27-L251` | 紧凑 4-part 范本：steel portal frame(`L30-L129`，含双 post + sill + 内嵌 guide channel visual + bolt 印刷) + planar lift_panel(`L130-L168`) + crank_wheel(`L169-L201`，含 ring rim + 4 spokes + handle 子) **直接装配到 frame**（无 operator_housing 中间件）+ latch_arm(`L202-L221`)；3 articulations：PRISMATIC `(0,0,1)` `[0, 0.22]` + CONTINUOUS `(0,1,0)` + REVOLUTE latch `(0,1,0)` `[-0.20, 0.70]` |
| S3 | `rec_sluice_gate_with_vertical_lift_panel_baeff4a3cdac4ffca0cc072a25e57452` | `data/records/rec_sluice_gate_with_vertical_lift_panel_baeff4a3cdac4ffca0cc072a25e57452/revisions/rev_000001/model.py:L51-L267` | 大型 concrete-headwall masonry frame(`L58-L107`，含双 pier 厚壁 + lintel + bolted steel C-channel guides visual) + ribbed lift_panel(`L108-L135`，含厚板 + 多 horizontal_rib + center_rib) + operator_box(`L151-L194`，独立 FIXED gearbox housing) + mesh-rim handwheel(`_build_handwheel_mesh` L38-L49, `L203-L215`) + locking_pawl(`L229-L248`)；5 articulations：PRISMATIC `[0, 1.48]` + FIXED operator_box + CONTINUOUS handwheel_spin + REVOLUTE pawl_pivot |
| S4 | `rec_sluice_gate_with_vertical_lift_panel_cbce5d1422874e66b6b752f7d6ccc23d` | `data/records/rec_sluice_gate_with_vertical_lift_panel_cbce5d1422874e66b6b752f7d6ccc23d/revisions/rev_000001/model.py:L28-L175` | 中型 steel channel_frame(`L28-L93`，含 2 post + top crossbeam + 嵌入 guide visual) + planar lift_panel(`L94-L108`) + **大型 crank_wheel 直接装配到 frame**(`L109-L130`，torus rim + 4 spokes + handle，CONTINUOUS axis `(1,0,0)`) + inspection_door(`L131-L146`，侧 REVOLUTE 翻盖 `(0,0,-1)` `[0, 1.75]`) |
| S5 | `rec_sluice_gate_with_vertical_lift_panel_cb020d56f9df4fa6958a99857183d61d` | `data/records/rec_sluice_gate_with_vertical_lift_panel_cb020d56f9df4fa6958a99857183d61d/revisions/rev_000001/model.py:L17-L221` | 极简 4-part：frame(`L25-L87`，最简 portal + 嵌入 guide visual) + planar barrier(`L88-L119`) + wheel 直挂 frame(`L120-L161`) + pawl(`L162-L180`)；适合 baseline planar-slab + direct-mount 组合 |
| S6 | `rec_sluice_gate_with_vertical_lift_panel_1ccde76ef9a1475c9cdef6ad5046c4af` | `data/records/rec_sluice_gate_with_vertical_lift_panel_1ccde76ef9a1475c9cdef6ad5046c4af/revisions/rev_000001/model.py:L20-L260` | **cadquery profiled frame + cadquery handwheel/pawl**：`_xz_annulus`/`_xz_rect`(L20-L46) + `_build_handwheel`(L39-L47, cq annulus+spokes+grip) + `_build_pawl`(L48-L60, cq tapered tooth) + frame `L70-L188` + gate `L189-L208` + wheel `L209-L222` + pawl `L223-L229`；4 articulations 主+wheel+pawl |
| S7 | `rec_sluice_gate_with_vertical_lift_panel_343851e69f6c46539b1b64b75b0c9333` | `data/records/rec_sluice_gate_with_vertical_lift_panel_343851e69f6c46539b1b64b75b0c9333/revisions/rev_000001/model.py:L19-L313` | **separate twin-rail frame**：frame(`L31-L149`) + 2 个独立 `guide_0/1` part（rail 独立成 FIXED part，类似 S1 但更纤细）+ planar panel(`L172-L223`) + handwheel 直挂 frame(`L224-L262`) + inspection_flap(`L263-L282`，top-hinged REVOLUTE) |
| S8 | `rec_sluice_gate_with_vertical_lift_panel_a911c485778042cf86e65494477e02aa` | `data/records/rec_sluice_gate_with_vertical_lift_panel_a911c485778042cf86e65494477e02aa/revisions/rev_000001/model.py:L29-L315` | direct-drive 大手轮范本：`_handwheel_mesh`(L29-L60) + 大 frame + **for-loop separate rails**(`L98-L125`，每根 rail 都是独立 part + FIXED) + ribbed lift_plate(`L126-L181`) + operator_housing(`L192-L258`) + 大直径 handwheel(`L267-L283`) + locking_pawl(`L284-L314`) |
| S9 | `rec_sluice_gate_with_vertical_lift_panel_04ad25dc920546abb88a0e45796d59c0` | `data/records/rec_sluice_gate_with_vertical_lift_panel_04ad25dc920546abb88a0e45796d59c0/revisions/rev_000001/model.py:L47-L251` | steel-portal frame(`L47-L135`) + **ribbed panel**(`L136-L169`，含 panel_rib + crossbar 横纵肋) + handwheel 直挂(`L170-L207`) + hatch(`L208-L224`，REVOLUTE axis `(0,0,1)` 旋转 hatch) |
| S10 | `rec_sluice_gate_with_vertical_lift_panel_08792383522a4dedafae6b90dfb9bcb8` | `data/records/rec_sluice_gate_with_vertical_lift_panel_08792383522a4dedafae6b90dfb9bcb8/revisions/rev_000001/model.py:L19-L232` | masonry concrete frame + gearbox housing 范本：`_midpoint`/`_distance`/`_rpy_for_cylinder`/`_add_member`(`L19-L44`) + `_handwheel_rim_mesh`(`L46-L63`) + masonry part(`L76-L137`) + ribbed lift_panel(`L138-L151`) + 独立 FIXED gearbox part(`L152-L169`) + handwheel(`L170-L190`) + inspection_door(`L191-L228`，door_hinge REVOLUTE) |
| S11 | `rec_sluice_gate_with_vertical_lift_panel_afca15e512e34dd6adda67b5ac387f85` | `data/records/rec_sluice_gate_with_vertical_lift_panel_afca15e512e34dd6adda67b5ac387f85/revisions/rev_000001/model.py:L19-L207` | 最简 baseline：`_add_side_channel`(`L19-L38`) 帮 frame visual 嵌入 guide channel；frame(`L40-L95`) + planar gate_leaf(`L96-L122`) + 小手轮直挂(`L123-L162`) + gearbox_cover(`L163-L176`，top-hinged REVOLUTE cap) |

剩余 17 个 5 星样本（如 `cda5c4e7`/`cf3dbfa3`/`d073b45e`/`ed1de96f`/`f94ff00c`/`12cc8563`/`1817e6e9`/`25ba8955`/`5133b94d`/`7039dafc`/`781e4802`/`8bd24ccb`/`8fc467cc`/`9e7a48e5`/`a7bdaea0`/`b7071967`/`cda5c4e7`）按 model.py grep 验证后归入 S1-S11 同族，仅作为多样性交叉验证；它们的结构特征已被现有候选覆盖，避免把变体当独立 candidate 重复。

## 槽位 + 候选模块表

### Slot 1：frame（root：sill + 两侧 pier/post + lintel + guide channel 拓扑）
最不动的水工底座。负责把 lift_panel 关在两侧导轨内、给 sill 提供闭门密封面、并提供 operator_housing/handwheel 顶部支点。`guide_rail` 在大多数样本里是 frame 的 ornament visual（Rule 1），仅在 S1/S7/S8 等明确把每根 rail 写成独立 `model.part` + FIXED 装配时进入 `separate_rails` 分支。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `masonry_two_pier` | S3 / S10 (baef / 0879) | `baef:L58-L107` / `0879:L76-L137` | eligible if compatible | 两根厚混凝土 pier(`Box ~0.6×0.4×height`) + sill 底槛 + top lintel + 内嵌或螺栓 C-channel guide visual + 印刷铭牌/水位标尺；适配大孔径 1.2-3m，最厚重 |
| `steel_portal_two_post` | S2 / S4 / S5 / S9 / S11 (2828 / cbce / cb020 / 04ad / afca) | `2828:L30-L129` / `cbce:L28-L93` / `cb020:L25-L87` / `04ad:L47-L135` / `afca:L40-L95` | eligible if compatible | 两根刷漆 steel 立柱(`Box ~0.10×0.10×height`) + 顶 crossbeam/lintel + 紧贴 panel 的内置 guide channel visual + 底 sill plate；中小孔径 0.3-1.5m 最常见，最稳健 |
| `separate_rails_portal` | S1 / S7 / S8 (04a1 / 3438 / a911) | `04a1:L45-L83` + `L150-L156` / `3438:L150-L155` / `a911:L98-L125` | eligible if compatible | portal frame + **每根 guide_rail 写成独立 `model.part` + FIXED `frame→guide_i`**，往往附带 `_add_guide_rail`/for-loop helper；guide 几何更精细、可独立 verify capture overlap |
| `cadquery_profiled_block` | S6 (1ccde) | `1ccde:L20-L46` + `L70-L188` | eligible if compatible | cadquery `_xz_annulus`/`_xz_rect` 组合出的 monolithic profiled headwall block；frame 走 cq mesh，sill+guide 一体成型，适合 profiled gate 配套 |

### Slot 2：lift_panel（沿 (0,0,1) PRISMATIC 升降的 gate leaf，唯一主自由度 child）
身份件。永远是 PRISMATIC `(0,0,1)` 的 child，永远 parent=frame。leaf 上的 stiffener/edge bar/seal 全是 leaf.visual，不拆 part。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `planar_slab` | S2 / S4 / S5 / S11 (2828 / cbce / cb020 / afca) | `2828:L130-L168` / `cbce:L94-L108` / `cb020:L88-L119` / `afca:L96-L122` | eligible if compatible | 单 Box plate + 底 lip/seal_strip visual + 顶 yoke lug 给 stem 接口；最简 0.03-0.08m 厚，小孔径默认 |
| `ribbed_stiffened_plate` | S1 / S3 / S8 / S9 / S10 (04a1 / baef / a911 / 04ad / 0879) | `04a1:L162-L195` / `baef:L108-L135` / `a911:L126-L181` / `04ad:L136-L169` / `0879:L138-L151` | eligible if compatible | main plate + 2-4 horizontal rib(`Box ~plate_w×0.08×0.10`) + 1-2 vertical center/edge stiffener + 底 bottom_edge + 顶 yoke + lift lug；中大孔径 1.0-3m 主力 |
| `cadquery_profiled_panel` | S6 (1ccde) | `1ccde:L189-L208` | eligible if compatible | cadquery 组合出整体成型 panel（含一体的 reinforcement ribs / edge channels），mesh 复杂度高，配 `cadquery_profiled_block` frame 使用 |

### Slot 3：hoist（顶部旋转输入：handwheel/crank + 可选 operator_housing 中间件）
人手操作的提升机构。CONTINUOUS rotation 是这一组的标志关节；它的 parent 由 `hoist_mount` 决定：直接挂 frame（紧凑 / 大 crank wheel 设计）或经独立 FIXED `operator_housing`/`gearbox`/`operator_box` 一层中间件（厚重 gearbox 设计）。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `gearbox_handwheel_via_housing` | S1 / S3 / S8 / S10 (04a1 / baef / a911 / 0879) | `04a1:L194-L251` + handwheel `L252-L287` / `baef:L151-L228` / `a911:L192-L283` / `0879:L152-L190` | eligible if compatible | 独立 FIXED `operator_housing`/`operator_box`/`gearbox` part（含 crossbeam+gearbox body+bonnet+wheel_support+shaft_boss+pawl_bracket visuals），handwheel `model.part` 含 3-4 spokes + rim + hub + shaft + grip stem，CONTINUOUS `operator_housing→handwheel` axis `(0,±1,0)` 或 `(0,0,1)`；handwheel 直径 0.15-0.30m，适配 small-to-medium 闸 |
| `large_crank_wheel_direct` | S2 / S4 / cbce / cda5 (2828 / cbce / cda5) | `2828:L169-L201` / `cbce:L109-L130` / `cda5:L109-L145` (via `_handwheel_shape` cq L20-L67) | eligible if compatible | **无 operator_housing 中间件**：crank_wheel 直接 CONTINUOUS 挂 frame；轮型为 torus rim/ring + 4 spokes + 末端 handle/knob，直径 0.28-0.42m，强调高 mechanical advantage；轴可能 `(0,1,0)` 或 `(1,0,0)` |
| `direct_handwheel_on_frame` | S5 / S7 / S9 / S11 (cb020 / 3438 / 04ad / afca) | `cb020:L120-L161` / `3438:L224-L262` / `04ad:L170-L207` / `afca:L123-L162` | eligible if compatible | 小型 handwheel（直径 0.10-0.25m）**直接 CONTINUOUS 挂 frame**，无 housing 中间件；rim+spokes(3-4)+hub+grip 全 primitive Box/Cylinder，最紧凑 |
| `cadquery_handwheel_via_housing` | S6 (1ccde) | `1ccde:L39-L47` + `L209-L222` | eligible if compatible | cadquery `_build_handwheel`（annulus rim + tapered spokes + grip）+ 可选 housing，材质 cast iron，适合 profiled gate 配套 |

### Slot 4：gated_child（gated 第二件，几乎每个 5 星都有一个）
水工闸门安全/检修的第二并列件。`none` 仅做兼容降级用；5 星中绝大多数都引入恰好一个。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `locking_pawl_revolute` | S1 / S3 / S5 / S6 / S8 (04a1 / baef / cb020 / 1ccde / a911) | `04a1:L289-L324` + 关节 `L367-L380` / `baef:L229-L266` / `cb020:L162-L221` / `1ccde:L223-L258` / `a911:L284-L314` | eligible if compatible | 独立 `locking_pawl`/`pawl` part(pivot_barrel + root + arm + tooth + neck + handle visuals)，REVOLUTE 挂在 operator_housing 或 frame 上，轴 `(0,±1,0)`，`[-0.65, 0.45]` 或 `[0, 0.7]`，咬合 wheel ratchet 或 panel rack |
| `latch_arm_revolute` | S2 (2828) | `2828:L202-L249` | eligible if compatible | 单 part `latch_arm`(barrel + arm + hook + counterweight visuals)，REVOLUTE 直接挂 frame，轴 `(0,1,0)` `[-0.20, 0.70]`；轻量化 ratchet/latch 形态，没有 pawl tooth 阵列 |
| `inspection_door_revolute` | S4 / S7 / S9 / S10 (cbce / 3438 / 04ad / 0879) | `cbce:L131-L146` + `L165-L174` / `3438:L263-L282` / `04ad:L208-L224` / `0879:L191-L228` | eligible if compatible | 独立 `inspection_door`/`hatch`/`flap` part(panel + frame + hinge_lug + knob/handle visuals)，REVOLUTE 侧/顶 hinge，轴 `(0,0,±1)` 或 `(0,±1,0)`，`[0, 1.35..1.75]`，开盖检视 gearbox/控件 |
| `gearbox_cover_top_flap` | S11 (afca) | `afca:L163-L207` | eligible if compatible | 小型 `gearbox_cover` part(box + handle visuals)，REVOLUTE top-hinge `(0,1,0)` 上翻盖，作为最简 gated 件，区别于侧开 inspection_door |

## 槽位图（slot graph）
```
pattern = mixed
（身份链 frame → lift_panel（单 PRISMATIC `(0,0,1)`）
 + hoist branch（CONTINUOUS，optionally via FIXED operator_housing）
 + optional gated_child branch（REVOLUTE）
 + optional FIXED separate guide_rail 中间件×2）

                              frame (Slot1)  ── FIXED ──►  [guide_rail_i] ×{0,2}
                                │              (仅 separate_rails_portal)
                                │
            ┌───────────────────┼────────────────────────────┐
            │ PRISMATIC          │                            │ FIXED (optional)
            │ axis=(0,0,1)       │                            ▼
            │ [0, panel_travel]  │                       operator_housing
            ▼                    │                       (FIXED frame→housing)
       lift_panel (Slot2)        │                            │ CONTINUOUS
       （leaf+ribs+yoke）        │                            │ axis=(0,±1,0) 或 (0,0,1)
                                 │ CONTINUOUS                 ▼
                                 │ axis=(0,±1,0) 或 (1,0,0) handwheel/crank_wheel (Slot3, with housing)
                                 ▼
                       handwheel/crank_wheel (Slot3, direct)
                                 │
            ┌────────────────────┴────────────────────────────┐
            │ REVOLUTE                                          │ REVOLUTE
            │ parent = operator_housing 或 frame                │ parent = frame
            │ axis 视类型                                        │ axis 视类型
            ▼                                                  ▼
       locking_pawl / latch_arm / inspection_door / gearbox_cover  (Slot4)
```

- 身份链恒为 `frame → lift_panel`（恰好一个 PRISMATIC，axis 永远 `(0,0,1)`，行程 0.15-2.3m）。
- Slot1=`separate_rails_portal` 时引入 2 个 FIXED `guide_rail` 中间件 part；其他三个 Slot1 分支中 guide channel 是 frame visual。
- Slot3 有两条装配子分支：
  - `gearbox_handwheel_via_housing` / `cadquery_handwheel_via_housing` 路径：先一个 FIXED `frame→operator_housing`，再 CONTINUOUS `operator_housing→handwheel`。
  - `large_crank_wheel_direct` / `direct_handwheel_on_frame` 路径：直接 CONTINUOUS `frame→handwheel|crank_wheel`，无中间件。
- Slot4≠`none` 时引入一个独立 REVOLUTE child，parent 与 Slot3 是否带 housing 匹配（带 housing 时 pawl 多挂 housing；无 housing 时挂 frame）。
- Slot4=`none` 仅为兼容降级；5 星样本中没有真实 none 形态，sampler 默认不抽 none。

## 每槽位 Module Emits / Interfaces

### Slot 1 / frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root)；可选 `guide_rail_0`/`guide_rail_1` 仅 `separate_rails_portal` 分支 | S1/S2/S3 |
| visuals | piers/posts + sill + lintel/top_cap + 内嵌 guide channel（baked 形态）+ seal_strip + 标尺/铭牌 | S1-S11 |
| internal joints | `separate_rails_portal` 时 2 个 FIXED `frame→guide_rail_i` | S1/S7/S8 |
| upstream interface | 落地 root，无 upstream | — |
| downstream interface | sill 平面（与 lift_panel 底 seal 接触）；两侧 guide channel 内壁（与 lift_panel 两侧 edge_bar 滑配）；top crossbeam / lintel face（承 operator_housing 或 handwheel 直挂） | S1/S2/S3 |

### Slot 2 / lift_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lift_panel` / `gate_leaf` / `lift_plate` / `gate` / `barrier` / `panel` / `closure_panel` 单一 part | S1/S2/...所有 |
| visuals | main plate + bottom_edge/seal_strip + edge_bar×2（贴 guide channel 内壁）+ horizontal rib×0..4 + vertical stiffener×0..2 + 顶 yoke/lug（接 stem/hoist 输出） | S1/S3/S8/S9 |
| internal joints | 无 | — |
| upstream interface | 顶 yoke 几何中心 = stem 名义连接点（hoist→panel 名义 mating，**不实建第二关节**：在 5 星样本里 stem 只作为 hoist 内部 visual，handwheel 旋转用 CONTINUOUS 表达，panel 升降用独立 PRISMATIC 表达，两者用 origin/range 数值耦合而非真实驱动链） | S1/S3 |
| downstream interface | 两侧 edge_bar 落在 frame guide channel 内（滑动接触，0.001-0.005m clearance）；底 seal_strip 落在 sill 顶面（closed pose gap ≤ 0.001m） | S1/S2/S3 |

### Slot 3 / hoist
| emits | 描述 | 来源 |
|---|---|---|
| parts | 可选 `operator_housing`/`operator_box`/`gearbox` (FIXED 中间件) + `handwheel`/`crank_wheel`/`wheel` (CONTINUOUS child) | S1/S3/S4/S8 |
| visuals | housing 分支：crossbeam + gearbox body + bonnet + wheel_support + shaft_boss + pawl_bracket/pawl_bridge + service_box；wheel 分支：rim(torus/annulus/Box ring) + hub + 3-4 spokes + grip stem | S1/S3/S4 |
| internal joints | 可选 FIXED `frame→operator_housing` + CONTINUOUS `operator_housing|frame→handwheel|crank_wheel` axis `(0,±1,0)` 或 `(0,0,1)` 或 `(1,0,0)` | S1/S2/S4 |
| upstream interface | housing 底面 / 大轮 hub 中心：贴 frame top crossbeam/lintel 上表面（FIXED 或 CONTINUOUS pivot） | S1/S2 |
| downstream interface | handwheel/wheel 的 spoke/grip 末端是 wow 点，无下游 mating；pawl_bracket/pawl_bridge visual 是 Slot4 locking pawl 的承力面 | S1/S3 |

### Slot 4 / gated_child
| emits | 描述 | 来源 |
|---|---|---|
| parts | `locking_pawl` / `latch_arm` / `inspection_door` / `hatch` / `inspection_flap` / `gearbox_cover` 单一 part | S1/S2/S3/S4/S7/S10/S11 |
| visuals | 每种 ~3-7 个 visual（pivot barrel + arm/tooth/handle 或 door panel + hinge lug + knob） | S1/S2/S4 |
| internal joints | 1 REVOLUTE `(operator_housing|frame)→child`，axis 视类型，`[lower, upper]` `[-0.65, 0.45]` 到 `[0, 1.75]` | S1/S2/S4 |
| upstream interface | pivot barrel / hinge knuckle 与 Slot3 的 pawl_bracket / housing 侧壁 / frame top 直接 mating（captured-pin 形态需 `allow_overlap`） | S1/S3/S10 |
| downstream interface | pawl tooth 与 wheel ratchet 名义咬合（不实建关节，几何近接）；door panel 翻开/合上的 swept volume 不能穿 housing/frame | S1/S4 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `frame_style` | enum | `masonry_two_pier` / `steel_portal_two_post` / `separate_rails_portal` / `cadquery_profiled_block` | sampled | drives Slot1 拓扑（是否多 2 个 FIXED guide_rail part） | S3/S2/S1/S6 |
| `panel_style` | enum | `planar_slab` / `ribbed_stiffened_plate` / `cadquery_profiled_panel` | sampled | drives Slot2 visual 复杂度（含/不含 ribs） | S2/S1/S6 |
| `hoist_style` | enum | `gearbox_handwheel_via_housing` / `large_crank_wheel_direct` / `direct_handwheel_on_frame` / `cadquery_handwheel_via_housing` | sampled | drives Slot3 是否多 1 个 FIXED `operator_housing` part + handwheel/wheel 轴族 | S1/S2/S5/S6 |
| `gated_child` | enum | `locking_pawl_revolute` / `latch_arm_revolute` / `inspection_door_revolute` / `gearbox_cover_top_flap` / `none` | weighted sampled（`none` 权重接近 0） | drives Slot4 是否多 1 个 REVOLUTE child part | S1/S2/S4/S11 |
| `panel_w` | float | 0.42 - 2.90 m | sampled | leaf 宽（影响 frame pier 间距 + guide 距） | S1/S3/S8 |
| `panel_h` | float | 0.75 - 3.00 m | sampled | leaf 高（影响 frame 立柱高 + lift travel 上限） | S1/S3 |
| `panel_thickness` | float | 0.035 - 0.16 m | sampled | leaf 厚（baseline planar 0.035, ribbed 0.05-0.08, profiled 大型 0.10-0.16） | S2/S3 |
| `panel_travel` | float | 0.15 - 2.30 m | derived ≈ panel_h × 0.7-0.9 | PRISMATIC `[0, panel_travel]` upper；保证 closed→opened 行程接近 panel_h 但留 yoke clearance | S1/S2/S3 |
| `pier_thickness` | float | 0.10 - 0.65 m | derived from `frame_style` | masonry 0.40-0.65、steel_portal 0.10-0.18、separate_rails 0.12-0.20 | S3/S2/S1 |
| `pier_spacing` | float | 0.50 - 2.95 m | derived ≈ `panel_w + 2 * guide_capture` | 双 pier 内侧间距 = panel 宽 + 2×guide capture depth | S1/S3 |
| `guide_capture` | float | 0.04 - 0.18 m | sampled | guide channel 在 panel 两侧覆盖深度（baseline 0.08） | S1/S2 |
| `wheel_radius` | float | 0.08 - 0.42 m | derived from `hoist_style` | `direct_handwheel_on_frame` 0.08-0.20、`gearbox_handwheel` 0.15-0.30、`large_crank_wheel_direct` 0.28-0.42 | S1/S2/S4 |
| `wheel_axis` | enum | `(0,1,0)` / `(0,-1,0)` / `(1,0,0)` / `(0,0,1)` | sampled (compat with hoist_style) | CONTINUOUS axis；direct wheel 多 `(0,1,0)` 或 `(1,0,0)`、housing 多 `(0,1,0)`、04ad 罕见 `(0,0,1)` | S1/S2/S4/S9 |
| `housing_height` | float | 0.18 - 0.55 m | sampled (仅 housing-bearing 分支) | operator_housing 高度（gearbox body + bonnet 子件总高） | S1/S3 |
| `gated_child_axis` | enum | `(0,1,0)` / `(0,-1,0)` / `(0,0,1)` / `(0,0,-1)` | derived from `gated_child` | pawl/latch 多 `(0,±1,0)`、inspection_door 多 `(0,0,±1)`、gearbox_cover_top_flap `(0,1,0)` | S1/S4/S9/S11 |
| `gated_child_range` | float | `[-0.65, 0.45]` ~ `[0, 1.75]` | derived from `gated_child` | pawl 短行程双向、door/cover 单向到 ~1.35-1.75 | S1/S4 |
| `panel_rib_count` | int | 0..4 | derived（`planar_slab`=0, `ribbed_stiffened_plate`∈{2,3,4}, `cadquery_profiled_panel`=fixed） | leaf 横肋数；不计入 slot graph，仅 leaf.visual 数量影响 | S1/S3/S8/S9 |
| `controlled_local_scales` | dict | 见拓扑多样性审计 / Controlled local parameterization 行 | clamped | 各局部 scale 安全比例，不破坏接口 | — |
| `palette` | enum | concrete / steel / coated_plate / cast_iron / warning_yellow / dark_steel 等材质组 | sampled | 颜色/材质，不计入拓扑 | 全样本 |

参数只表达语义选择、尺寸、行程、角度、局部安全 scale 或 palette；未实现拓扑（如水平推拉滑闸、扇形闸、双 leaf 叠放）不进 enum。

## Multiplicity / Copy Logic

- 无模板级可变复制数量逻辑：核心结构由固定 named slots 表达（frame、lift_panel、operator_housing/handwheel、gated_child），不暴露 `*_count` 作为主拓扑采样轴。
- 固定成对的 module-local 重复保留为 module-local construction，并使用稳定命名（不进 seed domain 主轴）：
  - `separate_rails_portal` 永远是 2 个 guide_rail（左右对称，命名 `guide_0`/`guide_1`，placement 由 `pier_spacing` 派生）。
  - `masonry_two_pier` / `steel_portal_two_post` 永远是 2 根 pier/post visual（同样左右对称镜像）。
  - panel `ribbed_stiffened_plate` 含 2 根 edge_bar 和 0-4 根 horizontal rib，rib 数量由 `panel_rib_count` 受控（属 controlled local，不改变 part 树）。
  - handwheel 永远 3-4 spoke visual；crank_wheel 永远 4-6 spoke visual；这些是 module-local fixed copies，不进 seed domain 主轴。
- 未来若要把"二组双闸"（dual-leaf side-by-side）或"上下双 panel stop-log"升级为可变 multiplicity，必须补充 5 星样本来源、N_range、placement 规则、joint policy 与 reviewer 审核；当前 28 个 5 星样本中没有真实多 leaf 案例，因此 spec 拒绝在不补 source 的情况下进入 sampling。

## 拓扑多样性审计

总组合数（笛卡尔积，未加相容约束）：
Slot1 frame_style(4) × Slot2 panel_style(3) × Slot3 hoist_style(4) × Slot4 gated_child(4 主+ 1 none) = **240**（含 none 240，主域 192）。


理由：只看会改变 part 数 / joint 数 / joint 拓扑的结构骨架：
- Slot1 `frame_style`：`separate_rails_portal` 引入 2 个额外 FIXED `guide_rail` part（part 数 +2，joint 数 +2 FIXED）；其余三个分支维持 1-part frame（guide 嵌 visual）。**2 个结构骨架（with-rails / no-rails）**。
- Slot3 `hoist_style`：含 housing 的两个分支（`gearbox_handwheel_via_housing` / `cadquery_handwheel_via_housing`）引入 1 个额外 FIXED `operator_housing` part；direct 的两个分支无 housing。**2 个结构骨架（with-housing / no-housing）**。
- Slot4 `gated_child`：5 个值 → `none`(无第二件) / `locking_pawl`(+1 REVOLUTE part, axis Y) / `latch_arm`(+1 REVOLUTE part, axis Y, 单 hook) / `inspection_door`(+1 REVOLUTE part, axis Z 或 Y, hinge 在侧 / 顶) / `gearbox_cover_top_flap`(+1 REVOLUTE part, axis Y, top-hinge)。**5 个结构骨架**（按 axis 族 + hinge 位置区分）。
- Slot1 × Slot3 × Slot4 = 2 × 2 × 5 = **20 种 part/joint-拓扑骨架**，远超 ≥10 distinct 门槛。叠加 Slot2 panel_style（仅几何换装，不计入）后离散组合 192-240。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。

Procedural Sampling / Sweep Plan：sampler 先 procedural 抽 `frame_style` → `panel_style` → `hoist_style` → `gated_child`，每一步从 compatible 子集中按近均匀权重抽（`gated_child=none` 权重极低，仅为兼容降级）。`resolve_config` 阶段把 `panel_w/panel_h/panel_thickness/panel_travel/pier_spacing/guide_capture/wheel_radius/wheel_axis/housing_height/gated_child_axis/gated_child_range` 做 clamp + derived（pier_spacing = panel_w + 2×guide_capture；panel_travel ≤ panel_h - yoke_clearance）；不兼容组合（例如 `cadquery_profiled_panel` × `steel_portal_two_post` × `direct_handwheel_on_frame` 厚 leaf 配紧凑小手轮）通过 `wheel_radius` derived range 自动落到大值，不需要硬拒。

Topology target：1000-seed slot choice tuple distinct 建议 ≥80（受 Slot2 panel_style 实际只改 leaf visual 复杂度而非 part 数限制；20 个真实骨架 × multi-axis 离散变化叠加 controlled local scale 应可达 ≥80，低于 300 因 Slot2 不增 part 数）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Regression overrides：默认无。若 sweep 发现稳定失败组合（例如 `large_crank_wheel_direct` 配 `masonry_two_pier` 时 frame top crossbeam 厚度不够支撑大轮 hub），可加少量显式 regression seed 并写明原因；不得用小型 curated / modulo 表作为主 seed domain。

Controlled local parameterization（初版模板必须包含的局部安全 scale）：

- `pier_thickness_scale ∈ [0.85, 1.15]`：在 `frame_style` 默认厚度上做 ±15% 缩放，clamp 后用于 frame pier/post 视觉厚度；不改变 part 数、不破坏 guide_capture clearance。
- `guide_capture_scale ∈ [0.75, 1.30]`：缩放 `guide_capture`，clamp 到 `[0.04, 0.18]`；保证 leaf 两侧 edge_bar 始终落在 guide channel 内（min capture ≥ panel_thickness/2 + 0.005）。
- `wheel_radius_scale ∈ [0.85, 1.20]`：在 hoist_style 默认 wheel 半径上 ±20%；clamp 到 hoist_style 允许 range（不让小 handwheel 长到比 frame 还宽）。
- `housing_height_scale ∈ [0.85, 1.15]`（仅 housing-bearing 分支）：缩放 operator_housing 总高；clamp 保证 handwheel hub 不与 frame top_cap 干涉。
- `panel_rib_spacing_scale ∈ [0.85, 1.15]`（仅 `ribbed_stiffened_plate`）：rib 沿 Z 间距缩放；不改变 rib 数量、保持顶/底/中位置不破坏 yoke 与 bottom_edge。
- `panel_travel_scale ∈ [0.8, 0.95]`：把 PRISMATIC upper 缩到 `(panel_h - yoke_clearance) × scale`，保证开到 upper 时 leaf 顶不撞 lintel。
- `gated_child_range_scale ∈ [0.85, 1.15]`：缩放 Slot4 REVOLUTE range；clamp 不超过 ±0.85 rad 防止 pawl/door 翻穿 housing。

所有局部 scale 在 `resolve_config` 中 clamp / 派生，受 InterfaceSpec / MatingContract / guide capture / sill seal gap / yoke clearance / lintel clearance 约束；它们只能改变安全比例、clearance 或细节尺寸，不能改变未声明的拓扑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural-first 4-slot 顺序抽样；`gated_child=none` 权重 ~0.02，仅作为降级 | slot_choices_for_seed 与实际 build choices 完全一致 |
| compatibility matrix | `cadquery_profiled_panel` 倾向配 `cadquery_profiled_block` / `cadquery_handwheel_via_housing`（同 cq 风格族）但不硬绑；`large_crank_wheel_direct` 不与 `masonry_two_pier` 强配（masonry top crossbeam 兼容大轮 hub）；`gated_child` 中 `locking_pawl_revolute` 优先与 housing-bearing hoist 搭（pawl_bracket 在 housing visual 上），与 direct hoist 搭时 pawl parent=frame | 无悬空件、guide capture 充足、closed pose seal gap、wheel hub 不撞 frame top |
| controlled local variation | 7 项 scale 全部 clamp + derived，不改变拓扑 | proportions 自然、guide clearance、seal 接触、yoke 净空、肋间距合理 |
| regression overrides | none（首版）；后续仅在 sweep 复现 stable failure 时加少量 | 已知失败回归或 reviewer 指定 |
| random sweep | seeds 0-49 初始 sweep，0-999 成熟度 | contract failures + closed/opened pose AABB + capture overlap |

每槽位候选数：

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| Slot1 frame | 4 | yes | yes | masonry / steel_portal / separate_rails / cadquery；4 个结构家族 |
| Slot2 lift_panel | 3 | yes | yes | planar / ribbed / cadquery_profiled；几何家族差异显著 |
| Slot3 hoist | 4 | yes | yes | gearbox-housing / large-crank-direct / direct-handwheel / cadquery-via-housing |
| Slot4 gated_child | 4(+`none`) | yes | yes | locking_pawl / latch_arm / inspection_door / gearbox_cover_flap；none 仅降级 |

## Validator（author_run_tests 必须覆盖的点）

- identity：存在 `frame` + `lift_panel`（任意命名同义：lift_plate / gate_leaf / barrier / gate / panel / closure_panel）；存在恰好一个 PRISMATIC 主关节连接两者。
- primary joint：lift PRISMATIC parent=frame、child=lift_panel、axis 严格 `(0,0,1)`（容差 ≤ 0.02）、`upper > lower`、`upper - lower ∈ [0.15, 2.50]`、`lower == 0`。
- hoist joint：存在恰好一个 CONTINUOUS 关节连接 handwheel/crank_wheel 到 frame 或 operator_housing；轴在 `{(0,±1,0), (1,0,0), (-1,0,0), (0,0,±1)}` 中（容差 0.05）；hoist part 含 hub 中心 + 至少 3 个 spoke visual 或 torus rim mesh。
- housing wiring：当 `hoist_style ∈ {gearbox_*via_housing, cadquery_*via_housing}` 时，存在恰好一个 FIXED `frame→operator_housing` 关节，且 handwheel parent=operator_housing；否则 handwheel/crank_wheel parent=frame、无独立 housing part。
- guide wiring：当 `frame_style == separate_rails_portal` 时存在 2 个 FIXED `frame→guide_rail_i` 关节、2 个独立 part；否则 guide channel 是 frame.visual，无独立 guide_rail part。
- closed pose：joint=0 时 lift_panel 底 seal_strip 几何与 frame sill 顶面 Z gap ∈ `[0.0, 0.005]` m（无穿模、无悬空）；leaf 两侧 edge_bar 在 X 方向落入 frame guide channel 内（X overlap ≥ panel_thickness/2 + 0.005）。
- opened pose：joint=upper 时 lift_panel 顶 yoke 与 frame top_cap/lintel 底面 Z gap ≥ 0.02 m（不撞顶）；leaf 底 bottom_edge 已离开 sill 顶（Z gap ≥ upper × 0.9）；leaf 始终保留在 guide capture 范围内（两侧 edge_bar 不脱 guide）。
- gated child：当 `gated_child != none` 时存在恰好一个 REVOLUTE 关节，parent 与 hoist_style 一致（housing-bearing 时 parent=operator_housing 或 frame，direct 时 parent=frame）；axis 与 `gated_child` 类型一致；`upper - lower ≤ 2.5`；child part 含 pivot barrel/hub visual 与 parent 接触点 coaxial。
- captured pin / hinge：locking_pawl pivot barrel 与 operator_housing pawl_bracket 视觉重叠时使用 `allow_overlap(...)` 声明（S1 `L367-L385` 写法范本）。
- grounding & no floating：frame 落地（含 sill 底面 Z≈0）；lift_panel、operator_housing/guide_rail/handwheel/gated_child 全部经 FIXED 或主动关节 attach；所有 visual（piers/sill/lintel/guide channel/bolts/handles/stem 等）落在 frame 或 module-local part 上，无悬空 visual。
- slot_choices_for_seed returns implemented module names and matches actual `assemble` choices.
- config_from_seed 使用 deterministic procedural sampling（不依赖 seed=0 anchor、不轮换 < 50 项 curated 表作为主域）。

## Reject cases（必须能识别并拒绝）

- lift_panel 缺失，或被改成 REVOLUTE / FIXED（变成铰链翻起式 drawbridge 或固定挡板，丢身份）。
- PRISMATIC axis 不是 `(0,0,1)`（变成水平推拉滑闸），或 lower≠0，或 upper<0.15（无有效行程）。
- closed pose lift_panel 底悬空（与 sill gap > 0.01）或穿透 sill / lintel；opened pose 顶部 yoke 撞 lintel / 直接顶飞 frame。
- hoist 缺失（没有 handwheel/crank_wheel）；或 hoist 被改成 PRISMATIC（不是旋转输入）；或 hoist parent 错挂到 lift_panel 上（变成机构反向驱动）。
- `separate_rails_portal` 声称独立 guide_rail part 却把 guide 全画成 frame.visual（拓扑自相矛盾）；或 baseline 分支硬塞独立 guide_rail part（违 Rule 1）。
- `gearbox_handwheel_via_housing` 声称有 operator_housing 中间件但 handwheel parent=frame；或 direct 分支硬塞 operator_housing 浮空 part。
- 同时强加两个 gated_child（pawl + inspection_door 同时实化），或 gated_child 与 hoist 没有几何 mating（pawl 浮在半空、door 不在 housing/frame 上）。
- handwheel/crank_wheel 完全没有 spoke 或 hub（只剩一根 cylinder shaft 充数），不构成 wow 件。
- ribbed_stiffened_plate 的 rib 全部漂浮在 leaf 表面以外 / 不与 main plate 接触；或 panel_thickness 小于 0.020m 但带 4 根肋（比例错乱）。
- frame 上 sill / pier / lintel 拆成 FIXED 装饰 part（违 Rule 1）而非 visual。

## 与相邻类别的边界

- vs `singleleaf_drawbridge` / `paper_cutter_guillotine`：本类 leaf 沿 **PRISMATIC 垂直平移** 升降，不是 REVOLUTE 翻起/砍下；hoist 是 CONTINUOUS 旋转输入而不是受重力的 REVOLUTE 杠杆。
- vs `radial_sector_gate` / `revolving_door`：本类不绕水平/竖直轴旋转开关，扇形弧形闸属于不同 spine。
- vs `sliding_window` / `display_freezer_with_sliding_glass_lids`：本类是 mechanical-advantage hoist 驱动的水工/工业闸，含 handwheel、pier、sill seat、可选 locking pawl；纯居家滑动窗没有 hoist 也没有 pier。
- vs `barrier_gate`：本类是 vertical-lift 水闸（PRISMATIC `(0,0,1)`），不是 REVOLUTE 升降杆；不混入。
- vs `crane_tower` / `elevator`：本类 PRISMATIC 直接驱动 leaf 升降，不含 cable/cabin/counterweight chain；hoist 输出与 leaf 升降之间不实建第二关节，仅几何耦合。
- 同类内 baked-guide vs separate-rails：baked = guide channel 嵌入 frame visual（1-part frame）；separate = 2 个独立 FIXED `guide_rail` part（3-part frame 区）。用 `frame_style` gate，不把 separate rails 几何塞进 baked 默认分支。
- 同类内 with-housing vs direct-hoist：with-housing = 独立 FIXED `operator_housing`/`gearbox`/`operator_box` 中间件（多 1 个 part），handwheel parent=housing；direct = 无 housing，wheel parent=frame。用 `hoist_style` gate。

## 模板实现备注（可选）

- `_handwheel_rim_mesh` (S1 L30-L43)、`_handwheel_mesh` (S8 L29-L60)、`_build_handwheel` (S6 cq L39-L47)、`_handwheel_shape` (cda5 cq L20-L67) 是 4 个 hoist 风格的 helper 范本，按 hoist_style 切换。
- `_add_guide_rail`(S1 L45-L83) / `_add_side_channel`(S11 L19-L38) 是两种 guide channel emit 模式：前者在 separate_rails_portal 时 emit 独立 `guide_rail` part，后者在 baked 形态时只往 frame visual 里塞 channel face；模板应保留两条路径并按 `frame_style` 切换。
- `_add_member` / `_midpoint` / `_distance` / `_rpy_for_cylinder`(S10 L19-L44) 是 masonry/concrete frame 的 bar 几何 helper，配 `masonry_two_pier` 使用。
- `_build_pawl`(S6 L48-L60, cadquery tapered tooth) 是 pawl 的 cq 形态范本；`locking_pawl` baseline 走 primitive Box（S1 L289-L324）。
- captured-pin 重叠（pawl pivot_barrel ↔ housing pawl_bracket、handwheel shaft ↔ housing shaft_boss、handwheel hub ↔ wheel_support）通常需要 element-scoped `ctx.allow_overlap(...)` 声明，参考 S1 L367-L385、S3 L255-L267 写法。
- `cadquery_profiled_block` × `cadquery_profiled_panel` × `cadquery_handwheel_via_housing` 是同一 cq 风格族，建议在 sampler 中以更高权重作为联合候选出现；但不作为硬约束。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending（待人工审核）|
| reviewer notes | SPEC_ONLY_DRAFT；28 个 5 星全 grep + 11 个精读到 part/articulation 层；身份恒为 frame + lift_panel + 1 PRISMATIC `(0,0,1)` + 1 CONTINUOUS hoist；Slot1 4 candidates（masonry/steel_portal/separate_rails/cadquery）、Slot3 4 candidates（housing-bearing vs direct, primitive vs cq）、Slot4 4 candidates（pawl/latch/door/cover）；Slot2 3 candidates（planar/ribbed/cq_profiled，仅 visual 复杂度区别）；待人工 review |
