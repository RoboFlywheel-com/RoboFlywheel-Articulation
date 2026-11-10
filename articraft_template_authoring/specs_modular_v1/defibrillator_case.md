# Defibrillator case — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `defibrillator_case` |
| template path | `agent/templates/defibrillator_case.py` |
| test path (optional) | `tests/agent/test_defibrillator_case_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children per family root + multiplicity on ventilation slats) |

`pattern` 说明：一个 body-form 根件（cabinet 或 case_base）承载所有子件（opening / aed / latch / beacon）作为 parallel children；vent slats 由单个 count 轴复制。两个结构脊（family）由 body_form 决定，其余 slot 按 family 条件采样。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star samples in this subcategory (2 origins + 12 forks) |
| source_index_policy | only adopted module sources are indexed below |

阅读结论：本小类有两个结构脊。CABINET 脊（origin2 rec_...ef2187）= 中空钣金箱 cabinet（cadquery hollow shell）+ 一个开启机构（侧铰门 / 底翻门 / 顶翻透明盖 / 卷帘）+ AED 模块（prismatic 抽出 / revolute 摆出 / fixed 托架）+ 门上把手或旋钮闩 + 可选顶置报警灯 + 右侧壁 N 条通风百叶。CARRYCASE 脊（origin1 rec_...4aa24）= 软/硬携行箱 case_base + 一个铰接盖（侧翻 clamshell 盖 / 顶翻 fold-over 盖）+ FIXED 内嵌 AED + 前 velcro 翻盖或 over-center 卡扣。两脊都必须保留一个真实非-FIXED 开启关节，并把一台 AED 保留在内。12 个 fork 各自只改一根轴。

## 核心身份

一个专门保护单台 AED/除颤器的箱体/外壳，通过一个真实铰接门/盖（或等效开启机构：侧翻门、底翻门、顶翻透明盖、卷帘、clamshell 盖、fold-over 软盖）打开以取出设备。内部始终保留一台 AED（托架 / 滑出架 / 摆出臂）。成熟域覆盖：墙挂钣金柜、立柱夹装柜、户外防雨柜、软携行箱、硬壳携行箱、肩背软包。

不该混入：通用储物柜（无 AED 身份 / 无内嵌设备）、信报箱/电表箱、工具箱/相机箱、无 AED 的软急救包、保险箱/锁盒、纯展示柜。

## 槽位 + 候选模块表

Family 由 `body_form` 决定：`_family_of(body_form)` ∈ {cabinet, carrycase}。opening / aed_retention / latch / vent / beacon 均按 family 条件采样（见 §9 兼容矩阵）。

### Slot A：body_form （③ Primary Form Family，root）

| module_name | source_type | source evidence | model.py:Lx-Ly | family | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| wall_cabinet_box | origin_anchor | rec_...ef2187 | L28-50 (`_cabinet_shell`) + L96-120 | cabinet | eligible if compatible | cadquery hollow 钣金箱 + 内背板 + 搁架；Volumetric Envelope Form |
| pole_mount_enclosure | forked_anchor | rec_..._pole_mount | L81-146 (`_pole_mount_bracket`) + L219-251 | cabinet | eligible if compatible | 同箱体 + C-collar 抱箍/U-bolt/立柱 visuals；Volumetric Envelope Form |
| outdoor_weatherproof_cabinet | forked_anchor | rec_..._outdoor_cabinet | L71-108 (`_roof_cap`) + L242-248 | cabinet | eligible if compatible | 同箱体 + 斜顶雨檐 cap + hooded louvers；Volumetric Envelope Form |
| molded_soft_carry_case | origin_anchor | rec_...4aa24 | L104-242 (base walls + `_rounded_plate` L26) | carrycase | eligible if compatible | box 壁 + ExtrudeGeometry 圆角底/内衬盘；Planar Boundary Form |
| rigid_hard_shell_case | forked_anchor | rec_..._hardshell_case | L87-110 / L113-138 (cadquery shells) + L193-216 | carrycase | eligible if compatible | cadquery 硬壳托 + 加强肋 + 铰链桶；Volumetric Envelope Form |
| soft_shoulder_bag_pouch | forked_anchor | rec_..._shoulder_pouch | L126-160 + L252-271 (top handle tube) | carrycase | eligible if compatible | 高身软包 box 壁 + D-ring + tube 提手；Macro Surface Construction |

### Slot B：opening_mechanism （② 关节/机构，核心开启关节，parallel child of root）

| module_name | source_type | source evidence | model.py:Lx-Ly | family | eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| front_hinged_door | origin_anchor | rec_...ef2187 | L53-63 (`_door_frame`) + L207-215 (REVOLUTE axis 0,0,1) | cabinet | eligible | 侧铰平板门 + 观察窗洞；REVOLUTE +Z |
| drop_down_flap | forked_anchor | rec_..._dropdown_flap | L56-72 + L296-304 (REVOLUTE axis -1,0,0 底铰) | cabinet | eligible | 底铰门前下翻；REVOLUTE ±X |
| clear_flip_up_cover | forked_anchor | rec_..._clear_flip_cover | L62-84 (`_clear_cover`) + L329-339 (REVOLUTE axis 1,0,0 顶铰) | cabinet | eligible | 顶铰透明弧盖上翻；REVOLUTE +X |
| roll_up_shutter | forked_anchor | rec_..._roll_shutter | L60-67 + L160-167 (loop) + L284-294 (PRISMATIC axis 0,0,1) | cabinet | eligible | N 片卷帘 + 导轨 + 卷筒罩；PRISMATIC +Z |
| clamshell_side_lid | origin_anchor | rec_...4aa24 | L244-305 (lid) + L396-409 (REVOLUTE axis 0,1,0) | carrycase | eligible | 侧翻壳盖；REVOLUTE +Y（本模板 authored closed，正角上掀） |
| foldover_top_flap | forked_anchor | rec_..._shoulder_pouch | L332-404 + L508-521 (REVOLUTE axis 1,0,0) | carrycase | eligible | 顶翻软盖含前 drape；REVOLUTE +X |

### Slot C：aed_retention （② 关节，parallel child of root，携带 AED 模块）

| module_name | source_type | source evidence | model.py:Lx-Ly | family | eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| prismatic_slideout_shelf | origin_anchor | rec_...ef2187 | L185-205 + L216-224 (PRISMATIC axis 0,1,0) | cabinet | eligible | AED 模块搁架滑出；PRISMATIC +Y |
| swing_out_revolute_bracket | forked_anchor | rec_..._swingout_bracket | L215-255 + L268-289 (REVOLUTE axis 0,0,1 + cradle_to_aed FIXED) | cabinet | eligible | 摆出臂托盘（cradle 部件 + AED FIXED）；REVOLUTE +Z |
| fixed_cradle | origin_anchor | rec_...4aa24 / rec_...ef2187 | L410-416 (base_to_aed FIXED) | cabinet + carrycase | eligible | AED FIXED 内嵌于泡沫/搁架（degrade：软箱唯一保留方式，见 §9） |

### Slot D：latch_style （② 关节 + accessory，parallel child of opening 或 root）

| module_name | source_type | source evidence | model.py:Lx-Ly | family | eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| pull_handle | origin_anchor | rec_...ef2187 | L174-176 (pull_handle + posts) | cabinet | eligible | 门/帘上固定抓握把手（visual，非关节） |
| rotary_knob_latch | forked_anchor | rec_..._rotary_latch | L175-214 + L247-258 (REVOLUTE axis 0,1,0 面法向) | cabinet | eligible (非 shutter) | T 型旋钮闩，绕门面法向 REVOLUTE 独立部件 |
| velcro_strap_flap | origin_anchor | rec_...4aa24 | L376-394 + L417-430 (REVOLUTE axis 0,1,0) | carrycase | eligible | 前 velcro 软翻盖，REVOLUTE 独立部件 |
| snap_latch | forked_anchor | rec_..._hardshell_case | L383-406 (2×) + L510-524 (REVOLUTE axis 0,-1,0) | carrycase | eligible | 2 个 over-center 卡扣，各自 REVOLUTE 独立部件 |

## 槽位图（slot graph）

pattern: mixed（family 条件 parallel_children + vent multiplicity）

```
[body_form root]  (cabinet 或 case_base，root，无 upstream)
   ├─[opening_mechanism]  REVOLUTE(±Z/±X/±Y) 或 PRISMATIC(+Z)  child of root
   │      └─(可选) rotary_knob_latch / snap_latch → REVOLUTE child of opening panel
   ├─[aed_retention]      PRISMATIC(+Y) / REVOLUTE(+Z)+FIXED / FIXED  child of root
   ├─[latch_style: velcro_strap_flap] REVOLUTE(+Y) child of root（carrycase）
   ├─(可选) alarm_beacon  FIXED child of root（cabinet only，顶置）
   └─[vent slats ×N]      root 表面 visual 复制（cabinet only）
