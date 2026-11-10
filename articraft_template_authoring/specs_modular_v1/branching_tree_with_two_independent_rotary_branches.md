## 元信息

| 项 | 值 |
|---|---|
| slug | `branching_tree_with_two_independent_rotary_branches` |
| template path | `agent/templates/branching_tree_with_two_independent_rotary_branches.py` |
| test path (optional) | `tests/agent/test_branching_tree_with_two_independent_rotary_branches_template.py` |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 35 |
| read_count | 35 |
| read_scope | 类别内全部 35 个 5 星样本；每条均读取 `record.json`、`revision.json`、`prompt.txt`、`model.py` |
| source_index_policy | 仅索引下方采纳 module source |

结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| vertical_spine / mast 支撑 + 2 单链支臂 | 18 | 最常见；staggered 或 bilateral 安装 |
| tower_stand / pedestal 立柱 + 2 revolute | 7 | 同轴 Z yaw 或 collar 接口 |
| ladder_frame / cheek_arm 双轨框 | 4 | FIXED cheek → REV arm |
| trunk_y_tree 同高双侧 hub | 2 | Y 形主干 |
| two_link_chain 每分支 2 节 | 2 | 4 revolute，仍属双树非串联臂 |
| hub_spoke / bracket_carrier 中间件 | 4 | FIXED hub/bracket → REV spoke/branch |

## 核心身份

**恰好两个且仅两个独立 rotary branch** 挂载在同一 grounded support carrier 上。每个分支有可见 pivot / hub / bearing station，并通过独立 `REVOLUTE` 关节运动；它们不是串联链条，也不是同一 rotor 的双叶片。

成熟形态：检具树、工装支架、ladder fixture、pedestal stand、Y 形机械树。固定支撑提供两个清楚接口站，活动分支提供刚性 arm、pad / fork / plate / linkage beam。

边界：
- 不是 `branching_tree_with_three_independent_rotary_branches`（分支数固定 2，非 3）。
- 不是 `robotic_arms` / `serial_elbow_arm` 单链串联臂（即使 `two_link_chain` 每侧 2 节，仍是 **双份并行树**）。
- 不是 `dual_independent_finger_chains` 指状链。
- 不是风扇/涡轮叶片或静态树枝雕塑。

## 槽位 + 候选模块表

### Slot A：support_carrier

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `vertical_spine` | rec_branching_tree_with_two_independent_rotary_branches_0004 | L83-L133 | eligible if compatible | 底板 + 竖直箱形 spine；侧向 root block + hinge plate |
| `vertical_mast` | rec_branching_tree_with_two_independent_rotary_branches_2e7d777ce8c840c9add9a081c6f0d857 | L54-L97, L125-L165 | eligible if compatible | 圆/方 mast + base plate；hub block / yoke |
| `tower_stand` | rec_branching_tree_with_two_independent_rotary_branches_69dc78b32e6440de80ec472e5f718e5c | L33-L167 | eligible if compatible | 重底座 + 短塔台；collar 双接口 |
| `ladder_frame` | rec_branching_tree_with_two_independent_rotary_branches_754fee72af00441ea2a027db63e9f456 | L45-L72, L143-L195 | eligible if compatible | 双竖轨 ladder + 横档；cheek 安装面 |
| `trunk_y_tree` | rec_branching_tree_with_two_independent_rotary_branches_0002 | L60-L77, L97-L135 | eligible if compatible | Y 形 trunk；同高双侧 hub |
| `pedestal_or_wall` | rec_branching_tree_with_two_independent_rotary_branches_d6a279d480704ba584e3f5ee1ddba80d | L157-L229 | eligible if compatible | 重脚 pedestal 或 wall backplate + clamp pod |

