# cauldron (traditional cast-iron cooking cauldron) — Modular Spec

> 来源小类：`picture/Other/cauldron`（articraft_data 上游 Other/cauldron fork-variant pool）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Other_cauldron.md`。
> **"cauldron" 在此 = 传统铸铁炊煮锅（cast-iron cooking pot）**：一只厚壁中空铸铁锅身（鼓腹 / 直筒 / 宽浅），上有可开合锅盖，配吊环 / 耳柄 / 三脚架悬挂，可选锅底铸铁腿。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（1 parent + 6 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5（逐一核对均为真 cauldron 铸铁锅）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一读全文核对）。引用以 part / joint / helper **名字** 为准（`pot_body` / `lid` / `loop_handle` / `_pot_solid` / `_bowl_solid` / `_lid_solid` / `_leg_solid` / `_hinge_lug_solid` / `_hinge_strap_solid` / `_clamp_arm_solid` / `_ear_solid` / `tripod_hub` / `lid_lift` / `lid_hinge` / `handle_pivot` / `clamp_pivot_{i}` / `hub_to_pot` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `cauldron` |
| template path | `agent/templates/Other_cauldron.py` |
| test path (optional) | `tests/agent/test_cauldron_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: pot_form + lid_mechanism + handle_suspension 各自挂到共同锅身 root（parallel children），**外加** `leg_count` 锅底腿多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、leg 循环与 run_tests 的 allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **parent（`f944b57b`）** 基线拓扑：`pot_body`（root，鼓腹中空 revolve 锅身 + 整体 pedestal 圆足）+ `lid`（child，domed disc + locating lip + 两个 handle boss）+ `loop_handle`（grandchild）。两个 joint：`lid_lift` PRISMATIC +Z（提盖 0.12 m）+ `handle_pivot` REVOLUTE +X（吊环 flat→upright）。无锅底腿（N=0）。
- **pot_form 轴（Slot A）**：straight_cylindrical（`26cd72d3`，`_pot_solid` 改 lathe 直筒 + 3 个 inline tab leg）/ wide_shallow_bowl（`cef6bfac`，`_bowl_solid` lathe 宽浅碗 + 3 个 inline revolved leg）相对 parent 的鼓腹 revolve 是 root 锅身 **mesh / 足迹形态**变化（part 树 / joint 拓扑不变），是 mesh-helper 维度。两个 cylindrical/bowl 变体**已内置 3 腿**（`for i in range(LEG_COUNT=3)` inline visual）→ 同时是 leg_count 的 copy-logic 源。
- **lid_mechanism 轴（Slot B）**：真正的 joint 拓扑变化。lift_off_dome（parent，`lid_lift` **1×PRISMATIC** +Z）/ hinged_flip（`8d43806f`，`lid_hinge` **1×REVOLUTE** +X 后铰翻盖，pot 上 `hinge_lug` + lid 上 `hinge_strap` captured 绕轴）/ clamp_locking（`607ffa31`，保留 `lid_lift` PRISMATIC **+ `clamp_{0,1}` 两片 REVOLUTE 卡扣** `clamp_pivot_{i}` 镜像，共 3 joint）。
- **handle_suspension 轴（Slot C）**：swing_bail（parent，`loop_handle` + `handle_pivot` **REVOLUTE** +X 吊环）/ side_loop_ears（`09d73153`，去吊环，改 `ear_{0,1}` 两个 **FIXED** 固定耳柄，盖无 boss）/ tripod_stand（`2de73386`，**改 root**：`tripod_hub` 为 root，3 条 FIXED 腿，pot 经 `hub_to_pot` **REVOLUTE** 钟摆悬挂在 hub 下；保留 bail/lid/handle）。tripod 是真正的 root coordinate / slot graph 变化 → 见 §5/§9 兼容门控。
- **leg_count 轴（多重性）**：锅底等角铸铁腿数。N=0（parent / hinged_flip / clamp_locking 鼓腹锅无腿，坐 pedestal 足）；N=3（cylindrical/bowl/ears 变体的 `for i in range(LEG_COUNT)`）。腿是**非移动件**（inline 锅身 visual 或 FIXED 子件），绕锅底等角；N=4 为内插（无独立样本，见 §3 阻塞说明）。

## 核心身份

一只**传统铸铁炊煮锅（cast-iron cooking cauldron）**：厚壁中空铸铁锅身（厚壁 revolve / lathe 开口腔体，真实可盛装的凹腔），形态可为鼓腹圆锅（round belly）/ 直筒锅（stockpot cylinder）/ 宽浅碗（cazo / 宽锅）；锅口上方一只锅盖按某种机构开合（**主活动语义 1**）：提盖（PRISMATIC +Z 提离锅口）/ 后铰翻盖（REVOLUTE +X 绕后 rim 翻开）/ 提盖 + 卡扣锁（PRISMATIC 提盖 + 双 REVOLUTE 卡扣解锁）；锅身侧 / 盖上配提握 / 悬挂方式（**主活动语义 2**）：摆动吊环（REVOLUTE +X bail）/ 固定双耳柄（FIXED 两侧 loop ear）/ 三脚架悬挂（tripod_hub root，pot 经 REVOLUTE 钟摆吊挂）；可选锅底等角铸铁腿 N∈[0,4]（吊挂锅 N=0、吉普赛三足 N=3、立式 N=4）。默认成熟域：单锅单盖 × pot_form × lid_mechanism × handle_suspension × leg_count 的小型铸铁炊具。

