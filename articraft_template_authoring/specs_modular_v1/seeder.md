# seeder — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `seeder` |
| template path | `agent/templates/seeder.py` |
| test path (optional) | `tests/agent/test_seeder_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel-children moving parts + row multiplicity of inline visuals) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 17 (3 picture anchors + 14 slot-fork variants) |
| read_count | 17 (3 anchors read in full; 14 forks read for the module-local part they contribute) |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

Anchors (all three share ONE skeleton): a single root `frame`/`chassis` part that
inlines every non-moving element (side rails, cross members, transverse axle(s),
tapered open hopper mesh, seed throat + chute tubes, metering housing/cheeks,
furrow opener + soil tools, twin bent push-handle tubes + grips, depth pivot boss),
plus exactly four moving child parts on `+Y` axes: **two ground wheels**
(`CONTINUOUS`), **one metering rotor** (`CONTINUOUS`), **one depth lever**
(`REVOLUTE`). All 14 forks preserve this 5-part / 4-joint topology exactly
(confirmed: every fork has 4 articulations and {chassis, wheel×2, meter, lever}),
so the category's diversity is **not** skeletal — it lives in ③ form families of
the rotor / opener / running-gear, in ④ drive-detail decoration, and in the
`row_count` multiplicity of the inline hopper→chute→opener lane.

## 核心身份

A walk-behind (hand-pushed) seed planter / row seeder: a wheeled ground-driven
frame carrying a seed hopper, an exposed metering rotor that doles seed as the
ground wheels turn, a seed chute, and a soil-engaging furrow opener, steered by
tall push handles with a depth-adjust lever. Mature domain = single- to few-row
push planters. It is NOT a broadcast fertilizer spreader (no spinning disc fan,
seed is placed in a furrow not flung), NOT a garden cart (has metering + opener +
seed path, not just a tub on wheels), and NOT a tractor-drawn drill.

## 槽位 + 候选模块表

### Slot A：meter_form  (③ Primary Form Family — the metering rotor; CONTINUOUS child, axis +Y)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype / 结构特征 |
|---|---|---|---|---|---|
| vane_paddle | forked_anchor | rec_picturex_0611__seeder__002 | L427-L453 | eligible if compatible | Volumetric Envelope Form — core cylinder + 8 radial box paddles |
| finger_paddle | forked_anchor | rec_picturex_0611__seeder__001 | L354-L374 | eligible if compatible | Volumetric Envelope Form — hub + 6 spoke fingers + paddle tips |
| pocket_plate | forked_anchor | rec_picturex_0611__seeder__003 | L384-L409 | eligible if compatible | Planar Boundary Form — flat seed-plate disc + hub + sphere seed pockets + drive lug |
| fluted_roller | forked_anchor | rec_0611_seeder_var_metering_fluted_roller | L~40-L62 (`_fluted_roller_mesh`) | eligible if compatible | Macro Surface Construction — transverse roller with 10 rounded full-length flutes |
| perforated_plate | forked_anchor | rec_0611_seeder_var_metering_perforated_seed_plate | meter_wheel part | eligible if compatible | Planar Boundary Form — cast plate with a ring of drilled seed holes |

### Slot B：opener_form  (③ Primary Form Family — soil-engaging tool; inline visuals on chassis, per row, no joint — Rule 1)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype / 结构特征 |
|---|---|---|---|---|---|
| hoe_shank | forked_anchor | rec_picturex_0611__seeder__002 | L360-L396 | eligible if compatible | Volumetric Envelope Form — box shank + pointed furrow blade mesh + covering shoe |
| forged_shoe | forked_anchor | rec_picturex_0611__seeder__003 | L338-L357 (`_furrow_opener` L70-88, `_soil_blade` L91-108) | eligible if compatible | Volumetric Envelope Form — forged pointed opener + trailing soil knife + welded bridge |
| runner_shoe | forked_anchor | rec_0611_seeder_var_opener_form_runner_shoe | `_closing_shoe` / `_runner_toe` | eligible if compatible | Volumetric Envelope Form — long low runner boot carrying the seed outlet |
| double_disc | forked_anchor | rec_0611_seeder_var_opener_form_double_disc_opener | `_furrow_opener` (paired toe-in discs + axle + hanger straps) | eligible if compatible | Planar Boundary Form — two dished toe-in discs on a common hanger |

### Slot C：wheel_layout  (①/③ running gear — two CONTINUOUS ground wheels, axis +Y; degrade to 2, reason below)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| tandem | forked_anchor | rec_picturex_0611__seeder__001 / __002 | 001 L338-L352,L399-L416 / 002 L421-L425,L491-L508 | eligible if compatible | fore & rear wheels on the frame centerline, one axle each |
| side_by_side | forked_anchor | rec_picturex_0611__seeder__003 | L379-L382,L438-L455 | eligible if compatible | twin coaxial wheels straddling one front axle |

Degrade reason (Slot C = 2): the entire 5-star pool realizes exactly these two
ground-wheel arrangements; a third layout would be fabricated skeleton with no
`forked_anchor`, which Rule 3 forbids. Both are structurally distinct (axle count
and wheel-position topology differ) so ≥2 holds.

### Multiplicity：row_count  (inline hopper→chute→opener lane ×N — no joints, Rule 1)

Covered in §8. N∈{1,2,3,4,6}; source anchors N=1 (001/002/003), forks N=1/2/4/6.

### ④ decoration：drive_detail  (host-conformal drive dressing near the wheel→meter path)

| module_name | source_type | source evidence | 结构特征 |
|---|---|---|---|
| chain_guard | record_only | rec_0611_seeder_var_drive_ground_wheel_chain_drive (`meter_drive_guard`, `drive_pin`) | thin curved guard tube from axle region to meter housing |
| belt_cover | record_only + world_knowledge_extrapolation | rec_0611_seeder_var_drive_belt_driven_meter | flat cover plate hugging the meter housing side |
| direct_pin | record_only | rec_0611_seeder_var_drive_direct_axle_meter_drive | short exposed drive pin/boss at the meter shaft |

Decoration only: emitted as chassis `.visual(...)` welded onto the meter housing;
never a part, never a joint, never a new seed function.

## 槽位图（slot graph）

pattern: mixed

```
                         chassis (root: rails + crossmembers + axle(s) + handles
                                  + meter housing + depth pivot boss)
                         |            |            |                |
      [CONTINUOUS +Y]    |            | [CONT +Y]  | [CONT +Y]      | [REVOLUTE +Y]
      wheel_a ----(axle capture)      | meter_rotor (shaft capture) | depth_lever (pivot capture)
      wheel_b ----(axle capture)      |            (Slot A form)     |
                                      |
     inline on chassis (no joint): row_count × { mast → hopper mesh → throat → chute → opener(Slot B form) }
     inline on chassis (no joint): drive_detail decoration welded on meter housing
