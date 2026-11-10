# Modular Spec — playground_seesaw

## 元信息
| 项 | 值 |
|---|---|
| slug | `playground_seesaw` |
| template path | `agent/templates/Playground_Seesaw.py` (module file named by slug per CLI convention; exports use stem `seesaw`) |
| test path (optional) | (inline `run_seesaw_tests`, no separate pytest file) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel beam(s) on a shared base + seat-count multiplicity per beam) |

`stem` = `seesaw`. Template exports `build_seesaw`, `config_from_seed`,
`run_seesaw_tests`, plus `slot_choices_for_seed` / `slot_choices_for_config`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 retained parent seeds + 90 fork-variant siblings (combinatorial multi-axis diffs) |
| read_count | 3 parents read in full; variant pool read via prompt structural-change tally + spot-read of model.py (approved temporary fast path) |
| read_scope | all 3 picture-family parents (001 vintage, 002 four-seat tube, 003 modern commercial) + structural-change directive of every `rec_qwen_seesaw_00{1,2,3}_v*` |
| source_index_policy | only adopted module sources are indexed below |

Adopted parent sources (S-ids in Module Source Index):

- **S1** `rec_model-a-vintage-playground-seesaw-about-3-0-m-lo_20260610_085246_107703_152f9b4a` — single rectangular-bar beam, arched crossed-tube base, central revolute, wood seat + inverted-U grab handle + rubber tire bumper per end.
- **S2** `rec_model-a-four-seat-playground-seesaw-made-of-bent_20260610_085257_909864_2c2b677d` — two independent yellow tube-truss beams in a shallow X on a sky-blue arched tube base; each beam its own revolute pivot; seat plate + T-handlebar per end; axle-sleeve hub.
- **S3** `rec_model-a-modern-commercial-playground-seesaw-abou_20260610_085310_256700_c240aa26` — single thick curved banana tube on a gray cylindrical pedestal + black cast pivot bracket; clamp collars, drop-tube seats, handle-grip plates, single central revolute.
- **S4** (variant family, e.g. `rec_qwen_seesaw_001_v02`, `_005`) — central coil spring on a **prismatic** (Z) joint under the beam, with the beam rock revolute stacked above the spring hub (prismatic + revolute chain).

## 核心身份

A playground seesaw is a long balance beam that **rocks about a single horizontal
pivot axis** carried by a static central support, with a **seat at each end**
(and, for cross/four-seat forms, seats at the ends of more than one beam). The
primary non-fixed joint is always the beam pivot (revolute), optionally preceded
by a central spring-compression prismatic joint. Identity invariants: opposed
seats that swap height when the beam rocks; the base stays grounded and static;
beam length ~2.4-3.2 m; pivot height ~0.3-0.85 m.

Not a swing (no overhead frame / hanging seats — that is `playground_swing`),
not a spring rider (a seesaw balances two riders across a pivot, a rider bounces
one rider on a coil), not a bench or plank by itself (must articulate).

## 槽位 + 候选模块表

Three replaceable structural layers plus one multiplicity axis (seats per beam).

### Slot A：beam_form （rocking-beam body family）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_plank_beam` | S1 | L168-L192 | eligible if compatible | single long rectangular `Box` bar beam + pivot sleeve + gusset; classic plank |
| `tube_truss_beam` | S2 | L131-L192 | eligible if compatible | top tube + diagonal brace truss + axle sleeve hub (swept/cylinder tubes) |
| `curved_banana_beam` | S3 | L103-L141 | eligible if compatible | thick parabolic swept tube dipping at center, sweeping up at ends + pivot stub |
| `heavy_steel_beam` | S2/S3 | S2 L137-L141 + S3 L26-L31 | eligible if compatible | one fat straight `Cylinder` tube beam (large radius), commercial look |
| `compact_short_beam` | S1 | L32, L168-L183 | eligible if compatible | shorter (~2.0 m) plank-style beam for backyard/triangular-support form |

