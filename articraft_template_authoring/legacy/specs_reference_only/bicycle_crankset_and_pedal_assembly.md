# Bicycle Crankset And Pedal Assembly Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `bicycle_crankset_and_pedal_assembly` |
| template path | `agent/templates/bicycle_crankset_and_pedal_assembly.py` |
| test path | `tests/agent/test_bicycle_crankset_and_pedal_assembly_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 36 |
| read_count | 36 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
自行车中轴、曲柄和脚踏总成：中轴壳内的 spindle/crank assembly 绕主轴旋转，两侧曲柄相差约 180 度，链盘位于驱动侧，左右脚踏绕各自踏轴旋转或折叠。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_bicycle_crankset_and_pedal_assembly_0001 | `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L236-L477` | canonical bottom bracket shell, combined crankset part, chainring, opposite pedals, continuous crank and pedal spin |
| S2 | rec_bicycle_crankset_and_pedal_assembly_0008 | `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L248-L422` | modular three-piece BMX layout: separate spindle, arms, sprocket and pedal parts |
| S3 | rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca | `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L217-L324` | road double crankset: outer/inner chainrings and fixed arms on spindle |
| S4 | rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257 | `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L123-L318` | folding-bike compact crankset and pedal hinge knuckles |
| S5 | rec_bicycle_crankset_and_pedal_assembly_0006 | `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L155-L348` | MTB double rings, spider arms, clipless pedal bodies and bounded revolute spin joints |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| bottom_bracket_shell | 固定中轴壳，含 bearing cups/collars，可带少量 frame stubs | bb_shell_length: float, bb_shell_radius: float, bb_shell_style: enum | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L236-L283`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L248-L267` |
| spindle | 中轴主轴；可为 crankset 的 visual，也可为独立 part | spindle_length: float, spindle_radius: float, assembly_layout: enum | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L285-L310`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L268-L292` |
| crankset_combined | 合并式 crankset part，包含 spindle、左右曲柄、spider、链盘和 pedal bosses | crank_length: float, arm_profile: enum, chainring_count: int | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L285-L363`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L172-L303` |
| right_crank / left_crank | 模块化曲柄 part，固定在 spindle 两端，相位相差 180 度 | crank_length: float, arm_profile: enum, arm_width: float | S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L293-L332`; S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L226-L267` |
| chainring / sprocket | 驱动侧链盘；可为单盘、双盘、BMX sprocket 或 bash-guard 外环 | chainring_count: int, chainring_profile: enum, tooth_style: enum, bash_guard: bool | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L324-L346`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L334-L356`; S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L232-L260`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L202-L247` |
| left_pedal / right_pedal | 左右脚踏；可为 platform/cage、clipless、folding pedal | pedal_style: enum, pedal_width: float, pedal_length: float | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L365-L438`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L221-L318`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L304-L348` |
| spider_arms | 链盘固定蛛爪，通常为 4/5 臂或 carrier tabs | spider_arm_count: int, spider_style: enum | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L324-L346`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L192-L219`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L235-L247` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| bb_to_crank_spin | continuous or revolute | spindle axis `(1, 0, 0)` or `(0, 1, 0)` after template coordinate choice | bottom bracket center | continuous or `[-pi, pi]` | crank/spindle assembly 绕中轴旋转 | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L450-L458`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L374-L382`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L320-L328` |
| spindle_to_right_crank | fixed | spindle axis | drive-side spindle end | fixed | 模块化布局中右曲柄固定到 spindle | S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L383-L403`; S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L292-L305` |
| spindle_to_left_crank | fixed | spindle axis | non-drive spindle end, phase offset pi | fixed | 左曲柄固定到 spindle 另一端 | S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L390-L396`; S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L299-L305` |
| right_pedal_spin | continuous or revolute | pedal axle axis, parallel to spindle axis | right crank pedal eye | continuous or `[-pi, pi]` | 右脚踏绕踏轴自由旋转 | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L468-L477`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L404-L422`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L329-L338` |
| left_pedal_spin | continuous or revolute | pedal axle axis, opposite side sign allowed | left crank pedal eye | continuous or `[-pi, pi]` | 左脚踏绕踏轴自由旋转 | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L459-L468`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L338-L346` |
| pedal_fold_left/right | revolute | hinge axis near pedal inner bridge, usually `(0, -1, 0)` or local pedal-width axis | crank arm boss / folding pedal knuckle | `[0, pi/2]` | folding pedals inward fold for compact-bike variants | S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L291-L318` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| assembly_layout | enum | `combined_crankset` / `modular_three_piece` | `combined_crankset` | modular 时 spindle/arms/chainring 独立 fixed 串联 | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L285-L477`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L268-L422` |
| spindle_axis | enum | `x` / `y` | `x` | 模板坐标归一化后所有 crank/pedal joints 共轴或平行 | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L450-L477`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L374-L422` |
| crank_length | float | `0.118-0.180` | `0.170` | pedal origin radial offset | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L305-L310`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L163-L184` |
| crank_arm_profile | enum | `forged_solid` / `hollow_tapered` / `stubby_bmx` / `short_folding` | `forged_solid` | controls arm mesh/box taper and length class | S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L293-L332`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L163-L184`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L249-L303` |
| chainring_count | int | `1 / 2` | `1` | `2` creates inner+outer rings | S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L232-L260`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L208-L233` |
| chainring_profile | enum | `round_single` / `road_double` / `bmx_sprocket` / `oval_one_by` / `bash_guard` | `round_single` | ring radii and optional guard | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L324-L346`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L334-L356`; S3 / `data/records/rec_bicycle_crankset_and_pedal_assembly_32f074afe5b34845a25b71af925a3aca/revisions/rev_000001/model.py:L237-L260` |
| spider_style | enum | `none_direct_mount` / `four_arm` / `five_arm` / `solid_carrier` | `five_arm` | `spider_arm_count` derived unless direct mount | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L324-L346`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L198-L219`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L235-L247` |
| pedal_style | enum | `platform` / `cage` / `clipless` / `folding_cage` | `platform` | folding style replaces pedal spin with fold hinge or adds fold hinge | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L365-L438`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L221-L318`; S5 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0006/revisions/rev_000001/model.py:L304-L348` |
| pedal_motion_mode | enum | `spin` / `fold` / `spin_and_fold` | `spin` | folding samples use revolute fold; most samples use continuous/revolute spin | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L459-L477`; S4 / `data/records/rec_bicycle_crankset_and_pedal_assembly_5492a24e5e1541298cc2205abbcf2257/revisions/rev_000001/model.py:L291-L318` |
| crank_phase_offset | float | `pi` fixed | `pi` | left crank/pedal origin is right side + pi | S1 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0001/revisions/rev_000001/model.py:L305-L310`; S2 / `data/records/rec_bicycle_crankset_and_pedal_assembly_0008/revisions/rev_000001/model.py:L390-L396` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| bottom_bracket_shell | cartridge/pressfit/wide shell with bearing cups | no | yes | bb_shell_style | bearing cup/collar topology differs by sample |
| assembly topology | combined crankset part / modular spindle+arms+ring parts | no | yes | assembly_layout | SDK part tree differs materially |
| crank arms | forged solid / hollow tapered / short folding / stubby BMX | no | yes | crank_arm_profile | profile and boss geometry are qualitative |
| chainring | single / double / BMX sprocket / oval one-by / bash guard | no | yes | chainring_profile, chainring_count | ring count and tooth/guard form cannot be captured by radius only |
| spider | none/direct / 4-arm / 5-arm / carrier tabs | no | yes | spider_style | spider topology changes visible mounting |
| pedals | platform/cage / clipless / folding cage | no | yes | pedal_style, pedal_motion_mode | pedal body and joint type vary |
| spindle axis | x-axis / y-axis in samples | yes after normalization | no | spindle_axis | Coordinate difference should be normalized, but parameter can document output orientation |

## 组合逻辑（Composition Logic）
1. Choose `assembly_layout`. Combined layout creates `bottom_bracket_shell`, `crankset_combined`, `left_pedal`, `right_pedal`; modular layout creates `bottom_bracket_shell`, `spindle`, both crank arms, chainring/sprocket and pedals.
2. Establish a single spindle axis and derive all arm rotations and pedal origins from `crank_length` and `crank_phase_offset = pi`.
3. Place chainring only on drive side; if `chainring_count = 2`, create outer and inner rings with small axial offset.
4. Create crank spin joint first, then fixed modular joints if needed, then pedal spin/fold joints.
5. Pedal tread, bolts, collars, dust caps and tooth details are visual children of their nearest moving part.

## 已有模板写法参考
continuous_rotor / revolute_hinge / radial_array

## 约束
- Spindle/crank spin axis and both pedal axle axes must be parallel.
- Left and right crank arms must be approximately 180 degrees apart.
- Chainring/sprocket must stay on one drive side and clear the bottom bracket shell.
- Pedals must be mounted at crank ends, outboard of the arms, not near the spindle center.
- Folding pedals must hinge near the pedal eye and fold inward along the crank, not detach.
- Modular layout fixed joints must keep arms and chainring attached during crank rotation.

## Validator
| 检查项 | 标准 |
|---|---|
| crank joint | exactly 1 crank spin joint, continuous or revolute with full/near-full range |
| pedal joints | two pedal motion joints; spin pedals continuous/revolute, folding pedals revolute with upper near pi/2 |
| axis check | crank and pedal spin axes parallel after coordinate normalization |
| phase check | left/right crank pedal origins differ by about pi |
| drive side | chainring count matches parameter and sits on drive side |
| attachment | pedals attach at crank ends; no pedal floating |
| part diversity | `assembly_layout`, `crank_arm_profile`, `chainring_profile`, `pedal_style` exist |
| identity | visible bottom bracket, two crank arms, chainring/sprocket and two pedals |

## Reject cases
- Missing bottom bracket or crank spin joint.
- Pedals placed near spindle instead of crank ends.
- Left and right arms not opposed.
- Chainring centered inside shell or on both sides without parameter support.
- Pedal axes not parallel to crank axis.
- Folding pedal represented only by color or static geometry.
- Crankset looks like a generic fan/gear rather than bicycle drivetrain.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
