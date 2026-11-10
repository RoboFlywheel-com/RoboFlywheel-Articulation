# speed_gate modular spec

## 元信息

| 项 | 值 |
|---|---|
| slug | `speed_gate` |
| template path | `agent/templates/speed_gate.py` |
| test path (optional) | template-local `run_speed_gate_tests` |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed`（parallel children + bounded multiplicity） |

## Category Binding

`category_slug=speed_gate` · `template_slug=speed_gate` ·
`mechanism_profile=swing_revolute` · `export_namespace=speed_gate`。机器真值见
`articraft_template_authoring/category_template_registry.json`；固定 swing 机构不是伪装成
单候选的可变 slot。`diversity_profile=constrained`：本类只有一个诚实主运动 spine，核心
词汇来自 3 种柜体、4 种门翼和 2 种 reader；高风险由 `Visual Risk` 独立表达。

## 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all category_slug=`speed_gate`, rating=5 records；逐个读取 `record.json`、`revision.json`、`prompt.txt`、`model.py` |
| source_index_policy | only the nine adopted records in the reviewed source map are indexed below |

## 核心身份

`speed_gate` 是带 `N` 条行人通道的落地式门禁：`N+1` 个纵长柜体沿 X 方向形成通道链，每条通道有两片从相邻柜体侧面伸出的透明对开门翼；每片门翼绕真实竖直主轴独立摆动。柜体承载 reader、主轴轴承和侧面支撑。生产模板只实现已验收的 vertical-axis swing，绝不混入 vertical retract、telescopic retract、三辊闸、普通围栏或 solid-wall turnstile。

## 槽位 + 候选模块表

### Slot A：pedestal_form（③ Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tapered_hex` | origin_anchor | `rec_picturex_0611__speed_gate__001__png_54981d2cd9e84316b2a4769f9ba6a943/rev_000001` | `L28-L59`, `L184-L270` | eligible under swing interface | CadQuery hex outline + top/bottom loft；side socket attached to tapered host |
| `drafted_rounded` | origin_anchor | `rec_picturex_0611__speed_gate__002__png_0a454d17b7944c38a11fa734e37dfd49/rev_000001` | `L34-L91`, `L259-L361` | eligible under swing interface | true filleted rectangular solid with cut draft wedges；rounded cap |
| `slim_rounded` | forked_anchor | `rec_0611_speed_gate_var_pedestal_form_slim_rounded/rev_000001` | `L44-L88`, `L231-L421` | eligible under swing interface | CadQuery stadium/slot profile extrusion；slimmer cabinet envelope |

### Slot B：barrier_form（③ Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_mid` | origin_anchor | `rec_picturex_0611__speed_gate__001__png_54981d2cd9e84316b2a4769f9ba6a943/rev_000001` | `L279-L329` | eligible | flat transparent mid-height leaf + pivot spindle + clamp + upper/lower brackets |
| `curved_glass` | forked_anchor | `rec_0611_speed_gate_var_wing_form_curved_glass/rev_000001` | `L61-L103`, `L315-L410` | eligible only through recomputed curved profile | cylindrical shell leaf；panel and hinge-side clamp share the same curvature datum |
| `full_height` | forked_anchor | `rec_0611_speed_gate_var_wing_form_full_height/rev_000001` | `L271-L356`, `L458-L472` | eligible under height/sweep bound | tall flat transparent panel with the same captured spindle interface |
| `waist_high` | forked_anchor | `rec_0611_speed_gate_var_wing_form_waist_high/rev_000001` | `L113-L127`, `L365-L422` | eligible | rounded-edge acrylic waist-height panel + spindle/clamp assembly |

### Slot C：reader_terminal（① source-backed fixed functional layer）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flush_pad` | origin_anchor | `rec_picturex_0611__speed_gate__001__png_54981d2cd9e84316b2a4769f9ba6a943/rev_000001` | `L229-L270` | eligible | low top reader/control pad with status edge |
| `raised_terminal` | origin_anchor | `rec_picturex_0611__speed_gate__002__png_0a454d17b7944c38a11fa734e37dfd49/rev_000001` | `L313-L361` | eligible | rear-supported upright housing + visible terminal screen，located outside +Y swing arc |

