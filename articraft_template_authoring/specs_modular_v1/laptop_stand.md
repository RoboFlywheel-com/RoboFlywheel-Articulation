# laptop_stand — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `laptop_stand` |
| template path | `agent/templates/laptop_stand.py` |
| test path (optional) | `tests/agent/test_laptop_stand_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: each form is a support/base root carrying its own articulated risers/uprights/arms (parallel_children — uprights + brace struts on the fold rail; link arms / post / scissor stack / spine on the rotating base), plus a ventilation-slot multiplicity axis (`vent_count`) that copies one through-cut N times along the A-family slotted bars.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 8 ids in the task (2 origin anchors A/B + 6 verified forks) |
| source_index_policy | only adopted module sources are indexed in the slot tables below |

Two source families (both fully adopted):
- **A-family** (cadquery slotted-bar / shell stock): origin A `rec_foldable-…defb8533` builds the twin lightening-slotted aluminum rails + ratcheted rear uprights + crossing brace struts (X silhouette) + upturned front hooks with `_lightening_slot_bar` / `_hook_bracket_mesh`. Forks reuse the same cadquery vocabulary: `…_var_mechanism_prop_leg` (single rear kickstand), `…_var_skeleton_wedge` (closed volumetric ventilated wedge), `…_var_n9_vents` (denser louver count).
- **B-family** (`ExtrudeGeometry` / mesh sit-stand riser on a rotating base): origin B `rec_workspace__laptop_stand__001…bcafa993` builds a broad rounded turntable base + perforated side arm-linkage + clamp-lip tray with `_rounded_plate_mesh` / `_arm_plate_meshes`. Forks: `…_var_mechanism_prismatic_post` (telescoping height post), `…_var_skeleton_scissor_lift` (double-X pantograph), `…_var_skeleton_center_column` (single central cantilever spine).

## 核心身份

A **laptop stand** is a desk device that lifts a laptop off the desk to an ergonomic height/angle, presenting a laptop-scale support surface (rails / tray / plate) with a front retaining lip or hook so the machine cannot slide off, on a grounded self-supporting footprint (rubber feet or a broad base), and — except for the explicitly-static wedge riser — at least one real height / tilt / rotation articulation. Default mature domain spans the portable foldable X-frame (origin A), the fabric-free sit-stand arm-linkage riser (origin B), the single rear prop-leg kickstand, the closed volumetric inclined wedge, the telescoping prismatic post, the scissor/pantograph lift, and the single central cantilever spine.

Must NOT drift into (see §11): monitor stand / monitor arm / VESA pole mount; tablet or phone easel/dock; desk / table / lap desk; book / document stand; cooling pad / fan tray.

## 槽位 + 候选模块表

### Slot A：form （① 骨架 + ② 关节 + ③ 主体形态家族 — 主多样性槽）
The primary form family. Each candidate is a structurally distinct kinematic + envelope prototype emitted onto its own support/base root (a fold rail, or a rounded rotating base). This is the required **③ Primary Form Family slot registered into `slot_choices`** (form-dominated 小类) and simultaneously carries the ① skeleton and ② joint diversity — every candidate is a different part-joint graph.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `fold_x_frame` | origin_anchor | origin A `rec_foldable-…defb8533` | L33-L58 (`_lightening_slot_bar`), L93-L151 (rear upright), L153-L192 (brace strut), L217-L360 (twin rails + 4 fold REVOLUTE `upright_pitch_*`/`strut_pitch_*`) | eligible if compatible | twin lightening-slotted rails on rubber feet + 2 ratcheted uprights + 2 crossing brace struts (folding X); 4 REVOLUTE; **Planar Boundary Form** (open bar-linkage frame) |
| `prop_kickstand` | forked_anchor | `rec_laptop_stand_var_mechanism_prop_leg` | L128-L218 (slotted tray + front hook), L220-L292 (width-spanning leg), L293-L315 (`tray_to_leg` REVOLUTE) | eligible if compatible | one flat ventilated inclined tray + single width-spanning rear leg on exactly ONE REVOLUTE setting tilt/height; **Planar Boundary Form** (thin inclined slotted deck) |
| `wedge_riser` | forked_anchor | `rec_laptop_stand_var_skeleton_wedge` | L102-L160 (`_wedge_shell_mesh` boolean cavity + top-panel vent cuts), L198-L248 (shell + side vents + 4 feet), L174-L181 (embedded rubber saddle) | eligible if compatible | one rigid closed ventilated wedge shell (top panel + solid side walls + footed base); explicitly `static_only` (all FIXED); **Volumetric Envelope Form** (closed inclined shell) |
| `pedestal_arm` | origin_anchor | origin B `rec_workspace__…bcafa993` | L25-L132 (`_rounded_plate_mesh`/`_arm_plate_meshes`), L143-L242 (base + turntable + perforated arm-linkage), L294 (`turntable_yaw` CONTINUOUS), L302/L311 (`arm_pitch`/`tray_tilt` REVOLUTE) | eligible if compatible | broad rounded rotating base + paired perforated side arms lift a clamp-lip tray; CONTINUOUS yaw + 2 REVOLUTE; **Volumetric Envelope Form** (tray-on-arm riser) |
| `telescoping_post` | forked_anchor | `rec_laptop_stand_var_mechanism_prismatic_post` | L120-L143 (outer tube), L145-L175 (inner slider), L242-L250 (`lift_column` PRISMATIC), L251-L262 (`tray_tilt`) | eligible if compatible | outer post + inner nested slider on ONE PRISMATIC height joint; keeps yaw + tray_tilt; **Volumetric Envelope Form** (telescoping column) |
| `scissor_lift` | forked_anchor | `rec_laptop_stand_var_skeleton_scissor_lift` | L54-L96 (`_bar_from_origin`/`_bar_centered`), L179-L265 (inner+outer crossed link pairs), L266-L300 (carriage), L359-L400 (`scissor_spread` driving + `scissor_cross`/`tray_level` Mimic + `tray_tilt`) | eligible if compatible | double-X pantograph: crossed inner/outer link pairs + leveling carriage; one driving REVOLUTE + 2 Mimic-coupled REVOLUTE keep the tray level; **Macro Surface Construction** (pantograph vertical lift replaces the tray-on-arm read) |
| `central_spine` | forked_anchor | `rec_laptop_stand_var_skeleton_center_column` | L35-L52 (`_central_spine_mesh`), L91-L123 (base yoke), L131-L144 (single central column), L149-L162 (tray bracket), L202-L232 (yaw + `arm_pitch` + `tray_tilt`) | eligible if compatible | twin side arms collapsed into one central cantilever spine on the centerline; single base yoke + single tray bracket; keeps yaw + arm_pitch + tray_tilt; **Planar Boundary Form** (single central load path, sides open) |

Six-axis note: 7 recognizable prototypes covering Planar Boundary (fold_x_frame, prop_kickstand, central_spine), Volumetric Envelope (wedge_riser, pedestal_arm, telescoping_post) and Macro Surface Construction (scissor_lift). ≥3 satisfied. All 7 are source-backed (origin_anchor / forked_anchor); none is world-knowledge padding.

### Slot B：retainer （④ / 前部保持接口 — 由 form gated）
The front laptop-retaining lip/hook. Two structurally distinct candidates, gated by form family (A-family + wedge present an upturned L-hook; B-family risers present a front clamp lip + foot). Non-articulating in every realized form — emitted as host `.visual(...)` (Rule 1).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hook_lip` | origin_anchor | origin A `_hook_bracket_mesh` L66-L90 (+ prop fork L191-L210) | L66-L90 | eligible: A-family + wedge | upturned L-shaped cadquery hook lip + rubber saddle at the support front tip |
| `clamp_lip` | origin_anchor | origin B tray front lips/feet L243-L275 | L243-L275 | eligible: B-family | paired front clamp lips + lip feet (Box) gripping the laptop front edge on the tray |

