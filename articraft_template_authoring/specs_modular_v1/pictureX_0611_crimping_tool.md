# pictureX_0611_crimping_tool — modular spec

## 元信息

| 项 | 值 |
|---|---|
| slug | `pictureX_0611_crimping_tool` |
| template path | `agent/templates/pictureX_0611_crimping_tool.py` |
| test path (optional) | — (sweep-pipeline 为验收信号，暂不写 pytest) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children：head/controls 模块的 part 挂到 skeleton 的 frame/carrier；multiplicity：die station / turret nest / nest pair 计数） |

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (3 originals + 5 confirmed forks, rated_by=picturex_0611_centrifuge_to_drafting_variant_confirmed_20260714) |
| source_index_policy | only adopted module sources are indexed below；全部 8 条样本均被采纳（无排除样本） |

Source id 约定（下文引用）：

- S1 = `rec_picturex_0611__crimping_tool__001__png_b1dc55ef9a464866b3da68627196df5e`
- S2 = `rec_picturex_0611__crimping_tool__002__png_bb7fbd8e74a44490a20087674b984a06`
- S3 = `rec_picturex_0611__crimping_tool__003__png_5ac1472bfeda42a5b4e6a2b4aa673fbc`
- S4 = `rec_picturex0611_crimping_tool_fork_single_hex_die_20260714`（fork of S2）
- S5 = `rec_picturex0611_crimping_tool_fork_six_station_die_20260714`（fork of S2）
- S6 = `rec_picturex0611_crimping_tool_fork_interchangeable_cassette_20260714`（fork of S1）
- S7 = `rec_picturex0611_crimping_tool_fork_rotating_turret_die_20260714`（fork of S1）
- S8 = `rec_picturex0611_crimping_tool_fork_four_indent_head_20260714`（fork of S3）

## 核心身份

手动棘轮式端子压接钳（manual ratcheting terminal crimper）：两支长柄以复合杠杆/棘轮机构
驱动一对相向闭合的压接模（die），模上有一或多个端子工位；具有可再打开的释放机构
（release lever / pawl）和压力调节件（star wheel / dial）。类别铁律：**始终是"两柄复合闭合 +
真实闭模机构 + 释放路径"的压接工具** —— 不是剪线钳（wire cutter only）、不是普通钳子
（pliers without dies）、不是孤立模块（die set alone）、不是液压/台式压机。

三条原始样本给出**三种不同的 frame/linkage 骨架**（这是本类的 ① 主轴，也是 ③ 主体形态家族载体）：

1. S1：开 V 形锻造双柄 + 浮动 die carrier + 非对称 drive link 的复合关节头。
2. S2：紧凑层叠板式（laminated cheek plates）棘轮架，上模绕主销 mimic 反向闭合。
3. S3：一体宽头 lower body + 上柄小角度棘轮开合 + 内置 press plate 的直列压头。

die-bank 多重性（N∈{1,5,6} 锚点）与 head 机构（cassette / turret / four-indent）按骨架家族 gating，
不跨骨架混用（见 §9 compatibility matrix）。

## 槽位 + 候选模块表

### Slot A：`skeleton`（frame + 双柄 + 主闭合机构；① 骨架图 + ③ 主体形态家族载体）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_v_compound` | forked_anchor | S1 | L101-L273（fixed_handle L101-L181；moving_handle L184-L262；main_closing_pivot L264-L273）+ die_carrier/drive_link L276-L348 | eligible | root `fixed_body`（锻造 shank 板 + 橙色 grip + 橡胶 inset + 铆钉群）+ `moving_handle`（对称锻件）+ REVOLUTE 主闭合销（0..0.42）+ `die_carrier`（REVOLUTE, mimic ×1.78）+ `drive_link`（REVOLUTE 小摆角）。cadquery 挤出多边形 + 圆盘。③ form_subtype=Planar Boundary Form：高瘦开 V 钳形轮廓 |
| `layered_ratchet_frame` | forked_anchor | S2 | L132-L237（fixed_frame L132-L170；moving_handle L172-L196；handle_pivot L198-L206；upper_die die_pivot mimic −0.65 L222-L237） | eligible | root `fixed_body`（capsule shank ∪ 开窗 side cheek plate + 蓝 grip + 贯穿销组）+ `moving_handle`（capsule shank，带真孔）+ REVOLUTE handle_pivot（−0.12..0.22, 带 rpy 预转）+ `upper_die`（REVOLUTE mimic 反向）。③ form_subtype=Planar Boundary Form：短粗层叠板轮廓 |
| `inline_press_frame` | forked_anchor | S3 | L92-L292 + 关节 L352-L381（lower_body 宽头板 L104-L157；上柄 L259-L292；main_pivot 0..12° L352-L366；press_motion mimic 0.70 L367-L381） | eligible | root `fixed_body`（一体宽头板 + raised head layer + 蓝 grip 带指槽 + 红 accent + 销/螺钉群）+ `upper_handle`（钳制小开角）+ `press_plate`（REVOLUTE mimic 0.70）。③ form_subtype=Planar Boundary Form：直列宽头长柄轮廓 |

