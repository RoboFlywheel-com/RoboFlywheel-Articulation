# candy_vending_machine — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `candy_vending_machine` |
| template path | `agent/templates/candy_vending_machine.py` |
| test path (optional) | `tests/agent/test_candy_vending_machine_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children chassis + multiplicity selectors） |

主结构是一个接地 body（chassis），多个机构以 parallel children 形式挂到 body：旋转 selector/coin 机构（multiplicity 1–3）、取货 flap/door/drawer、可选 refill 盖/门。没有串联运动 spine，因此用 parallel-children + multiplicity 而非 linear chain。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 24 |
| read_count | 24 |
| read_scope | all 5-star samples in candy_vending_machine |
| source_index_policy | only adopted module sources are indexed below |

24 个 5 星样本聚为 5 个形态族：
1. pedestal / countertop gumball globe（透明球 + 立柱/铸座 + 投币旋钮 + 取货 flap + 顶部 refill 盖）：`3db2f25c`、`43ed2cb8`、`653a20ac`、`b369717d`、`853ebf9e`、`5896f5c4`、`35e27aaa`、`f1c7c8db`、`d8046df5`。
2. dual / twin reservoir（两个透明 globe/hopper + 共享底座 + 中央 collection cup + 双旋钮 + 双 refill 盖）：`2fdcbef7`、`88e5eb91`、`90967138`。
3. tall glazed spiral cabinet（高柜 + 烟熏玻璃门 + 螺旋货道 + 选择拨盘 + 取货 flap / cash drawer）：`9c8af8`、`208919`、`997931`、`1e77fe`。
4. stacked canister / bin cabinet（2–3 个堆叠透明罐/仓 + 多个 selector 拨盘 + 下方取货门）：`0dfd76`、`0f8e34`、`02c9f3`、`b394ff`。
5. wall-mounted shallow hopper（壁挂浅箱 + 透明前 hopper + 投币旋钮 + 取货 cup flap + 侧/顶 refill 门）：`00e555`、`e6a5fe`、`ae2c9d28`、`f0acb1f1`。

跨全部样本的普适主运动：**CONTINUOUS 选择/投币旋钮（1–3 个）** + **REVOLUTE 取货 flap/door（或 PRISMATIC cash drawer）**。次级运动：refill 盖/门（REVOLUTE）、玻璃前门（REVOLUTE 竖铰）。

## 核心身份

Candy vending machine 是接地的售糖机：一个稳定 body 容纳/展示透明产品仓，正面有用户可操作的旋转选择/投币机构（连续转动），下方有取货门/翻盖把糖果送出，部分形态在顶部/侧面有补货盖/门。比例从台面 gumball（~0.4–0.6 m 高）到大堂落地柜（~1.2–1.8 m 高）。识别要点：透明可见产品仓 + 连续旋转旋钮 + 取货翻盖。

不该混入的相邻类别：
- `gumball_machine` 纯扭蛋机若无独立类别则并入本模板的 pedestal_globe chassis；不要把工业自动售货柜（带屏幕/制冷）的结构塞进来。
- `chest_freezer` / `display_freezer`：售货柜玻璃门易与制冷柜混淆，但本类别没有制冷压缩机/温控，门后是糖果货道不是冷冻篮。
- `desk_with_drawer`：cash drawer 是取货/收银抽屉，不是家具抽屉柜。

## 槽位 + 候选模块表

### Slot A：chassis（接地 body + 一体化透明产品仓 + 该形态原生的 refill 机构）

每个 chassis 候选是结构上不同的 part tree。透明产品仓、铸座、立柱、玻璃、货道等不动结构按 Rule 1 折成 body 的 named visual；chassis 工厂同时发出该形态原生的 refill 活动件（见 Slot D）。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `pedestal_globe` | rec_..._3db2f25c | L71-132 | eligible if compatible | 圆 foot + 立柱 + cast housing box + LatheGeometry 透明球 + crown 环；旋钮在 housing 正面 |
| `dual_hopper_pedestal` | rec_..._88e5eb91 | L112-265 | eligible if compatible | 宽底盘 + 立柱 + 共享 body + 2 个 Lathe 透明 hopper + 中央 pickup 凹槽 |
| `tall_glazed_cabinet` | rec_..._9c8af8 | L70-208 | eligible if compatible | 高矩形柜 + 烟熏玻璃前面板 + tube_from_spline_points 螺旋货道 + pickup chute |
| `stacked_canister_cabinet` | rec_..._0dfd76 | L32-217 | eligible if compatible | 落地柜 + N 个堆叠透明 bin（矩形/Lathe）+ 下部 pickup recess + mechanism column |
| `wall_mount_hopper` | rec_..._00e555 | L39-124 | eligible if compatible | 壁挂浅箱 backplate + 透明前 hopper 框 + coin faceplate |

补充来源（同族迁移参考）：`653a20ac` L114-209、`b369717d` L118-218、`43ed2cb8` L60-171（globe）；`90967138` L19-307（dual hopper）；`208919` L101-353、`997931` L201-350、`1e77fe` L61-99（glazed cabinet）；`0f8e34` L37-279、`02c9f3` L57-146、`b394ff` L14-54（canister cabinet）；`e6a5fe` L34-183、`ae2c9d28` L39-111、`f0acb1f1` L69-163（wall/compact）。

### Slot B：dispense（旋转选择 / 投币机构，multiplicity-aware）

每个候选发出 N 个旋钮 part（CONTINUOUS）挂到 body。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_knob` | rec_..._e6a5fe | L204-244 | eligible if compatible | 1 个 KnobGeometry（faceted/lobed）ribbed grip + 指示，CONTINUOUS，axis Y |
| `dual_selectors` | rec_..._02c9f3 | L230-290 | eligible if compatible | 2 个 selector（shaft+hub+disc+pointer），CONTINUOUS，axis Y |
| `triple_selectors` | rec_..._0dfd76 | L159-188 | eligible if compatible | 3 个 selector（shaft+grip_disk+pointer_bar），CONTINUOUS，axis Y |
| `coin_head_wheel` | rec_..._853ebf9e | L275-313 | eligible if compatible | 1 个投币头轮（hub+wheel+handle/finger post），CONTINUOUS，axis X/Y |

