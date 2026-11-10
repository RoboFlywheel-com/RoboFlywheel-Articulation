# Healthcare_Pill_bottle_box — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_Pill_bottle_box` |
| template path | `agent/templates/Healthcare_Pill_bottle_box.py` |
| test path (optional) | `tests/agent/test_Healthcare_Pill_bottle_box_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (Family A bottle = linear_chain body->closure; Family B organizer = parallel_children/multiplicity tray->N lids) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 7 declared sources (Family A: 3, Family B: 4) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

一个 **药品收纳容器** 小类，包含 **两个不可自由组合的 ③ 主体形态家族**：

- **Family A — 药瓶 / vial**：中空塑料瓶体（圆柱或方柱截面）+ 闭合机构（螺旋/提拉盖 PRISMATIC，或翻盖 REVOLUTE）。瓶内琥珀色软胶囊填充（装饰性内部，非 slot）。身份 = 瓶身 + 标签 + 顶盖。
- **Family B — 药盒 / 分格收纳盒 organizer**：浅托盘（矩形或圆形）+ N 个药格 + 格盖机构（每格独立翻盖 REVOLUTE xN，或单张滑盖 PRISMATIC，或旋转拨盘 REVOLUTE-z）。身份 = 分格井 + 盖机构 + 日期标记。

两家族结构互斥：螺旋盖不属于药盒，翻格盖不属于药瓶。模板把 family 作为最顶层 ③ 选择，config_from_seed 先抽 family 再只抽该 family 的槽位；resolve_config 拒绝跨家族组合。

不该混入：普通饮料/化妆品瓶（Container_Bottle）、工具/钓具盒（tackle_box）。

## 5 星样本阅读摘要 (sources)
Family A: S_A1 rec_a-cylindrical-...-9552f090 (round bottle+lift cap), S_A2 rec_pillbox_var_square_bottle (square), S_A3 rec_pillbox_var_fliptop (fliptop REVOLUTE).
Family B: S_B1 rec_a-portable-7-day-...-81682422 (7 flip lids), S_B2 rec_pillbox_var_14cell (14 grid), S_B3 rec_pillbox_var_sliding_lid (sliding), S_B4 rec_pillbox_var_round_weekly (dial).

## 槽位 + 候选模块表

### Slot F (Primary Form Family, top): form_family
| module | source_type | source | model.py | eligibility | 结构特征 |
|---|---|---|---|---|---|
| bottle | forked_anchor | S_A1 | L107-L266 | eligible | 中空瓶体 root + 单一 closure；Volumetric Envelope (旋转体). |
| organizer | forked_anchor | S_B1 | L88-L229 | eligible | 浅托盘 root + N 格盖 parallel；Volumetric Envelope (浅盘). |

### Family A - Slot A1: bottle_body_form (Planar Boundary)
| module | source_type | source | model.py | eligibility | 结构 |
|---|---|---|---|---|---|
| round_cylinder | forked_anchor | S_A1 | L33-L63 | eligible | CadQuery 旋转轮廓中空壳 (圆截面). |
| square_prism | forked_anchor | S_A2 | L68-L93 | eligible | CadQuery rounded-rect box + 圆颈 + shell(-wall). |

候选=2（源池仅圆/方两截面，有据降 2；③ 主多样性由 family 分叉 + organizer 底盘共同承载）。

### Family A - Slot A2: bottle_closure (关节类型)
| module | source_type | source | model.py | eligibility | 结构 |
|---|---|---|---|---|---|
| screw_lift_cap | forked_anchor | S_A1 | L223-L265 | eligible if compatible | cap (圆柱+滚花肋) PRISMATIC z 提拉. iface_key=bottle_mouth. |
| fliptop_hinged | forked_anchor | S_A3 | L242-L313 | eligible if compatible | neck_collar(body visual)+flip_lid REVOLUTE y. iface_key=bottle_mouth. |

### Family B - Slot B1: lid_mechanism (关节/骨架)
| module | source_type | source | model.py | eligibility | 结构 |
|---|---|---|---|---|---|
| individual_flip_lids | forked_anchor | S_B1 | L160-L187 | eligible if base=rect | N compartment_lid_{n} REVOLUTE(-x), 后缘铰接向上翻. |
| single_sliding_cover | forked_anchor | S_B3 | L153-L191 | eligible if base=rect | 单张 sliding_cover PRISMATIC x. |
| rotating_dial_lid | forked_anchor | S_B4 | L211-L273 | eligible if base=round | 单张 dial_lid (pie 窗) REVOLUTE z 绕中心柱. |

### Family B - Slot B2: compartment_count N (multiplicity)
| module | source_type | source | model.py | eligibility | 结构 |
|---|---|---|---|---|---|
| weekly_7 | forked_anchor | S_B1 | L125-L157 | eligible | 7 格 (矩形井或 7 pie). |
| twice_daily_14 | forked_anchor | S_B2 | L128-L200 | eligible | 7x2=14 均布网格. |

rect 家族 N in [4,28]，round-dial 家族 N in [4,8] pie 扇区。

### Family B - Slot B0 (派生 ③): organizer_base_form
rect_tray (mechanism in {flip, sliding}) / round_tray (mechanism=dial)。由 lid_mechanism 派生，不独立采样。

## 槽位图

pattern: mixed

Slot F [form_family]:
- bottle: bottle_body(root) --[A2 closure joint]--> {screw_lift_cap(PRISMATIC z) | fliptop_hinged(REVOLUTE y)}；软胶囊填充+标签 = bottle_body 的 host-conformal visuals（不动，非 part）。
- organizer: base_tray(root) --[B1 lid joints]--> {individual_flip_lids: base --REVOLUTE(-x)--> compartment_lid_{0..N-1} (parallel x N) | single_sliding_cover: base --PRISMATIC(+x)--> sliding_cover | rotating_dial_lid: base --REVOLUTE(+z)--> dial_lid}。

跨 slot 接口/joint：
- A2: mating = 瓶口 rim (body_shell +z @ z=BODY_TOP_Z) 对 cap_shell -z (screw)，或 neck_collar(body visual +z) 对 lid_disk -z (fliptop)。
- B1 flip: 每格 mating = well_{n}_rear_wall +z (z=WALL_TOP_Z) 对 lid_panel -z；REVOLUTE axis(-1,0,0) origin(x,y_rear,WALL_TOP_Z) range[0, clamp<=88deg]。
- B1 slide: mating = slide_rail_0 +z 对 cover_panel -z；PRISMATIC axis(1,0,0) origin(0,0,COVER_BOTTOM_Z)。
- B1 dial: mating = outer_rim +z 对 dial_disc -z；REVOLUTE axis(0,0,1) origin(0,0,WALL_TOP_Z) range[0, SECTOR*(N-1)]；中心柱穿盘孔 element allow_overlap。

互斥/派生：family 决定 A* 或 B* 全体；base_form 由 mechanism 派生；bottle 无 tray/lid，organizer 无 cap/collar。

## 每槽位 Module Emits / Interfaces

Slot F/bottle - bottle_body(root): parts=[bottle_body]; visuals=body_shell(mesh)+fill_core_*(Cylinder,连通贴内壁+底)+fill_pellet_*(scaled Sphere,嵌 core)+label_band/accent_*(host-conformal sleeve); 无 internal joints (软胶囊/标签是 visuals,Rule1); downstream=瓶口 body_shell +z, iface_key=bottle_mouth. (S_A1 L118-L221)

A2/screw_lift_cap: parts=[closure_cap]; visuals=cap_shell(Cyl)+cap_rib_*(Box)+顶盘; joint bottle_to_cap PRISMATIC z[0,cap_lift] mating(body_shell+z, cap_shell-z); upstream=cap_shell -z(local0) iface_key=bottle_mouth. (S_A1 L223-L265)

A2/fliptop_hinged: parts=[flip_lid] (collar 折入 body visual neck_collar,Rule1); visuals=neck_collar+lid_disk(Cyl)+lid_tab(Box)+hinge_barrel(Cyl); joint body_to_flip_lid REVOLUTE y[0,~1.5] mating(neck_collar+z, lid_disk-z); upstream=lid_disk -z. (S_A3 L242-L313)

Slot F/organizer - base_tray(root): parts=[base_tray]; rect visuals=rounded_base_bottom(mesh)+4 rim+well_{n}_floor/_rear_wall/_front_wall/_side_wall_*(Box); round visuals=base_plate(disc mesh)+outer_rim(ring mesh)+center_post(Cyl)+divider_wall_{i}(Box)+well_floor_{i}(sector mesh); downstream=well_{n}_rear_wall +z (rect) / outer_rim +z (round) / slide_rail top. (S_B1 L107-L157; S_B4 L121-L209)

B1/individual_flip_lids (x N): parts=[compartment_lid_{0..N-1}] 统一 helper 同尺寸共享 1 mesh; visuals/lid=lid_panel(rounded_box mesh 复用)+front_fingernail(Box)+hinge_leaf(Box)+日期 decals(宿主 visual); joint base_to_lid_{n} REVOLUTE(-1,0,0)[0,<=88deg] mating(well_{n}_rear_wall+z, lid_panel-z). (S_B1 L160-L187)

B1/single_sliding_cover: parts=[sliding_cover]; visuals=cover_panel(rounded_box mesh)+cover_groove_*+grip_tab+日期 decals; joint base_to_sliding_cover PRISMATIC x[0,travel] mating(slide_rail_0+z, cover_panel-z). (S_B3 L153-L191)

B1/rotating_dial_lid: parts=[dial_lid]; visuals=dial_disc(pie 窗+中心孔 mesh)+grip_tab+window_indicator; joint base_to_dial_lid REVOLUTE z[0,SECTOR*(N-1)] mating(outer_rim+z, dial_disc-z); post 穿孔 element allow_overlap. (S_B4 L212-L273)

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 标称默认 | 约束类型 | 约束/函数 | 来源 |
|---|---|---|---|---|---|---|
| form_family | enum | {bottle, organizer} | bottle | choice | 顶层 ③ 家族 procedural | Slot F |
| palette_style | enum | {amber_bottle,clear_bottle,white_bottle,pastel_organizer,cream_organizer,mint_organizer} | amber_bottle | choice | family 相容子集(bottle3/organizer3), 驱动每个 .visual(material=) | 8.5 涂装 |
| bottle_body_form | enum | {round_cylinder,square_prism} | round_cylinder | choice | 仅 family=bottle | A1 |
| bottle_closure | enum | {screw_lift_cap,fliptop_hinged} | screw_lift_cap | choice | 仅 family=bottle | A2 |
| lid_mechanism | enum | {individual_flip_lids,single_sliding_cover,rotating_dial_lid} | individual_flip_lids | choice | 仅 family=organizer | B1 |
| organizer_base_form | enum(派生) | {rect_tray,round_tray} | rect_tray | equation | =round_tray if dial else rect_tray | B0 |
| compartment_count N | int | rect[4,28]/dial[4,8] | 7 | conditional | 上限随 mechanism (dial<=8) | 8 |
| body_height_scale | float | [0.80,1.25] | 1.0 | independent | clamp | S_A1 |
| body_radius | float | [0.026,0.036] | 0.030 | independent | clamp(bottle) | S_A1 |
| cap_lift | float | derived | 0.05 | equation | =clamp(cap_height*2.2,0.03,0.06) | S_A1 |
| base_w | float | [0.10,0.17] | 0.130 | independent | clamp(rect) | S_B1 |
| base_d | float | derived | 0.100 | equation | =base_w*0.77 | S_B1 |
| tray_radius | float | [0.050,0.075] | 0.065 | independent | clamp(round) | S_B4 |
| lid_open_angle | float | derived | 1.5 | equation/inequality | <=1.53, panel 顶端 y<=后排井前缘 | S_B1 |
| grid | constraint | cols=min(7,N),rows=ceil(N/cols) | — | inequality | cell_w/d>0; lid 复用同 mesh | 接口 |
| dial | constraint | SECTOR=2pi/N, 窗=1 扇区, 旋转上界=SECTOR*(N-1) | — | inequality | — | S_B4 |

连续采样契约：先 independent(body_radius/height_scale 或 base_w/tray_radius) -> equation(base_d,cap_lift,open_angle) -> inequality(网格/夹角/扇区)。

### 7.5 编译预算
自报 <= 15s/seed（依据：瓶旋转壳+分格盒轻量 CadQuery，实测同类 5-15s）。复用：N 个 lid 复用同一 rounded_box_mesh；瓶体 1 mesh + <=4 薄 sleeve；盖肋/井墙全 Box primitive；dial N<=8 sector mesh；软胶囊 Cylinder primitive + <=12 复用 1 sphere mesh。tolerance 0.0003-0.0008, angular<=0.15。超预算先降精度。sweep --compile-timeout 120 (看门狗)。

## Multiplicity / Copy Logic
轴 1: compartment_count N (仅 Family B)。count_param=compartment_count；N_range rect[4,28]（weekly7/AMPM14/4x28 及之间）, round-dial[4,8]。sampling: 小 N 高频(7,14)、大 N(21-28) 稀有、dial 集中 7；测试偏小、产品全程。copied object=compartment_lid_{n}(flip) 或 well_{n}/well_floor_{i}(slide/dial)。naming=compartment_lid_{n}/well_{n}_*/well_floor_{i}。placement rect=行主序 cols=min(7,N),rows=ceil(N/cols) 末行可部分；dial=N 等角 pie。joint policy flip=每格 REVOLUTE(-x) 后缘统一 open_angle；slide/dial=单盖 joint(井不动)。source/gating flip N 个 lid(7/14 覆盖轴)，slide/dial N 只影响井数。
Family A 无 copy loop（closure 单件；软胶囊填充装饰内部非 slot）。

## 视觉多样性 6 轴考察
| 轴 | 判断 | 有/无 | 取值/来源 |
|---|---|---|---|
| 1 骨架图 | 加减会动 part/边 | 有 | bottle body->1 closure; organizer tray->N lids(flip)/1 cover(slide)/1 dial. forked_anchor(7 源). |
| - multiplicity | 同构 xN | 有 | 见 8: N rect[4,28]/dial[4,8] 小 N 高频. |
| 2 关节类型 | 换 type/轴 | 有 | PRISMATIC z(screw)、PRISMATIC x(slide)、REVOLUTE y(fliptop)、REVOLUTE -x(flip lids)、REVOLUTE z(dial). 全 forked_anchor,每种在 sweep 出现. |
| 3 主体形态家族 | 换核心几何原型 | 有 | family=bottle(Volumetric 旋转体) vs organizer(浅盘); bottle round/square(Planar Boundary); organizer rect/round 盘(Volumetric). source-backed,登记 slot_choices. |
| 4 表面装饰 | 叠表面细节 | 有 | bottle: host-conformal 标签 sleeve+彩条(随 radius(z)/half-width 共形)、盖滚花肋; organizer: 日期号 decals(1-7)、格缝暗线、拨盘 day dots. record_only+world_knowledge_extrapolation,宿主派生. |
| 5 尺寸/行程 | 连续改尺寸/行程 | 有 | bottle H via height_scale[0.80,1.25]/radius[0.026,0.036]; organizer base_w[0.10,0.17]/tray_r[0.050,0.075]. 运动包络: cap PRIS z[0,cap_lift]、fliptop REV[0,~1.5]、flip lid REV[0,<=88deg]、slide PRIS[0,travel]、dial REV[0,SECTOR*(N-1)]. motion_test_plan: 每机构 targeted ctx.pose + fail_if_parts_overlap_in_sampled_poses(max_pose_samples<=32); 全程不穿模. |
| 6 涂装 | 只改材质/颜色 | 有 | palette_style>=3(目标6): bottle{amber/clear/white translucent plastic+black/white cap}; organizer{pastel translucent blue/green/pink/amber+cream/mint frame}. 材质大类 plastic(translucent+opaque)+paper label; >=3 大类覆盖. |

收尾自检: template batch 0-9 seed 必须肉眼看到两家族、round/square 瓶、flip/slide/dial 盒、不同 N、非单色。

## 拓扑多样性审计
总组合(离散): bottle body(2)xclosure(2)=4; organizer mechanism(3)xN 覆盖; family(2) 顶层分叉 -> 合计 >=15；1000-seed slot choice tuple distinct 按 ≥300 report-only 口径观察，低于 300 时记录小词汇类别上限，palette(6)+连续尺度只补视觉多样性。
seed_domain_policy: procedural_first。config_from_seed(seed)=random.Random(seed): 先抽 family(~50/50) 再抽 palette+槽位+N(加权小 N), 全 procedural, seed0 不特殊, 无 curated 表。
Topology target: 1000-seed distinct按 ≥300 report-only 口径观察。
Controlled local: body_radius/body_height_scale/base_w/tray_radius(independent clamp); base_d/cap_lift/lid_open_angle(equation); N+网格(inequality/conditional). 都在 resolve_config 求解。

| item | policy | validator focus |
|---|---|---|
| sampler | family->palette->slots->N weighted 小 N | slot_choices_for_seed==build 选择 |
| compatibility matrix | 跨家族非法 gate; base_form 派生; dial->round; N 上限随 mechanism | 无跨家族/悬空/穿模/非法对 |
| controlled local variation | 上列 scale clamp/derived | 比例变化不破坏接口/clearance/joint origin/身份 |
| regression overrides | none | — |
| random sweep | 0-35 初验,0-999 成熟 | contract failures; axis_realization |

| slot | candidate_count | >=2 | >=3 | 备注 |
|---|---|---|---|---|
| form_family | 2 | yes | no | 顶层家族互斥大结构 |
| bottle_body_form | 2 | yes | no | 源池仅圆/方,有据降2 |
| bottle_closure | 2 | yes | no | screw/fliptop |
| lid_mechanism | 3 | yes | yes | flip/slide/dial |
| compartment_count | N 档 | 覆盖 | — | N 不计 distinct |

## Validator
- slot_choices_for_seed 返回已实现 module 名(family+该家族槽位+N 档)
- config_from_seed 全 procedural(含 seed0)
- compatibility: family 决定槽位集; base_form 派生; dial<->round 其余<->rect; 跨家族拒绝
- 关键 joint 类型/轴: cap PRIS z; fliptop REV y; flip lid REV -x; slide PRIS x; dial REV z
- 每个非 FIXED joint 有 MatingContract 到真实 face
- 复制件命名/布局 compartment_lid_{n}/well_{n}, 统一 hinge policy
- 连续 scale 在 resolve_config clamp/派生

## Reject cases
- 跨家族组合(螺旋盖装药盒、翻格盖装药瓶)
- closure/lid joint 缺 MatingContract 或 mating face 悬空>contact_tol
- 软胶囊填充/标签/日期号做成 FIXED part(应宿主 visual,Rule1)
- CadQuery 旋转/box shell 降级成裸 Cylinder/Box(Rule3)
- 翻格盖 open_angle 过大越后排井穿模
- 每 lid 各生成 mesh(应复用)导致超预算
- 标签常数半径套方瓶/缩放瓶悬空(Rule4)
- N 超档(rect>28/dial>8) 或网格 cell 退化

## 与相邻类别的边界
- 不该混入 Container_Bottle(普通瓶,无 pill-fill 身份/无 organizer 家族)
- 不该混入 tackle_box/工具箱(大提手+金属闩,非药格)
- 不该混入 Container_Pump 化妆品泵瓶(泵头机构,非 pill 闭合)

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 两家族+跨家族 gate+每非 FIXED joint MatingContract+lid mesh 复用+host-conformal 标签,已落定。 |

## Module Source Index
| source_id | slot | module | sample_id | model.py | 采纳 |
|---|---|---|---|---|---|
| S_A1 | F.bottle/A1.round/A2.screw | round bottle+lift cap | rec_a-cylindrical-...-9552f090 | L33-L266 | 旋转壳+软胶囊+PRISMATIC 提拉盖 |
| S_A2 | A1.square | square bottle | rec_pillbox_var_square_bottle | L68-L137 | box+shell 方瓶+方盖 |
| S_A3 | A2.fliptop | fliptop | rec_pillbox_var_fliptop | L114-L313 | 颈环+REVOLUTE 翻盖 |
| S_B1 | F.organizer/B1.flip/B2.7 | 7-day flip organizer | rec_a-portable-7-day-...-81682422 | L88-L229 | 矩形托盘+N 翻格盖 |
| S_B2 | B2.14 | 14-cell grid | rec_pillbox_var_14cell | L128-L200 | 7x2 均布网格 multiplicity |
| S_B3 | B1.sliding | sliding cover | rec_pillbox_var_sliding_lid | L140-L211 | 导轨+PRISMATIC 滑盖 |
| S_B4 | B1.dial/B0.round | round weekly dial | rec_pillbox_var_round_weekly | L43-L273 | 圆盘+pie 井+REVOLUTE-z 拨盘 |
