# pictureX_0611_hydraulic_jack

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_hydraulic_jack` |
| template path | `agent/templates/pictureX_0611_hydraulic_jack.py` |
| test path (optional) | none |
| stage | `SPEC_ONLY_DRAFT` |
| status | `implemented; sweep-pipeline pass on 2026-07-14` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all source-map accepted rating=5 samples for `pictureX_0611_hydraulic_jack` |
| source_index_policy | all 11 read sources are indexed in §14; adopted candidate sources are cited in slot tables |

Source map read: `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__hydraulic_jack.md`.

Accepted source ids read: `rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14`, `rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae`, `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713`, `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713`, `rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713`, `rec_picturex0611_hydraulic_jack_fork_double_stage_ram_20260713`, `rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713`, `rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714`, `rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714`, `rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714`, `rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714`.

## 核心身份

Hydraulic jack = compact lifting tool with a grounded base/chassis, visible hydraulic barrel or lift cylinder, extending ram or lift platform, pump/release actuation, and a load-contact saddle/toe/cradle. It may be upright (bottle/toe), rolling floor-style, low-profile floor-style, or fitted with a transmission cradle. It must not become a screw-only scissor jack, gantry/crane, or generic lift table without hydraulic jack pump/ram hardware.

## 槽位 + 候选模块表

### Slot A：`jack_family`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bottle_jack` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713` | L91-L365 | eligible | upright base, vertical hydraulic barrel, prismatic ram, pump handle |
| `floor_trolley` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713` | L63-L533 | eligible | wheeled low chassis, lift rails, platform/arm lift, pedal/handle pump |
| `toe_jack` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713` | L54-L490 | eligible | upright ram with low toe foot/load shoe and pump handle |
| `low_profile_floor` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714` | L60-L593 | eligible | long shallow chassis, low lift arm envelope, wheels/casters |

### Slot B：`ram_module`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_stage_ram` | forked_anchor | `rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14`; `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713` | L296-L393; L165-L265 | eligible | one prismatic chrome ram / cylinder rod |
| `double_stage_ram` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_double_stage_ram_20260713` | L296-L450 | eligible | nested first/second stage ram visual family; template samples visible second stage |
| `screw_extension_saddle` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713` | L492-L589 | eligible if compatible | threaded screw extension and saddle pad on top of ram |

### Slot C：`load_interface`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_saddle` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713`; `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713` | L281-L298; L229-L302 | eligible | flat or round load saddle on ram/platform |
| `toe_foot` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713` | L200-L262 | eligible for toe/upright forms | low toe plate and guide lugs |
| `transmission_cradle` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714` | L316-L362 | eligible for trolley/low floor; degraded to saddle on bottle where needed | cradle crossbar, side uprights, tilt pin/support |

### Slot D：`pump_module`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hand_pump` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713`; `rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14` | L307-L350; L408-L427 | eligible | revolute pump handle with grip |
| `foot_pedal` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713`; `rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714` | L398-L442; L399-L419 | eligible for trolley/low floor | pedal-style revolute pump input |
| `air_over_hydraulic` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714` | L449-L584 | eligible | air motor canister, pneumatic stroke rod, air valve block, plus pump actuation |

### Slot E：`safety_module`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | source-backed absence | original/bottle/floor/toe anchors without lock bar | L106-L427; L91-L365; L63-L533; L54-L490 | eligible | no ratchet lock, only hydraulic lift/pump |
| `safety_lock_bar` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714` | L449-L540 | eligible except toe form degrades to none | ratchet lock bar, teeth, pawl hook/pin visual on base |

### Slot F：`wheel_count`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `0` | forked_anchor | bottle/toe anchors | L91-L365; L54-L490 | eligible for upright families | no casters; grounded base plate |
| `2` | forked_anchor | `rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae`; floor source wheel helpers | L33-L64; L534-L637 | eligible for trolley/floor | rear/front pair subset sampled for compact wheeled base |
| `4` | forked_anchor | `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713`; `rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714` | L460-L523; L465-L583 | eligible for trolley/low floor | four caster/wheel positions with revolute wheel spin |

### Visual parameter：`palette_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `shop_red_black` | record_only | red painted bottle/floor steel anchors | L91-L365; L63-L533 | eligible | red paint, black rubber/dark hardware, chrome ram |
| `service_blue_chrome` | record_only | blue source materials from origin/toe/double-stage | L106-L427; L54-L490; L296-L450 | eligible | blue paint, chrome ram, dark grip |
| `zinc_black` | record_only | zinc/chrome hardware and black components across floor sources | L351-L650; L274-L596 | eligible | grey zinc body, black rubber, bright steel |
| `yellow_safety_black` | record_only + 20260714 safety anchor | `rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714` | L449-L540 | eligible | yellow warning/safety paint with black hardware |
| `dark_green_steel` | world_knowledge_extrapolation(⑥ only) | anchors: red/blue/zinc painted steel sources | generated material table | eligible | dark industrial painted steel + chrome |

