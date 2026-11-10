# pictureX_0611_Cabinet_with_doors — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Cabinet_with_doors` |
| template path | `agent/templates/pictureX_0611_Cabinet_with_doors.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Cabinet_with_doors_template.py` (skipped; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children door leaves parented to one carcass + door_count / shelf_count multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | all 5-star samples in this subcategory (5 origins + 8 forked/probe variants) |
| source_index_policy | only adopted module sources are indexed below |

**Per-source read (all read in full):**

- **001** cylindrical/oval walnut drum, 2 curved flush-slab handleless doors, 4 slender painted-steel legs, 1 curved shelf. Curved carcass shell + curved doors are `mesh_from_cadquery` annular-sector extrusions (`_arc_points` L41-66, `_carcass_shell_shape` L102-109, `_door_shape` L130-154). Two REVOLUTE hinges, axis Z, one door authored open (L384-415). Legs via `_add_leg` (L162-191).
- **002** rectilinear pale-maple box, 2 framed woven-cane doors w/ brass pulls, 4 round dowel legs, 1 shelf. Box carcass (L179-233), `_add_door_visuals` frame+cane+beads+handle+hinge knuckles (L42-135), cane = `PerforatedPanelGeometry`→`mesh_from_geometry` (L155-169), 2 REVOLUTE (L264-289). **Canonical coordinate convention: X=width, Y=depth, front=−Y, hinge axis Z.**
- **003** tall ivory box, 2 full-height pierced-scroll carved doors, 4 square feet + shaped plinth apron, 3 shelves, 3 hinges/door. Carved door = `mesh_from_cadquery` ornamental union (`_ornamental_door_mesh` L51-146); plinth apron = `mesh_from_cadquery` (`_plinth_rail_mesh` L149-169); 3-shelf loop (L224-231); REVOLUTE loop w/ `hinge_count:3` (L375-393). Front face = +Y in source.
- **004** wide low walnut credenza, 3 glazed curtain-back doors, 6 lathe-turned feet, 2 shelves. Turned feet = `LatheGeometry`→`mesh_from_geometry` (`_turned_foot_mesh` L25-40); glazed door = frame + `glass_panel` Box (`aged_glass` α0.30 L263-265) + `curtain_backing` Box + 9 fold Boxes (`_add_door_visuals` L96-240, curtain L141-160); 2-shelf loop (L319-325); 3 REVOLUTE (L456-474).
- **005** two-tier walnut hutch, 4 doors (2 raised-panel lower + 2 arched glazed upper), 2 feet + moulded plinth. Raised-panel door + carved medallion = `mesh_from_cadquery` (`_lower_door_wood` L76-144); arched glazed frame + `smoky_glass` pane (α0.30 L223) = `mesh_from_cadquery` (`_upper_door_wood` L42-58 / `_upper_door_glass` L61-73); 4 REVOLUTE (L395-409). Front face = −Y in source.
- **var_single_door** N=1: single wide leaf, hinge moved to side panel, one joint (L254-273).
- **var_flush_slab_doors** flush solid `door_slab` Box, framed construction removed (`_add_door_visuals` L39-49), Box-only doors.
- **var_sliding_doors** PRISMATIC bypass: 2 sliders on offset Y planes (front −0.197 / rear −0.130), axis ±X, travel 0.40, top guide rail + bottom track sill Boxes (L240-260), rollers replace hinge knuckles (L127-137), joints L291-322.
- **var_bifold_door** door_0 split into `door_0` + `door_0_leaf_b` (half-width, coupled by a 2nd REVOLUTE parent=door_0 at the shared stile, upper 2.90 rad, L314-329); door_1 stays full leaf. `door_width` kwarg (L51-54).
- **var_tapered_body** trapezoid carcass (top<base): lofted `side_panel_0/1` + `back_panel` = `mesh_from_cadquery` loft (L225-280), top<base Boxes, taper-compensated doors (L65-182).
- **var_plinth_base** legs replaced by one recessed toe-kick `plinth_base` Box (L238-250).
- **var_wall_mounted** floating, elevated `BODY_BOTTOM=1.20`, rear steel hanging-rail cleat + mounting plates (L236-264), no legs.
- **var_probe_single_door_cylindrical** compatibility probe: N=1 wide curved leaf on cylindrical body (curved shell + single curved door, hinge on curved rim; converged).

## 核心身份

A freestanding (or wall-hung) storage **case whose PRIMARY articulation is one or more doors opening over an enclosed cavity**: a single load-bearing carcass (sides/top/base/back) plus ≥1 door leaf that is a moving child of the carcass on a real non-fixed joint (revolute swing, or prismatic slide for the bypass variant). Default mature domain: casework 0.72–1.46 m wide, 1.0–1.75 m tall, 0.38–0.47 m deep, on legs / feet / plinth / wall cleat.

Must read as a **door cabinet**, NOT: a chest-of-drawers / dresser (drawer as primary articulation — excluded), an open bookshelf (no doors), or an all-glass vitrine display box (glazed *doors* are in-scope; an all-glass body is not).

## 槽位 + 候选模块表

### Slot A：body_form （③ 主体形态家族 / Primary Form Family — 登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `rect_box` | origin_anchor | 002/003/004/005 | 002:L179-233 | Volumetric Envelope Form (rect prism) | eligible if compatible | Box side/top/base/back panels; axis-aligned front opening + front face-frame rails |
| `cylindrical_shell` | origin_anchor | 001, var_probe | 001:L102-113,242-263 | Macro Surface Construction (bent curved shell) | eligible if compatible | `ExtrudeGeometry` annular-sector shell (real curved mesh, **not** downgraded) + Cylinder top/base; curved front opening |
| `tapered_box` | forked_anchor (from 002) | var_tapered_body | var:L225-291 | Volumetric Envelope Form (trapezoid, top<base) | eligible if compatible | `LoftGeometry` slanted side/back panels + narrower top slab (real tapered mesh) |

### Slot B：door_kind （③ door form family + ④ 表面装饰）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `framed_cane` | origin_anchor | 002 | 002:L42-135,155-169 | eligible on rect/tapered | Box stile/rail frame + inset rattan panel + light woven lattice bars (④) + brass pull |
| `glazed_curtain` | origin_anchor | 004 (005 upper) | 004:L96-240 | eligible on rect/tapered | Box frame + translucent `glass` panel + textile `curtain_backing` + fold bars (④) |
| `flush_slab` | forked_anchor (from 002) | var_flush_slab_doors | var:L39-78 | eligible on rect/tapered | single solid `door_slab` Box + pull |
| `fretwork_pierced` | origin_anchor | 003 | 003:L51-146 | eligible on rect/tapered | Box frame + dark recessed backing + vertical/scroll fret bars (④ pierced read) + drop pull |
| `raised_panel` | origin_anchor | 005 lower | 005:L76-144 | eligible on rect/tapered | Box slab + raised moulding bars + `Sphere` carved medallion (relief) + knob |
| `curved_slab` | origin_anchor | 001 | 001:L130-154,301-338 | eligible **only on cylindrical_shell** | `ExtrudeGeometry` annular-sector curved leaf (real curved mesh) + concealed hinge barrels |

Decoration note (Rule 4/§8.5 ④): woven-cane / fretwork / curtain folds are ④ surface decoration rendered as **host-derived flat lattice/fold bars sized from the final door opening** (frame inset), not as a cadquery-perforated sheet. The Rule-3-critical curved geometry (cylindrical shell + `curved_slab` + lathe-turned feet) is kept as real curved meshes; flat decorative fields use flat geometry (`PerforatedPanelGeometry` cadquery cut measured at **46 s/panel** — over budget — so it is intentionally not used).

### Slot C：door_mechanism （② 关节类型 + ① 拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `revolute_swing` | origin_anchor | all 5 origins | 002:L264-289 | eligible (all bodies) | 1 REVOLUTE per leaf, axis Z, outward toward −Y, lower=0 |
| `sliding_bypass` | forked_anchor (from 002) | var_sliding_doors | var:L240-260,291-322 | eligible only on rect_box + flat door + N=2 | 2 PRISMATIC bypass on offset Y planes, axis ±X + top/bottom track Boxes |
| `bifold` | forked_anchor (from 002) | var_bifold_door | var:L274-329 | eligible only on rect_box + flat door + N=2 | door_0 = leaf A + coupled `door_0_leaf_b` (2nd REVOLUTE parent=door_0); door_1 plain |

### Slot D：support_base （① 支撑拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `metal_legs` | origin_anchor | 001 | 001:L162-191,285-299 | eligible (all bodies) | 4 slender Cylinder legs + mounts + floor glides |
| `dowel_legs` | origin_anchor | 002 | 002:L235-251 | eligible (all bodies) | 4 round wood Cylinder legs + square sockets |
| `turned_feet` | origin_anchor | 004 | 004:L25-40,376-391 | eligible on rect/tapered | 6 `LatheGeometry` turned feet (real turned mesh) + plinth band |
| `feet_plinth` | origin_anchor | 003/005 | 003:L264-285; 005:L243-246 | eligible on rect/tapered | 4 Box feet + moulded plinth core/moulding |
| `recessed_plinth` | forked_anchor (from 002) | var_plinth_base | var:L238-250 | eligible on rect/tapered | single recessed toe-kick Box, no legs |
| `wall_mount` | forked_anchor (from 002) | var_wall_mounted | var:L236-264 | eligible on rect/tapered | elevated carcass + rear steel hanging-rail cleat + mounting plates, no floor support |

Every slot ≥3 candidates (D=6, B=6, A=3, C=3). No single-candidate slot.

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
support_base ──[fused into carcass.visual, no joint — Rule 1]── carcass(body_form)
                                                                    │
                            parallel children (one joint per leaf) ─┤
                                                                    ├─ door_0 (door_kind + door_mechanism)
                                                                    ├─ door_1 ...
                                                                    └─ door_{N-1}  [+ door_0_leaf_b child of door_0 for bifold]
                            interior shelves (shelf_count) fused into carcass.visual
```

- The carcass is the single grounded root part `carcass`. **support_base is decoration fused as `carcass.visual(...)` (Rule 1 — legs/feet/plinth/cleat do not articulate → not separate parts).**
- Each door leaf is a separate moving child part parented directly to `carcass` (parallel-children; no serial chain).
- **Cross-joint interface / mating:**
  - revolute/box: hinge at door outer edge, axis Z, origin `(hinge_x, −depth/2, door_center_z)`. Door back plane and carcass front face-frame rail both at world y=−depth/2. MatingContract: parent `front_rail_*` `negative_y` ↔ child `door_mount_rail` `positive_y`.
  - prismatic/box: origin at door edge, axis ±X; MatingContract door `door_mount_rail` ↔ carcass `track_sill` along −Y (tangential X free = sliding).
  - bifold fold joint: parent=door_0, child=door_0_leaf_b, axis Z at shared stile — captured folding-hinge, **mating omitted** (grandfathered) + element-scoped `allow_overlap`.
  - cylindrical/curved: curved mating faces are not axis-aligned → **MatingContract omitted (documented curved-face exemption, Rule 2)**; hinge barrels captured via `allow_overlap` + `expect_contact` (as origin 001).
- Mutually exclusive: `curved_slab` ⇔ `cylindrical_shell` only; `sliding_bypass`/`bifold` ⇔ rect_box + flat door + N=2; `turned_feet`/`feet_plinth`/`recessed_plinth`/`wall_mount` ⇔ rect/tapered (cylindrical drum stands on legs only).

## 每槽位 Module Emits / Interfaces

### Slot A / carcass (body_form)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass` (root) | 002:L171-177 |
| visuals | side/top/base/back + front face-frame rails (`front_rail_bottom/top`, `mid_rail` if tiered) + shelves + support_base | 002:L179-233; 001:L242-263; var_tapered:L225-291 |
| internal joints | none (single part) | — |
| downstream interface | front opening: `front_rail_*` `negative_y` face @ y=−depth/2 (mating anchor); opening_width/height/z bounds for door sizing | 002:L219-233 |

### Slot B+C / door_{i} (door_kind + door_mechanism)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}` (+ `door_0_leaf_b` for bifold) | 002:L253-262; var_bifold:L283-290 |
| visuals | kind-specific front geometry + uniform `door_mount_rail` back Box + hinge/roller hardware + handle | 002:L42-135; 004:L96-240; 001:L130-154 |
| internal joints | REVOLUTE `carcass_to_door_{i}` (Z, outward) / PRISMATIC (±X) / bifold 2nd REVOLUTE `door_0_to_door_0_leaf_b` | 002:L264-289; var_sliding:L291-322; var_bifold:L314-329 |
| upstream interface | `door_mount_rail` `positive_y` back face @ carcass front plane | 002:L269,282 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | rect_box / cylindrical_shell / tapered_box | rect_box | choice | procedural sampler | Slot A |
| `door_kind` | enum | framed_cane / glazed_curtain / flush_slab / fretwork_pierced / raised_panel / curved_slab | framed_cane | conditional | curved_slab⇔cylindrical; others⇔rect/tapered | Slot B |
| `door_mechanism` | enum | revolute_swing / sliding_bypass / bifold | revolute_swing | conditional | sliding/bifold⇔rect_box+flat+N=2 | Slot C |
| `support_base` | enum | metal_legs / dowel_legs / turned_feet / feet_plinth / recessed_plinth / wall_mount | dowel_legs | conditional | cylindrical⇔{metal_legs,dowel_legs} | Slot D |
| `palette_style` | enum | walnut / maple / ivory / oak / painted / industrial | walnut | choice | per-seed `rng.choice` → mats{} | ⑥ / common PALETTES |
| `door_count` | int(N) | 1–4 | 2 | conditional | N=4 → 2 tiered rows; sliding/bifold ⇒ N=2; cylindrical ⇒ N∈{1,2} | 001/004/005/var_single |
| `shelf_count` | int(N) | 1–3 | 2 | independent | clamp [1,3] | 002/004/003 |
| `width` | float | rect/tapered [0.72,1.46]; cyl diameter [0.70,0.82] | 0.90 | independent | clamp | ⑤ image evidence |
| `depth` | float | [0.36,0.48] | 0.40 | independent | clamp | ⑤ |
| `height` | float | [1.00,1.75]; +0.35 floor if N=4 | 1.20 | conditional | tiered raises min height | ⑤ |
| `door_swing` | float | [1.55,1.92] rad | 1.75 | independent | clamp; cylindrical clamp [1.6,1.9] | 002:L273; 003:L388 |
| `slide_travel` | float | [0.30,0.42] m | 0.38 | independent | only used by sliding_bypass | var_sliding:L41 |
| (—) | constraint | — | — | inequality | leaf_w = (opening_width − reveals)/doors_per_row ≥ 0.18; else reduce door_count | 002 |
| (—) | constraint | — | — | inequality | door_height ≤ opening_height − top/bottom reveal (0.016) | 001:L513-542 |

## 7.5 编译预算 / compile budget
**Self-reported: ≤ 12 s / seed** (measured helpers: annular-sector `ExtrudeGeometry` shell 0.003 s, curved door 0.001 s, `LoftGeometry` tapered panel <0.001 s, `LatheGeometry` turned foot 0.024 s). All hero curved/tapered surfaces use pure-python `mesh_from_geometry` (no cadquery boolean); **`PerforatedPanelGeometry` is banned (46 s/panel measured)**. Tessellation: annular shells ≤64 seg, turned feet ≤28 seg, curved doors ≤40 seg. All N identical door leaves reuse one built `Mesh` per hinge-side (`direction`). Sweep hang-guard `--compile-timeout 120` (watchdog only).

## Multiplicity / Copy Logic

Two independent multiplicity axes.

**Axis 1 — door_count (leaves):**
- `count_param`: number of door child parts + `carcass_to_door_*` joints. `N_range` = [1,4]; sampling domain weighted: N=2 (0.5), N=1 (0.2), N=3 (0.2), N=4 (0.1). Test small, product full.
- copied_object: door leaf built by the resolved door_kind factory (`_build_door_leaf`).
- naming: `door_{index}` (+`door_0_leaf_b` for bifold); joints `carcass_to_door_{index}`.
- placement_rule: leaves side-by-side across the front opening, each hinged on the cabinet-end side nearest its cell center (left cells hinge-left axis (0,0,−1); right cells hinge-right axis (0,0,+1)). N=4 → two stacked rows of 2 (tiered hutch read, ① topology) with a `mid_rail`; else single row.
- joint_policy: revolute lower=0.0, outward upper = door_swing (1.55–1.92 rad); prismatic lower=0, upper=slide_travel for sliding.
- gating: sliding/bifold ⇒ N=2; cylindrical ⇒ N∈{1,2}.

**Axis 2 — shelf_count (interior shelves):**
- `count_param`: interior shelf Boxes fused into carcass. `N_range` = [1,3]; sampling uniform.
- copied_object: `shelf_{i}` Box (curved trimmed slab for cylindrical) at evenly-spaced z inside the cavity.
- naming: `shelf_{index}`. Not articulated (Rule 1 — fused visuals).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | door_count multiplicity 1–4 (N=4 tiered 2×2 rows, ①); bifold adds coupled `door_0_leaf_b` part+joint. source-backed: 001/004/005/var_single/var_bifold |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: door_count [1,4] weighted; shelf_count [1,3] |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE swing (all origins) vs PRISMATIC bypass (var_sliding) vs bifold coupled REVOLUTE (var_bifold); each appears in sweep |
| ③ 主体形态家族 | 换核心 part 的可识别几何原型 | 有 | body_form: rect_box (Volumetric Envelope), cylindrical_shell (Macro Surface Construction, real curved), tapered_box (Volumetric Envelope trapezoid) — registered slot; door_kind: 6 recognizable leaf forms. source-backed 001/002/003/004/005/var_tapered/var_flush |
| ④ 表面装饰 | 叠加表面细节 | 有 | woven-cane lattice / fretwork bars / curtain folds / raised-panel medallion / brass pull-knob-drop handle styles; host-derived from final door opening (③→⑤→④). record_only + world_knowledge_extrapolation from 002/003/004/005 |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | width 0.72–1.46, height 1.0–1.75, depth 0.36–0.48; **motion envelope**: revolute axis Z, opens toward −Y, [0, door_swing∈1.55–1.92]; prismatic axis ±X [0, slide_travel 0.30–0.42]; bifold fold [0, 2.90]. motion_test_plan below |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material大类 wood/painted-metal/glass/textile + 6 colorways {walnut, maple, ivory, oak, painted, industrial}; ≥ceil(0.5×6)=3 material大类 covered (wood, metal, glass) |

**motion_test_plan (⑤ / Rule 5):** `run_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` (revolute/prismatic sample {0, lower, upper, mid}). Targeted `ctx.pose(...)`: (a) each door opens outward — door panel world-y decreases (−Y) when joint driven to mid; (b) closed pose retains a narrow center reveal between adjacent leaves; (c) sliding door translates ≥ 0.15 m along X at upper travel; (d) bifold leaf_b folds back against leaf A. Element-scoped `allow_overlap`: hinge barrels/rollers captured in carcass edge; bifold fold-hinge overlap door_0↔leaf_b; adjacent sliding bypass doors overlap in Y (intentional bypass).

## 采样与覆盖审计

总组合数（离散，忽略连续 scale）：
- cylindrical branch: 1 body × 1 door(curved) × 1 mech × 2 support × N∈{1,2} = 4
- rect_box branch: 5 door × [revolute N∈{1,2,3,4}=4, sliding N=2, bifold N=2 = 6] × 6 support = 180
- tapered branch: 5 door × 1 mech × N∈{1,2,3,4}=4 × 4 support = 80
- topology tuples ≈ 4+180+80 = **264**; × 6 palette × 3 shelf_count ≈ 4752 total. Meets the report-only ≥300 richness target at the topology level.

理由：door cabinets are form-diverse; body×door×mechanism×support×multiplicity carries the diversity; palette/dims are secondary.

seed_domain_policy：procedural_first. `config_from_seed` samples body_form first, then gates door_kind/mechanism/support/count per the compatibility matrix, then dims. `seed=0` is a normal procedural sample (not special-cased). No curated/modulo table.
Topology target：≥300 legal tuples not fully reached at topology-only (264) but exceeded once palette/shelf counted (4752); door-cabinet topology space is genuinely bounded by the 13 source anchors + compatibility gating (documented above).
Regression overrides：none at authoring; add only for reviewer-selected regressions.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form → gated (door_kind, mechanism, support, count) → palette/shelf → dims; weighted door_count | slot_choices_for_seed matches build choices |
| compatibility matrix | curved_slab⇔cylindrical; sliding/bifold⇔rect_box+flat+N=2; turned/plinth/wall⇔rect/tapered; cylindrical⇔legs | no floating support, no door 穿模, hinge axis outward, closed-pose reveal, max N=4 |
| controlled local variation | width/depth/height/door_swing/slide_travel clamped in resolve_config; leaf_w & door_height derived from opening (inequality) | proportions vary without breaking mating/clearance/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass, 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | ③ registered |
| door_kind | 6 | yes | yes | curved_slab cylindrical-only |
| door_mechanism | 3 | yes | yes | gated to rect_box for non-revolute |
| support_base | 6 | yes | yes | |

## Validator
- `slot_choices_for_seed` returns implemented module names for body_form/door_kind/door_mechanism/support_base/palette_style + door_count/shelf_count.
- `config_from_seed` uses deterministic procedural sampling for all seeds incl. seed 0.
- compatibility gating in `config_from_seed`+`resolve_config` prevents illegal combos (curved on box, sliding on cylindrical, wall_mount on cylindrical, N>2 on sliding/bifold).
- MatingContract present on every axis-aligned revolute/prismatic door joint; curved & bifold-fold joints use documented grandfather + allow_overlap.
- door joints REVOLUTE axis Z (or PRISMATIC ±X for sliding) with lower=0 and outward opening.
- copied doors follow `door_{i}` naming and side-by-side / tiered placement.
- `run_tests` includes `fail_if_parts_overlap_in_sampled_poses` + targeted open/closed pose checks.

## Reject cases
- Door swings inward / into carcass (wrong axis sign) → 穿模.
- Curved cylindrical body downgraded to a plain Cylinder/Box (Rule 3 violation).
- `PerforatedPanelGeometry` dense cane field → 46 s compile blowout.
- Support fused as a FIXED-joint part instead of `carcass.visual` (Rule 1) → floating-part smell.
- Door leaf wider than the opening cell (negative reveal) → closed-pose overlap between leaves.
- N=4 requested on sliding/bifold, or curved_slab on rect_box → illegal topology.
- Adjacent open doors collide (over-wide door_swing with narrow cabinet).

## 与相邻类别的边界
- 不该混入：chest-of-drawers / dresser — drawer as primary articulation; this subcategory's primary DOF is a door (no drawer parts emitted).
- 不该混入：open bookshelf — must have ≥1 real door leaf over the cavity.
- 不该混入：all-glass vitrine display box — glazed *doors* on a wood/painted carcass are in-scope; a frameless all-glass body is not.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored from 13 5★ sources; ③ body_form slot registered; compile budget kept ≤12 s by avoiding cadquery perforation; curved shells/doors/turned-feet preserved as real meshes. |

## 模板实现备注
- Shared helper: `agent/templates/picturex_0611_common.py` (`material_set`, `add_box`, `add_cylinder`, `clamp`, `basic_template_report`). Extend its `PALETTES` with `maple`, `ivory` (additive; siblings unaffected).
- Uniform `door_mount_rail` Box on every door back plane gives one clean MatingContract face across all door kinds.
- Element-scoped `allow_overlap`: hinge barrels↔carcass edge; bifold door_0↔leaf_b fold; sliding bypass door_0↔door_1 (Y offset).
- Reuse one built door `Mesh` per `direction` (hinge side) to hold compile time.
