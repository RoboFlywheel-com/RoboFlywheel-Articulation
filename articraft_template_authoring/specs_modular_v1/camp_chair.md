# camp_chair — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `camp_chair` |
| template path | `agent/templates/camp_chair.py` |
| test path (optional) | `tests/agent/test_camp_chair_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: every subsystem parents to a single `chair_frame` root (parallel_children — the folding scissor braces, footrest, armrests, reclining back, swivel riser are all children of the frame), and a seat-cell multiplicity axis (`seat_cells`, bench/loveseat) copies the seat bay + one folding brace per bay.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | all 16 ids in `spec5star/camp_chair.txt` (2 origin anchors A/B + 14 forks/probe) |
| source_index_policy | only adopted module sources are indexed in the slot tables below |

Two source families:
- **Origin B family** (`chair_frame` root part carrying all tube/fabric/hardware `visual(...)`; 3 scissor-brace children `front_cross_brace`, `side_cross_brace_0/1` REVOLUTE; helpers `_tube_pose`/`_add_tube`/`_add_ball`/`_add_box` → `Cylinder`/`Sphere`/`Box`). Records: origin B, director_frame, low_pole_hub, rocker_base, bar_height, butterfly_sling, moon_saucer, swivel_seat, recline_back, xframe_stool, bench_multi, tripod_stool. This is the template's structural spine (proven, robust primitives; 12/16 sources share it).
- **Origin A family** (`base_frame` bent-tube `tube_from_spline_points` mesh scaffold + `_fabric_panel_geometry` sagged cloth meshes + REVOLUTE footrest/armrests/scissor legs). Records: origin A, flat_cot_lounger, zero_gravity, probe_full_recliner. Adopted for the **sling/lounge form families** (`_fabric_panel_geometry` mesh preserved, not downgraded) and the **reclining-footrest / hinged-armrest motions**.

## 核心身份

A **camp chair** is a portable, foldable/packable outdoor seat: a fabric-or-sling seating surface tensioned on a collapsible tube/pole frame with at least one real non-fixed folding/reclining/swivel joint. Default mature domain spans the high-back padded quad-fold armchair (origin B), the fabric-sling reclining lounge with footrest (origin A), the round moon/saucer bucket, the flat chaise/cot lounger, and the backless X-frame stool. Every seed keeps the folding scissor braces (the guaranteed articulated mechanism) plus, per motion slot, a reclining footrest / hinged fabric arms / back-recline hinge / 360° swivel seat.

Must NOT drift into: rigid indoor dining/office chairs, gas-lift/5-star-base task chairs, wheeled or powered-recliner chairs, patio glider benches, camp cots with no chair mode, hammocks, picnic tables (see §11).

## 槽位 + 候选模块表

### Slot A：form_family （③ 主体形态家族 — 主多样性槽）
seat/back/arm envelope emitted onto the seat host part (frame, or a swivel/recline child).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `high_back_armchair` | origin_anchor | origin B | L131-L171 (seat sling boxes + tall padded back panels + arm pads) | eligible if compatible | Box padded seat + tall padded back (`seat_gray_center`,`back_gray_center`,side panels,pillow); **Volumetric Envelope Form** (thick padded boxy seat+back) |
| `recliner_lounge` | origin_anchor | origin A | L205-L275 (`_fabric_panel_geometry` seat+back+accent+headband meshes) | eligible if compatible | sagged cloth **mesh** sling seat + leaning back panel + orange accent bands; **Planar Boundary Form** (thin sagged bilinear sheets) |
| `moon_saucer_bowl` | forked_anchor | rec_camp_chair_var_moon_saucer | L115-L179 (`TorusGeometry` rim + `LatheGeometry.from_shell_profiles` deep bowl) | eligible if compatible | round tubular rim + deep concave lathe bucket sling; **Macro Surface Construction** (revolved bowl replaces rectilinear seat/back read) |
| `flat_cot_lounger` | forked_anchor | rec_camp_chair_var_flat_cot_lounger | L157-L290 (near-coplanar seat/back/footrest fabric panels) | eligible if compatible | near-horizontal chaise: low-angle seat+back+footrest sheets; **Planar Boundary Form** (coplanar bed-like planes) |
| `backless_stool` | forked_anchor | rec_camp_chair_var_xframe_stool | L130-L134 (`seat_gray_center` only, no back_/arm_ visuals) | eligible if compatible | seat sling only, no back posts/panel; **Planar Boundary Form** (single seat plane) |

Six-axis note: this slot is the required **③ Primary Form Family slot registered into `slot_choices`** (form-dominated 小类). 5 recognizable prototypes covering Planar Boundary (recliner_lounge, flat_cot, backless), Volumetric Envelope (high_back_armchair) and Macro Surface Construction (moon_saucer). ≥3 satisfied.

### Slot B：base_stance （① 支撑结构 / ⑤ 座高比例）
foot/base structure + seat-height on the frame root.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pad_feet` | origin_anchor | origin B | L83-L95 (4 `Box` rubber pad feet + rivets) | eligible if compatible | 4 pad feet under upright legs; standard seat height (seat_z≈0.46) |
| `rocker_runners` | forked_anchor | rec_camp_chair_var_rocker_base | L86-L119 (2 curved `tube_from_spline_points` runner rails replace feet) | eligible if compatible | 2 fore-aft curved runner rails (mesh) instead of 4 feet; glider base |
| `bar_height_rail` | forked_anchor | rec_camp_chair_var_bar_height | L101-L105 (`foot_rest_rail` + collar tubes, elongated legs) | eligible if compatible | tall legs (seat_z≈0.60) + a front foot rail with collars |
| `low_compact` | forked_anchor | rec_camp_chair_var_low_pole_hub | L70-L140 (short low frame) | eligible if compatible | short legs, low compact seat (seat_z≈0.34) backpacking stance |

