# Clock Tower with Rotating Hour and Minute Hands Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `clock_tower_with_rotating_hour_and_minute_hands` |
| template path | `agent/templates/clock_tower_with_rotating_hour_and_minute_hands.py` |
| test path (optional) | `tests/agent/test_clock_tower_with_rotating_hour_and_minute_hands_template.py` |
| stage | `APPROVED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed`（tower spine + multiplicity dial/hands） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 36 |
| read_count | 36 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / prompt were read |
| samples_adopted_as_module_sources | 5 |
| samples_read_but_not_adopted | 31 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| monolithic tower part（dial visuals baked） | 12 | 单 `tower` part；dial/markers 为 visuals；hands 可能为子 part 或同 part |
| tower + hour_hand + minute_hand（单面） | 11 | 3-part；2× CONTINUOUS hand joints |
| tower + roof/clock_face + hands | 6 | 4–5 part；clock_face 独立 part |
| tiered shaft stack（base→shaft→lantern→dial→hands） | 4 | 6+ part 链，多 FIXED + 2 hand joints |
| dual-face housing（front/rear hands） | 1 | 6 part；4 hand parts + housing |
| shaft/plinth minimal（hands on shaft） | 2 | 2 part 但 4–5 joints（多 stage revolute） |
| bell-only / incomplete hands | 2 | 非默认成熟域 |

被采纳样本逐条标注：
- `rec_clock_tower_with_rotating_hour_and_minute_hands_004c708c80f84d9290185a2bd93e2c5c` — adopted：4-face glazed tower；每面独立 hour/minute part + CONTINUOUS joints；`_marker_ring` helper。
- `rec_clock_tower_with_rotating_hour_and_minute_hands_08ab090df8e646d9b5321cb2792c3439` — adopted：campanile round shaft + single clock face + mesh hands + belfry roof/bell visuals。
- `rec_clock_tower_with_rotating_hour_and_minute_hands_496b6569dfdd427b8101252fc8220196` — adopted：base→shaft→lantern→clock_face→hands 分层链。
- `rec_clock_tower_with_rotating_hour_and_minute_hands_89a4bced8c8b4ae0842c9b508c84d146` — adopted：column + housing + front/rear hour/minute；dual-face。
- `rec_clock_tower_with_rotating_hour_and_minute_hands_f551a3041a6b43d78aee3c9f757f262f` — adopted：base→shaft→belfry→roof→bell + clock_face + hands；7 part 丰富塔。
- Remaining 31 samples — read but not adopted：tower 装饰（band、spire、antenna）、palette、单面 vs 四面但结构已被覆盖；12 个 monolithic tower-only 样本 dial  baked 无独立 hand part，归入 integrated dial 模块。

## 核心身份

**Clock tower with rotating hour and minute hands**：竖向塔身（clock tower / campanile / shaft stack）上至少一面（通常多面）有时钟 dial，且有 **独立的 hour hand 与 minute hand** 各绕 dial 中心 **coaxial CONTINUOUS/REVOLUTE** 旋转。塔身本身 FIXED；可动语义集中在 hands（可选 bell swing 但不替代 hand 关节）。默认成熟域是 **multi-face glazed tower + per-face stacked hands**。

