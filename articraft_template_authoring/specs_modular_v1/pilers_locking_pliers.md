# pilers_locking_pliers — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_locking_pliers` |
| template path | `agent/templates/pilers_locking_pliers.py` |
| test path (optional) | `tests/agent/test_pilers_locking_pliers_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (fixed 7-part parallel/serial skeleton; slots swap part geometry, not topology) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 origin_anchor + 8 single-axis forks) |
| source_index_policy | only adopted module sources are indexed below |

关键观察：全部 9 个样本共享**同一条 7-part / 6-joint 过中心（over-center）肘节锁死骨架**——
没有任何 fork 增删 part 或 joint。骨架恒为：`jaw_frame`(root) + `movable_jaw` + `upper_handle` +
`lower_handle` + `locking_link` + `release_lever` + `adjustment_screw`；joint 恒为
`jaw_pivot`/`upper_handle_pivot`/`lower_handle_pivot`/`linkage_pivot`/`release_lever_pivot`
(5× REVOLUTE, axis +Z) + `adjustment_travel` (PRISMATIC, axis −Y)。fork 之间的真实差异全部落在
**特定 part 的可识别几何形态原型**（③ 主体形态家族 / 机构形态）与个别关节的**轴符号/行程**（②/⑤）上，
而非骨架图（①）。因此本类别是"固定骨架上的形态主导类"：主多样性来自 ③ jaw_form 形态族 + 三个次级机构形态槽。
所有 pivot 均为 pin-through-plate 的 captured pin（穿销），按 AUTHORING Rule 2 grandfathering 省略
`mating=`，用 element-scoped `allow_overlap` + `expect_contact` 表达捕获接触（与已通过的 sibling
`pilers_slip_joint_pliers` 相同套路）。

## 核心身份

Locking pliers（大力钳 / Vise-Grip 式锁定钳）：一把带**过中心肘节锁死机构**的手动夹钳。
握把闭合后 `locking_link` 越过死点把 `movable_jaw` 锁在闭合位；`release_lever` 手动越回死点解锁；
尾部 `adjustment_screw` 顶在 `lower_handle` 尾端，螺纹进给改变闭合钳口开度（夹持力预设）。
默认成熟域 = 银色锻钢钳身、锯齿钳口、黑色/彩色调节旋钮与解锁片。

**不该混入**：普通 slip-joint pliers（滑动支点、无锁死肘节、无解锁片，见 §11）；台钳 bench vise
（固定基座、丝杠主进给、无握把肘节）。must_keep：过中心锁、可调钳口、手动解锁、可见支点接口、
≥1 个真实非-FIXED 关节。

## 槽位 + 候选模块表

### Slot A：jaw_form（③ 主体形态家族 / Primary Form Family —— 登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| curved_jaw | forked_anchor | `rec_0611_pilers_locking_pliers_var_jaw_form_curved_jaw` | `_fixed_jaw_profile` L76-113 / `_movable_jaw_profile` L116-151；jaw_pivot L473-486 | Planar Boundary Form | eligible if compatible | 对置凹弧锯齿钳口（12 齿）；ExtrudeGeometry 平板轮廓 |
| long_nose_jaw | forked_anchor | `rec_0611_pilers_locking_pliers_var_jaw_form_long_nose_jaw` | `_fixed_jaw_profile` L76-102 / `_movable_jaw_profile` L105-132；jaw_pivot L452-465 | Planar Boundary Form | eligible if compatible | 细长渐缩尖嘴，单条长直锯齿边（17/16 齿） |
| c_clamp_jaw | forked_anchor | `rec_0611_pilers_locking_pliers_var_jaw_form_c_clamp_jaw` | `_fixed_jaw_profile` L76-107 / `_movable_jaw_profile` L110-133；jaw_pivot L461-474 | Planar Boundary Form | eligible if compatible | 深喉 C 形固定框（throat_depth≈0.090）+ 短摆臂动钳；钳口面法向朝 −Y |
| sheet_metal_wide_jaw | forked_anchor | `rec_0611_pilers_locking_pliers_var_jaw_form_sheet_metal_wide_jaw` | `_fixed_wide_grip_profile` L133-148 / `_movable_wide_grip_profile` L151-172；`WIDE_JAW_WIDTH` L24；jaw_pivot L514-527 | Volumetric Envelope Form | eligible if compatible | 成形钣金宽夹面（挤出宽度 0.032，远宽于 PLATE_THICKNESS 0.006），在基础曲钳上叠加 wide-face 视觉 |

### Slot B：locking_mechanism（② 联动耦合 / ③ 肘节形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| classic_toggle_link | forked_anchor | `rec_0611_pilers_locking_pliers_var_locking_mechanism_classic_toggle_link` | `_locking_link_profile` L173-192；toggle_pivot_eye L382-387 + toggle_bearing_pad L388-393 + 17-coil spring L394-415；linkage_pivot L516-529 | eligible if compatible | 长曲狗骨肘节板 + 承压轴承端 + 长螺旋弹簧；`over_center_lock=True` |
| compound_jaw_linkage | forked_anchor | `rec_0611_pilers_locking_pliers_var_locking_mechanism_compound_jaw_linkage` | compound_link_seat L277-282（jaw_frame）+ compound_link_rivet L311-316（movable_jaw）；jaw_pivot meta L468-485 | eligible if compatible | 在锁定链外增加偏置摇臂耦合销（forged_fork_cheek 座 + rocker 尾），把动钳做成复合联动；locking_link 本体沿用基础轮廓 L173-189 |

### Slot C：release（② 解锁片轴向 / ③ 凸轮片形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| captured_thumb_lever | forked_anchor(origin baseline) | `rec_picturex_0611__pilers_locking_pliers__001__png_a9bb7cc245c841b4babcc31cfc106f12` | `_release_lever_profile` L186-199 + release_thumb_pad L402-407；release_lever_pivot L502-515 (axis +Z, lower −0.12 upper 0.34) | eligible if compatible | 细长解锁片 + 小拇指垫，捕获在 lower_handle 铆销上 |
| one_hand_push_release | forked_anchor | `rec_0611_pilers_locking_pliers_var_release_one_hand_push_release` | `_release_lever_profile` L186-203 + 放大 release_thumb_pad(r=0.010) L411-416 + 加厚 plate L402-410 + release_pivot_pin(r=0.0027) L351-356；release_lever_pivot L511-524 (axis **(0,0,−1)** 翻转, lower 0.0 upper 0.32) | eligible if compatible | 冲压凸轮鼻 + 宽掌推压片，单手向 lower_handle 推压解锁；解锁轴符号翻转 |

### Slot D：adjustment（③ 调节器形态 / ⑤ 进给行程）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| captured_knurled_screw | forked_anchor(origin baseline) | `rec_picturex_0611__pilers_locking_pliers__001__png_a9bb7cc245c841b4babcc31cfc106f12` | adjustment_screw L409-444（shaft len 0.036 + KnobGeometry(0.014,0.013,count=28)）；upper_handle Box adjustment_socket L315-320；adjustment_travel L516-529 (upper 0.006) | eligible if compatible | 短滚花螺杆 + Box 尾插槽，标准锁定钳尾部调节 |
| quick_adjust_thumbwheel | forked_anchor | `rec_0611_pilers_locking_pliers_var_adjustment_quick_adjust_thumbwheel` | adjustment_screw L422-455（shaft len 0.044 + thumbwheel_collar L428-433 + KnobGeometry(0.022,0.010,count=36)）；upper_handle Cylinder adjustment_socket L315-323；adjustment_travel L527-540 (upper 0.010) | eligible if compatible | 加宽免工具拇指轮 + 环形项圈 + Cylinder 尾套，行程延长；`tool_free=True` |

硬约束满足：每个 slot ≥2 candidate；jaw_form 4 个（③ 主体形态家族，≥3 达标）；无单候选 slot；每个
candidate 均有 `forked_anchor` record_id + 真实 `model.py:Lx-Ly`。captured_thumb_lever /
captured_knurled_screw 采用 origin_anchor 作为该轴基线（原始资产内实存的形态），非世界知识杜撰。

## 槽位图（slot graph）

pattern: mixed（固定骨架；slot 只替换指定 part 的几何/meta，不改边的存在与关节类型）

```
jaw_frame(root)
 ├─[jaw_pivot REVOLUTE +Z, captured pin, lower≈-0.16 upper≈0.20]──> movable_jaw      (Slot A 形态 + Slot B 耦合销)
 ├─[upper_handle_pivot REVOLUTE +Z, captured pin]──────────────────> upper_handle
 │        └─[adjustment_travel PRISMATIC −Y, captured in socket]──> adjustment_screw (Slot D)
 └─[lower_handle_pivot REVOLUTE +Z, captured pin]──────────────────> lower_handle
          ├─[linkage_pivot REVOLUTE +Z, captured pin]──────────────> locking_link    (Slot B)
          └─[release_lever_pivot REVOLUTE ±Z, captured pin]────────> release_lever   (Slot C)
