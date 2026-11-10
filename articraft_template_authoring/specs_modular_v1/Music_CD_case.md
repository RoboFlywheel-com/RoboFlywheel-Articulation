# CD Jewel Case Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `cd_jewel_case` |
| template path | `agent/templates/Music_CD_case.py` |
| test path (optional) | `tests/agent/test_cd_jewel_case_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：根 chassis（rigid 壳体的 `base`，或 digipak 的 `tray_panel`）下挂三个可替换层 —— **body_type**（壳体形态/footprint）、**closure_hinge**（开合机构：摆盖 REVOLUTE / 侧翻 REVOLUTE / 滑套 PRISMATIC / digipak 书脊折 REVOLUTE）、**inner_tray**（持碟机构：中心轮毂 / 无盘托口袋 / 双面翻托 / 小册夹）—— 外加 **一根 multiplicity 轴 `disc_count`**（碟片复制数 N），N 选择两种不同 copy-logic（共面并列 / 堆叠书页）。slot 之间正交但有强 compatibility gating（来自 source map 排除项 + 结构推理）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category: 1 parent + 10 variants，`model.py` 全文逐条阅读 |
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below（见 §14 Module Source Index） |

11 个 5★ 样本（1 parent + 10 variant，全部 compile=success、workbench-only、仍明确读作 CD 珠宝盒）逐条阅读摘要：

- **S1 parent `rec_clear-plastic-cd-jewel-case-with-a-hinged-transp_...61eddc85`** — 标准刚性透明珠宝盒（**三槽基线 + N=1 multiplicity 基线**）。`base`(root) = 透明 `base_frame`（开顶薄壳 `_shallow_shell` L60-69 / `_base_frame` L72-74）+ 暗色 `inner_tray`（中心轮毂 hub + 8 齿 rosette + 两个前指槽，`_tray_solid` L77-123）。`lid` = 透明 `lid_shell`（`_lid_shell` L126-144）。`disc` = 银碟 `disc_body` + 偏心 `disc_marker`（`_disc_solid` L147-157）。关节：`base_to_lid` REVOLUTE 后缘 +Y、axis +X、0→70°（L201-209）；`hub_to_disc` CONTINUOUS axis +Z 父=base（L232-240）。run_tests 校验 lid 透明/上掀、hinge 沿 X、disc 偏心 marker 旋转、disc 落轮毂、tray 嵌入 frame（captured-pin allow_overlap）。可读性契约样板：clear shell + dark center-hub tray + 摆盖 + 旋碟。

- **S2 `rec_cd_jewel_case_var_body_slimline`** — slimline 薄盒。Slot A 拓扑差异：`base` 退化成超薄透明 `base_plate`（`_base_plate_geom` L151-153，1mm，无深 frame 裙），**dark tray 迁移进 lid**（`lid` = `lid_cover` + `lid_tray`，`_lid_cover_geom` L156-179 / `_lid_tray_geom` L182-189，hub 朝 -Z 向下）；`disc` 的 `hub_to_disc` CONTINUOUS **父=lid**（L274-283），随盖开合。`base_to_lid` REVOLUTE axis **-X**（L238-249）。闭合高度 ~5mm（≈标准一半）。run_tests 断言闭合高度 0.003–0.008、base 薄(<2mm)、tray 在 lid 不在 base、disc 随 lid 开合（L306-406）。这是 slimline 候选源，确立"托盘上盖 + disc 父=lid"拓扑。

- **S3 `rec_cd_jewel_case_var_body_doublewide`** — 双倍宽多槽盒。Slot A：`CASE_W=0.284`（≈2×标准），`base` = base_frame + 单一共享 `tray_floor`（带中央 divider 脊 + 每槽指槽，`_tray_floor` L128-164）+ **for-loop 发射的 `hub_rosette_{i}`**（`_hub_rosette(x_offset)` L92-125，沿 `HUB_X[]` 偏置，L223-228）。lid 跨全宽（≥80%，L403-410）。单碟坐在 `HUB_X[DISC_SLOT]`（L264-294）。run_tests 断言宽≥0.25、深不变、两 hub 分离≥0.10、lid 跨 80%。这是 doublewide 候选源，也是共面 multiplicity 的"共享 tray_floor + 多 hub boss"placement 参照。

- **S4 `rec_cd_jewel_case_var_body_digipak`** — 数码纸盒书折。Slot A 根本不同：**无刚性壳、不是 clamshell** —— `tray_panel`(root) = 不透明 `cardboard` `tray_board` + `spine` 脊条 + 暗塑 `disc_tray`（molded 中心轮毂，`_disc_tray` L67-104，胶在 +X 板上）；`cover_panel` = 不透明 `cover_board`（L160-178）；`spine_fold` REVOLUTE **axis +Y** 0→170°（L183-194，书脊折叠即闭合机构）；`hub_to_disc` CONTINUOUS（L216-224）。run_tests 断言面板不透明(alpha≥0.95)、cover 绕 Y 上折、disc 落轮毂、cover 接触 spine。这是 digipak 候选源 —— **body_type 自带耦合 closure（spine fold），不与 3 个刚性 closure 共存**。

- **S5 `rec_cd_jewel_case_var_hinge_topflip`** — 侧翻盖。Slot B：`_lid_shell` 平移使 hinge 边在 x=0、body 向 -X（L124-145），`base_to_lid` REVOLUTE 原点 `(HINGE_X,0,HINGE_Z)`、**axis +Y**、0→70°（L202-210，绕 +X 短边翻、自由 -X 边上掀）。base 仍是 baseline center-hub（L168-185）。run_tests 断言 hinge 沿 Y、原点在 +X 边、自由边右移上掀。这是 topflip closure 候选源。

- **S6 `rec_cd_jewel_case_var_hinge_slidingsleeve`** — 滑套（无铰链）。Slot B：`base` = baseline frame + center-hub tray；新增 `sleeve`（透明 slipcase tube，`_sleeve_shell` L124-152，-X 端开口）；`base_to_sleeve` **PRISMATIC axis +X** 0→0.17m（L209-217）。`allow_isolated_part` + 闭合 overlap 证明（L264-279）代替接触。run_tests 断言 prismatic、沿 X、滑开露 base。这是 slidingsleeve closure 候选源，确立"滑套 PRISMATIC + isolated-part 闭合证明"拓扑。

- **S7 `rec_cd_jewel_case_var_tray_trayless`** — 无盘托口袋。Slot C：删 hub/rosette/spin —— `base` = frame + 纸/布 `sleeve_pocket`（`_sleeve_pocket` L74-117，-Y 前缘开口，顶面圆窗）+ **inline `disc_body` 作为 base visual（固定，无 part、无 spin joint）**（L174-179）。仅 `base_to_lid` REVOLUTE。run_tests 显式断言无 inner_tray、无 CONTINUOUS 关节、恰好 2 parts（L284-307）。这是 trayless 候选源，"碟平躺口袋、固定不旋"下界拓扑（**N=1 only**）。

- **S8 `rec_cd_jewel_case_var_tray_dualsided`** — 双面翻托。Slot C：`base` = frame + `pivot_post_{0,1}` 轴承柱（`_pivot_post` L93-106）；新增 `flip_tray` part = `tray_panel`（带前指槽 + 侧柱让位槽 + **整体 pivot 销**，`_tray_panel` L146-194）+ **两面 hub** `hub_face_{0,1}`（`_hub_face(face_sign)` L109-143）；`base_to_flip_tray` REVOLUTE **axis +X** 0→π（L282-292，绕中央 X 轴翻 180°）；`disc` 的 `tray_to_disc` CONTINUOUS **父=flip_tray**（L338-346）。run_tests 断言双 hub 上下、翻 180° 留 footprint、disc 父=flip_tray、销座接触 post。这是 dualsided_flip 候选源，"中央 X 翻托 + 双面轮毂 + disc 父=翻托"拓扑（**需 base 刚性 frame 装柱 + 摆/翻顶盖让翻**）。

- **S9 `rec_cd_jewel_case_var_tray_bookletclip`** — 小册夹。Slot C：**baseline center-hub tray 不变**（L229-246），lid 内面**追加** 4 个 `clip_{i}`（`_booklet_clip` L186-203，for-loop L260-266）夹持 `booklet_card`（`_booklet_card` L206-219）。`base_to_lid` REVOLUTE（L283-291）、`hub_to_disc` CONTINUOUS（L314-322）不变。run_tests 断言 4 clip + card 存在、card 在 lid 内面、随 lid 开合、clip 唇压 card（element allow_overlap）。这是 bookletclip 候选源 —— **lid 侧加法特征，tray 拓扑不变；需有摆/翻顶盖承载夹**。

- **S10 `rec_cd_jewel_case_var_discs_n2`** — 双碟共面（multiplicity N=2 第一种 copy-logic）。`CASE_W=0.270`（沿 X 加宽），`TRAY_SECTION_W=(CASE_W-2WALL)/N`（L47），`disc_cx(i)` 均匀分布（L64-66）；**for-loop**：每槽 `_tray_section(cx)`（floor+hub+rosette+notch，L88-132）→ `tray_{i}`（L185-191），每碟 `disc_{i}`（`disc_{i}_body`/`disc_{i}_marker`）+ `hub_to_disc_{i}` CONTINUOUS axis +Z **父=base**（L224-253）。共享单 base/lid。run_tests 断言两 tray/两独立旋碟、共面同高、各自落槽。这是**共面 copy-logic** 源：N 个并列 CONTINUOUS 旋碟全父=base，沿 X 均布。

- **S11 `rec_cd_jewel_case_var_discs_n4`** — 四碟堆叠书页（multiplicity N=4 第二种 copy-logic）。`NUM_DISCS=4`，**加高** `base_frame`（`WALL_H=0.034`，`_base_frame` L78-86）；**for-loop**：每页 `leaf_{i}`（共享 `leaf_mesh`，`_leaf_plate` L89-148，hub+rosette+notch+hinge barrel）+ `base_to_leaf_{i}` REVOLUTE **axis -X** 0→120° 在 `_leaf_hinge_z(i)=LEAF_FIRST_Z+i·LEAF_SPACING`（L263-274）；每碟 `disc_{i}` + `leaf_{i}_to_disc_{i}` CONTINUOUS axis +Z **父=该 leaf**（L293-301）。单顶 `lid`。run_tests 断言 4 页/4 碟、各页上掀、各碟旋、页 Z 递增堆叠。这是**堆叠书页 copy-logic** 源（N≥3）：每碟旋相对**自己的铰链页**（父=leaf 非 base），沿 +Z 堆叠，加高 frame。

跨样本观察：全 11 样本共享 `_shallow_shell` 开顶壳 helper、`_tray_solid/_tray_section/_hub_rosette` 的 hub+8 齿 rosette+前指槽词汇、`_disc_solid`（120mm 银碟 + 中心孔 + 偏心 marker）、captured-hub `allow_overlap`（hub 穿碟孔捕获）、`hub_to_disc` CONTINUOUS +Z 旋碟检查（偏心 marker quarter-turn）。配色高度一致（clear_plastic alpha≈0.30 / tray_dark≈0.10 / disc_silver≈0.82；digipak/trayless 例外用不透明 cardboard/paper），为 §7 `palette_style` 提供基线 + 现实 colorway。差异严格落在 4 个轴上：**(A) body_type 壳体形态**、**(B) closure_hinge 开合机构**、**(C) inner_tray 持碟机构**、**(N) disc_count 复制数 + copy-logic**。

## 核心身份

CD 珠宝盒（CD jewel case）：一个**扁平矩形塑料盒**，footprint 约 0.142(X)×0.125(Y) m（单碟，容纳 120mm 标准光盘 `DISC_R=0.060`），含一个**开合机构**与一个**持碟机构**。世界系约定：盒平铺 XY 面、+Z 向上；X=盒宽、Y=盒深；后缘铰链沿 +Y 边、铰链轴沿 X；前指槽在 -Y 边；z=0 为壳体底面，装配向 +Z 堆叠。碟为 120mm 圆盘（`DISC_R=0.060`、`DISC_T=0.0012`、中心孔 `DISC_HOLE_R=0.0075`），落在中心轮毂 rosette 上、绕 +Z CONTINUOUS 旋转（trayless 例外：碟固定平躺、不旋）。

成熟域：标准透明刚性珠宝盒（clear shell + dark center-hub tray + 后缘摆盖 + 旋碟），及其现实变体 —— slimline 薄盒（托盘上盖）、doublewide 双宽（多 hub 槽）、digipak 不透明纸书折；开合可为后缘摆盖 / 侧翻盖 / 滑套 / digipak 书脊折；持碟可为中心轮毂 / 无盘托口袋 / 双面翻托 / 小册夹；碟数 N 可 1（单 hub）/ 2（共面并列）/ 3–6（堆叠书页）。身份强约束：

- **必须**是扁平矩形、容纳至少一张 120mm 圆盘的盒（footprint 由碟径派生，留壁间隙）。
- **必须**有一个开合机构（摆盖 / 侧翻 / 滑套 / 书脊折之一），且为非 fixed 关节。
- **除 trayless 外必须**有中心轮毂 rosette 捕获碟 + CONTINUOUS 旋碟（hub 穿碟孔的 captured-pin overlap）。
- 透明/半透明塑料壳是默认身份；**digipak 不透明纸卡 + trayless 不透明纸口袋**是仅有的两个不透明例外。

边界（不该混入）见 §11。

## 槽位 + 候选模块表

### Slot A：body_type（主 footprint 槽 —— 壳体形态；决定 root part 树、壳厚/宽、tray 归属面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `standard_rigid`（基线） | S1 `rec_clear-plastic-cd-jewel-case-with-a-hinged-transp_...61eddc85` | `model.py:L40-L57`(dims)、`L60-L74`(`_shallow_shell`/`_base_frame`)、`L160-L184`(base = base_frame + inner_tray) | eligible if compatible | 标准刚性透明珠宝盒：`base`(root) = 透明开顶 `base_frame` 薄壳 + 暗色 `inner_tray`，全高 ~10mm。tray 在 base 上；lid 内面空。承载全部 closure/tray 候选。 |
| `slimline` | S2 `rec_cd_jewel_case_var_body_slimline` | `model.py:L44-L64`(dims)、`L151-L189`(`_base_plate_geom`/`_lid_cover_geom`/`_lid_tray_geom`)、`L201-L234`(base 薄板 + lid 携 tray) | eligible if compatible | 薄盒：`base` 退化为超薄透明 `base_plate`（1mm，无深 frame 裙），**dark tray 迁移到 lid**（`lid_cover`+`lid_tray`，hub 朝 -Z）；`disc` 父=lid。闭合高 ~5mm。**part 归属拓扑不同**（tray 在 lid、disc 父=lid）。 |
| `doublewide` | S3 `rec_cd_jewel_case_var_body_doublewide` | `model.py:L43-L69`(dims/HUB_X/N_DISC_SLOTS)、`L92-L164`(`_hub_rosette`/`_tray_floor`)、`L207-L234`(base = frame + tray_floor + hub_rosette_{i} loop) | eligible if compatible | 双宽多槽壳：`CASE_W≈2×`，单一共享 `tray_floor`（中央 divider 脊）+ **for-loop `hub_rosette_{i}`** 沿 X 排布；lid 跨全宽 ≥80%。提供共面多碟的"共享 floor + 多 hub boss"footprint。 |
| `digipak` | S4 `rec_cd_jewel_case_var_body_digipak` | `model.py:L34-L56`(dims)、`L61-L104`(`_cardboard_panel`/`_disc_tray`)、`L130-L194`(tray_panel root + cover_panel + `spine_fold`) | eligible if compatible | 不透明纸书折盒：`tray_panel`(root) = `cardboard` `tray_board` + `spine` 脊条 + 暗塑 molded `disc_tray`；`cover_panel` 不透明纸卡。**无刚性壳、不是 clamshell**；`spine_fold` REVOLUTE +Y 即闭合（**自带耦合 closure，见 Slot B 派生行**），inner_tray 锁定 digipak 原生 center-hub disc_tray。 |

> Slot A 四候选结构差异充分：`standard_rigid` vs `slimline` 是 tray/disc 归属面变化（base→lid，part 树拓扑变），`doublewide` 是加宽 + 多 hub boss（footprint + 复制结构），`digipak` 是**整套 root 替换**（无壳、纸面板、书脊折耦合 closure）。非尺寸/颜色微变。

### Slot B：closure_hinge（主机构槽 —— 开合机构；决定 closure 子件 part + joint 类型/轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `clamshell_swing`（基线） | S1 `rec_clear-plastic-cd-jewel-case-with-a-hinged-transp_...61eddc85` | `model.py:L126-L144`(`_lid_shell`)、`L187-L209`(lid part + `base_to_lid` REVOLUTE +X 0→70°) | eligible if compatible | 后缘摆盖：透明 `lid_shell`，`base_to_lid` REVOLUTE 原点后 +Y 边、axis +X、0→70°；hinge 沿 X 左右走，自由 -Y 前缘上掀。承载全部 tray 候选。 |
| `topflip` | S5 `rec_cd_jewel_case_var_hinge_topflip` | `model.py:L45`(HINGE_X)、`L124-L145`(`_lid_shell` 平移)、`L202-L210`(`base_to_lid` REVOLUTE +Y 0→70°) | eligible if compatible | 侧翻盖：hinge 转到 +X 短边，`base_to_lid` REVOLUTE 原点 `(HINGE_X,0,HINGE_Z)`、**axis +Y**、自由 -X 边上掀。joint 轴从 +X→+Y（拓扑差异）。 |
| `slidingsleeve` | S6 `rec_cd_jewel_case_var_hinge_slidingsleeve` | `model.py:L53-L67`(sleeve dims)、`L124-L152`(`_sleeve_shell`)、`L195-L217`(sleeve part + `base_to_sleeve` PRISMATIC +X)、`L264-L279`(isolated + 闭合证明) | eligible if compatible | 滑套（无铰链）：透明 `sleeve_shell`（-X 端开口 tube）套住 base，`base_to_sleeve` **PRISMATIC axis +X** 0→0.17m 滑出。无 lid part；用 `allow_isolated_part` + 闭合 overlap 证明替接触。**joint 拓扑 = PRISMATIC（非 REVOLUTE）**。 |
| `spine_fold`（digipak 耦合，派生非独立采样） | S4 `rec_cd_jewel_case_var_body_digipak` | `model.py:L160-L194`(cover_panel + `spine_fold` REVOLUTE +Y 0→170°) | conditional：**仅当 body_type=digipak 时强制启用，不进入 B 的独立采样池** | digipak 自带书脊折闭合：`cover_panel` 不透明纸卡绕 `spine`（x=0）REVOLUTE **axis +Y** 0→170° 翻合。是 body-coupled closure，与 3 个刚性 closure 互斥（digipak 无刚性壳可摆/翻/套）。 |

> Slot B **3 个独立采样候选**（clamshell_swing / topflip / slidingsleeve）跨 **REVOLUTE +X / REVOLUTE +Y / PRISMATIC +X** 三种 joint 拓扑，是本模板拓扑多样性的主驱动槽之一。第 4 行 `spine_fold` 是 digipak body 的**耦合派生 closure**（不独立采样、由 body_type=digipak 触发），列入表以保接口完整、不计入"3 个采样候选"。

### Slot C：inner_tray（持碟机构槽 —— 决定持碟 part 是否活动 + 旋碟 joint 父级/拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `center_hub`（基线） | S1 `rec_clear-plastic-cd-jewel-case-with-a-hinged-transp_...61eddc85` | `model.py:L77-L123`(`_tray_solid`：hub+8 齿 rosette+2 指槽)、`L211-L240`(disc + `hub_to_disc` CONTINUOUS +Z 父=base) | eligible if compatible | 固定暗色 tray，单中心轮毂 rosette 捕获 1 碟；`hub_to_disc` CONTINUOUS axis +Z **父=base**。碟在 hub 上旋。承载 multiplicity（N≥1）。 |
| `trayless` | S7 `rec_cd_jewel_case_var_tray_trayless` | `model.py:L74-L117`(`_sleeve_pocket`)、`L160-L184`(base = frame + sleeve_pocket + **inline disc_body**)、断言 `L284-L307` | conditional：**仅 N=1**（无 hub/无 leaf，不能堆叠/并列） | 无盘托口袋：不透明纸/布 `sleeve_pocket`（前缘开口 + 顶圆窗），`disc_body` **inline 为 base visual（固定、无 part、无 spin joint）**。joint 拓扑 = 无旋碟件（恰好 2 parts，仅 closure 1 关节）。 |
| `dualsided_flip` | S8 `rec_cd_jewel_case_var_tray_dualsided` | `model.py:L93-L143`(`_pivot_post`/`_hub_face`)、`L146-L194`(`_tray_panel` 整体销)、`L255-L292`(flip_tray + `base_to_flip_tray` REVOLUTE +X 0→π)、`L319-L346`(disc 父=flip_tray) | conditional：需刚性 frame 装柱 + 可掀顶盖（standard_rigid/doublewide × clamshell/topflip） | 双面翻托：`base` 加 `pivot_post_{0,1}` 轴承柱，`flip_tray` part（`tray_panel`+双面 `hub_face_{0,1}`+整体 pivot 销）绕中央 X 轴 REVOLUTE 翻 180°；`disc` 的 `tray_to_disc` CONTINUOUS **父=flip_tray**。新增活动 part + 第三个非 fixed 关节。 |
| `bookletclip` | S9 `rec_cd_jewel_case_var_tray_bookletclip` | `model.py:L162-L219`(`_booklet_clip`/`_booklet_card`)、`L249-L273`(lid + clip_{i} loop + booklet_card)、断言 `L456-L518` | conditional：需可掀顶盖承载夹（standard_rigid/doublewide × clamshell/topflip） | baseline center-hub tray **不变**，lid 内面加 4 个 `clip_{i}` 夹持 `booklet_card`（lid 侧加法 visual，无新关节）。tray + 旋碟拓扑同 `center_hub`，差异在 lid 内多一组夹 + 册。 |

> Slot C 四候选跨 **CONTINUOUS 父=base（center_hub）/ 无旋碟件（trayless）/ 第三 REVOLUTE 翻托 + CONTINUOUS 父=flip_tray（dualsided_flip）/ center_hub + lid 加法（bookletclip）** 四种持碟拓扑。`trayless` 是无旋碟下界（N=1），`dualsided_flip` 引入额外活动 part + 翻转关节，是本模板拓扑多样性另一主驱动槽。

## 槽位图（slot graph）

pattern = `mixed`（parallel children over A/B/C + 一根 multiplicity 轴 disc_count，N 选 copy-logic）

```
# ── 刚性壳体路径（body_type ∈ {standard_rigid, slimline, doublewide}）──
[base]  (root：透明 base_frame/base_plate；z=0 底面；rigid frame 提供 closure/tray/post 锚)
   |
   |-- [Slot B closure] :
   |       · clamshell_swing :  base --REVOLUTE base_to_lid (origin (0,+HINGE_Y,HINGE_Z), axis +X, 0→lid_open)--> [lid]
   |       · topflip        :  base --REVOLUTE base_to_lid (origin (+HINGE_X,0,HINGE_Z), axis +Y, 0→lid_open)--> [lid]
   |       · slidingsleeve  :  base --PRISMATIC base_to_sleeve (origin (0,0,SL_JOINT_Z), axis +X, 0→sleeve_travel)--> [sleeve]
   |
   |-- [Slot C tray] + [Multiplicity disc_count N] :
   |       · center_hub (N=1)      : disc --CONTINUOUS hub_to_disc (origin (0,0,disc_z), axis +Z, 父=base)
   |       · center_hub (N=2 共面) : for i: disc_{i} --CONTINUOUS hub_to_disc_{i} (origin (disc_cx(i),0,DISC_Z), axis +Z, 父=base)   ← 加宽 CASE_W、tray_{i} 并列
   |       · center_hub (N≥3 书页) : for i: leaf_{i} --REVOLUTE base_to_leaf_{i} (origin (0,LEAF_HINGE_Y,_leaf_hinge_z(i)), axis -X, 0→120°)
   |                                          └ disc_{i} --CONTINUOUS leaf_{i}_to_disc_{i} (origin (0,hub_cy,disc_z_in_leaf), axis +Z, 父=leaf_{i})   ← 加高 base_frame
   |       · trayless (N=1)        : disc_body 作为 base visual（无 part / 无 joint）；sleeve_pocket 口袋
   |       · dualsided_flip (N=1)  : base(+pivot_post_{0,1}) --REVOLUTE base_to_flip_tray (origin (0,0,PIVOT_Z), axis +X, 0→π)--> [flip_tray(双面 hub)]
   |                                          └ disc --CONTINUOUS tray_to_disc (origin (0,0,disc_hub_z), axis +Z, 父=flip_tray)
   |       · bookletclip (N=1)     : center_hub disc 同上（父=base）+ lid 内 clip_{i}/booklet_card visual（挂 lid，无 joint）
   |
   +-- [slimline 派生]：tray(center_hub) 改挂 lid（lid_tray），disc 的 hub_to_disc 父=lid（随盖开合）

