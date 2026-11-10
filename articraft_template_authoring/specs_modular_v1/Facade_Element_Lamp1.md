# wall_lantern — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `wall_lantern` |
| 大类/小类 (picture) | `Facade Element/Lamp1` (placeholder picture name; real object = facade wall lantern) |
| source map | `<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Facade_Element__Lamp1.md` |
| template path | `agent/templates/Facade_Element_Lamp1.py` |
| test path (optional) | `tests/agent/test_wall_lantern_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (serial chain bracket→suspension→body + a `lantern_count` multiplicity axis over the head, N_range [1,5]) |

### Provenance (parents + pictures)
| parent record_id | picture | 覆盖 |
|---|---|---|
| `rec_build-a-realistic-articulated-3d-model-of-a-lamp_20260609_185910_557031_f8540f5f` | `picture/Facade Element/Lamp1/001.png` | leaf wall plate + scroll gooseneck arm + hook + single chain link + flared-roof / caged-glass swinging lantern (axis X, outward +Y) |
| `rec_build-a-realistic-articulated-3d-model-of-a-lamp_20260609_185914_197581_ece7fee7` | `picture/Facade Element/Lamp1/002.png` | octagonal cast-iron backplate + bracket tabs + forged hook arm + chain loop + cylindrical amber-glass lantern (domed cap, wrought cage, socket + bulb; axis Y, outward +X) |

### Module source records (adopted variants)
| record_id | adopted as |
|---|---|
| `rec_lamp1_var_gooseneck_arm` | Slot A `gooseneck_arm` |
| `rec_lamp1_var_chain_drop` | Slot A `chain_drop` |
| `rec_lamp1_var_caged_cylinder_lantern` | Slot B `caged_cylinder_body` |
| `rec_lamp1_var_conical_roof` | Slot B `conical_roof_body` (rebased from parent-2 frame) |
| `rec_lamp1_var_double_lantern` | Slot C multiplicity reference (only sampled multi-head proof, `lantern_count = 2`; template N_range = [1,5], N≥3 by-construction) |

> **Canonical frame for this template = Parent-1 frame** (real meters, Z-up): wall plane is X-Z at y=0; bracket extends into +Y away from the wall; +Z up. Pendulum swing axis = **X** (a horizontal line in the wall plane); the lantern swings toward/away from the wall in the Y-Z plane. The pivot is the hook eye at `(0, HOOK_Y, HOOK_Z)` (or `(hx, HOOK_Y, HOOK_Z)` per head). Parent-2 and its derived `conical_roof` candidate are authored in a rotated frame (outward +X, axis Y); they are **rebased** into the canonical frame (its (x_p2, 0, z_p2) → canonical (0, y, z), axis Y→X, sign of swing fixed so positive q lifts the lantern outward in +Y). The rebase is a coordinate relabel only — geometry/part-tree is preserved.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (2 parents + 5 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

**共享结构（all 7）**: 一个 wall-mounted carriage / sconce lantern。固定 root = 墙面安装件（backplate）+ 一段从板向外/向上弯曲的支臂 + 末端的钩 (hook/eye)。一个 lantern 头由钩通过 chain link/loop 悬挂，**唯一真实活动 = 钟摆式 REVOLUTE swing**（绕一条平行于墙面的水平轴，pivot 在钩眼，lantern frame 原点即 pivot，几何向下 −Z 悬挂）。Lantern 头共有：top cap/roof（finial 收顶）、translucent glass 圆柱体、围绕 glass 的 cage（竖straps/bars + 横 ring bands）、bottom retaining ring（+ drip finial 或 base ring）。chain link 与 hook 是两个互锁的环（intentional interlink / `allow_overlap`），finial neck 穿过 link 底部被捕获（suspension capture）。

**逐源差异**:
- **parent 557031 (001)**: leaf/fleur 立面墙板 (`_wall_plate_shape`)；scroll S-curve gooseneck 臂 (`_scroll_arm_mesh`)；单 chain link (torus)；锥形 flared sheet-metal roof (`_roof_shape`) + 平直 glass 圆柱 + strap/band cage (6 straps×3 bands) + bottom ring + drip。swing axis **X**, origin `(0, 0.235, 0.060)`, lower/upper ±0.45。
- **parent 197581 (002)**: 八边形 cast-iron backplate + 中央 spine boss + 上/下 bracket tabs（带 bolt heads）+ forged 球-柱采样 hook arm 末端 torus eye；chain loop (torus)；domed black-iron cap + flared collar；薄壁 hollow glass 管；wrought cage（2 bands + 4 straps）；base ring；内部 socket stem + LED bulb。swing axis **Y**, origin `(0.085, 0, 0.064)`, lower/upper ±0.35。
- **gooseneck_arm** (parent-1 fork): 唯一结构改动是支臂 → 高拱 shepherd's-crook (`_gooseneck_arm_mesh`)，crest 远高于钩眼与墙板顶；其余与 parent 1 完全相同。
- **chain_drop** (parent-1 fork): 悬挂从单 link → N=5 interlocking torus links（交替 ring 平面），candidate-local chain-link 计数；lantern 体与 parent 1 相同。
- **caged_cylinder_lantern** (parent-1 fork): body slot 改动 — 平 cylindrical cap (`roof_cap`, disk+lip+neck) + 圆截面竖 bars cage（BAR_N=8 个独立 `bar_i`）+ ring bands（独立 `band_i`）+ 内部 lathe bulb（socket 座入 floor）；arm 仍是 scroll。
- **conical_roof** (parent-2 fork): body slot 改动 — 平 dome → 直边 conical aged-copper roof + finial（stem+ball）；其余（八边形 backplate、forged hook arm、cylindrical glass、wrought cage、socket+bulb）同 parent 2。
- **double_lantern** (parent-1 fork): multiplicity 参考（唯一被直接采样的多头证据，N=2）— N_HEADS=2，forked trunk + 每头 branch (`_fork_trunk_mesh`/`_fork_branch_mesh`)，每头 `lantern_{i}` part + `lantern_swing_{i}` REVOLUTE about X at `(±FORK_X, HOOK_Y, HOOK_Z)`，LANTERN_SCALE=0.72 缩小，FORK_X=0.130 横向偏移（→ 两头 spacing=2·FORK_X=0.260；`2·GLASS_R·0.72=0.118 ≪ 0.260`，间距裕度充足）。该源的 fork 几何**硬编码为恰好 2 头**（trunk + 2 branch），不能推广到 3–5；模板对 N≥3 改用 §5/§8 的 **horizontal multi-hook crossarm/bar**（条 width∝N，N 个均匀对称 hook eyes）。模板 N_range=[1,5] **合法地超出** 被采样 N（FORK_VARIANTS 仅须证明 copy-logic，N_range 的所有权归模板自身），N∈{3,4,5} 为 **by-construction**（无须各自的 5★ 源）。

## 核心身份

`wall_lantern` 是一个**立面墙挂式提灯/壁灯 (facade wall lantern / carriage sconce)**：一块螺栓固定在垂直墙面上的安装板（leaf/fleur 或八边形 cast-iron shield），一段从板向外伸出并弯曲的支臂（scroll、高拱 gooseneck 或带 forged eye 的钩臂），末端一个钩眼通过一节或一串 chain link/loop 悬挂一个 lantern 头。lantern 头是一个**带半透明玻璃体 + 金属 cage + 顶 cap/roof（finial 收顶）+ 底 retaining ring** 的封闭灯笼，可能内含 socket+bulb。唯一真实运动是 lantern 头绕钩眼的**钟摆式 REVOLUTE swing**（风中摇摆，轴平行于墙面）。

成熟域：墙面安装、向外悬挑的支臂、悬挂在钩上、cage 包裹的玻璃灯体、钟摆 swing。默认 1 个头；多头立面壁灯支持 `lantern_count` ∈ **[1,5]**（共享 bracket，每头独立 swing）——N=1 单臂，N=2 fork（或 bar），N≥3 用横向 multi-hook crossarm/bar（条上 N 个均匀对称 hook eyes）。其中 N∈{1,2} 被 5★ 池直接采样，N∈{3,4,5} 为 by-construction（模板拥有该 range，见 §8）。

不应混入：落地/台面灯（无墙板、无悬挑悬挂）；吊顶 chandelier/pendant（从天花顶部下垂、非墙挂、常多臂辐射）；可调臂工作灯（articulated_task_lamp，臂上有多个驱动关节而非单一钟摆）；纯装饰 sconce（无悬挂活动灯体）。

## 槽位 + 候选模块表

> Slot A 与 Slot B 在**两种 bracket/lantern 家族**间组合时统一到 canonical (parent-1) 框架：scroll-family 支臂直接采用；conical_roof body 候选从 parent-2 框架 rebase。所有 candidate 都接到同一 `hook_eye` 接口点（pivot）。

### Slot A：arm / suspension（固定 root 的支臂 + 钩 + 悬挂）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `scroll_arm` | rec_build-...185910_557031 (parent 1) | L193-L214 (`_scroll_arm_mesh`) + 钩 L217-L240 (`_hook_mesh`) + 单 link L274-L287 | eligible if compatible | 低 S-curve scroll gooseneck 管，crest≈0.15；末端 hook curl (YZ 平面)；单 chain link (torus, XZ 平面) 悬挂。part tree: bracket{plate,scroll_arm,hook}; lantern child via 单 link。 |
| `gooseneck_arm` | rec_lamp1_var_gooseneck_arm | L199-L224 (`_gooseneck_arm_mesh`) + 钩 L227-L250 + 单 link (parent-1 link 同) | eligible if compatible | 高拱 shepherd's-crook 管，crest≈0.285（远高于钩眼+0.10 与墙板顶+0.10）；加粗 ARM_R=0.014；同 hook+单 link 悬挂。结构差异=支臂 chain depth/silhouette。 |
| `chain_drop` | rec_lamp1_var_chain_drop | scroll 臂 L194-L215 + 钩 L218-L242 + **多 link** L261-L295 (`_chain_link_cz`,`_chain_link_shape(index)`) emit L453-L459 | eligible if compatible | scroll 臂 + N=5 interlocking torus links（交替 ring 平面 even=XZ/odd=YZ），candidate-local chain-link 计数 (N_CHAIN_LINKS)，悬挂明显更长。结构差异=悬挂链 part 数 + interlink 拓扑。 |

### Slot B：lantern body / cap（摆动 child 的灯体）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flared_roof_body` | rec_build-...185910_557031 (parent 1) | roof L313-L328 (`_roof_shape`) + glass L331-L338 + strap/band cage L341-L376 (`_cage_shape`) + bottom_ring+drip L379-L406 | eligible if compatible | 宽 flared 锥形 sheet-metal roof（eave 0.140 远宽于 glass 0.082）+ 平直 glass 圆柱 + 6 竖 straps×3 横 bands 的 unioned cage + bottom ring + drip finial。无内部 bulb。 |
| `caged_cylinder_body` | rec_lamp1_var_caged_cylinder_lantern | cap L320-L344 (`_roof_shape`→`roof_cap`) + glass L347-L354 + 独立 bars L357-L370 (`_cage_bar_shape`) emit L515-L521 + bands L373-L390 emit L523-L529 + bulb L393-L423 (`_bulb_shape`) + bottom_ring L426-L453 | eligible if compatible | 平 cylindrical disk cap（disk+下 lip+中央 neck collar）+ glass + **圆截面竖 bars cage**（BAR_N=8 个独立 `bar_i` + 3 独立 `band_i`）+ 内部 lathe bulb（socket 座入 floor plate）+ bottom ring。结构差异=cap 形态 + cage 由 unioned strap → 离散 round bars + 加 bulb part。 |
| `conical_roof_body` | rec_lamp1_var_conical_roof（parent-2 派生，rebase 到 canonical 框架） | cap L228-L279 (`_build_cap_shape`，profile L244-L253，finial stem+ball L265-L279) + glass L282-L296 (hollow tube) + base_ring L299-L309 + cage L312-L349 (2 bands+4 straps) + socket L352-L367 + bulb L370-L387 | eligible if compatible | 直边 conical aged-copper roof（XY span > 高度的 tapering cone）+ stem+ball finial + **薄壁 hollow** glass 管 + wrought-iron cage（2 bands+4 straps）+ base ring + 内部 socket stem + LED bulb。结构差异=roof 直锥 + hollow glass + socket/bulb 内构。rebase: parent-2 (x_p2,0,z_p2)→canonical (0,y,z)。 |

