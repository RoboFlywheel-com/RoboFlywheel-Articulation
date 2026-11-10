# folding_door — Modular Spec (SPEC_ONLY_DRAFT)

> Authored from the 10 5★ sources (1 parent + 9 variants) per SPEC_TEMPLATE.md.
> Every candidate cites a real `record_id` + `model.py:Lx-Ly` span.

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_door` |
| template path | `agent/templates/Door_folding_door.py` |
| test path (optional) | `tests/agent/test_folding_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（multiplicity 叶链 + per-leaf infill parallel-children；以 leaf_count N 复制为主轴的 linear hinge chain） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category（parent + 9 variants，rating=5 synced） |
| source_index_policy | only adopted module sources are indexed below |

阅读要点（全部 10 个 model.py 已逐行读）：

- **共享骨架**：每个样本都是 `frame`（静态 root：header track + 左/右 jamb + floor track，单个 CadQuery union mesh `_build_root_frame_shape`）+ N 个 `leaf_{i}` 铰接件。叶片在 X/Z 平面悬挂，折叠摆入 ±Y；closed (zero) pose 全叶共面于 Y≈0。世界系：opening 居中于 X=0，Z 从 0（地）到 `OPENING_HEIGHT`。
- **叶片局部系恒定**：每个叶片在 leaf-local hinge frame 创作 —— hinge edge 在 local x=0，叶片沿 +X 延伸到 x=LEAF_W，厚度沿 Y 居中。这是所有 infill / track / kinematics 候选共享的接口契约。
- **铰链策略两类**：parent 是 center-biparting 双链（左对 leaf_0/leaf_1 铰左 jamb、右对 leaf_3/leaf_2 铰右 jamb，右链整体 rpy=(0,0,π) 翻转）；n2/n6/n8 是 single_direction_stack 单链（一条连续 `for i in range(LEAF_COUNT)` 链，首叶铰左 jamb，后续叶铰前叶 free edge `(LEAF_W,0,0)`，axis 交替 ±Z zig-zag）。
- **关键 loop-emission gotcha**：parent 的 4 叶 + 4 articulation 是**手写**的（`_add_leaf(model,"leaf_0"..)` × 4 + `model.articulation(...)` × 4，L348-412），叶链未 loop 化。n2/n6/n8 已示范必需的 `for i in range(LEAF_COUNT)` 重写（共享 `_add_leaf` helper + 统一线性链铰链策略）。模板必须照 n2/n6/n8 做循环发射。
- **infill 是 leaf-local 可替换层**：5 种填充各有自己的 helper，全部填进同一 leaf-local 开口（framed_glass=双开口+midrail、frameless=单大开口、solid=实心木板、louvered=水平百叶 for-loop、muntin=玻璃格条 grid for-loop）。infill 切换不改 hinge frame、不改铰链拓扑。
- **track 是 root frame + 叶端硬件层**：flush_header_pivot（基线，朴素 header+floor）、perimeter_cased_U_channel（header/threshold 双 U 槽 + 每叶 top/bot pivot pin）、bottom_track_floor_guided（厚地轨双导轨 + 每叶底 guide roller/stem，z_anchor 移到导轨顶）。track 切换改 root mesh + 叶端硬件 visual + 铰原点 Z anchor。
- **intentional overlaps**：每样本都 `ctx.allow_overlap`：glass/panel rebate 进 frame lip、相邻叶共享 hinge line knuckle、叶 hinge edge 接 jamb、handle standoff 进 frame；这些是 element-scoped / part-pair captured overlap，模板必须在循环里复刻所有 N 个。

## 核心身份

折叠门（folding / bi-fold / accordion / concertina door）：一组 N 片刚性叶片（leaf）用竖直铰链串成一条**线性折叠链**，每片铰在前一片的竖直 meeting edge 上，交替折向（zig-zag），驱动时整链 concertina 折叠贴向门框一侧（single-direction stack）或中央两侧对开（center-biparting bi-fold）。叶片自一个静态 root 门框（header track 顶轨 + 双 jamb + floor track 地轨）悬挂；顶轨/地轨导向，绝不漂浮。每片叶可填玻璃/实木/百叶/格条。默认成熟域：室内隔断门 / 衣柜门 / 阳台折叠门，N∈[2,100]，opening 宽 1.0–6.0 m、高约 2.0–2.4 m。

核心可动语义 = **铰链链折叠**：每个 leaf↔leaf 与 jamb↔leaf 连接都是 REVOLUTE（绕竖直 ±Z 轴），原点落在真实可见的 knuckle/pivot 竖线上，相邻关节 axis 交替反号产生 concertina。