```

接口点位：opening→root 铰链原点在 root 前/顶/底缘，MatingContract 把门内面对 root 前缘（法向接触）；captured-hinge overlap 用 element-scoped allow_overlap。aed→root 搁架顶面/左壁 pivot/泡沫底。latch→opening panel 或 root。beacon→root 顶面 FIXED。

## 每槽位 Module Emits / Interfaces

### Slot A / cabinet body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet` (root) | origin2 L96 |
| visuals | cadquery hollow shell + dark_back_panel + aed_shelf + N side_vent_i + (pole/outdoor 附件) | origin2 L97-120; pole L219-251; outdoor L211-248 |
| downstream interface | 前面 @ y=+D/2；搁架顶；顶面 | origin2 |

### Slot A / carrycase body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `case_base` (root) | origin1 L104 |
| visuals | box 壁 + ExtrudeGeometry 圆角底/内衬（molded）/ cadquery 硬壳+肋+铰桶（hardshell）/ 高身壁+D-ring+tube 提手（pouch） | origin1 L104-242; hardshell L176-278; pouch L126-327 |
| downstream interface | 顶开口缘；泡沫底；前面 | origin1 |

### Slot B / opening_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door` / `shutter` / `lid` | origin2 L122 / roll L152 / origin1 L244 |
| internal joints | root→panel REVOLUTE 或 PRISMATIC | 各源 |

