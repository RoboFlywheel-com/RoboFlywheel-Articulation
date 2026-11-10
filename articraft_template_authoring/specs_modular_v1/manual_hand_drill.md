# manual_hand_drill — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `manual_hand_drill` |
| template path | `agent/templates/manual_hand_drill.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (a grounded `body` chassis carries a serial spindle→chuck chain, a serial drive_gear→crank→grip chain, and a parallel speed_lever child) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 origin anchor + 8 forked_anchor slot variants) |
| source_index_policy | only adopted module sources are indexed below |

Reading notes (all 9 records share the SAME 7-part / 6-joint skeleton; forks re-plumb exactly one slot each):

- `rec_picturex_0611__manual_hand_drill__001__png_...` (671 L, origin): compact cobalt-blue cast-iron geared "eggbeater" hand drill. Part tree = `body` (grounded cast frame + long straight varnished-wood rear handle + selector mount), `drive_gear` (large exposed 40-tooth spur wheel + hub + shaft + thrust washer), `spindle` (long shaft + 14-tooth pinion + lathe chuck nose + backstop), `chuck_sleeve` (knurled toothed ring), `crank` (offset arm + fastener), `crank_grip` (axle + turned wood grip + end cap), `speed_lever` (boss + arm + tip). Joints: `body_to_drive_gear` CONTINUOUS +Y, `body_to_spindle` CONTINUOUS +X, `spindle_to_chuck_sleeve` REVOLUTE +X, `drive_gear_to_crank` CONTINUOUS +Y, `crank_to_grip` CONTINUOUS +Y, `body_to_speed_lever` REVOLUTE +Y (±0.42). Helpers: `_build_cast_frame`, `_build_toothed_wheel`, `_build_crank_arm`, `_wood_handle_mesh` (LatheGeometry), `_chuck_nose_mesh` (LatheGeometry).
- `..._var_gear_train_single_pinion_drive` (740 L): `drive_gear` big spur → single spoked **crown wheel** with axial crown teeth on ONE face (`_build_single_pinion_drive_wheel` L136-176); adds a `Mimic` keying crank 1:1 to drive rotation. Joint types/axes unchanged. ② mechanism / ③ gear form.
- `..._var_gear_train_dual_pinion_drive` (727 L): `drive_gear` big spur → **two coaxial narrow pinions** `drive_pinion_0/1` on one shaft (loop over `_build_toothed_wheel(width=0.006)`, L261-288) with a `pinion_bridge` spacer. Joints unchanged. ③ gear form (+more drive visuals).
- `..._var_gear_train_enclosed_bevel_drive` (782 L): adds `_build_enclosed_bevel_housing` (L135-197, a cast pod body visual) + `_build_bevel_drive_wheel` (L199-244, cone-based bevel crown, 32 teeth); `drive_gear` big flat spur → bevel cone wheel. Joints unchanged. ② mechanism / ③ gear form; adds one body visual (not a new part).
- `..._var_grip_form_pistol_grip` (723 L): body `main_handle` lathe barrel → **lofted dropped pistol grip** (`_wood_handle_mesh(pistol=True)` L161-193, 7 elliptical XZ sections). No part/joint change. ③ Primary Form Family.
- `..._var_grip_form_breast_plate_grip` (726 L): body `main_handle` barrel → **broad lofted oval breast pad** (`_breast_plate_mesh` L177-192 + `_breast_plate_end_mesh` L194-202). No part/joint change. ③ Primary Form Family.
- `..._var_speed_selection_sliding_two_speed_sele` (761 L): `body_to_speed_lever` REVOLUTE +Y → **PRISMATIC +X** [0, 0.028]; adds `_build_selector_mount` guide (L189-223) with side rails + hard stops; speed_lever reshaped into a sliding carriage. ② joint-type change.
- `..._var_speed_selection_reversible_ratchet_sel` (733 L): `body_to_speed_lever` stays REVOLUTE +Y but range widens to ±0.48; adds `_build_ratchet_selector_arm` (L161-185, stamped reversing paddle) + a dark-steel detent boss. ② mechanism / ③ paddle form.
- `..._var_chuck_collet_chuck` (747 L): `_chuck_nose_mesh` rewritten to a **4-finger collet** (rear shank + cone + tool bore + two saw-cut slots, L176-217); `chuck_sleeve` knurled toothed ring → knurled **collet nut** (`_build_collet_nut` L219-260). Joint `spindle_to_chuck_sleeve` unchanged (REVOLUTE +X). ③ chuck-head form.

Every fork re-plumbs exactly one slot; the shared skeleton (7 parts / 6 joints) is identical everywhere. This is a mechanism-dominated tool with one registered ③ Primary Form Family slot (the rear grip) plus a ③-flavored chuck-head slot.

## 核心身份

A **manual (hand-cranked) hand drill** ("eggbeater" / breast drill): a grounded cast-metal `body` frame that carries (a) a spindle running fore-aft on a CONTINUOUS bearing, tipped by a keyed/collet **chuck** that grips a bit; (b) a large side-mounted **drive gear** turned by an offset **crank** with a free-spinning **grip**, meshing with a spindle pinion to spin the chuck; (c) a rear **hand grip / breast plate** the operator pushes against; and (d) a small **speed selector** lever/slider. Defining features: the exposed drive wheel, the offset crank + free grip, the forward-projecting chuck, and at least one real non-FIXED joint (the drive train is CONTINUOUS multi-turn).

Category identity:
- one grounded `body` holding the cast frame, rear grip form, and selector mount;
- one `drive_gear` (CONTINUOUS +Y) meshing a `spindle` pinion; the `crank` (CONTINUOUS +Y) + free `crank_grip` (CONTINUOUS +Y) turn it;
- one `spindle` (CONTINUOUS +X) tipped by a `chuck_sleeve` (REVOLUTE +X, jaw tightening);
- one `speed_lever` selector (REVOLUTE +Y small range, or PRISMATIC +X short slide).

Distinct from an **electric drill** (has a motor housing + trigger, no crank/gear wheel) and a **brace-only auger** (a single sweep U-frame, no gear train). Neighbor rejects below in §11.

## 槽位 + 候选模块表

Four slots. All re-plumb one layer of the shared skeleton; `grip_form` is the registered ③ Primary Form Family slot.

### Slot A: `gear_train` — the drive wheel form + gear mechanism (drive_gear part)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_spur_gear` | forked_anchor | `rec_picturex_0611__manual_hand_drill__001__png_...` (`picture/0611/manual_hand_drill/001.png`) | L95-132 (`_build_toothed_wheel`), L251-304 (drive_gear block) | eligible if compatible | Large exposed flat **spur wheel** (40 radial teeth) + blue gear face + hub + shaft + thrust washer, meshing a 14-tooth spindle pinion. `③ Macro Surface Construction` = open radial spur crown. |
| `single_pinion_crown` | forked_anchor | `..._var_gear_train_single_pinion_drive` | L136-176 (`_build_single_pinion_drive_wheel`), drive_gear block | eligible if compatible | Spoked **crown wheel** with axial crown teeth on one face (36 teeth) + small hub cap; crank keyed 1:1. `③ Macro Surface Construction` = spoked crown / axial teeth. |
| `dual_pinion` | forked_anchor | `..._var_gear_train_dual_pinion_drive` | L261-288 (twin-pinion loop) | eligible if compatible | **Two coaxial narrow pinions** `drive_pinion_0/1` on one shaft with a `pinion_bridge` spacer. `①`+`③` = doubled drive visuals / stacked-pinion envelope. |
| `enclosed_bevel` | forked_anchor | `..._var_gear_train_enclosed_bevel_drive` | L135-197 (`_build_enclosed_bevel_housing`), L199-244 (`_build_bevel_drive_wheel`) | eligible if compatible | **Bevel cone crown wheel** (32 teeth) running inside a cast enclosed housing (an added body visual). `②` (bevel mesh) + `③ Volumetric Envelope Form` = conical bevel wheel in a pod. |

