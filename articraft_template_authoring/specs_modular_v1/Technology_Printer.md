# Technology_Printer — Modular Spec

> Finished from the scaffold. Slot decomposition, candidates, ranges, §8.5 6-axis,
> §9 audit and §7.5 budget resolved against the 9 rating-5 sources. Parallel-children
> pattern (all slot parts parent to the root `body`), mirroring the reference
> `dishwasher_with_dropdown_door_and_sliding_racks` (drop-down door REVOLUTE +
> sliding racks PRISMATIC → scanner-lid REVOLUTE + fold-out trays PRISMATIC).

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Printer` |
| template path | `agent/templates/Technology_Printer.py` |
| test path (optional) | `tests/agent/test_Technology_Printer_template.py` (not written) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children slots on `body` + multiplicity axis on control-panel buttons) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (3 origins + 6 variants), each `model.py` read fully |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：

- **DeskJet origin** (`rec_a-white-hp-deskjet-...c7dd9a61`, 398L): compact rounded cadquery body with a front output-bay cut (L25-46); flatbed `scanner_lid` REVOLUTE rear hinge, axis `(-1,0,0)`, lid extends `-Y` so +q lifts the front edge (L127-160); rear `rear_tray` FIXED upright feed + `paper_stack` FIXED (L162-208); front `output_tray` FIXED shelf + `extension_arm` PRISMATIC pull-out along `-Y` (L210-256); 3 PRISMATIC push-buttons on a top control deck (L258-278).
- **OfficeJet origin** (`...bbac26a7`, 213L): boxy `chassis` with split lower side blocks around a drawer bay (L53-84); ADF `scanner_lid` (flatbed slab + ADF hump cover/feed-face/top-tray) REVOLUTE rear hinge (L106-124); front-bottom `input_tray` PRISMATIC pull-out cassette (L128-144); FIXED flush touchscreen bezel/glass/icons as chassis visuals — no moving panel (L72-77).
- **Brother origin** (`...9cae5bca`, 454L): rounded cadquery body with output-slot + panel recess cuts (L57-90); flatbed `scanner_lid` REVOLUTE rear hinge (L178-211); front `output_tray` PRISMATIC pull-out (L213-250) with nested `paper_stopper` REVOLUTE flip-up flap on the tray front edge (L252-282); a clean `for i,bx in enumerate(btn_xs)` button loop → `button_{i}` PRISMATIC press-inward (`+Y`) (L284-337).
- **Variants** (each rating-5): `singlefunction` — domed closed top deck, scanner_lid REMOVED, print-only (L114-119); `workgroup` — `z_lift` tall pedestal body, same ADF top (L54-131); `inktank` — external `tank_housing` + translucent CMYK `tank_window_{i}` + `tank_cap_{i}` bulging `+X` (L103-122, L177-222); `foldinput` — `body_to_rear_tray` re-typed FIXED→REVOLUTE fold, paper rides along (L162-193); `tiltpanel` — separate `control_panel` part, `chassis_to_control_panel` REVOLUTE bottom-edge hinge tilts out (L74-96); `buttoncount` — `btn_xs = tuple(-0.118+i*0.020 for i in range(6))` → N=6 buttons (L293).

## 核心身份

An inkjet **all-in-one (AIO) printer**: a grounded rectangular plastic housing (print engine) with a **flatbed scanner / document-cover on top** that opens on a rear hinge, **paper handling** (a rear-feed or front cassette input plus a front output tray/extension), and an **operator control panel** (a button strip, a flush touchscreen, or a tilting touchscreen) on the upper-front face. Default mature domain: compact desktop and small-office inkjet AIOs (multi-function print+scan+copy), including EcoTank/supertank and tall workgroup envelopes. Every unit keeps at least one working joint (scanner lid, paper tray, output extension, fold-out rear support, tilt panel, or push-buttons) — never a sealed box.

Not to be confused with: a standalone flatbed **scanner/copier** (no print engine / paper output stack), a **fax machine** (telephony, handset, no scanner glass lid semantics), or a **3D printer / plotter** (gantry motion, no flatbed lid). Those neighbors are excluded at the identity boundary (§11).

## 槽位 + 候选模块表

All slots are **parallel children of the root `body` part** (the print engine housing). Non-moving structure (feed supports, output shelves, badges, screens, tank) is folded into `body` visuals per AUTHORING §A Rule 1; only articulating pieces become separate parts.

### Slot A：primary_form_family（③ 主体形态家族 + scanner/top structure）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| flatbed_scanner_top | forked_anchor | DeskJet + Brother origins | DeskJet L127-160 / Brother L178-211 | eligible if compatible | rounded (cadquery filleted+bay-cut) compact body; flatbed `scanner_lid` (flat rounded panel + glass underlay + hinge barrel) REVOLUTE rear hinge axis `-X`, +q lifts front edge |
| adf_document_feeder_top | forked_anchor | OfficeJet origin | L53-84 / L106-124 | eligible if compatible | boxy Box body; `scanner_lid` = flatbed slab + ADF hump (upper cover, white feed face, top tray, front bevel) REVOLUTE rear hinge |
| flat_top_no_scanner | forked_anchor | `rec_printer_var_singlefunction` (←DeskJet) | L41-48, L114-119 | eligible if compatible | rounded body, closed **domed top deck** body-visual; scanner_lid + hinge REMOVED (print-only). Articulation comes from paper handling / panel |
| tall_workgroup_body | forked_anchor | `rec_printer_var_workgroup` (←OfficeJet) | L54-131 | eligible if compatible | tall boxy pedestal (`z_lift` grows lower base, +dark base band), same ADF top |
| ink_tank_supertank | forked_anchor | `rec_printer_var_inktank` (←Brother) | L103-122, L177-222 | eligible if compatible | rounded body + external `tank_housing` bulge (`+X`) with translucent CMYK `tank_window_{i}` + `tank_cap_{i}`; flatbed top |
| wide_format_extra | world_knowledge_extrapolation (Volumetric Envelope Form) | anchors: 5 above + reviewer | n/a (`_build_body`, form="wide_format") | eligible if compatible | same part tree / same primitives / same interfaces; wider-shallower A3 envelope, flatbed top. form_subtype = Volumetric Envelope Form |

### Slot B：paper_handling（② input+output tray joint types; parallel children of `body`）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rear_feed_output_extension | forked_anchor | DeskJet origin | L162-256 | eligible if compatible | rear upright feed + paper (body visuals) + front output shelf (body visual) + `extension_arm` **PRISMATIC** pull-out `-Y` |
| front_cassette_drawer | forked_anchor | OfficeJet origin | L128-144 | eligible if compatible | bottom-front `input_tray` **PRISMATIC** pull-out cassette (floor+sides+front panel+paper) + front output shelf visual |
| front_output_tray_stopper | forked_anchor | Brother origin | L213-282 | eligible if compatible | front `output_tray` **PRISMATIC** pull-out + nested `paper_stopper` **REVOLUTE** flip-up on tray front edge |
| foldout_rear_input | forked_anchor | `rec_printer_var_foldinput` (←DeskJet) | L162-193 | eligible if compatible | rear-top `rear_tray` **REVOLUTE** fold (flat-rearward↔upright), paper rides along; + front output shelf visual |

### Slot C：control_panel（② operator-panel joint type + multiplicity）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| flat_button_strip | forked_anchor | Brother (L284-337) + DeskJet (L258-278) + buttoncount (L293) | as cited | eligible if compatible | panel band body-visual + display + N round `button_{i}` parts, each `body_to_button_{i}` **PRISMATIC** press-inward `+Y`. **Carries the multiplicity axis** (N buttons) |
| fixed_flush_touchscreen | forked_anchor | OfficeJet origin | L72-77 | eligible if compatible | flush touchscreen bezel + lit glass + colored app icons as **body visuals** (FIXED, no moving part) |
| tilting_touchscreen_panel | forked_anchor | `rec_printer_var_tiltpanel` (←OfficeJet) | L74-96 | eligible if compatible | separate `control_panel` part, `body_to_control_panel` **REVOLUTE** bottom-edge hinge tilts screen out toward user |

硬约束满足：每 slot ≥3 candidates（A=6, B=4, C=3），全部 `forked_anchor`（A 的 `wide_format_extra` 为 ③-form `world_knowledge_extrapolation`，同 part tree/primitive/interface）。

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                         body (root: print-engine housing, grounded)
                          │  top face (z=body_top, rear hinge line y≈rear_y)
   ┌──────────────────────┼───────────────────────────────┬─────────────────────┐
   │ Slot A top           │ Slot B paper_handling          │ Slot C control_panel│
   │ [REVOLUTE axis -X    │ [PRISMATIC -Y] or              │ [PRISMATIC +Y ×N]   │
   │  rear hinge, or none]│ [REVOLUTE fold] (+nested       │  or [REVOLUTE tilt] │
   scanner_lid            │  REVOLUTE stopper on tray)     │  or [none/visuals]  │
                       extension_arm / input_tray /        buttons_{i} /
                       output_tray→paper_stopper /         control_panel
                       rear_tray(fold)
```

