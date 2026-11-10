# Music Keyboard Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `music_keyboard` |
| template path | `agent/templates/Music_keyboard.py` |
| test path (optional) | `tests/agent/test_music_keyboard_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：根 `chassis`（桌面机身 / 倾斜木夹板机身）下挂三类平行子件 + 一根 multiplicity 轴：
- **共享脊柱（multiplicity 轴）**：后铰键床 `white_key_{i}`（自然音）+ `black_key_{j}`（升号），各自一个 REVOLUTE 按键关节（绕 +X，lower=0→press），数量由 `key_count` 派生（白/黑数由 `SHARP_AFTER` 边界表导出）。
- **Slot A control_surface**：机身后部 deck/panel 上的控制簇（drum-pad grid / fader bank / rotary-knob bank / 父级混合 deck），revolute 旋钮 + prismatic 推子/pad/滑块各携带运动学。
- **Slot B pitch_bender_interface**：键床左前方的表情控制器（joystick gimbal 嵌套链 / pitch+mod 双轮 / 静态 touch-strip）。
- **Slot C chassis_form**：承载键床 + 控制面的机身（flat-slab 桌面平板 / upright-wood-cheeks 倾斜楔形面板 + 木端板）。

两个 parent 是两条 baseline family（compact-MIDI-controller A / analog-synth B），**ONE template 跨两族**；A/B 仅在零件命名约定与控制混合上不同，世界系与按键运动学一致。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category：2 parents + 9 `rec_music_keyboard_var_*` 的 `model.py` 全文逐行已读 |
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

11 个 5★ 样本（2 parent + 9 variant，全部 rating=5、compile=success、workbench-only、≥1 非 fixed joint、仍明确读作 keyboard 控制器）逐条阅读摘要：

- **PA `rec_compact-midi-keyboard-controller-...99ed5d64`**（A 族 baseline，**A 系 fork 母资产**）— 25-mini-key 黑机身 + 红端板 MIDI 控制器。`chassis`（root）发射 `bottom_shell`(L162-167)+`control_deck`(L170-177，后部抬高 deck)+`key_bed`(L180-187，键下低床)+`{left,right}_end_cap`(L189-195，红)。键：15 白 `white_key_{i}`（notched 侧切 `_white_key_mesh` L98-112）+ 10 黑 `black_key_{j}`（楔形 `_black_key_mesh` L115-129），关节 `white_key_{i}_press`/`black_key_{j}_press`（REVOLUTE +X，0→WHITE_PRESS/BLACK_PRESS，L255-281），cx=−CORE_HALF+KEY_PITCH·(i+0.5)。控制：8 drum pad（2×4，`drum_pad_{i}` `pad_cap`，`drum_pad_{i}_press` PRISMATIC z−，0→PAD_TRAVEL，L283-300，bezel `pad_bezel_{r}_{c}` L197-205）+ 4 列旋钮（`knob_{k}` `knob_cap`，`knob_{k}_turn` REVOLUTE z ±KNOB_RANGE，L302-317，raised-dot 指示）+ 静态 `display_strip`+`strip_rim_*`（L207-240）。run_tests 验证 15/10/25 计数、按键 rest@0+下沉、pad 下沉、knob 竖轴。世界系：Z up，X 宽，front=−Y。

- **PB `rec_analog-synthesizer-keyboard-...c8a11966`**（B 族 baseline，**B 系 fork 母资产**）— 深灰 analog synth，teal section 框。`chassis` 发射 `base_shell`(L130-135，全幅底板)+`panel_housing`(L137-144，后部抬高面板，**面板比键床宽**，BODY_HALF_W=0.25 固定独立于键数)+`keybed_cheek`(L163-168)+`bender_block`+`pitch_strip`/`mod_strip`/`bend_strip_{0,1}`(L147-160，front-left 静态)+`{section}_frame_*` teal decals(L172-204)。键：15 白（LoftGeometry notched `_white_key_mesh` L86-96）+10 黑（`_black_key_mesh` L99-112），关节 `chassis_to_white_key_{i}`/`chassis_to_black_key_{j}`（REVOLUTE +X，0→KEY_PRESS_RAD，L231-260），cx=FIRST_WHITE_X+i·KEY_PITCH，hinge KEY_HINGE_Y=−0.030 藏于面板唇下。控制：20 旋钮场（12 `{section}_knob_{r}_{c}` + 8 `master_knob_{c}`，`knob_body`+`pointer`，`chassis_to_{name}` REVOLUTE z ±KNOB_LIMIT_RAD，`_add_knob` L289-328）+ 4 `env_slider_{s}`（`cap`+`cap_line`，`chassis_to_env_slider_{s}` PRISMATIC +Y ±SLIDER_TRAVEL，slot `slider_slot_{s}`，L333-366）。run_tests 验证 25 键、20 旋钮竖轴+指示+座落、slider 行程、pitch/mod 条位、teal decal 凸起。

- **`rec_music_keyboard_var_control_padgrid`**（Slot A 候选 `pad_grid_16`，B 族）— 4×4 背光 drum-pad grid 替换 B 的 20-knob 场。`pad_{i}` ×16（`pad_body` 锥形 `_pad_mesh` L121-140 + `backlight` 每行 amber/crimson/cobalt/lime，L156-160），`chassis_to_pad_{i}` PRISMATIC axis(0,0,−1) 0→PAD_PRESS（L294-328），bezel 平台 `pad_bezel_platform`(L226)+`pad_frame_{front/back/left/right}`(L237-255)，grid 中心 GRID_CENTER_X/Y。**保留键 + 4 env slider**（`env_slider_{s}` L388-422）。part 树拓扑不同（16 pad + 滑块，无旋钮场）。

- **`rec_music_keyboard_var_control_faderbank`**（Slot A 候选 `fader_bank_9`，A 族）— 9 线性推子替换 A 的 drum pad，**丢弃 4 列旋钮**。`fader_{i}` ×9（`cap_body` `_fader_cap_mesh` L131 + `cap_grip` `_fader_grip_mesh` L137），`fader_{i}_slide` PRISMATIC axis(0,1,0) 0→FADER_TRAVEL（L295-330），chassis `fader_slot_{i}`(L202)+`fader_rail_{i}_{left/right}`(L216)，N_FADERS=9 FADER_SPACING=0.028。键 A-style `white_key_{i}_press`（L256-292）。保留 display strip（STRIP_CY 后移 0.072 让位）。

- **`rec_music_keyboard_var_control_knobbank`**（Slot A 候选 `knob_grid_8`，A 族）— 2×4 旋钮 grid 替换 A 的 drum pad，**保留 4 列旋钮**。`grid_knob_{i}` ×8（`knob_cap` `_grid_knob_geometry` L131），`grid_knob_{i}_turn` REVOLUTE axis(0,0,1) ±GRID_KNOB_RANGE（L293-307，2 行 ×4 列）；外加列 `knob_{k}` ×4（`_knob_geometry` L142，`knob_{k}_turn` REVOLUTE z ±KNOB_RANGE，L312-322）；bezel `grid_knob_bezel_{r}_{c}`(L209)。键 L249-285。两簇 REVOLUTE 旋钮（8+4），无 pad/滑块。

- **`rec_music_keyboard_var_bender_joystick`**（Slot B 候选 `joystick_gimbal`，A 族）— 2-DOF 弹返 gimbal 摇杆，**嵌套子链**。`joystick_socket`(chassis visual，L349-358)；`joystick_gimbal`(`ring` `_joystick_ring_mesh` L163)，`joystick_pitch` REVOLUTE axis(0,1,0) ±JOYSTICK_TILT（parent=chassis，L369-379）；`joystick_stick`(`shaft` `_joystick_stick_mesh` L168)，`joystick_mod` REVOLUTE axis(1,0,0) ±JOYSTICK_TILT（**parent=gimbal，嵌套**，L390-400）。坐落于 A 的 drum-pad deck front-left（JOYSTICK_X=−0.120,Y=0.015）。同时保留 A baseline 8 pad+4 knob（与控制簇共存）。

- **`rec_music_keyboard_var_bender_twowheels`**（Slot B 候选 `pitch_mod_wheels`，B 族）— pitch+mod 双轮，水平横轴。`wheel_{i}` ×2（`wheel_body` cadquery `_bender_wheel_mesh` L196-214：disc+hub bore+rim grip），`chassis_to_wheel_{i}` REVOLUTE axis(1,0,0) ±WHEEL_LIMIT_RAD 弹返（L218-239）；chassis `wheel_cheek` 底板(L168-173)+`wheel_bracket_{0,1,2}` 三轴墙(L175-186)。替换 B 的 bender_block/touch-strip。WHEEL_COUNT=2 固定对。

- **`rec_music_keyboard_var_chassis_woodcheeks`**（Slot C 候选 `upright_wood_cheeks`，B 族）— 倾斜楔形面板 + 高木端板。`angled_panel`(`_angled_panel_mesh` L137-152，wedge 前低后高)+`base_shell`(L247-252) 替换 B 的 flat panel_housing；`cheek_0`/`cheek_1`(`_cheek_mesh` L113-134，梯形 walnut 端板，后高，L280-289)。控制以 `origin rpy=(PANEL_TILT_ANGLE,0,0)` + z=`panel_surface_z(y)`(L48) 重新座落于倾斜面（`_add_knob` L424-466、slider L471-）。`_tilted_bar_mesh`(L155-173) 让 decal/条随倾斜。证明控制簇可在倾斜面板上整体复位。

- **`rec_music_keyboard_var_keycount_13`**（multiplicity 样本 N=13，A 族）— N_WHITE=8、SHARP_AFTER=(0,1,3,4,5) 5 黑（L42,71），CORE_W=N_WHITE·KEY_PITCH=0.1568（L43），BODY_W=CORE_W+2·CAP_W；body 宽随白键数参数化收窄。run_tests 断言 8 白/5 黑、CORE_W=N_WHITE·KEY_PITCH。

- **`rec_music_keyboard_var_keycount_37`**（multiplicity 样本 N=37，A 族）— N_WHITE=22、SHARP_AFTER 15 项(L39,73)，CORE_W=0.4312（L40），body 宽随之放大。断言 22 白/15 黑。

- **`rec_music_keyboard_var_keycount_49`**（multiplicity 样本 N=49，B 族）— WHITE_KEY_COUNT=29、BLACK_AFTER_WHITE 20 项 4 八度(L36,46-51)，且 **recenter body**：BODY_CENTER_X=0.175、BODY_HALF_W=0.425（L26-27），base/panel 平移到 BODY_CENTER_X（L137-146）。断言 four octaves、20 黑、键床跨距。

跨样本观察：全 11 样本共享 **后铰键床 REVOLUTE 按键脊柱**（绕 +X，lower=0→press，front tip 下沉）+ **Z up / X 宽 / front=−Y 世界系** + **notched 白键 + 楔形黑键 + SHARP_AFTER 边界表** + **REVOLUTE 旋钮(竖 z) / PRISMATIC pad/fader/slider** + **captured-under-panel 键尾 allow_overlap**（PB L393-400）。差异严格落在四轴：**(A) 控制簇**、**(B) bender**、**(C) 机身形态**、**(N) 键数**。配色两族基线（A：黑机身+红端板；B：深灰+teal）为 §7 `palette_style` 提供基线 + 现实派生 colorway。**命名分歧**：A 用 `white_key_{i}_press`/`black_key_{j}_press`，B 用 `chassis_to_white_key_{i}`/`chassis_to_black_key_{j}`——模板须取一套 canonical（本 spec 取 B-style `chassis_to_*`）。

## 核心身份

音乐键盘控制器（music keyboard）：一排**后铰可按压琴键键床**（白自然音 + 黑升号）置于桌面机身前部，机身后部 deck/panel 承载一簇**演奏控制器**（drum pad / fader / rotary knob 的某种组合），键床**左前方**有一个**表情/弯音控制器**（摇杆 / 双轮 / 触条）。世界系约定：+X 为宽度（+右），+Y 为深度（+后，演奏者面对 −Y 前方），+Z 向上；物体以 `base_shell`/`bottom_shell` 近 z=0 着地；键床后铰线在 deck/panel 唇下（Y≈KEY_HINGE_Y/DECK_FRONT_Y），琴键向 −Y 伸出，按压 = REVOLUTE 绕 +X、lower=0、front tip 下沉。

成熟域：13–61 键（标准控制器八度区间）的桌面 MIDI 控制器 / 模拟合成器键盘，含可变数量键 + 后部一簇控制器（pad/fader/knob）+ 一个 bender + 桌面或倾斜木夹板机身。身份强约束：

- **必须**有后铰可按压键床（≥1 八度，白 + 黑键，每键 REVOLUTE 按压关节绕 +X、rest@0→下沉），白/黑数由 `key_count` + `SHARP_AFTER` 边界表导出。
- **必须**有后部控制簇（Slot A：pad/fader/knob 之一），其中旋钮 = REVOLUTE 竖轴、pad/fader/slider = PRISMATIC，至少一个非 fixed 控制件。
- **必须**有 bender 区（Slot B：摇杆 / 双轮 / 触条）位于键床左前方。
- 控制簇/bender/机身形态/键数可变（即 Slot A/B/C/N），但**桌面键盘身份**（一排按压键 + 后控制面）不可缺。

边界（不该混入）：

- 不混入 `digital_piano_with_stand`（88 全配重键 + 落地 L 形 / X 形琴架 + 谱架；本类是桌面无架控制器，13–61 轻键，无落地腿/谱架链）。
- 不混入 `accordion`（手风琴：纵向折叠风箱 PRISMATIC + 侧立键钮，无桌面机身、无后控制 deck，运动语义是风箱开合而非桌面按键）。
- 不混入 `dj_controller` / `mixing_console`（无琴键键床；核心是 jog wheel + 推子 + 通道条阵列；本类身份强制需要白/黑琴键键床脊柱）。

## 槽位 + 候选模块表

### Slot A：control_surface（主控制簇槽——决定后 deck/panel 控制件的 part 树 + joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `pad_block_8`（A 基线） | PA `rec_compact-midi-keyboard-controller-...99ed5d64` | `L132-135`(`_pad_mesh`)、`L137-145`(`_knob_geometry`)、`L197-205`(`pad_bezel_{r}_{c}`)、`L283-300`(`drum_pad_{i}` ×8 + `drum_pad_{i}_press` PRISMATIC z−)、`L302-317`(`knob_{k}` ×4 + `knob_{k}_turn` REVOLUTE z) | eligible if compatible | 2×4 drum pad（8，PRISMATIC 下压 0→PAD_TRAVEL，红 bezel）+ 4 列旋钮（REVOLUTE 竖轴 ±KNOB_RANGE，raised-dot）+ 静态 display strip。混合 pad+knob 簇。 |
| `pad_grid_16` | `rec_music_keyboard_var_control_padgrid` | `L121-140`(`_pad_mesh` 锥形)、`L156-160`(背光色)、`L226`(`pad_bezel_platform`)、`L237-255`(`pad_frame_*`)、`L294-328`(`pad_{i}` ×16 + `chassis_to_pad_{i}` PRISMATIC z−)、`L388-422`(保留 `env_slider_{s}` ×4) | eligible if compatible | 4×4 背光 drum-pad grid（16，PRISMATIC 0→PAD_PRESS，每行 amber/crimson/cobalt/lime 背光）+ 保留 4 env slider（PRISMATIC +Y）。**pad 数翻倍 + 无旋钮**，part 树拓扑不同。 |
| `fader_bank_9` | `rec_music_keyboard_var_control_faderbank` | `L131-141`(`_fader_cap_mesh`/`_fader_grip_mesh`)、`L202`(`fader_slot_{i}`)、`L216`(`fader_rail_{i}_{l/r}`)、`L295-330`(`fader_{i}` ×9 + `fader_{i}_slide` PRISMATIC +Y 0→FADER_TRAVEL) | eligible if compatible | 9 线性推子（PRISMATIC 沿 +Y 滑，cap_body+cap_grip，rail+slot 轨）替换 pad，**丢弃列旋钮**，保留 display strip。纯线性推子簇（无 REVOLUTE）。 |
| `knob_grid_8` | `rec_music_keyboard_var_control_knobbank` | `L131-152`(`_grid_knob_geometry`/`_knob_geometry`)、`L209`(`grid_knob_bezel_{r}_{c}`)、`L293-307`(`grid_knob_{i}` ×8 + `grid_knob_{i}_turn` REVOLUTE z ±GRID_KNOB_RANGE)、`L312-322`(列 `knob_{k}` ×4 + `knob_{k}_turn`) | eligible if compatible | 2×4 旋钮 grid（8，REVOLUTE 竖轴）+ 保留 4 列旋钮（共 12 REVOLUTE 旋钮）替换 pad。纯 REVOLUTE 旋钮簇。 |
| `knob_field_20`（B 基线） | PB `rec_analog-synthesizer-keyboard-...c8a11966` | `L266-287`(big/small `KnobGeometry`)、`L289-328`(`_add_knob`：`{section}_knob_{r}_{c}` ×12 + `master_knob_{c}` ×8 + `pointer`，`chassis_to_{name}` REVOLUTE z ±KNOB_LIMIT_RAD)、`L333-366`(`env_slider_{s}` ×4 + `chassis_to_env_slider_{s}` PRISMATIC +Y) | eligible if compatible | 密集 20-旋钮场（12 section + 8 master，REVOLUTE 竖轴 + 白指针）+ 4 env slider（PRISMATIC +Y）。最高密度混合簇，需最宽面板。 |

> Slot A 五候选结构差异充分：跨 **8 pad+4 knob / 16 pad+4 slider / 9 fader / 12 knob / 20 knob+4 slider** 五种 part 树 + joint 拓扑组合（PRISMATIC pad、PRISMATIC fader/slider、REVOLUTE knob 的不同混合与数量）。不只尺寸/颜色差异。

### Slot B：pitch_bender_interface（表情/弯音控制器槽——键床左前方；决定 bender 的 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `touch_strip`（A/B 基线） | PA `...99ed5d64` / PB `...c8a11966` | A：`L207-240`(`display_strip`+`strip_rim_{front/rear/inner/outer}` 静态)；B：`L147-160`(`bender_block`+`pitch_strip`/`mod_strip`/`bend_strip_{0,1}` 静态) | eligible if compatible | 静态触/弯音条块（chassis visual，无独立 part、无 joint）。最少 articulation 基线（仅键 + 控制簇活动）。 |
| `joystick_gimbal` | `rec_music_keyboard_var_bender_joystick` | `L163-174`(`_joystick_ring_mesh`/`_joystick_stick_mesh`)、`L349-358`(`joystick_socket` chassis visual)、`L361-379`(`joystick_gimbal`+`joystick_pitch` REVOLUTE axis(0,1,0) ±JOYSTICK_TILT，parent=chassis)、`L382-400`(`joystick_stick`+`joystick_mod` REVOLUTE axis(1,0,0)，**parent=gimbal 嵌套**) | eligible if compatible | 2-DOF 弹返 gimbal 摇杆：嵌套子链（stick 骑在 gimbal 上）。joint 拓扑 = 2× REVOLUTE 嵌套（pitch 绕 Y / mod 绕 X）。 |
| `pitch_mod_wheels` | `rec_music_keyboard_var_bender_twowheels` | `L168-186`(`wheel_cheek`+`wheel_bracket_{0,1,2}`)、`L196-214`(`_bender_wheel_mesh` cadquery)、`L218-239`(`wheel_{i}` ×2 + `chassis_to_wheel_{i}` REVOLUTE axis(1,0,0) ±WHEEL_LIMIT_RAD 弹返) | eligible if compatible | 直立 pitch+mod 双轮，水平横 X 轴；轮在三 bracket 墙间。joint 拓扑 = 2× REVOLUTE（平行，非嵌套）。 |

> Slot B 三候选跨 **无 joint（touch_strip）/ 2×REVOLUTE 嵌套（joystick）/ 2×REVOLUTE 平行（wheels）** 三种 bender 拓扑，是本模板第二多样性驱动槽。

### Slot C：chassis_form（机身形态槽——承载键床 + 控制面；决定面板倾斜 + 控制件座落帧）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_slab`（A/B 基线） | PA `...99ed5d64` / PB `...c8a11966` | A：`L162-195`(`bottom_shell`+`control_deck`+`key_bed`+`{side}_end_cap`)；B：`L130-168`(`base_shell`+`panel_housing`+`keybed_cheek`) | eligible if compatible | 桌面平板：水平抬高 control deck/panel，控制件直接座落于水平 deck top（z=DECK_TOP_Z/PANEL_TOP_Z，rpy=0）。 |
| `upright_wood_cheeks` | `rec_music_keyboard_var_chassis_woodcheeks` | `L48-53`(`panel_surface_z`)、`L113-134`(`_cheek_mesh`)、`L137-152`(`_angled_panel_mesh`)、`L155-173`(`_tilted_bar_mesh`)、`L247-289`(`base_shell`+`angled_panel`+`cheek_0/1`)、`L424-466`(控制 reseat `rpy=(PANEL_TILT_ANGLE,0,0)` + z=panel_surface_z(y)) | eligible if compatible | 倾斜楔形面板（前低后高）+ 两高 walnut 木端板（梯形，后高）；控制件以 `rpy=(PANEL_TILT_ANGLE,0,0)` + `panel_surface_z(y)` 重座于倾斜面。part 树 + 控制座落帧拓扑不同。 |

