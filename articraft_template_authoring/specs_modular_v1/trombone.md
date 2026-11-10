# Modular Spec — trombone (大类 0611)

## 元信息
| 项 | 值 |
|---|---|
| slug | `trombone` |
| template path | `agent/templates/trombone.py` |
| test path (optional) | `tests/agent/test_trombone_template.py` (not authored; sweep is authoritative) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern` = mixed: a fixed 3-part telescoping skeleton (`body` root + `outer_slide` PRISMATIC + `tuning_slide` PRISMATIC) with per-slot geometry swaps (parallel style/form layers) plus a conditional multiplicity of rotary-valve child parts (parallel children of `body`).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 (2 origin anchors + 9 slot forks) |
| read_count | 11 (both origins deep-read; 9 forks surveyed for part/joint/visual topology) |
| read_scope | all 5-star samples in this category (source map `0611__trombone.md`) |
| source_index_policy | only adopted module sources are indexed below |

**Reading summary.** Two origin lineages:

- **S1 `tenor_trombone`** (`rec_picturex_0611__trombone__001…`, model.py L182-301): root `body` (fixed bell section + fixed inner slide tubes) + `outer_slide` (PRISMATIC +X, travel 0.50 m) + `tuning_slide` (PRISMATIC −X, travel 0.025 m). Legs stacked in **Z** (bottom leg z=0, top leg z=TOP_Z=0.072), bell axis z=BELL_Z=0.190, rear tuning loop lower leg z=0.046. Tubes are `Cylinder` via `_x_tube`/`_z_bar` helpers (L51-66); bell flare + mouthpiece are `LatheGeometry` shells (L69-122); gooseneck / slide-bow / tuning-crook are `tube_from_spline_points`/`WirePath` sweeps (L125-179); a ribbed chrome brace disc = `Cylinder` + `TorusGeometry` rim + hub (L239-258). Two prismatic joints (L278-299) with rich telescoping `allow_overlap` + `expect_overlap` insertion tests (L320-650).
- **S2 `slender_tenor_trombone`** (`rec_picturex_0611__trombone__002…`, model.py L103-371): root `bell_section` + `hand_slide` (single PRISMATIC +X, travel 0.56 m). Legs spaced in **Y** (y=±0.052); hollow cadquery annular tubes + swept U-bows (L31-101); compact restrained `LatheGeometry` bell (L155-186); nickel-silver **stocking collars** + **U-bend ferrule** slide hardware (L323-345); a small round **counterweight** stack behind the rear bow (L262-279).

**Adopted unification.** The template is authored on the **S1 frame + primitive strategy** (Z-stacked legs; `Cylinder`+`LatheGeometry`+spline sweeps — no cadquery booleans, cheap tessellation) as the single coherent spine. S2's contributions (compact/restrained bell母线, collar/ferrule slide hardware, counterweight) enter as **candidate modules** within slots, keeping S1's primitive families (Rule 3: Lathe stays Lathe, sweeps stay sweeps). The 9 forks map to the diversity axes below.

## 核心身份

A brass **trombone**: a bell + mouthpiece air path joined by a curved gooseneck/tuning loop, with the defining **telescoping hand slide** (prismatic) that a player extends to change pitch, plus a rear **tuning slide** (small prismatic) and optional **rotary valve attachment(s)**. Mature domain = tenor/bass/soprano/contrabass hand-slide trombones and valve/rotary-attachment variants. Defining features that MUST survive: a wide Lathe **bell flare** far larger than the tubing, a mouthpiece, two parallel slide legs bridged by an outer U-bow, and ≥1 real prismatic slide joint with retained insertion at both closed and extended poses.

## 槽位 + 候选模块表

### Slot A：`bell_form` (③ Primary Form Family — 主体形态家族, carries primary visual diversity)

Governs the fixed `body`'s bell母线 (throat / rim / flare-length / flare-exponent) and the derived bell-axis height + rear-loop proportions. Same part tree, same primitive (`LatheGeometry.from_shell_profiles` flare + `Cylinder` tubes), same interface; only the discrete **Volumetric Envelope Form** (bell flare sweep母线) + rim size change. `form_subtype = Volumetric Envelope Form` for all four.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tenor` | forked_anchor | `rec_picturex_0611__trombone__001…` | L69-99 | eligible if compatible | classic medium flare, rim r≈0.100, flare_len≈0.40, exp≈2.6 (Volumetric Envelope Form) |
| `bass` | forked_anchor | `rec_0611_trombone_var_body_family_bass_trombone_with_f_attac` | L221-318 (bell L257) | eligible if compatible | larger deeper bell, rim r≈0.118, flare_len≈0.46, exp≈2.4; taller BELL_Z |
| `soprano` | forked_anchor | `rec_0611_trombone_var_body_family_compact_soprano_trombone` | L190-305 (bell L226) | eligible if compatible | small short bell, rim r≈0.062, flare_len≈0.24, exp≈2.8; compact frame |
| `slender` | forked_anchor(S2母线) | `rec_picturex_0611__trombone__002…` | L155-186 | eligible if compatible | restrained long-taper bell, rim r≈0.090, flare_len≈0.42, exp≈3.2 (S2 compact profile ported to S1 frame) |

