## 元信息

| 项 | 值 |
|---|---|
| slug | `branching_tree_with_three_independent_rotary_branches` |
| template path | `agent/templates/branching_tree_with_three_independent_rotary_branches.py` |
| test path (optional) | `tests/agent/test_branching_tree_with_three_independent_rotary_branches_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 38 |
| read_count | 38 |
| read_scope | all 5-star samples in this category; for each retained 5-star sample, `record.json`, `revision.json`, `prompt.txt`, and `model.py` were opened/read |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

这个类别是一个刚性固定支撑上挂载 **三个且仅三个独立 rotary branch** 的机械树。三个分支都应有自己的可见 pivot / hub / bearing station，并通过独立 `REVOLUTE` joint 运动；它们不是串联链条，也不是同一个 rotor 的三个叶片。成熟形态通常是检具、工装树、service panel bracket、pedestal/tower stand 或 underslung bridge frame：固定支撑提供三个清楚的接口站，活动分支提供刚性 arm、terminal pad / fork / tab / end plate。

不应混入四臂/二臂机构、风扇/涡轮/转盘、机器人三关节串联臂、单个 turnstile rotor、纯装饰树枝或没有真实 articulated moving parts 的静态雕塑。

## 槽位 + 候选模块表

### Slot A：support_carrier

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `radial_hub_plate` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L97-L152 | eligible if compatible | 中心圆盘/center boss，三组等角 spoke + hinge pad + thrust washer + pin cap；适合 planar radial 三臂 |
| `tower_pedestal_collar_stack` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L51-L91, L155-L205 | eligible if compatible | 圆形 base + plinth + vertical shaft，每个高度有 support flange；适合错层同轴 yaw arms |
| `rack_spine_side_saddles` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L51-L74, L153-L158 | eligible if compatible | 长 foot/upright/top cap + 左右交错 side saddles；三组支承在不同高度和左右侧 |
| `mixed_axis_rect_spine` | rec_branching_tree_with_three_independent_rotary_branches_091a5a769f1949e4a75abd4814751cd1 | L41-L108 | eligible if compatible | 矩形 spine，低位 trunnion cheeks、前向 vertical collar、高位 longitudinal collar；三个 bearing station 轴向不同 |
| `service_panel_backplate_pods` | rec_branching_tree_with_three_independent_rotary_branches_b5b95a66f47d4ccba765be8e92882a0b | L76-L106, L195-L219 | eligible if compatible | backplate + vertical spine + branch pods，pod 由 bridge/housing/cheeks/pin 形成 panel-mounted 接口 |
| `underslung_top_bridge` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L43-L104, L148-L190 | eligible if compatible | 顶部 bridge + hanger bracket + ribs，三个分支向下悬挂，固定支撑和活动臂视觉区分明显 |

### Slot B：three_station_axis_layout

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `planar_radial_z_axes` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L113-L174 | eligible if compatible | 三个等角 hinge_xy，三条 `REVOLUTE` 从 hub 到 arm，axis `(0, 0, 1)`，适合圆盘/径向布局 |
| `stacked_column_z_axes` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L193-L255 | eligible if compatible | lower/middle/upper 三个高度，parent 为 pedestal，三条同轴 Z revolute，rest angle 可错开 |
| `rack_alternating_side_axes` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L221-L247 | eligible if compatible | lower/middle/upper 接在 spine 左右交错 saddles，三条独立 revolute，joint origin 在可见 side saddle |
| `mixed_xyz_station_axes` | rec_branching_tree_with_three_independent_rotary_branches_276666fe4ead43919b478bf5249836d4 | L160-L204, L301-L329 | eligible if compatible | 上/中/下三个 bearing station 分别使用 Z/Y/X 轴；适合 inspection head / compact tooling tree |
| `panel_pod_x_axes` | rec_branching_tree_with_three_independent_rotary_branches_778c5ffe04a9472fb6a76e0ab6fd4ea6 | L102-L194 | eligible if compatible | backplate 固定 pod，pod 再以 X 轴 revolute 到 plate；允许 fixed pod 中间件但必须仍有三个 moving leaves |
| `underslung_hanger_y_axes` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L155-L190 | eligible if compatible | bridge 下方三个 hanger bracket，bracket-to-arm 为 Y 轴 revolute；适合吊挂式 frame |

### Slot C：branch_arm_set

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_linkage_eye_arms` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L28-L86, L153-L174 | eligible if compatible | 扁平 linkage arm，pivot eye、distal pad、boss、lightening slot；三臂同构但 angle/name 独立 |
| `collar_gusseted_tower_arms` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L94-L147, L218-L255 | eligible if compatible | collar + flanges + tapered beam + gusset + tip stop；适合 column collar stack |
| `pad_fork_tab_rack_set` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L77-L142, L160-L247 | eligible if compatible | 三个端部风格分别为 pad / fork / tab，带 hub、neck、rib、beam；适合 rack 或 mixed-axis spine |
| `fork_plate_yoke_tooling_set` | rec_branching_tree_with_three_independent_rotary_branches_5587a586efc940938efbddd243355ec3 | L146-L195, L213-L283 | eligible if compatible | fork branch、profile plate branch、yoke branch 三种活动臂，分别从 mast 的不同面独立旋转 |
| `metrology_pad_rect_fork_set` | rec_branching_tree_with_three_independent_rotary_branches_e5ea9cde1c164220bf1da2acaede1ae4 | L68-L81, L149-L236 | eligible if compatible | journal/collar 根部 + round pad、rect pad、angled fork 三种终端，强调检具/测量夹具身份 |
| `underslung_blade_arms` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L107-L138, L163-L190 | eligible if compatible | 向下悬挂的 blade/profile arm，长度可三档变化，root top cap 接 hanger pivot |

