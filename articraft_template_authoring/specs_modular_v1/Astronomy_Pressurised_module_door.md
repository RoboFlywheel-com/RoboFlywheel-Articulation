# Modular Spec — Astronomy / Pressurised module door

> **Current implementation override (2026-07-30):** the
> `rec_module_door_var_sliding_hatch` source remains documented below for pool
> coverage, but `sliding_hatch`, its PRISMATIC joint, rails and carriage are
> intentionally excluded from the runtime template. The approved closure
> family is hinge-only: single, reinforced, domed and double-leaf swing hatches.
> The final single-file template is the runtime truth.

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Pressurised_module_door` |
| template path | `agent/templates/Astronomy_Pressurised_module_door.py` |
| test path (optional) | `tests/agent/test_Astronomy_Pressurised_module_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root shell/aperture + parallel-children closure + optional radial-cover multiplicity + 3 decoration-count axes) |
| function stem | `astronomy_pressurised_module_door` (exports `build_astronomy_pressurised_module_door`, `config_from_seed`, `run_astronomy_pressurised_module_door_tests`) |

`pattern = mixed`: a single root `airlock_shell` part (pressurised module hull +
raised hatch collar + tan pressure seal + end plate with the through-opening)
carries a parallel-children `closure` slot (the moving hatch that seals the
opening + its inner handwheel), whose joints parent directly to the shell (no
serial chain joint). One `① multiplicity` axis (`cover_count`, a radial
debris-cover shutter ring of N independently-hinged panels) and three `④`
decoration-count axes (`bolt_count`, `dog_count`, `spoke_count`) ride on top.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 9 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_a-round-eva-airlock-hatch-on-a-white-pressurised_20260708_142809_748768_d440cc9f` — ORIGIN 母本 (circular airlock hull, raised round hatch collar + tan seal, single round hatch lid on a side REVOLUTE hinge swung open, inner handwheel, 8 latch dogs + 8 strikes + 12 bolts).
- `rec_module_door_var_bolt_ring_count` — ④ multiplicity: `PLATE_BOLT_N` 12→24 (dense bolt circle on end plate).
- `rec_module_door_var_latch_dog_count` — ④ multiplicity: `DOG_COUNT` 8→12 (dogs on lid rim + matching strikes on collar, paired).
- `rec_module_door_var_spoke_count` — ④ multiplicity: handwheel `SPOKE_COUNT` 3→5.
- `rec_module_door_var_dome_lid` — ③ lid form: flat disc lid → convex spherical-cap pressure **dome** (`LatheGeometry` cap profile).
- `rec_module_door_var_square_hatch` — ③ aperture form: round → **rounded-square** aperture/collar/seal/lid (cadquery filleted-rect solids + rings; square rim dog/strike layout).
- `rec_module_door_var_double_leaf` — ① skeleton: single lid → **two half-disc bi-parting leaves**, each on its own side REVOLUTE hinge, meeting at centre.
- `rec_module_door_var_sliding_hatch` — ② joint: hinge REVOLUTE → **PRISMATIC** lateral slide; adds a pair of slide-rail ribs on the shell + carriage sliders/crossbar under the lid.
- `rec_module_door_var_radial_covers` — ① multiplicity: adds a **radial debris-cover shutter ring** of `COVER_N=8` independently-hinged flat panels around the collar (each a REVOLUTE part parented to the shell).

## 核心身份

A **pressurised-module EVA hatch / airlock door**: a compact white cylindrical
pressurised-module **hull** whose top end plate carries a raised **hatch collar**
ringing a through-**opening** with a tan pressure **seal**, closed by a moving
**hatch** — one round or rounded-square lid on a side hinge, a convex pressure
dome lid, two bi-parting half-leaves, or a laterally-sliding pocket lid — with an
inner locking **handwheel** (hub + spokes + rim) on the pressure-side face,
radial **latch dogs** on the lid rim matched by **strike plates** on the collar,
a **bolt ring** on the end plate, EVA grab **handrails** on the hull, and
optionally a **radial debris-cover shutter ring** of independently-hinged panels
around the collar. At least one real non-fixed joint is always present (the hatch
hinge/slide) plus the handwheel spin. Default mature domain: ~1 m-radius module,
~0.5 m-radius opening, one hatch + one handwheel (+ 0/6/8/12 covers).

Not to be confused with the neighbouring picture subclass **Industrial / Blast
door** (a flat wall-mounted rectangular armoured leaf on a door frame, no
pressurised cylindrical hull, no collar/seal/handwheel identity) or **Astronomy
/ Return capsule** (a bell/sphere re-entry body whose hatch is a small detail on
a much larger heat-shielded volume, not the whole object).

## 槽位 + 候选模块表

### Slot A：shell_aperture (root · ③ Primary Form Family)

The root pressurised-module body. Same part tree across candidates: one
`airlock_shell` part carrying `hull_tube` + `hull_base_cap` + `hull_seam` +
`end_plate` (with the through-opening) + `hatch_collar` + `seal_ring` +
`plate_bolt_i` ring + `latch_strike_i` ring + `handrail_i`/`rail_post_i_k`
(all fused as `airlock_shell` visuals, Rule 1) + optional `debris_cover_i`
child parts. The **circular hull is invariant**; only the aperture cross-section
prototype (collar / seal / opening / matching lid plate) changes. All three
expose the identical mounting envelope (`collar_ro`, `seal_top`, `plate_top`,
`opening_ri`) so the closure slot is aperture-form-independent for placement.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `round_aperture` | forked_anchor (origin) | `rec_a-round-eva-...d440cc9f` | L66-L92 (hull+plate+collar+seal via `_ring`) | eligible | circular `_ring` collar/seal/opening + `Cylinder`/ring hull. **Planar Boundary Form** (circle) |
| `square_aperture` | forked_anchor | `rec_module_door_var_square_hatch` | L74-L119 (`_rounded_sq_solid`/`_rounded_sq_ring`/`_circle_with_sq_hole`), L179-L203, L215-L223 | eligible | rounded-square (filleted-rect) collar/seal/opening + square-rim dog/strike layout; circular hull unchanged. **Planar Boundary Form** (rounded rectangle) |
| `hex_aperture` | world_knowledge_extrapolation (③) | anchors: `square_hatch` cadquery polygon-ring idiom (L85-L119) + origin `_ring` part tree; reviewer | n/a (cadquery `.polygon(6,...)` ring/solid, same helpers) | eligible | regular-hexagon collar/seal/opening + matching hex lid plate; same part tree / primitive family (cadquery extrude+cut) / mounting interface. **Planar Boundary Form** (hexagon) |

### Slot B：closure (parallel child on shell · ① skeleton + ② joint + ③ lid form)

The moving hatch that seals the opening + the inner handwheel. Each candidate
parents its joint(s) directly to `airlock_shell` (parallel children; no auto
chain joint) and adds its own mount hardware (hinge bracket/pin, or slide rails)
to the shell as static visuals. The handwheel is a REVOLUTE child of the lid
(single/domed/sliding) or of `hatch_leaf_0` (double_leaf).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_swing_lid` | forked_anchor (origin, square_hatch) | `rec_a-round-eva-...d440cc9f` L114-L237; `rec_module_door_var_square_hatch` L261-L335 | eligible | one flat lid (`Cylinder` round / rounded-square / hex plate, derived from aperture form) on a side `hatch_hinge` **REVOLUTE** axis Y; rest q=0 = open, closes onto seal; lid carries dogs/lugs/strap/seal; handwheel child of lid. |
| `domed_swing_lid` | forked_anchor | `rec_module_door_var_dome_lid` | L52-L68 (`_dome_cap_profile`), L169-L181 | eligible if compatible | ③ lid form: same swing skeleton but a convex spherical-cap `lid_dome` (`LatheGeometry`) + apex hub boss replacing the flat disc. Gated → round aperture (spherical cap ↔ round rim). |
| `double_leaf` | forked_anchor | `rec_module_door_var_double_leaf` | L61-L78 (`_half_disc`), L185-L290 | eligible if compatible | ① skeleton: two `hatch_leaf_{0,1}` half-disc leaves, each on its own `leaf_hinge_{0,1}` **REVOLUTE** (axis ±Y), meeting at centre; rest q=0 = closed, opens outward; handwheel child of `hatch_leaf_0`. Gated → round aperture. |
| `sliding_hatch` | forked_anchor | `rec_module_door_var_sliding_hatch` | L62-L96 (`_rail_rib`/`_carriage_block`), L161-L281 | eligible if compatible | ② joint: one round lid on a `hatch_slide` **PRISMATIC** (axis Y) sliding pocket; adds 2 `slide_rail_k` ribs + mount pads to the shell and carriage sliders/stems/crossbar under the lid; rest q=0 = closed. Gated → round aperture. |

