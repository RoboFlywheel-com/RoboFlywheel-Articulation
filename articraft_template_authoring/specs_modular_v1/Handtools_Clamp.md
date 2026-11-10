# clamp (screw-driven hand clamp: C-clamp / G-clamp) — Modular Spec

> 来源小类：`picture/Handtools/Clamp`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Clamp.md`。
> **"Clamp" 在此 = 螺旋驱动手用夹具（screw-driven hand clamp，C 形 / G 形夹），不是 binder clip / 文具夹（已有独立 slug `clip`）、也不是台钳 vise 或钳子 pliers。**
> 结构家族 = 螺旋夹：一只 C 形 `frame`（root，下颚带固定 anvil，上臂带螺纹 boss）+ 一只 `screw` 螺杆（沿 boss 竖直 PRISMATIC 进给）+ 顶端用户把手 + 杆尖压脚（可选 swivel REVOLUTE）。
>
> **同步状态**：本 spec 引用的 6 个 5 星样本（2 个 parent + 4 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对）。引用以 part / joint / helper **名字** 为准（`frame`/`screw`/`pad`/`lever` part；`frame_to_screw`/`screw_to_pad`/`frame_to_lever` joint；`_build_frame_mesh`/`_frame_solid`/`_build_pad_mesh`/`_pad_solid`/`_build_pressing_disc_mesh`/`_build_lever_*`/`wing_{i}` 等），行号仅作定位。
>
> **坐标约定差异（重要，模板必须统一）**：两个 parent 家族用了不同的世界轴：
> - **A 家族**（e34de725 parent A + anvilfoot + leverhandle + winghandle）：screw 轴 = **+Z**，C 口朝 **−Y**，把手沿 **X**，screw part 原点 = 杆底尖，PRISMATIC axis=(0,0,−1)（正 q 向下夹），swivel pad REVOLUTE 绕 **Y**。
> - **B 家族**（1a4c37c7 parent B + frame 变体）：screw 轴 = **+Z**，C 口朝 **+X**，T-bar 沿 **Y**，screw part 原点 = boss 中心，PRISMATIC axis=(0,0,+1)（负 q 向下夹），pad **固定**无 joint。
> 两家族共享同一运动 spine（frame root → PRISMATIC screw → 可选 REVOLUTE pad），只是把手朝向 / 喉口朝向 / screw 原点参考点不同。**模板侧统一到 A 家族约定**（screw 轴 +Z、C 口 −Y、把手沿 X、screw 原点 = 杆底尖、PRISMATIC axis=(0,0,−1)、swivel 绕 Y），把 B 家族的 tbar_balls / boxy_deep 模块按此约定 rebase（见 §13）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `clamp` |
| template path | `agent/templates/Handtools_Clamp.py` |
| test path (optional) | `tests/agent/test_clamp_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `frame` + 三个并行替换层：foot/pad、handle、frame_silhouette；handle=side_lever 时 screw 与 lever 并列挂 frame）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（2 parent + 4 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 6（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 6/6 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 6 个样本）**：`frame`（root，C 形 body + 固定 anvil/fixed-jaw + 螺纹 boss + 螺杆 bore）+ `screw`（螺杆 spindle，PRISMATIC 沿竖直轴进给）。`frame_to_screw` PRISMATIC 是**所有候选共享的主夹紧运动**。spindle 螺纹与 boss bore 是 captured screw-in-boss 过盈（`allow_overlap(screw_core/spindle, frame_body)` + `expect_contact`，见 A L392-405 / B L456-462）。
- **Slot A foot/pad 轴**：是 part 数 / joint 拓扑变化。
  - swivel_ball_pad（parent A）：`pad` 是**独立 part**，`screw_to_pad` **REVOLUTE 绕 Y**（A L340-350），可倾贴斜面 → +1 part +1 joint。
  - fixed_flat_pad（parent B）：`swivel_pad` 是 `screw` 的 **visual**（B L297-301），**无独立 joint**（pad 固定随 screw 平移）。
  - anvil_disc（anvilfoot）：`pressing_disc` 是 `screw` 的 **visual**（anvilfoot L312），宽平压盘代替 ball，**无独立 joint**；run_tests 显式断言 `"screw_to_pad" not in articulations` 且 part 无 `pad`（anvilfoot L364-374, L406-411）。
- **Slot B handle 轴**：是 part 数 / joint 拓扑变化。
  - tbar_caps（parent A）：`handle_bar` + `handle_caps`（`for sign in (-1,1)` 对称端帽）作 `screw` visual（A L303-304），无 joint。
  - tbar_balls（parent B）：`tbar` + `ball_pos`/`ball_neg`（手写两份球端）作 `screw` visual（B L280-296），无 joint。
  - side_lever（leverhandle）：`lever` 是**独立 part**，`frame_to_lever` **REVOLUTE 绕 Z**（leverhandle L355-363），screw 为 mimic follower PRISMATIC；lever 含 hub+arm+grip+`grip_ridge_{i}` 5 根 ridge 循环（leverhandle L322-326）→ +1 part +1 joint（screw 与 lever 并列挂 frame）。
  - butterfly_wing（winghandle）：`hub` + `wing_{i}`（`for i,sign in enumerate((-1,1))` 两片扁平 Box 翼）作 `screw` visual（winghandle L261-268），无 joint。
- **Slot C frame_silhouette 轴**：是 mesh-profile 形态变化（不改 part/joint 拓扑）。
  - rounded_C（parent A/B）：A 用三段 filleted box union（`_build_frame_mesh` A L101-166）；B 用 XZ 闭合 polyline C-profile extrude + `fillet(0.006)`（`_frame_solid` B L102-172）。圆角喉口。
  - boxy_deep（frame 变体）：同 B 的 polyline C-profile，但更深更方（`back_x=-0.088`、`THROAT_DEPTH=0.120`、`BOSS_CENTER_Z=0.145`、`fillet(0.002)` 几乎不倒角）（frame L104-177）；run_tests 断言 frame height>0.160、x_span>0.130（frame L484-501）。

