# Modular Spec - freestanding_security_safe

## 元信息
| 项 | 值 |
|---|---|
| slug | `freestanding_security_safe` |
| template path | `agent/templates/Others_Safe.py` |
| test path (optional) | `tests/agent/test_freestanding_security_safe_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：核心是 freestanding box body → 右侧 vertical-axis REVOLUTE hinge → door 的 serial spine；door 面上**并联**挂载 lock_entry（dial / keypad）与 turn_handle（wheel / tbar / lever）两个旋转控件；door 自由边由一个 PRISMATIC bolt carriage（N 根 locking bolt 的 multiplicity 复制）锁入 body latch 壁；body 内部有可选 interior 层（shelf / drawer）与可选 base 层（feet / plinth）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | parent `compact_security_safe` + 10 single-axis fork variants (Others/Safe pool)；读 `model.py` / `record.json` / `prompt.txt` / Others__Safe source map |
| source_index_policy | only adopted module sources are indexed below |

来源记录:
- parent: `rec_model-a-compact-freestanding-security-safe-about_20260610_085143_253768_86c0d4c8` ← picture/Others/Safe/001.png
- variants: `rec_safe_var_{tbar_handle,lever_handle,keypad,dual_dial,no_shelf,inner_drawer,leveling_feet,plinth_base,two_bolts,five_bolts}`

全量阅读后的真实结构轴:

| 轴 | 观察到的真实结构变体 |
|---|---|
| turn_handle | four-spoke handwheel(parent)/ 单根水平 T-bar 把手 / 单根下摆 lever 把手 |
| lock_entry | rotary combination dial(parent)/ electronic keypad(12 按键)/ dual stacked dials |
| interior | 单层水平 shelf(parent)/ 无 shelf 单腔 / 前拉 cash drawer(prismatic) |
| base | flush 平底落地(parent)/ 四角 leveling feet / 抬高 plinth skirt 座 |
| bolt multiplicity | N 根 locking bolt(parent N=3;变体 N=2 / N=5) |

## 核心身份

`freestanding_security_safe` 是落地式（freestanding）金属保险箱：固定的 hollow thick-walled box body（后/左/右/顶/底壁 + 前开口）提供箱体与铰链承载；一块厚 door 通过右侧 vertical-axis REVOLUTE `door_hinge`（0→~120° 向外开）启闭；door 自由边由一个 PRISMATIC `bolt_carriage` 上的 N 根 locking bolt 锁入 latch 壁的 strike pockets；door 外面并联至少一个 lock_entry 控件（rotary dial 或 electronic keypad）与一个 turn_handle（手轮 / T-bar / lever），均绕 door-normal 轴转动。可选 interior 层（shelf / cash drawer）与可选 base 层（feet / plinth）。

核心身份不是：嵌墙式 wall-recessed 保险箱（本类是落地独立箱体，自带完整六面壁与底座）、普通柜门 cabinet、无锁机的收纳箱、保险柜以外的金库门。成熟模板必须保持 closed pose：door 贴合 body 开口、留真实 latch-side jamb gap，bolt 在 rest pose 穿过 gap 坐进 strike pocket；dial/keypad/handle 坐在 door 真实 boss/housing 上；hinge origin 落在可见 knuckle stack 上。

## 槽位 + 候选模块表

### Slot A：turn_handle（门面转动锁控机构；主机构槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| four_spoke_wheel | rec_model-a-compact-freestanding-security-safe-about_20260610_085143_253768_86c0d4c8 | L294-L323 | eligible if compatible | `handle_wheel` part：hub + hub_cap + `spoke_{i}`×4 + `spoke_knob_{i}`×4（for-range(4) 循环）；`handle_spin` REVOLUTE door-normal ±90°，坐 `handle_boss` |
| tbar_handle | rec_safe_var_tbar_handle | L295-L325 | eligible if compatible | `tbar_handle` part：中央 hub + 单根水平 `cross_bar` + 两端 knob；`handle_spin` REVOLUTE |
| lever_handle | rec_safe_var_lever_handle | L296-L327 | eligible if compatible | `handle_lever` part：hub + 单根 `lever_arm` + grip 端；`handle_spin` REVOLUTE 0→90° |

### Slot B：lock_entry（组合/密码输入界面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rotary_dial | rec_model-a-compact-freestanding-security-safe-about_20260610_085143_253768_86c0d4c8 | L252-L290 | eligible if compatible | `combination_dial` part：`dial_ring` + KnobGeometry `dial_knob` + `dial_tick_{i}`×12；`dial_spin` CONTINUOUS；door 面 `dial_boss` + `dial_index_mark` |
| electronic_keypad | rec_safe_var_keypad | L110-L127, L249-L340 | eligible if compatible | door visuals `keypad_housing` + `keypad_display` + `_button_geometry()` helper + `button_{i}`×12（3×4，各自 PRISMATIC 短行程按压）；无 rotary dial（`dial_spin` 拓扑缺省） |
| dual_rotary_dial | rec_safe_var_dual_dial | L91-L130, L300-L370 | eligible if compatible | `_build_dial(model, dial_index)` helper → `combination_dial_{i}`×2 + `dial_spin_{i}`×2 CONTINUOUS（for-range(2) 上下叠放） |

### Slot C：interior_layout（内胆/分层结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_shelf | rec_model-a-compact-freestanding-security-safe-about_20260610_085143_253768_86c0d4c8 | L134-L178 | eligible if compatible | `shelf` visual（嵌两侧壁，分上下两舱）+ floor/shelf `gold_ingot_{i}` 循环 props |
| no_shelf | rec_safe_var_no_shelf | L134-L162 | eligible if compatible | 去 shelf，单一开放内腔；`gold_ingot_{i}` 单层堆于箱底 |
| pull_out_drawer | rec_safe_var_inner_drawer | L90-L107, L148-L200 | eligible if compatible | `cash_drawer` part（front/base/side/back 壁，`_drawer_tray_mesh`）+ body 内 `runner` 固定承轨；`drawer_slide` PRISMATIC +X door-normal |

### Slot D：base_stance（底座/支撑形式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_bottom | rec_model-a-compact-freestanding-security-safe-about_20260610_085143_253768_86c0d4c8 | L122-L133 | eligible if compatible | `bottom_wall` 直接落地，无独立底座件（inline body visual） |
| leveling_feet | rec_safe_var_leveling_feet | L94-L103, L199-L215 | eligible if compatible | `_leveling_foot_mesh` helper + `foot_{i}`×4 四角短圆柱（for-range 循环，inline body visuals） |
| plinth_base | rec_safe_var_plinth_base | L36-L38, L147-L185 | eligible if compatible | 抬高 `plinth` skirt（四面 inset 裙板，inline body visuals）；body 抬升 PLINTH_H≈0.045 |

> 每个 slot 均 ≥3 candidates（含 parent 基线），无单 candidate slot。

## 槽位图（slot graph）

pattern: mixed

```
safe_body(Slot C interior 内嵌 + Slot D base 内嵌)
   |-- door_hinge [REVOLUTE axis=(0,0,1) @右侧 knuckle stack, lower=0 upper=2.094] --> door
   |                                                                                     |-- handle_spin [REVOLUTE axis=door-normal @handle_boss] --> Slot A turn_handle
   |                                                                                     |-- dial_spin  [CONTINUOUS axis=door-normal @dial_boss]  --> Slot B lock_entry(rotary/dual;keypad 时缺省此 joint,改为 button_{i} 各 PRISMATIC)
   |                                                                                     |-- bolt_slide [PRISMATIC axis=(0,-1,0) @door 自由边] --> bolt_carriage(Slot 多 bolt N)
