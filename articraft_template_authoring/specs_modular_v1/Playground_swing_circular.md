## 元信息
| 项 | 值 |
|---|---|
| slug | `circular_ring_swing` |
| template path | `agent/templates/Playground_swing_circular.py` |
| test path (optional) | `tests/agent/test_circular_ring_swing_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## HALO 不变量（类别身份硬约束 — 任何 candidate / seed 都不得违反）

座具是一个 **人要坐进去的圆环**。环永远是 **开口的 hoop / halo**：环心从不被实心盘、平台、甲板、绳网或任何面填满。木座只沿环的 **内侧下弧** 铺设，整个环心保持敞开，让人坐在环内、腿和身体有空间。Slot B 的三个 candidate 只在 **环截面**（圆管双环 ↔ 单扁钢带）与 **座弧深度**（146° ↔ 214°）上不同，全部是开口环。**实心圆盘平台座（solid disc）与绳网碟座（net saucer）属于出类目形态，永久排除，绝不作为 candidate。** 早期 `var_disc` / `var_net` 因违反本不变量已删除并替换为 `deep_cradle_ring` / `flat_band_ring`。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (1 converged parent + 6 rating-5 workbench forks) |
| samples_adopted_as_module_sources | 7 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

已完整读取本类别全部 7 个 5 星样本的 `model.py`：1 个 converged parent (`circular_ring_swing_pergola`) 与 6 个 rating-5 workbench forks（aframe / arch / cradle / band / p3 / p4）。这 7 个样本恰好张成本模板的三条多样性轴：support_frame（pergola / a-frame / arch）、ring_seat（bench / deep-cradle / flat-band，**三者皆开口环 halo**）、suspension multiplicity（single chain / 3-point bridle / 4-point bridle）。所有样本都保留同一身份核心：固定上方支架 → REVOLUTE `canopy_swing`（fore/aft，轴 +X，±45°）→ CONTINUOUS `ring_spin`（绕 +Z）→ 开口圆环座。无样本被排除。

## 核心身份

`circular_ring_swing` 是一个圆环座椅秋千：一个可坐的 **开口刚性圆环**（环心敞开、人坐进环内）从固定的上方支架悬吊下来，整体既能绕一条水平梁轴 **fore/aft 摆动 (REVOLUTE)**，又能绕自身竖直吊链轴 **自旋 (CONTINUOUS)**。其唯一识别身份是这条 **2 关节链：水平摆动 + 竖直自旋**，悬挂在一个静止的顶部 frame 下，下端是一个 **刚性开口圆环** 座具（木座只铺内侧下弧，环心永远敞开 —— 见 HALO 不变量）。

成熟默认域是 backyard / park-equipment 比例：约 3.0 m 宽支架、约 2.55 m 顶吊点、OD≈1.5 m 的环座、离地 >0.30 m。悬挂可以是单条中心吊链，也可以是 N 点 bridle（多条腿从环缘等角点汇聚到 **一个** 顶部 swivel），但 bridle 仍只产生一个 `ring_spin` swivel，**不构成闭环**。

不应混入：普通线性座板秋千（座具是平板/吊带，没有刚性圆环、没有自旋轴）、tire swing（轮胎软体，没有刚性圆环+座圈）、merry-go-round（地面安装的转盘，没有悬挂摆动）、以及 **任何把环心填满的实心盘 / 网碟座**（失去「坐进环内」的身份）。详见「与相邻类别的边界」。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_model-a-modern-circular-ring-swing-hanging-from-_20260610_085427_611739_83a6bd25` | `data/records/rec_model-a-modern-circular-ring-swing-hanging-from-_20260610_085427_611739_83a6bd25/revisions/rev_000001/model.py:L92-L138,L140-L197,L199-L238,L240-L264` | two_post_pergola frame、single_chain 悬挂、bench_ring_seat、2-关节链（canopy_swing + ring_spin）的 baseline |
| S2 | `rec_pcrs_var_aframe` | `data/records/rec_pcrs_var_aframe/revisions/rev_000001/model.py:L107-L204,L308-L331` | a_frame_support frame module（双 A 字撇腿 + 顶梁 + 百叶 + 脚板） |
| S3 | `rec_pcrs_var_arch` | `data/records/rec_pcrs_var_arch/revisions/rev_000001/model.py:L80-L165` | single_arch frame module（抛物拱梁 + 双脚 base bracket + crown collar 吊点） |
| S4 | `rec_pcrs_var_cradle` | `data/records/rec_pcrs_var_cradle/revisions/rev_000001/model.py:L59-L70,L201-L247` | **deep_cradle_ring** ring_seat（开口双铬环 + 32 木 `seat_plank_si` 沿更深下弧 θ163°→377°≈214°，板条爬高成低靠背；环心全开） |
| S5 | `rec_pcrs_var_band` | `data/records/rec_pcrs_var_band/revisions/rev_000001/model.py:L62-L72,L203-L251` | **flat_band_ring** ring_seat（CadQuery 单宽扁钢带 annulus `flat_band` R0.75/壁5mm/宽110mm + 22 木 `seat_plank_si` 沿下内弧；环心空 annulus 全开） |
| S6 | `rec_pcrs_var_p3` | `data/records/rec_pcrs_var_p3/revisions/rev_000001/model.py:L58-L107,L168-L264,L288-L313` | three_point_bridle 悬挂（hub + 3 `bridle_chain_i` 等角汇聚 + 环缘 anchors）；N-point swivel 收敛 idiom |
| S7 | `rec_pcrs_var_p4` | `data/records/rec_pcrs_var_p4/revisions/rev_000001/model.py:L47-L80,L139-L233,L234-L259` | four_point_bridle 悬挂（hub rod + swivel barrel + 4 `bridle_chain_i` 90° + 环缘 `bridle_anchor_i`） |