## 槽位图（slot graph）

pattern: `mixed`

`jack_family` selects the grounded physical frame:

- Upright path: `hydraulic_base` --[PRISMATIC +Z, captured ram]--> `lifting_ram`; `hydraulic_base` --[REVOLUTE about Y]--> `pump_handle`.
- Trolley/low-profile path: `hydraulic_base` with caster wheel children --[PRISMATIC +Z, lift rail support]--> `lift_platform`; `hydraulic_base` --[REVOLUTE about Y]--> `pump_handle`.
- `load_interface` is emitted on `lifting_ram` or `lift_platform`.
- `ram_module`, `pump_module`, `safety_module`, `wheel_count`, and `palette_style` are conditionally attached to the chosen frame. `safety_lock_bar` and `air_over_hydraulic` are host-mounted visual modules in the template to preserve a single stable motion spine while retaining the 20260714 anchor vocabulary.

Cross-slot interfaces:

- Ram/platform is captured by the cylinder gland or lift rails; the joint axis is vertical +Z and travel is clamped by `travel_scale`.
- Pump handle/pedal pivots on the real pump socket/boss, axis +Y, range approximately -34..36 degrees for handles and -10..32 degrees for pedals.
- Wheel spin joints attach to visible axle cylinders on trolley/low-profile bases, axis +Y.
- Transmission cradle and saddle pads sit on the top load-contact face and are not separate moving parts.

## 每槽位 Module Emits / Interfaces

### Slot A / module `bottle_jack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hydraulic_base`, `lifting_ram`, `pump_handle` | bottle source L91-L365 |
| internal joints | `ram_slide` PRISMATIC +Z, `pump_handle_pivot` REVOLUTE +Y | bottle source L232-L265, L350-L365 |
| upstream interface | grounded base plate | bottle source L114-L165 |
| downstream interface | vertical cylinder gland and ram top | bottle source L165-L298 |

### Slot A / module `floor_trolley` / `low_profile_floor`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hydraulic_base`, `lift_platform`, caster parts, `pump_handle` | floor L63-L533; low-profile L60-L593 |
| internal joints | caster revolutes, `hydraulic_lift_slide`, `pump_handle_pivot` | floor L302-L523; low-profile L257-L583 |
| upstream interface | rolling chassis bottom plane | floor L80-L221; low-profile L78-L196 |
| downstream interface | lift rail/platform top contact plane | floor L229-L302; low-profile L237-L257 |

### Slot A / module `toe_jack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hydraulic_base` with toe visuals, `lifting_ram`, `pump_handle` | toe source L54-L490 |
| internal joints | `ram_slide`, `pump_handle_pivot`; toe shoe visual is host-mounted in template | toe source L200-L475 |
| upstream interface | compact base + low toe load plane | toe source L75-L262 |
| downstream interface | vertical ram top or toe shoe contact | toe source L399-L429 |

### Slot B / `ram_module`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lifting_ram` visuals or `lift_platform` support visuals | single/double/screw sources |
| internal joints | ram/platform PRISMATIC joint stays one stable captured slide | S1/S6/S7 |
| upstream interface | gland/rail capture in base | S1/S6/S7 |
| downstream interface | load saddle/cradle face | S7/S9 |

### Slot C / `load_interface`
| emits | 描述 | 来源 |
|---|---|---|
| parts | saddle/cradle/toe visuals on ram/platform/base | S3/S5/S9 |
| internal joints | none; load interface is rigid to the lifting member | source modules use rigid saddle geometry |
| upstream interface | lifting member top face | S3/S9 |
| downstream interface | load contact plane/cup/cradle | S3/S9 |

