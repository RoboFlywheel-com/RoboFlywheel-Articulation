# Turnstile Gates Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `turnstile_gates` |
| template path | `agent/templates/turnstile_gates.py` |
| test path | `tests/agent/test_turnstile_gates_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 45 |
| read_count | 45 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / `prompt.txt` were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 39 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| central post/frame + radial arm rotor | 36 | fixed frame/support -> rotor CONTINUOUS about vertical axis |
| service-heavy central turnstile | 4 | base/bearing/wear rings/service panel as fixed/hinged subparts |
| premium split head / modules | 2 | base + bearing_module + fixed_frame + head modules + arm hub |
| lockout pawl / safety mechanism | 1 | rotor REVOLUTE/CONTINUOUS plus pawl REVOLUTE |
| swinging glass gate pair | 1 | left/right cabinets with opposing REVOLUTE gate leaves; accepted sample but topology differs strongly |
| inspection/service hatches | 3 | service panel and inspection hatch REVOLUTE on fixed base/frame |

被采纳样本逐条标注：
- `rec_turnstile_gates_0002` — adopted：rugged base_frame, rotor_assembly, service_panel, inspection_hatch, continuous central rotor。
- `rec_turnstile_gates_0003` — adopted：refined frame + rotor, simple seed-0 continuous three-arm turnstile。
- `rec_turnstile_gates_263530aa5ac54fec861233a7d86aa8c4` — adopted：service workhorse base, bearing_core, wear rings, rotor。
- `rec_turnstile_gates_76346937a9f345e2b518432844044a83` — adopted：base + bearing_module + fixed_frame + head modules + arm_hub。
- `rec_turnstile_gates_7b8754ba455e44da91b04ad418caad73` — adopted：industrial frame, rotor, lockout_pawl second REVOLUTE。
- `rec_turnstile_gates_e615c706540b431592c7295a69ffa83e` — adopted：dual cabinet swinging glass gate pair; flagged as broad-family candidate, likely review decision for split/optional module。
- Remaining 39 samples — read but not adopted: repeat central post/rotor families or only vary material, frame trim, weather hood, CAD helper, arm shape, or axis sign.

## 核心身份
`turnstile_gates` 是通道入口处控制单人通过的 gate mechanism。默认成熟域是 fixed frame/base/support 与 central rotor/arm hub，rotor 绕竖直轴 CONTINUOUS 或 limited REVOLUTE 旋转，带 3 个或更多 radial arms/bars/paddles。可选 service panel、inspection hatch、bearing modules、lockout pawl 提供维护/锁止细节。全高 swing/glass gate pair 在 5 星样本中存在，但与 central radial turnstile 的主运动 spine 不兼容，建议审核时决定是否拆成子 slug 或作为 gated alternate。

边界：
- 不包括普通双开门/闸门：必须有 turnstile access-control identity。
- 不混入 revolving door：turnstile 的 barrier arms/gates 是通行阻挡件，不是完整门翼围成旋转门舱。
- 不混入 barrier gate：没有横杆抬起的车辆道闸语义。
- 如果采用 swing glass gate pair，必须明确是 turnstile gate lane variant，不得让默认模板丢失 central rotor identity。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_turnstile_gates_0002` | `data/records/rec_turnstile_gates_0002/revisions/rev_000001/model.py:L24-L506` | rugged frame, rotor assembly, service panel and inspection hatch joints |
| S2 | `rec_turnstile_gates_0003` | `data/records/rec_turnstile_gates_0003/revisions/rev_000001/model.py:L27-L339` | simple refined frame + rotor seed topology |
| S3 | `rec_turnstile_gates_263530aa5ac54fec861233a7d86aa8c4` | `data/records/rec_turnstile_gates_263530aa5ac54fec861233a7d86aa8c4/revisions/rev_000001/model.py:L23-L38,L47-L382` | service base, bearing_core, wear rings, fixed subpart stack, rotor CONTINUOUS |
| S4 | `rec_turnstile_gates_76346937a9f345e2b518432844044a83` | `data/records/rec_turnstile_gates_76346937a9f345e2b518432844044a83/revisions/rev_000001/model.py:L21-L247` | split bearing module + fixed frame + head modules + arm_hub topology |
| S5 | `rec_turnstile_gates_7b8754ba455e44da91b04ad418caad73` | `data/records/rec_turnstile_gates_7b8754ba455e44da91b04ad418caad73/revisions/rev_000001/model.py:L22-L57,L68-L406` | industrial safety frame, radial rotor, lockout pawl REVOLUTE |
| S6 | `rec_turnstile_gates_e615c706540b431592c7295a69ffa83e` | `data/records/rec_turnstile_gates_e615c706540b431592c7295a69ffa83e/revisions/rev_000001/model.py:L15-L27,L39-L211` | dual cabinet swing gate alternate; review-gated because topology differs from central rotor |

