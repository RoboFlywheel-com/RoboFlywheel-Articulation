# sliding_turnstile modular spec

## 1. 元信息

| 项 | 值 |
|---|---|
| slug | `sliding_turnstile` |
| template path | `agent/templates/sliding_turnstile.py` |
| test path (optional) | none; mechanical authority is sweep-pipeline + blocker audit |
| stage | `SPEC_ONLY_DRAFT` |
| authoring_status | `implementation_ready` |
| __modular__ | `True` |
| pattern | `mixed`（parallel children + multiplicity） |

## Category Binding

`category_slug=sliding_turnstile` · `template_slug=sliding_turnstile` ·
`mechanism_profile=horizontal_prismatic_retract` · `export_namespace=sliding_turnstile`。
机器真值见 `articraft_template_authoring/category_template_registry.json`；不得混入 swing
或 vertical retract joint graph。`diversity_profile=constrained`：本类固定一个诚实 horizontal
retract spine，核心词汇由 3 种 hollow host、4 种门翼和 2 种 reader 构成；高风险由
`Visual Risk` 独立表达。

## 2. 5 星样本阅读摘要

| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples with `category_slug=sliding_turnstile` |
| source_index_policy | only the eight source-map-approved module records are indexed below |

已逐一读取全部八条记录的 `record.json`、`revision.json`、`prompt.txt` 与完整
`model.py`。其中 origin 003 提供空心横向收纳基线；lane-count-4 提供 N 复制规则；
其余六条分别提供两种柜体、三种门翼、raised reader 和两个修复后的机械 probe。
旧 swing origins、solid-host origin 002 及其衍生件不进入本 spec。

## 3. 核心身份

本类是商业人行横向收纳式闸机：`N+1` 个固定空心驱动柜体形成 N 条通道；每条通道由
左右各一片完整安全玻璃门翼关闭，并以独立水平 PRISMATIC joint 收回相邻柜体的真实内腔。
共享中间柜体同时容纳两片门翼，必须使用沿 Y 深度错开的两套开口、收纳腔与双侧导向。
本实现固定为 horizontal retract；不得混入 swing turnstile、tripod turnstile、solid cabinet、
vertical retract 或只有装饰槽却无内腔的 speed gate。

## 4. 槽位 + 候选模块表

### Slot A：`pedestal_form`（③ Volumetric Envelope Form）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `capsule_hollow` | origin_anchor | `rec_picturex_0611__sliding_turnstile__003__png_2a8af54613b6444f808d94553318b240/rev_000001` | `L35-L101`, `L163-L297` | eligible with all four leaves after host-specific opening derivation | stadium/capsule outer shell, offset inner void, side mouths, slotted cap/ring and bilateral/depth-paired guides |
| `slim_capsule_hollow` | forked_anchor | `rec_0611_sliding_turnstile_var_pedestal_form_slim_capsule/rev_000001` | `L35-L113`, `L135-L326` | eligible with all four leaves after host-specific opening derivation | compressed elliptical end caps, thinner positive wall, same hollow dual-track topology |
| `round_hollow` | forked_anchor + compatibility_probe | `rec_0611_sliding_turnstile_var_pedestal_form_round_dual_track/rev_000001` | `L58-L202`, `L213-L398`, `L399-L730` | initial sampler allows `rectangular` only; other leaf families are gated | shared circular descriptor drives shell, void, mouth chord, slotted cap/ring and shell-seated guides |

### Slot B：`barrier_form`（③ Planar Boundary Form）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rectangular` | origin_anchor | origin 003 `/rev_000001` | `L102-L112`, `L266-L314` | eligible with all hosts | standard tall rounded-rectangle safety glass + root spine + drive shoe/bearing |
| `waist_high` | forked_anchor | `rec_0611_sliding_turnstile_var_panel_form_waist_high_glass/rev_000001` | `L102-L112`, `L123-L316`, `L317-L537` | eligible with capsule/slim hosts | reduced-height outline; opening bottom/top, root and guide height derive from the same descriptor |
| `full_height` | forked_anchor | `rec_0611_sliding_turnstile_var_panel_form_full_height_glass/rev_000001` | `L103-L113`, `L124-L317`, `L318-L536` | eligible with capsule/slim hosts | floor-near full-height outline; full-height mouth and root/guide consumers |
| `sloped_shoulder` | forked_anchor + compatibility_probe | `rec_0611_sliding_turnstile_var_barrier_planform_sloped_shoulder_dual_track/rev_000001` | `L31-L91`, `L103-L191`, `L202-L437`, `L438-L781` | eligible with capsule/slim hosts | one `PanelFormDescriptor` drives mirrored XZ outline, root spine, shoe/bearing and swept envelope |

