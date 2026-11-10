# door — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `door` |
| template path | `agent/templates/Door_Door.py` |
| test path (optional) | `tests/agent/test_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（frame/casing(root) → leaf 的 REVOLUTE 竖铰 linear_chain 主脊；leaf → hardware 的可选 REVOLUTE/FIXED 子件 parallel_child；leaf 内 louver_panel 的 N-multiplicity 复制轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 17（6 parents + 11 variants；含两个 gap-fill fork `rec_door_var_fluted_sidelight_bar`（rating=5，由 P5 fork）/ `rec_door_var_ornate_s_pull`（rating=5，由 P3 fork），现已在磁盘上、已 sync、已读、已计入）|
| read_count | 17 |
| read_scope | all 5-star samples present on disk for this category（每个 `data/records/<id>/revisions/rev_000001/model.py` 全文读毕）|
| source_index_policy | only adopted module sources are indexed below |

读取清单（record_id → 简称）：

- P1 `rec_single-hinged-door-with-a-matte-dark-graphite-fi_20260606_115708_888790_d9a8adeb`（graphite glazed + lever/lock）
- P2 `rec_single-louvered-utility-door-gray-painted-steel-_20260606_115203_244494_72379bfd`（steel 2-louver + knob）
- P3 `rec_reflective-glass-door-with-ornate-curved-brass-p_20260606_115152_968871_61324bd6`（双扇 French 镜玻 + ornate S 拉手）
- P4 `rec_frameless-look-glass-door-a-large-clear-tempered_20260606_115151_982675_03743a3b`（无框清玻 + 固定侧板 + bar pull）
- P5 `rec_modern-dark-entry-door-with-a-tall-vertical-flut_20260606_115137_754364_286d9579`（暗色门 + 固定 fluted sidelight + bar pull）
- P6 `rec_single-hinged-interior-door-light-oak-wood-one-l_20260606_115124_332093_00107e3e`（oak raised-panel + lever）
- V1 `rec_door_var_solid_knob`、V2 `rec_door_var_solid_barpull`、V3 `rec_door_var_solid_louvered`
- V4 `rec_door_var_glazed_knob`、V5 `rec_door_var_glazed_barpull`、V6 `rec_door_var_glazed_louvered_split`
- V7 `rec_door_var_louvered_n1`、V8 `rec_door_var_louvered_n3`、V9 `rec_door_var_louvered_lever`
- V10 `rec_door_var_fluted_sidelight_bar`（由 P5 fork；plain-slab 叶升级为 TRUE 竖向 fluted 叶面，`for flute_i` 循环 + shared `_flute_rib_center` rib helper，保留 fixed fluted sidelight + bar pull）
- V11 `rec_door_var_ornate_s_pull`（由 P3 fork；更显著的多波黄铜 S 曲线拉手，THREE standoff necks `for standoff_i` 循环 vs 父 P3 的两个，swept-tube grip）

**结构变化轴观察**（用于 slot 划分）：

1. **叶面结构范式（leaf_style）** 是最大拓扑变化轴：实木 raised-panel（CadQuery routed groove + 1 proud panel）/ 竖向 glazed vision strip（through-cut + 独立 translucent pane）/ steel louver field（`VentGrilleGeometry`，N 块横百叶 + inter rail）/ full glass（独立 glass pane + edge trim，含双扇或侧板）/ fluted entry+sidelight（暗色叶 + 固定 fluted 侧灯；叶面本体可为 plain slab(P5) 或 TRUE 竖向 fluted 半圆 rib 阵列(V10)）。叶面差异改变 part tree、helper、primitive 与（full_glass 时）root 拓扑。
2. **操作五金（door_hardware）**：lever-on-rose（REVOLUTE +Y 子件，arm 摆）/ round knob（REVOLUTE +Y 子件，球转 或 KnobGeometry inline）/ straight bar pull（FIXED 或 inline，bar_tube + N standoff 循环）/ ornate S pull（spline tube + N standoff，bar pull 家族曲线变体；2-lobe+2 standoff(P3) 或 3-lobe+3 standoff(V11)）。差异改变 leaf 的子 part / joint 数与类型。
3. **louver_panel multiplicity**：N ∈ {1,2,3} 已样本覆盖（V7 N=1、P2/V9 N=2、V8 N=3），由 `for i in range(N)` + `louver_panel_i` + `inter_rail_j` + shared `_louver_panel` helper 复制；改变 leaf 内 visual 数量但不改 joint 拓扑（百叶是 leaf inline 视觉，不 jointed）。

**所有 15 个样本共享的不变主脊**：`frame/casing`(FIXED root) →（REVOLUTE，竖直轴 (0,0,±1)，origin 在 hinge 边竖线，limits 大致 `lower=0, upper≈1.6`）→ `leaf`。这是唯一 category-defining 主运动；hardware 子 joint 是次级、可选、低 effort 的 spindle 摆。

## 核心身份

Door = **单扇铰接门叶**（hinged door leaf），物理含义是一块沿竖直铰链边摆动的门扇，挂在一个固定门框/casing（两侧 jamb + head jamb，可含 sill/casing trim）上，门扇上携带一套操作五金（lever / knob / pull）。主功能 = 绕竖直铰轴开合（`frame_to_leaf` REVOLUTE）；次功能 = hardware 在门叶上的本地摆动（lever 压、knob 转）。默认成熟域 = 真实尺寸单扇门：叶宽 ~0.86–0.92 m、叶高 ~2.03–2.05 m、叶厚 ~0.040–0.045 m（玻璃门叶薄至 ~0.012 m），门框略大于叶并在 hinge 边以 lap/contact 支撑门叶。

**类别身份要素**（任何 seed 都必须成立）：

- root 是固定门框/casing，门叶是其唯一主运动子件，绕**竖直**铰轴（`abs(axis[2])≈1`）摆动，开合行程 ~0–1.6 rad。
- 门叶在 closed pose 下 hinge 边与 hinge jamb 接触/laps（不漂浮），open pose 下铰边仍连接、自由边扫入房间侧（±Y）。
- 门叶上有恰好一套主操作五金，位于 latch 边、~1.0–1.1 m 把手高度，凸出房间侧（+Y）。
- 站立在地面（zmin≈0），最高轴是 Z。

**不该混入的相邻类别**：Double Door / French Door（两扇均可动、center mullion，多一根 REVOLUTE 主脊）；Sliding Door（PRISMATIC 横移而非 REVOLUTE 摆）；Gate / 围栏门（户外栅栏立柱风格、不同 casing 语义）；Window / Casement（窗扇而非门，无地面落座、无 ~1.0 m 把手）。详见末节边界。

> full_glass 的 P3（双扇）与 P5（带 fixed sidelight）严格说带"第二扇可动叶"或"固定附加 bay"，与单扇主脊不完全正交。本 spec 把 full_glass / fluted_entry_sidelight 收为**单主动叶 + 可选固定附加 bay（side_panel / sidelight / mullion 都归 root 视觉，不可动）**的形态，**剔除"第二扇也可动"** 的 P3 双活叶语义（那属于 Double Door，移到边界节）。compatibility matrix 会限制这两个 leaf_style 只配 glass-friendly 的 bar/S pull，不混 knob/lever。

## 槽位 + 候选模块表

### Slot A：leaf_style（**主外观槽**——门叶面结构范式 + 是否带固定附加 bay）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| solid_raised_panel | P6 `rec_single-hinged-interior-door-light-oak-wood-one-l_...` | `_build_leaf_cq` L54-L94；frame+casing L126-L179；leaf visual L182-L189 | eligible if compatible | 实木 slab + routed border groove + 1 块 proud raised center panel（CadQuery cut+union），oak frame(jamb×2+head)+casing trim |
| solid_raised_panel | V2 `rec_door_var_solid_barpull` | `_build_leaf_cq` L78-L118 | eligible if compatible | 同 raised-panel 叶（与 P6 helper 同构），用于与 bar pull 配对的收敛记录 |
| glazed_vision_strip | P1 `rec_single-hinged-door-with-a-matte-dark-graphite-fi_...` | `_build_leaf_cq` L56-L79（through-cut vision opening）；`_build_glass_cq` L82-L90；leaf+pane L205-L220 | eligible if compatible | graphite flush slab，竖向窄玻通切 opening + 独立 translucent `vision_pane`，slim graphite frame |
| glazed_vision_strip | V4 `rec_door_var_glazed_knob` | `_build_leaf_cq` L62-L85；`_build_glass_cq` L88-L96 | eligible if compatible | 同 glazed 叶（与 P1 helper 同构），配 round knob |
| glazed_vision_strip | V6 `rec_door_var_glazed_louvered_split` | leaf rails/stiles/lock_rail L143-L167；`glass_pane`(upper) L173-L181；glazing beads loop L187-L200；`lower_louver_panel` L203-L208 | eligible if compatible | 上半 glazed vision pane + 下半单块 louver，中 lock rail 分隔（split 叶，N_louver=1）；展示 glazed 与 louver 在同一叶共存 |
| louvered_vented | P2 `rec_single-louvered-utility-door-gray-painted-steel-_...` | `_louver_panel` L85-L100；leaf rails/stiles/lock_rail L137-L165；upper+lower louver L170-L181；casing L113-L132 | eligible if compatible | steel 叶 + raised perimeter frame + 上下两块横百叶（N=2，手写 upper/lower）+ lock_rail；steel casing(head/sill/2 jamb) |
| louvered_vented | V3 `rec_door_var_solid_louvered` | `_build_leaf_cq`（带 recess）L65-L105；`_build_louver_panel_mesh` L108-L128 | eligible if compatible | oak 叶满铺 1 块 louver field（N=1，半凹陷 recess seat） |
| louvered_vented | V7 `rec_door_var_louvered_n1` | `_louver_panel` L80-L95；louver loop `for i in range(LOUVER_PANEL_COUNT)` L160-L166（N=1）| eligible if compatible | steel 叶单块满高 louver（N=1，已用循环范式，无 lock_rail）|
| louvered_vented | V8 `rec_door_var_louvered_n3` | `_louver_panel` L93-L108；inter_rail loop L169-L175；louver loop `for i in range(N_PANELS)` L181-L187（N=3）| eligible if compatible | steel 叶三块等高 louver + 两 inter_rail（N=3，**正式 multiplicity 范式**）|
| full_glass | P4 `rec_frameless-look-glass-door-a-large-clear-tempered_...` | `_glass_pane` L69-L80；`_edge_frame` L83-L100；`_root_surround` L103-L136；leaf L199-L208；side_panel(root) L184-L193 | eligible if compatible | 无框清玻 leaf（glass pane + dark edge frame）+ **固定 side_panel(root 视觉)** + hinge post surround |
| full_glass | P3 `rec_reflective-glass-door-with-ornate-curved-brass-p_...`（**仅取单叶 + frame helper**）| `_build_leaf` L137-L208（单侧 s 实例）；`_add_glass_trim` L211-L233；frame head/sill/jambs/mullion L100-L123 | eligible if compatible（**降级使用**：只采纳一侧 leaf 的 part tree + glass trim helper + frame，**不采纳第二活叶**）| 镜玻 leaf（glass + dark retaining trim）+ frame(含 center_mullion 作为 root 视觉)；第二扇在本 spec 内**固定**化为 root 附加 bay |
| fluted_entry_sidelight | P5 `rec_modern-dark-entry-door-with-a-tall-vertical-flut_...` | `_frame_with_sidelight` L92-L117；`_sidelight_glass`(flute loop) L120-L150；`_mullion` L153-L163；`_leaf_panel`(叶 + strip 开口) L166-L197；`_leaf_glass_strip` L200-L211 | eligible if compatible | 暗色 leaf（plain slab + 竖玻 strip）+ **固定 fluted sidelight bay(root)** + mullion；叶面本体是 plain slab（flute 仅在 sidelight 上）|
| fluted_entry_sidelight | V10 `rec_door_var_fluted_sidelight_bar`（由 P5 fork）| `_frame_with_sidelight` L97-L122；`_sidelight_glass`(flute loop) L125-L155；`_mullion` L158-L168；`_flute_rib_center`(shared rib helper) L171-L178；`_leaf_panel`(TRUE 竖向 fluted 叶 + `for flute_i` rib loop L217-L218 + rib union/trim L221-L243 + strip 开口) L181-L251；`_leaf_glass_strip` L254-L265；`_build_handle`(bar tube + 2 standoff) L268-L293 | eligible if compatible | **TRUE 竖向 fluted 叶面**：thin base plate + 一排等距竖向半圆 flute rib（`for flute_i in range(n_flutes)` + shared `_flute_rib_center` helper，rib union 进 plate 再 back-cut 成半圆突起）+ 竖玻 strip；保留 fixed fluted sidelight bay(root) + mullion + bar pull。修复 P5 plain-slab 叶为真正 fluted 叶 |

### Slot B：door_hardware（操作/开合五金机构，挂在 leaf 的 latch 边）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| lever_on_rose | P6 `rec_single-hinged-interior-door-light-oak-wood-one-l_...` | `_build_handle_cq`(rose+hub+neck+lever arm) L97-L116；part+visual L192-L206；`leaf_to_lever` REVOLUTE +Y L218-L226 | eligible if compatible | 压杆把手（rose+hub+neck+arm 单 mesh）绕 spindle(+Y) 转，lower=-0.5 upper=0 |
| lever_on_rose | P1 `rec_single-hinged-door-with-a-matte-dark-graphite-fi_...` | `_build_lever_cq` L93-L110；`_build_lock_cq`(FIXED escutcheon) L113-L167；`leaf_to_lever` L269-L277；`leaf_to_lock` FIXED L261-L267 | eligible if compatible | lever（仅 arm 转）+ 独立 FIXED `door_lock`（rose+backstrap+keyhole escutcheon，不随 lever 动）|
| lever_on_rose | V9 `rec_door_var_louvered_lever` | lever_rose visual L192-L200；`lever` part(arm+hub) L205-L231；`leaf_to_lever` REVOLUTE +Y L236-L244 | eligible if compatible | rose 作 leaf 静视觉，lever arm+hub 为独立 part，spindle +Y，press downward（upper=0.55）|
| round_knob | V1 `rec_door_var_solid_knob` | `_build_knob_cq`(rose+neck+sphere dome) L97-L127；part L203-L216；`leaf_to_knob` REVOLUTE +Y L228-L236 | eligible if compatible | 圆 domed knob（sphere dome + rose + neck）绕 spindle(+Y) 转，对称 ±0.8 |
| round_knob | V4 `rec_door_var_glazed_knob` | `_build_knob_cq`(oblate dome + back flat cut) L99-L149；`leaf_to_knob` L232-L240 | eligible if compatible | 圆 oblate domed knob（squash + back flat seat），±1.2 转 |
| round_knob | P2 `rec_single-louvered-utility-door-gray-painted-steel-_...` | `KnobGeometry`+grip+bore L186-L203；`knob_rose` L205-L210；`latch_plate`/`latch_keyhole` L213-L228 | eligible if compatible（**inline 降级**：KnobGeometry 圆 knob + rose + latch plate 是 leaf inline 视觉，无独立 knob joint）| SDK `KnobGeometry`(domed,knurled,round bore) inline + 圆 rose cyl + latch plate + keyhole boss（钢百叶叶上）|
| straight_bar_pull | V2 `rec_door_var_solid_barpull` | `_build_bar_tube_cq`(hollow tube) L121-L147；`_build_standoff_cq` L150-L166；bar+standoff loop `for i in range(NUM_STANDOFFS)` L243-L260 | eligible if compatible | 长竖直 hollow bar tube + 2 standoff（**循环 + name_i**，inline 视觉，无独立 joint）|
| straight_bar_pull | V5 `rec_door_var_glazed_barpull` | `_build_pull_bar_cq`(tube+end caps) L107-L132；`_build_standoff_cq`(base+post) L135-L159；`bar_pull` part L215-L236；`leaf_to_pull` FIXED L250-L256 | eligible if compatible | 独立 `bar_pull` part（tube + 2 standoff 循环），`leaf_to_pull` **FIXED** |
| straight_bar_pull | P4 `rec_frameless-look-glass-door-a-large-clear-tempered_...` | `_bar_handle`(back-to-back bars + through standoffs) L139-L172；leaf handle L204-L208 | eligible if compatible | 玻璃门双面 bar pull + through-glass standoff（玻璃叶专用，inline 视觉）|
| straight_bar_pull | P5 `rec_modern-dark-entry-door-with-a-tall-vertical-flut_...` | `_build_handle`(bar + 2 standoff) L214-L239；leaf handle L268-L272 | eligible if compatible | 长竖直 bar pull + 2 standoff（暗色叶，inline 视觉）|
| ornate_s_pull | P3 `rec_reflective-glass-door-with-ornate-curved-brass-p_...` | `_s_handle_points`(2-lobe S spline) L68-L87；`_add_brass_handle`(`tube_from_spline_points` + 2 standoff) L236-L272 | eligible if compatible | 波浪 S 曲线黄铜拉手（spline tube + 2 cylindrical standoff，玻璃叶专用，inline 视觉）|
| ornate_s_pull | V11 `rec_door_var_ornate_s_pull`（由 P3 fork）| `_s_handle_points`(3-lobe S spline，`for i in range(n)` n=19) L68-L91；`_standoff_neck_z`(shared standoff-Z helper) L94-L97；`_add_brass_handle`(`tube_from_spline_points` swept grip + `for standoff_i in range(3)` standoff loop) L246-L286 | eligible if compatible | 更显著多波 S 曲线黄铜拉手（3-lobe `sin(3πt)` swept spline tube + **THREE** standoff necks `for standoff_i in range(n_standoffs)` 循环 + shared `_standoff_neck_z` 等距 helper，玻璃叶专用，inline 视觉）。比 P3 多一波、多一根 standoff |

> **fluted_entry_sidelight 与 ornate_s_pull 的来源状态（单候选降级已解除）**：source map 早先把 `fluted_entry_sidelight` 与 `ornate_s_pull` 标为单候选值，并计划用两个 fork（`rec_door_var_fluted_sidelight_bar`、`rec_door_var_ornate_s_pull`）补成 ≥2。这两个 fork **现已在磁盘上、已 sync（rating=5）、已读全文**（V10 / V11）。因此**两者的单候选降级理由已解除**：
> - `fluted_entry_sidelight` 现有 **2 个真实来源**：P5（plain-slab 叶 + fixed fluted sidelight）与 V10（TRUE 竖向 fluted 叶面，`for flute_i` rib loop + shared `_flute_rib_center` helper，修复 P5 的 plain slab）。两个来源结构差异明确（plain slab 叶面 vs 半圆 rib 阵列叶面），不只是换尺寸/色。它仍归入"主动叶 + 固定附加 bay"装配家族（与 full_glass 共契约），compatibility matrix 中只与 bar pull 配对，sampling 权重较低（glass 叶家族），但**不再是单候选 slot**。
> - `ornate_s_pull` 现有 **2 个真实来源**：P3（2-lobe spline + 2 standoff）与 V11（3-lobe spline + 3 standoff `for standoff_i` 循环 + shared `_standoff_neck_z` helper）。两个来源结构差异明确（波数 2 vs 3、standoff 数 2 vs 3、是否走循环范式），符合"candidate 之间须有结构差异，非纯尺寸/色/装饰"。它属 bar-pull 家族曲线变体（与 straight_bar_pull 共享 standoff helper、spline tube vs 直 tube），仅 eligible 于 glass 叶、权重较低，但**不再是单候选 slot**。

每槽 candidate 计数：Slot A leaf_style = **5 distinct module（每个均 ≥2 来源，含 fluted = P5+V10）**；Slot B door_hardware = **4 distinct module（每个均 ≥2 来源，含 ornate = P3+V11）**。无 1-candidate slot，无需降级理由。

## 槽位图（slot graph）

pattern: `mixed`

```
[Slot A leaf_style → root frame/casing(FIXED)]
        │
        │  frame_to_leaf  (REVOLUTE, axis=(0,0,±1), origin=hinge 竖线,
        │                  limits lower=0 upper≈1.6, effort≈40)   ← 唯一主脊
        ▼
   [leaf]  ──(N-multiplicity)──► louver_panel_i  (inline 视觉, 无 joint;
        │                         inter_rail_j 分隔; 仅 louvered_vented)
        │
        ├─ Slot B = lever_on_rose / round_knob(turning variant):
        │     leaf_to_lever / leaf_to_knob  (REVOLUTE, axis=(0,±1,0),
        │     origin=latch 边 ~1.05m, low effort, small range)  ← 次级摆
        │     [+ 可选 leaf_to_lock FIXED escutcheon (P1 lever 变体)]
        │
        └─ Slot B = straight_bar_pull / ornate_s_pull / knob(inline) :
              leaf_to_pull (FIXED)  或  纯 inline 视觉(无 joint)
