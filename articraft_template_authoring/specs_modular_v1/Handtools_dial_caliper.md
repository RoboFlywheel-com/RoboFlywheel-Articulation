# dial_caliper (analog dial / digital / vernier sliding measuring caliper) — Modular Spec

> 来源小类：`picture/Handtools/dial caliper`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Handtools_dial_caliper.md`。
> **"dial_caliper" 在此 = 滑动测量卡尺家族**（analog 表盘 / digital 数显 / vernier 游标三种读数，皆为卡尺），核心机构是 `beam`（root）+ `slider`（carriage）沿 **PRISMATIC** `beam_to_slider`（axis +X）滑动量测——这是每个候选都有的「定义性机构」。analog 读数额外加一个 **CONTINUOUS** `slider_to_needle`（axis +Z，mimic 滑动行程）；digital / vernier 去掉 needle 后仅剩 prismatic（仍 ≥1 非 fixed joint）。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 parent + 8 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5（逐一核对 `record.json`）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐文件全文读取核对）。引用以 part / joint / helper **名字** 为准（`beam` / `slider` / `needle` / `lock_screw` / `_beam_body` / `_fixed_jaw` / `_slider_body` / `_dial_bezel` / `_dial_face` / `_dial_ticks` / `_dial_needle` / `_thumb_roller` / `_depth_rod` / `_lcd_housing` / `_lcd_screen` / `_lcd_segments` / `_main_scale_ticks` / `_thumb_lip` / `_lock_screw` / `beam_to_slider` / `slider_to_needle` / `slider_to_lock_screw` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `dial_caliper` |
| template path | `agent/templates/Handtools_dial_caliper.py` |
| test path (optional) | `tests/agent/test_dial_caliper_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（root `beam` 同时挂 readout / jaw_config / accessory / beam_profile 四个槽位的 part / visual；`slider` 是公共 carriage，readout 与 accessory 的活动件挂在它或 beam 上）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 槽位变体；均 converged，compile success、均含 ≥1 非 fixed joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享拓扑骨架（每个候选都有）**：`beam`（root，`_beam_body` + `beam_scale` visual + `fixed_jaw` visual）→ `slider`（carriage，`_slider_body`：saddle 抱梁 + 镜像 jaws + readout boss/neck）经 **`beam_to_slider` PRISMATIC axis=(1,0,0)**（origin=SLIDER_REST_X，lower=0 / upper=SLIDE_TRAVEL=0.150）。两条恒定 captured allow_overlap：`slider_body`↔`beam_body`（saddle 抱梁）、`depth_rod`↔`beam_body`（rod 走梁尾通道，accessory 决定是否存在）。parent / depthjaw / internaljaw / stepjaw / lockscrew / norod / channel_beam 共 7 个样本是 **analog 读数**（带 `needle` part + `slider_to_needle` CONTINUOUS）；digital / vernier 两个去掉 needle。
- **readout 轴**（Slot A）：analog（`dial_bezel`/`dial_face`/`dial_ticks` 圆表 visual + `needle` 独立 part + `slider_to_needle` CONTINUOUS）/ digital（`lcd_housing`/`lcd_screen`/`lcd_segments`/`button_{i}` 平板 LCD visual，**删 needle/joint**）/ vernier（梁上 `main_scale_ticks` + slider 上 vernier plate+ticks，**删 needle/joint**）——这是真正改 part 数（needle ±1）与 joint 拓扑（CONTINUOUS ±1）的轴。
- **jaw_config 轴**（Slot B）：dual_inside_outside（大外量 blade + 小内量 tip，上下两套）/ depth_flat（下颚改短平 registration foot）/ internal_only（删下 blade，仅上内量 tip，root 改窄）/ step_jaw（下颚 compound：step shoulder ledge + 主 blade）——`fixed_jaw` 与 `slider_body` 的 jaw polyline 形态变化，part 树不变（jaw 是 beam/slider 的 visual，非独立 part）。
- **accessory 轴**（Slot C）：rod_and_roller（`depth_rod` visual + `thumb_roller` 18-flute 旋钮 visual）/ lock_screw（删 thumb_roller，加 `lock_screw_boss` visual + **`lock_screw` 独立 part** + `slider_to_lock_screw` REVOLUTE +Z）/ simplified_no_rod（删 depth_rod + thumb_roller，加 `thumb_lip` 模制凸唇 visual）——lock_screw 增 1 part + 1 REVOLUTE joint（真正拓扑变化）；no_rod 删 depth_rod（同时去掉 rod↔beam allow_overlap）。
- **beam_profile 轴**（Slot D）：flat_bar（`_beam_body` 单 box + 圆角，saddle 矩形抱梁）/ channel_beam（`_beam_body` I-section：上下 flange + web + 底面 guide rail 槽；slider saddle 改 I-cavity + gib 入槽）——beam 与 slider saddle 的 mesh 截面变化，part 树 / joint 不变。
- **module-local 复制（非 slot 轴）**：`dial_ticks`（analog 内 `for i in range(50)`，每 5 为 major）、`thumb_roller` flutes（`for i in range(18)`）、`lock_screw` knurl flutes（`for i in range(20)`）、vernier 主尺 ticks（`for i in range(total_ticks)`，total≈171）与游标 ticks（`for i in range(10)`）——全是 module 内部循环，不作 slot 轴（见 §8）。

## 核心身份

一支 ~150 mm（6"）滑动测量**卡尺**：一根扁平 graduated **梁**（`beam`，长 ~0.205 m，长轴沿 +X，截面在 Y-Z；顶面有刻度带 / 主尺）作 root，左端固定 **fixed_jaw** 量爪头；一只 **slider**（carriage，saddle 抱梁、镜像量爪）沿 **PRISMATIC `beam_to_slider`（+X）** 滑动——正 q 张开量爪间隙、推 depth rod 出梁尾，这是**定义性测量机构**。slider 上挂一种**读数装置**（圆表盘 + 摆动指针 / 平板数显 LCD / 游标刻度窗），并可选**微调 / 锁定附件**（带刻花的 thumb roller + depth rod / 旋锁螺丝 / 简化模制 thumb lip）。活动语义 = **carriage 沿梁滑动量测**（恒定 PRISMATIC），analog 读数另加**指针随行程摆动**（CONTINUOUS mimic），lock_screw 附件另加**锁丝拧动**（REVOLUTE +Z）。默认成熟域：readout(3) × jaw_config(4) × accessory(3) × beam_profile(2) 的笛卡尔积小型手持卡尺。

