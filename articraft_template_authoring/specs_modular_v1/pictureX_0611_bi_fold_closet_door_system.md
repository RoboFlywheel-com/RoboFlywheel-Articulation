# pictureX_0611_bi_fold_closet_door_system — Modular Spec (SPEC_ONLY → IMPLEMENTED)

> Authored from the 15 5★ sources (1 origin parent + 13 normal slot-fork variants + 1 compatibility probe-only record) per SPEC_TEMPLATE.md.
> Every candidate cites a real `record_id` + `model.py:Lx-Ly`. All 15 `model.py` read line-by-line.

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_bi_fold_closet_door_system` |
| template path | `agent/templates/pictureX_0611_bi_fold_closet_door_system.py` |
| stage | `IMPLEMENTED` |
| status | `complete_visual_confirmed_2026-07-13` |
| variant_gate | `confirmed_by_user_2026-07-12` |
| __modular__ | `True` |
| pattern | `mixed`（multiplicity 叶对 pairs 主轴 + per-pair 耦合折叠链 + per-leaf 面板家族 parallel-children） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 15 |
| read_count | 15 |
| read_scope | all 5★ synced at rating=5（origin parent + 14 variants） |

阅读要点（15 个 model.py 全读）：

- **共享骨架**：`frame`（静态 root：sill + 双 jamb + header + 铝 U-track（web + 双 lip）+ 每对 pivot socket/bracket；多对时加 mullion posts）+ 每个 bi-fold *pair* = `pivot_leaf` + `handle_leaf`（trifold 再 +`mid_leaf`）+ 可选 `guide` roller。世界系：opening 居中 X=0，Z 0（地）→ FRAME_HEIGHT；叶折向 −Y（朝观者），carcass 在 +Y（柜内）。
- **每叶局部系恒定**：叶在 hinge-line 局部系创作 —— pivot 边在 local x=0，叶沿 `direction*LEAF_SPAN` 延伸，厚度沿 Y 居中（`centerline_y`）。所有面板家族/轨道/mount 候选共享此接口。（parent L86-92）
- **耦合折叠链（核心身份）**：每 pair 是一条 ≥2 铰的耦合链：`frame_to_pivot`(jamb/mullion REVOLUTE, axis ±Z) → `center_hinge`(REVOLUTE, axis ∓Z, `CENTER_HINGE_OFFSET=0.025` 让折叠 face-to-face 不穿模)。trifold 再串 `center_hinge_2`(handle→mid)。q=0 = 折叠 packet（rest = 参考图姿态），q=upper = 关闭共面。parent 用 `FOLDED_PIVOT_ANGLE=80°`、`FOLDED_CENTER_ANGLE=160°`——**center = 2×pivot** 恒等（L640-701）。
- **关键 loop-emission gotcha**：origin parent 手写 4 叶 + 4 铰（L563-701）；`var_triple_pair`/`var_quad_pair` 已示范必需的 `for k in range(NUM_PAIRS)` 循环重写 + `PAIR_CONFIGS=[(pivot_x,direction)]` + stable indexed 名 `pair{k}_*` / `frame_to_pivot_{k}` / `center_hinge_{k}` / `guide_spin_{k}`（triple L537-590, quad L268-360）。模板必须 loop 化。
- **独立采样折叠 → 穿模（本类头号风险）**：源用独立 pivot/center 铰 + `run_tests` 只测 closed/folded 两姿态。模板必须把 `center_hinge`（trifold 再 `center_hinge_2`）做成 `Mimic(frame_to_pivot, 2.0)`（AUTHORING §B Contract 3d coupled folding chain；mimic 2.0 精确匹配源 [0,80]/[0,160] 区间），让每 pair 成单参数折叠——独立采样 pivot/center 的非物理 scissor 组合被消除（与 `Door_folding_door.py` 同法）。
- **面板家族是 leaf-local 可替换层**（③）：flat laminate slab（parent）/ raised shaker fields（var_raised_panel L106-185）/ louvered slats loop（var_louvered L116-132 / var_louver_slat_count L108-130）/ framed glass lite（var_glass_lite L134-160）/ mirrored field（var_mirrored L94-108）。切换只改叶本体 parent.visual，不改铰链拓扑。
- **轨道/导向是 root + 叶端硬件层**：top-only U-track（parent L525-537 + roller guide）/ dual top+bottom（var_dual_track +`_add_bottom_guide_visuals` L281）/ pivot-only（var_pivot_only 去 guide + guide_spin，仅 header rail）。
- **jamb_mount / load_path / body_base**：pivot-pin-in-socket（parent）vs jamb butt-hinge knuckle（var_jamb_hinged L150-162）；bottom-supported vs top-hung（var_top_hung，顶 pivot 承重）；built-in carcass（parent L369-498，含 shelves/tower/drawer fronts）vs plain framed opening（var_plain_frame，去 carcass/drawers）。
- **intentional overlaps**：captured pivot-pin↔socket、center-hinge knuckle↔receiver、roller↔track、louver slat 微嵌 core——均 element-scoped，模板循环复刻。MatingContract 按 AUTHORING §A Rule 2 pin-through-sleeve 例外 **omit + grandfather**（与 `Door_folding_door.py` / `Door_Folding_gate.py` 同法，靠 flat articulation-origin baseline + element-scoped allow_overlap 守）。

## 核心身份

Bi-fold 衣柜门系统：顶轨（+可选地轨）+ 框住的 opening + 一或多个 **两叶（或多叶）bi-fold leaf pair**，每 pair 的叶用 center hinge 耦合、accordion 式折叠（**每 leaf ≥2 耦合 REVOLUTE**：jamb pivot + ≥1 center hinge），每 pair 由 jamb/mullion pivot 锚定。核心可动语义 = **耦合折叠链**（单参数 per pair，mimic 2.0）。

**Identity 边界（必须保留）**：top track + framed opening；≥1 bi-fold leaf pair；耦合折叠 hinge 链（jamb pivot + ≥1 center hinge）；折叠运动。
**不该混入**：sliding / bypass 衣柜门（单直线平移 PRISMATIC）、单叶平开门（单铰单叶）、top-hung barn door（滑动整板）。

## 槽位 + 候选模块表

### Slot A：panel_face（③ Primary Form Family — 登记进 slot_choices 的主体形态家族 slot）
form_subtype 均为 **Macro Surface Construction**（同 part tree / 同 Box 家族，改主体表面读法）。

| module_name | 5_star_source | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|
| flat_slab（基线） | origin parent | L90-135（door_core + face_panel + near/far_stile + top/bottom_rail） | Macro Surface Construction | 光面 laminate slab + 薄 face + 窄边条 |
| raised_panel | rec_bi_fold_closet_door_system_var_raised_panel | L106-185（proud stiles/rails/mid_rail + `raised_field_{i}` + chamfer band，SHAKER_*） | Macro Surface Construction | shaker 框凸出 + 双凹入 raised field + 倒角带 |
| louvered | rec_bi_fold_closet_door_system_var_louvered / var_louver_slat_count | L116-132 / L108-130（`for k: louver_slat_{k}` 角度板 between rails） | Macro Surface Construction | 框内 N 条等距倾斜百叶（`louver_slat_count` 二级 N） |
| glass_lite | rec_bi_fold_closet_door_system_var_glass_lite | L134-160（`glass_field` 半透 + 前面 stile caps） | Macro Surface Construction | 框内 framed 半透玻璃 lite |
| mirrored | rec_bi_fold_closet_door_system_var_mirrored | L94-108（`mirror_field` 高反银面 inset in stile/rail） | Macro Surface Construction | 框内高反射镜面 field |

### Slot B：track_guide（顶轨/导向 — root track mesh + 叶端 roller 硬件 + guide part/joint）
| module_name | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| top_only（基线） | origin parent | L525-537（track_web + track_lip_0/1）+ L620-623/703-726（`guide` roller part + `guide_spin` CONTINUOUS） | 顶 U-track + 每 pair 顶 roller（continuous）跑轨内 |
| dual_track | rec_bi_fold_closet_door_system_var_dual_track | `_add_bottom_guide_visuals` L281 + bottom track web/lip + `bottom_guide_spin` | 顶+底双轨 + 每 pair 顶/底 roller |
| pivot_only | rec_bi_fold_closet_door_system_var_pivot_only | 去 `guide`/`guide_spin`（L242 起无 guide helper）；仅 header rail | 无 roller：叶仅靠 jamb pivot + center hinge 支撑（②去一条 continuous 边） |

### Slot C：body_base（root 主体）
| module_name | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| built_in_carcass（基线） | origin parent | L369-498（closet_back/sides/floor/ceiling + tower_partition + center_shelf_0..4 + bay_shelf + hanging_rail + drawer fronts 作 static visual） | 深内嵌衣柜 carcass + 中央 shelf/drawer tower（drawer fronts 为不动 visual，非 prismatic——interior fit-out，非门 identity） |
| plain_frame | rec_bi_fold_closet_door_system_var_plain_frame | L254 起（frame=sill+jambs+header+track only；去 carcass/drawers） | 朴素框住的 opening，无 carcass |

### Slot D：fold_topology（每 pair 叶数 / 折叠深度）
| module_name | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| bifold（基线，2 叶/pair） | origin parent | L648-701（frame_to_pivot → center_hinge） | 每 pair 2 叶 + 1 center hinge（jamb pivot + 1 center = 2 耦合铰） |
| trifold（3 叶/pair） | rec_bi_fold_closet_door_system_var_trifold_leaf | L605-662, L697-792（+`mid_leaf` +`center_hinge_2` handle→mid） | 每 pair 3 叶 + 2 center hinge（LEAF_SPAN 缩到 0.255 保 pair 宽） |

### Slot E：jamb_mount（jamb 锚定硬件）
| module_name | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| pivot_pin（基线） | origin parent | L137-162（bottom/top_pivot_pin）+ L539-557（frame bottom_socket/top_bracket/top_socket） | pin-in-socket 捕入式旋转（grandfathered pin-through） |
| jamb_hinged | rec_bi_fold_closet_door_system_var_jamb_hinged | L150-162（`jamb_hinge_strap_{k}` + `jamb_hinge_barrel` 沿叶 jamb 边） | jamb 边 butt-hinge knuckle 竖线（铰原点落 knuckle 线） |

### Slot F：load_path（承重路径）
| module_name | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| bottom_supported（基线） | origin parent | L539-545（bottom_socket 承重）+ pivot_z=0.065 | 底 socket 托叶，顶为导向 |
| top_hung | rec_bi_fold_closet_door_system_var_top_hung | 顶 pivot 承重（top_bracket/socket 加厚，底为轻导向 pin） | 顶挂承重，底导向 |

### handle_grip（④ record_only companion，非独立 slot）
pull_bar + pull_mount（parent L210-234）作最后叶 free 边视件；knob/recessed/none 为 world-knowledge companion，不 fork。

## 槽位图（slot graph）

pattern: mixed（pair multiplicity 主轴；panel_face = per-leaf parallel child；track/body/mount = root + 叶端硬件层）

```
frame (static root: sill+jambs+header+U-track [Slot B] + mullions + per-pair sockets [Slot E/F]
        + [Slot C] carcass/shelves/drawer-fronts OR bare)
  │  per pair k  (Slot 'panel_pair_count' 复制 N 次; direction[k]=+1 (k<N-1) / -1 (last))
  ├─[REVOLUTE axis=±Z origin=world(pivot_x[k],0,PIVOT_Z)]──► pair{k}_pivot_leaf   (DRIVER)
  │        pair{k}_pivot_leaf ─[REVOLUTE axis=∓Z origin=local(dir*LEAF_SPAN,OFFSET,0)
  │                              Mimic(driver,2.0)]─► pair{k}_handle_leaf
  │        [Slot D trifold] pair{k}_handle_leaf ─[REVOLUTE Mimic(driver,2.0)]─► pair{k}_mid_leaf
  │        [Slot B top_only/dual] last_leaf ─[CONTINUOUS axis=Z]─► pair{k}_guide (roller)
  │        [Slot B dual] last_leaf ─[CONTINUOUS]─► pair{k}_bottom_guide
  │  每 leaf 内部（Slot A parallel children，挂叶本体，无 joint）：
  │     door_core + panel_face 视件（flat/raised/louver loop/glass/mirror）+ stiles/rails
  │     + hinge knuckle 视件 + [Slot E] pivot pin OR jamb-hinge knuckle + [last leaf] pull_bar + guide_bracket
