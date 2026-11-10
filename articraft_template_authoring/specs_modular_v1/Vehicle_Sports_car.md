# sports_car — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `sports_car` |
| template path | `agent/templates/Vehicle_Sports_car.py` |
| test path (optional) | `tests/agent/test_sports_car_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern` 说明：所有 slot 的 part/joint 都挂到一个共同的单体 `body`（lofted lower body + boolean 挖腔）作为 parent / chassis：车身剖面族决定 body mesh 本身，门 / 大灯 / 尾部 / 翻盖各自作为 body 的子件挂载（门 + 翻盖是 REVOLUTE 子件，灯 / 尾翼 / 排气是 body visual），轮 / 转向节经共享骨架挂到 body。无 multiplicity 轴。故主装配方式是 `parallel_children`（围绕共同 chassis 的并联子件），不是串链。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category（`external examples --rating-min 5 --category-slug sports_car` 返回 11 条，全部读取） |
| source_index_policy | only adopted module sources are indexed below |

读取的 11 个 5★ 样本（用途分类）：

- **双母资产（2）**：P1 `rec_classic-mercedes-300sl-gullwing-sports-car-in-de_…88ed264e`（vintage，gullwing 门，独立 roof dome）；P2 `rec_bright-yellow-lamborghini-diablo-style-wedge-sup_…655801c5`（modern wedge，scissor 门，一体 fastback 顶）。这两个母资产锚定本小类的两个 profile family（vintage ↔ wedge）。
- **干净单轴 body fork（2）**：`rec_sportscar_fastback_body_v01`、`rec_sportscar_teardrop_body_v01`（均 off P2，统一 door=scissor 基线上只换 `LOWER_SECTIONS`，干净隔离车身轴）。
- **干净单轴 feature fork（2）**：`rec_codex_car002_v07`（pop-up 翻灯盖，off P2 仅加一个前翻板 + 一个 REVOLUTE）；`rec_codex_car002_v09`（后舱百叶翻盖，off P2 仅加一个后翻板 + 一个 REVOLUTE）。
- **多轴 reskin（5，只取目标轴，把同时变化的其余特征当噪声过滤）**：`rec_porsche_911_v01`（dihedral 门 + round 灯 + ducktail）、`rec_pagani_huayra_v01`（round-pod quad 灯 + central-quad 排气 + 裸碳/银）、`rec_ferrari_f40_v01`（big GT wing + central 排气 + race-red）、`rec_bugatti_chiron_v01`（rounded body + dihedral 门 + quad-LED 灯 + two-tone）、`rec_koenigsegg_regera_v01`（dihedral 门 + 单中置 oval 排气 + icy-blue/carbon）。

**关键观察 / 对源映射的修正**：所有 11 个样本共享同一 kinematic 骨架（前轮 steer+spin、后轮 spin、双门 swing）和同一 `superellipse_side_loft(LOWER_SECTIONS, …)` 车身管线（截面 tuple `(y, z_min, z_max, width)`，loft 沿 +Y，XZ 超椭圆截面，exponents 控圆/楔）。源映射里关于「gullwing 同时在 Mercedes + Pagani 演示」**经源码复核不成立**：Pagani 的 `DOOR_AXIS` 实为 scissor 式横向轴（`(-1/norm,0,±tilt/norm)`，model.py:L110-113），并非纵向 Y 鸥翼轴。**gullwing（纵向 Y 轴顶脊铰）只有 P1 Mercedes 一份原生证据**，且与 vintage 独立 roof part 强绑定（开门会带走半个 roof）。这影响门槽降级理由与兼容性矩阵（见下）。

## 核心身份

`sports_car` = 双门、低矮、四轮、单座舱的高性能公路跑车 / 超跑 / hypercar。物理含义与不变结构：

- 单体 lofted 车身（`superellipse_side_loft` 侧剖面），boolean 挖出座舱腔 + 两个门洞（切穿侧面，开门见舱不见实心截面）。
- **恒 4 轮**：前 2 轮 steer（REVOLUTE 竖直 king-pin）+ spin（CONTINUOUS 横向轴），后 2 轮 spin（CONTINUOUS）。前轮 spin 挂在转向节上（spin 轴随转向角摆动）。
- **恒 2 门**：REVOLUTE 上掀 / 外展 / 侧开（轴随门机构槽变）。
- 直轴杆 hub-to-hub 穿 bored channel；独立 spinning 方向盘。
- 默认成熟域：公路合法的双门跑车比例（轴距 ~2.4–2.7、轮距 ~1.5–1.8、车高低矮），从经典 vintage（直立 greenhouse + 鼓包翼子板）到现代 wedge / hypercar（一体低矮 fastback）。

不该混入的相邻类别见末节边界。

## 槽位 + 候选模块表

> 所有 `model.py:Lx-Ly` 均指对应 `data/records/<id>/revisions/rev_000001/model.py`。源 id 缩写：
> P1 = `rec_classic-mercedes-300sl-gullwing-sports-car-in-de_20260608_164442_671467_88ed264e`，
> P2 = `rec_bright-yellow-lamborghini-diablo-style-wedge-sup_20260612_133511_811503_655801c5`。

### Slot A：body_profile_family（主 footprint 槽 —— 车身剖面族）

