# Folding Arm Chain Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_arm_chain` |
| template path | `agent/templates/folding_arm_chain.py` |
| test path | `tests/agent/test_folding_arm_chain_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 40 |
| read_count | 40 |
| read_scope | all 5-star samples in `data` for category `folding_arm_chain` |
| category_metadata | `data/categories/folding_arm_chain/category.json` |
| source_index_policy | only adopted module sources are indexed below |

已完整读取该类别全部 40 个 5 星样本的 `model.py`、`revision.json`、`record.json`、`prompt.txt` 和 dataset/category metadata。采用为模块来源的样本覆盖平面扁平连杆、Y 轴 clevis 折叠链、悬挂式 bracket、bridge mount、hatch-support side plates、low-profile root plate、4 段 flat-bar chain、hook tab、triangular shoe 和 heavy end bracket。未采用的 5 星样本多为同一拓扑的尺寸、颜色或装饰密度重复，不写入 source table。

## 核心身份

`folding_arm_chain` 是接地或壁/桥式安装件承载的一串刚性连杆，连杆通过多个真实 revolute hinge 串联折叠。类别身份来自：固定 root support、2-5 段可折叠 rigid link、每个 joint 有可见 pin / boss / clevis / bushing 支撑、末端有小型 service plate / end pad / shoe / hook / end bracket。成熟域应保持“机械折叠链 / stay / deployable linkage”，不是通用 robot arm、不是 telescoping boom、不是 multisegment industrial manipulator，也不是 task lamp 或 monitor mount。

两大主轴都在 5 星样本中反复出现：

- `z_planar_stack`：XY 平面内的扁平 plate/bar 绕 Z 轴折叠，常见于 compact service arm、flat-bar deployable linkage、low-profile support plate。
- `y_clevis_stack`：X/Z 或悬挂结构中的 fork / clevis / side-plate 铰链绕 Y 轴折叠，常见于 hatch support、bridge-mounted stay、underslung bracket 和 side cheek linkage。

默认模板 seed domain 可以覆盖两大轴系，但必须通过 compatibility matrix 保证 root support、link profile、terminal module 与 axis family 一致。

## 槽位 + 候选模块表

### Slot A：`root_support`

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `compact_service_plate` | `rec_folding_arm_chain_0001` | `data/records/rec_folding_arm_chain_0001/revisions/rev_000001/model.py:L71-L90,L140-L149` | eligible if compatible | CadQuery compact base plate with circular pivot pad and slots; Z-axis planar root joint. |
| `four_bolt_flat_foot` | `rec_folding_arm_chain_0002` | `data/records/rec_folding_arm_chain_0002/revisions/rev_000001/model.py:L37-L49,L121-L131` | eligible if compatible | Foot + neck + boss plate with four bolt holes and central hinge hole; Z-axis flat-bar chain root. |
| `bridge_hanger_clevis` | `rec_folding_arm_chain_045dcc4f03e44d17baab376939e9f86c` | `data/records/rec_folding_arm_chain_045dcc4f03e44d17baab376939e9f86c/revisions/rev_000001/model.py:L108-L129,L229-L299` | eligible if compatible | Two separated bridge feet, uprights, crossmember, hanger, root tie bar, twin root cheeks, visible bolts; Y-axis suspended clevis. |
| `underslung_top_bracket` | `rec_folding_arm_chain_17826d7ae9e74ae4b415c0693b38bce6` | `data/records/rec_folding_arm_chain_17826d7ae9e74ae4b415c0693b38bce6/revisions/rev_000001/model.py:L54-L96,L126-L131` | eligible if compatible | Top mounting plate with lower clevis cheeks and hinge pin, chain hangs below the bracket; Y-axis under-slung support. |
| `hatch_base_lug` | `rec_folding_arm_chain_28e49b79c26b4e2ca76c7c60207feb45` | `data/records/rec_folding_arm_chain_28e49b79c26b4e2ca76c7c60207feb45/revisions/rev_000001/model.py:L77-L124` | eligible if compatible | Broad mounting foot, two upright clevis cheeks, clevis bridge, lower stop tab, pin and foot bolts; Y-axis hatch stay root. |
| `low_profile_root_plate` | `rec_folding_arm_chain_dca8b6f3a84d4debb0612482dd6ea629` | `data/records/rec_folding_arm_chain_dca8b6f3a84d4debb0612482dd6ea629/revisions/rev_000001/model.py:L85-L127` | eligible if compatible | Rounded rectangular mesh plate with screw holes, root boss and vertical pin; low-profile Z-axis stack. |

### Slot B：`chain_multiplicity`

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `two_link_service_chain` | `rec_folding_arm_chain_0001` | `data/records/rec_folding_arm_chain_0001/revisions/rev_000001/model.py:L151-L224` | eligible if compatible | Two arm parts plus moving service plate; 3 serial revolute joints; compact service-arm domain. |
| `three_link_stay_chain` | `rec_folding_arm_chain_2ec0062097f349ebb312519b42559372` | `data/records/rec_folding_arm_chain_2ec0062097f349ebb312519b42559372/revisions/rev_000001/model.py:L201-L303` | eligible if compatible | Three links in series with bracket-to-link, link-to-link, link-to-terminal revolute joints about Y. |
| `four_flat_bar_chain` | `rec_folding_arm_chain_0002` | `data/records/rec_folding_arm_chain_0002/revisions/rev_000001/model.py:L133-L189` | eligible if compatible | Four alternating flat-bar arms in a deployable Z-axis stack; tool plate attaches at distal end. |
| `four_link_end_bracket_chain` | `rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b` | `data/records/rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b/revisions/rev_000001/model.py:L214-L351` | eligible if compatible | Four detailed twin-strap links with end bracket; 5 moving bodies and 5 serial revolute joints. |
| `five_link_slot_stack_chain` | `rec_folding_arm_chain_225376f32756481eb1f430e8144b8d3a` | `data/records/rec_folding_arm_chain_225376f32756481eb1f430e8144b8d3a/revisions/rev_000001/model.py:L17-L36,L62-L109` | eligible if compatible | Five CadQuery `slot2D` flat links copied in series, Z-axis revolute chain, washers and pins at every distal joint. |

### Slot C：`link_profile`

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `slotted_flat_bar` | `rec_folding_arm_chain_0002` | `data/records/rec_folding_arm_chain_0002/revisions/rev_000001/model.py:L52-L77,L91-L111` | eligible if compatible | CadQuery eyelet flat bar with elongated central slot and two hinge holes. |
| `forked_bar_link` | `rec_folding_arm_chain_2ec0062097f349ebb312519b42559372` | `data/records/rec_folding_arm_chain_2ec0062097f349ebb312519b42559372/revisions/rev_000001/model.py:L88-L112,L201-L278` | eligible if compatible | Box bar with cylindrical proximal eye, distal fork cheeks, end caps and visible forked interface. |
| `tapered_bridge_link` | `rec_folding_arm_chain_045dcc4f03e44d17baab376939e9f86c` | `data/records/rec_folding_arm_chain_045dcc4f03e44d17baab376939e9f86c/revisions/rev_000001/model.py:L132-L183,L301-L447` | eligible if compatible | CadQuery lofted/tapered beam from proximal ring to distal clevis, tapering section toward terminal pad. |
| `rounded_side_plate_link` | `rec_folding_arm_chain_28e49b79c26b4e2ca76c7c60207feb45` | `data/records/rec_folding_arm_chain_28e49b79c26b4e2ca76c7c60207feb45/revisions/rev_000001/model.py:L43-L57,L125-L287` | eligible if compatible | `ExtrudeWithHolesGeometry` rounded side plates, dual side plates, bushings, spacers, stop tabs and formed fork bridge. |
| `boxed_distal_yoke` | `rec_folding_arm_chain_4b011def6fa74b85a89c188d8d91192d` | `data/records/rec_folding_arm_chain_4b011def6fa74b85a89c188d8d91192d/revisions/rev_000001/model.py:L60-L89,L128-L147` | eligible if compatible | CadQuery boxed body with distal yoke cheeks and cylindrical hub holes; Y-axis scissor-like boxed link. |
| `twin_strap_inspection_link` | `rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b` | `data/records/rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b/revisions/rev_000001/model.py:L39-L148,L214-L264` | eligible if compatible | Paired pierced straps, access covers, ribs, bushing cylinders and mechanical stop blocks; heavy detailed 4-link chain. |

### Slot D：`terminal_module`

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `service_plate` | `rec_folding_arm_chain_0001` | `data/records/rec_folding_arm_chain_0001/revisions/rev_000001/model.py:L115-L130,L181-L190` | eligible if compatible | Moving compact service plate with circular pivot neck, rectangular work plate and elongated slot. |
| `tool_plate` | `rec_folding_arm_chain_0002` | `data/records/rec_folding_arm_chain_0002/revisions/rev_000001/model.py:L80-L88,L138-L151` | eligible if compatible | Tool plate with lug, plate, nose, pivot hole, slot and two bolt holes. |
| `integral_end_pad` | `rec_folding_arm_chain_dca8b6f3a84d4debb0612482dd6ea629` | `data/records/rec_folding_arm_chain_dca8b6f3a84d4debb0612482dd6ea629/revisions/rev_000001/model.py:L190-L218` | eligible if compatible | Compact pad carrier mesh plus rubber pad; low-profile terminal pad. |
| `triangular_end_shoe` | `rec_folding_arm_chain_47dcc5a3a7744892bc71a732c9766dff` | `data/records/rec_folding_arm_chain_47dcc5a3a7744892bc71a732c9766dff/revisions/rev_000001/model.py:L149-L167,L210-L265` | eligible if compatible | Polygonal triangular shoe with small through holes; source attaches by fixed distal connection. |
| `hook_tab` | `rec_folding_arm_chain_86d7e2458f4f44a7afda852c89996b8c` | `data/records/rec_folding_arm_chain_86d7e2458f4f44a7afda852c89996b8c/revisions/rev_000001/model.py:L122-L140,L171-L176` | eligible if compatible | Terminal bar with upright, top nose, lower shelf, front lip and gusset hook. |
| `heavy_end_bracket` | `rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b` | `data/records/rec_folding_arm_chain_87de655f8d354acd8e5a329908c7410b/revisions/rev_000001/model.py:L266-L310` | eligible if compatible | Twin fork rails, end bearings, mounting blade, cross stop and access cover with screws. |

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A root_support]
  -- REVOLUTE root hinge at visible clevis / boss / root pin -->
[Slot B chain_multiplicity]
  -- repeats Slot C link_profile as link_0..link_{N-1} with serial REVOLUTE joints -->
[Slot D terminal_module]
```

