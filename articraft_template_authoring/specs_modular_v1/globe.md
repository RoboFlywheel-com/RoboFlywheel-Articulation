# Globe Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `globe` |
| template path | `agent/templates/globe.py` |
| test path | `tests/agent/test_globe_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 27 |
| read_count | 27 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / `prompt.txt` were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 21 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| base + meridian/yoke + globe | 13 | support -> meridian REVOLUTE or FIXED, meridian -> globe CONTINUOUS |
| base turntable + upper support + globe | 9 | base -> cradle/support CONTINUOUS and support -> globe CONTINUOUS |
| outer cradle + inner ring + globe | 2 | nested rings: outer cradle -> inner ring REVOLUTE, inner ring -> globe CONTINUOUS |
| wall arm / cantilever mount | 1 | wall arm -> meridian ring REVOLUTE, ring -> globe CONTINUOUS |
| globe + auxiliary date/knob ring | 2 | date ring or side knobs as additional CONTINUOUS parts |

被采纳样本逐条标注：
- `rec_globe_0002` — adopted：classic base + meridian + globe, continent meshes, meridian tilt REVOLUTE, globe spin CONTINUOUS。
- `rec_globe_0fc4e0cefb164176b77a767cd54d8816` — adopted：outer cradle + inner ring + globe, graticule and surface patch helpers。
- `rec_globe_1c4dea866a4340d792eedfb836a2c683` — adopted：partial support ring, globe spin, date ring CONTINUOUS。
- `rec_globe_35a4dc2d75144987ae667216dff6d05d` — adopted：fixed meridian ring, dense graticule/land patch functions。
- `rec_globe_bb728b5bb5b64df798b3ef95f629fb38` — adopted：base ring -> support pedestal CONTINUOUS, support -> globe CONTINUOUS, raised pedestal geometry。
- `rec_globe_dd09f51da481436e8a10f6b573d84744` — adopted：wall_arm + partial meridian frame + globe, wall-mounted variant。
- Remaining 21 samples — read but not adopted: repeat these support/globe spin families or differ only by material, axis sign, graticule density, or primitive implementation.

## 核心身份
`globe` 是一颗带地图/经纬线视觉的球体，安装在底座、meridian ring、cradle、pedestal 或 wall arm 上，并至少支持 globe 自身绕轴旋转。成熟默认域包含 static support、可选 meridian/cradle tilt/yaw stage、globe sphere with land/graticule visuals，以及 `globe_spin` CONTINUOUS 主关节。辅助 date ring、side knobs 或 base turntable 可以增加第二运动，但不能替代 globe 球体本身。

边界：
- 不包括纯球体摆件：必须有 stand/cradle/support 语义和 globe spin。
- 不混入 planetarium/orrery：多行星系统、轨道链不是本类别。
- 不混入 map stand：核心必须是球形 globe，不是平面地图。
- 不混入 gyroscope：ring 可以存在，但 globe 地图/经纬线身份必须明确。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_globe_0002` | `data/records/rec_globe_0002/revisions/rev_000001/model.py:L62-L94,L187-L393` | classic base/yoke arms/meridian/globe, continent meshes, two-joint REVOLUTE + CONTINUOUS chain |
| S2 | `rec_globe_0fc4e0cefb164176b77a767cd54d8816` | `data/records/rec_globe_0fc4e0cefb164176b77a767cd54d8816/revisions/rev_000001/model.py:L27-L126,L152-L296` | outer cradle, inner meridian ring, graticule mesh, nested ring topology |
| S3 | `rec_globe_1c4dea866a4340d792eedfb836a2c683` | `data/records/rec_globe_1c4dea866a4340d792eedfb836a2c683/revisions/rev_000001/model.py:L21-L178,L241-L421` | partial support ring, stand-heavy visual stack, globe spin plus date ring spin |
| S4 | `rec_globe_35a4dc2d75144987ae667216dff6d05d` | `data/records/rec_globe_35a4dc2d75144987ae667216dff6d05d/revisions/rev_000001/model.py:L36-L178,L191-L392` | fixed meridian ring, spherical land patches, graticule, dense globe visual style |
| S5 | `rec_globe_bb728b5bb5b64df798b3ef95f629fb38` | `data/records/rec_globe_bb728b5bb5b64df798b3ef95f629fb38/revisions/rev_000001/model.py:L36-L88,L106-L242` | base ring, rotating support pedestal, elevated support-to-globe CONTINUOUS chain |
| S6 | `rec_globe_dd09f51da481436e8a10f6b573d84744` | `data/records/rec_globe_dd09f51da481436e8a10f6b573d84744/revisions/rev_000001/model.py:L27-L103,L113-L324` | wall arm support, partial meridian ring, wall-mounted REVOLUTE + globe spin |

## 槽位 + 候选模块表