不该混入：
- **千分尺 / 测微计（micrometer）**——主机构是螺纹 thimble REVOLUTE 旋进（spindle/anvil 螺旋测量），不是直线 PRISMATIC carriage；马蹄 frame 形态不同，出类。
- **直尺 / 卷尺 / 钢尺（ruler / tape）**——纯刻度尺无 carriage、无量爪、无活动测量机构（最多卷尺有卷簧），缺 PRISMATIC slider 即出类。
- **量规 / 塞规 / 螺纹规（gauge blocks / plug gauge）**——固定量块无滑动 carriage、无读数装置。
- **digital 与 vernier 仍是卡尺**：digital 只是把圆表盘换平板 LCD、vernier 换游标刻度，梁+slider+PRISMATIC carriage 的卡尺身份不变（去 needle 后仍 ≥1 非 fixed joint）。

## 槽位 + 候选模块表

> **建模注记**：四个槽位都挂在公共 `beam`(root)/`slider`(carriage) 上（parallel_children）。**只有 readout 与 accessory 改 part 树 / joint 拓扑**（needle part ±1 与 CONTINUOUS ±1；lock_screw part +1 与 REVOLUTE +1）。**jaw_config 与 beam_profile 是 mesh-profile 维度**（jaw polyline / beam 截面重写，part 数 / joint 不变），列为候选轴以对齐 schema，与前两轴的笛卡尔积共同撑开多样性（见 §9）。恒定 PRISMATIC `beam_to_slider` 不属任何槽（是骨架）。

### Slot A：readout（测量读数装置 —— 改 needle part 与 needle joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| analog_dial（基线） | rec_..._b08cf719（parent） | `_dial_bezel` L205-221 / `_dial_face` L224-233 / `_dial_ticks`(for i in range(50)) L236-253 / `_dial_needle` L256-275 / dial visuals L358-375 / `needle` part L397-402 / `slider_to_needle` CONTINUOUS L425-433 | eligible if compatible | 圆 chrome bezel + 白表面 + 50-tick 表盘（slider visual）+ **独立 `needle` part** 绕 +Z **CONTINUOUS** 摆动（mimic 滑动行程）；part 数 = beam+slider+needle，joint = PRISMATIC + CONTINUOUS |
| digital_lcd | rec_caliper_var_digital | LCD 常量 L63-69 / `_lcd_housing` L212-228 / `_lcd_screen` L231-237 / `_lcd_segments`(digit loop) L240-280 / `_button_pad` L283-293 / LCD+button visuals L378-410 / **单 PRISMATIC only** L435-445 | eligible if compatible | 平板矩形 LCD housing + 凹陷 screen + segment bars + 2 个 `button_{i}` pad（全 slider visual）；**删 needle part / 删 slider_to_needle**，仅剩 PRISMATIC（run_tests L491-496 断言「exactly one articulation」）|
| vernier_scale | rec_caliper_var_vernier | scale 常量 L62-70 / `_tick_mark` helper L143-152 / `_main_scale_ticks`(for i in range(~171)) L155-198（beam visual L352-356）/ slider vernier plate+ticks(for i in range(10)) in `_slider_body` L250-287 / **单 PRISMATIC only** L395-405 | eligible if compatible | 梁顶 `main_scale_ticks` 主尺（多 fine ticks）+ slider 顶 vernier plate + 10-tick 游标窗（fused 进 slider_body）；**删 needle part / 删 joint**，仅剩 PRISMATIC（run_tests L506-518 断言无 dial/needle）|

### Slot B：jaw_config（量爪配置 —— `fixed_jaw` + slider jaw polyline 形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| dual_inside_outside（基线） | rec_..._b08cf719（parent） | `_fixed_jaw`（root block + 大外量 lower_blade + 小上内量 upper）L92-135 / `_slider_body` 镜像 jaws L138-202（lower L159-171 / upper L173-184）| eligible if compatible | 上下两套：大 outside-measuring blade（drop −Y ~0.040 渐尖）+ 小 inside-measuring knife tip（rise +Y ~0.022）；通用内 / 外量爪 |
| depth_flat | rec_caliper_var_depthjaw | JAW_DOWN_LEN=0.014 + ROD 加长 L54/68-69 / `_fixed_jaw` 平 foot L94-139 / `_slider_body` 平 foot L142-206 | eligible if compatible | 下颚改**短平 registration foot**（矩形平底，drop ~0.014，`extrude(JAW_T*1.2)` 稍宽稳）+ 保留上内量 tip；depth rod 强化为主测量件（ROD_LEN 0.195 出梁尾），用于 step / depth 配准 |
| internal_only | rec_caliper_var_internaljaw | `_fixed_jaw` **仅上 tip**（窄 root L108-112 + upper L113-125，删 lower blade）L97-126 / `_slider_body` 仅上 tip（删 lower）L129-179 | eligible if compatible | **删去下外量 blade**，仅保留上 inside-bore knife tip（root 改为梁顶半高板，不下伸）；slim 内孔测量头（run_tests L503-526 断言 jaw 不下伸梁底）|
| step_jaw | rec_caliper_var_stepjaw | STEP 常量 L57-62 / `_fixed_jaw` compound step L100-146（step polyline L118-126）/ `_slider_body` compound step L149-216（step polyline L171-179）| eligible if compatible | 下颚 **compound**：上段 flat step registration face（set back STEP_DEPTH=0.0045）+ 水平 step ledge（STEP_HEIGHT=0.012）+ 主测量 blade 续下到尖；step / shoulder 测量爪（run_tests L549-582 验 step profile）|

