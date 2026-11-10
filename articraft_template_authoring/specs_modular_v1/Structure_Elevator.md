# elevator — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `elevator` |
| template path | `agent/templates/Structure_Elevator.py` |
| test path (optional) | `tests/agent/test_elevator_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：核心是 `parallel_children`（一个静态 `wall_surround`/`frame` root，挂若干 FIXED landing 固件 + 若干 PRISMATIC 滑动门叶 + 1 个 interior reveal 的 visuals/FIXED cab），叠加 **一条 multiplicity 轴**（door_leaf_count ∈ {1,2,4}，由 Slot A 门机构 gating 决定）。surround_facade（B）、interior_reveal（C）、landing_fixtures（D）是固定 named-slot 选择轴，不复制。

> ⚠️ 本 spec **完全替换**仓库里旧的 freestanding elevator shaft（hoistway / traveling cab / guide rails / counterweight / drive sheave）spec。旧对象被误读了。真实参考图与 12 个 5★ 母体都是 **电梯层站入口（elevator landing entrance）**：墙面围框 + 门洞开口 + 滑动门叶 + 门洞上方楼层指示器 + 旁边呼叫面板 + 地面带槽门槛 sill + 门后内部 reveal（裸暗井道 ↔ 装修轿厢）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12（2 parent + 10 converged variant，全部逐行通读 model.py，逐候选解析真实 `model.py:Lx-Ly`） |
| read_scope | all 5-star samples in this category（2 distinct parents P1/P2 + 10 single-axis variants，每个针对一个 slot 候选） |
| source_index_policy | only adopted module sources are indexed below |

要点（12/12 全读）：

- **统一坐标系**：所有样本一致 — **Z-up，米**；**+X = 墙宽 / 门滑动轴**；**+Y = 墙厚 / 进入井道的深度**；**+Z = 高**；楼面 / 门槛在 **z = 0**；门洞从墙体切穿；门叶坐在墙前浅口袋 `y∈[-0.040, 0]`（或 alcove 后部 / 轿厢门轨）；shaft / cab reveal 退在门后 `y∈[0, ~0.35]`（cab 更深 ~1.5）。
- **统一根装配 = parallel_children**：每样本一个**静态 root**（granite/marble `wall_surround` 或 metal `frame`），CadQuery「实心 slab 切出门洞」做真正 through-cut（P1 `_granite_wall_shape` L115-126、P2 `_marble_surround_shape` L99-141）。门叶是独立 part 经 PRISMATIC articulation 挂上去；indicator / call_panel / sill 是**独立 FIXED part**，各自 embed/butt 进墙（seated-mount overlap + `expect_contact`）；jamb / shaft recess / architrave / reveal panels / cab 装修是 parent visual 或 FIXED 子件。
- **类别身份 = PRISMATIC 沿 X 滑动门叶**：所有门叶都是 **PRISMATIC，轴 ±X**（无 REVOLUTE swing 门）。center-opening = 两叶镜像 ±X（P1 L400-421 / P2 L530-548）；side telescopic = 两叶同向 -X、travel 分级（side_telescopic L407-418）；single = 一叶 -X 全宽（single_slide L395-405）；4-leaf telescopic = side×leaf 嵌套 4 叶、inner travel 远、outer travel 近（center_four_leaf L326-359）。closed=q0（门叶在中缝相接 / 全覆盖门洞）、open=upper（让开门洞中心）。
- **嵌入固件 overlap 合约**：indicator/call_panel/sill 各 `allow_overlap(part, wall)` + `expect_contact(part, wall)` 证明 seated（P1 L444-462）。4-leaf 的 outer 叶在 rear track 还要对 `granite_slab`/`shaft_recess` element-scoped allow_overlap（center_four_leaf L435-454）。telescopic 两叶必须 **offset Y 平面**（不同轨）否则互穿（side_telescopic TRACK_FRONT_Y/REAR_Y L62-63；4-leaf FRONT/REAR_TRACK_CY L59-60）。
- **interior reveal 三态**：bare_dark_shaft = 5 薄板暗盒（P1 `_shaft_recess_shape` L170-198，作 wall 的 parent visual）；furnished_cab = 深 cab shell + teal 墙板 + handrail + ceiling + floor，作独立 FIXED part（P2 `_cab_shell_shape` L235-274 + handrail L336-363 + surround_to_cab FIXED L464-470）；mirror_panel_cab = cab shell + 大镜面 + 抛光 trim、去掉 handrail（mirror_cab L277-325）。
- **landing fixtures 四型**：digit_indicator+call_plate（P1 7-seg 红数字 L233-269 + 小 up/down plate L272-301）；lit indicator（P2 amber 段 L366-391）；arrow_lantern + large_panel（双箭头 lantern cluster L240-305 + 大单按钮 panel L308-330）；lcd_strip + touch_call（宽 LCD bar L233-253 + flush 触摸盘 L266-286）；minimal_none（去掉 indicator & call_panel，只剩 wall+sill+doors，minimal L294-305 断言缺席）。
- **surround facade 四型**：flush_stone_wall（P1/P2 平 slab through-cut）；proud_architrave_portal（proud_architrave `_architrave_shape` L161-195，3 级阶梯线脚向 -Y 凸出）；recessed_alcove（recessed_alcove 墙前切 niche + 四面 reveal 板 L122-176，门退到 alcove 后部）；metal_framed_pylon（metal_pylon 细钢 mullion + head beam + 薄 infill L114-130，窄金属门框）。
- **手写 / loop**：door 叶在多数样本是 2 次手写 helper（`_leaf_shape(sign)`），但 telescopic/4-leaf/alcove/pylon/minimal 已 loop 化（`for i`/嵌套 side×leaf）发射门叶 + per-leaf PRISMATIC joint；reveal/mullion/infill 也有 loop（alcove reveal、pylon mullion/infill）。这些是 multiplicity / 复制母体。

## 核心身份

一个 **电梯层站入口（elevator landing entrance）**：站立在楼面（z=0）上的一面墙体围框（granite/marble 宽墙 或窄金属门框），中间一个切穿的矩形门洞；门洞里有 **1 / 2 / 4 片沿 X 平移（PRISMATIC）开闭的金属滑动门叶**（category-defining motion）；门洞上方有一个固定的**楼层位置指示器**（7 段数字 / 点亮段 / 箭头 lantern / LCD 条），旁边约 1.1 m 高处有一个固定的**厅外呼叫面板**（up/down 小盘 / 大单按钮 / 触摸盘），地面有一条带门轨槽的**门槛 sill**，门后是一个**内部 reveal**（裸暗井道 5 板 ↔ 装修轿厢 ↔ 镜面轿厢）。成熟域 = 客梯 / 观光梯 / 货梯层门立面，矩形门洞，center-opening / side-telescopic / single-slide / 4-leaf telescopic 门机构，石材 / 大理石 / proud 线脚 portal / recessed alcove / 窄钢 pylon 围框。

不该混入的相邻类别见 §与相邻类别的边界。**特别注意**：本对象是**层站立面**，不是 freestanding 井道机器（无 hoistway / 行驶轿厢沿竖轨升降 / 对重 / 曳引轮），也不是普通门 / 闸门（它以门洞上方立面 + 楼层指示器 + 厅呼面板 + 门后 reveal 的整套层站语义为身份，门叶尺度 ≤ 半门洞、装在窗台之上的立面而非整扇落地通行门）。

## 槽位 + 候选模块表

### Slot A：door_mechanism（滑动门叶机构 — 全部 PRISMATIC 沿 X，leaf 数 1/2/4 与机构耦合）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| center_opening_2leaf（基线） | rec_a-passenger-...f45c0537 (P1) / rec_a-lobby-...a14558c5 (P2) | P1：`_leaf_shape(sign)` L150-167 + `wall_to_left_door` PRISMATIC axis(-1,0,0) L400-410 + `wall_to_right_door` axis(1,0,0) L411-421；P2 同型 `_door_leaf_shape` L213-232 + L530-548 | eligible if compatible | 2 叶在中缝 x=0 相接，镜像对向 ±X 平移；leaf_count=2 |
| side_opening_telescopic_2leaf | rec_elevator_var_side_telescopic | `_leaf_shape(x_center, y_center)` L153-173 + leaf_specs（door_0 fast/front-track travel 0.62、door_1 slow/rear-track travel 0.31）L367-381 + 关节 loop 同向 axis(-1,0,0) per-leaf travel L407-418；两轨 Y `TRACK_FRONT_Y/REAR_Y` L62-63 | eligible if compatible | 2 叶同侧 -X 滑、leading 远 / trailing 近，open 时 -X 侧 nested 重叠；两叶 offset Y 轨 |
| single_slide_1leaf | rec_elevator_var_single_slide | `_door_leaf_shape` 全宽单板 L152-168 + `DOOR_TRAVEL = OPEN_W+0.05` L70 + `wall_to_door` 单 PRISMATIC axis(-1,0,0) L395-405 | eligible if compatible | 1 全门洞宽板向 -X 滑进墙口袋（货 / 服务梯）；leaf_count=1 |
| center_opening_telescopic_4leaf | rec_elevator_var_center_four_leaf | `_leaf_shape(side, leaf_idx)` L137-164 + side×leaf 嵌套 loop 发 4 叶 + per-leaf PRISMATIC（inner travel 0.82 / outer 0.42）L326-359；两轨 `FRONT/REAR_TRACK_CY` L59-60 | eligible if compatible | 4 叶（每侧 2 叶 inner/outer），inner 在中缝相接、outer 在 rear track，inner travel 远 / outer 近，open 时每侧 nested 在 jamb；leaf_count=4 |

降级说明：4 候选，无降级。每个改变 leaf 数（1/2/4）+ joint 数 + 平移拓扑（镜像对向 / 同向分级 / 单叶 / 4 叶分级两轨）→ 拓扑等价类。

### Slot B：surround_facade（固定 root 围框；门洞坐落其中）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_stone_wall（基线） | rec_a-passenger-...f45c0537 (P1) / rec_a-lobby-...a14558c5 (P2) | P1 `_granite_wall_shape`（平 slab through-cut）L115-126 + `_jamb_shape` L129-147；P2 `_marble_surround_shape`（marble + 浅 reveal step + dado groove）L99-141 | eligible if compatible | 平墙板，门洞是 through-cut；root part `wall_surround` |
| proud_architrave_portal | rec_elevator_var_proud_architrave | `_architrave_shape`（3 级阶梯，每级向 -Y 凸 ARCH_STEP_DEPTH、外缘 narrowing，ARCH_STEPS loop）L161-195 + architrave visual on wall L381-385；ARCH dims L96-103 | eligible if compatible | 凸出墙前的阶梯线脚 portal 框，绕门洞向 -Y 凸 ~48mm |
| recessed_alcove | rec_elevator_var_recessed_alcove | `_granite_wall_shape`（墙前切 alcove pocket + 门洞穿后壁）L122-144 + `_side_reveal_shape` L147-150 + `_top_reveal_shape` L153-159 + `_back_reveal_shape` L162-176 + reveal panels loop L371-387；ALCOVE dims L51-53；门退到 alcove 后部 `DOOR_FRONT_Y=ALCOVE_D-LEAF_T` L65 | eligible if compatible | 门洞沉入墙前 niche，四面（L/R/top/back-header）brushed-steel reveal 板，门在 alcove 后平面 |
| metal_framed_pylon | rec_elevator_var_metal_pylon | `_frame_member` L114-123 + `_infill_panel` L126-130 + mullions loop L291-298 + head_beam L301-306 + 侧 infill loop L309-320 + upper_infill L322-332；FRAME dims L44-54；root part `frame` L288 | eligible if compatible | 窄钢门框：2 竖 mullion + head beam + 薄 sheet infill（观光 / 玻璃井道）；root 是 `frame` 不是宽石墙 |

降级说明：4 候选，无降级。每个改变 root primitive / 门洞承载方式（平 through-cut / proud 线脚叠加 / niche+reveal 多板 / 窄金属框架）→ 拓扑等价类。

### Slot C：interior_reveal（门开后门洞内显示的内部）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bare_dark_shaft（P1 基线） | rec_a-passenger-...f45c0537 (P1) | `_shaft_recess_shape`（back+L+R+ceil+floor 5 薄板暗盒）L170-198 + 作 `wall_surround` parent visual L329-331 | eligible if compatible | 浅暗 5 板井道盒（depth ~0.35），无家具；wall 的 parent visual |
| furnished_cab（P2） | rec_a-lobby-...a14558c5 (P2) | `_cab_shell_shape`（深 cab 壳 back+side+ceil）L235-274 + `_cab_back_panels_shape`（teal 墙板）L277-311 + `_ceiling_shape` L314-322 + `_floor_shape` L325-333 + `_handrail_shape` L336-363；`surround_to_cab` FIXED L464-470 + `cab_to_handrail` FIXED L482-488 | eligible if compatible | 深 ~1.5 装修轿厢：壳 + teal 墙板 + 扶手 handrail + ceiling + floor；独立 FIXED `cab_interior` part（+ handrail FIXED 子件） |
| mirror_panel_cab | rec_elevator_var_mirror_cab | `_mirror_panel_shape`（后壁大镜）L277-290 + `_mirror_trim_shape`（两侧抛光竖条）L293-311 + `_cab_side_panels_shape` L314-325 + ceiling/floor 同 P2；cab visuals L423-459（**无 handrail**） | eligible if compatible | 装修轿厢但后壁是大反射镜面 + 抛光 trim，去掉扶手 |

降级说明：3 候选，无降级。bare_dark_shaft = wall 的薄板 parent visual（无独立 cab part）；furnished/mirror = 独立 FIXED `cab_interior` part（深盒 + 子装修，furnished 多 handrail FIXED 子件、mirror 多镜面/trim visual 去 handrail）→ part tree / joint count 不同 → 拓扑等价类。

### Slot D：landing_fixtures（楼层指示器 + 厅呼控制；FIXED 到 wall，可整体移除）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| digit_indicator+call_plate（基线） | rec_a-passenger-...f45c0537 (P1) | `_indicator_box_shape` L225-230 + `_digit_shape`（7-seg 红 "1" + 上箭头）L233-269 + `_call_plate_shape` L272-279 + `_call_buttons_shape`（up/down 双钮）L282-301；`wall_to_indicator`/`wall_to_call_panel` FIXED L376-389 | eligible if compatible | 黑盒 + 红 7 段数字 + 小 up/down 双按钮呼叫盘；两独立 FIXED part |
| arrow_lantern+large_panel | rec_elevator_var_arrow_lantern | `_lantern_housing_shape` L240-258 + `_lantern_backplate_shape` L261-273 + `_arrow_lens_shape`（up/down 三角箭头 emissive）L276-305 + 大 `_call_plate_shape` L308-316 + 单大钮 `_call_button_shape` L319-330；combined housing L368-388 | eligible if compatible | 上下双箭头 lantern cluster（housing+backplate+amber 箭头透镜）+ 更大单按钮呼叫盘 |
| lcd_strip+touch_call | rec_elevator_var_lcd_strip | `_lcd_strip_face_shape`（宽 flat emissive LCD 条）L233-253 + `_touch_button_shape`（flush 触摸圆盘）L266-286；IND 宽条 dims L70-74 / PLATE 窄 L76-81；indicator/call_panel parts L319-338 | eligible if compatible | 宽 LCD 显示条 + flush 电容触摸单盘 |
| minimal_none | rec_elevator_var_minimal | build 仅 wall+sill+doors（无 indicator/call_panel part）L212-278；tests 断言 `"indicator" not in parts` / `"call_panel" not in parts` L294-305 | eligible if compatible | 无指示器、无呼叫盘（后勤 / 货梯层）；只剩 wall + sill + doors |

降级说明：4 候选，无降级。digit/lantern/lcd 改变 indicator/call_panel 的 part 内 visual primitive（7-seg vs 双箭头 lantern cluster vs LCD 条 / 双钮 vs 大单钮 vs 触摸盘）；minimal_none 直接删掉两个 FIXED part（part / joint count 减少）→ 拓扑等价类。

## 槽位图（slot graph）

pattern: mixed（parallel_children 固定 named slots + 一条 door_leaf multiplicity 轴 + leaf-count gating by Slot A）

```
                 door_mechanism (Slot A)  决定 leaf 数(1/2/4) + PRISMATIC 轴方向/travel 分级 + 是否两轨 offset Y
                          │
                          ▼
  [root: wall_surround / frame] ──parent visual──> { jamb, shaft/reveal(Slot C bare), sill 槽,
      (静态 root part, Slot B)                       architrave(B portal) / reveal panels(B alcove) /
      │                                              mullion+infill(B pylon) }
      │
      ├─ Slot D landing_fixtures（可选, FIXED 到 wall, minimal=移除）
      │     ├─[FIXED]─> indicator   （embed 进 wall 门洞上方, seated overlap+contact）
      │     └─[FIXED]─> call_panel  （embed 进 wall 门洞旁 ~1.1m, seated overlap+contact）
      │
      ├─[FIXED]─> sill              （门槛 butt 进 wall 前面, z≈0, 门轨槽）
      │
      ├─ Slot C interior_reveal
      │     ├─ bare_dark_shaft  → wall 的 parent visual（无独立 part）
      │     └─ furnished/mirror → [FIXED surround_to_cab]─> cab_interior（深盒）
      │                              └─ furnished 多 [FIXED cab_to_handrail]─> handrail
      │
      └─ door_leaf multiplicity（Slot A, leaf_count ∈ {1,2,4}）
            └─ for i in range(leaf_count):
                 leaf_{i}（独立 part）─[PRISMATIC axis ±X + per-leaf travel limit]─> wall/frame
                   （center=镜像对向 ±X；telescopic=同向 -X 分级 travel + offset Y 轨；
                     single=单叶 -X；4-leaf=每侧 inner/outer 两轨分级）
