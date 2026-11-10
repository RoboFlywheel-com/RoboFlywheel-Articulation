# Technology_Monitor — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Monitor` |
| template path | `agent/templates/Technology_Monitor.py` |
| test path (optional) | `tests/agent/test_Technology_Monitor_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel panel↔carrier + linear stand chain; whole-skeleton switch by stand family) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this 小类 (2 origins + 6 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

Read notes (all `data/records/<id>/revisions/rev_000001/model.py`, read FULLY):

- **S1 parent A** `rec_a-standard-16-10-widescreen-desktop-lcd-monitor-…015db054` (`widescreen_lcd_monitor`), L34-L182.
  Flat desk-stand monitor. part `stand` {hex_base(cq polyline), slotted_pillar(cq box+cable slot), base_collar(Cyl), top_crosshead(Box), yoke_arm_{i}(Box×2), hinge_cheek_{i}(Cyl×2)} + part `screen` {rear_shell(Box), bezel(BezelGeometry mesh), display_panel(Box), rear_mount(Box), hinge_barrel(Cyl)}; ONE joint `stand_to_screen` REVOLUTE X (tilt, rest rpy=(-0.12,0,0), [-0.22,0.20]). Screen frame origin = hinge axle; panel center +0.105 above hinge (hinge at lower third).
- **S2 parent B** `rec_ultrawide-curved-…0ea51d17` (`curved_monitor`), L36-L254.
  Curved super-ultrawide on central neck. parts `base_foot`{base_foot_shell(cq V-foot)}, `neck_riser`{neck_riser_shell(cq loft), swivel_hub(Cyl)}, `neck_carriage`{carriage_plate(Box), tilt_barrel(Cyl X)}, `screen_panel`{panel_housing(YZ loft along X), screen_glass(YZ loft), vesa_mount(Box boss)}; joints `base_to_neck_swivel` REV Z (±30°), `neck_to_carriage_height` PRIS Z (±40mm), `carriage_to_screen_tilt` REV X (−5..+15°). PANEL_W 0.72 / PANEL_H 0.21 (~3.4:1), BOW 0.050 concave (mid toward −Y).
- **S3** `rec_monitor_var_twin_leg_base`, L46-L216. Fork of A: `stand` replaces single plate with `leg_{i}`(cq A-frame beam ×2, shared helper) + `foot_pad_{i}`(Box×2) + `central_column`(Box) + `junction_gusset` + `column_collar`, KEEPS top_crosshead+yoke+`stand_to_screen` tilt. Two splayed legs meeting at a column.
- **S4** `rec_monitor_var_ergonomic_arm`, L63-L392. Fork of A: replaces desk stand with articulating arm. parts `desk_clamp`{clamp_body(cq C-clamp), clamp_bolt_{i}×2}, `arm_lower`{lower_beam(cq), lower_shoulder_housing(Cyl Z), lower_elbow_housing(Cyl X)}, `arm_upper`{upper_beam(cq), upper_vesa_adapter(Box)}, `vesa_head`{vesa_bracket(Box), vesa_plate(cq 4-hole), vesa_bolt_{i}×4}, `screen`(same as A). joints `clamp_to_lower_arm` REV Z (shoulder ±2.6), `lower_to_upper_arm` REV −X (elbow −0.30..1.80), `upper_to_vesa` FIXED, `vesa_to_screen` REV X (tilt). captured-shaft allow_overlap elbow_housing↔upper_beam.
- **S5** `rec_monitor_var_wall_mount`, L21-L198. Fork of A: no ground base. parts `wall_plate`{plate_body(Box)}, `mount_bracket`{bracket_backplate(Box), bracket_arm_{i}(Box×2), bracket_pivot_{i}(Cyl X ×2)}, `screen`(same as A). joints `wall_to_bracket` FIXED, `bracket_to_screen` REV X (tilt). captured pivots grab hinge_barrel ends (allow_overlap).
- **S6** `rec_monitor_var_curved_21_9`, L36-L256. Fork of B: same neck/carriage/loft part tree, retuned PANEL_W 0.62 / PANEL_H 0.27 (~2.3:1), BOW 0.025 (gentler). Moderate curved ultrawide.
- **S7** `rec_monitor_var_tilt_swivel`, L22-L223. Fork of A: splits `stand` into fixed `base`{hex_base, base_collar} + swiveling `column`{slotted_pillar, top_crosshead, yoke_arm_{i}, hinge_cheek_{i}} (column visuals offset −SWIVEL_Y/−SWIVEL_Z into swivel frame). NEW `base_to_column` REV Z (±1.0) + kept `stand_to_screen` tilt. 2 DOF.
- **S8** `rec_monitor_var_portrait_pivot`, L22-L208. Fork of A: inserts intermediate `pivot_hub`{hub_disk(Cyl Y), hub_bracket(Box)} between stand and screen. joints `stand_to_pivot` REV X (tilt), `pivot_to_screen` REV Y (portrait, 0..π/2, panel-normal). landscape↔portrait rotation.

## 核心身份

A **desktop computer monitor**: exactly one display panel carried by a support (desk stand / articulating arm / wall bracket). The panel is the hero (a thin, framed or bezelled rectangular/curved slab, screen facing −Y). The support raises the panel above the desk and provides **at least a tilt DOF**; richer supports add swivel, height and portrait-pivot. Default mature domain: consumer/office/gaming desktop monitors 22"–49", flat 16:9/16:10 or curved ultrawide 21:9/32:9, on a pedestal/V-foot/twin-leg stand, a clamp arm, or a VESA wall bracket. A fixed no-DOF monitor is rejected (tilt is always articulated).

Not a TV cabinet, not a laptop, not an all-in-one PC, not a tablet, not a bare picture frame.

## 槽位 + 候选模块表

### Slot A：Stand support family (base topology — strongest structural axis)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| pillar_stand | forked_anchor | S1 / S7 | S1:L34-L127 / S7:L38-L223 | eligible if compatible | hex_base + slotted_pillar + top_crosshead/yoke head; tilt, optional swivel (base↔column split) |
| vfoot_neck | forked_anchor | S2 / S6 | S2:L119-L216 / S6:L123-L256 | eligible if compatible | wide V/T foot + tapered neck (swivel) + carriage (height) + tilt_barrel; carries flat OR curved panel |
| twin_leg | forked_anchor | S3 | S3:L58-L159 | eligible if compatible | two splayed A-frame legs (`leg_{i}`) meeting at a central column; tilt, optional swivel |
| wall_mount | forked_anchor | S5 | S5:L74-L196 | eligible if compatible | wall_plate + short mount_bracket + captured pivots; NO ground base, tilt only |
| ergo_arm | forked_anchor | S4 | S4:L179-L390 | eligible if compatible | desk_clamp + arm_lower/elbow/arm_upper + vesa_head; multi-revolute arm + tilt |

### Slot B：③ Primary Form Family (panel form)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| flat_16_10 | forked_anchor | S1 | S1:L129-L170 | Planar Boundary Form | flat Box+BezelGeometry panel, aspect ~1.6 |
| flat_16_9 | world_knowledge_extrapolation (③) | anchors: S1 + reviewer | n/a (same part tree, aspect param 1.78) | Planar Boundary Form | same flat screen part tree, retuned aspect |
| flat_ultrawide | world_knowledge_extrapolation (③) | anchors: S1 + S6 + reviewer | n/a (aspect param ~2.33, BOW=0) | Planar Boundary Form | flat 21:9 slab, same part tree |
| curved_21_9 | forked_anchor | S6 | S6:L48-L108 | Volumetric Envelope Form | concave lofted/meshed slab, aspect ~2.3, gentle bow |
| curved_32_9 | forked_anchor | S2 | S2:L46-L104 | Volumetric Envelope Form | concave super-ultrawide slab, aspect ~3.4, deep bow |

The curved candidates change the **Volumetric Envelope** (flat slab → concave bowed slab) keeping the same screen part tree (housing + glass + hinge_barrel) and primitive family (a meshed curved surface, matching the reference `desktop_monitor` `_curved_slab`); the flat candidates change the **Planar Boundary** (aspect ratio). ≥2 recognizable prototypes (flat vs curved) + aspect sub-variants cover the form-dominated ③ axis.

### Slot C：② stand MECHANISM (joint set on the panel↔support path)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| tilt_only | forked_anchor | S1 / S5 | S1:L172-L180 / S5:L184-L196 | eligible if compatible | 1 DOF: panel tilt REVOLUTE X (always present) |
| tilt_swivel | forked_anchor | S7 | S7:L196-L206 | eligible if compatible | + base↔column swivel REVOLUTE Z |
| tilt_portrait | forked_anchor | S8 | S8:L189-L208 | eligible if compatible | + pivot_hub portrait REVOLUTE Y (panel-normal, landscape↔portrait) |
| tilt_swivel_height | forked_anchor | S2 / S6 | S2:L182-L252 | eligible if compatible | + swivel REV Z + height PRISMATIC Z (vfoot 3-DOF ergonomic) |
| arm_shoulder_elbow_tilt | forked_anchor | S4 | S4:L340-L390 | eligible if compatible | shoulder REV Z + elbow REV X + panel tilt REV X (ergo_arm) |

Slot A and Slot C correlate (each carrier carries its own natural joint set) — mechanism is largely **derived** from the chosen stand family, with swivel/portrait as optional additions on the ground stands. Every mechanism keeps tilt (REVOLUTE X) so no seed is a fixed no-DOF monitor.

## 槽位图（slot graph）

pattern: mixed

```
                              (Slot B panel form: flat | curved)
                                          │  child = screen (hinge_barrel at frame origin)
                                          ▼
