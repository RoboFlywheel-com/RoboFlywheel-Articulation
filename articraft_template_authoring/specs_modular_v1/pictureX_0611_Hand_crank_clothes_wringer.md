# pictureX_0611_Hand_crank_clothes_wringer

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Hand_crank_clothes_wringer` |
| template path | `agent/templates/pictureX_0611_Hand_crank_clothes_wringer.py` |
| stage | `TEMPLATE_SWEEP_PASS` |
| status | `sweep-pipeline pass, pass_rate=1.00` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in source map `0611__Hand-crank_clothes_wringer.md`, including 20260714 supplement anchors |
| source_index_policy | only adopted module sources are indexed below |

Source map: `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Hand-crank_clothes_wringer.md`.

## 核心身份

手摇衣物压水 wringer：核心是成对或三根并列橡胶压辊、侧向支架/轴承座、手摇曲柄传动、上压力调节桥，以及台夹/落地/墙架等真实安装方式。不得漂移成 pasta maker、laminator、洗衣机、晾衣架或泛用齿轮箱；滚轮必须保持压水 nip，曲柄必须驱动滚轮旋转，压力结构必须读作调节上辊压紧力。

## 槽位 + 候选模块表

### Slot A：`support_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `origin_bench` | origin_anchor | S1 | L83-L149, L274-L394 | eligible if compatible | 紧凑 bench/upright 框，底梁+顶梁+双侧立柱，2 个台夹螺杆；Primary Form = compact bench frame |
| `table_clamp` | forked_anchor | S2 | L83-L162, L286-L430 | eligible if compatible | 下横梁改成强夹座、gusset、bushing、T-handle clamp，仍承载同一 wringer head |
| `freestanding_floor` | forked_anchor | S3 | L90-L143, L340-L423 | eligible if compatible | 额外 `floor_stand` root + FIXED wringer head，四脚底座、长腿、横撑；Primary Form = freestanding floor frame |
| `wall_bench_bracket` | forked_anchor | S4 | L179-L219, L358-L424 | eligible if compatible | 后置 wall/bench bracket plate、bolt、gusset；不采台夹；Primary Form = wall/bench mounted bracket |

### Slot B：`pressure_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_screw_bridge` | forked_anchor | S1, S5 | S1 L251-L365; S5 L284-L433 | eligible if compatible | 中央 pressure screw / handle / hub + 两侧 prismatic pressure blocks，`pressure_slide_1` mimic `pressure_slide_0` |
| `spring_loaded_bridge` | forked_anchor | S6 | L154-L241, L357-L433 | eligible if compatible | 双 guide posts、spring anchors、可见 compression springs、spring bridge；无手动 pressure screw turn |
| `dual_handwheel_pressure` | forked_anchor | S10 | L253-L329, L415-L442 | eligible if compatible | tie bar + 双 side pressure posts + 两个 continuous handwheel adjusters，handwheel mimic pressure screw |

### Slot C：`drive_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_bent_crank` | origin_anchor | S1 | L205-L249, L325-L356 | eligible if compatible | 单 crank_drive part，bent tube crank + grip，continuous `crank_rotation` 驱动上辊和下辊 mimic |
| `exposed_twin_gear` | forked_anchor | S7 | L35-L70, L195-L230, L352-L380 | eligible if compatible | 上/下滚轮外侧 spur gears + drive hub/齿，齿轮视觉 attached to roller/crank host |
| `folding_crank_handle` | forked_anchor | S11 | L205-L283, L359-L382 | eligible if compatible | crank_drive stub + hinge ear/pin + 独立 `crank_handle`，`crank_fold` REVOLUTE 可把手柄向侧框收合 |

### Slot D：`feed_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_front` | origin_anchor | S1 | L83-L149 | eligible if compatible | 无前托板，衣物直接送入双/三辊 nip；front apron / lower beam 保持开放 |
| `fold_down_feed_shelf` | forked_anchor | S9 | L151-L167, L314-L454 | eligible if compatible | 前缘 frame hinge knuckles + 独立 `feed_shelf` part，`shelf_hinge` REVOLUTE，面板/hinge barrels/stops |

### Slot E：`roller_count`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `2` | origin_anchor | S1-S7, S9-S11 | S1 L165-L203, L334-L356 | eligible if compatible | 上/下两根橡胶辊；上辊随 pressure blocks，低辊固定在 frame bearing |
| `3` | forked_anchor | S8 | L20-L26, L71-L98, L230-L416 | eligible if compatible | `NUM_ROLLERS=3`，loop 发射 roller_0..2，顶梁抬高，顶辊随 pressure blocks，中/下辊固定 |

