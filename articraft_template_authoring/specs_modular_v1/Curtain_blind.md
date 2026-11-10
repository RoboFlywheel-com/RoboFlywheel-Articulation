# window_blind — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `window_blind` |
| 大类/小类 | `Curtain/blind`（window blinds） |
| source map | `<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Curtain__blind.md` |
| parent A (horizontal) | `rec_horizontal-wooden-venetian-blind-a-wooden-headra_20260611_160824_216734_cc3eb44b` — picture `picture/Curtain/blind/002.png`（002 = 横向 venetian） |
| parent B (vertical) | `rec_vertical-blinds-for-a-tall-window-a-long-extrude_20260611_160757_186286_2182787b` — picture `picture/Curtain/blind/001.png`（001 = 竖向 vanes） |
| template path | `agent/templates/Curtain_blind.py` |
| test path (optional) | `tests/agent/test_window_blind_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（headrail root + parallel shade panel；shade panel slot 内部 `multiplicity` 复制 slat/vane/fold/cell） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category（2 parents + 6 converged variants） |
| source_index_policy | only adopted module sources are indexed below |

读取的 8 个 5★ 样本（全部 `revisions/rev_000001/model.py`）：

| record_id | 角色 | name | 共享结构 | 关键差异 |
|---|---|---|---|---|
| `rec_horizontal-wooden-venetian-blind-...cc3eb44b` | parent A | `wooden_venetian_blind` | headrail(root) + bottom_rail lift driver + cord lock + pull cords + tassels | 30 块木 slat，每块 = invisible lift carrier（PRISMATIC，mimic `lift`，bottom-led 倍率）+ 木叶片（REVOLUTE `slat_tilt`，X 轴，±1.3 rad，followers 1:1 mimic）；两站 ladder tape（front+rear）+ tilt wand |
| `rec_vertical-blinds-for-a-tall-window-...2182787b` | parent B | `vertical_blinds` | headrail(root，挤铝长 channel) | 20 条 fabric vane 竖挂；单 `carrier_train`（PRISMATIC `vane_set_traverse`，X 轴 ±0.045）整体平移；每 vane `vane_NN_tilt`（REVOLUTE Z 轴 ±90°，followers 1:1 mimic `vane_01_tilt`）；左端 control chain（REVOLUTE swing）；**无 lift / 无 bottom rail** |
| `rec_blind_var_roller_shade` | variant | `roller_shade` | 复用 horizontal headrail + cord lock + pull cord/tassel | shade panel 改为 roller：CadQuery 空心 roller_tube（REVOLUTE `roller`，X 轴，0..2π）+ 单张 fabric sheet + bottom_bar（PRISMATIC `shade_lift`，Z，0..0.55，独立 driver）；**无 slat 复制、无 tilt** |
| `rec_blind_var_roman_folds` | variant | `roman_blind` | 复用 horizontal headrail + bottom_rail lift + cord lock + pull cords + tassels | shade panel 改为 6 块 roman fold（正弦凸起 mesh 面板）；每 fold = PRISMATIC `fold_lift_i`（mimic `lift`，bottom-led）；**无 tilt、无 ladder tape**（改 lift cord strips） |
| `rec_blind_var_cellular_honeycomb` | variant | `cellular_honeycomb_shade` | 复用 horizontal headrail + bottom_rail lift + cord lock + pull cords + tassels | shade panel 改为 30 个 honeycomb cell（六边形 ExtrudeGeometry，沿 X 挤出）；每 cell = PRISMATIC `cell_lift_i`（mimic `lift`，bottom-led）；**无 tilt**（改 cord guides） |
| `rec_blind_var_slat_count_12` | variant | `wooden_venetian_blind` | 与 parent A 完全同构 | 仅 `SLAT_COUNT=12`、`SLAT_DEPTH=0.080`、`SLAT_PITCH=0.100`（更宽更稀的 slat）；证明 slat_count 是纯 multiplicity 轴 |
| `rec_blind_var_slat_count_40` | variant | `wooden_venetian_blind` | 与 parent A 完全同构 | 仅 `SLAT_COUNT=40`、`SLAT_DEPTH=0.040`、`SLAT_PITCH=0.0283`（更窄更密）；multiplicity 轴另一端 |
| `rec_blind_var_center_split_vertical` | variant | `center_split_vertical_blinds` | 复用 vertical headrail + chain swing + vane tilt mimic | traverse 改为左右两 train（`left_traverse` −X / `right_traverse` +X，各 0..0.05），vanes 01-10 挂 left、11-20 挂 right，中间留 split 缝；证明 Slot C 的 split policy |

共同骨架（所有 8 个样本）：**一根 root `headrail`**，shade panel 挂在 headrail 之下并由 headrail 派生接口承载；控制件（cord/wand/chain）挂在 headrail 上。两个 parent 的 root 坐标与主运动 spine 不同（horizontal 家族 = 垂直 lift Z + slat tilt X；vertical 家族 = 水平 traverse X + vane tilt Z），是本类别两条兼容分支的根源。

## 核心身份

window_blind = 挂在一根 **headrail / track（root part）** 下、由 **重复的 slat / vane / fold / cell（shade panel）** 构成、可通过 **lift / tilt / traverse** 之一或组合操控开合的窗户遮光装置。它的身份三要素：

1. **headrail 是唯一 root**：所有结构与控制件最终挂回 headrail；shade panel 不直接落地，靠 headrail 派生的 lift carrier / carrier_train / roller bearing / 接口承载。
2. **shade panel 是重复同构子件构成的可动遮光层**：venetian = N 块横 slat（lift + tilt 双自由度），vertical = N 条竖 vane（traverse + tilt），roller = 单张卷帘（卷轴 + lift），roman = N 块软折（lift），cellular = N 个蜂窝（lift）。重复数量（slat/vane/fold/cell count）是类别的核心 multiplicity。
3. **真实开合运动**：horizontal 家族靠 `lift` PRISMATIC 把 bottom rail 抬起、shade 子件 bottom-led 收拢成 stack；vertical 家族靠 `traverse` PRISMATIC 平移 vane set + `tilt` REVOLUTE 转 vane 角度。控制件（pull cord + tassel / tilt wand / control chain）是 headrail 上的可见 driver 表征。

默认成熟域：家用窗户尺度（宽 0.8–1.6 m，drop 1.1–2.0 m），单 headrail，单遮光层。

不该混入：见 §11。

## 槽位 + 候选模块表

> 行号均来自 `data/records/<id>/revisions/rev_000001/model.py`，逐文件 AST/手工核对。

### Slot A：shade panel topology（遮光层拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| horizontal_venetian | rec_horizontal-wooden-venetian-blind-...cc3eb44b (parent A) | L110-L229（build）；slat 复制循环 L194-L227；lift driver L181-L189；tilt joint L218-L227 | eligible if compatible | N 块横木 slat，每块 = 隐形 lift carrier（PRISMATIC，mimic `lift`，bottom-led 倍率 L197-L208）+ 木叶片（REVOLUTE `slat_tilt`/`slat_tilt_NN`，X 轴 ±1.3，followers 1:1 mimic L218-L227）；两站 ladder tape L122-L132 |
| vertical_vanes | rec_vertical-blinds-for-a-tall-window-...2182787b (parent B) | L75-L221（build）；carrier_train L121-L151；vane 复制循环 L158-L186；vane tilt L174-L183 | eligible if compatible | N 条竖 fabric vane 挂在单 `carrier_train` 下；vane `vane_NN_tilt`（REVOLUTE Z 轴 ±90°，followers 1:1 mimic `vane_01_tilt` L174-L183）；**无 lift / 无 bottom rail**，靠 traverse 开合 |
| roller_shade | rec_blind_var_roller_shade | L130-L264（build）；roller_tube L178-L226；roller joint L216-L226；shade panel + bottom_bar L228-L262；mesh helpers L92-L127 | eligible if compatible | 单张卷帘：空心 `roller_tube`（REVOLUTE `roller`，X 轴 0..2π L216-L226）+ 单 fabric sheet（CadQuery mesh L108-L114）+ `bottom_bar`（PRISMATIC `shade_lift`，Z 0..0.55，**独立 driver** L252-L262）；**无 slat 复制、无 tilt** |
| roman_folds | rec_blind_var_roman_folds | L156-L257（build）；fold mesh helper `_roman_fold_panel` L103-L152；fold 复制循环 L229-L255 | eligible if compatible | N 块 roman fold（正弦凸起 mesh 面板 L103-L152）；每 fold = PRISMATIC `fold_lift_i`（mimic `lift`，bottom-led L242-L255）；**无 tilt**，ladder tape 改为 lift cord strips L168-L179 |
| cellular_honeycomb | rec_blind_var_cellular_honeycomb | L126-L219（build）；hex mesh helper `make_honeycomb_cell` L98-L122；cell 复制循环 L197-L217 | eligible if compatible | N 个蜂窝 cell（六边形 ExtrudeGeometry 沿 X 挤出 L98-L122，单 mesh asset 复用 L192-L195）；每 cell = PRISMATIC `cell_lift_i`（mimic `lift`，bottom-led L206-L217）；**无 tilt**，ladder tape 改为 cord guides L138-L147 |

Slot A 共 5 个结构不同的 candidate（≥3）。其中 venetian/roman/cellular 共享 horizontal headrail + `lift` PRISMATIC bottom-rail spine（同一 root 坐标与主运动）；vertical 用独立的 horizontal-traverse spine；roller 用单卷轴 + 独立 lift（无 bottom-led 复制）。

### Slot B：slat / vane count（遮光层 multiplicity）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| parent_count | parents（A: `SLAT_COUNT=30` L59；B: `VANE_COUNT=20` L38） | A L59 + 复制循环 L194-L227；B L38 + 复制循环 L158-L186 | eligible if compatible | 继承 parent 的 slat/vane 数量与 pitch；horizontal 30 块、vertical 20 条 |
| slat_count_12 | rec_blind_var_slat_count_12 | `SLAT_COUNT=12` L59；`SLAT_DEPTH=0.080` L57；`SLAT_PITCH=0.100` L60；复制循环 L194-L227 | eligible if compatible | 稀疏宽 slat（12 块，100 mm pitch）；纯 multiplicity 端点，结构与 parent A 完全同构 |
| slat_count_40 | rec_blind_var_slat_count_40 | `SLAT_COUNT=40` L59；`SLAT_DEPTH=0.040` L57；`SLAT_PITCH=0.0283` L60；复制循环 L194-L227 | eligible if compatible | 密窄 slat（40 块，28 mm pitch）；multiplicity 另一端，结构与 parent A 完全同构 |

Slot B 是 multiplicity 轴本体（详见 §8），不是离散拓扑 slot：它通过 `slat_count` / `vane_count` 在 `slat_{i}` / `vane_{i}` 复制循环上加权采样实现。三个 candidate（parent + 12 + 40）刻画的是**同一轴的不同采样点**，所以本 slot 用三行展示采样域端点，下游模板把它实现为一个连续整数 count_param（而非离散 enum）。**`slat_count` / `vane_count` 仅适用于 venetian / vertical 候选**；roller 无复制（单卷帘），roman / cellular 用各自的局部 `fold_count` / `cell_count`（见 §8 与 §9 兼容矩阵）。

### Slot C：traverse / split policy（开合/分裂策略）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_stack | parents（A 单 bottom_rail lift；B 单 `carrier_train` traverse） | A lift L181-L189；B `vane_set_traverse` L143-L151 | eligible if compatible | 一组连续遮光层在一根 headrail 下：horizontal = 单 lift stack 收拢；vertical = 单 `carrier_train` 整体平移 |
| center_split_vertical | rec_blind_var_center_split_vertical | `_build_carrier_train` L98-L121；`left_traverse`(−X) L172-L183；`right_traverse`(+X) L191-L202；vane→train 分配 L211-L245；split gap test L460-L468 | eligible if compatible | vertical vane set 分左右两 `carrier_train`，向中线两侧反向平移开合，中间留 split 缝；vanes 01-10 挂 left、11-20 挂 right，tilt 仍全部 1:1 mimic `vane_01_tilt` |

Slot C 共 2 个 candidate（≥2，已达硬下限）。`single_stack` 适用全部 5 个 Slot A 模块（horizontal lift / vertical single-train 各取一支）；`center_split_vertical` **只与 `vertical_vanes` 兼容**（依赖 carrier_train + 竖 vane 拓扑），见 §9 兼容矩阵。Slot C 仅 2 个 candidate 的降级理由：源样本只显式给出"单组"与"竖向中分"两种 split 策略；横向 venetian 的左右分裂在 5★ 样本中不存在，不发明结构。

## 槽位图（slot graph）

pattern: `mixed`（headrail root → parallel shade panel；shade panel slot 内部 multiplicity 复制）

```
                         headrail (root part)
                              │
        ┌─────────────────────┼───────────────────────────┐
        │ (always)            │ (Slot A 选 horizontal 家族)  │ (Slot A 选 vertical 家族)
   control widgets       lift PRISMATIC (Z)            traverse PRISMATIC (X)
   (cord/wand/chain,     ├─ bottom_rail (driver)        └─ carrier_train(s)  ← Slot C
    headrail visual)     └─ shade子件×N  ← Slot B           └─ vane_{i} ×N    ← Slot B
                            (slat/fold/cell carrier,           REVOLUTE vane_NN_tilt (Z)
                             PRISMATIC *_lift_i mimic `lift`)   followers mimic vane_01_tilt
                            venetian only: + slat REVOLUTE
                            slat_tilt (X) followers mimic
