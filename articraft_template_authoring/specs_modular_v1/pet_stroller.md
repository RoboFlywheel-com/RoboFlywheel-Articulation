# pet_stroller — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pet_stroller` |
| template path | `agent/templates/pet_stroller.py` |
| test path (optional) | `tests/agent/test_pet_stroller_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: a single `frame` root carries every fixed chassis/undercarriage `.visual(...)`;
each subsystem (wheels + caster yokes, cabin body / carrier pod, fold-open canopy/dome + optional
front door, push handle) is a parallel child of the frame. Wheel-count (N∈{3,4}) is a multiplicity
axis folded into the chassis slot's candidate topology.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 9 ids (2 origin anchors A/B + 7 verified-PASS forks) |
| source_index_policy | only adopted module sources are indexed in the slot tables below |

Coordinate convention adopted = **origin A frame**: X = left/right (width), +Y = front / −Y = rear,
Z = up. Origin-B (and B-family forks) use X = forward; their structure (2 rear + 1 front jogger,
swing-bar handle, reversible handle) is re-expressed in A's frame (Rule 3 adaptation: part tree /
joint semantics / primitive family preserved, coordinates re-authored).

Source families:
- **Origin A** `rec_pet_animal_related__pet_stroller__001…` — 4-wheel champagne tubular frame, black
  fabric cabin (`basket_floor`/`side_wall_0/1`/`front_lip`/`rear_panel` + perforated mesh windows +
  `top_rim`/`side_rail` tubes + lower `storage_base` + `front_fork`/`front_spring`/fender), REVOLUTE
  `canopy_hinge`, REVOLUTE `handle_hinge` (U-tube), 4× CONTINUOUS `*_wheel_spin`. Helpers `_add_wheel`
  / `_tube` / `_canopy_shell_from_side_path`.
- **Origin B** `rec_pet_animal_related__pet_stroller__002…` — navy 3-wheel jogger, single front wheel
  on a fork, 2 rear wheels (Mimic-linked), swing-bar REVOLUTE handle, bezier fabric+mesh canopy.
  Helpers `_add_tube` / `_curved_fabric_panel` / `_bezier`.

## 核心身份

A **pet stroller** is a wheeled, human-pushed carriage whose main body is a fabric or rigid pet
cabin/bassinet mounted on a rolling frame, with a push handle gripped from behind, a folding/opening
canopy or top for pet access, rolling on ≥3 ground wheels each on a real CONTINUOUS spin joint. Every
seed keeps: an enclosed/semi-enclosed pet cabin on the rolling frame, a rear push handle (non-fixed
articulation), a fold-open canopy/top (non-fixed articulation), and ≥3 spinning ground wheels.

Must NOT drift into (see §11): standalone Pet carrier (no wheeled push frame), baby/child stroller
(5-point-harness infant seat, reclining backrest), dog crate / bird cage (static, no push frame),
pet wagon / hand-truck / open flatbed cart, floor playpen (no wheels).

## 槽位 + 候选模块表

### Slot A：chassis （① 骨架 / ② 前轮机构 / N 轮数 multiplicity）
Rolling base: wheel count + front-wheel mechanism. Wheels (and caster yokes) are parallel children of
`frame`; the slot also emits its frame-side mounting hardware (axle tubes/stubs, forks, sockets).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `four_wheel_fixed` | forked_anchor(origin) | A | model.py:L322-L371 (4 wheels + 4 CONTINUOUS spins, fixed front fork) | eligible if compatible | 2 large rear + 2 small front wheels, all spin directly on frame; N=4 |
| `four_wheel_swivel` | forked_anchor | rec_pet_stroller_var_mechanism_swivel_caster (from A) | model.py:L203-L251,L446-L476 (`_add_caster_yoke`; front_caster_swivel CONTINUOUS +Z + wheel spin child of yoke) | eligible if compatible | 2 rear (spin) + 2 front on swivel **caster_yoke** parts (yoke CONTINUOUS +Z, wheel CONTINUOUS child of yoke); N=4 + 2 yokes |
| `three_wheel_jogger` | forked_anchor(origin) | B | model.py:L466-L514 (2 rear Mimic + 1 front on fork, CONTINUOUS) | eligible if compatible | 2 large rear + 1 single centered front wheel on a fork; N=3 |

### Slot B：cabin_form （③ 主体形态家族 / Primary Form Family — 登记进 slot_choices）
Lower pet compartment body.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `soft_fabric_cabin` | forked_anchor(origin) | A, B | A model.py:L221-L248 (basket_floor + 4 fabric walls + perforated side/front mesh windows) | eligible if compatible | sewn fabric floor + side/front/rear panels + perforated mesh windows on `frame`; **Planar Boundary Form** (thin sewn panels) |
| `rigid_carrier_pod` | forked_anchor | rec_pet_stroller_var_form_rigid_carrier (from A) | model.py:L298-L375 (hollow rounded-rect tub + vent grilles + saddle brackets/clips) | eligible if compatible | rigid hollow rounded-rect molded tub (`ExtrudeWithHolesGeometry` wall ring + floor, **Mesh**) as a FIXED `pod` part, seated in frame saddle cradle + vent grilles; **Volumetric Envelope Form** |

Six-axis note: this is the required **③ Primary Form Family slot registered into `slot_choices`**. Two
source-backed prototypes (Planar Boundary sewn cabin vs Volumetric Envelope molded shell). A **third**
③ reading — a fully enclosed continuous-envelope pod — is realized by `enclosed_mesh_dome` in Slot C
(the top+body together read as an escape-proof enclosed dome). Reason for 2 candidates in this slot:
honest pet-stroller cabin bodies converge to sewn-fabric vs rigid-shell (the upstream source pool's
only two distinct lower-body constructions); the enclosure-degree ③ variation lives in Slot C. ≥2 with
documented reason (§4 硬约束 allowed path).

### Slot C：top_access （② 关节机构 / ③ 顶部包络）
The fold-open top. Always emits one REVOLUTE `canopy`; two candidates change its form/enclosure and one
adds a second REVOLUTE `front_door`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `fold_back_canopy` | forked_anchor(origin) | A, B | A model.py:L290-L300,L339-L347 (`_canopy_shell_from_side_path` fabric + ribs; `canopy_hinge` REVOLUTE X) | eligible (all forms) | arched fabric canopy, REVOLUTE X [−0.20,0.90] |
| `enclosed_mesh_dome` | forked_anchor | rec_pet_stroller_var_form_enclosed_dome (from B) | model.py:L442-L507 (`_dome_side_wall`/`_dome_front_wall` mesh dome wrapping to cabin rim; canopy REVOLUTE widened) | eligible: soft_fabric_cabin only | full mesh **dome** canopy (roof + side walls + front wall) enclosing the cabin, REVOLUTE X [0.0,1.20]; ③ Volumetric-Envelope enclosure |
| `front_door_canopy` | forked_anchor | rec_pet_stroller_var_mechanism_front_door (from A) | model.py:L321-L332,L369-L377 (`front_door` part + `front_door_hinge` REVOLUTE −X drop) | eligible: soft_fabric_cabin only | arched canopy **+** additional drop-down front `front_door` part, REVOLUTE −X [0.0,1.30] |

### Slot D：push_handle （② 关节类型）
Rear push handle, parallel child of `frame`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `u_fold_handle` | forked_anchor(origin) | A | model.py:L303-L320,L348-L356 (U-tube + grip; `handle_hinge` REVOLUTE X) | eligible if compatible | U-shape fold handle, REVOLUTE X [0.0,0.95] |
| `swing_bar_handle` | forked_anchor(origin) | B | model.py:L334-L365 (two side arms + foam grip; `base_to_handle` REVOLUTE Y) | eligible if compatible | swing-bar fold handle (2 arms + grip), REVOLUTE Y [−0.65,0.35] |
| `telescoping_handle` | forked_anchor | rec_pet_stroller_var_mechanism_telescoping_handle (from A) | model.py:L279-L285,L313-L353,L383-L391 (2 fixed outer sleeves on frame; handle U-tube slides; `handle_slide` PRISMATIC) | eligible if compatible | telescoping height-adjust handle, PRISMATIC along rear-upright axis [0.0,0.18] |
| `reversible_handle` | forked_anchor | rec_pet_stroller_var_mechanism_reversible_handle (from B) | model.py:L324-L393 (high transverse pivot bar + long arms + detent bosses; `base_to_handle` REVOLUTE Y wide) | eligible if compatible | reversible swing-over handle, REVOLUTE Y wide [−1.4,1.4] over the canopy |

Every candidate in every slot is structurally distinct (part tree / joint topology / primitive family),
not a re-skin. No single-candidate slot. Lower mesh storage basket, cup-holder, badges, tire tread type
and fabric colorway are ④/⑤/⑥ audit-only (record_only), NOT candidates.

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                       frame (root: champagne tubular chassis + lower storage basket + undercarriage
                              + axle/hinge hardware; carries every fixed .visual(...))
   Slot A chassis:
   ├─[CONTINUOUS X @rear axle y=-0.565 z=r_rear]────> rear_wheel_{0,1}        (all candidates)
   ├─[CONTINUOUS X @front axle y=0.630 z=r_front]───> front_wheel_{0,1}       (four_wheel_fixed)
   ├─[CONTINUOUS +Z @front socket] > caster_yoke_{0,1} ─[CONTINUOUS X]─> front_wheel_{0,1}  (four_wheel_swivel)
   └─[CONTINUOUS X @front fork y=0.630 x=0]─────────> front_wheel_0           (three_wheel_jogger, N=3)
   Slot B cabin_form:
   ├─ soft_fabric_cabin: fabric floor/walls/mesh as frame .visual(...)        (no child part)
   └─[FIXED @saddle cradle z=0.435] ────────────────> pod                     (rigid_carrier_pod)
   Slot C top_access:
   ├─[REVOLUTE X @canopy hinge y=-0.50 z=0.735]─────> canopy                  (all)
   └─[REVOLUTE -X @front hinge y=0.44 z=0.44]───────> front_door              (front_door_canopy only)
   Slot D push_handle:
   └─[REVOLUTE X | REVOLUTE Y | PRISMATIC @rear hinge y=-0.82 z=0.72]─> handle (one per candidate)
```

