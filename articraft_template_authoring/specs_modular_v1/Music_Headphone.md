# Over-Ear Headphones Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `over_ear_headphones` |
| template path | `agent/templates/Music_Headphone.py` |
| test path (optional) | `tests/agent/test_over_ear_headphones_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：根 `band`（头梁，root）下挂左右**镜像对称**两条相同子链 —— 每侧 `band → {side}_slider`（PRISMATIC 伸缩调节）→ `{side}_yoke`（Slot D 决定 FIXED/REVOLUTE/无）→ `{side}_cup`（REVOLUTE 耳倾仰）。cup 后盖（Slot B）与 cup 外形（Slot A）是 cup part 上的 module-local 几何/visual；headband 形态（Slot C）可改写 root part 本体并可加 1 个 PRISMATIC 悬带子件；vent_count 是 cup 后盖上的 module-level visual 复制轴（仅 vented-grille 后盖）。固定 named slots（cup 恒为 ×2，是耳机定义而非可变 N），叠加 1 根 vent_count multiplicity 轴。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category: `model.py` 全文逐行已读（parent + 9 variants） |
| samples_adopted_as_module_sources | 10 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

10 个 5★ 样本（1 parent + 9 variant，全部 compile=success、workbench-only、≥1 非 fixed joint、仍明确读作 over-ear 耳机）逐条阅读摘要：

- **S1 `rec_over-ear-headphones-with-padded-leather-ear-cups_20260609_080248_682174_5669f0bd`** — 全批 fork 母资产，**四 slot 全部基线**。root `band`（`_band_shell_mesh` 单条实心弧带 L80-87 + `_crown_pad_mesh` 皮质 crown pad L90-100 + `housing_l/r` 套筒 visual L103-108/L195-197）。每侧链：`band_to_{slider}` PRISMATIC axis (0,0,-1) 0→`SLIDER_TRAVEL=0.022`（L208-227），`{slider}_to_{yoke}` **FIXED**（L230-242），`{yoke}_to_{cup}` **REVOLUTE** +X ±0.44 耳倾仰（L244-268）。cup 外形=圆鼓 `_cup_shell_mesh`（drum `CylinderGeometry` + 浅球冠 `SphereGeometry` scale y 0.28 dome，L144-161），后盖=封闭实心 dome（dome 段 L156-159），TorusGeometry ear-pad（L171-175）。可读性契约样板：`for side, sl_nm, yk_nm, cp_nm in (...)` 镜像发射 + 显式 captured-pin `allow_overlap`（slider↔band housing / yoke↔slider / cup↔yoke clevis）+ cup 在 band crown 之下。

- **S2 `rec_over_ear_headphones_var_cup_oval`** — Slot A `vertical_oval`。`CUP_RX=0.034 < CUP_RZ=0.046`（高>宽，L62-66）；`_cup_shell_mesh` 改用 `superellipse_profile + ExtrudeGeometry` 椭圆鼓（L148-166），dome 椭圆缩放（`scale(CUP_RX/CUP_RZ, 0.28, 1)`），inner cap/ear-pad 椭圆化（L169-186）。run_tests 显式断言 `cup_dz > cup_dx*1.15`（L315-321）。骨架/关节与 S1 同。

- **S3 `rec_over_ear_headphones_var_cup_rounded_rect`** — Slot A `rounded_rect`。新 helper `_rounded_rect_cup_body()`（`rounded_rect_profile + ExtrudeGeometry`，`CUP_W=0.076 CUP_H=0.088 CUP_FILLET=0.018`，L143-156）；`_cup_shell_mesh` 圆角矩形本体 + raised panel（L159-181）；ear-pad 用 `tube_from_spline_points` 沿圆角矩形轮廓闭合扫掠（L198-212）。run_tests 断言 rounded-rect footprint（dz>dx、宽度≈CUP_W、pad 非圆，L341-358）。骨架/关节同 S1。

- **S4 `rec_over_ear_headphones_var_back_vented_grille`** — Slot B `open_back_vented_grille`（钻孔板实现）。model 名 `open_back_headphones`（L219）；`_cup_shell_mesh` 去 dome 仅 drum（L152-158）；`_vented_back_plate_mesh` 用 `ExtrudeWithHolesGeometry`（中心孔 + `VENT_COUNT=8` 孔环，L184-199）+ 每孔 `_vent_rim_mesh` torus 缘（L202-213）；cup visual `{cp}_grille` + `for i in range(VENT_COUNT)` 发 `{cp}_vent_{i}`（L283-298）。run_tests 断言 back-plate 凸出 drum + 每 cup 恰 VENT_COUNT 个 vent rim + grille visual 存在（L382-419）。

- **S5 `rec_over_ear_headphones_var_grille_vent_count`** — Slot B `open_back_vented_grille`（径向肋实现，**vent_count multiplicity 权威源**）。`VENTS_PER_CUP=8`（L68，注释「clearly ≠ 12」）；drum-only shell（L146-151）+ 固定框架 `_grille_ring_mesh`（torus 边框 L154-159）+ `_grille_hub_mesh`（中心 hub 盘 L162-167）+ 单根 `_vent_slot_mesh` 径向肋 `BoxGeometry`（L170-181）；`for i in range(VENTS_PER_CUP)`：`rib.rotate_y(2π·i/N)` 均布后 `translate(0, side·CUP_HD, −CUP_R)` 贴后盖中心，命名 `{cp}_vent_{i}`，left/right 各一份（L273-279）。run_tests 断言每 cup vent 数==VENTS_PER_CUP、ring/hub 存在、`VENTS_PER_CUP != 12`（L367-385）。

- **S6 `rec_over_ear_headphones_var_back_exposed_driver`** — Slot B `exposed_driver_behind_ring`。drum-only shell（L145-150）+ `_back_ring_mesh`（外保护环 torus L153-158）+ `_grille_bars_mesh`（**固定 3 根**径向支条 L161-173）+ `_driver_cone_mesh`（露出驱动单元锥 `ConeGeometry` L176-185）+ `_dust_cap_mesh`（中心防尘帽半球 L188-193）；新增 material `cone_mat`/`cap_mat`（L219-220）；cup visuals `{cp}_ring/bars/driver/dustcap/innercap/pad`（L279-296）。run_tests 断言 ring 凸出 cup、driver 凹陷在 ring 之后、dust cap 在 ring 内、shell 在 Y 向薄（无 dome，L393-434）。骨架/关节同 S1。

- **S7 `rec_over_ear_headphones_var_band_twin_rods`** — Slot C `twin_parallel_rods`。`ROD_RADIUS=0.0025 ROD_SPACING=0.018`、`HOUSING_W` 加宽到 0.028（L29-40）；`_rod_arc_path(x_offset)` + `_band_rod_mesh`（细圆钢丝弧杆 tube L75-93）；root `band` 发 `band_rod_0/1`（`for i,x_off in (-S/2, S/2)`，`polished_steel` 材质，X 分离）+ `band_pad` + `_rod_clip_mesh`（夹片 stem+clamp ring 把 crown pad 连到两杆 L109-125）+ housing（L214-235）。run_tests 断言 twin rod visuals 存在、X 分离>0.010、同 Y 弧、细 wire（L338-363）。每侧链/cup 关节同 S1。

- **S8 `rec_over_ear_headphones_var_band_suspension_strap`** — Slot C `suspension_strap_under_arch`（⚠ 改写 root + 加 PRISMATIC 子件）。root 部件**更名 `band`→`arch`**（`_arch_mesh` 薄扁弹簧钢外弧 `arch_frame` L89-97/L220-223）；**新增 part `suspension_strap`**（`_strap_mesh` 沿 catenary `_strap_arc_path` 下垂 L100-122，`strap_body`，leather_tan）；**新增 joint `arch_to_strap` PRISMATIC** axis (0,0,-1) 0→`STRAP_DROOP=0.008`（下垂调节 L246-258）；`_strap_clip_mesh` 端部夹片（L125-130）；每侧 prismatic 改名 `arch_to_{slider}`（L274-284）。run_tests 断言 arch 顶与 strap 顶之间可见 sag gap≥0.008、strap 端连 arch、droop joint 下移 strap、strap 与 arch 同 Y 宽（L348-375）。cup 关节同 S1。

- **S9 `rec_over_ear_headphones_var_attach_single_pivot`** — Slot D `single_pivot_hanger`（⚠ 删 yoke，改 part 树 + 关节拓扑）。**无 yoke part**；`_hanger_arm_mesh`（细吊臂 BoxGeometry + 横向 pivot post `CylinderGeometry` 沿 X，L115-135）inline 为 slider visual `{sl}_arm`（L205-210）；part 改名 `slider_{i}`/`cup_{i}`（`for i in range(2): side=1-2*i`，L199-202）；`band_to_slider_{i}` PRISMATIC（L216-226）；**`slider_{i}_to_cup_{i}` REVOLUTE** 直连 +X ±0.44，origin `(0,0,SLIDER_BOT_Z−ARM_H=−0.060)`（slider→cup 取代「FIXED+REVOLUTE」对，L242-252）。run_tests 显式断言 `not any("yoke" in n)`、pivot 在 cup top edge、cup 单 pivot 倾仰（L271-305）。captured-pin overlap element-scoped 到 `slider_i_arm`（L332-337）。

- **S10 `rec_over_ear_headphones_var_attach_folding_hinge`** — Slot D `collapsible_folding_hinge`（⚠ slider↔yoke 接口由 FIXED 升级为折叠 REVOLUTE）。保留 yoke + `_hinge_barrel_mesh`（X 轴 knuckle barrel `{yk}_hinge` visual L149-154/L246-247）；**`{slider}_to_{yoke}` 由 FIXED 改 REVOLUTE**：`fold_axis=(−side,0,0)`，range 0→`FOLD_UPPER=1.50`（≈86° 内折向头梁，L251-264）；`{yoke}_to_{cup}` 仍 REVOLUTE +X ±0.44 倾仰（L280-290）。每侧两个 revolute（fold + tilt）。run_tests 断言 cup 折向 Y=0、fold 抬高 cup z、tilt 仍可动（L358-375）。

跨样本观察：10 样本共享 `band` root + `band_to_slider` PRISMATIC（伸缩）+ `yoke→cup`（或 `slider→cup`）REVOLUTE（耳倾仰）+ 镜像 `for side ... (left/right)` 发射 + captured-pin `allow_overlap`（slider↔housing / yoke↔slider / cup↔yoke 或 cup↔arm）+「cup 在 band crown 之下」「slider top 永驻 housing 内」契约。差异严格落在四轴：**(A) cup 外形**、**(B) cup 后盖样式**、**(C) headband 形态**、**(D) cup↔band 连接的关节拓扑**，外加 **(N) vented 后盖通风条数**。配色基线高度一致（gunmetal band / 近黑 leather pad / metal_dk slider+yoke / shell_lt 浅银 cup），变体引入 polished_steel / leather_tan / brushed_steel / cone_mat 等，为 §7 `palette_style` 提供基线 + 可派生 colorway。

## 核心身份

Over-ear（circumaural）耳机：**头梁（headband）** 经左右**镜像对称两侧伸缩臂**吊住**两只完全包耳的耳罩（ear cup）**，每只 cup 含驱动腔 + 环形海绵/皮 ear-pad（pad 内圈大于耳廓，**整圈包住耳朵**）。世界系约定：+Z 向上（band crown 在最高 z=`BAND_APEX_Z≈0.102`），+Y / −Y 为左右两耳（cup 在 ±Y≥0.04），cup 沿头梁 leg 端点向下悬挂、位于 crown 之下；cup 轴沿 ±Y（drum `CylinderGeometry` 轴 Y），后盖朝外（±Y outboard），ear-pad 朝内（−side，贴耳）。

成熟域：经典可调头梁 over-ear 耳机，含 root 头梁（实心弧带 / 双钢丝 / 悬带式外弧）+ crown pad、左右 PRISMATIC 伸缩 slider（戴合尺寸调节）、cup↔band 连接机构（双叉 gimbal / 单 pivot / 折叠铰链）、cup 倾仰 REVOLUTE、cup 外形（圆 / 椭圆 / 圆角矩形）、cup 后盖（封闭 dome / 开放通风栅 / 露出驱动）、环形 ear-pad。身份强约束：

- **必须**恰好 2 只镜像对称包耳 cup（不是 1 只、不是 3 只；左 +Y、右 −Y）。
- **必须**有 root 头梁跨接两侧 + 每侧 PRISMATIC 伸缩 slider（尺寸调节）。
- **必须**每只 cup 有 cup↔band 的**非 fixed 倾仰 REVOLUTE**（耳倾仰），cup 悬于 band crown 之下。
- **必须**环形 ear-pad 朝内贴耳、内圈包住耳廓（circumaural，pad 比耳大）；cup 有驱动腔语义（inner cap / driver / grille）。
- headband 形态、后盖样式、连接机构、外形可变（Slot A/B/C/D），但「双包耳 cup + 头梁 + 伸缩 + 倾仰」身份不可缺。

边界（不该混入）见 §11。

## 槽位 + 候选模块表

### Slot A：cup_shape（耳罩外形 — cup part 本体 + ear-pad/inner-cap 轮廓；主 footprint 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `round_drum`（基线） | S1 `rec_over-ear-headphones-...-5669f0bd` | `L60-L63`(CUP_R/DEPTH 常量)、`L144-L161`(`_cup_shell_mesh` drum+dome)、`L164-L168`(inner cap)、`L171-L175`(torus ear-pad) | eligible if compatible | 圆鼓形：`CylinderGeometry` 鼓（CUP_R=0.040）轴 Y + 浅球冠 dome；圆环 `TorusGeometry` ear-pad、圆 inner cap。footprint 各向同径。 |
| `vertical_oval` | S2 `rec_over_ear_headphones_var_cup_oval` | `L62-L70`(CUP_RX<CUP_RZ + PAD 常量)、`L148-L166`(`superellipse_profile + ExtrudeGeometry` 椭圆鼓 + 椭圆 dome)、`L169-L176`(椭圆 inner cap)、`L179-L186`(椭圆缩放 torus pad) | eligible if compatible | 竖椭圆鼓（高>宽，`CUP_RZ=0.046 > CUP_RX=0.034`，dz>dx·1.15）；dome/pad/inner-cap 椭圆缩放贴合。**mesh 生成法不同**（superellipse extrude 而非 cylinder）。 |
| `rounded_rect` | S3 `rec_over_ear_headphones_var_cup_rounded_rect` | `L55-L66`(CUP_W/H/FILLET + PAD 常量)、`L143-L156`(`_rounded_rect_cup_body` `rounded_rect_profile+ExtrudeGeometry`)、`L159-L181`(shell+raised panel)、`L184-L195`(矩形 inner cap)、`L198-L212`(沿圆角矩形轮廓闭合扫掠 pad) | eligible if compatible | 圆角矩形 studio-monitor 耳罩（`CUP_W=0.076 CUP_H=0.088 CUP_FILLET=0.018`，taller-than-wide）；ear-pad 用 `tube_from_spline_points` 沿圆角矩形轮廓闭合扫掠（非 torus）。**新 helper + 非圆 pad 拓扑**。 |

> Slot A 三候选结构差异充分：`round_drum` 是 cylinder+sphere、`vertical_oval` 是 superellipse-extrude（生成法 + 长宽比都变）、`rounded_rect` 是 rounded-rect-extrude + 非圆扫掠 pad（新 helper、非圆 pad）。三者非纯尺寸/颜色差异。

### Slot B：cup_back_style（耳罩后盖样式 — cup 后盖 visual 群 + 通风/驱动语义；与 vent_count 耦合）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `closed_solid_dome`（基线） | S1 `rec_over-ear-headphones-...-5669f0bd` | `L144-L161`(`_cup_shell_mesh`)、其中 `L156-L159`(SphereGeometry scale y 0.28 dome) | eligible if compatible | 封闭实心球冠后盖（drum + 浅 dome，**无开孔**，sealed/closed-back）。N=0（无通风条）。 |
| `open_back_vented_grille` | S5 `rec_over_ear_headphones_var_grille_vent_count`（multiplicity 权威源）；S4 `rec_over_ear_headphones_var_back_vented_grille`（钻孔板替代实现） | S5：`L68`(VENTS_PER_CUP)、`L146-L151`(drum-only shell)、`L154-L159`(grille ring)、`L162-L167`(grille hub)、`L170-L181`(单根 `_vent_slot_mesh` 径向肋)、`L273-L279`(N 复制循环)；S4：`L184-L199`(`ExtrudeWithHolesGeometry` 钻孔板)、`L202-L213`(torus vent rim) | eligible if compatible | 开放通风后盖：drum-only shell（去 dome）+ 固定框架（ring + hub）+ **N 根均布径向通风肋**（`_vent_slot_mesh`，绕 cup 轴 `rotate_y(2π·i/N)`）。**vent_count multiplicity 轴的唯一宿主**。可选钻孔板替代实现（S4）。 |
| `exposed_driver_behind_ring` | S6 `rec_over_ear_headphones_var_back_exposed_driver` | `L145-L150`(drum-only shell)、`L153-L158`(`_back_ring_mesh` 保护环)、`L161-L173`(`_grille_bars_mesh` 固定 3 支条)、`L176-L185`(`_driver_cone_mesh` 驱动锥)、`L188-L193`(`_dust_cap_mesh` 防尘帽)、`L279-L296`(cup visuals) | eligible if compatible | 露出驱动后盖：drum-only + 外保护环 torus + **固定 3 根**十字栅条 + 露出的 `ConeGeometry` 驱动单元锥 + 中心防尘帽半球。栅条数固定（非 vent_count 轴），有 driver/dust-cap part 语义。 |

> Slot B 三候选跨「封闭实心 dome（N=0）/ 开放 N 通风肋（multiplicity）/ 露出驱动锥+固定栅条」三种后盖拓扑，是后盖语义与 vent_count 复制轴的开关。`open_back_vented_grille` 有两份 5★ 实现（径向肋 S5 权威 + 钻孔板 S4 替代），模板取 S5 径向肋作 multiplicity 主源。

### Slot C：headband_form（头梁形态 — root part 本体 + 可选悬带子件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_solid_arch`（基线） | S1 `rec_over-ear-headphones-...-5669f0bd` | `L80-L87`(`_band_shell_mesh` sweep_profile_along_spline+rounded_rect_profile)、`L90-L100`(`_crown_pad_mesh`)、`L189-L201`(root `band` + band_shell+band_pad+housing) | eligible if compatible | 单条实心弧带（`sweep_profile_along_spline` 沿 YZ 弧扫掠圆角矩形截面）+ 皮质 crown pad。root part `band`，visuals `band_shell`+`band_pad`。 |
| `twin_parallel_rods` | S7 `rec_over_ear_headphones_var_band_twin_rods` | `L29-L40`(ROD_RADIUS/ROD_SPACING + HOUSING_W 加宽)、`L75-L93`(`_rod_arc_path`/`_band_rod_mesh`)、`L109-L125`(`_rod_clip_mesh`)、`L214-L235`(root 双杆+夹片) | eligible if compatible | 双平行细钢丝弧杆（`band_rod_0/1`，X 分离 `ROD_SPACING=0.018`，`polished_steel`）+ 夹片 stem+clamp ring 把 crown pad 连到两杆。HOUSING_W 加宽到 0.028 容双杆。root part `band`，**visual 群拓扑不同**（双杆+夹片，无单实心弧带）。 |
| `suspension_strap_under_arch` | S8 `rec_over_ear_headphones_var_band_suspension_strap` | `L32-L40`(ARCH/STRAP 常量)、`L89-L122`(`_arch_mesh`/`_strap_arc_path`/`_strap_mesh`)、`L125-L130`(`_strap_clip_mesh`)、`L220-L236`(root 改名 `arch`)、`L238-L258`(新 part `suspension_strap` + `arch_to_strap` PRISMATIC) | eligible if compatible | 薄扁弹簧钢外弧（`arch_frame`）+ 下方悬吊皮带（`suspension_strap`，沿 catenary `_strap_arc_path` 下垂）；**新增 part + `arch_to_strap` PRISMATIC**（0→`STRAP_DROOP=0.008` 下垂调节）。**root part 在原样本更名 `band`→`arch`**（模板须统一 root 命名，见 §13）。 |