### Slot C：head multiplicity（`lantern_count` 复制轴，N_range [1,5]）

两个结构候选 archetype（不是两个采样档；它们覆盖整个 N_range [1,5]）：

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_arm` (N=1) | parents + single variants（gooseneck/chain_drop/caged/conical 皆单头） | parent 1 articulation L484-L492；single bracket 无 fork/bar | eligible if compatible | `lantern_count=1`：单 chain link/loop 悬挂的单头，bracket 为单臂（无 fork/bar），1 个 `lantern_swing` REVOLUTE，HOOK_XS=[0]。 |
| `multi_head_bar` (N≥2) | rec_lamp1_var_double_lantern（N=2 直接采样；N=3–5 by-construction，同 copy-logic） | fork/bar root L155-L197 (`_fork_trunk_mesh` L155-L165, `_fork_branch_mesh` L168-L179, `_hook_mesh(cx)` L182-L197)；per-head emit L398-L437；per-head swing L442-L452；per-head scale L207-L229 (`_lantern_z_layout`) | eligible if compatible | `lantern_count∈[2,5]`：横向 multi-hook crossarm/bar（条 width∝N），N 个均匀对称 hook eyes 在 `HOOK_XS`（以 0 为中心）；N 个 `lantern_{i}` part + N 个 `lantern_swing_{i}` REVOLUTE about X at `(HOOK_XS[i], HOOK_Y, HOOK_Z)`；每头 `head_scale=f(N)`（随 N 递减，N=2 取 ≈0.72）。N=2 可退化为既有 fork（trunk+2 branch）或 bar——模板择一并保持一致；N≥3 必用 bar（fork 仅 2 头硬编码，不推广）。 |

> **单 candidate slot 说明**: 无。Slot A=3、Slot B=3、Slot C=2 个结构 archetype（覆盖 N∈[1,5]），均 ≥2。
> **Slot C 退化说明**: Slot C 是 `lantern_count` multiplicity 轴（N∈[1,5]），通过 §8 的 copy logic 表达。它折为两个 archetype 而非五个 candidate，因为真实拓扑分叉只有两类：`single_arm`（直臂、单 part、单 joint）与 `multi_head_bar`（crossarm/bar root + 多 `lantern_{i}` part + 多 joint）。N 在 [2,5] 内的变化是同一 bar archetype 的 copy-count 派生（bar width、HOOK_XS、head_scale 随 N），不是新的结构家族，故归一个 candidate；这两类 part-tree/joint 拓扑差异满足 ≥2 结构差异。

## 槽位图（slot graph）

pattern: `mixed`（serial bracket→suspension→body 链 + 在 head 上的 `lantern_count` multiplicity）

```
wall_bracket (FIXED root)
  └─ [Slot A: scroll_arm | gooseneck_arm | chain_drop]  (plate + arm + hook + suspension)
       │  downstream interface: hook_eye @ (hx, HOOK_Y, HOOK_Z)  [pivot point]
       │
       └─[REVOLUTE lantern_swing  axis=X(1,0,0)  origin=hook_eye  range≈[-0.45,0.45]]→
            lantern[_i] (SWINGING child, frame origin = pivot, hangs −Z)
              └─ [Slot B: flared_roof_body | caged_cylinder_body | conical_roof_body]
                   (chain link/loop capture · cap/roof+finial · glass · cage · bottom ring [· socket+bulb])

  multiplicity (Slot C, lantern_count = N ∈ [1,5]):
    N=1 → single_arm: single straight arm, one lantern, one lantern_swing, HOOK_XS=[0]
    N=2 → multi_head_bar (or legacy fork): bar/fork root; 2× lantern_{i} + 2× lantern_swing_{i}, head_scale≈0.72, HOOK_XS=[-s,+s]
    N=3..5 → multi_head_bar: horizontal crossarm/bar (width ∝ N) with N eyes;
             N× lantern_{i} + N× lantern_swing_{i}; head_scale=f(N) (decreasing);
             HOOK_XS evenly spaced & symmetric about 0; each REVOLUTE about X at (HOOK_XS[i], HOOK_Y, HOOK_Z)
