# stove — Modular Spec

> 来源小类：`picture/Other/stove`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Other_stove.md`。
> **"stove" 在此 = 独立式落地灶 / 燃气灶台（freestanding gas range / cooktop）**：一只接地的箱体，**顶面是带燃烧器灶头 + 锅架的灶台（cooktop）**，箱体前面有控制旋钮 + 一扇烤箱门，箱体底部是踢脚座 / 抽屉 / 灶腿。**核心身份 = 顶部灶头（burner + grate）+ 控制旋钮**；这是 stove 与 built_in_oven 的根本区别（built_in_oven 无灶头、是纯嵌入式热腔箱体）。
>
> **同步状态**：本 spec 引用的 **8 个 5 星样本**（2 个 parent + 6 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5（已逐一核对 `record.json`）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一打开核对，单 revision）。引用以 part / joint / helper **名字**为准（`body` / `oven_door` / `door_{i}` / `cooktop_lid` / `griddle_plate` / `storage_drawer` / `leg_{i}` / `lid` / `knob_{i}` / `grate_{gi}` / `burner_cap_{i}` / `oven_door_hinge` / `cooktop_lid_hinge` / `drawer_slide` / `knob_{i}_dial` / `_build_grate_mesh` / `_build_lid_glass_mesh` / `_build_leg_profile` / `KnobGeometry` / `BezelGeometry` 等），行号仅作定位。
>
> **来源缺口披露（重要）**：source map 声明 `burner_count` 多重性轴有 `rec_variant-burner-count-2-...` / `rec_variant-burner-count-6-...` 两个变体记录，但**这两条记录未同步进 `data/records/`**（已 `ls | grep burner` 确认不存在）。因此 burner_count **不依赖缺失的 burner-count 变体**，而是直接取两个 parent 的 **`for ... BURNER_*` 灶头复制循环 + `for ... KNOB_YS` 旋钮复制循环**（P1 灶头 L180-198 / 旋钮 L299-328；P2 灶头 L301-323 / 旋钮 L477-498）作 copy-logic 源——burner 复制本就是 parent 内置的循环结构，N=2/6 是同一循环的退化 / 扩展，不需要专门变体。这一缺口已在 §3 / §8 / §审核记录显式记录。

## 元信息
| 项 | 值 |
|---|---|
| slug | `stove` |
| template path | `agent/templates/Other_stove.py` |
| test path (optional) | `tests/agent/test_stove_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: `door_mechanism`（主机构）+ `cooktop`（灶面）+ `base`（底座），**外加** `burner_count` 灶头多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 parent + 6 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only。source map 标注的 2 个 burner-count 变体**未同步**，不计入，见顶部缺口披露）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples present in this category（已同步的 8 个）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本；无污染排除（见 §排除 / 污染） |

阅读要点（用于槽位 / 多重性分解）：

- **统一坐标系（两 parent 一致）**：两个 parent 都用 **+X = 灶台前方（朝用户）**、宽度沿 **Y**、Z 向上、接地于 z=0。P1（compact，`ee507c92`）灶台面 ≈0.785 m、P2（stainless，`10691ac9`）灶台面 ≈0.90 m。两者结构家族相同（箱体 + 顶灶台 + 前控制面板 + 前烤箱门），**无需坐标归一**（不像 built_in_oven 的 P1/P2 需要统一），直接以 +X 前向为唯一约定。
- **door_mechanism（主机构槽，真正的 joint 拓扑轴）**：drop_down_front（底铰下翻 **1×REVOLUTE** axis=(0,1,0)，origin 在前底沿；两 parent 基线）/ side_hinged_swing（左竖铰侧开 **1×REVOLUTE** axis=(0,0,-1)，origin 在前左 jamb）/ french_double（法式双门 **2×REVOLUTE** axis=(0,0,∓1) 镜像中线对开）→ joint **数量与轴向**不同，是真正的拓扑变化。
- **cooktop（灶面槽，改顶面 part 树 + 可选 joint）**：open_burners（明火灶头无盖；burner cap + base + 锅架 `grate_{gi}`，**无独立活动件**或锅架 FIXED；两 parent 基线）/ glass_lift_lid（在灶头上加一只 `cooktop_lid` 玻璃掀盖，后铰 **1×REVOLUTE** axis=(0,-1,0) 向上掀起；P1 / P2 的 `lid` 同语义）/ griddle_flat_top（用一整块 `griddle_plate` 平面铁板灶替换灶头 + 锅架，FIXED）→ 灶面是 part 数 / 可选 joint 的拓扑变化。
- **base（底座槽，改底部 part 树 + 可选 joint）**：plinth_kickbase（实心踢脚座 plinth，**无独立件**；两 parent 基线）/ storage_drawer（底部加一只 `storage_drawer` 保温 / 储物抽屉，**1×PRISMATIC** axis=(1,0,0) 向前 +X 拉出）/ raised_legs（用四条 `leg_{i}` 复古撇腿把整机抬离地面，腿是 **body visual / 非移动件**，Rule 1）→ 底座是 part 数 / 可选 joint 的拓扑变化。
- **burner_count（多重性轴，核心）**：顶面灶头数。两 parent 都用循环发射灶头（P1 `for i,(bx,by) in enumerate(BURNER_XY)` 4 头 L180-198；P2 nested `for bx in BURNER_XS: for by in BURNER_YS` 4 头 L301-323），每头 = drip_cup/base + burner_body + `burner_cap_{i}` + 对应锅架；同时前面板 `for i,ky in enumerate(KNOB_YS)` 复制旋钮（P1 6 钮 / P2 5 钮）。burner_count 复制 burner 单元 + 对应 knob → 同构子件 N 次复制，改 part 数与 joint 数（旋钮 REVOLUTE）。
- **非拓扑差异**（不另立 candidate）：灶台高 / 箱体尺寸、控制面板倾角、handle 样式、burner 排布微调、material 配色——只换尺寸 / 装饰 / 颜色，归入连续 scale 或 `palette_style`。

## 核心身份

一只**独立式落地燃气灶 / 灶台**（freestanding gas range / cooktop）：接地的中空 `body`（root，由箱体外壳 + 烤箱腔 + 前控制面板 + 顶部灶台甲板组成），**顶面是灶台**——N 个燃气灶头（`burner_cap` 银盖 + 燃烧器 base + 铸铁 / 钢丝锅架 `grate`），前控制面板上有 N 个**旋钮** `knob`（KnobGeometry，REVOLUTE / 拨转），箱体前面一扇或两扇**烤箱门** `oven_door` / `door_{i}`（带玻璃窗 + 把手），箱体底部是踢脚座 / 储物抽屉 / 复古撇腿。活动语义 = **烤箱门开合**（底铰下翻 REVOLUTE +Y / 侧铰 REVOLUTE -Z / 法式双开 2×REVOLUTE ∓Z）+ **旋钮拨转**（REVOLUTE，绕前法向或面板法向）+ 可选**灶面掀盖**（玻璃盖 REVOLUTE -Y 后掀）+ 可选**储物抽屉**（PRISMATIC +X 拉出）。默认成熟域：door_mechanism × cooktop × base × burner_count∈[1,6] 的独立式燃气灶。

