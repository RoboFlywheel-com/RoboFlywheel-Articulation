# Modular Spec — Urban Environment / bucket1 (fire bucket)

## 元信息
| 项 | 值 |
|---|---|
| slug | `bucket1` |
| template path | `agent/templates/Urban_Environment_bucket1.py` |
| test path (optional) | `tests/agent/test_bucket1_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`parallel_children`：root 是 `bucket` 体（revolved 薄壳 + 卷边 rim），handle/mount/band 三个独立结构层各自挂在 bucket 上或位于其上方。bail handle 是定义性 REVOLUTE 子件；mount 可把 bucket 反挂为 FIXED 子件（wall bracket），band 是 multiplicity 复制轴。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (2 parents + 9 single-axis variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：

- **两个 parent 只在 body profile 上不同**（apex-down cone vs flat-bottom tapered cylinder）；rim、lugs、rivets、bail wire、REVOLUTE 关节四者完全一致。每个 parent 用 `for sgn,tag in ((+1,"pos"),(-1,"neg"))` 循环对称发射两个 pivot lug + rivet；bail 是单条 `tube_from_spline_points` spline；body 是 `LatheGeometry.from_shell_profiles` 旋转薄壳。
- **bail REVOLUTE = 不变的定义关节**：joint origin 恰在 lug pivot 轴 `(0,0,LUG_Z)`，axis `(0,1,0)`（±Y 直径线），limits `±100°`，q=0 直立、±95° 摆到侧面。所有 body/mount/band 变体都原样保留这个关节。
- **没有任何 parent 含 reinforcing band**（只有单个 rolled-rim torus）；band 变体新增的 hoop 必须由 `for i in range(n)` 共享 helper 循环发射，半径按各 band 高度的局部 wall radius 计算（tapered 线性插值），不得手写。
- handle 变体把 bail 替换为**等价真实 non-fixed 关节**：fixed_side_grips 保留一个 fold-flat REVOLUTE（axis X），no_handle 用 hinged lid REVOLUTE（rim-tangent axis Y）。绝不退化成纯 FIXED。
- mount 变体：wall_bracket 用 root=`bracket`（背板+bolt holes+cradle ring/arm），`bracket_to_bucket` FIXED，bail 仍 revolute；hook_ring 在 rim 上方加四臂+plate+shank+torus 吊环（全部 inline bucket visual，纯装饰）。
- 颜色：body red_metal `(0.62,0.09,0.08)`、steel wire `(0.72,0.74,0.77)`，几乎所有变体一致 → palette_style 是安全的纯材质轴（不当结构轴）。

## 核心身份

bucket1 = **红漆薄板钢消防桶 / 火桶（fire bucket / fire pail）**。物理结构恒为：(1) 一个 hollow thin-wall **revolved 旋转薄壳**桶体（cone-pointed / tapered / straight / hemispherical），(2) 顶口一圈 **rolled rim**（卷边 torus，身份不变量，绝不去掉），(3) rim 两侧 ±Y 对称的 **riveted pivot lugs**，(4) 一根 **steel-wire BAIL 提手**，绕 ±Y lug 直径线做 **REVOLUTE** 摆动——bail swing REVOLUTE 是**定义性关节**，每个变体必须保留它或用等价真实 non-fixed 关节（fold-flat grip / hinged lid）替换。可选 wall bracket / hook ring 挂载。默认成熟域：手提救火沙桶尺度（高 ~0.25–0.40 m，口径 ~0.16–0.28 m）。

不该混入相邻类别：

- **bucket2（木桶 / wooden keg / cooper bucket）**：bucket2 是木板条 (stave) + 多道金属 hoop 箍的木质容器，常是腰鼓形/直桶，无 sheet-metal 旋转薄壳、无 red paint、无 bail-wire REVOLUTE 提手。bucket1 是单片冲压钢薄壳 + 卷边 + 钢丝 bail，材质与构造完全不同 → 不混入木板拼接体或多道紧箍 hoop（bucket1 的 band 是稀疏 reinforcing rib，不是结构紧箍）。
- **Fire_Extinguisher（灭火器）**：灭火器是封闭加压钢瓶 + 顶部阀门/喷管/压力表/扳机手柄，是密封受压容器；bucket1 是**开口**桶 + 卷边 + 摆动 bail，无阀门无喷嘴无压力表 → 不混入封顶瓶、squeeze handle、hose/nozzle。

## 槽位 + 候选模块表

### Slot A：body profile（旋转薄壳轮廓 — root part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `conical_pointed` | rec_red-...conical...8f71e941 | L60-L81（`_conical_shell_mesh`）, build L91-L126 | eligible if compatible | apex-down 尖锥薄壳，z=0 是 apex 点，无平底，不能直立（只能挂）；outer `[(apex_r,0),(top_r*.5,h*.5),(top_r,h)]` |
| `tapered_cylinder` | rec_red-...tapered-cy...c25e8986 | L58-L87（`_revolved_shell_mesh`）, build L96-L137 | eligible if compatible | 上宽下窄锥台 + 平底盘（`bottom_t`），可直立；`top_r>bot_r` |
| `straight_pail` | rec_bucket1_var_body_straight_pail | L58-L88（同 `_revolved_shell_mesh`，`BOT_R==TOP_R`）, build L91-L107 | eligible if compatible | 直壁不锥圆筒，top_r==bot_r，平底直立 |
| `hemispherical_bowl` | rec_bucket1_var_body_hemispherical | L60-L107（`_bowl_outer_profile`/`_bowl_inner_profile`/`_bowl_shell_mesh`）, `expected_outer_radius` L110-L120 | eligible if compatible | 四分之一圆弧曲线旋转半球碗，曲率非线性增长，小平底 `BOTTOM_FLAT_R` 可坐 |
| `deep_narrow_cone` | rec_bucket1_var_body_deep_cone | L61-L82（`_conical_shell_mesh`，`TOP_R=0.08,BODY_H=0.40`）, build L85-L111 | eligible if compatible | 高瘦漏斗锥（h:d≈2.5，parent≈0.93），比 parent 更尖更深 |

注：Slot A 实现上是两族 helper —— cone 族（`_conical_shell_mesh`，参数 top_r/height）与 lathe 族（`_revolved_shell_mesh`，参数 top_r/bot_r/height）+ bowl 族（弧线 profile）。`tapered_cylinder` 与 `straight_pail` 是同 helper 不同 `bot_r`，但 `straight_pail` 因 top==bot 触发不同的 taper 测试断言（top-wider 检查反转），算独立 topology 类。

### Slot B：handle（搬运机构 — bail REVOLUTE 家族 = 定义性关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `swing_bail_revolute` | both parents | conical L128-L166 / tapered L139-L183 | eligible if compatible | 单条 steel-wire bail spline（9 控制点 arch），`bucket_to_handle` REVOLUTE，origin `(0,0,LUG_Z)`，axis `(0,1,0)`，limits ±100°；rim 两侧 lug+rivet 由 ±Y 循环发射 |
| `fixed_side_grips` | rec_bucket1_var_handle_fixed_grips | `_make_dloop_grip_mesh` L91-L118, build/loop L150-L201, joint L206-L219 | eligible if compatible | 两个 ±Y D-loop side grip（`for i in range(2)`）；i=0 是 fold-flat REVOLUTE child part（axis `(1,0,0)`，limits 0–85°），i=1 是 inline 固定 grip；保留**一个**真实 non-fixed 关节 |
| `hinged_lid` (no_bail) | rec_bucket1_var_handle_no_handle | hinge ears L117-L139, lid part L147-L200, `bucket_to_lid` REVOLUTE L202-L218 | eligible if compatible | 无 bail/lugs；+X rim 加 hinge ears+barrel，flat 圆盘 lid（disk+rim+strap+knob）绕 rim-tangent Y 轴 REVOLUTE（limits 0–110°）开合；lid 是新的定义性 non-fixed 关节 |

降级说明：Slot B 仅 3 个 candidate（不到 4-6），但每个都是结构不同的真实运动家族（bail swing / fold-flat grip / hinged lid），样本池已穷尽 5★ 中的全部 non-fixed handle 拓扑；不强凑装饰变体。≥3 满足硬约束。

### Slot C：mounting（如何支撑/悬挂）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `free_standing` | both parents | tapered 平底 L72-L85 / cone 挂吊（无附件） | eligible if compatible | 无附加 mount；平底坐地（lathe 族）或靠 bail 悬挂（cone 族） |
| `wall_bracket` | rec_bucket1_var_mount_wall_bracket | 常量 L59-L83, `_cradle_ring_mesh` L112-L127, bracket build L137-L181, `bracket_to_bucket` FIXED L255-L262 | eligible if compatible | root=`bracket`：竖直背板 `back_plate`（2 个 `bolt_hole_i`）+ 340° `cradle_ring`（在 38% 高处抱住桶体）+ `cradle_arm`；`bracket_to_bucket` FIXED，bail 仍 REVOLUTE |
| `hook_ring` | rec_bucket1_var_mount_hook_ring | 常量 L59-L68, mount build L133-L185 | eligible if compatible | rim 上方对称轴加四 `hook_arm_i`（`for i in range(4)`，90° 间隔）+ `hook_plate` + `hook_shank` + `hook_ring` torus 吊环；全部 inline bucket visual（纯装饰，无新关节） |

### Slot D：rim / band detail（加强 hoop ribs — distinct-N 复制轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rolled_rim_only` | both parents | rim L96-L100 (cone) / L102-L106 (tapered) | eligible if compatible | 仅单个 `rolled_rim` torus，N_bands=0 |
| `bands_n2` | rec_bucket1_var_bands_two | `_wall_radius_at_z` L63-L65, `_band_heights` L68-L73, `_band_mesh` L76-L84, loop L162-L173 | eligible if compatible | `NUM_BANDS=2`，`for i in range(2)` 发射 `band_i` torus，半径按各高度局部 wall radius |
| `bands_n3` | rec_bucket1_var_bands_three | `_wall_radius_at` L62-L64, `_band_mesh` L67-L72, loop L150-L162 | eligible if compatible | `BAND_COUNT=3`，`for i in range(3)` 发射 `band_i`，高度 `BODY_H*(i+1)/(N+1)` |