**不该混入**（详见末节边界）：Sliding Door（直线平移、PRISMATIC、无铰链链）、普通铰链 Door（单叶单铰、无链式复制）、卷帘/百叶卷门（多叶但纯平移卷绕、非刚性叶 + 竖铰链）。

## 槽位 + 候选模块表

### Slot A：leaf_count（MULTIPLICITY N — 折叠叶片数，触发 loop 重写）

count_param = `leaf_count`。candidate 行 = 已有样本的 distinct N（模板采样域 N_range 远大于此，见 Multiplicity 节）。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| N=4（基线，手写未 loop） | rec_a-4-panel-bi-fold-interior-glass-partition-door-_20260608_160138_925763_9234fbaa | L344-L412（手写 4× `_add_leaf` + 4× `model.articulation`） | eligible if compatible | 4 叶、4 REVOLUTE、center-biparting 双链；叶链手写，模板须 loop 化 |
| N=2 | rec_folding_door_var_n2 | L338-L389（`for i in range(LEAF_COUNT)` 叶发射 + 铰链链） | eligible if compatible | 单 concertina 对，链式铰，single chain；最小 loop 示范 |
| N=6 | rec_folding_door_var_n6 | L339-L390（`for i in range(LEAF_COUNT)` 双循环） | eligible if compatible | 6 叶紧凑链，loop 发射，single chain，CENTER_LEAF_INDEX handle |
| N=8 | rec_folding_door_var_n8 | L311-L359（`for i in range(LEAF_COUNT)` 双循环） | eligible if compatible | 8 叶连续 accordion 链，loop 发射，single chain |

### Slot B：leaf_infill（叶片填充层；每候选一个 infill helper，填进同一 leaf-local 开口）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| framed_glass_midrail（基线） | rec_a-4-panel-bi-fold-interior-glass-partition-door-_20260608_160138_925763_9234fbaa | `_build_leaf_frame_shape` L97-L148 + `_build_glass_shape` L151-L190 | eligible if compatible | 周框 + 横 mid-rail（MID_RAIL_FRACTION）分上下两开口 + 双玻璃片（上长下短）rebate 进框 |
| frameless_full_glass | rec_folding_door_var_frameless_glass | `_build_leaf_frame_shape` L96-L132 + `_build_glass_shape` L135-L160 | eligible if compatible | 去 mid-rail，仅极简周边 edge rail + 单整片 edge-to-edge 高玻璃 |
| solid_panel | rec_folding_door_var_solid_panel | `_build_leaf_frame_shape` L97-L148 + `_build_wood_panel_shape` L151-L177（`{leaf}_wood_panel`，material="wood"） | eligible if compatible | 周框 + midrail 框 + 单实心 opaque 木板 insert（PANEL_T）填满整开口，不透明 |
| louvered_slats | rec_folding_door_var_louvered | 共享 `_build_slat_shape` L108-L119 + `_add_leaf` 内 slat for-loop L254-L286（`{leaf}_slat_upper_i` / `{leaf}_slat_lower_i`，水平 SLAT_ANGLE 倾板，n=round(opening_h/pitch)） | eligible if compatible | 框内上下开口各 for-loop 发射 N 条水平倾斜木百叶（plantation shutter），WOOD_RGBA |
| muntin_grid_glass | rec_folding_door_var_muntin_grid | `_add_muntin_grid_to_leaf` L158-L223（`for i in range(1,n_rows)` 横条 / `for j in range(1,n_cols)` 竖条 / `for i,j` lite grid；`{leaf}_muntin_h_*` / `_muntin_v_*` / `_lite_*`），`_add_leaf` 调两次 L302-L323 | eligible if compatible | 玻璃 + 细 muntin 格条把每开口分成 n_cols×n_rows 小 lite（colonial grid） |

### Slot C：folding_kinematics（折叠链拓扑 — 铰链链策略）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_direction_stack（采样默认） | rec_folding_door_var_n2 L357-L389 / rec_folding_door_var_n6 L358-L390 / rec_folding_door_var_n8 L328-L358 | 见各 source | eligible if compatible | 一条连续链：joint 0 = frame→leaf_0 铰左 jamb `HINGE_X[0]`；joint i≥1 = leaf_{i-1}→leaf_i 铰 `(LEAF_W,0,0)`；axis 交替 +Z(偶)/-Z(奇)；全链整体 stack 一侧（左 jamb）。任意 N 通用 |
| center_biparting_bifold | rec_a-4-panel-bi-fold-interior-glass-partition-door-_20260608_160138_925763_9234fbaa | L365-L412（左链 leaf_0/leaf_1 铰左 jamb；右链 leaf_3/leaf_2 铰右 jamb，原点带 rpy=(0,0,π)；两链 axis 各自交替 ±Z） | eligible if compatible | 两条对称半链各铰一个 jamb，中央 biparting 对开；仅适用偶数 N（左右各 N/2 叶）。pull handle 在中央 meeting 叶 |

