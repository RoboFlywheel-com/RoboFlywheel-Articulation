# Modular Spec — Agricultural / Tractor

## 元信息
| 项 | 值 |
|---|---|
| slug | `tractor` |
| template path | `agent/templates/tractor.py` |
| test path (optional) | `tests/agent/test_tractor_template.py` (skipped; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：单 `chassis` 根 part，四条命名 slot（operator_station / front_axle / implement /
hood_form）以 parallel-children + 小串链方式挂到 chassis（front_axle 是 chassis 的转向 child，
其上再挂前轮 continuous child；loader boom 挂 chassis，bucket 挂 boom；trailer 挂 chassis 再挂
trailer 轮），外加一根 grille-slat multiplicity 轴（FIXED 装饰内联在 chassis 的 grille 面）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 origins + 6 slot-fork variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读结论：
- **Origin A**（`rec_use-...-4133cc32`，蓝色封闭 cab + 后挂 trailer）：`chassis` 单根，`steering_axle`
  实心梁绕中央竖 pin REVOLUTE 转向（无 steering_wheel mimic），`trailer_frame` 绕后 hitch pin
  yaw REVOLUTE，6 轮各 CONTINUOUS（2 rear + 2 front + 2 trailer），前轮/拖车轮 `Mimic` 到
  rear_spin。轮子用 `TireGeometry`/`WheelGeometry`（BoltPattern count=6）。grille 用 `VentGrilleGeometry`。
  captured-pin 全部 element-scoped `allow_overlap` + `expect_overlap`，无 MatingContract（grandfather）。
- **Origin B**（`rec_use-...-482a6ef6`，绿色 John Deere 敞开站）：`chassis` 单根，独立旋转
  `steering_wheel` part（`steering_wheel_turn` REVOLUTE），`front_axle` 实心梁 REVOLUTE 转向且
  `Mimic(joint="steering_wheel_turn", 0.36)`，`hitch` 三点提升臂 REVOLUTE，4 轮各 CONTINUOUS。
  `long_hood`+`hood_raised_spine` 盒式 hood，`front_grille_panel`+10 根 `grille_slat_{idx}` 竖栅（Rule1
  内联装饰），弧形 `_arc_fender_geometry` mesh 后挡泥板。这是模板主骨架来源（最参数化）。
- 6 variants 各改一根主结构轴、其余保持 B/A baseline：`rops`（2-post ROPS tube 拱）、`tricycle`（窄前
  track）、`singlefront`（单前轮 yoke）、`loader`（tower+boom+bucket 双 REVOLUTE，基于 A）、`roundhood`
  （cadquery 圆鼻 hood mesh）、`grille6`（栅 N=10→6）。

## 核心身份

农用 **拖拉机（Tractor）**：一台在地面滚动的牵引底盘——**大后轮 + 小前轮**（后 Ø 明显 >1.55× 前），
长引擎 hood 在前、司机站在后、前端散热 grille、竖排气管、后牵引/提升装置。核心运动学：**每个车轮各绕
自己真实车轴 CONTINUOUS 自转**、**前轴/转向机构绕竖直 pin REVOLUTE 转向**、后端 implement（三点提升 /
装载 boom+curl / 拖车 yaw）为 REVOLUTE。成熟域 = 单体自走式轮式拖拉机。

不该混入：割草机 / lawn tractor（无 hood/grille 引擎前置识别、无大小轮对比——见 Powertools_Lawn_mower）、
铰接式装载机 / 挖机（articulated frame 中折 + 无小前轮身份）、通用四轮 vehicle/toy car（等大四轮、无
引擎 hood+grille+竖排气+大小轮对比的拖拉机识别）。

## 槽位 + 候选模块表

### Slot A：operator_station（司机站；决定是否封闭 cab / 敞开）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| enclosed_cab | forked_anchor | A `rec_use-...-4133cc32` | L116-L150 | eligible if compatible | cab_roof + rain_cap + 4 posts + 前/后风挡 + 侧窗 glass + 门板 + 后视镜；封闭玻璃驾驶室（chassis 内联 visual），座椅在内 |
| open_bare | forked_anchor | B `rec_use-...-482a6ef6` | L231-L243 | eligible if compatible | operator_platform + seat_cushion + seat_back + dash_cowl，无顶无护架；纯敞开 |
| open_ROPS | forked_anchor | `rec_tractor_var_rops` | L277-L320 | eligible if compatible | open_bare + 一根 `tube_from_spline_points` 连续 2-post ROPS 拱（两立柱+顶横梁）+ 底座板 + gusset；开放翻滚护架 |

（三者都共用后置 `steering_wheel` 旋转 part + `steering_column`，由 station 提供的转向柱锚点定位——见 §6。）

### Slot B：front_axle（前轴/转向机构；决定前轮数与前 track）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wide_standard | forked_anchor | B `rec_use-...-482a6ef6` | L299-L316 | eligible if compatible | 宽实心 `front_axle_beam` + 中央 pivot_pin + tie_rod + 2 spindle + 2 knuckle_boss；2 前轮 y≈±0.66；整梁 REVOLUTE 转向，2 前轮 CONTINUOUS |
| narrow_tricycle | forked_anchor | `rec_tractor_var_tricycle` | L300-L311 | eligible if compatible | 同 part tree 但梁缩短 + spindle 内拉到 y≈±0.10；2 前轮近中线（row-crop tricycle） |
| single_front | forked_anchor | `rec_tractor_var_singlefront` | L297-L312 | eligible if compatible | `steering_yoke`（kingpin_stem + yoke_crown + 2 fork_arm + 2 axle_stub + drag_link）夹持 **1** 居中前轮；yoke REVOLUTE 转向 + 1 前轮 CONTINUOUS（轮数 4→3） |

### Slot C：implement（后端作业装置；互斥单选）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| plain_drawbar | forked_anchor | A `rec_use-...-4133cc32` | L153-L158 | eligible if compatible | 仅后横梁 + drawbar + clevis 板 + hitch_pin_lug 内联 chassis visual（Rule1，无 child、无关节）；最简牵引杆 |
| three_point_hitch | forked_anchor | B `rec_use-...-482a6ef6` | L318-L329, L386-L394 | eligible if compatible | 独立 `hitch` part（drawbar + 2 lift_arm + hitch_pivot_pin + clevis）绕后 pivot REVOLUTE 升降 |
| front_loader | forked_anchor | `rec_tractor_var_loader` | L221-L367 | eligible if compatible | hood 侧 tower（内联 chassis visual）+ `loader_boom`（2 arm + cross tube + lift_cylinder）REVOLUTE 举升 + `loader_bucket`（back/floor/side/cutting_edge）REVOLUTE 翻斗 |
| towed_trailer | forked_anchor | A `rec_use-...-4133cc32` | L162-L189, L208-L216, L312-L330 | eligible if compatible | `trailer_frame`（tongue + coupler + a-frame + 木质 cargo bed + underframe + axle）绕后 hitch pin yaw REVOLUTE + 2 trailer 轮 CONTINUOUS |

### Slot D：hood_form（③ 主体形态家族 / Primary Form Family；form_subtype = Volumetric Envelope Form）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| long_flat | forked_anchor | B `rec_use-...-482a6ef6` | L189-L190 | eligible if compatible | 盒式 `long_hood` Box + `hood_raised_spine` Box 顶脊；平直实用长引擎罩（Volumetric Envelope: 直棱柱包络） |
| rounded_vintage | forked_anchor | `rec_tractor_var_roundhood` | L195-L205 | eligible if compatible | 单 `mesh_from_cadquery` 圆角盒（`.edges("\|Z").fillet` + 顶棱 fillet），复古圆鼻整壳；同 mount、同接口，只换体量包络 |
| stepped_modern | world_knowledge_extrapolation(仅③) | anchors: long_flat(B) + rounded_vintage(var) + reviewer | 生成函数 `_hood_stepped_mesh`（cadquery 两级台阶盒 union） | eligible if compatible | 同 part tree（单 hood 壳 visual）、同 primitive 家族（cadquery mesh）、同 chassis mount；只改宏观体量为**前低后高的阶梯楔形**现代罩（Volumetric Envelope Form）。Rule3 内，两道闸 sweep 必过 + reviewer 背书 |

硬约束核对：A/B/C 各 3-4 个 source-backed candidate（≥3）；D 有 2 个 forked_anchor + 1 个 ③ 世界知识外推
（合法：换 Volumetric Envelope 原型即结构差异，非只换尺寸/涂装）。无单-candidate slot。

## 槽位图（slot graph）

pattern: mixed（chassis 为唯一根，其余以 parallel-children + 小串链挂接）

```
                         chassis (root)
   ┌───────────┬──────────────┼───────────────┬─────────────────────┐
   │           │              │               │                     │
operator_station  hood_form   front_grille   [rear implement]   steering_wheel
 (inline visuals) (inline mesh)  panel+slat×N   (Slot C)         (part)
   │                              (multiplicity)   │                 │
 (ROPS arch=part? no →           FIXED inline    ┌─┴──────┐    steering_wheel_turn
  inline chassis visual)                          │        │      REVOLUTE z
                                                  │        │        │
   front_axle (part) ──REVOLUTE z (steer, Mimic←steering_wheel_turn)─┘
        │                                         │        │
   front_wheel(s) ──CONTINUOUS y (spin)      three_point  towed_trailer
   (child of front_axle)                      _hitch      (trailer_frame part)
                                              (part)          │ yaw REVOLUTE z
   rear_wheel_0/1 (part) ──CONTINUOUS y      REVOLUTE y   trailer_wheel_0/1
   (child of chassis)                                     CONTINUOUS y (child of trailer_frame)

   front_loader:  chassis --REVOLUTE y--> loader_boom(part) --REVOLUTE y--> loader_bucket(part)
                  (loader tower = inline chassis visual; boom pivots directly off chassis)
```

跨 slot 连接接口点位与关节：
- **chassis → front_axle**：接口 = chassis 前 `front_bolster`/`front_pedestal` casting 的竖直 pivot pin 面
  （captured-pin，pin 埋在 casting 内）；joint = REVOLUTE，axis=(0,0,1)，origin=(前 pivot x, 0, 0.40)，
  `Mimic(steering_wheel_turn, 0.36)`，range ±0.45·steer_scale。无 MatingContract（captured-pin grandfather）。
- **front_axle → front_wheel_i**：接口 = spindle/axle_stub 圆柱（穿入轮 hub）；joint = CONTINUOUS，axis=(0,1,0)，
  origin 在 spindle 端（轮 hub 中心，symmetry centerline）。captured-pin grandfather + element allow_overlap。
- **chassis → steering_wheel**：接口 = `steering_column` 顶端（hub 坐柱顶）；joint = REVOLUTE，axis=(0,0,1)
  （沿倾斜柱），range ±1.25·steer_scale。captured-pin（hub on column）grandfather。
- **chassis → rear_wheel_i**：接口 = `rear_axle_housing`/stub 圆柱；CONTINUOUS，axis=(0,1,0)，origin 在轮 hub
  中心。grandfather + allow_overlap。
- **chassis → hitch**（three_point_hitch）：接口 = `rear_hitch_mount` 的 pivot pin；REVOLUTE，axis=(0,1,0)，
  range [-0.30,+0.42]·hitch_scale。grandfather（pin through bracket）。
- **chassis → trailer_frame**（towed_trailer）：接口 = 后 drawbar `hitch_pin_lug`；REVOLUTE yaw，axis=(0,0,1)，
  range ±0.24。trailer 局部坐标以 hitch pin 为原点。grandfather。
- **chassis → loader_boom**（front_loader）：接口 = hood 侧 tower 顶 `tower_pivot_pin`（inline chassis visual）；
  REVOLUTE，axis=(0,-1,0)（正 q 抬升 boom），range [-0.50,+0.75]·loader_scale。grandfather。
- **loader_boom → loader_bucket**：接口 = boom 尖 `bucket_curl_pin`；REVOLUTE，axis=(0,1,0)，range
  [-0.80,+1.00]·loader_scale。grandfather。
- **operator_station / hood_form / grille slats**：全 FIXED-style 内联 chassis visual（Rule1），不产生 joint。
  （ROPS 拱、cab、hood mesh、栅条都是 chassis 表面几何，非独立活动 part。）

互斥/可选：Slot C 四选一（互斥）；front_loader 与其余 implement 互斥；trailer 仅在 towed_trailer 出现；
front_axle 决定前轮数（3 vs 4，非 N-sweep）。

## 每槽位 Module Emits / Interfaces

### Slot A / enclosed_cab
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（全部 cab_roof/posts/glass/门/镜 内联 chassis visual，Rule1） | A / L116-L150 |
| internal joints | 无 | — |
| upstream interface | chassis operator_platform 顶面（座椅+柱脚落点） | A / L64 |
| downstream interface | 提供 `steering_column` 顶端锚点给共享 steering_wheel（cab 内） | A / L139-L140 |

### Slot A / open_bare
| emits | parts=无（platform/seat/dash 内联 chassis visual） · joints=无 | B / L231-L243 |
|---|---|---|
| upstream interface | chassis 后段顶面 | B / L232 |
| downstream interface | `steering_column` 顶端锚点（敞开、外露） | B / L236-L242 |

### Slot A / open_ROPS
| emits | parts=无（ROPS 拱 tube mesh + 底板 + gusset 内联 chassis visual，Rule1；连续单管拱是一条几何，不活动） · joints=无 | rops / L277-L320 |
|---|---|---|
| upstream interface | operator_platform 顶（ROPS 底座板落点） | rops / L307-L308 |
| downstream interface | `steering_column` 顶端锚点 | B / L236-L242 |

### Slot B / wide_standard | narrow_tricycle | single_front
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_axle`（或 `steering_yoke`）+ 1-2 `front_wheel*`（各独立 part） | B L299-L316 / tricycle L300-L311 / singlefront L297-L312 |
| internal joints | 每前轮 CONTINUOUS `front_wheel*_spin`（axis y，origin 在 spindle/axle_stub） | B L368-L385 / singlefront L364-L372 |
| upstream interface | chassis 前 casting 竖 pivot pin（REVOLUTE steer，Mimic steering_wheel_turn） | B L331-L340 |
| downstream interface | 前轮外缘（落地面 z=front_r） | B L308-L316 |

### Slot C / plain_drawbar
| emits | parts=无（drawbar/clevis/lug 内联 chassis rear visual，Rule1） · joints=无 | A / L153-L158 |
|---|---|---|
| upstream interface | chassis 后端顶面 | A / L153 |
| downstream interface | 无（终端） | — |

### Slot C / three_point_hitch
| emits | parts=`hitch` · joints=`chassis_to_hitch` REVOLUTE axis y | B / L318-L329, L386-L394 |
|---|---|---|
| upstream interface | chassis `rear_hitch_mount` pivot（后 pin） | B / L292, L386-L394 |
| downstream interface | 提升臂末端（挂具） | B / L321-L322 |

### Slot C / front_loader
| emits | parts=`loader_boom` + `loader_bucket`（tower 内联 chassis visual） · joints=`chassis_to_loader_boom` REVOLUTE(y) + `boom_to_loader_bucket` REVOLUTE(y) | loader / L221-L367 |
|---|---|---|
| upstream interface | hood 侧 tower 顶 `tower_pivot_pin`（inline chassis visual） | loader / L253-L258 |
| downstream interface | boom 尖 `bucket_curl_pin` → bucket | loader / L297-L302 |

### Slot C / towed_trailer
| emits | parts=`trailer_frame` + 2 `trailer_wheel*` · joints=`chassis_to_trailer_frame` yaw REVOLUTE(z) + 2 CONTINUOUS(y) | A / L162-L189, L208-L216, L312-L330 |
|---|---|---|
| upstream interface | 后 drawbar `hitch_pin_lug`（trailer 局部原点 = hitch pin） | A / L156, L208-L216 |
| downstream interface | 无（终端拖挂） | — |

### Slot D / long_flat | rounded_vintage | stepped_modern
| emits | parts=无（hood 壳 = 单/双 chassis visual，Rule1） · joints=无 | B L189-L190 / roundhood L195-L205 / gen |
|---|---|---|
| upstream interface | chassis engine_block 顶面（hood 坐落） | B / L188-L190 |
| downstream interface | 前端接 grille panel | B / L202 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| operator_station | enum | enclosed_cab / open_bare / open_ROPS | — | choice | deterministic sampler | Slot A |
| front_axle | enum | wide_standard / narrow_tricycle / single_front | — | choice | deterministic sampler | Slot B |
| implement | enum | plain_drawbar / three_point_hitch / front_loader / towed_trailer | — | choice | deterministic sampler | Slot C |
| hood_form | enum | long_flat / rounded_vintage / stepped_modern | — | choice | ③ Primary Form Family | Slot D |
| palette_style | enum | jd_green / belarus_blue / massey_red / kubota_orange / newholland_blue / vintage_grey | jd_green | choice | `rng.choice(PALETTE_STYLES)` → mats | ⑥ / world palette |
| n_grille_slats | int(mult) | [4,16]（product 域）；测试偏小 | 10 | conditional | 见 §8；FIXED 内联；N 由 grille 面宽等距派生 pitch | B L203-L204 / grille6 |
| rear_wheel_scale | float | [0.88, 1.12] | 1.0 | independent | clamp；驱动 rear_r 与所有后轮 z（belly-anchored） | B L308-L310 |
| front_wheel_frac | float | [0.48, 0.56] | 0.52 | independent | clamp（保证 rear_r/front_r ≥ 1.78 > 1.55 身份） | B L313-L316 |
| (—) rear>front 身份 | constraint | — | — | inequality | `front_r = rear_r * front_wheel_frac`（equation）→ ratio∈[1.78,2.08]，恒 >1.55 | 身份 check |
| front_r | float | derived | — | equation | `= rear_r * front_wheel_frac`；前轮中心 z=front_r（落地） | B L313-L316 |
| wheelbase_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放前 pivot x 与后轴 x（对称，不动 z） | B L331/L350 |
| rear_track_scale | float | [0.92, 1.08] | 1.0 | independent | 后轮 |y|；rear_axle_housing 长度随之 | B L350-L367 |
| front_track_scale | float | [0.92, 1.08] | 1.0 | conditional | 仅 wide_standard 生效（tricycle 固定窄、single 无 track） | B L368-L385 |
| hood_length_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 hood x-extent + grille x（不动 z / ground） | B L189-L190 |
| steer_limit_scale | float | [0.85, 1.10] | 1.0 | independent | steering_wheel_turn 与 front steer(mimic) range | B L338/L348 |
| hitch_lift_scale | float | [0.85, 1.12] | 1.0 | conditional | 仅 three_point_hitch；缩放 lift range [-0.30,0.42] | B L393 |
| loader_range_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 front_loader；缩放 lift/curl range | loader L320/L366 |
| (—) 前转向 clearance | constraint | — | — | inequality | 全 steer 极限下前轮不得撞 hood/chassis：front track/wheelbase 组合在 `resolve_config` 保证前轮 y 外缘 > hood 半宽 | 接口/clearance |

连续尺寸采样契约：先采 independent（rear_wheel_scale / wheelbase / track / hood_length / steer / *_scale）
→ equation 派生 front_r 及所有 wheel-z / axle-z / fender-arc-radius（单源 helper `_wheel_dims`）→
inequality 投影（rear>front 身份、前转向 clearance）→ conditional 解析（front_track 仅 wide、hitch/loader
range 仅对应 implement）。所有约束在 `resolve_config` 求解，builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**每-seed 预算：≤ 18s**（依据：6 轮 × [TireGeometry+WheelGeometry] mesh + 弧 fender mesh + 可选
cadquery 圆鼻/阶梯 hood + 可选 ROPS tube + 可选 trailer 木箱 + steering torus——中重放样类）。
降本手段：**相同轮型共享同一 `Mesh` 对象**（rear-type 生成一次给 2 后轮、front-type 生成一次给
2/1 前轮 + 2 trailer 轮，最多 2 tire + 2 rim mesh 而非 6+6）；cadquery hood `tolerance≈0.0012`/
`angular_tolerance≈0.2`；ROPS tube `radial_segments=12,samples_per_segment=8`；fender arc `segments=24`；
BoltPattern 小 count。超预算先降精度再迭代。`--compile-timeout 120`（~3× 预算，仅看门狗）。

## 8. Multiplicity / Copy Logic

**一根 multiplicity 轴：`n_grille_slats`**
- `count_param`：`n_grille_slats`；`N_range`：产品域 `[4,16]`，模板测试偏小（sampler 权重：小 N 高频）。
  sampling domain 权重档：`{4,5,6,7,8,9,10}` 高频、`{11..16}` 稀有（`rng.choices` 递减权重）。
- copied object：`grille_slat_{idx}` —— 竖向细 Box 栅条，等距沿 grille 面 Y 分布（pitch = grille 面净宽/(N+1)）。
- naming / placement：`for idx in range(N)` 共享 `_grille_slat` 几何 helper，均匀 Y 摆放；uniform policy。
- joint policy：**FIXED 装饰，内联为 chassis.visual**（Rule1，无 joint），嵌入 `front_grille_panel` 面。
- source/gating：B L203-L204（N=10）/ `rec_tractor_var_grille6`（N=6）；N 编入 `slot_choices` 为
  `("grille_slat_count", f"n{N}")`（N 只覆盖不计 distinct）。

wheels 数量**不是** N-sweep：前轮数（3 vs 4）由 Slot B（single_front vs 其余）离散决定；trailer 轮由
Slot C 决定；后轮恒 2。轮 lug 数是 `BoltPattern(count=...)` 参数（恒 ≥4 all-positive，非 slot、非 N-sweep）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | operator_station 3（cab/open/ROPS，影响内联 part 图与顶部结构）× front_axle 3（wide 2轮 / tricycle 2轮 / single 1轮——**改前轮 part 数 4↔3** 与 spin 边数）× implement 4（drawbar 无 child / hitch +1 REVOLUTE / loader +2 part+2 REVOLUTE / trailer +1 part+1 yaw+2 轮）。全 forked_anchor（见 slot 表）。distinct 结构图 ≥ 3×3×4 去 N。 |
| └ multiplicity | 同构件 ×N | 有 | `n_grille_slats` N∈[4,16]，权重小 N 高频（§8）。source: B/grille6。 |
| ② 关节类型 | 边换 type/轴 | 有 | CONTINUOUS（每轮自转 axis y）、REVOLUTE z（steering_wheel_turn + front steer mimic + trailer yaw）、REVOLUTE y（hitch lift / loader lift / loader curl）。全 source-backed；每种类型都会在 sweep 出现（wheels 恒有 continuous；steer 恒有 revolute-z；implement 带出 revolute-y）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | **hood_form** 登记进 slot_choices：long_flat（盒棱柱）/ rounded_vintage（cadquery 圆鼻整壳）/ stepped_modern（阶梯楔形）。form_subtype = **Volumetric Envelope Form**。前二 forked_anchor（B / roundhood），后一 world_knowledge_extrapolation（同 part tree/primitive/mount，只换体量包络）。 |
| ④ 表面装饰 | 不改轮廓的表面叠加 | 有 | grille 竖栅 style + N（§8）、hood 侧 `side_stripe`/`john_deere_letter` 品牌字带、`number_badge`、竖排气 cap、headlight bezel。record_only + host-conformal world_knowledge_extrapolation（随 palette 换色带/字）。派生序 ③→⑤→④（装饰读最终 hood/grille 面）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | rear_wheel_scale[0.88,1.12] + front_wheel_frac[0.48,0.56]（Ø 比恒>1.55）、wheelbase[0.90,1.10]、track[0.92,1.08]、hood_length[0.85,1.15]。关节运动包络：steering_wheel_turn axis-z [−1.25,+1.25]·s（driver）、front steer mimic ±0.45·s（front 全 steer 不撞 hood——inequality）、hitch lift axis-y [−0.30,+0.42]·s（后端抬升）、loader lift axis-y [−0.50,+0.75]·s、loader curl axis-y [−0.80,+1.00]·s、trailer yaw axis-z ±0.24。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=28, ignore_fixed=True)` + 每机构 targeted `ctx.pose`（后轮自转 valve 位移、前转向前轮 x 位移、hitch/loader/trailer 端位移）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted(metal) + rubber + glass + steel/chrome；配色 6：jd_green(绿+黄)/belarus_blue/massey_red(红+灰)/kubota_orange/newholland_blue(蓝+白)/vintage_grey。材质大类覆盖 ≥ ceil(0.5×6)=3（painted/rubber/glass/metal 均现）。 |

收尾自检：batch 0-9 需肉眼看到 3 种 hood 形、cab/ROPS/敞开三种站、单/双前轮、4 种 implement、栅条疏密、
6 涂装各现，且各关节全程不穿模。

## 拓扑多样性审计

总组合数：station(3) × front_axle(3) × implement(4) × hood(3) × N(4..16≈13 sampled ≈取若干) =
3×3×4×3 = **108 离散骨架组合**（未计 N 与连续 scale）。计 N 覆盖后远超 100。

理由：4 个 registered slot 每个 ≥3 candidate 且全 reachable（无 gating 屏蔽任何 candidate——全 108 组合合法），
N 覆盖 ≥3 档；1000-seed slot choice tuple distinct 预计 按 ≥300 富类别口径观察。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对 4 个 enum 各
`rng.choice`、N 加权 `rng.choices`、连续 scale `rng.uniform`，seed=0 不特殊。compatibility matrix：**全 108
组合合法**（无互斥对）——front_loader/trailer/hitch/drawbar 单选即互斥由 Slot C 保证；所有 station×front×hood
组合物理相容（loader tower 固定 chassis mount 不依赖 hood mesh；trailer 挂后端不依赖前部；single_front 与
loader 上下分层不冲突）。gating 仅做**连续可行域投影**（rear>front 身份、前转向 clearance、N pitch clamp），
不屏蔽任何离散 candidate。random sweep：seeds 0-35 初测 + corner。regression overrides：none（除非 sweep 暴露）。

Controlled local parameterization：rear_wheel_scale / front_wheel_frac(equation→front_r) / wheelbase_scale /
rear_track_scale / front_track_scale(conditional wide) / hood_length_scale / steer_limit_scale /
hitch_lift_scale(conditional) / loader_range_scale(conditional)。全部在 `resolve_config` clamp / 派生 /
投影，单源 helper `_wheel_dims` 统一 wheel-z / axle-z / fender-radius，不破坏 captured-pin 接口与身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rng：station→front_axle→implement→hood→N→palette→scales；无 curated 表 | slot_choices_for_seed == build 选择 |
| compatibility matrix | 全 108 组合合法；C 单选互斥；连续仅投影不屏蔽 | 无 floating / 无穿模 / 前转向 clearance / N pitch / rear>front |
| controlled local variation | 上列 scale + clamp/derive；wheel-z 单源 | 比例变而接口/落地/关节原点/身份不破 |
| regression overrides | none | — |
| random sweep | seeds 0-35 初测，0-999 成熟审计 | contract failures；axis_realization |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| operator_station | 3 | yes | yes | |
| front_axle | 3 | yes | yes | |
| implement | 4 | yes | yes | |
| hood_form | 3 | yes | yes | 2 forked_anchor + 1 ③ 外推 |
| grille_slat_count (N) | 覆盖 | yes | — | N 只覆盖不计 distinct |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（station/front_axle/implement/hood + grille N）
- `config_from_seed` 对全部 seed（含 0）用 deterministic procedural sampling
- compatibility：C 单选互斥；无非法离散组合被采样
- 无 regression override 轮换
- 主 seed domain 非 curated 小表
- 连续 scale 全 clamp/派生（wheel-z / front_r / fender-radius 单源），不破接口/落地/joint 原点/身份
- equation/inequality/conditional 全在 `resolve_config` 求解
- 关键 captured-pin 接口存在：spindle/axle_stub 入轮 hub、front pivot pin 埋 casting、hitch/trailer/loader
  pin——各 element-scoped `allow_overlap`（无 MatingContract，grandfather）
- 关节 type/axis/range：wheel spins CONTINUOUS(y)；steer REVOLUTE(z) 且 front mimic steering_wheel_turn；
  hitch/loader REVOLUTE(y)；trailer yaw REVOLUTE(z)
- copied grille slats 遵守 `grille_slat_{idx}` 命名 + 等距 + 统一 FIXED-inline policy
- 身份：rear tire Ø > 1.55× front；6/4/3 轮各落地 z≈0

## Reject cases

- 前轮≥后轮 或 无大小轮对比 → 非拖拉机（掉成通用四轮 vehicle）
- steering 到极限时前轮撞 hood/chassis（前 track/wheelbase clearance 未投影）
- wheel/tire 用 Box/Cylinder 占位替代 TireGeometry/WheelGeometry（违反 HARD RULE③）
- BoltPattern count=1 或 circle_diameter=0（崩溃）——必须 all-positive
- 装饰栅条/字带做成独立 FIXED part 而非 chassis inline visual（违反 Rule1，浮岛）
- hood mesh 换形后 grille/side_stripe 常数尺寸悬浮不贴（违反 Rule4 派生序 ③→⑤→④）
- loader boom/bucket 或 hitch 全行程穿 hood/前轮/地面（未做 sampled + targeted 运动测试）
- steering_wheel 与 front steer 未耦合（front 不随 steering_wheel_turn 动）
- 轮自转把轮心平移（origin 不在 hub 中心）

## 与相邻类别的边界

- 不该混入：Powertools / Lawn_mower（乘骑割草机——无 hood+grille 引擎前置识别、无大小轮对比、有割草甲板）
- 不该混入：铰接式装载机 / 挖掘机（articulated frame 中折 + 无小前轮拖拉机身份——留模板/gate 排除）
- 不该混入：通用 Vehicle/Toy car（等大四轮、无引擎 hood+竖排气+大小轮对比）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | ③ hood_form 含 1 个 world_knowledge_extrapolation candidate（stepped_modern），同 part tree/primitive/mount 只换 Volumetric Envelope，Rule3 内，需 sweep + reviewer 背书类别忠实。captured-pin 关节全 grandfather（无 MatingContract），仿 5 星源 allow_overlap 模式。 |

## 模板实现备注（可选）

- 共享 helper：`_wheel_meshes`（TireGeometry+WheelGeometry，按 large/small 复用 Mesh 对象降编译）、
  `_wheel_dims`（单源 wheel-z/axle-z/fender-radius）、`_arc_fender_geometry`（弧 mesh，segments=24）、
  `_grille_slat`、`_add_cyl_x/y/z`。
- captured-pin overlap 全 element-scoped `allow_overlap`（照抄各源 run_tests 的 allow/expect 块）：
  front spindle↔rim、rear housing↔rim、front pivot pin↔bolster、hitch pin↔mount、trailer axle↔rim、
  loader boom bracket↔tower pin。
- loader tower 折为 chassis inline visual（避免 origin loader 的 FIXED joint），boom 直接 pivot off chassis。
- 略去 origin A 的 mud_patch FIXED part；改为在轮 part 内联一个 off-center `valve_stem` visual 证明自转
  （Rule1，不加 FIXED joint）。
- steering_wheel 恒为独立旋转 part（三种 station 都有），前轴 `Mimic(steering_wheel_turn)`——统一转向语义。
```
