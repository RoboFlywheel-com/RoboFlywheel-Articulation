# Barcode Scanner Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `barcode_scanner` |
| template path | `agent/templates/barcode_scanner.py` |
| test path (optional) | `tests/agent/test_barcode_scanner_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (form-family root `scanner_body` + optional grounded mount parent + one moving control child) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this subcategory (2 origin anchors + 5 verified-PASS forks) |
| source_index_policy | only adopted module sources are indexed below; every listed sample is adopted |

Adopted sources (all 7 read, all adopted):

| source_id | record_id | model.py |
|---|---|---|
| SA | `rec_handheld-pistol-grip-barcode-scanner-black-plast_20260708_082438_119506_b32f70d1` | `data/records/rec_handheld-pistol-grip-barcode-scanner-black-plast_20260708_082438_119506_b32f70d1/revisions/rev_000001/model.py` |
| SB | `rec_wireless-handheld-barcode-scanner-pistol-grip-st_20260708_082427_891584_6c8ecc24` | `data/records/rec_wireless-handheld-barcode-scanner-pistol-grip-st_20260708_082427_891584_6c8ecc24/revisions/rev_000001/model.py` |
| SP | `rec_barcode_scanner_var_skeleton_presentation` | `data/records/rec_barcode_scanner_var_skeleton_presentation/revisions/rev_000001/model.py` |
| SW | `rec_barcode_scanner_var_skeleton_wand` | `data/records/rec_barcode_scanner_var_skeleton_wand/revisions/rev_000001/model.py` |
| SC | `rec_barcode_scanner_var_base_cradle` | `data/records/rec_barcode_scanner_var_base_cradle/revisions/rev_000001/model.py` |
| SM | `rec_barcode_scanner_var_mechanism_button` | `data/records/rec_barcode_scanner_var_mechanism_button/revisions/rev_000001/model.py` |
| SF | `rec_barcode_scanner_var_probe_fixedmount_tilt` | `data/records/rec_barcode_scanner_var_probe_fixedmount_tilt/revisions/rev_000001/model.py` |

## 核心身份

A handheld / countertop optical barcode reader: a scan head carrying a **recessed dark scan window** aimed forward (laser line or 2D area imager), a **defined support** (freestanding grip/tower base, dock cradle, or tilt mount foot), and **at least one real user control** (a squeeze-trigger REVOLUTE, a top scan/pair button PRISMATIC, or — for the fixed-mount form — an aiming tilt REVOLUTE). Default mature domain = small plastic electronic tool ~0.16–0.22 m tall.

不该混入：POS terminal / cash register / checkout stand（那是收银台，不是读码枪）；weighing scale / label printer / receipt printer；stylus/pen / flashlight / security camera / generic sensor housing。核心必须保留一个 recessed 前向扫描窗 + 一个真实用户控制关节。

## 槽位 + 候选模块表

三个 slot：**body_form**（① 主体形态家族 / 骨架，形态主导，登记进 `slot_choices`）、**mount**（① 接地支撑拓扑）、**control**（② 用户控制机构）。body_form 是接地 root `scanner_body`；mount 可选地插入一个接地父件（cradle/bracket）；control 挂一个运动子件。三者由 compatibility matrix 门控。

### Slot A：body_form（① / ③ Primary Form Family，形态主导主 slot）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pistol_grip` | forked_anchor | SB (+SA) | SB L48-L257（grip loft L49-67, head solids L99-168, trigger blade L172-182） | eligible if compatible | 斜握把 loft（elliptical/rounded-rect 分段 loft，Volumetric Envelope Form）+ 前倾扫描头（filleted box + 前面 pocket cut + 凹陷窗 + 橙 bezel + top_panel + ring）；grip 底 flare 接地 |
| `presentation_tower` | forked_anchor | SP | SP L54-L282（base_plate L54-74, neck loft L77-98, neck accent L101-109, head L115-182） | eligible if compatible | 宽扁 weighted base plate + 细锥 neck 立柱 loft + 顶部前倾扫描头（同 SB head 族），hands-free 台面机；base plate 底面接地 |
| `inline_wand` | forked_anchor | SW | SW L64-L212（barrel box+fillet+front pocket L64-79, side trigger L82-98, cable L101-125） | eligible if compatible | 单直筒 barrel（rounded-rect box，Volumetric Envelope Form，dx≫dz）+ 前鼻窗/激光 + 后端盖 + 侧拇指 trigger；barrel 平放接地 |
| `fixed_mount_box` | forked_anchor(+compatibility_probe) | SF | SF L73-L254（scanner box+pocket+trunnion bosses L73-117, bracket L158-172） | eligible if compatible | 紧凑 rounded 方盒 housing（Planar/Volumetric box）+ 前凹窗 + 激光 + 侧 trunnion bosses；须配 tilt bracket mount（下一 slot） |