主 footprint 槽：每个候选是一张**不同的 `LOWER_SECTIONS` 剖面表（+ greenhouse 结构差异）**，不是缩放旋钮。单一基表 + 标量 L/W/H 缩放**到不了** vintage（窄身高顶 + 独立 roof part），故必须携 ≥2 张授权基表。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| modern_wedge（基线） | P2 | L102-118（`LOWER_SECTIONS`）；L120-147（一体 greenhouse 三壳 windshield/roof/rear，**无独立 roof part**）；L172-193（`_lower_body_mesh`，exponents=4.0 硬楔肩） | eligible if compatible | 宽体低矮楔形（width≈2.02 / track 1.78 / wb 2.65 / GH≈0.35），一体 fastback 顶 |
| vintage_pontoon | P1 | L121-142（`LOWER_SECTIONS`，20 段窄身 + 鼓包前后翼子板 + 收腰门槛）；L144-155（**独立 roof dome part** ROOF_SECTIONS + windshield/rear_window shell）；L205-244（`_build_body_parts`，exponents=2.6 圆润） | eligible if compatible | 窄身高顶老爷车（width≈1.63 / track 1.49 / wb 2.40），直立 greenhouse + 独立 roof part + 鼓包翼子板。**证明 loft 能撑老爷车比例（剖面 shape 差异，非缩放）** |
| fastback | `rec_sportscar_fastback_body_v01` | L103-119（`LOWER_SECTIONS`，rounded nose + 宽 rear haunches，width 峰值 2.08@y=-1.30）；L176-184（`_lower_body_mesh`，exponents=3.0） | eligible if compatible | 911 式后置溜背，宽 rear haunch（干净单轴 fork off P2，仅改剖面表） |
| organic_teardrop | `rec_sportscar_teardrop_body_v01` | L103-119（`LOWER_SECTIONS`，前宽后窄水滴 width 2.00@y=1.0→1.40@tail）；L173-180（`_lower_body_mesh`，exponents=2.2 软曲面） | eligible if compatible | Huayra 式有机水滴曲面（干净单轴 fork off P2，仅改剖面表） |

> 备选 `rounded_hyper`（Chiron，`rec_bugatti_chiron_v01` L124-140，exponents=2.2 圆胖 W16）与 organic_teardrop 拓扑近似（同为低 exponent 圆润单体 loft，无独立 roof），**并入 organic_teardrop 家族不单列**，避免拓扑等价类重复。Slot A 实有 4 个结构不同的候选。

### Slot B：door_mechanism（结构槽 —— 门铰链拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| scissor_butterfly（基线） | P2 | L90-98（`DOOR_AXIS` 横向 X 主 + Z 微仰 `(-1/norm,0,±0.25/norm)`）；L726-744（door REVOLUTE 上掀，hinge=(0.88,0.84,0.70)） | eligible if compatible | 剪刀/蝴蝶门：前缘铰、横向 X 为主轴、上掀（cross-body 已验：P2 wedge + Ferrari sharp-wedge + Pagani teardrop 均用此轴） |
| gullwing | P1 | L95-104（`DOOR_AXIS` 纵向 Y `(0,∓1,0)`，HINGE_Z≈0.88 顶脊铰）；L664-721（`make_door`：门携侧窗 + flank skin，roof 保持固定整 dome）；L814-833（door REVOLUTE 上掀外展） | eligible if compatible | 鸥翼门：顶脊纵向 Y 轴、整片上掀。**只 P1 一份原生证据**，与 vintage 独立 roof 强绑定 |
| dihedral | `rec_porsche_911_v01` / `rec_koenigsegg_regera_v01` / `rec_bugatti_chiron_v01` | Porsche L105-108（`_DH=(0,-0.22,0.975)` 归一化）+ L875-894（door REVOLUTE 外展上旋）；Koenigsegg L102-105（`_DH=(0,-0.45,0.89)`）+ L865-883；Bugatti L114-117（`_DH=(0,-0.42,0.91)`）+ L1081-1099 | eligible if compatible | 二面角 / synchro-helix 门：前缘前倾近竖轴自定义矢量、外展+上旋。cross-body 已验（fastback + teardrop + rounded 三种车身） |

> **降级说明（Slot B 实有 3 候选，达 SPEC_TEMPLATE.md「3-6 目标」下限）**：曾考虑第 4 候选 `conventional`（竖轴 B 柱铰侧开门，老爷车实际多为侧开）。**语料缺该数据点**：用 `articraft fork`(qwen agent) 造 conventional / gullwing-on-wedge / scissor-on-vintage 单轴门变体**两轮（max-turns 80 / 90）全失败**，根因非几何（scissor-on-vintage 几何已成）而是 fork-agent harness 把父资产门机构 contract（铰链轴 + articulation 名）作为 immutable scaffold 注入、改门必违约。改门机构的干净数据点须改走 `articraft external`（直接编辑 model.py）路线，本 SPEC 阶段不造。故 Slot B 收 3 个 converged 候选，`conventional` 留作 future external-edit 数据点（reviewer 注记），不进首版 seed domain。