- Slot resolve order: chassis → cabin_form → top_access → handle. All children parent to `frame`
  (parallel); the caster front wheels parent to their `caster_yoke` (a 2-link serial sub-chain inside
  the chassis slot). Joint origins sit on real frame hardware (axle stubs/tubes, forks/sockets, canopy
  hinge pins/brackets, handle hinge brackets, front hinge bar) — every jointed child has an anchoring
  visual (Rule 2).
- Every non-FIXED joint is a captured pin-through-sleeve / turntable / prismatic-sleeve pivot:
  `MatingContract` cannot express two axis-aligned faces, so joints are **grandfathered** (omit
  `mating=`) with element-scoped `allow_overlap` + `expect_overlap` mirroring each source's `run_tests`.
  The single FIXED joint (`frame_to_pod`) uses a real saddle-cradle contact (Rule 1: the pod is a rigid
  sub-assembly needing its own reference frame; documented).
- Compatibility / gating (§9): `enclosed_mesh_dome` and `front_door_canopy` require
  `cabin_form=soft_fabric_cabin` (both forks are on soft-fabric single-tier bases; a dome/drop-door on a
  rigid closed tub is not source-faithful). All other combinations legal. Fallback: illegal top_access on
  a rigid pod → `fold_back_canopy`.

## 每槽位 Module Emits / Interfaces

