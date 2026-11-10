# Modular Spec — Bench / Wood Swing

## 元信息
| 项 | 值 |
|---|---|
| slug | `wood_swing` |
| template path | `agent/templates/Bench_Wood_Swing.py` |
| stage | `SPEC_ONLY_REWRITE` |
| status | `pending_review` |
| __modular__ | `True` |
| pattern | `mixed`：固定 bench-swing frame + 单一 fore/aft pendulum；结构 slot 为 `support_frame` x `suspension` x `bench_body` x `canopy`，另有板条/链节/绳段数量轴 |

## 重写结论
上一版 spec 把 `four_post_pergola + daybed_platform` 和 `single_hanging_chair` 当成同等主候选，导致 seed 漂到四柱吊床/单椅。此版收窄小类身份：

- 主体必须读作 **garden/porch bench swing**：固定支架 + 顶横梁/吊点 + 长椅座面 + 靠背 + 两侧扶手/端架 + 前后摆动。
- `pergola_garden_swing_daybed` 和 `single_hanging_chair` 是邻界/负例参考，不能作为随机 seed 的主形体候选。
- 允许链/绳/刚臂/杆吊挂，但它们必须服务于 **bench**，不能让悬挂件穿过座面或变成游乐场儿童荡板。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| upstream shard | `articraft_data/data/index/subcat/Bench__Wood_Swing.jsonl` |
| read_count | 12（5 parents + 7 variants） |
| accepted_core_sources | 7（4 bench parents + arch/rope/log-chain bench variants） |
| boundary_sources | 5（pergola daybed / bad chain bench / chain daybed / single chair / arched rope boundary） |

### Accepted Core Sources
| source_id | record_id | 采用内容 | 关键行号 |
|---|---|---|---|
| P1-log-glider | `rec_a-frame-log-lawn-glider-swing-round-log-a-frame-_20260611_160845_772176_76ea42fb` | round-log A-frame, pitched roof, two facing slatted seats, center table, log swing arms | A-frame `model.py:96-118`; roof `119-143`; seats/armrests `146-242`; swing arms + mimic `293-338`; glider platform/seats/table `340-432`; identity tests `670-700`, motion `733-770` |
| P2-metal-bench | `rec_metal-a-frame-swing-bench-cad-style-tubular-stee_20260611_160923_294907_5faa70db` | tubular A-frame, top crossbar with clevis lugs, rigid tubular arms, slatted bench, curved rolltop back, cup-holder armrests | A-frame `75-126`; arm helper `128-177`; crossbar/lugs `192-217`; bench/armrests/back `231-313`; swing driver+mimic `314-368`; slat tests `500-518`; motion tests `558-600` |
| P3-sheltered-bench | `rec_model-a-garden-swing-bench-sheltered-by-a-pitche_20260610_085418_407195_71fd0d8b` | slatted A-frame end walls, pitched roof, hanger bar, single rigid bench pendulum with rods | frame/roof/hanger `57-193`; bench body `196-286`; revolute `287-299`; bench tests `392-397`; motion tests `434-483` |
| P4-canopy-bench | `rec_outdoor-wooden-canopy-swing-chair-dark-stained-h_20260611_160902_717126_09703016` | square timber A-frame, fabric awning, wooden swing arms, slatted bench with armrests | scalloped awning helper `77-110`; A-frame/beam `121-166`; arm helper `247-273`; bench `280-350`; driver+mimic `352-381`; frame/bench tests `467-523`; motion tests `554-596` |
| V-arch-bench | `rec_wood_swing_var_archframe` | two-upright frame + top beam, still bench body and rigid arms | upright helper `78-107`; arm helper `109-158`; frame/beam `160-198`; bench `212-294`; swing driver+mimic `295-349`; bench tests `503-518`; motion tests `558-600` |
| V-rope-bench | `rec_wood_swing_var_ropebench` | four rope segments with mimic pendulum, still slatted bench under pitched shelter | rope helper `75-88`; frame/hanger `91-215`; rope segment joints `216-265`; bench start `266-300`; rope/bench tests `503-523` |
| V-log-chain | `rec_wood_swing_var_logchain` | source for oval chain-link vocabulary only; do not inherit facing-glider body as normal sampling | chain mesh `254-300`; frame/roof `300-352`; chain parts + mimic `353-396`; glider platform/seats/table `402-490`; chain and seat tests `718-800` |

