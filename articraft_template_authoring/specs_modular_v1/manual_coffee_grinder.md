# manual_coffee_grinder — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `manual_coffee_grinder` |
| template path | `agent/templates/manual_coffee_grinder.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (multiple slots parent to a grounded body chassis) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | 3 origin anchors (001 / 002 / 003) + 9 forked_anchor variants (body_form×2, hopper×2, catch×2, drive×2, mount×1) |
| source_index_policy | only adopted module sources are indexed below |

Reading notes:

- `rec_picturex_0611__manual_coffee_grinder__001__png_...` (613 L): traditional French-style hand grinder — turned wooden grounds body, layered cast-metal mounting rings, open thin-walled funnel hopper, two-post frame with adjustment collar, straight forged crank arm on a vertical drive shaft, free-spinning turned wooden grip. Three revolute joints (collar +Z, crank +Z multi-turn, grip +Z continuous).
- `rec_picturex_0611__manual_coffee_grinder__002__png_...` (588 L): modern travel grinder — tall black-anodized fine-ribbed aluminum cylinder, screw-off bottom grounds bin (prismatic -Z), knurled adjustment collar under the bearing shell, top crank arm with wood knob. Four non-fixed joints (collar REVOLUTE +Z, bin PRISMATIC -Z, crank CONTINUOUS +Z, grip CONTINUOUS +Z).
- `rec_picturex_0611__manual_coffee_grinder__003__png_...` (655 L): boxy walnut cabinet mill — rounded rectangular wooden cabinet, front pull-out grounds drawer (PRISMATIC -Y), top adjustment collar, blackened-metal burr flange and hopper, top crank with turned wood knob. Same four-joint pattern with drawer PRISMATIC on -Y instead of -Z.
- `..._body_form_slim_travel_cylinder`: 003-family topology re-plumbed as a tall slim cylindrical wooden travel body (Volumetric Envelope Form change).
- `..._body_form_square_wood_box`: 002-family topology re-plumbed as a square walnut wooden box housing (Planar Boundary Form change).
- `..._hopper_open_bowl`: 001-family with a wider, gently curved bowl hopper (Volumetric Envelope Form change).
- `..._hopper_hinged_covered_hopper`: 002-family extended with a REVOLUTE hinged bean-cover lid on top of the hopper (adds a `hopper_lid` PART).
- `..._catch_pull_out_drawer`: 003-family with a pull-out drawer variation.
- `..._catch_threaded_cup`: 002-family with a threaded screw-off cup.
- `..._drive_folding_top_crank`: 001-family extended with a fold hinge between the drive shaft and the crank arm (adds a `fold_arm` PART hinged about -Y).
- `..._drive_side_crank`: 003-family with a *horizontal* drive shaft exiting the right face of the cabinet — crank shaft axis is world +X instead of +Z (② axis change).
- `..._mount_table_clamp`: 001-family with a cast C-clamp bracket + adapter ring + upper jaw pad + threaded clamp screw replacing the stacked hopper mounting rings (visual-only, adds no new joint).

Three body-form families cover the three source parents; every non-origin fork extends one of them. All families share the same slot graph: **grounded body → adjustment_collar (REVOLUTE +Z) + crank_shaft (REVOLUTE +Z or +X, multi-turn) + optional catch (PRISMATIC) + optional hopper_lid (REVOLUTE)**, with the grip parented to the crank (or fold_arm) via a CONTINUOUS joint. Multiplicity is absent (single burr, single crank, single grip).

## 核心身识

A **manual (hand-driven) coffee grinder**: a tabletop/handheld grinder consisting of a grounded body (wooden cabinet, turned wood column, anodized cylinder, wooden box, or slim travel column) that carries a top hopper for whole coffee beans, a burr / grinder chamber and its adjustment collar for grind size, and a hand crank that turns a vertical (or horizontal) drive shaft to grind beans; ground coffee falls into a captured grounds bin (integrated in the body, a pull-out front drawer, or a screw-off bottom cup). A free-spinning wooden or metal grip rides the crank pin so the operator can turn the mill continuously.

Category identity:

- one grounded body that also holds the *fixed* hopper geometry and the *fixed* upper burr carrier;
- one moving crank_shaft (revolute, multi-turn, around vertical +Z or side +X) with a free-spinning grip at its tip;
- one adjustment_collar (revolute +Z, small range) that sets burr gap;
- optional prismatic catch (front drawer or bottom cup) that removes to empty grounds;
- optional REVOLUTE hopper_lid on hinged variants.

Smaller than a `manual_grain_mill` (fits on a countertop, hopper ≤ 6 cm tall, no A-frame legs) but hand-driven, unlike an `electric_coffee_grinder`. Neighbor rejects: electric grinder (motor, no crank), pepper mill (no grounds bin, single-turn cap), decorative container (no non-FIXED joint).

## 槽位 + 候选模块表

Four parallel-child slots + one optional visual-only mount slot.

### Slot A: `body_form` — grounded body form family (Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `turned_wood_stack` | forked_anchor | `rec_picturex_0611__manual_coffee_grinder__001__png_...` (`picture/0611/manual_coffee_grinder/001.png`) + `..._mount_table_clamp` + `..._hopper_open_bowl` + `..._drive_folding_top_crank` | 001 L65-L275 (`build_object_model` body block; `_cq_annulus`, `_crank_arm_shape`) | eligible if compatible | Turned wooden lathe body with alternating warm/dark wood bands (grooves at lower foot and upper shoulder); flared foot at the base, straight storage wall, upper shoulder bead. `Volumetric Envelope Form` = *turned-lathe stack*. Serves as its own grounds bin (integrated). |
| `anodized_cylinder` | forked_anchor | `rec_picturex_0611__manual_coffee_grinder__002__png_...` (`picture/0611/manual_coffee_grinder/002.png`) + `..._catch_threaded_cup` + `..._hopper_hinged_covered_hopper` | 002 L34-L200 (`_build_hopper_shell` with micro-ribs, `_build_lid`, `_build_burr_chamber`) | eligible if compatible | Tall thin-walled black-anodized aluminum cylinder with dense horizontal micro-ribs on the outer wall; internal floor with a shaft passage separates the hopper from the burr chamber. `Volumetric Envelope Form` = *thin-walled ribbed cylinder*. |
| `wood_cabinet` | forked_anchor | `rec_picturex_0611__manual_coffee_grinder__003__png_...` (`picture/0611/manual_coffee_grinder/003.png`) + `..._catch_pull_out_drawer` + `..._drive_side_crank` | 003 L31-L258 (`_wood_body_shape`, drawer_recess visuals, top_mount_plate stack) | eligible if compatible | Boxy rectangular walnut cabinet with filleted vertical edges; drawer recess trim frames a front cavity; blackened-metal top mount plate + burr flange + burr chamber stack up to the hopper. `Planar Boundary Form` = *rounded rectangular cabinet*. |
| `square_wood_box` | forked_anchor | `..._body_form_square_wood_box` | full file (L37-L92 `_build_hopper_shell` square box) | eligible if compatible | Solid *square* walnut wooden box housing (no filleted edges); hollow interior with an internal floor. `Planar Boundary Form` = *square wood box* (a distinct planar boundary from `wood_cabinet`). |
| `slim_travel_cylinder` | forked_anchor | `..._body_form_slim_travel_cylinder` | full file (L33-L60 `_wood_body_shape` cylindrical body) | eligible if compatible | Tall slim cylindrical wooden travel body with a fused drawer landing on the -Y face; body height > 1.25 × diameter. `Volumetric Envelope Form` = *slim travel cylinder* (a distinct volumetric envelope from `turned_wood_stack`). |

All bodies expose:
- A top face at world z = `body_top_z` where the adjustment_collar seats and the crank_shaft joint originates.
- A front face at world y = `-body_half_depth` where a pull_out_drawer can exit (or a side face for slim_travel_cylinder).
- A bottom face at world z = 0 where a threaded_cup can be captured.

### Slot B: `drive` — the manual crank

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `top_crank_arm` | forked_anchor | 001 L291-L317 (`crank_shaft` part with `_crank_arm_shape`, `drive_shaft` cylinder, `grip_pin` + `handle_washer`); 003 L313-L349 (`crank` part with `shaft_shoulder` + `crank_arm` box + `shaft_cap`) | 001 L291-L317, 003 L313-L349 | eligible if compatible | Straight horizontal crank arm rigid to a vertical (+Z) drive shaft. `crank_shaft` REVOLUTE +Z multi-turn (±12π). Grip attaches at the arm tip via a CONTINUOUS +Z joint. |
| `folding_top_crank` | forked_anchor | `..._drive_folding_top_crank` (adds `fold_arm` PART hinged about -Y between crank_shaft and grip) | full file (L47-L86 `_fold_hub_shape`, L89-L127 `_crank_arm_shape` folding; L288-L354 crank + fold_arm parts + REVOLUTE fold joint) | eligible if compatible | Two-piece crank: `crank_shaft` carries a clevis fold_hub with two ears + hinge pin; `fold_arm` PART hinges upward about -Y (range 0..≈π/2) via a REVOLUTE joint; deployed (q=0) the arm sits horizontally, folded (q≈π/2) it stands upright for storage. Grip attaches to `fold_arm` (not `crank_shaft`). ①/② skeleton + joint change. |
| `side_crank_arm` | forked_anchor | `..._drive_side_crank` (L322-L389 crank part with drive_shaft along -X, shaft_shoulder along +X, arm_bracket + crank_arm along +Z; body_to_crank REVOLUTE +X) | full file | eligible if compatible | Horizontal drive shaft exits the +X face of the body. `crank_shaft` REVOLUTE +X multi-turn (±12π). Crank arm extends vertically (+Z from the shaft) then out radially; grip mounts at the arm tip via a CONTINUOUS +X joint. Distinct ② axis (crank axis is world +X rather than +Z). |

### Slot C: `catch` — grounds container

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `integrated_body` | forked_anchor | 001 L91-L127 (`grounds_bin` visual is the turned wooden body itself; no separate PART) | 001 L91-L127 | eligible if compatible | No separate catch part; the body's grounds_bin visual doubles as the storage compartment. No prismatic joint. |
| `pull_out_drawer` | forked_anchor | 003 L259-L302 (`grounds_bin` part with drawer_tray + drawer_front + drawer_knob), 003 L373-L386 (`body_to_bin` PRISMATIC -Y); `..._catch_pull_out_drawer` (extended drawer construction) | 003 L259-L386 | eligible if compatible | Front-loading drawer with tray + front panel + knob; PRISMATIC along -Y (world), range [0, 0.075..0.085]. Adds a `catch` PART. |
| `threaded_cup` | forked_anchor | 002 L245-L260 (`grounds_bin` part with `bin_cup` lofted mesh), 002 L361-L375 (`housing_to_grounds_bin` PRISMATIC -Z, range [0, 0.035]); `..._catch_threaded_cup` | 002 L245-L375 | eligible if compatible | Screw-off cup at the bottom of the body; PRISMATIC along -Z (world), short travel [0, 0.03..0.05] representing threaded disengagement. Adds a `catch` PART. |

### Slot D: `closure` — optional bean hopper lid

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_hopper` | forked_anchor | 001 L149-L185 (open funnel hopper visual on body, no lid); 002 L34-L56 (hopper_shell is topless) | 001 L149-L185, 002 L34-L56 | eligible if compatible | No separate hopper lid part; bean-loading opening is exposed. |
| `hinged_covered_hopper` | forked_anchor | `..._hopper_hinged_covered_hopper` (adds a `hopper_lid` PART hinged along +X on the hopper rim, REVOLUTE range [0, ≈100°]) | full file | eligible if compatible | Adds a `hopper_lid` PART hinged on the hopper rim; opens upward to reveal the bean loading opening. REVOLUTE +X. ①/② skeleton + joint change. |