```

接口说明:
- **door 面 = Slot A + Slot B 的共享 mating face**：handle_boss / dial_boss(或 keypad_housing)均为 door 上真实 raised 接触面，joint origin 贴 boss 外表面，公共轴 = door-normal。两控件并联、互不依赖。
- **door 自由边 ↔ body latch 壁**：bolt rest pose 跨 jamb gap 进 strike pocket；bolt N 变化时 latch 壁 pocket 数必须同步（pocket 由同一 `BOLT_ZS` 列表循环钻孔）。
- **body 底面 ↔ Slot D base**：floor 接触面；feet/plinth 为 inline body visuals（无 FIXED 装饰 part），改变 body 离地高度 → 影响 hinge/door 的 world Z 锚点（见 plinth 变体 `BODY_KNUCKLE_ZS` 随 PLINTH_H 抬升）。
- **body 内腔 ↔ Slot C interior**：shelf 嵌两侧壁；drawer 的 `runner` 是 body 内固定承轨，`drawer_slide` origin 落在 runner 接触面。
- 互斥/可选/派生：Slot B=electronic_keypad ⇒ 无 `dial_spin`（改 12 个 button PRISMATIC）；Slot C=pull_out_drawer ⇒ 多一个 `drawer_slide` PRISMATIC；Slot D≠flush ⇒ body 整体 Z 抬升，所有 door-frame/hinge 锚点须随之重算。

## 每槽位 Module Emits / Interfaces

### Slot A / module four_spoke_wheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_wheel`(hub + hub_cap + spoke_{i}×4 + spoke_knob_{i}×4) | parent L294-L323 |
| internal joints | `handle_spin` REVOLUTE axis=door-normal range ±90° | parent L336-L344 |
| upstream interface | 坐 door 面 `handle_boss`(Cylinder, embed door slab) | parent L219-L224 |
| downstream interface | 无（叶端自由） | — |

