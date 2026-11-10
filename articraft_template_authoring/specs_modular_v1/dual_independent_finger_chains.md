# Dual Independent Finger Chains Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `dual_independent_finger_chains` |
| template path | `agent/templates/dual_independent_finger_chains.py` |
| test path (optional) | — |
| stage | `TEMPLATE_AFTER_REVIEW` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 |
| read_count | 33 |
| read_scope | 类别内全部 33 个 5 星样本：`record.json` / `revision.json` / `model.py` / prompt 已汇总阅读 |
| source_index_policy | 仅索引下方采纳的 module source |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| 2 链 × 2 节指骨（proximal + distal） | 18 | 左右镜像 REVOLUTE，轴 ±Z 或 ±Y |
| 2 链 × 3 节指骨 | 9 | 多一节 middle phalanx；本模板不采纳为可变 N |
| 单链或 3+ 链 | 4 | 超出本类别固定 multiplicity 边界 |
| palm 为 mounting plate / gripper block | 33 | 全部样本均有固定 palm chassis |

被采纳样本（逐条）：
- `rec_dual_independent_finger_chains_6c5941a465a54d3b8b06b20bb48f0092` — adopted：top_support + palm_block + 双链 3 节；左右 knuckle 轴镜像。
- `rec_dual_independent_finger_chains_92a390a81e5d404fab896964f0450b0f` — adopted：compact palm + 2 链 2 节 box phalanx。
- `rec_dual_independent_finger_chains_b84133f45bc744d1bf924cf3a803c254` — adopted：pedestal palm + barrel hinge links。
- `rec_dual_independent_finger_chains_0001`（seed=0 参考）— adopted：2 链 × 2 节，左 −Z / 右 +Z。

## 核心身份

一个 **palm chassis** 上固定安装 **两条互不耦合的指链**；每条链 **恰好 2 个 REVOLUTE 指节**（proximal → distal）。左右链各自独立运动，不得串成单链或共轴转子。

边界：
- 不包括 `robotic_leg` / `twojoint_revolute_chain` 单链串联。
- 不包括 3+ 指或 1 指的 gripper（本类别 multiplicity 写死为 2×2）。
- 不包括 PRISMATIC 滑动指节（本类别仅 REVOLUTE）。

## 槽位 + 候选模块表

### Slot A：palm_chassis

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `compact_gripper_palm` | S2 | `L160-L181` | eligible | 扁平方块 palm + 顶面 root socket |
| `mounting_plate_palm` | S1 | `L168-L181` | eligible | 顶板 + 侧肋 mounting plate |
| `pedestal_palm` | S3 | `L160-L175` | eligible | 抬高底座 + 窄顶面 |
| `tray_backplate_palm` | S1 | `L175-L181` | eligible | 背板托盘式 palm |

### Slot B：phalanx_profile

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rounded_box_phalanx` | S2 | `L182-L212` | eligible | box body + root barrel |
| `barrel_hinge_phalanx` | S3 | `L182-L200` | eligible | 圆柱铰链桶 + web |
| `sideplate_phalanx` | S1 | `L182-L227` | eligible | 双侧板 + spine |
| `tapered_box_phalanx` | S2 | `L196-L227` | eligible | 上下渐缩 box |

### Slot C：finger_layout（module-local variant）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `narrow` | S2 | root spacing | eligible | 链间距 ×0.82 |
| `standard` | S1 | root spacing | eligible | 锚点间距 |
| `wide` | S3 | root spacing | eligible | 链间距 ×1.22 |

### Slot D：material_palette

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `palm_gray_aluminum` | S1 | palette | eligible | 灰铝 + 蓝 accent |
| `dark_polymer` | S2 | palette | eligible | 深色聚合物 |
| `anodized_blue` | S3 | palette | eligible | 蓝色阳极 |
| `warm_bronze` | S1 | palette | eligible | 青铜暖色 |

## 槽位图（slot graph）

pattern = `mixed`（parallel_children + fixed multiplicity）

```
[Slot A palm_chassis] (grounded)
    |-- REVOLUTE, axis (-Z left / +Z right) --> [left_proximal]
    |       -- REVOLUTE --> [left_distal]
    |-- REVOLUTE, axis (+Z) -----------------> [right_proximal]
            -- REVOLUTE --> [right_distal]
