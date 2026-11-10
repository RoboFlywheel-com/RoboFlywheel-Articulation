# Technology_Audio_Device — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Audio_Device` |
| template path | `agent/templates/Technology_Audio_Device.py` |
| test path (optional) | `tests/agent/test_Technology_Audio_Device_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children：body 为 root，grille/controls/handle/antenna 全部挂 body；PLUS multiplicity 轴 button_count） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 (4 origins + 5 forked variants) |
| read_count | 9 |
| read_scope | all 5-star samples in this category (4 origins FULLY read line-by-line; 5 variants structurally verified via grep of loops/joints) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点（每个来源已通读 `revisions/rev_000001/model.py`）：

- **003 wooden tabletop** `rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_...c610b240`：landscape 木盒 `_rounded_cabinet()` (L31-39)，前面 `rounded_cherry_cabinet` mesh；ribbed cream 栅格 = `grille_top/bottom_rail` + `grille_side_rail_{side}` + 15 根 `grille_rib_{i}` loop (L165-190)；两个铬旋钮 `tuning_knob`/`volume_knob` (`add_knob` L258-269)，`cabinet_to_tuning`/`cabinet_to_volume` **REVOLUTE** 轴 -Y (L272-291)；无 handle 无 antenna。dial 刻度/字母/频率块全部 `parent.visual` on cabinet（Rule 1 正例）。
- **001 bronze transistor** `rec_retro-vintage-portable-transistor-radio-bronze-a_...43796658`：landscape bronze `_rounded_box`+`_cabinet_solid` (L61-101)；`_grille_mesh` = **SlotPatternPanelGeometry** ribbed panel (L99-127)；**3 个** knob（`knob_specs` list L369-402，**CONTINUOUS** `cabinet_to_{kname}` 绕 +Z→+Y，off-axis marker）；折叠提手 `_handle_mesh` swept arch + 两 knuckle (L190-217)，`cabinet_to_handle` **REVOLUTE** 轴 X (L411-421)；伸缩天线 `antenna_lower`/`antenna_upper`，`base_to_antenna` **REVOLUTE** swivel (L432) + `antenna_telescope` **PRISMATIC** (L448)。
- **005 tan minimalist** `rec_a-tan-beige-minimalist-retro-portable-radio-a-re_...25291653`：compact landscape `_rounded_box` (L32)；**PerforatedPanelGeometry** `speaker_grille` + `speaker_bezel`(BezelGeometry) + `speaker_backing` (L60-92)；**5 个顶部 push button** `button_{idx}` loop + `body_to_button_{idx}` **PRISMATIC** 下压 (L174-194)；固定拱形提手 = 2 `handle_saddle_{}` + swept `handle_arch`（一个独立 part），`body_to_handle` **FIXED** (L137-173)；伸缩天线 `antenna_swivel` REVOLUTE (L219) + `antenna_extend` PRISMATIC (L246)；折叠 clip `body_to_clip` REVOLUTE (L278)。
- **002 silver CD boombox** `rec_silver-portable-cd-radio-boombox-oval-body-with-_...c648725c`：**oval rounded-square slab** `_body_solid()` 坐地 (L118-155)；单个 recessed perforated speaker（basket+PerforatedPanel grille+surround+bezel+cap，L201-236）；CD 烟熏 dome 盖 `cd_lid` **REVOLUTE** `lid_hinge` (L258-289)；顶面 2 个 domed `_knob` **CONTINUOUS** + 2 `_deck_button` PRISMATIC；前面 recessed tray + **5 个 transport key** `transport_button_{i}` loop **PRISMATIC** (L360-386)；4 `foot_{i}`；rear 天线 swivel REVOLUTE + rod PRISMATIC。
- **变体 (forked anchors)**：`rec_audio_device_var_vertical_bar_grille`（`grille_bar_{i}` 竖条 loop，bar_count=30，L166-180，from 003）；`rec_audio_device_var_dual_stereo_speaker`（`speaker_grille_{i}` i∈{0,1} + per-side basket/surround/bezel/cap，`SPK_X_OFFSET`，from 002）；`rec_audio_device_var_tombstone_body`（`_rounded_cabinet` 立式拱顶 threePointArc，HEIGHT=0.48>WIDTH，from 003）；`rec_audio_device_var_button_count_low`（`button_xs` 3 项）/ `rec_audio_device_var_button_count_high`（`button_xs`=range(8)，8 项）——button_count multiplicity 覆盖 N∈{3,5,8}。

## 核心身份

便携 / 桌面复古收音机族：**retro tabletop radio / transistor radio / portable radio / CD-radio boombox**。物理含义 = 一个坐地或桌面放置的**音频接收/播放主机盒**，正面（-Y）主导一块**扬声器栅格**，加上一组**手动控制界面**（旋钮 / 按键 / 走带键），可选**提手**（便携）与可选**伸缩天线**（接收）。默认成熟域：家用/便携消费级收音机，宽 0.19–0.36 m。root = 单一 body/cabinet；所有硬件挂在它的正面 / 顶面 / 后上角。

**不该混入**：扬声器音箱（passive speaker，无收音/控制界面、无天线、无提手，纯箱体）；耳机 headphones（戴头结构、无箱体正面栅格）；麦克风 microphone（手持/杆状拾音，非盒体）；对讲机/军用电台 field radio（竖握手持、键盘 PTT 主导，不属本类别）。本类别的判据 = **横置/立式盒体 + 正面扬声器栅格 + 旋钮/按键控制 + 复古消费收音机比例**。

## 槽位 + 候选模块表

### Slot ③：body_form（Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| landscape_box | forked_anchor | 003 wooden; 001 bronze; 005 tan | 003 L31-39 `_rounded_cabinet`；001 L61-101 `_rounded_box`/`_cabinet_solid`；005 L32 `_rounded_box` | eligible if compatible | Volumetric Envelope Form：横置圆角填角盒，W>H，front=-Y，坐地 z=0 |
| oval_slab | forked_anchor | 002 boombox | 002 L118-155 `_body_solid` (fillet CORNER_R + 顶/底 edge fillet) | eligible if compatible | Volumetric Envelope Form：软圆角方块 slab（重填角→椭圆读感），W>D>H，坐地 |
| tombstone_vertical | forked_anchor | `rec_audio_device_var_tombstone_body` (from 003) | var L42-61 `_rounded_cabinet`（threePointArc 拱顶，HEIGHT=0.48>WIDTH=0.36） | eligible if compatible | Volumetric Envelope Form：立式高于宽、半圆拱顶（Planar 前轮廓由直墙+弧顶挤出） |

（世界知识可外推 cathedral-pointed / lunchbox-dome 顶型——同 part tree/同前面 interface；本版不进 sampler，留 reviewer。）

### Slot A：speaker_grille_construction（body visual 装饰，非独立 part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| horizontal_ribbed_slats | forked_anchor | 003 wooden; 001 bronze | 003 L134-190（rails + 15 `grille_rib_{i}` loop）；001 L99-127 SlotPatternPanelGeometry | eligible if compatible | 上下 rail + 两侧 rail + N 根横向 rib（loop box），叠成百叶 |
| perforated_hole_mesh | forked_anchor | 005 tan; 002 boombox | 005 L60-92（backing+BezelGeometry bezel+PerforatedPanelGeometry）；002 L201-214 | eligible if compatible | 深色 backing + bezel 框 + 冲孔 PerforatedPanel 面板 |
| vertical_bar_grille | forked_anchor | `rec_audio_device_var_vertical_bar_grille` (from 003) | var L151-180（rails + `grille_bar_{i}` 竖条 loop，bar_count） | eligible if compatible | 同栅格 rails，竖向 bar loop（top-to-bottom） |

### Slot B：speaker_layout（body visual 布局轴，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_center | forked_anchor | 003/001/005/002（全部） | 003 L128-190；002 L201-236 | eligible if compatible | 前面单块居中/偏置栅格 driver |
| dual_stereo | forked_anchor | `rec_audio_device_var_dual_stereo_speaker` (from 002) | var L71 `SPK_X_OFFSET` + L203-236 `speaker_grille_{i}` i∈{0,1} | eligible if compatible | 左右两块对称 driver（同一 grille 构造复制两份） |

### Slot C：control_interface（挂 body 的活动件，**保证每 seed ≥1 non-fixed joint**）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rotary_knob_bank | forked_anchor | 003 wooden; 001 bronze | 003 L258-291（2 knob REVOLUTE 轴 -Y）；001 L369-402（knob_specs → CONTINUOUS +Y，off-axis marker） | eligible if compatible | 下控制条 2–3 旋钮，`knob_{i}` REVOLUTE 绕前面法线 |
| push_button_row | forked_anchor | 005 tan | 005 L174-194 `button_{idx}` loop + `body_to_button_{idx}` PRISMATIC 下压 | eligible if compatible | 顶面一排 N 个 push button（multiplicity 轴 button_count），PRISMATIC -Z |
| transport_key_deck | forked_anchor | 002 boombox | 002 L360-386 `transport_button_{i}` PRISMATIC + L291-320 2 `_knob` CONTINUOUS | eligible if compatible | 前面下条一排 5 走带键 PRISMATIC(+Y 内压) + 2 小旋钮 |

### Slot D：carry_handle（挂 body，可无）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| no_handle | forked_anchor | 003 wooden; 002 boombox | 003（无 handle）；002（无 handle，坐地 boombox） | eligible if compatible | 无提手（桌面/坐地机型） |
| fixed_arched_bail | forked_anchor | 005 tan | 005 L137-173（2 `handle_saddle_{}` + swept `handle_arch`，`body_to_handle` **FIXED**） | eligible if compatible | 刚性拱形提手 = 独立 part，2 鞍座坐顶面 + 连续拱带，FIXED weld |
| folding_revolute_bail | forked_anchor | 001 bronze | 001 L190-217 `_handle_mesh` + L411-421 `cabinet_to_handle` **REVOLUTE** 轴 X | eligible if compatible | 折叠拱提手绕顶面 X 轴 pivot（captured knuckle-over-boss） |

### Slot E：antenna（挂 body 后上角，可无）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | forked_anchor | 003 wooden | 003（无天线） | eligible if compatible | 无天线（桌面机型） |
| telescoping | forked_anchor | 001 bronze; 005 tan; 002 boombox | 001 L432/448；005 L219/246；002 L409/437 | eligible if compatible | base(sleeve) REVOLUTE swivel 轴 X + rod PRISMATIC 伸缩沿 mast |

硬约束满足：每 slot ≥2 candidate（Slot A/C/D 3 个，③ 3 个，B/E 2 个）；无 1-candidate slot；每个 ①/②/multiplicity candidate 均 `forked_anchor` + 真实 `model.py:Lx-Ly`；③ 三个 form 均 source-backed。

## 槽位图（slot graph）

pattern: parallel_children + multiplicity（body 为唯一 root，其余全部为其直接 child 或其 visual）

```
                     body (root, Slot ③ body_form)
                       │  front face -Y  |  top face +Z  |  rear-top +Z/+Y
   ┌───────────────────┼───────────────────┬───────────────────┬──────────────┐
 grille(A)+layout(B)   controls(C)        handle(D)           antenna(E)
 (body.visual,         (parallel children  (child of body:      (child of body)
  no joint)             of body)            FIXED or REVOLUTE)
   ─ ribbed/perf/bar    ─ knobs: REVOLUTE   ─ none               ─ none
   ─ single / dual        绕 -Y(前面法线)   ─ fixed_bail: FIXED  ─ telescoping:
                        ─ buttons: PRISMATIC   (mount_fixed,        base REVOLUTE(swivel,X)
                          -Z (顶面下压 ×N)     MatingContract)      └ rod PRISMATIC(沿 mast +Z)
                        ─ transport: PRISMATIC ─ folding_bail:
                          +Y (前面内压) ×5       REVOLUTE 轴 X
                          + 2 knob REVOLUTE      (captured pivot)