```

跨 slot 接口点位：

- **Slot A → root**：每片 leaf 的 PRISMATIC joint，origin 在 seated（closed）位置 / sill-track 面（pylon origin z=LEAF_BOTTOM，metal_pylon L386），axis ±X。leaf 顶/底在 jamb head / sill 门轨上滑（retained）。closed=q0 中缝相接 / 全覆盖；open=upper 让开门洞中心 ≥0.9·OPEN_W。
- **Slot B = FIXED root**：门洞 through-cut 是所有候选共同接口；leaf / indicator / call_panel / sill / cab 全部 anchor 到这个 root（`wall_surround` 或 `frame`）。
- **Slot C 接口**：bare = wall 门洞内薄板 parent visual（y∈[0,0.35]）；furnished/mirror = `surround_to_cab` FIXED，cab front 平面 flush 门洞后（CAB_FRONT_Y=WALL_T），深退 +Y。
- **Slot D 接口**：indicator FIXED 在门洞上方（z>OPEN_H），call_panel FIXED 在门洞旁（cx>OPEN_HALF，0.9<cz<1.3）；各 embed 进 wall 前面（seated overlap + `expect_contact`）。minimal=两 part 都不建。

互斥 / 派生 / gating：
- **leaf_count 由 Slot A 决定**：single=1 / center_2leaf=2 / side_telescopic=2 / center_4leaf=4。telescopic（side / 4-leaf）强制两叶/两组 **offset Y 轨** + 同侧/分级 travel；center=镜像对向轴。
- **metal_framed_pylon × {furnished_cab, mirror_panel_cab}**：低优先（源 map 排除项）—— 玻璃 / 金属观光 pylon 通常配裸 / 玻璃井道而非全装修不透明轿厢；compatibility matrix gate furnished/mirror cab 仅配 {flush_stone_wall, proud_architrave_portal, recessed_alcove}，pylon 默认配 bare_dark_shaft。
- **minimal_none（D）× furnished_cab（C）**：允许但语义略怪（装修轿厢却无厅呼固件）——permitted，非结构冲突。

## 每槽位 Module Emits / Interfaces

### Slot A / module center_opening_2leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_door`/`right_door`（或 `door_0/1`），各 1 个 leaf visual | P1 / model.py:L363-373 |
| internal joints | 无（leaf 内无活动子件） | — |
| upstream interface | leaf 顶/底在 jamb head / sill 门轨滑（seated overlap，可 allow_overlap+contact） | P2 / model.py:L575-602 |
| downstream interface | `wall_to_left_door` PRISMATIC axis(-1,0,0) + `wall_to_right_door` axis(1,0,0)，origin seated center，upper=DOOR_TRAVEL(~0.52) | P1 / model.py:L400-421 |