```

- `finger_chain_multiplicity`：**固定 2**，不采样。
- `phalanx_multiplicity`：**固定每链 2**，不采样。
- Slot C 只改变 root_x 偏移，不改变关节数。

## 每槽位 Module Emits / Interfaces

### Slot A / compact_gripper_palm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `palm` | S2 |
| internal joints | — | — |
| downstream interface | 左右 root socket @ palm 顶面 | S1 L247-L273 |

### Slot B / rounded_box_phalanx
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_proximal`, `left_distal`, `right_proximal`, `right_distal` | S2 |
| internal joints | `left_proximal_to_distal`, `right_proximal_to_distal` REVOLUTE | S2 |
| upstream interface | pivot_hub @ phalanx 根部 | template |

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `palm_style` | enum | 4 palm modules | `compact_gripper_palm` | Slot A | S1-S3 |
| `link_profile` | enum | 4 phalanx modules | `rounded_box_phalanx` | Slot B | S1-S3 |
| `finger_spacing` | enum | narrow / standard / wide | `standard` | Slot C | S1-S3 |
| `material_style` | enum | 4 palettes | `palm_gray_aluminum` | Slot D | S1 |
| `palm_width` | float | 0.06–0.12 | 0.082 | 派生 root_x | S1 |
| `proximal_limit` | float | 0.30–0.55 | 0.42 | REVOLUTE 行程 | S1 |
| `distal_limit` | float | 0.22–0.45 | 0.34 | REVOLUTE 行程 | S1 |

## Multiplicity / Copy Logic

| 项 | 值 |
|---|---|
| `finger_chain_multiplicity` | **固定 2**（`2_independent_chains`）；左右各一条链，各有独立 REVOLUTE 根关节 |
| `phalanx_multiplicity` | **固定 2**（`2_phalanxes_per_chain`）；proximal + distal，无 middle 节 |
| joint policy | 每条链 2 个 REVOLUTE；左右根轴镜像（左 −Z，右 +Z） |
| naming | `left_proximal`, `left_distal`, `right_proximal`, `right_distal` |
| source/gating | 5 星样本中 3 节链不进入采样域；reviewer 确认本类别锁定 2×2 |

## 拓扑多样性审计

总组合数：4 × 4 × 3 × 4 = **192**（multiplicity 固定，不计入乘积）


seed_domain_policy：procedural_first

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `config_from_seed` 随机 palm / link / spacing / palette | `slot_choices_for_seed` 与 build 一致 |
| compatibility matrix | 全组合合法；multiplicity 不采样 | 4 链 4 关节恒存在 |
| controlled local variation | palm/proximal/distal 尺寸 clamp | 比例变化不破坏 pivot_hub 连通 |
| regression overrides | none | — |
| random sweep | seeds 0–49 | origin/island |

| slot | candidate_count | ≥2 | ≥3 |
|---|---:|---|---|
| palm_chassis | 4 | yes | yes |
| phalanx_profile | 4 | yes | yes |
| finger_layout | 3 | yes | yes |
| material_palette | 4 | yes | yes |

## Validator

- `slot_choices_for_seed` 导出 `finger_chain_multiplicity` / `phalanx_multiplicity` 固定字符串
- 恰好 4 个 phalanx part + 4 个 REVOLUTE（2 root + 2 inter-phalanx）
- `fail_if_articulation_origin_far_from_geometry(tol=0.020)`
- pivot_hub 与 phalanx body 几何连通（无 island）

## Reject cases

- 链数 ≠ 2 或每链节数 ≠ 2
- 左右链共轴或串联成单链
- 根关节非 REVOLUTE 或左右轴未镜像
- phalanx 浮岛 / pivot_hub 断开
- 把 PRISMATIC 滑动指混入本类别

## 与相邻类别的边界

- `twojoint_revolute_chain`：单链 2 节，无双独立链
- `robotic_leg`：3+ 节 + 更多自由度
- `branching_tree_with_three_independent_rotary_branches`：转轴分支，非指状链

## 模板实现备注（可选）

- 模板已在 spec 前实现并通过 `sweep-pipeline` 50/50；spec 为 retroactive 对齐。
- `hub_seam` 用于 phalanx pivot 与 body 连通性。
- 实现文件：`agent/templates/dual_independent_finger_chains.py`

## Module Source Index

| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_dual_independent_finger_chains_6c5941a465a54d3b8b06b20bb48f0092` | `L160-L301` | palm + 双链关节拓扑 |
| S2 | `rec_dual_independent_finger_chains_92a390a81e5d404fab896964f0450b0f` | `L160-L280` | compact palm + box phalanx |
| S3 | `rec_dual_independent_finger_chains_b84133f45bc744d1bf924cf3a803c254` | `L160-L280` | pedestal + barrel hinge |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | **approved** |
| reviewer notes | 用户确认 spec 通过（2026-06-07）。模板已对齐实现并通过 sweep-pipeline 50/50（34 distinct topology）。固定 2 链 × 2 节、四 slot 候选、左右 ±Z 轴策略已签收。 |
