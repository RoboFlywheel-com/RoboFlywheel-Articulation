# Power Switch Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `power_switch` |
| template path | `agent/templates/Equipment_Power_switch.py` |
| test path | `tests/agent/test_power_switch_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：一个 actuator 功能槽（被铰接的开关动作主体）+ 一个 mount 结构槽（承载面板/箱体的本体），再叠加一根 `gang_count` 链式 multiplicity 轴（同构开关单元沿板宽 X 等距复制）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（候选池：2 parent 基线 + 8 fork 变体；本小类为 picture-subcat fork 批，无独立 5★ 评级流水，按 picture_doctor 健康检查与 fork 收敛视作采纳源） |
| read_count | 10 |
| read_scope | all 2 parents + 8 variants in the `Equipment / Power switch` fork batch；每条 record 的 `revisions/rev_000001/model.py` 全文通读，定位 part/joint/helper 的真实行号 |
| source_index_policy | only adopted module sources are indexed below；10 条全部采纳为 module / multiplicity 源 |

**Dataset-root caveat**：本小类候选是 workbench-only 的 picture-subcat fork，直接 root 在 `articraft_data` repo 内（`collections=['workbench']`，未 promote），由 `articraft fork` 派生并 reconcile 进 `Equipment__Power_switch` picture shard。本 spec 引用一律采用 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly` 形式，行号取自上述仓库内的真实 `model.py`。

- 2 parents（各覆盖自己的 actuator+mount 基线格）：
  - `rec_build-a-realistic-articulated-3d-model-of-a-wall_20260609_154028_849119_5b4ad2d8`（扁平 WALL PLATE + roller_bail 拉闸；gang N=1 基线，所有 actuator fork 与 gang fork 均派生自此）
  - `rec_build-a-realistic-articulated-3d-model-of-a-powe_20260609_180112_553528_621bac5e`（PENDANT BOX 吊挂控制箱 + grab-handle slider + 3 按钮；所有 mount fork 均派生自此）
- 8 variants（变体目录名即 record_id）：`rec_power_switch_var_actuator_flip_toggle`、`rec_power_switch_var_actuator_rocker`、`rec_power_switch_var_actuator_pushbutton`、`rec_power_switch_var_actuator_rotary`、`rec_power_switch_var_mount_enclosure`、`rec_power_switch_var_mount_inline`、`rec_power_switch_var_gang_n2`、`rec_power_switch_var_gang_n3`。
- 正交分布：actuator 4 个 fork 全部带 flat_wall_plate（继承 5b4ad2d8），mount 2 个 fork 全部带 grab_handle_slider（继承 621bac5e）。某 actuator × 某 mount 的跨格混搭由模板 compatibility matrix 裁决，不在本批 fork 内。

## 核心身份

Power switch 是工作台尺度的设备级电源开关：一个固定的承载本体（墙装面板 / 吊挂控制箱 / 工业隔离箱 / 在线线缆桶）上挂着一个被用户操作的可动执行机构（actuator），actuator 绕本体前控制面做一次有限行程的开/关动作（翻摆、旋转、压入或线性推拉）。

固定本体（mount）提供：前控制面 / 凹陷 field、actuator 的专属承托件（keeper / boss / well / bezel / escutcheon / track），以及装饰性固定细节（louver 排气垫、角螺钉、conduit 管 + gland、cord 出线 boss、lug 安装耳）——这些都作为 mount 的 parent visual，不作为独立 part。

actuator（开关动作主体）必须有真实 articulation 语义，且行程有限（不是连续自由旋转）。可选地，单一墙装面板可沿板宽 X 联排多个同构开关单元（gang）。

边界：
- 不包括连续旋转、大刻度盘的旋钮（读作调光器/定时器旋钮）：rotary actuator 必须是有限行程的选择凸轮（限位 ±0.85 rad），不是无限连续转。
- 不包括无可动件的纯指示灯/信号灯：power switch 必须至少有一个非 FIXED 的 actuator joint。
- inline 线缆在线开关现实中不联排：`gang_count > 1` 不套用于 inline_cord_barrel。

## 槽位 + 候选模块表

### Slot A：actuator（被铰接的执行机构——开关动作主体）