### Slot A / module side_opening_telescopic_2leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0`(leading/front-track)、`door_1`(trailing/rear-track) | side_telescopic / model.py:L367-381 |
| internal joints | 2× PRISMATIC **同向 axis(-1,0,0)**、per-leaf travel（0.62 / 0.31） | side_telescopic / model.py:L407-418 |
| upstream interface | 两叶 offset Y 轨（TRACK_FRONT_Y -0.030 / TRACK_REAR_Y -0.010）避免互穿 | side_telescopic / model.py:L62-63 |
| downstream interface | open 时两叶 nested 在 -X 侧、X 重叠 >0.05、保持不同 Y 轨 | side_telescopic / model.py:L507-555 |

### Slot A / module single_slide_1leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（单全宽板） | single_slide / model.py:L364-368 |
| internal joints | 1× PRISMATIC axis(-1,0,0)，upper=OPEN_W+0.05(~1.20) | single_slide / model.py:L395-405 |
| upstream interface | 单叶在 sill 门轨滑，closed 全覆盖门洞、居中 | single_slide / model.py:L456-483 |
| downstream interface | open 右缘越过门洞左缘（让全空门洞） | single_slide / model.py:L486-494 |

### Slot A / module center_opening_telescopic_4leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_inner/left_outer/right_inner/right_outer`（side×leaf 嵌套 loop 发 4 叶） | center_four_leaf / model.py:L332-344 |
| internal joints | 4× PRISMATIC（左 axis -X / 右 axis +X），inner travel 0.82 / outer 0.42 分级 | center_four_leaf / model.py:L348-359 |
| upstream interface | inner 在 front track / outer 在 rear track（offset Y），outer 在 rear 时 element-scoped allow_overlap 进 granite_slab/shaft_recess | center_four_leaf / model.py:L435-454, L584-592 |
| downstream interface | open 每侧 inner+outer nested 在 jamb，clear gap >0.8·OPEN_W | center_four_leaf / model.py:L514-542 |

