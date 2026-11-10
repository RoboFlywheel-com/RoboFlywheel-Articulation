# Matchbox (safety matchbox / book of matches with a working closure and N matchsticks) — Modular Spec

> 来源小类：`picture/Others/Matchbox`（articraft_data 上游 Others/Matchbox fork-variant pool）。
> Source map: `articraft_data/picture_expansion/template_source_maps/Others__Matchbox.md`。
> 5★ 样本全读：1 parent（经典抽屉式安全火柴盒）+ 7 converged fork 变体（flip_lid / matchbook / standing / striker_top / n6 / n16 / n24）= 8 records，逐一读取 `revisions/rev_000001/model.py`。
> 引用 `model.py:Lx-Ly` 来自各样本当前 `revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`sleeve` / `tray` / `body` / `lid` / `cover` / `flap` / `_add_match_visuals` / `_add_vertical_match_visuals` / `_add_paper_match_standing` / `_add_paper_match_flat` / `sleeve_to_tray` / `body_to_lid` / `cover_to_flap` / `tray_to_match_{i}` / `striker_{i}` / `side_striker` / `top_striker_patch` / `match_{i}` / `ground_match_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `matchbox` |
| template path | `agent/templates/Others_Matchbox.py` |
| test path (optional) | `tests/agent/test_matchbox_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: closure 根机构 slot（sleeve+tray / body+lid / cover+flap）+ match_arrangement + striker_style，三轴挂在 closure 根件上；外加一根 multiplicity 轴 = match_count N，火柴子件 `match_{i}` 按 N 循环复制并全部 FIXED 在托盘 / 盒体上）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 7 converged fork 变体 = 8 |
| read_count | 8（全读，逐一 `model.py`）|
| read_scope | all 5-star samples in this category（1 parent + 7 variant，无抽样）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

批次：`others_matchbox_qwen37max_20260620`（dashscope qwen3.7-max / medium）。8 records 全部 compile=success（`--validate run_tests` 通过）、workbench-only（collections=['workbench']、category_slug=None）、≥1 非 fixed joint、单轴控制变量、仍明确读作火柴盒。

冗余 / 分流说明：
- **multiplicity 三 record 不另列 candidate**：`rec_matchbox_var_n6`（N=6）/ `rec_matchbox_var_n16`（N=16）/ `rec_matchbox_var_n24`（N=24，双层）均为 P1 同结构（`sleeve`+`tray`+`sleeve_to_tray` PRISMATIC + flat_row）的 match_count N 采样样本，归并为单 multiplicity 轴的 N 覆盖，不另立 closure / arrangement / striker candidate。n6/n16 单层换 pitch；n24 引入 `TOTAL_MATCHES = STICKS_PER_LAYER × NUM_LAYERS` 双层 packing（见 §8）。
- **matchbook 是耦合 closure**（见 §4 / §9 兼容性说明）：matchbook 形态天然携带自己的「paper-match comb」竖立纸火柴梳 + front-panel striker，是该 closure 候选的固有部件，故 matchbook 同时改了 closure 与 match 子模块的部件类型。模板把 paper-comb 绑定为 matchbook 的 native fill，drawer_slide / flip_lid 用 wooden-stick fill；故 match_arrangement / striker_style 两轴仅在 drawer_slide / flip_lid 系下自由组合（不与 matchbook 笛卡尔展开）。

## 核心身份

一只小尺度（~0.055 m 长 × 0.037 m 宽 × 0.014 m 高，桌面 / 手持）的**安全火柴盒 / 书式火柴皮**：一只可开合的薄壁纸 / 木闭合机构（closure），内含 N 根同构火柴子件，外部带擦火面（striker）。closure 根机构 slot 取三种形态之一：经典抽屉式（drawer_slide：cream 卡纸外套 `sleeve`（两端开口 hollow shell：top/bottom panel + 2 side wall + 顶面印刷 border）+ 内滑托盘 `tray`（floor + 4 wall，开顶 hollow），`sleeve_to_tray` PRISMATIC 沿长轴 +X 半开抽拉）/ 翻盖式（flip_lid：一体开顶盒体 `body`（floor + 4 wall + 后缘 cylindrical hinge knuckle）+ 平盖 `lid`，`body_to_lid` REVOLUTE 沿长轴后上缘 rest≈50° 开）/ 对折书皮式（matchbook：折叠纸皮 `cover`（高 back panel + 矮 front panel + bottom spine + pocket）+ 顶 `flap`，`cover_to_flap` REVOLUTE 沿顶折线、axis +X；flap 自 back panel 顶缘向上延伸（是 back panel 的续片），rest 微后倾敞开（露出火柴）、向前下翻合扣盖 front，**翻转全程不穿 back panel**，内含 paper-match comb）。盒内火柴排布（match_arrangement）取平躺单层一排（flat_row：`match_{i}` 沿 +X 平躺、Y 等距 pitch、头朝开口端，N 撑大切双层）或竖插成束（standing_bundle：`match_{i}` 竖立沿 +Z、头朝上、规则 grid；drawer_slide 下托盘抽出、竖立火柴排在外露区、**避开 sleeve 顶板不穿模**，flip_lid 下盒体开顶、stick 长度 clamp 在闭合 lid 平面下）。擦火面（striker_style）取两长侧各一条（both_long_sides）或单侧条 + 顶面擦火块（one_side_plus_top_patch）。

身份核心 = **带 ≥1 活动闭合关节（PRISMATIC 抽屉 / REVOLUTE 翻盖或书皮）的小盒 + 内含 N 根火柴 + 外擦火面**。火柴本身**全部 FIXED**（不活动），唯一活动关节是 closure；另有 2 根散落 `ground_match_{i}` FIXED 在盒前地面（孤立件 `allow_isolated_part`）。每个 closure 候选 ≥1 non-fixed joint。

## 与相邻类别的边界

- 不该混入：**`container_box`（储物 / 礼盒 / 运输箱）**——理由：container_box 是桌面 / 手持储物箱（~0.1–0.3 m），其身份在「带闭合机构的方角储物箱 + 可选内胆 / 隔板」，内部不含 N 根同构火柴、外部无擦火面（striker）。matchbox 虽与 container_box 的 sliding_drawer 形态同源（火柴盒式抽屉），但 matchbox 更小（~0.055 m）、**必有内含 N 火柴 + 外擦火面**，且 closure 词汇收窄为「抽屉 / 翻盖 / 书皮」三种，identity 在「装火柴 + 能擦火」。reject：造无火柴 / 无擦火面的空盒当 matchbox。
- 不该混入：**`lighter`（打火机）**——理由：lighter 是金属 / 塑料外壳 + 火石轮 / 按钮 / 喷嘴 / 可旋盖的点火器，identity 在「机械 / 气体点火机构」；matchbox 无火轮 / 喷嘴 / 燃料腔，靠 N 根独立火柴 + 擦火面取火。两者不复用点火词汇表。
- 不该混入：**`pen` / `marker` 等细长文具盒 / 烟盒（cigarette pack）**——理由：cigarette pack 是软 / 硬纸盒装 N 支等长圆柱烟支（无头、无擦火面、翻盖式硬盒或软盒撕口），matchbox 的子件是「带反应头的火柴」（一端有 ellipsoid / box head）且必带擦火面；drawer 组织接近但 matchbox 的 striker + match head 是判别特征。reject：把火柴头去掉当烟支、去掉 striker 当烟盒。

reject 案例：造无任何活动关节的死盒（违反 §3，closure 必须 ≥1 non-fixed joint）；去掉 N 火柴 / 去掉 striker 退化成普通小纸盒（出 matchbox 身份）；给 matchbox 补金属火轮 / 喷嘴当 lighter。

## 槽位 + 候选模块表

> **建模注记**：closure 根机构 slot 决定 root part 拓扑（`sleeve`+`tray` / `body`+`lid` / `cover`+`flap`）与唯一活动关节（PRISMATIC / REVOLUTE）。match_arrangement 决定盒内火柴子件的几何 + placement（平躺 / 竖立），由 multiplicity 轴 N 循环复制并 FIXED 到 tray/body。striker_style 决定擦火面的 inline visual 布局（贴在 closure 根件上，无独立 joint）。drawer_slide / flip_lid 两 closure × match_arrangement(2) × striker_style(2) 自由组合；matchbook 是耦合 closure（自带 paper-comb fill + front striker，不与另两轴笛卡尔展开，见 §9）。外加 match_count N multiplicity 轴。

### Slot A：closure（主开合机构槽——开盒机构 / 盒体形态，**每候选 ≥1 non-fixed joint**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| drawer_slide（基线）| P1 rec_model-a-classic-safety-matchbox-...a0e600f3 | `sleeve` 根 build L91-L142 + `tray` 子 L144-L166 + `sleeve_to_tray` PRISMATIC +X L172-L182（origin offset +0.020 半开，limits ±0.020）+ `_add_match_visuals` helper L65-L80 | eligible if compatible | 套筒 + 内滑抽屉托盘：`sleeve`（两端开口 hollow shell：bottom/top panel + 2 side wall）+ `tray`（floor + 2 side + 2 end wall，开顶），沿长轴 +X 抽拉 PRISMATIC，rest 半开；单活动件 |
| flip_lid | rec_matchbox_var_flip_lid | `body` 根（开顶 tray shell：floor + 2 long + 2 end wall + cylindrical `hinge_knuckle`）L87-L139 + `lid` 子（平 panel + 印刷 border）L144-L177 + `body_to_lid` REVOLUTE axis=(1,0,0) origin=后(-Y)上缘 L186-L202（rpy 编码 rest≈50° 开，limits -50°..+70°）+ `_add_match_visuals` L62-L76 | eligible if compatible | 一体开顶盒 + 后缘铰链翻盖：`body` 装火柴，`lid` 绕后上缘长轴 REVOLUTE 上掀，knuckle 可见铰；单活动件 |
| matchbook（耦合）| rec_matchbox_var_matchbook | `cover` 根（高 back panel + 矮 front panel + bottom spine + pocket + base_strip + paper-comb）+ `flap` 子 + `cover_to_flap` REVOLUTE **axis=(1,0,0)** origin=顶折线 `(0,0,BACK_H)`（rpy 编码 rest 微后倾敞开；limits = closed(向前下翻 ~ -175°)..open(~+30° 更后倾)）；**flap_panel 自顶折线向上延伸（origin z=+FLAP_H/2，是 back panel 续片），翻合全程不穿 back panel**；内含 paper-comb `_add_paper_match_standing` helper + `for i in range(N_MATCHES)`；striker 在 front_panel | eligible if compatible（**耦合，gating 见 §9**）| 对折书式纸火柴皮（book of matches）：折叠纸 `cover` + 顶 `flap` 绕顶折线 REVOLUTE 翻开/扣合；flap 是 back panel 顶缘续片，rest 微后倾露出火柴、向前下翻扣盖 front；内含扁平纸火柴梳竖立在 base_strip 上（matchbook native fill），front-panel 自带 striker；单活动件 |

硬约束记录：closure 3 distinct candidate（drawer_slide / flip_lid / matchbook，达下限 3）。含 PRISMATIC（drawer +X）+ REVOLUTE（flip_lid +X 后缘、matchbook +X 顶折线）两种 joint 拓扑 + 不同 root part tree（sleeve+tray 两端开口套筒 / body+lid 开顶盒 / cover+flap 折叠书皮），是真实结构差异。matchbook 额外耦合 paper-comb fill + front striker（见 §9 兼容性）。

### Slot B：match_arrangement（盒内火柴排布——由 multiplicity 轴 N 循环复制的子件几何 + placement）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_row（基线）| P1（单层）+ rec_matchbox_var_n24（双层）| `_add_match_visuals`（水平 stick `Box((STICK_L,STICK_S,STICK_S))` + `head_mesh` ellipsoid 朝 +X）L65-L80；单层 `for i in range(N)` L184-L202（pitch 等距、`tray_to_match_{i}` FIXED）；N24 双层 `for i in range(TOTAL_MATCHES)` row=i//STICKS_PER_LAYER col=i%STICKS_PER_LAYER L198-L212 | eligible if compatible | 平躺单层 / 双层一排：火柴沿 +X 平躺、Y 等距 pitch、头朝开口端，FIXED 到 tray/body；N 撑大单层放不下切双层（n24：LAYER_DZ=STICK_S 上叠、UPPER_X_OFFSET 错位让头）|
| standing_bundle | rec_matchbox_var_standing | `_add_vertical_match_visuals`（竖直 stick `Box((STICK_S,STICK_S,STICK_L))` 沿 +Z + `head_mesh_v` ellipsoid 朝 +Z 顶）；竖立 grid `for i in range(N_MATCHES)` col=i%GRID_COLS row=i//GRID_COLS（FIXED `tray_to_match_{i}`）| eligible if compatible | 竖插成束（满盒立放观感）：火柴长轴沿 Z 竖立、头朝上、规则矩形 grid，FIXED 到 tray；**drawer_slide 下托盘 rest 抽出（asymmetric：origin=+0.58·box_l，lower 闭合 flush / upper 微伸），grid 收束在外露区（grid x-center=box_l/2−rest/2），竖立火柴整株立在 sleeve 口外、不穿 top_panel——无 allow_overlap mask**；flip_lid 下盒体开顶，stick 长度 clamp 使头不穿闭合 lid |

硬约束记录：match_arrangement 2 candidate（flat_row / standing_bundle，降到下限 2，**降级理由见下**）。两者改火柴子件 primitive 朝向（水平 stick 长轴 X + 横 head ↔ 竖直 stick 长轴 Z + 顶 head）与 placement（线性 Y-pitch 行 / 二维 col×row grid）+ 不同 head_mesh（横 ellipsoid `scale(HEAD_LX/2,HEAD_R,HEAD_R)` ↔ 竖 ellipsoid `scale(HEAD_R,HEAD_R,HEAD_LX/2)`），是真实几何 / placement / 子件拓扑差异（非纯尺寸）。
> **降级理由（2 candidate）**：5★ 池内火柴排布只收敛出「平躺」与「竖立」两种真实拓扑（flat_row 含单 / 双层两 record，竖立含 standing 一 record）。第三种排布（如斜插 / 散乱堆）无收敛 5★ 来源，不强造空候选（§2.3：变化无足够来源则折入或不立）。flat_row 的单层↔双层是同一候选内 N 撑大的派生 packing（n24），不是独立 candidate。

### Slot C：striker_style（擦火面布局——贴在 closure 根件上的 inline visual，无独立 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| both_long_sides（基线）| P1 | `striker_{i}`(i∈0..1) inline 在 sleeve 的 side wall 循环内 L114-L120（`Box((0.050,0.0006,0.010))` proud 0.0001 贴每条长侧壁外面）| eligible if compatible | 两长侧各一条擦火条：sleeve / body 的两条长侧壁外面各贴一条 reddish-brown stippled striker strip（proud），对称；flip_lid 同样在 body side wall 发两条（L110-L117）|
| one_side_plus_top_patch | rec_matchbox_var_striker_top | 单条 `side_striker` 仅贴 -Y 长侧 L115-L122 + `top_striker_patch`（`Box((0.040,0.012,0.0004))` 印在 top_panel 旁 border）L146-L156；+Y 侧留素 cream（无 striker）| eligible if compatible | 单侧条 + 顶面擦火块：仅 -Y 一长侧一条 striker + 顶面 sleeve panel 旁印一块 striker patch；对侧长壁 plain cream（无 striker visual）|

硬约束记录：striker_style 2 candidate（both_long_sides / one_side_plus_top_patch，降到下限 2，**降级理由见下**）。两者改擦火面 visual 布局（对称两侧条 ↔ 单侧条 + 顶 patch）与擦火面位置（侧壁 ↔ 侧壁 + 顶面），是真实 visual 组 / 位置拓扑差异（striker 数量 + 顶面 patch 有无）。均为 closure 根件上的固定 visual，无独立 joint（活动关节由 closure 槽保证）。
> **降级理由（2 candidate）**：5★ 池内擦火面只收敛出「两长侧」与「单侧 + 顶 patch」两种真实布局。第三种（如全包裹环形 striker / 底面 striker）无收敛 5★ 来源 + 现实罕见，不强造空候选。striker 仅换 visual 布局不引入 joint，是真实 module-local 结构差异（数量 + 位置），非纯材质 / 颜色。

## 槽位图（slot graph）

pattern: mixed（closure 根件为 root 坐地 z=0；match_arrangement（火柴子件 ×N）+ striker（inline visual）挂到 closure 根件；match_count 为一根 N multiplicity 轴）

```
[closure 根件]  [ROOT, 坐地 z=0; 形态由 closure 决定]
   │
   ├── closure = drawer_slide:
   │     sleeve(两端开口 hollow shell + striker inline) --[sleeve_to_tray: PRISMATIC +X @ (SLIDE_HALF,0,0)]--> tray(开顶 hollow)
   │        └── tray --[tray_to_match_{i}: FIXED @ placement]--> match_{i}  (×N，由 match_arrangement 决定平躺/竖立)
   │
   ├── closure = flip_lid:
   │     body(开顶 tray shell + hinge_knuckle + striker inline) --[body_to_lid: REVOLUTE +X @ 后(-Y)上缘 (0,-BODY_W/2,BODY_H)]--> lid(平 panel + border)
   │        └── body --[body_to_match_{i}: FIXED @ placement]--> match_{i}  (×N，平躺/竖立)
   │
   └── closure = matchbook (耦合):
         cover(back+front panel + spine + base_strip + striker inline + paper-comb match_{i}) --[cover_to_flap: REVOLUTE +X @ 顶折线 (0,0,BACK_H)，flap 向上延伸续片]--> flap
            └── paper-comb match_{i} 是 cover 的 inline visual（`_add_paper_match_standing`），竖立在 base_strip，×N（matchbook native fill）
   │
   └── (所有 closure) [closure 根件] --[*_to_ground_match_{i}: FIXED @ 前(+Y)地面]--> ground_match_{i}  (×2，散落孤立件)
