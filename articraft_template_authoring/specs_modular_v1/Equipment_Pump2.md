# Hand Pump Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `hand_pump` |
| template path | `agent/templates/Equipment_Pump2.py` |
| test path | `tests/agent/test_hand_pump_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 (1 parent + 9 forked variants) |
| read_count | 10 |
| read_scope | all candidates in the `Equipment/Pump2` picture-subcat fork batch (parent + 9 variants) |
| source_index_policy | every candidate below is a directly read `model.py`; all 10 adopted as module sources |

数据根位置说明（dataset-root caveat）：本小类的候选不是某个常规 5 星类目的整批样本，而是 `articraft_data` 仓库内 **workbench-only** 的 picture-subcat fork。全部 9 个变体由唯一 parent `621823e2` 经 `articraft fork` 派生，仅入 `collections=['workbench']`，未 promote 进正式 dataset；绑入 `Equipment__Pump2` picture 子类 shard。因此引用一律写仓库内相对路径 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`，而非 dataset 编号化的 `rec_<slug>_NNNN`。

- parent（同时覆盖三槽 baseline）：`rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2`
- Slot A 变体：`rec_pump_var_handle_tbar`, `rec_pump_var_handle_dloop`, `rec_pump_var_handle_palmdisc`
- Slot B 变体：`rec_pump_var_base_flange`, `rec_pump_var_base_tripod`, `rec_pump_var_base_wallbracket`
- Slot C 变体：`rec_pump_var_outlet_gooseneck`, `rec_pump_var_outlet_barb`, `rec_pump_var_outlet_tapvalve`

## 核心身份

Hand pump 是手动桶式活塞泵（manual barrel hand pump）：一只竖直机加工 barrel 由铸件 base + yoke 夹座承托坐地，piston 杆经顶部 knurled cap gland 上伸、顶端带抓握件；用手把 plunger 向下压入 barrel 完成打气冲程（PRIMARY = `barrel_to_piston` PRISMATIC，唯一 hero 真关节，axis `(0,0,-1)`、`upper=STROKE`）。一根黑色 foot/wing lever 销在 yoke clevis 上绕销摇摆（SECONDARY = `yoke_to_lever` REVOLUTE，axis `(0,1,0)`）。base 侧 `_base_fitting_shape` 引出一个侧向 outlet stub（沿 -Y，中心 `(0,-0.038,0.030)`），上面接出水构件（软管/刚性喷口/带阀龙头）。

成熟域：手动柱塞泵（cast-metal barrel pump）。三个结构槽——handle（顶部抓握）、base（落地/贴墙承托）、outlet（侧向出水）——并联挂在同一根刚体 `pump_body` 与其 `piston` 子件上；所有候选都保留两个 hero 关节。

边界：
- 不读成电泵：handle 必须是手动柱塞抓握件，不能换成电动马达驱动（会丢失 `barrel_to_piston` PRISMATIC hero 关节）。
- 不混入化妆品/容器分配泵（cosmetic dispenser）：本类是铸件落地式泵体，不是瓶口按压头。

## 槽位 + 候选模块表

三个 slot 都并联挂在 `pump_body`（base、outlet）或其 `piston` 子件（handle）上。每个 slot baseline 由 parent `621823e2` 覆盖，本批每个变体各补一格，故每槽 4 candidate（1 baseline + 3 fork 变体）。

