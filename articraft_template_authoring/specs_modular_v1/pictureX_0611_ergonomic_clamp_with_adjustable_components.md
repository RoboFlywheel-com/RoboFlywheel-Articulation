# pictureX_0611_ergonomic_clamp_with_adjustable_components - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_ergonomic_clamp_with_adjustable_components` |
| template path | `agent/templates/pictureX_0611_ergonomic_clamp_with_adjustable_components.py` |
| test path (optional) | inline author tests |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | two image-faithful origins plus six accepted forks; complete metadata/prompt/build/tests |
| source_index_policy | laptop-tray image identity governs legacy label; forearm/monitor/static stands excluded |

Sources: origins 001 L18-L587, 002 L148-L498; forks gas spring L19-L606, telescoping boom L209-L528, scissor linkage L199-L549, quick release L18-L669, dual-screw clamp L164-L537, sliding tray rails L148-L595.

## 核心身份

Desk-clamped articulated laptop tray arm with supported height/reach/tilt adjustment and a broad stop-lipped equipment tray. Not a forearm support, VESA-only monitor arm or static laptop stand.

## 槽位 + 候选模块表

### Slot A：clamp_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_screw_clamp` | origin_anchor | origins | ranges above | eligible | C-clamp body/one spindle/column |
| `dual_screw_clamp` | forked_anchor | dual-screw fork | L164-L537 | eligible | broad two-spindle load-distribution form |

### Slot B：reach_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `serial_two_link` | origin_anchor | origins | ranges above | eligible | two z-revolute reach members |
| `gas_spring_parallelogram` | forked_anchor | gas fork | L19-L606 | eligible | counterbalanced parallel lower link |
| `telescoping_boom` | forked_anchor | telescoping fork | L209-L528 | eligible | prismatic second stage |
| `scissor_linkage` | forked_anchor | scissor fork | L199-L549 | eligible | crossed-link macro construction |

### Slot C：tray_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tilting_tray` | origin_anchor | origins | ranges above | eligible | y-revolute supported tray |
| `quick_release_tray` | forked_anchor | quick-release fork | L18-L669 | eligible | dovetail carriage/lock lever visual form |
| `sliding_tray_rails` | forked_anchor | sliding-rail fork | L148-L595 | eligible | x-prismatic tray carriage |

## 槽位图（slot graph）

`body` clamp -> `primary_arm` z-revolute -> `secondary_arm` z-revolute or x-prismatic -> `tray_yoke` y-revolute -> `laptop_tray` y-revolute or x-prismatic. Each upstream endpoint is a visible hub/yoke. Compatibility is candidate locked; folded tray-over-secondary-arm poses are documented transport nesting.

## 每槽位 Module Emits / Interfaces
| slot | emits | joints | interface/source |
|---|---|---|---|
| clamp | `body`, jaws/spindle/column host visuals | none | desk planes and shoulder hub; origins/dual fork |
| reach | `primary_arm`, `secondary_arm` with link/gas/scissor host visuals | revolute + revolute/prismatic | shoulder/elbow hubs; reach sources |
| tray interface | `tray_yoke`, quick-release host details | y-revolute | secondary endpoint; origin/quick fork |
| tray | `laptop_tray`, stop lip/embedded anti-slip strips | y-revolute or x-prismatic | yoke support plane/rail; origin/sliding fork |

## 参数范围汇总
| 参数 | 类型 | 范围 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 8 confirmed | serial arm A | choice | deterministic RNG | pool |
| module enums | enum | tables | derived | equation | candidate compatibility | source map |
| `primary_reach` | float | [0.24,0.50] | 0.34 | independent | clamp | sources |
| `secondary_reach` | float | [0.20,0.44] | 0.30 | independent | clamp | sources |
| `tray_width` | float | [0.34,0.54] | 0.42 | independent | yoke remains centered | tray sources |
| `tray_depth` | float | [0.23,0.39] | 0.30 | independent | front stop derived | tray sources |
| `slide_travel` | float | [0.05,min(0.17,0.48D)] | 0.11 | conditional | telescoping/sliding candidates | forks |

## compile budget

5-20s per seed; primitive arm/tray geometry.

## Multiplicity / Copy Logic

- No arbitrary N. Dual clamp spindles and three anti-slip strips are semantic/support or host-decoration counts.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 取值 / 理由 |
|---|---|---|
| ① 骨架图 | 有 | serial, telescoping, scissor, dual-base, sliding-tray graphs |
| └ multiplicity | 无 | no arbitrary repeated part family |
| ② 关节类型 | 有 | revolute arm/yoke/tray and prismatic boom/tray |
| ③ 主体形态家族 | 有 | serial/gas/scissor reach and tilt/quick-release/rail tray forms |
| ④ 表面装饰 | 有 | embedded anti-slip strips, vent/lock details as host visuals |
| ⑤ 尺寸/行程 | 有 | ranges above; sampled motion plus targeted four-stage poses; folded transport nesting scoped |
| ⑥ 涂装 | 有 | industrial, painted, slate metal/polymer palettes |

## 采样与覆盖审计

Eight source candidates deterministically resolve legal clamp/reach/tray modules, then continuous scales clamp/derive. No overrides. Sweep 0-35 plus corners and viewer 0-9; every reach/tray family must appear in axis realization.

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 8 | yes | yes | confirmed |
| clamp_module | 2 | yes | no | two honest source-backed topologies |
| reach_module | 4 | yes | yes | source-backed |
| tray_module | 3 | yes | yes | source-backed |

## Validator

- desk clamp, two-stage reach, supported yoke and broad stop-lipped tray always present
- choices match build; travel bounded by tray/reach sizes; sampled collision and targeted mechanism poses
- anti-slip strips embed into final tray surface

## Reject cases

- static stand; VESA-only terminal; forearm pad; floating tray/yoke; unsupported telescoping stage; tray slide exceeds depth; hidden collision waiver unrelated to folded transport.

## 与相邻类别的边界

- Forearm support: excluded because terminal is a broad laptop tray, not a padded cradle.
- Static laptop stand: excluded because desk clamp and articulated reach are mandatory.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | image identity governs legacy label; 8/8 sources read; pipeline and visual QA passed |