| module_name | record_id | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `roller_bail_drawlatch` | `rec_..._5b4ad2d8`（parent） | `.../model.py:L281-L325`（moving `_build_bail_arms`+`_build_roller`），fixed 承托 `_build_keeper` L208-L229 + `_build_side_bolts` L232-L254，joint `plate_to_bail` L381-L391 | eligible if compatible | 双臂滚柱拉闸越中扳过 keeper，绕侧螺栓 X 轴翻摆；hub 捕获 side_bolts（captured-pin） |
| `grab_handle_slider` | `rec_..._621bac5e`（parent） | `.../model.py:L311-L360`（moving `_build_slider_mesh`），slot 在 `selector_faceplate` L256-L308，joint `housing_to_slider` L469-L479 | eligible if compatible | 抓手块在 faceplate 竖槽内上拉/下推的线性隔离手柄 |
| `flip_toggle_dolly` | `rec_power_switch_var_actuator_flip_toggle` | `.../model.py:L297-L341`（moving `_build_toggle_lever`），fixed `_build_toggle_boss` L213-L270，joint `plate_to_toggle` L385-L395 | eligible if compatible | 单根中央 dolly 拨杆在 raised boss 双 ear 间捕获翻转，窄行程 ±9° |
| `rocker_paddle` | `rec_power_switch_var_actuator_rocker` | `.../model.py:L271-L311`（moving `_build_rocker_paddle` + marks L314-L337），fixed `_build_rocker_well` L205-L244，joint `plate_to_paddle` L393-L403 | eligible if compatible | 宽矩形跷板在 molded well 内绕中央横轴 see-saw，±0.24 rad |
| `pushbutton_cap` | `rec_power_switch_var_actuator_pushbutton` | `.../model.py:L262-L297`（moving `_build_button_cap`），fixed `_build_button_bezel` L209-L220 + `_build_bore_shadow` L223-L235，joint `plate_to_button` L347-L357 | eligible if compatible | 圆顶瞬动按钮压入 bezel 镗孔，唯一沿面法向 PRISMATIC 的行程 |
| `rotary_cam_selector` | `rec_power_switch_var_actuator_rotary` | `.../model.py:L278-L302`（moving `_build_knob_body` + `_build_pointer_skirt` L305-L320），fixed `_build_rotary_mount` L206-L251，joint `plate_to_selector` L370-L380 | eligible if compatible | 带指针 skirt 的旋转凸轮选择钮，绕面法向 Z 有限转 ±0.85 rad |

### Slot B：mount（承载 actuator + 面板的结构本体——结构槽，非复制体）

| module_name | record_id | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_wall_plate` | `rec_..._5b4ad2d8`（parent） | root `faceplate` 装配 `.../model.py:L335-L365`，`_build_faceplate` L126-L180 + `_build_louver_pad` L183-L205 + `_build_screws` L257-L275 | eligible if compatible | 薄壁竖向壁装面板（90×130×8mm），圆角竖板 + 凹 field + 顶 louver 垫 + 角螺钉；**唯一支持 gang>1 的 mount** |
| `pendant_box` | `rec_..._621bac5e`（parent） | root `housing` 装配 `.../model.py:L401-L460`，`_build_shell_mesh` L111-L160 + `_build_cage_mesh` L229-L253 + gland_collar L429-L442 + FIXED conduit_tubes L444-L460 | eligible if compatible | 吊挂八角 ABS 控制箱，顶 conduit 管 + 白 gland + cage 框 |
| `industrial_enclosure_box` | `rec_power_switch_var_mount_enclosure` | root `housing`（`square_industrial_isolator`）`.../model.py:L428-L521`，`_build_shell_mesh` L108-L141 + `_build_lid_lip_mesh` L144-L162 + `_build_lug_boss_mesh` L177-L202（`_lug_center` L165-L174） | eligible if compatible | 方形工业隔离箱（112×112×40mm），盖唇 lid_lip + 四角安装 lug boss；保留 slider + 3 button |
| `inline_cord_barrel` | `rec_power_switch_var_mount_inline` | root `housing`（`inline_cord_power_switch`）`.../model.py:L271-L340`，`_build_shell_mesh` L78-L107 + cord boss `_end_boss`/`_build_cord_bosses_mesh` L110-L134 + cord stub L137-L150 + `_build_top_cover_mesh` L153-L172 + `_build_slider_track_mesh` L199-L213 | eligible if compatible | 线缆中段在线开关圆角桶，两端 cord 出线 boss + 顶盖滑轨；仅保留 `slider`（无 button），**排除 gang>1** |

硬约束满足：Slot A = 6 candidate（≥3），Slot B = 4 candidate（≥3）。每个 candidate 结构不同（不同 part 树 / joint type / 承托件），均有真实 `model.py:Lx-Ly` 来源。

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot B mount]  --(per-candidate actuator joint, origin 贴 mount 前控制面)-->  [Slot A actuator]
                \
                 --(gang_count 链式 multiplicity, 仅 flat_wall_plate)--> actuator_{0..N-1} 沿板宽 X 等距

actuator joint type/axis 随 Slot A 候选而变（CRITICAL，逐候选声明）：
  roller_bail_drawlatch  REVOLUTE  axis (1,0,0)  X 横轴翻摆
  flip_toggle_dolly      REVOLUTE  axis (1,0,0)  X 横轴翻摆
  rocker_paddle          REVOLUTE  axis (1,0,0)  X 横轴 see-saw
  rotary_cam_selector    REVOLUTE  axis (0,0,1)  Z 面法向转
  pushbutton_cap         PRISMATIC axis (0,0,-1) -Z 法向压入
  grab_handle_slider     PRISMATIC axis (0,1,0)  +Y 竖向/纵向行程
```

