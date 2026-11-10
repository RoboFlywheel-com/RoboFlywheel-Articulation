# pictureX_0611_drawing_compass_with_adjustable_legs - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_drawing_compass_with_adjustable_legs` |
| template path | `agent/templates/pictureX_0611_drawing_compass_with_adjustable_legs.py` |
| test path (optional) | inline `run_picturex_0611_drawing_compass_with_adjustable_legs_tests` |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | all confirmed 5-star samples for this category; each `record.json`, `revision.json`, prompt and complete build/test code read |
| source_index_policy | all thirteen confirmed anchors are adopted; no divider-only samples |

Sources: origins `...001...` L153-L498, `...002...` L115-L374, `...003...` L151-L531, `...004...` L57-L471;
forks `rec_drawing_compass_var_bow_spring_head` L182-L541, `...quick_set_center_wheel` L163-L426,
`...extension_bar_radius` L83-L580, `...lead_cartridge` L181-L602,
`rec_drawing_compass_var_side_spindle_adjuster_20260714` L471-L549,
`rec_drawing_compass_var_center_point_collet_20260714` L556-L666,
`rec_drawing_compass_var_folding_lower_legs_20260714` L250-L423,
`rec_drawing_compass_var_hinged_pen_adapter_20260714` L288-L544,
`rec_drawing_compass_var_tubular_legs_20260714` L61-L298.

## 核心身份

Two supported legs share a visible head pivot; one terminates in a centre needle and one in a pencil/lead end. A real head or radius-control articulation changes the circle radius. Divider-only calipers, protractors and single-arm beam compasses are excluded.

## 槽位 + 候选模块表

### Slot A：source_candidate / head_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `ring_head` | origin_anchor | origin 001 | L153-L498 | eligible | ring/barrel crown, two revolute legs |
| `crescent_head` | origin_anchor | origin 002 | L115-L374 | eligible | crescent guide envelope |
| `link_head` | origin_anchor | origin 003 | L151-L531 | eligible | link-and-wheel crown |
| `bridge_head` | origin_anchor | origin 004 | L57-L471 | eligible | flat bridge and pencil holder |
| `bow_spring_head` | forked_anchor | `rec_drawing_compass_var_bow_spring_head` | L182-L541 | eligible | leaf-spring crown and spreader |

### Slot B：leg_module（腿骨架 / 腿构造）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `solid_taper_legs` | origin_anchor | origins 001-004 | ranges above | eligible | one-piece tapered bar shank per leg |
| `tubular_legs` | forked_anchor | `rec_drawing_compass_var_tubular_legs_20260714` | L61-L125, L220-L298 | eligible | tubular (round-section) leg profile + ferrule |
| `folding_knee_legs` | forked_anchor | `rec_drawing_compass_var_folding_lower_legs_20260714` | L250-L423, L556-L575 | eligible | leg split into upper + lower sections joined by a revolute knee; `hinge_cap` over the head pivot |

Both alternatives replace the same element (the shank hanging off the head pivot), so they are candidates of
one slot rather than separate slots (§B "if two axes can't share a mating surface they are one slot").

### Slot C：radius_control
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `threaded_spreader` | origin_anchor | origin 001 | L395-L431 | eligible | continuous transverse screw/wheel |
| `fine_adjust_screw` | origin_anchor | origin 002 | L266-L374 | eligible | crescent guide fine screw |
| `link_wheel` | origin_anchor | origin 003 | L362-L499 | eligible | articulated link and wheel |
| `quick_set_center_wheel` | forked_anchor | `rec_drawing_compass_var_quick_set_center_wheel` | L308-L426 | eligible | release-wheel housing |
| `extension_rail` | forked_anchor | `rec_drawing_compass_var_extension_bar_radius` | L330-L580 | eligible | prismatic telescoping radius bar |
| `side_spindle_adjuster` | forked_anchor | `rec_drawing_compass_var_side_spindle_adjuster_20260714` | L471-L549 | eligible | side-mounted spindle: `adjust_screw` shaft + outboard knurled wheel + opposing `side_clamp` head driving leg spread |

