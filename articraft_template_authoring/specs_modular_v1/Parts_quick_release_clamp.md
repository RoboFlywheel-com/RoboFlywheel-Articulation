# Quick Release Clamp Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `quick_release_clamp` |
| template path | `agent/templates/Parts_quick_release_clamp.py` |
| test path | `tests/agent/test_quick_release_clamp_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | parent baseline + all 6 forked variants in this picture subcategory |
| samples_adopted_as_module_sources | 7 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | every adopted source is a workbench-only fork; only the slot it replaces is indexed below |

**Dataset-root caveat**：本小类不是常规 5 星 record family，而是 `articraft_data` 仓库内 workbench-only 的 picture-subcategory fork 集合（`collections=['workbench']`，未 promote）。基线 `1b80e476` 来自 `picture/Parts/quick release clamp/001.png`（bicycle-style QR seat clamp），6 个变体均经 `articraft fork` 从基线派生，每个只替换一个 slot。源码引用形如 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`，行号取自各 record 实际 `model.py`。

- adopted as module sources（parent + 6 variants）：
  - `rec_model-a-bicycle-style-quick-release-seat-clamp-i_20260610_085231_449555_1b80e476`（baseline，覆盖 Slot A/B/C 全部基线模块）
  - `rec_quick_release_clamp_var_pinch_collar`（Slot A）
  - `rec_quick_release_clamp_var_hinged_collar`（Slot A）
  - `rec_quick_release_clamp_var_fold_lever`（Slot B）
  - `rec_quick_release_clamp_var_hex_bolt`（Slot B）
  - `rec_quick_release_clamp_var_wing_nut`（Slot C）
  - `rec_quick_release_clamp_var_dome_nut`（Slot C）

## 核心身份

Quick release clamp 是自行车/座管风格的快拆夹环：一只刚性 `collar`（抱住 seatpost bore 的开口环/开缝环）在 -X 侧留一条 throat/slit，两脚由一根沿 Y 横穿的 `cross_bolt` 串起；`cross_bolt` 的 +Y(cap-side)端挂一套**快拆动作机构**（cam-over-center 侧扳手 / 折叠扳手 / 沉孔六角扳手），-Y(nut-side)端挂一只**可旋调节螺母**。真正的运动学是 1 条 REVOLUTE（动作机构的 cam lever / 折叠铰）+ 1 条 CONTINUOUS（adjuster nut 绕 bolt 轴自转）。手柄扳到位时杠杆压紧两脚收拢 bore，松开即可快速脱出 seatpost。

默认成熟域：金属座管夹（aluminum collar + steel cross bolt + knurled/winged/acorn nut）。

