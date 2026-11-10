# walking_cane — Modular Spec

## 元信息

| 项 | 值 |
|---|---|
| slug | `walking_cane` |
| template path | `agent/templates/walking_cane.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `linear_chain` (handle → shaft-chain (multiplicity) → ground_interface) |

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (3 origins + 7 slot-fork variants under `data/records/`) |
| source_index_policy | only adopted module sources are indexed below |

Adopted 5-star sources (all rating=5, all synced under `arti-template/data/records/`):

- S1 `rec_walking_cane__walking_cane__001_png_edc0b703c97d47f89cc9d6d0804dc3c7/revisions/rev_000001/model.py` — green folding quad-cane: T-handle + telescoping upper + folding middle→lower + quad rubber base.
- S2 `rec_walking_cane__walking_cane__002_png_94c2f346438b418ba9729696453aa20e/revisions/rev_000001/model.py` — black adjustable cane: ergonomic T-handle + wrist strap + upper/lower telescoping tubes + adjustment button + rubber tip + optional tripod accessory base.
- S3 `rec_walking_cane__walking_cane__003_png_55ed776d6bbf4b6ebff9f55943ab9b18/revisions/rev_000001/model.py` — purple foldable cane: swept derby handle + 4-segment folding shaft chain with rubber tip.
- S4 `rec_0611_walking_cane_var_handle_form_crook/revisions/rev_000001/model.py` — crook handle variant of S1 (spline-swept shepherd's crook).
- S5 `rec_0611_walking_cane_var_handle_form_derby_offset/revisions/rev_000001/model.py` — derby offset handle variant of S2 (spline-swept forward derby crook).
- S6 `rec_0611_walking_cane_var_ground_interface_quad_base/revisions/rev_000001/model.py` — quad base variant of S2 (4 legs on a central hub replacing rubber tip).
- S7 `rec_0611_walking_cane_var_ground_interface_tripod_base/revisions/rev_000001/model.py` — tripod base variant of S3 (splayed 3-leg foot from central hub, mesh_from_geometry).
- S8 `rec_0611_walking_cane_var_secondary_motion_folding_seat/revisions/rev_000001/model.py` — folding-seat variant of S1 (cadquery seat plate + folding legs).
- S9 `rec_0611_walking_cane_var_shaft_count_2_telescoping_stages/revisions/rev_000001/model.py` — 2-stage telescoping shaft (parametrized `NUM_TELESCOPING_STAGES=2`).
- S10 `rec_0611_walking_cane_var_shaft_count_4_folding_segments/revisions/rev_000001/model.py` — 4 folding tube segments (`SHAFT_SEGMENT_COUNT=4`).

## 核心身份

Real-world walking cane: a hand-held mobility aid consisting of (a) an ergonomic upper **handle** the user grips, (b) one or more **shaft** segments (rigid, telescoping, or folding) transmitting weight from hand to ground, and (c) a **ground interface** (rubber tip / quad / tripod base) making stable ground contact. All source records preserve this triad and expose at least one non-FIXED joint (telescoping slide, folding hinge, or spring-button press).

Not to be confused with:

- **plain rod / rigid pole** — no ergonomic hand terminal, no ground foot; the cane's identity requires both.
- **crutch / walker** — has under-arm cradle / frame or multi-legged upright frame the user stands inside; canes are hand-held single-point support.
- **umbrella / hiking pole with grip strap** — different terminal function (canopy or telescoping trek pole); canes have a static hand-support handle designed for weight-bearing, not an opening spring or ice pick.

## 槽位 + 候选模块表

### Slot A：handle_form (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| t_handle | forked_anchor | S1 | model.py:L73-L125 | eligible if compatible | Capsule grip (+X axis), short vertical neck cylinder, wrist-strap eyelet + strap loop (mesh_from_geometry TorusGeometry + tube_from_spline_points). form_subtype=Volumetric Envelope Form (axial capsule). |
| ergonomic_T | forked_anchor | S2 | model.py:L92-L143 | eligible if compatible | Capsule grip rotated to +X, `Box` bracket + white socket collar (`_tube_shell` LatheGeometry), Sphere strap eyelet + Box eyelet stem, dark finger-groove cylinders as inline decoration. form_subtype=Volumetric Envelope Form. |
| crook | forked_anchor | S4 | model.py:L72-L106 | eligible if compatible | Spline-swept shepherd's-crook mesh via `tube_from_spline_points` (curving over top of shaft), transition collar. form_subtype=Macro Surface Construction (swept curve). |
| derby_offset | forked_anchor | S5 | model.py:L92-L139 | eligible if compatible | `tube_from_spline_points` derby crook (forward offset) + thicker grip sleeve section + Sphere end cap. form_subtype=Macro Surface Construction. |
| derby_swept | forked_anchor | S3 | model.py:L149-L182 | eligible if compatible | `sweep_profile_along_spline(rounded_rect_profile, ...)` broad swept-curve derby with palm bulge + hook_round spheres. form_subtype=Macro Surface Construction. |

### Slot B：shaft_count (multiplicity — number of stacked shaft segments)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| n2_telescoping | forked_anchor | S9 | model.py:L152-L226 (build), L232-L295 (joints) | eligible if compatible | 2 PRISMATIC stages: each stage is a `Cylinder` tube inside an outer `_hollow_ring` sleeve; child stage slides along -Z; allow_overlap on sleeve↔tube. |
| n2_folding | forked_anchor | S3 | model.py:L86-L292 (relevant folding chain L201-L292) | eligible if compatible | 2 REVOLUTE shaft segments joined by `fold_joint_i` (axis Y, rpy pre-set to zig-zag), collar hardware at each interface. |
| n3_telescoping | world_knowledge_extrapolation (multiplicity extension of S9) | anchors: S1, S2, S9 + reviewer | multiplicity extension via same helper `_stage_tube` from S9:L70-L73 | eligible if compatible | Same PRISMATIC pattern as n2 but a third nested stage; standard 3-stage adjustable canes exist. |
| n3_folding | forked_anchor | S3 (has 3 fold joints), reinforced by S10 pattern | S3:L261-L292 (3 REVOLUTE joints), S10 shows helper `_add_fold_segment_visuals` L75-L93 | eligible if compatible | 3 REVOLUTE segments (canonical foldable trekking-cane count). |
| n4_folding | forked_anchor | S10 | model.py:L23-L120 (constants + helper), main build L95-L400 | eligible if compatible | 4 REVOLUTE folding segments with `_add_fold_segment_visuals` helper; per-segment `_hollow_ring` collars. |
| n1_rigid | forked_anchor | S3 (handle_segment is a single rigid upper section L86-L197 without articulation) | S3:L107-L197 | eligible if compatible | Single rigid shaft — no articulated joint chain; ground interface still articulates via FIXED. Requires a non-FIXED motion elsewhere; only paired with a multi-leg base with a folding accessory (declare: with `n1_rigid`, ground interface downstream must carry the required non-FIXED joint — realized via a small PRISMATIC adjustment button pressed on the shaft, sourced from S2 button pattern). |

### Slot C：ground_interface (① structural topology)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rubber_tip | forked_anchor | S2 | model.py:L253-L272 (`_lathed_tip` L34-L46; FIXED lower_to_tip); S3:L237-L254 | eligible if compatible | LatheGeometry profile cane tip fixed to lowest shaft; `flat_tread_pad` Cylinder on bottom. Single-point contact. |
| quad_base | forked_anchor | S1 (quad_hub + 4 rubber pads) + S6 (quad accessory) | S1:L167-L203; S6:L275-L332 | eligible if compatible | Central hub disk + 4 radial legs (Cylinders) each terminated with rubber foot (Sphere or Cylinder). Wide 4-point contact. |
| tripod_base | forked_anchor | S7 | model.py:L34-L78 (`_tripod_base_mesh`) + L298-L314 (usage) | eligible if compatible | `mesh_from_geometry` CylinderGeometry union — central hub + 3 splayed legs + rubber feet. Reads as a rubberized tripod. |

Slot rationale: each slot has ≥3 structurally distinct candidates from ≥2 different origin records. The three slots share mating axes (all children mount on the shaft's -Z end / +Z end via cylinder collars), so any tuple assembles.

Compatibility gating (resolved in `resolve_config`, spec §9):

- `n1_rigid` cannot host the folding-secondary_motion; when it is chosen we force `secondary_motion=none`.
- `n2_telescoping`/`n3_telescoping` require the outer sleeve on the parent — so `handle_form` must be one of the T-shaped families (`t_handle`, `ergonomic_T`); if a swept-crook handle is drawn, we still emit an upper socket collar from the shaft module (not the handle) so the interface is preserved. No degradation needed.

## 槽位图（slot graph）

pattern: `linear_chain` (with `shaft_count` as internal multiplicity within the shaft slot)

```
handle_form            shaft_count (N stacked tube segments)                ground_interface
─────────── [FIXED   upper_socket]   ── [PRISMATIC or REVOLUTE joints between segments]  ── [FIXED  base_socket] ───
     ▲                                              ▲                                              ▲
  root part (grounded)               shaft_i cylinders                          ground foot / hub
