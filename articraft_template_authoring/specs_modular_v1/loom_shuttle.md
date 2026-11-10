# Modular Spec — loom_shuttle

## 元信息
| 项 | 值 |
|---|---|
| slug | `loom_shuttle` |
| template path | `agent/templates/loom_shuttle.py` |
| test path (optional) | `tests/agent/test_loom_shuttle_template.py` (not authored; sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear body → bobbin mechanism chain + optional parallel underside roller children on the body) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 origin parents + 6 verified forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

A loom shuttle is the handheld tool that carries the weft across the shed of a loom: an
**elongated wooden shuttle body with tapered/pointed ends** (length ≫ width, low height) holding a
**weft package** (bobbin / pirn / wound cotton) that **spins** so thread pays off as the shuttle
flies. The single invariant articulation is a real spinning weft package (revolute bobbin / pirn),
sometimes cantilevered (end-delivery) or carried on a hinged loading arm; industrial fly-shuttle
variants add underside race rollers. It is grip-free, base-free solid wood plus a little metal
hardware (nose tips, bearing eyelets, spindle).

Must NOT drift to: netting/tatting shuttle (net/lace tongue tool, no spinning weft), a bare
spinning-wheel/sewing bobbin with no shuttle body, or a pointed-wood visual neighbor (canoe / ski /
sled / letter-opener) with no weft package.

## 槽位 + 候选模块表

### Slot A：body_form  （③ Primary Form Family slot — carries the primary visual diversity）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `boat_hollow` | forked_anchor (origin) | rec_..._002 / rec_..._001 | 002 L69-L82, L120-L195 · 001 L49-L174 | eligible if compatible | Carved cadquery boat hull, deep enclosed rounded slot cavity, pointed ends, metal nose tips. **form_subtype = Volumetric Envelope Form** (deep carved 3D trough). |
| `flat_plank` | forked_anchor | rec_loom_shuttle_var_skeleton_flat_open | L63-L94, L127-L191 | eligible if compatible | Thin flat rectangular cadquery plank, shallow open-top channel, forked end notches; bobbin exposed. **form_subtype = Planar Boundary Form** (flat rectangular plate outline). |
| `ski_upswept` | forked_anchor | rec_loom_shuttle_var_form_ski | L57-L133, L191-L290 | eligible if compatible | Long slender cadquery ski slab, upswept pointed tips, shallow open channel. **form_subtype = Volumetric Envelope Form** (slender upswept solid, distinct from the deep boat trough). |

### Slot B：bobbin_mechanism  （② joint/mechanism slot — how the weft package is carried & spun）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `through_axle` | forked_anchor (origin) | rec_..._002 / rec_..._001 | 002 L197-L242 · 001 L228-L267 | eligible if compatible | Bobbin part = core cylinder + wound cotton + 2 flanges/bosses + red tail; single REVOLUTE about long +X, axle journaled in the two body bearing eyelets. 1 non-fixed joint. |
| `spindle_arm` | forked_anchor | rec_loom_shuttle_var_mechanism_spindle_arm | L205-L296 | eligible if compatible | Adds `spindle_arm` part hinged to body (REVOLUTE about Y at rear bearing, captured pin) that swings the pirn up for loading; bobbin re-parented onto the arm (REVOLUTE about arm X). 2 non-fixed joints, part tree depth +1. |
| `end_delivery` | forked_anchor | rec_loom_shuttle_var_mechanism_end_delivery | L71-L102, L166-L297 | eligible if compatible | Fixed cantilever `spindle_rod` (body visual) + nose tension-gate; tapered **LatheGeometry** pirn on the cantilever, supported at root only; single REVOLUTE pirn spin about +X. 1 non-fixed joint, cantilever topology. |

### Slot C：underside  （② + N — race glide, optional roller bogie with a multiplicity axis）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_race` | forked_anchor (origin baseline) | rec_..._001 / rec_..._002 | (absence of underside subtree) | eligible if compatible | Shuttle slides directly on the loom race; no underside part, no extra joint. |
| `roller_bogie` | forked_anchor | rec_loom_shuttle_var_mechanism_roller / rec_loom_shuttle_var_n_rollers4 | roller L246-L293 · n4 L197-L305 | eligible if compatible | N loop-emitted `roller_{i}` parts recessed into the keel underside, each on its own CONTINUOUS joint about transverse Y, riding on a fixed body-side axle pin (captured). N is the multiplicity axis. |

