# PictureX_0611_ironing_board2 - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_ironing_board2` |
| template path | `agent/templates/pictureX_0611_ironing_board2.py` |
| test path (optional) | n/a |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending_template` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | only current confirmed 5-star pool from `0611__ironing_board2.md` |
| source_index_policy | only the 7 confirmed origin/fork records below; downgraded historical records excluded |

## 核心身份

Compact ironing board: a padded narrow board top with an underside tray or hinge rail, plus a folding/supporting mechanism that positions the board for ironing. In-scope forms are tabletop short-leg boards, freestanding X-leg boards, wall-mounted fold-down boards, sleeve-board attachments, and T-leg height-adjustable supports. Exclude laundry drying racks, work tables, benches, shelves, and ironing presses.

## 槽位 + 候选模块表

### Slot A：board_top
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| capsule_perforated | origin_anchor | `rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567` | L26-L176, L324-L390 | eligible | capsule/tapered padded board, conformal cover pattern, underside tray, hinge tabs |
| slotted_pan | origin_anchor | `rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef` | L29-L133, L165-L230 | eligible | slotted pan board top, perforation slots, underside rails and hinge mounts |

### Slot B：support_or_base
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| tabletop_short_legs | forked_anchor | `rec_ironing_board2_var_tabletop_short_legs_refill` | L133-L370 | eligible | two short folding U-leg frames under board plus latch/brace revolute joints |
| x_leg_floor | forked_anchor | `rec_ironing_board2_var_x_leg_floor` | L134-L393 | eligible | freestanding floor-height crossing leg frames, central pivot visual, lock braces |
| wall_mount_fold_down | forked_anchor | `rec_ironing_board2_var_wall_mount_fold_down_refill` | L212-L526 | eligible; accessory gated off | wall bracket root, board hinge, folding support arm; two revolute joints |
| t_leg_height_adjust | forked_anchor | `rec_ironing_board2_var_t_leg_height_adjust_refill` | L226-L456 | eligible | twin telescoping T-posts with prismatic height travel and locking collars |

### Slot C：board_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | origin_anchor | origins plus non-sleeve variants | n/a | eligible | no side accessory |
| sleeve_board | forked_anchor | `rec_ironing_board2_var_sleeve_board_refill` | L324-L467 | eligible except wall mount | secondary narrow hinged sleeve board with support bracket and revolute side hinge |

## 槽位图（slot graph）

pattern: mixed

`board_top` is the host for tabletop, X-leg, T-leg, and sleeve-board cases. `support_or_base` attaches to underside hinge tabs or post mounts. `board_module=sleeve_board` attaches to a side lug on the host board and is gated off for `wall_mount_fold_down`. For wall-mount, the bracket is the root `body`, the board is a revolute child, and the support arm is a second bracket child.

跨 slot 接口：
- board underside hinge tabs -> folding leg frames: REVOLUTE about Y, lower deployed angle in `[-fold_angle, 0]`.
- board underside brace sockets -> lock braces: REVOLUTE about Y with small latch travel.
- board post mounts -> T-posts: PRISMATIC along Z, extension `[ -post_travel, 0 ]`; collar is REVOLUTE about Z.
- wall bracket hinge block -> board: REVOLUTE about Y; support arm also REVOLUTE about Y.
- board side lug -> sleeve board: REVOLUTE about X.

## 每槽位 Module Emits / Interfaces

### Slot A / capsule_perforated
| emits | 描述 | 来源 |
|---|---|---|
| parts | host board visual groups: padded board, rounded nose, tray, cover stripes, hinge tabs | origin 001 L26-L176, L324-L390 |
| internal joints | none; all board surface detail is host visual | AUTHORING Rule 1 |
| downstream interface | underside hinge/post sockets and side sleeve lug if needed | source-derived |

### Slot A / slotted_pan
| emits | 描述 | 来源 |
|---|---|---|
| parts | same host part with visible slotted cover/pan treatment | origin 002 L29-L133, L165-L230 |
| internal joints | none | source-derived |
| downstream interface | underside hinge/post sockets | source-derived |

### Slot B / tabletop_short_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | `leg_frame_0/1`, `lock_brace_0/1` | tabletop refill L255-L370 |
| internal joints | `board_to_leg_i` REVOLUTE, `board_to_brace_i` REVOLUTE | tabletop refill L287-L358 |
| upstream interface | underside hinge tabs and brace sockets on board | source-derived |
| downstream interface | rubber foot bar touches ground envelope | source-derived |

### Slot B / x_leg_floor
| emits | 描述 | 来源 |
|---|---|---|
| parts | floor-height `leg_frame_i` with `central_pivot`, `lock_brace_i` | X-leg refill L257-L393 |
| internal joints | two leg REVOLUTE joints plus two brace REVOLUTE joints | X-leg refill L310-L381 |
| upstream interface | underside hinge tabs | source-derived |
| downstream interface | full-height foot bars | source-derived |

### Slot B / wall_mount_fold_down
| emits | 描述 | 来源 |
|---|---|---|
| parts | wall bracket/root body, fold-down board, folding support arm | wall-mount refill L212-L526 |
| internal joints | `bracket_to_board` REVOLUTE, `bracket_to_support_arm` REVOLUTE | wall-mount refill L470-L495 |
| upstream interface | wall plate is root; board hinge pin seats in bracket | source-derived |
| downstream interface | support arm reinforces the folded board | source-derived |

### Slot B / t_leg_height_adjust
| emits | 描述 | 来源 |
|---|---|---|
| parts | two telescoping posts, crossbars/feet, locking collars | T-leg refill L226-L353 |
| internal joints | `board_to_post_i` PRISMATIC, `post_i_to_collar` REVOLUTE | T-leg refill L290-L335 |
| upstream interface | underside post mounts on board | source-derived |
| downstream interface | T crossbar and feet | source-derived |

### Slot C / sleeve_board
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sleeve_board` narrow padded board, hinge pin, support bracket | sleeve refill L324-L467 |
| internal joints | `board_to_sleeve` REVOLUTE about X | sleeve refill L444-L451 |
| upstream interface | board side lug | source-derived |
| downstream interface | n/a | source-derived |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| board_style | enum | capsule_perforated, slotted_pan | capsule_perforated | choice | deterministic sampler | origins |
| support_style | enum | tabletop_short_legs, x_leg_floor, wall_mount_fold_down, t_leg_height_adjust | x_leg_floor | choice | deterministic sampler | confirmed support variants |
| accessory_style | enum | none, sleeve_board | none | conditional | sleeve gated off when support_style=wall_mount_fold_down | sleeve refill |
| length | float | [0.72, 1.48] | 1.12 | independent | board features derive from length | origins |
| width | float | [0.23, 0.54] | 0.36 | independent | tray/hinge/support width derive from board width | origins |
| height | float | tabletop [0.24,0.50], others [0.48,0.92] | 0.72 | conditional | support style chooses range | support variants |
| fold_angle | float | [0.40, 1.30] rad | 0.92 | independent | REVOLUTE lower = `-fold_angle`; sampled-pose check covers lower/mid/closed | leg/brace variants |
| post_travel | float | [0.06, 0.28] | 0.18 | conditional | used only by T-leg prismatic posts | T-leg refill |
| tray_holes | int | [8,24] | 14 | independent | host visual count only; no new part | source map |
| foot_count | int | 2 or 4 | 4 | independent | encoded in slot choices; visuals remain on support part | source map |

