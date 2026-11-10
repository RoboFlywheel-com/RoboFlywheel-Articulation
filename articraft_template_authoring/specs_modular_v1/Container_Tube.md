# container_tube (squeeze tube: toothpaste / cosmetic / glue — soft body + crimped tail + shoulder + dispensing closure) — Modular Spec

> 来源小类：`picture/Container/Tube`（articraft_data 上游 Container/Tube fork-variant pool）。
> 本小类 fork 变体是组合式双轴 diff（body_footprint × closure_mechanism）：身份在"管身截面 × 顶部分配/闭合机构"两根固定 named slot，无 multiplicity 轴。
> 已逐一读取全部 11 个样本的 `model.py`（2 parent + 9 variant）；引用 `model.py:Lx-Ly` 来自各样本 `articraft_data`/`arti-template` 当前 `revisions/rev_000001/model.py`，以 part/joint/helper **名字** 为准（`_tube_body` / `_body_solid` / `_oval_loop` / `_rounded_rect_pts` / `_taper_levels` / `_open_neck` / `_cap` / `_nozzle_mesh` / `_cap_mesh` / `_open_neck_with_hinge` / `_flip_cap_lid` / `_nozzle_tip` / `_pull_cap` / `_base_cap_mesh` / `_flip_lid_mesh` / `_applicator_tip_mesh` / `_snap_cap_shell_mesh` / `_housing_mesh` / `_ball_mesh` / `_overcap_mesh` / `_twist_ring` / `_platform_disk` / `cap_lift` / `cap_rotate` / `cap_slide` / `flip_cap` / `cap_pull` / `lid_hinge` / `ball_roll` / `overcap_lift` / `body_to_twist_ring` / `twist_ring_to_platform`），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_tube` |
| template path | `agent/templates/Container_Tube.py` |
| test path (optional) | `tests/agent/test_container_tube_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_footprint + closure_mechanism；闭合/分配件挂到 tube_body 共同 root 的颈口/肩面/底口，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 2 parent + 9 qwen 单轴 fork 变体 = 11 |
| read_count | 11（全文逐一读取，无抽样）：P1 sunscreen-lift `60b00467` / P2 cosmetic-screw `7c11d416` 两 parent；body 轴变体 `cylindrical` / `oval_lozenge` / `tapered_cone`；closure 轴变体 `flip_top` / `pull_cone` / `standup_cap` / `slant_applicator` / `roller_ball` / `twist_up` |
| read_scope | all 5-star samples in this category（2 parent 全读 + 全部 9 个 `rec_container_tube_var_*` 全读，含 build_object_model + run_tests）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表与 §14 |

阅读要点（结构变化轴确认）：
- **两根真实结构轴**：(A) body_footprint = 管身截面/轮廓家族（slab 圆角矩形 / round-to-flat 挤压管 / 等径直筒 / 椭圆 lozenge / 单调收锥），换的是 loft helper 与截面 loop，非缩放；(B) closure_mechanism = 顶部分配/闭合机构，**决定 joint 拓扑**（PRISMATIC 升降盖 / CONTINUOUS+PRISMATIC 螺旋盖经 massless carrier / REVOLUTE 翻盖 / PRISMATIC 拉锥盖 / 站立底盘 REVOLUTE 翻盖 / **正轴 applicator + PRISMATIC +Z 拔盖** / CONTINUOUS 球关节滚珠+PRISMATIC overcap / 底旋 CONTINUOUS+腔内 PRISMATIC 升膏平台）。
- **冗余/装饰分流**：两 parent 的 `vertical_brand_mark_{i}` / `small_front_label_{i}`（for-i label 带）、`_nozzle_mesh` 螺纹环（k 循环）、`_cap_mesh` 滚花筋（i 循环）、standup 的 `grip_bump_{i}`、slant 的 `grip_rib_{i}`、twist 的 knurling fins 均为 for 循环发射的**装饰/握持细节带**，可作连续/装饰参数，**不构成结构 multiplicity 轴**（见 §Multiplicity）。
- **新模板实现分层**：保留 `body_footprint × closure_mechanism` 两根结构轴进 `slot_choices`；同时按 6 轴模型补充 appearance-only families：`body_profile_style`（straight / waisted / bulged）、`graphics_style`（front_panel / vertical_stripe / dual_stripe / wrap_band / none）、`tail_detail_style`（plain / single_crimp / double_crimp）、`closure_trim_style`（plain / single_band / double_band / ribbed）。这些都不改变 part-joint 图，只增强同一 closure 下的视觉差异。
- **闭合候选挂载约定（来自样本）**：standup / slant / roller 均 fork 自带 nozzle/shoulder 的 P2（`7c11d416`，round-to-flat 身）以承接出料嘴/肩部几何；twist_up fork 自 P1（`60b00467`，slab 身）以承接平面口腔内升降平台；flip_top / pull_cone 亦 fork 自 P1（slab 身 + 颈口/锥嘴）。

## 核心身份

软体挤压管（squeeze tube：牙膏 / 化妆膏 / 精华 / 护手霜 / 胶水）：一只直立软体管，中心轴沿 +Z，**底坐地 z=0 为压缝/软底**，居中于 (x=0,y=0)，管身向上抬升至肩部收窄、出顶口分配。管身由 CadQuery `loft` 发射为**薄壁中空 shell**（真实开口腔体 + 通到顶口的 bore），截面家族可为圆角矩形扁板 slab（broad 正面）/ round-to-flat 挤压管（底扁压缝→近圆肩）/ 等径圆直筒 barrel / 平滑椭圆 lozenge / 单调收锥 funnel。管顶（少数为管底）按某种**分配/闭合机构**开合（**主活动语义**）：垂直升降盖（PRISMATIC +Z）/ 双解耦螺旋盖（CONTINUOUS +Z 旋 + PRISMATIC +Z 滑，经 massless carrier）/ 后铰翻盖（REVOLUTE 水平轴）/ 尖锥拉拔盖（PRISMATIC +Z over 锥嘴）/ 宽扁站立底盘盖 + 小翻盖（base 固定 visual + REVOLUTE 水平翻盖）/ **正轴 applicator 嘴 + 斜切口沿 + PRISMATIC +Z 拔盖** / 穹顶球座滚珠涂抹头 + overcap（CONTINUOUS 球旋 + PRISMATIC +Z overcap，双活动件）/ 旋底升膏平台（CONTINUOUS +Z 底旋 → PRISMATIC +Z 腔内平台，链式耦合）。默认成熟域：单管单分配头（无嵌套 / 无 multiplicity）。