**Notes / hard-constraint compliance:**
- Every slot reaches ≥2 structurally distinct source-backed candidates (Slot A/B: 3 each; Slot C: 2,
  degraded-to-2 with reason: a shuttle is structurally minimal — the only source-backed underside
  variation is present/absent roller bogie).
- `handle_or_grip`, `support_or_base`, `surface_construction` are NOT real slots for this class (a
  shuttle is grip-free, base-free solid wood); intentionally not expanded (see source map budget).
- Size/color/decoration-only differences are folded into ④/⑤/⑥ (host-conformal visuals + palette +
  scales), not candidates.

## 槽位图（slot graph）

```
pattern: mixed

[Slot A body_form]  (root, grounded `body` part; exposes axle interface: axle_z, ±bearing_x, cavity)
      |
      | REVOLUTE(+X) bobbin spin        (through_axle: body → bobbin)
      |   OR REVOLUTE(+Y) arm hinge then REVOLUTE(+X) pirn spin  (spindle_arm: body → spindle_arm → bobbin)
      |   OR REVOLUTE(+X) cantilever pirn spin                    (end_delivery: body → bobbin)
      v
[Slot B bobbin_mechanism]  (weft package, mounted at the body's axle interface)

[Slot A body_form] --(parallel children on `body`)--> [Slot C underside]
      roller_bogie: N × CONTINUOUS(+Y) `roller_{i}` on fixed body-side axle pins (captured), keel centerline
      plain_race: no child
```

- **Slot order / parent relations:** `body` (Slot A) is the single grounded root. Slot B mounts on the
  body's shared axle interface. Slot C rollers are parallel FIXED-axle + CONTINUOUS children of `body`.
- **Cross-slot interface points:** the body exposes a canonical **axle interface** = axle height
  `axle_z`, bearing X positions `±bearing_x`, cavity floor top `cavity_floor_top_z`, keel bottom
  `keel_bottom_z`, footprint half-width. All Slot B/C geometry derives placement from these (single
  source of the shared quantities — Contract 3c), so any body form legally carries any mechanism.
- **Joint types/axes/ranges:** bobbin/pirn spin REVOLUTE about +X, `[-π, π]`; arm hinge REVOLUTE about
  +Y, `[0, arm_open]`; rollers CONTINUOUS about +Y. Bobbin/pirn journals and roller axles are captured
  pins (no clean axis-aligned face pair) → `mating` omitted, grandfathered, guarded by element-scoped
  `allow_overlap` in run_tests (mirrors cable_reel / the source records).
- **Mutual exclusion / gating:** none required — all body×mechanism×underside combos are physically
  plausible; the shared axle interface makes them all compatible.

## 每槽位 Module Emits / Interfaces

### Slot A / module boat_hollow | flat_plank | ski_upswept
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (single root) | 002 L120 / 001 L193 |
| visuals | `carved_hull` (cadquery mesh) + `cavity_floor` + metal nose tips + 2 bearing supports (`{front,rear}_bearing_saddle` box + `{front,rear}_bearing` ring) + host-conformal ④ (top holes, side eyelets, wood-grain streaks) | 002 L120-L195 / plank L127-L191 / ski L191-L290 |
| internal joints | none (all body detail is fused visuals, Rule 1) | — |
| axle interface (shared) | `axle_z`, `±bearing_x`, `cavity_floor_top_z`, `keel_bottom_z`, `half_width` derived per form | 002 L149-L161, L239 |

### Slot B / module through_axle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bobbin` | 002 L197 |
| visuals | `bobbin_core`, `cotton_thread`, `{front,rear}_flange`(+`_boss`), `red_thread` | 002 L201-L232 |
| internal joints | `body_to_bobbin` REVOLUTE +X `[-π,π]` at `(0,0,axle_z)` | 002 L234-L242 |
| support | `bobbin_core` seated on bearing saddles (contact) + rings captured (allow_overlap) | 002 L149-L161 |

### Slot B / module spindle_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spindle_arm`, `bobbin` | spindle_arm L206, L249 |
| visuals | arm: `spindle_rod`, `pivot_pin`, `pivot_collar`, `latch_hook`; body adds `front_latch_notch`; bobbin as through_axle | spindle_arm L198-L235, L254-L285 |
| internal joints | `body_to_spindle_arm` REVOLUTE +Y `[0,arm_open]` at `(bearing_x,0,axle_z)`; `spindle_arm_to_bobbin` REVOLUTE +X `[-π,π]` | spindle_arm L237-L247, L287-L296 |
| support | pivot_pin/collar captured on rear bearing (allow_overlap); latch_hook seats at front_latch_notch (contact) | spindle_arm L335-L369 |

