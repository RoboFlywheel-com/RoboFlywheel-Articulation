# Container cosmetic (concealer/compact cosmetic palette case) — Modular Spec

> 来源小类：`picture/Container/Cosmetic`（articraft_data 上游 Container/Cosmetic fork-variant pool）。
> 单一参考图 `001.png` = 后铰翻盖镜面遮瑕盘 compact。parent 占一个 cell，6 个 `rec_container_cosmetic_var_*` 各沿单一轴 fork。
> 引用 `model.py:Lx-Ly` 来自各样本 `data/records/<id>/revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`base` / `lid` / `shell` / `drawer` / `clasp` / `base_to_lid` / `shell_to_drawer` / `base_to_clasp` / `_pan_centers` / `_pan_mesh` / `_cell_grid_mesh` / `_base_tray_mesh` / `_lid_slab_mesh` / `_disc` / `_ring` / `_clasp_lever_mesh` / `_lid_lip_mesh` / `_shell_body_mesh` / `_drawer_body_mesh`），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_cosmetic` |
| template path | `agent/templates/Container_Cosmetic.py` |
| test path (optional) | `tests/agent/test_container_cosmetic_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named structural slots A=case_footprint / B=closure_mechanism + 一根真实 multiplicity 轴 C=pan_count，pan × N 在 tray/drawer 上循环发射）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 `rec_container_cosmetic_var_*`：square_body / round_body / slide_drawer / clasp_latch_lid / n4_pans / n12_pans）|
| read_count | 7（全文逐一读取 `build_object_model` + 所有 mesh helper + `run_tests`）|
| read_scope | all 5-star samples in this category（parent + 全部 6 fork 变体，无抽样）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

冗余/分流说明：
- parent + n4_pans + n12_pans 三者**仅 pan 网格行列不同**（2x4 / 2x2 / 3x4），共享 `base`/`lid`/`base_to_lid` REVOLUTE -X 拓扑 + 同一 `_pan_centers`/`_pan_mesh`/`_cell_grid_mesh` 循环骨架；归并为 multiplicity 轴 C（pan_count），**不另列 footprint/closure candidate**。
- square_body 改 footprint（近正方形 + bbox-from-centers `_cell_grid_mesh`），round_body 改 footprint（disc/ring 几何 + 径向 ring pan 排布），归 Slot A。
- slide_drawer 改 closure（PRISMATIC `shell`/`drawer` 抽屉，镜子移到 shell 内顶），clasp_latch_lid 改 closure（保留后铰翻盖 + 新增前缘可动 `clasp` REVOLUTE 卡扣），归 Slot B。

## 核心身份

化妆品容器 / 遮瑕盘 compact（cosmetic palette case）：一只**扁平躺放**的化妆盒，平躺于 XY 平面，底坐地，+X=length / +Y=depth / +Z=厚度（~0.015–0.018 m），整体远比厚度宽（盘状）。盒体由 CadQuery `_rounded_box`（box+`fillet("|Z")`+boolean cut 凹腔）或 `_disc`/`_ring`（圆盘）发射为带浅凹腔托盘，腔内嵌一排 / 一格一格的同构 concealer pan（膏体方块 / 圆饼，循环 `_pan_centers`→`_pan_mesh`，每块自己的 cell pocket，**recessed 不凸出 rim**），托盘带 silver frame，pan 之间有 silver `cell_grid` egg-crate 隔断；drawer 变体可在外壳顶面带 label strip。盒顶 / 盒侧一只盖按某机构开合（**主活动语义**）：后缘铰链翻盖（`base_to_lid` REVOLUTE 绕 -X 后 rim，0→110°，盖内贴 mirror）/ 线性抽屉（`shell_to_drawer` PRISMATIC 沿 +X 抽出装 pan 托盘，mirror 在固定外壳内顶）/ 后铰翻盖 + 前缘可动卡扣（`base_to_lid` REVOLUTE + `base_to_clasp` REVOLUTE +X 锁盖）。N（pan 数量）由 PAN_ROWS×PAN_COLS 网格（矩形）或径向 ring（圆形）派生，真实彩妆盘单格到约 24 格。默认成熟域：单盒、单盖机构、一组 pan。

不该混入：口红管 / 唇膏（细长竖立旋升管，是 `container_lipstick`）、细颈精华液瓶（dropper / pump 瓶，是 `container_bottle_serum`）、带盖直立储物罐 / 化妆罐（圆胖竖立罐 + 螺纹盖，是 `container_jar`）。本类的类别身份是**扁平躺放的多 pan 盘**（pan grid + 镜面盖 / 抽屉），不是竖立单腔瓶罐管。

## 槽位 + 候选模块表

> **建模注记**：`case_footprint`（Slot A）是 root tray/shell 的 mesh 形状属性（一次发射 `base_tray`/`shell_body` + frame + cell_grid，并决定 pan 排布是矩形网格还是径向 ring；drawer shell 可额外带顶面 label）。`closure_mechanism`（Slot B）决定 root↔活动盖 的 part/joint 拓扑（翻盖 / 抽屉 / 翻盖+卡扣），并决定 pan 挂在 `base` 还是 `drawer`、mirror 在 `lid` 还是 `shell`。`pan_count`（Slot C）是真实 multiplicity 轴：同构 pan × N 循环发射。三轴构成拓扑多样性（见 §9）。

### Slot A：case_footprint（盒体形态 / 足迹——root tray 的 mesh + pan 排布器）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_rect（基线）| rec_concealer-..._f124e974（parent）| `_rounded_box` L85-91 + `_base_tray_mesh` L94-109 + `_pan_centers`（矩形网格）L112-125 | eligible if compatible | 长方形圆角托盘（LEN_X≈0.13 × DEP_Y≈0.06），box+`fillet("|Z")`+boolean 凹腔，pan 为矩形网格 `pan_{row}_{col}` |
| square_rounded | rec_container_cosmetic_var_square_body | `_rounded_box` L86-92 + `_base_tray_mesh` L95-110 + `_pan_centers` L113-128 + `_cell_grid_mesh`（bbox-from-centers）L138-162 | eligible if compatible | 近正方形圆角盒（LEN_X≈DEP_Y≈0.078），L/D≈1.0（test L378-386），pan 方网格，cell_grid 由 pan center bbox 自适应 |
| round_disc | rec_container_cosmetic_var_round_body | `_disc` L72-74 + `_ring` L77-85 + `_base_tray_mesh`（disc 凹腔）L88-100 + `_pan_centers`（径向 ring）L103-111 + `_pan_mesh`（disc）L114-120 + `_cell_grid_mesh`（disc 板 + 圆 pocket）L123-137 | eligible if compatible | 圆盘形机身（RADIUS≈0.040），`_disc`/`_ring` 发射圆托盘 + 圆 ring frame，pan 为圆饼 `pan_{i}` 绕圆周径向排布，footprint round test（dx≈dy）L286-305 |

硬约束记录：case_footprint 3 candidate（达下限 3，目标 3-6）。参考图仅 1 张（rounded-rect），square 与 round 已是该类真实词汇表内最稳的两个扩展（与源 map §排除项一致：第 4 候选 oval/收腰有出类目风险，故停在 3）。rounded_rect / square 共享 `_rounded_box`+矩形网格 pan，round 用 `_disc`/`_ring`+径向 pan（不同 primitive 家族 + 不同 pan 排布器，是真实结构差异）。

### Slot B：closure_mechanism（**主开合机构槽**——盒盖动作 + part/joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rear_hinge_flip_lid（基线）| rec_concealer-..._f124e974（parent）| `lid` part L244 + `_lid_slab_mesh` L171-182 + `mirror` visual L281-285 + `base_to_lid` REVOLUTE axis=(-1,0,0) origin=后 rim L307-320 + hinge knuckles L295-302 | eligible if compatible | 后缘铰链翻盖：`base`(root)→`lid`，`base_to_lid` REVOLUTE 绕 -X 后 rim（origin `(0, DEP_Y/2, HINGE_Z)`），q=0 闭合盖座 / 0→110° 上翻；mirror 贴 lid 内面 well，pan 挂 base；2 part 1 joint |
| slide_out_drawer | rec_container_cosmetic_var_slide_drawer | `shell` part L271 + `_shell_body_mesh` L113-146 + `_mirror_plate_mesh`（shell 内顶）L175-184 + `drawer` part L286 + `_drawer_body_mesh`（tray+前 cap）L187-202 + `shell_to_drawer` PRISMATIC axis=(1,0,0) L317-330 | eligible if compatible | 线性抽屉：固定 `shell`(root,中空 sleeve)→`drawer`，`shell_to_drawer` PRISMATIC 沿 +X（origin 原点，q=0 收回 / 正 q 抽出 ≤0.08m），pan 挂 drawer，mirror 贴 shell 内顶 ceiling；2 part 1 joint，drawer-in-sleeve allow_overlap（L439-448）|
| flip_lid_with_clasp | rec_container_cosmetic_var_clasp_latch_lid | `lid`+`base_to_lid` REVOLUTE -X L402-415（同基线）+ `clasp` part L386 + `_clasp_lever_mesh`（arm+hook+barrel+button）L213-247 + `_lid_lip_mesh` L196-210 + clasp bosses L315-328 + `base_to_clasp` REVOLUTE axis=(1,0,0) 前缘 L422-435 | eligible if compatible | 后铰翻盖 + 前缘可动卡扣：保留 `base_to_lid` REVOLUTE -X，新增 `clasp` 件经 `base_to_clasp` REVOLUTE +X（origin 前缘 `(0, -DEP_Y/2, CLASP_PIVOT_Z)`），q=0 锁盖 hook 挂 lid_lip / 0→85° 解锁；3 part 2 joint（**2 活动件**）|

硬约束记录：closure_mechanism 3 candidate（达下限 3，目标 3-6）。含 REVOLUTE -X（翻盖）/ PRISMATIC +X（抽屉）/ REVOLUTE -X + REVOLUTE +X（翻盖+卡扣，2 joint）三种 joint 拓扑 + 不同 part count（2/2/3）+ 不同 mirror 承载（lid 内面 vs shell 内顶）。每个 candidate **≥1 non-fixed joint**。源 map §排除项的 `magnetic_lift_off_lid`（纯磁吸分离、0 个非 fixed joint）不作候选，已被 clasp 覆盖"按扣开合"语义。

### Slot C（multiplicity 轴）：pan_count（同构 concealer pan × N）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part·helper 名 / 结构特征 |
|---|---|---|---|---|
| n8_pans_2x4（基线）| rec_concealer-..._f124e974（parent）| `_pan_centers` L112-125 + `_pan_mesh` L128-132 + pan loop L222-229（8 个 `pan_{row}_{col}`）| eligible if compatible | 2 行 × 4 列 = 8 pans，矩形网格循环发射；PAN_COLS=4/PAN_ROWS=2 L46-47 |
| n4_pans_2x2 | rec_container_cosmetic_var_n4_pans | `_pan_centers` L106-119 + pan loop L219-226（4 个）；PAN_COLS=2/PAN_ROWS=2 L46-47；PAN_SX/GAP 适配 L48-52 | eligible if compatible | 2 行 × 2 列 = 4 pans，pan 加宽 + 间距加大适配同 footprint |
| n12_pans_3x4 | rec_container_cosmetic_var_n12_pans | `_pan_centers` L115-128 + pan loop L228-235（12 个）；PAN_COLS=4/PAN_ROWS=3 L46-47；PAN_SY 缩小 L49 适配 3 行 | eligible if compatible | 3 行 × 4 列 = 12 pans，pan_depth(Y) 缩小塞进 3 行；3-row test L378-403 |

硬约束记录：pan_count 是 multiplicity 轴（非固定 named slot），样本 N ∈ {4,8,12} 已覆盖网格因式分解（2x2/2x4/3x4）。圆形 footprint 用径向 ring 排布（PAN_COUNT，源 round_body L43-49/L103-111），矩形 footprint 用 ROWS×COLS 网格。所有 pan 共享 `_pan_mesh` + 同一循环骨架，仅数量 / 行列 / 间距变化。详见 §8。

## 槽位图（slot graph）

pattern: mixed（root tray/shell 为 ROOT，盖 / 抽屉挂到它 = parallel_children 风格的固定 named slots；pan × N = multiplicity 轴挂 root 或 drawer）

```
[ROOT, 坐地 z≈0, 扁平躺放]
case_footprint = rounded_rect / square_rounded:  base (=_base_tray_mesh + base_frame + cell_grid)
case_footprint = round_disc:                     base (=_disc tray + _ring frame + cell_grid + 圆 pan ring)

