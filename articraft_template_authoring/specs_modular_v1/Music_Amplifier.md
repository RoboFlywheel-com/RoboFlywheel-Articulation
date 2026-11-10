# Guitar Amplifier Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `guitar_amplifier` |
| template path | `agent/templates/Music_Amplifier.py` |
| test path (optional) | `tests/agent/test_guitar_amplifier_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：主体是 `linear_chain`（一个 `body` cabinet 携带一行 `multiplicity` 的 rotary `knob_i` 子件），其中一个 cabinet_form 候选（`mini_half_stack`）又把单一 `body` 拆成 2 节 FIXED 链（`speaker_cabinet` → `head_box`）并把 knobs 重挂到 `head_box`。即 cabinet 结构层（Slot A）可在「单 body」与「2-node FIXED stack」之间切换，knob 行始终是一根模板级 multiplicity 轴（`knob_count`）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category：1 parent + 10 `rec_guitar_amplifier_var_*`，每个 `model.py` 全文逐行已读 |
| samples_adopted_as_module_sources | 11（4 Slot-A + 3 Slot-B + 4 Slot-C，部分样本同时充当多个 slot 的基线 + 2 个 multiplicity N 端点样本） |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

11 个 5★ 样本（1 parent + 10 variants，全部 rating=5，compile=success、workbench-only、≥1 非 fixed joint、明确读作吉他音箱）逐条阅读摘要：

- **P (parent) `rec_marshall-style-mini-guitar-combo-amplifier-black_...34661766`**（全批 fork 母资产，359 行）—— Marshall 风格 mini combo 基线。单一 `body` 部件：rounded black-vinyl `cabinet`（cadquery `_cabinet_solid` L80-L100：top 面切出 gold-panel recess + 前面切出 grille pocket）。visuals：`gold_panel`（top recess，L159-L162）、`power_led`、`speaker_grille`（`PerforatedPanelGeometry` 旋转贴 +X，L169-L181）、`piping_h_*`/`piping_v_*`、`marshall_logo`、`corner_cap_*`、arched `handle`（`_handle_mesh` L103-L138）。Articulation：4× `knob_i`（`KnobGeometry` 针纹 + raised line indicator + off-axis raised pointer tab），`panel_to_knob_i` **CONTINUOUS 绕 +Z**（L224-L262），`MotionLimits(effort=0.3, velocity=8.0)`。run_tests 验证 4 knob、knob 坐 gold_panel（allow_overlap press-fit + expect_contact）、knob 立于 panel 之上、绕 +Z 旋转（pointer 偏置 +Y→quarter-turn 转入 +X）、grille 为薄 +X 朝向板。这是 ★★★★★ 可读性契约样板，三 slot 的基线来源。

- **`rec_guitar_amplifier_var_amp_head`**（389 行）—— 电子单元 head（无音箱段）。Slot A 候选 `head_unit`：`_cabinet_solid`（L79-L105）改成 low/wide/shallow（`CAB_W=0.240/CAB_D=0.140/CAB_H=0.095`，L46-L48），**前面无 grille pocket**，改切浅 vent recess；front 面发射 `front_vent_slots`（`SlotPatternPanelGeometry` 旋转贴 +X，L170-L183）替代 speaker_grille。knobs 仍 `panel_to_knob_i` +Z（L227-L264）。run_tests 显式断言「wider than tall」、「no speaker_grille」、「front_vent_slots 存在且近 +X」。这是 head_unit 候选源，也确立「head 无 grille → grille_style slot 对它 null」的兼容矩阵事实。

- **`rec_guitar_amplifier_var_mini_stack`**（365 行）—— half-stack：**两节 FIXED 链**。下层 root `speaker_cabinet`（grille/piping/logo/caps，L106-L177），上层 `head_box`（gold_panel/handle/knobs，L179-L226），`cabinet_to_head` **FIXED** 挂在 speaker top face（origin `(0,0,SPEAKER_H/2)`，L228-L235）；knobs 经 `head_to_knob_i` CONTINUOUS +Z **重挂到 head_box**（L237-L258）。`_make_knob_geometry` helper（L74-L90）共享 knob 造型。run_tests 断言 head 坐 speaker 顶、两节 stacked、gold_panel 在 head 上、grille 在 speaker 上。这是 mini_half_stack 候选源——本模板最大的结构变更（单 body → 2-node FIXED chain + knob 重 parent）。

- **`rec_guitar_amplifier_var_tilt_back_combo`**（498 行）—— wedge（tilt-back）cabinet。Slot A 候选 `tilt_back_wedge`：`_wedge_solid`（trapezoidal XZ profile extrude，L111-L131），rear 比 front 高（`H_FRONT=0.155/H_REAR=0.195`），front baffle 后倾 ~14°（`BAFFLE_TILT`），top 面 ~18° 斜面（`TOP_ANGLE`，L73-L81）。gold_panel + knobs 坐**斜 top 面**（L196-L203），knob `panel_to_knob_i` CONTINUOUS **绕 top-surface normal `(TOP_NX,0,TOP_NZ)`**（L308-L350），grille 贴 tilted baffle（L217-L234）。run_tests 断言 rear>front 高、grille 在斜 baffle、panel 在斜 top、knob 轴非纯竖直（`abs(ax[0])>0.1 and abs(ax[2])>0.5`）。这是 tilt_back_wedge 候选源，确立「cabinet solid + knob seat/轴随斜面派生」拓扑。

- **`rec_guitar_amplifier_var_front_faceplate`**（409 行）—— Slot B 候选 `front_faceplate`：top 改为平顶（仅 handle），gold_panel 变成 front 面 grille 上方的水平 strip（`PANEL_STRIP_*`，L55-L77；strip emit L197-L200），knob 经 `_build_knob_geometry_forward_facing`（rotate_y(+π/2) 把轴 +Z→+X，L148-L176）**绕 +X 向前**（`panel_to_knob_i` axis=(1,0,0)，L266-L289）。run_tests 断言 knob 向前突出、绕 +X 旋转（rest 偏 +Y→quarter 转入 +Z）、panel 在 grille 之上、top 平。这是 front_faceplate 候选源。

- **`rec_guitar_amplifier_var_angled_chamfer_panel`**（477 行）—— Slot B 候选 `angled_chamfer_facet`：top-front 边切 45° facet（chamfer wedge cut + recess ring，`_cabinet_solid` L105-L153；facet 常量 L64-L92），gold_panel 坐 facet（rotate_y(-FACET_ANGLE)，L208-L220），knob 绕 **facet normal `(0.707,0,0.707)`** CONTINUOUS（L294-L342）。run_tests 断言 panel 在 facet（低于 cabinet top、近前）、knob 向前倾、绕 facet 法向旋转（quarter-turn 改变 Y-extent）。这是 angled_chamfer_facet 候选源。

- **`rec_guitar_amplifier_var_cloth_grille`**（488 行）—— Slot C 候选 `woven_cloth`：speaker_grille 改为**真实表面起伏的 basket-weave 布纹**（`_woven_grille_mesh`：backing + 两族 ±45° 对角 rib，over/under checkerboard，L197-L258；`_add_rotated_box` 直接建 mesh L162-L194；常量 L149-L159），material `grille_cloth`。grille emit L289-L293。run_tests 断言 grille X-extent > 裸 backing 厚度（证明 rib 起伏存在）、覆盖 baffle 开口 ≥80%。cabinet/panel/knob 拓扑不变（top_recessed +Z）。这是 woven_cloth 候选源。

- **`rec_guitar_amplifier_var_dual_round_speakers`**（485 行）—— Slot C 候选 `dual_round_speakers`：粗开放 bar grille 露出**两个 lathe 圆 speaker 锥盆**。新增 `baffle_board`（与 pocket 壁共面，L226-L233）+ `speaker_0/1`（`_speaker_driver` `LatheGeometry` dust-cap/cone/surround/frame profile，L156-L193；`for i` 发射 L235-L244）+ 10 根 `grille_bar_i` 水平条 + `grille_vert_0` 中竖条（L246-L269）。run_tests 断言 speaker 为薄-X-圆-YZ driver、并排（Y 分离 Z 对齐）、在 grille bar 之后、bar 为薄前向横条。这是 dual_round_speakers 候选源（grille 由单板变为 open-bar + 后置 driver 簇）。

- **`rec_guitar_amplifier_var_quad_grille`**（421 行）—— Slot C 候选 `quad_grid`：front grille 拆成 **2×2 四格**。`_add_grille_cell`（每格 `PerforatedPanelGeometry` + 自带 4-bar piping border，L148-L183），`for i in range(4)` divmod 布置（L214-L221），中央十字 `grille_rib_h`/`grille_rib_v` 黑 vinyl 分隔（L223-L236）。run_tests 断言 4 格薄前向板、2×2 网格排布、每格 4 bar piping。这是 quad_grid 候选源。

- **`rec_guitar_amplifier_var_knobs_n2`**（382 行）—— multiplicity 端点 N=2。`KNOB_COUNT=2`、`KNOB_YS = tuple(-0.024 + i*0.048 for i in range(2))`（centered pair，L63-L66），**`PANEL_W` 收窄至 0.100**（L54）适配 2-knob 行；run_tests 断言 `len(knobs)==KNOB_COUNT`、`PANEL_W < CAB_W-0.04`、knob 在 panel Y 范围内。这是 `knob_count` 下界源，证明 panel 宽度须随 N 收缩。

- **`rec_guitar_amplifier_var_knobs_n6`**（376 行）—— multiplicity 端点 N=6。`KNOB_COUNT=6`、`_knob_spacing=0.028`、`KNOB_YS = tuple(-0.070 + i*0.028 for i in range(6))`（L64-L68），**`PANEL_W` 拓宽至 0.165**（L54）容纳 6-knob 行；run_tests 断言 6 knob、行均匀间距且 Y 居中（L289-L301）。这是 `knob_count` 上界源，证明 panel 宽度 + KNOB_YS spread 须随 N 增长重算。

跨样本观察：全部 11 样本共享 `body`(/`speaker_cabinet`+`head_box`) cabinet 根 + `KnobGeometry`（knurled + raised line indicator + off-axis raised pointer tab）knob helper + CONTINUOUS 旋钮关节 + `panel_to_knob`/`head_to_knob` 命名 + `allow_overlap(knob, panel)` press-fit 契约 + `expect_contact`。差异严格落在三个 slot 轴 + 一根 multiplicity 轴：**(A) cabinet_form**、**(B) control_panel_placement**、**(C) grille_style**、**(N) knob_count**。配色高度一致（black vinyl + gold panel + white piping + cream logo + dark grille + metal knob + red LED），为 §7 `palette_style` 提供基线 colorway，其余 colorway 为现实吉他音箱配色派生（仅改 material rgba，不改拓扑/接口）。

## 核心身份

吉他音箱（guitar amplifier，combo / head / 小 stack）：一个**矩形 vinyl/tolex 音箱体**，前面是 speaker baffle（perforated/cloth/open-bar grille，可见或不可见 driver），顶部或前面有一块 control panel（金色或银色），panel 上一行**可转动的旋钮**（gain/volume/tone/reverb…），每个旋钮一个 CONTINUOUS 旋转关节绕 panel 法向。世界系约定：**+X 为前（grille / baffle 面朝 +X）**，+Y 为机宽（左右），+Z 向上；音箱以 cabinet 底近 z=0 着地（mini_stack 以 speaker_cabinet 底着地）。

成熟域：桌面/小型吉他音箱（mini combo、amp head、mini half-stack、tilt-back wedge combo），含 cabinet（或 speaker_cabinet+head_box 两节）、front grille（dark perforated / woven cloth / open-bar+round drivers / 2×2 grid）、control panel（top recess / front strip / chamfer facet / 斜 top）+ 一行 2-6 个 CONTINUOUS 旋钮、white piping、cream logo、corner caps、carry handle。身份强约束：

- **必须**有一个朝 +X 的 front baffle / grille 区（除 `head_unit` 用 front_vent_slots 代替——head 是「无 speaker 段」的电子单元，仍属吉他音箱家族）。
- **必须**有一块 control panel + **一行 ≥2 个 CONTINUOUS 旋钮**（绕 panel 法向旋转，off-axis pointer 使旋转可见）。
- **必须**是带 grille/baffle 的箱体（不是裸喇叭、不是落地音柱）。
- cabinet 形态（combo / head / stack / wedge）、panel 位置、grille 样式、旋钮数可变（Slot A/B/C + N），但「箱体 + grille/baffle + 旋钮行」身份不可缺。

边界（不该混入，详见 §11）：不混入 PA / 主扩声音柱（无旋钮调音面板、不是吉他音箱比例）、不混入 hi-fi/家用书架音箱或落地音箱（无 control panel + 旋钮行、被动箱）、不混入收音机（带刻度盘/天线/扬声器但非乐器放大、比例与 baffle 语义不同）。

## 槽位 + 候选模块表

### Slot A：cabinet_form（主结构槽——音箱体形态；决定 root part 树是单 body 还是 2-node FIXED stack，以及 knob seat/轴的派生面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `full_combo`（基线） | P `rec_marshall-style-mini-guitar-combo-amplifier-black_...34661766` | `model.py:L80-L100`(`_cabinet_solid` top recess+grille pocket)、`L103-L138`(`_handle_mesh`)、`L46-L66`(dims/KNOB consts)、`L224-L262`(knob loop +Z) | eligible if compatible | 一体式 combo：单 `body` rounded black-vinyl box，top 面 recess 坐 gold_panel + 前面 grille pocket 坐 speaker_grille，knobs 绕 +Z；近正方比例（W0.18×D0.10×H0.18）。 |
| `head_unit` | `rec_guitar_amplifier_var_amp_head` | `model.py:L79-L105`(`_cabinet_solid` 无 grille pocket、切 vent recess)、`L46-L48`(low/wide/shallow dims)、`L170-L183`(`front_vent_slots` SlotPatternPanel)、`L227-L264`(knob loop) | eligible if compatible | 电子单元 head：单 `body`，**无 speaker 段**，low/wide/shallow（W0.24×D0.14×H0.095），front 面是 `front_vent_slots`（SlotPatternPanelGeometry）而非 grille。**part 树拓扑不同**（speaker_grille → front_vent_slots，grille_style slot 对它 null）。 |
| `mini_half_stack` | `rec_guitar_amplifier_var_mini_stack` | `model.py:L106-L177`(`speaker_cabinet` root)、`L179-L226`(`head_box` child)、`L228-L235`(`cabinet_to_head` FIXED)、`L237-L258`(`head_to_knob_i`)、`L74-L90`(`_make_knob_geometry`) | eligible if compatible | **两节 FIXED stack**：root `speaker_cabinet`（grille/piping/logo/caps）+ child `head_box`（gold_panel/handle/knobs），`cabinet_to_head` FIXED 挂在 speaker top face；knobs 重 parent 到 `head_box`（`head_to_knob_i`）。**根 part 树从 1 节变 2 节链 + knob 重 parent**——本模板最大结构变更。 |
| `tilt_back_wedge` | `rec_guitar_amplifier_var_tilt_back_combo` | `model.py:L111-L131`(`_wedge_solid` 梯形 XZ extrude)、`L43-L106`(cross-section/TOP_ANGLE/BAFFLE_TILT 派生)、`L196-L234`(panel+grille on 斜面)、`L308-L350`(knob loop 绕 top-surface normal) | eligible if compatible | wedge combo：单 `body`，cabinet solid 改为梯形棱柱（rear 高 front 低，front baffle 后倾 ~14°），gold_panel+knobs 坐 ~18° 斜 top 面，knob 轴 = top-surface normal `(TOP_NX,0,TOP_NZ)`（非纯竖直）；grille 贴 tilted baffle。**cabinet solid + knob seat/轴框架不同**。 |

> Slot A 四候选结构差异充分：`full_combo`/`head_unit`/`tilt_back_wedge` 各自重定义 `_cabinet_solid`/`_wedge_solid` 与 knob seat/轴（+Z / +Z / top-normal），`head_unit` 还删 speaker_grille 改 vent；`mini_half_stack` 把单 body 拆成 2-node FIXED 链并 knob 重 parent。不只是尺寸/颜色差异。

### Slot B：control_panel_placement（控制面板位置槽——gold_panel 的安装面 + knob 关节的 origin/axis 框架；part 名 `gold_panel` 稳定，判别子是 panel mount surface + `panel_to_knob_i` axis 向量）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `top_recessed`（基线） | P `rec_marshall-style-mini-guitar-combo-amplifier-black_...34661766` | `model.py:L159-L162`(gold_panel top recess emit)、`L51-L66`(PANEL/KNOB top consts)、`L224-L262`(`panel_to_knob_i` axis=(0,0,1)) | eligible if compatible | gold_panel 嵌入 top（+Z）面 recess，knobs **绕 +Z 朝上**。经典 Marshall 顶控布局。 |
| `front_faceplate` | `rec_guitar_amplifier_var_front_faceplate` | `model.py:L55-L77`(PANEL_STRIP consts)、`L197-L200`(front strip emit)、`L148-L176`(`_build_knob_geometry_forward_facing` rotate +Z→+X)、`L266-L289`(`panel_to_knob_i` axis=(1,0,0)) | eligible if compatible | gold_panel 是 front（+X）面 grille **上方的水平 strip**，knobs **绕 +X 朝前**；top 改平顶（仅 handle）。knob geometry 须 rotate_y(+π/2) 把轴转向前。**knob 轴框架不同（+X）**。 |
| `angled_chamfer_facet` | `rec_guitar_amplifier_var_angled_chamfer_panel` | `model.py:L64-L92`(facet 常量)、`L105-L153`(`_cabinet_solid` chamfer wedge cut)、`L208-L220`(panel on facet emit)、`L294-L342`(`panel_to_knob_i` axis=(FACET_NX,0,FACET_NZ)≈0.707) | eligible if compatible | top-front 边切 45° facet，gold_panel + knobs 坐 facet，knob **绕 facet normal `(0.707,0,0.707)`**（up-and-forward 朝向演奏者）。**cabinet solid 多一刀 chamfer + knob 轴框架不同（斜法向）**。 |

> Slot B 三候选跨 **+Z / +X / facet-normal** 三种 knob 关节轴框架与三种 panel mount surface（top recess / front strip / chamfer facet），是 knob 关节拓扑（origin/axis）的主驱动槽，结构差异充分（不只是 panel 平移）。

### Slot C：grille_style（前 baffle grille 样式槽——只替换 front baffle 的 grille visual 簇，可附加 driver/baffle_board 子 visual；cabinet/panel/knob 关节不受影响）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `perforated_panel`（基线） | P `rec_marshall-style-mini-guitar-combo-amplifier-black_...34661766` | `model.py:L169-L181`(`speaker_grille` PerforatedPanelGeometry 旋转贴 +X) | eligible if compatible | 单张 dark 穿孔板横跨 front baffle（`PerforatedPanelGeometry` rotate_y(π/2)）。 |
| `woven_cloth` | `rec_guitar_amplifier_var_cloth_grille` | `model.py:L149-L159`(cloth/rib consts)、`L162-L194`(`_add_rotated_box`)、`L197-L258`(`_woven_grille_mesh`)、`L289-L293`(emit) | eligible if compatible | basket-weave 布纹 grille，**真实表面起伏**：backing + 两族 ±45° 对角 rib，over/under checkerboard（`_woven_grille_mesh`）。material `grille_cloth`。**grille mesh 由穿孔板换成自建 weave mesh**。 |
| `dual_round_speakers` | `rec_guitar_amplifier_var_dual_round_speakers` | `model.py:L70-L81`(speaker layout consts)、`L156-L193`(`_speaker_driver` LatheGeometry)、`L226-L244`(`baffle_board`+`speaker_i` loop)、`L246-L269`(open bar grille) | eligible if compatible | 粗开放 bar grille 露出**两个 lathe 圆 driver**：新增 `baffle_board` + `speaker_0/1`（`LatheGeometry` dust-cap/cone/surround/frame）+ 10 `grille_bar_i` + `grille_vert_0`。**新增 driver/baffle 子 visual 簇 + grille 由单板变 open-bar**。 |
| `quad_grid` | `rec_guitar_amplifier_var_quad_grille` | `model.py:L68-L73`(grid consts)、`L148-L183`(`_add_grille_cell`)、`L214-L221`(2×2 cell loop)、`L223-L236`(cross ribs) | eligible if compatible | front grille 拆成 **2×2 四格**：每格 `PerforatedPanelGeometry` + 自带 4-bar piping border（`_add_grille_cell`），中央十字 `grille_rib_h/v` 分隔。**grille 由单板变 4-cell 网格 + 十字 rib**。 |

> Slot C 四候选跨「单穿孔板 / 自建 weave mesh / open-bar+lathe driver 簇 / 2×2 cell 网格」四种 grille 视觉拓扑（其中 dual_round 新增独立 driver/baffle visual），结构差异充分。注意：此 slot 对 `head_unit`（Slot A）不适用（head 无 speaker 段，用 front_vent_slots），见 §9 兼容矩阵。

## 槽位图（slot graph）

pattern = `mixed`（linear_chain body + multiplicity knob 行；其中 mini_half_stack 把 body 拆成 2-node FIXED 链）

```
[Slot A: cabinet_form]
   ·full_combo / head_unit / tilt_back_wedge:   单 root part  [body]
   ·mini_half_stack:  [speaker_cabinet] --FIXED cabinet_to_head (axis n/a, origin (0,0,SPEAKER_H/2))--> [head_box]
         |
         |  (Slot B: control_panel_placement —— gold_panel 安装在 mount surface;
         |   full/head/tilt 在 body, stack 在 head_box)
         |
         +-- [Slot C: grille_style] —— front baffle visual 簇 (perforated / cloth / dual_round / quad)
         |        · 挂在 full/tilt 的 body, stack 的 speaker_cabinet;
         |        · head_unit: 不适用 → 用 front_vent_slots 取代 (null grille)
         |
         +== [multiplicity: knob_count N×]  knob_i  --CONTINUOUS panel_to_knob_i (或 head_to_knob_i)-->
                  · axis = panel mount normal:  +Z(top_recessed) / +X(front_faceplate)
                            / (0.707,0,0.707)(chamfer) / (TOP_NX,0,TOP_NZ)(tilt_back top)
                  · origin = (KNOB_X, KNOB_YS[i], seat_z) on panel surface; i in range(N)
                  · parent = body (full/head/tilt) 或 head_box (mini_stack)