### Slot C：accessory（微调 / 锁定附件 —— 改 lock_screw part / depth_rod 存在性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rod_and_roller（基线） | rec_..._b08cf719（parent） | `_thumb_roller`(for i in range(18)) L278-294 / thumb_roller visual L380-385 / `_depth_rod` L297-303 / depth_rod visual L389-394 | eligible if compatible | `depth_rod` 细杆 visual（走梁尾通道，正 q 出尾）+ `thumb_roller` 18-刻花微调轮 visual（slider 下右缘）；两者皆 slider visual，**无新 part / joint**；恒定 rod↔beam allow_overlap 生效 |
| lock_screw | rec_caliper_var_lockscrew | `_lock_screw`(knurl for i in range(20)) L279-322 / `_lock_screw_boss` L325-334 / boss visual L417-428 / **`lock_screw` 独立 part** L431-436 / `slider_to_lock_screw` REVOLUTE +Z L491-501 / allow_overlap + expect L539-552/657-674 | eligible if compatible | **删 thumb_roller**；加 `lock_screw_boss` visual（slider saddle 顶 pad）+ **独立 `lock_screw` part**（刻花头 + 短轴）绕 +Z **REVOLUTE**（lower=0 / upper≈6.28）夹紧 carriage；part 数 +1、joint +1；保留 depth_rod |
| simplified_no_rod | rec_caliper_var_norod | `_thumb_lip` L275-299 / thumb_lip visual L373-382 / **无 `_depth_rod` / 无 `_thumb_roller`** / 仅 1 条 slider↔beam allow_overlap L439-445 | eligible if compatible | **删 depth_rod + thumb_roller**；加 `thumb_lip` 模制推唇 visual（slider 下右缘，3 grooves）；slider visual only，无新 part / joint；**去掉 rod↔beam allow_overlap**（无 rod）|

### Slot D：beam_profile（梁截面形态 —— `beam` 与 slider saddle 的截面 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_bar（基线） | rec_..._b08cf719（parent） | `_beam_body`（单 box + `fillet("|Z")`）L81-89 / `_slider_body` saddle（矩形抱梁 box + fillet）L138-153 | eligible if compatible | 扁平矩形 graduated bar（圆角长边）+ slider 矩形 saddle 抱梁截面；基线 |
| channel_beam | rec_dial_caliper_var_channel_beam | I-section 常量 L54-58 / `_beam_body` I-section（上下 flange + web + 底 rail 槽 cut）L89-126 / `_slider_body` I-cavity + gib L175-270（cavity cut L198-212、gib L214-224）/ beam_web + guide_rail visuals L405-427 | eligible if compatible | **I/channel 截面**梁（top/bottom flange + 细 web + 底面 guide rail 槽），slider saddle 改 I-shaped through-cavity + gib 入轨槽；part 树 / joint 与 flat_bar 一致，仅 beam+saddle 截面 mesh 重写（run_tests L626-655 验 I-section + gib 捕获）|

## 槽位图（slot graph）

pattern: parallel_children（root `beam` + 公共 `slider` carriage；四槽的 part / visual 挂到这条骨架上）

```
beam (root; 由 beam_profile 决定截面 mesh: flat_bar 单 box / channel_beam I-section+rail槽)
  │  visuals: beam_body + beam_scale + [vernier→main_scale_ticks] + fixed_jaw(由 jaw_config 形态)
  │
  └──[beam_to_slider: PRISMATIC axis=(1,0,0), origin=(SLIDER_REST_X,0,0), lower=0 / upper=0.150]  ← 骨架，恒定
        │
      slider (carriage; saddle 抱梁——flat 矩形 / channel I-cavity+gib; 镜像 jaws 由 jaw_config 形态)
        │
        ├── [readout slot]  (互斥三选一)
        │     ├─ analog_dial : dial_bezel/face/ticks (slider visual)
        │     │                + needle ──[slider_to_needle: CONTINUOUS axis=+Z, origin=表心]
        │     ├─ digital_lcd : lcd_housing/screen/segments/button_{i} (slider visual)  ← 无 needle joint
        │     └─ vernier_scale: vernier plate+ticks(slider) + main_scale_ticks(beam)  ← 无 needle joint
        │
        ├── [accessory slot]  (互斥三选一)
        │     ├─ rod_and_roller    : depth_rod + thumb_roller (slider visual)  ← 无新 joint
        │     ├─ lock_screw        : lock_screw_boss(slider visual) + depth_rod
        │     │                      + lock_screw ──[slider_to_lock_screw: REVOLUTE axis=+Z, origin=boss顶]
        │     └─ simplified_no_rod : thumb_lip (slider visual)  ← 删 depth_rod，无新 joint
        │
        └── (jaw_config 与 beam_profile 不挂独立 part：jaw polyline 改 fixed_jaw/slider_body 形态；
             beam_profile 改 beam_body/saddle 截面;均为 mesh-profile 维度)
```

接口点位与 joint 语义：
- **骨架 `beam_to_slider`（恒定，每候选都有）**：PRISMATIC axis=(1,0,0)，origin=(SLIDER_REST_X=0.044, 0, 0)，lower=0 / upper=SLIDE_TRAVEL=0.150。mating = slider saddle 抱梁内腔套梁截面（captured prismatic fit，**element-scoped allow_overlap** `slider_body`↔`beam_body`，照搬 parent L452-458）。channel_beam 时 saddle 是 I-cavity + gib 入 rail 槽（同一 captured 语义，allow_overlap 文案换 I-section 版 L543-549）。
- **readout 接口（互斥）**：所有读数件挂在 slider 顶 +Z 面 boss/platform/plate 上。
  - analog_dial：`needle` 独立 part 绕 dial 中心 **CONTINUOUS** axis=(0,0,1)，origin=(dial_cx=0.004, dial_cy=BEAM_H/2+0.004, dial_cz+0.0021)（落在表心，parent L425-433）。bezel/face/ticks 是 slider visual（不动）。
  - digital_lcd：LCD housing/screen/segments/buttons 全 slider visual，**无 joint**（run_tests 断言 articulation 数 == 1）。
  - vernier_scale：游标 plate+ticks fused 进 `slider_body`、主尺 `main_scale_ticks` 是 beam visual，**无 joint**。
