# Clipboard — Modular Spec

> 来源小类：`picture/Stationary/Clipboard`（articraft_data 上游小类样本池；对象身份为 letter/A4 paper clipboard）。
> 上游 source map：建议回填 `picture_expansion/template_source_maps/Stationary__Clipboard.md`（当前尚未建立；本 spec 已逐一内联全部 record_id + module 来源，source map 缺失不影响来源完整性）。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 **workbench-only** 样本（1 个 parent + 10 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 11 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（FORK_VARIANTS §7：收敛即入池——11 个样本均 compile rc=0、均含 ≥1 非 fixed joint、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_board_solid` / `_clamp_base_solid` / `_clamp_lever_solid` / `_bracket_solid` / `_cam_lever_solid` / `_anchor_block_solid` / `_bail_path_joint_local` / `_spine_plate_solid` / `_arch_wire_points` / `_eyelet_boss_solid` / `_swivel_ring_mesh` / `_hinge_spine_solid` / `_cover_panel_solid` / `base_to_lever` / `bracket_to_lever` / `anchor_to_bail` / `spine_to_arch` / `board_to_ring` / `board_to_cover` / `base_to_lever_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `clipboard` |
| template path | `agent/templates/Stationary_Clipboard.py` |
| test path (optional) | `tests/agent/test_clipboard_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| __modular__ | `True` |
| pattern | `mixed`（固定 root board + parallel-children 槽位：clamp_mechanism + hang_hardware + cover，**外加** clamp 的 `n_clamps` 多重性轴；board_form 决定 board 轮廓 + clamp 安装边/轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent + 10 单轴 fork 变体；均 converged，compile rc=0、均有 ≥1 非 fixed joint、workbench-only）|
| read_count | 11（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（小类只有这 11 个，无抽样）|
| source_index_policy | only adopted module sources are indexed below（11 个样本全部提供 module 来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_build-a-realistic-articulated-3d-model-of-a-clip_20260609_200030_214390_f7e86c02`）：letter-size 蓝色塑料 board + 顶边铬制 **torsion 弹簧夹**（`clamp_base` FIXED + `clamp_lever` REVOLUTE 绕 Y，前唇压纸、后指垫抬起开口）。**全批基线**：提供 rounded-rect board、FIXED 金属 base、REVOLUTE 弹簧 lever、finger caps、captured-pin allow_overlap 装配（`_board_solid` L73、`_clamp_base_solid` L85、`_clamp_lever_solid` L157、`base_to_lever` L296、allow_overlap L322）。
- **S1 togglelever**（`rec_clipboard_var_togglelever`）：弹簧夹改 **over-center toggle cam lever**——FIXED `bracket` + 凸轮 lever（圆 cam lobe + 压脚），REVOLUTE 绕 Y，lever 放平压纸、立起松开（`_bracket_solid` L98、`_cam_lever_solid` L170、`bracket_to_lever` L296）。**clamp_mechanism / toggle 来源**。
- **S2 wirebail**（`rec_clipboard_var_wirebail`）：弹簧夹改 **sprung wire bail**——FIXED `anchor_block` + 单根弯 round-wire U 形 bail，REVOLUTE 绕 Y，bail 前横杆下压纸（`_anchor_block_solid` L96、`_bail_path_joint_local` L139、`anchor_to_bail` L231，axis L236）。**clamp_mechanism / wire_bail 来源**。
- **S3 archring**（`rec_clipboard_var_archring`）：弹簧夹改 **split wire arch ring-binder**——FIXED `spine_plate` + 半圆 round-wire arch，REVOLUTE 绕 Y 开合捕获打孔纸（`_spine_plate_solid` L77、`_arch_wire_points` L123、`spine_to_arch` L211，axis L216）。**clamp_mechanism / arch_ring 来源**。
- **S4 foldback**（`rec_clipboard_var_foldback`）：弹簧夹改 **foldback/butterfly channel + 2 折臂**——FIXED `channel` + `for i in range(2)` 两根 mirror 弯线臂，各 REVOLUTE 绕 X（`_channel_body` L86、`_wire_arm_points` L175、`for i in range(2)` L243/264、`channel_to_arm_{i}` L267，axis L272）。**采纳为 multiplicity 循环范式参考**（每夹独立 base+mover 的 `for i` 发射 + 共享 helper + 统一 joint policy）。
- **S5 sideclamp**（`rec_clipboard_var_sideclamp`）：board 改 **landscape**，弹簧夹移到长左侧边，pivot 轴沿该边（`_board_solid` landscape L76-84，`box(BOARD_WID,BOARD_LEN,…)` L84、`base_to_lever` L303，axis L308）。**board_form / side_landscape 来源**（board 轮廓 + clamp 安装边成对变化）。
- **S6 clamps2**（`rec_clipboard_var_clamps2`）：弹簧夹 N=2，`for i in range(NUM_CLAMPS)` 沿顶边等距双夹，base/lever helper 带 `y_center` 参数（`_clamp_base_solid(y_center)` L93、`for i in range(NUM_CLAMPS)` L267/337，axis L310）。**multiplicity N=2 来源**。
- **S7 clamps3**（`rec_clipboard_var_clamps3`）：弹簧夹 N=3，`for i in range(CLAMP_COUNT)` 三夹等距（L71/258、`base_to_lever_{i}` L328）。**multiplicity N=3 来源**。
- **S8 roundedtop**（`rec_clipboard_var_roundedtop`）：board 改 **arched-head**——顶边为半圆弧（`threePointArc((-ARCH_RISE,0),(0,hw))` L91，`ARCH_RISE` L40），夹仍坐在弧肩平段。**board_form / arched_top 来源**。
- **S9 hangloop**（`rec_clipboard_var_hangloop`）：保留弹簧夹，加 **swivel hang ring**——board 边 `eyelet boss` + round-wire torus ring，REVOLUTE swivel 让 board 可挂（`_eyelet_boss_solid` L255、`_swivel_ring_mesh` L285、`board_to_ring` swivel REVOLUTE L395+）。**hang_hardware / swivel_ring 来源**。
- **S10 foldingcover**（`rec_clipboard_var_foldingcover`）：保留弹簧夹，加 **hinged front cover**——沿一条长侧边 hinge spine + cover panel，REVOLUTE 绕 X 翻合（`_hinge_spine_solid` L251、`_cover_panel_solid` L270、`board_to_cover` L400，axis L405）。**cover / folding_cover 来源**。