### Slot C：`reader_module`（① functional static skeleton）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flush_sensor` | origin_anchor | origin 003 `/rev_000001` | `L113-L122`, `L203-L265` | eligible on every host; position is host/track-derived | cap-integrated credential pad and status surface, fused into static host |
| `raised_biometric` | forked_anchor | `rec_0611_sliding_turnstile_var_reader_module_raised_biometric/rev_000001` | `L113-L216`, `L217-L415`, `L416-L725` | eligible only if plinth footprint clears all top slots | cap-supported plinth, raised terminal body, screen, camera aperture and status light; no extra FIXED part |

本类别只有一种 source-backed ② 主运动：horizontal PRISMATIC retract；它是 module-local fixed
mechanism spine，不伪造为单候选 slot。Multiplicity `lane_count` 附着于整个 host/leaf module family，
不是 N=2…6 的五个 candidate。

## 4.1 Form Dependency Contracts

| ③ candidate/family | accepted anchors + `model.py:Lx-Ly` | master descriptor/profile | dependent consumers | derivation/offset/clearance rules | congruence/clearance validator | status |
|---|---|---|---|---|---|---|
| capsule / slim / round host | origin 003 `L35-L101`; slim `L35-L113`; round `L58-L202` | `HostFormDescriptor`（width/depth/wall/profile family）+ resolved track descriptors | outer shell; inner void; side mouth; top cap slot; trim slot; rail span; reader support footprint | void=`inset(profile, wall)`; every mouth/slot centered at its track; rails terminate on inner shell; reader footprint avoids every slot | positive wall; profile/cap congruence; two-track Y separation; connected guides; child swept envelope inside void | eligible |
| rectangular / waist / full leaf | origin 003 `L102-L112`; waist `L102-L112`; full `L103-L113` | `BarrierFormDescriptor` XZ outline | glass; side mouth bottom/top; root spine; drive shoe; bearing; guide vertical span; swept envelope | one outline supplies bottom/root-top/tip-top; mouth has positive Z/Y clearance; root and shoe overlap the glass and each other physically | mirrored profile; shared thickness; root/shoe continuity; closed/mid/max shell/cap/foundation clearance | eligible on capsule/slim; round non-rectangular gated |
| sloped shoulder | sloped probe `L31-L91`, `L159-L191` | `BarrierFormDescriptor` mirrored polygon | glass; root spine; shoe; bearing; opening; guide span; swept envelope | unchanged root InterfaceSpec; tip/shoulder values sampled once; no rectangular backing panel or decorative slope overlay | mirrored vertices; root interface invariance; mouth congruence; closed/mid/max clearance | eligible on capsule/slim |

没有无来源的③外推；这里的四种门翼和三种柜体全部是 direct source-backed。模板仍使用共享
descriptor，让每种来源形态与所有容纳/匹配消费者共同派生，避免孤立换形。

## Compatibility Gates

`round_hollow × {waist_high, full_height, sloped_shoulder}` 明确 deny；已验收 round well
只捕获 rectangular leaf。其他 hollow host 必须从 barrier descriptor 同步派生 mouth、well、
两侧 rail 和 hidden length，不能把门翼装到没有容纳槽的柜体上。

## Combination Domain

- diversity profile：`constrained`，硬下限 16。
- core domain：未 gate 为 `3 × 4 × 2 = 24`；round-host gate 排除 6 个 core tuples，合法 **18**，通过 profile。
- multiplicity coverage：`lane_count={2,3,4,5,6}` 全部可达；边界覆盖 `2/4/6`。
- raw domain：未 gate 为 `24 × 5 = 120`；round-host gate 排除 30，合法 **90**。
- palette、连续 scale 和 N 不计入 core。旧的 90-vs-200 人工例外已由 schema-v2 profile
  契约取代；后续只能补真实耦合候选，不能放宽 N 或开放 round×非标准门翼凑数。

## Visual Risk