# ── digipak 路径（body_type = digipak，整套 root 替换）──
[tray_panel]  (root：不透明 cardboard tray_board + spine 脊 + molded disc_tray)
   |-- [Slot B = spine_fold 耦合]  tray_panel --REVOLUTE spine_fold (origin (0,0,PANEL_T/2), axis +Y, 0→170°)--> [cover_panel]
   +-- [Slot C = digipak center_hub]  tray_panel --CONTINUOUS hub_to_disc (origin (TRAY_CENTER_X,0,DISC_SEAT_Z), axis +Z)--> [disc]
```

接口点位与装配说明：

- **base → closure**：
  - clamshell_swing：joint origin 后 +Y 边 `(0, CASE_D/2, HINGE_Z=base 顶)`，axis +X；lid local 原点坐 hinge 线、body 向 -Y。q=0 闭合盖顶。
  - topflip：joint origin 右 +X 短边 `(CASE_W/2, 0, HINGE_Z)`，axis +Y；lid body 向 -X、自由边 -X 上掀。
  - slidingsleeve：joint origin `(0,0,SL_JOINT_Z)`（套腔中心高），axis +X，PRISMATIC 0→stroke；sleeve 内腔 = base 内容 + 全向 clearance，闭合时 base 嵌套腔内（`allow_isolated_part` + 闭合 overlap 证明，非接触）。
- **base/flip_tray/lid/leaf → disc（旋碟接口）**：disc 中心孔 `DISC_HOLE_R` 落 hub（`HUB_R`），hub 穿孔捕获（element-scoped `allow_overlap`：`disc_body ↔ inner_tray/tray_{i}/hub_rosette_{i}/hub_face_0/leaf_plate_{i}`）。`hub_to_disc` CONTINUOUS axis +Z，**父级随 Slot C / body_type 派生**：center_hub 父=base；slimline 父=lid；dualsided_flip 父=flip_tray；N≥3 书页 父=各 leaf_{i}。
- **dualsided_flip 专属接口**：`pivot_post_{0,1}` 立在 base frame 两侧壁内（`POST` 尺寸 L71-74），`flip_tray` 的整体 pivot 销座入柱（`allow_overlap` tray_panel↔pivot_post_{i} + `expect_contact`，L487-516）；翻轴 `base_to_flip_tray` REVOLUTE axis +X 在 `PIVOT_Z`。
- **digipak 专属接口**：`cover_board` 在 q=0 平开时接触 `spine`（`expect_contact`，L334-341）；disc_tray molded 在 +X tray_board 上、disc 落其 hub。
- **互斥 / 派生关系（详见 §9 compatibility matrix）**：digipak 整套替换 root 并耦合 spine_fold + 锁定 center_hub disc_tray；slidingsleeve 无 lid → 不承载 dualsided_flip/bookletclip；trayless 无 hub → N=1 only；dualsided_flip/bookletclip 需可掀顶盖（clamshell/topflip）+ 刚性 frame；topflip/slidingsleeve 沿 X → 不与共面 N≥2 加宽共存；slimline tray 在 lid → 锁定 center_hub + clamshell_swing。

## 每槽位 Module Emits / Interfaces

### Slot A / module `standard_rigid`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`(root) = `base_frame`（透明开顶薄壳）+ `inner_tray`（中心 hub+rosette+前指槽，由 Slot C 决定是否替换） | S1 / model.py:L160-L184 |
| internal joints | 无（base 内为 visual 组） | — |
| upstream interface | root；z=0 底面着地；frame 顶 `HINGE_Z=BASE_T` 供 closure 锚，frame 两侧壁供 dualsided pivot_post 锚 | S1 / model.py:L47-L48, L168-L184 |
| downstream interface | closure joint 原点（后 +Y 边 / 右 +X 边 / 套腔中心）；tray/disc 锚（中心 hub 轴 (0,0,disc_z)） | S1 / model.py:L201-L240 |