### Boundary / Do Not Promote To Main Sampling
| source_id | record_id | reason |
|---|---|---|
| B-pergola-daybed | `rec_wooden-pergola-garden-swing-daybed-a-heavy-timbe_20260606_115258_129620_2e535d45` | Four-post pergola + mattress/daybed dominates identity (`model.py:51-177`, daybed `153-297`). Use only as negative boundary and optional light roof vocabulary; never sample four-post frame or daybed body. |
| B-chainbench-bad | `rec_wood_swing_var_chainbench` | Rejected 2026-07-02. Do not overwrite this source record and do not use it as a positive template source: four independent corner chain/top-bracket vocabulary makes the bench/frame read visually tangled and unrealistic. Chain links may be represented, but generated topology must keep two side pivots with front/rear lower branch endpoints only. |
| B-chain-daybed | `rec_wood_swing_var_chaindaybed` | Same daybed/pergola drift with chain suspension. Chain copy logic may inform links, but daybed body and four-post frame are excluded. |
| B-single-chair | `rec_wood_swing_var_chairseat` | Single hanging chair, not bench swing. It has useful curved-panel craft (`model.py:123-156`) but fails required long-bench width/armrest/bench identity. |
| B-archrope | `rec_wood_swing_var_archrope` | Arched frame + rope is acceptable only if the generated seat remains bench-like; its arched beam should not replace the category with playground/park swing vocabulary. |

## 核心身份
Bench / Wood Swing = furniture-like porch or garden **bench swing**. Mandatory readable features:

- Fixed support frame with two side support planes or upright pairs and a transverse top beam/hanger bar.
- One bench assembly suspended below the beam and moving fore/aft on a REVOLUTE axis roughly parallel to +Y.
- Bench assembly has a slatted or panelled seat, a backrest, and side armrests/end frames.
- Suspension connects to bench sides/corners: rigid arms, rods, chains, or ropes may vary, but the seat remains one coherent pendulum.
- Optional canopy/roof can appear, but it cannot turn the object into a pergola bed.

Neighbor boundary:
- `playground_swing`: multiple independent child seats, belt/plank/tire seats, no furniture bench/back/armrest identity.
- fixed garden bench: no non-fixed pendulum joint.
- hammock/daybed/pergola swing: mattress/platform or four-post pavilion dominates; excluded here.
- single hanging chair: one-person chair shell, not a bench.

## Slot 候选表

### Slot A — `support_frame`
| module_name | source | line refs | sampling | structure |
|---|---|---|---|---|
| `round_log_a_frame` | P1-log-glider | `96-118`, `251-279` | eligible | two log A-frame end supports with a round top beam and mid cross braces |
| `tubular_a_frame` | P2-metal-bench | P2 `75-126`, `192-217` | eligible | splayed metal tube A-frames, top crossbar, clevis/lug hardware |
| `slatted_end_wall_a_frame` | P3-sheltered-bench / V-rope-bench | P3 `57-193`; V-rope `91-215` | eligible | A-shaped end walls with vertical slats, ridge beam, pitched shelter |
| `square_timber_a_frame` | P4-canopy-bench | `121-166`, canopy supports `247-305` | eligible | dark square-timber A-stand with top beam and tray/side rails |
| `upright_bar_frame` | V-arch-bench / B-archrope | V-arch `78-198`; archrope `103-184` | eligible but low weight | two vertical/upright side posts and a single top bar/arched beam; must keep bench furniture proportions |
| `four_post_pergola` | B-pergola-daybed | `51-152` | excluded | four-post pavilion frame; too strong, caused category drift |