```

接口点位与策略:
- **wall_bracket ↔ wall**: plate 背面贴墙 y=0（FIXED support，wall 隐式）；plate front 在 +Y。
- **arm → hook_eye (downstream interface)**: 支臂末端汇聚到 hook curl/eye，eye 中心 = pivot `(hx, HOOK_Y, HOOK_Z)`。所有 Slot A candidate 必须把 eye 放在同一 canonical pivot（≥10 distinct 的兼容前提）。
- **hook_eye → lantern (cross-slot joint)**: REVOLUTE `lantern_swing[_i]`，axis=X，origin=pivot，range≈±0.45（conical_roof_body 因 parent-2 原 ±0.35，rebase 后统一夹到 ±0.45 上限，实测仍合法）。
- **suspension capture (intentional interlink)**: chain link[0]/loop 与 `bracket_hook` 互锁 (`allow_overlap` + `expect_contact`)；finial neck 穿过末 link/loop 底被捕获 (`allow_overlap`)；chain_drop 中相邻 link 互锁。
- **body internal interfaces**: roof/cap 顶座 finial；glass 在 cap 下、bottom ring 上；cage 包裹 glass（straps/bars proud of glass）；bulb（若有）在 glass 内、socket 座入 floor/cap。
- 互斥/派生: Slot A 三者互斥（同一支臂只能一种）；Slot C 派生 bracket 拓扑（N=1 `single_arm` 直臂 vs N≥2 `multi_head_bar` crossarm/bar，N=2 可退化 fork）与 per-head `head_scale=f(N)`、bar width∝N、`HOOK_XS`（均匀对称于 0）。

## 每槽位 Module Emits / Interfaces

### Slot A / scroll_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_bracket` 视觉: `wall_plate`(leaf), `scroll_arm`(tube), `bracket_hook`(curl) | parent1 / L134-L190, L193-L214, L217-L240 |
| internal joints | 无（bracket 为单刚体 root） | parent1 / L422-L439 |
| upstream interface | plate 背面 @ y=0 贴墙（FIXED） | parent1 / L164-L173 |
| downstream interface | hook_eye @ (0, HOOK_Y=0.235, HOOK_Z=0.060)；单 chain link 在此互锁 | parent1 / L217-L240, L484-L492 |

