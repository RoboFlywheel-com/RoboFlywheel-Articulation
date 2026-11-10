# Modular Spec — Agricultural / Harvester vehicle (arm)

## 元信息
| 项 | 值 |
|---|---|
| slug | `harvester` |
| template path | `agent/templates/harvester.py` |
| test path (optional) | `tests/agent/test_harvester_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear_chain carrier→[turret]→boom→stick→head→grapple + wheels/rollers/finger multiplicity + parallel finger children) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (3 origins + 6 slot-fork variants) |
| source_index_policy | only adopted module sources are indexed below |

3 distinct origins fully seed the structural slots:
- **P1** `rec_use-…_26d122a9` — pedestal king-post base + **inverted-V** two-section boom + 4-finger felling grapple (rotator CONTINUOUS + `claw_finger_{i}` REVOLUTE). Isolated arm (no carrier).
- **P2** `rec_use-…_f77bf836` — John-Deere-green **wheeled bogie** carrier (6 wheels / 3 axles, CONTINUOUS) + glazed cab + 2-section **knuckle** boom + processing head (feed rollers/saw/delimbing knives) + one REVOLUTE `grapple_arm`.
- **P3** `rec_use-…_e451456d` — Komatsu-red **tracked crawler** + **turret slew** (REVOLUTE ±1.45 about Z) + 2-section knuckle boom + processing head.

6 forks fill the rest: `boom_telescopic` (stick→outer+inner PRISMATIC), `head_feller_saw` (saw disc + 2 `grab_arm` REVOLUTE), `head_log_grapple` (`grapple_frame`+rotator CONTINUOUS + 2 `jaw` REVOLUTE), `head_mulcher` (`mulcher_hood`+`mulcher_drum` CONTINUOUS + loop `tooth_{i}`, GATED), `track_rollers_6` (rollers 4→6/side), `wheels_8` (axles 3→4 / wheels 6→8, refactored to a computed `num_axles` loop).

## 核心身份

A forestry **harvester vehicle (arm)** = a self-propelled (or pedestal-mounted) carrier + an **articulated hydraulic crane/boom ARM** + a **harvester/processing head** end-effector. The "(arm)" makes the boom+head central: the defining silhouette is a heavy boxed multi-section boom reaching forward from a carrier, with a tool head hanging off the wrist. Kinematic spine: `carrier →[turret slew, tracked only]→ boom →(elbow)→ stick →(wrist)→ head →(rotator/fingers/jaws/drum)`. Joints are mostly REVOLUTE (boom lift, elbow, wrist), plus CONTINUOUS (wheels, head rotator, mulcher drum), PRISMATIC (telescopic extend), and a REVOLUTE-Z turret slew.

Not to be confused with: a **forwarder/log-loader** (a bunk-bed log carrier — no processing head), a bare **excavator** (bucket, not a forestry head), a **feller-buncher standalone** or a **standalone mulcher machine** (must still read as a boom-ARM carrying an attachment). The mulcher head is GATED for exactly this reason.

## 槽位 + 候选模块表

### Slot A：undercarriage（① 骨架图 root carrier + ② turret slew）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `wheeled_bogie` | forked_anchor | P2 `f77bf836` | L98-L332 | eligible if compatible | 1 `chassis` part; glazed cab greenhouse (inline visuals); `num_axles` bogie wheels as CONTINUOUS `*_wheel` parts (TireGeometry+WheelGeometry mesh); boom mounts directly on chassis (no turret) |
| `tracked_crawler` | forked_anchor | P3 `e451456d` | L60-L163 | eligible if compatible | 1 `chassis` part (rubber tracks + idlers + `*_roller_{i}` FIXED + grousers, all inline) + separate `turret` part on a REVOLUTE-Z **slew** joint; boom mounts on turret |
| `pedestal_static` | forked_anchor | P1 `26d122a9` | L95-L114 | eligible if compatible | 1 `base_mount` king-post column grounded at z=0 (backing block + king-post + cap + clevis ears + parking hook mesh); no wheels/tracks/slew; boom mounts on king-post |

### Slot B：boom_type（① 骨架图 arm sections + ② joint type）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `knuckle_2section` | forked_anchor | P3 `e451456d` (+P2) | L127-L201 | eligible if compatible | `boom` boxed lower section (REVOLUTE lift) + `boom_stick` boxed outer section (REVOLUTE elbow); side plates, pivot barrels, hydraulic barrel/rod pairs, warning-label decal, hose; wrist at stick tip |
| `inverted_V` | forked_anchor | P1 `26d122a9` | L118-L191 | eligible if compatible | `boom` member rising to an apex knuckle (REVOLUTE lift) + `boom_stick` member descending to the wrist (REVOLUTE elbow) — same 2-revolute topology, distinct up-then-down inverted-V ③ profile; slung lift cylinder + service hose |
| `telescopic_3section` | forked_anchor | `boom_telescopic` | L164-L243 | eligible if compatible | `boom` lower section (REVOLUTE lift) + `boom_stick` outer sleeve (REVOLUTE elbow) + `boom_stick_inner` telescoping member (PRISMATIC extend) with bronze guide pads/wear strips; wrist at inner tip |

### Slot C：head（"(arm)" 核心 slot，最丰富；① + ② + ③）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `processing_head` | forked_anchor | P3 `e451456d` (+P2) | L207-L236 | eligible if compatible | CTL processing head: `head` part (hanging link, backbone, painted motor cover, bottom feed frame, 2 `feed_roller` cyls, saw bar, 2 side `grapple_arm`+`delimbing_knife`, hose) — internals inline (Rule 1); motion = wrist REVOLUTE |
| `felling_grapple_4finger` | forked_anchor | P1 `26d122a9` | L195-L290 | eligible if compatible | wrist_yoke + `grapple_hub` on a CONTINUOUS **rotator** + N=4 `claw_finger_{i}` curved tines (REVOLUTE, close toward tool axis); yellow finger-drive cyls; mesh tube fingers |
| `feller_saw` | forked_anchor | `head_feller_saw` | L206-L265 | eligible if compatible | directional feller head: `head` (motor housing, `saw_disc` flat cylinder, saw guard, felling bar) + 2 accumulating `grab_arm_{i}` (REVOLUTE, close to bunch stems); no feed rollers |
| `log_grapple` | forked_anchor | `head_log_grapple` | L417-L528 | eligible if compatible | bypass loader grapple: `grapple_frame` (yoke+rotator housing) + `rotator` on CONTINUOUS joint + 2 curved `jaw_{i}` (REVOLUTE, clamshell close) with teeth/wear plates |
| `mulcher` | forked_anchor (GATED) | `head_mulcher` | L417-L545 | eligible if compatible; **gated** | rotary-drum mulcher attachment: `mulcher_head` hood box + `mulcher_drum` horizontal Cylinder on a CONTINUOUS joint carrying loop-emitted `tooth_{i}` bits. Gate: must still read as a boom-ARM with a mulcher attachment, not a standalone mulcher — enforced by keeping the full carrier+boom chain and the wrist REVOLUTE above the drum |

All Slot-C candidates expose the **identical wrist interface** (`head_wrist_pin` visual at head-local (0,0,0), body hanging −Z from the boom's wrist part), so any head mates any boom. Candidate distinction is genuine ①/②/③: different internal moving DOF (none / 4 fingers / 2 grab arms / rotator+2 jaws / 1 drum), joint types (REVOLUTE fingers/grab/jaws vs CONTINUOUS rotator/drum) and Primary Form Family (processing box vs finger-cage vs saw-disc vs clamshell-jaw vs drum-hood).

## 槽位图（slot graph）

pattern: `mixed`

```
undercarriage (Slot A, root carrier)
   │  [tracked_crawler ONLY] chassis --REVOLUTE axis=+Z (slew, ±slew)--> turret
   │  wheeled_bogie: N × chassis --CONTINUOUS axis=Y--> wheel_{i}   (multiplicity)
   ▼  boom mount = (boom_parent_part, pivot_xyz_local, base_pitch)