```

跨 slot 连接 / 接口点位：

- **headrail → shade panel（Slot A 主接口）**：
  - horizontal 家族（venetian / roman / cellular）：headrail 是 root，`lift` PRISMATIC（axis Z，origin `BOTTOM_RAIL_Z`，lower 0 / upper `RAIL_TRAVEL`）把 bottom_rail 当 master driver；每个 shade 子件经自己的 PRISMATIC `*_lift_i`（origin = 该子件 lowered Z，mimic `lift`，multiplier = `displacement_i / RAIL_TRAVEL`，bottom-led 单调递增）挂回 headrail。接口面 = headrail 底面 + 两站 ladder tape / cord strip / cord guide 提供视觉竖向支撑（slat 体侧穿 tape 0.5 mm 做 physical-contact）。
  - vertical 家族：headrail 是 root，`vane_set_traverse`（或 `left_traverse`/`right_traverse`）PRISMATIC（axis X，origin `RAIL_BOTTOM_Z`）把 carrier_train 挂在 rail 底面下方滑行；每条 vane 经 REVOLUTE `vane_NN_tilt`（parent = carrier_train，axis Z，origin = 该 vane 的 carrier stem 底）挂回 train。接口面 = rail 底面（carrier 顶贴合）+ carrier stem 底（vane hanger clip 贴合）。
  - roller：headrail root，`roller` REVOLUTE（axis X，origin `ROLLER_Z`，bearing 接触 headrail 底）+ `shade_lift` PRISMATIC（axis Z，独立 driver）；二者表征同一拉绳动作但 SDK 不支持跨类型 mimic，故并列两 driver。
- **shade panel 内部 multiplicity（Slot B）**：见 §8。
- **Slot C（single_stack vs center_split_vertical）**：派生自 Slot A 的 vertical 分支——single_stack 用一个 carrier_train + 一个 traverse；center_split 用左右两 train + 两个反向 traverse，vane→train 按 index 二分分配。horizontal 家族的 single_stack = 单 lift stack（无 split 对应物）。
- **control widgets**：始终是 headrail 的 child visual / REVOLUTE child（control_chain_swing），不改变 shade 拓扑。

互斥 / 派生关系：

- Slot C 的 `center_split_vertical` 与 Slot A 的 `vertical_vanes` **强绑定**（依赖 carrier_train + 竖 vane）；与其余 4 个 Slot A 模块互斥 → fallback 到 `single_stack`。
- Slot B 的 `slat_count`/`vane_count` 仅在 Slot A ∈ {venetian, vertical} 时是模板级 count_param；roller = 固定 1，roman/cellular = 局部 `fold_count`/`cell_count`（同样按 multiplicity 采样，但用各自的名字与 range）。

## 每槽位 Module Emits / Interfaces

### Slot A / module horizontal_venetian
| emits | 描述 | 来源 |
|---|---|---|
| parts | `headrail`(root, +ladder tapes/cord lock/cords/tassels/wand visuals)；`bottom_rail`；`slat_carrier_{i:02d}`(隐形)；`slat_{i:02d}`(木叶片) | cc3eb44b / L114-L227 |
| internal joints | `lift`(PRISMATIC, Z, 0..RAIL_TRAVEL, master)；`slat_lift_{i:02d}`(PRISMATIC, Z, mimic `lift`, bottom-led mult)；`slat_tilt`/`slat_tilt_{i:02d}`(REVOLUTE, X, ±1.3, follower mimic 1.0) | cc3eb44b / L181-L227 |
| upstream interface | headrail 为 root；bottom_rail/carrier 经 origin Z 挂到 headrail 底 | cc3eb44b / L181-L208 |
| downstream interface | ladder tape (front+rear @ ±0.20 X) 提供竖向支撑，slat 体穿 tape 0.5 mm；bottom_rail 升到 stack 下方 | cc3eb44b / L122-L132, L349-L416 |

### Slot A / module vertical_vanes
| emits | 描述 | 来源 |
|---|---|---|
| parts | `headrail`(root, 挤铝 channel + top_lip + end_caps + chain_boss)；`carrier_train`(spacer_rail + carrier_{i} + carrier_stem_{i})；`vane_{i:02d}`(hanger_clip + vane_strip)；`control_chain` | 2182787b / L88-L210 |
| internal joints | `vane_set_traverse`(PRISMATIC, X, ±0.045)；`vane_{i:02d}_tilt`(REVOLUTE, Z, ±90°, follower mimic `vane_01_tilt` 1.0)；`control_chain_swing`(REVOLUTE, X, ±0.25) | 2182787b / L143-L219 |
| upstream interface | headrail root；carrier_train 经 traverse origin 挂 rail 底面下 | 2182787b / L143-L151 |
| downstream interface | carrier stem 底 = vane pivot；vane hanger clip 贴 stem；闭合时相邻 vane_strip 侧向 overlap ≥10 mm（front/back stagger 防穿模） | 2182787b / L158-L186, L270-L281 |

### Slot A / module roller_shade
| emits | 描述 | 来源 |
|---|---|---|
| parts | `headrail`(root + brackets + cord lock + pull_cord + tassel)；`roller_tube`(空心 CadQuery shell + 端 bearing + wound ridge)；`bottom_bar`(weight + shade_panel sheet) | roller_shade / L134-L247 |
| internal joints | `roller`(REVOLUTE, X, 0..2π)；`shade_lift`(PRISMATIC, Z, 0..0.55, **独立 driver**) | roller_shade / L216-L262 |
| upstream interface | roller_tube bearing 接触 headrail 底；bottom_bar 经 shade_lift origin 挂 headrail | roller_shade / L216-L262, L401-L405 |
| downstream interface | shade sheet 顶到 headrail 底面（部署态）；bottom_bar 升起卷收 | roller_shade / L356-L362 |

### Slot A / module roman_folds
| emits | 描述 | 来源 |
|---|---|---|
| parts | `headrail`(root + lift cord strips + cord lock + pull cords + tassels)；`bottom_rail`；`fold_{i}`(正弦凸起 mesh 面板) | roman_folds / L160-L240 |
| internal joints | `lift`(PRISMATIC, Z, master)；`fold_lift_{i}`(PRISMATIC, Z, mimic `lift`, bottom-led) | roman_folds / L214-L255 |
| upstream interface | headrail root；bottom_rail/fold 经 origin Z 挂 headrail | roman_folds / L214-L255 |
| downstream interface | lift cord strips (@ ±0.20 X) 支撑，fold 穿 strip ~0.5 mm；fold 收拢成 stack | roman_folds / L168-L179, L366-L431 |

### Slot A / module cellular_honeycomb
| emits | 描述 | 来源 |
|---|---|---|
| parts | `headrail`(root + cord guides + cord lock + pull cords + tassels)；`bottom_rail`；`cell_{i:02d}`(六边形蜂窝 mesh，共享 asset) | cellular / L130-L217 |
| internal joints | `lift`(PRISMATIC, Z, master)；`cell_lift_{i:02d}`(PRISMATIC, Z, mimic `lift`, bottom-led) | cellular / L180-L217 |
| upstream interface | headrail root；cell 经 origin Z 挂 headrail | cellular / L206-L217 |
| downstream interface | cord guides (@ ±0.20 X) 支撑；cell 六边形截面 (depth>0.025, height>0.020) 收拢成 stack | cellular / L138-L147, L323-L389 |

### Slot C / module center_split_vertical（覆写 vertical 的 traverse）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_carrier_train`(vanes 01-10)；`right_carrier_train`(vanes 11-20)；其余同 vertical_vanes | center_split / L169-L189 |
| internal joints | `left_traverse`(PRISMATIC, −X, 0..0.05)；`right_traverse`(PRISMATIC, +X, 0..0.05)；vane tilt 不变 | center_split / L172-L202 |
| upstream interface | 两 train 各经 traverse origin 挂 rail 底面 | center_split / L172-L202 |
| downstream interface | 全开时两半中间留 ≥80 mm split 缝；同半内相邻 vane 仍 overlap ≥10 mm（跳过 10/11 中缝） | center_split / L357-L369, L460-L468 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `shade_topology` (Slot A) | enum | {horizontal_venetian, vertical_vanes, roller_shade, roman_folds, cellular_honeycomb} | — | choice | deterministic procedural sampler 选择 | Slot A table |
| `traverse_policy` (Slot C) | enum | {single_stack, center_split_vertical} | single_stack | conditional | `center_split_vertical` 仅当 `shade_topology=vertical_vanes`，否则强制 `single_stack` | center_split / L66-L67, L211-L245 |
| `slat_count` | int | [12, 40]（venetian only） | 30 | conditional | 仅 `shade_topology=venetian` 暴露；加权小 N 偏多；clamp `[12,40]` | slat_12 L59 / slat_40 L59 / parent A L59 |
| `vane_count` | int | [12, 28]（vertical only，建议域，超出 parent 20 需 viewer 复核） | 20 | conditional | 仅 vertical（含 split）暴露；clamp `[12,28]`；split 时须为偶数（左右平分） | parent B L38 |
| `fold_count` | int | [4, 9]（roman only，局部） | 6 | conditional | 仅 roman 暴露，独立于 `slat_count` | roman L47 |
| `cell_count` | int | [16, 40]（cellular only，局部） | 30 | conditional | 仅 cellular 暴露，独立于 `slat_count` | cellular L51 |
| `blind_width_scale` | float | [0.85, 1.20] | 1.0 | independent | 在范围内独立采样后 clamp；缩放 headrail/slat/vane 宽（X），不改拓扑 | A L55-L56 / B L46 |
| `drop_scale` | float | [0.80, 1.15] | 1.0 | independent | 缩放遮光层 drop（Z）；horizontal 重算 `RAIL_TRAVEL`，vertical 缩 `VANE_DROP` | A L107 / B L41 |
| `slat_pitch` | float | derived | — | equation | `= clamp(open_drop / (slat_count-1), STACK_PITCH+0.004, 0.105)`；不独立采样 | A L60, L89-L107 |
| `vane_pitch` | float | derived | — | equation | `= VANE_WIDTH − overlap`（保 ≥10 mm 侧向 overlap），随 `vane_count` 与 rail 长派生 | B L42, L62-L67 |
| `tilt_limit` | float | venetian 1.3 / vertical 1.5708 | — | conditional | 由 `shade_topology` 决定（横 slat ±1.3，竖 vane ±90°） | A L81 / B L53 |
| (—) | constraint | — | — | inequality | horizontal：`RAIL_UP_Z`(收拢 stack) ≤ headrail 底；`RAIL_TRAVEL>0.3`；各 `slat_lift` mult ∈(0,1] 且单调递增（bottom-led） | A L106-L107, L296-L313 |
| (—) | constraint | — | — | inequality | vertical：最外 vane 边 + `TRAVERSE_LIMIT` ≤ rail 端 cap（不滑出 rail）；闭合相邻 vane overlap ≥10 mm | B L62, L280-L281 / center_split L65-L67 |
| (—) | constraint | — | — | inequality | center_split：`vane_count` 偶数且左右各 `vane_count/2`；全开 split 缝 ≥80 mm | center_split L43-L46, L460-L468 |
| `palette_style` | enum | {wood_dark, wood_natural, white_pvc, grey_fabric, cream_cellular}（≥3，见 §palette） | wood_dark | choice | 每 seed 采样一组 material rgba；与 `shade_topology` 软关联（roller/roman/cellular 偏 fabric/pvc） | 见 palette 节 |