硬约束满足：每个 slot ≥3 结构不同 candidate（A=3, B=4）；每个普通
candidate 有 forked_anchor + `model.py:Lx-Ly`；唯一 `world_knowledge_extrapolation`
是 `hex_aperture`（③ Primary Form Family 例外，form_subtype=Planar Boundary Form，
几何锚定在 square_hatch 的 cadquery 多边形 ring/solid 惯用 + origin 的 `_ring`
part tree，保持同一 part tree / primitive 家族 / mounting interface，只改离散的
平面边界多边形）。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel child + multiplicity)

```
shell_aperture (root; round / square / hex)
   ├─[end plate hinge line · REVOLUTE(Y) swing | REVOLUTE(±Y) bi-part | PRISMATIC(Y) slide; captured pin/rail mount]→ closure  (lid | 2 leaves | slider) → handwheel (REVOLUTE Z child of lid/leaf)
   └─[end plate ring @ r=cover_hinge_r · REVOLUTE(tangent); captured lug/pin]→ debris_cover_i  (×cover_count independently-hinged panels; parallel children of shell)
```

- **slot 顺序 / parent**：`shell_aperture` 是 root，唯一被复用的 parent。`closure`
  的 joint 全部 `parent=airlock_shell`；debris covers 也全部 `parent=airlock_shell`
  （parallel children）。closure 只声明 `downstream` 接口（re-export shell），不声明
  `upstream`，因此 assembler 不发射自动 chain joint（模块自己发原始 joint，与 5 星源一致）。
