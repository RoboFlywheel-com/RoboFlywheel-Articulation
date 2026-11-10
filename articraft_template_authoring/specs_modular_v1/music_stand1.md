# music_stand1 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `music_stand1` |
| template path | `agent/templates/music_stand1.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `linear_chain` (base → column → desk) with per-slot internal joints |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 (3 origins + 7 forked variants) |
| read_count | 10 (origins read fully; variants inspected via slot-map + spot check) |
| read_scope | all 5-star `rec_0611_music_stand1*` + `rec_picturex_0611__music_stand1__*` synced under `data/records/` |
| source_index_policy | only adopted module sources indexed below |

Sources (arti-template/data/records/<id>/revisions/rev_000001/model.py):
- S1 = `rec_picturex_0611__music_stand1__001__png_d2462452f2844af9b48bfde226a5fd22` (weighted round pedestal, 2-stage telescoping, walnut solid tray, dual lock knobs, desk tilt).
- S2 = `rec_picturex_0611__music_stand1__002__png_f0e5c91b55d54a39aa056cc73ac35fe7` (folding tripod, single-stage telescoping, open wire-frame rest).
- S3 = `rec_picturex_0611__music_stand1__003__png_bea9d2286d784399bf2ecfe83ba56fa2` (folding tripod, 2-stage telescoping, perforated steel desk).
- V1 = `rec_0611_music_stand1_var_base_folding_tripod` — folding tripod variant off S1 skeleton.
- V2 = `rec_0611_music_stand1_var_base_round_weighted_base` — round base variant off S3.
- V3 = `rec_0611_music_stand1_var_desk_form_solid_tray` — solid tray variant off S1.
- V4 = `rec_0611_music_stand1_var_desk_form_split_folding_leaves` — split folding leaves off S2.
- V5 = `rec_0611_music_stand1_var_height_stages_single_stage` — collapses to a single prismatic.
- V6 = `rec_0611_music_stand1_var_height_stages_three_stages` — three telescoping prismatics.
- V7 = `rec_0611_music_stand1_var_retention_pivoting_page_clips` — page clips (④ decoration axis).

## 核心身份

An adjustable **sheet-music stand**: a small, grounded base, a vertical **telescoping column** (1–3 prismatic stages, each with a lock knob), a **music rest / desk** that supports sheet music with a shelf lip on the front, and a **rest tilt** revolute joint pointing the desk toward the reader. Rests below shoulder height (0.7–1.5 m). Not a lectern (no cabinet or podium volume), not a microphone/light stand (defining use is music, not mic/light mounting), not a keyboard stand (no keyboard tray).

## 槽位 + 候选模块表

### Slot A: `base_form` (①)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `round_pedestal` | forked_anchor | S1 | L86-147 | eligible if compatible | axisymmetric lathed shallow-dome disk with rubber foot + post socket; single root part `base` with no leg joints. |
| `folding_tripod` | forked_anchor | S2, S3, V1 | S2 L88-217 / S3 L146-260 / V1 L100-215 | eligible if compatible | tripod hub + three independently REVOLUTE `tripod_leg_{i}` parts with rubber feet; 3 clevis-cheek pairs on hub. |
| `weighted_wide_disk` | forked_anchor | V2 | L80-160 | eligible if compatible | wide round weighted disk footprint (larger than S1's round), no legs; visible ribbed sole and short post socket. |

### Slot B: `desk_form` (③ Primary Form Family — form-dominated)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `solid_tray` | forked_anchor | S1, V3 | S1 L50-64, L347-398 | eligible if compatible | Planar Boundary Form — rounded rectangular solid plate with two slots; walnut/wood or metal. |
| `perforated_panel` | forked_anchor | S3 | L48-110, L410-478 | eligible if compatible | Macro Surface Construction — thin steel plate perforated with rows of elongated slots. |
| `wire_frame` | forked_anchor | S2 | L279-362 | eligible if compatible | Macro Surface Construction — open beam frame: upper/lower/side rails + horizontal rails + center spine (no fill). |
| `split_folding_leaves` | forked_anchor | V4 | L280-460 | eligible if compatible | Volumetric Envelope Form — two mirrored half-panels meeting at center; each half is a rounded rectangle. |

### Slot C: `height_stages` (multiplicity, ①)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `n1` (single stage) | forked_anchor | V5 | L100-240 | eligible if compatible | 1 PRISMATIC column: `base` → `column` (with rest attached). |
| `n2` (two stages) | forked_anchor | S1, S3 | S1 L151-258 | eligible if compatible | 2 PRISMATIC stages: `base` → `mid_post` → `upper_post`. |
| `n3` (three stages) | forked_anchor | V6 | L120-350 | eligible if compatible | 3 PRISMATIC stages: `base` → `stage1` → `stage2` → `upper_post`. |

### Slot D: `palette_style` (⑥)

| module_name | source_type | source evidence | 结构特征 |
|---|---|---|---|
| `matte_black_walnut` | record_only | S1 | walnut desk + matte black column, warm upper post. |
| `all_black_steel` | record_only | S2, S3 | powder-coat black metal throughout, rubber feet. |
| `dark_hardware_wood` | record_only | S1, V3 | dark hardware + wood-toned desk. |
| `industrial_gray` | world_knowledge_extrapolation | reviewer | matte gray column, dark gray desk, black hardware — realistic music-stand production finish. |

## 槽位图（slot graph）

pattern: `linear_chain` with fixed-slot decorations.

```
[base_form: base part(s)] --[height_stages: N × PRISMATIC (Z axis), MatingContract stem-in-tube]--> [column final stage]
                                              └── per-stage lock knob (REVOLUTE about Y, on parent stage)
