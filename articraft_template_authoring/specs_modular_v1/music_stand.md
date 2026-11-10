# Music Stand — Modular Spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `music_stand` |
| template path | `agent/templates/music_stand.py` |
| test path (optional) | `tests/agent/test_music_stand_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear chain base→shaft→desk + parallel_children page retention on desk + multiplicity for height stages) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 (orchestra_style_music_stand) + 3 (picturex origin) + 12 (0611 fork variants) |
| read_count | 6 (3 origin + 3 spot-checked fork variants) |
| read_scope | 3 declared origin anchors (music_stand__001/002/003) plus scans of fork records for base/desk/page_retention topologies |
| source_index_policy | only adopted module sources are indexed below; declared 5★ forks in template_source_map used as authority |

## 核心身份

An adjustable **music stand** that supports sheet music. The defining structure
is a **grounded base**, a **vertical support column** (typically telescoping),
and a **desk / tray** whose plane holds the sheet music. The desk tilts on a
horizontal head hinge; the column height adjusts by a prismatic slide.
Optional page retainers (clips / swing arms) sit on the desk.

Excluded neighbors: lectern (podium body, no tilt desk), microphone stand
(no sheet-music desk), music-stand clip-on lamp (arm+shade instead of desk).

## 槽位 + 候选模块表

### Slot A：base (③ Primary Form Family — base topology)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `folding_tripod` | forked_anchor | `rec_picturex_0611__music_stand__003__png_...` (canonical) + `rec_0611_music_stand_var_base_folding_tripod` | 003 model L119-L253 | eligible if compatible | tripod hub cylinder + 3 REVOLUTE leg tubes + 3 REVOLUTE brace tubes; feet as spheres; form_subtype=Macro Surface Construction (3-legged tripod). |
| `four_leg_base` | forked_anchor | `rec_0611_music_stand_var_base_four_leg_base` from 003 | inherited hub + 4 leg pattern | eligible if compatible | central hub + 4 fixed leg tubes with feet (no fold hinges — legs FIXED, no articulation on legs); form_subtype=Volumetric Envelope Form (X-legged base). |
| `weighted_round_base` | world_knowledge_extrapolation (③) | anchors: `rec_orchestra_style_music_stand_e67000880da442f98994279a5e2fbb20` (weighted round base), `rec_0611_music_stand1_var_base_round_weighted_base` + reviewer | analogous to hub disk in 003 L120-L133 | eligible if compatible | short thick disc (planar boundary form) + rubber foot rim; no leg parts; form_subtype=Planar Boundary Form (round disc). |

Notes: three ③ candidates; each realizes a genuinely different base topology
(3-part fold vs 4 fixed legs vs monolithic disc).

### Slot B：desk_form (③ Primary Form Family — desk shape)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `perforated_panel` | forked_anchor | `rec_0611_music_stand_var_desk_form_perforated_panel` from 003 | 003 L323-L353 | eligible if compatible | wide rectangular ribbed tray (dense crossed ribs), lower retaining lip; form_subtype=Planar Boundary Form (rectangle). |
| `wire_frame` | forked_anchor | `rec_0611_music_stand_var_desk_form_wire_frame` from 001 | wire-frame variant | eligible if compatible | rectangular outer frame with 2 horizontal cross-rails (bookshelf-style open frame); form_subtype=Macro Surface Construction. |
| `solid_tray` | forked_anchor | `rec_0611_music_stand1_var_desk_form_solid_tray` | solid_tray variant | eligible if compatible | solid rectangular panel + tall retaining lip along bottom edge; form_subtype=Volumetric Envelope Form (thick slab). |

### Slot C：height_stages (multiplicity axis — telescoping segments)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_stage` | forked_anchor | `rec_0611_music_stand1_var_height_stages_single_stage` | inherited single-tube shaft | eligible if compatible | outer sleeve + one inner shaft; one PRISMATIC joint (shaft_slide). |
| `three_stage` | forked_anchor | `rec_0611_music_stand_var_height_stages_three_stages` from 001 | three_stage variant | eligible if compatible | outer sleeve + mid stage + inner shaft; two PRISMATIC joints (mid_slide + inner_slide). |