### Slot A / module `slimline`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` = 超薄 `base_plate`（无 frame 裙）；`lid` = `lid_cover` + **`lid_tray`（dark tray 迁移上盖）** | S2 / model.py:L201-L234 |
| internal joints | 无 | — |
| upstream interface | root base_plate；`HINGE_Z=BASE_PLATE_T+LID_DEPTH`(~5mm)，hinge axis **-X** | S2 / model.py:L57-L58, L238-L249 |
| downstream interface | disc 的 `hub_to_disc` CONTINUOUS **父=lid**（碟随盖开合）；锁定 center_hub + clamshell_swing | S2 / model.py:L271-L283 |

### Slot A / module `doublewide`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` = `base_frame`(加宽) + `tray_floor`(中央 divider) + **for-loop `hub_rosette_{i}`**；`lid_shell` 跨全宽 | S3 / model.py:L207-L234 |
| internal joints | 无 | — |
| upstream interface | root；`CASE_W≈2×`；`HUB_X[]` 沿 X 排 hub boss（press-fit 嵌 tray_floor，element allow_overlap） | S3 / model.py:L64-L69, L223-L228 |
| downstream interface | lid 跨 ≥80% 宽（`expect_overlap` min=CASE_W*0.8）；disc 落 `HUB_X[DISC_SLOT]`；为共面 multiplicity 提供 footprint | S3 / model.py:L286-L294, L403-L410 |