### Slot C / aed_retention
| emits | 描述 | 来源 |
|---|---|---|
| parts | `aed_module`（+ swingout: `cradle_bracket`） | origin2 L185 / swingout L215 |
| internal joints | root→aed PRISMATIC/FIXED，或 root→cradle REVOLUTE + cradle→aed FIXED | origin2 L216-224 / swingout L268-289 |

### Slot D / latch_style
| emits | 描述 | 来源 |
|---|---|---|
| parts (moving) | `latch_knob` / `snap_latch_i` / `front_flap` | rotary L193 / hardshell L385 / origin1 L376 |
| visuals | pull_handle 门上 fixed visual（非部件） | origin2 L174 |
| internal joints | panel→latch REVOLUTE（rotary 0,1,0；snap 0,-1,0；velcro 0,1,0） | 各源 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | 见 Slot A（6） | wall_cabinet_box | choice | procedural sampler | Slot A |
| opening_mechanism | enum | 见 Slot B（6） | front_hinged_door | conditional | 由 `_family_of(body_form)` gate | Slot B |
| aed_retention | enum | 见 Slot C（3） | prismatic_slideout_shelf | conditional | carrycase→fixed_cradle only | Slot C |
| latch_style | enum | 见 Slot D（4） | pull_handle | conditional | family + (shutter→pull_handle) gate | Slot D |
| vent_count | int | [3,12]（cabinet），0（carrycase） | 5 | conditional | 权重档小 N 偏多；carrycase=0 | origin2 L114 / dense=9 / sparse=3 |
| alarm_beacon | bool | {on, off}（cabinet），off（carrycase） | off | conditional | carrycase 恒 off | alarm L279-301 |
| palette_style | enum | 6 colorway（见 §8.5 ⑥） | white_powdercoat | choice | procedural sampler | 各源材质 |
| body_scale | float | [0.90, 1.12] | 1.0 | independent | 均匀采样后 clamp | 各源尺寸 |
| door_open_limit | float | [1.35, 1.75] rad | 1.75 | independent | clamp | origin2 L214 |
| aed_slide_travel | float | [0.16, 0.24] m | 0.22 | independent | clamp（≤ 前面净空） | origin2 L223 |
| (—) | constraint | — | — | inequality | shutter travel 派生 clamp∈[pitch, stack-pitch]；门开角受净空，targeted pose 验证不穿模 | roll L588 |