The wedge source (`…_var_skeleton_wedge`) actually articulates its front hooks (`wedge_to_hook_*` REVOLUTE, L273-L296); the template deliberately **fuses them as fixed `.visual(...)` lips embedded into the inclined top panel** (Rule 1) so the wedge is the single explicitly-static ③ candidate. This is the intentional adaptation, not a lost joint.

Every candidate in every slot is structurally distinct (part tree / joint topology / primitive family), not a re-skin. Retainer is a 2-candidate interface slot (form-locked, not independently sampled). Colorway/finish is NOT a candidate (⑥ audit-only, rides `palette_style`).

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
A-family root = stand_base / support_tray / wedge_body (cadquery slotted stock)
   fold_x_frame:  stand_base ──[REVOLUTE +Y @rail rear lug]──> upright_{0,1}
                  stand_base ──[REVOLUTE +Y @rail mid lug]──> brace_strut_{0,1}   (crosses upright → folding X)
                  hook_lip fused on stand_base (Rule 1)
   prop_kickstand: support_tray ──[REVOLUTE +Y @tray hinge lug]──> prop_leg
                   hook_lip fused on support_tray (Rule 1)
   wedge_riser:   wedge_body (single rigid part, NO joints); hook_lip lips fused into the top panel (Rule 1)