### Slot E: `mount` — optional table clamp (visual-only)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `standalone` | forked_anchor | 001/002/003 defaults (no clamp bracket) | — | eligible if compatible | Body sits on a table. No clamp geometry. |
| `table_clamp` | forked_anchor (④ decoration; host-conformal) | `..._mount_table_clamp` (L204-L226 replaces hopper mounting rings with C-clamp bracket + adapter ring + upper jaw pad; L269-L275 threaded clamp screw with T-handle) | full file | eligible if compatible | Adds a set of visual-only clamp bracket geometry to the body (annular base plate, horizontal arm, C-spine, upper jaw pad, T-handle threaded screw). No new PART, no new joint. |

## 槽位图（slot graph）

pattern: `parallel_children` (multiple children mount directly to the grounded body chassis)

```
body (grounded root)
 ├──[REVOLUTE +Z at body_top_z + small_offset]──> adjustment_collar
 ├──[REVOLUTE +Z or +X at crank_axis (top or side)]──> crank_shaft
 │                                                        │
 │      [if folding_top_crank: REVOLUTE -Y at fold_hub]───┴──> fold_arm
 │                                                                │
 │            [CONTINUOUS crank_axis at grip_pin]──────────────────┴──> grip
 │
 ├──[PRISMATIC -Y or -Z at catch mount, if catch != integrated_body]──> catch
 │
 └──[REVOLUTE +X at hopper_rim, if closure = hinged_covered_hopper]──> hopper_lid
```

