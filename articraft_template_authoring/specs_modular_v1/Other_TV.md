# tv (vintage CRT / cabinet television set) — Modular Spec

> 来源小类：`picture/Other/TV`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__TV.md`。
> **"TV" 在此 = 1980s 木纹机壳 CRT 电视机（display cabinet with a recessed CRT screen, a control column with channel dial + small knobs, on a tabletop / legs / swivel base）。不是平板挂墙电视、不是显示器（无独立 stand-neck tilt/swivel 颈）、不是收音机。**
> 结构家族 = CRT 电视：root `cabinet`（木壳 / 圆角太空舱 / 便携壳，含凹陷 front_plate + CRT bezel + 凸/平/圆 玻璃管 + 控制柱 vent/grille/nameplate）+ `channel_dial`（CONTINUOUS +X 旋钮）+ N 个小 `knob_{i}`（REVOLUTE +X）；可选 `swivel_base`（root pedestal，CONTINUOUS +Z 转台，cabinet 成为其 child）。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 个 parent + 8 个 fork 槽位/多重性变体）已同步进本仓库 `data/records/`，rating=5、compile=success、workbench-only、≥1 非 fixed joint。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字**为准（`cabinet` / `front_plate` / `crt_screen` / `screen_bezel` / `channel_dial` / `knob_{i}` / `cabinet_to_channel_dial` / `cabinet_to_knob_{i}` / `swivel_base` / `base_to_cabinet` / `_build_crt_glass_mesh` / `_build_porthole_glass_mesh` / `_build_pod_shell` / `_build_console_leg_mesh` / `_build_swivel_base_mesh` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `tv` |
| template path | `agent/templates/Other_TV.py` |
| test path (optional) | `tests/agent/test_tv_template.py`（不写，sweep-pipeline 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: cabinet_form + screen_tube + base_support，**外加** `knob_count` 控制旋钮多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 槽位/多重性变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本，无污染排除 |

阅读要点（用于槽位分解）：
- **基线拓扑（parent，`f8f3f341`）**：root `cabinet`（6 块木板 box 壳 + 凹陷 `front_plate` + `screen_bezel`(BezelGeometry) + `crt_screen`(LoftGeometry 凸面管) + 控制柱 `vent_recess`/`vent_louver_{i}`/`dial_escutcheon`/`grille_recess`/`grille_slat_{0..11}`/`samsung_nameplate`）+ `channel_dial`(child, **CONTINUOUS +X**, DIAL_JOINT_X 处) + 3 个具名小旋钮 `volume_knob`/`brightness_knob`/`tuning_knob`(child, **REVOLUTE +X**, ±135°)。所有 dial/knob `*_stem` captured 在 `front_plate` 孔内（allow_overlap + expect_overlap retained-insertion）。front 朝 +X，地面 z=0。
- **cabinet_form 轴（Slot A）**：rounded_space_age_pod（`_build_pod_shell` cadquery box+`edges("|Z").fillet`+cut cavity → 单曲面 mesh `pod_shell` 替 6 块木板，且已把 3 旋钮循环化为 `knob_{i}`/KNOB_COUNT）/ portable_with_handle（在 6 板木壳上加固定 inline `carry_handle`(tube_from_spline_points 拱形提梁) visual）。两者 part 树 / joint 拓扑与 parent 相同——cabinet_form 主要改 **壳体 mesh + 可选固定附件 visual**，不增删活动件。
- **screen_tube 轴（Slot B）**：flat_face_crt（`_build_crt_glass_mesh` 把 LoftGeometry sections 改近平面 ~1.5mm 微凸，bezel 仍矩形）/ porthole_round（`_build_porthole_glass_mesh` 用 **LatheGeometry** 圆顶 dome + bezel 改 `opening_shape="circle"` 圆 bezel）。仅换 `crt_screen`/`screen_bezel` 两个 visual 的 mesh-helper，**part 树 / joint 拓扑不变** → screen_tube 是 mesh-helper 维度（屏幕身份特征 primitive）。
- **base_support 轴（Slot C）—— 唯一真正改 part 树 / joint 拓扑的槽**：splayed_console_legs（`_build_console_leg_mesh` 4 条 LatheGeometry 撇腿作 cabinet 固定 inline visual `leg_{i}`+`leg_mount_{i}`，全 cabinet z-坐标抬 `Z_LIFT`，**无新 joint**）/ swivel_base（新增 root part `swivel_base`(`_build_swivel_base_mesh` lathe pedestal + `turntable_ring`)，cabinet 降为 child，**新增 `base_to_cabinet` CONTINUOUS +Z 转台 joint**，origin 在 PEDESTAL_TOP_Z）。tabletop 基线落地无支撑件、swivel_base 增一根独立 spine + root 切换。
- **knob_count 轴（Slot D 多重性）**：N=2(`KNOB_COUNT=2`)/N=5(`KNOB_COUNT=5`)，pod 变体已用 `KNOB_COUNT=3`。统一范式 `for i in range(N)` 发 `knob_{i}` part + `knob_{i}_stem`/`knob_{i}_cap` visual + `cabinet_to_knob_{i}` REVOLUTE +X，`knob_y = COL_Y + (i-(N-1)/2)·KNOB_SPACING` **沿 Y 等距**（不是 Z；source map 写"沿 Z"有误，实样沿控制柱 Y 排）→ 同构旋钮 N 次复制，各独立 REVOLUTE，N=3 即多数基线。`grille_slat_{0..11}` 是固定 12 片循环 visual（**无 joint，不暴露为模板 multiplicity**，作 cabinet 装饰 inline，照搬常数 12）。

## 核心身份

一台 **1980s 木纹 / 复古 CRT 电视机**：root `cabinet`（约 0.62m 宽 ×0.45m 高 ×0.32m 深，front 朝 +X，地面 z=0），机壳内嵌一块凹陷 `front_plate`，左 2/3 是 CRT 区（`screen_bezel` 框 + 凸/平/圆 `crt_screen` 玻璃管），右 1/3 是控制柱（顶部百叶 `vent`、方形 `dial_escutcheon`、细横条 `grille_slat`×12 喇叭格栅、`samsung_nameplate`）。活动语义 = **频道选台旋钮 `channel_dial`（CONTINUOUS 绕 +X 无限旋转，带 off-axis `pointer_wedge` 证明连续转动）+ N 个小控制旋钮 `knob_{i}`（REVOLUTE 绕 +X，±135°）**，全部 `*_stem` 轴穿入 front_plate 孔内 captured。可选 **swivel_base 转台**（cabinet 骑在 pedestal 上，`base_to_cabinet` CONTINUOUS 绕 +Z 左右转）。默认成熟域：cabinet_form × screen_tube × base_support × 旋钮数 N∈[1,8] 的桌面/落地式 CRT 电视。

不该混入：
- **平板挂墙电视 / 现代 LCD/OLED TV**——薄板无机壳深度、无 CRT 玻璃管 / 选台旋钮 / 木壳，主身份完全不同。
- **桌面显示器（desktop monitor）**——有独立 stand-neck 的 tilt/swivel 颈柱（见 `desktop_monitor_with_tilt_swivel_stand`），主运动 spine 是显示头绕颈倾仰；本类无颈、屏固定在机壳里，活动件是旋钮（swivel 是整机转台，不是屏倾仰）。
- **收音机 / 音响（radio / hi-fi）**——同有旋钮 + 格栅，但缺 CRT 屏 bezel + 玻璃管这套电视身份。

## 槽位 + 候选模块表

> **建模注记**：`cabinet_form`（Slot A）与 `screen_tube`（Slot B）都是**同一 part 树上不同 mesh / 固定 visual 的替换**（壳体 mesh、屏玻璃 mesh、bezel 形状、可选提梁），由 form-aware mesh helper 一次决定，**不增删活动件**；列为候选轴以对齐 schema 并与 base_support / N 笛卡尔积撑开多样性（见 §9）。`base_support`（Slot C）才是真正改 part 树 / root / joint 拓扑的轴（swivel_base 增一根 CONTINUOUS +Z spine + root 切换）。`knob_count`（Slot D）是同构旋钮 N 次复制的多重性轴。

### Slot A：cabinet_form（机壳形态 —— root cabinet 壳体 mesh + 可选固定附件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| boxy_wood（基线） | rec_model-…f8f3f341（parent）| 6-板木壳 L120-149 / `front_plate` L152-157 | eligible if compatible | 6 块 `Box` 木板（bottom/top/left/right/back + front_plate）拼方木壳；矩形机壳基线；root=cabinet |
| rounded_space_age_pod | rec_variant-…1a475b57 | `_build_pod_shell` L118-135 / `pod_shell` 装配 L157-162 / `front_plate` L164-169 | eligible if compatible | cadquery `box`+`edges("|Z").fillet(POD_FILLET)`+cut cavity → 单曲面 `pod_shell` mesh 替 6 板（强圆角太空舱）；part 树 / joint 与 parent 同（已用 `knob_{i}` 循环）|
| portable_with_handle | rec_variant-…cb7ecf95 | 6-板木壳 L123-160 / `carry_handle` L162-187（`tube_from_spline_points`）| eligible if compatible | 6 板木壳 + 顶部固定 inline `carry_handle`（拱形 tube 提梁，arch peak ~+0.09m，非移动件）；part 树 / joint 与 parent 同 |

### Slot B：screen_tube（屏幕 / 显像管 —— `crt_screen`+`screen_bezel` 两 visual 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bulged_crt_glass（基线） | rec_model-…f8f3f341（parent）| `_build_crt_glass_mesh` L90-103（凸面 sections）/ `screen_bezel`(矩形) L160-176 / `crt_screen` L177-182 | eligible if compatible | LoftGeometry 凸面 rounded-rect 玻璃管（4 段渐窄前凸 cap）+ 矩形 `rounded_rect` bezel；经典凸面 CRT |
| flat_face_crt | rec_variant-…d3e64ba3 | `_build_crt_glass_mesh` L91-108（近平面 sections）/ bezel+screen 装配 L164-187 | eligible if compatible | LoftGeometry sections 改近平面（~1.5mm 微凸）→ 晚期平面直角 CRT；bezel 仍矩形；仅 sections_spec 数值变 |
| porthole_round | rec_variant-…fa608269 | `_build_porthole_glass_mesh` L71-90（**LatheGeometry** 圆顶）/ 圆 bezel(`opening_shape="circle"`) L150-165 | eligible if compatible | LatheGeometry 圆顶 dome 玻璃 + 圆形 bezel（`opening_shape="circle"`/`outer_shape="circle"`）→ 圆窗 porthole CRT；换 lathe helper + bezel 形状 |

### Slot C：base_support（支撑 —— **唯一改 part 树 / root / joint 拓扑的主机构槽**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| tabletop（基线） | rec_model-…f8f3f341（parent）| cabinet 落地装配 L120-157（bottom_panel z=WOOD_T/2）| eligible if compatible | cabinet 直接坐地（bottom_panel 中心 z=WOOD_T/2，地面接触），**无支撑件、无新 part / joint**，root=cabinet |
| splayed_console_legs | rec_variant-…f3c0f936 | `_build_console_leg_mesh` L117-128 / `leg_{i}`+`leg_mount_{i}` L266-296 / `Z_LIFT` 抬升 L53,L152-263 | eligible if compatible | 4 条 LatheGeometry 锥撇腿作 cabinet **固定 inline visual** `leg_{0..3}`（roll=π 翻转 + SPLAY_ANGLE 外撇 + yaw 朝内）+ `leg_mount_{i}` 安装块；全 cabinet z-坐标抬 `Z_LIFT≈0.147`，**无新 joint**，root 仍=cabinet |
| swivel_base | rec_variant-…397aff58 | `_build_swivel_base_mesh` L117-133 / `swivel_base` part+`pedestal`+`turntable_ring` L151-164 / `base_to_cabinet` CONTINUOUS +Z L385-393 | eligible if compatible | **新增 root part `swivel_base`**（lathe 圆 pedestal + `turntable_ring`），cabinet 降为 child；**新增 `base_to_cabinet` CONTINUOUS axis=(0,0,1) 转台 joint**，origin=(0,0,PEDESTAL_TOP_Z)；root 切换为 swivel_base |

## 槽位图（slot graph）

pattern: mixed（cabinet_form + screen_tube 决定 root cabinet 的壳体 / 屏 / 附件 mesh（parallel children visual），base_support 决定 root 切换与可选转台 spine，knob_count 在 cabinet 上 N 次复制控制旋钮）

```
[base_support slot] 决定 root：
  tabletop / splayed_console_legs:  root = cabinet（坐地 / 抬 Z_LIFT）
  swivel_base:                      root = swivel_base ──[base_to_cabinet: CONTINUOUS axis=+Z, origin=(0,0,PEDESTAL_TOP_Z)]──> cabinet(child)