注：rim 本身是身份不变量（每个变体恒含 `rolled_rim`），Slot D 的真正变化轴是 reinforcing band 数量 N∈{0,2,3}（distinct-N）。

## 槽位图（slot graph）

pattern: parallel_children

```
[Slot C: mount root?]
   wall_bracket → bracket (root) --[bracket_to_bucket FIXED @ (0,0,0)]--> bucket
   free/hook    → bucket IS root

bucket (root, Slot A body shell + Slot D bands + rolled_rim + lugs)
   │
   ├─[Slot B handle]
   │    swing_bail → handle child --[bucket_to_handle REVOLUTE, origin (0,0,LUG_Z), axis (0,1,0), ±100°]
   │    side_grips → fold_grip child --[bucket_to_fold_grip REVOLUTE, origin (0,GRIP_MOUNT_Y,GRIP_MOUNT_Z), axis (1,0,0), 0–85°] (+ inline fixed grip)
   │    hinged_lid → lid child --[bucket_to_lid REVOLUTE, origin (HINGE_X,0,RIM_Z), axis (0,1,0), 0–110°]
   │
   └─[Slot C hook_ring] inline visuals above rim (no joint)
```

接口点位：

- **Slot A→B（bail/grips）**：pivot 接口在 rim 外侧 ±Y（bail）或壁面 ±Y（grip）。bail lug 沿 `LUG_Y = wall_top_r + 0.014`，`LUG_Z = BODY_H - 0.012`；joint origin 恰落在 lug 轴（no float）。grip pivot 在 `GRIP_MOUNT_Z = BODY_H-0.055` 处的局部壁半径外。
- **Slot A→B（hinged_lid）**：接口在 +X rim 切线，hinge barrel `(HINGE_X=TOP_R,0,RIM_Z)`，lid 在 rim 上方 `LID_SEAT_Z` 落座避免穿模。
- **Slot C→A（wall_bracket）**：cradle ring 在 `CRADLE_Z=0.38*BODY_H` 抱桶（ring center radius = 该高度 wall radius + tube*0.4），`bracket_to_bucket` FIXED origin `(0,0,0)`（bucket 在自身坐标系，bracket 背板在 +X）。
- **Slot D→A**：band torus 半径 = `_wall_radius_at(band_z)`，origin `(0,0,band_z)`，hug 壁面。

