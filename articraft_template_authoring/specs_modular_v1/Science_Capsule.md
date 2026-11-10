# Modular Spec — Science / Capsule

## 元信息
| 项 | 值 |
|---|---|
| slug | `capsule` |
| template path | `agent/templates/Science_Capsule.py` |
| stage | `TEMPLATE_AFTER_REVIEW_REVISION` |
| status | `realism_reworked` |
| __modular__ | `True` |
| pattern | `parallel slots`: Primary Form Family × seam/closure feature × surface feature |

## 核心身份

本模板限定为 **现实药用两片式硬胶囊**：较小的 `capsule_body` 和较大的
`capsule_cap` 都是中空 gelatin / HPMC shell，cap 沿长轴套在 body 上，闭合处可轴向拉开。

不再把同名 “capsule” 扩展到相邻对象：

- 不要 `screw_thread_revolute`：螺纹旋盖属于药瓶/容器语义，不是普通硬胶囊。
- 不要 `segment_count > 2`：3/4 节 telescoping chain 像伸缩管，不是药丸外壳。
- 不要 `bullet_tip`：锥尖会读成弹头/特殊容器。
- 不要 `flat_caplet`：方端 caplet 属于片剂/软胶囊邻域，和两片式硬胶囊的半球壳不同。
- sealed softgel 是单片融合壳、0 joint，可作为相邻类别但不进入本模板。

模板的真实骨架固定为：

```
capsule_body (root) -- body_to_cap PRISMATIC axis(-X) --> capsule_cap
```

所有合法 seed 都保留这一关节；多样性来自真实主体形态、接缝锁合细节和表面制造/识别特征。

## 5 星样本与世界知识外推

原始 parent 样本 `rec_build-a-realistic-articulated-3d-model-of-a-caps_...`
提供真实骨架：`capsule_body`、`capsule_cap`、单个 `body_to_cap` PRISMATIC 关节、
中空 shell、cap/body 双色和 imprint。

旧 variant 中仅保留与现实硬胶囊一致的部分：

| 旧来源 | 保留 | 处理 |
|---|---|---|
| parent dome + plain telescope | body/cap skeleton、PRISMATIC seam、imprint、双色材质 | 作为基准 |
| lockband variant | body groove + cap locking band | 收敛为 `snap_lock_ring` / `double_lock_rings` |
| flatcap / bulletip | 不保留 | 形态越界 |
| screwcap | 不保留 | closure 机制越界 |
| seg3 / seg4 | 不保留 | multiplicity 越界 |

新增的主体形态家族使用 `world_knowledge_extrapolation`：仍保持同一 part tree、同一
PRISMATIC joint、同一 CadQuery shell primitive，只改变离散 envelope / proportion。现实依据是
硬胶囊标准尺寸家族、临床盲法 over-encapsulation 胶囊、Coni-Snap / Snap-Fit 系列的锁合细节、
液体填充硬胶囊的 seam banding，以及排气/定位 dimples。

## Slot A — Primary Form Family / 主体形态家族

| module_name | source policy | 结构特征 |
|---|---|---|
| `standard_size0` | parent-backed | 标准两片式药用硬胶囊，body 较长、cap 较短，半球端，典型 size 0 比例 |
| `short_wide_blinding` | world-knowledge extrapolation | 短粗 over-encapsulation / blinding 胶囊，用于包住对照片剂或另一胶囊；直径更大、总长更短 |
| `long_slender_000` | world-knowledge extrapolation | 大号 000 风格，细长比例明显，仍是 cap/body 两片壳 |
| `small_compact_size4` | world-knowledge extrapolation | 小号紧凑胶囊，整体短小但保留 cap/body 套合 |

这些是主体 envelope 差异，不是连续 scale：每个 family 有离散的半径、body tube、cap tube 基准比例。
连续参数 `diameter_scale` / `length_scale` 只在 family 内做轻微扰动。

## Slot B — Seam / Closure Feature

| module_name | 关节 | emits | 现实语义 |
|---|---|---|---|
| `plain_overlap` | `body_to_cap` PRISMATIC | cap 直接套 body，无额外硬件 | 普通两片胶囊的基本闭合 |
| `snap_lock_ring` | `body_to_cap` PRISMATIC | body mouth 环形 groove + cap mouth 单 lock band | Coni-Snap / Snap-Fit 类锁合环 |
| `double_lock_rings` | `body_to_cap` PRISMATIC | 双 groove + 双 cap lock bands | 更强保持力的双锁环闭合 |
| `liquid_seal_band` | `body_to_cap` PRISMATIC | seam 外侧 bonded sealing band | 液体/半固体填充硬胶囊的封带语义 |

