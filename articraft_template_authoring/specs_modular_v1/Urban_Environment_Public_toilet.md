# Public Toilet Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `public_toilet` |
| template path | `agent/templates/Urban_Environment_Public_toilet.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (block root + per-cabin door children + multiplicity) |

## 样本阅读摘要
- 来源:`<ARTI_SKILL_ROOT>/articraft_data`,类目 `urban_environment`。
- 母资产 `rec_portable-toilet-cabin-porta-potty-a-magenta-red-_…5cec201b`(单间 porta-potty)+ 四连排 block 样本。
- 本会话用 dashscope/qwen3.7-max fork 管线**扩了 12 个结构变体**(全部 `status=success`):
  `roof_gable / roof_domed / roof_flat`、`walls_corrugated / walls_smooth`、`door_window`、`vent_twin`、`utility_handwash`、`interior_urinal`、`base_skid`、`accessible_wide`、`tall_narrow`。
- 母资产几何全为 Box/Cylinder 基本体(cabin 根 + 单门 REVOLUTE 竖铰链)。

## 核心身份
Portable public toilet cabin (porta-potty), or a row block of N identical cabins. Each cabin = floor pan/skid + three walls + a roof + a vent, with a full-height front DOOR that swings on a VERTICAL (+Z) hinge at a front corner. The block tiles cabins along +Y; each cabin has its own door (the only moving parts).

边界:不是单体家用 `toilet`(陶瓷坐便器);是户外整体式塑料隔间/连排。

## 槽位 + 候选模块
| slot | 候选 | 来源 |
|---|---|---|
| **roof** | `sloped` / `gable` / `domed` / `flat` | 母资产(domed=curved cap)+ roof_gable/flat |
| **walls** | `ribbed` / `corrugated` / `smooth` | 母资产(ribbed)+ walls_corrugated/smooth |
| **utility** | `corner_stack` / `twin_stack` / `roof_unit` | 母资产(corner)+ vent_twin / utility_handwash |
| **door**(每间) | `louvered` / `window` | 母资产(louver)+ door_window |
| **cabin_count** | `1..4`(多重性,每间一门) | 单间母资产 + 四连排 block |

外加 footprint `width_scale`(0.85–1.45,含 accessible_wide)/ `height_scale`(0.85–1.18,含 tall_narrow)坐标缩放,5 种配色(magenta/blue/green/gray/sand)。

## 槽位图(mixed)
```text
[block]  (root, all N cabin shells, grounded)
  └── cabin_i_to_door  REVOLUTE axis +Z  --> door_i   (i = 0..cabin_count-1)
```

## 关节
| 关节 | 类型 | parent | child | axis | range |
|---|---|---|---|---|---|
| `cabin_{i}_to_door` | REVOLUTE | block | door_{i} | `(0,0,1)` | `0..~1.75` |

## 部件
| part | 描述 |
|---|---|
| `block` | N 个 cabin shell(floor/skid、3 墙 ribbed/corrugated/smooth、roof、utility vent/stack/roof_unit、front header+jambs) |
| `door_{i}` | 门叶 + hinge stile(下探至地面含铰链原点)+ ribs/louver 或 window + 占用指示 + 把手 |

## 拓扑多样性

## 采样/验收
`config_from_seed`:rng 选各 enum + cabin_count(randint 1–4)+ 缩放。`compile-sweep 0-49 --quality-profile final`:**verdict=pass, pass_rate=1.0, diversity=49**(已通过)。

## Validator
- block 接地;每间 door 为 REVOLUTE 竖轴、关闭从 q=0;door 数 == cabin_count。
- 门叶/铰链立柱坐在 cabin 前框(element/part-scoped allow_overlap);roof_unit 坐檐口、不浮空。

## Reject
- 门浮在隔间外、roof/utility 件浮空、门轴非竖直。
- 变成单体陶瓷马桶(toilet 类目)。

## 审核记录
| reviewer | pending(SPEC_ONLY_DRAFT;变体由本会话 qwen fork 管线扩成,模板 0–49 全过)|
