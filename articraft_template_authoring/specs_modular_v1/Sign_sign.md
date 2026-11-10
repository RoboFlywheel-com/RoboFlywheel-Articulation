# sign — Modular Spec

> SPEC_ONLY draft. Authored from the 9 five-star sources in `data/records/<id>/revisions/rev_000001/model.py`.
> Identity: real-world sign assemblies. The template now covers several common manufactured sign families:
> folding floor caution A-frames, roadside/post-mounted signs, hanging blade signs, wall plaques, and table
> tent signs. Articulation is family-specific and mandatory: every sampled seed must contain at least one
> non-fixed joint. A-frames and table tents fold, hanging blade signs swing from a bracket, roadside faces
> swivel on adjustable post brackets, and wall plaques open on a side service hinge.

## 元信息
| 项 | 值 |
|---|---|
| slug | `sign` |
| template path | `agent/templates/Sign_sign.py` |
| test path (optional) | `tests/agent/test_sign_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（top-level sign_type + fixed named slots face_shape / graphic_style + legacy A-frame panel_profile / base_support / handle_mechanism + apex-knuckle multiplicity axis + optional tether linear_chain axis） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

阅读要点（两个 spine 家族；模板取 Family B 为 canonical apex frame）：

- **Family B — canonical（Y-axis fold, discrete knuckles）**：001.png parent + gabled + shield + base_feet + knuckles2 + knuckles5 共 6 源。约定：panel 在自身 local frame 中 apex line 位于 `z=0`、面板沿 `-Z` 下垂、宽度沿 `Y`、可见正面朝 `+X`、厚度沿 `+X`；front panel = root 并 visual 预倾 `rpy=(0,-APEX_HALF_OPEN,0)`，back panel = child 预倾 `+APEX_HALF_OPEN`，apex hinge `axis=(0,1,0)`、`lower=0, upper≈2.4`、q=0 即开启 A 字形。knuckle barrel 是离散 Y 轴短圆柱沿宽度排布、骑跨 pin line 捕获对侧 leaf（element-scoped allow_overlap + expect_contact）。warning placard = front panel 上的 raised visual（hazard triangle + text bands）。**此 spine 原生支持 knuckle_count multiplicity**，故选为 canonical。
- **Family A — adapted（X-axis fold, single wide barrel）**：002.png parent + handle_swivel + clip_chain 共 3 源。约定：panel 面在 X-Z 平面、厚度沿 `+Y`、fold `axis=(1,0,0)`、q=0 开启、`lower=-2*HALF_SPLAY, upper≈0.05`；单个宽 hinge barrel + skirt（`_build_hinge_handle`）一体连接两 leaf；corner feet 烘进 panel shell；graphic plate 内嵌。这 3 源贡献 **handle 机构（fixed grab-hole 的 barrel+skirt 写法、swing-up bail revolute、spreader chain linear_chain）** 与 corner-feet/vent-slot 写法；在 canonical apex frame 下采用时做一次 X↔Y 轴与 +Y↔+X 厚度方向的坐标映射（见实现备注）。
- 两家族都满足 identity（A 字形折叠、apex revolute、carry handle 近 apex、printed warning placard），neighbor 边界一致（非 street/post/hanging/billboard sign）。

## 核心身份

Sign / sign = **真实世界中的标识牌/警示牌/导视牌总类**，不是单一的 wet-floor 警示牌。物理本体必须包含可读的板面、可信的安装/支撑方式、以及至少一个真实的非 fixed 关节：立柱可调 swivel、墙臂吊牌摆动、侧铰链服务门、桌牌折痕、或便携 A-frame 铰链。板面可用几何 relief 表达 warning symbol、wayfinding arrow、shop mark、street-name bands、notice bands，避免生成无意义的红色尖片和横杆堆叠。

真实子域：

- `floor_caution_a_frame`：保留原来的注塑塑料 A 字警示牌，两片 leaf 顶端 apex hinge 折叠，可带 knuckle、脚垫、提梁、tether。
- `roadside_post`：路侧/园区/停车场标识，单立柱 + 背面横向 mounting rails + 薄板面，通常为矩形、圆形、八边形或圆角矩形；面板通过可调 post bracket 小角度转向。
- `hanging_blade`：店铺/室内导视悬挂牌，墙面 bracket + 横臂/横杆 + 两个吊环，板面可绕横杆轻微摆动。
- `wall_plaque`：门牌、铭牌、告示牌，浅薄板面 + 螺丝帽固定；采用真实常见的侧边 service hinge，可像检修盖/可更换铭牌面一样打开。
- `table_tent`：桌面菜单/预订/告示牌，两片小板绕顶部折痕/铰链形成浅 A 形轮廓，无需强行做成大型地面警示牌。

不该混入的相邻类别：大型 billboard/广告牌桁架、纯布 banner、无支撑的抽象 logo 雕塑、完全没有板面信息的机械架子。A-frame 只是一个 sign family，不再作为整个 `Sign/sign` 的唯一身份。

## 顶层槽位

### Slot 0：sign_type（真实结构族）

| module_name | 结构特征 | articulation policy |
|---|---|---|
| floor_caution_a_frame | 双 leaf 注塑警示牌，顶端 knuckle/apex hinge，正反两面 warning placard | `apex_hinge` REVOLUTE；可选 `handle_pivot`、tether links |
| roadside_post | 竖直金属/塑料 post，薄面板装在背面 rails / 可调夹具上 | `post_swivel` REVOLUTE，小角度绕立柱调朝向 |
| hanging_blade | 墙面 bracket + 横臂/挂杆，板面通过吊环悬挂 | `hanging_swing` REVOLUTE，小角度摆动 |
| wall_plaque | 墙面浅板，四颗螺丝帽/铆钉固定，浮雕或条带信息 | `plaque_hinge` REVOLUTE，侧边检修/换面铰链 |
| table_tent | 小型桌面折叠牌，双面 relief 信息 | `tent_crease` REVOLUTE，顶部折痕/薄铰链 |

### Generic face slots（非 A-frame family 也使用）

| slot | candidates | 说明 |
|---|---|---|
| face_shape | rectangle / rounded_rect / circle / octagon / arrow | 按 sign_type 过滤非法组合，例如 hanging_blade 不采八边形/箭头外轮廓 |
| graphic_style | warning / wayfinding / shop / street_name / notice | 用 relief 几何表达真实标识信息，不依赖随机文字 |

下面的 `panel_profile`、`base_support`、`handle_mechanism`、`knuckle_count`、`tether_chain` 继续服务于 `floor_caution_a_frame` family，以保留原有高细节和多样性。

## 槽位 + 候选模块表

### Slot A：panel_profile（面板轮廓 —— 主结构轴；apex fold REVOLUTE 保持不变）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_top | rec_build-a-realistic-articulated-3d-model-of-a-sign_20260609_215026_933125_3171150b | `_panel_shell` L58-L121（profile 主轮廓 L71-L79 threePointArc 顶弧 + cavity L87-L94 + handle_cut L97-L104 + ribs L106-L120） | eligible if compatible | 宽底 + threePointArc 圆顶弧顶边；hollow shell；含 rib 选项 |
| trapezoidal_tapered | rec_build-a-realistic-articulated-3d-model-of-a-sign_20260609_215029_914922_9ae01b65 | `_panel_profile` L63-L76（直边梯形 4 点）+ `_build_panel_shell` L79-L125（extrude + shell + vent slots L110-L120） | eligible if compatible | 直边梯形,底宽顶窄；shelled 背面；下部 vent slots 循环 |
| gabled_peaked | rec_sign_var_profile_gabled | `_gable_top_z` L67-L79 + `_panel_shell` L82-L146（5 点 pentagon profile L95-L104 双坡尖顶） | eligible if compatible | 双坡尖顶（house/pentagon）silhouette；knuckle Z 随 gable 顶边变化 |
| shield | rec_sign_var_profile_shield | `_shield_profile_wire` L64-L117（threePointArc 链：圆顶弧 + 近垂直侧 + 下扫至底尖）+ `_panel_shell` L120-L170 | eligible if compatible | 盾形：圆顶 + 直侧 + 下部内收圆角下尖；cavity 局限上区 |

### Slot B：base_support（底部稳定结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush_slab | rec_build-a-realistic-articulated-3d-model-of-a-sign_20260609_215026_933125_3171150b | `_panel_shell` L58-L121（底边 `lineTo(±half_w,-height)` L76-L77，无额外 foot 件，面板底边直接落地） | eligible if compatible | 面板底边直接落地，无外撇脚 |
| corner_feet | rec_sign_var_base_feet | `_outrigger_foot` L137-L173（外撇脚 pad）+ 发射循环 L270-L277（front）/ L314-L321（back，loop `foot_{i}` 命名） | eligible if compatible | 两底角外撇 molded foot pad，加宽前后脚印；left/right loop 发射、fused 入 shell 不增 joint |

> corner_feet 的第二来源（写法对照）：002.png parent `_build_panel_shell` 内 `foot` box + left/right union L102-L106（脚烘进 trapezoid shell，Family A 写法）。canonical 采用 base_feet 变体的 loop 版本以利 left/right 统一发射。

### Slot C：handle_mechanism（提手机构 —— 第二个关节轴的可选来源）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_grab_hole | rec_build-a-realistic-articulated-3d-model-of-a-sign_20260609_215029_914922_9ae01b65 | `_build_hinge_handle` L140-L186（barrel L148-L152 + skirt L159-L165 + 抓握 bar block L170-L176 + hand-hole cut L178-L183） | eligible if compatible | apex 固定抓握孔（一体 barrel+skirt+bar+hole）；无第二 joint。亦见 001 spine：`_panel_shell` 内 `handle_cut` L97-L104 直接在 panel 顶区切穿孔 |
| swing_up_bail | rec_sign_var_handle_swivel | `_build_carry_bail` L195-L229（tube_from_spline_points 弧形提梁）+ pivot ears `_build_hinge_barrel` L182-L190 + `handle_pivot` REVOLUTE L292-L308（axis=(1,0,0)，pivot 在 barrel 顶） | eligible if compatible | 可上翻 bail 提梁（第二个非 fixed REVOLUTE joint）；q=0 折平、upper≈π/2 立起 |

> 两 candidate 结构差异真实：fixed_grab_hole 不增加关节（提手是 hinge 件上的固定孔/bar），swing_up_bail 增加一个独立 REVOLUTE bail 子件并新增 `carry_handle` part + `handle_pivot` joint。

## 槽位图（slot graph）

pattern: `mixed`（named slots + 2 条 multiplicity 轴）

```
                    [apex hinge line z=0, axis=+Y]            (CANONICAL apex frame; Family B spine)
