# pictureX_0611_Desk_with_drawers_no_door — modular spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Desk_with_drawers_no_door` |
| template path | `agent/templates/pictureX_0611_Desk_with_drawers_no_door.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Desk_with_drawers_no_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed`（`parallel_children` + `multiplicity`） |

## Category Binding

category_slug: pictureX_0611_Desk_with_drawers_no_door · template_slug: pictureX_0611_Desk_with_drawers_no_door ·
mechanism_profile: prismatic_sliding_only（drawer / keyboard tray / tambour，全部 PRISMATIC；类别身份禁止 REVOLUTE 门扇）· export_namespace: pictureX_0611
diversity_profile: `constrained` ·
profile_reason: 诚实核心词汇 = ① support_family(5) × ③ worktop_form(3) × ② front_accessory(2)，
经 compatibility gate 后 **core_domain = 12**（见 `## Combination Domain`）。④ pull_style /
top_finish、⑥ palette 与连续尺寸按 counting policy 不计入 core；N 只进 raw。
本类别真实结构词汇受源池限制（5 origins 各一个支撑家族；③ 的 L-return 与 roll-top 各自只有
一个 gate 住的支撑锚点；② 只有 tray/none），诚实计数低于 constrained 下限 16，**不为达标
把 palette/pull/finish/N 乘进 core**。见 `## Combination Domain` 的 exception 说明。

`pattern` 说明：一个刚性 `desk_frame`（root part，承载 worktop + 支撑家族 + 抽屉 bank 壳体）
并联挂载 N 个独立抽屉（每屉一条 PRISMATIC）、可选 keyboard_tray（PRISMATIC）与可选
tambour（PRISMATIC，仅 roll_top）。抽屉数量 N（按支撑家族容量 gate）是主 multiplicity 轴；
support_family（①）与 worktop_form（③）是结构 slot。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 (5 origins + 3 forks, rating=5, rated_by=picturex_0611_centrifuge_to_drafting_variant_confirmed_20260714) |
| read_count | 8 |
| read_scope | all 5-star samples in this category, each revisions/rev_000001/model.py read in full |
| source_index_policy | only adopted module sources are indexed below; 本池 8 个样本全部被采纳（无 read-but-not-adopted 样本，故无排除项） |

样本缩写（下文引用）：
- `001` = rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b（roll-top twin-pedestal antique desk）
- `002` = …__002__…_7613e188f1a643e0ae2025f65a32cc54（slab-panel rectangular desk）
- `003` = …__003__…_e8f92b30f5d64469bc7be694c4008080（tubular sled modern desk）
- `004` = …__004__…_d23b1cac1d54454d99cc04c6c0bc6fcf（four-leg writing desk）
- `005` = …__005__…_69a514c4d7e942d49d0a196cbfa9012b（floating-top single pedestal desk）
- `fork_n8` = rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714（N=8 mirrored pedestals，fork of 005）
- `fork_n2` = rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714（N=2 shallow apron，fork of 004）
- `fork_lret` = rec_picturex0611_desk_with_drawers_fork_l_shaped_return_20260714（③ L-return worktop，fork of 003）

## 核心身份

一张**无门工作书桌（doorless work desk with sliding drawers）**：矩形（或 L 形/带 roll-top
罩）worktop 由接地支撑家族承载，正面保留**开放的膝部空间（open knee space）**，一组独立
可拉出的抽屉（每屉一条 PRISMATIC，axis (0,-1,0)，朝就座者 -Y 方向拉出，行程 ~0.27–0.34 m）
安放在 pedestal / apron bank 壳体内；后方浅 modesty panel 不落地、不封膝部。可选机构：
under-top keyboard tray（PRISMATIC -Y）与 roll-top tambour（PRISMATIC +Y，缩回罩下）。
**每个 seed 必须同时满足：开放膝部空间 ≥0.32 m、至少一个真滑动抽屉、全模型无任何门
（REVOLUTE 门扇）**。

不该混入：
- **dresser / Cabinet_with_drawers（纯抽屉柜）**：全宽抽屉塔无膝部空间 → 不是本类。
- **door cabinet / sideboard**：出现 REVOLUTE 门扇 → 跨类。
- **dining table**：无抽屉纯桌面 → 不是本类。
- **drafting table**：倾斜/可倾桌面 → 不是本类（worktop 恒水平）。

## 槽位 + 候选模块表

### Slot A：support_family（① 骨架 / 支撑家族 + 抽屉 bank 布局，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `twin_pedestal` | forked_anchor | fork_n8（← 005）+ 001 | fork_n8 L20-L34（常量）,L207-L301（镜像 bank 循环：inner/outer wall + back + bottom + top deck + plinth + 4 feet + fixed rails）,L303-L316（modesty + knee rails）；001 L248-L280（twin plinth/panels） | eligible if compatible | 两个镜像 4 壁 pedestal 箱夹中央膝部 bay；每 bank rows 个抽屉；modesty + knee rails 跨 bay |
| `panel_pedestal` | origin_anchor | 005 | 005 L190-L216（left full panel + floor rail + front edge + top spacers）,L218-L266（right pedestal：2 sides/back/bottom/top/plinth/4 feet）,L268-L282（浅 modesty + 2 knee rails）,L284-L304（fixed rails） | eligible if compatible | 左满高端板 + 右单 pedestal，中间开放膝部 bay，顶板悬浮于 spacers |
| `slab_panel_shelf` | origin_anchor | 002 | 002 L65-L92（end panel + shelf divider + left plinth + open shelf + band）,L94-L130（pedestal 双板 + plinth + back + cubby floor）,L132-L146（modesty + grain 条）,L147-L161（4 对钢 rail）,L177-L186（圆柱脚垫） | eligible if compatible | 左端板 + 窄开放搁架 bay + 右 pedestal（上部开放 cubby），层压板语言 |
| `tubular_sled` | origin_anchor | 003 | 003 L96-L121（tube_from_spline_points 雪橇管架 ×2）,L123-L139（前/后 tie rail 圆柱）,L141-L149（floor glides）,L165-L205（悬挂 pedestal + mounting blocks）,L207-L225（cabinet rails + frame brackets） | eligible if compatible | 两条连续镀铬管雪橇框 + 悬挂式抽屉柜（不落地），tie rails 连接 |
| `four_leg_apron` | forked_anchor | 004 + fork_n2（← 004） | 004 L24-L42（`_turned_leg_geometry` LatheGeometry）,L45-L53（`_arched_apron_geometry` ExtrudeGeometry 拱）,L157-L201（两 bank 壳体 + wood runners）,L203-L235（apron + modesty + 4 车削腿 + 铜环）；fork_n2 L186-L199（N=2 runner 布局）,L239-L243（浅屉 spec） | eligible if compatible | 4 条车削 Lathe 腿 + 拱形 apron（膝部拱高开），顶板下两浅 apron bank |