### Slot B — `suspension`
| module_name | source | line refs | sampling | structure |
|---|---|---|---|---|
| `rigid_log_arms` | P1-log-glider | arms `293-338`, platform mount `389-432` | eligible | two side hanger modules with front/rear lower branch arms; one driver revolute + one mimic follower |
| `rigid_tubular_arms` | P2-metal-bench / V-arch-bench | P2 `128-177`, `314-368`; V-arch `109-158`, `295-349` | eligible | metal tubular V-pair arms from crossbar lugs to bench armrests |
| `rigid_rods` | P3-sheltered-bench | rods `266-286`, pivot `287-299` | eligible | thin rods visually drawn on bench part; single revolute bench pendulum |
| `rigid_wood_arms` | P4-canopy-bench | arms `247-273`, joints `352-381` | eligible | square wooden arms bolted to bench sides |
| `chains` | V-log-chain + real bench-swing constraint | logchain helper `254-300`, joints `353-396`; reject pattern from quarantined chainbench | eligible | two moving side chain hangers, not four independent corner chains; each side has one top pivot/hub and two visible branch legs to front/rear lower contacts, with driver + mimic |
| `ropes` | V-rope-bench | rope helper `75-88`, rope joints `216-265` | eligible | two top side rope hangers; each may branch to front/rear lower contacts, with driver + mimic |

### Slot C — `bench_body`
| module_name | source | line refs | sampling | structure |
|---|---|---|---|---|
| `straight_slatted_bench` | P3/P4/V-rope | P3 `196-286`; P4 `280-350`; V-rope `266-300` | eligible | long bench with seat slats, reclined back slats, two armrests |
| `rolltop_metal_bench` | P2/V-arch | P2 `231-313`; V-arch `212-294` | eligible | CAD-style slatted seat, curved rolltop back, cup-holder armrests |
| `facing_glider_bench` | P1/V-log-chain | P1 `340-432`; V-log `402-490` | legacy/boundary, not sampled | two facing slatted seats plus center table/platform; too often reads as glider pavilion/odd chair in this class |
| `compact_wood_bench` | P4 | `280-350` | eligible | shorter two-seat wooden bench with vertical back slats and thick armrests |
| `daybed_platform` | B-pergola-daybed/B-chain-daybed | daybed `153-297` | excluded | mattress/platform makes output read as daybed/pergola swing |
| `single_hanging_chair` | B-single-chair | chair shell `390-458` | excluded | one-person chair, not bench |

### Slot D — `canopy`
| module_name | source | line refs | sampling | structure |
|---|---|---|---|---|
| `none` | P2-metal-bench / V-arch-bench | no roof part | eligible | open top beam/crossbar only |
| `pitched_gable_roof` | P1/P3/V-rope | P1 `119-143`, `281-291`; P3 `146-191`; V-rope `172-215` | eligible | two sloped sheets or slatted shelter over bench |
| `fabric_awning` | P4 | scallop helper `77-110`, panels/skirt `264-305` | eligible | canvas/fabric canopy with optional scalloped skirt |
| `light_flat_lattice_roof` | B-pergola-daybed vocabulary only | rafters `120-133` | legacy/boundary, not sampled | pergola vocabulary; map to pitched/fabric treatment unless manually reviewed |

## Slot Graph
```
root support frame
  ├─ fixed top beam / crossbar / hanger bar
  ├─ two top side pivot stations (left/right), not four independent corner pivots
  ├─ optional canopy roof fixed to frame
  └─ suspension driver REVOLUTE about +Y
       ├─ one mimic side hanger (same q, multiplier 1.0)
       ├─ each side hanger visually splits to front/rear lower lugs
       └─ fixed bench_body (slatted seat + backrest + armrests)
```

The kinematic tree is deliberately not a true closed 4-bar. Use the source-backed topology: one side hanger is the REVOLUTE driver and the opposite side hanger is a REVOLUTE mimic with `multiplier=1.0`; each side hanger may visually branch to front/rear lower contacts. Do not model four independent top pivot blocks.