不该混入：
- **带盖储物 / 化妆罐（container_jar）**——玻璃 / 陶瓷罐 + 螺纹旋升盖 / 友配帽，是单独的 `container_jar`；cauldron 是铸铁炊具 + 吊环 / 三足 / 翻盖身份。
- **敞口收纳容器 / 桶（shopping_bucket / bag_suitcase_box）**——cauldron 必有锅盖开合机构 + 铸铁炊具身份（吊环 / 三足 / 厚壁黑铁）。
- **平底煎锅 / 单柄长锅（frying pan / skillet）**——单根长直柄、无盖、浅，缺 cauldron 的中空深腔 + 盖 + 吊环 / 三足身份。
- **女巫魔法锅装饰摆件（纯装饰无开合 / 无关节）**——本类要求 ≥1 真实 articulation（盖或吊环或钟摆）。

## 槽位 + 候选模块表

> **建模注记**：`pot_form`（Slot A）是 root 锅身**同一组 mesh 的足迹 / 廓形**（鼓腹 / 直筒 / 宽浅），由 pot-form-aware mesh helper（`_pot_solid` revolve / lathe 直筒 / `_bowl_solid` lathe 碗）一次决定，不是独立串联 slot、不贡献额外 joint；列为候选轴以对齐 schema，它与 lid_mechanism / handle_suspension / leg_count 的笛卡尔积共同撑开多样性（见 §9）。`lid_mechanism` 与 `handle_suspension` 才是真正改 part 树 / joint 拓扑（甚至 root）的轴。

### Slot A：pot_form（锅身形态 / 足迹——root 锅身的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_belly（基线）| parent `f944b57b` | `_pot_solid` revolve 鼓腹 + pedestal 足 L71-106（filled 对照 L109-132）| eligible if compatible | 鼓腹圆锅：单 revolve 廓形（spline 鼓到 0.45 m 腹 → 收到 0.28 m 口 → 12 mm 壁），底带整体 pedestal 圆足（无腿，坐地）|
| straight_cylindrical | rec_variant-pot-form-straight-cylindrical-reshape-th_..._26cd72d3 | `_pot_solid` lathe 直筒 + shoulder L90-110 / `_leg_solid` tab L128-137 | eligible if compatible | 直筒 stockpot：lathe 直墙（0.35 m 直径）+ 锥肩收口 + 平底；**内置 3 个 tab leg**（`for i in range(LEG_COUNT)` inline visual，带 rpy spin）|
| wide_shallow_bowl | rec_variant-pot-form-wide-shallow-bowl-reshape-the-d_..._cef6bfac | `_bowl_solid` lathe 宽浅碗 L79-113 / `_leg_solid` revolved L186-202 | eligible if compatible | 宽浅碗 / cazo：lathe 廓形（rim 0.50 m 宽，远宽于高，width/height>2.5）；**内置 3 个 revolved leg**（`for i in range(LEG_COUNT)` inline visual，无需 rpy）|

硬约束记录：pot_form 3 candidate（达 3-6 下限）。全部 revolve / lathe 中空开口厚壁腔，共享 lid / handle 接口（rim 顶面），只换廓形 / 高宽比 / 是否带 pedestal 足。

### Slot B：lid_mechanism（**主开合机构槽 1**——锅盖动作，决定盖的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| lift_off_dome（基线）| parent `f944b57b` | `_lid_solid` L135-148 + `_lid_lip_solid` L151-164 + `lid_lift` PRISMATIC L224-232 | eligible if compatible | 提盖：单 `lid` child（domed disc + locating lip 落入锅口），`lid_lift` **PRISMATIC** axis=(0,0,1)，lower=0 坐口 / upper=0.12 提离；lip↔pot_shell captured（lip nests 锅口）|
| hinged_flip | rec_variant-lid-mechanism-hinged-flip-replace-the-li_..._8d43806f | `_hinge_lug_solid` L169-193 / `_hinge_strap_solid` L216-244 / `lid_hinge` REVOLUTE L316-326 | eligible if compatible | 后铰翻盖：单 `lid` child（dome + `hinge_strap` 绕轴），pot 上加 `hinge_lug`（plate + barrel），`lid_hinge` **REVOLUTE** axis=(1,0,0)，origin 后 rim 外（HINGE_Y, HINGE_Z），lower=0 闭合 / upper=2.0（~115° 翻开）；strap wrap↔barrel captured |
| clamp_locking | rec_variant-lid-mechanism-clamp-locking-replace-the-_..._607ffa31 | `_clamp_lug_solid` L207-220 / `_clamp_arm_solid` L223-257 / `lid_lift` PRISMATIC L303-311 + `clamp_pivot_{i}` REVOLUTE L354-367 | eligible if compatible | 提盖 + 卡扣锁：保留 `lid` + `lid_lift` **PRISMATIC** +Z；lid 上加 `clamp_lug_{i}`，外挂 `clamp_{0,1}` 两 child（toggle 臂 + hook lip），`clamp_pivot_{0,1}` **2×REVOLUTE** 镜像 axis=(1,0,0)（i=1 用 rpy z=π 镜像），lower=0 锁 / upper=1.8 解锁外摆；共 3 joint（pris + 2 rev）|

硬约束记录：lid_mechanism 3 candidate（达 3-6 下限）。含 PRISMATIC（提盖）/ REVOLUTE（翻盖）/ PRISMATIC+2×REVOLUTE（提盖+卡扣）三种 joint 拓扑。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。