### Slot C：motion （② 关节类型 — 折叠+舒适机构）
Always emits the scissor fold braces (REVOLUTE, the guaranteed non-FIXED joint); each candidate adds ONE extra mechanism (or none).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `scissor_fold` | origin_anchor | origin B | L174-L218 (front + 2 side scissor-brace children) + articulations L192-L218 | eligible (all forms) | 3 REVOLUTE scissor braces only (front axis +Y, side axes ±X) |
| `reclining_footrest` | origin_anchor | origin A | footrest child `base_to_footrest` REVOLUTE, L385-L416 | eligible: armchair/recliner_lounge/flat_cot | + `footrest_panel` REVOLUTE about lateral X at seat front (lift/fold); side-folds (front brace dropped) |
| `hinged_armrests` | origin_anchor | origin A | L/R `base_to_*_armrest` REVOLUTE, L320-L341 | eligible: armchair/recliner_lounge | + L/R `armrest` REVOLUTE about lateral X fold-up fabric arms |
| `back_recline` | forked_anchor | rec_camp_chair_var_recline_back | `back_recliner` child + `frame_to_recline_back` REVOLUTE, L173-L244 | eligible: armchair | back posts+panel move to `back_recliner` REVOLUTE about lateral X (rearward recline) |
| `swivel_riser` | forked_anchor | rec_camp_chair_var_swivel_seat | `seat_swivel` child + `base_to_swivel` CONTINUOUS +Z, L168-L331 | eligible: backless_stool | seat platform on `seat_swivel` CONTINUOUS +Z turntable (restricted to the compact backless seat so it clears the fixed legs when turning; armchair/moon deferred to avoid a frame-sized platform striking the legs) |

