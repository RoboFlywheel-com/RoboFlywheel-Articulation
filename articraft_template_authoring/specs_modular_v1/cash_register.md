# Electronic cash register — Modular Spec

> 来源小类：`picture/Retail_Shop Fixtures/Cash register`（2 origin parents + 4 单轴 fork 变体，均 compile PASS、均含 ≥1 非 fixed joint）。
> 上游 source map：`articraft_template_authoring/picture_source_maps/Retail_Shop_Fixtures__Cash_register.md`。
> 引用以 part/joint/helper **名字** 为准（`_prism_mesh` / `_register_shell` / `_till_insert` / `_bill_clip` / `add_key` / `console_to_printer_cover` / `drawer_to_lock` / `lcd_tilt` / `display_head_yaw` / `bill_clip_{i}_hinge` 等），行号按各样本 `rev_000001/model.py` 定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `cash_register` |
| template path | `agent/templates/cash_register.py` |
| test path (optional) | 不写，sweep 为唯一验收 |
| stage | `TEMPLATE_BUILT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 `drawer_housing` root + FIXED `register_body` ③ 头 + parallel-children：keypad / display / printer / drawer / lock，外加 coin 与 bill 两根多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（2 origin parents + 4 fork 变体；均 converged、compile PASS、均含 ≥1 非 fixed joint）|
| read_count | 6（全部 `model.py` 全文逐行读，含 build + run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below（6 个样本全部提供 module 来源）|

样本与采纳分工：
- **S_A 白色 ECR**（`rec_a-white-...546084bd`）：矩形 cabinet root + FIXED console（`_prism_mesh` 雕刻楔形壳：rear_housing / keyboard_deck / display_pod）；固定 display_pod（无关节 LCD）；铰接 printer_cover（revolute）；59 prismatic 键；`cabinet_to_drawer` prismatic；单排 coin till（`coin_divider_{0..3}` = 5 格）；`drawer_to_lock` revolute。**楔形 ③ 基线 + 固定显示 pod + 铰接打印机盖 + 单排 coin till + 旋转锁 + 键盘 prismatic 来源。**
- **S_B 炭灰 Sharp ER-A347**（`rec_a-dark-...7fc07459`）：root drawer_housing + FIXED register_body（`_register_shell` 楔形 cadquery）；twin open paper wells（无盖）；`lcd_tilt` revolute 操作员屏；`display_head_yaw` revolute 立杆顾客屏；`drawer_slide` prismatic；`_till_insert`（5 bill slots + 6 coin）+ `bill_clip_{0..4}` revolute 铰链；55 prismatic 键；静态 lock_cylinder。**倾仰 LCD + 立杆旋转顾客屏 + 开放双纸卷 + bill&coin till + 铰接压钞夹来源。**
- **S_flat flat POS 基座**（`rec_cash_register_var_body_flat_pos`，从 B fork）：`_register_shell` 楔形替换为浅平 `_pos_deck` 控制台，LCD 抬到直立 neck 上。**③ flat_pos_base 形态来源。**
- **S_tower 分层塔**（`rec_cash_register_var_body_tiered_tower`，从 A fork）：console 头重建为 3 层堆叠 box（keyboard / printer / display crown）替换单一楔形。**③ tiered_tower 形态来源。**
- **S_coin8**（`rec_cash_register_var_n_coin8`，从 A fork）：coin_divider count 4→7（8 格）。**coin 多重性样本（N=8）。**
- **S_bill7**（`rec_cash_register_var_n_bill7`，从 B fork）：bill-slot count 5→7 + 7 clips。**bill 多重性样本（N=7）。**

## 核心身份

台面式电子收银机（counter-top electronic cash register）：一只宽抽屉底座（`drawer_housing`，root，前面开口）承托一个 FIXED 收银机头（`register_body`），头上带键盘 deck、收据打印机构、操作员/顾客显示；底座前部是一只可 PRISMATIC 前后滑出的 `cash_drawer`，抽屉内是硬币/纸币钱盒（till），抽屉前面板带一枚可 REVOLUTE 旋转的钥匙锁。主用户机构 = 抽屉滑出 + 每键 −deck-normal 下压；叠加可选的打印机盖翻开 / LCD 倾仰 / 顾客屏旋转 / 压钞夹抬起 / 锁旋转。

默认成熟域：楔形 / 平板 POS / 分层塔三种机身形态；固定显示 pod / 倾仰 LCD / 立杆旋转顾客屏三种显示；铰接打印机盖 / 开放双纸卷两种打印机构；单排 coin till / bill&coin+压钞夹两种钱盒；coin 格 `[4,10]`、bill 格 `[3,8]`。

不该混入：裸 POS 电脑 / 显示器 / 平板支架 / 自助结账机；古董黄铜手摇机械收银机 / 台式计算器；自动售货机 / 出票机 / 保险箱。

## 槽位 + 候选模块表

> **建模注记**：`drawer_housing`（root，恒定）→ FIXED `register_body`（③ 形态）→ 一组 parallel children：keypad（N 键，挂 body）、display（挂 body）、printer（挂 body）、cash_drawer（PRISMATIC 挂 housing）、drawer_lock（REVOLUTE 挂 drawer）、bill_clips（REVOLUTE 挂 drawer）。body_form 通过返回一个 `BodyMounts` 结构，把 deck / printer / display 三个安装面单源传给下游 parallel children（Contract 3c）。

### Slot A：body_form（③ 主体形态家族 / Primary Form Family）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| classic_ecr_wedge（基线） | origin_anchor | S_A / S_B | S_A `_prism_mesh` L57-79 + console L182-206；S_B `_register_shell` L82-99 | eligible if compatible | 雕刻楔形 prism（rear 打印段抬起 + 前部斜键盘 deck）；`_prism_mesh` MeshGeometry 保留。form_subtype = **Volumetric Envelope Form**（斜楔体量包络）|
| flat_pos_base | forked_anchor | S_flat | `_pos_deck` L87-96 + body L154-191 | eligible if compatible | 低平控制 deck box（键在平面、LCD 上 neck）。form_subtype = **Planar Boundary Form**（平板矩形边界）|
| tiered_tower | forked_anchor | S_tower | 3 层堆叠 box L184-218 | eligible if compatible | 3 层堆叠 box（keyboard 基座 / printer 中层 / display crown）。form_subtype = **Macro Surface Construction**（阶梯塔状大尺度构成）|

### Slot B：display_mount（显示安装/机构，①②）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_display_pod（基线） | origin_anchor | S_A | display_pod L209-252（无关节）| eligible if compatible | 斜面 pod + bezel + screen，**inline 成 body visual**（不动 → 不建 part）|
| tilting_operator_lcd | origin_anchor | S_B | `lcd_tilt` L323-345 | eligible if compatible | body 上 bracket 承托 + `lcd_display` part，REVOLUTE 绕 +X 倾仰（±0.40）|
| pole_swivel_customer_display | origin_anchor | S_B | `display_head_yaw` L347-381 | eligible if compatible | body 上立杆 visual + `customer_display_head` part，REVOLUTE 绕 +Z 旋转（±1.5）|

### Slot C：receipt_printer（收据打印机构，②）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| hinged_printer_cover（基线） | origin_anchor | S_A | printer bay L254-279 + `printer_cover` L365-399 | eligible if compatible | printer bay 墙 + paper_roll（body visual）+ `printer_cover` part，REVOLUTE 绕 +X 翻开（0..1.35）|
| open_twin_paper_wells | origin_anchor | S_B | twin roll wells L169-194 | eligible if compatible | 双纸卷 well 墙 + 2 rolls + 2 paper strips，**inline body visual**（无盖 part）|

> 降级理由（2 candidate）：打印机构在样本池只有"铰接盖 vs 开放双卷"两个真实收敛形态；均结构性不同（盖为 REVOLUTE part，开放卷为纯 inline visual）。

### Slot D：drawer_till（钱盒，①）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| coin_only_single_row_till（基线） | origin_anchor | S_A / S_coin8 | coin_divider 循环 L436-442；S_coin8 N=8 | eligible if compatible | tray 壳 + 单排 `coin_divider_{i}`（N_coin 格，FIXED 装饰 visual），无纸币、无夹 |
| bill_and_coin_till_with_clips | origin_anchor | S_B / S_bill7 | `_till_insert` L102-116 + `_bill_clip` L119-129 + `bill_clip_{i}_hinge` L248-264；S_bill7 N=7 | eligible if compatible | 后排 bill 格 + 前排 coin 格 + 每 bill 格一只 REVOLUTE 压钞夹（tube+arm+pad），拓扑新增 N_bill part+joint |

> 降级理由（2 candidate）：钱盒有"纯硬币单排 vs 纸币+硬币+铰接夹"两个真实形态；bill&coin 相对 coin-only 新增整排 bill 格 + N_bill 个 REVOLUTE 夹（真实 part/joint 拓扑增量）。

> **注（cut-pockets → box compartments）**：S_B 的 `_till_insert` 用 cadquery 布尔 cut 出 bill/coin pockets；模板改用 box 隔板围成等效隔间（与 S_A coin_divider 的 box 做法一致），承载差异的结构层（后排 bill 隔间 + N_bill 铰接夹）完整保留、非缩放/涂装差异；换用 box 避免 cadquery 布尔、编译更快更稳。

## 槽位图（slot graph）

```
pattern: mixed（root housing + FIXED body head + parallel children + coin/bill multiplicity）

  drawer_housing (root, 恒定; 世界系 z=0 底, +Y 前, 顶面 BODY_SEAT_Z=0.137)
     │ FIXED housing_to_register_body @ (0,0,BODY_SEAT_Z)
  register_body (Slot A ③; body-local z=0 於 seat 面; 返回 BodyMounts)
     ├── keypad[N=5x5]     PRISMATIC 每键 −deck-normal @ deck 面（wedge 斜/flat·tower 平）
     ├── display_mount(B)  pod=inline visual / lcd=REVOLUTE +X / pole_head=REVOLUTE +Z
     └── receipt_printer(C) cover=REVOLUTE +X part / open_wells=inline visual
  drawer_housing
     └── cash_drawer       PRISMATIC +Y (housing_to_drawer, [0, drawer_travel])
           ├── drawer_lock     REVOLUTE +Y (drawer_to_lock, ±1.4)
           ├── till(D)         coin_only=FIXED 隔板 visual / bill&coin=隔板 + N_bill 夹
           └── bill_clip_{i}   REVOLUTE +X (bill_clip_{i}_hinge, [0,0.90]) ×N_bill（仅 bill&coin）