cabinet (由 cabinet_form 决定壳体 mesh：boxy_wood 6-板 / rounded_pod 单曲面 / portable +carry_handle)
  │  (front 朝 +X；screen_tube 决定 crt_screen+screen_bezel 的 mesh：bulged loft / flat loft / porthole lathe+圆 bezel)
  │  (控制柱 vent / dial_escutcheon / grille_slat×12 / nameplate = cabinet 固定 inline visual)
  │
  ├── channel_dial ──[cabinet_to_channel_dial: CONTINUOUS axis=+X, origin=(DIAL_JOINT_X, COL_Y, DIAL_CZ)]
  │       （dial_stem 穿入 front_plate / dial_escutcheon 孔内 captured；off-axis pointer_wedge）
  │
  └── [knob_count multiplicity 轴]  knob_{i}  i∈range(N)
        knob_{i} ──[cabinet_to_knob_{i}: REVOLUTE axis=+X, origin=(KNOB_JOINT_X, knob_y_i, KNOB_ROW_Z), ±135°]
        knob_y_i = COL_Y + (i-(N-1)/2)·KNOB_SPACING （沿控制柱 Y 等距对称）
        （knob_{i}_stem 穿入 front_plate 孔内 captured）
```

接口点位与 joint 语义：
- **base_support 接口（互斥三选一，决定 root）**：
  - tabletop：cabinet bottom_panel 坐地（z=WOOD_T/2），无 joint。
  - splayed_console_legs：cabinet 全体抬 `Z_LIFT=LEG_H·cos(SPLAY_ANGLE)`，4 条 `leg_{i}` 是 cabinet inline visual（top 在 cabinet bottom face、foot 撇向外落地），无 joint。
  - swivel_base：`swivel_base`(root) 上表面 `turntable_ring` ↔ cabinet bottom，`base_to_cabinet` CONTINUOUS axis=(0,0,1)，origin=(0,0,PEDESTAL_TOP_Z)；q=0 正面朝 +X。
- **channel_dial 接口（固定存在）**：cabinet 控制柱上方 `dial_escutcheon` boss ↔ `dial_stem`，`cabinet_to_channel_dial` CONTINUOUS axis=(1,0,0)，origin=(DIAL_JOINT_X, COL_Y, DIAL_CZ)（+Z 视 base_support 是否抬 Z_LIFT 而平移）；`dial_stem` captured 在 `front_plate`/`dial_escutcheon`（allow_overlap + expect_overlap min 0.008）。
- **knob_count 接口（N 次复制）**：每个 `knob_{i}` REVOLUTE axis=(1,0,0)，origin=(KNOB_JOINT_X, knob_y_i, KNOB_ROW_Z)，lower=-KNOB_RANGE/upper=+KNOB_RANGE(±135°)；`knob_{i}_stem` captured 在 `front_plate`（allow_overlap + expect_overlap min 0.008）。沿控制柱 Y 等距对称排布。
- **mating policy**：所有 dial/knob `*_stem` 是 shaft-in-bore captured-pin（轴穿入 front_plate / escutcheon 孔），swivel 是 turntable 面接触 —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（见各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：channel_dial q=0、knobs q=0、swivel q=0（正面朝 +X）；cabinet 落地 / 抬升 / 骑转台。
- **互斥 / 可选 / 派生**：base_support 三候选互斥（一次只一种支撑）；cabinet_form 三候选互斥；screen_tube 三候选互斥。swivel_base 把 root 从 cabinet 切到 swivel_base 并新增一根 spine（其余 cabinet 内部接口不变）。

## 每槽位 Module Emits / Interfaces

### Slot A / cabinet_form — boxy_wood（基线；rounded_pod / portable 仅换壳 mesh / 加 handle）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`（root；visual: 6 块木板 `bottom/top/left/right_side/back_panel` + `front_plate` + 控制柱 vent/escutcheon/grille/nameplate）| f8f3f341 L120-236 |
| internal joints | 无（cabinet 是 root，壳体内无活动件；活动由 dial/knob 提供）| — |
| upstream interface | root（坐地，无父）/ 或 swivel_base 的 child（见 base_support） | f8f3f341 L120-130 |
| downstream interface | front_plate 孔（供 dial/knob stem captured）+ 控制柱 boss（供 dial）| f8f3f341 L152-157, L207-213 |

