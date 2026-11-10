# Wine Cabinet Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wine_cabinet` |
| template path | `agent/templates/wine_cabinet.py` |
| test path (optional) | — |
| stage | `TEMPLATE_IMPLEMENTED` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed` |

## Category Binding

category_slug: `wine_cabinet` · template_slug: `wine_cabinet` · mechanism_profile: `multi_access_cabinet` · export_namespace: `wine_cabinet`

diversity_profile: `compositional` · diversity_profile_reason: six source-backed body forms, five reachable door states, four rack fabrics and three service states form 125 stable compatibility-gated core combinations; drawer and bottle counts are audited separately as multiplicity.

canonical source map: `articraft_data/picture_expansion/template_source_maps/0611__wine_cabinet.md`; all three originals and sixteen variants are user-approved and bound there to `rev_000001/model.py:Lx-Ly`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 19 |
| read_count | 19 |
| read_scope | 3 origin parents + 16 forked_anchor variants across body_form / door / drawer_count / rack_topology / bottle_count / service_motion axes (sibling slugs `wine_cabinet1` / `wine_cabinet2` excluded) |
| source_index_policy | 仅索引下方采纳 module source |

被采纳样本（全部为 5★，全部实际读取 `model.py`）：

- **Parents (3)**
  - `rec_0611__wine_cabinet__001_png_62ac124185034747b205148f999aad00` — paired warm-cream display cabinets: `pair_anchor` + `short_carcass` + `tall_carcass`, glass doors (revolute) + drawers (prismatic), bottles/glasses as FIXED contents. **816 lines.**
  - `rec_0611__wine_cabinet__002_png_76f657b3604f4a32b3c4df94bc4955b5` — wide low matte-black sideboard: single `carcass`, two REVOLUTE PerforatedPanelGeometry mesh doors, horizontal bottle rows on shelves, X-shaped diagonal rack. **541 lines.**
  - `rec_0611__wine_cabinet__003_png_468ec605652c47d184dee65530a455a6` — built-in bar wall: long `base_carcass` + separate `upper_carcass` + `countertop` + `light_strip`, two smoked-glass cooler doors (revolute), 3×3 drawer bank (prismatic), 10 fixed bottle-row sub-parts, 4 fixed display glass sections in upper cubbies. **492 lines.**
- **Body form forks (3)** — `rec_0611_wine_cabinet_var_body_form_single_tall`, `rec_0611_wine_cabinet_var_body_form_arched_display`, `rec_0611_wine_cabinet_var_body_form_corner`
- **Door forks (3)** — `rec_0611_wine_cabinet_var_door_paired_glass`, `rec_0611_wine_cabinet_var_door_sliding_glass`, `rec_0611_wine_cabinet_var_door_mesh_bifold`
- **Drawer-count forks (3)** — `rec_0611_wine_cabinet_var_drawer_count_1`, `_3`, `_5`
- **Rack topology forks (3)** — `rec_0611_wine_cabinet_var_rack_topology_horizontal_cradles`, `_diamond_lattice`, `_vertical_pegs`
- **Bottle-count forks (2)** — `rec_0611_wine_cabinet_var_bottle_count_12`, `_24`
- **Service-motion forks (2)** — `rec_0611_wine_cabinet_var_service_motion_fold_out_counter`, `rec_0611_wine_cabinet_var_service_motion_pull_out_tasting_shelf`

结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| 单主体 + 一对 REVOLUTE 前门 | 12 | 玻璃或网格门，L-swing / R-swing 对称，铰链在垂直边 |
| 抽屉栈（PRISMATIC，+Y 出） | 10 | 1 / 3 / 5 个抽屉，一层或两层，柜身下部 |
| 底柜内嵌横躺瓶架 / 显示格 | 14 | 分成 horizontal_cradles / diamond_lattice / vertical_pegs 三种 rack module |
| 上下双柜体（bar-wall built-in） | 4 | base + countertop + upper cubby wall |

## 核心身份

**Wine cabinet** = 具备酒瓶储存功能的**落地或落墙柜体**，正面至少有一个可动
`REVOLUTE` 门（玻璃 / 网格 / 木质）**或**至少一个可动 `PRISMATIC` 抽屉，
柜内以水平躺瓶槽 / 菱格 / 立式插桩形式承载瓶身（可含站立 bottles / stemware
作为 fixed 内容物）。

- 不该混入 `plain_table`（无门无抽屉的裸台面）。
- 不该混入 `open_rack_without_cabinet_function`（只有金属线架、没有前面板 / 顶
  面 / 底板围合腔体的开放酒架）。
- 不该混入 `drawer_cabinet_with_sliding_drawers`（仅抽屉栈，无门 + 无瓶架）—
  wine_cabinet 必然带 rack topology **或** door。
- 不该混入 `refrigerator_with_hinged_doors`（家电压缩机/温控板；wine_cabinet
  内部是无制冷模块的木/金属柜腔）。

## 槽位 + 候选模块表

> Design choices vs source map: the source map already declares 6 slot axes
> (body_form / door / drawer_count / rack_topology / bottle_count / service_motion).
> We map these onto **6 in-code slots**, all source-backed. Because the source
> map's 3 primary_form variants (single_tall / arched_display / corner) map
> cleanly onto ③ Primary Form Family and are the axis carrying the most visible
> variation, `body_form` is the registered ③ slot per §8.5.

### Slot A：body_form (③ Primary Form Family — REGISTERED)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · `form_subtype` |
|---|---|---|---|---|---|
| `paired_display` | forked_anchor | `rec_0611__wine_cabinet__001_png_62ac124185034747b205148f999aad00` | L346-L652 | eligible if compatible | **Volumetric Envelope Form** — two side-by-side box carcasses (short + tall) sharing a hidden rear rail; box envelope; distinct shorter/taller silhouette |
| `wide_low_sideboard` | forked_anchor | `rec_0611__wine_cabinet__002_png_76f657b3604f4a32b3c4df94bc4955b5` | L218-L396 | eligible if compatible | **Volumetric Envelope Form** — single wide (≈1.5m) shallow box with legs, low console proportion |
| `single_tall` | forked_anchor | `rec_0611_wine_cabinet_var_body_form_single_tall/rev_000001` | L18-L136, L346-L661 | eligible if compatible | **Volumetric Envelope Form** — one tall narrow (≈0.5m×1.8m) carcass |
| `arched_display` | forked_anchor | `rec_0611_wine_cabinet_var_body_form_arched_display/rev_000001` | L118-L187, L291-L477 | eligible if compatible | **Planar Boundary Form** — front boundary is arched (top-front edge extruded arch), otherwise box-like carcass |
| `built_in_bar_wall` | forked_anchor | `rec_0611__wine_cabinet__003_png_468ec605652c47d184dee65530a455a6` | L36-L317 | eligible if compatible | **Macro Surface Construction** — long base + rear-anchored upper wall unit with cubby dividers; two-tier silhouette |
| `corner_wrap` | forked_anchor | `rec_0611_wine_cabinet_var_body_form_corner/rev_000001` | L18-L538 | eligible if compatible | **Planar Boundary Form** — L-shaped footprint (main wing + return wing) |

Six ③ candidates cover Planar Boundary (arched / corner), Volumetric Envelope
(paired / wide_low / single_tall), and Macro Surface Construction (built_in),
exceeding the ≥3 requirement.

### Slot B：door_style

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `paired_glass_hinged` | forked_anchor | `rec_0611__wine_cabinet__001_png_...` + `rec_0611_wine_cabinet_var_door_paired_glass` | 001 L139-L223, L429-L491 | eligible if compatible | 2 REVOLUTE hinged glass doors, stile+rail+glass_panel visuals, hinge on outer vertical edge, opens outward |
| `mesh_bifold` | forked_anchor | `rec_0611__wine_cabinet__002_png_...` + `rec_0611_wine_cabinet_var_door_mesh_bifold` | 002 L117-L215, L331-L352 | eligible if compatible | two mirrored two-leaf assemblies: each complete wire-mesh outer leaf hinges to the carcass and carries a separately REVOLUTE inner leaf on an offset captured knuckle |
| `smoked_glass_cooler` | forked_anchor | `rec_0611__wine_cabinet__003_png_...` | L155-L216 | eligible if compatible | 2 REVOLUTE smoked-glass doors, thin edge_black frame + hinge_barrel + vertical_handle |
| `sliding_glass` | forked_anchor | `rec_0611_wine_cabinet_var_door_sliding_glass/rev_000001` | L115-L212, L215-L401 | eligible if compatible | 2 PRISMATIC glass panels sliding along +X on a track (top+bottom rails) |
| `none` | forked_anchor | derived when body_form=`built_in_bar_wall` upper unit has open cubbies; degraded fallback | — | eligible only if rack_topology != `none` (must have at least one moving joint elsewhere) | 无门；upper open cubby style — 仅 built_in / wide_low 允许 |

### Slot C：drawer_count (M1 — joint-bearing multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `0` | forked_anchor | `rec_0611__wine_cabinet__002_png_...` | (no drawer joints) | eligible if compatible | 无抽屉；wide_low / arched / single_tall 使用 |
| `1` | forked_anchor | `rec_0611_wine_cabinet_var_drawer_count_1/rev_000001` | L226-L268, L346-L610 | eligible if compatible | 一个 PRISMATIC 抽屉；短柜下部 |
| `3` | forked_anchor | `rec_0611__wine_cabinet__001_png_...` + `rec_0611_wine_cabinet_var_drawer_count_3` | 001 L493-L563 | eligible if compatible | 3 个抽屉（短柜 1 + 高柜 2 或均分栈）|
| `5` | forked_anchor | `rec_0611_wine_cabinet_var_drawer_count_5/rev_000001` | L18-L78, L81-L420 | eligible if compatible | 5 个抽屉栈 |
| `9` | forked_anchor | `rec_0611__wine_cabinet__003_png_...` | L219-L262 | eligible if built_in_bar_wall | 3×3 drawer bank；仅在 built_in_bar_wall 下可用 |

抽屉栈朝 **−Y** 滑动（面向观察者），origin 位于柜前开口平面。

### Slot D：rack_topology

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `horizontal_cradles` | forked_anchor | `rec_0611__wine_cabinet__003_png_...` + `rec_0611_wine_cabinet_var_rack_topology_horizontal_cradles` | 003 L104-L153 | eligible if compatible | 水平躺瓶货架层，每层 5 瓶横躺（`_add_horizontal_bottle`）|
| `diamond_lattice` | forked_anchor | `rec_0611__wine_cabinet__002_png_...` + `rec_0611_wine_cabinet_var_rack_topology_diamond_lattice` | 002 L290-L301 | eligible if compatible | 交叉对角分隔条形成 X 形菱格；可扩展为 3×3 lattice mesh |
| `vertical_pegs` | forked_anchor | `rec_0611_wine_cabinet_var_rack_topology_vertical_pegs/rev_000001` | L18-L475 | eligible if compatible | 竖直圆柱插桩，每桩间距容纳一瓶颈 |
| `open_shelves` | forked_anchor | `rec_0611__wine_cabinet__001_png_...` + `rec_0611__wine_cabinet__002_png_...` | 001 L74-L88, 002 L268-L288 | eligible if compatible | 平置开放层板（用于站立 bottles / stemware），不构成 rack 但仍写入 rack slot 表示"无 rack"退化 |
| `none` | forked_anchor | fallback | — | eligible only if drawer_count > 0 | 无 rack；须有至少一个可动关节（door 或 drawer）保证类别身份 |

### Slot E：bottle_count (M2 — fixed multiplicity, ④/fixed contents)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bottles_0` | forked_anchor | fallback | — | eligible if rack_topology in {none, open_shelves} | 无瓶；纯柜体 |
| `bottles_12` | forked_anchor | `rec_0611_wine_cabinet_var_bottle_count_12/rev_000001` | L35-L77, L217-L390 | eligible if rack_topology != none | 12 瓶均匀填入 rack 或 shelf；`_add_horizontal_bottle` 或 `_add_standing_bottle` |
| `bottles_24` | forked_anchor | `rec_0611_wine_cabinet_var_bottle_count_24/rev_000001` | L35-L80, L220-L403 | eligible if rack_topology != none | 24 瓶两层充填 |
| `bottles_50` | forked_anchor | `rec_0611__wine_cabinet__003_png_...` extrapolation | 003 L109-L153 | eligible if built_in_bar_wall or wide_low | 10 rows × 5 = 50 瓶；仅在大柜体启用 |