- **接口点位**：closure → 端板铰链线：swing/dome 在 `(-collar_ro-0.08, 0, hinge_z)`
  的 hinge pin（captured pin ↔ lid lugs）；double_leaf 在 `(±collar_ro, 0, hinge_z)`
  两侧 leaf 铰链（captured lug ↔ bracket）；sliding 在 `(0,0,rail_cap_top)` 的 rail
  running surface（carriage ↔ rail cap）。covers → 端板半径 `cover_hinge_r≈0.90` 圆环
  （captured lug/pin）。handwheel → lid/leaf 内面 `(lid_cx,0,-t)`。
- **跨 slot joint type/axis/range**：hatch_hinge REVOLUTE(Y, [-lid_open, 0.08]) /
  leaf_hinge REVOLUTE(±Y, [0, lid_open]) / hatch_slide PRISMATIC(Y, [0, slide_open]);
  cover_hinge REVOLUTE(tangent, [0, cover_open]); handwheel_spin REVOLUTE(Z, ±2.6).
- **互斥/派生**：`domed_swing_lid` / `double_leaf` / `sliding_hatch` gated → round
  aperture（see §9 compatibility）；square/hex aperture → 只 `single_swing_lid`。
  `dog_count` 对 square 固定为 8（方形周边 2-per-side 布局）。covers 与 closure 正交
  （挂在圆形端板上，独立于孔径形态），可与任意 closure 组合。

## 每槽位 Module Emits / Interfaces