冗余说明：S0/S5/S6/S7/S8/S9/S10 的 clamp 机构均为同一 `spring_jaw` 基线（弹簧夹），各自只改 1 根结构轴（安装边 / 数量 / board 轮廓 / 挂环 / 翻盖），其余层与 parent 同构；S1/S2/S3 各换 1 种夹机构；S4 是 foldback（采纳为 multiplicity 循环范式，其 foldback 机构本身折入 wire_bail 家族的 reject-边界讨论，不单列 candidate）。这正是 fork 池"单轴控制变量"的设计，diff 干净。

## 核心身份

纸夹板（letter/A4 paper clipboard）：一片薄塑料/硬质 board（厚 ~0.0032 m，长轴沿 X 或 Y，平躺于 z=0、正面朝 +Z），顶边（或左侧边）铆装一只低矮金属 **纸夹机构**——一只 FIXED 金属 base/bracket/anchor/spine 坐在 board 顶面，承载一只 **REVOLUTE 活动夹件**（弹簧 jaw / toggle cam lever / wire bail / arch ring），活动件绕安装边方向的轴转动，把纸压向 board（合）或抬起让纸进出（开）。**主用户机构 = 纸夹的开合**（每只夹一个 REVOLUTE joint）。

默认成熟域：一片矩形 / 弧头 / 横向 board，顶（或侧）边 1–3 只同构纸夹，夹机构为弹簧 jaw / toggle / wire bail / arch ring 之一；可选顶角 swivel hang ring（可挂）、可选沿长边 folding cover（folder 化）。活动语义恒为"夹件绕安装边轴 REVOLUTE 开合"，叠加可选的"挂环 swivel / 翻盖开合"REVOLUTE。rivet / 装饰盘恒为固定装饰（inline 进 base 或 board visual，不做独立 FIXED part）。

不该混入：活页夹 / ring binder（多孔环册 + 封皮书脊为主体，board 退化）；文件夹 / folder（无金属夹，纯对折塑料封套）；订书机 / stapler（铰链压钉 + 钉仓，出文具夹身份）；公告板 / clipboard easel（带支腿立架）；纯夹子 clip / 长尾夹 binder clip（无 board 载体）。Stationary 大类内区别于 Pen / Scissors / Calculator 等无 board+夹身份的文具。

## 槽位 + 候选模块表

