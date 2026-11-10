# Healthcare / First aid box — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_First_aid_box` |
| template path | `agent/templates/Healthcare_First_aid_box.py` |
| test path (optional) | `tests/agent/test_Healthcare_First_aid_box_template.py` (not authored; sweep is the gate) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children hub + multiplicity: base hub → lid/flap/handle/latch×N/tray×N) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | all synced 5★ sources for the PORTABLE first-aid hard case (source map `Healthcare__First_aid_box.md`) |
| source_index_policy | only adopted module sources indexed below; wall-cabinet origin excluded (overlaps Science/First_aid_cabinet) |

Sources (all `data/records/<id>/revisions/rev_000001/model.py`):
- **S1 parent** `rec_a-portable-first-aid-hard-case-a-rigid-rectangul_...f2b56491` — rigid rectangular case: `base` (cadquery `_hollow_open_box` rounded-rect shell + dark floor pad + tray ledges + front red cross + rear hinge barrel + latch strikes), `tray` PRISMATIC lift, `lid` REVOLUTE (open-bottom skirt + rounded slab top), `handle` REVOLUTE folding loop (`tube_from_spline_points`), `latch_0/1` REVOLUTE draw-latches.
- **S2 clamshell** `rec_firstaid_var_clamshell` — half-height `base` via `_three_wall_base` (front wall cut) + `front_flap` REVOLUTE drawbridge (bottom-front hinge, both halves open) + front_hinge_barrel; lid is top half-shell.
- **S3 cantilever** `rec_firstaid_var_cantilever_trays` — 2 `tray_arm_{i}` flat links REVOLUTE about +Y at tiered pivot bosses on inner side walls; `tray_{i}` FIXED to arm tip (tackle-box fan-out).
- **S4 rounded_tin** `rec_firstaid_var_rounded_tin` — vintage-tin ③ form: base `_hollow_open_box(..., fillet_top_bottom=0.005)` + `_domed_lid_shell` gently domed crown.
- **S5 stacked** `rec_firstaid_var_stacked_trays` — 3 `tray_{i}` PRISMATIC lift trays, per-level ledges, N-multiplicity.
- **S6 side_handles** `rec_firstaid_var_side_handles` — NO folding handle; fixed molded grab grips recessed into both short ends (`end_handle_recess/rim/bar_{side}` base visuals, no joint).

## 核心身份

A **PORTABLE first-aid hard case**: a rigid (or softly rounded vintage-tin) rounded-rectangular
box ~0.25–0.35 m wide with a hinged top lid, one or two front draw-latches, an interior of
lift-out / cantilever / stacked compartment trays, and a carry handle (folding top loop OR fixed
recessed end grips). It is a hand-carried case that sits on a surface, not mounted to anything.

**Not** a wall-mounted first-aid cabinet (shallow rectangular body + single side-hinged door, no
trays/handle/latches) — that layperson picture is served by the existing `Science/First_aid_cabinet`
template and was deliberately excluded from this source set. **Not** a tool/tackle box proper
(`tackle_box_with_simple_hinged_lid`) — identity here is medical (red cross + white field decal,
first-aid palettes, medicine trays), not fishing tackle.

## 槽位 + 候选模块表

### Slot A：lid / closure mechanism（顶盖闭合）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_top_lid | forked_anchor | S1 | L207-L251 | eligible if compatible | one full-cover top lid, REVOLUTE −X at rear edge; base full-height |
| clamshell_dual | forked_anchor | S2 | L226-L314 | eligible if compatible | half-height base + top-half `lid` REVOLUTE + `front_flap` drawbridge REVOLUTE +X at bottom-front; both halves open |

2 candidates (degrade reason: only two structurally distinct closure topologies exist in the 5★ pool — a
single top lid vs a two-leaf clamshell; a third would be a re-skin). Both source-backed.

### Slot B：interior organization（内部收纳）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_lift_tray | forked_anchor | S1 | L134-L205 | eligible if compatible | one lift-out compartment tray, PRISMATIC +z on side ledges |
| cantilever_tiers | forked_anchor | S3 | L169-L227 | eligible only with single_top_lid | 2 flat link arms REVOLUTE +Y (tiered), tray FIXED to each arm tip |
| stacked_trays | forked_anchor | S5 | L199-L212 | eligible only with single_top_lid | N∈{2,3} nested lift trays, each PRISMATIC +z on its own ledge level |

