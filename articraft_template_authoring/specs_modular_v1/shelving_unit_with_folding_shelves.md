# shelving_unit_with_folding_shelves — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `shelving_unit_with_folding_shelves` |
| template path | `agent/templates/shelving_unit_with_folding_shelves.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children shelves + folding-arm supports + multiplicity on tier_count) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 (2 origin + 10 forked variants synced) |
| read_count | 12 |
| read_scope | all synced records for `shelving_unit_with_folding_shelves` |
| source_index_policy | only adopted module sources are indexed below |

Source records (in `data/records/`):

- `rec_picturex_0611__shelving_unit_with_folding_shelves__001__png_e8b60115b93a454ea62704ad6bb82fd3` (origin: slotted-standard wall-mounted 2-tier folding shelf; per-side scissor-style hinged support arms)
- `rec_picturex_0611__shelving_unit_with_folding_shelves__002__png_dfef7f1783ab4ab1a8ac720fe4d09aed` (origin: white powdercoat 2-tier folding shelf; signal-red side struts with mimic-coupled fold)
- `rec_0611_shelving_unit_with_folding_she_var_tier_count_1` (N=1 shelf tier)
- `rec_0611_shelving_unit_with_folding_she_var_tier_count_3` (N=3 shelf tiers)
- `rec_0611_shelving_unit_with_folding_she_var_tier_count_4` (N=4 shelf tiers)
- `rec_0611_shelving_unit_with_folding_she_var_column_height_tall` (⑤ tall column drives TIER_COUNT derived from RAIL_HEIGHT)
- `rec_0611_shelving_unit_with_folding_she_var_fold_motion_drop_down` (② drop-down fold semantics)
- `rec_0611_shelving_unit_with_folding_she_var_fold_motion_fold_up` (② fold-up fold semantics)
- `rec_0611_shelving_unit_with_folding_she_var_fold_motion_concertina` (② concertina fold semantics)
- `rec_0611_shelving_unit_with_folding_she_var_support_scissor_bracket` (② scissor-bracket support arm)
- `rec_0611_shelving_unit_with_folding_she_var_support_articulated_stay` (② articulated stay support arm)
- `rec_0611_shelving_unit_with_folding_she_var_support_chain_stay` (② chain-stay support arm)

## 核心身份

**Physical meaning.** A wall-anchored upright frame (slotted standards + cross rails) that carries N horizontal shelves attached by REVOLUTE hinges at the rear edge; each shelf can fold up flat against the wall via a rear-x-axis hinge. Each folding shelf is additionally supported by a pair of side folding brace arms hinged to the frame — the arms are independent REVOLUTE joints that swing up under the shelf in the deployed pose.

**Must keep.** Wall frame is the fixed root; every non-fixed joint is REVOLUTE about the x-axis (front-back fold); shelf hinges are located at the rear-shelf plane; each shelf has ≥ 1 dedicated support-arm joint pair; the deployed pose is horizontal with the shelf board projecting forward (+y) and the support arms bearing on the shelf underside.

**Must not become.** Fixed cabinet (fully enclosed sides + doors), decorative wall panel (no articulated shelves), plain floating single wall shelf without a fold hinge, drawer chest.

## 槽位 + 候选模块表

### Slot A — `frame_form` (③ Primary Form Family; ① upright skeleton)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `slotted_standards` | forked_anchor | `rec_picturex_..._001_...` (origin 1) + `rec_0611_..._var_column_height_tall` | origin1 L96-L155 | eligible | Two narrow slotted channel standards + rear cross rails between them; short depth (near-flat against wall). `form_subtype = Planar Boundary Form` (flat frontal rail plane). |
| `panel_wall_frame` | forked_anchor | `rec_picturex_..._002_...` (origin 2) | origin2 L36-L67 | eligible | Wider box-section wall frame with cross ties + integrated hinge leaves at each level; reads as a shallow wall-mounted panel. `form_subtype = Macro Surface Construction` (paneled wall plate). |
| `boxed_bracket_frame` | world_knowledge_extrapolation | anchors: origin1, origin2 + reviewer | derived from origin1/2 frame layout | eligible | Twin square posts joined by a deeper rear box (both cross rails offset to +y); reads as an add-on wall-mount bracket. `form_subtype = Volumetric Envelope Form`. |

### Slot B — `fold_motion` (② hinge semantics for the shelf)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `drop_down` | forked_anchor | `rec_0611_..._var_fold_motion_drop_down` | model.py articulation region ~L200-260 | eligible | Shelf hinges at rear; rest pose horizontal, upper pose swings downward against the wall. Axis (1,0,0), MotionLimits(lower=0, upper≈1.5). |
| `fold_up` | forked_anchor | `rec_0611_..._var_fold_motion_fold_up` + origin1 | origin1 L257-L274 | eligible | Shelf hinges at rear; rest pose horizontal, upper pose swings upward against the wall (canonical). Axis (1,0,0), MotionLimits(lower=0, upper≈1.5). |
| `concertina` | forked_anchor | `rec_0611_..._var_fold_motion_concertina` + origin2 | origin2 L203-L217 | eligible | Coupled fold — each shelf hinge upper-pose folds toward the wall while its arms mimic-couple; produces an accordion collapse when multiple tiers fold together. Axis (1,0,0), MotionLimits(lower=0, upper≈1.5). |

### Slot C — `support_style` (② support-arm bracket geometry)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `scissor_bracket` | forked_anchor | `rec_0611_..._var_support_scissor_bracket` + origin1 | origin1 L281-L331 | eligible | Diagonal steel strut cylinder from rear pivot up to shelf-underside pad; classic scissor arm. |
| `articulated_stay` | forked_anchor | `rec_0611_..._var_support_articulated_stay` + origin2 | origin2 L104-L137 | eligible | Bent flat web + inward flange + pivot boss reading as a stamped articulated stay bracket. |
| `chain_stay` | forked_anchor | `rec_0611_..._var_support_chain_stay` | model.py L305-L440 | eligible | Shorter thin box strut + auxiliary short pad; reads as a chain-stay style short brace. |

### Slot D — `tier_count` (multiplicity axis, ① same-part × N)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `count_1` | forked_anchor | `rec_0611_..._var_tier_count_1` | model.py L200-L260 | eligible | 1 folding shelf tier. |
| `count_2` | forked_anchor | origin1 + origin2 | origin1 L214-L275 | eligible | 2 folding shelf tiers (canonical). |
| `count_3` | forked_anchor | `rec_0611_..._var_tier_count_3` | model.py L200-L260 | eligible | 3 folding shelf tiers. |
| `count_4` | forked_anchor | `rec_0611_..._var_tier_count_4` | model.py L200-L280 | eligible | 4 folding shelf tiers. |

### Slot E — `palette_style` (⑥ material palette; source-backed + realistic companions)

| module_name | source_type | source evidence | 结构特征 |
|---|---|---|---|
| `galvanized_gray` | forked_anchor | origin1 materials (`galvanized_steel`, `powder_coated_edge`, `light_gray_shelf`, `zinc_fastener`) | Canonical galvanized frame + light gray shelf + zinc hardware. |
| `white_signal_red` | forked_anchor | origin2 materials (`white_powdercoat`, `light_shelf`, `galvanized_edge`, `signal_red`, `dark_fastener`) | White powder-coat frame + light shelf + signal-red arms. |
| `black_steel_oak` | record_only + world_knowledge_extrapolation | anchors: origin1 + reviewer | Matte-black frame, warm oak shelves, brushed brass hardware. |
| `industrial_raw` | record_only + world_knowledge_extrapolation | anchors: origin1 | All-metal industrial: raw steel frame, dark charcoal shelves, black fasteners. |

## 槽位图（slot graph）

pattern: `mixed` — `frame_form` (fixed root) with `parallel_children` shelves + per-shelf arm pairs; `tier_count` is a `multiplicity` axis. Every non-fixed joint is REVOLUTE around the +x axis.

```
frame_form (fixed root, wall_frame)
   ├──[REVOLUTE x, MatingContract shelf_hinge_leaf→frame_hinge_leaf]──> shelf_{i}   (i∈[0,N))
   └──[REVOLUTE x, MatingContract arm_pivot_boss→frame_arm_ear]──> arm_{i}_{side}   (i∈[0,N), side∈{0,1})
