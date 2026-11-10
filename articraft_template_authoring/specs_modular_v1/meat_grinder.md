# meat_grinder — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `meat_grinder` |
| template path | `agent/templates/meat_grinder.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (mount / hopper / drive / output all attach to one grounded grind-chamber body) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | 3 origin anchors (001 / 002 / 003) + 11 forked_anchor variants (mount×2, hopper_form×3, output_attachment×2, drive×2, retaining×1, cutter_topology×1) |
| source_index_policy | only adopted module sources are indexed below (§14) |

Reading notes (all 14 read in full):

- `rec_picturex_0611__meat_grinder__001` — *manual_suction_meat_grinder_001*, ≈0.32 m tall. `cq.Solid.makeCylinder/makeCone` helpers → `mesh_from_cadquery`. Grind chamber is a hollow tube on **+X** raised to world z=0.155 by a cast pedestal spine (three stacked `_frustum_z` cones); vertical feed throat + shallow spun frustum hopper on +Z; suction rubber foot at the base; perforated cutting plate + threaded scallop retaining collar at the −X outlet; canted-disc auger + 4-arm cross knife; bent crank + free-spinning grip; a decorative side `vacuum_lever` (REVOLUTE about +Y). Joints: `housing_to_drive` CONTINUOUS +X, `housing_to_ring` CONTINUOUS +X, `drive_to_grip` CONTINUOUS +X, `housing_to_vacuum_lever` REVOLUTE +Y.
- `rec_picturex_0611__meat_grinder__002` — *manual_meat_grinder_002*, ≈0.45 m tall. SDK primitives for drive+clamp, `mesh_from_cadquery` for chamber/hopper/plate/flight/blade. Chamber on +X raised to world z=0.270 by a cast **C-clamp** frame (opening −X); lofted open funnel hopper; `twistExtrude` 3-turn auger flight; crossed-rect cutting blade; perforated cutting plate (FIXED part); `_x_annulus` retaining ring with 12 box grips. Joints: `plate_mount` FIXED, `retaining_ring_turn` REVOLUTE +X [−0.35, 6.30], `auger_crank_spin` CONTINUOUS +X, `crank_grip_spin` CONTINUOUS +X, `clamp_screw_turn` CONTINUOUS about **+Z** (vertical table screw).
- `rec_picturex_0611__meat_grinder__003` — *manual_meat_grinder_003*, chamber at world **z=0** (cleanest datum). `_x_tube/_z_tube/_box` helpers. Hollow tube housing + vertical throat + lofted hopper on +Z; cast pedestal + drilled bolt foot + U-clamp frame descending to z=−0.273 with a vertical threaded screw; perforated plate; `twistExtrude` 720° auger; crossed cutter; 4-lug retaining ring; **crank_arm authored as `mesh_from_geometry(tube_from_spline_points(...))`** (swept spline — Rule-3 critical); yellow grip + orange clamp handle. Joints: `body_to_auger` CONTINUOUS +X, `body_to_ring` REVOLUTE +X [−0.65, 0.65], `auger_to_grip` CONTINUOUS +X, `body_to_clamp_screw` **PRISMATIC** +Z [0, 0.045]. **Richest / most modular lineage → chosen as the unified chassis base.**
- `..._mount_bolt_down_countertop_base` (003): swaps the pedestal for a broad bolted foot (base plate + 2 side gussets + 4 counter-bored through-holes); **drops the clamp_screw part + joint** (permanently bolted → 4 parts / 3 non-FIXED joints).
- `..._mount_freestanding_pedestal` (001): swaps the suction foot for a cast plinth (`sole` disc + two frustum shoulders); keeps the full 001 joint set.
- `..._hopper_form_wide_tray_hopper` (002): shallow **elliptical** loading pan (ellipse loft 0.088×0.063 → 0.098×0.071) + elliptical rolled rim. *Planar Boundary Form* (wide elliptical opening).
- `..._hopper_form_covered_deep_funnel` (001): **deep** round frustum funnel (h≈0.132) + rolled rim + fixed rear **hood** covering >½ the mouth. *Volumetric Envelope Form* (deep tall funnel).
- `..._hopper_form_guarded_feed_chute` (002): tall **rectangular** chute (rect loft) + rectangular rim + integral **finger-guard grid** (3 transverse rails + spine). *Macro Surface Construction* (guarded rectangular tube).
- `..._output_attachment_sausage_stuffing_noz` (003): adds a lofted **tapered horn** (open both ends) + capture flange as a body outlet visual; keeps full 003 part set.
- `..._output_attachment_kibbe_former` (003): adds a **hollow annular cone** + rear flange + center **mandrel** on 3 cast spokes as a body outlet visual.
- `..._drive_spoked_handwheel` (002): replaces the bent crank with a cast **6-spoke handwheel** (hub + `_x_annulus` rim + 6 rod spokes) + offset spinner axle; grip spins on the spinner axle. Joints unchanged (CONTINUOUS +X).
- `..._drive_geared_crank` (002): adds a cast **18-tooth spur gear** (root r≈0.043, 5 lightening holes) rigid on the shaft, retaining the bent crank arm. Joints unchanged.
- `..._retaining_bayonet_retaining_ring` (001): retaining collar → 3 broad **bayonet ears** + 3 internal locking bosses (quarter-turn). **Ring joint CONTINUOUS→REVOLUTE** [0.0, 0.42] (short bayonet turn).
- `..._cutter_topology_dual_blade_cutter` (003): cutter → real **two-wing swept paddle** knife (polyline profile, mirrored) + hub + square drive socket. Internal to the chamber; folded into the always-present grind assembly (see §8 / Blocked).

**Unification decision.** All three lineages share one canonical spine, so the template builds **one** grounded grind-chamber `body` (datum = chamber axis at world **z=0**, per 003) and expresses diversity through 4 clean parallel-child slots, rather than shipping three chassis codebases. Per-lineage world-Z offsets (A 0.155 / B 0.270 / C 0.0) collapse to a single z=0 chamber with the mount hung below on −Z.

## 核心身份

A **manual (hand-cranked) meat grinder**: a grounded horizontal grind-chamber body (a hollow cylindrical housing whose bore runs along **+X**) that carries a vertical feed hopper/throat on +Z, an internal helical **auger** that is hand-cranked about the chamber axis, a perforated **cutting plate** and a **retaining ring** at the −X outlet, and a **mount** (table clamp, bolt-down countertop foot, or freestanding pedestal) that grounds it below on −Z. A free-spinning grip rides the crank pin so the operator can turn the auger continuously; the auger + cutter + crank turn as one rigid CONTINUOUS drive about +X.

Category identity:
- one grounded `body` holding the *fixed* grind chamber, feed throat, hopper geometry, and perforated cutting plate;
- one moving `auger_drive` (CONTINUOUS, multi-turn, about +X) carrying the auger flight, the cutter, and the crank/handwheel/gear drive geometry;
- one free-spinning `crank_grip` (CONTINUOUS +X) at the crank pin;
- one `retaining_ring` (CONTINUOUS +X threaded, or REVOLUTE +X quarter-turn bayonet) at the −X outlet, optionally capturing a sausage nozzle / kibbe former;
- optional `clamp_screw` (PRISMATIC +Z) when the mount is a table clamp.

Hand-driven, unlike an `electric_food_processor` (motor, no crank). Always has a grind chamber + auger + cutting plate, unlike a bare `sausage_stuffer`. Larger and clamp/bolt-mounted, distinct from a `pepper_mill` or `manual_coffee_grinder` (no grounds bin, no burr-gap collar; the meat grinder's defining feature is the perforated plate + retaining ring outlet).

## 槽位 + 候选模块表

Four parallel-child slots (mount / hopper_form / drive / output) attach to the one grounded `body`. The grind chamber, cutting plate, auger, cutter and grip form the always-present spine.

### Slot A: `mount` — grounded support form (② joint variety + ① part variety)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `table_clamp` | forked_anchor | `rec_picturex_0611__meat_grinder__003` (`picture/0611/meat_grinder/003.png`) + `rec_picturex_0611__meat_grinder__002` (C-clamp) | 003 `_build_clamp_frame` + `_build_screw_stem`/`_build_clamp_pad`; 002 `_make_clamp_frame` | eligible if compatible | Cast U/C-clamp frame of Boxes descending on −Z below the chamber + a vertical **`clamp_screw` PART** (threaded stem + pressure pad + cross handle) that travels **PRISMATIC +Z** to grip a table edge. Adds 1 moving part + 1 joint (① + ② vs the fixed mounts). |
| `countertop_base` | forked_anchor | `rec_0611_meat_grinder_var_mount_bolt_down_countertop_base` from `rec_picturex_0611__meat_grinder__003` | var `_build_mount_cast` (bolted foot) | eligible if compatible | Broad bolt-down foot: short pedestal + rectangular base plate (≈0.18×0.13) + 2 triangular side gussets + 4 counter-bored through-holes. Visual-only on `body`, no joint. |
| `freestanding_pedestal` | forked_anchor | `rec_0611_meat_grinder_var_mount_freestanding_pedestal` from `rec_picturex_0611__meat_grinder__001` | var `_pedestal_base` (cast plinth) | eligible if compatible | Cast plinth column: circular `sole` disc + two stacked frustum shoulders tapering up to the chamber. Visual-only on `body`, no joint. |

### Slot B: `hopper_form` — feed hopper / throat form (③ Primary Form Family, registered)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `wide_tray_hopper` | forked_anchor | `rec_0611_meat_grinder_var_hopper_form_wide_tray_hopper` from `rec_picturex_0611__meat_grinder__002` | var `_make_hopper` (elliptical pan) | eligible if compatible | Shallow **elliptical** loading pan (ellipse loft, wide mouth ≈0.098×0.071) + elliptical rolled rim on the throat top. `form_subtype = Planar Boundary Form` (wide elliptical opening). |
| `covered_deep_funnel` | forked_anchor | `rec_0611_meat_grinder_var_hopper_form_covered_deep_funnel` from `rec_picturex_0611__meat_grinder__001` | var `_hopper_tray` (deep funnel + hood) | eligible if compatible | **Deep** round frustum funnel (tall, h≈0.13) + rolled rim + a fixed rear **hood** visual covering >½ the mouth. `form_subtype = Volumetric Envelope Form` (deep tall funnel envelope). |
| `guarded_feed_chute` | forked_anchor | `rec_0611_meat_grinder_var_hopper_form_guarded_feed_chute` from `rec_picturex_0611__meat_grinder__002` | var `_make_hopper` (rectangular chute + guard grid) | eligible if compatible | Tall **rectangular** feed chute (rect loft) + rectangular rim + an integral **finger-guard grid** (3 transverse rails + 1 spine) across the mouth. `form_subtype = Macro Surface Construction` (guarded rectangular tube). |

All hoppers are non-articulating (Rule 1) → emitted as fused `body` visuals on the +Z throat top; hood/guard are fixed host-conformal decorations derived from the hopper's final rim.

### Slot C: `drive` — hand drive geometry on the auger (②/① surface + skeleton on `auger_drive`)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bent_hand_crank` | forked_anchor | `rec_picturex_0611__meat_grinder__003` + `__001` | 003 `crank_arm` via `mesh_from_geometry(tube_from_spline_points(...))` + `_build_grip`; 001 `_crank_drive` | eligible if compatible | Swept **bent crank arm** (Rule-3: spline tube mesh, not a cylinder) rigid to the +X shaft end, terminating in a crank pin; the `crank_grip` rides the pin (CONTINUOUS +X). Default. |
| `spoked_handwheel` | forked_anchor | `rec_0611_meat_grinder_var_drive_spoked_handwheel` from `rec_picturex_0611__meat_grinder__002` | var spoked_handwheel (hub + `_x_annulus` rim + 6 rod spokes + spinner axle) | eligible if compatible | Cast **6-spoke handwheel** (hub + rim ring + 6 radial rod spokes) rigid on the +X shaft, with an offset **spinner axle** at the rim; the grip rides that axle. `Macro Surface Construction` of the drive wheel. |
| `geared_crank` | forked_anchor | `rec_0611_meat_grinder_var_drive_geared_crank` from `rec_picturex_0611__meat_grinder__002` | var `_make_geared_crank_wheel` (18-tooth spur gear) | eligible if compatible | Cast **18-tooth spur gear** (root r≈0.043, reinforced hub, lightening holes) rigid on the +X shaft, plus the bent crank arm + grip. Adds the gear disc to the `auger_drive` part tree. |