### Slot B：branch_topology

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_rigid_branch` | rec_branching_tree_with_two_independent_rotary_branches_ca64a5ac2d864625ab2f246198787617 | L40-L168 | eligible if compatible | `carrier → branch_i` 单节刚性臂 |
| `two_link_chain` | rec_branching_tree_with_two_independent_rotary_branches_0001 | L136-L287 | eligible if compatible | `base → upper → forearm` ×2；4× REVOLUTE |
| `hub_spoke` | rec_branching_tree_with_two_independent_rotary_branches_1c3aae32c8e34b068d2af96e40700b9f | L53-L152 | eligible if compatible | FIXED hub @ mast；REV spoke |
| `cheek_arm` | rec_branching_tree_with_two_independent_rotary_branches_754fee72af00441ea2a027db63e9f456 | L75-L227 | eligible if compatible | FIXED cheek @ frame；REV arm |
| `bracket_carrier` | rec_branching_tree_with_two_independent_rotary_branches_388259dfa1954efcb9d005d5372d331c | L68-L270 | eligible if compatible | FIXED bracket @ spine；REV branch |

### Slot C：mount_layout

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `staggered_vertical_opposed` | rec_branching_tree_with_two_independent_rotary_branches_0004 | L33-L36, L97-L133 | eligible if compatible | upper@( +x, z_hi )，lower@( −x, z_lo ) |
| `bilateral_same_height` | rec_branching_tree_with_two_independent_rotary_branches_0002 | L28-L29, L97-L168 | eligible if compatible | left@(−x,z)，right@( +x,z ) 同 Z |
| `diagonal_quadrants` | rec_branching_tree_with_two_independent_rotary_branches_0b2bb69a478c46ea9ef4516c12cfebe9 | L186-L203 | eligible if compatible | upper_left + lower_right 对角 |
| `forward_plus_side` | rec_branching_tree_with_two_independent_rotary_branches_3239916e50454d5380d9ad7b2b222884 | L99-L124, L214-L252 | eligible if compatible | 前向 Y 站 + 侧向 X 站 |
| `orthogonal_fork_plate` | rec_branching_tree_with_two_independent_rotary_branches_3b8476bde00749aaaa84928c35c21164 | L29-L30, L330-L360 | eligible if compatible | 上叉 pitch X；下板 yaw Z |

### Slot D：joint_axis_policy

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `parallel_Y_pitch` | rec_branching_tree_with_two_independent_rotary_branches_0004 | L141-L168 | eligible if compatible | 两分支轴 `(0,1,0)` 同向 |
| `parallel_Z_yaw` | rec_branching_tree_with_two_independent_rotary_branches_69dc78b32e6440de80ec472e5f718e5c | L167-L190 | eligible if compatible | 两分支轴 `(0,0,1)` 同向 |
| `mirror_Y` | rec_branching_tree_with_two_independent_rotary_branches_2e7d777ce8c840c9add9a081c6f0d857 | L167-L180 | eligible if compatible | `(0,−1,0)` / `(0,1,0)` 镜像 |
| `orthogonal_per_branch` | rec_branching_tree_with_two_independent_rotary_branches_3239916e50454d5380d9ad7b2b222884 | L241-L252 | eligible if compatible | 分支 0 用 Y，分支 1 用 X |
| `two_link_chain_axes` | rec_branching_tree_with_two_independent_rotary_branches_0001 | L252-L287 | eligible if compatible | 每侧 shoulder+elbow 双关节链 |

## 槽位图（slot graph）

pattern: `mixed`

```text
support_carrier
  --[two fixed bearing stations / bracket sockets]-->
mount_layout
  --[station_0/1 pivot origin + clearance plane]-->
joint_axis_policy
  --[two REVOLUTE joints, one per station]-->