### Slot A / chassis
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_wheel_{0,1}`, `front_wheel_{0,1}` (or single `front_wheel_0`), + `caster_yoke_{0,1}` (swivel) | A L322-371 / swivel L404-411 / B L466-514 |
| internal joints | 2–4 CONTINUOUS wheel spins (axis X) + 2 CONTINUOUS caster swivels (axis +Z, swivel only) | A L357-371 / swivel L446-476 |
| upstream interface | wheels/yokes parent to `frame`; joint origins on frame axle stubs/tubes, forks, caster sockets (frame `.visual`) | A L264-288 |
| downstream interface | none (leaf children) | — |

### Slot B / cabin_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (soft: frame visuals) / `pod` (rigid, FIXED) | A L221-248 / rigid L303-375 |
| internal joints | none (soft) / `frame_to_pod` FIXED (rigid) | rigid L414-420 |
| upstream interface | soft: frame `.visual(...)`; rigid: `pod` seated on frame saddle brackets `pod_saddle_{i}` at z≈0.435 | rigid L226-229 |
| downstream interface | cabin rim (informational) for canopy/door seating | — |

### Slot C / top_access
| emits | 描述 | 来源 |
|---|---|---|
| parts | `canopy` (always) + optional `front_door` | A L290-300 / dome L442-497 / door L322-332 |
| internal joints | `canopy_hinge` REVOLUTE X (always) + optional `front_door_hinge` REVOLUTE −X | A L339-347 / door L369-377 |
| upstream interface | parents to `frame`; hinge origin on frame `canopy_hinge_bracket/pin` (and `front_hinge_bar` for door) | A L286-288 / door L226 |
| downstream interface | moving top (carries its own fabric/mesh/rib visuals; nothing chains below) | — |

### Slot D / push_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle` | A L303-320 |
| internal joints | one of: `handle_hinge` REVOLUTE X / `base_to_handle` REVOLUTE Y / `handle_slide` PRISMATIC | A/B/tele/rev |
| upstream interface | parents to `frame`; hinge/slide origin on frame `handle_hinge_bracket` / `telescope_sleeve` / `handle_pivot_bar` | A L274 / tele L279-285 / rev L327-356 |
| downstream interface | moving handle (carries grip/collar visuals; nothing chains below) | — |

