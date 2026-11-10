# blacksmith_tongs (forged articulated blacksmith tongs) — Modular Spec

> 来源小类：`picture/Others/blacksmith tongs`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Others__Others_blacksmith_tongs.md`。
> **"blacksmith tongs" 在此 = 锻造钢制铰接钳夹（forged articulated tongs）：两条锻钢臂在一块扁椭圆 boss 上交叠（half-lap），由一根圆头 rivet 铆接到一起 → 恰好 ONE REVOLUTE pivot（轴 ⟂ 工具平面）。捏合 reins/handles 即闭合 jaws。每条臂 = jaw(工作端) + boss(交叠铰接板) + rein/handle(长把端) + rivet。**不是剪刀(scissors)、不是钳子/老虎钳/扳手(pliers/wrench)、不是木上菜夹(wooden serving tongs)、不是螺杆台钳(clamp/vise)。**
> 结构家族 = 两条对称锻钢臂 + 一根把两臂铆到一起的 rivet。**核心运动 = `rivet_pivot` REVOLUTE：两臂绕 rivet 轴(⟂ 工具平面)相对转动，q=0 是松弛闭合的"jaws 几乎相碰、reins 略张"的休息姿态，upper(≈0.3 rad)是 jaws 张开 / reins 进一步外撇。**
>
> **同步状态**：本 spec 引用的 11 个 5 星样本（3 parent + 8 个单轴 fork 变体）**已同步进本仓库 `data/records/<id>/`，rating=5、workbench-only（两边都不进 dataset）**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行读完整、核对）。引用以 part / joint / helper **名字** 为准（`fixed_arm`/`moving_arm`(wolf-jaw 族) 或 `rear_arm`/`front_arm`(bow-ring / pincers) part；`rivet_pivot` / `boss_rivet_pivot` REVOLUTE joint；`_jaw_solid`/`_boss_solid`/`_rein_solid`/`_rivet_solid`/`_place`(wolf-jaw 族)、`_ring_half`/`_jaw_tip`/`_boss_plate`/`_rein`/`_rivet_shank`(bow-ring)、`_jaw`/`_bite_edge`/`_neck`/`_handle`/`_handle_tip`/`_dome`(pincers) helper；`jaw`/`boss`/`rein`/`rivet`(wolf-jaw 族) 或 `ring_jaw`/`jaw_tip`/`boss_plate`/`rein`/`rivet_*`(bow-ring) 或 `jaw`/`bite_edge`/`neck`/`boss_plate`/`handle`/`handle_tip`/`rivet_dome`(pincers) visual），行号仅作定位。
>
> **坐标约定（模板统一沿用 wolf-jaw parent 与全部 8 变体的约定——这是 fork baseline，11 样本里 9 个直接用它）**：工具躺在 **XY 平面**（扁臂法线 = Z），jaw 沿 **+X** 从 boss(x≈0) 伸出到 jaw tip(x≈0.086)，rein 沿 **−X** 伸到 tip(x≈−0.462)；两臂在 boss 处沿 **±Z** 堆叠（half-lap，fixed 半在 +Z 半叠、moving 是同一锻件绕 X 轴翻转 180° → jaw/rein 换边、lap 面相对）；`rivet_pivot` REVOLUTE **axis=(0,0,−1)**（⟂ XY 工具平面），origin 在 boss 中心堆叠面 `(0,0,Z_LIFT)`，**lower=0 / upper=0.3**（q=0 闭合休息、upper jaws 张开 + moving rein 外撇）。**两个 XZ-plane parent（bow-ring axis=(0,1,0)、pincers axis=(0,1,0)）的几何在模板侧 rebase 到这套 XY 约定**（jaw 在 +X / rein 在 −X / 臂沿 ±Z 堆叠 / pivot axis=(0,0,−1)），保留其 jaw 形态(half-ring / claw-bite)与 short_stout_handle 形态，详见 §13。

## 元信息
| 项 | 值 |
|---|---|
| slug | `blacksmith_tongs` |
| template path | `agent/templates/Others_blacksmith_tongs.py` |
| test path (optional) | `tests/agent/test_blacksmith_tongs_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定根臂 `fixed_arm`；`moving_arm` 经单个 `rivet_pivot` REVOLUTE 挂根臂；jaw_shape / rein_form / boss_rivet 三个 slot 只改写两臂的 jaw/rein mesh + boss/rivet 细节 visual，**arm 数恒为 2 经共享 `_place(flipped=)` / enumerate-arms helper 发射，非 multiplicity 轴**；rivet 是唯一 captured pivot pin）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（3 parent + 8 个单轴 fork 变体；均 converged、compile success、≥1 非 fixed joint(`rivet_pivot` REVOLUTE)、workbench-only，rating=5）|
| read_count | 11（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 11/11 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 11 个样本）**：两条对称锻钢臂（jaw + boss + rein/handle）在 boss 处 half-lap 交叠 + 一根 rivet 铆接 → 单个 `rivet_pivot` REVOLUTE（轴 ⟂ 工具平面）。q=0 jaws 几乎相碰(闭合休息)，upper(0.3–0.4 rad) jaws 张开 + reins 外撇。所有样本 `run_tests` 都验同一套核心：rivet 居中于 boss footprint（`expect_within(rivet, boss)`）、rivet 头露出 boss 两面（proud）、boss 是扁椭圆/圆盘 ~0.035–0.045m across、jaws 闭合时近接(`expect_gap` min 小)、jaws 沿臂向 side-by-side(`expect_overlap` x)、reins 长且双侧外撇、upper pose jaws 张开 + moving rein 外撇 +0.05–0.08m。
- **Slot A jaw_shape 轴（defining axis — closed jaws 抓什么；`jaw`/`ring_jaw`/`bite_edge` visual + `_jaw_solid` 族）**：是 jaw 工作端 **mesh-profile / 闭合接触语义** 变化（改写 jaw mesh + 闭合 gap 断言，**不改 part / joint 拓扑**——两臂仍各一 part + 单 `rivet_pivot` REVOLUTE）。
  - `wolf_flat_jaw`（baseline）：`_jaw_solid()` 扁 polyline `JAW_PTS` 收口成窄 V-notch + 横向 `GROOVES`（短扁 wolf 钳口，内面在中线收成窄 V 抓 bar）。
  - `ring_bow_jaw`（bow-ring parent）：`_ring_half()` 扁条半椭圆环 + `_jaw_tip()` 顶端 lap 小平片——两臂闭合时两半环合成一个大开口 oval bow loop（caliper 状）。
  - `pincer_claw_jaw`（pincers parent）：`_jaw()` 厚 spline claw 向内勾 + `_bite_edge()` 顶端硬化窄咬边 + `_neck()` web 把 jaw 接到 boss——nipper/end-cutter 形，闭合时 bite edges 近接、jaw 背留可见 throat。
  - `flat_box_jaw`：改写 `_jaw_solid()` 用 `JAW_BOX_PTS` 矩形——平行平面 box/pickup 钳口，夹平板（flat face、无 V-notch）。
  - `vgroove_jaw`：`_jaw_solid()` + `_vgroove_cutter()` 在内面 loft 三角 V-channel——深纵向 V 沟，两 jaw 闭合成 diamond socket 抓圆 bar 轴向。
  - `hollow_bit_jaw`：`_bit_jaw_solid()` + `_bore_cutter()` 沿 X 挖半圆柱 bore——opposed 凹半圆柱 bits 闭合成圆 bore 托 rod/pipe（JAW_T 加厚到 0.011 容纳 bore；用 enumerate-arms 循环——model copy-logic 范例）。
- **Slot B rein_form 轴（手握的长把端；`rein`/`handle` visual + `_rein_solid` 族）**：是 rein/handle **截面 / 端头形态 / 把长** 变化（改写 rein mesh + rein-tip 断言，不改 part / joint 拓扑，两臂仍各一 part + 1 REVOLUTE）。
  - `long_straight_rein`（baseline）：`_rein_solid()` 经 `REIN_SECTIONS` superellipse loft（pivot 处方截面 → tip 圆截面 taper，微外 bow，圆头 tip）——很长直 rein。
  - `scrolled_rein_ends`：`_rein_solid()` + `_scroll_solid()` 末段卷回扁锻 scroll/volute（装饰 fireplace-tong 形，flat spiral 躺工具平面）。
  - `looped_eye_reins`：`_rein_solid()` + `_eye_loop_solid()` 末端弯成带真 bore 的闭合 eye/ring（挂钩用，torus revolve + blend 球）。
  - `square_bar_reins`：`_rein_solid()` 用 `REIN_STATIONS` + 恒定方截面 `REIN_BAR_HALF`（chunky 全程方 bar，crisp edges，无 round-tip taper）。
  - `short_stout_handle`（secondary，pincers parent 跨槽备选）：`_handle()` lofted 圆角矩形 `HANDLE_SECTIONS` 短粗外 bow 把手 + `_handle_tip()` 圆 worn 端球（短粗 handle 代替长 rein）。
