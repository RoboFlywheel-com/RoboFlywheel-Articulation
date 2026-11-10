# Sci-fi Satellite Dish Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Urban_Environment_sci_fi_satellite_dish` |
| template path | `agent/templates/Urban_Environment_sci_fi_satellite_dish.py` |
| test path (optional) | inline `run_satellite_dish_tests` |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved_by_user_for_rebuild` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | parent + all converged variants listed in `articraft_data/picture_expansion/template_source_maps/Urban_Environment__sci-fi_satellite_dish.md` |
| source_index_policy | only adopted module sources are indexed below |

Adopted source records: parent `rec_sci-fi-satellite-dish-comm-unit-a-dark-matte-rec_20260612_113210_418481_e7ad375a`; dish-form variants `rec_satellite_dish_var_hex_faceted`, `rec_satellite_dish_var_segmented_petal`, `rec_satellite_dish_var_flat_phased_array`; panel-N variants `rec_satellite_dish_var_panels_n8/_n16/_n24`; mount variants `rec_satellite_dish_var_dual_arm_fork`, `rec_satellite_dish_var_tilt_tripod`; feed variants `rec_satellite_dish_var_cassegrain`, `rec_satellite_dish_var_offset_feed_arm`.

## 核心身份

Sci-fi communications satellite dish comm unit: a greebled dark equipment base on the ground, an azimuth REVOLUTE yoke, an elevation REVOLUTE dish/array head, and a signal aperture. The identity is not a home TV antenna and not a decorative dish: every seed must preserve aiming with `azimuth_rotation` around +Z and `elevation_tilt` around horizontal Y. Non-flat forms are circular parabolic reflectors; `flat_phased_array` is the only rectangular aperture and has no external feed horn.

Hard visual constraints from source inspection:
- Non-flat `dish_form` must read as one continuous circular dish silhouette.
- `hex_faceted` means source-style thin hex mirror facets tiled on the paraboloid, not circular pads, boxes, or rear-mounted arrays.
- `segmented_parabolic` and `petal_segmented` mean thin shell sectors/petals following `z=r^2/(4f)`, not chunky slabs.
- Square radiator grids belong only to `flat_phased_array`.
- The mount post/yoke may lean only when the source module does; no unsupported bent rod that visually misses the bearing/knuckle.

## 槽位 + 候选模块表

### Slot A：dish_form
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `segmented_parabolic` | `rec_satellite_dish_var_panels_n16` | L313-L434 | eligible if compatible | Circular parabolic reflector split into loop-emitted thin-shell sector `panel_{i}` with radial `seam_{i}` ribs; N is sampled from the panel multiplicity axis. |
| `hex_faceted` | `rec_satellite_dish_var_hex_faceted` | L51-L138, L421-L449 | eligible if compatible | Dark backing shell + many thin hex facets placed by `_hex_grid_centers` and tangent-oriented by `_hex_facet_mesh`; no rear square block field. |
| `petal_segmented` | `rec_satellite_dish_var_segmented_petal` | L311-L437 | eligible if compatible | Deployable-style radial petal reflector; each `panel_{i}` is a curved pie wedge with small hub `bolt_{i}`. |
| `flat_phased_array` | `rec_satellite_dish_var_flat_phased_array` | L261-L395 | eligible if compatible only with `feed=none` | Rectangular array plate + shallow back housing + four-edge trim + square radiator `panel_{i}` grid; no concave bowl. |

### Slot B：mount_gimbal
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_rear_yoke` | parent + dish variants | parent L240-L253; variants e.g. hex L333-L346 | eligible if compatible | Single rear yoke post, top knuckle, captured trunnion; default az/el support. |
| `dual_arm_fork` | `rec_satellite_dish_var_dual_arm_fork` | source map Slot B; model fork-arm loop | eligible if compatible | Two symmetric fork arms with bearing housings around a shared elevation shaft. |
| `tilt_tripod` | `rec_satellite_dish_var_tilt_tripod` | source map Slot B; tripod leg loop | eligible if compatible | Three fixed tripod support legs on the base plus a central mast and tilt knuckle. |

### Slot C：feed
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `center_fed_horn` | parent | parent dish assembly/feed region L271-L435 | eligible if `dish_form != flat_phased_array` | Prime-focus axial boom and horn in front of the parabolic reflector. |
| `cassegrain_sub` | `rec_satellite_dish_var_cassegrain` | source map Slot C | eligible if `dish_form != flat_phased_array` | Subreflector disc at focus with looped struts to the rim and recessed vertex feed. |
| `offset_feed_arm` | `rec_satellite_dish_var_offset_feed_arm` | source map Slot C | eligible if `dish_form != flat_phased_array` | Lower-rim swept offset arm with clamps and off-axis horn. |
| `none` | `rec_satellite_dish_var_flat_phased_array` | L261-L395 | eligible only if `dish_form=flat_phased_array` | Flat array aperture has no external feed. |

## 槽位图（slot graph）

pattern: `mixed`

