# pictureX_0611_Hole_punch — modular spec (v1 refresh 2026-07-14)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Hole_punch` |
| template path | `agent/templates/pictureX_0611_Hole_punch.py` |
| test path (optional) | — |
| stage | `P3_P4_REFRESH` |
| status | `sweep-pipeline PASS 2026-07-14` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star downstream records in `pictureX/0611/Hole_punch` including 20260714 supplement anchors |
| source_index_policy | only adopted module sources are indexed below |

已读 11 个 rating=5 source records: `rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d`, `rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff`, `rec_picturex0611_hole_punch_fork_handheld_c_loop_20260713`, `rec_picturex0611_hole_punch_fork_vertical_plunger_20260713`, `rec_picturex0611_hole_punch_fork_lever_carriage_20260713`, `rec_picturex0611_hole_punch_fork_desktop_n3_20260713`, `rec_picturex0611_hole_punch_fork_binder_n4_20260713`, `rec_picturex0611_hole_punch_fork_adjustable_paper_guide_20260713`, `rec_picturex0611_hole_punch_fork_heavy_duty_two_post_20260714`, `rec_picturex0611_hole_punch_fork_slot_head_20260714`, `rec_picturex0611_hole_punch_fork_long_reach_throat_20260714`.

## 核心身份

机械纸张打孔器：必须有承纸/喉口/底座或 C 形框架、与孔位对齐的 punch pin / slot blade、die opening、手动 lever / plunger / carriage 行程。成熟域是桌面办公两孔/三孔/四孔打孔器、长喉单孔打孔器、手持 C-loop 打孔器、重型双立柱办公打孔器。不得漂移成 stapler、paper cutter、press brake、binder clip、电动钻床或无 die hole 的普通夹具。

## 槽位 + 候选模块表

### Slot A：`frame_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `desktop_origin` | origin_anchor | `rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d` | L247-L364, L437-L454 | eligible | tapered cast base + head housing + die pedestal + single carriage; office desktop slab primary form |
| `framed_desktop` | origin_anchor | `rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff` | L50-L165, L226-L257 | eligible | wide base + rear cast side frame + pivot axle + two guided punch carriages |
| `handheld_c_loop` | forked_anchor | `rec_picturex0611_hole_punch_fork_handheld_c_loop_20260713` | L32-L98, L130-L240, L360-L395 | eligible if `n_holes=1` | compact C-loop jaw / spring frame, small throat and rear squeeze lever; handheld form |
| `heavy_duty_two_post` | forked_anchor | `rec_picturex0611_hole_punch_fork_heavy_duty_two_post_20260714` | L108-L193, L263-L309 | eligible if `mechanism_style=lever_carriage` | two tall guide posts, flanges, top press bridge, guide sleeves, vertical punch carriages; new 20260714 anchor |

Degrade/compat note: no degrade; 4 distinct source-backed frame/body forms. `heavy_duty_two_post` is gated to lever carriage because its source identity is the two-post guided press.

### Slot B：`mechanism_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `pivot_lever` | origin_anchor | `rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d` + `rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff` | rec001 L398-L454 / rec002 L181-L257 | eligible | REVOLUTE press handle driving punch pin/carriage down into dies |
| `vertical_plunger` | forked_anchor | `rec_picturex0611_hole_punch_fork_vertical_plunger_20260713` | L327-L355, L405-L465 | eligible if desktop and `n_holes=1` | PRISMATIC vertical plunger bar on guide columns; direct downstroke |
| `lever_carriage` | forked_anchor | `rec_picturex0611_hole_punch_fork_lever_carriage_20260713` | L107-L181, L190-L330 | eligible if desktop; required for `heavy_duty_two_post` | REVOLUTE lever + guided PRISMATIC carriage / carriage bar, punch pins mounted to carriage |

Degrade note: 3 structurally distinct actuation mechanisms, all source-backed.