```

- 接口点位：所有跨-slot 连接均为 **captured pin（穿销）revolute/prismatic**，销轴在两 part 的实心
  visual 内穿过（`central_pivot_boss` / `*_rivet` / `link_pivot_pin` / `release_pivot_pin` /
  `adjustment_socket`）。几何无法表达为两个轴对齐面贴合 → 按 Rule 2 grandfather 省略 `mating=`，
  用 element-scoped `allow_overlap` + `expect_contact` 声明捕获接触。
- 关节类型/边的存在跨所有 candidate 恒定；仅 Slot C 翻转 release 轴符号（②），Slot D 延长 prismatic 行程（⑤）。
- 无互斥/可选 slot：4 个 slot 全程存在，各自独立采样（`4 × 2 × 2 × 2` 全合法）。

## 每槽位 Module Emits / Interfaces

### Slot A / jaw_form（jaw_frame + movable_jaw 几何）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `jaw_frame`(root, 固定钳口 + 各 pivot boss/rivet), `movable_jaw`(动钳 + central_pivot_rivet) | curved L232-294 / 各 jaw fork |
| internal joints | `jaw_pivot` REVOLUTE +Z（movable 绕固定钳口摆） | origin L446-459 |
| upstream interface | root（jaw_frame 是唯一 root，无上游） | origin L232 |
| downstream interface | 承载 upper/lower_handle pivot boss + movable_jaw pivot | origin L251-268 |

### Slot B / locking_mechanism（locking_link + 耦合销）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `locking_link`(肘节板 + spring)；compound 额外在 jaw_frame/movable_jaw 加 seat/rivet **视觉** | origin L354-387 / compound L277-316 |
| internal joints | `linkage_pivot` REVOLUTE +Z（locking_link 挂在 lower_handle 销） | origin L488-501 |
| upstream interface | lower_handle 的 `link_pivot_pin`（captured） | origin L341-346 |
| downstream interface | 肘节自由端顶在 upper_handle（过中心接触，allow_overlap 声明） | classic L388-393 |

### Slot C / release（release_lever 几何 + 轴符号）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `release_lever`(凸轮片 + thumb_pad) | origin L389-407 |
| internal joints | `release_lever_pivot` REVOLUTE ±Z（捕获在 release_pivot_pin） | origin L502-515 |
| upstream interface | lower_handle 的 `release_pivot_pin`（captured） | origin L347-352 |
| downstream interface | 无（自由端拇指垫） | — |

### Slot D / adjustment（adjustment_screw + upper_handle socket）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `adjustment_screw`(shaft + knob/thumbwheel)；upper_handle 上的 `adjustment_socket` visual | origin L409-444 / L315-320 |
| internal joints | `adjustment_travel` PRISMATIC −Y（螺杆在 socket 内轴向进给） | origin L516-529 |
| upstream interface | upper_handle 的 `adjustment_socket`（captured 插入） | origin L315-320 |
| downstream interface | 螺杆头顶 lower_handle 尾端（功能接触，非独立 part） | origin meta |

要求满足：所有活动件（movable_jaw / 两握把 / locking_link / release_lever / adjustment_screw）都有
articulation 语义；不动细节（rivet/boss/serration/socket）写成 parent visual，非独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_form | enum | curved_jaw / long_nose_jaw / c_clamp_jaw / sheet_metal_wide_jaw | — | choice | deterministic procedural sampler | Slot A |
| locking_mechanism | enum | classic_toggle_link / compound_jaw_linkage | — | choice | sampler | Slot B |
| release | enum | captured_thumb_lever / one_hand_push_release | — | choice | sampler | Slot C |
| adjustment | enum | captured_knurled_screw / quick_adjust_thumbwheel | — | choice | sampler | Slot D |
| palette_style | enum | 6 colorways（见 §8.5 ⑥） | polished_steel | choice | `rng.choice(PALETTE_STYLES)` | 5★ 材质 |
| jaw_scale | float | [0.90, 1.12] | 1.0 | independent | 钳口 profile 绕 jaw_pivot 等比缩放，clamp | origin L76-151 |
| handle_len_scale | float | [0.90, 1.12] | 1.0 | independent | 握把 profile y（长度）缩放，clamp | origin L131-170 |
| grip_girth_scale | float | [0.92, 1.10] | 1.0 | independent | 握把 profile x（握径）缩放，clamp | origin L131-170 |
| open_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 jaw/handle/linkage/release REVOLUTE 行程幅度，clamp 到安全带 | origin motion_limits |
| adjustment_upper | float | derived | — | equation | `= 0.006`(screw) / `0.010`(thumbwheel)，随 Slot D 定 | origin L516-529 / L527-540 |
| (—) | constraint | — | — | inequality | 缩放后 REVOLUTE 行程 clamp 到 [source_lower*0.7, source_upper*1.1]，防越界穿模；违反回缩 | Rule 5 |

连续尺寸采样契约：先独立采 jaw_scale/handle_len_scale/grip_girth_scale/open_scale → adjustment_upper
由 Slot D enum 派生 → 各 REVOLUTE 行程按 open_scale 缩放后 clamp 投影到安全带。所有 clamp/派生在
`resolve_config` 内完成。

### 7.5 编译预算 / compile budget

自报预算：**≤15s/seed**。依据：骨架含 ~6 个 `ExtrudeGeometry` 平板挤出（钳口/握把/肘节/解锁片，
每条 profile ≤32 点）、1 条 `tube_from_spline_points` 弹簧（radial_segments=10, ~15 段）、
1 个 `KnobGeometry` 滚花旋钮（count 28–36）。tessellation 分档：滚花 ≤36 段，弹簧 radial ≤10，
平板挤出无曲面细分。无重布尔雕刻（sheet_metal_wide 仅叠加 wide-face 挤出视觉，不做 cut）。
sweep `--compile-timeout 120` 作看门狗（≈8×预算），非质量线。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（7 part / 6 joint 恒定骨架）表达，不暴露任何 `*_count`，
  也不通过循环复制模板级 visual/part/joint。锯齿齿数（serration_count）是各 jaw candidate profile
  内的固定装饰细节（④，宿主面派生），不作为 multiplicity 轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 无 | 全部 9 个 5★ 样本共享同一 7-part/6-joint 过中心肘节骨架，无 fork 增删 part/joint。骨架结构内在单一——locking pliers 的身份即此固定肘节机构；形态多样性由 ③ 承载。 |
| └ multiplicity | 同构件 ×N | 无 | 无重复子件轴（见 §8）。 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有（轴符号） | release 槽：`captured_thumb_lever` 轴 +Z vs `one_hand_push_release` 轴 (0,0,−1) 翻转（forked_anchor: var_release_one_hand_push_release L511-524）。其余关节类型/轴跨所有 candidate 恒定（5× REVOLUTE +Z + 1× PRISMATIC −Y）。声明的两个 release 轴符号在 sweep 中各自出现。 |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何原型 | 有（登记 slot=jaw_form） | **jaw_form**（登记进 slot_choices）4 candidate：curved_jaw / long_nose_jaw / c_clamp_jaw = Planar Boundary Form；sheet_metal_wide_jaw = Volumetric Envelope Form；全 forked_anchor（见 Slot A 表）。**次级形态槽**：locking_mechanism（classic 长肘节 vs compound 偏置摇臂耦合 = 联动形态）、release（细长片 vs 宽推压凸轮片）、adjustment（短滚花螺杆 vs 加宽拇指轮）——均 forked_anchor，换机构 part 的可识别形态原型。 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | 锯齿钳口 serration（`_serrated_edge` 由钳口 profile 逐段派生，随 ③ 形态与 ⑤ 缩放共形）、frame_rivet/pivot_boss、滚花旋钮 knurl（KnobGrip helix）。source_type=record_only；装饰几何均写成宿主 part visual，由宿主最终 profile 派生（派生顺序 ③→⑤→④）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | jaw_scale [0.90,1.12]、handle_len_scale [0.90,1.12]、grip_girth_scale [0.92,1.10]、open_scale [0.85,1.15]（见 §7）。运动包络：jaw_pivot(+Z, 合↔开 [-0.16,0.20]×open_scale)、upper/lower_handle_pivot(+Z, [-0.10,0.24])、linkage_pivot(+Z, [-0.16,0.22] 过中心)、release_lever_pivot(±Z, [-0.12,0.34])、adjustment_travel(−Y prismatic, [0, 0.006/0.010])。motion_test_plan：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` 跑全部关节 min/max/mid + targeted `ctx.pose` 各验 movable_jaw 开合、locking_link 过中心、release 摆动、adjustment 轴向进给。captured-pin 重叠 element-scoped 豁免。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 6 colorways：polished_steel（裸银）、nickel_bright（亮铬）、black_oxide_red（黑体+红解锁/旋钮）、blue_dipped（钢+蓝握把浸塑）、gunmetal_yellow（枪灰+黄握把）、raw_forged_grey（暗锻灰）。材质大类：metal（钢/铬）+ painted（浸塑握把/彩色解锁旋钮）=2 类，覆盖 ≥ceil(0.5×2)=1（实覆盖 2）。source_type=record_only（origin 材质 polished/bright/dark_steel + black_oxide 扩展现实配色）。 |

