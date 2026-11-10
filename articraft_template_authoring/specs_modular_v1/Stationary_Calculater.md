# Pocket calculator — Modular Spec

> 来源小类：`picture/Stationary/Calculater`（articraft_data 上游小类样本池；文件夹拼写为 `Calculater`，对象身份为 handheld calculator，本 spec slug 取规范拼写 `calculator`）。
> 上游 source map：建议回填 `picture_expansion/template_source_maps/Stationary__Calculater.md`（当前尚未建立；本 spec 已逐一内联全部 record_id + module 来源，source map 缺失不影响来源完整性）。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 个 parent + 5 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 6 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（FORK_VARIANTS §7：收敛即入池——6 个样本均 compile rc=0、均含 ≥1 非 fixed joint、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_build_body_mesh` / `_build_key_mesh` / `_build_cover_mesh` / `_build_kickstand_mesh` / `_build_display_hinge_bar_mesh` / `_key_specs` / `body_to_key_{kid}` / `body_to_cover` / `body_to_kickstand` / `body_to_display` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `calculator` |
| template path | `agent/templates/Stationary_Calculater.py` |
| test path (optional) | `tests/agent/test_calculator_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| __modular__ | `True` |
| pattern | `mixed`（固定 root body + parallel-children 槽位：display_mount + keypad_cover + rear_support，**外加** keypad 的 `n_cols × n_rows` 按键多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（1 parent + 5 单轴 fork 变体；均 converged，compile rc=0、均有 ≥1 非 fixed joint、workbench-only）|
| read_count | 6（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（小类只有这 6 个，无抽样）|
| source_index_policy | only adopted module sources are indexed below（6 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_build-a-realistic-articulated-3d-model-of-a-calc_20260609_200022_386588_14e5e957`）：矩形 slate-blue slab，FIXED flush LCD，FIXED 顶部 solar window，5 列科学计算器键盘（含 ctrl pair + r0–r4 + 跨两行 tall `+`，约 26 键），每键 PRISMATIC 下压。**全批基线**：提供 body 矩形壳、rounded-square 键帽、flush 显示、solar、keypad PRISMATIC 装配。
- **S1 keygrid**（`rec_calc_var_keygrid`）：把键盘重写为 `for i in range(n_keys)` 规则网格（4 列 × 5 行 = 20 键，`_KEY_DEFS` 表 (col,row)），并把 display + solar **inline 成 body visual**（无 FIXED 装饰 part）。**multiplicity 参考样本 + 循环发射范式**——模板的 keypad 复制逻辑、display/solar 内联策略以它为准。
- **S2 flip_cover**（`rec_calc_var_flip_cover`）：body mesh union 两个 hinge bracket + barrel，新增 `keypad_cover` part，REVOLUTE 绕 −X 在顶边翻开（铰链抬高到键帽之上）。**keypad_cover 槽位来源**。
- **S3 stand**（`rec_calc_var_stand`）：body 背面 cut 浅 recess，新增 `kickstand` part，REVOLUTE 绕 +X 在背面顶部展开支撑。**rear_support 槽位来源**。
- **S4 round**（`rec_calc_var_round`）：body 改 elliptical slab（`ellipse(BODY_RX, BODY_RY)`），键帽改 circular disc + 圆形 well。**shape_family 槽位来源**（footprint + 键帽形状成对变化）。
- **S5 tilt_display**（`rec_calc_var_tilt_display`）：display panel 改为 hinge-at-bottom，body 上加 hinge barrel visual，display 改 REVOLUTE 绕 +X 抬起。**display_mount 槽位来源**。

冗余说明：S0/S1/S2/S3/S5 的 body 均为矩形（同一 `rectangular_slab` 基线，提供共享壳 + keypad helper）；只有 S4 提供 elliptical 形态。5 个 fork 各自只改 1 根结构轴，其余层与 parent 同构——这正是 fork 池"单轴控制变量"的设计，diff 干净，每个轴恰好 1 个收敛候选。

## 核心身份

手持袖珍计算器（handheld pocket calculator）：一只薄板状壳体（slab，厚 ~0.012 m，纵向 portrait，长轴沿 Y），平躺于 z=0、正面朝 +Z；正面上三分之一是深色凹陷 LCD 显示窗，显示窗上方紧贴一条深色 solar-cell 窗，显示窗下方是一片**规则网格排列的按键**，每键是一只低矮键帽、可沿 −Z 短行程 **PRISMATIC 下压**（捕获在各自键井 well 内，静止时凸出面板、按下沉入井底）。**主用户机构 = 整片按键的下压**（每键一个 prismatic joint，统一行程 `KEY_TRAVEL≈0.0015 m`）。

默认成熟域：一只矩形或椭圆 slab，flush 或 tilt-up 显示，可选 keypad 翻盖 / 可选背面 kickstand，键盘为 `n_cols∈[3,6] × n_rows∈[4,6]` 的规则下压键网格（可选跨两行 tall `+`）。活动语义恒为"每键 −Z 下压"，叠加可选的"显示抬起 / 翻盖开合 / 支架展开"REVOLUTE。solar window 恒为固定装饰（inline body visual，不做独立 part）。

不该混入：遥控器 / remote control（按钮阵列但无 LCD 数字显示窗 + solar 身份，且通常长条形）、手机 / PDA（大屏占主面、键盘退化）、计算器键盘式的玩具收银机 / cash register（带抽屉、转盘等额外机构，出类目）、纯键盘 keyboard（无显示 + 无 solar + 非手持 slab）。Stationary 大类内也区别于 Clip / Folder / Pen 等无显示无键盘的文具。

## 槽位 + 候选模块表

> **建模注记（重要）**：calculator 是 **root body chassis + 一组 parallel children**——keypad（N 个 prismatic 键，挂 body）、display（flush=inline visual / tilt=REVOLUTE part，挂 body 显示窗下边）、可选 cover（挂 body 顶边）、可选 kickstand（挂 body 背面）；solar 恒为 body visual。**这些 child 不串成链**，各自独立挂到 body 的不同真实面。下面 4 个 slot 都是 body 的并联可替换层；keypad 的 N 由 §8 多重性轴描述。键帽形状随 shape_family 派生（圆 body→disc 键、矩形 body→rounded-square 键），故 shape_family 把 footprint 与键帽 primitive 成对绑定，不单列 key_cap slot。

### Slot A：shape_family（壳体 footprint + 键帽 primitive，成对）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular_square（基线） | rec_..._14e5e957（S0；S1/S2/S3/S5 同形） | `_build_body_mesh` L72-120 + `_rounded_box` L62-69 + `_build_key_mesh` L140-151 | eligible if compatible | 圆角矩形 slab（`box`+`fillet("|Z")`），rounded-square 键帽（`box`+`fillet`），矩形键井（`rect` cut） |
| oval_disc | rec_..._round（S4） | `_build_body_mesh` L100-144（`ellipse(BODY_RX,BODY_RY)` L104-108）+ `_build_key_mesh` 圆盘 L164-174 + 圆 well L133-142 | eligible if compatible | 椭圆 pill slab（`ellipse`+`extrude`），circular-disc 键帽（`circle`+`extrude`），圆形键井（`circle` cut） |

> 降级理由（2 candidate）：本小类单 parent，shape_family 仅 parent 矩形 + S4 椭圆两个真实收敛形态；现实计算器形态词汇表本身窄（矩形 / 圆角 pill 为主）。审核如需扩容应回 fork 池补造（如 tapered wedge slab / 折叠盖一体壳），不在模板侧虚构。

### Slot B：display_mount（显示窗安装/机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_flush_lcd（基线） | rec_..._keygrid（S1，inline visual 范式）/ rec_..._14e5e957（S0，FIXED part 形态） | S1 inline visual L206-211；S0 `_build_display_panel_mesh` L123-131 + FIXED `body_to_display` L246-255 | eligible if compatible | LCD 平躺贴 recess 底，**inline 成 body visual**（无活动；遵循"不动装饰不做独立 part"）|
| tilt_up_hinged | rec_..._tilt_display（S5） | `_build_display_panel_mesh`（hinge-at-bottom）L123-142 + `_build_display_hinge_bar_mesh` L145-160 + REVOLUTE `body_to_display` L284-303 | eligible if compatible | LCD 沿底边 hinge，body 上加 hinge barrel visual，REVOLUTE 绕 +X 抬起（range 0..0.85），display 成真实活动 part |

> 拓扑差异成立：tilt 相对 flush **新增 1 个 part + 1 个 REVOLUTE joint + body 上 hinge barrel**，part tree 与 joint 拓扑改变，非纯尺寸/材质。

### Slot C：keypad_cover（可选键盘翻盖；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | rec_..._14e5e957（S0；多数样本） | （无 cover part；body 无 hinge 硬件）| eligible if compatible | 无翻盖（baseline 缺省）|
| flip_cover_hinged | rec_..._flip_cover（S2） | body mesh union brackets+barrel L141-161 + `_build_cover_mesh` L183-198 + REVOLUTE `body_to_cover` L379-408 | eligible if compatible | 顶边 hinge bracket + barrel 焊进 body，薄翻盖 part 绕 −X 翻开（range 0..3 rad，铰链抬高到键帽之上）|

> 降级理由（含 none 共 2 candidate）：optional 机构槽，候选为 {缺省, 1 个真实翻盖机构}。`none` 是 parent 基线的合法取值，非"未实现占位"。

### Slot D：rear_support（可选背面支架；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | rec_..._14e5e957（S0；多数样本） | （无 kickstand part；body 背面无 recess）| eligible if compatible | 无支架（baseline 缺省）|
| fold_out_kickstand | rec_..._stand（S3） | body 背面 recess cut L130-140 + `_build_kickstand_mesh` L176-186 + REVOLUTE `body_to_kickstand` L353-383 | eligible if compatible | 背面浅 recess + 平板支腿，REVOLUTE 绕 +X 展开撑桌（range 0..0.60），收回平贴 recess |

> 降级理由：同 Slot C，optional 机构槽 {缺省, 1 个真实 kickstand}。

## 槽位图（slot graph）

```
pattern: mixed（root chassis + parallel children + keypad multiplicity）

                         body (root, shape_family ∈ {rectangular_square, oval_disc})
                          │   坐标：footprint 居中 XY，底面 z=0，正面 FACE_Z=BODY_T 朝 +Z
        ┌─────────────────┼───────────────────┬──────────────────┬───────────────────┐
        │                 │                   │                  │                   │
   solar_window      keypad[N]            display_mount       keypad_cover        rear_support
   (恒 body visual)  (multiplicity:       (Slot B)            (Slot C, optional)  (Slot D, optional)
                      n_cols×n_rows)
        │                 │                   │                  │                   │
   inline visual     key_{i}:             flush: inline       flip: REVOLUTE      kickstand: REVOLUTE
   @ top window      PRISMATIC −Z         visual @ recess     绕 −X @ 顶边         绕 +X @ 背面顶
   recess (FIXED     @ well floor         底 (FIXED 语义)      (hinge 抬到键帽上)  (收进背面 recess)
   语义, 不建 part)  (captured in well)   tilt: REVOLUTE +X
                                          @ 显示窗下边 hinge
