# Rotary Table with Tilting Trunnion Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `rotary_table_with_tilting_trunnion` |
| template path | `agent/templates/rotary_table_with_tilting_trunnion.py` |
| test path (optional) | `tests/agent/test_rotary_table_with_tilting_trunnion_template.py` |
| stage | `APPROVED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 34 |
| read_count | 34 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / prompt were read |
| samples_adopted_as_module_sources | 5 |
| samples_read_but_not_adopted | 29 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| cast base + tilt cradle + rotary faceplate | 7 | 侧 cheek 或 integrated tilt_frame；tilt(X) + rotary(Z) |
| base + lower rotary stage + upper table/faceplate | 17 | 两节 stacked：base→lower REVOLUTE + lower→upper REVOLUTE/TILT |
| base + turntable + open cradle + table | 5 | 4-part：base rotary + FIXED cradle + trunnion tilt table |
| pedestal + compact rotary + tilt | 2 | 短 pedestal，运动链仍为 rotary + tilt |
| split trunnion shafts as separate parts | 4 | left/right trunnion part + yoke plate；4+ joints |

被采纳样本逐条标注：
- `rec_rotary_table_with_tilting_trunnion_0519446d725e4e46b67e698286d090b6` — adopted：canonical side-cheek trunnion；base + tilt_frame + turntable；tilt REVOLUTE X + rotary CONTINUOUS Z。
- `rec_rotary_table_with_tilting_trunnion_0003` — adopted：cadquery base/turntable/cradle/table；base rotary + cradle tilt via journals。
- `rec_rotary_table_with_tilting_trunnion_7bb3557e7b6649c2a14e0fc757cc5794` — adopted：mesh yoke + split trunnion parts + tool_plate；4 articulations。
- `rec_rotary_table_with_tilting_trunnion_92932ff709e44dfcb5044b69c24be33a` — adopted：stacked lower_stage + faceplate；heavy cadquery base。
- `rec_rotary_table_with_tilting_trunnion_457ff797fbe743e0bcf591e86fe49131` — adopted：compact pedestal + rotary_base + table；短机台。
- Remaining 29 samples — read but not adopted：slot 数量、T-slot 样式、handwheel、clamp bolt 等装饰差异，运动链已被上述模块覆盖。

## 核心身份

工业/机加用 **rotary table with tilting trunnion**：固定 base 上承载一个可绕水平 trunnion 轴俯仰（tilt）的 stage，该 stage 上再有一个可绕竖直轴连续旋转的工作台面（faceplate/table）。必须同时存在 **tilt trunnion** 与 **rotary table** 两个语义，且 rotary 轴与 tilt 轴正交。默认成熟域是 side-support trunnion + slotted machinist disk。

边界：
- 不包括纯 turntable（无 tilt trunnion）。
- 不混入 `turntable` DJ/record player：身份件是机加 faceplate/T-slot，不是 platter+tonearm。
- 不混入 `coaxial_rotary_stack`：只有一层 tilt+rotary，不是多层同轴 stack。
- 不混入 crane/welding positioner 的 multi-axis arm：trunnion 必须是 table 两侧轴承座结构。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_rotary_table_with_tilting_trunnion_0519446d725e4e46b67e698286d090b6` | `data/records/rec_rotary_table_with_tilting_trunnion_0519446d725e4e46b67e698286d090b6/revisions/rev_000001/model.py:L29-L73,L75-L107,L111-L158,L160-L179` | canonical trunnion：side cheek base、tilt_frame cross saddle、slotted turntable、2 joints |
| S2 | `rec_rotary_table_with_tilting_trunnion_0003` | `data/records/rec_rotary_table_with_tilting_trunnion_0003/revisions/rev_000001/model.py:L68-L176,L185-L284,L286-L320` | cadquery shapes：base/turntable/cradle/table、journal trunnion、3 joints |
| S3 | `rec_rotary_table_with_tilting_trunnion_7bb3557e7b6649c2a14e0fc757cc5794` | `data/records/rec_rotary_table_with_tilting_trunnion_7bb3557e7b6649c2a14e0fc757cc5794/revisions/rev_000001/model.py:L60-L283,L292-L393` | mesh yoke + split trunnion shafts + tool plate |
| S4 | `rec_rotary_table_with_tilting_trunnion_92932ff709e44dfcb5044b69c24be33a` | `data/records/rec_rotary_table_with_tilting_trunnion_92932ff709e44dfcb5044b69c24be33a/revisions/rev_000001/model.py:L29-L224,L233-L393,L396-L413` | stacked base→lower_stage→faceplate |
| S5 | `rec_rotary_table_with_tilting_trunnion_457ff797fbe743e0bcf591e86fe49131` | `data/records/rec_rotary_table_with_tilting_trunnion_457ff797fbe743e0bcf591e86fe49131/revisions/rev_000001/model.py:L22-L143` | compact pedestal rotary+tilt |