## 槽位 + 候选模块表

### Slot A：fixed_support_lane
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `refined_frame` | S2 | `model.py:L154-L245` | eligible if compatible | compact frame/rails around central rotor |
| `rugged_base_frame` | S1 | `model.py:L92-L225` | eligible if compatible | heavy utility frame with panels and hatches |
| `service_bearing_base` | S3 | `model.py:L47-L197` | eligible if compatible | base plus bearing_core and service_door/wear rings |
| `split_head_lane` | S4 | `model.py:L30-L153` | eligible if compatible | base + bearing_module + fixed_frame + left/right head modules |
| `dual_cabinet_glass_lane` | S6 | `model.py:L39-L142` | eligible if compatible | left/right cabinet pair, no central rotor; review-gated alternate |

### Slot B：barrier_mechanism
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `three_arm_rotor` | S2 | `model.py:L270-L339` | eligible if compatible | central rotor with three radial arms, CONTINUOUS Z axis |
| `rugged_rotor_assembly` | S1 | `model.py:L293-L506` | eligible if compatible | heavy rotor with caps/arms plus service/inspection hatches |
| `bearing_hub_rotor` | S3 | `model.py:L284-L382` | eligible if compatible | rotor rides fixed bearing stack/wear rings |
| `modular_arm_hub` | S4 | `model.py:L165-L247` | eligible if compatible | arm_hub parented to bearing_module |
| `dual_swing_glass_gates` | S6 | `model.py:L150-L195` | eligible if compatible | opposing left/right gate leaves with REVOLUTE hinges |

### Slot C：service_and_locking
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | S2 | `model.py:L333-L339` | eligible if compatible | only rotor joint |
| `service_panel_and_hatch` | S1 | `model.py:L437-L529` | eligible if compatible | service panel vertical hinge + inspection hatch horizontal hinge |
| `fixed_bearing_service_stack` | S3 | `model.py:L154-L376` | eligible if compatible | service door fixed, bearing_core and wear rings fixed |
| `lockout_pawl` | S5 | `model.py:L364-L406` | eligible if compatible | pawl part with REVOLUTE lockout motion |

## 槽位图（slot graph）
pattern = `mixed`

Default central-rotor domain:

```
[Slot A fixed_support_lane]
      ├── CONTINUOUS/REVOLUTE, axis (0,0,1) --> [Slot B radial rotor / arm hub]
      └── optional REVOLUTE/FIXED --> [Slot C service panel / hatch / pawl / bearing stack]
```

Review-gated swing-gate alternate:

```
[base] -- FIXED --> [left_cabinet] -- REVOLUTE Z --> [left_gate]
       -- FIXED --> [right_cabinet] -- REVOLUTE -Z --> [right_gate]
```

The default template should likely seed central rotor. The dual swing gate branch should be either split or heavily gated after review.

## 部件（Parts）

