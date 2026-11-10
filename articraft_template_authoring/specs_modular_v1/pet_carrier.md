# pet_carrier — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pet_carrier` |
| template path | `agent/templates/pet_carrier.py` |
| test path (optional) | `tests/agent/test_pet_carrier_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: one enclosing `carrier_body` root part carries the cabin (floor + walls + roof + vents as `.visual(...)`); every access panel and moving carry sub-assembly is a child that parents to the body (or, for `rear_topload_lid`, the upper shell is itself the moving lid child). One multiplicity axis copies the wire-grate door bars (`grate_bars` N).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 12 ids in the task list (2 origin anchors A/B + 10 forks/probe) |
| source_index_policy | only adopted module sources are indexed in the slot tables below |

Two source families:
- **Origin A / soft family** (`carrier_body` root Box floor+fabric walls + `section_loft` domed top with `boolean_difference` hatch cut + `tube_from_spline_points` handle loop; REVOLUTE `top_hatch` swing-up and REVOLUTE `front_door` fold-down; `expandable_side_pod` PRISMATIC; backpack harness visuals). Records: origin A, backpack, basket, expandable.
- **Origin B / rigid family** (`kennel_body` root `mesh_from_cadquery` lofted+shelled tapered tan shell + black tub + rim flange; REVOLUTE side-swing `wire_door` (loop-emitted `Cylinder` grate bars, N_VBARS/N_HBARS); molded `Box` handle; `top_shell_lid` rear-hinge REVOLUTE; `slide_out_tray` PRISMATIC; wheeled base + 4 CONTINUOUS casters + PRISMATIC trolley handle). Records: origin B, topload, slide_tray, rolling, wire_cage, grate_n4, grate_n9, probe_double_door.

## 核心身份

A **pet carrier** is a portable, fully-enclosing container that holds one small pet for travel: a defined cabin with ventilation, **at least one real openable access panel with a working joint** (door / hatch / lid / slide-tray / expandable pod), and **a carry means** (top handle, shoulder/backpack harness, or wheeled trolley). Default mature domain spans the soft fabric duffel (origin A), the rigid two-shell molded kennel (origin B), the open welded-wire travel crate, and the woven wicker basket — each with one access mechanism and one carry system.

Must NOT drift into (see §11): stationary animal cage / birdcage / aviary; rolling luggage / suitcase / utility cart / pet stroller; laundry basket / storage bin / cooler / toolbox; human backpack / sling / baby carrier.

## 槽位 + 候选模块表

### Slot A：body_form （③ 主体形态家族 — 主多样性槽，root part `carrier_body`）
The enclosing cabin shell to a standard envelope (same floor / front-face / roof-plane interface), differing in macro surface construction + primitive family.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `soft_fabric_envelope` | origin_anchor | rec_soft-sided-airline-pet-carrier-purple-fabric-rou_… | L105-L260 (Box floor+walls + `section_loft` dome + mesh windows) | eligible if compatible | boxy fabric walls + lofted domed mesh top; **Volumetric Envelope Form** (soft padded box+dome) |
| `rigid_molded_clamshell` | origin_anchor | rec_two-tone-hard-plastic-pet-travel-kennel-tan-uppe_… | L72-L239 (`mesh_from_cadquery` loft+shell tub & tapered shell + flange) | eligible if compatible | two-shell molded tapered clamshell + rim flange + latch clips + oval vents; **Macro Surface Construction** (revolved/lofted molded shell) |
| `open_wire_cage_lattice` | forked_anchor | rec_pet_carrier_var_wire_cage | L126-L248 (corner posts + rails + loop-emitted `Cylinder` grid bars + floor pan) | eligible if compatible | open welded-wire lattice frame (posts/rails/bars) + floor pan; **Planar Boundary Form** (open wire boundary, no solid skin) |
| `woven_wicker_basket` | forked_anchor | rec_pet_carrier_var_basket | L103-L297 (`section_loft` woven shell+dome + `tube_from_spline_points` weave bands/stakes/rim) | eligible if compatible | woven rounded-rect basket + horizontal bands + vertical stakes + woven dome; **Macro Surface Construction** (woven tube-course surface) |

Six-axis note: this is the required **③ Primary Form Family slot registered into `slot_choices`** (form-dominated 小类). 4 recognizable prototypes covering Volumetric Envelope (soft), Macro Surface Construction (rigid molded, woven), Planar Boundary (wire lattice). ≥3 satisfied.

### Slot B：access （② 关节类型 / ① 骨架 — one openable access child）
Exactly one access mechanism per seed; the guaranteed non-FIXED joint(s).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `front_fold_door` | origin_anchor | origin A | L307-L348 (`front_door` panel + `body_to_front_door`) | soft / basket | mesh/panel door REVOLUTE bottom-hinge axis +Y, folds down-out (+X) over the front opening |
| `top_hatch` | origin_anchor | origin A | L262-L305 (`top_hatch` + `body_to_top_hatch`) | soft / basket | lid REVOLUTE rear-hinge axis −Y, swings up over the top opening |
| `expandable_side_pod` | forked_anchor | rec_pet_carrier_var_expandable | L369-L467 (`expandable_side_pod` + `body_to_side_pod` PRISMATIC +Y) | soft | fabric side pod PRISMATIC +Y expands the cabin; body left wall becomes the pod |
| `side_swing_door` | origin_anchor | origin B | L245-L313 (`wire_door` grate + `body_to_door`) | rigid / wire | wire-grate door REVOLUTE vertical axis +Z, side-hinge, swings out front; **multiplicity `grate_bars` N** |
| `rear_topload_lid` | forked_anchor | rec_pet_carrier_var_topload | L179-L243 (`top_shell_lid` + `body_to_top_lid`) | rigid | the whole upper shell IS the lid: REVOLUTE rear-hinge axis −Y lifts up |
| `slide_out_tray` | forked_anchor | rec_pet_carrier_var_slide_tray | L404-L424 (`slide_out_tray` + `body_to_tray` PRISMATIC +X) | rigid / wire | floor cleaning tray PRISMATIC +X slides out the front-bottom on rails |

### Slot C：carry （① 骨架 / ② 关节 — one carry system）
Exactly one carry means per seed.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `webbing_top_handle` | origin_anchor | origin A | L237-L252 (`carry_handle_loop` `tube_from_spline_points` arch) | soft / basket | arched webbing/cane handle loop (mesh tube) on the roof — host `.visual(...)` |
| `backpack_harness` | forked_anchor | rec_pet_carrier_var_backpack | L341-L415 (back panel + 2 straps + sternum clip + grab handle) | soft | semi-rigid back panel + mirrored shoulder straps + sternum clip + top grab handle — host `.visual(...)` on the rear wall |
| `molded_rigid_handle` | origin_anchor | origin B | L219-L239 (base plate + 2 risers + grip bar) | rigid / wire | molded Box handle (base/risers/grip) on the roof host — `.visual(...)` |
| `wheeled_rolling_trolley` | forked_anchor | rec_pet_carrier_var_rolling | L233-L551 (base platform + 4 caster CONTINUOUS + PRISMATIC trolley) | rigid / wire | raised cabin on a wheel base (platform+forks host visuals) + 4 `caster_wheel_i` CONTINUOUS + `trolley_handle` PRISMATIC +Z |

Every candidate is structurally distinct (part tree / joint topology / primitive family), not a re-skin. No single-candidate slot (each slot has 4 / 6 / 4 candidates). Palette / mesh-window decoration are NOT candidates (④/⑥ audit-only, ride via palette).

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                       carrier_body (root: floor + walls + roof + vents/windows as .visual)
  ├─[REVOLUTE +Y  @front-opening bottom edge]──> front_door        (access=front_fold_door)
  ├─[REVOLUTE −Y  @top-opening rear edge]──────> top_hatch         (access=top_hatch)
  ├─[PRISMATIC +Y @body left wall face]────────> expandable_side_pod (access=expandable_side_pod)
  ├─[REVOLUTE +Z  @front +Y jamb]──────────────> wire_door         (access=side_swing_door; ×N grate bars)
  ├─[REVOLUTE −Y  @rear roof rim]──────────────> top_shell_lid     (access=rear_topload_lid; lid = upper shell)
  ├─[PRISMATIC +X @tub front-bottom slot]──────> slide_out_tray    (access=slide_out_tray)
  ├─[CONTINUOUS +X @4 caster forks]────────────> caster_wheel_{0..3} (carry=wheeled_rolling_trolley)
  └─[PRISMATIC +Z @rear wall]──────────────────> trolley_handle    (carry=wheeled_rolling_trolley)
```

