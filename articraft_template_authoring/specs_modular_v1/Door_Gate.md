# gate — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `gate` |
| template path | `agent/templates/Door_Gate.py` |
| test path (optional) | `tests/agent/test_gate_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root surround = parent visual；leaf(s) 挂到 surround 为 parallel_children 的 1–2 个 REVOLUTE leaf；每个 leaf 内部用 multiplicity 循环发射 N 根 picket / bar / finial） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 parent + 8 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读笔记（全部 9 个均 rating=5；逐个读了 `model.py`）：

- **rec_door_gate（parent）** — 拱形石砌 surround（`_stone_masonry` L94-L157，真实半圆拱 + 矩形门洞布尔切割）+ 固定装饰 fanlight 铁艺（`_fanlight_grille` L177-L345：外缘环 + baluster-and-ring arcade band + 中央 oval medallion + 镜像 volute）+ gold 配件（`_fanlight_gold` L348-L379）。两扇镜像铁叶 `door_0`/`door_1`，每叶 `_leaf_iron(sign)` L482-L549：周框 + 三道横 rail 划分上/中/下三 panel，中段 panel 用 `for i in range(N_BARS)` L536-L543 均布发射 N 根方截面 picket，上下 panel 覆盖密集 C-scroll/volute（`_leaf_scroll_iron` L607-L656、`_scroll_panel_iron` L552-L604）。两个 REVOLUTE 竖轴铰（`surround_to_door_0` L844-L852 / `surround_to_door_1` L857-L866），`door_1` 用 `Mimic(joint="surround_to_door_0")` 镜像耦合，axis 取反，同一正 q 让两叶同时向 -Y 外摆。hinge knuckle 嵌入 jamb（captured-pin）用 element-scoped `allow_overlap`（run_tests L886-L899）。
- **rec_gate_var_plainbars** — 与 parent 同骨架，但 `_leaf_iron` L483-L535 移除全部 scrollwork helper，只保留周框 + 一整片满高 picket 场（`for i in range(N_BARS)` L526-L533，picket 从底框到顶框满高），是“纯竖栏 infill”的最简形态。
- **rec_gate_var_panelinfill** — `_leaf_iron` L485-L549：底 1/3 实心铁 kick panel（`_kick_panel` L714-L737，单独 visual `door_*_kick`）+ 上部 bar 场（`for i in range(N_BARS)` L536-L543，bar 仅在 kick rail 之上）。`_leaf_scroll_iron` 签名改为 `(sign, bar_z0, bar_z1, z0, z1)`（L607-L636，只在 bar 场加轻 overlay）。run_tests 额外断言 kick 在 leaf 下 1/3（L959-L974）。
- **rec_gate_var_n5** — `N_BARS = 5`（L67），与 parent 完全同骨架，仅 picket 数量改成 5（稀疏场）；run_tests 含 `N_BARS == 5` 断言（L1024）。
- **rec_gate_var_n11** — `N_BARS = 11`（L67），同骨架，密集场；run_tests 含 `N_BARS == 11`（L1024）。
- **rec_gate_var_flatrail** — 头部 profile 改造：`_rectangular_surround` L103-L138（左右 pillar + 平 lintel，三 box union，**无拱、无 fanlight**）+ 铁艺平顶横 rail `_top_rail` L141-L150（`TOP_RAIL_H` L75 / `TOP_RAIL_D` L76，横跨净开口）。leaf 仍为 scroll infill（`_leaf_iron` L261-L329，picket loop L315）。两 REVOLUTE 叶 + mimic 不变（L626-L645）。
- **rec_gate_var_speartop** — 头部 profile 改造：每根 picket 顶部加铸造矛尖 finial。`_spear_finial` L270-L293（XZ 半 profile `revolve(360)` 的回转体；常量 `PICKET_EXT`/`FINIAL_*` L80-L85）。`_leaf_iron` L301-L379 内 picket 延伸到 `z1+PICKET_EXT`（loop L360-L367），随后第二个 `for i in range(N_BARS)` L370-L373 在每根 picket 顶发射 finial。**无 fanlight**（开放矛尖排头）。
- **rec_gate_var_single** — leaf-count 改造：一扇宽叶 `gate_leaf`（`_leaf_iron()` 无 sign 参数 L429-L497，`LEAF_W = 2.14` 横跨全开口，`N_BARS = 14` 跨全叶，latch stile L490-L495）+ latch handle `_latch_handle` L703-L733。单个 `surround_to_leaf` REVOLUTE（L796-L804，**无 mimic**）。保留 arched surround + fanlight。run_tests 单叶版（L814+，latch 检查 L878）。
- **rec_gate_var_zbrace** — framing/brace 改造：`_z_brace(sign)` L790-L832（一根连续对角 box，从底-铰角到顶-闩角，旋转嵌入两端框角，单独 visual `door_*_brace` L875-L877 / L888-L890，material iron）。leaf base 与 parent 同（scroll infill `_leaf_iron` L482-L549）。两 REVOLUTE 叶 + mimic 不变（L900-L921）。

材质在全部 9 个样本里完全一致（`stone`/`plaster`/`threshold`/`iron`/`gold`，见 parent `_materials` L81-L86），即现有 5 星样本没有 colorway 变化——所以 `palette_style` 是本 spec **新增**的模板级参数（见 §7），不改拓扑、只重映射 iron/gold/stone 三种 material 的 rgba。

## 核心身份

Gate = **可外摆的开放镂空门**：一个固定的石砌 / lintel surround（root parent visual，不动）托住 1 或 2 扇用真实竖轴 REVOLUTE 铰连接的铁叶；每扇叶是一个周边框 + 内部由 N 根均布竖直 picket/bar（或实心 kick panel + bar 场）构成的**透空 infill 场**，常叠加锻铁 C-scroll/volute 装饰、顶部可为平头 / 矛尖 finial / 拱形，可加 Z 形对角 brace；双叶时两叶镜像 mimic 耦合、同一正 q 同时向 -Y 外摆。成熟域：花园 / 庭院 / 入户铁艺门（wrought-iron entrance/garden gate）。

不该混入：
- **实心遮挡门板（Door）**：本类核心是“可见空隙的镂空 infill 场 + N 根 picket 多重复制”，叶身大部分透空；panelinfill 的实心 kick 也只占下 1/3。Door 是整块实心门扇。
- **栅栏 / 围墙（Fence/Railing）**：Fence 是不会开合的连续静态 panel 序列；Gate 必须有真实 REVOLUTE 铰、可摆开让出通道。
- **窗格 / 格栅（Window grille）**：fanlight 在本类是 surround 上的**固定 parent visual**，不是独立可动件；不要把它当成主结构或独立 slot。

## 槽位 + 候选模块表

### Slot A：leaf infill pattern（叶内填充拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| ornamental_scroll_infill | rec_door_gate (parent) | `_leaf_iron` L482-L549；`_leaf_scroll_iron` L607-L656；`_scroll_panel_iron` L552-L604；`_volute` L449-L474 | eligible if compatible | 三 rail 划上/中/下 panel：中段 picket 场 + 上下密集 C-scroll/volute/oval-boss，覆盖在轻 picket 场上 |
| vertical_picket_infill | rec_gate_var_plainbars | `_leaf_iron` L483-L535（scroll helper 全删）；picket loop L526-L533 | eligible if compatible | 周框 + 一整片满高均布直竖 picket，无任何 scrollwork（最简透空场） |
| panel_and_bar_infill | rec_gate_var_panelinfill | `_leaf_iron` L485-L549；`_kick_panel` L714-L737；bar loop L536-L543；`_leaf_scroll_iron(sign,bar_z0,bar_z1,...)` L607-L636 | eligible if compatible | 底 1/3 实心铁 kick panel + 其上 bar 场（picket 仅占上 2/3）；kick 为单独 `door_*_kick` visual |

### Slot B：picket-top / top-rail profile（头部轮廓）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_top_with_fanlight | rec_door_gate (parent) | leaf 平头/平 rail `_leaf_iron` L482-L549；拱 surround + fanlight `_stone_masonry` L94-L157 / `_fanlight_grille` L177-L345 | eligible if compatible | 平顶横 rail + 方头 picket，配拱形石 surround + 固定 fanlight 铁艺（拱在 surround，不在叶头） |
| flat_rail_head_no_fanlight | rec_gate_var_flatrail | `_rectangular_surround` L103-L138；`_top_rail` L141-L150；常量 `TOP_RAIL_H` L75 / `TOP_RAIL_D` L76 / `LINTEL_H` L81 | eligible if compatible | 平矩形 surround（左右 pillar + 平 lintel，无拱）+ 横跨净开口的平铁顶 rail；**去掉 fanlight** |
| spear_pointed_tops | rec_gate_var_speartop | `_spear_finial` L270-L293；leaf picket 延伸 loop L360-L367 + finial loop L370-L373；常量 L80-L85 | eligible if compatible | 每根 picket 伸出顶 rail 之上，戴一枚回转体矛尖 finial（成排矛头开放头部）；**去掉 fanlight** |
| arched_cambered_top | — | （lathe/CadQuery 曲线头 rail + 跟随曲线的 picket 高度，现有 5 星无此片段） | not sampled (out of scope) | 凸 cambered 顶 rail，闭合双叶成连续拱。Slot B 已有 3 个候选，足够；列此项仅记录后续扩展方向，初版**不进 seed domain** |

### Slot C：framing / brace topology（框架 / 加固拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain_rails_frame | rec_door_gate (parent) | `_leaf_iron` 周框 + 横 rail L500-L529 | eligible if compatible | 矩形周框 + 仅横向 rail，无对角 brace（默认框架） |
| z_brace_diagonal | rec_gate_var_zbrace | `_z_brace(sign)` L790-L832；装配为单独 visual `door_*_brace` L875-L877 / L888-L890 | eligible if compatible | 经典 Z-brace ledged-and-braced：在 plain frame 上叠一根底铰角→顶闩角的连续对角铁 box，两端嵌入框角 |
| ring_and_arch_brace | — | （lathe/CadQuery 圆环 annulus 熔进框，现有 5 星无此片段） | not sampled (out of scope) | 大结构装饰环嵌入叶。Slot C 已有 2 个候选满足 ≥2；该项更重，会与开放 scroll 场争抢空间，初版**不进 seed domain** |

### Slot D：leaf count（叶数）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| double_leaf | rec_door_gate (parent) | `door_0`/`door_1` parts L817-L834；`surround_to_door_0` L844-L852 + `surround_to_door_1`（mimic）L857-L866 | eligible if compatible | 两镜像叶，各一 REVOLUTE 竖轴铰，`door_1` mimic-coupled 到 `door_0`，axis 取反，正 q 同步外摆 |
| single_leaf | rec_gate_var_single | `gate_leaf` part L768-L788；`_leaf_iron()`（无 sign，宽叶）L429-L497；`surround_to_leaf` REVOLUTE L796-L804；latch stile L490-L495 / `_latch_handle` L703-L733 | eligible if compatible | 一扇宽叶（`LEAF_W=2.14` 横跨全开口、`N_BARS=14` 跨全叶）在一侧 jamb 单铰，对侧 jamb 处为 latch stile + handle；**无 mimic**，恰好一个真 REVOLUTE |

## 槽位图（slot graph）

pattern: `mixed`

```
stone/lintel surround (root, fixed parent visual: masonry + threshold + plaster_reveal
                       + [fanlight_grille + fanlight_gold]?(B 决定) + [top_rail]?(B 决定))
        │
        ├─[REVOLUTE Z @ jamb_x = -(OPENING_W/2 - JAMB_REVEAL), origin on left jamb,
        │   axis=(0,0,-1), lower=0 upper≈1.92]──> leaf_0
        │
        └─[REVOLUTE Z @ jamb_x = +(OPENING_W/2 - JAMB_REVEAL), origin on right jamb,
            axis=(0,0,+1), Mimic(surround_to_leaf_0, mult=1, off=0)]──> leaf_1   (仅 Slot D=double)