### Slot C：handle_suspension（**主机构槽 2**——提握 / 悬挂方式，决定 handle part 树、joint 拓扑，可能改 root）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| swing_bail（基线）| parent `f944b57b` | `_handle_solid` L167-178 + 盖上 `handle_boss_{0,1}` L204-215 + `handle_pivot` REVOLUTE L236-244 | eligible if compatible | 摆动吊环：`loop_handle` 半圆 bail（pin ends 落入盖 boss），`handle_pivot` **REVOLUTE** axis=(1,0,0)，挂在 `lid` 上（grandchild），lower=0 flat / upper=1.57 upright；pin↔boss captured-pin |
| side_loop_ears | rec_variant-handle-side-loop-ears-remove-the-swing-b_..._09d73153 | `_ear_solid` 半环 ear L169-211 + `pot_to_ear_{i}` FIXED L293-302 | eligible if compatible | 固定双耳柄：去吊环（盖无 boss），改 `ear_{0,1}` 两 child（半环 ear + 嵌锅壁 mount pad），`pot_to_ear_{0,1}` **2×FIXED** 镜像 ±Y（i=1 用 rpy z=π）；ear pad↔pot_shell captured embed；本机构**无独立活动件**（活动靠 lid_mechanism 提供）|
| tripod_stand | rec_variant-suspension-tripod-stand-suspend-the-caul_..._2de73386 | `_hub_solid` L230-238 / `_hook_mesh` L241-262 / `_bail_mesh` L265-285 / `hub_to_pot` REVOLUTE L383-393 | eligible if compatible | 三脚架悬挂（**改 root**）：`tripod_hub`（root，hub + 长 hanging rod + J-hook）+ 3 条 `leg_{i}`（`hub_to_leg_{i}` **FIXED** splay 撑地）；`pot_body` 经 `hub_to_pot` **REVOLUTE** axis=(1,0,0) 钟摆吊挂（lower/upper=∓0.40），pot 上挂 bail 弧（`bail_ear_{0,1}` + `bail_rod`）；保留盖 + 吊环（grandchild/great-grandchild）|

硬约束记录：handle_suspension 3 candidate（达 3-6 下限）。含 REVOLUTE（吊环，挂 lid）/ 2×FIXED（固定耳，挂 pot）/ REVOLUTE 钟摆（tripod，改 root，pot 成 child）三种结构家族。tripod_stand 是 root coordinate / slot graph 变化 → §5/§9 单独门控其与 leg_count / 其它 slot 的兼容。

## 槽位图（slot graph）

pattern: mixed（**非 tripod 时**：`pot_body` 为 root，lid / handle / 腿挂到它（parallel children）；**tripod 时**：`tripod_hub` 为 root，pot 经 REVOLUTE 挂 hub 下，lid/handle 再挂 pot）。`leg_count` 在锅底等角复制铸铁腿 visual / FIXED 子件。

```
[非 tripod 分支]  pot_body (ROOT, 坐地 z=0; 由 pot_form 决定 revolve/lathe mesh + pedestal/平底)
  │
  ├── [lid_mechanism slot]  (互斥三选一)
  │     ├─ lift_off_dome : lid ──[lid_lift: PRISMATIC +Z @ 锅口 rim 中心]
  │     ├─ hinged_flip   : lid ──[lid_hinge: REVOLUTE +X @ 后 rim hinge_lug barrel]  (+ pot.hinge_lug)
  │     └─ clamp_locking : lid ──[lid_lift: PRISMATIC +Z]  (+ lid.clamp_lug_{i})
  │                         clamp_0 ──[clamp_pivot_0: REVOLUTE +X @ lid rim +Y lug]
  │                         clamp_1 ──[clamp_pivot_1: REVOLUTE +X @ lid rim -Y lug, rpy z=π]
  │
  ├── [handle_suspension slot]  (互斥三选一; tripod 见下)
  │     ├─ swing_bail     : loop_handle ──[handle_pivot: REVOLUTE +X @ 盖 boss 线]  (挂 lid, grandchild)
  │     └─ side_loop_ears : ear_0 ──[pot_to_ear_0: FIXED @ +Y rim]
  │                         ear_1 ──[pot_to_ear_1: FIXED @ -Y rim, rpy z=π]   (盖无 boss)
  │
  └── [leg_count multiplicity 轴]  leg_{i}  i∈range(N)   (inline pot visual 或 FIXED 子件)
        N=0 → 无腿（坐 pedestal 足 / 平底）; N=3 → 120° 等角; N=4 → 90° 等角

[tripod 分支]  tripod_hub (ROOT, 世界原点 apex)  ← handle_suspension = tripod_stand 专属 root
  │   (hub_body + hook 长 hanging rod + J-hook)
  ├── leg_{i} ──[hub_to_leg_{i}: FIXED splay @ hub bottom, rpy=(0,LEG_SPLAY,azimuth)]  i∈range(3)
  │
  └── pot_body ──[hub_to_pot: REVOLUTE +X @ hook contact (0,0,-HOOK_DROP)]  (钟摆 ∓0.40)
        │   (pot_shell + bail_ear_{0,1} + bail_rod 弧 → 搭在 hook 上)
        └── [lid_mechanism slot 照常挂 pot] + [盖上 handle_pivot 吊环照常]
            （tripod 时 leg_count 指 tripod 的 3 撑地腿，锅底不再另加腿 → 见 §9 门控）
```

接口点位与 joint 语义：
- **lid_mechanism 接口（互斥）**：
  - lift_off_dome：`lid_lift` origin=(0,0,POT_RIM_Z)（锅口 rim 顶中心），axis +Z PRISMATIC，q=0 坐口 / q=0.12 提离；lid `lid_lip` 落入锅口（captured，`allow_overlap(lid_lip↔pot_shell)`）。
  - hinged_flip：`lid_hinge` origin=(0, HINGE_Y=-(LID_R+0.015), HINGE_Z=RIM+0.010)（后 rim 外 hinge_lug barrel），axis +X REVOLUTE，q=0 闭合 / q=2.0 翻开；lid `hinge_strap` wrap 绕 pot `hinge_lug` barrel（captured，`allow_overlap(hinge_strap↔hinge_lug)`）。dome visual 用 origin 偏移落回锅口上方。
  - clamp_locking：`lid_lift` PRISMATIC +Z 同 lift_off_dome；外加 `clamp_{i}` child，`clamp_pivot_{i}` origin=(0, ±CLAMP_R, CLAMP_PIVOT_Z)（lid rim ±Y lug），axis +X REVOLUTE，q=0 锁 / q=1.8 解锁外摆（i=1 rpy z=π 镜像）；clamp boss↔`clamp_lug_{i}` captured + hook↔pot_shell rim captured（`allow_overlap` 各段照搬 L565-590）。
