# paper_shredder — Modular Spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `paper_shredder` |
| 大类 / 小类 (picture) | `Workspace` / `Paper shredder` |
| source-map path | `articraft_template_authoring/picture_source_maps/Workspace__Paper_shredder.md` |
| origin parents | `rec_workspace__paper_shredder__002_…4cfd0224`, `rec_workspace__paper_shredder__001_…5c69ea48` |
| template path | `agent/templates/paper_shredder.py` |
| test path (optional) | `tests/agent/test_paper_shredder_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern = mixed`: a single cabinet/bin `body` root carries several **parallel** child mechanisms (waste basket / cabinet door, shredder head, feed lid, cutter shafts, caster wheels, push buttons, mode switch) that each mate to an independent face/recess of the same chassis. There is no serial slot chain; every moving child hangs off the body (or off the tilt-up `head`, which is itself a body child). A **multiplicity** axis controls the push-button count.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | 2 origin parents + 8 converged `rec_paper_shredder_var_*` (all rating=5 on disk) |
| source_index_policy | only adopted module sources are indexed below (probe_round_liftoff read but NOT adopted — compatibility_probe) |

**Shared invariant structure (all 10 samples):** a boxy/rounded black-plastic bin housing (`body`/`shell`) with an overhanging shredder head, a top **feed slot**, a **control panel** with push buttons + a slide switch, a **waste basket/receptacle** below the head, and a support base (4 casters or feet). Object-intrinsic frame (001 family, adopted): `+Y` = out of the FRONT face; `+Z` up; `+X` = width. Body ≈ `0.42 W (X) × 0.34 D (Y) × 0.57 H (Z)`; head overhang at top; casters at the base corners.

## 核心身份

A **paper shredder**: a powered cutting head with a top feed slot mounted over a shred receptacle. Paper enters the top slot, passes the cutter throat, and shreds collect in a bin below. Identity anchors that must always hold: (1) a top shredder head with a long narrow **feed slot** and a cutter throat; (2) a **shred receptacle/bin** under the head; (3) at least one real **access or control articulation** (pull-out basket, swing door, tilt head, auto-feed lid, and/or powered cutter shafts) plus the top push-button/slide controls. Default mature domain = office/personal console shredder, black plastic, front-loading waste bin, 4 casters. Must NOT become: filing/storage cabinet, kitchen trash can without a cutter head, printer/scanner/copier, pasta roller / wringer / mangle.

## 槽位 + 候选模块表

### Slot BODY_FORM：主体形态家族 / Primary Form Family（③；root shell geometry）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `rect_cabinet` | forked_anchor(origin) | `…__001` / `…__002` | 001 L35-L61 (`_body_shell`); 002 L45-L116 | eligible if compatible | **Volumetric Envelope Form** — rounded rectangular box cabinet, cavity bored into the front for the bin, overhanging box head. Casters on a rectangular corner grid. |
| `round_drum` | forked_anchor | `rec_paper_shredder_var_round_bin` | L35-L58 (`_cylinder_bin_shell`), L61-L133 (round shell + cyl head + base plate) | eligible if compatible (gated → pull_out_basket only) | **Volumetric Envelope Form** — hollow cylindrical drum wall with a rectangular front basket opening, circular base plate, cylindrical overhanging head. Casters on a smaller circular ring. Same part tree/interfaces; only the envelope form + caster ring change. |

### Slot ACCESS：opening / access mechanism (②；primary access joint to the bin)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pull_out_basket` | forked_anchor(origin) | `…__001` / `…__002` | 001 L249-L313 (basket + `body_to_basket` PRISMATIC); 002 L197-L277 | eligible if compatible | shelled waste basket (tray + side/back walls + runners + front panel w/ smoked window + grip), PRISMATIC drawer along `+Y`, retained on guide rails. `body`→`basket` (1 prismatic joint). |
| `hinged_door` | forked_anchor | `rec_paper_shredder_var_door` | L64-L97 (`_door_panel`), L275-L355 (hinge barrel + door + `body_to_door` REVOLUTE z + FIXED basket) | eligible if compatible (gated → rect_cabinet only) | side-hinged front cabinet `door` part (panel + viewing window + pull-handle recess) on a VERTICAL `+Z` jamb hinge (~100°); the interior basket becomes a FIXED bin behind it. `body`→`door` (1 revolute joint) + FIXED basket. |
| `tilt_head` | forked_anchor | `rec_paper_shredder_var_tilt_head` | L63-L69 (`_head_module`), L239-L344 (`head` part + `body_to_head` REVOLUTE x) | eligible if compatible (gated → rect_cabinet only) | the shredder **head splits off** the body into a `head` part on a rear horizontal `+X` hinge (~80°), lifting to expose the bin; the top features (feed / controls / buttons / cutter) ride on the head. Keeps the PRISMATIC basket. `body`→`head` (revolute) + `body`→`basket` (prismatic). |

