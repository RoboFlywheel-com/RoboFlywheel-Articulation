# Document folder — Modular Spec

> 来源小类：`picture/Stationary/Folder`（articraft_data 上游小类样本池；对象身份为 file / document folder，一张刚性卡纸沿底部 spine 折成 back + front 两片封面，front 封面顶边切出 labeling tab，内夹一叠纸，一张活页正在抽出）。slug 取规范拼写 `folder`。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 **workbench-only** 样本（1 个 parent + 10 个单轴 fork 变体），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`，且上游 `rating` 当前为 `null`**。进入 TEMPLATE_AFTER_REVIEW 前需先把这 11 个 record 目录 + 物化缓存同步进本仓库并批量写 `rating=5`（收敛即入池：11 个样本均 compile rc=0、均含 ≥1 非 fixed joint、均不出类目）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_cover_profile` / `_spine_shape` / `_page_shape` / `_flap_shape` / `_prong_shape` / `_pleat_facet` / `spine_hinge_front` / `spine_hinge_sheet` / `flap_hinge` / `prong_bend_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `folder` |
| template path | `agent/templates/Stationary_Folder.py` |
| test path (optional) | `tests/agent/test_folder_template.py`（不写，sweep 为唯一验收）|
| stage | `TEMPLATE_BUILT` |
| status | `implemented`（sweep-pipeline verdict=pass）|
| __modular__ | `True` |
| pattern | `mixed`（固定 root `back_cover` chassis + parallel-children 槽位：front_cover/loose_sheet 核心铰链 + spine + interior + closure，**外加** captured-page stack 与 labeling-tab 两根多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent + 10 单轴 fork 变体；均 converged，compile rc=0、均有 ≥1 非 fixed joint、workbench-only）|
| read_count | 11（全部样本 prompt 全文 + parent / 关键机构 fork 的 `model.py` 逐行读，含 build_object_model + run_tests）|
| read_scope | all 5-star samples in this category（小类只有这 11 个，无抽样）|
| source_index_policy | only adopted module sources are indexed below（11 个样本全部提供 module / 轴来源，无未采用样本）|

样本与采纳分工：
- **S0 parent**（`rec_..._cf7c3a2e`）：letter-size 绿色 file folder。`back_cover`（root，含 `spine_fold` 圆角折 + STACK_N=3 captured pages 内联 visual），`front_cover`（带左三分之一 rect tab）REVOLUTE 绕 −X 在底 spine 开合，`loose_sheet`（带 ruled lines）REVOLUTE 绕 −X 抽出。**全批基线**：提供 cover profile、spine fold、page/ruled-line helper、两根核心 spine REVOLUTE 铰链。
- **S1 corner**（`rec_folder_var_corner`）：把封面外角从 rounded 改 square-cut（footprint shape family）。**corner_style 槽位来源**（`CORNER_R→0`，去掉 `.edges("|Y").fillet`）。
- **S2 tabprofile**（`rec_folder_var_tabprofile`）：rect index tab → full-width straight-cut top tab（整条顶边抬高成一条宽 tab）。**tab_style `full_width_straight` 候选来源**。
- **S3 tabposition**（`rec_folder_var_tabposition`）：tab 从左三分之一移到居中。**tab_style `rect_index_center` 候选来源**（仅改 `TAB_X0`）。
- **S4 tabcount**（`rec_folder_var_tabcount`）：单 tab → 三个等距 staggered cut tabs，`for i in range(3)` + 共享 tab helper。**tab 多重性轴来源**（`n_tabs∈{1,3}` 及规则间距）。
- **S5 gusset**（`rec_folder_var_gusset`）：圆角单折 spine → accordion-pleated expanding gusset，`for i in range(N_PLEATS)` 之字形 pleat facet + 共享 `_pleat_facet` helper（N_PLEATS=6）。**spine_style `accordion_gusset` 候选来源**（spine 内部 pleat 多重性）。
- **S6 dividers**（`rec_folder_var_dividers`）：内部加 2 片 fixed divider 面板，`for i in range(2)` + 共享 helper，把单舱分成三舱。**interior `divider_panels` 候选来源**（fixed parent visual，不动→不建独立 part）。
- **S7 topflap**（`rec_folder_var_topflap`）：加 fold-over top closure flap，作 `front_cover` 的 REVOLUTE child，绕 +X 在 front cover 顶边翻下盖住正面。**closure `top_flap` 候选来源**（真实新增 1 part + 1 REVOLUTE）。
- **S8 prongfastener**（`rec_folder_var_prongfastener`）：内部加 two-hole metal prong fastener strip（fixed visual）+ 2 根 upright prong tongue，`for i in range(2)`，每 prong REVOLUTE 绕 −X 折弯夹住纸叠。**closure `prong_fastener` 候选来源**（fixed strip visual + N=2 REVOLUTE prong 多重性）。
- **S10 stackcount**（`rec_folder_var_stackcount`）：captured page stack 从 3 增到 7，同一 `for i in range(n)` loop + 共享 page helper。**captured-page 多重性轴来源**（`n_pages∈[3,7]` 及叠厚）。

冗余说明：所有 fork 的 `back_cover`/`front_cover`/两根核心 spine REVOLUTE 铰链均与 parent 同构（同一基线壳 + page/spine helper）；每个 fork 各自只改 1 根结构轴，diff 干净。10 个 fork 恰好把 5 个可替换 slot + 2 根多重性轴各覆盖一个收敛候选。

## 核心身份

文件夹 / 文档夹（file / document folder）：一张刚性卡纸（card stock，厚 ~0.0016 m）沿底部 **spine 折线**（沿 X 的水平折）折成 **back cover**（root，立在后面）与 **front cover**（绕底 spine REVOLUTE 翻开/合上）。坐标约定：+X = 封面宽（spine 沿 X）、+Y = 厚度/前后、+Z = 上（spine 在底 z=0，封面沿 +Z 升起）。front cover 顶边切出一个 **labeling tab**（凸出顶边的索引标签）。内部夹一叠 **captured pages**（固定内联在 back cover 上的纸，不动），其中一张 **loose sheet**（带 ruled lines）正绕同一 spine 线 REVOLUTE 抽出。**主用户机构 = front cover 绕底 spine 的开合（REVOLUTE）**，叠加 loose sheet 抽出（REVOLUTE）。

默认成熟域：rounded 或 square 角的 letter-size 封面；rect 索引 tab（左/中位置、1 或 3 个）或全宽直切 tab；圆角单折或 accordion 折叠 gusset spine；内部素净或加 fixed divider 隔板；可选 closure 机构（无 / 翻盖 top flap / 内部 prong fastener）；captured page 叠 3–7 张。活动语义恒为"front cover 绕底 spine 开合 + loose sheet 抽出"，叠加可选 closure 的 REVOLUTE（翻盖翻开 / prong 折弯）。captured pages、divider、prong strip plate、spine fold/gusset、tab 均为 back/front cover 上的 inline visual（不动→不建独立 FIXED part）。

不该混入：三孔 ring binder / 活页夹（带金属 ring 开合机构、硬质书脊、塑料环，机构身份不同）、clipboard（带夹子 clip + 硬背板，无折合封面）、信封 envelope（封口三角片，无 spine 折 + 无 tab + 无内页叠）、document wallet / zip case（拉链或松紧绳全封闭，非开放折合封面 + tab）。Stationary 大类内也区别于 Clip / Pen / Calculator / Scissors 等。

## 槽位 + 候选模块表

> **建模注记（重要）**：folder 是 **root `back_cover` chassis + 一组 parallel children + 两根多重性轴**。核心 children（恒存在）：`front_cover`（REVOLUTE 绕底 spine 开合，挂 back_cover）、`loose_sheet`（REVOLUTE 绕底 spine 抽出，挂 back_cover）。可选 closure children 挂 front_cover 或 back_cover。captured pages / divider / spine fold / tab / prong strip 均为 cover 上的 **inline visual**（不动装饰不建独立 part）。下面 corner_style / tab_style / spine_style 改的是 cover 上 inline 几何的 footprint/profile/构造族；interior / closure 是 body 的并联可替换层（closure 含真实活动 part）。tab 数与 page 数由 §8 两根多重性轴描述。

### Slot A：corner_style（封面外角 footprint shape family）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_corners（基线） | rec_..._cf7c3a2e（S0；多数 fork 同形） | `_cover_profile` L80-112（`.edges("|Y").fillet(CORNER_R)` L99） | eligible if compatible | 圆角矩形封面（`rect`+`extrude`+`fillet`），外四角 radiused |
| square_corners | rec_folder_var_corner（S1） | `_cover_profile`（`CORNER_R=0`，省略 `.fillet`）L80-112 | eligible if compatible | 方角矩形封面（crisp square-cut 外角），无角 fillet |

> 降级理由（2 candidate）：footprint 角处理只有 rounded / square 两个真实收敛形态，现实 file folder 外角词汇表本身窄。扩容须回 fork 池补造（如 clipped 斜切角），不在模板侧虚构。corner_style 同时控制 back+front 两封面、tab、closure flap 的角 fillet（成对绑定）。

### Slot B：tab_style（labeling tab 切割 profile）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rect_index_left（基线） | rec_..._cf7c3a2e（S0） | tab block L101-110（`TAB_X0=0.030` 左三分之一）| eligible if compatible | 窄矩形索引 tab，凸出顶边，左三分之一位置 |
| rect_index_center | rec_folder_var_tabposition（S3） | tab block（仅改 `TAB_X0` 至居中）L101-110 | eligible if compatible | 同窄矩形 tab，居中于顶边 |
| full_width_straight | rec_folder_var_tabprofile（S2） | full-width 顶 tab profile（整条顶边抬高，TAB_W≈COVER_W）| eligible if compatible | 整条顶边连续抬高成一条全宽直切 tab（straight-cut folder）|

> tab_style 与 §8 tab 多重性轴正交但有 gating：`full_width_straight` 是单条连续 tab，与 `n_tabs>1` 互斥（gating 见 §9，full-width 时强制 `n_tabs=1`）。

### Slot C：spine_style（底部 spine / gusset 构造族）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_fold（基线） | rec_..._cf7c3a2e（S0；多数 fork 同形） | `_spine_shape` L115-131（单条圆角 bar，`.edges("|X").fillet`）| eligible if compatible | 圆角单折 spine：一条横跨全宽的圆角 bar 桥接两封面底缘 |
| accordion_gusset | rec_folder_var_gusset（S5） | `_pleat_facet` L118-160 + `for i in range(N_PLEATS)` L207-227（N_PLEATS=6 之字形 pleat） | eligible if compatible | accordion 折叠 gusset：N 片规则之字形 pleat facet（`for i` loop + 共享 helper）沿底 spine 排列 |

> 拓扑差异成立（仍是 inline visual 不改 part 数）：accordion 把单一 spine_fold visual 换成 N 片 pleat visual（spine 内部 pleat 多重性），几何构造族与 visual 计数显著不同，非纯尺寸。

### Slot D：interior（内部隔板；optional 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain（基线） | rec_..._cf7c3a2e（S0；多数 fork 同形） | （无 divider；仅 captured page stack）| eligible if compatible | 内部素净（单舱，仅 captured pages）|
| divider_panels | rec_folder_var_dividers（S6） | divider helper + `for i in range(2)` 规则深度（fixed 内联 visual） | eligible if compatible | 加 2 片 fixed divider 隔板（page 同高同宽族），把内部分成三舱；不动→back_cover 内联 visual |

> 降级理由（含 plain 共 2 candidate）：optional 装饰槽 {素净, 1 个真实隔板族}。divider 不动，按"不动细节内联 parent visual"做 back_cover 的 inline visual（不建 FIXED part）。`plain` 是 parent 基线合法取值。

### Slot E：closure（可选闭合机构；optional 槽，含真实活动 part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none（基线） | rec_..._cf7c3a2e（S0；多数 fork 同形） | （无 closure part）| eligible if compatible | 无闭合机构（baseline 缺省，仅两核心 spine 铰链）|
| top_flap | rec_folder_var_topflap（S7） | `_flap_shape` L166-185 + REVOLUTE `flap_hinge` L309-317（绕 +X 在 front cover 顶边）| eligible if compatible | fold-over 顶翻盖，`front_cover` 的 REVOLUTE child，绕 +X 在 front cover 顶边翻下盖正面（新增 1 part + 1 REVOLUTE）|
| prong_fastener | rec_folder_var_prongfastener（S8） | `_fastener_strip_shape` L198（fixed visual）+ `_prong_shape` L233 + `for i in range(2)` REVOLUTE `prong_bend_{i}` L401（绕 −X 折弯）| eligible if compatible | 内部 metal fastener strip（fixed 内联 visual）+ 2 根 upright prong，每 prong REVOLUTE 绕 −X 折弯夹纸叠（N=2 REVOLUTE 多重性）|

> closure 提供 3 个真实结构不同候选（≥3 达标）：none / 翻盖（挂 front cover）/ prong（挂 back cover，N=2）。两个非 none 候选 part tree 与 joint 拓扑各异。

## 槽位图（slot graph）

```
pattern: mixed（root chassis + parallel children + tab/page multiplicity）

                    back_cover (root, corner_style ∈ {rounded, square})
                     │   坐标：footprint 居中宽 X，底 spine z=0，封面沿 +Z，厚度 +Y
                     │   inline visuals: spine_style (C), captured pages[n_pages] (mult),
                     │                    interior divider (D), prong strip (E.prong)
        ┌────────────┼───────────────────┬─────────────────────┬──────────────────┐
        │            │                   │                     │                  │
   front_cover   loose_sheet         closure(top_flap)     closure(prong)
   (核心, 恒存)  (核心, 恒存)         (Slot E, 挂 front)    (Slot E, 挂 back)
        │            │                   │                     │                  │
   REVOLUTE −X    REVOLUTE −X         flap: REVOLUTE +X     prong_i: REVOLUTE −X
   @ 底 spine     @ 底 spine          @ front 顶边          @ strip 顶 ×2
   (开合, tab     (抽出 loose          (翻下盖正面)          (折弯夹纸叠)
   见 Slot B +     sheet, ruled
   mult)          lines inline)