瓶子和来源支持的 stemware/tumbler 是 carcass-hosted FIXED visuals
（`_add_horizontal_bottle` / `_add_standing_bottle` / `_build_glassware` 派生），
每个实体落在实际 shelf row 上；它们承载类别识别所需的 ④ 内容物。

### Slot F：service_motion (② additional joint type)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | most parents | — | eligible if compatible | 无额外 service motion |
| `fold_out_counter` | forked_anchor | `rec_0611_wine_cabinet_var_service_motion_fold_out_counter/rev_000001` | L139-L160, L526-L865 | eligible if compatible | 额外一个 REVOLUTE 板（fold-out serving counter），铰链在柜身前沿上部 |
| `pull_out_tasting_shelf` | forked_anchor | `rec_0611_wine_cabinet_var_service_motion_pull_out_tasting_shelf/rev_000001` | L18-L426 | eligible if compatible | 额外一个 PRISMATIC tasting shelf，从中层拉出 |

**Slot G：palette_style (⑥ 涂装)** — 见 §7；共 5 个 realistic colorway，全部来自 5★ 源。

## Form Dependency Contracts

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| paired / wide-low / single-tall | 001/rev_000001 `L18-L136`,`L346-L652`; 002/rev_000001 `L218-L396`; single-tall/rev_000001 `L346-L661` | resolved body family + width/depth/height/panel thickness | shell, opening, hinge lines, drawer guides, rack envelope, bottle grid, service mounts | every consumer is derived from the same resolved dimensions | opening containment, guide containment and swept-clearance checks | source-backed |
| arched_display | arched variant/rev_000001 `L118-L187`,`L291-L477` | one arch span/rise/front-boundary profile | crown, front trim, opening top, door height and optional tasting-service datum | crown/trim/opening share profile; tasting shelf, guides and rack fabric stop below the crown lower face | profile center/span/rise agreement plus door/service swept clearance | source-backed |
| built_in_bar_wall | 003/rev_000001 `L18-L102`,`L218-L389` | two-tier base/upper descriptor | base, countertop, upper cubbies, lower access, rack grid | upper and countertop derive from base envelope | tier alignment/support contact and lower swept clearance | source-backed |
| corner_wrap | corner variant/rev_000001 `L18-L538` | one L-footprint descriptor | main wing, return wing, access opening and rack envelope | both wings/opening derive from one footprint | connected footprint and access sweep outside both wings | source-backed |