所有支撑元素**不动**，作为 `desk_frame` 的 visuals（Rule 1）。车削腿保持 LatheGeometry、
雪橇管保持 tube_from_spline_points、拱 apron 保持 ExtrudeGeometry —— 禁止 Box 降级（Rule 3）。

### Slot B：worktop_form（③ 主体形态家族 / Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `rectangular_slab` | origin_anchor | 002 / 003 / 005 | 002 L49-L63（top slab + front band）；003 L69-L94（slab + 四周 edge bands）；005 L168-L188（悬浮 slab + 边带） | Planar Boundary Form | eligible if compatible | 矩形 Box 顶板 + 边带 |
| `l_shaped_return` | forked_anchor | fork_lret（← 003） | fork_lret L72-L88（cadquery union L 形顶板）,L90-L131（沿 L 周界 6 段边带）,L178-L211（return 雪橇管架 + 连接 rail）,L222-L229（return glides） | Planar Boundary Form | eligible if compatible（仅 `tubular_sled`） | L 形顶板（主翼 + 左后 return 翼）+ return 管架支撑。模板用 ExtrudeGeometry L 多边形 profile 生成同一 union 轮廓 mesh（等价拉伸体，非降级） |
| `roll_top_hood` | origin_anchor | 001 | 001 L30-L49（`_hood_cheek` YZ polyline 拉伸颊板）,L320-L337（hood top/cap/moldings/back/posts）,L339-L359（分段曲线 trim）,L361-L378（pigeonhole organizer + 小抽屉 bank rails）,L409-L441（tambour part + PRISMATIC (0,+1,0) 0..0.18） | Volumetric Envelope Form | eligible if compatible（仅 `twin_pedestal`） | 顶板上加 roll-top 罩（两块阶梯轮廓颊板 + 罩顶 + 鸽笼 organizer + 2×3 小抽屉 bank）+ tambour 滑动帘。颊板用 ExtrudeGeometry 复刻 001 同一 polyline 拉伸（等价，非降级） |

### Slot C：front_accessory（② 关节补充机构，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `keyboard_tray` | origin_anchor | 002 | 002 L163-L175（under-top tray rails ×2）,L282-L309(tray panel + band + 双 runner）,L310-L324（PRISMATIC (0,-1,0) 0..0.255） | eligible if compatible（禁 `four_leg_apron` / `roll_top_hood`） | 顶板下导轨 + 独立滑出托盘 part |
| `none` | origin_anchor | 001/003/004/005 | 001/003/004/005 全文无 tray | always eligible | 无托盘 |

### Slot D：pull_style（④ 表面装饰 / hardware，record_only，登记进 slot_choices，host-conformal）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `bail_pull` | record_only | 001 | 001 L61-L83（`_add_bail_pull`：2 rosette 圆柱 + 2 stem + bar） | 期式吊环拉手，坐进前脸 |
| `bar_pull` | record_only | 002 | 002 L241-L253（2 pull post 圆柱 + 水平 bar） | 缎面金属横拉手 |
| `bow_pull` | record_only | 003 | 003 L227-L242（tube_from_spline_points 弓形管，`.copy()` 复用） | 镀铬弓形拉手（spline tube 保留，非 Box 降级） |
| `knob_rosette` | record_only | 004 | 004 L317-L334（rosette 圆盘 + stem + 黄铜 Sphere） | 古董圆钮 + 花座 |
| `u_pull` | record_only | 005 | 005 L96-L112（pull_bar 横圆柱 + 2 mount 圆柱） | U 形浅金属拉手 |

小抽屉（roll_top 鸽笼屉）固定用 001 L199-L204 的圆柱 knob（跟随其源）。pull 是 last
geometry：y 由抽屉前脸最终外表面派生（前脸恒平面，pull 贴前脸面挂出，Rule 4 ③→⑤→④）。

### Slot E：top_finish（④ 表面装饰，record_only，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `plain` | record_only | 002/003/005 | 002 L49-L63 等 | 素面顶板 + 边带 |
| `leather_inset` | record_only | 004 + 001 | 004 L115-L155（4 边 border 条 + inset leather field + 4 角黄铜 pin）；001 L307-L314（writing leather + 边框条） | 顶板上内嵌书写皮面 + 木边框；z 由顶板最终上表面派生、xy 内缩于顶板 footprint（host-conformal） |

gating：`leather_inset` 仅 `four_leg_apron` / `twin_pedestal`（004/001 的古董语言）；且仅
主翼矩形区域（l_return 不参与 —— l_return 恒 `tubular_sled` 已被 gate 排除）。

### Slot F：palette（⑥ 涂装，登记进 slot_choices）

5 个源配色（各 ≥6 材质键：top/wood/wood_dark/interior/metal/accent/glide）：
`antique_walnut`（001 L232-L237）、`pale_ash`（002 L31-L38）、`graphite_chrome`（003
L59-L65）、`mahogany_leather`（004 L79-L85）、`warm_walnut`（005 L153-L158）。

硬约束满足：support_family 5（①）、worktop_form 3（③，≥3 可识别形态原型：矩形平面边界 /
L 形平面边界 / roll-top 体量包络）、front_accessory 2、pull_style 5、top_finish 2、palette 5。
每个 ①/③/multiplicity candidate 均有 origin/forked anchor + `model.py:Lx-Ly`。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
desk_frame(root; worktop_form ③ + support_family ① + modesty + banks + rails)
  ├─[PRISMATIC axis(0,-1,0), origin=(bank_x, front_face_y, row_z), mating=front_panel(+y)⇄mate_rail_i(−y)]→ drawer_{...} ×N
  ├─[PRISMATIC axis(0,-1,0), mating=tray_runner_0(−x)⇄tray_rail_0(+x)]→ keyboard_tray  （仅 front_accessory=keyboard_tray）
  └─[PRISMATIC axis(0,+1,0), mating=slat_backing(+z)⇄tambour_track_0(−z)]→ tambour     （仅 worktop_form=roll_top_hood）
