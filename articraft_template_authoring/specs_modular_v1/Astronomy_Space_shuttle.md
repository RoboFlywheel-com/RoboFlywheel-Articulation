# Modular Spec — Astronomy / Space shuttle

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Space_shuttle` |
| template path | `agent/templates/Astronomy_Space_shuttle.py` |
| test path (optional) | `tests/agent/test_Astronomy_Space_shuttle_template.py` |
| stage | `TEMPLATE_COMPLETE` |
| status | `mechanically_ready` (`uv run articraft template check Astronomy_Space_shuttle --stage random-16\|random-36\|corner` all pass, 2026-08-01) |
| __modular__ | `True` |
| pattern | `mixed` (root airframe + 3 parallel-children slots + 3 multiplicity axes) |
| function stem | `astronomy_space_shuttle` (exports `build_astronomy_space_shuttle`, `config_from_seed`, `run_astronomy_space_shuttle_tests`) |

`pattern = mixed`: a single root `fuselage` part carries all fixed airframe
geometry (hull, wings, TPS skins, livery, payload-bay cavity, OMS pods, engine
bells). Three parallel-children slots parent their own articulations directly to
the fuselage (no serial chain joint): `control_surfaces` (bay doors + body flap +
elevons), `tail` (fin fused as a fuselage visual + articulated rudder panels),
`landing_gear` (nose + main gear chains + gear doors). Three multiplicity axes
ride on top: `engine_count` (fused SSME bells), elevon segment count (via the
control-surfaces module choice), and `main_wheel_count`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_build-the-nasa-space-shuttle-orbiter-endeavour-e_20260703_135555_323010_4400ecc9` — ORIGIN 母本 (blended-lifting-body hull, double-delta wing, single swept fin + split rudder, 3 SSME bells + 2 OMS pods, bay doors, elevons, body flap, revolute retract gear w/ dual main wheels + steerable nose fork + gear doors).
- `rec_space_shuttle_var_cylindrical_fuselage` — ③ form: near-circular Buran-like hull barrel (rebalanced sections, all exponents 2.0).
- `rec_space_shuttle_var_delta_wing` — ③ form: pure delta wing planform (constant LE sweep, no glove kink).
- `rec_space_shuttle_var_straight_fin` — ③ form: straight-tapered near-rectangular fin (unswept LE).
- `rec_space_shuttle_var_twin_tail` — ① skeleton: two smaller swept fins on the aft deck, each with a rudder (replaces single centerline fin).
- `rec_space_shuttle_var_elevons_split` — ① multiplicity: 2 elevon segments per wing (inboard + outboard) vs 1.
- `rec_space_shuttle_var_main_engines_2` — multiplicity: 2 SSME bells.
- `rec_space_shuttle_var_main_engines_4` — multiplicity: 4 SSME bells.
- `rec_space_shuttle_var_main_wheels_single` — ① multiplicity: 1 main wheel per strut vs 2.
- `rec_space_shuttle_var_telescoping_gear` — ② joint type: PRISMATIC telescoping gear struts (extend straight down) vs REVOLUTE retract.

## 核心身份

A **winged reusable spaceplane orbiter (Space Shuttle / Buran class) in landing
configuration**: a blended-lifting-body or near-circular **fuselage** with a
black-TPS underside and white upper skin, a low **delta wing** (double-delta or
pure delta) carrying hinged **elevons**, a **vertical tail** (single swept /
straight / twin) carrying a **rudder / speed-brake**, a **body flap** and closed
**payload-bay doors** on the spine, an aft cluster of **2-4 main engine bells**
flanked by 2 OMS pods, and a deployed tricycle **landing gear** (steerable nose
gear + 2 main gear on revolute or prismatic struts, spinning wheels, hinged gear
doors). At least one real non-fixed joint is always present (control surfaces +
gear). Default mature domain: ~37 m orbiter, gear down, bay doors closed.

Not to be confused with the neighbouring picture subclasses **Astronomy / Return
capsule** (a blunt ballistic re-entry body, no wings/tail) or **Astronomy /
Rocket engine** (a bare thrust chamber + nozzle, no airframe). The shuttle is
the whole winged airframe; the engine bells are one fused aft feature, not the
whole object.

## 槽位 + 候选模块表

### Slot A：airframe (root · ③ Primary Form Family — hull + wing planform + engine count)