### Slot A / gooseneck_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_plate`, `gooseneck_arm`(高拱 tube), `bracket_hook` | gooseneck / L140-L196, L199-L224, L227-L250 |
| internal joints | 无 | — |
| upstream interface | plate 背面 @ y=0 贴墙 | gooseneck / L170-L179 |
| downstream interface | hook_eye @ 同 canonical pivot；臂 crest 高于钩眼≥0.10（assert L599-L611） | gooseneck / L495-L503 |

### Slot A / chain_drop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_plate`, `scroll_arm`, `bracket_hook`；lantern child 含 N 个 `chain_link_i` | chain_drop / L135-L191, L194-L215, L218-L242, L453-L459 |
| internal joints | 无（链为 visual capture，非 joint） | — |
| upstream interface | plate 背面 @ y=0 | chain_drop / L165-L174 |
| downstream interface | hook_eye @ canonical pivot；link0 互锁 hook，末 link 捕获 finial | chain_drop / L257-L295, L496-L504 |
| copied object (local) | N_CHAIN_LINKS 个 `chain_link_i`（candidate-local 计数，非模板级 lantern_count） | chain_drop / L66-L70, L261-L295 |

### Slot B / flared_roof_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | lantern 视觉: `chain_link`, `finial`, `roof`(flared cone), `glass`, `cage`(straps+bands), `bottom_ring`(+drip) | parent1 / L441-L478 |
| internal joints | 无（lantern 为单刚体 child） | — |
| upstream interface | chain_link 顶弧互锁 hook；finial neck 被 link 捕获 | parent1 / L274-L287, L290-L310 |
| downstream interface | 灯体下垂 −Z；bottom ring 最低 | parent1 / L379-L406 |

### Slot B / caged_cylinder_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chain_link`, `finial`, `roof_cap`(disk+lip+neck), `glass`, `bar_0..bar_{BAR_N-1}`, `band_0..band_{BAND_N-1}`, `bulb`, `bottom_ring` | caged / L490-L542 |
| internal joints | 无 | — |
| upstream interface | chain_link 互锁 hook；finial 被捕获 | caged / L281-L294, L297-L317 |
| downstream interface | 灯体下垂；bulb socket 座入 bottom_ring floor (`allow_overlap` L593-L598) | caged / L393-L423, L426-L453 |
| copied object (local) | BAR_N 个 `bar_i` + BAND_N 个 `band_i`（candidate-local cage 计数） | caged / L90-L93, L357-L390 |

### Slot B / conical_roof_body（rebased）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chain_loop`, `conical_roof`(直锥+stem+ball finial), `lantern_glass`(hollow tube), `base_ring`, `lantern_cage`(2 bands+4 straps), `lamp_socket`, `led_bulb` | conical / L423-L459 |
| internal joints | 无 | — |
| upstream interface | chain_loop 互锁 hook eye（rebase 后 loop 平面/eye 重标到 canonical XZ/YZ）；finial stem 穿过 loop | conical / L209-L225, L260-L279 |
| downstream interface | 灯体下垂；socket+bulb 在 glass 内 | conical / L352-L387 |
| rebase note | 原 parent-2 frame (outward +X, axis Y) → canonical (outward +Y, axis X)：坐标 (x_p2,0,z)→(0,y,z)，joint axis (0,−1,0)→(1,0,0)，pivot (HOOK_REACH,0,HOOK_EYE_Z)→(0,HOOK_Y,HOOK_Z) | conical / L466-L474 |

### Slot C / single_arm (N=1)
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `lantern` part + 单臂 bracket（无 fork/bar） | parent1 / L442, L484-L492 |
| internal joints | 1 个 `lantern_swing` REVOLUTE | parent1 / L484-L492 |
| interface | hook_eye @ (0, HOOK_Y, HOOK_Z)；HOOK_XS=[0] | parent1 / L484-L492 |