- **Slot C boss_rivet 轴（两臂如何 lap + pin；`boss`+`rivet` visual + `_boss_solid`/`_rivet_solid` 族）**：是 boss 板 / rivet 头 **pivot 细节** 变化（改写 boss/rivet mesh + boss/rivet 断言，不改 part / joint 拓扑——rivet 仍是唯一 captured pivot pin、单 REVOLUTE）。
  - `flat_boss_domed_rivet`（baseline）：`_boss_solid()` half-lapped 扁椭圆 + `LAP_R` lap cut；`_rivet_solid()` 圆柱 shaft + 两个 domed sphere 头（round-head rivet proud on both faces）。
  - `countersunk_flush_rivet`：`_rivet_solid()` 锥头 revolve + `_boss_solid()` 加 `_countersink_cutter()` 锥孔——rivet 两端 peened flush 进锥形 countersink，pivot 齐平 boss 面。
  - `raised_boss_collar`：`_boss_solid()` 在 boss 外面 union 一段 inline 凸圆柱 collar/hub（带 bore），`_rivet_solid()` shaft + head 抬高到 collar 外面坐——turned 圆柱 collar/washer ring 把 rivet 头抬在 stepped boss 上（用 enumerate-arms 循环，Z_LIFT 加大到 0.014 容纳 collar）。

## 核心身份

一把**锻造钢制铰接钳夹**（forged articulated blacksmith tongs）：两条对称锻钢**臂**，每条由一根 bar 锻成—— jaw(工作端) + boss(扁椭圆 half-lap 铰接板) + rein/handle(很长的把端)；两臂在 boss 处 half-lap 交叠、由一根圆头 **rivet** 铆到一起，构成**恰好一个** `rivet_pivot` REVOLUTE（轴 ⟂ 工具平面）。捏合两 reins/handles 使两臂绕 rivet 相对转动、把两 jaws 合到一起夹热铁。jaw 工作端有六种形态：扁 wolf V-notch / 半环 bow loop / 厚 claw bite-edge / 平 box pickup / 纵 V-groove / 凹半圆柱 bore。rein 长把有四种主形态（直 taper / scroll 卷 / eye 环 / 方 bar）+ 一个跨 parent 的短粗 handle 备选。boss/rivet pivot 细节有三种（扁 boss + domed rivet / countersunk flush rivet / raised collar boss）。默认成熟域：jaw_shape(6) × rein_form(4) × boss_rivet(3) 的笛卡尔积 = 72。活动语义 = **两臂绕 rivet 轴(⟂ 工具平面)相对转动开合**（核心且唯一的非 fixed joint：`rivet_pivot` REVOLUTE，全候选共享）。jaw/boss/rein 都是 **FIXED-into-arm 的 parent visual（装饰几何 inline 进同一 Part，不作独立 FIXED part，Rule 1）**；rivet 是 captured pivot pin（fixed 臂的 visual，穿过 moving 臂 boss，由 element-scoped `allow_overlap` 守）。

不该混入（详见 §11）：
- **剪刀（scissors）**——两片刃绕中心 pivot 剪切片状物、刃成对称剪式、把手是闭环 finger loops；本类是夹持(grip)热铁的 tongs，jaws 不剪切、reins 是开放长把不是 finger loops。
- **钳子 / 老虎钳 / 扳手（pliers / wrench）**——pliers 是中段交叉 box-joint 的金属切/夹小工具(尺寸 ~0.15m、把手成对短)、wrench 多为单体或棘轮无开合 jaws；本类是 ~0.55m 长锻钢 boss-lap rivet tongs，jaw 在 boss 一侧、长 rein 在另一侧，非中段交叉的对称剪式。
- **木上菜 / 厨房夹（wooden serving tongs，已有独立 slug `wooden_tongs`）**——木质一体弹性夹(spring clip / scissor pin / 弯木)、palette 是木、~0.30m；本类是**锻钢** boss-lap rivet tongs，palette 全是 forged steel、~0.55m、有真 rivet 铆点。
- **螺杆台钳 / C 形夹（clamp / vise，已有独立 slug `clamp`）**——螺杆竖直 PRISMATIC 进给 + C 形 frame；本类主运动是绕 rivet 的单 REVOLUTE 开合，无螺杆无 frame。

## 槽位 + 候选模块表

> **建模注记**：三个 slot 都是**两臂同一对 mesh / 装饰 visual 的形态维度**，**都不改 part 树 / joint 拓扑**（两臂恒各一 Part + 单 `rivet_pivot` REVOLUTE，rivet 恒为唯一 captured pivot pin）。`jaw_shape`(Slot A) 改写 jaw mesh helper + 闭合接触语义（V-notch / ring loop / claw-bite / flat box / V-groove / 凹 bore）——这是**主 defining 轴**(满配 6 候选)。`rein_form`(Slot B) 改写 rein mesh helper + rein-tip 形态（直 taper / scroll / eye / 方 bar / 短粗 handle）。`boss_rivet`(Slot C) 改写 boss/rivet 细节 visual（扁 boss+domed / countersunk flush / raised collar）。三轴正交，共同撑开 6×4×3=72 组合（见 §9）。每个 slot 内候选**互斥单选**（一次一种 jaw / 一种 rein / 一种 boss-rivet）。

### Slot A：jaw_shape（jaw / working end —— **主机构槽 = defining 轴**，决定 closed jaws 抓什么 + jaw mesh / 闭合接触语义）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| wolf_flat_jaw（baseline）| rec_model-...wolf-jaw...af04e104（parent）| `_jaw_solid()` L114-130（`JAW_PTS` L58-66 + `GROOVES` L71-75）；`jaw` visual L188-192/210-214 | eligible if compatible | 短扁 wolf 钳口：`_jaw_solid` 扁 polyline 内面收成窄 V-notch tip + 横向 `GROOVES` 沟；两 jaw 闭合成窄 V 抓 bar；run_tests 验闭合 `expect_gap(jaw,jaw,y,0.0005-0.004)` + `expect_overlap(jaw,jaw,x,>0.05)`(L259-277) |
| ring_bow_jaw | rec_model-...bow-ring-jaw...12053487（parent）| `_ring_half()` L79-97 + `_jaw_tip()` L100-111；`ring_jaw`/`jaw_tip` visual L188-197/234-243 | eligible if compatible | 半环 bow loop：每臂顶端是扁条半椭圆环（`_ring_half` outer-inner ellipse cut）+ 顶端 lap 小平片（`_jaw_tip`）；两臂闭合两半环合成 ~0.09×0.12m 大开口 oval ring（caliper 状）；run_tests 验 `jaw_tip` lap `expect_overlap(xz)` + ring 尺寸(L281-326)；**模板侧 rebase 到 XY 约定**(见 §13) |
| pincer_claw_jaw | rec_model-...pincers...9dcb992b（parent）| `_jaw()` L89-125 + `_bite_edge()` L128-142 + `_neck()` L145-159；`jaw`/`bite_edge`/`neck` visual L248-262/305-319 | eligible if compatible | 厚 claw nipper：`_jaw` 厚 spline claw 向内勾、`_bite_edge` 顶端硬化窄咬边、`_neck` web 接 boss；闭合 bite edges 近接(`expect_gap 0.0005-0.003`)、jaw 背留 throat(`expect_gap 0.002-0.007`)(L362-382)；**模板侧 rebase 到 XY 约定**(见 §13) |
| flat_box_jaw | rec_blacksmith_tongs_var_flat_box_jaw | `_jaw_solid()` L110-120（`JAW_BOX_PTS` L66-71）| eligible if compatible | 平 box/pickup：改写 `_jaw_solid` 用矩形 `JAW_BOX_PTS`——平行内/外平面 box 钳口夹平板（flat face、无 V-notch）；run_tests 验平行面(jaw_width_y 0.010-0.018 恒定)(L270-286) |
| vgroove_jaw | rec_blacksmith_tongs_var_vgroove_jaw | `_jaw_solid()` L150-159 + `_vgroove_cutter()` L124-147（`V_GROOVE_STATIONS` L78-85）| eligible if compatible | 纵 V-groove：`_jaw_solid` + `_vgroove_cutter` 沿内面 loft 三角 V-channel；两 jaw 闭合成 diamond socket 抓圆 bar 轴向；run_tests 验闭合 `expect_gap(-0.001-0.005)` + V 在 Y 面(jaw Z-extent==JAW_T)(L379-383) |
| hollow_bit_jaw | rec_blacksmith_tongs_var_hollow_bit_jaw | `_bit_jaw_solid()` L130-148 + `_bore_cutter()` L119-127（`BIT_JAW_PTS` L72-80）；enumerate-arms 循环 L210-251 | eligible if compatible | 凹半圆柱 bore：`_bit_jaw_solid` + `_bore_cutter` 沿 X 挖半圆柱（JAW_T 加厚到 0.011 容纳 `BORE_R=0.005`）；两 bits 闭合成圆 bore 托 rod/pipe；run_tests 验 bore 含于 jaw 厚(jaw_z>2·BORE_R)(L313-328)；**enumerate-arms 循环范例**(`for i,(arm_name,flipped) in enumerate(arms)`) |