The root orbiter body. Same part tree across candidates: one `fuselage` part
carrying the hull loft (with a real payload-bay cavity cut), black-TPS belly /
nose / chine skins, forward RCS panel + ports, cockpit windows, crew hatch, bay
interior floor/rails/sills, one selected payload-bay support/interface layout,
US-flag + insignia + name livery, both wings (loft + black leading edge + black
underside), 2 OMS pods + nozzles, aft base heat shield, and `engine_count` fused
SSME bell + throat visuals. The ③ hull-envelope, ③ wing-planform and payload-bay
interface prototypes plus the engine count change; the mounting envelope for all
appendages is single-sourced (Contract 3c) so the child slots are form-independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `blended` (hull) | forked_anchor (origin) | origin `...4400ecc9` | L245-L278 (hull loft), L280-L432 (skins/livery/wings), L446-L488 (OMS/engines) | eligible | blended-lifting-body superellipse hull (flat wide belly, high crown, per-station exponents 2.0-3.4). **Volumetric Envelope Form** |
| `cylindrical` (hull) | forked_anchor | `rec_space_shuttle_var_cylindrical_fuselage` | L245-L261 | eligible | near-circular tube hull (half-height ~= half-width, all exponents 2.0). **Volumetric Envelope Form** |
| `double_delta` (wing) | forked_anchor (origin) | origin `...4400ecc9` | L73-L82 | eligible | double-delta planform: forward glove kink then main delta. **Planar Boundary Form** (wing planform outline) |
| `pure_delta` (wing) | forked_anchor | `rec_space_shuttle_var_delta_wing` | L73-L82 | eligible | pure delta: single constant LE sweep root-to-tip, no glove. **Planar Boundary Form** |
| `standard_bay` (payload interface) | controlled_extrapolation | origin `...4400ecc9` payload cavity/floor/rails/sills | L585-L652 | eligible | standard longitudinal rail + central keel, preserves the canonical shuttle cargo-bay support layout. **Functional Payload Interface** |
| `satellite_deployer` (payload interface) | controlled_extrapolation | origin payload rails/sills, derived deployment interface | L641-L652 | eligible | longitudinal deployment truss with forward/aft adapters and pedestals; all supports remain inside the bay envelope. **Functional Payload Interface** |
| `laboratory_module` (payload interface) | controlled_extrapolation | origin payload cavity/floor/rails, derived pressure-module interface | L585-L652 | eligible | cylindrical pressure module with port/starboard racks and an umbilical panel; bounded by the existing bay floor and door crown. **Functional Payload Interface** |
| `engine_count` 2/3/4 | forked_anchor | origin L472-L473 (3); `main_engines_2` L473 (2); `main_engines_4` L472-L477 (4) | see §8 | eligible | fused SSME bell (`LatheGeometry` profile) + dark throat disc, N copies on the aft base. multiplicity, ④ form-detail count |

hull_form × wing_form are two orthogonal ③ sub-axes built inside the one root
factory; each is registered independently in `slot_choices` (`hull_form`,
`wing_form`). The assembler keys the airframe SlotSpec by `hull_form`.

### Slot B：control_surfaces (parallel children on fuselage · ① skeleton + multiplicity elevon segments)