```

- All four joints parent directly to `chassis`; every joint origin sits on a real
  transverse shaft/axle/pivot cylinder that is captured through the child hub
  (pin-through-hub → `mating` omitted, grandfathered; element-scoped
  `allow_overlap` + `expect_overlap` mirror each anchor's `run_tests`).
- `wheel_layout` sets the axle count and wheel positions; `meter_form` sets the
  rotor geometry captured on the central `meter_shaft`; `opener_form` sets the
  per-row soil tool inlined on the chassis; `row_count` replicates the
  hopper→chute→opener lane laterally in Y.
- No cross-slot mating faces (parallel-children + inline): the chassis owns the
  single supported root; wheels/rotor/lever hang off it.

## 每槽位 Module Emits / Interfaces

### chassis (root, always emitted)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (root) | 001 L125 / 002 L166 / 003 L171 |
| visuals | side rails, cross members, transverse axle(s), meter housing + cheeks, depth pivot boss, twin push-handle tubes + grips + tie, per-row hopper/throat/chute/opener, drive_detail | 002 L176-L413 / 001 L125-L336 |
| child joints | `wheel_a_spin`,`wheel_b_spin` (CONT +Y), `meter_spin` (CONT +Y), `depth_adjust` (REV +Y) | 002 L491-L531 |

### Slot A / meter_rotor (CONTINUOUS +Y child)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `meter_rotor` | 002 L427 |
| visuals | hub + form-specific rotor geometry (paddles / fingers / plate+pockets / fluted roller / perforated plate) | per module table |
| joint | `meter_spin` CONTINUOUS axis (0,1,0), effort~3 vel~10 | 002 L509-L517 |
| capture | rotor hub captured on chassis `meter_shaft` (allow_overlap + expect_overlap) | 002 L706-L730 |

### Slot B / opener (inline on chassis per row — Rule 1, no joint)
| emits | 描述 | 来源 |
|---|---|---|
| visuals | shank/boot/disc + blade/shoe geometry, welded to the lane chute + a support bridge | 002 L360-L396 / 003 L338-L357 |

### Slot C / wheel_layout (two CONTINUOUS +Y children + chassis axle visuals)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_a`,`wheel_b` (WheelGeometry+TireGeometry mesh, drive_pin detail) | 003 L111-L150 |
| visuals(chassis) | 1 axle (side_by_side) or 2 axles (tandem) transverse cylinders | 002 L195-L213 |
| joints | `wheel_a_spin`,`wheel_b_spin` CONTINUOUS axis (0,1,0) | 002 L491-L508 |