边界：
- 必须保留 quick-release 语义（cam/折叠杠杆那条 REVOLUTE）。把动作机构换成纯螺纹手拧会读成普通 hose clamp / 管箍，出类目。
- collar 必须有 throat 或 pinch slit（可套上/脱出 seatpost）。完全闭合的实心环失去夹紧功能。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_...1b80e476`（parent） | `data/records/rec_model-a-bicycle-style-quick-release-seat-clamp-i_20260610_085231_449555_1b80e476/revisions/rev_000001/model.py:L176-L295` | baseline collar + cam lever + knurled nut，共享 `cross_bolt` 脊梁与两条主 joint |
| S2 | `rec_quick_release_clamp_var_pinch_collar` | `data/records/rec_quick_release_clamp_var_pinch_collar/revisions/rev_000001/model.py:L173-L242` | Slot A：全圆环 + 单条 -X 锯缝 pinch collar |
| S3 | `rec_quick_release_clamp_var_hinged_collar` | `data/records/rec_quick_release_clamp_var_hinged_collar/revisions/rev_000001/model.py:L243-L403` | Slot A：双半弧合页 collar（新增 `barrel_hinge` REVOLUTE + re-parent） |
| S4 | `rec_quick_release_clamp_var_fold_lever` | `data/records/rec_quick_release_clamp_var_fold_lever/revisions/rev_000001/model.py:L301-L338` | Slot B：折叠扁扳手 + clevis，`lever_hinge` REVOLUTE x |
| S5 | `rec_quick_release_clamp_var_hex_bolt` | `data/records/rec_quick_release_clamp_var_hex_bolt/revisions/rev_000001/model.py:L278-L328` | Slot B：沉孔 socket-head + 可收纳折叠 Allen-key，`hex_key_hinge` REVOLUTE -x |
| S6 | `rec_quick_release_clamp_var_wing_nut` | `data/records/rec_quick_release_clamp_var_wing_nut/revisions/rev_000001/model.py:L291-L328` | Slot C：蝶形手拧螺母（hub + 双对置指翼），沿用 `adjuster_nut_spin` |
| S7 | `rec_quick_release_clamp_var_dome_nut` | `data/records/rec_quick_release_clamp_var_dome_nut/revisions/rev_000001/model.py:L314-L322` | Slot C：封顶 acorn 盖形螺母，沿用 `adjuster_nut_spin` |

## 槽位 + 候选模块表

三个 named slot 全部挂在同一刚性 `collar`（或 hinged 变体的 `cam_arc`）上。每个 candidate 结构互不相同，且都有 fork 源码来源。

### Slot A：collar（夹环主体——抱住 seatpost bore 的开口环）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `omega_split_ring`（基线） | `rec_...1b80e476` | L176-L245（build；helper `_collar_band_solid` L88-L99 / `_throat_notch_solid` L71-L85 / `_lug_solid` L108-L117） | eligible if compatible | 单刚体 Omega 开口环，-X 楔形 throat 把 bore 豁开到两脚间；`collar` part，含 `collar_band` / `lug_cap_side` / `lug_nut_side`；无环上铰接 |
| `pinch_collar` | `rec_quick_release_clamp_var_pinch_collar` | L173-L242（build；helper `_pinch_slit_solid` L73-L80 / `_collar_band_solid` L83-L96） | eligible if compatible | 整圆环，仅 -X 壁开一条细窄锯缝（`PINCH_SLIT_HALF_W`），bore 保持连续圆通孔（非 Omega）；仍是单刚体 `collar` part |
| `hinged_collar` | `rec_quick_release_clamp_var_hinged_collar` | L243-L343（build；arc helper `_arc_profile_points` L98-L124 / `_collar_arc_solid` L131-L135 / `_hinge_leaf_solid` L157-L174 / `_hinge_pin_solid` L181-L184） | eligible if compatible（引入额外 REVOLUTE + re-parent） | 拆成 `cam_arc` / `nut_arc` 两 part 的表带式合页：+X 可见 barrel hinge 把 nut 半弧铰到 cam 半弧，-X lugs 仍由 lever bolt 夹合；新增 `barrel_hinge` REVOLUTE z(0→62°) |

### Slot B：actuation（+Y cap-side 的快拆动作机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cam_over_center_lever`（基线） | `rec_...1b80e476` | L248-L285（part L248-L254 + helper `_lever_handle_solid` L130-L162 + joint `lever_cam_pivot` L275-L285） | eligible if compatible | 实体侧扳手 `cam_lever`（`lever_handle`），外置短固定 `fixed_cam_barrel` boss；绕竖直 Z 轴 pivot 摆开，`lever_cam_pivot` REVOLUTE z(0→170°) |
| `fold_flat_lever` | `rec_quick_release_clamp_var_fold_lever` | L301-L338（part L301-L307 + helper `_folding_lever_solid` L142-L179 / `_fork_cheek_solid` L182-L192 + joint `lever_hinge` L328-L338） | eligible if compatible | 扁平折叠扳手 `folding_lever`（`flat_lever`，带 bored eye）绕 X 轴 hinge pin 上翻；固定件 `bolt_head` + `fork_cheek_{0,1}` clevis 双颊夹销；`lever_hinge` REVOLUTE x(0→95°) |
| `recessed_hex_bolt` | `rec_quick_release_clamp_var_hex_bolt` | L278-L328（part L278-L296 + helper `_socket_head_solid` L136-L151 / `_hex_drive_bit_solid` L164-L170 / `_folding_hex_key_arm_solid` L182-L189 + joint `hex_key_hinge` L317-L328） | eligible if compatible | 沉孔 socket-head 螺栓 `socket_head_bolt` + 可收纳折叠 Allen-key `hex_key`（`hex_drive_bit` / `hinge_knuckle` / `folding_hex_arm`）；六角臂绕 socket 口翻出，`hex_key_hinge` REVOLUTE -x(0→92°) |

