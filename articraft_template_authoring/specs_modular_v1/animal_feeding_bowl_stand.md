# Modular Spec — Animal feeding bowl stand

## 元信息
| 项 | 值 |
|---|---|
| slug | `animal_feeding_bowl_stand` |
| template path | `agent/templates/animal_feeding_bowl_stand.py` |
| test path (optional) | `tests/agent/test_animal_feeding_bowl_stand_template.py` (not authored; sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (① base-skeleton form family → height mechanism → bowl coupling ② + side-by-side bowl multiplicity N) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (2 origins + 6 forks + 1 compatibility_probe) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

An **elevated pet feeding-bowl stand**: a grounded base that raises one or more *open* feeding bowls off the floor to a comfortable eating height, holding each bowl in a support ring / socket / cutout, with at least one real non-fixed joint (a height slide, a bowl tilt, a leg fold, or a bowl lift-out). Two honest body-form families appear in the 5-star pool: (A) a **planar box-frame chain** — H-skid frame + square upright post + sliding ring carriage carrying side-by-side bowls; (B) a **volumetric pedestal-column** — radial/tripod/disc/foldable foot base + hollow pedestal sleeve + telescoping socket holder carrying one central bowl. The bowl itself is an open lathe shell (rolled rim, flat bottom) in both families.

Must NOT drift into: a low non-elevated twin-bowl mat/tray/placemat; a cage/crate-mounted clamp-on bowl holder (mounts to an enclosure, not a floor stand); a camera/mic tripod, floor lamp, plant stand or cake stand (the host must retain a real bowl + holder); an automatic gravity feeder / water fountain (no reservoir/pump).

## 槽位 + 候选模块表

### Slot A：base_skeleton （① 骨架 + ③ 主体形态家族）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `h_skid_frame` | forked_anchor (origin A) | rec_...__001 | L74-L123 (base) + L127-L208 (carriage+slide) | eligible if compatible | Planar Boundary Form: 2 box skids + crossbar + square upright_post + 4 rubber pads; column = square post; sliding square collar carriage. |
| `cross_pedestal` | forked_anchor (origin B) | rec_...__002 | L153-L204 | eligible if compatible | Volumetric Envelope Form: 4 radial capsule feet + toe pads + central_hub + hollow_pedestal_sleeve + 3 collars; column = round sleeve. |
| `tripod_pedestal` | forked_anchor | rec_..._var_base_tripod | L156-L244 | eligible if compatible | Volumetric Envelope Form: 3 tubular legs splayed 120° + foot pads + hub + sleeve. |
| `disc_pedestal` | forked_anchor | rec_..._var_base_disc | L102-L211 | eligible if compatible | Volumetric Envelope Form: solid weighted disc + anti-slip pad + hub + sleeve. |
| `fold_pedestal` | forked_anchor | rec_..._var_base_fold | L153-L202 + L298-L334 | eligible if compatible | Volumetric Envelope Form + ② fold: 4 legs REVOLUTE-hinged to hub barrels + sleeve. |
| `diner_frame` | forked_anchor | rec_..._var_diner_platform | L64-L136 | eligible if compatible | Planar Boundary Form: rigid 4-leg raised top panel with N circular bowl cutouts (no height column). |

### Slot B：bowl_coupling （② 关节类型 — 碗如何附着于支撑层）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_seat` | forked_anchor | rec_...__001 / __002 / bowls_n3 | 001 L212-236 / 002 L261-298 / n3 L247-275 | eligible if compatible | bowl FIXED into ring/socket seat; no bowl-level joint (the height slide is the mechanism). |
| `tilt_cradle` | forked_anchor | rec_..._var_bowl_tilt / _var_probe_twin_tilt | tilt L229-324 / probe L203-265 | eligible if compatible | bowl(s) on REVOLUTE tilt: pedestal → single ring-yoke tilt; frame → per-bowl trunnion tilt, axis y, 0–25°. |
| `liftout` | forked_anchor | rec_..._var_diner_platform | L141-L181 | eligible if compatible (diner only) | bowl on vertical PRISMATIC lift-out from the panel cutout, 0–0.12 m. |

### Slot C：bowl_multiplicity （① 子项 multiplicity — side-by-side 碗数 N）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `n1` | forked_anchor | rec_...__002 (single bowl) | L261-L298 | eligible if compatible | 1 bowl (central for pedestals, or single seat for frame/diner). |
| `n2` | forked_anchor | rec_...__001 (loop over 2) | L212-L236 | eligible if compatible (frame/diner) | 2 bowls side-by-side along x. |
| `n3` | forked_anchor | rec_..._var_bowls_n3 | L28-L36 + L199-L275 | eligible if compatible (frame/diner) | 3 bowls side-by-side, widened crossbar/panel. |

硬约束满足：base_skeleton 6 candidates (≥3 form-family prototypes: 4 volumetric pedestal + 2 planar frame), bowl_coupling 3, bowl_multiplicity 3. 每个都 ≥2 且 source-backed。Support style (square ring-carriage vs round ribbed-socket vs panel) 是 base-family 内在形态，不单列为 slot（它与 base ③ 一对多派生），避免造 1-candidate 假槽位。

## 槽位图（slot graph）

pattern: **mixed**

```
base_skeleton (root, grounded)
  │  [ PRISMATIC height slide, axis +z ]   (column families: frame collar-on-post / pedestal post-in-sleeve)
  │  [ (diner_frame: no slide — rigid panel) ]
  ▼
bowl_support layer (carriage / socket-holder / panel — internal to base module)
  │  [ bowl_coupling joint ]:
  │     fixed_seat  → FIXED   (bowl ⊂ ring/socket)
  │     tilt_cradle → REVOLUTE (yoke or trunnion, axis y, 0–25°)
  │     liftout     → PRISMATIC (axis +z, diner only)
  ▼
bowl × N (side-by-side along x, or single central)
```

- Cross-slot connection points: base→support is a PRISMATIC rail (column top; frame square post inside collar / pedestal inner post inside sleeve). Support→bowl is the coupling joint at each seat (ring plane / socket ring / panel cutout). Frame family also carries CONTINUOUS clamp-knob controls on the collar (family A) and (tilt) trunnion yokes.
- Gating: `liftout` is exclusive to `diner_frame`; `diner_frame` uses only `liftout`. Pedestal bases carry a central socket (N=1). Frame + diner carry side-by-side seats (N∈{1,2,3}). `fold_pedestal` uses `fixed_seat`, N=1 (keeps folding-leg pose sampling tractable).

## 每槽位 Module Emits / Interfaces

### Slot A / module h_skid_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base_frame` (foot_0/1, base_crossbar, upright_post, rubber_pad_*), `height_carriage` (collar_front/back/side_*, ring_i, tab_i, clamp_backbone), `clamp_knob_0/1` | 001 L74-198, L267-311 |
| internal joints | `base_to_carriage` PRISMATIC axis z limits[-0.11,0.08]; `carriage_to_knob_{0,1}` CONTINUOUS axis y | 001 L200-208, L280-311 |
| upstream interface | root (grounded); N/A | — |
| downstream interface | ring seats at carriage-local (bx,0,0); consumer joint = bowl_coupling | 001 L153-163 |

### Slot A / module cross_pedestal (representative pedestal; tripod/disc/fold share holder+slide)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (foot_i/toe_pad_i, central_hub, hollow_pedestal_sleeve, lock collars), `bowl_holder` (sliding_inner_post, top_socket, top_socket_lip, ribbed_support_ring, radial_bracket_i, upright_clip_i, clip_cap_i) | 002 L163-259 |
| internal joints | `height_slide` PRISMATIC axis z limits[0,0.09] | 002 L283-291 |
| upstream interface | root (grounded) | — |
| downstream interface | central ring seat at holder-local z≈0.268; consumer joint = bowl_coupling | 002 L232-237 |
| fold extra (fold_pedestal) | `leg_i` parts + `hub_to_leg_i` REVOLUTE axis tangent limits[0,1.55] + hub `hinge_barrel_i` visuals | base_fold L173-182, L298-334 |

### Slot A / module diner_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base_frame` (top_panel with N cutouts via ExtrudeWithHolesGeometry, leg_i, rubber_pad_i) | diner L84-136 |
| internal joints | none (rigid) | — |
| downstream interface | cutout centers (bx,0,panel_top); consumer joint = liftout PRISMATIC | diner L141-181 |

### Slot B / bowl_coupling
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed_seat: `bowl_i` (cup, rim, flat_bottom [+band/paws]); tilt_cradle: `tilt_yoke`(+ring/clips) or per-bowl trunnions; liftout: `bowl_i` with lift joint | 001/002/tilt/probe/diner |
| joints | fixed_seat FIXED; tilt_cradle REVOLUTE axis y 0–25°; liftout PRISMATIC axis z 0–0.12 | tilt L309-317 / probe L252-265 / diner L168-181 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_skeleton | enum | {h_skid_frame, cross_pedestal, tripod_pedestal, disc_pedestal, fold_pedestal, diner_frame} | — | choice | deterministic sampler | Slot A |
| bowl_coupling | enum | {fixed_seat, tilt_cradle, liftout} | — | choice | sampler + gate | Slot B |
| n_bowls | int | [1,3] | 1 | conditional | pedestal/fold→1; frame/diner→{1,2,3} | Slot C |
| material_style | enum | {powder_black, graphite_plastic, walnut_frame, chrome_white} | powder_black | choice | palette only | ⑥ |
| column_height_scale | float | [0.85, 1.15] | 1.0 | independent | clamp; scales column/holder z | ⑤ 001 L95 / 002 L154 |
| base_span_scale | float | [0.85, 1.20] | 1.0 | independent | clamp; scales foot footprint / crossbar | ⑤ 001 L88 / n3 L34 |
| bowl_size_scale | float | [0.92, 1.10] | 1.0 | independent | clamp; scales bowl + seat radius jointly | ⑤ |
| tilt_upper | float | [15°, 28°] | 25° | independent | tilt limit; only used by tilt_cradle | ⑤ tilt L316 |
| slide travel | float | derived | — | equation | frame=[-0.11,0.08]·hscale; pedestal=[0,0.09]·hscale | 001 L207 / 002 L290 |
| bowl_spacing | float | derived | 0.32 | equation | `= f(bowl_size_scale)` side-by-side c-to-c | n3 L29 |
| (—) | constraint | — | — | inequality | seat radius ≤ ring/socket inner radius (bowl drops through); crossbar/panel span ≥ N·spacing + margin; folded legs clear holder | 接口/clearance |

## 7.5 编译预算 / compile budget
Per-seed budget **≤ 30 s** (typical 12–22 s). Basis: bowls/rings are LatheGeometry+Torus meshes (segments 72–96) reused across N via a single shared `Mesh`; pedestal sleeves are 2-profile lathes (72 seg); knobs are `KnobGeometry`. Heaviest seed = frame N=3 tilt (3 bowls + 3 rims + tabs + trunnions) ≈ 22 s. Tessellation banding: small features (rims, collars, knob grips) ≤ 24 seg tube / 72 tubular; hero bowl shell 96 seg. Sweep `--compile-timeout 120` (≈4× watchdog).

## Multiplicity / Copy Logic

- **count_param:** `n_bowls` — side-by-side feeding seats.
  - `N_range` (product) **[1,3]**; sampling domain: N=1 high-frequency (all pedestals + single frame/diner), N=2 common, N=3 rarer. Test range is the full product [1,3]; band labels reported as raw `n1/n2/n3`.
  - copied object: `bowl_i` (cup + rolled rim + flat_bottom) + its seat (`ring_i`/`tab_i` on frame carriage, or `cutout_i` on diner panel) + its coupling joint (`carriage_to_bowl_i` / `base_to_bowl_i`).
  - placement_rule: linear along x, even center-to-center spacing ≈ 0.30–0.34 (derived from bowl_size_scale); crossbar/panel widened per N; frame center bowl (odd N) nests the upright post through its hollow interior (allowed overlap).
  - naming: `bowl_{i}`, `ring_{i}`, `tab_{i}`, joint `carriage_to_bowl_{i}` / `base_to_bowl_{i}`.
  - joint_policy: each bowl coupled via the chosen bowl_coupling joint; one shared PRISMATIC height slide raises all (column families).
  - source/gating: N∈{1,2,3} source-backed (002 single, 001 two, bowls_n3 three). Pedestal central socket + fold → N=1 (single central seat). diner → N∈{1,2,3} cutouts.
- **secondary loops (not a separate N-sweep):** pedestal radial feet (4), tripod legs (3), fold legs (4), diner legs (4), capture clips (4) are loop-emitted with the base module; leg count is the ① base-skeleton axis, not a standalone N axis.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 6 base skeletons (planar H-frame chain / volumetric pedestal / tripod / disc / foldable / rigid diner panel) + N bowl copies + optional tilt-yoke / trunnion parts + clamp-knob parts. All forked_anchor / source-backed. |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：n_bowls N∈[1,3]，权重 N=1 高频、N=3 稀有；pedestal/fold gate 到 N=1。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | PRISMATIC height slide (all column families, axis z); REVOLUTE tilt (tilt_cradle, axis y); REVOLUTE fold (fold_pedestal, tangent axis); PRISMATIC lift-out (diner liftout, axis z); CONTINUOUS clamp knob (frame, axis y). 每种在 sweep 中出现（base+coupling 组合）。全部 source-backed。 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | 登记进 base_skeleton slot：Planar Boundary Form = {h_skid_frame(box skids+square post), diner_frame(flat cutout panel)}；Volumetric Envelope Form = {cross_pedestal, tripod_pedestal, disc_pedestal, fold_pedestal}（sleeve+旋转母线 feet/legs/disc）。bowl = open lathe shell（both）。≥3 可识别原型，source-backed。 |
| ④ 表面装饰 | 叠加表面细节 | 有 (record_only + world_knowledge_extrapolation) | ribbed grip ring (pedestal, host-derived torus+ribs), lobed knurled clamp knobs (frame), rolled rim on bowl, blue enamel band + white paw marks on pedestal bowl (host-conformal lathe band derived from the bowl outer profile per-z; paws on the shell face). 全部写为宿主 part visual，由宿主表面派生；无独立 module/joint。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | column_height_scale[0.85,1.15], base_span_scale[0.85,1.20], bowl_size_scale[0.92,1.10], tilt_upper[15°,28°]. 关节运动包络 + motion_test_plan：<br>• height slide (frame): axis +z, [closed=-0.11·h, upper=+0.08·h]; sampled collision + targeted pose raises bowls ≥0.07 & collar stays engaged on post.<br>• height slide (pedestal): axis +z, [0, 0.09·h]; sampled + targeted post-in-sleeve stays inserted, holder rises ≥0.08.<br>• tilt (tilt_cradle): axis +y, [0, tilt_upper]; sampled + targeted rim moves & inter-bowl clearance at max tilt.<br>• fold (fold_pedestal): tangent axis, [0, 1.55]; sampled + targeted leg folds upward ≥0.04.<br>• liftout (diner): axis +z, [0, 0.12]; sampled + targeted bowl lifts ≥0.10 & clears panel.<br>continuous clamp knob: full turn, no 穿模 (stem allowed through backbone). No sampled-pose exemption needed. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material_style ∈ {powder_black(metal), graphite_plastic(plastic), walnut_frame(wood/painted), chrome_white(metal/painted)} — 4 palettes. Material classes covered: metal (powder-coat/stainless), plastic (textured), painted/wood — ≥ ceil(0.5×4)=2. Bowls stainless; enamel-band accent. |

**收尾自检**：base 6 形态在 0-9 seed 渲染里应肉眼拉开（frame vs pedestal vs tripod vs disc vs fold vs diner）；tilt/fold/liftout/slide 全程不穿模；ribbed ring / knobs / rim 贴合宿主面。

## 采样与覆盖审计

总组合数（合法，去除 gate 后的 slot-tuple）：
- h_skid_frame × {fixed_seat, tilt_cradle} × {n1,n2,n3} = 6
- {cross, tripod, disc}_pedestal × {fixed_seat, tilt_cradle} × {n1} = 6
- fold_pedestal × {fixed_seat} × {n1} = 1
- diner_frame × {liftout} × {n1,n2,n3} = 3
→ **16 distinct legal slot tuples** (× continuous scales × 4 palettes).

理由：object 结构较浅（base + adjustable holder + open bowl）。16 tuples 覆盖全部 6 base 形态、3 coupling 关节类型、3 multiplicity — coverage-complete 而非灌水。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 独立采 base_skeleton / bowl_coupling / n_bowls / material_style / 连续 scale；`resolve_config` 用 compatibility gate 把非法组合 downgrade（liftout↔diner 互斥收敛、pedestal/fold→N1、pedestal/fold coupling clamp）。`seed=0` 不特殊。无 curated/modulo 主表；无 regression override。
Topology target：16 legal tuples；1000-seed 采样应实现全部 16（富度受真实结构空间限制，object 本身简单，<300 合理，已说明组合空间与 gate）。report-only。
Controlled local parameterization：column_height_scale / base_span_scale / bowl_size_scale / tilt_upper（见 §7 range + clamp/derived）。均在 `resolve_config` clamp/派生，遵守连续采样契约（先 independent 后 equation 派生 slide/spacing 后 inequality 投影 seat-radius/span）；不破坏 seat 半径匹配、slide 咬合、fold 净空、类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order base→coupling→N; uniform choice then gate-downgrade; N weighted small | slot_choices_for_seed matches build choices |
| compatibility matrix | liftout⇔diner_frame exclusive; pedestal/fold→socket central N1; frame/diner→side-by-side; fold→fixed_seat only | no floating/collision/axis/max-N/bulky/optional-child failures |
| controlled local variation | 4 clamped scales | proportions vary without breaking seat fit, slide engagement, joint origin, identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass; 0-999 maturity | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_skeleton | 6 | yes | yes | 2 planar + 4 volumetric form prototypes |
| bowl_coupling | 3 | yes | yes | fixed / tilt / liftout |
| bowl_multiplicity | 3 | yes | yes | n1/n2/n3 |

## Validator

- slot_choices_for_seed returns implemented module names (base_skeleton, bowl_coupling, bowl_multiplicity)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility gate prevents illegal combos (liftout on non-diner; multi-bowl on central socket; tilt on fold)
- no regression overrides; no curated modulo main domain
- controlled scales clamped in resolve_config; cannot break seat fit / slide engagement / joint origin / N
- key joints present with expected type/axis/range (prismatic slide; revolute tilt/fold; prismatic liftout; continuous knob)
- copied bowls follow `bowl_{i}` naming + even x spacing + shared mesh
- every non-FIXED template calls `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose(...)` per mechanism

## Reject cases

- Bowl not elevated (holder rests on floor) — must sit on an elevated frame/column/panel.
- Height slide disengages (collar leaves post / post leaves sleeve) at travel extremes → shrink travel, keep engagement overlap check.
- Seat radius > bowl rim (bowl falls through with no seating overlap) or < cup (bowl can't drop in) → clamp seat/bowl jointly.
- Folded legs collide with holder/bowl mid-travel, or tilt spills the bowl past 28° / collides adjacent bowl.
- Center bowl (odd N frame) modeled solid so the upright post has no cavity to pass through (should be hollow lathe + allowed overlap).
- Liftout applied to a column base, or clamp knobs floating (no backbone contact).

## 与相邻类别的边界

- 不该混入：**cage/crate-mounted clamp bowl holder**（挂在围栏/笼子上，不是落地 stand）。
- 不该混入：**automatic gravity feeder / water fountain**（含料仓/水泵，不是纯 stand）。
- 不该混入：**low twin-bowl mat / placemat**（不抬升，缺 elevated base + 非固定关节）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Support-style (ring vs socket vs panel) is base-family-derived, not a separate slot, to avoid a 1-candidate pseudo-slot; the two independent non-form axes are bowl_coupling (②) and bowl_multiplicity (N). |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | base_skeleton | h_skid_frame | rec_...__001 | L74-208, L240-311 | box frame + square post + ring carriage + slide + knobs |
| S2 | base_skeleton | cross_pedestal | rec_...__002 | L153-259, L283-298 | radial feet + sleeve + socket holder + slide + bowl |
| S3 | base_skeleton | tripod_pedestal | rec_..._var_base_tripod | L55-64, L156-244 | 3 tube legs + hub + sleeve |
| S4 | base_skeleton | disc_pedestal | rec_..._var_base_disc | L102-115, L159-211 | weighted disc + anti-slip pad + sleeve |
| S5 | base_skeleton | fold_pedestal | rec_..._var_base_fold | L153-202, L298-334 | 4 REVOLUTE folding legs on hub barrels |
| S6 | base_skeleton | diner_frame | rec_..._var_diner_platform | L64-181 | cutout panel + 4 legs + prismatic lift-out bowls |
| S7 | bowl_coupling | tilt_cradle (pedestal) | rec_..._var_bowl_tilt | L229-324 | ring-yoke REVOLUTE tilt |
| S8 | bowl_coupling | tilt_cradle (frame) | rec_..._var_probe_twin_tilt | L203-265 | per-bowl trunnion REVOLUTE tilt |
| S9 | bowl_multiplicity | n3 | rec_..._var_bowls_n3 | L28-36, L199-275 | 3 side-by-side bowls, widened crossbar |
</content>
</invoke>