### Slot A / fixed_support_lane
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `frame` / `base_frame` / `base` / `fixed_frame` | ~8-40 | fixed lane/root with rails, cabinets, bearing support or service housing | S1-S5 |
| `left_cabinet` / `right_cabinet` | ~8 each | dual swing gate lane cabinets | S6 |
| `bearing_core` / `bearing_module` / `wear_ring_*` | ~2-6 | fixed bearing subparts | S3 / S4 |

### Slot B / barrier_mechanism
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `rotor` / `rotor_assembly` / `arm_hub` | ~4-24 | central rotating hub with radial arms/bars | S1-S5 |
| `left_gate` / `right_gate` | ~2 each | swing glass leaf alternate | S6 |

### Slot C / service_and_locking
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `service_panel` | ~3 | hinged service panel on base/frame | S1 |
| `inspection_hatch` | ~4 | hinged hatch on frame | S1 |
| `lockout_pawl` | ~4 | safety pawl/ratchet lock element | S5 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `rotor_spin` / `turnstile_rotation` | CONTINUOUS | A.frame/base/bearing | B.rotor | `(0,0,1)` | unlimited | central radial turnstile rotor around vertical post | S1 / S2 / S3 / S4 |
| `rotor_step` | REVOLUTE | A.frame | B.rotor | `(0,0,1)` | `[-pi, pi]` or detented | limited/stepped rotor variant | S5 |
| `service_panel_hinge` | REVOLUTE | A.frame | C.service_panel | `(0,0,1)` | `[0, 1.35]` | side service panel opens | S1 |
| `inspection_hatch_hinge` | REVOLUTE | A.frame | C.inspection_hatch | horizontal `(0,-1,0)` | `[0, 1.2]` | inspection hatch opens upward/downward | S1 |
| `lockout_pawl_hinge` | REVOLUTE | A.frame | C.lockout_pawl | `(0,1,0)` | `[-0.3, 0.7]` | pawl engages rotor teeth | S5 |
| `base_to_bearing_module` / `base_to_frame` | FIXED | A.base | A.bearing/frame | n/a | n/a | fixed service/bearing stack | S3 / S4 |
| `left_gate_hinge` / `right_gate_hinge` | REVOLUTE | A.left/right cabinet | B.left/right gate | `(0,0,±1)` | `[0, 1.57]` | review-gated swing gate leaf alternate | S6 |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `lane_style` | enum | `refined_frame`, `rugged_base`, `service_bearing`, `split_head`, `dual_cabinet_glass` | `refined_frame` | Slot A module; `dual_cabinet_glass` review-gated | S1-S6 |
| `barrier_style` | enum | `three_arm_rotor`, `rugged_rotor`, `bearing_hub`, `modular_arm_hub`, `dual_swing_glass` | `three_arm_rotor` | Slot B module, gated by lane_style | S1-S6 |
| `service_module` | enum | `none`, `service_panel_and_hatch`, `fixed_bearing_stack`, `lockout_pawl` | `none` | Slot C module | S1 / S3 / S5 |
| `arm_count` | int | `3..4` | `3` | copied rotor arm visuals under one rotor part, central domain only | S1 / S2 / S5 |
| `arm_style` | enum | `round_tube`, `flat_bar`, `paddle`, `capsule_rail` | `round_tube` | rotor visual substyle | S1 / S2 / S5 |
| `rotor_height` | float | `[0.55, 1.35]` | `0.9` | arm z positions and frame rails derived | S1 / S2 |
| `lane_width` | float | `[0.75, 1.6]` | `1.05` | frame/cabinet spacing and arm radius derived | S1 / S4 |
| `rotor_joint_type` | enum | `continuous`, `limited_revolute` | `continuous` | lockout_pawl may use limited revolute | S1 / S5 |
| `gate_leaf_style` | enum | `none`, `glass_leaf_pair` | `none` | only for dual_cabinet_glass | S6 |

## Multiplicity / Copy Logic