### Slot B: `grip_form` — rear hand grip Primary Form Family (body `main_handle` visual)  ← ③ registered slot

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `straight_barrel_handle` | forked_anchor | `rec_picturex_0611__manual_hand_drill__001__png_...` | L161-172 (`_wood_handle_mesh`), L214-240 (body handle block) | eligible if compatible | Long lathe-turned **straight barrel** wood handle projecting behind the gearbox (axis +X) with ferrule + endgrain cap. `form_subtype = Volumetric Envelope Form` (turned barrel). |
| `pistol_grip` | forked_anchor | `..._var_grip_form_pistol_grip` | L161-193 (`_wood_handle_mesh(pistol=True)` loft) | eligible if compatible | **Dropped pistol grip** lofted from 7 elliptical XZ sections (neck → palm swell → flared butt), hanging down (−Z). `form_subtype = Volumetric Envelope Form` (lofted pistol grip). |
| `breast_plate` | forked_anchor | `..._var_grip_form_breast_plate_grip` | L177-202 (`_breast_plate_mesh`, `_breast_plate_end_mesh`) | eligible if compatible | Short neck → shoulder → **broad lofted oval breast pad** to push against the chest. `form_subtype = Planar Boundary Form` (broad oval pad boundary). |

### Slot C: `speed_selection` — speed selector (speed_lever part + body mount)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pivot_lever` | forked_anchor | `rec_picturex_0611__manual_hand_drill__001__png_...` | L420-444 (speed_lever block), L496-509 (`body_to_speed_lever` REVOLUTE +Y) | eligible if compatible | Small boss + box arm + tip pivoting **REVOLUTE +Y** (±0.42). `②` revolute paddle. |
| `reversible_ratchet` | forked_anchor | `..._var_speed_selection_reversible_ratchet_sel` | L161-185 (`_build_ratchet_selector_arm`), speed_lever block | eligible if compatible | Stamped reversing paddle arm + dark-steel detent boss, **REVOLUTE +Y** wider ±0.48. `②`+`③` = reversing paddle form. |
| `sliding_two_speed` | forked_anchor | `..._var_speed_selection_sliding_two_speed_sele` | L189-223 (`_build_selector_mount` guide), speed_lever carriage, `body_to_speed_lever` PRISMATIC +X | eligible if compatible | Cast guide with side rails + hard stops; carriage slides **PRISMATIC +X** [0, 0.028]. `②` prismatic (distinct joint type). |