> **Slot C 仅 2 候选（理由）**：机身形态的真实结构词汇表本质为「水平桌面平板」vs「倾斜楔形面板 + 立木端板」两族——颜色/材质/比例微变（不同 deck 高度、不同端板木纹）仍属同一拓扑，不是新 part 树 / 新座落帧。按 `SPEC_TEMPLATE.md §4`「样本池不足时可降到 2 并说明理由」处置。差异已足够：`flat_slab` 控制座落水平 deck（rpy=0），`upright_wood_cheeks` 控制 reseat 倾斜面（rpy=tilt + panel_surface_z）+ 新增木端板 part。下游若要第 3 候选可加 `keytar_strap_body` 或 `angled_desktop_stand`（需新增 5★ 源）。

## 槽位图（slot graph）

pattern = `mixed`（multiplicity 键脊柱 + 平行控制/bender 子件 + chassis-派生座落帧）

```
[chassis]  (root：base_shell + control_deck/panel；Slot C 决定 flat / tilted + 控制座落帧)
   |
   |== [键脊柱 multiplicity] ==
   |   |-- white_key_{i}  --REVOLUTE chassis_to_white_key_{i} (axis +X, origin (cx_i, KEY_HINGE_Y, white_hinge_z), 0→key_press_rad)-->
   |   |-- black_key_{j}   --REVOLUTE chassis_to_black_key_{j} (axis +X, origin (bx_j, KEY_HINGE_Y, black_hinge_z), 0→key_press_rad)-->
   |        (i∈0..N_white−1 由 key_count 派生；j 由 SHARP_AFTER 边界表派生；后铰，front tip 向 −Y 伸出按压下沉)
   |
   |== [Slot A control_surface] ==（挂在后 deck/panel 上的控制簇，按所选 module 发射）
   |   · pad_block_8:   drum_pad_{i} (8) --PRISMATIC drum_pad_{i}_press (axis −Z, 0→PAD_TRAVEL)--> + knob_{k} (4) --REVOLUTE knob_{k}_turn (axis +Z, ±KNOB_RANGE)-->
   |   · pad_grid_16:   pad_{i} (16)    --PRISMATIC chassis_to_pad_{i} (axis −Z, 0→PAD_PRESS)--> + env_slider_{s} (4) --PRISMATIC +Y-->
   |   · fader_bank_9:  fader_{i} (9)   --PRISMATIC fader_{i}_slide (axis +Y, 0→FADER_TRAVEL)-->
   |   · knob_grid_8:   grid_knob_{i} (8)--REVOLUTE grid_knob_{i}_turn (axis +Z, ±GRID_KNOB_RANGE)--> + knob_{k} (4) --REVOLUTE-->
   |   · knob_field_20: {section}_knob_{r}_{c} (12) + master_knob_{c} (8) --REVOLUTE chassis_to_{name} (axis +Z, ±KNOB_LIMIT_RAD)--> + env_slider_{s} (4) --PRISMATIC +Y-->
   |
   |== [Slot B pitch_bender_interface] ==（键床左前方 bender 区，按所选 module 发射）
   |   · touch_strip:      (静态 chassis visual，无 joint)
   |   · joystick_gimbal:  chassis --REVOLUTE joystick_pitch (axis +Y, ±TILT)--> joystick_gimbal --REVOLUTE joystick_mod (axis +X, ±TILT, 嵌套)--> joystick_stick
   |   · pitch_mod_wheels: chassis --REVOLUTE chassis_to_wheel_{i} (axis +X, ±WHEEL_LIMIT, i∈0..1)--> wheel_{i}
   |
   +== [Slot C chassis_form] ==（决定 root part 形态 + 控制件座落帧）
       · flat_slab:          控制 origin rpy=(0,0,0)，z=deck_top
       · upright_wood_cheeks: 控制 origin rpy=(PANEL_TILT_ANGLE,0,0)，z=panel_surface_z(y)；新增 cheek_0/cheek_1 木端板 visual
```