> Slot C 三候选：`single_solid_arch` 单实心弧带、`twin_parallel_rods` 双杆+夹片（visual 群拓扑变 + HOUSING 加宽）、`suspension_strap_under_arch` 薄外弧 + **新 part + 新 PRISMATIC 子件**（articulation 增 1 DOF）。三者非纯尺寸/材质差异。

### Slot D：cup_attachment（耳罩↔头梁连接 — **真正承载运动学的 slot ⚠**；决定 cup↔band 非 fixed 关节拓扑 + part 树）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part/joint（cup↔band 连接处） |
|---|---|---|---|---|
| `two_tine_gimbal_clevis`（基线） | S1 `rec_over-ear-headphones-...-5669f0bd` | `L52-L58`(YOKE 常量)、`L122-L141`(`_yoke_mesh` `ClevisBracketGeometry`)、`L230-L242`(yoke part + `{slider}_to_{yoke}` **FIXED** origin (0,0,−0.038))、`L244-L268`(`{yoke}_to_{cup}` **REVOLUTE** +X ±0.44, origin (0,0,−YOKE_BORE_Z=−0.017)) | eligible if compatible | 双叉 clevis yoke FIXED 于 slider 底；cup 在 yoke bore 上 **REVOLUTE 仅耳倾仰**。part 树：slider + **yoke** + cup。cup↔band 活动 = 1× REVOLUTE（tilt），yoke 为刚接桥。 |
| `single_pivot_hanger` | S9 `rec_over_ear_headphones_var_attach_single_pivot` | `L47-L52`(ARM/PIVOT 常量)、`L115-L135`(`_hanger_arm_mesh` 吊臂+横 pivot post)、`L199-L210`(part `slider_{i}`/`cup_{i}`、hanger inline 为 slider visual `{sl}_arm`)、`L242-L252`(`slider_{i}_to_cup_{i}` **REVOLUTE** +X ±0.44, origin (0,0,SLIDER_BOT_Z−ARM_H=−0.060)) | eligible if compatible | **无 yoke part**：单侧吊臂带横 pivot post inline 进 slider；cup 直接 **REVOLUTE 挂在 slider 臂上**（取代「FIXED+REVOLUTE」对，删 yoke）。part 树：slider(含 arm) + cup。cup↔band 活动 = 1× REVOLUTE（slider→cup 直连）。 |
| `collapsible_folding_hinge` | S10 `rec_over_ear_headphones_var_attach_folding_hinge` | `L60-L63`(HINGE/FOLD 常量)、`L149-L154`(`_hinge_barrel_mesh`)、`L243-L264`(yoke + `{yk}_hinge` visual + `{slider}_to_{yoke}` **由 FIXED 改 REVOLUTE** 折叠 axis=(−side,0,0) 0→`FOLD_UPPER=1.50`)、`L280-L290`(`{yoke}_to_{cup}` REVOLUTE +X ±0.44 倾仰) | eligible if compatible | 折叠铰链：保留 clevis yoke + hinge barrel knuckle；**slider↔yoke 接口由 FIXED 升级为折叠 REVOLUTE**（内折向头梁 ≈86°）+ yoke→cup 倾仰 REVOLUTE。part 树：slider + **yoke** + cup。cup↔band 活动 = **2× REVOLUTE**（fold + tilt）。 |