### Slot D: `output` — −X outlet: retaining ring + optional attachment (②/① at the outlet interface)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_ring` | forked_anchor | `rec_picturex_0611__meat_grinder__003` + `__002` | 003 `_build_retaining_ring` (4 lugs); 002 `retaining_ring` (12 grips) | eligible if compatible | Threaded scallop/lug retaining collar wrapping the front flange, holding the cutting plate. `body_to_ring` **CONTINUOUS +X** (screws freely). No attachment. |
| `bayonet_ring` | forked_anchor | `rec_0611_meat_grinder_var_retaining_bayonet_retaining_ring` from `rec_picturex_0611__meat_grinder__001` | var `_retaining_ring` (3 ears + 3 locking bosses) | eligible if compatible | Bayonet collar: 3 broad ears + 3 internal locking bosses; quarter-turn. `body_to_ring` **REVOLUTE +X** [0.0, 0.42]. No attachment. (② joint-type/range change vs threaded.) |
| `sausage_nozzle` | forked_anchor | `rec_0611_meat_grinder_var_output_attachment_sausage_stuffing_noz` from `rec_picturex_0611__meat_grinder__003` | var `_build_sausage_nozzle` (lofted horn) | eligible if compatible | Threaded ring (CONTINUOUS +X) **+ a lofted tapered horn nozzle** (open both ends) captured at the outlet as a `body` visual. |
| `kibbe_former` | forked_anchor | `rec_0611_meat_grinder_var_output_attachment_kibbe_former` from `rec_picturex_0611__meat_grinder__003` | var `_build_kibbe_former` (annular cone + mandrel + 3 spokes) | eligible if compatible | Threaded ring (CONTINUOUS +X) **+ a hollow annular cone with a center mandrel on 3 cast spokes** at the outlet as a `body` visual. |