不该混入：
- **built_in_oven / 嵌入式烤箱 / 微波炉（无灶头箱体）**——本类**核心身份是顶部灶头 + 锅架 + 旋钮**；built_in_oven 是无灶头、无锅架的纯嵌入式热腔箱体（前开门 + 滑出烤架）。两类共享"前开门 + 旋钮"但 stove **必有灶头灶台**、built_in_oven **必无灶头**且强调腔内滑出 rack。见 §11 边界。
- **嵌入式 cooktop / 灶台面板（独立台面无烤箱箱体）**——本类是**整机落地灶**（灶台 + 下方烤箱箱体 + 底座），不是嵌入台面的纯灶头模块。
- **洗碗机 / 抽屉柜**——纯 PRISMATIC 箱体，无灶头、无烤箱腔身份。

## 槽位 + 候选模块表

> **建模注记**：三个真正改 part 树 / joint 拓扑的 named slot 是 `door_mechanism`（烤箱门开合）/ `cooktop`（灶面机构）/ `base`（底座机构）。第四根是 `burner_count` **多重性轴**，复制灶头单元 + 对应旋钮，改 part 数与 joint 数，编入 `slot_choices_for_seed` 作拓扑维度（见 §8/§9）。`body`（箱体 + 控制面板 + 烤箱腔）是固定 root，不作独立候选 slot（单一形态，随其他 slot 派生灶台 / 烤箱 mesh）。

### Slot A：door_mechanism（**主机构槽**——烤箱门开合，决定门的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| drop_down_front（基线） | rec_..._ee507c92（P1）/ rec_..._10691ac9（P2）| P1 `oven_door` part+`BezelGeometry`door_frame L248-284 / `oven_door_hinge` REVOLUTE L285-294；P2 door L383-445 / hinge L447-457 | eligible if compatible | 单 `oven_door` child，底铰下翻 **1×REVOLUTE** axis=(0,1,0)，origin=(HALF_D,0,PLINTH_TOP)（前底沿），lower=0 闭合 / upper=π/2 平展前伸 +X；含 `door_hinge_lug_{i}`（P2）captured into lower_front_panel（allow_overlap）|
| side_hinged_swing | rec_variant-door-mechanism-side-hinged-swing-change-_20260618_063803_125635_754e1747 | door part+`BezelGeometry`door_frame L410-493 / `oven_door_hinge` REVOLUTE L495-505；body hinge brackets/cups L343-360 | eligible if compatible | 单 `oven_door` child，左竖铰侧开 **1×REVOLUTE** axis=(0,0,-1)，origin=(DOOR_HINGE_X=0.305, DOOR_HINGE_Y=-0.25, DOOR_CENTER_Z=0.435)，free 边向 +X 摆出；door `door_hinge_pin_{i}` + `hinge_plate` 入 body `door_hinge_cup_{i}`（captured，allow_overlap L610-626）|
| french_double | rec_variant-door-mechanism-french-double-replace-the_20260618_063803_121384_3852f805 | `_build_half_door_frame_mesh` L213-228 / `door_{i}` 循环 L422-490 / 2×REVOLUTE ∓Z L480-490；body `door_hinge_barrel_{i}` L361-366 | eligible if compatible | **两片叶** child（`door_0` 左 hinge_y=-HALF_DOOR_W / `door_1` 右 hinge_y=+HALF_DOOR_W，各覆盖半宽），**2×REVOLUTE** 镜像（axis=(0,0,∓1)），中线对开各自独立开 0..π/2；每叶 `hinge_pin` 入 body `door_hinge_barrel_{i}`（captured，allow_overlap L596-620）|

### Slot B：cooktop（灶面机构——明火灶头 / 玻璃掀盖 / 平面铁板灶）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| open_burners（基线） | rec_..._ee507c92（P1）/ rec_..._10691ac9（P2）| P1 burner 循环 `drip_cup/burner_body/burner_cap_{i}` L180-198 + grate `grate_{gi}` FIXED L200-242；P2 `_build_grate_mesh` L107-159 + burner 循环 L301-323 | eligible if compatible | 明火灶头（无盖）：每头 `burner_cap_{i}` + base，上盖铸铁 / 钢丝**锅架** `grate_{gi}`（P1 锅架 FIXED part L236-242 / P2 `pan_support_{i}` 为 body visual）；灶头数由 burner_count 决定 |
| glass_lift_lid | rec_variant-cooktop-lid-glass-lift-lid-add-a-hinged-_20260618_063803_108536_324b9170 | `cooktop_lid` part（`lid_glass`+`lid_trim_*`+`lid_handle`）L247-309 / `cooktop_lid_hinge` REVOLUTE L311-322 / body `lid_hinge_bracket` L262-267 | eligible if compatible | 在明火灶头**之上**加一只 `cooktop_lid` 玻璃掀盖（玻璃板 + 四边 trim + grip tab），后铰 **1×REVOLUTE** axis=(0,-1,0)，origin=(HINGE_X=-0.296,0,HINGE_Z=0.820)（后 rim 铰线，behind 后排锅架），lower=0 盖住灶头 / upper≈85° 掀起露灶；与烤箱门 REVOLUTE 并存。**保留下方灶头 + burner_count** |
| griddle_flat_top | rec_variant-cooktop-lid-griddle-flat-top-replace-the_20260618_063803_110672_3991e157 | `griddle_plate` part（`griddle_surface` cadquery 平板 + 螺孔）L176-192 / `griddle_mount` FIXED L193-199 | eligible if compatible | 用一整块 `griddle_plate` **平面铁板灶**（teppanyaki 热板，box+fillet+cut 螺孔 mesh）替换明火灶头 + 锅架，**FIXED**（不动）；**无独立灶头 / 无 burner_count**（整面热板，灶头数轴对本候选退化为 N=0，见 §9 兼容矩阵）|

### Slot C：base（底座机构——踢脚座 / 储物抽屉 / 复古撇腿）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| plinth_kickbase（基线） | rec_..._ee507c92（P1）/ rec_..._10691ac9（P2）| P1 `plinth` body visual + 四 `foot_{i}` L67-81；P2 `plinth` L229-234 | eligible if compatible | 实心踢脚座 `plinth`（box，body visual，闭合烤箱腔底）+ 可选短脚 `foot_{i}`，**无独立活动件**（Rule 1） |
| storage_drawer | rec_variant-base-storage-storage-drawer-replace-the-_20260618_063803_119100_ed3ce770 | `storage_drawer` part（`drawer_front`+`drawer_bottom`/`drawer_side_{}`/`drawer_back`+`drawer_handle_bar`）L272-327 / `drawer_slide` PRISMATIC L330-338 | eligible if compatible | 底部加一只 `storage_drawer` 保温 / 储物抽屉（前面板 + 托盘箱 + 把手），**1×PRISMATIC** axis=(1,0,0) 向前 +X 拉出，origin=(HALF_D,0,DRAWER_CZ)，lower=0 收起 / upper=0.30 拉出；与烤箱门 REVOLUTE 并存。烤箱腔底抬高让出抽屉空间 |
| raised_legs | rec_variant-base-storage-raised-legs-lift-the-whole-_20260618_064727_806978_263d7de1 | `_build_leg_profile` L64-78 / `LatheGeometry` leg_geom + 四 `leg_{i}` body visual 循环 L106-118（`LEG_CORNERS` L56-62） | eligible if compatible | 四条 `leg_{i}` 复古撇腿（LatheGeometry 车削 chrome 腿 mesh，按 ±LEG_SPLAY 撇开）把整机抬离地面 LEG_H=0.14 m；腿是 **body visual / 非移动件**（Rule 1，FIXED 到 root body），改的是 part 数 + 整机离地高（body bottom 上移） |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: `door_mechanism` + `cooktop` + `base` 各自挂到共同 root `body`（parallel children），外加 `burner_count` 在 `body` 顶面灶台 N 次复制灶头单元 + 前面板对应旋钮）