互斥/可选/派生：

- Slot B 三 candidate **互斥**（一个 bucket 只有一种 handle 拓扑）。`hinged_lid` 删除 lugs/rivets（无 bail），与含 bail 的 mount 检查无冲突。
- Slot C `wall_bracket` 引入新 root + FIXED；`hook_ring` 与 `free_standing` 不改 root。
- Slot A 与 Slot C 兼容性：cone 族（无平底）+ `free_standing` 合法（设计为悬挂）；但 cone + `wall_bracket` 也合法（cradle 抱锥壁）。见 compatibility matrix。

## 每槽位 Module Emits / Interfaces

### Slot A / module body（所有 body profile 通用）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `bucket`；visual `bucket_shell`（旋转薄壳）+ `rolled_rim`（torus，不变量） | tapered L99-L107 |
| internal joints | 无（body 是 root，刚性） | — |
| upstream interface | root，或被 `wall_bracket` 经 FIXED 反挂 | bracket L255-L262 |
| downstream interface | rim ±Y lug 轴（bail/grip pivot）、+X rim 切线（lid hinge）、外壁面（band/cradle hug） | tapered L114-L131 |

### Slot B / module swing_bail_revolute
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket 上 `lug_pos/lug_neg` + `rivet_pos/rivet_neg`（±Y 循环）；child part `handle` 含 `bail_wire` | tapered L118-L165 |
| internal joints | `bucket_to_handle` REVOLUTE，origin `(0,0,LUG_Z)`，axis `(0,1,0)`，limits ±100° | tapered L170-L183 |
| upstream interface | bail-wire 端 seat 进 ±Y lug（`expect_contact` tol 0.004）；joint origin 在 lug 轴上 | tapered L311-L314 |
| downstream interface | 无（终端摆件） | — |

