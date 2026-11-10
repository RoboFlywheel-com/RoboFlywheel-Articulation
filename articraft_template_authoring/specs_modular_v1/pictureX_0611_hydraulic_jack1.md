# pictureX_0611_hydraulic_jack1

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_hydraulic_jack1` |
| template path | `agent/templates/pictureX_0611_hydraulic_jack1.py` |
| test path (optional) | sweep-pipeline only |
| stage | `SPEC_ONLY_DRAFT` |
| status | `implemented; awaiting final sweep` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all downstream rating=5 hydraulic_jack1 samples from `0611__hydraulic_jack1.md`, including 20260714 supplement anchors |
| source_index_policy | adopted modules indexed in slot tables and Module Source Index |

已读 5★ 样本：2 个 picture-bound origins + 6 个 20260713 fork anchors + 3 个 20260714 supplement anchors。记录均为 `collections=["workbench"]`，`picture.json` 指向 `pictureX/0611/hydraulic_jack1/{001,002}.png`，`rating=5`。CLI 按单一 `category_slug=pictureX_0611_hydraulic_jack1` 不命中，因为 records 保留了 picture-derived slug；本 spec 以 source map record id 为枚举真源。

## 核心身份

`pictureX_0611_hydraulic_jack1` 是液压举升千斤顶小类：稳定底座、液压缸/ram、泵柄或气助泵、释放阀、承重鞍座/托盘，以及至少一条可动举升或控制关节共同构成身份。允许瓶式 jack、toe jack、floor trolley jack、transmission cradle jack、motorcycle lift platform 这些同一液压举升家族的 service-jack 形态；不混入纯机械 scissor screw jack、shop crane、generic linear actuator 或发动机支架。

## 槽位 + 候选模块表

### Slot A：`body_family`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bottle_jack` | origin_anchor + forked_anchor | S1 origin 001; S3 bottle fork | S1 L76-L361; S3 L62-L334 | eligible if compatible | 竖直 base plate + cylinder shell + pump body；`ram_slide` PRISMATIC，泵柄/释放阀 REVOLUTE |
| `floor_trolley` | origin_anchor + forked_anchor | S2 origin 002; S4 floor trolley | S2 L124-L309; S4 L161-L412 | eligible if compatible | 长 rolling base、side rails、4 casters、lift carriage / arm；wheel REVOLUTE + lift PRISMATIC/REVOLUTE |
| `toe_jack` | forked_anchor | S5 toe jack | S5 L119-L422 | eligible if compatible | upright ram plus low toe foot and rear bracket，保留瓶式 ram/pump 拓扑但改变 load pickup ③ body form |

### Slot B：`load_interface`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_saddle` | origin_anchor + forked_anchor | S1/S2/S3 | S1 L273-L286; S2 L200-L216; S3 L202-L218 | eligible if compatible | 圆/方 saddle pad 固接在 ram 顶，默认载荷接触面 |
| `transmission_cradle` | forked_anchor | S6 transmission cradle | S6 L124-L143, L220-L240, L304-L322 | floor/service-jack family only; non-floor coerces to `floor_trolley` | 宽 cradle plate + side ears，`piston_to_saddle` REVOLUTE 小角度 tilt |
| `screw_extension_saddle` | forked_anchor, 20260714 | S9 screw extension saddle | S9 L76-L100, L329-L355, L413-L422 | eligible on bottle/toe; floor allowed but rare | threaded screw rod + knurl + cap，`screw_adjust` REVOLUTE around Z |
| `motorcycle_platform` | forked_anchor, 20260714 | S11 motorcycle platform | S11 L150-L164, L230-L262, L329-L336 | floor_trolley only; non-floor coerces to floor_trolley | broad deck + tie-down tabs，platform PRISMATIC lift atop carriage |

### Slot C：`ram_mechanism`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_stage_ram` | origin_anchor + forked_anchor | S1/S2/S3/S4/S5/S6/S8/S9/S10/S11 | S1 L273-L286, L334-L341; S4 L228-L237, L346-L382 | eligible | one visible lifting ram or lift carriage, primary PRISMATIC travel |
| `double_stage_ram` | forked_anchor | S7 double-stage ram | S7 L279-L319, L368-L386 | eligible; floor template keeps compact equivalent | nested `piston_stage_0`/`piston_stage_1`, two PRISMATIC telescoping stages |