### Slot B：rein_form（rein / handle 长把端 —— mesh-profile / 端头形态 / 把长维度，不改 part / joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| long_straight_rein（baseline）| rec_model-...wolf-jaw...af04e104（parent）| `_rein_solid()` L140-155（`REIN_SECTIONS` L87-94）；`rein` visual L198-202/220-224 | eligible if compatible | 很长直 rein：`_rein_solid` 经 `REIN_SECTIONS` superellipse loft（pivot 处方截面 → tip 圆截面 taper，微外 bow，圆头 tip，~0.45m）；run_tests 验 rein 长(0.40-0.50) + tips 双侧外撇(L329-341) |
| scrolled_rein_ends | rec_blacksmith_tongs_var_scrolled_reins | `_rein_solid()` L219-234 + `_scroll_solid()` L149-216（`SCROLL_*` L98-104）| eligible if compatible | 卷 scroll/volute：`_rein_solid` 末段 union `_scroll_solid`（flat spiral volute 躺工具平面，`SCROLL_TURNS=1.5`，loft 圆截面沿 spiral）；装饰 fireplace-tong 形；run_tests 验 scroll 超出 splay(rein min_y<−0.045) + 躺平(z<0.025)(L428-455) |
| looped_eye_reins | rec_blacksmith_tongs_var_looped_eye_reins | `_rein_solid()` L176-191 + `_eye_loop_solid()` L144-173（`EYE_LOOP_R`/`EYE_TUBE_R` L52-54）| eligible if compatible | 闭合 eye 环：`_rein_solid` 末端 union `_eye_loop_solid`（torus revolve `EYE_LOOP_R=0.011` 偏 −X + blend 球，带真 bore 挂钩用）；run_tests 验 eye 超出 tip(min_x<TIP_X−0.008) + Y 超 plain tip(L379-406) |
| square_bar_reins | rec_blacksmith_tongs_var_square_bar_reins | `_rein_solid()` L140-155（`REIN_STATIONS` L88-95 + `REIN_BAR_HALF` L51）| eligible if compatible | 恒定方 bar：`_rein_solid` 沿 `REIN_STATIONS` loft 恒定方截面（`REIN_BAR_HALF=0.0065`，全程 chunky 方 bar，crisp 4-corner edges，无 round-tip taper） |
| short_stout_handle（secondary）| rec_model-...pincers...9dcb992b（parent）| `_handle()` L181-194 + `_handle_tip()` L197-204（`HANDLE_SECTIONS` L74-80）| eligible if compatible（secondary B 形，模板可选纳入；标 secondary 因来自 pincers parent、需 rebase + 短把语义）| 短粗 handle：`_handle` lofted 圆角矩形 `HANDLE_SECTIONS` 短粗外 bow 把手(~0.22m，比 rein 短) + `_handle_tip` 圆 worn 端球；run_tests 验把外 bow + 端球(L473-500)；**模板侧 rebase 到 XY 约定 + 短把长**(见 §13) |

### Slot C：boss_rivet（boss / rivet pivot 细节 —— pivot mesh 维度，不改 part / joint 拓扑；rivet 恒为唯一 captured pivot pin）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_boss_domed_rivet（baseline）| rec_model-...wolf-jaw...af04e104（parent）| `_boss_solid()` L133-137 + `_rivet_solid()` L158-167（`LAP_R` L46、`RIVET_HEAD_R` L53）| eligible if compatible | 扁 boss + domed rivet：`_boss_solid` half-lapped 扁椭圆(`BOSS_A/B`)+`LAP_R` lap cut；`_rivet_solid` 圆柱 shaft + 两 domed sphere 头(`RIVET_HEAD_R=0.006`，proud on both faces)；run_tests 验 rivet 头 proud 上/下 boss 面(L292-301) |
| countersunk_flush_rivet | rec_blacksmith_tongs_var_countersunk_rivet | `_rivet_solid()` L182-204 + `_countersink_cutter()` L111-128 + `_boss_solid()` L155-161（`FLUSH_HEAD_R`/`HEAD_DEPTH` L54-55）| eligible if compatible | 齐平 countersunk：`_boss_solid` 加 `_countersink_cutter` 锥孔；`_rivet_solid` 锥头 revolve（`FLUSH_HEAD_R=0.007`/`HEAD_DEPTH=0.002`）两端 peened flush 进锥 countersink，pivot 齐平 boss 面；**模板侧需把 rivet 头 proud 断言换成 flush 断言** |
| raised_boss_collar | rec_blacksmith_tongs_var_raised_boss_collar | `_boss_solid()` L139-153（inline collar L144-153，`COLLAR_*` L56-59）+ `_rivet_solid()` L174-186；enumerate-arms 循环 L217-245 | eligible if compatible | 抬高 collar：`_boss_solid` 在 boss 外面 union inline 凸圆柱 collar/hub（`COLLAR_R=0.009`/`COLLAR_H=0.003` + bore）；`_rivet_solid` shaft+head 抬到 collar 外面坐（`RIVET_HEAD_Z=BOSS_PLATE_T+COLLAR_H`，Z_LIFT 加大到 0.014）；run_tests 验 boss z-extent>0.006 + 两 collar 对称(L336-355)；**enumerate-arms 循环范例** |

## 槽位图（slot graph）

pattern: parallel_children（固定根臂 `fixed_arm`(jaw+boss+rein+rivet 整条锻件)；`moving_arm`(同一锻件翻转 180°) 经单个 `rivet_pivot` REVOLUTE 挂根臂；jaw_shape 换两臂 jaw mesh helper、rein_form 换两臂 rein/handle mesh helper、boss_rivet 换两臂 boss/rivet 细节 visual——三 slot 都是改写两臂同一对 mesh / 装饰，不增 part / joint）

```
fixed_arm (root, 坐 boss/pivot 端; 整条锻件 = jaw + boss + rein + rivet)
  │   visual: jaw (由 jaw_shape 决定) + boss (由 boss_rivet 决定) + rein (由 rein_form 决定) + rivet (由 boss_rivet 决定, captured pivot pin)
  │
  └── moving_arm (child, 整条锻件 = jaw + boss + rein, 同一锻件绕 X 翻转 180° → jaw/rein 换边、lap 面相对)
         └──[rivet_pivot: REVOLUTE axis=(0,0,−1), origin=(0,0,Z_LIFT) boss 中心堆叠面, lower=0 / upper=0.3]  ← 全候选共享的唯一非 fixed joint
            （q=0 jaws 闭合休息(jaws 几乎相碰)、upper jaws 张开 + moving rein 外撇；两臂 ±Z half-lap 堆叠）

[jaw_shape slot 换两臂 jaw mesh helper]  (六选一互斥)
  └─ wolf_flat_jaw(_jaw_solid V-notch) / ring_bow_jaw(_ring_half+_jaw_tip 半环) / pincer_claw_jaw(_jaw+_bite_edge+_neck 厚 claw)
     / flat_box_jaw(_jaw_solid 矩形) / vgroove_jaw(_jaw_solid+_vgroove_cutter) / hollow_bit_jaw(_bit_jaw_solid+_bore_cutter 凹 bore)

[rein_form slot 换两臂 rein/handle mesh helper]  (四选一互斥 + short_stout_handle 可选 secondary)
  └─ long_straight_rein(_rein_solid taper) / scrolled_rein_ends(+_scroll_solid) / looped_eye_reins(+_eye_loop_solid)
     / square_bar_reins(_rein_solid 方 bar) / [short_stout_handle(_handle+_handle_tip 短粗)]

[boss_rivet slot 换两臂 boss/rivet 细节 visual]  (三选一互斥)
  └─ flat_boss_domed_rivet(_boss_solid+_rivet_solid domed) / countersunk_flush_rivet(+_countersink_cutter 锥头 flush)
     / raised_boss_collar(_boss_solid inline collar + rivet 抬高)
```

