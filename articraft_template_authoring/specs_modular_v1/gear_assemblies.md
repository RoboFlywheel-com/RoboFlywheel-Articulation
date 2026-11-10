# Gear Assemblies Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `gear_assemblies` |
| template path | `agent/templates/gear_assemblies.py` |
| test path (optional) | — |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 32 |
| read_count | 32 |
| read_scope | 类别内全部 32 个 5 星样本已汇总阅读 |
| source_index_policy | 仅索引下方采纳 module source |

结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| 侧架台 + 多平行轴 CONTINUOUS | 14 | frame + shaft_i spin about Z |
| 台板 + 2–4 个平行齿轮 | 11 | bench plate + pedestal per stage |
| 同轴叠放 stack | 5 | 多级 gear 共轴 stack |
| 静态齿轮组（无 spin） | 2 | 不采纳 |

被采纳样本：
- `rec_gear_assemblies_bde87ad659784ac8929fea99c8a6751e` — adopted：side_frame + 4×shaft CONTINUOUS。
- `rec_gear_assemblies_32c189269bd844e99b982bf179c0edbe` — adopted：channel plate bench。
- `rec_gear_assemblies_13db415fe2f049e48e514daa4dce5007` — adopted：heavy bench + 大齿轮。
- `rec_gear_assemblies_0001`（seed=0 参考）— adopted：open side-frame + 3 parallel stages。

## 核心身份

**gear bed / support** 承载 **N 个独立齿轮 stage**（`2..4`），每个 stage 一个 **CONTINUOUS** 自转关节（world +Z）。齿数为 **jointless visual multiplicity**（在 stage part 内复制 tooth visuals，不增加关节）。

边界：
- 不是 `coaxial_rotary_stack` 的纯同轴演示（本类别 parallel_bench 为主形态，coaxial_stack 为次形态）。
- 不是 `overshot_waterwheel` / `wind_turbine` 叶片转子。
- 每个 spin stage 必须 grounded 到 bed（平行）或经 bed 主轴连通（同轴）。

## 槽位 + 候选模块表

### Slot A：support_bed

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `open_side_frame` | S4 | `L85-L176` | eligible | 侧轨 + 中心垫 |
| `channel_plate` | S2 | `L95-L150` | eligible | 槽型台面板 |
| `heavy_bench` | S3 | `L90-L160` | eligible | 厚垫 + 质量块 |
| `compact_skid` | S2 | `L95-L130` | eligible | 脚垫 skid |

### Slot B：gear_profile

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `parallel_bench` | S4 | `L177-L220` | eligible | 相邻齿轮外缘保持小运行间隙，各 stage 由 bed 独立承载 |
| `coaxial_stack` | S1 | `L177-L220` | eligible | 共轴叠放，stage_i 父级为 stage_{i-1} 或 bed |

### Slot C：gear_stage_multiplicity（joint-bearing）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `2_spin_stages` | S2 | stage loop | eligible if N=2 | 2 关节 |
| `3_spin_stages` | S4 | stage loop | eligible if N=3 | 3 关节（seed=0） |
| `4_spin_stages` | S1 | stage loop | eligible if N=4 | 4 关节 |

### Slot D：material_palette

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `machined_steel` | S4 | palette | eligible | seed=0 默认 |
| `painted_industrial` | S2 | palette | eligible | — |
| `dark_oxide` | S3 | palette | eligible | — |
| `bronze_accent` | S1 | palette | eligible | — |

## 槽位图（slot graph）

pattern = `mixed`

**parallel_bench：**
```
[gear_bed] --CONTINUOUS Z--> [gear_stage_0]
           --CONTINUOUS Z--> [gear_stage_1]
           --CONTINUOUS Z--> [gear_stage_2] ...
```

