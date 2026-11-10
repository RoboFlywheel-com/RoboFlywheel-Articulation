## 元信息
| 项 | 值 |
|---|---|
| slug | `playground_swing` |
| template path | `agent/templates/playground_swing.py` |
| test path (optional) | `tests/agent/test_playground_swing_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 30 |
| read_count | 30 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

已完整读取 `playground_swing` 类别全部 30 个 5 星样本的 `model.py`、`revision.json`、`record.json`、`prompt.txt`，并读取 `data/categories/playground_swing/category.json`。5 星样本覆盖普通 A-frame 单座、双座 swing set、tire swing、strap swivel swing、toddler bucket swing、molded backyard swing、slatted lap-bar swing、platform swing、wide bench swing、face-to-face glider、disc swing 和 nest swing。未采用的样本只作为结构变化审计输入，不列入 module source table。

## 核心身份

`playground_swing` 是由可见固定支撑架或顶梁承载的儿童/游乐场摆荡设备。核心身份是：上方 beam / frame 提供可见支撑，悬挂机构把座椅或载具挂在顶端 pivot / swivel / yoke 上，下方载具随 revolute 或 continuous+revolute 关节摆动。成熟默认域应保持 park-equipment / backyard-equipment 比例，有真实地面支撑、顶梁、吊点、悬挂件、座具和摆动轴。

不应混入单独秋千椅家具、吊床、蹦床、跷跷板、滑梯或纯装饰 park bench。复杂 glider / platform / nest 模块可以进入本类别，但必须仍有顶梁支撑和摆动/摇摆关节语义。

## 槽位 + 候选模块表

### Slot A：support_frame

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `compact_a_frame_crossbeam` | rec_playground_swing_0001 | L89-L129 | eligible if compatible | 单座 A-frame：圆柱顶梁、两端 splayed legs、侧向 cross brace、顶端小吊点块；frame 是根 part，向下游提供一条中心 pivot line。 |
| `tube_a_frame_with_clevises` | rec_playground_swing_0002 | L61-L179 | eligible if compatible | 更完整的双侧 A-frame：四根斜腿、两侧 spreader、beam 下左右 clevis plate 和 pivot pin；接口显式是左右成对 pin sockets。 |
| `long_gantry_tire_frame` | rec_playground_swing_0003 | L114-L200 | eligible if compatible | 横向长 gantry：长 top beam、左右端 A-frame 支腿、ground skids、侧 brace、三个顶端 pivot bracket；适配 tire / multi-hanger payload。 |
| `multi_station_wide_frame` | rec_playground_swing_b6df00eb27ba4e568ae9d11497f67153 | L21-L88 | eligible if compatible | 从长 beam 双座 swing set 泛化的多站点 frame：同一加宽顶梁下可布置 1-5 个独立 station bay，每 bay 有自己的 pivot bracket；beam length、station spacing、端部/中部支撑随 `station_count` 派生。 |
| `minimal_top_beam_mount` | rec_playground_swing_ff0333498fcd4d118eee0c8ae613297d | L18-L54 | eligible if compatible | 非完整地面架的 timber / overhead beam mount：木梁、mount plate、fixed bearing、bolts；仅用于 strap swivel / disc 类单点悬挂。 |

### Slot B：suspension_spine

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_rigid_or_chain_pair` | rec_playground_swing_0001 | L131-L212 | eligible if compatible | 单个 `swing_assembly` child，从 frame 中心 revolute joint 悬挂；两侧链/杆和座板同属一个活动 part。 |
| `dual_clevis_pair` | rec_playground_swing_0002 | L154-L237 | eligible if compatible | frame 下左右 clevis plate + pivot pins，活动座具携带左右 pivot hubs 和 hanger rods；一个等效 revolute joint 表达双侧同轴摆动。 |
| `captured_sleeve_yoke` | rec_playground_swing_af976fdb588e4553ad346d96e15d3d27 | L66-L112 | eligible if compatible | 顶梁下固定 clevis plate + 长 pivot pin，child 有 pivot sleeve；适配 tire/yoke payload，单 revolute 关节沿 beam span。 |
| `vertical_swivel_plus_swing` | rec_playground_swing_ff0333498fcd4d118eee0c8ae613297d | L55-L162 | eligible if compatible | 两级运动：beam 到 swivel block 是 vertical continuous joint，swivel 到 hanger 是 lateral revolute joint；适配 strap / disc 单点悬挂。 |
| `parallelogram_glider_links` | rec_playground_swing_726ef995e5394cb2ad65d7d56636dd2a | L162-L186, L351-L395 | eligible if compatible | 四个上 pivot、drive link + three mimic parallel links，lower pivot mimic 让 bench carriage 近似保持水平；拓扑是多 part 多 joint。 |
| `two_side_link_rocker` | rec_playground_swing_c07add3805624996978d20766f67657c | L109-L154, L253-L270 | eligible if compatible | 宽 bench 的 hanger_yoke：左右上/下 pivot bushings、两根 side arms、上下 tie bars；frame_to_hanger 和 hanger_to_bench 两级 revolute。 |