收尾自检：batch 0-9 需肉眼看到 4 种钳口形态拉开、release 轴翻转导致解锁片摆向不同、adjustment 旋钮宽窄不同、
金属/浸塑配色都出现、锯齿贴合钳口面不悬空、全关节开合不穿模。

## 采样与覆盖审计

总组合数：jaw_form(4) × locking_mechanism(2) × release(2) × adjustment(2) = **32** slot 元组，
外加 palette(6) 与 4 个连续 scale。

理由：单 origin_anchor + 8 个单轴 fork 是本类别全部 5★ 源，锚点池上限决定离散组合空间为 32（report-only
的 1000-seed topology target 会 <300，属源锚点上限，合规——本指标不作 gate，也不反推上游变体数量）。
32 元组 + 连续 scale + 6 palette 足以覆盖成熟度观察。

seed_domain_policy：procedural_first（`config_from_seed` 对每个 ordinary seed 含 seed 0 用加权
`rng.choices` 独立采样 4 个 slot + palette + 连续 scale；无 curated/modulo 主表）。
Procedural Sampling / Sweep Plan：deterministic sampler 逐 slot 加权采（jaw_form 偏 curved；
其余 slot 偏 baseline），无非法组合（固定骨架，几何 swap 相互独立，compatibility 全通）。
无 regression overrides（除非 sweep 暴露具体失败 seed 再补，并注明理由）。
Topology target：32 元组 <300，源锚点上限，report-only。
Controlled local parameterization：jaw_scale / handle_len_scale / grip_girth_scale / open_scale
（§7 范围 + clamp），均 independent，`resolve_config` 内 clamp；REVOLUTE 行程按 open_scale 缩放后
inequality clamp 到安全带，不破坏 captured-pin 接口或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 slot 加权 choice + palette + 4 连续 scale；seed 0 不特殊 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全 32 组合合法（固定骨架，几何 swap 独立）；无互斥/fallback | 无 floating / collision / 轴错 / captured-pin 超界 |
| controlled local variation | jaw_scale/handle_len_scale/grip_girth_scale/open_scale + clamp | 比例变化不破 pivot 原点 / 行程 / 捕获接触 / 身份 |
| regression overrides | none | 仅在 sweep 暴露具体失败 seed 时补 |
| random sweep | seeds 0-35 首过；0-999 成熟度观察 | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| jaw_form | 4 | yes | yes | ③ 登记的 Primary Form Family slot |
| locking_mechanism | 2 | yes | no | 源锚点池仅 2 个 locking fork，达 ≥2 下限 |
| release | 2 | yes | no | origin baseline + 1 fork |
| adjustment | 2 | yes | no | origin baseline + 1 fork |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（4 slot 元组）
- config_from_seed 对所有 ordinary seed（含 0）用 deterministic procedural sampling
- compatibility：固定骨架下 32 组合全合法，无非法组合需 gating
- 无 regression overrides 长期轮换
- 连续 scale 均在 resolve_config clamp/派生，不破接口、行程、captured-pin 接触、类别 multiplicity
- 关键关节存在且类型/轴正确：5× REVOLUTE +Z（release 可 −Z）+ 1× PRISMATIC −Y
- captured pin 用 element-scoped allow_overlap + expect_contact，非 broad part-level
- 骨架恒 7 part / 6 joint，单 root=jaw_frame
- 每个非-FIXED 关节机构有 targeted ctx.pose 验证运动语义 + 全关节 sampled-pose 碰撞门