```

接口点位（每条 back/front→child 连接）：
- **back_cover → front_cover**（核心）：mating = 底 spine 线（`origin=(0, COVER_GAP+COVER_T, 0)`），joint = REVOLUTE，axis `(−1,0,0)`，range `[0,1.4]`。front cover 沿 +Z 升起，正 q 把顶边推向 +Y（开合）。
- **back_cover → loose_sheet**（核心）：mating = 底 spine 线（`origin=((COVER_W−PAGE_W)/2, COVER_T+0.0008+n_pages·STACK_GAP, 0)`），joint = REVOLUTE，axis `(−1,0,0)`，range `[0,1.2]`，正 q 把活页抽向 +Y。
- **front_cover → top_flap**（E.top_flap）：mating = front cover 顶边 hinge 线（`origin=(0, COVER_T, COVER_H)`），joint = REVOLUTE，axis `(1,0,0)`，range `[0,π]`。flap 沿 −Z 挂下（q=0 闭合盖正面），正 q 抬起。
- **back_cover → prong_i**（E.prong_fastener）：mating = fastener strip 顶缘（`origin=(prong_x_i, COVER_T+STRIP_T, STRIP_Z+STRIP_H)`），joint = REVOLUTE，axis `(−1,0,0)`，range `[0,~1.6]`，正 q 把 prong 折向 +Y 夹纸叠。
- **互斥/可选/派生**：Slot E 三选一（none / top_flap / prong_fastener，互斥单选）；Slot D optional 可与任一 closure 并存（异面）；tab 角 fillet、flap 角 fillet 由 corner_style **派生**；full_width_straight tab 与 `n_tabs>1` 互斥。

## 每槽位 Module Emits / Interfaces

### Slot A / module rounded_corners / square_corners
| emits | 描述 | 来源 |
|---|---|---|
| parts | `back_cover`（root）、`front_cover`（核心 child）；外角 fillet=CORNER_R（rounded）或 0（square）| S0 / `_cover_profile` L80-112；S1 corner |
| internal joints | 无（角处理只改 inline 几何）| — |
| downstream interface | 底 spine 线（供 front_cover / loose_sheet 锚定）| S0 / L99,247 |
| 派生 | tab、top_flap 的角 fillet 随此派生 | S0 / L109,L184 |

### Slot B / module rect_index_left / rect_index_center / full_width_straight
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：tab 作为 `front_cover` 的 inline 几何（union 进 cover profile）| S0 / L101-110 |
| upstream interface | 顶边切割位置（左/中/全宽）| S0 L105、S3 居中、S2 全宽 |

### Slot C / module rounded_fold / accordion_gusset
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：spine 作为 `back_cover` inline visual（rounded=单 bar；accordion=N pleat visual）| S0 `_spine_shape` L115-131；S5 `_pleat_facet`+loop L118-227 |
| upstream interface | 底 spine 线桥接两封面底缘 | S0 L123-130 |

### Slot D / module plain / divider_panels
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：divider 作为 `back_cover` inline fixed visual ×2（plain 时无）| S6 divider helper + `for i in range(2)` |
| upstream interface | 内部规则深度（page 同高同宽族）| S6 |

### Slot E / module top_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `top_flap`（flap 面板，hinge 边在 part frame z=0，向 −Z 挂下）| S7 `_flap_shape` L166-185 |
| internal joints | `flap_hinge` REVOLUTE，axis (1,0,0)，range [0,π]（挂 front_cover 顶边）| S7 L309-317 |
| upstream interface | front cover 顶边 hinge 线 `origin=(0,COVER_T,COVER_H)` | S7 L314 |

### Slot E / module prong_fastener
| emits | 描述 | 来源 |
|---|---|---|
| parts | `prong_{i}`（金属舌片，hinge 边在 part frame z=0，向 +Z 升）×2；`fastener_strip` 作 back_cover inline fixed visual | S8 `_prong_shape` L233、`_fastener_strip_shape` L198 |
| internal joints | `prong_bend_{i}` REVOLUTE，axis (−1,0,0)，range [0,~1.6] ×2（挂 back_cover strip 顶）| S8 L401 |
| upstream interface | fastener strip 顶缘 `origin=(prong_x_i,COVER_T+STRIP_T,STRIP_Z+STRIP_H)` | S8 L396-397 |

### 核心 child / front_cover + loose_sheet（恒存）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_cover`（REVOLUTE 开合）、`loose_sheet`（REVOLUTE 抽出，含 ruled lines inline visual）| S0 L206-226 |
| internal joints | `spine_hinge_front` / `spine_hinge_sheet` REVOLUTE，axis (−1,0,0) | S0 L242-268 |
| upstream interface | back_cover 底 spine 线 | S0 L247,263 |