```

接口点位与装配说明：

- **A 内部（mini_half_stack 专有）`speaker_cabinet → head_box`**：`cabinet_to_head` **FIXED**，origin = speaker top face `(0,0,SPEAKER_H/2)`，head_box 帧底坐于该面（head shell `z_offset=HEAD_H/2`，origin 在底）。仅此候选有 A-内部 joint；其余 cabinet_form 单 root 无 A-内部 joint。
- **B：gold_panel 安装面**：`top_recessed` = body top recess（panel 法向 +Z）；`front_faceplate` = body front 面 strip（法向 +X）；`angled_chamfer_facet` = body chamfer facet（法向 ≈0.707,0,0.707）；`tilt_back_wedge` 的原生 top = 斜 top（法向 TOP_NX,0,TOP_NZ）。mini_half_stack 时 panel 安装在 `head_box` 顶（B 默认折到 top_recessed，见 §9 排除）。
- **C：grille 安装面**：front baffle（+X 面），grille visual（及 dual_round 的 baffle_board/speaker_i）与 pocket 壁共面以保 mesh 连通。head_unit 时该面是 vent recess（front_vent_slots），grille_style null。
- **knob 行（multiplicity）`{body|head_box} → knob_i`**：`panel_to_knob_i`（full/head/tilt，parent=body）/ `head_to_knob_i`（mini_stack，parent=head_box），**CONTINUOUS**，origin `(KNOB_X, KNOB_YS[i], seat_z)`（panel 表面，seat 略嵌入 press-fit），axis = panel mount normal（由 Slot B + A=tilt 派生）。每 knob `allow_overlap(knob_i, gold_panel)` + `expect_contact`。
- **互斥 / 派生关系**：Slot A 决定 root part 树（单 body vs 2-node stack）与 knob parent + knob 轴的「斜面派生」（tilt_back）。Slot B 决定 gold_panel mount surface + knob 轴 origin/向量。Slot C 决定 front grille visual 簇（对 head_unit null）。knob 关节 axis 由 (A=tilt_back? top-normal : B 的 mount normal) 派生——**必须在 resolve_config 统一解析**，不可硬编码。`KNOB_YS` spread 与 `PANEL_W` 由 N 派生（multiplicity 适配）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `full_combo`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（cabinet + gold_panel + power_led + speaker_grille + piping_* + marshall_logo + corner_cap_* + handle） | P / model.py:L154-L222 |
| internal joints | 无（cabinet 内部为 visual 组） | — |
| upstream interface | root part；以 cabinet 底近 z=0 着地 | P / model.py:L80-L100, L220-L222 |
| downstream interface | top recess 供 Slot B；front pocket 供 Slot C；panel 表面供 knob 行 | P / model.py:L80-L100 |

### Slot A / module `head_unit`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（low/wide/shallow cabinet + gold_panel + `front_vent_slots` + piping_* + logo + caps + handle；**无 speaker_grille**） | `rec_guitar_amplifier_var_amp_head` / model.py:L154-L225 |
| internal joints | 无 | — |
| upstream interface | root part；着地 | model.py:L79-L105 |
| downstream interface | top recess 供 Slot B；**front 面为 vent（Slot C null）** | model.py:L170-L183 |

### Slot A / module `mini_half_stack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `speaker_cabinet`（root：cabinet_shell + speaker_grille + piping + logo + caps）+ `head_box`（child：head_shell + gold_panel + power_led + handle_strap/legs） | `rec_guitar_amplifier_var_mini_stack` / model.py:L106-L226 |
| internal joints | `cabinet_to_head`（FIXED，origin `(0,0,SPEAKER_H/2)`） | model.py:L228-L235 |
| upstream interface | root = speaker_cabinet，以其底着地；head_box 帧底坐 speaker top face | model.py:L182-L185, L228-L235 |
| downstream interface | grille/piping 在 speaker_cabinet（Slot C）；gold_panel 在 head_box top（Slot B 折到 top_recessed）；knob 行 parent = head_box（`head_to_knob_i`） | model.py:L188-L194, L237-L258 |