Interfaces:

- `body → adjustment_collar`: seat at world (0, 0, collar_z); axis +Z; motion_limits [-0.5, 0.5] rad; MatingContract on adjustment_seat visual pair.
- `body → crank_shaft`:
  - `top_crank_arm` / `folding_top_crank`: origin (0, 0, crank_axis_z_top); axis (0, 0, 1); REVOLUTE multi-turn ±12π.
  - `side_crank_arm`: origin (body_half_x, 0, crank_axis_z_side); axis (1, 0, 0); REVOLUTE multi-turn ±12π.
- `crank_shaft → fold_arm` (folding only): origin at the fold hub center (local frame of crank_shaft); axis (0, -1, 0); REVOLUTE [0, ≈π/2]. Captured hinge pin, mating omitted, guarded by element-scoped `allow_overlap`.
- `crank_shaft` (or `fold_arm`) `→ grip`: origin at the grip pin (local frame); axis parallel to the crank_shaft's rotation axis; CONTINUOUS. Captured on the grip pin, mating omitted, guarded by element-scoped `allow_overlap`.
- `body → catch` (if not integrated_body):
  - `pull_out_drawer`: origin at the front face; axis (0, -1, 0); PRISMATIC [0, 0.075..0.085].
  - `threaded_cup`: origin at the bottom face; axis (0, 0, -1); PRISMATIC [0, 0.030..0.050].