[column final stage] --[REVOLUTE about X, MatingContract tilt_barrel/tilt_cheek]--> [desk_form: desk]
```

- Base parents the whole chain; each height stage adds one PRISMATIC child of the previous stage (axis (0,0,1)).
- Each height stage has an accompanying lock-knob part (REVOLUTE about Y, parent = the stage BELOW the one it locks, decorative rotary).
- `desk_form` is the terminal child of the top column stage via a REVOLUTE about X for tilt.
- `folding_tripod` base_form adds 3 REVOLUTE leg parts children of the base hub.

## 每槽位 Module Emits / Interfaces

### Slot A / `round_pedestal`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` | S1 L86-147 |
| internal joints | (none) | — |
| upstream interface | ground plane at z=0 | S1 |
| downstream interface | `outer_tube` top rim at z=0.620, axis +Z | S1 L118-133 |

### Slot A / `folding_tripod`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (hub + column stub), `tripod_leg_0..2` | S2 L88-217, S3 L146-260 |
| internal joints | `leg_hinge_0..2` REVOLUTE, axis local Y, range ~[-0.6, 0.2] | S2 L199-217 |
| upstream interface | ground plane | S2 |
| downstream interface | column base rim at z ≈ 0.5 | S2 L128-145 |

### Slot A / `weighted_wide_disk`
Same as `round_pedestal` but wider disc; V2.

### Slot C / `n1..n3` (height stages)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mid_post`, `stage2` (n3), `upper_post` — one per stage | S1 L151-243 |
| internal joints | `height_lower`, `height_upper`, ... PRISMATIC axis +Z, range [0, 0.18] each | S1 L183-258 |
| upstream interface | outer_tube of parent | — |
| downstream interface | topmost stage tube tip | — |

Each stage has a lock knob: `lock_knob_k` REVOLUTE about Y on the parent stage (S1 L261-345).

### Slot B / desks
| emits | 描述 | 来源 |
|---|---|---|
| parts | `desk` | S1 L347-398 |
| internal joints | (none in desk) | — |
| upstream interface | tilt hinge on rear of desk (`hinge_barrel` axis +X) | S1 L382-393 |
| downstream interface | (terminal) | — |

Chained to top column stage via `desk_tilt` REVOLUTE about +X, MatingContract(tilt_barrel/tilt_cheek).

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_form` | enum | round_pedestal / folding_tripod / weighted_wide_disk | round_pedestal | choice | slot A | module table |
| `desk_form` | enum | solid_tray / perforated_panel / wire_frame / split_folding_leaves | solid_tray | choice | slot B | module table |
| `height_stages` | int | 1, 2, 3 | 2 | choice | slot C (weighted 0.30/0.45/0.25) | module table |
| `palette_style` | enum | matte_black_walnut / all_black_steel / dark_hardware_wood / industrial_gray | matte_black_walnut | choice | slot D | module table |
| `desk_width_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | S1 L51 |
| `desk_height_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | S1 L51 |
| `column_length_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp; scales each stage length | S1 L120,154 |
| `stage_travel_scale` | float | [0.85, 1.10] | 1.0 | independent | clamp; scales per-stage prismatic upper limit | S1 L192-256 |
| `base_scale` | float | [0.90, 1.15] | 1.0 | independent | clamp; scales base footprint | S1 L87-100 |
| `tilt_range` | float | [0.30, 0.50] | 0.42 | independent | desk_tilt upper limit magnitude | S1 L410-416 |
| (—) | constraint | — | — | inequality | each stage's retained overlap ≥ 0.055 m: `stage_length ≥ travel + overlap_min` — enforced by column_length_scale floor per N | S1 L521-568 |