each leaf (slot A × C 决定叶身, multiplicity 轴 N 决定竖元数量):
   perimeter frame ──(C: + diagonal z_brace box, 嵌两框角)
        └─ infill field：for i in range(N) 均布 picket/bar  ──(A: + kick panel / + scroll overlay)
                └─(B=spear: 第二个 for i in range(N) 在每 picket 顶发射 finial)
   leaf 还含 hinge knuckles（嵌 jamb，captured-pin，element-scoped allow_overlap）
```

接口点位：
- **surround ↔ leaf**：唯一跨 slot 活动连接。mating = jamb 内立面竖直 hinge 轴；joint origin 在 `(±(OPENING_W/2 - JAMB_REVEAL), 0, 0)`，axis 为 ±Z。leaf 在自身局部系从 hinge 边（local X=0）向中心延伸。
- **double 的两叶**：通过 `surround` 共同 parent + center 对称面装配；`leaf_1` 用 Mimic 把行程绑到 `leaf_0`，axis 取反，保证正 q 同时外摆（parent L857-L866）。
- **leaf 内 frame ↔ infill ↔ brace ↔ finial**：全部在 leaf-local 系熔成单个 visual（或少数并列 visual：iron / gold / knuckles / kick / brace），无内部 joint；brace/kick/scroll 端点都嵌入 rail/框以保证连通（zbrace L806-L811；scroll spine reach L571-L578）。
- **surround ↔ fanlight / top_rail**：固定 parent visual，`expect_contact(fanlight_grille, masonry)`（parent L963-L966）；top_rail 贴 lintel 下沿（flatrail L144）。

互斥 / 可选 / 派生关系：
- Slot B 决定 surround 形态与 fanlight/top_rail 是否存在：`straight_top_with_fanlight` → 拱 surround + fanlight；`flat_rail_head` → 矩形 surround + top_rail、无 fanlight；`spear_pointed_tops` → 拱或矩形 surround、无 fanlight、picket 伸出 + finial（见兼容矩阵）。
- Slot D=single 时只发射 1 个 leaf + 1 个 REVOLUTE（无 mimic），并启用 latch stile/handle；D=double 时发射镜像 2 leaf + mimic。
- multiplicity 轴 N 由 Slot D 派生其语义（double: 每叶 N；single: 全叶 N，范围加倍，见 §8）。

## 每槽位 Module Emits / Interfaces

### Slot A / module ornamental_scroll_infill
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf iron visual（frame+rails+picket 场+scroll）+ gold scroll accents visual | parent `_leaf_iron` L482-L549；`_leaf_scrolls` L687-L738 |
| internal joints | 无（叶内全熔成 visual） | parent `_leaf_iron` |
| upstream interface | hinge 边在 local X=0；由 surround REVOLUTE 消费 | parent L482-L489 |
| downstream interface | 中心 meeting 边（double）/ latch 边（single） | parent run_tests L948-L951 |

### Slot A / module vertical_picket_infill
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf iron visual（仅 frame + 满高 picket 场） | rec_gate_var_plainbars `_leaf_iron` L483-L535 |
| internal joints | 无 | 同上 |
| upstream / downstream interface | 同 ornamental（hinge 边 X=0 / 中心或闩边） | L483-L489 |

### Slot A / module panel_and_bar_infill
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf iron visual（frame + 上部 bar 场 + 轻 overlay）+ 独立 `door_*_kick` 实心板 visual | rec_gate_var_panelinfill `_leaf_iron` L485-L549；`_kick_panel` L714-L737 |
| internal joints | 无 | 同上 |
| upstream interface | hinge 边 X=0 | L485-L491 |
| downstream interface | kick 占下 1/3，bar 场占上 2/3（run_tests 断言 kick 在下三分位 L959-L974） | L520-L543 |

### Slot B / module straight_top_with_fanlight
| emits | 描述 | 来源 |
|---|---|---|
| parts | 拱石 surround masonry + 固定 fanlight_grille（iron）+ fanlight_gold | parent `_stone_masonry` L94-L157；`_fanlight_grille` L177-L345；`_fanlight_gold` L348-L379 |
| internal joints | 无（全固定 parent visual） | — |
| upstream interface | 提供两个 jamb 立面给 REVOLUTE origin | parent L838-L866 |
| downstream interface | fanlight 与 masonry 拱接触 `expect_contact` | parent L963-L966 |

### Slot B / module flat_rail_head_no_fanlight
| emits | 描述 | 来源 |
|---|---|---|
| parts | 矩形 surround（pillar×2 + lintel）+ 平铁 top_rail（固定 parent visual） | rec_gate_var_flatrail `_rectangular_surround` L103-L138；`_top_rail` L141-L150 |
| internal joints | 无 | — |
| upstream interface | 两 pillar 内面给 REVOLUTE origin；PILLAR_H = lintel 下沿（L80） | L626-L645 |
| downstream interface | top_rail 贴 lintel 下沿、横跨净开口；无 fanlight | L144-L149 |

### Slot B / module spear_pointed_tops
| emits | 描述 | 来源 |
|---|---|---|
| parts | leaf 内 picket 伸出顶 rail + 每 picket 顶 finial（回转体），熔进 leaf visual；surround 无 fanlight | rec_gate_var_speartop `_spear_finial` L270-L293；finial loop L370-L373 |
| internal joints | 无 | — |
| upstream interface | picket 顶 = `z1 + PICKET_EXT`；finial 基座坐在 picket 顶 | L356-L373 |
| downstream interface | 开放矛尖头（无 fanlight 也无 top_rail 封顶） | L369-L373 |

### Slot C / module plain_rails_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | 周框 + 横 rail（已含在 leaf iron visual 内） | parent `_leaf_iron` L500-L529 |
| internal joints | 无 | — |
| interfaces | frame 周边给 brace/infill 提供锚边 | L500-L513 |

### Slot C / module z_brace_diagonal
| emits | 描述 | 来源 |
|---|---|---|
| parts | 在 plain frame 之上叠一根对角 brace box（独立 visual `door_*_brace`） | rec_gate_var_zbrace `_z_brace` L790-L832；装配 L875-L877 |
| internal joints | 无 | — |
| upstream interface | brace 两端嵌入底-铰角 / 顶-闩角框中心（锚定接触） | L806-L811 |
| downstream interface | 随 leaf 一起转，与 leaf 同 part | L875-L877 |

### Slot D / module double_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0` + `door_1`（各 iron / gold / knuckles，C/A 可加 brace/kick visual） | parent L817-L834 |
| internal joints | `surround_to_door_0` REVOLUTE；`surround_to_door_1` REVOLUTE + Mimic 耦合 | parent L844-L866 |
| upstream interface | 两 jamb origin `(±(OPENING_W/2-JAMB_REVEAL),0,0)`，axis ±Z | L838-L865 |
| downstream interface | 中心 meeting，小 reveal gap（`expect_gap` -0.01..0.09） | run_tests L948-L951 |