- `body → hopper_lid` (if hinged_covered_hopper): origin at the hopper rim rear edge; axis (1, 0, 0); REVOLUTE [0, ≈100°]. Hinge barrel captured, guarded by element-scoped `allow_overlap`.

## 每槽位 Module Emits / Interfaces

### Slot A / module `turned_wood_stack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (root, grounded) with visuals: turned_grounds_body (LatheGeometry), lower_wood_band, upper_wood_band, hopper_mount, mount_bead, bowl_support, hopper_shell (open funnel), hopper_rim, burr_mount, bearing_sleeve, burr_flange, spring_coil_[0..3], frame_post_[0..1], frame_bridge_[0..1], frame_fastener_[0..1], adjustment_seat | S1 / 001 L84-L275 |
| internal joints | none | S1 |
| upstream interface | none (grounded) | — |
| downstream interfaces | `adjustment_seat` face (z = collar_z on axis (0,0,1)), `bearing_sleeve` top (z = crank_axis_z on axis (0,0,1)) | S1 |

### Slot A / module `anodized_cylinder`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` with visuals: hopper_shell (annulus with micro-ribs), fixed_burr_carrier, lid_plate + shaft_bushing on top, adjustment_seat, hopper_shell_rim | S2 / 002 L34-L200 |
| downstream interfaces | Same schema as `turned_wood_stack` | S2 |

### Slot A / module `wood_cabinet`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` with visuals: wood_body (cadquery box with fillets + drawer cavity), drawer_recess_top/bottom/left/right, top_mount_plate, burr_base_flange, burr_chamber, hopper_shell (bowl), hopper_lid_visual (fixed decoration if closure=open_hopper), bearing_sleeve, collar_washer, plate_fasteners | S3 / 003 L31-L258 |
| downstream interfaces | Same schema | S3 |

### Slot A / module `square_wood_box`
| emits | Same as wood_cabinet but with a squared box outer shell (no fillets) | S3a |

### Slot A / module `slim_travel_cylinder`
| emits | Same as wood_cabinet but with a cylindrical outer shell + fused drawer landing on the -Y face | S3b |

### Slot B / module `top_crank_arm`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank_shaft` with visuals: drive_shaft (Cylinder along Z), shaft_shoulder, crank_arm (Box along X), shaft_cap, grip_pin (Cylinder along Z), handle_washer | S1 / 001 L291-L317, S3 / 003 L313-L349 |
| upstream interface | joint origin (0, 0, crank_axis_z_top); axis +Z; REVOLUTE multi-turn | — |
| downstream interface | `grip_pin` face at (crank_arm_len, 0, arm_z + pin_z); axis +Z; CONTINUOUS | — |