Note: only 2 candidates (source pool has these two structurally distinct N
values). Additional stages get folded into `three_stage` (N=3 encoded).

### Slot D：page_retention (② joint / parallel children)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | 001/002/003 origins default (no retention clips) | 003 (no clip parts) | eligible if compatible | no additional parts / joints on desk. |
| `paired_clips` | forked_anchor | `rec_0611_music_stand_var_page_retention_paired_clips` from 001 | clip_arm variant | eligible if compatible | 2 REVOLUTE clip parts (small clip arm pivoting on desk lip), symmetric about desk center. |
| `paired_swing_arms` | forked_anchor | `rec_0611_music_stand_var_page_retention_paired_swing_arms` from 001 | clip_arm variant | eligible if compatible | 2 REVOLUTE swing arm parts (longer, page-side pivot), symmetric. |

## 槽位图（slot graph）

pattern: mixed (linear_chain + multiplicity + parallel_children)

```
base --[PRISMATIC +Z, MatingContract(base.height_collar.top_face, shaft.bottom_face)]--> shaft_stage_0
       (if three_stage: shaft_stage_0 --[PRISMATIC +Z]--> shaft_stage_1)
shaft (top) --[REVOLUTE +X, MatingContract(shaft.tilt_seat, desk.pivot_face)]--> desk
desk --[REVOLUTE ±X, parallel_children]--> clip_left, clip_right   (if page_retention != none)
```

- base always contains the outer telescoping sleeve at its top.
- desk_form's underside always exposes a tilt yoke face compatible with the shaft's tilt socket.
- page_retention parts attach to desk's top face lip.

## 每槽位 Module Emits / Interfaces

### Slot A / module folding_tripod
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (hub + outer_sleeve + height_collar + 3 leg_mount + brace_collar), `leg_0..2`, `brace_0..2` (7 parts) | 003 L119-L286 |
| internal joints | 3 REVOLUTE `leg_hinge_i` + 3 REVOLUTE `brace_hinge_i` | 003 L240-L286 |
| upstream interface | (root) | — |
| downstream interface | `outer_sleeve` top face at z=height_collar_z (axis +Z, PRISMATIC consumer) | 003 L136-L151 |

### Slot A / module four_leg_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | single `base` (hub + 4 leg tubes + feet + outer_sleeve + height_collar) | 003 + 4-leg fork |
| internal joints | none (legs fused as base visuals — Rule 1 / captured) | — |
| downstream interface | same as folding_tripod | — |

### Slot A / module weighted_round_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | single `base` (weighted disc + outer_sleeve + height_collar) | orchestra 5★ + 003 collar |
| internal joints | none | — |
| downstream interface | same as folding_tripod | — |

### Slot B / module perforated_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `desk` (tray shell + underside_bridge + 2 yoke sides + 2 hinge cyls + retaining lip) | 003 L323-L353 |
| upstream interface | 2 hinge_side cylinders forming the tilt bore; consumer joint REVOLUTE about X | 003 L339-L353 |
| downstream interface | desk top face for page retention parts | 003 L323-L332 |

### Slot B / module wire_frame
| emits | parts | `desk` (rectangular outer frame + 2 horizontal cross-rails + 2 yoke sides + 2 hinge cyls) | 001 wire_frame |
| upstream interface | 2 hinge cylinders (same as perforated) | — |
| downstream interface | frame top rail for retention | — |

### Slot B / module solid_tray
| emits | parts | `desk` (solid slab + tall bottom lip + 2 yoke sides + 2 hinge cyls) | solid_tray fork |