Primary assembly is a serial revolute chain. `chain_multiplicity` chooses the number and joint policy; `link_profile` supplies the reusable link body / hinge interface for each copied link. `terminal_module` either attaches as a final moving revolute child or is fused as distal geometry on the last link when the source terminal is fixed/non-articulating.

接口点位和 axis families:

- `z_planar_stack`: root and links expose `positive_x` / distal hinge at `(link_length, 0, stack_z)` and rotate about `(0,0,1)`; compatible with `compact_service_plate`, `four_bolt_flat_foot`, `low_profile_root_plate`, `slotted_flat_bar`, `twin_strap_inspection_link`, `service_plate`, `tool_plate`, `integral_end_pad`, `triangular_end_shoe`, `heavy_end_bracket`.
- `y_clevis_stack`: root clevis and link distal fork expose coaxial Y hinge through visible cheeks / barrels; joints rotate about `(0,1,0)` or `(0,-1,0)`; compatible with `bridge_hanger_clevis`, `underslung_top_bracket`, `hatch_base_lug`, `forked_bar_link`, `tapered_bridge_link`, `rounded_side_plate_link`, `boxed_distal_yoke`, `integral_end_pad`, `hook_tab`.
- Cross-slot MatingContract plan: every revolute joint must pin parent visible socket face / bearing face to child proximal eye / tongue face. Captured pins and bushings may use element-scoped `allow_overlap` only for named pin/bearing pairs.
- Fixed source terminals such as `triangular_end_shoe` are source evidence for shape; implementation should fuse fixed shoe geometry into the terminal link or justify a real separate terminal if it articulates. Do not emit a separate nonmoving fixed part only for decoration.

