# Paper Cutter Guillotine Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `paper_cutter_guillotine` |
| template path | `agent/templates/paper_cutter_guillotine.py` |
| test path (optional) | `tests/agent/test_paper_cutter_guillotine_template.py` — 可选回归网，默认被 pytest 排除；验收以 compile-sweep 为准 |
| stage | `APPROVED` |
| status | `APPROVED` |
| __modular__ | `True` |
| pattern | `mixed`（身份链 base→blade_arm 单 REVOLUTE + 并列 gated children + 可选 FIXED 中间件） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | 13 个 5 星全部用 grep 抽取了 `model.part(...)` 列表 / 每个 articulation(name,type,parent,child,axis,limit) / 几何 primitive 与 base 上的 ornament visual；其中 10 个按行精读以采纳可复用源码块（97d04、002e25、5013、a4d9236、e1d730、c6d987、02609、0001、0003、5a20、9f7cbe、0002、9feb69 — 实际全部精读到 part/joint 层） |
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 2 |
| source_index_policy | 仅索引被采纳的可复用片段；pivot 机构"嵌入 base 的 visual clevis"与"独立 FIXED pivot_bracket part"视为同一身份铰链的 `pivot_mount` 离散开关，不当成两套模板；finger_guard / hold_down / lock_handle / side_gauge 这些第二自由度统统视为 gated 可选件，不并入默认 1-blade 主干；base 上的 grid/ruler/fence/cutting-strip 一律 ornament visual，不拆 FIXED 装饰 part |

全部 13 个 5 星样本清单（record_id → 采纳判定）：

| record_id | parts | 主关节 + gated 件 | 判定 |
|---|---|---|---|
| `rec_paper_cutter_guillotine_002e25c9f7e247b68f3843ceec0b6cfd` | bed, cutter_arm | 1 REVOLUTE(arm_hinge) | adopted → S1（最简 2-part primitive base + 对角 yaw arm 锚点） |
| `rec_paper_cutter_guillotine_0002` | cutting_base, cutter_arm | 1 REVOLUTE | adopted → S2（baked hinge_pin visual + allow_overlap captured-pin + 对角 arm helper） |
| `rec_paper_cutter_guillotine_e1d730ecc5f24a189d0698dee8791f6f` | base, blade_arm | 1 REVOLUTE(pivot) | adopted → S3（baked clevis pivot：pad+2 cheek+bridge+pin_cap+pivot_pin visual） |
| `rec_paper_cutter_guillotine_0001` | base, guide_fence, cutting_arm | 1 FIXED(fence) + 1 REVOLUTE | adopted → S4（mesh ExtrudeGeometry base panel + 独立 FIXED guide_fence part + arm-beam mesh + finger_guard 作 arm visual） |
| `rec_paper_cutter_guillotine_0003` | base, side_fence, pivot_bracket, blade_arm | 2 FIXED + 1 REVOLUTE | adopted → S5（独立 FIXED side_fence + 独立 FIXED pivot_bracket(含 bracket_axle) + section_loft arm beam） |
| `rec_paper_cutter_guillotine_a4d9236c07dc45a1a245ac338963f4cd` | base, gauge_rail, side_gauge, pivot_bracket, blade_arm, finger_guard | 2 FIXED + 1 PRISMATIC + 2 REVOLUTE | adopted → S6（最稠密：FIXED gauge_rail→PRISMATIC side_gauge 链、FIXED pivot_bracket→REVOLUTE blade_arm 链、REVOLUTE finger_guard） |
| `rec_paper_cutter_guillotine_c6d987b526654fbc8c5208ef3c751793` | bed, blade_arm, hold_down | 1 REVOLUTE + 1 PRISMATIC(+Z) | adopted → S7（cadquery filleted bed board + hold_down 垂直夹紧件，slider 骑在 base-visual guide post 上） |
| `rec_paper_cutter_guillotine_5a20a7a198b34301ad11483a773e8669` | base, blade_arm, hold_down_bar | 1 REVOLUTE + 1 PRISMATIC(−Z) | adopted → S8（对角 cut_angle 派生 + hold_down_bar 含 slider sleeve 骑在 base-visual guide rod 上 + 多 pose QC） |
| `rec_paper_cutter_guillotine_9f7cbe262ec6467ca354e31c5b5dac60` | base, blade_arm, lock_handle | 1 REVOLUTE + 1 REVOLUTE(lock,±Z) | adopted → S9（侧置 hinge block + 旋转 lock_handle 安全锁：shaft+round_handle+pointer 骑在 lock_boss visual 上） |
| `rec_paper_cutter_guillotine_97d04cd4bddf4792a7b32ebe333cbec8` | base, blade_arm, lock_handle | 1 REVOLUTE + 1 REVOLUTE(lock,±X) | adopted → S10（ExtrudeGeometry arm panel + lock_handle 锁轮 shaft/hub/lock_wheel/lock_grip 骑在 lock_mount visual 上） |
| `rec_paper_cutter_guillotine_5013e3868075412f8ab5e6c40ad608fc` | bed, blade_arm, finger_guard | 1 REVOLUTE + 1 REVOLUTE(guard,±X) | adopted → S11（cadquery sloped blade + 透明 polycarbonate finger_guard 含 clip_loop，骑在 base-visual guard_hinge_knuckle 上） |
| `rec_paper_cutter_guillotine_02609e0d173548e3a9fb42c2c26560d0` | base, blade_arm, side_gauge, finger_guard | 1 REVOLUTE + 1 PRISMATIC + 1 REVOLUTE | adopted → S12（side_gauge 直接骑在 base-visual gauge_rail 上 PRISMATIC + finger_guard 骑在 base-visual guard_hinge_rod 上 REVOLUTE） |
| `rec_paper_cutter_guillotine_9feb69f5c0e846eab26b86bee3c89345` | base, blade_arm, finger_guard | 1 REVOLUTE + 1 REVOLUTE(guard) | read but not adopted as a *distinct* source；其 finger_guard（eyelet-clip 骑 base-visual guard_rod，对角 CUT_YAW）拓扑与 S11/S12 同族，结构特征已被 S11/S12 覆盖，仅作交叉验证 finger_guard 在 base-visual rail 上摆动的拓扑稳定性 |