Always emits: 2 payload-bay doors (REVOLUTE, closed at q=0), 1 body flap
(REVOLUTE). Elevon count is the structural axis.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_elevon` | forked_anchor (origin) | origin `...4400ecc9` | L490-L599 | eligible | 1 elevon per wing (2 total) `LoftGeometry` slab on wing-TE REVOLUTE hinge + bay doors + body flap. |
| `split_elevon` | forked_anchor | `rec_space_shuttle_var_elevons_split` | L552-L596 | eligible | ① multiplicity: 2 elevon segments per wing (inboard + outboard, 4 total), each its own REVOLUTE hinge; identical bay doors + body flap. |

2 candidates: only the elevon segment count structurally varies across the pool's
control-surface geometry; degrade-to-2 is source-limited and justified.

### Slot C：tail (parallel children on fuselage · ① skeleton + ③ form + ② rudder joint)

Vertical tail. The fin(s) are NON-moving so they are fused as `fuselage`
visuals (Rule 1); only the rudder panel(s) are separate REVOLUTE parts parented
to the fuselage.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `swept_fin` | forked_anchor (origin) | origin `...4400ecc9` | L91-L112 (stations/hinge), L434-L444 (fin loft), L513-L549 (split rudder) | eligible | one centerline swept `LoftGeometry` fin (LE sweeps aft w/ height) + 2 split rudder/speed-brake panels REVOLUTE on the swept hinge. **Planar Boundary Form** |
| `straight_fin` | forked_anchor | `rec_space_shuttle_var_straight_fin` | L95-L112 | eligible | one straight-tapered near-rectangular fin (unswept LE) + split rudder on the near-vertical hinge. **Planar Boundary Form** |
| `twin_tail` | forked_anchor | `rec_space_shuttle_var_twin_tail` | L92-L102 (stations), L431-L490 (twin fin + rudder build) | eligible | ① skeleton: 2 smaller swept fins on the aft deck (fused visuals at ±Y), each with 1 rudder REVOLUTE on its swept hinge. |

### Slot D：landing_gear (parallel children on fuselage · ② joint type + ① multiplicity main_wheel_count)

Deployed tricycle gear, gear-down at q=0. Nose gear = strut (retract joint) +
steerable fork (REVOLUTE) + spinning wheels (CONTINUOUS); 2 main gear = strut
(retract joint) + spinning wheels (CONTINUOUS); 2 hinged nose gear doors
(REVOLUTE). (Main gear doors were dropped post-review: fully open at q=0 they
rendered as a loose flat panel hanging beside the strut rather than a
recognizable door, and no other geometry depended on them — see 审核记录.)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `revolute_gear` | forked_anchor (origin) | origin `...4400ecc9` | L601-L753 | eligible | strut retract joints are **REVOLUTE** (rotate up into the wells). Nose fork REVOLUTE steer, wheels CONTINUOUS, gear doors REVOLUTE. |
| `prismatic_gear` | forked_anchor | `rec_space_shuttle_var_telescoping_gear` | L138-L139, L613-L628, L701-L718 | eligible | ② joint type: strut retract joints are **PRISMATIC** (telescope straight up along +Z). 构造随关节类型改变：伸缩腿的活动件是**内活塞**，外筒(`*_gear_housing`)与撑杆是熔进 fuselage 的固定结构，活塞在筒内滑动。Fork steer + wheels + doors unchanged. |
| `main_wheel_count` 1/2 | forked_anchor | origin L710-L722 (2); `main_wheels_single` L710-L722 (1) | see §8 | eligible | wheels per main strut: 1 centered or 2 (inboard+outboard). multiplicity, ① moving parts. |

硬约束满足：airframe ③ 有两根 registered slot（hull_form 2 + wing_form 2）；
control_surfaces 2（源限降到 2，已说明）；tail 3；landing_gear 2（+ wheel mult）。
每个 candidate 有 forked_anchor + `model.py:Lx-Ly`。无 `world_knowledge_extrapolation`
candidate（全部离散结构轴均由真实样本支撑）。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel children + multiplicity)

```
airframe (root; fuselage: hull{blended|cylindrical} + wing{double|pure delta} + N engine bells)
   ├─[wing TE REVOLUTE(Y) / spine REVOLUTE(X) / aft REVOLUTE(Y); fused-visual anchors]→ control_surfaces (bay doors ×2 + body flap + elevons ×[2|4])
   ├─[fin TE swept-hinge REVOLUTE; fin fused as fuselage visual]→ tail (rudder ×[2|2])
   └─[gear-well REVOLUTE(Y)|PRISMATIC(Z) + fork REVOLUTE(Z) + wheels CONTINUOUS(X)]→ landing_gear (nose+2 main gear + 2 nose doors)
```

- **slot 顺序 / parent**：`airframe` is root, the only reused parent. `control_surfaces`,
  `tail`, `landing_gear` all parent their joints to `fuselage` directly (parallel
  children). All three declare only a `downstream` interface (re-export fuselage),
  so the assembler emits NO automatic chain joint; each module emits raw joints to
  the fuselage, exactly as the 5-star sources do.
- **接口点位**：bay doors → sill hinge line `(BAY_X_MID, ±SILL_Y, SILL_Z)`; body
  flap → aft hinge `FLAP_HINGE`; elevons → wing TE `(ELEVON_HINGE_X, ±y, ELEVON_Z)`;
  rudder → fin TE swept hinge line; gear struts → well tops `(gear_x, ±y, top_z)`.
- **跨 slot joint type/axis/range**：bay door REVOLUTE(x, 0..2.6); body flap
  REVOLUTE(Y, -0.35..0.45); elevon REVOLUTE(Y, -0.6..0.4); rudder REVOLUTE(swept
  axis, -0.45..0.85 / ±0.55 twin); gear strut REVOLUTE(Y, 0..`GEAR_REVOLUTE_UPPER`)
  | PRISMATIC(+Z, 0..`gear_deploy`)（两者 q=0 均为放下，正向行程为收起）; fork
  steer REVOLUTE(Z, ±0.35); wheels CONTINUOUS(X).
- **互斥/派生**：`main_wheel_count` and `engine_count` are free multiplicity axes;
  hull_form × wing_form × elevon × tail × gear × counts are all orthogonal (no
  gating). Fin is a fused visual in every tail candidate (Rule 1).

## 每槽位 Module Emits / Interfaces

### Slot A / module airframe (blended|cylindrical × double_delta|pure_delta × N engines)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fuselage` (single root part) | origin L243 |
| visuals | `hull` (cadquery loft w/ bay cavity cut) + `belly_tiles`/`nose_cap`/`chine_band` + `forward_rcs_panel` + RCS ports + `window_pane_*` + `crew_hatch_ring` + `payload_bay_floor`/rails/sills + livery (`flag_*`/`insignia_roundel`/`name_strip`) + `{side}_wing`/`_leading_edge`/`_underside` + `{side}_oms_pod`/`_oms_nozzle` + `base_heat_shield` + `main_engine_nozzle_i`/`main_engine_throat_i` (N) | origin L245-L488 |
| internal joints | none (root, static body) | — |
| downstream interface | `fuselage` part, `hull` visual, `positive_z` face, anchor `(BAY_X_MID,0,SILL_Z)` (informational; children wire manually) | — |

