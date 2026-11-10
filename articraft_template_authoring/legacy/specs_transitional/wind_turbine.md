# Wind Turbine Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wind_turbine` |
| template path | `agent/templates/wind_turbine.py` |
| test path | `tests/agent/test_wind_turbine_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 38 |
| read_count | 13 |
| read_scope | 13 个 5 星样本完整或大段精读（0001 / 98062 / 6c3ae5 / a445 / 6ad7c / c4485 / 0002 / 232b / 8fe0 / 7525 / 220e / 633c / 3f22），其余 25 个全部 grep 过 part 名 / 关节类型 / 关节 axis / blade loop / 主几何 primitive（FanRotor/Lathe/section_loft/superellipse/Cone/Sphere），确认它们都落在已建模的结构族里，无新拓扑 |
| source_index_policy | 只索引被采纳的可复用片段；vertical-axis / 多塔聚合 等本类别不存在，未编造；blade count 在全部 38 个样本里恒为 3，但**按审核决定做成 2–5 加权采样的 multiplicity 槽位（默认/众数 3）**，2/4/5 由克隆数+相位参数化外推 |

## 核心身份
水平轴风力发电机（HAWT）：必须有落地的塔架（tower / 含 foundation）、塔顶绕竖直 Z 轴偏航的 nacelle 机舱、机舱前端绕水平 X 轴旋转的 rotor/hub，以及 `blade_count` 片（2–5，加权采样偏向 3）从 hub 径向均匀（`360°/N` 相位）伸出的叶片。主运动是 nacelle 偏航 + rotor 自旋；blade 可选俯仰（pitch）。边界：不是绕竖直轴的 VAWT（Darrieus/Savonius，无水平 hub），不是无塔的桌面风扇/排气扇（fan 无偏航塔架），不是 cooling fan / propeller（无机舱 + 偏航）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_wind_turbine_0001` | `data/records/rec_wind_turbine_0001/revisions/rev_000001/model.py:L101-L165` | LoftGeometry 锥形塔壳、superellipse_side_loft 机舱壳、ConeGeometry spinner、NACA airfoil blade loft、pitch cuff 的 helper 写法 |
| S2 | `rec_wind_turbine_0001` | `data/records/rec_wind_turbine_0001/revisions/rev_000001/model.py:L190-L310` | monolithic tower / nacelle / rotor 三件 + tower_to_nacelle FIXED + rotor_spin REVOLUTE 的整段装配（叶片融进 rotor mesh） |
| S3 | `rec_wind_turbine_98062d92cdcf4b55a157eddb6a0f4b50` | `.../rec_wind_turbine_98062d92cdcf4b55a157eddb6a0f4b50/revisions/rev_000001/model.py:L83-L222` | section_loft 塔壳 + 圆角矩形 yz 截面机舱壳；nacelle_yaw CONTINUOUS(Z) + rotor_spin CONTINUOUS(X)；叶片作 named visual 在 rotor 内按 120° clone |
| S4 | `rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb` | `.../rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb/revisions/rev_000001/model.py:L383-L525` | 独立 hub part + 3 个独立 blade part；hub_to_blade REVOLUTE pitch（feather 0.30→1.25）；blade_seat captured-flange overlap 模式 |
| S5 | `rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb` | `.../rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb/revisions/rev_000001/model.py:L547-L565` | blade root_flange / root_laminate 嵌入 hub blade_seat 的 `allow_overlap` Rule-2 grandfather 声明 |
| S6 | `rec_wind_turbine_a445ef92e8c747839eafcad528fc0620` | `.../rec_wind_turbine_a445ef92e8c747839eafcad528fc0620/revisions/rev_000001/model.py:L203-L348` | 四件 yaw-stack：base → bearing_module(FIXED) → head_module(yaw CONTINUOUS Z) → rotor(spin X)；foundation pad/plinth 作 base visual |
| S7 | `rec_wind_turbine_c4485b86313647b4b4eb5f7bcf1088fd` | `.../rec_wind_turbine_c4485b86313647b4b4eb5f7bcf1088fd/revisions/rev_000001/model.py:L286-L308` | nacelle_to_rotor + 3 个 hub_to_blade pitch（feather/stow upper≥1.30）的关节循环写法与 stow_yaw meta 标注 |
| S8 | `rec_wind_turbine_0002` | `data/records/rec_wind_turbine_0002/revisions/rev_000001/model.py:L582-L660` | per-blade pitch 的 blade_specs（phase + 径向 unit）→ rotor 上 pitch_flange support arm + REVOLUTE pitch（axis=blade direction vector）|
| S9 | `rec_wind_turbine_232b1bd2ac214440a984a980ddf36b0d` | `.../rec_wind_turbine_232b1bd2ac214440a984a980ddf36b0d/revisions/rev_000001/model.py:L62-L89` | 手写 `_tapered_tower_mesh` legacy 锥形铆接塔壳 helper（替代 Lathe 的轻量塔壳写法）|
| S10 | `rec_wind_turbine_232b1bd2ac214440a984a980ddf36b0d` | `.../rec_wind_turbine_232b1bd2ac214440a984a980ddf36b0d/revisions/rev_000001/model.py:L337-L408` | Sphere spinner cap + 叶片融进 rotor 的 monolithic rotor 写法 + nacelle_to_rotor CONTINUOUS(X) |
| S11 | `rec_wind_turbine_8fe0a625129e4da088c8f10e241ebd13` | `.../rec_wind_turbine_8fe0a625129e4da088c8f10e241ebd13/revisions/rev_000001/model.py:L52-L170` | 小型机：宽底板 + brace legs 塔（visual）；tail_boom + tail_vane 作 nacelle named visual；FanRotorGeometry 整体 rotor mesh |
| S12 | `rec_wind_turbine_7525b20e21254b76af9bc2337dc901ab` | `.../rec_wind_turbine_7525b20e21254b76af9bc2337dc901ab/revisions/rev_000001/model.py:L286-L373` | root_guard（FIXED 安全笼 part）+ lock_pin（PRISMATIC 锁定销 part）两个 service 附件 part 的写法 |
| S13 | `rec_wind_turbine_220e641da07c4423826cc412a680a3f6` | `.../rec_wind_turbine_220e641da07c4423826cc412a680a3f6/revisions/rev_000001/model.py:L212-L289` | access_hatch 作独立 part + nacelle_to_hatch REVOLUTE（开门 0→1.75 rad）|

