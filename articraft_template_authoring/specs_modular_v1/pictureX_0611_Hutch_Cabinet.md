# pictureX_0611_Hutch_Cabinet

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Hutch_Cabinet` |
| template path | `agent/templates/pictureX_0611_Hutch_Cabinet.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in `category_slug=picturex_0611__hutch_cabinet__001__png` |
| source_index_policy | every adopted module source is indexed in the slot tables and Module Source Index |

11 个 5★ 来源均来自 source map `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Hutch_Cabinet.md`，并已在 downstream `data/records/` 中以 rating=5 存在。`external examples --rating-min 5 --category-slug picturex_0611__hutch_cabinet__001__png --limit 50` 返回 `total_matches=11`。旧的 `pictureX_0611_Hutch_Cabinet` slug 查询为空是同步 metadata 继承了原始 image category slug；采用实际 record `category_slug` 作为 P2 gate。

读取的源码结构：origin 直线高柜 `model.py:L235-L376`；upper glass hinged `L268-L405`；open upper shelves `L235-L331`；tambour roll front `L235-L326`；lower drawer bank `L235-L382`；lower double door base `L248-L394`；drop-front secretary `L235-L439`；20260714 supplement lift-up flap `L328-L494`；sliding glass upper doors `L263-L486`；plate rack back `L263-L436`；wine cubby lower grid `L235-L436`。Blocked corner hutch has no committed record dir and is excluded per source map.

## 核心身份

Hutch cabinet = freestanding/tall furniture case with a lower storage base plus an upper hutch/display/storage section. It must read as furniture-scale cabinetry: plinth/crown/carcass, shelves or plate rack, paneled or glazed upper fronts, lower doors/drawers/cubbies, and real storage motion when applicable. It must not collapse into a plain bookcase, kitchen island, appliance garage, locker, vitrine-only case, wine rack alone, sideboard-only cabinet, or rolltop desk.

## 槽位 + 候选模块表

### Slot A：`upper_front`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_glass` | forked_anchor/origin_anchor | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba; rec_picturex0611_hutch_cabinet_fork_upper_glass_hinged_doors_20260713 | origin `L336-L361`; hinged fork `L369-L395` | eligible if compatible | two/three upper framed glass child doors, REVOLUTE vertical hinge joints, mullions/glass/pulls |
| `open_shelves` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_open_upper_shelves_20260713 | `L235-L331` | eligible if compatible | removes upper moving front, exposes shelf bays/dividers/back panel; no upper-front child joints |
| `tambour_roll` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_tambour_roll_front_20260713 | `L299-L317` | eligible if compatible | slatted roll/tambour child panel riding vertical PRISMATIC track |
| `sliding_glass` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_sliding_glass_upper_doors_20260714 | `L429-L486` | eligible if compatible | bypass glass panels in upper top/bottom tracks, PRISMATIC horizontal slides |
| `lift_up_flap` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_lift_up_flap_upper_20260714 | `L429-L483` | eligible if compatible; gated away from `drop_front_secretary` with tambour/lift stack | top-hinged glass flap doors with stays, REVOLUTE horizontal hinge |

### Slot B：`upper_back`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_shelves` | origin_anchor | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba | `L293-L311` | eligible if compatible | standard upper display shelves/back panel, no plate grooves |
| `plate_rack` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_plate_rack_back_20260714 | `L301-L347` | eligible if compatible | upper back becomes plate rack with loop-emitted vertical grooves/dividers and retaining rail |