接口点位与装配说明：

- **chassis → 琴键（按压）**：joint origin 在键后铰线 `(cx_i, KEY_HINGE_Y, hinge_z)`，axis=+X；键尾藏于 deck/panel 唇下（element-scoped `allow_overlap`：`key_body` ↔ `panel_housing`/`control_deck`，PB L393-400）。`cx_i` 沿 +X 等距 `KEY_PITCH`，黑键居于 `SHARP_AFTER` 自然音边界 +KEY_PITCH/2。
- **chassis → 控制簇（Slot A）**：控制件 joint origin 在后 deck/panel 顶面 `(x, y, control_anchor_z)`；`control_anchor_z` 与 rpy 由 **Slot C 派生**（flat → z=deck_top, rpy=0；tilted → z=panel_surface_z(y), rpy=(PANEL_TILT_ANGLE,0,0)）。pad/fader/slider 捕获 bezel/rail（element `allow_overlap`）。
- **chassis → bender（Slot B）**：bender 占键床**左前**专属区 `x < x_keybed_start`（touch_strip/joystick 在 deck 上，wheels 在 wheel_cheek housing 上）；joystick 为嵌套链（stick parent=gimbal），wheels 为平行对（parent=chassis）。
- **互斥 / 派生关系**：Slot A 五模块互斥（决定哪簇控制件存在）；Slot B 三模块互斥（决定 bender 形态）；Slot C 二模块互斥（决定 root 形态 + 所有控制件的 `control_anchor_z`/rpy 座落帧——**Slot C 切换会改写 Slot A 全部控制件 origin**，接口一致性关键）。`key_count` 派生 N_white/N_black + body 宽度。