## 每槽位 Module Emits / Interfaces

### Slot A / root support modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | One grounded root part: `root_support` / source-specific `base`, `bridge_support`, `support_bracket`, `base_lug`, or `root_plate`. | root source rows above |
| visuals | Mounting plate/foot/bracket, visible clevis cheeks or boss, pins, bolts/screws where present. | `root_support` source rows |
| internal joints | None, unless future reviewed source adds a moving clamp screw; current default root modules are fixed grounded parts. | source rows |
| upstream interface | Ground contact / wall/bridge mounting plane. | source rows |
| downstream interface | Root hinge axis and visible socket: `root_hinge_axis`, root clevis cheek faces or root boss top face. Consumer joint is REVOLUTE. | source rows |

### Slot B / chain multiplicity modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | `link_0..link_{N-1}` plus optional moving terminal child when source topology uses it. | `two_link_service_chain`, `three_link_stay_chain`, `four_flat_bar_chain`, `four_link_end_bracket_chain` |
| internal joints | Serial revolute joints from root to first link and between adjacent links; optional distal terminal joint. | source rows |
| upstream interface | First link proximal eye / tongue / bushing centered at root hinge origin. | source rows |
| downstream interface | Last link distal hinge or terminal anchor at `(last_length, 0, 0)` in last-link frame. | source rows |