### Slot A / module `tilt_back_wedge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（wedge cabinet + gold_panel on 斜 top + power_led + speaker_grille on tilted baffle + piping + logo + caps + handle） | `rec_guitar_amplifier_var_tilt_back_combo` / model.py:L186-L306 |
| internal joints | 无 | — |
| upstream interface | root part；wedge 底着地 | model.py:L111-L131 |
| downstream interface | 斜 top（法向 TOP_NX,0,TOP_NZ）供 Slot B/knob；tilted baffle 供 Slot C；knob 轴随 top-normal 派生 | model.py:L73-L106, L308-L350 |

### Slot B / module `top_recessed`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gold_panel`（top recess 板）+ `power_led` | P / model.py:L159-L167 |
| internal joints | 无（knob 关节归 multiplicity 轴） | — |
| upstream interface | 嵌入 cabinet top recess（press-fit） | P / model.py:L80-L90, L159-L162 |
| downstream interface | panel 表面 (z=PANEL_GOLD_Z) 供 knob 行，knob 轴 = +Z | P / model.py:L224-L262 |

### Slot B / module `front_faceplate`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gold_panel`（front 水平 strip）+ `power_led`（front） | `rec_guitar_amplifier_var_front_faceplate` / model.py:L197-L205 |
| internal joints | 无 | — |
| upstream interface | 贴 cabinet front 面 grille 上方；top 改平顶 | model.py:L91-L107, L197-L200 |
| downstream interface | panel front 表面供 knob 行，knob geometry rotate_y(+π/2)，knob 轴 = +X | model.py:L148-L176, L266-L289 |