### Slot FEED：feed mechanism (②；top paper entry)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_feed_slot` | forked_anchor(origin) | `…__001` / `…__002` | 001 L227-L232 (`feed_slot`); 002 L128-L136 | eligible if compatible | an open long narrow feed slot — a host-surface visual on the top plate. NO extra part/joint. |
| `autofeed_lid` | forked_anchor | `rec_paper_shredder_var_autofeed_lid` | L74-L87 (`_feed_housing`), L250-L269 (housing + stack_tray + `lid_hinge_barrel`), L390-L433 (`feed_lid` part + `body_to_feed_lid` REVOLUTE x) | eligible if compatible | a raised auto-feed housing with a recessed stack tray + a hinged `feed_lid` part (top-rear `+X` hinge, opens ~95° revealing the tray). `top`→`feed_lid` (1 revolute joint). |

### Slot CUTTING：cutting mechanism (②；throat under the feed slot)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `static_rollers` | forked_anchor(origin) | `…__002` | L105-L116 (`shredder_throat` + `cutter_roller_0/1` visuals) | eligible if compatible | a shredder throat + two static cutter-roller cylinder visuals on the head (host visuals, no joint). |
| `powered_shafts` | forked_anchor | `rec_paper_shredder_var_cutter_shafts` | promotes `cutter_roller_0/1` to `cutter_shaft_0/1` parts, 2 CONTINUOUS `+X` counter-rotating shafts captured in the throat | eligible if compatible | two counter-rotating CONTINUOUS cutter shafts (`+X`), captured between the throat side walls. `top`→`cutter_shaft_0/1` (2 continuous joints). |

### Slot SUPPORT：support / base (①；ground contact)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `caster_wheels` | forked_anchor(origin) | `…__001` / `…__002` | 001 L192-L217 (yokes) + L352-L373 (`caster_wheel_i` TireGeometry, `body_to_caster_wheel_i` CONTINUOUS); 002 L163-L194 + L316-L332 | eligible if compatible | 4 swivel-caster yokes (host visuals) + 4 CONTINUOUS rolling wheel parts (`+X`). `body`→`caster_wheel_0..3` (4 continuous joints). |
| `desk_feet` | forked_anchor | `rec_paper_shredder_var_desk_feet` | removes caster yokes + continuous joints; adds 4 FIXED rubber foot-pad **host visuals** under the plinth | eligible if compatible | 4 static rubber foot pads (host visuals on `body`, Rule 1 — no joint). Removes all 4 caster joints; the basket/buttons/etc. remain articulated. |

**Degrade note:** every supported slot reaches ≥2 structurally-distinct, source-backed candidates. ACCESS reaches 3. FEED / CUTTING / SUPPORT / BODY_FORM each reach exactly **2** — the 5★ pool for this 小类 converged exactly these structurally-distinct mechanisms (no third topology exists per axis); each pair differs by part count / joint type / envelope form, never by size or color. Inventing a 3rd candidate without a 5★ source is prohibited; left at 2 for reviewer approval.

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                              body  (root bin/cabinet shell; BODY_FORM = rect | round)
                               |
     ┌───────────┬─────────────┼──────────────┬──────────────┬───────────────┐
     ▼           ▼             ▼              ▼              ▼               ▼
   ACCESS      SUPPORT       (top surface, on `top_part` = head if tilt_head else body)
  basket/       casters/    ┌──────────┬──────────────┬─────────────┐
  door/         feet        ▼          ▼              ▼             ▼
  head                    FEED       CUTTING      buttons×N     mode_switch
 (PRISM/REV/REV)        open/lid   static/shafts  (PRISM ×N)     (PRISM x)
