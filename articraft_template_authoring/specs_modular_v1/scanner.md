# scanner — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `scanner` |
| template path | `agent/templates/scanner.py` |
| test path (optional) | `tests/agent/test_scanner_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 forked_anchor variants + 3 origin_anchors (11 total; 40 canonical flatbed parents also on disk) |
| read_count | 8 forked-anchor variants read in full (portable_slim, control_tilting_panel, feed_duplex_trays, feed_hinged_adf, lid_rising_book_hinge, scan_motion_visible_prismatic_scan_bar, scanner_topology_book_scanner, scanner_topology_sheet_fed) |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

Recurring structural spine across every variant:

- **Single root** (`scanner_body` / `chassis` / `base`) — a low, wide rounded prism, most variants carve a shallow **recessed platen well** on top; sheet-fed collapses the well into an internal scan strip inside a compact box.
- **Platen assembly** (glass patch + optional bezel + reference strip) is a `FIXED`-jointed part in some variants and inline `parent.visual(...)` in others; both encode the same non-moving scan bed.
- **Lid** (a graphite / dark panel with an inner pressure pad + hinge knuckles) is the ONE guaranteed non-`FIXED` articulation — a rear `REVOLUTE -X` hinge that opens ~65-90° upward. The topology-varying candidates are:
  - simple back-of-body pin hinge (portable_slim, book_scanner, sheet_fed).
  - rising_book_hinge — the same lid but the hinge origin sits on tower-and-slot brackets that raise the pivot line above the housing.
  - hinged_adf — the lid becomes an ADF tray carrier with a second `REVOLUTE -X` sub-lid (the ADF cover) parented to the lid; the tray/roller detail lives inside.
  - fixed_lid degrades to a bolt-down cover if the lid isn't articulated (never selected in the 5★ pool; excluded).
- **Control zone** on the front strip of the housing — every variant sports one or more PRISMATIC push buttons (0.8-1.5 mm downward travel, effort ≈ 2-4 N). Candidates: `control_ring_button` (single central scan button ringed by a bezel — parents), `dual_button_deck` (power + scan buttons on a molded deck — book_scanner), `quad_button_row` (four labeled buttons — hinged_adf), and `tilting_control_panel` (control_tilting_panel — the whole panel is REVOLUTE +X, buttons ride on top).
- **Status lens** (a small green/amber indicator cylinder embedded in the housing edge) appears on all variants as a non-moving `parent.visual(...)` (Rule 1).
- **Feet** (4 rubber/plastic pads under the housing) appear as `parent.visual(...)` on every variant.

## 核心身份

A **document scanner**: a real-world office/home peripheral whose sole job is to convert paper into digital images. The signature form is a **low, wide, rounded rectangular chassis** with a **glass platen** on top (or internal scan strip for sheet-fed) and a **rear-hinged lid** that opens upward to load paper. It is **not** an all-in-one printer / MFP (has no output tray, paper cassette, or printhead assembly), **not** a copier (no cover-catching output shelf), **not** a fax, **not** a barcode/handheld/gun scanner, **not** a 3D scanner. Motion is dominated by (1) the lid hinge and (2) tiny push-button PRISMATICs; heavier articulation (ADF sub-lid, tilting panel, rising book bracket) is real but bounded — 1-3 non-`FIXED` joints total.

## 槽位 + 候选模块表

### Slot A：`body_form`  (③ Primary Form Family, plus platen wiring)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flatbed_full` | forked_anchor | `rec_0611_scanner_var_control_tilting_panel` from picture 001 | L44-L73 (`_scanner_housing_shape`), L76-L83 (`_lid_panel_shape`) | eligible if compatible | Volumetric Envelope Form. Wide chassis 0.45×0.36×0.076 m with a large deep recessed platen well (0.342×0.250, well depth 0.032). Four cylindrical feet, rear hinge line at Y≈0.164, Z≈0.096. |
| `flatbed_slim` | forked_anchor | `rec_0611_scanner_var_body_form_portable_slim` from picture 001 | L28-L82 (`_scanner_housing_shape`, `_lid_panel_shape`) | eligible if compatible | Volumetric Envelope Form. Slim chassis 0.43×0.34×**0.030** m (housing z-extent <50 mm — tests assert this) with a shallow (0.010 deep) platen well. Low hinge line Z≈0.042. |
| `sheet_fed` | forked_anchor | `rec_0611_scanner_var_scanner_topology_sheet_fed` from picture 001 | L44-L96 (housing with feed slots), L88-L95 (lid) | eligible if compatible | Macro Surface Construction change. Compact 0.40×0.16×0.088 m tall-narrow enclosure, **no top platen well** (platen sits INSIDE the body as an internal scan strip); front intake slot + rear output slot are cut through the shell. Lid still hinges but only covers the internal strip. |
| `book_edge_flatbed` | forked_anchor | `rec_0611_scanner_var_scanner_topology_book_scanner` from picture 002 | L44-L98 (housing with book_edge cut), L139-L157 (ramp) | eligible if compatible | Planar Boundary Form change. Portrait 0.31×0.455×~0.09 m chassis where the **right-side upper wall is removed** and a wedge ramp connects the platen edge to the lower shell — allows a bound book spine to overhang. Rear hinge line Y≈0.207, Z≈0.062. |