### Slot B / module fixed_side_grips
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket 上 `grip_lug_{r/l}_{i}` + `grip_rivet_{r/l}_{i}`（`for i in range(2)` × ±X lug）；i=0 child `fold_grip`（`grip_wire_0`），i=1 inline `grip_wire_1` | L150-L201 |
| internal joints | `bucket_to_fold_grip` REVOLUTE，origin `(0,GRIP_MOUNT_Y,GRIP_MOUNT_Z)`，axis `(1,0,0)`，limits 0–85°（fold-flat） | L206-L219 |
| upstream interface | grip-wire 端 seat 进 ±X lug/rivet（scoped allow_overlap） | L256-L279 |
| downstream interface | 无 | — |

### Slot B / module hinged_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket 上 `hinge_ear_{0,1}` + `hinge_barrel`；child `lid` 含 `lid_disk/lid_rim/hinge_strap/lid_knob` | L117-L194 |
| internal joints | `bucket_to_lid` REVOLUTE，origin `(HINGE_X,0,HINGE_Z=RIM_Z)`，axis `(0,1,0)`，limits 0–110° | L202-L218 |
| upstream interface | lid 在 `LID_SEAT_Z` 落座于 rim 之上（不穿模）；strap 桥接 lid 到 barrel | L59-L62, L174-L184 |
| downstream interface | 无 | — |

### Slot C / module wall_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `bracket` 含 `back_plate` + `bolt_hole_{0,1}`（`for i in range(2)`）+ `cradle_ring` + `cradle_arm` | L140-L175 |
| internal joints | `bracket_to_bucket` FIXED，origin `(0,0,0)`（非定义关节；bail 仍提供 REVOLUTE） | L255-L262 |
| upstream interface | back_plate 贴 +X 墙（2 bolt holes） | L143-L159 |
| downstream interface | cradle ring 在 38% 高抱桶壁；bucket 成为 FIXED child | L162-L167 |

### Slot C / module hook_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket inline `hook_arm_{0..3}`（`for i in range(4)`）+ `hook_plate` + `hook_shank` + `hook_ring` torus | L133-L185 |
| internal joints | 无（纯装饰吊环） | — |
| upstream interface | 四臂从 rim 内缘桥到中心 plate | L136-L149 |
| downstream interface | 顶部 torus 吊环供外部 hook/post 悬挂 | L173-L185 |