[Slot A carrier] --[tilt REVOLUTE X @ carrier hinge/barrel, rest rpy≈-0.12]--> [screen]

pillar_stand : base --[swivel REV Z @ collar (optional)]--> column(pillar+yoke) --[tilt]--> screen
vfoot_neck   : base_foot --[swivel REV Z]--> neck --[height PRIS Z]--> carriage(tilt_barrel) --[tilt]--> screen
twin_leg     : base --[swivel REV Z @ collar (optional)]--> column(legs+col+yoke) --[tilt]--> screen
wall_mount   : wall_plate --[FIXED]--> mount_bracket --[tilt]--> screen
ergo_arm     : desk_clamp --[shoulder REV Z]--> arm_lower --[elbow REV X]--> arm_upper --[FIXED]--> vesa_head --[tilt]--> screen
tilt_portrait (pillar/twin_leg only) : ... yoke --[tilt REV X]--> pivot_hub --[portrait REV Y]--> screen
```

Interface points:
- **screen↔carrier tilt**: pivot axis = the screen's `hinge_barrel` centerline (X). Joint origin placed ON the carrier hinge (yoke hinge_cheeks / carriage tilt_barrel / bracket pivots / vesa_head plate). Captured-trunnion pivot → MatingContract omitted (grandfathered, per AUTHORING §Rule 2 / like `monitor_mount`); seated overlaps declared element-scoped `allow_overlap`, motion proven by targeted `ctx.pose`.
- **swivel**: REVOLUTE Z at the base collar / neck hub; the carrier part frame sits at the swivel center, its visuals offset into that frame (S7 pattern).
- **height**: PRISMATIC Z carriage sliding on the neck (vfoot).
- **shoulder/elbow**: REVOLUTE at the arm bearing housings (captured-shaft, allow_overlap).
- **FIXED**: `wall_to_bracket`, `upper_to_vesa` — welded interfaces, origin on the mating face.

## 每槽位 Module Emits / Interfaces

### Slot A / pillar_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`{hex_base, base_collar} + `column`{slotted_pillar, top_crosshead, yoke_arm_{i}, hinge_cheek_{i}} (swivel) or single `stand` (no swivel) | S1 L91-127 / S7 L102-146 |
| internal joints | `base_to_column` REV Z (optional) | S7 L196-206 |
| downstream interface | tilt hinge @ (0, HINGE_Y, HINGE_Z) in carrier frame | S1 L172-180 |