```

**接口点位 / 装配契约**：

- **A→root**：leaf_style 决定 root 形态。solid/glazed/louvered = frame(jamb×2+head[+sill/casing])，hinge jamb 内面在 hinge 竖线处 lap 门叶（HINGE_LAP≈0.004，contact 支撑）。full_glass/fluted = frame + **固定附加 bay（side_panel/sidelight/center_mullion 全部归 root 视觉**，hinge post/surround 提供 leaf 铰接锚）。
- **root→leaf 主脊**：`frame_to_leaf`(或 `casing_to_leaf` / `side_panel_to_leaf` / `frame_to_<side>_leaf`)，REVOLUTE，axis 竖直 `(0,0,1)` 或 `(0,0,-1)`（符号由 leaf-local +X/-X 朝向 + 开向决定），origin 在 hinge 边竖线（world `(hinge_x, 0, hinge_cz)`）。MatingContract：closed pose hinge 边与 hinge jamb / hinge post contact 或 expect_gap(max_pen≈0.006)；open pose 铰边仍 contact、自由边 AABB 越过 0.5·LEAF_W 进房间侧。
- **leaf→hardware（Slot B）**：mount 在 latch 边（leaf-local latch 侧），把手高度 ~1.0–1.1 m，凸出 +Y 房间面。
  - 摆动型（lever/turning knob）：REVOLUTE，axis=门法线 `(0,±1,0)`，origin 在 latch 边把手点；low effort（≈2–8），小行程；hardware 是独立 part。
  - 固定/内联型（bar pull FIXED、ornate S、inline knob）：`leaf_to_pull` FIXED，或直接作为 leaf 的 inline 视觉（bar_tube + standoff_i 循环 / spline tube + standoff）。
  - 可选附加：P1 lever 配独立 `door_lock` FIXED escutcheon（leaf 子件，不随 lever 动）。
- **leaf 内 multiplicity（louvered_vented 专属）**：`louver_panel_i`（i∈[0,N)）沿 leaf-local Z 等距，块间 `inter_rail_j`（j∈[0,N-1)）水平分隔；百叶板由 shared `_louver_panel` helper（VentGrilleGeometry，rpy=(±π/2,0,0) 使 face 落在 XZ、duct 沿 +Y）生成；**无独立 joint**（inline 视觉，随 leaf 摆）。

**互斥 / 可选 / 派生**：

- Slot B 摆动型（REVOLUTE lever/knob）与门法线轴绑定；bar/S pull 与 FIXED/inline 绑定——二者由 compatibility matrix gating（见 §拓扑多样性审计）。
- louver multiplicity 仅在 `leaf_style == louvered_vented` 时激活；其他 leaf_style 的 `louver_panel_count` 强制 = 0/不暴露。
- full_glass / fluted_entry_sidelight 的固定附加 bay 由 leaf_style 派生，非独立 slot。

## 每槽位 Module Emits / Interfaces

### Slot A / module solid_raised_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `door_frame`(hinge_jamb/latch_jamb/head_jamb/casing_*) + child `door_leaf`(leaf_body：routed groove + raised panel) | P6 / L126-L189 |
| internal joints | 无（叶为单 mesh）| P6 |
| upstream interface | hinge jamb 内面在 x≈0 lap leaf hinge 边（HINGE_LAP 0.004）| P6 / L130-L137 |
| downstream interface | `frame_to_leaf` REVOLUTE origin (0,0,SILL_Z=0) axis (0,0,1) | P6 / L209-L217 |

### Slot A / module glazed_vision_strip
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `door_frame`(slim graphite jamb×2+head) + `door_leaf`(leaf_body through-cut + 独立 `vision_pane` translucent) | P1 / L177-L220 |
| internal joints | 无（pane 随 leaf 视觉）| P1 |
| upstream interface | hinge jamb lap leaf hinge 边 | P1 / L180-L186 |
| downstream interface | `frame_to_leaf` REVOLUTE origin (0,0,0) axis (0,0,1) | P1 / L251-L259 |

### Slot A / module louvered_vented（含 multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `casing`(head/sill/right+left jamb) + `leaf`(top/bottom rail + hinge/latch stile [+ lock_rail] + `louver_panel_i`×N [+ inter_rail_j×N-1]) | P2 L113-L181 / V8 L121-L187 |
| internal joints | 无（百叶 inline）| P2 / V8 |
| upstream interface | hinge_stile 在 hinge_x=OPEN_W/2 与 right_jamb 内面 contact | P2 / L234-L243 |
| downstream interface | `casing_to_leaf` REVOLUTE origin (hinge_x,0,LEAF_CZ) axis (0,0,1) | P2 / L235-L243 |
| multiplicity emit | `louver_panel_i` via `for i in range(N)` + `_louver_panel` helper；`inter_rail_j` via `for j in range(N-1)` | V8 / L169-L187 |

### Slot A / module full_glass
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `side_panel`(side_glass + side_edge + root_surround/hinge post [+ side handle]) + child `glass_leaf`(leaf_glass + leaf_edge) | P4 / L184-L208 |
| internal joints | 无 | P4 |
| upstream interface | leaf hinge 边 glass/edge seat 在 root hinge post channel（allow_overlap） | P4 / L252-L261 |
| downstream interface | `side_panel_to_leaf` REVOLUTE origin (HINGE_X,0,Z_OFF) axis (0,0,-1) | P4 / L213-L221 |

> P3 作为 full_glass 第二来源时**只取单侧 `_build_leaf` 实例 + `_add_glass_trim` + frame(含 mullion 归 root)**；剔除第二个 `_build_leaf(... -1 ...)` 活叶（属 Double Door）。

### Slot A / module fluted_entry_sidelight
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `door_frame`(frame_perimeter + mullion + **fixed** sidelight_glass[竖 flute]) + child `door_leaf`(leaf_panel + leaf_glass_strip [+ bar_handle V10])；叶面本体 P5=plain slab / V10=TRUE 竖向 fluted rib 阵列 | P5 / L250-L267；V10 / L304-L326 |
| internal joints | 无 | P5 / V10 |
| upstream interface | leaf hinge 边 seat 在 frame jamb（hinge_overlap 0.008，allow_overlap）| P5 / L181-L189, L319-L325；V10 / L197-L201, L373-L379 |
| downstream interface | `frame_to_leaf` REVOLUTE origin (HINGE_X,0,Z_OFF) axis (0,0,-1) | P5 / L278-L286；V10 / L332-L340 |
| leaf flute emit（V10 专属）| TRUE 竖向 fluted 叶面：`for flute_i in range(n_flutes)` 经 shared `_flute_rib_center` helper 生成等距半圆 rib 阵列，rib union 进 base plate 后 back-cut 成半圆突起 | V10 / `_flute_rib_center` L171-L178, rib loop L217-L218, union/trim L221-L243 |

### Slot B / module lever_on_rose
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_handle`/`lever`(rose+hub+neck+arm 或 arm+hub) [+ 可选 FIXED `door_lock` escutcheon] | P6 L192-L206 / P1 L113-L167 |
| internal joints | `leaf_to_lever` REVOLUTE axis (0,1,0) low effort 小行程 [+ `leaf_to_lock` FIXED] | P6 L218-L226 / P1 L261-L277 |
| upstream interface | rose/hub seat 在 leaf latch 面（allow_overlap 穿叶）；arm 凸 +Y | P6 / L327-L335 |
| downstream interface | 叶末端 hardware，无下游 | — |