### Slot F：`palette_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `turquoise_white` | record_only + source palette | S1-S11 | material blocks e.g. S1 L76-L81 | eligible | turquoise painted metal + pale rubber + black polymer + bright steel |
| `red_black` | record_only + ⑥ extrapolation | S1-S11 + common real product finish | n/a | eligible | red painted frame + black rubber/knobs + zinc hardware |
| `zinc_black` | record_only + ⑥ extrapolation | S1-S11 + common real product finish | n/a | eligible | galvanized/zinc frame + black rollers/hardware shadow |
| `cream_green` | record_only + ⑥ extrapolation | S1-S11 + vintage laundry wringer finishes | n/a | eligible | cream/pale green frame + aged off-white rollers |
| `bare_steel` | record_only + ⑥ extrapolation | S1-S11 + common utility finish | n/a | eligible | bare steel frame + pale rollers + dark grip accents |

## 槽位图（slot graph）

pattern: mixed / parallel children around a shared wringer head.

`support_style` emits the grounded support and `frame`. `pressure_style` attaches `pressure_block_0/1` and pressure adjusters to `frame`; `roller_count` emits roller parts, with the top roller parented to pressure block(s) and fixed lower rollers parented to `frame`. `drive_style` attaches crank drive to the right pressure block / top roller axle. `feed_style` optionally emits a front shelf child of `frame`.

- `frame` --[`pressure_slide_0/1` PRISMATIC, axis +Z, [0, pressure_travel]]--> `pressure_block_0/1`.
- `pressure_block_1` --[`crank_rotation` CONTINUOUS, axis +X]--> `crank_drive`; if folding, `crank_drive` --[`crank_fold` REVOLUTE, axis +Y, [0, pi/2]]--> `crank_handle`.
- Fixed rollers: `frame` --[`roller_spin_i` CONTINUOUS, axis +X, mimic crank_rotation]--> `roller_i`; top roller: `pressure_block_0` --[`roller_spin_top` CONTINUOUS, axis +X, mimic crank_rotation]--> `roller_top`.
- Single/dual pressure: `frame` --[`pressure_screw_turn` CONTINUOUS, axis +Z]--> `pressure_screw`; dual handwheels add `pressure_screw` --[`handwheel_i_turn` CONTINUOUS, axis +Z, mimic pressure_screw_turn]--> `handwheel_i`.
- Feed shelf: `frame` --[`shelf_hinge` REVOLUTE, axis +X, [0, pi/2]]--> `feed_shelf`.

## 每槽位 Module Emits / Interfaces

### Slot A / `support_style`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`; for freestanding also `floor_stand` | S1 L83-L149; S3 L90-L143 |
| internal joints | freestanding: `stand_to_frame` FIXED with visible legs contacting the head | S3 L342-L349 |
| upstream interface | world/grounded support; no upstream slot | source map support skeleton |
| downstream interface | frame bearings, top beam, lower clamp/bracket faces consumed by pressure/roller/feed slots | S1 L117-L149; S4 L179-L219 |

### Slot B / `pressure_style`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pressure_block_0/1`; `pressure_screw` or spring visuals or `handwheel_0/1` | S5 L184-L325; S6 L204-L241; S10 L253-L329 |
| internal joints | `pressure_slide_0/1` prismatic +Z; optional `pressure_screw_turn`; optional handwheel continuous joints | S5 L362-L447; S10 L415-L442 |
| upstream interface | frame top beam / guide posts; captured stem/post passes through beam | S5 L424-L432; S10 L415-L442 |
| downstream interface | upper roller axle journals through both pressure blocks | S1 L334-L343 |

### Slot C / `drive_style`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank_drive`; optional `crank_handle` | S1 L205-L249; S11 L205-L283 |
| internal joints | `crank_rotation` continuous; optional `crank_fold` revolute | S1 L325-L333; S11 L359-L382 |
| upstream interface | keyed to top roller/right pressure block axle | S7 L694-L708 |
| downstream interface | crank handle/grip visible and reachable; drive mimics roller spins | S7 L739-L748 |

### Slot D / `feed_style`
| emits | 描述 | 来源 |
|---|---|---|
| parts | none for `open_front`; `feed_shelf` for fold-down shelf | S9 L314-L340 |
| internal joints | `shelf_hinge` REVOLUTE +X, [0, pi/2] | S9 L441-L454 |
| upstream interface | front apron / hinge knuckles on `frame` | S9 L151-L167 |
| downstream interface | no downstream slot; shelf panel supports laundry feed before rollers | S9 L745-L766 |