## 槽位 + 候选模块表

### Slot A：support（塔架/落地基座）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `monopole_tower` | `rec_wind_turbine_98062d92cdcf4b55a157eddb6a0f4b50` | L83-L110 | **yes** | 单根 section_loft/Lathe 锥形管塔，底有 foundation_pad/head_flange named visual，1 个 part（tower），nacelle 直接坐塔顶 |
| `tower_with_foundation` | `rec_wind_turbine_633cba46da42473b8b4582132a4a8e52` | L123-L298 | | 独立 `foundation` part（FIXED 在 tower 下）+ tower part，混凝土基座做受力锚点 |
| `bearing_module_stack` | `rec_wind_turbine_a445ef92e8c747839eafcad528fc0620` | L203-L266 | | tower(base) + 独立 `bearing_module` 偏航轴承鼓 part（FIXED 在塔顶），把偏航 DOF 放进单独 part |
| `braced_short_mast` | `rec_wind_turbine_8fe0a625129e4da088c8f10e241ebd13` | L52-L86 | | 宽底板 + 短桅杆 + 4 条 brace_legs（均 named visual），桌面/小型机的稳定低塔 |

### Slot B：nacelle（机舱）+ 偏航关节类型
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `yaw_continuous` | `rec_wind_turbine_98062d92cdcf4b55a157eddb6a0f4b50` | L111-L171 | **yes** | section_loft 机舱壳 + bedplate/shaft_housing named visuals；tower→nacelle CONTINUOUS，axis (0,0,1)，无限位 |
| `yaw_revolute_bounded` | `rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb` | L243-L496 | | 机舱壳同构，但 tower→nacelle REVOLUTE，axis (0,0,1)，limited service sweep（±1.15 rad 量级）|
| `yaw_fixed` | `rec_wind_turbine_0001` | L216-L294 | | 机舱坐塔顶但 tower_to_nacelle FIXED（不偏航，rigid 模型）；偏航 DOF 关闭 |