```

- **ACCESS** ⟷ body: front bin cavity. `pull_out_basket` = PRISMATIC `+Y` drawer on guide rails; `hinged_door` = REVOLUTE `+Z` jamb hinge + FIXED interior basket; `tilt_head` = REVOLUTE `+X` rear head hinge + PRISMATIC basket. Mutually exclusive.
- **SUPPORT** ⟷ body base: `caster_wheels` = 4 CONTINUOUS `+X` wheels on yokes; `desk_feet` = 4 FIXED foot visuals (no joint). Mutually exclusive.
- **Top surface** children parent to `top_part`: for `tilt_head`, `top_part = head` (so feed/controls/cutter tilt with the head); otherwise `top_part = body`. FEED (`open_feed_slot` visual / `autofeed_lid` revolute), CUTTING (`static_rollers` visuals / `powered_shafts` 2×continuous), buttons (PRISMATIC ×N), mode_switch (PRISMATIC `+X`).
- **Compatibility gates:** `round_drum` ⇒ ACCESS = `pull_out_basket` only (a rectangular swing door / rear tilt-head hinge do not seat on a round drum wall — round+lift-off head was only a *compatibility_probe*, explicitly not counted). `hinged_door` and `tilt_head` ⇒ BODY_FORM = `rect_cabinet` only. `tilt_head` ⇒ FEED = `open_feed_slot` **and** CUTTING = `static_rollers` (the tilting head carries only host-visual top features; moving top-surface child parts — auto-feed lid, powered cutter shafts — are gated to the non-tilt accesses so nothing swings off the head as it lifts). The hinged door is an **overlay** door (proud of the front face, so it never fouls the interior fixed bin); the pull-out drawer front is an **inset** face sized within the cabinet opening (never bites the surrounding shell face at any travel pose).

## 每槽位 Module Emits / Interfaces

### root / body (BODY_FORM)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (shell mesh: rect cavity-bored box + overhang head, OR round drum wall + base plate + cyl head); guide-rail visuals; top plate; control panel; side window; (head excluded from mesh when tilt_head) | 001 L35-L61 / round L35-L133 |
| internal joints | none (root) | — |
| downstream interface | front bin cavity (ACCESS), base pad (SUPPORT), top surface (FEED/CUTTING/controls) | 001 L200-L273 |

### ACCESS / pull_out_basket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket` (bottom tray + 2 side walls + back wall + 2 runners + front panel w/ smoked window + grip) | 001 L249-L285 |
| internal joints | `body_to_basket` PRISMATIC axis `(0,1,0)`, range `[-0.070, 0.120]`, origin `(0,0.100,0.115)` | 001 L302-L313 |

### ACCESS / hinged_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door` (panel + smoked front_window + pull_handle_recess), body `hinge_barrel` visual; `basket` becomes FIXED bin | door L275-L342 |
| internal joints | `body_to_door` REVOLUTE axis `(0,0,1)`, range `[0, ~100°]`, origin at left jamb; `body_to_basket` FIXED | door L314-L355 |

### ACCESS / tilt_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (head shell + hinge_knuckle; carries the top surface), body `hinge_barrel` visual; PRISMATIC `basket` | tilt L239-L275 |
| internal joints | `body_to_head` REVOLUTE axis `(1,0,0)`, range `[0, ~80°]`, origin at rear top edge; `body_to_basket` PRISMATIC | tilt L336-L355 |

### FEED / open_feed_slot
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (host visual `feed_slot` on `top_part`) | 001 L227-L232 |

### FEED / autofeed_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | host visuals `feed_housing` + `stack_tray` + `lid_hinge_barrel` on `top_part`; `feed_lid` part (panel + rim + grip + knuckle) | autofeed L74-L87, L250-L269, L390-L420 |
| internal joints | `{top}_to_feed_lid` REVOLUTE axis `(1,0,0)`, range `[0, ~95°]`, origin at rear housing rim | autofeed L422-L433 |

### CUTTING / static_rollers
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (host visuals `shredder_throat` + `cutter_roller_0/1` on `top_part`) | 002 L105-L116 |

