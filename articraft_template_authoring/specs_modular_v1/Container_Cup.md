# container_cup (drinking cup / travel mug / tumbler with sip/flip/screw/slide closures + optional handle) — Modular Spec

> 来源小类：`picture/Container/Cup`（articraft_data 上游 Container/Cup fork-variant pool）。
> 全部样本由单个 parent（kraft-paper 锥形纸杯 + snap-on sip 盖）fork 而来，每个变体只改一根目标轴。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template` 当前 `data/records/<id>/revisions/rev_000001/model.py`，以 part/joint/helper **名字** 为准（`_cup_shell` / `_cup_ribs` / `_cup_body` / `_lid_solid` / `_flap_panel` / `_loop_handle` / `_sleeve_body` / `_bracket_solid` / `_handle_bail_points` / `cup_to_lid` / `lid_to_sip_flap` / `cup_to_flap` / `lid_to_slide_ring` / `cup_to_sleeve` / `cup_to_handle` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_cup` |
| template path | `agent/templates/Container_Cup.py` |
| test path (optional) | `tests/agent/test_container_cup_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: body_form + lid_closure + handle_grip 三轴笛卡尔积，叠加一根 wall_pattern multiplicity 轴 N；lid / handle 挂到 cup 共同 parent，sip_flap/slide_ring 再挂到 lid）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 11 fork 变体 = 12 |
| read_count | 12（全部读全文 model.py：parent + straight_cylinder / waisted_tumbler / stemmed_foot / screw_twist_lid / flip_top_lid / slide_close_ring / loop_handle / snap_sleeve / fold_clip_handle / n12_bold_flutes / n8_facet_panels）|
| read_scope | all 5-star samples in this category（单 parent fork pool，逐一全读，不抽样）|
| source_index_policy | only adopted module sources are indexed below（§14）|

冗余/分流说明：
- 全 12 样本同 lid + sip_flap + cup 基线，每个变体仅沿一根轴改结构。body 轴 4 候选、lid 轴 4 候选、handle 轴 4 候选、N 轴（wall_pattern）多个采样。
- 变体之间共享几乎全部 helper（`_cup_shell` / `_lid_solid` / `_flap_panel` 逐字相同），只换被改轴的 helper/part/joint；只换尺寸/颜色不另列 candidate（颜色归 palette_style）。
- stemmed_foot 把 body helper 从 `_cup_shell` 升级为 `_cup_body`（revolve pedestal + bowl loft，多一段 stem+foot 几何，仍是单 `cup` root part，无新 joint）。

## 核心身份

一只直立中空饮用杯 / 旅行马克杯 / tumbler（drinking cup）：杯体沿 +Z 居中（x=0,y=0），底坐地 z=0，杯口开口朝上 z=+H。杯壁为 CadQuery `loft`/`extrude`/`revolve` 发射的厚壁中空开口 shell（真实饮用腔），外壁带竖肋/棱面防滑（multiplicity）。形态可为窄底宽口锥形纸杯 / 等径直壁圆柱马克杯 / 中段收腰旅行 tumbler / 杯碗+细柄+喇叭底足 pedestal。杯口上方一只盖（**主活动语义**）按某种机构开合：snap-on 圆顶 sip 盖直抬（PRISMATIC +Z lift-off）+ 小翻盖（lid 的 child REVOLUTE）/ 螺纹旋拧盖（REVOLUTE 绕 Z 旋拧封口，不抬升）/ 固定盖 + 大翻嘴 flip-top（盖 inlined 为 cup visual，仅 flap REVOLUTE）/ snap 盖 + 顶面旋转 slide ring 对位 drink hole（PRISMATIC lid + 盖上 REVOLUTE 绕 Z 环，captured pivot boss）。可选 handle/grip：无（仅防滑壁，基线）/ 侧 C 形耳把（固定 swept tube visual）/ 上下滑配防烫套筒（独立 part PRISMATIC +Z）/ 可折叠摆动 D-bail 提手（bracket 固定 visual + bail 独立 part REVOLUTE 水平铰）。默认成熟域：单杯单盖（无嵌套）。

不该混入：宽口带盖储物 / 化妆罐（wider-than-tall 罐体、screw-cap 密封罐，是 `container_jar`；cup 是直立饮用杯）、带壶嘴 + 提梁 + 加热底座的水壶（spout + bail + base，是 `container_kettle`）、细颈高瓶 / 酒瓶（tall narrow neck，是 `container_bottle`/`container_glass_bottle`）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 `cup`（root）part 的 mesh 属性（一次发射 shell + 肋/棱面 + 可选 pedestal），不是独立串联 slot。`lid_closure` 决定盖 part 数与 joint 拓扑（screw=lid 直挂 cup REVOLUTE Z；flip-top=盖 inlined 进 cup visual + 单 flap REVOLUTE；slide=lid PRISMATIC + 盖上 ring REVOLUTE Z）。`handle_grip` 各自挂到 cup（固定 visual 或独立 part+joint）。三轴笛卡尔积 + N 轴构成拓扑多样性（见 §9）。

### Slot A：body_form（杯体形态 / footprint——root `cup` part 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tapered_cone（基线）| rec_paper-coffee-cup-with-a-white-snap-on-sip-lid-th_..._2eedb76c | `_cup_shell` L62-99（三站 loft 锥壳 + 内腔 + rim bead）+ `_cup_ribs` L102-124 | eligible if compatible | 窄底（BASE_R）宽口（RIM_R）锥形 hollow shell，rolled rim bead，开口腔 |
| straight_cylinder | rec_container_cup_var_straight_cylinder | `_cup_shell` L60-86（`circle(CUP_R).extrude(CUP_H)` 等半径圆柱 + bead）+ `_cup_ribs` L89-106 | eligible if compatible | 直壁圆柱马克杯：常数半径 base→rim（无 taper），rim bead，开口腔 |
| waisted_tumbler | rec_container_cup_var_waisted_tumbler | `_cup_shell` L86-125（多站 `PROFILE` loft，腰部内收）+ `_profile_r` L71-83 + `_cup_ribs` L128-162 | eligible if compatible | 中段收腰 hourglass：宽底+宽口、窄腰（grip zone），multi-station loft 内外双壳 |
| stemmed_foot | rec_container_cup_var_stemmed_foot | `_cup_body` L70-130（`revolve` pedestal foot+stem ∪ bowl loft）+ `_bowl_radius_at` L133-136 + `_cup_ribs` L158-166 | eligible if compatible | 锥形杯碗 + 细 stem + 喇叭 foot pedestal（lathe revolve 半剖面），bowl 离地坐于 pedestal，单 `cup` part |

硬约束记录：body_form 4 candidate（达 3-6 目标）。全部 loft/extrude/revolve 中空开口腔，共享 `_cup_ribs` + lid/flap 基线（rim 口径 RIM_R 统一 0.045 保盖配合）；只换 footprint / 高宽比 / 收腰 / 是否带 pedestal。

### Slot B：lid_closure（**主开合机构槽**——盖动作；含 joint 拓扑多样：PRISMATIC ↔ REVOLUTE-twist ↔ REVOLUTE-flap）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| snap_lift_dome（基线）| rec_paper-coffee-cup-with-a-white-snap-on-sip-lid-th_..._2eedb76c | `_lid_solid` L127-206 + `cup_to_lid` PRISMATIC +Z L262-270 + `_flap_panel` L209-236 + `lid_to_sip_flap` REVOLUTE +X L286-296 | eligible if compatible | snap-on 圆顶盖直抬：`lid` part 经 `cup_to_lid` PRISMATIC +Z lift-off（q=0 坐 rim、正 q 直抬）+ `sip_flap` child 绕 +X REVOLUTE 翻盖（盖真实 spout 孔）；2 joint，flap 是 lid 的 child |
| screw_twist_lid | rec_container_cup_var_screw_twist_lid | `_cup_threads`/`_cup_thread_lug` L133-170 + `_lid_threads`/`_lid_thread_lug` L173-206 + `_lid_solid` L209-287 + `cup_to_lid` REVOLUTE +Z L348-362 + `lid_to_sip_flap` L379-389 | eligible if compatible | 螺纹旋拧盖：`cup_to_lid` REVOLUTE +Z（origin@rim top，q=0 拧紧、正 q 旋松 ~270°，不抬升）；cup 外螺纹 lug + lid 内螺纹 lug（`for i in range(N_THREADS)`）；flap 仍 lid 的 child |
| flip_top_lid | rec_container_cup_var_flip_top_lid | `_lid_solid` L119-195（**inlined 为 cup visual** L240）+ `_flap_panel` L198-225 + `cup_to_flap` REVOLUTE +X L270-282 | eligible if compatible | 固定盖 + 大翻嘴：盖 `lid_shell` 永久 union 进 `cup` part 的 visual（无 lift/twist joint），仅 `drink_flap` part 经 `cup_to_flap` REVOLUTE +X 翻开（**唯一 1 个 joint**，盖不可拆）|
| slide_close_ring | rec_container_cup_var_slide_close_ring | `_lid_solid` L117-192（含 center pivot boss + capture flange L167-181 + drink hole L184-191）+ `cup_to_lid` PRISMATIC +Z L256-264 + `_slide_ring_solid` L195-229 + `lid_to_slide_ring` REVOLUTE +Z L275-286 | eligible if compatible | snap 盖（`cup_to_lid` PRISMATIC +Z）+ 顶面 `slide_ring` part 绕 +Z REVOLUTE（origin@dome top center，q=0 闭合遮 drink hole、q=π 对位开）；ring 是 lid 的 child，captured pivot boss；2 joint |

硬约束记录：lid_closure 4 candidate（达 3-6 目标）。含 PRISMATIC（snap lift / slide 的 lid）+ REVOLUTE-twist（screw 绕 Z）+ REVOLUTE-flap（flip 绕 X）三种 joint 拓扑，且 part count/parent 拓扑不同（flip-top 盖 inlined 进 cup→少一个 part + 只 1 joint；snap/slide=lid 独立 part + 2 joint；screw=lid 直挂 cup REVOLUTE）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构；flip-top 由 flap REVOLUTE 兜底）。

### Slot C：handle_grip（提手 / 握持结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| ribbed_none（基线）| rec_paper-coffee-cup-with-a-white-snap-on-sip-lid-th_..._2eedb76c | `_cup_ribs` L102-124（仅竖肋防滑，无独立把手 / 无 joint）| eligible if compatible | 无独立把手：仅外壁竖肋 grip（防滑），空机构（不发射 handle part/joint）|
| loop_handle | rec_container_cup_var_loop_handle | `_loop_handle` L243-279（`tube_from_spline_points` C 形耳，两端 embed 进壁）+ cup visual `loop_handle` L294 | eligible if compatible | 侧 C 形马克杯耳把：swept tube 两端贴 +X 壁（固定 visual 挂 cup，无独立 joint，纯几何）|
| snap_sleeve | rec_container_cup_var_snap_sleeve | `_sleeve_body` L253-280 + `_sleeve_ridges` L283-321 + `sleeve` part + `cup_to_sleeve` PRISMATIC +Z L400-409 | eligible if compatible | 瓦楞防烫套筒：独立 `sleeve` part（锥形带 + corrugation ridges），`cup_to_sleeve` PRISMATIC +Z 沿杯壁上下滑配（friction fit），1 活动件 |
| fold_clip_handle | rec_container_cup_var_fold_clip_handle | `_bracket_solid` L261-291（cup visual `handle_bracket` L328）+ `_handle_bail_points` L294-312 + `carry_handle` part + `cup_to_handle` REVOLUTE -Y L404-413 | eligible if compatible | 可折叠 D-bail 提手：`handle_bracket` 固定 visual 挂 cup + `carry_handle`（bail wire）独立 part 经 `cup_to_handle` REVOLUTE axis=(0,-1,0) 水平铰（q=0 折平贴壁、正 q 摆出上翻 carry），captured pivot |

硬约束记录：handle_grip 4 candidate（达 3-6 目标）。含 none（空机构）/ 固定 visual（loop_handle 无 joint）/ PRISMATIC（snap_sleeve 独立 part）/ REVOLUTE（fold_clip_handle 独立 part）—— part count + joint 拓扑差异真实。可选轴：ribbed_none 表达"无 handle"。

## 槽位图（slot graph）

pattern: mixed（`cup` 为 root，坐地 z=0；lid / handle 挂到它；wall_pattern N 复制肋/棱面到 cup visual）

```
cup(body_form, wall_pattern N)   [ROOT, 坐地 z=0]
   │  (+ wall_pattern: N 根肋 _cup_ribs / N 块棱面 _facet_panel_i，cup 的固定 visual，无 joint)
   │
   ├── lid_closure = snap_lift_dome:
   │     cup --[cup_to_lid: PRISMATIC +Z @ rim, origin=(0,0,0) world]--> lid
   │            lid --[lid_to_sip_flap: REVOLUTE +X @ 盖后 rim hinge bar]--> sip_flap (child of lid)
   │
   ├── lid_closure = screw_twist_lid:
   │     cup --[cup_to_lid: REVOLUTE +Z @ (0,0,RIM_TOP_Z)]--> lid (cup外螺纹lug ↔ lid内螺纹lug)
   │            lid --[lid_to_sip_flap: REVOLUTE +X]--> sip_flap (child of lid)
   │
   ├── lid_closure = flip_top_lid:
   │     cup (lid_shell INLINED 为 cup 的固定 visual，无拆盖 joint)
   │     cup --[cup_to_flap: REVOLUTE +X @ 盖后 hinge bar]--> drink_flap   ← 唯一 joint
   │
   ├── lid_closure = slide_close_ring:
   │     cup --[cup_to_lid: PRISMATIC +Z]--> lid (dome 顶 center pivot boss + capture flange)
   │            lid --[lid_to_slide_ring: REVOLUTE +Z @ dome top center]--> slide_ring (child of lid)
   │
   ├── handle_grip = ribbed_none:        (无 handle part/joint)
   ├── handle_grip = loop_handle:         cup 固定 visual `loop_handle`（swept tube，无 joint）
   ├── handle_grip = snap_sleeve:         cup --[cup_to_sleeve: PRISMATIC +Z @ mid-wall]--> sleeve
   └── handle_grip = fold_clip_handle:    cup 固定 visual `handle_bracket`
                                          cup --[cup_to_handle: REVOLUTE -Y @ bracket ear pivot]--> carry_handle