### palette_style 颜色集（≥3，实测自 5★ 源）

| style | headrail/rail | shade(slat/vane/fold/cell) | accent(tape/cord/tassel) | 出处 |
|---|---|---|---|---|
| `wood_dark` | dark_wood_rail (0.20,0.135,0.09) | dark_wood (0.23,0.155,0.105) | tape_tan (0.72,0.60,0.44) / cord_tan (0.66,0.55,0.40) | parent A / cellular L83-L86, L70-L73 |
| `wood_natural` | headrail_wood (0.55,0.42,0.30) | fabric_cream (0.93,0.89,0.82) | cord_ivory (0.88,0.82,0.72) / tassel_wood (0.52,0.40,0.28) | roman L94-L99 |
| `white_pvc` | headrail_wood (0.38,0.24,0.15) + bracket_metal (0.50,0.50,0.53) | shade_fabric (0.93,0.89,0.82) | roller_metal (0.62,0.62,0.65) / cord_tan | roller L83-L89 |
| `grey_fabric` | extruded_aluminum (0.78,0.79,0.80) | gray_vane_fabric (0.45,0.45,0.46) | chain_silver (0.72,0.73,0.74) / tassel_black (0.05,0.05,0.055) | parent B L78-L82 |
| `cream_cellular` | dark_wood_rail (0.20,0.135,0.09) | fabric_cream (0.91,0.86,0.76) | cord_tan (0.66,0.55,0.40) | cellular L70-L73 |