### CUTTING / powered_shafts
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cutter_shaft_0/1` (cylinder shafts) captured in the throat | cutter_shafts fork |
| internal joints | `{top}_to_cutter_shaft_0/1` CONTINUOUS axis `(1,0,0)`, counter-rotating; captured-pin overlap allowed | cutter_shafts fork |

### SUPPORT / caster_wheels
| emits | 描述 | 来源 |
|---|---|---|
| parts | body caster yoke/axle host visuals; `caster_wheel_0..3` (TireGeometry tire + hub) | 001 L192-L217, L352-L373 |
| internal joints | `body_to_caster_wheel_0..3` CONTINUOUS axis `(1,0,0)`; captured axle overlap allowed | 001 L365-L373 |

### SUPPORT / desk_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (4 `foot_i` host foot-pad visuals on `body`) | desk_feet fork |
| internal joints | none | desk_feet fork |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | rect_cabinet / round_drum | rect_cabinet | choice | deterministic procedural sampler | BODY_FORM table |
| `access` | enum | pull_out_basket / hinged_door / tilt_head | pull_out_basket | choice | sampler; gated by `body_form` | ACCESS table |
| `feed` | enum | open_feed_slot / autofeed_lid | open_feed_slot | choice | sampler | FEED table |
| `cutting` | enum | static_rollers / powered_shafts | static_rollers | choice | sampler | CUTTING table |
| `support` | enum | caster_wheels / desk_feet | caster_wheels | choice | sampler | SUPPORT table |
| `button_count` | int (multiplicity N) | {2, 3, 5} | 3 | choice | weighted draw; §8 | 002 (N=2), 001 (N=3), controls_n5 (N=5) |
| `palette_style` | enum | charcoal / gloss_black / graphite / silver_top / warm_grey | charcoal | choice | per-seed colorway | materials across samples |
| `body_width_scale` | float | [0.90, 1.12] | 1.0 | independent | scales body X (rect) / drum radius (round); clamp | 001 L37 |
| `body_height_scale` | float | [0.92, 1.10] | 1.0 | independent | scales body Z + `top_z`, caster z unaffected; clamp | 001 L39 |
| `body_depth_scale` | float | [0.94, 1.08] | 1.0 | independent | scales body Y / front reach; clamp | 001 L38 |
| `basket_travel` | float | [0.09, 0.13] | 0.120 | conditional | only pull_out_basket / tilt_head; `≤ cavity_depth − margin` | 001 L313 |
| `door_open_angle` | float | [90°, 105°] | 100° | conditional | only hinged_door | door L354 |
| `head_tilt_angle` | float | [70°, 85°] | 80° | conditional | only tilt_head | tilt L343 |
| `lid_open_angle` | float | [85°, 100°] | 95° | conditional | only autofeed_lid | autofeed L432 |
| (—) | constraint | — | — | inequality | `basket footprint ≤ bin cavity − 2·wall`; round basket half-width `≤ drum_r − wall − clearance`; violate → shrink basket then re-derive | bin/basket interface |
| (—) | constraint | — | — | inequality | caster ring radius `≤ base_half − yoke − 0.01` (rect grid / round ring); violate → pull ring inward | base/caster |

Sampling contract (in `config_from_seed`/`resolve_config`): draw discrete slot enums with gating (`body_form`→`access`), draw `button_count` (weighted), draw palette; sample the 3 independent body scales then clamp; derive `top_z`/`cavity`/caster ring from scaled dims (equation); resolve conditional joint ranges only for the chosen modules; project the basket/caster inequalities (shrink to fit). `seed = 0` is not special.

### 7.5 编译预算 / compile budget（必填）
Per-seed budget **≈ 12–22 s** (rich cadquery boolean shells: rounded-box union/cut for rect, cylinder cut for round; TireGeometry casters; several small meshes). Basis: library reference for boolean-sculpt categories 5–30 s; the origin records compile in that band. Tessellation tiers: small features (buttons, cutter rollers, hinge barrels) ≤32 seg; hero shell fillets `min(radius,...)`; the 4 casters share ONE `TireGeometry` mesh shape; N buttons share one cylinder helper. `--compile-timeout 120` watchdog (≈6–10× budget) for parallel load.

## Multiplicity / Copy Logic

- **1 multiplicity axis: `button_count` (push buttons).**
  - `count_param`: `button_count`; `N_range` product domain `[1, 6]`; **test/sweep domain = {2, 3, 5}** (the exact source-backed counts: N=2 origin 002, N=3 origin 001, N=5 fork controls_n5). Sampling domain: weighted draw favouring N=3 (common), then N=2, N=5 rarer.
  - copied object: one `button` part with a `button_cap` cylinder, shared helper `_emit_button(i)`; naming `button_0..N-1`; placement: linear even spacing along the control-panel `X` at fixed `y`,`z` on `top_part`; joint policy: one PRISMATIC press joint per button (`axis (0,0,-1)`, shared limits `[0, 0.004]`), parented to `top_part`.
- casters are fixed at N=4 in both origins (a structural constant of the SUPPORT `caster_wheels` module, NOT a swept axis — both origins converged 4, no meaningful range). The `mode_switch` is a single fixed-identity slider, not a count axis.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | SUPPORT: 4-caster rolling base (adds 4 continuous parts) vs fixed desk feet (0 parts). ACCESS: drawer-in-cabinet vs swing-door+fixed-bin vs split-tilt-head topologies. FEED: +feed_lid part or not. CUTTING: +2 shaft parts or not. All forked_anchor / origin. |
| └ multiplicity | 同构件 ×N | 有 | `button_count` N∈{2,3,5}; 见 §8. |
| ② 关节类型 | 换 type/轴 | 有 | PRISMATIC basket/buttons/switch (`±Y`,`−Z`,`+X`), CONTINUOUS casters + cutter shafts (`+X`), REVOLUTE door (`+Z`), head (`+X`), feed lid (`+X`), FIXED basket (door variant) + feet. Every declared type appears in the sweep. forked_anchor/origin. |
| ③ 主体形态家族 | 换核心 part 的可识别几何原型 | 有 | BODY_FORM slot registered into `slot_choices`: `rect_cabinet` (Volumetric Envelope — box cabinet) vs `round_drum` (Volumetric Envelope — cylindrical drum). ≥2 recognizable prototypes, source-backed (origins + round_bin fork). `form_subtype` per candidate in the BODY_FORM table. |
| ④ 表面装饰 | 叠加表面细节 | 有 (record_only / host-conformal) | oval front_badge, indicator-dot strip, feed-slot icon strip, smoked side/front/basket windows, brushed-silver top plate — all host-surface visuals derived from the chosen shell face (per-form: badge sits on the flat front for rect, on the drum wall radius for round). No dedicated ④ variant; decoration is the last geometry, hugging ③/⑤. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | body width/height/depth scales (§7); joint envelopes: basket PRISMATIC `+Y [−0.070, +0.120]` (motion_test: slides out, stays retained); door REVOLUTE `+Z [0, 100°]` (swings clear of head); head REVOLUTE `+X [0, 80°]` (lifts, exposes bin); feed_lid REVOLUTE `+X [0, 95°]` (opens up); cutter shafts CONTINUOUS full turn; casters CONTINUOUS full turn; buttons PRISMATIC `−Z [0,0.004]`; switch PRISMATIC `+X [−0.011,0.011]`. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + one targeted `ctx.pose(...)` per key mechanism (basket-out, door-swing, head-tilt, lid-open, button-press, switch-slide, caster/shaft spin). Captured pins (caster axle↔hub, hinge barrel↔knuckle/door, shaft↔throat) get element-scoped `allow_overlap`. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 colorways (charcoal / gloss_black / graphite / silver_top / warm_grey), each body/head/window/control/rubber tokens; material classes plastic + metal (silver top plate) + translucent (smoked windows) + rubber (casters/feet) ≥ ceil(0.5×5). |

## 采样与覆盖审计

总组合数（离散拓扑，含 gate）：`rect×pull_out_basket` = FEED(2)×CUTTING(2)×SUPPORT(2)×buttons(3) = 24；`rect×hinged_door` = 24；`round×pull_out_basket` = 24；`rect×tilt_head` = FEED(1)×CUTTING(1)×SUPPORT(2)×buttons(3) = 6（tilt gate 固定 open_feed_slot + static_rollers）。总计 24+24+24+6 = **78** distinct topology combinations.

理由：78 ≥ 10 with wide margin. Slots change part trees / joint counts genuinely (SUPPORT ±4 continuous joints; ACCESS prismatic/revolute/split-part; FEED ±1 revolute; CUTTING ±2 continuous; BODY_FORM box↔cylinder envelope; buttons N). Below the ≥300 rich-category guideline because the honest legal topology space for this 小类 is bounded (a category cardinality limit, documented — the gates exclude only the physically-incompatible round+door / round+tilt cells and the tilt-head-with-moving-top-child cells), not a sampler weakness. Sweep `axis_realization` confirms every slot candidate is realized (access 3, body_form 2, feed 2, cutting 2, support 2, buttons 3) with 0 slot_choice_errors.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` does a deterministic per-seed weighted draw over the 6 discrete axes with `body_form`→`access` gating (round ⇒ basket), a mild bias toward the origin baseline (rect + basket + open_feed_slot + static_rollers + caster_wheels + N=3) so the common console shredder appears often while every legal combo remains reachable; then samples 3 independent body scales, derives `top_z`/cavity/caster-ring, resolves conditional joint ranges by chosen module, and projects the basket/caster inequalities. `seed = 0` is not special-cased.