### Slot A / vfoot_neck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base_foot`{base_foot_shell} + `neck_riser`{neck_riser_shell, swivel_hub} + `neck_carriage`{carriage_plate, tilt_barrel} | S2 L162-216 |
| internal joints | `base_to_neck_swivel` REV Z; `neck_to_carriage_height` PRIS Z | S2 L182-216 |
| downstream interface | tilt hinge @ carriage tilt_barrel | S2 L242-252 |

### Slot A / twin_leg
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand`/`column`{leg_{i}, foot_pad_{i}, central_column, junction_gusset, column_collar, top_crosshead, yoke_arm_{i}, hinge_cheek_{i}} | S3 L97-159 |
| internal joints | optional `base_to_column` REV Z | S7 analog |
| downstream interface | tilt hinge @ yoke | S3 L206-214 |

### Slot A / wall_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_plate`{plate_body} + `mount_bracket`{bracket_backplate, bracket_arm_{i}, bracket_pivot_{i}} | S5 L86-123 |
| internal joints | `wall_to_bracket` FIXED | S5 L176-182 |
| downstream interface | tilt hinge @ bracket pivots | S5 L184-196 |

### Slot A / ergo_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `desk_clamp`{clamp_body, clamp_bolt_{i}} + `arm_lower`{lower_beam, shoulder/elbow housings} + `arm_upper`{upper_beam, adapter} + `vesa_head`{bracket, plate, vesa_bolt_{i}} | S4 L193-288 |
| internal joints | `clamp_to_lower_arm` REV Z; `lower_to_upper_arm` REV X; `upper_to_vesa` FIXED | S4 L340-374 |
| downstream interface | tilt hinge @ vesa_head plate | S4 L379-390 |