`pedestal_base` --[`azimuth_rotation` REVOLUTE +Z]--> `azimuth_yoke` --[`elevation_tilt` REVOLUTE ±Y]--> `dish_assembly`

Slot B chooses the visible azimuth/elevation support hardware. Slot A and Slot C are sibling modules emitted as visuals inside `dish_assembly`; Slot C is gated by Slot A. Slot D (`panel_count`) is a multiplicity axis internal to Slot A. Decorative base greebles, panels, bolts, seams, radiator pads, and feed clamps are `parent.visual(...)`, not FIXED parts.

## 每槽位 Module Emits / Interfaces

### Slot A / module `segmented_parabolic`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dish_assembly` visuals `reflector_shell`, `reflector_rim`, `panel_{i}`, `seam_{i}` | panels_n16 L313-L434 |
| internal joints | none | panels are rigid visuals |
| upstream interface | elevation shaft in `dish_assembly` at yoke knuckle | parent/variants shared az-el chain |
| downstream interface | feed anchor along parabola axis +X, focus `focal` | parent feed |

### Slot A / module `hex_faceted`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `backing_shell`/`reflector_shell`, `reflector_rim`, many thin `panel_{i}` hex facets | hex L51-L138, L421-L449 |
| internal joints | none | facets are rigid visuals |
| upstream interface | same elevation shaft | shared az-el chain |
| downstream interface | same focus axis for real feeds | parent feed |

### Slot A / module `petal_segmented`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `reflector_shell`, petal `panel_{i}`, hub `bolt_{i}`, `reflector_rim` | petal L311-L437 |
| internal joints | none | rigid deployable-looking dish in this asset family |
| upstream interface | same elevation shaft | shared az-el chain |
| downstream interface | same focus axis | parent feed |

### Slot A / module `flat_phased_array`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `array_plate`, `back_housing`, `trim_*`, radiator `panel_{i}`, `array_neck`, trunnion shaft | flat L261-L395 |
| internal joints | none | array plate is rigid |
| upstream interface | elevation shaft/yoke knuckle captured by `panel_neck` | flat L371-L389 |
| downstream interface | none; forces `feed=none` | flat source |

### Slot B / modules
| emits | 描述 | 来源 |
|---|---|---|
| `single_rear_yoke` | `azimuth_yoke` with collar, post, top link/knuckle | parent L240-L253 |
| `dual_arm_fork` | two fork arms/bearings around horizontal elevation shaft | source map Slot B |
| `tilt_tripod` | three fixed tripod legs plus central mast/knuckle | source map Slot B |
| joints | all emit `azimuth_rotation`; `dish_assembly` emits `elevation_tilt` to chosen yoke | source map identity |

### Slot C / modules
| emits | 描述 | 来源 |
|---|---|---|
| `center_fed_horn` | axial boom + feed horn + tip | parent dish feed |
| `cassegrain_sub` | subreflector disc + `subreflector_strut_{i}` + vertex feed | source map Slot C |
| `offset_feed_arm` | lower rim arm + `arm_clamp_{i}` + offset horn | source map Slot C |
| `none` | no feed visuals | flat L261-L395 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `dish_form` | enum | 4 modules above | `segmented_parabolic` | choice | deterministic sampler; `flat_phased_array -> feed=none` | Slot A |
| `mount_gimbal` | enum | 3 modules above | `single_rear_yoke` | choice | all preserve azimuth/elevation chain | Slot B |
| `feed` | enum | `center_fed_horn`, `cassegrain_sub`, `offset_feed_arm`, `none` | `center_fed_horn` | conditional | `none` only for flat; non-flat `none` resolves to center feed | Slot C |
| `panel_count` | int | segmented 8/16/24; petal 8/12/16; hex rings 3/4/5; flat 24/32/40/48 | 16 | conditional | constrained by `dish_form` | Slot D |
| `dish_radius` | float | [0.27,0.34] m | 0.30 | independent | clamp; drives reflector, feed, and panel geometry | sources nominal 0.30 |
| `focal` | float | [0.145,0.190] m | 0.165 | inequality | clamp to `[0.42R,0.72R]` | parent/variants |
| `mount_lift` | float | [0.30,0.38] m | 0.34 | independent | keeps lower rim clear of yoke/base | parent rest pose |
| `palette_style` | enum | 4 sci-fi material sets | `dark_teal` | choice | sampled per seed; all visuals use named materials | parent/variants color families |

## Multiplicity / Copy Logic

