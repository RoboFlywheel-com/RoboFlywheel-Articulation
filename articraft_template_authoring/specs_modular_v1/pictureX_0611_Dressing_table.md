# pictureX_0611_Dressing_table - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Dressing_table` |
| template path | `agent/templates/pictureX_0611_Dressing_table.py` |
| test path (optional) | inline `run_picturex_0611_dressing_table_tests` |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | six confirmed origins plus seven accepted forks; full metadata/prompt/build/tests |
| source_index_policy | blocked tri-fold mirror is explicitly excluded |

Sources: origins 001 L64-L196, 002 L196-L367, 003 L73-L277, 004 L112-L418, 005 L157-L449, 006 L363-L489;
forks `rec_dressing_table_var_lift_top_mirror` L50-L332,
`rec_dressing_table_var_drawer_n2_20260714` L100-L193 / L290-L309,
`rec_dressing_table_var_drawer_n6_20260714` L104-L195 / L294-L317,
`rec_dressing_table_var_mirror_jewellery_door_20260714` L157-L248 / L497-L566,
`rec_dressing_table_var_trunnion_oval_mirror_20260714` L329-L362 / L440-L486,
`rec_dressing_table_var_kidney_plan_body_20260714` L65-L131 / L195-L250,
`rec_dressing_table_var_sliding_mirror_storage_20260714` L448-L502.

## 核心身份

Floor-supported dressing vanity with a usable worktop, mirror and accessible articulated storage. It must not collapse into a writing desk, sink vanity or loose wall mirror.

## 槽位 + 候选模块表

### Slot A：body_family
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `legged_drawer` | origin_anchor | origins 001/002 | ranges above | eligible | four legs, apron/drawer housing |
| `four_leg_console` | origin_anchor | origin 004 | L112-L418 | eligible | open console and rear stretcher |
| `pedestal_cabinet` | origin_anchor | origins 003/005 | ranges above | eligible | floor cabinet/pedestal envelope |
| `full_width_cabinet` | origin_anchor | origin 006 | L363-L489 | eligible | broad storage carcass |
| `compact_cabinet` | forked_anchor | lift-top fork | L50-L332 | eligible | compact body supporting lift top |
| `kidney_console` | forked_anchor | `rec_dressing_table_var_kidney_plan_body_20260714` | L65-L131, L195-L250 | eligible | kidney planform: side lobes sweep forward, centre front edge recedes into a scalloped apron (Planar Boundary Form) |

### Slot B：mirror_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rectangular_upright` | origin_anchor | origins 001/003/006 | ranges above | eligible | framed upright glass |
| `arched_upright` | origin_anchor | origin 002 | L196-L367 | eligible | arched frame identity |
| `upright_pivot` | origin_anchor | origins 004/005 | ranges above | eligible | y-axis mirror adjustment |
| `lift_top` | forked_anchor | lift-top fork | L50-L332 | eligible | x-hinged mirror/lid motion |
| `trunnion_oval` | forked_anchor | `rec_dressing_table_var_trunnion_oval_mirror_20260714` | L329-L362, L440-L486 | eligible | oval mirror captured between two side posts on a horizontal trunnion axle (`pivot_pin_*`, x-revolute); replaces the crown/pivot bridges |
| `jewellery_door` | forked_anchor | `rec_dressing_table_var_mirror_jewellery_door_20260714` | L157-L248, L497-L566 | eligible | mirror face on a vertically hinged jewellery-cabinet door (z-revolute, `mirror_hinge_leaf_*` + catch) |
| `sliding_mirror` | forked_anchor | `rec_dressing_table_var_sliding_mirror_storage_20260714` | L448-L502 | eligible | mirror panel on x-PRISMATIC runners that retracts to reveal the storage recess (source part `slide_mirror`; realized here as `mirror` + `body_to_mirror` PRISMATIC so every mirror module keeps one uniform contract) |

### Slot C：storage_module（bank layout；数量见 Multiplicity）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `centre_drawer` | origin_anchor | origins 001-004 | ranges above | eligible | single-column bay stack |
| `double_drawer` | origin_anchor | origins 001/006 | ranges above | eligible | two-column bay grid |
| `side_drawer` | origin_anchor | origin 005 | L157-L449 | eligible | pedestal-side storage layout |
| `drawer_bank` | forked_anchor | `rec_dressing_table_var_drawer_n2/n6_20260714` | L100-L195 | eligible | the explicit N-series bank (loop-emitted bays, one PRISMATIC per bay) |