## 每槽位 Module Emits / Interfaces

### 共享脊柱：keybed（multiplicity，所有组合）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `white_key_{i}`（visual `key_body` notched）×N_white + `black_key_{j}`（visual `key_body` 楔形）×N_black | PB / model.py:L224-251 |
| internal joints | `chassis_to_white_key_{i}` / `chassis_to_black_key_{j}`（REVOLUTE +X，0→key_press_rad，rest@0 front tip 下沉） | PB / model.py:L231-260 |
| upstream interface | 键后铰线坐落 `(cx_i, KEY_HINGE_Y, hinge_z)`；键尾捕获 panel/deck 唇下（element allow_overlap） | PB / model.py:L393-400 |
| downstream interface | 无（终端活动件）；N_white/N_black 由 `key_count` + `SHARP_AFTER` 派生 | §8 |

### Slot A / module `pad_block_8`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drum_pad_{i}`（`pad_cap`）×8 + `knob_{k}`（`knob_cap`）×4 + 静态 `pad_bezel_{r}_{c}` / `display_strip` | PA / model.py:L283-317, L197-240 |
| internal joints | `drum_pad_{i}_press`（PRISMATIC −Z 0→PAD_TRAVEL）+ `knob_{k}_turn`（REVOLUTE +Z ±KNOB_RANGE） | PA / model.py:L290-317 |
| upstream interface | pad 座落 bezel top（element allow_overlap `pad_cap`↔`pad_bezel`）；knob 座落 deck top | PA / model.py:L295, L312 |
| downstream interface | 无 | — |

### Slot A / module `pad_grid_16`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pad_{i}`（`pad_body`+`backlight`）×16（4×4）+ `env_slider_{s}` ×4 + 静态 `pad_bezel_platform`/`pad_frame_*` | padgrid / model.py:L294-328, L388-422 |
| internal joints | `chassis_to_pad_{i}`（PRISMATIC −Z 0→PAD_PRESS）+ `chassis_to_env_slider_{s}`（PRISMATIC +Y） | padgrid / model.py:L315-328 |
| upstream interface | pad 座落 bezel 平台 top（element allow_overlap）；grid 中心 GRID_CENTER_X/Y | padgrid / model.py:L290-292 |
| downstream interface | 无 | — |

### Slot A / module `fader_bank_9`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fader_{i}`（`cap_body`+`cap_grip`）×9 + 静态 `fader_slot_{i}`/`fader_rail_{i}_{l/r}` + display strip | faderbank / model.py:L295-330, L202-216 |
| internal joints | `fader_{i}_slide`（PRISMATIC +Y 0→FADER_TRAVEL） | faderbank / model.py:L316-330 |
| upstream interface | cap 座落 rail top（z=DECK_TOP_Z+FADER_RAIL_H），起点在 slot 前端，element allow_overlap cap↔rail | faderbank / model.py:L324-329 |
| downstream interface | 无 | — |