### Slot B / module round_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_knob`(rose+neck+sphere/oblate dome) 或 inline KnobGeometry+rose+latch_plate | V1 L203-L216 / P2 L186-L228 |
| internal joints | `leaf_to_knob` REVOLUTE axis (0,1,0) 对称小转（turning 型）；inline 型无 joint | V1 L228-L236 |
| upstream interface | knob rose seat 在 leaf latch stile（expect_contact / allow_overlap）| V1 L365-L372 |
| downstream interface | 无 | — |

### Slot B / module straight_bar_pull
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bar_pull`(pull_bar/bar_tube + `standoff_i`×2 循环) 或 leaf inline bar+standoff | V5 L215-L236 / V2 L243-L260 |
| internal joints | `leaf_to_pull` FIXED（独立 part 时）；inline 时无 joint | V5 L250-L256 |
| upstream interface | standoff base seat 在 leaf 面（allow_overlap）；bar 凸 +Y、竖直 | V5 L446-L450 |
| downstream interface | 无 | — |

### Slot B / module ornate_s_pull
| emits | 描述 | 来源 |
|---|---|---|
| parts | `*_handle_bar`(spline S tube) + `*_standoff_i`（cylindrical）inline 视觉；P3=2-lobe+2 standoff，V11=3-lobe+3 standoff（`for standoff_i in range(n)` 循环） | P3 / L236-L272；V11 / L246-L286 |
| internal joints | 无（FIXED/inline）| P3 / V11 |
| upstream interface | standoff seat 在 glass leaf 面（expect_contact handle_standoff_on_glass / `*_leaf_handle_standoff_i_on_glass`）| P3 / L351-L357；V11 / L373-L379 |
| downstream interface | 无 | — |
| standoff multiplicity emit | `*_standoff_i` via `for standoff_i in range(n_standoffs)` + shared `_standoff_neck_z` 等距 helper（n 固定 2(P3)/3(V11)，非 count_param）| V11 / `_standoff_neck_z` L94-L97, loop L276-L286 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| leaf_style | enum | solid_raised_panel / glazed_vision_strip / louvered_vented / full_glass / fluted_entry_sidelight | — | choice | deterministic procedural sampler 选择；gating 见 compatibility matrix | Slot A 表 |
| door_hardware | enum | lever_on_rose / round_knob / straight_bar_pull / ornate_s_pull | — | choice | sampler 选择；受 leaf_style gating（glass 叶不配 knob/lever）| Slot B 表 |
| louver_panel_count | int | [1, 6]（产品域）；样本覆盖 {1,2,3}；测试偏小 N | 2 | conditional | 仅 `leaf_style==louvered_vented` 时有效；其它 leaf_style 强制 0/不暴露；加权小 N 偏多 | V7/V8/P2 §Multiplicity |
| hardware_mount_mode | enum(derived) | revolute_spindle / fixed / inline | — | conditional | 由 door_hardware 派生：lever/turning knob→revolute_spindle；bar/S pull→fixed/inline；KnobGeometry→inline | Slot B 表 |
| leaf_width_scale | float | [0.95, 1.06] | 1.0 | independent | clamp；叶宽 = LEAF_W·scale，保持 0.82–0.95 m 真实域 | P6 L32 / P2 L39 |
| leaf_height_scale | float | [0.98, 1.03] | 1.0 | independent | clamp；叶高保持 1.98–2.10 m（测试 leaf_height_realistic）| P6 L33 |
| leaf_thickness | float | derived | — | equation | `= 0.012 (glass 叶) / 0.040–0.045 (实/钢/木叶)`，由 leaf_style 派生，不独立采样 | P4 L33 / P6 L34 |
| open_angle_upper | float | [1.4, 1.7] | 1.6 | independent | hinge motion_limits.upper；下限固定 0（closed）| 所有 P/V hinge limits |
| handle_height | float | [1.00, 1.10] | 1.05 | independent | clamp；hardware origin world z；测试 handle_at_lever_height | P6 L195 / V1 L206 |
| louver_slat_pitch | float | [0.024, 0.034] | 0.026–0.032 | independent | clamp；VentGrille slat_pitch（仅 louvered）| P2 L94 / V3 L57 |
| frame_face_scale | float | [0.9, 1.15] | 1.0 | independent | clamp；jamb/casing face 宽缩放，须保持 opening = leaf + 2·reveal | P2 L46-L55 |
| palette_style | enum | light_oak / dark_graphite / white_painted / steel_gray / clear_glass_brass / glass_steel | — | choice | 每 seed 抽一种 colorway（见下）；纯换色不改拓扑 | 见下 palette |
| (—) | constraint | — | — | inequality | `frame opening_w = leaf_w·leaf_width_scale + 2·reveal`；`opening_h = leaf_h·leaf_height_scale + 2·reveal`；违反则按比例回缩 reveal/frame_face | 接口 / clearance |
| (—) | constraint | — | — | inequality | louvered: `N·panel_h_min + (N-1)·inter_rail ≤ inner_h`（inner_h = leaf_h - 2·rail）；超出则降 N 或拒绝重采（板太薄）| V8 L71-L72 |
| (—) | constraint | — | — | conditional | glass 叶（full_glass/fluted/glazed 的玻璃 bay）只接受 hardware ∈ {straight_bar_pull, ornate_s_pull}；solid/louvered/glazed-strip 钢/木叶接受全部 4 种 | compatibility matrix |

**palette_style colorway（≥3，目标 4–6；均观测自 5★ 源）**：

| palette_style | leaf 材质/色 | frame/casing 色 | hardware 色 | glass 色(若有) | 观测来源 |
|---|---|---|---|---|---|
| light_oak | light_oak (0.82,0.66,0.45) | oak_shadow (0.66,0.50,0.33) | brushed_steel (0.74,0.76,0.78) | — | P6/V1/V2/V3 |
| dark_graphite | graphite (0.20,0.21,0.23) | graphite_frame (0.15,0.16,0.18) | brushed_steel / knob_brass (0.72,0.62,0.38) | vision_glass (0.78,0.85,0.88,0.35) | P1/V4/V5 |
| steel_gray | gray_steel (0.55,0.56,0.57) | gray_steel_dark (0.42,0.43,0.45) | brushed_metal (0.72,0.72,0.74) | clear_glass (0.82,0.88,0.90,0.35) | P2/V7/V8/V9/V6 |
| dark_entry | leaf_dark (0.16,0.16,0.175) | frame_graphite (0.13,0.13,0.145) | brushed_steel (0.78,0.79,0.81) | glass_tinted (0.62,0.70,0.74,0.34) | P5 |
| glass_brass | clear/reflective glass (0.62,0.70,0.74,0.45) | dark_frame (0.12,0.12,0.14) | brass (0.76,0.58,0.22) | — | P3 |
| glass_steel | clear_glass (0.72,0.80,0.84,0.28) | dark_edge (0.10,0.10,0.11) | brushed_steel (0.80,0.81,0.83) | — | P4 |

palette_style 与 leaf_style 有弱兼容偏好（glass_brass/glass_steel 偏配 full_glass/glazed；light_oak 偏配 solid/louvered-oak），但允许跨配以增色彩多样性；sampler 按 leaf_style 加权抽 palette，纯换色不计拓扑变更。

## Multiplicity / Copy Logic

本类别有 **1 根模板级复制轴**（louver_panel_count）。其余重复（bar pull standoff、glazing bead）是固定 2/4 个、非 count_param。

**轴 1：louver_panel_count**（门叶内横百叶 vented 板的堆叠块数）

- `count_param`: `louver_panel_count`
- `N_range`: **[1, 6]**（产品域；样本覆盖 {1,2,3}）。采样域可大于样本覆盖；实门极少 >5（N>5 板趋薄）。
- sampling domain（权重档）：小 N 高频、大 N 稀有——建议 `N=1` ~25%、`N=2` ~35%、`N=3` ~25%、`N=4` ~10%、`N=5` ~4%、`N=6` ~1%（测试偏 N≤3，产品全程；参照 template_test_vs_product_N_domain）。
- copied object: 一块横百叶 VentGrille 板（shared helper `_louver_panel(width,height,name)` → `VentGrilleGeometry`，rpy=(±π/2,0,0)）。
- naming: `louver_panel_i`（i∈[0,N)）；分隔 rail `inter_rail_j`（j∈[0,N-1)）。
- placement: 沿 leaf-local Z 等距，`PANEL_CZ[i] = BOT_INNER + i·(PANEL_H+INTER_RAIL) + PANEL_H/2`，`INTER_RAIL_CZ[j]` 居于相邻板间（见 V8 L78-L85）；居中于 leaf X。
- joint policy: 百叶板为 leaf 的 **inline 视觉（非 jointed 装饰）**，门叶整体走 `casing_to_leaf`/`frame_to_leaf` REVOLUTE 这一唯一摆动；百叶不单独 articulate。
- source/gating: V8 `rec_door_var_louvered_n3` 是正式循环范式（L169-L187）；V7 N=1（L160-L166）；P2 N=2（手写 upper/lower，正式模板按 V8 统一为循环）；V3 N=1（oak 满铺，`_build_louver_panel_mesh`）。**仅 `leaf_style==louvered_vented` 激活**；其它 leaf_style `louver_panel_count` 不暴露（=0）。

**次级重复轴（非 count_param，固定数量，强制 `for i in range(n)` + name_i 循环）**：

- bar pull 的 standoff：`standoff_i`，n=2 固定（V2 L254-L260、V5 L229-L236）。
- glazed_louvered_split 的 glazing bead：`glazing_bead_i`，n=4 固定（V6 L193-L200）。
- ornate S pull 的 standoff：`*_standoff_i`，n∈{2,3}（P3 n=2 L260-L272；V11 n=3 已用 `for standoff_i in range(n_standoffs)` 循环 + shared `_standoff_neck_z` 等距 helper L276-L286）。n 随所选 ornate_s_pull 来源固定（非加权 count_param），正式模板统一走循环 + name_i。

这些非 count_param，不进入加权采样，但实现时统一用循环 + name_i 命名以保持一致性。

## 拓扑多样性审计

```
总组合数（合法、经 compatibility gating）：