```

接口点位（每条 body→child 连接）：
- **body → key_{i}**：mating face = 键井 well 底面（`origin=(cx, cy, FACE_Z−WELL_DEPTH)`），joint = PRISMATIC，axis `(0,0,−1)`，range `[0, KEY_TRAVEL]`。MatingContract = 键帽底部捕获在井内（静止凸出面板 `KEY_PROUD`、井壁四周 `WELL_CLEAR` 间隙）。
- **body → display（flush）**：inline body visual，origin 贴 recess 底 `FACE_Z−DISPLAY_DEPTH`，无 joint。
- **body → display（tilt）**：mating = 显示窗下边 hinge 线（`origin=(0, DISPLAY_Y−DISPLAY_L/2, FACE_Z−DISPLAY_DEPTH)`），joint = REVOLUTE，axis `(1,0,0)`，range `[0,0.85]`；body 侧 hinge barrel visual 提供真实承托。
- **body → keypad_cover（flip）**：mating = 顶边抬高的 hinge pin（`origin=(0, BODY_L/2, FACE_Z+KEY_PROUD+COVER_T+ε)`），joint = REVOLUTE，axis `(−1,0,0)`，range `[0,3]`；body 侧 bracket+barrel 焊接，与 cover hinge 边过盈（element-scoped allow_overlap）。
- **body → rear_support（kickstand）**：mating = 背面顶部 hinge 线（`origin=(0, KICK_HINGE_Y, 0)`，z=0 背面），joint = REVOLUTE，axis `(1,0,0)`，range `[0,0.60]`；收回时支腿嵌入背面 recess（面贴面）。
- **互斥/可选/派生**：Slot C、D 各为 optional（可同时存在，挂不同面，互不干涉）；键帽 primitive 由 Slot A **派生**（oval_disc→圆盘键，rectangular_square→方键）；flush 与 tilt 互斥（同一显示窗只能二选一）。

## 每槽位 Module Emits / Interfaces

### Slot A / module rectangular_square
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，`body_shell` visual：圆角矩形 slab + 周边 groove + 显示/solar/键井 cut）| S0 / `_build_body_mesh` L72-120 |
| internal joints | 无（root）| — |
| downstream interface | 正面 FACE_Z 平面 + 各键井 well 底（供 keypad / display / cover 锚定）；背面 z=0（供 kickstand）| S0 / L72-120 |
| 派生 | 键帽 = rounded-square（`box`+`fillet`），键井 = 矩形 `rect` cut | S0 / `_build_key_mesh` L140-151；well cut L109-118 |

### Slot A / module oval_disc
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（椭圆 pill slab，`ellipse(BODY_RX,BODY_RY)`+extrude，圆形键井 cut）| S4 / `_build_body_mesh` L100-144 |
| downstream interface | 同上但 footprint 为椭圆（键网格须落在椭圆内）| S4 / L100-144 |
| 派生 | 键帽 = circular disc（`circle`+`extrude`），键井 = 圆 `circle` cut | S4 / `_build_key_mesh` L164-174；well cut L133-142 |

### Slot B / module fixed_flush_lcd
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`lcd` 作为 body visual 内联于显示窗 recess | S1 / L206-211 |
| internal joints | 无（FIXED 语义；遵循"不动装饰不建 FIXED part"）| S1 / L206-211 |
| upstream interface | 贴 body 显示窗 recess 底 `FACE_Z−DISPLAY_DEPTH` | S1 / L210 |

### Slot B / module tilt_up_hinged
| emits | 描述 | 来源 |
|---|---|---|
| parts | `display`（`lcd` 面板，hinge 边在 part frame y=0）；body 侧加 `display_hinge_bar` visual | S5 / panel L123-142、bar L145-160/274-282 |
| internal joints | `body_to_display` REVOLUTE，axis (1,0,0)，range [0,0.85] | S5 / L284-303 |
| upstream interface | 显示窗下边 hinge 线（hinge barrel visual 承托）| S5 / L275-282 |

### Slot C / module flip_cover_hinged
| emits | 描述 | 来源 |
|---|---|---|
| parts | `keypad_cover`（薄翻盖，hinge 边在 part frame y=0,z=0）；body 侧 union 两 bracket + barrel | S2 / cover L183-198、hinge 硬件 L141-161 |
| internal joints | `body_to_cover` REVOLUTE，axis (−1,0,0)，range [0,3]（q=0 盖合，q=upper 翻到机身后）| S2 / L395-408 |
| upstream interface | 顶边抬高 hinge pin（高出键帽，避免压键）；bracket/barrel 与 cover 过盈，element-scoped allow_overlap | S2 / HINGE_Z L69、allow_overlap L611-618 |

### Slot D / module fold_out_kickstand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `kickstand`（平板支腿，hinge 边在 part frame y=0）；body 背面 cut recess | S3 / leg L176-186、recess L130-140 |
| internal joints | `body_to_kickstand` REVOLUTE，axis (1,0,0)，range [0,0.60]（q=0 收平嵌 recess，q=upper 撑出 −Z）| S3 / L370-383 |
| upstream interface | 背面 z=0 顶部 hinge 线；收回时支腿面贴 recess 底（真实接触）| S3 / KICK_HINGE_Y L68、recess L130-140 |

### keypad multiplicity / module key_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `key_{i}`（键帽 visual，形状由 Slot A 派生）× N | S1 循环 L228-247 |
| internal joints | `body_to_key_{i}` PRISMATIC，axis (0,0,−1)，range [0,KEY_TRAVEL] × N | S1 L251-264 |
| upstream interface | 各键井 well 底（body 上对应 cut）| S1 well rects L186-191 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| shape_family | enum | {rectangular_square, oval_disc} | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| display_mount | enum | {fixed_flush_lcd, tilt_up_hinged} | — | choice | sampler 选择 | Slot B 表 |
| keypad_cover | enum | {none, flip_cover_hinged} | none | choice | sampler 选择；optional | Slot C 表 |
| rear_support | enum | {none, fold_out_kickstand} | none | choice | sampler 选择；optional | Slot D 表 |
| key_cap_shape | enum(derived) | derived | — | conditional | `= square if shape_family==rectangular_square else disc` | Slot A 派生 |
| n_cols | int | [3, 6] | 4 | independent | 加权采样（小 N 偏多）后 clamp | §8 / S1 `_KEY_DEFS` |
| n_rows | int | [4, 6] | 5 | independent | 加权采样后 clamp | §8 / S1 `ROW_Y` |
| has_tall_plus | bool | {True, False} | False | conditional | 仅 `n_cols>=5` 时可 True（科学布局右下角跨两行 `+`）| S0 tall plus L214-217 |
| body_scale | float | [0.92, 1.12] | 1.0 | independent | 缩放 footprint（矩形 BODY_W/BODY_L 或椭圆 BODY_RX/BODY_RY），clamp 保 portrait（length>width）| S0 L35-37 / S4 L39-41 |
| key_pitch_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 COL_PITCH / 行距；clamp 使网格落在面板内 | S0 L161-175 |
| (—) | constraint | — | — | inequality | 键网格 XY 包络 ≤ 显示窗下方可用面板区（`n_cols·pitch_x·key_pitch_scale ≤ usable_w·body_scale`，行向同理）；越界则回缩 pitch 或拒绝重采 | 接口 / footprint |
| (—) | constraint | — | — | inequality | oval_disc：键网格四角须落在椭圆 `(x/BODY_RX)²+(y/BODY_RY)²≤1` 内；越界回缩网格 | S4 footprint |
| cover_reach_scale | float | [0.85, 1.05] | 1.0 | conditional | flip_cover 存在时缩放 COVER_L；若 display_mount==tilt 则 clamp 使 cover 只覆盖 keypad 区（不压到可抬起的显示）| S2 COVER_L L65 |
| kickstand_len_scale | float | [0.85, 1.10] | 1.0 | independent | kickstand 存在时缩放 KICK_L；clamp 使收回时支腿不超出背面 footprint | S3 KICK_L L63 |

连续 scale 默认独立采样 → 派生 key_cap_shape / has_tall_plus（conditional 按上游 enum/N 解析）→ inequality 把网格包络投影回面板/椭圆可行域，无法满足则拒绝重采。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

keypad 是唯一多重性来源，含 **2 根紧耦合 count 轴（网格行列）**，按规则单独声明：

- `count_param`: **`n_cols`** 与 **`n_rows`**（规则下压键网格的列数、行数）
- `N_range`:
  - `n_cols ∈ [3, 6]`（产品域；3=极简、4=基础、5=科学、6=宽科学）
  - `n_rows ∈ [4, 6]`（产品域；4=基础、5=标准、6=多功能行）
  - 已覆盖样本：S1 = 4×5（20 键，规则网格，loop 范式）；S0 = 5 列 + ctrl pair + r0..r4 + tall `+`（≈26 键，含 module-local tall-plus 变体）
- sampling domain（权重档）：小网格高频（4×5、4×4、5×5 常见），6×6 / 含 tall_plus 的科学布局稀有（长尾）
- copied object: 单只键帽 part `key_{i}`（形状由 shape_family 派生）+ 其 PRISMATIC 下压 joint；几何由共享 helper `_build_key_mesh` 按 (w,l) 或 radius 缓存复用
- naming: `key_{i}` / `body_to_key_{i}`，`for i in range(n_cols*n_rows)`（S1 已用此结构，直接作 module 源码）
- placement: 规则网格——列 X 中心 `COL_X[col]`（按 `n_cols` 居中等距）、行 Y 中心 `ROW_Y[row]`（按 `n_rows` 在显示窗下方等距），均经 key_pitch_scale / body_scale 缩放并 clamp 进面板
- joint policy: 每键**独立** PRISMATIC，axis (0,0,−1)，统一 range [0, KEY_TRAVEL]，统一 effort/velocity；键帽捕获在各自 well 内
- source/gating: 循环范式 S1 L228-264；module-local `has_tall_plus` 变体（右下角跨两行大键，占用 1 格列）仅 `n_cols>=5` 启用，源自 S0 tall-plus L214-217；oval_disc 下网格须落在椭圆内（§7 inequality）

## 拓扑多样性审计

总组合数（离散槽）：shape_family(2) × display_mount(2) × keypad_cover(2) × rear_support(2) = **16**
叠加 multiplicity：n_cols(4 值) × n_rows(3 值) = 12 种网格规模（多数产生不同键数 → 不同 part/joint 计数 = 不同拓扑等价类），再叠 has_tall_plus（科学布局）。
→ 16 × ~12 ≈ **190+ distinct 拓扑**（扣除少量键数碰撞后仍远超门槛）。

理由：仅 16 个离散槽组合即 >10；键网格规模轴再乘 ~12，distinct 拓扑充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——先加权选 4 个离散 slot（cover/support 偏 none，shape 偏矩形，display 偏 flush）、再加权采 n_cols/n_rows（小网格偏多）、派生 key_cap_shape/has_tall_plus、采连续 scale、经 `resolve_config` 的 inequality 把网格投影回 footprint 可行域。compatibility matrix 排除/校正非法组合（见下表）。`seed=0` 不特殊。无需 regression overrides（无已知失败回归；若 sweep 暴露特定 seed 失败，再稀疏加显式 override 并注明）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）（本类 ~190 上界可达；若实测低于 300，多因键数碰撞，可调宽 n_cols/n_rows 权重）。
Controlled local parameterization：初版即含 `body_scale` / `key_pitch_scale` / `cover_reach_scale` / `kickstand_len_scale`（§7），全部 clamp/派生，受 footprint 包络、键井捕获、hinge 抬高、recess 嵌合约束，不改变拓扑、键的 prismatic 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：shape→display→cover→support→(n_cols,n_rows)→scales；加权（cover/support 偏 none，小网格偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | oval_disc⇒disc 键帽 + 网格落椭圆内；flush↔tilt 互斥；cover+tilt⇒cover 只盖 keypad 区（cover_reach clamp）；has_tall_plus⇒n_cols≥5；cover/support 可并存（异面）| 无穿模/悬空/越界键、hinge 抬到键帽上、kickstand 收回贴 recess、cover 闭合不压可抬显示 |
| controlled local variation | body_scale / key_pitch_scale / cover_reach_scale / kickstand_len_scale + clamp | 比例变化不破坏键井捕获、hinge 接触、footprint 包络、joint origin、类别身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 InterfaceSpec/MatingContract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A shape_family | 2 | yes | no | 单 parent 小类，矩形+椭圆两个真实形态；扩容须回 fork 池补造 |
| B display_mount | 2 | yes | no | flush（inline visual）/ tilt（REVOLUTE part），真实拓扑差异 |
| C keypad_cover | 2 | yes | no | optional：{none, flip_cover} |
| D rear_support | 2 | yes | no | optional：{none, kickstand} |
| (mult) keypad | n_cols[3-6]×n_rows[4-6] | — | — | 多重性轴，提供主拓扑乘子 |

## Validator

- slot_choices_for_seed returns implemented module names（shape_family / display_mount / keypad_cover / rear_support + (n_cols, n_rows)）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：oval_disc⇒disc 键 + 网格落椭圆；flush↔tilt 互斥；cover+tilt 时 cover 只盖 keypad；has_tall_plus⇒n_cols≥5
- optional regression overrides 初版为空（如加须稀疏 + 注明）
- controlled local scale params 全部 clamp，且不破坏键井捕获 / hinge 接触 / footprint 包络 / joint origin / 类别身份
- cross-part scale 依赖（键网格包络 vs footprint、cover_reach vs display、kickstand_len vs recess）在 `resolve_config` 内 inequality/conditional 求解，不留到 builder 失败
- critical InterfaceSpec / MatingContract 存在：键-井底捕获、tilt hinge barrel 承托、cover bracket/barrel 过盈、kickstand-recess 面贴面
- key joints：每键 PRISMATIC axis (0,0,−1) range [0,KEY_TRAVEL]；tilt display REVOLUTE +X；cover REVOLUTE −X；kickstand REVOLUTE +X
- copied objects 遵循 `key_{i}` 命名 + 规则网格 placement + 统一 joint policy
- solar window 恒为 body visual（不建 FIXED 装饰 part）

## Reject cases

- 把 solar window / flush display 做成 FIXED-joint 独立 part（违反"不动装饰内联 body visual"）。
- 键帽悬浮或穿出面板：未捕获在 well 内（静止应凸出 `KEY_PROUD`、底沉入井 `WELL_DEPTH`）。
- 键网格越出 footprint：矩形溢出边缘、或 oval_disc 下四角落在椭圆外。
- oval_disc 仍用方键帽 / 矩形键井（键帽 primitive 未随 shape_family 派生）。
- flip_cover hinge 直接放在面板上压住键帽（未抬高到键帽之上），或闭合 cover 与 tilt-up display 互相穿插（未做 cover_reach gating）。
- kickstand 展开方向错误（向 +Z 正面翻而非 −Z 背面撑），或收回时不嵌入背面 recess（幻影接触）。
- 用连续 enum/尺寸冒充拓扑：只改 body 尺寸/颜色而不换 shape_family/display/cover/support/网格规模就当作新拓扑。
- keypad 用手写命名的 2–3 个键代替 `for i in range(N)` 循环发射（多重性退化）。
- config_from_seed 采样到未实现组合（如 tilt+flush 同时、has_tall_plus 在 n_cols<5）。

## 与相邻类别的边界

- 不该混入：遥控器 remote control（按钮阵列但无 LCD 数字显示窗 + solar 身份，常长条形；calculator 身份 = 显示窗 + 网格下压键 + solar）。
- 不该混入：手机 / PDA / 翻盖电子词典（屏幕占主面，键盘退化或为全字母 QWERTY；calculator 为算术网格键 + 上三分之一小显示窗）。
- 不该混入：纯键盘 keyboard / 数字小键盘 numpad（无显示窗、无 solar、非手持 slab）。
- 不该混入：玩具收银机 / cash register（带抽屉、转盘、出钞等额外机构，出"手持计算器"语义）。
- Stationary 大类内：区别于 Clip / Folder / Pen / Scissors 等无显示无键盘文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 用户审核通过（"spec is fine"）。模板已实现 `agent/templates/Stationary_Calculater.py`（注册于 `cli/template.py` TEMPLATE_REGISTRY），`uv run articraft template sweep-pipeline calculator` 分阶段 1/5/20/50 seeds 全 pass_rate=1.0，verdict=pass， distinct=42。剩余：viewer 目检（人工）。原审核问题：①4 个 slot 各 2 candidate 的降级；②n_cols×n_rows N_range 与权重；③cover+tilt 的 cover_reach gating ① 4 个 slot 各 2 candidate 的降级是否接受，还是要求回 fork 池把 shape_family/display 补到；② keypad 双 count 轴 n_cols×n_rows 的 N_range 与权重档；③ cover+tilt 的 cover_reach gating 方案是否认可，或改为二者互斥）|

## 模板实现备注（可选）

- 共享 helper：`_build_body_mesh`（按 shape_family 分矩形/椭圆两路）、`_build_key_mesh`（按 key_cap_shape 分 box/circle）、`_key_grid`（按 n_cols×n_rows 生成 COL_X/ROW_Y 与 well rects/circles，统一供 body cut 与 keypad 发射）。
- InterfaceSpec/MatingContract 注意点：tilt display 的 hinge barrel 必须真实 union/visual 到 body 显示窗下边；flip_cover 的 bracket+barrel 须焊进 body 并对 cover hinge 边声明 **element-scoped allow_overlap**（过盈销，参考 S2 L611-618）；kickstand 收回时与背面 recess 的面贴面接触（recess 深度 = 支腿厚，参考 S3）。
- 派生与门控集中在 `resolve_config`：key_cap_shape、has_tall_plus、cover_reach（依赖 display_mount）、网格包络投影。
- 模板实现前先从 `MATURE_TEMPLATE_METHOD.md` 的 reference map 选 1–3 个"root chassis + parallel children / 多重性按键阵列"近邻模板深读（运动拓扑相近者，如带 N 个独立 pivot/press 子件的阵列模板），不按类别名相似选。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A / mult | rectangular_square / keypad 基线 | rec_..._14e5e957 | `_build_body_mesh` L72-120、`_build_key_mesh` L140-151、`_key_specs`(+tall plus) L178-219、PRISMATIC 键 L283-316 | 矩形壳 + 方键帽 + 科学键盘 + tall-plus 变体 + prismatic 装配基线 |
| S1 | B / mult | fixed_flush_lcd / 循环范式 | rec_calc_var_keygrid | inline display+solar L206-217、`_KEY_DEFS` 网格 L169-180、`for i` 发射 L228-264 | flush 内联策略 + keypad 循环多重性范式 |
| S2 | C | flip_cover_hinged | rec_calc_var_flip_cover | hinge 硬件 union L141-161、`_build_cover_mesh` L183-198、REVOLUTE `body_to_cover` L379-408、allow_overlap L611-618 | 翻盖 part + 顶边抬高 hinge + 过盈接口 |
| S3 | D | fold_out_kickstand | rec_calc_var_stand | recess cut L130-140、`_build_kickstand_mesh` L176-186、REVOLUTE `body_to_kickstand` L353-383 | 背面支架 part + recess 嵌合接口 |
| S4 | A | oval_disc | rec_calc_var_round | `_build_body_mesh`(ellipse) L100-144、`_build_key_mesh`(disc) L164-174、圆 well L133-142 | 椭圆壳 + 圆盘键帽 + 圆键井 |
| S5 | B | tilt_up_hinged | rec_calc_var_tilt_display | `_build_display_panel_mesh`(hinge) L123-142、`_build_display_hinge_bar_mesh` L145-160、REVOLUTE `body_to_display` L284-303 | 抬起显示 part + body hinge barrel 承托 |