### Slot B / module `angled_chamfer_facet`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gold_panel`（坐 facet）+ `power_led`（facet） | `rec_guitar_amplifier_var_angled_chamfer_panel` / model.py:L208-L235 |
| internal joints | 无 | — |
| upstream interface | cabinet top-front 切 45° facet（`_cabinet_solid` chamfer cut + recess ring，press-fit 嵌入 facet） | model.py:L105-L153, L208-L220 |
| downstream interface | facet 表面供 knob 行，knob geometry rotate_y(+FACET_ANGLE)，knob 轴 = facet normal (0.707,0,0.707) | model.py:L294-L342 |

### Slot C / module `perforated_panel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`speaker_grille`（PerforatedPanelGeometry）为 cabinet/speaker_cabinet 的 visual | P / model.py:L169-L181 |
| internal joints | 无 | — |
| upstream interface | rotate_y(π/2) 贴 front baffle，嵌入 grille pocket | P / model.py:L169-L181 |
| downstream interface | 无 | — |

### Slot C / module `woven_cloth`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`speaker_grille`（`_woven_grille_mesh` backing + 2 rib families）为 visual，material `grille_cloth` | `rec_guitar_amplifier_var_cloth_grille` / model.py:L197-L258, L289-L293 |
| internal joints | 无 | — |
| upstream interface | 贴 front baffle；rib over-relief 须 < pocket 深度 | model.py:L149-L159 |
| downstream interface | 无；logo 坐 cloth front 面（backing + over-rib relief） | model.py:L316-L319 |