- **accessory 接口（互斥）**：
  - rod_and_roller：`depth_rod` 走梁尾通道（**element-scoped allow_overlap** `depth_rod`↔`beam_body`，parent L460-466）；`thumb_roller` slider visual。无新 joint。
  - lock_screw：`lock_screw` 独立 part 绕 +Z **REVOLUTE**，origin=(boss_x=-0.010, boss_y=0, boss_top_z)（落在 boss 顶面，L491-501）；锁丝轴入 boss / slider body 是 captured fastener（**element-scoped allow_overlap** `lock_screw_head`↔`slider_body` 与 ↔`lock_screw_boss`，L539-552；并配 `expect_overlap`/`expect_gap` 守座入 L657-674）。
  - simplified_no_rod：`thumb_lip` slider visual，**无 depth_rod** → builder 须**不发射** rod↔beam allow_overlap（否则 allow_overlap 引用不存在 elem 报错，见 §10 reject）。
- **rest pose**：carriage q=0（量爪「归零」小间隙）；needle q=0（指针指 +X）；lock_screw q=0（未拧紧）。
- **互斥 / 可选 / 派生**：readout 三选一互斥；accessory 三选一互斥；jaw_config 四选一、beam_profile 二选一互斥。**needle part / slider_to_needle 仅 analog_dial 才发射**（digital/vernier 不发射，否则违反「exactly one articulation」断言语义）。**dial_ticks 仅 analog_dial 内存在**（见 §8）。**depth_rod↔beam allow_overlap 仅在 accessory∈{rod_and_roller, lock_screw}（有 rod）时发射**。jaw_config 与 beam_profile 与读数 / 附件正交（任意组合可装配）。

## 每槽位 Module Emits / Interfaces

### Slot A / readout — analog_dial
| emits | 描述 | 来源 |
|---|---|---|
| parts | `needle`（独立 part，可摆）；slider visual: `dial_bezel`/`dial_face`/`dial_ticks`（圆表，不动）| S0 / `_dial_*` L205-275、dial visuals L358-375、`needle` part L397-402 |
| internal joints | `slider_to_needle` CONTINUOUS axis=(0,0,1)，origin=表心，effort=0.5 v=10（mimic 滑动）| S0 / L425-433 |
| upstream interface | dial boss（`_slider_body` boss L189-195）承 bezel 背板；needle 挂表心 | S0 / L189-195, L430 |
| module-local copy | `dial_ticks` `for i in range(50)`（每 5 为 major）—— **仅本 module 存在** | S0 / L236-253 |

### Slot A / readout — digital_lcd
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；slider visual: `lcd_housing`/`lcd_screen`/`lcd_segments`/`button_{i}`（i∈range(2)）| S1 / L212-293, L378-410 |
| internal joints | 无（**删 needle / slider_to_needle**；仅剩骨架 PRISMATIC）| S1 / L435-445（单 joint）|
| upstream interface | slider 顶矩形 platform（`_slider_body` platform L195-201）承 LCD housing | S1 / L195-201 |
| module-local copy | `lcd_segments` digit loop（4 digit × 7-seg-like）+ `button_{i}` for i in range(2) | S1 / L253-280, L401-410 |

### Slot A / readout — vernier_scale
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；beam visual: `main_scale_ticks`；slider visual: vernier plate + 游标 ticks（fused 进 `slider_body`）| S2 / `_main_scale_ticks` L155-198、slider vernier L250-287 |
| internal joints | 无（**删 needle / joint**）| S2 / L395-405（单 joint）|
| upstream interface | 梁顶面承主尺 ticks；slider 顶 plate（`_slider_body` plate L254-259）承游标 ticks | S2 / L254-265 |
| module-local copy | 主尺 `for i in range(total_ticks≈171)`（major/half/minor）+ 游标 `for i in range(10)` | S2 / L178-197, L276-285 |

### Slot B / jaw_config（dual_inside_outside 为例；其余仅换 jaw polyline）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`fixed_jaw`（beam visual）+ slider jaws（fused 进 `slider_body`）| S0 / `_fixed_jaw` L92-135、slider jaws L159-184 |
| internal joints | 无（量爪不动；量测由骨架 PRISMATIC carriage 提供）| — |
| upstream interface | fixed_jaw 焊在 beam −X 头；slider jaws 焊在 carriage 左面（量测面）| S0 / L98-99, L155 |
| 变体 | depth_flat（平 foot，S3 L94-206）/ internal_only（仅上 tip + 窄 root，S4 L97-179）/ step_jaw（compound step，S5 L100-216）| — |

### Slot C / accessory — rod_and_roller
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`depth_rod` + `thumb_roller`（slider visual）| S0 / L278-303, L380-394 |
| internal joints | 无 | — |
| upstream interface | depth_rod 走梁尾通道（rod↔beam allow_overlap）；thumb_roller 挂 slider 下右缘 | S0 / L389-394, L460-466 |
| module-local copy | `thumb_roller` flutes `for i in range(18)` | S0 / L283-291 |

### Slot C / accessory — lock_screw
| emits | 描述 | 来源 |
|---|---|---|
| parts | **`lock_screw` 独立 part**（刻花头 + 短轴，可拧）；slider visual: `lock_screw_boss` + `depth_rod` | S1(lockscrew) / `_lock_screw` L279-322、boss L325-334、part L431-436 |
| internal joints | `slider_to_lock_screw` REVOLUTE axis=(0,0,1)，origin=boss 顶，lower=0 / upper≈6.28 | lockscrew / L491-501 |
| upstream interface | 锁丝轴入 boss / slider body（captured fastener，allow_overlap + expect_overlap/gap）| lockscrew / L539-552, L657-674 |
| module-local copy | `lock_screw` knurl flutes `for i in range(20)` | lockscrew / L296-305 |