### Slot C：`punch_head_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `round_pin_head` | origin_anchor | origins + `desktop_n3` / `binder_n4` | rec002 L75-L86, L226-L257; desktop_n3 L81-L92 | Planar Boundary Form | eligible | circular punch pins and annular round dies; repeated as N stations |
| `slot_head` | forked_anchor | `rec_picturex0611_hole_punch_fork_slot_head_20260714` | L72-L80, L134-L176, L454-L467 | Planar Boundary Form | eligible if non-heavy desktop; sampled as single oblong hole station | elongated slot die + stadium/oblong slot punch blade; new 20260714 anchor |

Degrade note: 2 candidates because the 11-source pool contains exactly two punch-head aperture families: round holes and elongated slot holes. `slot_head` is source-backed and visually distinct; no third aperture family appears in-pool.

### Slot D：`throat_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `standard_throat` | origin_anchor | origins | rec001 L35-L109, rec002 L50-L107 | eligible | normal office throat/deck depth, die table close to pivot/head |
| `adjustable_guide` | forked_anchor | `rec_picturex0611_hole_punch_fork_adjustable_paper_guide_20260713` | L207-L247, L372-L410 | eligible desktop | sliding/slotted guide bar, depth fence and ruler/slot details on paper support |
| `long_reach_throat` | forked_anchor | `rec_picturex0611_hole_punch_fork_long_reach_throat_20260714` | L35-L87, L222-L244, L329-L410, L511-L520 | eligible desktop, not handheld | extended throat deck, longer reach scale, depth stop/ruler ticks; new 20260714 anchor |

Degrade note: no degrade; 3 distinct throat/support treatments. `long_reach_throat` is a ⑤ proportion/travel anchor plus visible throat-deck candidate.

### Slot E：`n_holes`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `1` | origin/forked_anchor | rec001 + `vertical_plunger` + `slot_head` + `long_reach_throat` | rec001 L224-L250, L437-L454; vertical L249-L465 | eligible; forced for handheld/plunger/slot | single punch station / single die |
| `2` | origin_anchor | rec002 + `lever_carriage` + `heavy_duty_two_post` | rec002 L226-L257; two_post L263-L309 | eligible desktop | two punch stations with aligned dies |
| `3` | forked_anchor | `rec_picturex0611_hole_punch_fork_desktop_n3_20260713` | L81-L92, L248-L292 | eligible desktop non-slot | three evenly spaced carriages/dies |
| `4` | forked_anchor | `rec_picturex0611_hole_punch_fork_binder_n4_20260713` | L98-L153, L336-L358 | eligible desktop non-slot | four-hole binder punch span with wide base |

Multiplicity note: `n_holes` is the template-level repeated punch station axis; see §8.

### Slot F：`palette_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `painted_blue_steel` | record_only | blue painted office base + chrome pins across origins | rec002 L50-L86 | eligible | blue painted body, steel dies/pins, dark grips |
| `red_office_chrome` | record_only | red/painted companion variants in mature template palette; office material family in sources | source map ⑥ + template palette | eligible | red painted body, chrome/nickel hardware |
| `graphite_black` | record_only | dark rubber/plastic grips and dark guide hardware in all desktop sources | rec002 L269-L323; lever_carriage L330-L377 | eligible | graphite body with black grip/detail |
| `green_office` | record_only | office painted-metal colorway companion | source map ⑥ + mature template palette | eligible | green painted body, steel pins |
| `brushed_nickel` | record_only | handheld and metal-frame sources | handheld L186-L240, L251-L269 | eligible | nickel/chrome hand punch finish |

Palette is sampled per seed as `palette_style`; it is not counted as structural candidate but is included in `slot_choices` for audit visibility.

## 槽位图（slot graph）

pattern: `mixed`