硬约束满足：4 个 slot，candidate 数 3/3/3/4，均 ≥2（三个 ≥3）；每个 candidate 有 `forked_anchor` 来源 + `model.py` 位置；candidate 之间为真实结构差异（part/joint 增减或 ③ 形态原型切换），非只换尺寸/涂装。③ 形态主导 slot = `hopper_form`，登记进 `slot_choices`，3 个 candidate 分别标注 `form_subtype`。

## 槽位图（slot graph）

pattern: `parallel_children`（mount / hopper / output visuals fuse to `body`; auger + ring + clamp_screw are children of `body`; grip is a child of `auger_drive`）

```
body (grounded root: grind_chamber + feed_throat + cutting_plate; hopper_form + mount + output visuals fused on)
 ├──[CONTINUOUS +X at (0.115,0,0)]────────────────> auger_drive (auger_flight + cutter + drive[C] geometry)
 │                                                     │
 │        [CONTINUOUS +X at crank pin (drive-dep.)]────┴──> crank_grip
 │
 ├──[CONTINUOUS +X (threaded) OR REVOLUTE +X [0,0.42] (bayonet) at (-0.100,0,0)]──> retaining_ring
 │
 └──[PRISMATIC +Z [0,0.045] at (0.035,0,-0.24), only if mount = table_clamp]──> clamp_screw
```