### Slot B：`slide_style` (③/② slide-hardware form)

Governs the `outer_slide` grip hardware (all styles keep the two `Cylinder` outer legs + spline `slide_bow` + `outer_slide_brace`; the mounted hardware differs). 2 candidates — the 5★ pool has exactly two slide-hardware families (S1 disc-braced vs S2 collar/ferrule); degrade-to-2 justified by the source pool.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `disc_brace` | forked_anchor | `rec_picturex_0611__trombone__001…` | L239-258 | eligible if compatible | ribbed chrome brace disc = `Cylinder` disc + `TorusGeometry` rim + `Cylinder` hub on the slide brace |
| `plain_collar` | forked_anchor | `rec_picturex_0611__trombone__002…` | L323-345 | eligible if compatible | two nickel stocking collar rings on the outer legs + a U-bend nose ferrule; no disc |

### Slot C：`valve_attachment` (② joint / mechanism type)

Rotary valve section parented to `body`. Adds 0 / 1 / 2 REVOLUTE **rotor** child parts (captured spindle in a casing) + host-visual casing/wrap-loop on `body`. 3 candidates spanning ②: no rotary joint / one / two.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | `rec_picturex_0611__trombone__001…` | L182-301 | eligible if compatible | plain hand-slide trombone; no rotor part, no rotary joint |
| `single_rotary` | forked_anchor | `rec_0611_trombone_var_attachment_single_rotary_trigger` | L355-470 | eligible if compatible | one `valve_rotor` part (REVOLUTE +Z) = rotor stem + thumb-lever paddle, captured in a `Cylinder` casing + brass wrap loop on `body` |
| `dual_rotary` | forked_anchor | `rec_0611_trombone_var_attachment_dual_rotary_triggers` | L349-410 | eligible if compatible | two `valve_rotor_{0,1}` parts (REVOLUTE +Z each), two casings + wrap loops on `body` |

## 槽位图（slot graph）

pattern: mixed

```
                 body (root, fixed bell section + fixed inner slide legs)
                  │   [bell_form → Slot A sets body bell/loop geometry]
    ┌─────────────┼───────────────────────────────┬────────────────────────┐
    │ PRISMATIC +X│ origin=(OUTER_X0,0,0)          │ PRISMATIC −X           │ REVOLUTE +Z ×{0,1,2}
    │ telescoping │ retained insertion            │ origin=(TUNING_X0,0,LOOP_LOW_Z)   captured spindle
    ▼             │                               ▼                        ▼
 outer_slide  [slide_style → Slot B]          tuning_slide          valve_rotor[_i]  [valve_attachment → Slot C]
  + water_key ×{0,1,2}  [multiplicity]
```

