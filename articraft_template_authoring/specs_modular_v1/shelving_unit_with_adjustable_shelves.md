# shelving_unit_with_adjustable_shelves — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `shelving_unit_with_adjustable_shelves` |
| template path | `agent/templates/shelving_unit_with_adjustable_shelves.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity on shelf_count) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 (origin + 7 forked variants synced) |
| read_count | 8 |
| read_scope | all synced records for `shelving_unit_with_adjustable_shelves` |
| source_index_policy | only adopted module sources are indexed below |

Source records (in `data/records/`):

- `rec_picturex_0611__shelving_unit_with_adjustable_shelves__001__png_533ba1a88611432880d7a18eb92b3cf3` (origin: stepped modular open shelving; welded box grid frame + open cubbies + adjustable shelves + pull-out trays)
- `rec_0611_shelving_unit_with_adjustable_var_frame_open_ladder` (①: ladder-style frame — only end uprights)
- `rec_0611_shelving_unit_with_adjustable_var_frame_wall_rail` (①/③: wall-rail frame — top rail + drop uprights)
- `rec_0611_shelving_unit_with_adjustable_var_adjustment_peg_brackets` (②: shelf brackets via peg-holes; welded grid frame)
- `rec_0611_shelving_unit_with_adjustable_var_adjustment_slotted_standards` (②: slotted metal standards; welded grid frame)
- `rec_0611_shelving_unit_with_adjustable_var_shelf_count_3` (N=3 adjustable shelves)
- `rec_0611_shelving_unit_with_adjustable_var_shelf_count_5` (N=5 adjustable shelves — matches origin)
- `rec_0611_shelving_unit_with_adjustable_var_shelf_count_7` (N=7 adjustable shelves)

## 核心身份

**Physical meaning.** A grounded, open, multi-level storage unit whose defining feature is a set of PRISMATIC shelves that can be re-pinned to different vertical positions on a rigid upright structure. The uprights (posts / ladder / wall rail) are always the fixed parent; every non-fixed joint is a shelf or a tray. Optional fixed decorations (open cubbies) and optional pull-out trays populate the same frame.

**Must keep.** Vertical support skeleton (posts, ladder rails, or wall drop-rails) + horizontal cross rails + at least one PRISMATIC shelf with `axis=(0,0,1)` and a short vertical travel + a stable floor stance.

**Must not become.** Plain cabinet (fully enclosed sides + door), dining table without storage, single-shelf floating wall shelf, drawer chest.

## 槽位 + 候选模块表

### Slot A — `frame_form` (③ Primary Form Family; ① upright skeleton)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `welded_box_grid` | forked_anchor | `rec_picturex_0611__shelving_unit_with_adjustable_shelves__001__png_...` (origin) + `rec_0611_..._var_adjustment_peg_brackets` + `rec_0611_..._var_adjustment_slotted_standards` | origin L245-L366 | eligible | Full welded steel-tube grid: 4 corner + interior posts, cross rails at each level, depth rails at every intersection. `form_subtype = Volumetric Envelope Form` (dense rectangular cage). |
| `open_ladder_frame` | forked_anchor | `rec_0611_..._var_frame_open_ladder` | model.py L245-L346 | eligible | Only two end uprights per section (no interior posts); horizontal rungs at each level span full width; depth rails only at end posts. `form_subtype = Macro Surface Construction` (open skeletal ladder). |
| `wall_rail_frame` | forked_anchor | `rec_0611_..._var_frame_wall_rail` | model.py L245-L360 | eligible | Continuous top horizontal rail with drop uprights hung from the rail; bottom rail at floor. Reads as a rail-hung system rather than a cage. `form_subtype = Planar Boundary Form` (flat frontal rail plane). |

### Slot B — `adjustment_mechanism` (② joint hardware for the shelves)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hook_brackets` | forked_anchor | origin record | L109-L179 | eligible | Four small charcoal-steel bracket blocks under each shelf hook onto front/rear rails. Short PRISMATIC vertical travel ~50 mm. |
| `peg_brackets` | forked_anchor | `rec_0611_..._var_adjustment_peg_brackets` | model.py L109-L179 | eligible | Pin/peg style bracket cylinders under each shelf sit in pin-holes drilled into the posts. Same joint semantics; distinct bracket geometry. |
| `slotted_standards` | forked_anchor | `rec_0611_..._var_adjustment_slotted_standards` | model.py L109-L179 | eligible | Vertical slotted metal standards riveted to posts; L-clip brackets hook into slots. Bracket geometry is a longer L-tab. |