（说明：read but not adopted = 2 个 = 9feb69 + 计入 0001 的 finger_guard-as-visual 形态并入 S4，不另立源；其余 11 个均直接被某 slot 候选采纳。）

## 核心身份
台式裁纸闸刀（guillotine paper cutter）：一块落地的平板 `base`（承载 cutting bed/mat、印刷网格与刻度尺、纸张定位 fence、cutting strip/anvil 砧条，以及后角的 pivot 支座几何），加一根绕**单个 REVOLUTE 后角铰链**上下摆动的 `blade_arm`（长闸刀刃 + 上脊 + 末端握把），刀刃落下时贴着砧条把纸切断。身份恒为 base + blade_arm + 恰好一个把刀臂连到 base 的 REVOLUTE，轴水平（沿切割对角线方向，典型 `(0,-1,0)` / `(±1,0,0)`），行程 0 → ~70-92°，wow 点与唯一必需自由度就是这把"砍"下来的刀臂。可选 gated 第二件：压纸 hold-down 横杆（PRISMATIC 垂直夹紧）、安全 finger_guard（绕切割线轴 REVOLUTE 上翻的透明护板）、旋转 lock_handle（锁刀的安全旋钮）、side_gauge 侧向纸张定位尺（沿 rail PRISMATIC 平移）。