> ⚠ **运动学集中在本 slot**：基线里 slider↔yoke 是 FIXED，唯一活动是 yoke↔cup 耳倾仰 REVOLUTE。`single_pivot_hanger` 删 yoke、用 `slider→cup` REVOLUTE 取代「FIXED+REVOLUTE」对（part 树变化）；`collapsible_folding_hinge` 把 `slider→yoke` 升级为折叠 REVOLUTE（每侧 +1 个非 fixed DOF）。三者跨「1×REVOLUTE（带刚接 yoke）/ 1×REVOLUTE（无 yoke 直连）/ 2×REVOLUTE（fold+tilt）」三种 joint 拓扑，是本模板 articulation 拓扑的主驱动开关，**不可仅当几何换皮**。

## 槽位图（slot graph）

pattern = `mixed`（left/right 镜像对称两条相同子链 + 可选 root 悬带子件）

```
[band]  (root：头梁；Slot C 决定本体 = 单实心弧带 / 双钢丝杆 / 薄外弧；housing_l/r 套筒 visual)
  │
  │  (Slot C = suspension_strap_under_arch 时，root 增 1 子件)
  ├── [suspension_strap]  --PRISMATIC arch_to_strap (axis (0,0,-1), origin (0,0,0), 0→STRAP_DROOP=0.008)-->
  │
  ├── 左侧链 (side=+1)
  │     [left_slider] --PRISMATIC band_to_left_slider (axis (0,0,-1), origin (0, +LEG_Y, LEG_Z), 0→SLIDER_TRAVEL=0.022)-->
  │        │   (Slot D 决定下一段接口)
  │        ├─ D=gimbal:  [left_yoke] --FIXED   left_slider_to_left_yoke (origin (0,0,SLIDER_BOT_Z=-0.038))-->
  │        │                [left_cup] --REVOLUTE left_yoke_to_left_cup (axis +X, origin (0,0,-YOKE_BORE_Z=-0.017), ±0.44)-->
  │        ├─ D=folding: [left_yoke] --REVOLUTE left_slider_to_left_yoke (axis (-side,0,0), origin (0,0,-0.038), 0→1.50 fold)-->
  │        │                [left_cup] --REVOLUTE left_yoke_to_left_cup (axis +X, origin (0,0,-0.017), ±0.44 tilt)-->
  │        └─ D=single_pivot: (无 yoke) [left_cup] --REVOLUTE left_slider_to_left_cup (axis +X, origin (0,0,SLIDER_BOT_Z-ARM_H=-0.060), ±0.44)-->
  │           (cup 上挂 Slot A 外形 + Slot B 后盖 visual 群 + Slot B=vented 时 N 根 vent_{i} 复制)
  │
  └── 右侧链 (side=-1)  …镜像同构（origin Y = -LEG_Y，fold_axis=(+1,0,0)）
```