### Slot D / module bands_n（N∈{2,3}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | bucket inline `band_{i}` torus（`for i in range(N)`，shared `_band_mesh` helper） | bands_two L162-L173 |
| internal joints | 无 | — |
| upstream interface | 每 band 半径 = `_wall_radius_at(band_z)`，hug 壁面无 float | bands_three L67-L72 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_profile` | enum | conical_pointed / tapered_cylinder / straight_pail / hemispherical_bowl / deep_narrow_cone | — | choice | deterministic procedural sampler | Slot A 表 |
| `handle` | enum | swing_bail_revolute / fixed_side_grips / hinged_lid | — | choice | sampler | Slot B 表 |
| `mount` | enum | free_standing / wall_bracket / hook_ring | — | choice | sampler；与 body 经 compatibility gate | Slot C 表 |
| `band_count` | enum/int | {0, 2, 3} | 0 | choice | distinct-N 复制轴；0=rolled_rim_only | Slot D 表 |
| `palette_style` | enum | fire_red / galvanized / sand_tan / weathered_brick / hammered_gunmetal / forest_green | fire_red | choice | 仅改材质 rgba，不改结构；body+wire+accent 一致 | parents L87-L88 |
| `body_height_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 `BODY_H`（cone/lathe/bowl 各自 base） | cone L41 / tapered L37 |
| `top_radius_scale` | float | [0.90, 1.15] | 1.0 | independent | clamp；缩放 `TOP_R` | tapered L35 |
| `taper_ratio` | float | [0.55, 1.00] | 0.75 | conditional | `BOT_R = taper_ratio·TOP_R`；straight_pail 锁 1.0、cone 不适用、bowl 不适用 | tapered L35-L36 |
| `handle_rise_scale` | float | [0.85, 1.25] | 1.0 | independent | clamp；缩放 `HANDLE_RISE`（仅 bail） | parents L54 |
| `lug_y_offset` | float | derived | 0.014 | equation | `LUG_Y = wall_top_r + 0.014`；随 top_radius_scale 派生 | parents L46/L49 |
| `cradle_z_frac` | float | [0.30, 0.45] | 0.38 | conditional | 仅 wall_bracket；`CRADLE_Z = frac·BODY_H` | bracket L60-L65 |
| (—) | constraint | — | — | inequality | bail：`LUG_Y - WIRE_R > rim_outer_y + 0.001`（连杆站在 rim 外）；违反则放大 `lug_y_offset` 重投影 | parents L293-L298 |
| (—) | constraint | — | — | inequality | bail clear：`HANDLE_RIM_CLEAR_Z > (RIM_Z+RIM_TUBE-LUG_Z)+WIRE_R`（过 rim 才弯）；派生满足 | parents L300-L306 |
| (—) | constraint | — | — | inequality | band：`band_z ∈ [BODY_H·0.08, BODY_H·0.92]`，避开底/rim；N≤3 时天然满足 | bands_two L68-L73 |
| (—) | constraint | — | — | inequality | lid seat：`LID_SEAT_Z ≥ RIM_TUBE + 0.001`（lid 不穿 rim） | no_handle L62 |

palette_style 目标 ≥3，列出 6 个 colorway（fire_red 救火红 / galvanized 镀锌银灰 / sand_tan 沙黄 / weathered_brick 旧砖红 / hammered_gunmetal 锤纹枪铁 / forest_green 军绿）。注意 body 测试断言中含"red"硬检查——实现时这些断言须改成"按 palette_style 期望色判定"，不能锁死 red。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：reinforcing band 数量。**

- `count_param`：`band_count`
- `N_range`：本小类本轴产品域 `{0} ∪ [2, 5]`（测试偏小：N∈{0,2,3} 高频；产品全程到 5 稀有）。5★ 源仅证实 N=0/2/3；N∈{4,5} 由 `_band_heights` 均匀公式 `BODY_H·(i+1)/(N+1)` 自然外推，sweep 上限设 5。
- sampling domain（权重档）：N=0 ~40%，N=2 ~30%，N=3 ~20%，N=4 ~7%，N=5 ~3%（小 N 高频、大 N 稀有）。
- copied object：单个 `_band_mesh` torus（thin hoop rib），半径按各 band 高度局部 wall radius。
- naming：`band_{i}`，i ∈ range(N)。
- placement：均匀分布 `band_z = z_lo + span·(i+1)/(N+1)`，`z_lo/z_hi` 留底/rim 边距（`BAND_MARGIN_FRAC=0.08`）。
- joint policy：无关节（inline parent visual，刚性装饰 rib）。
- source/gating：bands_two L162-L173 / bands_three L150-L162；仅 lathe/cone/bowl 旋转壁可挂（半径取自 `_wall_radius_at`）；hemispherical 用其曲率 radius 函数取 band 半径。

