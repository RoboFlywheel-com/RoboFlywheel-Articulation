# Container / Shipping container (ISO intermodal corrugated-steel cargo container) — Modular Spec

> 来源小类：`picture/Container/Shipping container`（articraft_data 上游 Container/Shipping container fork-variant pool）。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template/data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`body` / `door_l` / `door_r` / `body_to_door_*` REVOLUTE / `_corrugated_wall` / `_corrugated_end_wall` / `_corrugated_door_panel` / `_louvered_wall` / `_louver_slat` / `_insulated_wall` / `_corrugated_lid_panel` / `body_to_roof_lid` REVOLUTE / `body_to_curtain` PRISMATIC / `body_to_bow_hinged` REVOLUTE / `handle_*` REVOLUTE / `rod_i` / `keeper_i_j` / `corner_i` 等），行号仅作定位。
> 全部 9 个 record（1 parent + 8 fork 变体）均**逐一全文读取**，不抽样。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_shipping_container` |
| template path | `agent/templates/Container_Shipping_container.py` |
| test path (optional) | `tests/agent/test_container_shipping_container_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: door_closure + roof_top + wall_surface 挂到共同 root `body`（parallel_children）；door_closure 内含 door-leaf **multiplicity 复制轴** door_count）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 converged fork 变体）|
| read_count | 9（全部全文读取）|
| read_scope | all retained samples in this category（parent + 全部 fork 变体）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

逐样本要点（均已全文读）：
- **parent** `rec_white-twenty-foot-...0e395b54`（白色 ISO 20ft）：root `body`（floor/roof/2× `side_wall_*` 竖波纹/`front_wall`/`door_header`/`door_sill`/`post_p`/`post_n`/8× `corner_i`）+ 2× 货门（`door_l`/`door_r` REVOLUTE 侧铰 +Z）+ 每门 2× `rod_i`/`keeper_i_j` + cam handle（`handle_*` hub/lever/grip REVOLUTE 绕 rod +Z）。door_closure=double_swing_doors / roof_top=flat_solid / wall_surface=corrugated 三轴基线，N=2。
- **var_n4_doorleaves**：door_closure 的 **N=4** 复制证据。`for i in range(DOOR_COUNT=4)` 生成 `door_0..3`，偶数叶 +Y 铰 / 奇数叶 -Y 铰；新增 `mullion` 中柱作内铰点；每叶 1× rod + 1× handle；`_build_handle()` helper 抽出。
- **var_single_swing_door**：door_closure 的 **N=1**。单 `door` 满宽（`door_w = W-0.16`），+Y 铰，4× rod/handle 集中一片；test 断言只 1 个 door part。
- **var_roll_up_door**：door_closure = roll_up（PRISMATIC 轴）。`curtain` part（`bottom_bar` + `slat_0..21` loop，`N_SLATS=22`）经 `body_to_curtain` PRISMATIC +Z 竖向滑升；body 增 `track_p/n` 导轨 + `drum` 卷筒。
- **var_side_access_doors**：door_closure = side_access。开口移到 +Y 长侧壁；两端铰 `door_0`/`door_1` REVOLUTE +Z 向 +Y 外开；`_corrugated_side_door_panel` helper（XZ 平面，ribs face +Y）；body 改 `end_wall_p`/`end_wall_n` 实端壁 + `post_0/1`。
- **var_hatch_lid**：roof_top = hatch_lid。去固定 roof，改 `roof_lid` part 经 `body_to_roof_lid` REVOLUTE axis=(-1,0,0) 沿 +Y 长顶边上翻；body 增 `top_rail_p/n`/`top_rail_end`/`hinge_barrel_0..4`/`latch_rail`；`_corrugated_lid_panel` + `_hinge_barrel`/`_lid_hinge_eye` helper。
- **var_open_top_tarp**：roof_top = open_top_tarp。去固定 roof，改 `tube_from_spline_points` 弧形 `bow_0..3` 固定弓 + `tarp_main` 软篷（body visual）+ 1× `bow_hinged` part 经 `body_to_bow_hinged` REVOLUTE axis=(-1,0,0) 可掀；`top_rail_p/n` + `hinge_ear_0/1` + `hinge_barrel`。
- **var_louvered_vents**：wall_surface = louvered_vents。`side_wall_*` 改 `_louvered_wall`（`_louver_slat` 横向斜置百叶 loop，`n_slats` 由墙高自适应，倾角 35°）；端壁/门保持波纹。
- **var_smooth_reefer_panel**：wall_surface = smooth_reefer。`side_wall_*` + `front_wall` 改 `_insulated_wall`/`_insulated_end_wall` 平滑齐面无肋（冷藏式）；test 断言墙 Y 厚 ≈ WALL_T。

冗余/分流说明：door 数差异（1/2/4）属同一 multiplicity 轴，不另立 candidate；只换颜色/材质（白/锈/蓝/灰）不另列 candidate，统一归 `palette_style`。跨轴组合（如 roll_up × louvered）不专门造变体，留给模板采样器。

## 核心身份

ISO 国际标准化海运集装箱（intermodal shipping container）：一只**长卧钢箱**，长轴沿 +X、宽沿 Y、高沿 Z，底坐地（floor 顶面在 z≈0.10），长宽高近 ISO 20ft（L≈6.06 / W≈2.44 / H≈2.59，X 最长且 X>Y+1、X>Z+1）。root `body` 发射：钢 floor + 顶（固定 roof 或被 roof_top 槽替换）+ 两长侧壁（竖波纹 / 百叶 / 平滑保温三选一，由 wall_surface 槽决定）+ 一端 `front_wall` + 8× `corner_i` 角件（dark 立方体）+ 门洞框（`door_header`/`door_sill`/`post_*`）。**主活动语义**是一端（默认 +X 货端）的开闭机构（door_closure 槽）：双扇侧铰波纹货门（REVOLUTE，各带 2× 竖锁杆 `rod` + 凸轮把手 `handle` REVOLUTE）/ 单扇满宽门 / 多叶交替铰门（N 复制）/ 卷帘门（PRISMATIC 竖升）/ 侧壁长门对（开口移到长侧壁）。可选顶部结构（roof_top 槽）：固定平钢顶 / 后铰波纹翻盖（REVOLUTE 上翻）/ 开顶弧弓+软篷（固定弓 + 1× 可掀弓）。默认成熟域：单箱单端开闭机构 + 固定平顶 + 竖波纹壁。

