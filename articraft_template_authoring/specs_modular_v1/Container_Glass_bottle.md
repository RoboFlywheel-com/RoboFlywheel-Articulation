# Container / Glass bottle (glass beverage / wine / oil / dropper vessel) — Modular Spec

> 来源小类：`picture/Container/Glass bottle`（articraft_data 上游 Container/Glass bottle fork-variant pool；source map：`picture_expansion/template_source_maps/Container__Glass_bottle.md`）。
> 全量读取：1 个 parent（dark-glass beer bottle，crown cap）+ 12 个 `rec_container_glass_bottle_var_*` 变体，**逐一读 `revisions/rev_000001/model.py` 全文**（≥5 个样本，门槛满足）。
> 引用 `model.py:Lx-Ly` 来自 arti-template `data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`_bottle_solid` / `_profile_loft` / `_flask_loft` / `_revolve_profile` / `_cap_mesh` / `_screw_cap_mesh` / `_neck_threads_mesh` / `_collar_mesh` / `_bail_mesh` / `_cork_mesh` / `_pipette_tube` / `_spout_solid` / `_flip_cap_solid` / `bottle_to_cap` / `bottle_to_stopper` / `bottle_to_cork` / `bottle_to_dropper` / `bottle_to_flip_cap` / `bottle_to_marble` 等），行号仅作定位（fork 变体源码长度相近，行号或随重编微移）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_glass_bottle` |
| template path | `agent/templates/Container_Glass_bottle.py` |
| test path (optional) | `tests/agent/test_container_glass_bottle_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots：bottle_body_profile + closure_mechanism；closure 的活动件 / 固定密封件挂到 bottle 共同 parent（root），无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13（1 parent + 12 单轴 fork 变体，均 converged / retained 5★）|
| read_count | 13（全部 model.py 全文逐一读取）|
| read_scope | all 5-star samples in this category（无抽样；每个 closure 变体 joint 拓扑 / part tree 各异，逐一读取）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14（本类 13 个样本全部被采纳为 module 来源，无落选）|

冗余/分流说明：
- **parent（dark-glass beer bottle）同时是 body 基线 `long_neck` 与 closure 基线 `pry_off_crown_cap` 的来源**：`_bottle_solid`（长颈啤酒瓶轮廓 lathe）+ `_cap_mesh`（皇冠压盖）+ `bottle_to_cap` PRISMATIC +Z（pop-off）。
- body 6 个变体（wine / stubby / boston / hip_flask / decanter / slim_flute）都只改 `_bottle_solid` 的轮廓 sections、**保持 parent 的 crown cap + PRISMATIC pop-off 机构不变**——它们是纯 body-profile fork，归入 `bottle_body_profile` 槽，不另列为 closure candidate。
- closure 6 个变体（screw_cap / swing_top / cork / dropper_pipette / pour_spout / codd_marble）都**保持 parent 的 long_neck body 不变（codd_marble 仅在颈内多挖 pinch chamber bore）**，只换瓶口封口机构 + joint 拓扑——它们是纯 closure fork，归入 `closure_mechanism` 槽，不另列为 body candidate。
- 两轴正交：每个变体只动一轴、另一轴保持 parent 基线 → 干净的二轴笛卡尔积（见 §9）。

## 核心身份

一只直立中空**玻璃瓶**（glass beverage / wine / oil / 药剂 vessel）：中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。瓶身由 CadQuery `loft` / `revolve`（旋转体 lathe）发射为**厚壁中空玻璃 shell**（真实开口腔体，口部开 bore），材质为**半透明玻璃（rgba alpha < 1）**——这是 Glass bottle 的核心身份标记（区别于不透明塑料瓶）。瓶身轮廓家族：高瘦长颈啤酒瓶（直筒身 + 斜肩 + 细长颈 + 外翻唇口）/ 葡萄酒瓶（高直筒身 + 高圆肩急收 + 短直颈 + 凹底 punt）/ 矮胖 steinie（粗矮身 + 缓圆肩 + 极短颈）/ 波士顿圆瓶（圆肩连续过渡入短窄颈 + 珠唇口，药/油瓶形）/ 扁酒壶 hip_flask（**非圆截面** D/肾形 loft，一面凸一面凹）/ 宽肩 decanter/carafe（矮宽球腹 + 极宽斜肩急收 + 长细颈）/ 高瘦 flute（连续平滑收入颈无肩部断口）。

瓶口上方一只封口机构按某种动作开合（**唯一活动语义**，每候选 ≥1 non-fixed joint）：皇冠压盖（PRISMATIC +Z pop-off，crimp 齿裙）/ 螺纹旋盖（CONTINUOUS +Z 旋，knurled 盖 + neck thread rings）/ 摆杆翻塞 swing-top（REVOLUTE +Y，铰接 wire bail + ceramic plug + rubber gasket，绕颈 collar 摆起）/ 软木塞 cork（PRISMATIC +Z 直拔，锥塞坐 bore + grip head 露唇）/ 滴管 dropper（PRISMATIC +Z 直拔，cap collar + 细玻璃 pipette tube 伸入瓶膛 + 顶部 squeeze bulb）/ 倒酒嘴翻盖 pour_spout（固定锥形 spout insert + REVOLUTE +X flip_cap 绕后铰掀开）/ Codd 玻璃珠塞（PRISMATIC -Z 下压，颈内 captive marble 抵 rubber ring 密封、下压进 pinch chamber 开启）。

默认成熟域：单瓶身 + 单封口（无嵌套 / 无 multiplicity / 无提把）。

不该混入：通用塑料瓶 / 运动水瓶 / 挤压瓶（`container_bottle`，不透明塑料 + 翻盖吸管 / 泵头 / 挤压机构，是更广的塑料封口家族）；精华 / 美容滴管小瓶（`container_bottle_serum`，小尺寸化妆滴管瓶）；宽口储物 / 化妆罐（`container_jar`，口径≈瓶身、螺旋大盖 / 后铰翻盖，无细长颈）；敞口无盖杯 / 马克杯（`cup`，无可闭口）；带提把 jug / growler、双口连体瓶（出 Glass bottle 类目）。

## 槽位 + 候选模块表

> **建模注记**：`bottle_body_profile` 是 root `bottle` part 的 mesh 属性（一次 `_bottle_solid()` lathe/loft 发射半透明玻璃 shell，含开口 bore），不是独立串联 slot。`closure_mechanism` 各候选把活动封口件（+ 必要的固定 neck 硬件 visual）挂到 `bottle`（parallel children）。两轴笛卡尔积构成拓扑多样性（见 §9）。closure 各候选互斥（一次只一种封口）。

### Slot A：bottle_body_profile（瓶身轮廓家族 / 足迹——root `bottle` 的玻璃 shell mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| long_neck（基线）| rec_dark-glass-beer-bottle-with-a-crimped-metal-crow_…_2a24ec81 | `_profile_loft` L43-L55 / `_bottle_solid` L58-L98 / `bottle` part + `bottle_glass` visual L169-L174 | eligible if compatible | 高瘦长颈啤酒瓶：圆截面 loft（直筒身 + 斜肩 + 细长颈 + 外翻 rolled lip），厚壁开口 shell（outer.cut(inner)），LIP_TOP_Z≈0.230 |
| wine_bottle | rec_container_glass_bottle_var_wine_bottle | `_profile_loft` L50-L65 / `_bottle_solid` L68-L132（高圆肩急收 + 短直颈 + 球 punt cut）| eligible if compatible | 葡萄酒瓶：高直筒身 → 高圆肩急收 → 短直颈；底部 `punt_sphere` cut 出凹底 punt（L102-L108），较粗 body（~0.075 m φ）|
| stubby_steinie | rec_container_glass_bottle_var_stubby_steinie | `_profile_loft` L45-L57 / `_bottle_solid` L60-L110（粗矮身 + 缓圆肩 + 极短颈）| eligible if compatible | 矮胖 steinie：宽 body（~0.080 m φ）+ 缓圆肩 + 极短 stubby 颈，h<0.18 低高宽比，圆截面 loft |
| boston_round | rec_container_glass_bottle_var_boston_round | `_profile_loft` L48-L60 / `_rounded_shoulder_sections` L63-L78（cosine 圆肩）/ `_bottle_solid` L81-L… | eligible if compatible | 波士顿圆瓶：直筒身 → cosine 平滑圆肩连续过渡入短窄颈 → 小 bead lip（药/油瓶形），圆截面 loft + 程序化圆肩 helper |
| hip_flask | rec_container_glass_bottle_var_hip_flask | `_flask_profile_pts` L56-L79（D/肾形截面点）/ `_flask_loft` L82-L99 / `_bottle_solid` L102-L143 | eligible if compatible | **扁酒壶：非圆截面** —— `_flask_loft` 用多边形点 loft D/肾形截面（+Y 凸面、-Y 凹面，`circle_blend` 在 body→neck 渐变到圆），扁宽身（dx>1.6·dy）+ 短窄颈，**唯一非旋转对称 body** |
| decanter_carafe | rec_container_glass_bottle_var_decanter_carafe | `_profile_loft` L49-L61 / `_carafe_solid` L64-L… | eligible if compatible | 宽肩醒酒/卡拉夫瓶：矮宽球腹（max φ~0.11 m）+ 极宽斜肩急收 + 长细颈，圆截面 loft（注意 helper 名 `_carafe_solid` 而非 `_bottle_solid`）|
| slim_flute | rec_container_glass_bottle_var_slim_flute | `_revolve_profile` L43-L62 / `_flute_outer_profile` L65-L89 / `_flute_inner_profile` L92-L… | eligible if compatible | 高瘦笛形：极高极窄（h~0.30 m，max φ~0.054 m），瓶身连续平滑收入颈无肩部断口（莱茵/阿尔萨斯 flute）；**用 `revolve` 而非 loft** 发射圆截面 lathe（拓扑等价，primitive 不同）|

硬约束记录：bottle_body_profile 7 candidate（超 3-6 目标）。除 hip_flask（非圆 D/肾截面，`_flask_loft`）外全部圆截面 lathe（loft 或 revolve），共享「厚壁开口玻璃 shell = outer.cut(inner) + 半透明 glass material」的 body 契约，只换 footprint / 高宽比 / 肩部回收 / punt 有无 / 截面形状。hip_flask 的非圆截面是真实结构差异（不同 loft helper + 非旋转对称 AABB），保留为独立 candidate。

### Slot B：closure_mechanism（**主开合机构槽**——瓶口封口动作 / 唯一活动关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| pry_off_crown_cap（基线）| rec_dark-glass-beer-bottle-with-a-crimped-metal-crow_…_2a24ec81 | `_cap_mesh` L101-L158（穹顶 + 21 crimp 齿裙 inline 循环）/ `crown_cap` part L183-L184 / `bottle_to_cap` PRISMATIC +Z L194-L202 | eligible if compatible | 皇冠压盖：单 `bottle_to_cap` PRISMATIC +Z（origin 在 lip top `(0,0,LIP_TOP_Z)`），盖 skirt crimp 罩 over lip，q=0 坐下 / 正 q 直起 pop-off；1 活动件、1 joint |
| screw_cap | rec_container_glass_bottle_var_screw_cap | `_screw_cap_mesh` L163-L201（knurled star 外壳 + 内 thread rings）/ `_neck_threads_mesh` L149-L160（neck 外 thread rings，挂 bottle visual）/ `_thread_ring` L121-L129 / `bottle_to_cap` **CONTINUOUS** +Z L248-L256 | eligible if compatible | 螺纹旋盖：`bottle_to_cap` CONTINUOUS +Z（origin lip top），knurled 圆筒盖绕轴旋转就位；bottle 上多 `neck_threads` 固定 visual，`expect_contact` 守 thread 啮合；1 活动件、1 joint（旋转无平移）|
| swing_top | rec_container_glass_bottle_var_swing_top | `_collar_mesh` L138-L171（neck collar + pivot ears，挂 bottle visual）/ `_bail_mesh` L174-L228（wire bail，`_rod` L113-L135）/ `_plug_mesh` L231-L266 / `_gasket_mesh` L269-L278 / `bottle_to_stopper` **REVOLUTE** +Y L327-L337 | eligible if compatible | 扣压翻塞 swing-top：`bottle_to_stopper` REVOLUTE +Y（origin PIVOT_Z≈0.210 颈上 collar），`stopper` part 含 3 visual（bail_wire + plug_ceramic + plug_gasket），绕铰摆起离口；bottle 上多 `neck_collar` 固定 visual；captured pivot fit（bail 销插 collar ear）|
| cork | rec_container_glass_bottle_var_cork | `_cork_mesh` L101-L171（锥塞 + tip sphere + grip head + grain 凹槽）/ `cork_stopper` part L196-L197 / `bottle_to_cork` PRISMATIC +Z L207-L215 | eligible if compatible | 锥形软木塞：`bottle_to_cork` PRISMATIC +Z（origin lip top，upper≈0.05 长行程），锥塞坐 bore 内（z-overlap≥0.010）+ grip head 露唇上方，正 q 直拔出口；1 活动件、1 joint |
| dropper_pipette | rec_container_glass_bottle_var_dropper_pipette | `_cap_collar` L119-L169 / `_pipette_tube` L172-L210（`LatheGeometry.from_shell_profiles`）/ `_squeeze_bulb` L213-L252 / `dropper_cap` part（3 visual）L278-L300 / `bottle_to_dropper` PRISMATIC +Z L310-L320 | eligible if compatible | 滴管/吸管盖：`bottle_to_dropper` PRISMATIC +Z（origin lip top，upper≈0.13 极长行程），`dropper_cap` part 含 3 visual（cap_collar + 长 pipette_tube 伸入瓶膛 + 顶部 squeeze_bulb），整组沿轴直拔；pipette 在 bore 内（XY within）|
| pour_spout | rec_container_glass_bottle_var_pour_spout | `_spout_solid` L129-L179（锥形导流嘴 insert，**挂 bottle 固定 visual** origin lip top L243-L248）/ `_flip_cap_solid` L182-L225 / `flip_cap` part L256-L261 / `bottle_to_flip_cap` **REVOLUTE** +X L272-L282 | eligible if compatible | 倒酒嘴翻盖：固定锥形 `pour_spout` insert 坐瓶口（bottle 的 fixed visual，非活动件）+ `flip_cap` 活动件绕后铰 `bottle_to_flip_cap` REVOLUTE +X（origin HINGE_Y/HINGE_Z 在 spout 后顶）掀开露 spout channel；1 活动件、1 joint，封口件分裂成「固定 spout + 活动 flip_cap」|
| codd_marble | rec_container_glass_bottle_var_codd_marble | `_bottle_solid` L72-L128（颈内多挖 pinch ring + marble chamber bore）/ `marble` part（`Sphere`）L168-L177 / `rubber_ring`（`TorusGeometry`）固定 visual L148-L159 / `bottle_to_marble` PRISMATIC **-Z** L186-L196 | eligible if compatible | Codd 玻璃珠塞：颈内 captive `marble`（Sphere），`bottle_to_marble` PRISMATIC -Z（origin marble_seat_z 唇下），q=0 抵 `rubber_ring`（lip 内固定 torus visual）密封、正 q 下压进 pinch chamber 开启；bottle 颈 bore 改出 pinch 缩口 + chamber；`allow_isolated_part`（marble 颈内囚禁）|

硬约束记录：closure_mechanism 7 candidate（超 3-6 目标）。joint 拓扑覆盖：PRISMATIC +Z（crown pop-off / cork pull / dropper extract）、CONTINUOUS +Z（screw spin）、REVOLUTE +Y（swing-top）、REVOLUTE +X（pour-spout flip）、PRISMATIC -Z（codd marble push-down）。每个 candidate **≥1 non-fixed joint**。part count / visual count 各异：crown / cork = 1 part 1 visual；screw = 1 part + bottle neck_threads 固定 visual；swing = 1 part 3 visual + bottle neck_collar 固定 visual；dropper = 1 part 3 visual（LatheGeometry tube）；pour = 1 活动 part + bottle 固定 spout visual；codd = 1 Sphere part + bottle rubber_ring 固定 visual + 改 neck bore。

## 槽位图（slot graph）

pattern: parallel_children（`bottle` 为 root，坐地 z=0；closure 活动件 / 固定硬件挂到它；无 multiplicity）

```
bottle(bottle_body_profile)  [ROOT, 半透明玻璃 shell, 坐地 z=0]
   │  (+ closure 派生的固定 neck 硬件 visual 挂 bottle: screw=neck_threads / swing=neck_collar
   │     / pour=pour_spout insert / codd=rubber_ring + 改 neck bore)
   │
   ├── closure = pry_off_crown_cap:
   │     bottle --[bottle_to_cap: PRISMATIC +Z @ (0,0,LIP_TOP_Z)]--> crown_cap
   │
   ├── closure = screw_cap:
   │     bottle(+neck_threads visual) --[bottle_to_cap: CONTINUOUS +Z @ lip top]--> screw_cap
   │
   ├── closure = swing_top:
   │     bottle(+neck_collar visual) --[bottle_to_stopper: REVOLUTE +Y @ (0,0,PIVOT_Z)]--> stopper(bail+plug+gasket)
   │
   ├── closure = cork:
   │     bottle --[bottle_to_cork: PRISMATIC +Z @ lip top]--> cork_stopper
   │
   ├── closure = dropper_pipette:
   │     bottle --[bottle_to_dropper: PRISMATIC +Z @ lip top]--> dropper_cap(collar+pipette_tube+bulb)
   │
   ├── closure = pour_spout:
   │     bottle(+pour_spout insert 固定 visual @ lip top)
   │            --[bottle_to_flip_cap: REVOLUTE +X @ (0,HINGE_Y,HINGE_Z) spout 后顶]--> flip_cap
   │
   └── closure = codd_marble:
         bottle(+rubber_ring 固定 visual @ lip; neck bore 挖 pinch+chamber)
                --[bottle_to_marble: PRISMATIC -Z @ (0,0,marble_seat_z)]--> marble(Sphere, captive)