### Slot C / accessory — simplified_no_rod
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`thumb_lip`（slider visual，模制推唇 + 3 grooves）；**无 depth_rod / 无 thumb_roller** | norod / `_thumb_lip` L275-299, L373-382 |
| internal joints | 无 | — |
| upstream interface | thumb_lip 挂 slider 下右缘；**builder 须省略 rod↔beam allow_overlap**（无 rod）| norod / L439-445（仅 1 条 allow_overlap）|

### Slot D / beam_profile（flat_bar 为例；channel_beam 换截面 + saddle cavity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`beam_body`（beam visual）+ slider saddle（fused 进 `slider_body`）| S0 / `_beam_body` L81-89、saddle L148-153 |
| internal joints | 无（截面变化不改 joint）| — |
| upstream interface | beam 截面 ↔ slider saddle 内腔（captured prismatic fit）| S0 / L148-153 |
| 变体 | channel_beam：I-section + rail 槽 + saddle I-cavity + gib（S6 `_beam_body` L89-126、saddle L175-270，加 beam_web/guide_rail visual L405-427）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| readout | enum | analog_dial / digital_lcd / vernier_scale | analog_dial | choice | deterministic procedural sampler 选；analog 才发 needle part + CONTINUOUS | Slot A 表 |
| jaw_config | enum | dual_inside_outside / depth_flat / internal_only / step_jaw | dual_inside_outside | choice | sampler 选；改 jaw polyline 形态（互斥）| Slot B 表 |
| accessory | enum | rod_and_roller / lock_screw / simplified_no_rod | rod_and_roller | choice | sampler 选；lock_screw 加 part+REVOLUTE，no_rod 删 depth_rod | Slot C 表 |
| beam_profile | enum | flat_bar / channel_beam | flat_bar | choice | sampler 选；改 beam + saddle 截面 mesh（互斥）| Slot D 表 |
| has_needle（derived） | bool | derived | — | equation | `= (readout == analog_dial)`；控制 needle part + slider_to_needle 是否发射 | Slot A 派生 |
| has_depth_rod（derived） | bool | derived | — | equation | `= (accessory in {rod_and_roller, lock_screw})`；控制 depth_rod visual + rod↔beam allow_overlap 是否发射 | Slot C 派生 |
| palette_style | enum | satin_stainless / polished_chrome / white_dial / black_dial / digital_grey / vernier_steel | satin_stainless | palette | palette only，**不计入 slot_choice**；见下「palette_style 候选」| 各样本材质 |
| beam_len_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 BEAM_LEN（0.205）→ SLIDE_TRAVEL 联动派生；clamp 保细长 | parent L48 |
| beam_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BEAM_H（0.020）→ saddle / jaw root / flange 高联动；clamp | parent L49 |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | equation | `SLIDE_TRAVEL = k · (BEAM_LEN − head_len − carriage_w)`；不独立采样（取值列 derived）| parent L56 |
| jaw_drop_scale | float | [0.85, 1.15] | 1.0 | conditional | 缩放 JAW_DOWN_LEN；仅 jaw_config∈{dual,step}（depth_flat 用短 foot 固定档、internal_only 无下颚）；clamp | parent L52 / depthjaw L54 / step L53 |
| dial_radius_scale | float | [0.90, 1.10] | 1.0 | conditional | 缩放 DIAL_R / DIAL_FACE_R（含 ticks 半径）；仅 readout=analog_dial；clamp 使 bezel ≤ boss | parent L60-61 |
| lcd_size_scale | float | [0.90, 1.10] | 1.0 | conditional | 缩放 LCD_W/H；仅 readout=digital_lcd；clamp 使 screen < housing | digital L64-68 |
| lock_screw_turn_scale | float | [0.85, 1.10] | 1.0 | conditional | 缩放 slider_to_lock_screw upper；仅 accessory=lock_screw；clamp ≤ 2π·1.1 | lockscrew L498-500 |
| (—) | constraint | — | — | inequality | readout 装置 footprint ≤ slider 顶可用面：`max(2·DIAL_R, LCD_W, vernier_plate_W) ≤ carriage_w + boss_margin`；越界回缩 dial_radius/lcd_size | 接口 / clearance |
| (—) | constraint | — | — | inequality | carriage 行程不撞 fixed_jaw 头：`SLIDER_REST_X − head_len ≥ 0` 且 `SLIDER_REST_X + SLIDE_TRAVEL + carriage_w/2 ≤ BEAM_LEN − margin`；越界回缩 slide_travel | parent L56-60 |
| (—) | constraint | — | — | inequality | channel_beam saddle I-cavity + clearance 包络 beam I-section：`wall_t + clr 带` 不穿 flange；违反回缩 clr 或拒采 | channel L185-212 |

**palette_style 候选（4-6 realistic colorways）**：
1. `satin_stainless`（缎面不锈钢梁 STEEL=(0.74,0.76,0.79) + steel_dark slider + chrome bezel + 白表 + 黑针；parent 默认）。
2. `polished_chrome`（梁与 slider 皆抛光 chrome=(0.82,0.84,0.87)，亮面工具卡尺）。
3. `white_dial`（强调白底表盘 DIAL_WHITE=(0.93,0.93,0.90) + 黑刻度 + 黑针，对比读数；analog 偏好）。
4. `black_dial`（黑底表面 + 白刻度反相，工业风；analog 偏好）。
5. `digital_grey`（深灰 housing HOUSING_DARK=(0.22,0.23,0.25) + 绿灰 LCD_BG=(0.18,0.22,0.20) + 背光段 LCD_SEG；digital 偏好）。
6. `vernier_steel`（全钢梁 + 深刻度 SCALE_DARK + 米白游标板 VERNIER_PLATE=(0.88,0.88,0.85)；vernier 偏好）。

> palette_style 仅改材质 RGBA，不进 slot_choice、不改拓扑。3/4 偏好 analog、5 偏好 digital、6 偏好 vernier（sampler 可按 readout 弱加权，但任意 palette × 任意 readout 都合法）。