closure_mechanism 决定 ROOT 名 + 活动盖拓扑：

 ├── closure = rear_hinge_flip_lid:   ROOT=base
 │      base --[base_to_lid: REVOLUTE axis=-X @ 后 rim (0, +DEP_Y/2, HINGE_Z)]--> lid (mirror 贴 lid 内面 well)
 │      pan × N 挂 base（_pan_centers 网格/ring → pan_{...}）
 │
 ├── closure = slide_out_drawer:      ROOT=shell（中空 sleeve，mirror 贴 shell 内顶 ceiling）
 │      shell --[shell_to_drawer: PRISMATIC axis=+X @ origin]--> drawer
 │      pan × N 挂 drawer（drawer tray 上 _pan_centers → pan_{...}）
 │
 └── closure = flip_lid_with_clasp:   ROOT=base
        base --[base_to_lid: REVOLUTE axis=-X @ 后 rim]--> lid (mirror + lid_lip 前缘 catch)
        base --[base_to_clasp: REVOLUTE axis=+X @ 前缘 (0, -DEP_Y/2, CLASP_PIVOT_Z)]--> clasp (arm+hook 锁 lid_lip)
        pan × N 挂 base
```

接口点位与 joint 语义：
- **翻盖接口（rear_hinge_flip_lid / flip_lid_with_clasp）**：`base_to_lid` origin 落在后 rim 中心 `(0, +DEP_Y/2, HINGE_Z=BASE_H+LID_H/2)`，axis=(-1,0,0) REVOLUTE，q=0 闭合盖座 base rim、0→110°（`math.radians(110)`）上翻；hinge knuckles 是 base 上 grounded silver visual（parent L295-302）。lid 件 mesh 在 lid-local frame（origin 在 hinge），slab 向 -Y 偏 DEP_Y/2、向 +Z 偏 LID_H/2 摆位（parent L249-258）。mirror 贴 lid 内面 well（top < slab top，parent L281-285）。
- **抽屉接口（slide_out_drawer）**：`shell_to_drawer` origin 在原点 `(0,0,0)`，axis=(1,0,0) PRISMATIC，q=0 drawer 收回坐 shell 内 / 0→0.08m 抽出（SLIDE_UPPER L97）。shell 是五壁板 union 的中空 sleeve（`_shell_body_mesh` L113-146），mirror 贴 shell 内顶（mirror top < shell body top，L398-409）。pan 挂 drawer tray（`_drawer_body_mesh` tray+前 cap，L187-202）。
- **卡扣接口（flip_lid_with_clasp）**：`base_to_clasp` origin 在前缘 `(0, -DEP_Y/2, CLASP_PIVOT_Z=BASE_H+0.003)`，axis=(1,0,0) REVOLUTE，q=0 锁（hook 挂 `lid_lip`，XY+Z overlap L568-580）/ 0→85°（`math.radians(85)`）解锁（hook 离 lip，L583-594）。clasp bosses 是 base 上 grounded silver ears（L315-328）；`lid_lip` 是 lid 前-top 缘 catch ridge（L196-210）。
- **pan 接口（multiplicity）**：pan 为 `base`/`drawer` 的 `base.visual(...)`/`drawer.visual(...)`（无独立 joint，随 root/drawer 运动），坐各自 cell pocket 内 recessed（pan top ≤ cell_grid rim，parent test L359-372）。
- **mating policy**：盖盖 / 抽屉 / 卡扣均为 captured / 友配重叠（盖 frame 座 base rim、drawer body 套 shell sleeve、clasp hook 挂 lid_lip），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 rim / hinge / 前缘硬件）+ element-scoped `allow_overlap`（见各样本 run_tests 的 `ctx.allow_overlap`：lid_frame↔base_frame、drawer_body↔shell_body、cell_grid↔shell_body、clasp_lever↔lid_lip/lid_slab）守 overlap。
- **rest pose**：所有盖 q=0 闭合 / 抽屉收回 / 卡扣锁定；lid 上翻 / drawer 抽出 / clasp 解锁为 viewer 目检的活动语义。
- **互斥 / 可选**：closure_mechanism 各候选互斥（一次只一种盖机构）；slide_out_drawer 把 root 改名 `shell` 且 pan 挂 `drawer`（mirror 移 shell），其余两种 root=`base` 且 pan 挂 `base`（mirror 在 lid）。

## 每槽位 Module Emits / Interfaces

### Slot A / case_footprint（ROOT tray，决定 mesh + pan 排布器）
| emits | 描述 | 来源 |
|---|---|---|
| parts | rounded_rect/square: `base`（visual: `base_tray` + `base_frame` + `cell_grid`）/ round: `base`（disc tray + ring frame + disc cell_grid）| parent `_base_tray_mesh` L94-109 / square `_cell_grid_mesh` L138-162 / round `_disc`/`_ring`/`_base_tray_mesh` L72-100 |
| internal joints | 无（root tray 本身无活动件）| — |
| upstream interface | 坐地 z≈0（root）| parent BASE_H L37 |
| downstream interface | 后 rim 中心（翻盖 joint parent 接口）/ 原点（抽屉 joint）/ 前缘（clasp joint）；pan 排布器 `_pan_centers`（网格 vs 径向 ring）| parent HINGE_Y/HINGE_Z L67-69 / round `_pan_centers` L103-111 |

### Slot B / closure_mechanism（每候选发射对应活动盖 + 决定 root 名 / mirror 承载）
| emits | 描述 | 来源 |
|---|---|---|
| parts | flip: `lid`(slab+frame+mirror) / drawer: `shell`(sleeve+mirror)+`drawer`(tray+cap+grip) / clasp: `lid`(+`lid_lip`)+`clasp`(lever)+clasp bosses | parent `lid` L244-285 / drawer `shell`/`drawer` L271-312 / clasp `lid`/`clasp` L333-395 |
| internal joints | `base_to_lid` REVOLUTE -X（flip）/ `shell_to_drawer` PRISMATIC +X（drawer）/ `base_to_lid` REVOLUTE -X + `base_to_clasp` REVOLUTE +X（clasp）| parent L307-320 / drawer L317-330 / clasp L402-435 |
| upstream interface | 挂 root（base/shell）后 rim / 原点 / 前缘 | parent L312 / drawer L322 / clasp L407/L427 |
| downstream interface | mirror 承载面：lid 内面 well（flip/clasp）/ shell 内顶 ceiling（drawer）| parent L281-285 / drawer `_mirror_plate_mesh` L175-184 |

### Slot C / pan_count（multiplicity，挂 base 或 drawer 的循环 visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：N 个 `pan_{row}_{col}`（矩形）/ `pan_{i}`（圆形）为 base/drawer 的循环 `base.visual(...)`，坐各自 cell pocket | parent loop L222-229 / round loop L184-190 / drawer loop L299-306 |
| internal joints | 无（pan 随 root/drawer 运动，无独立 joint，符合 §inline copied 件规则）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_footprint | enum | rounded_rect / square_rounded / round_disc | rounded_rect | choice | deterministic procedural sampler 选 | module table |
| closure_mechanism | enum | rear_hinge_flip_lid / slide_out_drawer / flip_lid_with_clasp | rear_hinge_flip_lid | choice | sampler 选 | module table |
| pan_count | int (multiplicity) | [2, 24]（见 §8）| 8 | conditional | 网格行列由 N 因式分解（矩形）/ 径向 ring（圆形）；按 footprint 解析行列与间距 | multiplicity 轴 / `_pan_centers` |
| palette_style | enum | classic_skin_silver / rose_gold_nude / matte_black_jewel / clear_acrylic_pastel / warm_brass_cream / glossy_ivory_gold / pearl_blush_silver / marble_white_rosegold / frosted_mint_silver / graphite_silver_metal（9 colorway，含显式 finish 维度）| classic_skin_silver | palette | palette only，**不计入 slot_choice**；选 case/frame/pan 配色 + finish 质感 | §palette 表 |
| case_length_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 LEN_X（矩形）/ RADIUS（圆）→ 影响可容 pan 网格，clamp | parent LEN_X L35 / round RADIUS L34 |
| case_depth_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 DEP_Y（矩形）；round_disc 时锁定 = case_length_scale 保圆 | parent DEP_Y L36 |
| case_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 BASE_H/LID_H/SHELL_H → HINGE_Z / 抽屉腔高，clamp | parent BASE_H/LID_H L37-38 / drawer SHELL_H L31 |
| pan_size_scale | float | derived | 1.0 | equation | `PAN_SX/PAN_SY = f(footprint_inner, rows, cols, gap)`；pan 尺寸由可用网格区与 N 派生，不独立采样 | parent PAN_SX/SY L49-50 / n4 L48-49 / n12 L48-49 |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 `shell_to_drawer` SLIDE_UPPER + hinge/clasp upper limit，clamp | drawer SLIDE_UPPER L97 / parent upper L317 / clasp upper L433 |
| (—) | constraint | — | — | inequality | pan 装得下：`rows·(PAN_SY+gap) ≤ inner_depth` 且 `cols·(PAN_SX+gap) ≤ inner_len`（圆：`N·pan_arc ≤ 2π·ring_r`）；违反则缩 pan_size 或减 rows/cols 重排 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 盖罩配合：`lid_outer ≤ base_outer + proud`（flip）/ `drawer_body ≤ shell_cavity − clear`（drawer）；违反按比例回缩 | 接口 / clearance |
| (—) | constraint | — | — | conditional | round_disc ⇒ pan 排布用径向 ring（PAN_COUNT），矩形 footprint ⇒ ROWS×COLS 网格；`case_depth_scale` 在 round 时锁定 = `case_length_scale` | footprint 派生 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`pan_size_scale` 为 equation（pan 尺寸由 footprint 内腔 × 网格 × gap 派生，保 pan 装得下且 recessed）。`case_depth_scale` 在 round_disc 时按 conditional 锁定 = case_length_scale（保圆）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 case_footprint / closure_mechanism 的拓扑。

### palette_style 配色（采纳自 5★ 源色板，每 seed 采样）

> 列结构沿用 5★（case body / frame·cell_grid / pan 主色族 / mirror·accent），**新增一列 `finish 材质质感`** 作为显式材质-finish 维度（matte / high-gloss / metallic / pearlescent-iridescent / clear-acrylic / rose-gold·brass·silver / soft-touch / marble-print）。finish 只描述同一组 rgba 上叠加的真实彩妆盒表面质感语义（哑光 / 高光 / 金属 / 珠光虹彩 / 透明亚克力 / 玫瑰金·黄铜·银 / 软触橡胶漆 / 大理石纹印刷），不改拓扑、不改 slot、不改任何尺寸/joint。

| palette_style | case body | frame / cell_grid | pan 主色族 | mirror / accent | finish 材质质感 | 来源 |
|---|---|---|---|---|---|---|
| classic_skin_silver（基线）| 深炭黑 `(0.10,0.10,0.12)` | silver `(0.78,0.80,0.83)` | 肤色 + 校色 pastel（beige/tan/green/peach/lavender）| mirror_glass `(0.82,0.88,0.92)` / label_white | **soft-touch**（case 软触哑光黑）+ silver frame 微光 | parent PAN_COLORS L73-82 + materials L188-192 |
| rose_gold_nude | 香槟米白 | rose-gold `(0.83,0.62,0.55)` 暖金 frame | nude 裸色族（深浅米/驼/裸粉）| mirror_glass / 米白 label | **rose-gold metallic**（frame 玫瑰金抛光）+ satin case | 改 frame_silver→rose-gold，pan 取 n12 deep-tan/caramel/ivory L80-85 |
| matte_black_jewel | 哑光纯黑 | 黑 frame + 银细边 | 珠光宝石色（n12 的深色族 espresso/caramel + 校色）| mirror_glass / 银 accent | **matte**（纯哑光黑）+ silver hairline 高光细边 | n12 PAN_COLORS 深色档 L80-85 |
| clear_acrylic_pastel | 半透明 `lid_clear (0.86,0.90,0.93,0.55)` 盒体 | silver 细 frame | 全 pastel 校色（green/lavender/peach/fair）| mirror_glass | **clear acrylic**（盒体透明亚克力 α≈0.55）| parent clear material L191 + pastel pan L75-79 |
| warm_brass_cream | 奶油米 case | brass `(0.72,0.62,0.30)` 暖铜 frame | 暖肤色（tan/peach/medium-peach/natural-beige）| mirror_glass / 奶白 label | **brass metallic**（frame 黄铜暖金）+ cream matte case | square pan L73-83 + 暖色 frame 替换 |
| glossy_ivory_gold（新增）| 高光象牙白 `(0.96,0.86,0.74)` | 暖金 `(0.80,0.66,0.34)` frame | 暖肤色（ivory/natural-beige/caramel/light-beige）| mirror_glass / 金 accent | **high-gloss**（象牙白镜面漆）+ gold metallic frame | n12 ivory/natural-beige/caramel L81-84 + 暖金 frame |
| pearl_blush_silver（新增）| 珠光裸粉 `(0.95,0.84,0.82)` | silver `(0.78,0.80,0.83)` | 裸粉 pastel（fair/peach/lavender/light-beige）| mirror_glass / 珠白 label | **pearlescent / iridescent**（盒体珠光虹彩）+ silver frame | parent fair/peach/lavender L77-79 + pastel pan |
| marble_white_rosegold（新增）| 白底大理石纹 `(0.93,0.92,0.90)` + 灰纹理 | rose-gold `(0.83,0.62,0.55)` frame | 暖肤色（light-beige/warm-tan/natural-beige/deep-tan）| mirror_glass / rose-gold accent | **marble-print**（盒体大理石纹印刷）+ rose-gold metallic frame | parent/n12 暖肤 PAN_COLORS + rose-gold frame |
| frosted_mint_silver（新增）| 半透磨砂薄荷 `(0.80,0.90,0.85,0.60)` | silver 细 frame | 校色族（green/lavender/peach/fair）| mirror_glass | **clear acrylic（磨砂 frosted）**（盒体磨砂半透） | parent green/lavender/peach 校色 L75-79 + frosted clear |
| graphite_silver_metal（新增）| 拉丝石墨灰 `(0.32,0.33,0.36)` | bright-silver `(0.85,0.86,0.88)` | 中性肤色（warm-tan/medium-peach/deep-tan/caramel）| mirror_glass / silver accent | **metallic**（铝合金拉丝）+ bright-silver hairline | parent/n12 中性肤 PAN_COLORS + 金属拉丝 case |

palette_style 仅改材质 rgba + finish 质感语义（不计 slot_choice，不改拓扑/slot/joint/尺寸）；**9 个 colorway** 锚定 5★ 样本的 PAN_COLORS / materials（深炭黑 / silver / mirror_glass / lid_clear / 肤色族 pastel），新增的 ivory-gold / pearl-blush / marble / frosted-mint / graphite 为该类真实彩妆盒词汇内的合理推断配色；finish 维度覆盖 matte / high-gloss / metallic / pearlescent-iridescent / clear-acrylic / rose-gold·brass·silver / soft-touch / marble-print 八种真实质感。按 seed `rng.choice(PALETTE_STYLES)` 采样。

## Multiplicity / Copy Logic

本类有 **1 根 multiplicity 轴**：pan_count（同构 concealer pan × N）。

- `count_param`：`pan_count`（矩形 footprint 由 PAN_ROWS × PAN_COLS 网格因式分解派生；圆形 footprint 由 PAN_COUNT 径向 ring 派生）。
- `N_range`：**[2, 24]**（真实彩妆 / 遮瑕盘单格到约 24 格；测试偏小、产品全程）。样本已覆盖 N ∈ {4, 8, 12}。
- sampling domain（权重档）：小 N 高频（N ∈ {4,6,8,9} 最常见，对应 2x2/2x3/2x4/3x3/ring-6），中 N 中频（N ∈ {10,12,15,16}），大 N 稀有（N ∈ {18,20,24}）。矩形按 `N → 最接近正方/合 footprint 长宽比的 (rows,cols)` 因式分解（如 8→2x4、9→3x3、12→3x4、24→4x6）；圆形按 N 均布于单 ring（N≤8）或双 ring（N>8）。
- copied object：单个 concealer pan（共享 `_pan_mesh()` rounded-box 凹腔膏体 / `_disc` 圆饼）。
- naming：矩形 `pan_{row}_{col}`（循环 `for (row,col,cx,cy) in _pan_centers()`）；圆形 `pan_{i}`（循环 `for (i,cx,cy) in _pan_centers()`）。
- placement：矩形规则网格（X/Y 等距，`_pan_centers` 居中 + 向前缘 -Y 偏移留 label 区）；圆形径向 ring（`cx=ring_r·cos θ, cy=ring_r·sin θ`）。每 pan 坐自己的 cell pocket（`_cell_grid_mesh` 逐 pan cut pocket），recessed 不凸 rim。
- joint policy：统一为 base/drawer 的 `base.visual(...)`（无独立 joint，随 root/drawer 运动）；非装饰但不可动的复制件，符合 inline copied 规则。
- source/gating：N 上限随 footprint × scale 派生（`rows·(PAN_SY+gap) ≤ inner_depth` 等不等式在 resolve 解析）；装不下时缩 pan_size 或减档，不发射悬空 pan。

## 拓扑多样性审计

总组合数：case_footprint(3) × closure_mechanism(3) × pan_count(N 采样档，取 ~6 个代表档 {4,6,8,9,12,16/24}) = 3 × 3 × 6 = **54**。
（仅 case_footprint × closure_mechanism = **9**；叠 pan_count N 档后 ≫ 10。）

理由：case_footprint(3) × closure_mechanism(3) 的笛卡尔积即 9 distinct（不同 primitive 家族 disc/box + 不同 joint 拓扑 REVOLUTE/PRISMATIC/双 REVOLUTE + 不同 part count 2/2/3）；再叠 pan_count multiplicity 轴（N 改变 pan 复制件数 / 网格行列 / part 总数）后，topology distinct（按 part tree + joint set + pan 数签名）远超 10。closure_mechanism 引入 REVOLUTE -X（翻盖）/ PRISMATIC +X（抽屉，root 改名 shell + mirror 移位）/ REVOLUTE+REVOLUTE（翻盖+卡扣，2 活动件 3 part）等真实结构差异。slot_choices 编入 (case_footprint, closure_mechanism, pan_count_signature) 三轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（case_footprint × closure_mechanism）+ 加权采样 pan_count（小 N 偏多、大 N 稀有），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 派生处理边界组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 ~40-54（9 个 footprint×closure 组合 × 多 N 档；受真实词汇表约束的轴是 footprint(3)/closure(3)，N 档撑开剩余）。低于 300 的原因：本小类真实结构词汇就是 3 footprint × 3 closure × N 档，参考图仅 1 张，square/round 已是最稳扩展；不强行注水发明形态（与源 map §排除项一致）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（case_length / case_depth / case_height / pan_size(equation) / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`pan_size_scale` 为 equation（由 footprint 内腔 × 网格 × N 派生）；`case_depth_scale` 在 round_disc 时 conditional 锁定 = case_length_scale。pan 装下不等式 + 盖罩配合不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 joint origin（后 rim / 原点 / 前缘）、盖罩 / 抽屉 / 卡扣配合、pan recessed 位置或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` case_footprint × closure_mechanism（9 全正交），加权采 pan_count，再 uniform 各 scale + palette_style | slot_choices_for_seed 含 (footprint, closure, pan_count_sig) 且与 build 一致 |
| compatibility matrix | (1) round_disc 用径向 ring pan 排布（PAN_COUNT，N≤8 单 ring / N>8 双 ring）；矩形用 ROWS×COLS 网格。(2) slide_out_drawer ⇒ root 改名 `shell`、pan 挂 `drawer`、mirror 移 shell 内顶；其余 closure root=`base`、pan 挂 `base`、mirror 在 lid（resolve 解析承载，不 gate 掉）。(3) 各 closure 互斥。(4) 大 N（>16）+ 小 case_length_scale ⇒ 缩 pan_size 或减档（不等式回缩，不悬空）。(5) 9 个 footprint×closure 组合全合法（无硬 gate-out）| 无 floating / collision / pan 凸 rim / lid 穿盒 / drawer 脱壳 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；pan_size equation 由 footprint×N 派生；case_depth conditional 锁圆 | 比例变化不破坏 joint origin / 盖罩配合 / pan recessed / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 盖动作 / 抽屉抽出 / 卡扣解锁 / pan recessed / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_footprint | 3 | yes | yes | rounded_rect / square_rounded（box+fillet）+ round_disc（disc/ring）|
| closure_mechanism | 3 | yes | yes | flip(REV -X) / drawer(PRIS +X, root=shell) / flip+clasp(REV+REV, 3 part 2 joint) |
| pan_count (multiplicity) | N∈[2,24]（样本 {4,8,12}）| yes | yes | 矩形网格因式分解 / 圆形径向 ring |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (case_footprint, closure_mechanism, pan_count_signature) 三轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（含 pan_count 加权采样）
- `resolve_config` 各 scale clamp 到声明范围；pan_size equation 由 footprint×N 派生；case_depth conditional 在 round 锁圆；pan 装下不等式 + 盖罩 / 抽屉配合不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：9 个 footprint×closure 全合法（无硬 gate-out）；round 用径向 ring、矩形用网格；drawer 时 root=shell / pan→drawer / mirror→shell
- 连续 scale clamp 后不破坏 joint origin（后 rim / 原点 / 前缘）/ 盖罩配合 / pan recessed / 坐地 / 类别身份
- 关键 joint：flip `base_to_lid` REVOLUTE 绕 -X (abs(axis[0])>0.99) origin 后 rim；drawer `shell_to_drawer` PRISMATIC +X (abs(axis[0])>0.99)；clasp +`base_to_clasp` REVOLUTE +X 前缘 有限 limit(85°)；每 closure ≥1 非 fixed joint
- multiplicity：N 个 `pan_{...}` 循环发射（共享 `_pan_mesh`），坐各自 cell pocket recessed（pan top ≤ cell_grid rim），naming/placement 按矩形网格 / 圆形 ring policy
- captured-fit：element-scoped `allow_overlap`（lid_frame↔base_frame / drawer_body↔shell_body / cell_grid↔shell_body / clasp_lever↔lid_lip / clasp_lever↔lid_slab）
- grandfather：盖 / 抽屉 / 卡扣 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把容器做成竖立单腔瓶 / 罐 / 管（细颈瓶身、旋升口红、竖立化妆罐）→ 失类别身份；本类必须扁平躺放 + 多 pan 盘 + 镜面盖 / 抽屉。
- pan 凸出 cell rim / 浮在 tray 上方而非坐 cell pocket recessed → `pan top ≤ cell_grid rim` FAIL（parent test L359-372）。
- 翻盖 joint origin 放盒底 / 任意点而非后 rim 真实 hinge 硬件；抽屉 joint 非 +X 原点；clasp 非前缘 +X → `fail_if_articulation_origin_far_from_geometry` FAIL。
- closure rest pose 设成张开 / 抽出 / 解锁而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- slide_out_drawer 时把 pan 挂 shell（应挂 drawer）或 mirror 留 lid（应移 shell 内顶）→ 抽屉抽出后 pan 不跟随 / mirror 错位。
- round_disc 用矩形网格 pan 排布（应径向 ring）或 box 占位体当圆盘 → 失圆 footprint（round test dx≈dy FAIL，L286-305）。
- 给盖 / 抽屉 / 卡扣 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 大 N 装不下仍硬发射致 pan 互穿 / 出 tray 边界 → pan 装下不等式应在 resolve 缩 pan_size 或减档。