`hidden_slide`、`multi_joint`。视觉审核必须核对完整 hidden well、双侧纵向 rail、全行程
啮合，以及 closed/mid/max 中门翼没有扫入 host shell。

## 5. 槽位图（slot graph）

pattern: `mixed`

```text
floor_anchor
  └─ pedestal_form × (N+1) [static visuals, hollow host chain, constant lane_pitch]
       ├─ reader_module × (N+1) [static host visuals; slot-clearance gate]
       └─ lane i, side s: PRISMATIC +X/-X rail interface → barrier_form × 2N
```

- Host centers lie on the world X axis; lane i is between host i and i+1.
- Every internal host emits two Y-depth-offset `TrackDescriptor`s; end hosts emit one.
- Each barrier joint origin is its host-side mouth center; axis points from the lane back into that host;
  range is `[0, travel]`, with 0=closed and max=fully retracted.
- Parent mating face is the named upper guide bearing face; child mating face is the named shoe bearing;
  the two touch without modeled penetration. The opposite guide provides visible lateral capture.
- `round_hollow × {waist_high, full_height, sloped_shoulder}` is gated/rejected in the initial sampler;
  it must not silently fall back or enter the Cartesian product.

## 6. 每槽位 Module Emits / Interfaces

### Slot A / all host candidates

| emits | 描述 | 来源 |
|---|---|---|
| parts | one root `floor_anchor`; `N+1` named shell/cap/trim/foot visual groups | origin 003 `L163-L265`; N=4 `L150-L337` |
| internal joints | none; host and reader details are static parent visuals | authoring Rule 1 + source loops |
| upstream interface | floor contact plane z=0; each shell seats on its named foot/backing plate | origin 003 `L163-L265` |
| downstream interface | one or two named horizontal track descriptors with mouth center, Y depth, guide faces and usable cavity chord | origin 003 `L223-L265`; round `L138-L202`, `L331-L398` |

### Slot B / all barrier candidates

| emits | 描述 | 来源 |
|---|---|---|
| parts | `gate_{lane}_{side}` with connected glass, root spine, drive shoe and shoe bearing | origin 003 `L266-L314`; sloped `L438-L560` |
| internal joints | one PRISMATIC joint per leaf, world X axis toward host, `[0, travel]` | origin 003 `L315-L526`; N=4 `L150-L337` |
| upstream interface | shoe bearing ↔ corresponding host upper-guide face at the side mouth | round `L399-L730`; sloped `L438-L781` |
| downstream interface | free leading edge; opposing pair leaves category-appropriate anti-pinch center gap | origin 003 `L414-L526` |

### Slot C / reader modules

| emits | 描述 | 来源 |
|---|---|---|
| parts | no new part; named sensor or plinth/body/screen/camera/status visuals on each host | origin 003 `L203-L265`; raised `L217-L415` |
| internal joints | none | sources |
| upstream interface | host-specific cap support patch outside all top slots | raised `L113-L216`, `L417-L555` |
| downstream interface | entrance-facing credential surface | raised source |

## 6.5 活动机构与运动净空契约

| mechanism/module | complete moving solid | parent support/guide | mating interface | joint origin/axis/range | closed/mid/max swept envelope + minimum clearance | exact intentional-contact elements | validator |
|---|---|---|---|---|---|---|---|
| horizontal retract leaf (all four forms) | congruent glass profile + root spine + lower drive shoe + named shoe bearing, all mutually contacting | true hollow shell and side mouth; two longitudinal side guide faces per track; internal hosts have two Y-offset tracks; each guide embeds into the uncut shell wall rather than stopping at a coincident face | exact zero-penetration `shoe_bearing` face to named `guide_upper` face; opposite `guide_lower` captures with positive running clearance | mouth center; axis `(-direction,0,0)`; `[0, exposed_reach]` | shell/cap/mouth clearance ≥2 mm; sibling-track Y separation ≥20 mm; opposing leaves keep ≥12 mm closed gap; shoe retains ≥30 mm rail overlap at 0/mid/max | none; the mating faces touch without represented overlap | `fail_if_parts_overlap_in_sampled_poses`; targeted all-joint closed/mid/max poses; N=2 and N=6 engagement + sibling clearance; allowance count=0 |

任何 shell↔gate、root↔gate、sibling gate、element pair 或 whole-part allowance 都是 blocker。
`guide_upper`↔`shoe_bearing` 通过共享坐标派生为真实接触但零穿透，不依赖碰撞豁免。

