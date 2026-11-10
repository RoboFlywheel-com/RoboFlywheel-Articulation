# PictureX_0611_Industrial_rolling_work_table - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Industrial_rolling_work_table` |
| template path | `agent/templates/pictureX_0611_Industrial_rolling_work_table.py` |
| test path (optional) | n/a |
| stage | `P3_P4_ITERATED` |
| status | `sweep_pipeline_pass` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all confirmed 5-star samples for `0611 / Industrial_rolling_work_table` |
| source_index_policy | only the 7 current confirmed 5-star records are adopted; downgraded historical `rec_rolling_work_table_var_lower_shelf_handle` is excluded |

Adopted source records:
`rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275`,
`rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445`,
`rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9`,
`rec_picturex_0611__industrial_rolling_work_table__004__png_d11cca56695549bb9bda9bfd813476e2`,
`rec_industrial_rolling_work_table_var_drawer_cabinet`,
`rec_industrial_rolling_work_table_var_adjustable_height`,
`rec_industrial_rolling_work_table_var_pegboard_rack_refill`.

## 核心身份

工业滚动工作台：刚性工作面、金属管/板框架、四个脚轮及轮滚动语义，常见下层搁板、抽屉柜、升降腿或后置工具挂板/托盘。默认成熟域是 workshop / industrial / service cart work surface。排除无工作面的工具柜、厨房推车、静态工作台、纯货架、scissor lift cart。

## 槽位 + 候选模块表

### Slot A：body_family
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| open_frame_shelf_table | origin_anchor | 001/003/004 origins | 001 L38-L142; 003 L104-L184; 004 L73-L147 | eligible | folded or wood work surface, tube legs, lower shelf / wire grid, open frame |
| drawer_cabinet_table | forked_anchor | `rec_industrial_rolling_work_table_var_drawer_cabinet` + 004 origin | fork L44-L153, L156-L216, L333-L364; 004 L148-L166 | eligible | under-top cabinet bay, 2-4 prismatic drawers, rails/pulls/stops |
| adjustable_height_table | forked_anchor | `rec_industrial_rolling_work_table_var_adjustable_height` | L80-L118, L197-L288, L330-L461 | eligible | four telescoping sleeve posts, locking collars, caster sockets ride on sliding outer posts |
| pegboard_tool_rack_table | forked_anchor | `rec_industrial_rolling_work_table_var_pegboard_rack_refill` | L80-L111, L199-L223, L445-L498 | eligible | rear uprights, vertical pegboard/tool-rack panel, rack-mounted sliding tray above work surface |

### Slot B：top_style
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| folded_stainless | origin_anchor | 001 + drawer fork | 001 L42-L72; drawer fork L48-L78 | eligible | thin metal skin with downturned aprons |
| wood_slab | origin_anchor | 003/004 + pegboard fork | 003 L59-L73, L104-L109; 004 L73-L78; pegboard L73-L78 | eligible | thick wood slab / chamfered board-top read |
| equipment_deck | origin_anchor | 002 workstation origin | 002 L126-L150, L199-L242 | eligible | black equipment deck with front lip/control surface cues |

### Slot C：caster_set
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| swivel_wheel_lock_set | origin/fork_anchor | all 7 records | 001 L144-L198, L262-L329; 003 L202-L329; pegboard L258-L337 | eligible | four caster yokes, continuous vertical swivel, continuous wheel spin, revolute lock pedal |
| sleeve_mounted_casters | forked_anchor | adjustable-height fork | adjustable L330-L461 | eligible only with `adjustable_height_table` | caster set mounted under sliding `outer_post_i` instead of root body |

## 槽位图（slot graph）

pattern: mixed

`body_family` owns the root `body` work surface, frame, shelves/storage/rack, and any rail visuals. `top_style` is a body-local visual family chosen before decoration. `caster_set` is four parallel child assemblies: normally `body -> caster_yoke_i -> caster_wheel_i / caster_lock_i`; for `adjustable_height_table`, `body -> outer_post_i -> caster_yoke_i -> caster_wheel_i / caster_lock_i`.

Interface points:

- body/table frame exposes four lower leg sockets at `_leg_positions`; caster swivel joints mount on those sockets with vertical +Z continuous axes.
- drawer bay exposes front-facing paired rails; drawer parts attach by +/−Y prismatic slides and remain supported by root visual rails.
- adjustable body exposes four inner posts; each `outer_post_i` mates around the post by vertical prismatic travel along −Z, then exposes a caster socket.
- pegboard rack exposes rear uprights and two tray rails; `sliding_tray` attaches by a prismatic joint along −Y toward the operator.

## 每槽位 Module Emits / Interfaces