### Slot C：rotor（轮毂 + `blade_count` 叶片）构造方式
（叶片数 = `blade_count`，2–5 加权采样偏向 3；下表以 source 的 N=3 为例，实现按 N 等分相位 `360°/N` 克隆）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `monolithic_rotor` | `rec_wind_turbine_98062d92cdcf4b55a157eddb6a0f4b50` | L173-L222 | **yes** | 单个 rotor part：hub_barrel + spinner + N 片 blade（airfoil loft / clone）全作 named visual 融进同一 part；只有 1 个 nacelle→rotor REVOLUTE/CONTINUOUS（axis X）|
| `pitching_blades` | `rec_wind_turbine_6ad7c7431e4c4997ab151936eb6085bb` | L383-L525 | | 独立 hub part（含 N 个 blade_socket）+ N 个独立 blade part；nacelle→hub spin(X) + N 个 hub→blade pitch REVOLUTE（axis 沿叶片径向，feather range）|
| `fixed_socket_blades` | `rec_wind_turbine_6c3ae5ee832d48d2b98461a981ab69f6` | L248-L334 | | 独立 hub + N 个独立 blade part，但 hub→blade 为 FIXED 径向 socket（叶片不俯仰，仅整体随 hub 自旋）|

### Slot D：accessories（机舱/轮毂上的可选附件，0..N 并联）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `tail_vane` | `rec_wind_turbine_8fe0a625129e4da088c8f10e241ebd13` | L107-L118 | **yes** | tail_boom + tail_vane 作 nacelle named visual（不动→不是 part），下风向小型机的尾舵 |
| `access_hatch` | `rec_wind_turbine_220e641da07c4423826cc412a680a3f6` | L212-L289 | | 独立 `access_hatch` part + nacelle→hatch REVOLUTE 开门关节（axis Z，0→1.75 rad）|
| `root_guard` | `rec_wind_turbine_7525b20e21254b76af9bc2337dc901ab` | L286-L314 | | 独立 `root_guard` 安全笼 part，FIXED 到 nacelle（独立刚体参考系，故用 FIXED）|
| `lock_pin` | `rec_wind_turbine_7525b20e21254b76af9bc2337dc901ab` | L359-L373 | | 独立 `lock_pin` part + nacelle→lock_pin PRISMATIC（轴向锁定销，captured-pin overlap）|

> Slot D 候选数 = 4，但语义是「0..N 并联挂件」而非互斥单选；seed=0 取 `tail_vane`。所有 4 个候选都有独立 5 星来源、结构互不相同（visual / revolute door / fixed cage / prismatic pin），不存在退到 2 的情况。

## 槽位图（slot graph）
pattern = **mixed**（linear chain + 内嵌 parallel children + 可选 parallel accessories）

```
[Slot A support] --(FIXED, 落地; bearing_module/foundation 子件 FIXED 链)-->
[Slot B nacelle] --(yaw: Z 轴, FIXED|REVOLUTE|CONTINUOUS)-->
[Slot C rotor / hub] --(spin: X 轴, REVOLUTE|CONTINUOUS)-->
        |
        +-- monolithic_rotor:     N blades 融进 rotor part（无额外关节）
        +-- pitching_blades:      hub --(pitch: 叶片径向轴 ×N, REVOLUTE)--> [blade_0..N-1]   ← parallel children
        +-- fixed_socket_blades:  hub --(FIXED ×N)--> [blade_0..N-1]                          ← parallel children
        （N = blade_count，2–5 加权采样偏向 3；叶片绕 hub 按 360°/N 等分相位）

[Slot B nacelle] --(可选, parallel)--> [Slot D accessories: tail_vane(visual) / access_hatch(REVOLUTE) / root_guard(FIXED) / lock_pin(PRISMATIC)]
```