Every candidate in every slot is structurally distinct (part tree / joint topology / primitive family), not a re-skin. No single-candidate slot. Colorway/stitching are NOT candidates (⑥/④ audit-only, ride along via `palette_style`).

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                         chair_frame (root: legs + seat rails + pivot hardware + feet/runners/rail)
   ├─[REVOLUTE +Y  @front pivot ~z=0.65·seat_z]──> front_cross_brace          (scissor_fold, always; × N bays for bench)
   ├─[REVOLUTE +X  @left  side pivot]───────────> side_cross_brace_0          (scissor_fold, always)
   ├─[REVOLUTE −X  @right side pivot]───────────> side_cross_brace_1          (scissor_fold, always)
   ├─[REVOLUTE −Y  @seat-front hinge]──────────> footrest_panel              (motion=reclining_footrest)
   ├─[REVOLUTE ±Y  @rear-post hinge]──────────> {left,right}_armrest         (motion=hinged_armrests)
   ├─[REVOLUTE −Y  @recline hinge z≈seat_z+0.05]> back_recliner (hosts back)  (motion=back_recline)
   └─[CONTINUOUS +Z @seat center]─────────────> seat_swivel   (hosts seat+back) (motion=swivel_riser)
```

- Slot order (resolve): base_stance → form_family → motion → seat_cells. base_stance sets `seat_z`/foot structure; form_family reads `seat_z` and the motion routing to know its host part (frame vs seat_swivel vs back on back_recliner); motion adds children; seat_cells copies bays.
- Cross-slot connection points: all children parent to `chair_frame` (parallel). Joint origins sit on real frame hardware (scissor pivot pins, seat-front hinge tube, rear-post hinge, seat-center hub) — see §6.
- Every non-FIXED joint is a captured pin-through-sleeve / turntable pivot: `MatingContract` cannot express two axis-aligned faces, so joints are **grandfathered** (omit `mating=`) with element-scoped `allow_overlap` + `expect_overlap` mirroring each source's `run_tests` (identical pattern to `Healthcare_Wheelchair`).
- Mutual exclusion / gating: motion is gated by form (table above); `back_recline`/`hinged_armrests` need a back/arm-bearing form; `swivel_riser` reroutes seat host; `seat_cells`>1 only for high_back_armchair + pad_feet + scissor_fold.

## 每槽位 Module Emits / Interfaces

### Slot A / form_family
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (visuals only) — seat/back/arm envelope as `.visual(...)` on the host part (frame, or seat_swivel, or back on back_recliner) | origin B L131-171 / origin A L205-275 |
| internal joints | none | — |
| upstream interface | host part = frame (default) / seat_swivel (swivel) / back on back_recliner (back_recline); seat_z from base_stance | swivel_seat L168-267 |
| downstream interface | seat top face (informational) for footrest/arm hinge placement | — |

### Slot B / base_stance
| emits | 描述 | 来源 |
|---|---|---|
| parts | none — feet/runners/rail as frame `.visual(...)` | origin B L83-95 |
| internal joints | none | — |
| upstream interface | sets `seat_z`, `leg_bottom_z`, foot structure on `chair_frame` root | rocker L86-119 / bar L101-105 |
| downstream interface | frame lower structure (leg tops at seat_z) consumed by braces + seat | — |

### Slot C / motion
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_cross_brace`, `side_cross_brace_0/1` (always) + optional `footrest_panel` / `{l,r}_armrest` / `back_recliner` / `seat_swivel` | origin B L174-218 / origin A / recline L173-244 / swivel L168-331 |
| internal joints | 3× scissor REVOLUTE (always) + one of: footrest REVOLUTE −Y / arm REVOLUTE ±Y / recline REVOLUTE −Y / swivel CONTINUOUS +Z | see slot table |
| upstream interface | parents to `chair_frame`; joint origins on frame pivot hardware | origin B L192-218 |
| downstream interface | moving child (carries its own decoration visuals; nothing chains below) | — |