### Slot A / module `digipak`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tray_panel`(root) = `tray_board`(纸) + `spine`(脊条) + `disc_tray`(暗塑 molded hub)；`cover_panel` = `cover_board`(纸) | S4 / model.py:L130-L178 |
| internal joints | `spine_fold` REVOLUTE +Y 0→170°（耦合 closure，见 Slot B 派生行） | S4 / model.py:L183-L194 |
| upstream interface | root tray_panel；spine 在 x=0 fold 线、tray_board 在 +X、cover 从 -X 折过来 | S4 / model.py:L46, L130-L145 |
| downstream interface | disc `hub_to_disc` CONTINUOUS 在 `(TRAY_CENTER_X,0,DISC_SEAT_Z)`；不透明纸 + 锁定 center_hub disc_tray；排斥 3 刚性 closure | S4 / model.py:L216-L224 |

### Slot B / module `clamshell_swing`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`(透明 `lid_shell`) | S1 / model.py:L187-L192 |
| internal joints | `base_to_lid` REVOLUTE origin 后 +Y 边、axis +X、0→lid_open（70° 基线） | S1 / model.py:L201-L209 |
| upstream interface | lid local 原点坐后缘 hinge 线 `(0, CASE_D/2, BASE_T)` | S1 / model.py:L201-L206 |
| downstream interface | lid 内面供 bookletclip 挂 clip/card；闭合 q=0 盖顶 | S1 / model.py:L126-L144 |

### Slot B / module `topflip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`(透明 `lid_shell`，平移使 hinge 在 +X 边、body 向 -X) | S5 / model.py:L188-L193 |
| internal joints | `base_to_lid` REVOLUTE origin `(CASE_W/2,0,BASE_T)`、**axis +Y**、0→lid_open | S5 / model.py:L202-L210 |
| upstream interface | lid local 原点坐右 +X 短边 hinge 线 | S5 / model.py:L124-L145 |
| downstream interface | lid 内面供 bookletclip 挂载；自由 -X 边上掀 | S5 / model.py:L271-L301 |

### Slot B / module `slidingsleeve`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sleeve`(透明 `sleeve_shell` tube，-X 端开口) | S6 / model.py:L195-L200 |
| internal joints | `base_to_sleeve` PRISMATIC axis +X 0→stroke(0.17) | S6 / model.py:L209-L217 |
| upstream interface | 套腔内尺寸 = base 内容 + `SL_CLEAR` 全向间隙；joint origin `(0,0,SL_JOINT_Z)`；`allow_isolated_part` + 闭合 overlap 证明 | S6 / model.py:L53-L67, L264-L279 |
| downstream interface | 无 lid 内面 → 不承载 bookletclip/dualsided_flip（gating） | S6 / 排除项 |

