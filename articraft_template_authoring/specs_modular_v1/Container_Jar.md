# Container jar (lidded glass/ceramic storage & cosmetic jar) — Modular Spec

> 来源小类：`picture/Container/Jar`（articraft_data 上游 Container/Jar fork-variant pool）。
> **TEMPORARY fast path（审核同意）**：本小类的 fork 变体是组合式多轴 diff（body × lid × seal），不逐一读 record，直接读 parent + qwen 补造样本的 `model.py` 抽取 slot / module 词汇。
> 引用 `model.py:Lx-Ly` 来自各样本 `articraft_data` 当前 `revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`_jar_glass_solid` / `_body_solid` / `_lid_solid` / `_neck_threads` / `_gasket_ring` / `lid_rotate` / `lid_slide` / `lid_hinge` / `stopper_lift` / `shaker_rotate` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_jar` |
| template path | `agent/templates/Container_Jar.py` |
| test path (optional) | `tests/agent/test_container_jar_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + lid_closure + seal_interior；lid / 内部件挂到 jar_body 共同 parent，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 parent + ~65 qwen fork 变体（3 个 qwen 家族 jar_001 / _002 / _003，各 ~15-27 converged 变体）|
| read_count | 3 parent 全文（face-cream `072e38fe` / square-storage `9e3c6ab6` / square-bottle `7af717d1`）+ qwen 家族头部 + 全量 grep 抽取 lid 机构轴（REVOLUTE X/Y flip、CONTINUOUS+PRISMATIC screw、PRISMATIC lift-off、shaker insert、stopper lift）+ gasket helper（`jar_002_v01` `_gasket_ring`）|
| read_scope | combinatorial fork pool（fast path）：parent 全读，qwen 按 lid-轴 / body-轴 / seal-轴聚类抽样代表样本读 model.py |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

冗余/分流说明：
- 3 parent 中 face-cream（`072e38fe`）与 square-storage（`9e3c6ab6`）是真 jar（screw-cap 旋升机构），采纳为 lid 基线 + body 基线；square-bottle（`7af717d1`）实为 square **BOTTLE**（lift-off 友配帽、tall>>section），按提示**不作 jar body**，仅其 lift-off PRISMATIC 帽机构折入 `lid_closure` 候选。
- qwen jar_001/_002/_003 大量变体只换 body 比例 / 颜色 / gasket 有无 / lid 机构，归并入对应 slot 候选；只换尺寸 / 颜色不另列 candidate。

## 核心身份

带盖的玻璃 / 陶瓷储物 / 化妆品罐（lidded jar）：一只直立中空罐体，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。罐体由 CadQuery `revolve` / `box+shell` 发射为厚壁中空 shell（真实开口腔体），形态可为圆胖化妆罐 / 高圆柱储物罐 / 方角圆边罐 / 多面棱柱（apothecary）/ 圆宽口（mason）/ 收肩罐；罐口上方一只盖按某种机构开合（**主活动语义**）：连续螺纹旋升盖（CONTINUOUS spin + PRISMATIC lift 经 massless carrier）/ 友配抬升盖（纯 PRISMATIC +Z lift-off）/ 后铰翻盖（REVOLUTE 绕后 rim 水平轴）/ 夹扣盖+竖提塞（lid_hinge REVOLUTE + stopper_lift PRISMATIC）/ 撒料旋转插盖（screw 盖 + 内部 shaker 盘绕 +Z REVOLUTE）。可选密封 / 内部件：橡胶 gasket 圈（固定 visual，坐罐口内）/ 底足圈 base rim（固定 visual）/ 无。默认成熟域：单罐单盖（无嵌套 / 无 multiplicity）。

不该混入：细颈高瓶 / 酒瓶（tall narrow neck bottle，是单独的 `container_bottle` 模板——square-bottle parent 即此，已折出 body）、敞口无盖容器 / 收纳箱（无盖机构，是 `bag_suitcase_box`）、带提把可嵌套购物篮（bail 提把 + 嵌套堆叠，是 `shopping_bucket`）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 jar_body（root）的 mesh 属性（一次 `_body_mesh(body_form)` 发射 shell + neck + thread ridges），不是独立串联 slot。`lid_closure` / `seal_interior` 各自挂到 jar_body（parallel children / 固定 visual）。三轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_form（罐体形态 / 足迹——root jar_body 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_squat_cream（基线）| rec_..._072e38fe（face-cream parent）| `_jar_glass_solid` L49-69 + `_neck_threads` L72-87 | eligible if compatible | revolve 圆胖化妆罐（wider-than-tall），圆肩收 neck + 螺纹圈，厚壁开口腔 |
| tall_cylinder_storage | rec_..._jar_001_v03 / 各 jar_001 | `_body_solid` L60-130（tall cyl + wide-mouth rim） | eligible if compatible | 高圆柱储物罐（taller-than-wide），宽口 rim，revolve 圆截面 |
| square_rounded | rec_..._9e3c6ab6（square-storage parent）| `_body_solid` L51-110（box+fillet+shoulder loft+round neck+shell） | eligible if compatible | 方角圆边罐 box shell（filleted vertical edges）→ 收肩 loft → 圆 neck，shell 中空 |
| faceted_apothecary | rec_..._jar_002 family | `_body_solid`（多面棱柱 revolve / 低段数）L60-130 | eligible if compatible | 多面棱柱 apothecary 罐（低 radial 段数 revolve / 棱面），收肩 neck |
| round_wide_mouth_mason | rec_..._jar_003 family | `_body_solid` L?（宽口 mason 罐，short neck + 大口径 rim）| eligible if compatible | 圆宽口 mason 储物罐：罐口直径接近罐身，short thread neck + 宽 rim |
| tapered_shoulder | rec_..._jar_002_v01 | `_body_solid`（圆胖收肩 + 宽口螺纹 neck + gasket 槽）L63-130 | eligible if compatible | 圆收肩罐（squat body → 宽口 threaded neck），明显肩部过渡 |

硬约束记录：body_form 6 candidate（达 3-6 目标上限）。全部 revolve / box-shell 中空开口腔，共享 neck + thread-ridge helper，只换 footprint / 高宽比 / 棱面段数 / rim 口径。

### Slot B：lid_closure（**主开合机构槽**——罐盖动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| continuous_screw_cap（基线）| rec_..._072e38fe / _9e3c6ab6 | `_lid_solid` L120-139 + `lid_rotate` CONTINUOUS L197-205 + `lid_slide` PRISMATIC L223-231（072e38fe）| eligible if compatible | 螺纹旋升盖：经 massless `lid_carrier`，`lid_rotate` CONTINUOUS +Z（旋）+ `lid_slide` PRISMATIC +Z（抬离 neck）；2 joint + 1 massless carrier part |
| lift_off_friction_cap | rec_..._7af717d1（square-bottle，仅借机构）| `_cap_solid` L73-94 + `body_to_cap` PRISMATIC L131-139 | eligible if compatible | 友配抬升盖：单 `body_to_cap` PRISMATIC +Z（无旋转），盖罩 over neck，q=0 坐下 / 正 q 直抬离 |
| rear_hinge_flip_lid | rec_..._jar_001_v03 等 X-轴 REVOLUTE | `lid_hinge` REVOLUTE axis=(1,0,0) origin=后 rim L255-262 | eligible if compatible | 后铰翻盖：盘盖绕后 rim 水平 +X 轴 REVOLUTE，q=0 闭合盖座 rim，正 q 上翻 ~115° |
| clamp_lid_stopper | rec_..._jar_001_v03 | `lid_hinge` REVOLUTE L255-262 + `stopper_lift` PRISMATIC L284-291 | eligible if compatible | 夹扣盘盖（后铰 REVOLUTE）+ 中央竖提橡胶塞（`stopper_lift` PRISMATIC +Z 拔出宽口）；2 活动件（盖 + 塞）|
| shaker_insert_cap | rec_..._jar_001_v08 | `lid_rotate` CONTINUOUS + `lid_slide` PRISMATIC + `shaker_rotate` REVOLUTE +Z L374-382 | eligible if compatible | 撒料盖：screw 盖（rotate+slide）+ 盖内 shaker 圆盘绕 +Z REVOLUTE（对位撒料孔），有限 limit |

硬约束记录：lid_closure 5 candidate（达 3-6 目标）。含 CONTINUOUS / PRISMATIC / REVOLUTE 三种 joint 拓扑 + 多 joint 复合（screw=2、clamp+stopper=2、shaker=3）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。

### Slot C：seal_interior（密封 / 内部件——固定 visual 或无）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| plain（基线）| 各 parent | —（不发射密封件）| eligible if compatible | 无密封 / 内部件（仅罐口螺纹）|
| rubber_gasket_ring | rec_..._jar_002_v01 | `_gasket_ring` L132-141 + `gasket_ring` visual L207 | eligible if compatible | 橡胶 gasket 圆环，坐 neck 口内（固定 visual union/挂 jar_body，无独立 joint）|
| base_foot_rim | rec_..._jar_003 family | revolve 底足圈段（body 底外缘抬起圈）| eligible if compatible | 罐底外缘抬起的 foot rim 圈（固定 visual），罐离地坐于环足 |

硬约束记录：seal_interior 3 candidate（达下限 3）。gasket / foot_rim 均为固定 visual（无独立 joint），plain 为空机构。样本只支持这三族；主多样性由 body_form × lid_closure 提供（见 §9）。

## 槽位图（slot graph）

pattern: parallel_children（jar_body 为 root，lid / 内部件挂到它；无 multiplicity）

```
jar_body(body_form, seal_interior)  [ROOT, 坐地 z=0]
   │  (+ seal_interior 固定 visual: gasket_ring / base_foot_rim，挂 jar_body，无 joint)
   │
   ├── lid_closure = continuous_screw_cap:
   │     jar_body --[lid_rotate: CONTINUOUS +Z @ neck rim top]--> lid_carrier(massless,无 visual)
   │              lid_carrier --[lid_slide: PRISMATIC +Z]--> lid
   │
   ├── lid_closure = lift_off_friction_cap:
   │     jar_body --[body_to_cap: PRISMATIC +Z @ cap seat]--> cap
   │
   ├── lid_closure = rear_hinge_flip_lid:
   │     jar_body --[lid_hinge: REVOLUTE +X @ 后 rim 边, z=rim_top]--> lid
   │
   ├── lid_closure = clamp_lid_stopper:
   │     jar_body --[lid_hinge: REVOLUTE +X @ 后 rim]--> lid
   │     jar_body --[stopper_lift: PRISMATIC +Z @ mouth center]--> stopper
   │
   └── lid_closure = shaker_insert_cap:
         jar_body --[lid_rotate CONTINUOUS +Z]--> lid_carrier(massless)
              lid_carrier --[lid_slide PRISMATIC +Z]--> lid
              lid --[shaker_rotate: REVOLUTE +Z @ lid 内]--> shaker_disc