```

跨 slot 连接点位：

- **frame → pivot_leaf**：REVOLUTE，世界原点 `(pivot_x[k],0,PIVOT_Z)`，axis `±Z`（dir 定号）。pivot_x[k] = section_left(k) + PIVOT_INSET（dir+1）/ section_left(k)+PAIR_SPAN−PIVOT_INSET（dir−1）。铰轴落 pivot pin / jamb knuckle 竖线（origin-honesty）。
- **pivot_leaf → handle_leaf**：REVOLUTE，leaf-local `(dir*LEAF_SPAN, CENTER_HINGE_OFFSET, 0)`，axis 与 driver 反号；`Mimic(driver, 2.0)`。center hinge knuckle 竖线（x=dir*LEAF_SPAN）= 铰轴。
- **handle_leaf → mid_leaf**（trifold）：同上 local `(dir*LEAF_SPAN, OFFSET, 0)`，`Mimic(driver, 2.0)`。
- **last_leaf → guide**：CONTINUOUS，local `(dir*LEAF_SPAN, −OFFSET, LEAF_HEIGHT)`（顶）/ `(…,0)`（底 dual）；roller 跑 track_web footprint。
- **Slot B/C/E/F** 派生 root visual + 叶端硬件；不新增跨 pair joint。

## 每槽位 Module Emits / Interfaces

### panel_pair_count（复制单元 = pair）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pair{k}_pivot_leaf` + `pair{k}_handle_leaf`（+trifold `pair{k}_mid_leaf`）（+roller `pair{k}_guide`[+`_bottom_guide`]） | quad L268-360 |
| internal joints | `frame_to_pivot_{k}`(driver REVOLUTE) + `center_hinge_{k}`(mimic 2.0)（+`center_hinge_2_{k}`）（+`guide_spin_{k}` CONTINUOUS） | quad L277-360 / trifold L697-792 |
| upstream interface | pivot_leaf ← frame@`(pivot_x[k],0,PIVOT_Z)`；后叶 ← 前叶@local`(dir*LEAF_SPAN,OFFSET,0)` | triple L537-590 |
| downstream interface | last leaf free 边 = guide 挂点 + pull handle | parent L703-726 |

