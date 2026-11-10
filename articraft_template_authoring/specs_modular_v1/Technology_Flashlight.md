# Technology_Flashlight — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Flashlight` |
| template path | `agent/templates/Technology_Flashlight.py` |
| test path (optional) | `tests/agent/test_Technology_Flashlight_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern`：body 是 root（电池筒 + 灯头光学在不旋焦时为 body visual + 携带件），
head（旋焦时为独立 CONTINUOUS 子件）、switch（PRISMATIC 子件）都并联挂到 body。
crenellation 齿/肋是 head 上的 multiplicity（FIXED inline visual，无 per-copy joint）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 origins + 6 variants), model.py 全文逐行 |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：

- **origin A** `rec_a-yellow...5b5f681c`（黄色塑料手电，纯 SDK，头在 **-X**、尾在 **+X**、侧按钮在 **+Y**）：
  body 单 part 承载 `barrel_shell` Cylinder(L47-52)、`shoulder_shell` LatheGeometry.from_shell_profiles(L55-76)、
  `head_shell` Lathe 空心头壳(L79-102)、`front_bezel_ring`/`rear_bezel_band` Lathe 环(L105-133)、
  16 根 `head_rib_{i}` Cylinder 纵肋 `for i in range(16)`(L136-145)、4 根 `barrel_grip_{i}` 模压导轨(L148-156)、
  `tail_cap`+`tail_eyelet` TorusGeometry(L159-173)、`parabolic_reflector` Lathe 抛物锥(L176-199)、
  `led_bulb` Sphere(L200-205)、`lens_disc` Cylinder 透镜盘(L207-212)。
  `button` 独立 part（`button_base`+`button_cap` ExtrudeGeometry, L216-240）经 `body_to_button` **PRISMATIC** 径向内压(L267-275)。
  `strap` 独立 part（`strap_loop` tube_from_spline_points 闭合软环, L243-265）经 `body_to_strap` **FIXED** 挂尾眼(L276-282)。
- **origin B** `rec_black...baf8fda5`（黑色战术手电，cadquery，头在 **+X**、尾在 **-X**、侧按钮在 **+Z**）：
  `_body_solid` loft 阶梯铝筒(L59-72)、`_knurl_band` 菱形滚花 2×28 肋(L75-93)、
  `_bezel_mesh` 花齿攻击环 `for i in range(8)`(L96-120)、`_head_shell_mesh` 喇叭头挖锥腔(L123-147)、
  `_reflector_mesh` 深漏斗反射镜(L150-162)。**`focus_head` 独立 part**（head_shell+bezel_ring+reflector+led_emitter+bezel_marker, L206-228）
  经 `head_focus_twist` **CONTINUOUS** 绕 +X 轴旋焦(L230-238，无 mating,靠 allow_overlap 套 body lip)。
  `push_button` part 经 `button_press` **PRISMATIC** 压入 -Z(L241-255)，坐在 `button_boss` 平台上。
- **variant floodhead** `rec_flashlight_var_floodhead`（← origin A）：大直径浅碟反射镜 + 大平透镜，20 根肋(L138)，加 `reflector_retainer`/`led_mount`。
- **variant anglehead** `rec_flashlight_var_anglehead`（← origin A）：L 形直角头，头颈垂直筒身，光束 90° 出射（体量包络边界样本）。
- **variant tailswitch** `rec_flashlight_var_tailswitch`（← origin A）：`barrel_extension`(L157-164) + `tail_button` 独立 part(L215-230)经 `tail_press` **PRISMATIC** 轴 (-1,0,0) 前压(L260-267)。
- **variant slideswitch** `rec_flashlight_var_slideswitch`（← origin A）：`slide_track` body visual(L215-220) + `slider` part(L223-236)经 `body_to_slide` **PRISMATIC** 轴 (1,0,0) upper 0.008 沿筒滑(L263-269)。
- **variant pocketclip** `rec_flashlight_var_pocketclip`（← origin B）：`_pocket_clip_mesh` sweep_profile_along_spline 弹钢夹(L167-188) + `_clip_mount_solid` 卡箍(L191-205)，均为 body visual(L245-255)。
- **variant bezelN** `rec_flashlight_var_bezelN`（← origin B）：`_bezel_mesh` 花齿数 N 变化(L96-121)，证明 crenellation 是 `for i in range(N)` 真实复制轴。