## Per-Module Emits / Interfaces
- `support_frame` emits the fixed grounded frame and beam/hanger hardware. It must expose exactly two top side pivot stations/parallel connector bars (`left`, `right`) above the bench sides.
- `suspension` emits two moving side-hanger modules. Each module may visually split into front/rear rods, chains, or ropes at the lower bench contacts. All non-fixed joints are REVOLUTE about +Y, with one driver and one mimic.
- `bench_body` emits one coherent furniture bench. Required visuals or equivalents: `seat_slat_*`, `back_slat_*` or curved back panel + slats, `armrest_*`, side/end rails.
- `canopy` emits only frame-attached shade/roof details. It must not introduce a second ground frame family.

## 参数范围
| 参数 | 类型 | 范围 / 候选 | 约束 |
|---|---|---|---|
| `support_frame_module` | enum | `round_log_a_frame`, `tubular_a_frame`, `slatted_end_wall_a_frame`, `square_timber_a_frame`, `upright_bar_frame` | `upright_bar_frame` low weight; no `four_post_pergola` |
| `suspension_module` | enum | `rigid_log_arms`, `rigid_tubular_arms`, `rigid_rods`, `rigid_wood_arms`, `chains`, `ropes` | choose compatible visual material with frame; all keep bench pendulum |
| `bench_body_module` | enum | `straight_slatted_bench`, `rolltop_metal_bench`, `compact_wood_bench` | no daybed, no single chair; `facing_glider_bench` is legacy input mapped away |
| `canopy_module` | enum | `none`, `pitched_gable_roof`, `fabric_awning` | roof cannot dominate identity; `light_flat_lattice_roof` is legacy input mapped away |
| `palette_style` | enum | `cedar_red_roof`, `light_gray_metal`, `sage_pine`, `dark_stained_canvas`, `natural_rope_teak` | sampled per seed; every visual uses palette materials |
| `seat_slat_count` | int | 4-18 | looped; not a structural slot |
| `back_slat_count` | int | 4-10 | looped or mapped to rolltop rows |
| `roof_rib_count` | int | 8-28 | only when roof present |
| `chain_link_count` | int | 8-20 | only for `chains`; repeated `chain_link_{i}` |
| `rope_segment_count` | int | 1-4 visual segments per rope | only for `ropes`; repeated/segmented rope visuals |
| `swing_limit` | float | 0.32-0.48 rad | clear frame/roof/ground at both extremes |
| `frame_scale` | float | 0.92-1.08 | clamp before deriving clearances |

## Multiplicity / Copy Logic
- Seat slats and back slats are loop-emitted. Observed counts: P1 seat 4/back 5 per side, P2 seat 16/back 8, P3/P4 seat 6/back 4-9.
- Roof ribs/rafters are loop-emitted. Observed counts: P1 roof ribs 16 per panel; P3/V-rope 24; P5 rafters 13 but use only as light roof vocabulary.
- Chain links are loop-emitted from a shared helper with alternating orientations, but `rec_wood_swing_var_chainbench` is a negative topology example and must not be copied as a source of four independent top anchors.
- Chain/rope side hangers may emit two visual branches per side hanger. The top interface remains two side pivots; four lower contacts are allowed only as branch endpoints, not as four independent top anchors.
- Chain/rope hangers should not add a lower rigid side bar between the front and rear lower lugs; the bench side rail already provides the coherent lower structure.
- Do not fork or slot pure N changes. N is controlled by seed sampling.

## §8.5 视觉多样性 6 轴考察
| axis | present? | spec decision |
|---|---|---|
| ① Part-tree / skeleton | yes | frame and suspension choices change support/hanger part tree but stay within bench-swing identity |
| ② Joint topology | yes | one driver + optional mimic followers vs single bench pivot; always at least one REVOLUTE fore/aft pendulum |
| ③ Primary Form Family | yes | A-frame, slatted end-wall, square timber A-stand, upright bar frame; four-post pergola excluded |
| ④ Surface detail | yes | slats, ribs, lugs, cup holders, scalloped skirt, tray shelves, foot plates, end caps |
| ⑤ Multiplicity | yes | slat counts, roof ribs, chain links, rope segments |
| ⑥ Material / palette | yes | cedar/red roof, gray metal, sage pine, dark stained canvas, rope/teak |

