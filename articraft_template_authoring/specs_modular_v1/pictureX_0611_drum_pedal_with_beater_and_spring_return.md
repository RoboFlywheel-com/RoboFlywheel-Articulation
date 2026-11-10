# pictureX_0611_drum_pedal_with_beater_and_spring_return - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_drum_pedal_with_beater_and_spring_return` |
| template path | `agent/templates/pictureX_0611_drum_pedal_with_beater_and_spring_return.py` |
| test path (optional) | inline author tests |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | confirmed origin plus five accepted drive/platform forks; full metadata/prompt/build/tests |
| source_index_policy | torsion-spring and under-board compression forks are blocked and not indexed/adopted |

Sources: origin `rec_picturex_...drum_pedal...001...` L66-L612; `rec_drum_pedal_var_direct_drive_link` L67-L667; `...strap_drive` L102-L700; `...double_chain_drive` L66-L663; `...longboard` L66-L618; `...split_heel_plate` L78-L729.

## 核心身份

Hoop-clamped bass-drum pedal with a hinged footboard, visible drive, rotating beater shaft/head and side extension-spring return. Exclude hi-hat pedals, electronic triggers and loose mallets.

## 槽位 + 候选模块表

### Slot A：drive_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_chain` | origin_anchor | origin | L66-L612 | eligible | one chain row between board/cam |
| `direct_link` | forked_anchor | direct-drive fork | L67-L667 | eligible | rigid link/tab |
| `strap_cam` | forked_anchor | strap fork | L102-L700 | eligible | flexible strap visual and round cam |
| `double_chain` | forked_anchor | double-chain fork | L66-L663 | eligible | paired semantic chain rows |

### Slot B：footboard_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `split_board` | origin_anchor | origin | L66-L612 | eligible | short board/heel arrangement |
| `longboard` | forked_anchor | longboard fork | L66-L618 | eligible | continuous long platform |
| `articulated_heel` | forked_anchor | split-heel fork | L78-L729 | eligible | extra revolute heel plate |

### Slot C：return_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `side_extension_spring` | origin_anchor | all accepted pool | ranges above | eligible for all | visible side spring anchored to frame/beater |
| torsion/compression alternatives | blocked | source-map failure clusters | n/a | ineligible | not force-passed |

## 槽位图（slot graph）

Root `body` carries base, posts, hoop clamp and return spring. Parallel children: `footboard` y-revolute at heel, `beater` y-revolute at bearing bridge, and continuous `hoop_adjuster`; optional `heel_plate` is another y-revolute child. Drive visuals live on the beater/footboard hosts. Footboard/beater extreme combinations are coupled in reality and explicitly sequenced in motion QC.

## 每槽位 Module Emits / Interfaces
| slot | emits | joints | interface/source |
|---|---|---|---|
| frame/return | `body` with base/posts/bearing/clamp/spring | none | ground and hoop face; origin |
| drive | `beater` with rod/head and chain/link/strap host visuals | `body_to_beater` revolute | visible bearing barrel; all drive anchors |
| platform | `footboard`, optional `heel_plate` | revolute board/heel | heel hinge on base; origin/forks |
| hoop | `hoop_adjuster` | continuous z | supported clamp jaw; origin |

## 参数范围汇总
| 参数 | 类型 | 范围 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 6 accepted | single chain | choice | deterministic RNG | pool |
| drive/platform/return | enum | tables | derived | equation | candidate locked; return fixed to accepted mechanism | source map |
| `length` | float | [0.32,0.54] | 0.42 | independent | clamp | sources |
| `width` | float | [0.12,min(0.22,0.48L)] | 0.16 | inequality | stable base/post span | frame |
| `board_angle` | float | [0.28,0.68] rad | 0.48 | independent | feasible pedal envelope | sources |
| `beater_throw` | float | [0.55,1.10] rad | 0.82 | independent | sampled motion guard | sources |

## compile budget

5-20s per seed; low-count primitives and no boolean meshes.

## Multiplicity / Copy Logic

- No arbitrary N. Double-chain uses exactly two semantic rows; traction ribs are host decoration.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 取值 / 理由 |
|---|---|---|
| ① 骨架图 | 有 | normal/longboard/split-heel moving graphs |
| └ multiplicity | 无 | chain-row count is semantic 1/2 form, not arbitrary N |
| ② 关节类型 | 有 | revolute board/beater/heel, continuous hoop screw |
| ③ 主体形态家族 | 有 | chain/link/strap drive and split/longboard platform forms |
| ④ 表面装饰 | 有 | traction ribs and coatings as host visuals |
| ⑤ 尺寸/行程 | 有 | ranges above; sampled motion and targeted board/beater/adjuster poses; coupled drive overlap documented |
| ⑥ 涂装 | 有 | industrial/painted/walnut/slate metal and accent palettes |

## 采样与覆盖审计

Six accepted candidates drive compatible modules. No blocked spring alternative or regression override enters sampling. Sweep 0-35 plus corners; preview 0-9. Finite source vocabulary explains topology saturation below 300.

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 6 | yes | yes | accepted only |
| drive_module | 4 | yes | yes | source-backed |
| footboard_module | 3 | yes | yes | source-backed |
| return_module | 1 | no | no | folded into fixed accepted frame contract; blocked alternatives excluded |

## Validator

- hoop interface, return spring, footboard and beater always visible
- non-fixed input/output motion, sampled collision, targeted press/strike/adjust poses
- blocked torsion/compression mechanisms never sampled

## Reject cases

- no hoop clamp/return/beater; static board; hi-hat/e-trigger drift; unsupported drive row; blocked return fork reintroduced; drive coupling hidden only to pass motion QC.

## 与相邻类别的边界

- Hi-hat pedal: excluded because output is a bass-drum beater.
- Electronic trigger: excluded because mechanical beater and return are mandatory.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 6/6 accepted sources read; two blocked returns excluded; pipeline and visual QA passed |