## 核心身份

Flashlight = **单手持照明手电筒**：一根沿主轴的圆柱电池筒身（root），前端一个更宽的灯头
（抛物/漏斗反射镜 + 透明透镜 + LED 光源，光沿主轴出射），一个开关机构（侧按钮 / 旋焦头 /
尾帽点动 / 侧滑），可选携带件（腕带 / 口袋夹）。默认成熟域是手持尺度（长径比 ~4:1–7:1，
筒径 ~0.03–0.05m）。核心识别 = 「筒身 + 更宽发光头 + 反射镜/透镜可见 + 至少一个可动开关」。

不该混入：营地灯 / lantern（360° 漫射球泡、无定向反射镜、通常有提梁座）；头灯 headlamp
（带头带/枢转灯体、非手持长筒）；探照灯/工作灯（三脚架/手柄枪把、极大反射碟）。

## 槽位 + 候选模块表

### Slot A：head_form（③ Primary Form Family — 灯头/斗环包络 + 光学）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| smooth_reflector_cone | forked_anchor | rec_a-yellow...5b5f681c | L79-212 | eligible if compatible | 圆滑塑料斗环 + 平滑抛物反射锥 + 大清透镜 + 纵肋；Volumetric Envelope Form |
| crenellated_strike_bezel | forked_anchor | rec_black...baf8fda5 | L96-224 | eligible if compatible | 喇叭头 + 花齿攻击环 + 深漏斗反射镜；Planar Boundary Form（前缘齿廓） |
| wide_floodlight_head | forked_anchor | rec_flashlight_var_floodhead | L55-247 | eligible if compatible | 大直径浅碟反射镜 + 大平透镜（泛光）；Volumetric Envelope Form |
| penlight_micro_head | world_knowledge_extrapolation (③ Volumetric Envelope) | anchors: 上三者 + reviewer | 生成函数 `_build_head_visuals` (head_ratio 小档) | eligible if compatible | 同 head part tree/lathe primitive/interface；小窄头、浅反射镜、小透镜；Volumetric Envelope Form |

### Slot B：body_form（③ Primary Form Family — 筒身/握持包络）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| straight_cyl_barrel | forked_anchor | rec_a-yellow...5b5f681c | L47-76 | eligible if compatible | 等径塑料 Cylinder 筒 + 锥形肩过渡到头；Volumetric Envelope Form |
| stepped_tactical_tube | forked_anchor | rec_black...baf8fda5 | L59-93 | eligible if compatible | 阶梯铝筒（尾帽 + 中段握持鼓凸 + 前唇）Lathe 多段轮廓；Volumetric Envelope Form |

**degrade 理由（2 candidates）**：源池第 3 个 body 候选 `right_angle_head_body`
（`rec_flashlight_var_anglehead`）是 source map 明确标注的 **boundary case**（体量包络大改、
头颈垂直、易漂浮/穿模/出类目），source map 预授权「若反复不收敛则记为 blocked」。为保证
首版 sweep 收敛、且它与 twist_focus 组合需要额外 perpendicular-neck probe，本版先 **blocked/deferred**，
不进 seed domain（登记在下方「排除项」）。body 主多样性由 straight/stepped 两个明显不同的体量包络
（等径 Cylinder vs 阶梯 grip-swell Lathe）承载，其余结构多样性由 head_form(4)/switch(4)/carry(3) + N 撑起。