### Slot B / module `folding_top_crank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank_shaft` with visuals: drive_shaft, fold_hub (clevis with two ears + hinge pin); `fold_arm` PART with visuals: crank_arm (extending along +X in local frame), grip_pin, handle_washer | `..._drive_folding_top_crank` L47-L127, L288-L354 |
| internal joints (module-level) | `crank_shaft → fold_arm` REVOLUTE -Y at fold hub center | — |
| downstream interface | grip attaches to `fold_arm.grip_pin` | — |

### Slot B / module `side_crank_arm`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank_shaft` with visuals: drive_shaft (Cylinder along X, exits body +X face), shaft_shoulder (along +X), arm_bracket (Box), crank_arm (Box along +Z from bracket), grip_pin (Cylinder along X), handle_washer | `..._drive_side_crank` L322-L389 |
| upstream interface | origin (body_half_x, 0, crank_axis_z_side); axis +X; REVOLUTE multi-turn | — |
| downstream interface | `grip_pin` face at (arm_len_x, 0, arm_z_top); axis +X; CONTINUOUS | — |

### Slot C / module `integrated_body`
| emits | No new part; the body's own grounds_bin visual serves as the storage compartment | S1 |

### Slot C / module `pull_out_drawer`
| emits | `catch` part with visuals: drawer_tray (cadquery box with cavity), drawer_front (rounded rect panel), drawer_knob_stem, drawer_knob; PRISMATIC joint body→catch on -Y | S3 / 003 L259-L386 |

### Slot C / module `threaded_cup`
| emits | `catch` part with visuals: bin_cup (lofted mesh); PRISMATIC joint body→catch on -Z, short travel | S2 / 002 L245-L375 |

### Slot D / module `open_hopper`
| emits | No new part; the body's hopper_shell visual is topless | S1 / S2 / S3 |

### Slot D / module `hinged_covered_hopper`
| emits | `hopper_lid` PART with visuals: dust_cover (disc), dust_hinge_barrel (Cylinder along X); REVOLUTE joint body→hopper_lid on +X at the rim rear edge; range [0, ≈100°] | `..._hopper_hinged_covered_hopper` |

### Slot E / module `standalone`
| emits | No new geometry | S1/S2/S3 defaults |