- **Parent relation:** every slot part is a direct child of `body` (parallel children). The only serial nesting is `output_tray → paper_stopper` (REVOLUTE) inside Slot B (Brother).
- **Interface points:** scanner_lid mates on the **body top face** at the rear hinge line (`z=body_top`, `y=rear_y-ε`); it seats on the top (contact) and covers the flatbed footprint (xy overlap). Paper parts mate at the **front face** slot lip (`y=front_y`, output z≈0.06 / cassette z≈0.02) or the **rear-top edge** (fold). Buttons/panel mate on the **upper-front panel band** (`y=front_y`, `z≈body_top-0.04`). Tilt panel hinges at the **panel bottom edge** (`y=front_y`, `z≈body_top-0.09`).
- **Joint types/axes/ranges:** scanner_lid REVOLUTE `-X` `[0, 1.20]`; extension_arm / input_tray / output_tray PRISMATIC `-Y` (travel below); paper_stopper REVOLUTE `-X` `[0, 80°]`; rear_tray fold REVOLUTE `-X` `[0, 1.35]`; buttons PRISMATIC `+Y` `[0, 1.5mm]`; tilt panel REVOLUTE `+X` `[0, 0.62]`.
- **Mutual exclusion / derivation:** `flat_top_no_scanner` and `wide_format_extra` control whether a scanner lid exists; the paper-handling slot ALWAYS supplies ≥1 non-FIXED joint, guaranteeing every seed keeps a working joint even when Slot A has no lid and Slot C is a fixed touchscreen.