```

- `desk_frame` 是唯一 root；所有可动件为其并联 PRISMATIC 子件，无串链。
- 抽屉接口：抽屉 `front_panel` 的 **positive_y（背）面** 与 frame `mate_rail_{i}` 的
  **negative_y（前）面** 在 closed pose 于 bank 前平面 `front_face_y` 贴合
  （MatingContract，法向 Y，contact_tol ≤3mm；切向 x/z 自由）。
- tray 接口：tray `tray_runner_0` 的 negative_x 面贴 frame `tray_rail_0` 的 positive_x 面
  （法向 X，行程沿 Y，法向位置全程不变）。
- tambour 接口：tambour `slat_backing` 的 positive_z 面贴 frame `tambour_track_0` 的
  negative_z 面（法向 Z，行程沿 Y）。
- worktop_form / support_family 只改 `desk_frame` visuals 与抽屉 bank 容量/位置，不改抽屉
  part 内部拓扑。互斥：`roll_top_hood`⇒`twin_pedestal`；`l_shaped_return`⇒`tubular_sled`；
  `keyboard_tray` 禁与 `four_leg_apron`（拱 apron 占据顶板下前沿）及 `roll_top_hood` 组合。

## 每槽位 Module Emits / Interfaces

### Slot A / support_family
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（bank 壁/背/底/顶 deck/plinth/feet/腿/管架/端板/搁架/modesty/knee rails/fixed rails 均 desk_frame visuals） | fork_n8 L207-L316；005 L190-L304；002 L65-L186；003 L96-L225；004 L157-L236 |
| internal joints | 无 | — |
| upstream interface | 接地 z=0（feet/plinth/管弯底/腿底） | — |
| downstream interface | worktop 支承面（bank top deck / spacers / apron 顶 / 管架顶弯）+ 每屉 `mate_rail_{i}` negative_y 面 + 膝部 bay [knee_x0,knee_x1] | 005 L400-L419（pedestal supports slab）|

### Slot B / worktop_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rectangular_slab`/`l_shaped_return` 无独立 part；`roll_top_hood` 额外 emit `tambour` part（slat_backing + 12 slats + leading rail/grip）与 6 个 `small_drawer_{b}_{r}` part | 001 L409-L441（tambour）,L399-L407（small drawers） |
| internal joints | `tambour_slide` PRISMATIC axis(0,+1,0) lower=0 upper≈0.18；`small_drawer_*_slide` PRISMATIC (0,-1,0) 0..0.155 | 001 L429-L441,L206-L215 |
| upstream interface | 顶板底面坐在 Slot A 支承面上 | 005 L400-L409 |
| downstream interface | 顶板最终上表面（leather_inset 的 z 派生源）；hood 内 organizer/track 面 | 004 L139-L144 |

### Slot C / front_accessory（keyboard_tray）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `keyboard_tray`（tray_panel + tray_front_band + tray_runner_0/1） | 002 L282-L309 |
| internal joints | `frame_to_keyboard_tray` PRISMATIC (0,-1,0) 0..~0.25 | 002 L310-L324 |
| upstream interface | tray_runner_0 negative_x ⇄ frame tray_rail_0 positive_x（贴合） | 002 L163-L175 |
| downstream interface | 无（叶子件） | — |

### 抽屉 module（multiplicity，loop-emitted；Slot A 决定 bank 位置与 kind）
| emits | 描述 | 来源 |
|---|---|---|
| parts | pedestal 屉 `drawer_{b}_{r}`：front + front_edge_band + bottom + side_0/1 + back + moving_rail_0/1 + pull(s)；apron 屉：front + 4 molding 条 + box bottom/sides/back + pull；small 屉（roll_top）：front + inset + floor + sides + back + knob | 005 L21-L134；004 L246-L334 + fork_n2 L243-L331；001 L152-L216 |
| internal joints | 无（抽屉刚性） | — |
| upstream interface | `front_panel` positive_y 面（贴 mate_rail），local y=0 = joint origin | 005 L44-L49 |
| joint | `frame_to_<drawer>` PRISMATIC parent=desk_frame axis=(0,-1,0) lower=0 upper=travel + damping/friction + MatingContract | 005 L114-L133；004 L336-L354；001 L139-L148 |

## Form Dependency Contracts

本模板的③ 三个 candidate **全部 source-backed**（`rectangular_slab` = 002/003/005；
`l_shaped_return` = fork_lret；`roll_top_hood` = 001），因此**没有 `world_knowledge_extrapolation`
受控外推③**，本表按"无外推③"登记。唯一需要声明的形态-依赖耦合是 `l_shaped_return`：其
轮廓不是自由换形，而是驱动 return 支撑与周界边带的单一 master profile。

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| `rectangular_slab` | 002 `model.py:L49-L63`; 003 `model.py:L69-L94`; 005 `model.py:L168-L188` | `_top_outline()` 矩形 (width, depth) | top_slab；front/rear/side edge bands；支撑家族顶面接触；leather_inset 内缩域 | edge band 沿 outline 周界派生；leather 内缩 `outline − border_w` | `top_slab` AABB == (width, depth)；band 贴 outline | eligible（source-backed，非外推） |
| `l_shaped_return` | fork_lret `model.py:L72-L88`（cq union L 顶）,`L90-L131`（6 段周界边带）,`L178-L211`（return 雪橇管架） | `_top_outline()` 返回 L 多边形（主翼 + 左后 return 翼），单一真源 | top_slab（ExtrudeGeometry 同一 L 多边形）；6 段周界边带；return 雪橇管架 x/y；return glides；modesty 让位 | return 翼 `w=0.407×width`（fork_lret L78: 0.550/1.350）、`ext=0.79×depth`（L78-L81: 0.490/0.620）；return 管架 x = 翼中心；glides 落在管架下弯 | outline 顶点/顺序一致；return 管架顶面 == slab 底面（接触）；膝部 bay 不被 return 侵占 | eligible（仅 `tubular_sled`） |
| `roll_top_hood` | 001 `model.py:L30-L49`（颊板 polyline）,`L320-L378`（hood + organizer）,`L409-L441`（tambour） | `_CHEEK_PROFILE`（(y,z) 轮廓，按 `s=depth/0.70` 缩放）单一真源 | 两块颊板；hood 顶板；organizer 包络；tambour 行程上界；小抽屉 bank z 行 | 颊板 y 按 `s` 缩放；hood 顶 `z0 = slab_top + _HOOD_H`；tambour 上界 = 罩内可用 y − backing 长 − 0.012 | 颊板/罩顶/organizer 共享同一 `s`；tambour 全行程在罩内不撞 organizer | eligible（仅 `twin_pedestal`） |

