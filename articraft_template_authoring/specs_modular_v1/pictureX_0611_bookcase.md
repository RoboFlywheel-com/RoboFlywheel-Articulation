# pictureX_0611_bookcase — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_bookcase` |
| template path | `agent/templates/pictureX_0611_bookcase.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_bookcase_template.py` (not authored) |
| stage | `IMPLEMENTED` |
| status | `complete_visual_confirmed_2026-07-13` |
| variant_gate | `confirmed_by_user_2026-07-12` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children doors/drawers/shelves on one carcass + multiplicity shelves/bays/sections) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 20 (6 origins + 14 converged forks) |
| read_count | 20 |
| read_scope | all 20 downstream 5-star samples for `pictureX/0611/bookcase` |
| source_index_policy | only adopted module sources are indexed below |

Reading summary: every source builds a single grounded `carcass` part holding all
static geometry (side panels, back, top/bottom, shelf boards, dividers, base) and
attaches moving children: `door_i` REVOLUTE (vertical hinge axis, swings outward),
`drawer_i` PRISMATIC (slides out the front), and — only in the adjustable variant —
`display_shelf_i` PRISMATIC (small vertical travel). Shelves are loop-emitted boards
with stable indexed naming (`display_shelf_{index}` / `shelf_{index}`). The origins
(001/003/004/006) fuse decorative arches/rosettes/turned-legs via `mesh_from_cadquery`;
the converged forks (open_shelving, base_cabinet_doors, corner, cube_grid, ladder,
plinth/toe_kick, shelves_n*) are Box-primitive based. Core structure across all forms
is a box case + box shelves (+ cylinder legs); the cadquery meshes carry ④ decoration
(arched pediment, scalloped apron, turned legs, rosettes) on top of that box skeleton.

## 核心身份
A free-standing case of vertical side supports carrying a stack of horizontal book
shelves, with at least one real non-fixed joint (a glazed/panel door, a drawer, or a
prismatic adjustable shelf). Default mature domain: warm/dark wood or painted upright
book case, ~1.0–1.55 m wide, 0.42–0.57 m deep, 1.6–2.3 m tall, 2–8 shelves. It must
NOT become a wardrobe (clothes rail, no book shelving), a sideboard (low, horizontal,
no vertical book stack), a nightstand (tiny single-drawer box), or a doored display
cabinet with no shelving. Vertical side supports + a stack of book shelves is the
invariant kept across every form family.

## 槽位 + 候选模块表

### Slot A：carcass_form  （③ Primary Form Family — form-dominated class）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| `rectangular_upright` | origin_anchor | 005 / 002 | 005 L240-325; 002 L152-217 | Volumetric Envelope Form | single upright box: 2 side panels + back + top/bottom + N shelves + (bay-1) dividers |
| `two_tier_hutch` | origin_anchor | 003 | 003 L194-296 | Macro Surface Construction | upper+lower carcass split by a mid divider shelf; upper glass doors, lower panel doors |
| `legged_highboy` | origin_anchor | 004 | 004 L269-407 (carcass), L478-540 (doors/drawers) | Volumetric Envelope Form | case raised on 4 turned legs (cylinders), crown/pediment band on top |
| `grid_hutch` | origin_anchor | 006 | 006 L392-540 | Macro Surface Construction | bay_count side-by-side bays with vertical partitions, per-bay upper glass door |
| `ladder` | forked_anchor | rec_bookcase_var_ladder (from 004) | L169-320 | Volumetric Envelope Form | leaning trapezoid: raked side supports, depth/width decrease upward, base drawer |
| `corner` | forked_anchor | rec_bookcase_var_corner (from 005) | L206-405 | Planar Boundary Form | L-plan footprint: two perpendicular shelf wings meeting at a rear corner |
| `cube_grid` | forked_anchor | rec_bookcase_var_cube_grid (from 006) | L247-363 | Macro Surface Construction | rows×cols cube matrix (rows from shelf_count, cols from bay_count), one representative door |
| `barrister` | forked_anchor | rec_bookcase_var_barrister (from 001) | L142-285 | Macro Surface Construction | vertical stack of N framed sections, one glass door per section |