### Slot C / module single_stage
| emits | `shaft` part; internal joint `shaft_slide` PRISMATIC +Z (parented to base) | 003 L290-L321 |
| interface | tilt_barrel at top for desk consumer | 003 L297-L310 |

### Slot C / module three_stage
| emits | `shaft`, `mid_shaft` parts; 2 PRISMATIC joints | three_stage fork |
| interface | tilt_barrel at top of shaft (topmost stage) | inherited |

### Slot D / module paired_clips
| emits | `clip_left`, `clip_right` parts; 2 REVOLUTE joints (child of desk) | 001 clip variant |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base` | enum | `folding_tripod / four_leg_base / weighted_round_base` | — | choice | procedural sampler | Slot A |
| `desk_form` | enum | `perforated_panel / wire_frame / solid_tray` | — | choice | procedural sampler | Slot B |
| `height_stages` | enum | `single_stage / three_stage` | — | choice | procedural sampler | Slot C |
| `page_retention` | enum | `none / paired_clips / paired_swing_arms` | — | choice | procedural sampler | Slot D |
| `palette_style` | enum | `graphite_black / satin_silver / polished_brass / matte_ivory` (4 palettes) | — | choice | procedural sampler | palette |
| `base_scale` | float | [0.90, 1.15] | 1.0 | independent | clamp only | 003 base_hub 0.032 |
| `column_height_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | 003 outer_sleeve 0.580 |
| `desk_width_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | 003 desk 0.560 wide |
| `desk_depth_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | 003 desk 0.360 deep |
| `tilt_range_scale` | float | [0.85, 1.10] | 1.0 | independent | clamp | 003 desk_tilt [-0.55,0.40] |
| `slide_travel_scale` | float | [0.85, 1.10] | 1.0 | independent | clamp | 003 shaft_slide 0.220 |

### 7.5 编译预算 / compile budget
Target ≤ 8 s per seed. Geometry uses only `Box`, `Cylinder`, `Sphere`
primitives (no cadquery boolean ops on the hot path), so tessellation cost is
negligible. `--compile-timeout 120` (default) is 15× budget.

### 8. Multiplicity / Copy Logic

Single multiplicity axis: `height_stages_count ∈ {1, 3}` encoded as
`single_stage` / `three_stage` module names (per §B multiplicity-in-module-name
pattern). N=1 emits 1 PRISMATIC shaft joint; N=3 emits 2 PRISMATIC joints
(mid_shaft + inner_shaft), shaft/mid always parented to base.

- count_param: implicit via `height_stages` enum
- N_range: {1, 3}; N=1 weight 0.6, N=3 weight 0.4
- copied object: `shaft_stage_i` shares same helper mesh, named `shaft_i`, all
  PRISMATIC +Z, mating declared on each collar/shaft pair.

### 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | tripod (6 hinges + 1 prismatic + 1 revolute) vs four_leg (0 leg hinges) vs weighted_round (0 leg hinges) — `page_retention=none` → 0 clip joints, `paired_clips`/`paired_swing_arms` → +2 REVOLUTE. All forked_anchor. |
| └ multiplicity | 同构件 ×N | 有 | height_stages N ∈ {1,3}, weights (0.6, 0.4); see §8. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE (desk tilt X-axis, leg fold Y-axis in local frame, clip pivot) + PRISMATIC (shaft slide Z-axis) + CONTINUOUS knob spin optional; sources 003/001/002. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的几何形态原型 | 有 | Slot A: tripod (Macro Surface Construction) / four_leg (Volumetric Envelope) / weighted_round_base (Planar Boundary). Slot B: perforated (Planar Boundary rectangle) / wire_frame (Macro Surface Construction) / solid_tray (Volumetric Envelope). All registered in `slot_choices`. |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 无 | Baseline template keeps decoration minimal (retaining lip is structural, not decoration). Palette colors carry visual differentiation. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | `base_scale [0.90,1.15]`, `column_height_scale [0.85,1.15]`, `desk_width_scale [0.85,1.15]`, `desk_depth_scale [0.85,1.15]`, `tilt_range_scale [0.85,1.10]`, `slide_travel_scale [0.85,1.10]`. Motion envelopes: shaft_slide axis Z, opens upward, [0, 0.220 * slide_travel_scale]; desk_tilt axis X, tilt-forward, [-0.55, 0.40] × tilt_range_scale; leg_hinge axis Y (folding_tripod only), [0, 1.25]; clip pivot axis X, [0, 1.0]. motion_test_plan: rely on compiler baseline `harness_motion_qc` at closed/lower/upper/mid + targeted `ctx.pose` proving shaft rises, desk tilts, clips rotate. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 4 palettes registered — `graphite_black` (dark powder + rubber), `satin_silver` (light metal), `polished_brass` (warm metal), `matte_ivory` (painted). Cover metal + painted + rubber material categories. |