### Slot C：switch_mechanism（② joint type / 布置）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| side_push_button | forked_anchor | rec_a-yellow...5b5f681c & rec_black...baf8fda5 | A:L216-275 / B:L241-255 | eligible if compatible | body 上 `button_boss` 平台 + `push_button` 独立 part，**PRISMATIC** 径向内压 -Z；head 固定融入 body |
| twist_focus_head | forked_anchor | rec_black...baf8fda5 | L206-238 | eligible if compatible | 整个灯头成独立 `focus_head`，**CONTINUOUS** 绕 +X 轴旋焦；off-axis `bezel_marker` 使旋转可测 |
| tailcap_click_switch | forked_anchor | rec_flashlight_var_tailswitch | L215-267 | eligible if compatible | `tail_button` 独立 part（尾帽），**PRISMATIC** 轴 (-1,0,0) 前压；head 固定融入 body |
| longitudinal_slide_switch | forked_anchor | rec_flashlight_var_slideswitch | L215-269 | eligible if compatible | body 上 `slide_track` + `slider` 独立 part，**PRISMATIC** 轴 (+1,0,0) 沿筒滑；head 固定融入 body |

### Slot D：carry_feature（携带件 — 次要 slot；"none" 是合法非-module 值）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | forked_anchor（origin B 无携带件） | rec_black...baf8fda5 | n/a（不发 part/visual） | eligible if compatible | 无携带件（战术裸筒） |
| lanyard_strap_loop | forked_anchor | rec_a-yellow...5b5f681c | L159-173, L243-282 | eligible if compatible | `tail_eyelet` Torus（body visual）+ `strap` 独立 part，软环 FIXED 挂尾眼（穿眼 allow_overlap） |
| spring_pocket_clip | forked_anchor | rec_flashlight_var_pocketclip | L167-205, L245-255 | eligible if compatible | `pocket_clip` sweep 弯夹 + `clip_mount` 卡箍，均 body visual（不发 joint） |

硬约束满足：Slot A/C 各 ≥3 候选；Slot D 3 值（含 none）；Slot B 记 degrade 理由降到 2。
每个普通候选均有 `forked_anchor` + `model.py:Lx-Ly`；`penlight_micro_head` 标 `world_knowledge_extrapolation`
且保持同 head part tree/lathe primitive/interface，只离散改体量包络。

## 每槽位 Module Emits / Interfaces

### body (root, always) — body_form ∈ {straight_cyl_barrel, stepped_tactical_tube}
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` | A:L44 / B:L176 |
| visuals (straight) | `barrel_shell` Cylinder, `shoulder_shell` Lathe | A:L47-76 |
| visuals (stepped) | `body_shell` Lathe 多段阶梯轮廓（尾帽/握持鼓/前唇）, `grip_knurl_{i}` 滚花肋 | B:L59-93 |
| head optics（非旋焦时融入 body） | `head_shell` Lathe, `parabolic_reflector` Lathe, `lens_disc` Cyl, `led_bulb` Sphere, `front_bezel_ring` Lathe, `head_rib_{i}`/`bezel_tooth_{i}` ×N | A:L79-212 / B:L96-224 |
| tail | `tail_cap` Cylinder（+ `tail_eyelet` Torus 仅 lanyard） | A:L159-173 |
| carry visuals（仅 pocketclip） | `pocket_clip` sweep, `clip_mount` band | pocketclip:L167-205 |
| internal joints | 无（body 内部全 FIXED-inline visual） | Rule 1 |
| downstream interface | body 轴 (0,0,0)（head twist pivot）; barrel 表面（button boss/track）; tail 面（tail button/strap） | A/B |

### focus_head（仅 twist_focus）— head_form 决定光学包络
| emits | 描述 | 来源 |
|---|---|---|
| parts | `focus_head` | B:L206 |
| visuals | `head_shell`, `reflector`, `lens_disc`, `led_emitter`, `front_bezel_ring`, 齿/肋 ×N, `bezel_marker`(off-axis) | B:L206-224 |
| internal joints | 无 | |
| upstream interface | body 轴 (0,0,0)，CONTINUOUS 轴 (1,0,0)，无 mating（套筒 bearing grandfathered） | B:L230-238 |

### switch part（side/tail/slide）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_button` / `tail_button` / `slider` | A:L216 / tailswitch:L215 / slideswitch:L223 |
| visuals | side:`button_base`+`button_cap`；tail:`tail_cap`(+`rubber_boot`)；slide:`slider_knob` | 各源 |
| joint | side:`button_press` PRISMATIC (0,0,-1) 0-1.5mm，mating(button_boss↔button_cap)；tail:`tail_press` PRISMATIC (-1,0,0) 0-3mm，mating(barrel 尾面↔tail_cap)；slide:`body_to_slide` PRISMATIC (1,0,0) 0-8mm，mating(slide_track↔slider_knob) | A:L267-275 / tailswitch:L260-267 / slideswitch:L263-269 |