```
body (root, 坐地 z=0; outer shell + 烤箱腔 liner/rail + 前控制面板 + 顶部灶台甲板;
      cooktop/base slot 决定灶台与底部 mesh)
  │
  ├── [door_mechanism slot]  (互斥三选一)
  │     ├─ drop_down_front  : oven_door ──[oven_door_hinge: REVOLUTE axis=+Y, origin=(HALF_D,0,前底沿)]
  │     ├─ side_hinged_swing: oven_door ──[oven_door_hinge: REVOLUTE axis=-Z, origin=(前面,-0.25,Z_MID)]
  │     └─ french_double    : door_0 ──[door_0_hinge: REVOLUTE axis=-Z, origin=(前面,-HALF_DOOR_W,Z_MID)]
  │                           door_1 ──[door_1_hinge: REVOLUTE axis=+Z, origin=(前面,+HALF_DOOR_W,Z_MID)]
  │
  ├── [cooktop slot]  (三选一)
  │     ├─ open_burners   : (灶头 burner_cap_{i}/base = body visual; 锅架 grate_{gi}; 无盖) + burner_count 生效
  │     ├─ glass_lift_lid : cooktop_lid ──[cooktop_lid_hinge: REVOLUTE axis=-Y, origin=(后 rim,0,HINGE_Z)] + 下方灶头 + burner_count 生效
  │     └─ griddle_flat_top: griddle_plate ──[griddle_mount: FIXED] (整面热板; burner_count 退化 N=0)
  │
  ├── [base slot]  (三选一)
  │     ├─ plinth_kickbase: (plinth + foot_{i} = body visual; 无 joint)
  │     ├─ storage_drawer : storage_drawer ──[drawer_slide: PRISMATIC axis=+X, origin=(HALF_D,0,DRAWER_CZ)]
  │     └─ raised_legs    : (leg_{i} = body visual, 抬高整机; 无独立 joint)
  │
  └── [burner_count multiplicity 轴]  burner unit i∈range(Nb) + 对应 knob_{i}
        灶头单元 burner_cap_{i}/burner_body_{i}/(drip_cup_{i}) + grate（锅架按灶头分组）;
        旋钮 knob_{i} ──[knob_{i}_dial / knob_{i}_turn: REVOLUTE 绕面板/前法向]
        placement: 灶头沿灶台 XY 网格、旋钮沿 Y 等距并排;
        cooktop=griddle_flat_top → Nb 退化为 0（整面热板无灶头），但旋钮仍可保留（控烤箱/铁板温度，见 §9）
```

接口点位与 joint 语义：
- **door_mechanism 接口（互斥）**：所有门机构挂在 `body` 前面腔口铰线硬件上。
  - drop_down_front：前底沿铰线，REVOLUTE axis=(0,1,0)，origin=(HALF_D,0,PLINTH_TOP / DOOR_HINGE_Z)；P2 `door_hinge_lug_{i}` captured into `lower_front_panel`（allow_overlap）。q=0 竖直闭合 / q=π/2 平展前伸 +X。
  - side_hinged_swing：左竖铰，REVOLUTE axis=(0,0,-1)，origin=(DOOR_HINGE_X,DOOR_HINGE_Y=-0.25,DOOR_CENTER_Z)；door `door_hinge_pin_{i}`+`hinge_plate` 入 body `door_hinge_cup_{i}`（allow_overlap）。q=0 闭合 / q=π/2 free 边摆向 +X。
  - french_double：左 / 右竖铰各一，REVOLUTE axis=(0,0,∓1)（origin 左 / 右 jamb ∓HALF_DOOR_W），两叶中线对接、各自独立 0..π/2 开；每叶 `hinge_pin` 入 body `door_hinge_barrel_{i}`（allow_overlap）。
- **cooktop 接口（三选一）**：
  - open_burners：灶头 / 锅架坐灶台甲板（`expect_gap` 锅架 rest on rim、`expect_overlap` 锅架 over cooktop）；锅架 P1 为 FIXED part、P2 为 body visual（无独立活动）。burner_count 生效。
  - glass_lift_lid：后 rim 铰线 `lid_hinge_bracket`（body）↔ `cooktop_lid`，REVOLUTE -Y，origin=(HINGE_X,0,HINGE_Z)，q=0 盖住灶头（`expect_overlap` 盖覆盖灶台 footprint）、q≈85° 掀起；保留下方灶头 + burner_count。
  - griddle_flat_top：`griddle_plate` FIXED 坐灶台凹槽（`expect_contact` 坐底）；替换灶头 → burner_count 退化 N=0（无灶头单元）。
- **base 接口（三选一）**：
  - plinth_kickbase：无 joint（plinth/foot 为 body visual，闭合烤箱腔底，坐地）。
  - storage_drawer：底部抽屉腔 ↔ `storage_drawer`，PRISMATIC +X，origin=(HALF_D,0,DRAWER_CZ)，q=0 收起 / 拉出 0.30；抽屉侧 captured into 底部导轨（allow_overlap，照搬样本 run_tests）。
  - raised_legs：`leg_{i}` 为 body visual（非移动，Rule 1），整机 body bottom 上移 LEG_H；腿底坐地。
- **burner_count 接口**：灶头单元（cap+base+drip）为承载在 body 顶面甲板上的 visual / FIXED 锅架，knob 为前面板 REVOLUTE 活动件；灶头沿灶台 XY 网格绝对式分布，旋钮沿 Y 绝对式等距并排。
- **mating policy**：所有 hinge 是 pin/lug-in-cup/barrel captured-pin、抽屉是 rail captured-slide、knob 是 cap-on-panel captured、灶头 / 锅架 / 腿是坐落 contact —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有门 / 叶 q=0 闭合（lower=0），cooktop_lid q=0 盖住，storage_drawer q=0 收起，knob q=0。
- **互斥 / 可选 / 派生**：door_mechanism 三候选互斥（一次只一种门机构）；cooktop 三候选互斥；base 三候选互斥；plinth_kickbase / open_burners 是空 / 基线机构；griddle_flat_top 取消灶头 → burner_count 派生为 0（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot root / body（固定 root；cooktop / base 决定灶台与底部 mesh）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: 外壳 `side_wall_*`/`back_wall`/`top_housing`/`cooktop_deck` + 烤箱腔 `liner_*`/`cavity_floor`/`cavity_ceiling`/`*_rack_rail_{i}` + 前控制面板 `control_panel` + 灶台 rim）| P1 L64-177 / P2 `body` L226-349 |
| internal joints | 无（body 是 root）；P2 含一只 FIXED `lower_rack`（烤箱内固定下架）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | 前面腔口铰线硬件（供 door_mechanism）+ 顶部灶台甲板 / rim（供 cooktop）+ 底部腔 / 地面（供 base）+ 前控制面板（供 knob）| P1 L113-137 / P2 L325-360 |

