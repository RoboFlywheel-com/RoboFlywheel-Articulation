# Modular Spec — surge_protector_switch

## 元信息
| 项 | 值 |
|---|---|
| slug | `surge_protector_switch` |
| template file | `agent/templates/Electrical_Wiring_Surge_protector_switch.py` (KEY-named) |
| functions | stem-named (`build_surge_protector_switch`, `config_from_seed`, ...) |
| test path (optional) | skipped while batch-authoring |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

一根挤出 bar `housing`（ROOT）承载所有固定 visual（outlet plate/socket、switch bezel/well、
side rib、mount hardware、LED、cord/plug）；K 个 rocker 是 housing 的并列 REVOLUTE 子件；可选 reset
breaker 是 housing 的 PRISMATIC 子件。无跨 slot 串链（parallel_children），outlet/rocker 数为 multiplicity。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples (2 origins + 5 forks) |
| source_index_policy | only adopted module sources indexed below |

S1 黑色 recessed-flat、S2 黄色 raised-bezel（2 origin）+ four_outlet/twelve_outlet/single_master/
reset_breaker/usb_ports（5 fork），全部逐个读 model.py。

## 核心身份
一根挤出 bar 壳 surge-protector 排插：顶面一排 N 个 NEMA outlet + 一排独立 red-rocker 开关（每个
rocker 自己一个 REVOLUTE）+ captive cord + plug；可选 green LED、reset/breaker push button、USB、壁挂支架。
- 不该混入 配电箱/distribution board（断路器 + DIN 母排阵列，非 outlet+rocker）。
- 不该混入 单个墙面开关/wall switch（墙盒开关，本类是带 N outlet 的可移动排插，必有 cord+plug）。

## 槽位 + 候选模块表

### Slot A：housing_form（③ Primary Form Family）
| module_name | source_type | source | model.py:Lx-Ly | eligibility | 结构特征 (form_subtype) |
|---|---|---|---|---|---|
| recessed_flat | forked_anchor | S1 | L57-120 | eligible | 平顶 CadQuery shell；outlet=下沉 socket（dark cavity+brass+rim frame，plate 齐顶面）；switch=下沉 well（dark 井底+detent rim）。Macro Surface Construction |
| raised_bezel | forked_anchor | S2 | L119-237 | eligible | rounded 挤出 shell；outlet=凸出 plate mesh（切穿 blade/ground）+brass backing+shadow；switch=凸出 bezel mesh；side rib+center divider。Volumetric Envelope Form |

2 candidate：样本池仅 2 origin 各锚一 form family；本类主轴是 multiplicity+switch_scheme（非形态主导），
③ 以 2 source-backed candidate 达标（§8.5「样本不足 ≥2 并说明理由」）。

### Slot B：switch_scheme（① 骨架/关节数 主轴）
| module_name | source_type | source | model.py:Lx-Ly | eligibility | 结构特征 |
|---|---|---|---|---|---|
| per_outlet | forked_anchor | S2+four/twelve | S2 L311-349 | eligible | N 个 rocker 逐 outlet；N 个 REVOLUTE。count=N |
| master_plus_individual | forked_anchor | S1 | L32-36,206-217 | eligible | N per-outlet + 1 master（cord 端 list 前置）；N+1 REVOLUTE。「N outlets vs N+1 switches」显式 |
| single_master | forked_anchor | single_master fork | L60-343 | eligible | 保 N outlet，仅 1 大 master rocker；恰 1 REVOLUTE |

### Slot C：mount（③/① mount hardware，无关节）
| module_name | source_type | source | model.py:Lx-Ly | eligibility | 结构特征 |
|---|---|---|---|---|---|
| flat_feet | forked_anchor | S1 | L189-195 | eligible | 底面 4 rubber 脚 + 4 角螺丝；桌面型 |
| wall_keyhole_guard | forked_anchor | S2 | L145-180 | eligible | 端盖 + keyhole tab mesh（切孔）+ guard bar/post + 螺丝；工程壁挂型 |

### Slot D：face_power（④ + ② 关节类型）
| module_name | source_type | source | model.py:Lx-Ly | eligibility | 结构特征 |
|---|---|---|---|---|---|
| cord_plug | forked_anchor | S2（弃 S1 编织 greeble） | L249-307 | eligible | swept-spline cord + round plug（blade+ground pin）；无 LED |
| cord_plug_led | forked_anchor | S2 | L240-307 | eligible | cord+plug + green LED |
| reset_breaker | forked_anchor | reset fork | L48-282 | eligible | cord+plug+LED + reset push button（revolve dome+stem，PRISMATIC ±Z）。唯一 ② prismatic face |
| usb_ports | forked_anchor | usb fork | L87-294 | eligible | cord+plug+LED + USB block（切穿 2×A+1×C）+brass+label；纯 visual 无关节 |