## Multiplicity / Copy Logic

本类别有 **1 根主 multiplicity 轴**（shade panel 重复子件数），但因 Slot A 拓扑不同，其 `count_param`、命名、joint policy 随所选模块而变（conditional 轴）。center_split 在 vertical 分支额外引入一个固定的 `side_count=2`（不采样）。

### 轴 1：shade panel 子件数（主轴，conditional 命名）

- **count_param**：
  - `shade_topology=horizontal_venetian` → `slat_count`
  - `shade_topology=vertical_vanes`（含 center_split）→ `vane_count`
  - `shade_topology=roman_folds` → `fold_count`（局部）
  - `shade_topology=cellular_honeycomb` → `cell_count`（局部）
  - `shade_topology=roller_shade` → 固定 1（单卷帘，无复制）
- **N_range（本小类本轴的产品域；测试偏小、产品全程）**：
  - slat_count：测试偏小 [12, 30]，产品全程 **[12, 40]**（5★ 端点 12 与 40 已实测；40 为高密上限）。
  - vane_count：测试 [12, 20]，产品 **[12, 28]**（parent=20 实测；>28 需 viewer 复核 rail 长足够）。
  - fold_count：**[4, 9]**（parent=6 实测）。
  - cell_count：**[16, 40]**（parent=30 实测）。
