# Blender Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `blender` |
| template path | `agent/templates/blender.py` |
| test path | `tests/agent/test_blender_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 46 |
| read_count | 46 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
电动搅拌/料理设备，至少包含 motor base/body、容器或手持 shaft、可旋转 blade/tool，以及可选 lid/cap/control。核心运动是 blade/tool 绕竖直或 shaft 轴连续旋转，部分样本还包含 jug twist-lock、lid hinge、cap press、trigger/dial 等辅助关节。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_blender_b5de179e8b984fe793430409008bf897 | `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L117-L350` | countertop jug blender: motor base, clear pitcher, handle, lid, center cap, dial and blade spin |
| S2 | rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562 | `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L45-L326` | commercial sound-enclosure blender: base, jar, blade assembly, hinged noise hood |
| S3 | rec_blender_f8cf6dc9c409425aaa7bee101674500b | `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L152-L260` | immersion blender: motor handle, detachable shaft, blade rotor, power trigger |
| S4 | rec_blender_f513f69f35204dab87e58687d44fb722 | `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L89-L322` | personal/single-serve blender: compact base, threaded cup, blade assembly and flip-spout lid |
| S5 | rec_blender_9ab7f5088ee24cbf967fe44e7722dc87 | `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L33-L270` | vacuum blender: round base, jug twist lock, suction connector cap, cap press and front dial |
| S6 | rec_blender_d764a1f50a04442fb4f7f90cbe69584e | `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L55-L419` | commercial bar blender with hinged lid, safety latch, button panel and blade rotor |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| motor_base | 台式/个人/商用 blender 的固定底座，含 drive coupling、control panel、feet | blender_layout: enum, base_shape: enum, base_width/depth/height: float | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L117-L136`; S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L45-L92`; S4 / `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L89-L146`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L33-L77`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L55-L138` |
| pitcher_or_jar | 台式 blender 的容器，含透明壁、collar、rim、handle、spout | jar_shape: enum, jar_height: float, jar_profile: enum, handle_style: enum | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L137-L212`; S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L94-L214`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L78-L152`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L139-L233` |
| bottle_or_cup | personal/travel blender 的 compact cup/bottle | cup_style: enum, cup_height: float, flip_lid_enabled: bool | S4 / `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L147-L322` |
| motor_handle | immersion blender 手柄/电机壳 | handle_profile: enum, trigger_style: enum | S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L152-L168` |
| shaft_assembly | immersion blender 可拆 shaft 和 bell guard | shaft_length: float, guard_style: enum, shaft_lock_style: enum | S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L169-L185` |
| blade_assembly | 可旋转 blade/tool；台式在 jar/base 底部，immersion 在 shaft tip | blade_style: enum, blade_count: int, blade_radius: float | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L295-L350`; S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L215-L245`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L186-L201`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L295-L337` |
| lid | pitcher/jar/cup 顶盖，可 fixed、hinged 或带 removable center cap | lid_style: enum, lid_motion: enum | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L213-L262`; S4 / `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L279-L322`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L234-L294` |
| center_cap / connector_cap | 可选中心盖、真空连接盖或 press cap | cap_style: enum, cap_motion: enum | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L263-L268`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L179-L216` |
| dial_or_controls | 旋钮、按钮、trigger 或 rocker；可为 visual 或可动 part | control_style: enum, control_motion: enum | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L270-L294`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L202-L260`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L83-L112` |
| noise_hood | 商用隔音罩，可选 hinged polycarbonate enclosure | hood_enabled: bool, hood_style: enum, hood_open_angle: float | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L246-L326` |
| safety_latch | 商用 blender 可选安全锁扣 | safety_latch_enabled: bool, latch_style: enum | S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L338-L419` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| blade_spin | continuous or revolute | usually `(0, 0, 1)`; immersion may use shaft axis `(0, 0, -1)` | blade hub / drive shaft axis | continuous or full `[-tau, tau]` / `[0, tau]` | blade/tool rotates inside jar/cup/guard | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L341-L350`; S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L303-L312`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L235-L245`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L390-L404` |
| jar_twist_lock | revolute | `(0, 0, 1)` | base coupling / jar collar center | about `[-0.40, 0.55]` | jar/cup twist-locks onto base | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L289-L302`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L235-L243` |
| lid_hinge | revolute | horizontal hinge axis `(1, 0, 0)` or `(-1, 0, 0)` | jar rim/lid rear edge | `[0, 1.7-1.9]` | hinged lid or flip-spout lid opens from jar/cup | S4 / `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L279-L322`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L376-L389` |
| center_cap_twist | revolute | `(0, 0, 1)` | lid center | `[0, 0.45]` | removable center cap twist | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L323-L331` |
| connector_cap_press | prismatic | `(0, 0, -1)` or `(0, 0, 1)` | jug top mouth | `[0, 0.012-0.018]` | vacuum connector/seal cap presses into jar mouth | S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L253-L262` |
| hood_hinge | revolute | horizontal rear hinge axis `(0, -1, 0)` or equivalent | base rear hinge rail | `[0, 1.25]` approx | commercial sound hood opens | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L312-L326` |
| shaft_lock | revolute | shaft axis `(0, 0, 1)` | motor handle lower coupling | `[0, 0.45]` or quarter-turn | immersion shaft locks into handle | S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L220-L234` |
| trigger_or_dial | revolute / continuous / prismatic | front face or trigger hinge axis | mounted on base/handle face | small rocker `[−0.3,0.3]`, trigger `[0,0.35]`, dial continuous | user control motion | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L332-L340`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L245-L260`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L262-L270` |
| safety_latch_hinge | revolute | horizontal latch axis | front latch mount | `[0, 1.05]` | commercial safety latch flips | S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L404-L419` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| blender_layout | enum | `countertop_jug` / `personal_cup` / `immersion_wand` / `commercial_hood` / `vacuum_jug` / `bar_blender` | `countertop_jug` | Determines main part tree and allowed joints | S1-S6 |
| base_shape | enum | `rectangular` / `round_disc` / `tapered_commercial` / `none_for_immersion` | `rectangular` | constrained by `blender_layout` | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L117-L136`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L33-L77`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L55-L138` |
| jar_shape | enum | `square_pitcher` / `cylindrical_jug` / `rounded_rect_jar` / `inverted_cup` / `none` | `square_pitcher` | `none` only for immersion layout | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L137-L212`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L78-L152`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L139-L233` |
| blade_style | enum | `two_blade_cross` / `four_blade_cross` / `six_blade_stack` / `immersion_blade_set` / `beater_tool` | `four_blade_cross` | controls blade visuals and sweep radius | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L295-L350`; S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L215-L245`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L186-L201`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L295-L337` |
| jar_lock_motion | enum | `fixed` / `twist_lock` | `fixed` | twist creates `jar_twist_lock` revolute | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L289-L302`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L235-L243` |
| lid_style | enum | `flat_lid` / `center_cap_lid` / `flip_spout` / `hinged_shield` / `vacuum_cap` / `none` | `center_cap_lid` | selects lid/cap parts and joints | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L213-L331`; S4 / `data/records/rec_blender_f513f69f35204dab87e58687d44fb722/revisions/rev_000001/model.py:L279-L322`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L179-L262`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L234-L294` |
| control_style | enum | `dial` / `button_panel` / `rocker` / `trigger` / `none` | `dial` | determines control part/joint or visual buttons | S1 / `data/records/rec_blender_b5de179e8b984fe793430409008bf897/revisions/rev_000001/model.py:L270-L340`; S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L202-L260`; S6 / `data/records/rec_blender_d764a1f50a04442fb4f7f90cbe69584e/revisions/rev_000001/model.py:L83-L112` |
| hood_enabled | bool | `true / false` | `false` | true only for commercial layouts; creates `noise_hood` and `hood_hinge` | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L246-L326` |
| shaft_lock_style | enum | `none` / `quarter_turn` / `press_and_twist` | `none` | immersion layout uses shaft lock joint | S3 / `data/records/rec_blender_f8cf6dc9c409425aaa7bee101674500b/revisions/rev_000001/model.py:L152-L260` |
| blade_spin_speed_class | enum | `slow_display` / `normal` / `high_speed` | `high_speed` | maps to velocity metadata only | S2 / `data/records/rec_blender_c6e4b2a3ed7845b4b55b56097a4b6562/revisions/rev_000001/model.py:L303-L312`; S5 / `data/records/rec_blender_9ab7f5088ee24cbf967fe44e7722dc87/revisions/rev_000001/model.py:L244-L252` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| overall layout | countertop jug / personal cup / immersion wand / commercial hood / vacuum jug / bar blender | no | yes | blender_layout | 46 个样本中存在台式、手持、商用罩、真空盖等拓扑差异 |
| base/body | rectangular motor base / round disc / tapered commercial housing / cylindrical handle | no | yes | base_shape, handle_profile | 手持与台式不是尺度差异 |
| container | square pitcher / cylindrical jug / inverted cup / none for immersion | no | yes | jar_shape, cup_style | 容器形态决定 handle/lid/blade placement |
| blade/tool | two/four/six cross blades / immersion blade set / beater-like tool | no | yes | blade_style | blade count and guard relation are qualitative |
| lid/cap | fixed lid / center cap / hinged lid / flip spout / vacuum press cap | no | yes | lid_style, cap_style | lid motion and seal topology vary |
| controls | dial / button panel / trigger / rocker / none | no | yes | control_style, control_motion | controls appear in different locations and joint types |
| noise hood/safety latch | none / hinged clear hood / hinged latch | no | yes | hood_enabled, safety_latch_enabled | commercial samples include enclosure and latch not expressible by size |
| jar handle | none / side handle / bridge handle | no | yes | handle_style | handle topology varies by jar/cup layout |