### Slot D: `chuck` — chuck head form (chuck_sleeve part + spindle nose visual)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `keyed_geared_chuck` | forked_anchor | `rec_picturex_0611__manual_hand_drill__001__png_...` | L175-186 (`_chuck_nose_mesh`), L306-367 (spindle nose + `chuck_sleeve` toothed ring) | eligible if compatible | Lathe-turned tapered chuck nose + **knurled toothed ring** sleeve (32-rib key ring). `③` chuck-head form (geared key chuck). |
| `collet_chuck` | forked_anchor | `..._var_chuck_collet_chuck` | L176-217 (4-finger collet nose), L219-260 (`_build_collet_nut`) | eligible if compatible | **4-finger collet** nose (rear shank + cone + tool bore + two saw-cut jaw slots) + knurled **collet nut** sleeve. `③` chuck-head form (collet). |

硬约束说明:
- `chuck` has 2 candidates (degraded from target 3). Reason: the 5-star pool forked exactly one chuck variant (`collet_chuck`) off the origin's keyed geared chuck; no third structurally-distinct chuck source exists. Both candidates are `forked_anchor`, structurally distinct (toothed key ring vs collet jaws + nut), and share the REVOLUTE +X `spindle_to_chuck_sleeve` interface. No world_knowledge_extrapolation candidate added (kept source-faithful).
- `grip_form` is registered into `slot_choices` as the ③ Primary Form Family slot with 3 recognizable prototypes (straight barrel / pistol / breast plate); each candidate carries a `form_subtype`.

## 槽位图（slot graph）

pattern: `mixed`