### depth_lever (REVOLUTE +Y child, always emitted)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `depth_lever` (sleeve + bent arm tube + grip) | 002 L455-L489 |
| joint | `depth_adjust` REVOLUTE axis (0,1,0), lower/upper ≈ [-0.32,+0.40] | 002 L518-L531 |
| capture | lever sleeve on chassis `depth_pivot` (allow_overlap + expect_overlap) | 002 L731-L755 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| meter_form | enum | vane_paddle/finger_paddle/pocket_plate/fluted_roller/perforated_plate | — | choice | procedural sampler | Slot A |
| opener_form | enum | hoe_shank/forged_shoe/runner_shoe/double_disc | — | choice | procedural sampler | Slot B |
| wheel_layout | enum | tandem/side_by_side | — | choice | procedural sampler | Slot C |
| row_count | int | {1,2,3,4,6} | 1 | choice | weighted (small-N heavy); clamp [1,6] | §8 |
| drive_detail | enum | chain_guard/belt_cover/direct_pin | — | choice | procedural sampler | ④ |
| palette_style | enum | 5 colorways | classic_blue_green | choice | procedural sampler | §8.5 ⑥ |
| wheel_radius_scale | float | [0.85,1.25] | 1.0 | independent | uniform then clamp | 001 r0.36 / 002 r0.18 / 003 r0.25 |
| hopper_scale | float | [0.88,1.15] | 1.0 | independent | uniform then clamp | 002 L53-71 |
| handle_height_scale | float | [0.88,1.18] | 1.0 | independent | uniform then clamp | 001 L221-255 |
| meter_radius_scale | float | [0.88,1.15] | 1.0 | independent | uniform then clamp | 002 L427-453 |
| depth_travel_scale | float | [0.85,1.15] | 1.0 | independent | uniform then clamp | 002 L525-530 |
| row_spacing | float | derived | — | equation | `= max(2*hopper_half_w+0.04, 0.16*hopper_scale)` | 2_row fork L294-296 |
| (—) | constraint | — | — | inequality | wheel disc X-band must clear working zone: `wheel_center_x - wheel_r ≥ working_x_max + 0.05`; if violated push wheel_center_x outward | clearance |
| (—) | constraint | — | — | inequality | side rails inboard of wheels: `rail_y + rail_hw + 0.005 ≤ side_wheel_y - wheel_hw` (side_by_side) | clearance |