- `arm_count`: `N_range=3..4`, sampling domain=`all integers`; copied object=rotor arm visuals under one rotor part, not independent parts/joints; placement=`360°/N` radial spacing around vertical hub; naming=`arm_i` visuals; source=S1/S2/S5. If implementation chooses separate arm parts, they must be FIXED to rotor and still move with one rotor joint.
- `gate_leaf_count`: `N_range=fixed 2`, module-derived only for `dual_cabinet_glass`; copied object=left/right gate part + independent REVOLUTE joint pair with mirrored axes; naming=`left_gate`, `right_gate`; source=S6.
- Fixed rails, fasteners, turnstile teeth, pawl teeth, bearing rings and service labels are module-local visuals/fixed structure, not exposed count parameters.

## 拓扑多样性审计

总组合数：5 lane modules x 5 barrier modules x 4 service modules x 2 arm_count values = 200 before legality gating.


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| fixed_support_lane | 5 | yes | central frame and dual-cabinet alternate |
| barrier_mechanism | 5 | yes | multiple rotor topologies plus swing-gate alternate |
| service_and_locking | 4 | yes | none/service/fixed bearing/pawl |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| fixed support | refined frame / rugged base / bearing stack / split head / dual cabinets | no | yes | `lane_style` | part tree differs substantially |
| barrier | radial arms / rugged rotor / modular hub / swing glass leaves | no | yes | `barrier_style`, `gate_leaf_style` | central rotor and swing gate are incompatible topologies |
| arms | round tubes / flat bars / paddles / capsule rails | no | yes | `arm_style` | visual identity of barrier changes |
| bearing/service | none / bearing module / wear rings / service panel / hatch | no | yes | `service_module` | fixed and revolute subparts differ |
| lockout | none / pawl | no | yes | `service_module=lockout_pawl` | second joint and safety story |
| dimensions | lane width / rotor height / arm radius | yes | no | continuous params | size differences only |

## 组合逻辑（Composition Logic）
1. Default central domain: establish vertical rotor axis from frame/base bearing center; derive arm radius and frame clearance from lane_width.
2. Rotor arms are placed radially under one rotor part and rotate together; never give each arm independent random rotation.
3. Service panels/hatches hinge on frame/cabinet edges; pawl origin sits near rotor ratchet path.
4. Bearing module/wear rings are FIXED chain or baked visuals around same vertical axis.
5. Review-gated dual swing gate branch uses mirrored cabinet contact planes and mirrored gate hinge axes; it should not be mixed with radial rotor in the same instance.

## 已有模板写法参考
`revolving_door` / `coaxial_rotary_stack` / `barrier_gate` / `revolute_hinge`（仅参考写法）

## 约束
- Default seed must be central radial turnstile with vertical rotor axis.
- Rotor arms must be radially distributed and attached to central hub.
- Rotor joint axis must be vertical `(0,0,1)` unless reviewed limited variant still uses vertical axis.
- Swing gate alternate is mutually exclusive with central rotor and should be reviewed for possible split.
- Service/hatch/pawl cannot occlude rotor arms in closed pose.

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | access-control turnstile lane with fixed support and barrier |
| default rotor | seed/default has central rotor with vertical CONTINUOUS joint |
| arm distribution | arm_count arms distributed evenly around hub |
| no independent arms | arms do not each rotate randomly; one rotor motion controls them |
| service joints | panels/hatches/pawl have correct parent and hinge axis |
| mutually exclusive | dual swing gate branch not combined with radial rotor |
| no floating | frame, bearing, rotor, gates, panels are connected |
| diversity | lane_style/barrier_style/service_module branches covered |

## Reject cases
- 变成普通栏杆、门或 barrier gate，没有 turnstile barrier mechanism。
- rotor axis not vertical or arms not radial。
- each arm independently rotates like a fan blade set rather than a turnstile hub。
- central rotor and dual swing glass gates mixed incoherently。
- service panel/pawl/hatch floats or blocks lane unrealistically。
- arm_count produces overlapping arms or exits frame clearance。
- default seed lacks central turnstile identity。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；建议重点审查 `dual_cabinet_glass` 是否拆分子 slug；未进入模板实现阶段 |