### Slot C / multi_head_bar (N≥2)
| emits | 描述 | 来源 |
|---|---|---|
| parts | crossarm/bar root（width∝N；N=2 可退化 `fork_trunk`+`fork_branch_{i}`）+ N 个 `bracket_hook_{i}`；`lantern_{i}` part ×N | double / L375-L392, L398-L437 |
| internal joints | `lantern_swing_{i}` REVOLUTE ×N，axis X，origin `(HOOK_XS[i], HOOK_Y, HOOK_Z)` | double / L442-L452 |
| interface | 每头 hook_eye_{i} @ `(HOOK_XS[i], HOOK_Y, HOOK_Z)`，HOOK_XS 均匀对称于 0；per-head `head_scale=f(N)`（N=2≈0.72，随 N 递减） | double / L76-L82, L394-L452 |
| copy logic | N∈[2,5]：N=2 直接采样（FORK_VARIANTS 证明 copy-logic），N=3–5 by-construction（同一 bar archetype 的 copy-count 派生，模板拥有 N_range） | double / L76-L82, L381-L398 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `arm_choice` | enum | `scroll_arm` / `gooseneck_arm` / `chain_drop` | — | choice | deterministic procedural sampler | Slot A table |
| `body_choice` | enum | `flared_roof_body` / `caged_cylinder_body` / `conical_roof_body` | — | choice | deterministic procedural sampler | Slot B table |
| `lantern_count` | int (multiplicity) | **[1, 5]**（N_range，模板拥有）；5★ 池仅直接采样 N∈{1,2}，N=3–5 by-construction | 1 | choice | weighted draw（偏小 N：1≈45% / 2≈30% / 3≈15% / 4≈7% / 5≈3%）；见 §8 | Slot C / double L76-L82 |
| `chain_link_count` | int (candidate-local) | [1, 6]；仅 `arm_choice=chain_drop` 时 >1 | 5 | conditional | 仅当 arm=chain_drop 激活；否则=1（单 link） | chain_drop L66-L70 |
| `cage_bar_count` | int (candidate-local) | [6, 10]；仅 `body_choice=caged_cylinder_body` | 8 | conditional | 仅 caged_cylinder body 激活；其余 body 用 strap cage（固定 6） | caged L90 |
| `palette_style` | enum | `galvanized_zinc`/`warm_galvanized_bronze`/`black_cast_iron`/`aged_copper`/`verdigris_copper`（见下表） | `galvanized_zinc` | choice | per-seed 采样，决定 material RGBA 集 | 各源 material 块 |
| `hook_reach_scale` | float | [0.85, 1.15] | 1.0 | independent | 缩放 HOOK_Y（钩眼外伸）；clamp 后 arm 末端重算到 eye | parent1 L59, double L40 |
| `lantern_size_scale` | float | [0.85, 1.10] | 1.0 | independent | 整灯体等比缩放（roof/glass/cage/ring 同乘） | double L79, L207-L229 |
| `head_scale` | float | derived，随 N 递减 | 1.0 (N=1) / ≈0.72 (N=2) / 递减至 N=5 | equation | `head_scale(N)` 单调递减（N=1→1.0，N=2→≈0.72，N=3..5 进一步缩小，使相邻 glass AABB 不交）；建议 `head_scale(N)=min(1.0, 0.72·2/N)` 之类的递减式，并被 §下 inequality 回缩 | double L79, L395-L396 |
| `bar_spacing` | float | derived（取代 `fork_x`） | spacing(2)=2·0.130=0.260 | conditional | N≥2：bar 半宽与 `HOOK_XS` 均匀对称于 0；`spacing(N)` = 相邻 hook 间距，bar width ∝ N；N=2 时可退化 fork（`fork_x`=spacing/2）；保证相邻头 AABB 不交（见 inequality） | double L77, L81 |
| `swing_range` | float | [0.30, 0.45] | 0.45 | independent | REVOLUTE lower/upper = ±swing_range；clamp 后验证闭合姿态不穿墙板 | parents L491/L458 |
| (—) | constraint | — | — | inequality | `相邻两头 glass AABB 不相交`（N≥2）：`2·glass_r·head_scale + clearance ≤ spacing(N)`（`spacing(N)`=相邻 hook 间距）；违反则增大 `spacing(N)`（加宽 bar）或减小 `head_scale(N)` | double L585-L588 |
| (—) | constraint | — | — | inequality | `cap/roof eave 覆盖 glass`：`roof_bot_r ≥ glass_r + margin`（flared/conical/caged 各自）；违反则放大 roof | parents expect_within |
| (—) | constraint | — | — | inequality | `finial top ≤ link 顶`，`bottom ring 最低`：垂直布局链按 §_z_layout 派生，禁止灯体顶穿 hook | parents L257-L271 等 |

连续尺寸采样契约：先采 independent（`hook_reach_scale`, `lantern_size_scale`, `swing_range`）→ 按 equation 派生 `head_scale=f(N)`（由 lantern_count，随 N 递减）→ conditional 解析 `bar_spacing`/`HOOK_XS`/`chain_link_count`/`cage_bar_count`（由上游 enum/N）→ 用 inequality 投影/回缩（相邻头间距 `2·glass_r·head_scale+clearance≤spacing(N)`、roof 覆盖、垂直链不穿模），不满足则回缩（加宽 bar 或缩小 head_scale）或拒绝重采。

### palette_style colorways（per-seed 采样，≥3；取自 5★ 源观察到的真实 material 集）
每个 colorway 给一组 metal/glass/accent material RGBA（贴合立面金属壁灯：黑/古铜/铜/铜绿/镀锌）。模板按 seed 采样 `palette_style`，再把 body/cage/accent material 名映射到该 colorway。

| palette_style | metal_body | metal_dark / accent | cage / strap | glass | bulb (若有) | 来源 |
|---|---|---|---|---|---|---|
| `galvanized_zinc` (default) | zinc `(0.66,0.68,0.69,1)` | zinc_dark `(0.55,0.57,0.59,1)` | iron_rust `(0.55,0.40,0.34,1)` | cool glass `(0.62,0.74,0.74,0.45)` | warm `(1.0,0.96,0.82,1)` | parent1 L417-L420 / caged L464-L467 |
| `warm_galvanized_bronze` | warm zinc `(0.64,0.65,0.62,1)` | dark galv `(0.52,0.53,0.50,1)` | reddish iron `(0.52,0.38,0.32,1)` | glass `(0.60,0.72,0.72,0.45)` | warm | gooseneck L428-L431 |
| `black_cast_iron` | cast_iron `(0.16,0.17,0.18,1)` | wrought_iron `(0.22,0.23,0.24,1)` | wrought_iron `(0.22,0.23,0.24,1)` | amber `(0.74,0.58,0.30,0.45)` | warm_bulb `(1.0,0.96,0.82,1)` + socket_brass `(0.55,0.45,0.22,1)` | parent2 L379-L383 |
| `aged_copper` | aged_copper `(0.42,0.28,0.18,1)` | wrought_iron `(0.22,0.23,0.24,1)` | wrought_iron `(0.22,0.23,0.24,1)` | amber `(0.74,0.58,0.30,0.45)` | warm_bulb + socket_brass | conical L393-L398 |
| `verdigris_copper` (派生) | verdigris green `(0.36,0.55,0.48,1)`（古铜绿，铜氧化外推） | dark patina `(0.24,0.36,0.32,1)` | wrought_iron `(0.22,0.23,0.24,1)` | cool glass `(0.62,0.74,0.74,0.45)` | warm | 由 aged_copper 风化外推（立面铜灯常见铜绿） |