leaf_style(5) × door_hardware(4) × louver_panel_count(N 采样, 仅 louvered)

朴素上限：5 × 4 = 20（不含 N）。
计入 louvered_vented 的 N∈[1,6] 6 档：
  - 非 louvered 的 4 个 leaf_style × hardware 合法格：见 gating 后约 4×(3.x) ≈ 14（glass 叶限 2 种 hardware）
  - louvered_vented × hardware(4) × N(6) = 24
  合计合法 (leaf_style,hardware,N) 拓扑等价类 ≈ 14 + 24 = 38（>> 10）

朴素 leaf_style×hardware = 20 已 ≥ 10；计 N 后 ≈ 38。

注：组合数（拓扑等价类）不因新增 V10/V11 改变——二者是既有 module（fluted_entry_sidelight / ornate_s_pull）下的**第二个候选来源**，强化了来源稳健度但不新增拓扑分支。现 5 个 leaf_style 与 4 个 door_hardware **全部 ≥2 真实来源**，无单候选 slot。
```

理由：单 leaf_style(5)×hardware(4)=20 已 ≥10；louver N 轴再乘 6 档，合法拓扑等价类 ≈38。palette/scale 是连续/着色变化，不计入 slot choice tuple distinct，但 1000-seed 下 (leaf_style,hardware,N,mount_mode) 组合按 ≥300 富类别口径观察 之下限的合理范围；door 类别拓扑骨架有限（单脊门），故 slot choice tuple distinct 目标设 **≥30**（低于 300，原因：door 主脊固定、可动件少、leaf_style×hardware×N 是全部拓扑自由度），其余多样性来自 palette/连续 scale。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng`(或 seeded RNG) 依序：(1) 抽 `leaf_style`（5 等权或轻偏 solid/louvered）；(2) 依 leaf_style 经 compatibility matrix 抽合法 `door_hardware`；(3) 若 louvered_vented，按权重档抽 `louver_panel_count`，否则=0；(4) 派生 `hardware_mount_mode`、`leaf_thickness`；(5) 抽 `palette_style`（按 leaf_style 加权）；(6) 抽 independent 连续 scale（leaf_width/height_scale、open_angle_upper、handle_height、louver_slat_pitch、frame_face_scale），`resolve_config` 内派生 equation 并用 inequality 投影/回缩（opening=leaf+2·reveal；N·panel_h_min+(N-1)·inter_rail≤inner_h），不可行则回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回 `[("leaf_style",<m>),("door_hardware",<m>)]`（连续 scale 默认不记，除非改拓扑等价类——louver_panel_count 因改 visual 数量，建议作为 multiplicity 记号附带 N）。