## 槽位 + 候选模块表

### Slot A：machine_base

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `side_cheek_cast_base` | S1 | `model.py:L29-L73` | **yes** | 大底板 + 两侧 cheek + bearing caps |
| `cadquery_box_base` | S2 | `model.py:L68-L88,L185-L196` | | cadquery base_shell + mounting pad |
| `stacked_heavy_base` | S4 | `model.py:L29-L55,L233-L238` | | 厚 cast base + ribbing，承载 lower_stage |
| `compact_pedestal` | S5 | `model.py:L22-L80` | | 短 pedestal + top rotary seat |

### Slot B：tilt_trunnion_stage

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integrated_tilt_frame` | S1 | `model.py:L75-L107,L160-L169` | **yes** | cross saddle + rotary bearing race + pivot hubs；child of base tilt joint |
| `open_cradle_yoke` | S2 | `model.py:L107-L154,L212-L251,L307-L320` | | 双 riser + 双 arm cradle；table journals 骑在 arm 上 |
| `mesh_yoke_trunnions` | S3 | `model.py:L117-L283,L304-L393` | | cadquery yoke mesh + separate left/right trunnion parts |
| `lower_rotary_stage` | S4 | `model.py:L56-L137,L240-L325,L396-L404` | | lower_stage 兼 tilt+rotary 中间节（stacked 语义） |

### Slot C：rotary_faceplate

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `slotted_machinist_disk` | S1 | `model.py:L111-L158,L170-L179` | **yes** | T-slots + bolt holes + center bore；CONTINUOUS Z |
| `cadquery_table_plate` | S2 | `model.py:L155-L176,L253-L279` | | square table_plate + body + journals |
| `mesh_tool_plate` | S3 | `model.py:L200-L283,L316-L327` | | tool_plate mesh + clamp features |
| `large_faceplate` | S4 | `model.py:L138-L224,L325-L393,L405-L413` | | 大 faceplate + radial slots |

## 槽位图（slot graph）

pattern = `linear_chain`

```
[Slot A machine_base]
      -- tilt REVOLUTE, axis (1,0,0) typical -->
[Slot B tilt_trunnion_stage]
      -- rotary CONTINUOUS/REVOLUTE, axis (0,0,1) -->
