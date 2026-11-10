# cushion (cosmetic cushion powder compact) — Modular Spec

> 来源小类：`picture/Accessories/Cushion`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Accessories__Cushion.md`。
> **"Cushion" 在此 = 化妆气垫粉盒（cosmetic cushion powder compact，一只翻盖式化妆品粉盒盒体），不是抱枕 / 靠垫。**
> 结构家族 = 翻盖式粉盒：中空 base 碗 / 托 + 粉盘 + 盖（盖内镜子 / 标签）+ 铰链 + 前卡扣。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（2 个 parent + 7 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字** 为准（`_hollow_bowl` / `_hollow_base` / `_domed_lid` / `base_to_lid` / `leaf_rear` / `leaf_front` / `base_to_refill` / `base_to_puff_tray` / `powder_pan_{i}` / `pan_rim_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `cushion` |
| template path | `agent/templates/Accessories_Cushion.py` |
| test path (optional) | `tests/agent/test_cushion_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: case_footprint + lid_mechanism + interior，**外加** `pan_count` 粉盘多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（2 parent + 7 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **2 个 parent** 共享同一基线拓扑：`base`（root，中空碗 / 托 + 粉盘 base visual + 后铰链硬件）+ `lid`（child，盖内镜 / 标签 / 前卡扣 tab），单 `base_to_lid` REVOLUTE 后翻盖（axis=(-1,0,0)）。圆形（`81989983`，translucent 碗 + 花徽标签）与方形（`876ccf2a`，黑底白盖 + chrome 分模线 + 双环 logo）只在 footprint mesh 与装饰上不同，**part 树 / joint 拓扑相同**。
- **footprint 轴**（Slot A）：oval（`rec_cushion_var_oval`）把 base / lid mesh 改为椭圆 loft（`_oval_extrude`），part 树 / joint 与 parent 一致 → footprint 是 mesh-helper 维度，不改拓扑。
- **lid_mechanism 轴**（Slot B）：clamshell（`leaf_rear` + `leaf_front`，**2 个 REVOLUTE**，axes ∓X）/ slide_lid（`base_to_lid` **PRISMATIC** -Y，rail + slider）相对 rear_flip（1 REVOLUTE）是真正的 joint 拓扑变化。
- **interior 轴**（Slot C）：single_powder_pan（粉盘是 base visual，**无独立 joint**，Rule 1）/ refill_cartridge（`refill` 独立 part，**PRISMATIC +Z** 提起）/ puff_tray（`puff_tray` 独立 part，**REVOLUTE** 翻起）→ 内部机构是 part 数 / joint 拓扑变化。
- **pan_count 轴**（Slot D 多重性）：dual_pan（`for i in range(2)`，`powder_pan_{i}` / `powder_dome_{i}`）/ triple_pan（`for i in range(3)`，`pan_rim_{i}` / `pan_powder_{i}` / `pan_dome_{i}`）→ 同构粉盘 N 次复制，N=1 即各 parent。粉盘**非移动件**，作为 base visual inline 发射（Rule 1）。

## 核心身份

一只翻盖式**化妆气垫粉盒**（cosmetic cushion powder compact）：一只中空 `base`（半透明烟熏亚克力圆 / 椭圆碗，或亮黑圆角方托，内有凹腔），腔内坐 1 个或多个米色**粉盘**（`powder_pan`，含压粉 dome 表面），通过铰链 / 滑轨连一只**盖**（盖外有标签 / 双环 logo / 花徽，盖内贴大圆镜 `inner_mirror`），前缘有 latch tab + socket 卡扣对位。默认 footprint 沿 X 略宽（方 / 椭圆）或圆对称，坐地于 base 底。活动语义 = **盖的开合**（后单铰 REVOLUTE 翻起 / 双叶蛤壳 2×REVOLUTE 对开 / 横向 PRISMATIC 滑开）+ 可选**内部机构**（可取粉芯 PRISMATIC 提起 / 翻粉扑托盘 REVOLUTE）。默认成熟域：footprint × lid_mechanism × interior × 粉盘数 N∈[1,3] 的小型手持粉盒。

不该混入：
- **抱枕 / 靠垫 / 沙发 cushion（pillow）**——纯软体无铰链 / 无开合机构，是完全不同的类别（本类是硬壳粉盒）。
- **粉饼 / 散粉盒以外的化妆容器**（口红管 / 香水瓶 / 刷具筒）——非翻盖镜盒形态。
- **首饰盒 / 药盒（pill box）翻盖小盒**——虽同为翻盖小盒，但粉盒身份在于碗 + 粉盘 + 盖内镜 + 粉扑，缺这套即出类。

## 槽位 + 候选模块表

> **建模注记**：`case_footprint`（Slot A）是 base / lid / 内部件**同一组 mesh 的足迹形态**（圆 / 方 / 椭圆），由 footprint-aware mesh helper 一次决定，不是独立串联 slot、不贡献额外 joint；列为候选轴以对齐 schema，它与 lid_mechanism / interior / N 的笛卡尔积共同撑开多样性（见 §9）。`lid_mechanism` 与 `interior` 才是真正改 part 树 / joint 拓扑的轴。

### Slot A：case_footprint（外形 / 足迹——base+lid+内部件共享的 mesh 足迹）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round（基线） | rec_create-a-...-round-cushi_...81989983 | `_hollow_bowl` L25-29 / `_domed_lid` L32-34 / base+lid 装配 L49-85 | eligible if compatible | 圆形中空 translucent 碗（`cylinder` outer cut cavity）+ 圆 domed 盖；圆对称足迹基线 |
| square（基线） | rec_create-a-...-square-luxu_...876ccf2a | `_rounded_square` L27-29 / `_hollow_base` L31-35 / base+lid 装配 L48-85 | eligible if compatible | 圆角方形托（`box.edges("|Z").fillet`）+ 圆角方盖；X≈Y 方足迹基线 |
| oval | rec_cushion_var_oval | `_oval_extrude`/`_oval_ring`/`_hollow_oval_bowl`/`_oval_domed_lid`/`_build_oval_feature` L44-77 / base+lid 装配 L104-273 | eligible if compatible | 椭圆拉长足迹（`ellipse.extrude` loft，X 宽于 Y），base+lid+REVOLUTE 部件树与 round 一致，仅 mesh profile 重写 |

### Slot B：lid_mechanism（开合机构 —— **主机构槽**，决定盖的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rear_flip_hinge（基线） | rec_..._81989983 / rec_..._876ccf2a（2 parent）| `lid` part L62-75（81989983）+ `base_to_lid` REVOLUTE L77-85 | eligible if compatible | 单 `lid` child，后单铰翻盖 **1×REVOLUTE** axis=(-1,0,0)，origin 在后 rim 铰线，lower=0 闭合 / upper≈1.55-1.70 开 |
| clamshell_two_leaf | rec_cushion_var_clamshell | `leaf_rear` L117-164 + `leaf_front` L168-200 + `base_to_leaf_rear` REVOLUTE L204-211 + `base_to_leaf_front` REVOLUTE L213-220 | eligible if compatible | **两片叶** child（前 / 后各半深），**2×REVOLUTE** 镜像（rear axis=(-1,0,0)，front axis=(1,0,0)），中线对开；base 同时带前 / 后两组 `*_hinge_barrel_{i}` |
| slide_lid | rec_cushion_var_slide_lid | `_rail_profile` L39-48 / `_slider_slot` L51-59 / `lid` L123-188 + `base_to_lid` **PRISMATIC** L192-200 | eligible if compatible | 单 `lid` child，横向 **PRISMATIC** axis=(0,-1,0) 滑开（lower=0 / upper≈0.09）；base 边缘 `base_rail_{i}` T 轨 + lid `lid_slider_{i}` U 槽捕获 + `rail_stop_{i}` 端挡 |

### Slot C：interior（内部机构——粉盘 / 粉芯 / 粉扑托盘）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| single_powder_pan（基线） | rec_..._81989983 / rec_..._876ccf2a（2 parent）| `powder_pan` + `powder_dome` base visual L53-54（81989983）/ L52-53（876ccf2a）| eligible if compatible | 粉盘 + 压粉 dome 作为 **base visual**（Rule 1，无独立 part / joint）；坐凹腔底，盖闭合时被盖盖住 |
| removable_refill_cartridge | rec_cushion_var_refill_cartridge | `_refill_pan` L37-41 / `refill` part L69-85 + `base_to_refill` **PRISMATIC** +Z L87-95 | eligible if compatible | **可取粉芯** `refill` 独立 part（pan shell + powder_fill + sponge + 4 个 `locating_tab_{i}`），**PRISMATIC** axis=(0,0,1) 竖直提起（lower=0 坐底 / upper≈0.04）；与 `lid` REVOLUTE 并存 |
| flip_puff_tray | rec_cushion_var_puff_tray | `_puff_tray_disc` L37-41 / `puff_tray` part L104-126 + `base_to_puff_tray` **REVOLUTE** L128-136 + base 上 `tray_hinge_bracket_{i}`/`tray_hinge_barrel_{i}` L73-75 | eligible if compatible | **翻粉扑托盘** `puff_tray` 独立 part（tray_disc + applicator_puff sponge + 2 个 `tray_hinge_pin_{i}`），绕内后壁 **REVOLUTE** axis=(-1,0,0) 翻起露粉（lower=0 / upper≈1.40）；与 `lid` REVOLUTE 并存 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: case_footprint + lid_mechanism + interior 各自挂到共同 `base`（parallel children），外加 `pan_count` 在 `base` / 内部件上 N 次复制粉盘 visual）

```
base (root, 坐地; 由 case_footprint 决定碗/托 mesh + 凹腔 + 铰链/滑轨硬件)
  │
  ├── [lid_mechanism slot]  (互斥三选一)
  │     ├─ rear_flip_hinge : lid ──[base_to_lid: REVOLUTE axis=-X, origin=后 rim 铰线]
  │     ├─ clamshell       : leaf_rear ──[base_to_leaf_rear:  REVOLUTE axis=-X, origin=后 rim]
  │     │                    leaf_front ─[base_to_leaf_front: REVOLUTE axis=+X, origin=前 rim]
  │     └─ slide_lid       : lid ──[base_to_lid: PRISMATIC axis=-Y, origin=base 顶面中心接触面]
  │
  ├── [interior slot]  (三选一)
  │     ├─ single_powder_pan : (粉盘 = base visual, 无 joint)
  │     ├─ refill_cartridge  : refill ──[base_to_refill: PRISMATIC axis=+Z, origin=腔底]
  │     └─ flip_puff_tray    : puff_tray ──[base_to_puff_tray: REVOLUTE axis=-X, origin=内后壁 tray 铰线]
  │
  └── [pan_count multiplicity 轴]  powder_pan_{i} / powder_dome_{i}  i∈range(N)
        发射位置随 interior：single_powder_pan → 直接在 base 凹腔；
        refill_cartridge → 在 refill part 内；flip_puff_tray → 在 base 凹腔（托盘下方）
