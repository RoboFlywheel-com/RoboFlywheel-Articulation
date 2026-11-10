# corkscrew (winged "butterfly" / direct-pull T-handle corkscrew) — Modular Spec

> 来源小类：`picture/Kitchen/Corkscrew`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Corkscrew.md`。
> **"Corkscrew" 在此 = 红酒开瓶器（wine corkscrew）：螺旋蜗杆 worm + 用户把手 + 进给机构**。
> 结构家族 = 经典翼形("butterfly")开瓶器：一只 `body_frame`（root，钟形 bell skirt + 双竖板 plate + 支腿 leg + 铆钉 boss）+ 两片 `wing_lever` 杠杆翼（铆钉枢轴，REVOLUTE，~100° 行程）+ 一根 `rack_spindle` 齿条主轴（沿板间槽竖直下行 PRISMATIC，~0.04m）+ 一个 `t_handle_worm` 蜗杆把手部件（worm helix + shaft core + T-bar，绕主轴 CONTINUOUS 旋转）。另一分支是 **direct-pull**（无翼，body 加顶 bridge，用户旋 T-bar 蜗杆然后直拔）。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对）。引用以 part / joint / helper **名字** 为准（`body_frame`/`wing_lever_{i}`/`wing_paddle_{i}`/`rack_spindle`/`t_handle_worm`/`ball_knob_worm`/`foil_cutter` part；`wing_pivot_{i}`/`spindle_travel`/`worm_spin`/`cutter_spin` joint；`_build_body_frame`/`_build_wing`/`_build_paddle_wing`/`_build_aero_blade`/`_build_bent_tbar`/`_build_ball_knob`/`_build_foil_cutter_collar`/`_build_cutter_blade`/`_build_rack_sleeve`/`_build_worm` helper），行号仅作定位。
>
> **坐标约定（全 8 样本统一，无家族分歧）**：直立摆放，bell 接地于 z=0；竖直轴 = **+Z**（worm/主轴轴线）；翼枢轴沿 **Y**（镜像 ±Y）；T-bar 横杆沿 **X**；主轴下行 PRISMATIC axis=(0,0,−1)；worm/cutter 旋转 CONTINUOUS axis=(0,0,+1)。所有样本完全一致 → 模板无需 rebase。

## 元信息
| 项 | 值 |
|---|---|
| slug | `corkscrew` |
| template path | `agent/templates/Kitchen_Corkscrew.py` |
| test path (optional) | `tests/agent/test_corkscrew_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `body_frame`；`rack_spindle` PRISMATIC 挂 body，`t_handle_worm` CONTINUOUS 挂 spindle；wing_geometry 两翼 REVOLUTE 并列挂 body；可选 foil_cutter CONTINUOUS 挂 body；mechanism=direct_pull 时整套翼缺席）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、BLADE/PERF 常量与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（winged 全部 7 个样本）**：`body_frame`（root，bell skirt 旋转壳 + 双竖板 + 4 支腿 + 2 组铆钉 boss）+ `wing_lever_{i}`×2（铆钉枢轴 REVOLUTE，齿条扇齿面对主轴）+ `rack_spindle`（齿环堆 + guide collar 在板间槽滑行 PRISMATIC）+ `t_handle_worm`（worm helix + shaft core + 把手；CONTINUOUS 绕 +Z 旋）。`spindle_travel` PRISMATIC + `worm_spin` CONTINUOUS 是**所有 winged 候选共享的核心运动**；翼是 `wing_pivot_{i}` 双 REVOLUTE。captured 接口：铆钉销过盈进翼 hub bore、guide collar 过盈进板槽、shaft core 过盈进 sleeve bore（parent L468-545）。
- **Slot A wing geometry 轴**：4 个候选只换翼 mesh helper，part 树 / joint 拓扑**不变**（两翼 REVOLUTE 不变）——属翼形态维度（spade/paddle/curved/lattice），与 mechanism=winged 绑定。
  - spade（parent）：`_build_wing`（polyline 叉形 spade 臂 + 4 圆齿）L119-166，平面挤出，叉尖；parent 手写两翼。
  - paddle：`_build_paddle_wing`（宽 polyline 桨叶 half-width 0.015 + 6 径向 box 齿）L121-181，翼重构为 `for i in range(2)` 循环 L251-276。
  - curved：`_build_aero_blade`（3 段椭圆 `loft` + 3 齿）L119-165，真 3D 弯刀形（非平面挤出），循环翼 L237-258。
  - lattice：`_build_wing` + `PERF_ROWS` 通孔 cut 循环 L130-187（PERF_ROWS 常量 L55-62），spade 翼镂空穿孔，循环翼 L256-264。
- **Slot B handle 轴**：3 个候选改 `t_handle_worm` 顶端把手 mesh（worm_spin 的 child visual），joint 拓扑不变（仍单 CONTINUOUS）。
  - straight_t_bar（parent）：`t_bar`（横 Cylinder 沿 X）+ `t_bar_tip_{i}`（球端帽，`for i,sx in enumerate((-1,1))`）L268-280，经典横 T 杆。
  - angled_bar：`t_bar` visual = `_build_bent_tbar`（boss + 两臂上倾 30° + 球尖，`for sign in (-1,1)`）L200-234，visual L305-309，V 形上折 T-bar。
  - ball_knob：part 改名 `ball_knob_worm` L275；`ball_knob` visual = `_build_ball_knob`（lathe sphere ~21mm + neck）L200-216，visual L288-292，单球握把替横杆。
- **Slot C foil crown 轴**：可选 `foil_cutter` 部件（bell bore 内额外 CONTINUOUS 旋转盘），是 part 数 / joint 拓扑变化。
  - plain（parent）：无 `foil_cutter` part / 无 `cutter_spin` joint，裸 bell bore。
  - rotating_cutter：`foil_cutter` part = `_build_foil_cutter_collar`（旋转环 collar）L220-235 + `blade_{i}`×3（`for i in range(BLADE_COUNT=3)`，`_build_cutter_blade`）L238-250, L343-350；`cutter_spin` CONTINUOUS +Z L396-404，press-fit 进 bell bore（allow_overlap L642-666）→ **+1 part +1 非 fixed joint**。
- **Slot D mechanism 轴**：整体运动拓扑 —— **winged vs direct_pull**。
  - winged（parent）：`wing_lever_{i}`×2 + `wing_pivot_{i}`×2 REVOLUTE + `rack_spindle`/`spindle_travel` + `t_handle_worm`/`worm_spin`，双翼齿条驱动主轴下行（butterfly 机构）。
  - direct_pull：**无翼 part / 无 `wing_pivot_*`**；`body_frame` 加顶 `bridge` + shaft bore（`_build_body_frame` L113-132），仅 `spindle_travel` PRISMATIC + `worm_spin` CONTINUOUS（无 Slot A）。

