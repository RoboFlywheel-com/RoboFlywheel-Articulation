# pictureX_0611_hydraulic_jack2

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_hydraulic_jack2` |
| template path | `agent/templates/pictureX_0611_hydraulic_jack2.py` |
| source map | `picture_expansion/template_source_maps/0611__hydraulic_jack2.md` |
| stage | `TEMPLATE_COMPLETE` |
| status | `sweep-pipeline PASS` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| rating_filter | all downstream `rating=5` samples for inherited slug `picturex_0611__hydraulic_jack2__001__png` |
| source_index_policy | only adopted 5-star source records and source-map accepted anchors are indexed below |

Accepted source records:
- `rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0`
- `rec_picturex0611_hydraulic_jack2_fork_bottle_jack_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_floor_trolley_jack_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_toe_jack_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_double_stage_ram_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_screw_extension_saddle_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_transmission_cradle_20260713`
- `rec_picturex0611_hydraulic_jack2_fork_air_over_hydraulic_20260714`
- `rec_picturex0611_hydraulic_jack2_fork_safety_lock_bar_20260714`
- `rec_picturex0611_hydraulic_jack2_fork_low_profile_floor_20260714`
- `rec_picturex0611_hydraulic_jack2_fork_motorcycle_platform_20260714`

Excluded source:
- `rec_picturex0611_hydraulic_jack2_fork_long_reach_floor_jack_20260713`: source map marks retry1/retry2 exit 143 with no committed record directory, so it is not part of this template.

## 核心身份

`pictureX_0611_hydraulic_jack2` is a hydraulic lifting/service jack family. Every accepted instance keeps a stable base or chassis, a hydraulic cylinder/ram, a pump handle or pump-actuated control, a load contact interface, and at least one non-fixed articulation. The family includes upright bottle jacks, wheeled floor/trolley jacks, low-profile floor jacks, toe jacks, nested ram variants, service load cradles, air-over-hydraulic assist, safety lock bars, and motorcycle platform adapters.

Reject drift toward:
- scissor screw jack or purely mechanical screw jack
- shop crane or boom hoist
- lift table without visible jack hardware
- generic linear actuator or jack stand without pump/ram/load-contact identity

## 槽位 + 候选模块表
| slot | candidates | evidence | compatibility / sampling |
|---|---|---|---|
| `body_family` | `origin_floor`, `floor_trolley`, `low_profile_floor`, `bottle_jack`, `toe_jack` | origin floor jack build lines 48-467; floor trolley build lines 48-476; low-profile 20260714 source build lines 48-480; bottle build lines 31-291; toe build lines 48-479 | primary chassis/root topology; `wheel_count` derives from body |
| `ram_mechanism` | `single_stage_ram`, `double_stage_ram`, `screw_extension_saddle` | origin/floor cylinder and piston lines 147-177; double-stage source stage lines 179-221 and joints 432-454; screw extension source lines 246-333 and 512-528 | toe load blocks screw extension; bottle may use all three ram choices |
| `load_interface` | `saddle_cup`, `toe_pickup`, `transmission_cradle`, `motorcycle_platform` | origin saddle lines 225-238; toe bracket lines 226-250; transmission cradle lines 227-285 and tilt joint lines 455-462; motorcycle platform 20260714 deck/rubber/tie-down region around lines 237-280 | bottle uses saddle/cradle; toe uses toe/saddle; floor-like bodies can use all four |
| `pump_mechanism` | `manual_pump`, `air_over_hydraulic` | manual pump handle lines 246-304 and pump articulation lines 417-433 in floor/origin; air-over-hydraulic 20260714 source air assist/regulator/hose lines 321-437 | air assist is floor-body only; bottle/toe degrade to manual pump |
| `safety_mechanism` | `open_lift`, `safety_lock_bar` | `open_lift` is source absence/default; safety lock bar 20260714 source lock bar/pawl region lines 339-434 and pivots lines 568-586 | safety lock bar is floor-body only; bottle/toe degrade to `open_lift` |
| `palette_style` | `shop_blue_black`, `service_red_black`, `zinc_grey_black`, `yellow_safety_steel`, `matte_black_chrome` | record-only painted steel/chrome/rubber/brass finishes across all 11 samples | per-seed material palette; does not change geometry |
| `wheel_count` | `0`, `2`, `4` | bottle has fixed base; toe source has compact toe support; floor/trolley/low-profile sources have paired/symmetric wheels | derived: bottle 0, toe 2, floor-like 4 |

## 槽位图

Mixed pattern with a single `chassis` root:

`body_family` creates the root envelope. Floor-like bodies create a wheeled low chassis, lift rails, hydraulic cylinder, pivoting `lift_arm`, wheels, and rear pump deck. `bottle_jack` creates a compact plate, upright cylinder, vertical ram, and side pump barrel. `toe_jack` uses the floor-family skeleton with shorter base, low toe foot, and two wheels.

`ram_mechanism` attaches to the chassis and pushes the lift arm or upright load head. `single_stage_ram` emits one prismatic `lifting_ram`; `double_stage_ram` emits nested `piston_stage_0` and `piston_stage_1`; `screw_extension_saddle` adds source-backed threaded saddle visuals on the load host while keeping hydraulic ram motion.

`load_interface` is host-conformal visual geometry on the lift arm or vertical ram, not a fixed decorative child. It changes the load-contact silhouette while preserving the same hydraulic motion chain.

`pump_mechanism` emits the moving pump handle in all cases; `air_over_hydraulic` adds regulator, air cylinder, hose, and fitting visuals on the chassis for floor-like bodies.

`safety_mechanism` emits a visible lock bar, ratchet teeth, and pawl on floor-like bodies. The lock hardware is represented as host visuals so it does not create small fixed decoration parts.

`palette_style` is global material assignment and appears in `slot_choices_for_seed` for audit.

## 每槽位 Module Emits / Interfaces
| module | emits | interfaces | source / note |
|---|---|---|---|
| floor-like body | `chassis`, `lift_arm`, wheels, lift rails, cylinder body, pump deck | `lift_arm_hinge` revolute; wheel spin revolutes; ram child slots on chassis | origin/floor/low-profile/toe sources |
| bottle body | `chassis`, `lifting_ram`, side pump barrel | `ram_slide` prismatic; pump handle revolute beside upright cylinder | bottle source lines 31-291 |
| single-stage ram | `lifting_ram` chrome cylinder and ram head | prismatic `ram_slide` from chassis | origin/floor/bottle/toe records |
| double-stage ram | `piston_stage_0`, `piston_stage_1` | nested prismatic `stage0_slide` and `stage1_slide` | double-stage record lines 179-221, 432-454 |
| screw extension saddle | threaded post, grooves, rotating load pad visuals | host-attached to load parent; hydraulic ram remains moving mechanism | screw-extension record lines 246-333 |
| saddle/toe/cradle/platform load heads | saddle cup, low toe pickup, transmission cradle ears/ribs, motorcycle platform deck/rubber/tie-down tabs | host-conformal visuals on lift arm or ram; no isolated fixed child | toe, transmission, motorcycle 20260714 sources |
| manual pump | `pump_handle` with eye, neck, handle tube, rubber grip | revolute `pump_handle_hinge` | all manual jack sources |
| air-over-hydraulic assist | air cylinder, mount bracket, fitting, routed hose, regulator knob | chassis-host visuals; pump handle remains mechanical control | 20260714 air source lines 321-437 |
| safety lock bar | lock bar, pivot bracket, ratchet teeth, pawl/tooth | chassis/lift-arm host visuals; no fixed decoration part | 20260714 safety source lines 339-434 |

## 参数范围汇总
| param | range / candidates | rationale |
|---|---|---|
| `body_family` | five listed candidates | covers all accepted body-form anchors, including 20260714 low-profile floor |
| `ram_mechanism` | three listed candidates | single, double, and screw-extension hydraulic variants |
| `load_interface` | four listed candidates | saddle, toe, transmission cradle, and 20260714 motorcycle platform |
| `pump_mechanism` | manual / air-over-hydraulic | covers new air assist while keeping baseline pump |
| `safety_mechanism` | open / safety lock bar | covers new lock-bar anchor |
| `palette_style` | five named palettes | per-seed material diversity |
| `wheel_count` | 0, 2, 4 | derived from body family, not independently sampled |
| `width_scale` | 0.90-1.14 generated, clamped 0.86-1.20 | source proportion variance |
| `length_scale` | 0.88-1.18 generated, clamped 0.84-1.22 | floor/low/trolley length variance |
| `height_scale` | 0.90-1.16 generated, clamped 0.86-1.18 | upright/bottle/ram height variance |
| `travel_scale` | 0.82-1.18 generated, clamped 0.78-1.22 | hydraulic travel variance |

Compatibility/degrade policy:
- `bottle_jack`: load interface is resolved to `saddle_cup` or `transmission_cradle`; pump becomes `manual_pump`; safety becomes `open_lift`; `wheel_count=0`.
- `toe_jack`: load interface is resolved to `toe_pickup` or `saddle_cup`; pump becomes `manual_pump`; safety becomes `open_lift`; `wheel_count=2`.
- `air_over_hydraulic` and `safety_lock_bar` are only retained on `origin_floor`, `floor_trolley`, and `low_profile_floor`.
- Incompatible user-provided configs are resolved deterministically rather than throwing, preserving API stability.

## Compile Budget
| item | value |
|---|---|
| target per-seed compile | under 2 seconds |
| canonical timeout | 120 seconds |
| canonical workers | 16 |
| latest observed pipeline wall time | about 2-3 seconds for 48 seeds on this workspace |
| implementation approach | primitives only; no external mesh or CadQuery dependency |

Canonical command:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 uv run articraft template sweep-pipeline pictureX_0611_hydraulic_jack2 --max-workers 16 --compile-timeout 120
```

