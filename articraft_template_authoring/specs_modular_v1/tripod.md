# Modular Spec — tripod (0611)

## 元信息
| 项 | 值 |
|---|---|
| slug | `tripod` |
| template path | `agent/templates/tripod.py` |
| test path (optional) | `tests/agent/test_tripod_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (legs = parallel children of hub; center_column + head = chain stacked on hub top) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 origin anchors + 16 forked variant anchors (all rating 5) |
| read_count | 3 origins fully + head(fluid/gimbal) + center_column(leveling/boom) + foot variants (targeted) |
| read_scope | all 3 origin 5-star samples read in full; forked variants sampled for their delta geometry |
| source_index_policy | only adopted module sources are indexed below |

Origins:
- **S1** `rec_picturex_0611__tripod__001` — tall black camera tripod. chassis (center_sleeve + spider + brace_collar + column_clamp + crank_mount) → PRISMATIC `center_column_slide` → center_column → REVOLUTE `head_pan` → pan_base (drum + rounded body + 2 fork cheeks) → REVOLUTE `head_tilt` → tilt_head (barrel + body + plate_support + spline pan_handle) → PRISMATIC `plate_slide` → mounting_plate. REVOLUTE `column_crank_turn`. 3 legs: REVOLUTE `leg_hinge` → upper_leg → PRISMATIC `upper_to_middle` → middle_leg → PRISMATIC `middle_to_lower` → lower_leg (rubber foot); per-stage flip levers (REVOLUTE) + REVOLUTE `brace_hinge` braces. ~25 joints.
- **S2** `rec_picturex_0611__tripod__002` — compact ball-head tripod. hub (LatheGeometry shell + head_seat) → REVOLUTE `head_pan` → pan_body (lathe shell + trim rings + tilt_socket) → REVOLUTE `head_tilt` → tilt_head (Sphere tilt_ball + stem + toothed_ring + plate + pad); CONTINUOUS pan_lock, CONTINUOUS mount_screw. 3 legs: REVOLUTE `leg_hinge` → upper_leg (rounded sleeve mesh) → PRISMATIC `leg_extension` → lower_leg (loft rubber foot); REVOLUTE `clamp_hinge`.
- **S3** `rec_picturex_0611__tripod__003` — compact silver tabletop tripod, fixed threaded mount, single-section legs. hub (brushed/machined aluminum stack + thread crests + clevis ears) → REVOLUTE `hub_to_leg` × 3 → leg (aluminum tube + ferrule + rubber foot). No head articulation, no column.

Forked-variant deltas adopted: fluid_video head (cadquery swept `_fluid_head_shell` + transverse fluid cartridge), gimbal head (axle + hub disks + spline swing arm + carriage rail), geared/ball head knob detailing, leveling-bowl column (open cast bowl cap), reversible boom column (boom_pivot_housing + horizontal boom tube), retractable spikes / suction feet (foot visual family on `lower_leg`).

## 核心身份

A tripod is a **three-legged equipment support**: a central hub/chassis grounding three deployable (hinged, optionally telescoping) legs, topped by a mounting interface (fixed threaded stud, or a pan/tilt/ball/gimbal camera head), optionally raised by a center column. Defining features kept: exactly three legs, at least one real non-fixed joint (leg hinge always articulates), a visible mounting interface at top, feet on a common support plane. Default mature domain: black photo/video camera tripod (S1/S2) and compact aluminum tabletop tripod (S3).

不该混入：
- **monopod** — a single leg; a tripod must have 3 splayed legs on a common ground plane.
- **four-leg stand / easel / light stand base** — 4+ legs or a fixed splay base; excluded.
- **camera / telescope / light that sits ON a tripod** — the payload is out of scope; we build the support + its mounting head only (an empty quick-release plate / stud / ball saddle is the terminal, no camera body).

## 槽位 + 候选模块表

### Slot A：legs (① skeleton + multiplicity leg_stage_count + topology)

Legs are parallel children of the hub. Each candidate owns the hub geometry and returns the head-mount seat height. Multiplicity axis `leg_stage_count` ∈ {1,2,3} is realized by the candidate itself (see §8).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_section` | forked_anchor | S3 `rec_picturex_0611__tripod__003` | L80-L235 | eligible if compatible | small clevis-ear aluminum hub; 3× REVOLUTE `leg_hinge` only; 1 tube + ferrule + rubber foot per leg (stage=1) |
| `two_stage` | forked_anchor | S2 `rec_picturex_0611__tripod__002` | L115-L289 | eligible if compatible | lathe hub shell + captured pivot pins; per leg REVOLUTE `leg_hinge` → PRISMATIC `leg_extension` → lower_leg + REVOLUTE `clamp_hinge` (stage=2) |
| `three_stage` | forked_anchor | S1 `rec_picturex_0611__tripod__001` | L103-L526 | eligible if compatible | tall spider chassis + center sleeve; per leg REVOLUTE `leg_hinge` → PRISMATIC `upper_to_middle` → PRISMATIC `middle_to_lower` + 2 flip levers (stage=3) |
| `braced_three_stage` | forked_anchor | S1 `rec_picturex_0611__tripod__001` (brace subtree) | L528-L576 | eligible if compatible | `three_stage` + REVOLUTE `brace_hinge` strut from brace_collar to each leg (stage=3, center-braced topology ①) |