```

接口点位与 joint 语义：
- **lid_mechanism 接口（互斥）**：所有盖机构挂在 `base` 后 / 边 rim 硬件上。
  - rear_flip_hinge：后 rim 铰线 `hinge_barrel_{i}`（base）↔ `lid_hinge_pin_{i}`（lid）captured-pin；REVOLUTE +(-X)，origin=(0, +HINGE_Y, HINGE_Z)（落在后铰线硬件上）。
  - clamshell：前 / 后两组 barrel；rear REVOLUTE axis=-X（origin 后 rim），front REVOLUTE axis=+X（origin 前 rim），两叶各覆盖半深、中线对开。
  - slide_lid：base 左右 `base_rail_{i}` T 轨 ↔ lid `lid_slider_{i}` U 槽 captured-slide；PRISMATIC -Y，origin=(0,0,顶面接触面 Z)。`rail_stop_{i}` 限位。
- **interior 接口（三选一）**：
  - single_powder_pan：无 joint（粉盘 base visual，坐凹腔底，`expect_overlap(powder_pan, clear_bowl/black_tray)`）。
  - refill_cartridge：腔底中心 ↔ `refill` 部件，PRISMATIC +Z，origin=(0,0,腔底 seat)，q=0 坐底、提起到约 +0.04；`locating_tab_{i}` 插入碗壁定位（captured）。
  - flip_puff_tray：内后壁 `tray_hinge_bracket_{i}`/`tray_hinge_barrel_{i}`（base）↔ `tray_hinge_pin_{i}`（puff_tray），REVOLUTE -X，origin=(0, tray_hinge_y, tray_hinge_z)；q=0 盖住粉盘、翻起露粉。
- **pan_count 接口**：粉盘 / dome 为**非移动 visual**（Rule 1，inline 到承载 part 的 visual，无独立 joint）；沿 X 等距并排。承载 part 由 interior 决定（见下表）。
- **mating policy**：所有 hinge 是 pin-in-barrel captured-pin（销在 barrel 内）、slide 是 rail-in-slot captured-slide、refill locating_tab 是 tab-in-wall captured —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（见各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有盖 / 叶 / 托 q=0 闭合，refill q=0 坐底，粉盘坐腔底。
- **互斥 / 可选 / 派生**：lid_mechanism 三候选互斥（一次只一种盖机构）；interior 三候选互斥；single_powder_pan 无独立机构件（空机构）；clamshell 取消单一 `lid` 改双叶 → interior 的 lid-并存假设按盖机构调整（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / case_footprint（以 round 为例；square/oval 仅换 mesh helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`（visual: `clear_bowl`/`black_tray` 主壳 + `rim_gasket` + 后铰硬件 `rear_hinge_leaf`/`hinge_saddle_{i}`/`hinge_barrel_{i}`）| 81989983 `_hollow_bowl` L25-29 + L49-59 / 876ccf2a `_hollow_base` L31-35 + L48-58 / oval L104-177 |
| internal joints | 无（base 是 root，内部无活动件）| — |
| upstream interface | root（坐地，无父）| — |
| downstream interface | 后 / 边 rim 铰链 / 滑轨硬件 + 凹腔（供 lid_mechanism / interior 接入）| 81989983 L55-59 |