### Slot B / surround_facade emits
| emits | 描述 | 来源 |
|---|---|---|
| flush_stone_wall | root `wall_surround`：slab through-cut + jamb；P2 加 marble reveal step + dado groove | P1 L115-147 / P2 L99-141 |
| proud_architrave_portal | wall 多 `architrave_frame` visual（ARCH_STEPS loop 阶梯线脚向 -Y 凸） | proud_architrave / model.py:L161-195, L381-385 |
| recessed_alcove | `_granite_wall_shape` 切 alcove pocket + 后壁门洞 + 4 reveal 板（side loop + top + back-header）；门退 alcove 后部 | recessed_alcove / model.py:L122-176, L371-387 |
| metal_framed_pylon | root `frame`：mullion loop + head_beam + 侧/上 infill loop（窄金属框） | metal_pylon / model.py:L291-332 |

### Slot C / interior_reveal emits
| emits | 描述 | 来源 |
|---|---|---|
| bare_dark_shaft | `shaft_recess` 5 薄板暗盒，wall 的 parent visual（无独立 part / joint） | P1 / model.py:L170-198, L329-331 |
| furnished_cab | 独立 `cab_interior` part（shell+teal 板+ceiling+floor）+ `handrail` FIXED 子件；`surround_to_cab`/`cab_to_handrail` FIXED | P2 / model.py:L235-363, L461-488 |
| mirror_panel_cab | `cab_interior`（shell+大镜面+抛光 trim+side 板+ceiling+floor，去 handrail）；`surround_to_cab` FIXED | mirror_cab / model.py:L277-325, L423-467 |