## compile budget

Per seed budget: 15-25s; all geometry is Box/Cylinder and the dominant cost is sampled pose QC across 2-5 moving joints. Sweep watchdog should use `--compile-timeout 120`.

## Multiplicity / Copy Logic

- count_param: `tray_holes`, `foot_count`.
- N_range: tray holes 8-24 as host visual slots; foot count 2 or 4.
- copied object / naming / placement / joint policy: tray holes are non-moving visuals on the board; rubber feet are visuals on leg/post support parts, not separate fixed children. Count is reported through `slot_choices_for_seed` for foot multiplicity.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | tabletop: 4 REVOLUTE child parts; X-leg: 4 REVOLUTE with floor-height central-pivot visual; wall: bracket root + board/support arm REVOLUTE; T-leg: PRISMATIC posts + REVOLUTE collars; sleeve adds a REVOLUTE child. All forked_anchor. |
| └ multiplicity | 同构件 ×N | 有 | `tray_holes` [8,24] host visuals; `foot_count` 2/4 support visuals, see §8. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE Y folding legs/braces/wall board/arm, REVOLUTE X sleeve, PRISMATIC Z telescoping posts. All source-backed. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | capsule_perforated vs slotted_pan board top; Planar Boundary/Form surface treatment from the two origin anchors. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | cover stripes/cross slots, tray slots, screw heads, collar tabs; all host-conformal visuals on the owning part. |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | length/width/height, fold_angle, post_travel. Motion plan: sampled collision across joints plus targeted pose for leg swing, wall fold-down, T-post travel, and sleeve hinge. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | painted, industrial, oak, walnut palettes. |