## Topology Diversity Audit
- Nominal eligible upper bound: 5 support frames x 6 suspensions x 3 bench bodies x 3 canopy options = 270, plus chain/rope multiplicity choices.
- Compatibility narrowing:
  - `rigid_log_arms` prefers `round_log_a_frame` or wood palettes; can be mapped to timber frames if proportions remain light.
  - `rigid_tubular_arms` prefers tubular/upright frames.
  - `fabric_awning` prefers `square_timber_a_frame` but can adapt to A-frame.
  - `light_flat_lattice_roof` is not in normal sampling; map legacy configs to `pitched_gable_roof` or redesign only after visual review.
- Seed 0 anchor: P2/P3-like A-frame bench, with clear top beam, two top side pivot stations, side hangers branching to lower bench contacts, slatted seat, backrest, armrests.

## Validator Requirements
The template tests must assert:

- At least one non-fixed REVOLUTE joint named as the swing driver, axis approximately +Y, limits around +/-0.32..0.48 rad.
- If mimic followers exist, every follower references the driver with multiplier 1.0.
- A fixed support frame exists and remains grounded; a top beam/crossbar/hanger bar exists above the bench.
- Exactly two top side pivot stations exist. Validator should reject `pivot_pin_front_left/front_right/rear_left/rear_right`-style four independent top corner pivots.
- Chain/rope variants have exactly two moving side hanger parts. They must not emit `chain_front_left`, `chain_rear_right`, or equivalent four-corner moving parts/joints.
- Side hangers may branch to four lower contacts, but all lower branches must derive from the two top side pivots.
- Bench body has slatted or panelled seat, visible backrest, and two armrests/end frames.
- Bench width is furniture-like, roughly 1.0-1.8 m, and wider than a single chair.
- In both swing extremes, bench clears ground, side frame, and roof/canopy if present.
- `daybed_platform`, `single_hanging_chair`, and `four_post_pergola` module names never appear in `slot_choices_for_seed`.
- Palette differs across seeds; every visual material is driven by `mats[...]`.

## Reject Cases
- Four-post pergola/daybed/mattress dominates the scene.
- Single hanging chair or egg-chair silhouette.
- Playground swing set: multiple independent child seats, tire/belt/plank seats, no furniture back/armrests.
- Bench is fixed and does not swing.
- Suspension rods/chains/ropes pass through the seat, back, or frame in the rest pose.
- Canopy or roof is so large/heavy that the object reads as pavilion rather than bench swing.
- Four independent top pivot blocks/corner anchors for rigid rods, chains, or ropes.
- Chain/rope variants with fake lower rigid bars or visually tangled four-corner chain pendulums.
- Facing-glider/daybed/pergola vocabulary in normal sampling, including oversized flat lattice roofs.
- Monochrome random output unless the sampled palette explicitly represents the gray metal CAD source.

## 审核记录
| 项 | 结论 |
|---|---|
| rewrite reason | old spec over-promoted daybed/pergola and single-chair variants |
| topology correction | 2026-07-02: quarantined `rec_wood_swing_var_chainbench` as a problem sample; changed template/spec from four independent corner top anchors to source-backed two side pivot stations; `facing_glider_bench` and `light_flat_lattice_roof` removed from normal sampling |
| bad source lock | 2026-07-02: `rec_wood_swing_var_chainbench` moved to boundary as a rejected source; do not overwrite that record and do not promote its four-corner chain topology into the template |
| reviewer status | implemented; `uv run articraft template sweep-pipeline Bench_Wood_Swing --max-workers 1` passed 50/50 |