> **建模注记（重要）**：clipboard 是 **root board chassis + 一组 parallel children**——clamp[N]（每夹 = FIXED base + REVOLUTE mover，挂 board）、可选 hang ring（挂 board 顶角 eyelet）、可选 cover（挂 board 长边 hinge spine）；rivet/eyelet/hinge-spine 恒为 board 或 base visual。**这些 child 不串成链**，各自独立挂到 board 的不同真实面。下面 3 个 slot 都是 board 的并联可替换层；clamp 的 N 由 §8 多重性轴描述。board_form 把 board 轮廓与 clamp 安装边/轴成对绑定（portrait 顶边 / arched 顶边 / landscape 侧边），不单列安装边 slot。

### Slot A：board_form（board 轮廓 + clamp 安装边/轴，成对）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rect_rounded（基线） | S0（`_..._f7e86c02`；多数 fork 同形） | `_board_solid` L73-82（`box`+`fillet("|Z")`）| eligible if compatible | 圆角矩形 portrait slab，clamp 坐顶（−X 短）边，pivot 轴沿 Y |
| arched_top | S8（`rec_..._roundedtop`） | `_board_solid` L75-92（`threePointArc((-ARCH_RISE,0),(0,hw))` L91）| eligible if compatible | 顶边半圆弧头 portrait slab，clamp 坐弧肩平段，pivot 轴沿 Y |
| side_landscape | S5（`rec_..._sideclamp`） | `_board_solid` L76-84（`box(BOARD_WID,BOARD_LEN,…)` L84，长轴沿 Y）| eligible if compatible | 横向 landscape slab，clamp 坐长左侧边，pivot 轴沿该边（Y） |

> 3 candidate（达 ≥3 目标）：parent 矩形 + roundedtop 弧头 + sideclamp 横向，三个真实收敛 board 轮廓 / 安装姿态。

### Slot B：clamp_mechanism（纸夹机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| spring_jaw（基线） | S0（`_..._f7e86c02`） | `_clamp_base_solid` L85-154 + `_clamp_lever_solid` L157-222 + `_finger_caps_solid` L225 + `base_to_lever` L296 | eligible if compatible | FIXED 铆 base（footplate+hump+cheeks+barrel）+ 弧形 sheet-metal 弹簧 lever（前唇+后指垫+pin sleeve），REVOLUTE 绕 Y |
| toggle_lever | S1（`rec_..._togglelever`） | `_bracket_solid` L98-169 + `_cam_lever_solid` L170-221 + `bracket_to_lever` L296 | eligible if compatible | FIXED bracket + 凸轮 lever（圆 cam lobe + 压脚 + 长 handle），REVOLUTE 绕 Y，放平压纸/立起松开 |
| wire_bail | S2（`rec_..._wirebail`） | `_anchor_block_solid` L96-138 + `_bail_path_joint_local` L139 + `anchor_to_bail` L231（axis L236）| eligible if compatible | FIXED anchor block + 单根弯 round-wire U 形 bail（轴 + 两腿 + 前横杆），REVOLUTE 绕 Y，前横杆下压纸 |
| arch_ring | S3（`rec_..._archring`） | `_spine_plate_solid` L77-111 + `_arch_wire_points` L123 + `spine_to_arch` L211（axis L216）| eligible if compatible | FIXED spine plate + 半圆 round-wire arch（轴 + 弧），REVOLUTE 绕 Y 开合捕获打孔纸 |

> 4 candidate（超 ≥3 目标）：弹簧 jaw / toggle cam / wire bail / arch ring 四个真实收敛机构。每个都新增/替换 mover part 的几何与 joint range，非纯尺寸/材质。foldback（S4）的双折臂机构本身可视为 wire_bail 家族的 N=2 变体，为保持 candidate 结构纯净未单列（其循环范式采纳进 §8 multiplicity）。

### Slot C：hang_hardware（可选顶角挂环；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | S0（`_..._f7e86c02`；多数样本） | （无 ring part；board 无 eyelet boss）| eligible if compatible | 无挂环（baseline 缺省）|
| swivel_ring | S9（`rec_..._hangloop`） | `_eyelet_boss_solid` L255-284 + `_swivel_ring_mesh` L285 + REVOLUTE `board_to_ring` swivel L395+ | eligible if compatible | board 顶角 eyelet boss（inline board visual）+ round-wire ring part，REVOLUTE swivel 绕 eyelet 轴（X），让 board 可挂 |

> 降级理由（含 none 共 2 candidate）：optional 机构槽，候选为 {缺省, 1 个真实挂环}。`none` 是 parent 基线合法取值，非"未实现占位"。