### Slot D：top_track / suspension（顶轨/吊挂/导向样式 — root mesh + 叶端硬件 + 铰原点 Z anchor）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_header_pivot（基线） | rec_a-4-panel-bi-fold-interior-glass-partition-door-_20260608_160138_925763_9234fbaa | `_build_root_frame_shape` L197-L240（header+左右 jamb+floor union）；铰 z_anchor=`LEAF_BOTTOM_Z` L363 | eligible if compatible | flush 连续 header 顶轨 + 朴素 jamb pivot + 薄 floor track；无额外叶端硬件；最朴素 |
| perimeter_cased_U_channel | rec_folding_door_var_perimeter_frame | `_build_root_frame_shape` L212-L282（header 底面 U 槽 cut + threshold 顶面 U 槽 cut）+ `_add_leaf` 内 top/bot pivot pin L333-L348（`{leaf}_pivot_top` / `{leaf}_pivot_bot`） | eligible if compatible | 全周 cased 框：header/threshold 双 U-channel 捕叶上下边 + 每叶 hinge 边 top/bot pivot guide pin 入槽 |
| bottom_track_floor_guided | rec_folding_door_var_bottom_track | `_build_root_frame_shape` L219-L300（厚 floor base + 双 raised guide rail）+ `_add_leaf` 内 roller/stem L355-L388（`{leaf}_roller` / `{leaf}_roller_stem`）；铰 z_anchor=`FLOOR_H+GUIDE_RAIL_H` L465 | eligible if compatible | 厚地轨双导轨承重 + 每叶底 guide roller(横 Y)+vertical stem 滑入地槽；顶仅细导向（不承重）；铰原点锚在导轨顶接触面 |

## 槽位图（slot graph）

pattern: mixed（multiplicity 叶链主轴；infill = per-leaf parallel child；track = root + 叶端硬件层）

```
frame (static root: header track + L/R jamb + floor track  [Slot D 决定 root mesh + z_anchor])
  │
  ├─[REVOLUTE  axis=±Z  origin=world(HINGE_X[0], 0, z_anchor)]──► leaf_0
  │       (Slot C: single → frame; center-biparting → 左/右 jamb 各起一链)
  │
  leaf_0 ─[REVOLUTE axis=∓Z origin=local(LEAF_W,0,0)]─► leaf_1 ─[…]─► leaf_{N-1}
          (Slot A 复制 N 次；Slot C 决定单链 vs 双对称链 + axis 交替号)
  │
  每个 leaf_i 内部（Slot B parallel children，挂在 leaf_i 本体上，无额外 joint）：
     {leaf_i}_frame (steel)  +  infill（glass / wood panel / slat loop / muntin grid）
     +  {leaf_i}_knuckle_*（hinge line 视件）
     +  Slot D 叶端硬件：pivot_pin（perimeter）/ roller+stem（bottom_track）/ 无（flush）
```

跨 slot 连接点位：

- **frame → leaf_0**：REVOLUTE，世界原点 `(HINGE_X[0], 0, z_anchor)`，axis ±Z。`z_anchor` 由 Slot D 决定（flush=`LEAF_BOTTOM_Z`；perimeter=`LEAF_BOTTOM_Z`；bottom_track=`FLOOR_H+GUIDE_RAIL_H` 导轨顶）。`HINGE_X[i]=LEFT_HINGE_X + i*LEAF_W`。
- **leaf_{i-1} → leaf_i**：REVOLUTE，**leaf-local** 原点 `(LEAF_W, 0, 0)`（父叶 free edge），axis 与父关节反号（zig-zag）。这是 leaf-local hinge frame 接口契约，所有 infill/track 候选共享。
- **Slot C 互斥**：single_direction_stack（一条链 frame→leaf_0→…）与 center_biparting_bifold（两条链分别铰左/右 jamb，右链原点带 rpy=(0,0,π)）是互斥拓扑。center-biparting 仅偶数 N。
- **Slot B parallel children**：infill visual 直接挂在 `leaf_i` 本体上，无独立 joint（不动装饰），随叶片刚体一起折。
- **Slot D 派生**：root frame mesh 与每叶 hinge-edge 硬件 visual 由 Slot D 选择决定；bottom_track 还派生 `z_anchor` 上移。