- **sampling domain（权重档：小 N 高频、大 N 稀有）**：在各 range 内做加权整数采样——以标称默认（30/20/6/30）为中心、向小 N 偏多；高密尾部（slat 40 / cell 40 / vane 28）稀有抽到。venetian split=2 时 `slat_count` 不适用（split 仅 vertical）。
- **copied object**：
  - venetian：每 i → `slat_carrier_{i:02d}`(隐形 lift 级) + `slat_{i:02d}`(木叶片)。
  - vertical：每 i → `vane_{i:02d}`(hanger_clip + vane_strip) + 对应 carrier truck/stem。
  - roman：每 i → `fold_{i}`(mesh 面板)。
  - cellular：每 i → `cell_{i:02d}`(共享 hex mesh asset 实例)。
- **naming**：`slat_{i:02d}` / `vane_{i:02d}` / `fold_{i}` / `cell_{i:02d}`，1-based，自上而下（vertical 自左向右）。
- **placement**：等 pitch。horizontal lowered Z = `TOP_*_Z − (i−1)·pitch`；vertical X = `FIRST_VANE_X + (i−1)·VANE_PITCH`（center 对称）。
- **joint policy**：
  - horizontal（venetian/roman/cellular）：每子件一根 PRISMATIC `*_lift_{i}`，mimic master `lift`，multiplier = `displacement_i / RAIL_TRAVEL`（bottom-led 严格单调递增，∈(0,1]）；venetian 额外每 slat 一根 REVOLUTE `slat_tilt_{i}` follower mimic `slat_tilt` 1.0。
  - vertical：每 vane 一根 REVOLUTE `vane_{i:02d}_tilt`，follower（i≥2）mimic `vane_01_tilt` 1.0；i=1 为 driver。traverse 是 carrier_train 级单关节（非每子件）。
