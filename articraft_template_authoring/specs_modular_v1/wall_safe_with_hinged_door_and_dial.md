# Modular Spec - wall_safe_with_hinged_door_and_dial

## 元信息
| 项 | 值 |
|---|---|
| slug | `wall_safe_with_hinged_door_and_dial` |
| template path | `agent/templates/wall_safe_with_hinged_door_and_dial.py` |
| test path (optional) | `tests/agent/test_wall_safe_with_hinged_door_and_dial_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：核心是 wall-safe body -> hinged door 的 serial REVOLUTE spine，门面上并联挂载 rotary dial / handle / wheel，另有 source-backed optional auxiliary module（deposit flap / prismatic drawer）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 |
| read_count | 33 |
| read_scope | all 5-star samples in `wall_safe_with_hinged_door_and_dial`; read `model.py` / `revision.json` / `record.json` / `prompt.txt` / category metadata |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的真实结构轴：

| 轴 | 观察到的真实结构变体 |
|---|---|
| body / case | hollow recessed wall box from primitive walls; document-safe tall carcass with real front frame; CADQuery square recessed frame; broad wall flange / hinge trim |
| door / hinge | right vertical hinge with alternating barrels; left vertical hinge with alternating knuckles; heavy vault slab with raised ribs and hinge rib; deposit-opening door with cutout mesh |
| lock control | continuous combination dial; revolute or continuous handle; spoked handwheel; lower latch lever |
| auxiliary motion | no auxiliary child; top-hinged deposit flap; hinged document flap; shallow prismatic drawer |

## 核心身份

`wall_safe_with_hinged_door_and_dial` 是嵌入墙面的保险箱：固定的 recessed body/case 提供墙体框、侧壁、背板和铰链承载；一个厚重门板通过垂直 REVOLUTE hinge 向外开启；门面至少有一个可旋转 combination dial，并通常配有 handle / handwheel / latch lever。核心身份不是普通柜门、抽屉柜、电子 keypad safe 或无铰链的 lock box。

成熟模板必须保持 closed pose：门板贴近/略 proud 于 frame，dial/handle 坐在门面真实 bushing 上，hinge origin 落在可见 hinge barrels/knuckles 上。可选 deposit flap 或 drawer 只能作为附加活动层，不得替代主 door hinge。

## 槽位 + 候选模块表

### Slot A：body_case

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| recessed_rect_box | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L33-L59 | eligible if compatible | primitive hollow wall-safe body: side walls/back/frame + right hinge leaf/barrels |
| tall_document_case | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L56-L133 | eligible if compatible | tall narrow document-safe carcass with side/top/bottom walls, proud front frame, body hinge webs/knuckles |
| cadquery_square_frame | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L24-L88 | eligible if compatible | CADQuery square frame/recess mesh with fixed hinge knuckles/brackets |
| broad_flange_left_case | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L60-L146 | eligible if compatible | wall surface + recessed case + left trim hinge flange and alternating stationary knuckles |

### Slot B：door_panel_hinge

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| right_hinged_deposit_door | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L61-L90 | eligible if compatible | thick right-hinged slab with bevels, free edge, hinge edge, deposit flap reveal; REVOLUTE `body_to_door` |
| cutout_document_door | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L137-L175, L243-L251 | eligible if compatible | ExtrudeWithHoles door panel with upper deposit opening, hinge leaf/web/knuckles; REVOLUTE `door_hinge` |
| cadquery_flat_door | rec_wall_safe_with_hinged_door_and_dial_8a6bb6f94c0b454896796a6e0026d6bd | L36-L67 | eligible if compatible | CADQuery recessed body mate + flat door panel, simple hinge barrel; REVOLUTE `body_to_door` |
| vault_ribbed_left_door | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L147-L209, L248-L256 | eligible if compatible | raised perimeter ribs, hinge rib, door knuckles, dial bearing; left/outward REVOLUTE case-to-door |

### Slot C：lock_control

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| knurled_combination_dial | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L92-L128 | eligible if compatible | mesh_from_geometry dial with tick marks and center cap; CONTINUOUS door-to-dial |
| dial_over_lever_handle | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L177-L220, L252-L269 | eligible if compatible | separate rotary dial plus lever handle/hub; CONTINUOUS dial and REVOLUTE lever spindle |
| cadquery_spoked_handwheel | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L24-L49, L212-L274 | eligible if compatible | CADQuery spoked handwheel plus continuous dial, both mounted to door bearing |
| lower_latch_lever | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L129-L188 | eligible if compatible | continuous dial with center hub plus lower latch lever as REVOLUTE door child |

### Slot D：auxiliary_motion

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| no_auxiliary | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L118-L188 | eligible if compatible | only main door + dial + latch; no extra moving auxiliary part |
| top_deposit_flap | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L68-L79, L162-L176 | eligible if compatible | door reveal plus separate top-hinged deposit flap; REVOLUTE `door_to_flap` |
| document_flap_cutout | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L137-L175, L223-L275 | eligible if compatible | cutout door plus matching flap panel; REVOLUTE flap hinge at top of slot |
| shallow_inner_drawer | rec_wall_safe_with_hinged_door_and_dial_c49f5dbe0645494b857910f53e190f30 | L94-L128 | eligible if compatible | internal shallow drawer/tray as PRISMATIC child from body after main door/dial |

## 槽位图（slot graph）

pattern: mixed

```text
[Slot A body_case]
  -- REVOLUTE vertical hinge at visible frame/knuckle axis -->