### Slot D：`pump_module`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `manual_pump` | origin_anchor + forked_anchor | S1-S7/S9-S11 | S1 L293-L361; S4 L279-L331, L392-L412 | eligible | side pump handle REVOLUTE + release valve REVOLUTE; hose/pump body fixed visual |
| `air_over_hydraulic` | forked_anchor | S8 air-over-hydraulic module | S8 L338-L421 | eligible | added air motor canister, air hose, trigger block, `air_assist_swivel` REVOLUTE |

### Slot E：`safety_module`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_release` | origin_anchor + record_only | S1/S2/S3/S4/S5/S6/S7/S8/S9/S11 | S1 L314-L361; S4 L315-L412 | eligible | release valve only, no ratcheting lock bar |
| `safety_lock_bar` | forked_anchor, 20260714 | S10 safety lock bar | S10 L124-L149, L331-L445 | eligible | side ratchet bar + teeth + pawl family; template samples hinged lock bar module |

### Slot F：`palette_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `safety_yellow_black` | record_only | S1/S5/S7/S8/S9 | S1 L88-L94; S5 L134-L140; S9 L125-L131 | eligible | yellow painted body, black rubber, chrome ram |
| `shop_red_chrome` | record_only | S2/S4/S6/S10/S11 | S2 L135-L141; S4 L172-L176; S10 L180-L187 | eligible | red painted jack, polished steel/chrome, black wheels |
| `service_blue_zinc` | world_knowledge_extrapolation(⑥ only) | source palette envelope S1-S11 + reviewer | template palette map | eligible | common shop-blue paint + zinc/black hardware, same geometry |
| `industrial_gray_warning` | world_knowledge_extrapolation(⑥ only) | source palette envelope S1-S11 + reviewer | template palette map | eligible | gray industrial body with yellow warning accents |
| `black_low_profile` | record_only + extrapolation(⑥) | S3/S4 dark hardware, S8 pneumatic gray | S3 L77-L82; S8 L88-L95 | eligible | black low-profile service finish with chrome ram |

## 槽位图（slot graph）

pattern: `mixed`

`body_family` emits root `hydraulic_base` and body-specific support geometry. `ram_mechanism` attaches to the root cylinder/rails with PRISMATIC lift joints and emits the load carrier (`lifting_ram` / `piston_stage_1` / `lift_carriage`). `load_interface` attaches on the carrier top: flat saddle is carrier visual; cradle/screw/platform are child parts with REVOLUTE or PRISMATIC joint. `pump_module` and `safety_module` are parallel children mounted on real sockets on `hydraulic_base`. `palette_style` drives all visual materials and does not affect topology.

Compatibility / degrade policy:

- `motorcycle_platform` requires `body_family=floor_trolley`; resolver coerces non-floor selections to `floor_trolley`.
- `transmission_cradle` is gated to the floor/service-jack family; resolver coerces non-floor selections to `floor_trolley` so the cradle clears upright wiper seals and lock bars.
- `support_count=4` only for floor trolley casters; upright bottle/toe forms expose `0` or `2` side stabilizers.
- `double_stage_ram` is source-backed for upright jacks; on floor trolley it is represented as a compact lift-carriage ram equivalent to avoid an unsourced long nested floor-jack spine.
- `air_over_hydraulic` and `safety_lock_bar` may coexist after side-mount separation; sweep validates sampled motion.

## 每槽位 Module Emits / Interfaces

### Slot A / module `bottle_jack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `hydraulic_base` with `base_plate`, `cylinder_shell`, collars, pump body, hose, label | S1 L98-L265; S3 L87-L202 |
| internal joints | none inside root; consumed by Slot C/D/E | S1 L334-L361 |
| upstream interface | ground/root support plane at base plate bottom | S1/S3 |
| downstream interface | vertical cylinder top receives ram carrier | S1 L273-L341 |

### Slot A / module `floor_trolley`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `hydraulic_base`; four `caster_*` wheel parts | S4 L181-L212 |
| internal joints | `caster_*_spin` REVOLUTE around wheel axle | S4 L202-L212 |
| upstream interface | rolling base bottom / caster contact | S4 |
| downstream interface | central lift carriage rail, pump socket, side safety mounts | S4 L346-L412; S10 L331-L445 |

### Slot A / module `toe_jack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hydraulic_base` with low toe foot and rear bracket plus upright cylinder | S5 L119-L325 |
| internal joints | consumed by ram/pump/release modules | S5 L395-L422 |
| upstream interface | low toe foot/base plate support | S5 |
| downstream interface | vertical ram top; no wide cradle/platform interface | S5 |