- **handle_suspension 接口（互斥）**：
  - swing_bail：`handle_pivot` origin=(0,0,PIVOT_Z)（盖 boss 线，挂 `lid`），axis +X REVOLUTE，q=0 flat / q=1.57 upright；bail pin↔`handle_boss_{i}` captured-pin（`allow_overlap(handle_loop↔boss_{0,1})`）。
  - side_loop_ears：`pot_to_ear_{i}` origin=(0, ±EAR_MOUNT_R, EAR_MOUNT_Z)（锅壁侧，挂 `pot_body`），**FIXED**（i=1 rpy z=π 镜像）；ear pad↔pot_shell embed（`allow_overlap(ear_body↔pot_shell)`）；盖此时**无 boss**（无 bail）。
  - tripod_stand：root=`tripod_hub`；`hub_to_leg_{i}` origin=(0,0,-HUB_H/2) rpy=(0,LEG_SPLAY,azimuth) **FIXED**；`hub_to_pot` origin=(0,0,-HOOK_DROP) axis +X **REVOLUTE** 钟摆 ∓0.40；pot 上 `bail_rod` 搭 hook（`allow_overlap(bail_rod↔hook)`），leg-leg / leg-hub / leg-hook apex 汇聚 overlap 各段照搬 L461-485。
- **leg_count 接口**：锅底等角铸铁腿；non-tripod 时为 `pot_body` 的 inline visual（cylindrical/bowl 风格，Rule 1）或 FIXED 子件（ears 风格 `pot_to_leg_{i}` FIXED）。绕锅底等角（N=3→120°、N=4→90°），feet 落地 z≈0。
- **mating policy**：所有 hinge / pin / strap / ear pad / clamp boss / bail-on-hook 是 captured / friction 接口（销在 barrel / pad 嵌壁 / 弧搭钩），几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 rim / hinge / boss / hook 硬件）+ element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 段）。
- **rest pose**：所有盖 q=0 闭合 / 坐口、吊环 q=0 flat、卡扣 q=0 锁、tripod 钟摆 q=0 垂直；腿 / 耳 FIXED。盖开 / 吊环立 / 卡扣解 / 钟摆摆为 viewer 目检的活动语义。
- **互斥 / 可选 / 派生**：lid_mechanism 三候选互斥；handle_suspension 三候选互斥（tripod 独占 root 变化）；side_loop_ears 无独立活动件（空机构，活动靠 lid）；tripod_stand 把 root 从 pot 改为 hub，**锅底 leg_count 须 gate 为 0**（撑地靠 tripod 三腿，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / pot_form（root 锅身；以 rounded_belly 为例，cylindrical/bowl 仅换 mesh helper + 内置腿）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pot_body`（visual: `pot_shell`/`bowl_shell` revolve/lathe 厚壁中空锅身[ + leg_{i} inline 腿]）| parent `_pot_solid` L71-106 / cylindrical `_pot_solid` L90-110 / bowl `_bowl_solid` L79-113 |
| internal joints | 无（root 锅身本身无活动件；tripod 分支例外，见 Slot C）| — |
| upstream interface | 坐地 z=0（root；tripod 时改为 hub 的 REVOLUTE child）| — |
| downstream interface | 锅口 rim 顶面中心（lid joint parent 接口）+ 锅壁侧 / 后 rim（ear / hinge 硬件）+ 锅底（leg 接口）| parent POT_RIM_Z L41 |

### Slot B / lid_mechanism（每候选发射对应活动盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（dome + lip[ + hinge_strap / clamp_lug_{i}]）[+ pot.hinge_lug][+ clamp_{0,1}] | 各 lid 源 |
| internal joints | `lid_lift` PRISMATIC +Z（提盖）/ `lid_hinge` REVOLUTE +X（翻盖）/ `lid_lift` PRISMATIC + `clamp_pivot_{0,1}` 2×REVOLUTE（提盖+卡扣）| parent L224-232 / hinged_flip L316-326 / clamp L303-367 |
| upstream interface | lid_lip 落锅口（lift_off/clamp）/ hinge_strap 绕 pot barrel（hinged_flip）| parent L151-164 / hinged_flip L216-244 |

### Slot C / handle_suspension — swing_bail
| emits | 描述 | 来源 |
|---|---|---|
| parts | `loop_handle`（半圆 bail + pin ends）+ lid 上 `handle_boss_{0,1}` | parent L167-178, L204-215 |
| internal joints | `handle_pivot` REVOLUTE axis=(1,0,0)，origin=(0,0,PIVOT_Z)，挂 `lid`，lower=0 / upper=1.57 | parent L236-244 |
| upstream interface | bail pin↔盖 boss captured-pin | parent L278-291 (allow_overlap) |

### Slot C / handle_suspension — side_loop_ears
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ear_{0,1}`（半环 ear + 嵌壁 mount pad）；盖**无 boss** | ears `_ear_solid` L169-211 |
| internal joints | `pot_to_ear_{0,1}` **2×FIXED** origin=(0,±EAR_MOUNT_R,EAR_MOUNT_Z)（i=1 rpy z=π）| ears L293-302 |
| upstream interface | ear pad↔pot_shell embed captured | ears L342-349 (allow_overlap) |

### Slot C / handle_suspension — tripod_stand（改 root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tripod_hub`(root: hub_body + hook) + `leg_{0,1,2}`（splay 撑地）+ pot 上 `bail_ear_{0,1}` + `bail_rod` 弧 | tripod L230-285, L329-345 |
| internal joints | `hub_to_leg_{i}` **3×FIXED** splay + `hub_to_pot` **REVOLUTE** axis=(1,0,0) origin=(0,0,-HOOK_DROP) 钟摆 ∓0.40 | tripod L310-319, L383-393 |
| upstream interface | bail_rod 搭 hook cradle captured + leg-leg / leg-hub apex 汇聚 captured | tripod L454-485 (allow_overlap) |