```

接口点位：
- **housing → register_body**：FIXED，origin=(0,0,BODY_SEAT_Z)（counter_top 顶面）；body 底面 body-local z=0 落於此面 → 接触；grandfathered（无 MatingContract，靠面接触 + FIXED origin-on-interface）。
- **body → key_{r}_{c}**：PRISMATIC，origin 在 deck 面 `(cx, cy, deck_z(cy))`、rpy=(−deck_pitch,0,0)，axis (0,0,−1)，range [0,KEY_TRAVEL]；键帽 skirt 嵌入 deck（element-scoped allow_overlap keycap↔body_shell）。
- **body → lcd_display**：REVOLUTE，origin 在 bracket 顶，axis (1,0,0)，range [−0.40,0.40]；lcd_housing 底坐嵌 bracket（allow_overlap）。
- **body → customer_display_head**：REVOLUTE，origin 在立杆顶，axis (0,0,1)，range [−1.5,1.5]；collar 套杆顶（allow_overlap，轴=杆对称中心线）。
- **body → printer_cover**：REVOLUTE，origin 在 bay 后墙顶，axis (1,0,0)，range [0,1.35]；盖闭合搁 bay 墙缘（接触）。
- **housing → cash_drawer**：PRISMATIC，axis (0,1,0)，range [0,drawer_travel]；till 底贴 housing 底（allow_overlap tray_floor↔bottom_panel）。
- **drawer → drawer_lock**：REVOLUTE，axis (0,1,0)（barrel 对称轴），range [−1.4,1.4]；barrel 后端贴 drawer_front。
- **drawer → bill_clip_{i}**：REVOLUTE，origin 在 till 后墙，axis (1,0,0)，range [0,0.90]；hinge tube 捕获在后墙（allow_overlap clip_tube↔tray_rear_wall）。
- **互斥/可选/派生**：Slot B 三选一；Slot C 二选一；bill_clips 仅 bill&coin till 存在；display/printer 在机身后区按 x 分侧避让（printer 偏左、display 偏右）。

## 每槽位 Module Emits / Interfaces

### Slot A / classic_ecr_wedge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `register_body`（`body_shell` = `_prism_mesh` 楔形 prism）| S_A `_prism_mesh` L57-79 |
| downstream interface | BodyMounts：斜 deck 面（deck_pitch>0）+ rear 打印顶 + 右侧 display 座 | S_A / S_B |

### Slot A / flat_pos_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `register_body`（`body_shell` = 平 deck Box）| S_flat `_pos_deck` L87-96 |
| downstream interface | BodyMounts：平 deck 面（pitch=0）+ deck 后区打印 + neck/pole display | S_flat L154-191 |

### Slot A / tiered_tower
| emits | 描述 | 来源 |
|---|---|---|
| parts | `register_body`（`body_shell` 基座 + `printer_tier` + `display_crown` 三 Box）| S_tower L184-218 |
| downstream interface | BodyMounts：基座平 deck + 中层 printer 顶 + 右偏 crown display | S_tower |

### Slot B / fixed_display_pod
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`display_pod`/`display_bezel`/`display_screen` inline body visual | S_A L209-252 |

### Slot B / tilting_operator_lcd
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lcd_display`（lcd_housing + lcd_screen）；body 上 `lcd_bracket` visual | S_B L323-345 |
| internal joints | `body_to_lcd` REVOLUTE axis (1,0,0) range [−0.40,0.40] | S_B `lcd_tilt` |

