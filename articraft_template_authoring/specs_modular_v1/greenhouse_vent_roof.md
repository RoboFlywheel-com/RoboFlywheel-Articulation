# greenhouse_vent_roof (Agricultural / Greenhouse vent roof) — Modular Spec

> 来源小类：`Agricultural / Greenhouse vent roof`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Agricultural__Greenhouse_vent_roof.md`。
> **一段玻璃温室屋面（a glazed greenhouse ROOF SECTION，建筑构件），不是整栋温室，也不是普通窗 / 门。**
> 结构家族 = 坡屋面骨架（roof_frame）+ 玻璃格 + 一套可开启通风机构（vent）。**每个 seed 必须有 ≥1 个真实开启关节**（top-hinged 顶铰扇 revolute / louvre 百叶 revolute / ridge-flap 脊翻板 revolute / sliding 推拉板 prismatic）——纯固定玻璃屋面无开启件即出类。
>
> **同步状态**：本 spec 引用的 10 个 5 星样本（1 origin + 9 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5，workbench-only，category_slug=`greenhouse_vent_roof`。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一全文读完核对）。引用以 part / joint / helper **名字**为准（`roof_frame` / `_plane_xyz` / `_plane_box` / `vent_sash` / `roof_to_vent_sash` / `stay_arm` / `latch_handle` / `_build_vent_sash` / `louvre_blade_{i}` / `sliding_vent_panel` / `ridge_vent_flap` / `_build_arched_rake` / `glass_lower_{ci}_{ri}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `greenhouse_vent_roof` |
| template path | `agent/templates/greenhouse_vent_roof.py` |
| test path (optional) | `tests/agent/test_greenhouse_vent_roof_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root `roof_frame`（parallel parent）+ roof_geometry / glazing / frame_member 三个固定形态轴叠在 roof 上，**外加** vent_mechanism 主机构轴与其内含的 sash / louvre 多重性）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 origin + 9 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 10（**全部读完整 `model.py`**，不抽样；含每个样本的 `_plane_*` helpers、part 树、articulation 与 run_tests 的 allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 10/10 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **origin 是单坡铝框 + 单顶铰扇**：`roof_frame`（root，pitched 坡面 `_plane_xyz` 骨架 + 3×2 玻璃格 `glass_lower_{ci}_{ri}` + curb + 脊铰线 fixed 铰叶 / knuckle + EPDM seal + 装饰）+ `vent_sash` + `latch_handle` + `stay_arm`，3 个 REVOLUTE（`roof_to_vent_sash` 顶铰 axis=(0,-1,0)、`sash_to_latch`、`sash_to_stay_arm`）。**origin 只有 1 个手写 sash，sash 计数多重性需 loop 重写成 `_build_vent_sash(i)`**（sash_x2 / sash_x3 已给出该循环）。
- **roof_geometry 轴**（Slot A，③ Volumetric Envelope Form）：mono_pitch（origin，单 `_plane_xyz` 坡）/ even_span（`roof_span`，水平 ridge cap + `_right_plane_xyz`/`_left_plane_xyz` 两镜像坡）/ curved_eave（`roof_curved_eave`，`_build_arched_rake` 用 `sweep_profile_along_spline` 造弓形拱檐 mesh + `arch_purlin`）。三者**玻璃 / curb / 脊铰 / 机构都仍在同一 `_plane_xyz` 主坡系**，roof_geometry 只改 rake / 椽 + 是否加镜像左坡 → 与所有机构正交。
- **vent_mechanism 轴**（Slot B，①/② 主机构，改 part 树与 joint 拓扑）：top_hinged_prop（origin，顶铰扇 + stay + latch，REVOLUTE）/ louvre_bank（`vent_louvre`，`louvre_blade_{i}`×6 各一 REVOLUTE）/ sliding_panel（`vent_sliding`，`sliding_vent_panel` 沿坡 **PRISMATIC** + latch）/ ridge_flap（`vent_ridge_flap`，`ridge_vent_flap` 长脊翻板 REVOLUTE + stay + latch）。
- **glazing 轴**（Slot C，③ Planar Boundary Form）：multi_pane_grid（origin，3×2 小玻璃格 + `transom_mid` + `mullion_lower_{i}`）/ single_pane（`glazing_single_pane`，2 大 `glass_sheet_{i}` rafter-to-rafter，去掉 `transom_mid`/`mullion_lower`）。
- **frame_member 轴**（Slot D，③ Macro / ⑥）：aluminium_box（origin，薄铝盒杆）/ timber_bar（`frame_timber`，加厚木截面杆 + `putty_*` 油灰嵌缝 + 天然木材质）。
- **sash 多重性**（Slot B 内子轴）：`_build_vent_sash(i)` → `vent_sash_{i}` + 独立 `roof_to_vent_sash_{i}` REVOLUTE + `stay_arm_{i}` + `latch_{i}`，跨坡 Y 平铺（sash_x2 N=2 / sash_x3 N=3）。
- **louvre 多重性**（Slot B 内子轴）：`louvre_blade_{i}` N 片各一 REVOLUTE（`vent_louvre` N=6）。

## 核心身份

一段**玻璃温室坡屋面**（Agricultural / Greenhouse vent roof）：pitched 铝 / 木框骨架 `roof_frame`（脊 `ridge_rail`、檐 `eave_rail`、rake 椽、`transom_*` 横档、`mullion_*` 竖档）托一片玻璃格 / 大玻璃，中段留一个**可开启通风口**（curb sill + jambs 框边），口内装一套开启机构：**顶铰扇**（top-hinged sash 绕脊 REVOLUTE 上掀，folding scissor `stay_arm` 撑开 + `latch_handle` 钩闩）/ **百叶**（louvre 一排 `louvre_blade_{i}` 各绕横轴 REVOLUTE 翻转）/ **推拉板**（`sliding_vent_panel` 沿坡 PRISMATIC 滑出）/ **脊翻板**（`ridge_vent_flap` 长板绕脊 REVOLUTE 上掀）。屋面几何 = 单坡 / 对称双坡 / 弓形拱檐；玻璃 = 多格 / 大板；框材 = 铝盒杆 / 木杆 + 油灰。默认成熟域 = roof_geometry × vent_mechanism × glazing × frame_member × 机构多重性 的一段屋面 bay。活动语义 = **通风口开启**（≥1 个 revolute 或 prismatic）。

不该混入：
- **整栋温室 / 玻璃房建筑**——本类是一段**屋面构件**（roof section），不建墙 / 门 / 地基 / 整栋体量。
- **普通窗（window / sliding_window）**——窗是竖直墙上的采光洞口；本类是**倾斜屋面**上的通风口，主身份在 pitched roof_frame + 玻璃坡面 + 沿脊 / 沿坡的开启机构。
- **天窗 / 屋顶舱盖（skylight / roof hatch / trap door）单铰小盖**——虽同为屋面开启件，但缺温室的**格状玻璃坡面 + 铝 / 木玻璃杆骨架 + 通风机构**这套身份；本类是农业温室通风屋面。
- **百叶窗 / 遮阳帘（blind / shutter）**——louvre 候选借百叶形态，但整体仍是温室坡屋面 bay，不是室内窗帘。

## 槽位 + 候选模块表

> **建模注记**：`roof_geometry`（Slot A）是**同一主坡 `_plane_xyz` 系上的椽 / 檐几何形态**（单坡 / 双坡 / 拱檐），由 roof-geometry helper 决定，不改动玻璃 / curb / 脊铰 / 机构的坐标系 → 与 B/C/D 正交。`vent_mechanism`（Slot B）才是改 part 树 / joint 拓扑的主轴。`glazing`（C）改 roof 固定玻璃场的 Planar 形态，`frame_member`（D）改杆截面 / 材质 + 油灰。

### Slot A：roof_geometry（屋面几何 —— ③ Primary Form Family / Volumetric Envelope）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| mono_pitch（基线） | forked_anchor | rec_use-the-attached-...32a39adc（origin）| `_plane_xyz` L29-37 / `ridge_rail`/`eave_rail`/`rake_rail_0/1` L112-115 | Volumetric Envelope Form | eligible if compatible | 单个 pitched 坡面：`_plane_box(ridge_rail/eave_rail)` + 直 `rake_rail_0/1` 两椽；主坡 `_plane_xyz` 系 |
| even_span（对称双坡） | forked_anchor | rec_ghvent_var_roof_span | `_right_plane_xyz`/`_left_plane_xyz` L33-46 / 水平 `ridge_rail` cap L144-146 / 右坡 rails L149-154 / 左坡镜像 `eave_rail_left`+`rake_rail_left_*`+`transom_left_*`+`mullion_left_*`+`glass_left_*` L227-249 | Volumetric Envelope Form | eligible if compatible | 中央水平脊帽 + 两镜像坡（右坡带机构，左坡满玻璃）；主坡系与 mono 一致，只叠一个镜像左坡 |
| curved_eave（弓形拱檐） | forked_anchor | rec_ghvent_var_roof_curved_eave | `_arch_path` L88-101 / `_build_arched_rake`（`rounded_rect_profile`+`sweep_profile_along_spline`+`mesh_from_geometry`）L104-116 / 拱椽 `rake_arch_{idx}` L152-159 / `arch_purlin_{i}` L162-171 | Macro Surface Construction | eligible if compatible | 椽用弓形 mesh 扫掠（**Lathe/loft 曲面，不得降级成 Box**）+ 拱檩；玻璃 / curb / 机构仍在直 `_plane_xyz` 平面 |

### Slot B：vent_mechanism（开启机构 —— **主机构槽**，决定活动 part 树与 joint 拓扑；含机构内多重性）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| top_hinged_prop（基线，N 扇）| forked_anchor | rec_use-...32a39adc（origin，N=1）+ rec_ghvent_var_sash_x2（N=2）+ rec_ghvent_var_sash_x3（N=3）| origin `vent_sash` L169-205 / `latch_handle` L208-214 / `stay_arm` L217-234 / 3×REVOLUTE L237-270 · sash_x2 `_build_vent_sash(model,bay_idx,...)` L89-229 + `_bay_v_center` L84-86 + loop L343-348 · sash_x3 `N_BAYS=3` L24 + loop L331-334 | eligible if compatible | 每扇顶铰 **REVOLUTE** `roof_to_vent_sash_{i}` axis=(0,-1,0) 上掀 + `stay_arm_{i}` 折撑（REVOLUTE）+ `latch_{i}`（REVOLUTE）；跨坡 Y 平铺 N 扇（`_build_vent_sash(i)`）|
| louvre_bank（一排百叶，N 片）| forked_anchor | rec_ghvent_var_vent_louvre（N=6）| `_build_louvre_blade(model,roof,i,...)` L83-134（panel+axle+bracket+edge_seal+bolt+REVOLUTE）/ roof `louvre_head_rail` L188 + `blade_bearing_{i}_{s}` L203-207 + `louvre_linkage_bar`+`linkage_tab_{i}` L210-216 / loop L239-240 | eligible if compatible | N 片 `louvre_blade_{i}` 各一 **REVOLUTE** `frame_to_louvre_blade_{i}` axis=(0,-1,0) 翻转；curb 上 `blade_bearing_{i}_{s}` 轴承 + 联动杆 |
| sliding_panel（推拉板，1 板）| forked_anchor | rec_ghvent_var_vent_sliding | `vent_rail_{i}`+lip+stop L165-174 / `sliding_vent_panel` L209-268（glass+rails+`slider_shoe_{s}_{e}`+pull handle）/ `latch_handle` L273-279 / **PRISMATIC** `roof_to_sliding_vent` axis=(1,0,0) L286-296 / `panel_to_latch` L299-307 | eligible if compatible | 单 `sliding_vent_panel` 沿坡 **PRISMATIC** 滑出（沿 `vent_rail_{i}` C 槽轨，`slider_shoe` 捕获）+ latch |
| ridge_flap（长脊翻板，1 板）| forked_anchor | rec_ghvent_var_vent_ridge_flap | flap curb L128-130 / 脊铰 4 叶 L142-146 / `ridge_vent_flap` L171-206（更宽 `FLAP_HALF=0.62`）/ `latch`+`stay` L209-232 / **REVOLUTE** `roof_to_ridge_flap` axis=(0,-1,0) L237-245 + `ridge_flap_to_latch`/`ridge_flap_to_stay_arm` L249-268 | eligible if compatible | 单条**沿脊长翻板** `ridge_vent_flap` 绕脊 **REVOLUTE** 上掀（比 sash 更宽 Y 跨度）+ stay + latch |

### Slot C：glazing（固定玻璃场形态 —— ③ Planar Boundary Form）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| multi_pane_grid（基线）| forked_anchor | rec_use-...32a39adc（origin）| `transom_mid`/`transom_low` L118-119 / `mullion_lower_{i}` L120-121 / `glass_lower_{ci}_{ri}` 3×2 格 + `glass_side_{i}` L136-140 | Planar Boundary Form | eligible if compatible | 下场 3×2 小玻璃格（`for ci: for ri:`）+ 中横档 + 竖档；密骨架多格 |
| single_pane（大玻璃板）| forked_anchor | rec_ghvent_var_glazing_single_pane | 去 `transom_mid`/`mullion_lower`，保 `transom_low` L119 / 2 大 `glass_sheet_0/1`（upper_u/lower_u rafter-to-rafter）L134-147 + `glass_side_{i}` 大条 | Planar Boundary Form | eligible if compatible | 2 张大 polycarbonate 板从椽到椽，单低横档分上 / 下板；少骨架大板 |

### Slot D：frame_member（框材截面 / 材质 —— ③ Macro Surface Construction + ⑥）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| aluminium_box（基线）| forked_anchor | rec_use-...32a39adc（origin）| 薄铝盒杆 `ridge_rail`(0.085,·,0.060)/`transom`(0.050,·,0.044)/`mullion`(·,0.042,0.040) L112-124 / sash rails(0.060/0.080 厚) L177-181 | Macro Surface Construction | eligible if compatible | 薄铝盒截面杆（金属），无油灰 |
| timber_bar（木杆 + 油灰）| forked_anchor | rec_ghvent_var_frame_timber | 加厚木杆 `ridge_rail`(0.095,·,0.068)/`transom`(0.058,·,0.052)/`mullion`(·,0.052,0.050) L117-134 / `putty_transom_*`/`putty_mullion_{i}` 油灰嵌缝 L136-143 / 加厚 sash rails(0.070/0.088) L192-196 + sash `putty_*` L200-205 | Macro Surface Construction | eligible if compatible | 更粗木截面杆（天然木）+ 玻璃 rebate 油灰嵌缝 `putty_*`（host-conformal 表面细节）|

> **候选数说明**：A=3、B=4 均 ≥3；C=2、D=2 降到 2 —— 原因：5 星样本池 glazing 只有 multi_pane_grid 与 single_pane 两种真实形态，frame_member 只有 aluminium 与 timber 两种真实框材（diamond-lap horticultural 玻璃与 steel-tube 框为 source map §排除项标注的模板外推，非样本支撑 → 不作候选，见 `AUTHORING.md` §A Rule 3）。两者各有 ≥2 结构不同候选，成立且非单候选 slot。

## 槽位图（slot graph）

pattern: mixed（root `roof_frame` 为共同 parent（parallel children）；roof_geometry / glazing / frame_member 是叠在 roof 上的固定形态轴；vent_mechanism 的活动 part 挂到 `roof_frame`，其内含 sash / louvre 多重性）

```
roof_frame (root; 由 roof_geometry 决定椽/檐几何 + glazing 决定固定玻璃场 + frame_member 决定杆截面/材质/油灰;
            中段留通风口 curb; 机构侧固定框(脊铰叶/knuckle | 百叶轴承 | 推拉轨 | flap curb) 也发在 roof_frame)
  │
  └── [vent_mechanism slot]  (四选一; 每 seed 必有 ≥1 开启关节)
        ├─ top_hinged_prop (N∈[1,3] 扇, 跨坡 Y 平铺; 每扇经 _build_vent_sash(i)):
        │     vent_sash_{i} ──[roof_to_vent_sash_{i}: REVOLUTE axis=(0,-1,0), origin=脊铰线]
        │       ├─ latch_{i}    ──[sash_{i}_to_latch_{i}:  REVOLUTE axis=(0,1,0), origin=扇下横档]
        │       └─ stay_arm_{i} ──[sash_{i}_to_stay_arm_{i}: REVOLUTE axis=(0,1,0), origin=扇下 mount tab]
        ├─ louvre_bank (N∈[4,8] 片):
        │     louvre_blade_{i} ──[frame_to_louvre_blade_{i}: REVOLUTE axis=(0,-1,0), origin=curb 轴承]
        ├─ sliding_panel (1 板):
        │     sliding_vent_panel ──[roof_to_sliding_vent: PRISMATIC axis=(1,0,0), origin=口顶 header 座]
        │       └─ latch_handle ──[panel_to_latch: REVOLUTE axis=(0,1,0)]
        └─ ridge_flap (1 板):
              ridge_vent_flap ──[roof_to_ridge_flap: REVOLUTE axis=(0,-1,0), origin=脊铰线]
                ├─ latch_handle ──[ridge_flap_to_latch:  REVOLUTE axis=(0,1,0)]
                └─ stay_arm     ──[ridge_flap_to_stay_arm: REVOLUTE axis=(0,1,0)]