3 candidates. cantilever_tiers / stacked_trays require a full-height base cavity → gated to
single_top_lid (Slot A). clamshell_dual → forced single_lift_tray (shallow half-shell base).

### Slot C：handle（提携）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| folding_top_handle | forked_anchor | S1 | L253-L289 | eligible if compatible | spline-tube carry loop `handle`, REVOLUTE +X on lid top; lid gets handle_mounts |
| fixed_side_grips | forked_anchor | S6 | L132-L166 | eligible if compatible | recessed molded grip (recess + rim + metal bar) on both short ends; parent.visual on base, no joint |

2 candidates (degrade reason: the 5★ pool has exactly two carry solutions — a moving top loop vs fixed
end grips). Both source-backed.

### Slot D：body form / Primary Form Family ③

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| rigid_rect | forked_anchor | S1 | L40-L62 | Volumetric Envelope Form | eligible if compatible | crisp rounded-rect shell (small corner radius, no top/bottom fillet); flat skirt+slab lid |
| rounded_tin | forked_anchor | S4 | L50-L99 | Volumetric Envelope Form | eligible if compatible | softly rounded vintage tin: `fillet_top_bottom` body edges + gently `_domed_lid_shell` crown |

2 candidates (degrade reason: the observed primary-form space of a portable first-aid case is narrow —
crisp hard case vs rounded tin; both anchored to real records). Registered as the ③ slot in `slot_choices`.
Both keep the SAME part tree, SAME cadquery shell primitive family, SAME rim/lid/tray interfaces; they
differ only in the discrete envelope form (edge fillet + lid crown), a legal ③ structural distinction.

## 槽位图（slot graph）

pattern: mixed — `base` is the grounded hub; every other module parents to it (or to the lid).

```
                base  (root; cadquery hollow rounded-rect shell, Slot D form)
                 │
   ┌─────────────┼───────────────┬──────────────────┬─────────────────────┐
   │             │               │                  │                     │
 [Slot A]     [Slot B]        [Slot C]           latch×N               (Slot C alt)
 lid          interior        folding handle     draw-latches          fixed side grips
 REVOLUTE −X  PRISMATIC/       REVOLUTE +X        REVOLUTE +X           parent.visual on
 rear rim     REVOLUTE arms    on LID top         on base front         base short ends
   │           (base→tray/arm)  (lid→handle)       (base→latch_i)        (no joint)
   └─[clamshell only]→ front_flap REVOLUTE +X at base bottom-front edge
```

Interface points (all real face contacts unless noted):
- base rim `base_wall`(+z) ── lid `lid_skirt`/`lid_dome`(−z): closed lid seats on rim; REVOLUTE −X, origin on `rear_hinge_barrel`.
- base `front_hinge_barrel` ══ `front_flap` `flap_panel` (coaxial captured pin): REVOLUTE +X drawbridge at bottom-front edge; `mating` OMITTED (grandfathered pin-in-barrel per AUTHORING Rule 2), element-scoped `allow_overlap` (clamshell only).
- base `tray_ledge_{i}_0`(+z) ── `tray_{i}` `tray_floor`(−z): tray rests on ledge; PRISMATIC +z.
- lid `handle_mount_0`(+z) ── `handle` `handle_pivot_0`(−z): loop pivots on lid; REVOLUTE +X.
- base `latch_strike_{i}`(−y) ── `latch_{i}` `clasp_plate`(+y): draw-latch on front face; REVOLUTE +X.
- arm `arm_cradle_{i}`(+z) ── `tray_{i}` `tray_floor`(−z): tray FIXED on arm tip (cantilever), via `mount_fixed`.
- base `arm_pivot_boss_{i}` ══ arm `arm_pivot_pin_{i}` (coaxial captured hinge pin): REVOLUTE +Y, `mating` OMITTED (grandfathered pin-in-sleeve per AUTHORING Rule 2), element-scoped `allow_overlap`.

## 每槽位 Module Emits / Interfaces

### base hub (root; Slot D form)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` | S1 L74 |
| visuals | `base_wall`(cadquery shell), `empty_compartment`(dark floor pad), `tray_ledge_*`, `cross_field`+`cross_vertical`+`cross_horizontal`(④ decal), `rear_hinge_barrel`, `latch_strike_{i}`; (rounded_tin) fillet_top_bottom + softer corner radius; (clamshell) `_three_wall_base` + `front_hinge_barrel` + `flap_seat`; (fixed_side_grips) `end_handle_recess/rim/bar_{side}` | S1/S2/S4/S6 |
| internal joints | none | — |
| downstream interfaces | rim `base_wall`+z (lid), ledges `tray_ledge_*`+z (trays), front `latch_strike_*`−y (latch), `flap_seat`+z (flap) | S1 |