### Slot C：seat_payload

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `belt_or_plank_seat` | rec_playground_swing_ea0bb7e594f74ca2b95ad5093abba458 | L115-L221 | eligible if compatible | 软 belt / flat plank 单座：四段 chain runs、左右 seat brackets、lofted belt seat mesh；payload 与 pair hanger 同 part。 |
| `toddler_bucket_seat` | rec_playground_swing_1ccb2e94810e44459d9c5c20a103f514 | L19-L53, L130-L184 | eligible if compatible | 深 bucket shell，有圆形腿孔、front/rear rims、side straps、pivot barrels；单活动 part，强调 molded safety seat。 |
| `tire_seat_three_hanger` | rec_playground_swing_0003 | L95-L111, L201-L283 | eligible if compatible | Lathe tire shell、三个下锚点和三根 hanger links；视觉三 pivot，等效单 revolute 摆动。 |
| `slatted_seat_with_lap_bar` | rec_playground_swing_4354e6c4695d4e2f809faf99a9952185 | L95-L248 | eligible if compatible | slatted seat_assembly + 独立 `lap_bar` part；主 swing revolute 外另有 `seat_to_lap_bar` revolute。 |
| `standing_platform_deck` | rec_playground_swing_631316662fa34b00bd5b9dad9707feb4 | L80-L202 | eligible if compatible | side_links + platform 两 part：平台 tread deck、rails、hand bar、上下 clevis pins；lower pivot mimic top pivot 反向保持平台姿态。 |
| `bench_with_lower_pivots` | rec_playground_swing_c07add3805624996978d20766f67657c | L155-L270 | eligible if compatible | 宽 bench part：lower pivots、side frames、seat/back slats；通过 hanger_to_bench 小角度 revolute 与 yoke 相连。 |
| `face_to_face_glider_bench` | rec_playground_swing_726ef995e5394cb2ad65d7d56636dd2a | L187-L350 | eligible if compatible | rectangular bench cradle、两套 face-to-face seats、backs、center footwell、四个 lower clip brackets；适配 parallelogram_glider_links。 |
| `disc_seat_with_folding_footrest` | rec_playground_swing_799839ac6c084c288ccc508d42c1d5ec | L54-L244 | eligible if compatible | 单点 disc seat + separate `footrest_ring` part；主 beam_to_seat revolute，seat_to_footrest revolute 控制折叠脚环。 |
| `nest_basket_seat` | rec_playground_swing_f117b975f8d54a95b642d00a4c44a425 | L141-L214 | eligible if compatible | 圆形 padded basket ring、inner rope ring、网格绳、lower clips；两个上 pivot mimic + lower basket rocking pivot。 |

## 槽位图（slot graph）

pattern: `mixed`

默认串联：

```text
support_frame
  --[fixed beam underside / pivot socket / top bearing interface]-->
suspension_spine
  --[lower hanger eye / seat bracket / yoke lower pivot / payload anchor]-->
seat_payload
```

兼容性 gate：

- `compact_a_frame_crossbeam` + `single_rigid_or_chain_pair` + `belt_or_plank_seat` 是 procedural sampling marker 组合。
- `tube_a_frame_with_clevises` 可接 `dual_clevis_pair`，再接 `belt_or_plank_seat`、`toddler_bucket_seat`、`slatted_seat_with_lap_bar`。
- `long_gantry_tire_frame` 可接 `captured_sleeve_yoke`，再接 `tire_seat_three_hanger`；也可接 `two_side_link_rocker` + `bench_with_lower_pivots`，但需同轴 pivot spacing 适配。
- `multi_station_wide_frame` 是 multiplicity 承载 frame：`station_count=1..5`，每个 station 独立选择一个 compatible `station_recipe`，可以重复同一 recipe，也可以混合 belt、bucket、tire、lap-bar、platform、bench、glider、disc、nest 等不同秋千类型。frame 必须按 station 的 footprint 和数量加宽顶梁、生成 station pivot hardware，`station_count>=4` 时必须增加中部支撑或加强 brace。
- `minimal_top_beam_mount` 只接 `vertical_swivel_plus_swing`，再接 strap/plank style payload 或 `disc_seat_with_folding_footrest`。
- `parallelogram_glider_links` 只接 `face_to_face_glider_bench`，因为 lower clip / mimic topology 专用。
- `two_side_link_rocker` 只接 `bench_with_lower_pivots` 或 `nest_basket_seat` 的双下夹点版本。