跨 slot 接口：
- actuator ↔ mount：所有 actuator 都挂在 mount 前控制面（plate `faceplate_shell` 前面 z≈`PLATE_T`，或 pendant/enclosure `selector_faceplate` 面，或 inline `BARREL_T` 顶面）；joint origin 贴前面/凹 field，mating face = 前控制面，anchor = actuator (x,y) 中心。
- 每种 actuator 自带其专属固定承托件（roller=keeper+side_bolts；toggle=raised_boss 双 ear；rocker=rocker_well；pushbutton=button_bezel 镗孔；rotary=rotary_mount escutcheon；slider=faceplate slot / 顶盖 track）。换 actuator 时连承托件一起替换。
- gang 单元 ↔ plate：每个 `bail_{i}` 的 `plate_to_bail_{i}` origin = `(_unit_x(i), PIVOT_Y, PIVOT_Z)`，mating face = 共享 `faceplate_shell` 前面，anchor = 各单元 keeper/side_bolt 联接处。各单元独立、互不联动。

## 每槽位 Module Emits / Interfaces

### Slot A / module `roller_bail_drawlatch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `roller_bail`（`bail_arms` + `roller`） | `.../5b4ad2d8/.../model.py:L367-L379` |
| internal joints | 无（bail 是单刚体） | — |
| upstream interface | hub 捕获固定 `side_bolts`（element-scoped allow_overlap） | L232-L254 / L458-L465 |
| downstream/consumer joint | `plate_to_bail` REVOLUTE **axis (1,0,0)**，origin `(0,PIVOT_Y,PIVOT_Z)`，limits `[-0.20, 1.30]` | L381-L391 |

### Slot A / module `flip_toggle_dolly`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `toggle`（`toggle_lever`） | `.../flip_toggle/.../model.py:L377-L383` |
| upstream interface | hub 捕获在 `raised_boss` 双 ear 间 | L213-L270 |
| consumer joint | `plate_to_toggle` REVOLUTE **axis (1,0,0)**，limits `rad(-10°)..rad(9°)` | L385-L395 |

### Slot A / module `rocker_paddle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `rocker_paddle`（`paddle_shell` + `top_mark` + `bottom_mark`） | `.../rocker/.../model.py:L373-L391` |
| upstream interface | pivot foot 接触 field，paddle 框在 `rocker_well` 内 | L205-L244 |
| consumer joint | `plate_to_paddle` REVOLUTE **axis (1,0,0)**，limits `[-0.24, 0.24]` | L393-L403 |

### Slot A / module `rotary_cam_selector`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `selector_knob`（`knob_skirt` + `pointer_skirt`） | `.../rotary/.../model.py:L356-L368` |
| upstream interface | knob skirt 坐落 `rotary_mount` escutcheon 面 | L206-L251 |
| consumer joint | `plate_to_selector` REVOLUTE **axis (0,0,1)**，limits `[-0.85, 0.85]` | L370-L380 |

