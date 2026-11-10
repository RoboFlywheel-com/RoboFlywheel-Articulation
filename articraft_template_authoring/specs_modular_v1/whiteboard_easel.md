# Whiteboard Easel — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `whiteboard_easel` |
| template path | `agent/templates/whiteboard_easel.py` |
| test path (optional) | `tests/agent/test_whiteboard_easel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear stand→board chain + multiplicity legs + parallel caster/clamp children) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 origins + 6 verified forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

A free-standing **floor whiteboard easel**: a tall planar dry-erase writing panel framed by a
perimeter rail, carried on its own portable leg/base stand that raises the board to writing height,
with a marker tray/ledge at the lower board edge and at least one real non-fixed joint (caster spin,
leg telescope/fold, board revolve/tilt/slide, or a locking clamp knob). The board body is intrinsically
a planar rectangle — honest structural diversity lives in the **support skeleton** (how it stands) and
the **board articulation** (how the panel connects/moves). Must NOT drift into: wall-mounted whiteboard
(no floor stand), tabletop flip easel (no floor legs), artist canvas painting easel (no dry-erase board),
freestanding sign/menu holder (display frame, not a writing board), or a drafting desk (horizontal desk
surface with drawers).

## 槽位 + 候选模块表

### Slot A：support_base （① skeleton / topology — 主结构轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rolling_post_base` | forked_anchor | rec_...__001 + var_board_revolve/var_board_slide | 001 L152-L173, L233-L331; revolve L99-L199 | eligible if compatible | Two rigid vertical posts (x=±0.46) on H-runner feet, tied by low crossbar; 4 continuous casters. Full-height posts → mounting masts for any board motion. |
| `folding_tripod_base` | forked_anchor | rec_...__002 + var_n4_legs | 002 L256-L393; n4 L256-L407 | eligible if compatible (static only) | N∈{3,4} splayed legs hinged under a mount hub; each leg = REVOLUTE fold + PRISMATIC telescope + rubber foot. Multiplicity axis. |
| `t_column_base` | forked_anchor | var_base_tbase | tbase L148-L320 | eligible if compatible (static only) | Single central mast column behind board + 4-arm star hub base + 4 continuous casters. Board on a rear bracket. |
| `four_post_frame_base` | forked_anchor | var_base_fourpost | fourpost L91-L180 | eligible if compatible | Four rigid tubular posts (2 front x=±0.46 y=0, 2 rear y=+0.40) in a closed ladder frame with crossbars + floor glides. Front posts = mounting masts. |

### Slot B：board_motion （② joint / mechanism — 主结构轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `static_framed` | forked_anchor | rec_...__001 / __002 | 001 L87-L148; 002 L172-L254 | eligible (all bases) | Board FIXED to the stand mount; only the clamp knobs + base legs/casters move. |
| `revolve_trunnion` | forked_anchor | var_board_revolve | revolve L349-L449 | eligible (two-mast bases) | Double-sided board on a horizontal-X REVOLUTE trunnion (±π) between the two posts; trunnion stubs captured in post bushings. |
| `tilt_carriage` | forked_anchor | var_board_tilt | tilt L126-L350 | eligible (two-mast bases) | A distinct `tilt_carriage` part FIXED across the post tops carries a pivot rod; board REVOLUTE on it (0..~1.1 rad) from upright toward drafting angle. |
| `slide_carriage` | forked_anchor | var_board_slide | slide L100-L249 | eligible (two-mast bases) | Board frame carries square carriage sleeves wrapping the posts; PRISMATIC vertical height slide (0..0.35). |

### Companion features (not standalone slots)
- `flip_chart_top` ∈ {none, top_clamp_bar}: ④ decoration — a top flip-chart clamp bar + brackets fused as
  `board.visual(...)` (from 002 L239-L254). Non-articulating → never a FIXED part.
- `clamp_knobs`: two REVOLUTE thumb-wheel lock knobs on the board sides (all sources) — always present, a
  stable ② feature that guarantees ≥1 non-fixed joint even for static/rigid bases.

硬约束满足：support_base 4 candidates（全部 forked_anchor，源码可回溯）；board_motion 4 candidates（全部
forked_anchor）；每个 candidate 结构不同（part tree / joint 拓扑不同），非只换尺寸/涂装。板体 ③ 为单一平面
矩形族（见 §8.5 ③ underfilled_reason），不登记独立 ③ slot。