接口点位与 joint 语义：
- **fixed_arm → moving_arm（rivet_pivot，全候选共享、唯一非 fixed joint）**：mating = 两臂在 boss 处的 half-lap 堆叠接触面（lap plane）+ 穿过两 boss 的 rivet。REVOLUTE **axis=(0,0,−1)**（⟂ XY 工具平面），origin=`(0,0,Z_LIFT)` boss 中心堆叠面（rivet 轴线所在），lower=0 / upper=0.3（q=0 jaws 闭合休息、upper jaws 张开 + moving rein 外撇）。两臂 boss footprint `expect_within(rivet, boss, xy)`（rivet 居中于 boss）。
- **boss/rivet → 根臂（boss_rivet slot 决定，captured / inline）**：
  - rivet 作 **fixed 臂的 visual（captured pivot pin）**，穿过 moving 臂 boss——element-scoped `allow_overlap(fixed_arm, moving_arm, elem_a="rivet", elem_b="boss")`（所有 11 样本 run_tests 都有这条，照搬）。rivet 头 proud(domed/collar) 或 flush(countersunk) 由 boss_rivet 候选决定。
  - boss half-lap = 两臂 boss 板在 lap plane 面对面堆叠（`LAP_R` lap cut + `LAP_EPS` 微 z 间隙），是各臂 visual。raised_boss_collar 的 collar 是 boss visual inline union（无独立 joint，Rule 1）。
- **jaw → 根臂（jaw_shape slot 决定）**：jaw mesh 作各臂 visual（hollow_bit / claw 等改写 jaw helper）。jaw 闭合接触（V-notch 近接 / ring lap / bite edge 近接 / 平面 gap / V diamond / 圆 bore）是 captured / bridging 接触，由各样本 run_tests 的 `expect_gap`/`expect_overlap` 守（照搬各 jaw 候选断言）。pincer 的 `neck` web、bite_edge 是同臂 visual（无独立 joint，Rule 1）。
- **rein/handle → 根臂（rein_form slot 决定）**：rein mesh 作各臂 visual。scroll / eye 是 rein 末段 union 进同一 rein mesh（不是独立 part，Rule 1）；short_stout_handle 的 handle_tip 球是同臂 visual。
- **mating policy**：所有连接接口（rivet 穿 boss、boss half-lap、jaw 闭合近接）是 **captured / bridging / lap 堆叠**（rivet 嵌入两 boss、jaw lap 接触），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 rivet_pivot origin（落在 boss 中心 rivet 轴线）+ element-scoped `allow_overlap(rivet, boss)` 守 captured overlap（照搬各样本 run_tests）。
- **rest pose**：`rivet_pivot` q=0（jaws 闭合休息、jaws 几乎相碰、reins 略张）。
- **互斥 / 可选 / 派生**：jaw_shape 六候选**互斥单选**（一次一种 jaw）；rein_form 四主候选**互斥单选**（+ short_stout_handle 可选 secondary，与四主候选同槽互斥）；boss_rivet 三候选**互斥单选**。三轴正交（任意 6×4×3=72 组合合法，仅 raised_boss_collar × pincer_claw_jaw 一组接口间隙需 conditional 重算，见 §9）。无 multiplicity 轴——臂数恒为 2、rivet 恒为 1。

## 每槽位 Module Emits / Interfaces

### Slot A / jaw_shape — wolf_flat_jaw（baseline，其余 jaw 候选仅换 jaw mesh helper，两臂共用）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（jaw mesh 作两臂 `jaw` visual，inline 进 fixed_arm/moving_arm Part）| af04e104 `_jaw_solid` L114-130 / visual L188-192,210-214 |
| internal joints | 无（jaw_shape 不改 joint；唯一 joint 是 boss_rivet 处的 `rivet_pivot`）| — |
| upstream interface | jaw 根接到 boss（同臂 mesh，half-lap 处）；hollow_bit/claw 等改写 jaw helper（claw 另有 `neck` web visual 接 boss）| 各 jaw 候选表 |
| downstream interface | 两 jaw 闭合接触（V-notch/ring lap/bite/平面/V/bore），由各候选 run_tests 的 `expect_gap`/`expect_overlap` 守（照搬）| af04e104 L259-277 |

### Slot B / rein_form — long_straight_rein（baseline，其余 rein 候选仅换 rein mesh helper，两臂共用）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（rein/handle mesh 作两臂 `rein` visual，inline 进 Part；scroll/eye 是 rein 末段 union 同 mesh）| af04e104 `_rein_solid` L140-155 |
| internal joints | 无（rein_form 不改 joint）| — |
| upstream interface | rein 根接到 boss（同臂 mesh，−X 方向）；scroll/eye/方 bar/短 handle 改写 rein helper 或 union 末段装饰 | scrolled L149-234 / eye L144-191 / square L140-155 / handle L181-204 |
| downstream interface | rein tip 形态（圆头 / scroll / eye 环 / 方端 / handle 端球），由各候选 run_tests 验（照搬）| 各 rein 候选表 |