**coaxial_stack：**
```
[gear_bed] --CONTINUOUS Z--> [gear_stage_0]
           --CONTINUOUS Z (parent-relative)--> [gear_stage_1] --> ...
```

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `gear_stage_count` | int | 2–4 | 3 | Slot C multiplicity | S1-S4 |
| `gear_profile` | enum | parallel / coaxial | `parallel_bench` | Slot B | S1,S4 |
| `support_bed` | enum | 4 modules | `open_side_frame` | Slot A | S4 |
| `tooth_counts` | tuple[int] | 每 stage 8–64 | ANCHOR (20,32,36) | visual multiplicity | S4 |
| `bed_length_scale` | float | 0.75–1.35 | 1.0 | stage X 跨度 | procedural |
| `gear_module_scale` | float | 0.75–1.35 | 1.0 | pitch_radius | procedural |

## Multiplicity / Copy Logic

| 项 | 值 |
|---|---|
| M1 `gear_stage_multiplicity` | **joint-bearing**；`gear_stage_count` ∈ [2,4]；导出 `"{N}_spin_stages"` |
| M2 `tooth_multiplicity` | **jointless**；每 stage 内 `gear_tooth_{k}` visual 循环，`k ∈ [0, tooth_count)` |
| naming | `gear_stage_{i}`, `bed_to_stage_{i}` 或 `stage_{i-1}_to_stage_{i}` |
| placement | parallel：按相邻齿轮外缘累计 X 中心距并保留约 1 mm 运行间隙；coaxial：Z 叠放 + bed 主轴 |
| joint policy | 全部 CONTINUOUS，axis (0,0,1) |

## 拓扑多样性审计

总组合数：4 × 2 × 3 × 4 = **96**（tooth 组合另计）


seed_domain_policy：procedural_first

| item | policy |
|---|---|
| coaxial gating | coaxial 需 bed 主轴 + stage 间 allow_overlap；关节原点用父坐标系相对偏移 |
| regression overrides | none |
| random sweep | 0–49 首轮；coaxial + parallel 均须 pass |

## Validator

- `tooth_multiplicity` visuals 数 = sum(tooth_counts)
- parallel：每个 `bed_to_stage_i` parent=gear_bed
- coaxial：链式 parent；`coaxial_clip` 与 bed spindle 接触
- element-scoped `allow_overlap`：bed↔stage、stage↔stage（coaxial）

## Reject cases

- stage 数 <2 或 >4
- 缺 CONTINUOUS 或轴非 +Z
- coaxial 关节原点用世界 Z 而非父相对坐标
- tooth visuals 数与 tooth_counts 不符
- parallel 相邻齿轮外缘间隙偏离约 1 mm，导致明显分离或穿入
- 齿轮 stage 与 bed 断连（isolated parts）

## 与相邻类别的边界

- `coaxial_rotary_stack`：演示用同轴多层，无齿形 bench 身份
- `traditional_windmill`：叶片转子，非齿轮齿形

## 模板实现备注（可选）

- 模板已先行实现并通过 sweep 50/50（49 distinct）。
- `coaxial_stack` 使用 `coaxial_pedestal` + `coaxial_spindle` + `coaxial_clip`。
- seed=0 锚定 `rec_gear_assemblies_0001` 参数。

## Module Source Index

| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_gear_assemblies_bde87ad659784ac8929fea99c8a6751e` | `L85-L220` | side frame + 多轴 |
| S2 | `rec_gear_assemblies_32c189269bd844e99b982bf179c0edbe` | `L85-L200` | channel bench |
| S3 | `rec_gear_assemblies_13db415fe2f049e48e514daa4dce5007` | `L85-L200` | heavy bench |
| S4 | `rec_gear_assemblies_0001` | template anchor | seed=0 三 stage 平行 |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | **approved** |
| reviewer notes | 用户确认 spec 通过（2026-06-07）。模板已对齐实现并通过 sweep-pipeline 50/50（49 distinct topology）。gear_stage_count 2–4、tooth jointless multiplicity、parallel/coaxial 双 profile 已签收。 |