接口点位与装配说明：

- **band → slider（伸缩，所有 D 共享）**：joint origin 在 band-leg 弧端点 `(0, side·LEG_Y, LEG_Z)`（= housing 顶），PRISMATIC axis (0,0,-1) 0→`SLIDER_TRAVEL`。slider bar top 永驻 housing 内（captured；`SLIDER_TOP_Z − SLIDER_TRAVEL ≥ −HOUSING_H`）。`LEG_Y=BAND_R·sin(CROWN_HALF)`、`LEG_Z=BAND_C_Z+BAND_R·cos(CROWN_HALF)`，随 `headband_scale`（BAND_R）派生。
- **slider → cup mount（Slot D 决定）**：gimbal=slider→yoke FIXED（yoke 在 SLIDER_BOT_Z），folding=slider→yoke REVOLUTE 折叠（同 origin，axis (-side,0,0)），single_pivot=无 yoke、slider→cup REVOLUTE 直连（origin 下移到臂底 SLIDER_BOT_Z−ARM_H）。
- **yoke/slider → cup（倾仰，所有 D 共享语义）**：cup frame origin 与 pivot 重合 → **cup pivot 永在 cup TOP（cup-local z=0）**，cup 几何（Slot A/B）全部 z≤0 向下悬挂；REVOLUTE axis +X ±0.44。Slot A 改变 cup 几何尺寸但**不改 pivot 在 cup top 的接口**。
- **cup 后盖（Slot B）+ vent 复制（N）**：后盖 visual 群挂在 cup part 朝外 ±Y 面（`side·CUP_HD` 外侧）；vented 后盖时 `for i in range(vent_count)` 在后盖中心绕 cup 轴均布 vent 肋（`{cp}_vent_{i}`），left/right 各一份。
- **互斥 / 派生关系**：Slot B 三值互斥（决定后盖 part/visual 群 + 是否暴露 vent_count）；Slot D 三值互斥（决定 yoke 是否存在 + cup↔band 关节拓扑，single_pivot 与 folding 因 yoke 有无天然单选）；Slot C 三值互斥（决定 root 本体 + 是否有 strap 子件，root part 须统一命名为 `band`）。`vent_count` 仅在 Slot B=`open_back_vented_grille` 时有意义。ear-pad/inner-cap 轮廓由 Slot A 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / module `round_drum`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`{cp}_shell`（drum+dome）/`{cp}_cap`（inner cap）/`{cp}_pad`（torus）为 cup part 的 visual | S1 / model.py:L246-L251 |
| internal joints | 无（外形是 cup visual） | — |
| upstream interface | cup pivot 在 cup-local z=0（cup top）；drum 各向同径 CUP_R | S1 / model.py:L144-L161 |
| downstream interface | 后盖（Slot B）挂朝外 ±Y 面 `side·CUP_HD`；pad 朝内 −side 贴耳 | S1 / model.py:L156-L175 |

### Slot A / module `vertical_oval`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{cp}_shell`(superellipse 椭圆鼓+椭圆 dome)/`{cp}_cap`/`{cp}_pad`(椭圆缩放 torus) 为 cup visual | S2 / model.py:L257-L262 |
| internal joints | 无 | — |
| upstream interface | cup pivot 在 cup top（z=0）；CUP_RZ>CUP_RX（高>宽） | S2 / model.py:L148-L166 |
| downstream interface | dome/pad 椭圆缩放贴 cup footprint；后盖挂朝外面 | S2 / model.py:L160-L186 |

### Slot A / module `rounded_rect`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{cp}_shell`(圆角矩形本体+raised panel)/`{cp}_cap`/`{cp}_pad`(沿圆角矩形轮廓闭合扫掠) 为 cup visual | S3 / model.py:L283-L288 |
| internal joints | 无 | — |
| upstream interface | cup pivot 在 cup top（z=0）；`_rounded_rect_cup_body` taller-than-wide | S3 / model.py:L143-L156 |
| downstream interface | 非圆 ear-pad（tube_from_spline_points 闭合扫掠）；后盖挂朝外面 | S3 / model.py:L198-L212 |

### Slot B / module `closed_solid_dome`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：后盖 = `{cp}_shell` 内的封闭浅球冠 dome（cup visual） | S1 / model.py:L156-L159 |
| internal joints | 无 | — |
| upstream interface | 坐落于 cup 朝外 ±Y 面（`side·(CUP_HD+0.006)`），sealed 无孔 | S1 / model.py:L156-L159 |
| downstream interface | 无 vent_count（N=0） | — |

### Slot B / module `open_back_vented_grille`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`{cp}_grille_ring`/`{cp}_grille_hub`（固定框架）+ `{cp}_vent_{i}`（N 根径向肋）为 cup visual（钻孔板替代实现用 `{cp}_grille` + torus `{cp}_vent_{i}`） | S5 / model.py:L269-L279；S4 / model.py:L287-L294 |
| internal joints | 无（vent 肋是刚性 cup visual，无关节） | — |
| upstream interface | drum-only shell（去 dome）；ring/hub/vent 坐落于后盖中心 `side·CUP_HD` | S5 / model.py:L146-L167 |
| downstream interface | **暴露 vent_count multiplicity 轴**（详见 §8） | S5 / model.py:L273-L279 |