boom_type (Slot B)
   boom_parent --REVOLUTE axis=Y (boom_lift)--> boom
   boom --REVOLUTE axis=Y (boom_to_stick, elbow)--> boom_stick
   [telescopic ONLY] boom_stick --PRISMATIC axis=X (stick_extend)--> boom_stick_inner
   ▼  wrist mount = (wrist_part, wrist_xyz_local, wrist_pitch)
head (Slot C)
   wrist_part --REVOLUTE axis=Y (stick_to_head, wrist)--> head
   [felling_grapple] head --CONTINUOUS axis=Z (head_rotator)--> grapple_hub --REVOLUTE axis=Y ×4--> claw_finger_{i}
   [feller_saw]      head --REVOLUTE axis=Z ×2--> grab_arm_{i}
   [log_grapple]     head --CONTINUOUS axis=Z (head_rotator)--> rotator --REVOLUTE axis=X ×2--> jaw_{i}
   [mulcher]         head --CONTINUOUS axis=Y (head_to_drum)--> mulcher_drum
   [processing]      (no internal moving child — motion is the wrist)
```

Interface points:
- **boom mount** — the boom root pivot barrel (boom-local (0,0,0), captured in the carrier/turret yoke). Joint origin = `pivot_xyz` in the boom-parent's local frame; axis Y; the base up-pitch is baked into the joint-origin rpy. Captured-pin geometry → grandfathered (no MatingContract), guarded by flat articulation-origin baseline + element-scoped `allow_overlap`.
- **elbow** — boom tip barrel captured in the stick root yoke; joint origin at boom-local tip; axis Y.
- **telescopic slide** — inner member slides through the outer sleeve guide collars; PRISMATIC axis X, origin on the sleeve; guide-pad overlaps grandfathered.
- **wrist mount** — stick/inner tip barrel captured in the head hanging link; joint origin = `wrist_xyz` in the wrist-part local frame; axis Y.
- **rotator / drum / finger / jaw / grab pivots** — hub/rotator drum axis Z; finger/jaw/grab pins; all captured-pin → grandfathered + element-scoped `allow_overlap`.

Mutual exclusion / conditional: turret slew exists ONLY under `tracked_crawler`. Wheel multiplicity exists ONLY under `wheeled_bogie`; roller multiplicity ONLY under `tracked_crawler`; `pedestal_static` has no running-gear multiplicity.

## 每槽位 Module Emits / Interfaces

### Slot A / module wheeled_bogie
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (frame + green cab greenhouse + fenders + hood + guards, inline visuals); `front_left_wheel`…×2·N (tire+rim mesh + hub) | P2 / L159-L332 |
| internal joints | `chassis_to_{wheel}` CONTINUOUS axis=Y ×(2·num_axles) | P2 / L324-L332 |
| upstream interface | root (no upstream) | — |
| downstream interface | boom mount: parent=`chassis`, pivot on the front deck, base_pitch up | P2 / L373-L381 |

### Slot A / module tracked_crawler
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (rubber tracks + idlers + `*_roller_{i}` + grousers + red cab, inline); `turret` (turntable drum/neck + yokes) | P3 / L60-L114 |
| internal joints | `chassis_to_turret` REVOLUTE axis=Z (slew) | P3 / L115-L123 |
| upstream interface | root | — |
| downstream interface | boom mount: parent=`turret`, pivot above slew, base_pitch up | P3 / L155-L163 |

### Slot A / module pedestal_static
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base_mount` king-post column (backing block, king-post, top cap, clevis ears, parking-hook mesh) grounded at z=0 | P1 / L95-L114 |
| internal joints | none | — |
| upstream interface | root | — |
| downstream interface | boom mount: parent=`base_mount`, pivot at king-post clevis, base_pitch up | P1 / L139-L147 |

