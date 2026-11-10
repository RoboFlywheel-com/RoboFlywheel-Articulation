# Modular Spec - n_joint_revolute_chain

## 元信息
| 项 | 值 |
|---|---|
| slug | `n_joint_revolute_chain` |
| template path | `agent/templates/n_joint_revolute_chain.py` |
| test path (optional) | `tests/agent/test_n_joint_revolute_chain_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：主结构是 serial revolute chain；Slot A 用真实 3-joint / 4-joint 来源表达 N 的拓扑 multiplicity，Slot B/C/D/E 分别替换 root support、link body family、axis family 和 terminal module。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 80 (`threejoint_revolute_chain` 41 + `fourjoint_revolute_chain` 39) |
| read_count | 80 |
| read_scope | all 5-star samples in both source categories: `threejoint_revolute_chain` and `fourjoint_revolute_chain`; read `model.py` / `revision.json` / `record.json` / `prompt.txt` / category metadata |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的真实结构轴：

| 轴 | 观察到的真实结构变体 |
|---|---|
| joint_count | 3 serial REVOLUTE joints; 4 serial REVOLUTE joints; all adopted sources have one grounded root and serial child links |
| root_support | CADQuery pedestal/column; bridge clevis support; desk C-clamp/turret; side cheek plate |
| link_body_family | CADQuery solid hubbed beam; ExtrudeWithHoles open frame/fork; boxed fork with washer/pin stacks; CADQuery alternating side plates; tube/spring boom |
| axis_family | all pitch axes parallel Y; all planar yaw axes parallel Z; mixed yaw root + pitch distal chain |
| terminal | plain end pad/tab; sensor pod; microphone head; rectangular calibration pad |

## 核心身份

`n_joint_revolute_chain` 是一个 grounded serial kinematic chain：一个固定 base/root support 承载 `N` 个连续 REVOLUTE joints，N 目前只从 5 星来源中采样 `{3, 4}`。链条由 `link_0..link_{N-2}` 和 terminal/end-effector 组成，每个活动段通过可见 hinge pin / boss / clevis / plate / hub 与上游连接。核心 identity 是 **serial revolute-only chain**，不是 prismatic-revolute 混合链、不是 parallel linkage、不是 decorative articulated arm。

默认成熟域：机械演示臂、可折叠支架、传感器/麦克风/压板末端的小型 serial arm。模板实现可把 N 作为受控 multiplicity，但初版只允许 `{3,4}`，因为这是已完整读取并采纳的 5 星样本来源范围。

## 槽位 + 候选模块表

### Slot A：joint_count_topology

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| three_revolute_serial | rec_threejoint_revolute_chain_0001 | L119-L186 | eligible if compatible | base + upper_arm + forearm + wrist_pad; exactly 3 REVOLUTE joints (`shoulder`, `elbow`, `wrist`), all axis `(0,-1,0)` |
| four_revolute_serial | rec_fourjoint_revolute_chain_0001 | L111-L243 | eligible if compatible | base + link1..link4 + fixed sensor_pod; 4 serial REVOLUTE joints before terminal; mixed Z root yaw and Y pitch joints |

样本池只覆盖 3 和 4 joint count；因此该 slot 只有 2 个 candidate，但这是目标 slug 的核心 N multiplicity 来源，不用连续参数伪造更多 N。

### Slot B：root_support

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cadquery_pedestal_column | rec_threejoint_revolute_chain_0001 | L52-L67, L119-L125 | eligible if compatible | CADQuery base plate + vertical column + shoulder block + rear rib; root hinge sits at raised shoulder |
| bridge_clevis_support | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L217-L255 | eligible if compatible | bridge base with two posts, top bridge, upper/lower root lugs, visible root pin |
| desk_clamp_turret | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L72-L127 | eligible if compatible | desk edge + clamp spine/jaws/screw/pressure pad + vertical post and turret cap; root yaw support |
| side_cheek_plate | rec_fourjoint_revolute_chain_b52c6dfef1c445eea742a7cbdd912a1e | L140-L167 | eligible if compatible | ExtrudeWithHoles cheek plate + boss ring + pin stack; compact side-mounted root pivot |

### Slot C：link_body_family

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cadquery_solid_hubbed_beam | rec_threejoint_revolute_chain_0001 | L70-L93, L127-L150 | eligible if compatible | CADQuery proximal hub + beam + distal hub + lower stiffener; mesh_from_cadquery required |
| extruded_open_frame_fork | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L23-L85, L128-L203, L263-L295 | eligible if compatible | ExtrudeGeometry / ExtrudeWithHoles open link plate with boss holes, fork cheeks, pin caps, end tab |
| boxed_fork_washer_stack | rec_fourjoint_revolute_chain_0258e457733c46cf8889e372451a929a | L29-L155, L221-L318 | eligible if compatible | Box beam + hub cylinders + distal fork cheeks + washer/cap-screw stacks at hinge pins |
| cadquery_alternating_side_plate | rec_fourjoint_revolute_chain_3694cd7dfa63427f943f702f663653c1 | L64-L113, L150-L176 | eligible if compatible | CADQuery side plates alternating layer side; cut holes/slots, raised bosses, compact end tab |
| tube_spring_boom | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L129-L252 | eligible if compatible | twin tube boom with crossbars, clevis plates, helical springs via `tube_from_spline_points` |

### Slot D：axis_family

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| parallel_pitch_y | rec_threejoint_revolute_chain_0001 | L160-L186 | eligible if compatible | all chain joints axis `(0,-1,0)`; vertical lifting/pitching chain in X-Z plane |
| parallel_yaw_z | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L297-L316 | eligible if compatible | stacked plate chain with all root/mid/distal joints axis `(0,0,1)`; planar yaw folding |
| mixed_root_yaw_then_pitch | rec_fourjoint_revolute_chain_0001 | L180-L235 | eligible if compatible | root joint axis `(0,0,1)`, downstream link joints axis `(0,-1,0)`; deployable arm with yaw base then pitch chain |
| side_plate_pitch_y | rec_fourjoint_revolute_chain_b52c6dfef1c445eea742a7cbdd912a1e | L180-L215 | eligible if compatible | all four joints axis `(0,-1,0)` through alternating side plates and end tab |

### Slot E：terminal_module

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| compact_pad_tab | rec_threejoint_revolute_chain_0001 | L149-L158 | eligible if compatible | wrist/end part with CADQuery wrist body and rectangular pad visual |
| sensor_pod_fixed | rec_fourjoint_revolute_chain_0001 | L67-L72, L170-L178, L236-L243 | eligible if compatible | sensor mast/body/visor/lens as terminal, fixed to last link after 4 revolute joints |
| microphone_head | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L254-L292 | eligible if compatible | microphone body with wrist hub, stem, grille, bands, mount collar |
| rectangular_calibration_pad | rec_fourjoint_revolute_chain_0258e457733c46cf8889e372451a929a | L287-L331 | eligible if compatible | wrist hub + beam + backing lug + rectangular pad plate/rubber face/screws |

## 槽位图（slot graph）

pattern: mixed

```
[Slot B root_support]
  -- joint_0 REVOLUTE axis from Slot D at root pivot / bearing / cheek -->