## Multiplicity / Copy Logic
| N axis | values | copied object / policy |
|---|---|---|
| `wheel_count` | 0, 2, 4 | derived from body; wheels named `wheel_i`, symmetric placement, each gets revolute spin |
| `ram_stage_count` | 1 or 2 | `single_stage_ram` emits one ram; `double_stage_ram` emits nested stage0/stage1 prismatic chain |
| `tie_down_tab_count` | fixed 4 inside `motorcycle_platform` | source-backed platform detail, not a registered independent N axis |
| `ratchet_tooth_count` | fixed 6 inside `safety_lock_bar` | source-backed safety detail, not a registered independent N axis |
| `screw_thread_groove_count` | fixed 5 inside `screw_extension_saddle` | source-backed saddle detail, not a registered independent N axis |

## 6 轴审计
| axis | treatment | realized values / motion plan |
|---|---|---|
| 1 skeleton / structural topology | source-backed | upright bottle base, wheeled floor/trolley chassis, shallow low-profile floor chassis, compact toe jack chassis; `wheel_count` covers 0/2/4 |
| 2 joint / mechanism type | source-backed | prismatic ram, nested two-stage prismatic ram, revolute lift arm, revolute pump handle, revolute wheels; screw-extension saddle represented as threaded host load contact |
| 3 primary form family | source-backed | origin floor, trolley floor, 20260714 low-profile floor, bottle jack, toe jack, transmission cradle load head, 20260714 motorcycle platform |
| 4 surface decoration / details | record-only and host-conformal | collars, saddle pads, threaded grooves, cradle ribs, rubber pads, tie-down tabs, air hose/regulator, safety ratchet teeth |
| 5 proportion / size / travel | sampled numeric | width/length/height/travel scales plus body-specific chassis dimensions; motion limits include `lift_arm_hinge[-0.45,0.34]`, `pump_handle_hinge[-0.34,0.42]`, `ram_slide[0,0.105*travel]`, two-stage slides `[0,0.070*travel]` and `[0,0.060*travel]` |
| 6 material / palette / finish | per-seed palette | shop blue/black, service red/black, zinc grey/black, yellow safety/steel, matte black/chrome; all include chrome/steel ram and dark rubber components |