### Slot B / module `spine_fold`（digipak 耦合，派生）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover_panel`(不透明 `cover_board` 纸卡) | S4 / model.py:L160-L178 |
| internal joints | `spine_fold` REVOLUTE axis +Y 0→170°，绕 spine(x=0) | S4 / model.py:L183-L194 |
| upstream interface | 仅 body_type=digipak 触发；joint origin `(0,0,PANEL_T/2)`；cover 平开接触 spine | S4 / model.py:L183-L194, L334-L341 |
| downstream interface | 无（终端活动件） | — |

### Slot C / module `center_hub`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `inner_tray`(hub+8 齿 rosette+2 前指槽，base/lid 上的 visual)；`disc` part(`disc_body`+`disc_marker`) | S1 / model.py:L77-L123, L211-L224 |
| internal joints | `hub_to_disc` CONTINUOUS axis +Z；**父级由 body 派生**（base / lid(slimline) / leaf(N≥3) / flip_tray） | S1 / model.py:L232-L240 |
| upstream interface | hub 穿碟孔捕获（`disc_body↔inner_tray` element allow_overlap）；disc 中心轴 (0,0,disc_z) | S1 / model.py:L322-L351 |
| downstream interface | 承载 multiplicity（N≥1 复制）；disc 在 footprint 内、落 hub 上 | S1 / model.py:L330-L351 |

### Slot C / module `trayless`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sleeve_pocket`(不透明纸/布口袋，前开口+顶窗，base visual)；`disc_body` **inline base visual**（无 disc part） | S7 / model.py:L160-L184 |
| internal joints | 无（碟固定、无 CONTINUOUS） | S7 / model.py:L284-L293 |
| upstream interface | 口袋嵌 base frame（element allow_overlap）；碟平躺口袋腔（`disc_body↔sleeve_pocket` allow_overlap） | S7 / model.py:L336-L372 |
| downstream interface | 无；显式断言无 inner_tray、无 CONTINUOUS、恰好 2 parts → **N=1 only** | S7 / model.py:L266-L307 |

### Slot C / module `dualsided_flip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | base 加 `pivot_post_{0,1}`；`flip_tray` part(`tray_panel`+双面 `hub_face_{0,1}`+整体 pivot 销)；`disc` part | S8 / model.py:L235-L278, L319-L335 |
| internal joints | `base_to_flip_tray` REVOLUTE axis +X 0→π；`tray_to_disc` CONTINUOUS axis +Z **父=flip_tray** | S8 / model.py:L282-L292, L338-L346 |
| upstream interface | pivot 销座入 `pivot_post_{i}`（element allow_overlap + expect_contact）；翻轴 PIVOT_Z | S8 / model.py:L487-L516 |
| downstream interface | disc 在上 hub_face_0 旋（element allow_overlap `disc_body↔hub_face_0`）；需 base 刚性 frame + 可掀顶盖 | S8 / model.py:L462-L485 |