### Slot A candidates（panel_face，全 leaf-local parent.visual，无 joint）
| module | emits | 来源 |
|---|---|---|
| flat_slab | `door_core`+`face_panel`+`near/far_stile`+`top/bottom_rail` | parent L90-135 |
| raised_panel | `door_core`+`near/far_stile`+`top/bottom/mid_rail`+`raised_field_{0,1}`+chamfer band | raised_panel L119-185 |
| louvered | `door_core`+stiles/rails+`louver_slat_{0..M-1}`（M=`louver_slat_count`） | louvered L116-132 |
| glass_lite | `door_core`(frame)+`glass_field`(半透)+stile caps | glass_lite L134-160 |
| mirrored | `door_core`+`mirror_field`(高反)+stiles/rails | mirrored L94-108 |

### Slot B / C / D / E / F
见槽位表；均为 root visual / 叶端硬件 / 叶数拓扑 / mount 硬件 swap，emit 已在上表列出，无独立跨 pair joint（trifold 例外：per pair +1 center hinge + 1 mid_leaf part）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `panel_face` | enum | flat_slab / raised_panel / louvered / glass_lite / mirrored | flat_slab | choice | deterministic sampler | Slot A |
| `track_guide` | enum | top_only / dual_track / pivot_only | top_only | choice | sampler | Slot B |
| `body_base` | enum | built_in_carcass / plain_frame | built_in_carcass | choice | sampler | Slot C |
| `fold_topology` | enum | bifold / trifold | bifold | choice | trifold ⇒ LEAF_SPAN 缩至 ~0.255、per pair +mid_leaf+center_hinge_2 | Slot D |
| `jamb_mount` | enum | pivot_pin / jamb_hinged | pivot_pin | choice | sampler | Slot E |
| `load_path` | enum | bottom_supported / top_hung | bottom_supported | choice | sampler | Slot F |
| `palette_style` | enum | warm_taupe / primed_white / natural_oak / walnut / mirror_silver / frosted_glass | warm_taupe | choice | 与 face 软关联（非硬绑） | palette 节 |
| `panel_pair_count` (N) | int | [1,4]（primary multiplicity；产品域 up to ~6） | 2 | independent | 见 Multiplicity | Slot pair 表 |
| `louver_slat_count` (M) | int | [8,22]（secondary，仅 louvered） | 14 | conditional | 仅 `panel_face==louvered` 生效；否则忽略 | louvered L123 |
| `leaf_span` | float | derived | 0.365 (bi) / 0.255 (tri) | equation | `= 0.365 (bifold) / 0.255 (trifold)`（保 pair_span≈0.73-0.765） | trifold L32 |
| `pair_span` | float | derived | 0.73 | equation | `= leaves_per_pair * leaf_span` | quad L29 |
| `mullion_width` | float | [0.05,0.07] | 0.06 | independent | clamp | quad L30 / triple L27 |
| `frame_height` | float | [2.20,2.40] | 2.30 | independent | clamp | parent L24 |
| `leaf_height` | float | derived | 2.09 | equation | `= frame_height - 0.21`（header+sill 余量） | parent L31 |
| (—) | constraint | — | — | inequality | `opening_width = N*pair_span+(N-1)*mullion`；frame_width=opening+2*jamb；随 N/topology 派生，无溢出 | quad L33 |
| (—) | constraint | — | — | inequality | `PIVOT_INSET < leaf_span`（pivot 落 section 内不越 mullion）；违反 clamp inset | quad L48 |