跨 slot 接口点位：
- `body → auger_drive`: axis (1,0,0); origin on the rear bearing bore centerline (0.115, 0, 0); CONTINUOUS multi-turn. Captured journal (auger flight inside the chamber bore) → `mating` omitted (grandfathered), guarded by element-scoped `allow_overlap`.
- `auger_drive → crank_grip`: axis (1,0,0); origin at the crank pin (bent crank: (0.065, 0.045, −0.100); handwheel: on the spinner axle; gear: same as bent crank); CONTINUOUS. Captured pin → `mating` omitted, `allow_overlap`.
- `body → retaining_ring`: axis (1,0,0); origin on the front flange centerline (−0.100, 0, 0); CONTINUOUS (threaded) or REVOLUTE [0,0.42] (bayonet). Ring wraps the flange (captured collar) → `mating` omitted, `allow_overlap`.
- `body → clamp_screw`: axis (0,0,1); origin on the clamp boss bore (0.035, 0, −0.24); PRISMATIC [0, 0.045]. Threaded stem in the boss bore → `mating` omitted, `allow_overlap`.

互斥/派生：`clamp_screw` part+joint exists **iff** `mount == table_clamp`. `output ∈ {sausage_nozzle, kibbe_former}` adds one outlet `body` visual; `bayonet_ring` alone changes the ring joint type/range. The three non-FIXED spine joints (auger, grip, ring) are always present; the clamp screw is the only conditional joint.

## 每槽位 Module Emits / Interfaces

### Chassis (always) / part `body`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (root, grounded) | S3 / 003 |
| visuals | `grind_chamber` (cadquery hollow tube +X + front_collar + rear_bearing + vertical throat, bores cut — single fused mesh), `cutting_plate` (perforated disc at −X, cadquery mesh) | S3 `_build_housing_cast` + `_build_cutting_plate` |
| internal joints | none | — |
| downstream interfaces | rear bearing bore (0.115,0,0)+X for auger; front flange (−0.100,0,0)+X for ring; throat top +Z for hopper; −Z for mount; −X outlet for output attachment; clamp boss −Z for clamp_screw | S3 |

### Chassis (always) / part `auger_drive`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `auger_drive` | S3 / 003 |
| visuals | `auger_flight` (`twistExtrude` mesh — Rule 3), `cutter_blade` (crossed-rect or two-wing swept mesh), `drive` geometry per Slot C, `grip_pin` (small +X cyl) | S3 `_build_auger_core`/`_build_cutter_blade` + Slot C |
| internal joints | none (drive geometry is rigid to the auger) | — |
| upstream interface | joint origin (0.115,0,0), axis +X, CONTINUOUS multi-turn | S3 |
| downstream interface | `grip_pin` face at the crank pin, axis +X, CONTINUOUS | S3 |

### Chassis (always) / part `crank_grip`
| emits | `crank_grip` part: `grip_sleeve` (`_x_tube` shell) + sphere/`_x_tube` end cap | S3 `_build_grip` |
| upstream interface | on the crank pin, axis +X, CONTINUOUS | S3 |

### Chassis (always) / part `retaining_ring`
| emits | `retaining_ring` part per Slot D (threaded scallop/lug collar or bayonet 3-ear collar) | S3/S2/S1 |
| upstream interface | origin (−0.100,0,0), axis +X, CONTINUOUS (threaded) or REVOLUTE [0,0.42] (bayonet) | S3/S1 |

### Slot A / module `table_clamp`
| emits | `body` visuals: `clamp_frame` (Box U-frame on −Z) + `clamp_boss` (`_z_tube`). **`clamp_screw` PART**: `screw_stem` (+Z Cylinder) + `clamp_pad` + `clamp_handle` (Box cross). Joint `body_to_clamp_screw` PRISMATIC +Z [0,0.045]. | S3 `_build_clamp_frame`/`_build_screw_stem`/`_build_clamp_pad`; S2 `_make_clamp_frame` |
### Slot A / module `countertop_base`
| emits | `body` visuals: `mount_pedestal` + `base_plate` (Box) + `gusset_[0,1]` (Box) + `bolt_hole_[0..3]` decorations. No part, no joint. | S3v `_build_mount_cast` |
### Slot A / module `freestanding_pedestal`
| emits | `body` visuals: `pedestal_sole` (disc) + `pedestal_shoulder`/`pedestal_boss` (frusta). No part, no joint. | S1v `_pedestal_base` |

### Slot B / module `wide_tray_hopper` / `covered_deep_funnel` / `guarded_feed_chute`
| emits | `body` visuals on the throat top: `hopper_shell` (loft mesh — elliptical pan / deep funnel / rectangular chute) + `hopper_rim` (annulus) + (deep: `hopper_hood`; guarded: `guard_rail_[0..2]` + `guard_spine`). No part, no joint. | S2v/S1v/S2v |