身份硬标志：① 长卧大箱（X 最长，米级尺寸），② 竖波纹钢蒙皮，③ 8 个角件，④ 后端货门 + 竖锁杆/凸轮把手锁具，⑤ 真实铰链/滑升运动语义。

## 与相邻类别的边界

- 不该混入：**container_box（桌面纸/木收纳箱）**——理由：box 是小型桌面箱（开盖翻盖小件），shipping container 是米级长卧钢箱、竖波纹蒙皮、8 角件、货门锁杆，footprint 与身份完全不同。
- 不该混入：**container_locker（柜/储物柜）**——理由：locker 是直立柜体（柜门朝前、内置层板/挂杆），shipping container 是长卧运输钢箱、长轴 X 最长、端门 + 锁杆凸轮，非家具柜。
- 不该混入：**bag_suitcase / 通用收纳箱**——理由：无 ISO 角件、无波纹钢、无锁杆货门机构。
- reject：用纯 Box 占位当箱体而无波纹/角件/锁具 → 失类别身份。

## 槽位 + 候选模块表

> **建模注记**：三轴均挂到共同 root `body`（parallel_children）。`wall_surface` 是 body 的 `side_wall_*`（±`front_wall`）mesh helper 选择（一次性发射 body visual，非独立串联 slot）；`roof_top` 是 body 顶部的 visual/可动子件（固定 roof visual 或 `roof_lid`/`bow_hinged` 活动 part 挂 body）；`door_closure` 是 body 端口的活动门机构（含 N 复制轴）。三轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：door_closure（**主开合机构槽** —— 货门/开闭机构；必须保 ≥1 非 fixed joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| double_swing_doors（基线 N=2）| rec_white-twenty-foot-...0e395b54 | `_corrugated_door_panel` L87-117 + `door_l`/`door_r` part L208-217 + `body_to_door_l/r` REVOLUTE +Z L233-243 + `handle_*`(hub/lever/grip) + `door_to_handle` REVOLUTE +Z L274-305；rod/keeper L256-269 | eligible if compatible | +X 端双扇侧铰波纹门，各 2× `rod` + 凸轮 `handle`（绕 rod +Z REVOLUTE）；每扇 REVOLUTE +Z 绕外铰边，q=0 闭合，正 q 自由边 +X 外摆 0..120° |
| single_swing_door（N=1）| rec_container_shipping_container_var_single_swing_door | 单 `door` part L199-204 + `body_to_door` REVOLUTE +Z L218-228 + 4× rod/handle loop L236-289 | eligible if compatible | +X 端单扇满宽侧铰门（`door_w = W-0.16`），+Y 铰，4× 锁杆/把手集中一片；test 断言只 1 个 door part |
| n_doorleaves（N=4 多叶）| rec_container_shipping_container_var_n4_doorleaves | `for i in range(DOOR_COUNT)` L232-290 + `door_i` + `body_to_door_i` REVOLUTE +Z L258-268 + `_build_handle` helper L113-144 + `mullion` 中柱 L201-203 | eligible if compatible | +X 端 N 片窄叶交替铰（偶 +Y / 奇 -Y），中柱 `mullion` 作内铰点；每叶 1× rod + 1× handle；是 multiplicity 轴的 N>2 证据 |
| roll_up_door | rec_container_shipping_container_var_roll_up_door | `curtain` part(`bottom_bar`+`slat_i` loop)L260-279 + `body_to_curtain` PRISMATIC +Z L282-292 + `_curtain_slat` L121-123 + `track_p/n` L242-246 + `_drum_assembly` L130-168 | eligible if compatible | +X 端单片分段卷帘门，`body_to_curtain` PRISMATIC +Z 竖升 0..2.30m；body 增导轨 `track_*` + 卷筒 `drum`；无凸轮把手 |
| side_access_doors | rec_container_shipping_container_var_side_access_doors | `door_0`/`door_1` part L231-237 + `body_to_door_*` REVOLUTE +Z 向 +Y L246-257 + `_corrugated_side_door_panel` L102-128 + `post_0/1` L200-203 + 实 `end_wall_p/n` L178-185 | eligible if compatible | 开口移到 +Y 长侧壁，两端铰整长侧门对向 +Y 外开；端壁改实壁（无 +X 端口）；门面 XZ 平面 ribs face +Y |

硬约束记录：door_closure 5 candidate（达 3-6 目标）。含 REVOLUTE +Z（swing）/ PRISMATIC +Z（roll-up）两种 joint 拓扑 + multiplicity 轴（door_count 1/2/4）+ 接口点位变化（+X 端口 vs +Y 侧壁）。每个 candidate **≥1 non-fixed joint**（满足主机构 ≥1 活动）。

### Slot B：roof_top（顶部结构 —— 固定顶 visual 或可动顶件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| flat_solid（基线）| rec_white-twenty-foot-...0e395b54 | body `roof` 固定 visual L146-148（`BoxGeometry((body_len,W,0.05))` @ z=H-0.025）| eligible if compatible | 固定平钢顶板（body visual，无独立 joint）|
| hatch_lid | rec_container_shipping_container_var_hatch_lid | `roof_lid` part L428-434 + `body_to_roof_lid` REVOLUTE axis=(-1,0,0) L460-470 + `_corrugated_lid_panel` L134-173 + `top_rail_p/n`/`top_rail_end` L249-258 + `hinge_barrel_i`/`_hinge_barrel` L180-185,L265-270 + `lid_eye_i`/`latch_rail` L437-448 | eligible if compatible | 去固定 roof，整片波纹顶盖 `roof_lid` 沿 +Y 长顶边 REVOLUTE -X 轴上翻 0..100°；body 增顶框 `top_rail_*` + 铰链桶 `hinge_barrel_i` + 锁条 `latch_rail`；q=0 盖座 rim |
| open_top_tarp | rec_container_shipping_container_var_open_top_tarp | 固定 `bow_0..3`(`_build_bow_mesh` tube)L478-487 + `tarp_main`(`_build_tarp_mesh`)L494-503 + `bow_hinged` part L597-628 + `body_to_bow_hinged` REVOLUTE axis=(-1,0,0) L651-661 + `top_rail_p/n` L473-476 + `hinge_ear_0/1` L665-672 | eligible if compatible | 去固定 roof，弧形钢弓 `bow_i`（tube_from_spline）+ 软篷 `tarp_main`（body visual）+ 1× 可掀弓 `bow_hinged` REVOLUTE -X 上掀 0..80°；顶部敞开框架式 |