### Slot B / module `exposed_driver_behind_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`{cp}_ring`/`{cp}_bars`(固定 3 支条)/`{cp}_driver`(驱动锥)/`{cp}_dustcap`/`{cp}_innercap` 为 cup visual | S6 / model.py:L279-L296 |
| internal joints | 无（驱动锥/防尘帽是刚性 cup visual，无关节） | — |
| upstream interface | drum-only shell；保护环凸出 cup 朝外面，driver 凹陷在环之后 | S6 / model.py:L153-L193 |
| downstream interface | 无 vent_count（栅条固定 3，非复制轴） | — |

### Slot C / module `single_solid_arch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `band`（visuals `band_shell` 单实心弧带 + `band_pad` crown pad + `housing_l/r`） | S1 / model.py:L189-L201 |
| internal joints | 无（root） | — |
| upstream interface | root（无父） | — |
| downstream interface | band-leg 弧端点 `(0, side·LEG_Y, LEG_Z)` 供两侧 slider PRISMATIC 挂接；housing 捕获 slider top | S1 / model.py:L103-L108, L216-L227 |

### Slot C / module `twin_parallel_rods`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `band`（visuals `band_rod_0/1` 双钢丝杆 + `band_pad` + `pad_clip_0/1` 夹片 + `housing_l/r`） | S7 / model.py:L214-L235 |
| internal joints | 无（root） | — |
| upstream interface | root（无父） | — |
| downstream interface | band-leg 端点同基线（HOUSING_W 加宽到 0.028 容双杆）；slider PRISMATIC 挂接 | S7 / model.py:L37-L40, L228-L235 |

### Slot C / module `suspension_strap_under_arch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `band`（薄外弧 `arch_frame` + `strap_clip_0/1` + `housing_l/r`）+ **新 part `suspension_strap`**（`strap_body` 下垂皮带） | S8 / model.py:L220-L245 |
| internal joints | **`band_to_strap` PRISMATIC**（axis (0,0,-1)，0→`STRAP_DROOP=0.008` 下垂调节；样本名 `arch_to_strap`，模板统一为 `band_to_strap`） | S8 / model.py:L246-L258 |
| upstream interface | root（无父）；strap 端部夹片坐落 arch 下侧端点（element-scoped contact） | S8 / model.py:L125-L130, L359-L360 |
| downstream interface | band-leg 端点同基线；arch 顶与 strap 之间留可见 sag gap≥0.008 | S8 / model.py:L348-L357 |

### Slot D / module `two_tine_gimbal_clevis`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{side}_yoke`（ClevisBracketGeometry，visual `{yk}_body`） | S1 / model.py:L230-L235 |
| internal joints | `{slider}_to_{yoke}` **FIXED**（origin (0,0,SLIDER_BOT_Z)）+ `{yoke}_to_{cup}` **REVOLUTE** +X ±0.44（origin (0,0,-YOKE_BORE_Z)） | S1 / model.py:L236-L242, L258-L268 |
| upstream interface | yoke base 贴 slider 底（captured，allow_overlap yoke↔slider） | S1 / model.py:L236-L242 |
| downstream interface | cup top 插入 yoke clevis gap（captured，allow_overlap cup↔yoke）；cup pivot 在 yoke bore | S1 / model.py:L256-L268 |

### Slot D / module `single_pivot_hanger`
| emits | 描述 | 来源 |
|---|---|---|
| parts | **无 yoke part**：吊臂+横 pivot post inline 为 slider visual `{sl}_arm` | S9 / model.py:L205-L210 |
| internal joints | `{slider}_to_{cup}` **REVOLUTE** +X ±0.44（origin (0,0,SLIDER_BOT_Z−ARM_H)，slider→cup 直连） | S9 / model.py:L242-L252 |
| upstream interface | hanger arm 固接 slider 底；cup top 绕 pivot post（captured，allow_overlap cup↔slider elem `{sl}_arm`） | S9 / model.py:L327-L337 |
| downstream interface | 断言无 yoke part（`not any("yoke" in n)`）；pivot 在 cup top edge | S9 / model.py:L271-L305 |

### Slot D / module `collapsible_folding_hinge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{side}_yoke`（ClevisBracketGeometry + `{yk}_hinge` barrel knuckle visual） | S10 / model.py:L243-L247 |
| internal joints | `{slider}_to_{yoke}` **REVOLUTE 折叠**（axis (-side,0,0)，0→`FOLD_UPPER=1.50`）+ `{yoke}_to_{cup}` REVOLUTE +X ±0.44 倾仰 | S10 / model.py:L251-L264, L280-L290 |
| upstream interface | hinge barrel 坐落 slider 底 fold 接口（captured，allow_overlap yoke↔slider） | S10 / model.py:L377-L383 |
| downstream interface | cup top 插入 yoke clevis gap；fold 时 cup 折向 Y=0 且抬高 z（断言 L358-L375） | S10 / model.py:L358-L375 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `cup_shape` | enum | `round_drum` / `vertical_oval` / `rounded_rect` | `round_drum` | choice | deterministic procedural sampler 选择；决定 cup 几何 + ear-pad/inner-cap 轮廓 | Slot A 表 |
| `cup_back_style` | enum | `closed_solid_dome` / `open_back_vented_grille` / `exposed_driver_behind_ring` | `closed_solid_dome` | choice | sampler 选择；决定后盖 visual 群 + 是否暴露 vent_count | Slot B 表 |
| `headband_form` | enum | `single_solid_arch` / `twin_parallel_rods` / `suspension_strap_under_arch` | `single_solid_arch` | choice | sampler 选择；决定 root 本体 + 是否有 strap PRISMATIC 子件 | Slot C 表 |
| `cup_attachment` | enum | `two_tine_gimbal_clevis` / `single_pivot_hanger` / `collapsible_folding_hinge` | `two_tine_gimbal_clevis` | choice | sampler 选择；**决定 cup↔band 关节拓扑 + yoke 有无（articulation 主开关）** | Slot D 表 |
| `vent_count` | int | `[4, 16]`（仅 B=open_back_vented_grille） | 8 | conditional | 加权采样（小 N 偏多）；仅当 `cup_back_style==open_back_vented_grille` 时有效，否则 N=0/不适用；避开测试排除值 12 | S5 / model.py:L68, L273-L279（详见 §8） |
| `palette_style` | enum | `silver_black_pads` / `matte_black_leather` / `white_grey` / `tan_leather_brass` / `studio_grey` / `polished_steel_black` | `silver_black_pads` | choice | 每 seed 采样 colorway；仅改 material rgba，不改拓扑/尺寸/接口 | S1 mats L183-L186（+ 跨变体配色派生，见下） |
| `headband_scale`（BAND_R） | float | [0.88, 1.12] | 1.0 | independent | 头梁弧半径整体缩放；clamp。决定 crown 高度 + leg 端点位置 | S1 `BAND_R` L25 |
| `cup_size_scale` | float | [0.85, 1.15] | 1.0 | independent | cup 外形整体缩放（CUP_R / CUP_RX,RZ / CUP_W,H）；clamp。pad/inner-cap/后盖随动 | S1 `CUP_R` L61；S2 L63-64；S3 L56-57 |
| `cup_depth_scale` | float | [0.85, 1.20] | 1.0 | independent | cup 沿 ±Y 轴向深度（CUP_DEPTH）缩放（包耳深度）；clamp | S1 `CUP_DEPTH` L62 |
| `slider_travel_scale` | float | [0.8, 1.25] | 1.0 | independent | PRISMATIC 伸缩行程缩放；clamp | S1 `SLIDER_TRAVEL` L39 |
| `cup_tilt_limit` | float | [0.30, 0.55] | 0.44 | independent | cup 倾仰 REVOLUTE 的 ±limit（rad）；clamp | S1 tilt limits L266 |
| `fold_limit`（仅 D=folding） | float | [1.20, 1.55] | 1.50 | conditional | 折叠 REVOLUTE 上限（rad），仅 cup_attachment=folding_hinge 时有效；clamp | S10 `FOLD_UPPER` L63 |
| `LEG_Y` / `LEG_Z`（slider mount） | float | derived | — | equation | `LEG_Y = BAND_R·sin(CROWN_HALF)`、`LEG_Z = BAND_C_Z + BAND_R·cos(CROWN_HALF)`（随 headband_scale 派生）；不独立采样 | S1 L30-L31 |
| `PAD_MAJOR/RX/RZ` / inner-cap 尺寸 | float | derived | — | equation | ear-pad/inner-cap 轮廓 `= f(cup 尺寸)`（Slot A 决定圆/椭圆/矩形）；随 cup_size_scale 派生 | S1 L65-L66；S2 L68-L70；S3 L63-L66 |
| `cup_pivot_origin_z` | float | derived | — | equation | cup REVOLUTE origin Z：gimbal/folding `= -YOKE_BORE_Z`、single_pivot `= SLIDER_BOT_Z - ARM_H`（随 Slot D 派生，保 pivot 在 cup top） | §槽位图接口说明 |
| (—) | constraint | — | — | inequality | **slider 永驻 housing**：`SLIDER_TOP_Z − SLIDER_TRAVEL·slider_travel_scale ≥ −HOUSING_H`。违反则回缩 slider_travel_scale。 | S1 L45-L47, L320-L325 |
| (—) | constraint | — | — | inequality | **cup 在 crown 之下**：缩放后 cup 顶 world z ≤ band_top − 0.04（cup 悬于 crown 下）。违反则回缩 cup_size_scale 或抬 headband_scale。 | S1 L299-L302 |
| (—) | constraint | — | — | inequality | **fold 闭合 clearance（D=folding × 大 cup）**：D=folding_hinge 在 `q=fold_limit` 全折叠位，左右 cup 内侧 Y 向 gap ≥ 0.002（两 cup 折向 Y=0 不互穿）。违反则回缩 cup_size_scale / fold_limit；不可行则该组合 fallback（见 §9）。 | S10 fold-inward L358-L371 |
| (—) | constraint | — | — | inequality | **着地/包络**：缩放后整体 min_z ∈ [-0.004, 0.006]；cup pivot 始终在 cup top（A 切换不破接口）。 | S1 inertial/aabb L198-L201 |