```

接口点位与 joint 语义：
- **snap lift 接口**：`cup_to_lid` PRISMATIC，origin world `(0,0,0)`，axis +Z（q=0 盖坐 rim、正 q 直抬离）。盖 skirt 罩 over rim bead 是 captured / snap fit。
- **screw 接口**：`cup_to_lid` REVOLUTE，origin `(0,0,RIM_TOP_Z)`，axis +Z（q=0 拧紧、正 q 旋松 ~270°，无 Z 平移）。cup 外螺纹 lug（`_cup_threads`，`for i in range(N_THREADS)`）⊗ lid 内螺纹 lug（`_lid_threads`）captured 啮合（allow_overlap）。
- **flip-top 接口**：盖 inlined 进 cup（无拆盖 joint）；`cup_to_flap` REVOLUTE，origin 在盖后 hinge bar `(0, HINGE_Y, hinge_z)`，axis +X（q=0 翻嘴闭合、正 q 上翻 ~120°）。
- **slide 接口**：`cup_to_lid` PRISMATIC +Z；`lid_to_slide_ring` REVOLUTE，origin 在 dome top center `(0,0,z_top+LID_DOME_H)`，axis +Z（q=0 ring 体遮 drink hole、q=π 对位开），captured pivot boss + capture flange 防 ring 飞脱。
- **sip_flap 接口**（snap / screw 候选）：`lid_to_sip_flap` REVOLUTE，origin 在盖 `(0, HINGE_Y, hinge_z)`，axis +X，flap 是 **lid 的 child**（随盖抬升/旋拧 + 独立翻开）。
- **sleeve 接口**：`cup_to_sleeve` PRISMATIC，origin 在 mid-wall `(0,0,SLEEVE_REST_Z)`，axis +Z（friction fit 滑配，lower=-0.020 / upper=+0.030），sleeve 内壁罩 cup 外壁（captured，allow_overlap）。
- **handle 接口**：`cup_to_handle` REVOLUTE，origin 在 +X bracket ear pivot `(pivot_x,0,pivot_z)`，axis -Y（q=0 折平贴壁、正 q 摆出上翻 ~115°），bail captured 在 bracket ears（allow_overlap）。loop_handle 为固定 swept tube visual（两端 embed 进壁，allow_overlap，无 joint）。
- **mating policy**：盖 skirt 罩 rim / 螺纹 lug 啮合 / sleeve 罩壁 / bail captured 在 ear 均为 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 overlap（见各样本 run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有盖 q=0 闭合 / 坐下；sip_flap / drink_flap q=0 闭合盖嘴；slide_ring q=0 遮孔；sleeve q=0 mid-wall；carry_handle q=0 折平贴壁。lid 抬升/旋拧/翻起/ring 旋转/sleeve 滑动/handle 摆出为 viewer 目检的活动语义。
- **互斥 / 可选**：`handle_grip=ribbed_none` 是空机构；lid_closure 各候选互斥（一次只一种盖机构）；handle_grip 各候选互斥。`sip_flap` 仅 snap/screw 候选发射；flip-top 用 `drink_flap`（child of cup 而非 lid）；slide 用 `slide_ring`（无 sip_flap）。

## 每槽位 Module Emits / Interfaces

### Slot A / cup（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cup`（visual: `cup_shell`/`cup_body` shell + `cup_ribs` 或 `facet_panel_i`[ + handle 固定 visual]）| parent `_cup_shell` L62-99 / stemmed `_cup_body` L70-130 |
| internal joints | 无（root 杯体本身无活动件）| — |
| upstream interface | 坐地 z=0（root）| parent L250-252 inertial |
| downstream interface | rim top 中心 `(0,0,RIM_TOP_Z)`（lid joint parent 接口）+ mid-wall（sleeve）+ +X 壁（handle）| parent RIM_TOP_Z L40 |