### 固定 mechanism module（②）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `swing_revolute` | origin_anchor | origin 001 and origin 002 | origin 001 `L271-L356`; origin 002 `L362-L419` | always selected | complete leaf, captured vertical spindle, one independent REVOLUTE per leaf, closed→+Y open |

`swing_revolute` 只有一个生产候选，因此不是可替换 slot，而是每个 barrier module 的 module-local fixed mechanism。被拒绝的 retract records 不进入 enum，也不以单候选 slot 伪装多样性。

## Form Dependency Contracts

所有③均有直接 accepted anchor，本版没有无来源③外推。仍以以下 master descriptor 防止消费者错配：

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| pedestal family | Slot A three anchors above | `{outline,width,depth,height,top_profile}` | body mesh, top cap, side inset, reader footprint, socket origin, floor footprint | cap/reader/socket positions derive from realized width/depth/height；socket axis=`half_width+pivot_offset` | cap contact, reader support, socket/mating gap, floor containment, all-pose clearance | eligible |
| curved barrier | curved source `L61-L103`, `L315-L410` | one cylindrical shell `(chord,radius,thickness,height)` | glass shell, hinge-edge placement, clamp reach, swept proxy | all use same local hinge origin/chord；no old rectangular opening/frame retained | shell begins at declared clamp offset；closed seam and closed/mid/max sampled collision | eligible |
| planar barrier family | flat/full/waist anchors above | `{reach,height,thickness,edge treatment}` | panel solid, clamp height, spindle height, upper/lower bracket positions, swept proxy | all Z consumers derive from one leaf height；lane pitch derives from reach | support connectivity, anti-pinch seam and full-swing clearance | eligible |

## Compatibility Gates

三个 pedestal 与四个 barrier 共用 captured vertical spindle interface，因此没有额外 deny
row。reader 必须位于负 Y/top 安全区并避开正 Y swing envelope，由模板测试和 sampled
collision 共同验证。

## Combination Domain

- diversity profile：`constrained`，硬下限 16。
- core domain：`pedestal_form(3) × barrier_form(4) × reader_terminal(2) = 24`，无 deny gate，合法 **24**，通过 profile。
- multiplicity coverage：`lane_count={1,2,3,4,5}` 全部可达；边界覆盖 `1/3/5`。
- raw domain：`24 × lane_count(5) = 120`，合法 **120**。
- palette、连续 scale 和 N 不计入 core。旧的 120-vs-200 人工例外已由 schema-v2 profile
  契约取代；后续仍只能补真实耦合的主体、门翼和功能模块，不能用颜色或放宽 N 凑核心数。

## Visual Risk

`curved_fit`、`multi_joint`。视觉审核必须核对 curved glass 与 clamp/spindle 共形，以及
closed/mid/max 中门翼、reader 和相邻 pedestal 的净空。

## 槽位图（slot graph）

pattern: `mixed`

```text
mounting_frame.floor_plate
  ├─ FIXED floor contact ─▶ pedestal_i[pedestal_form + reader_terminal], i=0..N
  │                           ├─ right socket ─ REVOLUTE +Z ─▶ lane_i_left_leaf
  │                           └─ left socket  ─ REVOLUTE -Z ─▶ lane_{i-1}_right_leaf
  └─ local cell i = pedestal_i + opposed leaves + pedestal_{i+1}
```

- Pedestal FIXED origin lies on floor-plate positive-Z / body negative-Z contact plane.
- Leaf joint origin is the named side spindle bearing center; axis is vertical；range `[0,swing_angle]`.
- Every lane always has two leaves；`wings_per_lane` is not an axis.
- Cross-source composition is legal only because all three hosts expose the same socket key and all four leaves expose the same spindle/root envelope；reader stays on the negative-Y/top region while leaves sweep into +Y.

## 每槽位 Module Emits / Interfaces

### Slot A / pedestal modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedestal_i` with source-primitive body, cap, side inset, reader and bilateral socket/bearing visuals | Slot A anchors |
| internal joints | none；stationary details are host visuals | source records |
| upstream interface | `pedestal_body.negative_z` to `floor_plate.positive_z` | origins `L259-L361` / `L184-L270` |
| downstream interface | named `hinge_socket_left/right` and `spindle_bearing_left/right`; common vertical axis | swing anchors |