### Slot C / link profile modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | Repeated moving link bodies using the selected profile; helper must preserve source primitive class (`mesh_from_cadquery`, `ExtrudeWithHolesGeometry`, Box/Cylinder detail stacks). | link source rows |
| internal joints | None inside a link part; all link-to-link articulations are emitted by chain assembly. | source rows |
| upstream interface | Proximal eye / tongue / bushing visual at local hinge origin. | link source rows |
| downstream interface | Distal eye / fork / clevis / yoke face and hinge axis. | link source rows |

### Slot D / terminal modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | Moving terminal part when terminal has a real revolute relationship; otherwise terminal visual fused onto last link. | terminal source rows |
| internal joints | Optional terminal REVOLUTE for service/tool/end bracket sources; fixed-source shoe/pad should be fused unless reviewer requests separate part with real support. | terminal source rows |
| upstream interface | Proximal hinge eye / lug or last-link distal face. | terminal source rows |
| downstream interface | End-use face: service plate top, tool plate bolt face, rubber pad face, hook lip, shoe face, end bracket mounting blade. | terminal source rows |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `root_support` | enum | 6 modules in Slot A | sampled | Determines axis family and root hinge origin | Slot A |
| `chain_multiplicity` | enum / count | `two_link_service_chain`, `three_link_stay_chain`, `four_flat_bar_chain`, `four_link_end_bracket_chain`, `five_link_slot_stack_chain`; derived `link_count` 2-5 | sampled | Determines part count, joint count and terminal policy | Slot B |
| `link_profile` | enum | 6 modules in Slot C | sampled | Must match axis family and chain count | Slot C |
| `terminal_module` | enum | 6 modules in Slot D | sampled | Must match axis family and terminal joint policy | Slot D |
| `axis_family` | enum | `z_planar_stack`, `y_clevis_stack` | derived | Derived from root/link compatibility, not independently sampled if incompatible | all sources |
| `link_count` | int | 2, 3, 4, 5 | derived from `chain_multiplicity` | copied link count | Slot B |
| `link_lengths` | tuple[float] | approx `[0.10, 0.55]` per link | sampled/clamped | Derived from reach scale, count and source profile proportions | link sources |
| `link_width_scale` | float | `[0.75, 1.25]` | 1.0 | Scales plate width/clevis gap with clamp to avoid hinge gaps | link sources |
| `plate_thickness_scale` | float | `[0.80, 1.20]` | 1.0 | Scales plate thickness while preserving pin overlap | link sources |
| `hinge_radius_scale` | float | `[0.85, 1.15]` | 1.0 | Pin/bushing radius; derived contact and overlap allowances | all hinge sources |
| `stack_offset_scale` | float | `[0.75, 1.25]` | 1.0 | Z-axis stack separation or Y-axis cheek gap | planar/clevis sources |
| `joint_limit_scale` | float | `[0.75, 1.20]` | 1.0 | Multiplies source motion limits with compatibility clamps | joint source rows |
| `terminal_size_scale` | float | `[0.80, 1.25]` | 1.0 | Service plate / pad / hook / bracket dimensions | Slot D |

## Multiplicity / Copy Logic

- `count_param`: `link_count`.
- `N_range`: 2-5 moving links.
- sampling domain:
  - `two_link_service_chain` -> `link_count=2`, terminal usually moving service plate (`3` revolute joints total).
  - `three_link_stay_chain` -> `link_count=3`, classic support stay (`3` revolute joints, terminal may be integrated).
  - `four_flat_bar_chain` -> `link_count=4`, flat deployable chain (`4` revolute link joints + optional terminal).
  - `four_link_end_bracket_chain` -> `link_count=4`, heavy twin-strap chain with end bracket (`5` serial revolute joints in source).
  - `five_link_slot_stack_chain` -> `link_count=5`, CadQuery slot-link Z-stack (`5` serial revolute link joints; terminal is fused to the final link to preserve the count identity).