## 活动机构与运动净空契约

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| pedestal drawer `drawer_{b}_{r}`（005 L21-L134） | front + front_edge_band + bottom + side_0/1 + back + moving_rail_0/1 + pull | bank 内 `fixed_rail_{i}_{0,1}` 双侧纵向导轨（005 L284-L304），bank inner/outer wall 侧向包容 | `front_panel(+y)` ⇄ `mate_rail_{i}(−y)`，contact_tol 3mm | origin=(bank.cx, bank.front_y, row_z)，axis=(0,−1,0)，[0, travel≤box_depth−0.07] | closed: 前脸贴 bank 前平面；mid/max: 屉盒沿 −Y 滑出到开阔膝部前方，侧向与 wall 保留 ≥12mm（005 L490-L505 语义） | 无（滑出方向开阔，无捕获接触） | `fail_if_parts_overlap_in_sampled_poses` + 每屉 targeted `ctx.pose({joint:upper})` 断言 −Y 位移 ≥0.6×travel |
| apron drawer `drawer_{b}_{r}`（004 L246-L354 + fork_n2 L239-L331） | front + 4 molding 条 + box bottom/side_0/1/back + pull | bank 壳体 + `drawer_rail_{i}` 木 runner（004 L186-L201） | 同上 | origin=(bank.cx, bank.front_y, row_z)，axis=(0,−1,0)，[0, travel≤box_depth−0.07] | 同上；apron 屉浅（front_h 0.066/0.076），全程在拱 apron 上方 | 无 | 同上 |
| small drawer `small_drawer_{b}_{r}`（001 L152-L216） | front + inset + floor + side_0/1 + back + knob | organizer 隔板/立柱 | `front_panel(+y)` ⇄ `mate_rail(−y)` | axis=(0,−1,0)，[0, 0.155] | 全程在罩内 organizer 前方，不与 tambour 干涉（tambour 停在 organizer 上方） | 无 | 同上 |
| `keyboard_tray`（002 L282-L324） | tray_panel + tray_front_band + tray_runner_0/1 | 顶板下 `tray_rail_0/1` 双侧钢导轨（002 L163-L175） | `tray_runner_0(−x)` ⇄ `tray_rail_0(+x)`（法向 X，行程沿 Y，法向位置全程不变） | origin=(knee_cx, −0.175×depth, rail_z−0.030)，axis=(0,−1,0)，[0, ≤0.26] | closed: 托盘缩在顶板下；max: 伸入膝部前方开阔空间 | 无 | 同上 + targeted −Y 位移 |
| `tambour`（001 L409-L441） | slat_backing + 12 slats + leading_rail + leading_grip | hood 内 `tambour_track_0/1` 双侧轨 | `slat_backing(+z)` ⇄ `tambour_track_0(−z)`（法向 Z，行程沿 Y） | origin=(0, tambour_oy, tambour_oz)，axis=(0,**+1**,0)，[0, ≤0.20] | closed: 帘在罩前沿；max: 向后 +Y 缩回罩下，停在 organizer 上方不穿 hood_back | 无 | 同上 + targeted `+Y` 位移 |

- 所有活动件均为完整实体（前脸 + 底 + 双侧 + 后），无 facade-only、无腔内横条、无中央假导轨。
- **全模板零 `allow_overlap`**：抽屉/托盘/帘的滑出方向均开阔，无捕获式接触；若某姿态穿模，一律收行程或改几何，不加 allowance。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| support_family | enum | twin_pedestal/panel_pedestal/slab_panel_shelf/tubular_sled/four_leg_apron | panel_pedestal | choice | procedural sampler | Slot A |
| worktop_form | enum | rectangular_slab/l_shaped_return/roll_top_hood | rectangular_slab | conditional | roll_top⇒twin_pedestal；l_return⇒tubular_sled | Slot B |
| rows_per_bank | int | pedestal 族 [2,4]；four_leg_apron [1,2] | 4 / 1 | conditional | 上限随 support_family 变化（§8） | §8 |
| front_accessory | enum | keyboard_tray/none | none | conditional | 禁 four_leg_apron / roll_top_hood | Slot C |
| pull_style | enum | bail_pull/bar_pull/bow_pull/knob_rosette/u_pull | u_pull | choice | procedural sampler | Slot D |
| top_finish | enum | plain/leather_inset | plain | conditional | leather 仅 four_leg_apron / twin_pedestal | Slot E |
| palette_style | enum | antique_walnut/pale_ash/graphite_chrome/mahogany_leather/warm_walnut | warm_walnut | choice | procedural sampler | Slot F |
| width | float | [1.20, 1.50] | 1.30 | independent | clamp | 002 L49 1.50 / 005 L171 1.26 / 004 L98 1.38 |
| depth | float | [0.58, 0.70] | 0.62 | independent | clamp | 003 L71 0.62 / 004 L98 0.68 |
| worktop_height | float | [0.72, 0.78] | 0.75 | independent | clamp（顶板上表面 z） | 003 L330（0.74-0.80）/ 004 L92 0.766 |
| drawer_travel | float | [0.27, 0.34] | 0.30 | independent | clamp；`≤ box_depth − 0.07`（保留插入，004 meta L353） | 002 L276 0.30 / 004 L347 0.34 |
| pedestal_w | float | derived | — | equation | `= min(0.44, (width − knee_min)/n_ped − wall_margin)`（n_ped=1 或 2） | fork_n8 L30-L34 |
| knee_clear | float | derived | — | inequality | `width − Σ(bank 占位) ≥ 0.32`；违反时按比例收缩 pedestal_w | fork_n8 L416-L425（0.31-0.33）/ 005 L390-L399（0.68-0.695） |
| box_depth | float | derived | — | equation | `= depth − back_t − 0.05`（悬挂 pedestal 用 bank 深） | 005 L61（0.45 箱/0.54 bank） |
| return_w/return_d | float | derived | — | equation | `= 0.42×width / 0.84×depth`（L-return 翼，随主翼缩放） | fork_lret L78-L81（0.55/0.52 @1.35/0.62） |
| hood_h | float | derived | — | equation | `= 0.50×(worktop_height 比例)`（hood 顶 ≈ worktop+0.50） | 001 L31-L42（0.79→1.255） |
| (—) | constraint | — | — | inequality | `travel ≤ box_depth − 0.07`；tambour_travel ≤ hood 内可用 y − backing 长 | 001 L429-L441 |
| (—) | constraint | — | — | conditional | rows_per_bank 上限：pedestal 族 4、apron 族 2；小抽屉固定 2×3（仅 roll_top） | §8 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解（独立采样 → 派生 → 投影收缩 →
conditional 解析），不留到 builder 失败。