### Slot C：headlight_style（大灯 —— 唯一带可选拓扑子选项的灯槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| exposed_rect（基线） | P2 | L435-486（车头前缘平嵌矩形/条灯簇：surround/reflector/bar/lens，纯 body visual，无 joint） | eligible if compatible | 现代平嵌矩形条灯（visual-only） |
| round_fixed | P1 / `rec_porsche_911_v01` | P1 L513-543（圆形铬圈灯碗 set into fender crown）；Porsche L552-596（深 round bucket + chrome ring + clear convex lens + 内反射盘，rpy 前仰，纯 body visual） | eligible if compatible | 圆灯碗/凸透镜（visual-only） |
| quad_cluster | `rec_pagani_huayra_v01` / `rec_bugatti_chiron_v01` | Pagani L477-543（sculpted pod + 3× round jewel{cup+bezel+lens} + amber turn）；Bugatti L665-708（dark housing + 4× LED bar「four eyes」+ chrome brow + amber DRL，纯 body visual） | eligible if compatible | 四灯组/quad-LED 簇（visual-only） |
| pop_up_cover | `rec_codex_car002_v07` | L604-637（`make_headlight_cover` part：`cover_panel`+`cover_front_seam`+`cover_outer_seam`+`hinge_pin`）；L779-791（`headlight_cover_{side}_hinge` REVOLUTE，axis=(1,0,0)，upper=0.90） | eligible if compatible | **翻灯（带铰活动盖）改拓扑**：加 2 个 part + 2 个 REVOLUTE。是 round/rect 之上的可选叠加层（盖下仍是嵌灯） |

> Slot C 是 **shape 选择（exposed_rect / round / quad，纯外观）× pop_up{有/无}（结构性）** 的乘积。pop_up 是叠加在底层灯之上的可选翻盖（盖 + 铰），下游建模为「C_shape ∈ {rect, round, quad}」+「C_popup ∈ {0,1}」两个子轴；pop_up 才改 part/joint 拓扑。pop_up 盖下默认配 round/rect（不配 quad-pod，盖会挡住整组 pod —— 见兼容性矩阵）。

### Slot D：rear_treatment（尾部 —— 尾翼 / 鸭尾 / 后舱翻盖 + 排气正交子轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| integrated（基线） | P2 | L529-543（百叶 engine deck，无独立大翼，纯 body visual）；L568-589（黑尾板 + 尾灯，整合尾） | eligible if compatible | 整合尾（visual-only） |
| big_gt_wing | `rec_ferrari_f40_v01` / `rec_bugatti_chiron_v01` | Ferrari L544-566（P2 原生 twin pylon + `wing_blade`）/ F40 L568-595（`wing_pylon`+`wing_blade`+`wing_gurney`+endplate）；Bugatti L778-792（`wing_support`+`wing_blade`+`wing_gurney`，纯 body visual） | eligible if compatible | 大 GT 双柱尾翼 + gurney lip（visual-only，独立 part 但 fixed） |
| ducktail | `rec_porsche_911_v01` | L653-676（`ducktail_blade`+`ducktail_lip`+`ducktail_riser_{side}`，低 lip 贴 engine lid，纯 body visual） | eligible if compatible | 鸭尾扰流低 lip（visual-only） |
| engine_louver_cover | `rec_codex_car002_v09` | L604-629（`engine_cover` part：`cover_panel`+5×`cover_louver_k`+`cover_hinge_pin`）；L768-777（`engine_cover_hinge` REVOLUTE，axis=(1,0,0)，upper=0.75） | eligible if compatible | **后舱百叶翻盖（带铰）改拓扑**：加 1 个 part + 1 个 REVOLUTE |

正交子轴 **exhaust ∈ {side, central_quad, central_single}**（不改 part-tree 拓扑等价类，是 body visual 布局变体，作为 D 的并行外观子轴）：

| sub_choice | 5_star_source | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|
| side（基线） | P2 | L568-589（两侧出 `exhaust_{side}` 黑管，左右各一） | 两侧出 |
| central_quad | `rec_pagani_huayra_v01` / `rec_ferrari_f40_v01` | Pagani L735-762（2×2 钻石簇 4× `exhaust_{tag}` + `exhaust_ring_{tag}` + `exhaust_surround`）；Ferrari L623-650（中置 twin `exhaust_{side}` + `exhaust_ring_{side}` + 第三 `exhaust_center`/`exhaust_ring_center`） | 中置四出/三出簇 |
| central_single | `rec_koenigsegg_regera_v01` | L705-721（单大 `exhaust_ring`(chrome) + `exhaust`(dark bore) 中置 oval） | 单中置 oval |

> Slot D 建模为「D_blade ∈ {integrated, big_gt_wing, ducktail}（外观）」+「D_louver_cover ∈ {0,1}（结构性翻盖，可叠加在任意 D_blade 之上）」+「D_exhaust ∈ {side, central_quad, central_single}（外观子轴）」。只有 engine_louver_cover 改 part/joint 拓扑。