### Slot A：handle（顶部柱塞抓握，挂 `piston` 部件，经 `barrel_to_piston` PRISMATIC 主关节驱动）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `ball_knob_plunger`（baseline） | `rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2/revisions/rev_000001/model.py:L278-L385` | eligible if compatible | `piston` 部件：`ball_knob`(Sphere) + `rod`(Cylinder) + `piston_head`(`_piston_head_shape`)；大号黑色实心球柄压在杆顶 |
| `handle_tbar` | `rec_pump_var_handle_tbar` | `data/records/rec_pump_var_handle_tbar/revisions/rev_000001/model.py:L289-L320`（helper）+ `L414-L418`（emit） | eligible if compatible | `_t_bar_grip_shape`：横向 crossbar + 两端 end_collar + 向下 socket 套住 rod 顶端；水平 T 型横握把 |
| `handle_dloop` | `rec_pump_var_handle_dloop` | `data/records/rec_pump_var_handle_dloop/revisions/rev_000001/model.py:L290-L319`（helper）+ `L419-L431`（emit） | eligible if compatible | `_pull_loop_geometry`(closed Catmull-Rom 弯管) + `loop_socket`(Cylinder)；封闭 D 形提拉环，中间留手孔 |
| `handle_palmdisc` | `rec_pump_var_handle_palmdisc` | `data/records/rec_pump_var_handle_palmdisc/revisions/rev_000001/model.py:L290-L310`（helper）+ `L405-L409`（emit） | eligible if compatible | `_push_disc_geometry`(LatheGeometry)；车削掌推圆盘，掌压式握面 |

### Slot B：base（`pump_body` 根刚体上的承托脚/支座）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cast_hex_foot`（baseline） | `rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2/revisions/rev_000001/model.py:L147-L226` | eligible if compatible | `_base_fitting_shape`(polygon(6) 六角脚盘 + neck) + `_yoke_shape`；铸件六角脚盘 + 夹座，直接坐地 |
| `base_flange` | `rec_pump_var_base_flange` | `data/records/rec_pump_var_base_flange/revisions/rev_000001/model.py:L152-L220`（`_base_fitting_shape`+`_flange_bolt_shape`）+ `L347-L360`（`flange_bolt_{i}` 循环 emit） | eligible if compatible | 法兰圆盘底座 + 4 颗螺栓圈(`for i in range(4)`)，落地固定 |
| `base_tripod` | `rec_pump_var_base_tripod` | `data/records/rec_pump_var_base_tripod/revisions/rev_000001/model.py:L179-L215`(`_tripod_leg_shape(angle)`)+ `L342-L352`（`leg_{i}` 循环 emit） | eligible if compatible | 三脚撑架，三条铸腿(`for i in range(3)`，120° 等分)外撑落地 |
| `base_wallbracket` | `rec_pump_var_base_wallbracket` | `data/records/rec_pump_var_base_wallbracket/revisions/rev_000001/model.py:L201-L259`(`_back_plate_shape`/`_saddle_clamp_band_shape`/`_fastener_head_shape`)+ `L387-L434`（emit） | eligible if compatible | 墙挂背板 + 抱箍鞍座，环抱 barrel 贴墙；落地脚改为 wall mount |

### Slot C：outlet（base 侧 `_base_fitting_shape` outlet stub，沿 -Y、中心 `(0,-0.038,0.030)`）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `loose_rubber_hose`（baseline） | `rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pump_20260609_180115_462868_621823e2/revisions/rev_000001/model.py:L334-L356` | eligible if compatible | `hose`(`tube_from_spline_points`，9 控制点，free end 落地)；黑橡胶软管绕泵一圈、末端松落地面 |
| `outlet_gooseneck` | `rec_pump_var_outlet_gooseneck` | `data/records/rec_pump_var_outlet_gooseneck/revisions/rev_000001/model.py:L192-L232`(`_spout_socket_shape`/`_downturned_nozzle_shape`)+ `L383-L411`（emit） | eligible if compatible | `spout_socket` + `gooseneck_spout`(spline) + `downturned_nozzle`；刚性鹅颈弯管喷口，末端下弯 |
| `outlet_barb` | `rec_pump_var_outlet_barb` | `data/records/rec_pump_var_outlet_barb/revisions/rev_000001/model.py:L184-L230`(`_barbed_nipple_shape`)+ `L381-L384`（emit） | eligible if compatible | `barbed_nipple`(`for i in range(3)` 倒刺环)；直插带倒刺接管嘴 |
| `outlet_tapvalve` | `rec_pump_var_outlet_tapvalve` | `data/records/rec_pump_var_outlet_tapvalve/revisions/rev_000001/model.py:L190-L240`(`_tap_body_shape`)+ `L346-L364`(`_tap_handle_shape`)+ `L520-L528`(`tap_to_handle` 关节) | eligible if compatible | `tap_body`(挂 body) + `tap_handle` 部件；带阀体的出口 + 可转 tap 手柄（额外第三个非固定关节） |