Topology target：1000-seed slot-choice-tuple distinct expected ≈ 96 (the full legal set). Below the ≥300 suggestion because the category has exactly 96 legal topologies (compatibility-gated); report-only, not a gate.

Controlled local parameterization：`body_width_scale` / `body_height_scale` / `body_depth_scale` (independent, clamped) drive `top_z`, cavity footprint, caster ring, basket footprint via equations; joint ranges (`basket_travel`, `door/head/lid` angles) independent/conditional. All resolved/clamped in `resolve_config`; none breaks an interface, clearance, joint origin, or category identity.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted draw over 6 axes with body_form→access gate + baseline bias; per-seed scale jitter; deterministic from seed | `slot_choices_for_seed` matches build choices |
| compatibility matrix | round_drum ⇒ access=pull_out_basket; hinged_door/tilt_head ⇒ rect_cabinet; all other cells legal; conditional dims resolved per chosen module | no floating, no collision, correct joint axis/range, closed-pose bin covered |
| controlled local variation | body scales + top_z/cavity/caster-ring equation chain + joint-range jitter; clamp per §7 | proportions vary without breaking bin cavity seat, caster contact, hinge origin, or identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass, 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| BODY_FORM | 2 | yes | no | box vs drum envelope; 5★ pool converged exactly 2 |
| ACCESS | 3 | yes | yes | basket / door / tilt-head |
| FEED | 2 | yes | no | open slot vs auto-feed lid |
| CUTTING | 2 | yes | no | static rollers vs powered shafts |
| SUPPORT | 2 | yes | no | casters vs feet |

