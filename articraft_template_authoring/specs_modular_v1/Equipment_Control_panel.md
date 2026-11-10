# Control Panel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `control_panel` |
| template path | `agent/templates/Equipment_Control_panel.py` |
| test path | `tests/agent/test_control_panel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 (3 parents + 10 forked variants) |
| read_count | 13 |
| read_scope | 全部读完：3 个 device-archetype parent + 10 个 picture-subcat fork variant 的 `model.py` 逐文件扫描 |
| samples_adopted_as_module_sources | 13（全部采纳；每个 fork 各覆盖一个 slot 取值或 multiplicity 轴） |
| source_index_policy | only adopted module sources are indexed below |

**数据根说明（dataset-root caveat）**：本 spec 的样本均为 articraft_data 仓内 workbench-only 的 picture-subcat fork，未 promote 到正式 dataset；它们由 `articraft fork` 从 3 个 parent 派生、`collections=['workbench']`、绑入 `Equipment__Control_panel` subcat shard。引用一律按 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`（相对 articraft_data 仓根）。

- parents（3 种 device archetype，各覆盖不同 mount/control/readout 取值）:
  - `rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180035_243303_c28c270c` (P1 "rod" / `pendant_control_station`)
  - `rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180037_817594_647d2061` (P2 "rail" / `rail_mounted_control_panel`)
  - `rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180040_391603_ab3b9f65` (P3 "conduit" / `industrial_disconnect_panel`)
- variants（10，每个 dir == record_id）: `rec_control_panel_var_mountA_backplate`, `rec_control_panel_var_mountA_railN`, `rec_control_panel_var_ctrlB_rotaryknob`, `rec_control_panel_var_ctrlB_togglebank`, `rec_control_panel_var_ctrlB_mushroom`, `rec_control_panel_var_ctrlB_pushbtn_railrotary`, `rec_control_panel_var_readC_gauge`, `rec_control_panel_var_readC_lcdrow`, `rec_control_panel_var_N3_buttons`, `rec_control_panel_var_N6_buttons`。

## 核心身份

Control panel（工业控制面板 / 控制箱 / 隔离开关柜）是一个**承载机构（mount）+ 前面控制簇（control）+ 前面显示簇（readout）** 三层组合的设备外壳。物理含义：一只刚性壳体（die-cast 小盒 / 圆角塑料壳 / 钣金柜）被某个固定机构挂载到墙、轨、吊杆或线管上（mount 决定 root 与所有跨件 FIXED 联接），壳体前面（或侧壁）布置一组**真实可动**的人机输入件（push-button 内压、selector/toggle/disconnect-handle 旋转、mushroom e-stop 深行程锁定 —— hero 关节都在这里），以及一组**纯 housing 固定 visual** 的显示 / 指示件（LCD、数显窗、模拟表、LED 行、通风槽 —— 无关节）。

默认成熟域：mount ∈ {pendant_rod, rail_clamp, conduit_wall, wall_backplate}；control ∈ {round_push_buttons, rotary_disconnect_handle, rotary_selector_knob, toggle_switch_bank, mushroom_estop}；readout ∈ {none/bare_bezel, rect_lcd_with_leds, digital_display_window, analog_round_gauge, lcd_led_vent_cluster}；前排圆 push-button 数 `BUTTON_COUNT` 为一根 multiplicity 轴。