### Slot B / module single_elevon | split_elevon
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{side}_payload_bay_door` ×2, `body_flap`, `{side}_elevon` (single) or `{side}_{seg}_elevon` (split) | origin L493,L584,L554 |
| visuals | door arc-loft shells, body-flap box, elevon `LoftGeometry` slabs | origin L500,L585,L570 |
| internal joints | `fuselage_to_{side}_payload_bay_door` REVOLUTE, `fuselage_to_body_flap` REVOLUTE, `wing_to_{side}[_{seg}]_elevon` REVOLUTE(Y) | origin L503-L511,L591-L599,L573-L581 |
| upstream interface | **none declared** (parallel-children; parents joints to `fuselage`) | — |
| downstream interface | re-export fuselage (passthrough) | — |

### Slot C / module swept_fin | straight_fin | twin_tail
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{side}_rudder_panel` ×2 (single fin) or `tail_fin_{i}_rudder` ×2 (twin) | origin L523; twin L466 |
| visuals (on fuselage) | `vertical_stabilizer` + `fin_leading_edge` (single) or `tail_fin_{i}_body`/`_leading_edge` ×2 (twin) — fused fuselage visuals (Rule 1) | origin L441; twin L440 |
| internal joints | `fin_to_{side}_rudder_panel` REVOLUTE(swept axis) or `tail_fin_{i}_to_rudder` REVOLUTE | origin L541; twin L481 |
| upstream interface | **none declared** | — |
| downstream interface | re-export fuselage | — |

### Slot D / module revolute_gear | prismatic_gear (× main_wheel_count)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nose_gear_strut`, `nose_gear_fork`, `{side}_nose_wheel` ×2; `{side}_main_gear_strut` ×2, main wheels (1 or 2 per strut); `{side}_nose_gear_door` ×2 (main gear doors dropped post-review) | origin L603-L753 |
| visuals | revolute: 整条腿 strut tube+piston+braces 都在活动 part 上；prismatic: 只有 piston(+axle) 在活动 part 上，`*_gear_housing`/`*_gear_drag_brace`/`*_gear_side_brace` 熔进 fuselage；两者共用 `WheelGeometry`+`TireGeometry` wheels 与 box nose-gear-door panels | origin L604-L753 |
| internal joints | strut retract REVOLUTE(Y, 0..`GEAR_REVOLUTE_UPPER`) or PRISMATIC(+Z, 0..`gear_deploy`)；两者均 **gear-DOWN at q=0，正向行程一律为收起**；fork REVOLUTE(Z) steer; wheel CONTINUOUS(X); nose-gear-door REVOLUTE | origin L613-L753; prismatic telescoping_gear L613-L718 |
| 行程如何定 | prismatic 行程不是先挑一个数再去 mask 撞到的东西，而是从结构反解三条上限取交集：活塞冠部须留在筒内、收起后轮子须停在筒下方、收起后 nose fork 须让开筒口 → `gear_deploy ∈ [0.50, 0.75]`。revolute 行程 `GEAR_REVOLUTE_UPPER=0.7` 同理取在摆起后轮子仍让开机翼下表面处。 | 本次修复 |
| upstream interface | **none declared** | — |
| downstream interface | re-export fuselage | — |