No body form is a world-knowledge ③ extrapolation; all six accepted candidates are directly source-backed.

## 槽位图（slot graph）

pattern = `mixed`（parallel_children 主导 + multiplicity）

```
[root_carcass] (grounded)              ← body_form slot (single, paired, sideboard, arched, corner, built_in)
    |-- REVOLUTE (outer vertical edge) --> [door_L]    ← door_style slot (except none/sliding)
    |       `-- REVOLUTE --> [door_L_inner]               mesh_bifold only
    |-- REVOLUTE (outer vertical edge) --> [door_R]      or PRISMATIC when sliding_glass
    |       `-- REVOLUTE --> [door_R_inner]               mesh_bifold only
    |-- PRISMATIC (-Y, per index) --> [drawer_0 .. drawer_{N-1}]    ← drawer_count slot
    |-- FIXED shelves/rack fabric (as body visuals) at rack_topology slot
    |-- FIXED carcass-hosted bottle/glass visuals × resolved count    ← bottle_count/content slot
    |-- optional REVOLUTE --> [fold_out_counter]                     ← service_motion slot
    |   OR
    |-- optional PRISMATIC (-Y) --> [pull_out_tasting_shelf]
    +-- (for built_in_bar_wall) FIXED --> [upper_carcass] + FIXED --> [countertop] + FIXED --> [light_strip]
```

- Doors are parallel children of the root carcass (parent = carcass；multiple
  doors do NOT share downstream/upstream chain — each has its own mating
  contract to the outer vertical edge).
- Drawers are parallel children of the same carcass (PRISMATIC -Y, origin on
  front opening plane).
- Rack fabric (horizontal_cradles shelf boards, diamond X-bars, vertical pegs
  columns) are `carcass.visual(...)` — Rule 1: 不动就不是 part.
- Bottles, stemware and tumblers are static carcass-hosted visuals (body / neck /
  cork and supported cup profiles); `_add_horizontal_bottle`,
  `_add_standing_bottle` and `_build_glassware` mirror the accepted records.
- For `built_in_bar_wall`, base + countertop + upper are three FIXED-jointed
  parts (composed kinematic sub-assembly — separate reference frames matter for
  the two-tier silhouette).

## 每槽位 Module Emits / Interfaces

### Slot A / body_form modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass` (root); optional `upper_carcass` / `countertop` / `light_strip` when built_in_bar_wall | 001 L385, 002 L230, 003 L36 |
| internal visuals | side_walls / back_panel / base_plinth / top_trim / top_panel / shelves / dividers / bezels / hinge_mount tabs | 001 L37-L136, 002 L233-L329, 003 L37-L88 |
| internal joints | FIXED base→upper_carcass / base→countertop / upper→light_strip (built_in only) | 003 L96-L102, L311-L317, L381-L387 |
| upstream interface | (root) — grounded | — |
| downstream interface | outer vertical hinge edge (per door hand), front opening plane (per drawer band), inner shelf faces (for rack fabric) | 001 L444-L456, L502-L515 |

### Slot B / door modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | glass/smoked: `door_L`, `door_R`; mesh bifold: two outer plus two inner complete leaves — each mesh leaf emits perimeter stiles/rails and crossed wire field, with handles on the free inner leaves | 001 L139-L223, 002 L117-L215, 003 L155-L216 |
| internal visuals | glass frame/panel or open crossed-wire mesh frame, handle, outer hinge barrels; bifold additionally has offset inter-leaf pins/barrels and grounded end straps | as above |
| internal joints | none (each door part is self-contained) | — |
| upstream interface | door child origin = hinge line; panel extends inward from hinge; visuals authored so (0,0,0) lies inside AABB | 001 L444-L458 |
| joint policy | carcass ↔ outer door via REVOLUTE about signed Z; mesh inner leaf has a second outward-safe REVOLUTE signed Z range and is collision-tested independently and jointly. Sliding version: PRISMATIC along ±X, limits [0, door_width×0.85] | 001 L440-L491, 002 L201-L214, 003 L203-L216 |