## 核心身份

一只**螺旋驱动手用夹具**（screw-driven hand clamp，C 形 / G 形夹）：一只铸铁 / 钢 **C 形 frame**（root，坐地于喉口背脊；下颚（fixed jaw）端有固定 **anvil 压垫**，上臂有螺纹 **boss**），一只 **screw 螺杆**（带螺纹 spindle）沿 boss 竖直 **PRISMATIC** 进给入喉口夹紧工件，杆顶有用户**把手**（T-bar 端帽 / T-bar 球端 / 单侧 lever / 蝶形 wing），杆尖有**压脚**（可 swivel 倾摆的 ball pad / 固定平 pad / 宽平 anvil 压盘）。默认成熟域：foot(3) × handle(4) × frame_silhouette(2) 笛卡尔积的小型手持螺旋夹。活动语义 = **螺杆沿竖直轴进给夹紧**（核心 PRISMATIC，全候选共享）+ 可选 **swivel pad REVOLUTE**（绕 Y 倾贴）+ side_lever 时的 **lever REVOLUTE**（绕 Z 摆动驱动）。

不该混入：
- **binder clip / 文具弹簧夹 / 鳄鱼夹（clip）**——靠弹簧 / 杠杆张力夹纸 / 线，无螺杆进给、无 C 形铸铁 frame；已有独立 slug `clip`。
- **台钳 / 桌虎钳（bench vise）**——固定在工作台上、双滑块平行颚、丝杆驱动滑块横移；本类是手持 C 形单螺杆夹，frame 是 C 形不是箱形导轨座。
- **钳子 / 老虎钳（pliers）**——双臂绕中心 pivot 剪切 / 夹持，无螺杆、无 C frame、无 anvil。
- **快速夹 / F 形夹（bar clamp / quick clamp）的滑动横梁**——本类 frame 是固定深度 C 喉，不是可沿长杆滑动的横梁滑块（若需可作单独 slug）。

## 槽位 + 候选模块表

> **建模注记**：`frame_silhouette`（Slot C）是 `frame` part **同一 C 形 body 的 mesh 足迹形态**（圆角浅喉 / 方深喉），由 frame mesh helper 一次决定，**不改 part 树 / joint 拓扑**；列为候选轴以对齐 schema，与 foot × handle 笛卡尔积共同撑开多样性（见 §9）。`foot/pad`（Slot A）与 `handle`（Slot B）才是改 part 数 / joint 拓扑的轴（swivel pad +REVOLUTE / side_lever +REVOLUTE）。

### Slot A：foot / pad（杆尖压脚 —— 决定 screw 尖端 part 树与是否多一个 swivel joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| swivel_ball_pad（基线）| rec_build-...-clam_...e34de725（parent A）| `pad` part L307-308 + `_build_pad_mesh`（neck+disc）L256-277 + `screw_to_pad` **REVOLUTE** axis=(0,1,0) L340-350 | eligible if compatible | 球窝 swivel 压脚：`pad` **独立 part**（neck 捕入杆尖 + 平面朝下的圆 disc），绕 **Y REVOLUTE** 倾摆贴斜面（lower=−0.30 / upper=0.30）；**+1 part +1 joint** |
| fixed_flat_pad | rec_build-...-clam_...1a4c37c7（parent B）| `swivel_pad` visual L297-301 + `_pad_solid`（disc+neck）L219-237；**无 screw_to_pad joint** | eligible if compatible | 圆平压脚刚性固定在杆尖：`swivel_pad` 是 `screw` 的 **visual**（neck 捕入 spindle 尖，`allow_overlap(swivel_pad, spindle)` B L470-476），随 screw 平移，**无独立 part / joint** |
| anvil_disc | rec_clamp_var_anvilfoot | `pressing_disc` visual L312 + `_build_pressing_disc_mesh`（hub+宽 disc）L261-283；**无 joint** | eligible if compatible | 宽平 anvil 压盘（DISC_R=0.024，直径 ~48mm，远宽于 ball pad）刚性固定杆尖：`pressing_disc` 作 `screw` visual，run_tests 断言无 `screw_to_pad`、无 `pad` part、disc 宽且扁（anvilfoot L466-475）；**无独立 part / joint** |

