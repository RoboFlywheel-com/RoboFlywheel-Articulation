# Modular Spec — automotive_differential_differential_gear

## 元信息
| 项 | 值 |
|---|---|
| slug | `automotive_differential_differential_gear` |
| template path | `agent/templates/automotive_differential_differential_gear.py` |
| test path (optional) | `tests/agent/test_automotive_differential_differential_gear_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (hub: single `carrier_cage` root; ring gear FIXED, side gears / spider gears / drive pinion / planet worms / dog collar all parent directly to the carrier) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (1 origin anchor + 7 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

Sources (read in full):
- **O = origin** `rec_...__001_png_aeabd1e9b136406aa0eebf9bf43ee47e` — open cast cage carrier (cadquery `_carrier_cage_geometry` L58-92), helical spur ring (SpurGear mesh L154-170), 2 bevel side gears + axle outputs (L180-220), 2 bevel spider pinions on cross shaft (hub + 12 radial Box teeth L224-251), bevel drive pinion (L254-284). All gear joints CONTINUOUS, ring FIXED.
- **P4 = var_pinions4** — full carrier + gears rebuilt from SDK **primitives** (solid cheeks/bridges/collars/flange L39-100, Cylinder+Box gears), 4-pinion spider cross (2 cross shafts, 4 spiders at 90° L162-198). Primitive-carrier + primitive-gear source.
- **CC = var_carrier_closed** — closed hollow-shell carrier variant (barrel Cylinder + collars + flange + snout + ribs + inspection ports L96-188), primitive ring/side/spider gears via `_ring_gear_visuals` L20-44 & `_bevel_gear_visuals` L47-73.
- **LC = var_lsd_clutch** — bevel spiders + stacked friction/steel clutch plate loop (N=6) between each side gear and carrier cheek (L163-214).
- **VC = var_lsd_viscous** — sealed viscous drum (annular, rides with carrier L171-176) enclosing an interleaved plate stack (N=8, even→side_0 / odd→side_1 L216-260); spiders enclosed/absent.
- **TS = var_torsen** — helical worm side gears (SpurGear helix 42° L220-232) + 3 pairs of helical planet worms (`Worm` mesh L121-139) CONTINUOUS about X in radial carrier pockets (L265-312).
- **LK = var_locker** — open bevel spiders + splined `dog_collar` PRISMATIC axial engagement (carrier dog teeth + lock boss L142-164, collar L275-323, `carrier_to_lockcollar` PRISMATIC L315-323).
- **RB = var_ring_bevel** — ring gear rebuilt as conical crown-wheel (`_crown_wheel_body_geometry` L110-122 + backing disc L125-139) with repositioned drive pinion cone (L330-349).

## 核心身份

一套汽车差速器齿轮组（automotive differential gear set）：一个绕**轴半轴中心线（X 轴）自转的 carrier（差速器壳/架）**，外挂一个由输入 drive pinion 驱动的 final-drive ring/crown 齿轮（`carrier_to_ring` FIXED + `carrier_to_pinion` CONTINUOUS），carrier 内部通过差速齿轮机构（bevel spider / clutch-LSD / viscous-LSD / Torsen 蜗轮 / locker）把扭矩分给**恰好两个同轴输出 side/axle 齿轮**（`side_gear_0/1` CONTINUOUS about X），允许两输出以不同速度旋转。

**成熟默认域**：乘用车/卡车后桥或前桥差速器核心（open diff、LSD、Torsen、diff-lock）。side gear 数量**恒为 2**（半轴输出定义），不是 multiplicity 轴。
**不该混入**：普通变速箱/减速机（无同轴双半轴输出）；单个 spur/bevel 齿轮或齿轮对（无 carrier、无双输出分流）；作减速用的行星/周转减速单元（sun+ring+carrier 减速器）；spool / 锁死实心轴（无差速动作，失去独立输出身份）。

## 槽位 + 候选模块表

### Slot A：carrier_form（① 骨架 + ③ 主体包络，ROOT part `carrier_cage`，容纳全部齿轮）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| open_cage | forked_anchor | O, P4 | O L58-92 / P4 L39-100 | Macro Surface Construction (开窗镂空笼架) | eligible | cadquery 开窗笼：环形 cheeks（inner 开孔露出内部齿轮）+ 4 根 window bridge + 轴承 collar + ring flange + shoulder + pinion snout + ribs。内部齿轮可见。 |
| closed_case | forked_anchor | CC | CC L96-188 | Volumetric Envelope Form (封闭壳体) | eligible | cadquery 封闭壳：与 open_cage 相同的实心端 cheeks（内部齿轮同样贴 cheek 面就位、轴线穿过实心 cheek）+ 实心 outer barrel 壁替代窗口 bridge + 同样的 collar/flange/snout/ribs；barrel 壁上切 4 个 inspection port 真通孔（既是 ③/④ 细节，又打通内腔使内外壳面并为单一 mesh 连通体）。 |

（Slot A 降到 2 candidate 的理由：真实汽车差速器壳只有"开窗镂空笼"与"封闭铸壳"两大形态族；再细分只是 ④/⑤ 装饰/尺寸，非结构。）

### Slot B：ring_gear_form（③ 主体形态家族，FIXED 于 carrier flange 的终传动齿轮）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| helical_spur | forked_anchor | O, CC | CC L20-44 (`_ring_gear_visuals`) | Planar Boundary Form (平盘圆周齿) | eligible | 扁平圆盘 ring：Cylinder 盘体 + 沿圆周的径向 Box 齿（helical spur 盘齿），轴向薄、径向大；drive pinion 在盘侧沿 Y 啮合。 |
| bevel_crown | forked_anchor | RB | RB L110-152, L219-254 | Volumetric Envelope Form (锥形冠轮) | eligible | 锥形 crown-wheel：cadquery 锥/环盘 tooth cone + backing disc（结构厚度 + bolt 重叠），drive pinion 重定位为锥齿在冠轮周缘啮合。 |

（Slot B 降到 2 candidate 的理由：final-drive ring 只有"平盘 helical spur"与"锥形 spiral-bevel crown wheel"两个真实形态族；hypoid 只是 bevel 的偏置 ④ 变体，非新结构。）

### Slot C：internal_mechanism（① 骨架 + ② 关节 + ③ 形态，carrier 内部差速机构；负责发射 `side_gear_0/1` + 各自 joint + 内部齿轮）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| open_spider | forked_anchor | O, P4, CC | O L224-251 / P4 L162-198 | eligible | bevel side gears（hub + 径向 Box 齿）+ N 个 bevel spider pinion（hub + 12 齿）在 cross shaft 上，CONTINUOUS。`n_spider ∈ {2,4}` 为 multiplicity（N=4 加第二根 cross shaft，90° 分布）。 |
| clutch_lsd | forked_anchor | LC (+ O spiders) | LC L163-214 | eligible | open_spider（2 spider）之上，每个 side gear 与 carrier cheek 之间叠一摞交替 friction/steel clutch 盘（N=6 循环，carrier visual）。 |
| viscous_lsd | forked_anchor | VC | VC L171-176, L216-260 | eligible | 无外露 spider：同轴密封 viscous drum（carrier visual）内嵌 N=8 交替 keyed 盘（even→side_0 / odd→side_1）；side gear 加 hub_connector 伸入 drum。 |
| torsen | forked_anchor | TS | TS L121-139, L216-312 | eligible | 用 **helical worm side gears**（SpurGear helix mesh）替换 bevel side gear；3 对（6 个）helical planet worm（`Worm` mesh，rh/lh 各一）CONTINUOUS about X，径向 120° 分布嵌 carrier 内部。无 bevel spider。 |
| locker | forked_anchor | LK (+ O spiders) | LK L142-164, L275-323 | eligible | open_spider（2 spider）之上，加 carrier dog teeth + lock boss（carrier visual）与一个 splined `dog_collar`，`carrier_to_lockcollar` **PRISMATIC** 沿 X 轴向 [0, 0.018] 咬合行程。 |

硬约束满足：Slot A 2 candidate（结构：开窗 vs 封闭壳，均 source-backed）、Slot B 2 candidate（③ 形态：平盘 vs 锥冠）、Slot C 5 candidate（① 机构族）。每个 candidate 结构不同、有 forked_anchor 来源。side gear 恒为 2（不可 multiplicity）。

## 槽位图（slot graph）

pattern: parallel_children（hub：单 root `carrier_cage`，全部子件挂到它）

```
carrier_cage (ROOT, cadquery shell + cross_shaft/drum/dog-teeth/bolt-shank/port carrier visuals)
  ├─[carrier_to_ring     FIXED       @ Origin(); ring seated on flange, bolt shanks overlap ring]──> ring_gear   (Slot B)
  ├─[carrier_to_side_0   CONTINUOUS axis(1,0,0) @ (-0.041,0,0); journal seated in axle collar]──────> side_gear_0 (Slot C)
  ├─[carrier_to_side_1   CONTINUOUS axis(1,0,0) @ (+0.041,0,0); journal seated in axle collar]──────> side_gear_1 (Slot C)
  ├─[carrier_to_spider_i CONTINUOUS axis(0,1,0)/(0,0,1) @ cross-shaft; hub captured on shaft]────────> spider_gear_i (open_spider/clutch/locker; i in range(n_spider))
  ├─[carrier_to_planet_i CONTINUOUS axis(1,0,0) @ radial pocket; worm shaft seated in carrier]───────> planet_worm_i (torsen; i in range(6))
  ├─[carrier_to_pinion   CONTINUOUS axis(0,1,0) @ (-0.145,-0.225,0); shaft captured in snout]─────────> drive_pinion (Slot B repositions teeth)
  └─[carrier_to_lockcollar PRISMATIC axis(1,0,0) @ (-0.104,0,0); collar slides on side_0 hub]─────────> dog_collar   (locker only)