## 槽位图（slot graph）

pattern: mixed

```
support_base (root, grounded "stand")
    --[board_motion joint: FIXED | REVOLUTE(x,±π) | REVOLUTE(x,0..1.1) via tilt_carriage | PRISMATIC(z,0..0.35)]-->
        board_frame (shared planar panel + marker tray + mount plate)
            --[REVOLUTE(x,±π) ×2]--> clamp_knob_{0,1}  (parallel children)
support_base --[CONTINUOUS caster ×4]--> caster_{i}_{j}      (rolling_post / t_column only, parallel children)
support_base --[REVOLUTE fold ×N + PRISMATIC telescope ×N]--> leg_{i} / leg_{i}_lower  (folding_tripod only)
tilt_carriage (intermediate part) --[FIXED]--> support_base ; board --[REVOLUTE]--> tilt_carriage
```

- 跨 slot 连接点：stand 顶部两根 masts（rolling_post 的两柱 / four_post 的两前柱）在 board 中心高度
  Z_CENTER=1.355 提供 mounting 面；hub/column bases 在 board 背中心提供 mount plate。
- 跨 slot joint type/axis/range 由 board_motion 决定（见 §8.5 ⑤）。
- 互斥/gating：revolve/tilt/slide 只与两-mast bases（rolling_post、four_post）兼容；folding_tripod、
  t_column 仅与 static_framed 兼容（见 §9 compatibility matrix）。

## 每槽位 Module Emits / Interfaces

### Slot A / rolling_post_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand`（2 posts, 2 H-runner feet visuals, low crossbar, 2 yoke/mount bosses）+ `caster_{0..1}_{0..1}` | 001 L152-L331 |
| internal joints | `stand_to_caster_{i}_{j}` CONTINUOUS axis x ×4 | 001 L323-L331 |
| downstream interface | two-mast mount: post_x=(±0.46), post_top_z≈1.96, mount at (0,0,Z_CENTER) | 001 L152-L173 |

### Slot A / folding_tripod_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand`（mount hub + N hinge blocks）+ `leg_{i}` (outer) + `leg_{i}_lower` ×N | 002 L256-L393 |
| internal joints | `stand_to_leg_{i}` REVOLUTE fold + `leg_{i}_slide` PRISMATIC ×N | 002 L354-L393 |
| downstream interface | hub mount plate at board bottom-center (0,0,Z_CENTER-0.565) | 002 L256-L276 |

### Slot A / t_column_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand`（mast column + star hub + 4 arms + mount bracket）+ `caster_{0..3}_0` | tbase L148-L311 |
| internal joints | `stand_to_caster_{i}_0` CONTINUOUS axis x ×4 | tbase L300-L311 |
| downstream interface | rear bracket mount at (0,+y,Z_CENTER) | tbase L163-L172 |

### Slot A / four_post_frame_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand`（4 posts + crossbars + gussets + glides） | fourpost L91-L180 |
| internal joints | none (rigid); floor glides are visuals | fourpost L102-L115 |
| downstream interface | two front-mast mount: post_x=(±0.46), mount at (0,0,Z_CENTER) | fourpost L96-L108 |

### Slot B / static_framed
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board_frame`（panel/rails/tray/mount_plate）+ `clamp_{0,1}` | 001 L87-L229 |
| internal joints | `board_to_clamp_{i}` REVOLUTE axis x ±π ×2 | 001 L207-L229 |
| upstream interface | FIXED board→stand at base mount anchor | 001 L87-L148 |

### Slot B / revolve_trunnion
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board_frame`（+ back writing surface + 2 trunnion stubs）+ `clamp_{0,1}` | revolve L355-L434 |
| internal joints | `board_to_clamp_{i}` REVOLUTE ×2 | revolve L314-L347 |
| upstream interface | REVOLUTE board→stand axis (1,0,0) ±π at (0,0,Z_CENTER); stubs in post bushings | revolve L441-L449 |