### Slot A / module tbar_handle, lever_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tbar_handle`(hub+cross_bar+knob) / `handle_lever`(hub+lever_arm+grip) | var L295-L327 |
| internal joints | `handle_spin` REVOLUTE door-normal | var |
| upstream interface | 同 `handle_boss` | parent boss |

### Slot B / module rotary_dial
| emits | 描述 | 来源 |
|---|---|---|
| parts | `combination_dial`(dial_ring + KnobGeometry dial_knob + dial_tick_{i}×12) | parent L252-L290 |
| internal joints | `dial_spin` CONTINUOUS door-normal | parent L345-L353 |
| upstream interface | door 面 `dial_boss` + `dial_index_mark` | parent L213-L231 |

### Slot B / module electronic_keypad
| emits | 描述 | 来源 |
|---|---|---|
| parts | door visuals `keypad_housing`/`keypad_display` + `button_{i}`×12 parts | keypad L249-L340 |
| internal joints | `button_slide_{i}`×12 PRISMATIC door-normal（短行程按压）；无 dial_spin | keypad L323-L340 |
| upstream interface | door 面 keypad_housing（替代 dial_boss 区域） | keypad L249-L264 |

### Slot B / module dual_rotary_dial
| emits | 描述 | 来源 |
|---|---|---|
| parts | `combination_dial_{i}`×2（共享 `_build_dial` helper） | dual L107-L130, L300-L370 |
| internal joints | `dial_spin_{i}`×2 CONTINUOUS | dual L360-L370 |
| upstream interface | door 面双 `dial_boss_{i}` 上下叠放 | dual |

### Slot C / module single_shelf, no_shelf, pull_out_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shelf` visual / (无) / `cash_drawer` part + `runner` body visual | parent L136-141 / no_shelf / drawer L148-200 |
| internal joints | 无 / 无 / `drawer_slide` PRISMATIC +X | drawer |
| upstream interface | shelf 嵌两侧壁 / — / runner 固定面 | — |