其余 slot 的 ±Y lug 对、±X grip lug 对、4 hook arms、2 bolt holes、2 hinge ears 都是**固定 N** 对称循环（非可变 multiplicity），按 named slot 表达，不暴露 `*_count`。

## 拓扑多样性审计

总组合数：A × B × C × D = 5 × 3 × 3 × 4 = **180**（D 含 N∈{0,2,3} 三个已验证档；加 N∈{4,5} 外推后 band 轴 5 档 → 5×3×3×5 = 225）。≥10 → PASS。

理由：仅 Slot A（5）× Slot B（3）已给 15 个 distinct part-tree/joint-topology 组合（body shell helper 不同、joint 数/类型/child part 不同），远超 10；加 mount root 切换（FIXED 引入新 root）与 band distinct-N 进一步放大。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng` 对四个 enum 轴各做加权抽样（A 均匀；B：bail 偏多 ~0.6、grips ~0.25、lid ~0.15；C：free ~0.5、hook ~0.3、bracket ~0.2；D：按上表 band 权重档），再对连续 scale 按"先 independent → 派生 equation → 投影 inequality → 解析 conditional"契约求解。compatibility matrix 在 `resolve_config` 内 gate 非法组合并 fallback。无大型 curated/modulo 表；至多保留 1–2 个 regression override（若 sweep 暴露已知失败 seed）。Topology target：1000-seed distinct 建议 按 ≥300 report-only 口径观察；本类 enum 组合 ~180–225 + 连续 scale 扰动，可达 按 ≥300 report-only 口径观察（band/grip/lid 关节拓扑是主多样性来源）。

Controlled local parameterization：`body_height_scale`[0.85,1.20]、`top_radius_scale`[0.90,1.15]、`taper_ratio`[0.55,1.00]（conditional：straight 锁 1.0，cone/bowl N/A）、`handle_rise_scale`[0.85,1.25]、`cradle_z_frac`[0.30,0.45]（conditional：仅 bracket）。全部在 `resolve_config` clamp/派生；`lug_y_offset` 由 top_radius_scale equation 派生以保 bail 连杆站在 rim 外（inequality 投影）。这些 scale 只改安全比例，不破坏 pivot 轴语义、bail-rim clearance、lid seat、band hug 或 fire-bucket 身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A 均匀；B/C/D 加权；连续 scale 按采样契约 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 见下方矩阵；非法组合 fallback | 无 floating / 穿模 / 错轴 / closed-pose / band 越界 / lid 穿 rim |
| controlled local variation | 上列 5 个 scale + clamp/派生 | 比例变化不破坏 pivot/clearance/support/joint origin/身份 |
| regression overrides | none（除非 sweep 暴露具体失败 seed） | 仅已知失败或审核指定 |
| random sweep | seeds 0-49 初查，0-999 成熟审计 | 与 contract failures |

compatibility matrix（关键 gate）：

- `body=cone族(conical/deep_cone)` + `mount=free_standing`：合法（设计为悬挂，无平底；测试断言"apex 最低点"而非"平底坐地"）。
- `body=cone族` + `band_count>0`：合法（band 半径取锥壁线性 radius）；但 band 须在 apex 之上 margin 内。
- `handle=hinged_lid` ⇒ **删除 lugs/rivets/bail**（无 bail），lid 是定义关节；与 mount 任意组合合法（lid hinge 在 +X，cradle 抱壁不撞 hinge）。
- `handle=hinged_lid` + `body=cone族`：gate 检查 lid 盘半径 = 锥顶 top_r（cone 顶口较窄，lid 仍可盖）。
- `mount=wall_bracket` ⇒ 引入 root `bracket` + FIXED；`handle` 仍提供真实 REVOLUTE（bail/grip/lid 之一），FIXED 不算定义关节。
- band_z 必须 ∈[0.08,0.92]·BODY_H（inequality）；N>3 时检查相邻 band 不重叠（间距 > 2·BAND_TUBE_R）。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A | 5 | yes | yes | cone/lathe/bowl 三族 helper |
| B | 3 | yes | yes | bail / fold-grip / hinged-lid 三种真实非固定关节 |
| C | 3 | yes | yes | free / bracket(FIXED root) / hook_ring |
| D | 4(+2 外推) | yes | yes | distinct-N bands N∈{0,2,3}(+4,5) |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D 四元组）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（cone+free、lid 删 lug、bracket FIXED root、band 越界）
- optional regression overrides are sparse and justified（默认 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped（body/top/taper/handle_rise/cradle scale），不破坏 pivot/clearance/joint origin/multiplicity
- cross-part scale dependencies resolved in `resolve_config`：`BOT_R=taper·TOP_R`(equation)、`LUG_Y` 派生、bail-rim clearance 与 lid-seat inequality 投影
- critical InterfaceSpec / MatingContract：bail/grip 端 contact lug（tol 0.004）、cradle hug 壁、band hug 壁、lid seat 在 rim 上
- key joints have expected type/axis/range：bail REVOLUTE axis (0,1,0) origin (0,0,LUG_Z) ±100°；fold_grip REVOLUTE axis (1,0,0) 0–85°；lid REVOLUTE axis (0,1,0) 0–110°；bracket FIXED
- 每个非-lid 变体恒含 `rolled_rim`（身份不变量）；每个变体恰含 **≥1 个真实非-FIXED 关节**（定义性 bail/grip/lid）
- copied objects follow naming/placement：`band_{i}` 均匀分布、半径=局部 wall radius

## Reject cases

- 某变体只剩 FIXED 关节、无任何真实摆动件（丢失定义性 REVOLUTE）。
- 去掉 `rolled_rim`（破坏 sheet-metal fire-bucket 身份）。
- bail joint origin 不在 lug 轴上（handle 漂浮）或 axis 非 ±Y 水平直径线。
- bail 连杆穿过 rim（`LUG_Y - WIRE_R ≤ rim_outer_y`）或在 rim 高度以下就弯（撞 rim）。
- body 用 Box/棱柱而非旋转薄壳（漂向通用 tote/caddy，混入 bucket2/木桶身份）。
- 把 body 做成封顶加压瓶 + 阀门/喷嘴（混入 Fire_Extinguisher）。
- band 落在桶底以下、rim 以上，或半径不匹配壁面而浮空/陷入。
- hinged_lid 仍保留 lugs/bail（双重 handle 语义矛盾）或 lid 穿 rim/桶壁。
- palette 把 body 与 wire 锁死成 red 而忽略 palette_style；或 palette_style 改了结构而非仅材质。
- wall_bracket cradle 不抱壁（ring 半径≠该高度 wall radius）导致桶悬空。

## 与相邻类别的边界

- 不该混入：**bucket2（木桶 / wooden keg）**——木板条 stave + 多道紧箍 hoop 的木质腰鼓桶，无 sheet-metal 旋转薄壳、无 red paint、无 bail-wire REVOLUTE；bucket1 的稀疏 reinforcing band 不是结构紧箍 hoop。
- 不该混入：**Fire_Extinguisher（灭火器）**——封闭加压钢瓶 + 顶部阀门/喷管/压力表/squeeze handle；bucket1 是开口桶 + 卷边 rim + 摆动 bail，无阀门无喷嘴无封顶。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_revolved_shell_mesh`（tapered/straight 共用，仅 bot_r 变）、`_conical_shell_mesh`（conical/deep_cone 共用）、`_band_mesh` + `_wall_radius_at`（band 轴）、`tube_from_spline_points`（bail/grip/cradle 共用）。bowl 用独立弧线 profile helper。
- captured-pin / scoped allow_overlap：lug↔rim、rivet↔lug、bail_wire↔lug、grip_wire↔grip_lug/rivet、band↔shell、cradle_ring↔shell、lid↔rim、hook_arm↔rim——全部 element-scoped，复制 5★ 各变体的 allow_overlap 调用（按所选 module 条件发射）。
- body 测试中的"red"硬断言须改写为按 `palette_style` 期望色判定，避免锁死 fire_red。
- N∈{4,5} band 仅由均匀公式外推，无 5★ 源；sweep 上限 5，并加相邻 band 不重叠 inequality 检查。
- cone 族 + free_standing 时，body 测试断言用"apex 最低点/无平底"，不要套用 lathe 族的"平底坐地"断言（按 body_profile 条件选断言）。