### Slot C / module `bent_hand_crank` / `spoked_handwheel` / `geared_crank`
| emits | `auger_drive` visuals: bent → `crank_arm` (spline tube mesh) + `grip_pin`; handwheel → `handwheel_hub` + `handwheel_rim` (annulus) + `spoke_[0..5]` + `spinner_axle` (grip_pin equivalent); geared → `gear_disc` (18-tooth spur mesh) + `crank_arm` + `grip_pin`. | S3/S2v |

### Slot D / module `plain_ring` / `bayonet_ring` / `sausage_nozzle` / `kibbe_former`
| emits | `retaining_ring` part geometry (threaded collar vs bayonet 3-ear); `sausage_nozzle`/`kibbe_former` additionally emit one fused `body` outlet visual (`sausage_nozzle` horn loft / `kibbe_former` annular cone + mandrel + 3 spokes). | S3/S1v |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount` | enum | `table_clamp` / `countertop_base` / `freestanding_pedestal` | — | choice | deterministic procedural sampler | Slot A |
| `hopper_form` | enum | `wide_tray_hopper` / `covered_deep_funnel` / `guarded_feed_chute` | — | choice | — | Slot B |
| `drive` | enum | `bent_hand_crank` / `spoked_handwheel` / `geared_crank` | — | choice | — | Slot C |
| `output` | enum | `plain_ring` / `bayonet_ring` / `sausage_nozzle` / `kibbe_former` | — | choice | — | Slot D |
| `palette_style` | enum | `stainless_rubber` / `cast_aluminum_offwhite` / `stainless_yellow` / `tinned_high_contrast` / `red_enamel` / `bronze_and_brass` | first | choice | 6 realistic colorways from the 5-star pool | palette table |
| `body_scale` | float | [0.90, 1.10] | 1.0 | independent | uniform, clamp; applied as `unit_scale` on all meshes + multiplier on primitives (chamber radius co-varies with it, so the auger/plate/ring stay concentric) | 全域 |
| `hopper_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; multiplies hopper mouth width + height only | hopper h/r |
| `crank_reach_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; multiplies the crank-pin radial offset / handwheel spinner offset only | 003 crank spline / 002 handwheel r |
| `chamber_radius_scale` | float | derived (= body_scale) | 1.0 | equation | `= body_scale` — the chamber, auger, plate and ring must co-vary to stay concentric, so radius is not sampled independently (folded into the global `body_scale` unit_scale) | 001/002/003 chamber r |
| (—) | constraint | — | — | inequality | grip swept-clear: crank pin radius `crank_reach × pin_r_nominal ≥ chamber_r × chamber_radius_scale + grip_r + 0.006`; else raise `crank_reach` to the minimum. Resolved in `resolve_config`. | Rule 5 |
| (—) | constraint | — | — | conditional | `spoked_handwheel` caps `crank_reach_scale ≤ 1.05` (spinner axle must stay inside the rim); resolved after `drive` is picked. | Slot C |
| (—) | constraint | — | — | conditional | `clamp_screw` params (stroke [0,0.045], boss z) exist **iff** `mount == table_clamp`. | Slot A |

连续尺寸采样契约（写进 `config_from_seed` / `resolve_config`）：
1. 独立采样 `body_scale`, `chamber_radius_scale`, `hopper_scale`, `crank_reach_scale`（均匀）。
2. 无 equation 派生（各 scale 语义独立；`chamber_radius_scale` 只缩放半径不缩放长度以保持 auger 贴合）。
3. inequality 投影：`crank_reach_scale = max(sampled, min_for_grip_clearance)`。
4. conditional：`spoked_handwheel` 上限、`clamp_screw` 存在性在采样/解析时按上游 choice 解析。

## 7.5 编译预算 / compile budget

Target: **≤18 s per seed**. Heaviest ops: one fused chamber mesh (tube + collar + bearing + throat + bores cut), one perforated cutting plate (concentric hole-ring boolean cuts — hole rings kept modest: 6 + 12), one `twistExtrude` auger flight, one hopper loft, and (output-dependent) one horn/kibbe loft. Everything else is SDK `Cylinder`/`Box`/`Sphere` (crank arm spline is one `tube_from_spline_points`; spokes/teeth/gussets are primitives). Cadquery meshes are cached per (form,scale) via `AssetContext`; the N identical spokes/teeth/bolt-holes reuse one shared `Mesh`/primitive. Tessellation: `tolerance=0.0008–0.0011`, `angular_tolerance=0.08–0.10`; small-radius pins/bolts/teeth ≤32 segments, hero chamber/hopper ≤64. Under the sweep-pipeline hang-guard `--compile-timeout 120` (~6–7× budget). If a seed exceeds budget: cut plate hole count and gear tooth count first.

## 8. Multiplicity / Copy Logic

- 无模板级复制数量轴：核心结构由固定 named slots/parts 表达（body / auger_drive / crank_grip / retaining_ring / optional clamp_screw）。The N-repeated sub-elements that DO appear — 6 handwheel spokes, 18 gear teeth, 4 bolt holes, 3 kibbe spokes, 2–3 guard rails, plate perforation rings — are **fixed per-module decoration counts** (part of a candidate's identity, not a swept axis), so no `*_count` is exposed and no template-level part/joint is loop-replicated across seeds. The `cutter_topology` source axis (4-arm cross vs two-wing dual blade) is folded into the always-present cutter geometry (a fixed internal detail behind the plate, low visibility) rather than a swept slot — recorded here per the "must write, even if none" discipline.

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Baseline part tree = body + auger_drive + crank_grip + retaining_ring (4 parts, 3 non-FIXED joints). ①-changing module: `mount = table_clamp` adds a **`clamp_screw` PART + PRISMATIC +Z joint** (→ 5 parts / 4 joints) vs `countertop_base` / `freestanding_pedestal` (no extra part). Source-backed: 003 & 002 clamp screws vs `..._mount_bolt_down_countertop_base`. (Both structural skeletons appear in every sweep.) forked_anchor. |
| └ multiplicity | 同构件 ×N | 无 | 见 §8 — spokes/teeth/bolts are fixed per-module decoration counts, not a swept N axis. |
| ② 关节类型 | 图不变,某条边换 type/轴 | 有 | Joint-type/axis set realized across the sweep: CONTINUOUS +X (auger, grip, threaded ring), REVOLUTE +X [0,0.42] (`bayonet_ring`), PRISMATIC +Z [0,0.045] (`table_clamp` clamp_screw). `output = bayonet_ring` flips the ring edge CONTINUOUS→REVOLUTE; `mount = table_clamp` adds the PRISMATIC edge. All source-backed (001 bayonet REVOLUTE, 003 clamp PRISMATIC, 002 clamp CONTINUOUS). Every declared type appears in the sweep. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | 有 | Slot B `hopper_form` registered into `slot_choices` with 3 source-backed candidates: `wide_tray_hopper` = **Planar Boundary Form** (wide elliptical opening), `covered_deep_funnel` = **Volumetric Envelope Form** (deep tall funnel + hood), `guarded_feed_chute` = **Macro Surface Construction** (rectangular guarded tube). All `forked_anchor`. (≥3 recognizable prototypes, not scale/paint.) |
| ④ 表面装饰 | 原型不变,叠加表面细节 | 有 | (record_only + world_knowledge_extrapolation, host-conformal): perforated plate hole rings (derived on the plate face), retaining-ring scallops/lugs/grips, handwheel spokes, gear teeth + lightening holes, bolt-hole counterbores on the countertop foot, finger-guard grid on the chute, rolled hopper rims, hood ribs. All emitted as host-part visuals derived from the final host surface (derive order ③→⑤→④). No decoration is a separate part/joint. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | Key scales: `body_scale ∈ [0.90,1.10]`, `chamber_radius_scale ∈ [0.92,1.10]`, `hopper_scale ∈ [0.90,1.15]`, `crank_reach_scale ∈ [0.85,1.15]`. Motion envelopes (each non-continuous joint): `retaining_ring` bayonet REVOLUTE +X, opening +, [0.0, 0.42]; `clamp_screw` PRISMATIC +Z, tightening +, [0.0, 0.045]. Continuous joints (auger, grip, threaded ring) turn full-circle. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` over all joints + targeted `ctx.pose(...)` at auger=π (grip carried around the axis), bayonet ring=0.42 (turns), clamp_screw=0.045 (rises). continuous joints use `qc_sample_values {0, ±π/2, π}`. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 palettes: `stainless_rubber`, `cast_aluminum_offwhite`, `stainless_yellow`, `tinned_high_contrast`, `red_enamel`, `bronze_and_brass`. Material大类 covered: metal (stainless/aluminum/tinned), painted (red_enamel), bronze/brass + rubber/plastic accents ⇒ ≥ ceil(0.5×6)=3. Each palette assigns body_metal / steel_light / dark_steel(blade,plate) / accent(grip) / accent2. |