branch_topology[branch_count fixed at 2]
```

- `support_carrier` 是唯一 grounded root parent；允许 `hub_spoke` / `cheek_arm` / `bracket_carrier` 发出 FIXED 中间件，但这些不算 rotary branch。
- `mount_layout` 定义 `station_0` / `station_1` 的 pivot origin、左右/上下错位和对称策略。
- `joint_axis_policy` 消费 station 接口，定义 axis、rest angle、motion limits。
- `branch_topology` 在 station 上 emit 两个 moving branch leaves。

## 每槽位 Module Emits / Interfaces

### Slot A / support_carrier

| module | emits | 描述 | 来源 |
|---|---|---|
| `vertical_spine` | parts | fixed `support`/`spine`；base_plate、spine_column、root blocks、hinge plates | 0004 / L83-L133 |
| `vertical_spine` | downstream interface | `station_0/1.pivot_origin` at staggered hub X/Z | 0004 / L141-L168 |
| `vertical_mast` | parts | fixed `mast`；base disc、shaft、hub blocks | 2e7d777c / L54-L97 |
| `tower_stand` | parts | fixed `stand`；heavy base、tower collar | 69dc78b3 / L33-L120 |
| `ladder_frame` | parts | fixed `frame`；dual uprights、rungs | 754fee72 / L45-L72 |
| `trunk_y_tree` | parts | fixed `trunk`；Y-bar + bilateral hubs | 0002 / L60-L135 |
| `pedestal_or_wall` | parts | fixed `pedestal` or `backplate`；clamp pads | d6a279d4 / L157-L229 |

### Slot B / branch_topology

| module | emits | 描述 | 来源 |
|---|---|---|
| `single_rigid_branch` | parts | two moving `upper_branch`/`lower_branch` or `branch_0/1` | ca64a5ac / L40-L168 |
| `two_link_chain` | parts + joints | four revolute：`upper`+`forearm` per side | 0001 / L136-L287 |
| `hub_spoke` | fixed + revolute | FIXED hub child；REV spoke leaf | 1c3aae32 / L53-L152 |
| `cheek_arm` | fixed + revolute | FIXED cheek；REV arm | 754fee72 / L196-L227 |
| `bracket_carrier` | fixed + revolute | FIXED bracket pod；REV branch | 388259df / L238-L270 |

### Slot C / mount_layout

| module | emits | 描述 | 来源 |
|---|---|---|
| `staggered_vertical_opposed` | interface | upper/lower stations at different Z and opposite X | 0004 / L33-L36 |
| `bilateral_same_height` | interface | mirrored ±X hubs at common Z | 0002 / L28-L29 |
| `diagonal_quadrants` | interface | diagonal quadrant placement | 0b2bb69a / L186-L203 |
| `forward_plus_side` | interface | forward-facing + side-facing stations | 3239916e / L214-L252 |
| `orthogonal_fork_plate` | interface | upper fork + lower plate stations | 3b8476bd / L330-L360 |

### Slot D / joint_axis_policy

| module | emits | 描述 | 来源 |
|---|---|---|
| `parallel_Y_pitch` | joints | 2× REVOLUTE，axis `(0,1,0)` | 0004 / L141-L168 |
| `parallel_Z_yaw` | joints | 2× REVOLUTE，axis `(0,0,1)` | 69dc78b3 / L167-L190 |
| `mirror_Y` | joints | mirror Y pitch per branch | 2e7d777c / L167-L180 |
| `orthogonal_per_branch` | joints | per-branch orthogonal axes | 3239916e / L241-L252 |
| `two_link_chain_axes` | joints | 4 revolute chain semantics | 0001 / L252-L287 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_carrier` | enum | 6 modules | sampled | procedural sampler + compatibility | Slot A |
| `branch_topology` | enum | 5 modules | sampled | gated by support + mount | Slot B |
| `mount_layout` | enum | 5 modules | sampled | gated by support geometry | Slot C |
| `joint_axis_policy` | enum | 5 modules | sampled | gated by mount + branch topology | Slot D |
| `branch_count` | int | exactly `2` | `2` | 类别身份；不采样 | 全部 5 星 |
| `station_spacing_scale` | float | [0.85, 1.20] | sampled | hub Z/X 间距派生 | 0004 / L33-L36 |
| `arm_reach_scale` | float | [0.80, 1.25] | sampled | beam/pad 长度 clamp | 0004 / L38-L41 |
| `joint_limit_style` | enum | `compact`, `medium`, `wide` | sampled | 映射 half-angle / travel | 0004 / L43, L148-L167 |

## Multiplicity / Copy Logic

