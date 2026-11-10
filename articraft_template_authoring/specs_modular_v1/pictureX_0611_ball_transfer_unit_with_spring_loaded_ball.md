# Modular Spec — pictureX_0611_ball_transfer_unit_with_spring_loaded_ball

## 元信息

- slug: `pictureX_0611_ball_transfer_unit_with_spring_loaded_ball`
- category: 0611 / ball_transfer_unit_with_spring_loaded_ball
- template: `agent/templates/pictureX_0611_ball_transfer_unit_with_spring_loaded_ball.py`
- `__modular__ = True`
- stage: `IMPLEMENTED`
- status: `complete_visual_confirmed_2026-07-13`
- variant_gate: `confirmed_by_user_2026-07-12`
- source map: `articraft_data/picture_expansion/template_source_maps/0611__ball_transfer_unit_with_spring_loaded_ball.md`
- 5★ pool: 1 origin anchor + 11 normal forked variants + 1 compatibility probe-only record = 13 records (all rated 5, synced at `data/records/<id>/revisions/rev_000001/model.py`).
- compile budget: ≤ 20 s / seed (see §7.5).
- **underfilled_reason (inherited from source map):** mechanically simple part — one load ball, one housing, one spring stack. Real structural vocabulary is dominated by the mounting interface plus a few body-form / mechanism / orientation variants. This spec honors that vocabulary and does not pad toward the upper slot budget.

## 5 星样本阅读摘要

All 13 sources share one kinematic spine, differing only along the declared axes:

```
housing (root)
 ├─ retainer            FIXED     (pressed cup capturing the ball crown)
 ├─ compression_spring  FIXED     (hidden axial spring envelope; absent in rigid variant)
 └─ spring_carrier      PRISMATIC (spring preload, z travel 3mm)  |  FIXED (rigid seat)
     ├─ roll_frame      CONTINUOUS axis-x   (hidden orthogonal rolling core)
     │   └─ load_ball   CONTINUOUS axis-y   (the exposed load-bearing transfer ball)
     └─ support_ball_{i:02d}  FIXED × N     (radial nest in the lower race)
```

- **Origin anchor** `rec_picturex_0611__...__001` (`model.py`): the canonical stepped press-fit cylinder. `_housing_geometry` L25-49, `_retainer_geometry` L52-60, `_carrier_geometry` L63-87; housing part L127-143; retainer + `housing_to_retainer` FIXED L145-165; `compression_spring` + `housing_to_spring` FIXED L167-186; `spring_carrier` + `housing_to_carrier` PRISMATIC (axis (0,0,1), lower=-0.003, upper=0) L188-219; `roll_frame` Sphere(0.002) + `carrier_to_roll_frame` CONTINUOUS axis-x L224-242; `load_ball` Sphere(0.0125) + `roll_frame_to_ball` CONTINUOUS axis-y L244-266. Overall envelope 0.056×0.056×0.0655 m; ball dia 0.025 m; ball center z=0.053; flange top z=0.056.
- **Mount forks** (① skeleton, all keep the stepped cylinder body, change only the base/mount interface): `var_flange_bolt_mount` `_housing_geometry` L25-55 (broad base plate r=0.038×0.005 + 4 bolt holes on r=0.030 circle); `var_threaded_stud_mount` L25-60 (hex collar + stepped shank + 7 annular thread grooves below the floor); `var_side_bracket_mount` L18-47 (two symmetric lateral ears with bolt holes in ±x); `var_machined_square_base` L25-46 (76×76×8 mm square plate + 4 corner holes at 30 mm).
- **Body-form forks** (③ Primary Form Family): `var_hex_body` L25-45 (regular hex prisms, AF 44/50 mm, circular retainer seat — Volumetric Envelope Form); `var_shallow_wide_cup` housing L25-22 + solid-cup carrier L62-90 (low-profile r=0.024×0.015 cup + broad flange, ball center dropped to z=0.016, retainer z=0.020, spring z=0.003 — Macro Surface Construction).
- **Preload fork** (② mechanism): `var_rigid_nonspring_seat` carrier L62-87 (solid seat post replacing the plunger), `housing_to_carrier` FIXED L186-190, `compression_spring` part removed (run_tests asserts its absence L274-279).
- **Orientation fork** (① skeleton): `var_ball_down_orientation` inverts the whole stack, `housing_to_carrier` PRISMATIC axis (0,0,-1) L216-227, joints/origins mirrored L168-273.
- **Multiplicity forks** (N): `var_support_balls_n8/n12/n16` add a radial ring `support_ball_{i:02d}` (Sphere r≈0.0018 at pitch r=0.008) each FIXED to `spring_carrier`; n8 ring L268-300, ring checks L528-573.
- **Compatibility probe:** `var_probe_flangemount_balldown` (bolt flange at top × inverted ball-down) `_housing_geometry` L25-76, inverted stack L156-291, clearance checks L329-420.

