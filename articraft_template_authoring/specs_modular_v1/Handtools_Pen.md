# Handtools / Pen — Modular Spec

> 来源小类：`picture/Handtools/Pen`
> 上游 source map：`articraft_data/picture_expansion/template_source_maps/Handtools__Pen.md`
> **同步前置**：本 spec 当前引用的 `model.py:Lx-Ly` 来自上游 `articraft_data/data/records/` 已收敛样本；本仓库 `arti-template/data/records/` 里还未完成这批 Handtools/Pen 样本的正式 5★ sync。进入 TEMPLATE_AFTER_REVIEW 前，需要先做 P2 sync，把 parent + converged variants 同步进本仓库并写 `rating=5`。本 spec 的行号以当前上游文件为准。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pen` |
| template path | `agent/templates/Handtools_Pen.py` |
| stage | `SPEC_ONLY` |
| status | `drafted_from_source_map` |
| __modular__ | `True` |
| pattern | `parallel_children`（单 root barrel + 1 个主机构 child + 可选 clip child + 软 multiplicity grip 细节） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（2 parents + 7 single-axis fork variants） |
| read_count | 9 |
| read_scope | all converged samples listed in `Handtools__Pen.md` |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **S0 parent A** `rec_build-a-realistic-articulated-3d-model-of-a-pen-_20260609_163942_733176_1c47d9da`：银色金属 click-action retractable ballpoint，round lathed barrel + `windowed_clip` + `plunger`。提供基线 `click_plunger / round_lathe / windowed_clip / plain`。
- **S1 parent B** `rec_build-a-realistic-articulated-3d-model-of-a-pen-_20260609_200037_041760_bd7a9b72`：STABILO BOSS rounded-rect highlighter + pull-off cap。补齐 `rounded_rect / removable_pull_cap`。
- **S2** `rec_ht_pen_var_twist`：上部 `sleeve` 绕长轴旋转，提供 `twist_sleeve`。
- **S3** `rec_ht_pen_var_slider`：长槽 thumb slider，提供 `side_slider`。
- **S4** `rec_ht_pen_var_capped`：带铰接 cap，提供 `hinged_cap` 与一组 `ring_bands`。
- **S5** `rec_ht_pen_var_hex`：hex barrel + six `face_strip_{i}`，提供 `hex_prism / face_strips`。
- **S6** `rec_ht_pen_var_solidclip`：去 window 的实体 tapered clip，提供 `solid_clip`。
- **S7** `rec_ht_pen_var_noclip`：clipless 干净 collar + 4 个 `grip_ring_{i}`，提供 `no_clip / ring_bands`。
- **S8** `rec_ht_pen_var_grip`：waisted/bulged rubber grip zone + 6 个 `grip_ring_{i}`，提供 `contoured_rubber_grip`。

## 核心身份

Handtools/Pen 在这批样本里的稳定身份是：**单支手持书写工具**，细长杆状主体，前端是 ballpoint / nib，用户主机构用于“露出、推进、开启或闭合书写端”，而不是容器/套装/桌面摆件。
它与 `Stationary/Pen` 的主要边界不是“是否能写字”，而是**默认形态语义**：Handtools/Pen 这批来源以金属 ballpoint / mechanism-heavy body 为主，允许引入 supplementary rounded-rect capped marker 只为补齐结构词汇，不应让模板整体滑向“粗短荧光笔”身份。

不该混入：
- pencil / mechanical pencil：细芯推进或木杆石墨，机制与 nib 身份不同
- stylus / touch pen：无 ink tip / cap grammar
- pen holder / multi-pen set：多件容器，出“单支 pen”身份

## 槽位 + 候选模块表

### Slot A：actuation（主用户机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| click_plunger | parent A | `model.py:L154-L186`, `model.py:L228-L245` | eligible | `plunger` 沿 `-Z` PRISMATIC 下压，按钮缩入 barrel bore |
| twist_sleeve | `rec_ht_pen_var_twist` | `model.py:L97-L117`, `model.py:L271-L284` | eligible | 上部 `sleeve` 绕 `+Z` REVOLUTE，quarter-turn twist |
| side_slider | `rec_ht_pen_var_slider` | `model.py:L188-L228`, `model.py:L315-L328` | eligible | 侧向 thumb slider 在长槽里沿 `-Z` PRISMATIC 下滑 |
| hinged_cap | `rec_ht_pen_var_capped` | `model.py:L179-L242`, `model.py:L340-L353` | eligible | 铰接 cap 绕 `-Y` REVOLUTE 翻开 |
| removable_pull_cap | parent B | `model.py:L128-L171`, `model.py:L224-L234` | eligible | cap 沿 `+X` PRISMATIC 拔出，套住 nib |

> 降级说明：本类 actuation 已有 5 个真实收敛候选，足够作为主多样性轴；不再虚构“twist-cap / double-cap”等未在 Handtools source map 收敛的模块。

### Slot B：barrel_profile（主体截面 / 外形词汇）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_lathe | parent A | `model.py:L73-L96` | eligible | 经典 round lathed tapered barrel |
| hex_prism | `rec_ht_pen_var_hex` | `model.py:L83-L96`, `model.py:L126-L166` | eligible | 六边形 prism body + round conical nose |
| rounded_rect | parent B | `model.py:L71-L93` | eligible | rounded-rect highlighter style body + stepped collar |

### Slot C：pocket_clip

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| windowed_clip | parent A | `model.py:L99-L148` | eligible | spring blade + oval window + bridge + foot |
| solid_clip | `rec_ht_pen_var_solidclip` | `model.py:L100-L199` | eligible | 无 window 的 tapered solid clip，带 curl + ball foot |
| no_clip | `rec_ht_pen_var_noclip` | `model.py:L166-L218` | eligible | 无 `clip` part，clean collar |

### Slot D：grip_surface / surface detail

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain | parent A | `model.py:L73-L96` | eligible | smooth metal barrel，无额外 grip 特征 |
| contoured_rubber_grip | `rec_ht_pen_var_grip` | `model.py:L90-L171`, `model.py:L279-L295` | eligible | waisted / bulged / necked rubber grip 区 + 6 个 texture rings |
| ring_bands | `rec_ht_pen_var_noclip`, `rec_ht_pen_var_capped` | `model.py:L98-L125`, `model.py:L181-L189`; `model.py:L118-L131`, `model.py:L300-L309` | eligible | 沿轴等距 raised annular bands |
| face_strips | `rec_ht_pen_var_hex` | `model.py:L99-L121`, `model.py:L271-L288` | eligible | 六个面条形 grip strips，和 hex faces 一一对应 |

## 槽位图（slot graph）

```text
pattern: parallel_children

                   barrel (root)
        ┌────────────┼─────────────┬──────────────┐
        │            │             │              │
  actuation      pocket_clip   grip_surface   tip/nose
  (Slot A)       (Slot C)      (Slot D)       (derived with profile)
        │            │             │
    one active     fixed/none     inline repeated visuals
    mechanism      or fixed trim  or contour on barrel