## 7.5 编译预算 / compile budget（必填）

**每-seed 预算 ≤ 15s**（依据：库内直箱家具 5–10s；本类主体为 Box carcass；最重 seed 为
roll_top（2 块 ExtrudeGeometry 颊板 + 14 抽屉全 Box/Cylinder）或 tubular_sled（3 条 spline
tube 管架））。分档 tessellation：spline tube samples_per_segment ≤14、radial ≤16（源 20 →
降）；bow pull radial ≤14 且同 geometry `.copy()` 复用（003 L280 语义）；Lathe 车削腿
segments ≤32（源 40 → 降）；拱 apron ≤24 段；hood 颊板 polyline ≤10 点。N 个同构抽屉的
front/box/pull 尺寸相同时复用同一 mesh/几何对象。超预算先降精度再迭代。sweep
`--compile-timeout 120`（看门狗 ≈8×）。

## 8. Multiplicity / Copy Logic

本小类有**一根主 multiplicity 轴：抽屉数量 N**（由 support_family 容量 gate + roll_top 附加
小抽屉 bank 组成）。

**Axis 1 — 抽屉数量 N（drawer count）**
- `count_param`: `rows_per_bank`（每 bank 行数）；N = rows_per_bank × n_banks (+6 小抽屉当
  roll_top)。
  - `twin_pedestal`：n_banks=2，rows∈[2,4] → N=4/6/8；+`roll_top_hood` 附加 2×3 小抽屉 →
    N=10/12/14（anchor N=14，001 = 8 主 + 6 小）。
  - `panel_pedestal` / `slab_panel_shelf` / `tubular_sled`：n_banks=1，rows∈[2,4] → N=2/3/4
    （anchor N=4：002/003/005 全部 4 屉）。
  - `four_leg_apron`：n_banks=2，rows∈[1,2] → N=2/4（anchors：N=2 fork_n2、N=4 004）。
- `N_range`（产品域）: **[2,14]**，anchors N=2/4/8/14；由 support family 容量 gate（四腿
  apron 桌不可能挂 14 屉；单 pedestal 不超 4）。
- sampling domain（权重档）：rows 小值偏多（pedestal 族 rows 2/3/4 ≈ 0.30/0.35/0.35；apron
  rows 1/2 ≈ 0.55/0.45）；roll_top（大 N 路径）由 worktop_form 采样加权 ~0.35（仅
  twin_pedestal 内）稀有化 N≥10 尾部。
- copied object: 一个抽屉 = front_panel(+edge band/molding) + 敞口盒（bottom+side_0/1+back）
  + moving rails（pedestal 屉）+ pull(s)，外加 frame 上专属 `mate_rail_{i}`（+ pedestal 族
  fixed_rail 对）与一条 PRISMATIC。
- naming: 主抽屉 `drawer_{bank}_{row}`（bank 0=右/单，1=左镜像；row 0=顶 → 底），apron 屉
  `drawer_{bank}_0/1`，小抽屉 `small_drawer_{bank}_{row}`；joint `frame_to_<part>`；
  小抽屉 joint `frame_to_small_drawer_{b}_{r}`。
- placement: pedestal 族沿 bank 内高 graduated rows（顶浅底深，005 L284-L289 语义）；apron
  屉在 bank 壳体内水平排；小抽屉 2 bank × 3 行 flanking 中央鸽笼（001 L399-L407）。
- joint policy: 恰好一条 PRISMATIC/屉，parent=desk_frame，axis=(0,-1,0)，lower=0，
  upper=travel（主屉 0.27–0.34；apron 屉 ≈0.34；小抽屉 0.155），damping/friction 参照
  005 L127（damping 6 friction 3），每屉 MatingContract + 全行程保留插入。
- source/gating: N 上限 14（仅 twin_pedestal+roll_top）；不做 N=0/1（无抽屉读作 dining
  table，跨类）；rows 上限按族 clamp。

**Axis 2 — roll_top 小抽屉 bank（固定 2×3，不独立采样）**：仅随 `roll_top_hood` 出现，
2 bank × 3 行固定（001 L399-L407），不暴露独立 count 参数 —— 记为主轴的 conditional 附加项。

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | support_family 5 种支撑拓扑（twin pedestal / panel+pedestal / panel+shelf+pedestal / tubular sled 悬挂柜 / four-leg apron），全部 source-backed（fork_n8+001 / 005 / 002 / 003 / 004+fork_n2）；可动 part 增减：keyboard_tray（002）、tambour+6 小抽屉（001）按 gate 出现。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：N∈{2,3,4,6,8,10,12,14}，anchors 2/4/8/14，rows 小值高频、N≥10 稀有（roll_top gate）。 |
| ② 关节类型 | 图不变，换 type/轴 | 有（同 type 多轴向/语义） | 全部 PRISMATIC（源池仅暴露滑动机构）：抽屉 axis (0,-1,0) 朝用户；keyboard_tray axis (0,-1,0)（002 L310-L324）；tambour axis **(0,+1,0)** 向后缩回罩下（001 L429-L441）。REVOLUTE 门扇被类别身份禁止（会变 door cabinet）。声明的每种（drawer/tray/tambour）都在 sweep 的 axis_realization 中出现。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | worktop_form 3 candidates：`rectangular_slab`（Planar Boundary，002/003/005）、`l_shaped_return`（Planar Boundary，fork_lret）、`roll_top_hood`（Volumetric Envelope，001）；登记进 slot_choices；曲面/异形用 ExtrudeGeometry/spline tube 实体（无 Box 降级）。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | pull_style 5（bail/bar/bow/knob/u，record_only，贴前脸最终面挂出）+ top_finish 2（plain/leather_inset：皮面 z 由顶板最终上表面派生、xy 内缩 footprint，边框条围合，004 L115-L155）+ 前脸 edge band/molding（005 L69-L74 / 004 L263-L289）。派生顺序 ③→⑤→④。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | width[1.20,1.50] / depth[0.58,0.70] / worktop_height[0.72,0.78] / drawer_travel[0.27,0.34]；graduated 前脸高（顶浅底深）。运动包络：每主/apron 屉 轴(0,-1,0)、开向 -Y、[0, travel≤box_depth−0.07]；小抽屉 [0,0.155]；tray 轴(0,-1,0) [0,≈0.25]；tambour 轴(0,+1,0) [0,≈0.18]（罩内 y 可用域投影）。motion_test_plan：`fail_if_parts_overlap_in_sampled_poses`（max_pose_samples=48，N≥10 时 32，ignore_fixed=True）+ 每屉/tray/tambour 各一条 targeted `ctx.pose({joint:upper})`（主屉 -Y 位移 ≥0.6×travel、tray -Y、tambour +Y）。抽屉朝开阔方向滑离本体，全程无新增穿模；无 sampled-pose exemption。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 wood(antique/laminate)/metal(chrome,brass,nickel,steel)/leather/rubber；配色 5：antique_walnut/pale_ash/graphite_chrome/mahogany_leather/warm_walnut（各 ≥6 键）。材质大类覆盖 ≥ ceil(0.5×5)=3（wood+metal+leather+rubber=4）。 |