### Slot D：marking_end
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pencil_clamp` | origin_anchor | origins 001-004 | ranges above | eligible | external pencil/lead holder |
| `pencil_holder` | forked_anchor | extension fork | L369-L580 | eligible with extension rail | supported sliding holder |
| `integrated_lead_collet` | forked_anchor | `rec_drawing_compass_var_lead_cartridge` | L444-L602 | eligible | integrated cartridge/collet form |
| `hinged_pen_adapter` | forked_anchor | `rec_drawing_compass_var_hinged_pen_adapter_20260714` | L288-L544 | eligible | `adapter_yoke` + `pencil_holder`: a revolute pen-adapter yoke carrying a technical pen off the marking-leg tip |

### Slot E：centre_end
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_needle` | origin_anchor | origins 001-004 | ranges above | eligible | needle fused into the centre-leg tip |
| `needle_cartridge_collet` | forked_anchor | `rec_drawing_compass_var_center_point_collet_20260714` | L556-L666 | eligible | `needle_cartridge` prismatic inside a collet sleeve (settable point depth) |

## 槽位图（slot graph）

pattern: mixed. `head_module` is root; `leg_module` hangs `needle_leg` / `marking_leg` off the head as parallel
y-revolute children (and, for `folding_knee_legs`, a second revolute knee to `needle_lower_leg` /
`marking_lower_leg`). `radius_control` is a captured transverse continuous screw or x-prismatic rail at the
lower head guide. `centre_end` and `marking_end` are hosted on whichever part carries the leg tip: fused as host
visuals for the plain forms, or emitted as one extra articulated part (`needle_cartridge` PRISMATIC /
`pen_adapter` REVOLUTE) for the collet / pen-adapter candidates. Compatibility is source-candidate locked by
`resolve_config`, so no illegal module tuple is reachable.

## 每槽位 Module Emits / Interfaces