### Slot C / module `dual_round_speakers`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 articulated part：`baffle_board` + `speaker_0/1`（LatheGeometry driver）+ `grille_bar_i`(×10) + `grille_vert_0` 皆 visual | `rec_guitar_amplifier_var_dual_round_speakers` / model.py:L226-L269 |
| internal joints | 无（driver 为 static visual，不旋转） | — |
| upstream interface | baffle_board 与 pocket 壁共面（mesh 连通）；speaker 在 grille bar 之后 | model.py:L226-L244 |
| downstream interface | 无 | — |

### Slot C / module `quad_grid`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`grille_cell_0..3` + 每格 `cell_pipe_{i}_{h,v}{k}` + `grille_rib_h`/`grille_rib_v` 皆 visual | `rec_guitar_amplifier_var_quad_grille` / model.py:L148-L236 |
| internal joints | 无 | — |
| upstream interface | 4 cell 嵌入 front pocket，十字 rib 黑 vinyl 分隔（与 cabinet 同 material 保连通） | model.py:L214-L236 |
| downstream interface | 无 | — |

### Multiplicity / module `knob_row`（knob_count 轴）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knob_{i}`（i∈range(N)，KnobGeometry knurled + raised line indicator + off-axis pointer tab） | P / model.py:L224-L250 |
| internal joints | `panel_to_knob_{i}`（或 `head_to_knob_{i}`，mini_stack），CONTINUOUS，axis=panel mount normal，MotionLimits(0.3, 8.0) | P / model.py:L254-L262；stack model.py:L250-L258 |
| upstream interface | knob 坐 gold_panel 表面（seat 略嵌入，`allow_overlap(knob_i, gold_panel)` + `expect_contact`） | P / model.py:L253-L262 |
| downstream interface | 无（终端活动件） | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `cabinet_form` | enum | `full_combo` / `head_unit` / `mini_half_stack` / `tilt_back_wedge` | `full_combo` | choice | deterministic procedural sampler；决定 root part 树 + knob parent + knob 轴斜面派生 | Slot A 表 |
| `control_panel_placement` | enum | `top_recessed` / `front_faceplate` / `angled_chamfer_facet` | `top_recessed` | choice | sampler；决定 gold_panel mount surface + knob 轴 origin/向量；受 A gate（见 §9） | Slot B 表 |
| `grille_style` | enum | `perforated_panel` / `woven_cloth` / `dual_round_speakers` / `quad_grid` | `perforated_panel` | choice | sampler；A=head_unit 时 null（用 front_vent_slots） | Slot C 表 |
| `knob_count` (N) | int | [2, 6] | 4 | conditional | multiplicity 轴；加权采样（见 §8）；上限随 PANEL_W 可行域 clamp | n2/n6 sources |
| `palette_style` | enum | `black_vinyl_gold` / `tweed_brown` / `red_tolex_silver` / `blonde_oxblood` / `british_blue_gold` / `silver_face_chrome` | `black_vinyl_gold` | choice | 每 seed 采样 colorway；仅改 material rgba，不改拓扑/尺寸/接口 | P mats L144-L151（+ 现实音箱配色派生） |
| `overall_size_scale` | float | [0.85, 1.20] | 1.0 | independent | 各向同性整体尺度；clamp。`head_unit` 偏宽矮、`tilt_back` 偏大、combo 居中 | P envelope L46-L48；head L46-L48 |
| `cabinet_aspect_scale` | float | [0.88, 1.15] | 1.0 | independent | cabinet 高宽比（H/W）微调；clamp；不改 grille/panel 接口 | P L46-L48；tilt H_FRONT/H_REAR L44-L48 |
| `panel_width_scale` | float | [0.90, 1.12] | 1.0 | independent | gold_panel Y 跨度基准缩放；clamp（再由 N 派生最终 PANEL_W） | P PANEL_W L54；n6 L54 |
| `knob_diam_scale` | float | [0.85, 1.15] | 1.0 | independent | knob 直径缩放；clamp；影响 KNOB_YS 最小间距下限 | P KNOB_DIAM L63 |
| `baffle_inset_scale` | float | [0.90, 1.10] | 1.0 | independent | grille pocket / baffle 开口相对 cabinet 的内缩；clamp；不破 piping 框 | P grille pocket L94-L99 |
| `PANEL_W` (effective) | float | derived | — | equation | `= clamp(base_PANEL_W * panel_width_scale, KNOB_SPAN(N)+2*margin, CAB_W - 2*edge)`；其中 `KNOB_SPAN(N) = (N-1)*knob_pitch + KNOB_DIAM` | n2 L54；n6 L54, L67-L68 |
| `KNOB_YS` | tuple | derived | — | equation | `= centered even spacing for i in range(N)`：`KNOB_YS[i] = -KNOB_SPAN/2 + i*knob_pitch`，居中 Y=0 | P L65；n6 L68 |
| `knob_axis` | vec3 | derived | — | equation | `= top-surface normal if A=tilt_back_wedge else B-mount normal`（+Z/+X/facet）；不独立采样 | tilt L348；chamfer L340；front L287 |
| `knob_seat` (origin) | vec3 | derived | — | equation | `= panel surface point + mount_normal*(panel_thick - embed)`（press-fit 略嵌入），随 A/B 派生 | P L253-L259；chamfer L327-L339 |
| (—) | constraint | — | — | inequality | **knob 行装得下**：`KNOB_SPAN(N) + 2*edge_margin ≤ PANEL_W_effective` 且 `PANEL_W_effective ≤ CAB_W - 2*0.015`。违反时先缩 `knob_pitch` 到 knob 不相邻穿模下限（`≥ KNOB_DIAM + 0.004`），仍不行则拒绝该 N 或回缩 `knob_count` 上限。 | n2 L305-L306；n6 L289-L301 |
| (—) | constraint | — | — | inequality | **相邻 knob 不穿模**：`knob_pitch ≥ KNOB_DIAM*knob_diam_scale + 0.004`。违反时增大 knob_pitch（连带放宽 PANEL_W）或减小 knob_diam_scale。 | P KNOB_YS L65；n6 spacing L67 |
| (—) | constraint | — | — | inequality | **grille 起伏 / driver 深度 ≤ pocket 深度**（C=woven_cloth rib relief 或 dual_round speaker depth 不得超出 baffle pocket）。违反时回缩 relief/depth 或加深 pocket。 | cloth L155-L159；dual SPEAKER_DEPTH L72 |
| (—) | constraint | — | — | inequality | **着地**：缩放后 `min_z ∈ [-0.004, 0.006]`，cabinet（或 mini_stack 的 speaker_cabinet）底着地。违反时按 overall_size_scale 回缩。 | P L220-L222；stack L174-L177 |