## 7.5 编译预算 / compile budget
Self-reported budget: **≤18 s / seed** (typical ≈8-12 s). Meshes per seed:
2× WheelGeometry (one shared geometry, instanced), 1× lofted hopper (shared,
instanced across rows), 1× opener cadquery solid (shared, instanced across rows),
1× meter rotor (primitives for vane/finger/pocket; one cadquery solid for
fluted/perforated). Tessellation: hopper/opener tolerance ≈0.0008-0.001,
fluted roller flutes reuse one solid; N-row lanes reuse the SAME hopper/opener
mesh geometry objects (no re-tessellation per row). ≤32 pose samples in Rule-5
collision (4 joints). Timeout hang-guard 120 s (≈7× budget).

## Multiplicity / Copy Logic

- **Axis: row_count**
  - `count_param`: `row_count`
  - `N_range`: product domain [1,6]; test domain {1,2,3,4,6}. Weighted sampling:
    N=1 heavy, N=2 common, N∈{3,4} occasional, N=6 rare (small-N-heavy per §8).
  - copied object: one seeding lane = {mast, hopper mesh, seed throat, meter/feed
    housing stub, seed chute, opener(form) visuals} inlined as chassis `.visual`.
  - naming: `f"{elem}_{i}"` for lane i; placement: regular, centered on Y,
    `row_y = (i - (N-1)/2) * row_spacing`.
  - joint policy: **none** — lanes are non-moving (Rule 1). Only the single central
    metering rotor, two wheels, and lever articulate regardless of N (matches all
    forks: 4 joints for every row_count).
  - source/gating: 2_row fork L283-396 (transverse toolbar + shared lane recipe);
    N clamps to [1,6]; row span limited so outer lanes clear the wheels
    (side_by_side: lanes trail behind the front axle in X so Y overlap is safe).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 说明 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part | 无（单一骨架） | 全部 17 样本 = 5 part / 4 joint 同一运动学图（chassis + wheel×2 + meter + lever）；无 source 支持增删活动件。 |