- `body` is the single root; `outer_slide`, `tuning_slide`, and every `valve_rotor` are direct children.
- **outer_slide** joint: PRISMATIC axis +X, origin at `(OUTER_X0,0,0)` on the inner-leg axis; interface = inner top/bottom `Cylinder` legs telescoped by the outer legs (captured proxy, `allow_overlap`, joint **omits** `MatingContract` — Rule 2 grandfather for telescoping sleeves). Travel derived so closed insertion ≥ 0.50 m and extended insertion ≥ 0.05 m.
- **tuning_slide** joint: PRISMATIC axis −X, origin at `(TUNING_X0,0,LOOP_LOW_Z)`; interface = fixed loop legs telescoped by tuning sleeves (captured proxy, `allow_overlap`, omits `MatingContract`). Travel ≤ 0.03 m, insertion retained.
- **valve_rotor** joint(s): REVOLUTE axis +Z, origin at the casing center on `body`; rotor spindle captured in the casing bore (`allow_overlap` rotor↔casing, omits `MatingContract` — captured pin). Range a small thumb throw.
- Slots are independent (any bell_form × slide_style × valve_attachment × water_key_count is legal): the body always exposes the same inner-leg + loop-leg + brace interfaces regardless of bell母线.

## 每槽位 Module Emits / Interfaces

### Slot A / `bell_form` (writes `body`)
| emits | 描述 | 来源 |
|---|---|---|
| parts | none new — writes `body` visuals: `inner_top_tube`,`inner_bottom_tube`, stockings, `mouthpiece_receiver`,`gooseneck_ferrule`,`inner_slide_brace`, `mouthpiece`(Lathe),`gooseneck_tube`(sweep),`loop_lower_tube`,`bell_tube`,`bell_flare`(Lathe, per form),`bell_brace`,`loop_brace` | S1 model.py:L193-221 |
| internal joints | none | — |
| upstream interface | root — `body` grounded; exposes inner top/bottom leg axes (z=TOP_Z, z=0) for the outer slide, and loop legs (z=LOOP_LOW_Z, z=BELL_Z) for the tuning slide | S1:L195-221 |
| downstream interface | inner-leg `Cylinder` faces (telescoped by outer_slide); loop-leg faces (telescoped by tuning_slide); casing seats for valve_attachment | S1:L195-299 |

### Slot B / `slide_style` (writes `outer_slide`)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `outer_slide` visuals: `outer_top_tube`,`outer_bottom_tube`,`outer_top_sleeve`,`outer_bottom_sleeve`,`slide_bow`(sweep),`outer_slide_brace` + style hardware (`disc_brace`: `brace_disc`,`disc_rim`,`disc_hub`; `plain_collar`: `slide_collar_0/1`,`u_bend_ferrule`) + water keys | S1:L227-258 / S2:L323-345 |
| internal joints | none | — |
| upstream interface | outer legs telescope the inner legs; joint origin `(OUTER_X0,0,0)`, PRISMATIC +X | S1:L278-288 |
| downstream interface | none (leaf) | — |

### Slot C / `valve_attachment` (writes `body` host visuals + `valve_rotor[_i]` parts)
| emits | 描述 | 来源 |
|---|---|---|
| parts | 0/1/2 `valve_rotor[_i]` = `rotor_stem`(Cylinder) + `rotor_hub` + `trigger_lever`(Box) + `thumb_paddle`(Cylinder) | single L420-450 / dual L349-410 |
| host visuals on body | `valve_casing[_i]`(Cylinder) + `valve_wrap_loop[_i]`(sweep) + `rotor_cap[_i]` | single L355-404 |
| internal joints | `body_to_valve_rotor[_i]` REVOLUTE +Z, small thumb-throw range | single L451-470 |
| upstream interface | casing bore on `body` captures the rotor stem (grandfathered captured pin, omit MatingContract) | single L451-470 |