### leg_count multiplicity（锅底腿复制；non-moving，non-tripod 分支）
| emits | 描述 | 来源 |
|---|---|---|
| parts | non-tripod：`leg_{i}` inline pot visual（cylindrical/bowl 风格，Rule 1）或 FIXED 子件（ears 风格）| cylindrical L195-205 / bowl L220-230 / ears L251-268 |
| joints | inline 风格无 joint（Rule 1）；FIXED 风格 `pot_to_leg_{i}` FIXED | ears L262-268 |
| placement | `for i in range(N)`，绕锅底等角（N=3→`2π·i/3`、N=4→`2π·i/4`），feet z≈0 | cylindrical L196-205 / bowl L221-230 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| pot_form | enum | rounded_belly / straight_cylindrical / wide_shallow_bowl | rounded_belly | choice | deterministic procedural sampler 选；决定 root 锅身 mesh helper | module table |
| lid_mechanism | enum | lift_off_dome / hinged_flip / clamp_locking | lift_off_dome | choice | sampler 选；主机构 1（互斥）| module table |
| handle_suspension | enum | swing_bail / side_loop_ears / tripod_stand | swing_bail | choice | sampler 选；主机构 2（互斥，tripod 改 root）| module table |
| leg_count (N) | int | 声明域 [0,4]；sweep 采样域 {0,3,4}（偏小加权：0 高频、3 常见、4 长尾）| 0 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；N 与 pot_form / handle_suspension 联动（见下 conditional + §8）| cylindrical/bowl leg 循环 |
| palette_style | enum | matte_black_cast_iron / weathered_rust_iron / seasoned_graphite / enamel_red / enamel_blue / polished_pewter | matte_black_cast_iron | palette | palette only，**不计入 slot_choice**；逐 seed 采样 | 各样本材质 |
| pot_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放锅身 belly/cyl/rim 半径主尺寸（保足迹比例），clamp | resolve clamp |
| pot_height_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放锅身高 → POT_RIM_Z → lid mount 高度，clamp | resolve clamp |
| rim_radius_scale | float | [0.92, 1.10] | 1.0 | equation | `RIM_R = base·rim_radius_scale`；lid 外径 / lip / hinge / ear / boss mount 半径派生跟随（保盖罩 / lip 配合）| resolve clamp |
| lid_open_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 REVOLUTE 盖 / 卡扣 / 吊环 `motion_limits.upper`，clamp（保 ≤π·0.95）| resolve clamp |
| lid_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 lift_off_dome / clamp_locking（PRISMATIC 提盖）有效；缩放 `lid_lift` upper（≥ 清锅口所需行程）| resolve clamp |
| leg_height_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 N≥1（有腿）有效；缩放腿高 → 抬锅高度，clamp（保 feet 落地 z≈0）| resolve clamp |
| swing_limit_scale | float | [0.80, 1.15] | 1.0 | conditional | 仅 tripod_stand 有效；缩放 `hub_to_pot` 钟摆 ∓limit，clamp（保 pot 不撞腿）| resolve clamp |
| (—) | constraint | — | — | inequality | 盖覆盖锅口：lift_off/clamp 闭盖 XY 覆盖锅口 ≥0.08 / hinged_flip dome footprint 覆盖锅口 ≥0.20；违反按比例回缩 lid / rim scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | lip / hinge / ear / boss 半径配合：`lid_lip_R ≤ RIM_INNER_R − clearance` 且 `lid_outer_R ≥ RIM_OUTER_R + overhang`；违反按比例回缩 | 接口 / clearance |
| (—) | constraint | — | — | conditional | handle_suspension=tripod_stand 时 leg_count gate 为 0（撑地靠 tripod 三腿）；非 tripod 时 N∈{0,3,4} 自由（见 §8/§9）| 接口 / root |
| (—) | constraint | — | — | conditional | 腿排布不超锅底：N·leg_footprint 绕锅底等角不互撞，`leg_placement_R` 按 pot_width 派生（保 feet 在锅底外缘内）| 接口 / clearance |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。`rim_radius_scale` 为 equation（lid / lip / hinge / ear / boss mount 半径跟随 rim）。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 pot_form / lid_mechanism / handle_suspension / N 的拓扑或 root**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（锅底等角铸铁腿数）：