- `count_param`: `branch_count`
- `N_range`: exactly `2`；禁止 1、3 或更多分支。
- sampling domain: 固定数量；`mount_layout` 派生 `station_0/1` 角色名（`upper_branch`/`lower_branch` 或 `left_branch`/`right_branch`）。
- copied object: 每个 station 一个 moving branch leaf + 一个 `REVOLUTE`（`two_link_chain` 每侧额外 1 个 elbow 关节，仍计为 1 个 branch leaf 拓扑）。
- naming: `upper_branch`/`lower_branch`、`left_branch`/`right_branch` 或 `branch_0`/`branch_1`。
- placement: station origins 来自 `mount_layout`；branch 几何在局部坐标系沿 reach 方向放置。
- joint policy: 恰好两个独立 rotary leaves；FIXED hub/cheek/bracket 不计入 branch 数。
- source/gating: 所有组合须保留可见 hub/bearing 支撑与 closed-pose clearance。

## 拓扑多样性审计

总组合数：6 × 5 × 5 × 5 = 750 raw；compatibility gating 后估计 **55–75** 合法组合。


理由：35 样本中观测到 31 种独立 4-slot 组合（88.6%）；support、mount、axis、branch topology 四层真实结构差异充足。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：
- deterministic procedural sampling：`support_carrier` → legal `mount_layout` → legal `joint_axis_policy` → compatible `branch_topology` → continuous scales。
- `seed=0` 不特殊。
- compatibility matrix 排除 `two_link_chain` 与非 bilateral/staggered mount 的非法配对；`hub_spoke` 禁止 `parallel_Z_yaw`；`cheek_arm` 仅配 `ladder_frame`。
- 初始 sweep seeds `0-49`；成熟度审计 `0-999`；viewer 预览覆盖各 support 族。

Topology target：1000-seed distinct 富类别建议 ≥300（report-only）；gating 后仍应有充足合法组合。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | support → mount → axis → branch | `slot_choices_for_seed` 反映实际 build |
| compatibility matrix | 见下表 | 无 floating hub、closed-pose 穿模 |
| controlled local variation | `station_spacing_scale`, `arm_reach_scale` | 不破坏 InterfaceSpec |
| regression overrides | none 初版 | 仅失败回归或审核指定 |
| random sweep | 0-49 初验，0-999 成熟度 | diversity + 双分支独立性 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_carrier | 6 | yes | yes | spine/mast/tower/ladder/trunk/pedestal |
| branch_topology | 5 | yes | yes | single/2-link/hub/cheek/bracket |
| mount_layout | 5 | yes | yes | stagger/bilateral/diagonal/forward-side/orthogonal |
| joint_axis_policy | 5 | yes | yes | Y/Z/mirror/orthogonal/2-link |

### Compatibility matrix / gating

| support_carrier | legal mount_layout | legal branch_topology | gating notes |
|---|---|---|---|
| `vertical_spine` | staggered, bilateral, diagonal | single, bracket, two_link | two_link 需 bilateral 或 staggered |
| `vertical_mast` | staggered, forward_plus_side | single, hub_spoke | hub_spoke 优先 mast |
| `tower_stand` | staggered, bilateral | single | 要求 collar Z 间距 > arm thickness |
| `ladder_frame` | staggered, cheek staggered | single, cheek_arm | cheek_arm 专属 ladder |
| `trunk_y_tree` | bilateral_same_height | single, two_link | 禁止 diagonal |
| `pedestal_or_wall` | bilateral, staggered | single | wall 版需可见 clamp pod |

| branch_topology | legal joint_axis_policy | gating notes |
|---|---|---|
| `two_link_chain` | two_link_chain_axes | 禁止 orthogonal_per_branch |
| `hub_spoke` | mirror_Y, parallel_Y_pitch | 禁止 parallel_Z_yaw |
| `cheek_arm` | mirror_Y | 仅 ladder + cheek mount |
| `bracket_carrier` | parallel_Y_pitch, parallel_−Y | 需 side bracket clearance |

## Validator

- `__modular__ = True`
- `slot_choices_for_seed` 返回四个 slot 的实际 module 名
- `config_from_seed` 全 seed procedural sampling；`seed=0` 不特殊
- 恰好两个独立 `REVOLUTE` branch leaves（`two_link_chain` 计 4 关节但 2 个 branch 拓扑）
- 每个关节 origin 在可见 hub/bearing/cheek/bracket 内
- 单关节 pose 不改变另一分支 world pose（独立性测试）
- 禁止 mimic、共享 child drive