**收尾自检**：batch 0-9 中 5 支撑家族与 3 worktop 形态肉眼拉得开；5 palette 出现；pull 贴前脸
不悬空；leather 皮面坐在顶板上表面；抽屉/tray/tambour 全行程不穿模；每 seed 膝部 bay 开放。

## 拓扑审计（topology audit）

- root parts: 恰好 1（desk_frame）。
- 每个可动件（drawer/tray/tambour）是 desk_frame 的直接 PRISMATIC 子 part，无二级链。
- 无 FIXED 关节（腿/管架/apron/modesty/organizer 均 desk_frame visuals）。
- 无浮空 part：抽屉经 front_panel⇄mate_rail 接触进入连通树；tray 经 runner⇄rail 接触；
  tambour 经 slat_backing⇄tambour_track 接触。
- worktop_form 只改 desk_frame visuals（+roll_top 附加 tambour/小抽屉子件）；抽屉盒恒矩形。
- N 变化只改抽屉 part 数与对应 mate_rail/fixed_rail/joint 数，拓扑保持"1 frame + N+K 并联
  prismatic 子件"。
- 每 seed 无任何名为/语义为 door 的 part 或 REVOLUTE 门扇；膝部 bay 内无落地遮挡（modesty
  为上部浅板）。

## 采样与覆盖审计

core theoretical：support_family(5) × worktop_form(3) × front_accessory(2) = 30（未 gate）
raw theoretical：30 × N 档 = 加入有界整数 N 后的完整配置规模（见 `## Combination Domain`）

实际合法组合域：由下方 `## Compatibility Gates` 的 deny 行、MatingContract、膝部 ≥0.32 m
不等式和 swept-clearance validator 定义。**不开放完整笛卡尔积。**

理由：主多样性来自离散 slot（① support_family + ③ worktop_form + ② accessory）+ N；
④ pull/top_finish 与 ⑥ palette 按 counting policy 不计入 core（只做覆盖）；连续 scale
（width/depth/height/travel）只做局部微调，同样不计入。

## Compatibility Gates

| # | deny 条件 | 理由 |
|---|---|---|
| G1 | `worktop_form=roll_top_hood` AND `support_family≠twin_pedestal` | roll-top 罩 + 14 屉容量只有 001（twin pedestal）这一个锚点；挂到单 pedestal/雪橇/四腿上没有承载与容量来源。 |
| G2 | `worktop_form=l_shaped_return` AND `support_family≠tubular_sled` | return 翼的支撑只有 fork_lret 的 return 雪橇管架这一个锚点（L178-L211）；其它家族需要发明 return 支撑 = 无来源。 |
| G3 | `front_accessory=keyboard_tray` AND `support_family=four_leg_apron` | 004 的拱形 apron 实体占据顶板下前沿（L203-L208，z 0.545-0.718），与托盘导轨物理冲突。 |
| G4 | `front_accessory=keyboard_tray` AND `worktop_form=roll_top_hood` | 唯一 roll-top 锚点 001 无托盘；两者组合是无锚点的 ② 外推，且落在最重 seed（14 屉 + tambour）上，编译预算与净空风险最高。 |
| G5 | `top_finish=leather_inset` AND `support_family∉{four_leg_apron, twin_pedestal}` | 皮面书写域只有 004/001 两个古董语言锚点；层压板/镀铬现代族贴皮面是无来源的身份混淆。 |
| G6 | `rows_per_bank > 4`（pedestal 族）/ `> 2`（apron 族） | 超出 bank 容量：pedestal 族 zone 高度只容 4 行 graduated 前脸；004 的 0.178 m 浅 apron 壳体只容 2 行。 |
| G7 | `knee_clear < 0.32 m` | 类别身份硬约束（开放膝部空间）；`resolve_config` 按比例收缩 pedestal_w，无法满足则拒绝。 |
| G8 | `drawer_travel > box_depth − 0.07` | 保留插入量（004 L353 `retained_insertion_m: 0.073`）；违反时投影回缩，不留到 builder 失败。 |
| G9 | `front_accessory=keyboard_tray` AND 发射 005 的 knee cross rails | **实现期发现（2026-07-16 sweep）**：005 L276-L282 的两条 knee 横撑与 002 L282-L309 的托盘占据膝部 bay 同一段顶板下空间（closed pose 实测穿模 16mm）。两个来源本身互斥——005（横撑锚点）无托盘，002（唯一托盘锚点）无横撑——故同时发射属无来源组合。有托盘时不发射 knee rails；modesty 板（真正连接 bay 的构件）恒发射。 |

全部 gate 在 `config_from_seed` 采样时即条件化（不会采到非法组合），并在 `resolve_config`
中二次校验 raise —— 非法组合**不进入 seed domain**，不靠 build 期失败兜底。

## Combination Domain

- diversity_profile / reason: `constrained` —— 诚实核心词汇受源池限制：5 个 origin 各贡献
  一个支撑家族（①）；③ 的两个非矩形形态各自只有一个 gate 住的支撑锚点；② 只有 tray/none。