### Slot D / module flush_bottom, leveling_feet, plinth_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | (inline `bottom_wall`) / `foot_{i}`×4 body visuals / `plinth` skirt body visuals | parent / feet L199-215 / plinth L147-185 |
| internal joints | 无（全 inline 非活动装饰，无 FIXED part） | — |
| upstream interface | body 底面，抬升 body world Z | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `turn_handle` | enum | four_spoke_wheel / tbar_handle / lever_handle | — | choice | deterministic procedural sampler | Slot A |
| `lock_entry` | enum | rotary_dial / electronic_keypad / dual_rotary_dial | — | choice | sampler | Slot B |
| `interior_layout` | enum | single_shelf / no_shelf / pull_out_drawer | — | choice | sampler | Slot C |
| `base_stance` | enum | flush_bottom / leveling_feet / plinth_base | — | choice | sampler | Slot D |
| `bolt_count` | int | [2, 6] | 3 | independent | 加权采样(小 N 偏多)，clamp [2,6] | multiplicity |
| `palette_style` | enum | charcoal_steel / gunmetal / sand_vault / navy_vault / brushed_inox | charcoal_steel | choice | per-seed `rng.choice` | 5★ 配色 |
| `body_width_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp;缩放 BODY_Y | parent envelope |
| `body_height_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp;缩放 BODY_Z | parent envelope |
| `body_depth_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp;缩放 BODY_X | parent envelope |
| `door_thick_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp;缩放 DOOR_THICK | parent L40 |
| `base_lift` | float | derived | 0.0 | equation | `= 0`(flush) / `≈0.03`(feet) / `≈0.045`(plinth)，由 `base_stance` 派生 | Slot D |
| (—) | constraint | — | — | inequality | door leaf W/H ≤ body 开口 − 2·jamb；bolt 行程使 rest bolt 末端 ∈ strike pocket 深度内 | 接口 / clearance |
| (—) | constraint | — | — | conditional | `bolt_count` 上限随 body_height_scale（栓位沿门高等距，间距 ≥ 2·BOLT_R+gap） | multiplicity |

采样契约：先采 independent 主尺度 → 派生 `base_lift` 等 equation → inequality 投影/回缩（door 不超开口、bolt 进 pocket）→ conditional 解析 bolt_count 上限。

## Multiplicity / Copy Logic

- count_param: `bolt_count`
- N_range: [2, 6]（产品域；门高有限，>6 栓位互挤。测试偏小，sweep 主跑 2-5）
- sampling domain: 加权 `rng.choices([2,3,4,5,6], weights=[3,4,3,2,1])`（小 N 高频，大 N 稀有）
- copied object: 单根 lock bolt（共享 bolt Cylinder 几何）+ latch 壁对应 strike pocket（cadquery cut）
- naming: `lock_bolt_{i}`（carriage 内）、pocket 经 `for zr in BOLT_ZS` 循环钻
- placement: 沿门高在 `BOLT_ZS`（由 bolt_count 等距生成）分布；全在同一 carriage 上
- joint policy: N 根 bolt 全随单一 `bolt_carriage`（一个 PRISMATIC `bolt_slide`）整体平移；bolt 自身不单独活动
- source/gating: parent(N=3) / two_bolts(N=2) / five_bolts(N=5，自带 `lock_bolt_` 计数断言)

（注：Slot B=electronic_keypad 的 12 个 button 是 module-local 固定复制，不暴露为模板级 count_param —— 它是该 candidate 内部的 keypad 布局，不是独立 multiplicity 轴。）

## 拓扑多样性审计

总组合数：A(3) × B(3) × C(3) × D(3) = 81 结构组合 × bolt N 采样数(取 5: {2,3,4,5,6}) = 405