硬约束记录：roof_top 3 candidate（达下限 3）。flat_solid 为固定 visual（无 joint）；hatch_lid/open_top_tarp 各引入 1× REVOLUTE axis=(-1,0,0) 上翻活动件（roof_lid / bow_hinged）+ 顶框 visual 组改写。主多样性由 door_closure × wall_surface 充裕支撑（见 §9）。

### Slot C：wall_surface（侧壁/表面结构 —— 非装饰，表面家族更换；root body 的 `side_wall_*`/`front_wall` mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| corrugated（基线）| rec_white-twenty-foot-...0e395b54 | `_corrugated_wall` L55-70（竖肋 for-loop）+ `_corrugated_end_wall` L73-84 + body `side_wall_p/n`/`front_wall` L153-161 | eligible if compatible | 竖向波纹钢侧壁（base skin + 竖肋 loop，肋数由墙长自适应）+ 波纹端壁 |
| louvered_vents | rec_container_shipping_container_var_louvered_vents | `_louvered_wall` L72-109（top/bottom rail + post + `_louver_slat` 横向斜置百叶 loop）+ `_louver_slat` L61-69（35° 斜置）+ body `side_wall_*` L192-195 | eligible if compatible | 侧壁改横向斜置百叶通风片（等距 loop，`n_slats` 由墙高自适应），有结构框 rail/post；端壁保持波纹 |
| smooth_reefer | rec_container_shipping_container_var_smooth_reefer_panel | `_insulated_wall` L56-63（平滑齐面无肋）+ `_insulated_end_wall` L66-70 + body `side_wall_*`/`front_wall` L139-147 | eligible if compatible | 去波纹肋，改平滑保温齐面板（冷藏式），墙 Y 厚 ≈ WALL_T；test 断言无肋 |

硬约束记录：wall_surface 3 candidate（达下限 3）。三者均改 body 侧壁 mesh helper（corrugated 竖肋 / louvered 横斜百叶+框 / insulated 平滑），是真实表面结构家族差异（part tree 同、visual mesh 拓扑不同），非纯装饰/颜色。样本只支持这三族。

## 槽位图（slot graph）

pattern: mixed（root `body` 为 parent，三槽 parallel_children 挂上去；door_closure 内含 door_count multiplicity 复制轴）

```
body(wall_surface, roof_top=flat_solid 时含 roof visual)  [ROOT, 长卧坐地 z≈0]
  │  wall_surface ∈ {corrugated / louvered_vents / smooth_reefer}：决定 body side_wall_*(/front_wall) mesh helper（固定 visual）
  │  door_closure 的端口框 visual（post/header/sill 或 track/drum 或 side post + 实端壁）随所选 door module 在 body 上发射
  │
  ├── roof_top = flat_solid:
  │     body 固定 visual "roof"（无 joint）
  │
  ├── roof_top = hatch_lid:
  │     body 顶框 visual(top_rail_*, hinge_barrel_i, latch_rail)
  │     body --[body_to_roof_lid: REVOLUTE axis=(-1,0,0) @ +Y 长顶边 hinge line, z=H]--> roof_lid
  │
  ├── roof_top = open_top_tarp:
  │     body 顶框 visual(top_rail_p/n, hinge_ear_0/1) + 固定 bow_0..3 tube + tarp_main 软篷(body visual)
  │     body --[body_to_bow_hinged: REVOLUTE axis=(-1,0,0) @ +Y top rail, z=H]--> bow_hinged(可掀弓+tarp_hinged)
  │
  ├── door_closure = double_swing_doors / single_swing_door / n_doorleaves（N 复制）:
  │     for i in range(door_count):
  │       body --[body_to_door_i: REVOLUTE axis=(0,0,±1) @ 端口外铰边/中柱, z=H/2]--> door_i
  │            door_i --[door_i_to_handle_*: REVOLUTE axis=(0,0,1) @ rod_x,rod_y]--> handle_*（凸轮把手）
  │
  ├── door_closure = roll_up_door:
  │     body(track_p/n 导轨 + drum 卷筒 visual)
  │     body --[body_to_curtain: PRISMATIC axis=(0,0,1) @ FRAME_X, z=SILL_TOP]--> curtain(bottom_bar + slat_i loop)
  │
  └── door_closure = side_access_doors:
        body(开口移 +Y 侧壁; end_wall_p/n 实端壁; post_0/1)
        body --[body_to_door_0: REVOLUTE axis=(0,0,+1) @ -X 开口边, y=W/2]--> door_0
        body --[body_to_door_1: REVOLUTE axis=(0,0,-1) @ +X 开口边, y=W/2]--> door_1
             door_i --[door_i_to_handle_i_j: REVOLUTE axis=(0,0,1)]--> handle_i_j
```