### Slot B / module end_delivery
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bobbin` (tapered pirn); body adds cantilever hardware | end_delivery L234 |
| visuals | body: `spindle_rod`(cantilever), `spindle_collar`, `tension_gate_post`, `tension_gate_eyelet`; bobbin: LatheGeometry `bobbin_core`/`cotton_thread` + locating collars + `red_thread` | end_delivery L166-L196, L239-L286 |
| internal joints | `body_to_bobbin` REVOLUTE +X `[-π,π]` at `(≈bearing_x-0.005,0,axle_z)` | end_delivery L289-L297 |
| support | pirn bore surrounds `spindle_rod` (element-scoped allow_overlap); rear flange near rear bearing | end_delivery L337-L354 |

### Slot C / module roller_bogie
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_{i}` (i in 0..N-1) | roller L262-L281 / n4 L279-L299 |
| visuals | roller: `roller_wheel_{i}`; body adds `roller_axle_{i}` (fixed pin through wheel) | roller L266-L278 / n4 L210-L227, L283-L288 |
| internal joints | `body_to_roller_{i}` CONTINUOUS +Y at `(x_i,0,roller_z)` | roller L280-L288 / n4 L290-L298 |
| support | wheel surrounds fixed body axle pin (captured, allow_overlap) | n4 L401-L409 |

- 活动件都有 articulation 语义（bobbin/pirn spin, arm hinge, roller spin）。
- 不动细节（nose tips, eyelets, holes, grain, tension gate, latch notch, cavity floor）都是宿主 part
  visual，不作为独立 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | boat_hollow / flat_plank / ski_upswept | — | choice | deterministic procedural sampler | Slot A |
| bobbin_mechanism | enum | through_axle / spindle_arm / end_delivery | — | choice | deterministic procedural sampler | Slot B |
| underside | enum | plain_race / roller_bogie | — | choice | deterministic procedural sampler | Slot C |
| n_rollers | int | [2, 6] | 2 | conditional | only meaningful when underside=roller_bogie; weighted (small N common); clamp | roller / n4 |
| palette_style | enum | 5 colorways (honey / oiled-brown / pale-pine / dark-endgrain / steel-brass mixes) | honey_oiled | choice | palette only, no geometry | ⑥ |
| length_scale (ls) | float | [0.90, 1.15] | 1.0 | independent | scales all +X dims (body length, bearing_x, bobbin length, roller spacing); clamp | ⑤ / 002 L24 |
| bobbin_radius_scale (rs) | float | [0.94, 1.06] | 1.0 | independent | scales bobbin core/thread/flange radii; clamp | ⑤ / 002 L201-L216 |
| arm_open | float | [0.80, 1.15] rad | 1.0 | independent | spindle_arm hinge upper limit; clamp | spindle_arm L246 |
| (—) | constraint | — | — | equation | `axle_z = cavity_floor_top_z(form) + flange_radius + 0.0016`; `flange_radius = 0.0142·rs`; bearings rise to `axle_z` | clearance |
| (—) | constraint | — | — | equation | `roller_z = keel_bottom_z(form) − roller_radius + 0.001` (crown hangs below keel with a small gap) | roller clearance |
| (—) | constraint | — | — | inequality | bobbin footprint must stay within body half-width: `flange_radius ≤ half_width(form) − 0.001`; rs range chosen so this holds for all forms | expect_within |

所有 equation/inequality 在 `resolve_config` 内求解（axle_z、flange_radius、roller_z 派生），不留到 builder。

### 7.5 编译预算 / compile budget
Per-seed budget **≈ 25 s** (three cadquery hull forms + one LatheGeometry pirn; heaviest is the ski
union/fillet hull). Basis: the source records compile in ~10-20 s each. Tessellation kept cheap:
cadquery `tolerance=0.0007`, torus/cone radial ≤36, lathe segments ≤32, rollers reuse one wheel
`Cylinder`. Sweep hang-guard `--compile-timeout 120` (≈3-5×, watchdog only). If a seed exceeds ~20 s,
lower hull tessellation before iterating.