### Slot C / drawer modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_i` for i in [0, N) | 001 L226-L268, 003 L218-L261 |
| internal visuals | drawer_front + drawer_bottom + drawer_side_{0,1} + drawer_handle + drawer_handle_mount_{0,1} | 001 L231-L268 |
| joint policy | carcass ↔ drawer_i via PRISMATIC axis=(0,-1,0), limits [0, drawer_travel]; origin on front opening plane at `(0, -depth/2, drawer_center_z[i])` | 001 L502-L563, 003 L248-L261 |

### Slot D / rack_topology fabric (visual, not part)

| emits | 描述 | 来源 |
|---|---|---|
| carcass visuals | horizontal_cradles: repeated shelf boards + optional metal cradle rods; diamond_lattice: crossed diagonal bars or 3×3 lattice mesh; vertical_pegs: array of thin cylinders; open_shelves: plain shelf boards | 001 L74-L104, 002 L268-L301, 003 L104-L153 (rack_shelf), plus var-record derivations |

Rack fabric is `carcass.visual(...)` (Rule 1). Each fabric is derived so it fits
`interior_width × interior_depth × rack_height` — parameterized to body_form
dimensions, not hard-coded.

### Slot E / bottle_count multiplicity

| emits | 描述 | 来源 |
|---|---|---|
| carcass visuals | `bottle_i_body/neck/cork` for i in [0, bottle_count), plus source-backed stemware/tumblers where the accepted body family contains them | 001 L272-L344, 002 L33-L114, 003 L109-L153 |
| internal visuals | bottle_body + bottle_neck + bottle_cork (+ optional bottle_label) | 001 L271-L313, 002 L33-L79 |
| joint policy | none: contents are static host visuals at `(bx, by, bz)` derived from a named real rack row | 001 L306-L312, 002 L23-L30, 003 L147-L153 |

### Slot F / service_motion

| emits | 描述 | 来源 |
|---|---|---|
| parts | `fold_out_counter` (single REVOLUTE panel) OR `pull_out_tasting_shelf` (single PRISMATIC shelf) | 001 fold-out var, 003 tasting var |
| joint policy | fold_out_counter: external captured REVOLUTE axis=(1,0,0), origin at front-top edge, q=0 upward-stowed, limits [0, π/2]; pull_out_tasting_shelf: captured bilateral PRISMATIC axis=(0,-1,0), limits [0, 0.25] | as above |

## Mechanism Structure / Swept-Clearance / Element Allowance

| mechanism | complete moving entity | grounded support / mating | shared dependency and closed/mid/max rule | exact allowance only |
|---|---|---|---|---|
| hinged doors | framed leaf, infill, handle, two short barrels | two coaxial parent pins connected to the side wall by rear bridges/outboard elbows; jamb is segmented around hardware pockets | external hinge axis and free-edge width derive from one opening profile; every leaf pair and service sibling is sampled together | each `hinge_barrel_z` ↔ matching `hinge_mount_i_z` |
| mesh bifold inter-leaf hinge | two complete framed crossed-wire leaves per side, inner-leaf handle, two short captured barrels | outer leaf carries offset pins plus end straps/elbows outside the barrel sweep | outer and inner joint ranges are valid independently; closed is coplanar, mid/max visibly fold without assuming a hidden mimic coupling | each `interleaf_pin_z` ↔ matching `interleaf_barrel_z` only |
| sliding doors | complete framed leaf with top/bottom rails | two real bypass tracks joined to the host; drawer-bearing bodies add a 45 mm track bay above the drawer bank | opening/rail/track/travel share one datum and stay engaged over full X travel | each named rail ↔ its matching named track |
| drawers | front, bottom, both sides, rear constraint, bilateral runners | longitudinal side guides, built-in bay dividers and required outer mounting clips | height is 72% of actual row pitch; complete boxes and adjacent doors are sampled closed/mid/max | matching indexed side guide ↔ runner only |
| fold-out counter | panel, ledge, barrel and two hangers | continuous top support, gussets and two capture brackets | q=0 stores upward above the door envelope; +X rotation opens forward and remains above/disjoint from door sweep | barrel ↔ each named bracket only |
| tasting shelf | tray, front edge and bilateral runners | host-mounted guides and bridges | top panel/arch crown defines service datum; rack fabric, bottles and glassware reserve the entire guide/shelf swept channel | matching tasting guide ↔ runner only |

Whole-part `allow_overlap` is prohibited. Static content has no collision waiver:
resolved bottle N must equal emitted bottle bodies, and accepted stemware/tumblers
remain upright on a named physical shelf selected below any service envelope.

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | 6 modules (see Slot A) | `wide_low_sideboard` | choice | procedural sampler | Slot A |
| `door_style` | enum | 5 modules | `smoked_glass_cooler` | choice | resolve_config gates by body_form | Slot B |
| `drawer_count` | int | {0, 1, 3, 5, 9} | 3 | choice | 9 only when body_form=built_in_bar_wall | Slot C |
| `rack_topology` | enum | 5 modules | `horizontal_cradles` | choice | not-none if door_style=none; else free | Slot D |
| `bottle_count` | int | {0, 12, 24, 50} | 12 | choice | 50 only when built_in_bar_wall or wide_low; 0 only when rack in {none, open_shelves} | Slot E |
| `service_motion` | enum | 3 modules | `none` | choice | fold_out_counter mut-excludes sliding_glass door | Slot F |
| `palette_style` | enum | 5 palettes | `warm_cream_maple` | choice | independent of structural slots | Slot G |
| `carcass_width` | float | [0.42, 1.80] m | 1.50 | independent | uniform sample then clamp by body_form family (paired: [0.90, 1.20], wide_low: [1.30, 1.80], single_tall: [0.42, 0.55], arched: [0.55, 0.80], built_in: [2.60, 3.30], corner: [1.40, 1.80]) | 001-003 dimensions |
| `carcass_depth` | float | [0.32, 0.60] m | 0.42 | independent | uniform sample; clamp `[0.32, 0.44]` for tall/paired; `[0.38, 0.60]` for wide/built_in | 001-003 |
| `carcass_height` | float | [0.75, 1.90] m | 0.86 | conditional | body_form determines usable band: paired -> [1.25, 1.90], wide_low -> [0.75, 0.95], single_tall -> [1.60, 1.90], arched -> [1.10, 1.55], built_in -> [0.82, 0.92] (upper adds 0.85-0.95), corner -> [0.82, 0.92] | 001-003 |
| `drawer_travel` | float | [0.14, 0.30] m | 0.22 | inequality | `drawer_travel ≤ carcass_depth × 0.72` | 001 L513, 003 L259 |
| `door_open_angle` | float | [1.20, 1.75] rad | 1.65 | independent | REVOLUTE upper limit | 001 L455, 002 L211 |
| `slide_axis_sign` | enum | {L, R, both} | both | choice | sliding_glass door subvariant | var record |
| (—) | inequality | — | — | inequality | `drawer_count ≤ 5` unless `body_form=built_in_bar_wall`; `bottle_count ≤ 24` unless body_form in {built_in_bar_wall, wide_low_sideboard} | joint budget + rack density |
| (—) | conditional | — | — | conditional | door_style eligibility per body_form (see resolve_config compatibility matrix below) | slot F gate |