### Slot A / module `pushbutton_cap`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `button_cap` | `.../pushbutton/.../model.py:L339-L345` |
| upstream interface | skirt 落入 `button_bezel` 真实通孔 + `bore_shadow` 套筒 | L209-L235 |
| consumer joint | `plate_to_button` PRISMATIC **axis (0,0,-1)**，travel `[0, 0.0040]` | L347-L357 |

### Slot A / module `grab_handle_slider`
| emits | 描述 | 来源 |
|---|---|---|
| parts | moving `slider`（block + neck + grab loop） | `.../621bac5e/.../model.py:L463-L468` |
| upstream interface | block 在 `selector_faceplate` 竖槽内，bear on field floor | L311-L360 |
| consumer joint | `housing_to_slider` PRISMATIC **axis (0,1,0)**，travel `[0, SLIDER_TRAVEL]` | L469-L479 |

### Slot B / module `flat_wall_plate`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `faceplate`（`faceplate_shell` + `louver_pad` + `mount_screws`） | `.../5b4ad2d8/.../model.py:L335-L365` |
| internal joints | 无（root 纯固定本体） | — |
| downstream interface | 前控制面 z=`PLATE_T`，接收 actuator joint origin；支持 gang>1 沿 X 复制 | L126-L205 |

### Slot B / module `pendant_box`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `housing`（shell + cage + gland_collar + FIXED conduit_tubes + selector_faceplate） | `.../621bac5e/.../model.py:L401-L460` |
| internal joints | 无（conduit_tubes 是固定 visual，明确不铰接） | L444-L460 / L529-L535 |
| downstream interface | `selector_faceplate` 竖槽 + 底排 3 button 镗孔 | L256-L308 |

### Slot B / module `industrial_enclosure_box`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `housing`（shell + lid_lip + 4×lug_boss + cage + selector_faceplate） | `.../enclosure/.../model.py:L442-L479` |
| internal joints | 无（lid_lip/lug_boss 固定 visual） | L144-L202 |
| downstream interface | `selector_faceplate` 竖槽 + 3 button 镗孔（保留 slider+button） | L298-L350 |

### Slot B / module `inline_cord_barrel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `housing`（rounded shell + top_cover + cord bosses + cord stubs + slider_track） | `.../inline/.../model.py:L282-L317` |
| internal joints | 无（cord boss/stub 固定 visual） | L110-L213 |
| downstream interface | 顶盖 `slider_track` 长槽（轴向沿桶长 Y）；**仅承载 slider，无 button，无 gang** | L199-L213 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `actuator_style` | enum | `roller_bail_drawlatch` / `grab_handle_slider` / `flip_toggle_dolly` / `rocker_paddle` / `pushbutton_cap` / `rotary_cam_selector` | `roller_bail_drawlatch` | choice | 由 deterministic procedural sampler 选择；决定 consumer joint type/axis/range（见槽位图） | Slot A table |
| `mount_style` | enum | `flat_wall_plate` / `pendant_box` / `industrial_enclosure_box` / `inline_cord_barrel` | `flat_wall_plate` | choice | 由 sampler 选择 | Slot B table |
| `gang_count` | int | `[1, 6]` | 1 | conditional | 仅 `mount_style==flat_wall_plate` 且 `actuator_style==roller_bail_drawlatch` 时可 >1；其余 mount/actuator 强制 =1 | n2 L68 / n3 L40 |
| `unit_pitch` | float | `[0.058, 0.070]` | 0.066 | independent | 板宽 X 单元间距；clamp 后保证相邻 keeper 不穿模 | n2 `.../gang_n2/.../model.py:L69`，n3 L41 |
| `plate_w` | float | derived | 0.090 | equation | `= max(0.090, gang_count * unit_pitch + 2*edge_margin)`，随 N 自动加宽 | n2 L40 vs parent L38 |
| `actuator_throw` | float | per-candidate | 见各 joint | conditional | REVOLUTE：toggle `rad(-10..9)`、rocker `±0.24`、rotary `±0.85`、roller `[-0.20,1.30]`；PRISMATIC：button `[0,0.0040]`、slider `[0,SLIDER_TRAVEL]` | 各 joint limits |
| (—) | constraint | — | — | inequality | gang：`gang_count * unit_pitch ≤ plate_w - 2*edge_margin`；违反则回缩 unit_pitch 或拒绝重采 | n2 `_unit_x` L115-L117 |
| `palette` | enum | plate_metal / abs_gray / painted_steel / … | per-module | choice | module-local 材质，不改拓扑 | 各 `_register_materials` |