### Slot A / single_top_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` | S1 L207 |
| visuals | `lid_skirt`(open-bottom cadquery shell) or `lid_dome`(rounded_tin), `lid_top`(rounded slab; flat form only), `dark_lid_liner`, `latch_keeper_{i}`, (folding handle) `handle_mount_{i}` | S1/S4 |
| joint | `base_to_lid` REVOLUTE axis(−1,0,0) origin(0,+D/2,base_h) range[0,1.85]; MatingContract base_wall+z ↔ lid_skirt/lid_dome−z | S1 L243 |

### Slot A / clamshell_dual
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` (top half), `front_flap` | S2 L227/L273 |
| joints | `base_to_lid` REVOLUTE −X (rim seat mating); `base_to_front_flap` REVOLUTE axis(1,0,0) origin(0,−D/2,0) range[0,1.50]; captured pin-in-barrel (mating omitted, grandfathered) | S2 L262/L305 |

### Slot B / single_lift_tray · stacked_trays · cantilever_tiers
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tray_{i}` (floor+4 walls+dividers+front_pull); cantilever adds `tray_arm_{i}` | S1 L134 / S5 L66 / S3 L78 |
| joints | `base_to_tray_{i}` PRISMATIC axis(0,0,1) range[0,travel], MatingContract tray_ledge_{i}_0+z ↔ tray_floor−z; cantilever: `base_to_tray_arm_{i}` REVOLUTE +Y (mating omitted, captured pin) + `tray_arm_{i}_to_tray_{i}` FIXED via mount_fixed (arm_cradle+z ↔ tray_floor−z) | S1/S5/S3 |

### Slot C / folding_top_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle` (`tube_from_spline_points` loop + `handle_pivot_{i}`) | S1 L253 |
| joint | `lid_to_handle` REVOLUTE axis(1,0,0) origin(0,−D/2,lid_top_z+0.007) range[0,1.45]; MatingContract handle_mount_0+z ↔ handle_pivot_0−z | S1 L281 |

### Slot C / fixed_side_grips
| emits | 描述 | 来源 |
|---|---|---|
| visuals (on base, no part/joint) | `end_handle_recess_{side}`(dark pocket), `end_handle_rim_{side}`(frame), `end_handle_bar_{side}`(metal grip cylinder) | S6 L132 |