## 7. 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `pedestal_form` | enum | capsule/slim/round hollow | capsule | choice | round downstream gate restricts barrier form | Slot A |
| `barrier_form` | enum | rectangular/waist/full/sloped | rectangular | conditional | round host → rectangular; capsule/slim → all four | Slot B compatibility evidence |
| `reader_module` | enum | flush/raised | flush | conditional | host-specific footprint must clear all top slots | Slot C |
| `palette_style` | enum | stainless_blue/graphite_teal/bronze_smoke/white_green | stainless_blue | choice | deterministic per seed; all visuals consume resolved palette | source palettes + ⑥ record-only |
| `lane_count` | int | `[2,6]` | 2 | conditional | host=`N+1`, moving leaves/joints=`2N` | origin 003 + lane_count_4 |
| `lane_pitch_scale` | float | `[0.96,1.08]` | 1.0 | independent | sampled then clamped | source proportions |
| `host_height_scale` | float | `[0.96,1.06]` | 1.0 | independent | sampled then clamped | source proportions |
| `leaf_reach_scale` | float | `[0.94,1.05]` | 1.0 | independent | sampled then projected to lane equation | source proportions |
| `lane_pitch` | float | derived | 0.95 m | equation | `host_width + 2*closed_leaf_reach + center_gap` | origin 003 geometry |
| `travel` | float | derived | 0.295 m | equation | `closed_leaf_reach`; max pose places leading edge at mouth while retaining shoe engagement | origin 003 |
| track separation | constraint | — | — | inequality | `abs(track_y1-track_y0) >= shoe_depth + 2*guide_thickness + 0.020` | round probe |
| cavity fit | constraint | — | — | inequality | usable inner chord ≥ leaf total length + 4 mm; mouth width ≥ panel/root thickness + 4 mm | source-map MatingContract |
| reader clearance | constraint | — | — | conditional | reader AABB disjoint from every slot AABB by ≥8 mm | raised reader probe |

采样顺序：先选 host/reader/N 与 independent scales，再按 compatibility gate 选 leaf，随后派生
lane pitch/travel/track descriptors，并投影 cavity、slot、reader 和 swept-clearance 不等式；builder
不负责猜测或随机降级。

### 7.5 编译预算 / compile budget

预算 `<=20 s/seed`，包括 N=6。依据：来源的 N=4 CadQuery 版本约 5.9 s；模板对同一
host/track signature 和同一方向 leaf 复用 mesh，主体 tolerance 约 1.5–2 mm，避免按 lane 重做
布尔。N=6 smoke 与 corner 必须实测，超预算先减少重复 tessellation 而不是砍 N 或行程。

## 8. Multiplicity / Copy Logic

- `count_param`: `lane_count`。
- `observed_N`: `{2,4}`；`derived_N_range`: every integer `[2,6]`。
- source evidence:
  - N=2 origin 003 `/rev_000001` `model.py:L163-L314`：3 hosts、4 leaves、共享中间 host 双轨；
  - N=4 `rec_0611_sliding_turnstile_var_lane_count_4/rev_000001` `_compute_pedestal_tracks`
    `model.py:L129-L149`、build loop `L150-L337`、joint/tests `L338-L544`。
- interpolation: N=3 uses the same constant-pitch host chain and parity-alternating track rule between
  observed 2 and 4; no per-N asset is required。
- extrapolation: N=5–6 are allowed only while host count=`N+1`, active joints=`2N`, each internal host
  has two independent depth-offset tracks, local cavity/wall/guide/root interfaces remain invariant,
  footprint grows linearly and N=6 stays under compile budget with clean closed/mid/max sweep。
- sampling: N=2/3 common, N=4 anchor moderate, N=5/6 rarer; every value remains reachable.
- placement/naming: host `pedestal_i`; lane i emits `gate_{i}_0` (host i, +X extension) and
  `gate_{i}_1` (host i+1, -X extension); one uniform PRISMATIC joint `gate_{i}_{s}_slide` per gate。