```

接口点位与 joint 语义：
- **drawer 接口**：`sleeve_to_tray` origin 在 `(drawer_rest,0,0)`，axis +X PRISMATIC。flat_row：对称半开（origin=slide_half，limits ±slide_half，rest q=0 半开）。standing_bundle：**抽出 rest（origin=+0.58·box_l），limits lower=-drawer_rest（闭合 flush）/ upper=+小量（仍 captured），竖立火柴排在外露区**。tray 在 sleeve 腔内是 captured 友配（cross-section `expect_within yz`），无 MatingContract（grandfather）。
- **flip_lid 接口**：`body_to_lid` origin 在后(-Y)上缘 `(0,-BODY_W/2,BODY_H)`，axis +X，REVOLUTE，rpy 编码 rest≈50° 开，limits -50°（闭合水平盖顶）..+70°（更开）；lid panel 边缠 cylindrical `hinge_knuckle` 处 element-scoped `allow_overlap`（knuckle ↔ lid_panel）。
- **matchbook 接口**：`cover_to_flap` origin 在顶折线 `(0,0,BACK_H)`，axis **+X**，REVOLUTE；flap_panel 自折线**向上延伸**（child origin `(0,wall/2,FLAP_H/2)`，是 back panel 续片），rpy 编码 rest 微后倾敞开，limits = closed(向前下翻 ~ -175°)..open(~+30° 更后倾)。**因 flap 在枢轴之上，向前翻合全程不扫过枢轴下方的 back panel——rest 姿态与 back panel / front panel / comb 均无交叠，无需任何 `allow_overlap`**。
- **match 接口**：`tray_to_match_{i}` / `body_to_match_{i}` FIXED，origin 在 placement（flat_row: `(stick_xc, yc, stick_zc)` 沿 Y-pitch；n24 双层: 加 layer 偏 z + UPPER_X_OFFSET；standing: `(xc, yc, floor_top)` col×row grid）。matchbook 的 paper-comb 不是独立 part / joint，是 cover 的 inline visual（`{name}_tab`+`{name}_head`）。
- **striker 接口**：striker strip / patch 是 closure 根件的 inline visual（无 joint），proud 贴侧壁外面 / 印在 top panel；by-element AABB 校验 proud。
- **ground_match 接口**：`*_to_ground_match_{i}` FIXED，origin 在前(+Y)地面 `(cx,cy,ground_zc)`，×2 散落孤立件，`allow_isolated_part`（继承 parent）。
- **rest pose**：closure 在 q=0 为半开（drawer）/ ~50° 开（flip）/ ~70° 开（matchbook），均露出火柴（viewer 目检活动语义）；火柴 + striker + ground_match 固定。
- **互斥 / 可选**：closure 各候选互斥（一次一种）；match_arrangement 各候选互斥；striker_style 各候选互斥。matchbook closure 强制 native paper-comb fill + front striker（不读 match_arrangement / striker_style 两轴，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / closure = drawer_slide（ROOT = sleeve）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sleeve`（root: bottom/top panel + 2 side wall + border inline visual）+ `tray`（floor + 2 side + 2 end wall）| P1 `sleeve` L91-L142 / `tray` L144-L166 |
| internal joints | `sleeve_to_tray` PRISMATIC +X（limits ±SLIDE_HALF）| P1 L172-L182 |
| upstream interface | sleeve 坐地 z=0（root）| P1 |
| downstream interface | tray 腔接 match（`tray_to_match_{i}` FIXED）；sleeve 长侧 / 顶面接 striker | P1 L184-L202 |