连续尺寸采样契约：先采 `unit_pitch`（independent）→ 派生 `plate_w`（equation）→ 用 gang inequality 投影/回缩 → `gang_count` 与 `actuator_throw` 范围按 `actuator_style`/`mount_style` 上游 choice 解析（conditional）。

## Multiplicity / Copy Logic

本 spec 有 **1 根** multiplicity 轴。

- `count_param`：`gang_count`（变体源码命名不统一——n2 用 `UNIT_COUNT`、n3 用 `BAIL_COUNT`；模板统一为 `gang_count`）。
- `N_range`：`[1, 6]`（真实联排开关常见 1–4 gang，留余量到 6）。测试偏小（N∈{1,2,3} 有已收敛样本），产品全程到 6。
- sampling domain（权重档）：小 N 高频（N=1/2/3 占绝大多数），N=4..6 稀有尾部。
- copied object：一个开关 gang 单元 = 一条 moving `roller_bail` + 其专属固定板特征（`_build_keeper(x_off)` + `_build_side_bolts(x_off)`，n3 还含 per-unit `_build_louver_pad(x_off)`），共享 `faceplate` 壁板为根。
- naming：part `bail_{i}`、joint `plate_to_bail_{i}`，`for i in range(gang_count)` 循环发射；n2 用 `_add_bail_unit_visuals(bail, i)` 封装单元视觉。
- placement：沿板宽 X 等距，`_unit_x(i) = (i - (N-1)/2) * UNIT_PITCH` 居中对称。
- joint policy：每个 gang 自带独立 `plate_to_bail_{i}` REVOLUTE，axis `(1,0,0)`，limits 全单元一致，互不联动（n2 run_tests 显式验证 independence）。
- source / gating：
  - **copy-logic 源码取变体（不取 parent）**：parent（N=1，`.../5b4ad2d8/.../model.py:L367-L391`）以 `roller_bail`/`plate_to_bail` 手写单元、**未循环化**；n2（`.../gang_n2/.../model.py`：`_unit_x` L115-L117，fixed 循环 L376-L395，bail/joint 循环 L397-L412）与 n3（`.../gang_n3/.../model.py`：`BAIL_COUNT` L40，循环 L364-L411）已重写为 `bail_{i}`/`plate_to_bail_{i}` + `_unit_x(i)` 干净循环链，模板应以 n2/n3 为复制逻辑源。
  - **gating**：`gang_count > 1` 仅在 `flat_wall_plate` × `roller_bail_drawlatch` 上验证收敛。其余 mount（pendant_box / industrial_enclosure_box / inline_cord_barrel）与其余 actuator 套 gang>1 **未造样本**，由 compatibility matrix 强制 `gang_count = 1`，不假定任意 mount × 任意 N 收敛。N=1 退化为单 `plate_to_bail` 命名。

## 拓扑多样性审计


理由：actuator 槽单独就产生 4 种不同 joint 拓扑（REVOLUTE X / REVOLUTE Z / PRISMATIC −Z / PRISMATIC +Y），mount 槽改变 root part 集合与固定 visual 拓扑，gang 轴改变 moving child 数量与 joint 数量；三者正交叠加。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling，`seed=0` 不特殊。先选 mount，再从 compatible actuator 集合选 actuator，再按 gating 决定是否开 `gang_count`，最后采连续 scale。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本小类受 actuator×mount compatibility 裁剪与 gang gating 约束，distinct 上限主要由「合法 actuator×mount 组合 × N 档 × 局部 scale 分箱」决定，若低于 300 需在审核时记录裁剪原因。