采样契约：先采 body_form/palette/body_scale（independent）→ family gate 采 opening/aed/latch/vent/beacon（conditional）→ resolve_config 内 clamp 全部连续量与派生 shutter travel。

### 7.5 编译预算 / compile budget（必填）
自报预算：≤12s/seed（timeout watchdog 120）。依据：每 seed 至多 3–4 个 cadquery boolean（cabinet hollow shell 1；hardshell lower+lid 2；clear cover 1；roll shutter 单片 slat mesh 复用 1），其余 Box/Cylinder/ExtrudeGeometry。通风百叶用表面 box visual 表达（不对壳做 N 次 cut-through），vent 复制成本与 N 无关，hero 壳面仍 cadquery hollow boolean（不降级，Rule 3 合规）。tessellation：cadquery tolerance 0.0012；N 个 slat 复用同一 Mesh。

## Multiplicity / Copy Logic

轴 1：vent_count（cabinet family 唯一 multiplicity 轴）
- count_param：`vent_count` = 右侧壁 side_vent_i 百叶片数量
- N_range：产品域 [3,12]；测试偏小；权重档 {3:.14,4:.16,5:.20,6:.16,7:.12,8:.08,9:.06,10:.04,11:.02,12:.02}
- copied object：单个百叶 box visual（+ outdoor 追加 hood box）；naming：稳定索引 side_vent_i；placement：右侧壁竖直等距；joint policy：静态 fixed 装饰（表面 box，无关节）
- source/gating：origin2 L114 (N=5)；dense=9；sparse=3。carrycase family 无 vent（N=0，slot_choices 记 vent_0）

（次级 loop hinge_knuckle_i / red_icon_panel_i / snap_latch 对不作为独立采样轴。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 两大结构脊 cabinet vs carrycase；roll-shutter slat 拓扑；swingout 增 cradle 部件；alarm_beacon 增/减 FIXED 子装配。全部 source-backed |
| └ multiplicity | 同构件 ×N | 有 | vent_count N∈[3,12]（§8）；carrycase N=0 声明无 vent |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE +Z/-X/+X/+Y/面法向/snap；PRISMATIC +Z shutter、+Y aed；swingout REVOLUTE +Z + FIXED；fixed_cradle FIXED。全部 source-backed，每种类型在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有（body_form slot，登记 slot_choices，6 candidate） | wall_cabinet/pole/outdoor=Volumetric Envelope；molded=Planar Boundary；hardshell=Volumetric Envelope；pouch=Macro Surface Construction。source-backed |
| ④ 表面装饰 | 叠加表面细节 | 有 (record_only + world_knowledge_extrapolation) | DEFIBRILLATOR 红标题、绿 AED 十字、白 AED 条、观察窗、gasket、硬壳肋、pouch EMS 十字。宿主共形：signage/window 位置随门尺寸派生；vent 随右壁。非独立 candidate |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 (record_only) | body_scale [0.90,1.12]；door_open_limit [1.35,1.75]；aed_slide_travel [0.16,0.24]。运动包络：门 REVOLUTE [0,open] 前向；shutter PRISMATIC [0,travel] 上抬；aed PRISMATIC [0,slide] 前抽。motion_test_plan：每非-continuous 关节 targeted ctx.pose(upper) 验证方向+位移；harness sampled motion-QC（默认开）扫全程；captured hinge/pin element-scoped allow_overlap；无 exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal / plastic(shell/fabric) / glass(window)。≥6 colorway：white_powdercoat、safety_yellow、emergency_green、charcoal_orange、red_black_ems、medical_blue。palette_style 每 seed 采样驱动全部 .visual；材质大类覆盖 ≥3 |

## 采样与覆盖审计

总组合数（近似，family 条件）：cabinet ≈ 3×4×3×2×2×10 ≈ 1440（shutter 减半 latch）；carrycase ≈ 3×2×1×2 ≈ 12。有效离散组合 » 300。