`palette_style` colorway 取值（rgba 仅作示意，下游模板落实；`black_vinyl_gold` = 5★ 样本唯一实际出现配色，其余为现实吉他/贝斯音箱配色派生，仅改 material rgba，拓扑/尺寸/接口完全不变）：
- `black_vinyl_gold`（= P 基线，全 11 样本配色）：vinyl 黑 (0.07,0.07,0.08)、panel 金 (0.86,0.62,0.18)、grille 暗 (0.10,0.10,0.11)、piping 白 (0.92,0.92,0.90)、logo cream (0.95,0.93,0.86)、knob 金属 (0.78,0.78,0.80)、LED 红 (0.85,0.12,0.10)、trim 黑 (0.04,0.04,0.05)。
- `tweed_brown`（Fender 复古 tweed）：cabinet tweed 浅黄褐 (0.74,0.62,0.38)、panel 暗铬 (0.55,0.55,0.57)、grille 棕 oxblood-cloth (0.30,0.16,0.12)、piping 暗棕条 (0.32,0.22,0.12)、knob 黑胶 (0.10,0.10,0.11)、logo gold-script (0.78,0.60,0.22)。
- `red_tolex_silver`（红 tolex + 银面板）：cabinet 红 tolex (0.45,0.06,0.07)、panel 银 (0.80,0.81,0.83)、grille 银灰布 (0.55,0.55,0.55)、piping 白、knob chrome (0.82,0.83,0.85)、logo 白。
- `blonde_oxblood`（Fender blonde + oxblood grille）：cabinet 米白 blonde (0.80,0.74,0.58)、panel 暗铬 (0.50,0.50,0.52)、grille oxblood (0.34,0.12,0.10)、piping 暗棕、knob 黑、LED 红。
- `british_blue_gold`（英式蓝 vinyl + 金面板）：cabinet 深蓝 (0.10,0.16,0.34)、panel 金 (0.86,0.62,0.18)、grille 暗灰布 (0.18,0.18,0.20)、piping 白、knob 金属、logo cream。
- `silver_face_chrome`（silver-face + chrome 控制面板）：cabinet 黑 vinyl (0.07,0.07,0.08)、panel 亮银 (0.85,0.86,0.88)、grille 银蓝布 (0.40,0.43,0.50)、piping 银条 (0.70,0.70,0.72)、knob chrome、LED 蓝绿 (0.10,0.55,0.55)。

## Multiplicity / Copy Logic

本模板有 **1 根模板级复制数量轴**：`knob_count`（control panel 上的旋钮行）。

- `count_param`：`knob_count`（N）
- `N_range`：**[2, 6]**（本小类产品域：mini/桌面吉他音箱常见 2-6 个旋钮——音量/增益/三段 EQ/混响）。5★ 已覆盖端点 {2, 4, 6}（n2 / parent(=4) / n6）。测试偏小 N（2-4），产品全程 [2,6]。
- sampling domain（权重档）：**3-4 旋钮最高频**（典型 mini combo），2 与 5-6 次频，**>6 不采**（panel 宽度 / CAB_W 上限封顶——本小类无更大 N 的真实形态）。建议权重 ~ {2:0.18, 3:0.26, 4:0.28, 5:0.16, 6:0.12}（小 N 偏多、尾部稀有）。
- copied object：每个 knob = 一个 `knob_i` part，由共享 `KnobGeometry`（knurled count=28 + raised line indicator + recessed_disk top + off-axis raised pointer tab，press-fit base）构建，每复制件几何相同。
- naming：`knob_{i}` part/visual + `panel_to_knob_{i}` 关节（mini_half_stack 时 `head_to_knob_{i}`），i ∈ range(N)。
- placement：gold_panel 上沿 Y 的居中均匀一行，`KNOB_YS[i] = -KNOB_SPAN/2 + i*knob_pitch`（居中 Y=0），固定 `KNOB_X` / panel 表面 seat_z；panel 表面随 Slot B（top/front/facet/斜top）派生。
- joint policy：**CONTINUOUS** 旋转绕 panel mount 法向（+Z top / +X front / facet-normal chamfer / top-surface-normal wedge），`MotionLimits(effort=0.3, velocity=8.0)`；每 knob `allow_overlap(knob_i, gold_panel)`（press-fit seat）+ `expect_contact`。
- source/gating：N=2 源 `rec_guitar_amplifier_var_knobs_n2`（PANEL_W 收窄 0.100）、N=6 源 `rec_guitar_amplifier_var_knobs_n6`（PANEL_W 拓宽 0.165 + respaced）。**`PANEL_W` 与 `knob_pitch` 必须随 N 在 `resolve_config` 派生/clamp**（§7 两条 inequality），不可让 knob 行溢出 panel 或相邻穿模。

## 拓扑多样性审计

总组合数（slot-only，含兼容矩阵 gating）：
- `full_combo`：B(3) × C(4) = 12
- `tilt_back_wedge`：B(3) × C(4) = 12
- `mini_half_stack`：B(1：仅 top_recessed) × C(4) = 4
- `head_unit`：B(3) × C(1：vent，grille null) = 3

合法 (A,B,C) 拓扑类 = 12+12+4+3 = **31**。计入 multiplicity N 采样档（{2,3,4,5,6} → 5 档；最少按 5★ 已验 {2,4,6} 3 档）：**31 × 3 = 93**（按 5 档则 155）distinct 拓扑组合。原始未 gate 乘积 = 4×3×4×3 = 144，减去排除项（见兼容矩阵）。