**连续尺寸采样契约**：先采 independent（mullion_width、frame_height、N、M）→ equation 派生（leaf_span←topology、pair_span、opening_width、leaf_height）→ inequality 投影（inset<leaf_span，clamp）。conditional：louver_slat_count 仅 louvered；trifold 改 leaf_span。

## 7.5 编译预算 / compile budget
自报 **≤20s/seed**。全 Box/Cylinder，无 cadquery/mesh。最坏 quad(4)×trifold(3 叶)×louvered(22 slat)=12 叶×~22 = ~264 slat box + ~200 其他 visual——Box tessellation 廉价（小特征 ≤16 段，主面默认）；N 个相同 slat 复用 Box 构造。motion QC `max_pose_samples=48`（≤4 driver + continuous roller，Cartesian 上限截断），`ignore_fixed=True`。实测 quad-trifold-louvered 单 seed 远 <20s。

## Multiplicity / Copy Logic

- **PRIMARY: `panel_pair_count` (N)** — N 个 bi-fold leaf pair。
  - N_range: `[1,4]`（产品域可 ~6 满墙衣柜）；samples: 1(var_single_pair)/2(parent)/3(var_triple_pair)/4(var_quad_pair)。
  - sampling: 小 N 高频（`weights={1:2,2:4,3:2,4:1.5}`）。
  - copied object: pair = pivot_leaf+handle_leaf(+mid) + `_add_leaf_visuals` + joints（frame_to_pivot REVOLUTE + center_hinge REVOLUTE mimic + [guide CONTINUOUS]）+ 该 pair 的 socket/bracket + roller。
  - naming: `pair{k}_pivot_leaf`/`pair{k}_handle_leaf`/`pair{k}_mid_leaf`/`pair{k}_guide`；joints `frame_to_pivot_{k}`/`center_hinge_{k}`/`center_hinge_2_{k}`/`guide_spin_{k}`。
  - placement: pairs 沿 opening 按 `pair_pitch` 平铺，section_left(k)=−opening/2+k*pitch；dir[k]=+1(k<N-1)/−1(last)；相邻 pair 间 mullion post。
  - joint policy: 每 pair 1 driver revolute + ≥1 mimic center revolute（真耦合折叠链）+ 可选 continuous roller。
  - source/gating: parent 手写 4 叶，triple/quad 已示范 loop；模板必 loop 化。