边界：
- 不是 rotary/circular trimmer（滚刀沿导轨滑动）—— 本类刀刃靠 REVOLUTE 绕固定铰链"砍"，不靠 PRISMATIC 滑切；side_gauge 的 PRISMATIC 只是定位尺，不是切割主自由度。
- 不是通用 `single_revolute_hinge`（铰链五金）—— 本类的固定半永远是带 cutting bed / fence / 刻度的裁纸台 base，moving 半是带刃的长刀臂，且常带第二把 gated 自由度。
- 不是 `lever_press` / `stapler`（往下压的杠杆压头）—— 本类的"动"件是带刃刀臂沿砧条切，不是平头压块。
- base 上的 grid/ruler/rear fence/cutting strip/rubber feet/hinge cheek 都是不动装饰，按 Rule 1 必须 `base.visual(...)`，不拆 FIXED 装饰 part。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_paper_cutter_guillotine_002e25c9f7e247b68f3843ceec0b6cfd` | `data/records/rec_paper_cutter_guillotine_002e25c9f7e247b68f3843ceec0b6cfd/revisions/rev_000001/model.py:L29-L108` | `_hinge_world` 对角 yaw 锚点 helper + primitive Box base（bed/rear_fence/front_lip/cutting_strip/measure_mark/grid_line/hinge_cheek/hinge_foot 全 visual） |
| S2 | `rec_paper_cutter_guillotine_0002` | `data/records/rec_paper_cutter_guillotine_0002/revisions/rev_000001/model.py:L36-L130` | `_arm_offset`/`_arm_point` 对角 arm 坐标 helper + baked `hinge_pin` Cylinder visual + clevis hinge_cheek_left/right；`L252-L298` allow_overlap(hinge_pin,hinge_barrel) captured-pin 写法 |
| S3 | `rec_paper_cutter_guillotine_e1d730ecc5f24a189d0698dee8791f6f` | `data/records/rec_paper_cutter_guillotine_e1d730ecc5f24a189d0698dee8791f6f/revisions/rev_000001/model.py:L97-L188` | baked clevis pivot：pivot_pad+rear_cheek+front_cheek+bracket_bridge+pin_cap×2+pivot_pin 全是 base visual，blade_arm 含 hub，pivot REVOLUTE `(0,-1,0)` 90° |
| S4 | `rec_paper_cutter_guillotine_0001` | `data/records/rec_paper_cutter_guillotine_0001/revisions/rev_000001/model.py:L45-L75,L91-L147` | `ExtrudeGeometry.from_z0(rounded_rect_profile)` base panel mesh + `ExtrudeGeometry.centered` arm-beam mesh helper + `L149-L178,L230-L236` 独立 FIXED `guide_fence` part(rear_fence_bar+lip+squaring_stop+knob) |
| S5 | `rec_paper_cutter_guillotine_0003` | `data/records/rec_paper_cutter_guillotine_0003/revisions/rev_000001/model.py:L88-L105,L107-L142` | 独立 FIXED `side_fence` part + 独立 FIXED `pivot_bracket` part(seat+backbone+cheek_inner/outer+`bracket_axle` Cylinder)；`L144-L194` `section_loft` lofted-mesh arm beam；`L196-L223` `base→fence`/`base→bracket` FIXED + `bracket→arm` REVOLUTE |
| S6 | `rec_paper_cutter_guillotine_a4d9236c07dc45a1a245ac338963f4cd` | `data/records/rec_paper_cutter_guillotine_a4d9236c07dc45a1a245ac338963f4cd/revisions/rev_000001/model.py:L88-L143,L145-L180` | FIXED `gauge_rail` part(rail_bar+cap+stop) + PRISMATIC `side_gauge` part(carriage+fence+brace+thumb_knob) 的滑动子装配 + 独立 `pivot_bracket`；`L262-L302` 两 FIXED + PRISMATIC + 2 REVOLUTE 关节群 |
| S7 | `rec_paper_cutter_guillotine_c6d987b526654fbc8c5208ef3c751793` | `data/records/rec_paper_cutter_guillotine_c6d987b526654fbc8c5208ef3c751793/revisions/rev_000001/model.py:L35-L43,L121-L135,L176-L214` | `_rounded_board` cadquery filleted bed + base-visual `guide_post` 导柱 + `hold_down` part(clamp_bar+slider_block+cap) PRISMATIC `(0,0,1)` 垂直夹紧 |
| S8 | `rec_paper_cutter_guillotine_5a20a7a198b34301ad11483a773e8669` | `data/records/rec_paper_cutter_guillotine_5a20a7a198b34301ad11483a773e8669/revisions/rev_000001/model.py:L39-L64,L125-L141,L185-L252` | 对角 `cut_angle`/`offset_from_hinge` 派生 helper + base-visual `guide_rod` + `hold_down_bar` part(slider_sleeve×2+clamp_bar+clamp_pad+bar_handle) PRISMATIC `(0,0,-1)` |
| S9 | `rec_paper_cutter_guillotine_9f7cbe262ec6467ca354e31c5b5dac60` | `data/records/rec_paper_cutter_guillotine_9f7cbe262ec6467ca354e31c5b5dac60/revisions/rev_000001/model.py:L104-L144,L185-L222` | base-visual `lock_boss` + `lock_handle` part(lock_shaft+round_handle+lock_pointer) REVOLUTE `(0,0,1)` 旋转安全锁 + 侧置 hinge block |
| S10 | `rec_paper_cutter_guillotine_97d04cd4bddf4792a7b32ebe333cbec8` | `data/records/rec_paper_cutter_guillotine_97d04cd4bddf4792a7b32ebe333cbec8/revisions/rev_000001/model.py:L33-L117,L176-L246` | `ExtrudeGeometry(rounded_rect_profile)` table_top + base-visual `lock_mount` + `lock_handle` part(shaft+hub+lock_wheel+lock_grip) REVOLUTE `(1,0,0)` 锁轮 + ExtrudeGeometry arm panel |
| S11 | `rec_paper_cutter_guillotine_5013e3868075412f8ab5e6c40ad608fc` | `data/records/rec_paper_cutter_guillotine_5013e3868075412f8ab5e6c40ad608fc/revisions/rev_000001/model.py:L103-L118,L120-L163,L165-L203` | base-visual `guard_hinge_stand`/`guard_hinge_knuckle` + 透明 polycarbonate `finger_guard` part(clear_panel+clip_loop×3+clip_tab) REVOLUTE `(1,0,0)` + cadquery sloped blade |
| S12 | `rec_paper_cutter_guillotine_02609e0d173548e3a9fb42c2c26560d0` | `data/records/rec_paper_cutter_guillotine_02609e0d173548e3a9fb42c2c26560d0/revisions/rev_000001/model.py:L50-L111,L151-L217` | base-visual `gauge_rail`/`gauge_rail_base` + `side_gauge` part(saddle_top+side×2+gauge_fence) PRISMATIC `(1,0,0)` 直接骑 base rail；base-visual `guard_hinge_rod` + `finger_guard` part REVOLUTE `(1,0,0)` |

## 槽位 + 候选模块表

### Slot 1：base（裁纸台底座，root part）
落地的平板裁纸台。承载 cutting bed/mat、印刷网格刻度、rear/side fence、cutting strip 砧条、rubber feet——这些全是 ornament visual（Rule 1），不拆 part。是 root，blade_arm 与所有 gated 件最终都接地于它。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `prim_box_bed` | S1 (002e25) | `model.py:L51-L108` | eligible if compatible | 纯 Box 拼接：bed 板 + rear_fence + front_lip + cutting_strip + 5+5 条 measure_mark/grid_line + hinge_cheek×2 + hinge_foot 全 visual，最稳健 |
| `mesh_rrect_bed` | S4 / S10 (0001 / 97d04) | `0001:L45-L53,L91-L147` / `97d04:L33-L117` | eligible if compatible | `ExtrudeGeometry.from_z0(rounded_rect_profile)` 或 `ExtrudeGeometry(rounded_rect_profile)` 圆角台面 mesh + cutting_mat + ruler strip + 印刷标记 + 角铰几何 |
| `cadquery_fillet_bed` | S7 (c6d987) | `model.py:L35-L43,L58-L97` | eligible if compatible | cadquery `box.edges(" | Z").fillet` 软角 bed board + cut_strip + rear/side fence + 印刷 grid_tick/ruler_tick visual |
| `plinth_plus_plate_bed` | S8 / S12 (5a20 / 02609) | `5a20:L66-L99` / `02609:L31-L62` | eligible if compatible | 双层：dark plinth Box + 上 bed_plate + 对角 cut_line_strip + front scale + 印刷 mat，重型办公量级 |

### Slot 2：blade_arm（闸刀臂，主 REVOLUTE child）
绕后角铰链上下摆动的长刀臂：根部 hub/barrel/eyelet + arm spine/beam + 刃条（sharp_edge/blade_strip）+ 末端握把。是身份的 wow 件。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `prim_box_arm` | S1 / S3 (002e25 / e1d730) | `002e25:L110-L152` / `e1d730:L141-L178` | eligible if compatible | hinge_barrel/hub Cylinder + blade_plate Box + sharp_edge Box + upper_spine + grip Cylinder，全 primitive，最稳健 |
| `extrude_profile_arm` | S4 / S10 (0001 / 97d04) | `0001:L56-L75,L180-L223` / `97d04:L120-L174` | eligible if compatible | `ExtrudeGeometry`/`ExtrudeGeometry.centered` 雕出锥形 arm beam/panel + steel blade backing + handle grip + end cap，工业感外形 |
| `cadquery_sloped_arm` | S11 (5013) | `model.py:L120-L163` | eligible if compatible | cadquery `Workplane.polyline().close().extrude()` 斜刃 + red arm_bar + pivot_hub + front_grip，斜面刃 |
| `lofted_eyelet_arm` | S5 / S9feb (0003 / 9feb69) | `0003:L144-L194` / `9feb69:L210-L267` | eligible if compatible | `section_loft`/`_eyelet_mesh` 派生锥形 arm beam + pivot eyelet/sleeve + blade_edge + handle grip，对角 yaw 锚定 |

### Slot 3：pivot_mount（后角铰链支座拓扑）
刀臂铰链的承力支座如何表达 + part 数（是否独立 pivot_bracket part）。decide blade_arm 的 parent 是 base 还是独立 bracket。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `baked_clevis_in_base` | S3 / S12 (e1d730 / 02609) | `e1d730:L103-L139` / `02609:L63-L92` | eligible if compatible | pivot pad + 两 cheek + bridge + pin_cap + pivot_pin 全是 **base 的 visual**，blade_arm 直接 `base→blade_arm` REVOLUTE，captured-pin 用 allow_overlap |
| `baked_pin_in_base` | S2 (0002) | `model.py:L86-L130` | eligible if compatible | hinge_block + hinge_cap + hinge_cheek_left/right + 一根 `hinge_pin` Cylinder 全 base visual，blade_arm hinge_barrel 抱住销，`base→blade_arm` REVOLUTE |
| `separate_pivot_bracket` | S5 / S6 (0003 / a4d9236) | `0003:L107-L142,L203-L223` / `a4d9236:L145-L180,L278-L293` | eligible if compatible | 独立 FIXED `pivot_bracket` part(seat/backbone/cheek×2 + `bracket_axle` Cylinder)，`base→pivot_bracket` FIXED + `pivot_bracket→blade_arm` REVOLUTE，多一个 part |

说明：`baked_clevis_in_base` 与 `baked_pin_in_base` 都是"销/支座嵌进 base visual、2-part 主干"，但前者是双 cheek + 外露 pin cap 的开放 clevis、后者是 block+cap 半包式带独立 pin 视觉，part 树相同(2)但 base 上 hinge-hardware visual 子树明确不同；`separate_pivot_bracket` 是唯一引入第 3 个 part 并把 blade_arm 改 parent 的拓扑分支。三者结构上分明。

### Slot 4：second_dof（gated 第二自由度 / 可选件）
裁纸台常见的第二把动作件。`none` 为默认主干（只有刀臂）；其余各引入恰好一个额外 part + 一个额外关节。每个候选都把自己的承力 visual（guide post/rod、rail、lock boss、guard knuckle）嵌进 base，按 Rule 2 真锚定。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | S1 / S3 (002e25 / e1d730) | `002e25:L154-L162` / `e1d730:L180-L188` | eligible if compatible | 无第二件，只有 base + blade_arm + 1 REVOLUTE（占 5 星多数：5/13 纯 2-part） |
| `hold_down_bar_prismatic` | S7 / S8 (c6d987 / 5a20) | `c6d987:L176-L214` / `5a20:L185-L252` | eligible if compatible | 独立 `hold_down`/`hold_down_bar` part(clamp_bar+slider sleeve/block+pad)，PRISMATIC 垂直夹紧 `(0,0,±1)`，slider 骑 base-visual guide post/rod |
| `finger_guard_revolute` | S11 / S12 (5013 / 02609) | `5013:L165-L203,L195-L203` / `02609:L177-L189,L209-L217` | eligible if compatible | 独立透明 `finger_guard` part(clear panel + clip loop/frame)，绕切割线轴 REVOLUTE `(±1,0,0)` 上翻，骑 base-visual guard knuckle/rod |
| `lock_handle_revolute` | S9 / S10 (9f7cbe / 97d04) | `9f7cbe:L185-L222` / `97d04:L176-L246` | eligible if compatible | 独立 `lock_handle` part(shaft + round_handle/lock_wheel + pointer/grip)，旋转安全锁 REVOLUTE `(0,0,1)`/`(1,0,0)`，骑 base-visual lock boss/mount |
| `side_gauge_prismatic` | S6 / S12 (a4d9236 / 02609) | `a4d9236:L114-L143,L269-L277` / `02609:L151-L175,L200-L208` | eligible if compatible | 独立 `side_gauge` part(carriage/saddle + fence + thumb knob)，沿 rail PRISMATIC `(1,0,0)` 平移定位纸张；rail 可是 base-visual(02609) 或独立 FIXED `gauge_rail` part(a4d9236) |

## 槽位图（slot graph）
```
pattern = mixed
（身份链 base → blade_arm（单 REVOLUTE）+ 并列 gated 第二件 + 可选 FIXED 中间件）

                         base (Slot1: prim_box / mesh_rrect / cadquery / plinth)
                           │
        ┌──────────────────┼───────────────────────────┬───────────────────────┐
        │ REVOLUTE          │ (pivot_mount=separate)    │ Slot4 second_dof      │ (FIXED, gated)
        │ (rear-corner      │ FIXED                     │ gated child           │
        │  hinge, axis      ▼                           ▼                       ▼
        │  对角水平向)    [pivot_bracket part]      [second_dof part]      [gauge_rail part]
        │                   │ REVOLUTE                  │                  (仅 side_gauge 用独立 rail 时)
        ▼                   ▼                           │ PRISMATIC / REVOLUTE
   blade_arm (Slot2) ◄──────┘                           ▼
   （baked pivot 时 parent=base；                  hold_down_bar / finger_guard /
     separate 时 parent=pivot_bracket）             lock_handle / side_gauge