### Slot C — `shelf_count` (multiplicity axis, ① same-part × N)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `count_3` | forked_anchor | `rec_0611_..._var_shelf_count_3` | model.py L379-L399 | eligible | 3 adjustable shelves distributed on the tall frame section. |
| `count_5` | forked_anchor | origin | L379-L405 | eligible | 5 adjustable shelves (canonical). |
| `count_7` | forked_anchor | `rec_0611_..._var_shelf_count_7` | model.py L379-L410 | eligible | 7 adjustable shelves. |

### Slot D — `insert_module` (optional pull-out storage; ② PRISMATIC axis y-)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | `rec_0611_..._var_shelf_count_3` (no trays instantiated in build_object_model tray region) | model.py L400+ | eligible | No trays instantiated; frame has runners but no non-fixed insert. |
| `pull_out_trays` | forked_anchor | origin | L402-L426 | eligible | 3–6 shallow open trays per frame, each PRISMATIC y-, short pull-out. |

### Slot E — `palette_style` (⑥ material palette; source-backed + realistic companions)

| module_name | source_type | source evidence | 结构特征 |
|---|---|---|---|
| `charcoal_walnut_oak` | forked_anchor | origin materials (`charcoal_steel`, `walnut`, `walnut_shadow`, `light_oak`, `oak_edge`) | Warm two-tone wood on charcoal steel — canonical reference colorway. |
| `painted_white` | record_only + world_knowledge_extrapolation | anchors: origin + `..._var_adjustment_slotted_standards` (steel/oak/walnut colorway) + reviewer | Painted-white steel frame + light oak shelves + brushed hardware — realistic companion. |
| `industrial_black_steel` | record_only + world_knowledge_extrapolation | anchors: origin (charcoal_steel base) | All-steel: black frame, dark grey shelves, chrome hardware. |
| `natural_ash` | record_only + world_knowledge_extrapolation | anchors: origin (light_oak / oak_edge) | Pale ash uprights, honey shelves, brass hardware. |

## 槽位图（slot graph）

pattern: `mixed` — `frame_form` (parent) with `parallel_children` shelves + optional trays; the shelf group is a `multiplicity` axis.

```
frame_form (fixed root)
   ├──[FIXED, at floor plane]──> (world)
   ├──[PRISMATIC z, MatingContract bracket→post_rail]──> shelf_0 .. shelf_{N-1}   (N = shelf_count)
   └──[PRISMATIC -y, MatingContract tray_bottom→tray_runner]──> tray_0 .. tray_{M-1}   (M = 0 or M_default)
```

- The frame is always the fixed root; every non-fixed joint has `parent = frame`.
- Shelf joints: axis `(0,0,1)`, `MotionLimits(lower=0, upper≈0.05, effort=120, velocity=0.08)`.
- Tray joints (when Slot D = `pull_out_trays`): axis `(0,-1,0)`, `MotionLimits(lower=0, upper≈0.18, effort=45, velocity=0.20)`.
- Optional fixed decorations (open cubbies) are additional FIXED-joint children of the frame; they carry no articulation and are only present in `welded_box_grid`.

## 每槽位 Module Emits / Interfaces

### Slot A / `frame_form`
| emits | 描述 | 来源 |
|---|---|---|
| parts | Single `frame` part with many `Box` visuals (posts / rungs / rails / feet). | origin model.py L267-L358 |
| internal joints | none (frame is a solid rigid part). | — |
| upstream interface | Grounded via lowest visual box `z ≈ 0`; `frame` is the fixed root of the object. | origin L294-L307 |
| downstream interface | Front/rear rails at discrete `z` levels expose horizontal support surfaces where shelves and trays mate. Named `tall_cross_rail_*`, `low_cross_rail_*`, `tray_runner_*`. | origin L309-L347 |