### Slot D / landing_fixtures emits
| emits | 描述 | 来源 |
|---|---|---|
| digit_indicator+call_plate | `indicator`(box+7seg 红数字+箭头) + `call_panel`(plate+up/down 双钮)，两 FIXED part | P1 / model.py:L225-301, L376-389 |
| arrow_lantern+large_panel | `indicator`(双箭头 lantern cluster：housing+backplate+amber 透镜) + `call_panel`(大 plate+单大钮) | arrow_lantern / model.py:L240-330, L364-399 |
| lcd_strip+touch_call | `indicator`(box+宽 LCD 条) + `call_panel`(窄 plate+flush 触摸盘) | lcd_strip / model.py:L233-286, L319-338 |
| minimal_none | 不建 indicator / call_panel（part / joint 减少） | minimal / model.py:L212-278 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_mechanism | enum | center_opening_2leaf / side_opening_telescopic_2leaf / single_slide_1leaf / center_opening_telescopic_4leaf | — | choice | 由 sampler 选择；决定 leaf_count(1/2/4) + 轴方向 + 是否两轨 offset Y | Slot A table |
| surround_facade | enum | flush_stone_wall / proud_architrave_portal / recessed_alcove / metal_framed_pylon | — | choice | 决定 root primitive；pylon gate Slot C（见 compatibility） | Slot B table |
| interior_reveal | enum | bare_dark_shaft / furnished_cab / mirror_panel_cab | — | choice | conditional：furnished/mirror 仅配 stone/portal/alcove（非 pylon） | Slot C table |
| landing_fixtures | enum | digit_indicator+call_plate / arrow_lantern+large_panel / lcd_strip+touch_call / minimal_none | — | choice | minimal_none 删除 2 FIXED part | Slot D table |
| door_leaf_count | int (count_param, Slot A 派生) | {1, 2, 4} | 2 | conditional | = f(door_mechanism)：single→1, center_2leaf/side_telescopic→2, center_4leaf→4；不独立采样 | Slot A multiplicity |
| palette_style | enum | dark_granite_steel / cream_marble_brass / blue_glass_pylon / light_stone_bronze / dark_metal_lcd / mirror_polished | dark_granite_steel | choice | 每 seed 抽一组 (wall/door/jamb/indicator/accent/shaft/sill/cab) rgba；不改拓扑（见下 palette） | 见 palette 来源 |
| wall_width_scale | float | [0.90, 1.15] | 1.0 | independent | clamp；缩放 WALL_W / FRAME_W（X 宽度） | P1 WALL_W L44 / pylon FRAME_W L54 |
| wall_height_scale | float | [0.92, 1.10] | 1.0 | independent | clamp；缩放 WALL_H / FRAME_H | P1 WALL_H L45 |
| opening_width_scale | float | [0.90, 1.12] | 1.0 | equation/independent | 缩放 OPEN_W；leaf_w 派生（见下）；4-leaf 默认更宽 OPEN_W~1.8 | P1 OPEN_W L50 / 4leaf L46 |
| opening_height_scale | float | [0.95, 1.06] | 1.0 | independent | clamp；缩放 OPEN_H（联动 LEAF_TOP/IND_CZ 派生） | P1 OPEN_H L51 |
| door_open_frac | float | [0.0, 1.0] | 0.0 | independent | 映射 joint q（rest 闭合）；× per-leaf motion_limits.upper | 各机构 motion_limits |
| (—) | constraint | — | — | equation | `LEAF_W = OPEN_W / leaf_count_per_pass`（center_2leaf=OPEN_W/2、single=OPEN_W、4leaf=OPEN_W/4、telescopic=OPEN_W/2）；leaf 高 = OPEN_H − LEAF_BOTTOM | P1 L54-57 / 4leaf L51 |
| (—) | constraint | — | — | inequality | `telescopic 两叶/两组 offset Y 轨 ≥ LEAF_T`：side/4-leaf front-track 与 rear-track Y 差 ≥ 一叶厚，否则滑动互穿，回缩或拒绝 | side_telescopic L62-63 / 4leaf L57-60 |
| (—) | constraint | — | — | inequality | `door travel 让开门洞`：center upper≈LEAF_W+margin（open center_gap>0.9·OPEN_W）；single upper≈OPEN_W+0.05；telescopic leading>trailing×1.5；4-leaf inner>outer+0.10 | 各机构 motion_limits |
| (—) | constraint | — | — | inequality | `indicator above opening`(z>OPEN_H) & `call_panel beside`(cx>OPEN_HALF, 0.9<cz<1.3) & `sill at floor`(z≈0)；缩放后仍满足，否则 clamp | P1 tests L549-563 |
| (—) | constraint | — | — | conditional | `furnished/mirror cab` 需要门后足够深（CAB_DEPTH~1.5）+ surround≠pylon；pylon⇒bare_dark_shaft | mirror_cab L71-80 / 源 map 排除项 |

palette_style 来源（≥3，目标 4-6，全部观测自 5★ 源）。每色映射全部材质角色 (wall / door / jamb·frame / indicator_housing / accent_lit / shaft_dark / sill / cab_panel)：

- **dark_granite_steel**（P1）：wall granite (0.17,0.17,0.20) / door steel (0.72,0.73,0.75) / jamb steel_dark (0.55,0.56,0.58) / indicator_black (0.04,0.04,0.05) / accent red_led (0.88,0.10,0.10) / shaft_dark (0.05,0.05,0.06) / sill steel / cab(若有) teal — P1 L98-104。
- **cream_marble_brass**（P2）：wall marble_cream (0.91,0.88,0.80) / door brass (0.84,0.66,0.26) / jamb·track brass / indicator amber housing / accent amber_lit (0.98,0.70,0.18) / shaft→cab teal_panel (0.16,0.33,0.40) / sill brass / cab brushed_metal handrail (0.70,0.72,0.74) + ceiling_white (0.90,0.90,0.86) + dark_cab_floor (0.20,0.20,0.22) — P2 L402-408。
- **blue_glass_pylon**（metal_pylon 派生）：frame steel_frame (0.42,0.44,0.48) / door steel (0.72,0.73,0.75) / infill 偏冷玻璃蓝 (0.30,0.36,0.44) / indicator_black / accent red_led / shaft_dark / sill steel — metal_pylon L96-102（infill 由 (0.32,0.34,0.38) 暖偏冷蓝，人工审核确认）。
- **light_stone_bronze**（proud_architrave 派生）：wall 浅石 (0.62,0.60,0.56) / architrave_stone 对比石 (0.24,0.23,0.27) / door 青铜 (0.46,0.40,0.30) / jamb bronze_dark (0.30,0.27,0.22) / indicator_black / accent amber (0.95,0.72,0.18) / shaft_dark / sill bronze — 由 architrave_stone L115 暖偏移派生（人工审核确认色值）。
- **dark_metal_lcd**（lcd_strip）：wall granite (0.17,0.17,0.20) / door steel / jamb steel_dark / indicator_black / accent lcd_glow 冷白 (0.75,0.88,0.95) / touch_face (0.22,0.22,0.24) / shaft_dark / sill steel — lcd_strip L98-104。
- **mirror_polished**（mirror_cab）：wall marble_cream / door brass / accent mirror_glass (0.92,0.93,0.94) + polished_trim (0.82,0.82,0.84) / cab teal_panel + ceiling_white — mirror_cab L386-393。