- Slot order (resolve): body_form → access → carry. `carry=wheeled_rolling_trolley` sets `ground_clearance>0` so the body floor lifts and the casters fill the gap (single-sourced in `resolve_config`). `access=expandable_side_pod` omits the body left wall. `access=rear_topload_lid` builds the upper shell as the moving lid child (body root = tub only); the carry roof handle then rides on the lid part.
- Cross-slot connection points: every child parents to `carrier_body`; joint origins sit on real body hardware (front-opening sill, top-opening rear edge, left wall face, front jamb, rear roof rim, tub front slot, caster forks, rear wall).
- Every non-FIXED joint is a **captured hinge-knuckle / captured rail / captured axle** pivot (the sources model door hinges as knuckle-around-pin, trays on molded rails, casters on axle pins). `MatingContract` cannot express two non-axis-aligned captured faces, so joints are **grandfathered** (omit `mating=`) and kept honest with element-scoped `allow_overlap` + `expect_overlap`/targeted `ctx.pose` mirroring each source's `run_tests` (identical discipline to `camp_chair`). **No FIXED articulation exists** — every child is a real moving joint; non-articulating detail is a host `.visual(...)` (Rule 1).
- Mutual exclusion / gating: access & carry are gated by body_form (§9 matrix); `grate_bars` N only applies to `side_swing_door`.