### Slot D / `pump_module`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_handle`; optional air canister/valve visuals on base | S3/S8/S10 |
| internal joints | `pump_handle_pivot` REVOLUTE for handle/pedal | S3 L350-L365; S8 L442-L552 |
| upstream interface | pump socket/boss on base | S3/S10 |
| downstream interface | grip or pedal contact | S8/S10 |

### Slot E / `safety_module`
| emits | 描述 | 来源 |
|---|---|---|
| parts | ratchet bar, teeth, pawl hook/pin as base visuals | S11 L449-L540 |
| internal joints | none in template; source anchor has lock-bar/pawl revolutes, but template degrades to host-mounted visible lock to keep compatibility | S11 L486-L540 |
| upstream interface | side rail/center web of base | S11 |
| downstream interface | visible ratchet/pawl lock indicator | S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `jack_family` | enum | `bottle_jack`, `floor_trolley`, `toe_jack`, `low_profile_floor` | `floor_trolley` | choice | sampled by seed, then compatibility-resolved | Slot A |
| `ram_module` | enum | `single_stage_ram`, `double_stage_ram`, `screw_extension_saddle` | `single_stage_ram` | choice | `screw_extension_saddle` + `transmission_cradle` on `floor_trolley` degrades to `single_stage_ram` | Slot B |
| `load_interface` | enum | `flat_saddle`, `toe_foot`, `transmission_cradle` | `flat_saddle` | conditional | `toe_foot` only upright/toe; `transmission_cradle` best on trolley/low floor; bottle renders compact saddle/cradle vocabulary safely | Slot C |
| `pump_module` | enum | `hand_pump`, `foot_pedal`, `air_over_hydraulic` | `hand_pump` | conditional | `low_profile_floor` hand-pump degrades to `foot_pedal`; air-over-hydraulic adds base-mounted air hardware and keeps pump pivot | Slot D |
| `safety_module` | enum | `none`, `safety_lock_bar` | `none` | conditional | toe form degrades to `none`; other forms host-mount visible safety lock | Slot E |
| `wheel_count` | int enum | `0`, `2`, `4` | `4` | conditional | upright families force `0`; trolley/low floor force `2` or `4` | Slot F |
| `palette_style` | enum | five palettes listed above | `shop_red_black` | choice | sampled per seed; every visual material is looked up from the palette table | ⑥ sources |
| `width_scale` | float | `[0.86, 1.18]` | `1.0` | independent | sampled first, clamped in `resolve_config` | source size spread |
| `height_scale` | float | `[0.84, 1.20]` | `1.0` | independent | sampled first, clamped in `resolve_config` | source size spread |
| `travel_scale` | float | `[0.78, 1.20]` | `1.0` | independent | sampled first; ram/lift travel = nominal travel * scale | ram/lift source motion |
| frame-wheel feasibility | constraint | derived | - | inequality | if `jack_family in {bottle_jack,toe_jack}` then `wheel_count=0`; else `wheel_count in {2,4}` | source compatibility |
| load-interface feasibility | constraint | derived | - | conditional | illegal high-risk combinations are downgraded in `resolve_config` before build | compatibility matrix |

## 7.5 编译预算 / compile budget

Per-seed compile budget: <=20s. Basis: template uses boxes/cylinders only, no CAD booleans/mesh generation; final sweep measured sub-0.12s per seed on 0-35 and corner seeds. Tessellation stays default SDK cylinder tessellation; no source mesh/lathe downgrade is introduced because the implemented stable template intentionally samples the primitive-compatible subset of the anchors.

## Multiplicity / Copy Logic