### Slot B / `adjustment_mechanism`
| emits | 描述 | 来源 |
|---|---|---|
| parts | Extra bracket geometry added into the shelf part (as visuals) — pegs / hook brackets / slotted L-clips. | origin L149-L162 |
| internal joints | none. | — |
| upstream interface | Bracket-underside face (`support_bracket_0..3` visuals) mates to a frame `tall_cross_rail_*` top face (`positive_z`). | origin L146-L162 |
| downstream interface | Shelf slab centered above bracket layer. | origin L134-L144 |

### Slot C / `shelf_count`
| emits | 描述 | 来源 |
|---|---|---|
| parts | N shelf parts named `shelf_{i}` (`i ∈ [0, N)`). | origin L379-L405 |
| internal joints | one PRISMATIC joint per shelf, `frame → shelf_{i}`. | origin L164-L178 |
| upstream interface | Bracket bottoms sit on a `tall_cross_rail_*` top; distributed at even levels. | origin L164-L178 |
| downstream interface | Shelf top face at `support_level + FRAME_TUBE/2 + bracket_h + SHELF_T`. | origin L124-L127 |

### Slot D / `insert_module`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 0 or M tray parts `tray_{j}`. | origin L400-L426 |
| internal joints | one PRISMATIC per tray, `frame → tray_{j}`, axis `(0,-1,0)`. | origin L227-L241 |
| upstream interface | Tray bottom (`bin_bottom` visual, `negative_z`) mates to a `tray_runner_*` top face (`positive_z`). | origin L200-L204 |
| downstream interface | Tray front lip visible outside the frame front plane. | origin L220-L225 |

### Slot E / `palette_style`
| emits | Materials (`case_metal`, `shelf_wood`, `edge_wood`, `bracket_metal`, `foot_rubber`) registered on the model; every visual sets `material=mats[...]`. |
| upstream interface | none (naming policy). |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | `welded_box_grid` / `open_ladder_frame` / `wall_rail_frame` | `welded_box_grid` | choice | procedural sampler | slot A |
| `adjustment_mechanism` | enum | `hook_brackets` / `peg_brackets` / `slotted_standards` | `hook_brackets` | choice | procedural sampler | slot B |
| `shelf_count` | int | {3, 4, 5, 6, 7} | 5 | independent | integer sampling, clamp `[3,7]` | slot C |
| `has_pull_out_trays` | bool | {False, True} | True | independent | boolean sampling | slot D |
| `tray_count` | int | {3, 4, 5, 6} | 6 | conditional | only when `has_pull_out_trays`; else 0 | slot D |
| `palette_style` | enum | `charcoal_walnut_oak` / `painted_white` / `industrial_black_steel` / `natural_ash` | `charcoal_walnut_oak` | choice | procedural sampler | slot E |
| `frame_width` | float | [1.60, 2.40] m | 2.22 | independent | clamp | origin geometry |
| `frame_height` | float | [1.60, 2.30] m | 2.16 | independent | clamp | origin geometry |
| `frame_depth` | float | [0.36, 0.50] m | 0.44 | independent | clamp | origin geometry (`FRAME_DEPTH`) |
| `shelf_travel` | float | [0.035, 0.075] m | 0.055 | independent | clamp | origin L172-L176 |
| `tray_travel` | float | [0.14, 0.20] m | 0.18 | independent | clamp | origin L234-L239 |
| (—) | constraint | — | — | inequality | `shelf_slab_width ≤ single_bay_width − 2·(post_half + clearance)` (avoid post clipping) | origin L36-L45 `_crosses_interior_post` |
| (—) | constraint | — | — | inequality | shelf `support_level` values must lie within `[0.05, frame_height − 0.10]`; even distribution `support_level_i = z_low + i·(z_high−z_low)/(N−1)` | frame layout |
| (—) | constraint | — | — | inequality | tray `center_x` must be in a bay center (never at a post-x); tray depth ≤ `frame_depth` | origin L343-L347 |