```

接口点位与 joint 语义：
- **screw / shaker 接口**：`lid_rotate` origin 落在 neck rim top 中心 `(0,0,RIM_TOP_Z)`，axis +Z（CONTINUOUS）；`lid_slide` 经 massless `lid_carrier`（无 visual），axis +Z（PRISMATIC，q=0 坐下、正 q 抬离）。carrier 解耦旋转 / 平移共享 +Z。shaker 的 `shaker_rotate` origin 在 lid 内盘面中心，axis +Z，REVOLUTE 有限 limit。
- **lift-off 接口**：`body_to_cap` origin 在 cap 罩下口坐位 z（cap skirt 罩 over neck），axis +Z PRISMATIC（无旋转），q=0 罩下 / 正 q 直抬离。
- **flip / clamp 接口**：`lid_hinge` origin 在后 rim 边硬件（`(0, -NECK_OUTER_R, RIM_TOP_Z)` 类），axis +X，REVOLUTE 闭合 q=0、上翻正 q；clamp 的 `stopper_lift` origin 在 mouth 中心、axis +Z PRISMATIC（拔塞）。
- **seal 接口**：gasket_ring / base_foot_rim 为固定 visual，挂 jar_body（无独立 joint）；gasket 坐 neck 口内、foot_rim 在罐底外缘。
- **mating policy**：盖 skirt 罩 over neck rim 是 captured / 友配（盖壁与 neck 几何故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 rim / hinge 硬件）+ element-scoped `allow_overlap(lid↔jar_body 的 skirt↔glass)` 守 overlap（见各 parent run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有盖 q=0 闭合 / 坐下；stopper q=0 塞入口；shaker q=0；gasket / foot_rim 固定。lid 旋转 / 抬升 / 翻起为 viewer 目检的活动语义。
- **互斥 / 可选**：`seal_interior=plain` 是空机构（不发射密封件）；lid_closure 各候选互斥（一次只一种盖机构）。`lid_carrier` massless part 仅在 screw / shaker 候选发射。

## 每槽位 Module Emits / Interfaces

### Slot A / jar_body（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `jar_body`（visual: `jar_glass` shell + neck thread ridges[ + seal_interior 固定 visual]）| 072e38fe `_jar_glass_solid` L49-69 / 9e3c6ab6 `_body_solid` L51-110 |
| internal joints | 无（root 罐体本身无活动件）| — |
| upstream interface | 坐地 z=0（root）| — |
| downstream interface | neck rim top 中心（lid joint 的 parent 接口）| 072e38fe RIM_TOP_Z L36 |

### Slot B / lid_closure（每候选发射对应活动盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`(+`lid_carrier` massless) / `cap` / `lid`+`stopper` / `lid`+`shaker_disc` | 各 lid 源 |
| internal joints | `lid_rotate` CONTINUOUS +Z + `lid_slide` PRISMATIC +Z（screw）/ `body_to_cap` PRISMATIC +Z（lift-off）/ `lid_hinge` REVOLUTE +X（flip）/ `lid_hinge`+`stopper_lift`（clamp）/ +`shaker_rotate` REVOLUTE +Z（shaker）| 072e38fe L197-231 / 7af717d1 L131-139 / jar_001_v03 L255-291 / jar_001_v08 L374-382 |