**Compatibility matrix (enforced in `resolve_config` — degrades not raises unless
enum literal is invalid):**

| body_form | door_style choices | rack_topology choices | drawer_count max |
|---|---|---|---|
| `paired_display` | paired_glass_hinged, smoked_glass_cooler | open_shelves, horizontal_cradles, diamond_lattice | 0 (single-stack module excluded; paired source bays remain represented by the body anchor) |
| `wide_low_sideboard` | mesh_bifold, smoked_glass_cooler, paired_glass_hinged | diamond_lattice, horizontal_cradles, vertical_pegs, open_shelves | 3 |
| `single_tall` | paired_glass_hinged, smoked_glass_cooler, sliding_glass | horizontal_cradles, vertical_pegs, open_shelves | 3 |
| `arched_display` | paired_glass_hinged, smoked_glass_cooler | horizontal_cradles, open_shelves, diamond_lattice | 3 |
| `built_in_bar_wall` | smoked_glass_cooler, none | horizontal_cradles, diamond_lattice, vertical_pegs, open_shelves | 9 |
| `corner_wrap` | smoked_glass_cooler, paired_glass_hinged, none | horizontal_cradles, vertical_pegs, open_shelves | 5 |

Illegal combinations are silently downgraded (first legal choice) in
`resolve_config`, so `config_from_seed` may sample freely and gating is
one-way idempotent.

## Compatibility Gates

| id | action | when | reason / validator |
|---|---|---|---|
| `body_door_source_contract` | deny | `door_style` not in `_BODY_DOORS[body_form]` | no accepted hinge/track opening contract for that body; resolve to the first source-backed door |
| `paired_body_no_single_stack_drawer` | deny | `body_form=paired_display` and `drawer_count>0` | the accepted paired body has two independent bays; the current single-stack module would sweep through the center divider |
| `nine_drawers_built_in_only` | deny | `drawer_count=9` and body is not built-in | 3x3 bank requires accepted built-in face width and two internal bay dividers |
| `rack_body_contract` | deny | rack not in `_BODY_RACKS[body_form]` | rack must fit the resolved interior envelope and remain supported |
| `bottle_capacity` | deny | requested bottle count exceeds resolved, service-safe row × column rack capacity | reported N must equal emitted supported visuals; pull-out service reserves its swept channel and a source-backed glassware row before N is solved; 50 remains reachable on large horizontal racks |
| `foldout_vs_sliding_track` | deny | fold-out counter with sliding glass | service hinge and bypass-track envelope compete; other hinged-door combinations use an upward-stowed leaf at the external front-top hinge so independent sweeps remain disjoint |
| `tasting_headroom` | deny | tasting shelf on wide-low or built-in body | accepted rack rows leave no dedicated vertical service bay |

All enabled combinations must pass InterfaceSpec/MatingContract geometry, category identity, closed/mid/max sampled collision and exact-element allowance audit. An unchecked Cartesian product is not exposed.

## Combination Domain

- diversity_profile: `compositional`; floor `120`, target `120`, exception: none.
- core axes: `body_form(6) × door_style(5) × rack_topology(5) × service_motion(3)`; raw core `450`; exact stable compatibility-gated legal core `125` (pass).
- raw domain adds discrete multiplicities `drawer_count={0,1,3,5,9}` and `bottle_count={0,12,24,50}`; raw theoretical `9000`; exact compatibility/capacity-gated legal raw `640` after one-pass idempotent projection.
- drawer admitted/reachable: all `{0,1,3,5,9}`; boundary coverage `0/3/9` plus accepted anchors `1/5`.
- bottle admitted/reachable: all `{0,12,24,50}`; boundary coverage `0/24/50` plus accepted anchor `12`.
- palette, material, ④ decoration and continuous dimensions are excluded from core/raw structural counting.

## Visual Risk

- `drawer`: every moving drawer is a complete containment box with bilateral longitudinal guides; inspect closed/mid/max engagement and adjacent-stack clearance.
- `hidden_slide`: sliding glass and tasting-shelf runners must remain visibly captured at maximum travel.
- `multi_joint`: two doors plus up to nine drawers and a service mechanism require combined-pose collision sampling.
- category-specific `rack_content_clearance`: bottle neck/cork visuals must remain behind the front access sweep and exactly match the resolved bottle multiplicity.

### 7.5 编译预算 / compile budget

**Target: ≤18 s / seed** (库内实测 cabinet-like modular templates 5-16 s; wine_cabinet
uses only Box / Cylinder / Sphere for the vast majority of visuals — no
LatheGeometry, one optional PerforatedPanelGeometry for `mesh_bifold` doors
(库内实测 ~2 s), no cadquery, no重 boolean).

- 小半径特征 tessellation ≤32 段 (bottle_body radius=0.028 每根 12 段即可辨识)。
- 主体英雄面 ≤64 段 (side_walls, doors, drawers 全是 Box 无需 tessellation)。
- N 个相同 bottle 全部复用 `_add_horizontal_bottle` / `_add_standing_bottle`
  helper（共享 primitive）；bottle_count=50 时不额外造 mesh。