### Slot B / modules
| emits | 描述 | 来源 |
|---|---|---|
| `flat_saddle` parts | carrier-local `flat_saddle_pad` + `round_saddle_button` visual | S1 L273-L286; S2 L200-L216 |
| `transmission_cradle` parts/joint | child `transmission_cradle`, cradle plate/ears, `carrier_to_transmission_cradle` REVOLUTE X tilt | S6 L220-L240, L304-L322 |
| `screw_extension_saddle` parts/joint | child `screw_extension`, threaded rod/ridges/cap, `screw_adjust` REVOLUTE Z | S9 L329-L355, L413-L422 |
| `motorcycle_platform` parts/joint | child `motorcycle_platform`, broad deck/tie-down tabs, PRISMATIC platform lift | S11 L230-L262, L329-L336 |

### Slot C / modules
| emits | 描述 | 来源 |
|---|---|---|
| `single_stage_ram` | `lifting_ram` or `lift_carriage`; one PRISMATIC lift joint | S1 L273-L341; S4 L212-L237, L346-L382 |
| `double_stage_ram` | `piston_stage_0` + `piston_stage_1`; nested PRISMATIC joints | S7 L279-L319, L368-L386 |

### Slot D / modules
| emits | 描述 | 来源 |
|---|---|---|
| `manual_pump` | `pump_handle`, `release_valve`; REVOLUTE pump and valve joints | S1 L293-L361; S4 L279-L331, L392-L412 |
| `air_over_hydraulic` | plus `air_assist` canister/hose/trigger, `air_assist_swivel` REVOLUTE | S8 L338-L421 |