### Slot E / `roller_count`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_0..N-1` with axle + rubber cylinder + optional gear visuals | S8 L71-L98, L230-L235 |
| internal joints | `roller_spin_i` continuous +X; lower/middle frame-parented, top pressure-block-parented | S8 L375-L416 |
| upstream interface | frame bearing blocks / pressure blocks | S8 L176-L184, L333-L405 |
| downstream interface | crank drive attaches to top roller axle; pressure slot moves top roller carriage | S8 L364-L416 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support_style` | enum | origin_bench / table_clamp / freestanding_floor / wall_bench_bracket | origin_bench | choice | sampled, then compatibility gates applied | Slot A |
| `pressure_style` | enum | single_screw_bridge / spring_loaded_bridge / dual_handwheel_pressure | single_screw_bridge | choice | spring gated out with 3 rollers and folding crank | Slot B |
| `drive_style` | enum | plain_bent_crank / exposed_twin_gear / folding_crank_handle | plain_bent_crank | choice | folding crank gated out with spring pressure | Slot C |
| `feed_style` | enum | open_front / fold_down_feed_shelf | open_front | choice | freestanding_floor forces open_front | Slot D |
| `roller_count` | int enum | 2 / 3 | 2 | conditional | 3 forces non-spring pressure; top_z derived from N | Slot E / §8 |
| `palette_style` | enum | turquoise_white / red_black / zinc_black / cream_green / bare_steel | turquoise_white | choice | sampled per seed; drives all visual materials | Slot F |
| `width_scale` | float | [0.86, 1.24] | 1.0 | independent | `width = 0.466 * width_scale`; roller_length = 0.75 * width | S1 dimensions parameterized |
| `height_scale` | float | [0.90, 1.16] | 1.0 | independent | roller_spacing = 0.064 * height_scale | S8 |
| `crank_scale` | float | [0.82, 1.18] | 1.0 | independent | crank reach = 0.168 * crank_scale | S1/S11 |
| `top_z` | float | derived | 0.237/0.301 | equation | `lower_z + roller_spacing*(roller_count-1) + 0.068` | S8 L20-L26 |
| `pressure_travel` | float | [0.004, 0.014] | 0.010 | independent | prismatic upper bound; sampled-pose tested | S1/S6/S10 |
| support-pressure-drive-feed gates | constraint | — | — | conditional | listed in §9 compatibility matrix; resolved before build | implementation |

## 7.5 编译预算 / compile budget

Per-seed compile budget: 20s. Rationale: template uses Boxes/Cylinders plus small `tube_from_spline_points` crank meshes and simple repeated teeth; no heavy booleans or cadquery solids. Tessellation stays modest (`radial_segments=12`, gear teeth 12-16, crank samples per segment 10).

## Multiplicity / Copy Logic

- count_param: `roller_count`.
- N_range: `[2,3]` for this 小类; 2 is common, 3 is source-backed by S8 only.
- sampling domain: weighted `(2,2,2,3)` so standard twin rollers dominate but 3-roller feed appears in sweep.
- copied object: roller part names `roller_0..roller_N-1`; each has `axle` + `rubber`; exposed-gear module can add per-roller gear visuals.
- placement: z positions `lower_z + i * roller_spacing`; lower/middle rollers parent to `frame`; top roller parents to pressure block.
- joint policy: every roller has CONTINUOUS +X spin; top roller mimics crank +1, lower/middle alternate signs.
- gating: `roller_count=3` excludes `spring_loaded_bridge` in initial sampler because the source-backed spring record is 2-roller only and the spring seats collide with the raised middle-bearing envelope.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或结构支撑层 | 有 | `support_style`: origin_bench/table_clamp/freestanding_floor/wall_bench_bracket (S1-S4); `feed_style=fold_down_feed_shelf` adds moving shelf part (S9); `drive_style=folding_crank_handle` adds moving handle part (S11). |
| └ multiplicity | 同构件 ×N | 有 | `roller_count` 2/3, source-backed S1/S8; see §8. |
| ② 关节类型 | 图不变或相邻图中机制换 type/轴 | 有 | CONTINUOUS crank/rollers; PRISMATIC pressure slides/clamps; REVOLUTE shelf hinge and folding crank; dual handwheel CONTINUOUS adjusters. Sources S1/S9/S10/S11. |
| ③ 主体形态家族 / Primary Form Family | wringer support envelope changes recognizably | 有 | Registered in `support_style`: compact bench/table clamp (Volumetric Envelope Form), freestanding floor wringer (Macro Surface Construction), wall/bench bracketed wringer (Planar Boundary + support envelope). Source-backed S1-S4. |
| ④ 表面装饰 | host-conformal non-structural details | 有 | gear teeth on roller/crank hosts (S7), fasteners/bosses/brackets (S1-S4), spring coils/seats (S6), handwheel lobes (S10). Decorations are emitted as host visuals, not extra fixed parts. |
| ⑤ 尺寸/行程 | continuous scale and motion ranges | 有 | width_scale [0.86,1.24], height_scale [0.90,1.16], crank_scale [0.82,1.18], pressure_travel [0.004,0.014]. Motion envelopes: `pressure_slide_0/1` +Z [0,pressure_travel] sampled; `crank_rotation` continuous full spin sampled; `crank_fold` +Y [0,pi/2] targeted; `shelf_hinge` +X [0,pi/2] targeted; clamp slides [−0.015,0.012] sampled where present. `run_tests` calls sampled-pose collision with local captured-pin allowances. |
| ⑥ 涂装 | geometry unchanged, material/color only | 有 | `palette_style` = turquoise_white / red_black / zinc_black / cream_green / bare_steel; material classes cover painted metal, bare/zinc metal, rubber, black polymer/dark hardware. Sampled per seed and applied to every visual material role. |

## 采样与覆盖审计

总原始组合数：4 support × 3 pressure × 3 drive × 2 feed × 2 roller_count × 5 palette = 720.

Legal topology combos after gates: freestanding excludes feed shelf; spring excludes 3-roller and folding crank; folding crank excludes spring. Palette is sampled but geometry-free. Legal geometry tuples remain >100, enough for diverse sweep and viewer inspection.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses deterministic `random.Random(seed)` and weighted roller_count, then resolves compatibility before build. `slot_choices_for_seed(seed)` reports all six fields. No regression overrides or small curated seed table are used.

Topology target：1000-seed slot choice tuple coverage should realize every declared candidate; exact legal tuple count is report-only because compatibility gates intentionally remove source-unsupported compound cells.

Controlled local parameterization：continuous scales are clamped in `resolve_config`; `top_z`, `roller_length`, `side_x`, and pressure origins derive from resolved dimensions. Build does not leave cross-part constraints to fail later.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | support → pressure → drive → feed → roller_count → palette, then resolve gates | axis_realization should show every candidate |
| compatibility matrix | freestanding_floor ⇒ open_front; roller_count=3 ⇒ not spring_loaded_bridge; folding_crank_handle ⇒ not spring_loaded_bridge | no floating stand/shelf, no spring/middle-bearing collision, crank hinge visible |
| controlled local variation | width/height/crank/travel clamped and derived | roller nip preserved, top beam clears N=3, crank reachable |
| regression overrides | none | procedural seed domain is primary |
| random sweep | final 0-35 stage with corner seeds | contract failures, axis_realization, failed_corner_seeds |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_style | 4 | yes | yes | ③ Primary Form slot |
| pressure_style | 3 | yes | yes | spring has compatibility gates |
| drive_style | 3 | yes | yes | folding crank is 20260714 anchor |
| feed_style | 2 | yes | no | source pool has exactly open/no shelf and fold-down shelf; documented degrade |
| roller_count | 2 | yes | no | honest N range 2-3 only; 4+ excluded |
| palette_style | 5 | yes | yes | ⑥ axis, not structural topology |

## Validator

- `slot_choices_for_seed` returns implemented module names for support, pressure, drive, feed, roller_count, and palette_style.
- `config_from_seed` is deterministic procedural sampling for all ordinary seeds including seed 0.
- Compatibility matrix prevents unsupported source combinations and is resolved before geometry build.
- `palette_style` is sampled per seed and drives every visual material role.
- Critical joints exist with expected type/axis/range: pressure slides +Z, crank/rollers continuous +X, shelf hinge +X, folding crank +Y.
- Copied rollers follow `roller_i` naming and top/fixed parent policy.
- Captured overlaps are local to bearings, pressure posts, clamps, gears, and shelf hinge hardware.
- Dynamic tests include sampled-pose collision and targeted pressure, crank/fold, and shelf motion checks.

## Reject cases

- Output reads as pasta maker / laminator because rollers are too small, crank absent, or laundry support frame missing.
- `fold_down_feed_shelf` floats in front of the frame or has no `shelf_hinge`.
- `dual_handwheel_pressure` shows only one handwheel or handwheels do not attach to a pressure tie bar.
- `folding_crank_handle` is only a decorative bend and lacks `crank_fold`.
- 3-roller layout fails to raise top beam or leaves the third roller unsupported.
- Gear teeth, spring coils, handwheel lobes, or fasteners are emitted as separate fixed parts instead of host visuals.
- Palette is monochrome or not sampled per seed.
- Motion tests are removed or broad overlap allowances hide unrelated collisions.

## 与相邻类别的边界

- 不该混入：pasta maker / dough roller，因为本类必须有 laundry/wringer scale support, clamp/bracket/floor mount, and pressure adjusters rather than kitchen feed tray cues.
- 不该混入：laminator，因为本类 has hand crank, rubber wringing rollers, exposed support hardware, and pressure bridge rather than flat office appliance housing.
- 不该混入：washing machine or motorized wringer，因为 source map excludes motorized/washer-integrated variants.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pass |
| reviewer notes | 11 synced 5-star sources read; 20260714 anchors `fold_down_feed_shelf`, `dual_handwheel_pressure`, `folding_crank_handle` are adopted. `feed_style` and `roller_count` are 2-candidate slots because source-backed space honestly has only open/fold shelf and 2/3 rollers; 4+ rollers and motorized washer integration are excluded. |

## 模板实现备注（可选）

- Template implements the declared slots directly in `agent/templates/pictureX_0611_Hand_crank_clothes_wringer.py`.
- The crank/roller/pressure geometry uses the source family’s X-axis roller convention.
- Captured mechanical overlaps are scoped in `run_picturex_0611_hand_crank_clothes_wringer_tests`: bearing/axle, pressure stem/top beam, clamp screw/bracket, gear/axle, spring seat/block, and shelf hinge hardware.
- Compatibility gates are implemented in `config_from_seed` and repeated in `resolve_config` so user-supplied configs degrade safely.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | support/pressure/drive/roller/palette | origin_bench, single_screw_bridge, plain_bent_crank, 2 rollers | `rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b` | L83-L394 | baseline frame, rollers, crank, pressure screw, clamps |
| S2 | support | table_clamp | `rec_picturex0611_hand_crank_clothes_wringer_fork_table_clamp_frame_20260713` | L83-L430 | clamp brackets, bushing, T-handle clamp |
| S3 | support | freestanding_floor | `rec_picturex0611_hand_crank_clothes_wringer_fork_freestanding_floor_frame_20260713` | L90-L423 | floor stand and fixed wringer head |
| S4 | support | wall_bench_bracket | `rec_picturex0611_hand_crank_clothes_wringer_fork_wall_bench_bracket_20260713` | L179-L424 | wall/bench bracket plate and gussets |
| S5 | pressure | single_screw_bridge | `rec_picturex0611_hand_crank_clothes_wringer_fork_pressure_screw_bridge_20260713` | L284-L447 | pressure screw bridge and prismatic pressure blocks |
| S6 | pressure | spring_loaded_bridge | `rec_picturex0611_hand_crank_clothes_wringer_fork_spring_loaded_bridge_20260713` | L154-L241, L357-L433 | guide posts, springs, spring bridge |
| S7 | drive/decoration | exposed_twin_gear | `rec_picturex0611_hand_crank_clothes_wringer_fork_exposed_twin_gear_drive_20260713` | L35-L70, L195-L230, L352-L380 | spur gears, drive hub, gear allowances |
| S8 | multiplicity | roller_count=3 | `rec_picturex0611_hand_crank_clothes_wringer_fork_three_roller_feed_path_20260713` | L20-L26, L71-L98, L230-L416 | loop-emitted 3 rollers and raised frame |
| S9 | feed | fold_down_feed_shelf | `rec_picturex0611_hand_crank_clothes_wringer_fork_fold_down_feed_shelf_20260714` | L151-L167, L314-L454 | fold-down shelf, hinge knuckles, shelf hinge |
| S10 | pressure | dual_handwheel_pressure | `rec_picturex0611_hand_crank_clothes_wringer_fork_dual_handwheel_pressure_20260714` | L253-L329, L415-L442 | tie bar and dual handwheel adjusters |
| S11 | drive | folding_crank_handle | `rec_picturex0611_hand_crank_clothes_wringer_fork_folding_crank_handle_20260714` | L205-L283, L359-L382 | folding crank handle and `crank_fold` |