B-family root = base (broad rounded plate) ──[CONTINUOUS +Z @center]──> turntable
   pedestal_arm:     turntable ──[REVOLUTE +Y]──> link_arms ──[REVOLUTE +Y]──> upper_tray
   telescoping_post: turntable ──[PRISMATIC +Z]──> inner_slider ──[REVOLUTE +Y]──> upper_tray
   central_spine:    turntable ──[REVOLUTE +Y]──> link_column ──[REVOLUTE +Y]──> upper_tray
   scissor_lift:     turntable ──[REVOLUTE −Y]──> scissor_inner ──[REVOLUTE −Y mimic]──> scissor_outer
                     scissor_outer ──[REVOLUTE −Y mimic]──> slider_carriage ──[REVOLUTE +Y]──> upper_tray
   clamp_lip fused on upper_tray (Rule 1)
```

- Slot order (resolve): `form` → `retainer` (= RETAINER_BY_FORM[form]) → `vent_count` (A-family only, else 0) → `palette_style` → continuous scales. `seed=0` is not special.
- Cross-slot connection points: A-family children pin through rail/tray hinge lugs; B-family children stack on the rotating turntable through yoke/lug/carriage pivots. Joint origins sit on real hardware (hinge lugs, pivot washers, tube bores) — see §6.
- Every non-FIXED joint is a captured pin-through-lug / turntable pivot / nested-tube slider that `MatingContract` cannot express as two axis-aligned faces, so joints are **grandfathered** (omit `mating=`) with element-scoped `allow_overlap` + `expect_overlap`/`expect_contact` mirroring each source's `run_tests` (same discipline as `camp_chair` / `Healthcare_Wheelchair`).
- Mutual exclusion / gating: retainer is form-locked (hook_lip for A+wedge, clamp_lip for B); `vent_count` only applies to A-family (`VENTED_FORMS`), clamped to ≤5 on the wedge top panel; the wedge is the sole static form.

## 每槽位 Module Emits / Interfaces

### Slot A / form (per form)
| emits | 描述 | 来源 |
|---|---|---|
| parts | fold_x: `stand_base` + `upright_{0,1}` + `brace_strut_{0,1}`; prop: `support_tray` + `prop_leg`; wedge: `wedge_body` (only); pedestal: `base`+`turntable`+`link_arms`+`upper_tray`; post: +`inner_slider`; spine: +`link_column`; scissor: +`scissor_inner`/`scissor_outer`/`slider_carriage` | per-form sources above |
| internal joints | fold_x 4× REVOLUTE; prop 1× REVOLUTE; wedge none; B-family CONTINUOUS yaw + REVOLUTE arm/tilt (pedestal/spine), PRISMATIC lift + REVOLUTE tilt (post), driving REVOLUTE + 2 Mimic REVOLUTE + tilt (scissor) | per-form articulations |
| upstream interface | grounded root (rail feet / wedge feet / rounded base plate) sits on the desk | origin A L217+ / wedge L198-L248 / origin B L143-L166 |
| downstream interface | support surface top face (slotted deck / laptop plate) hosts the retainer + rubber saddle | origin A / origin B tray |

### Slot B / retainer
| emits | 描述 | 来源 |
|---|---|---|
| parts | none — hook lips / clamp lips + feet are host `.visual(...)`, never FIXED-jointed parts (Rule 1) | `_hook_bracket_mesh` L66-L90 / origin B lips L243-L275 |
| internal joints | none | — |
| upstream interface | fused onto the support front edge (fold rail front / tray front / wedge low panel edge) | per source |
| downstream interface | retains the laptop front edge (informational) | — |

不动细节（ventilation slots, rail grooves, rubber pads/saddles/feet, ratchet buttons, side vents）都是宿主 part 的 `.visual(...)`，不是 FIXED-jointed part（Rule 1）。本模板唯一没有关节的 form 是 wedge_riser（显式 static ③ 候选）；其余 form 的每个 child 都是真正会动的关节，没有 phantom FIXED anchor。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `form` | enum | 7 modules (Slot A) | fold_x_frame | choice | deterministic procedural sampler `rng.choice(FORMS)` | Slot A table |
| `retainer` | enum | hook_lip / clamp_lip | — | equation | `= RETAINER_BY_FORM[form]` (form-locked, not independently sampled) | Slot B table |
| `vent_count` | int (mult.) | [3,11] product; test skews small | 5 | conditional | A-family only (`VENTED_FORMS`), else 0; wedge clamped ≤5 (top-panel real estate); weighted `min(randint,randint)` small-N | origin A N=5 L224 / n9_vents `RAIL_SLOT_COUNT=9` L28 |
| `palette_style` | enum | 4 colorways (see §8.5 ⑥) | silver_aluminum | choice | `rng.choice(PALETTE_STYLES)` | origins + companion forks |
| `plate_len_scale` | float | [0.95, 1.05] | 1.0 | independent | uniform sample then clamp in `resolve_config` | proportion ⑤ |
| `riser_height_scale` | float | [0.96, 1.06] | 1.0 | independent | uniform sample then clamp; B-family riser rise = 0.200·scale | proportion ⑤ |
| (—) | constraint | — | — | conditional | `vent_count` domain resolved from `form` before it is realized (0 for B-family, ≤5 for wedge) | §9 |

所有 `equation`/`conditional` 在 `resolve_config` 内求解（`retainer`、`vent_count` domain）；连续 scale 采样后立即 clamp；builder 不再失败。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤14 s/seed**（库内实测本类 2–5 s/seed，见 sweep 日志）。依据：B-family 主体是 `ExtrudeGeometry`/`Box`/`Cylinder` 图元 + 少量 rounded-plate mesh；A-family 用 cadquery `_lightening_slot_bar`（slot2D + N cutThruAll）与一处 `_wedge_shell_mesh` 布尔雕刻（outer.cut(cavity) + N 个 vent 切割）——最重的一档。分档 tessellation：cadquery `tolerance≈0.0006 / angular_tolerance≈0.08`，圆特征 `_circle_profile segments≤24`；N 个相同 vent 切割在同一 `_lightening_slot_bar` 内一次成型，N 根相同 rail 复用同一个 `Mesh`。超预算先降 tessellation 再迭代（`AUTHORING.md` §C）。

## Multiplicity / Copy Logic

**Axis 1 — `vent_count` (ventilation louver/slot count), sources origin A (N=5) + `rec_laptop_stand_var_n9_vents` (N=9).**
- `count_param` = `vent_count`; product domain `[3,11]` (`VENT_MIN,VENT_MAX`); sampling domain = weighted small-N draw `min(rng.randint(3,11), rng.randint(3,11))` (biases low), test 偏小、product 全程。
- copied object = one through-slot cut fed to `_lightening_slot_bar` (rounded or rect), looped over `cuts`; naming = indexed slot cuts inside the rail/bar loop (`_even_rect_cuts` for the fold rail, per-bar cut tuples for the prop tray, `xs` loop for the wedge top panel).
- placement = evenly spaced along the bar long axis (fold rail span 0.240, prop bar span 0.200, wedge panel between front/rear x).
- joint policy = FIXED decorative through-cuts (no articulation change).
- source / gating = **A-family only** (`VENTED_FORMS = {fold_x_frame, prop_kickstand, wedge_riser}`); B-family forms get `vent_count=0` (their perforation is baked into the arm/plate meshes, not a template copy axis); the wedge top panel is clamped to ≤5 slots.

No other template-level copy axis: the paired uprights/struts/rails/side-arms are fixed 2-count structure per form (loop-emitted with stable indexed names `upright_{i}`, `brace_strut_{i}`, `side_arm_{side}`, `inner_link_{i}`), not an exposed `*_count` multiplicity.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | 7 distinct part-joint graphs (Slot A): fold-X 4-revolute frame (A) · single prop-leg revolute (fork) · static wedge (fork) · arm-linkage riser (B) · telescoping post (fork) · scissor pantograph (fork) · central spine (fork). All source-backed forked_anchor/origin_anchor. |
| └ multiplicity | 同构件 ×N | 有 | `vent_count` N∈[3,11] weighted small-N, A-family only (wedge ≤5) — see §8. Sources origin A N=5 + n9_vents N=9. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE +Y/−Y (fold pitch, prop leg, arm pitch, tray tilt, scissor stack) · CONTINUOUS +Z (turntable yaw) · PRISMATIC +Z (lift column) · Mimic-coupled REVOLUTE (scissor_cross/tray_level) · all-FIXED (wedge). Source-backed (origin A/B + prismatic_post + scissor_lift). Every declared type appears in sweep (7 forms cover all). |
| ③ 主体形态家族 | 换核心几何原型 | 有 | 7 prototypes registered in `slot_choices`: Planar Boundary (fold_x_frame, prop_kickstand, central_spine), Volumetric Envelope (wedge_riser, pedestal_arm, telescoping_post), Macro Surface Construction (scissor_lift). Source-backed. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only) | lightening/ventilation slots, rail side grooves, rubber pads/saddles/feet, ratchet adjust buttons, release lever, pivot washers/bushings. Emitted as host `.visual(...)` derived from the deck/rail/panel face they sit on (derive order ③→⑤→④; the wedge lips are embedded into the inclined top panel, not floating). Not standalone modules. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | plate_len_scale [0.95,1.05], riser_height_scale [0.96,1.06] (B rise=0.200·scale). **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): fold upright_pitch REVOLUTE +Y [−0.10, 1.55]; fold strut_pitch +Y [−0.10, 1.05]; prop tray_to_leg +Y [0.0, 0.85] (hard stop where the leg meets the tilted deck); turntable_yaw CONTINUOUS +Z (full turn); arm_pitch REVOLUTE +Y [−0.45, 0.45]; tray_tilt +Y [−0.35, 0.65]; lift_column PRISMATIC +Z [0.0, 0.100]; scissor_spread REVOLUTE −Y [0.0, 0.85] with scissor_cross (×−2 mimic) & tray_level (×1 mimic) keeping the tray level. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses` (32–96 samples per form) + one targeted `ctx.pose(...)` per mechanism (fold drops upright toward rail; prop leg folds up; yaw swings tray footprint; arm/tilt move tray; lift raises tray with inner tube retaining insertion; scissor spread lifts tray). Captured-pivot / nested-tube / hinge-seat contacts are element-scoped `allow_overlap`; no broad exemption needed. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes: metal (silver aluminum body + satin pivot hardware), painted (space-grey / matte-black / arctic-white body), plastic (rubber feet/pads/saddles). ≥4 colorways: silver_aluminum, space_grey, matte_black, arctic_white. Material-class coverage ≥ ceil(0.5×4)=2 every seed (metal/painted body + plastic rubber + hardware always present). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——7 个 form 拉得开（fold-X / prop / wedge / arm-riser / post / scissor / spine）、metal/painted/plastic 材质都出现、hook/clamp 保持嘴与 vent 贴合宿主面不悬空、fold/prop/lift/scissor/yaw 关节全程不穿模。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- form(7) × retainer(form-locked, 1 each) × vent_count(A-family: fold/prop N∈[3,11] realized-distinct, wedge N∈{clamped ≤5}; B-family: none) × palette(4) × continuous scales.
- Discrete slot-tuple space `(form, retainer, vent_count)` realizes **24 distinct tuples over 1000 seeds** (7 forms; A-family forms fan out over vent counts, B-family collapse to `none`). report-only, not a gate — laptop-stand structural vocabulary is deliberately `simple` band (8 source anchors), and the note in the source map documents that padding past 8 would be ④/⑤/⑥ cosmetic or neighbor drift.