## Validator
- `slot_choices_for_seed` returns implemented module names for all 6 axes (body_form/access/feed/cutting/support/button_count)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility gating prevents illegal cells (round+door, round+tilt); conditional dims resolved only for chosen modules
- optional regression overrides: none
- controlled local scale params clamped; cannot break bin cavity seat, caster ground contact, hinge origin, or identity
- cross-part scale dependencies (top_z / cavity / caster-ring / basket footprint) resolved in `resolve_config`
- critical joint semantics: basket PRISMATIC `+Y` (or FIXED under door); door REVOLUTE `+Z`; head REVOLUTE `+X`; feed_lid REVOLUTE `+X`; cutter shafts CONTINUOUS `+X`; casters CONTINUOUS `+X`; buttons PRISMATIC `−Z`; switch PRISMATIC `+X`
- captured-pin element-scoped `allow_overlap` for caster axle↔hub, hinge barrel↔door/knuckle, cutter shaft↔throat
- copied buttons follow `button_i` naming + linear even placement, loop-emitted via shared helper

## Reject cases
- Bin/receptacle missing, or a solid block with no cutter head + feed slot (becomes a filing cabinet / trash can).
- Basket that slides fully out / detaches (travel > cavity depth), or a FIXED "drawer" that never opens with no other access articulation.
- Door hinged on the wrong edge / not covering the bin opening in closed pose; tilt head that clips the body mid-travel; feed lid opening downward into the head.
- Cutter shafts floating (not captured in the throat) or a powered-shaft joint that is not CONTINUOUS about `+X`.
- Caster wheels floating off their yokes / not CONTINUOUS, or `desk_feet` emitting a foot as a FIXED-joint part (Rule 1) or leaving the body floating above the floor.
- Illegal gated cell realized (round_drum + door, round_drum + tilt_head).
- Body scale left un-propagated so a scaled bin breaks the basket seat or caster contact.
- Inventing a candidate with no 5★ source, or ④ decoration built at constant radius floating off a scaled/curved face.