边界（不该混入）：
- 不是仪表 / 收音机：control 簇必须以**输入件**为主导，不能把整面做成单旋钮 + 大屏读作仪表。
- 不是断路器 / 配电盘内部：本类描述的是带壳的人机面板，不展开内部母排 / 端子排接线拓扑。
- 不是 keypad / 键盘：push-button 是少量大圆动量按钮（2–12），不是密排字符键阵。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | P1 `...c28c270c` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180035_243303_c28c270c/revisions/rev_000001/model.py:L193-L344` | pendant_rod mount + round_push_buttons(手写 top/bottom) + side toggle；readout=none(裸 bezel) |
| S2 | P2 `...647d2061` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180037_817594_647d2061/revisions/rev_000001/model.py:L258-L340` | rail_clamp mount + round_push_buttons(手写 left/right) + rect_lcd_with_leds |
| S3 | P3 `...ab3b9f65` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-cont_20260609_180040_391603_ab3b9f65/revisions/rev_000001/model.py:L303-L407` | conduit_wall mount + rotary_disconnect_handle(hero) + digital_display_window + 门面 `range(4)` fixed-visual 按钮行 |
| S4 | `rec_control_panel_var_mountA_backplate` | `data/records/rec_control_panel_var_mountA_backplate/revisions/rev_000001/model.py:L308-L330` | wall_backplate mount module（平板 + 四角 keyhole 凸台，替换双轨夹块） |
| S5 | `rec_control_panel_var_mountA_railN` | `data/records/rec_control_panel_var_mountA_railN/revisions/rev_000001/model.py:L343-L417` | rail_clamp 跨体实现（双轨 + saddle/web/pads rear clamp 装到大 enclosure 机体） |
| S6 | `rec_control_panel_var_ctrlB_rotaryknob` | `data/records/rec_control_panel_var_ctrlB_rotaryknob/revisions/rev_000001/model.py:L335-L367` | rotary_selector_knob control module（滚花旋钮 + 指针，REVOLUTE +Y ±135°） |
| S7 | `rec_control_panel_var_ctrlB_togglebank` | `data/records/rec_control_panel_var_ctrlB_togglebank/revisions/rev_000001/model.py:L351-L372` | toggle_switch_bank control module（SWITCH_COUNT=3 拨杆，REVOLUTE +X ±0.45） |
| S8 | `rec_control_panel_var_ctrlB_mushroom` | `data/records/rec_control_panel_var_ctrlB_mushroom/revisions/rev_000001/model.py:L296-L347` | mushroom_estop control module（大蘑菇深行程锁定柱塞，PRISMATIC -X 0.012） |
| S9 | `rec_control_panel_var_ctrlB_pushbtn_railrotary` | `data/records/rec_control_panel_var_ctrlB_pushbtn_railrotary/revisions/rev_000001/model.py:L421-L468` | round_push_buttons 在 P3 机体上的跨体实现（侧门一排 PRISMATIC +X，SIDE_BUTTON_COUNT=4，去掉旋转手柄） |
| S10 | `rec_control_panel_var_readC_gauge` | `data/records/rec_control_panel_var_readC_gauge/revisions/rev_000001/model.py:L321-L346` | analog_round_gauge readout module（金属圈+刻度盘+11 tick+指针+hub，纯 fixed visual） |
| S11 | `rec_control_panel_var_readC_lcdrow` | `data/records/rec_control_panel_var_readC_lcdrow/revisions/rev_000001/model.py:L274-L313` | lcd_led_vent_cluster readout module（给 P1 裸 bezel 补凹陷 LCD + 3 LED 行 + 竖排通风槽） |
| S12 | `rec_control_panel_var_N3_buttons` | `data/records/rec_control_panel_var_N3_buttons/revisions/rev_000001/model.py:L379-L429` | multiplicity copy-logic 源（N=3）：`for i in range(BUTTON_COUNT)` 发射 `button_{i}` part + `door_to_button_{i}` PRISMATIC |
| S13 | `rec_control_panel_var_N6_buttons` | `data/records/rec_control_panel_var_N6_buttons/revisions/rev_000001/model.py:L372-L423` | multiplicity copy-logic 源（N=6）：同一循环发射 `button_{i}` part + `button_slide_{i}` PRISMATIC |

## 槽位 + 候选模块表

### Slot A：mount（device 后部承载机构 —— 决定 root 与所有跨件 FIXED 联接）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `pendant_rod` | P1 `...c28c270c` | L202-L266（rod root + `_build_cable_gland` L119-L138；`rod_to_housing` FIXED L260-L266） | eligible if compatible | 竖直钢吊杆为 root；盒体经上下 `top_gland`/`bottom_gland` captive 挂在杆上，rod 穿过 housing |
| `rail_clamp` | P2 `...647d2061` | L236-L315（`_build_clamp_shape` L236-L250、`_build_rail_shape` L253-L255；`clamp_to_rail_top`/`clamp_to_rail_bottom` FIXED L309-L315） | eligible if compatible | 壳后夹块开双半管槽，两根独立横轨各为独立 part 卡入槽（rail = child，FIXED）；railN 变体把同一 mount 移植到大 enclosure（`_build_rear_clamp_shape` saddle+web+pads，`...mountA_railN/...model.py:L255-L330`） |
| `conduit_wall` | P3 `...ab3b9f65` | L245-L319（`_build_conduit_shape` L245-L295：4 竖管+strap+drop+jbox 单体）；`base_to_enclosure` FIXED L374-L380 | eligible if compatible | 竖直线管束为 root，横向 strap 贴柜后承载柜体；柜为 enclosure child |
| `wall_backplate` | `rec_control_panel_var_mountA_backplate` | L233-L330（`_build_wall_back_plate_shape` L233-L263、`_build_mount_tab_shape` L264-L280；`housing_to_back_plate` FIXED@`BACK_Y` L324-L330） | eligible if compatible | 平矩形墙板 + 四角 keyhole 螺柱凸台（`mounting_tab_0..3`），替换双轨夹块，板贴壳后缘 flush |

注：Slot A = 4 个 distinct 结构家族。`rail_clamp` 在两个机体上各有实现（P2 小塑料壳 / railN 大 enclosure），证明该 mount module 可跨 body 复用，但计为**一个**家族。

### Slot B：control（主输入簇 —— hero 关节所在）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `round_push_buttons`（基线） | P2 `...647d2061` | L212-L233（`_build_button_shape`）；L317-L338（emit `button_left`/`button_right` + `press_button_{...}` PRISMATIC -Y）；P1 同义实现 `...c28c270c/...model.py:L141-L163`+`L268-L307`（PRISMATIC -X） | eligible if compatible | 圆形动量按钮，沿前面板法向 PRISMATIC 短行程内压；**N 轴的几何单元** |
| `rotary_disconnect_handle` | P3 `...ab3b9f65` | L169-L230（`_build_operator_base_shape` L169-L188、`_build_handle_shape` L191-L230）；`operator_handle` REVOLUTE +X 160° L395-L405 | eligible if compatible | 侧壁旋转隔离手柄 hub+lever，OFF↓/ON↑，绕侧壁 +X operator 轴（唯一非前面法向 hero） |
| `rotary_selector_knob` | `rec_control_panel_var_ctrlB_rotaryknob` | L220-L253（`_build_selector_knob_geometry`/`_build_selector_stem`/`_build_pointer_mark`）；`turn_selector` REVOLUTE +Y ±135° L357-L367 | eligible if compatible | 单个滚花选择旋钮绕面法向(+Y)转，带指针刻度 `pointer_mark` |
| `toggle_switch_bank` | `rec_control_panel_var_ctrlB_togglebank` | L223-L262（`_build_switch_socket`/`_build_toggle_shape`）；`SWITCH_COUNT=3` L67；emit `switch_{idx}`+`housing_to_switch_{idx}` REVOLUTE +X ±0.45 L351-L372 | eligible if compatible | 一排小拨杆，各在前面 bushing(`switch_socket_{idx}`) 内 pitch 摆动；自带内部 multiplicity(SWITCH_COUNT) |
| `mushroom_estop` | `rec_control_panel_var_ctrlB_mushroom` | L142-L191（`_build_estop_guard`/`_build_estop_gasket`/`_build_estop_mushroom_cap`）；`housing_to_emergency_stop` PRISMATIC -X 深 0.012 L332-L347 | eligible if compatible | 单个大蘑菇急停（guard+gasket+cap），深行程锁定柱塞，替换两圆按钮 |

注：Slot B 收敛为 5 个 distinct module。`pushbtn_railrotary`（S9，`...ctrlB_pushbtn_railrotary/...model.py:L258-L297`+`L421-L468`，`SIDE_BUTTON_COUNT=4` PRISMATIC +X）是 `round_push_buttons` 模块在 P3 family 的**跨体实现 + 演示 rotary→pushbtn 替换**，计入 `round_push_buttons` 家族，不另算第 6 个 module。

### Slot C：readout（前面显示 / 指示簇 —— 全为 housing 固定 visual，无关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rect_lcd_with_leds` | P2 `...647d2061` | L179-L209（`_build_display_glass`/`_build_display_bezel`/`_build_led`）；vent slots `SLOT_COUNT=5` cut L153-L160；emit L262-L283 | eligible if compatible | 矩形凹陷 LCD + 顶部 3 LED + 左列通风槽 |
| `digital_display_window` | P3 `...ab3b9f65` | L153-L155（`_build_display_glass_shape`）；门 pocket cut L109-L117；emit L347-L352 | eligible if compatible | 门上单块凹陷数显窗 |
| `analog_round_gauge` | `rec_control_panel_var_readC_gauge` | L195-L255（`_build_gauge_rim`/`_build_gauge_dial`/`_build_gauge_needle`/`_build_gauge_hub`、`_build_gauge_tick` L210-L226）；emit `gauge_tick_{idx}` `for idx in range(11)` L321-L346 | eligible if compatible | 沉孔圆形模拟表：金属圈+刻度盘+11 tick+指针+中心 hub |
| `lcd_led_vent_cluster` | `rec_control_panel_var_readC_lcdrow` | L208-L235（`_build_lcd_frame`/`_build_led_lens`）；`VENT_SLOT_COUNT=4` L80；emit `indicator_led_{i}`(range 3)+`vent_slot_{i}` L274-L313 | eligible if compatible | 给原裸 bezel(P1) 加凹陷 LCD + 3 色 LED 行 + 竖排通风槽 |