### Slot B：center_column (② joint type / raise mechanism)

Optional prismatic riser between hub top and head; when present adds PRISMATIC column slide + REVOLUTE crank. Requires the tall S1 hub (three_stage / braced) which has the center sleeve; snapped to `none` otherwise.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | S2/S3 | S2 L325-L338 (head parents straight to hub) | eligible if compatible | no column part; head_pan parents directly to hub seat |
| `crank_column` | forked_anchor | S1 `rec_picturex_0611__tripod__001` | L154-L223 | eligible if legs∈{three_stage,braced} | PRISMATIC `center_column_slide` (column tube + top cap) + REVOLUTE `column_crank_turn` (spline crank arm + rubber grip) |
| `boom_column` | forked_anchor | `rec_0611_tripod_var_center_column_reversible_horizontal_bo` | L154-L200 | eligible if legs∈{three_stage,braced} | crank_column + `boom_pivot_housing` box + horizontal `boom_tube` + tail cap (head sits at boom end) |
| `leveling_column` | forked_anchor | `rec_0611_tripod_var_center_column_leveling_bowl_column` | L185-L200 | eligible if legs∈{three_stage,braced} | crank_column with open cast `_leveling_bowl_cap` half-ball socket top instead of flat cap |

### Slot C：head (③ Primary Form Family / Primary Form slot — registered in slot_choices)

The head is the form-dominant recognizable element (≥5 distinct form families). Pan/tilt heads parent REVOLUTE `head_pan` to the mount seat; `fixed_mount` adds no joint (threaded stud fused onto the hub visual).

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| `fixed_mount` | forked_anchor | S3 `rec_picturex_0611__tripod__003` | L87-L120 | Planar Boundary Form | threaded mount stack (shoulder + platform + stud + thread crests) fused into hub visual; NO head joint (legs supply articulation) |
| `three_way_pan_tilt` | forked_anchor | S1 `rec_picturex_0611__tripod__001` | L227-L348 | Volumetric Envelope Form | pan_base fork (drum + rounded body + 2 cheeks) → REVOLUTE tilt boxy body + spline pan handle → PRISMATIC `plate_slide` quick plate |
| `ball_head` | forked_anchor | S2 `rec_picturex_0611__tripod__002` | L291-L444 | Volumetric Envelope Form (spherical) | lathe pan_body + trim rings + tilt_socket → REVOLUTE Sphere `tilt_ball` + stem + toothed ring + plate/pad |
| `fluid_video_head` | forked_anchor | `rec_0611_tripod_var_head_fluid_video_head` | L48-L64, L282-L345 | Macro Surface Construction | pan_base fork → REVOLUTE cast swept `_fluid_head_shell` + transverse fluid cartridge + spline pan handle + plate_support |
| `gimbal_head` | forked_anchor | `rec_0611_tripod_var_head_gimbal_head` | L262-L324 | Planar Boundary Form (skeletal cradle) | pan_base fork → REVOLUTE gimbal axle + 2 hub disks + spline swing arm + carriage rail |

硬约束满足：Slot A=4, Slot B=4, Slot C=5，全部 ≥3；每个 candidate 有 forked_anchor + Lx-Ly；无单-candidate slot。

## 槽位图（slot graph）

pattern: mixed