### Slot C / seal_interior（≠plain 时，固定 visual 挂 jar_body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（gasket_ring / base_foot_rim 为 jar_body 的固定 visual）| jar_002_v01 `_gasket_ring` L132-141 |
| internal joints | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | round_squat_cream / tall_cylinder_storage / square_rounded / faceted_apothecary / round_wide_mouth_mason / tapered_shoulder | round_squat_cream | choice | deterministic procedural sampler 选 | module table |
| lid_closure | enum | continuous_screw_cap / lift_off_friction_cap / rear_hinge_flip_lid / clamp_lid_stopper / shaker_insert_cap | continuous_screw_cap | choice | sampler 选 | module table |
| seal_interior | enum | plain / rubber_gasket_ring / base_foot_rim | plain | choice | sampler 选；含空机构 | module table |
| material_style | enum | blue_glass / clear_glass / amber_glass / frosted_white / ceramic_cream / brass_lid | blue_glass | palette | palette only，**不计入 slot_choice** | palette |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放罐体高度 H → RIM_TOP_Z → lid mount 高度，clamp | resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体半径 / 半宽 → neck R 同比，clamp（保盖罩配合）| resolve clamp |
| neck_radius_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；lid bore / cap skirt 半径派生跟随（保罩配合）| resolve clamp |
| lid_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放盖高 / skirt 深，clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lid_slide / stopper_lift 行程 + hinge limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`lid_bore_R ≥ NECK_R + clearance` 且 `lid_outer_R ≤ body_R + proud`，违反按比例回缩 lid_height/neck scale | 接口 / clearance |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（lid bore / cap skirt 半径跟随 neck 半径，保证盖罩 neck 的配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / lid_closure / seal_interior 的拓扑。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + lid_closure + seal_interior）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单罐单盖。