### Slot B / lid_closure（每候选发射对应活动盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`(+`sip_flap`) / `lid`+threads(+`sip_flap`) / `drink_flap`(盖 inlined 进 cup) / `lid`+`slide_ring` | 各 lid 源 |
| internal joints | `cup_to_lid` PRISMATIC +Z + `lid_to_sip_flap` REVOLUTE +X（snap）/ `cup_to_lid` REVOLUTE +Z + `lid_to_sip_flap`（screw）/ `cup_to_flap` REVOLUTE +X（flip，唯一 joint）/ `cup_to_lid` PRISMATIC +Z + `lid_to_slide_ring` REVOLUTE +Z（slide）| parent L262-296 / screw L348-389 / flip L270-282 / slide L256-286 |
| upstream interface | rim top / 盖后 hinge bar / dome top center | 各源 origin |

### Slot C / handle_grip（≠ribbed_none 时）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（loop_handle 为 cup 固定 visual）/ `sleeve`（snap_sleeve）/ `handle_bracket` 固定 visual + `carry_handle`（fold_clip）| loop L243-294 / sleeve L386-399 / fold L383-402 |
| internal joints | 无（loop）/ `cup_to_sleeve` PRISMATIC +Z（sleeve）/ `cup_to_handle` REVOLUTE -Y（fold）| sleeve L400-409 / fold L404-413 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | tapered_cone / straight_cylinder / waisted_tumbler / stemmed_foot | tapered_cone | choice | deterministic procedural sampler 选 | module table |
| lid_closure | enum | snap_lift_dome / screw_twist_lid / flip_top_lid / slide_close_ring | snap_lift_dome | choice | sampler 选 | module table |
| handle_grip | enum | ribbed_none / loop_handle / snap_sleeve / fold_clip_handle | ribbed_none | choice | sampler 选；含空机构 | module table |
| wall_pattern_count (N) | int | [6, 60] | 56 | multiplicity | 杯壁竖肋/棱面复制数；加权采样（见 §Multiplicity）| parent `N_RIBS` L38 / n8 `N_FACETS` L36 |
| palette_style | enum | kraft_paper / glossy_white_ceramic / matte_black_ceramic / brushed_steel_tumbler / pastel_matte_ceramic / colorprint_plastic / enamel_camp / frosted_translucent / polished_copper_tumbler | kraft_paper | palette | palette only，9 配色 × 显式 finish 维度，**不计入 slot_choice**；per-seed `rng.choice(PALETTE_STYLES)` | palette（见下）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放杯高 CUP_H → RIM_TOP_Z → lid mount 高度，clamp | resolve clamp |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放杯身半径 BASE_R/RIM_R 同比 → neck/rim R 跟随，clamp（保盖罩配合）| resolve clamp |
| rim_radius_scale | float | [0.92, 1.08] | 1.0 | equation | `RIM_R = base · rim_radius_scale`；lid skirt bore / dome / 螺纹 lug 半径派生跟随（保盖罩 rim 配合）| resolve clamp |
| lid_dome_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放盖 dome 高 LID_DOME_H / skirt 深，clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 cup_to_lid lift 行程 / sleeve travel / flap·handle limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`lid_skirt_bore_R ≥ RIM_R + clearance` 且 `lid_outer_R ≤ body_R + proud`；sleeve `sleeve_bore_R ≥ wall_R_at_z + clearance`，违反按比例回缩 lid_dome/rim scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | `wall_pattern` 低 N（≤~10）走 facet_panel（棱面）形态、高 N 走 thin rib；棱面 half-width `r·tan(π/N)` 随 N 解析（见 n8 `_facet_panel` L128-129）| 接口 / multiplicity |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`rim_radius_scale` 为 equation（lid skirt bore / dome / 螺纹 lug 半径跟随 rim 半径，保盖罩 rim 配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / lid_closure / handle_grip 的拓扑或 N 的等价类。