理由：31 个 slot 组合即远超 10——Slot A 跨「单 body / 2-node FIXED stack / wedge solid / head(无 grille)」四种 root 拓扑，Slot B 跨「+Z / +X / facet-normal」三种 knob 关节轴框架，Slot C 跨「单板 / weave mesh / open-bar+lathe driver 簇 / 2×2 网格」四种 grille 视觉拓扑，knob_count 又改 knob part/joint 数量。即便 palette_style 与连续 scale 不计入 topology 等价类，单 slot 组合即达 31 distinct。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG 加权采样：先选 `cabinet_form`（A，4 选 1，可对 `full_combo` 经典基线略加权），按 A gate 解析 `control_panel_placement`（B）合法集（A=mini_half_stack 时 B 强制 `top_recessed`），按 A gate 解析 `grille_style`（C，A=head_unit 时 C=null/vent），再加权采样 `knob_count`（N，小 N 偏多）、`palette_style` 与所有 `independent` 连续 scale，按 `equation` 派生 `PANEL_W`/`KNOB_YS`/`knob_axis`/`knob_seat`，最后用 §7 inequality（knob 行装得下、相邻不穿模、grille 起伏/driver 深度、着地）投影/回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定 `[(cabinet_form,…),(control_panel_placement,…),(grille_style,…),(knob_count,N)]`（连续 scale 不进 slot_choices）。兼容矩阵 gating 在 `resolve_config` 解析，不留到 builder 失败。`seed=0` 不特殊。无需 regression overrides（11 个 5★ 源齐全、各格已收敛）；若 sweep 暴露特定坏组合再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别 slot 池约束封顶在 31（slot 组合上限，knob_count 另乘 N 档）。本类别 grille/panel/cabinet 词汇表有限（A 4 + B 3 + C 4 + 1 multiplicity 轴），31 个拓扑类 × N 档 × palette(6) × 连续 scale 谱共同提供视觉/比例多样性。若 1000-seed 实测 distinct <300，属类别固有 slot 上限（31×N），非建模缺陷——可在审核记录注明。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization（初版模板应含的关键连续 scale）：`overall_size_scale [0.85,1.20] independent`、`cabinet_aspect_scale [0.88,1.15] independent`、`panel_width_scale [0.90,1.12] independent`、`knob_diam_scale [0.85,1.15] independent`、`baffle_inset_scale [0.90,1.10] independent`；派生 `PANEL_W = clamp(base*panel_width_scale, KNOB_SPAN(N)+2*margin, CAB_W-2*edge)`（equation+inequality）、`KNOB_YS`（equation）、`knob_axis`/`knob_seat`（equation，随 A/B 派生）。遵循连续尺寸采样契约：先采 independent → 派生 equation → 用 §7 inequality（knob 装得下/不穿模/grille 深度/着地）投影回缩 → conditional（knob_count 上限随 PANEL_W 解析）。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（gold_panel mount surface、knob seat 随 A/B 派生、mini_stack 的 cabinet_to_head FIXED 面）、MatingContract（knob press-fit 捕获 gold_panel、grille 嵌入 pocket）或 multiplicity（knob_count 行宽适配）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→(B gate)→(C gate)→N→palette→连续 scale；加权 enum + 加权 N + 派生/clamp | `slot_choices_for_seed` 与 build choices 一致（含 N） |
| compatibility matrix | A=mini_half_stack × B∈{front_faceplate, angled_chamfer_facet} **排除**（head_box 是独立上箱，front/chamfer faceplate 与上箱框架冲突，需 panel 重锚到 head_box 面——未采样；fallback → top_recessed）。A=head_unit × C=任意 grille **null**（head 无 speaker 段，用 front_vent_slots，C 不适用）。其余 (A,B,C) 默认合法。 | 无 floating / 无穿模 / knob 行不溢出 panel / grille 嵌 pocket / 着地 / mini_stack 两节相接 |
| controlled local variation | 5 个 independent scale + 派生 PANEL_W/KNOB_YS/knob_axis/seat；全部 clamp + 4 条 inequality 回缩 | 比例随机但 knob 在 panel、轴向正确、grille 不超 pocket、着地、吉他音箱身份不破 |
| regression overrides | none（11 个 5★ 源各格已收敛，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（knob 行/grille 深度/着地 + mini_stack 接缝） |、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A cabinet_form | 4 | yes | yes | combo / head / stack / wedge |
| B control_panel_placement | 3 | yes | yes | top / front / chamfer |
| C grille_style | 4 | yes | yes | perforated / cloth / dual_round / quad |
| (multiplicity) knob_count | N∈[2,6] | — | — | 1 根 multiplicity 轴，非 slot 候选 |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{full_combo, head_unit, mini_half_stack, tilt_back_wedge}、B∈{top_recessed, front_faceplate, angled_chamfer_facet}、C∈{perforated_panel, woven_cloth, dual_round_speakers, quad_grid}、N∈[2,6]）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + N + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：A=mini_half_stack 的 B 强制 top_recessed（front/chamfer fallback）；A=head_unit 的 C=null（front_vent_slots）。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（overall_size/cabinet_aspect/panel_width/knob_diam/baffle_inset）在 `resolve_config` clamp/派生；4 条 inequality（knob 行装得下、相邻 knob 不穿模、grille 起伏/driver 深度 ≤ pocket、着地）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：knob press-fit 捕获 `gold_panel`（`allow_overlap(knob_i, gold_panel)` + expect_contact）；grille visual（及 dual_round 的 baffle_board）嵌入 front pocket 且与壁共面（mesh 连通）；mini_half_stack 的 `head_box` 经 `cabinet_to_head` FIXED 坐 speaker top face。
- 关键 joint type/axis/range：knob 行 = N× CONTINUOUS 绕 panel mount 法向（+Z/+X/facet/top-normal），MotionLimits(0.3, 8.0)；mini_half_stack 的 `cabinet_to_head` = FIXED。
- copied object 命名/placement：`knob_{i}`（i∈range(N)）+ `panel_to_knob_{i}`（或 `head_to_knob_{i}`）；KNOB_YS 居中均匀，PANEL_W 随 N 派生 clamp。
- 吉他音箱身份不变量：朝 +X 的 front grille/baffle（head_unit 用 front_vent_slots）；≥2 个 CONTINUOUS 旋钮成一行；箱体（combo/head/stack/wedge）+ control panel + 旋钮行齐备；以 cabinet 底着地。
- A=head_unit：断言无 speaker_grille、有 front_vent_slots、wider-than-tall；A=mini_half_stack：断言 head_box 坐 speaker top、gold_panel 在 head_box、grille 在 speaker_cabinet、knob parent=head_box；A=tilt_back_wedge：断言 knob 轴非纯竖直（abs(ax[0])>0.1 且 abs(ax[2])>0.5）。

## Reject cases