### Slot A / module round_aperture | square_aperture | hex_aperture
| emits | 描述 | 来源 |
|---|---|---|
| parts | `airlock_shell` (single root part) + optional `debris_cover_i` child parts | origin L66; radial_covers L279 |
| visuals | `hull_tube` + `hull_base_cap` + `hull_seam` + `end_plate`(with opening) + `hatch_collar` + `seal_ring` + `plate_bolt_i`(×bolt_count) + `latch_strike_i`(×dog_count) + `handrail_i`/`rail_post_i_k` | origin L66-L147; square L179-L223; bolts bolt_ring_count L48,L96 |
| internal joints | (root, static body) + optional `cover_hinge_i` REVOLUTE(tangent) for each debris cover | radial_covers L313-L323 |
| downstream interface | `airlock_shell` part, `end_plate` visual, face `positive_z`, anchor `(0,0,plate_top)` (informational; children wire manually) | — |

### Slot B / module single_swing_lid | domed_swing_lid | double_leaf | sliding_hatch
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hatch_lid` (+ `lock_handwheel`) \| `hatch_leaf_0`+`hatch_leaf_1` (+ `lock_handwheel`) \| `hatch_lid` (+ `lock_handwheel`) | origin L152,L211; double L198,L294; sliding L204,L284 |
| shell visuals added | `hinge_bracket_lug_k`+`hinge_pin` (swing/dome) \| `leaf_bracket_i_k` (double) \| `slide_rail_k`+`rail_mount_pad_k` (sliding) | origin L114-L127; double L149-L164; sliding L161-L177 |
| lid/leaf visuals | `lid_disc`/`lid_dome`+`lid_dome_step`+`lid_hub_boss`+`lid_seal_ring`+`latch_dog_j`(×dog_count)+`lid_hinge_lug_k`+`hinge_strap`; leaf: `leaf_disc_i`+`leaf_step_i`+`leaf_seal_i`+`leaf_hub_i`+`leaf_latch_i_j`+`leaf_hinge_lug_i_k`+`leaf_hinge_strap_i`; sliding adds `carriage_slider_k`+`carriage_stem_k`+`carriage_crossbar` | origin L152-L199; dome L169-L181; double L205-L276; sliding L238-L271 |
| handwheel visuals | `wheel_hub` + `wheel_spoke_j`(×spoke_count) + `wheel_rim` | origin L211-L228; spoke_count L218 |
| internal joints | `hatch_hinge` REVOLUTE(Y) \| `leaf_hinge_{0,1}` REVOLUTE(±Y) \| `hatch_slide` PRISMATIC(Y); + `handwheel_spin` REVOLUTE(Z) | origin L200-L237; double L279-L323; sliding L273-L310 |
| upstream interface | **none declared** (parallel-children; parents joints directly to `airlock_shell`) | — |
| downstream interface | re-export shell downstream (passthrough) | — |

活动件语义：hatch hinge/slide 打开/关闭舱门；leaf hinge 双开对开；cover hinge 掀开
防尘盖；handwheel 旋转锁紧。不动细节（bolts/strikes/handrails/seal/hub/strap/dogs/
rails/brackets）写成宿主 part visual，非独立 part（Rule 1）。captured pin/lug/rail
socket 用 element-scoped allow_overlap（Rule 2 例外），hinge/slide 原点落在 shell 真实
end-plate/rail 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `aperture_form` | enum | round_aperture / square_aperture / hex_aperture | round_aperture | choice | procedural sampler | Slot A |
| `closure_module` | enum | single_swing_lid / domed_swing_lid / double_leaf / sliding_hatch | single_swing_lid | choice | procedural sampler | Slot B |
| `cover_count` | int | {0, 6, 8} (obs: 0 origin, 8 radial_covers; 6 interp) | 0 | conditional | debris-cover ring; gated to round aperture + swing-lid closure (else 0); half-step ring phase clears the single -X hinge bracket | radial_covers L49 |
| `bolt_count` | int | {12, 24} (obs: 12 origin, 24 bolt_ring_count) | 12 | independent | end-plate bolt ring count | origin L94, bolt_ring_count L48 |
| `dog_count` | int | {8, 12} (obs: 8 origin, 12 latch_dog_count) | 8 | conditional | dogs (lid) + strikes (collar) paired; forced 8 for square aperture | origin L103/L175, latch_dog_count L48 |
| `spoke_count` | int | {3, 5} (obs: 3 origin, 5 spoke_count) | 3 | independent | handwheel spokes | origin L218, spoke_count L218 |
| `hull_radius_scale` | float | [0.90, 1.10] | 1.0 | independent | uniform, clamp; scales hull radius (all radial features co-derive) | origin L34 |
| `hull_r` | float | derived | — | equation | `= 1.00 · hull_radius_scale` | origin L34 |
| `collar_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; collar outer / opening radius | origin L38-L39 |
| `collar_ro` | float | derived | — | equation | `= 0.60 · collar_scale`; `opening_ri = 0.50 · collar_scale` | origin L38-L39 |
| `lid_open` | float | [1.55, 2.00] | 1.90 | independent | swing lid / leaf open angle (rad) | origin L46 |
| `slide_open` | float | derived | — | equation | `= 2 · collar_ro + 0.20` (travel to clear opening) | sliding L55 |
| `dome_height` | float | [0.10, 0.20] | 0.15 | conditional | domed_swing_lid apex height; else n/a | dome_lid L46 |
| `cover_open` | float | [1.2, 1.6] | 1.4 | conditional | debris-cover hinge upper (rad); else n/a | radial_covers L321 |
| (—) | constraint | — | — | inequality | `cover_count>0` only when `aperture_form==round_aperture`; `domed/double/sliding` only when round; `dog_count==8` when square | see §9 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 参数范围汇总 → 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: ≤ 30 s** (hang-guard `--compile-timeout 90`).
Geometry is cadquery-based (matching every 5-star source): rings
(`_ring`), rounded-square filleted solids/rings, half-disc arcs, a `LatheGeometry`
dome cap (≤48 seg), rail ribs, carriage blocks, and N shared debris-cover panel
meshes. All N covers share ONE `cover_panel`/`cover_lug`/`cover_grip` mesh; both
leaves share the half-disc helper; the rail rib + carriage meshes are built once
and reused across the pair. Fillet/boolean ops (rounded-square, carriage slot)
are the cost drivers; keep fillet counts minimal, arc segments ≤32, lathe ≤48.
Expect 8-20 s/seed; downgrade fillet/segment counts first if over.