[Slot B door_panel_hinge]
  ├─ CONTINUOUS / REVOLUTE door-normal control axis --> [Slot C lock_control]
  └─ optional REVOLUTE flap or PRISMATIC drawer --> [Slot D auxiliary_motion]
```

接口点位：

- body_case downstream interface：front frame hinge line, vertical axis through visible barrels/knuckles; parent face is hinge leaf / frame edge.
- door_panel_hinge upstream interface：door hinge rib/leaf/knuckles centered on the same vertical hinge axis; child face is hinge knuckle or hinge leaf.
- lock_control upstream interface：door face bushing/dial bearing/handle hub; consumer joint axis is door-normal `(0, ±1, 0)` or local equivalent from source.
- auxiliary_motion upstream interface：for flap, top edge of deposit opening on door; for drawer, interior guide/slot inside body; no_auxiliary emits no extra child.

Compatibility / derived policies:

- `document_flap_cutout` requires `cutout_document_door` or another door with explicit deposit opening.
- `shallow_inner_drawer` pairs with body cases that expose an interior guide; it must not be sampled with an auxiliary flap in the same build.
- left/right hinge side is derived from door candidate; body hinge visuals must mirror or be selected compatibly.
- `cadquery_spoked_handwheel` requires a door bearing large enough for the wheel hub; reject very small flat doors.

## 每槽位 Module Emits / Interfaces

### Slot A / module recessed_rect_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` with hollow walls, frame, hinge leaf/barrels | S-A1 / L33-L59 |
| internal joints | none; body is fixed root | S-A1 |
| upstream interface | none | S-A1 |
| downstream interface | right vertical hinge barrels on frame edge | S-A1 / L55-L59 |

### Slot A / module tall_document_case
| emits | 描述 | 来源 |
|---|---|---|
| parts | tall `body` carcass with back/sides/top/bottom and front frame | S-A2 / L56-L133 |
| internal joints | none | S-A2 |
| upstream interface | none | S-A2 |
| downstream interface | hinge_x / door_y vertical body knuckle axis | S-A2 / L118-L133 |

### Slot A / module cadquery_square_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | CADQuery `case` mesh plus hinge brackets/knuckles | S-A3 / L24-L88 |
| internal joints | none | S-A3 |
| upstream interface | none | S-A3 |
| downstream interface | frame side hinge brackets | S-A3 / L76-L88 |

### Slot A / module broad_flange_left_case
| emits | 描述 | 来源 |
|---|---|---|
| parts | wall surface, recessed body, hinge flange, stationary knuckles | S-A4 / L60-L146 |
| internal joints | none | S-A4 |
| upstream interface | none | S-A4 |
| downstream interface | left trim hinge flange and knuckle axis | S-A4 / L123-L146 |