### Slot B / barrier modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | one complete leaf per invocation: panel + full-height spindle + clamp + two hinge brackets | barrier anchors |
| internal joints | one REVOLUTE emitted by assembler per leaf；vertical ±Z；`[0,1.25..1.48]` | origins 001/002 |
| upstream interface | `pivot_spindle` captured by named host bearing/socket | swing anchors |
| downstream interface | none | — |

### Slot C / reader modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | no separate part；reader visuals fuse to `pedestal_i` | origins 001/002 |
| internal joints | none | source |
| upstream interface | top/rear cabinet support surface | source |
| downstream interface | none | — |

## 活动机构与运动净空契约

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| every `lane_i_{left,right}_leaf` | transparent panel + vertical pivot spindle + matching clamp + upper/lower hinge brackets | real cabinet side shroud, lower thrust pad and coaxial annular upper spindle bearing | `spindle_thrust_{side}.positive_z` ↔ `pivot_spindle.negative_z`; upper bearing captures spindle with 1 mm radial running clearance | cabinet-local `x=±(half_width+pivot_offset), y=0, z=hinge_z`; axis ±Z; `[0,swing_angle]` | closed leaves retain 14–22 mm anti-pinch gap；mid/max rotate toward +Y and clear cabinet, negative-Y reader, sibling and adjacent lanes；minimum undeclared collision clearance >5 mm | none；thrust faces touch, annular bearing has positive radial clearance | current-pose overlap, sampled poses for all joints, targeted closed/mid/max for every leaf；N=1 and N=5 boundary |

## Element Allowance Audit

- Production scope contains zero overlap allowances. `pivot_spindle` rests on a real named thrust face and runs inside a true annular `spindle_bearing_left/right` with positive radial clearance.
- No `leaf↔pedestal`, sibling-leaf, moving↔frame or static whole-part allowance.
- Any allowance, especially glass/panel/clamp/host-body scope, is blocking until spec/source-map review.

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `pedestal_form` | enum | 3 Slot A values | `tapered_hex` | choice | deterministic procedural sampler | Slot A |
| `barrier_form` | enum | 4 Slot B values | `flat_mid` | choice | deterministic procedural sampler；all share swing root | Slot B |
| `reader_terminal` | enum | `flush_pad`,`raised_terminal` | `flush_pad` | choice | mounted outside +Y swing envelope | Slot C |
| `palette_style` | enum | 5 realistic metal/glass palettes | `stainless_green` | choice | drives every visual material | source palettes |
| `lane_count` | int | `[1,5]` | 2 | conditional | observed 1–3；bounded extrapolation 4–5 | N anchors |
| `pedestal_height` | float | `[0.90,1.02]` m | 0.94 | independent | uniform then clamp | origins |
| `pedestal_depth_scale` | float | `[0.93,1.07]` | 1.0 | independent | scales source-specific depth only | host anchors |
| `leaf_reach` | float | `[0.27,0.34]` m | 0.30 | independent | uniform then clamp | barrier anchors |
| `leaf_height` | float | derived | form nominal | equation | `min(host_height-0.10, form_height*scale)` | form contract |
| `lane_pitch` | float | derived | derived | equation | `2*(half_host_width+pivot_offset+leaf_reach)+anti_pinch_gap` | copy/spacing contract |
| `plate_width` | float | derived | derived | equation | `N*lane_pitch + host_width + end_margins` | host-growth contract |
| `swing_angle` | float | `[1.25,1.48]` rad | 1.40 | conditional | full-height/raised-reader combinations still pass sampled clearance | swing sources |
| — | constraint | — | — | inequality | exact counts: pedestals=`N+1`, active joints=`2N`; reader Y < 0, leaf opens +Y | interface/identity |

采样顺序：离散 choices/N → independent scales → leaf/pitch/plate equations → boundary assertions；不可行显式 config 拒绝，不静默降级 candidate。

## 7.5 编译预算 / compile budget