### Slot B：handle / drive grip（杆顶用户把手 —— 决定把手 part 树与是否多一个 lever joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| tbar_caps（基线）| rec_build-...-clam_...e34de725（parent A）| `handle_hub` L302 + `handle_bar`（YZ 圆杆沿 X，`_build_handle_bar_mesh` L228-236）L303 + `handle_caps`（`for sign in (-1,1)` 圆角端帽，`_build_handle_caps_mesh` L239-253）L304 | eligible if compatible | 细 T 横杆 + 两小端帽，作 `screw` visual（无 joint）；横杆沿 X、宽 >0.08、坐 boss 上方（A run_tests L431-444）|
| tbar_balls | rec_build-...-clam_...1a4c37c7（parent B）| `tbar`（XZ 圆杆沿 Y，`_tbar_solid` L240-249）L280-284 + `ball_pos`/`ball_neg`（手写两 `Sphere`）L285-296 | eligible if compatible | T 横杆 + 两大球端（tommy bar），作 `screw` visual（无 joint）；球端跨 spindle 沿 Y（B run_tests L384-393，`allow_overlap(ball_*,tbar)` L477-490）。**rebase 注记**：源在 Y 轴，模板侧改沿 X 对齐 A 约定；两球折成 `for sign in (-1,1)` 循环（源是手写两份）|
| side_lever | rec_clamp_var_leverhandle | `lever` part L308-326（hub L310 + arm L314 + grip L318 + `grip_ridge_{i}` `for i in range(5)` L322-326）+ `frame_to_lever` **REVOLUTE** axis=(0,0,1) L355-363；screw 为 mimic follower PRISMATIC L377-387 | eligible if compatible | 单侧摆动 lever：`lever` **独立 part**（绕 **Z REVOLUTE** 在 boss 顶 hub 摆动，lower=0/upper=1.5），驱动 screw 进给（mimic）；含 5 根 grip ridge 循环；`allow_overlap(screw_core, lever_hub)`（leverhandle L537-543）；**+1 part +1 joint**（screw 与 lever 并列挂 frame）|
| butterfly_wing | rec_clamp_var_winghandle | `handle_hub` L258 + `wing_{i}`（`for i,sign in enumerate((-1,1))` 两扁平 `Box` 翼）L261-268 | eligible if compatible | 蝶形 / 翼形拧柄：hub + 两片扁平拇指翼（thin in Z、wide），作 `screw` visual（无 joint）；翼 X 跨 >0.06、坐 boss 上方（winghandle run_tests L396-423）|

### Slot C：frame_silhouette（C 形 frame 足迹 —— mesh-profile 维度，不改拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_C（基线）| rec_build-...-clam_...e34de725（A）/ ..._1a4c37c7（B）| A `_build_frame_mesh` 三段 box union + `edges("|X").fillet(0.006)` L101-166；B `_frame_solid` XZ polyline C-profile extrude + `fillet(0.006)` L102-172 | eligible if compatible | 经典圆角浅喉 C/G frame（喉深 ~0.06-0.09，圆倒角 0.006）；`frame` body + 固定 anvil/jaw + boss + bore |
| boxy_deep | rec_clamp_var_frame | `_frame_solid` 同 B 的 polyline 但更深更方：`back_x=-0.088`/`THROAT_DEPTH=0.120`/`BOSS_CENTER_Z=0.145`/`fillet(0.002)`（几乎不倒角，方角）L104-177；run_tests 断言 height>0.160、x_span>0.130（L484-501）| eligible if compatible | 深喉方角 C frame（喉更深、reach 更长、右直角不倒角）；part/joint 与 rounded_C 一致，仅 mesh-profile 重写 |

> 降级理由（Slot C 仅 2 candidate）：fork 池 frame 形态只有 parent 的圆角浅喉 + frame 变体的方深喉两个真实收敛形态；现实螺旋夹 frame 形态词汇表本身窄（圆角 C / 方深喉为主）。审核如需扩容应回 fork 池补造（如 deep-throat C-clamp 加长杆、box-section 焊接 C），不在模板侧虚构。Slot A(3) × Slot B(4) 已提供主拓扑多样性，Slot C ×2 充裕（见 §9）。

## 槽位图（slot graph）

pattern: parallel_children（固定 root `frame`；`screw` PRISMATIC 挂 frame；foot/pad 与 handle 各自的活动件按候选挂 screw 或并列挂 frame；frame_silhouette 只换 frame mesh）

```
frame (root, 坐地; 由 frame_silhouette 决定 C body mesh + 固定 anvil/jaw + 螺纹 boss + bore)
  │
  ├── screw ──[frame_to_screw: PRISMATIC axis≈(0,0,−1), origin=杆底尖 rest_tip_z]   ← 全候选共享主夹紧运动
  │     │   （spindle 螺纹 captured 进 boss bore：allow_overlap(screw_core/spindle, frame_body) + expect_contact）
  │     │
  │     ├── [foot/pad slot]  (三选一)
  │     │     ├─ swivel_ball_pad : pad(独立 part) ──[screw_to_pad: REVOLUTE axis=(0,1,0), origin=(0,0,−PAD_NECK_H) 杆尖下]
  │     │     ├─ fixed_flat_pad  : swivel_pad = screw visual (无 joint，捕入杆尖)
  │     │     └─ anvil_disc      : pressing_disc = screw visual (无 joint，宽平盘)
  │     │
  │     └── [handle slot 的非 lever 候选挂 screw visual]  (tbar_caps / tbar_balls / butterfly_wing)
  │           ├─ tbar_caps     : handle_hub + handle_bar + handle_caps{±} (screw visual, 无 joint)
  │           ├─ tbar_balls    : tbar + ball{±} (screw visual, 无 joint)
  │           └─ butterfly_wing: handle_hub + wing_{i} i∈range(2) (screw visual, 无 joint)
  │
  └── [handle slot 的 side_lever 候选并列挂 frame]
        └─ side_lever : lever(独立 part) ──[frame_to_lever: REVOLUTE axis=(0,0,1), origin=(0,0,boss_top+HUB/2)]
              （screw 仍是 frame 的 PRISMATIC child，lever 是 mimic 驱动；allow_overlap(screw_core, lever_hub)）
              lever 含 lever_hub + lever_arm + lever_grip + grip_ridge_{i} i∈range(5)
```