## 核心身份

一只**红酒开瓶器（wine corkscrew）**：核心永远是一根**螺旋蜗杆 worm**（真实 helix sweep，世界竖直 +Z 轴）+ 一个**用户把手**（旋蜗杆入瓶塞）+ 一套**进给/起塞机构**。两大机构家族：
- **winged ("butterfly") 翼形**（成熟主域）：黑色 `body_frame`（钟形 bell skirt 坐瓶口 + 双竖黑板 + 支腿 + 铆钉 boss），两片铬翼 `wing_lever` 绕铆钉枢轴 **REVOLUTE**（~100°）摆起，内侧扇齿啮合主轴齿条，把齿条主轴 `rack_spindle` 沿板间槽 **PRISMATIC** 顶下 ~0.04m；主轴上端 `t_handle_worm`（worm helix + shaft core + T-bar 把手）绕轴 **CONTINUOUS** 旋入瓶塞。
- **direct_pull 直拔**（无翼小分支）：同 body+bell，但 body 顶加 `bridge` 横梁 + shaft bore，无翼；用户直接旋 T-bar 蜗杆入塞，再沿 PRISMATIC 直拔起塞。

默认成熟域：mechanism=winged 时 wing_geometry(4) × handle(3) × foil_crown(2) = 24；mechanism=direct_pull 时（无 wing_geometry）handle(3) × foil_crown(2) = 6。活动语义 = **worm CONTINUOUS 旋入**（全候选共享）+ **主轴 PRISMATIC 下行**（全候选共享）+ winged 的 **双翼 REVOLUTE 摆动** + 可选 **foil cutter CONTINUOUS 旋转**。整体尺度小（body ~0.05m 宽，T-bar 顶 ~0.17m 高，主轴行程 ~0.038m）。

不该混入：
- **bottle opener（撬盖式开瓶器 / 啤酒起子）**——杠杆撬瓶盖，无螺旋蜗杆、无 worm 旋入运动；本类 identity 在 helical worm + 旋入/起塞，缺 worm 即出类。
- **waiter's friend / 侍者刀（lever wine key）**——折叠刀身 + 单铰 worm + 双台阶 fulcrum 撬臂，主运动 spine 是折叠铰 + 撬动，不是本类的竖直 PRISMATIC 进给 + 双翼/直拔（如需可作单独 slug）。
- **electric / lever-arm corkscrew（电动 / 单手压杆开瓶器）**——单根长压杆 + 内置自动旋入，与本类双翼齿条 / 直拔的机构家族不同。

## 槽位 + 候选模块表

> **建模注记**：`wing_geometry`（Slot A）是 `wing_lever` part **同一两翼的 mesh 形态**（spade/paddle/curved/lattice），由翼 mesh helper 一次决定，**不改 part 树 / joint 拓扑**（两翼 REVOLUTE 不变）；列为候选轴以对齐 schema，与 handle × foil_crown 笛卡尔积撑开 winged 多样性（见 §9）。**Slot A 仅在 mechanism=winged 时存在**（direct_pull 无翼可贴 → 兼容矩阵 gate，见 §9）。`foil_crown`（Slot C）与 `mechanism`（Slot D）才是改 part 数 / joint 拓扑的轴（foil cutter +CONTINUOUS / direct_pull −两翼两 REVOLUTE）。`handle`（Slot B）改把手 mesh，joint 拓扑不变（仍单 worm_spin CONTINUOUS）。

### Slot A：wing geometry（杠杆翼形态 —— **仅 mechanism=winged**，两翼 mesh helper，不改拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| spade（基线）| rec_model-a-classic-winged-butterfly-corkscrew-about_...65a27fb6（parent）| `_build_wing`（叉形 spade polyline + 4 圆齿 + pivot bore）L119-166 / 两翼 `wing_lever_0`/`wing_lever_1` 手写 L234-245 | eligible if compatible (mech=winged) | 平面挤出叉尖 spade 翼，叉形圆角尖 + 4 圆齿扇区；parent 基线（两翼手写）|
| paddle | rec_corkscrew_var_wing_paddle | `_build_paddle_wing`（宽桨 polyline half-width 0.015 + 6 径向 box 齿）L121-181 / `for i in range(2)` 翼 `wing_paddle_{i}` L251-276 | eligible if compatible (mech=winged) | 宽扁桨形翼（明显比 spade 宽，X 跨 >0.026），6 齿扇区；翼重构为 `for i in range(2)` 循环 + 镜像轴 |
| curved | rec_corkscrew_var_wing_curved | `_build_aero_blade`（3 段椭圆 `loft` + 3 齿）L119-165 / `for i in range(2)` 翼 `wing_lever_{i}` L237-258 | eligible if compatible (mech=winged) | 雕塑弯刀 / aero 翼（真 3D 椭圆 loft，向外弓出，Y 厚 > 平板），3 齿；循环翼 |
| lattice | rec_corkscrew_var_wing_lattice | `_build_wing` + `PERF_ROWS` 通孔 cut 循环 L130-187（PERF_ROWS 常量 L55-62）/ `for i in range(2)` 翼 `wing_lever_{i}` L256-264 | eligible if compatible (mech=winged) | spade 翼镂空交错圆孔（轻量化 lattice，6 行 staggered 穿孔）；循环翼 |

### Slot B：handle / drive grip（蜗杆部件顶端把手 —— `worm_spin` 的 child visual，joint 拓扑不变）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_t_bar（基线）| rec_model-a-classic-winged-butterfly-corkscrew-about_...65a27fb6（parent）| `t_bar`（横 Cylinder 沿 X，`rpy=(0,π/2,0)`）L268-273 + `t_bar_tip_{i}`（球端帽，`for i,sx in enumerate((-1,1))`）L274-280 | eligible if compatible | 经典横 T 横杆 + 两小球端帽，作 `t_handle_worm` visual（无独立 joint）；横杆沿 X、跨 ≥0.065 |
| angled_bar | rec_corkscrew_var_handle_angled_bar | `_build_bent_tbar`（boss + 两臂上倾 30° + 球尖，`for sign in (-1,1)` mirror）L200-234 / `t_bar` visual=bent_t_bar mesh L305-309 | eligible if compatible | V 形上折 T-bar，两臂从 hub 上倾约 30°，球尖收口；作 `t_handle_worm` visual（无 joint）|
| ball_knob | rec_corkscrew_var_handle_ball_knob | part 改名 `ball_knob_worm` L275 / `_build_ball_knob`（lathe sphere R≈0.0105 + neck）L200-216 / `ball_knob` visual L288-292 | eligible if compatible | 单球握把（直径 ~21mm）+ 短 neck 接 shaft top，替代横杆；shaft core 顶降低让球坐上方；作 `worm` part visual（无 joint）|