- count_param: `wheel_count`.
- N_range: `0`, `2`, `4`.
- sampling domain: `0` is forced for upright bottle/toe forms; `2` and `4` are sampled for trolley/low-profile forms.
- copied object / naming / placement / joint policy: caster parts are named `caster_<x>_<y>` with symmetric placement and a REVOLUTE spin joint around +Y. The template reports `wheel_count` in `slot_choices`.
- ram stages: `ram_module=double_stage_ram` adds a visible second-stage ram but keeps one stable prismatic ram joint; separate stage-count joints from S6 are not sampled to avoid combining nested independent ram travel with all jack families.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | upright ram+pump graph (`bottle_jack`, `toe_jack`) vs wheeled trolley graph with caster spin and platform lift (`floor_trolley`, `low_profile_floor`); source-backed S3/S4/S5/S8 |
| └ multiplicity | 同构件 ×N | 有 | `wheel_count` = 0/2/4; see §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | PRISMATIC ram/lift; REVOLUTE pump handle/pedal; REVOLUTE wheel spin; source-backed S3/S4/S8/S10. Air-over-hydraulic source has pneumatic PRISMATIC stroke but template degrades to host-mounted air hardware plus pump pivot for compatibility. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | `bottle_jack` upright cylinder (Volumetric Envelope Form), `floor_trolley` wheeled floor chassis (Macro Surface Construction), `toe_jack` low toe shoe (Planar Boundary Form), `low_profile_floor` long shallow chassis (Volumetric Envelope Form). All source-backed; no unsourced primary-form candidates. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | collars, release valve, warning/ratchet lock bar, air valve block, cradle uprights, saddle pads; record_only plus host-mounted source-backed details S9/S10/S11. Decorations are host visuals, not floating parts. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | `width_scale [0.86,1.18]`, `height_scale [0.84,1.20]`, `travel_scale [0.78,1.20]`; ram/lift travel scales by PRISMATIC joint upper bound. Motion plan: targeted `ctx.pose(...)` covers ram/lift extension and pump open; sweep harness motion QC runs baseline sampled poses. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | five per-seed palettes: red/black, blue/chrome, zinc/black, yellow safety/black, dark green/steel; material classes painted steel, chrome/zinc steel, rubber/dark grip. |

## 采样与覆盖审计

总组合数（resolved reachable topology）：reported 630 from sweep probe. Raw declared space before compatibility gates is 4 jack families × 3 ram modules × 3 load interfaces × 3 pump modules × 2 safety states × 3 wheel counts × 5 palettes = 3240, but upright/trolley compatibility and forced wheel counts reduce this.