```

Cross-slot connections & interfaces:

1. **handle → shaft**: FIXED articulation `handle_to_shaft_0` with mating between `handle_collar` (bottom face of handle module) and `shaft_0_top_collar`. Both faces axis-aligned in -Z. `iface_key = "shaft_collar_r011"` locking the tube radius agreement.
2. **shaft_i → shaft_{i+1}** (multiplicity chain):
   - PRISMATIC along -Z when the shaft family is `telescoping` (sliding sleeve/tube pair, allow_overlap on the sleeve↔tube), motion_limits (lower=0, upper≈0.070–0.090).
   - REVOLUTE around +Y when the shaft family is `folding` (fold_joint axis 0,1,0), motion_limits (lower=−fold_angle, upper=0) or (lower=0, upper=fold_angle) with meta `straight_pose` so folded rest / straight-in-line poses are both representable.
   - joint MatingContract on collar↔collar for the FIXED-during-rest pattern is not applicable (these are non-FIXED); we rely on the compiler baseline `fail_if_articulation_origin_far_from_geometry` + element-scoped `allow_overlap` for captured slide/pin geometry.
3. **shaft_last → ground_interface**: FIXED articulation `shaft_to_ground`, MatingContract between `shaft_bottom_collar` (Z-face) and ground `ground_top_face` visual on the ground module. `iface_key="cane_foot_r018"`.

Optional secondary_motion (spring button): the resolver may emit a small PRISMATIC `adjustment_button` child on shaft_1 (patterned after S2 L228-L250) when handle is one of the T-family — this is what guarantees at least one non-FIXED joint even for the `n1_rigid` shaft choice.

## 每槽位 Module Emits / Interfaces

### Slot A / module t_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `handle` | S1 model.py:L73 |
| visuals | `t_handle` (capsule +X), `handle_neck` (Cylinder), `upper_shaft_stub` (Cylinder), `handle_socket_collar` (`_hollow_ring`), optional `strap_eyelet` + `wrist_strap` | S1 L74-L125 |
| internal joints | (none — root) | — |
| upstream interface | (none — this is the root module) | — |
| downstream interface | `handle_socket_collar` bottom face (Z=−neck_len), `iface_key="shaft_collar_r011"` | S1 L96 |

### Slot A / module ergonomic_T
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `handle` | S2 L93 |
| visuals | `ergonomic_grip` (capsule +X), `white_handle_bracket` (Box), `white_socket_collar` (`_tube_shell`), `vertical_handle_post` (Box), `handle_screw` (Cylinder), `finger_groove_{i}` (inline Cylinders), `strap_eyelet` (Sphere) + `eyelet_stem` (Box) | S2 L92-L143 |
| downstream interface | `white_socket_collar` bottom face, iface_key="shaft_collar_r011" | S2 L108 |

### Slot A / module crook
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `handle` | S4 L72 |
| visuals | `crook_handle` (mesh from `tube_from_spline_points` swept crook), `crook_neck` (`_hollow_ring`), transition `upper_shaft_stub` (Cylinder) | S4 L74-L112 |
| downstream interface | `crook_neck` bottom face, iface_key="shaft_collar_r011" | S4 L101 |

### Slot A / module derby_offset
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `handle` | S5 L92 |
| visuals | `derby_crook` (mesh `tube_from_spline_points`), `ergonomic_grip` (offset section overlay), `crook_end_cap` (Sphere), `white_socket_collar` (`_tube_shell`) | S5 L92-L155 |
| downstream interface | `white_socket_collar` bottom face | S5 L149 |

### Slot A / module derby_swept
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `handle` | S3 L100 |
| visuals | `curved_handle` (mesh via `sweep_profile_along_spline(rounded_rect_profile)`), `handle_palm_bulge` + `handle_hook_round` (Spheres), `handle_neck` (Cylinder), `white_handle_collar` (Cylinder) | S3 L149-L196 |
| downstream interface | `white_handle_collar` bottom face | S3 L116 |

### Slot B / module n{2..4}_telescoping (multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shaft_0 … shaft_{N-1}` | S9 |
| visuals per shaft_i | `tube_i` (Cylinder), `top_collar_i` (`_hollow_ring`), `bottom_collar_i` (`_hollow_ring`), optional `pin_hole_{j}` per adjustment row (S2 pattern) | S9 L70-L226 |
| internal joints | `slide_i` (PRISMATIC axis (0,0,−1), lower=0, upper=stage_travel) between shaft_{i-1} and shaft_i | S9 L232-L262 |
| upstream interface | `top_collar_0` top face, iface_key="shaft_collar_r011" | derived |
| downstream interface | `bottom_collar_{N-1}` bottom face, iface_key="cane_foot_r018" | derived |