### Slot A / module open_frame_shelf_table
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body`; visuals `work_surface`, four legs, lower rails, `lower_shelf` / `shelf_wire_*` | 001 L38-L142; 003 L104-L184; template helper `_add_base_frame` / `_add_lower_shelf` |
| internal joints | none beyond shared caster joints | sources |
| upstream interface | root frame | source-backed |
| downstream interface | four leg caster sockets | 001 L88-L93; 003 L155-L160 |

### Slot A / module drawer_cabinet_table
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` cabinet visuals plus `drawer_i` moving children | drawer fork L101-L153, L333-L364; 004 L136-L166 |
| internal joints | `body_to_drawer_i` PRISMATIC, axis −Y, travel `[0, drawer_travel]` | drawer fork L347-L364; 004 L156-L165 |
| upstream interface | root frame and cabinet rails | source-backed |
| downstream interface | shared caster sockets | source-backed |

### Slot A / module adjustable_height_table
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` with `inner_post_i`, moving `outer_post_i` with sleeve/collar/knob/socket | adjustable L197-L288 |
| internal joints | `height_adjust_i` PRISMATIC, axis −Z, travel `[0, height_travel]` | adjustable L269-L288 |
| upstream interface | inner post sockets on root frame | source-backed |
| downstream interface | caster sockets on `outer_post_i` | adjustable L257-L268, L424-L436 |

### Slot A / module pegboard_tool_rack_table
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` with `rack_upright_i`, `pegboard_panel`, `tray_rail_i`; moving `sliding_tray` | pegboard L80-L111, L199-L223 |
| internal joints | `body_to_sliding_tray` PRISMATIC, axis −Y, travel `[0, tray_travel]`; optional drawer joints inherited from 004-style drawer bank | pegboard L213-L223; 004 L180-L197 |
| upstream interface | rear top frame uprights tied to body | source-backed |
| downstream interface | shared caster sockets | pegboard L258-L337 |

### Slot B / top_style
| emits | 描述 | 来源 |
|---|---|---|
| parts | body-local top visuals only; no independent part because the top is rigid with the frame | 001 L42-L72; 003 L104-L109; 002 L126-L150 |
| internal joints | none | Rule 1 |
| upstream/downstream interface | does not affect joints; geometry clamps within body envelope | source-backed |

### Slot C / caster_set
| emits | 描述 | 来源 |
|---|---|---|
| parts | `caster_yoke_i`, `caster_wheel_i`, `caster_lock_i` for i=0..3 | 001 L262-L329; 003 L202-L329; pegboard L258-L337 |
| internal joints | `caster_swivel_i` CONTINUOUS +Z; `wheel_spin_i` CONTINUOUS +X; `caster_to_lock_i` REVOLUTE +X | sources |
| upstream interface | body or `outer_post_i` caster socket | sources |
| downstream interface | none | terminal wheel/lock mechanisms |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_family | enum | open_frame_shelf_table, drawer_cabinet_table, adjustable_height_table, pegboard_tool_rack_table | open_frame_shelf_table | choice | deterministic `config_from_seed`; pegboard is sampled as a normal candidate | Slot A |
| top_style | enum | folded_stainless, wood_slab, equipment_deck | wood_slab | conditional | pegboard excludes folded_stainless to keep rack read clear | Slot B |
| drawer_count | int | 0, 2, 3, 4 | 3 | conditional | active only for drawer_cabinet_table and pegboard_tool_rack_table; else resolved to 0 | drawer sources |
| width | float | [0.82, 1.55] | 1.18 | independent | clamp in `resolve_config` | origins |
| depth | float | [0.46, 0.78] | 0.60 | independent | clamp in `resolve_config` | origins |
| height | float | [0.70, 1.02] | 0.90 | independent | clamp in `resolve_config`; rack height derived from final top | origins |
| drawer_travel | float | [0.18, 0.36] | 0.30 | conditional | active only for drawer-bearing families | drawer fork / 004 |
| height_travel | float | [0.08, 0.20] | 0.14 | conditional | active only for adjustable_height_table | adjustable fork |
| tray_travel | float | [0.14, 0.26] | 0.20 | conditional | active only for pegboard_tool_rack_table | pegboard fork |
| rack_height | float | derived | 0.48 | equation | `rack_base_z = height + 0.03`, fixed rack height to preserve pegboard silhouette | pegboard fork |

## compile budget

Per seed budget: 15-30s. The template uses mostly box/cylinder visuals and a fixed four-caster set; no heavy boolean mesh operations are introduced in the slug implementation.

## Multiplicity / Copy Logic