- self-declared budget: `≤20 s/seed`，包括 N=5。
- implementation target: shared CadQuery meshes per seed（同形 pedestals/leaves复用），hero surfaces tolerance 2.5–3 mm；smoke 实测约 3–5 s/seed。

## Multiplicity / Copy Logic

- `count_param`: `lane_count`.
- `observed_N`: `{1,2,3}`；`derived_N_range`: every integer `[1,5]`.
- accepted source evidence:
  - N=1: `rec_0611_speed_gate_var_lane_count_1/rev_000001`, repeated unit/copy loop `model.py:L245-L445`, tests `L446-L633`.
  - N=2: `rec_0611_speed_gate_var_lane_count_2/rev_000001`, loop/shared-center policy `L242-L466`, tests `L467-L657`.
  - N=3: `rec_0611_speed_gate_var_lane_count_3/rev_000001`, loop/shared-center policy `L242-L441`, tests `L442-L616`.
- interpolation/source range: 1–3 directly represented.
- extrapolation gate: 4–5 repeat the accepted invariant local lane cell；host chain grows rather than compressing local geometry；N=5 must pass joint-count, compile-budget and all-leaf closed/mid/max clearance.
- sampling domain: `(1,2,2,3,3,4,5)`，small/observed N weighted higher while boundaries remain reachable.
- copied object/naming/joint policy: for lane `i`, emit `lane_i_left_leaf` from pedestal `i` right socket and `lane_i_right_leaf` from pedestal `i+1` left socket；one independent REVOLUTE each.
- capacity formula: `pedestal_count=N+1`, `joint_count=2N`, constant local lane pitch, overall footprint linear in N.
- `validation_counts`: `{1,2,3,4,5}`；observed anchors 1/2/3, extrapolated representative 4, maximum 5；N=1 and N=5 receive full-chain motion checks.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 取值 / 来源或理由 |
|---|---|---|---|
| ① 骨架图 | part-joint graph | 有 | `N+1` cabinet / `2N` moving-leaf graph + flush/raised reader fixed layer；source-backed |
| └ multiplicity | 同构件 ×N | 有 | N=1–5；见 §8，精确 copy-rule 来源和边界 gate |
| ② 关节类型 | edge type/axis | 有（固定） | only source-backed REVOLUTE vertical spindle；retract blocked |
| ③ Primary Form Family | core recognizable geometry | 有 | 3 CadQuery host forms + 4 sourced barrier profiles；all registered in slot choices |
| ④ 表面装饰 | host-conformal visuals | 有 | source-backed side inset、status band、cap seam；all derive from realized host dimensions and attach to final host surface |
| ⑤ 尺寸/行程 | dims/range | 有 | host H/depth, leaf reach/height, swing `[1.25,1.48]`; sampled collision and all-leaf closed/mid/max |
| ⑥ 涂装 | material/color | 有 | 5 palettes；painted/stainless metal + transparent glass/acrylic；sampled per seed |

## 采样与覆盖审计

理论离散域：`3 × 4 × 2 × 5(N) × 5(palette) = 600`；mechanism 固定 swing，不乘虚假候选。

实际合法域由公共 socket/spindle InterfaceSpec、lane-pitch equation、reader Y-side gate、source primitive identity和 sampled swept clearance定义。跨来源模块允许生成新资产，不要求同一 record 共现；每一 seed 都重新计算依赖几何，禁止 unchecked Cartesian product。

seed_domain_policy: `procedural_first`；seed 0 不特殊；无 regression override。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent seeded choices + weighted N；`resolve_config` derives all coupled geometry | `slot_choices_for_seed` exactly matches build |
| compatibility matrix | all reviewed swing roots use common interface；curved/full/waist recompute leaf/spindle/clamp heights；reader stays negative-Y | current + sampled collision, closed seam, MatingContract |
| controlled local variation | host height/depth, leaf reach/height, swing angle within table bounds | no interface/origin/category break |
| regression overrides | none | no curated modulo table |
| random sweep | canonical 0–35 + corner plan；explicit N=1..5 boundary configs | axis realization, N=5, all leaf poses |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| pedestal_form | 3 | yes | yes | all source-backed |
| barrier_form | 4 | yes | yes | all source-backed |
| reader_terminal | 2 | yes | no | reviewed source pool has exactly two legitimate reader structures |