## 每槽位 Module Emits / Interfaces

### Slot A / leaf_count（复制单元 = leaf）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `leaf_0 .. leaf_{N-1}`（每叶一个 part，含 frame+infill+knuckle+硬件 visual） | n8 / model.py:L311-L312 |
| internal joints | 每叶引入 1 个上游 REVOLUTE（jamb 或前叶）；共 N 个非固定关节 | n8 / model.py:L328-L358 |
| upstream interface | leaf_0 ← frame@`(HINGE_X[0],0,z_anchor)`；leaf_i ← leaf_{i-1}@local`(LEAF_W,0,0)` | n2 / model.py:L363-L389 |
| downstream interface | leaf_i free edge（local x=LEAF_W）= 下一叶 hinge mating face | n6 / model.py:L378-L390 |

### Slot B / framed_glass_midrail
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{leaf}_frame`（steel 周框+midrail mesh）+ `{leaf}_glass`（上+下玻璃 union），visual on leaf | parent / model.py:L263-L274 |
| internal joints | 无（infill 是 leaf 本体不动视件） | parent / model.py:L97-L190 |
| upstream interface | 填进 leaf-local 双开口（上 `[t,w-t]×[mid+half,h-t]`，下 `[t,w-t]×[t,mid-half]`），glass rebate=0.006 进框 lip | parent / model.py:L121-L190 |
| downstream interface | 无（终端层） | — |

### Slot B / frameless_full_glass
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{leaf}_frame`（仅周边 edge rail，无 midrail）+ `{leaf}_glass`（单整片） | rec_folding_door_var_frameless_glass / model.py:L96-L160 |
| internal joints | 无 | — |
| upstream interface | 单大开口 `[t,w-t]×[t,h-t]`，单 pane rebate=0.006 | rec_folding_door_var_frameless_glass / model.py:L118-L160 |

### Slot B / solid_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{leaf}_frame`（周框+midrail）+ `{leaf}_wood_panel`（实心 opaque 木板，material="wood"） | rec_folding_door_var_solid_panel / model.py:L255-L259 |
| internal joints | 无 | — |
| upstream interface | 单实心板 `[t-rebate,w-t+rebate]×[t-rebate,h-t+rebate]`，PANEL_T 厚，rebate 进框 | rec_folding_door_var_solid_panel / model.py:L151-L177 |

### Slot B / louvered_slats
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{leaf}_frame` + `{leaf}_slat_upper_i` / `{leaf}_slat_lower_i`（for-loop 水平倾斜木板，material="wood"） | rec_folding_door_var_louvered / model.py:L259-L286 |
| internal joints | 无（百叶为固定视件，非可调） | — |
| upstream interface | 共享 `slat_mesh`（一次 build，多 leaf instance）；上下开口各 `n=max(3,round(open_h/SLAT_PITCH_TARGET))` 等距 | rec_folding_door_var_louvered / model.py:L108-L119, L342-L344 |

### Slot B / muntin_grid_glass
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{leaf}_frame` + `{leaf}_muntin_h_{suf}_i` / `_muntin_v_{suf}_j`（细条）+ `{leaf}_lite_{suf}_i_j`（小玻璃格） | rec_folding_door_var_muntin_grid / model.py:L186-L223 |
| internal joints | 无 | — |
| upstream interface | 对上/下开口各调 `_add_muntin_grid_to_leaf`，n_cols×n_rows grid（upper 3×3、lower 3×6），lite_inset 防触条 | rec_folding_door_var_muntin_grid / model.py:L302-L323 |

### Slot C / single_direction_stack
| emits | 描述 | 来源 |
|---|---|---|
| parts | 不 emit part（消费 leaf_count）；定义铰链拓扑 | n2 / model.py:L357-L389 |
| internal joints | `frame_to_leaf_0`(jamb) + `leaf_{i-1}_to_leaf_i`(i≥1)，REVOLUTE，axis 交替 ±Z，limits [0,2.5~2.7] | n8 / model.py:L328-L358 |
| upstream interface | leaf_0 铰左 jamb `HINGE_X[0]`@z_anchor | n2 / model.py:L363-L375 |
| downstream interface | 整链 stack 折向左 jamb 一侧 | n2 / model.py:L377-L389 |