### 9. 采样与覆盖审计

总组合数：3 (base) × 3 (desk_form) × 2 (height_stages) × 3 (page_retention) × 4 (palette) = 216

理由: 216 seed-choice combos ≥ modular target; 0-35 sweep will realize a broad subset of every axis.

seed_domain_policy: procedural_first

Procedural Sampling / Sweep Plan:
- `config_from_seed(seed)` uses `random.Random(seed)` to pick each slot enum
  and continuous scale independently.
- No compatibility gating needed: every combination is legal (paired_clips
  and paired_swing_arms use hinge cylinders on the desk lip, which every desk
  form exposes; single_stage/three_stage both dock into every base's height_collar).
- Random sweep: seeds 0-15 fast, 16-35 final, corner appended.
- Topology target: report-only.
- Controlled local scale params: `base_scale`, `column_height_scale`,
  `desk_width_scale`, `desk_depth_scale`, `tilt_range_scale`, `slide_travel_scale`
  — all clamped in `resolve_config`; independent.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order base→desk_form→height_stages→page_retention→palette; enum choice(uniform) | slot_choices_for_seed matches build |
| compatibility matrix | fully legal — no gates | — |
| controlled local variation | 6 scale params, clamped, independent | proportions vary; no interface break |
| regression overrides | none | — |
| random sweep | seeds 0-35 (fast+final), corner appended | verdict pass, axis realization visible |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base | 3 | yes | yes | ③ Primary Form Family; source-backed + 1 world_knowledge_extrapolation |
| desk_form | 3 | yes | yes | ③ Primary Form Family |
| height_stages | 2 | yes | no | multiplicity axis; only two source-backed N values |
| page_retention | 3 | yes | yes | none + 2 clip variants |

### 10. Validator 和 Reject cases

## Validator
- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic Random(seed) for every seed including 0
- controlled local scale params clamped in resolve_config
- every non-FIXED articulation declares a MatingContract to real visuals OR is
  a captured-pin case with element-scoped allow_overlap in run_tests
- 4 palettes registered with `model.material`; every visual carries a material
- shaft_slide PRISMATIC +Z; desk_tilt REVOLUTE X-axis
- copy tests: paired retention modules emit exactly 2 symmetric children

## Reject cases
- desk shell floats above yoke (missing underside_bridge)
- clip pivot origin >15mm from any desk visual (anchor honesty)
- shaft slides out of the sleeve at upper limit (must retain overlap ≥ 0.03)
- tripod legs collide at fully folded pose (respect lower limit 0)
- desk tilt endpoints collide with shaft (respect upper 0.40)
- palette sampled but visuals use hard-coded material — palette must flow

### 11. 与相邻类别的边界

## 与相邻类别的边界
- 不该混入：lectern（no tilting sheet-music desk on a telescoping column; lectern is a podium body）
- 不该混入：microphone stand（no wide sheet-music desk, only a mic clip/boom）
- 不该混入：music-stand clip-on lamp（arm+shade replaces the desk）

### 12. 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored inline with template; sweep-pipeline is authoritative signal. |
