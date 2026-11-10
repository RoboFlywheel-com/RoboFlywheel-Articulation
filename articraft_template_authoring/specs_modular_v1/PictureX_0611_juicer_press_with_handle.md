# PictureX_0611_juicer_press_with_handle - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_juicer_press_with_handle` |
| template path | `agent/templates/pictureX_0611_juicer_press_with_handle.py` |
| test path (optional) | inline `run_picturex_0611_juicer_press_with_handle_tests` |
| stage | `TEMPLATE_ITERATION` |
| status | `sweep_pipeline_target` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 |
| read_count | 5 |
| read_scope | current confirmed 5-star pool for `0611 / juicer_press_with_handle` only |
| source_index_policy | source map + synced 5-star records; excluded downgraded historical `rec_juicer_press_var_*` records |

Confirmed sources read:

| source | model.py lines read | adopted role |
|---|---:|---|
| `rec_picturex_0611__juicer_press_with_handle__001__png_4f95d74d2d3847cd8bdb9c4751cc97b7` | L24-L632 | origin lever press, dual posts, cup/strainer, lever/linkage, prismatic ram |
| `rec_juicer_press_with_handle_var_screw_press` | L22-L579 | screw crosshead, threaded ram, top handwheel, continuous drive |
| `rec_juicer_press_with_handle_var_c_frame_lever_refill` | L29-L720 | C-frame casting, long lever, linkage, guide ram |
| `rec_juicer_press_with_handle_var_rack_pinion_refill` | L30-L734 | rack-pinion side drive, rack ram, pinion housing |
| `rec_juicer_press_with_handle_var_bench_clamp_press_refill` | L29-L826 | bench clamp base, clamp screw, lever/linkage, cup/strainer |

## 核心身份

Manual tabletop or bench-mounted juicer press with a load-bearing frame, centered cup/strainer receiver, vertical press head/ram, and a human-operated force mechanism. Exclude electric juicers, blenders, standalone citrus reamers, and generic clamps without juicing receiver/press head.

## 槽位 + 候选模块表

### Slot A：source_candidate / frame_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `origin_lever_press` / `dual_post_frame` | origin_anchor | origin record | L193-L428 | eligible | weighted base, twin guide posts, upper crosshead, lever pivot, cup/strainer |
| `screw_press` / `screw_crosshead` | forked_anchor | `rec_juicer_press_with_handle_var_screw_press` | L215-L393 | eligible | dual-post frame plus threaded nut housing and handwheel mount |
| `c_frame_lever` / `c_frame_casting` | forked_anchor | `rec_juicer_press_with_handle_var_c_frame_lever_refill` | L231-L467 | eligible | C-shaped rear column and upper throat arm with ram guide |
| `rack_pinion_press` / `rack_crosshead` | forked_anchor | `rec_juicer_press_with_handle_var_rack_pinion_refill` | L211-L453 | eligible | slotted crosshead and side pinion bearing housing |
| `bench_clamp_press` / `bench_clamp_base` | forked_anchor | `rec_juicer_press_with_handle_var_bench_clamp_press_refill` | L284-L556 | eligible | C-clamp base with upper plate, lower jaw, upright and crosshead |

### Slot B：force_mechanism
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `lever_linkage` | origin_anchor/forked_anchor | origin + C-frame | origin L287-L428; C-frame L316-L467 | eligible with lever frames | revolute long lever, secondary linkage, prismatic ram |
| `screw_handwheel` | forked_anchor | `rec_juicer_press_with_handle_var_screw_press` | L306-L393 | eligible with screw crosshead | continuous handwheel, visible spokes/knob, threaded ram |
| `rack_pinion` | forked_anchor | `rec_juicer_press_with_handle_var_rack_pinion_refill` | L321-L453 | eligible with rack crosshead | side crank/pinion, toothed rack on prismatic ram |
| `clamp_lever` | forked_anchor | `rec_juicer_press_with_handle_var_bench_clamp_press_refill` | L350-L556 | eligible with bench clamp | clamp screw plus lever/linkage and vertical press ram |