### Slot B：`lid_mechanism`  (①/② — the primary hinge topology)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `simple_hinge` | forked_anchor | `rec_0611_scanner_var_body_form_portable_slim` (also portable_slim + sheet_fed use identical topology) | L128-L279 (body knuckles + hinge_pin + lid REVOLUTE `-X`) | eligible if compatible | 1 REVOLUTE `-X` from body to lid. Body carries 2-3 fixed rear knuckles + a continuous hinge pin; lid carries 2 rotating knuckles + panel + inner pad. Opens ≈65-95° upward. |
| `rising_book_hinge` | forked_anchor | `rec_0611_scanner_var_lid_rising_book_hinge` from picture 003 | L44-L92 (`_base_hinge_shape` towers + slots), L94-L145 (`_lid_hinge_shape` link arms + pivot pins) | eligible if compatible | Same 1 REVOLUTE `-X` joint, but the hinge origin is raised ~15 mm on a pair of towers with vertical guide slots; the lid carries L-shaped link-arm brackets with pivot pins that ride the slots. Topology is the same axis + joint count as `simple_hinge`; the distinguishing structural change is the extra rear tower geometry on both mating sides. |
| `hinged_adf` | forked_anchor | `rec_0611_scanner_var_feed_hinged_adf` from picture 003 | L286-L343 (`base_to_lid` REVOLUTE), L346-L390 (`lid_to_adf_cover` sub-lid) | eligible if compatible | 2 REVOLUTE `-X` joints: (1) body→lid raises the whole ADF carrier; (2) lid→adf_cover raises the ADF top cover (0-0.85 rad). Lid carries `adf_base`, `adf_liner`, `feed_roller_{0,1}` etc as its visuals. Same base rear-hinge line as `simple_hinge`. |

### Slot C：`controls`  (② PRISMATIC / REVOLUTE + button multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `control_ring_button` | forked_anchor | `rec_0611_scanner_var_body_form_portable_slim` (also `sheet_fed`) | L178-L212 (control_panel + scan_button PRISMATIC `-Z`, 0.0012 m travel) | eligible if compatible | 1 FIXED `control_panel` part (a `_control_ring_shape` ring on front housing) + 1 PRISMATIC scan button parented to the panel; 1 non-fixed joint. |
| `dual_button_deck` | forked_anchor | `rec_0611_scanner_var_scanner_topology_book_scanner` from picture 002 | L119-L136 (`_control_deck_shape` inline in chassis), L355-L411 (`add_push_button` PRISMATIC power + scan) | eligible if compatible | Deck geometry inlined on the chassis (`parent.visual`); 2 PRISMATIC push buttons parented directly to the chassis; 2 non-fixed joints. |
| `quad_button_row` | forked_anchor | `rec_0611_scanner_var_feed_hinged_adf` from picture 003 | L393-L423 (`base_to_button_{0..3}` PRISMATIC row of 4) | eligible if compatible | 4 PRISMATIC push buttons in a row on the front control surround (inlined on chassis); 4 non-fixed joints. multiplicity N=4 with per-button icon width variation. |
| `tilting_control_panel` | forked_anchor | `rec_0611_scanner_var_control_tilting_panel` | L86-L102 (`_control_panel_shape`) + a REVOLUTE `+X` panel joint carrying the button (spec §8: panel tilts 0-25°) | eligible if compatible | 1 REVOLUTE `+X` for the panel (0-0.44 rad) + 1 PRISMATIC scan button riding the panel; 2 non-fixed joints. Same footprint & mounting as `control_ring_button` on the front deck. |