### Slot B / flat panel (`screen`)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `screen`{rear_shell(Box), bezel(BezelGeometry), display_panel(Box), rear_mount(Box), hinge_barrel(Cyl)} | S1 L129-170 |
| internal joints | none (hinge is the cross-slot tilt joint) | — |
| upstream interface | `hinge_barrel` at frame origin captured by carrier tilt | S1 L165-170 |

### Slot B / curved panel (`screen`)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `screen`{panel_housing(curved mesh), screen_glass(curved mesh), vesa_mount(Box), hinge_barrel(Cyl)} | S2/S6 L219-234 |
| internal joints | none | — |
| upstream interface | `hinge_barrel` at frame origin (panel centered on hinge) | S2 analog |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| stand_family | enum | pillar_stand / vfoot_neck / twin_leg / wall_mount / ergo_arm | pillar_stand | choice | procedural sampler | Slot A |
| panel_form | enum | flat_16_10 / flat_16_9 / flat_ultrawide / curved_21_9 / curved_32_9 | flat_16_10 | choice | sampler; gated vs stand_family (§9) | Slot B |
| has_swivel | bool | {False, True} | True | conditional | only pillar_stand / twin_leg (vfoot always swivels; wall/arm never) | S7 / S1 |
| has_portrait | bool | {False, True} | False | conditional | only pillar/twin_leg AND aspect<2.0 AND not curved | S8 |
| material_style | enum | office_black / silver / white / gaming_red / brushed_alu / gunmetal (6) | office_black | choice | sampler | ⑥ |
| screen_width | float | [0.42, 0.95] | 0.58 | independent | uniform, clamp | S1/S2 dims |
| panel_aspect | float | derived | 1.6 | equation | = {16_10:1.60,16_9:1.78,ultrawide:2.33,curved_21_9:2.30,curved_32_9:3.40}[panel_form] | Slot B |
| panel_height | float | derived | — | equation | = screen_width / panel_aspect | S1 L211 |
| bezel | float | [0.008, 0.022] | 0.016 | independent | uniform, clamp | S1 L138 |
| curve_bow | float | derived | — | equation | curved_21_9→0.025, curved_32_9→0.050, flat→0.0 | S2/S6 |
| pillar_height | float | [0.30, 0.42] | 0.34 | independent | uniform, clamp (ground stands) | S1 L23 |
| height_travel | float | [0.030, 0.050] | 0.040 | conditional | vfoot only (PRIS), else 0 | S2 L215 |
| swivel_range | float | ±[0.5, 1.0] rad | ±0.7 | independent | REVOLUTE Z symmetric | S7 L204 |
| tilt_range | tuple | lower∈[-0.24,-0.16], upper∈[0.16,0.24] | (-0.22, 0.20) | independent | REVOLUTE X | S1 L179 |
| (—) | constraint | — | — | inequality | curved ⇒ stand∈{pillar,vfoot,twin_leg}; wall/arm ⇒ flat; portrait ⇒ flat aspect<2.0 | realism gate §9 |