## 槽位图（slot graph）

pattern: `mixed`

```text
support_carrier
  --[fixed support stations / bearing pads / bracket sockets]-->
three_station_axis_layout
  --[three REVOLUTE joints, one per station]-->
branch_arm_set[branch_count fixed at 3]
```

- `support_carrier` 是唯一固定 root parent，或在 `panel_pod_x_axes` / `underslung_hanger_y_axes` 中额外 emit 三个 fixed bracket/pod child；这些中间件必须刚性连接到 root，不算 rotary branch。
- `three_station_axis_layout` 消费 support 的 `station_0/1/2` 接口，定义每个 station 的 pivot origin、axis、rest orientation、clearance plane 和 joint limits。
- `branch_arm_set` 消费三个 station 的 pivot interface，emit 三个 moving branch parts：`branch_0/1/2` 或 semantic names such as `lower_branch`, `middle_branch`, `upper_branch`。
- 跨 slot InterfaceSpec 必须包含：`support_root_frame`、`station_i.pivot_origin`、`station_i.axis_local`、`station_i.mating_face`、`station_i.clearance_plane`、`station_i.branch_rest_rpy`。
- `panel_pod_x_axes` 与 `underslung_hanger_y_axes` 允许 `support -> bracket/pod` fixed articulation，再 `bracket/pod -> moving branch` revolute；validator 仍按三个 independent rotary leaves 验收。

## 每槽位 Module Emits / Interfaces

### Slot A / support_carrier modules

| module | emits | 描述 | 来源 |
|---|---|---|---|
| `radial_hub_plate` | parts | fixed `support`; center plate, boss, three hinge pads/pins | S1 / model.py:L97-L152 |
| `radial_hub_plate` | upstream interface | ground/root frame at hub center | S1 / model.py:L97-L152 |
| `radial_hub_plate` | downstream interface | three radial `station_i` origins at 120 degree spacing, Z-axis bearing faces | S1 / model.py:L113-L174 |
| `tower_pedestal_collar_stack` | parts | fixed `support`; base disc, plinth, tower shaft, support flanges | S2 / model.py:L51-L91, L155-L205 |
| `tower_pedestal_collar_stack` | downstream interface | three stacked collar stations along Z, each with horizontal support flange | S2 / model.py:L193-L255 |
| `rack_spine_side_saddles` | parts | fixed `support`; upright spine with side saddles and top/foot caps | S3 / model.py:L51-L74, L153-L158 |
| `rack_spine_side_saddles` | downstream interface | left/right alternating side saddle sockets with visible hub disks | S3 / model.py:L221-L247 |
| `mixed_axis_rect_spine` | parts | fixed `support`; rectangular spine with trunnion cheeks, forward collar, high longitudinal collar | S4 / model.py:L41-L108 |
| `mixed_axis_rect_spine` | downstream interface | X/Y/Z-oriented bearing stations at low/forward/high positions | S4 / model.py:L215-L241 |
| `service_panel_backplate_pods` | parts | fixed `support`; wall/backplate, spine, branch pods as fixed visual or fixed child modules | S5 / model.py:L76-L106, L195-L219 |
| `service_panel_backplate_pods` | downstream interface | front-facing pod sockets around spine with X-axis journal alignment | S5 / model.py:L207-L255 |
| `underslung_top_bridge` | parts | fixed `support`; top bridge plus three hanger brackets | S6 / model.py:L43-L104, L148-L190 |
| `underslung_top_bridge` | downstream interface | underside bracket pivot points and downward clearance volume | S6 / model.py:L155-L190 |