### Slot E（multiplicity）：outlet_count N
见 §8。N ∈ {4,6,8,12} source-backed，外推 [3,14]；bar LENGTH+pitch 由 N 重算。

## 槽位图（slot graph）
```
pattern: mixed (parallel_children + multiplicity)
                housing (ROOT, form=Slot A)  top +Z, switch row y=SWITCH_Y, outlet row y=OUTLET_Y
   ┌──────────────┬──────────┴──────────┬───────────────────┐
 Slot B         Slot C               Slot D            outlets ×N (Slot E, fixed visuals)
 rocker×K       mount hardware       cord/plug/LED
 REVOLUTE +Y    (fixed visuals,      (+ optional reset
 每个独立       无关节)              PRISMATIC +Z child)
 挂 housing
```
- 所有活动件（rocker×K、可选 reset）都是 housing 并列子件，无跨 slot 串链。
- rocker pivot = housing switch 位置 bezel/well pocket（pin captured，omit MatingContract，grandfathered captured-pin）。
- rocker 关节 axis = (0,1,0)（+Y，全模板统一，含 master）；pivot_pin rpy=(π/2,0,0) 与 axis 一致（两源 S1=X/S2=Y，选 S2 的 Y）。
- reset button 关节 axis = (0,0,1)（+Z 压入）。
- housing_form(A) 与 switch_scheme(B) 共享 resolve 单源派生的 `switch_specs`（(x,y,kind) 列表）：A 画 bezel/well，B 放 rocker（Contract 3c）。

## 每槽位 Module Emits / Interfaces
### Slot A housing_form
parts: `housing`(ROOT); visuals: shell mesh + N outlet + K bezel/well + rib + divider + label（S2 L119-237/S1 L57-120）；无关节；downstream: 顶面 switch pocket 供 B，顶面 reset 孔位供 D。
### Slot B switch_scheme
parts: `rocker_{i}`(K)；visuals: red cap mesh + pivot_pin + on/off marker（S2 L314-339）；joints: `housing_to_rocker_{i}` REVOLUTE (0,1,0) [-travel,travel]（master ±0.25）；upstream: rocker(0,0,0) 落 housing bezel/well，pin captured omit mating。
### Slot C mount
parts: 无（纯 housing visual）；visuals: feet+螺丝 / end cap+keyhole+guard（S1 L189-195/S2 L145-180）；无关节。
### Slot D face_power
parts: reset_breaker 才有 `reset_breaker_button`(PRISMATIC)；visuals: cord spline tube + plug + 可选 LED/USB block（S2 L249-307,240-245 / usb L264-294）；joints: reset `housing_to_reset_breaker` PRISMATIC (0,0,1) [0,travel]。
活动件（rocker/reset）有 articulation；不动件（cord/plug/LED/USB/mount/label/rib）写 housing visual。

## 参数范围汇总
| 参数 | 类型 | 范围/候选 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| housing_form | enum | recessed_flat/raised_bezel | raised_bezel | choice | sampler | A |
| switch_scheme | enum | per_outlet/master_plus_individual/single_master | per_outlet | choice | sampler | B |
| mount | enum | flat_feet/wall_keyhole_guard | wall_keyhole_guard | choice | sampler | C |
| face_power | enum | cord_plug/cord_plug_led/reset_breaker/usb_ports | cord_plug_led | choice | sampler | D |
| outlet_count N | int | [3,14] 锚{4,6,8,12} | 8 | conditional | 加权采样(§8)；length/pitch 派生 | E/S2,four,twelve |
| palette_style | enum | 6 colorway(§8.5⑥) | safety_yellow | choice | sampler→mats 驱动所有 .visual | S1/S2 |
| body_length | float | derived | — | equation | =2·max(outlet_extent,switch_extent)+margin(含 master pitch) | four/twelve↔N |
| outlet_pitch | float | [0.070,0.092] | 0.080 | independent | uniform+clamp | S2/four 0.080 |
| body_width | float | [0.072,0.120] | 0.086 | independent | uniform+clamp | S1 0.118/S2 0.082 |
| body_height | float | [0.028,0.040] | 0.031 | independent | uniform+clamp | S1 0.036/S2 0.030 |
| rocker_travel | float | [0.18,0.28] rad | 0.22 | independent | REVOLUTE 上界 clamp | S2 0.22/S1 0.27 |
| reset_travel | float | [0.003,0.006] m | 0.004 | independent | PRISMATIC 上界 clamp | reset 0.004 |
| (—) | constraint | — | — | inequality | switch_specs 全部 |x|<body_length/2-cap；否则加大 length | 接口 |
| (—) | constraint | — | — | inequality | 相邻 switch |Δx|≥cap_w+0.006（±travel 不互撞）；由 pitch≥0.070 保证 | clearance |