```

接口点位与 joint 语义：
- **roof_geometry 接口**：mono/even/curved 都在 `_plane_xyz(r,u,v,w)` 主坡系上发脊 / 檐 / 玻璃 / curb / 脊铰 / 机构；roof_geometry 只额外发（even_span：水平 ridge cap + 镜像左坡；curved_eave：拱椽 mesh + 拱檩，**拱檩只放在下场 u>vent_u1 处，避免开启扇上掀时穿模**）。三者 `ridge_rail` 都在脊峰、都供机构脊铰 / seating 用同名 `ridge_rail` allow_overlap。
- **vent_mechanism 接口（四选一，挂 root `roof_frame`）**：
  - top_hinged_prop：脊铰线 `fixed_hinge_leaf_*`/`fixed_hinge_knuckle_*`/`hinge_pin_*`（roof）↔ `sash_hinge_leaf/knuckle`（sash）captured-pin；`roof_to_vent_sash_{i}` REVOLUTE axis=(0,-1,0)，origin=`_plane_xyz(r,0,v_center,0.064)`（落在脊铰硬件上），lower=0 闭合 / upper≈1.05 上掀。stay / latch 各挂 sash（REVOLUTE，captured-pin）。
  - louvre_bank：curb `blade_bearing_{i}_{s}`（roof）↔ 叶 `axle`（captured-pin）；`frame_to_louvre_blade_{i}` REVOLUTE axis=(0,-1,0)，origin=`_plane_xyz(r, u_pivot_i, 0, BLADE_PIVOT_W)`，lower=0 / upper≈0.7。
  - sliding_panel：roof `vent_rail_{i}` C 槽 ↔ 板 `slider_shoe_{s}_{e}`（captured-slide）；`roof_to_sliding_vent` PRISMATIC axis=(1,0,0)，origin=`_plane_xyz(r,vent_u0,0,PANEL_W)`（口顶座），lower=0 / upper≈travel；latch 挂板（REVOLUTE）。
  - ridge_flap：脊铰线（4 叶 knuckle）↔ 翻板铰叶（captured-pin）；`roof_to_ridge_flap` REVOLUTE axis=(0,-1,0)，origin=脊铰线，lower=0 / upper≈1.05；stay / latch 挂翻板（REVOLUTE）。
- **glazing 接口**：固定玻璃场发在 roof（下场 u>vent 带）；multi_pane_grid 发 3×2 `glass_lower_{ci}_{ri}` + 中横档 + 竖档，single_pane 发 2 大 `glass_sheet_{i}` + 单低横档。与机构正交（机构占中段 vent 带，玻璃占下场）。
- **frame_member 接口**：aluminium_box 用薄铝截面（金属材质），timber_bar 用加厚木截面 + 玻璃 rebate 油灰 `putty_*`（host-conformal 贴玻璃 / 杆面表面细节，Rule 4）。
- **mating policy**：所有脊铰是 pin-in-knuckle captured-pin、louvre axle-in-bearing captured-pin、slider shoe-in-rail captured-slide、stay / latch pin-in-tab captured-pin —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry`(0.015) 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有扇 / 叶 / 翻板 / 板 q=0 闭合（贴坡面）；stay q=0 收拢；latch q=0 钩合。
- **互斥 / 可选 / 派生**：vent_mechanism 四候选互斥（一次只一种机构）；sash 多重性仅 top_hinged 有效、louvre 多重性仅 louvre 有效（见 §8 / §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / roof_geometry — mono_pitch（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | roof_frame visual：`ridge_rail`/`eave_rail`/`rake_rail_0/1`（`_plane_box`）| origin L112-115 |
| internal joints | 无（roof 是 root）| — |
| upstream interface | root | — |
| downstream interface | 主坡 `_plane_xyz` 面 + 脊峰 `ridge_rail`（供玻璃 / curb / 机构接入）| origin L29-37 |