```
hub/chassis (root, grounded)
 ├─[REVOLUTE leg_hinge_i, axis=+Y local, ×3 @ azimuth 120°]→ legs (Slot A)
 │      └ two_stage: →[PRISMATIC leg_extension_i]→ lower_leg
 │      └ three_stage/braced: →[PRISMATIC upper_to_middle_i]→ middle →[PRISMATIC middle_to_lower_i]→ lower
 │      └ braced: hub —[REVOLUTE brace_hinge_i]→ brace_i (parallel strut to leg)
 └─ head mount seat @ (0,0,seat_z):
        Slot B = none:  head_pan parents to hub
        Slot B = crank/boom/leveling: hub —[PRISMATIC center_column_slide]→ center_column
                                       hub —[REVOLUTE column_crank_turn]→ crank
                                       → head_pan parents to center_column top
        └─[REVOLUTE head_pan, axis=+Z]→ pan_base (Slot C, unless fixed_mount)
             └─[REVOLUTE head_tilt, axis=-Y]→ tilt_head
                  └─[PRISMATIC plate_slide, axis=+X]→ mounting_plate  (three_way / fluid only)
```

Interface points:
- **legs↔hub**: leg hip barrel captured on hub pivot pin/clevis ear at radius `hinge_r`, z=`hinge_z`; REVOLUTE axis local +Y (tangential) so each leg folds in its own radial vertical plane.
- **column↔hub**: column tube slides inside hub `center_sleeve`/`column_clamp` bore (PRISMATIC, axis +Z); origin on hub top face.
- **head↔mount**: pan_base drum contact face on seat (mount_z); REVOLUTE +Z symmetry centerline.
- **tilt↔pan**: tilt barrel/ball between the fork cheeks / in socket; REVOLUTE -Y.
- **plate↔tilt**: quick plate rides on plate_support top (PRISMATIC +X rail).

Mutually exclusive / derived: `fixed_mount` ⇒ no head_pan/tilt/plate; column∈{crank,boom,leveling} requires three_stage/braced legs; `plate_slide` only exists for three_way/fluid heads.

## 每槽位 Module Emits / Interfaces

### Slot A / single_section (S3)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hub` (root), `leg_0..2` | S3 L80-L205 |
| internal joints | `hub_to_leg_i` REVOLUTE axis +Y, range [-0.15, 0.45] | S3 L208-L235 |
| upstream interface | n/a (hub is root) | — |
| downstream interface | hub top seat @ z=seat_z for head/column | S3 L99-L110 |

### Slot A / two_stage (S2)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hub`, `upper_leg_i`, `lower_leg_i`, `clamp_lever_i` | S2 L115-L289 |
| internal joints | `leg_hinge_i` REVOLUTE +Y; `leg_extension_i` PRISMATIC -Z [0,0.035]; `clamp_hinge_i` REVOLUTE [0,1.0] | S2 L202-L285 |
| downstream interface | hub top seat @ z=0.27·scale | S2 L115-L135 |

### Slot A / three_stage & braced (S1)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis`(root), `upper_leg_i`, `middle_leg_i`, `lower_leg_i`, flip `*_lever_i`, (braced:) `brace_i` | S1 L103-L576 |
| internal joints | `leg_hinge_i` REVOLUTE; `upper_to_middle_i`/`middle_to_lower_i` PRISMATIC +Z; flip REVOLUTE; (braced) `brace_hinge_i` REVOLUTE | S1 L421-L576 |
| downstream interface | chassis center_sleeve top @ z=seat_z (carries column or head) | S1 L103-L123 |

### Slot B / crank|boom|leveling (S1 + variants)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `center_column`, `column_crank` | S1 L154-L223 |
| internal joints | `center_column_slide` PRISMATIC +Z [-0.08,0.22]; `column_crank_turn` REVOLUTE [-π,π] | S1 L167-L223 |
| upstream interface | column tube captured in chassis column_clamp bore | S1 L167-L175 |
| downstream interface | column top cap / bowl / boom-end @ mount_z for head_pan | S1 L161-L166 |

### Slot C / pan-tilt heads (S1/S2/variants)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pan_base`, `tilt_head`, (three_way/fluid:) `mounting_plate` | S1 L227-L348 / S2 L291-L385 |
| internal joints | `head_pan` REVOLUTE +Z [-π,π]; `head_tilt` REVOLUTE -Y [~-1.15,1.2]; (three_way/fluid) `plate_slide` PRISMATIC +X | S1 L247-L348 |
| upstream interface | pan_base drum bottom face on mount seat | S1 L247-L260 |
| downstream interface | quick plate / ball saddle top (payload interface, terminal) | S1 L321-L333 |