## 槽位图（slot graph）

pattern: `parallel_children`

```text
                 [pump_body 根刚体 (barrel + cap + base_fitting + yoke)]
                  │
   barrel_to_piston PRISMATIC ──────► [Slot A handle / piston]  (axis (0,0,-1), upper=STROKE)
   yoke_to_lever     REVOLUTE  ──────► [lever]                  (origin (-0.052,0,0.044), axis (0,1,0), [-0.5,0.5])
   FIXED (root visuals)        ──────► [Slot B base]            (落地脚 / 法兰 / 三脚 / 墙挂背板, z≈0 或贴墙)
   FIXED (outlet stub, -Y)     ──────► [Slot C outlet]          (软管 / 鹅颈 / 倒刺) ── 默认无独立关节
                                       └─ outlet_tapvalve 例外: tap_to_handle REVOLUTE
                                          (origin (0,TAP_Y,TAP_BOSS_TOP_Z), axis (0,0,1), [0, π/2])
```

接口点位与跨 slot 连接：
- Slot A handle ↔ `piston` rod：所有 handle 候选用一个向下 socket/collar 套住 `rod` 顶端，统一挂 `piston` 部件；consumer joint = `barrel_to_piston` PRISMATIC（origin `(0,0,0)`，axis `(0,0,-1)`，`upper=STROKE`），mating = 杆顶轴线 anchor。
- Slot B base ↔ 地面/墙：base 候选是 `pump_body` 根刚体的承托结构（FIXED，非活动件），落地式脚底 z≈0；`base_wallbracket` 例外为贴墙抱箍（`saddle_clamp_band` 环抱 barrel footprint）。
- Slot C outlet ↔ base_fitting outlet stub：spout/nipple/tap 进口套接在 `_base_fitting_shape` 侧向 outlet stub（沿 -Y，中心 `(0,-0.038,0.030)`）；baseline 软管自由落地，gooseneck/barb 为刚性 FIXED 附件；`outlet_tapvalve` 额外引出 `tap_handle` 部件 + `tap_to_handle` REVOLUTE。
- lever ↔ yoke pin（全候选共享，未改）：`yoke_to_lever` REVOLUTE，lever hub bore 抱住 yoke pin（captured-pin allow_overlap）。

互斥/可选：handle、base、outlet 三槽互不互斥，各自独立选择。`base_wallbracket` × `loose_rubber_hose` 是已知风险组合（软管"落地"约束在墙挂姿态下不成立，见 compatibility matrix）。`tap_to_handle` 仅在 `outlet_tapvalve` 出现，是可选 moving child。

## 每槽位 Module Emits / Interfaces

### Slot A / module `ball_knob_plunger` (baseline)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `piston` 部件：`piston_head` + `rod` + `ball_knob` | parent / model.py:L359-L385 |
| internal joints | 无 module 内关节；handle 刚性属于 `piston` | parent / model.py:L359-L385 |
| upstream interface | 杆顶轴线 socket 套住 rod；由 `barrel_to_piston` PRISMATIC 消费 | parent / model.py:L403-L411 |
| downstream interface | piston_head 滑入 barrel bore（retained insertion, allow_overlap） | parent / model.py:L500-L516 |