### Slot A / cabinet_form — rounded_space_age_pod
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`（visual: 单曲面 `pod_shell` mesh 替 6 板 + `front_plate` + 同款控制柱）| 1a475b57 `_build_pod_shell` L118-135 / 装配 L157-169 |
| internal joints | 无 | — |
| upstream interface | root（坐地）；front 开口供 front_plate 嵌入 | 1a475b57 L157-162 |

### Slot A / cabinet_form — portable_with_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`（6 板木壳 + 固定 inline `carry_handle` 拱形 tube 提梁 + 同款控制柱）| cb7ecf95 `carry_handle` L162-187 |
| internal joints | 无（carry_handle 是非移动 visual，Rule 1）| — |
| upstream interface | root（坐地）；top_panel 承提梁 | cb7ecf95 L162-187 |

### Slot B / screen_tube — bulged_crt_glass（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | cabinet 上 `screen_bezel`(矩形 BezelGeometry) + `crt_screen`(LoftGeometry 凸面管) 两 visual | f8f3f341 `_build_crt_glass_mesh` L90-103 / L160-182 |
| internal joints | 无（屏固定在机壳，非移动件）| — |
| upstream interface | 嵌 front_plate 左 2/3，glass 前缘 recessed 在木前缘后 | f8f3f341 L177-182 |