### Slot A / roof_geometry — even_span
| emits | 描述 | 来源 |
|---|---|---|
| parts | 水平 `ridge_rail` cap + 右坡 `eave_rail_right`/`rake_rail_right_*` + 镜像左坡 `eave_rail_left`/`rake_rail_left_*`/`transom_left_*`/`mullion_left_*`/`glass_left_{ci}_{ri}` | roof_span L144-154, L227-249 |
| internal joints | 无 | — |
| downstream interface | 右坡（=主坡 `_plane_xyz`）供机构；左坡满玻璃无机构 | roof_span L33-46 |

### Slot A / roof_geometry — curved_eave
| emits | 描述 | 来源 |
|---|---|---|
| parts | 拱椽 `rake_arch_{idx}`（`sweep_profile_along_spline` mesh，Rule 3 不得降 Box）+ `arch_purlin_{i}`（仅下场 u>vent_u1）| roof_curved_eave L104-171 |
| internal joints | 无 | — |
| downstream interface | 直 `_plane_xyz` 面仍供玻璃 / curb / 机构；拱只在 rake / 檩 | roof_curved_eave L88-116 |

### Slot B / vent_mechanism — top_hinged_prop（N 扇）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每扇 `vent_sash_{i}`（`vent_glass`+`sash_top/bottom_rail`+`sash_stile_0/1`+`sash_glazing_bar`+`sash_drip_lip`+`sash_gasket_*`+`sash_hinge_leaf/knuckle`+`stay_mount_tab`+`sash_corner_plate`）+ `latch_{i}` + `stay_arm_{i}`；roof 侧脊铰 `fixed_hinge_leaf/knuckle`+`hinge_pin`+curb+seal | origin L143-205 / sash_x2 `_build_vent_sash` L89-229 |
| internal joints | `roof_to_vent_sash_{i}` REVOLUTE axis=(0,-1,0)（lower=0/upper≈1.05）+ `sash_{i}_to_latch_{i}` REVOLUTE axis=(0,1,0) + `sash_{i}_to_stay_arm_{i}` REVOLUTE axis=(0,1,0) | origin L237-270 / sash_x2 L196-227 |
| upstream interface | `sash_hinge_knuckle`↔roof `fixed_hinge_knuckle`/`hinge_pin` captured-pin（脊铰线）| origin L143-147, L190-192 |