## 每槽位 Module Emits / Interfaces

### Slot A / module flatbed_scanner_top / adf_document_feeder_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_lid` | DeskJet L127 / OfficeJet L106 |
| internal joints | `body_to_scanner_lid` REVOLUTE, axis `(-1,0,0)`, origin at rear-top hinge line, `[0,1.20]` | DeskJet L152-160 / OfficeJet L116-124 |
| upstream interface | seats on body **top face** `z=body_top`; lid frame dips −0.003 to contact; covers flatbed xy | Brother L93-109, L369-377 |
| downstream interface | none (leaf) | — |

### Slot A / module flat_top_no_scanner / wide_format_extra
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (Slot A contributes only body visuals) | singlefunction L114-119 |
| internal joints | none | singlefunction (scanner joint removed) |
| body visuals | domed/flat closed top deck | singlefunction L41-48 |

### Slot B / paper_handling (all parents = body)
| emits | 描述 | 来源 |
|---|---|---|
| parts | one of: `extension_arm` (PRISMATIC) / `input_tray` (PRISMATIC) / `output_tray` (PRISMATIC)+`paper_stopper` (REVOLUTE) / `rear_tray` (REVOLUTE fold) | DeskJet L235-256 / OfficeJet L128-144 / Brother L213-282 / foldinput L162-193 |
| internal joints | `body_to_extension_arm`/`body_to_input_tray`/`body_to_output_tray`(+`output_tray_to_paper_stopper`)/`body_to_rear_tray` | as cited |
| upstream interface | front slot lip `y=front_y` (prismatic, `-Y`) or rear-top edge (fold, `-X`) | Brother L236-250 |
| body visuals | rear feed support + paper + front output shelf + output shadow | DeskJet L162-208 |