### Slot C：foil crown（可选铝箔切割冠 —— bell bore 内额外旋转部件，改 part/joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| plain（基线）| rec_model-a-classic-winged-butterfly-corkscrew-about_...65a27fb6（parent）| 无 `foil_cutter` part / 无 `cutter_spin` joint | eligible if compatible | 裸 bell bore，无切箔冠；parent 基线（空机构）|
| rotating_cutter | rec_corkscrew_var_crown_rotating_cutter | `foil_cutter` part：`_build_foil_cutter_collar`（旋转环 collar，BLADE_COUNT/CUTTER 常量 L205-217）L220-235 + `blade_{i}`×3（`for i in range(BLADE_COUNT=3)`，`_build_cutter_blade`）L238-250, L343-350 + `cutter_spin` **CONTINUOUS** +Z L396-404 + allow_overlap(frame_shell↔cutter_collar) L642-666 | eligible if compatible | 环形切箔冠 + 3 内向刀片，绕 bell bore 轴 **CONTINUOUS** 旋（bell mouth 内 press-fit）；**+1 part +1 非 fixed joint** |

> 降级理由（Slot C 仅 2 candidate）：现实开瓶器的切箔冠形态词汇表本身只有"无冠"与"旋转切箔冠"两种真实收敛形态——fork 池只造了 plain（parent 基线）与 rotating_cutter 两个。这是受真实结构上限约束的合法 2-candidate slot（plain 是空机构基线、rotating_cutter 是 +1 part+joint 的真实拓扑增量）。审核如需扩容应回 fork 池补造（如固定式 foil 刀环、侧翻式切箔器），不在模板侧虚构。Slot A(4) × Slot B(3) 已提供 winged 主拓扑多样性，Slot C ×2 充裕（见 §9）。

### Slot D：mechanism（整体驱动机构 / 运动拓扑 —— winged vs direct_pull）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| winged（基线）| rec_model-a-classic-winged-butterfly-corkscrew-about_...65a27fb6（parent）| `wing_lever_{i}`×2 + `wing_pivot_0`/`wing_pivot_1` **REVOLUTE** ±Y L284-302 / `rack_spindle`+`spindle_travel` PRISMATIC L304-312 / `t_handle_worm`+`worm_spin` CONTINUOUS L314-322 | eligible if compatible | 翼形 butterfly：两齿条杠杆翼驱动主轴下行（含 Slot A 两翼）；定义性机构 |
| direct_pull | rec_corkscrew_var_mech_direct_pull | **无翼 part / 无 `wing_pivot_*`**；`body_frame` 加顶 `bridge`+shaft bore（`_build_body_frame` L113-132）/ 仅 `spindle_travel` PRISMATIC L220-228 + `worm_spin` CONTINUOUS L230-238 / run_tests 断言无 wing part/joint L253-264 | eligible if compatible | 无翼直拔：body 顶加 bridge 横梁，用户旋 T-bar 蜗杆入塞再直拔；**无 Slot A**（兼容矩阵 gate）|

## 槽位图（slot graph）

pattern: parallel_children（固定 root `body_frame`；`rack_spindle` PRISMATIC 挂 body；`t_handle_worm` CONTINUOUS 挂 spindle；wing_geometry 两翼 REVOLUTE 并列挂 body；可选 foil_cutter CONTINUOUS 挂 body；mechanism=direct_pull 时整套翼缺席、body 加 bridge）

```
body_frame (root, 坐地于 bell skirt; bell + 双竖板 + 支腿 + 铆钉 boss; direct_pull 额外加顶 bridge+shaft bore)
  │
  ├── rack_spindle ──[spindle_travel: PRISMATIC axis=(0,0,−1), origin=(0,0,JOINT_TOP_Z=0.123)]   ← 全候选共享主进给
  │     │   （guide collar captured 进板间槽：allow_overlap(rack_sleeve, frame_shell) + expect_overlap z≥0.015）
  │     │
  │     └── t_handle_worm ──[worm_spin: CONTINUOUS axis=(0,0,+1), origin=(0,0,0)]   ← 全候选共享 worm 旋入
  │           │   （shaft core 过盈 running fit 进 sleeve bore：allow_overlap(rack_sleeve, shaft_core)）
  │           └── [handle slot 顶端把手 = worm part visual]  (三选一, 无 joint)
  │                 ├─ straight_t_bar : t_bar(横 Cyl 沿 X) + t_bar_tip_{i} i∈range(2)
  │                 ├─ angled_bar     : bent_t_bar mesh(boss + 两臂上倾 30° + 球尖)
  │                 └─ ball_knob      : ball_knob mesh(sphere + neck); part 改名 ball_knob_worm
  │
  ├── [wing_geometry slot — 仅 mechanism=winged]  两翼固定对(loop range(2), 非 N 轴)
  │     wing_lever_0 ──[wing_pivot_0: REVOLUTE axis=(0,+1,0), origin=(−PIVOT_X,0,PIVOT_Z), lower=0/upper≈1.745(100°)]
  │     wing_lever_1 ──[wing_pivot_1: REVOLUTE axis=(0,−1,0), origin=(+PIVOT_X,0,PIVOT_Z), lower=0/upper≈1.745(100°)]
  │       （翼 mesh = wing_geometry 候选: spade/paddle/curved/lattice; 铆钉销 captured 进翼 hub bore）
  │       （mechanism=direct_pull: 整段缺席 — 无 wing part、无 wing_pivot joint）
  │
  └── [foil_crown slot]  (二选一)
        ├─ plain          : (无 foil_cutter part, 无 cutter_spin joint)
        └─ rotating_cutter: foil_cutter ──[cutter_spin: CONTINUOUS axis=(0,0,+1), origin=(0,0,0.003)]
              （collar press-fit 进 bell bore：allow_overlap(frame_shell, cutter_collar); blade_{i} i∈range(3) 内向刀片）
```