所有连续 scale 在 `resolve_config` clamp / 派生；每 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度 / 表盘尺寸，**绝不改变 readout / jaw_config / accessory / beam_profile 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级 multiplicity 轴**：核心结构由 4 个固定 named slots（readout / jaw_config / accessory / beam_profile）表达，不暴露任何 `*_count`，也不通过循环复制**模板级** visual/part/joint。
- **module-local 复制（非 slot 轴，模板侧固定循环、不暴露为参数）**：
  - `dial_ticks` `for i in range(50)`（analog_dial 内，每 5 为 major）—— **仅 readout=analog_dial 时存在**（dial_ticks 不在 digital/vernier 下出现）。
  - `thumb_roller` flutes `for i in range(18)`（accessory=rod_and_roller 内）。
  - `lock_screw` knurl flutes `for i in range(20)`（accessory=lock_screw 内）。
  - vernier 主尺 `for i in range(total_ticks≈171)` + 游标 `for i in range(10)`（readout=vernier_scale 内）。
  - digital `lcd_segments` digit loop（4×7-seg-like）+ `button_{i}` `for i in range(2)`（readout=digital_lcd 内）。
  这些是各 module **内部固定循环发射**的刻度 / 刻花 / 段码 visual，数量是 module 内常量（不随 seed 变化、不构成拓扑等价类差异），**不作独立 multiplicity 轴**，因此本类无 N_range / sampling domain。
- **readout 耦合说明**：needle part + `slider_to_needle` CONTINUOUS 是 analog_dial 的 module-internal 装置（has_needle = (readout==analog_dial) 派生），不是 multiplicity；它随 readout enum 选择而存在 / 缺席，不是「N 个 needle」可变轴。

## 拓扑多样性审计

总组合数：readout(3) × jaw_config(4) × accessory(3) × beam_profile(2) = **72**（无 multiplicity 乘子；与 source map 组合数预审 3×4×3×2=72 一致）。

joint-拓扑维度小计：readout 决定 {PRISMATIC+CONTINUOUS（analog）| PRISMATIC only（digital/vernier）}（2 类 joint-topology）× accessory 决定 {无新 joint（rod / no_rod）| +REVOLUTE（lock_screw）}（2 类）= 4 种「joint 拓扑类」；叠 jaw_config(4) × beam_profile(2) 的 part-mesh 维度 → 72 distinct part-tree/mesh 组合。


seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四个 named slot（readout / jaw_config / accessory / beam_profile），经兼容矩阵合法化（本类四轴基本正交，无硬互斥——见下表），派生 has_needle / has_depth_rod，再 `rng.choice` palette_style（按 readout 弱加权），再 uniform 各 conditional / independent 连续 scale（解析 conditional 范围：jaw_drop 仅 dual/step、dial_radius 仅 analog、lcd_size 仅 digital、lock_screw_turn 仅 lock_screw）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §7 的 beam_len_scale / beam_height_scale（independent）、slide_travel_scale（equation 派生自 beam_len）、jaw_drop_scale / dial_radius_scale / lcd_size_scale / lock_screw_turn_scale（conditional，随 slot 选择解析）。采样契约：先采 named slot + palette → 派生 has_needle / has_depth_rod / slide_travel → 采 independent beam_len/height → 解析 conditional scale 范围（按所选 readout/jaw/accessory）→ 用三条 clearance inequality（readout footprint ≤ slider 面、carriage 行程不撞 fixed_jaw 头 / 不出梁尾、channel saddle 包络 I-section）投影 / 回缩。跨部件依赖（readout footprint vs slider 面、行程 vs 梁长 / 头长、saddle cavity vs beam 截面）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 PRISMATIC/CONTINUOUS/REVOLUTE origin、captured allow_overlap 接口或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四 named slot（经兼容矩阵），派生 has_needle/has_depth_rod，`rng.choice` palette（按 readout 弱加权），再 uniform 各 conditional/independent scale | slot_choices_for_seed 含 (readout/jaw_config/accessory/beam_profile) 四对且与 build 一致 |
| compatibility matrix | (1) **readout=digital_lcd / vernier_scale ⇒ 不发射 needle part + slider_to_needle**（has_needle=False）；analog 才发——needle 与 dial 强绑定，digital/vernier 装 needle 会与「prismatic-only 读数」语义冲突且使 dial_ticks/needle 出现在无表盘上（gating）。 (2) **dial_ticks 仅 readout=analog_dial 内发射**（digital/vernier 无表盘则无 dial_ticks）。 (3) **accessory=simplified_no_rod ⇒ 不发射 depth_rod visual 且不发射 rod↔beam allow_overlap**（has_depth_rod=False）；rod_and_roller/lock_screw 才发 depth_rod + 对应 allow_overlap——否则 allow_overlap 引用不存在 elem 报错。 (4) **accessory=lock_screw ⇒ 发射 lock_screw part + slider_to_lock_screw REVOLUTE + lock_screw_head↔(slider_body/lock_screw_boss) 两条 allow_overlap + expect_overlap/gap**；非 lock_screw 不发。 (5) jaw_config 与 beam_profile 与 readout/accessory **正交**（任意组合可装配）；jaw_drop_scale 仅 dual/step 有效（depth_flat 短 foot 固定、internal_only 无下颚）。 (6) channel_beam saddle 必须用 I-cavity+gib（不可与 flat saddle 混用）。 | 无 floating / collision / needle 出现在 digital-vernier / depth_rod allow_overlap 悬引用 / readout footprint 溢出 slider / carriage 撞 fixed_jaw 头或出梁尾 / channel saddle 不抱 I-beam |
| controlled local variation | 7 个 clamped scale（beam_len/height independent、slide_travel equation、jaw_drop/dial_radius/lcd_size/lock_screw_turn conditional），每 build 统一；conditional 随 slot 解析 | 比例变化不破坏 PRISMATIC/CONTINUOUS/REVOLUTE origin、captured allow_overlap、readout 座入、carriage 行程、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 readout/jaw/accessory/beam QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A readout | 3 | yes | yes | analog（PRISMATIC+CONTINUOUS+needle part）/ digital（PRISMATIC only）/ vernier（PRISMATIC only）|
| B jaw_config | 4 | yes | yes | dual / depth_flat / internal_only（删下 blade）/ step（compound）|
| C accessory | 3 | yes | yes | rod_and_roller / lock_screw（+part+REVOLUTE）/ simplified_no_rod（删 rod）|
| D beam_profile | 2 | yes | no | flat_bar parent 基线 + channel_beam（I-section+gib）；fork 池只有这两个真实截面形态，扩容须回 fork 池补造（如圆杆 / 三角杆），不在模板侧虚构 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名，含四对 `("readout", …)/("jaw_config", …)/("accessory", …)/("beam_profile", …)`（连续 scale 不入 slot_choice）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 派生 has_needle=(readout==analog_dial)、has_depth_rod=(accessory∈{rod_and_roller,lock_screw})、slide_travel=equation；各 scale clamp 到声明范围；conditional（jaw_drop/dial_radius/lcd_size/lock_screw_turn）随 slot 解析；三条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating：digital/vernier **不发** needle/slider_to_needle/dial_ticks；no_rod **不发** depth_rod 及其 allow_overlap；lock_screw **才发** lock_screw part+REVOLUTE+两条 allow_overlap+expect；jaw/beam 正交
- 连续 scale clamp 后不破坏 PRISMATIC/CONTINUOUS/REVOLUTE origin / captured allow_overlap / readout 座入 / carriage 行程 / 类别身份
- 关键 joint：骨架 `beam_to_slider` PRISMATIC axis≈(1,0,0)（每候选都有，round==(1,0,0)）；analog `slider_to_needle` CONTINUOUS axis≈(0,0,1)；lock_screw `slider_to_lock_screw` REVOLUTE axis≈(0,0,1)；digital/vernier 时 `len(articulations)`==1（仅 PRISMATIC），analog/rod==2、analog+lock_screw==3
- captured 接口 element-scoped `allow_overlap`：恒定 `slider_body`↔`beam_body`（flat 或 I-section 文案）；条件 `depth_rod`↔`beam_body`（仅 has_depth_rod）；lock_screw `lock_screw_head`↔`slider_body` 与 ↔`lock_screw_boss`（仅 lock_screw，并配 expect_overlap/gap），照搬各样本 run_tests 的 allow_overlap 段
- module-local 循环（dial_ticks×50 / flutes×18 / knurl×20 / vernier ticks / lcd segments / buttons×2）按各 module 固定常量发射，不暴露为参数
- grandfather：所有 captured 接口（saddle 抱梁、rod 走通道、锁丝入 boss）省略 MatingContract，由 `fail_if_articulation_origin_far_from_geometry`（0.015）守 origin + element-scoped allow_overlap 守 captured overlap