- **source/gating**：parent A L194-L227 / parent B L158-L186 / roman L229-L255 / cellular L197-L217 / slat_12 L59 / slat_40 L59；gating 见 §9 兼容矩阵。

### 轴 2：vertical split side_count（固定，不采样）

- center_split_vertical 引入 `side_count=2`（左右两 carrier_train），是 Slot C 的拓扑选择而非采样轴；single_stack 时 side_count=1。固定值，不进入加权采样。来源 center_split L43-L46, L66-L67。

## 拓扑多样性审计

总组合数（拓扑等价类，不含连续 scale）：

```
Slot A(5) × 适配的 Slot C × Slot B 采样档
= horizontal_venetian × single_stack × slat_count{12,...,40 加权≈4 档} = 4
+ vertical_vanes × {single_stack, center_split} × vane_count{4 档}      = 8
+ roller_shade × single_stack × {1}                                     = 1
+ roman_folds × single_stack × fold_count{3 档}                         = 3
+ cellular_honeycomb × single_stack × cell_count{3 档}                  = 3
≈ 19 distinct 拓扑（仅按"模块+count 档"粗算；含 count 细化与 palette 时远大于此）
```

理由：5 个结构不同的 Slot A 模块本身就给出 5 个不同 part-tree / joint-topology（lift+tilt 双轴 / traverse+tilt / roller+lift / lift-only mesh-fold / lift-only hex-cell），再叠加 Slot C 的 vertical split 分支与多档 count，粗算 ≈19 distinct 拓扑等价类，已超 10。即使把 count 视为同一拓扑、仅数模块×split，也有 5+1=6 个纯拓扑 + venetian/vertical 的 count 变化使叶节点数突变（slat/vane part 数随 N 变），足够把 distinct 推过 10。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic procedural sampling——先 `ctx.rng` 加权选 `shade_topology`（5 选 1，可对常见的 venetian/vertical 略加权），再按 §9 兼容矩阵解析 Slot C（仅 vertical 允许 center_split，且 split 时 `vane_count` 取偶数）与 count_param（按 conditional range 加权小 N），最后采 `blind_width_scale`/`drop_scale` 等 independent scale 并 clamp、派生 pitch、用 inequality 投影到可行域。`seed=0` 不特殊。少量 regression override 仅用于已知失败回归（暂无）。random sweep：seeds 0-49 初版、0-999 成熟审计；viewer 目检覆盖每个 Slot A 模块各 1 个 + center_split 1 个。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别离散等价类受限于 5 模块 ×2 split，主要靠 count_param（slat 12-40 / vane 12-28 / fold 4-9 / cell 16-40）与 part 数突变拉开 distinct。低于 300 时说明类别拓扑天然受限（窗帘只有有限几种遮光层机构），palette 只补视觉多样性；不设门。