活动件全部有 articulation；lock 旋钮/mount 螺丝等极小旋件按 Rule 1 折成宿主 parent.visual（不动细节，减关节与碰撞风险），装饰 stud/thread crests 亦为宿主 visual。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| legs_style | enum | single_section / two_stage / three_stage / braced_three_stage | three_stage | choice | procedural sampler | Slot A |
| column_style | enum | none / crank_column / boom_column / leveling_column | none | conditional | non-`none` requires legs∈{three_stage,braced}; else snap none | Slot B |
| head_style | enum | fixed_mount / three_way_pan_tilt / ball_head / fluid_video_head / gimbal_head | ball_head | conditional | fixed_mount ⇒ column=none | Slot C |
| palette_style | enum | 6 colorways (§8.5 ⑥) | matte_black | choice | procedural sampler | S1/S2/S3 materials |
| height_scale | float | [0.85, 1.20] | 1.0 | independent | uniform sample, clamp | S1/S2 leg length |
| spread_scale | float | [0.85, 1.20] | 1.0 | independent | uniform sample, clamp | S1/S2 leg splay |
| leg_fold_upper | float | derived | 0.35 | equation | `= min(source_upper, 0.35)` keep 3 folded legs clear of center | S1-S3 hinge |
| (—) | constraint | — | — | inequality | column present ⇒ legs tall-hub family; violate ⇒ snap column=none | interface |

连续尺寸采样契约：先采 height_scale, spread_scale (independent) → 派生 fold ranges (equation) → column/head 兼容性 (conditional/inequality) 在 `resolve_config` 内解析。

## 7.5 编译预算 / compile budget

Per-seed budget: **≤25s** (typical 12-20s). Basis: sources use cadquery hollow tubes (telescoping sleeves), LatheGeometry hubs, spline tubes (crank/pan handle/gimbal arm/legs), loft feet — moderate boolean/sweep cost. Tessellation discipline: cadquery `tolerance=0.001, angular_tolerance=0.08`; Lathe `segments≤64`; spline `samples_per_segment≤16, radial_segments≤18`; small features ≤32 seg. **Reuse one shared Mesh across the 3 identical legs** (build leg sleeve/tube/foot meshes once). Prefer SDK Cylinder/Box/Sphere over cadquery where the source allows. sweep `--compile-timeout 120` (watchdog ≈ 5× budget).

## Multiplicity / Copy Logic

- **Axis 1 — leg_count**: fixed at **3** (category identity; NOT sampled). 3 legs at azimuth spacing 120° via shared helper, named `leg_{i}` / `upper_leg_{i}` etc., regular radial placement, uniform per-leg joint policy.
- **Axis 2 — leg_stage_count** ∈ {1,2,3}: realized by legs_style candidate (single=1, two_stage=2, three/braced=3). Registered in `slot_choices` as `("leg_stages", str(n))`. N_range bounded by source samples (S3=1, S2=2, S1=3); 4-stage not authored (no clean source beyond forked var; excluded to bound compile + collision). Weight: three_stage/two_stage common, single_section + braced rarer.
- copied object / naming / placement / joint policy: shared leg helper per style, `name_{i}`, 120° radial, uniform joints, per-leg captured-pin allow_overlap.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | legs_style {single(1 hinge/leg), two_stage(hinge+prismatic), three_stage(hinge+2 prismatic), braced(+brace revolute)}; column present adds prismatic+revolute. forked_anchor S1/S2/S3 + variants |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：leg_count=3 固定；leg_stage_count∈{1,2,3} |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE (leg_hinge +Y, head_pan +Z, head_tilt -Y, crank, brace, clamp), PRISMATIC (leg_extension/telescope +Z, column_slide +Z, plate_slide +X). 每种在 sweep 出现。source-backed |
| ③ 主体形态家族 | 换核心 part 形态原型 | 有 | head slot ≥5 families: fixed_mount(Planar Boundary), three_way_pan_tilt(Volumetric Envelope), ball_head(Volumetric spherical), fluid_video_head(Macro Surface swept cast), gimbal_head(Planar skeletal cradle). 登记进 slot_choices。source-backed + variant anchors |
| ④ 表面装饰 | 叠加表面细节 | 有 (record_only) | thread crests (S3), trim/toothed rings (S2), red identification mark (S1), recessed leg face (S2), clamp housings — 均为宿主 part.visual，随 ③/⑤ 尺寸缩放派生（不独立常数） |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | height_scale [0.85,1.2], spread_scale [0.85,1.2]. 运动包络: leg_hinge REVOLUTE +Y [-0.15, ≤0.35] (fold inward); leg telescope PRISMATIC +Z [0, ~0.09] (extend out); column_slide PRISMATIC +Z [-0.08,0.22]; head_pan REVOLUTE +Z [-π,π]; head_tilt REVOLUTE -Y [-1.15,1.2]; plate_slide PRISMATIC +X [-0.018,0.018]. motion_test_plan: sampled collision (max_pose_samples=40, ignore_fixed) + targeted `ctx.pose`: leg extends outward, head_tilt raises plate, head_pan rotates plate, leg folds inward. captured pins/telescoping sleeves/ball socket → element-scoped allow_overlap (not broad) |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 colorways, 大类 metal+plastic+rubber: matte_black(S1), satin_silver(S2), brushed_aluminum(S3), graphite_pro, carbon_red, titanium_gray. 材质大类覆盖 ≥ ceil(0.5×6)=3 |