```
body (grounded root; carries cast_frame, grip_form visual, selector_mount, [enclosed_bevel housing visual])
 ├──[CONTINUOUS +Y at gear axis (0,0,0.015)]──> drive_gear   (gear_train slot: form of the wheel)
 │        └──[CONTINUOUS +Y at (0,0.046,0)]──> crank
 │                    └──[CONTINUOUS +Y at crank tip (0.061,0.006,-0.043)]──> crank_grip
 ├──[CONTINUOUS +X at spindle axis (0,0,-0.050)]──> spindle   (chuck slot: nose visual)
 │        └──[REVOLUTE +X at (-0.084,0,0)]──> chuck_sleeve    (chuck slot: sleeve part)
 └──[REVOLUTE +Y | PRISMATIC +X at selector mount]──> speed_lever  (speed_selection slot)
```

Interfaces / joints:
- `body → drive_gear`: origin (0,0,0.015); axis (0,1,0); CONTINUOUS multi-turn. `drive_gear` toothed_wheel meshes the `spindle` pinion → element-scoped `allow_overlap(drive_gear.teeth, spindle.pinion, reason="gear mesh")`. Captured shaft; mating omitted, guarded by flat origin baseline.
- `drive_gear → crank`: origin (0,0.046,0); axis (0,1,0); CONTINUOUS. Captured on gear hub; `allow_overlap` crank_fastener ↔ gear hub.
- `crank → crank_grip`: origin at crank tip (0.061,0.006,-0.043); axis (0,1,0); CONTINUOUS free-spinning. Captured on grip axle; `allow_overlap` grip_axle ↔ crank grip_eye.
- `body → spindle`: origin (0,0,-0.050); axis (1,0,0); CONTINUOUS multi-turn. Spindle rides the hollow cast sleeve bore → `allow_overlap(spindle.shaft, body.cast_frame)` element-scoped (bearing bore).
- `spindle → chuck_sleeve`: origin (-0.084,0,0); axis (1,0,0); REVOLUTE ±π (jaw tightening). Sleeve captures the nose → `allow_overlap(chuck_sleeve, spindle.nose)`.
- `body → speed_lever`: `pivot_lever`/`reversible_ratchet` origin (0.050,0.026,-0.050), axis (0,1,0), REVOLUTE [-0.42..0.42] / [-0.48..0.48]; `sliding_two_speed` origin at guide, axis (1,0,0), PRISMATIC [0, 0.028]. Captured in the mount → element-scoped `allow_overlap` selector boss/tip ↔ mount.

## 每槽位 Module Emits / Interfaces

### Slot A / module `open_spur_gear` (also the shared drive-chain skeleton)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drive_gear` (toothed_wheel spur mesh, blue_gear_face, gear_hub, gear_shaft, thrust_washer); shared: `crank` (crank_arm + crank_fastener) chained CONTINUOUS; `crank_grip` (grip_axle + wood_grip + grip_end) chained CONTINUOUS | S1 / 001 L251-304, 369-418 |
| internal joints | `drive_gear_to_crank` CONTINUOUS +Y, `crank_to_grip` CONTINUOUS +Y | S1 / 001 L478-495 |
| upstream interface | `body_to_drive_gear` origin (0,0,0.015), axis +Y, CONTINUOUS | S1 |
| downstream interface | gear teeth mesh the spindle pinion (element allow_overlap) | S1 |

### Slot A / modules `single_pinion_crown` / `dual_pinion` / `enclosed_bevel`
| emits | Same `drive_gear` part + crank + crank_grip chain; only the wheel mesh (and, for `enclosed_bevel`, one extra `body` housing visual) differ | single_pinion L136-176 / dual_pinion L261-288 / enclosed_bevel L135-244 |

### Slot B / module `straight_barrel_handle` / `pistol_grip` / `breast_plate`
| emits | `body.main_handle` visual + `handle_ferrule` + `main_handle_end` (all `body` visuals, Rule 1 — non-moving) | 001 L214-240 / pistol L161-193 / breast L177-202 |
| internal joints | none (rear grip is fixed body geometry) | — |
| interface | fused into the grounded `body`; no joint | — |