## 槽位 + 候选模块表

### Slot A：support_frame（固定上方支架 — 承 `canopy_swing` 顶吊点）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `two_post_pergola` | S1 | `model.py:L92-L138` | eligible if compatible | 双方钢柱 (x=±1.425, 0.15 sq) + 顶梁 (3.0×0.28) + 34 百叶 `fin_i` + 顶部 gusset 板 + 16 rivets；root part，向下游给中心顶吊点 (0,0,2.55)。 |
| `a_frame_support` | S2 | `model.py:L107-L204` | eligible if compatible | 两组 A 字架（每组前后两条 ±Y splay 撇腿在 apex 汇聚）+ 横向 cross brace + 脚板 `foot_plate_i` + 顶脊梁 `ridge_beam` + 百叶 + apex gusset/rivets；root part，apex 顶梁给同一中心吊点。 |
| `single_arch` | S3 | `model.py:L80-L165` | eligible if compatible | 单条抛物拱钢管梁 (`tube_from_spline_points`，half_span 1.40, height 2.70) + 双脚 base plate/gusset/bolts + crown collar/bracket 安装盘；冠顶给中心吊点，无顶梁百叶。 |

### Slot B：ring_seat（可坐 **开口** 圆环座 — 整体随 CONTINUOUS `ring_spin` 自旋；**永远是开口 halo，环心不填**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bench_ring_seat` | S1 | `model.py:L199-L238` | eligible if compatible | 双铬圆管环 `hoop_i` (R=0.725, tube 0.025, y=±0.0375) + 22 块木 `seat_plank_si` 沿下内弧 (θ 197°→343°≈146°) 跨双环成弧凳；环面 XZ 平面 (轴 Y)，**环心敞开**。 |
| `deep_cradle_ring` | S4 | `model.py:L201-L247` | eligible if compatible | 同款双铬圆管环 `hoop_i` (R=0.725) + 32 块木 `seat_plank_si` 沿 **更深** 下弧 (θ 163°→377°≈214°)，板条爬高至两侧形成低靠背 cradle；**环心仍全开**，仅座弧更深。 |
| `flat_band_ring` | S5 | `model.py:L203-L251` | eligible if compatible | **单宽扁钢带** `flat_band`（CadQuery `circle(0.75).circle(0.745).extrude` 成空心 annulus，宽 0.110）替代双圆管 + 22 块木 `seat_plank_si` 沿下内弧固定在带内壁；**annulus 环心全开**。 |

> Slot B 三候选差异是 **环截面 + 座弧深度**，不是「填不填环心」—— 三者环心一律敞开。
> 绝不引入 solid disc / net saucer（违反 HALO 不变量，出类目）。

### Slot C：suspension（悬挂脊柱 — 把 frame 顶吊点与 ring 连成 2-关节链；N 点采样）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_chain` | S1 | `model.py:L140-L197` | eligible if compatible | 单条中心吊链：eye-bolt `anchor_stem` + `anchor_eye` + 4 oval `chain_link_i`（交替 yz/xz 面）+ `hook_eye` + J `hook`；hook bowl 处 spin joint。对应 `suspension_point_count = 1`。 |
| `n_point_bridle` | S6 / S7 | `model.py:L168-L264` (S6) / `model.py:L139-L233` (S7) | eligible if compatible | 顶部 anchor stem/rod + hub plate/swivel barrel，N 条 `bridle_chain_i` 从 hub 等角发散到环缘 N 等角点的 `bridle_anchor_i`/lug；多链仍汇聚到 **一个** swivel。对应 `suspension_point_count ∈ {3,4}`（可扩 2）。 |