### Slot B / door_panel_hinge modules
| module | emits | upstream interface | downstream interfaces | 来源 |
|---|---|---|---|---|
| right_hinged_deposit_door | door slab, bevels, free edge, hinge edge, flap gaps; door REVOLUTE | hinge edge/barrel axis | door face for dial/handle/flap | S-B1 / L61-L90 |
| cutout_document_door | ExtrudeWithHoles door slab with cutout, hinge leaf/web/knuckles | cutout door hinge knuckle axis | door face bushing + deposit opening top edge | S-B2 / L137-L175, L243-L251 |
| cadquery_flat_door | simple flat panel paired to CADQuery body hinge | hinge barrel axis | door face for simple dial/handle | S-B3 / L36-L67 |
| vault_ribbed_left_door | raised-rib vault door, hinge rib, door knuckles, dial bearing | left hinge rib/knuckles | large dial bearing and wheel/dial mount | S-B4 / L147-L209, L248-L256 |

### Slot C / lock_control modules
| module | emits | upstream interface | internal joints | 来源 |
|---|---|---|---|---|
| knurled_combination_dial | dial mesh, center cap, tick marks | door dial bushing | CONTINUOUS dial spin | S-C1 / L92-L128 |
| dial_over_lever_handle | dial cap/pointer + lever hub/arm/end | door face spindle sockets | CONTINUOUS dial + REVOLUTE lever | S-C2 / L177-L220, L252-L269 |
| cadquery_spoked_handwheel | CADQuery handwheel plus continuous dial | large door bearing | CONTINUOUS dial and wheel | S-C3 / L24-L49, L212-L274 |
| lower_latch_lever | combination dial + lower latch lever | lower door face | CONTINUOUS dial + REVOLUTE latch lever | S-C4 / L129-L188 |

### Slot D / auxiliary_motion modules
| module | emits | upstream interface | internal joints | 来源 |
|---|---|---|---|---|
| no_auxiliary | no extra child | none | none | S-D1 / L118-L188 |
| top_deposit_flap | flap panel and hinge cylinder | door deposit opening top edge | REVOLUTE top-hinged flap | S-D2 / L68-L79, L162-L176 |
| document_flap_cutout | door cutout reveal and flap panel | cutout slot top edge | REVOLUTE document flap | S-D3 / L137-L175, L223-L275 |
| shallow_inner_drawer | inner drawer/tray | body guide slot | PRISMATIC body-to-drawer | S-D4 / L94-L128 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| body_case | enum | recessed_rect_box / tall_document_case / cadquery_square_frame / broad_flange_left_case | sampled | controls root envelope, hinge side compatibility | Slot A |
| door_panel_hinge | enum | right_hinged_deposit_door / cutout_document_door / cadquery_flat_door / vault_ribbed_left_door | sampled | controls door part tree, hinge side, door face sockets | Slot B |
| lock_control | enum | knurled_combination_dial / dial_over_lever_handle / cadquery_spoked_handwheel / lower_latch_lever | sampled | controls rotary children on door | Slot C |
| auxiliary_motion | enum | no_auxiliary / top_deposit_flap / document_flap_cutout / shallow_inner_drawer | sampled | optional child and extra joint type | Slot D |
| width_scale | float | [0.86, 1.16] | sampled | safe body/door width; clamped by hinge and dial clearance | source dimensions |
| height_scale | float | [0.86, 1.20] | sampled | safe height and hinge barrel spacing | source dimensions |
| depth_scale | float | [0.85, 1.15] | sampled | recessed box depth and frame proudness | source dimensions |
| hinge_barrel_count | int | 2-5 | sampled | local hinge visual repeat only; not topology multiplicity | S-A/S-B |
| handle_spoke_count | int | 0, 3-8 | sampled by lock_control | handwheel/spoked handle visuals | S-C |
| door_swing_limit | float | [1.1, 1.9] rad | sampled | door REVOLUTE limit, rest pose remains closed | S-B |
| drawer_travel | float | [0.04, 0.10] | sampled when drawer | PRISMATIC limit; must stay within body depth | S-D4 |

## Multiplicity / Copy Logic

本类别没有模板级可变 part/joint 数量 multiplicity；核心 named slots 固定为 body, door, lock control, optional auxiliary。

Module-local repeated elements are allowed:

- hinge barrels/knuckles: repeated visuals on body/door hinge line, count 2-5, no separate joints.
- dial ticks: repeated visuals on dial part, no separate joints.
- handle/handwheel spokes: repeated visuals inside lock_control module, no separate joints.
- lock bolts/trims: repeated door visuals only.


## 拓扑多样性审计

总组合数（合法化前）：A(4) × B(4) × C(4) × D(4) = 256。


理由：即使 compatibility gating 移除 deposit cutout / drawer 等不兼容组合，body case、door hinge, lock control 和 auxiliary motion 仍提供远超 10 个真实 part tree / joint topology 组合。D slot 能改变是否有额外 REVOLUTE flap 或 PRISMATIC drawer，C slot 能改变 dial-only、dial+lever、handwheel、latch lever 的 child structure。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：

- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special.
- Sampling order: body_case -> door_panel_hinge -> lock_control -> auxiliary_motion -> local scales/counts.
- `resolve_config` applies compatibility matrix before build and exposes final choices through `slot_choices_for_seed`.
- Initial sweep range: seeds 0-49 via `uv run articraft template sweep-pipeline wall_safe_with_hinged_door_and_dial`.
- Maturity audit: seeds 0-999, target slot choice tuple distinct ≥300 unless compatibility constraints are reviewer-narrowed.
- Regression overrides: none initially; future overrides only for known failed seeds or reviewer-selected examples.

Controlled local parameterization：

- `width_scale [0.86,1.16]`, `height_scale [0.86,1.20]`, `depth_scale [0.85,1.15]`: derive frame, door, hinge line, dial and handle placements; must preserve closed pose and frame containment.
- `hinge_barrel_count 2-5`: local visual repeat along hinge; no extra articulation.
- `handle_spoke_count 0/3-8`: local handwheel/handle visual repeat; requires real hub and door bushing.
- `door_swing_limit [1.1,1.9]`: lower limit includes rest closed pose; opening must move door outward.
- `drawer_travel [0.04,0.10]`: only for `shallow_inner_drawer`, clamped to safe depth.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural-first weighted slot choices with compatibility gates | `slot_choices_for_seed` matches built slots |
| compatibility matrix | cutout flaps require cutout door; drawer requires body guide; handwheel requires large bearing; hinge side mirrored between body and door | no floating flap/drawer, no impossible hinge side, no door-normal axis mismatch |
| controlled local variation | clamp body/door/dial/hinge dimensions in `resolve_config` | closed door, visible hinge, rotary controls attached to door face |
| regression overrides | none initially | only sparse failure/reviewer-driven overrides |
| random sweep | 0-49 initial, 0-999 maturity | , hinge origin, mating gap, overlap, door swing semantics |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| body_case | 4 | yes | yes | real case/carcass variations |
| door_panel_hinge | 4 | yes | yes | real hinge/door part tree variations |
| lock_control | 4 | yes | yes | dial/handle/wheel/latch structure changes |
| auxiliary_motion | 4 | yes | yes | none/flap/drawer changes joint topology |

Compatibility matrix / gating：

- `document_flap_cutout` requires `cutout_document_door`; `top_deposit_flap` requires a visible door cutout/reveal.
- `shallow_inner_drawer` requires body/case with interior guide and cannot pair with auxiliary flaps.
- `vault_ribbed_left_door` should pair with left/broad/cadquery case or mirrored root hinge; reject right-only hinge visuals unless mirrored.
- `cadquery_spoked_handwheel` requires door bearing and enough door face clearance; reject tiny document doors.
- all lock controls must mount to the door, not body, and use door-normal rotary/revolute axes.

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for all four slots.
- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special.
- Main door joint is REVOLUTE, vertical, and swings outward from a visible hinge line.
- Dial joint is CONTINUOUS and mounted on a real door bushing/bearing.
- Handle/wheel/latch children, when present, are mounted to the door face with real support and MatingContract.
- Auxiliary flap is REVOLUTE around a visible top edge; drawer is PRISMATIC along a real guide and does not replace the main door.
- Closed pose keeps door within or just proud of frame; no door/body collision except declared hinge capture.
- CADQuery / ExtrudeWithHoles / mesh dial sources are preserved, not downgraded to crude placeholders.

## Reject cases