```

- The wall_frame is the fixed root; every non-fixed joint has `parent = wall_frame`.
- Shelf joints: axis `(1,0,0)`, `MotionLimits(lower=0, upper≈1.5, effort=45, velocity=1.1)`. Rest at q=0 = horizontal open pose; q=upper = folded (either up or down depending on `fold_motion`).
- Arm joints: axis `(1,0,0)`, `MotionLimits(lower=0, upper≈1.5, effort=18, velocity=1.5)`. Rest at q=0 = deployed under shelf.
- `fold_motion` is a semantic label on the shelf-hinge meta (all three are REVOLUTE x); axis and limits are identical. Slot B selects the meta label + coupling (concertina adds Mimic coupling of arms to shelf).

## 每槽位 Module Emits / Interfaces

### Slot A / `frame_form`
| emits | 描述 | 来源 |
|---|---|---|
| parts | Single `wall_frame` part with many `Box`/`Cylinder` visuals (standards / cross-rails / hinge cheeks / arm ears). | origin1 L86-L156 |
| internal joints | none. | — |
| upstream interface | Grounded via lowest visual `z ≈ 0`; `wall_frame` is the fixed root. | origin1 L98-L108 |
| downstream interface | Rear hinge-leaf pads at each shelf level expose the shelf-hinge mounting face; side arm-ear pads expose the arm-pivot mounting face. Named `frame_hinge_leaf_{i}`, `frame_arm_ear_{i}_{side}`. | origin2 L48-L63 |

### Slot B / `fold_motion`
| emits | 描述 | 来源 |
|---|---|---|
| parts | No new parts; sets meta label on shelf hinge and (for concertina) enables Mimic coupling of arm hinges to shelf hinge. | origin2 L203-L244 |
| internal joints | none new. | — |
| upstream/downstream | none. | — |

### Slot C / `support_style`
| emits | 描述 | 来源 |
|---|---|---|
| parts | Per arm part: pivot boss (Box), diagonal strut (Box), support pad (Box); style-dependent shape. | origin1 L286-L309 |
| internal joints | none inside arm. | — |
| upstream interface | Pivot boss (`negative_z` face) mates to `frame_arm_ear_{i}_{side}` (`positive_z` face). | origin1 L311-L330 |
| downstream interface | Support pad top face at arm end reads as bearing against shelf-underside in the deployed pose. | origin1 L304-L309 |

### Slot D / `tier_count`
| emits | 描述 | 来源 |
|---|---|---|
| parts | N shelf parts `shelf_{i}` and 2N arm parts `arm_{i}_0`, `arm_{i}_1`. | origin1 L214-L275, L281-L331 |
| internal joints | N shelf hinges `frame_to_shelf_{i}` + 2N arm hinges `frame_to_arm_{i}_{side}`. | origin1 L257-L274 |
| upstream interface | Shelf hinge origin at `(0, hinge_y, level_i)`. | origin1 L262 |
| downstream interface | Shelf board slab projects toward +y with front edge. | origin1 L223-L239 |

### Slot E / `palette_style`
| emits | Materials (`frame_metal`, `shelf_wood`, `edge_metal`, `arm_metal`, `fastener_metal`) registered on the model; every visual sets `material=mats[...]`. |
| upstream interface | none (naming policy). |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | `slotted_standards` / `panel_wall_frame` / `boxed_bracket_frame` | `slotted_standards` | choice | procedural sampler | slot A |
| `fold_motion` | enum | `drop_down` / `fold_up` / `concertina` | `fold_up` | choice | procedural sampler | slot B |
| `support_style` | enum | `scissor_bracket` / `articulated_stay` / `chain_stay` | `scissor_bracket` | choice | procedural sampler | slot C |
| `tier_count` | int | {1, 2, 3, 4} | 2 | independent | integer sampling, clamp `[1,4]` | slot D |
| `palette_style` | enum | `galvanized_gray` / `white_signal_red` / `black_steel_oak` / `industrial_raw` | `galvanized_gray` | choice | procedural sampler | slot E |
| `frame_width` | float | [0.55, 1.00] m | 0.72 | independent | clamp | origin1 L20,L37 |
| `column_height` | float | [0.75, 1.60] m | 0.96 | independent | clamp; drives `TIER_COUNT` upper bound | column_height variant |
| `shelf_depth` | float | [0.24, 0.40] m | 0.32 | independent | clamp | origin1 L21 |
| `fold_travel` | float | [1.20, 1.55] rad | 1.48 | independent | clamp | origin1 L266 |
| (—) | constraint | — | — | inequality | `tier_count · level_step + level_start + top_margin ≤ column_height`; else clamp tier_count | column_height variant L52 |
| (—) | constraint | — | — | inequality | shelf hinge origin.z within `[level_start, column_height − top_margin]` | frame layout |

### 7.5 编译预算

**Budget: 25 s per seed.** Justification: dozens of `Box`/`Cylinder` visuals on a single frame + N shelves + 2N arm parts (each ~5 visuals). Pure primitives, no boolean operations (frame meshes from source seeds are replaced with layered Boxes in the modular template). Comparable to `shelving_unit_with_adjustable_shelves` (~15 s).

## Multiplicity / Copy Logic

- **tier_count** (main axis)
  - `count_param`: `tier_count`
  - `N_range`: `[1, 4]`; sampling weighted toward 2-3
  - copied object: shelf part with hinge visuals + a pair of arm parts
  - naming: `shelf_{i}`, joint `frame_to_shelf_{i}`; `arm_{i}_0`, `arm_{i}_1`, joints `frame_to_arm_{i}_0`, `frame_to_arm_{i}_1`
  - placement: shelf `level_i = LEVEL_START + i · LEVEL_STEP`; support arms hinged at `(± ARM_X, hinge_y, level_i)`
  - joint policy: identical REVOLUTE x-axis for every shelf; identical REVOLUTE x-axis for every arm
  - source/gating: `column_height` drives max tier_count; `tier_count = min(config.tier_count, floor((column_height − level_start − top_margin)/level_step) + 1)`

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 详情 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `tier_count` and `frame_form` add/remove non-fixed edges; source_type=forked_anchor. |
| └ multiplicity | 同构件 ×N | 有 | See §Multiplicity (tier_count 1-4). |
| ② 关节类型 | 图不变,某条边换 type/轴 | 有 | Shelf hinge: REVOLUTE (1,0,0) with meta label from `fold_motion` (`drop_down`/`fold_up`/`concertina`); concertina additionally adds Mimic coupling of arm hinges. Arm pivot: REVOLUTE (1,0,0). Support geometry from `support_style`. source_type=forked_anchor. Sweep asserts REVOLUTE + `fold_motion` label variation. |
| ③ 主体形态家族 | 图&关节不变,换核心 part 的可识别几何形态原型 | 有 | `frame_form` slot: 3 candidates, each labelled `form_subtype` (Planar Boundary / Macro Surface Construction / Volumetric Envelope), source-backed / (extrapolated) and registered in `slot_choices`. |
| ④ 表面装饰 | 原型不变,叠加表面细节 | 有 | Frame slot mouths, rail screws, front fascia, mounting ears — all authored as parent visuals on frame/shelf (record_only). No independent decoration parts. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `frame_width`, `column_height`, `shelf_depth`, `fold_travel`. Shelf hinge envelope: axis (1,0,0), [0, upper∈[1.20, 1.55]]; arm hinge envelope: axis (1,0,0), [0, upper∈[1.20, 1.55]]. `motion_test_plan`: `ctx.pose({shelf_hinge: upper})` — check shelf front rotates upward (rest_z(front) < raised_z(front)) or downward per `fold_motion`; `ctx.pose({arm_hinge: upper})` — check arm swings upward. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 4 palette styles covering (a) galvanized+gray shelf, (b) white powdercoat+signal red arms, (c) black steel+oak, (d) industrial raw. Material categories: `metal` (galvanized/painted/raw), `wood` (oak — only in `black_steel_oak`), `painted` (white powdercoat, signal red). Coverage ≥ 2 material categories per palette across sweep. |

## 采样与覆盖审计

总组合数：`frame_form × fold_motion × support_style × tier_count × palette` = 3 × 3 × 3 × 4 × 4 = **432**; plus 4 continuous scales — sufficient to saturate a 40-seed sweep.

seed_domain_policy: `procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses `random.Random(seed)` to independently sample each enum slot from its candidate tuple, sample `tier_count` uniformly in `[1,4]`, sample continuous scales in their ranges, and clamp. `seed=0` reproduces canonical galvanized_gray + slotted_standards + fold_up + scissor_bracket + tier_count=2.
Topology target: 40-seed sweep exhausts frame_form × fold_motion × support_style combinations with ≥ 1 replica each; 1000-seed run reserved for maturity audit (report only).
Regression overrides: none at P0.
Controlled local parameterization: `frame_width`, `column_height`, `shelf_depth`, `fold_travel`. All clamped in `resolve_config` under §7 constraints and validated against tier_count vs column_height inequality before the builder runs.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 5 enum slots + 4 continuous scales, no compatibility gate | `slot_choices_for_seed` matches build choices |
| compatibility matrix | none required (all frames accept all fold motions, supports and tier counts within column bound) | no floating shelf, no arm intersection at rest |
| controlled local variation | frame/shelf/travel scales, clamped | proportions vary without breaking hinges |
| regression overrides | none | — |
| random sweep | seeds 0-39 first pass, 0-999 maturity | axis realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 3 | yes | yes | |
| fold_motion | 3 | yes | yes | meta label + optional Mimic |
| support_style | 3 | yes | yes | |
| tier_count | 4 | yes | yes | multiplicity |
| palette_style | 4 | yes | yes | |