## 与相邻类别的边界

- 不该混入：**container_lipstick 口红 / 唇膏**（细长竖立旋升管，单 swivel/screw 轴）——理由：lipstick 是竖立细管 + 旋升膏体，cosmetic compact 是扁平躺放多 pan 盘。
- 不该混入：**container_bottle_serum 精华液瓶**（细颈 dropper / pump 瓶，竖立单腔）——理由：serum 是竖立瓶身 + 滴管/泵头，cosmetic 是扁平盘 + 镜面盖。
- 不该混入：**container_jar 化妆罐 / 储物罐**（圆胖竖立罐 + 螺纹 / 翻盖单腔）——理由：jar 是竖立单腔罐（wider-than-tall 但仍直立装一坨膏），cosmetic 是躺放多 pan 盘（grid + mirror + 一格一格）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。3 footprint × 3 closure × N(pan_count) multiplicity 轴；footprint×closure=9 clears ，叠 N 档 ~40-54。closure 含 REVOLUTE -X 翻盖 / PRISMATIC +X 抽屉（root=shell, mirror 移顶, pan 挂 drawer）/ 翻盖+卡扣双 REVOLUTE（3 part 2 joint）。pan_count [2,24] 真实彩妆域。palette_style 9 colorway（含显式 finish 维度：matte/high-gloss/metallic/pearlescent-iridescent/clear-acrylic/rose-gold·brass·silver/soft-touch/marble-print）锚定 5★ PAN_COLORS/materials + 真实推断配色。与 lipstick/bottle_serum/jar 边界：扁平躺放多 pan 盘 vs 竖立单腔瓶罐管。|