**palette_style 配色（9 coordinated colorways × 显式 material-finish 维度，按 seed `rng.choice(PALETTE_STYLES)` 采样；palette-only，不改任何 slot/candidate/multiplicity/joint/dimension/topology）**，锚定 5★ 样本材质 RGBA（有据处直引，其余为同小类真实推断配色）。

每个 colorway 给四个语义构件色 + 一个 finish：**body**（杯身）/ **lid**（盖，含 sip_flap/drink_flap/slide_ring 等盖件）/ **handle_accent**（耳把/套筒/bail/螺纹 lug/底足等握持·配件）/ **print_band**（印刷·肋·缝·腰带等装饰带）。finish 为饮用杯/旅行马克杯/tumbler 的真实表面工艺。

| colorway | body rgba | lid rgba | handle/accent rgba | print/band rgba | finish | 锚点 / 来源 |
|---|---|---|---|---|---|---|
| `kraft_paper`（基线）| 牛皮纸 (0.74,0.55,0.36) | 白盖 (0.93,0.93,0.92) | 卡纸套筒 (0.70,0.50,0.30) | 深缝 (0.62,0.45,0.29) | **kraft 纸**（哑面纸质，纤维质感）| parent / 多数变体 `kraft_paper`/`kraft_seam`/`lid_white`/`corrugated_card` L235-238,318-321,327-331 |
| `glossy_white_ceramic` | 釉白 (0.95,0.95,0.94) | 浅灰盖 (0.86,0.85,0.83) | 浅灰配件 (0.82,0.81,0.80) | 浅灰肋 (0.80,0.79,0.78) | **陶瓷亮釉**（gloss glaze，高光镜面）| `ring_offwhite` (0.86,0.85,0.83) L238 一族亮白 |
| `matte_black_ceramic` | 哑黑 (0.14,0.14,0.16) | 深炭盖 (0.18,0.18,0.20) | 钢灰配件 (0.55,0.56,0.58) | 暗灰肋 (0.24,0.24,0.26) | **哑光陶瓷**（matte glaze，无反光）| `clip_plastic` (0.18,0.18,0.20) L321 + `bail_wire` (0.55,0.56,0.58) L322 一族暗色 |
| `brushed_steel_tumbler` | 拉丝钢 (0.66,0.67,0.69) | 钢灰盖 (0.58,0.59,0.61) | steel bail (0.55,0.56,0.58) | 暗钢腰带 (0.48,0.49,0.51) | **拉丝不锈钢**（brushed stainless，金属丝纹）| `bail_wire` (0.55,0.56,0.58) L322 金属 tumbler |
| `pastel_matte_ceramic` | 奶油陶瓷 (0.92,0.87,0.78) | 白盖 (0.93,0.93,0.92) | 浅褐配件 (0.80,0.73,0.63) | 浅褐肋 (0.80,0.73,0.63) | **哑光陶瓷**（pastel matte glaze，柔和粉调）| stemmed_foot `ceramic_cream` (0.92,0.87,0.78) + `ceramic_ribs` (0.80,0.73,0.63) L283-284 |
| `colorprint_plastic` | 品牌品红 (0.84,0.20,0.36) | 白盖 (0.93,0.93,0.92) | 白配件 (0.90,0.90,0.88) | 印刷描边 (0.30,0.28,0.32) | **亮面印刷塑料**（glossy printed plastic，饱和品牌色）| kraft 基线换印刷色（结构不变；推断真实彩印杯）|
| `enamel_camp` | 搪瓷蓝 (0.16,0.32,0.46) | 搪瓷蓝盖 (0.14,0.28,0.42) | 钢边·把手 (0.30,0.30,0.32) | 白边圈 (0.93,0.93,0.92) | **珐琅搪瓷**（enamel，瓷釉镀钢+黑边）| 经典露营 enamel mug（推断；钢边引 `bail_wire` 暗钢族）|
| `frosted_translucent` | 磨砂半透白 (0.88,0.90,0.91) | 半透盖 (0.82,0.85,0.87) | 半透配件 (0.78,0.82,0.85) | 浅蓝肋 (0.72,0.78,0.82) | **磨砂半透塑料**（frosted/translucent，霜面）| 推断真实磨砂 tumbler（offwhite 族提亮 + 冷调）|
| `polished_copper_tumbler` | 抛光铜 (0.72,0.45,0.30) | 暗铜盖 (0.58,0.36,0.24) | 铜配件 (0.66,0.41,0.27) | 暗铜腰带 (0.50,0.31,0.20) | **抛光铜·金属 tumbler**（polished copper，暖金属镜面）| 推断真实铜 moscow-mule tumbler（kraft 暖色族重定为金属铜）|

