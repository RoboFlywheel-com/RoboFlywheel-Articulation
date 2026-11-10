# Modular Spec — conduit_bender

## 元信息
| 项 | 值 |
|---|---|
| slug | `conduit_bender` |
| registry key / module | `Electrical_Wiring_Conduit_bender` (file `agent/templates/Electrical_Wiring_Conduit_bender.py`) |
| template path | `agent/templates/Electrical_Wiring_Conduit_bender.py` |
| build/test stem | `conduit_bender` (`build_conduit_bender`, `run_conduit_bender_tests`) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (form-family branch + parallel children off a grounded root; hand-branched like `Science_Capsule`, not the `assemble()` chain) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (2 origins S1/S2 + 5 forks) |
| source_index_policy | only adopted module sources are indexed below |

Sources (abbrev):
- **S1** `rec_use-...228873_1dc8f80a` rev_000002 — yellow floor tripod stand, welded yoke, black-cast curved shoe (annular sector web + channel + lips), single long lever + rubber grip, foot pedal, hook lip, degree ticks, galvanized conduit arc. `model.py:184-360`.
- **S2** `rec_use-...228545_39453ad4` rev_000001 — blue-cast handheld lever bender, cast-in white degree scale, foot pedal + serrated tread, single swing arm w/ pressure roller, copper sample conduit (spline tube). `model.py:116-360`.
- **hand_emt** `rec_conduit_bender_var_hand_emt_bender` — cast head + long straight pull handle + foot-peg step; the seated conduit (workpiece) is the moving part, pivots about shoe-groove center. `model.py:177-392`.
- **hydraulic_ram** `rec_conduit_bender_var_hydraulic_ram_bender` — tubular floor frame + hydraulic ram (PRISMATIC former die) + revolute pump handle + fixed reaction rollers; conduit fixed. `model.py:110-458`.
- **two_handle_scissor** `rec_conduit_bender_var_two_handle_scissor` — S2 shoe + TWO revolute handles (roller + forming), scissor convergence. `model.py:274-449`.
- **ratchet_bender** `rec_conduit_bender_var_ratchet_bender` — S2 shoe + revolute ratchet drive (toothed sector) + revolute pump/pawl handle (2 revolute). `model.py:273-457`.
- **bench_clamp_mount** `rec_conduit_bender_var_bench_clamp_mount` — S2 shoe but base swapped to a C-clamp bracket + screw (replaces foot pedal). `model.py:186-260`.

## 核心身份

A pipe/conduit bender: the tool an electrician uses to put controlled bends in EMT/rigid electrical conduit. Its identity spine = a **curved forming SHOE** (an annular-sector grooved former with a U-channel + raised side rims that cradle the tube) + a **REVOLUTE bending joint** about the shoe-groove center + a **lever/handle** that drives the bend, plus a hook lip and a printed **degree scale**. A galvanized/copper **sample conduit** is seated in the groove. The category is **form-dominated**: it spans four distinct ③ Primary-Form families (floor tripod stand, compact handheld cast lever, single-long-handle hand EMT bender, hydraulic ram/frame bender), which is the dominant diversity axis.

Neighbor boundary — must NOT drift into: pliers / two-jaw gripping hand tools (a conduit bender forms a tube against a fixed curved shoe, it does not cut/grip between two jaws), wire strippers / crimpers (no cutting edges or die pockets), or a plain pipe wrench. The curved grooved shoe + degree scale + seated conduit keep it identifiably a bender.

## 槽位 + 候选模块表

### Slot A：form_family  （③ Primary Form Family — PRIMARY / form-dominated main axis）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `floor_tripod` | forked_anchor | S1 | L199-360 | Volumetric Envelope Form (tall splayed A-frame stand envelope) | eligible | root=`frame` (tripod legs+yoke+socket+labels) -> REVOLUTE bend -> `bender_head` (curved shoe+lever fused+pedal+hook+ticks) -> FIXED `conduit`; 1 movable joint |
| `handheld_lever` | forked_anchor | S2 | L119-360 | Volumetric Envelope Form (compact flat cast disc body) | eligible | root=`shoe_head` (curved shoe+scale+hook+base_mount) -> REVOLUTE bend -> `lever` (Slot C) ; `shoe_head` -> FIXED `conduit`; 1-2 movable joints |
| `hand_emt` | forked_anchor | hand_emt fork | L190-392 | Planar Boundary Form (one long straight-handle profile + head) | eligible | root=`bender` (curved shoe + long straight handle + foot-peg fused) -> REVOLUTE bend -> `conduit` (workpiece pivots about shoe center); 1 movable joint |
| `hydraulic_ram` | forked_anchor | hydraulic fork | L129-458 | Macro Surface Construction (boxy machine frame + cylinder + rollers reads as a machine) | eligible | root=`frame` (floor frame+rollers+cylinder) -> PRISMATIC `ram` (former die) + REVOLUTE `pump_handle` ; `frame` -> FIXED `conduit`; 2 movable joints |