### Slot C / module `pivot_lever` / `reversible_ratchet` / `sliding_two_speed`
| emits | `speed_lever` part (selector_boss + selector_arm + selector_tip [+ carriage/paddle]) + `selector_mount` body visual | 001 L241-249, 420-444 / ratchet L161-185 / sliding L189-223 |
| internal joints | `body_to_speed_lever` REVOLUTE +Y (pivot/ratchet) or PRISMATIC +X (sliding) | 001 L496-509 |
| upstream interface | mount on body at (0.050, 0.026, -0.050) | S1 |

### Slot D / module `keyed_geared_chuck` / `collet_chuck`
| emits | `spindle.chuck_nose` visual (lathe nose or collet jaws) + `chuck_sleeve` part (toothed ring or collet nut) | 001 L175-186, 352-367 / collet L176-260 |
| internal joints | `spindle_to_chuck_sleeve` REVOLUTE +X | S1 / 001 L464-477 |
| upstream interface | sleeve captures spindle nose at (-0.084,0,0) | S1 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `gear_train` | enum | `open_spur_gear` / `single_pinion_crown` / `dual_pinion` / `enclosed_bevel` | — | choice | procedural sampler | Slot A |
| `grip_form` | enum | `straight_barrel_handle` / `pistol_grip` / `breast_plate` | — | choice | procedural sampler | Slot B |
| `speed_selection` | enum | `pivot_lever` / `reversible_ratchet` / `sliding_two_speed` | — | choice | procedural sampler | Slot C |
| `chuck` | enum | `keyed_geared_chuck` / `collet_chuck` | — | choice | procedural sampler | Slot D |
| `palette_style` | enum | `cobalt_enamel` / `oxblood_enamel` / `black_japanned` / `forest_green_enamel` / `bare_cast_steel` | `cobalt_enamel` | choice | 5 realistic hand-drill colorways | palette table |
| `frame_scale` | float | [0.90, 1.12] | 1.0 | independent | **global similarity transform** about the world origin: every cadquery mesh gets `unit_scale=frame_scale`, every primitive dim / `Origin.xyz` / joint origin / prismatic travel is ×`frame_scale`. A true similarity keeps the gear mesh + all clearances intact at every scale. | 001 |
| `crank_reach_scale` | float | [0.90, 1.18] | 1.0 | independent | crank arm length + grip pivot radius only (on top of `frame_scale`); larger reach = more clearance | 001 L369-380 |
| `selector_travel_scale` | float | [0.85, 1.15] | 1.0 | independent | selector REVOLUTE range / PRISMATIC slide travel only | 001 L500-508 |
| (—) | constraint | — | — | inequality | crank swept-clear: `crank_reach·crank_reach_scale ≥ min_reach` so the grip orbit clears the wheel/body; else grow crank_reach | interface / Rule 5 |
| (—) | constraint | — | — | inequality | `sliding_two_speed` slide travel clamped to the guide length (`travel ≤ 0.028·frame_scale`) so the carriage stays on the rails | mount geometry |

连续尺寸采样契约: sample the 3 `independent` scales uniformly; no `equation` derivations (`frame_scale` is a similarity, `crank_reach`/`selector_travel` are per-part); project the two `inequality` constraints in `resolve_config` (grow `crank_reach` to a clearance floor; clamp selector travel to the guide). No `conditional` ranges.

## 7.5 编译预算 / compile budget

Target: **≤18 s per seed**. Geometry = 1 cadquery cast frame (`mesh_from_cadquery` tol 0.0007), 1-2 cadquery toothed/bevel wheels (tol 0.0004), 1-2 LatheGeometry/loft grips (48 seg), 1 cadquery chuck nose/collet + optional collet nut. Tessellation: small-radius pins/washers/teeth ≤32 seg, hero frame/wheel ≤64; LatheGeometry `segments=48`. Meshes cached per (slot-value, scale-bucket) via `AssetContext`; identical sub-parts reuse one `Mesh`. Sweep hang-guard `--compile-timeout 120` (~6× budget).