## Reject cases

- digital_lcd / vernier_scale 仍发射 `needle` part 或 `slider_to_needle` CONTINUOUS（或发 dial_ticks）→ 与「prismatic-only 数显 / 游标读数」语义冲突、表盘刻度出现在无表盘上；必须 gate（has_needle=(readout==analog_dial)）。
- accessory=simplified_no_rod 仍发射 `depth_rod` 或其 `depth_rod`↔`beam_body` allow_overlap → allow_overlap 悬引用不存在 elem 报错；必须 gate（has_depth_rod）。
- accessory=lock_screw 漏发 `lock_screw` part / `slider_to_lock_screw` REVOLUTE / `lock_screw_head` 两条 allow_overlap → 锁丝漂浮或 captured overlap 未声明 FAIL。
- 把骨架 `beam_to_slider` PRISMATIC 放在非 analog 时仍叫 needle joint，或 needle 用 PRISMATIC mimic 平移 → joint 语义错（needle 是 CONTINUOUS 绕 +Z）。
- carriage rest pose 设成张开量程而非 q=0 小间隙（量爪「归零」）→ current-pose 与 viewer 目检不符（所有样本 lower=0）。
- joint origin 放在梁 / slider 中心或任意点而非真实硬件（SLIDER_REST_X / 表心 / boss 顶）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 saddle 抱梁 / rod 走通道 / 锁丝入 boss 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- channel_beam 用 flat saddle（不抱 I-section / 无 gib 入 rail 槽）→ slider 不捕获梁、悬空；须用 I-cavity + gib（S6 L198-224）。
- jaw_drop_scale 在 internal_only / depth_flat 上误用（删了下颚或固定短 foot）→ conditional 未解析、jaw 形态破坏；jaw_drop 仅 dual/step。
- readout footprint scale 过大致 dial/LCD/游标板溢出 slider 顶面或撞 fixed_jaw 头 → §7 inequality FAIL；须按比例回缩。
- 把连续尺寸 / 颜色 / 材质（palette_style / beam scale）当新 candidate 塞进 slot → 不是结构差异。
- 把「千分尺（螺纹旋进 spindle）/ 直尺（无 carriage）」语义混入 → 出类，本类是 PRISMATIC 滑动 carriage 卡尺。

## 与相邻类别的边界

