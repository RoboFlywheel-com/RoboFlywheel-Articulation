# pictureX_0611_Ice_crream_machine

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Ice_crream_machine` |
| template path | `agent/templates/pictureX_0611_Ice_crream_machine.py` |
| stage | `TEMPLATE_DRAFT` |
| status | `implemented` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 |
| read_count | 5 |
| read_scope | all 5-star samples in this category |
| source_index_policy | adopted module sources indexed in `0611__requested_batch_variant_source_map.md` |

## 核心身份
Small hand-operated ice cream / frozen dessert machine: tub or churn body, lid/head, rotary hand drive, internal dasher/cutter, and plausible bearing/support path. It must not become a blender, drink dispenser, generic bucket, or coffee grinder.

## 槽位 + 候选模块表
### Slot A：body_family
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| cutter_box | forked_anchor | `rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0` | `_make_chassis:L55-L112` | eligible if compatible | rectangular chassis, feed head, cutter-machine silhouette |
| bucket_canister | forked_anchor | `rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80` | `_frustum_shell:L22-L45` | eligible if compatible | round bucket/canister body with rim |
| freezer_bowl | forked_anchor | `rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c` | `_bowl_shape:L68-L78` | eligible if compatible | low rounded freezer bowl with top head |
| framed_tub | forked_anchor | `rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469` | `_make_tub_shell:L60-L72` | eligible if compatible | wooden tub inside support rails |
| open_churner_stand | forked_anchor | `rec_ice_crream_machine_var_open_churner_stand` | generated variant | eligible if compatible | open bucket-on-stand churner |

### Slot B：drive_style
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| side_handwheel | forked_anchor | source 004 | `_make_handwheel:L165-L177` | eligible if compatible | side rotary wheel |
| side_crank | forked_anchor | sources 001/003 | `_make_crank:L130-L140` | eligible if compatible | crank throw with grip |
| top_crank | forked_anchor | source 002 | `_crank_shape:L81-L94` | eligible if compatible | top/offset rotary crank |

## 槽位图（slot graph）
pattern: mixed

`body_family` owns fixed tub/head/dasher visuals. `hinged_lid` attaches to the tub top with a revolute X-axis hinge. `drive_style` attaches to the body by a revolute shaft axis selected by drive placement. All drive modules share the same bearing envelope and are compatible with every body family.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| body_family/* | body part, tub/case, base, internal dasher shaft | root support plane | top lid hinge face, side/top drive bearing |
| drive_style/* | `rotary_drive` part + revolute joint | side or top bearing origin | crank/handwheel motion range `[-pi, pi]` |
| access lid | `hinged_lid` part + revolute joint | tub rim hinge | opening range `[0, lid_swing]` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_family | enum | 5 candidates | bucket_canister | choice | sampled deterministically | source map |
| drive_style | enum | 3 candidates | side_crank | choice | sampled deterministically | source map |
| radius | float | [0.13, 0.30] | 0.22 | independent | clamp | source proportions |
| width | float | [0.38, 0.82] | 0.58 | independent | clamp | source proportions |
| height | float | [0.40, 0.92] | 0.62 | independent | clamp | source proportions |
| crank_radius | float | [0.06, 0.19] | 0.12 | independent | clamp | crank sources |
| lid_swing | float | [0.50, 1.55] | 1.15 | independent | clamp | lid/head sources |

## 编译预算 / compile budget
Per-seed budget: 20s. Geometry is primitive-only boxes/cylinders with no booleans or high tessellation.

## Multiplicity / Copy Logic
- 无模板级数量轴；dasher blades and perforation-like details are fixed module-local visuals.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | box machine, bucket, bowl, framed tub, open stand |
| multiplicity | 无 | no product-domain count parameter |
| ② 关节类型 | 有 | revolute lid and revolute drive |
| ③ 主体形态家族 | 有 | cutter box, bucket canister, freezer bowl, framed tub/open stand |
| ④ 表面装饰 | 有 | rims, head blocks, wood/metal bands as host visuals |
| ⑤ 尺寸/行程 | 有 | radius, width, height, crank radius, lid swing |
| ⑥ 涂装 | 有 | oak, painted, industrial, walnut |

## 采样与覆盖审计
Total combinations: 5 x 3 x 4 palettes = 60 plus continuous scales. Procedural sampler chooses body, drive, palette, then clamps dimensions. Seeds 0-35 should show every body family and drive; 0-999 is report-only maturity audit.

## Validator
- `slot_choices_for_seed` returns body_family, drive_style, palette_style.
- `build_*` emits body, hinged_lid, rotary_drive and non-fixed joints.
- Motion ranges are clamped before building.

## Reject cases
- Missing tub/canister/bowl identity.
- Drive becomes electric appliance or blender-like blade jar.
- Lid/drive floats without bearing relationship.