### Slot A / head_module
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head` | origins/forks above |
| internal joints | two y-revolute leg pivots (emitted with Slot B) | all anchors |
| downstream interface | visible crown barrel plus lower spreader-support spine | source head/pivot families |

### Slot B / leg_module
| emits | 描述 | 来源 |
|---|---|---|
| parts | `needle_leg`, `marking_leg` (+ `needle_lower_leg`, `marking_lower_leg` when folding) | origins + tubular/folding forks |
| internal joints | two y-revolute head pivots; two y-revolute knees for `folding_knee_legs` | folding fork L556-L575 |
| upstream interface | head pivot barrel at `x = ±0.24·leg_spread` | source head/pivot families |

### Slot C / radius_control
| emits | 描述 | 来源 |
|---|---|---|
| parts | `radius_control` | screw/wheel/extension/side-spindle anchors |
| internal joints | continuous x screw or prismatic x rail | origins 001-004, fork anchors |
| upstream interface | captured guide at `z=-0.46*leg_length` | source spreader location |

### Slot D / marking_end
| emits | 描述 | 来源 |
|---|---|---|
| parts | host visual on the marking leg tip; `pen_adapter` (REVOLUTE) for the hinged adapter | origins + lead/pen forks |
| internal joints | none, or one y-revolute yoke pivot | pen-adapter fork L527-L544 |
| upstream interface | aligned working-tip plane with centre needle | category contract |

### Slot E / centre_end
| emits | 描述 | 来源 |
|---|---|---|
| parts | host visual on the needle leg tip; `needle_cartridge` (PRISMATIC) for the collet | origins + collet fork |
| internal joints | none, or one z-prismatic cartridge stroke | collet fork L595-L612 |
| upstream interface | collet sleeve concentric with the centre axis | collet fork |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 13 confirmed candidates | `ring_head` | choice | deterministic RNG | source pool |
| module enums | enum | tables above | source-derived | equation | derived from candidate compatibility | source map |
| `leg_length` | float | [0.28,0.48] m | 0.36 | independent | clamp | all anchors |
| `leg_spread` | float | [0.07,min(0.19,0.46L)] m | 0.12 | inequality | preserves crown and tip alignment | interfaces |
| `extension_travel` | float | [0.04,min(0.16,0.38L)] m | 0.10 | conditional | rail candidate only | extension fork |
| knee travel | derived | `[0, 0.85]` rad | — | equation | `_KNEE_UPPER_LIMIT`; source knees run `[0, 2.4]`, clamped so the folded lower leg clears the spreader | folding fork L556-L575 |
| cartridge stroke | derived | `[0, 0.020]` m | — | equation | `_CARTRIDGE_STROKE` | collet fork L595-L612 |

## compile budget

5-20s per seed; Box/Cylinder procedural geometry only, no repeated booleans. Measured: <1s/seed.

## Multiplicity / Copy Logic

- 无复制数量逻辑：the two legs are distinct semantic roles, not an arbitrary N array. The folding candidate adds a
  second *section* per leg (a topology change, not a sampled count).

## 视觉多样性 6 轴考察
| 轴 | 怎么判断 | 有/无 | 取值 / 理由 |
|---|---|---|---|
| ① 骨架图 | moving part/edge changes | 有 | 4-part two-leg graph; +1 part/joint for the needle cartridge; +1 for the pen adapter; +2 parts/+2 joints for the folding knee legs; source-backed prismatic extension |
| └ multiplicity | repeated N | 无 | centre and marking legs are role-specific |
| ② 关节类型 | edge label changes | 有 | revolute leg pivots + knees, continuous adjuster/side spindle, prismatic extension rail, prismatic needle cartridge, revolute pen-adapter yoke |
| ③ 主体形态家族 | recognizable envelope changes | 有 | ring/crescent/link/bridge/bow heads; solid-taper vs tubular leg profile; pencil clamp vs lead collet vs needle-cartridge collet vs technical-pen adapter; Volumetric Envelope Form |
| ④ 表面装饰 | host detail | 有 | knurling/graduations/grip bands, host-conformal; ferrule and clamp heads derived from the host shank section |
| ⑤ 尺寸/行程 | continuous scale/motion | 有 | ranges above; sampled collision plus targeted left/right radius, knee-fold, cartridge-extend and pen-tilt poses; coupled-leg overlap declaration covers unreachable independent crossings |
| ⑥ 涂装 | materials/colors | 有 | industrial, painted, walnut, slate metal/accent palettes |

## 采样与覆盖审计

Thirteen source candidates drive compatible head/leg/control/marking/centre modules; independent continuous
values are sampled then clamped. No regression overrides. Sweep plan: smoke 0-7, full pipeline 0-35 plus
corners. 1000-seed topology probe is report-only; finite source vocabulary is expected to saturate below 300
tuples.

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 13 | yes | yes | confirmed pool (4 origins + 9 forks) |
| head_module | 5 | yes | yes | source-backed |
| leg_module | 3 | yes | yes | source-backed (tubular + folding forks) |
| radius_control | 6 | yes | yes | source-backed |
| marking_end | 4 | yes | yes | source-backed |
| centre_end | 2 | yes | no | only the collet fork gives a second structurally distinct centre end; flagged, not padded |

Realized on the 0-35 + corner sweep (`axis_realization`): all 13 `source_candidate` values, all 3 `leg_module`
values, all 6 `radius_control` values (incl. `side_spindle_adjuster` ×10), all 4 `marking_end` values (incl.
`hinged_pen_adapter` ×3) and both `centre_end` values (`needle_cartridge_collet` ×3).

## Validator

- deterministic `config_from_seed`, exact `slot_choices_for_seed`, implemented compatibility only
- visible head support, aligned centre/marking tips, three or more non-fixed mechanisms
- sampled-pose collision and targeted leg / knee / cartridge / pen-adapter poses
- no decoration-only fixed parts (the folding `hinge_cap` stays a head visual)

## Reject cases

- missing one working leg/tip; shared pivot not visible; static radius control; divider-only drift; extension without supported rail; crossed-leg pose treated as a normal reachable state; a knee, cartridge or pen adapter attached without a real articulation.

## 与相邻类别的边界

- Divider/caliper: lacks distinct marking and centre roles.
- Beam compass/trammel: single beam topology rather than two shared-pivot legs.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | P3 pool confirmed 2026-07-14; 13/13 sources read (5 late forks folded in 2026-07-14); pipeline pass (0-35 + corner, pass_rate 1.0) and programmatic geometric QA passed. Image previews unavailable in this environment (`pyrender` not installed) — identity checked programmatically instead. |