### Slot E：livery_palette（涂装 / 材质族 —— 纯外观，必填 `palette_style` 参数）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| gloss_solid（基线） | P2 | L280-291（`gloss_yellow` 单色高光 + 黑饰 + 银轮 + 琥珀/红尾） | eligible if compatible | 单色高光漆 + 黑饰条 |
| metallic_chrome | P1 / `rec_porsche_911_v01` | P1 L293-303（`maroon` 深红 + `chrome`/`dark_chrome` 镀铬 grille/bumper/headlamp ring）；Porsche L350-362（`guards_red` + chrome） | eligible if compatible | 金属漆 + 镀铬饰条（vintage/复古族） |
| bare_carbon_accent | `rec_pagani_huayra_v01` / `rec_koenigsegg_regera_v01` | Pagani L298-309（`carbon_fibre` 裸碳 body + `polished_alloy` 银饰 + `carbon_trim`）；Koenigsegg L286-297（`ice_blue` + `carbon`） | eligible if compatible | 裸碳纤 body + 抛光铝/银饰条 |
| two_tone | `rec_bugatti_chiron_v01` | L299-316（`silver_upper` + `bugatti_blue` 双色 + `chrome_trim`）；L337-347（沿 C-line 高度 `BLUE_TOP=0.58` 拼第二张 inset side-loft 蓝下身皮）；L377-417（`cline_{side}_k` C 线 chrome 描边） | eligible if compatible | 双色分色（C 线分界，下身另一张 inset loft 皮 + chrome 描边） |

> **`palette_style` colorway（≥3，目标 4-6；每 seed 抽一个；与所有结构槽完全正交、不参与 clearance）**，取自 5★ 实测材质集：
> 1. `diablo_gloss_yellow`（P2 L280-291：gloss_yellow + black_trim + silver_alloy + amber/tail_red）
> 2. `vintage_maroon_chrome`（P1 L293-303：maroon + chrome + dark_chrome + lens_pale）
> 3. `pagani_bare_carbon_silver`（Pagani L298-309：carbon_fibre + polished_alloy + carbon_trim）
> 4. `bugatti_two_tone_silver_blue`（Bugatti L302-316：silver_upper + bugatti_blue + chrome_trim，需 two_tone 几何皮）
> 5. `ferrari_rosso_corsa`（Ferrari L276-288：rosso + chrome + ferrari_yellow shield + silver_alloy）
> 6. `koenigsegg_icy_blue_carbon`（Koenigsegg L286-297：ice_blue + carbon + dark_alloy + lens_pale）

## 槽位图（slot graph）

pattern: `parallel_children`（围绕共同单体 `body` chassis 的并联子件）

```
                          [Slot A body_profile_family]
                          单体 lofted body（superellipse_side_loft）
                          + boolean 挖座舱腔 + 2 门洞（切穿侧面）
                                       |
        ┌───────────┬──────────────────┼───────────────────┬────────────────┐
        |           |                  |                    |                |
  共享骨架     [Slot B door]      [Slot C headlight]   [Slot D rear]    [Slot E livery]
  (固定)      门 ×2               灯 visual + 可选翻盖    尾 visual + 可选翻盖  纯材质
        |           |                  |                    |                （正交，不接触）
  前轮 steer    door_{L,R}_hinge   (pop_up:                (louver_cover:
  REVOLUTE(Z)   REVOLUTE             headlight_cover_       engine_cover_
  ±0.40         (轴随机构槽:          {side}_hinge           hinge REVOLUTE
  king-pin      scissor=X微仰/        REVOLUTE axis=X        axis=X upper=0.75)
   ↳ 前轮 spin   gullwing=Y/          upper=0.90)            + exhaust 子轴
   CONTINUOUS(X) dihedral=_DH)                               (side/quad/single)
  后轮 spin
  CONTINUOUS(X)
```

接口点位与 joint：

- **Slot A → 共享骨架**：A 决定 `body` mesh + 关键尺度常量（`HALF_TRACK` / `FRONT_AXLE_Y` / `REAR_AXLE_Y` / `WHEEL_R`），骨架的转向节 origin、轮 origin、轴杆 channel 全部从这些常量派生。骨架不随 A 变拓扑（始终 2 steer REVOLUTE + 4 spin CONTINUOUS），只随 A 的 track/wheelbase 平移挂点。**mating**：转向节 steer 关节 origin=`(±HALF_TRACK, FRONT_AXLE_Y, WHEEL_R)`，轴=Z；轮 spin 关节轴=X。
- **Slot A → Slot B**：门挂点 = body 侧面门洞上缘 / 前缘。门 REVOLUTE 的 origin（hinge 点）与 axis 由 B 决定（scissor=前缘横向、gullwing=顶脊纵向、dihedral=前缘前倾矢量）。**clearance 约束**：gullwing 顶脊铰需要足够 roof 高度（见兼容性矩阵）。
- **Slot A → Slot C / D**：灯簇 / 尾翼 / 排气挂到 body 前缘 fender corner / 尾板，Y 由车长（A 的剖面表 y 范围）派生。pop_up 翻盖 REVOLUTE origin 在前 fender（`(±0.54, 1.82, 0.515)` 量级，axis=X），louver 翻盖 REVOLUTE origin 在后舱（`(0, -1.02, 0.79)` 量级，axis=X）。
- **Slot E**：纯材质 override，挂到所有上述 part 的 material 字段，无几何接口、无 clearance。two_tone 额外派生一张 inset 蓝下身 loft 皮（同 A 的剖面表 + `BLUE_TOP` 截顶）。

互斥 / 可选 / 派生：

- B 的 gullwing 派生自 A（强偏好 vintage_pontoon，需独立 roof part；low wedge 上需顶铰 clearance gate）。
- C 的 pop_up、D 的 louver_cover 为**可选** moving child（0/1），互不干涉、可共存。
- D 的 exhaust 子轴与 D_blade 正交。
- E 与所有结构槽正交。