- `caster_count`: fixed 4, copied from all confirmed records; each caster has swivel, wheel-spin, and lock joints.
- `drawer_count`: conditional N in `{2,3,4}` for drawer-cabinet and pegboard/tool-rack tables; sampled and recorded as `("drawer_count", "nN")`.
- `height_post_count`: fixed 4 for `adjustable_height_table`.
- `peg_hole_count`: fixed local visual grid on `pegboard_panel`; decorative, body-local, not a template-level multiplicity axis.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `body_family`: open frame, drawer cabinet, adjustable height, pegboard/tool rack; all fork/source-backed |
| └ multiplicity | 同构件 ×N | 有 | drawer_count `{2,3,4}` conditional; fixed 4 casters; fixed 4 height posts |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | CONTINUOUS caster swivel/wheel spin; REVOLUTE caster lock; PRISMATIC drawer, height post, rack tray |
| ③ 主体形态家族 / Primary Form Family | 核心 part 可识别几何形态原型 | 有 | open shelf body, cabinet body, telescoping-post body, rear pegboard rack body; source-backed anchors |
| ④ 表面装饰 | 宿主表面细节 | 有 | top seams, pegboard holes, drawer pulls, rails, lock pedals; host-local visuals only |
| ⑤ 尺寸/行程 | 连续尺寸/比例/行程 | 有 | width/depth/height independent; drawer/tray/height travel conditional. Motion tests cover drawer pull, rack tray pull, height post extension, caster swivel |
| ⑥ 涂装 | 材质/颜色 | 有 | oak, painted, industrial, walnut palettes; materials include wood/panel/metal/dark/accent/glass categories |

## 采样与覆盖审计

总组合数：4 body_family × up to 3 top_style × 4 drawer_count bins including n0 × 4 palettes, with conditional gates; true reachable topology tuples are lower because drawer_count resolves to n0 on non-drawer families and folded_stainless is gated off for pegboard.

seed_domain_policy：procedural_first。`config_from_seed(seed)` uses deterministic RNG choices, not a curated fixed table. Pegboard/tool-rack is a normal `body_family` candidate and appears in ordinary seed sweeps (for example seed 0/9 under the current sampler).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | choose `body_family`, gated `top_style`, drawer count, palette, dimensions/travel; all exposed via `slot_choices_for_seed` | seed 0-35 should include pegboard_tool_rack_table and drawer/height/open families |
| compatibility matrix | drawer_count forced n0 unless body supports drawers; pegboard gates out folded_stainless; sleeve-mounted casters only with adjustable family | no floating tray, no drawer on open/height family, caster parent follows body vs outer_post |
| controlled local variation | width/depth/height/travel clamped in `resolve_config` | proportions vary without losing rolling work-table identity |
| regression overrides | none | no seed special casing |
| random sweep | use capped sweep-pipeline 0-35/validator default | contract failures, slot choices, and pegboard rack realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_family | 4 | yes | yes | includes confirmed pegboard/tool-rack refill |
| top_style | 3 | yes | yes | body-local visuals |
| caster_set | 2 | yes | no | one is conditional sleeve-mounted caster parent for height-adjust body |

## Validator

- `slot_choices_for_seed` returns implemented values: `body_family`, `top_style`, `drawer_count`, `palette_style`.
- `config_from_seed` is deterministic procedural sampling and has no curated seed table.
- `resolve_config` clamps dimensions and resolves conditional drawer count before build.
- Pegboard/tool-rack table emits rear `rack_upright_*`, `pegboard_panel`, `tray_rail_*`, and `sliding_tray`.
- Drawer-bearing families emit prismatic drawer joints and visible runner rails.
- Adjustable-height family emits four `outer_post_i` parts and four `height_adjust_i` prismatic joints.
- Every seed emits four caster swivel joints, four wheel-spin joints, and four caster lock joints.
- Tests include targeted motion checks for drawers, rack tray, height posts, and caster swivel.

## Reject cases

- Any sample using downgraded historical `rec_rolling_work_table_var_lower_shelf_handle`.
- Table without wheels or without work surface.
- Pegboard candidate missing rear rack/panel or rack sliding tray.
- Drawer candidate with static/fused drawers.
- Adjustable-height candidate whose casters remain parented to root body instead of moving sleeve posts.
- Identity drift into tool chest, kitchen cart, fixed bench, generic shelving, or scissor lift.

## 与相邻类别的边界

This slug remains a mobile industrial work surface. A tool cart can have pegboard/drawers, but when the cabinet/storage mass dominates and the worktop becomes secondary it belongs to `Handtools_Tool_cart`; when the object is static it is a workbench, not this rolling table.

## 审核记录

2026-07-13: User confirmed the current variant pool. P3+P4 update uses exactly the 7 confirmed 5-star records in `articraft_template_authoring/picture_source_maps/0611__Industrial_rolling_work_table.md`; `rec_industrial_rolling_work_table_var_pegboard_rack_refill` is promoted to a sampled `body_family` candidate. Capped sweep-pipeline verdict: pass, 48/48 seeds, pass_rate 1.0.