## 每槽位 Module Emits / Interfaces

### Slot A / body_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carrier_body` root (all cabin geometry as `.visual(...)`) | A L105-260 / B L163-239 / wire L129-248 / basket L196-315 |
| internal joints | none | — |
| upstream interface | root — provides standard anchors: `floor_z`, `front_face_x`, front-opening rect, top-opening rect, `roof_z`, left-wall face (single-sourced in resolved config) | — |
| downstream interface | body faces consumed by access + carry joint origins | — |

### Slot B / access
| emits | 描述 | 来源 |
|---|---|---|
| parts | one of `front_door` / `top_hatch` / `expandable_side_pod` / `wire_door` (+ N grate bars) / `top_shell_lid` / `slide_out_tray` | see slot table |
| internal joints | one REVOLUTE or PRISMATIC to `carrier_body` | A L295/L338 / expandable L458 / B L303 / topload L233 / tray L414 |
| upstream interface | parents to `carrier_body`; origin on body opening hardware | — |
| downstream interface | moving panel (carries its own trim/grate/window visuals; nothing chains below) | — |

### Slot C / carry
| emits | 描述 | 来源 |
|---|---|---|
| parts | `webbing_top_handle`/`molded_rigid_handle`/`backpack_harness` → host `.visual(...)` (no new part); `wheeled_rolling_trolley` → base visuals on body + `caster_wheel_{0..3}` CONTINUOUS + `trolley_handle` PRISMATIC | A L237-252 / B L219-239 / backpack L341-415 / rolling L233-551 |
| internal joints | rolling: 4× CONTINUOUS caster spin (+X) + 1× PRISMATIC trolley (+Z); others none | rolling L310/L541 |
| upstream interface | parents to `carrier_body`; caster/trolley origins on body base/rear hardware | — |
| downstream interface | none | — |

