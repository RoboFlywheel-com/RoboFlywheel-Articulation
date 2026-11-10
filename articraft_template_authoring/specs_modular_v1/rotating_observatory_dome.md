# Rotating Observatory Dome Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `rotating_observatory_dome` |
| template path | `agent/templates/rotating_observatory_dome.py` |
| test path | `tests/agent/test_rotating_observatory_dome_template.py` |
| stage | `REVIEWED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 |
| four_star_supplement | 13 |
| read_count | 16 |
| read_scope | all 3 five-star samples + 13 four-star supplement（5 星不足 5 个，经用户确认补读 4 星）: `model.py` / `revision.json` / `record.json` / `prompt.txt` were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 10 |
| source_index_policy | only adopted reusable snippets are indexed below |

> ⚠️ 样本约束记录：本类别 retained 5 星样本仅 3 个（低于工作流 §2.1 的 5 个下限）。经用户明确确认，补读全部 13 个 4 星样本以获取充分的部件/关节多样性。6 个被采纳模块来源中有 3 个来自 5 星样本；其余 3 个来自结构干净、参数化良好的 4 星样本，并已在下表逐条标注 rating。

全量阅读后的结构族分布（标注 5★/4★ 来源）：

| 结构族 | 样本数 | 5★/4★ | 说明 |
|---|---:|---|---|
| drum/base -> dome -> single hinged shutter leaf（REVOLUTE） | 11 | 3★5 + 8★4 | 最大族；slit 由 lofted/spherical shell 切出，shutter 绕水平轴翻起 |
| base -> dome -> twin sliding shutters（2× PRISMATIC，或 PRISMATIC + REVOLUTE） | 4 | 0★5 + 4★4 | lower/upper 双滑板，沿 dome Z 滑动 |
| base -> rotation_band(中间件) -> dome -> crown hatch（REVOLUTE） | 1 | 1★5 | 0004，独有中间 rotation_band part |
| pier + fixed ring_track -> dome -> fixed slit_frame -> twin shutters | 1 | 0★5 + 1★4 | 6bffe，shutters 挂在 fixed slit_frame |

> 5 星族：单 REVOLUTE flap（fea4a），crown hatch + rotation_band（0004），up-and-over rail flap（57b39）。三个 5 星都只有 single shutter DOF；无一使用 twin sliding shutters。

被采纳样本逐条标注：
- `rec_rotating_observatory_dome_fea4ae109f11450dbb054dc400d19903`（5★）— adopted：最干净 canonical，foundation + support_pier(望远镜代理) + dome_shell + shutter_leaf，CONTINUOUS Z dome rotation + REVOLUTE slit shutter，全部由 `LatheGeometry.from_shell_profiles`/`section_loft` profiles 驱动。
- `rec_rotating_observatory_dome_57b3940eec574b97aac4f1de4c86589e`（5★）— adopted：up-and-over rail-mounted shutter（guide rails + rollers + roller arms）的最佳现实参考。
- `rec_rotating_observatory_dome_0004`（5★）— adopted：premium ellipsoid shell + 独有中间 rotation_band + crown_hatch（REVOLUTE X）+ 8 roller 组件。
- `rec_rotating_observatory_dome_2fd43504e09f459f97e9312e6650dfeb`（4★）— adopted：desktop 尺度 PRISMATIC lower + REVOLUTE upper 组合 shutter 的最干净参考。
- `rec_rotating_observatory_dome_a65c769cc4f648e1929c38f7eebd1cf1`（4★）— adopted：compact 单 closed-revolution dome profile loft 模板，base ring + dome + shutter_leaf。
- `rec_rotating_observatory_dome_275ae55b7d5c448da886916012469944`（4★）— adopted：`boolean_difference` 切 slit + 计算 tangent hinge pitch 的最紧凑“真实”做法。
- Remaining 10 samples — read but not adopted：同一 base -> rotating dome -> shutter 链的 dome profile / drum 尺度 / roller 细节差异，已被上述模块覆盖。

## 核心身份
`rotating_observatory_dome` 是一个旋转天文台圆顶：静态 cylindrical base/drum/foundation 承载一个绕竖直 Z 轴连续旋转（azimuth rotation, CONTINUOUS）的半球/穹顶 dome shell，dome 上有一道狭缝 slit，由一个 shutter 机构开合露出 slit（单 REVOLUTE 翻盖、双 PRISMATIC 滑板、或 crown hatch）。半球穹顶 + slit + shutter 是不可缺的身份件。默认成熟域是 dome rotation(CONTINUOUS Z) + single REVOLUTE shutter；twin sliding shutter、rotation_band、telescope pier、roller bogies、service ledge 都是可选。语料中无内部望远镜的 altitude/azimuth 关节（pier 仅作非可动代理）。

边界：
- 不包括固定不动的穹顶：必须有 dome rotation + shutter articulation。
- 不混入 planetarium dome / 普通 dome 建筑：必须有可旋转 dome + 可开 slit shutter。
- 不混入 radar dome / radome：是带 slit 的天文台圆顶，不是封闭雷达罩。
- 不要发明内部望远镜 alt/az 关节（语料中 pier 不可动）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | rating | model.py 来源 | 采纳用途 |
|---|---|---|---|---|
| S1 | `rec_rotating_observatory_dome_fea4ae109f11450dbb054dc400d19903` | 5★ | `.../rec_rotating_observatory_dome_fea4ae109f11450dbb054dc400d19903/revisions/rev_000001/model.py:L24-L396` | canonical：consts L24-L33、`_radial_extent`/`section_loft` helpers L42-L145、foundation L167-L246、support_pier L248-L265、dome_shell(curb+spherical band+hinge lugs)L267-L335、shutter_leaf L337-L359、joints(FIXED pier L361 / CONTINUOUS dome_rotation L368 / REVOLUTE slit_shutter L377)L361-L396 |
| S2 | `rec_rotating_observatory_dome_57b3940eec574b97aac4f1de4c86589e` | 5★ | `.../rec_rotating_observatory_dome_57b3940eec574b97aac4f1de4c86589e/revisions/rev_000001/model.py:L24-L580` | rail shutter：params L24-L44、spherical-strip + shell helpers L69-L339、stationary_base(wall/curb/track/bogies)L351-L417、dome_shell(4 skin patches+skirt+guide rails+standoffs)L419-L506、slit_shutter(skin+rollers+roller arms)L508-L556、joints(CONTINUOUS L558 / REVOLUTE (0,-1,0) up-and-over L567)L558-L580 |
| S3 | `rec_rotating_observatory_dome_0004` | 5★ | `.../rec_rotating_observatory_dome_0004/revisions/rev_000001/model.py:L70-L586` | premium：ellipsoid shell helpers L70-L352、base_ring(rings+8 roller assemblies)L400-L467、rotation_band(中间件)L469-L484、dome_shell(shell+crown ring+seam battens+bearing collars)L486-L525、crown_hatch L527-L555、joints(CONTINUOUS L557 / FIXED band->dome L566 / REVOLUTE crown_hatch X L573)L557-L586 |
| S4 | `rec_rotating_observatory_dome_2fd43504e09f459f97e9312e6650dfeb` | 4★ | `.../rec_rotating_observatory_dome_2fd43504e09f459f97e9312e6650dfeb/revisions/rev_000001/model.py:L26-L585` | PRISMATIC+REVOLUTE：consts L26-L50、base L373-L418、dome_shell(cyl+spherical+crown cap)L420-L467、lower_shutter(PRISMATIC panel+stiles+brackets)L469-L522、upper_shutter(REVOLUTE flap)L524-L547、joints(CONTINUOUS L549 / PRISMATIC lower L558 / REVOLUTE upper (0,-1,0) L572)L549-L585 |
| S5 | `rec_rotating_observatory_dome_a65c769cc4f648e1929c38f7eebd1cf1` | 4★ | `.../rec_rotating_observatory_dome_a65c769cc4f648e1929c38f7eebd1cf1/revisions/rev_000001/model.py:L25-L291` | compact loft：single profile L25-L49、helpers L53-L139、base_ring(foundation/drum/curb/torus rail)L152-L178、dome_shell(lofted body+skirt+slit guides+crown cheeks)L180-L228、shutter_leaf(lofted crown panel+hinge barrel/brackets)L230-L265、joints(CONTINUOUS L267 / REVOLUTE (0,-1,0) L276)L267-L291 |
| S6 | `rec_rotating_observatory_dome_275ae55b7d5c448da886916012469944` | 4★ | `.../rec_rotating_observatory_dome_275ae55b7d5c448da886916012469944/revisions/rev_000001/model.py:L40-L221` | boolean slit：`ring_band` helper + hinge math L40-L62、base_ring(drum+support ring+4 piers+roller torus)L64-L116、dome_shell(Lathe shell + `boolean_difference` slit cut + hinge brackets)L118-L178、shutter_leaf(boolean box leaf)L180-L197、joints L199-L221 |

## 槽位 + 候选模块表

### Slot A：base_drum
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `pier_plus_ring_track` | S1 | `model.py:L167-L246` | **yes** | foundation + observation floor + bearing track（+ 非可动 pier） |
| `wall_curb_track_bogies` | S2 | `model.py:L351-L417` | | 圆筒墙 + curb + track + roller bogies |
| `ring_with_rollers` | S3 | `model.py:L400-L467` | | rings + 8 roller assemblies（premium） |
| `solid_drum` | S4 | `model.py:L373-L418` | | desktop 实心圆筒 drum + curb |
| `annular_ring_band` | S5 | `model.py:L152-L178` | | foundation/drum/curb + torus rail |

### Slot B：rotating_dome
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `lathe_loft_hemisphere` | S1 | `model.py:L267-L335` | **yes** | `from_shell_profiles` 半球壳 + curb + slit hinge lugs |
| `spherical_strip_patches` | S2 | `model.py:L419-L506` | | 4 skin patches + skirt + guide rails + standoffs |
| `ellipsoid_band_crown` | S3 | `model.py:L486-L525` | | ellipsoid shell + crown ring + seam battens + bearing collars（配 rotation_band） |
| `compact_revolution_profile` | S5 | `model.py:L180-L228` | | 单 closed-revolution lofted body + skirt + slit guides |
| `boolean_cut_shell` | S6 | `model.py:L118-L178` | | Lathe shell + `boolean_difference` 切 slit |

### Slot C：shutter_mechanism
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `single_revolute_flap` | S1 | `model.py:L337-L396` | **yes** | 单 shutter leaf 绕水平轴翻起（outward/up-and-over） |
| `rail_roller_flap` | S2 | `model.py:L508-L580` | | up-and-over leaf + guide rails + rollers + roller arms |
| `crown_hatch_revolute` | S3 | `model.py:L527-L586` | | crown 顶 hatch 绕 X 翻开（需 rotation_band） |
| `prismatic_plus_revolute` | S4 | `model.py:L469-L585` | | lower PRISMATIC 滑板 + upper REVOLUTE flap |
| `boolean_box_leaf` | S6 | `model.py:L180-L221` | | boolean box leaf + 计算 tangent hinge pitch |

### Slot D：auxiliary_detail
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `none` | S1 | — | **yes** | 无额外件 |
| `telescope_pier` | S1 | `model.py:L248-L265` | | 中心非可动 pier/pedestal（望远镜代理，FIXED） |
| `roller_bogies` | S2 | `model.py:L351-L417` | | base 上 roller bogie 阵列（count 6-12 装饰） |
| `rotation_band` | S3 | `model.py:L469-L484` | | base 与 dome 之间的中间旋转环（FIXED 到 dome） |
| `service_ledge` | S2 | `model.py:L351-L417` | | 内圈 observation/service ledge |

## 槽位图（slot graph）
pattern = `linear_chain`

```
[Slot A base_drum]
      -- (optional) FIXED telescope_pier [Slot D] -->
      -- (optional) FIXED rotation_band [Slot D]，再 CONTINUOUS，或直接：
      -- azimuth_rotation CONTINUOUS, axis (0,0,1) -->
