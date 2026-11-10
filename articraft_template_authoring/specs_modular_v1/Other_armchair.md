# armchair — Modular Spec

> 来源小类：`picture/Other/armchair`。
> 上游 source map：`picture_expansion/template_source_maps/Other__armchair.md`。
> `"armchair"` 在此 = 带扶手的单座软包坐具，覆盖 lounge / office / gaming / pod chair。

## 元信息
| 项 | 值 |
|---|---|
| slug | `armchair` |
| template path | `agent/templates/Other_armchair.py` |
| pattern | `mixed` |
| __modular__ | `True` |

## Summary
- 核心身份：`seat + backrest + armrest + support/recline system`。
- 运行时保留四条主轴：
  - `chair_form`
  - `base_support`
  - `recline_mechanism`
  - `armrest`
- `office_mesh` 现在以 **blue-mesh adjustable-arm office chair** 为默认基线表达。
- 从 `Chair_Chair` 迁移来的 `rec_chair_var_blue_mesh_prismatic_armrests_codex_redo` 已绑定到 `Other/armchair` 小类，不再属于 `Chair/Chair`。

## Slot Structure

### Slot A: `chair_form`
- `winged_lounge`
- `egg_pod`
- `office_mesh`
- `racing_bucket`

说明：
- `office_mesh` 是吸收后的 office 主形态。
- 默认 palette 会落到 blue/teal mesh 风格，匹配迁移过来的资产语义。

### Slot B: `base_support`
- `five_star_caster`
- `four_wood_legs`
- `cantilever_sled`

说明：
- `five_star_caster` 现在保留两层旋转语义：`pedestal_anchor_to_base` 只控制五爪带轮底座绕 `+Z` 旋转；气压柱和座位走独立分支，座面上方仍保留 `lift_piston_to_seat` under-seat swivel。

### Slot C: `recline_mechanism`
- `swivel_tilt`
- `rocker_glider`
- `full_recliner_footrest`

### Slot D: `armrest`
- `fixed_arms`
- `flip_up`
- `height_adjust`

说明：
- `height_adjust` 仍然是 armchair 自身标准机构槽，不再借道 `Chair_Chair` 的派生高背逻辑。

## Public Interfaces / Runtime Contract
- `ChairForm`、`Armrest` 等 public enum 名称保持不变。
- `office_mesh` 不新增第五种 `chair_form`，而是直接替换 office 语义的主基线。
- `height_adjust` 仍输出 `seat_to_armrest_{i}` PRISMATIC +Z。

## Compatibility
- `caster_count` 仅在 `five_star_caster` 生效。
- `egg_pod` 强制 `fixed_arms`。
- `rocker_glider` 仅在有 swivel spine 的底座上保持；不兼容时降级到 `swivel_tilt`。
- `full_recliner_footrest` 当前只保留在 `five_star_caster` 上；落到 `four_wood_legs` / `cantilever_sled` 时降级到 `swivel_tilt`，避免 visitor-chair 底座挂出不合理的脚托导轨包。
- `office_mesh` 应兼容 `fixed_arms / flip_up / height_adjust` 三种 armrest 路径。

## Migration Notes
- 已修正 armchair 侧旧 source map 引用路径。
- `rec_chair_var_blue_mesh_prismatic_armrests_codex_redo` 作为小类资产迁入 `Other/armchair`：
  - 从 `Chair__Chair.jsonl` 移除
  - 插入 `Other__armchair.jsonl`
  - record 自身的 `picture.json` 绑定到 `picture/Other/armchair/003.png`
  - lineage 改为 root，不再作为 `Chair_Chair` fork 出现
- 当前 hydrated record 目录已按 `Other/armchair` 原始资产语义同步；模板侧 `office_mesh` 以该 blue-mesh + recline + height-adjust armrest 资产作为 office 基线表达。

## Test Expectations
- `office_mesh + five_star_caster + height_adjust` 应稳定生成 blue-mesh 办公椅语义。
- `fixed_arms`、`flip_up`、`height_adjust` 都要继续通过。
- 非 office forms 不应被 blue-mesh 默认色或机构错误污染。