- core axes / cartesian count / gate-filtered legal count:
  `support_family(5) × worktop_form(3) × front_accessory(2)` = **30 笛卡尔** →
  G1/G2/G3/G4 过滤后 **core_domain = 12**
  （合法 (support,worktop) 对 7 个：twin×rect、twin×roll、panel×rect、shelf×rect、
  sled×rect、sled×l_return、apron×rect；其中 twin×roll 与 apron×rect 禁 tray → 12）。
- multiplicity axes / admitted integers / reachable integers / min-mid-max boundaries:
  一根轴 `drawer_count`。admitted = 可达 = **{2,3,4,6,8,10,12,14}**；min=2（fork_n2 apron /
  单 pedestal 2 行）、mid=8（twin pedestal 4 行 ×2）、max=14（twin+roll_top：8 主 + 6 小，
  001 锚点）。observed anchors 2/4/8/14 全部可达。
- raw cartesian count / gate-filtered legal count: **raw_domain = 35**（12 个 core 组合各自
  按支撑家族容量展开其合法 N 档）。
- excluded: palette(5)、material、host-conformal decoration（pull_style 5 / top_finish 2）、
  continuous dimensions（width/depth/worktop_height/drawer_travel）。
- profile floor / recommended target / exception: constrained 硬下限 **16**；本类别诚实
  core = **12**，**低于下限 4**。**不申请靠假轴达标**——不把 palette(5)/pull(5)/finish(2)/N(8)
  乘进 core（那样会得到虚假的 ~5600）。此处登记为**诚实 shortfall，需要 domain-hash-bound
  人工例外**；若人工不批，唯一诚实的补法是上游为 `l_shaped_return` / `keyboard_tray` /
  第 3 个 ② 附加机构补 fork anchor，而不是修改计数口径。

## Visual Risk

- `drawer`（主风险）：N 最高 14 个并联 prismatic；每屉必须是完整敞口盒 + 双侧纵向导轨；
  全行程 −Y 滑出不得穿 bank wall / apron / 膝部结构。
- `hidden_slide`：keyboard_tray 与 tambour 的导轨在顶板下 / 罩内，闭合姿态肉眼不可见，
  必须在视觉 QA 用 mid/max 姿态与局部视图证明啮合。
- `multi_joint`：roll_top seed 有 15 条并联 prismatic（14 屉 + tambour），
  `max_pose_samples` 按 §8.5 ⑤ 降到 32 控预算。
- `curved_fit`：hood 颊板（ExtrudeGeometry polyline）与 tambour 直线化行程的贴合；
  001 用曲面侧轨、模板线性化，需目检帘不脱轨。
- 类别特有：**开放膝部空间**（≥0.32 m）与**无门**是身份线，任一 seed 违反即跨类到
  dresser / cabinet。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 先采
support_family（加权），再在其合法集内条件采样 worktop_form / rows_per_bank /
front_accessory / top_finish，再采 pull/palette 与连续 scale；`resolve_config` clamp + 派生
pedestal_w/box_depth/return/hood 尺寸 + 投影 travel/knee 可行域 + 解析 conditional rows 上限。
compatibility matrix：roll_top⇒twin_pedestal；l_return⇒tubular_sled；keyboard_tray 禁
four_leg_apron/roll_top；leather 仅 apron/twin。无 regression overrides（主 seed domain 全程
序化）。random sweep 0-35 初过（sweep-pipeline fast/final/corner），0-999 成熟审计；viewer
目检 batch 0-9。
Topology target：1000-seed slot 元组覆盖 report-only。
Controlled local parameterization：width / depth / worktop_height / drawer_travel（均
independent + clamp）；pedestal_w / box_depth / knee_clear / return_w / hood_h 按 equation/
inequality 派生（§7），不破坏 MatingContract / 支撑接触 / joint 轴 / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | support 加权 → 条件 worktop/rows/accessory/finish → pull/palette → 连续 scale | slot_choices_for_seed == build choices |
| compatibility matrix | roll_top⇒twin；l_return⇒sled；tray 禁 apron/roll_top；leather 仅 apron/twin；rows clamp 按族 | 无 floating/collision/axis/超 N 失败 |
| controlled local variation | width/depth/height/travel clamp + knee/travel 投影 | 比例变化不破坏接口/膝部空间/joint 轴/类别身份 |
| regression overrides | none | — |
| random sweep | 0-35 初过（pipeline），0-999 成熟审计 | failure clusters；axis_realization（5 支撑/3 worktop/rows/accessory 全部实现）；viewer 0-9 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_family ① | 5 | yes | yes | |
| worktop_form ③ | 3 | yes | yes | 形态主导 slot，gated |
| drawer multiplicity (rows/N) | N∈{2..14} 8 档 | yes | yes | 主 multiplicity 轴 |
| front_accessory ② | 2 | yes | no | 样本池只含 tray/none 两种附加机构（002 唯一 tray 源），已说明 |
| pull_style ④ | 5 | yes | yes | record_only |
| top_finish ④ | 2 | yes | no | 样本池只含素面/皮面两种顶面处理，已说明 |
| palette ⑥ | 5 | yes | yes | |

## Validator

- slot_choices_for_seed 返回已实现 module 名（support_family/worktop_form/drawer_count/
  front_accessory/pull_style/top_finish/palette_style）
- config_from_seed 对所有普通 seed 用程序化采样（含 seed 0）
- compatibility gating 阻止非法组合（roll_top⇔twin、l_return⇔sled、tray/leather gate、rows clamp）
- 无 regression overrides
- 连续 scale 依赖（equation/inequality/conditional）在 resolve_config 求解
- 每个可动件存在 MatingContract（drawer front_panel⇄mate_rail；tray runner⇄rail；tambour
  backing⇄track）
- 每条抽屉 joint 是 PRISMATIC，axis=(0,-1,0)，lower=0，upper∈[0.15,0.34]；tambour axis=(0,+1,0)
- copied drawers 遵循命名/放置策略；graduated 前脸高顶浅底深
- 车削腿 Lathe / 管架 spline tube / 拱 apron & hood 颊板 & L 顶 ExtrudeGeometry（无 Box 降级）
- 每 seed 膝部空间 ≥0.32 m 且至少 1 屉、无 door

## Reject cases