接口点位与 joint 语义：
- **swing-door 接口**：`body_to_door_*` origin 落在端口外铰边硬件（`(DOOR_X, ±(door_half_w+0.04), H/2)`）或多叶的中柱 `mullion`，axis=(0,0,±1)（per-leaf 选号，正 q 自由边外摆）。`door_i_to_handle` origin 在 rod 位（`(rod_x, rod_y, 0.05)`），axis +Z REVOLUTE，凸轮把手绕锁杆旋转。
- **roll-up 接口**：`body_to_curtain` origin 在门洞框中心底（`(FRAME_X, 0, SILL_TOP)`），axis +Z PRISMATIC，q=0 帘底坐 sill、正 q 竖升入 header 后；curtain 在 `track_*` 导轨内。
- **side-access 接口**：`body_to_door_{0,1}` origin 在 +Y 侧壁开口两端（`(OPENING_X{0,1}, W/2, H/2)`），axis=(0,0,±1)，门向 +Y 外开；端壁改实壁（无 +X 端口）。
- **hatch-lid 接口**：`body_to_roof_lid` origin 在 +Y 长顶边 hinge line（`(body_cx, W/2-CORNER-TOP_RAIL_W, H)`），axis=(-1,0,0)，q=0 盖座 rim（`latch_rail` 锁条）、正 q 上翻；`lid_eye_i` 嵌 `hinge_barrel_i`（captured-fit）。
- **open-top 接口**：固定 `bow_i` + `tarp_main` 是 body visual（无 joint）；`body_to_bow_hinged` origin 在 +Y top rail（`(BOW_POS_X[-1], BOW_SPAN/2, H)`），axis=(-1,0,0) 上掀；`hinge_barrel` 嵌 `hinge_ear_0/1`（captured-fit）。
- **wall / roof=flat 接口**：side_wall / front_wall / 固定 roof 为 body 固定 visual，无独立 joint。
- **mating policy**：门铰边框座 `post`、curtain 帘 ↔ track、lid_eye ↔ hinge_barrel、hinge_barrel ↔ hinge_ear、handle hub ↔ rod 均为 **captured / 友配**（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 post / rim / rod 硬件）+ element-scoped `allow_overlap` 守 overlap（见各 parent/变体 run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有门 q=0 闭合 / 卷帘 q=0 落底 / lid q=0 盖座 / bow_hinged q=0 落座；固定 roof / bow / tarp / wall 固定。门摆 / 帘升 / 盖翻 / 弓掀 / 把手转为 viewer 目检的活动语义。
- **互斥 / 可选**：roof_top=flat_solid 是空机构（仅固定 roof visual）；door_closure 各候选互斥（一次一种端口机构）；side_access 把端口从 +X 移到 +Y（与 +X 端 roof 机构正交，hatch/open-top 仍沿 +Y 长顶边，互不冲突）。

## 每槽位 Module Emits / Interfaces

### Slot ROOT / body（wall_surface + door_closure 端框 + roof=flat 时 roof visual，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: `floor` + `side_wall_p/n`(wall_surface mesh) + `front_wall` + 8× `corner_i` + 端口框 `door_header`/`door_sill`/`post_*` + [roof=flat 时 `roof`]）| parent L135-188 |
| internal joints | 无（root 箱体本身无活动件）| — |
| upstream interface | 长卧坐地（floor 顶 z≈0.10）| parent L141-143 |
| downstream interface | 端口外铰边 / 顶边 hinge line / +Y 侧壁开口（door_closure / roof_top joint 的 parent 接口）| parent L227-238 |

### Slot A / door_closure（每候选发射对应端口活动机构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_l`+`door_r`(+`handle_*`) / 单 `door`(+4 handle) / `door_0..N-1`(+handle_i) / `curtain` / `door_0`+`door_1`(+handle_i_j) | 各 door 源 |
| internal joints | `body_to_door_*` REVOLUTE +Z(swing×N) + `door_to_handle_*` REVOLUTE +Z / `body_to_curtain` PRISMATIC +Z(roll-up) / +Y 侧门 REVOLUTE +Z(side) | parent L233-305 / roll_up L282-292 / side L246-305 |
| body 端框 visual | swing/single/n: `post_p/n`(+`mullion` if N>2)/header/sill；roll_up: `track_p/n`+`drum`；side: `post_0/1`+`end_wall_p/n` | 各源 body 段 |

### Slot B / roof_top（flat=固定 visual；hatch/open-top=活动顶件 + 顶框）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part(flat) / `roof_lid`(hatch) / `bow_hinged`(open-top) | hatch L428 / open-top L597 |
| internal joints | 无(flat) / `body_to_roof_lid` REVOLUTE -X(hatch) / `body_to_bow_hinged` REVOLUTE -X(open-top) | hatch L460-470 / open-top L651-661 |
| body 顶 visual | `roof`(flat) / `top_rail_*`+`hinge_barrel_i`+`latch_rail`(hatch) / `top_rail_p/n`+固定`bow_i`+`tarp_main`+`hinge_ear_0/1`(open-top) | parent L146-148 / hatch L249-276 / open-top L473-503,L665-672 |

### Slot C / wall_surface（root body 的 side_wall_* mesh helper 选择）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`side_wall_p/n`(/`front_wall`) 为 body 固定 visual，mesh helper 不同）| corrugated L153-161 / louvered L192-195 / smooth L139-147 |
| internal joints | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_closure | enum | double_swing_doors / single_swing_door / n_doorleaves / roll_up_door / side_access_doors | double_swing_doors | choice | deterministic procedural sampler 选 | module table |
| roof_top | enum | flat_solid / hatch_lid / open_top_tarp | flat_solid | choice | sampler 选 | module table |
| wall_surface | enum | corrugated / louvered_vents / smooth_reefer | corrugated | choice | sampler 选 | module table |
| door_count | int | [1, 4]（door_closure ∈ swing 家族时生效）| 2 | conditional | 仅 swing 门族暴露；roll_up/side_access 固定 1 帘/2 侧门；加权小 N 偏多（见 §Multiplicity）| n4 L50,L232 / single L234 |
| palette_style | enum | iso_white / maersk_blue / rust_red / weathered_grey / container_green / safety_orange / heavy_rust / fresh_glossy_blue / two_tone_blue_grey / reefer_white（**10 配色**，见下 §Palette 表，每色含 body/doors/accent RGBA + finish）| iso_white | palette | palette only，**不计入 slot_choice**；逐 seed `rng.choice(PALETTE_STYLES)` 采样 | parent L127-129 / hatch L201 / open-top L422 |
| finish | enum（**material-finish 维度，随 palette_style 绑定**）| matte_industrial / weathered / heavily_weathered / glossy / semi_gloss | matte_industrial | palette | 每个 colorway 自带 finish（见 §Palette 表 finish 列），非独立采样；palette only，**不计入 slot_choice** | parent L127-129 / hatch L201 / open-top L422 |
| length_scale | float | [0.90, 2.05] | 1.0 | independent | 缩放 L（20ft↔40ft 连续）→ body_len / 肋数 / 帘 slat 数 / bow 数自适应，clamp；不改拓扑 | parent L35 |
| height_scale | float | [0.92, 1.18] | 1.0 | independent | 缩放 H（standard↔high-cube）→ 壁高 / 门高 / 锁杆长 / 帘行程派生，clamp | parent L37 |
| width_scale | float | [0.96, 1.06] | 1.0 | independent | 缩放 W → 门宽 / 端壁宽 / 顶盖宽派生，clamp（保 ISO 比例）| parent L36 |
| corr_pitch_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放波纹/百叶 pitch → 肋/百叶数反比派生，clamp（细节密度，不改拓扑）| parent L50 / louver L55 |
| door_open_limit | float | [100°, 130°] | 120° | independent | swing 门 REVOLUTE upper limit，clamp；roll_up 行程 = OPENING_H 派生 | parent L242 |
| (—) | constraint | — | — | inequality | 长卧不变式：`L·length_scale > W·width_scale + 1.0` 且 `L·length_scale > H·height_scale + 1.0`（保 X 最长身份），违反则回缩 length_scale | parent test L327-331 |
| (—) | constraint | — | — | conditional | 多叶宽度：`leaf_w = (W·width_scale - 0.16)/door_count ≥ 0.30`（叶太窄则降 door_count 上限），在 resolve 解析 | n4 L226 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。肋数 / 百叶数 / 帘 slat 数 / bow 数都是 **length/height 派生的次级复制层**（由 `max(1, int(span/pitch))` 自适应，非独立采样），随 length_scale/height_scale/corr_pitch_scale 解析。scale 只动安全比例 / clearance / 细节密度，绝不改 door_closure / roof_top / wall_surface 的拓扑或 door_count 等价类。