收尾自检：head 形态家族在 0-9 seed 渲染必须肉眼拉开；palette 明显变化；telescoping/pan/tilt 全程不穿模。

## 采样与覆盖审计

总组合数：legs(4) × column(4, gated) × head(5) × palette(6) ≈ 4×5×6 base × column multiplier. 合法组合（column gating）约 legs{single,two}×column{none}×head{5} + legs{three,braced}×column{4}×head{5} = 2×1×5 + 2×4×5 = 10+40 = 50 topological combos × 6 palettes = 300 config-combos，× height/spread 连续.

seed_domain_policy：procedural_first。config_from_seed(seed): rng=Random(seed); sample palette; sample legs_style (weighted: three_stage 0.35, two_stage 0.30, single 0.20, braced 0.15); sample column_style gated on legs; sample head_style gated on column (fixed_mount only when column none, weight higher for single/two); sample height_scale, spread_scale. seed=0 无特殊化（procedural）。No curated table.
Topology target：1000-seed slot tuple coverage report-only；真实拓扑组合 ≈50，兼容约束限制，低于 300 已说明（column 需 tall hub、fixed_mount 需 none column、3-leg 固定）。
Controlled local parameterization：height_scale, spread_scale ∈[0.85,1.2] clamp；leg fold upper derived-clamped ≤0.35；不破坏 interface/clearance/joint origin。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted legs→column(gated)→head(gated)→palette; height/spread uniform | slot_choices_for_seed matches build |
| compatibility matrix | column≠none ⇒ tall hub; fixed_mount ⇒ column none; snap illegal to legal | no floating column, no head on missing seat |
| controlled local variation | height/spread scale clamp | proportions vary, feet stay on plane, interfaces intact |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial, 0-999 maturity | axis_realization; head family + telescoping visible |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| legs | 4 | yes | yes | multiplicity leg_stage_count |
| center_column | 4 | yes | yes | gated on tall hub |
| head | 5 | yes | yes | ③ primary form slot |

## Validator

- slot_choices_for_seed returns implemented module names (legs/column/head/leg_stages/palette)
- config_from_seed uses deterministic procedural sampling for all seeds incl. 0
- compatibility matrix snaps illegal column/head combos before build
- controlled scales clamped in resolve_config; cannot break interfaces/clearance/joint origin
- key joints: leg_hinge REVOLUTE +Y; telescope/column PRISMATIC +Z; head_pan REVOLUTE +Z; head_tilt REVOLUTE -Y
- 3 legs at 120°; shared leg mesh; captured-pin overlaps element-scoped

## Reject cases

- monopod (1 leg) or 4+ legs.
- column floating above hub (no center_sleeve capture) / head parented to a missing seat.
- telescoping stage fully separated from its sleeve (no retained insertion) at any pose.
- legs collide with each other at fold upper (range too wide) — cap fold upper.
- head pan/tilt drives payload plate through the fork or column (穿模 at limit pose).
- Lathe/mesh hub or swept fluid shell downgraded to plain Box/Cylinder.
- decorative lock knob / stud spawned as FIXED-joint floating part instead of host visual.

## 与相邻类别的边界

- 不该混入：monopod（单腿；tripod 必须 3 条张开腿共地面）。
- 不该混入：four-leg stand / light stand（≥4 腿或固定张开底座）。
- 不该混入：camera/telescope on tripod（负载本体越界；仅造支撑 + 顶部空 mounting 接口）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 3 origins + variants; proceeding straight to template per P4 |