> 5 colorway ≥3 ✓，黑 / 古铜(bronze) / 铜(copper) / 铜绿(verdigris) / 镀锌(zinc) 全覆盖。前 4 个 RGBA 直接取自 5★ 源 material 块；`verdigris_copper` 由 aged_copper 风化外推（真实立面铜灯的常见铜绿态），标注为派生。`palette_style` 仅改 material/颜色，不改任何拓扑或尺寸。

## Multiplicity / Copy Logic

> 单根 multiplicity 轴：`lantern_count`（lantern 头数）。candidate-local 计数（`chain_link_count`、`cage_bar_count`）**不是**模板级 multiplicity，它们由所选 candidate 内部循环复制 visual，不暴露为模板级 `*_count`，单独在 §7 conditional 行声明。

### 轴 1：`lantern_count`
- `count_param`: `lantern_count`
- `N_range`: **`[1, 5]`**（模板拥有该 range）。无 N≥3 的禁止：横向 multi-hook crossarm/bar 让 3–5 头沿一条水平 bar 均匀排开，每头独立 swing，相邻头间距由 inequality 保证不碰。
  - **采样 vs by-construction（诚实说明）**：5★ 池中只有 N∈{1,2} 被**直接采样**（single 变体 + `double_lantern` N=2）。N∈{3,4,5} 是 **by-construction**：模板的 `multi_head_bar` archetype 用同一 copy-logic（bar + N eyes + per-head scale）合法地把 N_range 扩到 5，**N_range 合法地超出被采样的 N**（FORK_VARIANTS 仅须证明 copy-logic 正确，N_range 的所有权归模板，不要求每个 N 都有独立 5★ 源）。
- sampling domain（权重档，偏小 N）: N=1 ≈45%（单头默认成熟域）、N=2 ≈30%（双头立面壁灯，有直接源）、N=3 ≈15%、N=4 ≈7%、N=5 ≈3%。
- copied object: 每个 head 一个 `lantern_{i}` part（含 chain link/loop + cap/roof + glass + cage + bottom ring [+ socket/bulb]）+ 一个 `lantern_swing_{i}` REVOLUTE；N≥2 时 bracket root 为 `multi_head_bar`（横向 crossarm/bar，width∝N）+ N 个 `bracket_hook_{i}`（N=2 可退化为既有 `fork_trunk` + `fork_branch_{i}`）。
- naming: `lantern_0..lantern_{N-1}`；joint `lantern_swing_0..lantern_swing_{N-1}`；hook `bracket_hook_0..bracket_hook_{N-1}`。N=1 时退化为无后缀 `lantern` + `lantern_swing` + 单 `bracket_hook`（或统一 `_0` 后缀，模板择一并在测试断言）。
- placement: head i 的 pivot = `(HOOK_XS[i], HOOK_Y, HOOK_Z)`，`HOOK_XS` **均匀对称分布于 0**（N=1→`[0]`；N=2→`[-s,+s]`；N≥3→N 个等间距点，中心 0，bar 半宽 ∝ N）。每头 lantern 几何在自身 pivot-原点局部系下垂 −Z。
- joint policy: 每头恰好 1 个独立 REVOLUTE swing，axis=X，range=±swing_range；所有头共享同一 FIXED bracket root；bar/fork 臂/hook 为 bracket 的 FIXED visual，不计入 swing 数。
- per-head scale: `head_scale=head_scale(N)` 随 N 单调递减（N=1→1.0，N=2→≈0.72，N=3..5 进一步缩小），使相邻 glass AABB 不交；不满足 inequality 时回缩 head_scale 或加宽 bar。
- source/gating: 任意相邻两头必须 AABB 不相交（inequality, §7：`2·glass_r·head_scale + clearance ≤ spacing(N)`），且每头悬挂 capture（link↔hook、finial↔link）独立成立；N≥2 时 body_choice 对所有头一致（同一 body candidate 复制，不混搭）。

## 拓扑多样性审计

总组合数：Slot A(3) × Slot B(3) × Slot C/lantern_count(5, N∈[1,5]) = **45 ≥ 10 ✓**（原 N∈{1,2} 时为 18；N_range 扩到 [1,5] 后跨 slot 拓扑等价类升到 45）。
（candidate-local `chain_link_count`/`cage_bar_count` 仅在各自 candidate 内变体，不另算入跨 slot 拓扑组合，但会增加 mesh 级多样性。）

理由：45 个 (arm × body × count) 组合每个都改变 part-tree / joint 拓扑（arm 改 bracket silhouette 与悬挂链 part 数；body 改 cap+cage+内构 part 集；count 改 part 数与 joint 数：N 个 `lantern_{i}`+N 个 swing，且 N=1 `single_arm` 直臂 vs N≥2 `multi_head_bar` crossarm/bar 是真实 root 拓扑分叉），远超 10。即便只算被直接采样的 N∈{1,2}（3×3×2=18）也已 ≥10；扩到 N=5 后 45 更稳过门控。N=3–5 为 by-construction，组合在采样中以小权重出现（见下 sweep plan）。