```
- 身份链恒为 `base -> blade_arm`（exactly one REVOLUTE，轴水平沿切割对角线）。
- Slot3=`separate_pivot_bracket` 时插入一个 FIXED `pivot_bracket` 中间件，blade_arm 改 parent 为它（chain：base→bracket→arm）；否则 pivot 嵌 base，blade_arm 直接 parent=base。
- Slot4≠`none` 时并列引入一个 gated 第二 part + 第二关节（hold_down/side_gauge=PRISMATIC，finger_guard/lock_handle=REVOLUTE）。
- Slot4=`side_gauge_prismatic` 且 rail 取独立件时，再多一个 FIXED `gauge_rail` 中间件（base→rail→side_gauge 链）。

## 部件（Parts）
### Slot1 / base
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `base` / `bed` / `cutting_base` | ~10-30 | bed/mat 面 + rear/side fence + cutting_strip 砧条 + grid/ruler 印刷标记 + rubber feet + 后角 pivot hardware visual，全 ornament 不拆 part；落地 root | S1/S4/S7/S8/S10/S12 |

### Slot2 / blade_arm
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `blade_arm` / `cutter_arm` / `cutting_arm` | ~5-9 | hub/barrel/eyelet 根 + arm spine/beam（Box 或 Extrude/loft/cadquery mesh）+ blade/sharp edge 刃条 + handle grip/end cap | S1/S3/S4/S5/S10/S11 |

### Slot3 / pivot_mount
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `pivot_bracket`（仅 separate） | ~4-6 | 独立 FIXED 支座：mount pad/seat + cheek×2 + bridge/backbone + `bracket_axle` Cylinder，承 blade_arm 铰链 | S5/S6 |
| （baked 时无独立 part） | — | clevis cheek + pin_cap + pivot_pin 作为 base.visual | S3/S2/S12 |

### Slot4 / second_dof（gated，每种引入一个 part）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `hold_down` / `hold_down_bar` | ~4-5 | clamp_bar + rubber pad + slider sleeve/block×2 + handle，PRISMATIC 垂直夹纸 | S7/S8 |
| `finger_guard` | ~5-7 | 透明 clear panel + frame top/bottom + clip loop/eyelet×2-3，REVOLUTE 上翻护刃 | S11/S12 |
| `lock_handle` | ~3-4 | shaft + round_handle/lock_wheel + pointer/grip，旋转安全锁 | S9/S10 |
| `side_gauge` | ~4 | carriage/saddle + 立 fence + brace + thumb knob，沿 rail PRISMATIC 定位纸张 | S6/S12 |
| `gauge_rail`（仅 side_gauge 用独立 rail） | ~3-4 | rail bar + cap + 两端 stop，FIXED 到 base，承 side_gauge 滑动 | S6 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `base_to_blade_arm` / `pivot` / `blade_hinge` / `arm_hinge` | revolute | base 或 pivot_bracket(Slot3) | blade_arm | 水平：`(0,-1,0)` / `(-1,0,0)` / `(1,0,0)`（沿切割对角线法向） | `[0.0, ~1.15..1.6]` rad（72°–92°） | 主关节：刀臂绕后角铰链上下砍；axis 与 cut line 几何一致 | S1/S2/S3/S5/S6/S8 |
| `base_to_pivot_bracket` / `base_to_bracket` | fixed | base | pivot_bracket | n/a | n/a | 仅 Slot3=`separate_pivot_bracket`：独立支座固定到 base | S5/S6 |
| `base_to_hold_down(_bar)` / `hold_down_slide` | prismatic (gated) | base | hold_down(_bar) | `(0,0,1)` 或 `(0,0,-1)` | `[0.0, ~0.010..0.036]` m | 仅 Slot4=`hold_down_bar_prismatic`：压纸杆垂直夹紧（短行程） | S7/S8 |
| `base_to_finger_guard` / `guard_hinge` | revolute (gated) | base | finger_guard | `(1,0,0)` / `(0,1,0)` / `(-1,0,0)`（沿切割线轴） | `[0.0, ~1.15..1.9]` rad | 仅 Slot4=`finger_guard_revolute`：透明护刃绕切割线上翻 | S11/S12 |
| `base_to_lock_handle` / `lock` | revolute (gated) | base | lock_handle | `(0,0,1)` 或 `(1,0,0)` | `[0.0, π/2]` 或 `[-70°,+70°]` | 仅 Slot4=`lock_handle_revolute`：旋转安全锁 | S9/S10 |
| `gauge_slide` / `rail_to_side_gauge` / `base_to_side_gauge` | prismatic (gated) | base 或 gauge_rail | side_gauge | `(1,0,0)` | `[0.0, ~0.16..0.44]` m | 仅 Slot4=`side_gauge_prismatic`：侧纸尺沿 rail 平移 | S6/S12 |
| `base_to_gauge_rail` | fixed (gated) | base | gauge_rail | n/a | n/a | 仅 side_gauge 用独立 rail：rail 固定到 base | S6 |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `base_style` | enum | `prim_box_bed` / `mesh_rrect_bed` / `cadquery_fillet_bed` / `plinth_plus_plate_bed` | `prim_box_bed` | drives Slot1 台面构造 | S1/S4/S7/S8 |
| `arm_style` | enum | `prim_box_arm` / `extrude_profile_arm` / `cadquery_sloped_arm` / `lofted_eyelet_arm` | `prim_box_arm` | drives Slot2 刀臂构造 | S1/S4/S11/S5 |
| `pivot_mount` | enum | `baked_clevis_in_base` / `baked_pin_in_base` / `separate_pivot_bracket` | `baked_clevis_in_base` | drives Slot3：是否独立 pivot_bracket part、blade_arm parent | S3/S2/S5 |
| `second_dof` | enum | `none` / `hold_down_bar_prismatic` / `finger_guard_revolute` / `lock_handle_revolute` / `side_gauge_prismatic` | `none` | drives Slot4：是否多一个 gated part + 关节 | S1/S7/S11/S9/S6 |
| `arm_axis` | enum | `neg_y=(0,-1,0)` / `neg_x=(-1,0,0)` / `pos_x=(1,0,0)` | `neg_y` | blade_hinge.axis；与切割对角线一致 | S1/S9/S2 |
| `cut_yaw` | float | `-0.75 .. 0.0` rad（对角切割角）或 0（正交） | sampled | arm/cutting_strip 沿对角线旋转量；helper 派生 arm 坐标 | S1/S2/S8/9feb69 |
| `base_x` (bed length) | float | `0.38 - 0.82` | sampled | 台面长边 | S2/S1/S9 |
| `base_y` (bed depth) | float | `0.27 - 0.48` | sampled | 台面短边 | S2/S1/S6 |
| `base_thickness` | float | `0.014 - 0.055` | sampled | 台板厚（plinth 时含双层） | S2/S9 |
| `arm_length` | float | `0.39 - 0.74` | derived≈`base_x` 量级 | 刀臂长 = 台面长 + 握把外伸 | S1/S3/S10 |
| `pivot_z` | float | `0.077 - 0.176` | sampled | 铰链高（baked vs bracket vs 重型 column 不同） | S3/S2/S9 |
| `blade_upper` | float | `1.15 - 1.61` rad（66°–92°；实测开角幅值全距）| `1.25` | 刀臂开角幅值（正向 `[0,upper]` 或负向 `[-upper,0]`，见 a4d923）| 全样本 |
| `guard_upper` | float | `1.15 - 1.9` rad | `1.6` | finger_guard 上翻上限（仅 gated） | S11/9feb69 |
| `hold_down_travel` | float | `0.010 - 0.036` m | `0.018` | 压纸杆行程（仅 gated，短） | S7/S8 |
| `side_gauge_travel` | float | `0.16 - 0.44` m | `0.20` | 侧纸尺行程（仅 gated） | S6/S12 |
| `lock_range` | enum/float | `[0,π/2]` / `[-70°,70°]` | `[0,π/2]` | 锁旋钮行程（仅 gated） | S9/S10 |
| `palette` | enum | board/steel/blade/grip/mat/red/clear 等材质组 | sampled | 颜色/材质，不计入拓扑 | 全样本 |

## Multiplicity / Copy Logic

- 无模板级复制数量逻辑：核心结构由固定 named slots 和 gated module-local fixed copies 表达，不暴露全局 `*_count` 作为主拓扑采样轴。
- 若某个 module source 内部包含固定成对、环形阵列或若干重复 visual/part，模板实现应把它保留为 module-local construction，并使用稳定命名；不得把未审核的可变复制数量加入 seed domain。
- 未来若要把固定重复结构升级为可变 multiplicity，必须补充来源、N_range、placement、joint policy、regression seeds 和 reviewer 审核记录。

## 拓扑多样性审计

总组合数（笛卡尔积，未加相容约束）：
Slot1 base_style(4) × Slot2 arm_style(4) × Slot3 pivot_mount(3) × Slot4 second_dof(5) = **240**。


理由：只看会改变 part 数 / joint 数 / joint 拓扑的结构骨架（base/arm 的构造 enum 不改拓扑，仅换 mesh/primitive，不计入）：
- Slot3 `pivot_mount`：`separate_pivot_bracket` 引入一个额外 FIXED part（part 数 +1，多一个 FIXED joint 且 blade_arm 改 parent）；两个 baked 变体则维持 2-part 主干 → **2 个结构骨架**（baked / separate）。
- Slot4 `second_dof`：5 个取值 → `none`(纯 2-part) / `hold_down`(+1 part,+1 PRISMATIC) / `finger_guard`(+1 part,+1 REVOLUTE) / `lock_handle`(+1 part,+1 REVOLUTE,轴族不同) / `side_gauge`(+1 part,+1 PRISMATIC,且可再 +1 FIXED gauge_rail part) → **5+ 个结构骨架**。
- Slot3 × Slot4 = 2 × 5 = **10 种 part/joint-拓扑骨架**（part 数从 2 到 5、关节数从 1 到 3、含/不含第二 REVOLUTE/PRISMATIC），达到 10 distinct 最低门槛。叠加 4 base_style × 4 arm_style 的几何换装后离散组合达 240。

每槽位候选数：
| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---|---|---|
| Slot1 base | 4 | yes | |
| Slot2 blade_arm | 4 | yes | |
| Slot3 pivot_mount | 3 | yes | baked_clevis / baked_pin / separate_bracket 三结构家族 |
| Slot4 second_dof | 5 | yes | 含 `none` 默认 + 4 种 gated 件，每种结构骨架不同 |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
- identity：存在 base + blade_arm；存在恰好一个把 blade_arm 连到 base（或 pivot_bracket）的 REVOLUTE 主关节。
- primary joint：blade_hinge 是 REVOLUTE，axis 水平（判 `axis.z≈0`，**含 cut_yaw 对角偏转**——如 0002 的 `(-0.56,-0.83,0)`，勿写死成离散集 `{(0,-1,0),(±1,0,0)}`，否则与本模板自带的 `cut_yaw` 参数自相矛盾、会误拒对角刀）；开角幅值 `|upper-lower|∈[1.1, 1.65]`（正向开 `lower≈0`，或负向开 `upper≈0`——如 a4d923 的 `[-1.2, 0]`，按幅值判不写死符号）；不是 PRISMATIC/CONTINUOUS。
- pivot mount：`separate_pivot_bracket` 时存在 FIXED `base→pivot_bracket` 且 blade_arm parent=pivot_bracket；否则 blade_arm parent=base 且 pivot hardware 是 base.visual。
- captured pin：pivot_pin/bracket_axle 与 blade_arm 的 hub/barrel/eyelet/sleeve coaxial 穿过，用 `allow_overlap(...)` 声明 press-fit（S2/S3/S5 写法）。
- blade closes：closed pose blade 刃条在 XY 投影覆盖 cutting_strip（min_overlap≥0.25），且刃条贴 cutting strip（small gap 0.0005–0.008，无穿模）。
- blade opens：开到 upper 时 blade/handle AABB 顶 Z 显著抬升（>0.2m），刃离开砧条（gap≥0.04）。
- cut line：blade 沿对角线横跨台面（blade_dx > base_x×0.6），axis 与 cut_yaw 几何一致。
- second_dof（gated）：`hold_down` 为 PRISMATIC 垂直、行程短（0.008–0.036m），lowered pose 几乎贴 bed；`finger_guard` REVOLUTE 绕切割线轴上翻；`lock_handle` REVOLUTE 旋转；`side_gauge` PRISMATIC 沿 rail 横移，saddle 始终骑 rail。
- grounding & no floating：base 落地；blade_arm、pivot_bracket、所有 gated part 全部 attached/FIXED；hinge cheek/pin/guide post/rail/lock boss/grid/fence 全是 base.visual 或 FIXED，无悬空件。

## Reject cases（必须能识别并拒绝）
- 缺 blade_arm（只有平板台），或刀臂被做成 PRISMATIC 滑切 / FIXED 不动（那是 trimmer / 静态摆件，不是闸刀）。
- blade_hinge 轴竖直（`(0,0,1)`）或不在后角铰线上，刀臂绕错误中心摆动 / 侧开。
- blade 闭合却不贴 cutting strip（悬半空 / 投影不重叠 / 穿透台面），或开到 upper 仍压在台面上。
- `separate_pivot_bracket` 声称独立支座却把 blade_arm 直接 parent=base（或反之），bracket/arm parent 关系自相矛盾；或 pivot_bracket 悬空不 FIXED 到 base。
- pivot_pin/bracket_axle 比 hub bore 还粗导致非 press-fit 穿模却没 allow_overlap 声明，或 pin 漂浮不与 base/bracket 接触。
- gated 第二件几何不连贯（hold_down slider 不骑 guide post、side_gauge saddle 不骑 rail、finger_guard 不绕 base knuckle）→ 砍掉该件退回纯 blade_arm 主干，不强塞悬空件。
- 把 rear fence / grid / ruler / cutting strip 拆成 FIXED 装饰 part（违 Rule 1）而非 base.visual。
- 同时强加 2 个以上 gated 第二自由度堆砌（应一次只 gate 一件），或把 side_gauge 的 PRISMATIC 当成"切割主自由度"冒充闸刀。

## 与相邻类别的边界
- vs `rotary_paper_trimmer`（滚刀裁纸器）：本类刀刃靠单 REVOLUTE 绕后角铰链"砍"；滚刀沿导轨 PRISMATIC 滑切是另一类，不混入。
- vs `single_revolute_hinge`（铰链五金）：本类固定半永远是带 cutting bed/fence/刻度的裁纸台 base、moving 半是带刃长刀臂，且常带 gated 第二件；纯两 hinge half 出界。
- vs `lever_press` / `stapler`（杠杆压头）：本类动件是带刃刀臂沿砧条切纸，不是平头压块往下压；若是压头机构出界。
- vs `desk_lamp_arm` / `serial_elbow_arm`（多串联 revolute 臂）：本类只有一个把刀臂连到 base 的 REVOLUTE，无 reach-derived 多节连杆链；side_gauge/finger_guard/hold_down 都是并列 gated 件，不是串联第二关节。
- 同类内 baked vs separate pivot：baked = 销/支座嵌进 base visual（2-part 主干）；separate = 独立 FIXED pivot_bracket（3-part），用 `pivot_mount` gate，不把 bracket 几何塞进 baked 默认分支。

## 模板实现备注（可选）
- `_arm_offset`/`_hinge_world`/`offset_from_hinge`（S1/S2/S8）这类"对角 cut_yaw 锚点 helper"是把 arm 坐标从 hinge-local 旋到 world 的共享工具，blade_arm 与所有沿对角线的 cutting_strip/finger_guard 都复用。
- captured-pin 重叠（pivot_pin↔hub、bracket_axle↔sleeve）预期需要 `ctx.allow_overlap(...)` 声明（S2 `L264-L270`、S3 `L198-L204`、S5 `L246-L252` 是写法范本）。
- `separate_pivot_bracket` 与 `base_to_gauge_rail` 是仅有的两个合法 FIXED articulation（独立 sub-assembly 各需自己的参考系，Rule 1 例外），实现时上方需 docstring 说明为何不用 visual fuse。
- base 上所有 grid/ruler/fence/cutting strip/feet/hinge hardware 必须是 `base.visual(..., name=...)`，绝不可拆 FIXED 装饰 part（Rule 1 核心约束）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending（待人工审核）|
| reviewer notes | SPEC_ONLY_DRAFT；13 个 5 星全 grep + 13 个精读到 part/joint 层（10+ 行级精读）；身份恒为 base + blade_arm + 1 REVOLUTE 后角铰链，无 no-arm 变体；second_dof 5 候选含默认 `none`，每种 gated 件结构骨架不同；pivot_mount 区分 baked(2-part) vs separate bracket(3-part)；待人工 review |