- 出现 REVOLUTE 门扇 / door part（跨类 → cabinet）
- 膝部 bay 被落地板/塔体封死（读作 dresser/cabinet，非 desk）
- N=0 或无 PRISMATIC 抽屉（读作 dining table）
- worktop 倾斜（读作 drafting table）
- 任一抽屉缺 front_panel / bottom / side_0/1 / back（不是真实敞口盒）
- 抽屉 joint 非 PRISMATIC 或轴不是 (0,-1,0) 或 lower≠0；tambour 开向错误（-Y 会撞 organizer）
- 车削腿/管架/拱 apron/hood 颊板被 Box 降级
- four_leg_apron 挂 >4 屉或 pedestal 族 >4 行（超容量）
- MatingContract 缺失或贴合面间隙 >3mm；closed/sampled pose 穿模
- pull 悬空脱离前脸；leather 皮面浮出/陷入顶板

## 与相邻类别的边界

- 不该混入：Cabinet_with_drawers / dresser —— 全宽抽屉塔无膝部空间；本类恒有 ≥0.32 m 开放膝部 bay。
- 不该混入：Cabinet_with_doors / sideboard —— 出现 REVOLUTE 门扇；本类只有 prismatic 滑动件。
- 不该混入：dining table —— 无抽屉；本类每 seed ≥2 屉。
- 不该混入：drafting table —— 可倾/倾斜桌面；本类 worktop 恒水平。

## Authoring 自检记录
| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| self-check notes | ② 轴：源池仅含滑动机构（drawer/tray/tambour 三种 prismatic 语义、两种轴向），REVOLUTE 被类别身份排除，按 source map Blocked/Excluded 记录。front_accessory/top_finish 各 2 candidates：源池分别只有 002（tray）与 004+001（leather）一种附加结构/顶面处理，已按"样本池不足降到 2"说明。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | twin_pedestal | fork_n8 (+001) | fork_n8 L20-L34,L207-L316 | 镜像 bank 循环 + knee rails + modesty |
| S2 | A | panel_pedestal | 005 | L190-L304 | 端板 + 单 pedestal + spacers + knee rails |
| S3 | A | slab_panel_shelf | 002 | L65-L186 | 端板 + 搁架 bay + cubby pedestal + 钢 rail + 脚垫 |
| S4 | A | tubular_sled | 003 | L96-L225 | spline tube 雪橇框 + tie rails + 悬挂柜 + brackets |
| S5 | A | four_leg_apron | 004 (+fork_n2) | 004 L24-L53,L157-L236；fork_n2 L186-L199,L239-L243 | Lathe 腿 + 拱 apron + bank 壳体 + N=2/4 |
| S6 | B | rectangular_slab | 002/003/005 | 003 L69-L94 | Box 顶板 + 边带 |
| S7 | B | l_shaped_return | fork_lret | L72-L131,L178-L229 | L 顶轮廓 + return 管架 + 周界边带 |
| S8 | B | roll_top_hood | 001 | L30-L49,L320-L378,L409-L441 | 颊板 profile + hood + organizer + tambour + 小抽屉 bank |
| S9 | C | keyboard_tray | 002 | L163-L175,L282-L324 | tray rails + tray part + joint |
| S10 | — | pedestal drawer | 005 (+fork_n8) | 005 L21-L134 | front/box/moving rails/joint |
| S11 | — | apron drawer | 004 (+fork_n2) | 004 L246-L354 | molding 前脸 + wood runner + joint |
| S12 | — | small drawer | 001 | L152-L216 | 小屉 + knob + joint |
| S13 | D | pulls | 001/002/003/004/005 | 001 L61-L83；002 L241-L253；003 L227-L242；004 L317-L334；005 L96-L112 | 5 pull 家族 |
| S14 | E | leather_inset | 004 (+001) | 004 L115-L155；001 L307-L314 | 皮面 + 边框 + 角 pin |
| S15 | F | palettes | 001-005 | 001 L232-L237；002 L31-L38；003 L59-L65；004 L79-L85；005 L153-L158 | 5 配色 |

## 模板实现备注（可选）

- pedestal 屉 / apron 屉 / 小抽屉共享一个 `_build_drawer_part` 分派 helper（kind 参数），
  front/box 尺寸由 DrawerSpec 单源派生（Contract 3c）。
- MatingContract 全部法向贴合（Y/X/Z 各一族）；无 captured-pin，不需要 allow_overlap
  （抽屉滑出方向开阔）。若 tambour 与 hood_back 在上限接近，收 travel 而非加 allowance。
- `mate_rail_{i}` 的 -Y 面即 bank 前平面；抽屉 joint origin y = 该平面，front_panel 背面
  local y=0（贴合 0 间隙）。
- l_shaped_return / roll_top_hood 组合暂只与其 gate 的支撑家族进 seed domain（无其它组合）。
- 001 的侧 X 交叉撑（L283-L304）与 hood 曲线 trim（L339-L359）作为 twin_pedestal(antique
  palette)/roll_top 的 host visuals 装饰采纳；002 的 modesty grain 条（L139-L146）随
  slab_panel_shelf。
- **实现期修正记录（2026-07-16）**，三项，均在 sweep 中实测确认：
  1. **G9 knee rails ⇄ keyboard_tray 互斥**（见 `## Compatibility Gates`）。
  2. **抽屉/托盘导轨用 1mm 嵌入式 running fit**：`fail_if_isolated_parts` 的
     `contact_tol=1e-06` 要求真实接触，0.5mm 间隙会让 tray 被判为 isolated part；
     1mm 嵌入远低于 `overlap_tol=0.005`，既保证支撑连通又不触发穿模门。
     （005 L87-L93 / L294-L304 本身即"两轨恰好贴合"的语义。）
  3. **leather 角 pin 坐进皮面**：004 L147-L155 的 pin 在源中悬于皮面边缘外 1mm；
     本模板把 pin 内移到 `±(width/2 − 0.090)` 并压入皮面上表面 1.5mm，
     消除 disconnected-island（Rule 4 宿主派生）。
- **来源保真自检**：车削腿保持 `LatheGeometry`（segments 40→32 降精度，非降级）；
  雪橇管/return 管/bow pull 保持 `tube_from_spline_points`（radial 20→16、
  samples 14→12，仅降精度）；拱 apron / hood 颊板 / L 顶保持 `ExtrudeGeometry`
  实体拉伸（fork_lret 的 cadquery union 与同一 L 多边形拉伸等价）。全模板
  `allow_overlap` 数量 = 0。