`palette_style` colorway 取值（rgba 仅作示意，下游模板落实；全部源自 5★ 观察的 gunmetal/leather/metal_dk/shell_lt 基线及变体引入的 polished_steel/leather_tan/brushed_steel/cone_mat）：
- `silver_black_pads`（= S1 基线）：band gunmetal (0.24,0.24,0.26)、cup shell 浅银 (0.73,0.74,0.75)、pad/crown 近黑 leather (0.08,0.07,0.07)、slider/yoke metal_dk (0.19,0.19,0.21)。
- `matte_black_leather`：band+cup 全哑光黑 (0.10,0.10,0.11)、pad 黑 leather、五金 metal_dk；统一深色消费旗舰风。
- `white_grey`：cup shell 白 (0.90,0.90,0.91)、pad 中灰 (0.45,0.45,0.47)、band 浅灰金属 (0.62,0.63,0.65)。
- `tan_leather_brass`：cup shell 深炭 (0.16,0.15,0.14)、pad+crown 棕褐 leather_tan (0.42,0.30,0.18)、band 黄铜/拉丝 (0.66,0.54,0.30) —— 复古监听/木质风。
- `studio_grey`：全中性拉丝灰 brushed_steel (0.55,0.55,0.57) band + 深灰 cup (0.30,0.31,0.33) + 黑 pad —— 录音棚监听风。
- `polished_steel_black`：band polished_steel (0.55,0.56,0.58)（twin-rod 风）+ cup 黑 (0.12,0.12,0.13) + 黑 leather pad + driver cone_mat (0.12,0.12,0.13) —— 开放/露驱动监听风。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：`vent_count`（条件性，仅 vented-grille 后盖）。** 其余复制（cup ×2、housing ×2、twin rod ×2、strap clip ×2）均为**固定 module-local 循环**（非模板可变轴）。

### 轴 N1：`vent_count`（每只 cup 后盖的均布通风条数）
- `count_param`：`vent_count`（源码 `VENTS_PER_CUP`，S5 L68）。
- `N_range`：`[4, 16]`（本小类本轴产品域；**8 为已验证样本**，测试显式排除 12 故 N_range 须能避开 12）。注：**父对象封闭实心 dome 无通风条（N=0）**；`exposed_driver` 用固定 3 根栅条（非 vent_count 轴）。
- sampling domain（权重档）：小 N 高频（6-10 常见消费/监听栅孔密度），尾部（13-16）稀有；显式从候选集剔除 12（测试 `VENTS_PER_CUP != 12`）。
- copied object：单根 `_vent_slot_mesh` 径向肋（`BoxGeometry`，S5 L170-181），外加**固定**框架 `_grille_ring_mesh`(`{cp}_grille_ring`) + `_grille_hub_mesh`(`{cp}_grille_hub`)（S5 L154-167）。（钻孔板替代实现 S4：`_vented_back_plate_mesh` 中心孔+N 孔环 + 每孔 `_vent_rim_mesh` torus 缘。）
- naming：`for i in range(vent_count)` → visual 名 `{cp}_vent_{i}`（每 cup 独立计数，left/right 各一份）。
- placement：绕 cup 轴 `rotate_y(2π·i/N)` 均布后 `translate(0, side·CUP_HD, −CUP_R)` 贴后盖中心；left/right 两 cup 各复制一份（S5 L273-279）。
- joint policy：vent 肋是 cup part 上的**刚性 visual（无关节）**，纯外观复制，**不新增 articulation**；N 变化只改 cup 视觉，不动骨架。
- source/gating：**仅当 `cup_back_style == open_back_vented_grille` 时启用**；`closed_solid_dome`→N=0（轴不暴露），`exposed_driver_behind_ring`→固定栅条（轴不暴露）。见 §9 compatibility matrix。

### 固定 module-local 循环（非模板轴，不暴露为 `*_count`）
- 左右 cup ×2（`for side ...` / `for i in range(2)` 镜像；over-ear = 双 cup 定义，恒 2）。
- `housing_l/r` ×2、twin rod `band_rod_0/1` + `pad_clip_0/1` ×2（仅 C=twin_rods）、`strap_clip_0/1` ×2（仅 C=suspension）、exposed_driver 固定 3 根 `grille_bars`（仅 B=exposed_driver）。这些是固定结构，不构成可变 multiplicity 轴。

## 拓扑多样性审计

总组合数：A × B × C × D = 3 × 3 × 3 × 3 = **81** slot 组合（cup 恒 ×2 不计入）。
叠加 `vent_count` multiplicity（仅 B=open_back_vented_grille 子集，N∈[4,16]\{12} 约 12 个样本）：vented 子集 27 组合 × ~12 N ≈ 324，非 vented 子集 54 组合 × 1 ≈ 54，合计 **≈ 378** 个 distinct seed 配置（远超 10）。