### Slot A / closure = flip_lid（ROOT = body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root: floor + 2 long + 2 end wall + cylindrical `hinge_knuckle`）+ `lid`（panel + 印刷 border）| flip_lid `body` L87-L139 / `lid` L144-L177 |
| internal joints | `body_to_lid` REVOLUTE +X @ 后上缘（rest≈50° 开，limits -50°..+70°）| flip_lid L186-L202 |
| downstream interface | body 腔接 match（`body_to_match_{i}` FIXED）；body 长侧 / 顶面接 striker；lid 边缠 knuckle（allow_overlap）| flip_lid L204-L220 |

### Slot A / closure = matchbook（ROOT = cover，耦合 native fill）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`（root: back+front panel + spine + base_strip + striker + paper-comb inline visual）+ `flap` | matchbook `cover` L112-L161 / `flap` L164-L173 |
| internal joints | `cover_to_flap` REVOLUTE **+X** @ 顶折线 `(0,0,BACK_H)`，flap_panel 自折线向上延伸（续片）；rest 微后倾敞开，limits closed(~ -175° 向前下翻)..open(~+30°)；rest 全程无穿模、无 allow_overlap | matchbook `cover_to_flap` |
| downstream interface | paper-comb `match_{i}_tab`/`match_{i}_head` 竖立在 base_strip（cover inline visual，×N native fill）；front_panel 接 striker | matchbook `_add_paper_match_standing` L74-L89 + comb loop L159-L161 + striker L140-L145 |