### Slot B / module n{2..4}_folding (multiplicity)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shaft_0 … shaft_{N-1}` | S3 / S10 |
| visuals per shaft_i | `tube_i` (Cylinder), `top_collar_i` (Cylinder), `bottom_collar_i` (Cylinder), `upper_cord_socket_i`, `lower_cord_socket_i` (Cylinder end plugs) | S3 L86-L155 / S10 L75-L93 |
| internal joints | `fold_joint_i` (REVOLUTE axis (0,1,0), rpy pre-set to fold_angle so rest pose is zig-zag / stow, motion_limits allow straightening) between shaft_{i-1} and shaft_i | S3 L261-L292 |
| upstream interface | `top_collar_0` top face, iface_key="shaft_collar_r011" | derived |
| downstream interface | `bottom_collar_{N-1}` bottom face (last-segment lower cord socket), iface_key="cane_foot_r018" | derived |

### Slot B / module n1_rigid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shaft_0` (single) + `adjustment_button` (small PRISMATIC child, so a non-FIXED joint exists) | S3 handle_segment L107-L197 + S2 L228-L250 |
| visuals per shaft_0 | `tube_0` (Cylinder), `top_collar_0` (Cylinder), `bottom_collar_0` (Cylinder), `pin_hole_{j}` inline visuals | S3, S2 |
| internal joints | `button_press` PRISMATIC on shaft_0, axis (1,0,0), tiny travel (motion_limits ≈ [−0.004, 0.002]) | S2 L228-L250 |
| upstream interface | `top_collar_0` top face | derived |
| downstream interface | `bottom_collar_0` bottom face | derived |