### Slot A / door_mechanism — drop_down_front
| emits | 描述 | 来源 |
|---|---|---|
| parts | `oven_door`（visual: `BezelGeometry` door_frame + `window_glass`/`door_glass` + `handle_bar`/`door_handle` + `handle_standoff_{i}` + P2 `door_hinge_lug_{i}`）| P1 L248-284 / P2 L383-445 |
| internal joints | `oven_door_hinge` REVOLUTE axis=(0,1,0)，origin=(HALF_D,0,PLINTH_TOP/DOOR_HINGE_Z)，lower=0 / upper=π/2 | P1 L285-294 / P2 L447-457 |
| upstream interface | door 底沿坐前面腔口；P2 `door_hinge_lug_{i}` captured into `lower_front_panel`（allow_overlap）| P2 run_tests L564-568 |

### Slot A / door_mechanism — side_hinged_swing
| emits | 描述 | 来源 |
|---|---|---|
| parts | `oven_door`（door-local origin 在左竖铰线；`door_frame`+`door_glass`+`glass_retainer_{i}`+`hinge_plate`+`door_hinge_pin_{i}`+竖把手 `door_handle`/`handle_standoff_{i}`）| L410-493 |
| internal joints | `oven_door_hinge` REVOLUTE axis=(0,0,-1)，origin=(DOOR_HINGE_X,DOOR_HINGE_Y=-0.25,DOOR_CENTER_Z=0.435)，lower=0 / upper=π/2 | L495-505 |
| upstream interface | `door_hinge_pin_{i}`+`hinge_plate` 入 body `door_hinge_cup_{i}`（左 jamb captured，allow_overlap）| run_tests L610-626 |

### Slot A / door_mechanism — french_double
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0`（左，local origin 左竖铰）+ `door_1`（右，local origin 右竖铰）各 `door_frame`(half)+`door_glass`+近中线竖把手 `door_handle`/`handle_standoff_{j}`+`hinge_pin` | `_build_half_door_frame_mesh` L213-228 / 循环 L422-490 |
| internal joints | `door_0_hinge` REVOLUTE axis=(0,0,-1) origin=(DOOR_HINGE_X,-HALF_DOOR_W,DOOR_CENTER_Z) + `door_1_hinge` REVOLUTE axis=(0,0,1) origin=(DOOR_HINGE_X,+HALF_DOOR_W,..)，各 lower=0/upper=π/2 | L480-490 |
| upstream interface | 两叶 free 边中线对接；每叶 `hinge_pin` 入 body `door_hinge_barrel_{i}`（双组 captured，allow_overlap）| run_tests L596-620 |

### Slot B / cooktop — open_burners
| emits | 描述 | 来源 |
|---|---|---|
| parts | 灶头 `drip_cup_{i}`/`burner_body_{i}`/`burner_cap_{i}`（P1 body visual）/ `burner_base_{idx}`/`burner_cap_{idx}`/`pan_support_{idx}`（P2 body visual）+ 锅架 `grate_{gi}`（P1 FIXED part）| P1 L180-242 / P2 L298-323 |
| internal joints | 无活动（P1 锅架 `grate_{gi}_mount` FIXED；P2 锅架为 body visual）| P1 L236-242 |
| upstream interface | 灶头 / 锅架坐灶台甲板（`expect_gap` 锅架 rest on rim / `expect_overlap` over cooktop）| P1 run_tests L448-482 |

### Slot B / cooktop — glass_lift_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cooktop_lid`（`lid_glass` + `lid_trim_front/rear/left/right` + `lid_handle` grip tab）；body 上加 `lid_hinge_bracket` | L247-309 |
| internal joints | `cooktop_lid_hinge` REVOLUTE axis=(0,-1,0)，origin=(HINGE_X=-0.296,0,HINGE_Z=0.820)，lower=0 / upper≈radians(85°) | L311-322 |
| upstream interface | 后 rim `lid_hinge_bracket`（body）↔ lid 玻璃板后缘（captured 铰线）；q=0 盖覆盖灶台 footprint（`expect_overlap`）| run_tests L592-650 |

### Slot B / cooktop — griddle_flat_top
| emits | 描述 | 来源 |
|---|---|---|
| parts | `griddle_plate`（`griddle_surface` cadquery 平板 box+fillet+螺孔 mesh，替换灶头 + 锅架）| L176-192 |
| internal joints | `griddle_mount` FIXED（整面热板不动）| L193-199 |
| upstream interface | griddle 坐灶台凹槽（`expect_contact` 坐底，`part_world_aabb` 大平板）| run_tests L384-410 |