### Slot B / vent_mechanism — louvre_bank（N 片）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `louvre_blade_{i}`（`panel`+`axle`+`bracket_{s}`+`edge_seal`+`bolt_{s}`）×N；roof 侧 `louvre_head_rail`+`blade_bearing_{i}_{s}`+`louvre_linkage_bar`+`linkage_tab_{i}`+curb+`sill_weather_seal` | vent_louvre `_build_louvre_blade` L83-134 / roof L188-216 |
| internal joints | `frame_to_louvre_blade_{i}` REVOLUTE axis=(0,-1,0)（lower=0/upper≈0.7）×N | vent_louvre L124-132 |
| upstream interface | 叶 `axle`↔roof `blade_bearing_{i}_{s}` captured-pin | vent_louvre L299-308 |

### Slot B / vent_mechanism — sliding_panel（1 板）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_vent_panel`（glass+rails+`sash_stile_0/1`+`slider_shoe_{s}_{e}`+`slide_pull_handle`+gaskets）+ `latch_handle`；roof 侧 `vent_rail_{i}`+`vent_rail_lip_{i}`+`vent_rail_stop_*`+`vent_header`+seals | vent_sliding L165-174, L209-279 |
| internal joints | `roof_to_sliding_vent` PRISMATIC axis=(1,0,0)（lower=0/upper≈travel）+ `panel_to_latch` REVOLUTE axis=(0,1,0) | vent_sliding L286-307 |
| upstream interface | 板 `slider_shoe_{s}_{e}`↔roof `vent_rail_{i}`/`vent_rail_lip_{i}` captured-slide | vent_sliding L322-341 |

### Slot B / vent_mechanism — ridge_flap（1 板）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ridge_vent_flap`（`flap_glass`+`flap_*_rail`+`flap_stile_*`+`flap_hinge_leaf/knuckle`+`stay_mount_tab`+`flap_gasket_*`）+ `latch_handle` + `stay_arm`；roof 侧 4 `fixed_hinge_leaf/knuckle`+`hinge_pin`+`flap_curb_*`+seal | vent_ridge_flap L128-206 |
| internal joints | `roof_to_ridge_flap` REVOLUTE axis=(0,-1,0)（lower=0/upper≈1.05）+ `ridge_flap_to_latch` + `ridge_flap_to_stay_arm`（REVOLUTE axis=(0,1,0)）| vent_ridge_flap L237-268 |
| upstream interface | 翻板 `flap_hinge_knuckle`↔roof `fixed_hinge_knuckle`/`hinge_pin` captured-pin | vent_ridge_flap L142-146, L188-190 |

### Slot C / glazing — multi_pane_grid（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | roof visual：`transom_mid`+`transom_low`+`mullion_lower_{i}`+`glass_lower_{ci}_{ri}`(3×2)+`glass_side_{i}` | origin L118-140 |

### Slot C / glazing — single_pane
| emits | 描述 | 来源 |
|---|---|---|
| parts | roof visual：仅 `transom_low` + 2 大 `glass_sheet_0/1`（rafter-to-rafter）+ 大 `glass_side_{i}`；去 `transom_mid`/`mullion_lower` | glazing_single_pane L119, L134-147 |