### captured-page multiplicity / stack_page_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：`stack_page_{i}` 作 back_cover inline visual ×n_pages（不动 captured pages）| S0 `for i in range(STACK_N)` L194-203；S10 n=7 |
| upstream interface | back_cover 内面规则 Y 叠放 | S0 L194-203 |

### labeling-tab multiplicity / tab_{i}（见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：n_tabs 个 tab block union 进 front_cover profile（规则 staggered 间距）| S4 `for i in range(3)` 共享 tab helper |
| upstream interface | front cover 顶边规则等距位置 | S4 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| corner_style | enum | {rounded_corners, square_corners} | rounded_corners | choice | deterministic procedural sampler 选择 | Slot A 表 |
| tab_style | enum | {rect_index_left, rect_index_center, full_width_straight} | rect_index_left | choice | sampler 选择 | Slot B 表 |
| spine_style | enum | {rounded_fold, accordion_gusset} | rounded_fold | choice | sampler 选择 | Slot C 表 |
| interior | enum | {plain, divider_panels} | plain | choice | sampler 选择；optional | Slot D 表 |
| closure | enum | {none, top_flap, prong_fastener} | none | choice | sampler 选择；optional 单选 | Slot E 表 |
| n_tabs | int | [1, 4] | 1 | independent | 加权采样（1 偏多）后 clamp；`full_width_straight` 时强制 1 | §8 / S4 |
| n_pages | int | [2, 8] | 3 | independent | 加权采样（小叠偏多）后 clamp | §8 / S0、S10 |
| n_pleats | int | [4, 8] | 6 | conditional | 仅 `spine_style==accordion_gusset` 时有意义；加权采样后 clamp | §8 / S5 |
| cover_w_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 COVER_W（封面宽）；clamp 保 letter 比例 | S0 L41 |
| cover_h_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 COVER_H（封面高）；clamp 保 portrait | S0 L42 |
| tab_proj_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 TAB_H（tab 凸出高）；clamp | S0 L48 |
| flap_reach_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 closure==top_flap 时缩放 FLAP_H；clamp 使翻盖闭合不超出封面底缘 | S7 FLAP_H L68 |
| (—) | constraint | — | — | inequality | tab 网格 X 包络 ≤ 封面顶边可用宽（`n_tabs·tab_pitch ≤ COVER_W·cover_w_scale − 2·margin`）；越界回缩 tab 宽或减 n_tabs | 接口 / footprint |
| (—) | constraint | — | — | inequality | captured page 叠 Y 厚 ≤ 内部 cover gap（`n_pages·STACK_GAP ≤ COVER_GAP − clearance`）；越界回缩 STACK_GAP | 接口 / S0 内夹 |
| (—) | constraint | — | — | inequality | accordion pleat 总 Y 深 ≤ spine gusset 深域（`n_pleats·pleat_dy ≤ GUSSET_DEPTH`）；按比例分配 | S5 L199 |