## 拓扑多样性审计

总组合数：body_form(6) × lid_closure(5) × seal_interior(3) = **90**。

仅 body_form × lid_closure = **30 ≥ 10** 已可过门控；叠 seal_interior 后充裕。

理由：本类拓扑多样性来源充裕——body_form(6) × lid_closure(5) 的笛卡尔积即 30 distinct，远超 10；lid_closure 引入 CONTINUOUS+PRISMATIC（screw 2 joint + massless carrier）/ PRISMATIC（lift-off）/ REVOLUTE +X（flip）/ REVOLUTE+PRISMATIC（clamp+stopper 2 活动件）/ +REVOLUTE +Z（shaker 3 joint）等不同 joint 拓扑 + 不同 part count，是真实结构差异。seal_interior 在 plain↔gasket↔foot_rim 间改 jar_body visual 组。slot_choices 编入三轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 gating 见下），再 uniform 各连续 scale + `rng.choice` palette。compatibility matrix 排除非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 90（90 组合的采样空间足够；受真实词汇表约束的轴是 seal_interior(3)，但 body_form(6) × lid_closure(5) 已撑开 30）。低于 300 的原因：本小类真实结构词汇就是 6 body × 5 lid × 3 seal = 90，是该类目的合理上限，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / neck_radius / lid_height / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（lid bore / cap skirt 半径派生跟随）。盖罩配合不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 lid joint origin（neck rim top / 后 rim hinge / mouth center）、盖罩 neck 配合、seal 位置或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），再 uniform 各 scale + palette | slot_choices_for_seed 含三轴且与 build 一致 |
| compatibility matrix | (1) `clamp_lid_stopper` 与 `rear_hinge_flip_lid` 需要宽口 rim 才能下塞 / 翻盖 → body_form ∈ 含宽口的形态时优先；窄口 body_form 仍可用但 stopper / flip 尺寸按 rim 口径派生（resolve 解析，不 gate 掉，保多样性）。(2) `lift_off_friction_cap` 盖罩 over 整个上身 → neck 处理为 cap skirt 罩配合（不发射独立长 neck，避免穿模）。(3) 各 lid_closure 互斥。(4) seal=base_foot_rim 与任意 body_form / lid 正交。无硬 gate-out（90 组合全合法，只在 resolve 派生尺寸适配）| 无 floating / collision / lid 穿罐 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_radius equation 驱动 lid bore | 比例变化不破坏 lid joint origin / 盖罩配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | lid 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 6 | yes | yes | revolve / box-shell 罐体六族 |
| lid_closure | 5 | yes | yes | screw(CONT+PRIS) / lift-off(PRIS) / flip(REV X) / clamp+stopper(REV+PRIS) / shaker(+REV Z) |
| seal_interior | 3 | yes | yes | plain 空 + gasket 固定圈 + foot_rim 固定足 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, lid_closure, seal_interior) 三轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 lid bore；盖罩配合不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：90 组合全合法（无硬 gate-out），窄口 body 时 stopper / flip 尺寸按 rim 口径在 resolve 派生
- 连续 scale clamp 后不破坏 lid joint origin / 盖罩配合 / 坐地 / 类别身份
- 关键 joint：screw `lid_rotate` CONTINUOUS +Z (abs(axis[2])>0.99) + `lid_slide` PRISMATIC +Z + massless `lid_carrier`（无 visual）；lift-off `body_to_cap` PRISMATIC +Z；flip `lid_hinge` REVOLUTE +X (abs(axis[0])>0.99)；clamp +`stopper_lift` PRISMATIC +Z；shaker +`shaker_rotate` REVOLUTE +Z 有限 limit
- captured-fit：element-scoped `allow_overlap(lid skirt ↔ jar glass)`（盖罩 neck rim）；shaker disc ↔ lid 内壁；stopper ↔ neck rim
- grandfather：盖罩 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用 boxy 占位体（纯 Box）当圆罐 body → 失类别身份；圆 body 必须 revolve / lathe，方 body 用 box+fillet+shell。
- lid joint origin 放在罐底 / 任意点而非 neck rim top / 后 rim hinge / mouth center 真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- screw 盖不用 massless carrier 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 lid 单 part → 旋转与抬升耦合错误（应 body→carrier→lid 两 joint）。
- lid_closure rest pose 设成张开 / 抬起而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- 给盖罩 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（material_style 是 palette，不计 slot_choice）。
- 把 square-bottle parent 当 jar body 塞回 body_form → 出 jar 语义（是细颈 bottle，归 `container_bottle`）。
- lid 抬升 / flip 时穿罐壁 / origin 漂移 → 盖罩配合不等式或 origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_bottle 细颈瓶 / 酒瓶**（tall narrow neck，square-bottle parent 即此，已折出 body 仅借 lift-off 帽机构）——理由：bottle 是细长瓶身 + 长颈，jar 是宽口罐身。
- 不该混入：**bag_suitcase_box / 通用容器收纳箱**（无盖开合机构）——理由：jar 的类别身份是带盖开合的罐口。
- 不该混入：**shopping_bucket 购物篮**（bail 提把 + 可嵌套堆叠）——理由：jar 无提把、无 multiplicity，是单罐单盖。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | Approved per the two-phase task directive (write spec first, then implement in the same session). 6 body × 5 lid × 3 seal = 90 combos; body×lid=30 clears . screw=massless carrier 解耦、clamp=lid+stopper 双活动件、shaker=3 joint；seal 三候选；无 multiplicity 轴；square-bottle 仅借 lift-off 帽机构不作 body。|