不动细节（mesh windows, oval vent rows, weave bands/stakes, latch clips, piping, logo patches, handle loop, back panel, straps）都是宿主 part `.visual(...)`，不是 FIXED-jointed part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | 4 modules (Slot A) | soft_fabric_envelope | choice | procedural sampler | Slot A table |
| `access` | enum | 6 modules (Slot B) | front_fold_door | conditional | sampled from `ALLOWED_ACCESS[body_form]` | Slot B table |
| `carry` | enum | 4 modules (Slot C) | webbing_top_handle | conditional | sampled from `ALLOWED_CARRY[body_form]` | Slot C table |
| `grate_bars` | int (mult.) | N∈{4,6,9} | 6 | conditional | only if `access==side_swing_door`, else 0; weighted mid≫coarse/dense | wire grate B / grate_n4 / grate_n9 |
| `palette_style` | enum | 5 colorways (see §8.5 ⑥) | purple_mesh / tan_black / … | choice | rng.choice(PALETTE_STYLES) | origins + companion forks |
| `size_scale` | float | [0.92, 1.12] | 1.0 | independent | uniform then clamp | proportion ⑤ |
| `width_scale` | float | [0.90, 1.10] | 1.0 | independent | uniform then clamp (cabin Y) | proportion ⑤ |
| `ground_clearance` | float | derived {0.0 or ≈0.085} | 0.0 | equation | `= 0.086·size_scale if carry==wheeled_rolling_trolley else 0.0` | rolling L73 |
| (—) | constraint | — | — | conditional | access/carry allowed-sets resolved from body_form before sampling | §9 matrix |
| (—) | constraint | — | — | inequality | door_top_z ≤ rim_z−0.005 and sill_z ≥ floor_z+0.02 so the front opening fits the wall; violated → clamp door rect | opening fit |

所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解；builder 不再失败。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤35 s/seed**（典型 8–25 s；`rigid_molded_clamshell` 的 cadquery loft+shell+vent boolean 是重项）。依据：库内参考重布尔雕刻 30–60 s，本类只有一个 form 用 cadquery，其余是 `Box`/`Cylinder`/`section_loft`/`tube_from_spline_points` mesh。分档 tessellation：小半径 wire/tube 特征 `radial_segments ≤ 12`；`section_loft` 主体英雄面用源档；rigid vent boolean 行数收敛到 ≤2 行以控布尔耗时；N 个相同 grate 杆 / caster 复用同一构造 helper。sweep `--compile-timeout 120` 作看门狗（≈3× 上限）。超预算先降精度再迭代。

## Multiplicity / Copy Logic

**Axis 1 — `grate_bars` (wire-grate door bar count), sources rec_pet_carrier_var_grate_n4 / origin B / grate_n9.**
- `count_param` = `grate_bars` N (vertical bars); horizontal bars derived `≈ round(N/2)`. Product/test domain N∈{4,6,9} (coarse / origin / dense). sampling domain: weighted mid (6) high, coarse/dense rarer.
- copied object = `door_wire_vertical_{i}` / `door_wire_horizontal_{i}` `Cylinder` bars on the `wire_door` part, even-spaced between the heavy border wires (loop-emitted, shared helper, stable indexed names).
- placement/joint policy: FIXED decoration visuals on the moving `wire_door` part (they ride with the door revolute). gating: only when `access==side_swing_door`; otherwise the axis is absent (`grate_bars=0`, reported as `n0`).