### Slot B：mount（① 接地支撑拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | SA/SB/SP/SW | SB build L186-257（grip 直接接地）/ SP base plate | eligible if compatible | 无独立支撑件；`scanner_body` 自身接地为 root（grip flare / tower plate / wand 平放） |
| `charging_cradle` | forked_anchor | SC | SC L195-L296（foot plate L195-203, upright U-saddle + head-support plate L206-296），FIXED dock L394-400 | eligible if compatible | 独立 `cradle_base` root（weighted foot + 竖直 U-channel saddle + head-support plate）；`scanner_body` 以 FIXED nose-up 姿态坐入 dock |
| `tilt_bracket` | forked_anchor | SF | SF L158-172（ClevisBracketGeometry U 型两颊 + 底板 + bore），REVOLUTE tilt L237-252 | eligible if compatible | 独立 `mount_base` clevis 支架 root（两颊 + 底脚 + 横向 bore）；`scanner_body` 以 trunnion 插入 bore，REVOLUTE tilt 瞄准（此关节即该形态的控制机构） |

### Slot C：control（② 用户控制机构 / 运动子件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `squeeze_trigger` | forked_anchor | SB(+SA) | SB trigger blade L172-182, REVOLUTE `trigger_pivot` L247-257 | eligible if compatible | 头下悬挂 trigger blade（knuckle 捕获在头 underside），REVOLUTE 轴 +Y，正 q 后扫挤压 |
| `trigger_plus_top_button` | forked_anchor | SM | SM welled top_panel L144-162, ring bezel L165-175, button cap+stem L178-202, PRISMATIC `top_button_press` L275-287, REVOLUTE trigger L296-306 | eligible if compatible | 保留 squeeze trigger REVOLUTE，并在 top_panel 凹井里加一个 PRISMATIC 按下 scan/pair 按钮（~3 mm 行程） |
| `side_thumb_trigger` | forked_anchor | SW | SW trigger pad+stem L82-98, REVOLUTE `grip_to_trigger` L199-210 | eligible if compatible | barrel 侧面小拇指 trigger（stem 穿过筒壁），REVOLUTE 轴 -X，正 q 内按 |
| `none` | forked_anchor | SF | SF build L152-254（无 trigger，唯一非-FIXED 关节是 bracket tilt） | eligible if compatible | 无独立控制子件；控制机构由 mount 的 `tilt_bracket` REVOLUTE 提供（仅 fixed_mount_box 用） |

硬约束满足：每个 slot ≥3 candidate（body_form 4，mount 3，control 4），全部 source-backed（`forked_anchor`）。形态主导主 slot = body_form，已登记进 `slot_choices`，含 ≥3 可识别主体形态原型（pistol_grip / presentation_tower / inline_wand / fixed_mount_box）。Candidate 之间是真实 part-tree / 骨架 / 关节 / 主体形态差异，非换尺寸/涂装。

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot B mount root]                      [Slot A body_form: scanner_body]       [Slot C control child]
  none            ─(scanner_body 自身为 root, grip/plate/barrel 接地 z=0)─→
  charging_cradle ─FIXED (cradle_to_scanner, origin=dock pose, nose-up tilt)──→  scanner_body ──REVOLUTE/PRISMATIC──→ trigger / top_button
  tilt_bracket    ─REVOLUTE (bracket_hinge, axis Y, bore center, tilt aim)────→  scanner_body   (fixed_mount_box: control=none)