## Multiplicity / Copy Logic

- **count_param**: `wall_pattern_count`（杯壁竖肋 / 棱面复制数；单根独立 multiplicity 轴）。
- **N_range**: `[6, 60]`（本小类本轴产品域；6 = 粗壮少棱面 facet，60 = 细密肋。测试偏小、产品全程）。样本已覆盖 {56(parent), 12(n12_bold_flutes), 8(n8_facet_panels)}。
- **sampling domain**（权重档）：小 N 高频、大 N 稀有——典型饮用杯 8-24 道肋/棱面最常见；权重偏向 [8,28]，[28,60] 尾部稀有低频采样。
- **copied object**: 单根竖肋 lofted segment（`_cup_ribs` 内 `for i in range(N_RIBS)` 的 rib，parent L107-123）；低 N facet 形态时为单块 trapezoidal facet panel（n8 `_facet_panel(i)` L102-162，`for i in range(N_FACETS)` L287）。
- **naming**: 肋统一发射为一个 union 后的 `cup_ribs` visual（parent L249）；facet 形态每块独立命名 `facet_panel_{i}`（n8 L289）。
- **placement**: 绕杯轴等角 `ang = 2*pi*i/N`（parent L108 / n8 L113），沿 taper / contour 跟随半径（parent L109-112 / waisted `_profile_r` / stemmed `_bowl_radius_at`）。
- **joint policy**: 全部作为 `cup` part 的固定 visual（**无独立 joint**，随 root 走）。copy logic 在样本间完全隔离（除 N 与 n8 的 facet 形态外其余层保持 parent 基线）。
- **source/gating**: parent `_cup_ribs` L102-124（thin rib）；n8 `_facet_panel` L102-162（低 N 棱面，half-width `r·tan(π/N)` 随 N 解析）。`conditional`：N≤~10 走 facet panel、N>~10 走 thin rib（resolve 解析，见 §7 conditional 行）。