front_panel(root, profile=Slot A, base=Slot B)
   |  --[REVOLUTE apex_hinge, axis=+Y at z=0, lower=0 upper≈2.4]-->  back_panel(child, mirror profile=A, base=B)
   |
   |  --[knuckle barrels: N copies along apex Y; visuals on front (and alternating on back); NO extra joint]
   |
   |  --[Slot C handle]
   |        fixed_grab_hole: raised/cut visual on front near apex (FIXED, no joint)
   |        swing_up_bail  : carry_handle part --[REVOLUTE handle_pivot, axis=+X at barrel top]--> bail
   |
   └  --[optional tether chain: link_0 --[REVOLUTE]--> link_1 --> ... link_{M-1}]  (linear_chain spreader)
            front_panel --[REVOLUTE front_to_link_0, axis=+X]--> link_0 ; inter-link --[REVOLUTE axis=+X]-->
```

接口点位说明：

- **apex_hinge（类目定义关节）**：mating = 两 leaf 共享 apex line（local `z=0`）；pivot/axis = panel 宽度方向（canonical `+Y`）；range `[0, ~2.4]` rad，q=0 即开启 A 字形（rest pose = open）。front 是 parent、back 是 child；两 leaf visual 各预倾 `∓APEX_HALF_OPEN` 使 rest 即站姿。
- **knuckle ↔ leaf**：knuckle barrel 骑跨 pin line，沿 apex Y 等距/对称排布，与对侧 leaf 顶边为 captured contact（element-scoped allow_overlap + expect_contact）。不新增关节，随 apex_hinge 运动。
- **base_support ↔ leaf**：corner_feet 在 leaf 底角，沿 `±Y` 外撇、沿 `-Z` 下伸、嵌入 shell 底边融合（同 part，无 joint）。flush_slab 无接口件。
- **handle ↔ apex**：fixed_grab_hole 是 hinge/leaf 顶区一体件（FIXED）。swing_up_bail 的 `handle_pivot` REVOLUTE 挂在 hinge barrel 顶的 pivot ears 上，`axis=+X`（与 fold 轴正交于 canonical 时需轴映射，见备注），q=0 折平 / upper≈π/2 立起。
- **tether chain ↔ 两 leaf**：可选 spreader；anchor pad 在两 leaf 内面，chain 由 `front_panel → link_0 → ... → link_{M-1}` 逐节 REVOLUTE（axis=+X，平行 main hinge）串联，限制最大张开。互斥/可选：只在 handle≠swing_bail 的稳定组合或独立 gate 下采样（避免与 bail 同时调试两条新增关节链）。

互斥/可选/派生关系：

- Slot A/B/C 三轴独立；profile 决定 knuckle barrel 的 Z 落点函数（gabled 用 `_gable_top_z`、其余用顶弧圆 `arc_cz/arc_r`）→ profile **conditional** 影响 knuckle 放置公式但不改关节拓扑。
- swing_up_bail ⇒ 新增 `carry_handle` part + `handle_pivot` joint（拓扑等价类改变，进 slot_choices）。
- tether chain 是可选 multiplicity 轴，默认关闭（低频开启），与 handle 轴正交。

## 每槽位 Module Emits / Interfaces

### Slot A / module rounded_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | front_shell / back_shell（hollow molded shell，threePointArc 圆顶） | S1 / model.py:L58-L121 |
| internal joints | 无（leaf 本体；fold 由 apex_hinge 提供） | S1 / model.py:L255-L268 |
| upstream interface | apex line `z=0` 顶弧边（供 knuckle 落座；arc_cz=-0.3062, arc_r=0.3012） | S1 / model.py:L71-L79, L131-L155 |
| downstream interface | 底边落地（flush）或供 corner_feet 嵌入；正面 +X 供 warning placard | S1 / model.py:L76-L77, L184-L214 |

### Slot A / module trapezoidal_tapered
| emits | 描述 | 来源 |
|---|---|---|
| parts | front_shell / back_shell（直边梯形 extrude + back shell + vent slots） | S2 / model.py:L79-L125 |
| internal joints | 无 | S2 / model.py:L255-L270 |
| upstream interface | apex top edge `z=-TOP_GAP`（供 barrel/skirt 桥接） | S2 / model.py:L63-L76 |
| downstream interface | 底边 + 烘入 corner feet（L102-L106）；vent slots 为 parent visual 细节 | S2 / model.py:L102-L120 |

### Slot A / module gabled_peaked
| emits | 描述 | 来源 |
|---|---|---|
| parts | front_shell / back_shell（5 点尖顶 pentagon） | S3 / model.py:L82-L146 |
| internal joints | 无 | S3 / model.py:L270-L283 |
| upstream interface | gable 顶边函数 `_gable_top_z(y)` 决定 knuckle Z（conditional） | S3 / model.py:L67-L79, L149-L174 |
| downstream interface | 宽底落地；正面 +X warning placard | S3 / model.py:L191-L229 |

### Slot A / module shield
| emits | 描述 | 来源 |
|---|---|---|
| parts | front_shell / back_shell（盾形：圆顶 + 直侧 + 下尖） | S4 / model.py:L120-L170 |
| internal joints | 无 | S4 / model.py:L283-L296 |
| upstream interface | 圆顶弧（同 rounded arc_cz/arc_r）供 knuckle 落座 | S4 / model.py:L173-L200 |
| downstream interface | 底尖（不适合 corner_feet 全宽外撇 → 见 compatibility matrix）；上区 placard | S4 / model.py:L221-L253 |

### Slot B / module flush_slab
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立件（leaf 底边即落地面） | S1 / model.py:L76-L77 |
| internal joints | 无 | — |
| upstream interface | leaf 底边 `z=-height` | S1 / model.py:L76 |
| downstream interface | 地面接触线 | S1 / model.py:L76 |

### Slot B / module corner_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | front_foot_{i} / back_foot_{i}（每 leaf 2 个，loop 发射） | S5 / model.py:L137-L173, L270-L277, L314-L321 |
| internal joints | 无（fused 入 leaf，仅 apex_hinge 一个 joint；测试断言 `len(joints)==1`） | S5 / model.py:L454-L461 |
| upstream interface | 嵌入 leaf 底角（`FOOT_INSET_Y`/`FOOT_EMBED_Z` 融合） | S5 / model.py:L150-L172 |
| downstream interface | 加宽前后脚印的地面接触 pad（外撇 ±Y、下伸 -Z） | S5 / model.py:L153-L163 |

### Slot C / module fixed_grab_hole
| emits | 描述 | 来源 |
|---|---|---|
| parts | hinge_handle（barrel+skirt+bar+hand-hole），或 panel 顶区 handle_cut 通孔 | S2 / model.py:L140-L186 ; S1 / model.py:L97-L104 |
| internal joints | 无第二关节；`front_to_hinge` FIXED 把 hinge 件固定到 front | S2 / model.py:L225-L239 |
| upstream interface | apex line（barrel 沿宽度，skirt 下伸接两 leaf 顶边） | S2 / model.py:L148-L165 |
| downstream interface | 抓握孔（hand passes through） | S2 / model.py:L178-L183 |

### Slot C / module swing_up_bail
| emits | 描述 | 来源 |
|---|---|---|
| parts | carry_handle（bail tube）+ hinge barrel 上的 pivot ears | S6 / model.py:L195-L229, L182-L190 |
| internal joints | `handle_pivot` REVOLUTE（axis +X，pivot 在 barrel 顶；q=0 折平、upper≈π/2 立起） | S6 / model.py:L292-L308 |
| upstream interface | pivot ears boss（barrel 顶 `z=HINGE_R+PIVOT_EAR_H`） | S6 / model.py:L182-L190, L291 |
| downstream interface | bail 弧顶供手提（captured contact bail↔ear，element-scoped allow） | S6 / model.py:L552-L566 |

### 可选轴 / tether chain（来自 clip_chain）
| emits | 描述 | 来源 |
|---|---|---|
| parts | link_{i}（flat stadium link）+ 两 leaf 内面 anchor pad | S7 / model.py:L156-L194, L197-L220 |
| internal joints | `front_to_link_0` + `link_{i}_to_link_{i+1}` 全 REVOLUTE，axis +X，每节 ±CHAIN_JOINT_LIMIT | S7 / model.py:L421-L452 |
| upstream interface | front anchor pad（内面 contact） | S7 / model.py:L284-L293, L332-L340 |
| downstream interface | back anchor pad（限位 spreader 终点） | S7 / model.py:L373-L380 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| panel_profile | enum | rounded_top / trapezoidal_tapered / gabled_peaked / shield | rounded_top | choice | deterministic procedural sampler | Slot A table |
| base_support | enum | flush_slab / corner_feet | flush_slab | choice | sampler；shield+corner_feet 受限（见 compatibility） | Slot B table |
| handle_mechanism | enum | fixed_grab_hole / swing_up_bail | fixed_grab_hole | choice | sampler | Slot C table |
| tether_chain_enabled | bool | {False, True} | False | choice | 低频开启；与 handle 轴正交 | S7 / L403-L452 |
| palette_style | enum | safety_yellow / safety_orange / red_white / hi_vis_lime / black_yellow_stripe / industrial_gray | safety_yellow | choice | ≥3 必需，目标 4-6；只改材质不改拓扑 | 见下方 palette 说明 |
| knuckle_count (N) | int | [1, 7] | 3 | independent (weighted) | 沿 apex Y 对称/等距；见 Multiplicity | S(knuckles2/5)+parents |
| tether_link_count (M) | int | [2, 5] | 4（仅当 tether_chain_enabled） | conditional | 仅 tether on 时采样；linear_chain | S7 / L67, L410 |
| apex_half_open | float | [0.12, 0.22] rad | 0.18 | independent | rest 开启半角；clamp | S1 / L43 ; S2 / L39 |
| panel_height_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 PANEL_HEIGHT；保持 >0.45 m floor-sign 断言 | S1 / L38 |
| panel_width_scale | float | [0.92, 1.12] | 1.0 | independent | 缩放 PANEL_WIDTH；保持 >0.25 m 断言 | S1 / L37 |
| knuckle_band_len_scale | float | derived | 1.0 | equation | `= clamp(PANEL_WIDTH / (N · k))`，N 大时缩短单 barrel，防越界/相邻穿插 | S(knuckles5) / L45 |
| foot_spread_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 corner_feet；外撇量随 panel_width_scale 上限 | S5 / L57 |
| (—) | constraint | — | — | inequality | knuckle 总占宽 `Σ band_len ≤ PANEL_WIDTH·0.95`；违反则按比例缩 band_len 或减 N | S(knuckles) |
| (—) | constraint | — | — | inequality | tether 总长 `Σ PITCH·M ≤ apex 张开后两 anchor 间距 + 余量`；违反则减 M | S7 / L68-L72 |
| (—) | constraint | — | — | inequality | apex_half_open 与 panel_height_scale 联合保证 open footprint `back+Y − front−Y > 0.12 m`（稳定脚印断言） | S2 / L374-L378 |

**palette_style 说明（≥3，目标 4-6，源自样本观察）**：样本均为 caution 黄系（`(0.96,0.78,0.06)` / `(0.92,0.80,0.10)` 等，见 S1 L51-L55 / S2 L55-L57），knuckle/graphic 为黑、hazard 三角为红（S2 L51-L55）。模板暴露 6 档 colorway，仅替换材质 rgba 不改拓扑：

1. `safety_yellow` — leaf 黄 + 黑 knuckle + 黑字 + 红三角（基线，001/002）
2. `safety_orange` — 高亮橙 leaf（工地常见变体）
3. `red_white` — 红底白字（禁止/危险样式）
4. `hi_vis_lime` — 荧光黄绿（高可视）
5. `black_yellow_stripe` — 黑黄警示条纹 placard
6. `industrial_gray` — 灰本体 + 黄警示带（仓储风）

## Multiplicity / Copy Logic

本小类有 **2 根 multiplicity 轴**（主轴 knuckle，可选轴 tether），各自独立加权采样、各自 clamp、各自进 slot_choices。

### 轴 1（主）：apex knuckle barrels
- `count_param`: `knuckle_count` (N)
- `N_range`: `[1, 7]`（产品域；测试偏小 N，尾部稀有）。样本覆盖：002 parent=1 宽 barrel、001 parent=3 bands、knuckles2 变体=2、knuckles5 变体=5。
- sampling domain（权重档）：N∈{1,2,3} 高频（~70%，单/双/三 knuckle 最常见），N∈{4,5} 中频（~25%，piano-hinge 风格），N∈{6,7} 稀有（~5%，需 band_len 缩短）。
- copied object：单个 knuckle barrel（Y 轴短圆柱），几何来自 `_knuckle_barrel(cy)`（knuckles2 L129-L155）/ `_hinge_knuckle_barrel(cy)`（knuckles5 L125-L150）。
- naming：`knuckle_{i}`（i=0..N-1）。
- placement：沿 apex 宽度对称/等距。偶数 N 对称分布（knuckles2：`±PANEL_WIDTH/4`，L218-L221）；奇数/通用：`cy = -W/2 + slot_width·(i+0.5)`，`slot_width=W/N`（knuckles5 L240-L242）。barrel Z 由 profile 顶边函数确定（gabled→`_gable_top_z`，其余→顶弧圆 arc_cz/arc_r）。N=1 时退化为单宽 barrel（002 写法，band_len≈full hinge length）。
- joint policy：**所有 knuckle 共享同一 apex_hinge REVOLUTE 销轴，不新增 joint**。knuckle 为 leaf 上的 visual（捕获对侧 leaf，element-scoped allow_overlap + expect_contact）。N≥4 可选 piano-style 交替分配（偶 index→front、奇 index→back，knuckles5 L241-L257），交替时对每个 knuckle 各写 element-scoped allow + contact。
- source/gating：knuckles2 / knuckles5 + 两 parent；与 panel_profile **conditional**（barrel Z 函数随 profile）。

### 轴 2（可选）：tether spreader chain
- `count_param`: `tether_link_count` (M)
- `N_range`: `[2, 5]`（产品域）。来源 clip_chain N_LINKS=6（L67），模板收窄至 [2,5] 控关节链长。
- sampling domain：仅当 `tether_chain_enabled=True`（默认低频，~10-15% seeds）；M∈{2,3} 高频、{4,5} 较低。
- copied object：flat stadium `link_{i}`（`_build_chain_link` L156-L194）。
- naming：`link_{i}`（part）+ `link_{i}_body`（visual）。
- placement：linear_chain，从 front anchor 沿 +Y 逐节 PITCH 间距铺向 back anchor。
- joint policy：`front_to_link_0` + `link_{i}_to_link_{i+1}` 全 REVOLUTE，axis +X（平行 main hinge），每节 ±CHAIN_JOINT_LIMIT（L74）。
- source/gating：clip_chain。与 swing_up_bail 同采样时为高调试风险组合 → 默认 gate 互斥或仅在 fixed_grab_hole 下开 tether（见 compatibility matrix）。

## 拓扑多样性审计

总组合数：
- 核心 named slots：panel_profile 4 × base_support 2 × handle_mechanism 2 = **16**
- 乘 knuckle N 的 distinct 拓扑数（N∈{1,2,3,4,5,6,7} = 7，且 N≥4 piano-alternating 再分一类，保守计 N distinct ≈ 7）：16 × 7 = **112**
- 再乘 tether_chain {off, on×M∈[2,5]=4} = 5：112 × 5 = **560**（含可选轴）

理由：仅 panel_profile(4) × knuckle_N(≥4 个不同 N) = 16 ≥ 10 已过；handle 轴新增 carry_handle part + handle_pivot joint 进一步分离拓扑等价类；tether 轴再翻倍。distinct topology 远超 10。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed：先按权重抽 panel_profile / base_support / handle_mechanism（compatibility gate 过滤非法组合）→ 抽 knuckle_count N（小 N 偏多）→ 抽 tether_chain_enabled（低频）及 M（仅 on 时）→ 抽 palette_style → 抽连续 scale（independent 先抽 apex_half_open / height_scale / width_scale → equation 派生 knuckle_band_len_scale → inequality 投影/回缩 knuckle 总占宽 & tether 总长 & open footprint → conditional 解析 foot_spread / M 范围）。`slot_choices_for_seed` 返回 `(slot_name, module_name)` + N + tether 状态（连续 scale 不记入除非改拓扑等价类）。少量 regression overrides 仅用于已知失败回归。random sweep：seeds 0-49 初轮、0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本模板理论 distinct=560，受 compatibility gate（shield×corner_feet 降级、bail×tether 互斥）实际略低，但 panel_profile×N×handle×tether 组合足以 ≥300。

Controlled local parameterization：关键连续 scale = `apex_half_open`[0.12,0.22]、`panel_height_scale`[0.92,1.10]、`panel_width_scale`[0.92,1.12]、`knuckle_band_len_scale`(derived)、`foot_spread_scale`[0.85,1.20]（conditional）。均在 `resolve_config` clamp/派生：先抽 independent 主尺度 → equation 派生 band_len → inequality 投影（knuckle 总占宽 ≤ 0.95·W、tether 总长 ≤ anchor 间距、open footprint > 0.12 m）→ conditional 解析。这些 scale 只改安全比例，不破坏 apex_hinge 轴/range、knuckle 捕获接口、corner_feet 融合或类目 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order: profile→base→handle→knuckle N→tether(M)→palette→scales；weighted（小 N 偏多、tether 低频）；compatibility gates | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | shield+corner_feet → 降级为 flush_slab 或仅近顶部窄脚（盾形底尖无全宽外撇着力点）；swing_up_bail + tether_chain → 默认互斥（避免同调两条新增关节链），如需共存须各自 allow_overlap 全声明；N≥6 → 强制 knuckle_band_len_scale 缩短并校验不相邻穿插；N=1 → 退化单宽 barrel | no floating, collision, axis, max multiplicity, bulky module, optional moving child failures |
| controlled local variation | apex_half_open / height_scale / width_scale / band_len(derived) / foot_spread(cond)；全 clamp/inequality | 比例变化不破坏接口、clearance、support、apex/handle joint origin、类目 identity |
| regression overrides | none（首版）；后续仅记已知失败 seed + 原因 | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A panel_profile | 4 | yes | yes | rounded/trapezoid/gabled/shield |
| B base_support | 2 | yes | no | 样本池仅 2 真实结构；不为凑数发明第三 |
| C handle_mechanism | 2 | yes | no | fixed grab-hole vs swing bail；结构差异真实（后者增关节） |

> Slot B/C 各 2 candidate 的降级理由：5 星样本池中 base_support 只观测到 flush 与 corner-feet 两种真实结构层；handle 只观测到固定抓握孔与可上翻 bail 两种。二者均为真结构差异（非尺寸/颜色），且 ≥2 满足硬门槛；不发明无来源的第三结构（符合 README SPEC_ONLY）。

## Multiplicity / Copy Logic 已在上方独立小节给出（2 轴）。

## Validator

- slot_choices_for_seed returns implemented module names（含 knuckle N 与 tether 状态）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（shield×corner_feet、bail×tether、N≥6 band_len）
- optional regression overrides are sparse and justified（首版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；cross-part deps（band_len equation、knuckle 占宽/tether 长/open footprint inequality、foot_spread/M conditional）resolved in `resolve_config`
- critical InterfaceSpec/MatingContract 存在：apex line 共享、knuckle 捕获对侧 leaf、corner_feet 融合、bail pivot ears、tether anchor pad
- key joints：apex_hinge REVOLUTE axis=+Y（canonical）range`[0,~2.4]` q=0 开启；handle_pivot REVOLUTE axis=+X range`[0,~π/2]`（swing bail）；tether 全 REVOLUTE axis=+X
- copied objects 遵循命名/放置：knuckle_{i} 对称/等距、link_{i} linear_chain、foot_{i} left/right

## Reject cases

- apex fold 做成 FIXED 或 PRISMATIC（丢失类目定义关节）— 必须 REVOLUTE。
- apex 轴方向错误（canonical 应沿 panel 宽度；混用 X/Y spine 导致 fold 轴与几何不匹配 → A 字形不成立）。
- rest pose（q=0）即合拢扁平（应为开启站姿）；或 open footprint `back+Y − front−Y ≤ 0.12 m`（不稳）。
- knuckle barrel 不捕获对侧 leaf（free-floating，无 expect_contact）或缺 element-scoped allow_overlap 导致整体碰撞失败。
- knuckle N 过大致相邻 barrel 穿插 / 越出 panel 宽度（未缩 band_len）。
- shield profile 配全宽 corner_feet（底尖无着力点，脚悬空/穿模）— 必须降级。
- swing_up_bail 与 tether_chain 同时新增两条关节链而未补全各自 allow_overlap/contact（连接性失败）。
- 两 leaf profile 不同形（apex 处无法干净对接；样本均双 leaf 同形）。
- 混入 street/post/hanging/billboard sign（单立柱、悬挂摆动、大型固定）— 出类目。
- carry handle 不在 apex 附近（应近顶 hinge；测试断言 handle top z ≈ panel top z）。

## 与相邻类别的边界

- 不该混入：**street sign / sign post**（单根立柱 + 顶部固定板，无 leaf、无 apex 折叠关节；运动语义完全不同）。
- 不该混入：**hanging sign / swinging shop sign**（顶部悬挂、绕水平轴重力摆动；其关节是悬挂摆而非两 leaf 间的 apex fold，且不站立于地面）。
- 不该混入：**billboard / 大型广告牌**（大尺寸固定结构，无折叠、非便携地面牌）。
- 不该混入：**traffic light / signal head**（柱上信号灯，无折叠 leaf）。
- 远亲不进 seed domain：**chalkboard sandwich-board A-frame**（虽 A 形折叠，但木框 + 书写黑板面 identity；本模板专注塑料 caution sign 形态、印刷 warning placard、knuckle hinge）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- **Spine 选择**：canonical = Family B（apex axis=+Y、离散 knuckle、原生支持 knuckle multiplicity，6/9 源）。Family A（002 parent / handle_swivel / clip_chain）的 handle/feet/chain 写法采用时做坐标映射：Family A 的 fold axis=+X、厚度沿+Y → 映射到 canonical 的 axis=+Y、厚度沿+X（即把 Family A 的 (X,Y) 互换为 canonical 的 (Y,X)）。swing bail 的 `handle_pivot` 在 canonical 下 pivot 轴应取 panel 宽度的正交水平轴（提梁绕前后向上翻），实现时按 canonical apex frame 重设 axis，不照搬 Family A 的 (1,0,0)。
- 共享 helper：`_panel_shell(profile, ...)` 单一入口按 panel_profile enum 切换轮廓子函数（rounded threePointArc / trapezoid polyline / gable pentagon / shield arc-chain）；`_knuckle_barrel(cy, profile_top_z_fn)` 跨 N 复制；`_outrigger_foot(corner_y)` left/right；`_build_chain_link()` + `_build_anchor_pad()` tether。
- InterfaceSpec/MatingContract 重点：apex 共享 line（两 leaf + 所有 knuckle）、knuckle↔对侧 leaf captured contact、corner_feet↔leaf 底角融合、bail↔pivot ears、tether anchor pad↔link_0/link_{M-1}。
- captured-pin overlap 需 element-scoped allow_overlap：每个 `knuckle_{i}`↔对侧 `*_shell`（piano 交替时双向各写）、`carry_bail`↔`hinge_barrel` ear、`*_anchor_pad`↔`link_{i}_body`。
- 暂不进 seed domain 的组合：swing_up_bail × tether_chain（默认互斥，gate 关闭）。
- knuckle Z 落点函数依赖 profile（conditional）：gabled 用 `_gable_top_z(cy)`（gabled L67-L79），rounded/shield/trapezoid 用顶弧圆 `arc_cz=-0.3062, arc_r=0.3012`（多源一致）。