注：Slot C = 4 个 distinct candidate（两 parent + 两变体全覆盖，含给 P1 补 readout 的 lcdrow）。空态 `none / bare_bezel`（P1 裸 bezel，`...c28c270c/...model.py:L221-L227`）是 readout 的可选缺省（不发任何 readout visual），不计入 4 个 distinct candidate。

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A mount]  --(ROOT)-->  carries housing
[Slot A mount]  -- FIXED (mount-specific seat) -->  [housing]
[housing]       -- hero non-FIXED, 贴前面板面/侧壁 -->  [Slot B control]
[housing]       -- FIXED visual (no joint), 沉入前面 pocket -->  [Slot C readout]
[Slot B control] -- ×BUTTON_COUNT PRISMATIC copies (round_push_buttons only) -->  [button_{i}]
```

说明：
- **root/parent 关系**：Slot A mount 提供 root part（rod / base-conduit / housing-with-rail-clamp / housing-with-backplate）；housing 经一条 mount-specific FIXED 接到 root。pendant_rod=rod 为 root、housing 为 child（`rod_to_housing`）；conduit_wall=base 为 root、enclosure 为 child（`base_to_enclosure`）；rail_clamp=housing 为 root、两 rail 为 child（`clamp_to_rail_*`，反向：壳承轨）；wall_backplate=housing 为 root、back_plate 为 child（`housing_to_back_plate`）。
- **跨 slot 接口点位**：
  - mount↔housing：rail_clamp = 夹块半管槽 seat 双轨（axis 沿 X 轨向）；wall_backplate = 平板 y=0 贴壳后缘 flush（`BACK_Y`，expect_gap 验贴合）；conduit_wall = strap 贴柜后承载（allow_overlap 表 bolted seat）；pendant_rod = rod 经 gland captive 穿过（expect_within 验居中）。mating face = 后缘 / 侧轨面。
  - control↔housing 前面：所有 push-button/knob/toggle/mushroom 的 joint origin 贴前控制面（P2/P3=+Y `FACE_Y`/门面；P1=+X `FRONT_X` bezel 面），anchor = 各控制件 (x,z) 中心。**例外**：`rotary_disconnect_handle` 的 operator_base 法兰/shaft 在 -X 侧壁，REVOLUTE 绕 +X operator 轴。
  - readout↔housing 前面：display/gauge 沉入前面 pocket cut（`disp_pocket`/`gauge_pocket`/门 pocket），LED 坐 well，anchor = pocket 中心 (x,z)；全为 housing 固定 visual。
- **跨 slot joint type / axis / range**：mount→housing 全 FIXED；control→housing 视 module 取 PRISMATIC（push-button -X/-Y/+X，行程 0.0028–0.012）或 REVOLUTE（knob ±135°、toggle ±0.45、disconnect 0–160°）；readout→housing 无 joint（fixed visual）。
- **互斥 / 可选 / 派生**：readout 可为空（none/bare bezel）；`rotary_disconnect_handle` 与小 rail 壳互斥（侧壁余量不足，见排除项）；`BUTTON_COUNT` 轴只在 control=`round_push_buttons` 时激活。

## 每槽位 Module Emits / Interfaces

### Slot A / module `pendant_rod`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `suspension_rod`(root, `rod_shaft`), `housing`(+`top_gland`/`bottom_gland`/`front_bezel`) | S1 / L202-L257 |
| internal joints | 无（mount 内部刚性） | S1 |
| upstream interface | rod 为世界 root，竖直 +Z | S1 / L202-L214 |
| downstream interface | `rod_to_housing` FIXED，rod captive 穿过 housing 上下 gland（allow_overlap + expect_within 居中） | S1 / L260-L266, L359-L385 |

### Slot A / module `rail_clamp`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`(root, 含 `rear_clamp`), `rail_top`, `rail_bottom`（各独立 part） | S2 / L262-L308 |
| internal joints | `clamp_to_rail_top` / `clamp_to_rail_bottom`（FIXED，两轨 seat 进半管槽） | S2 / L309-L315 |
| upstream interface | housing 为 root；rear_clamp 桥接前壁→后腔→外凸，承载双轨 | S2 / L236-L250, L285-L293 |
| downstream interface | 夹块半管槽 seat 双轨（axis 沿 X），allow_overlap + expect_contact 验 seat | S2 / L484-L504 |