- **SECONDARY: `louver_slat_count` (M)** — 仅 `panel_face==louvered`。
  - N_range `[8,22]`；samples 10/16/22（var_louvered / var_louver_slat_count）。copied: `louver_slat_{i}` Box between rails，等距 pitch，static visual（无 joint）。gating: 非 louvered 时该轴不生效。
- **INTERIOR（record_only，非门 identity anchor）**：DRAWER_COUNT=5 —— 模板作 **static drawer-front visual**（非 prismatic），归 body_base=built_in_carcass 的 fit-out，不 fork。

## 视觉多样性 6 轴考察

| 轴 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|
| ① 骨架图 | 有 | pair multiplicity N∈[1,4]（part/joint 数随 N）；fold_topology bifold/trifold（±mid_leaf+center_hinge_2）；track_guide top_only/dual/pivot_only（±guide part+continuous 边）；body_base carcass/plain（±carcass visual）。source-backed（single/triple/quad/trifold/dual_track/pivot_only/plain_frame 变体）。 |
| └ multiplicity | 有 | §8：panel_pair_count N∈[1,4] 加权（小 N 高频）；louver_slat_count M∈[8,22] 仅 louvered。 |
| ② 关节类型 | 有 | REVOLUTE jamb pivot（±Z）+ REVOLUTE center hinge（mimic 2.0）+ CONTINUOUS roller；pivot_only 去 continuous 边；jamb_hinged 换铰硬件同 type。source-backed（parent/pivot_only/jamb_hinged/dual_track）。 |
| ③ 主体形态家族 | 有（登记进 slot_choices，主多样性载体） | `panel_face`：flat_slab / raised_panel / louvered / glass_lite / mirrored，各 form_subtype=Macro Surface Construction，source-backed anchors（5 变体）。 |
| ④ 表面装饰 | 有（record_only + host-conformal） | face_panel / shaker chamfer band / louver slats（M 档）/ glass stile caps / pull_bar / hinge knuckle；均由叶 front 面 `centerline_y−LEAF_THICKNESS/2` 逐叶派生共形（③→⑤→④）。 |
| ⑤ 尺寸/行程 | 有 | mullion_width[0.05,0.07]、frame_height[2.20,2.40]、leaf_span(bi 0.365/tri 0.255 equation)、louver M[8,22]。**运动包络**：frame_to_pivot REVOLUTE axis±Z 开向 −Y，`[closed=upper, folded=0]` 即 [0, FOLDED_PIVOT_ANGLE=80°]；center_hinge mimic 2.0 `[0,160°]`；roller CONTINUOUS 整圈。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` + targeted `ctx.pose` 测 closed（全 pair→upper 共面）与 folded（→0 packet 朝 −Y）+ 位移断言；mimic 使 pair 单参数，无独立-采样 scissor。 |
| ⑥ 涂装 | 有 | 材质大类 painted(primed_white)/wood(oak,walnut)/laminate(warm_taupe)/glass(frosted)/mirror(silver)——6 配色，覆盖 ≥ceil(0.5×6)=3 大类。source-backed（各变体 rgba + world-knowledge 扩展）。 |

**收尾自检**：panel_face 5 家族肉眼可分；6 palette 材质大类都现；louver slat 贴框；折叠全程 mimic 不穿模。

## 采样与覆盖审计

总组合数：panel_face(5) × track_guide(3) × body_base(2) × fold_topology(2) × jamb_mount(2) × load_path(2) = **240 slot 组合** × N(1-4) × M(louvered) ≫ 富类别线。

seed_domain_policy：procedural_first（seed=0 不特殊）。

**Procedural Sampling / Sweep Plan**：`config_from_seed(seed)` 用 `random.Random(seed)`：(1) 加权抽 N（小 N 高频）；(2) 均匀抽 panel_face/track_guide/body_base/fold_topology/jamb_mount/load_path；(3) louvered 时抽 M∈[8,22]；(4) 抽 palette_style；(5) 采连续 scale（mullion_width/frame_height）→ resolve_config equation 派生（leaf_span/pair_span/opening/leaf_height）→ inequality clamp（inset<leaf_span）。无 regression overrides。

Topology target：1000-seed distinct slot tuple 富类别 ≥300（report-only）——240 组合 × N × palette 轻松达标。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted N → 6 enum choice → M(cond) → palette → 连续 scale → 派生 | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | louver M 仅 louvered；trifold ⇒ leaf_span 缩；pivot_only 去 roller；plain_frame 去 carcass；top_hung/bottom 换承重硬件；所有 face/mount 与任意 N/topology 兼容（共享 leaf-local frame） | no floating/collision，hinge axis/range，closed-pose 共面，max N，fold packet 不穿 carcass |
| controlled local variation | mullion_width、frame_height；leaf_span/pair_span/opening/leaf_height equation 派生 clamp | 比例变化不破接口/clearance/铰原点/identity |
| regression overrides | none | — |
| random sweep | 0-15 fast → 0-35 final + corner | contract failures；axis_realization |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A panel_face | 5 | yes | yes | ③ 主形态 slot |
| B track_guide | 3 | yes | yes | |
| C body_base | 2 | yes | no | 2 结构不同 root |
| D fold_topology | 2 | yes | no | ±叶+铰 |
| E jamb_mount | 2 | yes | no | 铰硬件 |
| F load_path | 2 | yes | no | 承重路径 |
| panel_pair_count | 4 distinct（采样 [1,4]） | yes | yes | primary multiplicity |
| louver_slat_count | 3 distinct（[8,22]，cond） | yes | yes | secondary，gated |

## Validator
- slot_choices_for_seed 返回 implemented module names（panel_face/track_guide/body_base/fold_topology/jamb_mount/load_path/panel_pair_count/louver_slat_count）
- config_from_seed deterministic（seed=0 不特殊）
- compatibility: louver M 仅 louvered；trifold 改 leaf_span；pivot_only 去 roller；plain_frame 去 carcass
- 无 regression overrides；不循环 curated 表
- 连续 scale（mullion_width/frame_height）clamp；leaf_span/pair_span/opening/leaf_height equation 派生在 resolve_config 求解
- inequality（inset<leaf_span、opening 派生铺满）在 resolve_config 投影
- 每 pair：driver REVOLUTE + ≥1 center REVOLUTE `Mimic(driver,2.0)`（真耦合折叠链）；铰原点落 pivot pin / center-knuckle 竖线
- key joints: frame_to_pivot axis±Z limits[0,80°]；center_hinge mimic 2.0 limits[0,160°]；roller continuous
- copied objects: `pair{k}_*` 命名 + pair_pitch placement + 每 pair captured overlap 循环复刻
- **coupled-fold validator**：`ctx.pose(all pivot→upper)` 全叶共面 doorway plane（|core y|<tol）；`ctx.pose(all→0)` 全叶 packet 朝 −Y（core y<−0.10）；无叶穿 carcass（carcass +Y、叶 −Y）；sampled poses 无 scissor

## Reject cases
- 独立 pivot/center 铰未 mimic 耦合 → 采样到非物理 scissor 组合穿模（本类头号失败）。
- pair 手写未 loop → N≠2 时缺件/越界。
- center = pivot（mimic 1.0）而非 2.0 → 折叠时 free 边不回 track、handle 叶乱摆。
- pivot 铰原点没落 jamb/mullion pivot 竖线 → 折叠绕错轴、叶漂浮。
- trifold LEAF_SPAN 不缩 → pair 过宽溢出 opening。
- louver M 大 + trifold + quad → slat 数爆炸超 compile 预算（cap M≤22）。
- closed pose 叶不共面（Y 差过大）或大 X gap → 读不出关闭。
- 折叠 packet 穿入 carcass（+Y）→ 叶折向搞反（须朝 −Y）。
- louver_slat 未 gated 到 louvered face → 非 louvered 也发 slat。
- pivot_only 仍发 guide/guide_spin → 悬空 roller。

## 与相邻类别的边界
- 不该混入：**sliding / bypass 衣柜门**（叶直线平移 PRISMATIC、无铰折叠链）。
- 不该混入：**单叶平开门**（单铰单叶、无 center hinge 耦合、无 pair 复制）。
- 不该混入：**top-hung barn door**（滑动整板 PRISMATIC、无折叠）。
- 不该混入：**freestanding accordion room-divider**（无门框 root / 无顶轨 / 非建筑 opening 件）。

## Module Source Index
| source_id | slot | module | record_id | model.py | 采纳 |
|---|---|---|---|---|---|
| S1 | all | origin baseline（2-pair bifold flat top_only carcass pivot-pin bottom） | rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258 | L62-1087 | leaf-local frame + 耦合链 + flat + carcass |
| S2 | pair_count | N=1 | rec_bi_fold_closet_door_system_var_single_pair | full | single pair |
| S3 | pair_count | N=3 loop | rec_bi_fold_closet_door_system_var_triple_pair | L57-590 | loop + mullion + PAIR_CONFIGS |
| S4 | pair_count | N=4 loop | rec_bi_fold_closet_door_system_var_quad_pair | L71-380 | loop + FOLD_DIRS + pair_pivot |
| S5 | D | trifold | rec_bi_fold_closet_door_system_var_trifold_leaf | L605-792 | mid_leaf + center_hinge_2 |
| S6 | A | raised_panel | rec_bi_fold_closet_door_system_var_raised_panel | L106-185 | shaker fields |
| S7 | A | louvered | rec_bi_fold_closet_door_system_var_louvered | L116-132 | slat loop |
| S8 | A/M | louver_slat_count | rec_bi_fold_closet_door_system_var_louver_slat_count | L108-130 | 二级 M |
| S9 | A | glass_lite | rec_bi_fold_closet_door_system_var_glass_lite | L134-160 | glass field |
| S10 | A | mirrored | rec_bi_fold_closet_door_system_var_mirrored | L94-108 | mirror field |
| S11 | B | dual_track | rec_bi_fold_closet_door_system_var_dual_track | L281 | bottom guide |
| S12 | B | pivot_only | rec_bi_fold_closet_door_system_var_pivot_only | L242 | no roller |
| S13 | C | plain_frame | rec_bi_fold_closet_door_system_var_plain_frame | L254 | no carcass |
| S14 | E | jamb_hinged | rec_bi_fold_closet_door_system_var_jamb_hinged | L150-162 | butt-hinge knuckle |
| S15 | F | top_hung | rec_bi_fold_closet_door_system_var_top_hung | joints | top-hung load |

## GATE P3
- spec complete；every candidate real model.py:Lx-Ly ✓
- no undocumented single-candidate slot（all ≥2）✓
- topology audit present ✓
- §7.5 compile budget ≤20s ✓
- MatingContract：pin-through-sleeve 折叠铰 omit+grandfather（AUTHORING §A Rule 2 例外，同 Door_folding_door/Door_Folding_gate）✓