### Slot D：cover（可选 folding 封盖；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | S0（`_..._f7e86c02`；多数样本） | （无 cover part；board 无 hinge spine）| eligible if compatible | 无封盖（baseline 缺省）|
| folding_cover | S10（`rec_..._foldingcover`） | `_hinge_spine_solid` L251-269 + `_cover_panel_solid` L270-292 + REVOLUTE `board_to_cover` L400（axis L405）| eligible if compatible | board 长侧边 hinge spine（inline board visual）+ 薄 cover panel part，REVOLUTE 绕 X 翻合（闭合平贴 board，开起立） |

> 降级理由：同 Slot C，optional 机构槽 {缺省, 1 个真实 folding cover}。

## 槽位图（slot graph）

```
pattern: mixed（root chassis + parallel children + clamp multiplicity）

                         board (root, board_form ∈ {rect_rounded, arched_top, side_landscape})
                          │   坐标：footprint 居中 XY，底面 z=0，正面 FACE_Z=BOARD_THK 朝 +Z
        ┌─────────────────┼───────────────────┬──────────────────┐
        │                 │                   │                  │
   rivet/eyelet/      clamp[N]            hang_hardware       cover
   hinge-spine        (multiplicity:       (Slot C, optional)  (Slot D, optional)
   (恒 inline visual)  n_clamps)
        │                 │                   │                  │
   inline board/     clamp_base_{i}:      swivel: REVOLUTE    folding: REVOLUTE
   base visual       FIXED @ 安装边        绕 X(eyelet 轴)     绕 X @ 长侧边
   (FIXED 语义,      clamp_mover_{i}:      @ 顶角 eyelet boss  (hinge spine 承托)
   不建 part)        REVOLUTE 绕 Y
                     @ pivot barrel
                     (captured pin sleeve)
```

接口点位（每条 board→child 连接）：
- **board → clamp_base_{i}**：mating face = 安装边 board 顶面（FIXED `origin=(CLAMP_CENTER_X, cy, FACE_Z)`），joint = FIXED。base mesh authored 于自身帧（footplate 底 z=0、pivot 在 local (0,0,PIVOT_RISE)），FIXED origin 落在 footplate 上（真实 base+board 几何）。
- **clamp_base_{i} → clamp_mover_{i}**：mating = pivot barrel（base 帧 `origin=(0,0,PIVOT_RISE)`），joint = REVOLUTE，axis `(0,−1,0)`，range `[0, open_limit]`（机构相关）。MatingContract = mover pin sleeve 捕获在 base barrel（captured-pin，过盈 element-scoped allow_overlap）。
- **board → swivel_ring（swivel）**：mating = 顶角 eyelet boss 顶面（`origin=(EYELET_X, EYELET_Y, FACE_Z)`），joint = REVOLUTE，axis `(1,0,0)`（eyelet 轴），range `[−π, π]`；ring 线缠 eyelet boss（captured-pin）。
- **board → cover（folding）**：mating = 长侧边 hinge spine 线（`origin=(load_len/2, edge_len/2, FACE_Z+HINGE_R)`），joint = REVOLUTE，axis `(−1,0,0)`，range `[0,2.4]`；hinge knuckle 缠 board hinge spine（captured-pin）。
- **互斥/可选/派生**：Slot C、D 各为 optional（可同时存在，挂不同面，互不干涉）；clamp 机构 mover 几何与 open_limit 由 Slot B **派生**；board 轮廓 + clamp 安装边由 Slot A **成对派生**；clamp 数量 N 由 §8 多重性轴。

## 每槽位 Module Emits / Interfaces

### Slot A / module rect_rounded
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board`（root，圆角矩形 portrait slab，inline rivet/eyelet/hinge-spine visual）| S0 / `_board_solid` L73-82 |
| internal joints | 无（root）| — |
| downstream interface | 顶（−X）边 board 顶面（供 clamp 锚定）；顶角（供 ring）；长侧边（供 cover）| S0 / L73-82 |

### Slot A / module arched_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board`（弧头 portrait slab，`threePointArc` 顶弧）| S8 / `_board_solid` L75-92 |
| downstream interface | 同上但顶边为弧；clamp 坐弧肩平段 | S8 / L91 |