[Slot C rotary_faceplate]
```

主约束基准：trunnion 水平轴穿过 side cheek 中心；rotary 竖轴与 trunnion 正交且通过 bearing race 中心。faceplate 半径、slot 长度从 bearing race 直径派生。

## 部件（Parts）

### Slot A / side_cheek_cast_base
| part | visual_count | 描述 | 来源 |
| `base` | ~8 | base_plate、side_support、bearing caps、cheek ribs | S1 L29-L73 |

### Slot B / integrated_tilt_frame
| part | visual_count | 描述 | 来源 |
| `tilt_frame` | ~6 | cross_saddle、rotary_bearing、race、pivot_hubs | S1 L75-L107 |

### Slot C / slotted_machinist_disk
| part | visual_count | 描述 | 来源 |
| `turntable` | ~10 | disk、rim、center bore、slots、fixture holes | S1 L111-L158 |

## 关节（Joints）

| 关节 | 类型 | parent | child | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `base_to_tilt_frame` | REVOLUTE | base | tilt_frame | (1,0,0) | ~[-1.05,1.05] | trunnion tilt | S1 |
| `tilt_frame_to_turntable` | CONTINUOUS | tilt_frame | turntable | (0,0,1) | full | 工作台旋转 | S1 |
| `base_to_turntable` | REVOLUTE | base | turntable | (0,0,1) | ±π | cradle 方案的 base 旋转 | S2 |
| `cradle_to_table` | REVOLUTE | cradle | table | (1,0,0) | ±60° | journal trunnion tilt | S2 |
| `base_rotation` | CONTINUOUS | base | yoke | (0,0,1) | full | split trunnion 方案 | S3 |
| `trunnion_tilt` | REVOLUTE | yoke | tool_plate | (1,0,0) | limited | plate 相对 yoke 俯仰 | S3 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `base_style` | enum | `side_cheek` / `cadquery_box` / `stacked_heavy` / `pedestal` | `side_cheek` | Slot A | S1-S5 |
| `tilt_stage_style` | enum | `integrated_frame` / `open_cradle` / `mesh_yoke` / `lower_stage` | `integrated_frame` | Slot B | S1-S4 |
| `faceplate_style` | enum | `slotted_disk` / `square_table` / `mesh_plate` / `large_faceplate` | `slotted_disk` | Slot C | S1-S4 |
| `table_diameter` | float | 0.45–1.10 | sampled | 派生 slot 长度、base footprint | S1,S2 |
| `base_footprint_x` | float | 0.70–1.40 | sampled | side cheek 间距 | S1 |
| `tilt_limit_rad` | float | 0.8–1.2 | 1.05 | trunnion 行程 | S1,S2 |
| `slot_count` | int | 2–4 | 3 | T-slot 条数（module-local 固定循环） | S1 |

## Multiplicity / Copy Logic

- `slot_count`：**不是**模板级随机 count；各 module 内固定 2–4 条 T-slot 循环，来自 5 星样本观察，不独立采样 N。
- side cheek ribs、fixture holes、bolt holes 为 module-local 固定循环（`slot_i`、`fixture_hole_i`）。
- 无 radial-multiplicity 叶片/臂复制逻辑。

## 拓扑多样性审计

总组合数：4 × 4 × 4 = **64**


| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---:|---|---|
| machine_base | 4 | yes | |
| tilt_trunnion_stage | 4 | yes | |
| rotary_faceplate | 4 | yes | |

## 部件多样性审计（Part Diversity Audit）

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base footprint | yes | partial | yes | `base_style` | cheek vs pedestal vs stacked |
| tilt mechanism | yes | no | yes | `tilt_stage_style` | integrated vs cradle vs split trunnion |
| faceplate | yes | partial | yes | `faceplate_style` | round slots vs square table vs mesh |
| handwheel/clamp | partial | yes | no | n/a | 装饰 optional visuals |

## Validator（author_run_tests 必须覆盖的点）

- seed=0 复现 S1：3 parts、tilt REVOLUTE + rotary CONTINUOUS。
- trunnion hub 与 side cheek 接触；turntable disk  seated on rotary bearing。
- rotary 旋转时 slot/face 特征 XY 包络变化；tilt 时 faceplate 相对 base Z 间隙保持。
- open_cradle 模块：left/right journal 与 cradle arm 接触；tilt 极限时 table 不穿透 turntable。
- tilt 轴必须为水平 X（或 Y），rotary 轴必须为竖直 Z；禁止两轴平行。

## Reject cases（必须能识别并拒绝）

- 只有 rotary 无 trunnion tilt（纯 turntable）。
- 只有 tilt 无 rotary workspace（纯 swiveling vise head）。
- faceplate 与 base 无 bearing 接触、trunnion hub 悬空。
- joint 轴与 table 法线同向（语义混淆 rotary vs tilt）。

## 与相邻类别的边界

- 不该混入：`turntable`（DJ/record player；无 trunnion cheek）。
- 不该混入：`coaxial_rotary_stack`（多层同轴转台，非 tilt+rotary 两节）。
- 不该混入：`monitor_mount` / `cantilever_articulated_arm`（arm link 链，非 machinist table）。
- 不该混入：`traditional_windmill` / `overshot_waterwheel`（建筑/水车旋转件）。

## 模板实现备注（可选）

- S2 四 part 链（base→turntable→cradle→table）与 S1 三 part 链拓扑不同；实现时用 module 内部 part 树封装，assemble 仍输出 2 个 chain joint。
- S3 split trunnion 的 plate_to_trunnion joints 可能 grandfathered；优先在 tilt_frame 模块内用 visuals 表达 trunnion shaft。
- positive tilt 时 table 需 `expect_gap` 相对 base/turntable（参考 S2 tests L400-L408）。
- cadquery mesh 模块需 `check_mesh_files_exist` / asset path 处理（S2/S4）。