## 核心身份

A housing/cup capturing ONE large load-bearing ball that rolls freely on a captive support race (two CONTINUOUS rolling joints, center held captive), spring-loaded (PRISMATIC preload) or rigidly seated, with a mounting interface to a machine/table. The exposed load ball + its real multi-axis rolling articulation + the closed retaining cup + the grounding mount are the four must-keep elements.

## 与相邻类别的边界

- 不该混入 **swivel / rigid caster**：有 fork / wheel / swivel yoke —— BTU 没有分叉臂或轮子，只有一颗滚珠。
- 不该混入 **plain ball / thrust bearing**：等径滚珠环无单颗突出承载球、无外壳 —— BTU 必须有一颗大突出 load ball。
- 不该混入 **trackball / 装饰球 / gravity ball drop**：无外壳、无支承 race、无 spring 预压 —— BTU 的 race + 预压是身份的一部分。
- 排除 **roller-based transfer**（圆柱滚子）漂向 conveyor roller；排除**一壳多大球**（非真实 BTU 形态）；排除**静态无滚动球顶**（违反 must_keep 滚动关节）。

## 槽位 + 候选模块表

### Slot A：mount （① 骨架 / 安装接口）— 5 candidates
| module | form/interface | source | model.py 来源 |
|---|---|---|---|
| `press_fit` | plain smooth cylindrical drop-in body, no external holes (parent) | origin_anchor | origin `_housing_geometry` L25-49 |
| `bolt_flange` | broad flat base plate + ring of N_bolt through holes | var_flange_bolt_mount | L25-55 |
| `threaded_stud` | hex collar + stepped threaded shank projecting below the floor | var_threaded_stud_mount | L25-60 |
| `side_bracket` | two symmetric lateral ears with bolt holes (wall/rail mount) | var_side_bracket_mount | L18-47 |
| `machined_square_base` | solid square base plate + 4 corner bolt holes | var_machined_square_base | L25-46 |

### Slot B：body_form （③ 主体形态家族 / Primary Form Family, 登记进 slot_choices）— 3 candidates
| module | form_subtype | source | model.py 来源 |
|---|---|---|---|
| `stepped_round_cylinder` | Volumetric Envelope Form — stepped round cylinder (parent) | origin_anchor | origin L25-49 |
| `hex_prism` | Volumetric Envelope Form — hex wrench-flats prism, circular retainer seat | var_hex_body | L25-45 |
| `shallow_wide_cup` | Macro Surface Construction — low-profile wide flanged cup | var_shallow_wide_cup | L25-22 + carrier L62-90 |

### Slot C：preload （② 关节类型）— 2 candidates
| module | joint | source | model.py 来源 |
|---|---|---|---|
| `spring_prismatic` | `housing_to_carrier` PRISMATIC axis-z, travel 3mm, + compression_spring part (parent) | origin_anchor | origin L188-219, spring L167-186 |
| `rigid_fixed_seat` | `housing_to_carrier` FIXED, no spring part | var_rigid_nonspring_seat | carrier L62-87, FIXED L186-190 |