```

接口约定：
- root 始终是 `barrel`
- 主机构 child 只有一个：`plunger` / `sleeve` / `slider` / `cap`
- `clip` 若存在，通常是独立 child 但 FIXED；`no_clip` 时整个 child 消失
- `grip_surface` 一律优先作为 `barrel.visual(...)` 内联，不额外制造无意义 FIXED joint

## 每槽位 Module Emits / Interfaces

### Slot A / click_plunger
- emits:
  - `plunger` child
  - `barrel_to_plunger` PRISMATIC
- interface:
  - barrel 顶部 bore 口
  - 轴向 `-Z`

### Slot A / twist_sleeve
- emits:
  - `sleeve` child
  - `barrel_to_sleeve` REVOLUTE
- interface:
  - seam 平面 `z = SEAM_Z`
  - 轴向 `+Z`

### Slot A / side_slider
- emits:
  - `slider` child
  - `barrel_to_slider` PRISMATIC
- interface:
  - barrel 侧槽顶端
  - 轴向 `-Z`

### Slot A / hinged_cap
- emits:
  - `cap` child
  - `barrel_to_cap` REVOLUTE
- interface:
  - nose-cone 顶侧 hinge lug
  - 横轴 `-Y`

### Slot A / removable_pull_cap
- emits:
  - `cap` child
  - `barrel_to_cap` PRISMATIC
- interface:
  - collar 前肩 + cap mouth
  - 轴向 `+X`

### Slot B / round_lathe
- emits:
  - lathed `barrel_body`
- interface:
  - top bore / seam / cap seat 都围绕圆截面展开

### Slot B / hex_prism
- emits:
  - `_hex_prism` body + round nose union
- interface:
  - 可承接 `click_plunger`
  - `face_strips` 可与 6 面耦合

### Slot B / rounded_rect
- emits:
  - rounded-rect body + stepped collar
- interface:
  - 与 `removable_pull_cap` 天然匹配

### Slot C / windowed_clip
- emits:
  - `clip` child with oval window

### Slot C / solid_clip
- emits:
  - `clip` child with tapered blade + curl + ball foot

### Slot C / no_clip
- emits:
  - no `clip` child

### Slot D / contoured_rubber_grip
- emits:
  - contoured grip silhouette in `barrel_body`
  - repeated `grip_ring_{i}` visuals

### Slot D / ring_bands
- emits:
  - repeated `grip_ring_{i}` visuals

### Slot D / face_strips
- emits:
  - repeated `face_strip_{i}` visuals

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 |
|---|---|---|---|---|---|
| actuation | enum | `{click_plunger, twist_sleeve, side_slider, hinged_cap, removable_pull_cap}` | `click_plunger` | choice | 主拓扑轴 |
| barrel_profile | enum | `{round_lathe, hex_prism, rounded_rect}` | `round_lathe` | choice | 与部分 grip / cap 兼容矩阵耦合 |
| pocket_clip | enum | `{windowed_clip, solid_clip, no_clip}` | `windowed_clip` | choice | `no_clip` 删除整个 child |
| grip_surface | enum | `{plain, contoured_rubber_grip, ring_bands, face_strips}` | `plain` | conditional | `face_strips` 仅对 `hex_prism` 有意义 |
| n_grip_bands | int | `[0, 8]` | `0` | conditional | `ring_bands` 时启用；样本覆盖 `4,5,6` |
| palette_style | enum | `{brushed_silver, graphite_black, navy_cap, charcoal_rubber}` | `brushed_silver` | choice | 每 seed 采样，避免单色池 |
| barrel_len_scale | float | `[0.92, 1.08]` | `1.0` | independent | 保持 pen 细长身份 |
| barrel_girth_scale | float | `[0.92, 1.08]` | `1.0` | independent | 不得把 pen 拉成 marker brick |
| actuation_travel_scale | float | `[0.9, 1.15]` | `1.0` | conditional | 缩放 plunger/slider/cap travel |
| grip_zone_scale | float | `[0.85, 1.15]` | `1.0` | conditional | ring/strip/grip zone 包络必须仍落在 barrel 可用区 |

## Multiplicity / Copy Logic

当前类没有“核心结构级”的自由 multiplicity 轴；可复制对象都属于 grip surface 的软重复逻辑：

- `ring_bands`
  - copied object: `grip_ring_{i}`
  - source:
    - `rec_ht_pen_var_noclip` `model.py:L181-L189`
    - `rec_ht_pen_var_capped` `model.py:L300-L309`
    - `rec_ht_pen_var_grip` `model.py:L279-L295`
  - naming: `grip_ring_{i}`
  - placement: 沿 `Z` 轴等距
  - joint policy: inline `barrel.visual(...)`
  - observed N: `4, 5, 6`

- `face_strips`
  - copied object: `face_strip_{i}`
  - source: `rec_ht_pen_var_hex` `model.py:L271-L288`
  - naming: `face_strip_{i}`
  - placement: `for i in range(6)`，通过 `rpy=(0,0,angle)` 均匀环绕
  - joint policy: inline `barrel.visual(...)`
  - observed N: `6`，并且与六边形面数强耦合

模板建议：
- `ring_bands` 可暴露 `n_grip_bands ∈ [0, 8]`
- `face_strips` 不暴露自由 N，固定跟 `hex_prism` facet count 绑定

## 拓扑多样性审计

离散组合上界：

- `actuation`: 5
- `barrel_profile`: 3
- `pocket_clip`: 3
- `grip_surface`: 4

理论乘积：`5 × 3 × 3 × 4 = 180`

兼容矩阵后仍显著高于门槛：
- `face_strips` 仅对 `hex_prism` 合法
- `rounded_rect` 最自然搭 `removable_pull_cap`
- `hinged_cap` / `removable_pull_cap` 需要 cap-compatible nose/collar grammar


## 兼容矩阵 / 排除项

- `face_strips` × 非 `hex_prism`：排除
- `rounded_rect` × `windowed_clip` / `solid_clip`：可做但需重新 author clip 接口面；v1 模板建议先降低采样权重
- `hinged_cap` × `click_plunger` / `side_slider` / `twist_sleeve`：互斥，主机构只能选一个
- `no_clip` 时不得再保留任何 `clip` part / `barrel_to_clip` FIXED joint
- 颜色、材质、轻微尺寸浮动都不是结构轴，不能当 fork 候选冒充 topology diversity

## palette_style 建议

模板阶段建议至少提供 4 组每-seed 采样色板：

- `brushed_silver`
  - 铝银 barrel + chrome clip/button
- `graphite_black`
  - 深灰 barrel + 黑色机构件
- `navy_cap`
  - 银色 body + navy cap / sleeve accent
- `charcoal_rubber`
  - 银色 body + 深色 grip / face strips

说明：
- `lime_highlighter` 虽来自 supplementary parent B，但会把整体身份拉向 Stationary/Pen，模板阶段不建议作为高频 palette_style

## reviewer notes

- 这份 spec 严格基于 `Handtools__Pen.md` 和 9 个收敛样本撰写，没有借用 `Stationary_Pen.md` 作为模块来源。
- supplementary parent B (`picture/Stationary/Pen/001.png`) 只用于补齐 `rounded_rect + removable_pull_cap` 结构格子；模板实现时需要对采样权重做 gating，避免整体风格偏离 Handtools/Pen 的金属 ballpoint 主身份。
- 下一阶段进入模板前，建议优先挑 2 个参考成熟模板：
  - 一个 root + 单主机构 child + 可选 trim child 的笔类/手工具模板
  - 一个带 soft multiplicity visuals 的模板