接口点位与 joint 语义：
- **frame → screw（全候选共享）**：mating = boss bore。PRISMATIC axis≈(0,0,−1)（A 约定，正 q 向下夹），origin=(0, ANVIL_Y, rest_tip_z)（A L330）；rest 时 spindle 螺纹穿过 boss、杆尖悬在 anvil 上方 OPEN_GAP≈0.030（开口姿态）。captured screw-in-boss 过盈 → `allow_overlap(screw_core, frame_body)` + `expect_contact`（A L392-405）。motion_limits lower=0 / upper≈0.028（夹到 anvil 前止）。
- **screw → pad（foot=swivel_ball_pad 时）**：mating = 杆尖球窝。REVOLUTE axis=(0,1,0)，origin=(0,0,−PAD_NECK_H)（杆尖下 swivel center，A L347），lower=−0.30/upper=0.30；`pad` neck 捕入杆尖。foot=fixed_flat_pad / anvil_disc 时**无此 joint**（pad/disc 是 screw visual，captured `allow_overlap(pad_elem, spindle)`）。
- **frame → lever（handle=side_lever 时）**：mating = boss 顶 hub。REVOLUTE axis=(0,0,1)，origin=(0, ANVIL_Y, boss_top_z+LEVER_HUB_H/2)（leverhandle L360），lower=0/upper=1.5；lever 摆动 mimic 驱动 screw 下行；`allow_overlap(screw_core, lever_hub)`（screw 穿 hub bore，leverhandle L537-543）。handle 其余候选**无此 joint**（hub/bar/wing 是 screw visual）。
- **handle 非 lever 候选 → screw**：handle_bar/caps、tbar/balls、hub/wing 作 `screw` visual，captured 过盈 `allow_overlap`（tbar↔spindle、ball↔tbar、wing root↔hub）。
- **mating policy**：所有 captured 接口（screw-in-boss、pad-neck-in-tip、tbar-cross-hole、ball-on-bar、wing-root-in-hub、screw-in-lever-hub）是 captured-fit（销 / 杆 / 颈嵌入孔），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：screw q=0（喉口开，杆尖悬 anvil 上方）；swivel pad q=0（不倾）；side_lever q=0（arm 沿 +X 静止）。
- **互斥 / 可选 / 派生**：foot 三候选互斥；handle 四候选互斥；swivel_ball_pad 独有 `screw_to_pad` REVOLUTE，其余 foot 无；side_lever 独有 `frame_to_lever` REVOLUTE 且 lever 并列挂 frame，其余 handle 挂 screw visual。frame_silhouette 与 foot/handle 正交（任意组合都合法，仅尺寸联动，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot C / frame_silhouette（以 rounded_C 为例；boxy_deep 仅换 mesh profile + 尺寸）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root，visual：`frame_body` C 形 body + 固定 `anvil_pad`（A 家族）/ fixed jaw nose（B 家族）+ 螺纹 boss + bore）| A `_build_frame_mesh`+`_build_anvil_mesh` L101-177 / B `_frame_solid` L102-172 / boxy_deep L104-177 |
| internal joints | 无（frame 是 root）| — |
| upstream interface | root（坐地，无父）| — |
| downstream interface | boss bore（供 screw PRISMATIC 接入）+ boss 顶（供 side_lever REVOLUTE hub）+ 下颚 anvil（夹紧对位面）| A L146-166 / leverhandle L351 |

### Slot A / foot — swivel_ball_pad
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pad`（visual：`swivel_pad` = neck + 平面朝下圆 disc）| A `pad` L307-308 / `_build_pad_mesh` L256-277 |
| internal joints | `screw_to_pad` REVOLUTE axis=(0,1,0)，origin=(0,0,−PAD_NECK_H)，lower=−0.30/upper=0.30 | A L340-350 |
| upstream interface | pad neck 捕入 screw 杆尖（captured，`expect_origin_distance(screw,pad,xy,max=0.006)`）| A L522-528 |

### Slot A / foot — fixed_flat_pad
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`swivel_pad` 为 `screw` visual）| B `_pad_solid` L219-237 / L297-301 |
| internal joints | 无 | — |
| upstream interface | pad neck 捕入 spindle 尖（`allow_overlap(swivel_pad, spindle)`）| B L470-476 |

### Slot A / foot — anvil_disc
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`pressing_disc` 为 `screw` visual，宽平盘 + 小 hub）| anvilfoot `_build_pressing_disc_mesh` L261-283 / L312 |
| internal joints | 无（run_tests 断言无 `screw_to_pad`、无 `pad` part）| anvilfoot L364-374, L406-411 |
| upstream interface | disc hub 捕入 spindle 尖（与 fixed_flat_pad 同 captured 范式）| anvilfoot L312 |

### Slot B / handle — tbar_caps
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_hub` + `handle_bar` + `handle_caps` 为 `screw` visual）| A L302-304 |
| internal joints | 无 | — |
| upstream interface | hub/bar 坐 spindle 顶（captured，bar 沿 X）| A `_build_handle_bar_mesh` L228-236 |

### Slot B / handle — tbar_balls
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`tbar` + `ball_pos`/`ball_neg` 为 `screw` visual）| B L280-296 |
| internal joints | 无 | — |
| upstream interface | tbar 穿 spindle cross-hole（`allow_overlap(tbar,spindle)`）+ ball 坐 bar 端（`allow_overlap(ball_*,tbar)`）| B L463-490 |

### Slot B / handle — side_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever`（visual：`lever_hub` + `lever_arm` + `lever_grip` + `grip_ridge_{i}`×5）| leverhandle L308-326 |
| internal joints | `frame_to_lever` REVOLUTE axis=(0,0,1)，origin=(0,ANVIL_Y,boss_top+HUB/2)，lower=0/upper=1.5 | leverhandle L355-363 |
| upstream interface | lever hub 坐 boss 顶；screw 穿 hub bore（`allow_overlap(screw_core,lever_hub)`，screw 仍 frame 的 PRISMATIC child mimic）| leverhandle L537-543 |