## 模板实现备注（可选）

- 共享 helper：`_rounded_box(sx,sy,sz,r)`（矩形 footprint，box+`fillet("|Z")`+cut）+ `_disc`/`_ring`（圆 footprint）+ `_pan_centers(footprint, rows, cols / pan_count)`（矩形网格 vs 径向 ring，分支返回 `(row,col,cx,cy)` 或 `(i,cx,cy)`）+ `_pan_mesh()`（rounded-box / disc 膏体）+ `_cell_grid_mesh()`（逐 pan cut pocket，bbox-from-centers 自适应，源 square L138-162）全 module 公用。
- closure 分支：rear_hinge_flip_lid / flip_lid_with_clasp ⇒ root=`base`、mirror 贴 lid 内面 well；slide_out_drawer ⇒ root=`shell`（五壁板 union sleeve，`_shell_body_mesh` L113-146）、pan 挂 `drawer`、mirror 贴 shell 内顶（`_mirror_plate_mesh` L175-184）。clasp 分支额外发射 `clasp` 件（`_clasp_lever_mesh` L213-247）+ `lid_lip`（L196-210）+ clasp bosses（L315-328）+ `base_to_clasp` REVOLUTE +X。
- multiplicity：`_pan_centers` 按 resolve 出的 (rows, cols) 或 (pan_count, ring 层数) 发射；N 由 footprint × scale 不等式 clamp（装不下缩 pan_size 或减档）。
- captured-fit overlap：`run_container_cosmetic_tests` 里复刻各样本 allow_overlap：`lid_frame↔base_frame`（flip/clasp）、`drawer_body↔shell_body` + `cell_grid↔shell_body`（drawer）、`clasp_lever↔lid_lip` + `clasp_lever↔lid_slab`（clasp）。
- pan_size equation：`resolve_config` 由 `inner_len/inner_depth × (rows,cols) × gap` 派生 `PAN_SX/PAN_SY`，保 pan 装得下且 recessed（pan top ≤ cell rim）。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类的 parallel_children + captured-fit grandfather + palette + clamp 骨架）；含 multiplicity 轴的模板（如 fence_cascade / shopping_bucket 类的 per-axis 加权 N 采样 + clamp + sweep 上限）作 pan_count 采样参考。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | rounded_rect + rear_hinge_flip_lid + n8_pans_2x4（parent 基线）| rec_concealer-..._f124e974 | `_rounded_box` L85-91 / `_base_tray_mesh` L94-109 / `_pan_centers` L112-125 / `_pan_mesh` L128-132 / `_cell_grid_mesh` L135-156 / `_lid_slab_mesh` L171-182 / `base_to_lid` REVOLUTE L307-320 / mirror L281-285 | 长方盒 footprint 基线 + 后铰翻盖镜面盖 + 2x4 pan 网格 + cell_grid 隔断 |
| S2 | A | square_rounded | rec_container_cosmetic_var_square_body | `_rounded_box` L86-92 / `_base_tray_mesh` L95-110 / `_pan_centers` L113-128 / `_cell_grid_mesh`（bbox-from-centers）L138-162 / L/D test L378-386 | 近正方形 footprint + bbox 自适应 cell_grid |
| S3 | A/C | round_disc + 径向 pan ring | rec_container_cosmetic_var_round_body | `_disc` L72-74 / `_ring` L77-85 / `_base_tray_mesh` L88-100 / `_pan_centers`（径向）L103-111 / `_pan_mesh`（disc）L114-120 / `_cell_grid_mesh`（disc）L123-137 / round test L286-305 | 圆盘 footprint + 圆 ring frame + 径向圆饼 pan 排布器 |
| S4 | B | slide_out_drawer | rec_container_cosmetic_var_slide_drawer | `_shell_body_mesh` L113-146 / `_mirror_plate_mesh` L175-184 / `_drawer_body_mesh` L187-202 / `shell_to_drawer` PRISMATIC L317-330 / allow_overlap L439-448 | 中空 sleeve shell + PRISMATIC 抽屉 + mirror 移 shell 内顶 + pan 挂 drawer |
| S5 | B | flip_lid_with_clasp | rec_container_cosmetic_var_clasp_latch_lid | `_clasp_lever_mesh` L213-247 / `_lid_lip_mesh` L196-210 / clasp bosses L315-328 / `base_to_lid` REVOLUTE L402-415 / `base_to_clasp` REVOLUTE +X L422-435 / allow_overlap L608-626 | 后铰翻盖 + 前缘可动卡扣（2 joint / 3 part） |
| S6 | C | n4_pans_2x2 | rec_container_cosmetic_var_n4_pans | PAN_COLS/ROWS L46-47 / `_pan_centers` L106-119 / pan loop L219-226 / colors L71-76 | multiplicity N=4（2x2）网格 + pan/gap 适配 |
| S7 | C | n12_pans_3x4 + palette 扩色 | rec_container_cosmetic_var_n12_pans | PAN_COLS/ROWS L46-47 / PAN_SY 适配 L49 / `_pan_centers` L115-128 / pan loop L228-235 / PAN_COLORS（12 色含 deep/caramel/ivory/espresso）L72-85 / 3-row test L378-403 | multiplicity N=12（3x4）+ palette_style 深色 / nude / jewel 配色源 |