### Slot A / module `knob_grid_8`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grid_knob_{i}`（`knob_cap`）×8（2×4）+ `knob_{k}`（`knob_cap`）×4 + 静态 `grid_knob_bezel_{r}_{c}` | knobbank / model.py:L293-322, L209 |
| internal joints | `grid_knob_{i}_turn`（REVOLUTE +Z ±GRID_KNOB_RANGE）+ `knob_{k}_turn`（REVOLUTE +Z ±KNOB_RANGE） | knobbank / model.py:L295-322 |
| upstream interface | knob 座落 bezel/deck top（element allow_overlap） | knobbank / model.py:L298 |
| downstream interface | 无 | — |

### Slot A / module `knob_field_20`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{section}_knob_{r}_{c}` ×12 + `master_knob_{c}` ×8（各 `knob_body`+`pointer`）+ `env_slider_{s}` ×4 + 静态 `slider_slot_{s}`/`{section}_frame_*` | PB / model.py:L289-366, L172-204 |
| internal joints | `chassis_to_{knob_name}`（REVOLUTE +Z ±KNOB_LIMIT_RAD）×20 + `chassis_to_env_slider_{s}`（PRISMATIC +Y）×4 | PB / model.py:L308-321, L353-366 |
| upstream interface | knob 座落 panel top（z=PANEL_TOP_Z）；slider cap 座落 slot rail；env slider 捕获 slot（element allow_overlap） | PB / model.py:L313, L358 |
| downstream interface | 无；最宽控制簇（需 body 面板 ≥ 0.50 m，见 §9 fit gate） | — |

### Slot B / module `touch_strip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`display_strip`/`strip_rim_*`（A）或 `bender_block`/`pitch_strip`/`mod_strip`/`bend_strip_*`（B）为 chassis visual | PA L207-240 / PB L147-160 |
| internal joints | 无（不活动） | — |
| upstream interface | 静态条块坐落键床左前方 chassis 上 | PB / model.py:L147-160 |
| downstream interface | 无 | — |

### Slot B / module `joystick_gimbal`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `joystick_gimbal`（`ring`）+ `joystick_stick`（`shaft`）+ 静态 `joystick_socket` | joystick / model.py:L349-400 |
| internal joints | `joystick_pitch`（REVOLUTE +Y ±TILT，parent=chassis）+ `joystick_mod`（REVOLUTE +X ±TILT，**parent=gimbal 嵌套**） | joystick / model.py:L369-400 |
| upstream interface | socket 坐落 deck front-left（JOYSTICK_X,Y）；gimbal 捕获 socket top（element allow_overlap） | joystick / model.py:L353-374 |
| downstream interface | stick 嵌套挂 gimbal（joint origin=(0,0,0) 相对 gimbal） | joystick / model.py:L390-395 |

### Slot B / module `pitch_mod_wheels`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`（`wheel_body`）×2 + 静态 `wheel_cheek`/`wheel_bracket_{0,1,2}` | twowheels / model.py:L168-239 |
| internal joints | `chassis_to_wheel_{i}`（REVOLUTE +X ±WHEEL_LIMIT_RAD 弹返，i∈0..1，平行非嵌套） | twowheels / model.py:L226-239 |
| upstream interface | 轮在三 bracket 墙间横 X 轴上（wheel_axle_z/y）；轮 bore 捕获轴（element allow_overlap） | twowheels / model.py:L188-231 |
| downstream interface | 无 | — |

### Slot C / module `flat_slab`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`bottom_shell`/`base_shell` + `control_deck`/`panel_housing` + `key_bed`/`keybed_cheek` + `end_cap` 为 chassis visual | PA L162-195 / PB L130-168 |
| internal joints | 无 | — |
| upstream interface | 控制座落帧：水平 deck top，`control_anchor_z=DECK_TOP_Z/PANEL_TOP_Z`，rpy=(0,0,0) | PA L295,312 / PB L313 |
| downstream interface | 向 Slot A/B 提供水平座落 z + rpy=0 | — |

### Slot C / module `upright_wood_cheeks`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cheek_0`/`cheek_1`（walnut 木端板，独立 visual）+ `angled_panel`/`base_shell` 楔形 chassis visual | woodcheeks / model.py:L247-289 |
| internal joints | 无 | — |
| upstream interface | 控制座落帧：倾斜面，`control_anchor_z=panel_surface_z(y)`，rpy=(PANEL_TILT_ANGLE,0,0) | woodcheeks / model.py:L450-453 |
| downstream interface | 向 Slot A/B 提供倾斜座落 z(y) + rpy=tilt（**改写 Slot A 全部控制件 origin**） | woodcheeks / model.py:L424-466 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `control_surface` | enum | `pad_block_8` / `pad_grid_16` / `fader_bank_9` / `knob_grid_8` / `knob_field_20` | `pad_block_8` | choice | deterministic procedural sampler 选择；决定 Slot A part 树 + joint 拓扑 + 控制 footprint 宽度 | Slot A 表 |
| `pitch_bender_interface` | enum | `touch_strip` / `joystick_gimbal` / `pitch_mod_wheels` | `touch_strip` | choice | sampler 选择；决定 bender joint 拓扑 | Slot B 表 |
| `chassis_form` | enum | `flat_slab` / `upright_wood_cheeks` | `flat_slab` | choice | sampler 选择；决定 root 形态 + 控制座落帧（z/rpy） | Slot C 表 |
| `palette_style` | enum | `black_controller_red` / `dark_gray_teal_synth` / `silver_synth_walnut` / `crimson_boutique` / `graphite_blue_pads` / `cream_vintage` | `black_controller_red` | choice | 每 seed 采样 colorway；仅改 material rgba，不改拓扑/尺寸/接口 | PA L151-157 / PB L118-125 + 跨样本配色派生 |
| `key_count` | int (multiplicity) | {13, 25, 37, 49, 61}（加权，详见 §8） | 25 | independent (weighted) | 每 seed 加权采样；派生 N_white/N_black（见 §8） | §8 / keycount 样本 |
| `key_pitch` | float | [0.0185, 0.0250] | 0.0220 | independent | 琴键间距（mini 0.0196 ↔ full 0.024 两族之间）；clamp | PA KEY_PITCH=0.0196 / PB KEY_PITCH=0.024 |
| `key_press_rad` | float | [0.050, 0.065] | 0.060 | independent | 全键统一按压行程上限（lower=0）；clamp | PA WHITE_PRESS L70 / PB KEY_PRESS_RAD L51 |
| `body_depth_scale` | float | [0.92, 1.10] | 1.0 | independent | 机身前后深度缩放（键长 + deck 深等比）；clamp | PA BODY_D L33 / PB depth L27-28 |
| `panel_height_scale` | float | [0.85, 1.15] | 1.0 | independent | 后 deck/panel 抬高高度缩放；clamp | PA DECK_TOP_Z L46 / PB PANEL_TOP_Z L32 |
| `control_turn_limit_rad` | float | [2.2, 2.7] | 2.5 | independent | 旋钮 REVOLUTE 对称限位 ±limit（仅含旋钮的 Slot A）；clamp | PA KNOB_RANGE L87 / PB KNOB_LIMIT_RAD L52 |
| `N_white` | int | derived | — | equation | `= 7·octaves+1`（由 `key_count` 派生：13→8,25→15,37→22,49→29,61→36） | §8 / keycount 样本 |
| `N_black` | int | derived | — | equation | `= key_count − N_white`（由 `SHARP_AFTER` 边界表长度派生：5/10/15/20/25） | §8 / keycount 样本 |
| `keybed_width` | float | derived | — | equation | `= N_white · key_pitch`（body 键床区宽度，end cap 随之） | keycount_13 L43 / keycount_37 L40 |
| `control_anchor_z` | float | derived | — | conditional | `flat_slab → deck_top·panel_height_scale, rpy=0`；`upright_wood_cheeks → panel_surface_z(y), rpy=(PANEL_TILT_ANGLE,0,0)`（由 `chassis_form` 解析） | woodcheeks L450-453 |
| `body_panel_width` | float | derived | — | equation | `= max(bender_zone_w + keybed_width + right_margin, control_footprint_w(control_surface) + 2·side_margin)`（机身后面板取键床与控制簇 footprint 的较大者；body 随密集控制簇加宽） | PB BODY_HALF_W=0.25 独立于键数 L26 |
| (—) | constraint | — | — | inequality | **控制簇 fit**：`body_panel_width ≥ control_footprint_w + 2·side_margin`。控制 footprint：pad_block_8≈0.13 / knob_grid_8≈0.13 / fader_bank_9≈0.24 / pad_grid_16≈0.16 / knob_field_20≈0.47 m。违反时按 §9 fallback（密集簇→紧凑簇）或加宽 body 直至满足（恒可满足）。 | §9 compatibility |
| (—) | constraint | — | — | inequality | **bender 左区保留**：bender footprint（joystick≈0.05 / wheels≈0.09 / touch≈0.10 m）≤ `bender_zone_w`，且 `x_keybed_start = body_left_edge + bender_zone_w`，键床不侵入 bender 区。违反时扩 `bender_zone_w` 或键床右移。 | PB 键床 FIRST_WHITE_X=−0.118 vs bender x=−0.191 |
| (—) | constraint | — | — | inequality | **按压离地**：全键 `q=key_press_rad` 全压位，front tip `min_z ≥ base_top`（不穿底板）。违反时回缩 `key_press_rad` 或抬 hinge_z。 | PB L444-451 |
| (—) | constraint | — | — | inequality | **键间隙 + 黑键骑高**：相邻白键 X 间隙 ≥ 0.0005；黑键 AABB 落在 notched 白尾通道内、骑于白键面之上。违反时缩 key_pitch 下限或重采。 | PB L404-430 |
| (—) | constraint | — | — | inequality | **倾斜面控制 within（C=upright_wood_cheeks）**：控制件 reseat 后须落在 `angled_panel` 倾斜面边界内（不超出端板间宽、不穿 cheek）。违反时收控制 grid 跨度或加宽端板间距。 | woodcheeks L424-466 |