### tuning_slide (fixed skeleton, always emitted)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tuning_slide`: `tuning_lower_sleeve`,`tuning_upper_sleeve`,`tuning_crook`(sweep),`tuning_slide_brace` | S1:L263-273 |
| internal joints | `tuning_slide_travel` PRISMATIC −X | S1:L289-299 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `bell_form` | enum | tenor / bass / soprano / slender | — | choice | deterministic sampler | Slot A |
| `slide_style` | enum | disc_brace / plain_collar | — | choice | deterministic sampler | Slot B |
| `valve_attachment` | enum | none / single_rotary / dual_rotary | — | choice | deterministic sampler | Slot C |
| `water_key_count` | int (multiplicity) | {0,1,2} | 1 | choice | weighted sampler (see §8) | water_key forks |
| `palette_style` | enum | 5 colorways (§8.5 ⑥) | gold_lacquer | choice | deterministic sampler | S1/S2 materials |
| `frame_scale` | float | [0.90, 1.12] | 1.0 | independent | global similarity; every dim/origin/joint-origin/travel ×`s`; meshes `unit_scale=s` | S1 dims |
| `form_scale` | float | derived | 1.0 | equation | `= {soprano:0.82, tenor:1.0, slender:1.03, bass:1.09}[bell_form]`; folds into `s = frame_scale·form_scale` | Slot A |
| `bell_rim_r` | float | derived | — | equation | `= per-form rim radius` (0.062…0.118)·s | Slot A |
| `BELL_Z` | float | derived | — | equation | `= (TOP_Z + bell_rim_r_nom + 0.020)·s` — bell axis rises with rim so the flare clears the top slide tube | Rule: bell-clears-slide |
| `slide_extension_scale` | float | [0.75, 1.0] | 1.0 | conditional | scales slide travel **down only**; upper = `derived_max_travel·scale`, never exceeds retained-insertion bound | S1:L44 |
| (—) | constraint | — | — | inequality | closed insertion `= (INNER_X1 − OUTER_X0)·s − 0.06·s ≥ 0.50·s`; extended insertion `≥ 0.05·s` ⇒ `max_travel = (INNER_X1−OUTER_X0−min_engage)·s`; clamp travel to it | S1:L41-44 |
| (—) | constraint | — | — | inequality | tuning travel `≤ 0.03·s`, tuning insertion retained `≥ 0.015·s` extended | S1:L44-48 |

All `equation`/`inequality`/`conditional` are solved in `resolve_config`; the builder never fails on them.

### 7.5 编译预算 / compile budget（必填）
**Budget: ≤ 12 s/seed.** Basis: geometry is `Cylinder`/`Box`/`TorusGeometry` primitives + a handful of `LatheGeometry` shells (bell 48-64 seg, mouthpiece 40 seg) + short `tube_from_spline_points` sweeps (gooseneck/bow/crook/wrap-loop, ≤18 radial seg, ≤10 samples/seg) — **no cadquery boolean solids**, so far under the 5-20 s typical band. Tessellation tiers: bell hero flare ≤64 seg, mouthpiece/collars ≤40, sweep radial ≤18, small radii ≤24. Water keys and dual rotors reuse one shared helper each. Sweep hang-guard `--compile-timeout 120` (≈10× budget). Exceed budget ⇒ drop bell segments before iterating.

## Multiplicity / Copy Logic

One multiplicity axis: **water keys** (spit valves).