理由：81 个 slot 组合各改变 part 树或 joint 拓扑 —— Slot D 跨「1×REVOLUTE(带 FIXED yoke) / 1×REVOLUTE(无 yoke 直连) / 2×REVOLUTE(fold+tilt)」三种 articulation 拓扑（part 树 yoke 有无），Slot C 含「新 part + PRISMATIC strap 子件」(+1 DOF) vs 单/双 root visual，Slot B 改后盖 part/visual 群且开关 vent_count 复制轴，Slot A 改 cup 几何生成法。单 slot 组合即达 81 distinct，远超 10 门槛；叠加 vent_count 更高。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG 独立加权采样四个 slot enum（A/B/C/D 各 3 选 1，默认近均匀，可对 `round_drum`/`closed_solid_dome`/`single_solid_arch`/`two_tine_gimbal_clevis` 经典基线略加权），**先解析 Slot B → 若 = open_back_vented_grille 则加权采样 `vent_count`（小 N 偏多，剔除 12），否则不暴露该轴**；再采样 `palette_style` 与所有 `independent` 连续 scale（headband/cup_size/cup_depth/slider_travel/cup_tilt），按 `equation` 派生 LEG_Y/LEG_Z、pad/inner-cap 尺寸、cup_pivot_origin_z（随 Slot D），`conditional` 解析 fold_limit（仅 D=folding），最后用四条 `inequality`（slider 驻 housing、cup 在 crown 下、fold 闭合 clearance、着地/包络）投影回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定的 `[(cup_shape,…),(cup_back_style,…),(headband_form,…),(cup_attachment,…),(vent_count,N)]`（连续 scale 不进 slot_choices）。compatibility gating 在 `resolve_config` 解析，不留到 builder 失败。`seed=0` 不特殊。无需 regression overrides（10 源全部已收敛、四 slot 齐全）；若 sweep 暴露坏组合再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别约束封顶在 81 slot 组合（vent_count 不改 part-tree 等价类，只增 cup 视觉计数，可计入或不计入 topology 等价类）。若把 vent_count 不同 N 计入则 distinct 按 ≥300 富类别口径观察；若仅按 part-tree/joint 拓扑等价类则封顶 81。81（或 ≥300 含 N）满足/接近 100 目标，slot 池由 over-ear 结构词汇表（headband 3 + 后盖 3 + cup 形 3 + 连接 3）固有决定，非建模缺陷。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization（初版模板应含的关键连续 scale）：`headband_scale [0.88,1.12] independent`、`cup_size_scale [0.85,1.15] independent`、`cup_depth_scale [0.85,1.20] independent`、`slider_travel_scale [0.8,1.25] independent`、`cup_tilt_limit [0.30,0.55] independent`、`fold_limit [1.20,1.55] conditional`；派生 LEG_Y/LEG_Z（headband_scale）、pad/inner-cap 尺寸（cup_size_scale）、cup_pivot_origin_z（Slot D）。遵循连续尺寸采样契约：先采 independent → 派生 equation → 解析 conditional（fold_limit）→ 用四条 inequality 投影回缩。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（slider 坐 band-leg 端点、cup pivot 永在 cup top、后盖坐朝外面）、MatingContract（slider 捕获 housing、yoke 捕获 slider、cup 捕获 yoke/arm）或 multiplicity（cup 恒 2、vent_count 仅 vented 后盖）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 B→(vent_count)→A→C→D + palette + 连续 scale；compatibility gate 在 resolve_config | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | A×B×C×D 81 组合默认全合法（over-ear 身份不冲突）。**关键 gate**：①`vent_count` 仅 B=open_back_vented_grille（其余后盖不暴露 N，强制 N=0/固定）；②**D=collapsible_folding_hinge × 大 cup（A=rounded_rect/vertical_oval × cup_size_scale 上限）**：fold 闭合需 §7 inequality 保左右 cup 内侧 gap≥0.002，不可行则回缩 cup_size_scale 或 fold_limit，仍不可行则 D fallback 到 two_tine_gimbal_clevis；③Slot C=suspension_strap 须统一 root part 名为 `band`（不可残留 `arch` 命名，否则下游 `band_to_slider` 失配）；④Slot D=single_pivot 无 yoke part，folding/gimbal 有 yoke —— 模板按 D 决定是否发射 yoke part（part 树开关）。 | 无 floating / 无穿模 / fold 闭合左右 cup 不互穿 / slider 驻 housing / cup 在 crown 下 / 恰 2 cup |
| controlled local variation | 5+1 个 independent/conditional scale + 派生 LEG/pad/pivot；全部 clamp + 四条 inequality 回缩 | 比例随机但 cup pivot 在 cup top、slider 捕获、后盖坐朝外面、着地、over-ear 身份不破 |
| regression overrides | none（10 源全部已收敛，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（fold 闭合/slider/着地 + vent_count 计数） |、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A cup_shape | 3 | yes | yes | round / oval / rounded_rect |
| B cup_back_style | 3 | yes | yes | closed_dome / vented_grille / exposed_driver |
| C headband_form | 3 | yes | yes | single_arch / twin_rods / suspension_strap |
| D cup_attachment | 3 | yes | yes | gimbal / single_pivot / folding（articulation 主轴） |
| (N) vent_count | mult-axis | — | — | 条件轴，仅 B=vented_grille，N∈[4,16]\{12} |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{round_drum, vertical_oval, rounded_rect}、B∈{closed_solid_dome, open_back_vented_grille, exposed_driver_behind_ring}、C∈{single_solid_arch, twin_parallel_rods, suspension_strap_under_arch}、D∈{two_tine_gimbal_clevis, single_pivot_hanger, collapsible_folding_hinge}），以及 B=vented 时附带 `vent_count`∈[4,16]\{12}。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + vent_count + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：vent_count 仅 vented 后盖；D=folding × 大 cup 通过 fold 闭合 clearance gate 或回缩/ fallback 到 gimbal；C=suspension 统一 root 名 `band`；D 决定 yoke part 是否发射。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（headband/cup_size/cup_depth/slider_travel/cup_tilt/fold_limit）在 `resolve_config` clamp/派生；四条 inequality（slider 驻 housing、cup 在 crown 下、fold 闭合 clearance、着地）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：slider top 捕获 band `housing`（element allow_overlap，slider↔band）；yoke base 捕获 slider 底（D=gimbal/folding，allow_overlap yoke↔slider）；cup top 捕获 yoke clevis gap（D=gimbal/folding）或 hanger pivot post（D=single_pivot，element `{sl}_arm`）；C=suspension 时 strap 端部捕获 arch 下侧。
- 关键 joint type/axis/range：band→slider = PRISMATIC (0,0,-1) 0→SLIDER_TRAVEL（所有 D 共享）；cup 倾仰 = REVOLUTE +X ±cup_tilt_limit；D=gimbal slider→yoke = FIXED；D=folding slider→yoke = REVOLUTE (-side,0,0) 0→fold_limit；D=single_pivot slider→cup = REVOLUTE +X（无 yoke）；C=suspension band→strap = PRISMATIC (0,0,-1) 0→STRAP_DROOP。
- copied object 命名/placement：cup `left_/right_`（side=±1 镜像）；vent `{cp}_vent_{i}`（i∈0..vent_count-1，绕 cup 轴均布，left/right 各一份）；twin rod `band_rod_{i}` / strap clip `strap_clip_{i}`（固定 2）。
- over-ear 身份不变量：恰好 2 只镜像包耳 cup；cup 悬于 band crown 之下；ear-pad 朝内贴耳（circumaural）；每 cup 有 cup↔band 非 fixed 倾仰 REVOLUTE；左 +Y / 右 −Y 对称。
- B=closed_solid_dome：无 grille/vent visual；B=open_back_vented_grille：每 cup 恰 vent_count 个 `{cp}_vent_{i}` + ring/hub；B=exposed_driver：有 ring/bars/driver/dustcap visual。
- D=single_pivot_hanger：断言无 yoke part；D=collapsible_folding_hinge：断言 fold 时左右 cup 折向 Y=0 且抬高 z、tilt 仍可动。

## Reject cases