硬约束说明：
- Slot A、Slot B 各 3 个 candidate（满足 3-6 目标）；Slot B 三者全是开口环。
- Slot C 表面上 2 个 candidate（`single_chain` vs `n_point_bridle`），但 `n_point_bridle` 内部由 `suspension_point_count` N 驱动复制（见 Multiplicity），实际拓扑分支为 {N=1 single, N=2/3/4 bridle}，结构差异充分（hub plate 的有无、leg/chain 数量、环缘 anchor 数量都不同），不视为「只换数字」的伪 candidate。

## 槽位图（slot graph）

pattern: `mixed`（linear_chain 主干 + Slot C 的 multiplicity）

```text
support_frame (Slot A, root, fixed to ground)
  --[canopy_swing: REVOLUTE, origin=(0,0,RAIL_Z0≈2.55), axis=(1,0,0), ±45°]-->
suspension (Slot C, hanger_chain / bridle_hub)
  --[ring_spin: CONTINUOUS, origin=(0,0,SPIN_Z), axis=(0,0,1), unlimited]-->
ring_seat (Slot B, 开口环)
```

跨 slot 接口点位：

- `support_frame.downstream.top_pivot`：顶梁/apex/crown 下底面正中心，world (0, 0, RAIL_Z0)。所有 frame module 都必须在此给出同一条 fore/aft REVOLUTE 轴 (1,0,0) 与吊点 z；anchor stem 在此 socket 进梁体（intentional embed）。
- `suspension.upstream`：消费 top_pivot，emit `canopy_swing` REVOLUTE；anchor stem 顶端嵌入 frame 顶梁/crown collar。
- `suspension.downstream.swivel`：suspension-local (0,0,SPIN_Z) 处的竖直自旋接口，emit `ring_spin` CONTINUOUS（轴 Z）。`single_chain` 的 swivel 在 hook bowl；`n_point_bridle` 的 swivel 在 hub 中心。
- `ring_seat.upstream`：环顶 eyelet/clevis（single_chain）或环缘 N 等角 `bridle_anchor`（bridle）必须与 suspension 下端可见接触。bridle 的环缘锚点数量必须等于 `suspension_point_count`。

兼容性 gate：
- `single_chain` 三种 ring_seat 全兼容（eyelet 在环顶居中，三种开口环都不冲突）。
- `n_point_bridle` 三种 ring_seat 全兼容；bridle 腿落点按 N 等角落在环外缘 bore 上（圆管 `hoop` 或扁带 `flat_band` 的外周），半径 = 环半径×scale。三种 ring_seat 环心都敞开，bridle 腿无填充面可穿，唯一注意是落点附近 seat plank 的 allow_overlap。
- 所有 frame module × 所有 suspension × 所有 ring_seat 自由组合（3×2-with-N×3）；无互斥对。Bridle 收敛点的 swivel z 随 frame 顶吊点不变（始终中心吊）。

派生关系：`ring_spin` 始终是 suspension→ring；`canopy_swing` 始终是 frame→suspension。换 frame module 只改顶吊点 z 与 frame part tree，不改两关节语义。

## 每槽位 Module Emits / Interfaces

### Slot A / module `two_post_pergola`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `pergola_frame`：2 `post_i`、`top_rail`、34 `fin_i`、`gusset_*`、`rivet_*` | S1 / model.py:L92-L138 |
| internal joints | none（全静态 visual） | S1 / model.py:L92-L138 |
| upstream interface | root ground support；无 parent | S1 / model.py:L95-L101 |
| downstream interface | 顶梁下底中心 top_pivot (0,0,RAIL_Z0)，REVOLUTE 轴 (1,0,0) | S1 / model.py:L240-L254 |

### Slot A / module `a_frame_support`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `aframe_support`：4 `leg_*`（splay）、`foot_plate_i`、`brace_i`、`ridge_beam`、`fin_i`、`apex_plate_i`/`rivet_*` | S2 / model.py:L107-L204 |
| internal joints | none | S2 / model.py:L107-L204 |
| upstream interface | root ground support（脚板落地） | S2 / model.py:L143-L151 |
| downstream interface | apex 顶脊梁下中心 top_pivot (0,0,RAIL_Z0=APEX_Z)，REVOLUTE 轴 (1,0,0) | S2 / model.py:L308-L321 |