连续尺寸采样契约: independent (screen_width, bezel, pillar_height, swivel/tilt) 先采 → equation (panel_height, panel_aspect, curve_bow) 派生 → conditional (height_travel, has_swivel, has_portrait, panel_form remap) 按 stand_family 解析。All resolved in `resolve_config`.

## 7.5 编译预算 / compile budget
Per-seed budget **≤ 12 s** (依据: mostly Box/Cylinder/BezelGeometry primitives; curved panels use a single pure-`MeshGeometry` curved slab, segments_x=28 / segments_z=6, one shell + one glass mesh, no cadquery boolean sculpting). Flat seeds ~3-6 s, curved seeds ~6-10 s. Small features ≤24 seg. Sweep hang-guard `--compile-timeout 120` (watchdog only).

## Multiplicity / Copy Logic

- 无独立可调 multiplicity 轴。核心结构由固定 named slots 表达，不暴露 tunable `*_count`。
- Structural for-loop pairs are FIXED at 2/4 (`yoke_arm_{i}`/`hinge_cheek_{i}`, twin `leg_{i}`/`foot_pad_{i}`, wall `bracket_arm_{i}`/`bracket_pivot_{i}`, arm `clamp_bolt_{i}`×2, `vesa_bolt_{i}`×4) — geometric symmetry pairs / hardware patterns from the sources, not a tunable N. Emitted via shared-helper `for i` loops (Rule 3/§4).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 5 stand skeletons (Slot A): pillar (base+column), vfoot (foot+neck+carriage), twin_leg, wall (plate+bracket), ergo_arm (clamp+2-link+head). part/joint counts 3↔6. forked_anchor S1/S2/S3/S4/S5/S7. |
| └ multiplicity | 同构件 ×N | 无 | 声明无 tunable N (see §8). |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE X (tilt, every seed), REVOLUTE Z (swivel S7 / shoulder S4), PRISMATIC Z (height S2), REVOLUTE Y (portrait S8), REVOLUTE X (elbow S4), FIXED (wall/arm welds). Each type realized across seeds. forked_anchor. |
| ③ 主体形态家族 | 换核心 part 的可识别几何原型 | 有 | flat slab (Planar Boundary: 16:10/16:9/ultrawide aspect) vs concave bowed slab (Volumetric Envelope: 21:9 gentle / 32:9 deep). Registered as `panel_form` in slot_choices. forked_anchor S1/S2/S6 + ③ extrapolation for flat aspect. |
| ④ 表面装饰 | 叠加表面细节 | 有 | bezel frame (BezelGeometry derived from panel W/H), rear_mount VESA boss, slotted_pillar cable slot, base_collar/column_collar ring — host part visuals, non-structural, hug ③/⑤. record_only. |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | screen_width [0.42,0.95], bezel [0.008,0.022], pillar_height [0.30,0.42], aspect 1.6-3.4. Joint envelopes: tilt REV X [-0.22,+0.20]; swivel REV Z ±[0.5,1.0]; height PRIS Z [0,0.05]; portrait REV Y [0,π/2]; shoulder REV Z ±2.6; elbow REV X [-0.30,1.80]. motion_test_plan: `fail_if_parts_overlap_in_sampled_poses` (max 48, ignore_fixed) + targeted `ctx.pose` per DOF. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | plastic housing + glass screen + metal base/foot; 6 palettes (office_black, silver, white, gaming_red accent, brushed_alu, gunmetal). 材质大类 ≥ ceil(0.5×6)=3 (plastic/glass/metal). |

## 拓扑多样性审计

总组合数：Slot A (5) × Slot B panel (flat 3 / curved 2, gated) × mechanism (derived + optional swivel/portrait ≈5) × material (6) — legal-combo space > 200.


