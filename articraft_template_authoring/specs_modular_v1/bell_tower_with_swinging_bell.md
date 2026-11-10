# Bell Tower With Swinging Bell Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `bell_tower_with_swinging_bell` |
| template path | `agent/templates/bell_tower_with_swinging_bell.py` |
| test path | `tests/agent/test_bell_tower_with_swinging_bell_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 38 |
| read_count | 38 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / `prompt.txt` were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 32 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| open frame / belfry cote + one swinging bell | 17 | 木架、钢架、Alpine cote、四柱 frame；主关节为 tower/frame -> bell REVOLUTE |
| masonry / church / campanile tower + belfry opening | 9 | 方形或圆形塔身、Gothic/campanile/onion-dome，bell 在开口中水平轴摆动 |
| cupola / rooftop bell tower | 1 | roof plate + cupola FIXED，再 cupola -> bell REVOLUTE |
| garden post / harbor post | 3 | 单柱或简化 post + crossarm，bell 悬挂摆动 |
| multi-bell / carillon | 4 | 同一 tower/frame 下多 bell 或 helper 内多 bell，仍是水平轴摆动 |
| bell + clapper / striker secondary motion | 15 | clapper 或 external striker 作为第二 REVOLUTE；若 bell 固定而只有 clapper 动，则不作为 procedural sampling marker |
| rope pulley / guide wheel auxiliary motion | 2 | guide wheel / pulley CONTINUOUS 为可选附属运动，不是类别主身份 |

被采纳样本逐条标注：
- `rec_bell_tower_with_swinging_bell_0003` — adopted：四柱焊接钢 frame、X bracing、bell shell、yoke arms、frame -> bell REVOLUTE。
- `rec_bell_tower_with_swinging_bell_0004` — adopted：roof plate + octagonal cupola + louver panels + bell + fixed clapper。
- `rec_bell_tower_with_swinging_bell_2f0ad6cf7c17417ab1291268aa663643` — adopted：raked timber bell cote、arched yoke、hanger cheek、bell + independent clapper REVOLUTE。
- `rec_bell_tower_with_swinging_bell_80aac230bfe74f47bf1eecb678386cdc` — adopted：Gothic stone belfry tower、pointed arches、multi-bell helper。
- `rec_bell_tower_with_swinging_bell_65f83abb46784f14a516d52ad4095a57` — adopted：masonry tower + swing bell + separate guide wheel CONTINUOUS。
- `rec_bell_tower_with_swinging_bell_d362039f24d341dd934698320851a0c0` — adopted：Japanese bonsho frame + suspended bell + external striker REVOLUTE。
- Remaining 32 samples — read but not adopted: fall into the same structural families above or only add material, roof, ornament, axis sign, or CAD implementation variants without new reusable topology.

## 核心身份
`bell_tower_with_swinging_bell` 是一个承载钟体的塔、亭、壁架或 belfry frame，核心识别点是静态支撑结构里悬挂一口可摆动 bell，bell 或 bell+yoke 绕水平轴作 REVOLUTE 摆动。默认成熟域应包含可辨认的 tower/frame/cupola/post、bell shell、pivot/yoke 或 hanger，以及主 swing joint。clapper、external striker、guide pulley、louver、roof/spire、open arch 和 service details 是可选扩展，不能替代主 bell swing。

边界：
- 不包括固定钟体、只有 clapper 摆动的 stationary bell installation，除非作为可选降级变体并明确主类别仍有 swinging bell seed。
- 不混入 wind chime / gong stand：必须是 bell tower/belfry 语义，bell 是钟形壳体而不是平面 gong。
- 不混入 clock tower：clock face 可作为装饰，但核心运动必须是 bell swing。
- 不混入 church building：完整教堂体量不是必要身份，重点在 belfry/tower 和 bell articulation。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_bell_tower_with_swinging_bell_0003` | `data/records/rec_bell_tower_with_swinging_bell_0003/revisions/rev_000001/model.py:L43-L118,L133-L405` | steel frame helper、X bracing、bell shell/yoke、主 REVOLUTE swing |
| S2 | `rec_bell_tower_with_swinging_bell_0004` | `data/records/rec_bell_tower_with_swinging_bell_0004/revisions/rev_000001/model.py:L82-L192,L201-L420` | octagonal cupola / roof plate / louver shell、cupola -> bell REVOLUTE、clapper FIXED |
| S3 | `rec_bell_tower_with_swinging_bell_2f0ad6cf7c17417ab1291268aa663643` | `data/records/rec_bell_tower_with_swinging_bell_2f0ad6cf7c17417ab1291268aa663643/revisions/rev_000001/model.py:L31-L98,L102-L276` | timber cote、arched yoke、hanger cheeks、bell + clapper dual REVOLUTE |
| S4 | `rec_bell_tower_with_swinging_bell_80aac230bfe74f47bf1eecb678386cdc` | `data/records/rec_bell_tower_with_swinging_bell_80aac230bfe74f47bf1eecb678386cdc/revisions/rev_000001/model.py:L30-L211,L223-L441` | Gothic tower body、pointed arch openings、multi-bell assembly helper |
| S5 | `rec_bell_tower_with_swinging_bell_65f83abb46784f14a516d52ad4095a57` | `data/records/rec_bell_tower_with_swinging_bell_65f83abb46784f14a516d52ad4095a57/revisions/rev_000001/model.py:L22-L67,L102-L331` | masonry tower + pyramid roof、bell shell、optional guide wheel CONTINUOUS |
| S6 | `rec_bell_tower_with_swinging_bell_d362039f24d341dd934698320851a0c0` | `data/records/rec_bell_tower_with_swinging_bell_d362039f24d341dd934698320851a0c0/revisions/rev_000001/model.py:L34-L58,L66-L262` | Japanese bonsho post-and-beam frame、external striker REVOLUTE |