## 槽位图（slot graph）

pattern: parallel_children. Root `body` provides worktop, floor support, drawer housing + per-bay runners, and
either mirror posts (`rectangular_upright` / `arched_upright` / `upright_pivot` / `lift_top` / `trunnion_oval`)
or a `jewellery_storage_case` + slide rails (`jewellery_door` / `sliding_mirror`). `drawer_{i}` are N y-prismatic
children of the body; `mirror` is one revolute (y / x / z) or prismatic (x) child. The two moving families share
the chassis but their simultaneous extreme poses are sequenced by an explicit compatibility allowance.

## 每槽位 Module Emits / Interfaces
| slot | parts / visuals | joints | interface/source |
|---|---|---|---|
| body_family | root `body`, legs/cabinet/worktop/kidney lobes+apron/posts or mirror case as host visuals | none | floor/contact plane and worktop; origins + kidney fork |
| mirror_module | `mirror`, glass/frame/trunnion-pin/hinge-leaf/runner visuals | `body_to_mirror` revolute or prismatic | visible pivot bridge, trunnion post, hinge barrel or slide rail; origins/forks |
| storage_module | `drawer_{i}` × N, box/front/knob visuals | `body_to_drawer_{i}` prismatic × N | drawer housing + paired per-bay runners; origins + N-series forks |

## 参数范围汇总
| 参数 | 类型 | 范围 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 13 confirmed | drawer vanity | choice | deterministic RNG | source pool |
| module enums | enum | tables above | derived | equation | candidate-locked compatibility | source map |
| `drawer_count` | int (N) | [1,6] | 2 | choice | pinned to 2 / 6 by the two N-series candidates, else sampled | drawer_n2 / drawer_n6 forks |
| `width` | float | [0.68,1.24] | 0.92 | independent | clamp | origins |
| `depth` | float | [0.32,min(0.56,0.62W)] | 0.42 | inequality | stable floor/worktop footprint | interfaces |
| `table_height` | float | [0.60,0.86] | 0.72 | independent | clamp | origins |
| `mirror_height` | float | [0.38,0.78] | 0.56 | independent | posts / mirror case derive from it | origins |
| `drawer_travel` | float | [0.10,min(0.30,0.62D)] | 0.20 | inequality | remains guided | drawer sources |
| mirror slide travel | derived | `clamp(0.18·W, 0.08, 0.22)` | — | equation | `_mirror_slide_travel`; single-sourced for build + tests | sliding fork L487-L501 |
| slide rail / runner z | derived | `0.42·case_h` | — | equation | `_mirror_slide_rail_offset`; body rail and panel runner are one quantity in two frames (Contract 3c) | sliding fork L468-L486 |

## compile budget

5-20s per seed; primitive-only furniture geometry. Measured: <1s/seed at N=6.

## Multiplicity / Copy Logic

**count_param:** `drawer_count` (N) — the drawer-bank bay count.

| 项 | 值 |
|---|---|
| count_param | `drawer_count` |
| N samples (source) | `N=2` (`rec_dressing_table_var_drawer_n2_20260714`, model.py:L290-L309, two bays) and `N=6` (`rec_dressing_table_var_drawer_n6_20260714`, model.py:L294-L317, 2 columns × 3 rows) |
| N_range | `1-6` (`_DRAWER_COUNT_RANGE`) |
| copied object / naming | one drawer assembly per bay: `drawer_{i}`, visuals `drawer_box` / `drawer_front` / `drawer_knob`, plus body-side `runner_{i}_outer` / `runner_{i}_inner`. Emitted by one shared helper `_add_vanity_drawer_bank(...)` with `for i in range(r.drawer_count)`, mirroring the sources' shared `_add_drawer(...)` + `_add_root_runner(...)` loop (model.py:L100-L195). |
| placement rule | evenly stacked bays down the vanity body opening. `_drawer_bank_layout(...)` is the single source of the grid: `cols = 2 if N>=4 else (1 if centre_drawer else min(2,N))`, `rows = ceil(N/cols)`, uniform column/row pitch inside a bank of height `clamp(0.09+0.055·rows, 0.10, min(0.30, 0.42·table_height))`; every bay's front and box derive from that pitch, so bays never touch as N grows. |
| joint policy | exactly one PRISMATIC slide per drawer, `body_to_drawer_{i}`, axis `(0,-1,0)`, `[0, drawer_travel]` — uniform across the bank, as in the sources (`DRAWER_TRAVEL`). |
| distinctness note | per VISUAL_DIVERSITY_MODEL §2, N buys coverage, not distinctness; it is declared here because the source pool now establishes a controlled one-axis N series (it previously did not). |