### Slot D：orientation （① 骨架）— 2 candidates
| module | topology | source | model.py 来源 |
|---|---|---|---|
| `ball_up` | ball crown exposed at +z, mount below (parent) | origin_anchor | origin full stack |
| `ball_down` | whole stack rigidly inverted (rot180 about x): ball at -z, mount at top | var_ball_down_orientation | L156-273 (probe L156-291) |

### Slot E：support_ball_count（N multiplicity, §8）
N ∈ {8, 12, 16} source-backed; procedural range 6–20 single radial ring; see §8.

`palette_style` (⑥ 涂装, ≥3 target 4-6): 6 realistic steel colorways from the sources — `satin_steel`, `polished_steel`, `bearing_steel`, `dark_steel`, `zinc`, `stainless` (rgba lifted / extended from origin L114-125).

## 槽位图（slot graph）

```
Slot B body_form  ─┐
Slot A mount       ├─► housing (ONE cadquery part; body_form shapes upper envelope,
Slot D orientation ┘    mount adds base/stud/ears, orientation applies global rot180x)
                          │ FIXED   → retainer
                          │ FIXED   → compression_spring   (only if Slot C = spring_prismatic)
                          └ PRISMATIC|FIXED (Slot C) → spring_carrier
                                        │ CONTINUOUS-x → roll_frame
                                        │                └ CONTINUOUS-y → load_ball
                                        └ FIXED × N (Slot E) → support_ball_{i:02d}
```

Slots A/B/D all co-shape the single `housing` part (they share the housing envelope surface), so they are alternative *composable facets* of the housing rather than serial chain slots; C/E are downstream of the carrier. This is the honest decomposition for a one-housing part — separate serial slots would invent mating seams the sources do not have.

## 每槽位 Module Emits / Interfaces

- **housing** (A×B×D): emits part `housing` with visual `stepped_housing` (cadquery mesh, `body`-keyed material). Anchors every downstream FIXED/PRISMATIC joint. No InterfaceSpec chain (single-part hub).
- **retainer**: part `retainer`, visual `retaining_cup`; `housing_to_retainer` FIXED with MatingContract (retainer `negative_z` ↔ housing flange `positive_z`).
- **compression_spring** (C=spring only): part `compression_spring`, Cylinder visual `spring_envelope`; `housing_to_spring` FIXED.
- **spring_carrier** (C): part `spring_carrier`, cadquery visual `spring_plunger`; `housing_to_carrier` PRISMATIC (axis (0,0,zf), limits ±3mm) or FIXED. Captured plunger-in-bore ⇒ mating omitted (grandfathered, Rule 2), backed by run_tests contact.
- **roll_frame / load_ball**: Sphere visuals `bearing_core` / `load_ball`; `carrier_to_roll_frame` (axis-x) and `roll_frame_to_ball` (axis-y) CONTINUOUS. Concentric ball-in-socket ⇒ mating omitted (grandfathered, Rule 2), backed by run_tests `expect_within`/`expect_overlap` to the visible race + support balls.
- **support_ball_{i:02d}** (E): Sphere visuals; `carrier_to_support_{i:02d}` FIXED to carrier at pitch radius.

## 参数范围汇总