补充来源：`43ed2cb8` L173-197、`5896f5c4` L194-229（lobed KnobGeometry）；`0f8e34` L281-337、`b394ff` L56-111（dial selectors）；`d8046df5` L174-198、`3db2f25c` L291-321（coin wheel/handle）。

### Slot C：retrieval（取货 / 收银机构）

每个候选发出 1 个活动取货件挂到 body。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `chute_flap` | rec_..._0dfd76 | L190-217 | eligible if compatible | 底铰 REVOLUTE 翻盖（panel + hinge barrel + pull lip），axis X，下翻 |
| `collection_cup_door` | rec_..._2fdcbef7 | L130-173 | eligible if compatible | body 上的 collection cup（visual）+ 透明前 flap（REVOLUTE，axis X） |
| `cash_drawer` | rec_..._997931 | L458-538 | eligible if compatible | PRISMATIC 抽屉（drawer body + face + runners），axis Y |
| `glazed_swing_door` | rec_..._208919 | L294-353 | eligible if compatible | 整面玻璃门 REVOLUTE 竖铰（stiles+rails+glass pane+handle），axis Z |

补充来源：`5896f5c4` L231-258、`e6a5fe` L246-274、`2fdcbef7` L290-309（flap）；`88e5eb91` L290-317（cup door）；`1e77fe` L259-298（drawer）；`9c8af8` L166-178、`f0acb1f1` L261-278（glazed/service door）。

### Slot D：refill（补货机构，gated 由 chassis 派生）

不是自由槽：由 chassis profile 决定可选集合。是 chassis 形态的原生活动件。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `top_lid` | rec_..._3db2f25c | L254-278 | eligible if compatible | 顶部圆 refill 盖（cap + badge + hinge leaf + barrel），REVOLUTE axis X，后铰上翻 |
| `dual_top_lids` | rec_..._88e5eb91 | L238-265 | eligible if compatible | 每个 hopper 一个顶盖，2 个 REVOLUTE |
| `side_door` | rec_..._00e555 | L285-312 | eligible if compatible | 侧铰 refill 门（panel + 竖 hinge barrel + tab），REVOLUTE axis Z |
| `none` | —（多数 cabinet 形态由前门/抽屉补货） | — | eligible if compatible | 不发出 refill 活动件 |