### Slot B / module knuckle_2section
| emits | 描述 | 来源 |
|---|---|---|
| parts | `boom` (box tube + side plates + pivot barrels + hydraulic pair + hose + label decal); `boom_stick` (box tube + wear plate + wrist barrel + crowd hydraulic + hose) | P3 / L127-L201 |
| internal joints | `boom_lift` REVOLUTE axis=Y; `boom_to_stick` REVOLUTE axis=Y | P3 / L155-L201 |
| upstream interface | boom root barrel at boom-local (0,0,0), captured in carrier/turret yoke | P3 / L132 |
| downstream interface | wrist mount: part=`boom_stick`, wrist tip barrel | P3 / L174 |

### Slot B / module inverted_V
| emits | 描述 | 来源 |
|---|---|---|
| parts | `boom` member rising to apex; `boom_stick` member descending to wrist; slung lift cylinder + hoses | P1 / L118-L191 |
| internal joints | `boom_lift` REVOLUTE axis=Y; `boom_to_stick` REVOLUTE axis=Y | P1 / L139-L191 |
| upstream interface | boom root barrel at (0,0,0) | P1 / L123 |
| downstream interface | wrist mount: part=`boom_stick`, wrist barrel | P1 / L159 |

### Slot B / module telescopic_3section
| emits | 描述 | 来源 |
|---|---|---|
| parts | `boom` lower section; `boom_stick` outer sleeve (guide collars + bronze bore lips); `boom_stick_inner` telescoping member (box tube + wear strips + guide pads + wrist barrel) | boom_telescopic / L123-L243 |
| internal joints | `boom_lift` REVOLUTE; `boom_to_stick` REVOLUTE; `stick_extend` PRISMATIC axis=X lower=0 | boom_telescopic / L190-L243 |
| upstream interface | boom root barrel at (0,0,0) | boom_telescopic / L128 |
| downstream interface | wrist mount: part=`boom_stick_inner`, wrist barrel | boom_telescopic / L213 |