不该混入：硬体细颈瓶 / 酒瓶（rigid bottle，是 `container_bottle`——管是软挤压壁、底压缝、肩部收口，瓶是硬壁直立 + 长颈）、宽口化妆罐 / 膏霜罐（lidded jar，是 `container_cosmetic`——罐是宽口罐身 + 盘盖，管是细口分配嘴 + 软身）、口红/唇膏旋管（是 `container_lipstick`——口红身份是膏体从套筒顶口旋出、无软挤压身/无分配嘴，twist_up 候选虽含升膏机构但挂在软挤压管身且为护理膏/止汗棒语义，非裸露口红膏）。

## 槽位 + 候选模块表

> **建模注记**：`body_footprint` 是 `tube_body`（root）的 mesh 属性（一次 `_body_mesh(footprint)` 发射 shell + 通顶 bore[ + shoulder/neck 顶口几何]），不是独立串联 slot。`closure_mechanism` 挂到 tube_body 共同 root（parallel children / 颈口·肩面·底口 mating）。两轴笛卡尔积构成拓扑多样性（见 §9）。
> 所有 `Lx-Ly` 已逐一从样本 `model.py` 核对。

### Slot A：body_footprint（管身截面/轮廓家族——root tube_body 的 mesh / 形状家族更换非缩放）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slab_rect（基线，P1）| rec_blue-sunscreen-squeeze-tube-with-a-hinged-flip-t_…_60b00467 | `_oval_loop`(超椭圆 p=3.4) L51-64 + `_loop_xy` L67-68 + `_tube_body`(loft+cavity cut) L71-97 | eligible if compatible | 圆角矩形扁板/超椭圆 slab：Y 宽 X 薄，broad 正面，loft 软底→平顶 deck，腔体 cut 通顶 |
| round_to_flat（基线，P2）| rec_cosmetic-cream-squeeze-tube-with-a-white-screw-c_…_7c11d416 | `_body_solid`(rounded-rect levels loft) L51-80 + `_rounded_rect_pts` L83-100 + `_body_mesh`(shell hollow) L103-128 | eligible if compatible | 经典圆-扁挤压管：底部扁压缝(wide·thin)→上行收圆近圆肩，inner loft cut shell 中空 |
| cylindrical | rec_container_tube_var_cylindrical | `_tube_body`(circle extrude + 底 taper loft + cavity cut) L53-82 + `_open_neck` L85-110 | eligible if compatible | 等径圆直筒 barrel：constant round radius，软底 taper，X≈Y，无扁面 |
| oval_lozenge | rec_container_tube_var_oval_lozenge | `_oval_loop`(纯椭圆 cos/sin) L53-63 + `_loop_xy` L66-67 + `_tube_body` L79-105 | eligible if compatible | 软扁椭圆/lozenge 截面：连续椭圆 loop（无超椭圆扁面），软底→平顶，纯圆顺 |
| tapered_cone | rec_container_tube_var_tapered_cone | `_taper_levels`(sqrt ease 单调收窄) L58-74 + `_loft_from_levels` L96-110 + `_body_solid` L113-117 + `_body_mesh`(shell) L120-136 | eligible if compatible | 宽扁底压缝→上行**单调收窄**至细圆肩的连续锥/漏斗 taper（非 barrel 非挤压鼓肚），每 loft level 严格变窄 |

硬约束记录：body_footprint **5 candidate**（达 3-6 目标上限）。全部 `loft` 中空开口腔，共享 rounded-rect/椭圆/超椭圆 loop helper + 通顶 bore cut，只换截面 loop 函数 / 高宽比 / 收锥 vs 等径 vs 鼓肚。无单 candidate 槽。

### Slot B：closure_mechanism（**主分配/闭合机构槽**——决定 joint 拓扑；挂 tube_body root）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part/joint/helper 名 + 结构特征 |
|---|---|---|---|---|
| lift_cap（基线，P1）| rec_…_60b00467 | `_open_neck`(annular bore neck+lip+ring) L100-125 + `_cap`(loft shell) L128-163 + part `lift_cap` + `cap_lift` **PRISMATIC +Z** L212-222 | eligible if compatible | 白盖沿 +Z 垂直升降罩住开口颈：单 `cap_lift` PRISMATIC +Z，origin 在 neck base，q 升/降 over 开口 neck。1 活动件 |
| screw_cap（基线，P2）| rec_…_7c11d416 | `_nozzle_mesh`(螺纹环 nozzle) L158-179 + `_cap_mesh`(滚花 cap) L182-207 + massless `cap_carrier` L227-228 + `cap_rotate` **CONTINUOUS +Z** L246-254 + `cap_slide` **PRISMATIC +Z** L255-263 | eligible if compatible | 双解耦螺旋盖：经 massless `cap_carrier`，`cap_rotate` CONTINUOUS +Z（旋）+ `cap_slide` PRISMATIC +Z（滑出螺纹 nozzle）。2 joint + 1 massless carrier |
| flip_top | rec_container_tube_var_flip_top | `_open_neck_with_hinge`(颈+hinge boss) L108-146 + `_flip_cap_lid`(living-hinge tab+lid+plug+thumb) L149-225 + part `flip_cap` + `flip_cap` **REVOLUTE axis=(1,0,0)** origin=后 rim collar L286-297 | eligible if compatible | 卡扣翻盖绕颈口后 rim 水平 +X 活铰摆开：q=0 闭合盖座 mouth，正 q 上翻 ~149°。1 活动件 REVOLUTE |
| pull_cone | rec_container_tube_var_pull_cone | `_nozzle_tip`(collar+锥+through-bore) L113-142 + `_pull_cap`(hollow 锥 shell) L145-171 + part `pull_cap` + `cap_pull` **PRISMATIC +Z** L220-230 | eligible if compatible | 尖锥分配嘴(base collar→pointed tip+bore) + 尖头拉拔盖沿 +Z 直拔脱出：q=0 seated over 锥嘴，正 q 拔离。1 活动件 PRISMATIC |
| standup_flip_cap | rec_container_tube_var_standup_cap | `_base_cap_mesh`(八角站立盘) L189-213 + `_orifice_ring_mesh` L221-229 + `_hinge_barrel_mesh` L232-240 + `_flip_lid_mesh`(小翻盖+plug+tab) L255-300 + part `flip_lid` + `lid_hinge` **REVOLUTE axis=(0,-1,0)** origin=盘 top 后 hinge L374-384 | eligible if compatible | 宽扁八角站立底盘盖(固定 visual 挂 body，管可倒立站盘上) + 小卡扣翻盖绕盘顶水平 -Y 活铰摆开露出 orifice。base 固定 + 1 活动件 REVOLUTE |
| slant_applicator | rec_container_tube_var_slant_applicator | `_applicator_tip_mesh`(斜切口沿 applicator 嘴) + `_snap_cap_shell_mesh`(coaxial cap shell) + `_grip_rib_solid` + part `snap_cap` + `cap_pull` **PRISMATIC +Z** | eligible if compatible | 正轴 applicator 嘴，顶部做斜切/斜口出料面，配套卡盖沿 **+Z** 直拔。1 活动件 PRISMATIC |
| roller_ball | rec_container_tube_var_roller_ball | `_housing_mesh`(穹顶球座 socket) L166-203 + `_ball_mesh`(steel 球+marker) L206-219 + `_overcap_mesh`(translucent overcap) L234-255 + part `applicator_ball`+`overcap` + `ball_roll` **CONTINUOUS axis=(1,0,0)** L296-304 + `overcap_lift` **PRISMATIC +Z** L310-320 | eligible if compatible | 穹顶球座内自由旋转滚珠涂抹头(真实滚动关节，CONTINUOUS +X) + 可拔 translucent overcap(PRISMATIC +Z)。**2 活动件** |
| twist_up_stick | rec_container_tube_var_twist_up | `_mouth_rim`(顶口环) L107-127 + `_twist_ring`(底滚花旋环) L130-179 + `_platform_disk`(腔内升膏盘) L182-203 + part `twist_ring`+`platform` + `body_to_twist_ring` **CONTINUOUS +Z**(底) L290-298 + `twist_ring_to_platform` **PRISMATIC +Z**(腔内，child of ring) L304-317 | eligible if compatible | 旋底升膏：管**底部**滚花旋环 CONTINUOUS +Z 驱动管口内平台沿 +Z 升降（膏/止汗棒升降机构，链式 body→ring→platform）。**2 joint 链式耦合** |