```

接口点位与 joint 语义：
- **顶口直动接口（crown / cork / dropper）**：joint origin 落在 lip top 中心 `(0,0,LIP_TOP_Z)`，axis +Z，PRISMATIC。q=0 封口件坐位（cap skirt 罩 lip / cork 锥塞坐 bore / dropper collar 罩 lip & pipette 伸 bore），正 q 直起/直拔。行程 upper 各异（crown/cork 0.03–0.05、dropper 0.13）。
- **螺纹接口（screw）**：origin lip top，axis +Z，CONTINUOUS（旋转无平移）；bottle neck 上 `neck_threads` 与 cap 内 thread rings 交错啮合，`expect_contact(screw_cap, neck_threads)` 守啮合面 + `expect_within(xy)` 守同轴。
- **摆杆铰接口（swing_top）**：`bottle_to_stopper` origin 在颈上 `(0,0,PIVOT_Z≈0.210)`，axis +Y，REVOLUTE（q=0 plug 坐 lip、gasket 接触 rim；正 q ~2.8 rad 摆开，plug 侧移并降到 lip 下）；bottle `neck_collar` ear 与 bail pin captured pivot fit。
- **翻盖铰接口（pour_spout）**：固定 `pour_spout` insert 是 bottle 的 visual（plug 坐 bore + flange 坐 lip + 锥 tube + 后 rib），`flip_cap` 经 `bottle_to_flip_cap` REVOLUTE +X（origin `(0, HINGE_Y, HINGE_Z)` 在 spout 后顶 barrel 处）；q=0 cap 罩 spout 口（xy-overlap + z 近接触），正 q ~1.5–2.3 rad 后翻露 channel。
- **珠塞直动接口（codd_marble）**：`bottle_to_marble` origin marble_seat_z（lip 下一个 marble 半径），axis **-Z**，PRISMATIC（q=0 marble 抵 lip 内 `rubber_ring` torus 密封；正 q ~0.025 下压进 chamber 开启）；marble 始终 XY-within 颈、Z-overlap 颈（不逃逸），由 neck bore 的 pinch 缩口囚禁。
- **mating policy（grandfather captured-fit）**：所有封口件与 bottle 的接触都是故意 captured / 友配过盈（cap skirt 罩 lip、cork 锥塞过盈坐 bore、dropper pipette 穿 bore、screw thread 交错、swing plug/gasket 压 rim、bail pin 插 collar ear、flip_cap 罩 spout、marble 囚 chamber），**非两刚体对接面 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 lip / neck pivot / spout 后顶 / marble seat 硬件）+ element-scoped `allow_overlap` 守 overlap（见各样本 run_tests 的 `ctx.allow_overlap`；codd 另加 `ctx.allow_isolated_part(marble)`）。
- **rest pose**：所有封口件 q=0 闭合 / 坐封（crown/screw/cork/dropper 坐口、swing plug 坐 lip、flip_cap 罩 spout、marble 抵 ring）。开口（pop-off / 旋离 / 拔出 / 摆起 / 翻开 / 下压）为 viewer 目检的活动语义。
- **互斥 / 可选**：closure 各候选互斥（一次只一种封口机构 + 其对应固定 neck 硬件 visual）。无可选空机构槽（封口是 Glass bottle 的类别身份，每瓶必有一个封口）。

## 每槽位 Module Emits / Interfaces

### Slot A / bottle（bottle_body_profile，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottle`（visual: `bottle_glass` 半透明 lathe shell[ + closure 派生固定 neck 硬件 visual]）| parent `_bottle_solid` L58-L98 / `bottle` part L169-L174 |
| internal joints | 无（root 瓶身本身无活动件）| — |
| upstream interface | 坐地 z=0（root）；半透明 glass material（alpha<1）| parent GLASS_RGBA L14 |
| downstream interface | lip top 中心 `(0,0,LIP_TOP_Z)`（顶口直动 / 旋 / 翻盖 joint 的 parent 接口）；颈上 PIVOT_Z（swing 铰）；marble_seat_z（codd） | parent LIP_TOP_Z L34 / swing PIVOT_Z L46 / codd marble_seat_z L185 |