### Slot B / pole_swivel_customer_display
| emits | 描述 | 来源 |
|---|---|---|
| parts | `customer_display_head`（collar+head_shell+digit_window+digit_band）；body 上 `display_pole` visual | S_B L347-381 |
| internal joints | `body_to_customer_display_head` REVOLUTE axis (0,0,1) range [−1.5,1.5] | S_B `display_head_yaw` |

### Slot C / hinged_printer_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | `printer_cover`（rear/front panel + 2 rails + cutter）；body 上 bay 墙 + paper_roll visual | S_A L254-399 |
| internal joints | `body_to_printer_cover` REVOLUTE axis (1,0,0) range [0,1.35] | S_A `console_to_printer_cover` |

### Slot C / open_twin_paper_wells
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`well_*_wall_{i}` + `paper_roll_{i}` + `paper_strip_{i}` inline body visual | S_B L169-194 |

### Slot D / coin_only_single_row_till
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`tray_*` + `coin_divider_{i}`（N_coin−1）drawer visual | S_A L404-442 |

### Slot D / bill_and_coin_till_with_clips
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tray_*` + `till_mid_divider` + `bill_divider_{i}` + `coin_divider_{i}` drawer visual；`bill_clip_{i}` part ×N_bill | S_B `_till_insert` L102-116、`_bill_clip` L119-129 |
| internal joints | `bill_clip_{i}_hinge` REVOLUTE axis (1,0,0) range [0,0.90] ×N_bill | S_B L248-264 |

### 核心恒定件
| emits | 描述 | 来源 |
|---|---|---|
| `cash_drawer` | drawer_front + till（Slot D），`housing_to_drawer` PRISMATIC +Y | S_A L404-451 / S_B L218-246 |
| `drawer_lock` | lock_barrel + face_ring + keyway，`drawer_to_lock` REVOLUTE +Y | S_A L454-481 |
| keypad `key_{r}_{c}` | 5×5 Box 键帽，`body_to_key_{r}_{c}` PRISMATIC | S_A/S_B add_key |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | {classic_ecr_wedge, flat_pos_base, tiered_tower} | — | choice | 加权 procedural sampler（楔形偏多）| Slot A |
| display_mount | enum | {fixed_display_pod, tilting_operator_lcd, pole_swivel_customer_display} | — | choice | sampler | Slot B |
| receipt_printer | enum | {hinged_printer_cover, open_twin_paper_wells} | — | choice | sampler | Slot C |
| drawer_till | enum | {coin_only_single_row_till, bill_and_coin_till_with_clips} | — | choice | sampler | Slot D |
| n_coin | int | [4, 10] | 5 | independent | 加权采样（5-6 高频、9-10 稀有）后 clamp | §8 / S_A,S_B,S_coin8 |
| n_bill | int | [3, 8] | 5 | conditional | 仅 bill&coin till 采纳；slot_choices 写 `no_bills` 否则 | §8 / S_B,S_bill7 |
| material_style | enum | {white_ecr, charcoal_ecr, light_pos} | white_ecr | choice | ⑥ 涂装 | S_A/S_B/S_flat |
| body_width_scale | float | [0.94, 1.06] | 1.0 | independent | 缩放 body_half_w；deck/printer/display 座随之派生（BodyMounts 单源）| S_A/S_B envelope |
| drawer_travel_scale | float | [0.90, 1.08] | 1.0 | independent | 缩放 drawer_travel；抽屉全程仍留 retain（min_overlap 测试）| S_A/S_B |
| key_pitch_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放键帽尺寸；clamp 保 ≤0.82×cell pitch（相邻键不触）| S_A/S_B |
| (—) | constraint | — | — | inequality | 键帽 ≤ 0.82×min(pitch_x,pitch_y)（防相邻键穿模）；在 `_emit_keypad` clamp | 接口 |

连续 scale 先独立采样 → BodyMounts 由 body_form + body_width_scale 派生所有安装面（单源，Contract 3c）→ 键帽尺寸按 pitch clamp。全部在 `resolve_config` / `_emit_keypad` 内求解。

## 7.5 编译预算 / compile budget

自报每-seed 预算 **≤15s**（依据：全部 Box/Cylinder primitive + 每 build 仅一个 `_prism_mesh`（~12 顶点凸 prism，仅楔形形态）；无 cadquery 布尔）。实测 sweep-pipeline 48 seeds 墙钟 ~13s（16 workers）。分档 tessellation 非必要（无高精度旋转/放样面）。

## Multiplicity / Copy Logic

**2 根独立 count 轴**，按规则各自声明：

- **coin compartments**（`n_coin`）
  - N_range `[4, 10]`（产品域）；测试偏小（5-6 常见），尾部 9-10 稀有
  - sampling domain 权重：`{4:3, 5:6, 6:6, 7:3, 8:3, 9:1, 10:1}`
  - 已覆盖样本：S_A=5（4 dividers）、S_B=6、S_coin8=8
  - copied object：`coin_divider_{i}` Box 隔板（N_coin−1 个）；even x-spacing；FIXED 装饰 visual on cash_drawer；两种 till 均有 coin 排
  - naming：`coin_divider_{i}`，`for i in range(n_coin-1)`
- **bill compartments + clips**（`n_bill`）
  - N_range `[3, 8]`（产品域）；权重 `{3:3,4:4,5:6,6:3,7:2,8:1}`
  - 已覆盖样本：S_B=5、S_bill7=7
  - copied object：`bill_divider_{i}`（N_bill−1）+ `bill_clip_{i}` part（N_bill，每格一只）+ `bill_clip_{i}_hinge` REVOLUTE；even x-spacing；hinge tube 捕获后墙
  - naming：`bill_clip_{i}` / `bill_clip_{i}_hinge`，`for i in range(n_bill)`
  - gating：仅 `drawer_till==bill_and_coin_till_with_clips` 时发射；否则 slot_choices 写 `no_bills`
- **keypad**（`KEY_COLS×KEY_ROWS`=5×5，恒定）：源样本键盘是异构多块网格（function/dept/numeric/mode/payment），**非单一干净 count_param**，故**不作 N 采样轴**（source map 明确排除），模板用固定规则网格 loop 发射代表键盘。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | cabinet→FIXED head→drawer 链（S_A,S_B）；bill&coin till 相对 coin-only **新增整排 bill part + N_bill REVOLUTE 夹**；display/printer 候选新增/去除 part（pod=0 part、lcd/pole=1 part；cover=1 part、open_wells=0 part）。全部 forked/origin source-backed |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：coin `[4,10]` + bill `[3,8]` 两轴，各带权重档 |
| ② 关节类型 | 边换 type/轴 | 有 | PRISMATIC drawer(+Y)、PRISMATIC 键(−deck normal)、REVOLUTE printer_cover(+X)、REVOLUTE lock(+Y)、REVOLUTE lcd_tilt(+X)、REVOLUTE pole_yaw(+Z)、REVOLUTE bill_clip(+X)；全 origin source-backed；每种在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有（登记进 slot_choices 的 `body_form` slot） | classic_ecr_wedge（Volumetric Envelope Form，`_prism_mesh` 楔体）/ flat_pos_base（Planar Boundary Form，平板）/ tiered_tower（Macro Surface Construction，阶梯塔）。3 个 source-backed 原型 |
| ④ 表面装饰 | 叠加表面细节 | 无（结构性最小）| 装饰（品牌牌/数字带/键色）仅作 host visual 派生的颜色/小 visual（digit_band 贴 head 前面、键帽 accent 色）；不引入独立装饰 part，也不做 count 轴。多样性由 ①②③ + 多重性承载 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | body_width_scale[0.94,1.06]、drawer_travel_scale[0.90,1.08]、key_pitch_scale[0.92,1.08]（见 §7）。关节运动包络：drawer PRISMATIC +Y [0,drawer_travel]（全程 retain）；键 PRISMATIC −deck normal [0,0.0026]；printer_cover REVOLUTE +X [0,1.35]（向上翻）；lcd REVOLUTE +X [−0.40,0.40]；pole REVOLUTE +Z [−1.5,1.5]；bill_clip REVOLUTE +X [0,0.90]（短翻片，抬起不穿 counter_top）；lock REVOLUTE +Y [−1.4,1.4]。motion_test_plan：`fail_if_parts_overlap_in_sampled_poses` + 每机构一条 targeted `ctx.pose`（drawer 滑出、键下压、cover 上翻、lcd 后倾、pole 旋转、bill_clip 抬起、lock 双向）|
| ⑥ 涂装 | 只改材质/颜色 | 有 | 3 档 palette：white_ecr / charcoal_ecr / light_pos（塑料/漆面大类；配色 ≥3）|

**收尾自检**：sweep axis_realization 实测 body_form 3/3、display_mount 3/3、receipt_printer 2/2、drawer_till 2/2、coin N∈{4..10}、bill N∈{3..8}+no_bills 全部出现；distinct slot-tuple = 45。

## 采样与覆盖审计

总组合数（离散槽）：body_form(3) × display_mount(3) × receipt_printer(2) × drawer_till(2) = **36**
叠加 multiplicity：coin(7 值) × bill(6 值，仅 bill&coin) → 远超门槛。

理由：仅 36 个离散槽组合即 >10；coin/bill 多重性再乘。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic 加权采样（body_form 楔形偏多；display/printer/till 均匀；coin/bill 小 N 偏多），采连续 scale，`resolve_config` clamp。`seed=0` 不特殊。无 regression overrides。
Topology target：1000-seed slot-tuple distinct（report-only）；36 离散 × 多重性 → 富类别，实测 48 seeds 已达 45。
Controlled local parameterization：`body_width_scale` / `drawer_travel_scale` / `key_pitch_scale`，全部 clamp/派生；body_width_scale 驱动 BodyMounts 单源派生所有安装面，不破坏 parallel-children 接口 / clearance / joint origin / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序 body_form→display→printer→till→(n_coin,n_bill)→scales；加权 | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | bill_clips 仅 bill&coin till；display/printer 后区按 x 分侧（printer 左 / display 右，tower crown 右偏）避让；键帽 ≤0.82 cell pitch | 无穿模/悬空/越界；cover 上翻不撞 crown；bill_clip 抬起不穿 counter_top |
| controlled local variation | body_width/drawer_travel/key_pitch scale + clamp | 比例变化不破坏接口/clearance/joint origin/类别身份 |
| regression overrides | none | — |
| random sweep | 初轮 0-35（+corner），成熟审计 0-999 | axis_realization；viewer 目检 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 3 | yes | yes | ③ 形态 slot |
| B display_mount | 3 | yes | yes | inline pod / tilt lcd / pole swivel |
| C receipt_printer | 2 | yes | no | 铰接盖 / 开放双卷 |
| D drawer_till | 2 | yes | no | coin-only / bill&coin+clips |
| (mult) coin | [4,10] | — | — | 多重性轴 |
| (mult) bill | [3,8] | — | — | 多重性轴（conditional）|

## Validator

- slot_choices_for_seed returns implemented module names（body_form/display_mount/receipt_printer/drawer_till + coin/bill multiplicity）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility gating：bill_clips 仅 bill&coin；n_bill 在 coin-only 记 `no_bills`；键帽尺寸 clamp
- controlled local scale 全部 clamp，且不破坏接口/clearance/joint origin/类别身份
- 关键 seated/captured 接口存在：body 坐 counter_top、键嵌 deck、lcd 坐 bracket、collar 套杆、cover 搁 bay、bill_clip tube 捕获后墙、till 底贴 housing
- key joints：键 PRISMATIC −deck normal；drawer PRISMATIC +Y；lock/lcd/cover/bill_clip/pole REVOLUTE 各自轴
- 复制件遵循 `coin_divider_{i}` / `bill_clip_{i}` 命名 + even spacing + 统一 joint policy
- 不动装饰（pod / open wells / coin dividers / 品牌色）为 host visual，不建 FIXED 装饰 part

## Reject cases

- 把 fixed_display_pod / open paper wells / coin dividers 做成 FIXED-joint 独立 part（违反不动装饰内联）。
- 键帽悬浮或穿出 deck（未坐嵌 deck 面）；相邻键穿模（键帽超 cell pitch）。
- bill_clip 抬起穿过 counter_top（arm 过长/行程过大）——须短翻片 + 行程 clamp。
- tower 机身 printer bay 与 display crown 同轴不避让（cover 上翻撞 crown）——须按 x 分侧。
- drawer_front 与 till 前墙脱开（island）——须面接触。
- coin-only till 采到 bill_clips，或 bill_clip 数与 bill 格数不符。
- 用连续 scale/涂装冒充拓扑：只改尺寸/颜色不换 body_form/display/printer/till/N。
- config_from_seed 采到未实现组合。

## 与相邻类别的边界

- 不该混入：POS 电脑 / 显示器 / 平板支架 / 自助结账机（收银机身份 = 抽屉 + 键盘 + 打印 + 显示 合体）。
- 不该混入：古董手摇机械收银机 / 台式计算器（无抽屉 till + 无收据打印）。
- 不该混入：自动售货机 / 出票机 / 保险箱（不同机构语义）。
- Retail_Shop Fixtures 内区别于货架 / 展示柜等无机构固定装置。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 模板已实现 `agent/templates/cash_register.py`（注册于 `cli/template.py`）。`sweep-pipeline cash_register` fast/final/corner 三阶段全 pass_rate=1.0、verdict=pass、corner 0 fail、distinct slot-tuple=45、6 轴 axis_realization 全候选出现。剩余：viewer 目检（人工）。待审：① Slot C/D 各 2 candidate 降级是否接受；② bill&coin till 的 cut-pockets→box-compartments 采纳是否认可；③ keypad 固定 5×5（非 N 轴）是否认可。|

## 模板实现备注（可选）

- 共享单源：`BodyMounts`（body_form 返回，把 deck/printer/display 三安装面单源传给 keypad/display/printer parallel children，Contract 3c）；`_bay_bounds`（printer bay 边界）；`_emit_coin_dividers`（两种 till 复用）；`_build_bill_clip`（N_bill 复用）。
- captured-pin / seated 全部 grandfathered（无 MatingContract，仿源记录）：靠 FIXED origin-on-interface（body 坐 counter_top）、REVOLUTE 轴-on-symmetry-axis（lock/pole/cover/clip）、PRISMATIC 原点豁免（键/drawer），配 element-scoped allow_overlap（键嵌 deck、lcd 坐 bracket、collar 套杆、clip tube 捕获后墙、till 底贴 housing）。
- tower 机身 crown 右偏 + printer bay 左偏（x 分侧），复现 S_tower 源里 crown 与 printer bay 分侧避让。
- bill_clip 为短翻片（arm ≤45mm、行程 ≤0.90），抬起不穿抽屉上方 counter_top。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S_A | A/B/C/D/core | wedge / pod / cover / coin-only / keys / lock / drawer | rec_a-white-...546084bd | `_prism_mesh` L57-79、display_pod L209-252、printer_cover L254-399、coin_divider L436-442、drawer_to_lock L454-481、add_key L318-360 | 楔形 ③ + 固定 pod + 铰接盖 + 单排 coin + 旋转锁 + 键盘 + 抽屉基线 |
| S_B | A/B/C/D/core | wedge / tilt+pole / open wells / bill&coin+clips | rec_a-dark-...7fc07459 | `_register_shell` L82-99、`lcd_tilt` L323-345、`display_head_yaw` L347-381、open wells L169-194、`_till_insert` L102-116、`_bill_clip` L119-129 | 倾仰 LCD + 立杆顾客屏 + 开放双卷 + bill&coin till + 压钞夹 |
| S_flat | A | flat_pos_base | rec_cash_register_var_body_flat_pos | `_pos_deck` L87-96 | 平板 POS ③ 形态 |
| S_tower | A | tiered_tower | rec_cash_register_var_body_tiered_tower | 3 层堆叠 L184-218 | 阶梯塔 ③ 形态 |
| S_coin8 | mult | coin N=8 | rec_cash_register_var_n_coin8 | coin_divider count 4→7 | coin 多重性样本 |
| S_bill7 | mult | bill N=7 | rec_cash_register_var_n_bill7 | bill count 5→7 + 7 clips | bill 多重性样本 |