### Slot C / boss_rivet — flat_boss_domed_rivet（baseline，其余 boss_rivet 候选仅换 boss/rivet 细节 visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（boss/rivet 作 visual：boss 各臂 visual、rivet 仅 fixed 臂 visual = captured pivot pin）| af04e104 `_boss_solid` L133-137 / `_rivet_solid` L158-167 / visual L193-207 |
| internal joints | **`rivet_pivot` REVOLUTE**（唯一非 fixed joint，全候选共享）axis=(0,0,−1)，origin=(0,0,Z_LIFT)，lower=0 / upper=0.3 | af04e104 L226-238 |
| upstream interface | root（fixed_arm 坐 boss/pivot 端，无父）| — |
| downstream interface | half-lap 堆叠面 + rivet 穿两 boss（captured，`allow_overlap(rivet, boss)`）；countersunk → flush 头；collar → 抬高头 + inline collar visual | af04e104 L250-256 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_shape | enum | wolf_flat_jaw / ring_bow_jaw / pincer_claw_jaw / flat_box_jaw / vgroove_jaw / hollow_bit_jaw | wolf_flat_jaw | choice | 由 deterministic procedural sampler 选；只换两臂 jaw mesh helper（共用），不改 part/joint；ring/claw 需 rebase(见 §13)| Slot A 表 |
| rein_form | enum | long_straight_rein / scrolled_rein_ends / looped_eye_reins / square_bar_reins / (short_stout_handle) | long_straight_rein | choice | sampler 选；只换两臂 rein/handle mesh helper（共用）；short_stout_handle 可选 secondary 需 rebase + 短把长 | Slot B 表 |
| boss_rivet | enum | flat_boss_domed_rivet / countersunk_flush_rivet / raised_boss_collar | flat_boss_domed_rivet | choice | sampler 选；只换 boss/rivet 细节 visual；countersunk → flush 头断言、collar → 抬高头 + Z_LIFT 加大 | Slot C 表 |
| palette_style | enum | dark_forged / weathered_gray / polished_highlight / browned_blued / bright_bare_steel / aged_pewter | dark_forged | palette | palette only，**不计入 slot_choice**；每 seed 采一套（body/jaw/boss/rivet 四色，见下表）| 各样本材质 |
| rein_length_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 rein 全长（`REIN_TIP_X`/`REIN_SECTIONS`/`REIN_STATIONS` 的 X）→ 联动 scroll/eye/handle 末段 X，clamp 保 overall ~0.50-0.60m | af04e104 L48,87-94 |
| jaw_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 jaw 宽（`JAW_PTS`/`JAW_BOX_PTS`/`BIT_JAW_PTS` 的 Y）保闭合 gap 仍合理，clamp | af04e104 L58-66 |
| jaw_length_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 jaw 长（jaw tip X）保 ~0.055-0.085m 短工作端，clamp | af04e104 L42 |
| boss_size_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 boss 椭圆 `BOSS_A`/`BOSS_B` + `LAP_R`（保 boss ~0.028-0.045m across + rivet 仍居中、lap 仍覆盖）→ 派生 rivet 居中容差，clamp | af04e104 L41-46 |
| splay_angle_scale | float | [0.80, 1.15] | 1.0 | independent | 缩放 rein splay（`REIN_TIP_Y` 双侧外撇半角）保 tips 仍读作双侧外撇(`min_y<−0.030`)，clamp | af04e104 L49 |
| pivot_travel_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 `rivet_pivot` upper（开合行程）保 upper 时 jaws 真张开(`expect_gap>0.005`) + moving rein 外撇 ≥0.05m，clamp（标称 upper=0.3）| af04e104 L237 |
| rivet_head_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 `RIVET_HEAD_R`/`FLUSH_HEAD_R`/`RIVET_SHAFT_R`（保 rivet 居中于 boss footprint + 头 proud/flush 仍成立），clamp | af04e104 L52-53 |
| bore_radius_scale | float | [0.85, 1.12] | 1.0 | conditional | 仅 jaw_shape=hollow_bit_jaw 有效；缩放 `BORE_R`（保 bore 含于加厚 JAW_T、不挖穿），clamp | hollow_bit L64 |
| vgroove_depth_scale | float | [0.80, 1.15] | 1.0 | conditional | 仅 jaw_shape=vgroove_jaw 有效；缩放 `V_GROOVE_DEPTH`/`V_GROOVE_HALF_Z`（保 V 不挖穿 jaw 厚），clamp | vgroove L74-75 |
| scroll_turns_scale | float | [0.80, 1.15] | 1.0 | conditional | 仅 rein_form=scrolled_rein_ends 有效；缩放 `SCROLL_TURNS`/`SCROLL_OUTER_R`（保 scroll 躺平 z<0.025 + 不撞 boss），clamp | scrolled L98,100 |
| eye_loop_scale | float | [0.85, 1.12] | 1.0 | conditional | 仅 rein_form=looped_eye_reins 有效；缩放 `EYE_LOOP_R`（保 eye bore 真闭合 + 超出 plain tip），clamp | eye L53 |
| collar_height_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 boss_rivet=raised_boss_collar 有效；缩放 `COLLAR_H` → 派生 `Z_LIFT`/`RIVET_HEAD_Z`（保 collar 抬高 + tool 仍躺平 z_extent<0.030），clamp | collar L57,59,37 |
| (—) | constraint | — | — | inequality | rivet 居中过盈：`RIVET_HEAD_R·rivet_head_scale ≤ min(BOSS_A,BOSS_B)·boss_size_scale − margin`（captured rivet 头不超出 boss footprint，`expect_within(rivet,boss)` 成立）；违反按比例缩 rivet_head_scale | af04e104 L280-288 |
| (—) | constraint | — | — | inequality | jaws 闭合不过头：q=0(rest) 两 jaw 仅近接(gap≥−0.001)、不互相穿越过中线；`pivot upper·pivot_travel_scale` 使 upper 时 jaws 真张开但休息时不穿模；违反缩 splay/upper 或回退 jaw_width | af04e104 L259-268 |
| (—) | constraint | — | — | inequality | tool 躺平：`tool z_extent ≤ 0.030`（含 boss 堆叠 + collar 抬高 + rivet 头 proud）；raised_boss_collar 时 `Z_LIFT` 派生 ≥ collar+boss 半堆叠；违反缩 collar_height_scale | af04e104 L318-319 |
| (—) | constraint | — | — | inequality | overall 长度：`0.50 ≤ overall_length ≤ 0.60`（rein_length_scale × jaw_length_scale 联合）；short_stout_handle 时放宽到 ~0.30m 短工具域（conditional 范围）；违反缩 rein_length | af04e104 L316-317 |
| (—) | constraint | — | — | inequality | hollow_bit bore 不挖穿：`BORE_R·bore_radius_scale < JAW_T/2 − wall_min`（凹半圆柱不挖穿 jaw 厚，jaw_z>2·BORE_R）；违反缩 bore_radius_scale | hollow_bit L313-320 |
| (—) | constraint | — | — | inequality | raised_collar × pincer 间隙：collar 抬高量 × pincer 短 neck 的贴合留隙重算（collar 不撞 neck/jaw 背）；违反缩 collar_height_scale 或回退 boss_rivet（见 §9 兼容矩阵）| collar L56-59 / pincers L145-159 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，基于 11 样本观察的 forged-steel 真实材质集 + 合理锻钢外推；每套给 body/jaw/boss/rivet 四 rgba）：
| palette_style | body（rein/臂）| jaw（工作端）| boss | rivet | 来源样本 |
|---|---|---|---|---|---|
| dark_forged（默认）| 深锻近黑灰 (0.27,0.28,0.30,1) | 暗 scale (0.23,0.24,0.26,1) | 暗 boss (0.23,0.24,0.26,1) | 暗 rivet (0.20,0.21,0.23,1) | pincers `aged_steel`/`boss_steel` (L239-242) |
| weathered_gray | 风化中灰 (0.37,0.38,0.40,1) | scale 灰 (0.30,0.31,0.33,1) | 灰 boss (0.26,0.27,0.29,1) | 暗 rivet (0.25,0.26,0.28,1) | wolf-jaw `forged_steel_gray`/`jaw_scale_steel`/`rivet_steel` (L183-185) |
| polished_highlight | 中灰 (0.37,0.38,0.40,1) | 抛光亮钢 worn (0.55,0.57,0.59,1) | 中灰 boss (0.30,0.31,0.33,1) | 亮 rivet (0.44,0.45,0.47,1) | pincers `worn_steel` (0.55,0.57,0.59) / bow-ring `worn_steel` (0.44,0.45,0.47) |
| browned_blued | 褐蓝锻钢 (0.22,0.18,0.16,1) | 深褐 (0.18,0.15,0.13,1) | 蓝褐 boss (0.16,0.16,0.20,1) | 蓝黑 rivet (0.14,0.14,0.18,1) | 锻钢 browning/bluing 外推（深色锻钢族）|
| bright_bare_steel | 亮裸钢 (0.62,0.63,0.65,1) | 亮钢 (0.66,0.67,0.69,1) | 亮 boss (0.58,0.59,0.61,1) | 亮 rivet (0.70,0.71,0.73,1) | 新锻 bright bare steel 外推 |
| aged_pewter | 旧锡灰 (0.45,0.46,0.47,1) | 旧锡 (0.40,0.41,0.42,1) | 旧锡 boss (0.42,0.43,0.44,1) | 暗锡 rivet (0.36,0.37,0.38,1) | bow-ring `forged_steel`/`boss_steel` 偏旧灰外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 jaw_shape / rein_form / boss_rivet 的拓扑**（arm 数恒为 2，rivet 恒为 1，joint 恒为单 `rivet_pivot` REVOLUTE）。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（jaw_shape / rein_form / boss_rivet）表达，不暴露 `*_count` 作为可变产品域；**臂数恒为 2、rivet 恒为 1**（双臂 + 单 rivet 是本类身份的固定结构，不是可变 N）。
- **对称双臂是 helper-发射的固定 N=2（非 multiplicity 轴）—— 这是模板要继承的 copy logic**：
  - copied object = **arm（jaw+boss+rein+rivet 的整条锻件）**；moving arm = fixed arm 的**同一锻件绕 X 轴翻转 180°**（jaw/rein 换边、half-lap 面相对）。
  - 复制范式：parent / 多数变体用 `_place(solid, *, flipped: bool)`（`if flipped: solid.rotate((0,0,0),(1,0,0),180)` 再 translate Z_LIFT）+ 对 fixed/moving 各调一次（wolf-jaw L170-176/189-224、scrolled/eye/square/countersunk/box/vgroove 同范式）；**hollow_bit_jaw 与 raised_boss_collar 已把双臂折成显式 `for i,(arm_name,flipped) in enumerate(arms): model.part(arm_name)` 循环（hollow_bit L210-251、collar L217-245）——是最干净的 copy-logic 范例，下游模板统一折成共享 `_emit_arm(i, flipped)` enumerate 循环**（i=0 fixed=root、i=1 moving=child；rivet 仅 i=0 fixed 臂发射 = captured pivot pin）。
  - naming = `fixed_arm`(root) / `moving_arm`(child)；placement = 同件翻转 180°；joint policy = fixed_arm 为 root，moving_arm 经单个 `rivet_pivot` REVOLUTE 铰接（axis=(0,0,−1) ⟂ 工具平面，origin boss 中心）。
- **存在固定 / 装饰性 N 的 module-local 阵列（非可变产品域，不进 slot_choice）**：
  - jaw 上的 `GROOVES`(wolf, L71-75)/`V_GROOVE_STATIONS`(vgroove, L78-85)/`JAW_DIMPLES_*`/`BOSS_DIMPLES`(L80-83) 列表循环、rein 的 `REIN_SECTIONS`/`REIN_STATIONS` loft 站点 `for i in range(REIN_SECTION_PTS)` 截面多边形点、scroll 的 `SCROLL_SECTIONS` loft 站点——**都是装饰 / 几何细分层**，固定或连续(controlled local parameterization)，**不入 slot、不作 N 轴**（脊数 / 截面点数变化不产生新 part/joint 拓扑）。