### Slot C / control_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `button_{i}` ×N (PRISMATIC) / none / `control_panel` (REVOLUTE tilt) | Brother L284-337 / OfficeJet L72-77 / tiltpanel L74-96 |
| internal joints | `body_to_button_{i}` PRISMATIC `+Y` `[0,1.5mm]` / — / `body_to_control_panel` REVOLUTE `+X` `[0,0.62]` | as cited |
| upstream interface | upper-front panel band `y=front_y`, `z≈body_top-0.04` | Brother L42-46 |
| body visuals | panel band + display + icons + brand plate | Brother L131-170 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| form_family (Slot A) | enum | {flatbed_scanner_top, adf_document_feeder_top, flat_top_no_scanner, tall_workgroup_body, ink_tank_supertank, wide_format_extra} | flatbed_scanner_top | choice | procedural sampler | Slot A table |
| paper_handling (Slot B) | enum | {rear_feed_output_extension, front_cassette_drawer, front_output_tray_stopper, foldout_rear_input} | front_output_tray_stopper | choice | procedural sampler | Slot B table |
| control_panel (Slot C) | enum | {flat_button_strip, fixed_flush_touchscreen, tilting_touchscreen_panel} | flat_button_strip | choice | procedural sampler | Slot C table |
| button_count (N) | int | [2, 8] | 4 | conditional | only when control_panel=flat_button_strip; else N=0 (not built) | buttoncount L293 |
| palette_style | enum | {warm_white, office_white_gray, brother_offwhite, charcoal_workgroup, supertank_white, graphite_two_tone} (6) | warm_white | choice | procedural sampler → mats[...] | ⑥ below |
| width_scale | float | [0.90, 1.12] | 1.0 | independent | body width `BW·width_scale`, clamp | ⑤ (DeskJet 0.43 / OfficeJet 0.50 / Brother 0.40) |
| depth_scale | float | [0.92, 1.10] | 1.0 | independent | body depth `BD·depth_scale`, clamp | ⑤ (0.31–0.42) |
| height_scale | float | [0.92, 1.12] | 1.0 | independent | body height `BH·height_scale`, clamp | ⑤ (compact 0.13–0.17; workgroup taller) |
| lid_open_scale | float | [0.85, 1.0] | 1.0 | equation | `lid upper = 1.20·lid_open_scale` (clearance-safe) | DeskJet L159 |
| tray_travel | float | derived | — | equation | `= min(0.16, body_depth·0.42)·depth_scale` | OfficeJet L143 / DeskJet L255 |
| (—) | constraint | — | — | inequality | button row span `(N-1)·0.024 ≤ panel_w-0.03`; if violated shrink spacing | Brother L293 |
| (—) | constraint | — | — | conditional | tall_workgroup_body forces BH≥0.26; wide_format widens BW, shrinks BH | workgroup L54-58 |

连续采样契约：先采 width/depth/height_scale (independent, uniform) → 派生 body dims, tray_travel, lid upper (equation) → button spacing 投影回缩 (inequality) → N 与 workgroup/wide dims 按上游 enum 解析 (conditional)。全部在 `resolve_config` 求解。

## 7.5 编译预算 / compile budget

自报预算 **≤18 s/seed**（依据：库内典型模板 5–20s；本类别几何以 Box 为主，rounded / ink-tank / flat-top 三个 form 用单个 cadquery filleted+cut/union mesh，`tolerance=0.001–0.002`，与 5★ 源同量级，源实测均在预算内）。分档 tessellation：cadquery fillet 半径特征 ≤ 默认段数；N 个按钮共用同一 `Cylinder` 原语（无 per-N 独立 mesh）。sweep `--compile-timeout 120`（3–6× 预算的看门狗，非质量门）。超预算先降 cadquery 精度再迭代。

## Multiplicity / Copy Logic