`palette_style` colorway 取值（rgba 仅示意，下游模板落实；全部源自 11 个 5★ 样本两族配色基线及现实变体；仅改 material，不改拓扑/尺寸/接口）：
- `black_controller_red`：机身黑 (0.10,0.10,0.11)、红端板/bezel (0.78,0.06,0.08)、白键 (0.93,0.93,0.91)、黑键 (0.07,0.07,0.08)、灰旋钮 (0.17,0.17,0.18)（= PA 基线）。
- `dark_gray_teal_synth`：机身深灰 (0.16,0.165,0.175)、teal 框 (0.55,0.86,0.80)、炭灰旋钮 (0.10,0.105,0.115)、白指针、白键（= PB 基线）。
- `silver_synth_walnut`：银铝面板 (0.66,0.67,0.69)、walnut 木端板 (0.42,0.26,0.15)、炭灰旋钮、白键、奶白条——vintage analog（配 `upright_wood_cheeks` 最佳）。
- `crimson_boutique`：crimson 机身 (0.62,0.10,0.12)、黑控制件、白键、银指针——boutique 红合成器。
- `graphite_blue_pads`：石墨机身 (0.13,0.14,0.16)、cobalt 背光 pad (0.22,0.50,1.0)、amber accent (1.0,0.55,0.15)、白键——节拍 pad 控制器。
- `cream_vintage`：奶白/象牙机身 (0.90,0.87,0.80)、tan 木端板 (0.55,0.40,0.24)、棕黑键、暖灰旋钮——复古立式。

## Multiplicity / Copy Logic

**1 根模板级 multiplicity 轴：`key_count`**（琴键脊柱）。控制簇子件数（pad/fader/knob/wheel）为**所选 Slot A/B module 内的固定 copy loop**，非独立模板轴。

### 轴 1：`key_count`（琴键脊柱）

- `count_param`: `key_count`（总键数 = N_white + N_black）。
- `N_range`（本小类产品域）：**[13, 61]**（标准控制器八度区间；13=1 八度、25=2、37=3、49=4、61=5）。测试偏小（13/25），产品全程到 61；white-count→`keybed_width = N_white · key_pitch` 参数化加宽已由 13/37/49 样本证明，故 ≥49 by construction 安全（61 稀疏采样）。
- sampling domain（权重档）：小 N 高频、大 N 稀有 — `{13: 0.20, 25: 0.40, 37: 0.20, 49: 0.15, 61: 0.05}`（25 键 = 最常见桌面控制器，居中加权；61 尾部稀有，body 极宽需 fit gate）。
- copied object：每自然音一个 `white_key_{i}`（visual `key_body` notched）+ 每升号一个 `black_key_{j}`（visual `key_body` 楔形）；各一个 REVOLUTE 关节。
- naming：0-based `white_key_{i}` / `black_key_{j}`；关节 canonical = **B-style** `chassis_to_white_key_{i}` / `chassis_to_black_key_{j}`（A-style `*_press` 弃用，模板统一一套）。
- placement：沿 +X 等距 `key_pitch` 后铰排（`cx_i = body_keybed_left + key_pitch·(i+0.5)`）；黑键居 `SHARP_AFTER`/`BLACK_AFTER_WHITE` 自然音边界 +key_pitch/2（每八度 5 黑：C# D# F# G# A#）；大 N body 可 recenter（keycount_49 BODY_CENTER_X L27）。
- joint policy：每键 REVOLUTE 绕 +X，axis=(1,0,0)，lower=0，upper=`key_press_rad`（rest@0，front tip 下沉）；全键共享同一限位。
- source/gating：N_white = 7·octaves+1（8/15/22/29/36），N_black = 5·octaves（5/10/15/20/25），由 `SHARP_AFTER` 边界表（每八度模式 `(0,1,3,4,5)` + 7·oct 偏移）派生；样本覆盖 {13,25,37,49}。

### module-local 固定 copy loop（非模板轴，由 Slot 选择决定，不暴露为 `*_count` 参数）

- pads：`drum_pad_{i}` = 8（pad_block_8，2×4）/ `pad_{i}` = 16（pad_grid_16，4×4）— `for i in range(PAD_ROWS·PAD_COLS)`。
- faders：`fader_{i}` = 9（fader_bank_9）— `for i in range(N_FADERS)`。
- knobs：列 `knob_{k}` = 4（pad_block_8 / knob_grid_8）；grid `grid_knob_{i}` = 8（knob_grid_8，2×4）；B 场 `{section}_knob_{r}_{c}` = 12 + `master_knob_{c}` = 8（= 20，knob_field_20）。
- env sliders：`env_slider_{s}` = 4（pad_grid_16 / knob_field_20）。
- bender wheels：`wheel_{i}` = 2（pitch_mod_wheels，固定对，非可变 N）。

这些子件数由所选 Slot A/B module **硬绑定**（pad_grid 永远 16，fader_bank 永远 9），是 module 身份的一部分，故不作为独立 multiplicity 轴采样。

## 拓扑多样性审计