`frame_style/body` is the root grounded part. `mechanism_style` attaches to the root by either a REVOLUTE lever pivot or PRISMATIC plunger/carriage guide. `punch_head_style` derives the punch pin/die aperture geometry inside the selected mechanism and body. `n_holes` is a multiplicity axis consumed by both body dies and moving pins/carriages. `throat_style` is a body/support layer emitted as root visuals and guide/depth-stop details. `palette_style` drives material selection.

Interfaces:
- body → lever: captured revolute pivot at rear hinge block / C-loop pivot post, axis +Y, range `[0, stroke_upper]`; source uses hinge barrel / pivot axle.
- body → plunger: vertical guide column and PRISMATIC slide axis -Z, range `[0, slide_travel]`.
- body → carriage: PRISMATIC guide post / carriage bore axis -Z; lever carriage additionally has REVOLUTE lever cam above it.
- punch stations: shared `pin_ys` and `pin_x` align moving punch pins or slot blade to die openings; die clearance is derived from pin gauge.
- throat/support: fixed body visuals, no separate fixed parts unless source record had guide parts; template folds guide/depth-stop marks into root visuals for robust support.

## 每槽位 Module Emits / Interfaces

### Slot A / frame modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` with base shell, die table, rear hinge/guide mount; handheld emits lower jaw/C-loop bridge visuals | rec001 L247-L364; rec002 L50-L165; handheld L130-L240; two_post L108-L193 |
| internal joints | none in frame itself; it publishes mount surfaces for mechanism joints | source records above |
| upstream interface | root, grounded | template |
| downstream interface | pivot block / guide column / two-post bridge mount and die station plane | source + template single-sourced resolved config |

### Slot B / mechanism modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pressing_lever`, `plunger_head`, `plunger_carriage`, `punch_pin_i` depending on mechanism | rec001 L398-L454; vertical L405-L465; lever_carriage L190-L330 |
| internal joints | `lever_pivot` REVOLUTE; `plunger_slide` PRISMATIC; `carriage_guide` PRISMATIC plus lever pivot | same |
| upstream interface | body pivot / guide mount | same |
| downstream interface | punch station local mounts at shared `pin_ys` | same |

### Slot C / punch head
| emits | 描述 | 来源 |
|---|---|---|
| parts | round pin visuals or oblong slot blade on `punch_pin_0`; die ring / slot die visuals on body | round: rec002 L75-L86; slot: slot_head L134-L176, L454-L467 |
| internal joints | no extra joints; geometry attaches to moving pin or body visual | same |
| upstream interface | consumes mechanism pin/carriage mount | same |
| downstream interface | die aperture / paper contact plane | same |

### Slot D / throat
| emits | 描述 | 来源 |
|---|---|---|
| parts | standard deck, adjustable guide/depth stop visuals, or long-reach throat deck/ruler/depth stop | adjustable L207-L247; long_reach L329-L410 |
| internal joints | template degrades guide sliders to body visuals for support; source has PRISMATIC guide parts | source records; compatibility downgrade documented |
| upstream interface | body top/paper deck | source |
| downstream interface | paper depth plane and die station clearance | source |