理由：多样性主要来自离散 `form`(①②③) 槽 + `vent_count`(N) + form-locked `retainer`(④/interface)；连续 scale 仅 clamp/derive，不撑多样性。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；`form = rng.choice(FORMS)`; `palette = rng.choice(PALETTE_STYLES)`; `vent_count = min(randint(3,11), randint(3,11))` (weighted small-N); continuous scales uniform then clamp. `resolve_config` derives `retainer = RETAINER_BY_FORM[form]` and resolves the `vent_count` domain from the form (0 for B-family, ≤5 for wedge). Compatibility matrix = `RETAINER_BY_FORM` + `VENTED_FORMS` gate (prevents illegal clamp-on-fold or vent-on-scissor). No regression overrides (procedural covers seed 0).
Topology target：24 distinct slot tuples over 1000 seeds (report-only, not a gate). Below the 300 richness suggestion because the subcategory is a `simple`-band form family with 8 honest source anchors and a form-locked retainer (no independent retainer/base cross-product); documented in the source map budget decision.
Controlled local parameterization：plate_len_scale, riser_height_scale — both clamped in `resolve_config`; they never break the captured-pin allowances (pivot origins are independent of the scales) or the nested-tube insertion inequality (post inner-tube retains ≥55mm insertion at max lift).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | form, palette, weighted vent_count, derived retainer + vent domain, clamped scales | slot_choices_for_seed matches build choices |
| compatibility matrix | RETAINER_BY_FORM + VENTED_FORMS gate; wedge vent ≤5; fallback → vent 0 for B-family | no floating retainer, collision, axis, closed-pose, over-vent failures |
| controlled local variation | plate_len_scale / riser_height_scale, clamped | proportions vary without breaking interfaces / clearance / joint origin / identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner 0-379), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| form | 7 | yes | yes | ③ primary form slot (also ①②) |
| retainer | 2 | yes | — | ④/interface, form-locked (2 structurally distinct) |
| vent_count (mult) | N∈[3,11] | yes | — | source origin A N=5 + n9_vents N=9 |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (form, retainer, vent_count)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix (`RETAINER_BY_FORM` + `VENTED_FORMS`) prevents illegal combos in `resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped in `resolve_config`; pivot origins independent of scale
- every non-FIXED joint is a captured pivot with element-scoped `allow_overlap` + `expect_overlap`/`expect_contact`; no MatingContract phantom anchors; no FIXED-jointed decoration parts (retainer/vents/pads are host visuals)
- key joints have expected type/axis/range (fold/prop/arm/tilt REVOLUTE +Y; yaw CONTINUOUS +Z; lift PRISMATIC +Z; scissor Mimic-coupled REVOLUTE; wedge all-FIXED)
- copied vent objects follow evenly-spaced indexed placement inside `_lightening_slot_bar` / wedge panel loops
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per mechanism

## Reject cases
- A form whose retainer floats above the deck instead of embedding into the support surface (wedge lip hovering over the top panel; hook island above the rail).
- fold_x brace/upright whose fold pose drives the strut through the rail or neighbor bar without an element-scoped crossed-brace allowance (the folding-X contact).
- prop leg whose fold range strangles or drives it through the ventilated deck (must hard-stop where the foot bar meets the tilted tray plane).
- scissor tray/carriage pivot contacts left un-allowed → swept-pose 穿模 at tray_tilt extremes / max spread (the captured-pivot washer↔plate and slide-rail↔lug seats must be element-scoped).
- telescoping post whose inner tube loses insertion (<55mm) at max lift, or whose outer/inner tubes are not nested.
- Downgrading cadquery `_lightening_slot_bar` / `_wedge_shell_mesh` boolean heroes or B-family `ExtrudeGeometry` rounded plates/arms to flat `Box` (Rule 3).
- B-family form emitting a non-zero `vent_count` (vents belong to A-family slotted stock only), or a monitor-pole / VESA drift.
- Monochrome output (palette_style not driving `.visual(material=...)`).

## 与相邻类别的边界
- 不该混入：monitor stand / monitor arm / VESA pole mount（承载显示器、不呈现 laptop 支撑面 + 前保持嘴 — neighbor drift）。
- 不该混入：tablet / phone easel / dock（更小、竖立单板托，非 laptop-scale 倾斜支撑面）。
- 不该混入：desk / table / lap desk（大平面工作台，不抬升 laptop 到 ergonomic 角度）。
- 不该混入：book / document stand（阅读架，无 laptop 保持嘴/通风）。
- 不该混入：cooling pad / fan tray（主体是风扇散热面，非 ergonomic 抬升机构）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 2 origin anchors (A cadquery slotted-stock fold frame + B ExtrudeGeometry sit-stand riser) + 6 verified forks → 7 source-backed forms. Retainer form-locked (2 candidates). Wedge front lips intentionally fused static (Rule 1) making it the single ③ static candidate. Scissor captured-pivot / hinge-seat contacts element-scoped (washer↔carriage_plate, slide_rail↔carriage_lug); decorative slide rail shrunk to keep the tilt-range penetration shallow. |

## 模板实现备注（可选）
- Shared helpers: A-family `_lightening_slot_bar` / `_hook_bracket_mesh` / `_even_rect_cuts` (cadquery); B-family `_rounded_plate_mesh` / `_tube_mesh` / `_arm_plate_meshes` / `_central_spine_mesh` / `_scissor_bar_*` (`ExtrudeGeometry`); `_build_b_base` / `_turntable_core` / `_emit_yaw` / `_emit_tray_surface` shared across all 4 B-family forms.
- Captured-pin element-scoped `allow_overlap` (grandfathered, no `mating=`): fold upright/strut hinge lug↔boss/pin + folding-X brace↔upright cross; prop leg hinge boss/pin↔tray lug; arm base/tray shaft↔yoke/tray lug; post outer↔inner tube nest + pivot shaft↔collar; spine base_yoke/tray_bracket↔central_spine; scissor center_shaft↔outer link/washer, tray_shaft↔carriage lug/bushing, tray_pivot_washer↔carriage_plate, slide_rail↔carriage_lug, tray_lug↔carriage_plate. Each mirrored with `expect_overlap`/`expect_contact` where the contact is present at rest.
- The wedge is the only all-FIXED form; `run_laptop_stand_tests` skips the "≥1 real articulation" identity check for `wedge_riser` only.