### strap（仅 lanyard）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `strap` | A:L243 |
| visuals | `strap_loop` tube_from_spline_points 闭合软环 | A:L243-265 |
| joint | `body_to_strap` FIXED origin 在 tail_eyelet；无 mating（软环穿眼 grandfathered） | A:L276-282 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| head_form | enum | {smooth_reflector_cone, crenellated_strike_bezel, wide_floodlight_head, penlight_micro_head} | smooth_reflector_cone | choice | deterministic procedural sampler | Slot A |
| body_form | enum | {straight_cyl_barrel, stepped_tactical_tube} | straight_cyl_barrel | choice | sampler | Slot B |
| switch_mech | enum | {side_push_button, twist_focus_head, tailcap_click_switch, longitudinal_slide_switch} | side_push_button | choice | sampler | Slot C |
| carry_feature | enum | {none, lanyard_strap_loop, spring_pocket_clip} | lanyard_strap_loop | choice | sampler | Slot D |
| palette_style | enum | {yellow_plastic, black_tactical, silver_industrial, olive_drab, hi_vis_orange, gunmetal} | yellow_plastic | choice | sampler；仅涂装 | ⑥ |
| head_crenellation_count | int | [6, 24] | 16 | independent | 加权采样（小 N 高频）后 clamp | A:L136 / B:L108 / bezelN |
| barrel_radius | float | [0.016, 0.030] | 0.020 | independent | clamp | A:L48 (0.028) / B:BODY_R 0.0175 |
| barrel_length | float | [0.110, 0.200] | 0.150 | independent | clamp | A:L48 (0.180) |
| head_ratio | float | [1.35, 2.30] | 1.70 | conditional | head 半径 = barrel_radius·head_ratio；wide_floodlight 偏大档、penlight 偏小档 | A head 0.052 vs barrel 0.028 ≈1.86 |
| head_radius | float | derived | — | equation | `= barrel_radius · head_ratio` | — |
| head_length | float | [0.038, 0.070] | 0.052 | independent | clamp | A head 长 ≈0.085 / B ≈0.05 |
| reflector_depth_ratio | float | [0.55, 0.95] | 0.80 | conditional | `= f(head_form)`：floodlight 浅(0.55)、strike 深(0.95)；反射镜深度 = head_length·此比 | A/B reflector |
| shoulder_length | float | [0.012, 0.028] | 0.018 | independent | clamp | A:L55-76 |
| (—) | constraint | — | — | inequality | `head_radius ≥ barrel_radius + 0.010`（头必须明显宽于筒，run_tests hero）；违反则回缩 head_ratio | A run_tests L303-309 |

## 7.5 编译预算 / compile budget

自报预算：**≤12s/seed**（依据：库内典型模板 5-20s；本类别每 seed 仅 2-4 个 Lathe 英雄面
（head_shell / reflector / shoulder / 可选 stepped body）+ 若干 Cylinder/Sphere/Torus 图元，无重布尔雕刻）。
分档 tessellation：反射镜/头壳英雄 Lathe `segments ≤ 72`；shoulder/bezel 环 `≤ 48`；
小图元（肋/齿/透镜）用 Cylinder 图元（无 mesh 文件）；N 个齿/肋复用同一 Cylinder 几何、只改 origin。
sweep `--compile-timeout 120`（看门狗 = 预算 ~10×，非质量线）。超预算先降 segments 再迭代。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**：`head_crenellation_count`。