### Slot A / module `handle_tbar` / `handle_dloop` / `handle_palmdisc`
| emits | 描述 | 来源 |
|---|---|---|
| parts | tbar=`t_bar_grip`；dloop=`pull_loop`+`loop_socket`；palmdisc=`push_disc` | 见 slot 表各 emit 行 |
| internal joints | 无（handle 刚性挂 `piston`） | — |
| upstream interface | 统一向下 socket/collar 套住 rod 顶端，挂 `piston` | tbar L289-L320 / dloop L290-L319 / palmdisc L290-L310 |
| downstream interface | 复用 baseline 的 `piston_head`↔barrel retained insertion | 各变体 piston 部件 |

### Slot B / module `cast_hex_foot` (baseline) / `base_flange` / `base_tripod` / `base_wallbracket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 全部为 `pump_body` 根刚体上的 visual（FIXED），无独立 part | parent L147-L226；flange L347-L360；tripod L342-L352；wallbracket L387-L434 |
| internal joints | 无关节（base 为静态承托） | — |
| upstream interface | base 与 barrel 经 `_base_fitting_shape` neck 正向就位 | parent L166-L173 |
| downstream interface | 落地脚底 z≈0；wallbracket 经 `saddle_clamp_band` 贴墙环抱 barrel | tripod L556-L558；wallbracket L657-L658 |
| module-local copy | flange `flange_bolt_{i}` range(4)；tripod `leg_{i}` range(3)（见 §8） | flange L347；tripod L342 |

### Slot C / module `loose_rubber_hose` (baseline) / `outlet_gooseneck` / `outlet_barb` / `outlet_tapvalve`
| emits | 描述 | 来源 |
|---|---|---|
| parts | hose / spout_socket+gooseneck_spout+downturned_nozzle / barbed_nipple / tap_body(+`tap_handle` part) | 见 slot 表各 emit 行 |
| internal joints | baseline/gooseneck/barb 无关节；**tapvalve 新增 `tap_to_handle` REVOLUTE** | tapvalve L520-L528 |
| upstream interface | 进口套接 `_base_fitting_shape` outlet stub（-Y, `(0,-0.038,0.030)`） | parent L174-L182 |
| downstream interface | hose free end 落地 z≈0；gooseneck nozzle 下弯；tap_handle 绕 `(0,0,1)` 转 | gooseneck L577-L587；tapvalve L667-L681 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `handle_style` | enum | `ball_knob_plunger` / `handle_tbar` / `handle_dloop` / `handle_palmdisc` | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `base_style` | enum | `cast_hex_foot` / `base_flange` / `base_tripod` / `base_wallbracket` | — | choice | deterministic procedural sampler 选择 | Slot B 表 |
| `outlet_style` | enum | `loose_rubber_hose` / `outlet_gooseneck` / `outlet_barb` / `outlet_tapvalve` | — | choice | deterministic procedural sampler 选择 | Slot C 表 |
| `stroke_scale` | float | [0.7, 1.3] | 1.0 | independent | `STROKE = 0.065 · stroke_scale`，clamp；不得超过 barrel 净 bore 高度 | parent / model.py:L48 |
| `barrel_height_scale` | float | [0.85, 1.2] | 1.0 | independent | 缩放 `BARREL_TOP_Z - BARREL_BOTTOM_Z` | parent / model.py:L38-L39 |
| `rod_top_z` | float | derived | — | equation | `= f(barrel_height_scale, KNOB_CENTER_Z)`，rod 长随 barrel 高派生 | parent / model.py:L370-L372 |
| `leg_count` | int | [3, 6] | 3 | conditional | 仅 `base_style=base_tripod` 时有效（module-local，§8） | tripod / model.py:L342 |
| `bolt_count` | int | [3, 8] | 4 | conditional | 仅 `base_style=base_flange` 时有效（module-local，§8） | flange / model.py:L347 |
| (—) | constraint | — | — | inequality | `STROKE ≤ (BARREL_TOP_Z − BARREL_BOTTOM_Z) − CUP_LEN`：full-stroke piston cup 不得脱出 barrel bore；违反则回缩 STROKE | 接口 / retained insertion |
| (—) | constraint | — | — | inequality | `ball_knob` 底缘 − `cap` 顶在 rest 与 full-stroke 都 ≥0.005 间隙；违反回缩 KNOB_CENTER_Z | parent / model.py:L466-L471, L543-L548 |