### Slot A：support_base
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `classic_desktop_base_yoke` | S1 | `model.py:L187-L260` | eligible if compatible | pedestal base, vertical yoke arms, brass feet/trim |
| `outer_cradle_stand` | S2 | `model.py:L152-L198` | eligible if compatible | outer ring/cradle and column support, inner ring pivots inside |
| `partial_ring_stand` | S3 | `model.py:L241-L340` | eligible if compatible | decorative stand with partial support ring, globe directly spins |
| `rotating_pedestal_base` | S5 | `model.py:L106-L187` | eligible if compatible | base_ring -> support_pedestal CONTINUOUS stage |
| `wall_arm_mount` | S6 | `model.py:L113-L159` | eligible if compatible | wall bracket/cantilever arm supporting meridian ring |

### Slot B：meridian_or_cradle
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `full_meridian_ring_tilting` | S1 | `model.py:L279-L331,L373-L393` | eligible if compatible | complete meridian ring with tick/axis cap, REVOLUTE tilt + globe spin |
| `inner_ring_nested_cradle` | S2 | `model.py:L205-L237,L281-L296` | eligible if compatible | inner_ring inside outer cradle, ring tilt then globe spin |
| `fixed_meridian_ring` | S4 | `model.py:L233-L276,L386-L392` | eligible if compatible | fixed meridian, only globe rotates |
| `no_ring_pedestal_spin` | S5 | `model.py:L144-L242` | eligible if compatible | support pedestal directly carries globe, no meridian ring |
| `partial_wall_meridian` | S6 | `model.py:L159-L194,L309-L324` | eligible if compatible | partial meridian frame on wall arm, REVOLUTE at arm |

### Slot C：globe_surface
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `continent_patch_globe` | S1 | `model.py:L80-L94,L346-L361` | eligible if compatible | ocean sphere with separate continent meshes and equator/latitude visual |
| `graticule_patch_globe` | S2 | `model.py:L54-L126,L244-L253` | eligible if compatible | graticule mesh plus surface patches |
| `dense_map_graticule` | S4 | `model.py:L36-L178,L276-L386` | eligible if compatible | many land patches, graticule, meridian tick visual |
| `minimal_ocean_globe` | S5 | `model.py:L199-L212` | eligible if compatible | simplified globe sphere with bands, useful for stable seed domain |

### Slot D：auxiliary_rotary
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | S1 | `model.py:L373-L393` | eligible if compatible | only meridian tilt + globe spin |
| `date_ring_spin` | S3 | `model.py:L391-L421` | eligible if compatible | date ring part spins around stand/globe axis |
| `rotating_support_stage` | S5 | `model.py:L227-L242` | eligible if compatible | base -> support_pedestal CONTINUOUS plus support -> globe CONTINUOUS |

## 槽位图（slot graph）
pattern = `mixed`

```
[Slot A support_base]
      ├── optional REVOLUTE/FIXED/CONTINUOUS --> [Slot B meridian_or_cradle]
      │             └── CONTINUOUS --> [Slot C globe_surface]
      └── optional CONTINUOUS --> [Slot D date_ring / rotating_support_stage]
```

主约束基准是 globe center、spin axis 和 support contact/pivot points。meridian ring radius must surround globe with clearance; yoke tips and globe axis caps must meet the same spin axis.

## 部件（Parts）

### Slot A / support_base
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `base` / `stand` / `outer_cradle` / `base_ring` / `wall_arm` | ~5-30 | desktop base, cradle stand, rotating pedestal, or wall arm root | S1 / S2 / S3 / S5 / S6 |

### Slot B / meridian_or_cradle
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `meridian` / `inner_ring` / `meridian_ring` / `support_pedestal` | ~2-16 | meridian ring, nested cradle ring, fixed support, or pedestal carrier | S1 / S2 / S4 / S5 / S6 |

### Slot C / globe_surface
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `globe` | ~3-30 | ocean sphere with continent patches, graticule, latitude/longitude bands | S1 / S2 / S4 / S5 |