- copied object: selected Slot C `link_profile` produces `link_0..link_{N-1}`.
- naming: `link_0`, `link_1`, ... plus `terminal` or source-style `service_plate`, `tool_plate`, `end_bracket` if emitted as a part.
- placement:
  - For `z_planar_stack`, each child origin is at the predecessor distal hinge, with safe `stack_z` offsets derived from source `STACK_OFFSET` / layer constants.
  - For `y_clevis_stack`, each child origin is at the predecessor distal clevis center; cheek gap and pin span clamp from source fork dimensions.
- joint policy:
  - Adjacent link joints are REVOLUTE.
  - Axis is derived by axis family.
  - Terminal modules with real articulation emit a final REVOLUTE. Fixed terminal shapes are fused into last link visuals unless reviewer explicitly approves a separate supported terminal part.
- source/gating: Slot B source rows define legal counts; compatibility matrix below restricts count/profile/root/terminal combinations.

## 拓扑多样性审计

总组合数 before compatibility gating：6 root supports × 4 chain multiplicities × 6 link profiles × 6 terminals = 864.


理由：即使 gate 分成两个 axis families，`z_planar_stack` 和 `y_clevis_stack` 各自都有多种 root/profile/terminal/count 组合。实现阶段只需采样稳定子域即可轻松超过 10 个 distinct slot choice tuples。

seed_domain_policy：procedural_first.

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 应使用 deterministic RNG。推荐顺序：先采样 `axis_family`，再采样兼容的 `root_support`，再采样 `chain_multiplicity`，再按 axis/count gate 采样 `link_profile` 和 `terminal_module`，最后采样受控连续 scale。`seed=0` 不特殊。初始 sweep 使用 seeds 0-49；成熟审计使用 0-999 检查 topology distinct、support、collision、joint origin 和 MatingContract。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；当前合法空间预计高于 300，除非实现阶段因复杂 mesh 或 MatingContract 收窄 seed domain，否则应达到建议线。

Regression overrides：none in SPEC_ONLY. 若实现阶段出现稳定失败 cluster，只允许少量 seed/config override，并写明失败回归原因；不得用 fixed modulo table 作为主 sampling 逻辑。

Controlled local parameterization：初版模板应包含 `link_reach_scale`、`link_width_scale`、`plate_thickness_scale`、`hinge_radius_scale`、`stack_offset_scale`、`terminal_size_scale`、`joint_limit_scale`。这些参数必须在 `resolve_config` 中 clamp；不得改变 `link_count`、axis family、part topology 或 terminal joint policy。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | axis-first conditional sampling, then root/count/profile/terminal choices | `slot_choices_for_seed` exactly matches built modules |
| compatibility matrix | reject incompatible root/profile/terminal/axis combos before build | no floating root, no impossible pin/clevis mating, no terminal gap |
| controlled local variation | clamp reach/width/thickness/hinge/stack/terminal scales | proportions vary without breaking contact, clearance or category identity |
| regression overrides | none initially | only reviewer-selected or failure-regression seeds |
| random sweep | 0-49 initial, 0-999 maturity | pass compiler baseline and |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| `root_support` | 6 | yes | yes | Two axis families represented |
| `chain_multiplicity` | 5 | yes | yes | Encodes link count and serial joint count |
| `link_profile` | 6 | yes | yes | Includes cadquery and `mesh_from_geometry` source complexity |
| `terminal_module` | 6 | yes | yes | Fixed-source terminals need Rule 1 adaptation |

### Compatibility Matrix / Gating

