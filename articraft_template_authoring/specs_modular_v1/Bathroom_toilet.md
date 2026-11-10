# Toilet Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `toilet` |
| template path | `agent/templates/Bathroom_toilet.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 样本阅读摘要
- 来源仓库:`<ARTI_SKILL_ROOT>/articraft_data`,类目 `bathroom`(toilet picture-family)。
- 池子:**25 条** —— 2 个母资产(`one-piece` 一体落地、`wall-hung` 壁挂)+ `qwen37-toilet-001-v01…v30` 约 23 个 qwen fork 变体。**已扩过变体,本模版不再扩**。
- 读样确认结构多样性充分(每条带头注释说明体型):
  - v01 壁挂+隐藏水箱碳carrier;v07 高位水箱+拉链(`pull_chain`);v13 **两件式**(独立 tank+tank_lid+bowl);v18 儿童款;v25 加长壁挂 skirted;v30 **商用 flushometer + flush_lever**。

## 核心身份
A toilet fixture: a glossy ceramic bowl with a hinged seat ring + lid (soft-close), a cistern/tank or wall carrier, and flush hardware. Core motion = seat ring + lid REVOLUTE hinges (lateral Y axis at the rear of the bowl); secondary motion = the flush control (button press PRISMATIC, lever REVOLUTE, or pull-chain PRISMATIC).

边界:不是 bidet / urinal / public_toilet cabin;就是单体坐便器。

## 采用源码索引
base = `<ARTI_SKILL_ROOT>/articraft_data/data/records/<id>/revisions/rev_000001/model.py`
| id | 用途 |
|---|---|
| P1 `rec_one-piece-white-ceramic-toilet-with-an-integrate_20260605_154135_382134_3d27a5c3` | one-piece 落地体几何(bowl 裙座 + 一体水箱 + seat_ring/lid REVOLUTE + 顶部 dual-button PRISMATIC) |
| P2 `rec_wall-hung-white-ceramic-toilet-with-a-soft-close_…` | 壁挂体(墙挂背板 + 悬臂 bowl + 隐藏水箱 + 多按钮) |
| V13 `rec_qwen_toilet_001_v13` | 两件式(独立 tank + tank_lid + bowl) |
| V30 `rec_qwen_toilet_001_v30` | 商用 flush_lever(REVOLUTE) |
| V07 `rec_qwen_toilet_001_v07` | 高位水箱 pull_chain(PRISMATIC) |

## 槽位 + 候选模块

### Slot A：body（陶瓷体 + 水箱/挂座,grounded root）
| module | 来源 | 结构特征 |
|---|---|---|
| `one_piece_floor` | P1 | 落地一体壳:裙座 bowl + 一体后水箱(平顶) |
| `wall_hung` | P2 | 墙挂背板 + 悬臂 bowl + 隐藏水箱(无落地裙座) |
| `two_piece` | V13 | 落地 bowl + 独立 close-coupled 水箱 + tank_lid |
≥3 候选,真·拓扑不同(落地一体 / 悬臂壁挂 / 分体水箱)。

### Slot B：flush（冲水控制,parent=body 的水箱/壳)
| module | 来源 | 关节 |
|---|---|---|
| `dual_button` | P1 | 顶部双键,PRISMATIC 下压 |
| `side_lever` | V30 | 侧扳手(水箱**侧面**护板+踏板手柄,绕前后 X 轴下压),REVOLUTE |
| `pull_chain` | V07 | 水箱**侧面**支架+链节+握把,PRISMATIC 下拉 |
> 扳手/拉杆挂在水箱 **+Y 侧面**(不是正面),更贴近真实安装。侧面护板/支架在 y 向加宽以跨过随 `width_scale` 缩放的水箱壁面 → 任意宽度都与壳体熔合(避免 disconnected-island);拉链用连续细杆串起链节珠+握把(避免离散珠子断成多岛)。
兼容门控:`pull_chain` 需要 `two_piece`/高水箱(壁挂隐藏箱不挂拉链);`dual_button` 适配一体/分体/壁挂;`side_lever` 适配一体/分体。

### Slot C：seat（座圈 + 盖)
| module | 关节 |
|---|---|
| `ring_lid` | seat_ring REVOLUTE + lid REVOLUTE(缓降) |
| `ring_only` | 仅 seat_ring REVOLUTE(商用开口座圈,无盖) |

## 槽位图（mixed)
```text
[Slot A body] (root, on floor or wall)
  ├── seat_ring_hinge REVOLUTE axis Y  --> seat_ring (Slot C)
  ├── lid_hinge       REVOLUTE axis Y  --> lid       (Slot C, 若 ring_lid)
  └── flush joint (PRISMATIC 下压/下拉 或 REVOLUTE 扳手) --> flush part (Slot B)
```

## 关节
| 关节 | 类型 | parent | child | axis | range |
|---|---|---|---|---|---|
| `seat_ring_hinge` | REVOLUTE | body | seat_ring | `(0,1,0)` | `0..~1.9` |
| `lid_hinge` | REVOLUTE | body | lid | `(0,1,0)` | `0..~1.9` |
| `flush_press` | PRISMATIC | body | flush_button | `(0,0,-1)` | `0..0.012` |
| `flush_lever` | REVOLUTE | body | flush_lever | `(0,1,0)` | `0..0.5` |
| `flush_chain` | PRISMATIC | body | pull_handle | `(0,0,-1)` | `0..0.06` |

## 参数 / 多重性
| 参数 | 范围 | 默认 |
|---|---|---|
| `body_module` | one_piece_floor / wall_hung / two_piece | one_piece_floor |
| `flush_module` | dual_button / side_lever / pull_chain | dual_button |
| `seat_module` | ring_lid / ring_only | ring_lid |
| `palette` | white / ivory / gray | white |
| 尺寸微扰(bowl 高/宽/tank) | 围绕基线 ±10% | — |
(toilet 无明显大多重性;多样性来自 body×flush×seat 组合 + 尺寸。)

## 拓扑多样性

## 采样/验收

## Validator
- 恰有一个 bowl 体(grounded:落地或挂墙,不浮空)。
- seat_ring + (若 ring_lid)lid 为 REVOLUTE 横轴铰链,关闭从 q=0。
- flush 关节类型与 flush_module 匹配;按钮/扳手/拉链坐落在水箱/壳上(可见支撑)。
- 座圈/盖闭合贴合 bowl 口;element-scoped allow_overlap 处理铰链 barrel 嵌入。

## Reject
- bowl 悬空、座圈/盖脱离铰链、水箱浮在 bowl 外、flush 件不接触壳体。
- 变成 bidet/urinal/小便池。

## 审核记录
| reviewer | pending(SPEC_ONLY_DRAFT;源自 25 个已扩 toilet 变体,无需再扩) |