- validation_counts: `{2,3,4,5,6}`; required boundaries `{2,6}` run all-joint closed/mid/max,
  host/leaf/joint cardinality, internal-track separation, guide engagement, reader clearance and compile budget。

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | functional reader skeleton `flush_sensor` / `raised_biometric`；moving graph 随 N 变为 `N+1` hosts + `2N` source-backed leaves |
| └ multiplicity | 同构件 ×N | 有 | §8：observed `{2,4}`，derived `[2,6]`，N=3 interpolation，N=5–6 gated extrapolation |
| ② 关节类型 | 同连接关节怎么动不同 | 有（固定单一 spine） | 仅 horizontal PRISMATIC world X；origin 003 `L315-L526`，N=4 `L338-L544`；swing 明确排除 |
| ③ 主体形态家族 | 换可识别几何形态原型 | 有 | host Volumetric Envelope: capsule/slim/round；leaf Planar Boundary: rectangular/waist/full/sloped；全部 direct source-backed 并登记入 slot choices |
| ④ 表面装饰 | 不改轮廓的表面叠加 | 有 | cap trim、service seam、status strip/reader bezel；`record_only`，均从最终 host surface/slot layout 派生并避开开口 |
| ⑤ 尺寸/行程 | 连续大小/比例/行程 | 有 | lane/host/leaf scales 见 §7；每个 PRISMATIC `[0,travel]`，0=closed、mid、max=inside host；sampled collision + targeted poses |
| ⑥ 涂装 | 材质/颜色 | 有 | 4 palettes: brushed metal/clear glass、graphite/teal glass、bronze/smoke glass、white metal/green glass；每 seed 采样且所有 visuals 使用 palette |

最终视觉 QA 用 set-cover 覆盖 3 host、4 leaf、2 reader、N={2,3,4,5,6}，尤其 N=6、
round gate、raised reader 和 sloped/full-height close-up；每个 moving seed 展示 closed/mid/max。

## 9. 采样与覆盖审计

理论未 gate 组合数：`3 × 4 × 2 × 5 = 120`（不计 4 palettes）。实际合法离散域：
capsule/slim 各 `4×2×5`，round 暂为 `1×2×5`，合计 90；reader 仍须逐 host layout
通过 top-slot footprint gate。跨来源组合可生成来源中未出现的新资产，但不开放未经验证的 round×非标准门翼。

- `seed_domain_policy`: `procedural_first`; seed 0 无特殊处理；无 curated/modulo table 或 regression override。
- sampler: 先采 `pedestal_form`、`reader_module`、N、scale；按 matrix 从可达 leaf 集合采样；
  `resolve_config` 校验显式 config，非法 round×nonstandard 直接回落到 documented safe rectangular only
  （普通 sampler 从不提出非法值；显式 regression config 被 canonicalize 并在 choices 中如实反映）。
- domain target：core 合法 18、raw 合法 90；1000 seeds 的 raw tuple 应接近饱和。N 只增加
  raw 配置和边界覆盖，不膨胀 core。
- controlled local parameterization: 三根 independent scale 按 §7 clamp，lane pitch/travel 为 equation，
  cavity/track/reader 为 inequality/conditional；不改变 joint spine、copy policy 或类别 identity。
- random sweep: canonical 0–35 + corner；axis realization 必须出现每个 registered value；N=6 corner clean。

### Compatibility matrix

| host × leaf | rectangular | waist | full | sloped |
|---|---|---|---|---|
| capsule | legal：origin 003 | legal：waist/full anchors，派生 mouth | legal | legal：sloped probe |
| slim capsule | legal：slim anchor | legal after shared descriptor/slot validators | legal after validators | legal after validators |
| round | legal：round probe | gated | gated | gated |

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | deterministic conditional sampling; all candidates reachable; no seed special case | `slot_choices_for_seed` equals resolved build choices |
| compatibility | matrix above + reader footprint + N boundary gates | interface/dimension/identity/swept clearance; no unchecked Cartesian product |
| controlled local variation | independent scales then equation/inequality projection | wall, track, mouth, guide and center gap remain positive |
| regression overrides | none | — |
| random sweep | 0–35 final + corner, dedicated N=2..6 tests | axis realization, failure clusters, allowance audit, N=6 budget |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| pedestal_form | 3 | yes | yes | all source-backed hollow hosts |
| barrier_form | 4 | yes | yes | all source-backed shared profiles |
| reader_module | 2 | yes | no | 5★池只有两种真实 reader skeleton；不凭空发明第三种 |

## 10. Validator