Topology target：1000-seed slot choice tuple distinct 建议 ≥30（见上理由，低于富类别建议 300 是因 door 拓扑骨架窄）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

regression overrides：none（首版不需要；如 sweep 出现特定失败格再按 seed + 失败原因稀疏添加）。不得用 curated/modulo 表作主 seed domain。

Controlled local parameterization：初版应含 `leaf_width_scale`、`leaf_height_scale`、`open_angle_upper`、`handle_height`、`louver_slat_pitch`、`frame_face_scale`（范围/约束见 §7）。全部在 `resolve_config` clamp/派生，遵守连续尺寸采样契约（先 independent → 派生 equation → 投影/回缩 inequality → 解析 conditional 范围）。这些 scale 只改安全比例（叶尺寸、开角、把手高、百叶间距、框面宽），不破坏 frame_to_leaf 铰接 origin、hinge lap contact、hardware mount contact、louver 多重性或 category identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | leaf_style→hardware(gated)→louver_N(weighted, louvered only)→palette→连续 scale | `slot_choices_for_seed` 与 build 选择一致 |
| compatibility matrix | glass 叶(full_glass/fluted/玻璃 bay)只配 {straight_bar_pull, ornate_s_pull}；ornate_s_pull/fluted 权重略低（glass 叶家族，非主流叶型），均已有 2 来源；louver_N 仅 louvered_vented；摆动型 hardware 须门法线轴 | 无 floating（hinge 边 contact）、无 collision、铰轴竖直、open/closed pose 合法、N≤6、glass 叶不挂 knob/lever（不真实）、可选 lock/lever child 不漏 |
| controlled local variation | leaf/height/frame/slat/handle/open_angle scale，clamp + 派生 | 比例变化不破坏接口、clearance、铰 origin、把手 contact、category identity |
| regression overrides | none | 仅已知失败回归 / 审核指定（首版无）|
| random sweep | seeds 0-49 初轮，0-999 成熟度审计 | 与 MatingContract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A leaf_style | 5 | yes | yes | solid/glazed/louvered/full_glass 各 ≥2 源；fluted 现 2 源(P5 plain-slab + V10 TRUE fluted)，单候选降级已解除；仍归 glass 叶家族 + gating |
| B door_hardware | 4 | yes | yes | lever/knob/bar 各 ≥2 源；ornate_s_pull 现 2 源(P3 2-lobe/2-standoff + V11 3-lobe/3-standoff)，单候选降级已解除；bar-pull 家族曲线变体 + 仅 glass 叶 gating |
| multiplicity louver_panel_count | N∈[1,6]（样本 {1,2,3}）| yes | yes(3 distinct) | 仅 louvered_vented |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（leaf_style ∈ 5、door_hardware ∈ 4）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊
- compatibility matrix / gating 阻止非法组合（glass 叶配 knob/lever；louver_N 在非 louver 叶激活）
- regression overrides 稀疏且有理由（首版无）
- 不把小型 curated 表当主 seed domain
- 受控局部 scale 被 clamp，无法破坏接口、clearance、铰 origin、louver 多重性（opening=leaf+2·reveal、N·panel_h_min+(N-1)·inter_rail≤inner_h 等不等式在 `resolve_config` 求解）
- cross-part scale 依赖（equation/inequality/conditional）在 `resolve_config` 解决，不留到 builder 失败
- 关键 InterfaceSpec/MatingContract 存在：hinge 边 closed lap/contact、open 仍连接、hardware seat 在 leaf 面
- 关键 joint 类型/轴/range：`frame_to_leaf` REVOLUTE 竖轴(abs axis[2]≈1) lower=0 upper∈[1.4,1.7]；摆动 hardware REVOLUTE 门法线轴(abs axis[1]≈1) low effort；bar pull FIXED
- 复制对象遵循命名/placement：`louver_panel_i` / `inter_rail_j` / `standoff_i` 循环、等距、居中