### Slot D / frame_member — aluminium_box / timber_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | 决定所有杆截面尺寸 + 材质（铝金属 / 天然木）；timber_bar 另发 host-conformal `putty_*` 油灰嵌缝（roof rebate + sash rebate）| origin L112-124,177-181 / frame_timber L117-143,192-205 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| roof_geometry | enum | mono_pitch / even_span / curved_eave | mono_pitch | choice | sampler 选；决定椽 / 檐几何（③ Envelope）| module table A |
| vent_mechanism | enum | top_hinged_prop / louvre_bank / sliding_panel / ridge_flap | top_hinged_prop | choice | sampler 选；主机构（互斥），每 seed 保 ≥1 开启关节 | module table B |
| glazing | enum | multi_pane_grid / single_pane | multi_pane_grid | choice | sampler 选；固定玻璃场形态（③ Planar）| module table C |
| frame_member | enum | aluminium_box / timber_bar | aluminium_box | choice | sampler 选；杆截面 + 材质 + 油灰 | module table D |
| sash_count (N_sash) | int | 声明域 [1,3]；sweep 采样域 [1,3]（偏小加权 1 高频 / 2 常见 / 3 长尾）| 1 | conditional→slot_choice | **仅 top_hinged 有效**；编入 slot_choice `n{N}`（拓扑维度）；其它机构 → n1 sentinel | sash_x2/x3 |
| louvre_count (N_louvre) | int | 声明域 [3,10]；sweep 采样域 [4,8]（product 全程 [3,10]，测试取 [4,8]）| 6 | conditional→slot_choice | **仅 louvre 有效**；编入 slot_choice `n{N}`；其它机构 → n0 sentinel | vent_louvre N=6 |
| palette_style | enum | mill_aluminium / white_painted / green_painted / natural_timber / galvanized_steel / anthracite_tinted（6）| mill_aluminium | palette+conditional | 材质 / 配色；**与 frame_member 联动**：timber_bar⟺natural_timber、aluminium_box⟺其余 5；frame 材质 + glass 材质都随之变 | 各样本材质 / frame_timber L99-101 |
| pitch | float | [0.32, 0.50]（≈18°–29°）| 0.42 | independent | 独立采样后 clamp；改 `_plane_xyz` 的 cos/sin，重导全部坡面元素 | roof_span L20 注释（0.26–0.61 档，收窄取 [0.32,0.50]）|
| ridge_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 `RIDGE_HEIGHT`（纯竖直偏移，安全）| origin L21 |
| open_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放各开启关节 `motion_limits.upper`（sash/flap 上掀角、louvre 翻角、slide 行程），clamp 到各安全上界 | 各样本 motion_limits |
| (—) | constraint | — | — | conditional | sash_count 仅 top_hinged 采样、louvre_count 仅 louvre 采样；其余机构置 sentinel（resolve 内解析）| §8 |
| (—) | constraint | — | — | conditional | palette_style 合法集依 frame_member（timber_bar→{natural_timber}；aluminium_box→其余 5）；resolve 内先定 frame_member 再定 palette | §9 |
| (—) | constraint | — | — | inequality | curved_eave 拱檩只在 u>vent_u1 下场发（避开开启扇上掀包络）；机构 vent 带 [vent_u0,vent_u1] 与下场玻璃场不重叠 | 接口 / clearance |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每 build 解析一次。scale 只动 pitch / 竖直高度 / 关节行程 —— **绝不改变 roof_geometry / vent_mechanism / glazing / frame_member / N 的拓扑**，也不改动玻璃格 / mullion 的 v 位（宽度定值，保 grid 一致）。

## Multiplicity / Copy Logic

**2 根 multiplicity 轴**（互斥激活，取决于 vent_mechanism）：

**轴 1 — sash_count（top_hinged 顶铰扇数）**
- **count_param**：`sash_count`（跨坡 Y 平铺的顶铰扇数）。
- **N_range**：声明产品域 **[1,3]**；sweep 采样域 **[1,3]**（偏小加权：1 高频 / 2 常见 / 3 长尾）。source map 建议 [1,6]，**收窄为 [1,3]** 因为：(a) 只有 N=1（origin）/2（sash_x2）/3（sash_x3）有样本；(b) N>3 时每扇 bay 半宽 = `VENT_HALF/N` < 0.115，`stay_mount_tab`(0.08 宽)/`latch`(0.11 宽) 装不进窄 bay，会撞 —— [4,6] 是 source map §排除项式的**降级留档**（需重调硬件才可造）。N=1 即 origin 单扇（不进循环）。
- **copied object**：单扇单元 `vent_sash_{i}`(+`latch_{i}`+`stay_arm_{i}`)，共享 `_build_vent_sash(model, i, r, mats)` helper 发射；N 个复用同一几何。
- **naming**：`vent_sash_{i}` / `latch_{i}` / `stay_arm_{i}`，joint `roof_to_vent_sash_{i}` / `sash_{i}_to_latch_{i}` / `sash_{i}_to_stay_arm_{i}`，`for i in range(N)`（sash_x2 L343-348 / sash_x3 L331-334 已用此结构）。
- **placement**：沿 Y **绝对式**等距平铺——bay 中心 `v_center = (2i-(N-1))·(VENT_HALF/N)`（`_bay_v_center` 式），每 bay 半宽 `VENT_HALF/N`；bay 间发 `vent_center_mullion` 隔断（N>1）。绝对式（每 i 的 v 由 N 与中心解析）是 N-不变前提。
- **joint policy**：每扇发独立 `roof_to_vent_sash_{i}` REVOLUTE + `sash_{i}_to_*`（stay/latch）REVOLUTE；统一 axis / range。captured-pin 脊铰 grandfather + element-scoped allow_overlap（照搬 sash_x2 run_tests L366-457）。
- **source/gating**：copy-logic 源取 sash_x2 `_build_vent_sash` L89-229；N=1 取 origin 单 `vent_sash`（等价 range(1)）。仅 vent_mechanism=top_hinged 激活；其它机构 sash_count 置 n1 sentinel。