### Slot B / closure_mechanism（每候选发射对应活动封口件 + 必要固定 neck 硬件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crown_cap` / `screw_cap` / `stopper`(bail+plug+gasket) / `cork_stopper` / `dropper_cap`(collar+pipette+bulb) / `flip_cap`(+bottle 固定 `pour_spout`) / `marble`(Sphere, +bottle 固定 `rubber_ring`) | 各 closure 源（见 §4 / §14）|
| internal joints | `bottle_to_cap` PRISMATIC +Z（crown）/ `bottle_to_cap` CONTINUOUS +Z（screw）/ `bottle_to_stopper` REVOLUTE +Y（swing）/ `bottle_to_cork` PRISMATIC +Z（cork）/ `bottle_to_dropper` PRISMATIC +Z（dropper）/ `bottle_to_flip_cap` REVOLUTE +X（pour）/ `bottle_to_marble` PRISMATIC -Z（codd）| parent L194-L202 / screw L248-L256 / swing L327-L337 / cork L207-L215 / dropper L310-L320 / pour L272-L282 / codd L186-L196 |
| fixed neck hardware（挂 bottle 的固定 visual）| screw `neck_threads` / swing `neck_collar` / pour `pour_spout` insert / codd `rubber_ring`（torus）| screw `_neck_threads_mesh` L149-L160 / swing `_collar_mesh` L138-L171 / pour `_spout_solid` L129-L179 / codd `rubber_ring` L148-L159 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| bottle_body_profile | enum | long_neck / wine_bottle / stubby_steinie / boston_round / hip_flask / decanter_carafe / slim_flute | long_neck | choice | deterministic procedural sampler 选 | module table |
| closure_mechanism | enum | pry_off_crown_cap / screw_cap / swing_top / cork / dropper_pipette / pour_spout / codd_marble | pry_off_crown_cap | choice | sampler 选 | module table |
| palette_style | enum | clear_flint / green_wine / amber_beer / cobalt_blue / olive_oil_green / frosted_satin_white / smoke_grey / uv_violet / opaline_milk | green_wine | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)` 选玻璃 colorway（含半透明 alpha + **material finish 维度** + 对应金属/金/cork/陶瓷/橡胶塞料配色）| 见下 §palette 来源 |
| body_height_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放瓶身高度 H → LIP_TOP_Z / PIVOT_Z / marble_seat_z / spout HINGE_Z 同比 → 各 joint origin 高度，clamp | parent 各 *_Z 常量 L29-L34 |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 body 半径 / 半宽（hip_flask 缩 BODY_HW），neck R 同比，clamp（保口部封口配合）| parent BODY_R L35 / flask BODY_HW L38 |
| neck_radius_scale | float | [0.92, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；cap bore / cork plug R / pipette 通道 / marble chamber R / spout plug R 派生跟随（保封口配合）| parent NECK_R L36 / 各 closure 口径 |
| closure_size_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放封口件主尺寸（cap skirt 深 / cork plug 长 / pipette 长 / spout 高 / marble R），clamp | 各 closure 尺寸常量 |
| joint_travel_scale | float | [0.85, 1.12] | 1.0 | independent | 缩放 PRISMATIC 行程 upper（crown/cork/dropper/codd）+ REVOLUTE upper（swing/pour），clamp 到声明上限内 | 各 MotionLimits |
| (—) | constraint | — | — | inequality | 封口配合：`cap_bore_R ≥ NECK_R + clearance` 且 `cap_outer_R ≤ body_R + proud`；cork/marble/pipette R ≤ bore − clearance；违反时按比例回缩 closure_size / neck scale 或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | conditional | swing_top PIVOT_Z 与 pour HINGE_Z 随 body_height_scale 重算（joint origin 必须随 lip / neck 高度移动）；hip_flask 的 closure 接口用其 lip 圆 bore（flask body→neck 已 blend 回圆，封口接口与圆瓶一致）| swing L46-L58 / pour L71-L72 / flask L118-L124 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（所有封口件的瓶口配合尺寸跟随 neck 半径）。scale 只动安全比例 / clearance / 行程 / 细节尺寸，**绝不改 bottle_body_profile / closure_mechanism 的拓扑、joint 类型 / 轴或封口件 part 数**。`palette_style` 只换材质颜色，不计 slot_choice。

### palette_style colorway 来源（≥3，本类取 9 真实玻璃配色 + 显式 material-finish 维度）
真实玻璃瓶 colorway，从 5★ 样本材质常量提炼（其余按 Glass bottle 真实色域推断补足），每 seed `rng.choice(PALETTE_STYLES)` 采样。每个 colorway = **玻璃身（tint rgba + alpha）+ 封口件（metal/gold/cork/ceramic/rubber）配色 + 显式 finish**。

**material-finish 维度（finish）**：每 colorway 显式声明一个表面光泽/质感语义标签，取值 `gloss`（透明高反光釉面玻璃，低 alpha 更透）/ `satin`（磨砂/缎面半透 frosted）/ `opaque_matt`（乳白/不透光 opaline，alpha 接近 1 但仍 <1 保 Glass 身份）。finish 只是材质 rgba/alpha 取值族 + viewer 目检语义标签，**不引入新 material 通道、不改任何拓扑 / 尺寸 / joint**；frosted/opaline 类按规则携带更高 alpha。

| colorway | glass rgba(+alpha) | finish | 配套封口件材质色 | 来源 |
|---|---|---|---|---|
| `clear_flint`（透明白料，gloss flint）| `(0.82,0.85,0.88,0.40)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` / red flip `(0.70,0.15,0.12,1)` | dropper PIPETTE_RGBA `(0.82,0.85,0.88,0.55)` / codd MARBLE_RGBA `(0.82,0.88,0.86,0.55)` 清透玻璃，调低 alpha 至 0.40 作瓶身 |
| `green_wine`（深绿酒瓶，gloss）| `(0.06,0.10,0.05,0.38)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` / gold cap `(0.55,0.52,0.18,1)` | wine_bottle GLASS_RGBA `(0.06,0.10,0.05,0.38)`（深绿半透明）|
| `amber_beer`（琥珀啤酒，gloss）| `(0.18,0.12,0.07,0.40)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` / red flip `(0.70,0.15,0.12,1)` | parent / stubby / cork / swing / screw / dropper / pour / codd GLASS_RGBA `(0.18,0.12,0.07,0.4)`（棕琥珀半透明）|
| `cobalt_blue`（钴蓝，gloss）| `(0.05,0.10,0.30,0.40)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` | 真实玻璃瓶常见钴蓝 colorway（深蓝半透明，alpha~0.40），样本未直接用但属 Glass bottle 真实色域，inferred 补足（仅换 glass rgba，不改结构）|
| `olive_oil_green`（橄榄油浅绿，gloss）| `(0.12,0.13,0.06,0.45)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` | slim_flute GLASS_RGBA `(0.12,0.10,0.06,0.45)` / boston `(0.16,0.10,0.06,0.45)` 风格的浅橄榄半透明 |
| `frosted_satin_white`（磨砂/缎面白，satin）| `(0.88,0.90,0.90,0.62)` | `satin` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` | 浅白半透磨砂玻璃 colorway（frosted → 更高 alpha~0.62），inferred 补足；finish=satin |
| `smoke_grey`（烟灰透明，gloss）| `(0.22,0.22,0.24,0.42)` | `gloss` | metal cap `(0.62,0.60,0.58,1)` / gold cap `(0.55,0.52,0.18,1)` / cork `(0.76,0.60,0.42,1)` / rubber `(0.35,0.08,0.06,1)` / red flip `(0.70,0.15,0.12,1)` | 真实烟熏灰玻璃瓶 colorway（中性灰半透明，alpha~0.42），inferred 补足（仅换 glass rgba）|
| `uv_violet`（UV 紫罗兰，gloss）| `(0.16,0.05,0.22,0.42)` | `gloss` | gold cap `(0.55,0.52,0.18,1)` / metal cap `(0.62,0.60,0.58,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` | Miron/UV 紫玻璃 colorway（深紫半透明，alpha~0.42），inferred 补足（精油/避光瓶常见，仅换 glass rgba）|
| `opaline_milk`（乳白 opaline，opaque_matt）| `(0.93,0.92,0.90,0.80)` | `opaque_matt` | gold cap `(0.55,0.52,0.18,1)` / metal cap `(0.62,0.60,0.58,1)` / cork `(0.76,0.60,0.42,1)` / ceramic `(0.92,0.88,0.80,1)` / rubber `(0.35,0.08,0.06,1)` | 乳白 opaline 不透光玻璃 colorway（最高 alpha~0.80 但仍 <1 保 Glass 身份），inferred 补足；finish=opaque_matt |