- `count_param` = `water_key_count`; `N_range` = product domain {0,1,2} (real trombones carry 0-2 water keys); sampling domain weighted **{1:0.5, 0:0.3, 2:0.2}** (one key most common).
- copied object: a `water_key` = small saddle nub (`Cylinder`) + lever (`Box`) + touch-cork (`Cylinder`), one shared helper `_water_key(...)`.
- naming: `water_key_saddle_{i}`, `water_key_lever_{i}`, `water_key_cork_{i}`.
- placement: key 0 on the `outer_slide` U-bow (near the nose); key 1 on the `tuning_slide` crook. Regular, host-derived placement.
- joint policy: **non-moving decoration** — folded into the host part as `parent.visual(...)` (Rule 1: a real spit key rotates, but the 5★ water-key forks author it as fixed host geometry, so we keep it fixed and fused, no FIXED-joint part).
- source/gating: `rec_0611_trombone_var_water_key_count_1_water_key` / `…_2_water_keys`. N sampled independently, clamped to {0,1,2}, recorded in `slot_choices`.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | Fixed spine = `body`+`outer_slide`(PRISMATIC)+`tuning_slide`(PRISMATIC); `valve_attachment` adds 0/1/2 REVOLUTE `valve_rotor` parts → 2-part/2-joint … 4-part/4-joint kinematic graphs. All forked_anchor (single/dual rotary forks). |
| └ multiplicity | 同构件 ×N | 有 | water_key_count ∈ {0,1,2}; weights {1:0.5,0:0.3,2:0.2}; source = water_key forks. See §8. |
| ② 关节类型 | 换 type/轴 | 有 | PRISMATIC +X (hand slide), PRISMATIC −X (tuning slide), REVOLUTE +Z (rotary valves, 0-2). Every declared type realized in sweep (valve_attachment guarantees revolute appears). forked_anchor. |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | Slot A `bell_form`: tenor / bass / soprano / slender — 4 recognizable bell **Volumetric Envelope Forms** (flare母线 throat/rim/len/exp differ, not mere scale). Registered in `slot_choices`. Slot B `slide_style` (disc vs collar hardware) adds a second ③/② axis. source-backed anchors. |
| ④ 表面装饰 | 叠加表面细节/改数 | 有 | Slide braces (`inner_slide_brace`,`outer_slide_brace`,`bell_brace`,`loop_brace`,`tuning_slide_brace`) as host visuals; ribbed chrome disc rim (disc_brace); collar rings (plain_collar); water keys ×{0,1,2}. `record_only`. All fused to host part surface (Rule 1/4), no constant-radius bands over tapered bodies. |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | `frame_scale`∈[0.90,1.12], `form_scale` per-form, `slide_extension_scale`∈[0.75,1.0]. **Motion envelopes:** hand slide PRISMATIC +X `[0, max_travel≈0.50·s]` (retained insertion, motion_test: sampled collision + `ctx.pose(max)` bow moves forward by travel); tuning slide PRISMATIC −X `[0, ≤0.03·s]` (`ctx.pose(max)` crook moves rearward, insertion retained); valve REVOLUTE +Z `[0, ≈0.6]` (`ctx.pose(upper)` paddle swings). `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` + one targeted `ctx.pose` per mechanism. No sampled-pose exemption. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | metal-family only (all brass/plated instruments). 5 colorways: `gold_lacquer` (S1: warm brass + chrome), `pale_gold_polished` (S2: pale brass + nickel silver), `silver_plated` (silver body + brass trim), `rose_brass` (reddish brass), `dark_lacquer` (antique dark brass). Roles: `brass`,`brass_deep`,`bright`,`accent`. metal覆盖 ≥ ceil(0.5×5)=3 ✓ (all 5 are metal-family — trombones are always brass/plated; single大类 justified). |

**收尾自检**: 0-9 seed renders must show 4 distinct bell silhouettes (soprano small ↔ bass wide), disc vs collar slides, 0/1/2 rotary valves + water keys, and 5 visibly different metal finishes; slides open full-travel without穿模.

## 采样与覆盖审计

总组合数：bell_form(4) × slide_style(2) × valve_attachment(3) × water_key_count(3) = **72** discrete topology combos; × continuous scales (frame/form/extension) → effectively unbounded. 72 ≥ 300 目标 не достигается на дискретном уровне; 理由: category组合空间真实上界 = 4×2×3×3=72 (bounded by source-backed candidates; trombone is a low-topology category — one dominant slide DOF). report-only Topology target 记为 72, 说明真实组合上界即此。

理由：primary diversity from ③ bell_form + ② valve_attachment + slide hardware; continuous scales carry ⑤; palette carries ⑥.

seed_domain_policy：procedural_first — `config_from_seed(seed)` seeds `random.Random(seed)`, samples each slot enum + weighted water_key_count + palette + continuous scales; seed 0 not special. No curated/modulo table.

Procedural Sampling / Sweep Plan：every slot independently sampled; no illegal combos exist (all slots share the invariant body interfaces), so no compatibility gating needed beyond clamps. Sweep 0-35 for pass; 0-999 report-only maturity. viewer 目检 seeds 0-9.

Topology target：72 (真实组合上界). report-only.

Controlled local parameterization：`frame_scale` (global similarity, clamp [0.90,1.12]), `slide_extension_scale` (travel down-scale, [0.75,1.0], conditional on retained-insertion inequality). `form_scale` derived per bell_form. All clamped/derived in `resolve_config`; none breaks the telescoping insertion or joint origins.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent per-slot rng.choice + weighted water_key + uniform scales | slot_choices_for_seed matches build choices |
| compatibility matrix | all combos legal (shared body interfaces); only clamp travel to insertion bound | no floating, no closed/mid overlap, retained insertion, valve axis |
| controlled local variation | frame_scale, slide_extension_scale, form_scale | proportions vary; interfaces/clearance/joint origins intact |
| regression overrides | none | — |
| random sweep | 0-35 initial pass, 0-999 maturity audit | contract failures; axis_realization; bell/slide/valve viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| bell_form | 4 | yes | yes | ③ primary form family |
| slide_style | 2 | yes | no | degrade-to-2: source pool has exactly two slide-hardware families |
| valve_attachment | 3 | yes | yes | ② joint diversity 0/1/2 revolute |
| water_key_count | 3 (N∈{0,1,2}) | yes | yes | multiplicity |