Motion QC plan:
- Sweep validates current pose overlap and articulation-origin proximity.
- Template tests allow only source-justified captured overlaps: ram in cylinder mouth, lift arm in rails, wheels on axles, and pump handle in socket.
- Non-moving visual details are host visuals on `chassis`, `lift_arm`, or `lifting_ram` to satisfy the no-fixed-decoration rule.

## 采样与覆盖审计
| item | value |
|---|---|
| sampler | deterministic per-seed slot cycling plus seeded continuous scales |
| raw registered slot space | 5 body x 3 ram x 4 load x 2 pump x 2 safety x 5 palette x derived wheel count |
| compatibility | resolver gates unsupported combinations before build |
| regression override | none |
| expected sweep visibility | every registered slot candidate appears in 0-35 plus corner stage |

Latest accepted sweep used the canonical thread-capped command above. Final report should show:
- `body_family`: all five candidates covered.
- `ram_mechanism`: single, double, screw-extension covered.
- `load_interface`: saddle, toe, transmission cradle, motorcycle platform covered.
- `pump_mechanism`: manual and air-over-hydraulic covered.
- `safety_mechanism`: open and safety lock bar covered.
- `palette_style`: all five palettes covered.
- `wheel_count`: 0, 2, and 4 covered.

## Validator / Reject Cases
Reject or resolve away:
- config tries `air_over_hydraulic` on bottle or toe jack
- config tries `safety_lock_bar` on bottle or toe jack
- config tries `motorcycle_platform` or `toe_pickup` on bottle jack
- config tries `transmission_cradle` or `motorcycle_platform` on toe jack
- config omits all moving hydraulic mechanisms
- generated model has isolated parts, unsupported overlaps, or articulation origins far from geometry