## Reject cases

- 任何 fork 增删 part/joint（本类别骨架恒定，拓扑变化即非法输入）
- jaw 形态 downgrade 到裸 Box/Cylinder（须保 ExtrudeGeometry 平板 profile，Rule 3）
- 锯齿/滚花装饰用常数尺寸套在缩放后钳口上（须宿主 profile 派生，Rule 4）
- REVOLUTE 行程放大到 movable_jaw 与 fixed jaw 穿模 / locking_link 越界撞握把
- captured pin 用 broad part-level allow_overlap 掩盖真实穿模
- release 轴符号搞错导致解锁片摆入 lower_handle 本体
- adjustment_screw 脱出 socket（prismatic 上界过大失去捕获接触）
- palette 只驱动部分 visual（须每个 `.visual(..., material=mats[...])` 都由 palette 解析）

## 与相邻类别的边界

- 不该混入：**普通 slip-joint pliers**（滑动多支点、无过中心锁死肘节、无解锁片、无尾部调节螺杆；
  见 sibling `pilers_slip_joint_pliers`——那是 slot_guide+slider 滑槽支点，本类别是固定 jaw_pivot + 肘节锁）
- 不该混入：**bench vise 台钳**（固定基座 + 丝杠主进给 + 无手握把肘节；本类别是手持双握把肘节锁钳）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 固定骨架形态主导类；③ 登记 slot=jaw_form(4)；locking/release/adjustment 为次级形态槽(各2)；captured-pin grandfather 套路同已过 sibling pilers_slip_joint_pliers。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | (skeleton) | 7-part over-center | rec_picturex_...a9bb7cc245 | L202-531 | 骨架 part/joint + captured-pin 接触 + 材质基线 |
| S_A1 | jaw_form | curved_jaw | var_jaw_form_curved_jaw | L76-151 | 钳口 profile |
| S_A2 | jaw_form | long_nose_jaw | var_jaw_form_long_nose_jaw | L76-132 | 细长尖嘴 profile |
| S_A3 | jaw_form | c_clamp_jaw | var_jaw_form_c_clamp_jaw | L76-133 | 深喉 C 框 profile |
| S_A4 | jaw_form | sheet_metal_wide_jaw | var_jaw_form_sheet_metal_wide_jaw | L24,L133-172 | 宽夹面挤出 |
| S_B1 | locking_mechanism | classic_toggle_link | var_locking_mechanism_classic_toggle_link | L173-192,L382-415 | 肘节板 + 弹簧 |
| S_B2 | locking_mechanism | compound_jaw_linkage | var_locking_mechanism_compound_jaw_linkage | L277-316 | 偏置摇臂耦合销 |
| S_C1 | release | captured_thumb_lever | rec_picturex_...a9bb7cc245 | L186-199,L502-515 | 基线解锁片 |
| S_C2 | release | one_hand_push_release | var_release_one_hand_push_release | L186-203,L511-524 | 宽推压凸轮片 + 轴翻转 |
| S_D1 | adjustment | captured_knurled_screw | rec_picturex_...a9bb7cc245 | L409-444,L516-529 | 基线滚花螺杆 |
| S_D2 | adjustment | quick_adjust_thumbwheel | var_adjustment_quick_adjust_thumbwheel | L315-323,L422-455 | 加宽拇指轮 + Cylinder 套 |
</content>
</invoke>