理由：the category has multiple real product families but a shared hydraulic identity. The template samples all declared visual/structural axes procedurally, then resolves illegal combinations before geometry is built.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` samples `jack_family` first, chooses compatible pools for load/pump/wheels, samples `palette_style` per seed, and calls `resolve_config`. `slot_choices_for_seed` reports `jack_family`, `ram_module`, `load_interface`, `pump_module`, `safety_module`, `wheel_count`, and `palette_style`.

Topology target：1000-seed report-only coverage should observe hundreds of tuples; final sweep probe reported reachable topology count 630 using 2000 probe seeds.

Controlled local parameterization：continuous scales are independent and clamped in `resolve_config`; joint ranges derive from `travel_scale`; incompatible wheel/load/pump choices are conditional-degraded before build. No regression overrides.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural RNG with first-choice family and conditional pools | `slot_choices_for_seed` matches resolved config |
| compatibility matrix | upright forces no wheels; toe degrades safety lock to none; low profile hand pump becomes foot pedal; high-risk floor cradle+screw extension degrades ram to single-stage | no unsupported wheels, no floating toe/cradle, no impossible lock geometry |
| controlled local variation | width/height/travel scales only | proportions vary without breaking pump socket, caster placement, ram travel |
| regression overrides | none | no fixed seed table |
| random sweep | canonical thread-capped `sweep-pipeline` 0-35 + corner | pass_rate, axis_realization, failed_corner_seeds |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| `jack_family` | 4 | yes | yes | includes 20260714 `low_profile_floor` |
| `ram_module` | 3 | yes | yes | includes screw saddle and double stage |
| `load_interface` | 3 | yes | yes | includes 20260714 `transmission_cradle` |
| `pump_module` | 3 | yes | yes | includes 20260714 `air_over_hydraulic` |
| `safety_module` | 2 | yes | no | real source pool has lock vs no-lock only; two candidates sufficient |
| `wheel_count` | 3 | yes | yes | multiplicity coverage |
| `palette_style` | 5 | yes | yes | per-seed color/material diversity |

Final mechanical audit (2026-07-14): `verdict=pass`, `pass_rate=1.0`, 48/48 seeds passed including 12 corner seeds. Axis realization covered: `jack_family` 4/4, `load_interface` 3/3, `palette_style` 5/5, `pump_module` 3/3, `ram_module` 3/3, `safety_module` 2/2, `wheel_count` 3/3.

## Validator

- `slot_choices_for_seed` returns implemented module names for all registered axes.
- `config_from_seed` is deterministic procedural sampling, including seed 0.
- `resolve_config` handles family/load/pump/safety/wheel compatibility before build.
- Per-seed `palette_style` drives every declared material through the palette table.
- Every generated seed has at least two non-fixed joints for hydraulic lift/pump or lift/wheel motion.
- Ram/lift and pump targeted `ctx.pose(...)` checks cover open/extended motion.
- Captured overlaps are limited to ram-in-cylinder, lift platform in rails, pump socket, and caster axle capture.
- `failed_corner_seeds` must remain empty or within corner tolerance; latest is empty.

## Reject cases

- Screw-only scissor jack with no hydraulic cylinder or pump.
- Crane/engine hoist/gantry frame replacing the jack footprint.
- Lift table/cart with platform only and no pump/ram hardware.
- Floating safety lock, air canister, saddle, or toe shoe not visually connected to base/ram/platform.
- Trolley base without wheels/casters when `jack_family` is floor/low-profile.
- Upright bottle/toe form with caster wheels.
- Palette-only variation with no structural slot coverage.
- Broad travel values that make the pump, ram, or lift platform collide outside captured/allowed mechanisms.

## 与相邻类别的边界

- 不该混入：scissor jack（screw-only X linkage; no hydraulic pump/ram identity）。
- 不该混入：engine crane / hoist（boom crane structure rather than compact jack）。
- 不该混入：generic lift table（platform lift without jack saddle/pump/cylinder vocabulary）。
- 不该混入：pneumatic cylinder alone（air-over-hydraulic must still read as hydraulic jack hardware）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec updated for 11 rating=5 samples and 20260714 anchors; template implemented and sweep-pipeline passed. |

## 模板实现备注（可选）

- The template intentionally keeps one stable motion spine per family: ram/lift PRISMATIC plus pump REVOLUTE, and caster REVOLUTE where applicable.
- `air_over_hydraulic` and `safety_lock_bar` are visible host-mounted modules rather than extra independent moving parts; this is the documented compatibility degradation from the source anchors to avoid incompatible motion spines across all jack families.
- `transmission_cradle` is sampled on trolley/low-profile forms and safely represented as the load interface where other families would otherwise require a different support graph.
- `palette_style` is sampled per seed and is included in `slot_choices` so the sweep report exposes colorway coverage.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | jack_family/ram/pump | origin hydraulic lift/table | `rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14` | L106-L427 | base frame, platform, cylinder, ram, pump handle source vocabulary |
| S2 | jack_family/wheel_count | origin rolling jack/cart | `rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae` | L90-L650 | rolling base, platform lift, caster/brake/wheel vocabulary |
| S3 | jack_family/ram/load/pump | bottle jack | `rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713` | L91-L365 | upright bottle body, ram, saddle, pump handle |
| S4 | jack_family/wheel_count/pump | floor trolley jack | `rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713` | L63-L533 | trolley chassis, wheel multiplicity, pump pedal, lift platform |
| S5 | jack_family/load | toe jack | `rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713` | L54-L490 | toe foot, upright ram/pump vocabulary |
| S6 | ram_module | double stage ram | `rec_picturex0611_hydraulic_jack_fork_double_stage_ram_20260713` | L296-L450 | second-stage ram visual and nested ram source |
| S7 | ram_module/load | screw extension saddle | `rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713` | L492-L589 | screw extension saddle and load pad |
| S8 | jack_family/wheel_count/pump | low profile floor | `rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714` | L60-L593 | 20260714 long low chassis, lift arms, wheels/casters |
| S9 | load_interface | transmission cradle | `rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714` | L316-L362 | 20260714 cradle crossbar/uprights/tilt pin |
| S10 | pump_module | air-over-hydraulic | `rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714` | L449-L584 | 20260714 air motor canister, pneumatic rod, air valve |
| S11 | safety_module | safety lock bar | `rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714` | L449-L540 | 20260714 ratchet lock bar and safety pawl vocabulary |

## Blocked / Excluded

- long-reach floor jack: source map reports original/retry1/retry2 exit 143 and no committed record directory; excluded from template candidates.
- motorcycle platform variants in downstream record folders are not in this source map's accepted 11 and were not sampled.