### Slot B / tilt_carriage
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tilt_carriage` (bracket + pivot rod) + `board_frame`(+ hinge lugs) + `clamp_{0,1}` | tilt L126-L239 |
| internal joints | `stand_to_carriage` FIXED; `board_to_carriage` REVOLUTE axis x 0..1.1; `board_to_clamp_{i}` ×2 | tilt L174-L377 |
| upstream interface | carriage FIXED to post tops; board REVOLUTE to carriage at (0,0,Z_CENTER) | tilt L126-L181 |

### Slot B / slide_carriage
| emits | 描述 | 来源 |
|---|---|---|
| parts | `board_frame`(+ carriage sleeves) + `clamp_{0,1}` | slide L155-L290 |
| internal joints | `stand_to_board` PRISMATIC axis z 0..0.35; `board_to_clamp_{i}` ×2 | slide L238-L290 |
| upstream interface | PRISMATIC board→stand axis (0,0,1); sleeves wrap posts | slide L209-L249 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| support_base | enum | rolling_post_base / folding_tripod_base / t_column_base / four_post_frame_base | — | choice | deterministic procedural sampler (weighted legal combos) | Slot A |
| board_motion | enum | static_framed / revolve_trunnion / tilt_carriage / slide_carriage | — | choice | gated by base (compatibility matrix §9) | Slot B |
| leg_count | int | {3,4} (folding_tripod only) | 3 | conditional | active only when base=folding_tripod; else N/A | 002 / n4 |
| flip_chart_top | enum | none / top_clamp_bar | none | choice | board.visual decoration only | 002 L239-L254 |
| material_style | enum | powder_blue / satin_aluminum / white_coat / dark_metal / classroom_green | powder_blue | choice | palette only | ⑥ evidence |
| board_width_scale | float | [0.92, 1.10] | 1.0 | independent | uniform sample then clamp; keeps H/W>1.4 portrait | ⑤ 001/002 |
| board_height_scale | float | [0.96, 1.08] | 1.0 | independent | uniform sample then clamp | ⑤ 001/002 |
| stand_spread_scale | float | [0.90, 1.12] | 1.0 | independent | caster/leg/post lateral spread | ⑤ 001/002 |
| (—) | constraint | — | — | inequality | post_x ≥ board_half_width + 0.05 so posts clear the board frame; if violated, widen post_x | interface/clearance |
| (—) | constraint | — | — | inequality | slide travel ≤ post_top_z − board_top_world at rest so the board stays captured on masts | slide L246 |

连续尺寸采样契约：先采 3 个 independent scales（board_width/height/stand_spread），无 equation 派生；用两条
inequality 在 `resolve_config` 内把 post_x / slide travel 投影到可行域；leg_count 为 conditional（仅 tripod）。

## 7.5 编译预算 / compile budget
自报预算：**≤15s/seed**（全部 Box/Cylinder 图元，无布尔/放样/mesh；最大件数 tripod N=4 约 12 parts /
~14 joints）。圆柱分段用 SDK 默认（casters/knobs 小半径特征）。超预算先降 caster/knob 段数再迭代。
sweep `--compile-timeout` 设 60（≈4×预算，看门狗）。

## 8. Multiplicity / Copy Logic

**轴 1：leg_count（folding_tripod_base 专属）**
- count_param `leg_count`；N_range 本小类本轴 = `[3,4]`（便携折叠易架物理上是三脚或四脚，更高不真实）。
  sampling domain：N=3 与 N=4 近似等权（各约 50%）；测试与产品域相同（窄域）。
- copied object：折叠腿子装配 = outer `leg_{i}`(`_build_outer_leg`) + `stand_to_leg_{i}` REVOLUTE fold +
  child `leg_{i}_lower`(`_build_inner_leg`) + `leg_{i}_slide` PRISMATIC。
- naming：`leg_{i}` / `leg_{i}_lower`，joints `stand_to_leg_{i}` / `leg_{i}_slide`。
- placement：从 hub 以规则环/矩形 splay（N=3：2 前 1 后；N=4：2 前 2 后）。
- joint policy：每条腿各自 revolute fold + prismatic telescope，无共享 joint（loop-emitted）。
- source/gating：仅 folding_tripod_base；其它 base 不暴露 `leg_count`。

**轴 2：casters** — rolling_post=4、t_column=4，固定于 base，不作为可采样 multiplicity（数量由 base 决定，
不暴露 `*_count`，非独立轴）。four_post 用 glides、tripod 用 rubber feet（无 caster）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 4 个 base skeleton：rolling_post（2柱+casters）/ folding_tripod（N折叠伸缩腿）/ t_column（中柱+星座+casters）/ four_post（4刚性柱框）。全部 forked_anchor（见 Slot A）。 |
| └ multiplicity | 同构件 ×N | 有 | leg_count∈{3,4}（tripod）；见 §8。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | board_motion：FIXED(static) / REVOLUTE x ±π(revolve) / REVOLUTE x 0..1.1(tilt) / PRISMATIC z(slide)；leg fold REVOLUTE + telescope PRISMATIC；caster CONTINUOUS x；clamp REVOLUTE x。每种类型都在 sweep 出现（全部 forked_anchor，见 Slot B）。 |
| ③ 主体形态家族 | 换核心 part 的可识别几何形态原型 | 无（underfilled） | underfilled_reason：书写板体本质是**单一平面矩形边界**（Planar Boundary Form），无诚实第二形态族——曲面/圆形板会漂向 sign/decor。故不登记独立 ③ slot；主多样性由 ①②承载（category-relative 合法：形态主导落在 support skeleton）。 |
| ④ 表面装饰 | 叠加表面细节/改装饰数 | 有 | flip_chart_top∈{none,top_clamp_bar}（record_only，002 顶夹条）+ marker tray/eraser rest/red magnet caps + clamp thumb wheels。均写成宿主 board.visual，随 ⑤ 尺寸共形（tray/夹条宽度按 board_width 派生）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | board_width_scale[0.92,1.10]、board_height_scale[0.96,1.08]、stand_spread_scale[0.90,1.12]（见 §7，H/W>1.4 保持）。关节运动包络：revolve REVOLUTE x [−π,π]（整程翻转，double-sided）；tilt REVOLUTE x [0,1.1]（upright→drafting，正向 −Y 倾）；slide PRISMATIC z [0,0.35]（上滑，全程 sleeve 抱柱）；leg fold REVOLUTE [0,0.9]；leg telescope PRISMATIC [0,0.15]；caster CONTINUOUS 整圈；clamp REVOLUTE [−π,π]。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses`（多关节 cap=32）+ 每机构一条 targeted `ctx.pose(...)`（revolve 翻转 top_rail 落到 pivot 下方；tilt 板前倾 −Y；slide 板上移 z；leg telescope 下伸；leg fold 摆动；caster 旋转）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 material_style：powder_blue / satin_aluminum / white_coat / dark_metal / classroom_green（powder-coated / aluminium / painted 三大类覆盖 ≥ceil(0.5×5)=3）。source：001 蓝、002 铝灰、tube 白、+world 扩展黑/绿。 |