### Slot B / lid_mechanism — rear_flip_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（visual: `white_domed_lid`/`black_lid_edge`+`white_lid_top` + 标签 / logo / 花徽 + `inner_mirror` + `front_latch_tab` + `lid_hinge_pin_{i}`）| 81989983 L62-75 / 876ccf2a L61-75 |
| internal joints | `base_to_lid` REVOLUTE axis=(-1,0,0)，origin=(0,+HINGE_Y,HINGE_Z)，lower=0 / upper≈1.55-1.70 | 81989983 L77-85 |
| upstream interface | `lid_hinge_pin_{i}` 落入 base `hinge_barrel_{i}`（captured-pin）| 81989983 L74-75 |

### Slot B / lid_mechanism — clamshell_two_leaf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `leaf_rear`（black_panel + white inset + logo + `inner_mirror` + `rear_hinge_pin_{i}` + center catch）+ `leaf_front`（black_panel + cream inset + `front_hinge_pin_{i}` + catch）| clamshell L117-200 |
| internal joints | `base_to_leaf_rear` REVOLUTE axis=(-1,0,0) origin=(0,+REAR_Y,HINGE_Z) + `base_to_leaf_front` REVOLUTE axis=(1,0,0) origin=(0,-FRONT_Y? ,HINGE_Z)（前 rim）| clamshell L204-220 |
| upstream interface | 前 / 后 `*_hinge_pin_{i}` 落入 base 前 / 后 `*_hinge_barrel_{i}`（双组 captured-pin）| clamshell L99-113, L137-143, L188-194 |