连续 scale 默认独立采样 → 派生 tab/flap 角 fillet（随 corner_style）→ conditional（n_pleats / flap_reach 按上游 enum 解析）→ inequality 把 tab 网格 / page 叠 / pleat 深投影回封面可行域。全部在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

folder 有 **3 根多重性轴**（tab 数、page 数、pleat 数），按规则各自单独声明：

### 轴 1：labeling-tab count（`n_tabs`）
- `count_param`: `n_tabs`
- `N_range`: `[1, 4]`（产品域；1=单索引、2-3=分类索引、4=密索引）。已覆盖样本：S0=1、S4=3
- sampling domain：1 偏多（高频），3-4 稀有（长尾）
- copied object：单条 tab block union 进 front_cover profile（不建独立 part；inline 几何）
- naming：`tab_{i}`（visual 内 union；slot_choices 编 `tabs_{n}`）
- placement：front cover 顶边规则等距 staggered（`for i in range(n_tabs)`）
- joint policy：无 joint（tab 是 front cover 的固定几何，随 front cover 开合而动）
- source/gating：S4 `for i in range(3)` + 共享 helper；`full_width_straight` tab_style 时强制 `n_tabs=1`（互斥，§9 gating）

### 轴 2：captured-page count（`n_pages`）
- `count_param`: `n_pages`
- `N_range`: `[2, 8]`（产品域；薄夹 2-3、厚夹 6-8）。已覆盖样本：S0=3、S10=7
- sampling domain：小叠偏多（3-4 高频），7-8 稀有
- copied object：单张 page（`_page_shape` helper）作 back_cover inline visual（不动 captured pages）
- naming：`stack_page_{i}`（visual 名；不建独立 part）
- placement：back_cover 内面沿 +Y 规则等距叠放（`for i in range(n_pages)`，间距 STACK_GAP）
- joint policy：无 joint（captured pages 固定，inline 装饰）
- source/gating：S0/S10 同一 loop；叠厚 inequality 投影（§7）