### Slot B / screen_tube — flat_face_crt
| emits | 描述 | 来源 |
|---|---|---|
| parts | `screen_bezel`(矩形) + `crt_screen`(LoftGeometry 近平面 sections) | d3e64ba3 `_build_crt_glass_mesh` L91-108 |
| internal joints | 无 | — |
| upstream interface | 同 bulged（嵌 front_plate 左 2/3，recessed）| d3e64ba3 L164-187 |

### Slot B / screen_tube — porthole_round
| emits | 描述 | 来源 |
|---|---|---|
| parts | `screen_bezel`(圆 BezelGeometry `opening_shape="circle"`) + `crt_screen`(LatheGeometry 圆顶 dome) | fa608269 `_build_porthole_glass_mesh` L71-90 / 圆 bezel L150-165 |
| internal joints | 无 | — |
| upstream interface | 圆窗嵌 front_plate 左 2/3，dome recessed | fa608269 L160-171 |

### Slot C / base_support — tabletop（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无支撑件（cabinet 直接坐地）| f8f3f341 L120-157 |
| internal joints | 无 | — |
| upstream interface | cabinet bottom_panel 中心 z=WOOD_T/2 接触地面 | f8f3f341 L125-130 |

### Slot C / base_support — splayed_console_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | cabinet inline visual `leg_{0..3}`(LatheGeometry 锥腿) + `leg_mount_{0..3}`(安装块)；cabinet 全体抬 `Z_LIFT` | f3c0f936 `_build_console_leg_mesh` L117-128 / L266-296 |
| internal joints | 无（腿是非移动件，Rule 1）| — |
| upstream interface | 4 腿 top 在 cabinet bottom face (z=Z_LIFT)，foot 撇向外落地 | f3c0f936 L273-296 |

### Slot C / base_support — swivel_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | **新 root `swivel_base`**（`pedestal` lathe + `turntable_ring`）；cabinet 降为 child | 397aff58 `_build_swivel_base_mesh` L117-133 / L151-164 |
| internal joints | `base_to_cabinet` CONTINUOUS axis=(0,0,1)，origin=(0,0,PEDESTAL_TOP_Z)，无 limits（无限转）| 397aff58 L385-393 |
| upstream interface | swivel_base root 坐地；`turntable_ring` 面 ↔ cabinet bottom（转台座入）| 397aff58 L159-164, L385-393 |

### channel_dial（固定存在的 CONTINUOUS 旋钮）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `channel_dial`(child；visual `dial_stem`/`dial_ribbed_ring`(KnobGeometry)/`dial_face`/`dial_tick_{0..7}`/`pointer_wedge`) | f8f3f341 L239-284 |
| internal joints | `cabinet_to_channel_dial` CONTINUOUS axis=(1,0,0)，origin=(DIAL_JOINT_X,COL_Y,DIAL_CZ)，无 limits | f8f3f341 L286-294 |
| upstream interface | `dial_stem` captured 在 `front_plate`/`dial_escutcheon`（allow_overlap+expect_overlap min0.008）| f8f3f341 L441-469 |