- `slot_choices_for_seed` 返回实际 resolved host/leaf/reader/N，不登记 swing 或 solid host。
- `config_from_seed` 对所有普通 seeds 使用 deterministic procedural sampling，seed 0 不特殊。
- host=`N+1`、gate/joint=`2N`、每个 joint 为 horizontal PRISMATIC；N=2..6 全覆盖。
- every internal host has two distinct Y-depth track descriptors; end hosts exactly one。
- every host is hollow with positive wall, true side mouths and slotted cap derived from the selected form。
- each moving gate has connected glass/root spine/shoe/bearing and visible bilateral guides。
- `fail_if_parts_overlap_in_sampled_poses(...)` + targeted closed/mid/max poses；N=2 与 N=6 检查全部 gates。
- guide engagement positive at closed/mid/max; sibling tracks and opposing gates stay separated。
- round chord/cap/slot congruence and round×nonstandard gate are enforced before build。
- raised reader plinth contacts cap and clears every top slot/swept envelope。
- whole-part/broad、element、unreviewed 和 weak-reason allowance count 必须全部为 0。
- compile budget ≤20s/seed at N=6。

## Reject cases

- swing、vertical retract、tripod 或 solid origin-002 host 混入本 slug。
- panel 穿入实心柜体，或只有黑色装饰槽而无真实 inner void / side mouth。
- shared host 缺第二轨、两轨同一 Y 深度、中央假轨或全行程失去 guide engagement。
- 只有 glass facade，缺 root spine / shoe / bearing；或为测试添加假横条/假支撑。
- round host 与 gated nonstandard leaf 被 sampler 组合，或 reader 覆盖 top slot。
- closed/mid/max 任一位姿 gate↔shell/cap/foundation/sibling 穿模或方向反转。
- whole-part/broad `allow_overlap`，或用弱理由掩盖 shell↔gate。
- N 超出 `[2,6]`、host/gate/joint 数不满足公式、N=6 超预算或边界净空失败。

## 11. 与相邻类别的边界

- 不该混入 `speed_gate` swing implementation：主运动、host accommodation 和 slot graph 不同。
- 不该混入 tripod turnstile：没有旋转毂或三叉杆。
- 不该混入普通 fence / door：必须保留读卡柜体链与每 lane 双向收纳机构。
- 不该混入 vertical retract：本类没有向下井/向上升降结构。

## 12. Authoring 自检记录

| 项 | 结论 |
|---|---|
| authoring_status | `implementation_ready` |
| self-check notes | 已按 `SPEC_REVIEW_TEMPLATE.md` 全项自检：8/8 sources 完读；所有①②③/N 候选均有精确来源；3×4×2 slots、N=2–6、form consumers、mechanism/swept/compatibility contracts 齐全；round 高风险组合显式 gated；无 broad allowance 计划；待模板 sweep 与 hash-bound visual QA 验证。 |

## 13. 模板实现备注

- 复用同 host/track signature 的 CadQuery shell mesh；N 增长只复制 visuals/joints。
- 静态 host/reader 全部作为 `floor_anchor` visuals；moving gates 才是 separate parts。
- MatingContract 指向真实 guide/shoe bearing face；几何采用 running clearance，因此不声明 overlap。
- round×非标准 leaf 暂不进入 seed domain，后续只有新增 compatibility probe 或完整 chord/opening/clearance
  证明后才能打开，不拆 category slug。

## 14. Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | host/mechanism/N | capsule + rectangular + N=2 | origin 003 | `L35-L112`, `L163-L526` | hollow host、dual tracks、2N PRISMATIC copy rule |
| S2 | host | slim capsule | slim fork | `L35-L113`, `L135-L540` | slim descriptor/cavity |
| S3 | leaf | waist | waist fork | `L102-L112`, `L123-L537` | waist outline/opening |
| S4 | leaf | full | full fork | `L103-L113`, `L124-L536` | full-height outline/opening |
| S5 | reader | raised | reader fork | `L113-L216`, `L217-L725` | supported biometric group |
| S6 | N | lane_count=4 | N=4 fork | `L129-L149`, `L150-L544` | general host/track/gate loops |
| S7 | host/probe | round | round dual-track fork | `L58-L202`, `L213-L730` | circular coupled consumers + element-level bearing idiom |
| S8 | leaf/probe | sloped | sloped dual-track fork | `L31-L91`, `L103-L781` | shared panel descriptor + root/shoe/bearing |