## Multiplicity / Copy Logic

- **count_param:** `n_rollers` on the `roller_bogie` underside module — the only repeated homogeneous
  part family in this class (the shuttle body + single weft package are inherently singular).
- **N_range:** `[2, 6]` (product domain); sampling domain = weighted, small N high-frequency
  (`weight ∝ 1/(1+|n-2|)` biasing toward 2-4), tail (5-6) rare. Test range exercises N=2..6.
- **N samples (source-backed via fork):** 2 (rec_loom_shuttle_var_mechanism_roller), 4
  (rec_loom_shuttle_var_n_rollers4).
- **copied object:** `roller_{i}` part + body-side `roller_axle_{i}` pin, loop-emitted via one shared
  `_emit_roller` helper; identical wheel geometry.
- **naming:** stable indexed `roller_{i}` / `roller_wheel_{i}` / `roller_axle_{i}` / `body_to_roller_{i}`.
- **placement:** equal spacing along the keel centerline (X), symmetric about x=0, crown proud below keel.
- **joint policy:** each roller its own `body_to_roller_{i}` CONTINUOUS joint about transverse +Y.
- Encoded into `slot_choices` as `("roller_n", "n{N}")` (or `"n0"` when plain_race) so
  `axis_realization` shows ≥2 realized counts. Decorative repeats (holes, grain, thread bands) are ④,
  not multiplicity.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Body is 1 part; **spindle_arm** adds a part + hinge edge (depth +1); **roller_bogie** adds N roller parts + N joint edges; **end_delivery** cantilever removes the far support. source-backed (origin + 4 forks). |
| └ multiplicity | 同构件 ×N | 有 | `n_rollers` ∈ [2,6], weighted small-N; see §8. forked (roller N2, n4). |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE +X (bobbin/pirn spin) · REVOLUTE +Y (arm hinge) · CONTINUOUS +Y (rollers). source-backed; each type realized in the sweep (through_axle/end_delivery=REVOLUTE, spindle_arm adds +Y REVOLUTE, roller_bogie adds CONTINUOUS). |
| ③ 主体形态家族 | 换核心 part 的可识别几何形态原型 | 有 | body_form slot登记进 `slot_choices`: `boat_hollow` (Volumetric Envelope — deep carved trough) · `flat_plank` (Planar Boundary — flat plate) · `ski_upswept` (Volumetric Envelope — slender upswept solid). 3 recognizable prototypes, all forked_anchor. |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 (record_only / world_knowledge_extrapolation) | Drilled top holes, side eyelets, wood-grain streaks, end-grain patches, brand-stamp-free worn wood, red thread tail — all **host part visuals** placed on the final hull top/flank surface (derive order ③→⑤→④), never separate parts. Count varies mildly per form. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 (record_only) | length_scale [0.90,1.15], bobbin_radius_scale [0.94,1.06], arm_open [0.80,1.15]. Motion envelopes: bobbin/pirn REVOLUTE +X [-π,π] (full spin, tested via off-axis red_thread displacement); arm hinge REVOLUTE +Y [0,arm_open] (lifts pirn up, tested by bobbin z-rise); rollers CONTINUOUS +Y (spin-in-place). `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)` + one targeted `ctx.pose(...)` per mechanism (bobbin spin, arm lift, roller spin). No sampled-pose exemption. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palettes covering wood tone (honey / oiled-brown / pale-pine) + weft (cream/aged) + metal (steel/brass) hardware. Material classes: painted/worn wood + metal (steel, brass) — ≥2 大类 ≥ ceil(0.5×5)=3 colorways cover it. |

**收尾自检:** each body_form prototype, mechanism, roller count, palette must be visibly distinct in
the 0-9 seed renders; decoration hugs the hull; no closed-pose or mid-travel 穿模.

## 采样与覆盖审计

总组合数：body_form(3) × bobbin_mechanism(3) × underside(2) = 18 topological cells；
roller_bogie 再乘 N∈[2,6] 的 5 档 → 3×3×(1 + 5) = 54 slot-choice tuples（含 multiplicity）。