### 轴 3：accordion pleat count（`n_pleats`）
- `count_param`: `n_pleats`
- `N_range`: `[4, 8]`（产品域；浅 gusset 4、深 gusset 8）。已覆盖样本：S5=6
- sampling domain：5-6 偏多，8 稀有
- copied object：单片 pleat facet（`_pleat_facet` helper）作 back_cover spine inline visual
- naming：`pleat_{i}`（visual 名）
- placement：底 spine 沿 +Y 规则之字形（`for i in range(n_pleats)`）
- joint policy：无 joint（pleat 固定 inline 几何）
- source/gating：**仅 `spine_style==accordion_gusset` 时有效**（conditional）；pleat 深 inequality 分配（§7）

## 拓扑多样性审计

总组合数（离散槽）：corner_style(2) × tab_style(3) × spine_style(2) × interior(2) × closure(3) = **72**
叠加 multiplicity：n_tabs(部分 tab_style 下 4 值) × n_pages(7 值) × n_pleats(spine 子轴 5 值) → 不同 part/joint/visual 计数 = 不同拓扑等价类。
→ 96 × ~数十 ≈ **数百 distinct 拓扑**（远超门槛）。

理由：仅 72 个离散槽组合即 ≫10；closure（含 N=2 多重性 part）+ tab/page/pleat 多重性轴再乘，distinct 拓扑充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——先加权选 5 个离散 slot（closure/interior 偏 none/plain，corner 偏 rounded，tab 偏 rect_index）、再加权采 n_tabs/n_pages/n_pleats（小 N 偏多）、经 `resolve_config` 的 conditional 解析（n_pleats 仅 accordion 有效、flap_reach 仅 top_flap）与 inequality（tab 网格/page 叠/pleat 深投影）。compatibility matrix 排除非法组合（full_width tab ↔ n_tabs>1）。`seed=0` 不特殊。无 regression overrides（无已知失败回归）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类约 96 离散组合 × 多重性，低于 300 时记录合法组合空间或采样权重原因。
Controlled local parameterization：初版含 `cover_w_scale` / `cover_h_scale` / `tab_proj_scale` / `flap_reach_scale`（§7），全 clamp/conditional，受 footprint 包络、tab 网格、page 叠厚、flap 闭合约束，不改拓扑、joint 语义或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序：corner→tab→spine→interior→closure→(n_tabs,n_pages,n_pleats)→scales；加权（closure/interior 偏 none/plain，小 N 偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | full_width_straight ⇒ n_tabs=1；n_pleats 仅 accordion 有效；closure 三选一互斥；divider 可与任一 closure 并存（异面）；flap_reach 仅 top_flap clamp | 无穿模/悬空/越界 tab、page 叠不溢、flap 闭合不超底缘、prong REVOLUTE 真实开合 |
| controlled local variation | cover_w/h_scale / tab_proj_scale / flap_reach_scale + clamp | 比例变化不破坏 spine 铰链、tab 网格、page 叠、flap 闭合、joint origin、类别身份 |
| regression overrides | none（初版无）| 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | 与 InterfaceSpec/MatingContract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A corner_style | 2 | yes | no | footprint 角处理只有 rounded/square 两真实形态 |
| B tab_style | 3 | yes | yes | 左/中 rect index + 全宽直切 |
| C spine_style | 2 | yes | no | 圆角单折 / accordion gusset |
| D interior | 2 | yes | no | optional：{plain, divider} |
| E closure | 3 | yes | yes | none / top_flap / prong_fastener |
| (mult) n_tabs/n_pages/n_pleats | — | — | — | 三根多重性轴，提供主拓扑乘子 |