## 模板实现备注（可选）

- 共享 helper：`_revolve_body(profile_pts, segments)`（圆 / 棱面 body）+ `_box_shell_body`（方 body）+ `_neck_with_threads(neck_r, rim_z)` + `_gasket_ring` + `_foot_rim` 全 module 公用。圆 body 用 CadQuery `revolve` + `mesh_from_cadquery`；方 body 用 `box`+`fillet("|Z")`+shoulder loft+shell+cut。
- screw / shaker：必须经 massless `lid_carrier`（无 visual，1e-4 mass Box inertial）解耦 `lid_rotate`(CONTINUOUS)→`lid_slide`(PRISMATIC)；shaker 再挂 `shaker_rotate`(REVOLUTE +Z 有限 limit) 到 lid。
- captured-fit overlap：`run_container_jar_tests` 里 `ctx.allow_overlap(lid, jar_body, elem_a=lid_skirt, elem_b=jar_glass, reason="盖 skirt 罩 over neck rim")`；clamp 的 stopper ↔ neck、shaker disc ↔ lid 内壁同理。
- neck_radius equation：`resolve_config` 派生 `lid_bore_R = NECK_R + clearance`、`cap_skirt_R = body_R + proud`，盖罩配合不等式在 resolve 投影。
- 参考模板：`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig dataclass + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` 报 topology family + `build_<stem>` + `run_<stem>_tests` 的 allow_overlap + element-scoped grandfather 骨架）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（captured-pin allow_overlap + 多 lid 机构分支）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | round_squat_cream + continuous_screw_cap | rec_..._072e38fe | `_jar_glass_solid` L49-69 / `_neck_threads` L72-87 / `_lid_solid` L120-139 / `lid_rotate`+`lid_slide` L197-231 | 圆罐 body 基线 + screw-cap 旋升机构 + massless carrier |
| S2 | A/B | square_rounded + continuous_screw_cap | rec_..._9e3c6ab6 | `_body_solid` L51-110 / `_thread_ridges` L113-126 / `_lid_solid` L134-170 / `lid_rotate`+`lid_slide` L210-227 | 方角圆边罐 body + screw-cap |
| S3 | B | lift_off_friction_cap | rec_..._7af717d1 | `_cap_solid` L73-94 / `body_to_cap` PRISMATIC L131-139 | 友配抬升帽机构（仅借机构，body 折出归 bottle）|
| S4 | A/B/C | tapered_shoulder + gasket | rec_..._jar_002_v01 | `_body_solid` L63-130 / `_gasket_ring` L132-141 / gasket visual L207 | 收肩罐 body + 橡胶 gasket 圈 |
| S5 | A/B | tall_cylinder_storage + clamp_lid_stopper | rec_..._jar_001_v03 | `_body_solid` L60-130 / `lid_hinge` REVOLUTE L255-262 / `stopper_lift` PRISMATIC L284-291 | 高圆柱储物罐 + 后铰夹扣盖 + 竖提塞 |
| S6 | B | shaker_insert_cap | rec_..._jar_001_v08 | `lid_rotate`+`lid_slide` + `shaker_rotate` REVOLUTE +Z L374-382 | 撒料盖（screw + 盖内旋转盘）|
| S7 | A | faceted_apothecary | rec_..._jar_002 family | `_body_solid`（低段数 revolve / 棱面）L60-130 | 多面棱柱 apothecary body |
| S8 | A | round_wide_mouth_mason | rec_..._jar_003 family | `_body_solid`（宽口 short neck）| 圆宽口 mason body |
| S9 | C | base_foot_rim | rec_..._jar_003 family | revolve 底足圈段 | 罐底环足固定圈 |
| S10 | B | rear_hinge_flip_lid | rec_..._jar_001 X-轴 REVOLUTE 变体 | `lid_hinge` REVOLUTE axis=(1,0,0) L255-262 | 后铰翻盖 |