### Slot E / module `table_clamp`
| emits | Adds visual-only C-clamp bracket geometry to `body`: table_clamp_bracket (cadquery cast bracket), hopper_adapter_ring, table_clamp_upper_pad, clamp_screw. Replaces the parent's hopper mounting rings (visual-only substitution). No new PART. | `..._mount_table_clamp` L204-L275 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | `turned_wood_stack` / `anodized_cylinder` / `wood_cabinet` / `square_wood_box` / `slim_travel_cylinder` | — | choice | procedural sampler | Slot A |
| `drive` | enum | `top_crank_arm` / `folding_top_crank` / `side_crank_arm` | — | choice | — | Slot B |
| `catch` | enum | `integrated_body` / `pull_out_drawer` / `threaded_cup` | — | choice | — | Slot C |
| `closure` | enum | `open_hopper` / `hinged_covered_hopper` | — | choice | — | Slot D |
| `mount` | enum | `standalone` / `table_clamp` | — | choice | — | Slot E |
| `palette_style` | enum | `walnut_and_iron` / `black_anodized` / `natural_oak_and_steel` / `ceramic_white_brass` / `red_lacquered` / `weathered_bronze` | first | choice | 6 realistic palettes (wood-and-cast-iron; anodized metal; natural oak + polished steel; ceramic white with brass hardware; red lacquered painted wood; weathered bronze) | palette table |
| `body_scale` | float | [0.90, 1.10] | 1.0 | independent | uniform | — |
| `body_radius_scale` | float | [0.90, 1.10] | 1.0 | independent | uniform (for cylindrical bodies); clamped to body_scale for box bodies | — |
| `crank_arm_length_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform; clamped so grip stays clear of body across 360° | 001 L48-L62 |
| `catch_stroke_scale` | float | [0.85, 1.10] | 1.0 | independent | uniform | 003 |
| (—) | constraint | — | — | inequality | grip swept-clear-of-body: `crank_arm_len × crank_arm_length_scale ≥ body_half_radius + grip_r + clearance` (top drives). Enforced by `resolve_config` clamp. | Rule 5 |
| (—) | constraint | — | — | inequality | `side_crank_arm` requires `crank_arm_len × crank_arm_length_scale ≥ body_half_x + shaft_shoulder_len + grip_r + clearance`. Clamped in `resolve_config`. | Rule 5 |
| (—) | constraint | — | — | conditional | `folding_top_crank` shrinks nominal crank_arm_length_scale by 0.9 to keep the fold hub within the frame envelope | — |

Continuous-scale sampling contract:

1. Sample `body_scale`, `body_radius_scale`, `crank_arm_length_scale`, `catch_stroke_scale` independently in their ranges.
2. Derive `body_radius_scale` = `body_scale` for box-shaped body_forms (`wood_cabinet`, `square_wood_box`) — locks proportions.
3. Project: `crank_arm_length_scale` = max(sampled, minimum-for-clearance).
4. `conditional` (drive-dependent `crank_arm_length_scale` cap) resolved after `drive` is picked.

## 7.5 编译预算 / compile budget

Target: ≤20 s per seed. Two-three cadquery lathes / boxes (body shell, hopper, optional catch cup/tray) + a handful of Cylinder/Box primitives. Reuse module cache. Tessellation: `tolerance=0.0006-0.0008`, `angular_tolerance=0.07-0.08` on cadquery meshes; small-radius pin/washer segments ≤32; hero body ≤64. Under the sweep-pipeline hang-guard `--compile-timeout 120` (~3-6× budget).

## 8. Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达 (body / adjustment_collar / crank_shaft / grip / optional catch / optional fold_arm / optional hopper_lid)。No `*_count` axis is exposed; no template-level visual/part/joint replication.

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Baseline part tree is body + adjustment_collar + crank_shaft + grip (4 parts, 3 non-FIXED joints). ①-adding modules: `folding_top_crank` adds `fold_arm` PART + REVOLUTE joint; `hinged_covered_hopper` adds `hopper_lid` PART + REVOLUTE joint; `pull_out_drawer` / `threaded_cup` each add a `catch` PART + PRISMATIC joint. Source-backed by respective `..._drive_folding_top_crank`, `..._hopper_hinged_covered_hopper`, `..._catch_pull_out_drawer`, `..._catch_threaded_cup` variants. |
| └ multiplicity | 同构件 ×N | 无 | Single burr, single crank, single grip: no template-level repetition axis. |
| ② 关节类型 | 图不变,某条边换 type/轴 | 有 | Drive axis flips between world +Z (`top_crank_arm`, `folding_top_crank`) and world +X (`side_crank_arm`). Both types appear in every sweep. Source-backed. Additionally the catch axis flips between world -Y (`pull_out_drawer`) and world -Z (`threaded_cup`); the fold_arm joint axis is world -Y REVOLUTE. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | 有 | Slot A `body_form` slot registers the ③ axis with 5 candidates: `Volumetric Envelope Form` (`turned_wood_stack` turned-lathe stack, `anodized_cylinder` thin ribbed cylinder, `slim_travel_cylinder` slim cylinder), `Planar Boundary Form` (`wood_cabinet` rounded rectangular, `square_wood_box` square boundary). ≥3 candidates source-backed (all 5 have `forked_anchor` variants). |
| ④ 表面装饰 | 原型不变,叠加表面细节 | 有 | (record_only + world_knowledge_extrapolation): dense horizontal micro-ribs on `anodized_cylinder` (per-face derived), turned wood bands (lower/upper grooves) on `turned_wood_stack`, drawer recess trim on `wood_cabinet`/`square_wood_box`/`slim_travel_cylinder`, adjustment collar knurling (scalloped lugs), hopper rim torus. All derived per-face from host bodies (§Rule 4). |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | Key scales: `body_scale ∈ [0.90,1.10]`, `body_radius_scale ∈ [0.90,1.10]`, `crank_arm_length_scale ∈ [0.85,1.15]`, `catch_stroke_scale ∈ [0.85,1.10]`. Joints: `adjustment_collar` REVOLUTE +Z limits ±0.5 rad (short motion); `crank_shaft` REVOLUTE multi-turn ±12π, integer-turn `qc_sample_values ∈ {0, ±π/2, π}`; `grip` CONTINUOUS same-axis; `catch` PRISMATIC world -Y or -Z, [0, 0.03..0.085]; `fold_arm` REVOLUTE -Y [0, ≈π/2]; `hopper_lid` REVOLUTE +X [0, ≈100°]. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` covers all pairs; targeted `ctx.pose(...)` at (crank=π/2), (crank=π), (fold=π/2), (catch=upper), (hopper_lid=upper) proves motion semantics. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 palettes: `walnut_and_iron`, `black_anodized`, `natural_oak_and_steel`, `ceramic_white_brass`, `red_lacquered`, `weathered_bronze`. Material categories: wood / anodized-metal / painted / ceramic / brass — ≥ ceil(0.5 × 6) = 3 categories covered. |