接口点位与 joint 语义：
- **body → rack_spindle（全候选共享）**：mating = 双板间槽 + guide collar。PRISMATIC axis=(0,0,−1)，origin=(0,0,JOINT_TOP_Z=0.123)（板顶面，parent L309）；rest q=0（主轴在板槽内，worm 悬 bell 上方）。captured：guide collar 在板槽内过盈 → `allow_overlap(rack_sleeve, frame_shell)` + `expect_overlap(z, min=0.015)`（parent L499-512）。motion_limits lower=0/upper=TRAVEL≈0.038。
- **rack_spindle → t_handle_worm（全候选共享）**：mating = sleeve bore。CONTINUOUS axis=(0,0,+1)，origin=(0,0,0)（与 PRISMATIC 帧重合，parent L319）；motion_limits 无上下限（CONTINUOUS）。captured：shaft core running fit 进 sleeve bore → `allow_overlap(rack_sleeve, shaft_core)` + `expect_within(xy, margin=0.001)` + `expect_overlap(z, min=0.020)`（parent L514-538）。
- **body → wing_lever_{i}（mechanism=winged 时，两翼固定对）**：mating = 铆钉 boss。REVOLUTE，wing_pivot_0 axis=(0,+1,0) origin=(−PIVOT_X,0,PIVOT_Z)；wing_pivot_1 axis=(0,−1,0) origin=(+PIVOT_X,0,PIVOT_Z)（镜像，parent L284-302）；lower=0/upper=WING_RANGE≈1.745(100°)，rest q=0（翼下垂贴板侧）。captured：铆钉销过盈进翼 hub bore → `allow_overlap(rivet_pin_{i}, wing_blade)` + `expect_overlap(y, elem=rivet_pin_{i}, min=0.004)`（parent L468-497）。
- **body → foil_cutter（foil_crown=rotating_cutter 时）**：mating = bell bore。CONTINUOUS axis=(0,0,+1)，origin=(0,0,0.003)（collar 坐 bell mouth 内 z=0..0.006，cutter L396-404）；motion_limits 无上下限。captured：collar 外壁 press-fit 进 bell 内壁 → `allow_overlap(frame_shell, cutter_collar)` + `expect_overlap(xy, min=0.002)` + `expect_overlap(z, min=0.004)`（cutter L642-666）。
- **handle 候选 → t_handle_worm**：t_bar/tip、bent_t_bar、ball_knob 作 `t_handle_worm`(/`ball_knob_worm`) visual，无独立 joint（随 worm CONTINUOUS 旋转）。
- **mating policy**：所有 captured 接口（rivet-in-hub-bore、collar-in-板槽、shaft-in-sleeve-bore、cutter-collar-in-bell-bore）是 captured-fit（销/领/杆嵌入孔/槽），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有 winged 翼 q=0（下垂贴板）；主轴 q=0（worm 悬 bell 上方，hb[0][z]>0.004）；worm/cutter q=0（CONTINUOUS rest 任意，取 0）。
- **互斥 / 可选 / 派生**：mechanism 二候选互斥（winged / direct_pull）；wing_geometry 四候选互斥**且仅 winged 可用**（direct_pull gate 掉整个 Slot A）；handle 三候选互斥；foil_crown 二候选互斥（plain=空机构 / rotating_cutter=+1 part+joint）。foil_crown 与 mechanism / handle 正交（任意可配）。

## 每槽位 Module Emits / Interfaces

### Slot D / mechanism — winged（含 root body + 共享主轴/蜗杆 + 两翼）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body_frame`（root，visual：`frame_shell` = bell skirt + 双竖板 + 4 支腿 + `rivet_pin_{i}`×2 + `rivet_cap_{i}_{0/1}`×4）+ `rack_spindle`（`rack_sleeve` = 齿环堆 + guide collar）+ `t_handle_worm`（`worm_helix` + `shaft_core` + handle）+ `wing_lever_{i}`×2 | parent `_build_body_frame` L80-116 / 铆钉 L215-231 / `_build_rack_sleeve` L169-184 / `_build_worm` L187-197 / 翼 L234-245 |
| internal joints | `spindle_travel` PRISMATIC axis=(0,0,−1) origin=(0,0,0.123) lower=0/upper≈0.038 + `worm_spin` CONTINUOUS axis=(0,0,+1) origin=(0,0,0) + `wing_pivot_0/1` REVOLUTE ±Y origin=(∓PIVOT_X,0,PIVOT_Z) lower=0/upper≈1.745 | parent L284-322 |
| upstream interface | root（坐地于 bell skirt z=0，无父）| parent L367-368 |
| downstream interface | 板间槽（供 rack_spindle PRISMATIC）+ 铆钉 boss（供翼 REVOLUTE）+ bell bore（供 foil_cutter）| parent L304-312, L284-302 |

### Slot D / mechanism — direct_pull（无翼，body 加 bridge）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body_frame`（root，visual：`frame_shell` = bell + 双板 + 支腿 + **顶 bridge 横梁 + shaft bore**，无铆钉 boss）+ `rack_spindle` + `t_handle_worm`；**无 wing part** | direct `_build_body_frame`+bridge L76-134 |
| internal joints | 仅 `spindle_travel` PRISMATIC + `worm_spin` CONTINUOUS；**无 wing_pivot** | direct L220-238 |
| upstream interface | root（坐地）| direct L291-293 |
| downstream interface | 板间槽（供 rack_spindle）+ bridge shaft bore（主轴穿出顶）| direct L113-132 |

### Slot A / wing_geometry — spade / paddle / curved / lattice（仅换翼 mesh helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wing_lever_{i}`×2（spade/curved/lattice）或 `wing_paddle_{i}`×2（paddle），visual `wing_blade`/`paddle_blade`（翼形 mesh 由 helper 决定）| spade `_build_wing` L119-166 / paddle `_build_paddle_wing` L121-181 / curved `_build_aero_blade` L119-165 / lattice `_build_wing`+PERF L130-187 |
| internal joints | `wing_pivot_{i}` REVOLUTE ±Y（由 mechanism=winged 提供，翼 mesh 不改 joint）| parent L284-302 / paddle L266-276 / curved L247-257 |
| upstream interface | 翼 hub bore captured 铆钉销（`allow_overlap(rivet_pin_{i}, wing_blade)` + `expect_overlap(y, min=0.004)`）| parent L468-497 |

### Slot B / handle — straight_t_bar / angled_bar / ball_knob（worm part visual，无 joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（把手作 `t_handle_worm`/`ball_knob_worm` visual）：`t_bar`+`t_bar_tip_{i}`（straight）/ `t_bar`=bent mesh（angled）/ `ball_knob`+改名 part（ball_knob）| straight parent L268-280 / angled `_build_bent_tbar` L200-234, L305-309 / ball `_build_ball_knob` L200-216, L275, L288-292 |
| internal joints | 无（把手随 worm_spin CONTINUOUS 旋转）| — |
| upstream interface | 把手坐 shaft top（captured 过盈进 shaft core 顶 / boss）| straight L268-273 / ball L207-216 |

