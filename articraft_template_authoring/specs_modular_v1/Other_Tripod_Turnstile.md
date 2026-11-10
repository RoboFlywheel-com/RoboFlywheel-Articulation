# tripod_turnstile — Modular Spec (as built)

## 元信息
| 项 | 值 |
|---|---|
| slug | `tripod_turnstile` |
| template path | `agent/templates/Other_Tripod_Turnstile.py` |
| test path (optional) | `tests/agent/test_tripod_turnstile_template.py` |
| stage | `IMPLEMENTED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

> 来源轴说明：本 slug 来自 **picture 小类 `Other/Tripod Turnstile`** 的 workbench
> 资产池（2 个 root seed + 8 个单轴变体），与 dataset 类目模板 `turnstile_gates`
> 是**独立的两条轴**（同物、不同源池）。详见「与相邻类别的边界」。
> 本文件是 review 后多轮迭代的 **as-built** spec（与发布的 `agent/templates/Other_Tripod_Turnstile.py` 一致）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | picture 小类 `Other/Tripod Turnstile` 全量 workbench 资产：2 root seed（stainless 002 / model-a 001）+ 8 单轴变体；`model.py` / `record.json` 全读 |
| source_index_policy | only adopted module sources are indexed below |
| samples_adopted_as_module_sources | 10 |

两个 root seed 共享同一核心拓扑：固定 pedestal/cabinet（frame）+ 1..N 个 rotor hub（每个带
`arm_count` 根 45° 锥面径向臂）+ 每 hub 一根 CONTINUOUS 转轴。S1(stainless) 侧装(side-mount)、
S2(model-a) 前装(front-mount) + 阶梯柱身/granite 顶/侧读卡器。**实现取舍**：front-mount（轴前下
倾、hub 在前斜面）会把立柱摆在通道正中、挡住人行走,因此**最终只采用 side-mount**(立柱在道边、
臂横跨车道);model-a 的**外观**(阶梯柱身/granite/侧读卡器)仍作为可选项保留。

## 核心身份

腰高(~1.0 m)门禁三辊闸:落地固定的 pedestal/cabinet 承载一个或多个 rotor hub,每 hub 在
45° 锥面上带 `arm_count`(默认 3)根等角径向拦挡臂,绕**自身倾斜轴 CONTINUOUS** 旋转,让人推臂
分次通过(可叠加一根 anti-panic 水平 REVOLUTE「落臂」)。**一条「车道」= 一个供单人通过的通道**:
人沿 +Y 走,臂沿 ±X **横跨车道**拦挡。整组闸机沿 X 排成**一排**,坐落在**一块薄地台板**上(唯一的
连接结构,无立柱间连杆)。

不该混入:全高旋转门 / 摆闸翼闸(无中央辊臂转子)、平移闸(PRISMATIC 门扇)。

## 槽位 + 候选模块表

### Slot A：pedestal_form(落地 cabinet 形态,frame 根)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rect_cabinet_head | S1 rec_stainless-…_ea880fc3 | L102-149 + assembly | eligible if compatible | 金字塔底 + 锥柱 loft + 楔形头 loft |
| stepped_chamfer_cabinet | S2 rec_model-a-…_35b5d879 | L72-99 + L138-153 | eligible if compatible | 空心薄壁柱 → chamfer loft → head box(model-a 外观) |
| round_post | S3 …round-post…_fccb7b6c | L93-131 + L247-258 | eligible if compatible | 圆柱立柱(lathe) + 半球顶 |
| slanted_optical_head | S4 …slanted-optical-head…_e0cb8f21 | L127-145 + L105-161 | eligible if compatible | 前倾斜面光学头 |

### Slot B：bank_style(整排闸机的组成方式,均为 side-mount、同一排 cy=0)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| uniform_single | S1 / S8 / S9 | pedestal_plan uniform 分支 | eligible if compatible | N 个单侧闸机同向,N 道,**每道 1 根棍**(对面=下一柱背面/外栏) |
| twin | S1 | pedestal_plan twin 分支 | K=2 only | 1 个中心**双侧**闸机,左右各一道,**每道 1 根棍**(对面=外栏) |
| ends_in_middle_double | S1(+S8) | pedestal_plan ends 分支 | hub_count≥2 | 两端单侧朝内 + 中间双侧;K 道用 K+1 柱;**每道 2 根棍**在道中央会合成 1 个拦挡点;gap=**2×lane_width** |

### Slot C：arm_mechanism(主机构槽 —— 辊臂动作)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| continuous_rotation(基线) | S1 …_ea880fc3 | L152-166 + L341-365 | eligible if compatible | hub 绕自身轴 CONTINUOUS,臂随转 |
| anti_panic_drop_arm | S7 …drop-arm…_e7cf9f83 | L178-192 + L395-451 | eligible if compatible | hub CONTINUOUS + 水平 REVOLUTE 落臂 carrier |

### Slot D：barrier(车道拦挡 / 导向)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tube_railings(基线) | S1 …_ea880fc3 | L169-213 + 装配 | eligible if compatible | 沿 Y(平行人行)管栏;两端外缘各一道(含 flush 端),坐地台板 |
| extended_guide_railings | S6 …extended…_dcc77210 | L172-226 + 装配 | eligible if compatible | 多段延长导栏(沿 Y 更长) |
| glass_swing_panel | S5 …glass-swing…_091848cd | L336-431(已重做为前置门) | eligible if compatible | **每个闸机正前方(+Y, GATE_FRONT_Y)居中一个铰柱**,单侧闸机 1 扇 / 双侧 2 扇,绕竖直 Z REVOLUTE;1:1 对应棍 |
| none | —(降级) | — | degrade only | 无装饰栏;flush 端仍有最小 curb |

## 槽位图(slot graph)

```
pattern: mixed
base_plate(薄地台板, cabinet visual, 跨整组 footprint, 唯一连接结构)
  └─ Slot A pedestal_form × N  (沿 X 一排, cy=0; top_plate/reader 为 appearance visual)
        每柱按 bank_style/faces 提供 ±X 侧面 boss(visual)
        ├─[rotor_spin_{i}: CONTINUOUS @ boss 面, 轴(±cosT,0,sinT)]─▶ Slot C hub_{i}(+arm_count 锥臂)
        │     anti_panic 时: cabinet ─[arm_drop REVOLUTE 水平]▶ carrier ─[CONTINUOUS]▶ hub
        │     × multiplicity hub_count(=车道数)、arm_count
        └─ Slot D barrier(FIXED 坐地台板: 管栏/延长栏/curb;  或 glass: 前置铰柱 + REVOLUTE-Z 叶)