### Slot E / n_holes
| emits | 描述 | 来源 |
|---|---|---|
| parts | loop-emitted `punch_pin_i` and body die visuals | rec001, rec002, desktop_n3, binder_n4 |
| internal joints | one FIXED pin-to-lever/carriage per station; carriage variants have one PRISMATIC guide relation | same |
| upstream interface | mechanism pin mount / carriage body | same |
| downstream interface | die aperture at same station index | same |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_style` | enum | desktop_origin / framed_desktop / handheld_c_loop / heavy_duty_two_post | desktop_origin | choice | sampled then gated | §4A |
| `mechanism_style` | enum | pivot_lever / vertical_plunger / lever_carriage | pivot_lever | conditional | handheld→pivot; heavy_duty_two_post→lever_carriage | §4B |
| `punch_head_style` | enum | round_pin_head / slot_head | round_pin_head | conditional | heavy_duty_two_post→round; slot_head forces non-heavy desktop single station | §4C |
| `throat_style` | enum | standard_throat / adjustable_guide / long_reach_throat | standard_throat | conditional | long_reach desktop only; handheld→standard | §4D |
| `n_holes` | int enum | 1 / 2 / 3 / 4 | 2 | conditional | handheld/plunger/slot→1 source station; lever_carriage desktop≥2 except slot adapter | §4E / §8 |
| `palette_style` | enum | painted_blue_steel / red_office_chrome / graphite_black / green_office / brushed_nickel | painted_blue_steel | choice | sampled per seed and mapped to mature hole-punch material presets | §4F |
| `reach_scale` | float | [0.92,1.34] | 1.0 | conditional | long_reach lower bound 1.20; mature base clamps to safe range | long_reach L35-L87 |
| `body_height_scale` | float | [0.92,1.15] | 1.0 | independent | clamp in `resolve_config` via base template | origins |
| `hole_pitch_scale` | float | [0.90,1.14] | 1.0 | conditional | ignored for N=1; otherwise station spacing | desktop_n3/binder_n4 |
| `handle_len_scale` | float | [0.88,1.23] | 1.0 | independent | lever length varies without moving pivot/die relation | origins |
| `pin_radius_scale` | float | [0.90,1.15] | 1.0 | equation | die bore derives from pin radius in mature base config | origins |
| compatibility | constraint | — | — | inequality/conditional | illegal tuples projected: handheld excludes plunger/carriage/long_reach/slot; plunger forces N=1; slot uses single oblong station; heavy-duty uses carriage | source map + §9 |

## 编译预算 / compile budget

Target ≤ 18 s / seed. The template reuses the mature `hole_punch` implementation (Box/Cylinder plus bounded tube/mesh helpers) and adds only a few low-tessellation body/pin visuals for the 20260714 anchors. No heavy booleans in the wrapper. Sweep watchdog: `--compile-timeout 120` with BLAS/OMP thread caps. If any seed exceeds 20 s, reduce decorative Cylinder segment counts in the base template before adding new geometry.

## Multiplicity / Copy Logic

- `count_param`: `n_holes`.
- `N_range`: `[1,4]`, source-backed samples 1 (rec001, vertical_plunger, slot_head, long_reach), 2 (rec002, lever_carriage, heavy_duty_two_post), 3 (`desktop_n3`), 4 (`binder_n4`).
- sampling domain: weighted small office range; N=1 common for handheld/plunger/slot/long-reach, N=2 common for desktop, N=3/4 rarer binder/desktop variants.
- copied object / naming / placement / joint policy: body emits die visuals at `pin_ys`; moving mechanism emits `punch_pin_i` / carriage stations at the same `pin_ys`; each pin has a FIXED mount to lever/plunger/carriage; carriage mechanisms additionally use PRISMATIC guide.
- gating: handheld, vertical plunger and slot-head forms collapse to one source station; heavy-duty two-post samples 2/3 round stations only because heavy-duty×slot is unsourced.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame/body skeletons: desktop_origin, framed_desktop, handheld_c_loop, heavy_duty_two_post; guide/depth-stop source has additional guide parts but template degrades to supported body visuals. All frame choices source-backed. |
| └ multiplicity | 同构件 ×N | 有 | `n_holes` 1/2/3/4, source-backed by rec001/rec002/desktop_n3/binder_n4; see §8. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE lever (+Y), PRISMATIC vertical plunger (-Z), REVOLUTE+PRISMATIC lever carriage. PRISMATIC guide sliders in source are downgraded to fixed body visuals for support, not declared as active template joints. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | `frame_style` desktop/framed/handheld/heavy-duty (Volumetric Envelope / Macro Surface Construction) and `punch_head_style` round vs slot (Planar Boundary Form). New 20260714 slot_head is registered in `slot_choices`. |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | die rings, screw heads, guide ruler ticks, guide slots, depth-stop marks, post flanges, bridge ribs; host body/pin visuals, source-backed record_only + source map §6. |
| ⑤ 尺寸/行程 | 连续改尺寸/比例/行程 | 有 | reach_scale [0.92,1.34], body_height_scale [0.92,1.15], hole_pitch_scale [0.90,1.14], handle_len_scale [0.88,1.23], pin_radius_scale [0.90,1.15]. Motion envelopes: lever REVOLUTE +Y `[0, stroke_upper]`; plunger/carriage PRISMATIC -Z `[0, slide_travel]`; tests use targeted press pose + sampled collision via base `run_hole_punch_tests`. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `palette_style` 5: painted_blue_steel, red_office_chrome, graphite_black, green_office, brushed_nickel. Material classes cover painted metal/plastic/rubber/steel/nickel ≥ ceil(0.5×5). Sampled per seed. |

收尾自检: seed 0-35 should visibly realize heavy-duty two-post, slot-head, long-reach throat, handheld C-loop, vertical plunger, lever carriage, N=1/2/3/4, and multiple palettes.

## 采样与覆盖审计

总组合数（before gating）: 4 frame × 3 mechanism × 2 punch_head × 3 throat × 4 N × 5 palettes = 1440. After source compatibility gates the practical structural space is ~150+ visible combinations, with `palette_style` multiplying colorways.

seed_domain_policy: procedural_first

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` uses `random.Random(seed)` for all seeds including 0. It samples `frame_style`, gates mechanism/head/throat/N by source-backed compatibility, samples continuous scales, then samples `palette_style`. No regression overrides. The wrapper adapts the mature `hole_punch` stable geometry and adds host-supported visuals for `heavy_duty_two_post`, `slot_head`, and `long_reach_throat`.