## Multiplicity / Copy Logic

**四根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 — `cover_count`（径向防尘盖数，① 会动 part 复制）
- `count_param`: `cover_count`; `N_range` product `{0,6,8}`, test `{0,6,8}`;
  sampling domain 加权（采样 {0,6,8,12}，12→8 回缩）：`{0: 0.55, 6: 0.15, 8: 0.30}`（无盖偏多）。
- copied object: `debris_cover_i` part（panel + 2 lugs + hinge pin + grip tab，
  共享 mesh）+ 各自 `cover_hinge_i` REVOLUTE(tangent axis)。half-step 角偏移使无盖对齐
  hatch 铰链侧。
- naming: `debris_cover_{i}` / `cover_hinge_{i}`。placement: `end_plate` 上半径
  `cover_hinge_r≈0.90` 均匀圆环，hinge z 落在端板面上（origin-honesty）。joint policy:
  每盖独立 REVOLUTE，rest q=0=闭合平贴。
- source/gating: radial_covers (N=8) L273-L323；gated → 仅 round aperture + swing-lid
  closure（single/domed，样本即 swing+covers 组合），其余为 0；half-step 相位避开 -X
  铰链托架。12 采到时回缩到 8（12 会把一片盖挤到托架方位）。
- 数量变化不改主体形态/机制。

### 轴 2 — `bolt_count`（端板螺栓环数，④ 装饰）
- `count_param`: `bolt_count`; `N_range` `{12,24}`, test `{12,24}`; 加权 `{12:0.6, 24:0.4}`。
- copied object: `plate_bolt_i` `Cylinder`（宿主 shell visual，半径 0.80 圆环，随
  hull_radius_scale/collar_scale 派生位置 — Rule 4 共形）。source: origin L94-L101,
  bolt_ring_count L48,L96。

### 轴 3 — `dog_count`（闩锁狗/撞板数，④ 装饰，配对）
- `count_param`: `dog_count`; `N_range` `{8,12}`, test `{8,12}`; 加权 `{8:0.6, 12:0.4}`；
  square aperture 固定 8。