### Slot A / module side_landscape
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board`（横向 landscape slab，长轴沿 Y）| S5 / `_board_solid` L76-84 |
| downstream interface | clamp 坐长左侧边，pivot 轴沿该边 | S5 / L84、`base_to_lever` L303 |

### Slot B / module spring_jaw
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_base_{i}`（FIXED 金属 base）+ `clamp_mover_{i}`（弹簧 lever + finger caps）| S0 / `_clamp_base_solid` L85、`_clamp_lever_solid` L157、`_finger_caps_solid` L225 |
| internal joints | `clamp_base_{i}_to_mover_{i}` REVOLUTE，axis (0,−1,0)，range [0,0.42·open_scale] | S0 / `base_to_lever` L296 |
| upstream/downstream interface | base footplate 贴 board 顶面；pivot barrel 承托 mover sleeve | S0 / L132-139、sleeve L211-219 |

### Slot B / module toggle_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_base_{i}`（FIXED bracket）+ `clamp_mover_{i}`（凸轮 lever：cam lobe+压脚+handle）| S1 / `_bracket_solid` L98、`_cam_lever_solid` L170 |
| internal joints | `clamp_base_{i}_to_mover_{i}` REVOLUTE，axis (0,−1,0)，range [0,0.55·open_scale] | S1 / `bracket_to_lever` L296 |
| upstream interface | bracket pin + cam lobe 在 pivot；压脚下压 board grip 区 | S1 / L170-221 |

### Slot B / module wire_bail
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_base_{i}`（FIXED anchor block+ears+barrel）+ `clamp_mover_{i}`（弯 wire U bail）| S2 / `_anchor_block_solid` L96、`_bail_path_joint_local` L139 |
| internal joints | `clamp_base_{i}_to_mover_{i}` REVOLUTE，axis (0,−1,0)，range [0,0.85·open_scale] | S2 / `anchor_to_bail` L231 |
| upstream interface | bail 轴在 pivot；前横杆下压 board grip 区 | S2 / L139-160 |

### Slot B / module arch_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_base_{i}`（FIXED spine plate+ears+barrel）+ `clamp_mover_{i}`（半圆 wire arch）| S3 / `_spine_plate_solid` L77、`_arch_wire_points` L123 |
| internal joints | `clamp_base_{i}_to_mover_{i}` REVOLUTE，axis (0,−1,0)，range [0,1.10·open_scale] | S3 / `spine_to_arch` L211 |
| upstream interface | arch 轴在 pivot；arch 平铺捕获打孔纸（不压脚，故 grip-reach 检查跳过）| S3 / L123-135 |

### Slot C / module swivel_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `swivel_ring`（round-wire ring）；board 侧加 `eyelet boss` inline visual | S9 / `_swivel_ring_mesh` L285、`_eyelet_boss_solid` L255 |
| internal joints | `board_to_swivel_ring` REVOLUTE，axis (1,0,0)，range [−π,π] | S9 / `board_to_ring` swivel L395+ |
| upstream interface | 顶角 eyelet boss 顶面；ring 线缠 boss（captured-pin）| S9 / L255-284 |

### Slot D / module folding_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`（薄 panel + hinge knuckle）；board 侧加 `hinge_spine` inline visual | S10 / `_cover_panel_solid` L270、`_hinge_spine_solid` L251 |
| internal joints | `board_to_cover` REVOLUTE，axis (−1,0,0)，range [0,2.4]（q=0 平贴，q=upper 立起）| S10 / `board_to_cover` L400 |
| upstream interface | 长侧边 hinge spine 线；cover knuckle 缠 spine（captured-pin）| S10 / L251-292 |