| axis_family | compatible root_support | compatible link_profile | compatible chain_multiplicity | compatible terminal_module | notes |
|---|---|---|---|---|---|
| `z_planar_stack` | `compact_service_plate`, `four_bolt_flat_foot`, `low_profile_root_plate` | `slotted_flat_bar`, `twin_strap_inspection_link`; `five_link_slot_stack_chain` forces `slotted_flat_bar` | `two_link_service_chain`, `four_flat_bar_chain`, `four_link_end_bracket_chain`, `five_link_slot_stack_chain`; `three_link_stay_chain` only with low-profile adaptation | `service_plate`, `tool_plate`, `integral_end_pad`, `triangular_end_shoe`, `heavy_end_bracket`; five-link source fuses terminal geometry | Preserve Z-axis stack offsets; avoid Y-clevis profiles. |
| `y_clevis_stack` | `bridge_hanger_clevis`, `underslung_top_bracket`, `hatch_base_lug` | `forked_bar_link`, `tapered_bridge_link`, `rounded_side_plate_link`, `boxed_distal_yoke` | `three_link_stay_chain`; `two_link_service_chain` only if terminal adapts to Y axis | `integral_end_pad`, `hook_tab`, `service_plate` if it becomes Y-axis service pad | Preserve visible fork/cheek mating and Y-axis pin span. |
| `heavy_twin_strap` | `low_profile_root_plate` or dedicated broad frame from `four_link_end_bracket_chain` | `twin_strap_inspection_link` | `four_link_end_bracket_chain` | `heavy_end_bracket` | Bulky but high-detail; keep as gated stable subdomain. |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for `root_support`, `chain_multiplicity`, `link_profile`, `terminal_module`, and derived `axis_family`.
- `config_from_seed(seed)` uses deterministic procedural sampling for ordinary seeds; `seed=0` is not special.
- Compatibility matrix prevents illegal root/profile/terminal/axis combinations before geometry is built.
- Every revolute joint has a visible parent clevis/boss/socket and child proximal eye/tongue/bushing.
- Every separate moving child joint has a MatingContract tying named parent and child mating faces.
- Captured pin/bushing overlap is declared element-scoped, not broad part-level unless unavoidable and justified.
- Non-moving terminal details from fixed-source samples are fused into parent visuals unless there is a real joint/support reason.
- Primitive complexity is preserved: `mesh_from_cadquery` and `ExtrudeWithHolesGeometry` source modules cannot be replaced by crude single Box/Cylinder placeholders.
- `link_count` controls actual part and joint count; naming is stable (`link_i`, terminal name).
- Controlled local scale params are clamped and cannot break interface contact, clearance, joint origins, or count/multiplicity.

## Reject cases

- Fewer than two moving links, or no serial revolute chain.
- A generic industrial robot arm with shoulder/elbow/wrist tooling but no folding plate/bar chain identity.
- Telescoping/prismatic-only boom with no serial hinge chain.
- Floating terminal pad, tool plate, hook, or end bracket not supported by visible link geometry.
- Fixed decorative parts emitted as separate parts without articulation or real reason.
- Pin/boss visuals far from joint origins, or joint axes not passing through visible hinge hardware.
- Mixing `z_planar_stack` root with Y-axis clevis link profile, or Y-axis bridge/hatch root with Z-stack flat bars.
- Source-derived cadquery/mesh plate modules reduced to plain boxes in implementation.
- Small curated/modulo seed table used as the primary sampling domain.

## 与相邻类别的边界

- 不该混入：`multisegment_foldout_arm`。后者是 industrial multi-segment boom/manipulator, can have broader base/end tooling; `folding_arm_chain` is a plate/bar stay/linkage with compact hinge hardware.
- 不该混入：`articulated_task_lamp`。Task lamp must include lamp head/light identity; this category is bare mechanical linkage/stay.
- 不该混入：`monitor_mount`。Monitor mount includes screen/VESA/end display support; folding arm chain has service plate/pad/shoe/hook only.
- 不该混入：`telescoping_boom`。Telescoping boom uses prismatic nested stages, not serial hinge plates.
- 不该混入：`robotic_arms` / `shoulderelbowwrist_arm`。Those are robot manipulators with wrist/tool semantics, not compact folding stays.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft generated from 40 five-star samples; waiting for human review before template implementation. |

## 模板实现备注（可选）

- The likely implementation graph is not a pure `_modular.py` auto-chain because `chain_multiplicity` and `link_profile` interact; a slug-specific assembler may be clearer while still exposing stable slot choices and InterfaceSpec/MatingContract data.
- Preserve source primitive types for each candidate: `mesh_from_cadquery` for CadQuery sources, `mesh_from_geometry(ExtrudeWithHolesGeometry)` for rounded plates, and Box/Cylinder detail stacks where the source uses explicit visuals.
- For z-axis planar stacks, derive `stack_z`/layer offsets from the selected chain multiplicity and plate thickness. Closed pose must not collapse all plates into a single plane.
- For y-axis clevis stacks, derive `cheek_gap`, `pin_span`, and `bushing_radius` from the selected root/profile pair. Parent clevis and child tongue should visibly interleave.
- Terminal modules with source FIXED joints, especially `triangular_end_shoe`, should be implemented as part of the last moving link unless reviewer approves a separate supported terminal articulation.
- Expected intentional overlaps: pin through bushing, bushing in eye, fork cheek around tongue. Declare these with named element pairs.