- copied object: `latch_dog_j`（lid/leaf rim Box）+ `latch_strike_j`（collar Box），
  数量配对，宿主 visual。round/hex 径向环；square 方形周边 2-per-side（固定 8）。
  source: origin L103/L175, latch_dog_count L48, square L215-L223/L298-L309。

### 轴 4 — `spoke_count`（手轮辐条数，④ 装饰）
- `count_param`: `spoke_count`; `N_range` `{3,5}`, test `{3,5}`; 加权 `{3:0.6, 5:0.4}`。
- copied object: `wheel_spoke_j` Box（handwheel 宿主 visual，均匀角分布）。
  source: origin L218, spoke_count L218。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构骨架 candidate：single swing lid（origin, forked_anchor, 1 lid part + hinge）／double bi-parting leaves（double_leaf, forked_anchor, 2 leaf parts + 2 hinges）／sliding pocket（sliding_hatch, forked_anchor, rail+carriage skeleton）。加上可选 radial debris-cover ring（radial_covers, forked_anchor，×cover_count 会动 part）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：cover_count {0,6,8}（① 会动 part，radial_covers；仅 swing-lid closure），bolt_count {12,24}、dog_count {8,12}、spoke_count {3,5}（④ 装饰数）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | hatch 主关节：REVOLUTE(Y) swing（origin）↔ PRISMATIC(Y) slide（sliding_hatch）↔ 双 REVOLUTE(±Y) bi-part（double_leaf）；cover_hinge REVOLUTE(tangent)（radial_covers）；handwheel_spin REVOLUTE(Z)（origin）。全部 forked_anchor；每种类型在 sweep 中出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **两处登记进 slot_choices**：(A) 孔径/collar/seal/lid 平面边界原型 — round circle（origin, Planar Boundary Form）/ rounded-square（square_hatch, Planar Boundary Form）/ hexagon（world_knowledge_extrapolation, Planar Boundary Form）。(B) lid 体量包络 — 平盘 disc（origin, 无凸起）vs 凸球冠 dome（dome_lid, Volumetric Envelope Form，`domed_swing_lid` candidate）。 |
| ④ 表面装饰 | 原型不变叠加表面细节 / 改装饰数 | 有 | `plate_bolt` 螺栓环（×bolt_count）、`latch_dog`/`latch_strike` 闩锁（×dog_count 配对）、`wheel_spoke` 辐条（×spoke_count）、`hull_seam` 焊缝带、`handrail` 扶手 — 均为宿主 part visual，位置由宿主表面（hull_r / collar_ro）逐-尺寸派生（Rule 4 共形，随 ③⑤ 移动）。source_type=record_only（origin/bolt_ring_count/latch_dog_count/spoke_count）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：hull_radius_scale[0.90,1.10]、collar_scale[0.90,1.15]、lid_open[1.55,2.00]、dome_height[0.10,0.20]、cover_open[1.2,1.6]。关节运动包络（每个非-continuous joint）：hatch_hinge REVOLUTE axis Y，rest q=0=开，闭合方向 -Y，[闭合 -lid_open, 开 0.08]；leaf_hinge REVOLUTE axis ±Y，外开，[0, lid_open]；hatch_slide PRISMATIC axis Y，[0, slide_open]；cover_hinge REVOLUTE tangent，[0, cover_open]；handwheel_spin REVOLUTE Z，[-2.6, 2.6]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；targeted `ctx.pose` — swing lid 闭合覆盖 opening、leaf 外开抬离 seal、slide 平移让开 opening、cover 掀起离壳、handwheel 转动扫辐条。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal；配色 ≥5 colorway：`nasa_white`（白壳 + 灰板 + 棕封 + 银五金）、`iss_module`、`soyuz_green`、`bare_alloy`、`charcoal_service`、`copper_thermal`。材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 round/square/hex 三种孔径、flat 与 domed 两种
lid、swing/double/slide 三种 closure、0/N covers、材质配色多样、hinge/slide/cover
全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- round aperture: closure 4 × cover_count 4 = 16；square/hex aperture: closure 1
  (single) × cover_count 1 (0) = 1，×2 forms = 2。合计 arch 层 **18**，再乘 ④ 装饰档
  bolt 2 × dog 2 × spoke 2 = 8 → **≈144**（含装饰档；结构 arch 18）。