补充来源：`653a20ac` L211-235、`43ed2cb8` L220-239、`b369717d` L240-251（top lid）；`2fdcbef7` L239-272（dual lids）；`f0acb1f1` L261-278（side service door）。

硬约束满足情况：Slot A 5 candidate、Slot B 4、Slot C 4、Slot D 4（含 `none`）。每个 candidate 结构不同且有 5 星来源，并已声明 sampling eligibility。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
                 chassis (root, grounded body, 透明产品仓 = body visuals)
                /        |          \             \
   dispense (1-3 knob)  retrieval(flap/door/drawer)  refill(lid/door/none)
   CONTINUOUS Y/X       REVOLUTE X / PRISMATIC Y     REVOLUTE X/Z
   parent=body          / REVOLUTE Z                 parent=body (或 cup→flap)
```

- 所有活动件直接挂 body（parallel children）。无跨 slot 串联铰链；assembler 用显式 slot dispatch，不用 `_modular.assemble` 自动链。
- 接口点位：
  - dispense：body 正面 `*_knob_boss` / `*_bezel` cylinder（沿旋转轴）作为可见锚；旋钮后端 shaft 嵌入 boss（captured-pin overlap）；joint origin 落在 boss 上，axis 穿过 boss 中心。
  - retrieval：body 下方 `pickup_*` 开口 + `flap_hinge_lug`/`hinge barrel`（flap）或 `runner` 导轨（drawer）或 `door_jamb` + `hinge_knuckle`（glazed door）。joint origin 落在铰线/导轨上。
  - refill：reservoir 顶/侧的 `refill_hinge_*` lug/barrel；joint origin 落在铰线上。
  - collection_cup_door 特例：cup 是 body visual，flap 的 parent 仍是 body，hinge 在 cup 前下缘。
- 跨 slot 兼容：dispense/retrieval/refill 的可选集合由 chassis profile 约束（见参数表与多样性审计），避免“globe 上装 cash drawer”等非法组合。

## 每槽位 Module Emits / Interfaces

### Slot A / chassis（以 `pedestal_globe` 为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root；含 foot/column/cast housing/clear globe(LatheGeometry)/crown rings/coin faceplate/chute frame 全部为 named visual） | `3db2f25c` L71-229 |
| internal joints | 无（refill 活动件由 Slot D 在同一 build 内发出） | — |
| upstream interface | 无（root，接地） | — |
| downstream interface | `body` part + 正面/顶部 mounting 参考点（knob_boss / refill_hinge / pickup opening 的世界坐标，存入 resolved config 供 B/C/D 消费） | `3db2f25c` L159-229 |

### Slot B / dispense（`single_knob`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `selector_0`（KnobGeometry cap + shaft + bearing collar） | `e6a5fe` L204-244 |
| internal joints | `body_to_selector_0` CONTINUOUS axis Y，effort~1.5 vel~8 | `e6a5fe` L186-203 |
| upstream interface | 消费 body 正面 `selector_boss_0`（可见 bezel cylinder），shaft 嵌入 boss | `e6a5fe` 同上 |
| downstream interface | 无（叶子） | — |

### Slot C / retrieval（`chute_flap`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `retrieval_flap`（panel + hinge barrel + pull lip） | `0dfd76` L190-217 |
| internal joints | `body_to_retrieval` REVOLUTE axis X，lower=0 upper~1.15–1.30 | `0dfd76` L190-217 |
| upstream interface | body 下方 `pickup_hinge_lug_*` + opening；flap hinge barrel 被 lug 捕获 | `0dfd76` 同上 |
| downstream interface | 无 | — |

### Slot D / refill（`top_lid`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `refill_lid`（cap disk + badge + hinge leaf + barrel） | `3db2f25c` L254-278 |
| internal joints | `body_to_refill` REVOLUTE axis X，lower=0 upper~1.35 | `3db2f25c` L254-278 |
| upstream interface | reservoir 顶 crown 后缘 `refill_hinge_barrel`；lid hinge 捕获 | `3db2f25c` L218-253 |
| downstream interface | 无 | — |

活动件均有 articulation 语义；不动细节（货道、刻度、面板、螺丝、糖果堆）写成 parent visual。captured-pin（shaft↔boss、barrel↔lug）用 element-scoped `allow_overlap` 声明。joint 全部 grandfather（不声明 MatingContract），靠 captured-pin overlap + articulation-origin-on-geometry + 可见支撑通过 baseline（参照 `wall_safe_with_hinged_door_and_dial` 已验证写法）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `chassis` | enum | pedestal_globe / dual_hopper_pedestal / tall_glazed_cabinet / stacked_canister_cabinet / wall_mount_hopper | pedestal_globe | seed/override | module table |
| `dispense` | enum | single_knob / dual_selectors / triple_selectors / coin_head_wheel | single_knob | 由 chassis profile 约束采样 | module table |
| `retrieval` | enum | chute_flap / collection_cup_door / cash_drawer / glazed_swing_door | chute_flap | 由 chassis profile 约束采样 | module table |
| `refill` | enum | none / top_lid / dual_top_lids / side_door | top_lid (pedestal_globe) | 由 chassis profile 约束采样 | module table |
| `selector_count` | int | 1–3 | 1 | 由 dispense 派生（single=1, dual=2, triple=3, coin=1） | `0dfd76`/`0f8e34` |
| `canister_count` | int | 2–3 | — | 仅 stacked_canister_cabinet；由 chassis 派生 | `0dfd76`/`0f8e34` |
| `body_w/d/h` | float | 各 chassis 各自范围（globe 高 0.40–1.0；cabinet 高 1.0–1.8；wall 高 0.55–0.90） | sampled / derived dimensions | 接口派生 | 各 chassis 来源 |
| `door_swing` | float | [1.05, 1.55] rad | 1.20 | flap/door upper | flap 来源 |
| `drawer_travel` | float | [0.08, 0.18] m | 0.13 | cash_drawer upper | `997931` |
| `palette_theme` | enum | classic_red / chrome_blue / mint_cream / charcoal / candy_pink | classic_red | 视觉 | 通用 |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette。未实现拓扑不入 enum。

## Multiplicity / Copy Logic

- `count_param`：`selector_count`（dispense 派生）和 `canister_count`（chassis 派生）。
- `N_range`：selector 1–3；canister 2–3。
- sampling domain：selector_count 由 dispense module 唯一决定（single=1/dual=2/triple=3/coin=1）；canister_count 仅在 stacked_canister_cabinet 时为 2–3，否则不暴露。
- copied object：selector part（`selector_i`，相同 helper 几何、沿正面竖向/横向等距）；canister bin（`bin_i` body visual 组，等距堆叠）。
- naming：`selector_i`、`body_to_selector_i`、`bin_i_*`。
- placement：selector 沿正面按 chassis 给的 mounting 列等距；canister 沿 z 等距堆叠。
- joint policy：每个 selector 一个独立 CONTINUOUS 关节；canister 是 body visual 无关节。
- source/gating：multiplicity 数量来自 5 星样本（triple canister/triple dial、twin column、dual hopper）。

## 拓扑多样性审计

总组合数：在 chassis profile 约束下（非自由笛卡尔积），合法 (chassis, dispense, retrieval, refill) 组合约为：
- pedestal_globe: 2 dispense × 2 retrieval × 2 refill = 8
- dual_hopper_pedestal: 1 × 2 × 2 = 4
- tall_glazed_cabinet: 2 × 3 × 1 = 6
- stacked_canister_cabinet: 3 × 2 × 1 = 6
- wall_mount_hopper: 2 × 2 × 3 = 12
合计约 36 个合法拓扑组合（未计 selector/canister multiplicity 与 palette）。

理由：chassis(5) 叠加 dispense/retrieval/refill 后远超 10。50 seed 随机采样保守估计能命中 ≥15 个 distinct tuple。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊。Sampler 先选择上游结构槽，再按 compatibility matrix / gating 从合法下游 candidate 集合采样；少量 regression overrides 仅用于已知失败回归或 reviewer 指定样本，不得作为主 seed domain。

Procedural Sampling / Sweep Plan：

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | conditionally independent deterministic sampling over compatible slot/module/multiplicity choices | `slot_choices_for_seed(seed)` 必须等于实际 build choices |
| compatibility matrix | 由 slot graph、InterfaceSpec / MatingContract、joint axis / range、support plane 和 validator 约束决定合法组合 | no floating, collision, axis, closed-pose, max multiplicity, bulky module, optional child failures |
| regression overrides | 默认无；仅允许少量已知失败回归或 reviewer 指定 seed | 记录 seed、组合和原因；不得用 modulo / curated 表作为主域 |
| random sweep | `sweep-pipeline` 的 0、0-4、0-19、0-49 cumulative seeds；成熟审计可扩到 0-999 | 、contract failures、viewer identity/proportion |


| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A chassis | 5 | yes | yes | |
| B dispense | 4 | yes | yes | |
| C retrieval | 4 | yes | yes | |
| D refill | 4 | yes | yes | 含 `none`；由 chassis gated |

## Validator

- slot_choices_for_seed 返回已实现 module 名 + multiplicity 标记（如 `("dispense_multiplicity","2_selectors")`）。
- Procedural sampling domain 已记录，compatibility gates 覆盖各 chassis 代表组合 + max multiplicity + prismatic + 竖铰 door + dual lids 等高风险组合。
- Procedural-first target 已记录。
- final 模板不无限轮换小 curated 表：采用条件随机采样作为主域。
- 关键 joint type/axis/range：selector CONTINUOUS（axis Y 或 X）；retrieval REVOLUTE axis X（flap/cup）或 PRISMATIC axis Y（drawer）或 REVOLUTE axis Z（glazed door）；refill REVOLUTE axis X（lid）或 Z（side door）。
- copied selectors 命名/等距 placement 正确；每个独立 CONTINUOUS 关节。
- captured-pin overlap（shaft↔boss、barrel↔lug、drawer↔runner）用 element-scoped allow_overlap 声明。

## Reject cases

- 把透明产品仓做成不透明实心壳（看不见糖果）→ 失去类别身份。
- selector 不转（做成静态旋钮 visual 而无 CONTINUOUS 关节）。
- 取货 flap/door 无关节或只摆开启姿态。
- 在 globe/pedestal chassis 上挂 cash_drawer / glazed_swing_door（无柜体承载，悬空）。
- selector 数量与 chassis 不符（单球挂三旋钮、堆叠柜只给一个旋钮却宣称 triple）。
- 旋钮/盖用 1–3 mm phantom disk 锚定（Rule 2）；必须嵌入真实 boss/lug。
- refill 盖闭合时悬空或与 crown 穿模；drawer 行程超过可用柜深。
- 把不动货道/刻度/糖果堆做成独立 FIXED part（Rule 1）。
- 旋钮轴未穿过 boss 中心导致 joint origin 离几何过远。

## 与相邻类别的边界

- 不该混入：`chest_freezer` / `display_freezer_with_sliding_glass_lids`（制冷柜：有压缩机/温控/滑动玻璃盖；本类别是常温糖果机，门后是货道）。
- 不该混入：`desk_with_drawer`（家具抽屉柜；cash_drawer 是收银/取货抽屉，属机器机构非家具）。
- 不该混入：工业自动售货机（带触屏/制冷/纸币器的大型 vendor）；本模板聚焦机械糖果机的连续旋钮 + 取货翻盖身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（用户单条指令要求 spec→template→viewer 端到端；作者代行 spec 起草，用户在 viewer 阶段终审） |
| reviewer notes | 端到端任务；procedural-first sampling / sweep plan 已写入；进入 TEMPLATE_AFTER_REVIEW 实现。 |

## 模板实现备注

- 共享 helper：`_clear_shell_mesh`（LatheGeometry.from_shell_profiles，globe/hopper/canister 透明壳）、`_spiral_mesh`（tube_from_spline_points，glazed cabinet 货道）、`_knob`（KnobGeometry + grip + indicator）、`_hinge_flap`、`_box/_cyl` 原语包装。
- chassis 工厂把 mounting 参考点（selector boss 列、refill hinge、pickup 开口、drawer runner、door jamb 的世界坐标）写入 resolved config，dispense/retrieval/refill 工厂据此放件。
- 所有 separate moving child 必须几何嵌入 body 的真实 boss/lug/runner（满足 `fail_if_isolated_parts` 与可见支撑），并在 `run_candy_vending_machine_tests` 用 try/except `allow_overlap` 批量声明 captured-pin overlap（参照 wall_safe）。
- joint 默认 grandfather（不声明 MatingContract），降低 mating-gap 风险；如 sweep 报浮空再加可见 boss。
- 透明材质 alpha 0.28–0.40；不要 alpha=1.0 当透明。