### Slot C / module rubber_tip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ground_foot` | S2 L253 |
| visuals | `rubber_tip_body` (LatheGeometry lathed profile), `flat_tread_pad` (Cylinder), `ground_top_face` (small Cylinder socket for MatingContract) | S2 L253-L272 |
| internal joints | (none) | — |
| upstream interface | `ground_top_face` +Z face, iface_key="cane_foot_r018" | derived |

### Slot C / module quad_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ground_foot` | S1 L153 / S6 L276 |
| visuals | `quad_hub` (Cylinder), `quad_arm_{i}` (Cylinder ×4, radial), `rubber_pad_{i}` (Cylinder or Sphere ×4) or `base_rubber_foot_{i}`, `ground_top_face` (Cylinder socket) | S1 L167-L203; S6 L275-L332 |
| internal joints | (none) | — |
| upstream interface | `ground_top_face` +Z face | derived |

### Slot C / module tripod_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ground_foot` | S7 L34-L78, L298-L314 |
| visuals | `tripod_base_mesh` (`mesh_from_geometry` union of hub cylinder + 3 splayed leg cylinders + 3 rubber-foot cylinders), `ground_top_face` (Cylinder socket) | S7 L34-L78 |
| internal joints | (none) | — |
| upstream interface | `ground_top_face` +Z face | derived |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `handle_form` | enum | t_handle / ergonomic_T / crook / derby_offset / derby_swept | — | choice | procedural sampler | Slot A |
| `shaft_family` | enum | telescoping / folding / rigid | — | choice | procedural sampler | Slot B |
| `shaft_count` | int | {1, 2, 3, 4} | — | conditional | rigid → 1; telescoping → sample {2,3}; folding → sample {2,3,4} | S9, S10, S3 |
| `ground_interface` | enum | rubber_tip / quad_base / tripod_base | — | choice | procedural sampler | Slot C |
| `palette_style` | enum | matte_green / brushed_black / glossy_purple / bare_aluminum / walnut_wood / painted_red | matte_green | choice | procedural sampler | S1, S2, S3, world-knowledge extension |
| `handle_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | dimensional variation across sources |
| `shaft_length_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp | S1 middle=0.42m, S2 upper=0.50m, S3 segment=0.27m |
| `shaft_radius_scale` | float | [0.90, 1.10] | 1.0 | independent | clamp; `shaft_r = 0.011 * shaft_radius_scale` | S1 r=0.012, S2 r=0.0065–0.011, S3 r=0.011 |
| `fold_angle_scale` | float | [0.85, 1.10] | 1.0 | independent | clamped; nominal fold ≈ 2.0 rad | S3 fold_1..3 |
| `telescoping_travel_scale` | float | [0.85, 1.10] | 1.0 | independent | clamped; nominal per-stage travel = 0.070 m | S1, S2 slide upper |
| `include_button` | bool | derived from shaft_family | — | conditional | `include_button = shaft_family in {telescoping, rigid}` (adds S2 spring button) | S2 pattern |
| (—) | constraint | — | — | inequality | `sum(shaft_length) * shaft_length_scale ≤ 1.4m` (total cane length envelope for realistic proportions) | field |
| (—) | constraint | — | — | inequality | `(N-1) * bottom_collar_z_extent + tube_radius ≤ shaft_r_inner` (nested telescoping legality) | S9 L152 |