- Perforated mesh 门只在 door_style=`mesh_bifold` 才生成；single-mesh geometry
  cached per (width, height, pitch) tuple。

If sweep flags `compile_timeout`, first降 bottle sphere→cylinder for shoulder,
then降 mesh hole density (pitch 0.017→0.022), then限 built_in_bar_wall bottle_count
上限到 24.

## Multiplicity / Copy Logic

Two independent multiplicity axes (§8 discipline):

- **M1 `drawer_count`** — **joint-bearing** (每 drawer 一个 PRISMATIC 关节)。
  - `count_param`: `drawer_count`
  - `observed_N`: {0, 1, 3, 5, 9}; `derived_N_range`: discrete admitted set {0, 1, 3, 5, 9}; no unobserved integer interpolation/extrapolation; built_in_bar_wall 才允许 9
  - sampling domain: uniform choice within the eligible subset
  - copied object / naming: `drawer_i`, `carcass_to_drawer_i`; identical
    geometry per drawer; stacked vertically with `drawer_pitch = usable_h /
    drawer_count`
  - placement: `drawer_center_z[i] = plinth_h + panel_t + drawer_pitch * (i + 0.5)`
    for i in [0, drawer_count); built_in_bar_wall uses 3×3 grid centers
  - joint policy: PRISMATIC axis=(0,-1,0); origin on carcass front opening plane
    at `(0, -depth/2, drawer_center_z[i])`; upper=drawer_travel
  - accepted source evidence: `rec_0611_wine_cabinet_var_drawer_count_5/rev_000001`, `model.py:L18-L78`,`L81-L420`; `rec_0611__wine_cabinet__003_png_468ec605652c47d184dee65530a455a6/rev_000001`, `model.py:L218-L262`
  - capacity/guide gate: pitch exceeds full-box height + 8 mm; every box has front/bottom/two sides/rear plus bilateral longitudinal guides; validation_counts={0,1,3,5,9}
- **M2 `bottle_count`** — **fixed visual multiplicity**（carcass-hosted，
  不增加 part tree 或运动学）。
  - `count_param`: `bottle_count`
  - `observed_N`: {0, 12, 24, 50}; `derived_N_range`: discrete admitted set {0, 12, 24, 50}; no unobserved integer interpolation/extrapolation; 50 仅 built_in_bar_wall / wide_low horizontal rack
  - sampling domain: uniform choice within the eligible subset
  - copied object / naming: `bottle_i_body/neck/cork`; per-bottle
    material cycles through 3-4 wine colorways (green/burgundy/amber/brown)
  - placement: `bottle_layout(rack_topology, carcass_dims, bottle_count)`
    computes 12/24/50 slots (rows × cols), preserves source orientation and
    removes every row consumed by glassware or a service swept envelope
  - joint policy: none; bottles do not move and are host `carcass.visual(...)` elements under Rule 1
  - accepted source evidence: `rec_0611_wine_cabinet_var_bottle_count_12/rev_000001`, `model.py:L35-L77`,`L217-L390`; `rec_0611_wine_cabinet_var_bottle_count_24/rev_000001`, `model.py:L35-L80`,`L220-L403`; 003/rev_000001 `model.py:L104-L153`
  - capacity gate: emitted count must exactly equal the resolved row×column cells; validation_counts={0,12,24,50}

### 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | door 门数 {2}, drawer 数 {0,1,3,5,9}, service_motion 是否加 1 个 REVOLUTE/PRISMATIC 子件, upper_carcass 是否存在（built_in only）→ 4 组结构变化；全部 forked_anchor（001/002/003 + 变体）|
| └ multiplicity | 同构件 ×N | **有** | 见 §8 — 两根：drawer_count {0,1,3,5,9} + bottle_count {0,12,24,50}；forked_anchor |
| ② 关节类型 | 图不变，某条边换 type/轴 | **有** | REVOLUTE (hinged doors, fold_out_counter, ±z axis), PRISMATIC (drawers -y, sliding_glass door ±x, tasting_shelf -y), FIXED (bottles, decorative sub-assemblies, built_in upper). Sliding_glass door 和 mesh_bifold 反映 door slot 上的 ② 变化；forked_anchor from `_var_door_sliding_glass` |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色） | **有** | Slot A `body_form` (登记进 `slot_choices`)：6 candidates — Planar Boundary Form (arched_display, corner_wrap), Volumetric Envelope Form (paired_display, wide_low_sideboard, single_tall), Macro Surface Construction (built_in_bar_wall)；每个 candidate `form_subtype` 已标于 Slot A 表；全部 forked_anchor |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | Bottle labels + cork variants (via bottle materials cycling), display_trim bezels around glass openings, LED light_strip visuals (warm_led material, present when body_form={paired_display, built_in_bar_wall} due to source support), hinge_mount tabs (edge_black), handle standoffs. 装饰几何均写为宿主 carcass / door visual，随 ③⑤ 共形（e.g. display_trim 长度 = `opening_top - display_bottom` 从 body 尺度派生）；source_type: record_only + host-conformal world_knowledge_extrapolation |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | **有** | 尺寸范围见 §7 `carcass_width/depth/height` 表；关节包络：door REVOLUTE [0, 1.20-1.75] rad open_direction=+外向y-；drawer PRISMATIC [0, 0.14-0.30] axis=-y；sliding_glass PRISMATIC [0, door_width×0.85] axis=+x；fold_out_counter REVOLUTE [0, π/2] axis=+x hinged front-top edge；tasting_shelf PRISMATIC [0, 0.25] axis=-y. **motion_test_plan:** run `ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` + targeted `ctx.pose(...)` for (a) both doors at open_angle (handles cleared front, glass panel outside carcass front face), (b) each drawer at drawer_travel (drawer_front y-position < carcass front face y - 0.15), (c) sliding_glass door at travel (panel center passes carcass midline), (d) service_motion at its extended pose. No sampled-pose exemption needed. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 5 palettes (see §7 / template PALETTES): `warm_cream_maple` (001 anchor: cream+maple+brass+warm_led), `matte_black_stainless` (002 anchor: matte_black+dark_metal+shelf_dark+smoked_glass), `built_in_dark` (003 anchor: matte_black+black_stone+edge_black+warm_led), `light_oak` (world-extrapolation from 001 palette family: oak+brass+glass), `walnut_bronze` (world-extrapolation from 003 family: warm_walnut+bronze_metal+smoked_glass). 材质大类覆盖 painted / metal / glass / wood → 4 类 ≥ ceil(0.5×5)=3. |