**收尾自检**：batch 0-9 应肉眼可见——3 种 hopper 形态拉得开（wide 扁 / deep 高 / chute 方带栅）、mount 三态（clamp 有竖螺杆 / bolt 有脚板 / pedestal 有柱）、drive 三态（弯柄 / 六辐轮 / 齿轮）、output 四态（plain / bayonet / 香肠嘴 / kibbe 锥）、材质大类都出现、关节开合全程不穿模。

## 9. 采样与覆盖审计

总组合数（结构+装配）：`mount (3) × hopper_form (3) × drive (3) × output (4)` = **108** legal structural tuples（palette ×6、连续 scale 不计入 tuple 数）。All 108 are legal — no cross-slot gating is required (mount/hopper/drive/output are geometrically independent parallel children on one chassis).

理由：4 独立 parallel-child 轴，无互斥组合；`clamp_screw` 的存在性完全由 `mount` 决定（派生，不是额外轴）。

seed_domain_policy：`procedural_first`

**Procedural Sampling / Sweep Plan**：`config_from_seed(seed)` 用 `random.Random(seed)`，独立采样 `mount`、`hopper_form`、`drive`、`output`、`palette_style`，再采 4 个连续 scale；`resolve_config` clamp 所有 scale 并解析 inequality（grip clearance）/ conditional（handwheel reach cap、clamp_screw 存在）。`seed=0` 不特殊。`slot_choices_for_seed` 与 `build_*` 选择逐位一致。