不动细节（lower storage basket, cup-holder ring, mesh windows, stitched trim, front spring, fenders,
badges, top_rim/side_rail tubes）都是宿主 part 的 `.visual(...)`，不是 FIXED-jointed part（Rule 1）。
唯一的 FIXED articulation 是 `frame_to_pod`（rigid carrier is a molded sub-assembly needing its own
reference frame; anchored on real saddle-cradle contact, documented Rule 1 exception）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `chassis` | enum | 3 modules (Slot A) | four_wheel_fixed | choice | procedural sampler | Slot A table |
| `cabin_form` | enum | 2 modules (Slot B, ③) | soft_fabric_cabin | choice | procedural sampler | Slot B table |
| `top_access` | enum | 3 modules (Slot C) | fold_back_canopy | conditional | gated by cabin_form (rigid → fold_back_canopy) | Slot C table |
| `push_handle` | enum | 4 modules (Slot D) | u_fold_handle | choice | procedural sampler | Slot D table |
| `wheel_count` | int (mult.) | {3,4} | 4 | conditional | derived from chassis (3 iff three_wheel_jogger) | Slot A / §8 |
| `palette_style` | enum | 4 colorways (§8.5 ⑥) | champagne_black | choice | rng.choice(PALETTE_STYLES) | A/B + companion forks |
| `rear_radius` | float | [0.145, 0.190] | 0.160 | independent | uniform then clamp; wheel center z = rear_radius | A/B tire radius |
| `front_radius` | float | [0.096, 0.130] | 0.110 | inequality | `front_radius ≤ rear_radius − 0.02`; wheel center z = front_radius | A/B tire radius |
| `cabin_width_scale` | float | [0.92, 1.08] | 1.0 | independent | scales cabin half-width, wheel x-track, canopy width | proportion ⑤ |
| (—) | constraint | — | — | equation | rear/front wheel center z + axle-stub z = tire radius (bottom on ground z=0) | ground contact |
| (—) | constraint | — | — | conditional | top_access resolved from cabin_form before use | §9 |