所有 equation/inequality 在 resolve_config 求解（body_length 派生；switch_specs 单源）。

### 7.5 编译预算
**≤12s/seed**（库内 mesh 模板 5-20s）。每 seed CadQuery：shell fillet×1、outlet_plate×1、switch_bezel×1、
rocker cap×1、master cap×≤1、mount_tab×≤1、usb block×≤1、reset dome×≤1、cord spline×1——每个只造一次
跨 N 复用同一 Mesh（Container_Locker `_cached_perforated_mesh` 同法，N=12 不重算 boolean）。cord
radial_segments=16 samples_per_segment=14（S2 20/18 降精度）；小 cylinder/dome ≤24 段。**不**逐 pit
boolean cut 进 shell（S1 那样 N×3 布尔随 N 变贵）——recessed 用复用 plate mesh 齐面 + dark cavity + rim box。

## Multiplicity / Copy Logic
**1 根轴：outlet_count N。**
- count_param `outlet_count`；N_range 产品域 [3,14]，锚 {4,6,8,12}；测试偏小。
- sampling domain（小 N 高频）：N∈(4,6,8,10,12,14,3,5) weights(0.24,0.22,0.20,0.12,0.10,0.05,0.04,0.03)；slot_choices 编码 `outlets_{N}`。
- copied object：outlet(plate/socket+brass+shadow/rim+2 screw) + per-outlet rocker（per_outlet/master+individual 时）。三 loop 共用同一 outlet_xs/switch_specs x list。
- naming：outlet_plate_{i}/brass_contact_backing_{i}/switch_bezel_{i}/rocker_{i}/housing_to_rocker_{i}。
- placement：x_i=(i-(N-1)/2)·pitch 中心对称；outlet y=OUTLET_Y 后排，switch y=SWITCH_Y 前排。
- joint policy：每 rocker 独立 REVOLUTE (0,1,0) 统一 limits（master ±0.25 略大）。
- gating：body_length 随 N 派生；sweep 上限 N=14；master_plus_individual switch count=N+1（master 前置）。

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | switch_scheme：per_outlet(N)/master+individual(N+1)/single_master(1) part+joint 数变；reset_breaker 加 1 PRISMATIC part。全 forked_anchor |
| └ multiplicity | 有 | outlet_count N（§8，[3,14] 锚{4,6,8,12} 小 N 高频） |
| ② 关节类型 | 有 | rocker REVOLUTE(0,1,0) 恒；reset_breaker 引入 PRISMATIC(0,0,1)（reset fork L274-282）。两 type 都在 sweep 出现 |
| ③ Primary Form Family | 有 | housing_form recessed_flat(Macro Surface Construction)/raised_bezel(Volumetric Envelope Form)。2 source-backed，登记 slot_choices。非形态主导，2+理由达标 |
| ④ 表面装饰 | 有 | face_power 叠 LED/USB+label/reset；mount 叠 guard/keyhole/endcap vs feet/screw；side rib+divider+on/off label。装饰贴 TOP_Z 面随 body dims 共形 |
| ⑤ 尺寸/行程 | 有 | length(N 派生)/width[0.072,0.120]/height[0.028,0.040]/pitch[0.070,0.092]。rocker REVOLUTE+Y [0,±0.18~0.28] on/off；reset PRISMATIC+Z [0,0.003~0.006]。motion_test_plan 见下 |
| ⑥ 涂装 | 有 | palette_style 6：industrial_black/safety_yellow/office_white/graphite_grey/brushed_steel/surge_blue。材质大类 molded_plastic+painted_metal(brushed_steel)+metal(brass/steel 恒)+translucent(red lens/green LED 恒)，覆盖≥3 ✓ |