### Slot B / match_arrangement（≠matchbook 时，火柴子件 ×N 挂 tray/body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | flat_row: `match_{i}`(水平 stick + 横 head, ×N) / standing_bundle: `match_{i}`(竖直 stick + 顶 head, ×N) | flat_row `_add_match_visuals` L65-L80 / standing `_add_vertical_match_visuals` L92-L106 |
| internal joints | `tray_to_match_{i}` / `body_to_match_{i}` FIXED（×N，火柴不活动）| P1 L196-L202 / standing L226-L232 |

### Slot C / striker_style（closure 根件上 inline visual，无 joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | both_long_sides: `striker_{i}`(×2 侧壁条) / one_side_plus_top_patch: `side_striker`(1 侧条) + `top_striker_patch`(顶 patch) | P1 `striker_{i}` L114-L120 / striker_top `side_striker`+`top_striker_patch` L115-L156 |
| internal joints | 无（striker 为 closure 根件固定 visual）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure | enum | drawer_slide / flip_lid / matchbook | drawer_slide | choice | deterministic procedural sampler 选 | module table |
| match_arrangement | enum | flat_row / standing_bundle | flat_row | choice | sampler 选；**仅 closure∈{drawer_slide,flip_lid} 时读**（matchbook 强制 paper-comb，见 §9）| module table |
| striker_style | enum | both_long_sides / one_side_plus_top_patch | both_long_sides | choice | sampler 选；**仅 closure∈{drawer_slide,flip_lid} 时读**（matchbook 强制 front striker）| module table |
| match_count | int | [4, 40] | 10 | conditional | multiplicity 轴；加权采样（小 N 偏多）；上限随 closure / arrangement / 盒内净宽派生 clamp（见 §8）| P1/n6/n16/n24/standing |
| palette_style | enum | classic_cream_kraft / white_blue_safety / brown_kraft_green / black_box_red / glossy_white_navy / red_safety（6 colorway）| classic_cream_kraft | palette | palette only，**不计入 slot_choice**；per-seed `rng.choice` | 见下 palette 表 |
| box_length_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放盒长 SLEEVE_L/BODY_L/COVER_W（长轴 X）→ tray / cavity / match 行长度 + slide 行程同比，clamp | resolve clamp |
| box_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放盒宽 SLEEVE_W/BODY_W/POCKET → tray 内宽 + flat_row Y-pitch 跨度 / grid 列数派生，clamp | resolve clamp |
| box_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放盒高 SLEEVE_H/BODY_H/BACK_H → side wall / 翻盖 mount 高 + standing 头出 rim 余量，clamp | resolve clamp |
| closure_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 drawer PRISMATIC 行程 SLIDE_HALF + flip/matchbook REVOLUTE open angle，clamp | resolve clamp |
| match_pitch_scale | float | [0.85, 1.20] | 1.0 | conditional | 缩放火柴 Y-pitch / grid spacing；合法上限随 N 与盒内净宽派生（N 大 pitch 收紧 / 切双层）| n6/n16/n24/standing |
| (—) | constraint | — | — | inequality | drawer 行程：`SLIDE_HALF·scale ≤ tray_insertion − retain_margin`（伸出仍 captured ~12mm），违反按比例回缩 | P1 接口 |
| (—) | constraint | — | — | inequality | flat_row 单层容量：`N·match_pitch ≤ tray_inner_width`；超限自动切双层（`NUM_LAYERS=ceil`，n24 packing）或回缩 pitch | n24 L55-L60 |
| (—) | constraint | — | — | inequality | standing_bundle grid：`GRID_COLS·GRID_ROWS ≥ N` 且 grid 跨度 ≤ 可用腔 XY；违反扩 grid 或回缩 pitch。**drawer 下可用 X 腔 = 外露区宽（≈0.58·box_l − clearance），非整托盘长** | standing grid sizing |
| (—) | constraint | — | — | conditional | **standing_bundle 不穿模（无 allow_overlap mask）**：drawer 下托盘抽出、grid 收束在外露区使竖立火柴整株立在 sleeve 口外（assert 每根 stick x-min > box_l/2）；flip_lid 下盒体开顶、stick 长度 clamp 使头停在闭合 lid 平面下（见 §9）| standing exposed-region placement |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`match_count` 上限 conditional 依 closure / arrangement / 盒宽；单层↔双层切换 + pitch 回缩 + grid 扩张为 inequality，在 resolve 投影 / 回缩，不留到 builder。scale 只动安全比例 / clearance / 细节尺寸，绝不改 closure / arrangement / striker 的拓扑。