### Slot B / lid_mechanism — slide_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（black_edge + white_top + parting + logo + mirror + `front_latch_tab` + `lid_slider_{i}` U 槽）| slide_lid L123-188 |
| internal joints | `base_to_lid` PRISMATIC axis=(0,-1,0)，origin=(0,0,顶面 Z)，lower=0 / upper≈0.09 | slide_lid L192-200 |
| upstream interface | `lid_slider_{i}` U 槽捕获 base `base_rail_{i}` T 轨（captured-slide），`rail_stop_{i}` 限位 | slide_lid L102-118, L182-188 |

### Slot C / interior — single_powder_pan
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`powder_pan`/`powder_dome` 为 base visual）| 81989983 L53-54 |
| internal joints | 无 | — |
| upstream interface | 坐 base 凹腔底（`expect_overlap` 守座入）| 81989983 run_tests L100 |

### Slot C / interior — removable_refill_cartridge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `refill`（`refill_pan` shell + `powder_fill` + `sponge` + `locating_tab_{i}`×4）| refill L69-85 |
| internal joints | `base_to_refill` PRISMATIC axis=(0,0,1)，origin=(0,0,腔底 seat)，lower=0 / upper≈0.04 | refill L87-95 |
| upstream interface | `locating_tab_{i}` 插入碗壁定位（captured）；refill 坐 `clear_bowl` 腔内 | refill run_tests L141-143 |