不动细节（cup holder ring, side pocket mesh, piping/stitch/logo bands, rivets, pillow bolster, foot pads）都是宿主 part 的 `.visual(...)`，不是 FIXED-jointed part（Rule 1）。本模板**没有任何 FIXED articulation**——每个 child 都是真正会动的关节。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `form_family` | enum | 5 modules (Slot A) | high_back_armchair | choice | procedural sampler | Slot A table |
| `base_stance` | enum | 4 modules (Slot B) | pad_feet | choice | procedural sampler | Slot B table |
| `motion` | enum | 5 modules (Slot C) | scissor_fold | conditional | sampled from form's allowed set | Slot C table |
| `seat_cells` | int (mult.) | {1,2,3} | 1 | conditional | >1 only if armchair+pad_feet+scissor_fold, else 1; weighted N1≫N2>N3 | bench_multi L61-273 |
| `palette_style` | enum | 6 colorways (see §8.5 ⑥) | black_orange_oxford | choice | rng.choice(PALETTE_STYLES) | origins + companion forks |
| `seat_z` | float | derived {low 0.34, pad 0.46, rocker 0.46, bar 0.60} | 0.46 | equation | `= f(base_stance)` | stance sources |
| `seat_width_scale` | float | [0.92, 1.08] | 1.0 | independent | uniform sample then clamp | proportion ⑤ |
| `back_height_scale` | float | [0.92, 1.12] | 1.0 | independent | uniform sample then clamp | proportion ⑤ |
| `track_scale` | float | [0.94, 1.06] | 1.0 | independent | scales left_x/right_x & rail widths | proportion ⑤ |
| (—) | constraint | — | — | inequality | scissor pivot_z = 0.65·seat_z, brace_half_z = 0.49·seat_z so brace bottom ≥ 0.02 and top ≤ seat_z·1.15 (folds clear); violated → clamp seat_z | fold clearance |
| (—) | constraint | — | — | conditional | motion allowed-set resolved from form before sampling seat_cells | §9 |

所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解；builder 不再失败。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤14 s/seed**（典型 5–12 s）。依据：库内实测参考典型模板 5–20 s；本类主体是 `Cylinder`/`Box`/`Sphere` 图元 + 少量 mesh（每个 form 至多一张 sagged-panel mesh，moon_saucer 一张 Torus + 一张 shell Lathe）。分档 tessellation：tube/round 小特征 `radial_segments ≤ 16`，Torus/Lathe 英雄面 `segments ≤ 56`；`_fabric_panel_geometry` nx≤8/ny≤6；N 个相同 brace 复用同一构造 helper。sweep `--compile-timeout 120` 作看门狗（≈3× 上限）。超预算先降精度再迭代。

## Multiplicity / Copy Logic

The `seat_cells` bench-copy machinery is implemented (`_bay_offsets` / `_bay_tag` / per-bay
`front_cross_brace_{i}`), but both template-level copy axes are **DECLARED-BUT-NOT-SAMPLED** in
v1 to keep the fold/support spine robust; each is documented with its deferral reason below.

**Axis 1 — `seat_cells` (bench / loveseat), source `rec_camp_chair_var_bench_multi`.**
- `count_param` = `seat_cells`; product domain [1,3]; copied object = one seat bay {seat pan + sling
  boxes + per-bay `front_cross_brace_{i}` REVOLUTE}, gated to `high_back_armchair + pad_feet +
  scissor_fold`.
- **Deferral reason:** the faithful loveseat tiles seats along the seat-front (widening the frame);
  a correct wide-frame layout needs the seat-rail / side-brace / per-bay-pivot geometry re-solved so
  every bay is supported without islands, which was not stably reachable in v1. `config_from_seed`
  pins `seat_cells=1`; the code path stays so a v2 can enable it after the wide-frame rework.

**Axis 2 — leg count (tripod N=3 vs quad N=4), source `rec_camp_chair_var_tripod_stool`.**
- **Deferral reason:** the quad 4-leg + scissor-brace spine is the shared mature topology across
  12/16 sources; the tripod radial-fold replaces scissor braces with a disjoint radial-tangent
  leg-fold mechanism that does not share the scissor-fold motion spine (AUTHORING §C: split the slug).
  Left for a dedicated `camp_stool_tripod` slug. Quad (N=4) is the sole realized leg count.