### 7.5 编译预算

**Budget: 25 s per seed.** Justification: dozens of `Box` visuals on a single frame + a variable number of shelves/trays (each with ~6 boxes). Purely box primitives, no boolean operations → similar to `drawer_cabinet_with_sliding_drawers` (~15 s) but with 2–3× visual count. All shelves and trays reuse a single small `Box`-based helper — no meshes.

## Multiplicity / Copy Logic

Two independent multiplicity axes:

- **shelf_count** (main axis)
  - `count_param`: `shelf_count`
  - `N_range`: `[3, 7]` (product domain 3–7; test range clamps to source-observed 3/5/7)
  - copied object: shelf part with bracket visuals
  - naming: `shelf_{i}`, `i ∈ [0, N)`; joint `frame_to_shelf_{i}`
  - placement: shelves evenly distributed by `support_level_i` over the tall bay region; same `center_x` unless bay index rotates
  - joint policy: identical PRISMATIC z-axis for every shelf
  - source/gating: enabled when `frame_form ∈ {welded_box_grid, open_ladder_frame, wall_rail_frame}` (all)
- **tray_count** (secondary axis)
  - `count_param`: `tray_count`
  - `N_range`: `[0, 6]`; 0 when `has_pull_out_trays=False`
  - copied object: tray part with tray box visuals
  - naming: `tray_{j}`, `j ∈ [0, M)`; joint `frame_to_tray_{j}`
  - placement: `center_x` picked from an ordered list of bay centers; tray depth clipped to `frame_depth`
  - joint policy: identical PRISMATIC y-axis, negative direction

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 详情 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `frame_form` picks the upright skeleton family (grid vs ladder vs wall-rail); `shelf_count` and `tray_count` add/remove non-fixed edges; source_type=forked_anchor. |
| └ multiplicity | 同构件 ×N | 有 | 见 §Multiplicity (shelf_count 3-7, tray_count 0-6). |
| ② 关节类型 | 图不变,某条边换 type/轴 | 有 | Every shelf: PRISMATIC z axis (`hook_brackets` / `peg_brackets` / `slotted_standards` all realize the same PRISMATIC axis but with distinct visible hardware). Every tray: PRISMATIC -y. Cubbies (when present): FIXED. source_type=forked_anchor. sweep asserts both PRISMATIC types appear. |
| ③ 主体形态家族 | 图&关节不变,换核心 part 的可识别几何形态原型 | 有 | `frame_form` slot: 3 candidates, each labelled with `form_subtype` (Volumetric Envelope / Macro Surface Construction / Planar Boundary), all source-backed and registered in `slot_choices`. |
| ④ 表面装饰 | 原型不变,叠加表面细节 | 有 | Open cubbies are host-conformal fixed decorations for `welded_box_grid` (record_only). Tray front lip, shelf front edge band — all authored as parent visuals on frame/shelf/tray. No independent decoration parts. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `frame_width`, `frame_height`, `frame_depth`, `shelf_travel`, `tray_travel` (see §7). Shelf-joint envelope: axis (0,0,1), [closed=0, upper∈[0.035,0.075]]; tray joint envelope: axis (0,-1,0), [0, upper∈[0.14,0.20]]. `motion_test_plan`: `ctx.pose({shelf_joint: upper})` — check shelf translates upward; `ctx.pose({tray_joint: upper})` — check tray translates in -y. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 4 palette styles covering (a) warm wood+steel, (b) painted white steel, (c) industrial black steel, (d) natural ash + brass. Material categories: `metal` (steel/brushed), `wood` (walnut/oak/ash/painted). Coverage ≥ 2 material categories per palette; ≥ 3 palettes across the sweep. |

## 采样与覆盖审计