封口件配色统一池（每 colorway 按其封口件类型取用，由 palette 表给出）：metal cap `(0.62,0.60,0.58,1)`（含 swing wire / screw cap）/ gold cap `(0.55,0.52,0.18,1)`（slim_flute L17）/ cork `(0.76,0.60,0.42,1)` / ceramic plug `(0.92,0.88,0.80,1)`（swing）/ rubber gasket/seal `(0.35,0.08,0.06,1)`（swing；codd seal `(0.10,0.08,0.06,1)` 同族）/ red flip cap `(0.70,0.15,0.12,1)`（pour）/ off-white spout insert `(0.92,0.90,0.85,1)`（pour）/ dropper cap collar `(0.12,0.12,0.12,1)` + pipette glass `(0.82,0.85,0.88,0.55)` + bulb rubber `(0.08,0.06,0.06,1)`。**所有 glass rgba alpha < 1（gloss 0.38–0.45 / satin ~0.62 / opaque_matt ~0.80），保半透明 Glass bottle 身份**。palette 不改任何拓扑 / 尺寸 / joint / 封口件 part 数。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（bottle_body_profile + closure_mechanism）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单瓶身单封口。
- 备注：parent `_cap_mesh` 内 21 个 crimp 齿（`for i in range(n_flutes)` L145-L156）、screw 的 thread rings / knurls、swing bail 的 `_rod` 段、dropper collar 的 thread tabs 等都是 module 内部 **inline 循环视觉装饰**（非独立 part、非结构 multiplicity），符合可读性契约，可作模板侧 inline 循环视觉的参考写法，不计为 multiplicity 轴。