## 槽位 + 候选模块表

### Slot A：support_structure
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `steel_x_braced_frame` | S1 | `model.py:L133-L348` | eligible if compatible | 四柱 frame、baseplate、top beam、X bracing、pivot plates，开放式工业 bell tower |
| `octagonal_rooftop_cupola` | S2 | `model.py:L201-L316` | eligible if compatible | roof_plate + octagonal cupola + louver panels，cupola FIXED 到 roof |
| `raked_timber_cote` | S3 | `model.py:L102-L165` | eligible if compatible | 双 raked upright + gabled apex + arched yoke support，窄 timber bell cote |
| `gothic_masonry_belfry` | S4 | `model.py:L223-L441` | eligible if compatible | stone shaft、pointed arch / octagonal spire、可容纳多 bell 的 belfry tier |
| `japanese_post_beam_pavilion` | S6 | `model.py:L66-L168` | eligible if compatible | 重 timber post-and-beam frame，适合 bonsho bell + striker |

### Slot B：bell_and_yoke
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bronze_bell_with_steel_yoke` | S1 | `model.py:L86-L118,L348-L399` | eligible if compatible | lathe bell shell、front/back yoke arm、boss、crossbar，bell_assembly 整体 swing |
| `arched_hanger_bell` | S3 | `model.py:L31-L98,L165-L256` | eligible if compatible | bell shell + arched yoke + hanger cheeks，bell 与 clapper 分别为 part |
| `cupola_cast_bell` | S2 | `model.py:L166-L192,L328-L383` | eligible if compatible | cupola 内 bell + fixed clapper visual/part，适合小 rooftop cupola |
| `bonsho_suspended_bell` | S6 | `model.py:L34-L58,L175-L211` | eligible if compatible | 直壁 bonsho-style shell，无西式大 yoke，配 external striker |

### Slot C：secondary_motion
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | S1 | `model.py:L399-L405` | eligible if compatible | 只有主 bell REVOLUTE，最稳健 |
| `internal_clapper_revolute` | S3 | `model.py:L213-L276` | eligible if compatible | clapper part 挂在 bell 下，绕同水平轴小角度摆动 |
| `external_striker_revolute` | S6 | `model.py:L211-L262` | eligible if compatible | striker 挂 frame，绕反向水平轴撞 bell |
| `guide_wheel_continuous` | S5 | `model.py:L309-L331` | eligible if compatible | guide_wheel / pulley 在 tower 上 CONTINUOUS，辅助 rope guide |

## 槽位图（slot graph）
pattern = `mixed`

```
[Slot A support_structure]  -- REVOLUTE horizontal hinge line --> [Slot B bell_and_yoke]
             |
             +-- optional REVOLUTE --> [Slot C internal_clapper or external_striker]
             |
             +-- optional CONTINUOUS --> [Slot C guide_wheel]