### Slot C / module processing_head
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (hanging link, backbone, painted motor cover, feed frame, 2 feed rollers, saw bar, side grapple arms + delimbing knives, hose) — all inline (Rule 1) | P3 / L207-L226 |
| internal joints | none (motion = wrist) | P3 |
| upstream interface | `head_wrist_pin` at head-local (0,0,0) | P3 / L208 |
| downstream interface | — (tool tip) | — |

### Slot C / module felling_grapple_4finger
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (wrist yoke + rotator housing + palm); `grapple_hub` (rotator drum + palm + finger-drive cyls + bosses); `claw_finger_{i}` ×4 mesh tines | P1 / L195-L290 |
| internal joints | `head_rotator` CONTINUOUS axis=Z; `hub_to_finger_{i}` REVOLUTE axis=Y ×4 | P1 / L246-L290 |
| upstream interface | `head_wrist_pin` at (0,0,0) | P1 / L196 |
| downstream interface | — | — |

### Slot C / module feller_saw
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (motor housing, `saw_disc` flat cylinder, saw guard, felling bar, pocket brackets); `grab_arm_{i}` ×2 | feller_saw / L206-L265 |
| internal joints | `head_to_grab_{i}` REVOLUTE axis=Z ×2 | feller_saw / L257-L265 |
| upstream interface | `head_wrist_pin` at (0,0,0) | feller_saw / L207 |
| downstream interface | — | — |

### Slot C / module log_grapple
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (frame yoke + rotator housing + gussets); `rotator` (turntable + jaw carrier + pivot lugs); `jaw_{i}` ×2 curved clamshell jaws w/ teeth | log_grapple / L417-L528 |
| internal joints | `head_rotator` CONTINUOUS axis=Z; `rotator_to_jaw_{i}` REVOLUTE axis=X ×2 | log_grapple / L481-L528 |
| upstream interface | `head_wrist_pin` at (0,0,0) | log_grapple / L418 |
| downstream interface | — | — |

### Slot C / module mulcher (GATED)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` (wrist rotator + yoke + `mulcher_hood` box + side plates + motor + deflector/guard/ribs/skids); `mulcher_drum` horizontal Cylinder + end plates + shafts + loop `tooth_{i}` | mulcher / L417-L538 |
| internal joints | `head_to_drum` CONTINUOUS axis=Y | mulcher / L540-L545 |
| upstream interface | `head_wrist_pin` region at (0,0,0) | mulcher / L419 |
| downstream interface | — | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| undercarriage | enum | wheeled_bogie / tracked_crawler / pedestal_static | — | choice | deterministic procedural sampler | Slot A |
| boom_type | enum | knuckle_2section / inverted_V / telescopic_3section | — | choice | sampler | Slot B |
| head | enum | processing_head / felling_grapple_4finger / feller_saw / log_grapple / mulcher | — | choice | sampler | Slot C |
| num_axles | int | [2, 5] (wheels 4–10) | 3 | conditional | only when undercarriage=wheeled_bogie; weighted 3–4 common | P2/wheels_8 L253-L263 |
| rollers_per_side | int | [3, 8] | 4 | conditional | only when undercarriage=tracked_crawler; weighted 4–6 | P3/track_rollers_6 L69 |
| palette_style | enum | jd_green / komatsu_red / black_arm / ponsse_yellow / tigercat_orange / industrial_grey | jd_green | choice | sampler | ⑥ |
| boom_reach_scale | float | [0.88, 1.15] | 1.0 | independent | clamp | ⑤ reach ~2.6 main |
| stick_reach_scale | float | [0.88, 1.15] | 1.0 | independent | clamp | ⑤ reach ~2.0 stick |
| carrier_len_scale | float | [0.90, 1.12] | 1.0 | independent | clamp | ⑤ |
| carrier_width_scale | float | [0.92, 1.10] | 1.0 | independent | clamp | ⑤ |
| head_size_scale | float | [0.90, 1.12] | 1.0 | independent | clamp | ⑤ |
| base_pitch | float | derived | 0.50 | equation | `= 0.50` rad up-pitch of boom (fixed nominal, per undercarriage) | P3 L160 |
| tire_radius | float | derived | 0.55 | conditional | `= min(0.55, 0.46·axle_pitch)` so adjacent tires never overlap | ⑤ clearance |
| axle_pitch | float | derived | — | equation | `= carrier_usable_len / (num_axles−1)` | wheels_8 L258 |
| roller_pitch | float | derived | — | equation | `= track_run / (rollers_per_side−1)` | P3 L69 |
| (—) | constraint | — | — | inequality | head bottom z > ground (0) across all sampled boom poses; boom/stick/head stay forward of carrier at |slew|≤max — verified by sampled-pose collision guard; violations clamp joint ranges, not scales | interface / clearance |
| lift range | float | [−0.42, 0.55] | — | independent | REVOLUTE boom lift envelope (conservative, forward-up) | P3 L162 |
| elbow range | float | [−0.65, 0.72] | — | independent | REVOLUTE elbow envelope | P3 L200 |
| wrist range | float | [−0.95, 0.95] | — | independent | REVOLUTE wrist envelope | P3 L235 |
| slew range | float | [−0.60, 0.60] | — | conditional | tracked only; narrowed from source ±1.45 so slewed arm clears carrier in sampled poses | P3 L122 |
| telescopic travel | float | [0, 1.0] | — | conditional | telescopic only; PRISMATIC, keeps ≥0.2 m retained insertion at full extend | boom_telescopic L242 |