## 9. 采样与覆盖审计

总组合数（结构+装配）：`body_form (5) × drive (3) × catch (3) × closure (2) × mount (2)` = **180** legal structural tuples (before palette / continuous scales). All tuples are legal; there is no gating.

seed_domain_policy: `procedural_first`.

**Procedural Sampling / Sweep Plan.** `config_from_seed(seed)` uses `random.Random(seed)`. Samples independently: `body_form`, `drive`, `catch`, `closure` (with a weight favoring `open_hopper` 0.7 / `hinged_covered_hopper` 0.3), `mount` (0.75 / 0.25 for standalone / table_clamp), `palette_style`, and continuous scales. `resolve_config` clamps every scale and re-applies drive-dependent clearance constraints, so `slot_choices_for_seed` matches `build_*` choices.

**Topology target.** 180 legal tuples; a 1000-seed report will show all body_form values, all drive values, all catch values, both closures, both mounts, all palettes. Report-only, not gated.

Regression overrides: none at P0.

**Controlled local parameterization.** `body_scale`, `body_radius_scale`, `crank_arm_length_scale`, `catch_stroke_scale`; all clamped in `resolve_config`; `body_radius_scale = body_scale` for box-shaped bodies (equation); `crank_arm_length_scale ≥ min_for_clearance` (inequality).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form → drive → catch → closure (weighted) → mount (weighted) → palette → continuous scales | `slot_choices_for_seed` == build choices |
| compatibility matrix | all tuples legal; no gating | no floating parts, no grip-vs-body collision through 360°, no catch collision at extremes |
| controlled local variation | body_scale / body_radius_scale / crank_arm_length_scale / catch_stroke_scale in specified ranges | proportions vary but grip stays clear of body; catch doesn't exit the body cavity envelope |
| regression overrides | none | — |
| random sweep | seeds 0-15 (fast) → 16-35 (final) → corner | corner covers extremes of each scale + rare tuple like `slim_travel_cylinder + side_crank_arm + threaded_cup` |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A `body_form` | 5 | yes | yes | 3 origin anchors + 2 variant anchors, all forked_anchor |
| B `drive` | 3 | yes | yes | 3 forked_anchor variants |
| C `catch` | 3 | yes | yes | 3 forked_anchor variants (including no-part `integrated_body`) |
| D `closure` | 2 | yes | no | binary axis; source-backed for both values |
| E `mount` | 2 | yes | no | binary axis; ④ decoration axis, no new joint |

## 10. Validator

- `slot_choices_for_seed` returns implemented module names for all 5 slot axes.
- `config_from_seed(0)` deterministically returns a legal, buildable config (registry contract).
- `resolve_config` clamps every continuous scale before the builder runs.
- `slot_choices_for_seed(seed)` matches actual build choices bit-for-bit.
- Every non-FIXED joint declares axis + range; captured pins/pivots are guarded by element-scoped `ctx.allow_overlap` in `run_manual_coffee_grinder_tests`.
- `run_manual_coffee_grinder_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` **plus** targeted `ctx.pose(...)` checks proving intended motion (crank rotates grip, catch translates, fold_arm swings up, hopper_lid opens up).
- No small curated / modulo table is used as the main seed domain.
- Shared body/collar/crank/grip geometry lives in single helpers; body_scale is single-sourced through `resolve_config`.

## Reject cases

- Electric motor drive (no crank, no free-spinning grip): rejected — belongs to `electric_coffee_grinder`.
- Decorative container mill (no non-FIXED joint): rejected — Rule 1 + spec 5-star pool.
- Grain-mill scale (A-frame legs, ≥40 cm tall trough): rejected — belongs to `manual_grain_mill`.
- Pepper mill scale / single-turn cap: rejected — belongs to `pepper_mill`.
- Grip that swept-collides with the body at half-turn: rejected — grip-vs-body clearance inequality + sampled-pose collision.
- Catch that translates past the body outer face (would fall off in reality): rejected — catch travel is a fraction of body_h/body_depth.
- Fold arm that collides with the crank shaft or the frame during folding: rejected — element-scoped `allow_overlap` on captured hinge pin, and the fold_arm sweeps outward from the shaft axis.

## 11. 与相邻类别的边界