## Validator

- `slot_choices_for_seed(seed)` returns the same 5-tuple that `build_shelving_unit_with_folding_shelves(config_from_seed(seed))` actually realizes.
- `config_from_seed` uses deterministic procedural sampling; `seed=0` returns canonical anchor config.
- `resolve_config` clamps every continuous scale and enforces `tier_count ≤ derived_max` before returning.
- `wall_frame` part exists and is the unique root.
- Exactly `tier_count` REVOLUTE x-axis shelf joints exist, all parented to `wall_frame`; each has `MotionLimits(lower=0, upper ∈ [1.20, 1.55])`.
- Exactly `2 · tier_count` REVOLUTE x-axis arm joints exist, all parented to `wall_frame`; each has `MotionLimits(lower=0, upper ∈ [1.20, 1.55])`.
- Every non-fixed joint declares a `MatingContract` (shelf hinge leaf→frame hinge leaf; arm pivot boss→frame arm ear).
- Palette materials cover ≥ 2 material categories on average across the sweep.
- `ctx.pose({shelf_hinge: upper})` — shelf board world position rotates such that its front edge rises (fold_up) / drops (drop_down) / rotates upward with mimic (concertina) — front-edge z-shift ≥ 0.10 in the folded pose.
- `ctx.pose({arm_hinge: upper})` — arm support-pad world z rises by ≥ 0.05.

## Reject cases

- Shelf hinge axis not `(1,0,0)` → wrong fold semantics.
- Shelf `parent != "wall_frame"` (e.g., shelf mounted on another shelf) → violates category identity.
- Missing `MatingContract` on any non-fixed joint → violates B/§B contract.
- Frame is not a single unique root part.
- No REVOLUTE joint at all → not a folding shelf.
- `tier_count · level_step` overruns column_height → tier overrun.
- Origin far from geometry (`fail_if_articulation_origin_far_from_geometry` > 0.02).

## 与相邻类别的边界

- 不该混入：Plain cabinet — this category is open; no full enclosure + door.
- 不该混入：Decorative wall panel — must have at least one articulated shelf.
- 不该混入：Fixed floating wall shelf — this unit's defining feature is the fold hinge.
- 不该混入：Shelving unit with adjustable shelves — that uses PRISMATIC z-axis; here every non-fixed joint is REVOLUTE x-axis.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Initial modular spec derived from 2 origin picture seeds + 10 forked variants. |