### 7.5 编译预算 / compile budget

Target per-seed: ≤ 12s (median). No heavy CadQuery booleans other than the perforated panel (which uses ~55 rounded-slot cuts once). Small radial features ≤ 32 segments, hero surfaces ≤ 48. Wire-frame desk uses only Box primitives. Perforated panel tessellation moderate.

## Multiplicity / Copy Logic

- **Axis 1**: `height_stages_count` (slot C).
  - `count_param` = `height_stages`
  - `N_range` = [1, 3] (product domain matches observed sources; test = full range; wider only if reviewer expands).
  - Sampling weights: N=1 0.30, N=2 0.45, N=3 0.25 (S1/S3 are N=2; S2 is N=1; V6 is N=3).
  - copied object: telescoping stage `mid_post`/`stage_{i}` — shared helper.
  - naming: `stage_0` (`mid_post`), `stage_1` … `stage_{N-1}` (topmost = `upper_post`).
  - placement: colinear along Z, each shorter and thinner than the parent (radius decreases by 0.0015 per stage).
  - joint policy: PRISMATIC axis +Z, MatingContract on parent tube inner / child tube outer.
- **Axis 2**: `folding_tripod` legs — always 3 (fixed count in every source of this candidate; not exposed as a parameter).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减 part/边 | 有 | `base_form`: 3 candidates (round_pedestal / folding_tripod / weighted_wide_disk), forked_anchor S1/S2/S3/V1/V2. `folding_tripod` adds 3 leg parts and 3 leg-hinge joints. |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: `height_stages` N∈{1,2,3}, forked_anchor S1/S2/S3/V5/V6. |
| ② 关节类型 | 图不变,换 type/轴 | 有 | PRISMATIC (height_stages, +Z), REVOLUTE (desk_tilt +X, lock_knobs +Y, leg_hinges +Y). Each type is realized in-sweep. Source: S1/S2/S3. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 形态原型 | 有 | `desk_form`: 4 candidates. `solid_tray` = Planar Boundary Form; `perforated_panel` = Macro Surface Construction; `wire_frame` = Macro Surface Construction; `split_folding_leaves` = Volumetric Envelope Form (two mirrored volumes). Registered in `slot_choices`. |
| ④ 表面装饰 | 加叠饰 | 有 | Front sheet-shelf lip is universal on every desk (record_only, S1 L370-381); wood-grain inserts on `solid_tray` walnut; pivoting page clips (V7) available as a decoration on top desk (record_only). |
| ⑤ 尺寸/行程 | 只连续改 | 有 | `desk_width_scale [0.85,1.15]`, `desk_height_scale [0.85,1.15]`, `column_length_scale [0.85,1.15]`, `stage_travel_scale [0.85,1.10]`, `base_scale [0.90,1.15]`, `tilt_range [0.30, 0.50]`. Motion tests: each PRISMATIC stage swept through [0, upper] & retention overlap verified; `desk_tilt` swept through ±tilt_range. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 4 palettes (matte_black_walnut, all_black_steel, dark_hardware_wood, industrial_gray). Material categories: painted metal + wood + rubber + steel; covers ≥ ceil(0.5×4)=2 metal categories. |

## 采样与覆盖审计

总组合数：base_form(3) × desk_form(4) × height_stages(3) × palette(4) = 144
（compatibility gating below removes ~0 due to no strict exclusions; all combos legal.）

理由：linear chain lets any desk sit on any column; the desk hinge is topology-invariant across desk_form.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses a stable `random.Random(seed)` to independently sample each slot (weighted for `height_stages`), then samples the continuous scale params uniformly and clamps. No compatibility gating is required — the chain assembly is homogeneous. Regression overrides: none. Random sweep: seeds 0-35 initial; corner stage from pipeline for extremes. Viewer inspection: seeds 0-9.