## 采样与覆盖审计

总组合数（degrade 前的裸乘积）：6 × 5 × 5 × 5 × 4 × 3 × 5 = **11 250**（body × door × drawer × rack × bottle × service × palette）。

Compatibility matrix 将非法组合稳定投影到 first-legal；机器审计的精确结构域为
core `125`、含 multiplicity raw `640`，不以材质或连续尺寸充数。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：
- `config_from_seed(seed)` 使用 `random.Random(seed)` 独立采样 7 个离散 slot
  + 4 个连续 scale；然后 `resolve_config` 按上面 compatibility matrix 静默降级
  非法组合。seed=0 不特殊。
- Sweep 范围：`0-35` fast/final + auto corner；正式完成要求所有机械 blocker
  为零，不能用 `pass_rate ≥ 0.90` 掩盖真实失败。
- Random sweep 覆盖检查：`axis_realization` 应报出全部 6 个 body_form
  candidate + 全部 4 个 door_style（可达） + 全部 drawer_count 档 + 全部 rack
  topology + 全部 bottle_count 档 + 3 service_motion + 5 palette。
- Regression overrides: none at initial version.
- Controlled local parameterization：`carcass_width`, `carcass_depth`,
  `carcass_height`, `drawer_travel`, `door_open_angle` — all clamped in
  `resolve_config`; violate inequality → 按比例回缩（no reject-and-resample
  because ranges have generous clearance）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent Random draws per slot, then compatibility gating in `resolve_config` | slot_choices_for_seed matches build choices |
| compatibility matrix | body_form determines eligible {door_style, drawer_count max, rack_topology}; door=none requires rack != none; bottle_count 50 requires built_in / wide_low | no floating rack; no illegal door for narrow body; drawer count fits carcass height |
| controlled local variation | 4 scale params (width/depth/height/travel) clamped and derived | proportions vary without breaking hinge origin proximity, drawer travel |
| regression overrides | none | — |
| random sweep | 0-35 for initial pass; corner appended | slot_choices coverage; no closed-pose overlap; door swings outward; drawer slides toward user |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 6 | yes | yes | ③ registered, all form_subtypes covered |
| B door_style | 5 | yes | yes | includes sliding PRISMATIC alt |
| C drawer_count | 5 | yes | yes | joint-bearing multiplicity |
| D rack_topology | 5 | yes | yes | 4 real topologies + open_shelves |
| E bottle_count | 4 | yes | yes | fixed-mult |
| F service_motion | 3 | yes | yes | none + 2 real motions |
| G palette_style | 5 | yes | yes | 3 source-backed + 2 world-extrap |

## Validator

- `slot_choices_for_seed` returns implemented module names (all 7 slots)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds; seed=0 is NOT special
- compatibility matrix in `resolve_config` prevents illegal combinations by silent degrade
- controlled scale params are clamped and cannot break hinge origin proximity, drawer travel, closed-pose clearance
- cross-part scale dependencies (`drawer_travel ≤ depth × 0.72`) resolved in `resolve_config`
- captured interfaces are element-scoped only: external coaxial door pin↔barrel, bifold inter-leaf pin↔barrel,
  bilateral drawer guide↔runner, sliding rail↔track, counter bracket↔barrel and
  tasting guide↔runner; no whole-part allowance exists
- key joints have expected type / axis / range:
  - doors: REVOLUTE (0,0,±1), limits [0, 1.20-1.75]; sliding_glass: PRISMATIC (±1,0,0)
  - drawers: PRISMATIC (0,-1,0), limits [0, drawer_travel]
  - service fold_out: REVOLUTE (1,0,0), limits [0, π/2]; tasting_shelf: PRISMATIC (0,-1,0)
- copied bottle visuals / drawer parts follow `bottle_i_*` / `drawer_i` naming + regular placement helper
- `ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` in `run_wine_cabinet_tests` — Rule 5 mandatory
- `ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)`

## Reject cases

- 抽屉滑动轴非 −Y（面板朝错方向）
- 门铰链原点不在柜身外侧竖边几何上（>15mm）
- 关闭或任一 sampled pose 中 door 与 carcass/抽屉/service 出现非 intentional overlap
- rack 或 bottle 悬空（bottle body 未接触 shelf 或 cradle）
- 门开到 upper 极限时 handle / glass panel 与相邻门或柜身穿模（e.g. 两扇内开门相撞）
- fold_out_counter 未在 q=0 向上收纳，或翻到 π/2 时进入门/柜体扫掠包络
- `built_in_bar_wall` 的 upper_carcass 未落到 countertop 上（导致 isolated part）
- multiplicity 数量与 part / joint 数不匹配
- palette_style 选中但某个 visual 未使用 `material=mats[...]`（monochrome fallback）

## 与相邻类别的边界

- `drawer_cabinet_with_sliding_drawers`：仅抽屉栈；无 rack、无 door 是它，wine_cabinet 至少要有一个 rack 或至少一个 door
- `refrigerator_with_hinged_doors`：家电，含压缩机/温控/大插件；wine_cabinet 内部只是柜腔 + rack
- `display_freezer_with_sliding_glass_lids`：卧式玻璃冷冻柜；wine_cabinet 是立式，主门 REVOLUTE 而非水平滑盖
- `shelving_unit_with_adjustable_shelves`：无 door 无 drawer 的开放架
- `dishwasher_with_dropdown_door_and_sliding_racks`：dropdown 门 + 铁丝篮，不是酒瓶架

## 模板实现备注

- 参考 `agent/templates/drawer_cabinet_with_sliding_drawers.py`（body + N drawer + optional lid 模式）和
  `agent/templates/dishwasher_with_dropdown_door_and_sliding_racks.py`（enum-slot + compatibility gating + palette）
  两个 flat-modular 模板；不使用 `_modular.py` SlotSpec assembler（我们的 slot graph 是 parallel-children + multiplicity，
  用 enum + resolve_config 直接实例化即可，dishwasher 走的是同一条路）。