### Slot C / base — plinth_kickbase
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plinth`（box，闭合烤箱腔底）+ 可选 `foot_{i}`（P1 四短脚）；均 body visual | P1 L67-81 / P2 L229-234 |
| internal joints | 无 | — |
| upstream interface | 坐地 z=0（`plinth` 底面接地）| — |

### Slot C / base — storage_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `storage_drawer`（`drawer_front` + `drawer_bottom`/`drawer_side_{}`/`drawer_back` 托盘 + `drawer_handle_bar`/`drawer_handle_standoff_{i}`）；body 底部抬高烤箱腔让出抽屉腔 + 下面板 | L272-327 |
| internal joints | `drawer_slide` PRISMATIC axis=(1,0,0)，origin=(HALF_D,0,DRAWER_CZ)，lower=0 / upper=0.30 | L330-338 |
| upstream interface | 抽屉侧 captured into 底部抽屉腔导轨（allow_overlap）；`expect_overlap` 拉出后保留 retained insertion | run_tests（drawer slide 段）|

### Slot C / base — raised_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 四 `leg_{i}`（LatheGeometry 车削 chrome 撇腿 mesh，按 ±LEG_SPLAY 撇开）；body visual | `_build_leg_profile` L64-78 / `LEG_CORNERS` L56-62 / 循环 L106-118 |
| joints | 无（Rule 1，腿非移动件 inline 为 body visual，FIXED 几何）| — |
| placement | `for i,(lx,ly) in enumerate(LEG_CORNERS)`，四角各一，rpy 按 ∓LEG_SPLAY 撇开；整机 body bottom 上移 LEG_H=0.14 | L106-118 |

### burner_count multiplicity（灶头 + 旋钮复制；改 part+joint 拓扑）
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-burner 复制 `burner_cap_{i}`/`burner_body_{i}`/(`drip_cup_{i}`)（灶头单元）+ 对应锅架 + 前面板 `knob_{i}`（KnobGeometry cap）| P1 burner L180-198 + knob L299-328 / P2 burner L301-323 + knob L477-498 |
| joints | 每钮 `knob_{i}_dial`（P1）/ `knob_{i}_turn`（P2）REVOLUTE，axis=前法向 / 面板法向，origin 在控制面板前面；灶头本身无独立 joint（Rule 1，body visual）| P1 L318-328 / P2 L485-498 |
| placement | 灶头沿灶台 XY **绝对式**网格分布（P1 `BURNER_XY` 2×2 / P2 `BURNER_XS`×`BURNER_YS`）；旋钮沿 Y **绝对式**等距并排（`KNOB_YS` 以中心对称解析）| P1 L43-46 / P2 L61-65 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_mechanism | enum | drop_down_front / side_hinged_swing / french_double | drop_down_front | choice | 由 deterministic procedural sampler 选；主机构（互斥）| module table |
| cooktop | enum | open_burners / glass_lift_lid / griddle_flat_top | open_burners | choice | sampler 选；灶面（互斥）；griddle 派生 burner_count→0 | module table |
| base | enum | plinth_kickbase / storage_drawer / raised_legs | plinth_kickbase | choice | sampler 选；底座（互斥）| module table |
| burner_count (Nb) | int | 声明域 [1,6]；sweep 采样域 [1,6]（偏小加权：2/4 高频、1/6 较少、奇数稀疏）| 4 | conditional→slot_choice | 编入 slot_choice 为 `("burner_count", f"b{Nb}")`（拓扑维度）；灶头沿灶台网格 + 对应旋钮；**Nb 与 cooktop 联动**：griddle_flat_top→Nb=0；Nb 受灶台面积 clamp（见不等式 + §8）| P1/P2 burner+knob 循环 |
| palette_style | enum | white_enamel / brushed_stainless / matte_black_steel / cream_retro / glossy_red | white_enamel | palette | palette only，**不计入 slot_choice**；5 配色（见 §palette）| 各样本材质 |
| cooktop_width_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放灶台 / 箱体 Y 宽（保比例），clamp；影响 burner 网格列数与 knob 沿 Y 可用排距 | resolve clamp |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放箱体高 → 烤箱腔净高 / 灶台面 Z / 控制面板高，clamp | resolve clamp |
| body_depth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放箱体深 BODY_D（X）→ 烤箱门高 / 抽屉行程上限 / 灶台进深，clamp | resolve clamp |
| door_open_angle_scale | float | [0.88, 1.05] | 1.0 | independent | 缩放门 / 叶 REVOLUTE `upper`，clamp（保 ≤π/2·1.0）| resolve clamp |
| lid_open_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 cooktop=glass_lift_lid 有效；缩放掀盖 REVOLUTE `upper`（≤ 暴露灶头所需，保 ≤π·0.95）| resolve clamp |
| drawer_travel_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 base=storage_drawer 有效；缩放 PRISMATIC `upper`（≤ 抽屉深 − retained insertion）| resolve clamp |
| burner_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 Nb≥2 有效；缩放灶头网格间距与对应旋钮并排间距 | resolve clamp |
| (—) | constraint | — | — | inequality | **灶头不超灶台**：`burner 网格 footprint（按 Nb 行列）+ margin ≤ cooktop_deck XY·cooktop_width_scale/body_depth_scale`；违反则减 Nb 或缩 burner_spacing | 接口 / clearance |
| (—) | constraint | — | — | inequality | **旋钮不超面板宽**：`Nk·KNOB_D + (Nk-1)·gap·burner_spacing_scale ≤ control_panel 宽·cooktop_width_scale − 2·margin`（Nk 旋钮数随 Nb 派生，见 §8）| 接口 / clearance |
| (—) | constraint | — | — | inequality | **抽屉行程 ≤ 抽屉深**：`DRAWER_TRAVEL·drawer_travel_scale ≤ 抽屉腔深·body_depth_scale − 0.04`（保 retained insertion ≥0.04）| 接口 / clearance |
| (—) | constraint | — | — | conditional | **掀盖闭合覆盖灶头**：cooktop=glass_lift_lid 时 lid 闭合 XY 覆盖灶台 footprint ≥0.20 | 接口 / closed pose |
| (—) | constraint | — | — | conditional | **griddle → Nb=0**：cooktop=griddle_flat_top 时不发射灶头 / 锅架（整面热板），burner_count 派生为 0；旋钮可保留为烤箱 / 铁板控（见 §9）| 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 door_mechanism / cooktop / base / Nb 的拓扑**。

### palette_style 配色（≥3，目标 4-6；从 5 星源材质提取，每 seed 采样一种）

| palette_style | 箱体 / 灶台 | 烤箱门 frame | 控制面板 / 旋钮 | 灶头 / 锅架 | 来源 |
|---|---|---|---|---|---|
| white_enamel（基线） | enamel_white (0.93,0.93,0.91) | enamel_white frame + glass_tint 窗 | knob_white (0.96,0.96,0.95) | cap_silver (0.82,0.83,0.84) / iron_black 锅架 | P1（compact）L52-61 |
| brushed_stainless | stainless_steel (0.72,0.73,0.75) + brushed_panel | matte_black frame + door_glass | knob_black (0.11,0.11,0.12) + brushed 面板 | burner_silver (0.80,0.81,0.82) / chrome_wire 锅架 | P2（stainless）L212-221 |
| matte_black_steel | matte black (0.13,0.13,0.14) | gloss black frame + dark glass | dark knobs + 银 accents | brushed alloy cap / black 锅架 | 合成（黑钢灶常见，从 matte_black/dark_steel 系派生）|
| cream_retro | cream enamel (0.92,0.90,0.85) | cream frame + chrome trim | chrome bezel knobs | chrome cap / black cast-iron 锅架 | 合成（复古奶白珐琅灶，从 enamel_white/leg_chrome 系派生）|
| glossy_red | gloss red enamel (0.62,0.10,0.10) | black frame + glass | chrome / black knobs | cap_silver / iron_black 锅架 | 合成（复古红珐琅灶，珐琅同工艺换色）|

> palette_style 是**纯材质映射**，不改任何 part/joint/尺寸/拓扑；5 配色覆盖白珐琅 / 不锈钢 / 黑钢 / 奶白复古 / 红珐琅，前两者直接取自 5 星源（P1/P2），后三者为同工艺合成现实配色。每 seed `rng.choice` 一种，写进 palette 不写进 slot_choice。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（灶头数；旋钮数从灶头数派生，不单独成轴）：

### 轴：burner_count（灶台灶头数 + 派生旋钮数）
- **count_param**：`burner_count`（模板变量 Nb / N_BURNERS）。旋钮数 Nk **派生**于 Nb（`Nk = Nb` 或 `Nb + 烤箱旋钮常量`，实现按 parent：每灶头一钮，烤箱温控钮可固定 +0/+1；spec 默认 `Nk = Nb`，旋钮与灶头一一对应，源自两 parent 每灶头一钮的语义）。**旋钮不单独成多重性轴**（与灶头联动派生）。
- **N_range**：声明产品域 **[1,6]**（独立式灶现实灶头数：1 单头 / 2 / 4 标准 / 5 / 6 专业双排；source map 建议 [1,6]）。`config_from_seed` sweep 采样域 **[1,6]**（偏小加权：2/4 高频、1/6 较少、奇数 3/5 稀疏）。Nb=1 即单头灶（不进多头网格循环，等价 range(1)）。
- **sampling domain**：`rng.choices((1,2,3,4,5,6), weights=(0.08,0.27,0.10,0.32,0.08,0.15))`（2/4 主流、6 专业灶尾部）；`resolve_config` 把任意外部 Nb clamp 到 [1,6]，按「灶头不超灶台」不等式回缩；**cooktop=griddle_flat_top 时强制 Nb=0**（整面热板，旋钮可保留控温）。
- **copied object**：单灶头单元——`burner_cap_{i}`+`burner_body_{i}`(+`drip_cup_{i}`)（P1 风格）/ `burner_base_{idx}`+`burner_cap_{idx}`+`pan_support_{idx}`（P2 风格，含锅架），共享 burner mesh helper（`Cylinder` / `_build_grate_mesh`）；+ 派生旋钮 `knob_{i}`（共享 `KnobGeometry` / `knob_mesh` 复用同一对象）。
- **naming**：`burner_cap_{i}` / `burner_body_{i}` / `drip_cup_{i}`（灶头）+ `knob_{i}` / `knob_{i}_dial`(P1)/`knob_{i}_turn`(P2)（旋钮），`for i in range(Nb)`（P1 `for i,(bx,by) in enumerate(BURNER_XY)` L180 / P2 nested loop L301-302 / knob `for i,ky in enumerate(KNOB_YS)` L299/L477 已用此结构，直接作源）。
- **placement**：灶头沿灶台 **XY 绝对式网格**分布（Nb≤2 单排沿 Y、Nb=3/4 双排 2×2、Nb=5/6 双排 2×3 / 3×2，由 Nb 解析网格行列、以灶台中心对称）；旋钮沿 **Y 绝对式**等距并排（以控制面板中心对称分布，间距随 burner_spacing_scale）。绝对式（每个 i 的位置由 Nb 与中心解析，不累加漂移）是 N-不变前提。
- **joint policy**：灶头是**非移动件**（Rule 1）→ body visual / FIXED 锅架，**不发射独立 joint**；派生旋钮每钮各独立 **REVOLUTE**（绕面板 / 前法向，0..270°）；活动关节由 door_mechanism / cooktop_lid / drawer 提供。
- **source/gating**：copy-logic 源取两 parent 的 burner 循环（P1 L180-198 / P2 L301-323）+ knob 循环（P1 L299-328 / P2 L477-498）；**source map 标注的 burner-count-2 / burner-count-6 变体未同步**（见顶部缺口披露），因此 N=2/6 由同一 parent 循环的退化 / 扩展实现，**不依赖缺失记录**。Nb 与 cooktop 的兼容（griddle→Nb=0）见 §9 矩阵。

## 拓扑多样性审计

总组合数：door_mechanism(3) × cooktop(3) × base(3) × burner_count 采样数(7，即 {0,1,2,3,4,5,6}，含 griddle 的 Nb=0) = **3 × 3 × 3 × 7 = 189**。
（含 1×REVOLUTE 下翻 / 1×REVOLUTE 侧铰 / 2×REVOLUTE 法式门 × 无盖 / REVOLUTE 掀盖 / FIXED 铁板灶 × 无 / PRISMATIC 抽屉 / 抬腿 × Nb 灶头 + 派生 Nk 旋钮 REVOLUTE 的 joint 数 / 类拓扑差异）

仅 door_mechanism(3) × cooktop(3) × base(3) = **27**（已远超门控）；叠 burner_count(7) → 189。

理由：三个 named slot 各提供真正的 joint 拓扑差异（门 1/1/2 REVOLUTE × 灶面 无盖/REVOLUTE盖/FIXED板 × 底座 无/PRISMATIC抽屉/抬腿），burner_count 改 part 数与 joint 数（多灶头 + 多旋钮 REVOLUTE）。**door_mechanism / cooktop / base / Nb 必须各自编入 `slot_choices_for_seed`**（`("door_mechanism",..)` / `("cooktop",..)` / `("base",..)` / `("burner_count",f"b{Nb}")`，对齐 cushion/built_in_oven/shopping_bucket/fence_cascade），否则同机构不同 N 在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（door_mechanism / cooktop / base），经兼容矩阵合法化（cooktop=griddle → Nb 派生 0），再 `rng.choices` 加权 Nb∈[1,6]（griddle 时 Nb=0），再 uniform 各连续 scale。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：189 组合的采样空间下，1000-seed slot choice tuple distinct 预计接近组合上限（189，受真实结构词汇表约束，**超过建议的 ≥300**）。本小类多重性中等（一根灶头 N 轴 + 三个三选一 named slot），拓扑空间充裕（189 distinct），连续 scale 与 5 配色再细分外观而非新拓扑。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 cooktop_width_scale / body_height_scale / body_depth_scale / door_open_angle_scale（independent）+ lid_open_angle_scale（conditional@glass_lift_lid）/ drawer_travel_scale（conditional@storage_drawer）/ burner_spacing_scale（conditional@Nb≥2）。全部 `resolve_config` clamp。采样契约：先采三 named slot + Nb（解析 conditional：griddle→Nb=0、lid_open 仅 glass_lift_lid、drawer_travel 仅 storage_drawer、burner_spacing 仅 Nb≥2）→ 采 independent width/height/depth/angle scale → 派生（烤箱腔高随 body_height、灶台面随高、Nk 随 Nb）→ 用四条 clearance inequality（灶头不超灶台、旋钮不超面板宽、抽屉行程不超深、掀盖闭合覆盖灶头）投影 / 回缩。跨部件依赖（灶头网格 vs 灶台面积、旋钮排布 vs 面板宽、行程 vs 抽屉深、掀盖覆盖 vs 灶台 footprint）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 hinge/rail/cap origin、captured-pin/lug/slide 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），再 `rng.choices` 加权 Nb∈[1,6]（griddle→0），再 uniform 各 scale | slot_choices_for_seed 含 `("door_mechanism",..)`/`("cooktop",..)`/`("base",..)`/`("burner_count",f"b{Nb}")` 且与 build 一致 |
| compatibility matrix | (1) **cooktop=griddle_flat_top × burner_count**：整面铁板灶无明火灶头 → 强制 **Nb 派生为 0**（不发射灶头 / 锅架）；旋钮可保留固定数（烤箱 + 铁板温控，默认 2）或随实现降级。 (2) **cooktop=glass_lift_lid × burner_count**：掀盖盖在灶头之上 → 灶头保留 Nb∈[1,6]，掀盖闭合 footprint 必须覆盖全部灶头（§7 conditional）；掀盖与烤箱门 REVOLUTE 正交共存。 (3) **base=storage_drawer × door_mechanism**：抽屉在烤箱腔下方 → 烤箱腔底抬高让出抽屉空间，烤箱门高随之减小（door_frame 高 clamp）；抽屉 PRISMATIC +X 与门 REVOLUTE 正交共存。 (4) **base=raised_legs × door_mechanism**：抬腿把整机上移 LEG_H，烤箱门 / 灶台 / 抽屉 origin 整体 +Z 平移；腿非移动件，与任意门 / 灶面正交。 (5) **door_mechanism × cooktop × base 三轴正交**（除 griddle→Nb=0 派生外，任意组合合法）。 (6) **至少 1 门保 ≥1 非 fixed joint**（door_mechanism 必发一只 REVOLUTE 门 / 双叶）。 | 无 floating / collision / 灶头超灶台 / 旋钮超面板宽 / 抽屉超深 / 掀盖不覆盖灶头 / 门不覆盖腔口 / 抬腿不接地 |
| controlled local variation | 7 个 clamped scale（cooktop_width/body_height/body_depth/door_open_angle independent + lid_open_angle@glass_lift_lid / drawer_travel@storage_drawer / burner_spacing@Nb≥2 conditional），每 build 统一 | 比例变化不破坏 hinge/rail/cap origin、captured 接口、门覆盖、掀盖覆盖、灶头坐台、抽屉 retained insertion、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 / 逐轴 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| door_mechanism | 3 | yes | yes | 1 REVOLUTE 下翻 / 1 REVOLUTE 侧铰 / 2 REVOLUTE 法式（互斥主机构）|
| cooktop | 3 | yes | yes | 无盖灶头 / REVOLUTE 掀盖 / FIXED 铁板灶（互斥）|
| base | 3 | yes | yes | 踢脚座（无 joint）/ PRISMATIC 抽屉 / 抬腿（无 joint）|
| burner_count (Nb) | 7（采样域 {0,1,2,3,4,5,6}，含 griddle 的 0）| yes | yes | 多重性轴，编入 slot_choice；旋钮数 Nk 派生 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("door_mechanism",..)` / `("cooktop",..)` / `("base",..)` / `("burner_count",f"b{Nb}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，Nb⊆[0,6]（griddle→0，否则 [1,6]）
- `resolve_config` clamp Nb 到声明域、各 scale clamp 到声明范围；lid_open_angle / drawer_travel / burner_spacing 为 conditional 随 cooktop / base / Nb 解析；cooktop=griddle 强制 Nb=0；四条 clearance inequality（灶头不超灶台、旋钮不超面板宽、抽屉行程不超深、掀盖覆盖灶头）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（griddle×Nb 派生 0；抽屉抬高烤箱腔；门必覆盖腔口；掀盖必覆盖灶头；至少 1 门保 ≥1 非 fixed joint）
- 连续 scale clamp 后不破坏 hinge/rail/cap origin / captured-pin/lug/slide 接口 / 门覆盖 / 掀盖覆盖 / 灶头坐台 / 抽屉 retained insertion / N 复制
- 关键 joint：drop_down `oven_door_hinge` REVOLUTE axis≈(0,1,0)；side_hinged `oven_door_hinge` REVOLUTE axis≈(0,0,-1)；french `door_0/1_hinge` 2×REVOLUTE 镜像 ∓Z/±Z；glass_lift_lid `cooktop_lid_hinge` REVOLUTE axis≈(0,-1,0)；storage_drawer `drawer_slide` PRISMATIC axis≈(1,0,0) upper≈0.30；knob `knob_{i}_dial/turn` REVOLUTE 0..270° 绕面板 / 前法向
- captured-pin / lug / slide / cap：element-scoped `allow_overlap`（side_hinged `door_hinge_pin_{i}`/`hinge_plate`↔`door_hinge_cup_{i}`；french `hinge_pin`↔`door_hinge_barrel_{i}`；drop_down(P2) `door_hinge_lug_{i}`↔`lower_front_panel`；lid `hinge_leaf_{i}`↔`lid_hinge_barrel_{i}`(P2 lid) / lid 后缘↔`lid_hinge_bracket`；drawer 侧↔导轨；knob `knob_shell`/`knob_cap`↔`control_panel`），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `burner_cap_{i}` / `knob_{i}` 命名 + 绝对式灶台网格 / Y 等距 placement + Rule 1（灶头 / 锅架 / 腿无独立 joint，旋钮各独立 REVOLUTE）
- grandfather：所有 hinge/lug/slide/cap captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 Nb 当普通 int 参数、不进 slot_choice → 同机构不同灶头数 slot_choice 同形，损失一整根拓扑维度（违反 §8/§9 硬要求）。
- cooktop=griddle_flat_top 仍发射明火灶头 → 整面铁板灶上不该有 burner cap；必须 gate（griddle→Nb=0）。
- 丢失灶头 / 锅架 / 旋钮把 stove 退化成 built_in_oven（无顶灶台）→ 出类；stove 必有顶部灶台（open_burners/glass_lift_lid 必含灶头、griddle 必含铁板）+ 控制旋钮。
- 把灶头 / 锅架 / 撇腿当独立活动 part 加 joint → 违反 Rule 1（非移动件，应 inline 为 body visual / FIXED）。
- 把门 / 叶 / 掀盖 / 抽屉 rest pose 设成张开 / 拉出而非 q=0 闭合收起 → current-pose 与 viewer 目检不符（所有样本闭合 lower=0）。
- hinge/rail/cap origin 放在箱体中心或任意点而非真实铰线 / 导轨 / 面板 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured `door_hinge_pin`/`hinge_plate`/`drawer` 侧 / `knob_cap` 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 掀盖闭合不覆盖全部灶头 / 烤箱门不覆盖腔口 → §7 conditional FAIL；须扩大 lid/door footprint 或减 burner_spacing。
- 灶头网格 / 旋钮排距过大超出灶台 / 面板宽 → §7 不等式 FAIL；须按比例缩间距或减 Nb。
- 把连续尺寸 / 颜色 / 材质（palette_style / width scale）当新 candidate 塞进 named slot → 不是结构差异。

## 与相邻类别的边界

- 不该混入：**built_in_oven / 嵌入式烤箱 / 微波炉**——本类**核心身份是顶部灶头（burner + grate）+ 控制旋钮**；built_in_oven 是**无灶头**的纯嵌入式热腔箱体（前开门 + 滑出 rack 烤架）。两类共享"前开门 + 旋钮"，但 stove 必有顶灶台、built_in_oven 必无灶头且强调腔内滑出烤架；已有独立模板 `built_in_oven`（spec 已在 `specs_modular_v1/Other_Built_in_oven.md` 明确把"落地灶 stove"列为不混入项，双向对齐）。
- 不该混入：**嵌入式 cooktop / 纯灶台面板**——本类是整机落地灶（灶台 + 下方烤箱箱体 + 底座），不是嵌入台面的纯灶头模块（无烤箱腔 / 无底座）。
- 不该混入：**洗碗机 / 抽屉柜 / 普通橱柜**——纯 PRISMATIC / 对开门箱体，无灶头、无烤箱腔、无控制旋钮身份。

## 排除 / 污染记录

- **无 5 星样本被排除为污染**：已同步的 8 个样本（2 parent + 6 变体）逐一打开核对，均为 genuine freestanding gas range/cooktop（顶灶台 + 前烤箱门 + 旋钮），无 built_in_oven 误入。
- **同名片段消歧**：`data/records/` 内另有 `rec_variant-door-mechanism-side-hinge-single-...e2a585a2` 与 `rec_variant-door-mechanism-french-double-door-...4f000702`（**built_in_oven 的门变体**，不同 timestamp/hash），**未被本 spec 引用**——stove 只引用 source map 明确命名的 `...side-hinged-swing-...754e1747` 与 `...french-double-replace-...3852f805`（已逐一核对 record id 一致）。
- **source map 声明但未同步的记录（缺口）**：`rec_variant-burner-count-2-...` / `rec_variant-burner-count-6-...` 在 `data/records/` 中**不存在**（已 grep 确认）。burner_count 轴改以两 parent 的 burner+knob 复制循环为 copy-logic 源，不依赖缺失记录（见顶部缺口披露 + §8 source/gating）。这是已知的来源覆盖局限，待审核确认是否需补同步这两条记录以加强 N=2/6 的回归证据。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **5 星样本数为 8 而非 source map 暗示的 10**——burner-count-2/6 两条变体未同步，burner_count 轴改用 parent 循环为源（≥5 门槛已过，8 个 genuine 源），是否接受 / 是否需补同步那两条记录；(2) burner_count N_range [1,6]（含 griddle 派生 0）是否合理，旋钮数 Nk=Nb 派生（不单独成轴）是否接受；(3) cooktop=griddle → Nb=0 的派生 gate、旋钮是否保留控温是否接受；(4) 坐标系无需归一（两 parent 同 +X 前向）是否确认；(5) palette_style 5 配色（white_enamel/brushed_stainless 取自源 + matte_black_steel/cream_retro/glossy_red 合成）是否够现实；(6) 与 built_in_oven 的边界（stove 必有顶灶头）是否双向对齐）|

## 模板实现备注（可选）

- 共享 helper：`_build_grate_mesh`（锅架，P2 cadquery 钢丝 / P1 box 铸铁，N 灶头共享）、`_build_lid_glass_mesh` / lid_trim（glass_lift_lid 掀盖）、`griddle_plate` cadquery（griddle）、`_build_leg_profile`+`LatheGeometry`（raised_legs 撇腿）、`BezelGeometry`door_frame / `_build_half_door_frame_mesh`（门 / 半门）、`KnobGeometry`+`knob_mesh`（旋钮，N 复用同一对象）、`storage_drawer` box 托盘。
- captured 接口 allow_overlap：`run_stove_tests` 里逐机构 / 逐轴补 element-scoped `allow_overlap`（side_hinged door_hinge_pin/hinge_plate↔door_hinge_cup（L610-626）/ french hinge_pin↔door_hinge_barrel（L596-620）/ drop_down(P2) door_hinge_lug↔lower_front_panel（P2 L564-568）/ lid hinge_leaf↔lid_hinge_barrel（P2 lid）/ drawer 侧↔导轨 / knob_shell↔control_panel（P2 L546-552）），照搬各样本 run_tests 段。
- conditional 范围解析顺序：先采 door_mechanism / cooktop / base / Nb → 解析 griddle→Nb=0 / lid_open_angle（仅 glass_lift_lid）/ drawer_travel（仅 storage_drawer）/ burner_spacing（仅 Nb≥2）/ 派生 Nk=Nb → 采 width/height/depth/angle independent scale → 派生烤箱腔高 / 灶台面 Z / 灶头网格行列 → 投影四条 clearance inequality。
- N 退化：Nb=1 用单灶头（不进网格循环，等价 range(1)）；cooktop=griddle 时 Nb=0（不发射灶头 / 锅架）；Nb≥2 走灶台网格 `for i in range(Nb)`。
- 灶头网格行列由 Nb 解析：Nb=1 单头居中 / 2 单排沿 Y / 3 单排 3 / 4 双排 2×2 / 5 双排 2+3 / 6 双排 2×3；旋钮一一对应沿 Y 等距。绝对式 placement（每个 i 位置由 Nb + 中心解析，不累加漂移）。
- 参考模板：`agent/templates/Other_Built_in_oven.py`（**同小类家族、邻类**：同为厨电箱体 + 前 REVOLUTE 门（drop_down/side_hinge/french 三机构完全同构）+ KnobGeometry 旋钮 CONTINUOUS/REVOLUTE + 多重性轴进 slot_choice + 兼容矩阵 gating + captured-pin allow_overlap，门机构 / 旋钮 / 多重性骨架可直接同构改编，仅加顶部灶台 + cooktop/base 两 named slot）；`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + 多重性轴 `("count",f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 + captured-pin allow_overlap）。

## Module Source Index

| source_id | slot/轴 | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root + door + cooktop + base + burner（基线）| body + drop_down_front + open_burners + plinth_kickbase | rec_..._ee507c92（P1 compact）| `body`+plinth+feet L64-81 / 烤箱腔 liner/rack L139-177 / burner 循环 L180-198 / grate `grate_{gi}` FIXED L200-242 / `oven_door`+REVOLUTE L248-294 / knob 循环+REVOLUTE L299-328 | 箱体 root + 下翻门基线 + 明火灶头 + 踢脚座 + burner/knob copy-logic 源 |
| S2 | root + door + cooktop + base + burner（基线）| body + drop_down_front + open_burners + plinth_kickbase | rec_..._10691ac9（P2 stainless）| `body` L226-349 / `_build_grate_mesh` L107-159 / burner 循环 L301-323 / `oven_door`+REVOLUTE+`door_hinge_lug` L383-457 / knob 循环+REVOLUTE L477-498 / 滑出 rack PRISMATIC L503-515 / allow_overlap L546-583 | 不锈钢箱体 + 下翻门（hinge_lug captured）+ 钢丝锅架 + brushed_stainless 配色 + captured 范式 |
| S3 | door_mechanism | side_hinged_swing | rec_variant-door-mechanism-side-hinged-swing-change-_20260618_063803_125635_754e1747 | door+`door_hinge_pin`/`hinge_plate` L410-493 / `oven_door_hinge` REVOLUTE -Z L495-505 / body hinge cups L343-360 / allow_overlap L610-626 | 侧铰单门（REVOLUTE -Z + door-local 左竖铰 origin + pin/cup captured）|
| S4 | door_mechanism | french_double | rec_variant-door-mechanism-french-double-replace-the_20260618_063803_121384_3852f805 | `_build_half_door_frame_mesh` L213-228 / `door_{i}` 循环 L422-490 / 2×REVOLUTE ∓Z L480-490 / body `door_hinge_barrel_{i}` L361-366 / allow_overlap L596-620 | 法式双叶（2×REVOLUTE 镜像 + 中线对接 + pin/barrel captured）|
| S5 | cooktop | glass_lift_lid | rec_variant-cooktop-lid-glass-lift-lid-add-a-hinged-_20260618_063803_108536_324b9170 | `cooktop_lid` part L247-309 / `cooktop_lid_hinge` REVOLUTE -Y L311-322 / body `lid_hinge_bracket` L262-267 | 玻璃掀盖（后铰 REVOLUTE -Y 掀起露灶，保留下方灶头）|
| S6 | cooktop | griddle_flat_top | rec_variant-cooktop-lid-griddle-flat-top-replace-the_20260618_063803_110672_3991e157 | `griddle_plate` part L176-192 / `griddle_mount` FIXED L193-199 | 平面铁板灶（整面 FIXED 热板替换灶头，Nb→0）|
| S7 | base | storage_drawer | rec_variant-base-storage-storage-drawer-replace-the-_20260618_063803_119100_ed3ce770 | `storage_drawer` part L272-327 / `drawer_slide` PRISMATIC +X L330-338 / body 抬高腔底 + 下面板 L88-111 | 储物 / 保温抽屉（PRISMATIC +X 拉出 + 烤箱腔抬高）|
| S8 | base | raised_legs | rec_variant-base-storage-raised-legs-lift-the-whole-_20260618_064727_806978_263d7de1 | `_build_leg_profile` L64-78 / `LatheGeometry` leg_geom + 四 `leg_{i}` body visual L106-118 / `LEG_CORNERS` L56-62 | 四撇复古车削腿（body visual 抬高整机，Rule 1）|