硬约束记录：closure_mechanism **8 candidate**（远超 3-6 目标）。含 PRISMATIC(+Z) / CONTINUOUS+PRISMATIC(screw=2 joint+carrier) / REVOLUTE(+X flip) / PRISMATIC(+Z pull) / REVOLUTE(-Y standup flip) / PRISMATIC(+Z applicator cap) / CONTINUOUS(+X 球)+PRISMATIC(+Z overcap)=2 活动件 / CONTINUOUS(+Z 底)→PRISMATIC(+Z 腔内)=链式 2 joint —— 五种以上 joint 拓扑 + 不同 part count + 不同挂载点（颈口顶 / 锥嘴 / 肩面 / applicator 嘴 / 球座 / 管底）。每个 candidate **≥1 non-fixed joint**。无单 candidate 槽。

## 槽位图（slot graph）

pattern: parallel_children（tube_body 为 root，坐地 z=0；closure 件挂到它，多数在顶口/肩面，twist_up 例外挂管底）

```
tube_body(body_footprint)  [ROOT, 坐地 z=0, loft shell + 通顶 bore]
   │  顶口接口 = 顶 deck / shoulder top / nozzle top / 锥嘴 base / 球座 rim（按 closure 派生）
   │
   ├── closure = lift_cap:
   │     tube_body + open_neck(visual) --[cap_lift: PRISMATIC +Z @ neck base]--> lift_cap
   │
   ├── closure = screw_cap:
   │     tube_body + shoulder + nozzle(visual) --[cap_rotate: CONTINUOUS +Z @ nozzle top]--> cap_carrier(massless,无 visual)
   │              cap_carrier --[cap_slide: PRISMATIC +Z]--> cap
   │
   ├── closure = flip_top:
   │     tube_body + open_neck_with_hinge(visual, hinge boss) --[flip_cap: REVOLUTE +X @ 后 rim collar, z=neck top]--> flip_cap
   │
   ├── closure = pull_cone:
   │     tube_body + nozzle_tip(visual, 锥嘴) --[cap_pull: PRISMATIC +Z @ 锥嘴 base]--> pull_cap
   │
   ├── closure = standup_flip_cap:
   │     tube_body + shoulder + nozzle + base_cap_disc + orifice_ring + hinge_barrel(固定 visual 挂 body)
   │              tube_body --[lid_hinge: REVOLUTE -Y @ 盘顶后 hinge barrel]--> flip_lid
   │
   ├── closure = slant_applicator:
   │     tube_body + shoulder + applicator_tip(斜切嘴 visual) --[cap_pull: PRISMATIC +Z @ shoulder top]--> snap_cap
   │
   ├── closure = roller_ball:
   │     tube_body + shoulder + housing_socket(穹顶球座 visual)
   │              tube_body --[ball_roll: CONTINUOUS +X @ 球心]--> applicator_ball
   │              tube_body --[overcap_lift: PRISMATIC +Z @ housing rim]--> overcap
   │
   └── closure = twist_up_stick:    [机构在管底 + 腔内，非顶口]
         tube_body + mouth_rim(顶口环 visual)
              tube_body --[body_to_twist_ring: CONTINUOUS +Z @ 管底 z=0]--> twist_ring
                   twist_ring --[twist_ring_to_platform: PRISMATIC +Z @ cavity bottom]--> platform
```