| param | range | 约束类型 | basis |
|---|---|---|---|
| `ball_radius` | 0.0110–0.0135 | independent | origin 0.0125 (dia 25mm); sr=ball_radius/0.0125 scales all radial geometry so the aperture lip stays ≤15mm from axis |
| `body_scale` | 0.88–1.20 | independent | body/shoulder girth only (not bore/flange) |
| `travel` (spring) | 0.0020–0.0040 sampled, then clamped | inequality | clamped to `min(ball_bottom, cup_bottom, support_bottom) − floor − 0.0006` so the moving stack never enters the floor web (binding on shallow cup) |
| `support_ball_count` N | 6–20 (int) | independent | ring multiplicity |
| `support_ball_radius` | derived | equation | = clamp(pitch·sin(π/N)·0.9, 0.0012, 0.0022) so a denser ring uses smaller balls (no self-overlap) |
| `pitch_radius` | derived | equation | = 0.62·bore_radius(body_form) |
| `ball_center_z` | derived | equation | per body_form (0.053 tall / 0.016 shallow), ×zf orientation |
| `retainer_z`, spring z, carrier origin | derived | equation | anchored to `ball_center_z` (Contract 3c single-source `_stack_heights`) |
| N_bolt (flange) | {3,4,6} | conditional | only when mount=bolt_flange (gated multiplicity) |

### 7.5 编译预算 / compile budget
≤ **20 s / seed**. 依据：origin housing cadquery mesh 实测 0.38 s；每 seed 3 个 cadquery mesh（housing/retainer/carrier）+ N≤20 个 Sphere 图元 ≈ 1.5–3 s。tolerance=0.00025 / angular=0.06 保持原 5★ 参数，不加密。sweep `--compile-timeout 120`（~4× 预算，watchdog）。

## Multiplicity / Copy Logic

- count_param: `support_ball_count` (N).
- N samples (source-backed): 8, 12, 16. Procedural range: **6–20**, single radial ring (below ~6 = unrealistic bed; above ~20 crowds one ring → would need a 2nd row = different topology, excluded).
- copied object: one small `Sphere(support_ball_radius)`; naming `support_ball_{i:02d}`.
- placement: single radial ring at `pitch_radius` in the lower race, `angle = 2π·i/N`, at the carrier lower-race z.
- joint policy: each support ball **FIXED to spring_carrier** (captive bed). The main `load_ball` keeps its two CONTINUOUS rolling joints as the real non-fixed articulation.
- N_bolt (flange bolt-hole count) is a **gated** second multiplicity — realized only when mount=bolt_flange; not a standalone N sample. slot_choices reports N_bolt only for that mount.

### 8.5 视觉多样性 6 轴考察

| 轴 | 有/无 | 取值/范围 + source_type |
|---|---|---|
| ① 骨架图 | 有 | mount {press_fit, bolt_flange, threaded_stud, side_bracket, machined_square_base} (①); orientation {ball_up, ball_down} (①). 均 forked_anchor/origin。 |
| └ multiplicity | 有 | support_ball_count N∈6–20 (源 8/12/16)；gated N_bolt∈{3,4,6}(flange)。见 §8。 |
| ② 关节类型 | 有 | preload {PRISMATIC spring (parent) ↔ FIXED rigid seat}; core 2× CONTINUOUS rolling kept in ALL seeds. forked_anchor。声明的 PRISMATIC 与 FIXED 都在 sweep 出现（slot_choices 覆盖）。 |
| ③ 主体形态家族 | 有 | body_form {stepped_round_cylinder=Volumetric Envelope, hex_prism=Volumetric Envelope, shallow_wide_cup=Macro Surface Construction}，登记进 slot_choices。source-backed anchors。 |
| ④ 表面装饰 | 无（host-conformal only） | 仅 polished/satin 钢带 + pressed retainer seam；无专用 fork（源 meta record_only）。不做常数半径贴花以免脱离宿主面。 |
| ⑤ 尺寸/行程 | 有 | body_scale 0.85–1.20, ball_radius 0.011–0.014；PRISMATIC travel [0, 0.0022–0.0038]（axis z, 方向 = 压缩，闭合=rest q0）。motion_test_plan: sampled collision (max 96) + targeted `ctx.pose({carrier:−travel or +travel})` 验证球冠压缩位移 + 两个 CONTINUOUS `ctx.pose` 验证球心 captive。continuous 整圈不穿模（球对称）。 |
| ⑥ 涂装 | 有 | metal 大类；6 配色 palette_style（satin/polished/bearing/dark steel + zinc + stainless），rng.choice per seed，覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：body_form 三原型在 batch 0-9 拉得开（高圆柱 / 六棱 / 矮宽杯）；6 钢配色都可能出现；无悬空装饰；prismatic 压缩全程不穿模。