### Slot D / auxiliary_rotary
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `date_ring` | ~1-3 | equatorial/desk date ring spinning around stand | S3 |
| `support_pedestal` | ~5-10 | rotating upper pedestal stage | S5 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `meridian_tilt` | REVOLUTE | A.base/cradle/wall_arm | B.meridian/inner_ring | `(1,0,0)` or `(0,1,0)` | `[-0.55, 0.55]` or reviewer-gated | meridian/cradle 倾角调节 | S1 / S2 / S6 |
| `meridian_fixed` | FIXED | A.base | B.meridian | n/a | n/a | fixed meridian ring variant | S4 |
| `support_yaw` | CONTINUOUS | A.base_ring | B.support_pedestal | `(0,0,1)` | unlimited | base turntable / rotating upper support | S5 |
| `globe_spin` | CONTINUOUS | B.meridian/support | C.globe | globe local polar axis, default `(0,0,1)` | unlimited | globe 自身主旋转 | S1 / S2 / S3 / S4 / S5 / S6 |
| `date_ring_spin` | CONTINUOUS | A.stand | D.date_ring | `(0,0,1)` | unlimited | auxiliary date ring spin | S3 |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_style` | enum | `classic_desktop`, `outer_cradle`, `partial_ring`, `rotating_pedestal`, `wall_arm` | `classic_desktop` | Slot A module | S1 / S2 / S3 / S5 / S6 |
| `meridian_style` | enum | `full_tilting`, `nested_inner`, `fixed_full`, `none_pedestal`, `partial_wall` | `full_tilting` | Slot B module; gated by support_style | S1 / S2 / S4 / S5 / S6 |
| `surface_style` | enum | `continent_patch`, `graticule_patch`, `dense_map`, `minimal_ocean` | `continent_patch` | Slot C module | S1 / S2 / S4 / S5 |
| `auxiliary_rotary` | enum | `none`, `date_ring`, `support_yaw` | `none` | Slot D module | S3 / S5 |
| `globe_radius` | float | `[0.32, 0.72]` | `0.5` | ring/base dimensions derive from radius | S1 / S2 |
| `axial_tilt_degrees` | float | `[15, 35]` | `23.5` | meridian/globe visual tilt; affects yoke contact points | S1 |
| `ring_clearance` | float | `[0.025, 0.09]` | `0.045` | meridian radius = globe_radius + clearance | S1 / S2 |
| `base_height` | float | `[0.12, 0.65]` | `0.28` | support style specific clamp | S1 / S5 |
| `graticule_density` | enum | `none`, `low`, `medium`, `high` | `medium` | surface visual count only | S2 / S4 |
| `land_patch_style` | enum | `simple_continents`, `abstract_patches`, `dense_patches` | `simple_continents` | surface module substyle | S1 / S4 |

## Multiplicity / Copy Logic

- 无模板级可变复制数量逻辑：核心 part 是 named support/meridian/globe/date_ring，不暴露 `continent_count`、`latitude_count` 或 `tick_count` 为模板级 count。
- Globe graticule lines, land patches, tick marks, yoke bolts, and decorative rings are module-local fixed visuals generated inside surface/support helpers. They may loop internally but do not create independent part+joint copies.

## 拓扑多样性审计

总组合数：5 support modules x 5 meridian modules x 4 surface modules x 3 auxiliary modules = 300 before legality gating.


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| support_base | 5 | yes | desktop/cradle/partial/pedestal/wall |
| meridian_or_cradle | 5 | yes | revolute/fixed/none/nested/partial |
| globe_surface | 4 | yes | map/graticule density changes visual topology |
| auxiliary_rotary | 3 | yes | none/date/support yaw |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| support/base | desktop base / outer cradle / rotating pedestal / wall arm | no | yes | `support_style` | root topology and contact plane differ |
| meridian/cradle | full tilting ring / fixed ring / nested ring / no ring / partial wall ring | no | yes | `meridian_style` | joint chain changes |
| globe surface | simple continents / dense patches / graticule mesh / minimal bands | no | yes | `surface_style`, `graticule_density` | 地图视觉是类别身份 |
| auxiliary | none / date ring / rotating support stage | no | yes | `auxiliary_rotary` | adds/removes part and CONTINUOUS joint |
| knobs/caps | none / side knobs / axis caps | partial | no | derived | 多为 support/meridian local fixed visual |
| globe radius/tilt | continuous radius and axial tilt | yes | no | `globe_radius`, `axial_tilt_degrees` | 连续参数足够表达尺寸/角度 |

## 组合逻辑（Composition Logic）
1. 从 `globe_radius` 和 `axial_tilt_degrees` 派生 globe center, polar axis, yoke contact points, meridian radius。
2. `support_style` 决定 contact plane / wall plane / pedestal height；ring and globe origin derive from support top.
3. `meridian_style` 决定 support -> meridian joint type；if `none_pedestal`, globe parent is support pedestal.
4. `globe_spin` origin is globe center; axis must align with globe polar axis and map visuals.
5. Surface patches are globe visuals in globe-local coordinates so they move with globe spin.

## 已有模板写法参考
`coaxial_rotary_stack` / `revolute_hinge` / `radial_array` / `turntable`（仅参考组织与 joint metadata）

## 约束
- 必须有 `globe` sphere part and `globe_spin` CONTINUOUS joint。
- Globe spin origin must be at globe center; axis must match polar caps/meridian support.
- Meridian ring must surround globe with clearance and not intersect the sphere severely.
- Wall-arm support must expose wall plane/base bracket, not float as desktop stand.
- Date ring/support yaw are optional, not substitutes for globe spin.

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | visible globe sphere with map/graticule visual and support |
| main joint | exactly or at least one `globe_spin` CONTINUOUS |
| axis placement | globe spin origin near sphere center |
| support chain | globe parented through meridian/support, no floating |
| meridian clearance | ring radius > globe radius by clearance |
| auxiliary | date ring/support yaw do not remove globe_spin |
| diversity | support_style/meridian_style/surface_style branches covered |

## Reject cases
- 纯球体没有底座/支架/地图视觉。
- globe spin axis not through sphere center。
- meridian ring intersects globe heavily or floats away。
- 变成 gyroscope/orbital model with no Earth-map identity。
- wall mount or pedestal support detached from globe center chain。
- surface_style only changes color while no continents/graticule/bands exist。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；未进入模板实现阶段 |