## Palette（palette_style colorways + material-finish 维度）

> **palette only**：以下 **10 个协调配色（colorway）** 不改任何 slot / candidate / multiplicity / joint / dimension / topology，逐 seed `rng.choice(PALETTE_STYLES)` 整组取色。每个 colorway = **corrugated body（箱体波纹钢蒙皮，含侧壁/端壁）+ doors（货门叶片/卷帘/侧门，与 body 协调或对比）+ accent（8× corner_i 角件 / 锁杆 rod / keeper / 把手 handle / 顶盖与门上贴标 decal）** + 一个 **finish（material-finish 维度）**。RGBA 锚定 5★ 样本所见处（parent L127-129 `white_steel`(0.90,0.91,0.92)/`grey_steel`(0.62,0.64,0.66)/`dark_hardware`(0.18,0.19,0.21)；hatch L201 `hatch_accent`(0.72,0.18,0.14)；open-top L422 `tarp_canvas`(0.12,0.22,0.38)；roll_up L181-182 `curtain_steel`(0.82,0.84,0.86)/`bar_steel`(0.45,0.47,0.50)），其余为 ISO 集装箱真实涂装的合理推断色。
>
> **finish 维度（material-finish）**：`matte_industrial`（标准海运工业哑光漆）/ `weathered`（褪色 + 局部锈斑刷扫 scuff）/ `heavily_weathered`（重度锈蚀斑驳，色相整体偏暗偏棕）/ `glossy`（出厂全新高光漆，亮角件）/ `semi_gloss`（冷藏箱半光洁净漆）。finish 随 colorway 绑定（非独立采样轴），只影响 material 的光泽/磨损语义与微调色相，不改拓扑。weathered / heavily_weathered 配色统一向 scuffed/rust 色调偏移。

| # | palette_style | finish | body（corrugated 蒙皮）RGBA | doors RGBA | accent（corner/rod/keeper/handle/decal）RGBA | 锚定 / 说明 |
|---:|---|---|---|---|---|---|
| 1 | `iso_white`（默认） | matte_industrial | (0.90, 0.91, 0.92, 1.0) | (0.62, 0.64, 0.66, 1.0) | (0.18, 0.19, 0.21, 1.0) | **5★ 锚定**：parent `white_steel`/`grey_steel`/`dark_hardware`（白箱基线） |
| 2 | `maersk_blue` | matte_industrial | (0.10, 0.32, 0.55, 1.0) | (0.10, 0.32, 0.55, 1.0) | (0.18, 0.19, 0.21, 1.0) | Maersk 企业蓝整箱涂装；白色船公司 decal（accent 浅化局部）；蓝近 open-top `tarp_canvas` 蓝域推断 |
| 3 | `rust_red` | matte_industrial | (0.55, 0.20, 0.16, 1.0) | (0.55, 0.20, 0.16, 1.0) | (0.18, 0.19, 0.21, 1.0) | 氧化红 / 铁红工业涂装；近 hatch `hatch_accent`(0.72,0.18,0.14) 红域推断、整体压暗 |
| 4 | `weathered_grey` | weathered | (0.45, 0.46, 0.47, 1.0) | (0.40, 0.40, 0.41, 1.0) | (0.40, 0.24, 0.16, 1.0) | 褪色灰旧箱 + 角件/锁杆锈棕 scuff；accent 偏锈棕表面磨损 |
| 5 | `container_green` | matte_industrial | (0.16, 0.36, 0.26, 1.0) | (0.16, 0.36, 0.26, 1.0) | (0.18, 0.19, 0.21, 1.0) | 经典集装箱墨绿涂装；暗硬件角件 |
| 6 | `safety_orange` | matte_industrial | (0.80, 0.38, 0.10, 1.0) | (0.80, 0.38, 0.10, 1.0) | (0.18, 0.19, 0.21, 1.0) | 安全橙 / 危险品箱涂装；暗硬件角件 |
| 7 | `heavy_rust` | heavily_weathered | (0.46, 0.26, 0.18, 1.0) | (0.36, 0.20, 0.14, 1.0) | (0.20, 0.15, 0.12, 1.0) | 重度锈蚀斑驳报废箱；body 锈棕、doors 更深锈、accent 暗锈；整体偏暗偏棕 scuff |
| 8 | `fresh_glossy_blue` | glossy | (0.08, 0.30, 0.58, 1.0) | (0.08, 0.30, 0.58, 1.0) | (0.85, 0.86, 0.88, 1.0) | 出厂全新高光蓝；亮镀锌角件/锁杆（accent 近 `curtain_steel`(0.82,0.84,0.86) 亮钢域）|
| 9 | `two_tone_blue_grey` | matte_industrial | (0.12, 0.34, 0.56, 1.0) | (0.62, 0.64, 0.66, 1.0) | (0.18, 0.19, 0.21, 1.0) | 双色：蓝箱体 + 灰货门（doors 锚 5★ `grey_steel`）；暗硬件 |
| 10 | `reefer_white` | semi_gloss | (0.92, 0.93, 0.94, 1.0) | (0.88, 0.89, 0.90, 1.0) | (0.30, 0.31, 0.33, 1.0) | 冷藏箱半光洁净白（reefer）；smooth_reefer 壁面尤配；accent 略浅暗钢（机组面板色）|