接口点位与 joint 语义：
- **lift_cap 接口**：`cap_lift` origin 在 neck base 中心 `(0,0,NECK_BASE_Z+ε)`，axis +Z PRISMATIC；盖罩 over 开口 neck（intentional capture）。
- **screw_cap 接口**：`cap_rotate` origin 在 nozzle top 中心 `(0,0,NOZZLE_TOP_Z)`，axis +Z CONTINUOUS；`cap_slide` 经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial），axis +Z PRISMATIC（解耦旋转/平移共享 +Z）。
- **flip_top 接口**：`flip_cap` origin 在颈口**后 rim collar** 硬件 `(0, -MOUTH_LIP_R, NECK_TOP_Z)`，axis +X，REVOLUTE 闭合 q=0、上翻正 q ~149°；living-hinge tab 锚在颈口承托面。
- **pull_cone 接口**：`cap_pull` origin 在**锥嘴 base** `(0,0,NOZZLE_BASE_Z)`，axis +Z PRISMATIC；盖 hollow 锥 over 锥嘴（capture）。
- **standup_flip_cap 接口**：`base_cap_disc`/`orifice_ring`/`hinge_barrel`/`grip_bump_{i}` 为**固定 visual** 挂 tube_body（offset 到 NOZZLE_TOP_Z 上方，无独立 joint）；`lid_hinge` origin 在**盘顶后 hinge barrel** `(HINGE_X, 0, BASE_CAP_TOP_Z+ε)`，axis -Y REVOLUTE（abs(axis[2])≈0 水平），小翻盖上翻 0..~117°。
- **slant_applicator 接口**：`cap_pull` origin 在 **shoulder top** `(0,0,SHOULDER_TOP_Z)`，axis = `+Z` PRISMATIC；嘴体保持正轴，只有顶部口沿做斜切 applicator 面，盖沿 +Z 直拔。
- **roller_ball 接口**：`ball_roll` origin 在**球心** `(0,0,BALL_ORIGIN_Z)`，axis +X CONTINUOUS（球在凹球座内自由滚）；`overcap_lift` origin 在 **housing rim** `(0,0,HOUSING_RIM_Z)`，axis +Z PRISMATIC（overcap 拔离）。**两独立活动件并挂 tube_body**。
- **twist_up_stick 接口**：`body_to_twist_ring` origin 在**管底** `(0,0,0)`，axis +Z CONTINUOUS（底旋环）；`twist_ring_to_platform` origin 在 **cavity bottom** `(0,0,CAVITY_BOTTOM_Z)`，axis +Z PRISMATIC，**parent=twist_ring**（链式耦合：旋环转 → 平台沿 +Z 升）；platform 始终 `expect_within` body bore，不出顶口。
- **mating policy**：盖罩 over neck/nozzle/锥嘴/housing、ball 坐 socket、platform 嵌 bore、base_cap 罩 nozzle 均为 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 neck/nozzle/锥嘴/hinge barrel/球心/housing rim/管底硬件）+ element-scoped `allow_overlap`（见各样本 run_tests 的 `ctx.allow_overlap`）守 overlap。
- **rest pose**：各样本 rest 不一（P1/oval lift_cap q=0 为**开/抬起**；cylindrical lift_cap q=0 为**闭合**；screw/pull/standup/slant/roller overcap q=0 多为**seated/闭合**；twist platform q=0 为**收回 retracted**）；模板侧统一 closed/seated 为 rest，开/抬/旋为 viewer 目检活动语义（实现时按 closure 显式设 rest，sweep 目检确认）。
- **互斥 / 可选**：closure 各候选互斥（一次只一种分配头）；`cap_carrier` massless part 仅 screw 候选发射；twist_up 的机构挂管底+腔内（非顶口），其顶口仅 `mouth_rim` 环。

## 每槽位 Module Emits / Interfaces

### Slot A / tube_body（body_footprint，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tube_body`(root)：visual = body shell（loft + 通顶 bore cut）[+ slab/round-to-flat/cyl/oval/cone 截面 mesh][+ closure 派生的 shoulder/neck/nozzle 顶口几何 visual] | P1 `_tube_body` L71-97 / P2 `_body_solid`+`_body_mesh` L51-128 |
| internal joints | 无（root 管体本身无活动件）| — |
| upstream interface | 坐地 z=0（root，底压缝/软底）| P1 BODY_BOTTOM_Z L37 |
| downstream interface | 顶口/肩面/锥嘴 base/球座 rim/管底（closure joint 的 parent 接口，按 closure 派生）| P2 NOZZLE_TOP_Z L38 |

### Slot B / closure_mechanism（每候选发射对应活动分配头，挂 tube_body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | lift_cap / cap(+massless cap_carrier) / flip_cap / pull_cap / flip_lid(+base_cap 固定 visual) / snap_cap / applicator_ball+overcap / twist_ring+platform | 各 closure 源 |
| internal joints | `cap_lift` PRISMATIC +Z（lift）/ `cap_rotate` CONT +Z + `cap_slide` PRIS +Z（screw）/ `flip_cap` REVOLUTE +X（flip）/ `cap_pull` PRIS +Z（pull）/ `lid_hinge` REVOLUTE -Y（standup）/ `cap_pull` PRIS +Z（slant_applicator）/ `ball_roll` CONT +X + `overcap_lift` PRIS +Z（roller）/ `body_to_twist_ring` CONT +Z + `twist_ring_to_platform` PRIS +Z（twist）| P1 L212-222 / P2 L246-263 / flip L286-297 / pull L220-230 / standup L374-384 / slant L330-341 / roller L296-320 / twist L290-317 |
| 固定 visual | standup 的 `base_cap_disc`/`orifice_ring`/`hinge_barrel`/`grip_bump_{i}` 挂 tube_body（无独立 joint）；twist 的 `mouth_rim` 顶口环 | standup L189-352 / twist L107-127 |

## Appearance-only families（③/④/⑥，不进 slot_choices）