## 采样与覆盖审计

总组合数：mount 5 × body_form 3 × preload 2 × orientation 2 × N(源3,程序15) = 5×3×2×2×15 = 900 (+ palette 6, + N_bolt gated)。honest 组合空间 ≥300，满足成熟度观察。

seed_domain_policy：procedural_first（seed=0 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次 rng.choice 每个 slot + rng.randint(6,20) N + rng.uniform 连续参数 + rng.choice palette_style。compatibility gating（§below）在 resolve_config 前应用。random sweep 0-35，viewer 目检 0-9。

| item | policy | validator/focus |
|---|---|---|
| sampler | slot order A→B→C→D→E, uniform rng.choice; N=randint(6,20); N_bolt=choice({3,4,6}) only if flange | slot_choices_for_seed == build choices |
| compatibility matrix | see below | no floating/collision/axis failures |
| controlled local variation | body_scale, ball_radius, travel, pitch (clamped/derived in resolve_config) | proportions vary w/o breaking clearance/joint origin |
| regression overrides | none | — |
| random sweep | 0-15 fast, 0-35 final, corner stage | axis_realization; viewer 0-9 |

**Compatibility matrix / gating (topology audit):**
- `bolt_flange` × `machined_square_base` 互斥概念 — 它们是同一 mount slot 的两个候选，天然互斥（单选），无需 gate。
- `bolt_flange`/`machined_square_base` base plate 与 `shallow_wide_cup` 自带宽 flange：兼容（cup 坐在 plate 上，body base offset = plate 厚），无 clash。
- `threaded_stud` × `ball_down`：stud 在 rot180 后指向上方 = 顶部螺柱穿板安装，合法（源 probe 同族思路）。
- **probe：`bolt_flange` × `ball_down`**（源 `var_probe_flangemount_balldown`）——顶部 bolt flange vs 倒置 retainer/ball crown 间隙。gating：ball_down 时 bolt 环半径 ≥ retainer 外径 + 2mm（派生检查），避免 bolt 环压到倒置 retainer。realized via slot_choices，corner stage 会命中。
- N_bolt 仅在 flange 生效（gated multiplicity），其余 mount 忽略。
- 无非法组合被静默丢弃；下方 Reject cases 是硬失败模式。

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| mount | 5 | yes | yes | |
| body_form | 3 | yes | yes | ③ Primary Form Family slot |
| preload | 2 | yes | no | 源仅 2 真实机制（spring/rigid）；degrade 理由：BTU 预压只有"弹簧预压"与"刚性座"两种真实形态，第三种会造类外结构 |
| orientation | 2 | yes | no | 源仅 ball_up/ball_down 两向；第三向无物理意义 |

## Validator

- `slot_choices_for_seed(seed)` 返回 implemented module 名（mount/body_form/preload/orientation/support_ball_count[/N_bolt]）。
- `config_from_seed` 全 seed（含 0）走 deterministic procedural sampling。
- resolve_config clamp 所有连续参数并派生 stack heights（单源 `_stack_heights`）、pitch、support_ball_radius；gating 非法组合。
- assert：load_ball 有 2 条 CONTINUOUS 关节且球心 captive；support ball 环数 == N；preload=spring ⇒ compression_spring 存在且 housing_to_carrier PRISMATIC；preload=rigid ⇒ 无 spring 且 FIXED。
- key joints type/axis：housing_to_carrier ∈ {PRISMATIC,FIXED}；carrier_to_roll_frame CONTINUOUS axis-x；roll_frame_to_ball CONTINUOUS axis-y。
- copied support balls 命名 `support_ball_{i:02d}`、FIXED to carrier、pitch 环放置。
- MatingContract：retainer↔housing FIXED 有 contract；captured/concentric 关节按 Rule 2 grandfather 省略 mating，run_tests 用 contact 断言补足。