### Slot C / interior — flip_puff_tray
| emits | 描述 | 来源 |
|---|---|---|
| parts | `puff_tray`（`tray_disc` + `applicator_puff` sponge + `tray_hinge_pin_{i}`×2）；base 上加 `tray_hinge_bracket_{i}`/`tray_hinge_barrel_{i}` | puff_tray L73-75, L104-126 |
| internal joints | `base_to_puff_tray` REVOLUTE axis=(-1,0,0)，origin=(0,tray_hinge_y,tray_hinge_z)，lower=0 / upper≈1.40 | puff_tray L128-136 |
| upstream interface | `tray_hinge_pin_{i}` 落入 base `tray_hinge_barrel_{i}`（内后壁 captured-pin）| puff_tray L154-157 |

### pan_count multiplicity（粉盘复制；non-moving visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`powder_pan_{i}`/`powder_dome_{i}`（dual）或 `pan_rim_{i}`/`pan_powder_{i}`/`pan_dome_{i}`（triple）作承载 part 的 visual | dual_pan L69-72 / triple_pan L68-87 |
| joints | 无（Rule 1，粉盘非移动件 inline）| — |
| placement | `for i in range(N)`，沿 X 等距并排（dual: center±span/2；triple: (i-1)·spacing）| dual_pan L69-71 / triple_pan L67-69 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_footprint | enum | round / square / oval | round | choice | 由 deterministic procedural sampler 选；决定 base/lid mesh helper | module table |
| lid_mechanism | enum | rear_flip_hinge / clamshell_two_leaf / slide_lid | rear_flip_hinge | choice | sampler 选；主机构（互斥）| module table |
| interior | enum | single_powder_pan / removable_refill_cartridge / flip_puff_tray | single_powder_pan | choice | sampler 选；含空机构 single_powder_pan | module table |
| pan_count (N) | int | 声明域 [1,3]；sweep 采样域 [1,3]（偏小加权：1 高频、2 常见、3 长尾）| 1 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；N 与 interior 联动（见下不等式 + §8）| dual_pan / triple_pan |
| palette_style | enum | translucent_acrylic / glossy_black_chrome / pastel | translucent_acrylic | palette | palette only，**不计入 slot_choice** | 各样本材质 |
| footprint_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 base/lid X 主尺寸（保 footprint 比例），clamp | resolve clamp |
| footprint_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 base/lid Y 主尺寸，clamp | resolve clamp |
| case_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放碗 / 托高 → 凹腔深 → HINGE_Z / 铰链高，clamp | resolve clamp |
| lid_open_angle_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 REVOLUTE 盖 / 叶 / 托 `motion_limits.upper`，clamp（保 ≤π·0.95）| resolve clamp |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 slide_lid 有效；缩放 PRISMATIC upper（≤ 暴露粉盘所需行程）| resolve clamp |
| pan_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放粉盘并排间距 | resolve clamp |
| (—) | constraint | — | — | inequality | 粉盘排布不超腔：`N·(2·PAN_R) + (N-1)·gap ≤ cavity_X − 2·margin`；违反时按比例缩 PAN_R / pan_spacing 或拒绝重采（见 triple_pan 腔加宽 L34 的对照）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 盖闭合覆盖粉盘 footprint：closed lid XY 覆盖 ≥0.08（rear_flip/slide）/ 每叶覆盖半深 ≥0.04（clamshell）| 接口 / clearance |
| (—) | constraint | — | — | conditional | interior=refill_cartridge / flip_puff_tray 时粉盘改发射在 refill / 托盘下（非裸腔），pan_count 仍编 slot_choice 但承载 part 改变（见 §8 / §9）| 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 case_footprint / lid_mechanism / interior / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（并排粉盘数）：