```

- 所有子件直接 parent = `carrier_cage`（hub 型 parallel children），不串链，无跨 slot mating chain。
- 接口点位（joint origin 均落在真实硬件上）：ring 与 carrier 同心（flange/bolt 圆）；side gear journal 坐进 collar 孔（X 轴）；spider hub 卡在 cross_shaft（Y/Z 轴）；planet worm shaft 坐进 carrier 内部（X 轴）；drive pinion shaft 坐进 snout（Y 轴）；dog collar 沿 side_0 hub 滑（X 轴）。
- carrier visuals（cross_shaft / viscous_drum / carrier_dog_tooth_* / lock_boss / bolt_shank_* / inspection_port_*）由所选 Slot C / Slot A module 按需追加到 root part（Rule 1：不动的机构支撑件折入 carrier visual，只有真正转动/滑动的件才建独立 part）。

## 每槽位 Module Emits / Interfaces

### Slot A / open_cage | closed_case（ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carrier_cage`（root）：cadquery 壳 `carrier_body`（实心端 cheeks + open_cage 4 根 window bridge 或 closed_case 实心 outer barrel 壁 + collar×2 + flange + shoulder + snout + ribs）；bolt head×n_bolt + bolt_shank×n_bolt（primitive Cylinder）；closed_case 壁上切 inspection_port×4 通孔 + inspection_port_i 装饰盘 | O L58-92 / CC L96-188 / P4 |
| internal joints | 无（所有齿轮由 Slot B/C 挂到 carrier） | — |
| downstream interface | flange/bolt 圆面（ring 座）；两侧 collar 孔（side journal 座，X 轴）；snout 孔（pinion shaft 座，Y 轴）；开放中心（spider/planet 空间） | O / CC |