### palette_style 颜色板（6 colorway，per-seed `rng.choice`，不计 slot_choice）

每个 colorway = **body（盒体 / sleeve / cover）+ closure（tray / lid / flap）+ striker（擦火面）+ match_wood（火柴杆）+ match_head（火柴头）+ print/accent（印刷 border / 标签）**。仿 `agent/templates/Accessories_Cushion.py` 的 `PALETTE_STYLES` 元组 + `palette_style=rng.choice(PALETTE_STYLES)` + `PALETTES[style]` dict 模式。realistic 锚定纸 / 木火柴盒范围（非 metallic-neon）。

| palette_style | body rgba | closure rgba | striker rgba | match_wood rgba | match_head rgba | print/accent rgba | 灵感来源 |
|---|---|---|---|---|---|---|---|
| classic_cream_kraft（基线）| cream `(0.89,0.84,0.71,1)` | cream_tray `(0.92,0.88,0.76,1)` | striker `(0.66,0.36,0.28,1)` | wood `(0.85,0.72,0.50,1)` | head_brown `(0.38,0.13,0.08,1)` | print_brown `(0.24,0.14,0.09,1)` | P1 / 全部 5★ 基线材质（cream 卡纸 + dark-red 头）|
| white_blue_safety | white_board `(0.93,0.92,0.90,1)` | white_tray `(0.95,0.94,0.92,1)` | striker_navy `(0.20,0.26,0.42,1)` | wood `(0.85,0.72,0.50,1)` | head_blue `(0.16,0.24,0.50,1)` | navy_ink `(0.16,0.22,0.40,1)` | white box + 蓝头安全火柴（realistic 推演）|
| brown_kraft_green | kraft `(0.72,0.56,0.36,1)` | kraft_inner `(0.66,0.50,0.32,1)` | striker_green `(0.18,0.34,0.22,1)` | wood `(0.82,0.68,0.46,1)` | head_green `(0.20,0.40,0.24,1)` | print_brown `(0.22,0.14,0.09,1)` | brown kraft + green 安全头（realistic 推演）|
| black_box_red | black_board `(0.13,0.13,0.14,1)` | charcoal_tray `(0.20,0.20,0.22,1)` | striker_gray `(0.45,0.43,0.42,1)` | wood `(0.84,0.70,0.48,1)` | head_red `(0.62,0.14,0.12,1)` | gold_ink `(0.80,0.66,0.30,1)` | 黑盒 + 红头（realistic colored colorway 推演）|
| glossy_white_navy | white_gloss `(0.96,0.96,0.95,1)` | white_gloss `(0.97,0.97,0.96,1)` | striker_navy `(0.18,0.24,0.40,1)` | wood `(0.85,0.72,0.50,1)` | head_navy `(0.14,0.22,0.46,1)` | navy_foil `(0.20,0.28,0.46,1)` | 白高光礼盒火柴 + 海军蓝头（realistic 推演）|
| red_safety | crimson_board `(0.66,0.16,0.16,1)` | crimson_inner `(0.58,0.14,0.14,1)` | striker_dark `(0.30,0.18,0.14,1)` | wood `(0.82,0.68,0.46,1)` | head_brown `(0.36,0.12,0.08,1)` | cream_label `(0.90,0.86,0.78,1)` | 红盒 + 棕头经典安全火柴（realistic 推演）|

> palette_style 仅换材质 rgba（不改结构 / 拓扑；材质 / 颜色差异不是 candidate，§2.4）。closure / arrangement / striker 的盒体 / 火柴 / 擦火面 / 印刷材质统一由 palette_style 派生。classic_cream_kraft 锚定全 5★ 基线 rgba；其余 5 板为 realistic 纸 / 木火柴盒范围内推演 colorway（white+blue / brown+green / black+red / glossy white+navy / red+brown，均为现实存在的火柴盒配色）。6 板满足 ≥3 / target 4–6。

## Multiplicity / Copy Logic

本 spec 有 **1 根 multiplicity 轴**（match_count），是 matchbox 唯一的「同构子件 × N」复制层。

- `count_param`：`match_count`（盒内火柴根数 N）。
- `N_range`：`match_count ∈ [4, 40]`（本小类本轴的产品域；测试偏小 N={4,6,10,16}，产品全程到 40；满盒木火柴常 20–45 根、纸火柴梳常 10–30 根）。已覆盖样本 N={6,10,16,24}（n6 / P1 基线 10 平躺单层 / n16 平躺加密 + standing 竖立 16 / n24 双层 24）。
- sampling domain（权重档）：小 N 高频、大 N 稀有 —— 建议权重 N∈[4,8]:0.30 / [9,14]:0.30 / [15,22]:0.22 / [23,30]:0.12 / [31,40]:0.06（小 N 偏多、尾部稀有）。每 build 对该轴做一次加权采样，编进 `slot_choices`，clamp 到 closure / arrangement / 盒宽派生上限。
- copied object：单根火柴 —— drawer/flip 系为木棍（`_add_match_visuals` / `_add_vertical_match_visuals` 共享 helper：square wooden stick `Box` + ellipsoid head mesh）；matchbook 系为扁平纸火柴（`_add_paper_match_standing`：paper tab `Box` + box head，竖立在 base_strip，是 matchbook native fill）。
- naming：`match_{i}`（i=0..N-1，盒内）+ joint `tray_to_match_{i}` / `body_to_match_{i}`（drawer/flip）；matchbook 为 cover inline visual `match_{i}_tab` / `match_{i}_head`（无独立 part / joint）。另 `ground_match_{i}`（i=0..1，散落地面，固定 2 根）+ `*_to_ground_match_{i}` FIXED。
- placement：
  - flat_row 单层：沿 +X 平躺、Y 等距 `yc = -pitch·(N-1)/2 + pitch·i`（n6 pitch=0.0052 / P1=0.0031 / n16=0.002，随 N 收紧）。
  - flat_row 双层（N 超单层容量）：`layer=i//STICKS_PER_LAYER`、`col=i%STICKS_PER_LAYER`、`zc += layer·LAYER_DZ`、`xc += layer·UPPER_X_OFFSET`（n24：STICKS_PER_LAYER=12、NUM_LAYERS=2、TOTAL=24）。
  - standing_bundle：竖立矩形 grid `col=i%GRID_COLS`、`row=i//GRID_COLS`、`xc/yc` 由 PITCH_X/Y 推导（standing：4×4=16），头出 rim。