- Door is fixed or missing the main REVOLUTE hinge.
- Dial is decorative visual only when the source/control module requires a rotating child.
- Handle/wheel floats on the door without bushing/hub support.
- Deposit flap is sampled on a door without a cutout/reveal.
- Drawer travel exceeds body depth or intersects the closed door.
- Hinge origin is not colocated with visible hinge barrels/knuckles.
- CADQuery case/handwheel or ExtrudeWithHoles door is replaced by a crude Box-only version.
- Template samples only color/size changes and lacks real lock/auxiliary topology variation.

## 与相邻类别的边界

- 不该混入：`wall_safe_with_hinged_door_and_keypad` or electronic keypad safes（keypad-only lock identity; this category requires round dial/control).
- 不该混入：`drawer_cabinet_with_sliding_drawers`（drawer can be auxiliary only; main identity is hinged wall safe).
- 不该混入：`cabinet_with_hinged_door`（lacks combination dial / safe frame / recessed vault semantics).
- 不该混入：`vault_door` as large freestanding vault（this category is a wall-mounted/recessed safe scale).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | User requested no separate approval; spec built after reading all 33 five-star samples and may proceed directly to TEMPLATE_AFTER_REVIEW. |

## 模板实现备注（可选）

- Reuse helpers for side-dependent hinge coordinates and door-normal axes.
- MatingContract focus: body hinge leaf/barrel -> door hinge knuckle; door dial bearing -> dial shaft/cap; door handle hub -> handle/wheel shaft; door cutout top edge -> flap hinge; body guide -> drawer rail.
- Element-scoped allow_overlap is expected for hinge pin/knuckle and dial shaft/bushing captures only.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | body_case | recessed_rect_box | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L33-L59 | primitive recessed body and right hinge barrels |
| S-A2 | body_case | tall_document_case | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L56-L133 | document-safe carcass and hinge knuckles |
| S-A3 | body_case | cadquery_square_frame | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L24-L88 | CADQuery case/frame and hinge brackets |
| S-A4 | body_case | broad_flange_left_case | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L60-L146 | broad wall flange and left hinge trim |
| S-B1 | door_panel_hinge | right_hinged_deposit_door | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L61-L90 | thick door slab, bevels, hinge, deposit reveal |
| S-B2 | door_panel_hinge | cutout_document_door | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L137-L175, L243-L251 | ExtrudeWithHoles door and hinge |
| S-B3 | door_panel_hinge | cadquery_flat_door | rec_wall_safe_with_hinged_door_and_dial_8a6bb6f94c0b454896796a6e0026d6bd | L36-L67 | CADQuery body + simple flat door hinge |
| S-B4 | door_panel_hinge | vault_ribbed_left_door | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L147-L209, L248-L256 | ribbed vault door and left hinge |
| S-C1 | lock_control | knurled_combination_dial | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L92-L128 | mesh dial and continuous spin |
| S-C2 | lock_control | dial_over_lever_handle | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L177-L220, L252-L269 | dial plus lever spindle |
| S-C3 | lock_control | cadquery_spoked_handwheel | rec_wall_safe_with_hinged_door_and_dial_82a4ccc1730043b887b2eac9ebdd3696 | L24-L49, L212-L274 | CADQuery handwheel and continuous control |
| S-C4 | lock_control | lower_latch_lever | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L129-L188 | latch lever and continuous dial |
| S-D1 | auxiliary_motion | no_auxiliary | rec_wall_safe_with_hinged_door_and_dial_8b9f7f36ed94414e9347d51161971f01 | L118-L188 | no extra auxiliary beyond door/dial/latch |
| S-D2 | auxiliary_motion | top_deposit_flap | rec_wall_safe_with_hinged_door_and_dial_864a084aaf8c41c29e66564b852ca7d0 | L68-L79, L162-L176 | top-hinged deposit flap |
| S-D3 | auxiliary_motion | document_flap_cutout | rec_wall_safe_with_hinged_door_and_dial_a3763368b7844a3ca30789cbd2172fc7 | L137-L175, L223-L275 | cutout document flap |
| S-D4 | auxiliary_motion | shallow_inner_drawer | rec_wall_safe_with_hinged_door_and_dial_c49f5dbe0645494b857910f53e190f30 | L94-L128 | shallow PRISMATIC drawer |