理由：仅 slot 组合就 81 种不同 part/joint 拓扑，远超 10；叠加 bolt N 与可选 drawer/keypad 的 joint 拓扑差异更高。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 seed 派生 RNG，对每个 enum slot 独立加权采样、对 bolt_count 加权采样、对连续 scale 在范围内独立采样后 clamp/派生；`slot_choices_for_seed` 返回与 build 一致的 (slot, module) 列表。无 curated/modulo 主表；不设特殊 seed=0。compatibility gating：keypad ⇒ 关 dial_spin；drawer 与 shelf 互斥（drawer 取代 shelf）；base≠flush ⇒ 全局 Z 抬升重算。
Topology target：1000-seed distinct 富类别建议 ≥300（report-only）（81 结构 × bolt N × scale 量化即可破百）。
Controlled local parameterization：body_width/height/depth_scale、door_thick_scale、base_lift(derived)、bolt 间距(随 N)。全部 clamp/派生于 `resolve_config`，不破坏 door↔opening clearance、bolt↔pocket 接触、hinge origin、类别 identity。
Regression overrides：none。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 加权 choice + bolt_count 加权 + scale 独立采样 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | keypad⇒no dial_spin；drawer 取代 shelf；base 抬升重算锚点 | 无漂浮/穿模/轴错/closed-pose 失败 |
| controlled local variation | body/door scale + base_lift + bolt 间距 clamp | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A turn_handle | 3 | yes | yes | |
| B lock_entry | 3 | yes | yes | keypad 改 joint 拓扑 |
| C interior | 3 | yes | yes | drawer 加 prismatic |
| D base | 3 | yes | yes | inline visuals |

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix prevents illegal combos (keypad+dial_spin, drawer+shelf 并存)
- no regression overrides (sparse/none)
- controlled local scale params clamped；door 不超开口、bolt 进 pocket、hinge origin 贴 knuckle
- cross-part scale deps (base_lift equation, bolt 间距 conditional) resolved in resolve_config
- critical interfaces exist：door_hinge knuckle stack、handle_boss、dial_boss/keypad_housing、bolt↔strike pocket
- key joints：door_hinge REVOLUTE z 0→2.094；handle_spin REVOLUTE door-normal；dial_spin CONTINUOUS（rotary/dual）；bolt_slide PRISMATIC；drawer_slide PRISMATIC（drawer 时）
- copied objects：lock_bolt_{i} 命名+等距 placement+统一 carriage joint policy

## Reject cases

- door 关合后 bolt 不进 strike pocket（jamb gap 与 bolt 行程不匹配）→ 锁不上
- keypad candidate 仍残留 dial_spin joint 或浮空 dial → 拓扑不一致
- 选 base=feet/plinth 但未抬升 hinge/door 锚点 → door 错位/穿地
- drawer 与 shelf 同时存在 → 内腔冲突
- bolt_count 过大致栓位互相穿插（间距 < 2·BOLT_R）
- 把连续 scale（body 高矮胖瘦）误当 candidate module
- handle/dial 浮在 door 面前方（未坐 boss 接触面）
- door 开到 120° 时叶片穿过 body 侧壁（hinge origin/door 宽不匹配）

## 与相邻类别的边界

- 不该混入：wall-recessed safe（嵌墙保险箱）——本类是落地独立箱体，自带完整六面壁 + 底座，非墙洞嵌入 + flange。
- 不该混入：普通 cabinet 柜门——本类有 lock_entry(dial/keypad) + locking bolt carriage 锁机，非简单磁吸/卡扣柜门。
- 不该混入：strongroom / 金库门——本类是可搬运的 freestanding 箱体（~0.5 m 量级），非整面墙的金库门。
- 不该混入：lockbox / 收纳箱——本类有真实 hinge + bolt 锁机 + dial/keypad，非无锁机的提手箱。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 自动管线：用户指示全程不停（不设人工审核 gate）。spec 由 source map + 11 个 5★ 样本全量阅读派生；slot A-D 各 ≥3 candidate，multiplicity bolt N 覆盖 {2,3,5}，组合数 405 ≫ 10。已批准进入 TEMPLATE 实现。 |

## 模板实现备注（可选）

- 共享 helper：Slot A 三 handle module 共用 hub + door-normal REVOLUTE 锚定；Slot B rotary/dual 共用 `_build_dial`；bolt 复制共用 bolt 几何 + `BOLT_ZS` 等距生成器。
- 代码结构可直接借鉴现有 `agent/templates/wall_safe_with_hinged_door_and_dial.py` 的 modular safe 脚手架（config_from_seed / resolve_config / slot_choices_for_seed / palette / _allow_expected_overlaps / run_tests），几何换成本 parent 的 freestanding box。
- captured-pin overlap：bolt_carriage 的 carriage_bar / lock_bolt_{i} 故意滑入 door slab proxy，需 element-scoped `allow_overlap`（见 parent run_tests L391-405）。
- palette_style 必须 per-seed 采样并驱动每个 `.visual(material=...)`，目标 4-6 colorway，避免 monochrome 池。
- base≠flush 时务必把 hinge HINGE_Z / BODY_KNUCKLE_ZS / door 锚点统一加 base_lift（见 plinth 变体 L61 的 `+ PLINTH_H`）。