Controlled local parameterization：初版应含 `blind_width_scale`[0.85,1.20]、`drop_scale`[0.80,1.15]（均 independent，clamp）；派生 `slat_pitch`/`vane_pitch`（equation，随 count 与 drop）；inequality 保证（a）horizontal 收拢 stack 顶 ≤ headrail 底且 `RAIL_TRAVEL>0.3`、lift mult 单调；（b）vertical 最外 vane + traverse ≤ rail 端、闭合 overlap ≥10 mm；（c）split 时 vane_count 偶数、全开缝 ≥80 mm。这些 scale 只改安全比例/clearance，不改 InterfaceSpec（headrail root + lift/traverse/tilt 接口）、不改 multiplicity 语义。所有 equation/inequality/conditional 在 `resolve_config` 内求解。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先选 Slot A（加权 5 选 1）→ 解析 Slot C（conditional：仅 vertical 可 split）→ 解析 count_param（conditional range 加权小 N）→ 采 width/drop scale → 派生 pitch → inequality 投影 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | center_split↔vertical 强绑定，其余 fallback single_stack；slat_count 仅 venetian、vane_count 仅 vertical、fold/cell_count 各自局部；roller 固定单帘 | 无 floating / collision / 轴错 / 闭合穿模 / 超 multiplicity / split 缝过小 |
| controlled local variation | width_scale / drop_scale independent + clamp；pitch derived | 比例变化不破坏 lift/traverse/tilt 接口、clearance、stack 收拢、split 缝、类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初版，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A shade panel topology | 5 | yes | yes | venetian/vertical/roller/roman/cellular |
| B slat/vane count（multiplicity 轴） | 3（采样端点 parent/12/40） | yes | yes | 实现为 conditional 连续 count_param，非离散 enum |
| C traverse/split policy | 2 | yes | no | 降级理由：5★ 仅给单组与竖向中分；横向左右分裂无源，不发明 |

## Validator

- `slot_choices_for_seed` returns implemented module names（shade_topology + traverse_policy + count_param 值）
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：center_split 仅 vertical；slat_count 仅 venetian；vane_count 仅 vertical；roller 固定单帘；split 时 vane_count 偶数
- optional regression overrides 暂无；不用 curated/modulo 表当主 seed domain
- controlled local scale（width/drop）clamped；pitch derived；不破坏接口/clearance/joint origin/multiplicity
- cross-part scale 依赖（pitch=equation、stack/overlap/split=inequality、count_range=conditional）在 `resolve_config` 解析，不留到 builder 才失败
- 关键 InterfaceSpec/MatingContract：headrail root；horizontal lift PRISMATIC(Z) + slat_lift mimic；venetian slat_tilt REVOLUTE(X) follower mimic；vertical traverse PRISMATIC(X) + vane_tilt REVOLUTE(Z) follower mimic；roller REVOLUTE(X) + shade_lift PRISMATIC(Z) 独立
- key joints type/axis/range：lift Z 0..RAIL_TRAVEL；slat_tilt X ±1.3；vane_tilt Z ±1.5708；traverse X；roller X 0..2π
- copied objects 命名/布局：`slat_{i:02d}`/`vane_{i:02d}`/`fold_{i}`/`cell_{i:02d}` 等 pitch，lift mult bottom-led 单调

## Reject cases

- shade panel 直接落地或悬空（未经 headrail 派生的 lift carrier / carrier_train / bearing 承载 root）。
- horizontal 收拢态 stack 顶部高于 headrail 底（穿过 headrail）或 `RAIL_TRAVEL ≤ 0.3`（行程不足）。
- `slat_lift` / `fold_lift` / `cell_lift` 的 multiplier 非 bottom-led 单调递增、或越界 (0,1]，导致下层穿入上层。
- 把 `slat_count` 用在 roller（应单帘）或把 `center_split` 用在非 vertical 模块（缺 carrier_train，必崩）。
- vertical 闭合态相邻 vane 侧向 overlap <10 mm（漏光/穿模），或 traverse 把最外 vane 滑出 rail 端 cap。
- center_split 全开缝 <80 mm（看不出中分）或 vane_count 为奇数（左右无法平分）。
- venetian slat_tilt 轴错配成 Z（应为长边 X）、或 vertical vane_tilt 轴错配成 X（应为竖 Z）。
- follower tilt joint 未 mimic driver（multiplier≠1.0 或 offset≠0），各 slat/vane 不同步。
- roller 把 `roller` 与 `shade_lift` 错配成跨类型 mimic（SDK 不支持，应并列两独立 driver）。