### Slot C：receiver_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `cup_strainer` | origin_anchor | origin record | L262-L286, L566-L632 | eligible | lathed cup, removable strainer plate, drain holes |
| `raised_strainer` | forked_anchor | screw/rack anchors | screw L281-L304; rack L294-L319 | eligible | higher metal strainer under ram/head |
| `deep_basket` | forked_anchor | bench-clamp anchor | L369-L392 | eligible | deeper receiver on clamp base |

## 槽位图（slot graph）

pattern: mixed

`frame_module` is the root chassis. `receiver_module` mounts on the base/cup center through a short prismatic service joint. `force_mechanism` mounts to the frame crosshead or side housing and drives `vertical_ram` through a prismatic press stroke. Bench-clamp adds a continuous clamp screw on the base; screw and rack modules replace the lever with continuous/revolute rotary input.

Compatibility is source-candidate locked:

| source_candidate | frame_module | force_mechanism | receiver_module |
|---|---|---|---|
| `origin_lever_press` | `dual_post_frame` | `lever_linkage` | `cup_strainer` |
| `screw_press` | `screw_crosshead` | `screw_handwheel` | `raised_strainer` |
| `c_frame_lever` | `c_frame_casting` | `lever_linkage` | `cup_strainer` |
| `rack_pinion_press` | `rack_crosshead` | `rack_pinion` | `raised_strainer` |
| `bench_clamp_press` | `bench_clamp_base` | `clamp_lever` | `deep_basket` |

## 每槽位 Module Emits / Interfaces