seed_domain_policy：procedural_first (seed 0 不特殊)。

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` uses `random.Random(seed)` to weight-pick stand_family, panel_form, material, and continuous dims; `resolve_config` applies the realism gates (curved⇒ground stand; wall/arm⇒flat; portrait⇒flat aspect<2.0 on pillar/twin_leg) and clamps. Compatibility matrix avoids absurd/collision-prone combos. No regression overrides. Sweep seeds 0-35 for the pass; corner stage probes numeric extremes + unrealized combos.

Topology target: 1000-seed distinct expected 按 ≥300 report-only 口径观察.

Controlled local parameterization: screen_width, bezel, pillar_height, swivel_range, tilt_range, height_travel — clamped/derived in `resolve_config`; none break the tilt interface, swivel/height clearance, joint origins, or identity.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted slot pick + gated remap in resolve_config | slot_choices_for_seed matches build choices |
| compatibility matrix | curved⇒{pillar,vfoot,twin_leg}; wall/arm⇒flat; portrait⇒pillar/twin_leg flat aspect<2.0 | no floating panel, no mid-tilt/portrait穿模, correct tilt axis |
| controlled local variation | continuous dims clamped/derived | proportions vary without breaking interfaces/clearance/identity |
| regression overrides | none | — |
| random sweep | 0-35 initial pass, 0-999 maturity | contract failures; axis_realization report |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A stand_family | 5 | yes | yes | |
| B panel_form | 5 | yes | yes | flat 3 + curved 2 |
| C mechanism | 5 | yes | yes | derived + optional swivel/portrait |
| material_style | 6 | yes | yes | |

## Validator

- slot_choices_for_seed returns implemented module names (stand_family, panel_form, stand_mechanism, material_style)
- config_from_seed uses deterministic procedural sampling for all seeds incl. seed 0
- compatibility gates prevent illegal combos (curved-on-wall/arm, portrait-on-ultrawide)
- every seed keeps the tilt REVOLUTE-X joint; ≥1 non-FIXED joint always
- captured-pin tilt/swivel joints omit MatingContract (grandfathered) with element-scoped allow_overlap + expect_contact; FIXED welds place origin on the mating face
- key joints have expected type/axis/range; panel hinge_barrel contains part-frame origin
- controlled scales clamped in resolve_config
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per DOF

## Reject cases

- Panel floating: hinge_barrel not captured by the carrier yoke/bracket/barrel (isolated part).
- Fixed no-DOF monitor: tilt joint missing or FIXED — rejected.
- Curved panel on wall/arm or portrait on ultrawide: illegal combo escaped the gate.
- Mid-tilt / mid-portrait穿模: panel sweeps into the column/pillar/base at a sampled pose.
- Bezel detached: bezel built at a constant size not derived from the (final) panel W/H.
- Downgraded primitive: curved panel emitted as a plain flat Box instead of a bowed mesh slab.
- Swivel column lifts/drops off the base (wrong swivel origin z).
- Arm self-collision at extreme shoulder/elbow poses without a declared captured-shaft allowance.

## 与相邻类别的边界

- 不该混入：TV / television（TV 是更大的独立整机，常挂墙或落地柜，无 desk swivel/height 人机工学 stand；monitor 以 desk stand + tilt/swivel/height 为身份）。
- 不该混入：Laptop（笔电是屏+键盘铰接一体，无独立 desk stand）。
- 不该混入：all-in-one PC / tablet / picture frame（monitor 必须有可倾斜支架且面板是显示屏，不是无 DOF 相框或含主机一体机）。
- 不该混入：`desktop_monitor_with_tilt_swivel_stand` orphan（同物；本 modular 模板取代它作为 Technology_Monitor 的正式模板，并加入 curved-ultrawide / wall / arm / twin-leg / portrait 家族）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 8/8 5★ sources read + cited (S1-S8). All candidates forked_anchor with real Lx-Ly except flat aspect ③ extrapolation (world_knowledge, same part tree). §8.5 6-axis + §9 audit + §7.5 budget present. Captured-pin tilt/swivel grandfather MatingContract per AUTHORING Rule 2 (like monitor_mount). |