## 8. Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots (body / drive_gear / spindle / chuck_sleeve / crank / crank_grip / speed_lever) 表达。No `*_count` axis is exposed; no template-level visual/part/joint replication. `dual_pinion` is a fixed 2-pinion module (only N=2 is source-backed), not a multiplicity axis.

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有(弱) | Shared skeleton = 7 parts / 6 joints across all forks (body, drive_gear, spindle, chuck_sleeve, crank, crank_grip, speed_lever). `dual_pinion` adds intra-`drive_gear` pinion visuals; `enclosed_bevel` adds a `body` housing visual. No fork adds/removes an articulated PART — the ① graph is intentionally fixed (all 9 source records share it). Source-backed. |
| └ multiplicity | 同构件 ×N | 无 | Single drive gear, single spindle, single crank, single selector; no repeated-part axis (see §8). |
| ② 关节类型 | 图不变,某条边换 type/轴 | 有 | `body_to_speed_lever` flips **REVOLUTE +Y** (`pivot_lever`, `reversible_ratchet`) ↔ **PRISMATIC +X** (`sliding_two_speed`) — both realized every sweep. `gear_train` changes the drive mesh type (spur vs crown vs bevel), coupling geometry only (all CONTINUOUS +Y). Source-backed by the two speed_selection variants. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | 有 | Registered slot = `grip_form` (3 prototypes): `straight_barrel_handle` = Volumetric Envelope Form (turned barrel), `pistol_grip` = Volumetric Envelope Form (lofted dropped grip), `breast_plate` = Planar Boundary Form (broad oval pad). Additionally `gear_train` (4 wheel forms: open spur / spoked crown / dual pinion / conical bevel — Macro Surface Construction + Volumetric Envelope) and `chuck` (2 head forms: geared key ring vs collet jaws) carry ③ form. All `forked_anchor`. |
| ④ 表面装饰 | 原型不变,叠加表面细节 | 有 | (record_only): gear teeth (radial/axial/bevel), knurled chuck ring ribs, collet nut knurling, cast-frame ribs/bosses, ferrule band. All host-derived (fused into the parent mesh, not floating parts — Rule 1/4). No template-level decoration-count axis. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | Scales: `frame_scale [0.90,1.12]` (global similarity, always visible), `crank_reach_scale [0.90,1.18]`, `selector_travel_scale [0.85,1.15]`. Motion envelopes: `body_to_drive_gear` / `drive_gear_to_crank` / `crank_to_grip` / `body_to_spindle` CONTINUOUS (整圈, `qc_sample_values {0, ±π/2, π}`); `spindle_to_chuck_sleeve` REVOLUTE +X [−π, π]; `body_to_speed_lever` REVOLUTE +Y [−0.42..0.42]/[−0.48..0.48] or PRISMATIC +X [0, 0.028·scale]. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + targeted `ctx.pose` proving (crank spins grip around the wheel clearing body), (spindle+chuck spin), (selector travels). Gear-mesh + captured-pin overlaps declared element-scoped. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palettes: `cobalt_enamel` (origin blue), `oxblood_enamel` (vintage maroon), `black_japanned` (black + brass + beech), `forest_green_enamel`, `bare_cast_steel` (unpainted grey iron + polished steel + light wood). Material categories: painted-enamel / metal / wood ≥ ceil(0.5×5)=3. Every `.visual(material=)` driven by the sampled palette. |

## 9. 采样与覆盖审计

总组合数（结构）：`gear_train (4) × grip_form (3) × speed_selection (3) × chuck (2)` = **72** legal structural tuples (before palette / continuous scales). All tuples legal; no gating needed (the four slots touch disjoint parts).

理由：mechanism-dominated tool; four independent structural axes each source-backed by the origin + forks. 72 tuples × 5 palettes = 360 discrete appearances — plenty for a maturity audit; report-only.

seed_domain_policy: `procedural_first`.

**Procedural Sampling / Sweep Plan.** `config_from_seed(seed)` uses `random.Random(seed)`; samples `gear_train`, `grip_form`, `speed_selection`, `chuck`, `palette_style` uniformly, then the five continuous scales uniformly. `resolve_config` clamps every scale and applies the two inequalities (crank-clear-of-wheel; selector-travel-on-guide). `slot_choices_for_seed(seed)` returns `(("gear_train",…),("grip_form",…),("speed_selection",…),("chuck",…))` matching `build_*` bit-for-bit. seed 0 is not special.