### Slot C / center_biparting_bifold
| emits | 描述 | 来源 |
|---|---|---|
| parts | 不 emit part；定义双对称链拓扑（左半 + 右半） | parent / model.py:L365-L412 |
| internal joints | 左链：`left_jamb_to_leaf_0`@`HINGE_X[0]` + `leaf_0_to_leaf_1`@local`(LEAF_W,0,0)`；右链：`right_jamb_to_leaf_3`@`HINGE_X[N]`(rpy=(0,0,π)) + `leaf_3_to_leaf_2`@local`(LEAF_W,0,0)`；axis ±Z | parent / model.py:L368-L412 |
| upstream interface | 左半第一叶铰左 jamb，右半第一叶铰右 jamb（180° 翻转向中央延伸） | parent / model.py:L391-L402 |
| downstream interface | 两半向中央 biparting；handle 在中央 meeting 叶 | parent / model.py:L353-L355 |

### Slot D / flush_header_pivot
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame_shell`（header+L/R jamb+floor union mesh） | parent / model.py:L337-L342 |
| internal joints | 无（静态 root） | — |
| upstream interface | header 跨满 opening 宽、为最高件；leaf 自 header 下悬挂 | parent / model.py:L204-L240 |
| downstream interface | 提供 `z_anchor=LEAF_BOTTOM_Z` 给铰原点；无叶端硬件 | parent / model.py:L363 |

### Slot D / perimeter_cased_U_channel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame_shell`（header 底 U 槽 + threshold 顶 U 槽）+ 每叶 `{leaf}_pivot_top` / `{leaf}_pivot_bot` | rec_folding_door_var_perimeter_frame / model.py:L229-L280, L336-L348 |
| internal joints | 无（pivot pin 为捕入槽的不动硬件视件） | — |
| upstream interface | leaf 顶/底边捕入 header/threshold CHANNEL（CHANNEL_DEPTH/CHANNEL_W）；LEAF_TOP/BOTTOM_Z 入槽 | rec_folding_door_var_perimeter_frame / model.py:L66-L70, L229-L239 |
| downstream interface | hinge-edge top/bot pivot pin 入双槽导向 | rec_folding_door_var_perimeter_frame / model.py:L333-L348 |