### Slot A / module `single_arch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `arch_frame`：`arch_beam`（拱钢管）、`foot_plate_i`、`gusset_i_j`、`bolt_i_j`、`crown_bracket` | S3 / model.py:L80-L165 |
| internal joints | none | S3 / model.py:L80-L165 |
| upstream interface | root ground support（双脚 base plate 落地） | S3 / model.py:L122-L161 |
| downstream interface | crown bracket 下中心 top_pivot (0,0,SWING_PIVOT_Z≈2.645)，REVOLUTE 轴 (1,0,0)；anchor stem socket 进 crown bracket | S3 / model.py:L154-L165 |

### Slot C / module `single_chain`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `hanger_chain`：`anchor_stem`、`anchor_eye`、4 `chain_link_i`、`hook_eye`、`hook` | S1 / model.py:L140-L197 |
| internal joints | none（模块内无关节） | S1 / model.py:L140-L197 |
| upstream interface | 消费 frame top_pivot，emit `canopy_swing` REVOLUTE；stem 顶嵌入梁 | S1 / model.py:L240-L254 |
| downstream interface | hook bowl 处 swivel，suspension-local (0,0,SPIN_Z=-0.576)，emit `ring_spin` CONTINUOUS 轴 Z | S1 / model.py:L256-L264 |

### Slot C / module `n_point_bridle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `bridle_hub`：`anchor_stem`/`drop_rod`、`anchor_eye`/`anchor_plate`、`hub`/`swivel_barrel`/`convergence_eye`、N 条 `bridle_chain_i` + 环缘 N 个 `bridle_anchor_i` | S6 / model.py:L168-L264；S7 / model.py:L139-L233 |
| internal joints | none | S6 / model.py:L168-L246 |
| upstream interface | 消费 frame top_pivot，emit `canopy_swing` REVOLUTE；stem/rod 顶嵌入梁 | S6 / model.py:L289-L302 |
| downstream interface | hub 中心 swivel，suspension-local (0,0,SPIN_Z=HUB_Z_LOCAL)，emit 单 `ring_spin` CONTINUOUS 轴 Z；N 条腿从 hub 发散到环缘 N 等角锚点（不构成闭环） | S6 / model.py:L304-L313 |

### Slot B / module `bench_ring_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `ring_seat`：`ring_eyelet`（或 bridle anchors）、`hanger_clevis`、2 `hoop_i`、22 `seat_plank_si`（θ 197°→343°） | S1 / model.py:L199-L238 |
| internal joints | none（整体随 ring_spin 旋转） | S1 / model.py:L199-L238 |
| upstream interface | 环顶 eyelet/clevis（single_chain）或环缘 N anchor（bridle）接 suspension 下端 | S1 / model.py:L202-L215 |
| downstream interface | 无（链尾载具） | — |
| **HALO** | 环心敞开，木座仅铺下内弧 146° | S1 / model.py:L228-L238 |

### Slot B / module `deep_cradle_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `ring_seat`：`ring_eyelet`、`hanger_clevis`、2 `hoop_i`（R=0.725，同 bench）、32 `seat_plank_si`（θ 163°→377°≈214°，爬高成低靠背） | S4 / model.py:L201-L247 |
| internal joints | none | S4 / model.py:L201-L247 |
| upstream interface | 同 bench（环顶 eyelet / 环缘锚点） | S4 / model.py:L203-L217 |
| downstream interface | 无 | — |
| **HALO** | 环心全开，座弧更深（214°）但绝不填心 | S4 / model.py:L229-L247 |