- `body_profile_style`：在同一 `body_footprint` 内再分 straight / waisted / bulged 三种轮廓原型；只改 loft control levels，不改 neck datum、joint origin 或 closure 接口。
- `graphics_style`：front_panel / vertical_stripe / dual_stripe / wrap_band / none。实现上必须先解 ③ shape 与 ⑤ dims，再从最终 body profile 采样 `surface(z)` 做 overlay shell，保证 decoration 共形贴合，不再允许常数半径整圈套筒。
- `tail_detail_style`：plain / single_crimp / double_crimp。只作用于底部压缝视觉语言，保持 z=0 坐地与宽扁压缝身份。
- `closure_trim_style`：plain / single_band / double_band / ribbed。只给 cap / lid / base_disc / twist_ring 外壳增加握持或装饰层，不改变关节类型、轴向或行程。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_footprint | enum | slab_rect / round_to_flat / cylindrical / oval_lozenge / tapered_cone | slab_rect | choice | deterministic procedural sampler 选 | Slot A 表 |
| body_profile_style | enum | straight / waisted / bulged | straight | shape-family | appearance-only；只改 body loft profile，不进 `slot_choices` | Appearance-only families |
| closure_mechanism | enum | lift_cap / screw_cap / flip_top / pull_cone / standup_flip_cap / slant_applicator / roller_ball / twist_up_stick | lift_cap | choice | sampler 选 | Slot B 表 |
| graphics_style | enum | front_panel / vertical_stripe / dual_stripe / wrap_band / none | front_panel | decoration | appearance-only；由最终 body surface 派生 overlay shell，不进 `slot_choices` | Appearance-only families |
| tail_detail_style | enum | plain / single_crimp / double_crimp | single_crimp | decoration | appearance-only；只改底部压缝视觉，不改坐地 / cavity / joint | Appearance-only families |
| closure_trim_style | enum | plain / single_band / double_band / ribbed | plain | decoration | appearance-only；cap/lid/ring 外壳 trim，不改 articulation type / axis / limits | Appearance-only families |
| palette_style | enum | blue_sunscreen / pale_yellow_cream / white_minimal / teal_serum / orange_glue / steel_rollon / pearl_blush_cosmetic / bare_aluminum_glue / charcoal_softtouch_twotone / mint_translucent_gel | blue_sunscreen | palette | palette only（含 material-finish 维：glossy-laminate / matte / pearlescent / metallic-laminate / bare-aluminum / soft-touch / translucent / two-tone），**不计入 slot_choice**；按 seed `rng.choice` | §palette |
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放管身高 H（BODY_TOP_Z / SHOULDER / NOZZLE 链派生）→ closure mount 高度，clamp | resolve clamp |
| body_radius_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放管身半径/半宽（TUBE_HALF_W·HALF_T / BODY_MAX_R / CRIMP），clamp（保压缝扁平比）| resolve clamp |
| neck_radius_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK/NOZZLE_R = base · neck_radius_scale`；cap bore / skirt / 锥嘴 / 球座半径**派生跟随**（保罩配合）| resolve clamp |
| closure_size_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放盖高/skirt 深/锥嘴长/球径/底盘径/平台行程，clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 cap_lift/cap_slide/cap_pull/overcap_lift/platform 行程 + hinge limit，clamp | resolve clamp |
| crimp_flat_ratio | float | derived | — | equation | `CRIMP_HALF_W ≥ CRIMP_HALF_T · 4`（压缝扁平：宽≥4×厚），仅 round_to_flat/tapered_cone | conditional on footprint |
| (—) | constraint | — | — | inequality | 盖罩配合：`cap_bore_R ≥ closure_neck_R + clearance` 且 `cap_outer_R ≤ body_R + proud`；twist `platform_R < cavity_R − clearance` 且 `platform 满行程 ≤ BODY_TOP_Z`；违反按比例回缩 closure_size/neck/travel scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | slant_applicator 的嘴体正轴、仅口沿斜切；standup base_cap_R 与 footprint 顶口正交但需 `base_cap_R > body_R`（站立稳定）；twist 机构挂管底（顶口仅 mouth_rim）| Slot B 表 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（cap bore / skirt / 锥嘴 / 球座半径派生跟随 neck/nozzle 半径，保盖罩配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_footprint / closure_mechanism 的拓扑、joint 轴或 multiplicity。
appearance-only styles 与 `palette_style` 正交采样，但都不进入 `slot_choices`；review 时看的是“同一结构槽组合下也能明显拉开外观”。

### palette_style 配色（≥3，本类 10 档，含显式 material-finish 维；前 6 档锚定 5★ 源真实配色，后 4 档为挤压管真实推断配色）

每档 colorway = 管身 body + 盖/分配头 cap/closure + 肩部/accent shoulder/accent + print（标记/label/滚花字带）+ **finish**（material-finish 维：glossy printed laminate / matte / pearlescent / metallic-laminate / bare aluminum / soft-touch / translucent / two-tone）。finish 仅作材质语义注记（驱动 rgba 选取与 alpha；模板侧映射到材质属性），不改任何几何 / 拓扑 / joint。

| palette_style | finish | 主体 body | 盖/分配头 cap/closure | 肩部/accent shoulder/accent | print（标记/字带） | 来源样本 |
|---|---|---|---|---|---|---|
| blue_sunscreen | glossy printed laminate（高光印刷复膜，最常见牙膏/防晒管面）| 浅蓝 (0.62,0.80,0.92,1.0) | 白盖 (0.95,0.96,0.97,1.0) | 浅蓝肩同 body / 白肩 (0.95,0.96,0.97,1.0) | 白 label/brand-mark (1.0,1.0,1.0,1.0) | P1 `60b00467` L169-171 / lift·flip·pull·twist |
| pale_yellow_cream | matte（哑光无光复膜，化妆膏管面）| 淡黄膏 (0.93,0.89,0.66,1.0) | 白盖 (0.96,0.96,0.95,1.0) | 灰银 shoulder/accent (0.78,0.80,0.82,1.0) | 灰银印字同 accent (0.78,0.80,0.82,1.0) | P2 `7c11d416` L213-215 / tapered_cone |
| white_minimal | matte（极简白哑光，无印刷或浅灰印字）| 白身 (0.96,0.96,0.95,1.0) | 白盖 (0.94,0.94,0.93,1.0) | 灰 grip/accent (0.82,0.82,0.80,1.0) | 灰印字 (0.82,0.82,0.80,1.0) | standup `cap_white`/`grip_grey` L307-310 |
| teal_serum | glossy printed laminate（高光青绿印刷，精华/眼霜杆）| 淡黄膏身 (0.93,0.89,0.66,1.0) | 青绿盖 (0.30,0.58,0.62,1.0) / 浅青 (0.55,0.78,0.78,1.0) | 银 shoulder/accent (0.72,0.76,0.78,1.0) | 银印字 (0.72,0.76,0.78,1.0) | slant `teal_cap` L284 / standup `lid_teal` L309 |
| orange_glue | glossy printed laminate（高光橙印刷，胶水/强力胶管）| 浅蓝/白身 (0.62,0.80,0.92,1.0) | 橙盖 (0.95,0.65,0.25,1.0) | 白肩/accent (1.0,1.0,1.0,1.0) | 白 label (1.0,1.0,1.0,1.0) | pull_cone `cap_orange` L178 |
| steel_rollon | metallic-laminate body + translucent overcap（金属镀膜身 + 半透盖，滚珠走珠瓶）| 淡黄膏身 (0.93,0.89,0.66,1.0) | 钢球 (0.72,0.73,0.75,1.0) + 半透 overcap (0.88,0.92,0.95,**0.85**) | 钢色 housing/accent (0.72,0.73,0.75,1.0) | 红 marker print (0.85,0.25,0.20,1.0) | roller `steel_ball`/`overcap_tint`/`ball_marker` L263-265 |
| pearl_blush_cosmetic | pearlescent（珠光复膜，高端化妆精华管，珠光偏粉）| 珠光粉 (0.95,0.84,0.86,1.0) | 玫瑰金盖 (0.86,0.70,0.62,1.0) | 浅珠白肩/accent (0.97,0.93,0.92,1.0) | 玫瑰金印字 (0.86,0.70,0.62,1.0) | 推断（pearl 化妆管；锚 white_minimal 白系 + 粉珠光）|
| bare_aluminum_glue | bare aluminum（裸铝管无复膜，油画颜料/工业胶/药膏铝管）| 裸铝身 (0.80,0.81,0.83,1.0) | 白盖 (0.94,0.94,0.93,1.0) | 铝灰肩/accent (0.72,0.73,0.75,1.0) | 黑印字 print (0.15,0.15,0.15,1.0) | 推断（裸铝挤压管；锚 steel `steel_ball` 0.72,0.73,0.75 金属灰）|
| charcoal_softtouch_twotone | soft-touch + two-tone（哑触感橡胶漆磨砂身 + 上下分色，男士护理/精华管）| 炭灰软触身 (0.22,0.23,0.25,1.0) / 上半 暖棕 (0.46,0.36,0.28,1.0)（two-tone 双段） | 炭灰盖 (0.18,0.19,0.21,1.0) | 哑黑肩/accent (0.13,0.13,0.14,1.0) | 暖铜印字 print (0.72,0.52,0.34,1.0) | 推断（soft-touch 橡胶漆 + 上下 two-tone 男士护理管；锚 white_minimal 反相暗系）|
| mint_translucent_gel | translucent（半透薄荷凝胶管，可见膏体，body 带 alpha）| 半透薄荷 (0.70,0.92,0.82,**0.72**) | 白盖 (0.95,0.96,0.97,1.0) | 半透青肩/accent (0.62,0.86,0.80,**0.72**) | 深绿印字 print (0.18,0.45,0.36,1.0) | 推断（translucent 凝胶管；锚 roller overcap alpha 0.85 风格 + teal 青系）|

palette_style 仅改材质 rgba + finish 语义（含 steel_rollon 半透 overcap alpha 0.85、mint_translucent_gel body/shoulder alpha 0.72），不改任何几何 / 拓扑 / joint，**不计入 slot_choice**；按 seed `rng.choice` 采样，与 footprint/closure 正交。translucent 档携 alpha<1（body/overcap），metallic-laminate / bare-aluminum 为不透明金属灰/金 rgba（finish 注记驱动模板侧材质语义，spec 层仅记 rgba + finish）。

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots（body_footprint + closure_mechanism）表达，不暴露 `*_count`，也不通过循环复制模板级身份 visual/part/joint。单管单分配头。
- 现有 for 循环发射件均为**装饰/握持细节带**，非身份级 N 轴，故不设 multiplicity：
  - `vertical_brand_mark_{i}`(8) / `small_front_label_{i}`(3) label 带（P1/oval/flip/pull/twist）；
  - `_nozzle_mesh` 螺纹环 k 循环(4)（P2/standup/slant…）；
  - `_cap_mesh` 滚花筋 i 循环(18)（P2）；
  - standup `grip_bump_{i}`(8)、slant `grip_rib_{i}`(12)、twist knurling fins(12)。
  - 这些可作模板侧**连续/装饰参数**（rib/fin/mark 密度，固定或小范围 clamp），不编进 `slot_choices`，不改拓扑等价类。
- N 样本已覆盖：无（不以 N 作轴）。模板建议 N_range：无身份级复制件。
- copied object / naming / placement / joint policy：无（无需 copy-logic module）。

## 拓扑多样性审计

总组合数：body_footprint(5) × closure_mechanism(8) = **40**。

仅 body_footprint × closure_mechanism = **40 ≥ 10** 已充裕过门控（无第三轴；palette_style 是 palette 不计）。

理由：本类拓扑多样性来源充裕——5 body × 8 closure 的笛卡尔积即 40 distinct，远超 10；closure 引入 PRISMATIC(+Z) / CONTINUOUS+PRISMATIC(screw 2 joint + massless carrier) / REVOLUTE +X(flip) / PRISMATIC(pull) / REVOLUTE -Y(standup, base 固定+翻盖) / PRISMATIC 斜轴(slant) / CONTINUOUS +X 球 + PRISMATIC +Z overcap(roller 2 活动件) / CONTINUOUS +Z → PRISMATIC +Z 链式(twist 2 joint 耦合) 等五种以上 joint 拓扑 + 不同 part count + 不同挂载点，是真实结构差异，非缩放/配色。body_footprint 改 root mesh 的截面 loop 家族（slab/round-to-flat/cyl/oval/cone）。slot_choices 编入两轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（笛卡尔积近全合法，少量尺寸派生见兼容表），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 处理跨轴尺寸派生（见下表），无硬 gate-out（40 组合全合法，仅在 resolve 派生尺寸适配）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9（重点核 closure 动作姿态 + 坐地 + 盖罩 overlap）。

Topology target：1000-seed slot choice tuple distinct 预计接近 40（40 组合即该类真实结构词汇上限：5 截面家族 × 8 分配机构）。低于 300 的原因：本小类真实结构词汇就是 body_footprint(5) × closure(8) = 40，是该类目合理上限（squeeze tube 是单口分配软容器，身份在两根轴），不强行注水；40 远超 ≥10 机械门槛且 closure 轴 joint 拓扑差异极丰富。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 6 个 scale（body_height / body_radius / neck_radius / closure_size / joint_travel + crimp_flat_ratio 派生）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（cap bore / skirt / 锥嘴 / 球座半径派生跟随）。盖罩配合 / platform-bore / 站立稳定不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（neck base / nozzle top / 锥嘴 base / 后 rim hinge / 盘顶 hinge / shoulder 斜轴 / 球心 / housing rim / 管底）、盖罩配合、坐地或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含两轴且与 build 一致 |
| compatibility matrix | (1) closure 各候选互斥（一次一种分配头）。(2) round_to_flat/tapered_cone 强制 `CRIMP_HALF_W ≥ 4·CRIMP_HALF_T`（压缝扁平）；cylindrical 强制 X≈Y；slab/oval 强制 Y 宽 X 薄；resolve 按 footprint 设截面比。(3) closure 顶口几何按 footprint 顶口半径在 resolve 派生（neck/nozzle/锥嘴/球座/shoulder R 跟随 body 顶口）。(4) slant `cap_pull` axis=TIP_AXIS（非 +Z，θ 派生）；standup `base_cap_R > body_R`（站立稳定）；twist 机构挂管底+腔内（顶口仅 mouth_rim），`platform_R < cavity_R − clearance` 且满行程 ≤ BODY_TOP_Z。(5) roller / twist 为 2 活动件，各 joint 独立 clamp。无硬 gate-out（40 组合全合法，仅 resolve 派生尺寸适配）| 无 floating / collision / 盖穿管壁 / joint 轴或 origin 错位 / platform 出顶口 / base_cap 不稳 |
| controlled local variation | 6 个 clamped scale，每 build 统一；neck_radius equation 驱动 cap bore/锥嘴/球座；装饰带 (mark/rib/fin) 密度固定或小 clamp | 比例变化不破坏 closure joint origin / 盖罩配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_footprint | 5 | yes | yes | slab / round-to-flat / cylindrical / oval_lozenge / tapered_cone，loft 截面家族 |
| closure_mechanism | 8 | yes | yes | lift(PRIS) / screw(CONT+PRIS+carrier) / flip(REV +X) / pull(PRIS) / standup(REV -Y+固定盘) / slant(PRIS 斜轴) / roller(CONT +X 球+PRIS overcap) / twist(CONT +Z→PRIS 链式) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_footprint, closure_mechanism) 两轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 cap bore/锥嘴/球座；盖罩配合 / platform-bore / 站立稳定 / 压缝扁平不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：40 组合全合法（无硬 gate-out），closure 顶口几何按 footprint 顶口半径在 resolve 派生
- 连续 scale clamp 后不破坏 closure joint origin / 盖罩配合 / 坐地 / 类别身份
- 关键 joint：lift `cap_lift` PRISMATIC +Z；screw `cap_rotate` CONTINUOUS +Z (abs(axis[2])>0.99) + `cap_slide` PRISMATIC +Z + massless `cap_carrier`（无 visual）；flip `flip_cap` REVOLUTE +X (abs(axis[0])>0.9, axis[2]≈0)；pull `cap_pull` PRISMATIC +Z；standup `lid_hinge` REVOLUTE 水平 (abs(axis[2])<0.01) + base_cap 固定 visual；slant `cap_pull` PRISMATIC axis=TIP_AXIS(非 +Z)；roller `ball_roll` CONTINUOUS +X + `overcap_lift` PRISMATIC +Z（双活动件）；twist `body_to_twist_ring` CONTINUOUS +Z + `twist_ring_to_platform` PRISMATIC +Z (parent=twist_ring 链式)
- captured-fit：element-scoped `allow_overlap`（盖罩 neck/nozzle/锥嘴/housing；ball ↔ socket；platform ↔ bore；base_cap ↔ nozzle；twist ring flange ↔ body bottom）
- grandfather：盖罩 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- 装饰带 (mark/rib/fin) 密度参数 clamp，不编进 slot_choices，不改拓扑等价类

## Reject cases

- 用 boxy 占位体（纯 Box）当软管 body → 失类别身份；body 必须 `loft` 中空 shell（rounded-rect/椭圆/超椭圆截面），软底/压缝坐地 z=0。
- closure joint origin 放在管底/任意点而非真实硬件（neck base / nozzle top / 锥嘴 base / 后 rim hinge / 盘顶 hinge barrel / shoulder 斜轴 / 球心 / housing rim / 管底旋环）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- screw 盖不用 massless carrier 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 cap 单 part → 旋转与抬升耦合错误（应 body→carrier→cap 两 joint）。
- twist platform 不设为 twist_ring 的 child（链式耦合）或升过顶口穿出 → 机构语义错 / platform 出 bore，`expect_within` FAIL。
- slant `cap_pull` 用 +Z 轴而非 TIP_AXIS 斜轴 → 盖不沿斜嘴轴拔出，穿模 / 轴错。
- closure rest pose 设成全张开/抬起而非 closed/seated（twist 为 retracted）→ current-pose 与 viewer 目检不符。
- 给盖罩 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质 / 装饰带密度当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette、mark/rib/fin 是装饰参数，均不计 slot_choice）。
- 盖抬升/翻起/拔出/球旋/平台升时穿管壁 / origin 漂移 → 盖罩配合不等式或 origin 检查 FAIL。
- 把 round_to_flat/tapered_cone 的扁压缝做成圆底（CRIMP 宽≈厚）→ 失挤压管身份；压缝必须 wide·thin（宽≥4×厚）。

## 与相邻类别的边界

- 不该混入：**container_bottle 硬体细颈瓶 / 酒瓶**——理由：bottle 是硬壁直立瓶身 + 长颈，tube 是软挤压壁、底压缝/软底坐地、肩部收口出细分配嘴；squeeze 软身 + crimped tail 是 tube 身份标记。
- 不该混入：**container_cosmetic 宽口膏霜罐 / lidded jar**——理由：jar/cosmetic 罐是宽口罐身 + 盘盖/旋盖罩整口，tube 是细口分配嘴（nozzle/锥嘴/球座/翻盖 orifice）+ 软挤压身。
- 不该混入：**container_lipstick 口红/唇膏旋管**——理由：口红身份是裸露膏体从硬套筒顶口旋出（无软挤压身、无分配嘴）；本类 twist_up 候选虽含底旋升膏平台机构，但挂在软挤压管身、为护理膏/止汗棒/护手膏语义（腔内平台 + 软身 + 顶口环），非口红裸膏套筒。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。逐一全读 11 样本（2 parent + 9 variant）。body_footprint(5) × closure_mechanism(8) = 40 combos（≥10 充裕）；closure 轴含 PRIS/CONT+PRIS+carrier/REV+X/REV-Y/PRIS 斜轴/CONT+X 球+PRIS overcap(双活动件)/CONT+Z→PRIS 链式 五种以上 joint 拓扑。palette_style 10 档（前 6 档锚 5★ 真实配色含 roller 半透 overcap；后 4 档 pearl_blush_cosmetic/bare_aluminum_glue/charcoal_softtouch_twotone/mint_translucent_gel 为挤压管真实推断配色），含显式 material-finish 维（glossy-laminate/matte/pearlescent/metallic-laminate/bare-aluminum/soft-touch/translucent/two-tone 8 种全覆盖），translucent（mint body/shoulder alpha 0.72 + roller overcap alpha 0.85）携 alpha，palette only 不计 slot_choice。无 multiplicity 轴（label/螺纹环/滚花筋/grip/fin 为装饰带参数）。每候选有真实 `model.py:Lx-Ly` + 命名 part/joint/helper。待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_loft_body(levels_or_loop, footprint)` 统一发射五种截面 body（slab 用超椭圆 `_oval_loop` p=3.4；oval 用纯椭圆 cos/sin；cylindrical 用 circle extrude+底 taper；round_to_flat 用 `_rounded_rect_pts` levels loft；tapered_cone 用 `_taper_levels` sqrt-ease 单调收窄 + `_loft_from_levels`）+ 内 loft cut shell 中空 + 通顶 bore；`_rounded_rect_pts` / `_oval_loop` / `_taper_levels` 全 footprint 公用。
- screw：必须经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial）解耦 `cap_rotate`(CONTINUOUS +Z)→`cap_slide`(PRISMATIC +Z)。twist：`twist_ring_to_platform` 的 parent 必须是 `twist_ring`（不是 body），链式耦合底旋→腔内升。roller：`ball_roll`(CONTINUOUS +X) 与 `overcap_lift`(PRISMATIC +Z) 两独立活动件均挂 tube_body。
- captured-fit overlap：`run_container_tube_tests` 里按 closure 复制各样本的 `ctx.allow_overlap`（盖 shell ↔ neck/nozzle/锥嘴/applicator_tip/housing；ball ↔ housing_socket；overcap ↔ housing/ball；platform ↔ tube_body bore；twist ring_shell ↔ tube_body；base_cap flip_lid ↔ base_cap_disc）；slant cap visual 带 `rpy=(0,TIP_ANGLE,0)` tilt。
- neck_radius equation：`resolve_config` 派生 `cap_bore_R = closure_neck_R + clearance`、`cap_outer_R = body_R + proud`、锥嘴/球座/shoulder R 跟随 body 顶口；盖罩配合 / platform-bore / 站立稳定不等式在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（最近邻：parallel_children 固定 named slot + body/closure 双轴 + screw massless carrier + flip REVOLUTE + 多 closure 分支 + captured-fit allow_overlap + 装饰非 multiplicity 的同款骨架）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig dataclass + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + element-scoped grandfather 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | slab_rect + lift_cap | rec_…_60b00467（P1）| `_oval_loop` L51-64 / `_loop_xy` L67-68 / `_tube_body` L71-97 / `_open_neck` L100-125 / `_cap` L128-163 / `cap_lift` PRISMATIC L212-222 | slab 超椭圆 body 基线 + 垂直升降盖机构 |
| S2 | A/B | round_to_flat + screw_cap | rec_…_7c11d416（P2）| `_body_solid` L51-80 / `_rounded_rect_pts` L83-100 / `_body_mesh` L103-128 / `_shoulder_mesh` L131-155 / `_nozzle_mesh` L158-179 / `_cap_mesh` L182-207 / massless `cap_carrier` L227-228 / `cap_rotate` CONT + `cap_slide` PRIS L246-263 | round-to-flat 挤压管 body 基线 + 双解耦螺旋盖 + massless carrier |
| S3 | A | cylindrical | rec_container_tube_var_cylindrical | `_tube_body`(circle extrude+底 taper+cavity) L53-82 / `_open_neck` L85-110 | 等径圆直筒 barrel body |
| S4 | A | oval_lozenge | rec_container_tube_var_oval_lozenge | `_oval_loop`(纯椭圆) L53-63 / `_loop_xy` L66-67 / `_tube_body` L79-105 | 软扁椭圆/lozenge body |
| S5 | A | tapered_cone | rec_container_tube_var_tapered_cone | `_taper_levels` L58-74 / `_loft_from_levels` L96-110 / `_body_solid` L113-117 / `_body_mesh` L120-136 | 单调收锥/漏斗 body |
| S6 | B | flip_top | rec_container_tube_var_flip_top | `_open_neck_with_hinge` L108-146 / `_flip_cap_lid` L149-225 / `flip_cap` REVOLUTE axis=(1,0,0) L286-297 | 颈口后铰翻盖（living-hinge）|
| S7 | B | pull_cone | rec_container_tube_var_pull_cone | `_nozzle_tip`(锥嘴+bore) L113-142 / `_pull_cap`(hollow 锥) L145-171 / `cap_pull` PRISMATIC +Z L220-230 | 尖锥分配嘴 + 拉拔盖 |
| S8 | B | standup_flip_cap | rec_container_tube_var_standup_cap | `_base_cap_mesh` L189-213 / `_orifice_ring_mesh` L221-229 / `_hinge_barrel_mesh` L232-240 / `_flip_lid_mesh` L255-300 / `lid_hinge` REVOLUTE axis=(0,-1,0) L374-384 | 八角站立底盘盖(固定)+小翻盖 |
| S9 | B | slant_applicator | rec_container_tube_var_slant_applicator | `_applicator_tip_mesh`(斜切嘴) L194-240 / `_snap_cap_shell_mesh` L247-272 / `_grip_rib_solid` L96-104 / `cap_pull` PRISMATIC axis=TIP_AXIS L330-341 | 斜切涂抹嘴 + 斜轴拔盖 |
| S10 | B | roller_ball | rec_container_tube_var_roller_ball | `_housing_mesh`(球座) L166-203 / `_ball_mesh` L206-219 / `_overcap_mesh` L234-255 / `ball_roll` CONTINUOUS +X L296-304 / `overcap_lift` PRISMATIC +Z L310-320 | 球座滚珠涂抹头(滚动关节)+overcap（双活动件）|
| S11 | B | twist_up_stick | rec_container_tube_var_twist_up | `_mouth_rim` L107-127 / `_twist_ring` L130-179 / `_platform_disk` L182-203 / `body_to_twist_ring` CONT +Z L290-298 / `twist_ring_to_platform` PRIS +Z(parent=ring) L304-317 | 旋底升膏平台机构（链式 2 joint）|