理由：cabinet 脊组合空间大；carrycase 脊较小但 body/opening/latch 提供拓扑差异；palette×body_scale 连续覆盖。

seed_domain_policy：procedural_first（seed=0 不特殊）。
Procedural Sampling / Sweep Plan：config_from_seed(seed) 用 random.Random(seed)：采 body_form → _family_of → 按 family 采 opening/aed/latch（gate 非法组合：shutter+rotary→pull_handle；carrycase+prismatic→fixed_cradle）→ vent_count（cabinet 权重，carrycase=0）→ alarm_beacon（cabinet bool，carrycase off）→ palette_style → body_scale/door_open_limit/aed_slide_travel。clamp/派生在 resolve_config。sweep 0-35 初检，0-999 成熟审计。
Topology target：≥300（满足）。report-only。
regression overrides：none。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form → family gate → opening/aed/latch/vent/beacon → palette/scale | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | carrycase→{clamshell,foldover}×{fixed_cradle}×{velcro,snap}×vent0×beacon_off；cabinet→{4 opening}×{3 aed}×{pull,rotary}×vent[3,12]×beacon{on,off}；shutter→pull_handle | 无脊混装、无 floating、无穿模、轴/range 正确 |
| controlled local variation | body_scale/door_open_limit/aed_slide_travel clamp | 比例变化不破坏接口/净空/关节原点/identity |
| regression overrides | none | — |
| random sweep | 0-35 初检，0-999 成熟审计 | contract failures；axis_realization；viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 6 | yes | yes | ③ Primary Form Family slot |
| opening_mechanism | 6 (cabinet 4 / carrycase 2) | yes | yes (cabinet) | family-gated |
| aed_retention | 3 (cabinet 3 / carrycase 1) | yes | yes (cabinet) | carrycase 单一 fixed_cradle：软箱唯一 AED 保留方式，degrade 有记录 |
| latch_style | 4 (cabinet 2 / carrycase 2) | yes | — | family-gated |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（body_form/opening/aed/latch/vent_N/beacon）
- config_from_seed 对所有 seed（含 0）用确定性 procedural sampling
- 兼容矩阵 gate 阻止非法脊混装
- 无 curated/modulo 主 seed 表
- body_scale/door_open_limit/aed_slide_travel 在 resolve_config clamp；shutter travel 派生并 clamp
- 每个非-FIXED joint 有 MatingContract 或 captured-pin element-scoped allow_overlap
- 关键关节 type/axis/range 符合候选表；每 seed 至少一个非-FIXED 开启关节
- copied vent 遵守 side_vent_i naming 与右壁等距 placement

## Reject cases

- 任一 seed 无非-FIXED 开启关节 → 违反核心身份
- carrycase body 装 cabinet 侧铰门 / prismatic 抽屉（脊混装）
- roll_up_shutter 配 rotary_knob_latch
- AED 模块缺失或 floating
- 门/盖开启全程穿模而无 allow_overlap 理由
- vent slat 悬空或 count 越界
- 装饰 signage 常数尺寸不随门面缩放
- 单色：palette_style 未驱动 .visual

## 与相邻类别的边界

- 不该混入：通用储物柜/更衣柜（Container_Locker）——无 AED 身份、多 bay bank
- 不该混入：信报箱/电表箱 / 工具箱/相机箱——无 AED、无医疗托架
- 不该混入：保险箱/锁盒——本类以快速取用为核心
- 不该混入：无 AED 的软急救包——必须保留可识别 AED 模块

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Container_Locker 结构孪生：parallel_children + family gate + vent multiplicity + palette_style |

## 模板实现备注（可选）
- cabinet family 共享 _cabinet_shell cadquery helper + _build_cabinet_aed；carrycase 共享 _rounded_plate/_rounded_ring ExtrudeGeometry helper + _build_case_aed
- captured overlaps 需 element-scoped allow_overlap：clamshell/hardshell barrel↔barrel、snap pin↔boss、rotary knob↔door、swingout pivot↔wall、shutter slat↔guide、door_shell↔shell(seated reveal)、beacon↔shell(顶座)
- pouch 丢弃 loose cable 与 shoulder strap spline，保留 top handle（端点嵌 rim）
- vents 用表面 box（不 cut-through）控制编译预算