`multi_station_wide_frame` 下的 station recipe 是 per-station tuple，而不是全局 slot 选择：

```text
station_i = support_frame.station_bay_i
          + suspension_spine_module_i
          + seat_payload_module_i
          + station_i own top pivot / swivel / mimic joints
```

推荐 station recipe pool：

- `simple_belt_station`: `single_rigid_or_chain_pair` or `dual_clevis_pair` + `belt_or_plank_seat`
- `bucket_station`: `dual_clevis_pair` + `toddler_bucket_seat`
- `tire_station`: `captured_sleeve_yoke` + `tire_seat_three_hanger`
- `lap_bar_station`: `dual_clevis_pair` + `slatted_seat_with_lap_bar`
- `platform_station`: platform source topology from `standing_platform_deck`
- `bench_station`: `two_side_link_rocker` + `bench_with_lower_pivots`
- `glider_station`: `parallelogram_glider_links` + `face_to_face_glider_bench`
- `swivel_disc_station`: `vertical_swivel_plus_swing` + `disc_seat_with_folding_footrest`
- `nest_station`: nest source topology from `nest_basket_seat`

跨 slot 接口点位：

- `support_frame.downstream.top_pivot_line`: 顶梁下方 pivot line，通常沿 beam span，坐标来自 frame module 的 `pivot_origin` 和 `axis`。
- `support_frame.downstream.station_pivots`: 对 multi-station frame、tire、nest、platform 或四连杆 glider 提供多个 pivot sockets，含 station index、pair index、world origin、axis、station footprint。
- `suspension_spine.upstream`: 消费 top pivot line / station pivots，并创建 `frame_to_*` revolute 或 `beam_to_swivel` continuous joint。
- `suspension_spine.downstream.lower_payload_interface`: 对 seat_payload 提供 lower pin、seat bracket、hanger endpoints、或 yoke lower pivot。
- `seat_payload.upstream`: 必须与 lower_payload_interface 可见接触；独立 accessory part（lap_bar、footrest_ring、basket lower pivot）必须挂在 payload part 上，不允许浮空。

## 每槽位 Module Emits / Interfaces

### Slot A / module `compact_a_frame_crossbeam`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame` with cylindrical crossbeam, four splayed legs, cross braces, two hanger block visuals | S1 / model.py:L89-L129 |
| internal joints | none | S1 / model.py:L89-L129 |
| upstream interface | root ground support; no parent | S1 / model.py:L89-L129 |
| downstream interface | centered pivot at beam underside / `JOINT_Z`, axis along local Y in source | S1 / model.py:L119-L123, L199-L212 |

### Slot A / module `tube_a_frame_with_clevises`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `support_frame` root with crossbeam, four tube legs, spreaders, hanger plates, pivot pins | S2 / model.py:L61-L179 |
| internal joints | none | S2 / model.py:L61-L179 |
| upstream interface | root support frame | S2 / model.py:L80-L85 |
| downstream interface | left/right clevis pivot pins at `pivot_half_y`, shared revolute origin on beam underside | S2 / model.py:L154-L179, L224-L237 |

### Slot A / module `long_gantry_tire_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gantry_frame` root with long top beam, two end A-frame supports, ground skids, braces, three pivot bracket pairs | S3 / model.py:L114-L200 |
| internal joints | none | S3 / model.py:L114-L200 |
| upstream interface | root gantry | S3 / model.py:L122-L127 |
| downstream interface | `SUPPORT_XS` three physical hanger sockets and equivalent centered top pivot | S3 / model.py:L186-L200, L270-L283 |

### Slot A / module `multi_station_wide_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame` with long box beam, end A-frame supports, repeated station bay pivot bracket pairs, optional center supports / braces for high station counts | S4 / model.py:L21-L88 |
| internal joints | none | S4 / model.py:L21-L88 |
| upstream interface | root support | S4 / model.py:L46-L57 |
| downstream interface | `station_count` station centers along the widened beam, each with its own top pivot hardware set and footprint reservation | S4 / model.py:L41-L44, L76-L88 |

### Slot A / module `minimal_top_beam_mount`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `beam` with timber beam, mounting plate, fixed bearing, bolts | S5 / model.py:L18-L54 |
| internal joints | none | S5 / model.py:L18-L54 |
| upstream interface | root overhead beam, no ground legs | S5 / model.py:L26-L54 |
| downstream interface | vertical swivel bearing at beam underside, z-axis continuous joint origin | S5 / model.py:L145-L153 |