## 槽位图（slot graph）

pattern: parallel_children

```
                    scanner_body   (root, ALWAYS from Slot A)
                    /     |       \
   [platen inline visuals]  [feet + status_lens inline visuals]
                    |
   Slot B: lid_mechanism   ───REVOLUTE -X (body_to_lid, +optional lid_to_adf_cover)──▶ lid
                    |
   Slot C: controls        ───FIXED or REVOLUTE +X (body_to_control_panel) + PRISMATIC(s)──▶ control_panel + button(s)
```

- **Slot A owns the root part (`scanner_body`)**, its housing mesh + platen + status lens + feet inline visuals, and exports (a) the rear hinge origin `(0, HINGE_Y, HINGE_Z)` for Slot B and (b) the front control mount pose for Slot C.
- Slot B (`lid_mechanism`) parents `lid` to `scanner_body` via `body_to_lid` REVOLUTE about `-X`; the `hinged_adf` candidate additionally emits `lid_to_adf_cover` REVOLUTE about `-X` (sub-lid).
- Slot C (`controls`) parents `control_panel` to `scanner_body` (FIXED for the ring, deck, quad candidates; REVOLUTE +X for the tilting candidate) and 1-4 PRISMATIC push buttons parented to the panel or directly to `scanner_body`.
- All three slots share a single `scanner_body` — the pattern is **parallel_children**, not a linear chain.

## 每槽位 Module Emits / Interfaces

### Slot A / module `flatbed_full` / `flatbed_slim` / `sheet_fed` / `book_edge_flatbed`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_body` (root) | portable_slim L128, book_scanner L220, sheet_fed L142, ADF L216 |
| inline visuals on scanner_body | housing_shell (mesh from `_scanner_housing_shape`) + platen_glass + reference_strip + status_lens + 4 feet + 2-3 fixed rear knuckles + hinge pin (for simple_hinge) | portable_slim L128-L169, book_scanner L224-L316, sheet_fed L142-L167, ADF L216-L283 |
| internal joints | none within the body module (all platen/status/feet are Rule 1 inline visuals) | portable_slim L157-L228 (platen/panel/status use FIXED articulations — allowed but downgraded to inline visuals here since none of them articulate) |
| upstream interface | n/a (root) | — |
| downstream interface | `body_hinge_anchor` = `(0, HINGE_Y, HINGE_Z)` on `housing_shell` for Slot B; `body_control_anchor` = front-center of `housing_shell` for Slot C | portable_slim L266-L269 (`body_to_lid` origin); book_scanner L340-L345 |

### Slot B / module `simple_hinge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` | portable_slim L229 |
| lid visuals | `lid_panel` (mesh from `_lid_panel_shape`) + `lid_inner_pad` + 2 hinge_bridges + 2 lid_knuckles | portable_slim L230-L258 |
| internal joints | `body_to_lid` REVOLUTE axis=(-1,0,0), limits ≈ [-1.13, +0.26] rad | portable_slim L260-L279 |
| upstream interface | consumes `body_hinge_anchor` from Slot A | portable_slim L266-L269 |
| downstream interface | none | — |

### Slot B / module `rising_book_hinge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` | lid_rising L94 |
| lid visuals | `lid_panel` + `lid_inner_pad` + 2 vertical link arm brackets + 2 horizontal link arms + 2 pivot pins + hinge_pin cross_bar | lid_rising L94-L145 |
| body visuals (added on scanner_body) | 2 hinge towers (0.030×0.032×0.024) at (±0.180, HINGE_Y, HINGE_Z) + 2 guide slot cutouts (Box(0.012, 0.038, 0.014)) — inline on `scanner_body` (Rule 1) | lid_rising L66-L91 (`_base_hinge_shape`) |
| internal joints | `body_to_lid` REVOLUTE axis=(-1,0,0), origin raised by `HINGE_RISE ≈ 0.015` above simple hinge | lid_rising L326-L343 (adapts base_to_lid) |
| upstream interface | consumes `body_hinge_anchor` + raises z by 15 mm | lid_rising L27 |
| downstream interface | none | — |