- **count_param**：`leg_count`（模板内变量 N / LEG_COUNT；锅底等角铸铁腿数）。
- **N_range**：声明产品域 **[0, 4]**（吊挂锅 N=0 / 吉普赛三足 N=3 / 立式 N=4）。`config_from_seed` 的 sweep 采样域 **{0, 3, 4}**（偏小加权：N=0 高频、N=3 常见、N=4 长尾）。**采样集合是离散 {0,3,4} 而非连续 [0,4]**——真实 cauldron 腿数现实上只有 0（吊挂 / 坐地 pedestal）、3（最常见的吉普赛三足）、4（立式四足）；1/2 腿不稳定、不真实，不采。N=0 即 parent 退化（无腿，坐 pedestal / 平底，不进循环）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((0,3,4), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp / snap 到 {0,3,4}（非法值 snap 到最近合法值）。
- **copied object**：单只铸铁腿——`leg_{i}`，共享 helper 发射（cylindrical 的 tab `_leg_solid` mesh / bowl 的 revolved `_leg_solid` / ears 的 `_make_leg_solid`）；N 个 visual 复用同一几何对象。
- **naming**：`leg_{i}`（inline visual 风格，cylindrical/bowl）或 `leg_{i}` 部件 + `pot_to_leg_{i}` FIXED（子件风格，ears）；`for i in range(N)`（cylindrical L196 / bowl L221 / ears L251 已用此结构，可直接作 copy-logic 源）。
- **placement**：绕锅底 **绝对式**等角分布——`theta = 2π·i/N`，`x = R·cos θ`、`y = R·sin θ`（N=3→120°、N=4→90°）；`leg_placement_R` 按 pot_width 派生。绝对式（每个 i 的角度由 N 解析，不累加漂移）是 N-不变前提；tab leg 需 `rpy=(0,0,theta)` 对齐，revolved leg 无需 rpy。
- **joint policy**：腿是**非移动件**（Rule 1）→ inline 为 `pot_body` visual（cylindrical/bowl 风格，**无独立 joint**）或 FIXED 子件（ears 风格 `pot_to_leg_{i}` FIXED）；活动关节由 lid_mechanism / handle_suspension 提供。**统一建议采用 inline visual 风格**（更简，Rule 1），N=0 不发射腿。
- **source/gating**：copy-logic 源取 cylindrical L195-205 / bowl L220-230（N=3 inline）/ ears L251-268（N=3 FIXED）；**N=0 取 parent / hinged_flip / clamp 的无腿鼓腹锅**（坐 pedestal）；N=4 内插（无独立样本，§3 阻塞说明：仅改 `range(3)`→`range(4)` + 角度 120°→90°，是 N-参数化的直接外推，无新拓扑）。**tripod_stand 时 leg_count gate 为 0**（撑地靠 tripod 三腿，锅底不另加腿；tripod 自身 3 腿是 handle_suspension module 固定结构，不受 leg_count 控制）。

## 拓扑多样性审计

总组合数：pot_form(3) × lid_mechanism(3) × handle_suspension(3) × leg_count 采样数(3，即 {0,3,4}) = **81**（扣除 tripod×N>0 的非法组合后实际合法组合见兼容矩阵）。

仅 lid_mechanism(3) × handle_suspension(3) = **9**（含 PRISMATIC / REVOLUTE / PRISMATIC+2REVOLUTE 盖 × REVOLUTE 吊环 / 2FIXED 耳 / REVOLUTE 钟摆改 root 的 joint 拓扑组合）≈ 已接近门控；叠 pot_form(3) → 27 ≥ 10 已稳过，叠 N 后充裕。

理由：lid_mechanism × handle_suspension 提供真正的 joint 拓扑差异（提盖 PRISMATIC / 翻盖 REVOLUTE / 提盖+双卡扣 × 吊环 REVOLUTE / 双固定耳 FIXED / 三脚架钟摆 REVOLUTE-改root = 9 种 joint-topology 类，且 tripod 整个改 root），叠 pot_form(3) 与 N({0,3,4}) 后总 81（扣非法）distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("leg_count", f"n{N}")`，对齐 cushion/shopping_bucket/fence_cascade），否则无腿与多腿在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（pot_form / lid_mechanism / handle_suspension），经兼容矩阵合法化（tripod gate N=0），再 `rng.choices` 加权 N∈{0,3,4}，再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 pot_width_scale / pot_height_scale / rim_radius_scale（equation）/ lid_open_scale / lid_travel_scale（conditional@PRISMATIC 盖）/ leg_height_scale（conditional@N≥1）/ swing_limit_scale（conditional@tripod）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：lid_travel 仅 PRISMATIC 盖、leg_height 仅 N≥1、swing 仅 tripod；并 gate tripod→N=0）→ 采 independent width/height/open scale → 派生（rim_radius equation 驱动 lid/lip/hinge/ear/boss mount 半径）→ 用两条 clearance inequality（盖覆盖锅口、lip/罩半径配合）投影 / 回缩。跨部件依赖（盖覆盖 vs rim、lip vs 内口径、腿排布 vs 锅底）显式落在 §7 inequality / conditional，在 `resolve_config` 内求解。这些 scale 不破坏 lid joint origin（rim 顶 / 后 rim hinge / boss 线 / hook）、盖罩配合、ear/leg 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵，tripod gate N=0），再 `rng.choices` 加权 N∈{0,3,4}，再 uniform 各 scale + `rng.choice` palette | slot_choices_for_seed 含 `("leg_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **tripod_stand × leg_count**：tripod 改 root 且自带 3 撑地腿 → 锅底 leg_count **gate 为 0**（pot 悬挂在空中，不能再有锅底腿撑地）；非 tripod 时 N∈{0,3,4} 自由。 (2) **side_loop_ears × lid_mechanism**：ears 去吊环但盖照常 → 与任意 lid_mechanism 正交（提盖 / 翻盖 / 卡扣均可配双固定耳）。 (3) **swing_bail × hinged_flip**：吊环挂 lid，翻盖时吊环随盖翻 → 兼容（吊环 boss 在 dome apex，翻盖整体动）；但翻盖开到 2.0 时吊环若 upright 可能超界 → resolve 派生吊环 upper 随 lid_open clamp。 (4) **clamp_locking × side_loop_ears / tripod**：卡扣挂 lid rim，与耳 / tripod 正交 → 允许。 (5) **leg_count × pot_form**：rounded_belly 带 pedestal 足，N≥1 时腿替代 pedestal 落地（resolve 派生 leg_placement_R 按 belly 外缘）；cylindrical/bowl 平底，N≥1 标准。 (6) pot_form 与 lid / handle 机构正交。 | 无 floating / collision / tripod 配锅底腿双重撑地 / 盖不覆盖锅口 / lip 超内口径 / 腿互撞 / 钟摆撞腿 |
| controlled local variation | 8 个 clamped scale（pot_width/height、rim_radius(eq)、lid_open、lid_travel@PRISMATIC、leg_height@N≥1、swing_limit@tripod），每 build 统一；conditional 随 lid_mechanism / N / handle_suspension 解析 | 比例变化不破坏 lid/hinge/boss/hook origin、盖罩 / lip 配合、坐地 / 悬挂、N 复制、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 逐机构 QC（盖动作 / 吊环立 / 卡扣解 / 钟摆摆 / 腿落地）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| pot_form | 3 | yes | yes | rounded_belly(parent revolve) / straight_cylindrical(lathe+3腿) / wide_shallow_bowl(lathe+3腿) |
| lid_mechanism | 3 | yes | yes | PRISMATIC 提盖 / REVOLUTE 翻盖 / PRISMATIC+2REVOLUTE 提盖+卡扣（互斥主机构 1）|
| handle_suspension | 3 | yes | yes | REVOLUTE 吊环 / 2FIXED 耳 / REVOLUTE 钟摆改root（互斥主机构 2）|
| leg_count (N) | 3（采样集 {0,3,4}，0 高频 / 4 长尾）| yes | yes | 拓扑维度，编入 slot_choice；tripod 时 gate 0 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("leg_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样集 ⊆ {0,3,4}
- `resolve_config` 把 leg_count snap 到 {0,3,4}，各 scale clamp 到声明范围；lid_travel / leg_height / swing_limit 为 conditional 随 lid_mechanism / N / handle_suspension 解析；两条 clearance inequality 在 resolve 内投影 / 回缩；**tripod_stand → leg_count gate 为 0**
- compatibility matrix / gating 阻止非法组合（tripod×N>0 双重撑地降级 N=0；盖闭合必覆盖锅口；lip ≤ 内口径；腿不互撞；钟摆不撞腿）
- 连续 scale clamp 后不破坏 lid/hinge/boss/hook origin / 盖罩 / lip 配合 / 坐地 / 悬挂 / N 复制
- 关键 joint：lift_off `lid_lift` PRISMATIC axis≈(0,0,1)（abs(axis[2])>0.99）；hinged_flip `lid_hinge` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99）；clamp `lid_lift` PRISMATIC +Z + `clamp_pivot_{0,1}` 2×REVOLUTE ±镜像 axis≈(1,0,0)；swing_bail `handle_pivot` REVOLUTE axis≈(1,0,0)；side_loop_ears `pot_to_ear_{0,1}` 2×FIXED；tripod `hub_to_pot` REVOLUTE axis≈(1,0,0) 钟摆 ∓limit + `hub_to_leg_{i}` 3×FIXED
- captured 接口：element-scoped `allow_overlap`（lift_off `lid_lip`↔`pot_shell`；hinged_flip `hinge_strap`↔`hinge_lug`；clamp `clamp_arm`↔`clamp_lug`/`pot_shell`；swing_bail `handle_loop`↔`handle_boss_{0,1}`；ears `ear_body`↔`pot_shell`；tripod `bail_rod`↔`hook`/leg-leg/leg-hub），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `leg_{i}` 命名 + 绝对式绕锅底等角 placement + Rule 1（inline visual 无独立 joint，或 FIXED）
- grandfather：所有 hinge / pin / strap / ear / clamp / bail-hook captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 无腿与多腿 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- tripod_stand 同时加锅底 leg_count>0 → pot 悬空 + 锅底腿双重撑地、腿悬在半空漂浮；必须 gate（tripod→N=0）。
- 把 tripod_stand 当普通 child slot（不改 root）→ pot 仍 root、hub 漂浮无支撑；tripod 必须 root=tripod_hub、pot 经 REVOLUTE 挂其下。
- 用 boxy 占位体（纯 Box）当圆锅 body → 失类别身份；圆 / 直筒 / 碗 body 必须 revolve / lathe 厚壁中空开口腔。
- 锅身做成实心（无中空腔）→ 失 cauldron 炊具身份；必须 revolve 薄壁开口（hollow_vol < 0.40·filled_vol，照搬各样本 hollowness 测试）。
- lid / clamp / handle / hinge origin 放在锅心或任意点而非真实 rim 顶 / 后 rim hinge_lug / 盖 boss 线 / hook 硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 盖 / 卡扣 / 吊环 / 钟摆 rest pose 设成张开 / 抬起而非 q=0 闭合 / flat / 锁 / 垂直 → current-pose 与 viewer 目检不符（所有样本 lower=0 / 闭合姿态）。
- 给 captured-pin / strap / ear / clamp / bail-hook 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 采 N=1 或 N=2 腿 → 不真实 / 不稳定（cauldron 腿数现实为 0/3/4）；采样集只 {0,3,4}。
- 把连续尺寸 / 颜色 / 材质（palette_style / pot scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"女巫魔法装饰锅 / 平底煎锅 / 玻璃储物罐"语义混入 → 出类，本类是带盖铸铁炊煮锅。

## 与相邻类别的边界

- 不该混入：**container_jar 带盖储物 / 化妆罐**——玻璃 / 陶瓷 + 螺纹旋升 / 友配帽，是单独 slug；cauldron 是铸铁炊具 + 吊环 / 三足 / 翻盖。
- 不该混入：**shopping_bucket / bag_suitcase_box 敞口收纳容器 / 桶**——无锅盖开合机构 + 无铸铁炊具身份。
- 不该混入：**平底煎锅 / 单柄长锅（frying pan / skillet）**——单根长直柄、无盖、浅腔，缺 cauldron 的深中空腔 + 盖 + 吊环 / 三足身份。
- 不该混入：**纯装饰魔法锅摆件**——无 articulation；本类要求 ≥1 真实活动机构（盖 / 吊环 / 钟摆）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) pot_form 建模为 mesh-helper 维度（非串联 slot）；(2) leg_count 采样集取离散 {0,3,4}（N=1/2 不真实排除，N=4 内插无独立样本，见 §3）；(3) **tripod_stand 改 root + gate leg_count=0** 的兼容降级策略是否接受（这是最关键的 root coordinate 变化）；(4) leg 复制统一用 inline visual 风格（Rule 1）还是保留 ears 的 FIXED 子件风格；(5) Topology target ~63<300 的说明是否接受（本小类真实结构上限）；(6) palette_style 6 档（黑铁 / 锈铁 / 石墨 / 红珐琅 / 蓝珐琅 / 锡白）是否合适）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_pot_solid`（revolve 鼓腹 / lathe 直筒）/ `_bowl_solid`（lathe 宽浅碗，按 pot_form 切换）+ `_pot_filled_solid`（hollowness 测试对照）+ `_lid_solid` / `_lid_lip_solid`（盖，全机构公用）+ `_leg_solid`（腿，N 复制复用同一几何）+ `_hinge_lug_solid` / `_hinge_strap_solid`（hinged_flip）+ `_clamp_arm_solid` / `_clamp_lug_solid`（clamp）+ `_ear_solid`（ears）+ `_hub_solid` / `_hook_mesh` / `_bail_mesh`（tripod）。圆 / 直筒 / 碗 body 用 CadQuery `revolve` + `mesh_from_cadquery`。
- root 分支：non-tripod → root=`pot_body`；tripod → root=`tripod_hub`，pot 经 `hub_to_pot` REVOLUTE 挂下，lid/handle 再挂 pot（注意 lid_lift / handle_pivot origin 需按 pot_body frame 的 BAIL_APEX_Z 偏移，照搬 tripod L401/L414）。
- captured 接口 allow_overlap：`run_cauldron_tests` 里逐机构补 element-scoped `allow_overlap`（lip↔shell / strap↔lug / clamp boss↔lug + hook↔rim / bail pin↔boss / ear pad↔shell / bail_rod↔hook + leg apex 汇聚），照搬各样本 run_tests 段（parent L268-291、hinged_flip L366-389、clamp L565-590、ears L329-349、tripod L454-505）。
- conditional 范围解析顺序：先采 lid_mechanism / handle_suspension / N → gate tripod→N=0 → 解析 lid_travel（仅 PRISMATIC 盖）/ leg_height（仅 N≥1）/ swing_limit（仅 tripod）→ 采 width/height/open independent scale → 派生 rim_radius equation（lid/lip/hinge/ear/boss 半径跟随）→ 投影两条 clearance inequality（盖覆盖锅口、lip/罩半径配合）。
- leg copy：统一建议 inline visual 风格（cylindrical/bowl 的 `for i in range(N)` pot.visual + 绝对式角度，Rule 1 无独立 joint）；N=0 不发射；tab leg（cylindrical）需 `rpy=(0,0,theta)`，revolved leg（bowl）无需 rpy。
- 参考模板：`agent/templates/Container_Jar.py`（同为 parallel_children + body mesh helper + 多 lid 机构互斥分支 + captured-fit allow_overlap + Config/ResolvedConfig + resolve clamp 骨架）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 兼容矩阵 gating + captured-pin allow_overlap）。cauldron 的 root-切换（tripod）参考 root-变化模板（如 playground_swing 类悬挂结构）的 hub-root + 钟摆 child 范式。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（parent 基线）| rounded_belly + lift_off_dome + swing_bail | rec_model-a-traditional-...cauldron_..._f944b57b | `_pot_solid` L71-106 / `_lid_solid` L135-148 / `_lid_lip_solid` L151-164 / `_handle_solid` L167-178 / `lid_lift` PRISMATIC L224-232 / `handle_pivot` REVOLUTE L236-244 / allow_overlap L268-291 | 鼓腹锅 body 基线 + 提盖 PRISMATIC + 吊环 REVOLUTE + captured-pin 范式 |
| S2 | A | straight_cylindrical | rec_variant-pot-form-straight-cylindrical-..._26cd72d3 | `_pot_solid` lathe 直筒 L90-110 / `_leg_solid` tab L128-137 / leg 循环 L195-205 | 直筒 stockpot body（lathe）+ tab leg copy-logic 源（N=3 inline）|
| S3 | A | wide_shallow_bowl | rec_variant-pot-form-wide-shallow-bowl-..._cef6bfac | `_bowl_solid` lathe L79-113 / `_leg_solid` revolved L186-202 / leg 循环 L220-230 | 宽浅碗 / cazo body（lathe）+ revolved leg copy-logic 源（N=3 inline）|
| S4 | B | hinged_flip | rec_variant-lid-mechanism-hinged-flip-..._8d43806f | `_hinge_lug_solid` L169-193 / `_hinge_strap_solid` L216-244 / `lid_hinge` REVOLUTE L316-326 / allow_overlap L366-373 | 后铰翻盖（REVOLUTE +X + hinge_lug/strap captured wrap）|
| S5 | B | clamp_locking | rec_variant-lid-mechanism-clamp-locking-..._607ffa31 | `_clamp_lug_solid` L207-220 / `_clamp_arm_solid` L223-257 / `lid_lift` PRISMATIC L303-311 / `clamp_pivot_{i}` REVOLUTE L329-367 / allow_overlap L565-590 | 提盖 + 双卡扣锁（PRISMATIC + 2×REVOLUTE 镜像 toggle）|
| S6 | C | side_loop_ears | rec_variant-handle-side-loop-ears-..._09d73153 | `_ear_solid` L169-211 / `pot_to_ear_{i}` FIXED L293-302 / leg 子件 L251-268 / allow_overlap L329-349 | 双固定耳柄（2×FIXED，去吊环）+ FIXED-子件 leg 风格源 |
| S7 | C | tripod_stand（改 root）| rec_variant-suspension-tripod-stand-..._2de73386 | `_hub_solid` L230-238 / `_hook_mesh` L241-262 / `_bail_mesh` L265-285 / `hub_to_leg_{i}` FIXED L310-319 / `hub_to_pot` REVOLUTE L383-393 / allow_overlap L454-505 | 三脚架悬挂（root=hub + pot 钟摆 REVOLUTE + bail 搭 hook）|
</content>
</invoke>