All four keep the identity trio (curved annular-sector shoe/former groove, a real revolute bending drive, seated conduit) but present genuinely different part trees / root coordinates -> branch the build on this value.

### Slot B：base_mount  （grounding layer; conditionally gated by Slot A）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tripod_stand` | forked_anchor | S1 | L202-213 | eligible when form=floor_tripod | splayed floor rails + 4 A-frame legs (`_cylinder_between` loop) + 2 cross braces + top socket |
| `foot_pedal` | forked_anchor | S2 | L186-204 | eligible when form=handheld_lever | blue cast foot pedal + serrated galvanized tread + `tread_tooth_{i}` loop |
| `bench_clamp` | forked_anchor | bench_clamp fork | L188-260 | eligible when form=handheld_lever | C-clamp neck/flange/spine/jaws + screw + T-handle + `clamp_bolt_{i}` loop (replaces foot pedal) |
| `foot_peg_step` | forked_anchor | hand_emt fork | L305-323 | eligible when form=hand_emt | cross foot-peg tube + `foot_peg_bracket_{i}` loop + anti-slip pad |
| `floor_frame` | forked_anchor | hydraulic fork | L131-145 | eligible when form=hydraulic_ram | tubular floor frame rails + splayed legs + cross braces + platform beam |

base_mount is a real 2-candidate free choice only inside `handheld_lever` (`foot_pedal` / `bench_clamp`); the other three families force their own physically-correct base. Across the sweep >=2 distinct base_mount values realize (report-only diversity satisfied).

### Slot C：lever_config  （② joint-type / drive axis; conditionally gated by Slot A）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 (joints) |
|---|---|---|---|---|---|
| `single_long_lever` | forked_anchor | S1 | L271-274 | forced when form=floor_tripod | one long lever + rubber grip fused into `bender_head` (bend = the head/frame REVOLUTE) |
| `single_swing_arm` | forked_anchor | S2 | L274-359 | eligible when form=handheld_lever | 1 REVOLUTE `swing_handle` (bushing+socket+tube+grip+pressure_roller) about shoe axis |
| `two_handle_scissor` | forked_anchor | scissor fork | L274-449 | eligible when form=handheld_lever | 2 REVOLUTE handles (`roller_handle` +Y, `forming_handle` -Y) both swing = scissor |
| `ratchet_pump` | forked_anchor | ratchet fork | L276-457 | eligible when form=handheld_lever | 2 REVOLUTE: toothed `ratchet_drive` (bend) + short `pump_handle` (pawl drive) |
| `fused_pull_handle` | forked_anchor | hand_emt fork | L275-323 | forced when form=hand_emt | long straight pull handle fused to `bender`; bend = the conduit REVOLUTE |
| `ram_pump_drive` | forked_anchor | hydraulic fork | L308-400 | forced when form=hydraulic_ram | PRISMATIC ram former + REVOLUTE pump handle |

Cross matrix legality lives in gating (§9): the 3 multi-option lever configs are the free ② axis inside `handheld_lever`; each other family forces its physically-consistent drive.

### Slot D：shoe_radius_group  （⑤ continuous, template-side — NOT a discrete slot）

Continuous `shoe_scale` in `[0.85, 1.20]` interpolating large_rigid(S1, outer≈0.166-0.207) <-> small_emt(S2, outer≈0.158). Drives the annular-sector radii + conduit path radius + tick radius together (equation-locked, 保形). Not forked separately (per source map 排除项).

## 槽位图（slot graph）

pattern: mixed (form-family branch; within a branch a grounded root with parallel movable children)

```
form_family = floor_tripod:
    frame(root) --[REVOLUTE axis -Y @ (0,0,PIVOT_Z), captured yoke axle]--> bender_head(shoe+lever+hook+ticks)
    bender_head --[FIXED, seated-overlap]--> conduit

form_family = handheld_lever:
    shoe_head(root, + base_mount in {foot_pedal, bench_clamp}) --[FIXED]--> conduit
    shoe_head --[REVOLUTE axis -/+Y @ shoe center, captured pin]--> lever(Slot C)
        single_swing_arm : 1 child          two_handle_scissor : 2 children (+/-Y)
        ratchet_pump     : ratchet_drive + pump_handle (2 children)

form_family = hand_emt:
    bender(root, shoe+long handle+foot_peg) --[REVOLUTE axis -Y @ shoe center, captured collar]--> conduit(workpiece)

form_family = hydraulic_ram:
    frame(root, + rollers + cylinder) --[PRISMATIC axis +X]--> ram(former die)
    frame --[REVOLUTE axis -Y @ pump boss]--> pump_handle
    frame --[FIXED, seated on clamps]--> conduit
```