### Slot B：`die_head`（压接模组 / head 机构；② 机构 + multiplicity 载体；按 skeleton gating）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `integral_fixed_die` | forked_anchor | S1 | L49-L81（_fixed_die/_moving_die 端子巢挖孔）+ L119-L123（fixed die visual on root）+ L289-L293（moving die visual on carrier） | eligible if skeleton=open_v_compound | 固定模块贴 root、移动模贴 die_carrier（均为 parent visual，不新增 part）；巢对数 `nest_pair_count`∈{2,3,4}（S1 源 3 对，loop 参数化） |
| `cassette_die` | forked_anchor | S6 | L84-L127（cassette shell/rails/notch + latch lever）+ L328-L348（carrier 增厚 + cassette_rail_{i}）+ L407-L456（die_cassette FIXED 捕获 + cassette_latch REVOLUTE −0.35..0.55） | eligible if skeleton=open_v_compound | 新 part `die_cassette`（FIXED，导轨捕获，有 docstring 理由）+ `cassette_latch`（REVOLUTE on carrier）；固定模同 S1；巢对数同上 |
| `turret_die` | forked_anchor | S7 | L49-L126（turret body 环轮 + 减重孔 + 檐口 detent + nest 块放置）+ L183-L193, L252-L257（mount boss + pivot shaft on root）+ L480-L524（die_turret part + turret_index REVOLUTE 0..1.5π） | eligible if skeleton=open_v_compound | 新 part `die_turret`（REVOLUTE 分度轮 on root）+ `turret_nest_count`∈{3,4,5} 个 loop-emitted nest 块（S7 源 N=4）；移动模同 S1 贴 carrier |
| `single_hex_die` | forked_anchor | S4 | L50-L98（_hex_cavity + 单工位 _jaw_plate）+ L217-L246（lower 折入 root visual / upper_die REVOLUTE mimic） | eligible if skeleton=layered_ratchet_frame | 单个居中六角工位（die_station_0）成对刻入上下 jaw plate；N=1 边界锚点 |
| `profile_station_die` | forked_anchor | S2 + S5 | S2 L50-L89（5 工位：3 圆 + 2 阶梯槽）；S5 L50-L116（_DIE_STATION_DEFS 六工位 0.018 规则间距 loop-emitted） | eligible if skeleton=layered_ratchet_frame | `die_station_count` N∈{3,4,5,6}（锚点 N=5 源、N=6 fork；loop 计数参数化，规则间距）；lower jaw 折入 root visual，upper jaw = `upper_die` part（skeleton 出关节）；locator tab（S2 L279-L300）折入 upper_die visual |
| `connector_press_head` | forked_anchor | S3 | L145-L171（die frame 三连接器腔 + 腔底）+ L296-L313（press_plate 三 press teeth） | eligible if skeleton=inline_press_frame | die frame + RJ45/RJ11/aux 三腔（源固定 3 腔，属机构身份，不做 N 轴）贴 root；press plate 承 press_tooth_{i} |
| `four_indent_head` | forked_anchor | S8 | L69-L81（radial head 环盘 + 4 径向导槽）+ L176-L203（terminal bore + guide walls）+ L324-L423（4 个 indenter part + REVOLUTE mimic 关节 + pivot pins） | eligible if skeleton=inline_press_frame | 径向头替换 die frame；4 个 loop-emitted `indenter_{i}` part（REVOLUTE mimic main_pivot，收敛压入）；N=4 是"four-indent"机构身份，固定不采样 |

### Slot C：`controls`（释放 + 调节控制组；② 机构；按 skeleton gating）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `lever_release_star_dial` | forked_anchor | S1 | L350-L373（release 锻造拇指杆 + rivet, REVOLUTE −0.28..0.22）+ L375-L398（八角 star wheel 压力盘, CONTINUOUS） | eligible if skeleton ∈ {open_v_compound, inline_press_frame} | `ratchet_release` part + `pressure_dial` part，均铰在 root 控制锚点（skeleton 导出 pivot 点位）；star wheel 为 CONTINUOUS |
| `paddle_release_disc_dial` | forked_anchor | S3 | L315-L333（release pivot + paddle + tip）+ L335-L350（adjustment dial + index tab）+ L382-L399（REVOLUTE −0.25..0.32 与 REVOLUTE −π..π） | eligible if skeleton ∈ {open_v_compound, inline_press_frame} | `ratchet_release`（paddle 柱塞式）+ `adjustment_control`（圆盘 dial）铰在 root 的 boss 锚点（boss 由 skeleton/root 出 visual, S3 L246-L257） |
| `handle_pawl_release` | forked_anchor | S2 | L241-L257（ratchet_link 桥板, REVOLUTE on moving_handle −0.16..0.14）+ L259-L275（release_pawl, REVOLUTE on moving_handle −0.24..0.20） | eligible if skeleton=layered_ratchet_frame（依赖 moving shank 上的真孔 + 销位 L174, L185-L204） | `ratchet_link` + `release_pawl` 两个薄板 part 铰在 moving_handle 销上 |