## 与相邻类别的边界

- 不该混入：**Curtain/curtain（布帘 / 窗帘布）**——窗帘是连续织物 + 挂环沿单 track 滑动、无重复刚性 slat/vane 也无 tilt 自由度；blind 的身份在于重复遮光子件 + lift/tilt/traverse 机构，二者 part-tree 与 joint 拓扑不同。
- 不该混入：**Door/shutter（百叶门 / 木百叶窗）**——shutter 的百叶嵌在刚性门框内、整框靠铰链开合，slat 通常固定或单棒联动且框是承重 root；blind 无门框，靠 headrail 悬挂、子件靠 cord/track 而非门框。
- 不该混入：**Equipment/roller_door 或卷帘门**——工业卷帘门是落地刚性帘片沿侧轨升降的门，不是窗户遮光的软帘 + headrail 机构。
- 不该混入：**Awning / 遮阳篷**——外置斜伸出墙的遮阳结构，有伸缩臂与倾斜面，非室内窗 headrail 垂挂遮光层。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 1) Slot C 仅 2 candidate（已说明降级理由：5★ 无横向左右分裂源）。2) Slot B 是 conditional multiplicity 轴（命名随 Slot A 变：slat/vane/fold/cell count），下游须按所选模块解析 count_param 与 range。3) vane_count 产品域上限 28 为建议值，>20 需 viewer 复核 rail 长。4) roller 为固定单帘（无复制）。请确认 N_range 与权重档。 |

## 模板实现备注（可选）

- horizontal 三模块（venetian/roman/cellular）共享 headrail + bottom_rail + `lift` master PRISMATIC + bottom-led mimic helper（`displacement_i / RAIL_TRAVEL`）；差异仅在 shade 子件几何（Box slat / 正弦 mesh fold / hex ExtrudeGeometry cell）与是否带 tilt（仅 venetian）。可抽一个 `build_horizontal_lift_stack(子件工厂, count, pitch, with_tilt)` helper。
- vertical 两 Slot C 分支共享 vane 工厂与 tilt mimic；single_stack=1 train、center_split=2 train（vane→train 按 index 二分，origin 不变，仅 traverse 轴方向 ±X 与 limit 不同）。
- roller 的 `roller` REVOLUTE 与 `shade_lift` PRISMATIC 必须并列两独立 driver（SDK 不支持跨类型 mimic）；不要试图用 mimic 绑定。
- captured/embed overlap：ladder tape / cord strip / cord guide 与 slat/fold/cell 的 0.5 mm 体穿，闭合 vane 的 front/back stagger overlap，center_split 同半 vane overlap，均需 element-scoped allow_overlap 局部声明（mirror 各源样本的 expect_overlap/expect_contact）。
- mesh asset 复用：cellular 的 hex cell 是单 mesh asset 被 N 个 visual 复用（cellular L192-L195），N 大时务必复用以控编译成本（参考 container_locker PerforatedPanel mesh-cache 经验）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | horizontal_venetian | rec_horizontal-wooden-venetian-blind-...cc3eb44b | L110-L229（slat loop L194-L227, lift L181-L189, tilt L218-L227） | headrail root + lift+tilt 双轴 spine + bottom-led mimic |
| S2 | A | vertical_vanes | rec_vertical-blinds-for-a-tall-window-...2182787b | L75-L221（carrier_train L121-L151, traverse L143-L151, vane L158-L186） | headrail root + traverse+tilt spine + vane mimic |
| S3 | A | roller_shade | rec_blind_var_roller_shade | L130-L264（roller L216-L226, shade_lift L252-L262, mesh L92-L127） | 单卷帘 roller REVOLUTE + 独立 lift |
| S4 | A | roman_folds | rec_blind_var_roman_folds | L156-L257（fold helper L103-L152, loop L229-L255） | lift-only 软折 mesh stack |
| S5 | A | cellular_honeycomb | rec_blind_var_cellular_honeycomb | L126-L219（hex helper L98-L122, loop L197-L217） | lift-only hex-cell stack + 共享 mesh asset |
| S6 | B | slat_count_12 | rec_blind_var_slat_count_12 | L59（SLAT_COUNT=12）+ loop L194-L227 | multiplicity 轴低端点（稀疏宽 slat） |
| S7 | B | slat_count_40 | rec_blind_var_slat_count_40 | L59（SLAT_COUNT=40）+ loop L194-L227 | multiplicity 轴高端点（密窄 slat） |
| S8 | C | center_split_vertical | rec_blind_var_center_split_vertical | L98-L121, L172-L202, L211-L245, L460-L468 | vertical 左右两 train 反向 traverse + split 缝 |