- 6 body_form 用 `if body_form == ...:` 分支在 `_build_carcass` 里生成对应 side_walls / back / top / plinth 布局；
  built_in_bar_wall 额外造 FIXED upper_carcass + countertop + light_strip。
- door 门是 parallel children（不使用 assembler chain），每扇门直接以 carcass 为 parent 造 REVOLUTE 或 PRISMATIC joint；
  hinge_barrel ↔ carcass hinge_mount tab 用 element-scoped `allow_overlap`（parent 001 pattern）。
- rack 织物写成 carcass.visual(...)（Rule 1 硬约束）；每种 topology 一个 helper：
  `_add_horizontal_cradle_row`, `_add_diamond_lattice_grid`, `_add_vertical_pegs_array`, `_add_open_shelves`.
- bottle / stemware helper 严格复刻源码：`_add_horizontal_bottle` 用 rpy=(π/2,0,0) Cylinder，`_add_standing_bottle` 竖直 Cylinder；
  `bottle_body` / `bottle_neck` / `bottle_cork` 名字保留（validator 依赖）。
- palette 通过 `mats = {name: model.material(f"wine_{name}_{palette_style}", rgba=...) for ...}` 集中生成；
  所有 `part.visual(..., material=mats[key])` 从 dict 取；禁止裸 RGBA。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / D / F | paired_display / open_shelves / (glass door hinge pattern) | `rec_0611__wine_cabinet__001_png_62ac124185034747b205148f999aad00` | L18-L136 (_add_carcass), L139-L223 (_add_glass_door), L226-L268 (_add_drawer), L271-L344 (_add_bottle / _add_glass) | body + doors + drawers + bottles |
| S2 | A / B / D | wide_low_sideboard / mesh_bifold / diamond_lattice | `rec_0611__wine_cabinet__002_png_76f657b3604f4a32b3c4df94bc4955b5` | L23-L114 (_fixed/_add_bottle/glass), L117-L215 (_add_mesh_door), L218-L396 (build_object_model carcass + diagonal rack) | mesh doors + diagonal rack |
| S3 | A / D / C | built_in_bar_wall / horizontal_cradles / 9 drawer bank | `rec_0611__wine_cabinet__003_png_468ec605652c47d184dee65530a455a6` | L18-L102 (base_carcass), L104-L153 (bottle_row helper), L155-L216 (cooler_door), L218-L261 (drawer bank), L264-L317 (upper_carcass FIXED) | 两层柜 + 大 rack + 抽屉栈 + smoked glass |
| V1 | A | single_tall | `rec_0611_wine_cabinet_var_body_form_single_tall/rev_000001` | L18-L136, L346-L661 | tall narrow envelope form |
| V2 | A | arched_display | `rec_0611_wine_cabinet_var_body_form_arched_display/rev_000001` | L118-L187, L291-L477 | planar boundary arch |
| V3 | A | corner_wrap | `rec_0611_wine_cabinet_var_body_form_corner/rev_000001` | L18-L538 | L-shaped planar boundary |
| V4 | B | paired_glass_hinged | `rec_0611_wine_cabinet_var_door_paired_glass/rev_000001` | L139-L251, L374-L680 | glass door reference |
| V5 | B | sliding_glass | `rec_0611_wine_cabinet_var_door_sliding_glass/rev_000001` | L115-L212, L215-L401 | PRISMATIC glass slider |
| V6 | B | mesh_bifold | `rec_0611_wine_cabinet_var_door_mesh_bifold/rev_000001` | L118-L307, L310-L490 | mesh door reference |
| V7 | C | drawer_count_1 | `rec_0611_wine_cabinet_var_drawer_count_1/rev_000001` | L226-L268, L346-L610 | single drawer variant |
| V8 | C | drawer_count_3 | `rec_0611_wine_cabinet_var_drawer_count_3/rev_000001` | L18-L389 | 3 drawer variant |
| V9 | C | drawer_count_5 | `rec_0611_wine_cabinet_var_drawer_count_5/rev_000001` | L18-L78, L81-L420 | 5 drawer variant |
| V10 | D | horizontal_cradles | `rec_0611_wine_cabinet_var_rack_topology_horizontal_cradles/rev_000001` | L18-L424 | cradle shelf per row |
| V11 | D | diamond_lattice | `rec_0611_wine_cabinet_var_rack_topology_diamond_lattice/rev_000001` | L21-L54, L57-L444 | 3×3 diamond lattice mesh (BoxGeometry merge) |
| V12 | D | vertical_pegs | `rec_0611_wine_cabinet_var_rack_topology_vertical_pegs/rev_000001` | L18-L475 | peg column array |
| V13 | E | bottle_count_12 | `rec_0611_wine_cabinet_var_bottle_count_12/rev_000001` | L35-L77, L217-L390 | 12-bottle fill |
| V14 | E | bottle_count_24 | `rec_0611_wine_cabinet_var_bottle_count_24/rev_000001` | L35-L80, L220-L403 | 24-bottle fill |
| V15 | F | fold_out_counter | `rec_0611_wine_cabinet_var_service_motion_fold_out_counter/rev_000001` | L139-L160, L526-L865 | REVOLUTE serving counter |
| V16 | F | pull_out_tasting_shelf | `rec_0611_wine_cabinet_var_service_motion_pull_out_tasting_shelf/rev_000001` | L18-L426 | PRISMATIC tasting shelf |

## 审核记录
| 项 | 结论 |
|---|---|
| authoring_status | implementation_ready |
| self-check notes | Source/category contracts complete. Systemic repairs: captured external coaxial door hinges with segmented jamb pockets; real two-leaf mesh bifolds with separately articulated inner leaves; bilateral complete drawer boxes and pitch-derived heights; drawer-aware sliding track bay; upward-stowed, grounded fold-out counter; host-mounted tasting runners; and one shared service/crown/rack/content clearance datum. Exact combo audit remains core `125`, raw `640`. Current written sweep report passes fast `16/16`, final `36/36`, corner `48/48`, with zero failure triage and zero whole-part allowance. Formal seed export remains blocked until schema v3 final render evidence and hash-bound human approval are current. |