### Slot D / bottom_track_floor_guided
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame_shell`（厚 floor base + 双 raised guide rail + 细 header）+ 每叶 `{leaf}_roller` + `{leaf}_roller_stem` | rec_folding_door_var_bottom_track / model.py:L259-L300, L355-L388 |
| internal joints | 无（roller/stem 为不动硬件视件） | — |
| upstream interface | leaf 重量经底 roller 落在双导轨 GUIDE_CHANNEL_GAP 槽内；header 仅细导向不承重 | rec_folding_door_var_bottom_track / model.py:L266-L290 |
| downstream interface | 铰 `z_anchor=FLOOR_H+GUIDE_RAIL_H`（导轨顶接触面） | rec_folding_door_var_bottom_track / model.py:L465 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `leaf_infill` | enum | framed_glass_midrail / frameless_full_glass / solid_panel / louvered_slats / muntin_grid_glass | framed_glass_midrail | choice | deterministic procedural sampler 选 | Slot B 表 |
| `folding_kinematics` | enum | single_direction_stack / center_biparting_bifold | single_direction_stack | choice | center_biparting 仅当 N 为偶 | Slot C 表 |
| `top_track` | enum | flush_header_pivot / perimeter_cased_U_channel / bottom_track_floor_guided | flush_header_pivot | choice | deterministic procedural sampler 选 | Slot D 表 |
| `palette_style` | enum | charcoal_framed_glass / clear_frameless_glass / walnut_solid_panel / oak_louvered / colonial_white_muntin / bronze_framed_glass | charcoal_framed_glass | choice | 见 palette 节；与 infill 软关联（见 conditional 行） | parent L87-L90 / louvered L98-L101 / solid_panel L87-L90 / muntin L94-L97 |
| `leaf_count` (N) | int | [2, 100]（采样加权，见 Multiplicity） | 4 | independent | per-N 加权抽；center_biparting 时投影到偶数 | Slot A 表 |
| `opening_width` | float | [1.0, 6.0] m | 2.20 | independent | 在范围内采样后 clamp | parent / model.py:L38 |
| `opening_height` | float | [2.0, 2.4] m | 2.10 | independent | 在范围内采样后 clamp | parent / model.py:L39 |
| `leaf_w` | float | derived | 0.535 | equation | `= (opening_width - k_jamb)/N`（single：`(W-JAMB_W)/N`；biparting：每半 clear_span/(N/2)），保证等宽铺满 clear span | n2 L65-L66 / n6 L57-L58 / n8 L58 |
| `frame_t` (stile 料宽) | float | [0.025, 0.050] m | 0.035 | independent | clamp；in-plane 周框料宽 | parent / model.py:L43 |
| `mid_rail_fraction` | float | [0.55, 0.72] | 0.66 | conditional | 仅 framed_glass/solid/louvered/muntin 有 midrail；frameless 时忽略 | parent / model.py:L63 |
| `handle_len` | float | [0.50, 0.90] m | 0.70 | independent | clamp；中央/末叶 pull bar 长 | parent / model.py:L72 |
| `glass_tint_alpha` | float | [0.22, 0.40] | 0.30 | independent | glass RGBA alpha；纯外观 | parent / model.py:L88 |
| (—) | constraint | — | — | inequality | `LEAF_W ≥ 4*FRAME_T`（叶须容下双侧框料+开口）；违反则减小 FRAME_T 或回缩 N | parent L122-L136 |
| (—) | constraint | — | — | inequality | `LEAF_TOP_Z > LEAF_BOTTOM_Z` 且 `LEAF_H > 2*FRAME_T`（叶高正、容下上下框） | parent L60-L62 |
| (—) | constraint | — | — | inequality | N·LEAF_W ≈ clear_span（铺满，无大 X gap / 无溢出 jamb） | n2 L478-L483 |

**连续尺寸采样契约**：先采 independent（opening_width/height、frame_t、handle_len、glass_tint、leaf_count）→ 按 equation 派生 leaf_w → 用 inequality 投影/回缩（叶宽容框、叶高正、铺满 clear span），不满足拒绝重采 → conditional（mid_rail_fraction 仅在有 midrail 的 infill 解析；center_biparting 把 N 投影到偶数）。

## Multiplicity / Copy Logic

- **count_param**: `leaf_count`（Slot A，唯一 multiplicity 轴）。
- **N_range**（本小类本轴产品域）: `[2, 100]`。测试偏小（sweep 主跑 N∈[2,12]）；产品全程到 100。模板采样域远大于样本覆盖 {2,4,6,8} 是正常的（per memory: config_from_seed = per-N 加权抽，小 N 高频、尾部稀有、N>50 强降权）。
- **sampling domain（权重档）**: 小 N 高频（N∈[2,8] 占多数权重，~常见门 3–6 叶），中 N 中频（[9,20]），大 N 稀有降权（[21,100]，accordion 隔断墙）。center_biparting 选中时把 N 投影到最近偶数。
- **copied object**: leaf（`_add_leaf` helper，emit frame+infill+knuckle+Slot-D 硬件）。
- **naming**: `leaf_{i}`，i∈[0,N)；joint = `frame_to_leaf_0`（首）+ `leaf_{i-1}_to_leaf_{i}`（i≥1）。
- **placement**: 沿 X 等宽排布，hinge 竖线 `HINGE_X[i] = LEFT_HINGE_X + i*LEAF_W`（i∈[0,N]，N+1 条线，[0]=左 jamb、[N]=右 jamb）。
- **joint policy**: 线性链 REVOLUTE。首叶铰 jamb（世界原点 `(HINGE_X[0],0,z_anchor)`），后续叶铰前叶 free edge（leaf-local `(LEAF_W,0,0)`），axis 交替 `+Z(偶 i)/-Z(奇 i)` 做 zig-zag concertina，limits `[0, ~2.5–2.7]`。center_biparting 时拆成两条对称链：左半铰左 jamb、右半铰右 jamb（右链原点带 `rpy=(0,0,π)`），各半内部同样交替号。
- **source/gating**: N=4 手写（parent L344-L412）；n2/n6/n8 已示范 `for i in range(LEAF_COUNT)` 单循环重写（n2 L338-L389, n6 L339-L390, n8 L311-L358）。**模板必须 loop 化**，不得照搬 parent 手写四调用。handle 挂在「中央/末端 meeting 叶」：single 挂末叶或 free-edge 最近 X=0 的叶（n8 leaf_3 / n6 CENTER_LEAF_INDEX）；biparting 挂中央两 meeting 叶之一。
- **overlap 复制**: 每叶须循环复刻所有 captured overlap（glass↔frame rebate、相邻叶 hinge-line、叶↔jamb、handle standoff↔frame、infill/硬件相关）；n2/n6/n8 已用 `for i in range(LEAF_COUNT)` 发 allow_overlap（n2 L431-L461）。

## 拓扑多样性审计

总组合数：infill(5) × kinematics(2) × track(3) × distinct-N(采样, ≥10) = **5×2×3 = 30 个 slot 组合**，再乘 N 采样多样性。仅 infill(5)×distinct-N(4 已有样本) = 20 ≥ 10 已过。

理由：N 轴直接改铰链数（single 链 j=N 个关节；biparting 双链）、part 数（N 个 leaf part）；kinematics 轴改链拓扑（单链 vs 双对称链 + jamb 挂点 + rpy 翻转）；track 轴改 root mesh + 每叶硬件 part（pivot pin / roller+stem / 无）+ z_anchor；infill 轴改每叶 part 集合（glass / wood panel / N 条 slat / muntin grid lite 数）。这些都改 part tree / joint count / 视件集合 → distinct topology 充裕。

seed_domain_policy：procedural_first（seed=0 不特殊）。

**Procedural Sampling / Sweep Plan**：`config_from_seed` 用 `ctx.rng`：(1) per-N 加权抽 leaf_count（小 N 高频）；(2) 抽 infill / track（均匀或弱权）；(3) 抽 kinematics（single 默认高频；center_biparting 仅偶数 N 才合法，否则 fallback single 或把 N 投影偶数）；(4) 抽 palette_style（与 infill 弱关联 conditional）；(5) 采连续 scale（opening_width/height、frame_t、handle_len、glass_tint）→ 派生 leaf_w → inequality 投影/回缩。compatibility matrix 阻断非法组合（见下）。无 regression overrides（样本池就绪、全 9 变体 converged）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。N 采样([2,100] 加权) × infill(5) × kinematics(2) × track(3) 按 ≥300 富类别口径观察；实际受 N 加权偏小，但 distinct (N,infill,kinematics,track) 元组在 1000 seed 内可轻松达到富类别观察线时按 ≥300 记录。

Controlled local parameterization：关键连续 scale = `opening_width`(1.0–6.0)、`opening_height`(2.0–2.4)、`frame_t`(0.025–0.050)、`mid_rail_fraction`(0.55–0.72, conditional)、`handle_len`(0.50–0.90)、`glass_tint_alpha`(0.22–0.40)。`leaf_w` 为 equation 派生（`(W-k_jamb)/N`），不独立抽。全部在 `resolve_config` clamp/派生/投影，受 inequality（叶容框、叶高正、铺满 clear span）约束，不破坏 leaf-local hinge frame 接口、不改铰链拓扑或 N。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 weighted N（小 N 偏多）→ infill/track/kinematics choice → palette → 连续 scale → 派生 leaf_w → inequality 回缩 | slot_choices_for_seed matches build choices |
| compatibility matrix | center_biparting ⇒ N 偶（奇 N fallback single 或投影偶）；frameless ⇒ 忽略 mid_rail_fraction；bottom_track ⇒ z_anchor 上移导轨顶；所有 infill/track 与任意 N、任意 kinematics 兼容（共享 leaf-local frame） | no floating, no collision, hinge axis/range, closed-pose coplanar, max N, 链长 |
| controlled local variation | opening_w/h、frame_t、handle_len、glass_tint、mid_rail_fraction(cond)；leaf_w 派生 clamp | 比例变化不破接口/clearance/铰原点/类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初查；0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A leaf_count | 4 distinct（{2,4,6,8} 样本；采样域 [2,100]） | yes | yes | multiplicity 轴 |
| B leaf_infill | 5 | yes | yes | |
| C folding_kinematics | 2 | yes | no | center_biparting 仅偶 N；2 个结构不同链拓扑，无 1-candidate slot |
| D top_track | 3 | yes | yes | |

## Validator

- slot_choices_for_seed returns implemented module names（infill / kinematics / track / N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating: center_biparting 仅偶 N；frameless 忽略 mid_rail；bottom_track z_anchor 上移
- 无 regression overrides；不循环 curated 表
- controlled local scale（opening_w/h、frame_t、handle_len、glass_tint、mid_rail_fraction）clamped；leaf_w equation 派生在 resolve_config 求解，不留 builder 失败
- cross-part inequality（叶容框 LEAF_W≥4·FRAME_T、叶高正、铺满 clear span）在 resolve_config 投影/回缩
- critical interface: leaf-local hinge frame（hinge edge x=0、free edge x=LEAF_W）一致；frame→leaf_0@`(HINGE_X[0],0,z_anchor)`、leaf_{i-1}→leaf_i@local`(LEAF_W,0,0)`
- key joints: N 个 REVOLUTE，axis 交替 ±Z，limits [0,~2.5–2.7]；closed pose 全叶 Y 共面、X 左→右有序铺满
- copied objects: `leaf_{i}` 命名 + `HINGE_X[i]` placement + 每叶 captured overlap 循环复刻
- 每叶有 frame + infill + knuckle 视件；track 选中时有对应叶端硬件（pivot pin / roller）

## Reject cases

- 叶链手写未 loop 化（照搬 parent 4 调用），N≠4 时部件缺失或越界。
- center_biparting 用于奇数 N（左右半不等、中央 meeting 错位 / 漂浮）。
- 相邻叶 axis 不交替（同号 co-rotate，不 concertina，折叠时穿模或不贴 jamb）。
- 铰原点没落在 free-edge 竖线（`(LEAF_W,0,0)`）或 jamb 线（`HINGE_X[0]`）→ 折叠绕错轴、叶分离漂浮。
- bottom_track 选中但 z_anchor 仍用 `LEAF_BOTTOM_Z`（叶悬空于导轨上 / roller 不接触地槽）。
- LEAF_W < 4·FRAME_T（大 N + 宽框）→ 开口塌缩、infill 退化或自交。
- closed pose 叶不共面（Y 差过大）或留大 X gap（门读不出「关闭」）。
- infill rebate / handle standoff / 相邻叶 hinge-line overlap 未声明 allow_overlap → 误报碰撞失败。
- N 采样无加权（均匀抽到大量 N>50）→ sweep 超时 / 巨链 self-collision。

## 与相邻类别的边界

- 不该混入：**Sliding Door / 滑动门**（叶片沿轨直线平移 PRISMATIC，无铰链链、无 concertina；folding door 的本质是 REVOLUTE 铰链串成的折叠链）。
- 不该混入：**普通铰链 Door / 单叶平开门**（单叶单铰挂 jamb，无 leaf↔leaf 链式复制、无 multiplicity N 轴）。
- 不该混入：**卷帘门 / roller shutter / 百叶卷门**（多水平条但纯卷绕平移、柔性帘；folding door 是刚性叶 + 竖直铰链 + 离散折叠）。
- 不该混入：**屏风 / room divider 摆件**（无门框 root、无顶/地轨悬挂导向、不是建筑开口件）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_add_leaf`（含 infill/track 硬件分支）、`_build_leaf_frame_shape`（infill 决定开口数）、`_build_root_frame_shape`（track 决定 U 槽/导轨）。leaf-local hinge frame 是所有候选的共同接口契约。
- loop 化关键：照 n2/n6/n8 用 `for i in range(LEAF_COUNT)` 发 leaf + articulation + allow_overlap；勿照搬 parent 手写。
- center_biparting：右半链原点带 `rpy=(0,0,π)`（翻转向中央延伸），仅偶 N；handle 在中央 meeting 叶。
- allow_overlap 须 element-scoped 复刻全部 N 个：glass/panel↔frame rebate、相邻叶 hinge-line、叶↔jamb、handle standoff↔frame、（perimeter）pivot pin↔channel、（bottom_track）roller↔guide rail。
- bottom_track 选中需同步把铰 `z_anchor` 改为 `FLOOR_H+GUIDE_RAIL_H`，并加每叶 roller+stem。
- palette_style 与 infill 弱关联（glass 系 palette 配 glass infill、wood 系配 solid/louvered），但实现为独立 enum + conditional 软约束，非硬绑定。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C/D | N=4 + center_biparting + flush（基线，手写） | rec_a-4-panel-bi-fold-interior-glass-partition-door-_20260608_160138_925763_9234fbaa | L97-L412 | leaf-local frame 契约 + center-biparting 链 + flush root；loop 化反例 |
| S2 | A/C | N=2 single chain | rec_folding_door_var_n2 | L233-L389 | 最小 loop 示范 + single_direction_stack |
| S3 | A/C | N=6 single chain | rec_folding_door_var_n6 | L246-L390 | loop 重写 + CENTER handle |
| S4 | A/C | N=8 single chain | rec_folding_door_var_n8 | L227-L358 | 连续 accordion loop |
| S5 | B | frameless_full_glass | rec_folding_door_var_frameless_glass | L96-L160 | 单开口 + 单整片玻璃 infill |
| S6 | B | solid_panel | rec_folding_door_var_solid_panel | L151-L259 | 实心木板 infill |
| S7 | B | louvered_slats | rec_folding_door_var_louvered | L108-L286 | slat for-loop infill |
| S8 | B | muntin_grid_glass | rec_folding_door_var_muntin_grid | L158-L323 | muntin grid infill |
| S9 | D | perimeter_cased_U_channel | rec_folding_door_var_perimeter_frame | L212-L348 | 双 U 槽 root + pivot pin |
| S10 | D | bottom_track_floor_guided | rec_folding_door_var_bottom_track | L219-L388, L465 | 厚地轨双导轨 + roller + z_anchor 上移 |