### Slot C：`lower_storage`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `four_doors` | origin_anchor | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba | `L315-L332` | eligible if compatible | four lower paneled REVOLUTE doors across base |
| `drawer_bank` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_lower_drawer_bank_20260713 | `L235-L382` | eligible if compatible | loop-emitted lower drawers with PRISMATIC slide joints; N = 1-4 in template |
| `double_door_base` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_lower_double_door_base_20260713 | `L335-L394` | eligible if compatible | two wide lower hinged doors, shelves behind, reduced drawer emphasis |
| `drop_front_secretary` | forked_anchor / compatibility_probe | rec_picturex0611_hutch_cabinet_fork_drop_front_secretary_20260713 | `L393-L439` | eligible only with straight hutch carcass; sampler gates away from tambour/lift stack | hinged writing flap in mid/lower section with cubby dividers and support-stay detail |
| `wine_cubby_grid` | forked_anchor | rec_picturex0611_hutch_cabinet_fork_wine_cubby_lower_grid_20260714 | `L301-L337` | eligible if compatible | loop-emitted lower wine-cubby grid cells, static host visuals plus optional side door |

### Slot D：`palette_style`

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `walnut` | record_only | origin / most forks use dark walnut + brass + smoked glass | origin `L246-L250`; forks same material block | eligible | dark wood body, brass hardware, smoked glass |
| `oak` | world_knowledge_extrapolation(⑥ only) | source map palette notes warm wood; hutch furniture domain | n/a; template material table | eligible | warm oak body, lighter panel, silver/brass hardware |
| `painted` | record_only + world_knowledge_extrapolation(⑥ only) | lower_double_door_base painted cream interior `L259-L264`; source map painted finish | `L259-L264` | eligible | cream painted cabinet finish with muted metal hardware |
| `slate` | world_knowledge_extrapolation(⑥ only) | source map allows painted/dark hardware variants | n/a; template material table | eligible | dark painted/slate case with brass-like hardware |
| `jeweler` | world_knowledge_extrapolation(⑥ only) | dark wood/glass/brass source extrapolated to display-cabinet finish | n/a; template material table | eligible | very dark display-case finish with greenish glass |

## 槽位图（slot graph）

pattern: `mixed`

`carcass` is the rooted host. `upper_back` and static trim are host visuals on `carcass`; `upper_front` and `lower_storage` emit parallel child parts only when their candidate has real motion.

`carcass.upper display bay` --[`upper_front` hinge/slide/flap/tambour joint, front face/track/hinge plane]--> `upper_front child parts`

`carcass.upper back panel` --[host-derived fixed shelf/back surface]--> `upper_back` visuals (`plain_shelves` or `plate_rack`)

`carcass.lower base bay` --[`lower_storage` hinge/slide/flap joint, face-frame/front track/contact plane]--> `lower_storage child parts`

Compatibility / degrade:
- `drop_front_secretary` remains in the straight-hutch domain; if sampled with `tambour_roll` or `lift_up_flap`, `resolve_config` degrades upper_front to `hinged_glass` so two large vertical-front flap mechanisms do not stack in one facade.
- `open_shelves` has no upper moving child; lower storage still guarantees at least one non-fixed hutch mechanism.
- `plate_rack` is interior/back-only and compatible with every upper-front mechanism; it is host visual geometry so no joint graph changes.
- `wine_cubby_grid` is lower-base static multiplicity plus an optional lower side door, compatible with all non-secretary upper fronts.
- `corner_hutch_carcass` is excluded because all 20260713 fork attempts exited 143 and no record directory exists.

## 每槽位 Module Emits / Interfaces

### Slot A / module `hinged_glass`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_glass_door_i` child parts with frame/glass/mullion/pull visuals | origin `L336-L361`; hinged fork `L369-L395` |
| internal joints | `upper_glass_door_i_hinge`, REVOLUTE around vertical z, closed→~83 degrees | origin `L354-L361` |
| upstream interface | carcass front upper bay stile/pilaster; hinge origin on front face | origin `L336-L361` |
| downstream interface | none | source topology |

### Slot A / module `open_shelves`
| emits | 描述 | 来源 |
|---|---|---|
| parts | no separate parts; `open_shelf_divider_i` and `display_shelf_i` host visuals | open shelves source `L235-L331` |
| internal joints | none for upper front | source topology |
| upstream interface | carcass upper bay/back panel | source topology |
| downstream interface | none | source topology |