## Multiplicity / Copy Logic

- **无复制数量逻辑（parent 级）**：核心结构由固定 named slots（`pump_body` 根刚体 + `piston` + `lever` + 三个结构槽）表达，不暴露 parent 级 `*_count`，也不通过循环复制模板级 part/joint。两个 hero 关节 `barrel_to_piston` PRISMATIC 与 `yoke_to_lever` REVOLUTE 均为单实例。

随后记录两个**局部 copy-logic 样本**——它们是 module-local 的可选 `count_param`，不是 parent 级 multiplicity 轴；只在对应 base module 被选中时生效：

- 局部样本 1（`base_tripod` 演示）：
  - count_param: `leg_count`
  - copied object: 单条三脚撑腿（helper `_tripod_leg_shape(angle)` 发射的一条铸腿，`model.py:L179-L215`）
  - naming: `leg_{i}`，循环 `for i in range(3)`（`model.py:L342-L352`）
  - placement: 角向等分 `angle = 2π·i/3`（120° 间隔），脚底落在 workbench（z≈0）
  - joint policy: **FIXED** —— 三条腿都是 `pump_body` 根刚体上的 visual，无独立关节（静态承托）
  - 建议 N_range: **[3, 6]**（三脚架物理下界=3；采样到 4/5/6 脚泛化为多脚底盘）
  - gating: 仅 `base_style=base_tripod` 时存在

- 局部样本 2（`base_flange` 演示）：
  - count_param: `bolt_count`
  - copied object: 单颗法兰螺栓头（helper `_flange_bolt_shape`，`model.py:L213-L220`）
  - naming: `flange_bolt_{i}`，循环 `for i in range(4)`（`model.py:L347-L360`）
  - placement: bolt-circle 角向等分 `angle = 2π·i/N`，半径 `FLANGE_BOLT_CIRCLE_R`
  - joint policy: **FIXED**（装饰/紧固件复制，非活动件）
  - 建议 N_range: **[3, 8]**
  - gating: 仅 `base_style=base_flange` 时存在

- 备注：两处循环都是纯 `for i in range(N)` + 角向公式发射，copy logic 一眼可读，可直接落成 module-local count_param；其余槽位与 baseline 仍是手写命名 singleton。

## 拓扑多样性审计

总组合数：`4 handle × 4 base × 4 outlet = 64`（若把 `leg_count` / `bolt_count` 局部 N 采样算进去更多，但主多样性来自 slot/module 选择）。

理由：64 个 slot 组合已远超 10；且 outlet slot 单独就改变关节图——`outlet_tapvalve` 引入额外 `tap_to_handle` REVOLUTE，其余 outlet 为 FIXED/无关节；base slot 引入 FIXED 复制循环 vs 命名 singleton；handle slot 改变 PRISMATIC 子件几何但保持关节图，提供 visual-topology 区分。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊。Sampling 先选三个结构槽 enum（各自独立加权），解析 module-local conditional count（`leg_count`/`bolt_count` 仅当对应 base 被选时采样），再采 independent 连续 scale（`stroke_scale`、`barrel_height_scale`），按 equation 派生 `rod_top_z`，最后用 inequality 把 STROKE / knob 间隙投影回可行域。