### clamp multiplicity / module clamp_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_base_{i}` + `clamp_mover_{i}`（机构由 Slot B 派生）× N | S6/S7 循环 L267/258 |
| internal joints | FIXED `board_to_clamp_base_{i}` + REVOLUTE `clamp_base_{i}_to_mover_{i}` × N | S6 L267-337、S7 L258-328 |
| upstream interface | 沿安装边等距 cy（共享 helper，统一 joint policy）| S6 `y_center` L93、`for i` L267 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| board_form | enum | {rect_rounded, arched_top, side_landscape} | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| clamp_mechanism | enum | {spring_jaw, toggle_lever, wire_bail, arch_ring} | — | choice | sampler 选择 | Slot B 表 |
| hang_hardware | enum | {none, swivel_ring} | none | choice | sampler 选择；optional | Slot C 表 |
| cover | enum | {none, folding_cover} | none | choice | sampler 选择；optional | Slot D 表 |
| clamp_mount_edge | enum(derived) | derived | — | conditional | `= side if board_form==side_landscape else top` | Slot A 派生 |
| n_clamps | int | [1, 3] | 1 | independent | 加权采样（小 N 偏多）后 clamp | §8 / S6 `NUM_CLAMPS`、S7 `CLAMP_COUNT` |
| board_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 board footprint（load_len/edge_len + arch_rise），clamp | S0 L36-37 / S8 L40 |
| clamp_span_scale | float | [0.88, 1.08] | 1.0 | independent | 缩放单夹 clamp_wid（沿安装边的 Y 占位）；clamp | S0 CLAMP_WID L44 |
| lever_reach_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 lever/bail/arch 前伸 reach；clamp | S0 LEVER_FRONT L61 |
| open_angle_scale | float | [0.85, 1.12] | 1.0 | independent | 缩放夹件 open_limit（按机构 base 角×scale，clamp 到 [0.20,1.40]）| S0 limit L302 |
| (—) | constraint | — | — | inequality | clamp 行包络：`n·clamp_wid + (n−1)·gap ≤ usable_edge`（usable=edge_len−2·margin）；越界则回缩 clamp_wid（min 0.038）| §8 / footprint |
| (—) | constraint | — | — | inequality | clamp 行等距 cy 由 `pitch=clamp_wid+gap` 居中布置，保证相邻 base 沿 Y 留实 gap（无穿模）| 接口 / clearance |

连续 scale 默认独立采样 → 派生 clamp_mount_edge（conditional 按 board_form 解析）→ inequality 把 clamp 行包络投影回 board 安装边可行域（回缩 clamp_wid），无法满足则回缩到最小。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

clamp 是唯一多重性来源，含 **1 根 count 轴**：

- `count_param`: **`n_clamps`**（沿安装边等距同构纸夹数）
- `N_range`: `n_clamps ∈ [1, 3]`（产品域；1=单夹基线、2=双夹宽 board、3=三夹宽 board。已覆盖样本：S0/多数 fork = 1；S6 = 2；S7 = 3）
- sampling domain（权重档）：单夹高频（weights [6,3,2]），3 夹稀有（长尾）
- copied object: 一只 `clamp_base_{i}`（FIXED）+ `clamp_mover_{i}`（REVOLUTE，机构由 Slot B 派生）；几何由共享 helper `_build_mech_meshes` 按机构生成，每夹重建（mesh 资产独立）
- naming: `clamp_base_{i}` / `clamp_mover_{i}` / `board_to_clamp_base_{i}` / `clamp_base_{i}_to_mover_{i}`，`for i, cy in enumerate(centers)`（S6/S7 已用此结构，直接作 module 源码）
- placement: 沿安装边等距——Y 中心 `cy = -span/2 + i·pitch`（`pitch=clamp_wid+gap`，居中），经 clamp_span_scale 缩放并 clamp 进安装边
- joint policy: 每夹 **独立** FIXED base + REVOLUTE mover，axis (0,−1,0)，统一 effort/velocity，open_limit 按机构；mover sleeve 捕获在各自 base barrel
- source/gating: 循环范式 S6 L267-337 / S7 L258-328；clamp_wid 越界回缩（§7 inequality）保证多夹不穿模

## 拓扑多样性审计

总组合数（离散槽）：board_form(3) × clamp_mechanism(4) × hang_hardware(2) × cover(2) = **48**
叠加 multiplicity：n_clamps(3 值) → 48 × 3 = **144 distinct 拓扑**（每个 n_clamps 改变 part/joint 计数 = 不同拓扑等价类）。
→ reachable_topology saturated=144（实测 probe），远超门槛。

理由：仅 48 个离散槽组合即 >10；clamp 数量轴再乘 3，distinct 拓扑 144 充裕。实测 50-seed distinct=41。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——加权选 4 个离散 slot（hang/cover 偏 none，board 偏 rect，mech 偏 spring_jaw）、加权采 n_clamps（小 N 偏多）、派生 clamp_mount_edge、采连续 scale、经 `resolve_config` 的 inequality 把 clamp 行投影回安装边可行域。`seed=0` 不特殊。无 regression overrides（无已知失败回归；若 sweep 暴露特定 seed 失败再稀疏加显式 override 并注明）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）（本类 144 上界可达；reachable_topology 已 saturated=144，实测 50-seed=41）。
Controlled local parameterization：初版即含 `board_scale` / `clamp_span_scale` / `lever_reach_scale` / `open_angle_scale`，全部 clamp/派生，受安装边包络、captured-pin、open range 约束，不改拓扑、REVOLUTE 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：board→mech→hang→cover→n_clamps→scales；加权（hang/cover 偏 none，小 N 偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | clamp 行越界回缩 clamp_wid；arch_ring 跳过 grip-reach 检查（平铺不压脚）；hang/cover 可并存（异面）| 无穿模/悬空/越界夹、captured pin sleeve 接触、cover 闭合平贴、ring swivel |
| controlled local variation | board_scale / clamp_span_scale / lever_reach_scale / open_angle_scale + clamp | 比例变化不破坏 sleeve 捕获、pivot 接触、安装边包络、joint origin、类别身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A board_form | 3 | yes | yes | 矩形 / 弧头 / 横向三个真实形态 |
| B clamp_mechanism | 4 | yes | yes | spring_jaw / toggle / wire_bail / arch_ring |
| C hang_hardware | 2 | yes | no | optional：{none, swivel_ring} |
| D cover | 2 | yes | no | optional：{none, folding_cover} |
| (mult) clamp | n_clamps[1-3] | — | — | 多重性轴，提供主拓扑乘子 |