[Slot C link_body_family instance link_0]
  -- joint_1 REVOLUTE axis from Slot D at link_0 distal interface -->
[Slot C link_body_family instance link_1]
  -- joint_2 REVOLUTE axis from Slot D at link_1 distal interface -->
...
  -- joint_{N-1} REVOLUTE axis from Slot D -->
[Slot E terminal_module]
```

Slot A `joint_count_topology` 派生 `N`：

- `three_revolute_serial` -> N=3, copied moving objects: two intermediate links plus terminal as the third revolute child.
- `four_revolute_serial` -> N=4, copied moving objects: three intermediate links plus terminal as the fourth revolute child, or four moving links plus fixed terminal when the terminal source requires a separate fixed child. Template implementation must keep exported `revolute_joint_count == N`.

接口点位：

- root_support downstream interface: root pivot bearing face / clevis pin / cheek plate boss. Consumer joint: REVOLUTE, axis determined by Slot D.
- link upstream interface: proximal hub/boss/plate hole centered at local origin; must visibly capture root pin or upstream distal pin.
- link downstream interface: distal hub/fork/pin center at `(link_length, 0, layer_offset)`; exposes the next REVOLUTE joint origin.
- terminal upstream interface: pivot hub/boss/plate at local origin; may emit fixed child details only when sourced (e.g. sensor pod source).

Compatibility / derived policies:

- `desk_clamp_turret` requires `mixed_root_yaw_then_pitch` or `parallel_pitch_y` with a visible turret cap; it should not pair with `parallel_yaw_z` unless the implementation adds a real horizontal turntable face.
- `side_cheek_plate` pairs best with `cadquery_alternating_side_plate` or `extruded_open_frame_fork`, because all use thin side plates and captured pins.
- `tube_spring_boom` requires N=3 in initial seed domain, because the source has lower/upper/microphone as 3 moving revolute children; N=4 extension should be reviewer-gated until implemented without inventing unsupported extra spring boom part tree.
- `sensor_pod_fixed` requires N=4 or a reviewer-approved N=3 shortening; default seed domain should pair it with `four_revolute_serial`.

## 每槽位 Module Emits / Interfaces

### Slot A / module three_revolute_serial
| emits | 描述 | 来源 |
|---|---|---|
| parts | root + two link bodies + terminal moving part | S-A1 / L119-L186 |
| internal joints | 3 REVOLUTE joints, serial parent-child order root -> link0 -> link1 -> terminal | S-A1 / L160-L186 |
| upstream interface | none; root is grounded | S-A1 |
| downstream interface | final terminal outgoing face optional, not used by default | S-A1 |

### Slot A / module four_revolute_serial
| emits | 描述 | 来源 |
|---|---|---|
| parts | root + three/four link bodies + terminal or fixed terminal detail | S-A2 / L111-L243 |
| internal joints | 4 REVOLUTE joints; optional fixed terminal child if using source terminal style | S-A2 / L180-L243 |
| upstream interface | none; root is grounded | S-A2 |
| downstream interface | final terminal outgoing face optional | S-A2 |

### Slot B / root_support candidates
| module | parts | downstream interface | 来源 |
|---|---|---|---|
| cadquery_pedestal_column | CADQuery base/column/shoulder/rib mesh | shoulder top hinge line / boss face | S-B1 / L52-L67, L119-L125 |
| bridge_clevis_support | base plate, posts, top bridge, root upper/lower lug, root pin | root clevis pin center, supports captured proximal boss | S-B2 / L217-L255 |
| desk_clamp_turret | desk clamp visuals, vertical post, turret cap | turret cap top / yaw bearing | S-B3 / L72-L127 |
| side_cheek_plate | extruded cheek plate, boss ring, pin stack | side pin axis through cheek boss | S-B4 / L140-L167 |

### Slot C / link_body_family candidates
| module | parts/visuals | upstream/downstream interfaces | 来源 |
|---|---|---|---|
| cadquery_solid_hubbed_beam | mesh_from_cadquery proximal hub + beam + distal hub + stiffener | proximal hub center at local origin; distal hub at link_length | S-C1 / L70-L93 |
| extruded_open_frame_fork | ExtrudeWithHoles center frame, fork cheeks, bridge, pin caps | proximal plate hole; distal fork pin | S-C2 / L23-L85, L128-L203 |
| boxed_fork_washer_stack | cylinder hub + box beam + fork cheeks + side washer stack | proximal hub; distal washer/pin stack | S-C3 / L29-L155 |
| cadquery_alternating_side_plate | CADQuery cut side plate with raised bosses and holes | alternating y-layer proximal/distal bosses | S-C4 / L64-L113 |
| tube_spring_boom | twin tubes, crossbars, clevis plates, helical spring mesh | turret/yaw sleeve at root or clevis crossbar at downstream | S-C5 / L129-L252 |

### Slot D / axis_family candidates
| module | joints | source semantics | 来源 |
|---|---|---|---|
| parallel_pitch_y | all axes `(0,-1,0)`; pitch/lift chain | shoulder/elbow/wrist lift in X-Z plane | S-D1 / L160-L186 |
| parallel_yaw_z | all axes `(0,0,1)`; planar stack | stacked plates rotate in horizontal plane | S-D2 / L297-L316 |
| mixed_root_yaw_then_pitch | root yaw `(0,0,1)`, downstream pitch `(0,-1,0)` | deployable arm yaw at base, pitch through links | S-D3 / L180-L235 |
| side_plate_pitch_y | all axes `(0,-1,0)` with alternating side plates | compact side-plate chain folds in side plane | S-D4 / L180-L215 |

### Slot E / terminal_module candidates
| module | emits | upstream interface | 来源 |
|---|---|---|---|
| compact_pad_tab | wrist body + rectangular pad | proximal hub / wrist joint at local origin | S-E1 / L149-L158 |
| sensor_pod_fixed | sensor mast/body/visor/lens; fixed terminal child when N=4 source style is used | terminal attaches to last link end via fixed support after N revolute joints | S-E2 / L67-L72, L170-L178, L236-L243 |
| microphone_head | wrist hub + microphone cylinder + grille bands | wrist hub in clevis plates | S-E3 / L254-L292 |
| rectangular_calibration_pad | wrist hub + beam + backing lug + rubber pad plate | wrist hub captures outer link distal pin | S-E4 / L287-L331 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| joint_count_topology | enum | three_revolute_serial / four_revolute_serial | sampled | determines `joint_count`, link instance count, terminal placement | Slot A |
| joint_count | int derived | {3, 4} | sampled | from Slot A; no free N beyond sources | S-A1/S-A2 |
| root_support | enum | cadquery_pedestal_column / bridge_clevis_support / desk_clamp_turret / side_cheek_plate | sampled | gated by axis_family and link_body_family | Slot B |
| link_body_family | enum | cadquery_solid_hubbed_beam / extruded_open_frame_fork / boxed_fork_washer_stack / cadquery_alternating_side_plate / tube_spring_boom | sampled | may gate N and axis family | Slot C |
| axis_family | enum | parallel_pitch_y / parallel_yaw_z / mixed_root_yaw_then_pitch / side_plate_pitch_y | sampled | determines per-joint axes and joint ranges | Slot D |
| terminal_module | enum | compact_pad_tab / sensor_pod_fixed / microphone_head / rectangular_calibration_pad | sampled | terminal requires compatible N and axis/clevis support | Slot E |
| link_length_scale | float | [0.82, 1.18] | sampled | scales source link lengths with min clearance | source dimensions |
| link_width_scale | float | [0.85, 1.15] | sampled | scales plate/beam widths | source dimensions |
| hub_radius_scale | float | [0.88, 1.14] | sampled | pin/boss/hub radius, must preserve captured pin fit | source dimensions |
| layer_spacing_scale | float | [0.90, 1.18] | sampled | side plate / fork y or z offsets | S-C2/S-C4 |
| joint_limit_scale | float | [0.75, 1.10] | sampled | clamps REVOLUTE motion limits; rest pose remains legal | S-D |
| terminal_size_scale | float | [0.80, 1.20] | sampled | pad/sensor/mic terminal size | S-E |
| material_style | enum | dark_steel / satin_aluminum / machine_gray / lab_blue / black_boom | sampled | palette only; not topology | all sources |

## Multiplicity / Copy Logic

本类别有核心 multiplicity：`joint_count`。

- count_param：`joint_count`
- N_range：{3, 4}
- sampling domain：`three_revolute_serial` -> 3; `four_revolute_serial` -> 4
- copied object：serial revolute joint instances `joint_0..joint_{N-1}`; intermediate links `link_0..link_{N-2}` plus terminal as final moving child or sourced fixed terminal child
- naming：root part `base` / `root_support`; moving links `link_0`, `link_1`, ...; terminal `terminal` or `end_effector`; joints `joint_0..joint_{N-1}`
- placement：each link instance places upstream interface at local origin and downstream interface at derived `link_length_i`; axis/layer offsets come from Slot D/C
- joint policy：all copied joints are `ArticulationType.REVOLUTE`; axis tuple is derived from `axis_family`; motion limits from source ranges with `joint_limit_scale`
- source/gating：N=3 from rec_threejoint_revolute_chain_0001 L160-L186 and related 3-joint samples; N=4 from rec_fourjoint_revolute_chain_0001 L180-L235 and related 4-joint samples

No other template-level counts are exposed. Module-local repeated elements such as screw heads, grille bands, spring turns, pin caps, or base bolts remain local visuals/helpers and are not counted as topology multiplicity.

## 拓扑多样性审计

总组合数（合法化前）：A(2) × B(4) × C(5) × D(4) × E(4) = 640。


理由：即使 compatibility gating removes roughly half of combinations, N=3/N=4, 4 root supports, 5 link families, 4 axis families, and 4 terminal modules leave far more than 10 distinct slot-choice tuples. N itself changes joint count and part tree, so topology diversity is not just decoration.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：

- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special.
- Sampling order: joint_count_topology -> root_support -> link_body_family -> axis_family -> terminal_module -> controlled local scales -> material_style.
- `resolve_config` applies compatibility matrix and may resample/fallback within implemented eligible candidates, but must expose the final choices through `slot_choices_for_seed`.
- Initial sweep range: seeds 0-49 via `uv run articraft template sweep-pipeline n_joint_revolute_chain`.
- Maturity audit: seeds 0-999, target slot choice tuple distinct ≥300.
- Regression overrides: none in the initial spec; future overrides only for reviewer-selected or failed regression seeds, with explicit reason.

Controlled local parameterization：

- `link_length_scale [0.82,1.18]`: clamp so total reach remains stable and terminal does not collide with root in rest pose.
- `link_width_scale [0.85,1.15]`: clamp by hub/fork clearances.
- `hub_radius_scale [0.88,1.14]`: derive pin radius and MatingContract face extents; child hub must still capture parent pin.
- `layer_spacing_scale [0.90,1.18]`: only for side-plate/fork families; must preserve alternating layer gaps and captured-pin overlap.
- `joint_limit_scale [0.75,1.10]`: limits never exclude rest pose 0; pitch chains avoid folding through base.
- `terminal_size_scale [0.80,1.20]`: terminal stays supported by last link and does not dominate chain identity.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural-first weighted choices; final choices exported exactly | `slot_choices_for_seed` matches built `joint_count`, root, link, axis, terminal |
| compatibility matrix | gate N, axis, root, link, terminal combos before build | no missing terminal, no N mismatch, no unsupported tube_spring N=4, no sensor_pod N=3 unless implemented |
| controlled local variation | clamp length/width/hub/layer/joint/terminal scales in `resolve_config` | proportions vary while pin capture, joint origin, MatingContract, and rest support hold |
| regression overrides | none | only reviewer/failure-driven sparse overrides later |
| random sweep | 0-49 initial, 0-999 maturity | , joint origin, mating gap, unsupported islands, overlap in rest and sampled poses |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| joint_count_topology | 2 | yes | no | only 3/4-joint source categories are in scope |
| root_support | 4 | yes | yes | true support topology differences |
| link_body_family | 5 | yes | yes | primitive/part tree differences |
| axis_family | 4 | yes | yes | joint axis topology differences |
| terminal_module | 4 | yes | yes | terminal part tree/interface differences |

Compatibility matrix / gating：

- `tube_spring_boom` -> only `three_revolute_serial` in initial implementation.
- `sensor_pod_fixed` -> prefer/require `four_revolute_serial` because source has four revolute joints plus fixed sensor pod.
- `desk_clamp_turret` -> require `mixed_root_yaw_then_pitch` or reviewer-approved pitch support; reject `parallel_yaw_z` without a real horizontal turntable mating face.
- `side_cheek_plate` -> require `side_plate_pitch_y`, `parallel_pitch_y`, `cadquery_alternating_side_plate`, or `extruded_open_frame_fork`.
- `parallel_yaw_z` -> require stacked plate/fork link family with explicit layer spacing; do not pair with tall pitch-only pedestal unless a planar bearing deck is built.
- `cadquery_solid_hubbed_beam` and `boxed_fork_washer_stack` are compatible with pitch-y families and bridge/pedestal roots.
- N=4 with any terminal must still expose exactly 4 REVOLUTE joints; fixed terminal details do not count toward N.

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for all five slots.
- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special.
- `resolve_config` derives `joint_count` only from `joint_count_topology` and clamps all local scales.
- Chain emits exactly N REVOLUTE joints named `joint_0..joint_{N-1}`.
- All REVOLUTE joint origins lie on visible hinge pins/bosses/clevises; no joint origin floats in space.
- Every moving child joint has a MatingContract between real parent/child faces: pin/boss, clevis/hub, cheek/plate, or turret/sleeve.
- Captured pins use element-scoped allow_overlap only for real pin-through-bore relationships.
- Link primitive family is preserved: CADQuery sources stay mesh_from_cadquery; ExtrudeWithHoles sources stay mesh_from_geometry/ExtrudeWithHolesGeometry; tube spring sources keep tube_from_spline_points.
- Terminal source semantics are preserved: sensor/microphone/pad terminals keep their sourced part tree and interface support.
- Rest pose is an extended serial chain with all links visibly supported; sampled posed chain folds without base collision or unsupported terminal.

## Reject cases

- Any sampled build has joint_count not equal to 3 or 4.
- A template uses continuous length parameters to imply N>4 without source-backed joints.
- A moving child lacks a REVOLUTE joint or has a non-source axis.
- A terminal floats at the end of the chain or is connected only by a phantom disk.
- CADQuery / ExtrudeWithHoles / tube-spring source modules are downgraded to crude Box-only placeholders.
- `tube_spring_boom` is sampled for N=4 without an implemented source-backed fourth revolute segment.
- `sensor_pod_fixed` is sampled for N=3 and silently drops/renames a revolute joint.
- Pin/boss overlaps are globally allowed instead of element-scoped captured-pin exceptions.
- Root support and axis family mismatch creates a yaw joint on a pitch-only clevis or a pitch joint on an unsupported flat plate.
- Rest pose or sampled pose makes terminal collide with base/root support.

## 与相邻类别的边界

- 不该混入：`twojoint_revolute_chain`（N=2 only; this template is N in {3,4} from three/four-joint sources).
- 不该混入：`threejoint_prismatic_chain` / `twojoint_prismatic_chain`（contains PRISMATIC joints; this spec is revolute-only).
- 不该混入：`prismaticrevolute_chain` and mixed prismatic/revolute chain categories（mixed joint type, different identity).
- 不该混入：`robotic_arms` / `articulated_task_lamp` as object categories（they may share kinematics but have domain-specific head/base semantics beyond generic revolute chain).
- 不该混入：parallel four-bar linkages or pantographs（not a single serial chain).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Built from all 80 five-star samples across `threejoint_revolute_chain` and `fourjoint_revolute_chain`; adopted source table only includes clear serial REVOLUTE structures with traceable part tree, joint axes, primitive complexity, and interfaces. Waiting for review before template implementation. |

## 模板实现备注（可选）

- Use `joint_count_topology` as the only template-level multiplicity gate; do not expose arbitrary N until new 5-star source categories are added.
- Implement link family factories as repeatable modules consuming `index`, `link_length_i`, `axis_family`, and `layer_offset_i`; keep source primitive family.
- MatingContract focus: root pin -> first link proximal hub; link_i distal pin/boss -> link_{i+1} proximal hub; final link -> terminal proximal hub.
- Element-scoped allow_overlap needed for captured pins through bosses/plates and for clevis cheek clearances where sources intentionally sandwich hubs.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | joint_count_topology | three_revolute_serial | rec_threejoint_revolute_chain_0001 | L119-L186 | 3 REVOLUTE chain part/joint topology |
| S-A2 | joint_count_topology | four_revolute_serial | rec_fourjoint_revolute_chain_0001 | L111-L243 | 4 REVOLUTE chain + fixed terminal style |
| S-B1 | root_support | cadquery_pedestal_column | rec_threejoint_revolute_chain_0001 | L52-L67, L119-L125 | CADQuery pedestal/root support |
| S-B2 | root_support | bridge_clevis_support | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L217-L255 | bridge clevis + root pin |
| S-B3 | root_support | desk_clamp_turret | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L72-L127 | clamp/turret support |
| S-B4 | root_support | side_cheek_plate | rec_fourjoint_revolute_chain_b52c6dfef1c445eea742a7cbdd912a1e | L140-L167 | side cheek plate root support |
| S-C1 | link_body_family | cadquery_solid_hubbed_beam | rec_threejoint_revolute_chain_0001 | L70-L93, L127-L150 | CADQuery hubbed link bodies |
| S-C2 | link_body_family | extruded_open_frame_fork | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L23-L85, L128-L203, L263-L295 | open frame/fork link bodies |
| S-C3 | link_body_family | boxed_fork_washer_stack | rec_fourjoint_revolute_chain_0258e457733c46cf8889e372451a929a | L29-L155, L221-L318 | boxed fork + washer stack links |
| S-C4 | link_body_family | cadquery_alternating_side_plate | rec_fourjoint_revolute_chain_3694cd7dfa63427f943f702f663653c1 | L64-L113, L150-L176 | CADQuery alternating side plates |
| S-C5 | link_body_family | tube_spring_boom | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L129-L252 | tube/spring boom link family |
| S-D1 | axis_family | parallel_pitch_y | rec_threejoint_revolute_chain_0001 | L160-L186 | all Y pitch axes |
| S-D2 | axis_family | parallel_yaw_z | rec_threejoint_revolute_chain_078f206087c840a5a8bb5a9d17058739 | L297-L316 | planar Z yaw axes |
| S-D3 | axis_family | mixed_root_yaw_then_pitch | rec_fourjoint_revolute_chain_0001 | L180-L235 | root Z yaw + downstream Y pitch |
| S-D4 | axis_family | side_plate_pitch_y | rec_fourjoint_revolute_chain_b52c6dfef1c445eea742a7cbdd912a1e | L180-L215 | side-plate Y pitch axes |
| S-E1 | terminal_module | compact_pad_tab | rec_threejoint_revolute_chain_0001 | L149-L158 | wrist pad terminal |
| S-E2 | terminal_module | sensor_pod_fixed | rec_fourjoint_revolute_chain_0001 | L67-L72, L170-L178, L236-L243 | fixed sensor pod terminal |
| S-E3 | terminal_module | microphone_head | rec_threejoint_revolute_chain_7ef3c1c443cd4565b4974afb584b1dc3 | L254-L292 | microphone terminal |
| S-E4 | terminal_module | rectangular_calibration_pad | rec_fourjoint_revolute_chain_0258e457733c46cf8889e372451a929a | L287-L331 | calibration pad terminal |