All `equation`/`inequality`/`conditional` constraints are solved in `resolve_config`.

## 7.5 编译预算 / compile budget
**Per-seed budget: ≤ 18 s** (self-report; heaviest seed = wheeled_bogie with TireGeometry+WheelGeometry meshes + felling_grapple mesh fingers). Basis: library reference 5–20 s typical; this category is box/cylinder-dominant with a few meshes. Tessellation tiers: tire tread ≤ 22 count, wheel spokes ≤ 8, hose/finger tube `radial_segments` ≤ 14, sphere ≤ 20×12. The tire and rim meshes are each built **once** and reused across all 2·N wheel parts (one shared `Mesh` per role). Grouser count capped ≈ 10/side. If a seed exceeds ~18 s, coarsen tire tread/spoke counts first. Sweep watchdog `--compile-timeout 120` (~7× budget) is a hang-guard only.

## 8. Multiplicity / Copy Logic

Two independent, mutually-exclusive count axes (only one is active per undercarriage) + one fixed finger count.

**Axis 1 — carrier wheels (`num_axles`, wheeled_bogie only)**
- `count_param` = `num_axles`; `N_range` = [2, 5] (wheels = 2·N ∈ [4, 10]); product domain [2,5]; sampling weights small-N biased: {2:0.15, 3:0.40, 4:0.30, 5:0.15}.
- copied object = one `*_wheel` part (shared tire+rim mesh) per axle-side; naming `wheel_{i}` with left/right; placement at computed `axle_pitch`; joint policy CONTINUOUS axis=Y; source P2/wheels_8 (computed loop). Encoded in slot_choices as `("running_gear", f"wheels{2*num_axles}")`.

**Axis 2 — track road rollers (`rollers_per_side`, tracked_crawler only)**
- `count_param` = `rollers_per_side`; `N_range` = [3, 8]; product domain [3,8]; weights {3:0.15, 4:0.30, 5:0.25, 6:0.20, 7:0.06, 8:0.04}.
- copied object = `side_{s}_roller_{i}` FIXED inline visual on the chassis; placement at computed `roller_pitch`; source P3/track_rollers_6. Encoded as `("running_gear", f"rollers{rollers_per_side}")`. Pedestal → `("running_gear", "static")`.