- 只有 1 只 cup（或 3 只以上），或 cup 不包耳/pad 朝外 —— 违反 over-ear circumaural 身份（必须恰好 2 只镜像包耳 cup、pad 朝内）。
- 缺 cup↔band 非 fixed 倾仰 REVOLUTE，或 cup 不在 band crown 之下（cup 漂在 crown 之上/同高）—— 读成 fixed 砖块，丢失耳机佩戴语义。
- Slot D 关节拓扑错配：single_pivot 仍残留 yoke part / 仍用 FIXED+REVOLUTE 对；folding_hinge 的 slider→yoke 仍是 FIXED（折叠 DOF 缺失）；gimbal 的 yoke→cup 非 REVOLUTE —— articulation 拓扑与所选 module 不符。
- cup pivot origin 未随 Slot D 派生（gimbal/folding 用 -YOKE_BORE_Z、single_pivot 用 SLIDER_BOT_Z-ARM_H）→ cup 悬空脱离 mount 或 pivot 不在 cup top。
- `vent_count > 0` 却 B≠open_back_vented_grille（封闭 dome / 露驱动后盖上长出通风肋），或 vent_count==12（测试排除值），或 vented 后盖却无 ring/hub 框架 —— multiplicity gate 失配。
- C=suspension_strap 残留 root 名 `arch` 未统一为 `band` → 下游 `band_to_slider` 引用失配；或 strap 端部未捕获 arch（strap 漂浮）/ 无可见 sag gap。
- D=folding_hinge × 大 cup 未做 fold 闭合 clearance → 全折叠位左右 cup 在 Y=0 互穿（穿模）；或 slider_travel 过大致 slider top 露出 housing（`SLIDER_TOP_Z − travel < −HOUSING_H`）。
- 把 boom microphone arm / 单 cup monocular 式听筒 / 无驱动语义的纯密封护耳罩混进来当 cup —— 错类别（见 §11）。

## 与相邻类别的边界

- 不该混入：**on-ear（supra-aural）耳机**（耳上式）—— on-ear cup 较小、pad 直接压在耳廓上（pad 内圈 ≤ 耳），cup 浅、不整圈包耳。over-ear 的身份是 **circumaural 包耳**：ear-pad 朝内、内圈大于耳廓整圈包住耳、cup 深（`cup_depth_scale` 不可缩到 on-ear 浅度，pad/cup 不可缩到压耳尺寸）。不要把 cup 缩小到压在耳上的 on-ear footprint。
- 不该混入：**护耳罩 / earmuffs（听力防护 / 保暖）**—— 外形似头梁+双 cup 但**无音频驱动语义**（实心密封 cup、无 inner driver cap、无 grille/露驱动后盖、无 cable），常厚泡棉/毛绒。over-ear 必须保留**驱动腔身份**（inner cap = 驱动 baffle，`exposed_driver` 露出 speaker cone，`vented_grille` 开放后腔）。不要去掉驱动/后盖语义做成纯护耳罩。
- 不该混入：**航空/通讯 headset（aviation headset）**—— headset 在 over-ear 基础上**多一根 boom microphone 臂**（话筒悬臂，常 + PTT / 旋臂关节），是其定义性附件。本 over-ear 模板**无 boom mic part / 无话筒悬臂关节**；一旦加 boom mic 就变成 aviation/gaming headset。不要引入话筒臂或下颌悬臂部件。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`band` root + `_band_arc_path`/`_crown_pad_mesh`/`_housing_mesh`/`_slider_mesh` + `for side ... (left/right)` 镜像发射 + captured-pin `allow_overlap` 契约在全 10 源一致，可抽公共 helper（保留 `# adopted: <source>` 注释）。Slot A 三模块各有 cup mesh helper（`_cup_shell_mesh` cylinder for round；superellipse-extrude for oval；`_rounded_rect_cup_body` for rect），按 `cup_shape` 分派；ear-pad/inner-cap helper 同样分派（torus / 椭圆 torus / 圆角矩形扫掠）。
- **Slot C root 命名统一**：`suspension_strap_under_arch` 源把 root 命名为 `arch`、per-side joint 命名 `arch_to_slider`。模板必须**统一 root part 名为 `band`**（三 C 值一致），suspension 把薄外弧 `arch_frame` 作为 `band` 的 visual + 追加 `suspension_strap` part 与 `band_to_strap` PRISMATIC；下游 `band_to_{slider}` 命名保持不变。
- **Slot D part-tree 开关**：gimbal/folding 发射 `{side}_yoke` part；single_pivot **不发射 yoke**、把吊臂 inline 为 slider visual `{sl}_arm` 并把 cup REVOLUTE 父改为 slider。`cup_pivot_origin_z` 与 cup REVOLUTE 父（yoke vs slider）按 Slot D 选择，不可硬编码。single_pivot 的 captured-pin overlap 须 element-scoped 到 `{sl}_arm`（参考 S9 L332-337）。
- captured-pin overlap 须 element-scoped `allow_overlap`：slider↔band housing（全模块）、yoke↔slider（D=gimbal/folding）、cup↔yoke clevis 或 cup↔`{sl}_arm`（按 D）、strap↔arch（C=suspension）。参考各源 run_tests 的 `allow_overlap` 块。
- **vent_count 双实现**：主用 S5 径向肋（`_grille_ring`+`_grille_hub`+N×`_vent_slot_mesh`），可选 S4 钻孔板（`ExtrudeWithHolesGeometry`+torus rim）。模板取一种作 vented_grille 实现，N 复制循环命名 `{cp}_vent_{i}`、left/right 各一份；剔除 N=12（测试排除）。
- **D=folding × 大 A cup** 组合：在 `resolve_config` 校验 fold 闭合 clearance（全折叠位左右 cup 内侧 Y gap），不可行则回缩 cup_size_scale/fold_limit，仍不可行该 seed 的 D fallback 到 `two_tine_gimbal_clevis`（compatibility matrix fallback 路径）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | `round_drum` / `closed_solid_dome` / `single_solid_arch` / `two_tine_gimbal_clevis` | `rec_over-ear-headphones-with-padded-leather-ear-cups_20260609_080248_682174_5669f0bd` | A `L60-63,L144-175`；B dome `L156-159`；C `L80-100,L189-201`；D `L122-141,L230-268`；shared spine `L208-227` | 四 slot 基线 + 共享头梁/伸缩/倾仰骨架 + captured-pin 契约 |
| S2 | A | `vertical_oval` | `rec_over_ear_headphones_var_cup_oval` | `L62-70,L148-186,L315-321` | 竖椭圆 cup（superellipse-extrude + 椭圆 pad/dome） |
| S3 | A | `rounded_rect` | `rec_over_ear_headphones_var_cup_rounded_rect` | `L55-66,L143-212,L341-358` | 圆角矩形 cup（新 helper + 非圆扫掠 pad） |
| S4 | B | `open_back_vented_grille`（钻孔板替代实现） | `rec_over_ear_headphones_var_back_vented_grille` | `L68-74,L184-213,L283-298,L382-419` | 钻孔板开放后盖 + torus vent rim（替代实现） |
| S5 | B / (N) | `open_back_vented_grille`（径向肋 + **vent_count 权威源**） | `rec_over_ear_headphones_var_grille_vent_count` | `L68,L146-181,L269-279,L367-385` | 径向肋开放后盖 + vent_count multiplicity（ring+hub+N 肋，排除 12） |
| S6 | B | `exposed_driver_behind_ring` | `rec_over_ear_headphones_var_back_exposed_driver` | `L145-193,L279-296,L393-434` | 露出驱动后盖（保护环+固定 3 栅条+驱动锥+防尘帽） |
| S7 | C | `twin_parallel_rods` | `rec_over_ear_headphones_var_band_twin_rods` | `L29-40,L75-93,L109-125,L214-235,L338-363` | 双钢丝弧杆头梁 + 夹片（HOUSING 加宽） |
| S8 | C | `suspension_strap_under_arch` | `rec_over_ear_headphones_var_band_suspension_strap` | `L32-40,L89-130,L220-258,L348-375` | 薄外弧 + 悬带 part + `band_to_strap` PRISMATIC droop（root 须改名统一） |
| S9 | D | `single_pivot_hanger` | `rec_over_ear_headphones_var_attach_single_pivot` | `L47-52,L115-135,L199-210,L242-252,L271-305` | 删 yoke、单 pivot 吊臂、slider→cup REVOLUTE 直连 |
| S10 | D | `collapsible_folding_hinge` | `rec_over_ear_headphones_var_attach_folding_hinge` | `L60-63,L149-154,L243-264,L280-290,L358-375` | 折叠铰链：slider→yoke FIXED→REVOLUTE fold + yoke→cup tilt（每侧 2 revolute） |