### Slot A / module `tambour_roll`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_tambour` child with loop-emitted `tambour_slat_i` | tambour source `L299-L317` |
| internal joints | `upper_tambour_slide`, PRISMATIC vertical +z | tambour source `L307-L317` |
| upstream interface | upper top/bottom guide tracks on carcass front | tambour source `L299-L317` |
| downstream interface | none | source topology |

### Slot A / module `sliding_glass`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sliding_glass_panel_0/1` bypass glass panels | sliding source `L429-L486` |
| internal joints | two horizontal PRISMATIC slide joints | sliding source `L429-L486` |
| upstream interface | staggered top/bottom front tracks | sliding source `L429-L486` |
| downstream interface | none | source topology |

### Slot A / module `lift_up_flap`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lift_up_flap_i` child panels with glass and support stays | lift-up source `L429-L483` |
| internal joints | `lift_up_flap_i_hinge`, REVOLUTE around horizontal x | lift-up source `L437-L447` |
| upstream interface | top hinge rail on upper front bay | lift-up source `L429-L483` |
| downstream interface | none | source topology |

### Slot B / modules `plain_shelves` and `plate_rack`
| emits | 描述 | 来源 |
|---|---|---|
| parts | no separate parts; shelf, groove, retaining rail visuals on carcass | origin `L293-L311`; plate rack `L301-L347` |
| internal joints | none | source topology |
| upstream interface | upper back panel / shelf plane | source topology |
| downstream interface | consumed by upper_front as shared bay volume | source topology |

### Slot C / module `drawer_bank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_drawer_i` or `secretary_lower_drawer_i`, each with front, box, pull | origin `L365-L376`; drawer bank fork `L235-L382` |
| internal joints | PRISMATIC slide joints along front/back y axis | origin `L369-L376` |
| upstream interface | lower base face frame / guide plane | source topology |
| downstream interface | none | source topology |

### Slot C / module `double_door_base` / `four_doors`
| emits | 描述 | 来源 |
|---|---|---|
| parts | lower hinged paneled doors | origin `L315-L332`; double door fork `L335-L394` |
| internal joints | REVOLUTE vertical door hinges | origin `L325-L332`; double door `L346-L354` |
| upstream interface | lower face-frame pilaster/stile | source topology |
| downstream interface | none | source topology |

### Slot C / module `drop_front_secretary`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drop_front_secretary_flap`, optional small drawers, cubby divider host visuals | drop-front source `L393-L439` |
| internal joints | REVOLUTE horizontal flap hinge plus optional drawer slides | drop-front source `L431-L439` |
| upstream interface | lower/mid carcass rail and secretary cubby bay | source topology |
| downstream interface | none | source topology |