Controlled local parameterization：初版应含 `unit_pitch`（gang 间距，independent，clamp `[0.058,0.070]`）、`plate_w`（derived，随 N 加宽）、各 actuator 的 `actuator_throw`（conditional，按 candidate joint limits）。所有连续参数在 `resolve_config` 内 clamp/派生，不破坏 InterfaceSpec / MatingContract / multiplicity；跨部件依赖（plate_w↔gang_count×unit_pitch）以 equation/inequality 显式声明。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mount→actuator→gang→scale 顺序；加权 choice，小 N 高频 | slot_choices_for_seed matches build choices |
| compatibility matrix | gang>1 仅 flat_wall_plate×roller_bail；inline 强制 N=1 无 button；rotary/button/slider/toggle/rocker × gang>1 非法降级为 N=1 | no floating, collision, axis 正确, max multiplicity, optional moving child |
| controlled local variation | unit_pitch / plate_w / actuator_throw，clamp+derive | proportions vary，keeper 不穿模，joint origin 贴前控制面 |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初版，0-999 成熟度审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A actuator | 6 | yes | yes | 4 种 joint 拓扑 |
| B mount | 4 | yes | yes | 4 种 root 固定拓扑 |

## Validator
- slot_choices_for_seed returns implemented module names（6 actuator + 4 mount）。
- config_from_seed uses deterministic procedural sampling for all ordinary seeds。
- compatibility matrix / gating prevents illegal combos：gang>1 只在 flat_wall_plate×roller_bail；inline 永远 N=1 且无 button。
- **每候选 consumer joint 轴向正确**（CRITICAL，不可统一硬编码）：roller/toggle/rocker → REVOLUTE axis (1,0,0)；rotary → REVOLUTE axis (0,0,1)；pushbutton → PRISMATIC axis (0,0,-1)；slider → PRISMATIC axis (0,1,0)。
- key joint limits 落在各 candidate 的真实 range（toggle rad(-10..9)、rocker ±0.24、rotary ±0.85、roller [-0.20,1.30]、button [0,0.0040]、slider [0,SLIDER_TRAVEL]）。
- actuator joint origin 贴 mount 前控制面；actuator 的专属承托件随 actuator 一起替换。
- gang：`plate_to_bail_{i}` 等距对称（`_unit_x`），各单元独立可动（一个铰接不带动另一个），plate_w 随 N 加宽。
- captured-pin overlap（roller hub↔side_bolts、toggle hub↔boss ears、button skirt↔bore）用 element-scoped allow_overlap，理由可见。
- final templates 不靠 small curated/modulo 表做主 seed domain；continuous scale 在 resolve_config 内 clamp/派生。

## Reject cases
- actuator joint 用单一硬编码 X 轴套到 rotary（应 Z）/ pushbutton（应 −Z）/ slider（应 +Y）上 → 轴向错误。
- actuator 做成连续自由旋转的大刻度盘旋钮（无限位）→ 读作调光器/定时器，出类目。
- 没有任何非 FIXED actuator joint（纯指示灯/信号灯）→ 不是 power switch。
- gang_count>1 套在 pendant_box / industrial_enclosure_box / inline_cord_barrel / 非 roller actuator 上 → compatibility gate 未裁剪。
- inline_cord_barrel 出现 button 或 N>1，或 cord boss/stub 不在桶两端 → 误装配。
- actuator 或 gang 单元悬空 / 用不可见接口盘连接 mount，或承托件（keeper/boss/well/bezel/escutcheon/track）缺失。
- 把 louver/conduit/gland/lug/cord 等固定细节做成独立 FIXED child part，而非 mount parent visual。
- plate_w 不随 gang_count 加宽 → 多单元穿模或溢出板边。

## 与相邻类别的边界
- 不该混入：调光器 / 定时器旋钮（`dimmer` / `timer_knob`）——它们是连续旋转大刻度盘读数；power switch 的 rotary 是有限行程选择凸轮（±0.85 rad），且核心身份是开/关而非连续调节。
- 不该混入：指示灯 / 信号灯（`indicator_light`）——纯发光、无可动件；power switch 必须有至少一个非 FIXED actuator joint。
- 不该混入：断路器面板 / 配电箱阵列——本类是单一开关本体（最多沿 X 联排同构 gang），不是带母排/多回路的配电拓扑。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。重点复核：(1) per-candidate consumer joint 轴向声明是否在模板实现中逐 module 落地，禁止统一硬编码 X 轴；(2) gang_count gating 是否严格限定 flat_wall_plate×roller_bail；(3) multiplicity copy-logic 以 n2/n3 循环链为源而非 parent 手写单元。审核通过前不进入模板实现。 |