### Slot B / helical_spur | bevel_crown
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ring_gear`：helical_spur = Cylinder 盘 + 径向 Box 齿；bevel_crown = cadquery 锥盘 `toothed_ring` + `crown_backing` disc | CC L20-44 / RB L110-139 |
| internal joints | `carrier_to_ring` **FIXED** @ Origin() | O L171-177 |
| interface | ring 与 carrier flange 同心；bolt_shank_i 穿过 ring（allow_overlap）提供支撑；bevel_crown 时 drive pinion 齿重定位至冠轮周缘 | O / RB |

### Slot C / open_spider（+multiplicity n_spider）| clutch_lsd | viscous_lsd | torsen | locker
| emits | 描述 | 来源 |
|---|---|---|---|
| parts (all) | `side_gear_0`,`side_gear_1`（bevel: hub + 径向齿 + axle_output + bearing_journal；torsen: helical worm hub；viscous: + hub_connector） | O L180-220 / TS L233-254 / VC L221-250 |
| parts (open/clutch/locker) | `spider_gear_i`（pinion_hub + 12 Box 齿），i in range(n_spider) | O L224-242 / P4 L180-198 |
| parts (torsen) | `planet_worm_i`（worm_threads Worm mesh + worm_shaft），i in range(6) | TS L277-312 |
| parts (locker) | `dog_collar`（collar_body + bore + shift_groove + 6 collar dog teeth） | LK L275-311 |
| carrier visuals | cross_shaft(×1 或 ×2 for n=4)；clutch_plate_{s}_{p}（LC）；viscous_drum + viscous_plate（VC）；lock_boss + carrier_dog_tooth_i（LK） | LC/VC/LK/O |
| internal joints | `carrier_to_side_{0,1}` CONTINUOUS axis(1,0,0)；`carrier_to_spider_i` CONTINUOUS axis(0,1,0)/(0,0,1)；`carrier_to_planet_i` CONTINUOUS axis(1,0,0)；`carrier_to_lockcollar` PRISMATIC axis(1,0,0) [0,0.018] | O / TS / LK |
| interface | journal 坐 collar；spider hub 卡 cross_shaft；planet shaft 座 carrier；collar 滑 side_0 hub（captured，element-scoped allow_overlap） | O/TS/LK |

活动件（side/spider/planet/pinion/dog_collar）都是独立 part 带 articulation。不动支撑件（cross_shaft、drum、clutch/viscous 盘、dog teeth、lock boss、bolt shank、port）折入 carrier visual（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| carrier_form | enum | open_cage / closed_case | open_cage | choice | 采样器选择 | Slot A |
| ring_form | enum | helical_spur / bevel_crown | helical_spur | choice | 采样器选择 | Slot B |
| mechanism | enum | open_spider / clutch_lsd / viscous_lsd / torsen / locker | open_spider | choice | 采样器选择 | Slot C |
| n_spider | int | {2, 4}（权重 0.65/0.35） | 2 | conditional | 仅 mechanism∈{open_spider,clutch_lsd,locker} 用；viscous/torsen 强制无 spider | §8 / P4 |
| palette_style | enum | dark_iron / nodular_grey / phosphate_black / oiled_bronze / machined_bright | dark_iron | choice | 采样 | ⑥ §8.5 |
| n_bolt | int | 8–12（权重偏 10） | 10 | independent | 装饰 bolt 圆数量（clamp） | O/CC |
| carrier_radius_scale | float | [0.90, 1.12] | 1.0 | independent | clamp（carrier 主半径/长度整体缩放） | O/CC |
| ring_radius_scale | float | [0.90, 1.12] | 1.0 | independent | clamp（ring 盘/冠半径） | O/RB |
| side_gear_scale | float | [0.90, 1.10] | 1.0 | independent | clamp（side/spider gear 体半径，同步保形以维持啮合读感） | O/CC |
| lock_travel | float | derived | 0.018 | equation | `= 0.5*(collar_x_free)`，locker collar 行程由 side_0 hub 长派生 | LK |
| (—) | constraint | — | — | inequality | 内部齿轮体半径 `side_body_r*side_gear_scale + tooth_h ≤ cheek_inner_r*carrier_radius_scale − 0.004`（齿轮全程留在开放中心，不与壳壁穿模） | 接口/clearance |
| (—) | constraint | — | — | inequality | `journal_r > collar_inner_r`（journal 坐进 collar 孔，保证连通 + captured 座）；`pinion_shaft_r > snout_inner_r` | 接口/连通 |

采样契约：先采 independent（carrier/ring/side scale、n_bolt）→ 派生 lock_travel（equation）→ inequality 投影（齿轮半径回缩到开放中心内、journal/shaft 座配合）→ conditional（mechanism 决定 n_spider / spider vs planet vs viscous / dog collar 合法域）。全部在 `resolve_config` 完成。scale 之间保形锁定处以 equation 声明，其余独立。

## 7.5 编译预算 / compile budget（必填）
自报 **≤30 s/seed**。依据：carrier 壳为 cadquery 布尔（环形 cheeks/barrel + collar/flange/snout/ribs union，tolerance 0.0018）典型 8–18 s；齿轮主体用 **primitive**（Cylinder 体 + Box 径向齿）几乎免费；torsen 用共享 `Worm` mesh（rh/lh 各建 1 次复用 6 个）+ 1 个 SpurGear helix side mesh（≈3–6 s）；bevel_crown 用 2 个小 cadquery 锥盘（≈3 s）。分档 tessellation：cadquery angular_tolerance 0.10、tolerance 0.0018–0.003；N 个同构盘/齿复用同一 `Mesh` / 循环 primitive。超预算先降 tolerance / 减 bridge 段再迭代。sweep `--compile-timeout 90`（≈3× 预算，watchdog）。

## Multiplicity / Copy Logic

**轴 1：n_spider（唯一模板级 multiplicity 轴）**
- count_param: `n_spider` / N_range 产品域 {2, 4}（2 = 标准对置 spider，4 = 重载 4-pinion spider cross）。奇数不用于真实汽车差速器（Blocked）。
- sampling domain：权重 (0.65, 0.35)，N=2 高频、N=4 稀有。
- copied object：`spider_gear_{i}` part（pinion_hub + 12 Box 齿循环），源 O `for index,y in [...]` L224 / P4 L180-198。
- naming：`spider_gear_0..n-1`；joint `carrier_to_spider_{i}`。
- placement：N=2 沿 Y 对置（±0.040）；N=4 沿 Y、Z 两根 cross shaft 90° 分布。joint policy：CONTINUOUS 绕各自径向轴。
- gating：仅 mechanism∈{open_spider, clutch_lsd, locker}；viscous_lsd / torsen 无 spider（强制 n_spider 语义为 0）。

**装饰复制（record_only，非 multiplicity 轴）**：flange bolt `bolt_{i}`/`bolt_shank_{i}`（N=n_bolt 8–12）、spider 齿 `tooth_{j}`（N=12）、clutch 盘 `clutch_plate_{s}_{p}`（N=6）、viscous 盘 `viscous_plate_{i}`（N=8）、torsen planet worm 对（3 对=6）、closed_case inspection port（N=4）。这些是各 module 内部固定循环，不暴露为独立采样档。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | (a) mechanism 换内部机构 → 增减会动 part：open_spider(2/4 spider) / clutch_lsd(2 spider+盘) / viscous_lsd(无 spider,盘) / torsen(6 planet worm,无 spider) / locker(2 spider + dog_collar)；(b) carrier_form 开窗 vs 封闭壳改壳骨架；(c) n_spider multiplicity 2↔4 改 spider part 数。全 forked_anchor 支撑（O/P4/CC/LC/VC/TS/LK）。 |
| └ multiplicity | 同构件 ×N | 有 | `n_spider ∈ {2,4}`，权重 (0.65,0.35)，仅 spider 机构，见 §8。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | 必现：`carrier_to_ring` FIXED；`carrier_to_side_{0,1}` CONTINUOUS(1,0,0)；`carrier_to_pinion` CONTINUOUS(0,1,0)。机构相关：spider CONTINUOUS(0,1,0)/(0,0,1)、planet CONTINUOUS(1,0,0)、**locker `carrier_to_lockcollar` PRISMATIC(1,0,0)**。均 source-backed；每种类型在 sweep 出现（locker 保证 PRISMATIC 现身，见 §9）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | 登记进 slot_choices 的两个 ③ slot：**ring_form** = helical_spur(Planar Boundary Form 平盘) vs bevel_crown(Volumetric Envelope 锥冠)；**carrier_form** = open_cage(Macro Surface Construction 镂空笼) vs closed_case(Volumetric Envelope 封闭壳)。另 torsen 用 helical worm side gear（Volumetric Envelope，替换 bevel side gear 形态）为 ③ ride-along。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | source_type=record_only + world_knowledge_extrapolation：铸铁 pebble 纹、机加工齿面高光、blackened bolt heads、closed_case inspection port。装饰几何由宿主表面派生随 ③⑤ 共形：inspection port 贴在 barrel 外半径（`radius=carrier_outer_r`）逐角度分布、bolt head 贴 flange 面圆周半径。非结构、折入 carrier visual。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | carrier_radius_scale[0.90,1.12]、ring_radius_scale[0.90,1.12]、side_gear_scale[0.90,1.10]、n_bolt 8–12（见 §7）。非-continuous 关节运动包络：唯一非-continuous 活动关节 = locker `carrier_to_lockcollar` PRISMATIC 轴(1,0,0)，行程 [0(脱开,外侧), 0.018(咬合,内滑)]，开启方向 +X。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（continuous 齿轮采 {0,±90°,180°} —— 齿轮绕自身对称轴自转，扫掠体≈静态盘，低碰撞风险；captured 座用 element-scoped allow_overlap 全 pose 生效）；targeted `ctx.pose`：(1) side_gear_0 自转见证 mark 绕 X 轴移动、轴心不动；(2) locker collar 咬合位沿 +X 内滑且 collar 齿与 carrier dog 齿 X 向重叠。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal（cast iron / machined steel / gear steel / bronze）；配色 5：dark_iron(O)、nodular_grey、phosphate_black（磷化黑 ring）、oiled_bronze（Torsen 青铜蜗轮）、machined_bright。每 palette 给 body/machined/gear/tooth/bolt/accent 分色。材质大类覆盖 ≥ ceil(0.5×5)=3（cast iron + steel + bronze ≥3）。 |

**收尾自检**：0-9 seed 渲染须肉眼可见 5 种机构（open/clutch/viscous/torsen/locker）、开窗 vs 封闭壳、平盘 vs 锥冠 ring、2↔4 spider、5 配色，装饰贴合不悬空，齿轮/ collar 全程不穿模。

## 采样与覆盖审计

总组合数（离散骨架）：carrier_form(2) × ring_form(2) × mechanism(5) = 20；含 n_spider（open/clutch/locker 各 ×2）→ distinct slot-choice tuple ≈ 2×2×(3 spider 机构×2 + 2 非 spider 机构) = 2×2×8 = **32**；× palette(5) = 160 视觉组合。

理由：机械窄类，核心 identity 固定 side gear=2 + carrier + ring + pinion，主多样性由 ③/① 的 mechanism（5）+ carrier_form（2）+ ring_form（2）+ n_spider（2）离散骨架承载；连续 scale / 配色只做 ride-along。

seed_domain_policy：procedural_first（含 seed 0，不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 carrier_form、ring_form、mechanism、n_spider（加权，仅 spider 机构）、palette、n_bolt、连续 scale；`resolve_config` 做 gating（viscous/torsen 无 spider；lock_travel 派生；齿轮半径 inequality 回缩到开放中心）。无 curated/modulo 主表；无 regression override（初版）。
Topology target：1000-seed slot_choice tuple 覆盖用于成熟度观察（report-only）。合法离散结构空间 ≈32（受 side gear=2 硬约束、机构族有限、奇数 spider 排除），低于 300 —— 真实原因：差速器是紧约束机械窄类（source map budget=simple/8 anchors），组合空间本就小；已用满 5 机构族 + 2 carrier + 2 ring + N=4 sample 的诚实结构覆盖，不注水。
若使用 regression overrides：无（初版）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | carrier→ring→mechanism→n_spider(加权)→palette→n_bolt→scale，全 deterministic（含 seed 0） | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | viscous_lsd/torsen 强制无 spider（n_spider 语义 0）；dog_collar 仅 locker；clutch 盘仅 clutch_lsd；drive pinion 齿随 ring_form 重定位；齿轮半径 inequality 回缩到 carrier 开放中心 | 无悬空/穿模/轴错/闭合穿模/max-N/bulky/可选活动子件失败 |
| controlled local variation | carrier_radius/ring_radius/side_gear scale + n_bolt，全 clamp + inequality 回缩 | 比例变化不破坏 journal/shaft/hub 座配合、开放中心 clearance、joint origin、类别 identity |
| regression overrides | none | — |
| random sweep | 0-15 fast、0-35 final、corner；成熟审计 0-999 | contract failures；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| carrier_form | 2 | yes | no | 开窗 vs 封闭壳（真实仅此二形态族，已说明） |
| ring_form | 2 | yes | no | 平盘 spur vs 锥冠 bevel（③ 形态，真实仅此二族） |
| internal_mechanism | 5 | yes | yes | open/clutch/viscous/torsen/locker |
| n_spider(mult) | 2 | yes | no | {2,4} 权重档 |

## Validator
- slot_choices_for_seed 返回已实现 module 名（carrier_form / ring_form / mechanism / n_spider / palette）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling；无小型 curated/modulo 主表
- compatibility gating：viscous/torsen 无 spider；dog_collar 仅 locker；clutch/viscous 盘仅对应机构
- 连续 scale 在 resolve_config clamp/派生/inequality 回缩，不留到 builder 失败
- 关键 joint：`carrier_to_ring` FIXED；`carrier_to_side_{0,1}` CONTINUOUS(1,0,0)；`carrier_to_pinion` CONTINUOUS(0,1,0)；spider/planet CONTINUOUS；locker `carrier_to_lockcollar` PRISMATIC(1,0,0)
- captured 座（journal-in-collar / hub-on-crossshaft / shaft-in-snout / ring-on-boltshank / collar-on-hub）用 element-scoped allow_overlap
- side gear 恒为 2；复制 spider 遵循 naming/placement/joint policy
- Rule 5：`fail_if_parts_overlap_in_sampled_poses(ignore_fixed=True)` + side_gear 自转 targeted pose + locker collar 滑动 targeted pose

## Reject cases
- 某 seed side gear ≠ 2，或缺少 carrier / ring / drive pinion（核心 identity 缺失）
- side gear joint 非 CONTINUOUS(1,0,0)，或 ring joint 非 FIXED，或 pinion joint 非 CONTINUOUS
- viscous/torsen 仍发射 bevel spider（未 gating）；非 locker 出现 dog_collar
- 内部齿轮半径超出 carrier 开放中心 → 与壳壁大面积穿模（未 inequality 回缩 / 未 element-scoped allow）
- captured 座缺失 → side gear / pinion / spider 悬空（isolated part）或 island
- locker collar 行程过大中途穿模，或 PRISMATIC 轴错（应 +X 内滑咬合）
- 装饰（inspection port / bolt head / tooth facet）常数尺寸悬浮于缩放后壳面之外（未随宿主半径派生）
- ring gear 做成独立多 FIXED 碎片 / 内部支撑件（cross_shaft/drum/盘/dog teeth）做成独立 FIXED part（应折入 carrier visual，违反 Rule 1）

## 与相邻类别的边界
- 不该混入：普通变速箱 / 减速机 / 齿轮箱（无同轴双半轴输出，非差速分流）
- 不该混入：单个 spur/bevel 齿轮或齿轮对（无 carrier、无双输出）
- 不该混入：行星/周转减速单元作减速器用（sun+ring+carrier 减速，非半轴分流）
- 不该混入：spool / mini-spool 锁死实心轴（无差速动作，失独立输出身份，见 Blocked）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 初版；hub 型 parallel_children（carrier root）；side gear=2 恒定不作 multiplicity；n_spider{2,4} 为唯一 multiplicity 轴；ring_form/carrier_form 为 ③ 形态 slot；locker 保证 PRISMATIC 关节现身。 |

## 模板实现备注
- 共享 helper：`_carrier_shell_mesh`（open/closed，cadquery 环形 cheeks/barrel）、`_bevel_gear_visuals`（hub + 径向 Box 齿）、`_emit_side_gears`、`_emit_spiders`、`_ring_helical_visuals` / `_crown_wheel_mesh`、`_emit_drive_pinion`。
- captured element-scoped allow_overlap：journal∩collar、pinion_hub∩cross_shaft、worm_shaft∩carrier_body、pinion_shaft∩carrier_body(snout)、toothed_ring∩bolt_shank_i、collar∩side_0（滑动）、clutch/viscous 盘∩carrier_body / drum。
- 不动机构支撑件（cross_shaft / viscous_drum / clutch/viscous 盘 / carrier_dog_tooth / lock_boss / bolt_shank / inspection_port）折入 carrier root visual，不建独立 FIXED part（Rule 1）。
- Rule 5：`fail_if_parts_overlap_in_sampled_poses(ignore_fixed=True)` + side_gear 自转见证 + locker collar 滑动 targeted pose。
- Blocked：奇数 spider（N=3 bevel 不用于汽车差速器）；spool / 锁死实心轴（violates core_identity）。
```