## Validator

- `slot_choices_for_seed` returns implemented module names for all 4 axes.
- `config_from_seed` uses deterministic procedural sampling for all seeds incl. 0.
- no illegal combinations (all slots compatible); travel clamped to retained-insertion inequality in `resolve_config`.
- no regression overrides.
- continuous scales clamped/derived in `resolve_config`; cannot break telescoping insertion, joint origins, or bell-clears-slide.
- key joints: `outer_slide_travel` PRISMATIC +X; `tuning_slide_travel` PRISMATIC −X; `body_to_valve_rotor[_i]` REVOLUTE +Z when present.
- water keys follow `water_key_*_{i}` naming, fused as host visuals.
- bell_flare is `LatheGeometry` (never downgraded to Cylinder/Box); gooseneck/bow/crook remain sweeps.

## Reject cases

- Bell flare downgraded to a Cylinder/cone, or missing (loses trombone identity).
- Slide with no retained insertion at closed or extended pose (tubes separate → floating / 穿模).
- Bell flare overlapping the top slide tube at rest (BELL_Z not risen with rim).
- A `valve_rotor` whose paddle does not visibly rotate under `ctx.pose`, or whose axis is wrong.
- Water key authored as a FIXED-joint micro-part instead of a fused host visual.
- Any single continuous scale driving primary diversity instead of the discrete ③ bell_form / ② valve slots.
- Illegal per-seed drift making `slot_choices_for_seed` disagree with the actual build.
- Tuning slide travel > 0.03 m or losing loop-leg engagement.

## 与相邻类别的边界

- 不该混入：**trumpet**（valves + short straight body, no telescoping hand slide; trombone's defining DOF is the prismatic slide）.
- 不该混入：**euphonium/tuba**（conical wrapped tubing, piston valves, no hand slide; much larger conical bore）.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored continuously with template (no spec-approval stop per workflow). |

## 模板实现备注（可选）

- Shared helpers: `_x_tube`/`_z_bar` (Cylinder tubes), `_bell_flare_mesh(form)` (parametric Lathe shell), `_sweep_bow`/`_gooseneck`/`_tuning_crook` (spline sweeps), `_water_key(host, i, ...)`, `_valve_rotor(model, i, ...)`, `_o(s,...)` (scaled Origin).
- Telescoping prismatic joints and captured rotor pins **omit `MatingContract`** and declare element-scoped `allow_overlap` (Rule 2 grandfather for sleeves/pins), mirroring both origins' run_tests.
- `BELL_Z` single-sourced from `bell_rim_r` (Contract 3c) so the bell always clears the top slide tube across ③/⑤.
- Global `s = frame_scale·form_scale` applied to every literal + `unit_scale=s` on every mesh (mirrors manual_hand_drill.py).

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | skeleton+A/B | tenor / disc_brace | `rec_picturex_0611__trombone__001…` | L182-301 | full spine, bell, slide+disc, tuning slide, joints, telescoping tests |
| S2 | A/B | slender / plain_collar | `rec_picturex_0611__trombone__002…` | L103-371 | compact bell母线, collar/ferrule hardware, counterweight |
| F1 | A | bass | `…body_family_bass_trombone_with_f_attac` | L221-318 | large bell profile |
| F2 | A | soprano | `…body_family_compact_soprano_trombone` | L190-305 | small bell profile |
| F3 | C | single_rotary | `…attachment_single_rotary_trigger` | L355-470 | rotor part + casing + wrap loop + REVOLUTE joint |
| F4 | C | dual_rotary | `…attachment_dual_rotary_triggers` | L349-410 | two rotor parts |
| F5 | mult | water keys | `…water_key_count_1_water_key` / `…_2_water_keys` | full | water-key host visuals |
</content>
</invoke>