## Reject cases

- 铰轴非竖直（abs(axis[2]) 不≈1）或门叶不绕 hinge 边摆 → 非 door 主脊。
- closed pose 门叶 hinge 边与 hinge jamb/post 无 contact（门叶漂浮）或 penetration > ~0.006。
- open pose 铰边失联（leaf origin 漂移）或自由边未扫入房间侧。
- glass 叶（full_glass/fluted/玻璃 bay）配 round_knob/lever_on_rose（不真实，gating 必须拦）。
- `louver_panel_count` 在非 louvered_vented 叶被激活，或 louvered 叶 N=0（无百叶却称 louver）。
- N 过大致板厚 < 物理下限（N·panel_h_min+(N-1)·inter_rail > inner_h 未回缩）→ 板穿模/趋零厚。
- hardware 不在 latch 边或把手高度偏离 ~1.0–1.1 m，或未凸出 +Y 房间面。
- frame opening 与 leaf 尺寸不匹配（opening ≠ leaf+2·reveal）→ 门叶卡死或大缝。
- full_glass/fluted 的附加 bay 被误做成第二**可动**叶（变成 Double Door）。
- 把第二活叶 / 横移 / 户外栅栏立柱混入（越界相邻类别）。

## 与相邻类别的边界

- 不该混入：**Double Door / French Door**（理由：两扇均可动 + center mullion，多一根 REVOLUTE 主脊；本类别只保留单主动叶，full_glass/fluted 的第二 bay 固定化为 root 视觉。磁盘上的 `rec_variant-door-mechanism-french-*` 双活叶记录不在本 source map，属 Double Door 范畴）。
- 不该混入：**Sliding Door**（理由：PRISMATIC 横移轨道，非 REVOLUTE 竖铰摆，主脊运动类型不同）。
- 不该混入：**Gate / 围栏门**（理由：户外栅栏立柱/横杆语义、无室内 frame+casing+~1.0m 把手，casing 与材质家族不同）。
- 不该混入：**Window / Casement**（理由：窗扇非门，无地面落座/zmin≈0 约束、无 ~1.0 m 操作把手；本类别 leaf 必须站立落地且带门把手高度的 hardware）。
- 不该混入：**纯五金件（lock / handle set）单品**（理由：本类别 hardware 必须是挂在门叶上的子件，不作独立 root）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。注意：(1) **单候选降级已解除**：先前 `rec_door_var_fluted_sidelight_bar`（V10）/ `rec_door_var_ornate_s_pull`（V11）两个 gap-fill fork 现已在磁盘上、已 sync（均 rating=5）、已读全文并计入（five_star_total 15→17）。fluted_entry_sidelight 现有 2 真实来源（P5 plain-slab 叶 + V10 TRUE 竖向 fluted rib 叶），ornate_s_pull 现有 2 真实来源（P3 2-lobe/2-standoff + V11 3-lobe/3-standoff 循环），两组 candidate 结构差异明确，**已无单候选 slot、无需降级理由**。(2) V11 源记录本体是双活叶 French door（与 P3 同），本 spec 只采纳其 ornate_s_pull 五金 module（Slot B），不引入其第二活叶；其玻璃叶若入 Slot A 仍按 P3 同款"单叶降级"处理（剔除第二活叶，归 Double Door 边界）。(3) full_glass 第二来源 P3 是双活叶 French door，本 spec 仅采纳其单叶 part tree + frame，剔除第二活叶（归 Double Door）——请确认。|