活动件语义：bay/gear/rudder/elevon/flap 关节都是真实活动件。不动细节（fin、
OMS pod、engine bell、TPS skin、livery、windows、bay interior）写成 `fuselage`
part visual，非独立 FIXED part（Rule 1）。gear strut / wheel captured pivots 用
element-scoped / part-scoped `allow_overlap`（Rule 2 captured-pin exception，与原始
样本一致）；joint origin 落在真实 fuselage/strut 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `hull_form` | enum | blended / cylindrical | blended | choice | procedural sampler | Slot A |
| `wing_form` | enum | double_delta / pure_delta | double_delta | choice | procedural sampler | Slot A |
| `payload_bay_layout` | enum | standard_bay / satellite_deployer / laboratory_module | standard_bay | choice | procedural sampler | Slot A |
| `control_module` | enum | single_elevon / split_elevon | single_elevon | choice | procedural sampler | Slot B |
| `tail_module` | enum | swept_fin / straight_fin / twin_tail | swept_fin | choice | procedural sampler | Slot C |
| `gear_module` | enum | revolute_gear / prismatic_gear | revolute_gear | choice | procedural sampler | Slot D |
| `engine_count` | int | {2,3,4} (obs: 2/3/4) | 3 | independent | weighted `{3:0.5,2:0.25,4:0.25}` | origin/eng2/eng4 |
| `main_wheel_count` | int | {1,2} (obs: 1/2) | 2 | independent | weighted `{2:0.7,1:0.3}` | origin/single |
| `palette_style` | enum | 4 colorways | nasa_endeavour | choice | procedural sampler | ⑥ |
| `fuse_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform, clamp; scales whole airframe about origin | origin L48 |
| `wing_span_scale` | float | [0.92, 1.10] | 1.0 | independent | uniform, clamp; scales wing spanwise stations | origin L74-82 |
| `gear_deploy` | float | [0.50, 0.75] | 0.65 | conditional | prismatic piston retract stroke（行程上限由结构解出，见 Slot D）；revolute uses fixed 0..`GEAR_REVOLUTE_UPPER` | telescoping L138 |
| `elevon_up` | float | [0.30, 0.45] | 0.40 | independent | elevon TE-up REVOLUTE upper | origin L580 |
| (—) | constraint | — | — | inequality | wing stations stay monotone in |y| (LE ordering) under `wing_span_scale`; scale clamp keeps loft non-self-intersecting | wing loft |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

### 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 45 s** (hang-guard `--compile-timeout 120`).
Geometry is dominated by: one cadquery boolean bay-cavity cut on the hull loft
(~20 sections at <=32 seg), several `superellipse_side_loft` skins (belly/nose/
chine/OMS at 36-48 seg), wing/fin `LoftGeometry` lofts, N `LatheGeometry` engine
bells (36 seg), and the tricycle wheels. Wheels are the heaviest: build ONE nose
`WheelGeometry+TireGeometry` mesh set and ONE main set, share across all wheel
parts (2 mesh sets, not 6). Both wings share one loft path; both OMS pods share
one profile. No per-seed re-tessellation growth. Expect 20-40 s/seed; if over,
drop superellipse `segments` (48->36->32) and bell `segments` first.

## Multiplicity / Copy Logic

**三根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp）：

### 轴 1 — `engine_count`（SSME 喷管数）
- `count_param`: `engine_count`; `N_range` product `[2,4]`, test `{2,3,4}`; sampling
  domain 加权 `{3:0.5, 2:0.25, 4:0.25}` (原型 3 偏多)。
- copied object: fused `main_engine_nozzle_i` bell (`LatheGeometry` profile) +
  `main_engine_throat_i` dark disc, laid out on the aft base heat shield per the
  per-count mount table. **Fused fuselage visuals, not parts, not joints** (bells
  do not articulate) → ④ form-detail count, covered not counted.
- naming: `main_engine_nozzle_{i}` / `main_engine_throat_{i}`; placement: per-count
  `engine_mounts` table (origin 3 = 1 top + 2 bottom; 2 = side-by-side; 4 = 2x2).
- source/gating: origin L472-473 (3), main_engines_2 L473 (2), main_engines_4 L472-477 (4). No gating.

### 轴 2 — `main_wheel_count`（每主起落架轮数）
- `count_param`: `main_wheel_count`; `N_range` `[1,2]`, test `{1,2}`; sampling 加权
  `{2:0.7, 1:0.3}`.
- copied object: `WheelGeometry+TireGeometry` wheel **part** on the main axle,
  1 centered (`woff=0`) or 2 (`woff=+-0.33`), each on its own CONTINUOUS spin joint.
  → ① moving-part multiplicity.
- naming: `{side}_main_wheel` (1) or `{side}_{outboard|inboard}_main_wheel` (2);
  joint `{side}_main_axle_to[_{wname}]_wheel` CONTINUOUS(X).
- source/gating: origin L710-722 (2), main_wheels_single L710-722 (1). No gating.

### 轴 3 — 副翼分段数（via `control_module`）
- `single_elevon` = 1 segment/wing (2 parts), `split_elevon` = 2 segments/wing
  (4 parts); each segment a REVOLUTE part. Encoded as the control_surfaces module
  choice (not a raw int) → ① moving-part multiplicity registered as `control_surfaces`.
- source: origin L551-581 (single), elevons_split L552-596 (split).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | elevon single(2 parts)↔split(4 parts) (origin/elevons_split, forked_anchor); tail single-fin(2 rudder parts)↔twin(2 fins+2 rudders) (origin/twin_tail); main_wheel_count 1↔2 (origin/single). 全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：engine_count{2,3,4}、main_wheel_count{1,2}、elevon segments{1,2}。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | gear strut retract REVOLUTE(Y)(origin) ↔ PRISMATIC(Z)(telescoping_gear)。全部 forked_anchor；两种类型都在 sweep 出现。(rudder REVOLUTE / wheels CONTINUOUS / fork REVOLUTE 是各 candidate 的固定语义。) |
| ③ 主体形态/功能家族 | 图&关节不变，换核心 part 可识别形态或功能原型 | 有 | **四处登记进 slot_choices**：hull_form — blended lifting body(origin) / near-circular barrel(cylindrical_fuselage), form_subtype=Volumetric Envelope Form; wing_form — double-delta(origin) / pure-delta(delta_wing), form_subtype=Planar Boundary Form; payload_bay_layout — standard cargo bay / satellite deployment truss / laboratory pressure module, form_subtype=Functional Payload Interface; tail fin — swept(origin) / straight(straight_fin), form_subtype=Planar Boundary Form。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | black TPS `belly_tiles`/`nose_cap`/`chine_band`, `forward_rcs_panel` + RCS ports, `window_pane_*`, `crew_hatch_ring`, livery `flag_*`/`insignia_roundel`/`name_strip`, engine bell count — 均为 `fuselage` part visual，随 ③(hull/wing 形态)/⑤(fuse_scale) 派生位置。source_type=record_only(origin)。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：fuse_scale[0.90,1.12]、wing_span_scale[0.92,1.10]、elevon_up[0.30,0.45]、gear_deploy[0.50,0.75](conditional prismatic)。关节运动包络（每个非-continuous joint）：bay door REVOLUTE axis ±x，open up/outboard [0, 2.6]; body flap REVOLUTE(Y) [-0.35, 0.45]; elevon REVOLUTE(Y) [-0.6, elevon_up]; rudder REVOLUTE(swept) [-0.45, 0.85] (twin ±0.55); gear strut REVOLUTE(Y)[0,`GEAR_REVOLUTE_UPPER`] or PRISMATIC(+Z)[0,gear_deploy]; fork REVOLUTE(Z) [-0.35, 0.35]; wheels CONTINUOUS. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)` (多关节 6+，降到 32); targeted `ctx.pose` — bay door swings up+outboard, elevon TE up, body flap up, rudder split, gear retract/telescope, fork steers wheels。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal/glass；配色 4 colorway：`nasa_endeavour`(white TPS + black underside + NASA livery)、`buran_white`(cool white)、`midnight_black`(dark ops)、`bare_aluminum`(silver metal skin)。材质大类覆盖 >= ceil(0.5×4)=2 (painted+metal 均出现)。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 blended/cylindrical 两种 hull、double/pure
delta 两种 wing、swept/straight/twin 三种 tail、2/3/4 engines、single/dual main
wheels、single/split elevons、revolute/prismatic gear、材质配色多样、所有活动关节
全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
hull 2 × wing 2 × payload_bay_layout 3 × control 2 × tail 3 × gear 2 × engine 3 × main_wheel 2 = **864**。