所有 seam feature 都必须保持轴向拉开；不允许 REVOLUTE screw cap。

## Slot C — Surface / Manufacturing Feature

| module_name | emits | 现实语义 |
|---|---|---|
| `printed_code` | cap 侧面 `cap_imprint` | 药品编号/识别码 |
| `vent_dimples` | body 近 mouth 的浅排气/定位凹点 | 生产闭合时排气/定位细节 |
| `orientation_bands` | cap/body 印刷环带 | 识别/方向/批次 banding，非结构关节 |

这些都是 parent visual，不新增 FIXED decoration part；对应 overlap 必须 element-scoped。

## 参数范围

| 参数 | 类型 | 范围 / 候选 | 约束 |
|---|---|---|---|
| `body_form_family` | enum | 4 family | Primary Form Family slot |
| `seam_feature` | enum | 4 seam modules | 全部 PRISMATIC，禁止 screw |
| `surface_feature` | enum | 3 surface modules | 不改变关节 |
| `palette_style` | enum | 6 realistic capsule colorways | 每 seed 采样，所有 visual 材质从 palette dict 取 |
| `diameter_scale` | float | `[0.94, 1.08]` | family 内轻微变化 |
| `length_scale` | float | `[0.92, 1.10]` | family 内轻微变化 |
| `seat_overlap` | float | `[0.0020, 0.0034]` | seated 时 cap/body 有真实 retained insertion |
| `separation_travel` | derived | `max(0.009, seat_overlap + radius + margin)` | max pose 能完全拉开 |
| `ground_lift` | derived | `cap_outer_r` | 胶囊躺在桌面，最低点 z=0 |

## Slot Graph

```
[body_form_family] --> solves radius/body_len/cap_len/ground_lift
        |
        v
capsule_body -- body_to_cap(PRISMATIC -X) --> capsule_cap
        ^                    ^
        |                    |
 [seam_feature]       [surface_feature]
 groove/ring/band     imprint/vents/orientation bands
```

接口约束：

- `capsule_body` root：mouth 在 x=0，tube + dome 延 +X。
- `capsule_cap` child：同 helper 生成后 `.mirror("YZ")`，mouth 朝 +X，闭合时套住 body mouth。
- `body_to_cap` origin = `(seat_overlap, 0, ground_lift)`，axis = `(-1,0,0)`。
- seated pose 必须有 cap/body x-overlap；max travel 必须有 x-gap。
- seam / marking / banding 都是 element-scoped intentional overlaps，不允许 broad part-level mask。

## 组合数与多样性审计

结构组合数：

`body_form_family(4) × seam_feature(4) × surface_feature(3) = 48 distinct`

这 48 个组合全部保持真实两片式硬胶囊身份，比旧版 `screw + chain + bullet` 更少跑偏。

采样策略：

1. 均匀采 `body_form_family`
2. 均匀采 `seam_feature`
3. 均匀采 `surface_feature`
4. 均匀采 `palette_style`
5. 采轻微连续 scale

## Validator

- 模板必须只生成 `capsule_body` + `capsule_cap` 两个 part。
- 必须只有一个非 FIXED 关节：`body_to_cap` PRISMATIC axis `(-1,0,0)`。
- 不允许 REVOLUTE screw seam。
- 不允许 `segment_{i}` 多段链。
- `short_wide_blinding` 的 body aspect 要明显短粗；`long_slender_000` 的 body aspect 要明显细长。
- `snap_lock_ring` / `double_lock_rings` 必须有 `cap_lock_bands`。
- `liquid_seal_band` 必须有 `liquid_seal_band`。
- `vent_dimples` 必须有 `body_vent_dimples`。
- `orientation_bands` 必须同时有 body/cap band。
- seated pose 验证 overlap + concentric；max travel 验证 gap。

## Reject Cases

- `screw_thread_revolute`：药瓶/容器，不是硬胶囊。
- `segment_count > 2`：伸缩管，不是 pill capsule。
- `bullet_tip`：弹头语义。
- `flat_caplet`：片剂/软胶囊邻域。
- sealed softgel：0 joint 单片壳，另开类别。
- 只靠颜色/scale 当结构多样性：不算 Primary Form Family。

## 当前实现备注

- `Science_Capsule.py` 已删除旧的 `EndCapProfile` / `segment_count` / screw path。
- 新增类型：`BodyFormFamily`、`SeamFeature`、`SurfaceFeature`。
- 保留 CadQuery 中空 shell，不退化成 box/cylinder。
- `run_capsule_tests` 对每个 slot 的关键 visual 和关节语义做 author-layer 检查。