边界：
- 不包括无 hands 的纯 tower 或 bell tower（无 hour/minute 关节）。
- 不混入 `metronome` / `turntable`：身份件是 tower + clock dial，不是 pendulum/platter。
- 不混入 `lighthouse_with_rotating_beacon`：rotating 的是 light beacon，不是 clock hands。
- 不混入 wristwatch / desk clock：必须有 **tower** 竖向体量（高径比 > 1.5）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_clock_tower_with_rotating_hour_and_minute_hands_004c708c80f84d9290185a2bd93e2c5c` | `data/records/rec_clock_tower_with_rotating_hour_and_minute_hands_004c708c80f84d9290185a2bd93e2c5c/revisions/rev_000001/model.py:L21-L49,L81-L252,L258-L324` | 4-face tower：`_annulus`/`_marker_ring`、glazed shaft/head、per-face hands + joints |
| S2 | `rec_clock_tower_with_rotating_hour_and_minute_hands_08ab090df8e646d9b5321cb2792c3439` | `data/records/rec_clock_tower_with_rotating_hour_and_minute_hands_08ab090df8e646d9b5321cb2792c3439/revisions/rev_000001/model.py:L50-L95,L136-L289,L291-L343` | campanile：round shaft、single dial、mesh `_hand_shape`、hour/minute parts |
| S3 | `rec_clock_tower_with_rotating_hour_and_minute_hands_496b6569dfdd427b8101252fc8220196` | `data/records/rec_clock_tower_with_rotating_hour_and_minute_hands_496b6569dfdd427b8101252fc8220196/revisions/rev_000001/model.py:L53-L243,L246-L323` | tiered：base/shaft/lantern/clock_face/hands + FIXED chain |
| S4 | `rec_clock_tower_with_rotating_hour_and_minute_hands_89a4bced8c8b4ae0842c9b508c84d146` | `data/records/rec_clock_tower_with_rotating_hour_and_minute_hands_89a4bced8c8b4ae0842c9b508c84d146/revisions/rev_000001/model.py:L39-L138,L148-L362,L364-L407` | dual-face：column/housing、front/rear hands、`_add_hand_geometry` |
| S5 | `rec_clock_tower_with_rotating_hour_and_minute_hands_f551a3041a6b43d78aee3c9f757f262f` | `data/records/rec_clock_tower_with_rotating_hour_and_minute_hands_f551a3041a6b43d78aee3c9f757f262f/revisions/rev_000001/model.py:L23-L304,L306-L380` | belfry stack：base/shaft/belfry/roof/bell/clock_face/hands |

## 槽位 + 候选模块表

### Slot A：tower_spine

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `glazed_multiface_head` | S1 | `model.py:L81-L252` | **yes** | square glass shaft + clock head + lantern + 4 face specs |
| `campanile_round_shaft` | S2 | `model.py:L136-L289` | | round limestone shaft + belfry roof + bell mesh |
| `tiered_shaft_stack` | S3 | `model.py:L53-L195` | | base + shaft + lantern_room FIXED 链 |
| `belfry_column_stack` | S5 | `model.py:L23-L220` | | base/shaft/belfry_frame/roof/bell 多层 |

### Slot B：clock_dial

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integrated_face_visuals` | S1 | `model.py:L223-L252` | **yes** | dial glass/rim/marks baked on tower per face_spec loop |
| `single_face_mount` | S2 | `model.py:L166-L218` | | 单 front face：rim + markers on cylindrical shaft |
| `separate_clock_face_part` | S3 | `model.py:L196-L245` | | 独立 clock_face part + markers |
| `dual_housing_dial` | S4 | `model.py:L197-L306` | | housing part 带 front/rear dial features |

### Slot C：hand_mechanism

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `multiface_indexed_hands` | S1 | `model.py:L258-L324` | **yes** | `hour_hand_i`/`minute_hand_i` + per-face CONTINUOUS joints |
| `single_face_mesh_hands` | S2 | `model.py:L72-L95,L291-L343` | | `_hand_shape` mesh + hour_hand/minute_hand |
| `stacked_simple_hands` | S3 | `model.py:L246-L323` | | hour/minute on clock_face；stacked Z offset |
| `front_rear_named_hands` | S4 | `model.py:L308-L407` | | front_hour/minute + rear_hour/minute |

## 槽位图（slot graph）

pattern = `mixed`

```
[Slot A tower_spine]  (root, FIXED)
      |
      +-- [Slot B clock_dial]  (visuals on tower OR separate clock_face part)
      |
      +-- [Slot C hand_mechanism × face_count]
              each face: tower/clock_face --CONTINUOUS--> hour_hand
                        tower/clock_face --CONTINUOUS--> minute_hand
                        (coaxial, minute slightly proud of hour)
```

主约束基准：每 face 的 dial 中心点 + face normal（local Z 指向外）；hour/minute joint origin 共轴，axis = face normal（CONTINUOUS Z in face-local frame）。

## 部件（Parts）

### Slot A / glazed_multiface_head
| part | visual_count | 描述 | 来源 |
| `tower` | ~40+ | plinth、glass shaft、corner posts、bands、clock room、lantern、roof | S1 L81-L252 |

### Slot C / multiface_indexed_hands（per face i）
| part | visual_count | 描述 | 来源 |
| `hour_hand_i` | ~3 | hour_blade、hub、tail | S1 L258-L276 |
| `minute_hand_i` | ~4 | spindle、blade、hub、tail | S1 L278-L302 |

## 关节（Joints）

| 关节 | 类型 | parent | child | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `face_i_hour` | CONTINUOUS | tower | hour_hand_i | face normal | full | 时针 | S1 |
| `face_i_minute` | CONTINUOUS | tower | minute_hand_i | face normal | full | 分针；同 origin，Z offset | S1 |
| `hour_hand_rotation` | CONTINUOUS | tower | hour_hand | face normal | full | 单面 campanile | S2 |
| `minute_hand_rotation` | CONTINUOUS | tower | minute_hand | face normal | full | 单面 campanile | S2 |
| `clock_face_to_hour_hand` | CONTINUOUS | clock_face | hour_hand | (0,0,1) | full | tiered 方案 | S3 |
| `clock_face_to_minute_hand` | CONTINUOUS | clock_face | minute_hand | (0,0,1) | full | tiered 方案 | S3 |
| `housing_to_front_hour` | CONTINUOUS | housing | front_hour_hand | face normal | full | dual-face | S4 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `tower_style` | enum | `glazed_multiface` / `campanile_round` / `tiered_stack` / `belfry_column` | `glazed_multiface` | Slot A | S1-S5 |
| `dial_style` | enum | `integrated` / `single_face` / `separate_part` / `dual_housing` | `integrated` | Slot B | S1-S4 |
| `hand_style` | enum | `indexed_multiface` / `mesh_blade` / `stacked_simple` / `front_rear` | `indexed_multiface` | Slot C | S1-S4 |
| `face_count` | int | 1–4 | 4 for S1 anchor | 决定 hand 复制数量 | S1,S2,S4 |
| `tower_height` | float | 4.0–18.0 | sampled | shaft/head 比例 | S1,S2 |
| `shaft_width` | float | 0.8–2.8 | sampled | head_size = f(shaft) | S1 |
| `dial_radius` | float | 0.45–0.85 | sampled | marker ring、hand length | S1,S2 |
| `hour_hand_length` | float | 0.28–0.55 | derived | ≤ 0.85 × dial_radius | S1,S2 |
| `minute_hand_length` | float | 0.38–0.72 | derived | > hour_hand_length | S1,S2 |