## Validator

- slot_choices_for_seed returns implemented module names（corner_style / tab_style / spine_style / interior / closure + tabs_{n} / pages_{n}）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：full_width tab⇒n_tabs=1；n_pleats 仅 accordion；closure 三选一
- optional regression overrides 初版为空
- controlled local scale params 全 clamp，不破坏 spine 铰链 / tab 网格 / page 叠 / flap 闭合 / joint origin / 类别身份
- cross-part scale 依赖（tab 网格 vs 封面宽、page 叠 vs cover gap、pleat 深 vs gusset 深）在 `resolve_config` 内 inequality 求解
- 核心 joints：spine_hinge_front / spine_hinge_sheet REVOLUTE axis (−1,0,0)；closure 各 REVOLUTE（flap +X / prong −X）
- copied objects 遵循 `stack_page_{i}` / `tab_{i}` / `pleat_{i}` / `prong_{i}` 命名 + 规则 placement + 统一 joint policy
- captured pages / spine / divider / tab / prong strip 恒为 cover inline visual（不建 FIXED 装饰 part）

## Reject cases

- 把 captured pages / spine fold / divider / prong strip / tab 做成 FIXED-joint 独立 part（违反"不动装饰内联 cover visual"）。
- front cover 不绕底 spine 真实 REVOLUTE 开合（核心机构退化为静态 booklet，零活动 joint）。
- closure 的 top_flap / prong 做成 FIXED 不动 part（应是真实 REVOLUTE 活动件）。
- tab 网格越出封面顶边、page 叠厚溢出 cover gap、accordion pleat 深超 gusset 深域。
- full_width_straight tab 同时 n_tabs>1（未做互斥 gating）。
- 多重性退化：用手写命名的 2-3 个 page/tab/prong 代替 `for i in range(N)` 循环 + 共享 helper。
- config_from_seed 采样到未实现组合（如 n_pleats 在 rounded_fold spine、closure 多选）。
- corner_style 改了 back cover 角但 tab/flap 角 fillet 未随派生（不一致）。