### Slot B / module `single_rigid_or_chain_pair`
| emits | 描述 | 来源 |
|---|---|---|
| parts | activity child `swing_assembly` with two hanging chain/rod runs and simple seat panel visuals | S6 / model.py:L131-L198 |
| internal joints | none inside module | S6 / model.py:L131-L198 |
| upstream interface | consumes one top pivot line; emits `swing_hinge` revolute | S6 / model.py:L199-L212 |
| downstream interface | payload is module-local or receives two side lower seat anchors | S6 / model.py:L139-L185 |

### Slot B / module `dual_clevis_pair`
| emits | 描述 | 来源 |
|---|---|---|
| parts | pivot hubs and vertical hanger rods on seat child, plus frame clevis hardware from compatible frame | S2 / model.py:L154-L223 |
| internal joints | none inside child; one equivalent revolute swing joint | S2 / model.py:L224-L237 |
| upstream interface | consumes left/right clevis pins and centered equivalent pivot origin | S2 / model.py:L205-L237 |
| downstream interface | lower rod embeds into payload top / seat bracket | S2 / model.py:L181-L223 |

### Slot B / module `captured_sleeve_yoke`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `tire_assembly` / yoke with top `pivot_sleeve`, three hanger lugs, captured by fixed frame pin | S7 / model.py:L66-L112 |
| internal joints | one frame_to_tire revolute, no lower articulation | S7 / model.py:L104-L112 |
| upstream interface | consumes long pivot pin across gantry clevis plates | S7 / model.py:L66-L78 |
| downstream interface | three lower tire clamp anchors under the sleeve | S7 / model.py:L97-L102 |

### Slot B / module `vertical_swivel_plus_swing`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `swivel_block` plus `seat_hanger`, top bearing cap, upper bushing, clevis cheeks, side links | S5 / model.py:L55-L144 |
| internal joints | `beam_to_swivel` continuous about Z, `swivel_to_hanger` revolute about X | S5 / model.py:L145-L162 |
| upstream interface | consumes vertical bearing under minimal beam mount | S5 / model.py:L55-L87, L145-L153 |
| downstream interface | lower pin / seat board attach line at hanger bottom | S5 / model.py:L88-L144 |

### Slot B / module `parallelogram_glider_links`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drive_link` plus three `parallel_link_*` children with upper/lower eyes | S8 / model.py:L162-L186 |
| internal joints | primary `beam_to_drive_link`, lower `drive_link_to_bench` with negative mimic, three mimic parallel top joints | S8 / model.py:L351-L395 |
| upstream interface | consumes four upper frame pivots | S8 / model.py:L105-L160, L351-L395 |
| downstream interface | four lower clip/pin positions in bench local frame | S8 / model.py:L302-L350 |

### Slot B / module `two_side_link_rocker`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hanger_yoke` with upper/lower bushings, left/right side arms, tie bars | S9 / model.py:L109-L154 |
| internal joints | frame_to_hanger revolute, hanger_to_bench revolute | S9 / model.py:L253-L270 |
| upstream interface | consumes two upper pivot sockets on frame | S9 / model.py:L111-L154, L253-L260 |
| downstream interface | lower pivot pair for bench / basket clips | S9 / model.py:L155-L169, L262-L270 |

### Slot C / module `belt_or_plank_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | belt/plank seat visuals, chain runs, side brackets on swing assembly | S10 / model.py:L115-L221 |
| internal joints | none beyond upstream swing joint | S10 / model.py:L222-L235 |
| upstream interface | two side hanger endpoints from pair suspension | S10 / model.py:L122-L177 |
| downstream interface | no downstream slot | S10 / model.py:L194-L221 |

### Slot C / module `toddler_bucket_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket shell mesh with leg holes, rims, side straps, pivot barrels, side mounts | S11 / model.py:L19-L53, L130-L175 |
| internal joints | none beyond top swing joint | S11 / model.py:L176-L184 |
| upstream interface | two pivot barrels / side straps to clevis pair | S11 / model.py:L150-L184 |
| downstream interface | no downstream slot | S11 / model.py:L130-L175 |

### Slot C / module `tire_seat_three_hanger`
| emits | 描述 | 来源 |
|---|---|---|
| parts | tire mesh / lathe shell, three hanger heads, three tire anchors, three hanger links | S3 / model.py:L95-L111, L201-L265 |
| internal joints | equivalent top revolute from suspension module | S3 / model.py:L266-L283 |
| upstream interface | three top supports or captured sleeve yoke | S3 / model.py:L216-L265 |
| downstream interface | no downstream slot | S3 / model.py:L208-L265 |