### Slot D / module single_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gate_leaf`（iron / gold / knuckles / latch_handle），宽叶 + latch stile | rec_gate_var_single L768-L788；latch stile L490-L495 |
| internal joints | 单个 `surround_to_leaf` REVOLUTE（无 mimic） | L796-L804 |
| upstream interface | 一侧 jamb origin `(-(OPENING_W/2-JAMB_REVEAL),0,0)`，axis -Z | L791-L803 |
| downstream interface | 对侧 jamb 处 latch stile/handle 贴合 | L489-L495 / L703-L733 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `infill_style` (Slot A) | enum | ornamental_scroll_infill / vertical_picket_infill / panel_and_bar_infill | — | choice | deterministic procedural sampler | Slot A table |
| `top_profile` (Slot B) | enum | straight_top_with_fanlight / flat_rail_head_no_fanlight / spear_pointed_tops | — | choice | sampler；arched_cambered_top 不进 domain | Slot B table |
| `frame_style` (Slot C) | enum | plain_rails_frame / z_brace_diagonal | — | choice | sampler；ring_and_arch_brace 不进 domain | Slot C table |
| `leaf_count` (Slot D) | enum | double_leaf / single_leaf | — | choice | sampler；派生 N 语义与 mimic | Slot D table |
| `palette_style` | enum | black_wrought_iron / gold_capped_iron / galvanized_silver / painted_white / painted_green / verdigris_bronze | black_wrought_iron | choice | 仅重映射 `iron`/`gold`/`stone` material rgba，不改拓扑/几何 | 新增（5 星 material 统一，见摘要；parent `_materials` L81-L86） |
| `picket_count` (轴 N) | int | double: [5,11]（产品 [5,16]）；single: [10,22]（产品 [10,32]） | double 7 / single 14 | conditional | 上限随 Slot D：single ≈ 2×double（一叶覆盖全宽） | parent `N_BARS=7` L67；n5/n11；single `N_BARS=14` L62 |
| `leaf_width_scale` | float | [0.92, 1.06] | 1.0 | independent | clamp；缩放 `LEAF_W` | parent `LEAF_W=1.06` L51 |
| `leaf_height_scale` | float | [0.92, 1.10] | 1.0 | independent | clamp；缩放 `LEAF_H` | parent `LEAF_H=2.18` L52 |
| `frame_width_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 `FRAME_W` 周框/rail 宽 | parent `FRAME_W=0.075` L66 |
| `bar_thickness_scale` | float | [0.8, 1.4] | 1.0 | independent | clamp；缩放 `BAR_W` picket 截面 | parent `BAR_W=0.020` L66 |
| `open_angle` | float | [0.0, 1.92] rad | 0.0 (closed) | independent | REVOLUTE lower=0 upper≈1.92；展示姿态用 | parent MotionLimits L851 / L864 |
| (—) | constraint | — | — | inequality | `OPENING_W = 2*(LEAF_W+JAMB_REVEAL)+0.04`（double）/ `LEAF_W ≈ OPENING_W-2*JAMB_REVEAL`（single）；surround 开口必须随 leaf_width_scale 重算，违反则按比例回缩 | parent `OPENING_W` L55；single L47 |
| (—) | constraint | — | — | inequality | picket air-gap：`N*BAR_W*bar_thickness_scale ≤ 0.80 * usable`（usable=inner-2*FRAME_W）；超出按 N 上限或回缩 bar_thickness_scale | parent picket loop L536-L543 |
| (—) | constraint | — | — | conditional | panel_and_bar_infill 的 N 只计 bar 场（上 2/3）；kick 占下 1/3 不参与 picket-count 读数 | panelinfill L520-L543 |
| (—) | constraint | — | — | conditional | spear_pointed_tops：`PILLAR_H / lintel` 不得低于 `LEAF_H + PICKET_EXT + FINIAL_H`，否则 finial 穿 surround 头 | speartop L80-L85, L356-L373 |

参数说明：连续 scale 默认相互独立，仅 `OPENING_W`（随 leaf_width_scale）、picket air-gap、spear 头净空、kick/N 读数四条用 inequality/conditional 显式声明。所有约束在 `resolve_config` 求解后再交给 builder。

## Multiplicity / Copy Logic

本模板有 **1 根 multiplicity 轴**：picket/bar 竖元数量。

- `count_param`：`picket_count`（模板内即 `N_BARS`）。
- `N_range`：
  - **double_leaf**：每叶 [5, 11]（测试偏小）；产品全程 [5, 16]，>11 稀有。
  - **single_leaf**：跨全叶 [10, 22]（测试偏小）；产品全程 [10, 32]，>22 稀有。（单叶覆盖全开口 ≈2 倍宽，故同视觉密度需约 2× picket，源样本 single `N_BARS=14` vs double parent 7。）
- sampling domain（权重档）：小 N 高频（double 5–9 / single 10–18 占多数），大 N 稀有尾部下调权重；按 Slot D 选好后再对该轴做一次加权采样并 clamp。
- copied object：方截面竖直 picket / bar（`cq.box(BAR_W, t*0.7, bar_h)`）。
- naming：循环内联进 leaf iron visual（`door_0_iron` / `door_1_iron` / `leaf_iron`），不是 per-picket part；spear 模式额外 `for i in range(N)` 发射 finial 也内联进同一 leaf visual。
- placement：均布偶数间距，`u = FRAME_W + usable * (i + 0.5) / N`，每次按当前 N 重算（parent L537）；spear finial 复用同一 index 公式（speartop L361/L371）。
- joint policy：所有 picket/finial 复制件都是 **静态 leaf visual，无 per-picket joint**。模板里唯一非固定 joint 是 surround↔leaf 的 REVOLUTE：double=2 个（door_1 mimic-coupled 到 door_0、axis 取反），single=1 个（无 mimic）。**绝不可把铰改成 FIXED。**
- source/gating：parent N=7、n5、n11 三个 5 星样本给出真实 N 多样性；panel_and_bar 的 N 仅作用于 kick rail 之上的 bar 场。

## 拓扑多样性审计

总组合数（不含连续 scale）：
Slot A(3) × Slot B(3) × Slot C(2) × Slot D(2) = **36** 个 module 组合。
计入 multiplicity：double N∈{5..11}=7 distinct、single N∈{10..22}=13 distinct（各按 Slot D 选）；topology-equivalence 上以“slot 组合 × N 桶”计，约 36 个 slot 组合再叉乘若干 N 桶 ≫ 100。

理由：仅 A×D×B 最小子集 3×2×3=18 ≥ 10；加上 C 与 N 远超门槛。每个 slot 都有 ≥2 个真实 5 星来源候选。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed 做 deterministic procedural sampling：先按权重选 Slot A/B/C/D 四个 enum（`seed=0` 不特殊），再依 compatibility matrix 合法化（见下），然后对 picket_count 轴按 Slot D 解析 N_range 后做加权采样并 clamp，最后采 independent 连续 scale → 派生 → inequality 投影回缩。`slot_choices_for_seed` 返回 `(slot, module)` 列表（不含连续 scale，除非改变拓扑等价类）。无大型 curated/modulo 表作为主域；regression overrides = none（初版无已知失败回归；如出现再按 seed+原因稀疏添加）。
Topology target：1000-seed slot choice tuple distinct 按 ≥300 report-only 口径观察；36 slot 组合 × 多个 N 桶，低于 300 时记录离散空间或采样权重原因。
Controlled local parameterization：初版包含 `leaf_width_scale`、`leaf_height_scale`、`frame_width_scale`、`bar_thickness_scale`、`open_angle` 五个关键连续 scale（范围/约束见 §7），全部在 `resolve_config` clamp/派生；`OPENING_W` 随 leaf_width_scale 重算（inequality），picket air-gap 与 spear 净空亦在此求解，保证不破坏 surround↔leaf InterfaceSpec、铰 origin/axis、mimic 与 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先选 A/B/C/D 四 enum（加权）→ 解析 N_range（依 D）→ 加权采 N → independent scale → equation/inequality 投影 | `slot_choices_for_seed` 与实际 build 选择一致 |
| compatibility matrix | A×B×C×D 默认全兼容；硬规则：(1) B=flat_rail_head 与 B=spear 均**去 fanlight**、B=straight 才有 fanlight；(2) A=panel_and_bar 的下 1/3 实心 kick 与 B=spear（picket 须满高伸出）冲突 → gate 掉该组合（degrade 到 ornamental/picket）；(3) C=z_brace 叠加在任意 A 之上，但与 A=panel_and_bar 同框时 brace 须画在 kick 之上 panel；(4) D=single 时强制 latch stile/handle + 单 REVOLUTE 无 mimic；(5) N 上限随 D（single≈2×double） | no floating / no collision / 铰 axis 与 range / closed pose 不互穿 / fanlight-or-toprail 二选一齐备 / kick 下三分位 / spear 净空 |
| controlled local variation | 5 个 clamp 过的连续 scale + OPENING_W 重算 | 比例变化不破 surround↔leaf 接口、reveal gap、铰 origin、picket air-gap、类别 identity |
| regression overrides | none | 仅已知失败回归 / 审核指定样本时再加 |
| random sweep | seeds 0–49 初轮，0–999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A leaf infill | 3 | yes | yes | scroll / picket / panel+bar |
| B top profile | 3 | yes | yes | fanlight / flat-rail / spear（arched 不进 domain） |
| C framing/brace | 2 | yes | no | plain / z-brace（ring 不进 domain，已 ≥2） |
| D leaf count | 2 | yes | no | double(mimic) / single(latch) |
| N picket_count（multiplicity 轴） | 3 distinct 源 (5/7/11) | yes | yes | 连续整数轴，源覆盖 5/7/11；single 域加倍 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（A/B/C/D 各取候选表内值；不返回 arched_cambered_top / ring_and_arch_brace）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊
- compatibility matrix / gating 阻止非法组合（panel_and_bar × spear；fanlight 与 top_rail 二选一；N 上限随 D）
- regression overrides 稀疏且有理由（初版 none）
- 不靠小型 curated / modulo 表作主 seed domain
- 连续 scale（leaf_width/height、frame_width、bar_thickness、open_angle）全部 clamp，不破接口 / clearance / 铰 origin / multiplicity
- 跨部件 scale 依赖（OPENING_W=f(leaf_width_scale)、picket air-gap、spear 净空）在 `resolve_config` 求解，不留到 builder 失败
- 关键 InterfaceSpec / MatingContract 存在：surround↔leaf REVOLUTE 接触（hinge knuckle captured-pin，element-scoped allow_overlap）；double 中心 reveal gap；fanlight↔masonry 接触
- 关键 joint 类型/轴/range：REVOLUTE，axis ±Z，lower=0 upper≈1.92；double=2 铰 + mimic（door_1 axis 取反），single=1 铰无 mimic
- 复制对象遵循命名/placement：picket/bar/finial 内联进 leaf visual，均布 `u=FRAME_W+usable*(i+0.5)/N`

## Reject cases

- 把任一 REVOLUTE 铰改成 FIXED，或 double 缺少 `door_1` 对 `door_0` 的 Mimic（两叶不同步外摆）
- double 的 `door_1` 没把 axis 取反，导致正 q 一叶外摆一叶内摆（自穿模）
- picket 太密：`N*BAR_W*bar_thickness_scale > 0.80*usable`，infill 无真实空隙，退化成实心 Door
- 采到 panel_and_bar_infill × spear_pointed_tops（实心 kick 与满高伸出 picket 冲突）而未被 gate
- B=straight 却丢了 fanlight，或 B=flat/spear 仍挂 fanlight（头部 profile 与 surround 不自洽）
- leaf_width_scale 变了但 OPENING_W / surround 开口没随之重算，叶与 jamb 穿模或漂浮
- hinge knuckle 嵌入 jamb 未做 element-scoped allow_overlap，被判穿模失败
- single_leaf 缺 latch stile/handle，或仍残留 mimic / 第二个铰
- spear finial 顶超过 surround 头净空（穿 lintel / 拱）而未 gate

## 与相邻类别的边界

- 不该混入：**Door（实心门）**（理由：本类核心是 N 根 picket 透空 infill 场 + 真实可摆铰；实心遮挡门扇不属于 Gate，panelinfill 的实心区也只限下 1/3）。
- 不该混入：**Fence / Railing（栅栏围栏）**（理由：Fence 是不开合的连续静态 panel；Gate 必须有 REVOLUTE 铰、能摆开让出通道）。
- 不该混入：**Window grille / 格栅**（理由：fanlight 在本类只是 surround 上的固定 parent visual，不是独立可动结构，不能升格为主 slot）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | ornamental_scroll_infill + straight_top_with_fanlight + plain_rails_frame + double_leaf | rec_door_gate | leaf L482-L549 / surround L94-L157 / fanlight L177-L379 / 铰+mimic L844-L866 | 基线 part tree + 双叶 REVOLUTE + mimic + 拱 surround + fanlight + scroll infill + picket loop |
| S2 | A | vertical_picket_infill | rec_gate_var_plainbars | `_leaf_iron` L483-L535 | 纯竖栏满高 infill |
| S3 | A | panel_and_bar_infill | rec_gate_var_panelinfill | `_leaf_iron` L485-L549 / `_kick_panel` L714-L737 | 下 1/3 实心 kick + 上部 bar 场 |
| S4 | N | N=5 / N=11 | rec_gate_var_n5 / rec_gate_var_n11 | `N_BARS` L67 + picket loop | multiplicity N 多样性 |
| S5 | B | flat_rail_head_no_fanlight | rec_gate_var_flatrail | `_rectangular_surround` L103-L138 / `_top_rail` L141-L150 | 矩形 surround + 平铁顶 rail、去 fanlight |
| S6 | B | spear_pointed_tops | rec_gate_var_speartop | `_spear_finial` L270-L293 / finial loop L370-L373 | 矛尖 finial 头、picket 伸出、去 fanlight |
| S7 | C | z_brace_diagonal | rec_gate_var_zbrace | `_z_brace` L790-L832 | 对角 Z-brace |
| S8 | D | single_leaf | rec_gate_var_single | `gate_leaf` L768-L788 / `_leaf_iron()` L429-L497 / `surround_to_leaf` L796-L804 / `_latch_handle` L703-L733 | 单叶单铰 + latch |

## 模板实现备注（可选）

- leaf-local helper（`_leaf_iron`、`_leaf_scroll_iron`、`_scroll_panel_iron`、`_volute`、`_kick_panel`、`_z_brace`、`_spear_finial`）在所有变体里共用同一 hinge-edge-at-X=0 约定，可直接抽成 Slot A/C 的 module factory，按 sign 参数化（single 版去 sign）。
- `palette_style` 只重写 `_materials` 的 `iron`/`gold`/`stone` rgba 三元组（galvanized → 银灰 iron + 去 gold；painted_white/green → 彩色 iron；verdigris → 青铜 gold + 暗 iron）；几何与 visual 名不变。
- hinge knuckle 嵌 jamb 与 z_brace/kick/scroll 端点嵌 rail 都需 element-scoped `allow_overlap`（参 parent run_tests L886-L899），不可全局放开。
- B=flat_rail_head 与 B=spear 必须同时切换 surround factory（矩形 vs 拱）并禁用 fanlight，避免“拱 surround + 平叶头”不自洽组合。
- single_leaf 的 N_range 与 OPENING_W 处理与 double 不同（全宽单叶），实现时按 Slot D 分支解析。