### Slot C：nut（-Y nut-side 的调节螺母）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `knurled_barrel_nut`（基线） | `rec_...1b80e476` | L256-L295（part L256-L272 + joint `adjuster_nut_spin` L286-L295） | eligible if compatible | 滚花圆筒桶状调节螺母 `adjuster_nut`（`knurled_nut`，`KnobGeometry` grip=knurled count=40）；绕 bolt 轴连续旋转 |
| `winged_thumb_nut` | `rec_quick_release_clamp_var_wing_nut` | L291-L328（part L291-L305 + helper `_thumb_nut_hub_solid` L165-L180 / `_thumb_wing_solid` L183-L197 + joint L319-L328） | eligible if compatible | 中心镗孔 `thumb_nut_hub` + 两片对置扁平径向指翼 `wing_{0,1}`（蝶形手拧螺母）；沿用 `adjuster_nut_spin` |
| `domed_acorn_nut` | `rec_quick_release_clamp_var_dome_nut` | L314-L322（part；helper `_acorn_cap_nut_solid` L131-L180 + joint `adjuster_nut_spin` L325-) | eligible if compatible | 封顶 acorn 盖形螺母 `acorn_cap_nut`（六角基 + 圆肩 + 旋转半球 dome + 盲 thread bore）；外端封闭、内端盲螺纹孔；沿用 `adjuster_nut_spin` |

硬约束自检：每个 slot 3 个 candidate（≥3 满足）；每个 candidate 结构差异为真（开口环 vs 圆环锯缝 vs 双半弧合页；摆动 cam 杠杆 vs 折叠铰扳手 vs 折叠六角钥匙；滚花桶 vs 蝶翼 vs 圆顶盖），不是单纯尺寸/颜色/材质换装。

## 槽位图（slot graph）

pattern: `parallel_children`

```text
                       [Slot A collar]  (root rigid body; -X throat/slit, shared cross_bolt along Y)
                          |        \
   lever_cam_pivot /      |         \   adjuster_nut_spin CONTINUOUS y
   lever_hinge /          |          \  (-Y nut-side, coaxial with cross_bolt)
   hex_key_hinge REVOLUTE |           \
   (+Y cap-side)          v            v
                  [Slot B actuation]   [Slot C nut]
```

- parent 关系：Slot B 与 Slot C 都是 Slot A `collar` 的并列 child（`parallel_children`）。三者共享脊梁 `cross_bolt`（Cylinder 沿 Y，`BOLT_Y_MIN..BOLT_Y_MAX`）：actuation 在 +Y 端、nut 在 -Y 端、collar lugs 在中段。
- **collar ↔ actuation 接口**：动作机构挂在 cap-side(+Y) lug 外端面 + 固定承托件（cam barrel / bolt_head+fork_cheek clevis / socket_head_bolt mouth）。基线 joint origin 在 `(PIVOT_X, LEVER_YC, PIVOT_Z=0.5·BAND_H)`。跨 slot joint type 恒为 REVOLUTE，轴随候选变化：基线 z / fold x / hex -x。
- **collar ↔ nut 接口**：`adjuster_nut` 挂在 nut-side(-Y) lug 外、贴 `nut_side_thrust_washer`，joint origin `(PIVOT_X, NUT_YC, PIVOT_Z)`，CONTINUOUS 绕 +Y，与 `cross_bolt` 同轴（thread-engagement proxy，需 element-scoped `allow_overlap`）。
- **hinged_collar 的 re-parent 例外**（互斥/派生）：Slot A=`hinged_collar` 时根 part 变 `cam_arc`，`lever_cam_pivot` parent=`cam_arc`、`adjuster_nut_spin` parent=`nut_arc`，且 nut/lever origin 减去 `HINGE_X` 偏置（child 半弧 local frame 在 +X hinge 轴）。模板做 A×B、A×C 跨格组合时必须统一处理此 parent 重定向与 `-HINGE_X` 偏置。