主链恒为 support → nacelle → rotor。Slot C 决定 rotor 之下是否再并联出 3 个 blade 子件及其关节类型；Slot D 在 nacelle 上并联 0..N 个附件。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `tower` | 落地塔架/桅杆，含 foundation_pad、base/top flange、可选 brace legs 等 named visual | `support_style`, `tower_height`, `tower_base_radius`, `tower_top_radius` | S2 / S3 / S6 / S9 / S11 |
| `foundation` | 可选独立混凝土基座 part，FIXED 在 tower 下（仅 `tower_with_foundation`）| `has_foundation`, `foundation_radius` | S6（633c）|
| `bearing_module` | 可选独立偏航轴承鼓 part，FIXED 在塔顶（仅 `bearing_module_stack`）| `has_bearing_module`, `yaw_drum_radius` | S6 |
| `nacelle` | 机舱壳 + bedplate / shaft housing / cooling box / 可选 tail_boom+tail_vane named visual | `nacelle_length`, `nacelle_width`, `nacelle_height`, `yaw_type` | S2 / S3 / S6 / S11 |
| `rotor` | monolithic 时为「hub + spinner + N blade」单 part；pitching/fixed 时退化为只含 hub+spinner 的 hub part | `rotor_style`, `hub_radius`, `blade_span`, `spinner_style`, `blade_count` | S2 / S3 / S10 |
| `hub`（=rotor 的别名）| pitching/fixed_socket 模式下的独立轮毂 part，含 N 个 blade_socket/seat（N=`blade_count`）| `hub_radius`, `socket_radius`, `pitch_root_radius`, `blade_count` | S4 / S6c3ae |
| `blade_i`（i=0..N-1）| pitching/fixed 模式下的 N 个独立叶片 part：root_flange + root_sleeve + airfoil blade_shell mesh；绕 hub 按 `360°/N` 等分相位 | `blade_span`, `blade_root_chord`, `blade_tip_chord`, `blade_twist`, `blade_count` | S4 / S7 / S8 |
| `access_hatch` | 可选独立检修门 part（REVOLUTE 开门）| `has_access_hatch` | S13 |
| `root_guard` | 可选独立叶根安全笼 part（FIXED）| `has_root_guard` | S12 |
| `lock_pin` | 可选独立转子锁定销 part（PRISMATIC）| `has_lock_pin`, `pin_stroke` | S12 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `foundation_to_tower` | fixed | A.foundation | A.tower | n/a | n/a | 基座→塔，仅 `tower_with_foundation` | S6（633c）|
| `tower_to_bearing` | fixed | A.tower | A.bearing_module | n/a | n/a | 塔顶→偏航轴承鼓，仅 `bearing_module_stack` | S6 |
| `tower_to_nacelle` (yaw) | fixed / revolute / continuous | A.tower 或 A.bearing_module | B.nacelle | `(0,0,1)` | continuous 无限位 / revolute ±(1.0~1.6) | 偏航主关节，类型由 Slot B 决定 | S2 / S3 / S4 / S6 |
| `nacelle_to_rotor` (spin) | revolute / continuous | B.nacelle | C.rotor 或 C.hub | `(1,0,0)` | revolute ±π / continuous 无限位 | 转子自旋主关节，恒沿 +X | S2 / S3 / S7 / S10 |
| `hub_to_blade_i` (pitch) | revolute | C.hub | C.blade_i | 叶片径向 unit（如 `(0,0,1)`/`(0,1,0)`/blade dir）| feather, 约 `[-0.35, 1.30]` | 仅 `pitching_blades`：每片独立俯仰 ×N（N=`blade_count`，i=0..N-1）| S4 / S7 / S8 |
| `hub_to_blade_i` (socket) | fixed | C.hub | C.blade_i | n/a | n/a | 仅 `fixed_socket_blades`：叶片刚性插 socket ×N | S6c3ae（L325-L334）|
| `nacelle_to_hatch` | revolute | B.nacelle | D.access_hatch | `(0,0,-1)` | `[0, 1.75]` | 可选检修门开合 | S13 |
| `nacelle_to_guard` | fixed | B.nacelle | D.root_guard | n/a | n/a | 可选安全笼（独立参考系故 FIXED）| S12 |
| `nacelle_to_lock_pin` | prismatic | B.nacelle | D.lock_pin | `(1,0,0)` | `[0, 0.32]` | 可选转子锁定销轴向插入 | S12 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_style` | enum | `monopole_tower` / `tower_with_foundation` / `bearing_module_stack` / `braced_short_mast` | `monopole_tower` | 决定 Slot A part 数与偏航父件 | S2 / S3 / S6 / S11 |
| `yaw_type` | enum | `continuous` / `revolute_bounded` / `fixed` | `continuous` | 决定 tower_to_nacelle 关节类型与限位 | S2 / S3 / S4 |
| `rotor_style` | enum | `monolithic_rotor` / `pitching_blades` / `fixed_socket_blades` | `monolithic_rotor` | 决定 rotor 是否拆出 `blade_count` 个 blade part + pitch 关节 | S2 / S4 / S6c3ae |
| `spinner_style` | enum | `cone` / `lathe_ogive` / `sphere_cap` | `cone` | rotor 鼻锥 named visual 形状 | S1 / S6 / S10 |
| `blade_count` | int | `2 / 3 / 4 / 5`（加权随机采样，偏向 3）| 3 | multiplicity：叶片 part/visual 绕 hub 按 `360°/N` 等分相位克隆；推荐权重 `{2:0.15, 3:0.50, 4:0.25, 5:0.10}`（3 概率最大，2/4 次之，5 最低）；38 样本均为 N=3，2/4/5 仅靠克隆数+相位参数化外推，无需新结构 | all（N=3 source）+ 参数外推 |
| `tower_height` | float | `0.34–80.0`（量级随 scale_class 跨度大）| sampled | hub_height ≈ tower_height（+brace 偏置）| S2 / S3 / S6 / S11 |
| `tower_base_radius` / `tower_top_radius` | float | base `0.05–4.3`，top `top<base` | sampled | 锥度，top_radius < base_radius | S3 / S6 |
| `blade_span` | float | 与 rotor_radius 同阶，`blade_span > nacelle_length` | sampled | rotor_diameter = 2·blade_span | S1 / S3 / S6 |
| `pitch_feather_upper` | float | `≥1.30`（feather/stow）| 1.35 | 仅 pitching_blades；pitch range `[lower<0, upper≥1.30]` | S4 / S7 |
| `has_foundation` | bool | derived（`support_style==tower_with_foundation`）| false | | S6（633c）|
| `has_bearing_module` | bool | derived（`support_style==bearing_module_stack`）| false | | S6 |
| `accessories` | set | 子集 of {`tail_vane`,`access_hatch`,`root_guard`,`lock_pin`} | {`tail_vane`} | 0..N 并联挂在 nacelle | S11 / S12 / S13 |

## 拓扑多样性审计
total_combinations = `len(support_style) × len(yaw_type) × len(rotor_style) × len(accessory_presence)`
= `4 (Slot A) × 3 (Slot B) × 3 (Slot C) × ≥2 (Slot D 至少有/无附件)` = **72**（仅按「是否带任一附件」二值算下界；按 4 个附件子集独立则远超）。


| slot | candidate_count |
|---|---|
| Slot A support | 4 |
| Slot B nacelle/yaw | 3 |
| Slot C rotor | 3 |
| Slot D accessories | 4（0..N 并联，下界按二值取 2）|

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 必含 tower(落地) + nacelle + rotor/hub；rotor 上 `blade_count` 片叶片（2–5，默认/众数 3）|
| chain topology | support → nacelle → rotor 主链不可跳父；foundation/bearing_module 若存在必 FIXED 串在 tower 侧 |
| yaw axis | tower_to_nacelle（非 fixed 时）axis 必为 `(0,0,1)`；fixed 时无 axis |
| spin axis | nacelle_to_rotor axis 必为 `(1,0,0)`（水平前向）|
| blade count | = `blade_count`（2–5，加权偏向 3）；monolithic 为 N 个 named visual，pitching/fixed 为 N 个 blade part；N 片绕 hub 等分 `360°/N` 相位 |
| pitch axis | pitching_blades 中每个 hub_to_blade_i axis 必沿该叶片径向（与 `360°/N` 安装相位一致），feather upper ≥ 1.30 |
| blade root mating | pitching/fixed 模式每个 blade root_flange 必与对应 hub blade_socket 接触；captured 部分用 `allow_overlap` 声明（Rule 2 grandfather，见 S5）|
| grounding | tower/foundation 必落地（min z ≈ 0），nacelle 坐塔顶，rotor hub 前伸出机舱（origin_gap x > 0）|
| blade clearance | 叶尖在所有 spin 姿态下离地、离塔 > 0（rotor 在塔前侧）|
| no floating | nacelle、rotor、blade、hatch、guard、lock_pin、tail_vane 全部有 attached/constrained 父件，无悬空装饰 |
| accessories | tail_vane 必为 nacelle visual（不动→不是 part，Rule 1）；access_hatch/root_guard/lock_pin 若为独立 part 必带 MatingContract 锚到真实 nacelle 面 |

## Reject cases
- 只有静态塔+机舱，没有 rotor 自旋关节，或 rotor 自旋轴不是水平 X。
- 偏航关节轴不是竖直 Z（如做成绕 X 偏航），或把偏航与自旋轴搞反。
- 叶片数量不在 `[2,5]` 区间，或 N 片相位不等分（非 `360°/N`），或叶片从空中开始、不在 hub 径向。
- pitching_blades 模式里 pitch 轴乱设（不沿叶片径向），或 feather 范围太小（upper < 1.30）。
- monolithic_rotor 模式却把 3 片叶片拆成独立 part 用 FIXED 关节连（违反 Rule 1，应作 named visual）。
- tail_vane 被做成独立 part 用 FIXED 关节挂在 1-3mm 接口盘上（违反 Rule 1/2，应融进 nacelle visual）。
- foundation/bearing_module/access_hatch 漂浮，未与 tower/nacelle 实体接触。
- rotor hub 没有前伸出机舱（origin 在机舱内或后方），叶尖扫到塔或地面。
- 做成 VAWT（竖直轴）或无塔风扇，丢失 HAWT 身份。

## 与相邻类别的边界
| 相邻类别 | 区别 |
|---|---|
| cooling_fan / exhaust_fan / desk_fan | 风扇无落地塔架、无偏航 Z 关节；wind_turbine 必有 tower + nacelle 偏航 + 前伸 hub |
| propeller / boat_propeller | 螺旋桨只有 hub+blades 自旋，无塔、无机舱、无偏航 |
| VAWT（Darrieus/Savonius 竖直轴风机）| VAWT 主轴竖直、叶片绕 Z 旋转、无水平 hub/nacelle；本模板是水平轴 X 自旋 |
| weather_vane / wind_sock | 风向标只有竖直轴 yaw、无旋转 rotor 和叶片 |
| serial_elbow_arm / cctv_mast pan-tilt | 机械臂/云台是串联 yaw+pitch 关节但无自旋 rotor、无 3 叶片；语义完全不同 |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。**审核修订：blade_count 由"恒 3"改为 2–5 加权采样 multiplicity 槽位（权重 {2:.15,3:.50,4:.25,5:.10}，默认/众数 3），N 片按 360°/N 等分相位克隆，样本只有 N=3 故 2/4/5 为参数外推**；Slot D 为 0..N 并联附件而非互斥单选 |
</content>
</invoke>