## Multiplicity / Copy Logic

- **`face_count`**：模板级 multiplicity。
  - `count_param`: `face_count`
  - `N_range`: `1..4`
  - sampling domain: 整数；S1 anchor 用 `4`；S2 用 `1`；S4 dual-face 用 `2`（front+rear，非径向复制）
  - copied object: 每 face 一对 `(hour_hand, minute_hand)` part + 2× CONTINUOUS joint
  - naming: `hour_hand_{i}` / `minute_hand_{i}` / `face_{i}_hour` / `face_{i}_minute`
  - placement: 径向四面 `(±Y, ±X)` face centers（S1 `face_specs`）；单面 campanile 仅 `i=0`
  - joint policy: 每 face 独立 joint；minute 与 hour 共 origin、不同 Z offset
  - source/gating: 1/2/4 faces 来自 5 星样本；`face_count=3` 为 reviewer-gated 外推（120° 间隔）

- hour markers（12 ticks）：module-local 固定 `for i in range(12)` 循环，**不是**模板级 count 参数。

## 拓扑多样性审计

有效组合：4 × 4 × 4 × face_count variants ≈ **64 × {1,2,4}**


| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---:|---|---|
| tower_spine | 4 | yes | |
| clock_dial | 4 | yes | |
| hand_mechanism | 4 | yes | |
| face_count | 1–4 | yes | multiplicity |

## 部件多样性审计（Part Diversity Audit）

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| tower silhouette | yes | no | yes | `tower_style` | glazed vs round vs tiered |
| dial mounting | yes | no | yes | `dial_style` | integrated vs separate part |
| hand construction | yes | partial | yes | `hand_style` | mesh vs box blade vs dual-face naming |
| face count | yes | no | yes | `face_count` | 1/2/4 面 |
| bell/spire | partial | yes | no | n/a | optional visuals on tower |

## Validator（author_run_tests 必须覆盖的点）

- seed=0 复现 S1：`face_count=4`，8 个 CONTINUOUS hand joints。
- hour/minute 共轴（`expect_origin_distance` xy ≤ 0.001）。
- minute hand Z 略高于 hour（stacked separation gap ≥ 0.004）。
- minute hand 旋转后 blade AABB 宽度显著增加（可见旋转）。
- tower 为唯一 root；hands 不得 FIXED 于 tower 而无 joint。
- `face_count=1` 时 campanile 模块仍须 2 个 hand joints。

## Reject cases（必须能识别并拒绝）

- 无 hour_hand 或无 minute_hand part/joint。
- 仅一个 hand joint（缺 hour 或 minute）。
- tower 高径比 < 1.2（desk clock 比例）。
- hands joint axis 不垂直于 dial 平面。
- monolithic tower 样本无 hand joints 被误选为 anchor。

## 与相邻类别的边界

- 不该混入：`bell_tower_with_swinging_bell`（bell swing 替代 clock hands）。
- 不该混入：`metronome`（pendulum arm，无 tower dial）。
- 不该混入：`lighthouse_with_rotating_beacon_assembly`（beacon rotation，非 clock hands）。
- 不该混入：`ceiling_fan` / `turntable`（水平转子，无 vertical tower dial）。

## 模板实现备注（可选）

- 12 个 monolithic `tower`-only 样本已读：dial 为 visuals，部分在 compile 时仍生成 hand joints；模块 `integrated_face_visuals` 吸收该族作为模块来源，不作为单一主来源。
- S1 四 face 循环是 multiplicity 参考实现；`face_specs` 数组应参数化为 `face_count`。
- S4 front/rear 命名与 S1 indexed 不同；用 `hand_style=front_rear` 时 `face_count` 固定 2，非径向复制。
- hour/minute 轻微 overlap 可 allow（hub 区域）；blade 之间需 gap check。
- tiered 模块（S3/S5）的 base→shaft FIXED 链在 tower_spine 模块内闭合，不增加 hand DOF。
