# Ceiling Light Fixture Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `ceiling_light_fixture` |
| template path | `agent/templates/ceiling_light_fixture.py` |
| test path | `tests/agent/test_ceiling_light_fixture_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 65 |
| read_count | 65 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
天花灯具必须有贴顶或吊装的 ceiling mount / canopy、承载光源的 housing / shade / lamp head，以及至少一种可维护或可调节的活动方式，例如 hinged diffuser、gimbal tilt、track slide、swing arm 或 pull-down pendant。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_ceiling_light_fixture_59154f09e2424b6b9f3ea97a19a01234` | `data/records/rec_ceiling_light_fixture_59154f09e2424b6b9f3ea97a19a01234/revisions/rev_000001/model.py:L32-L298` | flush / service-light canopy, layered housing, hinged access lens and latch hardware |
| S2 | `rec_ceiling_light_fixture_34869e2b6cfb4ef8ac9aea6c2b9db178` | `data/records/rec_ceiling_light_fixture_34869e2b6cfb4ef8ac9aea6c2b9db178/revisions/rev_000001/model.py:L40-L279` | track rail, captured sliding carriage, swivel yoke, cylindrical spot head, slide / swivel / tilt joints |
| S3 | `rec_ceiling_light_fixture_44265bc82273451dac900331281045f5` | `data/records/rec_ceiling_light_fixture_44265bc82273451dac900331281045f5/revisions/rev_000001/model.py:L59-L240` | semi-flush canopy, swing arms, bowl shades, arm swing and shade tilt joints |
| S4 | `rec_ceiling_light_fixture_068635441bc94a02b66d5b450305fb9a` | `data/records/rec_ceiling_light_fixture_068635441bc94a02b66d5b450305fb9a/revisions/rev_000001/model.py:L40-L190` | pull-down pendant canopy, lock button, prismatic cord, rotating drum shade |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `mount` / `canopy` | 必需；贴顶圆盘、盒式底座或轨道，作为根部固定件 | `mount_style`, `mount_width`, `mount_depth`, `canopy_radius`, `drop_length` | S1 / `model.py:L32-L98`; S2 / `model.py:L40-L83`; S3 / `model.py:L152-L192`; S4 / `model.py:L40-L76` |
| `housing` / `shade_i` / `lamp_head_i` | 必需；承载光源、透镜、灯罩或 spotlight barrel | `fixture_layout`, `shade_style`, `head_count`, `head_profile`, `diffuser_profile` | S1 / `model.py:L74-L157`; S2 / `model.py:L177-L237`; S3 / `model.py:L101-L135`; S4 / `model.py:L126-L168` |
| `access_lens` / `diffuser` | 条件必需；`fixture_layout=hinged_diffuser` 时为独立活动件 | `diffuser_profile`, `diffuser_radius`, `diffuser_open_angle` | S1 / `model.py:L230-L298` |
| `carriage_i` / `swivel_yoke_i` | 条件必需；`fixture_layout=track_spot` 时每个灯头有轨道滑块和 yoke | `head_count`, `track_length`, `slide_travel`, `yoke_style` | S2 / `model.py:L85-L175` |
| `arm_i` | 条件必需；`fixture_layout=branching_arm` 时每个灯罩由 swing arm 承载 | `arm_count`, `arm_layout`, `arm_reach`, `arm_swing_range` | S3 / `model.py:L59-L99`; S3 / `model.py:L193-L203` |
| `cord` | 条件必需；`fixture_layout=pull_down_pendant` 时为可伸缩吊线 | `cord_travel`, `drop_length`, `cord_spin_enabled` | S4 / `model.py:L96-L124` |
| `lock_button` / `latch` | optional；检修扣、拉绳锁止按钮或 lens latch | `service_latch_style` | S1 / `model.py:L217-L228`; S4 / `model.py:L78-L94` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `lens_hinge` | revolute | `(1, 0, 0)` | diffuser 后侧 / 侧后 hinge rail | `[0, 1.35]` | 检修透镜或底部 diffuser 向下翻开 | S1 / `model.py:L290-L298` |
| `rail_slide_i` | prismatic | `(1, 0, 0)` | track channel 中线 | `[-0.46, 0.46]` scaled by `track_length` | track head 沿轨道滑动 | S2 / `model.py:L244-L257` |
| `carriage_swivel_i` | continuous | `(1, 0, 0)` in adopted sample; template may remap to local down axis by layout | carriage bearing center | unbounded | spot yoke 在 carriage 上旋转 / 摆向 | S2 / `model.py:L258-L265` |
| `head_tilt_i` | revolute | `(0, -1, 0)` | yoke trunnion center | `[-0.35, 0.95]` | spotlight head 在 yoke 内俯仰 | S2 / `model.py:L266-L279` |
| `arm_swing_i` | revolute | `(0, 0, ±1)` | canopy hub side pivot | `[-1.25, 1.25]` | 半吸顶支臂绕 canopy 水平摆动 | S3 / `model.py:L205-L222` |
| `shade_tilt_i` | revolute | `(0, ±1, 0)` | arm tip hinge | `[-0.55, 0.85]` | 碗形灯罩在支臂末端俯仰 | S3 / `model.py:L223-L240` |
| `cord_slide` | prismatic | `(0, 0, -1)` | canopy cord outlet | `[-0.55, 0]` | pendant cord 垂直伸缩 | S4 / `model.py:L115-L124` |
| `shade_spin` | continuous | `(0, 0, 1)` | cord lower swivel cap | unbounded | 吊灯罩绕吊线连续旋转 | S4 / `model.py:L181-L190` |
| `lock_button_slide` | prismatic | `(-1, 0, 0)` | canopy side lock pocket | `[0, 0.012]` | 伸缩吊灯锁止按钮 | S4 / `model.py:L85-L94` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `fixture_layout` | enum | `hinged_diffuser` / `track_spot` / `branching_arm` / `pull_down_pendant` | `hinged_diffuser` | 决定主要活动件、joint set 和 part tree | S1 / `model.py:L32-L298`; S2 / `model.py:L40-L279`; S3 / `model.py:L59-L240`; S4 / `model.py:L40-L190` |
| `mount_style` | enum | `round_canopy` / `rectangular_track` / `compact_ceiling_plate` / `canopy_cup` | `round_canopy` | 由 `fixture_layout` 约束；track layout 使用 rectangular track | S1 / `model.py:L32-L98`; S2 / `model.py:L40-L83`; S4 / `model.py:L40-L76` |
| `shade_style` | enum | `bowl` / `drum` / `cylindrical_spot` / `flat_diffuser` | `flat_diffuser` | 决定 shade / head 几何轮廓 | S1 / `model.py:L230-L262`; S2 / `model.py:L177-L237`; S3 / `model.py:L101-L135`; S4 / `model.py:L126-L168` |
| `head_count` | int | `1-6` | `1` | track / branching layouts 可派生多个 head；pull-down 固定 1 | S2 / `model.py:L85-L279`; S3 / `model.py:L177-L240` |
| `arm_count` | int | `2-6` | `2` | 仅 `branching_arm` 使用；按 radial / bilateral layout 分布 | S3 / `model.py:L177-L240` |
| `track_length` | float | `0.7-1.6` | `1.2` | `slide_travel <= track_length * 0.40` | S2 / `model.py:L40-L83`; S2 / `model.py:L244-L257` |
| `drop_length` | float | `0.10-0.85` | `0.35` | pendant / semi-flush 从 canopy 下表面派生 | S3 / `model.py:L152-L176`; S4 / `model.py:L96-L124` |
| `diffuser_open_angle` | float | `0.8-1.6` rad | `1.35` | lens hinge upper limit | S1 / `model.py:L290-L298` |
| `tilt_range` | float pair | lower `-0.6--0.2`, upper `0.5-1.1` | `[-0.35, 0.95]` | 用于 head / shade tilt joint | S2 / `model.py:L266-L279`; S3 / `model.py:L223-L240` |
| `service_latch_style` | enum | `none` / `spring_tab` / `side_button` | `spring_tab` | `hinged_diffuser` 默认 spring tab；pull-down 默认 side button | S1 / `model.py:L217-L228`; S4 / `model.py:L78-L94` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| mount / canopy | 圆形 layered canopy / rectangular track / cup canopy / compact ceiling plate | no | yes | `mount_style` | 贴顶圆盘和长轨道是拓扑差异，不是宽高可连续变形得到 |
| light housing / shade | flat diffuser / bowl shade / drum shade / cylindrical spotlight head | no | yes | `shade_style`, `head_profile` | 光学主体轮廓差异是类别核心视觉差异 |
| activity layout | hinged service lens / sliding track head / swing arms / pull-down pendant | no | yes | `fixture_layout` | 活动链和 joint 数量完全不同，必须枚举 |
| support arm / carriage | none / track carriage / radial or bilateral arm / cord | no | yes | `arm_layout`, `fixture_layout` | 支撑拓扑差异显著，连续尺寸不足 |
| latch / lock | spring latch / side lock button / none | no | yes | `service_latch_style` | 操作件形式不同；非核心时可为 none |
| decorative screws / trim rings | none; mostly count / spacing / thickness variation | yes | no | `trim_density` | 只观察到数量、位置、厚度变化，可用连续或计数参数表达 |