## 拓扑多样性审计

总组合数：body_form(4) × lid_closure(4) × handle_grip(4) = **64** 结构组合 × wall_pattern N 采样（≥3 distinct 已覆盖，产品域 [6,60] 远多）。

仅 body_form × lid_closure = **16 ≥ 10** 已可过门控；叠 handle_grip 后 64，再叠 N 充裕。

理由：本类拓扑多样性来源充裕——body_form(4) × lid_closure(4) = 16 distinct 已超 10；lid_closure 引入 PRISMATIC（snap/slide lid）/ REVOLUTE +Z（screw twist）/ REVOLUTE +X（flip 唯一 joint，盖 inlined 改 part count）/ PRISMATIC+REVOLUTE +Z（slide lid + ring）等不同 joint 拓扑 + 不同 part count；handle_grip 引入 none / 固定 visual / PRISMATIC sleeve part / REVOLUTE bail part；wall_pattern N 改 copied-object 数与（低 N）形态等价类。slot_choices 编入 body/lid/handle 三轴 + N 轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 gating 见下）+ 加权采样 N（小 N 偏多）+ uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除非法 / 适配派生组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 64×（N 等价类数）；受真实词汇表约束的结构轴是 64 组合（4 body × 4 lid × 4 handle），是该小类合理上限，不强行注水。低于 300 的原因：本小类真实结构词汇就是这 64 组合 + N multiplicity，N 把 distinct 拓扑等价类进一步抬高（thin-rib vs facet 两形态 + 不同 N 段）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / rim_radius / lid_dome / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`rim_radius_scale` 为 equation（lid skirt bore / dome / 螺纹 lug 半径派生跟随）。盖罩配合 + sleeve 配合不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 lid joint origin（rim top / 盖后 hinge / dome top center）、盖罩 rim 配合、sleeve/handle 接口或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交）+ 加权 N + uniform 各 scale + palette_style | slot_choices_for_seed 含 body/lid/handle/N 四轴且与 build 一致 |
| compatibility matrix | (1) 各 lid_closure 互斥、各 handle_grip 互斥。(2) `flip_top_lid` 盖 inlined 进 cup → 不发射 `lid` 独立 part / 不发射 sip_flap（用 `drink_flap`），resolve 解析 part 集。(3) `slide_close_ring` 需 dome 顶 pivot boss + capture flange → lid_dome_scale 下限保 boss 高度（resolve clamp）。(4) `snap_sleeve` 与 `fold_clip_handle` 的 mount 在 mid-wall / +X 壁，与任意 body_form 正交（sleeve bore / bracket r 按 `wall_R_at_z` 派生，stemmed 的 pedestal 区不挂 handle，挂 bowl 段）。(5) `screw_twist_lid` 螺纹 lug 半径随 rim_radius equation 派生。(6) N 低段（≤~10）走 facet 形态、高段走 thin rib（conditional）。无硬 gate-out（64 组合全合法，只在 resolve 派生尺寸适配）| 无 floating / collision / lid 穿杯 / sleeve·handle 穿壁 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；rim_radius equation 驱动 lid bore + 螺纹 lug | 比例变化不破坏 lid joint origin / 盖罩配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 盖动作 / sleeve·handle 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | 锥形 / 直壁圆柱 / 收腰 tumbler / 带 pedestal foot |
| lid_closure | 4 | yes | yes | snap-lift(PRIS+REV flap) / screw(REV Z) / flip-top(REV X 唯一,盖inlined) / slide-ring(PRIS+REV Z) |
| handle_grip | 4 | yes | yes | none / loop(固定 visual) / sleeve(PRIS part) / fold-bail(REV part) |
| wall_pattern (N) | [6,60] | — | — | multiplicity 轴：thin rib / 低 N facet，等角复制 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, lid_closure, handle_grip, wall_pattern_count) 四轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；N 加权采样（小 N 偏多）
- `resolve_config` 各 scale clamp 到声明范围；rim_radius equation 驱动 lid bore / 螺纹 lug；盖罩 + sleeve 配合不等式在 resolve 内投影 / 回缩；facet vs thin-rib 由 N conditional 解析
- compatibility matrix / gating：64 组合全合法（无硬 gate-out），flip-top 盖 inlined / 不发 sip_flap；slide 需 boss；sleeve·bracket 半径按 wall_R 派生
- 连续 scale clamp 后不破坏 lid joint origin / 盖罩配合 / 坐地 / 类别身份
- 关键 joint：snap `cup_to_lid` PRISMATIC +Z (abs(axis[2])>0.99) + `lid_to_sip_flap` REVOLUTE +X (abs(axis[0])>0.99)；screw `cup_to_lid` REVOLUTE +Z（origin@rim top，twist 无 Z 平移）；flip `cup_to_flap` REVOLUTE +X（唯一 joint，盖 inlined 进 cup visual）；slide `cup_to_lid` PRISMATIC +Z + `lid_to_slide_ring` REVOLUTE +Z；sleeve `cup_to_sleeve` PRISMATIC +Z；fold `cup_to_handle` REVOLUTE -Y (abs(axis[1])>0.99)
- copied objects：N 根肋 `cup_ribs` union / 低 N `facet_panel_{i}` 等角 placement（`ang=2πi/N`），全为 cup 固定 visual（无 joint）
- captured-fit：element-scoped `allow_overlap`（lid skirt ↔ cup shell/ribs；lid threads ↔ cup threads；slide ring ↔ lid；sleeve band ↔ cup wall/ribs；bail wire ↔ bracket）
- grandfather：盖罩 / 螺纹 / sleeve / bail captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用 boxy 占位体（纯 Box）当圆杯 body → 失类别身份；圆 body 必须 loft/extrude/revolve，开口腔。
- lid joint origin 放在杯底 / 任意点而非 rim top / 盖后 hinge / dome top center 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- flip_top_lid 仍发射独立可拆 `lid` part + lift joint（而非把盖 inlined 进 cup 只留 flap REVOLUTE）→ 盖语义错（flip-top 盖不可拆）。
- screw_twist_lid 用 PRISMATIC 抬升而非 REVOLUTE +Z 旋拧，或旋拧时 Z 高度漂移 → twist 语义错（应 origin@rim、绕 Z 无平移）。
- slide_close_ring 不给 dome 顶 capture flange，ring 直接飞脱 / 无 captured pivot → ring 漂浮 FAIL。
- lid_closure / handle rest pose 设成张开 / 抬起 / 摆出而非 q=0 闭合贴壁 → current-pose 与 viewer 目检不符。
- 给盖罩 / 螺纹 / sleeve / bail captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 把宽口储物罐 / 化妆罐塞回 body_form（wider-than-tall + screw 密封）→ 出 cup 语义（归 container_jar）。
- sleeve / handle 在滑动 / 摆出时穿杯壁 / origin 漂移 → 配合不等式或 origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_jar 带盖储物 / 化妆罐**（wider-than-tall 罐体 + screw-cap 密封）——理由：jar 是宽口储物罐身，cup 是直立饮用杯（taller-or-equal、饮用口径、sip/flip/slide 饮用盖）。
- 不该混入：**container_kettle 水壶**（spout 壶嘴 + 提梁 + 加热底座）——理由：kettle 有倒水壶嘴 + base，cup 无壶嘴、是直饮口。
- 不该混入：**container_bottle / container_glass_bottle 细颈瓶**（tall narrow neck）——理由：bottle 细长瓶身 + 长颈 + 螺纹瓶口，cup 是宽口饮用腔。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。4 body × 4 lid × 4 handle = 64 结构组合；body×lid=16 已过 地板。lid 槽自带 PRISMATIC/REVOLUTE-twist/REVOLUTE-flap 三种 joint 拓扑 + part-count 差异（flip-top 盖 inlined）。叠 wall_pattern N∈[6,60] multiplicity（thin rib / 低 N facet 两形态）。palette_style 9 配色（coordinated colorways × 显式 material-finish 维度：kraft 纸 / 陶瓷亮釉 / 哑光陶瓷 / 拉丝不锈钢 / pastel 哑光陶瓷 / 亮面印刷塑料 / 珐琅搪瓷 / 磨砂半透 / 抛光铜；palette-only，锚定 5★ RGBA，不计 slot_choice）。全 12 样本逐一全读。|