### knob_count multiplicity（控制旋钮 N 次复制；REVOLUTE moving parts）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knob_{i}`(child)，visual `knob_{i}_stem`(Cylinder)+`knob_{i}_cap`(KnobGeometry，复用同一 knob_mesh) | 4c615bef L300-323 / 1a475b57 L320-335 |
| internal joints | `cabinet_to_knob_{i}` REVOLUTE axis=(1,0,0)，origin=(KNOB_JOINT_X, knob_y_i, KNOB_ROW_Z)，lower=-KNOB_RANGE/upper=+KNOB_RANGE | 4c615bef L325-338 |
| placement | `for i in range(N)`，`knob_y_i = COL_Y + (i-(N-1)/2)·KNOB_SPACING`（沿控制柱 Y 绝对式等距对称）| 4c615bef L59-61, L310 |
| upstream interface | `knob_{i}_stem` captured 在 `front_plate`（allow_overlap+expect_overlap min0.008）| 927cbb3a / 4c615bef run_tests allow_overlap 段 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cabinet_form | enum | boxy_wood / rounded_space_age_pod / portable_with_handle | boxy_wood | choice | sampler 选；决定壳体 mesh helper + 可选 carry_handle visual | module table |
| screen_tube | enum | bulged_crt_glass / flat_face_crt / porthole_round | bulged_crt_glass | choice | sampler 选；决定 crt_screen+screen_bezel mesh / bezel 形状 | module table |
| base_support | enum | tabletop / splayed_console_legs / swivel_base | tabletop | choice | sampler 选；主机构（互斥），swivel_base 切 root + 加 spine | module table |
| knob_count (N) | int | 声明域 [1,8]；sweep 采样域 [1,6]（偏小加权：2/3 高频、4 常见、5/6 长尾、1 稀疏）| 3 | conditional→slot_choice | 编入 slot_choice 为 `("knob_count", f"n{N}")`（拓扑维度）；§8 不等式约束控制柱宽 | 927cbb3a / 4c615bef / 1a475b57 |
| palette_style | enum | wood_grain_classic / walnut_console / space_age_cream / glossy_black / retro_teal | wood_grain_classic | palette | palette only，**不计入 slot_choice**；每 seed 采样一次 | 各样本材质（见下）|
| cabinet_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 CAB_W（控制柱 / 屏 Y 主尺寸），clamp；屏 / 控制柱布局按比例派生 | resolve clamp |
| cabinet_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 CAB_H（机壳高），clamp | resolve clamp |
| screen_size_scale | float | [0.88, 1.10] | 1.0 | equation | `crt_screen`/`screen_bezel` 主尺寸 `= k·cabinet_width_scale`（保屏不超左 2/3 区），不独立采样 | resolve derive |
| dial_diameter_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 DIAL_DIAMETER，clamp（保不撞 vent / knob 行）| resolve clamp |
| knob_range_scale | float | [0.85, 1.05] | 1.0 | independent | 缩放 knob REVOLUTE upper/lower（保 \|range\|≤π·0.95，对称）| resolve clamp |
| knob_spacing_scale | float | [0.85, 1.12] | 1.0 | conditional | 仅 N≥2 有效；缩放控制柱 KNOB_SPACING | resolve clamp |
| leg_height_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 splayed_console_legs 有效；缩放 LEG_H → Z_LIFT，clamp | resolve clamp |
| swivel_pedestal_scale | float | [0.90, 1.15] | 1.0 | conditional | 仅 swivel_base 有效；缩放 BASE_RADIUS/PEDESTAL 高，clamp（保 base 半径 ≥ cabinet 重心稳定）| resolve clamp |
| (—) | constraint | — | — | inequality | 旋钮排布不超控制柱：`(N-1)·KNOB_SPACING·knob_spacing_scale + 2·KNOB_R ≤ column_height − 2·margin`；违反时按比例缩 spacing 或拒绝重采（参考 N=5 样本 KNOB_SPACING=0.035）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 屏不超左 2/3 区：`screen_size_scale·SCREEN_W ≤ (2/3)·CAB_W·cabinet_width_scale − margin`（保不撞控制柱 seam）| 接口 / clearance |
| (—) | constraint | — | — | inequality | dial/knob stem 始终 captured：`stem_len − front_plate_thickness ≥ 0.008`（任意 scale 后 expect_overlap min0.008 仍满足）| 接口 / captured |
| (—) | constraint | — | — | conditional | base_support=splayed_console_legs / swivel_base 时所有 cabinet-local z 与 dial/knob joint origin z 整体平移（Z_LIFT / 转 child 坐标系），不改 cabinet 内部相对布局 | 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度 / 抬升，**绝不改变 cabinet_form / screen_tube / base_support / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（前面板控制旋钮数）：