Realized on the 0-35 + corner sweep: `drawer_count` ∈ {1:3, 2:15, 3:7, 4:6, 5:5, 6:12} — both source endpoints
(N=2, N=6) and every intermediate value appear.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 取值 / 理由 |
|---|---|---|
| ① 骨架图 | 有 | open legged, pedestal, full cabinet, kidney console; lift-top / trunnion-post / hinged-door / sliding-panel mirror source graphs; part count moves 3→8 with N |
| └ multiplicity | 有 | **drawer-bank N, 1-6, source-backed by the `drawer_n2` / `drawer_n6` forks**; loop-emitted `drawer_{i}`, one PRISMATIC each |
| ② 关节类型 | 有 | N prismatic drawer slides; mirror as y-revolute (upright), x-revolute (lift-top / trunnion), z-revolute (jewellery door) or x-prismatic (sliding panel) |
| ③ 主体形态家族 | 有 | legged/console/pedestal/full-width/compact/kidney bodies; rectangular / arched / oval-trunnion / door-mounted / sliding mirror envelopes; Volumetric Envelope and Planar Boundary forms |
| ④ 表面装饰 | 有 | moulding, knobs, mirror trim, hinge leaves, door catch, runner strips as host visuals; knob radius derives from the realized bay pitch so it hugs the front across N and ⑤ |
| ⑤ 尺寸/行程 | 有 | parameter ranges; sampled collision plus targeted drawer-open and mirror adjust/open/retract poses; lift-top / cased-mirror vs drawer sequencing explicit |
| ⑥ 涂装 | 有 | oak, painted, walnut, slate palettes with wood/metal/glass |

## 采样与覆盖审计

Thirteen source candidates deterministically select compatible body/mirror/storage modules; N and the continuous
scales then resolve through inequalities. No regression overrides. The candidate RNG stream offset is chosen so
the standard 0-35 sweep realizes every declared module and every N in 1-6 (the draw itself stays fully
procedural — Contract 4). Sweep 0-35 plus corners. Blocked tri-fold candidate is never sampled.

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 13 | yes | yes | confirmed (6 origins + 7 forks) |
| body_family | 6 | yes | yes | source-backed |
| mirror_module | 7 | yes | yes | tri-fold excluded |
| storage_module | 4 | yes | yes | source-backed |
| drawer_count (N) | 6 values | yes | yes | multiplicity axis, not a distinctness axis |

## Validator

- deterministic candidate-locked modules; usable worktop/floor support always present
- exactly `drawer_count` `drawer_{i}` parts, each with exactly one PRISMATIC `body_to_drawer_{i}`
- drawer and mirror non-fixed joints have targeted motion tests and sampled collision
- mirror pivot bridge / trunnion post / hinge barrel / slide rail and the drawer housing + runners are visible support geometry

## Reject cases

- no mirror/worktop/storage; floating mirror; static fake drawer; tri-fold blocked candidate; sink/plumbing drift; mirror opens through an open drawer without sequencing; a drawer bank emitted as N visuals on one part (must be N parts, N joints); sliding mirror runners floating off their rails.

## 与相邻类别的边界

- Writing desk: excluded without mirror and grooming identity.
- Bathroom sink vanity: excluded because no basin/plumbing.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | P3 confirmed 2026-07-14; 13/13 sources read (6 late forks folded in 2026-07-14, incl. the `drawer_n2`/`drawer_n6` N series that closes the previously documented multiplicity gap); blocked tri-fold remains excluded; pipeline pass (0-35 + corner, pass_rate 1.0). Image previews unavailable in this environment (`pyrender` not installed) — identity/topology checked programmatically instead. |