**Topology target.** 72 legal tuples; a 1000-seed report shows all 4 gear_train, all 3 grip_form, all 3 speed_selection, both chuck, all 5 palettes. Report-only, not gated.

Regression overrides: none at P0.

**Controlled local parameterization.** `frame_scale` (global similarity), `crank_reach_scale`, `selector_travel_scale`; all clamped in `resolve_config`. Cross-part relations expressed as `inequality` (crank reach clearance floor; selector travel vs guide) — resolved in `resolve_config`, never left to the builder.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | gear_train → grip_form → speed_selection → chuck → palette → continuous scales | `slot_choices_for_seed` == build choices |
| compatibility matrix | all 72 tuples legal; slots touch disjoint parts → no gating | no floating parts, gear-mesh/captured-pin overlaps element-scoped, crank clears wheel & body through 360°, selector stays on guide |
| controlled local variation | 3 scales in listed ranges | proportions vary without breaking bearings, gear mesh, crank clearance, chuck capture |
| regression overrides | none | — |
| random sweep | seeds 0-15 (fast) → 16-35 (final) → corner | corner covers scale extremes + rare tuples (e.g. `enclosed_bevel + breast_plate + sliding_two_speed + collet_chuck`) |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A `gear_train` | 4 | yes | yes | origin + 3 forked_anchor |
| B `grip_form` | 3 | yes | yes | ③ Primary Form Family slot; origin + 2 forked_anchor |
| C `speed_selection` | 3 | yes | yes | origin + 2 forked_anchor (② joint-type axis) |
| D `chuck` | 2 | yes | no | degraded to 2; only one chuck fork sourced (justified above) |

## 10. Validator

- `slot_choices_for_seed` returns implemented module names for all 4 slot axes.
- `config_from_seed(0)` deterministically returns a legal, buildable config (registry contract).
- `resolve_config` clamps every continuous scale and applies the crank-clearance + selector-travel inequalities before the builder runs.
- `slot_choices_for_seed(seed)` matches actual build choices bit-for-bit.
- Every non-FIXED joint declares axis + range; gear-mesh and captured-pin/bearing overlaps are guarded by element-scoped `ctx.allow_overlap` in `run_manual_hand_drill_tests`.
- `run_manual_hand_drill_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` **plus** targeted `ctx.pose(...)` proving intended motion (crank turns grip around the wheel; spindle+chuck spin; selector travels within range).
- Key joints have expected type/axis: drive/crank/grip/spindle CONTINUOUS, chuck REVOLUTE +X, speed_lever REVOLUTE +Y or PRISMATIC +X per slot.
- No small curated / modulo table is used as the main seed domain.
- Shared frame/wheel/handle/chuck geometry lives in single helpers; `frame_scale` single-sourced through `resolve_config`.

## Reject cases

- Electric drill housing (motor barrel + trigger, no crank/gear wheel): rejected — belongs to `Powertools_drill`.
- Brace-and-bit (single sweep U-frame, no gear train): rejected — different skeleton, no drive gear.
- Drive gear that does not mesh the spindle pinion (floating wheel): rejected — gear teeth must overlap the pinion (element allow_overlap present) and share the +Y axis.
- Crank/grip that sweep-collides with the body or wheel at a half-turn: rejected — crank-clearance inequality + sampled-pose collision.
- Chuck sleeve that floats off the spindle nose: rejected — sleeve must capture the nose (REVOLUTE +X, allow_overlap on the nose).
- Selector slider translating off the guide rails: rejected — travel clamped to guide length.
- Rear grip authored as a separate FIXED part instead of a `body` visual: rejected — Rule 1 (non-moving grip is body geometry).
- Downgrading LatheGeometry/collet/bevel meshes to crude Box/Cylinder: rejected — Rule 3.

## 11. 与相邻类别的边界