**Fixed — grapple fingers = 4** (`claw_finger_{i}`, felling_grapple only): a fixed source count (P1 loop), not exposed as a template-level count axis (single source). Feller grab arms = 2, jaws = 2, mulcher teeth loop = 18 — all fixed source counts, inline loops, not multiplicity axes.

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值 / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | undercarriage 3 (wheeled/tracked/pedestal; turret part only on tracked) × boom_type 3 (2-sec / inverted-V / 3-sec telescopic) × head 5 (processing none / 4-finger / 2-grab / rotator+2-jaw / 1-drum). All forked_anchor/source-backed. |
| └ multiplicity | 同构件 ×N | 有 | wheels N (axles [2,5]→wheels [4,10]) · rollers N [3,8]; see §8. N covered not counted. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE (boom lift / elbow / wrist / fingers-Y / grab-Z / jaws-X), CONTINUOUS (wheels-Y / head rotator-Z / mulcher drum-Y), PRISMATIC (telescopic-X), REVOLUTE-Z turret slew. Every declared type appears in the sweep across seeds. All source-backed. |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何原型 | 有 | undercarriage: wheeled greenhouse-on-tires / tracked crawler-with-turret / bare king-post pedestal (Volumetric Envelope). boom: straight boxed knuckle / peaked inverted-V / telescoping sleeve (Volumetric Envelope + Macro Surface). head: processing box / open finger-cage / flat saw-disc / clamshell-jaw / drum-in-hood (Volumetric Envelope + Macro Surface Construction). Registered in slot_choices (undercarriage, boom_type, head). |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | `record_only` + host-conformal: hydraulic hoses (`*_hose` spline tubes), warning `yellow_capacity_plate`+`capacity_black_mark_{i}` decals, cab work-lights/beacon/mirrors, grousers, guard rails, brush combs. Inline parent visuals (Rule 1), derived on the host face. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | boom_reach 0.88–1.15, stick_reach 0.88–1.15, carrier_len 0.90–1.12, carrier_width 0.92–1.10, head_size 0.90–1.12. Joint envelopes: lift [−0.42,0.55], elbow [−0.65,0.72], wrist [−0.95,0.95], slew ±0.60, telescopic [0,1.0]. motion_test_plan: sampled collision (`fail_if_parts_overlap_in_sampled_poses`, max_pose_samples=32 for the many-joint chain) + targeted `ctx.pose` per mechanism (boom raises head, elbow swings, telescopic extends, slew rotates, head fingers/grab/jaws close / drum spins / wrist swings). |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 palette_style: jd_green (green+yellow), komatsu_red (red+black), black_arm (blue-black), ponsse_yellow, tigercat_orange, industrial_grey. Material classes: painted (body/arm), metal (steel/chrome/aluminum), rubber (tires/tracks), glass (cab). ≥ ceil(0.5·6)=3 classes present each seed. |

**收尾自检**: batch 0-9 must visibly show all 3 undercarriages, 3 boom families, 5 heads, wheels-N vs rollers-N, and ≥4 palettes; heads read distinct; joints do not 穿模 across sampled poses.

## 9. 拓扑多样性审计

总组合数：undercarriage(3) × boom_type(3) × head(5) = **45** structural combos, × running-gear N (wheels {2..5}=4 + rollers {3..8}=6 + static 1 = 11 realized N-buckets) → sizeable slot-choice tuple space (≈45×~4 avg N ≈ 180+ distinct tuples).