Topology target: report-only 1000-seed audit should show all 4 frame styles, 3 mechanisms, both punch heads, 3 throat styles, N 1-4, and 5 palettes. The final P4 gate is 0-35 + corner stage pass with axis visibility confirmed.

Controlled local parameterization: `reach_scale` is conditionally raised for `long_reach_throat`; `pin_radius_scale` derives die clearance; `hole_pitch_scale` only applies when N>1. All compatibility and clamps are resolved in `resolve_config`, not left to builder failure.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | frame → mechanism/head/throat/N gates → scales → palette | `slot_choices_for_seed` matches `model.meta["slot_choices"]` |
| compatibility matrix | handheld→pivot/round/standard/N=1; plunger→N=1; slot_head→non-heavy desktop single oblong station; heavy_duty→lever_carriage+round; long_reach desktop only | no floating post/slot/throat visuals; no illegal moving joint combos |
| controlled local variation | reach/body height/pitch/handle/pin gauge clamped; die derives from pin gauge | pin-die alignment, lever/plunger press pose, throat visuals remain supported |
| regression overrides | none | procedural seed domain only |
| random sweep | canonical P4 command 0-35 + corner stage; optional 0-999 maturity audit | contract failures; axis_realization; failed_corner_seeds |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| frame_style | 4 | yes | yes | includes 20260714 heavy_duty_two_post |
| mechanism_style | 3 | yes | yes | REVOLUTE / PRISMATIC / compound |
| punch_head_style | 2 | yes | no | documented degrade: only round and slot heads in 11-source pool |
| throat_style | 3 | yes | yes | includes long_reach_throat |
| n_holes | 4 | yes | yes | multiplicity axis |
| palette_style | 5 | yes | yes | color/material audit, not structural |

## Validator