所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解；builder 不再失败。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤35 s/seed**（典型 12–25 s）。依据：库内实测参考典型模板 5–20 s，本类每 seed 造 3–4 个
tire/rim mesh（`TireGeometry`+`WheelGeometry`，最重）+ 1 张 canopy/dome mesh + 可选 pod
`ExtrudeWithHolesGeometry` 壳。分档 tessellation：wheel/tube `radial_segments ≤ 20`，tire tread
`count ≤ 26`，canopy/dome width_segments ≤ 8 / arc_segments ≤ 28，pod `corner_segments ≤ 8`；N 个同构
wheel 复用同一 `_add_wheel` helper。sweep `--compile-timeout 120` 作看门狗（≈3×上限）。超预算先降精度再迭代。

## Multiplicity / Copy Logic

**Axis 1 — wheel count `wheel_count` (N∈{3,4})**, source A (N=4) + B (N=3).
- `count_param` = ground-wheel count, **derived** from the chassis candidate (not independently sampled):
  `three_wheel_jogger` → N=3, `four_wheel_fixed`/`four_wheel_swivel` → N=4. Product domain {3,4}
  (both source-backed; no >4 or side-by-side twin per §Blocked).
- copied object = wheel part (`_add_wheel` tire+rim+hub_cap) + its CONTINUOUS `*_wheel_spin` joint;
  naming `rear_wheel_{i}` / `front_wheel_{i}`; placement = rear axle pair (always) + front axle pair
  (N=4) or single centered front (N=3). joint_policy = one CONTINUOUS spin per wheel (axis X). N enters
  `slot_choices` via the chassis candidate name (`three_wheel_jogger` vs `four_wheel_*`), so ≥2 wheel
  counts are visible in `axis_realization`.
- Repeated wheels/casters are loop-emitted with the shared `_add_wheel` / `_add_caster_yoke` helpers and
  stable indexed names.