理由：a loom shuttle is a structurally minimal class; 18 base topologies + roller multiplicity is an
honest, source-backed spread for the "simple (low end)" richness band. All continuous diversity
(scale/palette/decoration) rides on top.

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` seeds `random.Random(seed)` and samples
every field procedurally for **every** seed including seed 0 (no special case, no curated table):
`rng.choice` for the three slots + palette, weighted `rng.choices` for `n_rollers`, `rng.uniform` for
the three scales. `resolve_config` clamps scales and derives `axle_z`/`flange_radius`/`roller_z` from
the chosen form. Compatibility is universal (shared axle interface) → no gating needed, no regression
overrides. `slot_choices_for_seed` exports `(body_form, bobbin_mechanism, underside, roller_n)`.
Topology target：1000-seed slot-choice-tuple coverage is report-only; 54 legal tuples is the true
combinatorial ceiling for this minimal class (below 300 by class nature, not by under-sampling —
documented per §9 low-count allowance).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→C, uniform slot choice, weighted n_rollers, uniform scales | slot_choices_for_seed matches build choices |
| compatibility matrix | all combos legal (shared axle interface); rollers independent of top mechanism | no floating (bobbin/rollers captured & supported), no closed-pose collision beyond declared captured overlaps |
| controlled local variation | length_scale, bobbin_radius_scale, arm_open; all clamped, axle_z/flange/roller derived | proportions vary without breaking bearing support, floor clearance, footprint containment, joint origin |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass (+ corner stage); 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | ③ Primary Form Family slot |
| bobbin_mechanism | 3 | yes | yes | ② mechanism slot |
| underside | 2 | yes | no | degraded-to-2 with reason (minimal class; only source-backed underside variation) |

## Validator
- `slot_choices_for_seed` returns implemented module names for all 3 slots + roller_n.
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special).
- no illegal combinations (all legal by shared axle interface); no regression overrides.
- continuous scales clamped in `resolve_config`; axle_z/flange_radius/roller_z derived there.
- captured-pin overlaps (bobbin journal, pivot pin/collar, pirn-on-spindle, roller-on-axle) are
  element-scoped `allow_overlap`; no broad part-level allowances.
- key joints: bobbin/pirn REVOLUTE +X [-π,π]; arm hinge REVOLUTE +Y; rollers CONTINUOUS +Y.
- `roller_{i}` follow naming + equal-spacing placement policy.

## Reject cases
- Body not elongated (L/W ≤ 4) or missing tapered ends → not a shuttle.
- No spinning weft package (no revolute bobbin/pirn) → drifts to plain stick / letter-opener.
- Bobbin isolated / floating (no bearing contact or captured journal) → support failure.
- Decoration emitted as separate FIXED parts instead of host visuals → Rule 1 violation.
- Rollers translating instead of spinning in place, or not hanging below keel → mechanism failure.
- Broad part-level `allow_overlap(body, bobbin)` masking real 穿模 instead of element-scoped captures.
- Downgrading the end_delivery LatheGeometry pirn to a plain Cylinder → Rule 3 violation.
- Mid-travel arm-hinge collision with the hull (reversed swing / over-wide range).

## 与相邻类别的边界
- 不该混入：netting/tatting shuttle（net/lace 工具，中央 tongue，无旋转纬纱包；本类必须有 spinning weft）。
- 不该混入：spinning-wheel bobbin / bare sewing bobbin（只有 weft 包无 shuttle body）。
- 不该混入：canoe / ski / sled / letter-opener（尖头木器视觉近邻，无纬纱包与旋转关节）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored from 2 origin parents + 6 verified forks; 3 slots (3/3/2 candidates), roller multiplicity N∈[2,6]. Captured journals grandfathered like cable_reel. |

## 模板实现备注（可选）
- 共享 helper：`_body_geom(form, ls, rs)` returns the axle interface struct consumed by every Slot B/C
  module (single-sources axle_z / bearing_x / cavity_floor_top_z / keel_bottom_z / half_width).
- `_emit_bearings` (shared) gives every body form the identical two bearing supports so any mechanism
  mounts identically.
- Captured-pin element-scoped `allow_overlap`: bearing↔bobbin_core (through_axle); rear_bearing↔pivot
  pin/collar + carved_hull↔pivot_pin (spindle_arm); bobbin_core↔spindle_rod + collars (end_delivery);
  roller_axle_{i}↔roller_wheel_{i} (roller_bogie).
- ski_upswept shallow channel: bobbin thread may overlap the hull wall (source-declared) → element
  allow_overlap(cotton_thread↔carved_hull) gated on body_form==ski_upswept.
- One shared `_emit_roller(i, x)` for N rollers; `LatheGeometry` preserved for the end_delivery pirn.