- joint policy：盒内 `match_{i}` **全部 FIXED** 到 tray/body（火柴本身不活动）；唯一活动关节是 closure（PRISMATIC 抽屉 / REVOLUTE 翻盖或书皮）。散落 `ground_match_{i}` 以 `allow_isolated_part` 显式放行（前方地面孤立件，继承 parent，固定 ×2）。
- source / gating：单层 P1 L184-L202 / n6 L191-L203 / n16 L191-L203；双层 n24 L55-L60（常量）+ L198-L212（loop）；竖立 standing L215-L232。**gating**：N 上限随 closure（matchbook paper-comb 容量上限较低）/ arrangement（flat 单层容量 / standing grid 容量）/ 盒内净宽派生 clamp；超单层容量自动切双层 / 扩 grid（见 §7 inequality）。

> matchbook 的 paper-comb 也按 N 复制（`for i in range(N_MATCHES)` L159-L161），但 N 上限受 cover 宽 / base_strip 长制约（pitch=BASE_W/N），是同一 match_count 轴在 matchbook native fill 下的解析（不另立轴）。matchbook 下 match_arrangement / striker_style 两轴不展开（耦合，见 §9）。

## 拓扑多样性审计

总组合数（drawer_slide / flip_lid 自由系）：closure(2: drawer_slide, flip_lid) × match_arrangement(2) × striker_style(2) = **8** + matchbook(1，耦合，自带 fill + striker，不展开两轴) = **9 基础结构组合**。
含 match_count N 轴：每个不同 N 等价类（{4..8}/{9..14}/{15..22}/{23..30}/{31..40} 约 5 个有效拓扑等价类 + 单层↔双层 packing 切换）→ 进一步放大。

> 源 map 预审写 closure 3 × arrangement 2 × striker 2 = 12 ≥ 10。本 spec 据耦合说明把 matchbook 折出两轴笛卡尔（matchbook 自带 native fill + striker），保守口径取 drawer/flip 自由系 8 + matchbook 1 = **9 基础组合**；叠 match_count N 的 ~5 个等价类（含双层 packing）→ **9 × 5 ≈ 45 distinct ≫ 10**，过门控充裕。若按源 map 原口径（matchbook 也名义乘 2×2）则达 12 基础，更宽松。

理由：closure 含 PRISMATIC（drawer +X）+ REVOLUTE（flip +X / matchbook +X）两种 joint 拓扑 + 三种 root part tree（sleeve+tray / body+lid / cover+flap）。match_arrangement 改火柴子件 primitive 朝向（水平 stick + 横 head ↔ 竖直 stick + 顶 head）+ placement（线性行 ↔ col×row grid）。striker_style 改擦火面 visual 布局（两侧条 ↔ 单侧 + 顶 patch）。match_count N 改复制数 + 单层↔双层 packing 等价类。slot_choices 编入 closure + arrangement + striker + match_count N（matchbook 时 arrangement/striker 固定 native）。drawer/flip 自由系 8 + matchbook 1 + N 等价类 ≈ 45 distinct，远超 10。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先加权 `rng.choice` closure；若 closure∈{drawer_slide,flip_lid} 再各 `rng.choice` match_arrangement / striker_style（若 closure=matchbook 则两轴固定为 native paper-comb + front striker，不采样）；再对 match_count 做加权采样（小 N 偏多）；再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 适配少量组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 ~9 基础 × N 等价类（含双层）→ 接近 45–50。低于 300 的原因：本小类真实结构词汇就是 3 closure（其一耦合）× 2 arrangement × 2 striker + 1 根 match_count N 轴，是该类目（小火柴盒）的合理上限，不强行注水。N 轴贡献是连续 multiplicity 的等价类，slot choice tuple distinct 由 (closure, arrangement, striker, N-bucket, layer-mode) 元组定义。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（box_length / box_width / box_height / closure_travel / match_pitch）+ match_count（conditional multiplicity）。全部 `resolve_config` clamp + 每 build 统一应用。`match_count` 上限 conditional 依 closure / arrangement / 盒宽；单层↔双层切换 + pitch 回缩 + grid 扩张 inequality 在 resolve 投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（drawer slide rail / flip 后上缘 / matchbook 顶折线）、tray-in-sleeve 友配、火柴坐 floor / 头出 rim、坐地或类别身份。按 §7 约束类型声明：5 scale 为 independent（match_pitch 上限 conditional），match_count + 容量切换为 conditional/inequality，遵循连续尺寸采样契约（先采 independent → 派生 → 投影回缩 → 解析 conditional）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权 `rng.choice` closure；drawer/flip 系再各采 arrangement/striker（matchbook 固定 native）；加权采 match_count N；uniform 各 scale + palette_style | slot_choices_for_seed 含 (closure, arrangement, striker, match_count) 且与 build 一致；matchbook 时 arrangement/striker 标 native |
| compatibility matrix | (1) **matchbook 耦合**：closure=matchbook 强制 paper-comb native fill（竖立纸火柴）+ front-panel striker，**不读** match_arrangement / striker_style（gating：matchbook 分支固定两轴 = native）。(2) **drawer_slide / flip_lid 自由组合**：与 flat_row/standing_bundle、both_long_sides/one_side_plus_top_patch 全正交。(3) **standing_bundle 不穿模**：竖立火柴 STICK_L 远高于盒高。**drawer_slide+standing**：托盘抽出（asymmetric rest origin=+0.58·box_l），竖立 grid 收束在外露区使每根 stick x-min > box_l/2（整株立在 sleeve 口外，**不穿 top_panel，无 allow_overlap mask**）。**flip_lid+standing**：盒体开顶，resolve 把 standing 火柴长 clamp 到 ≤ body 内净高 + lid 余量，头停在闭合 lid 平面下（rest 开态露出）。(4) match_count N 上限随 closure（matchbook base_strip 容量低）/ arrangement（flat 单层容量 → 超则双层 / standing grid 容量 → 超则扩 grid）/ 盒宽 clamp。(5) closure 各候选互斥；arrangement / striker 各候选互斥。| 无 floating / collision（火柴互穿 / 头穿闭合 lid）/ closure 穿盒 / drawer 脱出 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale + match_count conditional + 单层/双层/grid 派生，每 build 统一 | 比例变化不破坏 closure joint origin / tray-in-sleeve 友配 / 火柴坐 floor / 头出 rim / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作 / 坐地 / overlap / match_count N QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| closure | 3 | yes | yes | drawer_slide(PRIS +X sleeve+tray) / flip_lid(REV +X body+lid) / matchbook(REV -X cover+flap, 耦合 native fill) |
| match_arrangement | 2 | yes | no | flat_row(平躺单/双层) + standing_bundle(竖立 grid)；降级理由见 §4（仅两种真实排布收敛）|
| striker_style | 2 | yes | no | both_long_sides(两侧条) + one_side_plus_top_patch(单侧 + 顶 patch)；降级理由见 §4（仅两种真实布局收敛）|
| match_count | (N 轴) | — | — | multiplicity 轴 [4,40]，样本 N={6,10,16,24}；非 enum slot，是复制数量轴 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (closure, match_arrangement, striker_style) 三轴 + match_count N；matchbook 分支 arrangement/striker 标 native（不采样）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（加权 closure + 条件采 arrangement/striker + 加权 match_count N + uniform scale + rng palette_style）
- `resolve_config` 各 scale clamp 到声明范围；match_count 上限按 closure/arrangement/盒宽 conditional 派生；flat 单层容量超限切双层（NUM_LAYERS）/ standing grid 容量超限扩 grid / pitch 回缩 inequality 在 resolve 投影
- compatibility matrix / gating：matchbook 强制 native fill + front striker（不展开两轴）；drawer/flip 自由组合；flip_lid+standing 头部不穿闭合 lid
- 连续 scale clamp 后不破坏 closure joint origin / tray-in-sleeve 友配 / 火柴坐 floor / 头出 rim / 坐地 / 类别身份
- 关键 joint：drawer `sleeve_to_tray` PRISMATIC +X（abs(axis[0])==1, axis[1]==axis[2]==0）；flip_lid `body_to_lid` REVOLUTE +X（abs(axis[0])>0.9, abs(axis[1])<0.1, abs(axis[2])<0.1，origin 在后上缘）；matchbook `cover_to_flap` REVOLUTE **+X**（abs(axis[0])>0.9，origin 在顶折线 z≈BACK_H）；火柴 `*_to_match_{i}` FIXED（×N，火柴不活动）
- standing 不穿模 assert：drawer+standing 每根 stick x-min > box_l/2（立在 sleeve 口外）；matchbook flap rest 与 comb 无 Y 交叠 + flap z-min ≥ back_h（立在 back panel 之上）
- captured-fit / 必要 overlap：element-scoped `allow_overlap`（drawer: tray↔sleeve 腔友配；flip: hinge_knuckle↔lid_panel）；packed 火柴相邻 touch allow_overlap；`allow_isolated_part`（ground_match_{i} ×2）。**matchbook flap 与 drawer+standing 在 rest 姿态均无穿模 → 不再有 flap↔panel / stick↔top_panel mask**
- grandfather：tray-in-sleeve / lid-on-body / flap captured-fit 省略 MatingContract，由 origin 检查（`fail_if_articulation_origin_far_from_geometry`）+ allow_overlap 守
- copied objects：match_{i} 遵循共享 helper（`_add_match_visuals` / `_add_vertical_match_visuals` / `_add_paper_match_standing`）+ pitch/grid placement + 全 FIXED joint policy；N 超单层切双层 packing（n24）
- palette_style 仅换材质 rgba（6 colorway），不计 slot_choice，不改拓扑