```

接口点位:
- **base_plate**:跨整组 footprint 的薄板(z 0–0.022);所有独立 part(hub via boss、rail、glass 柱)
  的 FIXED/REVOLUTE joint 原点都落在板上,既满足 `fail_if_articulation_origin_far_from_geometry`
  又让全模型连成一棵树,**无立柱间连杆**。
- **rotor 安装**:cabinet 在侧面 boss(visual),hub collar flush 坐 boss 端面(captured-seat,
  element-scoped `allow_overlap` + `expect_contact`);joint 轴 local +Z,rpy 映射到 (±cosT,0,sinT)。
- **barrier**:管栏/延长栏/curb = FIXED 坐地台板(沿 Y);玻璃门 = 前置铰柱(FIXED 坐板) + 叶 REVOLUTE-Z。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| pedestal_form | enum | rect / stepped_chamfer / round_post / slanted_optical_head | rect | choice | sampler 选 | Slot A |
| bank_style | enum | uniform_single / twin / ends_in_middle_double | uniform_single | conditional | K≥2 才采 twin/ends;twin 仅 K=2(否则降 uniform) | Slot B |
| arm_mechanism | enum | continuous_rotation / anti_panic_drop_arm | continuous_rotation | choice | sampler 选 | Slot C |
| barrier | enum | tube_railings / extended_guide_railings / glass_swing_panel / none | tube_railings | choice | K≥3 偏 none/extended | Slot D |
| top_plate / reader_module / palette_style | enum (appearance) | 见旧表(3 / 2 / 5) | — | choice | 仅换 visual/material,不动拓扑;每 seed 采样 | S1 / S2 |
| hub_count | int (multiplicity) | [1, 5] (=车道数) | 1 | independent | 加权小 N 偏多 | S8 / S9 |
| arm_count | int (multiplicity) | [3, 4] | 3 | independent | 权重偏 3(典型三辊) | S10 |
| hub_tilt_deg | float | [20, 35] | 28 | independent | clamp | S1 L58 |
| **lane_width** | float | [0.50, 0.72] (clamp 0.45–0.85) | 0.55 | **independent** | 单人通道宽;**驱动 arm_l、pitch、双棍 gap** | 新增 |
| pedestal_width_scale | float | [0.85, 1.25] | 1.0 | independent | clamp;闸机footprint/宽度 | S1 |
| arm_reach_scale (fill) | float | [0.90, 1.0] | 1.0 | independent | 棍占可行 reach 的比例(留多样性) | — |
| **arm_l** | float | derived | — | **equation** | `= fill × min( (lane_width − standoff − 0.06)/k − ARM_R ,  SIDE_HUB_Z − 0.06 )`;k=锥臂水平 reach 系数 | resolve_config |
| pitch(立柱中心距) | float | derived | — | **conditional** | `= 2·half + lane_width`(single/twin) / `2·half + 2·lane_width`(ends_double) | pedestal_plan |
| (—) | constraint | — | — | **inequality** | ends_double 两对向棍扫掠盘不重叠:`2·k·(arm_l+ARM_R) ≤ 2·lane_width − 2·standoff − clr`(由 arm_l 派生满足) | resolve_config |
| (—) | constraint | — | — | **inequality** | 单棍道:`k·(arm_l+ARM_R) ≤ lane_width − standoff − clr`(棍横跨到对面不撞) | resolve_config |

**连续尺寸采样契约(已实现于 `config_from_seed`/`resolve_config`):** 先采 independent
(`lane_width` / `pedestal_width_scale` / `arm_reach_scale` / `hub_tilt_deg`)→ 按 equation 派生
`arm_l`(填满车道、受落地余量封顶)→ 用上面两条 inequality 保证(由 arm_l 的派生公式天然满足,
即"每根棍只占其车道的 reach 预算")→ conditional 解析 pitch(单/双棍道) 与 bank_style 合法性。
**全部在 `resolve_config` 求解,不留到 builder。**

## Multiplicity / Copy Logic

- **count_param 1: `hub_count`**(=车道数,K)
  - `N_range`:`[1, 5]`;加权小 N 偏多(N=1/2 最常见)。
  - copied object:整 tripod hub(hub_core + arm_{j}×arm_count)+ 其 boss;ends_double 含端/中柱。
  - naming:`tripod_hub_{i}` / `for i ...`;boss `rotor_boss_{i}`。
  - placement:沿 X 等距,**同一排 cy=0**;pitch 见 §7(双棍道 ×2)。
  - joint policy:各 hub 独立 `rotor_spin_{i}` CONTINUOUS(轴 local +Z,世界轴由 boss 面 rpy 表达)。
  - bank 组成(由 `bank_style` 决定):uniform_single = K 柱全单侧同向;twin(K=2)= 1 中心双侧;
    ends_in_middle_double = K+1 柱(两端单侧朝内 + 中间双侧),每道 2 对向棍。
- **count_param 2: `arm_count`**(每 hub 辊臂数)
  - `N_range`:`[3, 4]`;权重偏 3。copied:单锥臂 `arm_{j}`;placement 锥面等角;随 hub 旋转。

## 拓扑多样性审计

结构轴乘积(不含 appearance):pedestal_form(4) × bank_style(3,K≥2) × arm_mechanism(2) ×
barrier(4) × hub_count(1–5) × arm_count(2) ≫ 数百种 part-tree/joint 拓扑。


seed_domain_policy:procedural_first。Sweep:seeds 0-49 初轮,0-999 成熟审计。Topology target 富类别建议 ≥300（report-only）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rotor_mount=side(恒) → 加权 hub_count → bank_style(K≥2) → 三结构 enum → arm_count → appearance → lane_width/pedestal/fill/tilt | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | twin 仅 K=2;K≥3 barrier 偏 none/extended;arm_l 派生填满车道并受落地封顶 | 无悬空/穿模、轴正确、棍 sweep 不碰对向棍(disk 不重叠)、一排同 Y |
| controlled local variation | lane_width / pedestal_width_scale / hub_tilt_deg(independent) + arm_l(equation) + pitch(conditional) | 比例变化不破坏 boss 接口、clearance、joint origin、identity |
| regression overrides | none | previously failed only |

## Validator

- slot_choices_for_seed returns implemented module names；config_from_seed 全程 procedural。
- **arm_l 由 lane_width/落地余量 equation 派生,不独立采样**;cross-part 依赖(equation/inequality/conditional)全部在 `resolve_config` 求解。
- ends_double 两对向棍扫掠盘不重叠(inequality);单棍道棍横跨不撞对面(inequality);均由 arm_l 派生满足。
- 所有立柱同一排(same Y);ends_double 每道 2 棍、其余每道 1 棍。
- 每 hub `rotor_spin_{i}` CONTINUOUS axis=local+Z;anti-panic 追加水平 REVOLUTE;glass 叶 REVOLUTE-Z。
- captured-seat:hub collar ↔ boss(element-scoped allow_overlap + expect_contact)。
- base_plate 提供所有 FIXED/REVOLUTE joint 的 parent 几何(无立柱间连杆);rail/curb/glass 坐板上。
- 栏杆沿 Y(span_y > 2·span_x);有栏杆时两端外缘都有栏杆。
- glass 1:1:`glass_leaf` 数 == 棍面数(单侧 1、双侧 2),前置居中,无底部连杆。
- palette/appearance 实际随 seed 变化(目检不得全同色/同顶/同读卡器)。

## Reject cases

- 立柱错位(Y stagger)使一道里两棍一前一后 → 人"连过两个"(必须同排会合成一个拦挡点)。
- 立柱排顺着人行方向 → 人沿排走"连过很多个"(立柱排必须 ⊥ 人行,每人过一道一棍组)。
- front-mount 把立柱摆在通道正中挡住人(已弃用,路由到 side)。
- 道宽/棍/闸机大小各自乱采:棍必须由 lane_width 派生填满车道;ends_double gap 必须=2×lane_width。
- ends_double 棍太长致对向扫掠盘重叠(旋转穿模);或单棍道棍撞到对面栏杆/下一柱。
- 出现立柱间连杆/底部连接条(应只有一块地台板);玻璃门带底部连杆。
- glass 与棍数不 1:1,或玻璃门没放在闸机正前方居中。
- 栏杆方向 ⊥ 人行(挡住路);或多闸机有栏杆时最外侧端缺栏杆。
- pedestal 形态降级成 Box/Cylinder(丢 loft/lathe)。

## 与相邻类别的边界

- 不该混入:`turnstile_gates`(dataset 类目模板)—— 同物但**源池不同轴**(dataset 5★ vs picture 小类 workbench),互不引用。
- 不该混入:摆闸/翼闸/全高旋转门(无中央辊臂转子);平移闸/速通门(PRISMATIC)。

## 模板实现备注

- side-mount 为唯一安装;front-mount(model-a 的前下倾 hub)因立柱挡道而弃用,但其**外观**
  (stepped_chamfer_cabinet / granite_overhang / side_card_reader)保留为 appearance 选项。
- 一块 `base_plate`(`_assembly_footprint` 算 footprint)是引擎要求的唯一连接(单 root + joint 原点
  需两端有几何);它替代了所有立柱间连杆/sill。
- 玻璃门重做为**每柱前置居中铰柱 + 1/2 叶**(原 S5 是中心后置 + 底部连杆,已弃);叶 leaf_w=lane_width。
- ends_double:`arm_l` 经 disk-no-overlap 公式收到"恰好填半个双宽道",两棍中央会合留 ~5cm。
- palette:参 `cushion.py` 的 `PALETTE_STYLES` + `rng.choice` 模式。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved (human-reviewed across多轮 viewer 迭代) |
| reviewer notes | 多轮人工目检确认:一排同 Y、每人过一道、栏杆 ∥ 人行且两端封闭、玻璃门正前方居中 1:1、无立柱间连杆(单地台板)、lane_width/闸机大小参数化且棍派生跟随。sweep verdict=pass。 |

## Module Source Index

| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_stainless-…_ea880fc3 | L102-425 | 核心 base:cabinet + 侧装 hub + 锥臂 + 管栏 + 转轴数学 |
| S2 | rec_model-a-…_35b5d879 | L39-210 | 外观:阶梯 chamfer 柱身 + granite 顶 + 侧读卡器 |
| S3 | …round-post…_fccb7b6c | L93-258 | 圆柱立柱 |
| S4 | …slanted-optical-head…_e0cb8f21 | L105-295 | 斜面光学头 |
| S5 | …glass-swing…_091848cd | L336-431 | 玻璃摆门 REVOLUTE(重做为前置门) |
| S6 | …extended-guide-railings…_dcc77210 | L172-431 | 多段延长导栏 |
| S7 | …anti-panic-drop-arm…_e7cf9f83 | L178-451 | 落臂 REVOLUTE 机构 |
| S8 | …hub-count-3…_9ed09ba3 | L242-387 | hub 复制逻辑 |
| S9 | …hub-count-1…_b6dc0f05 | 全文 | 单通道 |
| S10 | …arm-count-4…_e977074b | L347-365 | 每 hub 4 臂 |