Topology target：108 legal tuples；1000-seed report 应覆盖全部 mount/hopper/drive/output 值与 6 palettes。真实组合空间 108 < 300，因为这是一个 mechanism-dominated 单脊类别（源锚点 3 origin + 11 fork，slot 结构差异有限）；report-only，不作为 gate，不反推上游变体数量。

若使用 regression overrides：none at P0（如迭代中出现特定坏 seed 再稀疏登记，并注明原因）。

Controlled local parameterization：`body_scale`（整体）、`chamber_radius_scale`（腔半径，不动长度以保 auger 贴合）、`hopper_scale`（hopper 高/口径）、`crank_reach_scale`（曲柄销半径 / 手轮辐半径）。全部在 `resolve_config` clamp/投影；`crank_reach_scale` 有 grip-clearance inequality 下界与 handwheel conditional 上界；不破坏 InterfaceSpec / 关节原点 / 类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mount → hopper_form → drive → output → palette → 4 continuous scales | `slot_choices_for_seed` == build choices |
| compatibility matrix | all 108 tuples legal; no gating; `clamp_screw` derived from mount | no floating parts, no auger/grip-vs-chamber collision through 360°, no ring/clamp collision at extremes |
| controlled local variation | body_scale / chamber_radius_scale / hopper_scale / crank_reach_scale, clamped | proportions vary; grip stays clear of chamber; ring/clamp stay captured |
| regression overrides | none | — |
| random sweep | seeds 0-15 (fast) → 16-35 (final) → corner | corner covers scale extremes + rare tuple like `freestanding_pedestal + guarded_feed_chute + spoked_handwheel + kibbe_former` |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A `mount` | 3 | yes | yes | table_clamp / countertop_base / freestanding_pedestal (all forked_anchor) |
| B `hopper_form` | 3 | yes | yes | ③ Primary Form Family slot; 3 form_subtypes |
| C `drive` | 3 | yes | yes | bent_hand_crank / spoked_handwheel / geared_crank |
| D `output` | 4 | yes | yes | plain_ring / bayonet_ring / sausage_nozzle / kibbe_former |

## 10. Validator

- `slot_choices_for_seed` returns implemented module names for all 4 slot axes (mount / hopper_form / drive / output).
- `config_from_seed(0)` deterministically returns a legal, buildable config (registry contract); procedural sampling for all ordinary seeds.
- `resolve_config` clamps every continuous scale and resolves the grip-clearance inequality + handwheel/clamp conditionals before the builder runs.
- compatibility: all 108 tuples legal; no illegal combination reachable; `clamp_screw` part/joint present iff `mount == table_clamp`.
- `slot_choices_for_seed(seed)` matches actual build choices bit-for-bit.
- Critical interfaces exist: auger CONTINUOUS +X at rear bearing, ring CONTINUOUS/REVOLUTE +X at front flange, grip CONTINUOUS +X at crank pin, clamp_screw PRISMATIC +Z (when present).
- key joints have expected type/axis/range; captured pins/journals (auger-in-bore, ring-on-flange, grip-on-pin, screw-in-boss) guarded by element-scoped `ctx.allow_overlap` in `run_meat_grinder_tests` (mating omitted, grandfathered).
- `run_meat_grinder_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` **plus** targeted `ctx.pose(...)` proving intended motion (auger turns grip around the axis; bayonet ring turns; clamp screw rises).
- Rule-3 primitives preserved: auger `twistExtrude`, crank spline `tube_from_spline_points`, hopper/horn/kibbe lofts, perforated-plate boolean cuts — no downgrade to Box/Cylinder.
- controlled local scale params are clamped and cannot break interfaces, clearance, joint origin, or identity; no small curated/modulo table is the main seed domain.

## Reject cases

- Electric motor drive / no hand crank + free grip → belongs to `electric_food_processor`; rejected.
- No grind chamber / no perforated cutting plate + retaining ring (bare tube stuffer) → belongs to `sausage_stuffer`; rejected.
- Burr-gap adjustment collar + grounds bin, countertop scale → belongs to `manual_coffee_grinder`; rejected.
- Auger flight downgraded to a plain cylinder, or crank arm to a straight box (loses the swept identity) → Rule 3 violation; rejected.
- Grip that sweep-collides with the chamber/hopper at half-turn → grip-clearance inequality + sampled-pose collision; rejected.
- Retaining ring or sausage/kibbe attachment floating off the front flange (no capture contact) → isolated-part / mating failure; rejected.
- Clamp screw translating out of the clamp boss, or hopper/mount visual detached from the throat/chamber → connectivity failure; rejected.
- Bayonet ring given a full-turn CONTINUOUS range (should be a quarter-turn REVOLUTE) → ② semantics wrong; rejected.

## 11. 与相邻类别的边界

- 不该混入：`electric_food_processor` — motor-driven, bowl + rotating blade, no hand crank / free-spinning grip. Our category is hand-cranked only.
- 不该混入：`sausage_stuffer` (without grinder) — a plain cylinder + plunger, no auger / perforated cutting plate / retaining-ring outlet. The sausage nozzle here is an *attachment* on a full grinder, not the whole device.
- 不该混入：`manual_coffee_grinder` — burr + grind-gap adjustment collar + grounds bin, no perforated meat plate; smaller countertop scale.
- 不该混入：`manual_grain_mill` — millstone/burr on an A-frame stand or trough, gravity feed, no clamp-mounted horizontal auger chamber.