### Slot C / module `bookletclip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | center_hub `inner_tray` + `disc`（同基线）；lid 加 4×`clip_{i}` + `booklet_card`（lid visual，无 part） | S9 / model.py:L237-L273 |
| internal joints | `hub_to_disc` CONTINUOUS 父=base（同 center_hub）；clip/card 无 joint（随 lid 走） | S9 / model.py:L314-L322 |
| upstream interface | clip 唇压 card 边（element allow_overlap `clip_{i}↔booklet_card`） | S9 / model.py:L510-L518 |
| downstream interface | card 在 lid 内面、随 lid 开合上掀；需可掀顶盖（clamshell/topflip） | S9 / model.py:L473-L506 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_type` | enum | `standard_rigid` / `slimline` / `doublewide` / `digipak` | `standard_rigid` | choice | deterministic procedural sampler 选择；决定 root part 树 + tray 归属 + 是否耦合 spine_fold | Slot A 表 |
| `closure_hinge` | enum | `clamshell_swing` / `topflip` / `slidingsleeve` | `clamshell_swing` | choice | sampler 选择（3 候选）；body=digipak 时被 `spine_fold` 覆盖（不采样） | Slot B 表 |
| `inner_tray` | enum | `center_hub` / `trayless` / `dualsided_flip` / `bookletclip` | `center_hub` | choice | sampler 选择；受 §9 compatibility gate（body/closure/N 约束） | Slot C 表 |
| `disc_count`(N) | int | [1, 6] | 1 | choice(weighted) | multiplicity 轴；N 选 copy-logic（1 单 / 2 共面 / ≥3 书页）；受 §8 加权 + §9 gate | §8 / S1,S10,S11 |
| `palette_style` | enum | `clear_frame_black_tray` / `clear_frame_white_tray` / `frosted_grey` / `smoked_tint_black` / `opaque_coloured_card` / `translucent_colour_tray` | `clear_frame_black_tray` | choice | 每 seed 采样 colorway；仅改 material rgba（按 element 角色），不改拓扑/尺寸/接口 | 全 11 源 material 观察派生 |
| `case_margin_scale` | float | [0.9, 1.30] | 1.0 | independent | 碟边到壳内壁的间隙缩放；footprint = 2·DISC_R + 2·margin。clamp | S1 `CASE_W/CASE_D` vs `DISC_R` L40-50 |
| `case_height_scale` | float | [0.85, 1.25] | 1.0 | independent | frame 深度(Z) / WALL_H 缩放；闭合内高须容 tray+hub+disc。clamp | S1 `BASE_T`/`HUB_H` L42-55；S11 `WALL_H` L43 |
| `hub_radius_scale` | float | [0.92, 1.12] | 1.0 | independent | hub 外径缩放；须保持对碟孔的捕获过盈带。clamp | S1 `HUB_R` vs `DISC_HOLE_R` L52-54 |
| `lid_open_deg` | float | [60, 85] | 70 | independent | clamshell/topflip 开盖上限；digipak spine 用 `spine_open_deg` | S1 `base_to_lid` upper L208 |
| `spine_open_deg` | float | [150, 175] | 170 | conditional | 仅 body=digipak；书脊折上限 | S4 `spine_fold` upper L192 |
| `disc_radius` | float | fixed 0.060 | 0.060 | constant | **不采样**（真实 120mm CD = 类别 identity）；footprint 由它派生 | S1 `DISC_R` L50 |
| `case_width`(派生) | float | derived | — | equation | `= max(2·DISC_R+2·WALL+2·margin, N_coplanar·(2·DISC_R+2·WALL))`（共面时按 N 加宽）；不独立采样 | S3 `CASE_W` L44；S10 `TRAY_SECTION_W` L47 |
| `disc_seat_z`(派生) | float | derived | — | equation | `= tray_floor_z + floor_t + HUB_H·hub_radius_scale·0.7`（碟落 rosette 齿顶）；随 body/leaf 派生 | S1 L231；S11 `disc_z_in_leaf` L251 |
| `hub_to_disc.parent`(派生) | enum | derived | — | conditional | `= base`（center_hub/bookletclip/共面）/ `lid`（slimline）/ `flip_tray`（dualsided）/ `leaf_{i}`（N≥3 书页）；由 body+tray+N 派生 | §槽位图接口说明 |
| `sleeve_travel`(派生) | float | derived | — | equation | 仅 closure=slidingsleeve；`= case_width − overlap_min`，确保滑开完全露 base | S6 `upper=0.17` L216 |
| `leaf_spacing`(派生) | float | derived | — | conditional | 仅 N≥3 书页；`= max(DISC_T+HUB_H+clear, base_h_room/(N))`，确保堆叠不撞 | S11 `LEAF_SPACING` L48 |
| (—) | constraint | — | — | inequality | **碟容纳**：壳内半宽/半深 ≥ DISC_R + 0.003 clearance。违反 → 抬 `case_margin_scale` 下限重采。 | S1 disc-within L330-338 |
| (—) | constraint | — | — | inequality | **闭合内高**：闭合时壳内高 ≥ floor_t + HUB_H·scale + DISC_T + 0.001，盖不压碟。违反 → 抬 `case_height_scale`。 | S1 disc_bottom L346-351 |
| (—) | constraint | — | — | inequality | **hub 捕获带**：`DISC_HOLE_R < HUB_R·hub_radius_scale < DISC_HOLE_R + 0.0035`（hub 穿孔捕获但不撑裂）；违反 → clamp `hub_radius_scale`。 | S1 captured-hub allow_overlap L322-329 |
| (—) | constraint | — | — | inequality | **共面分槽不撞**（N≥2 共面）：`TRAY_SECTION_W = case_width/N ≥ 2·DISC_R + 2·WALL`；违反 → 按 N 加宽 case_width 或拒绝重采。 | S10 `TRAY_SECTION_W`/disc 共面 L47, L350-355 |
| (—) | constraint | — | — | inequality | **书页堆叠不撞**（N≥3）：`WALL_H ≥ LEAF_FIRST_Z + (N−1)·leaf_spacing + DISC_T + HUB_H + 0.002`；违反 → 按 N 抬 WALL_H（case_height_scale）。 | S11 leaf-stack L446-454 |
| (—) | constraint | — | — | inequality | **滑套闭合包覆**（slidingsleeve）：套内腔 ≥ base 内容 + SL_CLEAR；闭合 overlap ≥ 0.08。违反 → 放大套腔。 | S6 closed-cover L271-279 |

`palette_style` colorway 取值（rgba 仅示意，下游模板按 **element 角色** 落实：clear-shell 角色才施 alpha；digipak 纸卡 / trayless 纸口袋恒不透明 alpha=1）：
- `clear_frame_black_tray`（基线）：clear shell (0.55,0.60,0.68,0.30)、tray (0.10,0.10,0.12,1.0)、disc (0.80,0.82,0.85,1.0)。（= S1 基线）
- `clear_frame_white_tray`：clear shell 同上、tray 浅灰白 (0.86,0.87,0.90,1.0)、disc 银。
- `frosted_grey`：磨砂半透 shell (0.70,0.72,0.74,0.45)、tray 中灰 (0.45,0.45,0.48,1.0)、disc 银。
- `smoked_tint_black`：烟熏染色 shell (0.20,0.20,0.24,0.40)、tray 黑 (0.10,0.10,0.12,1.0)、disc 银。
- `opaque_coloured_card`（digipak/trayless 不透明体优先）：不透明深红纸卡 (0.45,0.12,0.12,1.0) / cover (0.22,0.26,0.36,1.0)、暗塑 disc_tray (0.10,0.10,0.12,1.0)、disc 银。（= S4 cover_card 派生）
- `translucent_colour_tray`：clear shell (0.55,0.60,0.68,0.30) + 半透蓝托 (0.20,0.35,0.62,0.55)、disc 银（彩色 jewel-tray 现实款）。

## Multiplicity / Copy Logic

**一根 multiplicity 轴：`disc_count`（碟片复制数 N）**，N 按值选两种不同 copy-logic（共面并列 / 堆叠书页），并受 §9 slot gating。

- `count_param`：`disc_count`（N）
- `N_range`：**[1, 6]**（本小类产品域；测试偏小、产品全程）。1=单 hub 基线；2=共面并列；3–6=堆叠书页；>6 盒变得不切实际地厚，封顶 6。
- sampling domain（权重档：小 N 高频、大 N 稀有）：
  - N=1 ~55%（单碟最常见，5★ parent + 多数 variant）
  - N=2 ~22%（共面双碟，S10）
  - N=3 ~8% / N=4 ~9%（书页，S11 有源故 N=4 略高）/ N=5 ~3% / N=6 ~3%（尾部稀有）
- copied object / naming / placement / joint policy —— **按 N 区间分两套**（模板按 `disc_count` 与 Slot 选 copy-logic）：
  - **N=1（无复制）**：单 `disc` + 单 `hub_to_disc`（父级由 body/tray 派生）。
  - **N=2（共面并列 copy-logic，源 S10）**：
    - copied object：`_tray_section(cx)` floor+hub+rosette+notch（或 doublewide 的 `_hub_rosette(HUB_X[i])`）+ 每 section 一 `disc_{i}`。
    - naming：`tray_{i}` / `disc_{i}`（`disc_{i}_body` / `disc_{i}_marker`）/ `hub_to_disc_{i}`，i∈0..N-1。
    - placement：沿 X 均布 `disc_cx(i) = (i−(N−1)/2)·TRAY_SECTION_W`，`TRAY_SECTION_W=(CASE_W−2·WALL)/N`，加宽 `CASE_W`；共享单 `base`/`lid`。
    - joint policy：N 个并列 CONTINUOUS 旋碟，全 axis +Z、**全父=base**，共面同高。
    - source/gating：**仅 standard_rigid/doublewide × clamshell_swing × center_hub**（topflip/slidingsleeve 沿 X 与加宽冲突；trayless 无 hub）。
  - **N≥3（堆叠书页 copy-logic，源 S11）**：
    - copied object：共享 `leaf_mesh`/`disc_mesh`，`leaf_{i}`(页) + `disc_{i}` 沿 +Z 堆叠。
    - naming：`leaf_{i}`（`leaf_plate_{i}`）/ `disc_{i}`（`disc_body_{i}`/`disc_marker_{i}`）/ per-leaf material `leaf_dark_{i}`；joint `base_to_leaf_{i}` / `leaf_{i}_to_disc_{i}`。
    - placement：堆叠 +Z，`_leaf_hinge_z(i)=LEAF_FIRST_Z+i·leaf_spacing`，加高 `base_frame`(WALL_H) 单顶 `lid` 封盖。
    - joint policy：每页 `base_to_leaf_{i}` REVOLUTE axis -X 0→120°；每碟 `leaf_{i}_to_disc_{i}` CONTINUOUS axis +Z **父=各自 leaf**（非 base）。
    - source/gating：**仅 standard_rigid × clamshell_swing × center_hub**（书页需加高单盒摆盖、center-hub 页 hub）。
- 其它 multiplicity 说明：**hub rosette 的 8 齿是 module-local 固定循环（`for i in range(8)`）**，不暴露为模板 count 参数；dualsided 的双面 `hub_face_{0,1}` 与 pivot_post_{0,1}、bookletclip 的 4 clip 同为**固定循环**（左右/上下/四角各定数），非 multiplicity 轴。

## 拓扑多样性审计

总组合数（含 N 采样，经 §9 compatibility gate 后的**合法**拓扑组合，粗算）：

- N=1 单碟：
  - standard_rigid × {clamshell, topflip, sliding} × {center_hub, trayless, dualsided_flip, bookletclip}（sliding 仅配 center_hub/trayless；dualsided/bookletclip 仅配 clamshell/topflip）≈ 4+4+2 = **10**
  - doublewide × {clamshell, topflip, sliding} × {center_hub(+bookletclip/dualsided 仅 clamshell/topflip)} ≈ **6**
  - slimline × clamshell × center_hub = **1**
  - digipak × spine_fold × center_hub = **1**
  小计 ≈ **18**
- N=2 共面：{standard_rigid, doublewide} × clamshell × center_hub = **2**
- N=3/4/5/6 书页：standard_rigid × clamshell × center_hub，每个 N 是不同 part/joint 计数签名 = **4**

**合法拓扑组合 ≈ 18 + 2 + 4 = 24+**（远超 10）。


理由：Slot B 跨 REVOLUTE+X / REVOLUTE+Y / PRISMATIC 三种 joint 拓扑，Slot C 跨 CONTINUOUS-父base / 无旋碟 / 翻托+CONTINUOUS-父flip_tray / center_hub+lid加法 四种持碟拓扑，Slot A 跨刚性壳 / 托上盖(disc 父=lid) / 加宽多hub / digipak整套替换(纸面板+spine fold) 四种 root 拓扑，multiplicity N 又改 part/joint 计数签名（共面 N 个并列旋碟、书页 N 页 N 碟）。每个合法组合都改 part 树或 joint 图签名，24+ distinct 远超 10 门槛。`palette_style` 与连续 scale 不计入 topology 等价类。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG：(1) 加权采样 `body_type`（4 选 1，略偏 standard_rigid）；(2) 若 body=digipak → closure 强制 `spine_fold`、tray 强制 `center_hub`（耦合，跳过独立采样）；否则加权采样 `closure_hinge`（3 选 1）+ `inner_tray`（4 选 1）；(3) 加权采样 `disc_count` N（小 N 偏多）；(4) 过 §9 compatibility matrix 解析 gating（非法组合 fallback 见下表）；(5) 采样 `palette_style` + 所有 independent 连续 scale，按 equation 派生 case_width/disc_seat_z/hub_to_disc.parent/sleeve_travel/leaf_spacing，最后用 §7 inequality（碟容纳、闭合内高、hub 捕获带、共面分槽、书页堆叠、滑套包覆）投影回缩或拒绝重采。`slot_choices_for_seed(seed)` 返回稳定 `[(body_type,…),(closure_hinge,…),(inner_tray,…),(disc_count,N)]`（连续 scale 不进 slot_choices，除非改拓扑等价类——本模板不会）。gating 全在 `resolve_config` 求解，不留 builder 失败。`seed=0` 不特殊。无需 regression overrides（11 格全部一次收敛、5★ 源齐全）；若 sweep 暴露坏组合再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别 slot 池约束，合法拓扑组合 ≈ 24+（A 4 × B 3+1耦合 × C 4 × N 6，经 gating 大量裁剪）。<300 是**类别固有约束**（CD 盒结构词汇表有限 + 强 compatibility 排除）而非建模缺陷——视觉/比例多样性由 24+ 拓扑 × `palette_style`(6) × 连续 scale 谱共同提供。与 source map 组合数预审一致。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization（初版模板应含的关键连续 scale）：`case_margin_scale [0.9,1.30] independent`、`case_height_scale [0.85,1.25] independent`、`hub_radius_scale [0.92,1.12] independent`、`lid_open_deg [60,85] independent`（digipak 用 `spine_open_deg [150,175] conditional`）；派生 `case_width`（含共面 N 加宽 equation）、`disc_seat_z`(equation)、`hub_to_disc.parent`(conditional)、`sleeve_travel`(equation, slidingsleeve)、`leaf_spacing`(conditional, N≥3)。`disc_radius` 固定 0.060（类别 identity 不采样）。遵循连续尺寸采样契约：先采 independent → 派生 equation → 用 §7 inequality（碟容纳/闭合内高/hub 捕获/共面分槽/书页堆叠/滑套包覆）投影回缩。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（closure joint 锚、hub 捕获面、pivot_post 座、spine 接触）、MatingContract（hub 穿碟孔 captured-pin allow_overlap、滑套 isolated 闭合证明）或 multiplicity（共面均布 / 书页堆叠不撞）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A(body)→[digipak 耦合 gate]→B(closure)→C(tray)→N(disc_count)→palette→连续 scale；compatibility gate 在 resolve_config | `slot_choices_for_seed` 与 build choices 一致 |
| compatibility matrix | **排除/降级**：① digipak → 强制 closure=spine_fold + tray=center_hub（耦合，3 刚性 closure 与 trayless/dualsided/bookletclip 全 gate 掉）。② slidingsleeve × {dualsided_flip, bookletclip} 非法（无 lid 承载）→ fallback tray=center_hub 或 trayless。③ trayless 仅 N=1（无 hub/无 leaf）→ 若采到 N≥2 则 fallback N=1 或 tray=center_hub。④ dualsided_flip/bookletclip 需 closure∈{clamshell,topflip} + body∈{standard_rigid,doublewide}（需刚性 frame + 可掀盖）→ 否则 fallback center_hub。⑤ 共面 N≥2 仅 {standard_rigid,doublewide}×clamshell_swing×center_hub（topflip/sliding 沿 X 冲突加宽）→ 否则 N→1 或 closure→clamshell。⑥ 书页 N≥3 仅 standard_rigid×clamshell_swing×center_hub → 否则 N→1。⑦ slimline 仅 clamshell_swing×center_hub（tray 在盖）→ 否则 fallback standard_rigid。 | 无 floating / 无穿模 / 闭合盖不压碟 / 滑套闭合包覆 / 共面不撞 / 书页堆叠不撞 / disc 父级正确 |
| controlled local variation | 4 independent scale + 派生 case_width/disc_seat_z/parent/sleeve_travel/leaf_spacing；全 clamp + 6 条 inequality 回缩 | 比例随机但碟容纳、hub 捕获、closure 锚、pivot 座、spine 接触、堆叠/共面间隙、类别 identity 不破 |
| regression overrides | none（11 格全部一次收敛，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（碟容纳/闭合内高/共面/书页/滑套 clearance + gating 合法性） |、无非法组合、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_type | 4 | yes | yes | standard_rigid / slimline / doublewide / digipak |
| B closure_hinge | 3 | yes | yes | clamshell_swing / topflip / slidingsleeve（+digipak 耦合 spine_fold 非独立采样） |
| C inner_tray | 4 | yes | yes | center_hub / trayless / dualsided_flip / bookletclip |
| N disc_count | 6(值) / 3(copy-logic) | yes | yes | 1 单 / 2 共面 / 3-6 书页；两套 copy-logic |

## Validator

- `slot_choices_for_seed` returns implemented module names（A∈{standard_rigid,slimline,doublewide,digipak}、B∈{clamshell_swing,topflip,slidingsleeve}(digipak→spine_fold)、C∈{center_hub,trayless,dualsided_flip,bookletclip}、N∈[1,6]）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling 选 slot + N + palette + 连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合（§9 七条 fallback：digipak 耦合、sliding×dualsided/booklet、trayless×N≥2、dualsided/booklet 需刚性+可掀盖、共面 N 仅 clamshell+std/double、书页 N≥3 仅 std+clamshell、slimline 仅 clamshell+center_hub）。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（case_margin/case_height/hub_radius/lid_open + 派生）在 `resolve_config` clamp/派生；6 条 inequality（碟容纳、闭合内高、hub 捕获带、共面分槽、书页堆叠、滑套包覆）在 `resolve_config` 求解，不留 builder 失败；`disc_radius` 固定不采样。
- 关键 InterfaceSpec/MatingContract 存在：hub 穿碟孔捕获（element allow_overlap `disc_body↔inner_tray/tray_{i}/hub_rosette_{i}/hub_face_0/leaf_plate_{i}`）；tray/口袋嵌 frame（element allow_overlap）；dualsided pivot 销座入 pivot_post（allow_overlap + expect_contact）；滑套 `allow_isolated_part` + 闭合 overlap 证明；digipak cover 接触 spine。
- 关键 joint type/axis/range：clamshell `base_to_lid` REVOLUTE +X 0→lid_open；topflip REVOLUTE +Y；slidingsleeve `base_to_sleeve` PRISMATIC +X 0→stroke；digipak `spine_fold` REVOLUTE +Y 0→170°；`hub_to_disc(_i)` CONTINUOUS +Z（父级 base/lid/flip_tray/leaf 按派生）；dualsided `base_to_flip_tray` REVOLUTE +X 0→π；书页 `base_to_leaf_{i}` REVOLUTE -X 0→120°。
- copied object 命名/placement：共面 `tray_{i}`/`disc_{i}`/`hub_to_disc_{i}`（沿 X 均布，全父=base）；书页 `leaf_{i}`/`disc_{i}`/`base_to_leaf_{i}`/`leaf_{i}_to_disc_{i}`（沿 +Z 堆叠，碟父=各 leaf）；旋碟 disc 父级随 body/tray/N 派生（不可硬编码）。
- CD 盒身份不变量：扁平矩形容 120mm 碟（footprint 由 disc_radius 派生）；至少 1 个非 fixed closure 关节；除 trayless 外有中心 hub rosette + CONTINUOUS 旋碟；透明壳默认（digipak/trayless 不透明例外）。
- C=trayless：断言无 inner_tray、无 CONTINUOUS 关节、恰好 2 parts、N=1；C=dualsided_flip：断言双面 hub_face + flip_tray 翻 180° + disc 父=flip_tray；A=slimline：断言 tray 在 lid 不在 base + disc 随 lid 开合 + 闭合高 ~5mm；A=digipak：断言面板不透明 + spine 绕 Y 折 + cover 接触 spine。

## Reject cases

- footprint 不容碟（壳内半宽/半深 < DISC_R + clearance）→ 碟穿壳或盖不下；或反向把 `disc_radius` 当自由变量缩放（破坏 120mm CD identity）。
- 闭合内高不足 → 盖压碎碟 / hub 顶穿盖（未用闭合内高 inequality 回缩 case_height_scale）。
- hub 半径越界（< 碟孔 → 碟不被捕获漂浮；或 ≫ 碟孔 → 撑裂穿模）→ 缺 hub 捕获带 clamp + captured-pin allow_overlap。
- 旋碟 `hub_to_disc` 父级错挂（slimline 未父=lid → 碟不随盖；dualsided 未父=flip_tray → 翻托时碟不翻；书页未父=各 leaf → 碟挂错页）。
- 非法 slot 组合未 gate：digipak 配刚性 closure / slidingsleeve 配 dualsided 或 bookletclip（无 lid 承载）/ trayless 配 N≥2（无 hub 可复制）/ 共面 N≥2 配 topflip 或 slidingsleeve（X 轴冲突）/ 书页 N≥3 配非 std-clamshell。
- 共面多碟分槽过窄（TRAY_SECTION_W < 碟径 + 壁）→ 相邻碟重叠穿模；书页堆叠 leaf_spacing 过小或 WALL_H 不足 → 页/碟相撞、盖盖不上。
- 滑套未做 isolated 闭合证明（缺 `allow_isolated_part`）→ 误判穿模 reject；或套腔过小夹死 base。
- 缺任何非 fixed closure 关节（盒读成死砖块，丢失开合语义）；或 disc 既无 hub 又无 trayless 口袋（碟漂浮无依托）。
- 把 DVD/Blu-ray 盒（更高、不同比例、塑料外封）、cassette 盒（装磁带非圆碟、无 hub/rosette）、或空矩形盒（无 hub/碟/透明壳 identity）混进来当 body_type。

## 与相邻类别的边界

- 不该混入：**DVD / Blu-ray case**（更高更深的书本式塑料盒，~190×135mm、含内页夹册轴 + 塑料外封套膜、碟立或单 hub 但盒比例与 jewel case 显著不同；Blu-ray 标志性蓝壳。CD jewel case 是扁方 ~142×125mm、双片合页 jewel 壳 + dark center-hub tray，比例与开合不同）。
- 不该混入：**cassette tape case**（装盒式磁带：内部是磁带卷轴窗 + 方形磁带腔，**无圆形 hub/rosette、无 120mm 圆碟、无旋碟关节**；外形虽也是透明扁盒但持物完全不同）。
- 不该混入：**generic box / 收纳盒**（空矩形容器，无 120mm 圆碟 + 中心轮毂 rosette + 透明壳的 CD identity；CD jewel case 必须有碟 + hub 捕获 + 开合机构，不是无内容的盒）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 新 slug `cd_jewel_case` 必须加入 `cli/template.py` 的 `TEMPLATE_REGISTRY` allow-list（importlib 文件名自动发现不足以让 sweep/batch CLI 识别）。
- 共享 helper：`_shallow_shell`（开顶壳）、`_tray_solid/_tray_section/_hub_rosette`（hub+8 齿 rosette+前指槽）、`_disc_solid`（120mm 碟+中心孔+偏心 marker）、captured-hub `allow_overlap` 在全 11 源一致，可抽公共 helper（保留 `# adopted: <source>` 注释）。body_type 各有 root 构建分派（rigid base vs digipak tray_panel）。
- **disc 父级派生**是最易错点：center_hub/bookletclip/共面 = 父=base；slimline = 父=lid；dualsided_flip = 父=flip_tray；书页 N≥3 = 父=各 leaf_{i}。必须从 resolved config 取，不可硬编码 base。
- captured-pin / isolated overlap 须 element-scoped：hub↔碟孔（全持碟）、tray/口袋↔frame、pivot 销↔pivot_post、滑套 isolated 闭合证明、clip 唇↔booklet_card、书页 hinge barrel↔rear wall、digipak cover↔spine 接触。参考各源 run_tests 的 allow_overlap/expect_contact 块。
- digipak 是**耦合 body**：body=digipak 时旁路 closure/tray 独立采样（强制 spine_fold + center_hub disc_tray），类似 matchbox 的 matchbook 耦合 closure；不要让 digipak 进入 3 刚性 closure 的采样。
- 两套 multiplicity copy-logic 由 `disc_count` 区间分派（共面 vs 书页），共面全父=base 沿 X 均布、书页碟父=各自 leaf 沿 Z 堆叠；hub 8 齿 / dualsided 双面 / bookletclip 4 clip 是固定循环非 multiplicity 轴。
- `palette_style` 须按 element 角色施色：仅 clear-shell 角色施 alpha<1，digipak 纸卡 / trayless 纸口袋恒不透明；否则违反"面板不透明 alpha≥0.95"断言。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / N | `standard_rigid` / `clamshell_swing` / `center_hub` / N=1 | `rec_clear-plastic-cd-jewel-case-with-a-hinged-transp_20260605_161820_827338_61eddc85` | `L40-L74`(dims/shell)、`L77-L123`(center-hub tray)、`L126-L144`(lid_shell)、`L147-L157`(disc)、`L160-L209`(base+lid+`base_to_lid` REVOLUTE+X)、`L211-L240`(disc+`hub_to_disc` CONTINUOUS+Z) | 四槽基线 + N=1 multiplicity 基线：刚性壳 + 摆盖 + 中心轮毂旋碟 |
| S2 | A | `slimline` | `rec_cd_jewel_case_var_body_slimline` | `L44-L64`、`L151-L189`、`L201-L234`(base 薄板 + lid 携 tray)、`L238-L283`(`base_to_lid` -X + `hub_to_disc` 父=lid) | 薄盒：tray 迁移上盖、disc 父=lid |
| S3 | A | `doublewide` | `rec_cd_jewel_case_var_body_doublewide` | `L43-L69`、`L92-L164`(`_hub_rosette`/`_tray_floor`)、`L207-L234`(hub_rosette_{i} loop)、`L264-L294` | 双宽多 hub 槽 + 共面 footprint 参照 |
| S4 | A / B(耦合) | `digipak` / `spine_fold` | `rec_cd_jewel_case_var_body_digipak` | `L34-L104`、`L130-L178`(tray_panel root + cover_panel)、`L183-L194`(`spine_fold` REVOLUTE+Y)、`L216-L224`(`hub_to_disc`) | digipak 纸书折 + 耦合 spine 闭合 |
| S5 | B | `topflip` | `rec_cd_jewel_case_var_hinge_topflip` | `L45`、`L124-L145`(`_lid_shell` 平移)、`L202-L210`(`base_to_lid` REVOLUTE+Y) | 侧翻盖：joint 轴 +X→+Y |
| S6 | B | `slidingsleeve` | `rec_cd_jewel_case_var_hinge_slidingsleeve` | `L53-L67`、`L124-L152`(`_sleeve_shell`)、`L195-L217`(`base_to_sleeve` PRISMATIC+X)、`L264-L279`(isolated+闭合证明) | 滑套：PRISMATIC 开合 + isolated 闭合证明 |
| S7 | C | `trayless` | `rec_cd_jewel_case_var_tray_trayless` | `L74-L117`(`_sleeve_pocket`)、`L160-L184`(inline disc base visual)、`L284-L307`(断言无旋碟/2 parts) | 无盘托口袋：碟固定不旋（N=1 only） |
| S8 | C | `dualsided_flip` | `rec_cd_jewel_case_var_tray_dualsided` | `L93-L143`(`_pivot_post`/`_hub_face`)、`L146-L194`(`_tray_panel` 整体销)、`L255-L292`(`base_to_flip_tray` REVOLUTE+X 0→π)、`L319-L346`(disc 父=flip_tray) | 双面翻托：第三 REVOLUTE + 双面 hub + disc 父=flip_tray |
| S9 | C | `bookletclip` | `rec_cd_jewel_case_var_tray_bookletclip` | `L162-L219`(clip/card)、`L237-L273`(center-hub tray + lid clip_{i}+card)、`L283-L322`、断言 `L456-L518` | center-hub + lid 内册夹（加法 visual，tray 拓扑不变） |
| S10 | N | center_hub 共面 N=2 | `rec_cd_jewel_case_var_discs_n2` | `L39-L66`(N/CASE_W/`disc_cx`)、`L88-L132`(`_tray_section`)、`L176-L197`(tray_{i} loop)、`L224-L253`(disc_{i}+`hub_to_disc_{i}` 父=base) | 共面 copy-logic：N 并列旋碟全父=base 沿 X 均布 |
| S11 | N | center_hub 书页 N=4 | `rec_cd_jewel_case_var_discs_n4` | `L36-L73`(NUM_DISCS/WALL_H/`_leaf_hinge_z`)、`L78-L148`(tall frame/`_leaf_plate`)、`L245-L301`(leaf_{i}+`base_to_leaf_{i}` REVOLUTE-X + disc_{i}+`leaf_{i}_to_disc_{i}` 父=leaf) | 书页 copy-logic：N 页 N 碟沿 Z 堆叠、碟父=各 leaf、加高 frame |