## 每槽位 Module Emits / Interfaces

### Slot A / module modern_wedge / vintage_pontoon / fastback / organic_teardrop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（单体 lofted lower body + boolean 座舱腔 + 门洞 + 轴杆 channel）；vintage 额外 emit 独立 `roof` dome part + windshield/rear_window shell | P2 / L172-275；P1 / L205-314 |
| internal joints | 无（A 自身不带 joint；joint 由共享骨架 + B/C/D 提供） | — |
| upstream interface | root：body 为整模型 parent chassis；轮触地 z=0，车头 +Y | P2 / L277-296 |
| downstream interface | 派生尺度常量 `HALF_TRACK`/`FRONT_AXLE_Y`/`REAR_AXLE_Y`/`WHEEL_R` 供骨架；门洞上缘/前缘供 B；fender corner + 尾板供 C/D | P2 / L48-98 |

### Slot B / module scissor_butterfly / gullwing / dihedral
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_left` / `door_right`（门皮 + 侧窗 glass + 镜 + handle，gullwing 额外携侧窗框） | P2 / L610-680；P1 / L664-721 |
| internal joints | 无（门内部刚性） | — |
| upstream interface | hinge 挂到 body 门洞缘；origin + axis 随机构（scissor `(0.88,0.84,0.70)`/X微仰；gullwing `(±0.52,0,0.88)`/Y；dihedral 前缘/`_DH`） | P2 / L90-98,726-744；P1 / L95-104,814-833；Porsche / L105-108,875-894 |
| downstream interface | door REVOLUTE 上掀/外展（活动件，articulation 语义：positive q 开门） | P2 / L726-744 |

### Slot C / module exposed_rect / round_fixed / quad_cluster (+ pop_up_cover 可选)
| emits | 描述 | 来源 |
|---|---|---|
| parts | 灯簇 = body visual（rect 条灯 / round 灯碗 / quad pod）；pop_up：额外 `headlight_cover_{side}` part（`cover_panel`+seams+`hinge_pin`） | P2 / L435-486；Porsche / L552-596；Pagani / L477-543；v07 / L604-637 |
| internal joints | pop_up：`headlight_cover_{side}_hinge` REVOLUTE axis=(1,0,0) upper=0.90（×2） | v07 / L779-791 |
| upstream interface | 灯挂到 body 前缘 fender corner；pop_up hinge origin `(±0.54,1.82,0.515)` | v07 / L779-791 |
| downstream interface | pop_up：翻盖上掀露灯（活动件） | v07 / L779-791 |

### Slot D / module integrated / big_gt_wing / ducktail (+ engine_louver_cover 可选) (+ exhaust 子轴)
| emits | 描述 | 来源 |
|---|---|---|
| parts | 尾翼/鸭尾/整合尾 = body visual（`wing_blade`+`wing_gurney`+pylon / `ducktail_blade`+`ducktail_lip`+riser / 整合）；排气 visual；louver：额外 `engine_cover` part（`cover_panel`+5×louver+`cover_hinge_pin`） | F40 / L568-595；Porsche / L653-676；Pagani / L735-762；v09 / L604-629 |
| internal joints | louver：`engine_cover_hinge` REVOLUTE axis=(1,0,0) upper=0.75（×1） | v09 / L768-777 |
| upstream interface | 尾翼/排气挂到 body 尾板；louver hinge origin `(0,-1.02,0.79)` | v09 / L768-777 |
| downstream interface | louver：后舱盖上掀（活动件） | v09 / L768-777 |

### 共享骨架（fixed，不属任一 slot —— 全变体一致）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{front,rear}_{left,right}`(tire+disc)、`steer_knuckle_{l,r}`、axle 杆、spinning steering wheel | P2 / L682-744 |
| internal joints | 前 `{knuckle}_steer` REVOLUTE axis=Z ±0.40（×2）；4× `{wheel}_spin` CONTINUOUS axis=X（前轮挂 knuckle、后轮挂 body） | P2 / L746-781 |
| upstream interface | 挂到 body，origin 由 A 的 track/wheelbase 常量派生 | P2 / L751-771 |
| downstream interface | 轮触地 z=0；前轮 spin 随 steer 摆动 | P2 / L764-781 |