(`asymmetric_seat_heights` and `four_seat_cross` are **not** separate beam
modules: asymmetry is a per-seat drop offset on any beam form; the cross/4-seat
look is produced by the **beam-count + seat-count multiplicity**, see §8.)

### Slot B：pivot_mechanism （how the beam rocks）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `central_revolute_teeter` | S1 | L222-L231 | eligible if compatible | one revolute, axis Y, ±~18-20°, beam child of base; default teeter |
| `spring_prismatic_revolute` | S4 | spring_compress (PRISMATIC Z) → beam_rock (REVOLUTE Y) | eligible if compatible | base → spring_hub PRISMATIC(Z) → beam REVOLUTE(Y); 2-link spring stack |
| `locking_pin_revolute` | S3 | L259-L270 | eligible if compatible | revolute with a visible locking-pin/axle-cap boss at the bracket; tighter range |

### Slot C：support_base （static ground support carrying the pivot）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `arched_tube_legs` | S1 | L57-L73, L131-L164 | eligible if compatible | two crossed bent-tube arches forming an A-saddle apex + axle bolt |
| `round_post_legs` | S2 | derived from S2 L95-L128 (straight tube uprights) | eligible if compatible | two splayed round-tube legs to a top cross axle (classic two-seat) |
| `triangular_A_frame` | S2 | L95-L128, L251-L264 (legs+cross brace) | eligible if compatible | A-frame triangle uprights + cross brace + axle bracket |
| `pedestal_bracket` | S3 | L64-L96 | eligible if compatible | gray cylindrical ground pedestal + black cast pivot bracket w/ bolt heads |

Optional base add-on (module-local, gated by config flag, not a separate slot):
`ground_pads` (rubber `Box` pads under feet, from variant directives) — emitted
as parent visuals on the base part when `ground_pads=True`.

## 槽位图（slot graph）

pattern: mixed (parallel-children + per-beam seat multiplicity)

```
support_base (static root part)
  └─[pivot_mechanism]─> beam_0 (beam_form)         # primary non-fixed joint(s)
        └─ for i in range(seat_count): seat_i + handle_i + (bumper_i)
  └─[pivot_mechanism]─> beam_1 (beam_form)   # only when beam_count==2 (cross/X)
        └─ for i in range(seat_count): seat_i + handle_i + (bumper_i)
```

- Cross-slot connection: `support_base` is the static parent; each beam attaches
  at the saddle/bracket apex via the chosen `pivot_mechanism`.
- For `central_revolute_teeter` / `locking_pin_revolute`: `base → beam`, single
  REVOLUTE, origin at pivot height, axis `(0,1,0)` (rotated by ±yaw for crossed
  beams), range ±TILT.
- For `spring_prismatic_revolute`: `base → spring_hub` PRISMATIC axis `(0,0,1)`
  small range, then `spring_hub → beam` REVOLUTE axis `(0,1,0)` ±TILT. The
  prismatic link is the captured-pin contact; the revolute is still the primary
  rock joint.
- Beam pivot is **always the primary non-fixed joint**; every variant has ≥1
  non-fixed joint (the beam revolute). Spring adds a 2nd non-fixed joint.
- `beam_1` is optional and only emitted when `beam_count==2`
  (mutually-exclusive with single-beam pivot mechanisms? no — both beams reuse
  the same pivot module). `pedestal_bracket` is single-beam only (it carries one
  central bracket); crossed twin beams require `arched_tube_legs` /
  `round_post_legs` / `triangular_A_frame` (two stacked axle heights). See
  compatibility matrix.

## 每槽位 Module Emits / Interfaces