```

- 接口点位：
  - mount==none：`scanner_body` 直接接地，root，无跨件关节。
  - mount==charging_cradle：`cradle_base`（foot bottom = ground z=0）为 root；`scanner_body` 经 FIXED `cradle_to_scanner`（origin=dock xyz，rpy=dock pitch）坐入 U-saddle；接触面 = saddle U-channel 壁 + head-support plate（seated overlap）。
  - mount==tilt_bracket：`mount_base` clevis（底板 bottom = ground）为 root；`scanner_body` 经 REVOLUTE `bracket_hinge`（origin=bore center，axis Y）；接触 = trunnion bosses ↔ cheek bore。
  - control：trigger/top_button 挂 `scanner_body`，pivot 在头 underside / top_panel well（captured pin/stem）。
- 互斥/gating：body_form 决定 mount 与 control 的合法集合（见 §9 compatibility matrix）。fixed_mount_box 必配 tilt_bracket 且 control=none（tilt 即机构）。pistol_grip 可选 none/charging_cradle。tower/wand 仅 none。

## 每槽位 Module Emits / Interfaces

### Slot A / module pistol_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_body`（root 或 cradle/bracket 子件） | SB L189 |
| visuals | grip_shell(loft), grip_insert_wrap(loft), head_shell(box+pocket cut), window_bezel, scan_window, top_panel, ring_light, ring_button（全部 fused 到 `scanner_body`） | SB L190-238 |
| internal joints | 无（head/window/panel/ring 都是不动装饰 → parent visual，Rule 1） | SB |
| upstream interface | 接地面（grip base flare 底，z=0）或 dock/bore 坐入面 | SB / SC / SF |
| downstream interface | 头 underside pivot（喂 squeeze_trigger）+ top_panel well（喂 top_button） | SB L247, SM L275 |

### Slot A / module presentation_tower
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_body` | SP L203 |
| visuals | base_plate, neck_column(loft), neck_accent, head_shell, window_bezel, scan_window, top_panel, ring_light, ring_button | SP L206-260 |
| internal joints | 无 | SP |
| upstream interface | base_plate 底面接地 z=0 | SP L206 |
| downstream interface | 头 underside pivot / top_panel well | SP L270 |

### Slot A / module inline_wand
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_body` | SW L133 |
| visuals | barrel_shell(box+front pocket), rear_cap, scan_window, laser_line, spec_label, cable_coil(tube) | SW L135-188 |
| internal joints | 无 | SW |
| upstream interface | barrel 底面平放接地 | SW |
| downstream interface | barrel +Y 侧面 pivot（喂 side_thumb_trigger） | SW L199 |

### Slot A / module fixed_mount_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | `scanner_body` | SF L175 |
| visuals | scanner_housing(box+pocket+trunnion bosses), scan_window, laser_line, spec_label, status_led, cable_coil | SF L178-234 |
| internal joints | 无 | SF |
| upstream interface | trunnion bosses（两侧 Y 面）插入 bracket bore | SF L97-116 |
| downstream interface | 无独立 control 子件（control=none） | SF |

### Slot B / module charging_cradle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cradle_base`（root） | SC L315 |
| visuals | foot_plate, saddle_cup(U-channel + risers + head-support plate), charge_led | SC L316-330 |
| internal joints | 无（saddle/led 是 fused 装饰） | SC |
| downstream interface | dock 坐入面：FIXED `cradle_to_scanner`，origin=dock xyz，rpy=dock pitch | SC L394-400 |

### Slot B / module tilt_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mount_base`（root） | SF L156 |
| visuals | bracket（ClevisBracketGeometry U + 底板 + bore） | SF L158-172 |
| internal joints | 无 | SF |
| downstream interface | REVOLUTE `bracket_hinge`，origin=bore center (0,0,bore_z)，axis (0,-1,0)，range [-0.35,0.35] | SF L237-252 |