### Slot A / module `conduit_wall`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`(root, `conduit_runs`：4 竖管+strap+drop+jbox), `enclosure` | S3 / L315-L328 |
| internal joints | 无（conduit 单体） | S3 |
| upstream interface | base 为 root，竖直线管束 + 横 strap | S3 / L245-L295 |
| downstream interface | `base_to_enclosure` FIXED，strap 贴柜后（allow_overlap 表 bolted seat） | S3 / L374-L380, L436-L440 |

### Slot A / module `wall_backplate`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`(root), `back_plate`(+`mounting_tab_0..3` keyhole 凸台) | S4 / L285-L323 |
| internal joints | 无 | S4 |
| upstream interface | housing 为 root | S4 / L285-L306 |
| downstream interface | `housing_to_back_plate` FIXED@`BACK_Y`，平板贴壳后缘 flush（expect_gap 验贴合） | S4 / L324-L330 |

### Slot B / module `round_push_buttons`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `button_left`/`button_right`（或 N 个 `button_{i}`） | S2 / L317-L326 |
| internal joints | `press_button_{left,right}` PRISMATIC，axis -Y（P1 = -X），行程 BTN_TRAVEL≈0.003 | S2 / L327-L338 |
| upstream interface | joint origin 贴前面板面 `FACE_Y`，anchor=(x,z) 中心；barrel captive 进 housing bore | S2 / L333, L464-L483 |
| downstream interface | 无（terminal 输入件） | — |