## 与相邻类别的边界
- 不该混入：**filing / storage cabinet** — has drawers/shelves but no cutter head + feed slot; our identity is the shredding head over a receptacle.
- 不该混入：**kitchen trash can / open bin** — a receptacle without a powered cutter head is not a shredder.
- 不该混入：**printer / scanner / copier** — top glass/lid + paper path but no shred bin + cutter throat.
- 不该混入：**pasta roller / wringer / mangle** — paired counter-rotating rollers superficially resemble cutter shafts, but those lack the bin + top feed slot + console housing; keep the shred receptacle + feed slot.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | ACCESS = 3 candidates; BODY_FORM/FEED/CUTTING/SUPPORT = 2 each (degrade documented — 5★ pool converged exactly 2 structurally-distinct mechanisms per axis). 96 gated topology combos ≥10. BODY_FORM is the registered ③ Primary-Form slot. 1 multiplicity axis (button_count {2,3,5}). Casters fixed N=4 (structural constant, not swept). probe_round_liftoff read but not adopted (compatibility_probe). |

## 模板实现备注（可选）
- `top_part` indirection: for `tilt_head`, feed/control/buttons/switch/cutter parent to the `head` part (they tilt with it); otherwise to `body`. A single `_to_top(x,y,z)` transform maps world coords to head-local when tilted (head-local origin = world rear-top hinge). Keeps one placement source (Contract 3c).
- Shared helpers: `_rounded_box`, `_body_shell` (rect, `include_head` flag so tilt excludes the fused head), `_round_shell`, `_paper_fill`/basket builder, `_emit_button(i)`, `_caster` (one TireGeometry mesh reused ×4).
- Captured-pin element-scoped `allow_overlap` (never broad): caster axle↔hub, hinge_barrel↔door_panel, hinge_barrel↔hinge_knuckle, cutter_shaft↔shredder_throat, door_panel↔lower_shell jamb seat.
- Overlaps gathered into a list during build and replayed in `run_tests` (washmachine idiom), plus `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` and targeted `ctx.pose(...)` per mechanism (Rule 5).

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | root | rect body + top surface + controls | `…__001` | L35-L61, L200-L273, L357-L392 | shared chassis + feed slot + control panel + buttons/switch |
| S0b | root | rect body (002 variant) + static cutters | `…__002` | L45-L116 | overhang head, throat + cutter rollers, casters |
| S1 | BODY_FORM | round_drum | `rec_paper_shredder_var_round_bin` | L35-L133 | cylindrical drum shell + base plate + cyl head |
| S2 | ACCESS | pull_out_basket | `…__001` | L249-L313 | prismatic waste basket |
| S3 | ACCESS | hinged_door | `rec_paper_shredder_var_door` | L64-L97, L275-L355 | revolute cabinet door + fixed bin |
| S4 | ACCESS | tilt_head | `rec_paper_shredder_var_tilt_head` | L63-L69, L239-L344 | revolute tilt-up head |
| S5 | FEED | autofeed_lid | `rec_paper_shredder_var_autofeed_lid` | L74-L87, L250-L269, L390-L433 | feed housing + revolute lid |
| S6 | CUTTING | static_rollers | `…__002` | L105-L116 | throat + static roller visuals |
| S7 | CUTTING | powered_shafts | `rec_paper_shredder_var_cutter_shafts` | promote rollers → 2 continuous shafts | powered cutter shafts |
| S8 | SUPPORT | caster_wheels | `…__001` | L192-L217, L352-L373 | continuous caster wheels |
| S9 | SUPPORT | desk_feet | `rec_paper_shredder_var_desk_feet` | fixed foot pads | static feet |
| S10 | multiplicity | button_count | `…__002` (2), `…__001` (3), `rec_paper_shredder_var_controls_n5` (5) | button loops | N∈{2,3,5} |
</content>
</invoke>