### Slot C / module `slatted_seat_with_lap_bar`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `seat_assembly` with slats and side hanger links, plus separate `lap_bar` part | S12 / model.py:L95-L248 |
| internal joints | main swing revolute and `seat_to_lap_bar` revolute | S12 / model.py:L176-L188, L235-L248 |
| upstream interface | top pivot sleeves / beam ears | S12 / model.py:L84-L104, L176-L188 |
| downstream interface | lap-bar hinge barrels captured at front seat corners | S12 / model.py:L138-L148, L191-L248 |

### Slot C / module `standing_platform_deck`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `side_links` and `platform` parts with deck, side rails, lower yokes, hand bar | S13 / model.py:L80-L183 |
| internal joints | `top_pivots` revolute and mimic `lower_pivots` revolute | S13 / model.py:L184-L202 |
| upstream interface | two top clevises on frame | S13 / model.py:L63-L78, L184-L191 |
| downstream interface | no downstream slot | S13 / model.py:L107-L183 |

### Slot C / module `bench_with_lower_pivots`
| emits | 描述 | 来源 |
|---|---|---|
| parts | wide bench with lower pivot bosses, side frames, seat slats, back slats | S9 / model.py:L155-L252 |
| internal joints | receives hanger_to_bench revolute from two_side_link_rocker | S9 / model.py:L262-L270 |
| upstream interface | lower pivot pair on hanger_yoke | S9 / model.py:L155-L169, L262-L270 |
| downstream interface | no downstream slot | S9 / model.py:L170-L252 |

### Slot C / module `face_to_face_glider_bench`
| emits | 描述 | 来源 |
|---|---|---|
| parts | rectangular bench frame, two face-to-face seat pans, back panels, center footwell, four lower clip brackets | S8 / model.py:L187-L350 |
| internal joints | lower mimic joint from drive link to bench; other parallel links mimic top pivot | S8 / model.py:L351-L395 |
| upstream interface | four lower clip/pin locations matching parallelogram links | S8 / model.py:L302-L350 |
| downstream interface | no downstream slot | S8 / model.py:L187-L350 |

### Slot C / module `disc_seat_with_folding_footrest`
| emits | 描述 | 来源 |
|---|---|---|
| parts | top beam/seat_assembly pattern with disc seat plus separate `footrest_ring` | S14 / model.py:L54-L214 |
| internal joints | `beam_to_seat` revolute, `seat_to_footrest` revolute | S14 / model.py:L215-L244 |
| upstream interface | single top hanger tongue / bushing under beam or swivel hanger | S14 / model.py:L63-L123, L215-L228 |
| downstream interface | footrest hinge lugs under seat disk | S14 / model.py:L148-L214, L229-L241 |