- **count_param**：`pan_count`（模板内变量 N / PAN_COUNT；base 凹腔 / refill / 托盘下的并排粉盘数）。
- **N_range**：声明产品域 **[1, 3]**（化妆粉盒内并排粉盘数现实上限很小，单 / 双 / 三盘已覆盖真实形态；source map 建议 [1,4] 取下界保守为 [1,3] 因为只有 N=1/2/3 有样本，N=4 无源 → 见 §3 阻塞说明）。`config_from_seed` 的 sweep 采样域 **[1, 3]**（偏小加权：N=1 高频、N=2 常见、N=3 稀疏）。N=1 即各 parent / 多数槽位变体的退化情形（单粉盘，不进循环）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((1,2,3), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,3]。
- **copied object**：单只粉盘单元——`powder_pan`(+`powder_dome`) 或带 rim 的 `pan_rim`(+`pan_powder`+`pan_dome`)，共享 helper 发射（`Cylinder` 几何 / `_powder_pan_dish` mesh）；N 个 visual 复用同一几何对象。
- **naming**：`powder_pan_{i}` / `powder_dome_{i}`（dual 风格）或 `pan_rim_{i}` / `pan_powder_{i}` / `pan_dome_{i}`（triple 风格），`for i in range(N)`（dual_pan L69 / triple_pan L68 已用此结构，可直接作 copy-logic 源）。
- **placement**：沿 X **绝对式**等距并排——以腔中心对称分布（dual: `x = -span/2 + i·span`；triple: `x = (i-1)·spacing`）。绝对式（每个 i 的 x 由 N 与中心解析，不累加漂移）是 N-不变前提。
- **joint policy**：粉盘是**非移动件**（Rule 1）→ inline 为承载 part 的 visual，**不发射独立 joint**；活动关节由 lid_mechanism / interior 提供。承载 part 由 interior 决定：single_powder_pan→base 凹腔；refill_cartridge→refill part 内；flip_puff_tray→base 凹腔（托盘下）。
- **source/gating**：copy-logic 源取 dual_pan L69-72（N=2）与 triple_pan L68-87（N=3）的 `for i in range(N)` 循环；**N=1 取 parent 的单 `powder_pan`**（未循环化，等价 range(1)）。N>1 与 interior 的兼容见 §9 矩阵。

## 拓扑多样性审计

总组合数：case_footprint(3) × lid_mechanism(3) × interior(3) × pan_count 采样数(3，即 {1,2,3}) = **81**。

仅 lid_mechanism(3) × interior(3) = **9**（含 1×REVOLUTE / 2×REVOLUTE / PRISMATIC × 无 / PRISMATIC / REVOLUTE 的 joint 拓扑组合）≈ 已接近门控；叠 footprint(3) → 27 ≥ 10 已稳过，叠 N 后充裕。