- **1 根 multiplicity 轴：** `button_count` (control-panel round push-buttons).
- `count_param` = `button_count`; `N_range` = **[2, 8]** (typical inkjet operator panels; 样本覆盖 N∈{3 DeskJet, 4 Brother, 6 buttoncount}); sampling domain = 在 [2,8] 均匀采样（窄域，直接采 raw N，小 N 常见）。
- copied object / naming / placement / joint policy: round `Cylinder(radius≈0.0095, length≈0.010)` cap; part `button_{i}`; evenly spaced along **X** on the panel band at constant Y/Z (`btn_xs` linspace centered on the panel, spacing clamped by inequality above); each cap an independent `body_to_button_{i}` **PRISMATIC** press-in (`+Y`, `[0,1.5mm]`) child of `body`. Source/gating: only built when `control_panel=flat_button_strip`; other panel candidates set N=0.
- 备注: DeskJet `feed_roller_{0,1,2}` and paper-width guides are **not** modeled as a multiplicity axis (folded into body visuals as decoration, per Rule 1); only the panel-button axis is a real copy loop.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | body(root) + {scanner_lid?} + {extension_arm / input_tray / output_tray(→paper_stopper) / rear_tray} + {button_{i}×N / control_panel / —}. Part/joint count varies by Slot A×B×C. forked_anchor (all 9 sources). |
| └ multiplicity | 同构件 ×N | 有 | button_count N∈[2,8], 见 §8 (buttoncount L293). |
| ② 关节类型 | 图不变换 type/轴 | 有 | scanner_lid REVOLUTE `-X`; extension/input/output tray PRISMATIC `-Y`; paper_stopper REVOLUTE `-X`; rear_tray fold REVOLUTE `-X`; buttons PRISMATIC `+Y`; tilt panel REVOLUTE `+X`. 每种都在 sweep 出现。forked_anchor (DeskJet/OfficeJet/Brother/foldinput/tiltpanel). |
| ③ 主体形态家族 | 换核心 part 几何原型（非缩放/换色） | 有 | 登记进 `slot_choices` 的 Slot A：flatbed_scanner_top / adf_feeder_top / flat_top_no_scanner / tall_workgroup_body / ink_tank_supertank (source-backed anchors) + wide_format_extra (`world_knowledge_extrapolation`, form_subtype=**Volumetric Envelope Form**). flat_top=**Macro Surface Construction** (closed domed top vs hinged lid); ink_tank=**Macro Surface Construction** (side reservoir bulge); workgroup=**Volumetric Envelope Form** (tall pedestal). |
| ④ 表面装饰 | 叠加表面细节 | 有 | HP roundel/strokes, brand plate, deskjet label, output-slot dark shadow, feed rollers, screen app-icons, cartridge seams, ink-level windows/caps + label strip. `record_only` + `world_knowledge_extrapolation`; 全部作为宿主 `body`/`scanner_lid` visual，随 ③ form 与 ⑤ 尺寸共形放置（派生顺序 ③→⑤→④）。 |
| ⑤ 尺寸/行程 | 只改连续尺寸/行程 | 有 | body W 0.40–0.50·[0.90,1.12], D 0.31–0.42·[0.92,1.10], H compact 0.14–0.17 / workgroup ≥0.26; 行程见下。**每个非-continuous 关节运动包络 + motion_test_plan**：<br>• scanner_lid REVOLUTE `-X` `[0, 1.20·lid_open_scale]` — sampled collision + targeted `pose(lid:open)` 断言 front-edge top-z 上升 >0.10。<br>• extension/input/output tray PRISMATIC `-Y` `[0, tray_travel]` — sampled + targeted pose 断言 front `y` 减小、retained overlap。<br>• paper_stopper REVOLUTE `-X` `[0, 80°]` — sampled + targeted pose 断言 top-z 上升。<br>• rear_tray fold REVOLUTE `-X` `[0, 1.35]` — sampled + targeted pose 断言 top-z 上升。<br>• buttons PRISMATIC `+Y` `[0, 1.5mm]` — sampled + targeted pose 断言 press-in。<br>• tilt panel REVOLUTE `+X` `[0, 0.62]` — sampled + targeted pose 断言 tilt-out `-Y`. 全程不穿模，intentional seat/retain overlaps 以 element-scoped `allow_overlap` 声明。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 plastic (matte/off-white/charcoal) + glass (scanner) + translucent ink (tank) + lit screen. 配色 6: warm_white, office_white_gray, brother_offwhite, charcoal_workgroup, supertank_white, graphite_two_tone (覆盖 white / white+gray / black/charcoal / two-tone)。`palette_style` per-seed → `mats[...]` 驱动每个 `.visual`。material 大类覆盖 ≥ ceil(0.5×6)=3. record_only. |

收尾自检：`template batch 0-9` 应肉眼可见 rounded↔boxy↔tall↔domed↔tank↔wide 形态拉开、白/灰/黑配色都出现、装饰贴合、开合全程不穿模。

## 拓扑多样性审计

总组合数：A(6) × B(4) × C(3) = **72** slot 组合；乘 button_count N∈[2,8] (7 值，仅 flat_button_strip) → 有效拓扑上界 ≈ 6×4×(1 + 1 + 7) = 216（C 的 touchscreen/tilt 各 1，button strip 7 个 N）。加 palette(6) 与连续 scale → 1000-seed distinct 远超 100。


seed_domain_policy：procedural_first（`config_from_seed(seed)` 用 `random.Random(seed)` 逐 slot 加权采样，seed=0 不特殊）。