- 不该混入：`electric_coffee_grinder` (相邻类别) — has a motor drive, no hand crank. Our category is hand-driven only.
- 不该混入：`pepper_mill_with_rotating_grinder_mechanism` — different scale, different grinding target, always has a full-turn cap or single-piece housing; our category always has a *grounds bin* (integrated or removable).
- 不该混入：`manual_grain_mill` — much larger scale, grounded A-frame or trough, tin-cup rather than cup catch.
- 不该混入：`Machinery_Watermill` — grounded on riverbed, water-driven, no crank/grip drive.

## 12. 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec authored from the 12-record 5-star pool (3 origins + 9 variants). Five parallel-child slots + one visual-only mount slot; 180 legal structural tuples. All source-backed; no world_knowledge_extrapolation candidates required. |

## 13. 模板实现备注

- `body_scale` is a uniform scale about the world (0,0,0) frame (world Z-up in top drives, world +X for side_crank); primitives multiply by `s`, mesh helpers receive `unit_scale=s`.
- Cadquery meshes are shared across seeds via the AssetContext cache: body shells (5 forms), hopper_shell (open funnel), catch_shape (pull_out_drawer + threaded_cup), adjustment_collar_shape, crank_arm_shape, hopper_lid_shape.
- Captured-pin/pivot overlaps are declared with element-scoped `ctx.allow_overlap` on: (a) grip vs grip_pin/handle_washer, (b) fold_arm vs fold_hub hinge_pin, (c) hopper_lid vs hopper_rim hinge_barrel, (d) catch vs body cavity walls. `mating` is omitted for these joints (grandfathered captured hinges).
- Non-FIXED joints (all revolute/prismatic/continuous) are declared with clean axis-aligned MatingContract-free interfaces; the compiler baseline gap check is grandfathered per captured-pin note.
- For `side_crank_arm`, the crank_shaft's child part frame origin sits at world (body_half_x, 0, crank_axis_z_side); visuals are authored in that local frame so the joint origin is on real hardware (shaft exit face).

## 14. Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / D | turned_wood_stack / top_crank_arm / integrated_body / open_hopper | rec_picturex_0611__manual_coffee_grinder__001 | L65-L400 | full turned-wood body + top crank + grip skeleton |
| S1a | E | table_clamp | rec_0611_manual_coffee_grinder_var_mount_table_clamp | L204-L275 | C-clamp bracket + adapter ring + upper jaw + T-handle screw visuals |
| S1b | B | folding_top_crank | rec_0611_manual_coffee_grinder_var_drive_folding_top_crank | L47-L127, L288-L354 | fold_hub clevis + fold_arm PART + REVOLUTE hinge joint |
| S1c | D | hinged_covered_hopper | rec_0611_manual_coffee_grinder_var_hopper_hinged_covered_hopper | L34-L120 | hinged hopper cover PART + REVOLUTE +X joint |
| S1d | D | open_bowl (visual variant of open_hopper) | rec_0611_manual_coffee_grinder_var_hopper_open_bowl | full file | wider bowl hopper visual (Volumetric Envelope Form variant) |
| S2 | A / B / C | anodized_cylinder / top_crank_arm / threaded_cup | rec_picturex_0611__manual_coffee_grinder__002 | L34-L400 | full anodized cylinder + hopper + threaded cup PRISMATIC -Z |
| S2a | C | threaded_cup (variant details) | rec_0611_manual_coffee_grinder_var_catch_threaded_cup | full file | threaded engagement lip visual |
| S3 | A / B / C | wood_cabinet / top_crank_arm / pull_out_drawer | rec_picturex_0611__manual_coffee_grinder__003 | L31-L500 | full wood cabinet + drawer + drawer PRISMATIC -Y |
| S3a | A | square_wood_box | rec_0611_manual_coffee_grinder_var_body_form_square_wood_box | L37-L92 | square (non-filleted) wood box hopper_shell |
| S3b | A | slim_travel_cylinder | rec_0611_manual_coffee_grinder_var_body_form_slim_travel_cylinder | L33-L60 | slim tall cylindrical wooden body + drawer landing |
| S3c | C | pull_out_drawer (variant) | rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer | full file | thin-wall rabbeted drawer tray + turned knob stem |
| S3d | B | side_crank_arm | rec_0611_manual_coffee_grinder_var_drive_side_crank | L322-L389 | horizontal drive_shaft along +X + REVOLUTE +X body_to_crank |