### Slot B / three_station_axis_layout modules

| module | emits | 描述 | 来源 |
|---|---|---|---|
| `planar_radial_z_axes` | internal joints | three support-to-branch `REVOLUTE` joints, axis `(0, 0, 1)` | S7 / model.py:L113-L174 |
| `planar_radial_z_axes` | downstream interface | branch local X points radially outward from hinge pad | S7 / model.py:L113-L174 |
| `stacked_column_z_axes` | internal joints | lower/middle/upper `REVOLUTE` joints on same tower axis family | S8 / model.py:L193-L255 |
| `stacked_column_z_axes` | downstream interface | branch origins stacked by height; rest angles staggered to avoid overlap | S8 / model.py:L193-L255 |
| `rack_alternating_side_axes` | internal joints | three side-saddle `REVOLUTE` joints with side-dependent origin/rpy | S9 / model.py:L221-L247 |
| `rack_alternating_side_axes` | downstream interface | lower/middle/upper branch roles alternate left/right side of spine | S9 / model.py:L221-L247 |
| `mixed_xyz_station_axes` | internal joints | three independent `REVOLUTE` joints with Z, Y, and X axes | S10 / model.py:L160-L204, L301-L329 |
| `mixed_xyz_station_axes` | downstream interface | each station has its own orthogonal clearance plane and bearing race orientation | S10 / model.py:L160-L204, L301-L329 |
| `panel_pod_x_axes` | fixed + revolute joints | optional fixed pod children plus three X-axis revolute leaf joints | S11 / model.py:L102-L194 |
| `panel_pod_x_axes` | downstream interface | branch tip plates or short pods rotate about local X | S11 / model.py:L102-L194 |
| `underslung_hanger_y_axes` | fixed + revolute joints | fixed hanger bracket to bridge, then Y-axis revolute arm | S12 / model.py:L155-L190 |
| `underslung_hanger_y_axes` | downstream interface | local arm length extends downward/forward from bracket pivot | S12 / model.py:L155-L190 |

### Slot C / branch_arm_set modules