## 采样与覆盖审计

总组合数：2 board styles × 4 support modules × 2 accessory states (gated for wall) × 2 foot-count states × 4 palettes = 112 nominal / 96 legal combinations before continuous parameters.

seed_domain_policy：procedural_first. `config_from_seed(seed)` uses deterministic `random.Random(seed)` for every seed, including seed 0. Compatibility matrix gates `sleeve_board` off for `wall_mount_fold_down`; no downgraded historical candidates are sampled.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | board_top -> support_or_base -> accessory -> foot_count/palette -> continuous scales | `slot_choices_for_seed` matches realized model meta |
| compatibility matrix | wall mount excludes sleeve; tabletop uses low height; T-leg uses prismatic travel; fold supports use REVOLUTE braces | no floating supports, no non-board category drift |
| controlled local variation | length/width/height, fold_angle, post_travel, tray_holes | proportions remain ironing-board-like and support attaches under/at wall hinge |
| regression overrides | none | failures should narrow sampler or repair geometry |
| random sweep | 0-35 plus corner stage via sweep-pipeline | verdict pass, axis_realization shows all support modules and sleeve candidate |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| board_top | 2 | yes | no | only two confirmed origin board-top anchors |
| support_or_base | 4 | yes | yes | confirmed support variants |
| board_module | 2 | yes | no | none vs confirmed sleeve module |

## Validator

- `slot_choices_for_seed` returns implemented module names and legal gated combinations.
- `config_from_seed` is deterministic procedural sampling for all seeds.
- Template exports `IroningBoard2Config`, `ResolvedIroningBoard2Config`, `config_from_seed`, `resolve_config`, `build_picturex_0611_ironing_board2`, `build_seeded_picturex_0611_ironing_board2`, `slot_choices_for_seed`, and `run_picturex_0611_ironing_board2_tests`.
- Board host contains padded board plus underside tray.
- Every support module has non-fixed joints with metadata.
- Motion tests include sampled-pose overlap and targeted pose checks.
- No historical downgraded records (`rear_iron_rest`, old tabletop, old x_leg_articulated) are used.

## Reject cases

- no padded board top or underside support/tray identity
- no moving support/accessory joints
- wall shelf, work table, laundry rack, bench, or ironing press drift
- floating leg frames, support arms, posts, or sleeve board
- sleeve-board sampled with wall mount
- historical downgraded variants used as module sources

## 与相邻类别的边界

- 不该混入：laundry drying rack（多杆晾晒结构不是 padded ironing surface）
- 不该混入：work table / bench（固定桌面缺少折叠/熨衣板运动语义）
- 不该混入：ironing press（压板/夹持机构而非窄 padded board）
- 不该混入：wall shelf（无 ironing-board board top 与 fold-down support arm）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Variant pool confirmed by user; template uses only the seven current 5-star confirmed records. |

## 模板实现备注

- The implementation intentionally keeps all non-moving decoration as host `visual(...)` geometry.
- Hinges, braces, support arms, telescoping posts, locking collars, and sleeve board are non-fixed articulated child parts.
- Broad overlap allowances are limited to source-backed captured hinge/socket/post interfaces and paired with sampled-pose QC plus targeted motion checks.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | board_top | capsule_perforated | `rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567` | L26-L176, L324-L390 | capsule board, tray, hinge hardware |
| S2 | board_top | slotted_pan | `rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef` | L29-L133, L165-L230 | slotted board/pan surface |
| S3 | support_or_base | x_leg_floor | `rec_ironing_board2_var_x_leg_floor` | L257-L393 | floor X-leg support and brace joints |
| S4 | support_or_base | wall_mount_fold_down | `rec_ironing_board2_var_wall_mount_fold_down_refill` | L212-L526 | bracket, fold-down board, support arm |
| S5 | support_or_base | tabletop_short_legs | `rec_ironing_board2_var_tabletop_short_legs_refill` | L133-L370 | short U-legs and latch braces |
| S6 | board_module | sleeve_board | `rec_ironing_board2_var_sleeve_board_refill` | L324-L467 | secondary sleeve board hinge |
| S7 | support_or_base | t_leg_height_adjust | `rec_ironing_board2_var_t_leg_height_adjust_refill` | L226-L456 | prismatic T-posts and locking collars |