- `__modular__ = True`.
- `config_from_seed` uses deterministic procedural sampling; seed 0 is ordinary.
- `slot_choices_for_seed` returns `frame_style`, `mechanism_style`, `punch_head_style`, `throat_style`, `n_holes`, `palette_style`.
- `build_picturex_0611_hole_punch` preserves API aliases and accepts both wrapper config and mature `HolePunchConfig`.
- compatibility matrix prevents unsupported handheld/plunger/slot/long-reach/heavy-duty combinations.
- no separate FIXED decorative parts in wrapper; new post/slot/throat details are supported body/pin visuals.
- mature base tests verify pin/die alignment, press stroke, sampled pose collision, joint origin proximity.
- every non-FIXED joint is inherited from mature `hole_punch` and covered by `run_hole_punch_tests`.
- final acceptance: thread-capped `sweep-pipeline pictureX_0611_Hole_punch --max-workers 16 --compile-timeout 120` verdict pass and pass_rate ≥0.90.

## Reject cases

- Looks like a stapler, clamp, cutter, or drill press without die holes.
- No visible punch pin / slot blade aligned to die.
- Slot-head sampled but no elongated slot die/blade is visible.
- Heavy-duty sampled but no two-post/press-bridge frame is visible.
- Long-reach sampled but no extended throat/depth/ruler detail is visible.
- Monochrome outputs across seeds because `palette_style` is not driving material selection.
- Any floating guide/depth/post visual or unsupported internal visual island.

## Compatibility / Degrade Notes

- `punch_head_style` has 2 candidates by source limitation: round pin and oblong slot only. This is accepted because both are source-backed and structurally distinct Planar Boundary forms.
- Source adjustable guide records contain PRISMATIC guide parts; wrapper degrades them to supported body visuals because the mature stable template's active motion contract focuses on the punch mechanism. This avoids adding fragile guide-slider joints while keeping the visual/source evidence.
- `slot_head` is sampled with a stable non-heavy desktop single-station mechanism plus additional oblong blade/die visuals. It preserves the source aperture identity without inventing a separate unsupported slot-carriage topology.
- `heavy_duty_two_post` is gated to lever carriage; other mechanisms on two-post frame are unsourced and not sampled.

## Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | frame/mechanism/head/throat/N | desktop_origin / pivot_lever / round / standard / 1 | `rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d` | L35-L216, L247-L364, L398-L454 | single-hole desktop source |
| S2 | frame/mechanism/N/palette | framed_desktop / pivot_lever / round / 2 | `rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff` | L50-L165, L181-L257, L269-L327 | two-hole framed desktop source |
| S3 | frame | handheld_c_loop | `rec_picturex0611_hole_punch_fork_handheld_c_loop_20260713` | L32-L98, L130-L240, L278-L395 | compact C-loop frame |
| S4 | mechanism | vertical_plunger | `rec_picturex0611_hole_punch_fork_vertical_plunger_20260713` | L327-L355, L405-L465 | PRISMATIC plunger |
| S5 | mechanism/N | lever_carriage / 2 | `rec_picturex0611_hole_punch_fork_lever_carriage_20260713` | L107-L181, L190-L330 | lever + carriage compound |
| S6 | N | 3 | `rec_picturex0611_hole_punch_fork_desktop_n3_20260713` | L81-L92, L248-L292 | three-hole desktop |
| S7 | N | 4 | `rec_picturex0611_hole_punch_fork_binder_n4_20260713` | L98-L153, L336-L358 | four-hole binder punch |
| S8 | throat | adjustable_guide | `rec_picturex0611_hole_punch_fork_adjustable_paper_guide_20260713` | L207-L247, L372-L410 | guide/depth-stop visual source |
| S9 | frame | heavy_duty_two_post | `rec_picturex0611_hole_punch_fork_heavy_duty_two_post_20260714` | L108-L193, L263-L309 | new two-post anchor |
| S10 | head | slot_head | `rec_picturex0611_hole_punch_fork_slot_head_20260714` | L72-L80, L134-L176, L454-L467 | new oblong slot punch anchor |
| S11 | throat | long_reach_throat | `rec_picturex0611_hole_punch_fork_long_reach_throat_20260714` | L35-L87, L222-L244, L329-L410, L511-L520 | new long throat anchor |