理由：结构词汇在此收敛——所有样本共享同一「pressurised 壳 + collar/seal + 可动舱门 +
handwheel」cell，可动骨架只有三种 + 一根可选 cover 复制 + 两种 lid 形态 + 三种孔径。
不硬凑组合空间（质量红线：不反推上游变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 aperture_form、closure_module、cover_count、bolt/dog/spoke count、palette、
连续 scale，再按 compatibility gate（square/hex→single_swing_lid + cover 0 + dog 8；
非-round→domed/double/sliding 不可达）在 `resolve_config` 求解。seed 0 pinned 到
origin 母本组合（round_aperture + single_swing_lid, 0 covers, 12 bolts / 8 dogs /
3 spokes, nasa_white）作为 documented regression anchor（sparse override，其余全
procedural）。random sweep `0-15`（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 ≈144
（见上，结构 arch 18），低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`hull_radius_scale`（hull_r 派生）、`collar_scale`
（collar_ro/opening_ri/slide_open 派生）、`lid_open`、`dome_height`（conditional）、
`cover_open`（conditional）。全部在 `resolve_config` clamp / 派生；不破坏 captured
pin/lug/rail 接口、hinge/slide 原点、multiplicity。连续尺寸契约：先采 independent
（hull_radius_scale/collar_scale/lid_open）→ equation 派生 collar_ro/opening_ri/
slide_open → conditional 解析 dome_height/cover_open/gates。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 aperture→closure→covers→decoration counts，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | square/hex → single_swing_lid + cover 0 + dog 8（gate）；domed/double/sliding → 仅 round；covers 与 closure 正交（挂圆端板） | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 5 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| shell_aperture | 3 | yes | yes | round/square/hex |
| closure | 4 | yes | yes | single-swing/domed-swing/double-leaf/sliding |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ cover/bolt/dog/spoke axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (square/hex → single_swing_lid + cover 0 + dog 8; domed/double/sliding → round only) in `resolve_config`
- controlled local scales clamped; cannot break captured pin/lug/rail interfaces, hinge/slide origin honesty, or multiplicity
- cross-part scale dependencies (collar_ro/opening_ri/slide_open) derived in `resolve_config`
- captured pin/lug/rail overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: hatch_hinge REVOLUTE(Y) / leaf_hinge REVOLUTE(±Y) / hatch_slide PRISMATIC(Y); cover_hinge REVOLUTE(tangent); handwheel_spin REVOLUTE(Z)
- copied `debris_cover_i` / `plate_bolt_i` / `latch_dog_j` / `wheel_spoke_j` follow naming + placement policy
- `run_astronomy_pressurised_module_door_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Swing lid/leaf/slider closed pose overlaps the collar or seal (no hover gap) → keep the closed lid seal ring hovering 0-0.02 above the collar seal (copy origin offsets); never bury it.
- Sliding lid open travel does not clear the opening, or drops vertically → set `slide_open = 2*collar_ro + margin`, PRISMATIC axis Y, and assert the lid stays at rail-cap height across the travel.
- double_leaf open pose self-intersects the two half-leaves, or the closed leaves gap at the meeting edge → half-disc `side` sign correct per leaf, rest q=0 = both closed meeting at centre, open lifts free edge above seal.
- Debris cover open pose collides with the open swing lid or with a neighbour → cap `cover_open`, half-step angular offset, gate covers to round aperture; never mask a real lid/cover 穿模 with a broad allow_overlap.
- Aperture-form swap leaves dogs/strikes/bolts floating off the new collar face (constant-radius decoration on a square/hex rim) → derive dog/strike placement from the realized rim (radial for round/hex, square-rim for square; Rule 4).
- Downgrading `_dome_cap_profile` LatheGeometry / rounded-square fillets / `_half_disc` arcs to crude Box/Cylinder placeholders (Rule 3 violation).

## 与相邻类别的边界

- 不该混入：**Industrial / Blast door**（平面壁挂矩形装甲叶 + 门框，无 pressurised
  圆柱壳、无 collar/seal/handwheel 身份特征）。
- 不该混入：**Astronomy / Return capsule**（钟形/球形再入体，舱门只是大体量热盾体上的
  小细节，非「壳 + 舱门」为主体的拓扑）。
- 不该混入：一个普通带铰链的圆盖（无 pressurised 壳、无 raised collar + tan seal +
  latch dog ring + handwheel 身份特征）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | `hex_aperture` 为 ③ Primary Form Family world_knowledge_extrapolation（锚定 square_hatch 的 cadquery 多边形 ring/solid 惯用 + origin part tree），待人工背书类别忠实。square/hex 孔径仅与 single_swing_lid 兼容（弯曲/半盘/滑轨样本仅 round 存在），是忠实于样本证据的门控，非稀释。 |

## 模板实现备注（可选）

- collar/opening/plate 几何量（collar_ro/opening_ri/plate_top/seal_top/slide_open）
  single-sourced in `ResolvedConfig`（Contract 3c），closure 与 covers 挂点全部从中派生。
- captured pin/lug/rail socket → 原始 joint（no MatingContract, grandfathered）+
  element-scoped `allow_overlap`，与全部 5 星源一致（Rule 2 例外）。
- 所有 N 个 debris cover 共享 `cover_panel`/`cover_lug`/`cover_grip` mesh；两 leaf
  共享 `_half_disc` helper；rail rib + carriage mesh 各建一次复用 —— 保编译预算。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：shell root 声明
  downstream；closure 只声明 downstream（re-export shell）→ 无自动 chain joint，模块发
  原始 joint 到 shell（parallel-children，同 Tipping_Barrow 惯用）。
- closure 模块把 hinge bracket/pin（swing/dome）、leaf brackets（double）、slide rails
  （sliding）作为 static visual 加到 `airlock_shell` part（模块特定的挂载硬件），covers
  由 shell 模块发射；lid/leaf 上的 dogs/lugs/strap 为宿主 visual（Rule 1）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | round_aperture + single_swing_lid | `rec_a-round-eva-...d440cc9f` (origin 母本) | L34-L354 | shell part tree（hull/collar/seal/plate）, 圆孔径, swing lid + REVOLUTE hinge, handwheel, dogs/strikes/bolts, 全部 test 语义 |
| S2 | A ④ | bolt_count=24 | `rec_module_door_var_bolt_ring_count` | L48, L96 | bolt ring multiplicity 上界 |
| S3 | B/④ | dog_count=12 | `rec_module_door_var_latch_dog_count` | L48-L51, L107-L108, L179-L180 | dogs+strikes paired multiplicity 上界 |
| S4 | B ④ | spoke_count=5 | `rec_module_door_var_spoke_count` | L218-L220 | handwheel spoke multiplicity 上界 |
| S5 | B ③ | domed_swing_lid | `rec_module_door_var_dome_lid` | L52-L68, L169-L181 | 凸球冠 dome lid（Volumetric Envelope Form, LatheGeometry cap） |
| S6 | A ③ | square_aperture | `rec_module_door_var_square_hatch` | L74-L119, L179-L223, L261-L309 | 圆角方形孔径/collar/seal/lid（Planar Boundary Form）+ 方形周边 dog/strike |
| S7 | B ① | double_leaf | `rec_module_door_var_double_leaf` | L61-L78, L149-L323 | 双半盘对开叶（① skeleton, 2 REVOLUTE 铰链） |
| S8 | B ② | sliding_hatch | `rec_module_door_var_sliding_hatch` | L62-L96, L161-L310 | PRISMATIC 侧滑口袋门 + rail/carriage |
| S9 | A/① | cover_count=8 (radial covers) | `rec_module_door_var_radial_covers` | L48-L77, L267-L323 | 径向防尘盖 shutter ring（① 会动 part multiplicity, REVOLUTE tangent hinge） |