| └ multiplicity | 同构件 ×N | 有 | `row_count` N∈{1,2,3,4,6}，权重小-N-heavy；见 §8。inline visuals，不加 joint。 |
| ② 关节类型 | 换 type/轴 | 无（source-backed 单一） | 3× CONTINUOUS(+Y) 轮/转子 + 1× REVOLUTE(+Y) 深度杆，全部 17 样本一致；无 source 支持换关节类型。sweep 中每种声明类型都出现（3 continuous + 1 revolute）。 |
| ③ 主体形态家族 | 换核心 part 可识别形态 | 有（3 根 ③ slot） | **meter_form**(5: vane/finger/pocket/fluted/perforated), **opener_form**(4: hoe_shank/forged_shoe/runner_shoe/double_disc), **wheel_layout**(2: tandem/side_by_side)。每个 candidate 标 form_subtype（见 Slot 表），均 forked_anchor。登记进 `slot_choices`。 |
| ④ 表面装饰 | 叠加表面细节 | 有 | `drive_detail`∈{chain_guard,belt_cover,direct_pin}，host-conformal 焊在 meter housing 上；record_only/world_knowledge_extrapolation。派生顺序 ③→⑤→④（贴合最终 housing 面）。 |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | wheel_radius_scale[0.85,1.25]、hopper_scale[0.88,1.15]、handle_height_scale[0.88,1.18]、meter_radius_scale、depth_travel_scale（见 §7）。运动包络：轮/转子 continuous 整圈不穿模（径向对称/桨叶在开放腔内）；depth_adjust REVOLUTE 轴 +Y 开启方向 up-back，[闭合0 → 可行 ±(0.32~0.40)]。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(32, ignore_fixed=True)` + 每机构 targeted `ctx.pose`（wheel drive_pin 位移 / meter feature 位移 / lever grip 扫弧）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted-steel / galvanized / rubber / dark-tool-steel；配色 5：classic_blue_green(001)、safety_orange(002)、farm_green_yellow(003)、oxide_red、teal_industrial。材质大类覆盖 ≥ ceil(0.5×?)。 |

## 采样与覆盖审计

总组合数：meter(5) × opener(4) × wheel_layout(2) × row_count(5) × drive_detail(3)
= 600 discrete slot tuples (× 5 palettes × continuous scales). ≥300 topology target met.

seed_domain_policy：procedural_first。`config_from_seed(seed)` uses `random.Random(seed)`
to pick each enum (uniform), row_count (weighted small-N), palette, and each
continuous scale (uniform in range). `resolve_config` clamps every scale, derives
`row_spacing`, and projects the two clearance inequalities (push wheels outboard /
inboard rails). No compatibility pair is illegal (all forms mount on the generic
central shaft / lane chute), so no gating needed beyond clamps; no regression
overrides. seed=0 is ordinary.

Topology target：600 slot tuples > 300 — sufficient for maturity audit.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | uniform enums + weighted row_count + uniform scales | slot_choices_for_seed matches build choices |
| compatibility matrix | all combinations legal; only geometric clamps | no floating lane, no wheel↔lane collision, rotor in open cradle |
| controlled local variation | 5 clamped scales + derived row_spacing | proportions vary without breaking capture joints or clearance |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial, corner stage; 0-999 maturity | contract failures; axis_realization; palette variety |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| meter_form | 5 | yes | yes | primary ③ |
| opener_form | 4 | yes | yes | ③ |
| wheel_layout | 2 | yes | no | degrade-justified (source pool = 2 arrangements) |
| drive_detail | 3 | yes | yes | ④ decoration |

## Validator

- slot_choices_for_seed returns implemented module names for every slot
- config_from_seed uses deterministic procedural sampling for all seeds incl. 0
- clamps keep scales in range; row_spacing derived; clearance inequalities resolved in resolve_config
- exactly 5 parts / 4 joints for every config (chassis + wheel×2 + meter + lever)
- meter joints CONTINUOUS +Y; depth_adjust REVOLUTE +Y with bounded travel
- captured-pin allow_overlap present for each wheel hub / rotor hub / lever sleeve
- N row lanes inlined as chassis visuals, none floating (each lane welded to a crossmember mast)
- palette drives every visual material

## Reject cases

- Wheel disc overlaps a seeding lane / opener (working zone not cleared in X).
- A row lane hopper/opener floats (not welded to a crossmember/mast) → island FAIL.
- Metering rotor paddles poke through the chassis frame mid-rotation.
- Depth lever arc collides with a wheel or handle.
- Downgrading the hopper loft / opener cadquery / WheelGeometry to a Box/Cylinder.
- drive_detail modeled as a separate part or joint instead of a chassis visual.
- Adding/removing a moving part (breaks the source-backed single skeleton).

## 与相邻类别的边界

- 不该混入：broadcast fertilizer spreader（离心撒播盘、无 furrow opener/seed 计量转子、种子被抛撒而非条播）。
- 不该混入：garden cart / wheelbarrow（只有 tub+轮，无 metering rotor / opener / seed path）。
- 不该混入：tractor-drawn seed drill（无 push handle、非 walk-behind、多为挂接式）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 3 picture anchors + 14 slot forks; single skeleton, ③-dominated diversity (meter/opener/wheel forms) + row multiplicity + drive decoration. |

## 模板实现备注（可选）
- 共享 helper：一个 WheelGeometry mesh 实例复用于两轮；一个 hopper loft solid + 一个 opener solid 复用于全部 N lane（不逐行重新 tessellate），守 §7.5。
- captured-pin：wheel hub↔axle、meter hub↔meter_shaft、lever sleeve↔depth_pivot 用 element-scoped allow_overlap（省 MatingContract，grandfathered）。
- 排除候选：`punch_wheel` opener（复杂 dibber 星形轮，暂不实现，opener slot 仍有 4 candidate ≥3）；`brush_meter` / `cup_feed` meter（需专用 housing mesh，超预算，meter slot 仍有 5 candidate）。若 reviewer 要求可后补。
</content>
</invoke>