- Cross-slot interface: the **revolute bending pivot** is the shared spine seam in every branch (origin on the shoe-center hub / yoke axle / pump boss = real captured-pin/boss hardware, satisfying the flat 0.015 m articulation-origin baseline). base_mount fuses into the root part's visual set (parent.visual, not a joint). Slot C children mate at the pivot via captured-pin geometry (MatingContract omitted -> grandfathered, guarded by element-scoped `allow_overlap`, like `Stationary_Scissors`).
- Gated/derived: base_mount and lever_config candidates are gated by form_family.

## 每槽位 Module Emits / Interfaces

### Slot A / floor_tripod
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root), `bender_head`, `conduit` | S1 / L199,228,310 |
| internal joints | `frame_to_bender_head` REVOLUTE axis(0,-1,0) @ (0,0,PIVOT_Z); `head_to_conduit` FIXED | S1 / L341-358 |
| bend pivot | head `pivot_hub`/`axle_pin` (Y cylinders at head origin) captured in frame bushings | S1 / L265-266,218-219 |

### Slot A / handheld_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shoe_head` (root), `conduit`, + Slot C lever part(s) | S2 / L119,247,274 |
| internal joints | `shoe_to_conduit` FIXED; Slot C REVOLUTE joint(s) axis(0,-/+1,0) @ shoe center | S2 / L265-271,351-359 |
| bend pivot | shoe `pivot_pin` (Y cylinder at center) captured in lever `pivot_bushing` | S2 / L178-183,276-280 |