硬约束核对：

- Slot A 3 候选、Slot B 7 候选（按骨架分族 2-3 个可达）、Slot C 3 候选（open_v/inline 各 2 可达，layered 1 可达——该族控制件依赖 moving shank 真孔与销位，跨骨架无源支撑，故 gating 收窄；整体 slot 候选数 ≥3 合规，layered 分支单候选在 §9 记录为 gated-single 而非独立 slot）。
- 所有候选均 `source_type=forked_anchor` 且有真实 `model.py:Lx-Ly`；无 world_knowledge_extrapolation 结构候选。③ 主体形态家族由 Slot A 的三个骨架轮廓承载（3 个可识别原型，全部 source-backed），登记进 `slot_choices`（`skeleton` 键）。
- 候选间均为结构差异（part 树 / 关节数 / 机构不同），非换色换尺寸。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
skeleton(root fixed_body)
  ├─[REVOLUTE main pivot, axis (0,0,±1), 源限位]→ moving_handle          （Slot A 内部）
  ├─(open_v) moving_handle ─[REVOLUTE mimic ×1.78]→ die_carrier ─[REVOLUTE ±0.2]→ drive_link
  ├─(layered) fixed_body ─[REVOLUTE mimic −0.65]→ upper_die              （关节属 Slot A，几何由 Slot B 填）
  ├─(inline)  fixed_body ─[REVOLUTE mimic 0.70]→ press_plate
  │
  ├─ Slot B die_head：视觉贴 fixed_body / die_carrier / upper_die / press_plate；
  │    cassette_die 额外： die_carrier ─[FIXED 捕获]→ die_cassette；die_carrier ─[REVOLUTE −0.35..0.55]→ cassette_latch
  │    turret_die  额外： fixed_body ─[REVOLUTE 0..1.5π 分度]→ die_turret
  │    four_indent 额外： fixed_body ─[REVOLUTE mimic ×4]→ indenter_{0..3}
  │
  └─ Slot C controls：fixed_body ─[REVOLUTE]→ ratchet_release；fixed_body ─[CONTINUOUS/REVOLUTE]→ pressure_dial/adjustment_control
       （layered：moving_handle ─[REVOLUTE]→ ratchet_link；moving_handle ─[REVOLUTE]→ release_pawl）
```

- Slot 顺序：skeleton → die_head → controls。die_head/controls 均为 parallel-children，读 skeleton 导出的
  锚点（InterfaceSpec dict：`head_mount`（root 头部面）、`carrier_face`（open_v）、`upper_die_pivot`（layered）、
  `press_face`（inline）、`release_pivot` / `dial_pivot`（控制销点位, 各骨架单源导出））。
- 主闭合销的跨 part 接口：laminated plate 面对面贴合（S1 主销盘 `main_pivot_shaft` 顶面 ↔ moving shank 底面；
  S2 侧板/boss 顶面 ↔ moving shank 底面；S3 头板顶面 ↔ upper shank 底面）→ 落成 MatingContract。
- 互斥：Slot B / Slot C 候选按 skeleton gating（见 §9），无 optional slot；die_head 与 controls 相互独立。

## 每槽位 Module Emits / Interfaces

### Slot A / `open_v_compound`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_body`（shank 板 + grip + rubber inset + stop + 铆钉/销盘）、`moving_handle`、`die_carrier`、`drive_link` | S1 L101-L262, L276-L348 |
| internal joints | `main_closing_pivot` REVOLUTE axis(0,0,−1) [0,0.42]；`handle_to_die_carrier` REVOLUTE mimic ×1.78 [0,0.76]；`carrier_to_drive_link` REVOLUTE [−0.22,0.18] | S1 L264-L273, L308-L318, L339-L348 |
| upstream interface | root（无上游） | — |
| downstream interface | `head_mount`（root 头部 +y 区）、`carrier_face`（die_carrier 板面）、`release_pivot`/`dial_pivot`（root 销盘位, S1 L172-L181） | S1 L157-L181 |