Secondary counts are record-only / fixed (not swept): caster wheels = 4 (fixed corner grid), oval vent rows, latch clips, weave bands/stakes, backpack straps = 2 (mirrored pair).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | access adds a distinct moving child (door / hatch / pod / grate-door / lid / tray) and carry adds 0 or {4 casters + trolley}; body_form swaps the whole root part-tree construction (fabric box+dome / molded clamshell / wire lattice / woven basket). source-backed: origins A/B + wire_cage / basket / rolling forks. |
| └ multiplicity | 同构件 ×N | 有 | `grate_bars` N∈{4,6,9} loop-emitted grate bars on `wire_door` (source grate_n4 / B / grate_n9); gated to `side_swing_door`. §8. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE +Y (front fold-down), REVOLUTE −Y (top hatch / rear lid), REVOLUTE +Z (side swing), PRISMATIC +Y (pod), PRISMATIC +X (tray), PRISMATIC +Z (trolley), CONTINUOUS +X (casters). All source-backed. Every declared type appears in sweep (soft→rev/prismatic pod; rigid→rev/prismatic tray/lid; rolling→continuous+prismatic). |
| ③ 主体形态家族 | 换核心几何原型 | 有 | 4 prototypes (Slot A): soft fabric box+dome (Volumetric Envelope), rigid molded clamshell (Macro Surface Construction), open wire lattice (Planar Boundary), woven basket (Macro Surface Construction). source-backed; registered in `slot_choices`. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only + world_knowledge_extrapolation) | mesh vent windows + oval vent-hole rows + wire-grate pattern + woven bands/stakes + piping + logo/brand patches. Host-conformal: each is a host `.visual(...)` placed on the wall/dome/roof face it sits on, following ③/⑤ (derive order ③→⑤→④). Decoration count/tone rides `palette_style`. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | size_scale [0.92,1.12], width_scale [0.90,1.10]; ground_clearance derived. **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): front_door REVOLUTE +Y [0,1.5] (fold down/out); top_hatch REVOLUTE −Y [0,2.2] (up); side_swing_door REVOLUTE +Z [0,1.5] (out); rear_topload_lid REVOLUTE −Y [0,1.8] (up); expandable_pod PRISMATIC +Y [0,0.12] (out); slide_tray PRISMATIC +X [0,0.17] (out); trolley PRISMATIC +Z [0,0.24] (up); caster CONTINUOUS +X full spin. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + one targeted `ctx.pose(...)` per mechanism (door folds outward; hatch/lid rises; pod/tray translates; trolley rises; caster is axisymmetric). Intentional closed-pose seating overlap declared element-scoped `allow_overlap`. No sampled-pose exemption needed. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes fabric + molded-plastic + metal-wire + woven-rattan + mesh; ≥5 colorways: purple_mesh_soft (A), tan_black_kennel (B), chrome_black_wire (wire_cage), natural_rattan (basket), grey_navy_travel (companion). Material-class coverage ≥ ceil(0.5×5)=3 (every seed shows ≥3 of fabric/plastic/metal/mesh). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——4 个 form 拉得开、fabric/molded/wire/woven 材质都出现、mesh 窗/vent/weave 贴合宿主面不悬空、door/hatch/lid/tray/pod/trolley/caster 关节全程不穿模、carrier 读作可携带（有 handle/harness/wheels）。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- soft: access{front_fold_door, top_hatch, expandable_side_pod}(3) × carry{webbing_top_handle, backpack_harness}(2) = 6
- basket: access{top_hatch, front_fold_door}(2) × carry{webbing_top_handle}(1) = 2
- rigid: access{side_swing_door, rear_topload_lid, slide_out_tray}(3) × carry{molded_rigid_handle, wheeled_rolling_trolley}(2) = 6 (side_swing ×3 grate N)
- wire: access{side_swing_door, slide_out_tray}(2) × carry{molded_rigid_handle, wheeled_rolling_trolley}(2) = 4 (side_swing ×3 grate N)
- ≈ (6+2+6+4) = **18 (body,access,carry) tuples**, × grate N{4,6,9} on the 2 side_swing bodies, × 5 palette × continuous scales.