## Reject cases

- closure 造成无任何活动关节的死盒（0 non-fixed joint）→ 违反类别身份（matchbox 必须 ≥1 closure 活动机构）；摩擦压合 / 磁吸等无关节闭合不立候选。
- closure joint origin 放在盒底 / 任意点而非 drawer slide rail（sleeve +X）/ flip 后上缘（-Y, z=BODY_H）/ matchbook 顶折线（z=BACK_H）真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- closure rest pose 设成全闭合（盖盖死 / 抽屉全推入）→ 看不到火柴，与 viewer 目检火柴盒「半开露火柴」语义不符；应 rest 半开 / ~50° / ~70° 开。
- drawer 行程超 tray 插入深（脱出无 captured）→ 行程 inequality 未在 resolve 回缩，FAIL。
- 把 matchbook 与 match_arrangement / striker_style 自由笛卡尔展开（给 matchbook 配平躺木棍 / 双侧条 striker）→ 违反 matchbook 耦合（自带竖立纸 comb + front striker），应 gating 固定 native fill。
- flip_lid + standing_bundle 闭合时竖立火柴头穿过闭合 lid（未做头部 clearance 校验）→ collision FAIL；应限 standing 火柴长 ≤ body 内净高 + lid 余量或保 rest 开态。
- match_count 超盒宽 / 单层容量上限未切双层 / 未扩 grid（火柴互穿 / 溢出 tray）→ conditional/inequality 缺失，collision FAIL。
- 给 tray-in-sleeve / lid-on-body / flap captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + element-scoped allow_overlap。
- 把 palette_style / 尺寸 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette 不计 slot_choice；单层/双层是同 arrangement 内 N 派生 packing 非新 candidate）。
- 去掉 N 火柴 / 去掉 striker 退化成普通小纸盒，或补金属火轮 / 喷嘴当 lighter → 出 matchbox 类目身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。closure(3: drawer_slide / flip_lid / matchbook) × match_arrangement(2) × striker_style(2)；matchbook 耦合（自带 paper-comb native fill + front striker，不与两轴笛卡尔展开）→ 保守口径 drawer/flip 自由系 8 + matchbook 1 = 9 基础组合，叠 match_count N 等价类 ≈ 45 distinct ≫ 10。closure 含 PRISMATIC(drawer +X) + REVOLUTE(flip +X / matchbook +X) 两种 joint 拓扑 + 三种 root part tree。1 根 multiplicity 轴 match_count [4,40]（样本 N={6,10,16,24}，n24 双层 TOTAL=STICKS_PER_LAYER×NUM_LAYERS=24）。palette_style 6 colorway（classic_cream_kraft 锚 5★ + 5 板 realistic 纸/木推演：white+blue / brown+green / black+red / glossy white+navy / red+brown）。8 records 全读。match_arrangement / striker_style 各降到 2 candidate（仅两种真实拓扑收敛，理由 §4）。与 container_box（无火柴无擦火面）/ lighter（火轮喷嘴）/ cigarette pack（无头无擦火面）边界已划。开放问题见下。|

## 与相邻类别的边界（汇总）