### Slot A / `layered_ratchet_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_body`（shank∪cheek plate + grip + 贯穿销组）、`moving_handle`（带真孔 shank + grip + 2 销）、`upper_die`（几何由 Slot B 填充） | S2 L132-L206, L222-L237 |
| internal joints | `handle_pivot` REVOLUTE axis(0,0,1) [−0.12,0.22]（origin rpy 0.17）；`die_pivot` REVOLUTE mimic −0.65 [−0.15,0.07] | S2 L198-L206, L228-L237 |
| upstream interface | root | — |
| downstream interface | `jaw_plate_frame`（上下 jaw 轮廓基准）、`upper_die` part 名、moving_handle 销位（`linkage_pivot`/`release_pivot`） | S2 L50-L111, L185-L204 |

### Slot A / `inline_press_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fixed_body`（宽头板 + raised layer + 切/剥刃 + grip 指槽 + accent + 销/boss）、`upper_handle`、`press_plate`（teeth 由 Slot B 填） | S3 L92-L313 |
| internal joints | `main_pivot` REVOLUTE axis(0,0,1) [0,0.21]；`press_motion` REVOLUTE mimic 0.70 [0,0.147] | S3 L352-L381 |
| upstream interface | root | — |
| downstream interface | `head_mount`（die frame 区域）、`press_face`（press_plate 板面）、`release_pivot`/`dial_pivot`（ratchet/adjustment boss, S3 L246-L257） | S3 L145-L157, L246-L257 |

### Slot B（代表：`profile_station_die`；其余同表结构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part（jaw 几何：lower 折入 `fixed_body` visual、upper 填入 `upper_die`）；cassette_die：`die_cassette`+`cassette_latch`；turret_die：`die_turret`；four_indent_head：`indenter_{0..3}` | S2/S5 L50-L116；S6 L407-L456；S7 L480-L524；S8 L324-L423 |
| internal joints | cassette：FIXED（捕获）+ REVOLUTE latch；turret：REVOLUTE 分度；four_indent：4×REVOLUTE mimic | 同上 |
| upstream interface | skeleton 的 `head_mount`/`carrier_face`/`upper_die`/`press_face` 锚点 | Slot A downstream |
| downstream interface | 无（叶模块） | — |

### Slot C（代表：`lever_release_star_dial`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ratchet_release`（杆 + rivet）、`pressure_dial`（star wheel + hub）；paddle 版为 paddle+tip / dial+index；layered 版为 `ratchet_link`+`release_pawl` | S1 L350-L398；S3 L315-L350；S2 L241-L275 |
| internal joints | REVOLUTE release [−0.28,0.22]（或源限位）；CONTINUOUS star dial / REVOLUTE dial [−π,π] | 同上 |
| upstream interface | skeleton 导出的 `release_pivot`/`dial_pivot`（或 layered 的 moving_handle 销位） | Slot A downstream |
| downstream interface | 无（叶模块） | — |

