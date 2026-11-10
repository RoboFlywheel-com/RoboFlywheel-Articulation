# Car Axles Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `car_axles` |
| template path | `agent/templates/car_axles.py` |
| test path (optional) | — |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 40 |
| read_count | 40 |
| read_scope | 类别内全部 40 个 5 星样本已汇总阅读 |
| source_index_policy | 仅索引下方采纳 module source |

结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| 差速壳 + 左右驱动 hub CONTINUOUS ±Y | 28 | axle_housing + left/right_hub |
| 含 pinion / yoke 小齿轮法兰 | 22 | 第三 CONTINUOUS +X |
| ribbed pumpkin / boxed carrier 壳体 | 15 | 壳体外形族 |
| 辐条数 4–8 | 40 | visual spoke studs（无独立关节） |

被采纳样本：
- `rec_car_axles_beba08ed26044614a955e43349028d22` — adopted：housing + hubs + pinion_yoke。
- `rec_car_axles_f65a3b6587074c9489539768d818465f` — adopted：boxed carrier housing。
- `rec_car_axles_fde2e6bd96c9447ba21eb1b96fdb39dc` — adopted：tube axle housing。
- `rec_car_axles_0001`（seed=0 参考）— adopted：ribbed_pumpkin + machined_disk + pinion。

## 核心身份

**差速器壳体（axle_housing）** 固定于世界；**左右驱动 hub** 各一 **CONTINUOUS** 关节绕 ±Y 旋转；可选 **pinion_flange** 绕 +X 旋转。辐条为 **jointless spoke multiplicity**（每 hub 内 visual studs）。

边界：
- 不是整车底盘或悬挂弹簧（仅车轴总成）。
- 不是 `overshot_waterwheel` 水车辐条转子。
- hub 数固定 2（左右驱动），不采样 1 或 3 hub。

## 槽位 + 候选模块表

### Slot A：axle_housing

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `ribbed_pumpkin` | S4 | `L219-L291` | eligible | 南瓜形肋壳 + 侧向 axle tunnel |
| `boxed_carrier` | S2 | `L231-L290` | eligible | 箱式 carrier |
| `tube_axle` | S3 | `L231-L260` | eligible | 中心管 + saddle |
| `heavy_cast` | S1 | `L231-L300` | eligible | 重铸铁块 |

### Slot B：hub_style

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `machined_disk` | S4 | `L432-L450` | eligible | 加工盘形法兰 |
| `flanged_drum` | S1 | `L432-L448` | eligible | 宽法兰鼓形 |
| `open_face` | S2 | `L432-L445` | eligible | 开口面轮毂 |
| `stud_plate` | S3 | `L432-L445` | eligible | 耳板 + 辐条环 |

### Slot C：pinion_module

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `pinion_spin` | S4 | `L450-L518` | eligible if has_pinion | pinion_flange + CONTINUOUS X |
| `none` | — | — | eligible if ¬has_pinion | 无第三关节 |

### Slot D：material_palette

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cast_iron` | S4 | palette | eligible | seed=0 |
| `machined_steel` | S1 | palette | eligible | — |
| `fleet_gray` | S2 | palette | eligible | — |
| `matte_black` | S3 | palette | eligible | — |

## 槽位图（slot graph）

pattern = `mixed`（parallel_children + optional third child）

```
[axle_housing] (grounded)
    |-- CONTINUOUS Y --> [left_hub]
    |-- CONTINUOUS Y --> [right_hub]
    |-- CONTINUOUS X --> [pinion_flange]   (optional, gated by has_pinion)
```

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `housing_style` | enum | 4 modules | `ribbed_pumpkin` | Slot A | S4 |
| `hub_style` | enum | 4 modules | `machined_disk` | Slot B | S4 |
| `has_pinion` | bool | ~72% true | true | Slot C | S4 |
| `spoke_count` | int | 4–8 | 6 | jointless multiplicity | S1-S4 |
| `material_style` | enum | 4 palettes | `cast_iron` | Slot D | S4 |

## Multiplicity / Copy Logic

| 项 | 值 |
|---|---|
| M1 `hub_multiplicity` | **固定 2**（`2_driven_hubs`）；left_hub + right_hub，各 1×CONTINUOUS |
| M2 `spoke_multiplicity` | **jointless**；`spoke_stud_{idx}`，`idx ∈ [0, spoke_count)`，每 hub 内复制 |
| joint policy | hub：axis ±Y；pinion：axis +X |
| naming | `left_hub`, `right_hub`, `pinion_flange` |
| source/gating | 5 星样本无单 hub 车轴；不采样 1 hub |

## 拓扑多样性审计

总组合数：4 × 4 × 2 × 4 = **128**（spoke_count 另计 5 档）


seed_domain_policy：procedural_first

| item | policy |
|---|---|
| pinion gating | `has_pinion` 随机；false 时无 pinion part/joint |
| housing-hub contact | `axle_tunnel` 桥接壳体与侧管；`allow_overlap` hub_journal↔bearing boss |
| random sweep | 0–49 |

## Validator

- 固定 2 hub + 0/1 pinion
- `spoke_multiplicity` 字符串与 `spoke_count` 一致
- `fail_if_part_contains_disconnected_geometry_islands` 对 housing/hub
- hub_journal 与壳体轴承座连通

## Reject cases

- hub 数 ≠ 2
- 缺 CONTINUOUS 或轴错误（hub 非 ±Y）
- housing 侧管浮岛
- pinion 与 housing 无桥接
- 辐条与 hub 本体断连

## 与相邻类别的边界

- `wheelbarrow`：单轮 + 把手，非差速壳
- `overshot_waterwheel`：水车大转子，非车轴 hub

## 模板实现备注（可选）

- 模板已先行实现并通过 sweep 50/50（44 distinct）。
- `_add_hub_spokes` 使用 `spoke_ring` 消除辐条浮岛。
- seed=0：`ribbed_pumpkin` + `machined_disk` + pinion + 6 spokes。

## Module Source Index

| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_car_axles_beba08ed26044614a955e43349028d22` | `L219-L518` | housing + hubs + pinion 拓扑 |
| S2 | `rec_car_axles_f65a3b6587074c9489539768d818465f` | `L231-L450` | boxed carrier |
| S3 | `rec_car_axles_fde2e6bd96c9447ba21eb1b96fdb39dc` | `L231-L450` | tube axle |
| S4 | `rec_car_axles_0001` | template anchor | seed=0 |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | **approved** |
| reviewer notes | 用户确认 spec 通过（2026-06-07）。模板已对齐实现并通过 sweep-pipeline 50/50（44 distinct topology）。2 driven hubs 固定、spoke 4–8 jointless、pinion 可选已签收。 |