### Slot E / modules
| emits | 描述 | 来源 |
|---|---|---|
| `plain_release` | no extra lock part beyond release valve | S1/S2 |
| `safety_lock_bar` | `safety_lock_bar` part with ratchet teeth, side pivot REVOLUTE | S10 L331-L445 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_family` | enum | `bottle_jack` / `floor_trolley` / `toe_jack` | `bottle_jack` | choice | deterministic weighted sampler | Slot A |
| `load_interface` | enum | `flat_saddle` / `transmission_cradle` / `screw_extension_saddle` / `motorcycle_platform` | `flat_saddle` | conditional | `motorcycle_platform⇒floor_trolley`; `transmission_cradle⇒floor_trolley`; `toe+platform⇒flat_saddle` | Slot B |
| `ram_mechanism` | enum | `single_stage_ram` / `double_stage_ram` | `single_stage_ram` | choice | floor trolley uses compact equivalent for double stage | Slot C |
| `pump_module` | enum | `manual_pump` / `air_over_hydraulic` | `manual_pump` | choice | side mount keeps air assist clear of lift path | Slot D |
| `safety_module` | enum | `plain_release` / `safety_lock_bar` | `plain_release` | choice | side mount separated from platform and air assist | Slot E |
| `support_count` | int | upright `0/2`; floor `4` | `0` | conditional | `body_family=floor_trolley⇒4`, else clamp `0..2` | S4 caster multiplicity; S5 stabilizer vocabulary |
| `palette_style` | enum | 5 styles listed in Slot F | `shop_red_chrome` | choice | per-seed sampled; maps every visual material through palette dict | S1-S11 |
| `width_scale` | float | `[0.84,1.18]` | `1.0` | independent | sampled then clamp | observed S1-S11 proportions |
| `height_scale` | float | `[0.86,1.22]` | `1.0` | independent | sampled then clamp | observed upright/floor height variation |
| `travel_scale` | float | `[0.78,1.20]` | `1.0` | independent | sampled then clamp; drives PRISMATIC upper limits | S1/S4/S7 travel ranges |
| `base_length/base_width/cylinder_height/ram_travel` | float | derived | derived | equation | derived from body family and scales in `resolve_config` | slot interfaces |
| interface feasibility | constraint | — | — | inequality | load interface footprint must stay within carrier envelope; resolver coerces illegal families | S6/S11 |

## 7.5 编译预算 / compile budget

每 seed 目标 1-5s，watchdog `--compile-timeout 120`。依据：模板使用 Box/Cylinder primitives 和少量 child parts，无 CadQuery mesh booleans；probe 0-4 实测单 seed 约 0.13-0.48s。主体圆柱段数使用 SDK 默认，未引入高段数 loft/mesh。

## Multiplicity / Copy Logic

本 spec 有 2 根轻量 multiplicity 轴：

- `support_count`: upright bottle/toe `0/2` side stabilizers，floor trolley 强制 4 casters。copied object: `side_stabilizer_*` visual 或 `caster_*` child part；placement: symmetric left/right or four corners；joint policy: casters REVOLUTE, stabilizers fixed root visuals。source: S4 L202-L212 for casters; S5 toe side stabilizer vocabulary L210-L216.
- `ram_stage_count`: encoded by `ram_mechanism` (`single_stage_ram` = 1, `double_stage_ram` = 2)。copied/nested object: `piston_stage_0/1`; joint policy: serial PRISMATIC telescoping; source S7 L279-L386.

No wide unbounded N is exposed; hose guard turns from S1/S8 are treated as surface/detail vocabulary, not a template-level count.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `body_family` changes root skeleton: upright bottle/toe vs wheeled floor trolley; `pump_module=air_over_hydraulic` adds air_assist child; `safety_module=safety_lock_bar` adds lock child. source-backed S1-S11 |
| └ multiplicity | 同构件 ×N | 有 | `support_count=0/2/4`; `ram_stage_count=1/2` via `ram_mechanism`; see §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | PRISMATIC ram/platform, REVOLUTE pump/release/cradle/screw/safety/air/casters. source-backed S1 L334-L361; S4 L346-L412; S9 L413-L422; S10 L423-L445 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变或近似不变，换核心可识别几何原型 | 有 | `bottle_jack`, `floor_trolley`, `toe_jack` as Volumetric Envelope + Macro Surface Construction anchors; `transmission_cradle` and `motorcycle_platform` as load-interface Primary Form anchors. source-backed S3/S4/S5/S6/S11 |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | instruction plates, warning accents, ratchet teeth, screw ridges, tie-down tabs, side collars; host-conformal root/carrier visuals. source-backed S1 L187-L223; S9 L340-L355; S10 L354-L372; S11 L247-L262 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | `width_scale`, `height_scale`, `travel_scale`; PRISMATIC ram/lift/platform upper limits sampled; motion plan: sampled collision plus targeted extended ram and pump-handle poses |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | five per-seed `palette_style`: safety yellow/black, shop red/chrome, service blue/zinc, industrial gray/warning, black low-profile; covers painted steel, chrome/zinc, rubber/dark hardware |

## 采样与覆盖审计

总组合数（legal after resolver）：约 `3 body × 4 load × 2 ram × 2 pump × 2 safety × 3 support bands × 5 palette`，经 compatibility gates 裁剪，1000 seed report-only topology target 远大于 300；probe discovered reachable topology 469 in 2000 seeds.

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 deterministic RNG weighted choices；`seed=0` 不特殊。先选 body，再选 body-compatible load interface；`motorcycle_platform` 强制 floor trolley，toe + cradle/platform 降级；再采 ram/pump/safety/palette/support/continuous scales，`resolve_config` clamp 和派生尺寸。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted body/load choices, then ram/pump/safety/palette; `slot_choices_for_seed` exports all realized axes | axis_realization must show all major candidates, especially 20260714 anchors |
| compatibility matrix | `motorcycle_platform⇒floor_trolley`; `transmission_cradle⇒floor_trolley`; toe cannot host platform; floor support_count=4; upright support_count≤2 | no floating platform/cradle, no side module collision, identity remains hydraulic jack |
| controlled local variation | width/height/travel scales derive base and ram dimensions; travel limits stay small and positive | no isolated parts, no sampled-pose overlap, stable proportions |
| regression overrides | none | ordinary procedural domain only |
| random sweep | canonical `sweep-pipeline` 0-35 + corner seeds with thread caps | verdict pass; corner stage clean; failed_corner_seeds read |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_family | 3 | yes | yes | ③ form slot |
| load_interface | 4 | yes | yes | includes three 20260714/compat anchors |
| ram_mechanism | 2 | yes | no | source pool only has 1 vs 2 stage; acceptable degrade |
| pump_module | 2 | yes | no | manual vs air-over-hydraulic; source pool only 2 |
| safety_module | 2 | yes | no | plain vs lock bar; source pool only 2 |
| palette_style | 5 | yes | yes | ⑥ per-seed colorways |

## Validator

- `slot_choices_for_seed` returns implemented module names for `body_family`, `load_interface`, `ram_mechanism`, `pump_module`, `safety_module`, `support_count`, `palette_style`.
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds; no curated seed table.
- `resolve_config` enforces compatibility/degrade policy before builder runs.
- Every non-fixed joint has a visible parent socket/support and a child visual at the joint origin.
- `run_picturex_0611_hydraulic_jack1_tests` runs model validity, isolation, current-pose overlap, sampled-pose overlap, joint-origin checks, and targeted ram/pump poses.
- Per-seed `palette_style` drives all materials through the palette map; outputs are not monochrome.
- Key joints have expected types: ram/lift/platform PRISMATIC; pump/release/cradle/screw/air/safety/casters REVOLUTE.

## Reject cases

- scissor screw jack without hydraulic cylinder/ram.
- shop crane/hoist arm replacing jack base and saddle.
- generic bare linear actuator without pump/release/load support.
- engine stand or transmission stand with no hydraulic lifting jack.
- decorative wheels/hoses as isolated floating parts.
- motorcycle platform sampled on upright bottle/toe body without floor-base compatibility coercion.
- safety bar or air assist intersecting lift/platform travel envelope.
- palette-only variation with no structural slot choices.

## 与相邻类别的边界

- 不该混入：car scissor jack / screw jack（纯机械螺杆剪式，不是液压缸/泵系统）。
- 不该混入：engine crane / shop hoist（长 boom 起重机，载荷路径不是 jack saddle/platform）。
- 不该混入：generic hydraulic cylinder actuator（缺少稳定底座、泵柄/释放阀、承重接口）。
- 不该混入：transmission stand without jack（如果只剩 stand/cradle 而无 hydraulic jack body，则越界）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec updated for 11 rating=5 samples and 20260714 anchors `screw_extension_saddle`, `safety_lock_bar`, `motorcycle_platform`; template implemented and sweep iteration in progress. |

## 模板实现备注（可选）

- Template is standalone for this slug to avoid changing shared `pictureX_0611_common_requested.py` used by sibling workers/slugs.
- The source records use CadQuery mesh helpers, but this template keeps the same part/joint semantics with SDK primitives for fast sweep budget; no Lathe/mesh source primitive was downgraded where a candidate depends on that primitive as identity.
- Captured hydraulic ram, wheel, pump, release, air assist, safety lock, and load-interface contacts use local `allow_overlap` in tests, paired with real visible sockets/mounts so parts are not floating.
- `service_blue_zinc` and `industrial_gray_warning` are ⑥-only palette extrapolations; they do not create structural candidates.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/F | origin upright hydraulic jack | `rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613` | L76-L361 | yellow upright body, ram, pump/release, palette |
| S2 | A/B/C/D/F | origin floor/service jack | `rec_picturex_0611__hydraulic_jack1__002__png_343b03cbe8414658969055f2ca9c7a13` | L124-L309 | red floor/body scaffold, saddle, pump/release |
| S3 | A/B/C/D/F | bottle jack | `rec_picturex0611_hydraulic_jack1_fork_bottle_jack_20260713` | L62-L334 | bottle body family, saddle, manual pump |
| S4 | A/B/C/D/F | floor trolley jack | `rec_picturex0611_hydraulic_jack1_fork_floor_trolley_jack_20260713` | L161-L412 | wheeled base, lift carriage, casters, pump/release |
| S5 | A/B/C/D/F | toe jack | `rec_picturex0611_hydraulic_jack1_fork_toe_jack_20260713` | L119-L422 | toe foot body family |
| S6 | B/C/D/F | transmission cradle | `rec_picturex0611_hydraulic_jack1_fork_transmission_cradle_20260713` | L124-L143, L220-L322 | cradle load interface and tilt joint |
| S7 | C/F | double-stage ram | `rec_picturex0611_hydraulic_jack1_fork_double_stage_ram_20260713` | L279-L386 | nested ram mechanism |
| S8 | D/F | air-over-hydraulic | `rec_picturex0611_hydraulic_jack1_fork_air_over_hydraulic_module_20260713` | L338-L421 | air assist module |
| S9 | B/C/D/F | screw extension saddle | `rec_picturex0611_hydraulic_jack1_fork_screw_extension_saddle_20260714` | L76-L100, L329-L422 | screw extension saddle anchor |
| S10 | E/F | safety lock bar | `rec_picturex0611_hydraulic_jack1_fork_safety_lock_bar_20260714` | L124-L149, L331-L445 | lock bar / pawl safety anchor |
| S11 | B/C/D/F | motorcycle platform | `rec_picturex0611_hydraulic_jack1_fork_motorcycle_platform_20260714` | L150-L164, L230-L358 | broad platform and tie-down tabs |