### Slot B / module `hinged_adf`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` + `adf_cover` | ADF L286, L346 |
| lid visuals | ADF-base mesh + `adf_liner` box + `front_edge_trim` + `lid_hinge` mesh + 2 feed_rollers | ADF L286-L323 |
| adf_cover visuals | `adf_cover_shell` mesh + 2 `paper_guide_i` + `cover_latch` | ADF L346-L370 |
| internal joints | `body_to_lid` REVOLUTE `-X` [-0.38, +1.15]; `lid_to_adf_cover` REVOLUTE `-X` [0, 0.85] | ADF L326-L343, L373-L390 |
| upstream interface | consumes `body_hinge_anchor` | ADF L332 |
| downstream interface | none | — |

### Slot C / module `control_ring_button`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `control_panel` (FIXED), `scan_button` (PRISMATIC) | portable_slim L178, L192 |
| control_panel visuals | `control_ring` mesh (rounded prism with rounded opening) | portable_slim L179-L183 |
| scan_button visuals | `button_cap` (Box) | portable_slim L192-L198 |
| internal joints | `body_to_control_panel` FIXED; `panel_to_scan_button` PRISMATIC axis=(0,0,-1) travel 0.0012 m | portable_slim L184-L211 |
| upstream interface | consumes `body_control_anchor` on `scanner_body` front | portable_slim L189 |
| downstream interface | none | — |

### Slot C / module `dual_button_deck`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `power_button`, `scan_button` (deck geometry inlined on body) | book_scanner L398-L411 |
| body visuals added | `control_deck` mesh + 2 status LEDs (`status_amber`, `status_green`) | book_scanner L259-L316 |
| button visuals (per button) | cap Cylinder + flange + stem | book_scanner L360-L381 |
| internal joints | 2× PRISMATIC `-Z` (`power_button_press`, `scan_button_press`) parented to `scanner_body`, travel 0.0012 m | book_scanner L382-L395 |
| upstream interface | consumes `body_control_anchor` | book_scanner L387 |
| downstream interface | none | — |

### Slot C / module `quad_button_row`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `button_0..button_3` (control surround inlined on body) | ADF L393-L423 |
| body visuals added | `control_surround` Box + `status_lens` | ADF L248-L258 |
| button visuals (per button) | `button_cap` Box + `button_icon` Box (icon width varies by index) | ADF L396-L407 |
| internal joints | 4× PRISMATIC `-Z` (`base_to_button_{i}`) travel 0.0012 m | ADF L408-L422 |
| upstream interface | consumes `body_control_anchor`, evenly spaces N buttons along local X | ADF L393 |
| downstream interface | none | — |

### Slot C / module `tilting_control_panel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `control_panel` (REVOLUTE), `scan_button` (PRISMATIC) | control_tilting L86-L102 + template author |
| control_panel visuals | `_control_panel_shape` — panel plate + rim + button hole | control_tilting L86-L102 |
| scan_button visuals | `button_cap` Box on top of panel | reused from `control_ring_button` |
| internal joints | `body_to_control_panel` REVOLUTE `+X` [0, 0.44 rad]; `panel_to_scan_button` PRISMATIC `-Z` travel 0.0012 m | control_tilting L26 + author |
| upstream interface | consumes `body_control_anchor` | — |
| downstream interface | none | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | `flatbed_full` / `flatbed_slim` / `sheet_fed` / `book_edge_flatbed` | — | choice | procedural sampler on seed | module table |
| `lid_mechanism` | enum | `simple_hinge` / `rising_book_hinge` / `hinged_adf` | — | choice | procedural sampler on seed | module table |
| `controls` | enum | `control_ring_button` / `dual_button_deck` / `quad_button_row` / `tilting_control_panel` | — | choice | procedural sampler on seed | module table |
| `palette_style` | enum | `office_beige` / `matte_black` / `silver_black` / `white_consumer` / `industrial_grey` | `white_consumer` | choice | procedural sampler on seed | recurring across sources |
| `body_width_scale` | float | [0.88, 1.12] | 1.0 | independent | uniform sample, clamp | portable_slim L20 / book_scanner L20 |
| `body_depth_scale` | float | [0.88, 1.12] | 1.0 | independent | uniform sample, clamp | portable_slim L21 |
| `body_height_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform sample, clamp; sheet_fed body is inherently taller | portable_slim L22 |
| `platen_well_depth_scale` | float | [0.80, 1.20] | 1.0 | independent | uniform sample, clamp | control_tilting L61 (well depth 0.032) |
| `lid_open_angle_scale` | float | [0.85, 1.10] | 1.0 | independent | uniform sample, clamp; final lid `upper` ∈ [1.0, 1.6] rad | portable_slim L275 |
| `panel_tilt_scale` | float | [0.85, 1.15] | 1.0 | independent | applies to `tilting_control_panel` only; final panel `upper` ∈ [0.32, 0.52] rad | control_tilting L26 |
| `button_travel_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform sample, clamp; final travel ∈ [0.0009, 0.0015] m | portable_slim L207-L211 |
| (—) | constraint | — | — | inequality | `well_depth ≤ body_height − 0.020`; if violated, shrink well depth first, then raise body_height | control_tilting L46-L61 |
| (—) | constraint | — | — | conditional | for `body_form=sheet_fed`, force `lid_mechanism` ∈ `{simple_hinge}` (no ADF on a sheet-fed body — the front slot IS the ADF); force `controls` ∈ `{control_ring_button, dual_button_deck}` (no quad row on a narrow-front sheet-fed) | sheet_fed L104 |
| (—) | constraint | — | — | conditional | for `body_form=book_edge_flatbed`, force `controls` ∈ `{dual_button_deck, quad_button_row}` (book scanner front deck is wide enough); allow all lid mechanisms | book_scanner L119-L136 |