Net: v1 has **no active template-level copy axis** (both considered, both deferred with reasons above);
core structural diversity is carried by the discrete form_family(③) + motion(②/①) + base_stance(①/⑤) slots.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | motion slot adds/removes moving children (0 extra → scissor_fold; +footrest / +2 arms / +back_recliner / +seat_swivel) → distinct part-joint graphs; seat_cells adds +1 brace child per bay. source-backed: origin B / origin A / recline_back / swivel_seat / bench_multi. |
| └ multiplicity | 同构件 ×N | 考察-无(deferred) | Both copy axes (`seat_cells` bench, leg-count tripod) declared-but-not-sampled in v1 with reasons — see §8. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE +Y/−Y/±X (scissor + footrest + arms + recline) and CONTINUOUS +Z (swivel). All source-backed (origin A/B, recline_back, swivel_seat). Every declared type appears in sweep (armchair reaches all). |
| ③ 主体形态家族 | 换核心几何原型 | 有 | 5 prototypes (Slot A): high_back_armchair (Volumetric Envelope), recliner_lounge & flat_cot & backless (Planar Boundary), moon_saucer (Macro Surface Construction). source-backed anchors + forks; registered in `slot_choices`. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only + world_knowledge_extrapolation) | orange piping bands + white contrast stitch rails + brand logo/text patch (origin B) / black edge piping + light stitch + orange accent+toe bands (origin A) / rim binding (moon_saucer). Host-conformal: emitted as host `.visual(...)` derived from the seat/back face they sit on, following ③/⑤ (derive order ③→⑤→④). Decoration count rides `palette_style`. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | seat_z {0.34–0.60}, seat_width_scale [0.92,1.08], back_height_scale [0.92,1.12], track_scale [0.94,1.06]. **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): scissor front REVOLUTE +Y [0, 0.45]; scissor side REVOLUTE ±X [0, 0.45]; footrest REVOLUTE lateral −X [0, 0.9] (lift up); armrest REVOLUTE lateral −X [0, 0.9] (fold-up); back_recline REVOLUTE lateral −X [0, 0.55] (rearward+down); swivel CONTINUOUS +Z full turn. `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)` + one targeted `ctx.pose(...)` per mechanism (fold changes brace AABB; footrest lifts +Z; arm folds up; back reclines rearward/down; swivel changes footprint). No sampled-pose exemption needed. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes fabric + metal (powder-coat tube) + plastic (feet/pivots) + painted-accent; ≥6 colorways: black_orange_oxford (B), brown_orange_sling (A), teal_navy_bowl, olive_canvas, blue_red_ripstop, grey_powder (companion forks). Material-class coverage ≥ ceil(0.5×6)=3 (fabric/metal/plastic all present every seed). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——5 个 form 拉得开、fabric/metal/plastic 材质都出现、piping/stitch 贴合座面不悬空、scissor/footrest/arm/recline/swivel 关节全程不穿模。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- form(5) × stance(4) × motion(form-gated: armchair 5 / recliner_lounge 3 / moon 2 / flat_cot 2 / backless 2) → per-form (5·4 + 3·4 + 2·4 + 2·4 + 2·4) = 20+12+8+8+8 = **56 (form,stance,motion) combos**, × seat_cells{1,2,3} on the armchair/pad/scissor cell (+2) → **≈58 distinct slot tuples**, × 6 palette_style × continuous scales → topology target easily >300 over 1000 seeds. report-only.

