# rivet_squeeze1 — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `rivet_squeeze1` |
| template path | `agent/templates/rivet_squeeze1.py` |
| test path (optional) | `tests/agent/test_rivet_squeeze1_template.py` (not authored; sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (a central `head` chassis + two mirrored REVOLUTE handle children; every slot emits inline visuals onto `head`/`handle_0`/`handle_1`) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 (1 origin seed + 13 slot-fork variants) |
| read_count | 14 |
| read_scope | all 5-star samples in this subcategory (0611 / rivet_squeeze1) |
| source_index_policy | only adopted module sources are indexed below |

Reading summary. All 14 records share ONE kinematic identity: parts `head` + `handle_0` + `handle_1`, and exactly **2 revolute squeeze joints** `head_to_handle_0` (free DOF, axis (0,−1,0), lower 0 / upper 0.35) + `head_to_handle_1` (axis (0,1,0), **mimic** of `_0`, multiplier 1.0). The mimic makes the two handles a symmetric squeeze about the central head. The `head` is a clean STATIC enclosed assembly; each variant swaps exactly ONE module/form slot and keeps the 2-revolute identity intact. Every record builds geometry with `cadquery` → `mesh_from_cadquery` (Lathe-class `revolve`, `sweep(makeHelix)`, `loft`, `polyline.extrude`, boolean `cut`/`union`) — NO record uses crude Box/Cylinder for the hero forms, so the template must preserve those primitives (Rule 3). Each handle carries a spare-tip holder on `handle_0` only (rack N=3 seed / magazine N=6 variant). The seed head visuals: `head_spine` + `red_head_body` (polyline-extruded anodized cover) + `side_plate_left/right` (diagonal links seated in slots) + `lower_housing` (solid cast block) + `pull_rod` + recessed `*_screw_*` hex fasteners + `branded_plate` + `brand_mark_{0..2}`; top nose stack `nose_washer` + `knurled_collar` + `hex_lock_nut` + `mandrel_tip`; under-head `bottle_adapter` + `collection_bottle`. Each handle: `metal_arm` + `pivot_lug` + `grip_core` + `grip_overmold(+_back)` + `pivot_cap`. The pivot is captured-pin geometry (round `pivot_lug` seated inside the machined cover pocket) — the source `run_tests` uses element-scoped `allow_overlap` + `expect_overlap` for the lug/cap, not a `MatingContract`.

## 核心身份

A **hand-powered two-handle lever rivet / rivet-nut setter**: two lever handles squeeze about a central head to pull a mandrel through a top nosepiece stack, catching spent mandrels in an under-head bottle. Physical invariants (must_keep): a central head with a top mandrel-pull nosepiece stack; two lever handles on a **symmetric revolute squeeze** (≥1 non-fixed joint, here 2 with a mimic); hand-powered actuation; an under-head spent-mandrel bottle. Default mature domain: a red/anodized-cover enclosed cast head, wide-V rubber-gripped handles, a translucent white catch bottle, and 3 spare nose tips on a handle rack. It must NOT drift into: a pneumatic/battery power rivet gun (powered, not hand-lever); a bench/press-mounted riveter (not handheld); a generic pliers/crimper/wire-stripper (no mandrel-pull nose stack + catch bottle).

## 槽位 + 候选模块表

All slots are source-backed and keep the fixed head + 2-revolute squeeze identity. Line ranges are `model.py:Lx-Ly` in each record's `revisions/rev_000001/model.py`.

### Slot A：handle_topology  (① skeleton)

Drives the moving `metal_arm` silhouette (segment count / reach / drop) and the grip + spare-rack attachment points on each handle. Same 2-revolute squeeze in every candidate.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wide_v (baseline) | origin_anchor | seed `rec_use-the-attached-...f3961d86` | L101-L160 (`_handle_shapes`) | eligible if compatible | two-segment shallow wide-V arm; grip far out at x≈0.39, z≈-0.16 |
| long_straight | forked_anchor | `rec_rivet_squeeze1_var_handle_long_straight` | L101-L175 (`_handle_shapes`, elbow knuckle L123-L129) | eligible if compatible | long near-parallel arm dropping to z≈-0.55; forged elbow knuckle |
| compact_short | forked_anchor | `rec_rivet_squeeze1_var_handle_compact_short` | L101-L162 (`_handle_shapes`) | eligible if compatible | short steeply-dropped stubby arm; grip at x≈0.19, z≈-0.21 |
| cranked_offset | forked_anchor | `rec_rivet_squeeze1_var_handle_cranked_offset` | L101-L183 (`_handle_shapes`; crank point p3 L110, forged knuckle bridges L119-L132) | eligible if compatible | three-segment dog-leg arm; grip dropped below pivot continuation; spare rack seated flush on outer shank |

### Slot B：head_form  (③ Primary Form Family — registered ③ slot)

Drives `red_head_body` + `lower_housing` + head enclosure geometry. Each is a recognizable ③ prototype; the top nose, pull rod, spine, screws, brand, bottle interface are preserved.

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| enclosed_cast (baseline) | origin_anchor | seed | L183-L266 (spine L183-193, side links L199-203/L244-249, red_body polyline L220-241, lower_housing L253-266) | Planar Boundary Form | eligible if compatible | rounded polyline-extruded anodized cover + solid cast lower block; two diagonal side links seated in cover/housing slots |
| inline_steel_linkage | forked_anchor | `rec_rivet_squeeze1_var_head_inline_steel_linkage` | L167-L287 (sealed spine cassette L167-175; front_plate/rear_plate/plate_bridge L206-287) | Macro Surface Construction | eligible if compatible | open spaced machined face-plate pair tied by a perimeter bridge around a sealed center cassette; adds `rear_head_plate` + `head_plate_bridge` visuals |
| squared_cast | forked_anchor | `rec_rivet_squeeze1_var_head_squared_cast` | L219-L307 (red_body box+chamfer+recess panels L219-259; boxy lower_housing L268-307) | Volumetric Envelope Form | eligible if compatible | broad rectangular chamfered cast blocks with recessed dark fastener panels; adds `head_side_panel_*` + `lower_side_panel_*` |
| round_barrel | forked_anchor | `rec_rivet_squeeze1_var_head_round_barrel` | L53-L79 (`_revolved_barrel` lathe revolve), L250-272 (upper barrel + pivot bosses + screw sleeves), L289-300 (lower barrel) | Volumetric Envelope Form | eligible if compatible | short lathe-turned cylindrical barrel sections (revolve母线) with cast pivot ears; **LatheGeometry — must not downgrade to Cylinder** |

### Slot C：nosepiece_form  (③ form)

Drives the top vertical mandrel-pull stack on `head`.

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| single_stack (baseline) | origin_anchor | seed | L301-L324 (`_knurled_collar` L53-64; washer/collar/lock_nut/mandrel_tip) | Volumetric Envelope Form | eligible if compatible | short washer + knurled collar + hex lock nut + square mandrel tip, inline |
| long_mandrel_stem | forked_anchor | `rec_rivet_squeeze1_var_nosepiece_long_mandrel_stem` | L53-L65 (tall `_knurled_collar`, 0.052 high, 32 ribs), L305-L342 (reordered stack + threaded stem) | Macro Surface Construction | eligible if compatible | tall ribbed chuck collar + long visibly-threaded steel mandrel rod (17 thread crests) + terminal hex chuck + square drive rising far above the head |

Degrade note: only 2 candidates. The 12-tool reference sheet shows only these two nose-stack lengths (short inline vs long exposed threaded stem); no third source-backed nose prototype exists. ≥2 with documented reason is compliant per SPEC_TEMPLATE §4.

### Slot D：return_mechanism  (② mechanism / ④)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none_static (baseline) | origin_anchor | seed | (absence — no return spring visual) | eligible if compatible | enclosed static toggle; no exposed return coil |
| two_handle_return_coils | forked_anchor | `rec_rivet_squeeze1_var_mechanism_return_spring` | L67-L145 (`_return_spring`/`_round_rod`/`_handle_return_spring` helix sweep), L463-L472 (per-handle emit) | eligible if compatible | one helical return coil + L-anchor wire per handle (a `return_spring` visual on EACH handle, swings with the handle); 2-revolute squeeze kept, no new powered joint |

Degrade note: 2 candidates (present / absent). Adding a return coil vs not is a real ② mechanism-presence axis observed in the pool. No third distinct return topology in the source set.

### Slot E：grip_construction  (④ grip module)

Drives grip visuals on each handle (host-conformal to the arm-end run).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| two_tone_overmold (baseline) | origin_anchor | seed | L133-L151 (`grip` beam + ridges + `panel_front/back`), L357-L370 (emit) | eligible if compatible | black molded core + red/coloured front+rear overmold panels (3 visuals) |
| single_ribbed_sleeve | forked_anchor | `rec_rivet_squeeze1_var_grip_single_ribbed_sleeve` | L133-L162 (one ribbed sleeve: 7 transverse bands + flared butt collar), L359-L361 (single emit) | eligible if compatible | one continuous molded ribbed rubber sleeve per handle; no two-tone panels (1 visual) |
| closed_loop_ring | forked_anchor | `rec_rivet_squeeze1_var_grip_closed_loop_ring` | L101-L154 (`_d_ring_grip` threePointArc loop + pads), L189-197 (`_handle_shapes` use) | eligible if compatible | closed D-ring loop grip (arc-extruded ring) + distal rubber pads at each arm end |

### Slot F：collection_bottle  (④ module)

Drives the under-head catch bottle + adapter on `head`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| compact_underslung (baseline) | origin_anchor | seed | L67-L98 (`_bottle`), L327-L338 (adapter + bottle emit straight below) | eligible if compatible | compact thin-wall translucent bottle straight below the head, screwed onto the adapter |
| large_canister | forked_anchor | `rec_rivet_squeeze1_var_bottle_large_canister` | L67-L101 (enlarged `_bottle`: body_height 0.180, r 0.035, stiffener hoops), L346-L348 (bottle emit, lower translate −0.293) | eligible if compatible | taller/larger cylindrical screw-on catch canister on the same adapter |
| angled_side_mount | forked_anchor | `rec_rivet_squeeze1_var_bottle_angled_side_mount` | L326-L372 (angled adapter stub + diagonally-hung bottle at −35°) | eligible if compatible | bottle on a diagonal threaded stub off one side of the lower casting, hanging down/outward off the pull-rod axis |

### Slot G：spare_tip_multiplicity  (N — multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rack_N (baseline family) | origin_anchor | seed | L381-L400 (`spare_tip_rack` beam + `spare_tip_{0..2}` loop) | eligible if compatible | linear spare-tip rack beam on `handle_0` with N seated hex nose tips |
| magazine_N (family) | forked_anchor | `rec_rivet_squeeze1_var_tip_magazine_six` | L67-L103 (`_spare_nose_tip` machined tip), L418-L451 (indexed magazine block + `tip_{0..5}` loop, range(6)) | eligible if compatible | onboard indexed magazine block with N sockets + N seated machined nose tips on `handle_0` |

N axis: count 3–8 (see §8). Both rack and magazine are the same multiplicity axis realized on a holder; N is the topology variation (never counted toward distinctness, only coverage).

## 槽位图（slot graph）

pattern: `parallel_children`

```
                      head (central chassis part — the grounded root)
   ┌──────────────┬──────────────┬──────────────┬───────────────┐
Slot B head_form  Slot C nose    Slot F bottle   Slot D return   (all inline visuals ON head, except return which is ON handles)
(cover+lower+     (top mandrel    (adapter+bottle
 side links+      stack)          below/side)
 spine+screws)
                      │
      head_to_handle_0 REVOLUTE  axis (0,−1,0)  origin (−0.050,0,0.012)  lower 0 / upper = derived squeeze_upper   [FREE DOF]
      head_to_handle_1 REVOLUTE  axis (0, 1,0)  origin ( 0.050,0,0.012)  MIMIC(head_to_handle_0, ×1.0)            [symmetric follower]
                      │
   handle_0 (side −1)          handle_1 (side +1)
   Slot A handle_topology (metal_arm + pivot_lug + pivot_cap)
   Slot E grip_construction (grip visuals)
   Slot D two_handle_return_coils (one return_spring visual per handle)
   Slot G spare_tip_multiplicity (rack/magazine + N tips) — handle_0 ONLY
```

- **Root / support base**: `head` is the grounded chassis. The two handles are its REVOLUTE children; every other slot contributes inline visuals to `head`, `handle_0`, or `handle_1` (no cross-slot InterfaceSpec chain — this is parallel-children like `nutcracker`, not a serial mating chain).
- **The two squeeze joints** are the only non-fixed articulations. Pivot geometry is captured-pin (round `pivot_lug` seated inside the machined cover pocket): the joint origin lies on the cover hardware; the joint **omits `MatingContract`** (captured-pin exception, AUTHORING Rule 2) and is guarded by element-scoped `allow_overlap` + `expect_overlap` for `pivot_lug`↔cover and `pivot_cap`↔cover, exactly as the seed/nutcracker sibling do.
- **Composability**: Slots A–G are independent — each swaps geometry on a fixed skeleton, all keeping the 2-revolute squeeze. head_form × handle_topology × nosepiece × grip × bottle × return × N are composable (§9 matrix), with two derived guards: (i) `squeeze_upper` is derived from the realized grip reach so mirrored grips stay clear of the centerline across combos; (ii) `angled_side_mount` bottle keeps its diagonal clear of the handles.

## 每槽位 Module Emits / Interfaces

### Slot A / handle_topology (`_handle_shapes(side, topology)`), emitted on `handle_0`/`handle_1`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `metal_arm`, `pivot_lug` visuals (grip/cap/rack added by other slots) | seed L101-160; variants per table |
| internal joints | none (single rigid handle part per side) | — |
| upstream interface | captured pivot: `pivot_lug` circle at part-frame origin, seated in head cover pocket at joint origin | seed L116-119, L402-420 |
| downstream interface | grip/rack attach points (`g0/g1`, rack start/end) passed to Slots E/G | seed L110-113, L381 |

### Slot B / head_form (`_emit_head_form`), emitted on `head`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head_spine`, `red_head_body`, `side_plate_left/right`, `lower_housing`, `pull_rod` (+ variant `rear_head_plate`/`head_plate_bridge` or `*_side_panel_*`) | seed L183-266; variants |
| internal joints | none (all inline head visuals) | — |
| upstream interface | pivot pockets at x=±0.050,z=0.012 (host for the two revolutes) | seed L199-203, L402-420 |
| downstream interface | nose seat (top face ~z=0.069), bottle adapter seat (~z=−0.104) for Slots C/F | seed L301, L327 |

### Slot C / nosepiece_form (`_emit_nosepiece`), emitted on `head`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nose_washer`, `knurled_collar`, `hex_lock_nut`, `mandrel_tip` | seed L301-324; long-stem variant L305-342 |
| internal joints | none | — |
| upstream interface | seats on head top face; each element embeds into the one below | seed L301-324 |

### Slot D / return_mechanism (`_emit_return_coils`), emitted on each handle (present variant)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `return_spring` visual on `handle_0` and `handle_1` (helix + L-anchor wire) | return_spring variant L112-145, L463-472 |
| internal joints | none — coil is a host visual that swings with its handle (no new joint) | source note L463-472 |

### Slot E / grip_construction (`_emit_grip`), emitted on each handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grip_core` + `grip_overmold` + `grip_overmold_back` (overmold); or `ribbed_grip` (sleeve); or D-ring `grip_core` + distal pads | seed L357-370; sleeve L359-361; loop L189-197 |
| internal joints | none | — |

### Slot F / collection_bottle (`_emit_bottle`), emitted on `head`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottle_adapter` + `collection_bottle` | seed L327-338; large L346-348; angled L326-372 |
| internal joints | none — bottle is a static head visual | — |
| upstream interface | screws onto lower_housing bottom face (straight or diagonal stub) | seed L327; angled L326-354 |

### Slot G / spare_tip_multiplicity (`_emit_spare_tips`), emitted on `handle_0` only
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spare_tip_rack`/`spare_tip_magazine` + `spare_tip_{i}` (rack) / `tip_{i}` (magazine), i in range(N) | seed L381-400; magazine L418-451 |
| internal joints | none — fixed decorations seated in the holder | source note |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| handle_topology | enum | wide_v / long_straight / compact_short / cranked_offset | — | choice | procedural sampler | Slot A |
| head_form | enum | enclosed_cast / inline_steel_linkage / squared_cast / round_barrel | — | choice | procedural sampler | Slot B |
| nosepiece_form | enum | single_stack / long_mandrel_stem | — | choice | procedural sampler | Slot C |
| return_mechanism | enum | none_static / two_handle_return_coils | — | choice | procedural sampler | Slot D |
| grip_construction | enum | two_tone_overmold / single_ribbed_sleeve / closed_loop_ring | — | choice | procedural sampler | Slot E |
| collection_bottle | enum | compact_underslung / large_canister / angled_side_mount | — | choice | procedural sampler | Slot F |
| spare_tip_count | int | 3–8 | 3 | independent | weighted sample (small N common); loop-emit tip_{i} | Slot G / seed L387, magazine L418 |
| palette_style | enum | ≥6 colourways (see §8.5 ⑥) | red_cast | choice | `rng.choice(PALETTE_STYLES)` → `mats` dict | ⑥ pool (13 obs.) |
| arm_reach_scale | float | [0.92, 1.10] | 1.0 | independent | clamp; scales handle arm reach + grip position | ⑤ (seed handle dims) |
| head_scale | float | [0.94, 1.08] | 1.0 | independent | clamp; scales head cover/lower block size | ⑤ (seed head dims) |
| nose_scale | float | [0.92, 1.10] | 1.0 | independent | clamp; scales nose stack height | ⑤ (seed nose dims) |
| bottle_scale | float | [0.92, 1.12] | 1.0 | independent | clamp; scales bottle body height/radius | ⑤ (seed bottle dims) |
| squeeze_upper | float | derived | 0.35 | equation | `= clamp(safe_upper(handle_topology, grip_construction, arm_reach_scale), 0.14, 0.35)` — bounded so mirrored grips keep ≥ clearance from centerline | seed L409 + kinematics |
| (—) | constraint | — | — | inequality | at pose `squeeze_upper` the two handles' grip/loop inner faces stay ≥ 0.012 clear (verified by sampled-pose test; if violated, `squeeze_upper` retracts) | closed-pose clearance |

All `equation`/`inequality`/`conditional` relations are solved in `resolve_config`; `independent` scales are sampled then clamped. `squeeze_upper` is DERIVED (never a sweep-tuned constant): shorter/bulkier grip reach ⇒ smaller feasible upper.

### 7.5 编译预算 / compile budget（必填）
Per-seed budget: **≤20s/seed** (typical 6–14s). Basis: the seed compiles all 3 parts (~35 cadquery solids) in the library-typical 5–20s band; the heaviest module unions (knurled collar 24–32 ribs, threaded mandrel 17 crests, return-coil helix sweep, round-barrel revolve, magazine N sockets) are the cost drivers. Tessellation tiers: small hardware (screws, tips, ribs, threads) `tolerance≈0.0005`; hero faces (cover, lower block, barrel, bottle) `tolerance≈0.0007`; N identical spare tips reuse ONE `_spare_nose_tip`/hex helper mesh path (build once per index, no per-seed O(n²)). If a combo exceeds budget, coarsen rib/thread counts before iterating (AUTHORING §C).

## Multiplicity / Copy Logic

One multiplicity axis.

- `count_param`: `spare_tip_count` — the number of spare nose tips on the `handle_0` holder.
- `N_range`: product domain **3–8**; sampling domain weighted small-N-common (3–4 most frequent, 7–8 rare). Sweep upper 8.
- copied object: one machined nose tip (hex `spare_tip` in the rack family / `_spare_nose_tip` in the magazine family) — ONE shared geometry helper, built once per index and placed.
- naming: `spare_tip_{i}` (rack family) / `tip_{i}` (magazine family); holder `spare_tip_rack` / `spare_tip_magazine`.
- placement: evenly spaced along the holder beam/magazine block on `handle_0` (linear row for rack, indexed row for magazine).
- joint policy: fixed decorations seated in the holder (host visuals of `handle_0`), NOT separate joints (Rule 1).
- source/gating: seed rack N=3 (L387), magazine N=6 (L418-451). N is chosen independently of the holder family; both families accept any N in 3–8.
- secondary multiplicity: recessed head hex screws (`*_screw_*`) and `brand_mark_{0..2}` are loop-emitted host decorations (④), NOT a candidate-anchor N axis — fixed counts.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | handle_topology: wide_v(seed) / long_straight / compact_short / cranked_offset — all keep the fixed head + 2× revolute symmetric squeeze; `forked_anchor` (Slot A). Kinematic graph (head + 2 handles, 2 revolute edges) is fixed identity; topology varies the moving arm silhouette. |
| └ multiplicity | 同构件 ×N | 有 | spare_tip_count 3–8 (see §8); weighted small-N-common. |
| ② 关节类型 | 边换 type/轴 | 有 | 2× REVOLUTE symmetric squeeze (mimic pair), axis (0,∓1,0) — fixed identity; return_mechanism adds two per-handle return coils (host visuals that swing with the handle, no new joint) as a ② mechanism-presence axis; `forked_anchor` (Slots B-joint identity, D). Declared joint type REVOLUTE appears in every seed. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的几何形态原型 | 有 | **head_form registered ③ slot**: enclosed_cast (Planar Boundary Form) / inline_steel_linkage (Macro Surface Construction) / squared_cast (Volumetric Envelope Form) / round_barrel (Volumetric Envelope Form, lathe revolve). Plus nosepiece_form ③: single_stack (Volumetric Envelope) / long_mandrel_stem (Macro Surface Construction). All `forked_anchor`. |
| ④ 表面装饰 | 叠加表面细节 / 改装饰数 | 有 | grip_construction (two_tone_overmold / single_ribbed_sleeve / closed_loop_ring), collection_bottle (compact / large / angled), recessed hex screws, knurled-collar knurling, branded_plate + brand_mark, magazine index rings — host-conformal, non-structural; `record_only` + `forked_anchor`. Grips/bottle/rack derive from the host arm-end / lower-block faces. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | arm_reach_scale [0.92,1.10], head_scale [0.94,1.08], nose_scale [0.92,1.10], bottle_scale [0.92,1.12]; spare_tip_count 3–8. Motion envelope: `head_to_handle_0` REVOLUTE axis (0,−1,0), opens/closes about the head, `[closed 0, feasible upper = squeeze_upper ∈ 0.14..0.35 rad]`; `head_to_handle_1` mimics it (axis (0,1,0)). `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses` (both handles move via the mimic across {0, mid, upper}); targeted `ctx.pose({squeeze: squeeze_upper})` asserts both grips move inward (|x| decreases) and stay ≥0.012 clear of centerline; `ctx.pose({squeeze: 0})` asserts the open rest V. `record_only`. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类: painted/anodized metal + rubber + translucent plastic + machined steel. Colourways ≥6 from the 13-observed pool: red / black / orange / steel-silver / green / blue / yellow / teal / violet / off-white / copper-bronze / chrome / gunmetal. PALETTE_STYLES ships ≥6; `rng.choice`. 材质大类覆盖 ≥ ceil(0.5×档). `record_only`. |

收尾自检: at `template batch` 0-9, each head_form prototype, both nose forms, all 3 grips, all 3 bottles, both return states, N∈{small..large}, and ≥6 colourways must be visibly distinct with no closed/mid-pose 穿模.

## 采样与覆盖审计

总组合数：handle_topology(4) × head_form(4) × nosepiece_form(2) × return_mechanism(2) × grip_construction(3) × collection_bottle(3) × spare_tip N(3–8 ⇒ 6) = 4·4·2·2·3·3·6 = **6912** discrete slot-choice tuples (palette ⑥ and continuous ⑤ scales multiply further but are not counted). Well above the ≥300 maturity target; report-only.

理由: seven independent source-backed axes, all composable on the fixed 2-revolute squeeze spine.

seed_domain_policy：procedural_first (seed 0 not special).
Procedural Sampling / Sweep Plan: `config_from_seed(seed)` seeds a `random.Random(seed)`, samples each slot independently (weighted so the mature enclosed_cast/wide_v/two_tone/compact-bottle/single_stack baselines stay a plurality, and rarer forms still appear), samples `spare_tip_count` (small-N common), `palette_style` via `rng.choice`, and the continuous scales. `resolve_config` validates enums, clamps scales, derives `squeeze_upper` from the realized grip reach, and resolves the bottle/handle clearance guard. No small curated/modulo table. No regression overrides at authoring time (add only if a specific seed regresses, documented inline).
Topology target: 6912 tuples ≫ 300; N counted as raw (narrow 3–8). report-only.
Controlled local parameterization: arm_reach_scale, head_scale, nose_scale, bottle_scale, squeeze_upper (derived) — all clamped/derived in `resolve_config`; none breaks the fixed 2-revolute identity, the captured-pivot seating, or the head connectivity.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent weighted per-slot choice + weighted N + palette + clamped scales | `slot_choices_for_seed` matches build choices |
| compatibility matrix | all A–G composable; guards: squeeze_upper retracts for long/bulky grips so mirrored grips clear centerline; angled bottle stub stays clear of handles; all forms keep the pivot pockets + nose/bottle seats | no floating, no closed/mid-pose collision, correct axis, N≤8, no unsupported bulky module |
| controlled local variation | arm_reach_scale / head_scale / nose_scale / bottle_scale clamped; squeeze_upper derived | proportions vary without breaking captured pivot, head connectivity, joint origin, or category identity |
| regression overrides | none (add only for a documented regressing seed) | previously failed / reviewer-selected only |
| random sweep | seeds 0-15 (fast) → 0-35 (final) + corner stage; 0-999 maturity audit optional | contract failures; axis_realization slot_value_counts; viewer 0-9 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| handle_topology | 4 | yes | yes | ① skeleton |
| head_form | 4 | yes | yes | ③ Primary Form Family (registered) |
| nosepiece_form | 2 | yes | no | only 2 source-backed nose lengths (documented) |
| return_mechanism | 2 | yes | no | present/absent ② mechanism (documented) |
| grip_construction | 3 | yes | yes | ④ grip module |
| collection_bottle | 3 | yes | yes | ④ module |
| spare_tip_multiplicity | N=3–8 | yes | yes | multiplicity axis (rack/magazine holder) |

## Validator

- `slot_choices_for_seed` returns implemented module names for all 7 slots (+ N band).
- `config_from_seed` uses deterministic procedural sampling for every ordinary seed including seed 0.
- compatibility matrix / gating prevents illegal combos: `squeeze_upper` derived so mirrored grips never cross centerline; angled bottle clears handles; N clamped 3–8.
- optional regression overrides are sparse and justified (none at authoring).
- controlled local scales are clamped/derived in `resolve_config`; cannot break the captured pivot seating, head connectivity, joint origin, or the 2-revolute identity.
- the 2 squeeze REVOLUTE joints exist with correct axes (0,∓1,0), origins (±0.050,0,0.012), and `head_to_handle_1` is a mimic of `head_to_handle_0`; captured-pin joints omit `MatingContract` (grandfathered) and use element-scoped `allow_overlap`/`expect_overlap`.
- each part is one connected geometry island (head decorations embed into their host; handle grips/rack embed into the arm).
- copied spare tips follow `spare_tip_{i}`/`tip_{i}` naming + even holder placement.
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose(...)` on the squeeze.

## Reject cases

- A handle/head form that drops one of the 2 revolute squeeze joints, or makes `head_to_handle_1` non-mimic (breaks symmetric squeeze identity).
- A head_form that downgrades the round_barrel revolve or the polyline cover to a crude Box/Cylinder (Rule 3 primitive downgrade).
- Grips/return coils/bottle/rack floating off their host (disconnected island) — every visible element must embed/contact its host part.
- `squeeze_upper` frozen at 0.35 for a long/bulky-grip combo so the two mirrored grips collide mid/closed travel.
- Spare tips or magazine sockets floating above the holder (not seated) or N outside 3–8.
- angled_side_mount bottle stub colliding with a handle at any pose, or leaving the bottle unsupported.
- A monochrome palette (all materials one colour) — fails the ⑥ viewer coverage check.

## 与相邻类别的边界

- 不该混入: 电动/气动/电池 power rivet gun — powered actuation, no hand-lever squeeze; out of subcategory.
- 不该混入: bench/press-mounted riveter — not handheld; different support/root frame.
- 不该混入: generic pliers / crimper / wire-stripper — no mandrel-pull top nose stack + under-head catch bottle (the rivet-setter identity).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Authored from the 0611/rivet_squeeze1 source map + 14 synced 5-star records; structural twin of the reviewed `nutcracker` modular template (same 0611 3-part / 2-revolute parallel-children family). |

## 模板实现备注（可选）

- Shared helpers across modules: `_beam_between` (all arms/links/racks), `_hex_prism`, `_socket_screw`, `_knurled_collar` (short/tall), `_bottle` (parametric), `_revolved_barrel` (round head), `_return_spring`/`_handle_return_spring` (helix), `_d_ring_grip`, `_spare_nose_tip` — ported verbatim in primitive type from the source records (no Box/Cylinder downgrade).
- The 2 squeeze revolutes are captured-pin → OMIT `MatingContract` (AUTHORING Rule 2 exception), element-scoped `allow_overlap(head, handle, elem_a="red_head_body", elem_b="pivot_lug"/"pivot_cap")` + `expect_overlap` for seating; return-coil variant adds `allow_overlap(head, handle, elem_a="red_head_body", elem_b="return_spring")`.
- Connectivity: every head decoration (screws, brand marks, nose stack, bottle adapter, side panels/plates) embeds ≥0.5mm into its host face; grips/rack embed into the arm — build so each part is ONE island (compile-sweep promotes island WARN → FAIL).
- `squeeze_upper` derived helper is the single source for the squeeze range (Contract 3c/3e) — no second hand-written travel constant.