- 不该混入：**container_box（储物 / 礼盒 / 运输箱）**——理由：无内含 N 火柴 + 无外擦火面，closure 词汇更宽（盖 / 门 / 抽屉 / 隔板）；matchbox 必有 N 火柴 + striker，更小尺度。
- 不该混入：**lighter（打火机）**——理由：金属 / 塑料壳 + 火轮 / 按钮 / 喷嘴 / 燃料腔机械点火；matchbox 靠独立火柴 + 擦火面取火，无点火机构。
- 不该混入：**cigarette pack（烟盒）/ 细长文具盒**——理由：烟支无反应头、盒无 striker；matchbox 子件带 head 且必带擦火面。

## 模板实现备注（可选）

- 共享 helper：`_add_match_visuals`（水平木棍 + 横 ellipsoid head，drawer/flip flat_row）/ `_add_vertical_match_visuals`（竖直木棍 + 顶 ellipsoid head，standing）/ `_add_paper_match_standing`（竖立纸 tab + box head，matchbook native）/ `_add_paper_match_flat`（散落纸火柴，matchbook ground）。closure helper 各自：`_build_sleeve_tray`（drawer：两端开口套筒 + 开顶托盘 + PRISMATIC）/ `_build_body_lid`（flip：开顶盒 + hinge_knuckle + 平盖 + REVOLUTE）/ `_build_cover_flap`（matchbook：折叠纸皮 + 顶 flap + REVOLUTE + native paper-comb）。striker helper：`_add_strikers(style)`（both_long_sides 两侧条 / one_side_plus_top_patch 单侧 + 顶 patch）。
- captured-fit overlap：`run_matchbox_tests` 里 element-scoped `ctx.allow_overlap`：drawer tray↔sleeve 腔（cross-section 友配，复制 P1 `expect_within`）/ flip hinge_knuckle↔lid_panel（复制 flip_lid 源）/ packed 火柴相邻 touch；`allow_isolated_part`(ground_match_{i} ×2，复制各 record)。**matchbook flap（向上延伸续片、+X 翻合）与 drawer+standing（外露区竖立）在 rest 姿态无穿模 → 不补 flap↔panel / stick↔top_panel mask；改为正向 assert（flap 离 comb、stick 立在 sleeve 口外）。**
- match_count multiplicity：`for i in range(N)` 发射 `match_{i}` + `*_to_match_{i}` FIXED，placement 由 arrangement 决定（flat 线性 / 双层 / grid）；N 上限 resolve clamp；超单层容量自动切双层（`NUM_LAYERS=ceil(N/STICKS_PER_LAYER)`，复制 n24 L55-L60 + L198-L212）。
- 行程 inequality：`resolve_config` 派生 drawer slide ≤ tray 插入 − retain_margin；flat 单层 N·pitch ≤ tray 内宽（超则双层）；standing grid 容量 ≥ N，在 resolve 投影 / 回缩。
- matchbook 耦合 gating：closure=matchbook 时 builder 固定 native paper-comb fill（`_add_paper_match_standing` ×N）+ front-panel striker，不读 match_arrangement / striker_style（sampler 也跳过这两轴的采样，slot_choices 标 native）。
- flip_lid + standing_bundle 头部 clearance：resolve 校验竖立火柴头不穿闭合 lid（限 STICK_L 或增 lid clearance），或保 rest 开态目检。
- 参考模板（实现阶段深读，按 slot graph / 运动拓扑选，非类名）：`agent/templates/Container_Box.py`（同家族「盒 + sliding_drawer」+ Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + captured-fit grandfather + multiplicity divider 轴）；`agent/templates/Accessories_Cushion.py`（`PALETTE_STYLES` 元组 + `palette_style=rng.choice(PALETTE_STYLES)` + `PALETTES[style]` dict colorway + 加权 multiplicity `rng.choices(weights=...)`）；含 multiplicity 轴的 fence/divider 类模板（N 加权采样 + `for i in range(N)` 复制 helper）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | drawer_slide + flat_row（单层）+ both_long_sides（基线）| rec_model-a-classic-safety-matchbox-...a0e600f3 | `sleeve` L91-L142 / `tray` L144-L166 / `sleeve_to_tray` PRISMATIC +X L172-L182 / `_add_match_visuals` L65-L80 / flat_row loop L184-L202 / `striker_{i}` ×2 L114-L120 / `ground_match_{i}` L204-L222 | 抽屉式套筒基线 + 平躺单层 + 两侧 striker + ground_match |
| S2 | A | flip_lid | rec_matchbox_var_flip_lid | `body`(+ `hinge_knuckle`) L87-L139 / `lid`(+ border) L144-L177 / `body_to_lid` REVOLUTE +X 后上缘 L186-L202 / allow_overlap knuckle↔lid L262-L272 | 翻盖盒体 + 后缘铰链翻盖（REVOLUTE +X，rest≈50° 开）|
| S3 | A/B/C | matchbook（耦合 native fill + front striker）| rec_matchbox_var_matchbook | `cover`(back/front panel + spine + base_strip + striker + comb) / `flap`（向上延伸续片）/ `cover_to_flap` REVOLUTE **+X** 顶折线 `(0,0,BACK_H)`（rest 微后倾、向前下翻扣合，无 flap allow_overlap）/ `_add_paper_match_standing` / comb loop / striker front-panel | 对折书皮（REVOLUTE +X，flap 续片向上、翻合不穿 back panel）+ 竖立纸火柴梳 native fill + front-panel striker |
| S4 | B | standing_bundle | rec_matchbox_var_standing | `_add_vertical_match_visuals` / 竖立 grid loop（drawer 下 grid 收束在抽出托盘外露区、不穿 top_panel；flip 下 stick 长 clamp 在闭合 lid 下）| 竖插成束（竖直 stick + 顶 head，col×row grid；整株立在 sleeve 口外 / 开顶盒内，无穿模）|
| S5 | C | one_side_plus_top_patch | rec_matchbox_var_striker_top | `side_striker`(单 -Y 侧条) L115-L122 / `top_striker_patch`(顶 patch) L146-L156 | 单侧条 + 顶面擦火块（+Y 侧 plain cream）|
| S6 | B(N) | flat_row 双层 packing（match_count N=24）| rec_matchbox_var_n24 | `STICKS_PER_LAYER`/`NUM_LAYERS`/`TOTAL_MATCHES`/`LAYER_DZ`/`UPPER_X_OFFSET` L55-L60 / 双层 loop `layer=i//STICKS_PER_LAYER` L198-L212 | match_count N 撑大时单层→双层 packing（multiplicity 轴上限切换）|
| S7 | B(N) | flat_row 单层 N 采样（N=6 / N=16）| rec_matchbox_var_n6（N=6）/ rec_matchbox_var_n16（N=16）| n6 `n_matches=6` pitch=0.0052 L191-L203 / n16 `n_matches=16` pitch=0.002 L191-L203 | match_count N 单层覆盖（小 N 疏 / 大 N 密 pitch 派生）|