### Slot C / foil_crown — rotating_cutter（plain 为空机构无 emit）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `foil_cutter`（visual：`cutter_collar` 旋转环 + `blade_{i}`×3 内向刀片）| cutter `_build_foil_cutter_collar` L220-235 / `_build_cutter_blade` L238-250 / L337-350 |
| internal joints | `cutter_spin` CONTINUOUS axis=(0,0,+1)，origin=(0,0,0.003)，无上下限 | cutter L396-404 |
| upstream interface | collar 外壁 press-fit 进 bell 内壁（`allow_overlap(frame_shell, cutter_collar)` + `expect_overlap(xy, min=0.002)` + `expect_overlap(z, min=0.004)`）| cutter L642-666 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| mechanism | enum | winged / direct_pull | winged | choice | 由 deterministic procedural sampler 选；direct_pull 时整个 wing_geometry slot 缺席（gate Slot A）| Slot D 表 |
| wing_geometry | enum | spade / paddle / curved / lattice | spade | conditional choice | **仅 mechanism=winged 生效**；direct_pull 时此 slot 不采样、不进 slot_choice | Slot A 表 |
| handle | enum | straight_t_bar / angled_bar / ball_knob | straight_t_bar | choice | sampler 选；把手作 worm visual（无 joint）| Slot B 表 |
| foil_crown | enum | plain / rotating_cutter | plain | choice | sampler 选；rotating_cutter 加 `foil_cutter` part + `cutter_spin` CONTINUOUS | Slot C 表 |
| palette_style | enum | chrome_black（默认）/ all_chrome / brass_black / gunmetal / antique_brass | chrome_black | palette | palette only，**不计入 slot_choice**；每 seed 采一套（见下表）| 各样本材质 |
| body_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 body X 主尺寸（PLATE_W / bell 半径，保 body ~0.05m 读作开瓶器），clamp | parent L34 / L28-31 |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放板高 / 钟高（PLATE_Z0/Z1 / BELL_H）→ 联动 PIVOT_Z / JOINT_TOP_Z / 整体 ~0.17m 高，clamp | parent L37-38 / L27 |
| spindle_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 PRISMATIC upper（进给行程 TRAVEL），clamp（≤ worm 可下行到 bell mouth 的行程）| parent L58 / L311 |
| worm_radius_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 worm coil 半径 + shaft core 半径（保 shaft-in-sleeve 过盈带），clamp | parent L54-57, L69 |
| wing_len_scale | float | [0.85, 1.15] | 1.0 | conditional | **仅 mechanism=winged**；缩放翼长 WING_LEN（保举翼 tip-to-tip span 0.15-0.21m），clamp | parent L49 |
| wing_open_scale | float | [0.85, 1.05] | 1.0 | conditional | **仅 mechanism=winged**；缩放 `wing_pivot_{i}` upper（WING_RANGE，保 ≤π·0.62），clamp | parent L51 / L291 |
| handle_span_scale | float | [0.85, 1.15] | 1.0 | conditional | handle=straight/angled 时缩放横杆跨度 TBAR_LEN（保 ≥0.065 读作把手）；ball_knob 时改缩 BALL_R | parent L76 / ball L75 |
| cutter_radius_scale | float | [0.90, 1.10] | 1.0 | conditional | **仅 foil_crown=rotating_cutter**；缩放 collar 半径（保 press-fit 进 bell bore 过盈带），clamp | cutter L207-217 |
| (—) | constraint | — | — | inequality | shaft-in-sleeve 过盈带：`sleeve_bore_r = shaft_r·worm_radius_scale − embed`，embed≈0.0003；违反则同步缩 sleeve bore 保过盈 | parent L55 |
| (—) | constraint | — | — | inequality | 进给不超 bell：`TRAVEL·spindle_travel_scale ≤ (rest worm 底 z − bell mouth z) + bell 内深`；违反按比例缩 travel（保 worm 下行穿 bell mouth 但不脱出底）| parent L451-457 |
| (—) | constraint | — | — | inequality | rest worm 悬空正：worm part 底 `hb[0][z] > 0.004`（rest 时 worm 不戳穿桌面）；违反抬高 rest 位或拒绝重采 | parent L382-384 |
| (—) | constraint | — | — | inequality | cutter-in-bell 过盈带（@rotating_cutter）：`CUTTER_R_OUT·cutter_radius_scale ≥ bell 内壁 r + 0.002`（保 press-fit）且 collar 不低于 bell skirt（cutter 底 z≥−0.001）；违反缩 cutter_radius | cutter L207, L668-672 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 5★ 样本观察的真实材质 + 现实开瓶器配色外推）：
| palette_style | body_frame | wing / spindle / worm | handle | foil_cutter（@rotating）| 来源 |
|---|---|---|---|---|---|
| chrome_black（默认）| 哑黑 (0.07,0.07,0.08) | 抛光铬 (0.76,0.78,0.81) | bright_steel (0.86,0.87,0.89) | cutter_steel (0.72,0.73,0.76) | 全 8 样本基线材质 |
| all_chrome | 抛光铬 frame | 抛光铬 | 抛光铬 | 铬 | 样本 chrome 族全身化 |
| brass_black | 哑黑 frame | 黄铜 (0.80,0.62,0.26) wing/spindle | 黄铜 | 黄铜 | 黄铜外推（古典开瓶器）|
| gunmetal | 枪灰 (0.28,0.30,0.33) frame | 枪灰 spindle + 铬 worm | 枪灰 | 钢 | 枪灰外推 |
| antique_brass | 做旧黄铜 (0.66,0.52,0.30) frame | 做旧黄铜 wing | 木色 (0.45,0.30,0.16) handle | 钢 | 仿古黄铜 + 木把外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 mechanism / wing_geometry / handle / foil_crown 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（mechanism / wing_geometry / handle / foil_crown）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint 形成可变结构差异轴。
- **存在固定 N 的对称 / 阵列 part / visual（非可变轴，不进 slot_choice）**：
  - **两翼是固定一对 N=2**（最关键）：butterfly 开瓶器现实上**永远有且仅有两片对置翼**。fork 变体把 parent 手写两翼重构成 `for i in range(2)`（paddle L251 / curved L237 / lattice L256）+ `_build_<blade>(inner_sign=±1)` + 镜像轴 `wing_pivot_{i}`（axis=(0,±1,0)）+ 同一 motion_limits。`range(2)` 只是可读性 refactor，**N 由真实物体固定为 2，不是 multiplicity 轴 — 严禁参数化翼数**。
  - `t_bar_tip_{i}`：parent / direct_pull 用 `for i,sx in enumerate((-1,1))` 发射 2 个球端帽（parent L274），固定 N=2。
  - `rivet_pin_{i}` / `rivet_cap_{i}_{0/1}`：`for i,sx in enumerate((-1,1))` + 内 `for sy in (-1,1)` 发射 2 销 + 4 帽（parent L215-231），固定 N=2/4（随 mechanism=winged）。
  - 主轴齿环：`for z_ring in (0.0065,0.0125,0.0185)` 固定 3 环（parent L172），module-local 固定阵列。
  - foil cutter `blade_{i}`：`for i in range(BLADE_COUNT=3)` 发射 3 内向刀片（cutter L343），**BLADE_COUNT=3 是固定切箔刀片数**，随 rotating_cutter module 固定，不暴露为可变 count 轴。
  - angled_bar 两臂：`for sign in (-1,1)`（angled L218）；ball_knob 单球（N=1）。