## 模板实现备注（可选）

- shared helper：louver 用 `_louver_panel`（VentGrilleGeometry，统一 rpy=(±π/2,0,0)）；CadQuery 叶（solid/glazed/fluted）共享 routed-groove / through-cut / fillet 模式；fluted 叶（V10）的竖向半圆 rib 阵列用 shared `_flute_rib_center(flute_i,...)` rib helper + `for flute_i in range(n)` 生成、union 进 base plate 再 back-cut，与 sidelight flute loop 同 pitch；bar pull 与 ornate S pull 共享 standoff helper（直 tube vs spline tube 仅换 bar 几何），ornate S 的 standoff 走 `for standoff_i in range(n)` + shared `_standoff_neck_z` 等距 helper（V11，n=3）。
- multiplicity 统一按 V8 `rec_door_var_louvered_n3` 的 `for i in range(N)` + `louver_panel_i` + `inter_rail_j` 范式实现；P2/V3 的手写 1~2 块在正式模板里改为循环。
- captured/seat overlap 需 element-scoped `allow_overlap`：hinge 边 lap hinge jamb（`leaf_body`↔`hinge_jamb` / `hinge_stile`↔`right_jamb`）、hardware rose/standoff seat 在 leaf 面、lever hub 穿 latch stile、glazed pane lap glazing rim、full_glass leaf edge seat 在 hinge post channel、louver panel 半凹陷 recess（V3）。
- 玻璃门叶（full_glass/fluted）的 root 拓扑（side_panel/sidelight/mullion 全归 root 视觉 + hinge post 提供铰锚）与单 frame 叶不同，实现时按 leaf_style 分两套 root factory；compatibility matrix 须确保它们只配 bar/S pull。
- 摆动 hardware（lever/turning knob）axis 必须门法线 (0,±1,0)、低 effort、小行程；bar/S pull 用 FIXED 或 inline，避免给纯拉手错配 REVOLUTE。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P1 | A / B | glazed_vision_strip / lever_on_rose(+lock) | rec_single-hinged-door-...graphite... | A:L56-90,L177-220 / B:L93-167,L261-277 | glazed 叶 part tree + lever 仅-arm 转 + FIXED escutcheon |
| P2 | A / B | louvered_vented(N=2) / round_knob(inline) | rec_single-louvered-utility-...steel... | A:L85-100,L113-181 / B:L186-228 | steel louver 叶 + casing + KnobGeometry inline knob/latch |
| P3 | A / B | full_glass(单叶降级) / ornate_s_pull | rec_reflective-glass-...brass... | A:L100-123,L137-233 / B:L68-87,L236-272 | 单叶 glass+trim+frame(mullion 归 root) + S spline 拉手 |
| P4 | A / B | full_glass / straight_bar_pull | rec_frameless-look-glass-...tempered... | A:L69-136,L184-221 / B:L139-172 | 无框玻璃叶 + 固定 side_panel + 双面 bar pull |
| P5 | A / B | fluted_entry_sidelight / straight_bar_pull | rec_modern-dark-entry-...fluted... | A:L92-211,L250-286 / B:L214-239 | 暗色叶 + 固定 fluted sidelight + bar pull |
| P6 | A / B | solid_raised_panel / lever_on_rose | rec_single-hinged-interior-...oak... | A:L54-94,L126-189 / B:L97-116,L218-226 | oak raised-panel 叶 + lever-on-rose REVOLUTE |
| V1 | B | round_knob(turning) | rec_door_var_solid_knob | L97-127,L228-236 | sphere domed knob REVOLUTE +Y |
| V2 | A / B | solid_raised_panel / straight_bar_pull(inline) | rec_door_var_solid_barpull | A:L78-118 / B:L121-166,L243-260 | raised 叶 + bar tube + standoff_i 循环 |
| V3 | A / B | louvered_vented(N=1) / lever_on_rose | rec_door_var_solid_louvered | A:L65-128 / B:L131-150 | oak 满铺 louver field + lever |
| V4 | A / B | glazed_vision_strip / round_knob(turning) | rec_door_var_glazed_knob | A:L62-96 / B:L99-149,L232-240 | glazed 叶 + oblate knob REVOLUTE |
| V5 | A / B | glazed_vision_strip / straight_bar_pull(FIXED) | rec_door_var_glazed_barpull | A:L72-104 / B:L107-159,L215-256 | glazed 叶 + bar_pull part + leaf_to_pull FIXED |
| V6 | A / B | glazed_vision_strip(split+louver) / round_knob(inline) | rec_door_var_glazed_louvered_split | A:L86-101,L143-208 / B:L213-255 | 上 glazed pane + glazing_bead_i 循环 + 下 louver |
| V7 | A | louvered_vented(N=1, loop) | rec_door_var_louvered_n1 | L80-95,L160-166 | 单块满高 louver（循环范式）|
| V8 | A | louvered_vented(N=3, loop) | rec_door_var_louvered_n3 | L93-108,L169-187 | 三块 louver + inter_rail（正式 multiplicity 范式）|
| V9 | B | lever_on_rose | rec_door_var_louvered_lever | L192-200,L205-244 | rose 静视觉 + lever part(arm+hub) REVOLUTE press |
| V10 | A / B | fluted_entry_sidelight(TRUE fluted 叶) / straight_bar_pull | rec_door_var_fluted_sidelight_bar | A:L97-122,L158-168,L171-251,L254-265,L304-340 / B:L268-293 | TRUE 竖向 fluted 叶面(`for flute_i` + shared `_flute_rib_center` rib helper) + fixed fluted sidelight + bar pull（修复 P5 plain-slab 叶）|
| V11 | B | ornate_s_pull(3-lobe/3-standoff) | rec_door_var_ornate_s_pull | L68-91,L94-97,L246-286 | 3-lobe swept spline S 拉手 + THREE standoff(`for standoff_i` 循环 + shared `_standoff_neck_z` 等距 helper)（P3 fork，多一波/多一根 standoff）|