要求核对：不动细节（rubber inset、红 accent、locator tab、腔底、销帽、rail、boss）一律 parent visual；
活动件（moving_handle、die_carrier、drive_link、upper_die、press_plate、cassette_latch、die_turret、
indenter、release、dial、link、pawl）均有 articulation 语义。

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `skeleton` | enum | open_v_compound / layered_ratchet_frame / inline_press_frame | — | choice | deterministic procedural sampler | Slot A 表 |
| `die_head` | enum | 7 候选 | — | conditional choice | 合法域依赖 skeleton（§9 matrix） | Slot B 表 |
| `controls` | enum | 3 候选 | — | conditional choice | 合法域依赖 skeleton（§9 matrix） | Slot C 表 |
| `palette_style` | enum | safety_orange / workshop_blue / blue_red_pro / red_black / yellow_black | — | choice | 涂装轴（⑥），仅换材质色 | S1/S2/S3 材质 + 世界知识补 2 组配色 |
| `die_station_count` | int | {3,4,5,6}（profile_station_die）；single_hex_die 恒 1 | 5 | conditional | 仅 layered 系 die 模块；间距×(N−1) ≤ jaw 工作跨度（pitch 0.018 源值，N≤6 可行） | S2 L62-L73；S5 L50-L61 |
| `nest_pair_count` | int | {2,3,4}（integral_fixed_die / cassette_die） | 3 | conditional | 巢心距沿 die 块高度均布，随 head_scale 缩放；巢半径按 §7 不等式派生收缩（N=4 时 k≈0.75） | S1 L55-L63, L73-L80 |
| `turret_nest_count` | int | {3,4,5}（turret_die） | 4 | conditional | 站角 2π/N；nest 块径向布置在 turret 轮辋 | S7 L60-L126 |
| `scallop_count` | int | {3,4,5}（inline grip 指槽，④装饰数） | 4 | conditional | 槽心沿 grip 下缘均布（由 grip 长度派生） | S3 L203-L206 |
| `handle_scale` | float | [0.90, 1.15] | 1.0 | independent | clamp；柄长/grip 长按同因子缩放 | S1/S2/S3 柄长 |
| `head_scale` | float | [0.92, 1.10] | 1.0 | independent | clamp；die 块/turret/jaw 轮廓整体缩放 | 同上 |
| `grip_thickness_scale` | float | [0.90, 1.12] | 1.0 | independent | clamp；仅 grip 剖面厚度 | S1 L124-L145 |
| `jaw_open_scale` | float | [0.85, 1.0] | 1.0 | independent | 主闭合关节 upper=源上限×scale（只收不放，防穿模） | S1 L271 / S2 L205 / S3 L361 |
| `grip_length` | float | derived | — | equation | `= 源 grip 长 × handle_scale`（与柄同步，防 grip 悬出柄端） | S1 L124-L133 |
| (—) | constraint | — | — | inequality | layered：`0.018×(die_station_count−1)×head_scale ≤ 0.095×head_scale`（源 jaw 跨度）恒成立于 N≤6；turret：nest 块宽 0.011 < 弦距 2R·sin(π/N)（N≤5 且 R=0.016 时成立，N>5 拒绝） | 接口 / clearance |
| (—) | constraint | — | — | inequality | open_v 巢梯：相邻两巢半径和 + 筋宽 ≤ 巢距，即 `r_i + r_{i+1} + 1.2mm ≤ (y1−y0)/(N−1)`。N=2/3 恒成立（k=1，锚点 N=3 与 S1 逐位一致）；**N=4 时源半径和 9.1mm > 巢距 8mm，会把 die 块前唇割断成两个 solid（islands，与 head_scale 无关）**，故半径整梯按 `k=min(1,(pitch−1.2)/max(r_i+r_{i+1}))` 派生收缩（N=4：fixed k≈0.747 / moving k≈0.696）。域不截断，靠派生保可行 | `_nest_radius_scale`；S1 L55-L63 |

连续尺寸采样契约：先采 4 个 independent scale（均匀）→ 派生 grip_length 等 equation 量 →
inequality 由 N 上限静态保证（N 域已按不等式截断，超界组合不进入采样域）→ conditional
（多重性计数、scallop）按上游 enum 解析。全部在 `resolve_config` 内完成。

### 7.5 编译预算 / compile budget

**每 seed ≤ 20s**。依据：三骨架均为 cadquery 挤出多边形/圆盘布尔（同源记录单件编译即此量级；
库内典型模板 5-20s），无重雕刻/放样。分档 tessellation：`mesh_from_cadquery` tolerance 取源值档
（0.0004-0.0007 m 或 mm 源的 0.12），小圆特征不加密；N 个同构 die 站/巢/nest 在同一 jaw/turret
solid 上布尔（单 mesh），indenter 4 件共享同一构造函数。超预算先降 tolerance 再迭代。

## Multiplicity / Copy Logic

三根窄多重性轴（均按 §8 逐轴声明；N 只覆盖不计 distinct）：

1. **`die_station_count`**（layered 系 jaw 工位数）
   - count_param：`die_station_count`；N_range：产品域 {1,3,4,5,6}（1 由 `single_hex_die` 模块承载，
     3-6 由 `profile_station_die` loop 承载）；锚点：N=1（S4）、N=5（S2）、N=6（S5）。
   - sampling domain / 权重：single_hex 0.2；N=5 0.32、N=4 0.16、N=3 0.16、N=6 0.16（源锚 N=5 最常见）。
   - copied object：jaw 工位腔（圆巢 / 阶梯槽 / 六角腔），成对刻入上下 jaw plate；
     naming：`die_station_{i}`（meta 记数）；placement：0.018×head_scale 规则间距（S5 L107 注释）；
     joint policy：工位是布尔腔，无独立关节；source/gating：仅 layered_ratchet_frame。
2. **`nest_pair_count`**（open_v 系固定/移动 die 块巢对数）
   - N_range {2,3,4}；锚点 N=3（S1 L55-L63 三巢）。权重：3 0.5 / 2 0.25 / 4 0.25。
   - copied object：对置圆巢 cutter 对；placement 沿 die 块均布；无独立关节；仅 open_v 系
     `integral_fixed_die`/`cassette_die`（turret 的巢按轴 3 计）。
   - **巢半径不是自由常量**：N 增大时巢距 (y1−y0)/(N−1) 收窄，相邻巢半径和一旦超过巢距就会
     合并并割断 die 块前唇。故半径整梯按 §7 不等式派生收缩（`_nest_radius_scale`）：
     N=2/3 返回 k=1（锚点几何与 S1 逐位一致，不受影响），仅外推档 N=4 收缩。
     此前 N=4 在全部 head_scale 下都把 fixed die 割成 2 个 solid（seed 21 islands）。