### Slot C / module `wine_cubby_grid`
| emits | 描述 | 来源 |
|---|---|---|
| parts | cubby grid is host visual; optional lower hinged side door | wine cubby source `L301-L337` |
| internal joints | optional lower door REVOLUTE; cubbies are static host visuals | source topology |
| upstream interface | lower base bay/back plane | source topology |
| downstream interface | none | source topology |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `upper_front` | enum | `hinged_glass`, `open_shelves`, `tambour_roll`, `sliding_glass`, `lift_up_flap` | `hinged_glass` | choice + conditional | if `lower_storage=drop_front_secretary` and upper is `tambour_roll/lift_up_flap`, degrade to `hinged_glass` | Slot A |
| `upper_back` | enum | `plain_shelves`, `plate_rack` | `plain_shelves` | choice | plate rack only adds host visuals | Slot B |
| `lower_storage` | enum | `four_doors`, `drawer_bank`, `double_door_base`, `drop_front_secretary`, `wine_cubby_grid` | `four_doors` | choice | sampled as parallel lower module | Slot C |
| `palette_style` | enum | `walnut`, `oak`, `painted`, `slate`, `jeweler` | `walnut` | choice | sampled per seed; every material comes from selected palette dict | Slot D / source map ⑥ |
| `shelf_count` | int | 2-4 | 2 | independent | clamp to `[2,4]`; affects display shelf count and plate rack groove count lower bound | origin shelves + open shelves |
| `lower_drawer_count` | int | 1-4 | 3 | conditional | clamp to `[1,4]`; only realized by drawer bank and secretary lower drawers | lower_drawer_bank |
| `upper_leaf_count` | int | 2-3 | 3 | conditional | sliding/lift-up resolve to 2; hinged resolves 2-3 | origin + hinged/sliding/lift sources |
| `width` | float | [0.74, 1.12] m | 0.94 | independent | clamp in `resolve_config`; all bay widths derived from it | source proportions |
| `depth` | float | [0.30, 0.44] m | 0.36 | independent | clamp in `resolve_config`; drawer travel ≤ 0.52*depth | source proportions |
| `lower_height` | float | [0.48, 0.70] m | 0.58 | independent | lower bay bounds derived | source proportions |
| `upper_height` | float | [0.68, 1.00] m | 0.88 | independent | total_height = lower_height + upper_height + 0.04 | source proportions |
| `drawer_travel` | float | [0.10, 0.24] m | 0.18 | inequality | `drawer_travel ≤ 0.52 * depth`; projected in `resolve_config` | drawer sources |
| door/flap/tambour travel | float | derived | — | equation | door swing = 1.45 rad, lift flap = 1.15 rad, tambour vertical travel = min(0.24, 0.34*bay_h), sliding travel = 0.25*bay_w | mechanism sources |

## 7.5 编译预算 / compile budget

每 seed 目标 ≤20s。依据：模板主要为 Box/Cylinder host visuals 和少量 moving child parts；未复用 source 中 heavy CadQuery cubby mesh，wine cubby grid 用 loop-emitted rectangular dividers表达，避免复杂布尔。sweep watchdog 使用 `--compile-timeout 120`。

## Multiplicity / Copy Logic

- `shelf_count`: N_range `[2,4]`; copied object `display_shelf_i`; placement is evenly spaced within upper bay; fixed host visuals on `carcass`; sources origin/open shelves/plate rack.
- `lower_drawer_count`: N_range `[1,4]`; copied object `lower_drawer_i`; each drawer is a child part with PRISMATIC slide; drawer height is derived from lower bay; sources lower drawer bank and origin apron drawers.
- `upper_leaf_count`: N_range `[2,3]`; copied object `upper_glass_door_i` for `hinged_glass`; sliding/lift-up resolve to 2 panels/flaps; sources origin, upper glass hinged, sliding glass, lift-up flap.
- `plate_groove_count`: derived `max(5, shelf_count+4)`; host visual grooves, no new joint; source plate rack back.
- `wine_cubby_grid`: implemented as 3×4 grid host visuals, matching accepted 20260714 anchor; grid count is not sampled wider in first template because source-backed accepted anchor only confirms 3×4.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | `open_shelves` removes upper front child parts; `plate_rack` changes upper back storage skeleton; `wine_cubby_grid` adds lower grid structure; all source-backed: open shelves, plate rack, wine cubby |
| └ multiplicity | 同构件 ×N | 有 | shelves 2-4, lower drawers 1-4, upper leaves 2-3, plate grooves ≥5, wine cubby 3×4; see §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE hinged glass/lower doors/drop-front/lift-up flap; PRISMATIC drawers/tambour/sliding glass; all forked/source-backed |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有（degraded） | `straight_high_hutch` only implemented. `corner_hutch_carcass` is excluded/blocked (no committed record after exit 143 retries). Form family is documented as degraded rather than invented; category diversity is carried by functional upper/lower modules. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | crown molding, pilasters, mullions, pulls, tambour slats, plate grooves, cubby dividers; host visuals, source-backed or record_only from all 11 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | width/depth/lower/upper height ranges; drawer travel `[0.10, min(0.24,0.52*depth)]`; door swing 1.45 rad; flap 1.15 rad; tambour and sliding travel derived from bay size. motion_test_plan: sampled pose overlap + targeted visible travel checks for first non-fixed mechanisms. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `walnut`, `oak`, `painted`, `slate`, `jeweler`; material families cover wood/painted/glass/metal in ≥5 colorways; sampled per seed via `palette_style` |