Continuous sampling contract (from `SPEC_TEMPLATE.md` §7): resolver first fixes scale parameters (independent), derives shaft dimensions, then applies clamps + inequality projection; the total-length inequality falls back to per-segment shrinkage.

### 7.5 编译预算 / compile budget

Target per-seed compile: **≤ 15 s** (typical). All modules use Cylinder / `_hollow_ring` (LatheGeometry, ≤48 segments) / cheap `mesh_from_geometry`; only `tripod_base` and swept-handle families use richer mesh unions with segment counts ≤24. Multiplicity is bounded (N ≤ 4). `tube_from_spline_points`/`sweep_profile_along_spline` handle geometry stays at `samples_per_segment ≤ 22`, `radial_segments ≤ 24`. If observed > 20 s, drop `radial_segments` to 16 first, then reduce `samples_per_segment`.

## Multiplicity / Copy Logic

Axis: `shaft_count_count` (Slot B).

- `count_param`: `shaft_count`
- `N_range` (product domain): `{1, 2, 3, 4}` — driven by source anchors (S9 N=2 telescoping, S3 N=3/4 folding, S10 N=4 folding, S3 handle_segment as N=1 rigid).
- sampling domain (per shaft_family):
  - `telescoping`: {2, 3} with weights (0.65, 0.35) (canonical adjustable-height canes are 2-stage; 3-stage exists but is rarer).
  - `folding`: {2, 3, 4} with weights (0.30, 0.40, 0.30) (3-4 is the classic foldable-cane count; 2 exists but is thinner in sources).
  - `rigid`: N=1 (no sampling — deterministic).