## 与相邻类别的边界

- 不该混入：三孔 ring binder / 活页夹（金属 ring 开合机构 + 硬书脊 + 塑料环；folder 身份 = 卡纸折合封面 + tab + 内页叠）。
- 不该混入：clipboard（硬背板 + 顶部 clip 夹，无折合封面 + 无 spine 折）。
- 不该混入：信封 envelope（封口三角片，无 spine 折 + 无 tab + 无开放内页叠）。
- 不该混入：document wallet / zip case（拉链或松紧绳全封闭，非开放折合封面 + tab）。
- Stationary 大类内：区别于 Clip / Pen / Calculator / Scissors 等无折合封面文具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 自动作者一次性产出 spec + 模板（用户要求不停审核）。模板已实现 `agent/templates/Stationary_Folder.py`（slug 已注册于 `cli/template.py`），`uv run articraft template sweep-pipeline folder` verdict=pass。原审核关注点：①corner_style/spine_style/interior 各 2 candidate 的降级是否接受（单 parent 小类，扩容须回 fork 池补造）；②3 根多重性轴（n_tabs/n_pages/n_pleats）的 N_range 与权重档；③closure 三选一互斥 + full_width↔n_tabs gating 方案。|

## 模板实现备注（可选）

- 共享 helper：`_cover_profile`（按 corner_style 分 rounded/square、按 tab_style + n_tabs 切顶边 tab）、`_spine_inline`（按 spine_style 分单折 bar / N pleat loop）、`_page_shape`（captured page + loose sheet 共用）、`_flap_shape` / `_prong_shape` / `_fastener_strip_shape`（closure 各候选）、`_divider_shape`（interior）。
- captured-pin/hinge 注意点：closure 的 prong/flap REVOLUTE 均为捕获/缝合几何（hinge 边缝在 cover 缘），joint 省略 MatingContract（grandfathered），靠 flat 0.015m articulation-origin 基线 + element-scoped `allow_overlap`（flap 闭合贴 front cover 外面、prong 穿纸叠、front cover 闭合贴 captured stack、loose sheet 在 stack 内）。
- 派生与门控集中在 `resolve_config`：tab/flap 角 fillet（随 corner_style）、n_pleats（仅 accordion）、flap_reach（仅 top_flap）、tab 网格 / page 叠 / pleat 深投影。
- 不动细节恒内联 cover visual：spine fold/gusset、captured pages、divider、prong fastener strip plate、tab。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | core/A/B/C/mult | 基线 | rec_..._cf7c3a2e | `_cover_profile` L80-112、`_spine_shape` L115-131、`_page_shape` L134-141、`_ruled_lines_shape` L144-159、核心 REVOLUTE L242-268、stack loop L194-203 | 封面壳 + 圆角折 spine + page/ruled helper + 两核心 spine 铰链 + page 多重性基线 |
| S1 | A | square_corners | rec_folder_var_corner | `_cover_profile`（CORNER_R=0） | 方角 footprint |
| S2 | B | full_width_straight | rec_folder_var_tabprofile | full-width 顶 tab profile | 全宽直切 tab |
| S3 | B | rect_index_center | rec_folder_var_tabposition | tab block（TAB_X0 居中） | 居中索引 tab |
| S4 | B/mult | tab count | rec_folder_var_tabcount | `for i in range(3)` + 共享 tab helper | tab 多重性轴 |
| S5 | C/mult | accordion_gusset | rec_folder_var_gusset | `_pleat_facet` L118-160 + `for i in range(N_PLEATS)` L207-227 | accordion gusset + pleat 多重性 |
| S6 | D | divider_panels | rec_folder_var_dividers | divider helper + `for i in range(2)` | 内部 fixed 隔板 |
| S7 | E | top_flap | rec_folder_var_topflap | `_flap_shape` L166-185 + REVOLUTE `flap_hinge` L309-317 | 翻盖闭合 part + REVOLUTE |
| S8 | E/mult | prong_fastener | rec_folder_var_prongfastener | `_fastener_strip_shape` L198、`_prong_shape` L233、`for i in range(2)` REVOLUTE `prong_bend_{i}` L401 | prong 闭合 + strip fixed visual + N=2 REVOLUTE |
| S10 | mult | page count | rec_folder_var_stackcount | 同 stack loop，n=7 | page 多重性轴 |