## 模板实现备注（可选）

- 共享 helper：`_cup_shell(body_form)`（loft 锥/圆柱、PROFILE loft 收腰）+ `_cup_body`（revolve pedestal+bowl，stemmed）+ `_cup_ribs(N)` / `_facet_panels(N)`（low-N 形态）+ `_lid_solid(lid_closure)` + `_flap_panel` + `_loop_handle` + `_sleeve_body`/`_sleeve_ridges` + `_bracket_solid`/`_handle_bail_points` 全 module 公用。
- flip-top 特殊：`_lid_solid` 结果 **union 进 `cup` 的 visual**（不发独立 lid part / 不发 sip_flap），仅 `drink_flap` part 经 `cup_to_flap` REVOLUTE；resolve 解析 part 集（少一个 part + 少一个 joint）。
- screw：cup 外螺纹 lug（`_cup_threads`，`for i in range(N_THREADS)`）+ lid 内螺纹 lug（`_lid_threads`），`cup_to_lid` REVOLUTE +Z origin@rim top；螺纹 lug 半径随 rim_radius equation 派生。
- slide：lid dome 顶 center pivot boss + capture flange（防 ring 飞脱），`lid_to_slide_ring` REVOLUTE +Z origin@dome top center。
- captured-fit overlap：`run_container_cup_tests` 复刻各样本 `ctx.allow_overlap`（lid skirt ↔ cup shell/ribs；lid threads ↔ cup threads；slide ring ↔ lid；sleeve band ↔ cup wall/ribs；bail ↔ bracket）。
- rim_radius equation：`resolve_config` 派生 `lid_skirt_bore_R = RIM_R + clearance`、`lid_outer_R = body_R + proud`、`sleeve_bore_R = wall_R_at_z + clearance`，配合不等式在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（同大类 body × lid × seal 三轴 parallel_children + screw/lift/flip lid 机构 + grandfather captured-fit 骨架，最接近）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig + config_from_seed + resolve_config clamp + slot_choices_for_config + allow_overlap 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | tapered_cone + snap_lift_dome + ribbed_none | rec_paper-coffee-cup-..._2eedb76c | `_cup_shell` L62-99 / `_cup_ribs` L102-124 / `_lid_solid` L127-206 / `cup_to_lid` PRISMATIC L262-270 / `_flap_panel` L209-236 / `lid_to_sip_flap` REVOLUTE L286-296 | 锥形杯 body 基线 + snap-lift 盖 + sip flap + 竖肋 multiplicity 基线 |
| S2 | A | straight_cylinder | rec_container_cup_var_straight_cylinder | `_cup_shell` L60-86（extrude 等径圆柱 + bead）/ `_cup_ribs` L89-106 | 直壁圆柱马克杯 body |
| S3 | A | waisted_tumbler | rec_container_cup_var_waisted_tumbler | `_cup_shell` L86-125（PROFILE loft 收腰）/ `_profile_r` L71-83 / `_cup_ribs` L128-162（contour-following） | 中段收腰 tumbler body + contour ribs |
| S4 | A | stemmed_foot | rec_container_cup_var_stemmed_foot | `_cup_body` L70-130（revolve pedestal foot+stem ∪ bowl loft）/ `_bowl_radius_at` L133-136 | 杯碗 + 细 stem + 喇叭 foot pedestal body |
| S5 | B | screw_twist_lid | rec_container_cup_var_screw_twist_lid | `_cup_threads` L164-170 / `_lid_threads` L200-206 / `cup_to_lid` REVOLUTE +Z L348-362 | 螺纹旋拧封口盖（cup/lid 螺纹 lug + 绕 Z 旋拧）|
| S6 | B | flip_top_lid | rec_container_cup_var_flip_top_lid | `_lid_solid` L119-195（inlined 为 cup visual L240）/ `cup_to_flap` REVOLUTE +X L270-282 | 固定盖 + 大翻嘴 flip-top（盖不可拆，唯一 flap joint）|
| S7 | B | slide_close_ring | rec_container_cup_var_slide_close_ring | `_lid_solid` L117-192（pivot boss + capture flange + drink hole）/ `_slide_ring_solid` L195-229 / `lid_to_slide_ring` REVOLUTE +Z L275-286 | snap 盖 + 顶面旋转环对位 drink hole |
| S8 | C | loop_handle | rec_container_cup_var_loop_handle | `_loop_handle` L243-279（tube_from_spline_points C 形耳）/ cup visual L294 | 侧 C 形马克杯耳把（固定 swept visual）|
| S9 | C | snap_sleeve | rec_container_cup_var_snap_sleeve | `_sleeve_body` L253-280 / `_sleeve_ridges` L283-321 / `cup_to_sleeve` PRISMATIC +Z L400-409 | 瓦楞防烫套筒（独立 part 上下滑配）|
| S10 | C | fold_clip_handle | rec_container_cup_var_fold_clip_handle | `_bracket_solid` L261-291 / `_handle_bail_points` L294-312 / `cup_to_handle` REVOLUTE -Y L404-413 | 可折叠 D-bail 提手（bracket visual + bail part REVOLUTE）|
| S11 | N | wall_pattern thin rib | rec_container_cup_var_n12_bold_flutes | `_cup_ribs` L100-122（N_RIBS=12，粗 flute circle 0.0025）| 竖肋 multiplicity 低 N 粗肋 |
| S12 | N | wall_pattern facet | rec_container_cup_var_n8_facet_panels | `_facet_panel(i)` L102-162（N_FACETS=8，`for i in range(N_FACETS)` L287，发 `facet_panel_{i}`）| 低 N 棱面 facet 形态（multiplicity conditional 形态）|