- 这些都是 **module-local 固定多份 / 对称 visual / part**（两翼对、球端帽、铆钉、齿环、切箔刀片），按 module 而非 multiplicity 轴声明——clamp 不存在"任意 N 片翼 / N 个把手 / N 片刀"的真实产品域。copied object 用共享 helper 发射、绝对式对称 placement（±sign·offset 或角度均分），翼对带各自 REVOLUTE（mechanism=winged 提供），其余固定 visual 无独立 joint（Rule 1，inline 承载 part visual）。
- **N 样本 / N_range**：无 multiplicity 轴可 sweep（source map 明确：count_param 无）。

## 拓扑多样性审计

总组合数：
- **winged 分支**：mechanism=winged × wing_geometry(4) × handle(3) × foil_crown(2) = **24**。
- **direct_pull 分支**（无 wing_geometry）：mechanism=direct_pull × handle(3) × foil_crown(2) = **6**。
- 合计 **30** 个拓扑等价类（全部正交合法，唯一 gate = wing_geometry ⟂ direct_pull）。

仅 winged 的 wing_geometry(4) × handle(3) = **12 ≥ 10**（已达机械门控）。叠 foil_crown(2) → 24，再叠 direct_pull 分支(6) → 30，充裕。

理由：winged 分支 wing_geometry × handle 单独即 12 distinct（翼形 4 种 × 把手 3 种，slot_choice tuple 区分），foil_crown 提供真正的 joint 拓扑差异（plain 无 cutter / rotating_cutter +1 CONTINUOUS）→ ×2=24；mechanism 提供最大 joint 拓扑差异（winged：双 REVOLUTE 翼 + PRISMATIC + CONTINUOUS(+CONTINUOUS cutter) vs direct_pull：仅 PRISMATIC + CONTINUOUS(+CONTINUOUS cutter)，少两 REVOLUTE + 两 wing part + 多 bridge）→ direct_pull 6 distinct 与 winged 24 全异。总 30 distinct，远超 ≥10。`slot_choices_for_seed` tuple：`("mechanism", m)`、`("wing_geometry", m)`（仅 winged）、`("handle", m)`、`("foil_crown", m)`——direct_pull 时 wing_geometry 项**不出现**（slot 缺席自然区分 winged/direct_pull）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` mechanism；若 winged 再 `rng.choice` wing_geometry（direct_pull 跳过此 slot）；再 `rng.choice` handle、foil_crown；经兼容矩阵合法化（唯一 gate：direct_pull ⊥ wing_geometry）；再解析 conditional scale（wing_* 仅 winged、cutter_radius 仅 rotating_cutter、handle_span 随 handle）；再 uniform 各 independent scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看双翼摆起 + worm 旋入 + 主轴下行 + cutter 旋转 + direct_pull bridge）。


Controlled local parameterization：见 §参数表的 body_width_scale / body_height_scale / spindle_travel_scale / worm_radius_scale（independent）+ wing_len_scale / wing_open_scale（@winged）/ handle_span_scale（随 handle）/ cutter_radius_scale（@rotating_cutter）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 mechanism（解析是否有 wing_geometry slot）+ wing_geometry/handle/foil_crown（解析 conditional 范围：wing_* 仅 winged、cutter_radius 仅 rotating_cutter）→ 采 independent body/travel/worm scale → 派生（sleeve bore 随 worm_radius_scale、JOINT_TOP_Z/PIVOT_Z 随 body_height_scale）→ 用四条 inequality（过盈带、进给不超 bell、rest worm 悬空正、cutter-in-bell 过盈）投影 / 回缩。跨部件依赖（sleeve bore vs shaft、travel vs bell 深、cutter vs bell bore）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 shaft-in-sleeve / rivet-in-hub / collar-in-板槽 / cutter-in-bell captured 接口、wing/spindle/worm/cutter joint origin、rest 姿态或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` mechanism → 若 winged 再 wing_geometry → handle / foil_crown（经兼容矩阵）→ 解析 conditional scale → uniform independent scale → 采 palette_style | slot_choices_for_seed 含 `("mechanism",m)`/`("handle",m)`/`("foil_crown",m)`，winged 额外含 `("wing_geometry",m)`；与 build 一致 |
| compatibility matrix | **唯一硬 gate：wing_geometry ⟂ mechanism=direct_pull**——direct_pull 无翼，wing_geometry 候选与该分支互斥；sampler 在 direct_pull 时**不采样 wing_geometry slot**（不进 slot_choice、不发射翼 part / wing_pivot joint），且 body 改用 bridge 版 `_build_body_frame`（无铆钉 boss）。其余轴正交全合法：handle × foil_crown × mechanism 任意组合；conditional 解析：(1) wing_len/wing_open 仅 winged 生效；(2) cutter_radius 仅 rotating_cutter；(3) handle_span 随 handle（ball_knob 改缩 BALL_R）；(4) direct_pull + rotating_cutter 合法（cutter 在 bell bore，与无翼/bridge 不冲突）。 | 无 floating / collision / direct_pull 误发翼 / winged 缺翼 / cutter 戳出 bell / worm 戳桌 / 进给超 bell |
| controlled local variation | 4 independent + 4 conditional clamped scale，每 build 统一；conditional 随 mechanism/handle/foil_crown 解析 | 比例变化不破坏 shaft-in-sleeve/rivet-in-hub/collar-in-bell captured、wing/spindle/worm/cutter origin、rest 悬空、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（翼摆起 / worm 旋入 / 主轴下行 / cutter 旋转 / direct_pull bridge）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| mechanism | 2 | yes | no | winged（含两翼双 REVOLUTE）/ direct_pull（无翼 + bridge）；运动拓扑互斥主轴，2 candidate 是真实机构家族上限（降级理由见下）|
| wing_geometry | 4 | yes | yes | spade/paddle/curved/lattice（翼 mesh 维度，仅 winged）|
| handle | 3 | yes | yes | straight_t_bar / angled_bar / ball_knob（worm visual 无 joint）|
| foil_crown | 2 | yes | no | plain（空机构）/ rotating_cutter（+1 part+CONTINUOUS joint）；切箔冠真实形态上限，2 candidate（降级理由见 Slot C 注）|


## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("mechanism",m)`/`("handle",m)`/`("foil_crown",m)`；winged 时额外含 `("wing_geometry",m)`，direct_pull 时**不含** wing_geometry 项
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；wing_*/cutter_radius/handle_span 为 conditional 随 mechanism/foil_crown/handle 解析；四条 inequality（过盈带、进给不超 bell、rest worm 悬空、cutter-in-bell 过盈）在 resolve 内投影 / 回缩
- compatibility matrix gate：mechanism=direct_pull 时不采样 wing_geometry、不发射 wing part / wing_pivot joint、body 用 bridge 版；winged 时必发两翼 + 双 wing_pivot REVOLUTE
- 连续 scale clamp 后不破坏 shaft-in-sleeve / rivet-in-hub / collar-in-板槽 / cutter-in-bell captured 接口、wing/spindle/worm/cutter joint origin、rest 悬空、固定阵列 visual
- 关键 joint：`spindle_travel` PRISMATIC axis≈(0,0,−1)（abs(axis[2])>0.99，全候选共享）；`worm_spin` CONTINUOUS axis≈(0,0,+1)（无上下限，全候选共享）；mechanism=winged 时 `wing_pivot_0` REVOLUTE axis≈(0,+1,0) + `wing_pivot_1` REVOLUTE axis≈(0,−1,0)（镜像 ±Y，lower=0/upper≈1.745）；foil_crown=rotating_cutter 时 `cutter_spin` CONTINUOUS axis≈(0,0,+1)（无上下限）
- captured 过盈：element-scoped `allow_overlap`（`rack_sleeve`↔`frame_shell`；`rack_sleeve`↔`shaft_core`；winged：`rivet_pin_{i}`↔`wing_blade`/`paddle_blade`；rotating_cutter：`frame_shell`↔`cutter_collar`），照搬各样本 run_tests 的 allow_overlap 段
- 固定阵列 / 对称 visual 遵循 `wing_lever_{i}`/`wing_paddle_{i}`(N=2 固定对)/`t_bar_tip_{i}`/`rivet_pin_{i}`/`rivet_cap_{i}_{...}`/`blade_{i}`(N=3 固定) 命名 + 绝对式对称 placement + Rule 1（除两翼带 REVOLUTE 外，其余固定 visual 无独立 joint）
- direct_pull 断言无 wing part、无 wing_pivot joint（照搬 direct L253-264）；winged 断言两翼 REVOLUTE ~100° 镜像（照搬 parent L340-348）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把翼数当可变 multiplicity 轴（暴露 `wing_count`、采样 N 个翼）→ 违反真实物体（butterfly 永远 2 翼固定对）；两翼是 `for i in range(2)` 固定对，N 不可变（source map §Multiplicity 硬要求）。
- mechanism=direct_pull 仍发射翼 part / `wing_pivot` REVOLUTE → 违反 direct_pull"无翼"拓扑（direct run_tests L253-264 显式断言无 wing part/joint）；direct_pull 必须 gate 掉整个 wing_geometry slot + 改用 bridge 版 body。
- mechanism=winged 缺翼或缺 `wing_pivot` REVOLUTE → 出 winged 身份（butterfly 必有两片摆翼齿条）。
- 把把手（t_bar/bent/ball）当独立活动 part 加 joint → 违反 Rule 1（把手是 worm part visual，随 worm_spin CONTINUOUS 旋转，无独立 joint）。
- foil_cutter `blade_{i}` 数量当可变 N → BLADE_COUNT=3 是固定切箔刀片数（随 rotating_cutter module 固定），非 multiplicity 轴。
- worm_spin / cutter_spin 设成 REVOLUTE 带上下限而非 CONTINUOUS → 蜗杆 / 切箔冠需连续旋入旋转（全样本 CONTINUOUS 无上下限）。
- rest pose 把翼设成张开或主轴设成全下行而非 q=0 → current-pose 与 viewer 目检不符（所有样本翼下垂 q=0、worm 悬 bell 上方 hb[0][z]>0.004）。
- `spindle_travel` / `wing_pivot` / `worm_spin` / `cutter_spin` origin 放在任意点而非真实硬件（板顶 / 铆钉 boss / sleeve 帧 / bell bore）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 进给行程过大致 worm 脱出 bell 底或戳穿桌面 → §7 第二/三条 inequality FAIL；须按比例缩 travel / 抬 rest 位。
- sleeve bore 开得比 shaft 大（无过盈）致 shaft 漂浮 → shaft-in-sleeve 不接触，`expect_overlap`/`expect_within` FAIL；bore 须比 shaft 紧 embed≈0.0003。
- 给 captured 过盈接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 bottle opener（撬盖）/ waiter's-friend（折叠撬臂）/ 电动开瓶器语义混入 → 出类，本类是 helical-worm 进给的翼形 / 直拔开瓶器。

## 与相邻类别的边界