其中非 N 结构槽位的 `core_domain` 为
2 × 2 × 3 × 2 × 3 × 2 = **144**；加入 `engine_count{2,3,4}` 和
`main_wheel_count{1,2}` 两根 N 轴后，`raw_domain = 144 × 3 × 2 = **864**`。

理由：真实结构词汇仍然收敛——所有样本共享同一「winged orbiter + control surfaces + gear」
cell，但 payload-bay layout 增加了可识别的承载/接口功能轴，不依靠颜色、连续尺寸或装饰
凑数。
不硬凑组合空间（质量红线：不反推上游变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 hull_form、wing_form、payload_bay_layout、control_module、tail_module、gear_module、engine_count、
main_wheel_count、palette、连续 scale。seed 0 pinned 到 origin 母本组合（blended +
double_delta + single_elevon + swept_fin + revolute_gear, 3 engines, dual wheels,
nasa_endeavour）作为 documented regression anchor（sparse override）。random sweep
`0-15`(fast) -> `0-35`(final) -> corner。

Topology target：真实 `core_domain = 144`、`raw_domain = 864`（见上），为新增的
payload-bay 承载/接口轴；report-only。

Controlled local parameterization：`fuse_scale`、`wing_span_scale`、`elevon_up`、
`gear_deploy`(conditional)。全部在 `resolve_config` clamp / 解析；不破坏挂点、joint
origin、multiplicity。连续尺寸契约：先采 independent → conditional 解析 gear_deploy。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 airframe->control->tail->gear，均匀 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全正交自由组合（无非法组合）；fin 恒为 fused visual | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 4 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| hull_form | 2 | yes | no | blended/cylindrical（③ Volumetric Envelope） |
| wing_form | 2 | yes | no | double/pure delta（③ Planar Boundary） |
| control_surfaces | 2 | yes | no | single/split elevon（源限降到 2） |
| tail | 3 | yes | yes | swept/straight/twin |
| landing_gear | 2 | yes | no | revolute/prismatic |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ engine_count/main_wheel_count/wing_form axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- controlled local scales clamped; cannot break appendage mount points, joint origin honesty, or multiplicity
- fin is always a fused fuselage visual (Rule 1); only rudder panels are parts
- captured gear-strut / wheel-axle overlaps are part-scoped `allow_overlap` (mesh-split component names unstable, same as origin), proven by stance/retraction pose checks
- key joints have expected type/axis/range: gear strut REVOLUTE(Y) or PRISMATIC(Z); rudder/elevon/flap/bay-door REVOLUTE; fork REVOLUTE(Z); wheels CONTINUOUS(X)
- copied `main_engine_nozzle_i` / main wheels / elevon segments follow naming + placement policy
- `run_astronomy_space_shuttle_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Elevon / rudder / body flap deflected pose collides with the wing/fin/hull at a joint extreme → shrink the range or seat the hinge inside the cove (element-scoped allow_overlap on the cove only, as origin).
- Gear retracts up and the strut/wheels punch through the hull at the retracted extreme → cap the retract range; keep gear-down at q=0 so the closed pose is clean.
- Bay doors opened past the sill collide with each other at the spine → keep the closed-seam gap; open direction up/outboard only.
- Fin modeled as a FIXED separate part instead of a fused visual (Rule 1 violation) → fuse the fin into `fuselage`, hinge the rudder to the fuselage.
- Downgrading the hull `mesh_from_cadquery` loft / wing `LoftGeometry` / bell `LatheGeometry` / `TireGeometry` wheels to crude Box/Cylinder placeholders (Rule 3 violation).
- Twin-fin rudder hinge origin off the fused fin visual → put the origin on the fin TE hinge line in fuselage frame.
- Per-seed re-tessellation or per-wheel rebuild blowing the compile budget → share wheel/OMS/bell meshes.

## 与相邻类别的边界

- 不该混入：**Astronomy / Return capsule**（钝头弹道再入体，无翼/尾/起落架/控制面拓扑）。
- 不该混入：**Astronomy / Rocket engine**（裸推力室 + 单喷管 + gimbal，无机身/翼/起落架）。
- 不该混入：一架普通喷气客机/战斗机（无 TPS 黑腹、无 OMS pod、无 payload bay、无再入体身份特征）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | mechanically ready — `uv run articraft template check Astronomy_Space_shuttle` 全链路通过：`random-16` 16/16、`random-36` 36/36、`corner` 12/12，整体 `verdict=pass`、`completion_status=legacy_compatible`（mechanical_hash `7c10cecc962ffeab15bf886714771825ca60823d2ac52663b1018ea50597d460`，2026-08-01，post landing-gear rework）。此前 `template_sweep_state.json`（2026-07-11）记录的 `fail_if_part_contains_disconnected_geometry_islands` 连续失败在当前 template.py 上无法复现，属于早于本次复核版本的历史失败，sweep-state 缓存条目已过期，不再是阻塞项。 |
| reviewer notes | 全部 9 变体与母本均在 PATHFINDER 确认池内且 5 星；无 world_knowledge_extrapolation candidate；fin 按 Rule 1 从 twin_tail 源的 FIXED part 改为 fused fuselage visual（rudder 直接铰接 fuselage）。9 个种子的渲染抽查（hull blended/cylindrical、wing double/pure delta、tail swept/straight/twin、gear revolute/prismatic、elevon single/split、engine 3/4、main_wheel 1/2、4 种涂装组合）外形清晰可辨、无浮动几何/穿模；判断当前 6 轴多样性已有充分源材料支撑，未额外新增候选。用户复核渲染图后指出主起落架旁的黑色舱门在 q=0 全开姿态下看起来像一片悬空的板，不像门；已删除 `{side}_main_gear_door` part + `fuselage_to_{side}_main_gear_door` joint 及其对应 overlap 声明（保留 nose gear door、两条 main gear strut 本身不变），删除后重跑 random-16/36/corner 全部重新通过。<br><br>**起落架返工（2026-08-01，用户报告"gear 很容易穿模机翼"）**：根因是 prismatic 分支把**整条腿**当活动件，再补一根 `*_strut_upper_slide` 顶杆去维持"全行程都有支撑"——那根杆固定伸到 trunnion 上方 `0.45+gear_deploy`（世界 z≈5.4-6.0），而主起落架站位在机翼下（翼面顶 ≈3.9），于是直接从翼面穿出，就是用户截图里机翼上方那根竖管。修复按"关节类型决定构造"重做：<br>① prismatic 改为真实伸缩腿——外筒 `*_gear_housing` 与撑杆熔进 fuselage 作固定结构，活动件只剩内活塞(+轮轴)，活塞永远滑在筒内，结构上不可能高过筒顶；顶杆 hack 删除。revolute 仍是整条腿绕 trunnion 摆，两种构造真正不同。<br>② 行程方向统一：两种关节 q=0 均为放下（轮子触地），正向一律为收起（prismatic 轴由 `(0,0,-1)` 改为 `(0,0,+1)`；原来正向是继续往下顶，会把轮子压到跑道以下）。<br>③ 行程范围由结构反解而非拍脑袋：取"活塞冠留在筒内 / 收起后轮子停在筒下 / 收起后 nose fork 让开筒口与撑杆"四条上限的交集 → `gear_deploy ∈ [0.45,0.70]`。<br>④ 修掉一个连带的真实建模错误：prismatic 行程是长度却**没有乘 `fuse_scale`**，在 `fuse_scale≈0.92` 的种子上相对行程偏大 8%，正是 seed 19/25 在 34/36 那轮失败的原因；已改为 `s * gear_deploy`（revolute 是角度，不需缩放）。<br>⑤ 新增三条守卫检查（收起后活塞仍在筒内、收起后主轮仍低于翼下表面、轮子确实向上移动），这类穿模以后会在 authored test 层直接失败而不是靠人眼发现。重跑 random-16 16/16、random-36 36/36、corner 12/12。 |

## 模板实现备注（可选）

- 全部 appendage 挂点从 origin 常量 (BAY/SILL/ELEVON/FIN/gear) 派生并乘 `fuse_scale`；single-sourced 在 `ResolvedConfig`（Contract 3c）。
- 复用 origin 的几何 helper（`_superellipse_wire`/`_airfoil_loop`/`_fin_loop`/`_door_arc_loop`/`_tube`）逐字移植，保 primitive 家族（Rule 3）。
- 两套 wheel mesh（nose/main）各建一次，跨全部 wheel part 复用；两翼共享 loft；两 OMS pod 共享 profile；N bell 共享 profile —— 保编译预算。
- captured gear-strut / wheel-axle overlap 用 part-scoped `allow_overlap`（mesh 自动拆分组件名不稳定，与 origin L788-812 一致）；其余 cove-seated 控制面用 element-scoped。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：airframe root 声明 downstream；control/tail/gear 只声明 downstream(re-export fuselage) -> 无自动 chain joint，各模块发原始 joint 到 fuselage（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | blended+double_delta+single_elevon+swept_fin+revolute_gear (母本) | origin `...4400ecc9` | L1-L976 | 全 part tree、hull/wing/fin/skins/livery、控制面/起落架 joint 语义、全部 test 语义 |
| S2 | A ③ | cylindrical hull | `rec_space_shuttle_var_cylindrical_fuselage` | L245-L261 | 近圆机身截面表 |
| S3 | A ③ | pure_delta wing | `rec_space_shuttle_var_delta_wing` | L73-L82 | 纯三角翼平面站表 |
| S4 | C ③ | straight_fin | `rec_space_shuttle_var_straight_fin` | L95-L112 | 直立锥形尾翼站表 + hinge |
| S5 | C ① | twin_tail | `rec_space_shuttle_var_twin_tail` | L92-L102, L431-L490 | 双尾翼 + 每翼 rudder |
| S6 | B ① | split_elevon | `rec_space_shuttle_var_elevons_split` | L552-L596 | 内/外分段副翼 |
| S7 | A mult | engine_count=2 | `rec_space_shuttle_var_main_engines_2` | L473 | 双喷管 mount |
| S8 | A mult | engine_count=4 | `rec_space_shuttle_var_main_engines_4` | L472-L477 | 四喷管 2x2 mount |
| S9 | D mult | main_wheel_count=1 | `rec_space_shuttle_var_main_wheels_single` | L710-L722 | 单主轮 |
| S10 | D ② | prismatic_gear | `rec_space_shuttle_var_telescoping_gear` | L138-L139, L613-L718 | PRISMATIC 伸缩起落架 |