## 12. 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec authored from the full 14-record 5-star pool (3 origins + 11 forked_anchor variants). One unified grind-chamber chassis (datum z=0) + 4 parallel-child slots (mount 3 / hopper_form 3 [③] / drive 3 / output 4) = 108 legal tuples; 6 palettes. All candidates source-backed. cutter_topology folded into the always-present cutter (low-visibility internal). |

## 13. 模板实现备注

- Unified world datum: grind chamber axis on world +X at z=0; outlet −X, drive +X, throat/hopper +Z, mount −Z. `body_scale` multiplies primitives; mesh helpers take `unit_scale`.
- Cadquery meshes shared across seeds via `AssetContext` cache: chamber shell, perforated plate, auger flight, 3 hopper lofts, sausage horn, kibbe cone, spline crank arm.
- Captured-pin/journal overlaps declared element-scoped: (a) `crank_grip.grip_sleeve` vs `auger_drive.grip_pin`/`spinner_axle`; (b) `auger_drive.auger_flight`/`cutter_blade` vs `body.grind_chamber`/`cutting_plate`; (c) `retaining_ring` vs `body.grind_chamber`/`cutting_plate`/outlet attachment; (d) `clamp_screw.screw_stem` vs `body.clamp_boss`. `mating` omitted on these joints (grandfathered captured hardware).
- Reuse one `_ring_mesh(form)` for plain vs bayonet, one `_hopper_mesh(form,scale)` for the 3 hoppers, one `_drive` emitter branching on Slot C, one `_outlet` emitter branching on Slot D.
- For `spoked_handwheel`, the grip parents to the offset `spinner_axle` (crank pin equivalent) rather than a bent-arm pin; keep the grip joint axis +X in all drives.

## 14. Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S3 | chassis / A / C / D | body + auger + grip + ring + table_clamp + bent_hand_crank + plain_ring | rec_picturex_0611__meat_grinder__003 | `_build_housing_cast`/`_build_cutting_plate`/`_build_auger_core`/`_build_cutter_blade`/`_build_retaining_ring`/`_build_grip`/`_build_clamp_frame`/`_build_screw_stem`/`_build_clamp_pad`/`crank_arm` spline | unified chassis + spine + default crank/ring + clamp |
| S3a | A | countertop_base | rec_0611_meat_grinder_var_mount_bolt_down_countertop_base | `_build_mount_cast` | bolted foot + gussets + bolt holes |
| S3b | D | sausage_nozzle | rec_0611_meat_grinder_var_output_attachment_sausage_stuffing_noz | `_build_sausage_nozzle` | lofted tapered horn + capture flange |
| S3c | D | kibbe_former | rec_0611_meat_grinder_var_output_attachment_kibbe_former | `_build_kibbe_former` | annular cone + mandrel + 3 spokes |
| S3d | (folded) | dual_blade_cutter | rec_0611_meat_grinder_var_cutter_topology_dual_blade_cutter | `_build_cutter_blade` | two-wing swept cutter reference (folded into cutter) |
| S2 | chassis / C | C-clamp + spoked_handwheel + geared_crank | rec_picturex_0611__meat_grinder__002 | `_make_chamber`/`_make_hopper`/`_make_auger_flight`(twistExtrude)/`_make_cutting_plate` | twistExtrude auger + clamp CONTINUOUS ref |
| S2a | C | spoked_handwheel | rec_0611_meat_grinder_var_drive_spoked_handwheel | spoked_handwheel block | hub + rim + 6 spokes + spinner axle |
| S2b | C | geared_crank | rec_0611_meat_grinder_var_drive_geared_crank | `_make_geared_crank_wheel` | 18-tooth spur gear + lightening holes |
| S2c | B | wide_tray_hopper | rec_0611_meat_grinder_var_hopper_form_wide_tray_hopper | `_make_hopper` | elliptical pan loft |
| S2d | B | guarded_feed_chute | rec_0611_meat_grinder_var_hopper_form_guarded_feed_chute | `_make_hopper` | rectangular chute + guard grid |
| S1 | A / D | freestanding_pedestal + bayonet_ring | rec_picturex_0611__meat_grinder__001 | `_housing_body`/`_hopper_tray`/`_pedestal_base`/`_retaining_ring` | pedestal plinth + bayonet ref |
| S1a | A | freestanding_pedestal | rec_0611_meat_grinder_var_mount_freestanding_pedestal | `_pedestal_base` | cast plinth (sole + 2 frusta) |
| S1b | B | covered_deep_funnel | rec_0611_meat_grinder_var_hopper_form_covered_deep_funnel | `_hopper_tray` | deep funnel + rear hood |
| S1c | D | bayonet_ring | rec_0611_meat_grinder_var_retaining_bayonet_retaining_ring | `_retaining_ring` | 3-ear bayonet collar + REVOLUTE [0,0.42] |