## Reject cases

1. load_ball 退化成非滚动固定球（缺 CONTINUOUS 关节）→ 违反 must_keep。
2. body_form 用 Box 拼壳而非 cadquery 旋转/棱柱包络 → 违反 Rule 3（降级图元）。
3. 球用 Box/多面体而非 Sphere/Lathe → 违反任务硬约束。
4. support ring 数与 N 不符，或命名不是 `support_ball_{i:02d}`。
5. rigid 变体仍生成 compression_spring，或 spring 变体 housing_to_carrier 非 PRISMATIC。
6. ball_down 只改 slot_choices 不真正倒置几何（球仍在 +z）→ 假实现。
7. 连续 travel / palette 撑多样性而 body_form 只有一种 → ③ 未达标。
8. prismatic 压缩位姿穿模（ball 穿过 retainer 或 carrier 穿 housing 底）。

## 模板实现备注

- 三个 A/B/D facet 共同构造单一 `housing` cadquery 实体：`_housing_solid(r)` 分支 body_form 造上体、mount 造底座/螺柱/耳、统一切 chamber + 孔；orientation=ball_down 时对 housing/retainer/carrier 三个实体 `.rotate((0,0,0),(1,0,0),180)`，并对所有 joint origin/visual origin 施加 R(x,y,z)=(x,−y,−z)、prismatic 轴 (0,0,1)→(0,0,−1)、continuous y 轴 (0,1,0)→(0,−1,0)——整体刚性旋转，等价重表达同一运动树，所有 clearance/mating 不变。
- captured-pin overlap 需 element-scoped allow_overlap：load_ball↔carrier（座在凹 race）、roll_frame↔load_ball（隐藏核）、support_ball_i↔carrier（座在 race）、spring↔housing/carrier（compliant 代理）。
- 单源共享 `_stack_heights(r)`（ball_center_z / retainer_z / spring_z / carrier_origin_z / chamber）避免散写。
- Contract 3d：预压是简单 axial prismatic，无合适 idiom（hinged/sliding_member 针对面板/抽屉），保留 raw `model.articulation`，已注释。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | complete; visual confirmed by user 2026-07-13 |
| reviewer notes | 每候选带 real model.py:Lx-Ly；single-candidate 无（最小 slot=2，含 documented degrade 理由）；topology audit + probe 已列；compile budget ≤20s。Post-gate sweep final pass_rate=1.0 and corner stage clean. Preview seeds `1,5,2,4,7,12,79,14,19,20` generated workbench-only records; user confirmed visual check on 2026-07-13. |

## Module Source Index
| source_id | slot | module | record | model.py |
|---|---|---|---|---|
| S1 | body_form/mount/preload/orient | stepped_round_cylinder / press_fit / spring_prismatic / ball_up | origin `__001` | L25-266 |
| S2 | mount | bolt_flange | var_flange_bolt_mount | L25-55 |
| S3 | mount | threaded_stud | var_threaded_stud_mount | L25-60 |
| S4 | mount | side_bracket | var_side_bracket_mount | L18-47 |
| S5 | mount | machined_square_base | var_machined_square_base | L25-46 |
| S6 | body_form | hex_prism | var_hex_body | L25-45 |
| S7 | body_form | shallow_wide_cup | var_shallow_wide_cup | L25-22, L62-90 |
| S8 | preload | rigid_fixed_seat | var_rigid_nonspring_seat | L62-87, L186-190 |
| S9 | orientation | ball_down | var_ball_down_orientation | L156-273 |
| S10 | multiplicity | N=8/12/16 | var_support_balls_n8/n12/n16 | L268-300 |
| S11 | probe | bolt_flange×ball_down | var_probe_flangemount_balldown | L25-291 |