理由：lid_mechanism × interior 提供真正的 joint 拓扑差异（1 REVOLUTE / 2 REVOLUTE / 1 PRISMATIC 盖 × 无 joint / PRISMATIC 内件 / REVOLUTE 内件 = 9 种 joint-topology 类），叠 footprint(3) 与 N(3) 后总 81 distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("pan_count", f"n{N}")`，对齐 shopping_bucket/fence_cascade），否则单盘与多盘在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（case_footprint / lid_mechanism / interior），经兼容矩阵合法化，再 `rng.choices` 加权 N∈[1,3]，再 uniform 各连续 scale。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 footprint_len_scale / footprint_width_scale / case_height_scale / lid_open_angle_scale / slide_travel_scale（conditional@slide_lid）/ pan_spacing_scale（conditional@N≥2）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：slide_travel 仅 slide_lid、pan_spacing 仅 N≥2）→ 采 independent footprint/height/angle scale → 派生（盖尺寸随 footprint scale 等比）→ 用两条 clearance inequality（粉盘排布不超腔、盖闭合覆盖粉盘）投影 / 回缩。跨部件依赖（粉盘排布 vs 腔宽、盖覆盖 vs footprint）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 hinge/slide origin、captured-pin/slide 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），再 `rng.choices` 加权 N∈[1,3]，再 uniform 各 scale | slot_choices_for_seed 含 `("pan_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **clamshell_two_leaf × interior**：clamshell 双叶占满 rim，flip_puff_tray 的内后壁托盘铰链与前叶冲突 → N>1 / refill / puff_tray 与 clamshell 组合时把 interior 降级为 single_powder_pan（或仅允许 single_powder_pan）；refill_cartridge（竖直 PRISMATIC 提起）与 clamshell 可共存（提起方向 +Z 不撞叶）→ 允许。 (2) **slide_lid × flip_puff_tray**：滑盖滑出方向 -Y 与翻托盘 -X 铰线不冲突 → 允许；slide_lid × refill_cartridge 允许（+Z 提起在滑盖滑开后）。 (3) **N>1（多粉盘）× interior**：refill_cartridge 的单 refill pan 复制为 N 个并排 refill 风险高（样本只有单 refill）→ N>1 时 gate interior∈{single_powder_pan, flip_puff_tray}（多盘裸腔 / 多盘+翻托盘），refill 限 N=1。 (4) footprint 与机构正交（round/square/oval 均可配任意盖 / 内件）。 | 无 floating / collision / 双叶撞托盘 / 多盘撞 refill / 盖不覆盖粉盘 / 行程不足 |
| controlled local variation | 6 个 clamped scale（footprint_len/width、case_height、lid_open_angle、slide_travel@slide、pan_spacing@N≥2），每 build 统一；slide_travel / pan_spacing 为 conditional | 比例变化不破坏 hinge/slide origin、captured 接口、盖覆盖、坐腔、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_footprint | 3 | yes | yes | round/square 为 parent 基线，oval 为 fork |
| lid_mechanism | 3 | yes | yes | 1 REVOLUTE / 2 REVOLUTE / PRISMATIC（互斥主机构）|
| interior | 3 | yes | yes | 无 joint / PRISMATIC / REVOLUTE 内件 |
| pan_count (N) | 3（采样域 {1,2,3}，1 高频 / 3 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("pan_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,3]
- `resolve_config` 把 pan_count clamp 到 [1,3]，各 scale clamp 到声明范围；slide_travel / pan_spacing 为 conditional 随 lid_mechanism / N 解析；两条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（clamshell×不兼容内件降级 single_powder_pan；refill 限 N=1；盖闭合必覆盖粉盘）
- 连续 scale clamp 后不破坏 hinge/slide origin / captured-pin/slide 接口 / 盖覆盖 / 坐腔 / N 复制
- 关键 joint：rear_flip `base_to_lid` REVOLUTE axis≈(-1,0,0)（abs(axis[0])>0.99）；clamshell `base_to_leaf_rear`/`base_to_leaf_front` 2×REVOLUTE 镜像 ±X；slide_lid `base_to_lid` PRISMATIC axis≈(0,-1,0)；refill `base_to_refill` PRISMATIC axis≈(0,0,1)；puff_tray `base_to_puff_tray` REVOLUTE axis≈(-1,0,0)
- captured-pin / slide / tab：element-scoped `allow_overlap`（`lid_hinge_pin_{i}`↔`hinge_barrel_{i}`；clamshell 前 / 后 pin↔barrel；`lid_slider_{i}`↔`base_rail_{i}`；refill `locating_tab_{i}`↔`clear_bowl`；puff `tray_hinge_pin_{i}`↔`tray_hinge_barrel_{i}`），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `*_pan_{i}` 命名 + 绝对式沿 X 等距 placement + Rule 1（无独立 joint）
- grandfather：所有 hinge/slide/tab captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 单盘与多盘 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- clamshell_two_leaf 与 flip_puff_tray 同时发射 → 双叶占满 rim、托盘内后壁铰链撞前叶；必须 gate（clamshell 配 single_powder_pan 或仅 refill）。
- refill_cartridge 在 N>1 时复制为多个并排 refill → 无样本支持、提起 / 定位 tab 互撞；refill 限 N=1。
- 把粉盘当独立活动 part 加 joint → 违反 Rule 1（粉盘非移动件，应 inline 为承载 part visual）。
- 盖 / 叶 / 托 rest pose 设成张开角而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本闭合姿态 lower=0）。
- hinge / slide origin 放在腔中心或任意点而非真实铰线 / 滑轨硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured-pin / captured-slide / locating-tab 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- pan_spacing 过大致粉盘超出凹腔 → §7 第一条不等式 FAIL；须按比例缩 PAN_R / spacing。
- 把连续尺寸 / 颜色 / 材质（palette_style / footprint scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"抱枕 / 靠垫"语义混入（软体无铰链）→ 出类，本类是硬壳翻盖粉盒。

## 与相邻类别的边界

- 不该混入：**抱枕 / 靠垫 / 沙发坐垫（pillow / throw cushion）**——纯软体、无铰链 / 无开合机构 / 无镜盒；与本类（硬壳翻盖镜盒）是完全不同的结构家族（名字相同语义不同，见顶部注记）。
- 不该混入：**口红管 / 香水瓶 / 刷具筒等其他化妆容器**——非翻盖镜盒形态（旋出 / 喷头 / 圆筒，主运动 spine 不同）。
- 不该混入：**首饰盒 / 药盒（pill organizer）翻盖小盒**——虽同为翻盖小盒，但缺粉盘 + 盖内镜 + 粉扑这套粉盒身份；如需可作单独 slug。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) case_footprint 建模为 mesh-helper 维度（非串联 slot）；(2) N_range 取 [1,3]（保守，N=4 无源，见 §3）还是按 source map 的 [1,4]；(3) clamshell × interior 与 N>1 × refill 的兼容降级策略；(4) Topology target 81<300 的说明是否接受（本小类真实结构上限）；(5) 粉盘 Rule 1 inline 无独立 joint 是否符合 multiplicity 审计期望）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_hollow_bowl`/`_hollow_base`/`_oval_*`（footprint mesh，按 case_footprint 切换）、`_domed_lid`/`_rounded_square`（盖 mesh）、`_rail_profile`/`_slider_slot`（slide_lid）、`_refill_pan`（refill）、`_puff_tray_disc`（puff_tray）、`_powder_pan_dish`/`Cylinder`（粉盘，N 复制复用同一几何对象）。
- captured 接口 allow_overlap：`run_cushion_tests` 里逐机构补 element-scoped `allow_overlap`（pin↔barrel / slider↔rail / tab↔bowl），照搬各样本 run_tests 段（81989983 L95-97、clamshell L238-258、slide_lid L212-219、refill L134-143、puff_tray L148-157）。
- conditional 范围解析顺序：先采 lid_mechanism / interior / N → 解析 slide_travel（仅 slide_lid）/ pan_spacing（仅 N≥2）/ 承载 part（interior 决定粉盘挂哪）→ 采 footprint/height/angle independent scale → 派生盖尺寸 → 投影两条 clearance inequality。
- N=1 退化：直接用 parent 的单 `powder_pan`（不进 range 循环），等价 range(1)；N≥2 走 dual/triple 的 `for i in range(N)`。
- 参考模板：`agent/templates/Bag_Suitcase_Shopping_bucket.py`（同为 mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap 骨架，本类可同构改编）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| round + rear_flip + single_pan | rec_..._81989983 | `_hollow_bowl` L25-29 / `_domed_lid` L32-34 / base+lid+REVOLUTE L49-85 / allow_overlap L95-97 | round footprint + rear_flip 基线 + 共享盖 helper + captured-pin 范式 |
| S2 | A / B / C（parent 基线）| square + rear_flip + single_pan | rec_..._876ccf2a | `_rounded_square` L27-29 / `_hollow_base` L31-35 / base+lid+REVOLUTE L48-85 | square footprint + 双环 logo + chrome 分模线基线 |
| S3 | A | oval footprint | rec_cushion_var_oval | `_oval_extrude`/`_oval_ring`/`_hollow_oval_bowl`/`_oval_domed_lid` L44-77 / 装配 L104-273 | 椭圆足迹 mesh helper（base+lid 树不变）|
| S4 | B | clamshell_two_leaf | rec_cushion_var_clamshell | `leaf_rear` L117-164 / `leaf_front` L168-200 / 2×REVOLUTE L204-220 / allow_overlap L238-258 | 双叶蛤壳（2×REVOLUTE 镜像）|
| S5 | B | slide_lid | rec_cushion_var_slide_lid | `_rail_profile` L39-48 / `_slider_slot` L51-59 / lid L123-188 / PRISMATIC L192-200 / allow_overlap L212-219 | 横向滑盖（PRISMATIC + rail/slider captured-slide）|
| S6 | C | removable_refill_cartridge | rec_cushion_var_refill_cartridge | `_refill_pan` L37-41 / `refill` L69-85 / PRISMATIC +Z L87-95 / allow_overlap L141-143 | 可取粉芯（PRISMATIC 提起 + locating tab）|
| S7 | C | flip_puff_tray | rec_cushion_var_puff_tray | `_puff_tray_disc` L37-41 / base tray hinge L73-75 / `puff_tray` L104-126 / REVOLUTE L128-136 / allow_overlap L154-157 | 翻粉扑托盘（内后壁 REVOLUTE）|
| S8 | D（multiplicity）| pan_count N=2 | rec_cushion_var_dual_pan | `for i in range(2)` `powder_pan_{i}`/`powder_dome_{i}` L69-72 | 双粉盘 copy-logic 源 |
| S9 | D（multiplicity）| pan_count N=3 | rec_cushion_var_triple_pan | `_powder_pan_dish` L38-50 / `for i in range(3)` `pan_rim_{i}`/`pan_powder_{i}`/`pan_dome_{i}` L68-87 | 三粉盘 copy-logic 源（带 rim 风格）|