```

主约束基准是 belfry 开口中的水平 pivot line。bell shell、yoke arms、hanger cheeks、bearing plates、clapper/striker origin 都必须由同一 pivot line 或 bell center 派生。

## 部件（Parts）

### Slot A / support_structure
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `frame` / `tower` / `cupola` / `pavilion` | ~8-50 | 静态承载结构：开放 frame、cupola、masonry belfry、post-beam pavilion | S1 / S2 / S3 / S4 / S6 |
| `roof_plate` | ~2 | rooftop cupola 的 roof/base 承载面 | S2 |

### Slot B / bell_and_yoke
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `bell` / `bell_assembly` / `bell_yoke` | ~5-14 | 可摆动 bell shell + yoke/crossbar/boss 或 suspended bell body | S1 / S2 / S3 / S6 |

### Slot C / secondary_motion
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `clapper` | ~2-6 | bell 内部摆锤，可 fixed 或 REVOLUTE | S2 / S3 |
| `striker` | ~4 | 外部撞木/striker，frame 上独立 REVOLUTE | S6 |
| `guide_wheel` / `pulley` | ~1-3 | 绳索导轮，tower 上 CONTINUOUS | S5 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `bell_swing` / `tower_to_bell` | REVOLUTE | A.frame/tower/cupola | B.bell | `(1,0,0)` or `(0,1,0)` | about `[-0.65, 0.65]` reviewer-gated | 主运动：bell 或 bell+yoke 绕水平 pivot line 摆动 | S1 / S2 / S3 / S4 / S5 / S6 |
| `clapper_swing` | REVOLUTE | B.bell | C.clapper | same as bell hinge | about `[-0.45, 0.45]` | 可选 internal clapper，小范围跟 bell 内部摆动 | S3 |
| `bell_to_clapper_fixed` | FIXED | B.bell | C.clapper | n/a | n/a | 小 cupola 的固定 clapper 结构 | S2 |
| `striker_swing` | REVOLUTE | A.frame | C.striker | horizontal, often opposite sign | about `[-0.55, 0.55]` | 外部 striker 朝 bell 摆动 | S6 |
| `guide_wheel_spin` | CONTINUOUS | A.tower | C.guide_wheel | horizontal | unlimited | rope guide pulley 自旋 | S5 |

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
| `support_style` | enum | `steel_x_braced_frame`, `octagonal_rooftop_cupola`, `raked_timber_cote`, `gothic_masonry_belfry`, `japanese_post_beam_pavilion` | `steel_x_braced_frame` | 选择 Slot A module | S1-S4 / S6 |
| `bell_style` | enum | `bronze_yoke`, `arched_hanger`, `cupola_cast`, `bonsho` | `bronze_yoke` | 与 support_style 合法化；bonsho 只配 pavilion/post-beam | S1 / S2 / S3 / S6 |
| `secondary_motion` | enum | `none`, `internal_clapper_revolute`, `fixed_clapper`, `external_striker`, `guide_wheel` | `none` | 决定 Slot C part/joint | S2 / S3 / S5 / S6 |
| `bell_count` | int | `1..3` | `1` | multi-bell 只在 masonry/open frame 子域采样；默认值为 1 | S4 |
| `tower_height` | float | `[1.4, 3.2]` | `2.2` | 支撑结构整体高度，派生 belfry opening 和 pivot z | S1 / S4 |
| `frame_width` | float | `[0.7, 1.8]` | `1.1` | 派生 post/arch spacing 和 bell radius 上限 | S1 / S3 |
| `bell_radius` | float | `[0.18, 0.48]` | `0.32` | 必须小于 opening half span with clearance | S1 / S3 / S6 |
| `swing_axis` | enum | `x`, `y` | `y` | 由 opening orientation / support_style 派生，不独立随机破坏 yoke | S1 / S2 / S3 |
| `roof_style` | enum | `none`, `saddle`, `pyramid`, `spire`, `cupola_roof` | `none` | support_style 限定合法值 | S2 / S4 / S5 |
| `arch_opening_style` | enum | `none`, `rectangular`, `round_arch`, `pointed_arch` | `rectangular` | masonry/cote 的 opening visual | S3 / S4 |
| `material_style` | enum | `steel`, `timber`, `stone`, `bronze_dark`, `mixed_church` | `steel` | palette 和 support_style 同步 | S1 / S3 / S4 / S6 |

## Multiplicity / Copy Logic

- `bell_count`: `N_range=1..3`, sampling domain=`all integers` but gated by `support_style in {gothic_masonry_belfry, steel_x_braced_frame}`; copied object=bell part + main swing joint + optional clapper part/joint; naming=`bell_i`, `clapper_i`, `bell_i_swing`; placement=side-by-side along pivot beam with equal spacing; source/gating=S4 multi-bell helper and carillon samples read in full; default value remains one bell.
- Module-local fixed repeats such as X braces, louvers, roof ribs, bolts, hinge cheeks, radial cap ribs, and decorative rings are baked visuals; they do not expose template-level count parameters.

## 拓扑多样性审计

总组合数：5 support modules x 4 bell modules x 5 secondary modules x 3 bell_count values = 300 before legality gating.


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| support_structure | 5 | yes | 开放钢架、cupola、timber cote、masonry tower、bonsho pavilion |
| bell_and_yoke | 4 | yes | yoke / arched hanger / cupola cast / bonsho shell |
| secondary_motion | 4 | yes | none / clapper / striker / guide wheel |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| support frame/tower | steel X-braced frame / octagonal cupola / timber cote / Gothic masonry / Japanese pavilion | no | yes | `support_style` | 拓扑、roof、opening、part tree 均不同 |
| bell shell | bronze yoke bell / arched hanger bell / straight bonsho / small cupola bell | no | yes | `bell_style` | shell profile 和 hanger 结构不能仅靠半径表达 |
| yoke / hanger | steel side arms / arched timber yoke / hanger cheeks / no western yoke | no | yes | `bell_style` + `yoke_style` derived | 决定 pivot capture 和 visual identity |
| clapper/striker | none / fixed clapper / internal clapper revolute / external striker | no | yes | `secondary_motion` | 是不同 part/joint 拓扑 |
| roof/spire | none / saddle / pyramid / pointed spire / cupola roof | no | yes | `roof_style` | 轮廓差异明显 |
| decorative braces/louvers | X braces / louvers / arch trim / ribs | no | yes | derived from `support_style` | 不作为独立随机拓扑，随 support module 派生 |
| pivot hardware | bearing plates / hanger cheeks / yoke bosses | partial | no | derived dimensions | 主要随 bell/support style 派生，连续尺寸足够 |

## 组合逻辑（Composition Logic）
1. 先由 `support_style` 建立静态 support envelope、belfry opening、pivot line、roof/top clearance。
2. 根据 pivot line 派生 bell center、yoke arm endpoints、bearing plate/cheek placement；bell radius 必须受 opening clearance 约束。
3. `bell_count > 1` 时沿 pivot beam 等距复制 bell + joint，每个 bell 的 axis 平行，不允许各自随机方向。
4. `secondary_motion` 若为 clapper，则 clapper origin 从 bell throat / pivot line 派生；若为 striker，则从 frame side post 派生撞击弧线；若为 guide_wheel，则从 tower side 的 rope path 派生。
5. Roof、louver、bracing、arch trim 作为 support visual，不创建无语义活动 part。

## 已有模板写法参考
`revolute_hinge` / `radial_array` / `single_revolute_hinge` / `lighthouse_with_rotating_beacon_assembly`（仅参考组织和 validator，不作部件来源）

## 约束
- 必须至少有一个 `bell_swing` REVOLUTE；axis 必须水平。
- bell/yoke 必须在 support opening 内，closed pose 不得穿 roof、base 或 side posts。
- bell_count 多于 1 时，所有 bell 共享同一 pivot beam 坐标系，间距必须留 clearance。
- fixed-only bell installation 不能作为默认 seed。
- guide wheel 和 striker 是可选辅助运动，不得替代主 bell swing。

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | 存在 support tower/frame/cupola/post + visible bell shell |
| main joint | 至少 1 个 REVOLUTE `bell_swing` |
| axis check | 主 swing axis 为水平 `(1,0,0)` 或 `(0,1,0)` |
| pivot placement | joint origin 位于 bell yoke/pivot 附近，不远离 bell geometry |
| no floating | bell、clapper、striker、guide wheel 均有 parent 约束 |
| diversity | `support_style`, `bell_style`, `secondary_motion` 覆盖离散分支 |
| multiplicity | `bell_count` 复制 part+joint 命名稳定，不能只复制 visual 且漏 joint |
| support clearance | bell closed pose 不穿 base/top beam/roof；multi-bell 不互穿 |

## Reject cases
- 只有钟楼或教堂，没有可摆动 bell。
- bell 固定在 frame 上，只有 clapper 动，却声称是 swinging bell。
- 主关节轴竖直，变成旋转展示件。
- bell 漂浮在 tower 外或 pivot 线不穿 yoke/bearing。
- 多个 bell 重叠或 joint origin 共享错误导致穿模。
- external striker 或 guide wheel 被当作主运动，bell 本体不动。
- 形态只靠颜色变化，support/bell 拓扑没有区别。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；未进入模板实现阶段 |