3. **`turret_nest_count`**（turret 轮辋 nest 块数）
   - N_range {3,4,5}；锚点 N=4（S7 L60-L61）。权重：4 0.5 / 3 0.25 / 5 0.25。
   - copied object：`nest_{i}` 块（共享构造 + 逐站旋转放置，S7 L116-L126）；随 turret part 一体，
     分度关节唯一；gating：仅 turret_die。

four_indent_head 的 4 indenter 为机构身份常数（"four-indent"），不作为采样轴（声明：该子机构无 N 轴）。
connector_press_head 三腔为 RJ45/RJ11/aux 连接器身份常数，不作为采样轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | 3 骨架（open_v：4 活动件链 / layered：2+mimic 上模 / inline：柄+press plate）+ head 机构增件（cassette+latch / turret / 4 indenter）+ controls 增件；全部 forked_anchor（S1-S8） |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：die_station_count {1,3,4,5,6}、nest_pair_count {2,3,4}、turret_nest_count {3,4,5}，各带权重档 |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE（主闭合/carrier/link/release/latch/turret/indenter/dial(S3)）、CONTINUOUS（star dial, S1 L390-L398）、FIXED（cassette 导轨捕获, S6 L421-L428，docstring 理由）、mimic 耦合（S1 ×1.78 / S2 −0.65 / S3 0.70 / S8 收敛式）；全 source-backed；CONTINUOUS 经 controls=lever_release_star_dial 在 sweep 中必现（open_v/inline 双骨架可达） |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | 3 个 Planar Boundary Form 原型 = Slot A 三骨架轮廓（高瘦开 V 锻钳 / 短粗层叠板 / 直列宽头），全部 source-backed（S1/S2/S3），登记进 slot_choices（`skeleton` 键）；head 侧另有 turret 环轮（Volumetric Envelope, S7）与 radial head 环盘（S8）随 die_head 键登记 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | record_only：橡胶 inset 板（S1 L135-L145，贴合 grip 轮廓内缩派生）、红 accent 条（S3 L211-L216，沿 grip 上缘板）、指槽 scallop（S3 L203-L206，从 grip 底缘布尔切除，`scallop_count`∈{3,4,5}）、铆钉/销帽群（S1 L157-L181、S3 L231-L243）、detent 檐口（S7 L85-L95）。全部由宿主 grip/板面派生（③→⑤→④ 顺序：先定骨架轮廓与 scale，再从最终 grip solid 切/贴） |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | 4 个 scale（§7）+ 运动包络：`main_closing_pivot` axis(0,0,−1) 开→合 [0, 0.42×jaw_open_scale]；`handle_pivot`(layered) axis(0,0,1) [−0.12, 0.22×s]；`main_pivot`(inline) [0, 0.21×s]；`carrier_to_drive_link` [−0.22,0.18]；release [−0.28,0.22]/[−0.24,0.20]/[−0.25,0.32]；`carrier_to_latch` [−0.35,0.55]；`turret_index` [0,1.5π]（分度全程）；dial(S3) [−π,π]。motion_test_plan：run_tests 调 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64-96, ignore_fixed=True)` + 每骨架 targeted `ctx.pose`（闭合位模间距 / turret 分度位移 / latch 开摆 / indenter 收敛 / 柄开合位移）；mimic 关节随驱动采样；无 sampled-pose exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：painted steel（黑氧化）、bare metal（镀锌/抛光销件）、polymer/rubber（grip、TPE inset）、hardened die steel；5 组 palette（橙黑 S1 / 蓝黑银 S2 / 蓝红黑 S3 / 红黑、黄黑为纯配色外推）；材质大类覆盖 4 ≥ ceil(0.5×4) |

收尾自检：0-9 seed 渲染须肉眼可见 —— 三骨架轮廓拉开、N 档变化、turret/cassette/four-indent 至少一现、
star dial 与 paddle dial 均出现、5 palette 中 ≥3 出现、grip 装饰贴合、关节全程不穿模。

## 采样与覆盖审计

总组合数（离散结构）：skeleton×die_head×controls 合法组合 = open_v(3×2) + layered(2×1) + inline(2×2) = 12；
乘 multiplicity 档（open_v ×3 nest 档 / turret 另 ×3、layered profile ×4）≈ 38 结构 tuple；再 ×5 palette ≈ 190
slot-choice tuple 上限。

理由：结构组合空间受三骨架不可跨族混装约束（frame 坐标系/承载件/接口点位互不共享——
S1 的 carrier 链、S2 的层叠销组、S3 的宽头板互斥），故 tuple 上限 ~190 < 300；
属"组合空间饱和、受源锚点约束"的合法状态（report-only）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 每 seed 按上表权重先采 skeleton，再按
compatibility matrix 条件采 die_head/controls/multiplicity/palette/scales；无 regression overrides；
`slot_choices_for_seed` 返回 (skeleton, die_head, controls, die_station_count|nest_pair_count|turret_nest_count, palette_style)。
Random sweep：sweep-pipeline 0-15 → 0-35 → corner；viewer 目检 0-9。
Topology target：~190 tuple 上限（见上），report-only。
Controlled local parameterization：handle_scale / head_scale / grip_thickness_scale / jaw_open_scale
（§7 范围与约束），均在 resolve_config clamp/派生，不破坏接口、销点位、multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | skeleton 加权 → die_head/controls 条件加权 → N 条件加权 → palette/scales | slot_choices_for_seed 与 build 一致 |
| compatibility matrix | die_head：open_v→{integral,cassette,turret}；layered→{single_hex,profile_station}；inline→{connector_press,four_indent}。controls：open_v/inline→{lever_star, paddle_disc}；layered→{handle_pawl}。非法组合不可达（条件采样，无降级路径） | 不出现跨骨架 head/controls；latch/turret/indenter 只在对应骨架出现 |
| controlled local variation | 4 scale clamp；grip_length 派生；N 域静态截断 | 比例变化不破坏销点位/贴合/闭合位 |
| regression overrides | none | — |
| random sweep | 0-35 + corner（pipeline 默认） | contract failures；axis_realization 确认每个候选/每档 N/CONTINUOUS 均出现 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| skeleton | 3 | yes | yes | ①+③ 载体 |
| die_head | 7 | yes | yes | 按骨架 gating（各族 2-3 可达） |
| controls | 3 | yes | yes | layered 分支 gated-single（源约束，见 Slot C 表） |

## Validator

- slot_choices_for_seed returns implemented module names（与 build 选择一致）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed 0 不特殊）
- compatibility matrix（条件采样）prevents illegal skeleton×head×controls 组合
- no regression overrides；不循环 curated 表
- 4 个 scale 在 resolve_config clamp；grip_length 等派生量不独立采样
- N 轴（die_station_count / nest_pair_count / turret_nest_count）域静态可行，loop 命名 `die_station_{i}` / `nest_{i}` / `indenter_{i}` 稳定
- 主闭合关节 / mimic 关节 type、axis、range 与源一致（S1/S2/S3 语义）
- 每个新 child part 有可见支撑（销盘/boss/rail/轮辋），捕获销类 overlap 用 element-scoped allow_overlap；
  零 whole-part allowance；每条 allowance 须经"关闭 allowance 的碰撞扫描"证实确有接触
  （宣称"faces meet"却实为间隙的声明必须删除，不得留作掩护）
- 主闭合销 MatingContract（三骨架各一：销盘顶面/侧板顶面/头板顶面 ↔ moving shank 底面）通过 gap 检查；
  纯捕获销关节（dial、release、turret、latch、indenter、carrier）按 Rule 2 grandfather（省略 mating）并注释
- run_tests 含 sampled-pose 碰撞 + 每机构 targeted ctx.pose

## Reject cases

- 出现剪线钳/普通钳（无对置 die、无释放机构）→ 类别身份失败
- head/controls 跨骨架混装（如 turret 装在 layered 上）→ 非法组合
- die 工位间距 × N 超出 jaw 跨度 → 工位溢出轮廓
- moving_handle 全闭时与 fixed grip 穿模（jaw_open_scale 失效）
- cassette/latch 悬空（无 rail/carrier 支撑路径）
- turret nest 块在分度全程与 moving die 深穿模（>源容忍 0.012）
- mimic 方向反号（闭柄时模张开）→ targeted pose 检查失败
- star dial CONTINUOUS 从未在 sweep 实现（controls 权重失衡）→ ② 覆盖失败
- 装饰（inset/accent/scallop）与 grip 最终表面脱节（未按 ③→⑤→④ 派生）

## 与相邻类别的边界

- 不该混入：**wire stripper / wire cutter**（Electrical_Wiring_Wire_stripper 已有模板；本类必须有对置压接模与棘轮释放，刃口只能作为 S3 源的附属特征存在）
- 不该混入：**普通钳 / bolt cutter**（无 die 工位、无复合 mimic 闭模机构）
- 不该混入：**液压/台式压接机**（源池全部为双柄手动工具；无液压缸、无台架）
- 不该混入：**孤立 die set / 模块盒**（cassette/turret 只能作为整钳的 head 机构出现）

## 审核记录

| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 统一世界系：工具平躺 XY 平面、板厚沿 Z、所有铰轴 (0,0,±1)。S1 源为 XZ 立面作图，
  改编时将其 (x,z) 轮廓映射为 (x,y)（同一 cadquery 挤出多边形家族，Rule 3 primitive 保真），
  轴 (0,±1,0)→(0,0,±1)。
- 三骨架 factory 返回 InterfaceSpec 锚点 dict（head_mount / carrier_face / release_pivot / dial_pivot …），
  head/controls factory 只消费锚点，不自定坐标 —— Contract 3c 单源化。
- 捕获销 overlap 清单（element-scoped allow_overlap）：主销盘↔shank 孔、carrier 销、release/dial 销、
  turret 轮毂↔pivot shaft/boss、cassette rail↔cassette body、indenter 臂↔radial head 导槽、
  press plate↔pivot pin。理由均引源 run_tests（S3 L489-L501、S6 L595-L607、S7 L629-L644、S8 L626-L659）。
  **已删除三条不成立的 turret 声明**：`nest_i↔moving_crimp_die`（原理由"crimp die faces meet at
  full stroke"——轴位改正后移动模在活动 nest 前 ~1.8mm 停住，是压接间隙不是捕获接触）、
  `nest_i↔turret_pivot_shaft`、`nest_i↔fixed_shank`。三者经关闭 allowance 的碰撞扫描
  （N=3..5 × head_scale 0.92..1.10 × 全行程）确认从不接触。**已删除两条 whole-part 声明**
  （`carrier↔cassette`、`cassette↔latch`，违反 Rule 7）——前者掩盖了卡匣与 carrier 板 10mm 实穿模。
- die_cassette 用 FIXED + docstring（可拆卡匣被 rail 捕获，非装饰；源 S6 L421-L428 同构）。
- sweep 前先跑 seeds 0-4 smoke 探针。

### 源几何改正（S6/S7 潜在缺陷，本模板按 Rule 5/6 必须修）

三条原始 fork 的自测只采样"authored（张开）位"，全行程穿模从未被它们自己的 run_tests 看到；
本模板按 Rule 5 调 `fail_if_parts_overlap_in_sampled_poses`，因此必须在改编时改正：

| 源 | 源写法 | 实测后果 | 本模板改法（Contract 3e 派生） |
|---|---|---|---|
| S7 L516 | turret 轴冻结在 x=10mm | 活动 nest 工作面落在 −11.5ds，比 die 面（−3ds）后退 8.5mm；移动模越过它、扎进轮辋 ~9.7mm | `_TURRET_CENTER_X_MM = _OPEN_V_DIE_FACE_X_MM + 巢轨半径 + 巢半宽` = 18.5mm；boss / pivot shaft / 分度关节全部读这一个点 |
| S6 L88-L92 | 卡匣外壳前缘直边 (5,34)→(6,84)，超出模工作面 4mm；其顶角绕主销的回转半径比模的工作顶点更大 | 全行程扎进 fixed die 块 8.1mm（**仅退让一个常量不够**，顶角仍撞） | 外壳前壁由模自身前缘轮廓 `_OPEN_V_DIE_FRONT_CHAIN` 派生（退 `_CASSETTE_WALL_MM`），模让开什么它就让开什么 |
| S6 L337 | 卡匣与加厚 carrier 板共占同一块钢（源注释自承 rails"read as one piece"） | `die_carrier_plate ↔ cassette_body` 10mm 实穿模（原被 whole-part allowance 掩盖） | carrier 板切到卡匣尾缘 `_CASSETTE_TAIL_Y_MM` 之下（留 0.3mm 抽出间隙），rails 下探到 y=20mm 生根，由 rails 做真实捕获 |
| S2/S4 jaw | 上模根缘随 head_scale 缩放，但销座（thrust washer）半径是冻结常量 0.0058 | head_scale>1.0033 时 upper_die 与接地体脱开（seed 11 gap 0.156mm）；head_scale=1.0 仅靠 0.019mm 余量侥幸通过 | washer 半径 = `_layered_jaw_root_y(ds) + _LAYERED_JAW_SEAT_EMBED_M`，销座随轮廓共变 |

### 已知遗留（交视觉 QA 判定，均在 gate 容差内、非本轮回归）

- `turret_wheel`（z=[−5.5,5.5]）与 `fixed_shank`（z=[−7.5,−2.5]）在 z 上重叠 3mm，低于
  overlap_tol=5mm 的 AABB 预筛，故不报；`turret_wheel↔turret_mount_boss` 则是 7mm 实重叠，
  靠 element-scoped allowance 放行。两者都是 S7 turret 装配的 z 分层遗留（轴位改正前后一致，
  非本轮引入）。若视觉 QA 判定轮辋"陷进"柄板，需重排 S7 turret 的 z 栈（本轮未动）。