## 组合逻辑（Composition Logic）
1. 先根据 `fixture_layout` 选择根部结构：round canopy、rectangular track、branching hub 或 pull-down canopy。
2. 生成根 part 后派生统一 ceiling reference plane，所有下挂件的 z 方向都从该平面向下布置。
3. `hinged_diffuser`：在 fixed housing 上建立 diffuser / access_lens part，hinge origin 放在后侧或侧后 rim，latch 作为 visual 或可选小 prismatic/revolute part。
4. `track_spot`：根 part 为 rail；每个 head 包含 carriage -> swivel_yoke -> lamp_head 的链，slide travel 受 rail length 限制。
5. `branching_arm`：根 part 为 canopy hub；每个 arm 按 `arm_layout` 分布，shade 挂在 arm tip hinge。
6. `pull_down_pendant`：canopy -> cord prismatic -> shade continuous spin；lock button 挂在 canopy side pocket。
7. 非活动 trim、screws、socket、bulb、rings 作为所属 part 的 visual，不创建独立 part。

## 已有模板写法参考
revolute_hinge / prismatic_slide / radial_array / handle_grip / button_slider / continuous_rotor

## 约束
- 每个实例必须有可识别 ceiling mount / canopy 或 track rail。
- 每个活动 lamp head、shade、lens 或 cord 必须有 joint metadata。
- `track_spot` 中 carriage 必须在 rail channel 内，slide 末端仍有插入 overlap。
- `hinged_diffuser` 中 hinge origin 必须在 diffuser 边缘，不得在面板中心。
- `branching_arm` 中 shade 必须低于 canopy，arm pivot 不得漂浮。
- `pull_down_pendant` 中 cord 必须穿过 canopy outlet，shade 必须挂在 cord 下端。
- 灯体必须包含 lens / diffuser / bulb / LED board 中至少一种发光识别件。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 存在 ceiling mount / canopy / rail 和至少一个 light housing / shade / head |
| joint count | 按 `fixture_layout` 至少 1 个活动 joint；track/branching layout joint 数与 head / arm 数一致 |
| axis check | hinge `(1,0,0)`；track slide `(1,0,0)`；pendant slide `(0,0,-1)`；head tilt 水平轴 |
| mount attachment | 所有活动件最终连接到 root mount / canopy / rail |
| no floating | carriage、arm、shade、diffuser、cord 与父件接触或合理穿入连接硬件 |
| part diversity | `fixture_layout`, `mount_style`, `shade_style` 存在并影响 part tree |
| range sanity | diffuser / shade tilt 不穿过 mount；track slide 不脱轨；cord slide 保持插入 canopy |

## Reject cases
- 没有 ceiling mount / canopy / rail，像普通台灯或落地灯。
- 只有静态灯罩，没有任何可动 lens、head、arm、cord 或 service part。
- hinge / tilt origin 在几何中心导致面板或灯头绕自身乱转。
- track head 滑出轨道或 carriage 漂浮。
- pendant cord 与 canopy outlet 脱离。
- branch arms 的 shade 穿过 canopy 或悬空在 arm 外。
- 只靠颜色变化表达类别差异，忽略布局和灯罩形态。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核；当前仅为 SPEC_ONLY_DRAFT，未进入模板实现阶段。 |