- `count_param`: `panel_count`.
- `N_range`: segmented `{8,16,24}`; petal `{8,12,16}`; hex ring count `{3,4,5}` converted to facet count; flat grid `{24,32,40,48}`.
- copied object: `panel_{i}` reflector sector / petal / hex facet / radiator pad; plus `seam_{i}` for segmented and `bolt_{i}` for petal.
- naming: stable zero-based `panel_{i}`, `seam_{i}`, `bolt_{i}`.
- placement: segmented/petal are full circular rings on paraboloid; hex uses concentric hex-grid centers clipped by circular aperture; flat uses row/column grid on array plate.
- joint policy: copied objects are rigid visuals in `dish_assembly`; no FIXED joints for decorative panels.
- source/gating: N=8/16/24 comes from panel variants; hex/petal/flat copy logic comes from their specific source records.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + 5★来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | moving part graph | 有 | mount changes single yoke / dual fork / tripod support; all keep base→azimuth→elevation→head. |
| └ multiplicity | 同构件 ×N | 有 | `panel_count`, `subreflector_strut_{i}`, `arm_clamp_{i}`, tripod legs; see §8. |
| ② 关节类型 | joint type/axis | 有 | azimuth REVOLUTE +Z and elevation REVOLUTE ±Y always present; no prismatic/continuous in this small class. |
| ③ 形状家族 | aperture/reflector profile | 有 | circular segmented, hex faceted circular, petal segmented circular, rectangular flat phased array. |
| ④ 表面装饰 | greebles/panels | 有 | base grille/ports/glow strips; panel seams/bolts/facets/pads must conform to host surface. |
| ⑤ 尺寸/行程 | continuous scale/range | 有 | dish radius, focal, mount lift, elevation range; resolve prevents impossible proportions. |
| ⑥ 涂装 | material/color | 有 | dark teal, military green, desert tan, deep navy; sampled per seed. |

## 拓扑多样性审计

总组合数：dish_form 4 × mount_gimbal 3 × feed 3 legal non-flat + flat-none combinations × N samples ≈ 108 legal families. `flat_phased_array` gates `feed=none`; non-flat gates `feed!=none`.


seed_domain_policy：procedural_first. `config_from_seed(seed)` samples dish form first, then compatible feed, mount, N, proportions, and palette. `resolve_config` clamps dimensions and enforces compatibility. No curated modulo table.

Topology target：legal topology count is below 300 only if palette is excluded and N is ignored; this class has a fixed two-joint aiming spine by identity, so diversity comes from aperture, mount, feed, and panel multiplicity rather than new joint chains.（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | sample Slot A → gated Slot C → Slot B → N → safe scales/palette | `slot_choices_for_seed` matches build |
| compatibility matrix | flat array iff feed none; non-flat iff real feed; all mount variants attach to elevation shaft | no floating feed, no concave shell on flat array |
| controlled local variation | radius/focal/mount_lift only; all clamped in `resolve_config` | circular dish remains circular, yoke captures trunnion |
| regression overrides | none | not allowed as main domain |
| random sweep | seeds 0-49 for pass, then viewer/batch selected seeds | module diversity, collision, support, visual identity |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| dish_form | 4 | yes | yes | includes flat gate |
| mount_gimbal | 3 | yes | yes | fixed two-joint spine |
| feed | 4 | yes | yes | `none` only flat |
| panel_count | 3+ | yes | yes | multiplicity axis |

## Validator

- `azimuth_rotation` exists, is REVOLUTE, and uses +Z.
- `elevation_tilt` exists, is REVOLUTE, and uses horizontal Y.
- Non-flat forms contain `reflector_shell` and `reflector_rim`; flat form contains `array_plate` and no reflector shell.
- `flat_phased_array` contains square radiator `panel_{i}` grid and no feed horn/subreflector/offset horn.
- `hex_faceted` contains many thin hex `panel_{i}` facets spread across a circular aperture; no round pad field, no rear square matrix.
- `segmented_parabolic`/`petal_segmented` panels follow the circular paraboloid and preserve a circular outline.
- Yoke/mast/fork/tripod visually supports the elevation shaft; no obviously missing/airborne rod.
- Decorative panels, seams, bolts, grilles, ports are visuals on parent parts, not separate fixed parts.

## Reject cases

- Non-flat seed looks like a rectangular array or a box field behind the dish.
- Hex seed uses circular pads, thick cylinders, extruded blocks, or incomplete non-circular rings instead of source-style hex facets.
- Petal/segmented seed has chunky slab panels rather than thin shell sectors.
- Flat array has a front feed horn or concave reflector shell.
- Support rod visually misses the knuckle/bearing or leans through the aperture in an unsupported way.
- Removing either azimuth or elevation joint.
- Replacing Lathe/Mesh reflector sources with crude flat boxes for non-flat forms.
- Turning the sci-fi comm unit into a domestic TV dish or roof antenna.

## 与相邻类别的边界

- 不该混入：`Urban_Environment_Roof_antena`（小型屋顶天线/电视天线，高杆和屋顶安装语义不同）。
- 不该混入：radio telescope observatory（可参考 az/el support，但本类必须保留 sci-fi equipment base and greebles）。
- 不该混入：generic solar panel / flat display（只有 `flat_phased_array` 可以是矩形阵列，且仍需 az/el comm-unit identity）。

## 审核记录

- 2026-06-30：用户要求删除旧 spec/template 并按已有 skill 重做；本 spec 依据 source map 和 5★ source snippets 重写，重点约束 dish 表面真实来源和 flat-array 互斥 gate。