实现注记：`PALETTE_STYLES`（10 项）为模块级常量；`config_from_seed` 中 `palette_style = rng.choice(PALETTE_STYLES)`，按表查 `(body_rgba, doors_rgba, accent_rgba, finish)` 整组发射 material（沿用各 5★ 样本 `model.material(name, rgba=...)` 命名族：body→`*_steel` / doors→门面 material / accent→`dark_hardware` 类）。finish 仅作为 material 光泽/磨损语义标签（哑光/褪色/重锈/高光/半光）与 weathered 系的色相偏移，**不新增 part / joint / slot**。两色（two_tone）与 reefer 仅 doors↔body RGBA 取不同行，仍是同一 palette 轴。

## Multiplicity / Copy Logic

本类有 **1 根模板级复制轴**（door_count），外加若干 **length/height 派生的次级肋/片复制层**（非独立采样轴，随尺寸自适应，不进 slot_choices）。

### 轴 1：door_count（货门叶片数 —— door_closure ∈ swing 门族时生效）
- `count_param`：`door_count`
- `N_range`：**[1, 4]**（本小类本轴产品域；测试偏小：1=single_swing、2=parent 双扇、4=n4 多叶已覆盖；上界 4 由叶宽不等式封顶，门太窄不真实）
- sampling domain（权重档）：N=2 高频（~55%，ISO 标准双扇是主形态）、N=1 中频（~25%，单扇）、N=3 低频（~10%）、N=4 稀有（~10%）；测试偏小、产品全程 [1,4]
- copied object：单个货门叶片 `door_i`（波纹门板 `_corrugated_door_panel` + `rod`(N=1 时 4 根 / N≥2 时 1-2 根/叶) + `keeper_i_j` + cam `handle` 链）
- naming：`door_i` / `body_to_door_i` / `handle_i`(或 `handle_{l/r}{ridx}`) / `door_i_to_handle_i`；保持 parent/n4 命名族
- placement：沿端口（+X）等宽分割 `slot_y_max = y_open_max - i·leaf_w`；偶 index +Y 铰、奇 index -Y 铰（交替）；N>2 时 body 发射中柱 `mullion` 作内铰点
- joint policy：每叶独立 `body_to_door_i` REVOLUTE 绕各自竖直铰边（axis=(0,0,±1) per-leaf），统一 effort=200/velocity=2/limits=0..door_open_limit；非 mimic（n4 test L448-456 断言每叶独立 joint）
- source/gating：n4 L232-290（loop）/ single L234（N=1）/ parent L201-205（N=2）；仅 swing 门族（double/single/n_doorleaves）暴露此轴；roll_up（固定 1 帘）/ side_access（固定 2 侧门）不暴露 door_count（其 module 名即固定了机构数）

### 次级派生复制层（非 slot_choices 轴，随尺寸自适应）
- corrugation 竖肋：`_corrugated_wall` 内 `n = max(1, int(length_x/CORR_PITCH))`，由 body_len & corr_pitch_scale 派生（parent L63）
- louver 百叶片：`_louvered_wall` 内 `n_slats = max(1, int(slat_field_h/LOUVER_PITCH))`，由墙高派生（louver L102）
- 卷帘 slat：roll_up `N_SLATS=22` 由 OPENING_H 派生（roll_up L56,L268）
- open-top bow：`N_BOWS=5` 由 body_len 派生（open-top L56,L73,L480）
- 角件 `corner_i`：固定 8（ISO 角件恒为 8，不可变）

这些次级层不进 `slot_choices_for_seed`（不改拓扑等价类，只改细节密度），在 resolve 内按 span/pitch 解析。

## 拓扑多样性审计

总组合数：door_closure(5) × roof_top(3) × wall_surface(3) = **45**（slot 笛卡尔积下界）。
叠 door_count multiplicity（swing 门族 3 个 module × N∈{1,2,3,4} 在 swing 内放大）后采样空间更大：仅 swing 门族即 3×4=12 个 (module,N) 拓扑变体，全轴 (12 swing 变体 + roll_up + side_access) × roof(3) × wall(3) = **126** 个 distinct 拓扑等价类。

仅 door_closure(5) × roof_top(3) = **15 ≥ 10** 已可过门控；叠 wall_surface 与 door_count 后充裕。

