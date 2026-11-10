# Camera Lens Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `camera_lens` |
| template path | `agent/templates/camera_lens.py` |
| test path | `tests/agent/test_camera_lens_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 51 |
| read_count | 51 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
相机镜头，至少包含同轴圆筒镜身、前/后玻璃或卡口端、一个或多个可旋转控制环。根据镜头类型可包含伸缩内筒、三脚架环、遮光罩、光圈环、tilt-shift 光学模块等，但所有活动件都必须围绕光轴或明确的偏移/倾斜机构运动。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829` | `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L100-L259` | cine zoom barrel, ribbed zoom/iris/focus ring mesh helpers, inner barrel mesh |
| S2 | `rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829` | `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L273-L438` | zoom lens part tree, zoom ring, iris ring, prismatic inner barrel, focus ring joints |
| S3 | `rec_camera_lens_78025792d0c04811a96df46e4abb50b0` | `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L58-L390` | super-telephoto long barrel, tripod collar foot, focus ring, collar/focus joints |
| S4 | `rec_camera_lens_eae9d22974ac445b8f365b95895d09f4` | `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L42-L260` | tilt-shift outer housing, rotation collar, shift carriage, tilted optical block |
| S5 | `rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633` | `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L191-L272` | manual prime barrel, focus/aperture rings, bayonet hood twist |
| S6 | `rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80` | `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L121-L264` | retractable kit zoom, unlock ring, zoom ring, extending front barrel |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `barrel` / `outer_barrel` | required；主镜身圆筒，含 rear mount、front bezel、glass、bearing lands | `barrel_length`, `barrel_radius`, `barrel_profile`, `mount_style` | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L100-L156`; S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L273-L322`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L58-L249`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L121-L152` |
| `zoom_ring` | optional but common；外筒上的旋转 zoom ring，可带 rib/gear/T handle | `zoom_ring_enabled`, `ring_style`, `zoom_ring_width`, `zoom_range_deg` | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L159-L184`; S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L323-L329`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L167-L205` |
| `focus_ring` | required for generic template；同轴 focus sleeve/ring | `focus_ring_style`, `focus_ring_width`, `focus_range_deg` | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L238-L259`; S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L395-L438`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L310-L390`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L223-L260` |
| `iris_or_aperture_ring` | optional；光圈/iris 控制环 | `aperture_ring_enabled`, `aperture_ring_style`, `aperture_range_deg` | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L187-L208`; S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L330-L335`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L230-L252` |
| `inner_barrel` / `front_barrel` | optional；伸缩内筒或前筒，可 prismatic | `extension_enabled`, `extension_length`, `extension_style` | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L211-L235`; S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L337-L392`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L206-L264` |
| `tripod_collar` | optional；长焦镜头的旋转三脚架环和脚座 | `tripod_collar_enabled`, `collar_style`, `foot_length` | S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L251-L309` |
| `hood` | optional；前端遮光罩/hood collar，常为 bayonet twist | `hood_enabled`, `hood_style`, `hood_twist_range_deg` | S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L237-L272` |
| `tilt_shift_stage` | optional；旋转 collar、横移 carriage 和倾斜 optical block | `tilt_shift_enabled`, `shift_axis`, `shift_travel`, `tilt_range_deg` | S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L42-L260` |
| `unlock_ring` | optional；retractable kit zoom 解锁环 | `unlock_ring_enabled`, `unlock_range_deg` | S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L153-L166`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L239-L247` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `zoom_ring_turn` | revolute/continuous | optical axis, default `(1, 0, 0)` in template | zoom ring center | 0-1.25 rad or continuous | zoom ring 围绕光轴旋转 | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L402-L410`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L248-L256` |
| `focus_ring_turn` | revolute/continuous | optical axis, default `(1, 0, 0)` | focus ring center | about -2.35 to 2.35 or continuous | focus ring 旋转 | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L430-L438`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L380-L390`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L253-L260` |
| `aperture_ring_turn` | revolute/continuous, optional | optical axis | aperture/iris ring center | 0-1.10 rad or continuous | 光圈环/iris 环旋转 | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L421-L429`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L244-L252` |
| `barrel_extension` | prismatic, optional | optical axis | inner/front barrel sliding sleeve | 0-0.032 m; retractable variants may be longer | inner/front barrel 沿光轴伸缩；可由 zoom ring metadata 驱动 | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L411-L420`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L257-L264` |
| `tripod_collar_turn` | continuous/revolute, optional | optical axis | collar land center | unbounded or full turn | 三脚架环绕镜身旋转，脚座随之绕轴运动 | S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L371-L379` |
| `hood_twist` | revolute, optional | optical axis | hood bayonet seat | 0 to about 0.5-1.2 rad | 遮光罩 bayonet twist | S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L262-L272` |
| `tilt_shift_rotate` | revolute, optional | optical axis | rotation collar center | -90° to 90° | tilt-shift 方向绕光轴旋转 | S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L221-L234` |
| `shift_slide` | prismatic, optional | `(1, 0, 0)` or selected transverse axis | collar/carriage center | -0.012 to 0.012 m | tilt-shift carriage 横移 | S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L235-L248` |
| `tilt_axis` | revolute, optional | `(0, 1, 0)` or orthogonal trunnion axis | optical block trunnion | about +/-8° | optical block 倾斜 | S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L249-L260` |
| `unlock_ring_turn` | continuous/revolute, optional | optical axis | unlock ring center | unlocked arc or continuous | retractable lens 解锁环 | S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L239-L247` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `lens_profile` | enum | `standard_zoom` / `macro_extending` / `telephoto_collar` / `manual_prime` / `cine_zoom` / `tilt_shift` / `retractable_kit` | `standard_zoom` | drives optional parts and proportions | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L273-L438`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L58-L390`; S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L42-L260`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L191-L272`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L121-L264` |
| `barrel_length` | float | 0.12-0.48 | 0.24 | `telephoto_collar` and `cine_zoom` use longer values | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L273-L322`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L58-L249` |
| `barrel_profile` | enum | `straight_cylinder` / `stepped_zoom` / `long_telephoto` / `short_pancake` / `tilt_shift_compact` | `stepped_zoom` | sets section profile and bearing lands | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L100-L156`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L58-L249`; S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L42-L76` |
| `ring_style` | enum | `rubber_ribbed` / `gear_teeth` / `fine_knurl` / `smooth_marked` / `t_handle` | `rubber_ribbed` | used for zoom/focus/aperture ring geometry | S1 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L159-L259`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L310-L390`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L223-L235` |
| `zoom_ring_enabled` | bool | true / false | true | false for prime/teleconverter profiles | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L323-L329`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L167-L205` |
| `aperture_ring_enabled` | bool | true / false | false | common for manual/cine primes | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L330-L335`; S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L230-L252` |
| `extension_enabled` | bool | true / false | true for zoom/macro | creates `inner_barrel`/`front_barrel` and prismatic joint | S2 / `data/records/rec_camera_lens_c164b5aad7594310b4f0d8bd7cc07829/revisions/rev_000001/model.py:L337-L420`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L206-L264` |
| `tripod_collar_enabled` | bool | true / false | false | true for long telephoto profiles | S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L251-L309`; S3 / `data/records/rec_camera_lens_78025792d0c04811a96df46e4abb50b0/revisions/rev_000001/model.py:L371-L379` |
| `hood_enabled` | bool | true / false | false | true for manual prime/cine variants | S5 / `data/records/rec_camera_lens_ab36f894f9284d2193ae70c5c36ee633/revisions/rev_000001/model.py:L237-L272` |
| `tilt_shift_enabled` | bool | true / false | false | if true replaces simple front optical group with collar/carriage/block | S4 / `data/records/rec_camera_lens_eae9d22974ac445b8f365b95895d09f4/revisions/rev_000001/model.py:L78-L260` |
| `unlock_ring_enabled` | bool | true / false | false | true for retractable kit profile | S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L153-L166`; S6 / `data/records/rec_camera_lens_c523cb1b668d47cba360ed7178e2fe80/revisions/rev_000001/model.py:L239-L247` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| barrel | straight cylinder / stepped zoom / long telephoto / compact tilt-shift / retractable kit | no | yes | `lens_profile`, `barrel_profile` | 主筒轮廓和可选机构拓扑不同 |
| control rings | focus only / zoom+focus / zoom+iris+focus / aperture+focus / unlock+zoom | no | yes | `ring_layout`, `zoom_ring_enabled`, `aperture_ring_enabled`, `unlock_ring_enabled` | ring 数量和功能影响 parts/joints |
| ring surface | rubber ribs / gear teeth / fine knurl / smooth marked / T-handle | no | yes | `ring_style` | 表面结构是可见形态差异 |
| inner/front barrel | none / macro extension / zoom inner barrel / retractable front barrel | no | yes | `extension_enabled`, `extension_style` | 是否伸缩及嵌套方式不同 |
| tripod collar | none / rotating collar with foot | no | yes | `tripod_collar_enabled`, `collar_style` | 长焦样本中有独立旋转环和脚座 |
| hood | none / bayonet twist hood / shade collar | no | yes | `hood_enabled`, `hood_style` | 遮光罩是独立可动/可拆式外形 |
| tilt-shift stage | none / rotate+shift+tilt optical block | no | yes | `tilt_shift_enabled` | tilt-shift 是完全不同的活动机构 |
| mount/front glass | bayonet rear mount / PL/cine mount / screw mount / front coated glass | no | yes | `mount_style`, `front_element_style` | 影响端部识别特征 |

## 组合逻辑（Composition Logic）
1. 根据 `lens_profile` 选择 barrel envelope、光轴方向和可选模块集合。
2. 构建 outer barrel：rear mount、front bezel/glass、ring bearing lands 和 index marks。
3. 按 `ring_layout`/enabled flags 创建 zoom/focus/aperture/unlock rings，并把所有 ring origin 放在光轴上。
4. `extension_enabled` 时创建 inner/front barrel，并添加光轴方向 prismatic joint；可在 metadata 中记录由 zoom ring 驱动。
5. `tripod_collar_enabled` 时在 barrel 中段创建 collar ring 与 foot，添加绕光轴 continuous joint。
6. `hood_enabled` 时在前端 bayonet seat 上创建 hood，并添加 hood twist joint。
7. `tilt_shift_enabled` 时创建 rotation collar、shift carriage、inner optical block，按 rotate -> shift -> tilt 的父子链装配。

## 已有模板写法参考
continuous_rotor / prismatic_slide / revolute_hinge / telescoping_tube / guide_shoe

## 约束
- 所有普通 ring 必须与镜头光轴同心，axis 与光轴一致。
- 至少有一个可旋转 control ring；generic 默认 focus ring required。
- front/rear glass 或可见光学端必须存在，不能只是实心圆柱。
- inner/front barrel 伸缩时必须仍部分插入 outer barrel。
- tripod collar 的 foot 必须随 collar 旋转绕 barrel 运动。
- tilt-shift 模式的 shift 轴必须垂直于光轴，tilt axis 必须垂直于 shift/光轴之一。
- 不同 `lens_profile` 的 optional parts 不应互相堆叠成不真实组合，例如 pancake 不带巨大 tripod foot。
- 非可动刻度、文字块、bayonet lugs 优先作为 parent visual。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | barrel + optical glass/front element + at least one control ring |
| ring coaxial | all control ring origins share optical axis with barrel |
| ring axis | ring joints use optical axis |
| extension | enabled 时 prismatic axis 为光轴，extended pose 仍嵌套 |
| tripod collar | enabled 时 collar has continuous/revolute axis on optical axis and foot swings around barrel |
| hood | enabled 时 hood twist axis is optical axis and hood remains seated |
| tilt-shift | enabled 时有 rotate, shift, tilt 三个 joints，父子链为 housing -> collar -> carriage -> optical block |
| part diversity | `lens_profile`, `barrel_profile`, `ring_style`, ring/extension/collar/hood/tilt-shift flags 均暴露 |
| no floating | all rings, barrel sections, collar, hood, optical blocks connected to main tree |

## Reject cases
- 只有普通圆柱，没有可见 glass/front element 或控制环。
- ring 轴不沿光轴，转动像侧面旋钮。
- focus/zoom ring 漂浮或与 barrel 不同心。
- inner barrel 伸出后完全脱离 outer barrel。
- tripod foot 固定在 barrel 上而 collar part 转不动。
- tilt-shift 的 shift/tilt 轴与光轴混淆，导致光学块绕自身乱转。
- 多个 profile 的部件无约束混搭，失去真实镜头结构。
- 变成相机机身、望远镜或手电筒。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