## 组合逻辑（Composition Logic）
1. Choose `blender_layout`; countertop/personal/commercial/vacuum build around `motor_base`, immersion builds around `motor_handle`.
2. For jar/cup layouts, place container centered on base coupling; choose fixed or twist-lock joint via `jar_lock_motion`.
3. Place blade/tool on container floor, base coupling, or shaft tip, and create exactly one primary `blade_spin` joint.
4. Build lid/cap according to `lid_style`; hinged and press/twist caps create their own joints, fixed lids do not.
5. Commercial layouts may add `noise_hood` and `safety_latch`; immersion layouts may add `shaft_lock` and trigger.
6. Buttons, scales, vents, feet and nonmoving trims are visual children of base/jar/handle.

## 已有模板写法参考
continuous_rotor / revolute_hinge / button_slider / handle_grip / gasket_strip

## 约束
- Every generated blender must include a rotating blade/tool joint.
- Blade sweep must stay inside jar/cup/bell guard footprint.
- Jar/cup must be seated on base coupling unless `blender_layout = immersion_wand`.
- Immersion shaft must remain coaxial with handle coupling and blade guard.
- Lid/cap must cover or insert into the container mouth when closed.
- Hood/latch/control parts must be visibly mounted and not floating.
- Do not generate a stand mixer unless explicitly selected as a reviewed extension; the default template should prefer blender identities above.

## Validator
| 检查项 | 标准 |
|---|---|
| blade joint | exactly one primary continuous/revolute blade spin joint |
| axis check | blade axis aligned with jar/shaft axis |
| containment | blade sweep inside jar/cup/guard footprint |
| container seating | jar/cup seated on base or shaft seated in handle |
| lid/cap consistency | selected lid/cap style creates expected fixed/revolute/prismatic joint |
| hood/latch consistency | hood/latch parameters match part and joint counts |
| controls | moving controls have appropriate axis and are mounted on base/handle |
| part diversity | `blender_layout`, `jar_shape`, `blade_style`, `lid_style`, `control_style` exist |
| identity | recognizable blender/immersion blender rather than generic cup or stand mixer |

## Reject cases
- No blade/tool spin joint.
- Blade floats outside the jar/cup/guard.
- Jar is not seated on the base coupling.
- Lid or cap hovers above the container without contact.
- Immersion shaft is disconnected from handle.
- Commercial hood opens around nothing or intersects jar severely.
- Selected layout collapses to the same geometry with only color changes.
- Model reads as stand mixer/food processor by default without blender-specific blade/container relation.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