> 骨架 joint 计数（基线 Diablo）：**2 REVOLUTE(steer) + 2 REVOLUTE(door) = 4 REVOLUTE + 4 CONTINUOUS(spin)**。叠加可选翻盖：+pop_up = +2 REVOLUTE，+louver = +1 REVOLUTE。（源映射「6 REVOLUTE + 2 CONTINUOUS」与实测略有出入；以实测为准：基线 4 REVOLUTE + 4 CONTINUOUS，pop_up/louver 各增 REVOLUTE。方向盘 spin 另计。）

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_profile_family` | enum | {modern_wedge, vintage_pontoon, fastback, organic_teardrop} | — | choice | deterministic procedural sampler 加权选；决定 `LOWER_SECTIONS` 表 + greenhouse 结构 | Slot A 表 |
| `door_mechanism` | enum | {scissor_butterfly, gullwing, dihedral} | — | choice | sampler 选；gullwing 受 body gate（见 conditional） | Slot B 表 |
| `headlight_shape` | enum | {exposed_rect, round_fixed, quad_cluster} | — | choice | sampler 选（纯外观） | Slot C 表 |
| `headlight_popup` | bool | {0, 1} | 0 | conditional | =1 时加翻盖 part+REVOLUTE；与 quad_cluster 不共存（gate 见兼容性） | v07 / L604-637 |
| `rear_blade` | enum | {integrated, big_gt_wing, ducktail} | — | choice | sampler 选（纯外观） | Slot D 表 |
| `rear_louver_cover` | bool | {0, 1} | 0 | independent | =1 时加后舱翻盖 part+REVOLUTE（与任意 rear_blade、与 pop_up 共存） | v09 / L604-629 |
| `exhaust_layout` | enum | {side, central_quad, central_single} | side | choice | sampler 选（纯外观布局） | Slot D 排气子表 |
| `palette_style` | enum | {diablo_gloss_yellow, vintage_maroon_chrome, pagani_bare_carbon_silver, bugatti_two_tone_silver_blue, ferrari_rosso_corsa, koenigsegg_icy_blue_carbon} | — | choice | sampler 选；纯材质，正交无 clearance；two_tone 派生 inset 下身皮 | Slot E 表 |
| `track_scale` | float | [0.92, 1.08] | 1.0 | independent | 缩 `HALF_TRACK`；clamp 后轮well/轴杆同步 | P2 / L50,63-67 |
| `wheelbase_scale` | float | [0.94, 1.06] | 1.0 | independent | 缩 `FRONT_AXLE_Y`/`REAR_AXLE_Y` 间距；clamp | P2 / L51-52 |
| `body_height_scale` | float | [0.95, 1.06] | 1.0 | independent | 缩剖面 z_max；clamp（不破 greenhouse seam） | P2 / L102-118 |
| `wheel_radius` | float | derived | 0.33 | equation | `= clamp(0.31·body_height_scale, 0.31, 0.36)`，触地 z=0 锚定不变 | P2 / L48 |
| `door_open_max` | float | [1.2, 1.6] | 1.4 | conditional | 上限随 door_mechanism（gullwing≤1.2 防扫穿、scissor/dihedral≤1.6） | P2/L98；P1/L104 |
| (—) | constraint | — | — | inequality | 门 swept-volume 顶/侧不穿 body：gullwing on low-wedge 须 `roof_top_z ≥ hinge_z + door_half_height·sin(open)`；不满足则回缩 door_open_max 或拒绝该 (body,door) 组合 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 前轮 steer ±0.40 throw 不扫入 fender well：`well_inboard_wall ≤ track − tire_half_width − steer_sweep`，违反按比例回缩 track_scale | P2 / L63-67,750 |
| (—) | constraint | — | — | conditional | gullwing 需独立 roof part（仅 vintage_pontoon 原生有）；在 wedge/fastback/teardrop 上选 gullwing 须先合成 roof shoulder 锚 + 通过顶铰 clearance gate，否则 sampler fallback 到 dihedral | P1 / L144-155,95-104 |

连续尺寸采样契约：先采 `track_scale`/`wheelbase_scale`/`body_height_scale`（independent，均匀）→ 派生 `wheel_radius`（equation）→ 用门 swept-volume + 前轮 steer-sweep 两条 inequality 投影/回缩 → 解析 `door_open_max` 与 gullwing-on-non-vintage 的 conditional 范围。所有约束在 `resolve_config` 求解，不留到 builder。

## Multiplicity / Copy Logic

- **无模板级复制数量逻辑（无 `*_count`）**：核心结构由固定 named slots 表达。轮恒 ×4（前 steer+spin、后 spin）、门恒 ×2、转向节恒 ×2 —— 均为「跑车」的定义而非可变 N。共享 kinematic 骨架（2 steer REVOLUTE + 4 spin CONTINUOUS + 2 door REVOLUTE）在全部变体中完全一致，骨架不拆、不暴露为 count。
- module-local 固定循环（非模板轴、不是 multiplicity）：左右镜像子件（door / steer_knuckle / wheel / 灯簇 / 排气簇）经 `side=±1` 镜像或 `zip` 循环发射；这是固定 2 / 4 个对称件的字面展开，不暴露为 `*_count` 参数、N 不可变。pop_up 翻盖固定 ×2（左右）、louver 翻盖固定 ×1。
- 模板建议 N_range：无（计数全固定）。
- copied object / naming / placement / joint policy：
  - copied object：左右对称 `wheel_{front,rear}_{left,right}_{tire,disc}` / `steer_knuckle_{l,r}` / `door_{left,right}` / `headlight_cover_{left,right}`；body 为单体 loft + boolean 挖腔。
  - naming：`wheel_*`、`steer_knuckle_{l,r}`、`door_{left,right}`、`headlight_cover_{side}`、`engine_cover`、`exhaust[_{tag}]`、`wing_blade`/`ducktail_blade`；车身随族命名。
  - placement：轮触地 z=0；车身沿 +Y（车头 +Y）；左右沿 ±X 镜像。
  - joint policy：前轮 steer(REVOLUTE 竖直 king-pin ±0.40) ⊕ spin(CONTINUOUS X)；后轮 spin(CONTINUOUS X)；门 REVOLUTE（轴随机构槽）；pop_up / louver 各自 REVOLUTE 翻板；直轴杆穿 bored channel。

## 拓扑多样性审计

总组合数（合法、含外观槽）：
A(4) × B(3) × C_shape(3) × C_popup(2) × D_blade(3) × D_louver(2) × D_exhaust(3) × E_palette(6)
= 4×3×3×2×3×2×3×6 = **23328**（去掉 gate 掉的非法组合后仍 ≫ 20；纯 door×light×rear×livery 口径 3×(3×2)×(3×2×3)×6 同样 ≫20）。

**结构性 distinct（改 part/joint 拓扑等价类的轴）**：
A(4) × B(3) × C_popup{有/无}(2) × D_louver{有/无}(2) = **48 结构性 distinct**。


seed_domain_policy：procedural_first（`seed=0` 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 对每个 enum 槽做加权采样（slot 顺序 A→B→C→D→E，body_profile_family 略均匀、door 略偏 scissor/dihedral（gullwing 较稀有因受 body gate）），可选 bool（popup/louver）各以 ~30% 概率开。`resolve_config` 先解析 conditional（gullwing-on-non-vintage 须过顶铰 gate 否则 fallback dihedral；popup × quad_cluster 互斥 → popup 时强制 shape∈{rect,round}），再采连续 scale 并按两条 inequality 回缩。无大型 curated/modulo 表作主 seed domain。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本类别仅结构性轴 48 distinct，叠加外观槽（shape×blade×exhaust×palette = 3×3×3×6=162）后 `slot_choices_for_seed` 维度足以在 1000 seed 内产 ≥300 distinct 元组组合；若下游只记结构轴则 48 为天花板，需在 `slot_choices_for_seed` 中纳入 headlight_shape/rear_blade/exhaust_layout（它们换 module factory、属合理 (slot,choice) 元组）以达 ≥300。**这是给 reviewer 的一个 open question**：是否把纯外观槽计入 topology 元组（机械允许，但语义上是外观）——建议计入以达 ≥300 同时在 spec 注明结构性下限是 48。

regression overrides：none（首版不需要）。如造模板期出现已知失败回归再按 seed + 理由补，sparse。

Controlled local parameterization：`track_scale`[0.92,1.08]、`wheelbase_scale`[0.94,1.06]、`body_height_scale`[0.95,1.06]（independent，clamp）；`wheel_radius`（equation derived from body_height_scale，触地锚定）；`door_open_max`[1.2,1.6]（conditional on door_mechanism）。两条 inequality：门 swept-volume clearance、前轮 steer-sweep vs fender well。全部在 `resolve_config` clamp/派生，不破坏骨架 joint origin、门 hinge 接口或类别 identity（4 轮 2 门固定）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A→B→C→D→E 加权 choice + popup/louver bool；连续 scale 后采 | slot_choices_for_seed matches build choices |
| compatibility matrix | gullwing 强偏好 vintage（非 vintage 须过顶铰 gate 否则 fallback dihedral）；popup ⊥ quad_cluster（互斥，popup 强制 rect/round）；popup+louver 共存 OK；exhaust 子轴自由；palette 全正交 | no floating, no door/wheel collision, hinge axis correct, gullwing roof-clearance, popup/louver coexist |
| controlled local variation | track/wheelbase/body_height/door_open scale + clamp；wheel_radius derived | proportions vary without breaking骨架 origin / 门 hinge / wheel 触地 / clearance |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮，0-999 成熟度审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_profile_family | 4 | yes | yes | modern_wedge/vintage_pontoon/fastback/organic_teardrop（rounded_hyper 并入 teardrop） |
| B door_mechanism | 3 | yes | yes | scissor/gullwing/dihedral；conventional 留 future external-edit（agent-fork 结构性阻塞） |
| C headlight_shape | 3 | yes | yes | rect/round/quad（× pop_up 0/1 子轴叠加，pop_up 才改拓扑） |
| D rear_blade | 3 | yes | yes | integrated/big_gt_wing/ducktail（× louver_cover 0/1 + exhaust{side/quad/single} 子轴） |
| E palette_style | 6 | yes | yes | 纯外观，6 colorway |

兼容性矩阵（compatibility / gating，按易坏组合优先排除）：

- **door ⊥ body（分离性）**：scissor/dihedral 已跨车身 cross-body 验证（scissor∈{wedge,sharp-wedge,teardrop}、dihedral∈{fastback,teardrop,rounded}），可自由组合。gullwing 仅 vintage 原生 → **gate**：gullwing 强偏好 vintage_pontoon；在 wedge/fastback/teardrop 上须先合成 roof shoulder 锚 + 过顶铰 clearance（`roof_top_z ≥ hinge_z + door_half·sin(open)`），不过则 sampler fallback 到 dihedral。
- **gullwing-on-wedge clearance**：vintage roof 高 z≈1.17，wedge 一体顶低；low body 上 gullwing 顶铰需校验开门 swept-volume 不穿顶 / 不悬空，必要时回缩 door_open_max 到 ≤1.2。
- **pop_up × quad_cluster 互斥**：翻盖会盖住整组 round-pod / quad 簇 → popup=1 时 headlight_shape 强制 ∈ {exposed_rect, round_fixed}（单灯碗可被盖覆盖，符合 v07 真实结构）。
- **pop_up（前）+ engine_louver_cover（后）可共存**：各自独立 REVOLUTE 翻板，互不干涉。
- **共享骨架与全部槽自由组合**：骨架不随槽变拓扑。
- **exhaust 子轴 / palette 与所有结构槽正交**：central_quad/single/side 任意配；palette 纯材质不参与 clearance（two_tone 仅派生 inset 下身皮，沿同一剖面表，无碰撞）。

## Validator

- slot_choices_for_seed 返回已实现 module 名（A/B/C_shape/C_popup/D_blade/D_louver/D_exhaust/E 的稳定元组）。
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling；seed=0 不特殊。
- compatibility matrix / gating 阻止非法组合（gullwing-on-non-vintage 无 roof gate、popup×quad、门/轮碰撞）。
- regression overrides 稀疏（首版 none）。
- 不无限轮换小型 curated 表作主 seed domain。
- 受控局部 scale（track/wheelbase/body_height/door_open）clamp，不破坏骨架 joint origin、门 hinge 接口、wheel 触地、类别 4 轮 2 门固定。
- cross-part scale 依赖（wheel_radius equation、门 swept-volume + steer-sweep inequality、gullwing-roof conditional）在 resolve_config 求解，不留到 builder。
- 关键 InterfaceSpec/MatingContract 存在：转向节 steer origin、轮 spin、门 hinge、pop_up/louver hinge、轴杆 channel。
- 关键 joint 类型/轴/范围：前 steer REVOLUTE axis=Z ±0.40；4 spin CONTINUOUS axis=X；门 REVOLUTE（轴随机构）；pop_up REVOLUTE axis=X upper=0.90；louver REVOLUTE axis=X upper=0.75。
- copied object 遵循 naming/placement（左右 ±X 镜像，轮触地 z=0）。

## Reject cases

- 把轮数 / 门数做成 `*_count` 可变 multiplicity 轴（4 轮 2 门是跑车定义，固定）。
- 单一基剖面表 + 标量 L/W/H 缩放冒充 body_profile_family（到不了 vintage 窄身高顶 + 独立 roof，必须 ≥2 张授权剖面表）。
- gullwing 门挂到 low wedge 而不过顶铰 clearance gate（开门扫穿顶 / 门悬空）。
- pop_up 翻盖叠加在 quad_cluster pod 上（盖挡住整组灯，违反 v07 真实结构）。
- 拆掉共享 kinematic 骨架或改其拓扑（前轮丢 steer 或丢 spin、后轮丢 spin、门丢 REVOLUTE）。
- 门洞没切穿侧面（开门见实心截面而非座舱腔）。
- 连续 scale 当独立自由变量各抽各的，不解 wheel_radius equation / 门 swept-volume 与 steer-sweep inequality（builder 阶段才碰撞）。
- 用小型 curated / modulo 表作主 seed domain 而非 deterministic procedural sampling。
- 把 livery/palette 或 headlight 透镜形状当结构 candidate（纯外观，不改 part/joint 拓扑）。

## 与相邻类别的边界

- 不该混入：**toy_car**（玩具车）——玩具车通常是简化整体壳 + 简化或无真实转向 / 无独立门 articulation，比例卡通化；sports_car 须有真实双门 swing + 前轮 steer king-pin + 4 轮 spin 的完整 kinematic 骨架与公路合法比例。
- 不该混入：**car_axles**（车桥 / 底盘组件）——那是悬挂/桥/传动的子系统级零件，没有完整车身 greenhouse / 门 / 灯 / 尾翼；sports_car 是整车成品，车身单体 loft 是主结构。
- 不该混入：**heavy vehicle（卡车 / 巴士 / 工程车）**——大尺寸、货箱 / 多轴 / 高底盘、非双门跑车比例；sports_car 锚定低矮双门双座舱、轴距 ~2.4–2.7、4 轮。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待审。Open questions：(1) gullwing 仅 P1 一份原生证据（源映射「Pagani 也 gullwing」经源码复核不成立，Pagani 实为 scissor 轴）——是否接受 gullwing 单源 + 与 vintage 绑定 + 非 vintage 须合成 roof gate，或要求先走 external-edit 补 gullwing-on-wedge 干净数据点。(2) topology ≥300 是否允许把纯外观槽（headlight_shape/rear_blade/exhaust_layout）计入 slot_choices 元组以达标（机械允许，结构性下限 48）。(3) Slot B 仅 3 候选（conventional 因 agent-fork 结构性阻塞缺失，留 future external-edit）——是否接受 3 候选收尾。 |

## 模板实现备注（可选）

- 共享 helper：所有 body 候选共享 `superellipse_side_loft` + `_box_cutter`（flip-winding 实心切刀）+ wheel-arch / cabin / axle-channel boolean 管线；只换 `LOWER_SECTIONS` 表 + exponents + (vintage) roof part。
- InterfaceSpec/MatingContract 重点：门 hinge（轴随机构槽，gullwing 须 roof shoulder 锚）、前转向节 steer origin（随 track/wheelbase 派生）、轴杆穿 bored channel（captured-pin，需 element-scoped allow_overlap）、pop_up/louver 翻盖 hinge。
- captured-pin overlap：轴杆 channel ⟂ body、翻盖 hinge_pin ⟂ body、门皮 seat 进门洞 —— 复制现有 reskin 的 allow_overlap 局部声明，per-element 限定。
- 暂不进 seed domain：conventional 门（须 external-edit）、rounded_hyper 单列（并入 teardrop）。