理由：多样性主要来自离散 form_family(③) + motion(②/①) + base_stance(①/⑤) + seat_cells(mult) 槽；连续 scale 仅做 clamp/derive，不撑多样性。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；先 `base_stance` → derive seat_z；`form_family`；`motion` = rng.choice(ALLOWED_MOTIONS[form])；`seat_cells` weighted then gated; `palette_style`; continuous scales uniform then clamp in `resolve_config`. Compatibility matrix = ALLOWED_MOTIONS dict + seat_cells gate (prevents illegal moon-saucer-recline / bench-rocker etc.). No regression overrides (procedural covers seed 0).
Topology target：≥300 over 1000-seed slot tuples (report-only, not a gate).
Controlled local parameterization：seat_width_scale, back_height_scale, track_scale (continuous), all clamped in `resolve_config`; they never break the scissor pivot clearance inequality (pivot_z & brace_half_z derive from seat_z) or the captured-pin allowances.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | stance→seat_z, form, form-gated motion, gated seat_cells, palette, scales | slot_choices_for_seed matches build choices |
| compatibility matrix | ALLOWED_MOTIONS[form] + seat_cells gate; fallback → scissor_fold / N=1 | no floating, collision, axis, closed-pose, bulky-bench failures |
| controlled local variation | seat_z/width/height/track scales, clamped | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| form_family | 5 | yes | yes | ③ primary form slot |
| base_stance | 4 | yes | yes | ①/⑤ |
| motion | 5 | yes | yes | ② (some form-gated) |
| seat_cells (mult) | N∈{1,2,3} | yes | — | source bench_multi |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (form_family, base_stance, motion, seat_cells)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix (ALLOWED_MOTIONS + seat_cells gate) prevents illegal combos in `resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped in `resolve_config`; seat_z-derived pivot/brace keep folds clear
- every non-FIXED joint is a captured pivot with element-scoped `allow_overlap` + `expect_overlap`; no MatingContract phantom anchors; no FIXED-jointed decoration parts
- key joints have expected type/axis/range (scissor REVOLUTE ±X/+Y; footrest/arm/recline REVOLUTE; swivel CONTINUOUS +Z)
- copied bench objects follow `seat_cell_{i}` / `front_cross_brace_{i}` naming + +Y tiling
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per mechanism

## Reject cases
- A form with a back panel but no rear posts / a back that floats above the seat (isolated island).
- Scissor brace whose folded pose (upper) drives it through the seat/back or the neighbor brace (穿模).
- Footrest/armrest/recline hinge origin off the frame hardware (>15mm) → articulation-origin fail.
- swivel_riser seat platform that doesn't rotate its footprint (dead joint) or collides the base X-frame mid-turn.
- moon_saucer bowl sling floating inside the rim without a support/contact path.
- bench seat_cells copied without a per-bay brace or divider leg → isolated bays / unsupported spans.
- Downgrading `_fabric_panel_geometry` / `LatheGeometry` / `TorusGeometry` heroes to flat `Box` (Rule 3).
- Monochrome output (palette_style not driving `.visual(material=...)`).

## 与相邻类别的边界
- 不该混入：office/task chair、gas-lift 5-star-base chair（有升降柱/星形轮座，非折叠管架 — neighbor drift）。
- 不该混入：wheelchair / wheeled chair（有行走大轮 + caster，属 Healthcare_Wheelchair）。
- 不该混入：patio glider bench / rigid dining chair（不可折叠、无 sling）。
- 不该混入：camp cot / hammock（纯卧具，无 chair 折叠机构）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Origin-B tube-primitive spine (12/16 sources) + origin-A fabric-panel mesh forms; tripod radial-fold deferred to a split slug (documented §8 Axis 2). |

## 模板实现备注（可选）
- Shared helpers: `_add_tube`/`_add_ball`/`_add_box` (origin B) + `_fabric_panel` (origin A `_fabric_panel_geometry`); one `_scissor_brace_meshes` builder reused for every bay (bench).
- Captured-pin element-scoped `allow_overlap`: scissor pivot pin↔collar + rivet↔collar/moving_tube (origin B run_tests); footrest/arm/recline hinge tube↔barrel; swivel hub↔collar + base_xframe↔spokes (swivel_seat run_tests).
- Motion routing: `seat_host` = seat_swivel (swivel) else frame; back on `back_recliner` (back_recline) else seat_host.