- **count_param**：`knob_count`（模板内变量 N / KNOB_COUNT；控制柱上小控制旋钮数；基线 3）。
- **N_range**：声明产品域 **[1, 8]**（CRT 电视前面板控制旋钮 1~8 个现实合理；source map 建议 [1,8]）。`config_from_seed` 的 sweep 采样域 **[1, 6]**（偏小加权：N=2/3 高频、N=4 常见、N=5/6 长尾、N=1 稀疏；上限 6 为 sweep 稳态，N=7/8 经 resolve clamp 合法但 sweep 稀采）。N=1 即单旋钮退化（仍走 range(1) 循环）。
- **sampling domain**：`config_from_seed` 用 `rng.choices(range(1,7), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,8]。
- **copied object**：单只控制旋钮单元——`knob_{i}` part（visual `knob_{i}_stem` Cylinder + `knob_{i}_cap` KnobGeometry）+ `cabinet_to_knob_{i}` REVOLUTE joint；N 个 cap 复用同一 `knob_mesh` 几何对象（`mesh_from_geometry(knob_geom, "small_control_knob")` 发一次，循环内复用）。
- **naming**：`knob_{i}` part / `knob_{i}_stem` / `knob_{i}_cap` visual / `cabinet_to_knob_{i}` joint，`for i in range(N)`（4c615bef L310 `for i, knob_y in enumerate(KNOB_YS)` / 927cbb3a L310 `for i in range(KNOB_COUNT)` 已用此结构，直接作 copy-logic 源）。
- **placement**：沿控制柱 **Y 绝对式**等距对称——`knob_y_i = COL_Y + (i-(N-1)/2)·KNOB_SPACING`（4c615bef L59-61）。绝对式（每个 i 的 y 由 N 与柱中心解析、不累加漂移）是 N-不变前提。X=KNOB_JOINT_X、Z=KNOB_ROW_Z 对所有 i 相同（在控制柱 dial 下方一排）。
- **joint policy**：每个 `knob_{i}` 是**独立活动件**，各发一个 `cabinet_to_knob_{i}` REVOLUTE axis=(1,0,0)，lower=-KNOB_RANGE/upper=+KNOB_RANGE（±135°）；`knob_{i}_stem` captured 在 front_plate。
- **source/gating**：copy-logic 源取 4c615bef L300-338（N=5，`enumerate(KNOB_YS)`）与 927cbb3a L310-338（N=2，`range(KNOB_COUNT)`），pod 变体 1a475b57 L320-349（N=3）作中段参照；**N=1 等价 range(1)**。N 与控制柱高的兼容见 §7 第一条不等式（旋钮排布不超柱）。
- **另：`grille_slat`**：cabinet 喇叭格栅是固定 **12 片**循环 visual（`for index in range(12)`，无 joint），**不暴露为模板 multiplicity 轴**（无结构变化样本，照搬常数 12 作 cabinet inline 装饰，Rule 1）。

## 拓扑多样性审计

总组合数：cabinet_form(3) × screen_tube(3) × base_support(3) × knob_count 采样数(6，即 {1..6}) = **162**。

仅 base_support(3) × knob_count(6) = **18** 已含真正的 joint 拓扑差异（tabletop/legs 无新 joint vs swivel_base 多一根 CONTINUOUS +Z spine + root 切换 × N 个 REVOLUTE 旋钮）≥10 已过；叠 cabinet_form(3) × screen_tube(3) → 162 充裕。

理由：base_support 提供真正的 part-tree / root / joint 拓扑差异（cabinet-root 坐地 / cabinet-root 抬腿 / swivel-root + base_to_cabinet CONTINUOUS +Z），叠 knob_count（N 个 REVOLUTE 旋钮，N 改 part / joint 计数）即 ≥18 种 joint-topology 类；再叠 cabinet_form / screen_tube 的 mesh 维度共 162 distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("knob_count", f"n{N}")`，对齐 cushion/shopping_bucket/fence_cascade），否则不同旋钮数在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（cabinet_form / screen_tube / base_support），经兼容矩阵合法化，再 `rng.choices` 加权 N∈[1,6]，再 uniform 各连续 scale，最后采 palette_style。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 cabinet_width_scale / cabinet_height_scale / screen_size_scale(equation@cabinet_width) / dial_diameter_scale / knob_range_scale / knob_spacing_scale(conditional@N≥2) / leg_height_scale(conditional@console_legs) / swivel_pedestal_scale(conditional@swivel_base)。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：knob_spacing 仅 N≥2、leg_height 仅 legs、swivel_pedestal 仅 swivel）→ 采 independent cabinet_width/height/dial/knob_range scale → 派生 screen_size = k·cabinet_width → 用三条 inequality（旋钮不超柱、屏不超左 2/3、stem 保 captured）投影 / 回缩。跨部件依赖（旋钮排布 vs 柱高、屏 vs 机壳宽、stem vs front_plate 厚）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 dial/knob/swivel joint origin、captured-pin 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），再 `rng.choices` 加权 N∈[1,6]，再 uniform 各 scale，再 `rng.choice` palette_style | slot_choices_for_seed 含 `("knob_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **base_support 与 cabinet_form / screen_tube 正交**（任意机壳 / 屏管均可配 tabletop / legs / swivel）。 (2) **swivel_base × N**：转台不影响旋钮数，允许全 N。 (3) **N>柱容**：N 受 §7 第一条不等式约束——若 (N-1)·spacing 超控制柱高，先缩 knob_spacing_scale，仍超则拒绝重采（sweep 域上限 6 已留余量）。 (4) **portable_with_handle × swivel_base**：提梁顶部不撞转台（提梁在 cabinet top、转台在 cabinet bottom）→ 允许。 (5) **splayed_console_legs × swivel_base 互斥**（同为 base_support 槽、二选一，不可同时抬腿又上转台）。 | 无 floating / collision / 旋钮超柱 / 屏撞控制柱 / stem 脱出 / swivel root 错位 / leg 不落地 |
| controlled local variation | 8 个 clamped scale（cabinet_width/height、screen_size(派生)、dial_diameter、knob_range、knob_spacing@N≥2、leg_height@legs、swivel_pedestal@swivel），每 build 统一；后三个 + knob_spacing 为 conditional | 比例变化不破坏 dial/knob/swivel joint origin、captured stem、屏布局、坐地 / 抬升、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（swivel +Z / dial +X / knob +X captured）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| cabinet_form | 3 | yes | yes | boxy_wood(parent) / rounded_pod / portable(fork)；壳 mesh 维度 |
| screen_tube | 3 | yes | yes | bulged / flat / porthole（屏 mesh + bezel 形状维度）|
| base_support | 3 | yes | yes | 无 joint 坐地 / 无 joint 抬腿 / swivel CONTINUOUS +Z（互斥主机构，真拓扑）|
| knob_count (N) | 6（采样域 {1..6}，2/3 高频 / 5/6 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("knob_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,6]，clamp 域 [1,8]
- `resolve_config` 把 knob_count clamp 到 [1,8]，各 scale clamp 到声明范围；screen_size 派生自 cabinet_width；knob_spacing / leg_height / swivel_pedestal 为 conditional 随 N / base_support 解析；三条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（base_support 三选一互斥；N 超柱降级 spacing 或拒采；stem 保 captured）
- 连续 scale clamp 后不破坏 dial/knob/swivel joint origin / captured stem / 屏布局 / 坐地或抬升 / N 复制
- 关键 joint：`cabinet_to_channel_dial` CONTINUOUS axis≈(1,0,0) 无 limits；`cabinet_to_knob_{i}` REVOLUTE axis≈(1,0,0) lower≈-KNOB_RANGE/upper≈+KNOB_RANGE；swivel_base 时 `base_to_cabinet` CONTINUOUS axis≈(0,0,1) origin z≈PEDESTAL_TOP_Z，且 swivel_base 为唯一 root
- captured-pin：element-scoped `allow_overlap`（`dial_stem`↔`front_plate`/`dial_escutcheon`；`knob_{i}_stem`↔`front_plate`），照搬各样本 run_tests 的 allow_overlap 段 + expect_overlap min0.008 retained-insertion（含 spun/turned pose 下仍 captured）
- copied object 遵循 `knob_{i}` 命名 + 沿控制柱 Y 绝对式等距 placement + 独立 REVOLUTE joint
- grandfather：所有 dial/knob captured stem + swivel turntable 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- off-axis `pointer_wedge` 存在于 channel_dial（证明 CONTINUOUS 转动，off-axis 距 >0.012）

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 不同旋钮数 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- swivel_base 时未把 root 切换为 `swivel_base`、或 cabinet 仍是 root / 无 `base_to_cabinet` joint → 转台不成立（样本 root_parts()[0]=="swivel_base"）。
- swivel `base_to_cabinet` 设成 REVOLUTE 有限角或非 +Z 轴 → 转台应 CONTINUOUS axis=(0,0,1) 无 limits（样本 L385-393）。
- channel_dial 设成 REVOLUTE 有限角 / 漏 off-axis pointer_wedge → 选台旋钮应 CONTINUOUS 无限转 + 带 pointer 证明（样本 L286-294, L279-284）。
- 把 dial/knob `*_stem` 当独立漂浮件不 captured / 漏 allow_overlap → mating-gap 或 retained-insertion FAIL；应 captured + allow_overlap + expect_overlap min0.008。
- 把 console legs / carry_handle 当独立活动 part 加 joint → 违反 Rule 1（腿 / 提梁非移动件，应 inline 为 cabinet visual）。
- splayed_console_legs 时漏整体 Z_LIFT 抬升 → cabinet 与腿穿模 / 浮空；须全 cabinet-local z + dial/knob joint origin z 同步抬 Z_LIFT。
- knob_spacing 过大致旋钮排出控制柱 → §7 第一条不等式 FAIL；须按比例缩 spacing 或拒采。
- screen_size 独立放大超左 2/3 区撞控制柱 seam → 应派生自 cabinet_width 并受 §7 第二条不等式约束。
- 把连续尺寸 / 颜色 / 材质（palette_style / 各 scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"平板挂墙 TV / 桌面显示器"语义混入（无 CRT 玻璃管 / 无旋钮 / 有独立 tilt 颈）→ 出类，本类是 CRT 机壳电视。

## 与相邻类别的边界

- 不该混入：**平板挂墙电视 / 现代 LCD/OLED TV**——薄板无机壳深度、无 CRT 玻璃管 / 选台旋钮 / 木壳，主身份完全不同（本类核心是凸/平/圆 CRT 管 + 旋钮控制柱）。
- 不该混入：**桌面显示器（desktop monitor）**——有独立 stand-neck 的 tilt/swivel 颈柱、屏可绕颈倾仰；本类无颈、屏固定机壳里，活动件是旋钮，swivel 是整机转台而非屏倾仰（见 `desktop_monitor_with_tilt_swivel_stand` 为不同 slug）。
- 不该混入：**收音机 / 台式音响（radio / hi-fi）**——同有旋钮 + 喇叭格栅，但缺 CRT 屏 bezel + 玻璃管这套电视身份；如需可作单独 slug。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) cabinet_form / screen_tube 建模为 mesh-helper 维度（非串联 slot，不增删活动件）；(2) base_support 为唯一真拓扑槽，swivel_base 切 root + 加 CONTINUOUS +Z spine 是否符合 multiplicity/拓扑审计期望；(3) knob_count N_range 声明 [1,8] / sweep 采样 [1,6] 是否接受（实样仅 N∈{2,3,5}，1/4/6/7/8 为外推，靠 range(N) + 绝对式 placement + §7 不等式保证）；(4) 旋钮沿 **Y**（非 source map 所写 Z）等距，已按实样修正；(5) grille_slat 固定 12 片不暴露为 multiplicity 是否认可；(6) splayed_console_legs × swivel_base 互斥（同槽二选一）是否需额外说明）|

## 模板实现备注（可选）

- 共享 helper：`_rounded_rect_outline`（屏 / bezel 通用 outline，所有样本都有）、`_build_crt_glass_mesh`（bulged / flat 共用，仅 sections_spec 数值切换）、`_build_porthole_glass_mesh`（porthole lathe）、`_build_pod_shell`（rounded_pod cadquery）、`_build_console_leg_mesh`（legs lathe）、`_build_swivel_base_mesh`（swivel pedestal lathe）、KnobGeometry（dial + knob 共用 knob_mesh，N 复制复用同一对象）。
- captured 接口 allow_overlap：`run_tv_tests` 里逐机构补 element-scoped `allow_overlap`（`dial_stem`↔`front_plate`/`dial_escutcheon`、`knob_{i}_stem`↔`front_plate`），照搬各样本 run_tests 段（parent L441-486、含 spun dial / turned knob pose 下 expect_overlap）。
- base_support root 切换：tabletop / legs → root=cabinet（legs 抬 Z_LIFT、dial/knob joint origin z 同步抬）；swivel_base → 先建 swivel_base(root) 再建 cabinet(child) + `base_to_cabinet` CONTINUOUS +Z；dial/knob joint origin 在 cabinet 子坐标系内，不受 swivel 平移（child 局部坐标）。
- conditional 范围解析顺序：先采 cabinet_form / screen_tube / base_support / N → 解析 knob_spacing(仅 N≥2) / leg_height(仅 legs) / swivel_pedestal(仅 swivel) / Z_LIFT(legs) → 采 cabinet_width/height/dial/knob_range independent scale → 派生 screen_size = k·cabinet_width → 投影三条 clearance inequality。
- N=1 退化：直接 `for i in range(1)` 发单 `knob_0`（等价旧具名单旋钮）；N≥2 走 `for i, knob_y in enumerate(KNOB_YS)`。
- 参考模板：`agent/templates/Bag_Suitcase_Shopping_bucket.py` 与已审 spec `Accessories_Cushion.md`（同为 mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap 骨架，本类可同构改编）；base_support 的 root 切换可参考有 base/turntable root 的转台模板（如 `parabolic_dish_on_azimuth_elevation_mount` 的 azimuth root spine 思路）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / dial / N（parent 基线）| boxy_wood + bulged_crt + tabletop + 3 knob | rec_model-…f8f3f341 | 6 板木壳 L120-157 / `_build_crt_glass_mesh` L90-103 / bezel+screen L160-182 / 控制柱 L185-236 / `channel_dial`+CONTINUOUS L239-294 / 3 knob REVOLUTE L296-333 / allow_overlap L441-486 | 基线机壳 + 凸面 CRT + 坐地 + dial/knob captured 范式 |
| S2 | A | rounded_space_age_pod | rec_variant-…1a475b57 | `_build_pod_shell` L118-135 / 装配 L157-169 / `knob_{i}` 循环 L320-349 | 圆角太空舱壳 mesh（已 knob_{i} 化）|
| S3 | A | portable_with_handle | rec_variant-…cb7ecf95 | `carry_handle`(tube_from_spline_points) L162-187 | 便携提梁（固定 inline visual）|
| S4 | B | flat_face_crt | rec_variant-…d3e64ba3 | `_build_crt_glass_mesh` 近平面 sections L91-108 | 平面直角 CRT 玻璃（sections 数值变）|
| S5 | B | porthole_round | rec_variant-…fa608269 | `_build_porthole_glass_mesh`(Lathe) L71-90 / 圆 bezel L150-165 | 圆窗 porthole CRT（lathe dome + 圆 bezel）|
| S6 | C | splayed_console_legs | rec_variant-…f3c0f936 | `_build_console_leg_mesh` L117-128 / `leg_{i}`+`leg_mount_{i}` L266-296 / Z_LIFT L53 | 四撇 console 腿（固定 inline + Z_LIFT 抬升，无 joint）|
| S7 | C | swivel_base | rec_variant-…397aff58 | `_build_swivel_base_mesh` L117-133 / `swivel_base` root L151-164 / `base_to_cabinet` CONTINUOUS +Z L385-393 | 旋转底座（新 root + CONTINUOUS +Z 转台 spine）|
| S8 | D（multiplicity）| knob_count N=2 | rec_variant-…927cbb3a | `KNOB_COUNT=2` L57 / `for i in range(KNOB_COUNT)` `knob_{i}` L310-338 | N=2 copy-logic 源（range 循环 + 对称 Y 排）|
| S9 | D（multiplicity）| knob_count N=5 | rec_variant-…4c615bef | `KNOB_COUNT=5`/`KNOB_SPACING` L57-61 / `for i, knob_y in enumerate(KNOB_YS)` L310-338 | N=5 copy-logic 源（绝对式等距 Y placement）|