### Slot B / module `rotary_disconnect_handle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle`(`disconnect_handle` hub+lever+grip)，`operator_base` 为 enclosure visual | S3 / L330-L334, L365-L370 |
| internal joints | `operator_handle` REVOLUTE +X，0–160°（OFF↓/ON↑） | S3 / L395-L405 |
| upstream interface | operator_base 法兰/shaft 在 -X 侧壁（`OP_X`），hub captive 套 shaft（allow_overlap） | S3 / L169-L188, L427-L433 |
| downstream interface | 无 | — |

### Slot B / module `rotary_selector_knob`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `selector_knob`(`selector_knob_shell`+`selector_stem`+`pointer_mark`) | S6 / L336-L354 |
| internal joints | `turn_selector` REVOLUTE +Y（面法向），±135° | S6 / L357-L367 |
| upstream interface | joint origin 贴面 `FACE_Y`，anchor=(KNOB_X, KNOB_Z) | S6 / L362 |
| downstream interface | 无 | — |

### Slot B / module `toggle_switch_bank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `switch_{idx}`(`{sname}_bat`) ×SWITCH_COUNT；`switch_socket_{idx}` 为 housing visual | S7 / L311-L317, L352-L359 |
| internal joints | `housing_to_switch_{idx}` REVOLUTE +X，±SWITCH_THROW(0.45)；SWITCH_COUNT=3 | S7 / L362-L372 |
| upstream interface | 各 joint origin 贴面 bushing 中心 `(_switch_x(idx), FACE_Y, SWITCH_Z)` | S7 / L367 |
| downstream interface | 无 | — |

### Slot B / module `mushroom_estop`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `emergency_stop`(`safety_guard`+`retaining_gasket`+`mushroom_cap`) | S8 / L302-L323 |
| internal joints | `housing_to_emergency_stop` PRISMATIC -X，深 0.012 latch | S8 / L332-L347 |
| upstream interface | joint origin 贴前 bezel 面 `bezel_face_x`，anchor=(0, ESTOP_CENTER_Z) | S8 / L300, L338 |
| downstream interface | 无 | — |