## Reject cases

- 分支数 ≠ 2
- 串联臂 A→B→C 单链（非双树）
- 单 rotor 双叶片装饰
- 隐藏/漂浮 joint origin
- FIXED 中间件未接触 support
- 仅换色/尺寸的假 candidate
- closed-pose 双分支互穿或穿 support
- 与 `three_independent_rotary_branches` 混淆（3 分支）

## 与相邻类别的边界

- 不该混入：`branching_tree_with_three_independent_rotary_branches`（分支数 3 vs 2）。
- 不该混入：`robotic_arms` / `serial_elbow_arm`（单链串联 vs 分叉树）。
- 不该混入：`dual_independent_finger_chains`（指状链 vs 工装支臂）。
- 不该混入：风扇/涡轮叶片（共享 rotor）。
- 不该混入：静态树枝（无可动 REVOLUTE leaves）。

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 用户 2026-06-09 确认通过；进入 TEMPLATE_AFTER_REVIEW |

## 模板实现备注（可选）

- 推荐 factories：`build_support_carrier`、`resolve_two_stations`、`build_branch_topology`、`attach_two_rotary_branches`。
- `two_link_chain` 须保留 cadquery mesh 复杂度（`0001`），不得降级为纯 Box。
- `MatingContract`：hub plate 与 branch barrel 接触；cheek 捕获 arm barrel。
- `hub_spoke` / `cheek_arm` / `bracket_carrier` 的 FIXED 子件须 `fail_if_isolated_parts` 豁免范围内显式连通。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | `vertical_spine` | rec_…_0004 | L83-L133 | spine + hinge pads |
| S2 | A | `vertical_mast` | rec_…_2e7d777c | L54-L97, L125-L165 | mast + hub blocks |
| S3 | A | `tower_stand` | rec_…_69dc78b3 | L33-L167 | tower collar stand |
| S4 | A | `ladder_frame` | rec_…_754fee72 | L45-L72, L143-L195 | ladder uprights |
| S5 | A | `trunk_y_tree` | rec_…_0002 | L60-L135 | Y-trunk bilateral |
| S6 | A | `pedestal_or_wall` | rec_…_d6a279d4 | L157-L229 | pedestal/wall clamp |
| S7 | B | `single_rigid_branch` | rec_…_ca64a5ac | L40-L168 | single revolute arms |
| S8 | B | `two_link_chain` | rec_…_0001 | L136-L287 | dual 2-link chains |
| S9 | B | `hub_spoke` | rec_…_1c3aae32 | L53-L152 | fixed hub + spoke |
| S10 | B | `cheek_arm` | rec_…_754fee72 | L75-L227 | cheek + arm |
| S11 | B | `bracket_carrier` | rec_…_388259df | L68-L270 | bracket + branch |
| S12 | C | `staggered_vertical_opposed` | rec_…_0004 | L33-L36, L97-L133 | staggered hubs |
| S13 | C | `bilateral_same_height` | rec_…_0002 | L28-L29, L97-L168 | ±X same Z |
| S14 | C | `diagonal_quadrants` | rec_…_0b2bb69a | L186-L203 | diagonal stations |
| S15 | C | `forward_plus_side` | rec_…_3239916e | L214-L252 | forward + side |
| S16 | C | `orthogonal_fork_plate` | rec_…_3b8476bd | L330-L360 | fork + plate |
| S17 | D | `parallel_Y_pitch` | rec_…_0004 | L141-L168 | Y-axis pair |
| S18 | D | `parallel_Z_yaw` | rec_…_69dc78b3 | L167-L190 | Z-axis pair |
| S19 | D | `mirror_Y` | rec_…_2e7d777c | L167-L180 | mirror Y |
| S20 | D | `orthogonal_per_branch` | rec_…_3239916e | L241-L252 | Y + X |
| S21 | D | `two_link_chain_axes` | rec_…_0001 | L252-L287 | 4-joint chain |