## Validator

- slot_choices_for_seed returns implemented module names（board_form / clamp_mechanism / hang_hardware / cover + clamps_{n}）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：clamp 行越界回缩 clamp_wid；arch_ring grip-reach 跳过；hang/cover 异面并存
- optional regression overrides 初版为空（如加须稀疏 + 注明）
- controlled local scale params 全部 clamp，且不破坏 sleeve 捕获 / pivot 接触 / 安装边包络 / joint origin / 类别身份
- cross-part scale 依赖（clamp 行包络 vs 安装边）在 `resolve_config` 内 inequality 求解，不留到 builder 失败
- critical captured-pin 接口存在：mover sleeve-barrel 捕获、ring-eyelet 缠绕、cover knuckle-spine 缠绕
- clamp joints：每夹 FIXED base + REVOLUTE mover axis (0,−1,0)；ring REVOLUTE +X；cover REVOLUTE −X
- copied objects 遵循 `clamp_base_{i}`/`clamp_mover_{i}` 命名 + 等距 placement + 统一 joint policy
- rivet/eyelet/hinge-spine 恒为 inline visual（不建 FIXED 装饰 part）

## Reject cases

- 把 rivet / eyelet boss / hinge spine 做成 FIXED-joint 独立 part（违反"不动装饰内联 visual"）。
- 纸夹 mover 悬浮：sleeve 未捕获在 base barrel（静止应缠 barrel、合时压向 board grip 区）。
- clamp 行越出安装边：多夹沿 Y 溢出 board 边缘，或相邻 base 沿 Y 穿模（未做 clamp_wid 回缩）。
- 用连续 enum/尺寸冒充拓扑：只改 board 尺寸/颜色而不换 board_form/mechanism/hang/cover/夹数就当新拓扑。
- clamp 多重性退化：用手写命名的 2–3 只夹代替 `for i in range(N)` 循环发射 + 共享 helper。
- joint origin 漂离几何：FIXED base / REVOLUTE mover origin 未落在 footplate / pivot barrel 真实硬件上（baseline tol 0.015 m）。
- arch_ring 误用"压脚下压"语义（它平铺捕获打孔纸，不压脚；grip-reach 检查须跳过）。
- swivel ring 轴错误（应绕 eyelet X 轴，非绕 Z），或 cover 翻向错误（应绕长边 X，非短边）。
- config_from_seed 采样到未实现组合，或 n_clamps 超出 [1,3]。

## 与相邻类别的边界

- 不该混入：活页夹 / ring binder（多孔环册 + 封皮书脊为主体，board 退化；clipboard 身份 = board 载体 + 顶/侧边纸夹）。
- 不该混入：文件夹 / folder（纯对折塑料封套，无金属夹机构）。
- 不该混入：订书机 / stapler（铰链压钉 + 钉仓，出文具夹身份）。
- 不该混入：纯夹子 clip / 长尾夹 binder clip（无 board 载体）。
- 不该混入：立式公告板 / clipboard easel（带支腿立架，非手持薄 board）。
- Stationary 大类内：区别于 Pen / Scissors / Calculator 等无 board+夹身份的文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 模板已实现 `agent/templates/Stationary_Clipboard.py`（注册于 `cli/template.py` TEMPLATE_REGISTRY，slug=clipboard），`uv run articraft template sweep-pipeline clipboard` 分阶段 1/5/20/50 seeds 全 pass_rate=1.0，verdict=pass， distinct=41、reachable_topology saturated=144。剩余：viewer 目检（人工）。审核要点：① Slot C/D 各 2 candidate（optional 机构槽）的降级是否接受；② n_clamps N_range [1,3] 与权重档；③ foldback（S4）作为 multiplicity 循环范式参考而未单列 clamp_mechanism candidate 是否认可，或要求单列 foldback 机构。|