- copied object: one `shaft_i` part per index; shared helpers `_build_telescoping_stage(part, i, tube_r, sleeve_r, length)` and `_build_folding_segment(part, i, tube_r, collar_r, length)` — identical geometry per index so bbox proportional to N.
- naming: `shaft_{i}`, joint `stage_slide_{i}` (telescoping) or `fold_joint_{i}` (folding).
- placement: serial chain along -Z; telescoping via PRISMATIC (each child origin at parent's `bottom_collar` interface); folding via REVOLUTE (each child origin at parent's `bottom_collar`, rpy pre-set to zig-zag fold angle so rest pose is stowed).
- joint policy: uniform (see slot graph); MatingContract omitted for slide/fold pairs (captured-slide/pin geometry — grandfathered) and covered by element-scoped `allow_overlap` between adjacent stage tubes / cord sockets.
- source/gating: `shaft_family` picks the pattern; `include_button` accessory on `shaft_1` (if it exists) or `shaft_0` provides a small PRISMATIC control so at least one non-FIXED joint always exists (guarantees Rule 5 test coverage even when N=1 rigid).

### 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B `shaft_family` × `shaft_count`: N shafts in a chain; joint chain length 1..N; ground_foot as separate part. Source-backed: S1 (3 shaft parts), S2 (upper+lower+button+tip+alt), S3 (handle+3 shafts+tip), S9 (N=2 telescoping), S10 (N=4 folding). |
| └ multiplicity | 同构件 ×N | 有 | See §8: N ∈ {1..4} per shaft_family; source-backed by S9/S10/S3. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | Slot B decides: telescoping → PRISMATIC axis (0,0,−1); folding → REVOLUTE axis (0,1,0). Optional `button_press` PRISMATIC axis (1,0,0). Source-backed: S1 has PRISMATIC + REVOLUTE, S3 has 3 REVOLUTE, S2 has 2 PRISMATIC. Every declared joint type appears in the sweep. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot A `handle_form` (5 candidates): t_handle (Volumetric Envelope Form), ergonomic_T (Volumetric Envelope Form), crook (Macro Surface Construction — swept curve), derby_offset (Macro Surface Construction — swept curve), derby_swept (Macro Surface Construction — swept `rounded_rect_profile`). Also Slot C `ground_interface` is ① primary (3 candidates: rubber_tip Volumetric Envelope Form, quad_base + tripod_base Planar Boundary Form). ≥3 recognizable form prototypes registered into `slot_choices`. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Inline visuals on shaft: `pin_hole_{i}` adjustment holes (0..5 rows), `finger_groove_{i}` on ergonomic_T handle, `strap_eyelet` + wrist_strap on grip families, latch_body/latch_slider on flashlight-cane style. All host-conformal (Cylinder pushed to shaft surface at `shaft_r + eps`). source_type=record_only. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | See §7: `handle_scale ∈ [0.85, 1.15]`, `shaft_length_scale ∈ [0.85, 1.15]`, `shaft_radius_scale ∈ [0.90, 1.10]`, `fold_angle_scale ∈ [0.85, 1.10]`, `telescoping_travel_scale ∈ [0.85, 1.10]`. Motion envelopes: `stage_slide_i` PRISMATIC axis (0,0,−1), [closed=0, upper≈0.070–0.090 m]; `fold_joint_i` REVOLUTE axis (0,1,0), [closed=fold_rest, upper=0 or straight]; `button_press` PRISMATIC axis (1,0,0), [−0.004, 0.002]. `motion_test_plan`: sampled collision on all joints via `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`; targeted `ctx.pose({slide: upper})` verifies extension AABB shift, `ctx.pose({fold: straight})` verifies straightened AABB. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `palette_style ∈ {matte_green, brushed_black, glossy_purple, bare_aluminum, walnut_wood, painted_red}`. Materials cover metal (aluminum + purple anodized + brushed silver) and painted (green, red) and wood (walnut), giving ≥3 material families across ≥6 palettes; source-backed by S1 (green+metal+rubber), S2 (black+aluminum+silver+white), S3 (purple+silver+black); walnut_wood + painted_red are world-knowledge extensions for realistic cane finishes. |