**motion_test_plan / sampled-pose**：per_outlet(N)/master+individual(N+1) 有多达 15 个互相独立、互不接触
（相邻间距≥pitch0.070>cap 宽）的 rocker 关节。run_tests 调 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32,
ignore_fixed=True)`（Cartesian 由 cap 限）+ 每机构 targeted ctx.pose（rocker ±travel 两端验 on_end_marker z
位移；reset [0,travel] 验 button z 压入）+ captured-pin 的 element-scoped allow_overlap（pin↔bezel、cap↔bezel seated）。
若 32-cap sampled 触发 compile_timeout 集群，降级为 Container_Locker 策略（去掉显式调用，依赖 compiler baseline
harness_motion_qc + targeted ctx.pose + allow_overlap），并在此写 exemption 理由。

## 拓扑多样性审计
总组合数：housing_form(2)×switch_scheme(3)×mount(2)×face_power(4)×N档(8)=**384**（palette 6 再×6 视觉，不计结构 distinct）。
seed_domain_policy：procedural_first（seed=0 不特殊）。sampler：每 slot 独立 rng.choice，N 用 rng.choices 加权，连续 rng.uniform+clamp。
compatibility：全正交无非法组合（都挂同一 housing）；唯一耦合 housing_form/switch_scheme 共享 switch_specs（单源派生）。
无 regression override。sweep 0-35 初过 → 0-999 成熟。Topology target 1000-seed distinct 按 ≥300 report-only 口径观察。
Controlled local：pitch/width/height/rocker_travel/reset_travel independent clamp；body_length equation(N,scheme,pitch)。全 resolve_config clamp/派生。

| slot | candidate_count | ≥2 | ≥3 |
|---|---:|---|---|
| housing_form | 2 | yes | no |
| switch_scheme | 3 | yes | yes |
| mount | 2 | yes | no |
| face_power | 4 | yes | yes |
| outlet_count | 8 档 | yes | yes |

## Validator
- slot_choices_for_seed 返回已实现 module 名
- config_from_seed 全 seed（含 0）deterministic 采样
- 无非法组合（全正交）；无 regression override；主 domain 非 curated 表
- pitch/width/height/travel clamp，body_length 派生，不破接口/clearance/joint origin/multiplicity
- 跨件依赖（body_length=f(N,scheme,pitch)、switch_specs）resolve_config 求解
- 每 rocker REVOLUTE(0,1,0) 挂 housing；reset PRISMATIC(0,0,1)
- pin-captured rocker omit MatingContract，run_tests element-scoped allow_overlap
- copied naming/placement（outlet_{i}/rocker_{i}，x 中心对称）

## Reject cases
- rocker(0,0,0) 不在 bezel/well 附近 → joint origin >15mm 悬空
- 用 S1 64-box 编织 cord greeble（应弃，用 spline tube）
- rocker/mount hardware 做成 FIXED-joint 独立 part（应 REVOLUTE 或 housing visual）
- N 个 recessed pit 逐个 boolean cut（compile 随 N 变贵超预算）
- master_plus_individual 忘记 body_length 加 master pitch → master 悬出/撞 cord
- 相邻 rocker 间距 < cap 宽 → ±travel 互撞
- rocker 轴两源混用（X/Y）→ 应全统一 (0,1,0)
- palette 变动 rocker/LED/brass 功能色（应恒 red/green/brass）

## 与相邻类别的边界
- 不该混入：配电箱/distribution board（断路器+DIN 母排阵列）
- 不该混入：单个墙面开关/wall switch（墙盒开关，非带 N outlet 排插）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 2 origin+5 fork 全读；rocker 轴统一(0,1,0)；弃编织 cord 用 spline tube；mesh 跨 N 复用控 compile；384 结构组合 |

## Module Source Index
| id | slot | module | sample_id | model.py |
|---|---|---|---|---|
| S1 | A/B/C | recessed_flat/master_plus_individual/flat_feet | rec_electrical_wiring_gpt55_...sixrockers | L32-217 |
| S2 | A/B/C/D | raised_bezel/per_outlet/wall_keyhole_guard/cord_plug(_led) | rec_use-...d5decd1b | L52-349 |
| S3 | E | outlets_4 | rec_surge_protector_switch_var_four_outlet | L23,178 |
| S4 | E | outlets_12 | rec_surge_protector_switch_var_twelve_outlet | N=12 |
| S5 | B | single_master | rec_surge_protector_switch_var_single_master_switch | L60-343 |
| S6 | D | reset_breaker | rec_surge_protector_switch_var_reset_breaker_button | L48-282 |
| S7 | D | usb_ports | rec_surge_protector_switch_var_usb_ports | L87-294 |