## 采样与覆盖审计

总组合数：5 `upper_front` × 2 `upper_back` × 5 `lower_storage` × 3 shelf bands × 4 drawer bands × 2 upper leaf bands × 5 palettes = 3000 raw tuples. Compatibility gate degrades `drop_front_secretary + {tambour_roll,lift_up_flap}` to `hinged_glass`, so effective topology tuples remain well above 300 and within stable straight-hutch scope.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` samples all slots with deterministic `random.Random(seed)`, including seed 0. `resolve_config` clamps continuous dimensions, projects drawer travel to depth, and performs the secretary upper-front degrade. Sweep uses 0-35 plus corner stage with the mandated thread caps. Viewer probe should choose seeds from `slot_choices_for_seed` so every upper_front, upper_back, lower_storage, and palette appears.

Topology target：1000-seed slot choice tuple coverage ≥300 expected; raw domain is 3000 and compatibility-gated domain remains high. Report-only axis realization must show all 5 upper fronts, both upper backs, all 5 lower storage modules, and ≥3 palettes in 0-35/corner or follow-up seed probe.

Controlled local parameterization：width, depth, lower_height, upper_height are independent; total_height is derived; drawer_travel is inequality-projected to depth. Child part dimensions derive from bay width/height and cannot exceed carcass openings.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted procedural choices over `upper_front`, `upper_back`, `lower_storage`, multiplicities, palette | `slot_choices_for_seed` matches `model.meta["slot_choices"]` |
| compatibility matrix | secretary degrades away from upper tambour/lift stack; open shelves rely on lower moving module; plate rack compatible with all | no two large flap fronts fighting; at least one mechanism |
| controlled local variation | all moving modules derive bay sizes from resolved carcass | no floating doors/drawers, no impossible travel |
| regression overrides | none | procedural domain remains primary |
| random sweep | 0-35 + corner; small batch probe covers all slot values | pass/fail clusters, axis_realization, failed_corner_seeds |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| `upper_front` | 5 | yes | yes | includes all 20260714 upper candidates |
| `upper_back` | 2 | yes | no | source pool only confirms plain shelves and plate rack; documented degrade |
| `lower_storage` | 5 | yes | yes | includes drawer bank, doors, secretary, wine cubby |
| `palette_style` | 5 | yes | yes | ⑥-only palette parameter |

## Validator

- `slot_choices_for_seed` returns implemented module names for `upper_front`, `upper_back`, `lower_storage`, `shelf_count`, `lower_drawer_count`, `upper_leaf_count`, `palette_style`.
- `config_from_seed` uses deterministic procedural sampling for ordinary seeds including seed 0.
- `resolve_config` clamps dimensions, projects drawer travel, and applies only the documented secretary upper-front degrade.
- Every sampled config builds a tall hutch with `carcass`, `plinth`, `counter_deck`, `crown_cap`, upper shelves, and at least one non-fixed storage/opening mechanism.
- Moving child parts are doors/drawers/flaps/sliders/tambour only; static trim, shelves, plate grooves, cubbies, slats, and pulls are host or moving-part visuals, not decorative FIXED parts.
- Key joints have expected type / axis / range: doors REVOLUTE z, drawers PRISMATIC y, tambour PRISMATIC z, sliding glass PRISMATIC x, lift/drop flaps REVOLUTE x.
- Motion tests include sampled-pose overlap plus targeted visible travel for non-fixed joints.
- Palette is sampled per seed and all visuals use materials from the chosen palette.

## Reject cases

- Looks like a plain bookcase: no lower base storage mechanism or furniture face-frame.
- Vitrine-only display case: upper glass exists but lower cabinet base absent.
- Kitchen island/appliance garage/locker drift.
- Wine rack alone: wine cubby grid without hutch upper section.
- Rolltop desk: tambour or secretary consumes the identity and upper hutch disappears.
- Corner hutch or L-shaped carcass: blocked upstream, not implemented in this slug.
- Moving child has no visible hinge/track/guide support or travel clips through closed pose.
- Monochrome output across seeds because `palette_style` is not sampled or not used.

## 与相邻类别的边界

- 不该混入：`bookcase`（bookcases may have shelves but lack the lower cabinet base and moving furniture storage).
- 不该混入：`Cabinet_with_glass_lift_up_vitrine`（vitrine is primarily a glass display case; Hutch_Cabinet must keep lower base and upper hutch furniture identity).
- 不该混入：`Kitchen_cabinet` / appliance garage（built-in kitchen cabinetry lacks the freestanding hutch proportions/crown/plinth).
- 不该混入：`wine rack`（wine cubbies are optional lower inserts, not the entire object).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 20260714 anchors added: `sliding_glass_upper_doors`, `plate_rack_back`, `wine_cubby_lower_grid`, `lift_up_flap_upper`. Corner hutch remains excluded due blocked upstream record. |

## 模板实现备注（可选）

- Uses a parallel-children host pattern: all slots attach to one `carcass`.
- The template intentionally keeps the primary form family to straight high hutch because the only corner-body candidate is blocked; this is an explicit degrade, not a silent drop.
- If future source map adds a successful corner hutch or china-cabinet/body-form anchor, split or add a `body_form` slot before widening combinations.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | core/body | straight high hutch | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba | `L235-L376` | carcass proportions, shelves, lower/upper hinges, drawers, walnut/glass/brass |
| S2 | upper_front | hinged_glass | rec_picturex0611_hutch_cabinet_fork_upper_glass_hinged_doors_20260713 | `L268-L405` | glass hinged upper doors, hinge/mullion detail |
| S3 | upper_front | open_shelves | rec_picturex0611_hutch_cabinet_fork_open_upper_shelves_20260713 | `L235-L331` | open shelf hutch topology |
| S4 | upper_front | tambour_roll | rec_picturex0611_hutch_cabinet_fork_tambour_roll_front_20260713 | `L299-L317` | vertical prismatic tambour front and slats |
| S5 | lower_storage | drawer_bank | rec_picturex0611_hutch_cabinet_fork_lower_drawer_bank_20260713 | `L235-L382` | lower drawer multiplicity |
| S6 | lower_storage | double_door_base | rec_picturex0611_hutch_cabinet_fork_lower_double_door_base_20260713 | `L335-L394` | two wide lower doors, painted interior evidence |
| S7 | lower_storage | drop_front_secretary | rec_picturex0611_hutch_cabinet_fork_drop_front_secretary_20260713 | `L393-L439` | secretary flap/cubby compatibility probe |
| S8 | upper_front | lift_up_flap | rec_picturex0611_hutch_cabinet_fork_lift_up_flap_upper_20260714 | `L429-L483` | top-hinged upper glass flaps |
| S9 | upper_front | sliding_glass | rec_picturex0611_hutch_cabinet_fork_sliding_glass_upper_doors_20260714 | `L429-L486` | bypass sliding glass upper doors |
| S10 | upper_back | plate_rack | rec_picturex0611_hutch_cabinet_fork_plate_rack_back_20260714 | `L301-L347` | plate grooves and retaining rail |
| S11 | lower_storage | wine_cubby_grid | rec_picturex0611_hutch_cabinet_fork_wine_cubby_lower_grid_20260714 | `L301-L337` | lower cubby grid multiplicity |