总组合数：control_surface × pitch_bender × chassis × key_count = **5 × 3 × 2 × 5 = 150**（slot 组合 30；× 5 个 key_count 样本，key_count 改变键 part 数 → 改变 topology 签名）。仅 slot 组合（不计 key_count）= **30**。


理由：仅 Slot 组合即 30 distinct（远超 10），每个都改变 part 树或 joint 拓扑——Slot A 跨 **8pad+4knob / 16pad+4slider / 9fader / 12knob / 20knob+4slider** 五种控制 part 树 + PRISMATIC/REVOLUTE 混合；Slot B 跨 **无 joint / 2×REVOLUTE 嵌套 / 2×REVOLUTE 平行** 三种 bender 拓扑；Slot C 跨 **水平座落 / 倾斜座落+木端板** 二种机身。再叠加 `key_count`（5 档，改键 part 数 5→61）→ 150 distinct topology 签名。`palette_style`（6）与连续 scale 不计入 topology 等价类时仍达 150。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG 独立加权采样四轴（control_surface 5 选 1、pitch_bender 3 选 1、chassis 2 选 1，默认近均匀可对 `pad_block_8`/`touch_strip`/`flat_slab` 经典基线略加权；`key_count` 按 §8 权重档），再采 `palette_style` 与所有 `independent` 连续 scale，按 `equation` 派生 N_white/N_black/keybed_width/body_panel_width，按 `conditional` 由 `chassis_form` 解析 `control_anchor_z`/rpy，最后用 §7 五条 `inequality`（控制 fit / bender 左区 / 按压离地 / 键间隙 / 倾斜 within）投影回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定 `[(control_surface,…),(pitch_bender,…),(chassis_form,…),(key_count,…)]`（连续 scale 不进 slot_choices）。compatibility gate 在 `resolve_config` 求解（不留到 builder）。`seed=0` 不特殊。无需 regression overrides（11 源齐全，每轴覆盖；若 sweep 暴露坏组合再按审核加 sparse override）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本模板 = **150**（30 slot 组合 × 5 key_count），按 ≥300 report-only 口径观察，低于 300 时需记录原因。多样性主体来自 slot 组合 + key_count multiplicity，配以 `palette_style`（6 colorway）× 连续 scale 谱提供视觉/比例多样性。

Controlled local parameterization（初版模板应含关键连续 scale）：`key_pitch [0.0185,0.0250] independent`、`key_press_rad [0.050,0.065] independent`、`body_depth_scale [0.92,1.10] independent`、`panel_height_scale [0.85,1.15] independent`、`control_turn_limit_rad [2.2,2.7] independent`；派生 `keybed_width = N_white·key_pitch`（equation）、`body_panel_width = max(bender_zone+keybed_width+margin, control_footprint+2·margin)`（equation）、`control_anchor_z`/rpy（conditional by chassis_form）。遵循连续尺寸采样契约：先采 independent → 派生 equation（keybed/body 宽）→ 解析 conditional（座落帧）→ 用五条 inequality 投影回缩。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（键后铰线、控制座落帧随 Slot C 派生）、MatingContract（键尾捕获面板唇、pad/fader 捕获 bezel/rail、joystick 嵌套 socket、wheel 捕获轴）或 multiplicity（key_count 派生 N_white/N_black）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 轴序 A→B→C→key_count，独立加权 enum/int 采样 + palette + 连续 scale；fit gate 在 resolve_config | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | A×B×C×N 全 150 组合**默认全合法**（桌面键盘身份不冲突；控制簇/bender 占机身不同区——后 deck vs 左前 bender 区——无空间互斥）。**唯一 fit gate**：密集 Slot A（`knob_field_20`≈0.47m、`fader_bank_9`≈0.24m）需 `body_panel_width ≥ control_footprint`——恒可由加宽 body 满足（B 族 body 本就独立于键数加宽）；若审美上不愿把 20-knob 场配 13-key 极窄键床，可对 `(knob_field_20 / pad_grid_16) × key_count∈{13}` 软降权或 fallback 到紧凑簇（`pad_block_8`/`knob_grid_8`），**非硬排除**。控制簇/bender **解耦于 fork parent**：样本里 fader/knob_grid/joystick 仅 fork 自 A，pad_grid/wheels/wood_cheeks 仅 fork 自 B，但模板允许全 cross-combo（如 wood_cheeks×fader_bank、joystick×knob_field、wheels×pad_block）；这些 cross-combo 未被样本采样但 by construction 合法（座落帧由 Slot C 统一改写，bender 区独立）。 | 无 floating / 无穿模 / 控制 fit 面板内 / bender 不侵键床 / 按压离地 / 桌面键盘身份 |
| controlled local variation | 5 个 independent scale + 派生 keybed/body 宽 + conditional 座落帧；全部 clamp + 五条 inequality 回缩 | 比例随机但键后铰、控制座落帧、bender 区、按压离地、键盘身份不破 |
| regression overrides | none（11 源每轴覆盖，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（控制 fit / bender 区 / 按压离地 / 倾斜 within / 大 N body 加宽） |、topology distinct、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A control_surface | 5 | yes | yes | pad8 / pad16 / fader9 / knob8 / knob20 |
| B pitch_bender_interface | 3 | yes | yes | touch / joystick / wheels |
| C chassis_form | 2 | yes | no | 降到 2 已说明理由（机身二族） |
| N key_count（multiplicity） | 5 档 | yes | yes | 13/25/37/49/61，加权 |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{pad_block_8, pad_grid_16, fader_bank_9, knob_grid_8, knob_field_20}、B∈{touch_strip, joystick_gimbal, pitch_mod_wheels}、C∈{flat_slab, upright_wood_cheeks}、N∈{13,25,37,49,61}）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + key_count + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：控制 fit gate（body_panel_width ≥ control_footprint）+ bender 左区保留 + 大 N body 加宽，密集簇×极窄键床软降权/fallback。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（key_pitch/key_press_rad/body_depth/panel_height/control_turn_limit）在 `resolve_config` clamp/派生；五条 inequality（控制 fit / bender 区 / 按压离地 / 键间隙 / 倾斜 within）+ equation（keybed/body 宽）+ conditional（座落帧）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：键尾捕获 `panel_housing`/`control_deck` 唇下（element allow_overlap）；pad/fader 捕获 bezel/rail；joystick stick 嵌套 gimbal（parent=gimbal）；wheel bore 捕获横轴；控制件座落帧 z/rpy 随 Slot C 派生。
- 关键 joint type/axis/range：键 = REVOLUTE +X 0→key_press_rad；旋钮 = REVOLUTE +Z ±limit；pad = PRISMATIC −Z 0→travel；fader/slider = PRISMATIC +Y 0→travel；joystick = REVOLUTE +Y/+X ±tilt（嵌套）；wheels = REVOLUTE +X ±limit（平行）。
- copied object 命名/placement：`white_key_{i}`/`black_key_{j}`（cx 沿 +X 等距 key_pitch，黑居 SHARP_AFTER 边界）；module-local 子件 `pad_{i}`/`fader_{i}`/`grid_knob_{i}`/`{section}_knob_{r}_{c}`/`wheel_{i}` 按 module 固定数。
- 桌面键盘身份不变量：后铰键床（白+黑，每键 REVOLUTE 按压 rest@0→下沉）；后部一簇控制件（≥1 非 fixed）；bender 区在键床左前；body 随 key_count 与控制簇加宽。
- N 派生：N_white=7·oct+1、N_black=5·oct，由 key_count 唯一确定；键计数断言匹配（如 PA L330-336 风格）。

## Reject cases