Topology target：1000-seed slot choice tuple distinct 目标受类别约束偏低——结构槽仅 64 组合、连续 scale 不改关节图，故 distinct 上界约为 64（×outlet 关节图分裂）。低于 300 的原因是这是一个紧致 fork 小类（10 个手读候选）；门控只需 ≥10，已稳过。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版模板包含 `stroke_scale`（行程，independent，clamp 到 bore 净高）、`barrel_height_scale`（barrel 高度，independent）、`rod_top_z`（equation 派生），以及 module-local `leg_count` / `bolt_count`（conditional）。所有连续参数在 `resolve_config` 内 clamp/派生，受 retained-insertion 与 knob-clearance inequality 约束，不破坏 InterfaceSpec / MatingContract。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先选 handle/base/outlet enum（独立加权），再解析 conditional count，再采连续 scale | slot_choices_for_seed matches build choices |
| compatibility matrix | `base_wallbracket × loose_rubber_hose` 降级（软管落地约束与墙挂冲突，改 fallback 到刚性 outlet 或重采）；其余组合合法 | no floating outlet, hose-floor vs wall-mount 冲突, tap axis, captured-pin overlap |
| controlled local variation | `stroke_scale` / `barrel_height_scale` clamp + `rod_top_z` 派生；`leg_count`/`bolt_count` clamp | proportions vary without breaking PRISMATIC retained insertion or knob clearance |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | , MatingContract, tap_to_handle optional child |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| handle | 4 | yes | yes | 1 baseline + 3 fork |
| base | 4 | yes | yes | 1 baseline + 3 fork；2 个含 FIXED 复制循环 |
| outlet | 4 | yes | yes | 1 baseline + 3 fork；tapvalve 加关节 |

## Validator
- slot_choices_for_seed returns implemented module names（handle/base/outlet）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix gates `base_wallbracket × loose_rubber_hose`（hose-floor vs wall-mount 冲突）
- optional regression overrides are sparse and justified（none 初版）
- 两个 hero 关节始终存在：`barrel_to_piston` PRISMATIC（axis `(0,0,-1)`、`upper=STROKE`）+ `yoke_to_lever` REVOLUTE（axis `(0,1,0)`、limits `[-0.5,0.5]`）
- `outlet_tapvalve` 启用时 `tap_to_handle` REVOLUTE 存在（axis `(0,0,1)`、limits `[0, π/2]`）
- retained insertion：piston_head 在 rest 与 full-stroke 都嵌在 barrel bore（allow_overlap，cup 不脱出）
- captured-pin：lever hub bore 抱住 yoke pin（element-scoped allow_overlap）
- handle socket 真实套住 rod 顶端，不得悬空
- base 落地脚底 z≈0（wallbracket 例外为贴墙）；outlet 进口真实套在 `_base_fitting_shape` outlet stub
- module-local `leg_{i}` / `flange_bolt_{i}` 复制遵循命名与角向等分 placement
- cross-part scale dependencies（`rod_top_z` equation、STROKE/knob inequality）resolved in `resolve_config`

## Reject cases
- handle 换成电动马达驱动 → 失去 `barrel_to_piston` PRISMATIC hero 关节，读作电泵。
- 缺 `barrel_to_piston` PRISMATIC 或 `yoke_to_lever` REVOLUTE 任一 hero 关节。
- piston cup 在 full-stroke 脱出 barrel bore（STROKE 过大，违反 retained-insertion inequality）。
- ball_knob 在 rest 或 full-stroke 嵌入 cap（违反 knob-clearance inequality）。
- handle/outlet 悬空或用不可见接口盘连接（handle 未套 rod、outlet 未套 outlet stub）。
- base 既不落地（z≈0）也不贴墙，泵体漂浮。
- `base_wallbracket` 配 `loose_rubber_hose` 时软管"落地"末端与墙挂姿态冲突未降级。
- 把 `leg_{i}` / `flange_bolt_{i}` 复制件做成带独立关节的活动子件（应为 FIXED root visual）。

## 与相邻类别的边界
- 不该混入：electric pump（电泵）——以电动马达/叶轮取代手动柱塞，无 `barrel_to_piston` PRISMATIC 手压冲程；本类 hero 是手动打气行程。
- 不该混入：container/Pump cosmetic dispenser（化妆品/瓶口分配泵）——那是瓶口按压头，是塑料容器的附件；本类是铸件落地/贴墙式机加工泵体，有 barrel + base + 侧向 outlet。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；workbench-only picture-subcat fork（parent 621823e2 + 9 变体）；等待人工审核，审核通过前不进入模板实现 |