No other template-level copy axis: the double/twin two-tier cabin (`rec_pet_stroller_var_skeleton_double_cabin`)
is **considered but deferred** — a stacked-tier cabin raises the whole frame (top_rim / rails / canopy &
handle hinge Z) and couples every other slot's mounting height, which was not stably reachable in v1
without re-solving the frame envelope; single-tier is the sole realized cabin height. Core structural
diversity is carried by the discrete chassis(①/②) + cabin_form(③) + top_access(②/③) + push_handle(②) slots.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | chassis adds/removes moving children (N=3 single front vs N=4 pair vs N=4 + 2 caster_yokes); top_access adds optional `front_door`; cabin_form adds optional `pod`. Distinct part-joint graphs. source-backed: A / B / swivel_caster / front_door / rigid_carrier forks. |
| └ multiplicity | 同构件 ×N | 有 | wheel_count N∈{3,4} derived from chassis candidate; see §8. |
| ② 关节类型 | 边换 type/轴 | 有 | CONTINUOUS X (wheel spin, all) + CONTINUOUS +Z (caster swivel) + REVOLUTE X (canopy, u_fold handle, front_door −X) + REVOLUTE Y (swing_bar, reversible handle) + PRISMATIC (telescoping handle). All source-backed (A/B + 4 mechanism forks). Every declared type appears in sweep. |
| ③ 主体形态家族 | 换核心几何原型 | 有 | Slot B cabin_form registered in `slot_choices`: `soft_fabric_cabin` (Planar Boundary Form, sewn panels) vs `rigid_carrier_pod` (Volumetric Envelope Form, molded shell); a 3rd Volumetric-Envelope enclosure reading via `enclosed_mesh_dome` (Slot C). form_subtype tagged per candidate. Reason for 2 in Slot B documented (§4 / Slot B note). source-backed anchors + forks. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only) | perforated side/front mesh windows, stitched/champagne trim (`top_rim`/`side_rail`), red front shock spring, fenders, cup-holder ring, pod vent grilles, canopy mesh panel. Host-conformal: emitted as host `.visual(...)` on the cabin/canopy face they sit on (derive order ③ form → ⑤ dims → ④). Not standalone candidates. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | rear_radius [0.145,0.190], front_radius [0.096,0.130] (front ≤ rear−0.02), cabin_width_scale [0.92,1.08]; wheel center z = radius (ground contact). **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): canopy REVOLUTE +X [−0.20,0.90] (lift front edge; dome [0.0,1.20]); front_door REVOLUTE −X [0.0,1.30] (drop outward+down); u_fold handle REVOLUTE +X [0.0,0.95] (fold down); swing_bar REVOLUTE Y [−0.65,0.35]; telescoping PRISMATIC [0.0,0.18] (extend up); reversible REVOLUTE Y [−1.4,1.4] (sweep rear↔front over canopy); wheel spin & caster swivel CONTINUOUS (full turn). `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)` + one targeted `ctx.pose(...)` per mechanism (canopy lifts +Z; door top drops; handle folds/extends/sweeps; caster swivel displaces wheel). No sampled-pose exemption needed. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes fabric + metal (champagne/silver tube) + plastic (hinges/forks/pod) + rubber (tires) + mesh; ≥4 colorways: champagne_black (A), navy_jogger (B), charcoal_grey, sand_tan. Material-class coverage ≥ ceil(0.5×4)=2 (fabric/metal/plastic/rubber all present every seed). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——soft vs rigid vs dome/door 形态拉得开、3-vs-4 轮、
4 种把手、fabric/metal/plastic/rubber 材质都出现、mesh 窗贴合宿主面不悬空、canopy/door/handle/caster
关节全程不穿模。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- chassis(3) × [soft × top_access(3) + rigid × top_access(1)] × push_handle(4)
  = 3 × (3 + 1) × 4 = **48 distinct slot tuples**, × wheel_count (derived) × 4 palette × continuous
  scales → topology target easily >300 over 1000 seeds (report-only, not a gate).