### Slot C / module squeeze_trigger
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trigger` | SB L240 |
| visuals | trigger_blade（knuckle + curved blade） | SB L172-182 |
| upstream interface | REVOLUTE `trigger_pivot`，origin=trigger pivot，axis (0,1,0)，range [0, squeeze] | SB L247-257 |

### Slot C / module trigger_plus_top_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trigger` + `top_button` | SM L268-289 |
| visuals | trigger_blade；button_cap+retention stem | SM L178-202 |
| internal joints | REVOLUTE `trigger_pivot`（同上）+ PRISMATIC `top_button_press`，origin=head center，axis head-local -Z，range [0, ~0.003] | SM L275-306 |
| host 依赖 | 头 top_panel 改用带凹井版本 + ring bezel（宿主 surface 派生，Rule 4） | SM L144-175 |

### Slot C / module side_thumb_trigger
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trigger` | SW L191 |
| visuals | trigger_pad + stem | SW L82-98 |
| upstream interface | REVOLUTE `grip_to_trigger`，origin=barrel +Y face pivot，axis (-1,0,0)，range [0, press] | SW L199-210 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | pistol_grip / presentation_tower / inline_wand / fixed_mount_box | pistol_grip | choice | deterministic procedural sampler | Slot A |
| `mount` | enum | none / charging_cradle / tilt_bracket | none | conditional | `∈ ALLOWED_MOUNTS[body_form]`（见 §9） | Slot B |
| `control` | enum | squeeze_trigger / trigger_plus_top_button / side_thumb_trigger / none | squeeze_trigger | conditional | `∈ ALLOWED_CONTROLS[body_form]`（见 §9） | Slot C |
| `palette` | enum | black_blue_corded / charcoal_orange_wireless / industrial_gray / retail_white / stealth_black | charcoal_orange_wireless | choice | 6 轴⑥；不改几何 | SA/SB/SF |
| `body_scale` | float | [0.95, 1.06] | 1.0 | independent | 整体主尺度倍率；clamp | SA-SF |
| `head_len_scale` | float | [0.94, 1.08] | 1.0 | independent | 头/筒长向比例（× body_scale）；clamp；fillet/pocket 绝对值保持有效 | SB/SW/SF |
| `trigger_travel` | float | REVOLUTE [0.22, 0.34] rad；PRISMATIC [0.0025, 0.0035] m | 0.30 / 0.003 | independent | 关节行程；clamp | SB/SM/SW |
| `tilt_range` | float | [0.24, 0.32] rad（对称 ±） | 0.30 | independent | bracket tilt 上/下界；clamp，box 须在 bore 间隙内全程不穿模（cheek 在 ±Y 出 tilt 平面） | SF |
| (—) | constraint | — | — | conditional | `mount`/`control` 合法集合随 `body_form` 解析（sampler 先选 body_form 再从合法集合抽） | §9 |

连续尺寸采样契约：先采 `body_scale` / `head_len_scale` / `trigger_travel` / `tilt_range`（均 independent，范围内均匀采样后 clamp）；无 equation/inequality 跨件派生（各件在同一 `scanner_body` 局部帧内按 scale 一致缩放，接口 z=0 接地与 dock/bore 坐入面由 `resolve_config` 固定）；`conditional` 的 mount/control 合法集合在采样前按 body_form 解析。

### 7.5 编译预算 / compile budget（必填）

每-seed 预算 **≤ 30 s**（依据：每个 5 星源记录单独编译均在此量级；本模板每 seed 只造一个 body_form + 一个 head + 一个 mount + 一个 control，几何量 ≈ 单个源记录）。cadquery loft/box+fillet+pocket cut 是主成本；fillet 半径用固定小绝对值（≤0.012），mesh_from_cadquery 用默认 tolerance=0.001；N 个相同子件无（本类无 multiplicity）。sweep hang-guard `--compile-timeout 120`（≈4× 预算）。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心 moving set = 至多一个 trigger + 至多一个 top_button（或一个 tilt），皆为 named singletons。trigger / scan window / scan button 在两个 origin 里都不是规则 loop-copied 簇。不暴露任何 `*_count`，不循环复制模板级 visual/part/joint。（`underfilled_reason`：barcode scanner 无 source-backed 重复同构件家族——无 louver/key/rib/shelf 阵列。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值 / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 4 种 source-backed 骨架：pistol_grip（grip loft + head + trigger）、presentation_tower（base plate + neck + head + trigger）、inline_wand（single barrel + side trigger）、fixed_mount_box（box + clevis bracket tilt）；mount 增删接地父件（none / cradle FIXED / bracket REVOLUTE）；control 增删运动子件。全部 `forked_anchor`（SA/SB/SP/SW/SC/SM/SF） |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：无 source-backed 重复件家族 |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE squeeze trigger（axis +Y，SB/SP/SC）、REVOLUTE side thumb trigger（axis -X，SW）、PRISMATIC top scan button（head-local -Z，SM）、REVOLUTE bracket tilt（axis Y，SF）；FIXED cradle dock（SC，合法子装配独立帧）。声明的每种类型都在 sweep 里出现（见 §9 axis_realization 计划） |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | 已登记进 `slot_choices` 的 body_form slot：pistol_grip=Volumetric Envelope Form（斜握把 loft 包络）、presentation_tower=Volumetric Envelope Form（立柱+宽扁底盘包络）、inline_wand=Volumetric Envelope Form（细长直筒包络，dx≫dz）、fixed_mount_box=Planar Boundary Form（矩形盒面/截面）。4 个可识别原型，source-backed |
| ④ 表面装饰 | 叠加表面细节 | 有（record_only + host-conformal） | 扫描窗类型：laser_line 1D（SA/SW/SF）vs 2D area imager in 橙 bezel（SB/SP/SC）；spec_label；illuminated ring / ring_button；grip rubber insert wrap；status/charge LED。全部作为宿主 `scanner_body` 表面 visual，凹窗由头前面 pocket 派生、bezel/label 贴头面——host-conformal，非独立 part/joint。派生顺序 ③主形→⑤尺寸→④装饰 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `body_scale` [0.95,1.06]、`head_len_scale` [0.94,1.08]（§7）。关节运动包络：squeeze/side trigger REVOLUTE 轴 +Y/-X，方向后扫/内按，[0, 0.22–0.34] rad；top_button PRISMATIC head-local -Z，[0, 0.0025–0.0035] m；bracket tilt REVOLUTE 轴 Y（bracket 旋 90° 使 bore/cheek 对齐 Y），[-0.32, +0.32] rad。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（ignore_fixed）；每个机构一个 targeted `ctx.pose`（trigger 后扫位移、button 下压位移、tilt 抬头/低头位移），无 sampled-pose exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 plastic（黑/炭灰机身）+ metal/steel（bracket/cradle 灰）+ glass（dark scan window）+ painted accent（safety-orange bezel/insert、blue trigger/ring、green LED）；配色 ≥5：black_blue_corded / charcoal_orange_wireless / industrial_gray / retail_white / stealth_black。材质大类覆盖 ≥ ceil(0.5×5)=3（plastic+metal+glass 均出现） |

## 采样与覆盖审计

总组合数（distinct slot 选择元组）：pistol_grip(mount{none,cradle}×control{squeeze,trigger+button}=4) + presentation_tower(none×{squeeze,trigger+button}=2) + inline_wand(none×side_thumb=1) + fixed_mount_box(tilt_bracket×none=1) = **8** distinct topology 元组（另有 palette×连续 scale 叠加的外观变化，不计入拓扑）。

理由：barcode scanner 是结构简单的手持电子工具（richness band **simple**）。诚实的结构词汇 = 3–4 个骨架族 + 一个 dock/bracket 支撑 + 一个主导机构（squeeze trigger）+ 一个备选机构（top button / tilt）。不用 laser-vs-imager(④)/corded-vs-wireless(④)/palette(⑥)/size(⑤) 充数拓扑。8 个拓扑元组是覆盖优先、无灌水的诚实上界。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对所有普通 seed（含 seed 0）用 `random.Random(seed)` 采样：先 `body_form`，再从 `ALLOWED_MOUNTS[body_form]` / `ALLOWED_CONTROLS[body_form]` 抽 mount/control，再抽 palette 与连续 scale。seed 0 不特殊。

Procedural Sampling / Sweep Plan：compatibility matrix / gating 见下表；非法组合（如 box 无 bracket、tower 进 cradle、box 加 trigger）由 sampler 从合法集合抽 + `resolve_config` 二次校正杜绝，不留到 builder 失败。无 regression override（默认）。Random sweep：seeds 0-35 初验；成熟度审计可 0-999。Viewer 目检 seeds 0-2。

Topology target：1000-seed slot 元组覆盖 report-only；本 simple 类真实组合空间 = 8 拓扑元组（源锚点上限 + 兼容约束所限，<300 属正常，已在上文说明真实组合空间与门控）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form 均匀 → mount/control 从 body_form 的合法集合均匀 → palette/scale | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | pistol_grip:{none,cradle}×{squeeze,trigger+button}; tower:{none}×{squeeze,trigger+button}; wand:{none}×{side_thumb}; box:{tilt_bracket}×{none} | 无 floating / collision / 轴错 / dock 悬空 / trunnion 脱 bore / trigger 穿把 |
| controlled local variation | body_scale [0.95,1.06], head_len_scale [0.94,1.08], trigger_travel, tilt_range；均 clamp | 比例变化不破接口/接地/dock 坐入/bore 间隙/joint origin/类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初验；0-999 成熟度 | contract failures; axis_realization; viewer identity |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | ③ 主体形态家族主 slot |
| mount | 3 | yes | yes | 含 `none` |
| control | 4 | yes | yes | 含 `none`（fixed_mount 专用，机构由 mount tilt 提供） |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且与 build 选择一致
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility matrix / gating 阻止非法组合（box 必配 tilt_bracket 且 control=none；tower/wand mount=none；cradle 仅 pistol_grip）
- 无 regression override；不循环小 curated/modulo 表
- 连续 scale 被 clamp，且不破坏接地/dock/bore 接口、clearance、joint origin、类别 identity
- 关键接口存在：scanner_body 接地或坐入 dock/bore；trigger pivot 在头 underside；tilt 在 bore center
- 关节 type/axis/range 符合：squeeze/side trigger REVOLUTE、top_button PRISMATIC、bracket tilt REVOLUTE、cradle FIXED
- Rule 5：`fail_if_parts_overlap_in_sampled_poses` + 每机构一 targeted pose；captured pin（trigger knuckle / trunnion / button stem）用 element-scoped `allow_overlap`

## Reject cases

- 无 recessed 扫描窗，或窗不在头前面（不再是 barcode scanner）
- 无任何非-FIXED 用户控制关节（trigger/button/tilt 全缺）
- fixed_mount_box 无 bracket → scanner 悬空 / 无接地
- trigger 悬空不接头 underside，或 squeeze 全程穿把/穿颈
- cradle/dock scanner 悬空或穿模；trunnion 脱出 bore；tilt 全程箱体撞两颊
- 漂移成 POS 终端 / 收银机 / 称重秤 / 手电 / 摄像头
- 用连续 scale 或涂装冒充拓扑多样性（拓扑必须来自离散 body_form/mount/control）

## 与相邻类别的边界

- 不该混入：POS terminal / cash register（收银台/键盘/钱箱，无手持读码枪 + trigger）
- 不该混入：weighing scale / label printer（称重/打印，无前向扫描窗 + 激光/imager）
- 不该混入：flashlight / security camera / stylus（无 recessed 扫描窗 + 用户扫描控制关节）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。simple band，8 拓扑元组，全 source-backed。 |