**轴 2 — louvre_count（louvre 百叶片数）**
- **count_param**：`louvre_count`（curb 内一排百叶片数）。
- **N_range**：声明产品域 **[3,10]**；sweep 采样域 **[4,8]**（偏小加权）。source map N_range [3,10]，测试取 [4,8]（覆盖足够 distinct，且叶少不至 curb 内间距过密撞、叶多不至编译 / motion QC 关节爆炸）。
- **copied object**：单叶 `louvre_blade_{i}`（`panel`+`axle`+`bracket`+`edge_seal`+`bolt`），共享 `_build_louvre_blade(model, roof, i, r, mats)` helper；curb 上 per-i `blade_bearing_{i}_{s}`+`linkage_tab_{i}` 也循环发。
- **naming**：`louvre_blade_{i}` / joint `frame_to_louvre_blade_{i}` / roof `blade_bearing_{i}_{s}` / `linkage_tab_{i}`，`for i in range(N)`（vent_louvre L203-216, L239-240）。
- **placement**：沿坡 u **绝对式**等距——`u_pivot_i = vent_u0 + (i+0.5)·(BLADE_SPAN/N)`，`BLADE_PITCH_U = BLADE_SPAN/N`，叶长 = pitch−0.005（留缝）。
- **joint policy**：每叶发独立 `frame_to_louvre_blade_{i}` REVOLUTE axis=(0,-1,0)，统一 range（0..0.7）；axle-in-bearing captured-pin grandfather + allow_overlap（照搬 vent_louvre L299-318）。
- **source/gating**：源取 vent_louvre `_build_louvre_blade` L83-134 + roof loop L203-240。仅 vent_mechanism=louvre 激活；其它机构 louvre_count 置 n0 sentinel。

（跨轴共享的采样 helper 待第三个 multiplicity 模板出现再抽，不提前抽象；两轴互斥激活，一次只一根有效。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加 / 减会动的 part 或一条边 | **有** | vent_mechanism 改整套活动 part 树：top_hinged（sash+stay+latch，3 part/扇）/ louvre（N 叶，1 part/叶）/ sliding（panel+latch，2 part）/ ridge_flap（flap+stay+latch，3 part）。全 `forked_anchor`（origin + 4 vent 变体）|
| └ multiplicity | 同构件 ×N | **有** | 见 §8：sash_count [1,3]（sash_x2/x3）+ louvre_count [4,8]（vent_louvre）；两轴互斥激活，各 N 域 + 偏小权重 |
| ② 关节类型 | 图不变，某边换 type / 轴 | **有** | REVOLUTE（sash/louvre/ridge_flap 上掀 axis=(0,-1,0)、stay/latch axis=(0,1,0)）+ **PRISMATIC**（sliding axis=(1,0,0)）。全 `forked_anchor`；每种类型在 sweep 里都出现（四机构都采样）|
| ③ 主体形态家族 | 图 & 关节不变，换核心 part 可识别几何原型 | **有** | 登记两根 ③ slot：roof_geometry（A，Volumetric Envelope：单坡 / 双坡 / 弓拱檐，各标 form_subtype）+ glazing（C，Planar Boundary：多格 / 大板）；均 source-backed（origin/roof_span/roof_curved_eave/glazing_single_pane）。frame_member（D，Macro Surface：薄铝 / 粗木杆截面）亦 ③ 类。每 candidate 已标 `form_subtype` |
| ④ 表面装饰 | 原型不变，叠表面细节 | **有** | timber_bar 的 `putty_*` 玻璃 rebate 油灰嵌缝（host-conformal，贴杆 / 玻璃面逐段发，随 ③ frame 截面 / ⑤ 尺寸共形）+ 各机构的 `*_screw`/`*_bolt`/`hinge_leaf`/`gasket` fastener 细节。`record_only`（frame_timber L136-143,200-205 + 各样本 screw 段）；派生顺序 ③→⑤→④ |
| ⑤ 尺寸 / 行程 | 离散不变，只连续改尺寸 / 行程 | **有** | pitch [0.32,0.50]、ridge_height_scale [0.90,1.12]、open_travel_scale [0.85,1.10]。关节运动包络（见下 §motion_test_plan）：sash/flap REVOLUTE axis=(0,-1,0) 上掀 [0,~1.05·scale]；louvre REVOLUTE [0,~0.7·scale]；sliding PRISMATIC axis=(1,0,0) 下滑 [0,~0.5·scale]；stay [−0.05,~0.9·scale]、latch [−0.4,0.4]。**每关节全程跑 `fail_if_parts_overlap_in_sampled_poses` + 至少 1 个 targeted `ctx.pose` 证开启方向**。`record_only` |
| ⑥ 涂装 | 几何不变，只改材质 / 颜色 | **有** | palette_style 6 档：mill_aluminium / white_painted / green_painted / natural_timber / galvanized_steel / anthracite_tinted；frame 材质 + glass 材质（clear vs anthracite 的 tinted glass）都变。材质大类覆盖 metal（铝 / 镀锌 / anthracite）+ painted（white/green）+ wood（timber）+ glass ≥ ceil(0.5×6)=3。`record_only`（各样本材质 + frame_timber timber/putty）|

**motion_test_plan**：top_hinged —— sampled collision（各 sash/stay/latch 关节 {0,lower,upper,mid}，max_pose_samples≤32 因 N×3 关节多）+ targeted `ctx.pose({roof_to_vent_sash_i:0.95})` 断言 open_top_z > closed+0.30。louvre —— sampled（N 叶各 {0,upper,mid}，max≤32）+ targeted `ctx.pose({frame_to_louvre_blade_i:upper})` 断言 blade top_z 上升。sliding —— sampled + targeted `ctx.pose({roof_to_sliding_vent:travel})` 断言板沿 +x 下滑且 z 降 = travel·sin(pitch)（留坡内）。ridge_flap —— sampled + targeted 断言 flap 上掀。captured overlap（脊铰 pin↔knuckle、louvre axle↔bearing、slider shoe↔rail、stay/latch pin↔tab、闭合扇 bed 到 ridge_rail/curb/seal）用 element-scoped `allow_overlap` 照搬各样本；stay↔roof 因 stay 悬在坡面**下方（室内侧）**，不与坡面玻璃相交。

**收尾自检**：0-9 seed 渲染须肉眼见 —— roof_geometry 三形态拉得开（单坡 / 双坡 / 拱檐）、四机构都出现且开启方向对、glazing 多格 vs 大板可辨、timber 粗木 + 油灰 vs 铝薄杆可辨、6 palette 都出现、关节开合全程不穿模。

## 拓扑多样性审计

总组合数：roof_geometry(3) × vent_mechanism(4) × glazing(2) × frame_member(2) × [sash N(3) | louvre N(5) | single(1)] ≈ 3×2×2×(3+5+1+1)=**120**（机构内多重性加权）。

仅 vent_mechanism(4) × roof_geometry(3) = **12**（含 REVOLUTE 顶铰 / louvre / ridge_flap + PRISMATIC sliding × 单坡 / 双坡 / 拱檐 的 joint-拓扑 × envelope 组合）≥ 10 已稳；叠 glazing / frame / N 后充裕。