- 不该混入：`Powertools_drill` (electric drill) — has a motor housing + trigger + battery, no hand crank / exposed drive gear. Our category is hand-cranked with a visible gear train.
- 不该混入：`brace_and_bit` / brace-only auger — a single bent-sweep U-frame with a chuck, no gear reduction, no offset crank-on-wheel.
- 不该混入：`hand_cultivator` / `seed_spreader` (0611 neighbors) — garden tools, no chuck / drive gear / spindle.
- 不该混入：`manual_coffee_grinder` — grinds beans into a grounds bin; no chuck, no forward-projecting spindle, drive is a top vertical crank not a side wheel.

## 12. 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec authored from the 9-record 5-star pool (1 origin + 8 slot forks). Four slots (gear_train ×4, grip_form ×3 [③], speed_selection ×3 [②], chuck ×2); 72 legal structural tuples; all slots touch disjoint parts so no gating. All source-backed; no world_knowledge_extrapolation candidate required. |

## 13. 模板实现备注

- Follow the `Accessories_Cushion.py` structure (direct `model.articulation` + parallel/serial children, per-palette `mats` dict driving every `.visual(material=)`), NOT the `_modular.py` `assemble` InterfaceSpec driver — the skeleton is fixed and slots swap part geometry.
- Port the origin helpers verbatim (`_build_cast_frame`, `_build_toothed_wheel`, `_build_crank_arm`, `_wood_handle_mesh`, `_chuck_nose_mesh`) plus the variant helpers (`_build_single_pinion_drive_wheel`, twin-pinion loop, `_build_enclosed_bevel_housing`, `_build_bevel_drive_wheel`, pistol loft, `_breast_plate_mesh`, `_build_selector_mount`, `_build_ratchet_selector_arm`, collet nose + `_build_collet_nut`). Keep primitive types (Rule 3).
- Captured-pin / bearing-bore / gear-mesh overlaps declared element-scoped in `run_manual_hand_drill_tests`: (a) drive_gear teeth ↔ spindle pinion (gear mesh), (b) spindle shaft ↔ cast_frame bore (bearing), (c) crank_fastener ↔ gear hub, (d) grip_axle ↔ crank grip_eye, (e) chuck_sleeve ↔ spindle nose, (f) selector boss/tip ↔ mount. `mating` omitted for these captured joints (grandfathered).
- All CONTINUOUS drive joints use `qc_sample_values = {0, ±π/2, π}`; the REVOLUTE chuck uses its ±π range; selector uses its clamped range. `frame_scale` applies as a uniform multiplier on primitive dims and mesh `unit_scale`.

## 14. Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | open_spur_gear / straight_barrel_handle / pivot_lever / keyed_geared_chuck (+ shared skeleton) | rec_picturex_0611__manual_hand_drill__001 | L23-L511 | full 7-part / 6-joint skeleton + origin candidates |
| S2 | A | single_pinion_crown | rec_0611_manual_hand_drill_var_gear_train_single_pinion_drive | L136-176 | spoked crown drive wheel |
| S3 | A | dual_pinion | rec_0611_manual_hand_drill_var_gear_train_dual_pinion_drive | L261-288 | twin coaxial pinions + bridge |
| S4 | A | enclosed_bevel | rec_0611_manual_hand_drill_var_gear_train_enclosed_bevel_drive | L135-244 | bevel cone wheel + enclosed housing body visual |
| S5 | B | pistol_grip | rec_0611_manual_hand_drill_var_grip_form_pistol_grip | L161-193 | lofted dropped pistol grip |
| S6 | B | breast_plate | rec_0611_manual_hand_drill_var_grip_form_breast_plate_grip | L177-202 | broad oval breast pad |
| S7 | C | sliding_two_speed | rec_0611_manual_hand_drill_var_speed_selection_sliding_two_speed_sele | L189-223 | prismatic sliding selector + guide |
| S8 | C | reversible_ratchet | rec_0611_manual_hand_drill_var_speed_selection_reversible_ratchet_sel | L161-185 | reversing ratchet paddle + detent |
| S9 | D | collet_chuck | rec_0611_manual_hand_drill_var_chuck_collet_chuck | L176-260 | 4-finger collet nose + knurled collet nut |
</content>
</invoke>