理由：多样性主要来自离散 body_form(③) + access(②/①) + carry(①/②) + grate_bars(mult) 槽；连续 scale 仅 clamp/derive，不撑多样性。Compatibility 收紧了组合空间（每个 form 只挂物理上合理的 access/carry），因此 1000-seed slot-tuple 覆盖 < 300 — 属真实组合上限（honest structural vocabulary，coverage-first，无 padding），report-only 非 gate。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；`body_form`=rng.choice(BODY_FORMS)；`access`=rng.choice(ALLOWED_ACCESS[body_form])；`carry`=rng.choice(ALLOWED_CARRY[body_form])；`grate_bars`=weighted rng.choice({4,6,9}) if side_swing else 0；`palette_style`=rng.choice；`size_scale`/`width_scale` uniform then clamp in `resolve_config`；`ground_clearance` derived. Compatibility matrix = ALLOWED_ACCESS + ALLOWED_CARRY dicts, so every sampled tuple is legal by construction (no rejection loop). No regression overrides (procedural covers seed 0).
Topology target：真实组合上限 ~18 tuples（×N×palette）；< 300 由紧兼容矩阵解释（report-only, 不作 gate，也不反推上游变体数量）。
Controlled local parameterization：size_scale, width_scale (continuous), clamped in `resolve_config`; ground_clearance derived from carry; they never break the opening-fit inequality, the joint origins (derived from envelope), or the captured-pivot allowances.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form, body-gated access, body-gated carry, gated grate N, palette, scales | slot_choices_for_seed matches build choices |
| compatibility matrix | ALLOWED_ACCESS[body] + ALLOWED_CARRY[body]; grate N only for side_swing; fallback → first legal candidate | no floating, collision, axis, closed-pose, bulky-module failures |
| controlled local variation | size_scale/width_scale clamped; ground_clearance derived | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | ③ primary form slot |
| access | 6 | yes | yes | ② (body-gated) |
| carry | 4 | yes | yes | ①/② (body-gated) |
| grate_bars (mult) | N∈{4,6,9} | yes | — | source grate_n4/B/grate_n9 |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (body_form, access, carry, grate_bars)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix (ALLOWED_ACCESS + ALLOWED_CARRY) prevents illegal combos in `config_from_seed`/`resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped in `resolve_config`; ground_clearance derived; opening rect kept inside the wall
- every non-FIXED joint is a captured pivot/rail/axle with element-scoped `allow_overlap` + targeted `ctx.pose`; no MatingContract phantom anchors; no FIXED-jointed decoration parts
- key joints have expected type/axis/range (front +Y REVOLUTE; hatch/lid −Y REVOLUTE; side +Z REVOLUTE; pod/tray/trolley PRISMATIC; caster CONTINUOUS +X)
- copied grate bars follow `door_wire_vertical_{i}` / `door_wire_horizontal_{i}` naming + even spacing
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per mechanism

## Reject cases
- A body_form whose access panel floats off the opening (isolated island) or leaves a mating gap.
- A door/lid/tray whose open pose drives through the cabin or a neighbor (穿模) at sampled poses.
- Access or caster/trolley joint origin off real body hardware (>15mm) → articulation-origin fail.
- `expandable_side_pod` that doesn't translate its cabin width, or a `slide_out_tray` that stays inside (dead joint).
- `wheeled_rolling_trolley` whose casters float above ground or whose cabin isn't lifted by `ground_clearance`.
- Carrier with no carry means, or a non-portable stationary cage read (category drift).
- Downgrading `section_loft` / `mesh_from_cadquery` / `tube_from_spline_points` heroes to flat `Box` (Rule 3).
- Monochrome output (palette_style not driving `.visual(material=...)`).

## 与相邻类别的边界
- 不该混入：stationary animal cage / birdcage / aviary（无携带手段、固定不可搬 — 每个 seed 必带 handle/harness/wheels）。
- 不该混入：rolling luggage / suitcase / utility cart / pet stroller（`wheeled_rolling_trolley` 保留 enclosed 宠物 cabin + 通风 + 真实宠物门，非人用行李）。
- 不该混入：laundry basket / storage bin / cooler / toolbox（`woven_wicker_basket` 保留 domed 宠物 lid + carry handle + 通风）。
- 不该混入：human backpack / sling / baby carrier（`backpack_harness` 保留 enclosed 宠物 cabin + mesh vents + 真实宠物门）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | soft (section_loft) + rigid (cadquery) + wire (cylinders) + basket (woven tubes) form spine; every child a captured-pivot moving joint (grandfathered like camp_chair); one grate-bar multiplicity axis. Tight body→access/carry compatibility keeps combos physically honest (topology target < 300 explained). |

## 模板实现备注（可选）
- Shared helpers: `_rect_loop`/`_build_dome` (origin A section_loft) reused by soft+basket; `_upper_shell_solid`/`_tub_solid` cadquery (origin B) for rigid + rear lid; `_bar` cylinder helper + grate helper reused by wire cage + side_swing_door; `_caster`/`_trolley` for rolling.
- Envelope anchors (`floor_z`, `front_face_x`, front/top-opening rects, `roof_z`, left-wall face) single-sourced in `ResolvedPetCarrierConfig` so access/carry joint origins and body openings never drift (Contract 3c).
- Captured-pivot element-scoped `allow_overlap`: door knuckle↔jamb; lid flange↔tub flange + latch clips; tray↔rails; pod gussets↔cabin (stowed); caster axle↔wheel bore; trolley riser↔roof. Mirror each source's `run_tests`.
- Access-dependent body: `rear_topload_lid` builds the upper shell as the lid (body root = tub); `expandable_side_pod` omits the body left wall. Carry-dependent: `wheeled_rolling_trolley` sets `ground_clearance`.