## 每槽位 Module Emits / Interfaces

### Slot A / module collar（omega_split_ring / pinch_collar / hinged_collar）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单刚体：`collar`（`collar_band` + `lug_cap_side` + `lug_nut_side` + 机加工 lip/groove visuals + `cross_bolt` + 两 thrust washer + cap-side 固定承托件）；hinged 变体改为两 part `cam_arc` / `nut_arc` | S1 `model.py:L176-L245`；S3 `model.py:L243-L343` |
| internal joints | omega/pinch：无环上 joint；hinged：`barrel_hinge` REVOLUTE z(0→62°)，parent=`cam_arc` child=`nut_arc` | S3 `model.py:L373-L382` |
| upstream interface | 世界根（座管 bore 轴 = +Z）；`cross_bolt` 沿 Y 为三 slot 共同参照轴 | S1 `model.py:L213-L220` |
| downstream interface | cap-side(+Y) lug 外端面 + 固定承托件 → actuation；nut-side(-Y) lug 外 + `nut_side_thrust_washer` → nut；hinged 时 child frame 平移 `-HINGE_X` | S1 `model.py:L221-L245`；S3 `model.py:L324-L334` |

### Slot B / module actuation（cam_over_center_lever / fold_flat_lever / recessed_hex_bolt）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 基线 `cam_lever`(`lever_handle`)；fold `folding_lever`(`flat_lever`) + 固定 `bolt_head`/`fork_cheek_{0,1}`/`hinge_pin`；hex `hex_key`(`hex_drive_bit`/`hinge_knuckle`/`folding_hex_arm`) + 固定 `socket_head_bolt`/`hex_socket_recess` | S1 `model.py:L248-L254`；S4 `model.py:L301-L307`；S5 `model.py:L278-L296` |
| internal joints | **真实主 REVOLUTE**：`lever_cam_pivot` z(0→170°) / `lever_hinge` x(0→95°) / `hex_key_hinge` -x(0→92°)，单实例 | S1 `model.py:L275-L285`；S4 `model.py:L328-L338`；S5 `model.py:L317-L328` |
| upstream interface | child 挂 collar cap-side lug 外端面，joint origin `(PIVOT_X, LEVER_YC / HINGE_Y / SOCKET_FACE_Y, PIVOT_Z)`；fixed 承托件须与 collar 几何对齐 | S1 `model.py:L237-L245`；S4 `model.py:L267-L298`；S5 `model.py:L264-L275` |
| downstream interface | 无（叶子 child） | — |

### Slot C / module nut（knurled_barrel_nut / winged_thumb_nut / domed_acorn_nut）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `adjuster_nut`：基线 `knurled_nut`(`KnobGeometry`)；wing `thumb_nut_hub` + `wing_{0,1}`；dome `acorn_cap_nut` | S1 `model.py:L256-L272`；S6 `model.py:L291-L305`；S7 `model.py:L314-L322` |
| internal joints | 无 nut-local joint；只接 `adjuster_nut_spin` CONTINUOUS y（单实例） | S1 `model.py:L286-L295` |
| upstream interface | child 挂 collar nut-side lug 外，贴 `nut_side_thrust_washer`，origin `(PIVOT_X, NUT_YC, PIVOT_Z)`，与 `cross_bolt` 同轴（captured-pin overlap 需局部 allow_overlap） | S1 `model.py:L286-L295` + L309-L316 run_tests allow_overlap |
| downstream interface | 无（叶子 child） | — |