### Slot A / frame_module
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` with base, posts/C-frame/bench clamp, crosshead or pinion housing | all five records, build lines listed above |
| internal joints | optional `body_to_bench_clamp_screw` continuous on bench-clamp candidate | bench-clamp L463-L475, L753 |
| downstream interface | cup center and ram guide center expressed as resolved origins | all source frames |

### Slot B / force_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `press_handle` with fused linkage/tab visuals; visible handwheel/rack/pinion/clamp details | origin/screw/C-frame/rack/bench records |
| internal joints | `body_to_press_handle` revolute or continuous; linkage bars are host visuals on the moving handle, not separate fixed/floating parts | source run_tests joint expectations + AUTHORING Rule 1 |
| downstream interface | drives `vertical_ram` along z through source-backed guide bore | all records |

### Slot C / receiver_module
| emits | 描述 | 来源 |
|---|---|---|
| parts | `juice_cup`, `perforated_strainer` with host-conformal hole visuals | all records |
| internal joints | `body_to_juice_cup` and `juice_cup_to_perforated_strainer` prismatic service/removal joints | source run_tests expect prismatic cup/strainer joints |
| upstream interface | centered below press head; clamped to source-compatible cup center | all records |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | five confirmed source candidates | `origin_lever_press` | choice | deterministic seed cycle over confirmed 5-star pool | source map |
| `frame_module` | enum | 5 frame modules | `dual_post_frame` | equation | derived from `source_candidate` compatibility table | Slot A |
| `mechanism_module` | enum | `lever_linkage`, `screw_handwheel`, `rack_pinion`, `clamp_lever` | `lever_linkage` | equation | derived from `source_candidate` compatibility table | Slot B |
| `receiver_module` | enum | `cup_strainer`, `raised_strainer`, `deep_basket` | `cup_strainer` | equation | derived from `source_candidate` compatibility table | Slot C |
| `width` | float | [0.32, 0.56] | 0.42 | independent | clamp before geometry | all records |
| `height` | float | [0.56, 0.90] | 0.72 | independent | clamp before geometry | all records |
| `throat_depth` | float | [0.12, min(0.25, width * 0.54)] | 0.18 | inequality | cup center must remain under crosshead/guide | frame interfaces |
| `lever_length` | float | [0.42, 0.78], screw/rack upper 0.58 | 0.58 | conditional | shortened for rotary modules | force mechanisms |
| `ram_travel` | float | [0.055, 0.155] | 0.11 | inequality | lower pose reaches strainer without exceeding cup depth | source run_tests targeted pose |
| `spoke_count` | int | 3-6 | 4 | conditional | screw handwheel only; still reported in slot choices for coverage | screw fork |
| `strainer_hole_count` | int | 12-32 | 18 | conditional | visual holes emitted on strainer host | source strainer loops |

## compile budget

Per seed budget: 5-20s. The template uses SDK Box/Cylinder primitives and host visual loops for holes/spokes rather than CadQuery booleans, so it should stay comfortably below the 120s sweep timeout.

## Multiplicity / Copy Logic

- `spoke_count`: 3-6 handwheel spokes/knob supports, source-backed by screw handwheel; emitted as visuals on `press_handle`.
- `strainer_hole_count`: 12-32 host-conformal drain-hole visuals on `perforated_strainer`; does not create separate fixed parts.
- `rubber_foot`: fixed four visual pads fused into `body`; not a separate part/joint.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | dual-post, screw-crosshead, C-frame, rack-crosshead, bench-clamp; all source-backed |
| └ multiplicity | 同构件 ×N | 有 | `spoke_count` 3-6; `strainer_hole_count` 12-32; §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | revolute lever/pinion, continuous handwheel/clamp screw, prismatic ram/cup/strainer |
| ③ 主体形态家族 / Primary Form Family | 核心 part 的可识别几何形态原型 | 有 | dual-post tabletop, C-frame casting, side rack-pinion, bench-clamp base; source-backed Volumetric Envelope/Macro Surface variants |
| ④ 表面装饰 | 表面细节 / 装饰数 | 有 | strainer holes, screw thread bands, rack teeth, rubber feet; host visuals only |
| ⑤ 尺寸/行程 | 连续改尺寸/比例/行程 | 有 | width/height/throat/lever/ram travel; motion_test_plan: sampled pose collision + targeted ram stroke, handle pose, clamp screw rotation |
| ⑥ 涂装 | 材质/颜色 | 有 | industrial, painted, walnut, slate via existing palette helper |

## 采样与覆盖审计

总组合数：5 source candidates × 4 palettes × 4 spoke bins × 5 strainer-hole bins, with frame/mechanism/receiver compatibility derived from source candidate.

seed_domain_policy: procedural_first. Seeds cycle through the five confirmed source candidates, then palette/count bins vary deterministically. This is deliberate because the confirmed pool has only five trustworthy structural anchors.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `source_candidate = candidates[seed % 5]`; derived frame/mechanism/receiver; palette/count bins vary by seed | `slot_choices_for_seed` returns implemented modules |
| compatibility matrix | source-candidate locked table above | no illegal cross-module hybrids |
| controlled local variation | width, height, throat, lever length, ram travel clamp in `resolve_config` | proportions vary without moving cup out from under head |
| regression overrides | none | ordinary seeds use same procedural path |
| random sweep | 0-35 plus pipeline corner seeds | compile warnings, motion audit, per-key coverage |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 5 | yes | yes | confirmed source pool |
| frame_module | 5 | yes | yes | derived compatibility |
| force_mechanism | 4 | yes | yes | lever, screw, rack, clamp |
| receiver_module | 3 | yes | yes | cup, raised strainer, deep basket |
| palette_style | 4 | yes | yes | visual material variation |

## Validator

- template exports `build_picturex_0611_juicer_press_with_handle`, `build_object_model`, `config_from_seed`, `slot_choices_for_seed`, and `run_picturex_0611_juicer_press_with_handle_tests`
- every ordinary seed maps to one of the five confirmed 5-star source candidates
- `rec_juicer_press_var_*` downgraded historical records are not used
- cup/strainer remains centered under press head
- ram has prismatic stroke and targeted pose coverage
- lever/handwheel/rack/clamp input has a non-fixed operating joint
- `run_tests` includes sampled-pose collision check and targeted `ctx.pose`
- no fixed decoration-only parts; holes/spokes/feet/threads/teeth are host visuals

## Reject cases

- electric juicer, blender, or standalone reamer
- generic bench clamp without cup/strainer and press head
- static decorative handle without an articulation
- ram/head not aligned over receiver
- source candidate outside the confirmed 5-star pool
- any use of downgraded `rec_juicer_press_var_*` records as module evidence

## 与相邻类别的边界

- Electric countertop juicer: excluded because this category is manual, framed, and handle/press operated.
- Hand citrus reamer: excluded because it lacks a frame, ram, and pressing mechanism.
- Generic clamp/vise: excluded unless it has a juicing receiver and press head.

## 审核记录

- 2026-07-13: variant pool confirmed by user; spec updated from 2 samples to current 5 confirmed 5-star records; historical downgraded `rec_juicer_press_var_*` excluded.