### Slot B / handle — butterfly_wing
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_hub` + `wing_{i}`×2 为 `screw` visual）| winghandle L258, L261-268 |
| internal joints | 无 | — |
| upstream interface | hub 坐 spindle 顶；wing root 嵌 hub（`for i,sign in enumerate((-1,1))`，run_tests 验 wing root 覆盖 hub X 范围）| winghandle L261-268, L431-440 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| foot | enum | swivel_ball_pad / fixed_flat_pad / anvil_disc | swivel_ball_pad | choice | 由 deterministic procedural sampler 选；swivel_ball_pad 独带 `screw_to_pad` REVOLUTE | Slot A 表 |
| handle | enum | tbar_caps / tbar_balls / side_lever / butterfly_wing | tbar_caps | choice | sampler 选；side_lever 独带 `frame_to_lever` REVOLUTE（lever 并列挂 frame）| Slot B 表 |
| frame_silhouette | enum | rounded_C / boxy_deep | rounded_C | choice | sampler 选；只换 frame mesh profile + 喉深尺寸 | Slot C 表 |
| palette_style | enum | red_blue_classic / black_zinc_chrome / cast_iron_steel / galvanized_industrial / orange_safety | red_blue_classic | palette | palette only，**不计入 slot_choice**；每 seed 采一套（材质/色，见下表）| 各样本材质 |
| throat_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放喉口竖直开口（THROAT / BOSS_CENTER_Z）→ 联动 screw_len、bore 高，clamp | A L52 / B L62 |
| throat_depth_scale | float | [0.85, 1.30] | 1.0 | independent | 缩放喉口 Y/X reach（THROAT_Y / THROAT_DEPTH）；boxy_deep 上限偏大，clamp | A L53 / B L91 |
| frame_section_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 frame 截面厚（FRAME_DEPTH/BAR、FRAME_THICK）保刚性观感，clamp | A L49-50 / B L52 |
| screw_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 spindle 半径 + boss bore（保 screw-in-boss 过盈带），clamp | A L66-67 / B L69-70 |
| screw_travel_scale | float | [0.80, 1.10] | 1.0 | independent | 缩放 PRISMATIC upper（夹紧行程），clamp（≤ 杆尖到 anvil 的可达行程）| A L332 |
| pad_radius_scale | float | [0.85, 1.20] | 1.0 | conditional | foot 压脚面半径（swivel/fixed/anvil disc 各自基线）；anvil_disc 基线最大，clamp | A L85 / anvilfoot L85 |
| swivel_range_scale | float | [0.80, 1.10] | 1.0 | conditional | 仅 foot=swivel_ball_pad 有效；缩放 `screw_to_pad` lower/upper（保 |q|≤0.35）| A L349 |
| lever_arm_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 handle=side_lever 有效；缩放 LEVER_ARM_LEN（保 arm 不超 frame 包络过远）| leverhandle L84 |
| lever_open_scale | float | [0.80, 1.10] | 1.0 | conditional | 仅 handle=side_lever 有效；缩放 `frame_to_lever` upper（保 ≤π·0.55）| leverhandle L362 |
| handle_span_scale | float | [0.85, 1.15] | 1.0 | conditional | handle=tbar_caps/tbar_balls/butterfly_wing 时缩放横杆 / 翼跨度（保 >0.06 读作把手）| A L78 / B L78 / winghandle L79 |
| (—) | constraint | — | — | inequality | screw-in-boss 过盈带：`boss_bore_r = (screw_r·screw_radius_scale + thread_r) − embed`，embed∈[0.0006,0.001]；违反则同步缩放 boss bore 保过盈 | A L160 / B L167 |
| (—) | constraint | — | — | inequality | 夹紧行程不超喉：`screw_travel·screw_travel_scale ≤ (rest_tip_z − anvil_top_z) − pad_thick − clearance`；违反按比例缩 travel | A L319-323 / B L97-101 |
| (—) | constraint | — | — | inequality | rest 开口正：`OPEN_GAP·throat_height_scale ≥ 0.012`（喉口必有真实开口，盖闭前止）；违反抬高 rest_tip_z 或拒绝重采 | A L320-321 |
| (—) | constraint | — | — | inequality | side_lever arm 不撞 frame spine：`LEVER_ARM_LEN·lever_arm_scale` 在 +X 方向不与 frame 背脊（−Y/+Y 侧）穿模；arm 沿 X 摆出，clamp | leverhandle L84, L475-494 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 5★ 样本观察的真实材质 / 色集）：
| palette_style | frame | screw/spindle | handle | pad/foot | 来源样本 |
|---|---|---|---|---|---|
| red_blue_classic（默认）| 红铸铁 (0.86,0.13,0.10) | 蓝 (0.13,0.32,0.72) | 紫 hub/bar + 橙端帽/翼 (0.95,0.42,0.08) | 蓝 | parent A / anvilfoot / winghandle / leverhandle |
| black_zinc_chrome | 黑铸铁 (0.10,0.10,0.11) | 锌镀 (0.74,0.76,0.79) | chrome T-bar (0.82,0.84,0.86) + 黑球 (0.07,0.07,0.08) | 锌 | parent B / frame |
| cast_iron_steel | 深灰铸铁 | 钢 spindle (0.62,0.64,0.67) | 钢把手 | 钢 anvil/pad | A `STEEL` + B cast_iron 混 |
| galvanized_industrial | 镀锌灰 frame | 锌螺杆 | 锌把手 | 锌 pad | B zinc 族外推 |
| orange_safety | 橙安全色 frame | 锌螺杆 | 橙 grip + 黑 rubber ridge (0.18,0.18,0.20) | 钢 | leverhandle `ORANGE`+`RUBBER` 配色外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 foot / handle / frame_silhouette 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（foot / handle / frame_silhouette）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 形成结构差异轴。
- **存在固定 N 的对称 / 阵列 visual（非可变轴，不进 slot_choice）**：
  - tbar_caps 的 `handle_caps`：源用 `for sign in (-1,1)` 对称发射 2 个端帽（A L243），固定 N=2。
  - tbar_balls 的 `ball_pos`/`ball_neg`：源**手写两份** `Sphere`（B L285-296）；模板侧应折成 `for sign in (-1,1)` 循环（与 tbar_caps 同范式），固定 N=2。
  - butterfly_wing 的 `wing_{i}`：源用 `for i,sign in enumerate((-1,1))` 发射 2 片翼（winghandle L261），固定 N=2。
  - side_lever 的 `grip_ridge_{i}`：源用 `for i in range(GRIP_RIDGE_COUNT=5)` 发射 5 根 grip ridge（leverhandle L322-326）；这是 module-local 固定装饰阵列（FIXED 语义 visual，非可变产品域），随 side_lever module 固定 N=5，不暴露为可变 count 轴。
- 这些都是 **module-local 固定多份 visual**（对称端帽 / 球端 / 翼 / grip ridge），按 module 而非 multiplicity 轴声明——clamp 不存在"任意 N 个把手 / N 个压脚"的真实产品域。copied object 用共享 helper 发射、绝对式对称 placement（±sign · span/2），无独立 joint（FIXED 装饰，inline screw/lever visual，Rule 1）。

## 拓扑多样性审计

总组合数：foot(3) × handle(4) × frame_silhouette(2) = **24**（全部正交合法，见 §9 兼容矩阵——无非法组合需 gate）。

仅 foot(3) × handle(4) = **12 ≥ 10**（已达机械门控）；其中 joint 拓扑差异来自：foot 的 {+REVOLUTE swivel / 无 joint × 2 固定脚} 与 handle 的 {+REVOLUTE lever / 无 joint × 3 固定把手} → joint-topology 等价类组合（screw-only / screw+pad-REVOLUTE / screw+lever-REVOLUTE / screw+pad+lever 双 REVOLUTE）×（foot 是否独立 part）。叠 frame_silhouette(2) → 24，充裕。

理由：foot × handle 单独即 12 distinct 组合，含 4 类真实 joint 拓扑（仅 PRISMATIC / PRISMATIC+swivel-REVOLUTE / PRISMATIC+lever-REVOLUTE / PRISMATIC+swivel+lever 双 REVOLUTE）与 part 数差异（screw 是否多 `pad` part、是否多 `lever` part）；叠 frame_silhouette(2) 后 24 distinct，远超 ≥10。**foot 与 handle 的 part/joint 差异天然进 `slot_choices_for_seed` 的 tuple**（`("foot", module)`、`("handle", module)`、`("frame_silhouette", module)`），swivel/lever 的多 part+joint 自然区分。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（foot / handle / frame_silhouette），经兼容矩阵合法化（本类三轴正交，无非法组合需排除，仅做 conditional scale 解析），再 uniform 各连续 scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 side_lever 摆动 + swivel pad 倾摆 + 夹紧闭合姿态）。


Controlled local parameterization：见 §参数表的 throat_height_scale / throat_depth_scale / frame_section_scale / screw_radius_scale / screw_travel_scale（independent）+ pad_radius_scale / swivel_range_scale（@swivel）/ lever_arm_scale / lever_open_scale（@lever）/ handle_span_scale（@非 lever）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：swivel_range 仅 swivel_ball_pad、lever_* 仅 side_lever、handle_span 仅非 lever）→ 采 independent 喉 / 截面 / 螺杆 / 行程 scale → 派生（boss bore 随 screw_radius_scale、screw_len 随 throat_height_scale）→ 用四条 inequality（过盈带、行程不超喉、rest 开口正、lever 不撞 spine）投影 / 回缩。跨部件依赖（boss bore vs spindle、travel vs 喉深、lever arm vs frame）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 screw-in-boss / pad-neck / lever-hub captured 接口、swivel/lever joint origin、固定阵列 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（foot/handle/frame_silhouette），再解析 conditional scale，再 uniform 各 independent scale，采 palette_style | slot_choices_for_seed 含 `("foot",m)`/`("handle",m)`/`("frame_silhouette",m)` 且与 build 一致 |
| compatibility matrix | **三轴正交，全 24 组合合法**——无非法组合需 gate。仅 conditional 解析：(1) swivel_range_scale 仅 foot=swivel_ball_pad 生效（否则忽略，pad/disc 无 joint）；(2) lever_arm_scale/lever_open_scale 仅 handle=side_lever 生效；(3) handle_span_scale 仅 tbar_caps/tbar_balls/butterfly_wing 生效；(4) pad_radius_scale 基线随 foot（anvil_disc 最大）；(5) side_lever + swivel_ball_pad 合法（双 REVOLUTE：lever 绕 Z + pad 绕 Y，互不冲突，lever 在杆顶、pad 在杆尖）。 | 无 floating / collision / lever 撞 frame / screw 不过 boss / pad 倾出喉 / 行程不足或穿 anvil |
| controlled local variation | 5 independent + 5 conditional clamped scale，每 build 统一；conditional 随 slot 解析 | 比例变化不破坏 screw-in-boss/pad-neck/lever-hub captured、swivel/lever origin、夹紧闭合、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 foot/handle 机构 QC（swivel 倾摆 / lever 摆动 / 夹紧闭合）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| foot/pad | 3 | yes | yes | swivel(+REVOLUTE 独立 part) / fixed(visual 无 joint) / anvil_disc(visual 无 joint) |
| handle | 4 | yes | yes | tbar_caps / tbar_balls（visual）/ side_lever(+REVOLUTE 独立 part) / butterfly_wing（visual）|
| frame_silhouette | 2 | yes | no | rounded_C / boxy_deep（mesh-profile 维度；2 candidate，降级理由见 Slot C 注 + §13）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("foot",m)`/`("handle",m)`/`("frame_silhouette",m)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；swivel_range/lever_*/handle_span/pad_radius 为 conditional 随 foot/handle 解析；四条 inequality（过盈带、行程不超喉、rest 开口正、lever 不撞 spine）在 resolve 内投影 / 回缩
- compatibility matrix 三轴正交无非法组合；conditional scale 仅在对应 module 生效（不在无 joint 候选上设 swivel/lever scale）
- 连续 scale clamp 后不破坏 screw-in-boss / pad-neck / lever-hub captured 接口、swivel/lever joint origin、夹紧闭合、固定阵列 visual
- 关键 joint：`frame_to_screw` PRISMATIC axis≈(0,0,−1)（abs(axis[2])>0.99、x/y≈0，全候选共享）；foot=swivel_ball_pad 时 `screw_to_pad` REVOLUTE axis≈(0,1,0)；handle=side_lever 时 `frame_to_lever` REVOLUTE axis≈(0,0,1)（abs(axis[2])>0.99）
- captured 过盈：element-scoped `allow_overlap`（`screw_core`↔`frame_body`；`swivel_pad`/`pressing_disc`↔`spindle/screw_core`；`tbar`↔`spindle`；`ball_*`↔`tbar`；`wing_*` root↔`handle_hub`；`screw_core`↔`lever_hub`），照搬各样本 run_tests 的 allow_overlap 段
- 固定阵列 visual 遵循 `handle_caps{±}`/`ball{±}`/`wing_{i}`/`grip_ridge_{i}` 命名 + 绝对式对称 placement + Rule 1（无独立 joint）
- side_lever 的 `lever` 与 `screw` 并列挂 frame（lever parent=frame、screw parent=frame，见 leverhandle L448-457）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- foot ∈ {fixed_flat_pad, anvil_disc} 时断言无 `screw_to_pad` joint、无 `pad` part（照搬 anvilfoot L364-374, L406-411）

## Reject cases

- foot=fixed_flat_pad / anvil_disc 仍发射 `screw_to_pad` REVOLUTE 或独立 `pad` part → 违反这两候选的"压脚是 screw visual 无 joint"拓扑（anvilfoot run_tests 显式拒）。
- handle=side_lever 把 `lever` 挂在 `screw` 而非 `frame`（lever 应与 screw 并列挂 frame，绕 Z 摆动 mimic 驱动；挂 screw 会随螺杆平移、撞 boss）。
- 把对称端帽 / 球端 / 翼 / grip ridge 当独立活动 part 加 joint → 违反 Rule 1（固定装饰阵列，应 inline 为 screw/lever visual）。
- screw rest pose 设成夹紧（q=upper）而非 q=0 开口姿态 → current-pose 与 viewer 目检不符（所有样本 rest 喉口开，杆尖悬 anvil 上方 OPEN_GAP）。
- `frame_to_screw` origin 放在喉中心或任意点而非杆底尖 / boss bore 真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 夹紧行程过大致压脚穿透 anvil（screw_travel 超 rest_tip_z−anvil_top_z）→ §7 第二条 inequality FAIL；须按比例缩 travel。
- boss bore 开得比 thread crest 大（无过盈）致 spindle 漂浮在孔内 → screw-in-boss 不接触，`expect_contact` FAIL；bore 须比 crest 紧 embed∈[0.0006,0.001]。
- 给 captured 过盈接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- side_lever arm 过长 / 摆角过大撞 frame spine 或 boss → §7 第四条约束 FAIL；clamp arm 长 / 摆角。
- 把连续尺寸 / 颜色 / 材质（palette_style / 喉 scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 binder clip / vise / pliers 语义混入（弹簧夹 / 平行颚 / 双臂剪）→ 出类，本类是 C 形单螺杆手夹。

## 与相邻类别的边界

- 不该混入：**binder clip / 文具弹簧夹 / 鳄鱼夹（clip）**——弹簧 / 杠杆张力夹持，无螺杆进给、无 C 铸铁 frame；已有独立 slug `clip`（主运动 spine 不同）。
- 不该混入：**台钳 / 桌虎钳（bench vise）**——箱形导轨座 + 双滑块平行颚 + 丝杆驱动滑块横移；本类 frame 是 C 形、单螺杆竖直进给。
- 不该混入：**钳子 / 老虎钳（pliers）**——双臂绕中心 pivot 剪切，无螺杆 / C frame / anvil。
- 不该混入：**快速夹 / F 形夹（bar/quick clamp）可滑横梁**——本类 frame 是固定深度 C 喉，不是可沿长杆滑动的横梁滑块（如需可作单独 slug）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **坐标约定统一到 A 家族**（screw 轴 +Z / C 口 −Y / 把手沿 X / screw 原点 = 杆底尖 / PRISMATIC axis=(0,0,−1) / swivel 绕 Y），把 B 家族 tbar_balls / boxy_deep 按此 rebase（见 §13）是否接受，还是模板内保留双约定分支；(2) frame_silhouette 仅 2 candidate（mesh-profile 维度，降级理由见 Slot C）是否接受还是要求回 fork 池补造；(3) side_lever 同时带 `frame_to_lever` REVOLUTE + screw mimic PRISMATIC，模板是否实现 mimic 联动还是仅 lever 摆动 + screw 独立 PRISMATIC（源把两者都做成可独立 pose 的 joint，screw 是真实 PRISMATIC、lever 是装饰性 REVOLUTE）；(4) side_lever × swivel_ball_pad 双 REVOLUTE 组合是否需特别 QC；(5) Topology target 24<300 的说明是否接受（本小类真实结构上限）；(6) palette_style 5 套是否合适，cast_iron_steel/galvanized/orange_safety 三套为样本配色外推。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **坐标统一**：模板统一到 A 家族约定。B 家族两个 module（tbar_balls、boxy_deep）需 rebase：
  - tbar_balls：源 tbar 沿 Y（B `_tbar_solid` 在 XZ workplane 沿 Y extrude），模板改沿 X（与 tbar_caps 同，YZ workplane 沿 X）；两球 `ball_pos`/`ball_neg` 折成 `for sign in (-1,1)` 循环置于 bar 端（X 轴）。
  - boxy_deep：源 `_frame_solid` C 口朝 +X、screw 原点 = boss 中心；模板改 C 口朝 −Y、screw 原点 = 杆底尖、PRISMATIC axis=(0,0,−1)（与 rounded_C / A 家族同），仅保留"深喉方角 + 几乎不倒角"的 profile 形态差异。
- **共享 helper**：`_build_frame_mesh`（按 frame_silhouette 切圆角浅喉 / 方深喉 profile + 喉 scale）、`_build_screw_core_mesh`（spindle + boss-fit 半径，注意 A 用 helical sweep、B/anvilfoot 用 ring 近似、frame/leverhandle/winghandle 用纯 cylinder——模板选最稳的 cylinder@thread_crest 半径，避免 boolean fragility，见 winghandle L186 / leverhandle L183）、`_build_pad_mesh`（按 foot 切 ball/flat/anvil disc）、`_build_handle`（按 handle 切 tbar/lever/wing）、`_build_grip_ridge`（side_lever 的 5 根 ridge 循环）。
- captured 接口 allow_overlap：`run_clamp_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（A L392-398、B L456-490、anvilfoot L380-386、leverhandle L521-543、winghandle L356-362）。
- conditional 范围解析顺序：先采 foot / handle / frame_silhouette → 解析 swivel_range（仅 swivel_ball_pad）/ lever_*（仅 side_lever）/ handle_span（仅非 lever）/ pad_radius 基线（随 foot）→ 采 independent 喉/截面/螺杆/行程 scale → 派生 boss bore（随 screw_radius_scale）+ screw_len（随 throat_height_scale）→ 投影四条 inequality。
- side_lever 实现注记：源把 `frame_to_lever`（REVOLUTE 绕 Z，lower=0/upper=1.5）与 `frame_to_screw`（PRISMATIC）做成两个可独立 pose 的 joint，screw 是真实夹紧 PRISMATIC、lever 是 mimic 装饰摆动（leverhandle 注释称 "mimic follower"，但代码未做真实 mimic 联动，两 joint 独立）。模板沿用此简化（两独立 joint），lever 与 screw 都 parent=frame。
- 参考模板：选运动拓扑相近的——root chassis + parallel children + 可选 REVOLUTE child（cushion 的 base + lid REVOLUTE + interior 互斥 / shopping_bucket 的 telescoping PRISMATIC + 翻盖 REVOLUTE）；clamp 的 frame→screw PRISMATIC + 可选 screw→pad / frame→lever REVOLUTE 与之同构。clamp 尺度小（frame ~0.13-0.18m、screw ~0.085m），joint origin 须精确落真实硬件面（≤0.015m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent A 基线）| swivel_ball_pad + tbar_caps + rounded_C | rec_build-...-clam_...e34de725 | `_build_frame_mesh` L101-166 / `_build_anvil_mesh` L169-177 / `_build_pad_mesh` L256-277 / `frame_to_screw` PRISMATIC L325-333 / `screw_to_pad` REVOLUTE L340-350 / handle bar+caps L228-253, L303-304 / allow_overlap L392-398 | A 家族基线坐标约定 + swivel pad（独立 part+REVOLUTE）+ T-bar 端帽 + 圆角 C frame + screw-in-boss captured 范式 |
| S2 | A / B / C（parent B 基线）| fixed_flat_pad + tbar_balls + rounded_C | rec_build-...-clam_...1a4c37c7 | `_frame_solid` polyline C-profile L102-172 / `_pad_solid` L219-237 / `swivel_pad` visual L297-301 / `_tbar_solid`+balls L240-249, L280-296 / `frame_to_screw` PRISMATIC L313-326 / allow_overlap L456-490 | 固定平 pad（screw visual 无 joint）+ T-bar 球端 tommy bar + polyline C-profile（B 家族，须 rebase 坐标）|
| S3 | A | anvil_disc | rec_clamp_var_anvilfoot | `_build_pressing_disc_mesh` L261-283 / `pressing_disc` visual L312 / 断言无 screw_to_pad/pad L364-374, L406-411 | 宽平 anvil 压盘（screw visual 无 joint，断言固定脚拓扑）|
| S4 | C | boxy_deep | rec_clamp_var_frame | `_frame_solid` 深方 profile L104-177 / 深喉断言 L484-501 | 深喉方角 C frame mesh-profile（B 家族，须 rebase 坐标）|
| S5 | B | side_lever | rec_clamp_var_leverhandle | `lever` part + hub/arm/grip L308-326 / `grip_ridge_{i}` `for i in range(5)` L322-326 / `frame_to_lever` REVOLUTE 绕 Z L355-363 / screw mimic PRISMATIC L377-387 / `screw_to_pad` REVOLUTE L392-400 / allow_overlap(screw_core,lever_hub) L537-543 | 单侧摆动 lever（独立 part+REVOLUTE 绕 Z，lever 并列挂 frame）+ 5 根 grip ridge 循环 |
| S6 | B | butterfly_wing | rec_clamp_var_winghandle | `handle_hub` L258 / `wing_{i}` `for i,sign in enumerate((-1,1))` L261-268 / wing-root-overlaps-hub 断言 L431-440 | 蝶形 / 翼形拧柄（hub + 2 片扁平 Box 翼作 screw visual，无 joint）|