| module | emits | 描述 | 来源 |
|---|---|---|---|
| `flat_linkage_eye_arms` | parts | three moving flat arm parts with pivot eye, distal pad, boss, lightening slot | S13 / model.py:L28-L86, L153-L174 |
| `flat_linkage_eye_arms` | upstream interface | consumes radial or planar Z-axis hinge; local X is arm reach direction | S13 / model.py:L113-L174 |
| `collar_gusseted_tower_arms` | parts | three collar/flange arms with tapered beam, gusset and tip stop | S14 / model.py:L94-L147, L218-L255 |
| `collar_gusseted_tower_arms` | upstream interface | consumes stacked column Z-axis collars | S14 / model.py:L218-L255 |
| `pad_fork_tab_rack_set` | parts | lower pad branch, middle fork branch, upper tab branch | S15 / model.py:L77-L142, L160-L247 |
| `pad_fork_tab_rack_set` | upstream interface | consumes rack or mixed side stations; each branch has a root hub/barrel | S15 / model.py:L221-L247 |
| `fork_plate_yoke_tooling_set` | parts | fork, profiled plate and yoke branches from different mast faces | S16 / model.py:L146-L195, L213-L283 |
| `fork_plate_yoke_tooling_set` | upstream interface | consumes mixed face-mounted station axes; branch local axis may be X or Y | S16 / model.py:L237-L280 |
| `metrology_pad_rect_fork_set` | parts | journal/collar roots plus round pad, rectangular pad, angled fork terminal | S17 / model.py:L68-L81, L149-L236 |
| `metrology_pad_rect_fork_set` | upstream interface | consumes column/rack station pivots with explicit journal clearance | S17 / model.py:L237-L263 |
| `underslung_blade_arms` | parts | three moving blade/profile arms with length variants | S18 / model.py:L107-L138, L163-L190 |
| `underslung_blade_arms` | upstream interface | consumes underslung hanger bracket pivot, local arm hangs below bridge | S18 / model.py:L170-L190 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_carrier` | enum | `radial_hub_plate`, `tower_pedestal_collar_stack`, `rack_spine_side_saddles`, `mixed_axis_rect_spine`, `service_panel_backplate_pods`, `underslung_top_bridge` | sampled | deterministic procedural sampler chooses, then compatibility gates axis/branch modules | Slot A table |
| `three_station_axis_layout` | enum | `planar_radial_z_axes`, `stacked_column_z_axes`, `rack_alternating_side_axes`, `mixed_xyz_station_axes`, `panel_pod_x_axes`, `underslung_hanger_y_axes` | sampled | must be compatible with support station interfaces | Slot B table |
| `branch_arm_set` | enum | `flat_linkage_eye_arms`, `collar_gusseted_tower_arms`, `pad_fork_tab_rack_set`, `fork_plate_yoke_tooling_set`, `metrology_pad_rect_fork_set`, `underslung_blade_arms` | sampled | must consume station axes and clearance planes from layout | Slot C table |
| `branch_count` | int | exactly `3` | `3` | category identity; not sampled | all 5-star sources |
| `station_spacing_scale` | float | `[0.85, 1.20]` | sampled | support dimensions derive clearance between station origins | S2/S3/S10 |
| `arm_reach_scale` | float | `[0.80, 1.25]` | sampled | arm reach shortened by compatibility gate for compact supports | S13-S18 |
| `joint_limit_style` | enum | `compact`, `medium`, `wide` | sampled | maps to per-axis lower/upper ranges, capped by collision gates | S7-S12 |
| `terminal_detail_density` | enum | `plain`, `machined`, `service_fasteners` | sampled | module-local visuals only; does not create new topology | S5/S10/S17 |

## Multiplicity / Copy Logic

- `count_param`: `branch_count`
- `N_range`: exactly `3`; do not sample 2, 4, or arbitrary branch count.
- sampling domain: fixed count, but branch role names and station placements are derived from `three_station_axis_layout`.
- copied object: each station emits one moving branch leaf and one `REVOLUTE` joint; some layouts also emit one fixed bracket/pod per station before the moving leaf.
- naming: prefer semantic names when layout has vertical roles (`lower_branch`, `middle_branch`, `upper_branch`); otherwise use stable `branch_0`, `branch_1`, `branch_2`.
- placement: station origins come from the axis layout; branch arm geometry is placed in local frame and rotated by `branch_rest_rpy`.
- joint policy: exactly three independent rotary leaf joints are required. Fixed bracket/pod joints are allowed but do not count as rotary branches.
- source/gating: all sampled modules must preserve visible per-station hub/bearing support and clearance between closed-pose arms.

## 拓扑多样性审计

总组合数：6 support carriers x 6 axis layouts x 6 branch arm sets = 216 raw combinations.


理由：即使 compatibility gates remove cross-family combinations, the remaining legal domain still contains radial hub, tower stack, rack spine, mixed-axis spine, panel pod and underslung bridge support families, plus multiple branch terminal sets and axis layouts. Distinct part trees include direct support-to-branch joints and fixed bracket/pod intermediate trees.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：

- deterministic procedural sampling first chooses `support_carrier`, then legal `three_station_axis_layout`, then compatible `branch_arm_set`, then continuous dimensions and detail density.
- `seed=0` is ordinary and has no anchor/reference semantics.
- compatibility matrix / gating filters illegal combinations before build, and `resolve_config` may shorten arms, widen station spacing, or fallback to a compatible branch set when support clearance is too tight.
- no regression overrides by default. Future overrides must be sparse, explicit, and tied to a failed sweep seed or reviewer-selected regression example.
- initial random sweep should run seeds `0-49`; maturity audit should inspect seeds `0-999` and viewer-preview a small spread across all support families.

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本 spec raw topology count 216，低于 300 时记录该离散结构空间上限，除非实现把额外 N/布局桶纳入 slot choice tuple。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | support -> legal axis layout -> legal branch arm set -> dimensions/detail; weighted choices allowed but all eligible modules must be reachable | `slot_choices_for_seed(seed)` returns the actual built support/layout/branch modules |
| compatibility matrix | pair support station family with axis layout; gate branch sets by axis orientation, local reach direction, and required clearance plane | no floating brackets, no branch/support penetration in closed pose, joint origins visually inside hubs |
| regression overrides | none in initial template | any future override must include seed and failure/reviewer reason |
| random sweep | seeds `0-49` for initial pass, `0-999` for maturity audit | , independent revolute count, bracket support contracts, collision clusters |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| support_carrier | 6 | yes | yes | covers radial, tower, rack, mixed-axis spine, panel, underslung |
| three_station_axis_layout | 6 | yes | yes | includes direct and fixed-bracket intermediate joint topologies |
| branch_arm_set | 6 | yes | yes | includes homogeneous linkage and heterogeneous pad/fork/tab sets |

### Compatibility matrix / gating

| support_carrier | legal axis layouts | preferred branch arm sets | gating notes |
|---|---|---|---|
| `radial_hub_plate` | `planar_radial_z_axes` | `flat_linkage_eye_arms`, `pad_fork_tab_rack_set` | require 120-degree station spacing and short enough arm reach to avoid branch overlap |
| `tower_pedestal_collar_stack` | `stacked_column_z_axes` | `collar_gusseted_tower_arms`, `metrology_pad_rect_fork_set` | require vertical spacing larger than branch thickness + collar height |
| `rack_spine_side_saddles` | `rack_alternating_side_axes`, `stacked_column_z_axes` | `pad_fork_tab_rack_set`, `metrology_pad_rect_fork_set` | require side alternation and no branch crossing through upright |
| `mixed_axis_rect_spine` | `mixed_xyz_station_axes` | `fork_plate_yoke_tooling_set`, `pad_fork_tab_rack_set`, `metrology_pad_rect_fork_set` | each branch local frame must align to station axis; reject if terminal points back into spine |
| `service_panel_backplate_pods` | `panel_pod_x_axes` | `metrology_pad_rect_fork_set`, `underslung_blade_arms` | fixed pod must visibly contact backplate; moving leaf count remains three |
| `underslung_top_bridge` | `underslung_hanger_y_axes` | `underslung_blade_arms`, `fork_plate_yoke_tooling_set` | require downward clearance under bridge and bracket ribs not intersecting arm sweep |

## Validator

- `__modular__` is `True`.
- `slot_choices_for_seed(seed)` returns implemented module names for `support_carrier`, `three_station_axis_layout`, and `branch_arm_set`.
- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds; `seed=0` is not special.
- The built model has exactly three independent rotary branch leaves, each with one required `REVOLUTE` joint.
- Fixed bracket/pod intermediate parts are allowed only when they are visibly supported and connected by fixed articulation or same-parent visual composition.
- Each `REVOLUTE` joint origin lies inside or on a visible hub/bearing/pod, and its axis aligns with the station's InterfaceSpec.
- compatibility matrix / gating prevents illegal support-axis-branch combinations, floating brackets, branch/backbone penetration, and closed-pose collisions.
- Optional regression overrides are sparse and justified; the final template does not endlessly cycle a small curated table as the main seed domain.
- Viewer check confirms three branches can move independently and are not a single shared rotor or serial chain.

## Reject cases

- Fewer or more than three rotary branches.
- A single rotor hub with three decorative blades where branches are not independent moving parts.
- Serial arm chain where branch 2 is parented to branch 1 or branch 3 is parented to branch 2.
- Hidden or floating joint origins without visible bearing, collar, pod, bracket or saddle support.
- Fixed bracket/pod modules that float away from the support carrier.
- Branch terminal differences that are only color/material changes with identical part tree.
- Support-only sculpture with no three `REVOLUTE` branch leaves.
- Arms intersect the support in closed pose or collide with each other across common sampled ranges.

## 与相邻类别的边界

- 不该混入：`three_blade_rotor` / wind turbine / fan（这类是同一 rotor 或 coaxial blade set，不是三个 independent branch joints）。
- 不该混入：serial robotic arm / multi-joint manipulator（三个旋转 joint 不应串联成一条 kinematic chain）。
- 不该混入：two-branch or four-branch rotary fixture（branch count 是身份约束，固定为 3）。
- 不该混入：static branching sculpture（没有 three independent `REVOLUTE` leaves）。
- 不该混入：generic panel with knobs（缺少可见 branch arms and rotary branch motion semantics）。

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft; no template implementation has been started |

## 模板实现备注（可选）

- Recommended high-level factories: `build_support_carrier`, `resolve_station_interfaces`, `build_branch_arm_set`, `attach_three_rotary_branches`.
- `InterfaceSpec` should expose `station_i.pivot_origin`, `axis_local`, `rest_rpy`, `mating_face`, `clearance_plane`, and optional `fixed_intermediate_parent`.
- `MatingContract` should assert every station has visible support around the pivot, arm root overlaps the bearing envelope enough to read as mechanically seated, and branch sweep clearance remains positive.
- For `panel_pod_x_axes` and `underslung_hanger_y_axes`, count branch leaves by moving `REVOLUTE` children, not by intermediate fixed pods/brackets.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A | `radial_hub_plate` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L97-L152 | fixed radial hub/support geometry |
| S2 | Slot A | `tower_pedestal_collar_stack` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L51-L91, L155-L205 | tower/pedestal support geometry |
| S3 | Slot A | `rack_spine_side_saddles` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L51-L74, L153-L158 | rack spine and side saddle carrier |
| S4 | Slot A | `mixed_axis_rect_spine` | rec_branching_tree_with_three_independent_rotary_branches_091a5a769f1949e4a75abd4814751cd1 | L41-L108 | rectangular spine with three different bearing stations |
| S5 | Slot A | `service_panel_backplate_pods` | rec_branching_tree_with_three_independent_rotary_branches_b5b95a66f47d4ccba765be8e92882a0b | L76-L106, L195-L219 | service panel backplate and pod support |
| S6 | Slot A | `underslung_top_bridge` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L43-L104, L148-L190 | top bridge and hanger brackets |
| S7 | Slot B | `planar_radial_z_axes` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L113-L174 | radial station placement and Z-axis revolute joints |
| S8 | Slot B | `stacked_column_z_axes` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L193-L255 | stacked column branch origins and joints |
| S9 | Slot B | `rack_alternating_side_axes` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L221-L247 | alternating side saddle station origins |
| S10 | Slot B | `mixed_xyz_station_axes` | rec_branching_tree_with_three_independent_rotary_branches_276666fe4ead43919b478bf5249836d4 | L160-L204, L301-L329 | mixed X/Y/Z bearing station layout |
| S11 | Slot B | `panel_pod_x_axes` | rec_branching_tree_with_three_independent_rotary_branches_778c5ffe04a9472fb6a76e0ab6fd4ea6 | L102-L194 | fixed pod plus X-axis rotary plate leaves |
| S12 | Slot B | `underslung_hanger_y_axes` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L155-L190 | bracket-to-arm underslung revolute pattern |
| S13 | Slot C | `flat_linkage_eye_arms` | rec_branching_tree_with_three_independent_rotary_branches_b36b00889b1e44bba4e5125134fa8a7e | L28-L86, L153-L174 | flat linkage arm geometry and radial attach |
| S14 | Slot C | `collar_gusseted_tower_arms` | rec_branching_tree_with_three_independent_rotary_branches_54f3f9b9686e443e9d7f91f87d923b6e | L94-L147, L218-L255 | collar/gusset/tip-stop arm family |
| S15 | Slot C | `pad_fork_tab_rack_set` | rec_branching_tree_with_three_independent_rotary_branches_b7cca747d4964a3b9db13d07388595a2 | L77-L142, L160-L247 | pad/fork/tab heterogeneous branch set |
| S16 | Slot C | `fork_plate_yoke_tooling_set` | rec_branching_tree_with_three_independent_rotary_branches_5587a586efc940938efbddd243355ec3 | L146-L195, L213-L283 | fork, plate and yoke branch geometries |
| S17 | Slot C | `metrology_pad_rect_fork_set` | rec_branching_tree_with_three_independent_rotary_branches_e5ea9cde1c164220bf1da2acaede1ae4 | L68-L81, L149-L236 | journal roots plus round/rect/fork terminal set |
| S18 | Slot C | `underslung_blade_arms` | rec_branching_tree_with_three_independent_rotary_branches_89dd7d2b7e484fb0959e46d7f73e2505 | L107-L138, L163-L190 | underslung profiled/blade arm family |