### Slot A / beam_form (each module)
| emits | 描述 | 来源 |
|---|---|---|
| parts | one beam `part` (`beam_{b}`) carrying beam body + pivot hub/sleeve/stub | S1 L168-L183 / S2 L195-L230 / S3 L103-L141 |
| seat fittings | per-seat `seat_{i}` plate + `handle_{i}` (T-bar / grab-handle / grip plate) + optional `bumper_{i}` | S1 L194-L220 / S2 L218-L229 / S3 L168-L257 |
| internal joints | none within beam by default; seat/handle are parent visuals on the beam part | S1, S2, S3 |
| upstream interface | pivot sleeve/stub/hub at beam-local origin, captured by base axle | S1 L170-L175 / S2 L171-L178 / S3 L136-L141 |
| downstream interface | seat plates at beam ends (the riders' contact plane) | S1 L196-L201 |

### Slot B / pivot_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | (spring variant) extra `spring_hub_{b}` part with coil-spring visual | S4 spring_hub |
| internal joints | REVOLUTE beam pivot (axis Y, ±TILT); spring variant adds PRISMATIC(Z) below | S1 L222-L231 / S4 spring_compress+beam_rock |
| upstream interface | axle bolt / bracket / spring hub at base apex | S1 L148-L164 / S3 L78-L96 |
| downstream interface | beam pivot sleeve seated on axle | S1 L242-L256 |

### Slot C / support_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | one static `base` part (legs/arches/pedestal + axle/bracket) | S1 L131-L164 / S3 L64-L96 |
| internal joints | none (static) | — |
| upstream interface | feet on ground plane (z≈0) | S1 L307-L310 |
| downstream interface | axle/bracket at pivot height = parent of beam joint | S1 L148-L154 / S3 L71-L76 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `beam_form` | enum | 5 modules above | flat_plank_beam | choice | procedural sampler | Slot A |
| `pivot_mechanism` | enum | 3 modules above | central_revolute_teeter | choice | procedural sampler; gated by beam_form | Slot B |
| `support_base` | enum | 4 modules above | arched_tube_legs | choice | procedural sampler; gated by beam_count | Slot C |
| `beam_count` | int | {1, 2} | 1 | conditional | 2 only when base ∈ {arched,round,triangular} | S2 |
| `seat_count` | int | {2, 4, 6} | 2 | choice (weighted) | per-beam seat multiplicity (§8) | S1/S2 |
| `ground_pads` | bool | {T, F} | F | independent | cosmetic base add-on | variant directive |
| `beam_length` | float | [2.0, 3.2] | 2.8 | independent | clamp; sampled per asset | S1 L32, S3 L31 |
| `pivot_z` | float | [0.30, 0.85] | 0.60 | independent | clamp; base height | S1 L35 / S3 L26 |
| `tilt` | float | [0.26, 0.40] rad | 0.33 | independent | revolute ±range (~15-23°) | S1 L54 / S3 L33 |
| `seat_drop` | float | derived | — | equation | `= f(pivot_z)`; seats kept above ground | S1 |
| `asym_offset` | float | [0.0, 0.10] | 0.0 | independent | per-end seat z asymmetry (asymmetric form) | variant directive |
| (—) | constraint | — | — | inequality | full-tilt: every beam end stays above ground (`pivot_z·... ≥ clearance`); shorten reach or reduce tilt if violated | clearance |
| (—) | constraint | — | — | conditional | `seat_count` placement spacing along beam ≤ half-length; collapses to 2 if beam too short | S2 |

Continuous-scale sampling contract: sample `beam_length`, `pivot_z`, `tilt`,
`asym_offset` (independent, clamped) → derive `seat_drop` from `pivot_z` →
project with the ground-clearance inequality (reduce tilt / shorten reach) →
resolve `seat_count`/`beam_count` conditionals against the chosen base.

## Multiplicity / Copy Logic

Two multiplicity axes:

### Axis 1 — `seat_count` (seats per beam)
- `count_param`: `seat_count`
- `N_range`: product domain `{2, 4, 6}` (2 = one rider per end, 4/6 = multiple
  riders side-by-side per end as in four-seat tube seesaws). Test domain favors 2.
- sampling domain (weighted): 2 → ~0.70, 4 → ~0.22, 6 → ~0.08 (small-N heavy).
- copied object: per seat `i` emit `seat_{i}` plate + `handle_{i}` + optional
  `bumper_{i}`, placed symmetrically: half the seats at the +X end, half at the
  −X end, fanned across the beam width (Y) when >2.
- naming: `seat_{i}`, `handle_{i}`, `bumper_{i}` (i = 0..seat_count-1).
- placement: pair up ends; lateral fan offset `dy` across beam width for the
  extra seats; longitudinal `±SEAT_X` from pivot.
- joint policy: seats/handles are **parent visuals on the beam part** (they
  rock with the beam); no per-seat joint by default. The beam revolute is the
  shared articulation. (Optional backrest/footrest joints are out of scope v1.)
- source/gating: S2 L194-L229 (per-end loop); clamp to 2 if `beam_length` too
  short to fit the fan.

### Axis 2 — `beam_count` (independent rocking beams)
- `count_param`: `beam_count`
- `N_range`: `{1, 2}` (2 = crossed shallow-X four/multi-seat form).
- sampling domain: 1 → ~0.70, 2 → ~0.30.
- copied object: per beam `b` emit `beam_{b}` part + its pivot mechanism + its
  seat loop.
- naming: `beam_{b}`, joints `beam_{b}_pivot` (+ `beam_{b}_spring` for spring).
- placement: beam 0 at yaw 0 (or +yaw), beam 1 at −yaw, stacked pivot heights
  so the beams clear each other (S2 high/low arch).
- joint policy: each beam its own independent revolute (+ optional spring
  prismatic). Both are non-fixed.
- source/gating: S2 (two independent beams). Only allowed when base carries two
  axle heights (`pedestal_bracket` forces `beam_count=1`).

## 拓扑多样性审计

总组合数 (topology-distinct, ignoring continuous scale):
beam_form (5) × pivot_mechanism (3) × support_base (4) × seat_count (3) ×
beam_count (2) = **360** nominal; after compatibility gating
(pedestal_bracket ⇒ beam_count=1 only; spring stack only with single beam)
the legal space is still well over **100** distinct topology classes.

理由：even ignoring continuous params, 5×3×4 = 60 base combos before the two
multiplicity axes; `slot_choices_for_seed` records beam_form, pivot_mechanism,
support_base, beam_count, seat_count and per-beam recipe, so distinct slot
signatures over seeds 0-9 already exceed 10, and over 0-49 / 0-999 far exceed it.

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` seeds a
`random.Random`, weighted-draws beam_form / pivot_mechanism / support_base /
beam_count / seat_count, samples continuous scales, then `resolve_config`
applies compatibility gating + clamps. `seed=0` is not special (it draws a
clean default-ish plank teeter). No regression overrides initially.
Topology target：1000-seed slot choice tuple distinct expected 按 ≥300 report-only 口径观察.
Controlled local parameterization：`beam_length` [2.0,3.2] independent;
`pivot_z` [0.30,0.85] independent; `tilt` [0.26,0.40] independent;
`asym_offset` [0,0.10] independent; `seat_drop` = equation(pivot_z);
ground-clearance inequality reduces tilt/reach; `seat_count` spacing is a
conditional on beam_length. All resolved in `resolve_config`; none changes the
declared slot topology or breaks the pivot interface.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted slot draws + 2 multiplicity axes, then resolve_config gating | slot_choices_for_seed matches build choices |
| compatibility matrix | pedestal_bracket ⇒ beam_count=1; spring_prismatic_revolute ⇒ beam_count=1 (single central spring stack); curved_banana_beam ⇒ base ∈ {pedestal_bracket, arched_tube_legs}; seat_count clamps to 2 if beam too short | no floating, no ground penetration at full tilt, single shared pivot axis, correct max multiplicity |
| controlled local variation | beam_length / pivot_z / tilt / asym_offset clamped; seat_drop derived | proportions vary, seats stay above ground, pivot interface intact |
| regression overrides | none initially | — |
| random sweep | seeds 0-9 initial pass, 0-49 stabilization, 0-999 maturity | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A beam_form | 5 | yes | yes | |
| B pivot_mechanism | 3 | yes | yes | |
| C support_base | 4 | yes | yes | |
| seat_count (mult) | 3 | yes | yes | {2,4,6} |
| beam_count (mult) | 2 | yes | no | {1,2} |

## Validator

- `slot_choices_for_seed` returns implemented module names
- `config_from_seed` uses deterministic procedural sampling for all seeds
- compatibility gating prevents illegal combos (pedestal+twin-beam, spring+twin)
- every variant has ≥1 non-fixed joint (beam revolute is primary)
- the beam pivot is REVOLUTE, axis horizontal (Y, or yaw-rotated), ±tilt range
- spring variant adds a PRISMATIC(Z) joint below the beam revolute
- base feet rest on the ground (z≈0); base part is static
- rocking one beam swaps its two end seats' heights; the other beam holds still
- copied seats/handles follow `seat_{i}` / `handle_{i}` naming + symmetric placement
- captured pivot overlaps declared with element-scoped `allow_overlap`
- continuous scales clamped/derived in `resolve_config`, not failing in builder

## Reject cases

- Beam pivot modeled as fixed / decorative (no real rock joint).
- Seats that do not swap height when the beam rocks.
- Base not grounded, or base moves when posed.
- Twin crossed beams on a single central pedestal bracket (geometrically wrong).
- Spring "compression" with no prismatic joint (purely visual coil).
- Seat fan so wide it overhangs past the beam ends or collides at full tilt.
- Beam dipping below ground at full tilt.
- seat_count not producing `seat_{i}` parts/visuals symmetrically.

## 与相邻类别的边界

- 不该混入：`playground_swing`（座椅吊在头顶横梁上摆动，不绕中央支点跷动；本类无头顶框架）。
- 不该混入：spring rider / bouncy animal（单人单弹簧上下弹跳，没有跨支点对座平衡）。
- 不该混入：bench / plank seat（无关节、不跷动；本类必须有真实 beam 旋转关节）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | combinatorial fork pool read via approved fast path; 3 parents read in full |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | flat_plank_beam, central_revolute, arched_tube_legs | rec_model-a-vintage-...-152f9b4a | L32-L231 | plank beam, arched base, central teeter, seat+handle+bumper |
| S2 | A/C, mult | tube_truss_beam, round/triangular legs, twin-beam + seat fan | rec_model-a-four-seat-...-2c2b677d | L95-L290 | truss beam, splayed legs, beam_count=2, seat_count loop |
| S3 | A/B/C | curved_banana_beam, locking_pin_revolute, pedestal_bracket | rec_model-a-modern-commercial-...-c240aa26 | L26-L270 | banana beam, pedestal+bracket, clamp-collar drop-tube seats |
| S4 | B | spring_prismatic_revolute | rec_qwen_seesaw_001_v02 / _v05 | spring_hub + spring_compress(PRISMATIC) + beam_rock(REVOLUTE) | central coil-spring prismatic stack below the beam revolute |

## 模板实现备注（可选）

- Shared helpers: `_add_tube(part, name, start, end, r, mat)` (segment pose),
  `_mat`, per-seat fan placement helper. Reuse the swing template's tube helper.
- Captured-pin overlaps: beam pivot sleeve ↔ base axle, and spring_hub ↔ bracket
  need element-scoped `allow_overlap` in `run_seesaw_tests`.
- Twin-beam variants reuse the single-beam build per beam with a yaw + stacked
  pivot height; gate against `pedestal_bracket`.
- Spring variant uses an extra `spring_hub_{b}` part between base and beam.
