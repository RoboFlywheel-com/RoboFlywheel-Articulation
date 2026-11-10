# Needle case — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `needle_case` |
| template path | `agent/templates/needle_case.py` |
| test path (optional) | `tests/agent/test_needle_case_template.py` (not written; sweep is authoritative) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (chained panels + parallel closure/flap children + multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (2 origins + 7 forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

A dedicated case/organizer that stores and protects knitting/sewing needles
(straight, double-pointed, or circular) in indexed positions, with a real
closure that keeps them contained. The default mature domain is a leather bifold
organizer that lies open on the table: one or more leather panels carry a needle
bed (channels / stitched band / retaining loops), a hinged retaining flap over
the tips, and a closure (snap cover flap / wrap tie / zip). A volumetric rigid
tube variant holds a double-pointed-needle bundle upright with a pull-off cap.

不该混入：generic tool/brush roll (no needle-specific beds), pen/pencil or
eyeglass case (no needle interior), jewelry roll or soft cosmetic pouch.

## 槽位 + 候选模块表

### Slot A：body_skeleton (① 骨架 / ③ 主体形态家族)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bifold` | forked_anchor(origin) | A + B | A L230-344 / B L196-300 | eligible if compatible | 2 leather panels chained by 1 spine REVOLUTE; planar boundary form (Planar Boundary Form) |
| `trifold` | forked_anchor | rec_needle_case_var_skeleton_trifold_roll | L325-467 | eligible if compatible | 3 panels chained by 2 spine REVOLUTEs (roll-up); same panel part tree ×3 |
| `single_flat` | forked_anchor | rec_needle_case_var_skeleton_single_flat | L175-258 | eligible if compatible | 1 panel, no spine fold; closure re-parents to the root panel |
| `tube` | forked_anchor | rec_needle_case_var_form_tube | L68-214 | eligible if compatible | Volumetric Envelope Form: LatheGeometry hollow cylinder + upright DPN bundle + prismatic pull cap |

`form_subtype`: `bifold`/`trifold`/`single_flat` = **Planar Boundary Form** (flat
leather panel outline); `tube` = **Volumetric Envelope Form** (3D revolved shell).

### Slot B：retention (② 关节 / internal ①) — planar skeletons only

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `channel_tunnels` | forked_anchor(origin) | A channel_strip + prismatic needles; trifold `_add_needle_bed` | A L88-104,L256-276 / trifold L269-319 | eligible if compatible | rail-walls forming open channels + one **PRISMATIC** slide needle part per channel (② signature) |
| `stitched_band` | forked_anchor(origin) | B `_add_needle_bed` | B L116-167 | eligible if compatible | needle tips (visuals) threaded under a stitched pocket band + dividers + stitch lines |
| `leather_loops` | forked_anchor | rec_needle_case_var_internal_loops | L116-181 | eligible if compatible | one swept-spline bent-leather retaining arch (Mesh) per needle |
| `upright_bundle` | forked_anchor | rec_needle_case_var_form_tube | L84-105,L168-178 | tube-only (gated) | DPN visuals in a hex ring inside the bore |

### Slot C：closure (② 关节)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `snap_cover_flap` | forked_anchor(origin) | A cover_flap; B closure_flap + snap_stud; single_flat | A L200-310 / B L254-279 / single_flat L206-240 | planar | REVOLUTE cover flap + brass snap studs, hinged on host panel outer edge |
| `wrap_tie` | forked_anchor | rec_needle_case_var_skeleton_trifold_roll wrap_tie | L155-163,L363-379 | planar | long narrow REVOLUTE leather tie strap on the host outer edge |
| `zipper` | forked_anchor | rec_needle_case_var_closure_zipper | L201-374 | planar | zip tape + brass teeth (host visuals) + **PRISMATIC** brass slider along the rail |
| `pull_cap` | forked_anchor | rec_needle_case_var_form_tube | L108-212 | tube-only (gated) | **PRISMATIC** pull-off cap with plug seated in the tube bore |

### Retaining tip flap (folded into Slot B — single-candidate, not a slot)
| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `tip_flap` | forked_anchor(origin) | B `_build_needle_flap` + hinge; A tip_flap | B L170-193,L284-300 / A L279-290 | REVOLUTE leather flap on the root panel's stitched seam ridge, over the tips |

单候选的 retaining flap 不单独立槽，按 AUTHORING §B 折入 retention（每个 planar 骨架在
root panel 上生成一片 tip flap，保留 B/A 的 needle-flap ② 特征而不重复到折叠面上）。

硬约束满足：Slot A 4 candidates、Slot B 3 planar candidates (+1 tube-gated)、Slot C 3
planar candidates (+1 tube-gated)，均 ≥2 且结构差异真实（part tree / joint type / primary
form 不同，非换色换尺寸）。accessory pocket（A flat/cable pocket）为单来源可选内胆，按
"不足以立槽" 折出，仅 record_only，未实现。

## 槽位图（slot graph）

pattern: mixed

```
panel_0 (root) --[fold_hinge_i REVOLUTE axis -y @ panel outer +x edge]--> panel_1 --> panel_2   (planar chain, 1..3 panels)
   each planar panel:  panel.retention_bed(visuals; channel_tunnels also emits PRISMATIC needle parts)
   panel_0:            --[tip_flap_hinge REVOLUTE axis -x @ flap_seam_ridge]--> panel_0_tip_flap
   last panel (host):  --[closure_hinge REVOLUTE | closure_slide PRISMATIC @ host outer +x edge]--> closure child

tube:  tube_body (LatheGeometry shell, DPN bundle visuals) --[closure_slide PRISMATIC axis +z @ mouth]--> cap
```

- 跨 slot 连接点：panel→panel 在 root 的 `panel_shell` 的 +x 边（`fold_hinge_i`，
  MatingContract panel_shell:+x ↔ panel_shell:-x）；closure 挂 host panel 的 +x 自由边
  （snap/wrap 用 MatingContract panel_shell:+x ↔ cover_leather:-x）；tip flap 挂 root 的
  `flap_seam_ridge`（stitched seam，grandfathered joint + allow_overlap）。
- 跨 slot joint：fold=REVOLUTE(axis -y, [0, 1.55])；closure=REVOLUTE([0,1.55]) 或
  PRISMATIC(zip rail / cap)；tip flap=REVOLUTE([0,2.4])。
- 互斥/派生：`tube` 骨架自足 → retention 强制 `upright_bundle`、closure 强制 `pull_cap`，
  不生成 planar 面板 / 折叠铰 / tip flap。planar 骨架 → retention/closure 从各自 3 候选采样。

## 每槽位 Module Emits / Interfaces

### Slot A / module `bifold`,`trifold`,`single_flat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_0` … `panel_{n-1}` (rounded ExtrudeGeometry leather shells) | B L208,213-237 |
| internal joints | `fold_hinge_1..{n-1}` REVOLUTE axis (0,-1,0) [0,1.55] | B L239-249 |
| upstream interface | root panel_shell（无 upstream，root） | — |
| downstream interface | last panel `panel_shell` +x free edge → closure host | B L269-279 |

### Slot A / module `tube`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tube_body` (LatheGeometry shell + brass rings + DPN visuals), `cap` | tube L68-121,141-196 |
| internal joints | `closure_slide` PRISMATIC axis (0,0,1) [0,0.08] | tube L199-212 |

### Slot B / module `channel_tunnels`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_i_needle_{c}` PRISMATIC slide needles (Cylinder) | A L256-276 |
| host visuals | `channel_rail_{k}` walls (Box) forming open channels | A L88-104 |
| internal joints | `panel_i_needle_{c}_slide` PRISMATIC axis (0,-1,0) [0,0.09] | A L265-276 |

### Slot B / module `stitched_band` / `leather_loops`
| emits | 描述 | 来源 |
|---|---|---|
| host visuals | needle tips + (band+dividers+stitch) or (per-needle swept-spline loop) + `flap_seam_ridge` | B L116-167 / loops L116-181 |

### Slot C / module `snap_cover_flap` / `wrap_tie` / `zipper` / `pull_cap`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `closure_flap` / `wrap_tie` / `zip_pull` / `cap` | B/single/trifold/zipper/tube (see table) |
| internal joints | `closure_hinge` REVOLUTE 或 `closure_slide` PRISMATIC | 见候选表 |
| upstream interface | host panel_shell +x edge（snap/wrap: MatingContract；zip/cap: grandfathered rail/bore） | zipper L201-267 / tube L199-212 |

不动细节（band/dividers/stitch lines/loops/snap discs/brass rings/zip teeth）一律
`part.visual(...)`，非独立 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| skeleton | enum | bifold / trifold / single_flat / tube | — | choice | procedural sampler | Slot A |
| retention | enum | channel_tunnels / stitched_band / leather_loops / upright_bundle | — | conditional | tube ⇒ upright_bundle; else 3-way | Slot B |
| closure | enum | snap_cover_flap / wrap_tie / zipper / pull_cap | — | conditional | tube ⇒ pull_cap; else 3-way | Slot C |
| needles_per_panel | int | [3,9]（测试小、产品全程） | 6 | independent | 加权采样小 N；clamp [3,9] | §8 |
| channel_count | int | derived | — | conditional | `= max(2, min(N, 9 // n_panels))`（限总滑动关节 ≤ ~9） | 关节预算 |
| size_scale | float | [0.95, 1.16] | 1.0 | independent | 仅缩放 panel shell + 折叠布局；bed 绝对（min scale 保证 bed 内嵌） | B 尺寸 |
| palette_style | enum | tan / saddle / cognac | tan | choice | 仅涂装 | ⑥ |

所有 `conditional` / `derived` 在 `resolve_config` 求解；bed y-extent 绝对且 ≤ ph(min)。

### 7.5 编译预算 / compile budget
自报预算 **≤ 12s / seed**（实测整批 48 seeds 16-17s wall，单 seed 远 < 12s）。分档
tessellation：LatheGeometry tube segments=32、needle radial_segments=14-16、loops
samples_per_segment=12、rounded_rect corner_segments=8；N 根同构 needle/loop 复用同一
`Mesh`（`_needle_tip_mesh` 单次生成）。无重布尔（channel 用 rail-walls 而非 cadquery cut）。

## Multiplicity / Copy Logic

一根独立复制轴：**needles_per_panel N**。
- `count_param` = `needles_per_panel`；`N_range` 产品域 [3,9]（测试偏小：加权
  `{4,5,5,6,6,6,7,8}` planar / `{5,6,6,7,8}` tube）；sampling domain 小 N 高频。
- copied object：`needle_i`（band/loops = host visual；channel = `panel_i_needle_c`
  PRISMATIC part；tube = DPN visual in hex ring）。indexed 命名 `needle_{i}` /
  `{panel}_needle_{c}`；placement = even-x row（planar）/ even-angle ring（tube）；
  joint policy = channel 每针一 PRISMATIC 滑动，其余 static。
- 派生 `channel_count = max(2, min(N, 9//n_panels))`，把滑动关节总数钳在 ~9 以内
  （对齐 channels_n6 fork 的 17 non-fixed 关节可造性）。
- dividers/loops 数随 N（band dividers = N+1）；record_only，随宿主派生。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | bifold(1 spine) / trifold(2 spine) / single_flat(0) / tube(cap)；retention 拓扑 channel(prismatic 针 part) vs band/loops(visual)。均 forked/origin source-backed |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：needles_per_panel [3,9]，加权小 N |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE fold/tip-flap/snap-cover/wrap-tie（axis -y/-x）+ PRISMATIC channel-needle slide / zip pull / tube cap（axis -y/+y/+z）。每种在 sweep slot_value_counts 均出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | Planar Boundary Form（bifold/trifold/single_flat 平面皮革面板）vs Volumetric Envelope Form（tube LatheGeometry 旋转壳）；登记进 `body_skeleton` slot。source-backed |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | 缝线 band_stitch、divider 脊、brass snap discs / rings / zip teeth、maker stud；均由宿主面逐-z 派生（band 贴 top_z、stud 嵌 cover top）。不单独立槽 |
| ⑤ 尺寸/行程 | 只改连续尺寸/行程 | 有 | size_scale [0.95,1.16]（§7）。运动包络：fold REVOLUTE axis -y [0,1.55]；tip flap axis -x [0,2.4]；snap/wrap REVOLUTE [0,1.55]；zip PRISMATIC +y [0, tape_len-body]；channel needle PRISMATIC -y [0,0.09]；cap PRISMATIC +z [0,0.08]。`motion_test_plan`：sampled collision (max_pose_samples=28) + 每机构一 targeted `ctx.pose`（fold 抬升 / flap 掀开 / 针滑出 / cover 掀起 / zip 滑动 / cap 拔出）。fold+cover 上界 1.55 止于叠合前（离散采样无法表达协调折合的全闭合，非缩窄真实行程） |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 leather(painted) / brass(metal) / steel / bamboo(wood) ≥3；配色 tan/saddle/cognac + 6 色可换针尖 ≥3-6 |

## 采样与覆盖审计

总组合数（planar）：skeleton(3) × retention(3) × closure(3) × N档 ≈ 3×3×3×~7 = ~189，
加 tube(1)×N档(~5) = ~194；含 size_scale 连续维实际远大。sweep 48 seeds 实现全部
4 skeleton / 4 retention / 4 closure / 5 N 档（见 axis_realization）。

理由：形态主导 + 机构多样类，主多样性来自离散 skeleton/retention/closure/N，size_scale
只做受控局部缩放。

seed_domain_policy：procedural_first（`config_from_seed` 对所有 seed 含 seed 0 走
`random.Random(seed)` 采样；seed 0 = tube，非特殊）。
Procedural Sampling / Sweep Plan：sampler 先采 skeleton，按 skeleton 解析 retention/closure
合法集（tube 强制 upright_bundle/pull_cap），再采 N + palette + size_scale，全部 clamp。
无 regression overrides。random sweep 0-35 初判 + corner；viewer 目检 0-2。
Topology target：report-only；真实组合 ~194（tube 分支自足使 planar 组合独立可造，
无需 cross-combine 探针）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | skeleton→(conditional retention/closure)→N→palette→size_scale，加权小 N | slot_choices_for_seed matches build |
| compatibility matrix | tube ⇒ upright_bundle+pull_cap（gated）；planar 全交叉合法 | no floating / collision / axis / max-multiplicity failures |
| controlled local variation | size_scale [0.95,1.16]（缩 panel shell + 折叠布局；bed 绝对内嵌）；channel_count 派生 | proportions vary without breaking hinges/mating/identity |
| regression overrides | none | — |
| random sweep | 0-35 initial pass + corner；0-999 maturity | contract failures; axis_realization; viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_skeleton | 4 | yes | yes | |
| retention | 3 (+1 tube-gated) | yes | yes | planar 3；upright_bundle tube 专用 |
| closure | 3 (+1 tube-gated) | yes | yes | planar 3；pull_cap tube 专用 |

## Validator

- slot_choices_for_seed returns implemented module names（4-tuple）
- config_from_seed uses deterministic procedural sampling for all seeds（seed 0 非特殊）
- compatibility gating prevents tube×planar-retention/closure 非法组合
- no regression overrides
- size_scale clamp 于 resolve_config；channel_count derived 于 resolve_config
- 关键 MatingContract：fold_hinge panel_shell:+x↔-x、snap/wrap closure panel_shell:+x↔cover_leather:-x
- 关键 joint type/axis/range：fold REVOLUTE -y、channel/zip/cap PRISMATIC、tip flap REVOLUTE -x
- copied needles follow indexed naming + even placement

## Reject cases

- 折叠/盖合全行程叠模（fold/cover 上界过大导致非相邻面互穿）
- channel 针滑动关节数爆掉可造预算（未派生 channel_count）
- bed 随 size_scale 缩到 panel 外（bed 未保持绝对 / scale 下界过小）
- tip flap 铺满每折叠面 → 折叠时 flap-flap 互穿
- 装饰件（stud/tie_stud）悬空成 island（未嵌入宿主面顶）
- 把 accessory pocket 当独立单候选槽（应折出为 record_only）
- 退化 hero mesh（tube LatheGeometry / loop 扫掠 → Box），违反 Rule 3

## 与相邻类别的边界

- 不该混入：generic tool/brush roll（无 needle-specific bed）
- 不该混入：pen/pencil 或 eyeglass case（无 needle 内胆）
- 不该混入：jewelry roll / 软化妆包（无索引 needle 保持结构 + 真实闭合）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | sweep-pipeline verdict=pass (fast/final/corner all pass), 48 seeds, all 4 skeleton / 4 retention / 4 closure / 5 N 档 realized; motion audit pass. 人工目检 batch 0-2 待主循环统一 pass。 |

## 模板实现备注（可选）

- 共享 helper：`_needle_tip_mesh` / `_dpn_mesh` / `_loop_mesh` / `_panel_mesh` 单次生成，N 复用。
- panel chain：root 面板 z∈[0,PANEL_T]；折叠面 local 原点在铰线（world z=HINGE_Z），top=-0.0005，
  与 B/forks 一致，保证开合时共面。
- grandfathered joints（omit mating=）：tip flap（stitched seam ridge）、channel needle
  slide（开放通道）、zip pull（rail）、cap（bore）——各配 element-scoped allow_overlap。
- fold/cover 上界 1.55、tip flap 仅在 root：离散 sampled-pose 笛卡尔积下避免折合叠模 + flap-flap 互穿。
```