### Slot B / module `flat_band_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | child `ring_seat`：`ring_eyelet`、`hanger_clevis`、单 `flat_band`（CadQuery annulus，外 R0.75 / 内 R0.745 / 宽 0.110）、22 `seat_plank_si`（θ 197°→343°，固定在带内壁） | S5 / model.py:L203-L251 |
| internal joints | none | S5 / model.py:L203-L251 |
| upstream interface | 同 bench；扁带顶部居中接 eyelet / 环缘锚点 | S5 / model.py:L205-L217 |
| downstream interface | 无 | — |
| **HALO** | 扁带本身是空心 annulus，环心全开，仅是更宽的环截面 | S5 / model.py:L220-L251 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support_frame` | enum | `two_post_pergola`, `a_frame_support`, `single_arch` | `two_post_pergola` | choice | 由 deterministic procedural sampler 选择 Slot A | S1 / S2 / S3 |
| `ring_seat` | enum | `bench_ring_seat`, `deep_cradle_ring`, `flat_band_ring` | `bench_ring_seat` | choice | 由 sampler 选择 Slot B；三者皆开口 halo，与所有 suspension 兼容 | S1 / S4 / S5 |
| `suspension_style` | enum | `single_chain`, `n_point_bridle` | `single_chain` | conditional | `single_chain ⇔ N=1`；`n_point_bridle ⇔ N≥2`；由 `suspension_point_count` 派生 | S1 / S6 / S7 |
| `suspension_point_count` | int (N) | `[1, 4]`（样本覆盖 1,3,4；2 由构造外推） | `1` | independent (加权) | per-轴加权采样（小 N 偏多）；N=1→single_chain，N≥2→bridle | S1 / S6 / S7 |
| `palette_style` | enum | `galvanized_warmwood`, `powdercoat_charcoal`, `light_steel_chrome`, `forest_green_oak`, `bronze_oak` | `galvanized_warmwood` | choice | 仅改材质 rgba，不改拓扑；见 palette 小节 | S1 / S2 / S3 |
| `frame_width_scale` | float | `[0.85, 1.15]` | `1.0` | independent | frame 整体宽度（post 间距 / A-frame 间距 / arch span）×scale，clamp | S1 / S2 / S3 |
| `pivot_height_scale` | float | `[0.92, 1.10]` | `1.0` | independent | 顶吊点 z = base_pivot_z × scale；派生 chain/bridle 长度与离地间隙 | S1 |
| `hoop_radius_scale` | float | `[0.88, 1.12]` | `1.0` | independent | 环半径 (HOOP_R / BAND_OUTER_R)×scale；派生 plank 半径与 bridle 落点 | S1 / S5 |
| `seat_plank_count` | int | `[16, 34]` | bench 22 / cradle 32 / band 22 | conditional | 三种 ring_seat 均沿弧等角复制木板；cradle 弧更长默认更多板 | S1 / S4 / S5 |
| `fin_count` | int | `[24, 40]`（pergola/aframe 专用） | `34` | conditional | 仅 frame 带百叶时有效（arch 无百叶，则忽略） | S1 / S2 |
| (—) | constraint | — | — | inequality | 离地间隙：`ring_bottom_z = pivot_z·pivot_height_scale + SPIN_Z + RING_C − ring_R·hoop_radius_scale > 0.25`；违反则回缩 `pivot_height_scale` ↑ 或 `hoop_radius_scale` ↓ | 接口 / clearance |
| (—) | constraint | — | — | inequality | 顶部净空：`ring_top_z < FIN_Z0`（环顶不穿百叶 / 拱腹）；违反则回缩 hoop / 抬 pivot | 接口 / clearance |
| (—) | constraint | — | — | inequality | bridle 落点须落在环外缘 bore 上：N 个 `bridle_anchor` 角等分 2π，半径 = 环半径·hoop_radius_scale（圆管 hoop 或扁带 flat_band 外周） | 接口 / mating |

约束求解放在 `resolve_config`：先采 `frame_width_scale / pivot_height_scale / hoop_radius_scale` 三个 independent 主尺度，再按 `suspension_point_count` 解析 `suspension_style` 与 bridle 锚点，最后用两条 clearance 不等式投影/回缩。`seat_plank_count` / `fin_count` 的合法性是 conditional（依赖所选 ring_seat / frame module）。

## Multiplicity / Copy Logic

**轴 1（主多样性轴）：`suspension_point_count` N**

- `count_param`: `suspension_point_count`
- `N_range`: `[1, 4]`（本小类本轴产品域；样本覆盖 N∈{1,3,4}，N=2 由 bridle 构造外推）
- sampling domain（权重档）：N=1 高频（≈50%，single_chain baseline）、N=3/N=4 中频（各≈22%）、N=2 低频（≈6%）；尾部稀有但全程可达
- copied object: bridle 腿 `bridle_chain_i` + 环缘锚点 `bridle_anchor_i`（成对：每根腿一个环缘锚点）
- naming: `for i in range(suspension_point_count)` → `f"bridle_chain_{i}"`、`f"bridle_anchor_{i}"`（N=1 退化为 `single_chain` 命名，无 bridle 前缀）
- placement: N 条腿从 hub 中心发散到环缘 N 等角点（角 = `i·2π/N`，半径 = 环半径·hoop_radius_scale）；N=1 时为单中心吊链，环顶 eyelet 居中
- joint policy: **不论 N 多少，始终只有 2 个关节** — frame→suspension `canopy_swing` REVOLUTE (轴 (1,0,0), ±45°) + suspension→ring `ring_spin` CONTINUOUS (轴 Z)；N 条腿汇聚到单 swivel，**禁止闭环**、禁止 per-leg joint
- source/gating: N=1 ← S1；N=3 ← S6；N=4 ← S7；N=2 外推。`suspension_style` enum 由 N 派生（N=1→single_chain，N≥2→n_point_bridle），不独立采样

**轴 2（次级，sweep-only 装饰复制）：`seat_plank_count`**

- `count_param`: `seat_plank_count`，`N_range` `[16, 34]`，默认 bench 22 / cradle 32 / band 22；copied object = 木 `seat_plank_si` 沿环下内弧等角（bench/band θ 197°→343°，cradle θ 163°→377°）；joint policy = none（随 ring 整体旋转的 baked visual）；gating = 三种 ring_seat 均有效（弧角随 module 取值）；source S1/S4/S5。交采样器扫，不作主多样性轴。

**轴 3（次级，sweep-only 装饰复制）：`fin_count`**

- `count_param`: `fin_count`，`N_range` `[24, 40]`，默认 34；copied object = 百叶 `fin_i` 沿顶梁等距；joint policy = none（baked visual）；gating = 仅 frame ∈ {pergola, a_frame}（arch 无百叶）；source S1/S2。交采样器扫。

其它 module-local 固定复制（rivets、gusset、cross brace、anchor link `chain_link_i`）都是 baked visual，不暴露 template-level count 参数。`flat_band` 是单件 CadQuery annulus（非复制）；不存在任何填心的 disc rib / net spoke / concentric 复制（已随 disc/net 候选删除）。

## 拓扑多样性审计

总组合数：support_frame (3) × ring_seat (3) × suspension N 档 ({1,2,3,4} → 4 个有效拓扑) = 3 × 3 × 4 = **36** 个 distinct 拓扑骨架（未计 palette 与连续 scale 与次级 plank/fin count）。


seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 做 deterministic procedural sampling；`seed=0` 不特殊。先选 `support_frame`，再选 `ring_seat`，再对 `suspension_point_count` 做加权采样并派生 `suspension_style` 与 bridle 锚点，最后采三个 independent scale + 解析 conditional 的 `seat_plank_count`/`fin_count`，用两条 clearance 不等式回缩。

Procedural Sampling / Sweep Plan：sampler 按上述顺序选 slot/module/N；compatibility matrix 全兼容（无互斥对），唯一 gate 是 N→suspension_style 派生与 bridle 落点必须在环外缘 bore 上。无需 regression overrides（首版默认无；若 sweep 发现稳定失败组合再加少量显式 seed 并注明）。

Topology target：1000-seed slot choice tuple distinct 目标 ≥36（受 3×3×4 = 36 拓扑上限约束，类别本身组合空间小，低于 300 属正常；连续 scale + plank/fin count + palette 提供进一步外观多样性但不增拓扑 distinct）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版模板应含 `frame_width_scale [0.85,1.15]`、`pivot_height_scale [0.92,1.10]`、`hoop_radius_scale [0.88,1.12]` 三个 independent 主尺度（均在 `resolve_config` 内 clamp），外加 conditional 的 `seat_plank_count` / `fin_count`。所有 scale 通过两条 clearance 不等式（离地 / 顶部净空）+ bridle 落点 mating 约束求解，不破坏 `canopy_swing` / `ring_spin` 接口、不破坏 N 复制、不破坏 HALO（scale 只改环半径/座弧密度，绝不填心）。跨部件依赖（pivot_height ↔ chain 长度 ↔ 离地间隙；hoop_radius ↔ plank/bridle 落点）以 inequality 显式声明，禁止各抽各的。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 frame→ring_seat→N(加权)→scales；N 派生 suspension_style + bridle 锚点 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 全兼容，无互斥对；唯一 gate = N→style 派生 + bridle 落点在环外缘 bore 上 | 无 floating / collision / 闭环 / 穿百叶 / 离地不足 / **填心** |
| controlled local variation | 3 个 independent scale + 2 conditional count，全 clamp / 不等式投影 | 比例变化不破坏 2 关节接口、离地、顶部净空、bridle 收敛、HALO 开口 |
| regression overrides | none | 仅未来发现失败回归时添加 |
| random sweep | seeds 0-4 → 0-19 → 0-49 初轮，0-999 成熟度审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A support_frame | 3 | yes | yes | pergola / a-frame / arch |
| B ring_seat | 3 | yes | yes | bench / deep-cradle / flat-band（**全开口 halo**） |
| C suspension | 2 (×N 档) | yes | 拓扑分支 4 | single_chain + n_point_bridle，N∈{1,2,3,4} 驱动 4 个 distinct 骨架 |

## Palette / Colorway

`palette_style` enum（≥3，目标 4-6；仅改 material rgba，不改拓扑，来源于样本中实际出现的材质族）：

| palette_style | frame | hoops/band/hardware | seat | 来源 |
|---|---|---|---|---|
| `galvanized_warmwood` (默认) | galvanized_steel (0.58,0.60,0.62) + light_steel 顶梁 + fin_grey 百叶 | polished_chrome (0.84,0.86,0.89) | warm_wood (0.60,0.40,0.22) | S1 |
| `powdercoat_charcoal` | dark_steel 粉末涂层 (0.30,0.32,0.34) | polished_chrome | warm_wood / 深木 | S2 dark_steel / S3 dark_steel |
| `light_steel_chrome` | light_steel (0.76,0.78,0.80) 全亮钢 | polished_chrome | 浅枫木 (≈0.72,0.58,0.40) | S1 light_steel |
| `forest_green_oak` | forest green 粉末涂层 (≈0.18,0.34,0.22) | brushed steel (≈0.70,0.72,0.74) | oak (≈0.66,0.50,0.30) | 由 S1/S2 frame palette 外推（park-equipment 常见绿） |
| `bronze_oak` | bronze (≈0.50,0.38,0.22) | bronze hardware | oak / warm_wood (≈0.66,0.50,0.30) | 由 S1/S2 frame palette 外推（古铜园艺色） |

palette 仅替换 frame / hoop(或 band)/hardware / seat-wood 三组材质 rgba；三种 ring_seat 的环（双圆管 hoop 或扁带 flat_band）跟随 hardware 色，木板跟随 seat 色。**不再有 net 绳料材质**（net 候选已删除）。

## Validator

- `slot_choices_for_seed` 返回 implemented module 名（support_frame / ring_seat / suspension_style）
- `config_from_seed` 对普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊
- compatibility matrix / gating 阻止非法组合（N→style 派生、bridle 落点 mating）
- regression overrides 稀疏且有理由（首版 none）
- 最终模板不无限轮换小型 curated 表作为主 seed domain
- controlled local scale（frame_width / pivot_height / hoop_radius）全部 clamp，且通过 inequality 求解；不破坏接口 / clearance / joint origin / N 复制 / **HALO 开口**
- 跨部件 scale 依赖（pivot↔chain 长↔离地；hoop↔plank/bridle 落点）在 `resolve_config` 求解，不留到 builder 失败
- 关键 InterfaceSpec / MatingContract 存在：frame top_pivot、suspension swivel、ring 顶 eyelet/环缘 bridle 锚点
- 关键 joint：`canopy_swing` REVOLUTE 轴 (1,0,0) ±45°（z≈2.55）、`ring_spin` CONTINUOUS 轴 (0,0,1)；**恰 2 个关节，N 不变关节数**
- 复制对象命名稳定：`bridle_chain_i`/`bridle_anchor_i`（N 对），`seat_plank_si`、`fin_i` 装饰复制
- identity：存在静止上方 frame + **刚性开口圆环** ring_seat + 2 关节链（水平摆动 + 竖直自旋）
- **HALO 检查**：每个 seed 的 ring 内部必须敞开 —— 环心区域无大面积实心 visual（无 disc/platform/deck/net）；木座只占下内弧；ring 沿 +X/+Z 的 AABB 投影在中心有空腔（座弧不超过 ~220°）
- 离地：ring 底 z > 0.25；顶部：ring 顶 < FIN_Z0 / 拱腹
- spin 检查：quarter spin 后环平面绕竖直轴转（hoop/band AABB 的 Y 跨度 > X 跨度）

## Reject cases

- **环心被实心盘 / 平台 / 甲板 / 绳网填满（违反 HALO 不变量，人无法坐进环内、无腿部空间）—— 出类目，最高优先级 reject。**（这正是删除 var_disc/var_net 的原因。）
- 只有 frame 没有可坐圆环，或座具是线性平板/吊带（退化成普通秋千，丢失 ring 身份）。
- 缺 `ring_spin` CONTINUOUS（环不能自旋）或 `canopy_swing` REVOLUTE（不能 fore/aft 摆动）—— 任一缺失即丢失 2 关节身份。
- N 点 bridle 被实现成闭环（多 swivel / per-leg joint / 环缘互连成环），而非汇聚到单 swivel。
- bridle 腿落点漂浮在环外或未落到外环 / 扁带 bore。
- ring 自旋轴被建成水平或 ring 摆动轴被建成竖直（轴搞反，变成转盘 / 旋转展示件）。
- 离地间隙为负（环触地）或环顶穿过百叶 / 拱腹（净空不等式未求解）。
- 把 frame 做成地面转盘基座（merry-go-round），或环座固定不悬挂。
- 形态只靠颜色 / palette 变化，frame / ring_seat / suspension 拓扑无区别。

## 与相邻类别的边界

- 不该混入 `playground_swing`（普通秋千）：普通秋千座具是平板 / 吊带 / 桶座 / 轮胎，沿水平轴单关节摆动；本类别核心是 **刚性开口圆环座 + 第二个 CONTINUOUS 自旋关节**，缺一即退化为普通秋千。
- 不该混入 tire swing：轮胎秋千是软体轮胎载具、通常三点吊但无刚性圆环 + 木座圈、且无自旋身份；本类别是 chrome 圆环（或扁钢带环）+ 下弧木座且强调绕竖直链轴自旋。
- 不该混入 merry-go-round（旋转木马 / 转盘）：转盘是 **地面安装** 的竖直轴转盘，没有上方悬挂 frame、没有 fore/aft 摆动；本类别必须悬挂在静止上方支架下并保留 **hang + spin 双关节**。
- 不该混入 hanging chair / hammock / saucer-nest swing：那些是单点吊休闲座或 **填心** 的网碟/碗座，无固定园艺支架语义、或填满了坐面；本类别是开口环 + fore/aft 摆动 + 自旋的双关节运动链。

## 模板实现备注（可选）

- frame / suspension / ring_seat 三组各自抽 build helper；frame helper 统一对外 emit `top_pivot (0,0,pivot_z)` 与 REVOLUTE 轴，让 suspension 与 ring 复用同一坐标系，换 frame 只改 pivot_z 与 part tree。
- `canopy_swing` anchor stem socket 进 frame 顶梁 / crown bracket 是 intentional embed，需 element-scoped `allow_overlap(frame, suspension, "top_rail"/"ridge_beam"/"crown_bracket", "anchor_stem")`（见 S1 L279-L285）。
- hook ↔ ring_eyelet 的捕获 embed（single_chain）需 element-scoped `allow_overlap(suspension, ring, "hook", "ring_eyelet")`（S1 L286-L292）。
- ring_seat 三 module 共享同一 eyelet/clevis + hoop/band 基座 helper；差异仅在 (a) 环截面：bench/cradle 用 `TorusGeometry(HOOP_R, HOOP_TUBE)` 双环，band 用 `mesh_from_cadquery` 的单 annulus（`cq.Workplane.circle(outer).circle(inner).extrude(width, both=True)` 再 `rotateAboutCenter((1,0,0),90)`，见 S5 L223-L238）；(b) seat plank 弧角：bench/band θ197°→343°，cradle θ163°→377°。**三者都只沿下内弧铺 plank，环心一律不填。**
- bridle 实现注意：S6 把 bridle 链放在 hub/suspension 一侧，S7 的 `bridle_chain_i` 随 ring 旋转、环缘 `bridle_anchor_i` 在 ring 上。**实现时统一选一种归属**：建议 bridle 腿归 suspension part（与 single_chain 的 hook 一致），环缘 anchor 归 ring part，每根腿 + 对应 anchor 成对声明 captured-pin allow_overlap。
- bridle 腿可能擦过相邻 seat plank，需对落点附近 plank 声明 allow_overlap。
- arch 的拱梁用 `tube_from_spline_points`；band 的 annulus 用 CadQuery；注意 segments / 布尔不要过密以控编译成本。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved (user-directed) |
| reviewer notes | 用户报告原 Slot B 的 solid_disc / net_saucer 违反「圆环须为开口 halo、人坐进环内留空间」的类别身份，要求删除全部 variant 并按 variants→spec→template 重做且不中途停。已删 var_disc/var_net，新增 deep_cradle_ring(var_cradle)/flat_band_ring(var_band) 两个开口环候选并贯穿 HALO 不变量。用户明确指示不在 gate 处停顿，故 spec 直接进入模板实现阶段。 |
