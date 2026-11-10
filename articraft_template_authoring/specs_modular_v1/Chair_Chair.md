# chair — Modular Spec

> 来源小类：`picture/Chair/Chair`。
> 上游 source map：`picture_expansion/template_source_maps/Chair__Chair.md`。
> 本模板现只覆盖 **stool / 简单单座椅**：单个 `seat` + 可选低背 `wrap_tub` + 一套 base/support。
> **不再承接** 高背办公椅、扶手、独立 recline、升降扶手；这些语义已迁移到 `Other_armchair`。

## 元信息
| 项 | 值 |
|---|---|
| slug | `chair` |
| template path | `agent/templates/Chair_Chair.py` |
| pattern | `mixed` |
| __modular__ | `True` |

## Summary
- 核心身份：single-seat chair / stool。
- 允许的真实运动：`seat_swivel` CONTINUOUS +Z；caster bases 额外允许 `caster_roll_*` 与 `base_swivel`。
- 禁止的语义：独立高背 part、扶手机构、recline 机构、office/armchair 高背外观。
- 原高背网背办公椅迁移资产已从本小类移出，不再作为 `Chair_Chair` 来源样本。

## Slot Structure

### Slot A: `base_support`
- `pedestal_disc`
- `sled_runner`
- `four_leg_dining`
- `tripod_pedestal`
- `caster_star`
- `caster_star_no_bearing`

说明：
- 这是主机构槽，决定 root part 与支撑 joint 拓扑。
- `caster_count` 只在 caster bases 上生效。
- `radial_support_count` 只在 `tripod_pedestal` 上生效。

### Slot B: `backrest`
- `none`
- `wrap_tub`

说明：
- `none` = backless stool。
- `wrap_tub` = seat inline visual，无独立 part / joint。

### Slot C: `seat_plan`
- `round`
- `square_rounded`

说明：
- 只决定坐面 mesh family，不引入额外 articulation。

## Public Types / Runtime Contract
- `Backrest = Literal["none", "wrap_tub"]`
- `BACKRESTS = ("none", "wrap_tub")`
- 模板输出中不应出现：
  - `backrest_frame`
  - `backrest_recline_hinge`
  - `left_armrest_height`
  - `right_armrest_height`
  - 任意 `armrest_*` part

## Sampling / Compatibility
- `base_support`、`backrest`、`seat_plan` 独立采样，再按底座类型解析 `caster_count` / `radial_support_count`。
- `wrap_tub` 在 sled / dining / tripod 上允许通过抬高 back base 避让支撑件。
- `seat_plan` 与所有 `base_support` 正交。
- `backrest=none` 与所有底座兼容。

## Test Expectations
- 多 seed 下只会出现 `backrest in {"none", "wrap_tub"}`。
- 所有底座都必须有 `seat_swivel` CONTINUOUS +Z。
- caster bases 必须保留脚轮滚动 articulation；tripod 必须保留 N 条放射腿 inline visuals。
- chair 产物不得再读作 armchair / office chair。

## Migration Notes
- 迁移后的高背网背办公椅资产已从 `Chair/Chair` 的 source/spec/template 中删除。
- 该资产现按小类绑定迁移到 `Other/armchair`，作为 armchair 侧 office 语义资产的一部分管理。