总组合数：`frame_form × adjustment × shelf_count × has_trays × palette` = 3 × 3 × 5 × 2 × 4 = **360**; plus 4 continuous scales — sufficient to saturate a 40-seed sweep.

seed_domain_policy: `procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses `random.Random(seed)` to independently sample each enum slot from its candidate tuple, sample `shelf_count` uniformly in `[3,7]`, sample `has_pull_out_trays` (True 60% / False 40%), sample `tray_count` in `[3,6]` when trays enabled, sample continuous scales uniformly in their ranges, and clamp. `seed=0` reproduces the canonical origin colorway + `welded_box_grid` + `hook_brackets` + `shelf_count=5` + trays on.
Topology target: 40-seed sweep exhausts frame_form × adjustment combinations with ≥ 4 replicas each; 1000-seed run reserved for maturity audit (report only).
Regression overrides: none at P0.
Controlled local parameterization: `frame_width`, `frame_height`, `frame_depth`, `shelf_travel`, `tray_travel`. All clamped in `resolve_config` under §7 constraints and validated against post-clearance and joint-range inequalities before the builder runs.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 5 enum slots + 4 continuous scales, no compatibility gate | `slot_choices_for_seed` matches build choices |
| compatibility matrix | none required (all frames accept all adjustments and shelf counts) | no floating shelf, no post clipping |
| controlled local variation | frame/shelf/tray scales, clamped | proportions vary without breaking bays |
| regression overrides | none | — |
| random sweep | seeds 0-39 first pass, 0-999 maturity | axis realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 3 | yes | yes | |
| adjustment_mechanism | 3 | yes | yes | |
| shelf_count | 5 | yes | yes | multiplicity |
| insert_module | 2 | yes | no | boolean gate — trays on/off |
| palette_style | 4 | yes | yes | |

## Validator

- `slot_choices_for_seed(seed)` returns the same 5-tuple that `build_shelving_unit_with_adjustable_shelves(config_from_seed(seed))` actually realizes.
- `config_from_seed` uses deterministic procedural sampling; `seed=0` returns canonical anchor config.
- `resolve_config` clamps every continuous scale and evaluates the inequality set before returning.
- `frame` part exists and is the unique root.
- Exactly `shelf_count` PRISMATIC z-axis joints exist, all parented to `frame`; each has `MotionLimits(lower=0, upper ∈ [0.035, 0.075])`.
- When `has_pull_out_trays=True`, exactly `tray_count` PRISMATIC -y-axis joints exist, all parented to `frame`; each has `MotionLimits(lower=0, upper ∈ [0.14, 0.20])`.
- Every non-fixed joint declares a `MatingContract` (bracket→rail or tray_bottom→runner).
- Every shelf slab clears every interior post in world x (no post clipping).
- Palette materials cover ≥ 2 material categories.
- `ctx.pose({shelf_joint: upper})` — shelf world z rises by ≥ shelf_travel − 0.005.
- `ctx.pose({tray_joint: upper})` — tray world y decreases by ≥ tray_travel − 0.02.

## Reject cases

- Shelf slab authored wider than a bay → clips a post → fail.
- Shelf `parent != "frame"` (e.g., shelf mounted on another shelf) → violates category identity.
- Tray joint axis not `(0,-1,0)` or with `lower != 0` → wrong motion semantics.
- Missing `MatingContract` on a non-fixed joint → violates B/§B contract.
- Frame is not a single unique root part → violates skeleton.
- No PRISMATIC joint at all → not an adjustable shelf.
- Origin far from geometry (`fail_if_articulation_origin_far_from_geometry` > 0.02).

## 与相邻类别的边界

- 不该混入：Plain cabinet — this category is open; no full enclosure + door.
- 不该混入：Dining table without storage — the frame here always carries adjustable shelves as its defining feature.
- 不该混入：Floating wall shelf — this unit has its own floor stance; not wall-anchored.
- 不该混入：Drawer chest — no sliding closed drawers as the primary storage; only optional open pull-out trays.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Initial modular spec derived from origin + 7 forked variants. |