```

接口点位与 joint：

- **grille + speaker_layout**：全为 **body.visual**（Rule 1：不动的装饰不作 part），坐落在 front face(-Y) 平面上方 grille 区，稍嵌入 body（同 part 无 overlap 检查）。
- **controls → body**：并联子件。knob = 圆盘 cap + 隐藏 shaft，`knob_{i}` **REVOLUTE**（rotary_knob_bank）/ **CONTINUOUS**（在 rotary_knob_bank 亦可）绕前面法线 -Y；轴嵌进 body（captured shaft → element-scoped allow_overlap，grandfather，无 mating）。button/transport = cap **PRISMATIC**（下压/内压），cap 嵌进 body → allow_overlap grandfather。pivot 原点落在 front/top 面上（origin-proximity 通过）。
- **handle → body**：`fixed_arched_bail` = **FIXED**，用 `mount_fixed` 单点声明 + **MatingContract**（saddle 底面 flat 坐在 body top 面，welded interface）。`folding_revolute_bail` = **REVOLUTE** 轴 X，knuckle 罩在顶面 boss 上（captured pin → allow_overlap grandfather，无 mating）。
- **antenna → body**：base **REVOLUTE** swivel 轴 X（knuckle 坐 boss，captured → allow_overlap）；rod **PRISMATIC** 沿 mast +Z（rod 嵌入 sleeve bore → allow_overlap sliding bearing）。

互斥/派生：speaker_layout=dual 时 grille 构造复制两份；button_count 仅在 controls=push_button_row 生效；no_handle/none 分支不发 part。**每 seed controls 必发 ≥1 non-fixed joint**（knob REVOLUTE / button PRISMATIC / transport PRISMATIC），满足"≥1 non-fixed joint"硬要求。

## 每槽位 Module Emits / Interfaces

### Slot ③ / body_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，唯一结构根） | 003 L74 / 001 L163 / 002 L170 |
| visuals | `body_shell`(mesh_from_cadquery rounded/oval/tombstone) + 装饰 band/trim/inset（同 part visual）；oval_slab 额外 `foot_{i}` ×4 | 003 L31-39；002 L118-199；tombstone var L42-61 |
| internal joints | 无（root） | — |
| downstream interface | front face 平面 y=-body_d/2（grille/controls 落此）；top face z=body_h（handle/antenna 落此） | 各源 FRONT_Y / Z_TOP |

### Slot A/B / grille + layout
| emits | 描述 | 来源 |
|---|---|---|
| visuals(on body) | ribbed：`grille_top_rail`/`grille_bottom_rail`/`grille_side_rail_{s}` + `grille_rib_{i}` loop；perf：`speaker_backing`+`speaker_bezel`+`speaker_grille`(PerforatedPanel)；bar：rails + `grille_bar_{i}` loop。dual 时后缀 `_{k}` (k∈{0,1}) | 003 L134-190；005 L60-92；bar var L151-180；dual var L203-236 |
| joints | 无（Rule 1 装饰无关节） | — |

### Slot C / control_interface
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotary：`knob_{i}` (i<knob_count∈{2,3})；push：`button_{idx}` (idx<button_count)；transport：`transport_key_{i}`×5 + `knob_{i}`×2 | 003 L258；001 L369；005 L174；002 L360 |
| per-part visuals | knob：`knob_cap`(KnobGeometry) + `knob_shaft` + off-axis `knob_pointer`；button/key：`key_cap`(rounded box) | 001 L378-388；005 L177-182；002 L303-306 |
| internal joints | knob `cab_to_knob_{i}` **REVOLUTE** 轴(0,-1,0)；button `body_to_button_{idx}` **PRISMATIC** 轴(0,0,-1)；transport `body_to_key_{i}` **PRISMATIC** 轴(0,1,0) | 003 L272；005 L184；002 L372 |
| interface | 各 pivot origin 落在 front/top 面（proximity ok）；cap 嵌 body → allow_overlap | 手持电台模式 |

### Slot D / carry_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed_bail/folding_bail：`carry_handle`（1 part：2 saddle/knuckle + swept arch）；no_handle：无 | 005 L137-166；001 L190-217 |
| joints | fixed：`body_to_handle` **FIXED**（mount_fixed + MatingContract saddle↔top）；folding：`body_to_handle` **REVOLUTE** 轴(1,0,0) 0→90° | 005 L164；001 L411 |

### Slot E / antenna
| emits | 描述 | 来源 |
|---|---|---|
| parts | telescoping：`antenna_base`(knuckle+mast sleeve) + `antenna_rod`(rod+tip)；none：无 + body 无 boss | 001 L219-241；002 L390-448 |
| joints | `antenna_swivel` **REVOLUTE** 轴(1,0,0) 0→85°；`antenna_extend` **PRISMATIC** 沿 mast | 005 L219/246；002 L409/437 |
| interface | base knuckle 坐 body `antenna_boss`（allow_overlap）；rod 滑入 mast bore（allow_overlap sliding bearing） | 002 L575-583 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | landscape_box / oval_slab / tombstone_vertical | landscape_box | choice | procedural sampler | ③ 表 |
| grille | enum | horizontal_ribbed / perforated_mesh / vertical_bar | horizontal_ribbed | choice | sampler | A 表 |
| speaker_layout | enum | single_center / dual_stereo | single_center | choice | sampler | B 表 |
| controls | enum | rotary_knob_bank / push_button_row / transport_key_deck | rotary_knob_bank | choice | sampler | C 表 |
| handle | enum | no_handle / fixed_arched_bail / folding_revolute_bail | no_handle | choice | sampler | D 表 |
| antenna | enum | none / telescoping | none | choice | sampler | E 表 |
| button_count | int | [2, 8]（multiplicity，仅 push_button_row） | 5 | conditional | 仅当 controls=push_button_row 生效；否则忽略 | 005 / low/high var |
| knob_count | int | {2, 3}（rotary_knob_bank；transport 固定 2） | 2 | conditional | 依 controls | 003(2)/001(3) |
| palette_style | enum | cherry_wood / tan_beige / silver / bronze_retro / walnut / matte_black | cherry_wood | choice | sampler；≥3，目标 6 | ⑥ |
| body_w | float | [0.19, 0.36] | 0.30 | independent | clamp | ⑤ (0.19 bronze–0.32 tan–0.36 tombstone) |
| body_aspect | float | derived | — | equation | landscape: h=0.55·w, d=0.45·w；oval: h=0.50·w, d=0.68·w；tombstone: h=1.35·w, d=0.60·w | ③×⑤ |
| body_scale | float | [0.92, 1.12] | 1.0 | independent | 整体缩放 clamp | 001/002 |
| grille_cover | float | [0.60, 0.80]（front 面 grille 占比） | 0.70 | conditional | push_button_row 顶置按键时可上探 0.80；下控制条时 ≤0.66 | 005 test 0.74 |
| knob_dia | float | [0.016, 0.054] | 0.030 | independent | clamp | 003(0.054)/001(0.030)/002(0.028) |
| button_travel | float | [0.0016, 0.005] | 0.004 | independent | PRISMATIC 上限 | 005/002 |
| antenna_slide | float | [0.070, 0.106] | 0.090 | independent | rod PRISMATIC 上限 | 001/005/002 |
| (—) | constraint | — | — | inequality | grille 区 z-span 不与 control 条 z-span 重叠（`grille_bottom > strip_top` 或 grille 顶置）；违反回缩 grille_cover | 003 layout test |
| (—) | constraint | — | — | inequality | handle saddle X-span 与 top 按键 X-span 分离（buttons 居中，saddles 靠两侧）；antenna_x 落 top 后右角，避开 saddle | 005 antenna 注释 |

连续尺寸采样契约：先采 independent（body_w, body_scale, knob_dia, button_travel, antenna_slide）→ equation 派生 body_aspect(按 form) → inequality 投影（grille_cover 回缩保证 grille/control 不重叠）→ conditional（button_count/knob_count/grille_cover 依 controls 解析）。全部在 `resolve_config` 求解。

## 7.5 编译预算 / compile budget

自报 **≤22 s/seed**（依据：body = 单次 cadquery fillet mesh ~3-6s；PerforatedPanel/SlotPattern 栅格中孔距 ≥0.009 控制孔数 ~200；ribbed/bar 用 Box loop（廉价）；swept handle 单条 spline；antenna = Cylinder 基元）。sweep `--compile-timeout 120`（>3×）。分档 tessellation：body 英雄面 tolerance 0.0009–0.0015；小特征（knob/antenna/foot）Cylinder radial ≤24-28；PerforatedPanel 孔距不低于 0.009；N 个相同 button/key/rib **复用同一个 Mesh 对象**（一次 `mesh_from_*`，loop 内共享）。超预算先降精度再迭代。

## Multiplicity / Copy Logic

**轴 1（主）：button_count**（顶部 push button bank）
- `count_param`: button_count；`N_range`: [2, 8]（产品域）；sampling domain 权重档：小 N 偏多（3-5 高频），6-8 稀有。
- 已覆盖 N: {3, 5, 8} → `rec_audio_device_var_button_count_low`(3) / 005 baseline(5) / `rec_audio_device_var_button_count_high`(8)。
- copied object = 可按压键帽 `key_cap`(rounded box mesh，复用同一 Mesh)；naming = `button_{idx}` via `for idx, x in enumerate(button_xs)`；placement = 顶面控制条 X 上均匀分布；joint policy = 每键独立 **PRISMATIC** `body_to_button_{idx}`，小下压行程。source/gating = 仅 controls=push_button_row 时生效；其它 controls 该轴不出现（slot_choices 里省略）。

**轴 2（次）：knob_count**（rotary_knob_bank 旋钮数）
- `count_param`: knob_count ∈ {2,3}；N=2 (003)、N=3 (001)；loop `knob_{i}` + `cab_to_knob_{i}` REVOLUTE；transport_key_deck 固定 2 个旋钮。窄域，raw N 编进 slot_choices。

**登记为词汇表（不单独作 multiplicity 轴）**：grille ribs `grille_rib_{i}` / bars `grille_bar_{i}`（数量随 grille 宽度派生，非产品轴）；transport keys `transport_key_{i}`×5（固定）；base feet `foot_{i}`×4（oval_slab 固定）；dial ticks 合并为 body visual 装饰。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | 结构形态：controls(旋钮银/按键排/走带键)、handle(无/固定/折叠)、antenna(无/伸缩) 增减活动 part；全 forked_anchor（003/001/005/002 + variants） |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：button_count[2,8]（小 N 偏多）+ knob_count{2,3} |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE(knob 绕-Y；folding handle 轴X；antenna swivel 轴X)、CONTINUOUS(knob spin 可选)、PRISMATIC(button -Z；transport +Y；antenna telescope +Z)、FIXED(fixed_bail handle)；全 forked_anchor；每种在 sweep 出现（sampler 覆盖） |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | landscape_box / oval_slab / tombstone_vertical 三 Volumetric Envelope（source-backed 003/002/tombstone-var），登记进 slot_choices；world_knowledge 可外推 cathedral/dome（本版未采样） |
| ④ 表面装饰 | 叠加表面细节 | 有 | wood 纹条 `top_grain_{i}`、front trim/bezel band、印刷 dial scale/字母/频率块、logo plate、knob knurl/flute、LCD 面——全部 **host-conformal body.visual**，随 ③(form) 与 ⑤(dims) 派生贴合前面（派生顺序 ③→⑤→④）；record_only + world_knowledge_extrapolation |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | body_w[0.19,0.36]、aspect(按 form 派生)、knob_dia[0.016,0.054]；关节包络：knob REVOLUTE ±π/闭合0；button PRISMATIC [0,0.005] -Z；transport [0,0.0016] +Y；folding handle REVOLUTE [0,π/2] 轴X 上抬翻折；antenna swivel [0,85°] 轴X + telescope [−slide,0] 或 [0,slide]。`motion_test_plan`：harness_motion_qc 全 sampled collision + 每机构 targeted `ctx.pose`（knob pointer 扫掠、button 下压、handle 翻折上抬、antenna 伸缩 tip 升 + swivel 侧摆）。continuous/prismatic 全程不穿模，captured pin 用 element-scoped allow_overlap |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：painted/lacquered wood、plastic(ABS)、metal(chrome/bronze/brass)、cream/ivory 键帽；配色 6：cherry_wood+cream / tan_beige+brass / silver+blue / bronze_retro+black / walnut / matte_black（材质大类覆盖 ≥ ceil(0.5×6)=3） |

收尾自检：`template batch` 0-9 seed 需肉眼可见——三种 body form 拉得开、六种配色都出现、grille 贴前面不悬空、旋钮/按键/提手/天线全程开合不穿模。

## 拓扑多样性审计

总组合数：body_form(3) × grille(3) × speaker_layout(2) × controls(3) × handle(3) × antenna(2) = **324**（× button_count/knob_count multiplicity 数量 → 按 ≥300 report-only 口径观察0 slot choice tuple distinct）。


seed_domain_policy：procedural_first（`config_from_seed` 对每个 seed 含 seed=0 用 `random.Random(seed)` 逐轴采样；seed 0 不特殊，无 curated 表）。

Procedural Sampling / Sweep Plan：`config_from_seed` 依次 rng 采 body_form/grille/speaker_layout/controls/handle/antenna（加权：landscape 偏多、single 偏多、no_handle/none 与有件近均衡）、button_count/knob_count multiplicity、palette_style、连续 scale。`resolve_config` clamp + 依 form 派生 aspect + inequality 回缩 grille_cover + conditional 解析 count。compatibility gating 见下表（无非法组合——任意 form 可配任意 grille/controls/handle/antenna；仅 dual_stereo 在 tombstone 窄体时收窄 offset）。regression overrides：none（首版）。random sweep：0-35 初验，0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 预计达到 ≥300 富类别建议线（324 结构组合 × multiplicity）。report-only，不设门。

Controlled local parameterization：关键连续 scale = body_w、body_scale、knob_dia、button_travel、antenna_slide、grille_cover；全部在 `resolve_config` clamp/派生，受 front-face 布局 inequality、joint range、captured-pin clearance、category identity 约束，不破坏 parallel-children 挂载与 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body 为 root，其余并联；加权 rng.choices 逐 slot + multiplicity + palette + scale | slot_choices_for_seed == build 选择 |
| compatibility matrix | 全组合合法；dual_stereo × tombstone 窄体 → 收窄 SPK offset；no_handle/none 不发 part；button_count 仅 push_button_row | 无 floating/collision/axis/max-N/bulky/optional-child 失败 |
| controlled local variation | body_w/scale/knob_dia/button_travel/antenna_slide/grille_cover clamp+派生 | 比例变化不破坏 interface/clearance/support/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-35 初验，0-999 成熟 | contract failures；axis_realization / |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form (③) | 3 | yes | yes | |
| grille (A) | 3 | yes | yes | |
| speaker_layout (B) | 2 | yes | no | 结构 2 值（单/双 driver），已足 |
| controls (C) | 3 | yes | yes | 保证 non-fixed joint |
| handle (D) | 3 | yes | yes | |
| antenna (E) | 2 | yes | no | 有/无（伸缩链） |

## Validator

- slot_choices_for_seed returns implemented module names（body_form/grille/speaker_layout/controls/handle/antenna + 条件 button/knob 计数）
- config_from_seed 对所有 seed（含 0）用 deterministic procedural sampling
- compatibility gating 阻止非法组合（本类别无硬非法组合；dual/tombstone 收窄）
- 无 regression overrides
- controlled local scale 全在 resolve_config clamp/派生，不破坏 interface/clearance/joint origin/multiplicity
- cross-part 依赖（body_aspect equation、grille_cover inequality、count conditional）在 resolve_config 求解
- 关键接口/关节：controls 每 seed ≥1 non-fixed joint；fixed_bail = FIXED + MatingContract；folding/knob/antenna = captured-pin element-scoped allow_overlap
- 复制件 `button_{idx}`/`knob_{i}`/`transport_key_{i}`/`grille_rib_{i}`/`grille_bar_{i}`/`foot_{i}` 遵循 naming+placement，复用共享 Mesh

## Reject cases

- 把 grille / dial scale / logo / wood grain 做成 FIXED-joint 独立 part（违反 Rule 1；必须 body.visual）
- grille 区与 control 条 z-span 重叠 → 前面挤压穿模（inequality 未回缩 grille_cover）
- oval body 用 Box 近似（违反 Rule 3；必须保 cadquery fillet mesh 的曲面读感）
- 某 seed 只有 FIXED handle 而 controls 无活动件 → 无 non-fixed joint（禁止；controls 恒发活动件）
- knob/antenna/handle captured-pin 用 broad part-level allow_overlap 掩盖真实穿模（必须 element-scoped + 真实过盈理由）
- top push button 与 handle saddle X-span 重叠（未分离布局）→ 顶面 closed-pose overlap
- button_count 复制未 loop（手写多个）或 N 超 [2,8] 未 clamp
- PerforatedPanel 孔距过密 / body tessellation 过细 → 超 22s 编译预算

## 与相邻类别的边界

- 不该混入：**passive speaker / 音箱**（无收音控制界面、无天线、无提手，纯箱体；本类别必须有旋钮/按键控制 + 复古收音机正面栅格身份）
- 不该混入：**headphones / microphone**（戴头/手持拾音结构，非坐地盒体正面栅格）
- 不该混入：**field radio / walkie-talkie**（竖握手持、键盘 PTT 主导、天线为主识别；本类别是横置/立式消费桌面机型，扬声器栅格主导正面）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | scaffold 全部 TODO 已解；6 slot（③body_form/A grille/B layout/C controls/D handle/E antenna）+ button_count/knob_count multiplicity；每 candidate 均 forked_anchor + 真实 model.py:Lx-Ly；每 seed controls 保证 ≥1 non-fixed joint；captured-pin grandfather + fixed_bail MatingContract；≤22s 预算 |

## 模板实现备注（可选）

- 共享 helper：`_rounded_body_mesh`(按 form 分支 cadquery)、`_grille_visuals`(按 construction×layout)、`_emit_knob`/`_emit_buttons`/`_emit_transport`(controls)、`_emit_handle`、`_emit_antenna`；button/key/rib 复用同一 Mesh 对象。
- MatingContract：仅 fixed_arched_bail（saddle 底面 flat ↔ body top 面，mount_fixed）。
- captured-pin element-scoped allow_overlap：knob_shaft↔body_shell；handle knuckle↔handle_boss（folding）；antenna knuckle↔antenna_boss；antenna_rod↔antenna_mast(sleeve)；button/transport cap↔body_shell。
- 暂不进 seed domain：CD 顶盖 REVOLUTE（002 专有，为收窄组合先不作 slot；如需可后加 lid slot）；cathedral/dome 顶型。