### 7.5 编译预算 / compile budget
Per-seed budget: **≤ 20 s**. All hero housings use CadQuery boolean union/cut (housing shell + platen well + feet), which library measurement puts at 5-15 s. Tessellation: rounded fillets on hero housing use tolerance ≤ 0.0008 m (matches 5★ sources), lid panel & control ring use 0.0006, mm-scale buttons use SDK default. All 4 feet on a body reuse a single cylinder — no per-foot mesh. Total per seed: expect 8-14 s wall-clock at max-workers 10.

## Multiplicity / Copy Logic

- **Multiplicity axis** `button_count` (Slot C-owned) with:
  - `count_param`: `button_count` implicit in the chosen `controls` module (1 for `control_ring_button` / `tilting_control_panel`, 2 for `dual_button_deck`, 4 for `quad_button_row`).
  - `N_range`: {1, 2, 4}. Not sampled independently — encoded in the `controls` enum.
  - Sampling domain: same weight as its enum candidate (`quad_button_row` gets the low weight since 4-button strip is less common).
  - copied object: PRISMATIC push button (Box cap + optional flange/stem). Naming: `scan_button` (single), `scan_button` + `power_button` (dual), `button_0..3` (quad).
  - Placement: evenly spaced along local X on the front control surround.
  - Joint policy: identical PRISMATIC axis `-Z`, travel `[0, 0.0012 m]` (scaled by `button_travel_scale`).
  - source/gating: encoded through the `controls` enum choice (§7); no independent `button_count` seed parameter.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `lid_mechanism` slot: simple_hinge (1 body-lid REVOLUTE) / rising_book_hinge (1 REVOLUTE, extra tower geometry) / hinged_adf (2 REVOLUTE, adds `adf_cover` part). All forked_anchor: portable_slim / lid_rising_book_hinge / feed_hinged_adf. |