Controlled local parameterization: `desk_width_scale`, `desk_height_scale`, `column_length_scale`, `stage_travel_scale`, `base_scale`, `tilt_range` (all `independent`); `stage_travel_scale` interacts with `column_length_scale` via inequality (retention overlap ≥ 0.055 m), resolved in `resolve_config`.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot A, B, C independent weighted, palette D independent | slot_choices_for_seed matches build choices |
| compatibility matrix | all legal; retention overlap enforced by scale clamp | no floating, no closed-pose overlap |
| controlled local variation | continuous scales clamped in resolve_config | proportions vary; joint travel preserved |
| regression overrides | none | — |
| random sweep | 0-35 initial + corner | axis_realization; viewer 0-9 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_form | 3 | yes | yes | |
| desk_form | 4 | yes | yes | ③ primary form family |
| height_stages | 3 | yes | yes | multiplicity axis |
| palette_style | 4 | yes | yes | |

## Validator

- `slot_choices_for_seed(seed)` returns exactly the 4-tuple of implemented module names for every seed.
- `config_from_seed` uses `random.Random(seed)` (deterministic procedural).
- All continuous scales clamped in `resolve_config`; retention-overlap inequality resolved before builder.
- Every non-FIXED joint declares a `MatingContract` to real visuals on both sides (see `_emit_stage`, `_emit_desk_tilt`, `_emit_lock_knob`, `_emit_leg_hinge`).
- Sampled PRISMATIC / REVOLUTE overlap gates pass via element-scoped `ctx.allow_overlap` for captured stems and hinge pins.
- Key joints: `height_stage_{i}` (PRISMATIC +Z), `desk_tilt` (REVOLUTE +X), `lock_knob_turn_{i}` (REVOLUTE ±Y), `leg_hinge_{i}` (REVOLUTE local Y).
- Copied stage parts follow `stage_{i}` naming and colinear placement.

## Reject cases

- Desk floating above the top column stage (missing tilt hinge barrel welded to desk).
- Column stage escaping its parent tube at full travel (retention overlap < 0.05 m).
- Lock knob knob-only, no visible stem — instant island fail.
- Tripod leg foot embedded in the ground below z=0 — closed-pose overlap.
- Desk perforations that break the outer boundary (perforation cutter outside the panel) — mesh assets invalid.
- Split folding leaves that gap or overlap at the center parting line beyond `contact_tol`.

## 与相邻类别的边界

- 不该混入 `lectern`: no cabinet/podium volume; base footprint stays small (< 0.4 m); no reading-panel bulk.
- 不该混入 `microphone_stand` / `light_stand`: the terminal payload is a **desk / rest** with a sheet-shelf lip, not a mic clip or lamp head.
- 不该混入 `keyboard_stand`: no wide flat X-frame; desk is a small vertical rest not a horizontal keyboard tray.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | first pass; sweep gates via pipeline. |

## 模板实现备注

- Shared helpers: `_stage_tube(radius, z0, z1)` (annular lathe tube), `_lock_knob(part, ...)`.
- MatingContract on `height_stage_{i}` uses parent tube visual `stage_{i}_tube` positive_z rim with child `stage_{i+1}_tube` negative_z base.
- Element-scoped `ctx.allow_overlap`: (child stage tube ↔ parent stage tube) for the captured telescoping fit; (lock stem ↔ collar) captured hardware; (leg hinge_barrel ↔ leg bracket cheeks) captured hinge; (tilt_pin ↔ hinge_barrel) captured desk hinge.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | round_pedestal / solid_tray / n2 | 001 origin | full file | topology + tests skeleton |
| S2 | A/B/C | folding_tripod / wire_frame / n1 | 002 origin | full file | tripod hub + wire frame |
| S3 | A/B/C | folding_tripod / perforated_panel / n2 | 003 origin | full file | perforated panel + tripod hub |
| V1 | A | folding_tripod | var_base_folding_tripod | leg hub + legs | folding tripod cross-reference |
| V2 | A | weighted_wide_disk | var_base_round_weighted_base | full file | wide-disk base geometry |
| V3 | B | solid_tray | var_desk_form_solid_tray | desk part | tray plate variant |
| V4 | B | split_folding_leaves | var_desk_form_split_folding_leaves | desk parts | split-leaves topology |
| V5 | C | n1 | var_height_stages_single_stage | column | single-stage collapse |
| V6 | C | n3 | var_height_stages_three_stages | column stack | 3-stage stack |
| V7 | ④ | decoration | var_retention_pivoting_page_clips | desk clips | page-clip decoration source |