## Neighbor Boundaries
| neighbor | boundary |
|---|---|
| scissor screw jack | uses crossed screw linkage; no hydraulic cylinder/pump identity |
| engine hoist / crane | boom and hook dominate instead of saddle/cradle jack interface |
| hydraulic lift table | platform-table identity without service jack pump/ram chassis |
| transmission stand | may share cradle, but this category keeps jack/trolley hydraulic lift identity |
| jack stand | passive support only; no hydraulic ram/pump |

## 审核记录
| 项 | 值 |
|---|---|
| implementation | `agent/templates/pictureX_0611_hydraulic_jack2.py` self-contained modular template |
| exports | `__modular__`, config dataclasses, `config_from_seed`, `resolve_config`, builders, slot choice helpers, test functions |
| new anchors | `air_over_hydraulic`, `safety_lock_bar`, `low_profile_floor`, `motorcycle_platform` included |
| open items | none |

## Module Source Index
| record | adopted evidence |
|---|---|
| origin floor jack | chassis/cylinder/piston/lift arm/saddle/pump/wheels/articulations: build lines 48-467 |
| bottle jack | compact base, upright cylinder, vertical ram, saddle, pump handle: build lines 31-291 |
| floor trolley jack | wheeled base, lift arm, saddle, pump handle: build lines 48-476 |
| toe jack | low toe foot, toe pickup bracket, ram, pump handle: build lines 48-479; toe bracket lines 226-250 |
| double-stage ram | nested ram stages and prismatic chain: lines 179-221, 432-454 |
| screw-extension saddle | threaded post/load pad and articulation region: lines 246-333, 512-528 |
| transmission cradle | cradle plate/ears/ribs and tilt joint reference: lines 227-285, 455-462 |
| air-over-hydraulic | air assist cylinder, regulator, hose, fitting: lines 321-437 |
| safety lock bar | lock bar, pawl, ratchet/strike bracket, pivots: lines 339-434, 568-586 |
| low-profile floor | shallow floor chassis and lower lift stance: build lines 48-480 |
| motorcycle platform | broad platform deck, rubber pads, tie-down tabs: around lines 237-280 |