## 采样与覆盖审计

Total combinations: 5 (handle_form) × 3 (shaft_family) × 4 (shaft_count values across families) × 3 (ground_interface) × 6 (palette_style) ≈ **1080** (before compatibility gating). Realistic reachable: ≈ 900 after gating (rigid → N=1 only).

Reason: three real ① / ③ topological axes plus one ⑥ palette axis and one internal ② multiplicity axis; every axis has source-backed candidates.

`seed_domain_policy`: procedural_first.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` uses `random.Random(seed)` — first samples `handle_form`, `shaft_family`, `ground_interface`, `palette_style`; then samples `shaft_count` from the family-conditional domain; then samples continuous scale parameters uniformly in their independent ranges. `resolve_config` clamps, enforces the shaft-count/family compatibility, and derives `include_button`. Sweep 0-35 covers all discrete axes; corner stage covers min/max on continuous scales. Topology target: 1000 seeds → expect >250 unique slot tuples given ~900 legal combinations. No small curated table.

Regression overrides: none at initial version.

Controlled local parameterization: `handle_scale`, `shaft_length_scale`, `shaft_radius_scale`, `fold_angle_scale`, `telescoping_travel_scale` — all clamped per §7, all independent, none breaks InterfaceSpec or clearance because collar bores derive `sleeve_inner = shaft_r + tube_gap` (tube_gap constant 0.0008 m for telescoping, tube_gap 0.001 m for fixed collars); MatingContract on FIXED handle→shaft and shaft→ground uses collar radii derived from `shaft_r_final`.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `random.Random(seed)`: handle_form, shaft_family, shaft_count (conditional), ground_interface, palette_style, then continuous scales | slot_choices_for_seed matches build choices |
| compatibility matrix | rigid → N=1 forced; telescoping/folding → N drawn from family-conditional domain; button accessory when handle is T-family AND shaft_family in {telescoping, rigid} | axis_realization shows all handle_form / shaft_family / ground_interface / N values reached |
| controlled local variation | 5 scale parameters, each clamped; MatingContract-relevant radii derived, not sampled independently | proportions vary without breaking interfaces or joint origin proximity |
| regression overrides | none | — |
| random sweep | 0-35 initial pass; 0-999 maturity audit | motion_test_audit for slide + fold + button; axis_realization for slot value counts |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| handle_form | 5 | yes | yes | ③ Primary Form Family slot |
| shaft_family | 3 | yes | yes | ① / ② combined family axis |
| shaft_count | 4 realized (1..4) | yes | yes | multiplicity within Slot B |
| ground_interface | 3 | yes | yes | ① topology axis |
| palette_style | 6 | yes | yes | ⑥ palette |

## Validator

- `slot_choices_for_seed` returns tuples for handle_form / shaft_family / shaft_count / ground_interface / palette_style that match the built model.
- `config_from_seed` uses deterministic `random.Random(seed)` for every seed including 0.
- Compatibility matrix in `resolve_config` prevents illegal `n1_rigid + folding` or `n>1 + rigid` combos (`n1_rigid` locks shaft_family=rigid, N=1).
- No small curated table.
- Continuous scale params are clamped to declared ranges; radii derivations (collar_inner = shaft_r + 0.0008) prevent interface breakage.
- Cross-part shaft_r derivations resolved in `resolve_config`.
- Critical InterfaceSpec / MatingContract points exist:
  - `handle → shaft`: FIXED with MatingContract on `handle_socket_collar` ↔ `shaft_0_top_collar`, tangential_containment=True.
  - `shaft_{N-1} → ground_foot`: FIXED with MatingContract on `shaft_bottom_collar` ↔ `ground_top_face`, tangential_containment=True.
  - Non-FIXED chain joints (`stage_slide_i`, `fold_joint_i`, `button_press`) omit MatingContract (captured slide/pin geometry — grandfathered by baseline).
- Key joints have expected type / axis / range: PRISMATIC (0,0,−1) for telescoping; REVOLUTE (0,1,0) for folding; PRISMATIC (1,0,0) for spring button.
- Copied objects follow naming policy (`shaft_{i}`, `stage_slide_{i}`, `fold_joint_{i}`).
- Rule 5 coverage: `run_walking_cane_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` + at least one `ctx.pose(...)` per key mechanism (extend slide, straighten fold, press button).

## Reject cases

- No handle module — a "cane" without a hand terminal is a plain rod (blocked at spec).
- Ground_interface floating above shaft — MatingContract with `tangential_containment=True` guarantees the foot sits under the shaft.
- Folded shaft self-intersecting at rest — clamp fold_angle_scale via clearance solver; if collision persists, reduce N or fold angle.
- Telescoping stage over-extended so lower tube exits the sleeve — inequality `stage_travel ≤ sleeve_length − guide_min_engagement` enforced in `resolve_config`.
- Handle collar and shaft radius mismatch — both derived from shared `shaft_r_final`; iface_key gate on unit test builds.
- Any slot module without a real anchoring visual on the mating face → Rule 2 violation.

## 与相邻类别的边界

- 不该混入: **crutch** — has a top under-arm cradle, not a hand-grip; handle_form never emits an under-arm pad.
- 不该混入: **umbrella / trek pole** — no canopy or opening mechanism; telescoping joints here are for height adjustment (short travel ≤ 0.09 m per stage), not multi-fold canopy shafts.
- 不该混入: **walker / rollator** — a walker is a multi-legged upright frame the user stands inside; a cane is a single-shaft hand-held support.
- 不该混入: **hiking staff / plain rod** — a plain rod has no ergonomic handle terminal and no rubberized ground foot module.

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored by P3+P4 subagent based on 10 5-star records (3 origins + 7 slot-fork variants). |

## 模板实现备注

- Shared helper `_hollow_ring(outer_radius, inner_radius, length, name)` reused across all shaft & collar hardware (matches S1/S3/S9 helpers).
- `handle_form=crook/derby_offset/derby_swept` require `tube_from_spline_points` / `sweep_profile_along_spline` — keep mesh sampling at library defaults (`samples_per_segment=16..22, radial_segments=16..24`) to stay under compile budget.
- Non-FIXED joints (`stage_slide_i`, `fold_joint_i`, `button_press`) do not carry MatingContract — they are captured-slide/captured-pin patterns; instead they use `ctx.allow_overlap` with element-level scope (e.g., `allow_overlap(shaft_i, shaft_{i+1}, elem_a="bottom_collar_i", elem_b="tube_{i+1}")`) mirroring S1/S2/S9 patterns.
- FIXED `handle_to_shaft` and `shaft_last_to_ground` declare MatingContract (`tangential_containment=True`) on the collar↔collar interface.
- No cadquery required in the initial version (S8 folding-seat uses cadquery; we skip that secondary_motion in v1 to keep compile fast). Rule 5 satisfied via slide/fold/button motion.