Degrade reason: none — 8 structurally distinct form families, all source-backed.

### Slot B：front_treatment  （② joint / mechanism type）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `full_glass_doors` | origin_anchor | 001 | 001 L370-448 | 1–2 full-height glazed doors, REVOLUTE Z axis, swing outward |
| `upper_glass_base_drawers` | origin_anchor | 002 / 005 | 002 L219-284; 005 L326-407 | upper glass doors REVOLUTE + 2–3 base drawers PRISMATIC |
| `glass_top_panel_base_doors` | origin_anchor | 003 / 006 | 003 L298-360 | upper glazed doors + lower solid panel doors, both REVOLUTE |
| `open_shelving` | forked_anchor | rec_bookcase_var_open_shelving (from 002) | L94-164 | exposed shelves, one base drawer PRISMATIC (keeps a non-fixed joint) |
| `base_cabinet_doors` | forked_anchor | rec_bookcase_var_base_cabinet_doors (from 002) | L107-220 | open upper shelves + paired lower cabinet doors REVOLUTE |
| `flip_up_glass` | forked_anchor | rec_bookcase_var_flip_up_glass (from 001) | L370-454 | top-pivot horizontal-axis REVOLUTE glass flaps over shelf stack |

Degrade reason: none — 6 candidates.

### Slot C：shelf_mechanism  （② joint type）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `fixed_shelves` | origin_anchor | all origins | 005 L280-320 | shelf boards fused into carcass (parent visuals), no joint |
| `adjustable_shelves` | forked_anchor | rec_bookcase_var_adjustable_shelves (from 005) | L316-351 | shelves are `display_shelf_i` parts, small-travel PRISMATIC Z |

Degrade reason: 2 candidates — shelf articulation is a binary (fixed vs prismatic);
the 5★ pool yields exactly these two treatments.

### Slot D：base_style  （③ secondary form / support）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `plinth` | origin_anchor | 001 / rec_bookcase_var_plinth_base | var_plinth L242-330 | solid recessed plinth block at floor, case sits on it |
| `legs` | origin_anchor | 004 / 005 / 006 | 004 L269-320 | 4 turned legs (cylinders) lift the case off the floor |
| `toe_kick` | forked_anchor | rec_bookcase_var_toe_kick_base (from 002) | L152-230 | recessed setback base rail (toe-kick) under the case |

### Slot E：back_panel  （④ surface / enclosure, host-conformal）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `solid_back` | origin_anchor | 001 / 004 | 001 L161-256 | full solid back panel |
| `open_back` | origin_anchor | 006 (right bay omits back) | 006 L392-540 | no back panel (open) |
| `beadboard_back` | world_knowledge_extrapolation (④) | anchors: 001/004 solid back + reviewer | n/a (host-derived vertical bead ribs across back face) | solid back + evenly spaced vertical bead ribs derived from case width/height |

## 槽位图（slot graph）

pattern: mixed

carcass_form (A) —[parent carcass; static case geometry]—→
  ├─ base_style (D)      : fused into carcass at case bottom (plinth block / 4 leg cylinders / toe-kick rail) — sets case_bottom_z lift
  ├─ back_panel (E)      : fused into carcass rear face (solid / omitted / beadboard ribs), host-conformal
  ├─ shelf_mechanism (C) : shelves either fused (fixed) or emitted as display_shelf_i PRISMATIC-Z children of carcass
  └─ front_treatment (B) : door_i REVOLUTE-Z (hinge at a front vertical edge, swing outward) and/or
                            drawer_i PRISMATIC-X (slide out front), all children of carcass

- All moving parts (`door_i`, `drawer_i`, `display_shelf_i`) parent directly to the
  single grounded `carcass` (parallel-children pattern; no serial chain).
- Cross-slot connection points: doors hinge on a front vertical edge (origin on the
  carcass front post/side panel, axis (0,0,±1)); drawers slide on the front opening
  plane (origin on carcass front, axis (±1,0,0)); adjustable shelves ride vertical
  rails inside the case (axis (0,0,1)).