- 这些都是 **module-local 固定 / 装饰多份 visual / loft 站点**，按 module 而非 multiplicity 轴声明——本类不存在"任意 N 个臂 / N 个 rivet"的真实产品域（真实 blacksmith tongs 恒为两臂单 rivet）。copied object（双臂）用共享 helper 发射、绝对式翻转对称 placement，rivet 是 captured pivot pin（fixed 臂 visual，无独立 joint，Rule 1），jaw/boss/rein 装饰 inline 为 arm visual（Rule 1）。

## 拓扑多样性审计

总组合数：jaw_shape(6) × rein_form(4) × boss_rivet(3) = **72**（全部正交合法，见 §9 兼容矩阵——无完全非法组合需 gate，仅 raised_boss_collar × pincer_claw_jaw 一组接口间隙需 conditional 重算）。若把 short_stout_handle 作为 rein_form 第 5 候选纳入，则 6×5×3 = **90**。


seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（jaw_shape / rein_form / boss_rivet），经兼容矩阵合法化（仅 raised_boss_collar × pincer_claw_jaw 需 conditional 重算 collar-neck 间隙，见下表，无组合完全排除），再解析 conditional scale（bore@hollow_bit、vgroove_depth@vgroove、scroll_turns@scrolled、eye_loop@eye、collar_height@raised_collar），再 uniform 各 independent scale（rein_length/jaw_width/jaw_length/boss_size/splay/pivot_travel/rivet_head）+ 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 rivet_pivot 开合闭口姿态 + 各 jaw 闭合接触语义[V-notch/oval ring/bite/box/V/bore] + rivet 头 proud/flush/collar + rein tip[taper/scroll/eye/方]）。