[Slot B rotating_dome]   (slit 切在 shell 上)
      -- shutter REVOLUTE (0,±1,0)/(1,0,0)  或  PRISMATIC (0,0,±1) -->
[Slot C shutter / panels]
```

主约束基准是 azimuth vertical axis、bearing track 平面、slit angular sector。dome 半径、slit 半角、hinge_z、shutter 行程、roller 位置都从这些基准派生。

## 部件（Parts）

### Slot A / base_drum
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `base_ring` / `foundation` / `support_base` / `base_pier` | ~3-25 | static 圆筒墙/drum/环形基座 + bearing track（+ roller bogies） | S1/S2/S3/S5 |

### Slot B / rotating_dome
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `dome_shell` / `dome` | ~1-30 | 旋转半球/穹顶壳，含切出的 slit（jambs/sill/rails 框边）；可选 crown cap、rotation skirt | S1-S6 |

### Slot C / shutter_mechanism
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `shutter_leaf` / `slit_shutter` / `crown_hatch` | ~1-13 | 单翻盖 leaf（含 hinge barrel/brackets/rollers） | S1/S2/S3/S5/S6 |
| `lower_shutter` / `upper_shutter` | ~3-13 | twin sliding 变体的下/上滑板（+ guide brackets） | S4 |

### Slot D / auxiliary_detail
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `support_pier` / `instrument_pedestal` | ~1-2 | 非可动望远镜代理（FIXED 到 foundation，不参与 dome 旋转） | S1 |
| `rotation_band` | ~1-3 | base 与 dome 间的中间旋转环（CONTINUOUS 在 band 上，band->dome FIXED） | S3 |

roller bogies、seam battens、crown ring、guide rail standoffs、slit jambs/sill 默认用 `parent.visual(...)` 挂在 base/dome 上，不建独立 part。

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `azimuth_rotation` / `dome_rotation` | CONTINUOUS | A.base_drum（或 D.rotation_band） | B.rotating_dome | `(0,0,1)` | unlimited | dome 绕竖直轴连续旋转（主 DOF，16/16） | S1-S6 |
| `slit_shutter` / `shutter_hinge` | REVOLUTE | B.rotating_dome | C.shutter_leaf | `(0,1,0)`/`(0,-1,0)`/`(1,0,0)`（水平，含 rpy tangent pitch） | `[0, 1.05~1.75]` | 单翻盖 shutter 开合 | S1/S2/S5/S6 |
| `crown_hatch_open` | REVOLUTE | B.rotating_dome | C.crown_hatch | `(1,0,0)` | `[0, ~1.5]` | crown 顶 hatch 翻开 | S3 |
| `shutter_travel`（lower/upper） | PRISMATIC | B.rotating_dome（或 fixed slit_frame） | C.lower/upper_shutter | `(0,0,1)`/`(0,0,-1)` | `[0, 0.45~1.20]` | twin sliding 滑板沿 dome Z 滑动 | S4 |
| `rotation_band_to_dome` | FIXED | D.rotation_band | B.rotating_dome | n/a | n/a | 中间旋转环固定到 dome（premium 变体） | S3 |
| `foundation_to_pier` | FIXED | A.foundation | D.support_pier | n/a | n/a | 非可动望远镜代理固定 | S1 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `base_style` | enum | `pier_ring_track`, `wall_curb_bogies`, `ring_rollers`, `solid_drum`, `annular_ring` | `pier_ring_track` | Slot A module | S1/S2/S3/S4/S5 |
| `dome_shape` | enum | `lathe_hemisphere`, `spherical_strip`, `ellipsoid_band`, `revolution_profile`, `boolean_cut` | `lathe_hemisphere` | Slot B module | S1-S6 |
| `shutter_style` | enum | `single_revolute_flap`, `rail_roller_flap`, `crown_hatch`, `twin_prismatic`, `prismatic_plus_revolute` | `single_revolute_flap` | Slot C module（5 星只见 single flap） | S1/S2/S3/S4 |
| `shutter_count` | int | `1, 2` | `1` | twin sliding = 2，其余 = 1 | S4 |
| `hinge_axis` | enum | `y`, `x` | `y` | shutter REVOLUTE 轴向，耦合 slit 朝向 | S1/S3 |
| `shutter_open_direction` | enum | `up_and_over`, `outward`, `slide_up` | `outward` | shutter 开启方向 | S1/S2/S4 |
| `dome_radius` | float | `[0.15, 4.1]` | `1.8` | dome 外半径（nominal 1.5-2.5） | S1/S4 |
| `dome_height` | float | `[0.15, 4.1]` | `1.7` | dome Z 高度（≈ radius，pointed crown 至 1.7×） | S1/S5 |
| `shell_thickness` | float | `[0.007, 0.12]` | `0.05` | 壳厚（≈ 1-4% radius） | S1/S4 |
| `drum_radius` | float | `[0.13, 4.3]` | `1.9` | base 半径（约 0.9-1.4× dome radius） | S1/S5 |
| `drum_height` | float | `[0.05, 1.9]` | `0.9` | base 高度 | S1/S2 |
| `slit_half_angle` | float | `[0.145, 0.34]` | `0.20` | slit 方位半角（≈8-20°） | S1/S6 |
| `shutter_half_angle` | float | `[0.145, 0.22]` | `0.20` | shutter 覆盖半角（含 overlap） | S1/S2 |
| `hinge_z` | float | `[drum_top, dome_crown]` | `dome_crown` | flap-up 在 crown，outward 在 slit base | S1/S2 |
| `shutter_open_upper` | float | REVOLUTE `[1.05, 1.75]` / PRISMATIC `[0.45, 1.20]` | `1.4` | shutter 开启行程 | S1/S4 |
| `bearing_track_z` | float | `= drum_height (+offsets)` | derived | track 顶 = drum 顶 | S1 |
| `telescope_pier` | bool | `True/False` | `True` | 中心非可动 pier（身份增强） | S1 |
| `rotation_band` | bool | `True/False` | `False` | base 与 dome 间中间环 | S3 |
| `roller_count` | int | `0, 6, 8, 12` | `8` | base roller bogie 数量（0=无） | S2/S3 |
| `crown_cap` | bool | `True/False` | `False` | dome 顶 crown cap 细节 | S4 |
| `service_ledge` | bool | `True/False` | `False` | 内圈 service ledge | S2 |

## Multiplicity / Copy Logic
- 模板级核心是 one base, one rotating dome, one shutter mechanism（shutter_count 1 或 2）：核心链不变。
- `roller_count`（0/6/8/12）是 base 上的 module-local 可变 N；slit jambs/sill、seam battens、guide rail standoffs、4-pier、bolt 等是 helper 内固定/装饰循环。
- twin sliding 变体固定 2 块滑板（lower+upper），不暴露任意 N。
- 不引入内部望远镜的 alt/az 数量或关节（pier 仅非可动代理）。

## 拓扑多样性审计
总组合数（gating 前）：5 base × 5 dome × 5 shutter × auxiliary 组合 ≈ 125+（受 shutter/rotation_band/crown gating）。


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| base_drum | 5 | yes | pier-track/wall-bogies/ring-rollers/solid/annular |
| rotating_dome | 5 | yes | lathe/strip/ellipsoid/revolution/boolean |
| shutter_mechanism | 5 | yes | single flap/rail flap/crown hatch/twin prismatic/prismatic+revolute |
| auxiliary | 4 | yes | none/pier/rotation_band/rollers |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base / drum | 实心 cylinder / 环形 ring-band / pier + fixed track；roller 0/6/8/12 | mostly（尺度） | yes | `base_style`, `drum_radius`, `drum_height`, `roller_count` | 拓扑与 rotation 接口不同 |
| rotating dome | lathe 半球 / spherical-strip mesh / ellipsoid / 单 revolution profile / boolean-cut；厚度；crown cap | radius/height/thickness 连续，profile 形态离散 | yes | `dome_shape`, `dome_radius`, `dome_height`, `shell_thickness`, `crown_cap` | 壳构造与 slit 切法不同 |
| shutter / slit panels（身份） | 单 REVOLUTE leaf(11) / twin PRISMATIC(2) / PRISMATIC+REVOLUTE(2) / crown hatch(1)；hinge x/y；lofted vs box；带/不带 rollers | 面板尺寸/hinge_z/行程连续 | yes（关键） | `shutter_style`, `shutter_count`, `slit_half_angle`, `hinge_axis`, `shutter_open_upper` | 主拓扑判别 enum |
| slit framing | 隐式 mesh void + Box jambs/sill/lintel / boolean cut / masked；slider 需 rails | jamb/sill 连续 | 轻度 | `guide_rails`（none/rails） | slider 需导轨 |
| telescope / pier | 多数无；中心 cylinder pier/pedestal；从不 articulated | pier 半径/高度连续 | yes（存在性） | `telescope_pier` | 非可动代理 |
| catwalk / service ledge | 罕见内圈 service ledge | 尺寸连续 | 轻度 | `service_ledge`（默认 off） | 存在性 bool |
| bearing track / skirt | Torus / Lathe ring / Cylinder；几乎恒存在 | 连续半径/截面 | no | `track_radius`, `skirt_height` | 始终包含，风格次要 |

## 组合逻辑（Composition Logic）
1. `base_style` 确定 contact plane、drum 半径/高度与 bearing track 平面；`drum_height` 给出 azimuth 轴顶高度。
2. `azimuth_rotation` 关节 origin 落在 bearing track 顶（xy=0），CONTINUOUS 竖直轴；若 `rotation_band=True` 则 CONTINUOUS 在 base->band，再 band->dome FIXED。
3. `dome_shape` + `dome_radius/height/thickness` 派生 dome shell，并在 `slit_half_angle` 方位扇区切出 slit（loft 缺口 / boolean cut / box jambs）。
4. `shutter_style` 决定 shutter 拓扑与关节：single flap REVOLUTE（hinge 在 crown 或 slit base，axis 由 hinge_axis 定）、twin PRISMATIC 沿 dome Z 滑、crown hatch REVOLUTE X。
5. shutter `hinge_z` 与 `rpy` tangent pitch 使闭合 shutter 贴合曲面壳；slit 与 shutter 半角匹配并留 overlap。
6. roller bogies 沿 track 圆周等分排布；telescope pier 固定在 foundation 中心、不随 dome 旋转。

## 已有模板写法参考
`parabolic_dish_on_azimuth_elevation_mount` / `lighthouse_with_rotating_beacon_assembly` / `turntable` / `revolving_door` / `rotary_post` / `louvered_shutter_assembly`（参考 CONTINUOUS rotary post、shutter REVOLUTE/PRISMATIC、lathe/loft 壳与 boolean slit 写法）

## 约束
- 必须有 dome rotation（CONTINUOUS 竖直 Z）与 shutter（REVOLUTE 或 PRISMATIC）两类运动，链序 base -> dome -> shutter。
- dome 必须是带 slit 的半球/穹顶壳；shutter 闭合时覆盖 slit，开启时露出。
- azimuth 关节 origin 在 bearing track 平面、xy 居中。
- shutter hinge/slide 必须落在 slit 边缘并与曲面壳贴合（必要时 rpy tangent pitch）。
- twin sliding 变体需 guide rails；slider 沿 dome Z。
- telescope pier 若存在必须非可动（FIXED），不引入 alt/az 关节。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 旋转 dome shell + slit + shutter 同时存在 |
| rotation joint | base -> dome 绕 `(0,0,1)` CONTINUOUS，origin 在 track 平面、xy 居中 |
| shutter joint | dome -> shutter REVOLUTE（水平轴）或 PRISMATIC（沿 Z），落在 slit 边缘 |
| chain order | base -> dome -> shutter，无漂浮 dome/shutter |
| slit/shutter match | slit 半角与 shutter 覆盖匹配，闭合贴合曲面 |
| diversity | `base_style` / `dome_shape` / `shutter_style` 分支均被覆盖 |
| pier | telescope pier（若有）为 FIXED 非可动 |

## Reject cases
- dome 固定不动，没有 azimuth rotation。
- 没有 slit / shutter，退化成封闭穹顶或 radome。
- azimuth axis 非竖直，或 shutter 轴向错误（slider 不沿 Z，flap 轴非水平）。
- shutter 闭合不覆盖 slit，或开启时与壳穿模/悬空。
- dome 脱离 base 漂浮，或 shutter 脱离 dome。
- telescope pier 随 dome 旋转或被加上 alt/az 关节（语料无）。
- twin sliding 滑板缺 guide rails 导致悬空滑动。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | 5 星样本仅 3 个（< 5 下限），经用户确认补读 13 个 4 星样本；用户审核通过，进入 TEMPLATE_AFTER_REVIEW |