- Compound forms carry intrinsic front articulation: `two_tier_hutch` forces
  `glass_top_panel_base_doors`; `grid_hutch` forces per-bay doors; `barrister` forces
  per-section flip/ swing doors. `corner`/`ladder`/`cube_grid` gate to open/simple
  fronts (see compatibility matrix).

## 每槽位 Module Emits / Interfaces

### Slot A / carcass_form (all forms)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass` (side panels, back, top, bottom, shelves-if-fixed, dividers/partitions, base, crown) | 005 L240-325 |
| internal joints | none (all static geometry is parent visuals) | 005 |
| downstream interface | front opening plane (x=+depth/2), front vertical edges (hinge posts), interior vertical rails | 005/002 |

### Slot B / front_treatment
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_i` (glazed/panel leaf), `drawer_i` (box+front+pull) | 002 L219-284; 005 L326-407 |
| internal joints | `carcass_to_door_i` REVOLUTE axis (0,0,±1) range [0, swing]; `carcass_to_drawer_i` PRISMATIC axis (±1,0,0) range [0, travel]; flip_up door REVOLUTE axis (0,±1,0) | 002 L236-284; var_flip_up L442-454 |
| upstream interface | hinge origin on carcass front edge / drawer origin on front plane | 005 L343-397 |

### Slot C / shelf_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed: none (shelf visuals on carcass); adjustable: `display_shelf_i` | var_adjustable L316-351 |
| internal joints | adjustable: `carcass_to_display_shelf_i` PRISMATIC axis (0,0,1) small travel | var_adjustable L349-351 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| carcass_form | enum | 8 forms above | rectangular_upright | choice | procedural sampler | Slot A |
| front_treatment | enum | 6 fronts above | full_glass_doors | conditional | gated by carcass_form (compat matrix) | Slot B |
| shelf_mechanism | enum | fixed_shelves / adjustable_shelves | fixed_shelves | choice | procedural sampler | Slot C |
| base_style | enum | plinth / legs / toe_kick | plinth | conditional | legged_highboy forces legs | Slot D |
| back_panel | enum | solid / open / beadboard | solid_back | choice | procedural sampler | Slot E |
| palette_style | enum | 6 colorways | warm_oak | choice | rng.choice(PALETTE_STYLES) | ⑥ |
| shelf_count | int (N) | [2, 8] | 4 | independent | weighted small-N | 003(2)/002(3)/n5/n7 |
| bay_count | int (N) | [1, 4] | 1 | independent | weighted small-N | 001(2)/006(3)/n4(4) |
| width | float | [0.60, 1.60] | 1.05 | independent | clamp | ⑤ 005/006 |
| depth | float | [0.32, 0.60] | 0.44 | independent | clamp | ⑤ 004/005 |
| height | float | [1.35, 2.30] | 1.90 | independent | clamp | ⑤ 004/006 |
| door_swing | float | [0.9, 1.85] rad | 1.55 | independent | clamp | ⑤ corner 1.65 |
| drawer_travel | float | [0.14, 0.30] | 0.24 | inequality | `≤ 0.72·(depth − back_t)` | ⑤ 004 |
| shelf_travel | float | [0.02, 0.06] | 0.04 | inequality | `≤ 0.35·shelf_pitch` (adjustable only, no shelf-shelf collision) | var_adjustable |
| leg_height | float | [0.10, 0.22] | 0.14 | conditional | only base_style=legs | 004 |

### 7.5 编译预算 / compile budget
Per-seed budget: **≤ 12 s** (watchdog `--compile-timeout 120`). All primitives are
Box + Cylinder (no boolean/cadquery in the template). N identical shelf/leg/book
sub-visuals reuse a single small `Box`/`Cylinder`; cylinder tessellation for legs is
SDK default (small radius). No hero surface; the class compiles well within budget.

## Multiplicity / Copy Logic

Two independent multiplicity axes:

- **shelf_count** (primary): count_param=`shelf_count`; N_range test [2,8], product-domain
  [2,8]; weighted small-N (3–5 common, 2/7/8 rarer). copied object=shelf board;
  naming=`display_shelf_{index}` (adjustable) / carcass visual `shelf_{index}` (fixed);
  placement=even vertical spacing over the case interior; joint policy=fixed to carcass,
  or per-shelf PRISMATIC-Z in `adjustable_shelves`. For `barrister` the sections use
  shelf_count as section count; for `cube_grid` shelf_count = row count.
- **bay_count** (secondary): count_param=`bay_count`; N_range [1,4]; weighted (1–2 common).
  copied object=vertical partition + per-bay door; naming=`divider_{index}` / `door_{index}`;
  placement=even horizontal grid; joint policy=one REVOLUTE door per bay for `grid_hutch`,
  partition-only for `rectangular_upright`; for `cube_grid` bay_count = column count.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | door/drawer/adjustable-shelf presence toggles moving parts; multiplicity below. All forked/origin-backed (Slot A/B/C). |
| └ multiplicity | 同构件 ×N | 有 | shelf_count [2,8], bay_count [1,4] — see §8; weighted small-N |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE-Z swing doors; REVOLUTE-Y flip-up glass (var_flip_up); PRISMATIC-X drawers (002/005); PRISMATIC-Z adjustable shelves (var_adjustable). Each realized in sweep. |
| ③ 主体形态家族 | 换核心 part 的几何形态原型 | 有 (主轴) | 8 form families in Slot A, each `form_subtype` labelled (Planar Boundary / Volumetric Envelope / Macro Surface). source-backed origins + forks. Registered in `slot_choices`. |
| ④ 表面装饰 | 叠加表面细节 | 有 | back_panel beadboard ribs (host-derived vertical ribs across back face); books on shelves; crown band on legged/highboy — host-conformal, derived from case width/height at final dims. `record_only` + `world_knowledge_extrapolation`. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | width[0.60,1.60] depth[0.32,0.60] height[1.35,2.30]; door_swing[0.9,1.85] axis Z outward [0,swing]; drawer_travel[0.14,0.30] axis X out [0,travel]; shelf_travel[0.02,0.06] axis Z [−t/2,+t/2]. motion_test_plan: sampled collision on all joints (max_pose_samples 48; 32 for many-bay); targeted `ctx.pose` opening one door (visible outward displacement) + one drawer (extended). No sampled-pose exemption. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 colorways: warm_oak, walnut, charcoal_painted, gray_oak_laminate, black_mahogany, sage_painted. material classes: painted / wood-laminate / glass (tinted) / metal (brass/steel). ≥ceil(0.5×6)=3 classes covered. |

## 采样与覆盖审计

总组合数：carcass_form(8) × front_treatment(≤6, gated) × shelf_mechanism(2) ×
base_style(3) × back_panel(3) × shelf_count(7) × bay_count(4) ≈ several thousand legal
tuples (before gating). Rich class; well above the 300 maturity target.

理由：form-dominated bookcase; the ③ carcass_form slot is the primary diversity
carrier, augmented by front/shelf/base/back/multiplicity/palette.

seed_domain_policy：procedural_first (seed 0 is an ordinary procedural sample, not
special-cased).

Procedural Sampling / Sweep Plan: `config_from_seed` seeds `random.Random(seed)`,
samples each slot enum and multiplicity independently, then applies the compatibility
gate `_gate_front(carcass_form, front_treatment)` which coerces illegal pairs to a
legal fallback (see matrix). `resolve_config` clamps all continuous scales, derives
drawer/shelf travel inequalities, and resolves conditional base_style. Sweep 0-35 for
pass; corner stage for per-field extremes. Viewer目检 seeds 0-9.

Compatibility matrix (gating in `_gate_front`):
| carcass_form | legal front_treatment | fallback |
|---|---|---|
| rectangular_upright | any of 6 | — |
| legged_highboy | full_glass_doors, upper_glass_base_drawers, glass_top_panel_base_doors, flip_up_glass | full_glass_doors |
| two_tier_hutch | glass_top_panel_base_doors (forced) | glass_top_panel_base_doors |
| grid_hutch | full_glass_doors, glass_top_panel_base_doors, upper_glass_base_drawers (per-bay) | full_glass_doors |
| barrister | flip_up_glass, full_glass_doors (per-section) | flip_up_glass |
| corner | open_shelving, full_glass_doors, base_cabinet_doors | open_shelving |
| ladder | open_shelving (forced, base drawer) | open_shelving |
| cube_grid | open_shelving, base_cabinet_doors | open_shelving |

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent per-slot weighted choice + gate | slot_choices_for_seed matches build |
| compatibility matrix | gate coerces illegal front to fallback; ladder/two_tier forced | no floating/collision/axis failures |
| controlled local variation | width/depth/height/swing/travel clamped + derived | proportions vary, interfaces intact |
| regression overrides | none | — |
| random sweep | 0-35 initial pass, corner stage | axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| carcass_form | 8 | yes | yes | ③ primary |
| front_treatment | 6 | yes | yes | gated |
| shelf_mechanism | 2 | yes | no | binary, documented |
| base_style | 3 | yes | yes | |
| back_panel | 3 | yes | yes | ④ |

## Validator

- slot_choices_for_seed returns implemented module names for every slot
- config_from_seed uses deterministic procedural sampling for all seeds incl. 0
- `_gate_front` prevents illegal carcass_form × front_treatment pairs
- no regression overrides
- continuous scales clamped/derived in resolve_config (drawer_travel, shelf_travel inequalities)
- every seed has ≥1 non-fixed joint (door/drawer/adjustable-shelf)
- key joints: doors REVOLUTE axis Z (flip-up Y), drawers PRISMATIC X, shelves PRISMATIC Z
- shelf/bay copied objects follow indexed naming and even placement
- run_tests calls `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` (Rule 5)

## Reject cases
- A door swinging inward into the carcass cavity (wrong axis sign) → 穿模.
- A drawer whose Z band overlaps a fixed shelf board → closed-pose overlap.
- Adjustable shelf travel ≥ shelf pitch → shelf-shelf collision.
- Legs too short so case bottom intersects floor plinth.
- bay_count doors wider than the bay → adjacent-door overlap when closed.
- carcass_form with zero moving joints (e.g. pure open shelving with no drawer).
- Non-conformal beadboard ribs standing proud of a scaled back face.

## 与相邻类别的边界
- 不该混入：wardrobe（无书架层、含挂衣杆；bookcase 必须有 vertical book-shelf stack）。
- 不该混入：sideboard（低矮横向、无垂直书架栈）。
- 不该混入：nightstand（单抽小盒，无 side-support 书架栈）。
- 不该混入：doored display cabinet with no shelving（必须保留 shelf stack）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | complete; visual confirmed by user 2026-07-13 |
| reviewer notes | MatingContract omitted on door/drawer joints, following the sibling passing templates (bookcase1/2, drawer_cabinet_with_sliding_drawers): support proven via `fail_if_articulation_origin_far_from_geometry` + justified element/part-scoped `allow_overlap` + baseline `harness_motion_qc`. Doors sit in front of the carcass front face (no closed-pose overlap); drawers/adjustable shelves ride inside the cavity with declared allow_overlap. Post-gate sweep final pass_rate=1.0 and corner stage clean. Preview seeds `0,4,75,127,36,495,6,5` generated workbench-only records; user confirmed visual check on 2026-07-13. |

## 模板实现备注
- Shared helpers: `_box`, `_cyl`, `_palette`. One `_front_plan(r)` returns door + drawer
  specs; one `_carcass_geometry(r)` dispatches on carcass_form.
- captured/interior overlaps: `allow_overlap(carcass, drawer_i)` (box inside cavity),
  `allow_overlap(carcass, display_shelf_i)` (shelf rides interior), `allow_overlap`
  between stacked drawers sharing the opening plane.