- 不该混入：**bottle opener / 啤酒撬盖起子**——杠杆撬瓶盖，无螺旋蜗杆、无 worm 旋入；本类 identity = helical worm + 旋入/起塞，缺 worm 即出类。
- 不该混入：**waiter's friend / 侍者刀（lever wine key）**——折叠刀身 + 单铰 worm + 双台阶 fulcrum 撬臂，主运动 spine 是折叠铰 + 撬动，不是本类竖直 PRISMATIC 进给 + 双翼/直拔（如需可作单独 slug）。
- 不该混入：**lever-arm / 电动开瓶器**——单根长压杆 + 自动旋入，机构家族不同（与本类双翼齿条 / 直拔 spine 不同）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **Slot A wing_geometry ⟂ mechanism=direct_pull** 的 gate 实现方式：direct_pull 时整个 wing_geometry slot 缺席（不进 slot_choice、不发翼 part/joint），是否接受作为唯一兼容硬约束；(2) 两翼为**固定对 N=2 非 multiplicity 轴**（`for i in range(2)`，严禁参数化翼数）是否符合期望；(3) mechanism 仅 2 candidate（winged / direct_pull）与 foil_crown 仅 2 candidate（plain / rotating_cutter）的降级理由（真实机构 / 切箔冠形态上限）是否接受还是要求回 fork 池补造；(4) Topology target 30<300 的说明是否接受（本小类真实结构上限）；(5) palette_style 5 套（chrome_black 默认 + all_chrome/brass_black/gunmetal/antique_brass，后四套为样本配色外推）是否合适；(6) winged 与 direct_pull 共享主轴/蜗杆/bell（仅 ±两翼 ±bridge）的 parallel_children 单模板装配是否接受，还是按机构家族拆 slug。)|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **共享 helper**：`_build_body_frame`（按 mechanism 切：winged 含铆钉 boss / direct_pull 加顶 bridge + shaft bore，bell+双板+支腿共享）、`_build_rack_sleeve`（齿环堆 + guide collar + bore，全候选共享）、`_build_worm`（helical sweep，全候选共享）、`_build_wing`/`_build_paddle_wing`/`_build_aero_blade`/`_build_wing`+PERF（按 wing_geometry 切翼 mesh，仅 winged）、`_build_bent_tbar`/`_build_ball_knob`/直 t_bar+tip（按 handle 切把手）、`_build_foil_cutter_collar`/`_build_cutter_blade`（仅 rotating_cutter）。两翼用 `for i in range(2)` + `_build_<blade>(inner_sign=±1)` + 镜像轴 `wing_pivot_{i}`（采纳 paddle/curved/lattice 已 refactor 的循环，parent 手写两翼亦等价）。
- captured 接口 allow_overlap：`run_corkscrew_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L468-545：rivet/guide/shaft；cutter L642-666：collar-in-bell；direct L355-401：guide/shaft，无 rivet）。
- conditional 范围解析顺序：先采 mechanism → 解析是否有 wing_geometry slot（winged 才采）→ 采 handle / foil_crown → 解析 wing_len/wing_open（仅 winged）/ cutter_radius（仅 rotating_cutter）/ handle_span（随 handle）→ 采 independent body/travel/worm scale → 派生 sleeve bore（随 worm_radius_scale）+ JOINT_TOP_Z/PIVOT_Z（随 body_height_scale）→ 投影四条 inequality。
- 关键尺度小（body ~0.05m 宽、T-bar 顶 ~0.17m 高、主轴行程 ~0.038m）：joint origin 须精确落真实硬件面（≤0.015m baseline）；worm 用 `cq.Wire.makeHelix` sweep（全样本统一），注意 helix sweep 稳定性。
- ball_knob 把手把 part 改名 `ball_knob_worm`（源 L275）：模板侧建议统一 part 名为 `t_handle_worm`（把手只换 visual），避免 part-name 随 handle 变动破坏 slot_choice / 测试 get_part；若保留改名须在测试按 handle 取对应 part 名。
- 参考模板：选运动拓扑相近的——`agent/templates/Handtools_Clamp.py`（同为 screw-driven hand tool：root frame + PRISMATIC screw + 可选 REVOLUTE pad/lever 并列挂 frame + captured screw-in-boss 过盈 + 三轴正交 + palette_style + conditional scale；corkscrew 的 body→spindle PRISMATIC + spindle→worm CONTINUOUS + 可选 wing/cutter 与之同构，唯一新增是 mechanism gate 掉整个 Slot A）；cushion 的 root chassis + 互斥机构 slot + captured-pin allow_overlap 骨架亦可参考。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | D / A / B / C（parent 基线）| winged + spade + straight_t_bar + plain | rec_model-a-classic-winged-butterfly-corkscrew-about_...65a27fb6 | `_build_body_frame` L80-116 / 铆钉 L215-231 / `_build_wing`(spade) L119-166 / 两翼 L234-245 / `_build_rack_sleeve` L169-184 / `_build_worm` L187-197 / t_bar+tip L268-280 / `wing_pivot_{i}` REVOLUTE L284-302 / `spindle_travel` PRISMATIC L304-312 / `worm_spin` CONTINUOUS L314-322 / allow_overlap L468-545 | winged 基线运动 spine（PRISMATIC+CONTINUOUS+双 REVOLUTE 翼）+ spade 翼 + 直 T-bar + 无冠 + 全套 captured 范式 |
| S2 | A | paddle | rec_corkscrew_var_wing_paddle | `_build_paddle_wing` L121-181 / `for i in range(2)` 翼 `wing_paddle_{i}` + 镜像轴 L251-276 / allow_overlap L507-535 | 宽桨翼 mesh + 两翼 `for i in range(2)` 循环 copy-logic 源 |
| S3 | A | curved | rec_corkscrew_var_wing_curved | `_build_aero_blade`(3 段椭圆 loft) L119-165 / `for i in range(2)` 翼 `wing_lever_{i}` L237-258 | 雕塑弯刀翼 mesh（真 3D loft）+ 循环翼 |
| S4 | A | lattice | rec_corkscrew_var_wing_lattice | `PERF_ROWS` 常量 L55-62 / `_build_wing`+穿孔 cut 循环 L130-187 / `for i in range(2)` 翼 L256-264 | 镂空 lattice 翼 mesh（spade + 6 行交错通孔）+ 循环翼 |
| S5 | B | angled_bar | rec_corkscrew_var_handle_angled_bar | `_build_bent_tbar`(boss+两臂上倾 30°+球尖, `for sign in (-1,1)`) L200-234 / `t_bar` visual L305-309 | V 形上折 T-bar 把手（worm visual 无 joint）|
| S6 | B | ball_knob | rec_corkscrew_var_handle_ball_knob | `_build_ball_knob`(sphere R≈0.0105+neck) L200-216 / part 改名 `ball_knob_worm` L275 / `ball_knob` visual L288-292 | 单球握把（worm visual 无 joint，part 改名注记见 §13）|
| S7 | C | rotating_cutter | rec_corkscrew_var_crown_rotating_cutter | CUTTER/BLADE 常量 L205-217 / `_build_foil_cutter_collar` L220-235 / `_build_cutter_blade` L238-250 / `foil_cutter` part + `for i in range(BLADE_COUNT=3)` blade L337-350 / `cutter_spin` CONTINUOUS L396-404 / allow_overlap(frame_shell↔cutter_collar) L642-666 | 旋转切箔冠（+1 part + CONTINUOUS joint，bell bore press-fit）|
| S8 | D | direct_pull | rec_corkscrew_var_mech_direct_pull | `_build_body_frame`+bridge+shaft bore L76-134 / 无翼 part / 仅 `spindle_travel` PRISMATIC L220-228 + `worm_spin` CONTINUOUS L230-238 / 断言无 wing part/joint L253-264 / allow_overlap L355-401 | 无翼直拔机构（body 加 bridge，gate 掉 Slot A）|