Procedural Sampling / Sweep Plan：per-seed `rng` 依次选 form_family, paper_handling, control_panel (均匀); button_count 仅当 flat_button_strip 时在 [2,8] 采样; palette_style 均匀; 3 个 scale uniform。`resolve_config` clamp 全部连续量、按 form 解析 conditional dims、投影 button spacing。Compatibility：无非法组合被完全禁止；两处 cross-slot 风险（ADF-top × 前 output tray 的 hump 净空、tilt-panel × front cassette 的前脸争用）经几何分层（lid 几何 z≥body_top；panel z≈body_top−0.04；cassette z≈0.02；output z≈0.06）避免碰撞，剩余共享包络以 element-scoped `allow_overlap` 声明并保留全行程。regression overrides: none。random sweep 0-35 初验，viewer 目检 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 >150。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：width_scale/depth_scale/height_scale (independent, clamp)，lid upper / tray_travel (equation 派生)，button spacing (inequality 回缩)。均在 `resolve_config` 求解，不破坏 body-top 接口、front-slot 接口、hinge 轴或 button multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 form→paper→panel→N→palette→scales, 均匀/加权 choice | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 无硬互斥；cross-slot 风险以几何分层 + element-scoped allow_overlap 处理，保留全行程 | 无 floating / collision / axis / retained-tray / bulky module 失败 |
| controlled local variation | 3 scale + 派生行程，clamp | 比例变化不破坏接口/净空/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初验 pass；0-999 成熟审计 | contract 失败；axis_realization / report |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A primary_form_family | 6 | yes | yes | 5 forked_anchor + 1 ③-form world_knowledge |
| B paper_handling | 4 | yes | yes | all forked_anchor |
| C control_panel | 3 | yes | yes | all forked_anchor; carries multiplicity |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (form_family, paper_handling, control_panel, button_count).
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds incl. seed 0.
- compatibility handled by geometric layering + element-scoped allow_overlap; no illegal combination禁用.
- no regression overrides.
- continuous scales clamped/derived in `resolve_config`; cross-part deps (tray_travel, lid upper, button spacing) resolved there, not in builder.
- critical contact/retain interfaces exist (lid seats on top; trays retained in slot; buttons seated in panel bore) — connectivity via contact/overlap, intentional overlaps grandfathered by element-scoped allow_overlap (matches 5★ sources + dishwasher reference; MatingContract omitted for these seat/capture interfaces as the sources and reference do).
- key joints: scanner_lid REVOLUTE `-X`; trays PRISMATIC `-Y`; paper_stopper/rear_tray/tilt REVOLUTE; buttons PRISMATIC `+Y`.
- every seed keeps ≥1 non-FIXED joint (paper_handling guarantees it).
- copied buttons follow `button_{i}` naming + even X spacing.
- Rule 5: `run_printer_tests` calls `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose(...)` per mechanism.

## Reject cases

- Scanner lid authored so +q swings the lid backward over the rear (wrong hinge axis sign) → 穿模 / lid opens down. (Must lift front edge up like sources.)
- A sealed box: form=flat_top + panel=fixed_touchscreen but paper module dropped → 0 non-FIXED joints. (Paper slot must always emit a joint.)
- Output tray / cassette pulled so far it detaches (no retained overlap with body) → isolated/floating part.
- Buttons over-spaced so the row exceeds the panel band, or button caps floating off the panel (no seat) → island / far-origin.
- Constant-radius decoration (badge/label) not conforming to the rounded body surface across ③/⑤ → detached decoration (Rule 4).
- Downgrading the rounded cadquery body / ink-tank housing / ADF hump to a crude single Box for a form that the source builds as a shaped mesh (Rule 3).
- Broad part-level `allow_overlap` masking a real mid-travel collision instead of fixing axis/range/clearance.

## 与相邻类别的边界

- 不该混入：standalone flatbed **scanner/copier**（无 print engine / 无 paper 输出 stack；printer 必须有 output tray + 打印机身）。
- 不该混入：**fax machine**（telephony/handset 语义；无 scanner-glass 文档盖 + 出纸 AIO 结构）。
- 不该混入：**3D printer / plotter**（gantry / 龙门运动；本类别是 flatbed 平板扫描盖 + 平面进出纸，非三维打印头）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Finished from scaffold; all 25 TODOs resolved against 9 rating-5 sources with real model.py:Lx-Ly citations. Parallel-children pattern per dishwasher reference. |

## 模板实现备注（可选）

- 共享 helper：`_box`, `_cyl`, `_rounded_shell` (cadquery, rounded/tank/flat-top forms only). N buttons share one `Cylinder` primitive.
- Seat/capture interfaces (lid-on-top, tray-in-slot, button-in-bore, stopper-on-tray, tilt-bezel-on-face) use connectivity contact + element-scoped `allow_overlap` (grandfathered), NOT MatingContract — mirroring the 5★ sources and the dishwasher reference, the proven-passing idiom for this hinge/slide topology.
- Cross-slot allowances: only where a moving part shares the front/top envelope with a body visual at the closed pose; declared element-scoped with a sequence/seat reason, full travel retained.