seed_domain_policy：`procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed 做 deterministic 加权采样：先抽 `arm_choice`（均匀 3 选 1）与 `body_choice`（均匀 3 选 1），再按权重抽 `lantern_count`（N∈[1,5]：1≈45% / 2≈30% / 3≈15% / 4≈7% / 5≈3%，偏小 N），再解析 candidate-local 计数与连续 scale（§7 契约）。compatibility matrix 排除非法组合（见下）。无需 curated/modulo 主表；`seed=0` 不特殊。少量 regression overrides 仅用于已知失败回归（见表，初版 none）。random sweep seeds 0-49 初版、0-999 成熟审计——加权偏小 N，但 0-999 sweep 应至少各覆盖一次 N=3/4/5（by-construction 的 multi_head_bar 必须实际被采到并 compile-pass）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本类别跨 slot 有 45 个纯拓扑等价类（3×3×5），叠加 candidate-local 计数（chain_link_count 6 档、cage_bar_count 5 档）后，离散拓扑变体数 ≈ 45 + 计数派生 ≈ 数十级；**可能仍低于 300，原因=类别天然结构家族有限（单一钟摆机构、固定 3×3×5 结构轴）**。主多样性来自 slot/body/count(N∈[1,5]) + candidate-local 计数 + 连续 scale，可接受。
Controlled local parameterization：关键连续 scale = `hook_reach_scale`[0.85,1.15]、`lantern_size_scale`[0.85,1.10]、`swing_range`[0.30,0.45]、派生 `head_scale=f(N)`（由 count，随 N 递减）、conditional `bar_spacing`/`HOOK_XS`（由 count+size，bar width∝N，均匀对称于 0）。全部在 `resolve_config` clamp/派生；按 §7 约束类型（independent→equation→inequality→conditional）求解，跨部件依赖（相邻头间距、roof 覆盖、垂直链不穿模）显式落 inequality，不当独立自由变量各抽各的。这些 scale 只改安全比例/clearance/外伸，不改 InterfaceSpec（hook_eye pivot）、MatingContract（capture interlink）或 multiplicity（N）本身。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 arm→body→count；arm/body 均匀，count 加权(1:0.45,2:0.30,3:0.15,4:0.07,5:0.03)；candidate-local 计数与 scale 后采 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 见下兼容性矩阵；所有 45 组合默认合法，唯 N≥2 需 body 全头一致 + 相邻头间距 gate | no floating / no collision（相邻头）/ axis=X / closed-pose 不穿墙 / N∈[1,5] / bulky body 缩放(head_scale=f(N)) |
| controlled local variation | hook_reach/lantern_size/swing_range/head_scale(N)/bar_spacing/HOOK_XS，clamp+派生 | 比例变化不破坏 hook_eye pivot、capture、roof 覆盖、joint range、类别身份 |
| regression overrides | none（初版）；后续仅记录具体失败 seed+理由 | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初版，0-999 成熟审计 | 与 contract 失败 |

兼容性矩阵 / gating（哪些跨 slot 组合不兼容）:
- arm × body：**全兼容**（任一支臂可挂任一 body；suspension capture 接口统一在 hook_eye）。`chain_drop` × 任一 body 合法（更长链只是顶部多 link，finial 仍被末 link 捕获）。
- count × body：N≥2 时所有头使用**同一** body candidate（不混搭）；N≥2 + `conical_roof_body`/`caged_cylinder_body` 允许，但需 `head_scale(N)` 缩小后 bulb/socket 内构仍在 glass 内（inequality）。N 越大 head_scale 越小，内构等比缩放仍成立。
- count × arm：N=1 用 `single_arm` 直臂；N≥2 强制 `multi_head_bar`（横向 crossarm/bar，N=2 可退化既有 fork，N≥3 必用 bar）替换直臂；`chain_drop` × N≥2 合法但每头各一条 N-link 链。
- gate 优先排除：相邻头碰撞（间距 inequality `2·glass_r·head_scale+clearance≤spacing(N)`，N 大时靠缩小 head_scale/加宽 bar 满足）、灯体顶穿 hook（垂直布局派生）、roof 不覆盖 glass（roof_bot_r 下限）、closed-pose（swing ±range）灯体撞墙板（hook_reach 下限保证外伸足够）、bar 总宽过大（N=5 bar 半宽随 head_scale 缩小受控，仍立面合理）。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A (arm/suspension) | 3 | yes | yes | scroll / gooseneck / chain_drop |
| B (lantern body/cap) | 3 | yes | yes | flared_roof / caged_cylinder / conical_roof |
| C (lantern_count) | 2 archetype | yes | no | multiplicity 轴 N∈[1,5]；2 个结构 archetype（single_arm / multi_head_bar），N=3–5 为 multi_head_bar 的 by-construction copy-count 派生 |

## Validator

- slot_choices_for_seed returns implemented module names（arm_choice, body_choice, lantern_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combinations（N∈[1,5]；N≥2 body 全头一致 + 相邻头间距 gate）
- optional regression overrides are sparse and justified（初版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped, cannot break hook_eye pivot / capture interlink / roof 覆盖 / joint range / lantern_count
- cross-part scale dependencies (head_scale(N) equation, bar_spacing/HOOK_XS/chain/bar conditional, 相邻头间距 inequality) resolved in `resolve_config`, not in builder
- critical InterfaceSpec/MatingContract exist: hook_eye pivot per head；chain link[0]/loop ↔ bracket_hook capture（allow_overlap+expect_contact）；finial neck ↔ 末 link capture
- key joints: `lantern_swing[_i]` REVOLUTE ×N，axis≈(1,0,0)，origin=`(HOOK_XS[i],HOOK_Y,HOOK_Z)`，range⊆[−0.45,0.45]
- copied objects follow naming/placement: `lantern_{i}`/`lantern_swing_{i}`/`bracket_hook_{i}`（i∈[0,N-1]）/`fork_branch_{i}`(N=2 退化)；chain_link_{i}/bar_{i}/band_{i} candidate-local
- mechanism: positive swing 把灯体底外移(+Y) 并抬升（pendulum arc）

## Reject cases

- 支臂不外伸或 hook_eye 不在墙前（hook_max_y ≤ plate front）→ 悬挂悬空/贴墙，reject。
- lantern_swing 非 REVOLUTE 或 axis 不平行墙面（非 X）→ 机构错误，reject。
- chain link/loop 不与 bracket_hook 互锁（无 capture contact）→ 灯体漂浮，reject。
- 灯体顶（finial/cap）穿过或高于 hook 撞支臂 → 垂直布局错误，reject。
- roof/cap eave 不覆盖 glass（roof_bot_r < glass_r）→ shade 不成立，reject。
- N≥2 任意相邻两头 glass AABB 相交（间距不足 `2·glass_r·head_scale+clearance > spacing(N)`）→ 多头碰撞，reject。
- lantern_count ∉ [1,5]（N<1 或 N>5）→ 越界 multiplicity，reject。
- N≥3 仍用 fork（仅 2 头硬编码）而非横向 crossarm/bar → bracket 拓扑错误，reject。
- N≥2 各头混用不同 body candidate → 非真实立面多头壁灯，reject。
- bulb（若有）超出 glass 包络或 socket 不座入 floor/cap → 内构脱节，reject。

## 与相邻类别的边界

- 不该混入：**articulated_task_lamp**（可调臂工作灯：臂上多个驱动关节 + 基座，运动是定位臂；本类只有单一钟摆 swing，灯体被动悬挂）。
- 不该混入：**chandelier / pendant light（吊灯）**（从天花板顶部下垂、非墙挂、常多臂辐射对称；本类有立面墙板 + 单侧向外悬挑的 bracket）。
- 不该混入：**street lamp / lamp post（落地路灯）**（落地竖杆、顶端灯头；本类墙挂、无落地杆）。
- 不该混入：**纯装饰 wall sconce（无活动灯体）**（固定灯罩贴墙；本类灯体钟摆可摆动，且由 chain 悬挂捕获）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。关键决策：(1) 采用 parent-1 canonical 框架（axis X / outward +Y），conical_roof_body（parent-2 派生）按坐标 relabel 做 rebase（geometry 不变）。(2) `lantern_count` 单 multiplicity 轴，**N_range=[1,5]**（按用户要求由 {1,2} 扩展，移除“禁止 N≥3”）；5★ 池仅直接采样 N∈{1,2}，N∈{3,4,5} 为 **by-construction**（N_range 合法地超出被采样 N，FORK_VARIANTS 仅证明 copy-logic）；N≥3 改用横向 multi-hook crossarm/bar（fork 仅 2 头硬编码不推广），per-head `head_scale=f(N)` 随 N 递减，相邻头间距 inequality `2·glass_r·head_scale+clearance≤spacing(N)`。(3) chain_link_count / cage_bar_count 为 candidate-local 计数，非模板级 multiplicity。(4) Slot C 折为 2 个结构 archetype（single_arm / multi_head_bar）覆盖 N∈[1,5]，已记降级理由。请确认：rebase 策略、swing_range 统一夹到 ±0.45、以及 N=3–5 by-construction（无独立 5★ 源）是否可接受。 |

## 模板实现备注（可选）

- 共享 helper：`_lathe_z`（roof/finial/drip/bulb 旋成体，三源一致）；`tube_from_spline_points`（arm/hook 管 + crossarm/bar）；`_lantern_z_layout(s)`（per-head scale 的垂直布局，single 用 s=1，N≥2 用 s=head_scale(N)）。
- crossarm/bar 实现：N≥2 的 `multi_head_bar` 用一条水平 tube（或 box）沿 X 跨过 `HOOK_XS` 全宽（width∝N），N 个 hook eyes 在 `HOOK_XS[i]` 处下垂；N=2 可保留既有 `_fork_trunk_mesh`+2`_fork_branch_mesh`（择一并测试断言）。`HOOK_XS` = N 个均匀对称分布于 0 的点，`spacing(N)`=相邻间距，由 head_scale(N) 反解保证不交。
- InterfaceSpec/MatingContract 注意：hook_eye pivot 必须三 arm candidate 与所有 N（每头 i）一致 origin 模式 `(HOOK_XS[i],HOOK_Y,HOOK_Z)`；capture interlink 用 element-scoped `allow_overlap`（chain_link↔bracket_hook、chain_link↔finial、chain_drop 相邻 link、caged bulb↔bottom_ring）。
- captured-pin / intentional overlap：每个 N 头（i∈[0,N-1]）与每个 chain_drop link 对都要复制对应的 `allow_overlap`（参考 §10 Overlap QC：一次性声明全部 N 头的 capture 对，避免 unmask 链式）。N=5 时即 5 头 ×（link↔hook + finial↔link）全部声明。
- rebase 实现：conical_roof_body 在 builder 内统一用 canonical 轴/坐标重写（不要保留 parent-2 的 axis=Y/outward +X），使其与其他 body 共享同一 lantern child frame 与 swing joint。
- 暂不进入 seed domain 的组合：无（45 组合全合法，N∈[1,5]）；N>5 永久排除（越界 multiplicity）。N=3–5 为 by-construction，须在 sweep 中实际被采样并 compile-pass（不能仅声明 range 而从不构造）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | scroll_arm | rec_build-...185910_557031 | L193-L214, L217-L240, L274-L287 | 低 scroll 臂 + hook + 单 link 悬挂 |
| S2 | A | gooseneck_arm | rec_lamp1_var_gooseneck_arm | L199-L224, L227-L250 | 高拱 shepherd's-crook 臂 |
| S3 | A | chain_drop | rec_lamp1_var_chain_drop | L194-L215, L261-L295, L453-L459 | scroll 臂 + N-link 链 (local count) |
| S4 | B | flared_roof_body | rec_build-...185910_557031 | L313-L406 | flared 锥 roof + glass + strap cage + ring |
| S5 | B | caged_cylinder_body | rec_lamp1_var_caged_cylinder_lantern | L320-L344, L357-L390, L393-L423, L426-L453 | 平 disk cap + round bar cage + bulb |
| S6 | B | conical_roof_body | rec_lamp1_var_conical_roof | L228-L279, L282-L296, L299-L349, L352-L387 | 直锥 copper roof + hollow glass + socket/bulb (rebased) |
| S7 | C | multi_head_bar (N≥2) | rec_lamp1_var_double_lantern | L155-L197, L207-L229, L398-L452 | N=2 直接采样的 fork/bar bracket + per-head lantern_{i} + swing_{i} + scale；copy-logic 推广到 N∈[2,5]（N≥3 crossarm/bar，by-construction） |