- 不该混入：**千分尺 / 测微计（micrometer）**——主测量机构是螺纹 thimble REVOLUTE 旋进（spindle/anvil），不是直线 PRISMATIC carriage；马蹄 frame 形态不同（注意：本类 lock_screw 的 REVOLUTE 是「锁丝」附件而非主测量机构，主机构恒为 PRISMATIC——勿与千分尺旋测混淆）。
- 不该混入：**直尺 / 卷尺 / 钢尺（ruler / tape measure）**——纯刻度尺无滑动 carriage / 无量爪 / 无活动测量机构；缺 `beam_to_slider` PRISMATIC 即出类。
- 不该混入：**量块 / 塞规 / 螺纹规（gauge blocks / plug / thread gauge）**——固定量具无 carriage、无读数装置。
- **digital / vernier 仍归本类**：去 needle 后仅剩 PRISMATIC（≥1 非 fixed joint），梁 + slider carriage + 量爪 + 读数装置的卡尺身份完整，是本 slug 的合法 readout 候选而非相邻类别。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) jaw_config 与 beam_profile 建模为 mesh-profile 维度（非串联 slot），readout 与 accessory 才改 part/joint 拓扑；(2) has_needle / has_depth_rod 派生 gating（digital/vernier 删 needle+dial_ticks、no_rod 删 depth_rod+allow_overlap、lock_screw 加 part+REVOLUTE+expect）是否符合 multiplicity/兼容审计期望；(3) beam_profile 仅 2 candidate（flat/channel，fork 池截面词汇窄）是否接受还是要求回 fork 池补造；(4) 无 multiplicity 轴（dial_ticks/flutes/vernier ticks 皆 module-local 固定循环）是否符合期望；(5) Topology target 72<300 的说明是否接受（本小类真实结构上限）；(6) 6 个 palette_style 是否够。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- 共享 helper：`_beam_body`（按 beam_profile 分 flat box / I-section+rail）、`_fixed_jaw` + slider jaw polyline（按 jaw_config 分 dual / flat-foot / 仅上 tip / step compound，fixed 与 slider 镜像复用同一 polyline 逻辑）、`_dial_*`（analog）、`_lcd_*`（digital）、`_main_scale_ticks`/`_tick_mark`/vernier ticks（vernier）、`_thumb_roller`/`_depth_rod`（rod_and_roller）、`_lock_screw`/`_lock_screw_boss`（lock_screw）、`_thumb_lip`（no_rod）。
- captured 接口 allow_overlap：`run_dial_caliper_tests` 里恒补 `slider_body`↔`beam_body`（flat 或 channel I-section 文案，parent L452-458 / channel L543-549）；conditional 补 `depth_rod`↔`beam_body`（仅 has_depth_rod，parent L460-466）；lock_screw 补 `lock_screw_head`↔`slider_body` + ↔`lock_screw_boss` + expect_overlap/gap（lockscrew L539-552, L657-674）。
- 派生 / 门控集中在 `resolve_config`：has_needle、has_depth_rod、slide_travel（equation）、conditional scale 解析（jaw_drop/dial_radius/lcd_size/lock_screw_turn）、三条 clearance inequality 投影。
- channel_beam 注意：slider saddle 必须随 beam_profile 切到 I-cavity + gib（S6 L198-224），并加 beam_web/guide_rail_mark visual（L405-427）；flat_bar 用矩形 saddle（parent L148-153）。两者 PRISMATIC origin/axis 不变。
- 参考模板：`agent/templates/Stationary_Pen.py`（同为「root + parallel/serial children + 互斥主机构槽 + 派生 gating（has_cap）+ module-local 固定循环 visual」结构，本类 readout/accessory 的 has_needle/has_depth_rod gating 可同构改编）；`agent/templates/Accessories_Cushion.py`（parallel_children + 互斥槽 + captured-pin allow_overlap 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/D（parent 基线）| analog_dial + dual_inside_outside + rod_and_roller + flat_bar | rec_..._b08cf719 | `_beam_body` L81-89 / `_fixed_jaw` L92-135 / `_slider_body` L138-202 / `_dial_*` L205-275 / `_thumb_roller` L278-294 / `_depth_rod` L297-303 / `needle` part L397-402 / PRISMATIC L408-418 / CONTINUOUS L425-433 / allow_overlap L452-466 | 骨架 + analog 表盘 + dual 量爪 + rod/roller + flat 梁 + 共享 captured-overlap 范式 |
| S1 | A | digital_lcd | rec_caliper_var_digital | LCD 常量 L63-69 / `_lcd_housing` L212-228 / `_lcd_screen` L231-237 / `_lcd_segments` L240-280 / `_button_pad` L283-293 / visuals L378-410 / 单 PRISMATIC L435-445（删 needle）| 平板数显读数（无 needle joint）|
| S2 | A | vernier_scale | rec_caliper_var_vernier | `_tick_mark` L143-152 / `_main_scale_ticks` L155-198 / slider vernier plate+ticks L250-287 / main_scale visual L352-356 / 单 PRISMATIC L395-405（删 needle）| 游标主尺 + 游标窗读数（无 needle joint）|
| S3 | B | depth_flat | rec_caliper_var_depthjaw | JAW_DOWN_LEN=0.014 L54 / ROD 加长 L68-69 / `_fixed_jaw` 平 foot L94-139 / `_slider_body` 平 foot L142-206 | 短平 registration foot 量爪（depth/step 配准）|
| S4 | B | internal_only | rec_caliper_var_internaljaw | `_fixed_jaw` 仅上 tip + 窄 root L97-126 / `_slider_body` 仅上 tip L129-179（删下 blade）| 内孔量爪（删去下外量 blade，slim 头）|
| S5 | B | step_jaw | rec_caliper_var_stepjaw | STEP 常量 L57-62 / `_fixed_jaw` compound step L100-146 / `_slider_body` compound step L149-216 | step/shoulder compound 量爪 |
| S6 | C | lock_screw | rec_caliper_var_lockscrew | `_lock_screw` L279-322 / `_lock_screw_boss` L325-334 / boss visual L417-428 / `lock_screw` part L431-436 / `slider_to_lock_screw` REVOLUTE L491-501 / allow_overlap+expect L539-552/657-674 | 旋锁螺丝（+独立 part + REVOLUTE +Z + captured fastener）|
| S7 | C | simplified_no_rod | rec_caliper_var_norod | `_thumb_lip` L275-299 / thumb_lip visual L373-382 / 仅 1 条 allow_overlap L439-445（无 depth_rod/thumb_roller）| 简化无 depth rod + 模制 thumb lip（删 rod allow_overlap）|
| S8 | D | channel_beam | rec_dial_caliper_var_channel_beam | I-section 常量 L54-58 / `_beam_body` I-section+rail L89-126 / `_slider_body` I-cavity+gib L175-270 / beam_web+guide_rail visual L405-427 | I/channel 截面梁 + saddle I-cavity + gib 入轨槽 |