## 采样与覆盖审计

总组合数（离散）：support_base(4) × board_motion(gated) × leg_count(2 for tripod) × flip_chart_top(2) ×
material(5) 。合法 (base,motion) 对 = rolling_post{4} + four_post{4} + tripod{1} + t_column{1} = **10 对**；
乘 flip_chart_top(2) × material(5) × leg_count(tripod 额外 ×2) ≈ 10×2×5 + tripod 分支 ×2 ≈ **110+ 离散组合**
（连续 scale 另计）。理由：coverage-first，形态主导类主多样性来自离散 ①②，连续 scale 只做局部微调。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 用 `random.Random(seed)` 加权采合法 (base,motion)
对，再采 leg_count/flip_chart_top/material/scales；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：加权 legal-combo 列表（canonical rolling_post+static、rolling_post+revolve、
tripod+static 等权重更高）；compatibility gating 在 `resolve_config` 内 `_downgrade_combo` 把非法 (base,motion)
对回退到该 base 的合法 motion（默认 static）。少量无 regression overrides。random sweep 0-35 初判，viewer 目检 0-2。
Topology target：report-only；本类真实离散组合 ~110，兼容约束限制在 10 个 (base,motion) 对 —— 低于 300 的原因是
板体 ③ 单一 + motion 受 base 结构约束，非上游锚点不足。