### Slot A / hand_emt
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bender` (root: shoe+long handle+foot_peg), `conduit` (moving workpiece) | hand_emt / L190,351 |
| internal joints | `bender_to_conduit` REVOLUTE axis(0,-1,0) @ shoe center | hand_emt / L378-390 |
| origin anchor | add small `pivot_collar` (Y cylinder) on conduit at center so AABB contains (0,0,0) and axis = collar centerline (fixes 0.015 origin baseline) | new (gotcha) |

### Slot A / hydraulic_ram
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (root), `ram`, `pump_handle`, `conduit` | hydraulic / L129,308,387,405 |
| internal joints | `frame_to_ram` PRISMATIC axis(1,0,0); `frame_to_pump` REVOLUTE axis(0,-1,0); `frame_to_conduit` FIXED | hydraulic / L426-456 |
| former | `ram` carries an annular-sector former die (groove floor + lips) — curved Mesh, not box | hydraulic / L338-375 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| form_family | enum | floor_tripod / handheld_lever / hand_emt / hydraulic_ram | — | choice | weighted procedural draw (§8/§9) | Slot A |
| base_mount | enum | tripod_stand / foot_pedal / bench_clamp / foot_peg_step / floor_frame | — | conditional | gated by form_family (§9) | Slot B |
| lever_config | enum | single_long_lever / single_swing_arm / two_handle_scissor / ratchet_pump / fused_pull_handle / ram_pump_drive | — | conditional | gated by form_family (§9) | Slot C |
| palette_style | enum | safety_yellow / industrial_blue / hydraulic_red / black_cast / galvanized_raw | safety_yellow | choice | `rng.choice(PALETTE_STYLES)` | ⑥ (all sources) |
| shoe_scale | float | [0.85, 1.20] | 1.0 | independent | uniform then clamp; scales shoe radii | S1 vs S2 radii |
| conduit_path_r | float | derived | — | equation | `= shoe_outer_r - groove_inset` | S1 L235-263 |
| tick_radius | float | derived | — | equation | `= shoe_outer_r * 0.90` (ticks hug the shoe face) | S1 L304-308 |
| handle_len_scale | float | [0.90, 1.15] | 1.0 | independent | scales lever/handle tube length | S1/S2 handles |
| (—) | constraint | — | — | inequality | seated conduit overlaps groove floor by <= tube radius (declared `allow_overlap`); posed lever grip stays clear of floor rails (floor_tripod) | S1 L434-466 |

## 7.5 编译预算 / compile budget
Self-declared budget: **<=14 s/seed**. Basis: sources compile in low-single-digit seconds; heaviest (hydraulic_ram) ~55 visuals incl. 5 annular-sector meshes + spline tubes. Tessellation tiers: annular-sector shoe/former **segments <= 56** (down from source 72/80), conduit/hook arc tubes **segments <= 56, radial_segments <= 16**, spline handle tubes **samples_per_segment <= 8, radial_segments <= 16**. Repeated sub-parts (ticks, ribs, teeth, legs, bolts) are small Box/Cylinder primitives in loops. One shared annular-sector helper reused across the shoe web/channel/lips. Sweep `--compile-timeout 120` is a 3x watchdog.

## Multiplicity / Copy Logic

- **No sampled template-level multiplicity axis.** No `*_count` is exposed to the sampler; core structure is fixed named parts per family.
- Repeated sub-parts ARE emitted by `for i in range(n)` + `name_{i}` + a shared helper (never copy-pasted N blocks): `degree_tick_{i}`, `cast_rib_{i}`, `tread_tooth_{i}`, `clamp_bolt_{i}`, `foot_peg_bracket_{i}`, tripod legs, `ratchet_tooth_{i}`. Counts fixed per family (④ decoration density), not a diversity axis.
- Gotcha applied: the S1 note about `rubber_foot_pad ×6` sharing one name — any duplicate-named loop parts are suffixed `_{i}`.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 4 part-joint 拓扑随 form_family 变：floor_tripod (frame->head->conduit, 1 mov) / handheld_lever (shoe->lever[+conduit], 1-2 mov) / hand_emt (bender->conduit, 1 mov) / hydraulic_ram (frame->ram + frame->pump[+conduit], 2 mov)。全 forked_anchor |
| └ multiplicity | 同构件 ×N | 无(采样) | 见 §8：无 sampled N；decoration 循环计数固定 per family |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE bend (all) + extra REVOLUTE (scissor 2nd, ratchet pump) + PRISMATIC ram (hydraulic) + FIXED conduit(seated). 轴主要 (0,-/+1,0)；ram (1,0,0)。每种随 lever_config/form gating 出现。forked_anchor: S2/scissor/ratchet/hydraulic |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有(主轴) | 登记 Slot A `form_family` ∈ {floor_tripod=Volumetric Envelope, handheld_lever=Volumetric Envelope(compact disc), hand_emt=Planar Boundary(long-handle), hydraulic_ram=Macro Surface(machine frame)}；全 forked_anchor；登记进 `slot_choices` |
| ④ 表面装饰 | 叠加表面细节 / 改装饰数 | 有 | degree ticks/scale plate, cast ribs, serrated tread teeth, warning-label stripes, ratchet teeth, clamp bolts — 均由宿主表面派生（radial ticks 置于 shoe 外缘固定半径面，随 `shoe_scale`/③ 家族 shoe 半径共形；派生顺序 ③->⑤->④）。source_type=record_only |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `shoe_scale`[0.85,1.20] 保形驱动 shoe/groove/conduit/tick 半径；`handle_len_scale`[0.90,1.15]。运动包络：bend REVOLUTE 轴(0,-/+1,0) (floor_tripod [-0.48,0.70], handheld [0,1.65], hand_emt [-0.09,1.05], scissor/ratchet 2 rev, hydraulic ram PRISMATIC [0,RAM_UPPER]+pump [0,0.70])。motion_test_plan: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + 每 movable joint 一条 targeted `ctx.pose(...)`；captured-pin overlaps element-scoped allow_overlap |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette_style，材质大类 = {painted_steel, cast_iron, galvanized_steel, warm_copper, black_rubber}（本类天然全金属+橡胶工具，如扳手）；配色 5 档 >= 3；覆盖 >= ceil(0.5×5)=3 材质大类 ✓ |

## 拓扑多样性审计

总组合数（合法）：floor_tripod(1×1) + handheld_lever(base 2 × lever 3 = 6) + hand_emt(1×1) + hydraulic_ram(1×1) = **9 离散拓扑**，× palette 5 × 连续 scale。form_family 4 全为不同 part tree。


seed_domain_policy：procedural_first。Procedural Sampling / Sweep Plan：`config_from_seed` 用 `random.Random(seed)`：(1) `form_family` weighted draw（handheld_lever 权重最高因内部组合最多，其余三家各占足够份额以在 0-35 全部出现）；(2) 依 form_family gate `base_mount`+`lever_config`（handheld 自由采样，其余 forced）；(3) 连续 `shoe_scale`/`handle_len_scale` 独立采样后 clamp；(4) `palette_style`=`rng.choice`。非法组合由 gate 排除（不会被采到）。无 regression override（seed=0 不特殊）。Topology target：9 离散 × palette/scale，1000-seed distinct 按 ≥300 富类别口径观察。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：`shoe_scale`（保形驱动 shoe/groove/conduit/tick 半径，equation-locked）、`handle_len_scale`（只改 lever tube 长度，不改 pivot 接口）。两者在 `resolve_config` clamp/派生；不破坏 captured-pin 接口或 conduit 座落 overlap。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted form_family -> gated base/lever -> independent scales -> palette | `slot_choices_for_seed` == build 选择 |
| compatibility matrix | handheld_lever: base in {foot_pedal,bench_clamp}, lever in {single_swing,two_handle_scissor,ratchet_pump}; floor_tripod->{tripod_stand,single_long_lever}; hand_emt->{foot_peg_step,fused_pull_handle}; hydraulic_ram->{floor_frame,ram_pump_drive} | 无非法组合装配 |
| controlled local variation | shoe_scale[0.85,1.20], handle_len_scale[0.90,1.15] clamped/derived | 比例变化不破坏 groove 配合/pivot 接口/座落 overlap |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial；0-999 maturity | contract failures; axis_realization |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| A form_family | 4 | yes | yes | 主轴，全 part-tree distinct |
| B base_mount | 5 (2 free in handheld) | yes | yes | conditional gated |
| C lever_config | 6 (3 free in handheld) | yes | yes | conditional gated |

## Validator

- `slot_choices_for_seed` returns implemented (form_family, base_mount, lever_config) tuples
- `config_from_seed` deterministic procedural sampling for all seeds incl. seed 0
- compatibility gating prevents illegal form×base / form×lever combos
- no regression overrides; not a curated modulo table
- `shoe_scale`/`handle_len_scale` clamped in `resolve_config`; cannot break groove-conduit fit or pivot interface
- every family emits: curved annular-sector forming shoe/former (Mesh, never Box), a real REVOLUTE bending joint, a seated conduit spline/arc tube, a printed degree scale
- captured-pin pivots: joint origin on hub/pin/collar hardware (<=0.015 m); element-scoped `allow_overlap`; conduit seated-overlap declared
- `run_conduit_bender_tests` runs baseline + `fail_if_parts_overlap_in_sampled_poses` + per-family targeted `ctx.pose(...)`

## Reject cases

1. Downgrading the curved shoe/channel/lips or former die from annular-sector Mesh to Box/Cylinder (Rule 3).
2. A boxy hook lip (S2 shipped a Box hook) — the hook must be a curved arc tube.
3. Missing revolute bending joint in any branch, or zero movable joints in a family.
4. Conduit floating (isolated part) — must seat with declared overlap contact or a pivot collar.
5. Pivot joint origin off the hub/pin centerline (>0.015 m) — hand_emt conduit pivot needs a `pivot_collar` at center.
6. Lever/handle 穿模 into floor rails / conduit / opposite handle mid-travel.
7. Palette not wired: a `.visual` hard-coding a color instead of `mats[role]`.
8. Duplicate visual names in a loop — suffix `_{i}`.

## 与相邻类别的边界

- 不该混入：pliers / 双钳手工具（弯管机把管压在固定曲面 shoe 上成型，非两钳口对夹；无剪切口）。
- 不该混入：wire stripper / crimper（无刃口、无压线 die 腔）。
- 不该混入：plain pipe wrench（无 grooved 曲面 shoe、无 degree 刻度、无 seated conduit）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | form-dominated; ③ form_family registered (4 candidates, all forked_anchor). base/lever conditionally gated by form. Hand-branched build (Science_Capsule style), captured-pin pivots grandfathered (Stationary_Scissors style). |

## 模板实现备注（可选）

- 共享 helper：`_annular_sector` (shoe web/channel/lips/former die), `_arc_tube` (conduit arc + curved hook), `_spline_tube` (handle/conduit), `_cylinder_between` (legs/braces/straight handle), `_add_radial_box` (ticks/ribs), `_emit_forming_shoe` (shared shoe group for the 3 manual families).
- Captured-pin overlaps needing element-scoped `allow_overlap`: pivot_pin<->pivot_bushing (handheld/scissor/ratchet), axle_pin<->pivot_bushing (floor_tripod), pivot_hub<->pivot_collar (hand_emt), piston_rod<->ram_cylinder_body + pump_boss<->pump_pivot_boss (hydraulic), conduit<->groove_floor (seated).
- MatingContract omitted on captured-pin revolute joints (grandfathered), guarded by flat 0.015 origin baseline + `allow_overlap`.