Controlled local parameterization：见 §参数表的 rein_length_scale / jaw_width_scale / jaw_length_scale / boss_size_scale / splay_angle_scale / pivot_travel_scale / rivet_head_scale（independent）+ bore_radius_scale（@hollow_bit）/ vgroove_depth_scale（@vgroove）/ scroll_turns_scale（@scrolled）/ eye_loop_scale（@eye）/ collar_height_scale（@raised_collar）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：bore 仅 hollow_bit、vgroove_depth 仅 vgroove、scroll_turns 仅 scrolled、eye_loop 仅 eye、collar_height 仅 raised_collar；overall-length 范围随 short_stout_handle 切短工具域）→ 采 independent rein 长 / jaw 宽 / jaw 长 / boss / splay / 开合 / rivet 头 scale → 派生（rivet 居中容差随 boss_size、Z_LIFT 随 collar_height、scroll/eye/handle 末段 X 随 rein_length）→ 用 inequality（rivet 居中过盈、jaws 闭合不过头、tool 躺平、overall 长度、bore 不挖穿、collar×pincer 间隙）投影 / 回缩。跨部件依赖（rivet 头 vs boss、Z_LIFT vs collar、末段 X vs rein_length、bore vs JAW_T）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 rivet captured 接口、`rivet_pivot` joint origin、固定双臂 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（jaw_shape/rein_form/boss_rivet），再解析 conditional scale，再 uniform 各 independent scale，采 palette_style | slot_choices_for_seed 含 `("jaw_shape",m)`/`("rein_form",m)`/`("boss_rivet",m)` 且与 build 一致 |
| compatibility matrix | **三轴基本正交，72(或 90) 组合全合法**——无组合完全排除。conditional / 接口解析：(1) **raised_boss_collar × pincer_claw_jaw**：collar 抬高量 × pincer 短 `neck`(L145-159) 的贴合留隙重算（collar 不撞 neck/jaw 背、Z_LIFT 派生足够）——非排除而是 conditional 重算间隙；(2) bore_radius 仅 hollow_bit；(3) vgroove_depth 仅 vgroove；(4) scroll_turns 仅 scrolled；(5) eye_loop 仅 eye；(6) collar_height 仅 raised_collar；(7) ring_bow_jaw / pincer_claw_jaw × 任意 rein/boss_rivet 合法（rebase 后 jaw 在 +X、rein 在 −X、不冲突）；(8) countersunk_flush_rivet × 任意 jaw 合法（断言从 rivet-proud 换 rivet-flush）；(9) short_stout_handle × 任意 jaw/boss_rivet 合法（短把 → overall ~0.30m 短工具域 conditional）。 | 无 floating / collision / 闭合穿越过头 / rivet 不居中 boss / rivet 头穿出 boss / bore 挖穿 jaw / collar 撞 neck / tool 不躺平 / 长度越界 |
| controlled local variation | 7 independent + 5 conditional clamped scale，每 build 统一；conditional 随 slot 解析 | 比例 / 行程 / 角度变化不破坏 rivet captured、`rivet_pivot` origin、开合闭口、固定双臂 visual、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 jaw_shape 接触语义 QC（V-notch/oval/bite/box/V/bore）+ rivet 头 proud/flush/collar + rein tip taper/scroll/eye/方 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| jaw_shape | 6 | yes | yes | wolf_flat / ring_bow / pincer_claw / flat_box / vgroove / hollow_bit（主 defining mesh / 接触语义轴，满配 6）|
| rein_form | 4 | yes | yes | long_straight / scrolled / looped_eye / square_bar（+ short_stout_handle 可选 secondary → 5）|
| boss_rivet | 3 | yes | yes | flat_boss_domed / countersunk_flush / raised_boss_collar（pivot 细节维度）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("jaw_shape",m)`/`("rein_form",m)`/`("boss_rivet",m)`（连续 scale、palette_style **不进** slot_choice，是装饰 / 颜色非拓扑维度）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；bore/vgroove_depth/scroll_turns/eye_loop/collar_height 为 conditional 随 jaw_shape/rein_form/boss_rivet 解析；六条 inequality（rivet 居中过盈、jaws 闭合不过头、tool 躺平、overall 长度、bore 不挖穿、collar×pincer 间隙）在 resolve 内投影 / 回缩
- compatibility matrix 三轴正交无组合完全排除；conditional scale 仅在对应 module 生效（不在非 hollow_bit 上设 bore、不在非 raised_collar 上设 collar_height）；raised_boss_collar × pincer_claw_jaw 重算 collar-neck 间隙
- 连续 scale clamp 后不破坏 rivet captured 接口、`rivet_pivot` joint origin、开合闭口、固定双臂 visual
- 关键 joint：`rivet_pivot` REVOLUTE **axis≈(0,0,−1)**（`abs(axis[2])>0.99` 且 x/y≈0，⟂ 工具平面，全候选共享），origin 落在 boss 中心 rivet 轴线（`fail_if_articulation_origin_far_from_geometry`），lower=0 / upper≈0.3（按 pivot_travel_scale）
- captured / bridging：element-scoped `allow_overlap(fixed_arm, moving_arm, elem_a="rivet", elem_b="boss")`（rivet 是 captured pivot pin 穿 moving boss，所有 11 样本 run_tests 都有，照搬）
- 各 jaw 候选断言照搬对应样本（wolf V-notch 近接 / ring jaw_tip lap / pincer bite-edge 近接 + jaw 背 throat / box 平行面 / vgroove diamond + V 在 Y 面 / hollow_bit bore 含于 jaw 厚）；rivet 头 proud(domed/collar) vs flush(countersunk) 按 boss_rivet 候选切断言
- 固定双臂 visual 遵循 `fixed_arm`/`moving_arm`(或 enumerate `arm_{i}`) 命名 + 翻转 180° 对称 placement + Rule 1（jaw/boss/rein 装饰 inline 为 arm visual、rivet captured 无独立 joint）
- grandfather：所有 captured / bridging / lap 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- rest pose：`rivet_pivot` q=0（jaws 闭合休息、jaws 几乎相碰、reins 略张）

## Reject cases

- 把 jaw_shape 不同候选混发（如同臂同时发 wolf V-notch jaw + hollow_bit bore jaw，或 ring 半环 + box 矩形）→ Slot A 单选互斥（一次一种 jaw mesh）。
- 暴露 `arm_count` 或把对称双臂 / rivet 当可变 multiplicity 轴编进 slot_choice → 臂数恒为 2、rivet 恒为 1 是固定身份结构（非 N 轴，违反 §8）。
- 加第二个非 fixed joint（如给 jaw 或 rein 额外 REVOLUTE/PRISMATIC，或把两 rivet 头当独立活动 part）→ 本类恒为**单个** `rivet_pivot` REVOLUTE（一根 rivet 一个 pivot）。
- rivet 漂浮 / 不居中 boss（`expect_within(rivet,boss)` FAIL）或 rivet 头穿出 boss footprint（rivet_head_scale 过大 → §7 第一条 inequality FAIL）→ rivet 是 captured pivot pin、须居中嵌入两 boss。
- 把 rivet 当独立 part 用 FIXED joint 接 boss、或给 jaw/boss/rein 装饰补 FIXED 子 part → 违反 Rule 1（rivet 是 fixed 臂 captured visual、jaw/boss/rein 装饰 inline 为 arm visual）。
- `rivet_pivot` rest pose 设成张开（q=upper）而非 q=0 闭合休息 → current-pose 与 viewer 目检不符（所有样本 rest jaws 几乎相碰）。
- `rivet_pivot` axis 设成非 ⟂ 工具平面（如绕 jaw 向 X / 沿臂）→ 违反"绕 rivet 轴(⟂ 工具平面)转"（所有样本断言 axis ⟂ 工具平面）。
- `rivet_pivot` origin 放在臂中心 / jaw / rein 而非 boss 中心 rivet 轴线 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 闭合穿越过头：q=0(rest) 两 jaw 互相穿越过中线（jaw_width / splay 过大）→ §7 第二条 inequality FAIL；缩 jaw_width / splay 或回退。
- jaws 在 rest 张开而非闭合（splay / upper 反向，jaws 休息时已分离过大）→ rest 应是闭合休息（jaws 几乎相碰），违反类别 rest 语义。
- hollow_bit bore 挖穿 jaw 厚（bore_radius_scale 过大 → jaw_z<2·BORE_R）→ §7 第五条 inequality FAIL；缩 bore_radius。
- raised_boss_collar 的 collar 撞 pincer 短 neck / jaw 背，或 collar 抬高致 tool 不躺平（z_extent>0.030）→ §7 第三/六条 inequality FAIL；缩 collar_height_scale / 重算间隙。
- countersunk_flush_rivet 仍发 proud domed 头断言（rivet 头露出 boss 面）→ 与 flush 拓扑矛盾（countersunk 时 rivet 应齐平 boss 面，须切 flush 断言）。
- palette 单色（body/jaw/boss/rivet 全同一 rgba）→ 锻钢 tongs 应有 body/jaw/boss/rivet 的 forged-steel 色差（每 seed 采一套 palette_style）。
- rein 互穿（splay 过小 / scroll / eye 末段相撞越过中线）→ 两 rein 应双侧外撇不互穿；违反 splay 语义。
- 把连续尺寸 / 颜色 / 材质（palette_style / 各 scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 scissors / pliers / wrench / wooden_tongs / clamp 语义混入（finger-loop 剪式 / 中段交叉 box-joint / 螺杆进给 / 木弹性夹 / C-frame）→ 出类，本类是双臂 boss-lap rivet 铰接的锻钢夹（详见 §11）。

## 与相邻类别的边界

- 不该混入：**剪刀（scissors）**——两片刃绕中心 pivot **剪切**片状物、刃成对称剪式、把手是**闭环 finger loops**；本类 jaws **夹持(grip)** 热铁不剪切，reins 是**开放长把**不是 finger loops，pivot 在 boss(jaw 一侧)非两等臂中段。
- 不该混入：**钳子 / 老虎钳 / 扳手（pliers / wrench）**——pliers 是中段**交叉 box-joint** 的小金属切/夹工具(~0.15m、把手成对短、jaw 在 pivot 一侧、handle 在另一侧成对称剪式)、wrench 多单体 / 棘轮无开合 jaws；本类是 ~0.55m 长锻钢、boss 处 **half-lap + rivet** 铆接（非 box-joint）、jaw 短在 +X / 长 rein 在 −X 的非对称长臂 tongs。
- 不该混入：**木上菜 / 厨房夹（wooden serving tongs，已有独立 slug `wooden_tongs`）**——木质一体弹性夹（spring clip / scissor pin / lock ring / 弯木）、palette 是**木**、~0.30m、close_mechanism 改 joint 数；本类是**锻钢** boss-lap **rivet** tongs（palette 全 forged steel、~0.55m、单 rivet 单 REVOLUTE、有真铆点 captured pin）。
- 不该混入：**螺杆台钳 / C 形夹（clamp / vise，已有独立 slug `clamp`）**——螺杆竖直 PRISMATIC 进给 + C 形 frame，主运动 spine 完全不同；本类主运动是绕 rivet 的单 REVOLUTE 开合，无螺杆无 frame。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **坐标统一到 wolf-jaw 的 XY 约定**（11 样本里 9 个直接用、bow-ring/pincers 两个 XZ parent 在模板侧 rebase 到 jaw 在 +X / rein 在 −X / 臂 ±Z 堆叠 / pivot axis=(0,0,−1)，见 §13）是否接受，还是要求保留各 parent 原坐标系分别建模；(2) **short_stout_handle 作为 rein_form 第 5 secondary 候选**（来自 pincers parent、需 rebase + 短把长 → overall 切 ~0.30m 短工具域 conditional）是否纳入（纳入则 6×5×3=90，不纳入则 6×4×3=72）；(3) **臂数恒为 2、rivet 恒为 1、单 `rivet_pivot` REVOLUTE、无 multiplicity 轴** 是否接受（本类多样性来自 jaw/rein/boss mesh 等价类而非 joint 数差异，与 wooden_tongs 的 close_mechanism 改 joint 数不同）；(4) **raised_boss_collar × pincer_claw_jaw** 的 collar-neck 间隙 conditional 重算（非排除）是否接受；(5) palette_style 6 套是否合适（dark_forged/weathered_gray/polished_highlight 为样本观察色，browned_blued/bright_bare_steel/aged_pewter 为合理锻钢外推）；(6) Topology target 72(或 90)<300 的说明是否接受（本小类真实结构上限，单 rivet 单 REVOLUTE 无放大空间）；(7) **countersunk_flush_rivet 时 rivet 头从 proud 断言切 flush 断言** 是否在模板侧按 boss_rivet 候选解析。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **坐标统一 / rebase**：模板统一沿用 **wolf-jaw parent 的 XY 约定**（jaw 沿 +X、rein 沿 −X、扁臂法线 Z、两臂 ±Z half-lap 堆叠、`rivet_pivot` REVOLUTE axis=(0,0,−1)、origin=(0,0,Z_LIFT)、q=0 闭合 / upper jaws 张开）——11 样本里 9 个（wolf parent + 8 变体）直接用它，模板直接照搬。**bow-ring(`ring_bow_jaw`) 与 pincers(`pincer_claw_jaw` + `short_stout_handle`) 两个 XZ-plane parent（原 axis=(0,1,0)、tool 在 XZ 平面）须在模板侧 rebase**：原坐标 (X 横, Z 沿臂, Y 厚) → 目标 (X 沿臂 jaw 向, Y 横/splay, Z 厚/lap 堆叠)，即 ring/claw 的 jaw 几何旋转到 +X、rein/handle 到 −X、half-lap 堆叠从 ±Y 改到 ±Z、pivot 轴从 +Y 改到 (0,0,−1)。rebase 时保留各 jaw 形态识别特征（ring 的 outer-inner-ellipse-cut 半环 + jaw_tip lap、claw 的 spline 厚 jaw + bite_edge + neck web）与 short_stout_handle 形态（lofted 圆角矩形短把 + 端球）。
- **共享 helper**：
  - `_emit_arm(i, flipped, ...)`：发两臂（折成 `for i,(arm_name,flipped) in enumerate([("fixed_arm",False),("moving_arm",True)])`，照搬 hollow_bit L210-251 / collar L217-245 的 enumerate 范例；i=0 fixed=root、i=1 moving=child；rivet 仅 i=0 发射 = captured pivot pin）。
  - jaw mesh helper 按 jaw_shape 切：`_jaw_solid`（wolf V-notch `JAW_PTS` / box 矩形 `JAW_BOX_PTS` / vgroove +`_vgroove_cutter` 由 outline + cutter 切换）、`_bit_jaw_solid`+`_bore_cutter`（hollow_bit 凹 bore，JAW_T 加厚到 0.011）、`_ring_half`+`_jaw_tip`（ring_bow rebase）、`_jaw`+`_bite_edge`+`_neck`（pincer_claw rebase）。
  - rein mesh helper 按 rein_form 切：`_rein_solid`（直 taper `REIN_SECTIONS` / 方 bar `REIN_STATIONS` 由 section 列表切换）、+`_scroll_solid`（scrolled 末段 union spiral volute）、+`_eye_loop_solid`（eye 末段 union torus，注意用 `cadquery.func` 的 `circle`/`face`/`revolve` 造 torus，照搬 eye L152-173）、`_handle`+`_handle_tip`（short_stout rebase 短把）。
  - boss/rivet helper 按 boss_rivet 切：`_boss_solid`（扁椭圆 + `LAP_R` lap / +`_countersink_cutter` 锥孔 / + inline collar union 由分支切换）、`_rivet_solid`（domed sphere 头 / 锥头 revolve flush / 抬高头 collar 由分支切换）。
- **captured 接口 allow_overlap**：`run_blacksmith_tongs_tests` 里补 element-scoped `allow_overlap(fixed_arm, moving_arm, elem_a="rivet", elem_b="boss")`（照搬全 11 样本，reason="round-head rivet 是 captured pivot pin 穿过 moving 臂 boss"）。collar 候选 reason 加"穿两 collar"，countersunk 候选 rivet 嵌 countersink。
- **conditional 范围解析顺序**：先采 jaw_shape / rein_form / boss_rivet → 解析 bore（仅 hollow_bit）/ vgroove_depth（仅 vgroove）/ scroll_turns（仅 scrolled）/ eye_loop（仅 eye）/ collar_height（仅 raised_collar）/ overall-length 范围（short_stout_handle → 短工具 ~0.30m，否则 ~0.55m）→ 采 independent rein 长 / jaw 宽 / jaw 长 / boss / splay / 开合 / rivet 头 scale → 派生（rivet 居中容差随 boss_size、Z_LIFT 随 collar_height、scroll/eye/handle 末段 X 随 rein_length、JAW_T 随 hollow_bit）→ 投影六条 inequality。
- **断言按 jaw_shape / boss_rivet 切**：jaw 闭合断言照搬对应 jaw 候选样本（V-notch 近接 / ring jaw_tip lap / bite-edge 近接 + jaw 背 throat / box 平行面 / vgroove diamond / hollow_bit bore 含于厚）；rivet 头断言按 boss_rivet 切（domed/collar → proud 上下 boss 面；countersunk → flush 齐平 boss 面）。
- **hollow_bit / raised_collar 注记**：两者已用 enumerate-arms 循环且 child(moving) 臂的 `_place` 处理略不同（hollow_bit 的 moving 臂 skip Z_LIFT 因 articulation origin 已提供，L196-199；collar 用 `cq.Location` moved，L189-202；countersunk 加 `skip_lift` 参数 L207-219）——下游统一折成一致的 `_place(flipped, skip_lift=...)` + enumerate 范例，注意 fixed(root)臂 mesh 烘焙 Z_LIFT、moving(child)臂 mesh 留在 child 帧（articulation origin 提供 Z_LIFT）。
- **参考模板**：选运动拓扑相近的——root + 单 child REVOLUTE 互斥 mesh 槽（**`wooden_tongs`** 最近：同 pivot-tongs 机制家族、sweep verdict=pass、同 fixed_arm→moving_arm 单 REVOLUTE + jaw/arm mesh 槽 + grip_detail 装饰槽 + palette_style per-seed 范式；唯一差异是 wooden_tongs 的 close_mechanism 改 joint 数而 blacksmith tongs 恒单 rivet 单 REVOLUTE——本类把多样性全放在 jaw/rein/boss mesh 槽）。blacksmith tongs 尺度（~0.55m 长、boss ~0.035m、rivet ~0.012m），rivet_pivot origin 须精确落 boss 中心 rivet 轴线（baseline ≤0.015m），所有 boolean(jaw groove/V/bore/scroll/eye/collar/countersink) 是 cadquery mesh_from_cadquery，保留 primitive 复杂度（Rule 3，不降级为 Box/Cylinder）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent baseline）| wolf_flat_jaw + long_straight_rein + flat_boss_domed_rivet | rec_model-...wolf-jaw...af04e104 | `_jaw_solid` L114-130 / `_boss_solid` L133-137 / `_rein_solid` L140-155 / `_rivet_solid` L158-167 / `_place` L170-176 / `fixed_arm`+`moving_arm` L187-224 / `rivet_pivot` REVOLUTE L226-238 / allow_overlap(rivet,boss) L250-256 | **fork baseline + 坐标约定**：扁 wolf V-notch jaw + 直 taper rein + 扁 boss/domed rivet + 双臂翻转范式 + 单 `rivet_pivot` REVOLUTE(axis=(0,0,−1)) + captured rivet allow_overlap |
| S2 | A | ring_bow_jaw | rec_model-...bow-ring-jaw...12053487 | `_ring_half` L79-97 / `_jaw_tip` L100-111 / `ring_jaw`+`jaw_tip` visual L188-243 / `boss_rivet_pivot` REVOLUTE L259-269 / jaw_tip lap 断言 L281-326 | 半环 bow loop jaw（outer-inner-ellipse-cut 半环 + 顶端 lap 平片，闭合成 oval ring；XZ→XY rebase）|
| S3 | A / B | pincer_claw_jaw + short_stout_handle | rec_model-...pincers...9dcb992b | `_jaw` L89-125 / `_bite_edge` L128-142 / `_neck` L145-159 / `_handle` L181-194 / `_handle_tip` L197-204 / `_dome` L219-233 / bite-edge 近接 + throat 断言 L362-382 / handle bow 断言 L473-500 | 厚 claw nipper jaw（spline claw + bite_edge + neck web）+ 短粗 handle secondary（lofted 圆角矩形短把 + 端球；XZ→XY rebase）|
| S4 | A | flat_box_jaw | rec_blacksmith_tongs_var_flat_box_jaw | `_jaw_solid` L110-120 / `JAW_BOX_PTS` L66-71 / 平行面断言 L270-286 | 平 box/pickup jaw（矩形 outline 平行内/外面夹平板，无 V-notch）|
| S5 | A | vgroove_jaw | rec_blacksmith_tongs_var_vgroove_jaw | `_jaw_solid` L150-159 / `_vgroove_cutter` L124-147 / `V_GROOVE_STATIONS` L78-85 / diamond + V 在 Y 面断言 L379-383 | 纵 V-groove jaw（内面 loft 三角 V-channel，闭合成 diamond socket 抓圆 bar）|
| S6 | A | hollow_bit_jaw | rec_blacksmith_tongs_var_hollow_bit_jaw | `_bit_jaw_solid` L130-148 / `_bore_cutter` L119-127 / `BIT_JAW_PTS` L72-80 / enumerate-arms L210-251 / bore 含于厚断言 L313-328 | 凹半圆柱 bore jaw（沿 X 挖半圆柱托 rod/pipe，JAW_T 加厚）+ **enumerate-arms copy-logic 范例** |
| S7 | B | scrolled_rein_ends | rec_blacksmith_tongs_var_scrolled_reins | `_rein_solid` L219-234 / `_scroll_solid` L149-216 / `SCROLL_*` L98-104 / scroll 超 splay + 躺平断言 L428-455 | 卷 scroll/volute rein 末端（flat spiral volute 躺工具平面，loft 圆截面沿 spiral）|
| S8 | B | looped_eye_reins | rec_blacksmith_tongs_var_looped_eye_reins | `_rein_solid` L176-191 / `_eye_loop_solid` L144-173 / `EYE_*` L52-54 / eye 超 tip 断言 L379-406 | 闭合 eye 环 rein 末端（torus revolve via `cadquery.func` + blend 球，带真 bore 挂钩）|
| S9 | B | square_bar_reins | rec_blacksmith_tongs_var_square_bar_reins | `_rein_solid` L140-155 / `REIN_STATIONS` L88-95 / `REIN_BAR_HALF` L51 | 恒定方 bar rein（全程方截面 loft，crisp 4-corner，无 taper）|
| S10 | C | countersunk_flush_rivet | rec_blacksmith_tongs_var_countersunk_rivet | `_rivet_solid` L182-204 / `_countersink_cutter` L111-128 / `_boss_solid` L155-161 / `FLUSH_HEAD_R`/`HEAD_DEPTH` L54-55 | 齐平 countersunk rivet（锥头 revolve 两端 peened flush 进 boss 锥孔，rivet 齐平 boss 面）|
| S11 | C | raised_boss_collar | rec_blacksmith_tongs_var_raised_boss_collar | `_boss_solid` L139-153（inline collar L144-153）/ `_rivet_solid` L174-186 / `COLLAR_*` L56-59 / enumerate-arms L217-245 / collar z-extent + 对称断言 L336-355 | 抬高 collar boss（boss 外面 union inline 凸圆柱 collar/hub + rivet 头抬高坐 collar 外面，Z_LIFT 加大）+ enumerate-arms 范例 |