- 无后铰按压键床，或键关节非 REVOLUTE +X / 非 rest@0→下沉（读成 fixed 键砖块，丢失琴键身份）。
- 控制簇全为静态 visual（无任何 PRISMATIC pad/fader/slider 或 REVOLUTE knob）→ 无非 fixed 控制件，退化为无功能面板。
- key_count 与 N_white/N_black 不自洽（黑键数 ≠ 5·octaves，或黑键未居 SHARP_AFTER 自然音边界）→ 键床错排/穿模。
- 控制件座落帧未随 Slot C 派生（`upright_wood_cheeks` 仍用 rpy=0 + 水平 z）→ 控制件悬浮于倾斜面之上/穿入面板。
- 密集控制簇（knob_field_20 / fader_bank_9）未做 fit gate → 控制件溢出面板边缘或与端板/键床穿模。
- 按压全压位 front tip 穿底板（key_press_rad 过大或 hinge_z 过低未回缩）。
- bender 侵入键床区（bender_zone_w 未保留 / 键床起点未右移）→ 摇杆/轮与白键穿模。
- 把落地琴架 + 谱架（digital piano）、风箱（accordion）、或纯 jog/推子阵列无键床（dj controller）混进来当本类。
- 混用 A-style `*_press` 与 B-style `chassis_to_*` 两套键关节命名（须统一 canonical）。

## 与相邻类别的边界

- 不该混入：`digital_piano_with_stand`（88 全配重键的数码钢琴 + 落地 L/X 形琴架 + 谱架 + 踏板；本类是桌面无架控制器，13–61 轻键，无落地腿/谱架/踏板链，机身直接桌面着地）。
- 不该混入：`accordion`（手风琴：纵向折叠风箱 PRISMATIC 开合 + 侧立钮键，运动语义是风箱而非桌面后铰按键；无后控制 deck、无桌面机身）。
- 不该混入：`dj_controller` / `mixing_console`（无白/黑琴键键床脊柱；核心是 jog wheel + 通道推子条 + 旋钮阵列；本类身份强制需要琴键键床——缺键床即出类）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：后铰键床 `_white_key_mesh(notched)` + `_black_key_mesh(楔形)` + `SHARP_AFTER` 边界生成 + `chassis_to_*_key_{i}` REVOLUTE 发射在全 11 源一致，可抽公共 keybed helper（按 `key_count` 派生 N_white/N_black，`# adopted: PB/keycount_*`）。两族 mesh 实现不同（A=ExtrudeGeometry、B=LoftGeometry），统一取 LoftGeometry（B-style，notched outline 更干净）。
- **命名 canonical**：键关节统一 `chassis_to_white_key_{i}`/`chassis_to_black_key_{j}`（B-style）；控制旋钮统一 `chassis_to_{knob_name}`。弃 A 的 `*_press`/`*_turn` 后缀风格，避免两套混用。
- **Slot C 座落帧是接口关键**：`flat_slab` → 控制 origin z=deck_top·panel_height_scale, rpy=0；`upright_wood_cheeks` → z=`panel_surface_z(y)`, rpy=`(PANEL_TILT_ANGLE,0,0)`。Slot A 全部控制件（pad/fader/knob/slider）的 origin 必须从 resolved 座落帧取值，不可硬编码——Slot C 切换会改写所有控制件 z/rpy（cross-combo 如 wood_cheeks×fader_bank 全靠此统一改写）。
- captured-pin / 接口 overlap 须 element-scoped `allow_overlap`：键尾↔panel_housing/control_deck 唇（全组合）；pad_cap↔bezel、fader cap↔rail、knob base↔deck、joystick gimbal↔socket、wheel bore↔横轴。参考各源 run_tests 的 allow_overlap 块。
- **joystick 嵌套**：`joystick_mod` parent=gimbal（非 chassis），origin=(0,0,0) 相对 gimbal；勿误挂 chassis（否则丢 2-DOF 嵌套语义）。
- **fit gate 在 resolve_config**：control_footprint_w 按 control_surface 查表（pad8/knob8≈0.13、fader9≈0.24、pad16≈0.16、knob20≈0.47），body_panel_width=max(键床+bender+margin, footprint+2·margin)；大 N（49/61）键床本就宽，自动满足；小 N×密集簇靠加宽 body（B 族先例：body 独立键数加宽）或 fallback 紧凑簇。
- **大 N body recenter**：key_count≥49 时 body 可能需 BODY_CENTER_X 平移（keycount_49 L27）以让 bender 左区 + 宽键床居中；keybed_width 与 body_panel_width 派生后统一定位。
- cross-combo 未被样本采样但合法：wood_cheeks×{fader/knob_grid/pad_block}、joystick×{pad_grid/knob_field/knob_grid}、wheels×{pad_block/fader/knob_grid}、各 bender×各 chassis×各 key_count。初版 sweep 应优先目检这些 cross-combo（样本只单轴变化，cross 是模板新增）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / 脊柱 | `pad_block_8` / `touch_strip(A)` / `flat_slab(A)` / keybed | `rec_compact-midi-keyboard-controller-...99ed5d64` | A 控制 `L132-145,197-240,283-317`；touch `L207-240`；chassis `L162-195`；键 `L242-281` | A 族基线：8pad+4knob + display strip + 桌面平板 + A-style 键 |
| S2 | A / B / C / 脊柱 | `knob_field_20` / `touch_strip(B)` / `flat_slab(B)` / keybed | `rec_analog-synthesizer-...c8a11966` | B 控制 `L266-366`；touch `L147-160`；chassis `L130-168`；键 `L209-260,393-400` | B 族基线：20knob+4slider + 触条 + 深灰平板 + canonical 键命名 |
| S3 | A | `pad_grid_16` | `rec_music_keyboard_var_control_padgrid` | `L121-140,156-160,226-255,294-328,388-422` | 4×4 背光 pad grid + 保留 env slider |
| S4 | A | `fader_bank_9` | `rec_music_keyboard_var_control_faderbank` | `L131-141,202-216,295-330` | 9 线性推子 PRISMATIC，丢列旋钮 |
| S5 | A | `knob_grid_8` | `rec_music_keyboard_var_control_knobbank` | `L131-152,209,293-322` | 2×4 旋钮 grid + 4 列旋钮（12 REVOLUTE） |
| S6 | B | `joystick_gimbal` | `rec_music_keyboard_var_bender_joystick` | `L163-174,349-400` | 2-DOF 嵌套 gimbal 摇杆（pitch+mod） |
| S7 | B | `pitch_mod_wheels` | `rec_music_keyboard_var_bender_twowheels` | `L168-239` | pitch+mod 双轮横 X 轴弹返 |
| S8 | C | `upright_wood_cheeks` | `rec_music_keyboard_var_chassis_woodcheeks` | `L48-53,113-173,247-289,424-466` | 倾斜楔形面板 + walnut 木端板 + 控制 reseat 倾斜面 |
| S9 | 脊柱 multiplicity | `key_count=13` | `rec_music_keyboard_var_keycount_13` | `L41-45,71,333-353` | N=13 (8白+5黑)，CORE_W=N_white·KEY_PITCH 参数化 |
| S10 | 脊柱 multiplicity | `key_count=37` | `rec_music_keyboard_var_keycount_37` | `L38-44,73,335-336` | N=37 (22白+15黑) |
| S11 | 脊柱 multiplicity | `key_count=49` | `rec_music_keyboard_var_keycount_49` | `L26-27,36,46-51,137-146,386-409` | N=49 (29白+20黑) 4 八度，body recenter (BODY_CENTER_X) |