### Slot C / module `rect_lcd_with_leds` / `digital_display_window` / `analog_round_gauge` / `lcd_led_vent_cluster`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 全部为 **housing/door 固定 visual**（无独立 part、无 joint）：`display_glass`/`display_bezel`/`led_{i}`（rect_lcd）；`display_glass`（digital window）；`gauge_rim`/`gauge_dial`/`gauge_tick_{idx}`/`gauge_needle`/`gauge_hub`（gauge）；`lcd_frame`/`lcd_glass`/`indicator_led_{i}`/`vent_slot_{i}`（lcd cluster） | S2 L262-L283 / S3 L347-L352 / S10 L321-L346 / S11 L274-L313 |
| internal joints | 无 | — |
| upstream interface | display/gauge 沉入前面 pocket cut（`disp_pocket`/`gauge_pocket`/门 pocket），LED 坐 well，anchor=pocket 中心 | 各源 pocket cut |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount_style` | enum | `pendant_rod` / `rail_clamp` / `conduit_wall` / `wall_backplate` | `rail_clamp` | choice | 由 procedural sampler 选择；决定 root 与 housing FIXED 接口 | Slot A 表 |
| `control_style` | enum | `round_push_buttons` / `rotary_disconnect_handle` / `rotary_selector_knob` / `toggle_switch_bank` / `mushroom_estop` | `round_push_buttons` | choice | 由 sampler 选择；hero 关节由此定 | Slot B 表 |
| `readout_style` | enum | `none` / `rect_lcd_with_leds` / `digital_display_window` / `analog_round_gauge` / `lcd_led_vent_cluster` | `rect_lcd_with_leds` | choice | 由 sampler 选择；纯 fixed visual | Slot C 表 |
| `button_count` | int | `[2, 12]` | 4 | conditional | 仅当 `control_style==round_push_buttons` 激活；否则忽略。见 Multiplicity 节 | S12/S13 / `BUTTON_COUNT` |
| `button_pitch` | float | `[0.040, 0.066]` | 0.060(N3)/0.044(N6) | conditional | 随 `button_count` 收紧：`button_count·button_pitch ≤ face_width − 2·margin` | S12 L52 / S13 L54 |
| `switch_count` | int | `[2, 6]` | 3 | conditional | 仅当 `control_style==toggle_switch_bank`；module-local 内部 multiplicity | S7 `SWITCH_COUNT` |
| `housing_w_scale` | float | `[0.85, 1.25]` | 1.0 | independent | 在 `[min,max]` 内独立采样后 clamp；前面宽度 | 各 housing `HOUSING_W`/`ENC_W` |
| `housing_h_scale` | float | `[0.85, 1.25]` | 1.0 | independent | 独立采样后 clamp；前面高度 | 各 housing `HOUSING_H`/`ENC_H` |
| `face_inset_scale` | float | derived | 1.0 | equation | `= f(housing_w_scale, housing_h_scale)`，pocket/bore/well 内缩比例锁定，保证 display/button 不越界 | readout/control pocket cut |
| (—) | constraint | — | — | inequality | `button_count·button_pitch + 2·edge_margin ≤ housing_w·housing_w_scale`；违反时按比例回缩 pitch 或拒绝重采 | control 行布局 |
| (—) | constraint | — | — | inequality | display pocket + control 行 + LED 行在前面竖向不重叠：`Σ cluster_h ≤ housing_h·housing_h_scale`；违反则回缩或重采 | 前面分区 |
| (—) | constraint | — | — | conditional | `rotary_disconnect_handle` 要求 mount 提供足够侧壁深度（`housing_depth ≥ operator_shaft_min`）；小 rail 壳不满足→gate 排除 | 排除项 |

## Multiplicity / Copy Logic

本类有 **2 根独立 multiplicity 轴**，按轴单独声明：

### 轴 1：`button_count`（前排圆 push-button 数 —— 模板级主轴）
- `count_param`: `BUTTON_COUNT`
- `N_range`: **[2, 12]**（采样域远大于样本；真实控制面按钮行常 2–8，留余量到 12）
- sampling domain: 小 N 高频（2–6 加权偏多）、大 N(8–12) 稀有尾部
- copied object: 单个圆 push-button cap（`_build_button_shape`/`_build_button_cap`）+ 门体对应 counterbore/stem bore
- naming: part `button_{i}`（visual `button_{i}_cap`/`button_{i}_plunger`），joint `button_slide_{i}`（N6 风格）或 `door_to_button_{i}`（N3 风格），`for i in range(BUTTON_COUNT)` 发射
- placement: 居中等距 `bx = (i − (BUTTON_COUNT−1)/2) · BUTTON_PITCH`（N3 pitch=0.060，N6 pitch=0.044），display 在上、按钮行在下
- joint policy: 每个按钮独立 PRISMATIC，axis=(0,−1,0)（内压门面），统一 `lower=0 upper=BUTTON_TRAVEL`(0.006)，effort/velocity 一致，互不联动
- source/gating: **copy-logic 源码 = N3/N6 变体（S12/S13，fork 自 P3），不是任何 parent**。
  - **关键提示**：P1/P2 的 N=2 是手写 `top/bottom`、`left/right` tuple（`...c28c270c/...model.py:L274`、`...647d2061/...model.py:L318`），**未循环化**；P3 parent 的门面 `for i in range(4)`（`...ab3b9f65/...model.py:L355-L362`）把按钮当门体 **fixed visual** 发射（无 joint）。N3/N6 变体已把该循环重写为「articulated `button_{i}` part + `button_slide_{i}`/`door_to_button_{i}` PRISMATIC」的干净 `for i in range(BUTTON_COUNT)`（S12 L379-L429、S13 L372-L423）。模板应以 N3/N6 为唯一 copy-logic 蓝本。
  - gating: 仅 `control_style==round_push_buttons` 时激活；其它 control module 忽略此轴。

### 轴 2：`switch_count`（toggle_switch_bank module-local 拨杆数）
- `count_param`: `SWITCH_COUNT`
- `N_range`: **[2, 6]**（module-local；样本 N=3）
- sampling domain: 小 N 偏多
- copied object: 单个拨杆 `switch_{idx}`(`{sname}_bat`) + 前面 bushing `switch_socket_{idx}`
- naming: part `switch_{idx}`，joint `housing_to_switch_{idx}`，`for idx in range(SWITCH_COUNT)` 发射
- placement: 居中等距 `x = SWITCH_CX + (idx − (SWITCH_COUNT−1)/2)·SWITCH_DX`
- joint policy: 每拨杆独立 REVOLUTE +X，±SWITCH_THROW(0.45)
- source/gating: 源 = S7（`...ctrlB_togglebank/...model.py:L311-L317`+`L352-L372`）；仅 `control_style==toggle_switch_bank` 时激活

两轴各自加权采样、各自 clamp、各自编进 `slot_choices`、各自设 sweep 上限；跨轴不共享 helper（待第二个 multiplicity 模板出现再抽象）。

## 拓扑多样性审计

总组合数：`4 mount × 5 control × 4 readout = 80` 基础结构组合；再乘 `button_count` 轴（`round_push_buttons` 分支 N∈[2,12] = 11 档）与 `switch_count` 轴（`toggle_switch_bank` 分支 N∈[2,6] = 5 档），总 seed domain ≫ 80 ≫ 10。

理由：control slot 单独就给出 5 种 distinct 关节模式（push-button PRISMATIC -Y/-X、disconnect REVOLUTE +X 侧壁、knob REVOLUTE +Y、toggle bank ×N REVOLUTE +X、mushroom PRISMATIC 深行程），叠加 mount 的 4 种 root/FIXED 拓扑（rod-captive / rail-child / conduit-base / backplate）与 button_count 轴，distinct 拓扑远超 10。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling 先选 mount→再从兼容集合选 control→选 readout→对激活的 multiplicity 轴各做一次加权采样；`seed=0` 不特殊。

Procedural Sampling / Sweep Plan：sampler 按 slot 顺序 mount→control→readout→multiplicity 采样，用 compatibility matrix 排除非法组合（见下）。少量 regression overrides 预留给已知失败组合，不作主 seed domain。Random sweep：首验跑 seeds 0、0-4、0-19、0-49（cumulative）检查 build / joint origin·axis·range / support / collision / ；成熟审计跑 0-999。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 slot 笛卡尔 80 + 两 multiplicity 轴足以支撑，无类别约束阻碍。

Controlled local parameterization：初版应含 `housing_w_scale`/`housing_h_scale`（independent，[0.85,1.25] clamp）、`face_inset_scale`（equation 派生于前两者，锁 pocket/bore 内缩）、`button_pitch`（conditional 随 button_count 收紧）。所有连续 scale 在 `resolve_config` 内 clamp/派生/投影，受前面布局不等式约束，不破坏 InterfaceSpec/MatingContract/multiplicity。跨部件依赖（pocket↔housing、pitch↔count↔face_width）显式落到 equation/inequality/conditional 行。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mount→control→readout→multiplicity 顺序加权选择，兼容门控 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | `rotary_disconnect_handle` 要求深侧壁机体（排除小 rail 壳）；`mushroom_estop` 不与窄门同面挤占；`analog_gauge` 与 `toggle_bank` 同面争位时回退；readout=none 合法 | no floating, collision, axis, max multiplicity, bulky module, optional child 失败 |
| controlled local variation | housing_w/h_scale + face_inset_scale + button_pitch，全部 clamp/派生 | 比例变化不破坏 pocket clearance、button bore 捕获、joint origin、类别身份 |
| regression overrides | none（如未来 sweep 发现稳定失败组合再加，需写明 seed + 原因） | 仅已知失败回归 / reviewer 指定 |
| random sweep | seeds 0-49 首验，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A mount | 4 | yes | yes | 4 distinct 结构家族；rail_clamp 跨两机体实现 |
| B control | 5 | yes | yes | 5 distinct 关节模式；pushbtn_railrotary 计入 round_push_buttons |
| C readout | 4 | yes | yes | +`none/bare_bezel` 可选空态（不计入 4） |

## Validator
- `slot_choices_for_seed` 返回已实现的 module 名（mount/control/readout/N）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling。
- compatibility matrix / gating 阻止非法组合（disconnect_handle↔小 rail 壳、gauge↔toggle 同面争位、mushroom↔窄门）。
- regression overrides 稀少且有理由。
- 模板不无限轮换小型 curated/modulo 表作为主 seed domain。
- 受控局部 scale（housing_w/h、face_inset、button_pitch）被 clamp，不破坏接口、clearance、joint origin、multiplicity。
- 跨部件 scale 依赖（equation/inequality/conditional）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 点存在：mount FIXED seat（rail 半管槽 / backplate flush / conduit strap / rod captive）、control joint origin 贴前控制面（disconnect 例外贴侧壁）、readout pocket 中心。
- 关键关节类型/轴/range 正确：mount 全 FIXED；push-button PRISMATIC 内压（行程 0.0028–0.012）；disconnect REVOLUTE +X 0–160°；knob REVOLUTE +Y ±135°；toggle REVOLUTE +X ±0.45；mushroom PRISMATIC -X 深 0.012。
- copied object 遵守 naming/placement：`button_{i}` part + `button_slide_{i}`/`door_to_button_{i}` joint 居中等距；`switch_{idx}` 同理。
- readout 簇全为 housing 固定 visual，无独立 part、无 joint。

## Reject cases
- mount 缺失或不构成单 root：housing 悬空，或两 root 不连通。
- control 簇无任何非 FIXED hero 关节（整面做成纯 fixed visual）。
- push-button/knob/toggle/mushroom 用不可见接口盘连接、悬空、或 joint origin 不贴前控制面（disconnect 例外）。
- 把整排按钮换成单旋钮再叠大屏 → 读作仪表/收音机（出类目）。
- 给 pendant_rod 盒加双轨，或给单旋钮面加 N 大按钮行而无 round_push_buttons 语义 → mount/control 语义冲突。
- `button_count` 越界（<2 或 >12），或 `button_count·button_pitch` 越过前面宽度导致按钮相撞/越界。
- readout 沉孔 pocket 与 control 行重叠穿模，或 display 浮在面外不沉入 pocket。
- 把 push-button/gauge tick 做成未连接的独立 FIXED child parts（应为门体 captured plunger / housing fixed visual）。

## 与相邻类别的边界
- 不该混入：`analog_gauge_instrument` / `radio_receiver`（理由：那类以**显示/读数为主导**、输入件次要；control_panel 必须 control 簇主导，readout 为附属 fixed visual）。
- 不该混入：`circuit_breaker_panel` / `distribution_board`（理由：那类展开内部母排/端子排接线拓扑；control_panel 只到带壳人机面板，不画内部布线）。
- 不该混入：`keypad` / `keyboard`（理由：密排字符键阵；control_panel 是少量大圆动量按钮 2–12 + 旋钮/拨杆/急停）。
- 不该混入：`hinged_cabinet_door`（理由：本类 door 视为 FIXED dead-front，hero 是面板控制件，不是摆门铰链）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；样本为 articraft_data 仓内 workbench-only picture-subcat fork（3 parent + 10 variant，全部 last compile=success）。等待人工审核，审核通过前不进入模板实现。 |