连续尺寸采样契约：先采 independent 主尺度（wall_width/height_scale、opening_width/height_scale、door_open_frac，均匀采样后 clamp）→ 按 equation 派生从属（LEAF_W=OPEN_W/leaf_pass，leaf_h=OPEN_H−LEAF_BOTTOM，IND_CZ/LANTERN_CZ=OPEN_H+offset）→ 用 inequality 把 telescopic offset-Y / door-travel-clear / fixture-placement 投影回缩或拒绝重采 → conditional（leaf_count by Slot A；furnished cab depth & ≠pylon）在采样前按 Slot A/B/C choice 解析。

## Multiplicity / Copy Logic

**一条 multiplicity 轴**（door_leaf，离散 enum 而非自由 N sweep）：

### 轴 A — door_leaf（门叶复制，count 与 Slot A 机构耦合）
- `count_param`：`door_leaf_count`，由 `door_mechanism` 派生（**非独立自由 N**）。
- `N_range`（本轴产品域）：`{1, 2, 4}`。样本已覆盖全部 distinct：single_slide(1) / center_2leaf+side_telescopic(2) / center_4leaf(4)。
- sampling domain：**不做加权 N sweep**——leaf 数是绑定门机构的离散 enum；每个机构当作一个 topology（4 个 Slot-A 候选已给 4 个 distinct leaf-count/joint 拓扑：1 叶单 PRISMATIC、2 叶镜像对向、2 叶同向分级两轨、4 叶分级两轨）。采样在 Slot A 选机构时一并定 leaf 数。
- copied object：一片门叶（共享 `_leaf_shape` helper，按 sign / (x_center,y_center) / (side,leaf_idx) 参数化）。
- naming：`left_door`/`right_door`（center），`door_{i}`（single / side_telescopic），`{side}_{inner|outer}`（4-leaf）。
- placement：center=对称 x=0 中缝；single=居中全宽；side_telescopic=同侧堆叠 + offset Y 轨；4-leaf=每侧 inner（中缝）/outer（jamb 侧）两轨。
- joint policy：每片叶各自一个 PRISMATIC（axis ±X），per-leaf travel limit（telescopic / 4-leaf = 分级 limit；center = 等 limit 对向轴）。
- source/gating：single_slide / side_telescopic / center_four_leaf 均已 loop 化发射门叶 + per-leaf joint（converged）；center_2leaf 在多数源是 2 次手写但 minimal/alcove 已 loop 化，模板用统一 `for i in range(leaf_count)` + 共享 helper 发射。

surround_facade（B）、interior_reveal（C）、landing_fixtures（D）为固定 named slot，**非复制轴**（不暴露 `*_count`，不循环复制模板级 facade/reveal/fixture）。注：Slot B alcove 的 4 reveal 板、pylon 的 2 mullion / 2 infill 是 module-local 固定子件（非模板级 multiplicity 轴），Slot C cab 的 teal 板 / trim 同理。

## 拓扑多样性审计

总组合数（slot 笛卡尔，未含连续 scale）：A × B × C × D = **4 × 4 × 3 × 4 = 192**。
door_leaf_count {1,2,4} 已绑定在 Slot A 的 4 个候选里（不额外乘）。compatibility gating（pylon⇒bare_dark_shaft，即 pylon 不配 furnished/mirror）后合法组合 ≈ 4×(3×4 + 1×... )；具体：B∈{stone,portal,alcove} 配 C∈{bare,furnished,mirror} = 3×3=9 facade×reveal；B=pylon 仅配 C=bare = 1；故 facade×reveal 合法 = 3×3+1 = 10，× A(4) × D(4) = **160 合法组合**，仍远超机械门槛。

理由：仅 A（4 leaf-count/joint 拓扑）× C（3 个改变 part tree 的 reveal：parent-visual / +cab part / +cab+handrail）已给 12 个拓扑不同组合；叠加 B（root primitive 不同）、D（含 minimal 删 2 part）后远超 10。每个 (A, B, C, D) 在 part count + joint count + leaf count 上都是不同 equivalence class（4-leaf=+2 part/+2 joint vs 2-leaf；furnished=+1 cab part +1 handrail part/joint；minimal=−2 part/−2 joint；pylon root=frame）。