理由：本类拓扑多样性来源充裕——door_closure(5) × roof_top(3) 笛卡尔积即 15 distinct，远超 10；door_closure 引入 REVOLUTE +Z swing（含 N=1/2/3/4 不同 part count）/ PRISMATIC +Z roll-up（curtain 单 part + 导轨/卷筒）/ +Y 侧壁 swing（接口点位从 +X 端移到 +Y 侧）等不同 joint 拓扑 + 不同 part count + 不同 root 接口面；roof_top 引入固定 visual / REVOLUTE -X 翻盖（roof_lid）/ REVOLUTE -X 掀弓（bow_hinged + tube 软篷）三种顶部拓扑；wall_surface 在 corrugated↔louvered↔smooth 间改 body 侧壁 mesh 拓扑。door_count 在 swing 门族内额外放大 part/joint 数量多样性。slot_choices 编入 (door_closure, roof_top, wall_surface, door_count)。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choices` 三个 named slot（加权，见 compatibility matrix 的少量 gating），door_closure ∈ swing 门族时再对 door_count 加权采样（小 N 偏多），再 uniform 各连续 scale（先 independent → 派生肋/片/帘/bow 数与从属尺度 → inequality 投影回缩长卧不变式 → conditional 解析叶宽上限）+ `rng.choice` palette_style。compatibility matrix 排除非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 126（45 slot 组合 × door_count multiplicity 放大）。≥300，满足建议。受真实词汇表约束的轴是 roof_top(3) 与 wall_surface(3)，但 door_closure(5) × door_count + roof × wall 已撑开 按 ≥300 report-only 口径观察。

Controlled local parameterization：见 §参数表的 6 个 scale（length / height / width / corr_pitch / door_open_limit / + 派生肋片数）。`length_scale`/`height_scale`/`width_scale` 为 independent 主尺度，肋/百叶/帘/bow 数为 equation 派生（`n = max(1,int(span/pitch))`），长卧不变式与叶宽为 inequality/conditional 在 resolve 投影/解析。这些 scale 不破坏 door joint origin（端口铰边 / +Y 侧壁 / 顶边 hinge）、captured-fit（post/track/eye/barrel/rod）、坐地或类别身份（X 始终最长）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choices` 三 named slot（加权）+ swing 时 door_count 加权 + uniform 各 scale + palette | slot_choices_for_seed 含 (door_closure, roof_top, wall_surface, door_count) 且与 build 一致 |
| compatibility matrix | (1) door_count 仅 door_closure ∈ {double_swing, single_swing, n_doorleaves} 暴露；roll_up/side_access 不采 door_count（固定机构数）。(2) `side_access_doors` 把端口移 +Y 侧壁 → body 改实端壁 `end_wall_p/n`（不发 +X 端口框），与 roof_top hatch/open-top（沿 +Y 长顶边）正交不冲突；侧门 +Y 外开与顶盖 +Y 上翻不在同一行程相撞（rest pose 均闭合）。(3) `roll_up_door` 需门洞框 `track_*`+`drum` → 与 corrugated/louvered/smooth 任意 wall 正交。(4) door_count=4 + width_scale 下限：叶宽不等式 `leaf_w ≥ 0.30` 在 resolve 解析，过窄则降 door_count 上限（不 gate 掉，保多样性）。(5) 各 door_closure / roof_top 互斥。45×door_count 组合近全合法，仅在 resolve 派生尺寸适配 | 无 floating / collision / 门穿箱 / 帘出导轨 / lid 穿顶 / joint 轴或 origin 错位 / 长卧身份破坏 |
| controlled local variation | 6 个 clamped scale + 派生肋/片/帘/bow 数，每 build 统一；长卧不变式 inequality 驱动 length_scale 回缩 | 比例变化不破坏 door joint origin / captured-fit / 坐地 / X 最长身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 门/帘/盖/弓/把手动作 + 坐地 + overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| door_closure | 5 | yes | yes | double_swing(REV+Z,N) / single_swing(REV+Z,N=1) / n_doorleaves(REV+Z,N≥3) / roll_up(PRIS+Z) / side_access(REV+Z@+Y) |
| roof_top | 3 | yes | yes | flat_solid(固定) / hatch_lid(REV-X 翻盖) / open_top_tarp(REV-X 掀弓+软篷) |
| wall_surface | 3 | yes | yes | corrugated(竖肋) / louvered_vents(横斜百叶+框) / smooth_reefer(平滑齐面) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (door_closure, roof_top, wall_surface, door_count) 四要素（door_count 仅 swing 门族）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`），seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；肋/百叶/帘/bow 数 equation 派生；长卧不变式 inequality 在 resolve 投影/回缩；叶宽 conditional 在 resolve 解析 door_count 上限
- compatibility matrix / gating：door_count 仅 swing 门族暴露；side_access 端口移 +Y 时 body 发实端壁；roll_up 发 track/drum；45×N 组合近全合法（无硬 gate-out），仅 resolve 派生尺寸适配
- 连续 scale clamp 后不破坏 door/lid/bow joint origin、captured-fit、坐地、X 最长身份
- 关键 joint：swing `body_to_door_*` REVOLUTE +Z (abs(axis[2])>0.99)；roll_up `body_to_curtain` PRISMATIC +Z；side `body_to_door_*` REVOLUTE +Z @ y≈W/2；hatch `body_to_roof_lid` REVOLUTE -X (abs(axis[0])>0.99)；open-top `body_to_bow_hinged` REVOLUTE -X；handle `door_to_handle_*` REVOLUTE +Z 有限 limit
- multiplicity：door_count 个 `door_i` 各有独立 `body_to_door_i`（非 mimic）；命名 door_i/handle_i；placement 等宽交替铰
- captured-fit：element-scoped `allow_overlap`（door_panel↔post / curtain↔track / slat↔header / lid_eye↔hinge_barrel / hinge_barrel↔hinge_ear / handle hub↔rod / handle hub↔door_panel / bracket↔top_rail）
- grandfather：所有 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- body 8× corner_i 角件恒存在；container 长卧不变式（X>Y+1 且 X>Z+1）每 seed 守

## Reject cases

- 用纯 Box 占位当箱体而无波纹/角件/锁杆货门 → 失类别身份（必须有 `_corrugated_wall` 竖肋 + 8× corner_i + door_closure 机构）。
- 容器变成直立柜（高>长）或小桌面箱 → 长卧不变式 FAIL（X 必须最长，米级）；混入 container_locker / container_box。
- door joint origin 放在箱底 / 任意点而非端口外铰边 / +Y 侧壁开口 / 顶边 hinge line 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 多叶门用 mimic / 共享单 joint 而非每叶独立 `body_to_door_i` → multiplicity 语义错（n4 断言每叶独立 joint）。
- door_closure rest pose 设成张开 / 帘升起 / 盖翻开而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- roll_up 帘出导轨 / 不发 track/drum，或 side_access 不改实端壁仍留 +X 端口框 → 几何穿模 / 双开口不真实。
- 给 captured-fit（post/track/eye/barrel/rod）补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把波纹 pitch / 颜色 / 材质 / 20ft↔40ft 尺寸当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette、尺寸是 controlled local param，不计 slot_choice）。
- door_count=4 + width_scale 下限致叶宽<0.30 未在 resolve 降上限 → 叶太窄穿模 / 不真实。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。9 record 全文读取（1 parent + 8 fork 变体）。3 槽 door_closure(5) × roof_top(3) × wall_surface(3) = 45 slot 组合，door_closure×roof_top=15 已过 ；叠 door_count multiplicity（swing 门族 N∈[1,4]）达 ~126 distinct 拓扑。door_closure 含 REVOLUTE +Z swing(N 复制) / PRISMATIC +Z roll-up / +Y 侧壁 swing；roof_top 含固定顶 / REVOLUTE-X 翻盖 / REVOLUTE-X 掀弓+软篷；wall_surface 含竖波纹/横斜百叶/平滑保温。palette_style **10 colorway**（iso_white / maersk_blue / rust_red / weathered_grey / container_green / safety_orange / heavy_rust / fresh_glossy_blue / two_tone_blue_grey / reefer_white），含显式 **material-finish 维度**（matte_industrial / weathered / heavily_weathered / glossy / semi_gloss），每 colorway = corrugated body + doors + accent(corner/rod/keeper/handle/decal) RGBA + finish，逐 seed `rng.choice` 整组取色（palette only，不计 slot_choice；RGBA 锚定 5★ white/grey/dark/hatch_red/tarp/curtain_steel，其余 ISO 真实涂装合理推断）。1 根 multiplicity 轴 door_count[1,4]（仅 swing 门族）+ 次级 length/height 派生肋/片/帘/bow 数。待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_corrugated_wall` / `_corrugated_end_wall` / `_corrugated_door_panel` / `_corrugated_side_door_panel` / `_louvered_wall`+`_louver_slat` / `_insulated_wall`+`_insulated_end_wall` / `_corrugated_lid_panel` / `_hinge_barrel`+`_lid_hinge_eye` / `_build_bow_mesh`+`_build_tarp_mesh`（tube_from_spline_points）/ `_curtain_slat` / `_drum_assembly` / `_corner_casting` / `_build_handle`（cam 把手 factory）全 module 公用，直接改编各源样本。
- door_count multiplicity：必须 `for i in range(door_count)` 生成 `door_i` + 各自 `body_to_door_i` REVOLUTE（非 mimic），偶/奇 index 交替铰，N>2 时 body 发 `mullion` 中柱作内铰点（见 n4 L201-203,L232-290）。
- captured-fit overlap：`run_container_shipping_container_tests` 里 element-scoped `ctx.allow_overlap`（door_panel↔post、handle hub↔rod、handle hub↔door_panel、curtain slat↔header、lid_eye↔hinge_barrel、hinge_barrel↔hinge_ear、bracket↔top_rail）——逐 door_closure/roof_top 候选复制对应 allow_overlap（见各变体 run_tests）。
- side_access：选中时 body 不发 +X 端口框（header/sill/post_p/n），改发实 `end_wall_p/n` + +Y 侧壁开口框 `post_0/1`（见 side L178-203）。
- roll_up：选中时 body 发 `track_p/n` 导轨 + `drum` 卷筒；curtain 单 part PRISMATIC +Z（见 roll_up L242-292）。
- 长卧不变式：`resolve_config` 投影 `length_scale` 使 `L·length_scale > max(W·width_scale, H·height_scale) + 1.0`，保 X 最长身份每 seed 守。
- 参考模板：`agent/templates/Container_Jar.py`（同大类 parallel_children + 主开合机构槽 + grandfather captured-fit 骨架）；含 multiplicity 轴的模板（如栅栏/购物篮 N 复制）参考其 `slot_choices_for_seed` 编入 N + 加权小 N 采样 + per-copy 独立 joint。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | ROOT/A/B/C | body + double_swing_doors + flat_solid + corrugated | rec_white-twenty-foot-...0e395b54 | body L135-188 / `_corrugated_wall` L55-70 / `_corrugated_door_panel` L87-117 / `body_to_door_*` L233-243 / `handle_*`+`door_to_handle` L274-305 / `roof` L146-148 | 箱体 root 基线 + 双扇侧铰门基线 + cam 把手 + 固定平顶 + 竖波纹壁 |
| S2 | A(mult) | n_doorleaves (door_count 轴) | rec_container_shipping_container_var_n4_doorleaves | `for i in range(DOOR_COUNT)` L232-290 / `body_to_door_i` L258-268 / `_build_handle` L113-144 / `mullion` L201-203 | door_count N=4 多叶复制轴 + handle factory + 中柱内铰 |
| S3 | A | single_swing_door (door_count=1) | rec_container_shipping_container_var_single_swing_door | 单 `door` L199-204 / `body_to_door` L218-228 / 4× rod loop L236-289 | 单扇满宽门 N=1 |
| S4 | A | roll_up_door | rec_container_shipping_container_var_roll_up_door | `curtain`+`slat_i` L260-279 / `body_to_curtain` PRISMATIC L282-292 / `track_*` L242-246 / `_drum_assembly` L130-168 | 卷帘门 PRISMATIC +Z 竖升机构 |
| S5 | A | side_access_doors | rec_container_shipping_container_var_side_access_doors | `door_0/1` L231-237 / `body_to_door_*` +Y L246-257 / `_corrugated_side_door_panel` L102-128 / `end_wall_p/n` L178-185 / `post_0/1` L200-203 | +Y 侧壁开口长侧门对（接口移侧壁）|
| S6 | B | hatch_lid | rec_container_shipping_container_var_hatch_lid | `roof_lid` L428-434 / `body_to_roof_lid` REVOLUTE -X L460-470 / `_corrugated_lid_panel` L134-173 / `top_rail_*`+`hinge_barrel_i`+`latch_rail` L249-276 / `_hinge_barrel`+`_lid_hinge_eye` L180-192 | 后铰波纹翻顶盖 + 顶框 + 铰链桶/眼 captured-fit |
| S7 | B | open_top_tarp | rec_container_shipping_container_var_open_top_tarp | 固定 `bow_i`(`_build_bow_mesh`) L478-487 / `tarp_main`(`_build_tarp_mesh`) L494-503 / `bow_hinged`+`body_to_bow_hinged` REVOLUTE -X L597-661 / `hinge_ear_0/1` L665-672 | 开顶弧弓+软篷 + 1× 可掀弓 + tube_from_spline 软篷 helper |
| S8 | C | louvered_vents | rec_container_shipping_container_var_louvered_vents | `_louvered_wall` L72-109 / `_louver_slat`(35° 斜置) L61-69 | 横向斜置百叶通风侧壁（自适应 n_slats）|
| S9 | C | smooth_reefer | rec_container_shipping_container_var_smooth_reefer_panel | `_insulated_wall` L56-63 / `_insulated_end_wall` L66-70 | 平滑保温齐面板（冷藏式无肋）|