### latch×N
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch_{i}` (`clasp_plate`+`clasp_lip`+`clasp_pivot`) | S1 L291 |
| joint | `base_to_latch_{i}` REVOLUTE axis(1,0,0) origin(x,−D/2−0.0055,base_h−0.040) range[0,1.20]; MatingContract latch_strike_{i}−y ↔ clasp_plate+y | S1 L311 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| lid_module | enum | single_top_lid / clamshell_dual | single_top_lid | choice | procedural sampler | Slot A |
| interior_module | enum | single_lift_tray / cantilever_tiers / stacked_trays | single_lift_tray | conditional | cantilever/stacked only if lid=single_top_lid; else single_lift_tray | Slot B + _gate |
| handle_module | enum | folding_top_handle / fixed_side_grips | folding_top_handle | choice | procedural sampler | Slot C |
| body_form | enum | rigid_rect / rounded_tin | rigid_rect | choice | procedural sampler (③) | Slot D |
| latch_count | int | {1, 2} | 2 | independent | weighted draw; mirrored on front face | S1 multiplicity |
| tray_count | int | {2, 3} (stacked only) | 3 | conditional | active only for stacked_trays; else 1 (single/cantilever fixed) | S5 |
| palette_style | enum | red_white / white_red / safety_green / medical_orange / olive_tin / clinical_blue | red_white | choice | drives every material | ⑥ |
| width_scale | float | [0.90, 1.10] | 1.0 | independent | W = 0.30·width_scale | S1 |
| depth_scale | float | [0.90, 1.10] | 1.0 | independent | D = 0.12·depth_scale | S1 |
| height_scale | float | [0.90, 1.10] | 1.0 | independent | base_h/case_h · height_scale | S1 |
| (—) | constraint | — | — | equation | tray_w = W − 0.035; tray_d = D − 0.030; tray_bottom_z = base_h − tray_h − 0.008; tray_travel = base_h + 0.010 − tray_bottom_z | interior fit |
| (—) | constraint | — | — | inequality | clamshell: case_h split base_h=lid_h=case_h/2; interior forced single tray so tray_h+gap ≤ base_h | Slot A×B |

## 7.5 编译预算 / compile budget
Self-reported budget: **≤22 s/seed** (sweep `--compile-timeout 120`, ~5× watchdog).
Per seed the heavy ops are the cadquery shells: `base_wall`/`_three_wall_base` (1), lid `lid_skirt`/`lid_dome` (1),
optional `lid_top` rounded slab (1), and the `tube_from_spline_points` handle mesh (1, folding only). All
cadquery shells use `corner_segments=10` and `tolerance=0.0006–0.0008` (source-proven). Trays are cheap Box
panels reused across N via a shared helper `_build_tray`. Total ~2–4 mesh/CAD ops/seed → well inside budget.

## Multiplicity / Copy Logic

**Axis 1 — latch_count** (front draw-latches):
- `count_param=latch_count`, `N_range={1,2}` (product + test); sampling domain weighted (0.30→1, 0.70→2, sample favours the observed 2).
- copied object: `latch_{i}` (clasp_plate+clasp_lip+clasp_pivot); naming `latch_{i}`; placement mirrored across X on the front face (count=1 centered x=0; count=2 at x=±0.074·W/0.30); joint policy uniform `base_to_latch_{i}` REVOLUTE +X. Source S1 shows N=2.

**Axis 2 — tray_count** (stacked lift trays):
- `count_param=tray_count`, `N_range={2,3}` (stacked_trays module only; single_lift_tray=1, cantilever=2 arms are fixed by module). sampling: uniform over {2,3}.
- copied object: `tray_{i}` on its own ledge level + `base_to_tray_{i}` PRISMATIC; naming `tray_{i}`, `tray_ledge_{i}_{0,1}`; placement stacked along z at even rest levels; joint policy uniform. Source S5 shows N=3.

(No shared cross-axis sampling helper abstracted — only two multiplicity templates so far; follow VARIANT_PIPELINE discipline.)

## 视觉多样性 6 轴考察
| 轴 | 怎么判断 | 有/无 | 取值 / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part | 有 | base hub + {single lid} vs {lid+front_flap}; interior {1 tray} / {2 arms+2 trays} / {N stacked trays}; +latch×N; handle part present iff folding. forked_anchor S1/S2/S3/S5/S6 |
| └ multiplicity | 同构件 ×N | 有 | latch {1,2}; stacked tray {2,3} — see §8 |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE (lid −X, flap +X, latch +X, handle +X, cantilever arm +Y), PRISMATIC (lift trays +z), FIXED (cantilever tray→arm). Each type appears in sweep. forked_anchor S1/S2/S3/S5 |
| ③ 主体形态家族 | 换核心几何形态原型 | 有 | Slot D: rigid_rect vs rounded_tin (Volumetric Envelope Form); registered in `slot_choices`. forked_anchor S1/S4 |
| ④ 表面装饰 | 叠加表面细节 | 有 | red-cross-on-white-field decal (host-derived on front face y=−D/2, or on flap for clamshell), latch escutcheons/keepers, tray dividers. record_only S1/S2 + host-conformal |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | W∈0.27–0.33, D∈0.108–0.132, case_h∈0.166–0.204; lid swing [0,1.85]≈106°, flap [0,1.50], latch [0,1.20], handle [0,1.45], tray lift [0,travel]. Motion plan below. record_only S1 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 palettes: red_white / white_red / safety_green / medical_orange / olive_tin(vintage) / clinical_blue; material大类 painted-metal + plastic + chrome hardware (≥ ceil(0.5·6)=3 大类). |

**motion_test_plan**: `run_first_aid_box_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`
plus targeted `ctx.pose(...)`: lid opens up (z↑), flap opens forward/down (−y), each tray lifts above rim, latch_0 flips
outward (−y), folding handle lifts. Sequenced overlaps declared element-scoped: tray/arm ↔ closed lid (lift only when lid
open), hinge barrels ↔ lid/base, latch clasp ↔ strike/keeper, cantilever pin ↔ boss. No sampled-pose exemption needed.

## 拓扑多样性审计

总组合数（可达）：
- single_top_lid × {single_lift_tray, cantilever_tiers, stacked_trays(2), stacked_trays(3)} × {folding, side_grips} × {rigid, rounded} × latch{1,2} = 4×2×2×2 = 64
- clamshell_dual × {single_lift_tray} × {folding, side_grips} × {rigid, rounded} × latch{1,2} = 1×2×2×2 = 8
- Total ≈ 72 distinct topology tuples (before continuous scales).

理由：Slot A 2, Slot B 3(+N), Slot C 2, Slot D 2 — every registered slot key realizes ≥2 distinct values in 0-35.

seed_domain_policy：procedural_first（`config_from_seed(seed)` = deterministic `random.Random(seed)` weighted draws; seed 0 not special).
Procedural Sampling / Sweep Plan：sample lid/handle/body_form/palette independently; sample interior then `_gate` to legal (clamshell→single tray); sample latch_count{1,2} and tray_count{2,3}; clamp scales in `resolve_config`; `_gate` prevents illegal (cantilever/stacked on clamshell). No regression overrides. Sweep 0-35 for pass, corner stage auto.
Topology target：1000-seed distinct ~72 (category is combinatorially bounded; below 300 is inherent to a 2×3×2×2 slot space — acceptable per spec note).（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：width_scale/depth_scale/height_scale ∈[0.90,1.10] clamped in `resolve_config`; tray footprint + rest z + travel derived (equation) from W/D/base_h; do not break rim/ledge/latch interfaces.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order lid→interior→handle→body_form→palette→latch_count→tray_count; weighted; `_gate` legality | slot_choices_for_seed matches build |
| compatibility matrix | clamshell ⇒ interior=single_lift_tray; cantilever/stacked ⇒ lid=single_top_lid | no shallow-base overflow / floating |
| controlled local variation | 3 body scales + derived tray fit, clamped | proportions vary without breaking mating/clearance |
| regression overrides | none | — |
| random sweep | 0-35 initial; corner auto | contract failures; axis_realization |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A lid | 2 | yes | no | only two closure topologies in pool |
| B interior | 3 | yes | yes | +N multiplicity |
| C handle | 2 | yes | no | moving loop vs fixed grips |
| D body_form | 2 | yes | no | ③ crisp vs rounded tin |

## Validator
- slot_choices_for_seed returns implemented module names (lid/interior/handle/body_form + latch/tray N labels)
- config_from_seed uses deterministic procedural sampling for all seeds incl. seed 0
- `_gate` prevents cantilever/stacked on clamshell and clamshell multi-tray
- no regression overrides
- body scales clamped in resolve_config; tray fit derived, never a frozen constant
- MatingContract on lid (rim seat) / tray-lift (ledge) / handle (mount) / single-lid latch (strike) + cantilever tray→arm FIXED; flap drawbridge pin, cantilever arm pin, clamshell draw-latch hook all grandfathered captured-pin/hook (Rule 2)
- key joints: lid REVOLUTE −X, flap REVOLUTE +X, latch REVOLUTE +X, tray PRISMATIC +z, handle REVOLUTE +X, cantilever arm REVOLUTE +Y
- copied latch_{i}/tray_{i} follow naming + mirror/stack placement

## Reject cases
- Trays/latches/handle spawned as FIXED decorative parts instead of real articulations, or the red cross made a FIXED part (must be parent.visual).
- Downgrading the cadquery `_hollow_open_box` / `_domed_lid_shell` shells to bare `Box` (loses hollow cavity + rounded/tin ③ identity).
- cantilever_tiers or stacked_trays selected on a clamshell (shallow) base → tray overflow / floating.
- Lid/flap/tray/latch joint with no MatingContract (except grandfathered captured cantilever pin) → phantom anchor.
- Tray lifts through a CLOSED lid without a sequenced `allow_overlap` (must open lid first) or an over-wide travel that pierces the lid.
- Monochrome output (single palette) — palette_style must drive every material.
- Wall-cabinet-style single side door with no trays/handle (that is First_aid_cabinet, not this).

## 与相邻类别的边界
- 不该混入：`Science/First_aid_cabinet`（wall-mounted shallow cabinet + side door; no carry handle / trays / draw-latches — the excluded origin).
- 不该混入：`tackle_box_with_simple_hinged_lid`（same box+lid+tray+latch mechanics but fishing-tackle identity; here the decal/palette/trays are medical).
- 不该混入：`Bag_Suitcase_*`（soft/large luggage; this is a small rigid medical case).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Portable hard case only; wall cabinet excluded (origin reconciled in source map). 6 sources > 5 threshold. |