## 拓扑多样性审计

总组合数：bottle_body_profile(7) × closure_mechanism(7) = **49**。

仅此二轴笛卡尔积 = **49 ≥ 10** 已充裕过门控（无 multiplicity 轴需叠加）。

理由：本类拓扑多样性来源充裕——body(7) × closure(7) = 49 distinct，远超 10。closure 引入 PRISMATIC +Z（crown/cork/dropper pop-off/pull/extract）/ CONTINUOUS +Z（screw spin）/ REVOLUTE +Y（swing-top）/ REVOLUTE +X（pour flip）/ PRISMATIC -Z（codd push-down）等不同 joint 拓扑 + 不同 part / visual count（1–3 visual、固定 neck 硬件有无），是真实结构差异。body 轴改 lathe 轮廓 + hip_flask 的非圆 D/肾截面（不同 loft helper、非旋转对称）。slot_choices 编入二轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（49 组合近全合法，少量 conditional 派生见下），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 派生适配（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9（每 closure 至少出现一次 + hip_flask）。

Topology target：1000-seed slot choice tuple distinct 预计接近 49（49 组合的采样空间足够；受真实词汇表约束的 49 是该小类的合理上限）。低于 300 的原因：本小类真实结构词汇就是 7 body × 7 closure = 49，是该类目的合理上限，不强行注水第三轴（参考 source map 排除项：finish/collar 形、size scale、handle/jug 均被拒为非独立结构轴）。49 distinct ≫ 10 门槛，且每个 closure joint 拓扑互异，多样性质量高。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / neck_radius / closure_size / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（所有封口件瓶口配合尺寸派生跟随）。封口配合不等式 + joint origin conditional（PIVOT_Z / HINGE_Z 随高度重算）在 resolve 内投影 / 解析，不留到 builder。这些 scale 不破坏 joint origin（lip top / 颈 pivot / spout 后顶 / marble seat）、封口配合、半透明玻璃身份或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（49 近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含二轴且与 build 一致 |
| compatibility matrix | (1) 全 49 组合合法（任意 body × 任意 closure 都能装：封口接口都落在 body 的 lip / neck，body→neck 已 blend 回圆 bore，hip_flask 亦然）。(2) closure 各候选互斥（一次一种 + 其固定 neck 硬件）。(3) `body_height_scale` 触发 swing PIVOT_Z / pour HINGE_Z / codd marble_seat_z 的 conditional 重算（joint origin 随 lip/neck 高度移动，resolve 解析）。(4) `neck_radius_scale` equation 驱动所有封口件瓶口配合尺寸（cap bore / cork plug / pipette / spout plug / marble chamber）。**无硬 gate-out**，仅在 resolve 派生尺寸 / origin 适配。 | 无 floating（codd marble 由 `allow_isolated_part` + within/overlap 守）/ collision / 封口件穿瓶壁 / joint 轴或 origin 错位 / rest pose 非闭合 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_radius equation 驱动封口配合；joint origin conditional 随高度重算 | 比例变化不破坏 joint origin / 封口配合 / 坐地 / 半透明玻璃身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作（pop-off / spin / swing / pull / extract / flip / push-down）/ 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| bottle_body_profile | 7 | yes | yes | lathe 玻璃 shell 七族（6 圆截面 loft/revolve + 1 非圆 D/肾 hip_flask）|
| closure_mechanism | 7 | yes | yes | crown(PRIS+Z) / screw(CONT+Z) / swing(REV+Y) / cork(PRIS+Z) / dropper(PRIS+Z) / pour(REV+X) / codd(PRIS-Z) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (bottle_body_profile, closure_mechanism) 二轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（49 组合 + palette_style）
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动所有封口件瓶口配合尺寸；封口配合不等式 + joint origin conditional（PIVOT_Z / HINGE_Z / marble_seat_z 随高度重算）在 resolve 内投影 / 解析
- compatibility matrix / gating：49 组合全合法（无硬 gate-out），任意 body × 任意 closure 可装（封口接口落在 lip / 圆 neck bore）
- 半透明玻璃身份：`bottle_glass` material alpha < 1（9 个 palette_style 全保 alpha<1：gloss 0.38–0.45 / satin frosted_satin_white ~0.62 / opaque_matt opaline_milk ~0.80，最高 0.80 仍 <1，不退化为不透明塑料瓶）；finish 维度（gloss/satin/opaque_matt）只是 rgba/alpha 取值族 + viewer 目检标签，不引入新 material 通道
- 连续 scale clamp 后不破坏 joint origin / 封口配合 / 坐地 / 半透明玻璃身份
- 关键 joint：crown/cork/dropper `bottle_to_*` PRISMATIC +Z (abs(axis[2])>0.99)；screw `bottle_to_cap` CONTINUOUS +Z（旋转无平移，半圈后 z/xy 不变）；swing `bottle_to_stopper` REVOLUTE +Y (abs(axis[1])>0.99)；pour `bottle_to_flip_cap` REVOLUTE +X (abs(axis[0])>0.99)；codd `bottle_to_marble` PRISMATIC -Z (axis[2]<-0.99)
- 固定 neck 硬件 visual 按 closure 发射：screw `neck_threads` / swing `neck_collar` / pour `pour_spout` insert / codd `rubber_ring`
- captured-fit：element-scoped `allow_overlap`（cap skirt ↔ glass、cork ↔ glass、pipette ↔ glass、screw thread ↔ neck_threads、swing plug/gasket ↔ glass & bail ↔ collar、flip_cap ↔ spout、marble ↔ glass）；codd 另加 `allow_isolated_part(marble)`
- grandfather：所有封口 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用不透明材质（alpha=1）做瓶身 → 失 Glass bottle 身份；`bottle_glass` 必须半透明（alpha<1），归不透明塑料瓶则出 `container_bottle`。
- 用 boxy 占位体（纯 Box）当瓶身 → 失类别身份；圆瓶身必须 loft / revolve lathe，hip_flask 用 `_flask_loft` 多边形 D/肾截面。
- closure joint origin 放在瓶底 / 任意点而非 lip top / 颈 pivot / spout 后顶 / marble seat 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- closure rest pose 设成张开 / 抬起 / 翻开而非 q=0 闭合坐封 → current-pose 与 viewer 目检不符（marble 必须 q=0 抵 ring 密封、flip_cap 必须 q=0 罩 spout）。
- screw cap 用 PRISMATIC 当 CONTINUOUS（或反之）、codd marble 用 +Z 当 -Z、pour flip 轴用 +Z 当 +X → joint 语义错误，joint 类型 / 轴检查 FAIL。
- 给封口 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap（codd 还需 allow_isolated_part）。
- 把 body-profile 变体（只改 `_bottle_solid` 轮廓）当 closure candidate、或把 closure 变体当 body candidate → 轴混淆；两轴正交（body 改 lathe 轮廓、closure 改瓶口机构）。
- 把 palette_style / 尺寸 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 colorway，不计 slot_choice）。
- 把宽口大盖罐（jar）/ 通用塑料挤压瓶（plastic bottle）/ 精华小滴管瓶（serum）混入 → 出 Glass bottle 类目（见 §边界）。
- 封口件开口（pop-off / 旋离 / 拔 / 摆 / 翻 / 压）时穿瓶壁 / origin 漂移 → 封口配合不等式或 origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_bottle 通用塑料瓶**——理由：那是不透明塑料 + 运动水瓶 / 翻盖吸管 / 泵头 / 挤压机构的更广封口家族；Glass bottle 是半透明玻璃 lathe 身 + 啤酒 / 酒 / 油 / 药剂玻璃封口（crown / cork / swing / codd / dropper / pour）。
- 不该混入：**container_bottle_serum 精华滴管瓶**——理由：那是小尺寸化妆精华滴管瓶（专门小类）；本类 dropper 候选是大玻璃瓶上的通用滴管封口之一，瓶身为饮料 / 酒尺寸玻璃瓶。
- 不该混入：**container_jar 宽口罐**——理由：jar 口径≈瓶身、螺旋大盖 / 后铰翻盖、无细长颈；glass bottle 有明确收肩 + 窄颈（含宽肩 decanter 也以长细颈收口）。
- 不该混入：**cup / mug 杯**——理由：杯敞口无可闭口机构；glass bottle 必有一个封口活动件。
- 不该混入：**jug / growler 提把瓶、双口连体瓶**——理由：加提把 / 双口出 Glass bottle 类目（source map 排除项）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_profile_loft(sections)`（圆截面 loft，6/7 body 候选 + 多个 closure 公用）+ `_revolve_profile`（slim_flute 圆 lathe，等价替代）+ `_flask_loft`/`_flask_profile_pts`（hip_flask 非圆 D/肾截面，专用）+ `_bottle_solid(profile)`（outer.cut(inner) 厚壁开口 shell）+ `_rod(p1,p2,r)`（swing bail wire 段，可复用）+ `_thread_ring`（screw neck/cap thread）。圆 body 用 loft/revolve；非圆 hip_flask 用多边形点 loft。
- closure 固定 neck 硬件：screw 的 `neck_threads`、swing 的 `neck_collar`、pour 的 `pour_spout` insert、codd 的 `rubber_ring`（TorusGeometry）+ neck bore 的 pinch/chamber 改挖——都挂 `bottle`（fixed visual / cut），不是独立 part。
- captured-fit overlap：`run_container_glass_bottle_tests` 里按 closure 声明 element-scoped `ctx.allow_overlap`（cap skirt↔glass、cork↔glass、pipette↔glass、screw_cap↔neck_threads、swing plug/gasket↔glass + bail↔collar、flip_cap↔pour_spout、marble↔glass）；codd 另加 `ctx.allow_isolated_part(marble, reason=...)`。
- neck_radius equation：`resolve_config` 派生各封口件瓶口配合尺寸（cap bore = NECK_R + clearance、cork/pipette/marble/spout plug R ≤ bore − clearance），封口配合不等式在 resolve 投影。
- joint origin conditional：swing PIVOT_Z、pour HINGE_Z、codd marble_seat_z、各顶口 LIP_TOP_Z 随 `body_height_scale` 重算（joint origin 跟随真实 lip / neck 高度）。
- screw CONTINUOUS：origin lip top、axis +Z、旋转无平移（半圈后 z/xy 不变，见 screw 样本 run_tests L332-L350）；codd PRISMATIC **-Z**（push-down 开启，axis 负 Z）。
- 参考模板：本仓库 `agent/templates/Container_Jar.py`（同 parallel_children + body×closure 二/三轴 + 多 closure joint 分支 + captured-fit allow_overlap + element-scoped grandfather 骨架，运动拓扑最接近）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig + config_from_seed + resolve_config clamp + slot_choices_for_config 报 topology family 的标准骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | long_neck + pry_off_crown_cap（parent）| rec_dark-glass-beer-bottle-…_2a24ec81 | `_profile_loft` L43-L55 / `_bottle_solid` L58-L98 / `bottle` L169-L174 / `_cap_mesh` L101-L158 / `bottle_to_cap` PRISMATIC +Z L194-L202 | 长颈玻璃 body 基线 + 皇冠 pop-off 机构基线 |
| S2 | A | wine_bottle | rec_container_glass_bottle_var_wine_bottle | `_bottle_solid` L68-L132 / `punt_sphere` cut L102-L108 | 葡萄酒瓶 body（高圆肩急收 + punt 凹底）|
| S3 | A | stubby_steinie | rec_container_glass_bottle_var_stubby_steinie | `_bottle_solid` L60-L110 | 矮胖 steinie body（宽身 + 极短颈）|
| S4 | A | boston_round | rec_container_glass_bottle_var_boston_round | `_rounded_shoulder_sections` L63-L78 / `_bottle_solid` L81-… | 波士顿圆瓶 body（cosine 圆肩连续过渡）|
| S5 | A | hip_flask | rec_container_glass_bottle_var_hip_flask | `_flask_profile_pts` L56-L79 / `_flask_loft` L82-L99 / `_bottle_solid` L102-L143 | 扁酒壶 body（非圆 D/肾截面，唯一非旋转对称）|
| S6 | A | decanter_carafe | rec_container_glass_bottle_var_decanter_carafe | `_profile_loft` L49-L61 / `_carafe_solid` L64-… | 宽肩 decanter/carafe body（宽球腹 + 长细颈）|
| S7 | A | slim_flute | rec_container_glass_bottle_var_slim_flute | `_revolve_profile` L43-L62 / `_flute_outer_profile` L65-L89 | 高瘦 flute body（连续无肩，revolve lathe）|
| S8 | B | screw_cap | rec_container_glass_bottle_var_screw_cap | `_screw_cap_mesh` L163-L201 / `_neck_threads_mesh` L149-L160 / `_thread_ring` L121-L129 / `bottle_to_cap` CONTINUOUS +Z L248-L256 | 螺纹旋盖（CONTINUOUS 旋 + neck thread 啮合）|
| S9 | B | swing_top | rec_container_glass_bottle_var_swing_top | `_collar_mesh` L138-L171 / `_bail_mesh` L174-L228 / `_plug_mesh` L231-L266 / `_gasket_mesh` L269-L278 / `bottle_to_stopper` REVOLUTE +Y L327-L337 | 摆杆翻塞 swing-top（REVOLUTE 铰 + bail/plug/gasket + collar captured pivot）|
| S10 | B | cork | rec_container_glass_bottle_var_cork | `_cork_mesh` L101-L171 / `bottle_to_cork` PRISMATIC +Z L207-L215 | 软木塞（PRISMATIC 直拔，锥塞坐 bore + grip head）|
| S11 | B | dropper_pipette | rec_container_glass_bottle_var_dropper_pipette | `_cap_collar` L119-L169 / `_pipette_tube`(LatheGeometry) L172-L210 / `_squeeze_bulb` L213-L252 / `bottle_to_dropper` PRISMATIC +Z L310-L320 | 滴管盖（PRISMATIC 直拔，collar + pipette 伸瓶膛 + squeeze bulb）|
| S12 | B | pour_spout | rec_container_glass_bottle_var_pour_spout | `_spout_solid` L129-L179（固定 visual L243-L248）/ `_flip_cap_solid` L182-L225 / `bottle_to_flip_cap` REVOLUTE +X L272-L282 | 倒酒嘴翻盖（固定 spout insert + REVOLUTE +X flip_cap 后铰）|
| S13 | B | codd_marble | rec_container_glass_bottle_var_codd_marble | `_bottle_solid`(pinch+chamber bore) L72-L128 / `marble`(Sphere) L168-L177 / `rubber_ring`(Torus) L148-L159 / `bottle_to_marble` PRISMATIC -Z L186-L196 | Codd 玻璃珠塞（PRISMATIC -Z 下压，captive marble + pinch chamber + rubber ring）|
</content>
</invoke>