要求：动作机构与螺母都是 articulated child（各 1 条真实 joint）。collar 上的 lip / groove / washer / barrel / bolt_head 等不动细节写成 parent visual，不作为独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `collar_style` | enum | `omega_split_ring` / `pinch_collar` / `hinged_collar` | `omega_split_ring` | choice | 由 deterministic procedural sampler 选择 | Slot A table |
| `actuation_style` | enum | `cam_over_center_lever` / `fold_flat_lever` / `recessed_hex_bolt` | `cam_over_center_lever` | choice | 由 sampler 选择；决定 +Y 端 REVOLUTE 轴与固定承托件 | Slot B table |
| `nut_style` | enum | `knurled_barrel_nut` / `winged_thumb_nut` / `domed_acorn_nut` | `knurled_barrel_nut` | choice | 由 sampler 选择；沿用 `adjuster_nut_spin` 轴/origin | Slot C table |
| `bore_radius_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 `BORE_R`/`BAND_OUTER_R`；clamp，保持壁厚 `BAND_OUTER_R−BORE_R>0` | S1 `model.py:L30-L33` |
| `band_height_scale` | float | [0.85, 1.25] | 1.0 | independent | 缩放 `BAND_H`；`PIVOT_Z=0.5·BAND_H` 随之派生 | S1 `model.py:L32`,L47 |
| `lever_reach_scale` | float | [0.85, 1.25] | 1.0 | independent | 缩放手柄/折叠臂长度（仅 Slot B 几何） | S1 `model.py:L130-L162` |
| `nut_len_scale` | float | derived | 1.0 | equation | `NUT_YC = f(NUT_LEN)`；改 `NUT_LEN` 须同步 `NUT_YC` 使螺母仍贴 thrust washer | S1 `model.py:L64-L66` |
| (—) | constraint | — | — | inequality | `BOLT_Y_MAX` 端头随 Slot B 候选变（cam barrel/bolt_head/socket head）；`cross_bolt` 必须同时盖住 +Y 承托件与 -Y 螺母 seating，违反则回缩 bolt 跨度或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | conditional | Slot A=`hinged_collar` 时 actuation/nut origin 解析为 `−HINGE_X` 偏置且 re-parent 到 `cam_arc`/`nut_arc` | S3 `model.py:L250`,L388-L403 |

参数只表达语义选择与尺寸/行程；未实现的拓扑不进 enum。所有 equation / inequality / conditional 在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（collar / actuation / nut）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。三个 slot 各占一个固定命名位。
- 没有 `count_param`、没有 `for i in range(N)` 链式发射、没有被复制的整块对象。
- 唯一两条真实非固定主 joint：动作机构那条 REVOLUTE（基线 `lever_cam_pivot` z / fold `lever_hinge` x / hex `hex_key_hinge` -x）+ `adjuster_nut_spin` CONTINUOUS y。两者均单实例，不复制。
- （局部例外，非模板轴）`winged_thumb_nut` 的两片 `wing_{i}` 用 `for i in range(2)` 发射（`rec_quick_release_clamp_var_wing_nut/.../model.py:L299-L305`），但这是一个 slot 候选**内部固定双翼几何**，N≡2，不是模板级 multiplicity 轴。
- （结构性副作用，非复制）`hinged_collar` 候选额外引入一条 `barrel_hinge` REVOLUTE z —— 是 Slot A 把单刚体环拆成双半弧的结果，仍非 ×N 复制逻辑。

## 拓扑多样性审计

总组合数：`3 collar × 3 actuation × 3 nut = 27`（无 multiplicity 轴，不乘 N）。


seed_domain_policy：procedural_first（`seed=0` 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对每个 slot 各做一次加权 module 选择 → 解析 conditional（hinged re-parent / `-HINGE_X`）→ 采 independent 连续 scale → 派生 `NUT_YC`/`PIVOT_Z` → 用 inequality 投影 `BOLT_Y_MAX` 跨度。compatibility matrix 优先排除：hinged_collar × 任一 actuation/nut 时漏掉 re-parent（→ 漂浮）、Slot B 承托件与 collar cap-side lug 几何错位、captured-pin overlap 未加 allow_overlap、closed pose 杠杆穿模。少量 regression overrides 仅用于已知失败回归。Topology target：1000-seed 建议 distinct ≥ 27 上限附近（本类候选有限，不强求 ≥300，已说明类别约束）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：`bore_radius_scale`、`band_height_scale`、`lever_reach_scale` 为关键连续 scale；`NUT_YC`（equation 派生）、`BOLT_Y_MAX` 跨度（inequality）保证螺母 seating 与 bolt 包覆不破坏 InterfaceSpec / MatingContract。所有 scale 在 `resolve_config` 中 clamp / 派生。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 三 slot 各自加权 choice + hinged re-parent gate | slot_choices_for_seed matches build choices |
| compatibility matrix | hinged_collar 强制 re-parent 与 `-HINGE_X`；Slot B 承托件须对齐 cap-side lug | no floating, axis, captured-pin, closed-pose collision |
| controlled local variation | bore/band/lever scale，clamp 保持壁厚>0、螺母贴 washer | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none（必要时记 seed + 原因） | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 初验，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A collar | 3 | yes | yes | |
| B actuation | 3 | yes | yes | |
| C nut | 3 | yes | yes | |

## Validator
- slot_choices_for_seed 返回 implemented module names（3×3×3）
- config_from_seed 对所有普通 seed 使用 deterministic procedural sampling
- compatibility matrix / gating 强制 `hinged_collar` re-parent 到 `cam_arc`/`nut_arc` 并施加 `-HINGE_X` 偏置，避免 actuation/nut 漂浮
- 关键 joint：动作机构恰 1 条 REVOLUTE（轴 z/x/-x 随候选），`adjuster_nut_spin` 恰 1 条 CONTINUOUS y 且与 `cross_bolt` 同轴；hinged 变体另含 `barrel_hinge` REVOLUTE z
- collar 必须保留 -X throat（omega）或 pinch slit，bore 不得完全闭合
- cross-part scale 依赖（`NUT_YC` equation、`BOLT_Y_MAX` inequality、hinged conditional）在 `resolve_config` 求解，不留到 builder
- captured-pin overlap（`cross_bolt`↔nut bore；fold `hinge_pin`↔`flat_lever`；hex `socket_head_bolt`↔`hex_drive_bit`）使用 element-scoped allow_overlap
- 局部 scale 受 clamp，不破坏 interface / clearance / joint origin / 类别 identity

## Reject cases
- collar 完全闭合（无 throat / 无 slit），无法套上或脱出 seatpost。
- 动作机构无 REVOLUTE（被改成纯螺纹手拧），失去 quick-release 语义，读成 hose clamp。
- 动作机构或螺母悬空 / 用不可见接口盘连接，不接触真实 collar lug 承托面。
- `adjuster_nut_spin` 轴偏离 `cross_bolt`（不再同轴），或螺母不贴 thrust washer。
- Slot A=`hinged_collar` 却未 re-parent / 未加 `-HINGE_X`，导致 actuation/nut 漂浮或穿模。
- 把 `wing_{i}` 双翼或 hinge knuckle 误当模板级 ×N multiplicity 暴露为 count_param。
- closed pose 下杠杆/折叠臂穿过 collar band 或 cam barrel。

## 与相邻类别的边界
- 不该混入 `hose_clamp` / 管箍（worm-drive / 螺纹收紧带）：那类没有 cam-over-center 或折叠杠杆的 quick-release REVOLUTE，靠连续螺纹收紧；本类必须保留侧扳手/折叠铰那条 REVOLUTE。
- 不该混入 `pipe_union` / 管接头活接：那类靠旋合螺母对接两段管路、无开口 throat collar、无快拆杠杆；本类的 `adjuster_nut` 只是预紧调节件，主功能是夹紧 seatpost bore 而非密封连通两管。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；7 源（parent + 6 fork variants），3 slot × 3 candidate = 27 ≥ 10 门槛；等待人工审核，审核通过前不进入模板实现 |