seed_domain_policy：procedural_first（`seed=0` 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 先抽 Slot A door_mechanism（定 leaf_count + 轴 + 两轨/单轨）→ 抽 Slot B surround_facade → 抽 Slot C interior_reveal（gated：pylon⇒bare）→ 抽 Slot D landing_fixtures → 抽 palette_style → 采连续 scale 并 clamp/投影回可行域。compatibility matrix 在 `resolve_config` 内 gating 排除非法组合（见下）。少量 regression overrides 仅用于已知失败回归（telescopic 两叶 Y 互穿、4-leaf rear-track outer 穿 granite/shaft、pylon×furnished、minimal 误留 fixture part）。random sweep：seeds 0-49 初轮、0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别离散结构上限 = 160 合法 slot 组合，低于 300 时说明为 pylon×cab gating 与类别空间收窄；6 palette 只补视觉多样性，不计入 tuple。
Controlled local parameterization：wall_width_scale [0.90,1.15]、wall_height_scale [0.92,1.10]、opening_width_scale [0.90,1.12]、opening_height_scale [0.95,1.06]、door_open_frac [0,1]。全部在 `resolve_config` clamp/派生：LEAF_W=OPEN_W/leaf_pass（equation）；telescopic offset-Y、door-travel-clear、fixture placement（z>OPEN_H / beside / floor）、furnished cab depth 用 inequality 投影回缩或拒绝。这些 scale 不改变拓扑等价类、不破坏 InterfaceSpec（门洞 through-cut / PRISMATIC ±X 轨 / offset-Y 两轨 / cab FIXED 接口 / fixture seated-mount）/ MatingContract / leaf multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽序 A(定 leaf_count)→B→C(gated pylon⇒bare)→D→palette→连续 scale；slot_choices_for_seed 仅记录改变拓扑等价类的 enum（含 leaf_count、minimal 删 part、cab part 增减） | slot_choices_for_seed matches build choices |
| compatibility matrix | door_mechanism⇒leaf_count(1/2/4) + 轴方向 + telescopic offset-Y 两轨；metal_framed_pylon⇒interior_reveal=bare_dark_shaft（furnished/mirror 仅配 stone/portal/alcove）；furnished/mirror 需门后 CAB_DEPTH 足够深；minimal_none 删 indicator+call_panel；telescopic/4-leaf 两叶/两组必 offset Y ≥ LEAF_T 且 travel 分级 | no floating, collision, axis, leaf-count, bulky cab, optional fixture failures |
| controlled local variation | wall_width/height_scale、opening_width/height_scale、door_open_frac，全 clamp + 派生 LEAF_W/leaf_h/IND_CZ，违反 offset-Y / travel-clear / fixture-placement inequality 投影回缩 | proportions vary without breaking through-cut / PRISMATIC ±X 轨 / offset-Y / cab FIXED / fixture seated-mount / identity |
| regression overrides | none（首版）/ 仅 telescopic Y 互穿、4-leaf rear-track outer 穿 granite/shaft、pylon×furnished gate、minimal 误留 fixture（如出现）按 seed 记录原因 | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A door_mechanism | 4 | yes | yes | center_2leaf / side_telescopic / single_slide / center_4leaf（含 leaf-count multiplicity {1,2,4}） |
| B surround_facade | 4 | yes | yes | flush_stone / proud_architrave / recessed_alcove / metal_pylon |
| C interior_reveal | 3 | yes | yes | bare_dark_shaft / furnished_cab / mirror_panel_cab |
| D landing_fixtures | 4 | yes | yes | digit+call / arrow_lantern+large / lcd+touch / minimal_none |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D enum + leaf_count + minimal 删 part / cab part 增减标记）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（`seed=0` 不特殊）
- compatibility matrix / gating prevents illegal module combinations（leaf_count by A；pylon⇒bare reveal；furnished/mirror 需深 cab + 非 pylon；telescopic offset-Y 两轨 + 分级 travel；minimal 删 2 fixture part）
- optional regression overrides are sparse and justified（仅 telescopic Y 互穿 / 4-leaf rear-track 穿模 / pylon×furnished / minimal 误留 fixture 已知风险）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (wall_width/height_scale, opening_width/height_scale, door_open_frac) are clamped and cannot break 门洞 through-cut / PRISMATIC ±X 轨 / offset-Y 两轨 / cab FIXED 接口 / fixture seated-mount / leaf multiplicity
- cross-part scale dependencies (LEAF_W=OPEN_W/leaf_pass equation；offset-Y / door-travel-clear / fixture-placement inequality；leaf_count / furnished-cab conditional) resolved in `resolve_config`, not in builder
- critical InterfaceSpec / MatingContract points exist：门洞 through-cut（所有 B）、PRISMATIC ±X 门轨（所有 A）、telescopic offset-Y 两轨（side/4-leaf）、surround_to_cab FIXED（furnished/mirror）、indicator/call_panel/sill seated-mount overlap+contact、4-leaf rear-track outer element-scoped allow_overlap
- key joints have expected type/axis/range：center 门叶 PRISMATIC 镜像 axis(∓1,0,0) 等 limit；telescopic 2 叶同向 axis(-1,0,0) 分级 limit；single 1 叶 PRISMATIC(-1,0,0)；4-leaf 每侧 inner/outer PRISMATIC(±1,0,0) 分级；indicator/call_panel/sill/cab/handrail FIXED；**无任何 REVOLUTE swing 门**
- copied objects follow naming and placement policy：`left_door`/`right_door` / `door_{i}` / `{side}_{inner|outer}`；每叶 closed=q0 中缝相接/全覆盖，open=upper 让开门洞中心，纯 ±X 平移无 Y/Z 漂移（telescopic 保持各自 Y 轨）
- minimal_none：断言 indicator / call_panel part 真的不存在；其余 D 候选 indicator 在 z>OPEN_H、call_panel beside（cx>OPEN_HALF, 0.9<cz<1.3）

## Reject cases

- REVOLUTE swing 门 / 铰链门作为 identity —— 本类别门叶仅 PRISMATIC 沿 X 滑动；任何 swing 门属 door/gate 小类，必拒。
- freestanding 井道机器（hoistway 沿竖轨升降的 traveling cab / counterweight / drive sheave / guide rails）—— 那是被误读的旧对象，必拒；本类别是固定层站立面，cab/shaft 只是门后 reveal、不沿 Z 行驶。
- 门叶 q=0 不闭合 / 不在中缝相接 / 不全覆盖门洞，或 open 不让开门洞中心（center_gap < 0.9·OPEN_W）。
- telescopic（side / 4-leaf）两叶 / 两组未 offset Y 轨（< LEAF_T）→ 滑动互穿；或 travel 未分级（leading≯trailing / inner≯outer）。
- indicator/call_panel/sill 漂浮（未 embed seated、无 `expect_contact`）；或 indicator 不在门洞上方 / call_panel 不在门洞旁 hand height / sill 不在 z≈0。
- metal_framed_pylon 强配 furnished/mirror 不透明轿厢（低优先排除项未 gate）；或 furnished/mirror cab 门后深度不足（cab 穿出门洞前 / 与门叶碰撞）。
- minimal_none 误留 indicator / call_panel part；或非 minimal 漏建 fixture。
- root 不站立（sill / wall 不在 z≈0）、不高于 / 宽于门洞、深度 > 高度（躺倒）；或 cab 未 FIXED 到 surround（漂浮断开）。
- 4-leaf rear-track outer 叶未对 granite_slab/shaft_recess element-scoped allow_overlap → 误报穿模 fail。

## 与相邻类别的边界