| └ multiplicity | 同构件 ×N | 有 | button_count implicit in `controls` (N ∈ {1,2,4}); see §8. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | `controls` slot: FIXED panel + PRISMATIC(-Z) button (ring), inline deck + 2×PRISMATIC(-Z) (dual), inline surround + 4×PRISMATIC(-Z) (quad), REVOLUTE(+X) panel + PRISMATIC(-Z) button (tilting). All forked_anchor: portable_slim / book_scanner / hinged_adf / control_tilting_panel. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色） | 有 | `body_form` slot: flatbed_full = **Volumetric Envelope Form** (wide low box + recessed well), flatbed_slim = **Volumetric Envelope Form** (thin wide slab + shallow well), sheet_fed = **Macro Surface Construction** (tall-narrow box with front/rear slot cutouts, NO top well), book_edge_flatbed = **Planar Boundary Form** (portrait with right-side wall removed + ramp). 4 candidates, all forked_anchor (control_tilting / portable_slim / sheet_fed / book_scanner). Registered as a `slot_choices` axis. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | `reference_strip` (thin bar rear of platen), `scan_light_strip` (badge), `front_seam` (chassis seam), status LEDs (amber+green cylinders), button `button_icon` (per-index Box width). All host-derived: strips sit ON the platen top surface (z = platen_z + 0.0002), LEDs embed into `control_surround` face. Derivation order ③→⑤→④: decoration positions computed from resolved body/platen surface heights. Source: book_scanner L240-L316, ADF L248-L258, ADF L403-L407. `record_only`. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | `body_{width,depth,height}_scale ∈ [0.85, 1.15]`, `platen_well_depth_scale ∈ [0.80, 1.20]`, `lid_open_angle_scale ∈ [0.85, 1.10]`, `panel_tilt_scale ∈ [0.85, 1.15]`, `button_travel_scale ∈ [0.85, 1.15]`. **Motion envelopes**: `body_to_lid` REVOLUTE `-X`, opens UP (+z toward operator=front), lower = -REFERENCE_LID_ANGLE (≈ -1.13 rad = -65°, closed), upper ∈ [+0.26, +1.60] rad (≈15°-90° open). `lid_to_adf_cover` REVOLUTE `-X`, opens UP, [0, 0.85 rad] (0-48°). `body_to_control_panel` REVOLUTE `+X` (only for `tilting_control_panel`), lower=0 flat, upper ∈ [0.32, 0.52 rad]. All PRISMATIC buttons `-Z`, [0, 0.0012] m. **motion_test_plan**: sampled `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`; targeted `ctx.pose(...)` checks: (a) closed lid seats on housing (lower limit), (b) open lid raises above housing top (upper limit), (c) button pressed lowers z by ≥0.0008 m, (d) if hinged_adf, adf_cover open rises above lid top, (e) if tilting panel, panel-tilted button also rises above closed position. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 5 palette_styles: `office_beige`, `matte_black`, `silver_black`, `white_consumer` (default), `industrial_grey`. Material families per palette: `shell` (painted plastic) + `platen_glass` (translucent) + `lid_graphite` (painted plastic) + `metal` (hinge parts). Covers painted-plastic + glass + metal (3 of 5 material classes) ≥ ceil(0.5 × 5) = 3. Sources: recurring across every read variant (portable_slim L102-L126, book_scanner L205-L218, ADF L195-L214). |

## 采样与覆盖审计

总组合数: 4 (body_form) × 3 (lid_mechanism) × 4 (controls) × 5 (palette) = **240** base combos (before compatibility gating). After gating (sheet_fed × ADF excluded, sheet_fed × quad_button excluded, sheet_fed × tilting_panel deferred to a full-body flatbed), reachable topology combos ≈ 180.

理由: 3 topology slots × 4/3/4 candidates comfortably exceeds the ≥3-per-slot threshold; each candidate structurally distinct (different part counts / joint counts / primitive families for the housing meshes). Palette is a ⑥ axis and does not count toward topology but doubles the visual diversity for viewer inspection.