### Slot C / module `nest_basket_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | padded torus basket ring, rope weave, lower clips, two hanger parts | S15 / model.py:L116-L183 |
| internal joints | two mimic top pivots and lower basket rocking pivot | S15 / model.py:L184-L214 |
| upstream interface | two top pins and lower basket clip axis | S15 / model.py:L108-L139, L184-L214 |
| downstream interface | no downstream slot | S15 / model.py:L141-L183 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_frame_module` | enum | `compact_a_frame_crossbeam`, `tube_a_frame_with_clevises`, `long_gantry_tire_frame`, `multi_station_wide_frame`, `minimal_top_beam_mount` | `compact_a_frame_crossbeam` | 由 seed 或 override 选择；决定 frame root、station bay count 和 pivot interface | Slot A table |
| `station_count` | int | compatibility gated `1..5` | `1` | frame 先随机，再按支架能力 gate：`compact_a_frame_crossbeam`/`minimal_top_beam_mount` 固定 1，`tube_a_frame_with_clevises` 为 1-2，`long_gantry_tire_frame`/`multi_station_wide_frame` 为 1-5 | S4 / model.py:L41-L44, L76-L88, L126-L146 |
| `station_recipe[i]` | tuple enum | `simple_belt_station`, `bucket_station`, `tire_station`, `lap_bar_station`, `platform_station`, `bench_station`, `glider_station`, `swivel_disc_station`, `nest_station` | `simple_belt_station` for station 0 | 每个 station 独立采样 compatible suspension + payload；允许重复，也允许混合不同类型 | Slot B/C tables + Multiplicity |
| `geometry_seed` | int | deterministic seed integer | `0` | 驱动每个 station 的内部几何 resolver；同一 seed 可复现尺寸、drop、radius、hub length 和 footprint | implementation resolver |
| `station_geometry[i]` | resolved struct | per recipe constrained ranges | recipe default | 每个 station 先 resolve `scale/width/depth/radius/drop/hanger_half_width/hub_length/footprint`，再由 builder 消费；禁止各尺寸独立乱采样 | implementation resolver |
| `suspension_spine_module` | enum | `single_rigid_or_chain_pair`, `dual_clevis_pair`, `captured_sleeve_yoke`, `vertical_swivel_plus_swing`, `parallelogram_glider_links`, `two_side_link_rocker` | `single_rigid_or_chain_pair` | 单站点时为全局选择；multi-station 时变为 `station_recipe[i].suspension` | Slot B table |
| `seat_payload_module` | enum | `belt_or_plank_seat`, `toddler_bucket_seat`, `tire_seat_three_hanger`, `slatted_seat_with_lap_bar`, `standing_platform_deck`, `bench_with_lower_pivots`, `face_to_face_glider_bench`, `disc_seat_with_folding_footrest`, `nest_basket_seat` | `belt_or_plank_seat` | 单站点时为全局选择；multi-station 时变为 `station_recipe[i].payload` | Slot C table |
| `beam_length_m` | float | derived `[1.2, 7.5]` | source default | 从 `station_count`、每 station resolver 返回的 footprint、station spacing、end clearance 派生；数量越多或站内几何越大，frame 越宽 | S4 / model.py:L29-L44 |
| `support_bay_count` | int | `2..4` | `2` | `station_count<=3` 可用两端支撑；`station_count>=4` 需要中部支撑或加强 brace | S4 / model.py:L59-L74 |
| `top_pivot_axis` | vector enum | local X / local Y / local Z continuous+X swing | local Y for seed0 | 从 frame beam orientation 和 suspension module 派生 | S1 / model.py:L199-L212; S5 / model.py:L145-L162 |
| `swing_limit_rad` | float | `[0.42, 0.85]` | `0.65` | 普通摆动角；glider/platform/nest 使用模块局部范围 | S1 / model.py:L206-L210; S4 / model.py:L129-L146; S8 / model.py:L351-L395 |
| `lower_rock_limit_rad` | float | `[0.18, 0.45]` | module default | 仅 bench/nest/platform 下级 pivot 使用 | S9 / model.py:L262-L270; S13 / model.py:L193-L202; S15 / model.py:L203-L214 |
| `seat_width_m` | float | `[0.34, 1.30]` | `0.52` | 由 payload module 尺寸派生，宽 bench / glider 扩大 | S10 / model.py:L194-L221; S9 / model.py:L170-L252 |
| `hanger_drop_m` | float | `[0.50, 1.60]` | `1.45` | 从 top pivot line 到 payload anchor 的垂向距离 | S10 / model.py:L122-L177; S13 / model.py:L27-L29 |
| `has_lap_bar` | bool | `false`, `true` | `false` | 仅 `slatted_seat_with_lap_bar` 为 true | S12 / model.py:L191-L248 |
| `has_footrest` | bool | `false`, `true` | `false` | 仅 `disc_seat_with_folding_footrest` 为 true | S14 / model.py:L172-L241 |

## Multiplicity / Copy Logic

- `count_param`: `station_count`
- `N_range`: `1..5`
- sampling domain: `support_frame_module` is sampled from all implemented frame families, then `station_count` is sampled through compatibility gates. Compact A-frame and minimal overhead mount are single-station, tube clevis frame supports 1-2 stations, and long gantry / multi-station wide frame support 1-5 stations. `station_count=1` remains valid for every support type.
- copied object: complete swing station = station-local suspension instance + compatible payload instance + all station-local joints + visible top pivot hardware. A station may itself be complex, for example glider four-link, nest basket, platform lower mimic, lap-bar hinge, or disc footrest hinge.
- station recipe sampling: for each `station_i`, independently sample a `station_recipe[i]` from the implemented recipe pool. Sampling may repeat the same recipe across multiple stations, or mix different recipes in one frame, e.g. belt + bucket + tire + nest.
- naming: every emitted part, visual group, articulation, mimic target, and test allowance is prefixed with `station_<i>_`. Examples: `station_2_frame_to_swing`, `station_3_lower_pivot`, `station_1_lap_bar_hinge`.
- per-station geometry: before placement, each `station_recipe[i]` runs a constrained resolver that samples internal scale and derives dependent dimensions such as seat width/depth, tire or nest radius, hanger half-width, hub length, drop, and final footprint. The builder consumes these resolved values so hanger endpoints, pivots, rim parts, slats, bars, and payload contact points stay connected.
- placement: frame computes `station_centers` along the top beam. Spacing uses each resolved station footprint plus clearance; bulky or enlarged tire, nest, glider, platform, and bench stations reserve wider bays than compact belt/bucket stations.
- frame scaling: `beam_length_m = sum(station_footprints) + inter_station_clearance * (N - 1) + end_clearance * 2`. For `long_gantry_tire_frame` / `multi_station_wide_frame` with `station_count>=4`, add center support posts / A-frame bay or diagonal braces so the long beam has a visible load path, not just a stretched unsupported bar.
- joint policy: each station owns its main swing joint(s). Mimic is allowed only inside a station recipe when the source topology uses mimic; station-to-station mimic is forbidden because mixed stations must move independently.
- source/gating: S4 supplies the source pattern for independent station bays and repeated pivot brackets. S1/S2/S3/S5/S8/S9/S10-S15 supply station recipe internals. A station recipe can only be sampled if its required top interface can be emitted by the frame bay.

## 拓扑多样性审计

总候选数（未计 gate）：5 support frames × 6 suspension modules × 9 payload modules × 5 station counts × 9 per-station recipe families。实际 seed domain 必须使用 compatibility gate，而不是全部笛卡尔组合。经 gate 后仍至少包含：

- seed0 normal single-seat chain/belt topology.
- clevis bucket / slatted / belt topologies.
- tire captured-sleeve topology.
- vertical swivel + swing two-joint topology.
- multi-station mixed swing-set topology with 1-5 independently sampled stations.
- bench two-level rocker topology.
- face-to-face parallelogram glider topology.
- platform counter-mimic lower pivot topology.
- nest basket mimic + lower rocking topology.
- disc seat + folding footrest accessory topology.


理由：候选不仅改变尺寸，还改变 part count、joint count、joint type、mimic policy、station count、station recipe sequence、lower accessory articulation 和 payload primitive family。`station_count=1..5` 与可重复/可混合的 station recipes 会产生真实 station-level topology diversity，而不是只改变 beam 长度。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_frame | 5 | yes | yes | 完整 A-frame、gantry、dual-bay、minimal overhead mount 均有不同接口。 |
| suspension_spine | 6 | yes | yes | 从单 revolute 到 continuous+revolute、parallelogram mimic、two-level rocker。 |
| seat_payload | 9 | yes | yes | seat primitive、part tree、lower accessory joint 明显不同。 |
| station_count | 5 | yes | yes | multi-station frame 下有效；1-5 个完整 station，可重复或混合不同 recipe。 |
| station_recipe | 9 | yes | yes | 每个 station 独立选择 compatible recipe，recipe 内部保留对应 joint / mimic / accessory topology。 |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator

- `slot_choices_for_seed(seed)` returns implemented module names and never returns an ungated incompatible combination.
- `station_count` is in `1..5`; `len(station_recipe_sequence) == station_count`.
- station recipe sequence may contain repeated recipes and mixed recipes; both paths must be covered by tests.
- every support module emits a visible root support path from ground or overhead beam to top pivot.
- `multi_station_wide_frame` widens beam and emits one station bay / pivot hardware set per station; `station_count>=4` also emits a center support or equivalent brace.
- every suspension module creates the expected joint type / axis / range: revolute for normal swing, continuous+revolute for swivel, mimic revolutes for glider/nest/platform where specified.
- payload modules with accessory parts create their local joints: lap bar hinge, footrest hinge, lower bench/basket/platform pivot.
- every station creates independently articulated swing station(s) with stable `station_<i>_*` names and no shared child part between stations.
- captured pivot / bushing overlap must be declared element-scoped in tests only for visible coaxial pins/sleeves from source patterns.

## Reject cases

- A floating seat, tire, bench, platform, or basket with no visible support path to top beam.
- A decorative frame without real top pivot interface.
- Treating tire, bucket, bench, platform, nest, and disc only as color/scale variants of one seat mesh.
- Using `station_count>1` by duplicating visuals inside one part while exposing only one articulation.
- Stretching the beam for `station_count>=4` without adding visible intermediate support / reinforcement.
- Sampling mixed station recipes but making all stations share one joint, one child part, or one mimic target.
- Combining `parallelogram_glider_links` with a payload that lacks four lower clip points.
- Combining `vertical_swivel_plus_swing` with a station bay that lacks a vertical bearing mount.
- Omitting mimic semantics for platform, nest, or glider modules whose source uses coupled motion.
- Letting lap bar or footrest accessory intersect or float instead of hinging from seat-local points.

## 与相邻类别的边界

- 不该混入：`porch_swing` / indoor hanging chair（通常是 furniture-like bench/sofa under roof, not playground equipment with park-style frame and pivot hardware）。
- 不该混入：`hammock`（fabric sling between two supports without rigid top beam pivot or revolute joint hardware）。
- 不该混入：`seesaw`（central fulcrum rocking board, not suspended from overhead support）。
- 不该混入：`playground_slide`（static ramp/ladder, no suspended payload swing motion）。
- 不该混入：`cradle` / baby rocker（floor-mounted rocking furniture rather than overhead playground suspension）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft generated from all 30 five-star playground_swing samples; awaiting human review before template implementation. |

## 模板实现备注（可选）

- 推荐先实现稳定 seed domain：normal single-seat, mixed multi-station frame with 1-5 station recipes, clevis bucket, tire yoke, swivel disc/strap, bench rocker, glider bench, platform, nest。不要在第一版采样所有笛卡尔组合。
- `InterfaceSpec` 应包含 `top_pivot_line`, `station_pivot_pair`, `single_swivel_bearing`, `lower_yoke_pair`, `four_link_clip_set` 五类接口。
- `MatingContract` 要求 top pivot hardware 可见接触：clevis plate to pivot sleeve / eye, bushing around pin, or hanger tongue inside cheeks。
- lap bar、footrest、captured pin/sleeve、bucket side strap 与 pin 的 overlap 只能用 element-scoped allow_overlap。
- `resolve_config` 应从 frame module 统一导出 pivot axes 和 station centers，payload 不应直接猜测 frame dimensions。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | support_frame | `compact_a_frame_crossbeam` | rec_playground_swing_0001 | L89-L129 | seed0 frame and centered pivot interface |
| S2 | support_frame / suspension_spine | `tube_a_frame_with_clevises`, `dual_clevis_pair` | rec_playground_swing_0002 | L61-L237 | detailed A-frame clevises, pivot pins, hanger rods |
| S3 | support_frame / seat_payload | `long_gantry_tire_frame`, `tire_seat_three_hanger` | rec_playground_swing_0003 | L95-L283 | gantry frame, tire lathe geometry, three hanger topology |
| S4 | support_frame | `multi_station_wide_frame` | rec_playground_swing_b6df00eb27ba4e568ae9d11497f67153 | L21-L150 | source pattern for long beam, independent station bays, repeated pivot brackets, and scalable station copy policy |
| S5 | support_frame / suspension_spine | `minimal_top_beam_mount`, `vertical_swivel_plus_swing` | rec_playground_swing_ff0333498fcd4d118eee0c8ae613297d | L18-L162 | overhead beam, swivel block, continuous+revolute chain |
| S6 | suspension_spine | `single_rigid_or_chain_pair` | rec_playground_swing_0001 | L131-L212 | seed0 two-chain/pair child and revolute swing |
| S7 | suspension_spine | `captured_sleeve_yoke` | rec_playground_swing_af976fdb588e4553ad346d96e15d3d27 | L66-L112 | captured sleeve + tire yoke pivot |
| S8 | suspension_spine / seat_payload | `parallelogram_glider_links`, `face_to_face_glider_bench` | rec_playground_swing_726ef995e5394cb2ad65d7d56636dd2a | L162-L395 | four-link glider, face-to-face bench, mimic joints |
| S9 | suspension_spine / seat_payload | `two_side_link_rocker`, `bench_with_lower_pivots` | rec_playground_swing_c07add3805624996978d20766f67657c | L109-L270 | bench yoke, lower pivots, slatted bench |
| S10 | seat_payload | `belt_or_plank_seat` | rec_playground_swing_ea0bb7e594f74ca2b95ad5093abba458 | L115-L221 | belt/plank payload, chain runs, seat brackets |
| S11 | seat_payload | `toddler_bucket_seat` | rec_playground_swing_1ccb2e94810e44459d9c5c20a103f514 | L19-L184 | bucket shell, leg holes, side straps, pivot barrels |
| S12 | seat_payload | `slatted_seat_with_lap_bar` | rec_playground_swing_4354e6c4695d4e2f809faf99a9952185 | L95-L248 | slatted seat plus hinged lap bar |
| S13 | seat_payload | `standing_platform_deck` | rec_playground_swing_631316662fa34b00bd5b9dad9707feb4 | L80-L202 | platform deck, side links, counter-mimic lower pivot |
| S14 | seat_payload | `disc_seat_with_folding_footrest` | rec_playground_swing_799839ac6c084c288ccc508d42c1d5ec | L54-L244 | disc seat and folding footrest part |
| S15 | seat_payload | `nest_basket_seat` | rec_playground_swing_f117b975f8d54a95b642d00a4c44a425 | L116-L214 | basket ring, rope weave, lower rocking pivot |