## Validator

- `slot_choices_for_seed` reports implemented values and mechanism=`swing_revolute`.
- deterministic procedural sampler for all ordinary seeds；no seed-0 special path.
- exact `N+1` pedestals and `2N` independently jointed complete leaves for N=1..5.
- each non-FIXED child has real spindle/socket/bearing support and a `MatingContract`.
- `lane_pitch`/anti-pinch seam derive from host width, pivot offset and leaf reach.
- every source primitive family remains CadQuery mesh where source is CadQuery/curved.
- current-pose plus sampled all-joint collision and targeted all-leaf closed/mid/max motion.
- no overlap allowance；spindle-bearing capture is modeled with annular running clearance.
- N=5 stays inside compile budget and keeps local interfaces invariant.

## Reject cases

- any vertical/telescopic retract module or deleted/experimental retract source enters sampling.
- any `wings_per_lane` independent axis or lane with other than two opposed leaves.
- N outside 1–5, pedestal count ≠N+1, joint count ≠2N, or overall host compressed instead of grown.
- box/flat placeholder replacing hex loft, rounded body or curved shell source primitive.
- leaf panel changes profile/height without matching spindle, clamp, brackets, lane pitch and swept proxy.
- reader, host, sibling or adjacent lane collision in closed/mid/max.
- facade-only leaf, invisible/fake support, disconnected active part, wrong joint axis/open direction.
- any overlap allowance, including broad part scope or unnecessary spindle-bearing waiver.
- output no longer reads as a pedestrian access-control speed gate.

## 与相邻类别的边界

- 不混入 `sliding_turnstile`：其 barrier 在 hollow cabinet/dual rail 内 PRISMATIC horizontal retract；本类是外侧 vertical spindle REVOLUTE swing。
- 不混入 tripod turnstile：没有 rotating three-arm hub。
- 不混入 ordinary fence：本类必须有 reader cabinets and independently actuated transparent leaves。
- 不混入 vertical retract experiment：该 profile upstream anchor不足且已从 production implementation 移除。

## Authoring 自检记录

| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| source completeness | 已枚举并读取 9/9 五星 records 的 record/revision/prompt/model；slot表只索引 reviewed source map 的 accepted records |
| schema/source self-check | 通过：①/②/③/N 均有 accepted exact line evidence，无 analogous/derived/n/a |
| mechanism/allowance self-check | 通过：complete leaf + real socket/annular bearing + MatingContract + all-pose plan；zero overlap allowances |
| diversity/compatibility self-check | 通过：3 host、4 barrier、2 reader、N=1–5、5 palettes；cross-source重组受 interface/dimension/identity/sweep gate |
| remaining human gate | 机械 sweep 后 coverage-driven visual QA；pending/approved hash gate before formal export |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | host/barrier/reader/mechanism | hex/flat/flush/swing | origin 001 | `L28-L59`,`L184-L356` | hex loft, flat leaf, flush controls, swing topology |
| S2 | host/reader/mechanism | drafted rounded/raised/swing | origin 002 | `L34-L91`,`L259-L419` | drafted rounded cabinet, raised terminal, swing interface |
| S3 | host | slim rounded | `rec_0611_speed_gate_var_pedestal_form_slim_rounded` | `L44-L88`,`L231-L421` | stadium-profile host |
| S4 | barrier | curved glass | `rec_0611_speed_gate_var_wing_form_curved_glass` | `L61-L103`,`L315-L410` | true curved shell + matching root |
| S5 | barrier | full height | `rec_0611_speed_gate_var_wing_form_full_height` | `L271-L356`,`L458-L472` | tall leaf envelope |
| S6 | barrier | waist high | `rec_0611_speed_gate_var_wing_form_waist_high` | `L113-L127`,`L365-L422` | rounded acrylic waist profile |
| S7–S9 | multiplicity | N=1/2/3 | three `lane_count` forks | ranges in §8 | repeated local cell, indexed naming, shared host, uniform joints |