Controlled local parameterization：board_width_scale / board_height_scale / stand_spread_scale。范围见 §7；
在 `resolve_config` 内 clamp + 两条 inequality 投影（post_x ≥ half_width+0.05；slide travel ≤ 上界）；不破坏 mount
接口 / clearance / joint origin / 类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted legal (base,motion) combos → leg_count/top/material/scales；seed 0 不特殊 | slot_choices_for_seed matches build choices |
| compatibility matrix | tripod/t_column → static only；rolling_post/four_post → all 4 motions；非法对 downgrade→static | no floating/collision/axis/max-mult/bulky/optional-child failures |
| controlled local variation | 3 continuous scales clamped + 2 inequalities | proportions vary without breaking interfaces/clearance/support/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass；0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 4 | yes | yes | |
| board_motion | 4 | yes | yes | 3/4 gated to two-mast bases |
| leg_count (mult) | 2 | yes | no | {3,4} physical bound |

## Validator
- slot_choices_for_seed returns implemented module names (support_base, board_motion, leg_multiplicity, flip_chart_top, material_style)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix / gating prevents illegal (base,motion) pairs (downgrade to static)
- no regression overrides needed
- controlled local scales clamped; cannot break mount interface / caster axis / clamp / motion origin
- inequalities (post_x, slide travel) resolved in `resolve_config`
- critical mount contacts exist (board↔stand at anchor; trunnion↔bushing; carriage↔posts; sleeves↔posts)
- key joints have expected type/axis/range (see §8.5 ⑤)
- copied leg objects follow naming/placement policy

## Reject cases
- Board panel not a tall portrait rectangle (H/W ≤ 1.4) → identity fail.
- Any board_motion realized as a floating/isolated part with no mount contact to the stand.
- revolve/tilt/slide realized on a non-two-mast base (illegal pair not downgraded).
- Marker tray missing or detached from the lower board edge.
- Board or legs penetrate the stand through the full motion range (穿模 in sampled poses).
- Non-articulating flip-chart bar / tray emitted as a separate FIXED part instead of a board visual.
- Casters/legs float above floor at rest, or slide carriage escapes the masts at full travel.

## 与相邻类别的边界
- 不该混入：wall-mounted whiteboard（无 floor stand；本类必须自立落地）。
- 不该混入：tabletop flip easel / drafting desk（无落地腿 / 有水平桌面抽屉）。
- 不该混入：sign / menu / poster holder（展示框，非可书写 dry-erase 板）。
- 不该混入：artist canvas painting easel（无 dry-erase 板 + marker tray）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Board ③ intrinsically single planar-rectangle family (underfilled, documented); 主多样性由 ① support_base + ② board_motion 承载，均 source-backed。 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | rolling_post_base | rec_...__001 | L152-L331 | posts + H-runner feet + casters + mount |
| S2 | A | folding_tripod_base | rec_...__002 / var_n4_legs | 002 L256-L393 / n4 L256-L407 | N folding+telescoping legs + hub |
| S3 | A | t_column_base | var_base_tbase | L148-L320 | mast column + star hub + casters |
| S4 | A | four_post_frame_base | var_base_fourpost | L91-L180 | 4 rigid posts + crossbars + glides |
| S5 | B | static_framed | rec_...__001/__002 | 001 L87-L229 | framed board + tray + clamp knobs |
| S6 | B | revolve_trunnion | var_board_revolve | L349-L449 | double-sided board + trunnion pivot |
| S7 | B | tilt_carriage | var_board_tilt | L126-L350 | tilt_carriage part + board hinge |
| S8 | B | slide_carriage | var_board_slide | L100-L249 | carriage sleeves + vertical prismatic |

## 模板实现备注（可选）
- 共享 helper：`_emit_board_frame`（所有 board_motion 复用）、`_emit_clamp_knobs`、`_rod_between`、
  `_add_square_sleeve`（slide/tripod sleeve）。
- Captured-pin element-scoped allow_overlap：caster axle↔fork、trunnion stub↔post bushing、leg inner↔outer
  sleeve、carriage pivot rod↔board hinge lug、slide sleeve↔post。
- Mount anchor 由 base 提供（`StandMount` dataclass）：two-mast bases → (0,0,Z_CENTER) + post_x；
  hub/column bases → board back/bottom center。static FIXED origin 落在 stand mount geometry + board mount_plate。
- 暂不进入 seed domain 的组合：tripod/t_column × {revolve,tilt,slide}（结构不支持，downgrade→static）。
</content>
</invoke>