seed_domain_policy：procedural_first.

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` seeds `random.Random(seed)` and draws undercarriage, boom_type, head each `rng.choice`, num_axles/rollers via weighted `rng.choices`, palette_style `rng.choice`, and the continuous scales `rng.uniform`. `resolve_config` validates enums, clamps scales, resolves conditional N (num_axles only meaningful for wheeled; rollers only for tracked), derives axle/roller pitch, tire_radius (clearance), and clamps joint ranges. Compatibility matrix: all 45 undercarriage×head combos are legal because every head shares the identical wrist interface (same part-tree/interface extrapolation) — turret slew is the only gated element (tracked only). No regression overrides in v1. Sweep seeds 0-35 initial + corner; 0-999 maturity if needed.

Topology target：1000-seed distinct ≥300 is the rich-category report-only guideline; current estimate is recorded here (≈180+ tuple space; source-anchored).

Controlled local parameterization：boom_reach_scale, stick_reach_scale, carrier_len_scale, carrier_width_scale, head_size_scale — all clamped in `resolve_config`; derived tire_radius/axle_pitch/roller_pitch enforce clearance; joint ranges fixed-conservative (independent) so scales cannot break the sampled-pose clearance or the captured-pin interfaces.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→C then N then palette then scales; weighted N | slot_choices_for_seed matches build choices |
| compatibility matrix | all A×C legal (shared wrist iface); slew gated to tracked; N gated to matching undercarriage; degrade N→ignored when undercarriage lacks that axis | no floating, no sampled-pose collision, boom clears carrier, head clears ground |
| controlled local variation | 5 continuous scales + derived clearance | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial, 0-999 maturity | contract failures; axis_realization report |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| undercarriage | 3 | yes | yes | |
| boom_type | 3 | yes | yes | |
| head | 5 | yes | yes | mulcher gated |
| running_gear (N) | 11 buckets | yes | yes | coverage only, N not counted |

## Validator

- slot_choices_for_seed returns implemented module names (undercarriage, boom_type, head, running_gear)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix / gating: slew tracked-only, N gated to matching undercarriage
- no regression overrides
- controlled local scales clamped; tire/axle/roller pitch derived so adjacent copies never overlap
- cross-part scale dependencies resolved in resolve_config
- captured-pin pivots (boom root/elbow/wrist/rotator/fingers/jaws/grab/drum/wheels) use element-scoped allow_overlap; grandfathered joints (no MatingContract) guarded by flat articulation-origin baseline
- key joints have expected type/axis/range (boom lift/elbow/wrist REVOLUTE-Y; slew REVOLUTE-Z; telescopic PRISMATIC-X; rotator/drum CONTINUOUS; fingers/grab/jaws REVOLUTE)
- copied objects follow naming (`wheel_{i}`, `side_{s}_roller_{i}`, `claw_finger_{i}`) and placement policy
- fail_if_parts_overlap_in_sampled_poses + targeted ctx.pose per mechanism

## Reject cases
- Boom/stick/head 穿模 into the carrier at drooped/slewed sampled poses (fix: narrow lift/elbow/slew ranges, not scales).
- Head dips below ground z=0 at full droop.
- Adjacent bogie tires or rollers overlapping (fix: derive pitch/tire_radius clearance).
- Wheel/turret/boom part isolated (no contact with parent) — captured-pin barrels must overlap their yokes.
- Downgrading tire/rim/finger meshes to Box/Cylinder placeholders (Rule 3 violation).
- Turret slew on wheeled/pedestal (slew is tracked-only) or wheels on a tracked/pedestal carrier.
- Mulcher head reading as a standalone machine (must keep the full carrier+boom+wrist chain above the drum).
- Finger/jaw/grab close angles causing un-declared self-overlap (declare grasp-contact allow_overlap between mating fingers/jaws).

## 与相邻类别的边界
- 不该混入：**forwarder / log-loader**（bunk-bed log carrier, no processing head — category risk; the articulated-frame forwarder undercarriage is gated OUT, not forked）。
- 不该混入：**excavator**（bucket end-effector, not a forestry head; identity is the processing/felling/grapple head）。
- 不该混入：**standalone mulcher / stump-grinder machine**（the mulcher head must remain a wrist-mounted attachment on the boom-ARM, not the whole machine — GATED）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Author-built modular template. Mulcher head gated (must read as arm+attachment). Slew narrowed ±0.60 vs source ±1.45 for sampled-pose clearance. |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P1 | A/B/C | pedestal_static / inverted_V / felling_grapple_4finger | rec_use-…_26d122a9 | L95-L290 | king-post base + inverted-V boom + 4-finger rotator grapple |
| P2 | A/B/C | wheeled_bogie / knuckle_2section / processing_head | rec_use-…_f77bf836 | L98-L464 | bogie wheels + cab + knuckle boom + processing head |
| P3 | A/B/C | tracked_crawler / knuckle_2section / processing_head | rec_use-…_e451456d | L60-L236 | tracks + turret slew + knuckle boom + processing head |
| V1 | B | telescopic_3section | rec_harvester_var_boom_telescopic | L164-L243 | outer sleeve + inner PRISMATIC |
| V2 | C | feller_saw | rec_harvester_var_head_feller_saw | L206-L265 | saw disc + 2 grab arms |
| V3 | C | log_grapple | rec_harvester_var_head_log_grapple | L417-L528 | rotator + 2 jaws |
| V4 | C | mulcher (gated) | rec_harvester_var_head_mulcher | L417-L545 | hood + drum + teeth |
| V5 | A | tracked rollers N | rec_harvester_var_track_rollers_6 | L69 | rollers 4→6/side |
| V6 | A | wheeled wheels N | rec_harvester_var_wheels_8 | L253-L345 | num_axles computed loop |