- `count_param`：`head_crenellation_count`；`N_range` = [6, 24]（产品域；样本已覆盖 {8 齿(B), 16 肋(A), 20 肋(floodhead), N(bezelN)}）；
  sampling domain：加权（小 N 6-12 高频粗齿/中肋，大 N 18-24 稀有细密防滑肋）。
- copied object：一个 crenellation 元件 — smooth/flood/penlight 头为 `head_rib_{i}` Cylinder 纵肋（A:L136-145）；
  crenellated_strike 头为 `bezel_tooth_{i}` Cylinder 齿（B:L108-119）。所有 copy 用同一几何 helper。
- naming：`head_rib_{i}` / `bezel_tooth_{i}`，`i∈range(N)`。
- placement：绕头轴等角 `theta = 2π·i/N`，半径 = 头外缘。
- joint policy：全部 FIXED inline visual 于承载 head 的 part（非旋焦=body，旋焦=focus_head），无 per-copy joint。
- source/gating：两 origin 均有真实 `for i in range(N)` 循环；N clamp 到 [6,24]，sweep 各自设上限。
- 次要复制逻辑（记录，不额外发轴）：stepped body 的 `grip_knurl_{i}` 握持肋（B:L75-93，随 stepped_tactical_tube 出现）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | body(root) + [focus_head twist 子件 \| switch 子件] + [strap FIXED 子件]；part 数随 switch/carry 变（旋焦=head 成 part；side/tail/slide=switch part；lanyard=strap part；pocketclip/none=纯 body visual）。全 forked_anchor（A/B/variants） |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`head_crenellation_count` ∈[6,24]，权重小 N 高频 |
| ② 关节类型 | 边换 type/轴 | 有 | PRISMATIC（side -Z / tail -X / slide +X）、CONTINUOUS（旋焦 +X）；全 forked_anchor（A button/B twist/tailswitch/slideswitch）；每种都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 可识别形态 | 有 | head_form={smooth_cone, crenellated_strike, wide_floodlight, penlight_micro}（前三 forked_anchor，第四 world_knowledge_extrapolation·Volumetric Envelope）；body_form={straight_cyl, stepped_tactical}（forked_anchor）。均登记进 `slot_choices`。form_subtype 见 Slot A/B 表 |
| ④ 表面装饰 | 叠加表面细节/改装饰数 | 有 | 纵肋 `head_rib_{i}`(A)、花齿 `bezel_tooth_{i}`(B)、菱形滚花 `grip_knurl_{i}`(B,随 stepped)、front/rear bezel 环带(A)；record_only + host-conformal（肋/齿半径由头外缘逐-head_radius 派生，随 ③⑤ 共形）；派生顺序 ③→⑤→④ |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | barrel_radius[0.016,0.030]、barrel_length[0.11,0.20]、head_ratio[1.35,2.30]、head_length[0.038,0.070]、reflector_depth_ratio[0.55,0.95]（见 §7）。**每个非-continuous 关节运动包络**：side_push PRISMATIC 轴(0,0,-1) 开启向内 [0,0.0015]；tail_press PRISMATIC 轴(-1,0,0) [0,0.003]；slide PRISMATIC 轴(1,0,0) [0,0.008]；旋焦 CONTINUOUS 整圈。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`；每机构一条 targeted `ctx.pose`（按钮内压位移、滑块沿轴位移、旋焦 off-axis marker 转到 -Y）。无 sampled-pose exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：glossy plastic / anodized aluminum / rubber accents / clear polycarbonate lens / silver reflector；palette_style ≥6：yellow_plastic、black_tactical、silver_industrial、olive_drab、hi_vis_orange、gunmetal。材质大类覆盖 ≥ ceil(0.5×6)=3 |

**收尾自检**：head_form 4 族在 0-9 seed 肉眼拉得开（细锥/花齿/泛光碟/微头）；body 直筒 vs 阶梯可辨；
palette 6 色都出现；肋/齿贴头面不悬空；按钮/滑块/旋焦全程不穿模。

## 拓扑多样性审计

总组合数：head_form(4) × body_form(2) × switch(4) × carry(3) = 96 离散组合（× N∈[6,24] 采样档）。

理由：head_form 4 / body_form 2 / switch 4 / carry 3 均可达且 ≥2。

seed_domain_policy：procedural_first（seed=0 不特殊，走同一 `random.Random(seed)` 采样）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次
`rng.choice` 抽 head_form/body_form/switch/carry/palette_style，加权抽 head_crenellation_count（小 N 高频），
`rng.uniform` 抽连续 scale，再 `resolve_config` clamp/派生/投影（head_radius=barrel_radius·head_ratio；
head_radius≥barrel_radius+0.010 回缩；reflector_depth_ratio 由 head_form 条件化）。无非法组合需 gate
（body_form 已排除 right_angle boundary case；其余 96 组合全兼容）。无 regression override。
random sweep / viewer 目检 0-35。

Topology target：1000-seed slot choice tuple distinct 预计 ~90+（96 离散组合 × N 覆盖），受类别本征组合数上限；低于 300 的原因是单物体类别离散轴有限（4×2×4×3），已用 head_form/switch 尽量拉开。report-only，不设门。

Controlled local parameterization：barrel_radius / barrel_length / head_ratio / head_length /
reflector_depth_ratio / shoulder_length / head_crenellation_count。范围/clamp/派生见 §7；
均在 `resolve_config` 求解，不破坏 mating/clearance/joint range/类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rng.choice 4 slot + 加权 N + uniform scale；seed=0 非特殊 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全 96 组合合法；right_angle_head_body blocked（不进域） | 无漂浮/穿模/轴/max-N/bulky/optional-child 失败 |
| controlled local variation | 7 个连续 scale，resolve_config clamp/派生/投影 | 比例变化不破坏接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初版；0-999 成熟审计 | contract failures；axis_realization |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| head_form | 4 | yes | yes | |
| body_form | 2 | yes | no | degrade 记录（right_angle boundary blocked） |
| switch_mech | 4 | yes | yes | |
| carry_feature | 3 | yes | yes | 含 none |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（与 build 选择一致）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility：right_angle_head_body 不进 seed domain；其余全合法
- 无 regression override
- 连续 scale 全在 resolve_config clamp/派生（head_radius=barrel_radius·head_ratio 等）
- 关键 MatingContract：button_boss↔button_cap、barrel 尾面↔tail_cap、slide_track↔slider_knob 存在
- 关键 joint：side/tail/slide PRISMATIC 轴 + 旋焦 CONTINUOUS 轴 (1,0,0) 正确
- N 复制 head_rib/bezel_tooth 命名 + 等角布置
- 每 seed ≥1 非-FIXED joint（switch 保证）

## Reject cases

- head 不比 barrel 明显宽（head_radius < barrel_radius+0.010）→ 不像手电（hero fail）
- 反射镜/透镜被实心头壳封住看不见（头壳未挖空 / lens 不透明）→ 失识别
- 灯头齿/肋悬空（半径未随 head_radius 派生，套在缩放头外）→ island/detached
- 某 seed 零可动关节（head 固定 + 无 switch part）→ 违反「每 seed ≥1 非-fixed joint」
- 按钮/滑块行程中穿模，或旋焦头套 body 未 allow_overlap → 穿模 fail
- 把 right_angle boundary case 放进 seed domain 导致漂浮头/neck 穿插/出类目
- 用 Box 占位替代反射镜锥/透镜（应 Lathe/Cylinder，Rule 3）
- strap 软环未过尾眼 allow_overlap → 穿模

## 与相邻类别的边界

- 不该混入：Lantern / 营地灯（360° 漫射球泡、无定向反射镜、有提梁/底座；flashlight 必须有沿轴定向反射镜 + 更宽头）
- 不该混入：Headlamp / 头灯（头带 + 枢转灯体、短身；flashlight 是长筒手持）
- 不该混入：探照灯 / 工作灯（枪把/三脚架 + 极大反射碟；flashlight 是单轴手持筒）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首版：body_form 降到 2（right_angle boundary blocked，source-map 预授权）；其余 slot 全 ≥3 |
