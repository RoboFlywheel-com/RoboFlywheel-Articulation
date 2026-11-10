# pictureX_0611_elevator_button_panel - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_elevator_button_panel` |
| template path | `agent/templates/pictureX_0611_elevator_button_panel.py` |
| test path (optional) | inline author tests |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `parallel_children + multiplicity` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | two origins and six accepted forks; complete metadata/prompt/build/tests |
| source_index_policy | all confirmed sources adopted |

Sources: origins 001 L203-L448, 002 L155-L460; forks square buttons L256-L506, single-column-8 L223-L469, horizontal console L179-L497, destination keypad L252-L528, glass touch hybrid L249-L535, split-zone banks L195-L540.

## 核心身份

Mounted elevator car control panel with floor selection, door/emergency controls and at least one physical actuator. Generic keypads, industrial cabinets and single hall-call plates are excluded.

## 槽位 + 候选模块表

### Slot A：enclosure_form (③ Primary Form Family)
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `portrait` | origin_anchor | origins 001/002 | ranges above | eligible | standard tall panel |
| `wide_portrait` | origin_anchor | origin 002 | L155-L460 | eligible | service/display-heavy envelope |
| `narrow_portrait` | forked_anchor | single-column fork | L223-L469 | eligible | narrow one-column boundary |
| `horizontal` | forked_anchor | horizontal fork | L179-L497 | eligible | low car-console boundary |
| `portrait_glass` | forked_anchor | glass hybrid | L249-L535 | eligible | black-glass macro surface |

### Slot B：layout_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `floor_grid` | origin_anchor | origins | ranges above | eligible | 2-column floor grid |
| `single_column` | forked_anchor | single-column fork | L223-L469 | eligible, N=8 | one vertical bank |
| `destination_keypad` | forked_anchor | keypad fork | L252-L528 | eligible | 3-column numeric/destination topology |
| `touch_hybrid` | forked_anchor | glass hybrid | L249-L535 | eligible | touch cells plus mechanical safety controls |
| `split_zone_banks` | forked_anchor | split-zone fork | L195-L540 | eligible | separated low/high banks |

### Slot C：actuator_form
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `round_mechanical` | origin_anchor | origins | ranges above | eligible | prismatic round caps |
| `square_mechanical` | forked_anchor | square/keypad forks | ranges above | eligible | prismatic square guide caps |
| `glass_touch` | forked_anchor | glass hybrid | L249-L535 | eligible with mechanical door/key | host touch cells; safety controls remain articulated |

## 槽位图（slot graph）

Root `body` panel; N floor selectors are parallel y-prismatic children for mechanical layouts, while touch cells are body visuals. `door_control` is always y-prismatic and `emergency_key` y-revolute, so every layout retains physical actuation. Layout/enclosure/actuator compatibility is source-candidate locked.

## 每槽位 Module Emits / Interfaces
| slot | emits | joints | interface/source |
|---|---|---|---|
| enclosure | `body`, enclosure/display/legend host visuals | none | wall mounting back plane; all sources |
| layout/actuator | `floor_button_i` or host touch cells | N y-prismatic joints | supported front face; origins/forks |
| safety controls | `door_control`, `emergency_key` | prismatic + revolute | bottom legend band/front face; sources |

## 参数范围汇总
| 参数 | 类型 | 范围 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 8 confirmed | portrait round | choice | deterministic RNG | pool |
| module enums | enum | tables | derived | equation | candidate compatibility | source map |
| `floor_button_count` | int | [4,24], single-column=8 | 10 | conditional | grid pitch derives from rows/cols | sources/fork |
| `width` | float | [0.20,0.46], horizontal ≥0.62 | 0.28 | conditional | enclosure form | sources |
| `height` | float | [0.48,1.02], horizontal ≤0.42 | 0.72 | conditional | enclosure form | sources |
| `button_stroke` | float | [0.003,0.012] m | 0.006 | independent | front-face guide | sources |

## compile budget

5-20s per seed; up to 24 primitive selector children.

## Multiplicity / Copy Logic

- `floor_button_count`: N=4..24, deterministic uniform test sampling; indexed `floor_button_i`; regular row/column placement; each mechanical selector gets one prismatic joint. N is coverage-only, not structural-distinct inflation.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 取值 / 理由 |
|---|---|---|
| ① 骨架图 | 有 | grid, keypad, touch hybrid, split banks |
| └ multiplicity | 有 | floor-button N=4..24; single-column N=8 |
| ② 关节类型 | 有 | prismatic selectors/door control and revolute key |
| ③ 主体形态家族 | 有 | portrait/narrow/horizontal/glass forms; Planar Boundary + Macro Surface Construction |
| ④ 表面装饰 | 有 | legends/braille/indicator bands as embedded host visuals |
| ⑤ 尺寸/行程 | 有 | enclosure/count/pitch/stroke; sampled collision + targeted selector/door/key poses |
| ⑥ 涂装 | 有 | stainless-like industrial, painted and slate/glass palettes |

## 采样与覆盖审计

Eight source candidates deterministically resolve legal modules; N and dimensions are then sampled/clamped. No overrides. Sweep 0-35 plus corners and viewer 0-9; axis report must show every layout/form/actuator and multiple N values.

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 8 | yes | yes | confirmed |
| enclosure_form | 5 | yes | yes | includes ③ slot |
| layout_module | 5 | yes | yes | source-backed |
| actuator_form | 3 | yes | yes | source-backed |

## Validator

- at least one mechanical selector plus door/key controls; indexed buttons remain supported
- deterministic choices and bounded count/pitch; sampled collision and targeted control poses
- front decoration embedded into the host panel surface

## Reject cases

- hall-call-only plate; generic keypad/cabinet; no door/emergency control; all-static touch surface; unsupported/floating selectors; count exceeds layout envelope.

## 与相邻类别的边界

- Hall call station: excluded because a car panel has floor bank plus door/emergency controls.
- Industrial control panel: excluded because elevator-specific layout/controls are mandatory.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 8/8 sources read; pipeline and seeds 0-9 visual QA passed |