理由：多样性主要来自离散 chassis(①/②) + cabin_form(③) + top_access(②/③) + push_handle(②) 槽；连续
scale 仅做 clamp/derive，不撑多样性。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；采
`chassis` → `cabin_form` → `top_access` (= rng.choice over the cabin_form-allowed set) → `push_handle`
→ `palette_style` → continuous scales uniform；全部在 `resolve_config` clamp/gate。Compatibility matrix
= `ALLOWED_TOPS[cabin_form]` (soft→3, rigid→1) + front_radius≤rear_radius−0.02 inequality。No regression
overrides (procedural covers seed 0; seed 0 not special).
Topology target：≥300 over 1000-seed slot tuples (report-only).
Controlled local parameterization：rear_radius, front_radius, cabin_width_scale (continuous), all
clamped/derived in `resolve_config`; they never break the wheel ground-contact equation (center z =
radius), the canopy/handle hinge origins (fixed), or captured-pin allowances.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | chassis, cabin_form, gated top_access, push_handle, palette, radii, width | slot_choices_for_seed matches build choices |
| compatibility matrix | ALLOWED_TOPS[cabin_form] (rigid→fold_back_canopy); front_radius≤rear_radius−0.02; fallback → fold_back_canopy | no floating, collision, axis, closed-pose, ground-contact failures |
| controlled local variation | rear/front radius, cabin_width_scale, clamped | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| chassis | 3 | yes | yes | ①/② + N∈{3,4} |
| cabin_form | 2 | yes | no | ③ primary form slot (2 + documented reason; 3rd ③ reading via dome in Slot C) |
| top_access | 3 | yes | yes | ②/③ (2 gated to soft cabin) |
| push_handle | 4 | yes | yes | ② |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (chassis, cabin_form, top_access, push_handle) + `n{wheel_count}`
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix (`ALLOWED_TOPS` + front≤rear−0.02) prevents illegal combos in `resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped/derived in `resolve_config`; wheel center z = tire radius (ground contact)
- every non-FIXED joint is a captured pivot with element-scoped `allow_overlap` + `expect_overlap`; no MatingContract phantom anchors; the sole FIXED joint (`frame_to_pod`) is a real saddle-cradle contact (documented Rule 1 exception)
- key joints have expected type/axis/range (wheel spin CONTINUOUS X; caster swivel CONTINUOUS +Z; canopy REVOLUTE X; front_door REVOLUTE −X; handles REVOLUTE X/Y or PRISMATIC)
- copied wheels follow `rear_wheel_{i}` / `front_wheel_{i}` naming + axle placement
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per mechanism

## Reject cases
- A wheel whose bottom is off the ground (center z ≠ radius) or that fails to spin (dead CONTINUOUS joint).
- Canopy/dome that folds through the cabin or its own side ribs (穿模) at the open pose.
- front_door hinge origin off the frame hinge bar (>15mm) → articulation-origin fail; or door that
  doesn't drop/rotate when opened (dead joint).
- Caster yoke swivel that doesn't displace the front wheel, or a front wheel that floats off the yoke axle.
- rigid `pod` floating above the saddle brackets (isolated part / no cradle contact); or a dome/door
  paired with a rigid pod (illegal combo — must be gated out).
- Telescoping handle whose inner tube leaves the outer sleeve (island) or doesn't extend on PRISMATIC.
- reversible handle whose wide arc drives the arms through the canopy at mid-swing (穿模).
- Downgrading `TireGeometry`/`WheelGeometry`/canopy/dome/pod Mesh heroes to crude `Box` (Rule 3).
- Monochrome output (palette_style not driving `.visual(material=...)`).

## 与相邻类别的边界
- 不该混入：Pet carrier（standalone handheld/backpack，无 wheeled push frame）。
- 不该混入：baby/child stroller（人类婴儿座 + 5 点安全带 + 靠背可躺）。
- 不该混入：dog crate / bird cage（静态笼体，无推行车架）。
- 不该混入：pet wagon / hand-truck / shopping cart（开放平板货斗或工具车，无 canopy/cabin）。
- 不该混入：pet playpen（地面围栏，无轮）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Origin-A 4-wheel champagne tubular spine + origin-B 3-wheel jogger adapted into A's frame; 4 mechanism forks (swivel caster / front door / telescoping / reversible) + rigid-carrier + enclosed-dome forks all adopted. Double-tier cabin deferred (§8, height coupling). cadquery unavailable → rigid pod built with `ExtrudeWithHolesGeometry` (Mesh, no Box downgrade). |

## 模板实现备注（可选）
- Shared helpers: `_add_wheel` (tire+rim+hub_cap, origin A), `_tube`, `_canopy_shell_from_side_path`
  (origin A), `_curved_fabric_panel` (origin B, dome), `_add_caster_yoke` (swivel fork), `_rounded_tub`
  (`ExtrudeWithHolesGeometry` pod, no cadquery).
- Captured-pin element-scoped `allow_overlap`: wheel axle stub ↔ hub_cap; caster socket ↔ kingpin/bearing;
  canopy hinge pin ↔ collar; handle hinge pin ↔ pivot/tube; telescope sleeve ↔ handle_tube; front hinge
  bar ↔ door_hinge_strip; pod clip tab ↔ pod shell/receiver — all mirroring each source's `run_tests`.
- Gating: `enclosed_mesh_dome` / `front_door_canopy` only with `soft_fabric_cabin`; resolved in
  `resolve_config` before build.