## 模板实现备注（可选）

- 共享 helper：`_board_solid`（按 board_form 分矩形/弧头/横向三路）、`_build_mech_meshes`（按 clamp_mechanism 返回 base/mover/caps 三元组）、`_cyl_between`（round-wire 3D 两点圆柱，wire_bail/arch_ring/swivel_ring 弯线共用，保证 island 连通）、`_clamp_centers_y`（按 n_clamps 等距布 cy）、`_emit_clamp`（FIXED base + REVOLUTE mover 统一发射）。
- captured-pin / element-scoped allow_overlap 注意点：mover pin sleeve 与 base barrel 过盈（参考 S0 L322）；swivel ring 线缠 eyelet boss；cover knuckle 缠 hinge spine；闭合纸夹 mover 压向 board grip 区——均在 `run_clipboard_tests` 声明 `ctx.allow_overlap`，joints 省略 MatingContract（captured-pin grandfathered）。
- joint-origin 落实：base mesh authored 于自身帧（footplate 底 z=0、pivot 在 local (0,0,PIVOT_RISE)），FIXED origin=(CLAMP_CENTER_X, cy, FACE_Z) 落在 footplate；REVOLUTE origin=(0,0,PIVOT_RISE) 落在 base barrel——避免 0.015 m baseline far-from-geometry。
- 派生与门控集中在 `resolve_config`：clamp_mount_edge（依 board_form）、open_limit（依 clamp_mechanism）、clamp 行包络回缩 clamp_wid。
- 弯线几何（wire_bail 腿 / arch 弧 / swivel ring 环）必须用 `_cyl_between`（3D 两点圆柱）逐段焊接，避免 `transformed(rotate)` extrude 方向错误导致 disconnected island（sweep 把 island WARN 提升为 FAIL）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A / B / mult | rect_rounded / spring_jaw 基线 | rec_..._f7e86c02 | `_board_solid` L73、`_clamp_base_solid` L85、`_clamp_lever_solid` L157、`_finger_caps_solid` L225、`base_to_lever` L296、allow_overlap L322 | 矩形 board + 弹簧夹 base/lever + captured-pin 装配基线 |
| S1 | B | toggle_lever | rec_..._togglelever | `_bracket_solid` L98、`_cam_lever_solid` L170、`bracket_to_lever` L296 | toggle cam lever 机构 |
| S2 | B | wire_bail | rec_..._wirebail | `_anchor_block_solid` L96、`_bail_path_joint_local` L139、`anchor_to_bail` L231 | 弯 wire U bail 机构 |
| S3 | B | arch_ring | rec_..._archring | `_spine_plate_solid` L77、`_arch_wire_points` L123、`spine_to_arch` L211 | 半圆 wire arch ring-binder 机构 |
| S4 | mult | clamp 循环范式参考 | rec_..._foldback | `_channel_body` L86、`for i in range(2)` L243/264、`channel_to_arm_{i}` L267 | 每夹独立 base+mover 的 for-i 循环 + 共享 helper + 统一 joint policy |
| S5 | A | side_landscape | rec_..._sideclamp | `_board_solid` L76-84、`base_to_lever` L303 | 横向 board + 侧边夹 |
| S6 | mult | clamps N=2 | rec_..._clamps2 | `_clamp_base_solid(y_center)` L93、`for i in range(NUM_CLAMPS)` L267/337 | 双夹等距多重性 + helper y_center 参数 |
| S7 | mult | clamps N=3 | rec_..._clamps3 | `for i in range(CLAMP_COUNT)` L71/258、`base_to_lever_{i}` L328 | 三夹等距多重性 |
| S8 | A | arched_top | rec_..._roundedtop | `_board_solid`(arch) L75-92、`threePointArc` L91 | 弧头 board 轮廓 |
| S9 | C | swivel_ring | rec_..._hangloop | `_eyelet_boss_solid` L255、`_swivel_ring_mesh` L285、`board_to_ring` L395+ | 顶角挂环 + eyelet boss captured swivel |
| S10 | D | folding_cover | rec_..._foldingcover | `_hinge_spine_solid` L251、`_cover_panel_solid` L270、`board_to_cover` L400 | 长边翻盖 part + hinge spine 承托 |