- 不该混入：**Elevator hoistway / shaft machine（井道机器，被误读的旧对象）** —— 那是 freestanding 竖井 + 沿竖导轨升降的行驶轿厢 + 对重 + 曳引轮；本小类是固定层站立面，门后 cab/shaft 只是静态 reveal，门叶沿 X 平移而非轿厢沿 Z 行驶。
- 不该混入：**普通门 / 闸门 / sliding door（落地通行门）** —— 那些可能是 REVOLUTE swing 或整扇落地通行；本小类门叶是窗台之上立面里的金属门、配楼层指示器 + 厅呼面板 + 门后 reveal 的整套层站语义，门叶尺度 ≤ 半门洞、有 sill 门槛槽 + 门洞上方 indicator。
- 不该混入：**Curtain wall / Facade element（幕墙 / 立面构件）** —— 幕墙是大面积无开启的固定玻璃格栅；本小类必须至少一片 category-defining 可动 PRISMATIC 滑动门叶 + 门洞 + 楼层指示器 + 厅呼，尺度为单层站入口而非整面立面。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；12/12 五星样本（2 parent + 10 converged variant）逐行全读，每候选解析真实 `model.py:Lx-Ly`。**全新 spec，完全替换旧的误读 freestanding-shaft spec**——真实对象是 elevator landing entrance（墙围框 + 门洞 + 滑动门叶 + 楼层指示器 + 厅呼面板 + 门槛 sill + 门后 reveal）。4 槽 door_mechanism(4)/surround_facade(4)/interior_reveal(3)/landing_fixtures(4) + door_leaf multiplicity{1,2,4}（绑 Slot A）+ compatibility matrix（pylon⇒bare reveal 排除项）+ palette 6 色已写；total combos 192（gated ~160 合法）；富余可过。等待人工审核后再进入 TEMPLATE_AFTER_REVIEW。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | center_opening_2leaf / flush_stone_wall / bare_dark_shaft / digit_indicator+call_plate | rec_a-passenger-...f45c0537 (P1) | L115-L423 | 基线母体：granite 平墙 through-cut + jamb + 5 板暗井道 + 2 叶镜像 PRISMATIC ±X + 7seg 数字 + up/down 呼叫盘 + sill |
| S2 | A/B/C/D | center_opening_2leaf / flush_stone_wall / furnished_cab / lit_indicator+call_plate | rec_a-lobby-...a14558c5 (P2) | L99-L550 | marble 平墙 + brass 2 叶 + 深装修轿厢(shell+teal 板+handrail+ceiling+floor, surround_to_cab/cab_to_handrail FIXED) + lit amber indicator |
| S3 | A | side_opening_telescopic_2leaf | rec_elevator_var_side_telescopic | L153-173, L62-63, L367-418 | 2 叶同向 -X 分级 travel(0.62/0.31) + offset Y 两轨 nested 母体 |
| S4 | A | single_slide_1leaf | rec_elevator_var_single_slide | L152-168, L70, L395-405 | 单全宽板 1 叶 PRISMATIC(-X) travel=OPEN_W+0.05 |
| S5 | A | center_opening_telescopic_4leaf | rec_elevator_var_center_four_leaf | L137-164, L57-60, L326-359, L435-454 | 4 叶 side×leaf 嵌套 loop + per-leaf 分级 PRISMATIC(±X) + rear-track outer allow_overlap 母体 |
| S6 | B | proud_architrave_portal | rec_elevator_var_proud_architrave | L96-103, L161-195, L381-385 | 3 级阶梯线脚 portal 向 -Y 凸（ARCH_STEPS loop） |
| S7 | B | recessed_alcove | rec_elevator_var_recessed_alcove | L51-53, L122-176, L371-387 | 墙前 niche + 4 面 reveal 板（side loop+top+back-header）+ 门退 alcove 后部 |
| S8 | B | metal_framed_pylon | rec_elevator_var_metal_pylon | L44-54, L114-130, L288-332 | 窄钢框 root `frame`：mullion loop + head beam + 薄 infill loop |
| S9 | C | mirror_panel_cab | rec_elevator_var_mirror_cab | L82-87, L277-325, L423-467 | 装修轿厢 + 后壁大镜面 + 抛光 trim + 去 handrail |
| S10 | D | arrow_lantern+large_panel | rec_elevator_var_arrow_lantern | L70-93, L240-330, L364-399 | 上下双箭头 lantern cluster(housing+backplate+amber 透镜) + 大单按钮呼叫盘 |
| S11 | D | lcd_strip+touch_call | rec_elevator_var_lcd_strip | L70-81, L233-253, L266-286, L319-338 | 宽 LCD 显示条 + flush 触摸单盘 |
| S12 | D | minimal_none | rec_elevator_var_minimal | L212-278, L294-305 | 删 indicator+call_panel，仅 wall+sill+doors（part/joint 减少） |

## 模板实现备注（可选）

- Slot A 4 机构共享 `_leaf_shape` helper（按 sign / (x_center,y_center) / (side,leaf_idx) 参数化）+ 统一 `for i in range(leaf_count)` 发射门叶 + per-leaf PRISMATIC joint；travel/轴/Y 轨由机构 gate。
- captured-mount overlap 须 element-scoped allow_overlap：indicator↔wall（门洞上方 embed）、call_panel↔wall（门洞旁 embed）、sill↔wall（门槛 butt）、telescopic/4-leaf 门叶↔门轨、4-leaf rear-track outer↔granite_slab/shaft_recess、cab↔surround（门洞后 flush）、handrail↔cab。每个 `door_{i}`/`cab`/fixture 须重复声明 + `expect_contact` 证明 seated（参 P1 L444-462、4leaf L435-454）。
- **telescopic offset-Y 两轨是核心收敛点**：side / 4-leaf 两叶 / 两组必须 offset Y ≥ LEAF_T（side TRACK_FRONT/REAR_Y L62-63、4leaf FRONT/REAR_TRACK_CY L59-60），否则滑动 sweep 时门叶互穿。run_tests 须断言「两叶在不同 Y 轨」+「leading travel > trailing×1.5 / inner > outer+0.10」（参 side_telescopic L497-555、4leaf L544-592）。
- **pylon×cab gating** 是已知收敛风险：`resolve_config` 须强制 metal_framed_pylon⇒bare_dark_shaft；furnished/mirror cab 仅配 stone/portal/alcove，且门后深度足够（CAB_DEPTH~1.5，cab front flush 门洞后）。
- minimal_none 须真正不建 indicator/call_panel part（不是建后隐藏）；run_tests 须断言两 part 缺席（参 minimal L294-305）。
- bare_dark_shaft 是 wall 的 parent visual（无独立 part），furnished/mirror 是独立 FIXED `cab_interior` part——slot_choices_for_seed 须把这个 part-tree 差异计入拓扑等价类。