- 无 front grille / baffle 也无 front_vent_slots（front 面全裸）——丢失音箱 baffle 身份。
- 无 control panel 或旋钮 < 2，或旋钮非 CONTINUOUS（做成 fixed 装饰旋钮）——丢失「可调音箱」语义。
- knob 行溢出 gold_panel（KNOB_SPAN(N) > PANEL_W）或相邻 knob 穿模（knob_pitch < KNOB_DIAM + 间隙）——N 适配未做 / PANEL_W 未随 N 派生。
- knob 关节 axis 未随 Slot B（+Z/+X/facet）或 A=tilt_back（top-normal）派生 → 旋钮飞向错误方向 / 悬空于错误面。
- mini_half_stack 未建 `cabinet_to_head` FIXED，或 knob 仍 parent=speaker_cabinet（未重 parent 到 head_box）→ head 悬空 / 旋钮挂错箱。
- A=head_unit 仍发射 speaker_grille（grille_style 未 gate 成 null）→ 与「无 speaker 段」身份矛盾（head 应是 vent）。
- grille 起伏（woven rib）或 dual_round driver 深度超出 baffle pocket → 穿出 cabinet 背面 / 与壳穿模。
- A=mini_half_stack × B=front_faceplate/chamfer 未 gate（panel 仍试图锚到不存在的 body front/chamfer 面）→ panel 悬空 / 锚错箱。
- 把 PA 音柱、家用书架/落地音箱、收音机当 cabinet（错类别，无旋钮调音面板 + 吉他音箱比例）。

## 与相邻类别的边界

- 不该混入：**PA / 主扩声音柱（speaker / PA cabinet）**（无 control panel + 旋钮调音行、是被动/线阵扩声箱、比例细高或方正大箱；吉他音箱必须有 front 旋钮面板 + mini 乐器箱比例 + grille baffle）。
- 不该混入：**hi-fi / 家用书架或落地音箱**（被动音箱，无 gain/tone 旋钮行、无 vinyl/tolex + piping + logo 的乐器箱外观；其前网是装饰布罩而非演奏者操作面板）。
- 不该混入：**收音机（radio）**（有扬声器网 + 旋钮但语义是接收调谐——含刻度盘/频率指针/伸缩天线、桌面小盒比例；吉他音箱是乐器放大、旋钮是音色/音量、无调谐刻度/天线，且 baffle 是主功能面）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`KnobGeometry`（knurled + raised line indicator + off-axis pointer tab）knob 造型在全 11 源一致，可抽 `_make_knob_geometry()`（mini_stack L74-L90 已抽；front_faceplate 多一步 rotate_y(+π/2)、chamfer/tilt 多 rotate_y(±angle) 把轴转到 mount 法向）。`_rounded_box`/`_handle_mesh` 在 combo 族一致。Slot A 各模块各有 cabinet solid helper（`_cabinet_solid` for combo/head/chamfer；`_wedge_solid` for tilt；mini_stack 用 `_rounded_box_mesh` ×2 + FIXED joint），按 `cabinet_form` 分派。
- captured-pin / press-fit overlap 须 element-scoped `allow_overlap`：每 `knob_i`↔`gold_panel`（全 A/B）；chamfer 额外 `gold_panel`↔`cabinet`、`power_led`↔`gold_panel`。参考各源 run_tests 的 `allow_overlap` 块。
- knob 关节 axis 与 origin 必须从 resolved `(cabinet_form, control_panel_placement)` 统一派生（A=tilt_back 优先用 top-surface normal，否则用 B 的 mount normal），不可硬编码——A/B 切换会改变捕获面与轴向。
- `PANEL_W` 与 `knob_pitch` 必须随 `knob_count` 在 `resolve_config` 派生 + clamp（§7 两条 inequality）；n2（PANEL_W=0.100）与 n6（PANEL_W=0.165 + spacing=0.028）是上下界参照。
- A=mini_half_stack：B 强制 `top_recessed`（panel 锚到 head_box 顶），knob parent=head_box（`head_to_knob_i`），grille/piping/logo/caps 在 speaker_cabinet；着地以 speaker_cabinet 底。A=head_unit：grille_style gate 成 null，front 面发射 `front_vent_slots`（SlotPatternPanelGeometry）。
- A=tilt_back_wedge × B=front_faceplate/chamfer 为「兼容但需重算 mount surface 框架」组合——若几何不可行（panel 在斜 baffle 上越界），该 seed 的 B fallback 到 wedge 原生斜 top（top_recessed 等价）。
- C=dual_round_speakers 新增 `baffle_board` + lathe `speaker_i` 为 static visual（不旋转，driver 不是活动件）；须与 pocket 壁共面保 mesh 连通，speaker 深度 ≤ pocket 深度。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / N | `full_combo` / `top_recessed` / `perforated_panel` / N=4 | `rec_marshall-style-mini-guitar-combo-amplifier-black_20260605_161808_582290_34661766` | A `L80-L100, L103-L138`；B `L159-L167`；C `L169-L181`；knob 行 `L224-L262`；consts `L46-L66` | 三 slot + multiplicity 基线：cabinet solid + top recess panel + 穿孔 grille + 4-knob CONTINUOUS 行 |
| S2 | A | `head_unit` | `rec_guitar_amplifier_var_amp_head` | `L46-L48, L79-L105, L170-L183, L227-L264` | low/wide/shallow head（无 grille，front_vent_slots） |
| S3 | A | `mini_half_stack` | `rec_guitar_amplifier_var_mini_stack` | `L74-L90, L106-L177, L179-L226, L228-L258` | 2-node FIXED stack（speaker_cabinet→head_box，knob 重 parent） |
| S4 | A | `tilt_back_wedge` | `rec_guitar_amplifier_var_tilt_back_combo` | `L43-L106, L111-L131, L196-L234, L308-L350` | wedge cabinet + 斜 top panel + knob 绕 top-surface normal |
| S5 | B | `front_faceplate` | `rec_guitar_amplifier_var_front_faceplate` | `L55-L77, L148-L176, L197-L200, L266-L289` | front 面 gold strip + knob 绕 +X |
| S6 | B | `angled_chamfer_facet` | `rec_guitar_amplifier_var_angled_chamfer_panel` | `L64-L92, L105-L153, L208-L220, L294-L342` | 45° chamfer facet panel + knob 绕 facet normal |
| S7 | C | `woven_cloth` | `rec_guitar_amplifier_var_cloth_grille` | `L149-L159, L162-L194, L197-L258, L289-L293` | basket-weave 布纹 grille（真实起伏 mesh） |
| S8 | C | `dual_round_speakers` | `rec_guitar_amplifier_var_dual_round_speakers` | `L70-L81, L156-L193, L226-L244, L246-L269` | open-bar grille + baffle_board + 2 lathe 圆 driver |
| S9 | C | `quad_grid` | `rec_guitar_amplifier_var_quad_grille` | `L68-L73, L148-L183, L214-L221, L223-L236` | 2×2 perforated 四格 + 十字 rib |
| S10 | N | `knob_count` 下界 N=2 | `rec_guitar_amplifier_var_knobs_n2` | `L54, L63-L66, L227-L262` | PANEL_W 收窄 0.100，2-knob centered pair |
| S11 | N | `knob_count` 上界 N=6 | `rec_guitar_amplifier_var_knobs_n6` | `L54, L64-L68, L230-L264` | PANEL_W 拓宽 0.165 + respaced，6-knob 行 |