理由：vent_mechanism 4 候选给真正 joint 拓扑差（1+ REVOLUTE 上掀 / N REVOLUTE 百叶 / PRISMATIC 推拉 / REVOLUTE 脊翻），roof_geometry 3 候选给 envelope 差，glazing / frame_member 各 2，两根 N 轴编进 slot_choice。**N 必须编入 `slot_choices_for_seed`**（`("sash_count", f"n{N}")` / `("louvre_count", f"n{N}")`），否则单 / 多扇在 slot_choice 无法区分。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` roof_geometry / vent_mechanism / glazing / frame_member，`rng.choice` palette（依 frame_member 合法集），再按 vent_mechanism 加权采对应 N（top_hinged→sash_count∈[1,3]、louvre→louvre_count∈[4,8]、否则无 N），再 uniform 采 pitch / ridge_height_scale / open_travel_scale。compatibility matrix 合法化组合。无 regression overrides（首版纯 procedural）。random sweep seeds 0-35 初轮 + 0-999 成熟审计；viewer 目检 0-9。

Topology target：120 组合采样空间下，1000-seed slot choice tuple distinct 预计接近组合上限（受真实结构词汇表约束）。低于 300 的说明：温室通风屋面真实结构 = roof_geometry(3) × vent_mechanism(4) × glazing(2) × frame(2) × N 这几组拓扑等价类；若严格按 whole-tuple distinct 计入 N 采样点（sash 3 + louvre 5）可达 ~120，接近 100，符合本小类真实结构上限（多样性靠离散 slot + N，非无限连续 scale）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：pitch（independent [0.32,0.50]，改坡角，重导 `_plane_xyz`）、ridge_height_scale（independent [0.90,1.12]，竖直偏移）、open_travel_scale（independent [0.85,1.10]，缩放各关节 upper，clamp 到各安全上界）。全部 `resolve_config` clamp。采样契约：先采离散 slot + palette（conditional 依 frame_member）+ N（conditional 依 vent_mechanism）→ 采 3 个 independent scale → clamp。无跨部件 equation 依赖（宽度 / 玻璃 v 位定值不随 scale 动，避免破 grid）；唯一 conditional 不等式 = curved_eave 拱檩只在下场发。这些 scale 不破坏 `_plane_xyz` 接口 / 脊铰 origin / captured 接口 / N 复制 / 类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四离散 slot + palette（依 frame）+ 按机构采 N，再 uniform 3 scale | slot_choices_for_seed 含 `("sash_count",n{N})`/`("louvre_count",n{N})` 且与 build 一致 |
| compatibility matrix | (1) **vent_mechanism × N**：sash_count 仅 top_hinged 采 [1,3]，louvre_count 仅 louvre 采 [4,8]，sliding/ridge_flap 无 N（sentinel）。 (2) **frame_member × palette**：timber_bar→palette=natural_timber（发 `putty_*`）；aluminium_box→palette∈{mill/white/green/galvanized/anthracite}（不发 putty）。 (3) **roof_geometry × vent_mechanism 正交**：机构都在主坡 `_plane_xyz` 系，任意 roof_geometry 可配任意机构；curved_eave 拱檩避开 vent 带（只发 u>vent_u1）以防开启扇上掀穿模。 (4) **glazing × 机构正交**：玻璃占下场，机构占 vent 带。 (5) ridge_flap 更宽（FLAP_HALF=0.62）→ side mullion 外移到 0.66、跳过 side glass。 | 无 floating / collision / 拱檩撞开扇 / 窄 bay 撞硬件 / 机构缺开启关节 / palette-frame 不符 |
| controlled local variation | pitch / ridge_height_scale / open_travel_scale 三 clamped scale，每 build 统一 | 比例变化不破 `_plane_xyz` 接口 / 脊铰 origin / captured / N / 身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-35 初轮 + corner；0-999 成熟审计 | axis_realization（四机构 / 三 roof / 两 glazing / 两 frame / N 直方图） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| roof_geometry | 3 | yes | yes | 单坡 / 双坡 / 拱檐（③ Envelope）|
| vent_mechanism | 4 | yes | yes | 顶铰 / 百叶 / 推拉(PRISMATIC) / 脊翻（主机构互斥）|
| glazing | 2 | yes | no | 多格 / 大板（池仅此二真实形态，降 2 有据）|
| frame_member | 2 | yes | no | 铝 / 木（池仅此二真实框材，降 2 有据）|
| sash_count | 3（{1,2,3}）| yes | yes | 仅 top_hinged；编 slot_choice |
| louvre_count | 5（{4..8}）| yes | yes | 仅 louvre；编 slot_choice |

## Validator
- `slot_choices_for_seed` 返回已实现 module 名，且含 `("sash_count",f"n{N}")` 与 `("louvre_count",f"n{N}")`（非激活轴用 sentinel n1/n0）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；seed=0 不特殊
- `resolve_config`：vent_mechanism 决定激活哪根 N（clamp sash→[1,3] / louvre→[4,8]）；frame_member 决定 palette 合法集；pitch/ridge_height/open_travel clamp；curved_eave 拱檩 gate 到下场；每 build 解析一次
- compatibility matrix / gating 阻止非法组合（N 错机构 / palette-frame 不符 / 拱檩撞开扇 / 窄 bay）
- 每 seed 必有 ≥1 非 fixed 开启关节（REVOLUTE 或 PRISMATIC）；机构主关节 axis / type 断言（sash/louvre/ridge_flap REVOLUTE axis≈(0,-1,0)；sliding PRISMATIC axis≈(1,0,0)）
- Rule 5：非 fixed 关节 → `fail_if_parts_overlap_in_sampled_poses` + 每机构 ≥1 targeted `ctx.pose` 证开启位移 / 方向
- captured-pin / slide：element-scoped `allow_overlap`（脊铰 pin↔knuckle / louvre axle↔bearing / slider shoe↔rail / stay·latch pin↔tab / 闭扇 bed 到 ridge_rail·curb·seal），照搬各样本 run_tests 段
- copied object 遵循 `vent_sash_{i}`/`louvre_blade_{i}` 命名 + 绝对式等距 placement + 共享 helper
- grandfather：所有 captured 接口省略 MatingContract，由 origin(0.015) + allow_overlap 守
- Rule 3：curved_eave 拱椽保 `sweep_profile_along_spline` mesh，**不得降级 Box**；连续 scale 不破接口
- 连续 scale clamp 后不破 `_plane_xyz` / 脊铰 origin / captured / N 复制 / 身份

## Reject cases
- 某 seed 无任何开启关节（纯固定玻璃屋面）→ 出类 FAIL（每 seed 必有 ≥1 revolute/prismatic 开启件）。
- 把 sash_count / louvre_count 当普通 int、不进 slot_choice → 单 / 多扇 slot_choice 同形，损失拓扑维度。
- curved_eave 拱椽降级成 Box（丢 `sweep_profile_along_spline`）→ 违反 Rule 3。
- curved_eave 拱檩发在 vent 带（u<vent_u1）→ 开启扇上掀撞檩，sampled-pose collision FAIL；拱檩须限下场。
- sash N>3 时每 bay 半宽 < 硬件宽度 → `stay_mount_tab`/`latch` 撞邻件；sash N 限 [1,3]。
- timber_bar 配非 natural_timber palette（或 aluminium 发 putty）→ palette-frame 不符；须 gate。
- 把脊铰 pin↔knuckle / slider↔rail / axle↔bearing 补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。
- 把不动的 `putty_*`/`screw`/`gasket`/`twine` 当独立 FIXED part → 违反 Rule 1（应 inline 为 roof / sash visual）。
- 机构 rest pose 设成张开而非 q=0 闭合 → current-pose 与目检不符。
- 机构主关节 origin 放坡面中心而非脊铰线 / 轴承 / 轨座 → `fail_if_articulation_origin_far_from_geometry`(0.015) FAIL。
- 把"整栋温室 / 普通窗 / 室内窗帘"语义混入 → 出类（本类是一段温室通风坡屋面构件）。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异。

## 与相邻类别的边界
- 不该混入：**整栋温室 / 玻璃房建筑**——本类是一段屋面构件（roof section），不含墙 / 门 / 地基 / 整栋体量。
- 不该混入：**普通窗（window / sliding_window）**——窗是竖直墙洞；本类是倾斜屋面上的通风口，主身份在 pitched roof_frame + 玻璃坡面。
- 不该混入：**天窗 / 屋顶舱盖 / trap door 单铰小盖**——缺温室格状玻璃坡面 + 玻璃杆骨架 + 通风机构身份。
- 不该混入：**百叶窗 / 室内遮阳帘（blind / shutter）**——louvre 候选借百叶形态，但整体仍是温室坡屋面 bay。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：确认 (1) sash N 收窄 [1,3]（N>3 窄 bay 撞硬件，[4,6] 降级留档）；(2) frame_member×palette 联动（timber⟺natural_timber）是否接受为 palette gating；(3) curved_eave 拱檩限下场以防开扇穿模；(4) roof_geometry×vent_mechanism 正交（机构都在主坡系）建模是否忠实；(5) glazing/frame_member 降 2 候选（池仅二形态，diamond-lap/steel-tube 为外推排除）是否接受。|

## 模板实现备注（可选）
- 共享 helper：`_plane_xyz(r,u,v,w)` / `_plane_box` / `_plane_cyl_y` / `_add_box` / `_add_cyl_y`（主坡系映射，全模块复用）；`_build_vent_sash(model,i,r,mats)`（sash 多重性）；`_build_louvre_blade(model,roof,i,r,mats)`（louvre 多重性）；`_build_arched_rake(r,v)`（curved_eave mesh）；`_roof_glazing_field`（glazing 分支）。
- captured 接口 allow_overlap：`run_greenhouse_vent_roof_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（origin L286-378 / sash_x2 L366-457 / vent_louvre L299-318 / vent_sliding L320-418 / vent_ridge_flap L283-359）。
- conditional 解析顺序：先采 vent_mechanism / roof_geometry / glazing / frame_member → 解析 palette（依 frame）→ 按机构采 N（sash/louvre）→ 采 pitch/ridge_height/open_travel → clamp。
- 材质 role-key（`mats` dict）：frame / frame_accent / hardware / glass / rubber / black_steel / bolt / jute / wire / putty（putty 仅 timber）；6 palette 各给 frame + glass 一套色，其余硬件色共享。
- 参考模板：`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + `("count",f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 helper 复用 + 兼容矩阵 gating + captured-pin element-scoped allow_overlap + palette dict 骨架，本类同构改编）；curved_eave mesh 参考 roof_curved_eave `sweep_profile_along_spline` 用法。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/D 基线 | mono_pitch + top_hinged(N=1) + multi_pane_grid + aluminium_box | rec_use-...32a39adc（origin）| `_plane_xyz` L29-37 / roof L108-167 / `vent_sash` L169-205 / `latch` L208-214 / `stay` L217-234 / 3×REVOLUTE L237-270 / allow_overlap L286-378 | 主坡系 + 顶铰扇 + 多格玻璃 + 铝框基线 + captured-pin 范式 |
| S1 | A | even_span | rec_ghvent_var_roof_span | `_right/_left_plane_xyz` L33-46 / ridge cap L144-146 / 左坡镜像 L227-249 | 对称双坡 envelope |
| S2 | A | curved_eave | rec_ghvent_var_roof_curved_eave | `_arch_path` L88-101 / `_build_arched_rake` L104-116 / 拱椽 L152-159 / 拱檩 L162-171 | 弓形拱檐 mesh 扫掠（Rule 3 保 mesh）|
| S3 | B | louvre_bank | rec_ghvent_var_vent_louvre | `_build_louvre_blade` L83-134 / roof bearings+linkage L188-216 / loop L239-240 | N 片百叶 REVOLUTE 机构 + 多重性源 |
| S4 | B | sliding_panel | rec_ghvent_var_vent_sliding | `vent_rail_{i}` L165-174 / `sliding_vent_panel` L209-268 / PRISMATIC L286-296 / allow_overlap L320-418 | 推拉板 PRISMATIC + 轨 / shoe captured-slide |
| S5 | B | ridge_flap | rec_ghvent_var_vent_ridge_flap | flap curb+脊铰 L128-146 / `ridge_vent_flap` L171-206 / REVOLUTE L237-268 | 长脊翻板 REVOLUTE + stay/latch |
| S6 | B（multiplicity）| sash_count N=2 | rec_ghvent_var_sash_x2 | `_bay_v_center` L84-86 / `_build_vent_sash` L89-229 / 中隔 mullion + per-bay curb/hinge/seal L276-312 / loop L343-348 / allow_overlap L366-457 | sash 多重性 copy-logic 源（跨坡平铺）|
| S7 | B（multiplicity）| sash_count N=3 | rec_ghvent_var_sash_x3 | `N_BAYS=3` L24 / `BAY_CENTERS` L30 / `_build_vent_sash` L88+ / loop L331-334 | sash N=3 多重性源 |
| S8 | C | single_pane | rec_ghvent_var_glazing_single_pane | `glass_sheet_0/1` rafter-to-rafter L134-147 / 去 transom_mid/mullion_lower | 大玻璃板 Planar 形态 |
| S9 | D | timber_bar | rec_ghvent_var_frame_timber | 加厚木杆 L117-134 / `putty_*` 油灰 L136-143,200-205 / 加厚 sash L192-196 / 木材质 L99-101 | 木框截面 + 油灰嵌缝（④ host-conformal）|