seed_domain_policy: `procedural_first` — every seed goes through `rng = random.Random(seed)`; no curated table.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)`:
1. Draw `body_form`, `lid_mechanism`, `controls` via `rng.choice(...)`; draw `palette_style`.
2. Apply compatibility gating in `resolve_config`: (a) if `body_form=sheet_fed`, force `lid_mechanism=simple_hinge` and `controls ∈ {control_ring_button, dual_button_deck}`; (b) if `body_form=book_edge_flatbed`, force `controls ∈ {dual_button_deck, quad_button_row}`.
3. Independent scales drawn on `[min, max]` and clamped.
4. `platen_well_depth ≤ body_height − 0.020` inequality resolved after scales are drawn (shrink well depth first, raise body_height as last resort).

Topology target: 1000-seed slot choice tuple coverage — expect roughly 150-180 distinct `(body_form, lid_mechanism, controls, palette)` tuples reached; ~40 topology-tuple combos (without palette) — well above the 300 flag for a low-complexity 3-slot template with heavy gating. report-only.

Controlled local parameterization: `body_width_scale`, `body_depth_scale`, `body_height_scale`, `platen_well_depth_scale`, `lid_open_angle_scale`, `panel_tilt_scale`, `button_travel_scale`. All in `[≈0.85, 1.15]`, clamped in `resolve_config`. None break interfaces because the hinge origin and control anchor are derived from resolved body dims.

Random sweep: 0-35 (initial fast + final), corner stage as per sweep-pipeline.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural `rng.choice` per slot + `rng.uniform` scales + compatibility gating in `resolve_config` | `slot_choices_for_seed` matches build choices |
| compatibility matrix | `sheet_fed × hinged_adf` blocked; `sheet_fed × quad_button_row` blocked; `sheet_fed × tilting_control_panel` blocked; `book_edge_flatbed × control_ring_button` blocked (front deck required); everything else allowed | no floating parts, no closed-pose collisions, no reversed hinge |
| controlled local variation | 7 continuous scales clamped in `[0.80, 1.20]` window; well-depth inequality resolved | proportions vary without breaking hinge origin / MatingContract / motion envelopes |
| regression overrides | none | — |
| random sweep | seeds 0-15 fast, 0-35 final, +corner | axis_realization shows all 4 body_forms, all 3 lid_mechanisms, all 4 controls, all 5 palettes |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | ③ Primary Form Family slot |
| lid_mechanism | 3 | yes | yes | ① skeleton + ② joint diversity |
| controls | 4 | yes | yes | ② + multiplicity |

## Validator

- `slot_choices_for_seed(seed)` returns `(body_form, lid_mechanism, controls, palette)` matching build.
- `config_from_seed(0)` succeeds; every seed 0-35 procedural.
- Compatibility gating blocks the 4 illegal combos listed above.
- `body_to_lid` REVOLUTE `-X` present on every build; motion_limits.upper ∈ [1.0, 1.6] rad.
- `hinged_adf` adds `lid_to_adf_cover` REVOLUTE `-X` [0, 0.85] and `adf_cover` part.
- At least one PRISMATIC push button per build; travel ∈ [0.0009, 0.0015] m; axis `(0,0,-1)`.
- `scanner_body` is the only root part.
- `MatingContract` declared on `body_to_lid` and `lid_to_adf_cover` (non-FIXED joints on non-captured pivots — use bridge/panel visual faces).
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` called in `run_tests`.
- Targeted `ctx.pose` checks: closed lid seats near housing top; open lid raises above housing top; button pressed lowers z; adf_cover raises above lid_top when opened; tilting panel raises button above closed pose.

## Reject cases

1. Any seed where the closed lid gaps > 5 mm from the housing top (spec §8.5 ⑤) — indicates hinge Z or lid panel Z drifted.
2. Reversed lid axis (positive lid motion goes DOWN or into the housing) — `hinged_panel` semantics require +q → +z; fail if closed-lid AABB top > open-lid AABB top.
3. `sheet_fed` build with `hinged_adf` chosen (compatibility gate must degrade).
4. Any `scanner_body` z-extent > 0.15 m — exceeds real scanner proportions (not a printer).
5. Isolated parts (a knuckle or ring floating off the housing) — Rule 1 fail.
6. Missing `MatingContract` on any non-FIXED body↔lid joint — Rule 2 fail.
7. Downgrading `_scanner_housing_shape` mesh to a plain Box for any body_form — Rule 3 fail.
8. Palette below 3 styles or below 3 material classes — spec §8.5 ⑥ fail.

## 与相邻类别的边界

- **不该混入 all-in-one printer / MFP** (`rec_all_in_one_printer_with_scanner_lid_and_paper_tray_*`): printers have an output tray, paper cassette, and a large-volume printhead assembly under the scan lid. A scanner has ONLY a scan bed + lid; no cassette, no printhead, no output shelf. Excluded via `must_not_become`.
- **不该混入 photocopier**: copiers add a document exit shelf on the side. Not modelled here.
- **不该混入 barcode scanner / handheld gun scanner** (`rec_barcode_scanner_var_base_cradle`): handheld pistol-grip form + trigger, no platen glass, no lid. Different Slot A candidates would be required — deliberately excluded from `body_form`.
- **不该混入 fax machine**: fax has telephone handset + numeric keypad + printer roll — none present in this template.
- **不该混入 3D scanner / body scanner**: turntable + tripod camera; a completely different form family and joint spine.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored 2026-07-12 by P3+P4 subagent from 8 forked-anchor 5★ variants + 3 origin_anchors |
