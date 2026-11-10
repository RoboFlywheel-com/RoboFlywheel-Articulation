# Modular Spec — trumpet

## 元信息
| 项 | 值 |
|---|---|
| slug | `trumpet` |
| template path | `agent/templates/trumpet.py` |
| test path (optional) | `tests/agent/test_trumpet_template.py` (skipped while authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel-children body + valve/slide multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in `0611__trumpet` source map (2 origins + 10 forked anchors) |
| source_index_policy | only adopted module sources are indexed below |

两条 build 血脉（同一运动学骨架，不同 primitive 组织）：
- **L1 (001 血脉)** — `_shell_mesh`(Lathe hollow) 阀套/滑管套 + `_tube_mesh` 铅管/铃尾 + Lathe 铃/号嘴 + Torus 铃缘/指环 + 单 water_key。origins/pocket/herald/bass/rotary/top_sprung。
- **L2 (002 血脉)** — merged `valve_block` MeshGeometry（`_hollow_tube`+`_ring_band`+Cylinder）+ `_tube` 静管网 + Lathe 铃/号嘴 + 双 water_key。origin_002/piccolo/valve_count_3-4/slide_control_*。

两血脉 identity 完全一致：固定 `trumpet_body`（铃+铅管+阀套+滑管套+指环/挂钩+号嘴，全部 fused visuals）根，其下挂 N 个活塞/回旋阀 (PRISMATIC/REVOLUTE)、主调音滑管 (PRISMATIC)、三阀滑管 (PRISMATIC)、以及 spit/water key（sources 里是 REVOLUTE 独立件；本模板按 Rule 1 融为宿主 visual，见备注）。模板统一采用 L1 的 primitive 组织（更自包含、Lathe/tube/torus 一致），并按 body_family 参数化铃母线与机身长度。

## 核心身份

黄铜小号（B♭ trumpet 家族）：保留**铃 (bell flare)** 张口、**号嘴 (mouthpiece) 进气路**、**紧凑的阀控管路 (valve-controlled tubing)**。核心运动学：一个 grounded `trumpet_body` 携带 3–4 个独立按键阀 (piston 竖直下压 PRISMATIC / rotary 竖轴 REVOLUTE) 与 1–2 根可拉出调音滑管 (PRISMATIC)。默认成熟域 = 侧视、铃朝 −X、号嘴朝 +X 的抛光黄铜/银镀小号。

不该混入：
- **trombone**：小号靠**阀**改变音高（短紧凑管路 + 竖直阀簇），长号靠一根**长伸缩手滑管**；小号必须保留阀机构，不得退化成单根长 PRISMATIC 手滑管主轴。
- **bugle without valve mechanism**：军号无阀；本类别必须至少有一组可动阀 (valve_count ≥ 3) —— 无阀即出界。

## 槽位 + 候选模块表

### Slot A：body_family（③ 主体形态家族 / Primary Form Family，主视觉多样性）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| standard | forked_anchor | `rec_picturex_0611__trumpet__001...` | L75-L142 | eligible if compatible | 全长 B♭：Lathe 铃 rim≈0.058/len≈0.186，直铅管，标称机身 |
| pocket | forked_anchor | `rec_0611_trumpet_var_body_family_pocket_trumpet` | L81-L155 | eligible if compatible | 口袋号：短宽铃 rim≈0.068/len≈0.118，卷绕紧凑铅管，机身 L≈0.72× |
| piccolo | forked_anchor | `rec_0611_trumpet_var_body_family_piccolo_trumpet` | L57-L191 | eligible if compatible | 高音短号：小铃 rim≈0.049/len≈0.148，短铅管，机身 L≈0.80× |
| herald | forked_anchor | `rec_0611_trumpet_var_body_family_herald_trumpet` | L53-L155 | eligible if compatible | 礼号/长号角：长直铃 len≈0.30，长机身 L≈1.25×，最小折叠 |
| bass | forked_anchor | `rec_0611_trumpet_var_body_family_bass_trumpet` | L54-L155 | eligible if compatible | 低音号：大铃 rim≈0.075/len≈0.24，长机身 L≈1.20× |

`form_subtype = Volumetric Envelope Form`（改变铃 flare 的 Lathe 母线 throat/rim/len/exp + 机身包络长度；同一 part tree/primitive/interface）。5 个可识别原型，满足 ≥3。

### Slot B：valve_mechanism（② 关节类型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| piston | forked_anchor | `rec_0611_trumpet_var_valve_mechanism_top_sprung_piston_valv` | L418-L478 | eligible if compatible | 竖直活塞：stem+guide_piston(套内)+button，PRISMATIC 沿 −Z 下压 |
| rotary | forked_anchor | `rec_0611_trumpet_var_valve_mechanism_rotary_valves` | L411-L451 | eligible if compatible | 回旋阀：rotor_stem(套内)+hub+finger paddle，REVOLUTE 绕 +Z |

2 候选（degrade 到 2 有理由）：valve_mechanism 是纯②关节类型轴，源池只提供 piston / rotary 两种真实机构，无第三种结构不同的阀机构源锚点；不虚构。两者都是 forked_anchor 支撑，且是本类别唯一强②轴，接受 2。

### Slot C：slide_control（② 关节类型 / 附加触发件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| dual_pull | forked_anchor | `rec_picturex_0611__trumpet__001...` / `__002...` | L432-L543 / L355-L467 | eligible if compatible | 主调音滑管 PRISMATIC −X + 三阀滑管 PRISMATIC +X，无触发件 |
| first_valve_trigger | forked_anchor | `rec_0611_trumpet_var_slide_control_first_valve_trigger` | L410-L457 | eligible if compatible | 在第一阀旁增一根 REVOLUTE 拇指触发杆 `first_valve_trigger` + 双 PRISMATIC 滑管 |
| main_slide_trigger | forked_anchor | `rec_0611_trumpet_var_slide_control_main_slide_trigger` | L376-L450 | eligible if compatible | 在主滑管鞍座增一根 REVOLUTE 触发杆 `main_slide_trigger` + 双 PRISMATIC 滑管 |

两 trigger 候选结构差异 = 触发 REVOLUTE 件的**附着点/驱动滑管不同**（valve0 前端 vs 主滑管后端），各由独立 fork 支撑，非 re-skin；dual_pull 无触发件。

### Multiplicity 轴：valve_count（N，见 §8）
3 / 4 阀（`rec_0611_trumpet_var_valve_count_3_valves` L24-L227 / `..._4_valves` L22-L228）。同构阀件 ×N 沿 X 均布。

## 槽位图（slot graph）

pattern: mixed（parallel_children 为主 + valve/slide 各自 multiplicity）

```
trumpet_body (Slot A, root, FIXED ground)
  ├─[PRISMATIC −Z (piston) | REVOLUTE +Z (rotary)]→ valve_0 .. valve_{N-1}   (Slot B × valve_count N)
  ├─[PRISMATIC −X]→ main_slide           (Slot C: dual_pull / *_trigger)
  ├─[PRISMATIC +X]→ third_slide          (Slot C: all)
  └─[REVOLUTE +Z]→ {first_valve_trigger | main_slide_trigger}  (Slot C: trigger variants only)
```

接口点位：
- **valve_i ↔ body**：阀套 (`valve_casing_i`, 竖直 hollow cylinder) 内壁捕获 valve stem/rotor stem。joint origin 在阀套中心线（+Z 对称轴），axis piston=−Z / rotary=+Z。captured-pin → 关节 **omit MatingContract**（grandfather），tests 里 element-scoped allow_overlap(casing↔stem/piston)。
- **main_slide ↔ body**：滑管公管插入固定 `main_slide_sleeve` 母套；joint origin 在套口，axis −X。telescoping → omit MatingContract，element-scoped allow_overlap(u_tube↔sleeve/feed/return)。
- **third_slide ↔ body**：同上，axis +X，`third_slide_sleeve`。
- **trigger ↔ body**：REVOLUTE +Z，pivot pin 捕获在 body 鞍座 boss；omit MatingContract，allow_overlap(pin↔boss)。

所有 cross-slot joint 都以 `trumpet_body` 为 parent（parallel children）；触发件是 slide_control 变体独有的可选 moving child。

## 每槽位 Module Emits / Interfaces

### Slot A / body_family
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trumpet_body`（根） | 001 L72 |
| visuals | bell_shell(Lathe)、bell_rim(Torus)、bell_tail+leadpipe(tube sweep)、mouthpiece_receiver(Cyl)、mouthpiece(Lathe)、valve_casing_i+top/bottom_cap+port、valve_bridge、main/third_slide_sleeve_{0,1}、slide feed/return(tube)、leadpipe/bell_brace、finger_ring(Torus)+stem、pinky_hook(tube)、water_key(融入宿主，见备注) | 001 L75-L387 |
| internal joints | 无（根，固定） | — |
| downstream interface | body 承接所有 parallel children 的 joint origin（阀套中心线、滑管套口） | 001 关节 origin |

### Slot B / valve_mechanism（× valve_count N）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `valve_0..valve_{N-1}` | 001 L390-L415 / rotary L411 |
| internal joints | piston: `valve_i_press` PRISMATIC axis −Z lower0 upper≈0.012；rotary: `valve_i_turn` REVOLUTE axis +Z lower0 upper≈0.5 | 001 L416-L429 / rotary L441 |
| upstream interface | valve stem/rotor 捕获于 body `valve_casing_i`；joint origin 阀套中心线 | 001 L416-L429 |

### Slot C / slide_control
| emits | 描述 | 来源 |
|---|---|---|
| parts | `main_slide`、`third_slide`，(+trigger 变体：`first_valve_trigger` 或 `main_slide_trigger`) | 001 L432/L493 / fork L410 |
| internal joints | `main_slide_pull` PRISMATIC −X (0..≈0.018)；`third_slide_pull` PRISMATIC +X (0..≈0.020)；trigger: `operate_<trigger>` REVOLUTE +Z (0..≈0.35) | 001 L477/L530 / fork L457 |
| upstream interface | 滑管公管插固定套；trigger pin 捕获宿主 boss；均 parent=body | 001/fork 关节 |

活动件均有 articulation 语义；不动细节（铃缘、指环、挂钩、鞍座、water key touch-cork）写成宿主 visual。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_family | enum | standard/pocket/piccolo/herald/bass | standard | choice | procedural sampler | Slot A |
| valve_mechanism | enum | piston/rotary | piston | choice | procedural sampler | Slot B |
| slide_control | enum | dual_pull/first_valve_trigger/main_slide_trigger | dual_pull | choice | procedural sampler | Slot C |
| valve_count | int | {3,4} 权重(0.7,0.3) | 3 | choice | multiplicity 加权采样 | §8 |
| palette_style | enum | 见 §8.5 ⑥（5 档） | polished_brass | choice | procedural sampler | 源材质 |
| frame_scale | float | [0.90, 1.12] | 1.0 | independent | 均匀采样后 clamp | 整体相似缩放 |
| valve_travel_scale | float | [0.85, 1.0] | 1.0 | independent | 采样后 clamp | 001 L423 upper |
| slide_extension_scale | float | [0.80, 1.0] | 1.0 | independent | 采样后 clamp | 001 L488 upper |
| s (global similarity) | float | derived | 1.0 | equation | `s = frame_scale * form_scale[body_family]` | 母线保形 |
| (—) | constraint | — | — | inequality | 主/三阀滑管行程 `≤ 套内可行程 − MIN_ENGAGE`，超出按比例回缩 | telescoping 保留插入 |
| (—) | constraint | — | — | inequality | 阀行程 `≤ guide_piston 在套内可退让深度`，保 retained | 001 L399/L423 |

所有 equation/inequality 在 `resolve_config` 求解并 clamp。

### 7.5 编译预算 / compile budget（必填）

**每-seed 预算 ≤ 12s（目标），hang-guard `--compile-timeout 120`。** 依据：几何全部为 Lathe 铃壳/号嘴 + `tube_from_spline_points` 铅管/滑管 + hollow-shell Lathe 阀套/滑管套 + Cylinder/Torus/Box，无 cadquery 布尔、无重雕刻——与已过 sweep 的 sibling `trombone`（≤12s）同量级，实际更接近典型 5–20s 档。分档 tessellation：铃母线 hero 面 ≤72 段、号嘴 ≤48、阀套/滑管套 ≤40、小 Torus/Cylinder ≤20–24 段。N 个同构阀件复用同一 `Mesh`（casing/piston 各建一次）。超预算先降精度。

## Multiplicity / Copy Logic

**轴 1：valve_count**
- `count_param`：`valve_count`；`N_range`：产品域 {3,4}（源锚点上限，真实小号极少 >4）；sampling domain 权重 {3:0.7, 4:0.3}（3 阀高频，4 阀稀有）。
- copied object：`valve_{i}` 阀件（piston 或 rotary，同构，共享 mesh）；naming `valve_{i}` / joint `valve_{i}_press|turn`；placement：沿 X 均布 `x_i = (i-(N-1)/2)*valve_spacing`；joint policy：每阀独立 PRISMATIC/REVOLUTE，统一 travel。
- source/gating：`..._valve_count_3_valves` / `..._4_valves`。valve_spacing 恒定 → 4 阀时阀簇更宽，滑管套 x 位随簇宽派生。

（water_key 不设 multiplicity 轴：sources 有 0/1/2，本模板一律融为宿主 visual，无独立轴——见 §8.5 ①-multiplicity。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | slide_control 加/减 trigger REVOLUTE 件（dual_pull 无 / *_trigger 有一根）；valve_count 改阀件数。均 forked_anchor 支撑（slide_control_* / valve_count_* forks） |
| └ multiplicity | 同构件 ×N | 有 | valve_count {3,4} 权重(0.7,0.3)，见 §8；water_key 融宿主不设轴 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | valve_mechanism：piston PRISMATIC−Z / rotary REVOLUTE+Z（两种都必须在 sweep 出现）；slide_control trigger 引入 REVOLUTE+Z。forked_anchor(rotary/top_sprung/slide_control_* forks) |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | body_family 5 档（standard/pocket/piccolo/herald/bass），form_subtype=Volumetric Envelope Form（铃 Lathe 母线 throat/rim/len/exp + 机身长度包络）；登记进 `slot_choices`。forked_anchor(body_family_* forks) |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有(record_only) | 铃缘 Torus band、指环/挂钩、阀顶帽、鞍座——均宿主 visual，随铃 rim 半径与机身长度 host-conformal 派生（bell_rim 半径 = 铃母线 rim_r；派生顺序 ③→⑤→④）。不新增装饰计数轴 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | frame_scale[0.90,1.12]、valve_travel_scale[0.85,1.0]、slide_extension_scale[0.80,1.0]。运动包络见下 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal（黄铜/银镀）；palette_style 5 档（见下），材质大类覆盖 ≥ ceil(0.5×5)=3（含 brass 系 + silver-plate + rose/dark 变体） |

**⑤ 运动包络 + motion_test_plan：**
- `valve_i_press`(piston)：axis −Z，闭合0 → 上界≈0.012·s·valve_travel_scale；`valve_i_turn`(rotary)：axis +Z，0 → ≈0.5·valve_travel_scale rad。
- `main_slide_pull`：axis −X，0 → ≈0.018·s·slide_ext；`third_slide_pull`：axis +X，0 → ≈0.020·s·slide_ext。
- `operate_<trigger>`：axis +Z，0 → ≈0.35 rad。
- motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)`（≥6 独立关节时降到 32）；每机构一条 targeted `ctx.pose(...)`：阀下压/回旋 paddle 位移、主滑管 −X 伸出、三阀滑管 +X 伸出、trigger paddle 摆动；telescoping/captured overlap 用 element-scoped allow_overlap 保 retained insertion，非 broad。无 sampled-pose exemption。

**⑥ palette_style（≥3，目标 4–6；均取自 5★ 源材质）：**
1. `polished_brass`（001：warm_bell + polished_brass + nickel_silver + pearl button）
2. `bright_lacquer`（002：bright_brass 铃 + polished_brass 机身 + silver_plate 号嘴 + dark_felt inlay）
3. `silver_plated`（银镀主体 + 金色 trim + silver 号嘴/阀杆）
4. `rose_brass`（玫瑰铜暖色 + 深铜 ferrule + 银亮件）
5. `dark_lacquer`（深色漆机身 + 暗铜 + 冷银亮件）

**收尾自检**：body_family 5 形态拉得开、piston/rotary 与 trigger 有/无都出现、palette 5 档肉眼可辨、装饰贴铃面不悬空、阀/滑管全程不穿模。

## 采样与覆盖审计

总组合数：body_family(5) × valve_mechanism(2) × slide_control(3) × valve_count(2) = **60** discrete slot-combo，再叠加连续 scale + palette(5)。

理由：源池为 2 origins + 10 forks，离散轴组合空间受源锚点上限约束（60）。Topology target 说明：60 < 300，因真实 5★ 源只支撑这 4 轴 × 各自档位；不虚构额外 skeleton/joint 候选来凑数（report-only，不 gate，不反推上游变体数）。1000-seed slot tuple 覆盖用于成熟度观察。

seed_domain_policy：procedural_first（seed=0 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对 4 个离散轴 `rng.choice` / valve_count 加权 `rng.choices`，对 3 个连续 scale `rng.uniform` 后 clamp，对 palette_style `rng.choice`。compatibility：所有轴独立可组合（无非法对）——任意 body_family × 任意 mechanism × 任意 slide_control × 任意 count 都能装配（阀套/滑管套位置随 body 与 valve_count 派生）。无 regression overrides。random sweep 0-35 初过，0-999 成熟度审计；viewer 目检 0-9。

Controlled local parameterization：frame_scale / valve_travel_scale / slide_extension_scale（§7 约束类型：independent；s = frame_scale·form_scale 为 equation；两条滑管/阀行程 inequality 在 resolve_config 回缩）。不破坏 captured-pin/telescoping 间隙、joint origin、类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 body→valve_mech→slide_ctrl→count；rng.choice/choices；连续 clamp | slot_choices_for_seed == build choices |
| compatibility matrix | 全兼容（无互斥对）；valve_count 改阀簇宽 → 滑管套 x 派生 | 无 floating/collision/axis/max-mult/bulky/optional-child 失败 |
| controlled local variation | 3 个 scale + clamp/派生 | 比例变化不破坏接口/间隙/支撑/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-35 初过，0-999 成熟度 | contract 失败；axis_realization；viewer 目检 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_family | 5 | yes | yes | ③ 主形态 |
| valve_mechanism | 2 | yes | no | ②，源池仅 2 真实机构，degrade 有理由 |
| slide_control | 3 | yes | yes | ② + 触发件 |
| valve_count(mult) | 2 | yes | no | N 轴，产品域 {3,4} |

## Validator

- slot_choices_for_seed 返回已实现 module 名（4 元组：body_family/valve_mechanism/slide_control/valve_count）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility：全兼容，无非法组合；valve_count 派生阀簇宽与滑管套位置
- 无 regression overrides；主 seed domain 非 curated/modulo 表
- frame/valve_travel/slide_extension scale 均 clamp，行程 inequality 在 resolve_config 回缩，不破坏 telescoping/captured 间隙
- 关键 joint 类型/轴：valve piston=PRISMATIC−Z / rotary=REVOLUTE+Z；main=PRISMATIC−X；third=PRISMATIC+X；trigger=REVOLUTE+Z
- captured-pin/telescoping 关节 omit MatingContract 并在 tests 里 element-scoped allow_overlap（非 broad part-level）
- copied valve_{i} 遵循 naming/placement 政策

## Reject cases

- 阀件数 < 3 或无阀（退化成 bugle）——出界。
- 用单根长 PRISMATIC 手滑管当主轴、丢掉阀簇（退化成 trombone）。
- 铃退化成 Cylinder（丢 Lathe 母线）或 body_family 之间铃/机身长度不可辨（③ 塌缩）。
- telescoping 滑管在任意行程脱出母套（retained insertion 失败）或阀 guide 脱出套。
- broad part-level allow_overlap 掩盖真实穿模；trigger/阀 REVOLUTE 全程 paddle/stem 穿模。
- palette 单一（全部 monochrome，palette_style 未驱动 .visual material）。
- 装饰（铃缘/指环）常数半径悬浮于缩放铃面外（非 host-conformal）。
- 连续 scale 极值下 joint origin 偏离硬件 >15mm 或滑管/阀行程 inequality 未回缩致穿模。

## 与相邻类别的边界

- 不该混入：**trombone**（长号靠长伸缩手滑管改音、无阀簇；小号必须保留 3–4 阀竖直阀机构与短紧凑管路）。
- 不该混入：**bugle without valve mechanism**（军号无阀；本类别至少 3 阀）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 直接进入模板实现（P3+P4 连续，无 spec 审批停顿） |

## 模板实现备注（可选）

- water_key（sources 里 001 单件 REVOLUTE / 002 双件 REVOLUTE）按 AUTHORING §A Rule 1 融为**宿主 visual**（saddle+lever+cork），不设独立 part/joint——与已过 sweep 的 sibling `trombone` 一致，降 joint 数、控 motion QC 预算。不作为声明 slot。
- 统一采用 L1(001) 的 primitive 组织：`_shell_mesh`(Lathe hollow) 阀套/滑管套、`_tube_mesh` 铅管/铃尾/滑管、Lathe 铃/号嘴、Torus 铃缘/指环。全局 `s` 缩放每个坐标/半径以保母线。
- captured-pin(阀 stem↔casing、trigger pin↔boss) + telescoping(滑管 u_tube↔sleeve/feed/return) 关节 **omit MatingContract**（Rule 2 grandfather），在 `run_trumpet_tests` 里逐-element `ctx.allow_overlap(...)` 声明。
- 阀套/滑管套 x 位随 valve_count 阀簇宽派生（Contract 3c 单源 helper `_valve_x(r)`）。
- bell_z（铃轴高度）单源自 rim_r（`_bell_z(r)`），保证铃 flare 始终清越顶部铅管（Rule 4/Contract 3c）。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | standard | rec_picturex_0611__trumpet__001... | L75-L387 | 主 body primitive 组织 + 全 fused visuals + 关节 origin |
| S2 | A | (bell 母线参考) | rec_picturex_0611__trumpet__002... | L57-L121 | 铃/号嘴 Lathe 母线备选 |
| S3 | A | pocket | rec_0611_trumpet_var_body_family_pocket_trumpet | L81-L155 | 短宽铃 + 卷绕铅管母线 |
| S4 | A | piccolo | rec_0611_trumpet_var_body_family_piccolo_trumpet | L57-L191 | 小铃 + 短机身 |
| S5 | A | herald | rec_0611_trumpet_var_body_family_herald_trumpet | L53-L155 | 长直铃 + 长机身 |
| S6 | A | bass | rec_0611_trumpet_var_body_family_bass_trumpet | L54-L155 | 大铃 + 长机身 |
| S7 | B | piston | rec_0611_trumpet_var_valve_mechanism_top_sprung_piston_valv | L418-L478 | 活塞 PRISMATIC−Z + guide 捕获 |
| S8 | B | rotary | rec_0611_trumpet_var_valve_mechanism_rotary_valves | L411-L451 | 回旋 REVOLUTE+Z + paddle |
| S9 | mult | valve_count 3/4 | rec_0611_trumpet_var_valve_count_3/4_valves | L22-L228 | N 均布 + 阀簇宽派生 |
| S10 | C | first_valve_trigger | rec_0611_trumpet_var_slide_control_first_valve_trigger | L410-L457 | 前端 REVOLUTE 触发杆 |
| S11 | C | main_slide_trigger | rec_0611_trumpet_var_slide_control_main_slide_trigger | L376-L450 | 主滑管 REVOLUTE 触发杆 |
| S12 | C | dual_pull | rec_picturex_0611__trumpet__001/002... | L432-L543 | 双 PRISMATIC 拉滑管基线 |
</content>
</invoke>
