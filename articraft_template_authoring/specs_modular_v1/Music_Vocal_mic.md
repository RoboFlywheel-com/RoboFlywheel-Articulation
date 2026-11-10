# Vocal Microphone Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `vocal_microphone` |
| template path | `agent/templates/Music_Vocal_mic.py` |
| test path (optional) | `tests/agent/test_vocal_microphone_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：本类别有**两个 baseline body family**，由 `mount_stand` 槽位决定其运动学脊柱（family-gated）。
- **Family A（USB-condenser，源自 parent A）**：根 `base`（加重圆盘 + 站架）→ `body`（REVOLUTE +Y 整体俯仰，windscreen 头为 body 内的 visual）→ N 个 `front_knob_{i}`（multiplicity 轴，CONTINUOUS +X）。
- **Family B（vintage 桌面，源自 parent B）**：根 `base`（加重圆盘 / 三脚 hub）→ `swivel_post`（CONTINUOUS +Z 水平旋转）→ `capsule_head`（REVOLUTE +Y 俯仰，windscreen 头是独立 part）+ `cable`（FIXED 下垂 XLR 线）。

`head_form` 槽位决定 windscreen 形态（在所选 family 内发射），`mount_stand` 槽位决定站架 + 真实 articulation 脊柱，`control_knob_count` 是仅 A family 的 multiplicity 轴。固定 family 内为 linear_chain，跨 family + 多 knob 复制 ⇒ `mixed`。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category: 2 parents + 6 variants `model.py` 全文已读 |
| samples_adopted_as_module_sources | 8 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

8 个 5★ 样本（2 parents + 6 variants，全部 converged/已同步，全部 compile=success、≥1 非 fixed joint、明确读作桌面 vocal microphone）逐条摘要：

- **A0 `rec_blue-usb-condenser-vocal-microphone-yeti-style-w_...91210c09`**（parent A，Family A 基线，全 A 批 fork 母资产）。脊柱：`base`（`_base_disc` L146-L159 加重圆盘 + 中央 hub + 双 `_fork_arm_mesh` L124-L143 Y 叉臂，root/static）→ `base_to_body`（REVOLUTE +Y，±45°，origin z=PIVOT_Z=0.118，L223-L231）→ `body`（`_body_shell` L87-L99 直筒 + `_mesh_grille_band` L63-L84 顶部竖肋网罩 + `_dome_cap` L102-L107 圆顶 + `_pivot_boss` L110-L121 双俯仰 trunnion 被叉臂 knuckle 捕获）。两个 CONTINUOUS 旋钮：`body_to_volume_knob`（+X 前轴，L268-L276）+ `body_to_gain_knob`（+Y 侧轴，L309-L317）。run_tests 校验 body 在双叉臂之间、base 最宽且着地、body 绕 +Y 俯仰（cap 前摆 +X 下沉）、两旋钮 off-center marker 旋转可读。**身份契约**：整头 windscreen 是 tilting `body` 的 visual（无独立 head part），mount=Y-fork 整体俯仰。

- **B0 `rec_vintage-silver-desktop-vocal-microphone-with-a-r_...4ebe60a8`**（parent B，Family B 基线，全 B 批 fork 母资产）。脊柱：`base`（`_base_mesh` L185-L195 加重圆盘）→ `base_to_post`（CONTINUOUS +Z，L225-L233）→ `swivel_post`（`_post_mesh` L165-L182 锥柱 + `_yoke_mesh` L128-L162 U 叉桥/臂）→ `yoke_to_capsule`（REVOLUTE +Y，±45°，origin z=YOKE_PIVOT_Z=0.130，L262-L275）→ `capsule_head`（`_capsule_mesh` L64-L109 扁椭圆 Shure-55 头 + `_loft_yz` L50-L61 + 横向 slat 切槽 + `_grille_interior_mesh` L112-L125 暗内块 + `badge` L249-L251 + `tilt_pin` L254-L255 被 yoke 捕获）+ `cable`（`base_to_cable` FIXED，下垂 XLR 线 + plug，L277-L317）。run_tests 校验 base 着地最宽、capsule 被 yoke 抱持（expect_contact）、capsule 绕 +Y 前后俯仰、post/yoke 绕 +Z 旋转、cable 接 base。**身份契约**：head 是独立 capsule part 钉在 U-yoke，mount=竖直 swivel post + U-yoke（双自由度脊柱）。

- **`rec_vocal_microphone_var_head_ball`**（Family A，Slot A 候选 `round_ball_windscreen`）。Slot A 替换：`_body_shell`（L72-L86）改为**锥形 lathe 身**（下宽上窄到 neck，BODY_TOP_R=0.022），头改为**球形线笼 windscreen**：`_sphere_grille_inner` L89-L95 暗内球 + `_sphere_grille_ribs` L98-L134（`_meridian_path` L147-L156 经线 + `_parallel_path` L159-L167 纬线 + `_rib_tube` L137-L144 共享细管 helper + 赤道加强环）+ `_head_collar` L170-L175 颈环。body 视觉 L263-L268。保留 A 脊柱（base_to_body REVOLUTE L300-L308 + 双旋钮）。run_tests 显式断言球头 XY≈Z 等径（round）、ribs 跨满球径、头心高于 body 顶。这是 `round_ball_windscreen` 权威源（A family）。

- **`rec_vocal_microphone_var_head_cyl_on_vintage`**（Family B，Slot A 候选 `cylindrical_mesh_basket` 的 B-family 实现）。Slot A 替换：`capsule_head` 改为**直立圆柱网篮**：`_basket_shell_mesh` L73-L119（`_basket_rib` L66-L68 共享肋 helper，16 竖肋 `for i in range(RIB_COUNT)` + 上/下 lathe 保持带）+ `_basket_dome_mesh` L122-L131 圆顶 + `_basket_interior_mesh` L134-L141 暗内筒 + `tilt_pin` L263-L265。capsule 视觉 L251-L266。保留 B 脊柱（base_to_post CONTINUOUS L240-L248 + yoke_to_capsule REVOLUTE L274-L287 + cable）。run_tests 断言 basket 高>宽（直立柱）、dome 为最高点、capsule 被 yoke 抱持。这是 `cylindrical_mesh_basket`（B family）权威源。

- **`rec_vocal_microphone_var_mount_shockcradle`**（Family A，Slot B 候选 `elastic_shock_cradle`）。Slot B 替换：Y-fork 双臂改为**整套静态 shock-mount 悬挂全部挂在 base 上**——后弧 `_support_arm_mesh` L161 → `_outer_ring_mesh` L180 外支撑环；`_cradle_ring_mesh` L191 内 cradle 环（**无夹爪**，由弹性带悬住）；`_elastic_band` L214 共享 helper（`N_BANDS=8`，`for i in range(N_BANDS)` L252-L253 把每条带从 outer ring 桥到 cradle ring，构成一个连通的静态总成）；`_pivot_axle_mesh` L204 中央俯仰轴杆。body 上仅增 `_pivot_hub_mesh` L135 俯仰轴套（被静态 pivot_axle 贯穿=captured pin）。base 部件 L243-L255，tilt joint `base_to_body` REVOLUTE +Y（origin (0,0,RING_Z=0.118)）——body 悬在静态 cradle 内绕 +Y 俯仰（保留 A 整体俯仰 + 双旋钮）。所有 cradle/band/axle 都 author 在 cradle 高度 z=RING_Z（不塌到 z=0）。run_tests 断言 cradle 环位于 tilt 轴高度且不随 body 俯仰移动、cradle 环包住 body、outer 环包住 cradle、每条 band 桥接 cradle→outer、body 与 base 悬挂各自连通无孤岛。这是 `elastic_shock_cradle`（A family）权威源（已修正：旧 fork 把 cradle+bands 焊在 tilting body 上且塌到 z≈0，结构错误）。

- **`rec_vocal_microphone_var_mount_tripod`**（Family B，Slot B 候选 `folding_desk_tripod`）。Slot B 替换：base 圆盘改为 `_hub_mesh` L199-L227 中央 hub + 三铰 boss + `_leg_strut_mesh` L230-L301 三锥腿（`N_LEGS=3`，120° splay，方向向量旋转入位）+ `_foot_mesh` L304-L326 橡胶脚。hub 部件 + 腿/脚 L340-L352。脊柱改 root=`tripod_hub`：`hub_to_post`（CONTINUOUS +Z，L363-L371）→ swivel_post → `yoke_to_capsule`（REVOLUTE +Y，L397-L410）+ `hub_to_cable`（FIXED，L447-L453）。run_tests 断言三脚着地、tripod 最宽、三腿≈120°等角、各腿同径、capsule 抱持/俯仰、post 绕 +Z 旋转。这是 `folding_desk_tripod`（B family）权威源。

- **`rec_vocal_microphone_var_controls_n3`**（Family A，multiplicity N=3）。`control_knob_count` 轴：删 A0 的 side gain knob，把控制收为**前面单列竖排**：`_front_knob_mesh` L170-L181 共享旋钮 helper + `_front_knob_marker` L184-L190 off-center pointer，`for i in range(N_FRONT_KNOBS=3)` 循环 L267-L292 发射 `knob_0/1/2`（`KNOB_NAMES`）+ `body_to_knob_{i}`（CONTINUOUS +X，`KNOB_Z_GROUND` L68 等距 Z）。run_tests 断言 3 旋钮、全在 +X 前面、自下而上排序、等距、各绕 +X 旋转。这是 N=3 源。

- **`rec_vocal_microphone_var_controls_n4`**（Family A，multiplicity N=4）。同上 N=4：`_front_knob_mesh` L173-L184 + `_front_knob_marker` L187-L195，`for i in range(KNOB_COUNT=4)` 循环 L266-L300 发射 `front_knob_0..3` + `front_marker_{i}` + `body_to_front_knob_{i}`（CONTINUOUS +X，`KNOB_ZS` L68）。关键：为容纳更高旋钮列，`BODY_TUBE_H` 0.110→0.160（L53），`GRILLE_BOTTOM_Z` 随之上移（L54）。run_tests 断言 4 旋钮全在前面、等距、各绕 +X 旋转、恰 4 个。这是 N=4 源（确立"N=4 需加长 body tube"约束）。

跨样本观察：A family 6 样本共享 `_base_disc`/`_fork_arm_mesh`/`_pivot_boss`/`_mesh_grille_band`/`_dome_cap`/旋钮 `KnobGeometry+marker` + body_off（`BODY_DZ` 把 ground 坐标移入 body part 帧）契约；B family 3 样本共享 `_loft_yz`/`_yoke_mesh`/`_post_mesh`/`_base_mesh`/`tilt_pin` + cable 契约。两 family 都遵守：加重 base 最宽且着地、windscreen 朝 +X、tilt 轴 +Y、captured-pin `allow_overlap`。**桥接点**：`cylindrical_mesh_basket` 头在两 family 都有 5★ 源（A=A0 的 grille_band+dome 整头，B=cyl_on_vintage 的独立 basket capsule），是把两 parent 合成 ONE 模板的结构纽带。配色横跨 blue-USB 与 satin-silver/chrome-vintage 两域，为 §7 `palette_style` 提供 family-flavored colorway 基线。

## 核心身份

桌面 vocal microphone（人声麦克风）：一支立在桌面**加重 base / 三脚架**上的麦克风，通过站架的可动机构（叉式 yoke 俯仰 / 竖直 swivel + yoke 俯仰 / 弹性 shock cradle）调整指向。世界系约定：+Z 向上，加重 base / 三脚脚以 z≈0 着地；windscreen/grille 头朝 +X（前面 = badge / MUTE / 旋钮列所在面）；俯仰 tilt 轴沿 +Y（水平侧轴）；B family 的 swivel 轴沿 +Z（站架中心竖轴）。

成熟域：两支 baseline body family 合成的单一模板——
- **Family A（USB condenser / Yeti 式）**：粗短直筒或锥筒 body 顶部带 windscreen 头（竖肋圆柱网罩 + 圆顶 / 球形线笼），**整头随 body 绕 +Y 叉式 yoke 俯仰**；前面一列 N∈{2,3,4} 个 CONTINUOUS 旋钮（音量/增益/指向）；站架=Y-fork yoke 或 elastic shock cradle，坐在加重圆盘上。
- **Family B（vintage 桌面 / Shure-55 式）**：独立 windscreen 头（扁椭圆肋纹 / 直立圆柱网篮）**钉在 U-yoke 中绕 +Y 俯仰**，yoke 由竖直 swivel post 承载（绕 +Z 旋转），坐在加重圆盘或折叠三脚架上；一根下垂 XLR 线固定在 base。

身份强约束：
- **必须**有一个加重 base / 三脚架作为最宽且着地的站架（不是手持，不是悬挂 boom）。
- **必须**有一个朝 +X 的 windscreen/grille 头（球笼 / 圆柱网篮 / 扁椭圆肋纹之一）。
- **必须**有真实 articulation：A family 至少 body 绕 +Y 俯仰；B family 至少 swivel(+Z) + capsule 俯仰(+Y)。
- 头形 / 站架 / 旋钮数可变（即 Slot A / Slot B / multiplicity），但"站在 base 上的可俯仰人声麦"身份不可缺。

边界（不该混入）见 §11。

## 槽位 + 候选模块表

### Slot A：head_form（windscreen / grille 头形态——决定头部 part/visual 树；在所选 family 内发射）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cylindrical_mesh_basket`（**桥接基线**，两 family 均有源） | A-family: A0 `rec_blue-usb-...91210c09`；B-family: `rec_vocal_microphone_var_head_cyl_on_vintage` | A: `model.py:L63-L84`(`_mesh_grille_band`)、`L87-L99`(`_body_shell` 直筒)、`L102-L107`(`_dome_cap`)、视觉 `L189-L191`；B: `model.py:L66-L68`(`_basket_rib`)、`L73-L119`(`_basket_shell_mesh`)、`L122-L131`(`_basket_dome_mesh`)、`L134-L141`(`_basket_interior_mesh`)、视觉 `L254-L260` | eligible if compatible（A 与 B family 均合法） | 直立圆柱 mesh windscreen：竖肋网罩 + 顶/底保持带 + 圆顶 + 暗内筒。A family 实现=整头作为 tilting `body` 的 visual（grille_band+dome 在 body 直筒顶部，**无独立 head part**）；B family 实现=独立 `capsule_head` part（basket_shell+dome+interior，钉在 yoke）。两实现同一视觉身份，按 family 派生。 |
| `round_ball_windscreen` | `rec_vocal_microphone_var_head_ball`（Family A） | `model.py:L72-L86`(`_body_shell` 锥形 lathe)、`L89-L95`(`_sphere_grille_inner`)、`L98-L134`(`_sphere_grille_ribs`)、`L137-L144`(`_rib_tube`)、`L147-L156`(`_meridian_path`)、`L159-L167`(`_parallel_path`)、`L170-L175`(`_head_collar`)、视觉 `L263-L268` | eligible if compatible（**仅 Family A**） | 球形线笼 windscreen：暗内球 + 经/纬 chrome 肋大圆笼 + 赤道环 + 颈环，坐在锥形 body 颈上。头随 `body` 绕 +Y 俯仰（整头 visual，无独立 part）。part 树与 `cylindrical_mesh_basket` 的 A 实现同名（body 内 visual 不同：head_inner/head_ribs/head_collar vs grille_band/dome_cap）。 |
| `vintage_oval_ribbed` | B0 `rec_vintage-...4ebe60a8`（Family B 基线） | `model.py:L50-L61`(`_loft_yz`)、`L64-L109`(`_capsule_mesh` 扁椭圆 + 横向 slat 切槽)、`L112-L125`(`_grille_interior_mesh`)、badge `L249-L251`、tilt_pin `L254-L255`、视觉 `L242-L255` | eligible if compatible（**仅 Family B**） | 扁椭圆/teardrop Shure-55 头：宽面朝 +X，横向 slat 网格切透前面，暗内块，圆 badge 在肋上，独立 `capsule_head` part 钉在 U-yoke 绕 +Y 俯仰。part 树与 `cylindrical_mesh_basket` 的 B 实现同为 capsule_head，但 visual（capsule_shell/grille_interior/badge vs basket_shell/dome/interior）+ 比例（扁 vs 直立柱）不同。 |

> Slot A 三候选结构差异充分：球笼（A，等径球 + 经纬肋）/ 圆柱网篮（双 family，竖肋直立柱）/ 扁椭圆肋纹（B，扁 teardrop + 横向 slat），是三套不同 windscreen mesh helper + 不同比例。`cylindrical_mesh_basket` 兼跨两 family（含两套 5★ 源），是合成单模板的桥。

### Slot B：mount_stand（站架 + 真实 articulation 脊柱——决定 family、root part、joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 / **articulation** |
|---|---|---|---|---|
| `rigid_forked_yoke`（**Family A 基线**） | A0 `rec_blue-...91210c09` | `model.py:L146-L159`(`_base_disc`)、`L124-L143`(`_fork_arm_mesh`)、`L110-L121`(`_pivot_boss`)、base 部件 `L173-L181`、joint `L223-L231` | eligible if compatible（Family A） | 加重圆盘 + 中央 hub + 两条弧形 Y 叉臂，臂顶 knuckle 捕获 body 俯仰 trunnion boss。**articulation**：`base_to_body` REVOLUTE，axis +Y，origin (0,0,0.118)，±45°（整 body 含整头前后俯仰）。无 swivel、无 cable。 |
| `elastic_shock_cradle` | `rec_vocal_microphone_var_mount_shockcradle`（Family A） | `model.py:L145`(`_base_disc`)、`L161`(`_support_arm_mesh`)、`L180`(`_outer_ring_mesh`)、`L191`(`_cradle_ring_mesh`)、`L214`(`_elastic_band`,`N_BANDS=8`)、`L204`(`_pivot_axle_mesh`)、`L135`(`_pivot_hub_mesh`)、base 部件 `L243-L255`、joint base_to_body | eligible if compatible（Family A） | 加重圆盘 + 后置弧形 support arm → 外支撑环；**整套悬挂静态挂在 base**：inner cradle 环由 8 条弹性悬挂带从 outer ring 桥到 cradle ring 悬住（一个连通静态总成），中央 pivot_axle 俯仰轴杆。**articulation**：`base_to_body` REVOLUTE，axis +Y，origin (0,0,RING_Z=0.118)，±45°——body 悬在静态 cradle 内、`pivot_hub` 被 pivot_axle 捕获绕 +Y 俯仰。无 swivel、无 cable；cradle 环 + bands + pivot_axle 是 **base** part visual（静态），body 仅带 pivot_hub。 |
| `weighted_base_disc`（**Family B 基线**） | B0 `rec_vintage-...4ebe60a8` | `model.py:L185-L195`(`_base_mesh`)、`L165-L182`(`_post_mesh`)、`L128-L162`(`_yoke_mesh`)、base `L208-L214`、post `L217-L233`、capsule joint `L262-L275`、cable `L277-L317` | eligible if compatible（Family B） | 加重圆盘 + 锥形 swivel post + U-yoke 桥/臂 + 下垂 XLR 线。**articulation**：`base_to_post` CONTINUOUS +Z（origin (0,0,0)，水平旋转）+ `yoke_to_capsule` REVOLUTE +Y（origin (0,0,0.130)，±45°，head 在 yoke 俯仰）+ `base_to_cable` FIXED。双自由度脊柱 + 固定 cable。 |
| `folding_desk_tripod` | `rec_vocal_microphone_var_mount_tripod`（Family B） | `model.py:L199-L227`(`_hub_mesh`)、`L230-L301`(`_leg_strut_mesh`)、`L304-L326`(`_foot_mesh`,`N_LEGS=3`)、hub 部件 `L340-L352`、post `L355-L362`、swivel joint `L363-L371`、capsule joint `L397-L410`、cable `L412-L453` | eligible if compatible（Family B） | root 改为中央 hub + 三条 splayed 锥腿（120°）+ 橡胶脚 + 下垂 XLR 线。**articulation**：`hub_to_post` CONTINUOUS +Z（水平旋转）+ `yoke_to_capsule` REVOLUTE +Y（±45°）+ `hub_to_cable` FIXED。脊柱同 B 基线，root part 由圆盘换成三脚 hub（part 树拓扑变化：+3 leg +3 foot visual）。 |

> Slot B 四候选跨**两条 joint 脊柱**：A family（`rigid_forked_yoke` / `elastic_shock_cradle`）= 单 REVOLUTE +Y 整体俯仰（+ N 旋钮 CONTINUOUS）；B family（`weighted_base_disc` / `folding_desk_tripod`）= CONTINUOUS +Z swivel + REVOLUTE +Y tilt + FIXED cable。这是本模板 articulation/topology 多样性的主驱动槽，`mount_stand` 携带真实 articulation。

## 槽位图（slot graph）

pattern = `mixed`（family-gated linear chain + Family A multiplicity 轴）

**Family A 脊柱（mount_stand ∈ {rigid_forked_yoke, elastic_shock_cradle}）：**
```
[base]  (root/static：加重圆盘 + {Y-fork 双臂 + pivot_axle | 后弧 support arm + outer ring + 内 cradle ring + 8 elastic bands + pivot_axle —— 整套静态悬挂})
   |
   |-- REVOLUTE base_to_body (axis +Y, origin (0,0,PIVOT_Z≈0.118), ±tilt_limit)
   v
[body]  (整头 windscreen 为 body visual：cyl=grille_band+dome | ball=head_inner+ribs+collar；
         + 前面 badge/MUTE；+ {双 pivot_boss 被叉臂捕获 | pivot_hub 被 base 静态 pivot_axle 捕获，body 悬在静态 cradle 内绕 +Y 俯仰})
   |
   |-- CONTINUOUS body_to_front_knob_{i} (axis +X, origin (BODY_R-0.001,0,KNOB_Z[i])) ×N   [N∈{2,3,4}]
   v
[front_knob_{i}]  (KnobGeometry + off-center marker，前面竖列)
```

**Family B 脊柱（mount_stand ∈ {weighted_base_disc, folding_desk_tripod}）：**
```
[base]  (root/static：{加重圆盘 | tripod_hub + 3 leg + 3 foot})
   |
   |-- CONTINUOUS base_to_post / hub_to_post (axis +Z, origin (0,0,0))
   v
[swivel_post]  (锥 post + U-yoke 桥/臂)
   |
   |-- REVOLUTE yoke_to_capsule (axis +Y, origin (0,0,YOKE_PIVOT_Z≈0.130), ±tilt_limit)
   v
[capsule_head]  (独立头 part：cyl=basket_shell+dome+interior | oval=capsule_shell+grille_interior+badge；
                 + tilt_pin 被 yoke 臂捕获)

[base] -- FIXED base_to_cable / hub_to_cable --> [cable]  (下垂 XLR 线 + plug)
```

接口点位与装配说明：
- **base → body（A，fold/tilt）**：joint origin 在俯仰轴 (0,0,PIVOT_Z) 或 (0,0,RING_Z)，axis +Y；body 几何以 ground 坐标 author，整体下移 `BODY_DZ=-PIVOT_Z` 进 body part 帧使轴心 = body-local z=0。`rigid_forked_yoke`：`pivot_boss_{pos,neg}` 捕获在 `fork_arm_{pos,neg}` knuckle（element allow_overlap）。`elastic_shock_cradle`：整套悬挂在 base 静态——8 条 `band_{i}` 两端嵌 `outer_ring`/`cradle_ring` tube 桥接成连通总成，`pivot_axle` 贯穿 `cradle_ring`/`outer_ring`；body 的 `pivot_hub` 被静态 `pivot_axle` 捕获（element allow_overlap，captured pin），body 悬在 cradle 内不接触 cradle。
- **base → swivel_post（B，swivel）**：joint origin (0,0,0)，CONTINUOUS +Z；post 脚/collar 嵌入 base/hub 顶（`weighted_base_disc`=seated 圆盘，`folding_desk_tripod`=深 collar 插入 hub）。
- **swivel_post → capsule_head（B，tilt）**：joint origin (0,0,YOKE_PIVOT_Z)，REVOLUTE +Y；`capsule_head` 的 `tilt_pin`（沿 Y）被两 yoke 臂 cap disc 捕获（element allow_overlap），head 侧壁在 U-yoke 臂间 running fit。
- **body / capsule → head_form**：A family head 是 body visual（cyl=grille_band+dome 坐 body 顶；ball=head_inner 下半穿入 body 颈 + head_collar 跨接，物理连接整头到 body 壳）。B family head 是 capsule part 的 windscreen visual（cyl=basket_interior 在 basket_shell 内；oval=grille_interior 在 capsule_shell 内）。
- **body → front_knob_{i}（A，multiplicity）**：joint origin (BODY_R-0.001, 0, KNOB_Z[i])，CONTINUOUS +X；旋钮沿 local +Z 建（center=False，mount 面 z=0），rpy=(0,π/2,0) 使面朝 +X，knob 底座嵌 `body_shell`（element allow_overlap）；off-center marker 使旋转可读。
- **base → cable（B，fixed）**：`base_to_cable` / `hub_to_cable` FIXED，cable_shell 从 base/hub 内侧引出（element allow_overlap）。
- **互斥 / 派生关系**：`mount_stand` 决定 family（A vs B）从而决定整条脊柱与 root part 名；`head_form` 在 family 内选（gating 见 §9）；`control_knob_count` 仅 A family 暴露（B family 无旋钮列，控制=单 badge 点）。head 的 upstream/downstream 接口（body visual vs capsule part + tilt_pin）由 family 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / module `cylindrical_mesh_basket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | A family：无独立 part（grille_band+dome_cap 为 `body` visual）。B family：`capsule_head` part 的 basket_shell/basket_dome/basket_interior visual | A0 / model.py:L189-L191；cyl_on_vintage / model.py:L254-L260 |
| internal joints | 无（windscreen 不单独 articulate；俯仰由 mount_stand 的 tilt joint 承担） | — |
| upstream interface | A：grille_band 坐 body 直筒顶（`GRILLE_BOTTOM_Z..GRILLE_TOP_Z`）；B：basket 坐 capsule 帧，`tilt_pin` 被 yoke 捕获 | A0 L54-L55；cyl_on_vintage L263-L265 |
| downstream interface | 无（终端头） | — |

### Slot A / module `round_ball_windscreen`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（head_inner/head_ribs/head_collar 为 `body` visual，坐锥形 body 颈上） | var_head_ball / model.py:L263-L268 |
| internal joints | 无 | — |
| upstream interface | head_inner 下半穿入 body 颈（`HEAD_CENTER_Z`），head_collar 跨接颈/球以物理连接整头到 body 壳（element allow_overlap） | var_head_ball / model.py:L89-L95, L170-L175, L439-L448 |
| downstream interface | 无 | — |

### Slot A / module `vintage_oval_ribbed`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `capsule_head` part 的 capsule_shell（扁椭圆 + 横向 slat 切槽）/ grille_interior（暗内块）/ badge | B0 / model.py:L242-L255 |
| internal joints | 无 | — |
| upstream interface | capsule 帧坐 yoke pivot；`tilt_pin`（沿 Y）被两 yoke 臂 cap disc 捕获（element allow_overlap） | B0 / model.py:L254-L255, L338-L345 |
| downstream interface | 无 | — |

### Slot B / module `rigid_forked_yoke`（Family A）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`（base_disc + fork_arm_pos/neg，root/static）；body 上 pivot_boss_pos/neg trunnion visual | A0 / model.py:L173-L181, L193-L204 |
| internal joints | `base_to_body` REVOLUTE +Y ±45°（origin (0,0,0.118)） | A0 / model.py:L223-L231 |
| upstream interface | base 着地最宽 footprint；pivot_boss 捕获在 fork_arm knuckle（element allow_overlap） | A0 / model.py:L345-L358 |
| downstream interface | body part 帧（tilting）供 head_form visual + N 旋钮挂接 | A0 / model.py:L187-L221 |

### Slot B / module `elastic_shock_cradle`（Family A）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`（base_disc + support_arm + outer_ring + cradle_ring + band_0..7 + pivot_axle，全 root/static 悬挂）；body 上仅 pivot_hub visual | shockcradle / model.py:L243-L255, L267+ |
| internal joints | `base_to_body` REVOLUTE +Y ±45°（origin (0,0,RING_Z=0.118)）——body 悬在静态 cradle 内俯仰 | shockcradle / model.py: build `base_to_body` |
| upstream interface | base 着地最宽；support_arm 根入 base hub + 接 outer_ring；8 band 桥 outer_ring↔cradle_ring（连通静态总成）；pivot_axle 贯穿两环 + 捕获 body pivot_hub（captured pin，element allow_overlap）；所有悬挂 author 在 z=RING_Z | shockcradle / model.py:L400-L450 |
| downstream interface | body part 帧（悬在静态 cradle 内 tilting，不接触 cradle）供 head_form visual + N 旋钮挂接 | shockcradle / model.py:L267-L379 |

### Slot B / module `weighted_base_disc`（Family B）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base`(base_disc)、`swivel_post`(post_shell + yoke_shell)、`cable`(cable_shell + xlr_tip) | B0 / model.py:L208-L233, L299-L307 |
| internal joints | `base_to_post` CONTINUOUS +Z（origin (0,0,0)）、`yoke_to_capsule` REVOLUTE +Y ±45°（origin (0,0,0.130)）、`base_to_cable` FIXED | B0 / model.py:L225-L233, L262-L275, L311-L317 |
| upstream interface | base 着地最宽；post 脚 seated 入 base 顶（element allow_overlap） | B0 / model.py:L350-L357 |
| downstream interface | yoke pivot 供 capsule_head（head_form）挂接 + tilt_pin 捕获面（yoke 臂 cap disc） | B0 / model.py:L128-L162, L262-L275 |

### Slot B / module `folding_desk_tripod`（Family B）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tripod_hub`(hub_shell + leg_0..2 + foot_0..2)、`swivel_post`(post_shell + yoke_shell)、`cable` | tripod / model.py:L340-L352, L355-L362, L435-L443 |
| internal joints | `hub_to_post` CONTINUOUS +Z、`yoke_to_capsule` REVOLUTE +Y ±45°、`hub_to_cable` FIXED | tripod / model.py:L363-L371, L397-L410, L447-L453 |
| upstream interface | 三脚脚着地最宽；post collar 深插 hub（element allow_overlap + expect_within）；foot taper 插 leg 端 | tripod / model.py:L486-L505 |
| downstream interface | yoke pivot 供 capsule_head（head_form）挂接 + tilt_pin 捕获面 | tripod / model.py:L139-L173, L397-L410 |

### multiplicity / module `front_knob_{i}`（Family A only，见 §8）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_knob_{i}`（KnobGeometry knurled body + off-center marker），i∈0..N-1 | n3 / model.py:L268-L283；n4 / model.py:L277-L290 |
| internal joints | `body_to_front_knob_{i}` CONTINUOUS +X（origin (BODY_R-0.001,0,KNOB_Z[i])） | n3 / model.py:L284-L292；n4 / model.py:L292-L300 |
| upstream interface | 旋钮底座嵌 body_shell 前壁（element allow_overlap），前面竖列等距 | n3 / model.py:L333-L340；n4 / model.py:L342-L349 |
| downstream interface | 无（终端活动件） | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount_stand` | enum | `rigid_forked_yoke` / `elastic_shock_cradle` / `weighted_base_disc` / `folding_desk_tripod` | `rigid_forked_yoke` | choice | deterministic sampler 选择；**决定 family（A vs B）+ root part + 脊柱 joint 拓扑**；先采本槽，family 由它派生 | Slot B 表 |
| `head_form` | enum | `cylindrical_mesh_basket` / `round_ball_windscreen` / `vintage_oval_ribbed` | `cylindrical_mesh_basket` | conditional | 合法集依 family：A→{cyl, ball}，B→{cyl, oval}（gating 见 §9）；在 family 内加权采样 | Slot A 表 |
| `control_knob_count`（=N） | int enum | A family：{2, 3, 4}；B family：`none`(=0) | 2 | conditional | **仅 A family 暴露**；B family 固定 none（控制=单 badge 点）。小 N 偏多 | §8 |
| `palette_style` | enum | `blue_usb_silver_grille` / `blackout_usb` / `matte_black_stage` / `vintage_satin_silver` / `vintage_chrome_oval` / `gold_vintage_brass` | `blue_usb_silver_grille` | conditional | 每 seed 采 colorway；**仅改 material rgba，不改拓扑/尺寸/接口**；palette 池按 family affinity 解析（A→前三，B→后三），见下 | A0 mats L165-L170；B0 mats L201-L205（+ 现实变体派生） |
| `overall_size_scale` | float | [0.85, 1.12] | 1.0 | independent | 各向同性整体尺度；clamp（中心偏向 1.0） | A0 envelope；B0 注 L18 |
| `base_radius_scale` | float | [0.88, 1.15] | 1.0 | independent | 加重圆盘半径 / 三脚 `FOOT_SPREAD_R` 缩放；clamp | A0 `BASE_R` L47；B0 `BASE_RADIUS` L39；tripod `FOOT_SPREAD_R` L53 |
| `body_tube_height_scale`（A family） | float | [0.90, 1.18] | 1.0 | conditional | A family body 直筒高 `BODY_TUBE_H`；**下限随 N 上升**（N=4 需 ≥1.0 容纳 4 旋钮列，参照 n4 把 0.110→0.160）；clamp | A0 `BODY_TUBE_H` L52；n4 L53 |
| `head_size_scale` | float | [0.85, 1.15] | 1.0 | independent | windscreen 头尺寸（球径 `HEAD_R` / 篮径 `BASKET_RADIUS` / 椭圆 `CAPSULE_HALF_*`）；clamp | var_head_ball L59；cyl L51；B0 L45-L47 |
| `tilt_limit_deg` | float | [30, 50] | 45 | independent | 俯仰 REVOLUTE ±limit（A `base_to_body` / B `yoke_to_capsule`）；clamp | A0 L230(±0.785)；B0 L269-L274(±45°) |
| `knob_dia_scale`（A family） | float | [0.85, 1.15] | 1.0 | independent | 前旋钮直径 `KNOB_DIA`；clamp；受 knob_z_spacing 约束（下方 inequality） | n3 `KNOB_DIA` L64；n4 L64 |
| `pivot_z` | float | derived | — | equation | A：`= PIVOT_Z·overall_size_scale`（俯仰轴高，body_off=−pivot_z）；B：`= YOKE_PIVOT_Z·overall_size_scale` | A0 L58；B0 L43 |
| `knob_z_spacing` | float | derived | — | equation | `= body_tube_span / (N+1)`（A family N 个旋钮在 grille 带下方等距，参照 n3 KNOB_Z_GROUND / n4 KNOB_ZS） | n3 L68；n4 L68 |
| `yoke_arm_inner_y` | float | derived | — | equation | B family `= head_half_w·head_size_scale + 0.011`（U-yoke 臂在头侧外 + running fit） | B0 `_yoke_mesh` L132；cyl L147 |
| `cradle/outer_ring_r` | float | derived | — | equation | `elastic_shock_cradle`：`cradle_ring_r = body_r + clearance`，`outer_ring_r = cradle_ring_r + band_len`（band 端点嵌两环） | shockcradle L60-L70 |
| (—) | constraint | — | — | inequality | **base 最宽且着地**：`base_radius_eff > max(body_r, head_half_extent)·head_size_scale + 0.02` 且缩放后 `min_z ∈ [-0.003, 0.003]`。违反→回缩 head_size/overall 或抬 base_radius 下限 | A0 L385-L402；B0 L359-L376；tripod L507-L526 |
| (—) | constraint | — | — | inequality | **A 旋钮列适配**：N 个 KNOB_Z 须落在 (BODY_BOTTOM, GRILLE_BOTTOM) 区间内且 `KNOB_DIA·knob_dia_scale ≤ knob_z_spacing − 0.002`（旋钮不互相 overlap、不越过 grille 带）。违反→升 body_tube_height_scale 或缩 knob_dia_scale | n3 L66-L68；n4 L53-L54, L67-L68 |
| (—) | constraint | — | — | inequality | **A 头/站架 tilt clearance**：在 ±tilt_limit 全俯仰位，windscreen 头（ball 半径 `HEAD_R` 最甚）与 fork 臂 / cradle outer ring 不穿模（Y 向 gap ≥ 0.002）。违反→缩 head_size_scale 或降 tilt_limit | var_head_ball L508-L516；shockcradle L490-L499 |
| (—) | constraint | — | — | inequality | **B 头在 yoke clearance**：`head_half_w·head_size_scale + running_fit ≤ yoke_arm_inner_y`，且 ±tilt_limit 俯仰时 capsule 不撞 post bridge。违反→缩 head_size_scale 或加宽 yoke | B0 L342-L345；cyl L356-L359 |

`palette_style` colorway 取值（rgba 仅示意，下游模板落实；源自 A0 blue-USB 与 B0 satin-silver/chrome-vintage 两域 + 现实变体）：
- **A-family affinity（USB-condenser 域）**
  - `blue_usb_silver_grille`：blue body (0.30,0.36,0.95) + 亮 chrome/silver mesh grille (0.72,0.76,0.82) + silver 旋钮 + 白 badge + 红 MUTE（= A0 基线 + chrome grille 强调）。
  - `blackout_usb`：matte black body (0.10,0.10,0.11) + 黑 mesh + 暗灰旋钮 + 红 MUTE（Yeti Blackout）。
  - `matte_black_stage`：全 matte black 舞台麦 (0.08,0.08,0.09) + 暗灰 grille + 微灰 ring/旋钮（演出黑）。
- **B-family affinity（vintage-desktop 域）**
  - `vintage_satin_silver`：satin silver body (0.80,0.81,0.83) + chrome cap (0.88,0.89,0.91) + 暗 grille interior (0.15,0.15,0.17)（= B0 基线）。
  - `vintage_chrome_oval`：polished chrome 头 (0.86,0.88,0.90) + 黑 slat grille + 深灰加重 base。
  - `gold_vintage_brass`：金/黄铜头 (0.78,0.62,0.24) + 暗 grille + 黑加重 base（Shure-55 gold / "Elvis mic" 配色）。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：`control_knob_count`（仅 Family A）。** 其余固定循环（cradle 8 bands、tripod 3 legs）是 module-local 固定数，不暴露为模板 count 参数。

- `count_param`：`control_knob_count`（N）
- `N_range`：本小类本轴产品域 **[2, 4]**（A0 基线=2，n3=3，n4=4）。测试偏小（N=2/3 高频），N=4 稀有（需加长 body）。
- sampling domain（权重档）：A family 内对 N 加权采样，`P(2)≈0.45 / P(3)≈0.35 / P(4)≈0.20`（小 N 偏多、N=4 尾部稀有，因其需 body_tube 加长且 clearance 更紧）。B family 不暴露该轴（N=none）。
- copied object：**一个前面旋钮** = 1 part（`front_knob_{i}`，KnobGeometry knurled body + off-center pointer marker visual）+ 1 CONTINUOUS joint（`body_to_front_knob_{i}`，axis +X）。
- naming：统一用 `front_knob_{i}` / `front_marker_{i}`（i∈0..N-1）。注：A0 用语义名（volume_knob/gain_knob + *_marker），n3 用 knob_{i}/marker_{i}，n4 用 front_knob_{i}/front_marker_{i}——模板**统一采 n4 的 `front_knob_{i}` 方案**。A0 的 side gain_knob（+Y 唯一例外）**collapse 进前面单列**（multiplicity 轴只发前面 +X 列），与 n3/n4 一致。
- placement：前面 +X 竖列，`x = BODY_R-0.001`，Z 中心等距（`KNOB_Z[i]`，在 grille 带下方、body 下段），由 `knob_z_spacing = body_tube_span/(N+1)` 派生；N=4 时 `body_tube_height_scale` 下限抬升以容纳更高列（参照 n4 BODY_TUBE_H 0.110→0.160）。
- joint policy：每旋钮 `body_to_front_knob_{i}` CONTINUOUS，axis (1,0,0)，effort 0.3 / velocity 8.0；旋钮沿 local +Z 建（center=False），rpy=(0,π/2,0) 使面朝 +X；`allow_overlap front_knob_{i} ↔ body_shell`（底座贴前壁）。
- source/gating：**仅 Family A**（USB-condenser 整 body 前面）。B family（vintage / tripod）无前旋钮列，控制 = 单 badge 点，N gated off B family（见 §9 compatibility）。

## 拓扑多样性审计

总组合数（topology 等价类，由 `slot_choices_for_seed` 报告的 (mount_stand, head_form, control_knob_count) 元组决定）：
- **Family A**：mount ∈ {rigid_forked_yoke, elastic_shock_cradle} (2) × head ∈ {cylindrical_mesh_basket, round_ball_windscreen} (2) × N ∈ {2,3,4} (3) = **12**
- **Family B**：mount ∈ {weighted_base_disc, folding_desk_tripod} (2) × head ∈ {cylindrical_mesh_basket, vintage_oval_ribbed} (2) × N=none (1) = **4**
- 合计 distinct topology 组合 = **16**（palette 与连续 scale 不计入 topology 等价类）。



seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 用 seed 派生 RNG 按**有序 gating** 采样（无需 reject）：
1. 采 `mount_stand`（4 路加权，baselines `rigid_forked_yoke` / `weighted_base_disc` 略加权）。
2. 由 mount 派生 `family`（A if mount∈{rigid_forked_yoke, elastic_shock_cradle}，否则 B）。
3. 在 family-legal 集采 `head_form`（A→{cyl, ball}，B→{cyl, oval}，`cylindrical_mesh_basket` 略加权为桥接基线）。
4. A family 采 `control_knob_count`∈{2,3,4}（小 N 偏多）；B family 设 none。
5. 采 `palette_style`（按 family affinity 池）。
6. 采所有 `independent` 连续 scale → 按 `equation` 派生（pivot_z / knob_z_spacing / yoke_arm_inner_y / cradle&outer ring r）→ 用四条 `inequality`（base 最宽&着地 / A 旋钮列适配 / 头-站架 tilt clearance / B 头在 yoke clearance）投影回缩；`conditional` 范围（body_tube_height 下限随 N、head_form 池随 family）在采样前解析。
`slot_choices_for_seed(seed)` 返回稳定 `[(mount_stand,…),(head_form,…),(control_knob_count,…)]`（B family 第三元组为 `(control_knob_count, "none")` 保持 4 个 B 组合各异；连续 scale/palette 不进 slot_choices）。gating 在 `resolve_config` 解析，不留到 builder。`seed=0` 不特殊。无需 regression overrides（8 源覆盖 16 组合全部一次收敛）；若 sweep 暴露坏组合再按审核加 sparse override。

Topology target：1000-seed slot choice tuple distinct 受类别 slot 池封顶在 **16**（A 2×2×3 + B 2×2）。16 <300 是**类别固有约束**（vocal mic 结构词汇表有限：两 body family、各 2 站架、各 2 头、A 加 3 档 N）而非建模缺陷——多样性由 16 拓扑组合 × 6 palette × 连续 scale 谱共同提供视觉/比例多样性。这与源 map 组合数预审一致（cross-family 头/站架/N 组合未被 5★ 采样，故不进 seed domain）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：`overall_size_scale [0.85,1.12] independent`、`base_radius_scale [0.88,1.15] independent`、`body_tube_height_scale [0.90,1.18] conditional(N)`、`head_size_scale [0.85,1.15] independent`、`tilt_limit_deg [30,50] independent`、`knob_dia_scale [0.85,1.15] independent`；派生 `pivot_z`、`knob_z_spacing = body_tube_span/(N+1)`、`yoke_arm_inner_y = head_half_w·head_size_scale + 0.011`、`cradle/outer_ring_r`。遵循连续尺寸采样契约：先采 independent → 派生 equation → 四条 inequality 投影回缩 → conditional（body_tube 下限/head 池）按上游解析。所有 scale 在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（base 最宽着地、pivot 轴心、tilt_pin/pivot_boss/cradle 捕获、head 坐落 body/yoke）、MatingContract 或 multiplicity（N 旋钮等距适配）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 有序：mount_stand → family → head_form(family-legal) → N(A only) → palette(family pool) → 连续 scale；gating 全在 resolve_config | `slot_choices_for_seed` 与 build choices 一致（16 distinct 元组） |
| compatibility matrix | head×mount 按 family gate：`vintage_oval_ribbed` 仅 B，`round_ball_windscreen` 仅 A，`cylindrical_mesh_basket` 两 family 皆可；`control_knob_count` 仅 A family；palette 池随 family。**有序采样天然合法，无非法组合需 reject**；唯一 fallback：若上游强制了 head 与 family 冲突（如回归 override 指定），head fallback 到 family 内的 `cylindrical_mesh_basket`。 | 无 floating / 无穿模 / base 最宽着地 / 俯仰&swivel clearance / 旋钮仅 A / 头形与 family 匹配 |
| controlled local variation | 6 independent/conditional scale + 派生 pivot/spacing/yoke/ring；全部 clamp + 四条 inequality 回缩 | 比例随机但站架最宽着地、捕获接口、旋钮列适配、tilt/swivel range、类别身份不破 |
| regression overrides | none（8 源覆盖 16 组合，无已知失败回归） | — |
| random sweep | seeds 0-49 初轮（contract），0-999 成熟审计（base 着地 / 旋钮列 / tilt&yoke clearance） |、无 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A head_form | 3 | yes | yes | cyl(桥接,双 family) / ball(A) / oval(B) |
| B mount_stand | 4 | yes | yes | y-fork / shock-cradle（A）/ weighted-disc / tripod（B） |
| multiplicity control_knob_count | N∈{2,3,4}（A only） | yes | yes | 3 档；B family = none |

## Validator

- `slot_choices_for_seed` returns implemented module names（mount_stand∈{rigid_forked_yoke, elastic_shock_cradle, weighted_base_disc, folding_desk_tripod}、head_form∈{cylindrical_mesh_basket, round_ball_windscreen, vintage_oval_ribbed}、control_knob_count∈{2,3,4,none}）。
- `config_from_seed` 对所有普通 seed 用 deterministic 有序 procedural sampling 选 mount→family→head→N→palette→连续 scale；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合：`vintage_oval_ribbed` 仅 B family、`round_ball_windscreen` 仅 A family、`control_knob_count` 仅 A family；head 与 family 冲突时 fallback 到 `cylindrical_mesh_basket`。
- 无 regression override（若加须 sparse + 注明 seed/理由）；不得用 curated/modulo 表当主 seed domain。
- 受控连续 scale（overall_size/base_radius/body_tube_height/head_size/tilt_limit/knob_dia）在 `resolve_config` clamp/派生；四条 inequality（base 最宽&着地 / A 旋钮列适配 / 头-站架 tilt clearance / B 头在 yoke clearance）+ conditional（body_tube 下限随 N、head 池随 family）在 `resolve_config` 求解，不留到 builder 失败。
- 关键 InterfaceSpec/MatingContract 存在：A family `pivot_boss_{pos,neg}` 捕获 `fork_arm_{pos,neg}` knuckle / cradle 夹爪嵌 body_shell + 8 band 嵌 outer_ring（element allow_overlap）；B family `tilt_pin` 捕获 yoke 臂 cap disc + post 脚 seated 入 base/hub（element allow_overlap）；head_form：ball head_inner 穿入 body 颈 + head_collar 跨接 / capsule grille_interior 在 shell 内；A 旋钮底座嵌 body_shell。
- 关键 joint type/axis/range：A family `base_to_body` REVOLUTE +Y ±tilt_limit + N× `body_to_front_knob_{i}` CONTINUOUS +X；B family `base_to_post`/`hub_to_post` CONTINUOUS +Z + `yoke_to_capsule` REVOLUTE +Y ±tilt_limit + `base_to_cable`/`hub_to_cable` FIXED。
- copied object 命名/placement：`front_knob_{i}`/`front_marker_{i}`（i∈0..N-1）前面 +X 等距竖列；joint origin Z 随 `knob_z_spacing` 派生。
- 身份不变量：恰好一个加重 base/三脚架（最宽、着地）；一个朝 +X 的 windscreen 头；A family 整 body 绕 +Y 俯仰、B family swivel(+Z)+capsule(+Y)；head 形与 family 匹配。
- B family：断言无 front_knob part/joint（控制=单 badge）；A family：断言无 swivel/cable，整头随 body 俯仰。

## Reject cases

- `vintage_oval_ribbed` 放到 A-family 整体俯仰 body 上（无独立 yoke-pinned capsule part）→ 扁椭圆头悬空 / 错俯仰脊柱（oval 头只在 B family U-yoke 有源）。
- `round_ball_windscreen` 放到 B-family swivel post 上（cross-family 未采样）→ 无锥形整 body 承托，球头漂浮 / 非法组合。
- `control_knob_count` 暴露在 B family（vintage / tripod）→ 在古董桌面麦前面长出旋钮列（错身份、无源）。
- A family 缺 `base_to_body` REVOLUTE +Y，或 B family 缺 swivel CONTINUOUS +Z / capsule REVOLUTE +Y → 读成静止砖块，丢失"可俯仰桌面麦"语义。
- 加重 base / 三脚架不是最宽 footprint 或不着地（min_z 偏离 0）→ 麦克风漂浮 / 头重脚轻倒下。
- windscreen 头未坐落/捕获：ball head_inner 未穿入 body 颈（head_collar 不跨接）→ 整头脱离 body；cyl basket / oval capsule `tilt_pin` 未被 yoke 臂捕获 → capsule 脱出 yoke。
- A 旋钮列越过 grille 带或相邻旋钮互相 overlap（N=4 未加长 body_tube / knob_dia 过大未回缩）→ 旋钮穿模 / 越界。
- `elastic_shock_cradle` 弹性 band 未触及 outer ring（cradle 悬挂读作断裂），或 `folding_desk_tripod` 三腿非 120°/未全着地 → 站架结构破。
- head_form 与 mount_stand family 不一致（未走 family gating）→ 头挂错脊柱/捕获面错名（A=body visual / B=capsule part + tilt_pin）。

## 与相邻类别的边界

- 不该混入：**handheld_dynamic_mic（手持动圈麦，如 SM58）**——单刚体握把 + 球网罩、**无 base/yoke/tripod 站架、无俯仰/swivel articulation**；本类别恒立在加重 base/三脚架上且头可动，手持麦缺站架与运动语义。
- 不该混入：**studio_boom_arm_mic / 悬臂麦克风支架**——多连杆配重悬臂 + shock mount 夹在桌沿，是 multi-link 机械臂类别（长链铰接），不是本类别紧凑桌面站架（单 yoke/post 俯仰）；运动学拓扑完全不同。
- 不该混入：**megaphone / bullhorn（扩音喇叭）**——喇叭锥 + 手枪握把 + 扳机开关，扩声号角而非 capsule windscreen 头，无加重 base 站架、无俯仰 yoke；身份、声学结构、articulation 均不同。
- 不该混入：**wireless_handheld / lavalier（无线手持/领夹麦）**——无站架、无桌面 articulation，单体或夹片，丢失"立在 base 上可俯仰"定义身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- **Family 分派**：`mount_stand` 是顶层分派键。A family 与 B family 走两套 build helper（A：`_base_disc`/`_fork_arm_mesh`/`_pivot_boss` 或 `_support_arm`/`_outer_ring`/`_cradle_ring`/`_elastic_band` + body_off BODY_DZ 整 body；B：`_base_mesh` 或 `_hub_mesh`/`_leg_strut`/`_foot` + `_post_mesh`/`_yoke_mesh` + cable）。建议公共 helper：加重 base 圆盘、windscreen mesh helper（cyl basket / ball cage / oval loft）按 head_form 分派并按 family 决定挂 body visual 还是 capsule part。
- **`cylindrical_mesh_basket` 双实现**：A family 用 A0 的 grille_band+dome_cap 作为 body 顶部 visual；B family 用 cyl_on_vintage 的 basket_shell+dome+interior 作为独立 capsule part。同一 head_form enum，按 family 走不同 emit 路径——务必让 `slot_choices_for_seed` 仍报告同名 `cylindrical_mesh_basket`（topology 计数把两 family 的 cyl 视为不同组合，因 mount_stand 元组已不同）。
- **captured-pin overlap 须 element-scoped `allow_overlap`**：A=`pivot_boss↔fork_arm` / `cradle_ring↔body_shell` / `band_{i}↔outer_ring` / `front_knob_{i}↔body_shell`；B=`tilt_pin↔yoke_shell` / `capsule(_shell|basket_shell)↔yoke_shell` / `grille_interior|basket_interior↔shell` / `post_shell↔base_disc|hub_shell` / `cable_shell↔base_disc|hub_shell` / tripod `foot_{i}↔leg_{i}`。参考各源 run_tests 的 allow_overlap 块。
- **旋钮列 N=4 加长**：A family N=4 时 `body_tube_height_scale` 下限须抬升（参照 n4 BODY_TUBE_H 0.110→0.160、GRILLE_BOTTOM_Z 上移），并把 `knob_z_spacing` 与 grille 带下沿一起重算——`config_from_seed` 内解析，勿硬编码 KNOB_ZS。
- **A0 的 side gain_knob collapse**：multiplicity 轴只发前面 +X 列（n3/n4 方案）；A0 的 +Y side knob 不作为模板默认（避免与 fork 臂/cradle 干涉，且与 N≥3 不一致）。N=2 也走前面双旋钮列。
- **palette 不进 topology**：`palette_style` 只改 material rgba；按 family affinity 池采样（A→blue/blackout/matte-black，B→satin-silver/chrome/gold-brass），避免"金色 blue-Yeti"等不现实配色。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| A0 | A(cyl,A) / B(rigid_forked_yoke) / mult | `rec_blue-usb-condenser-vocal-microphone-yeti-style-w_20260605_161854_747260_91210c09` | head `L63-L107, L189-L191`；mount `L110-L121, L124-L143, L146-L159, L173-L181, L223-L231`；knobs `L233-L317` | Family A 基线：直筒 body + grille 带 + dome 头 + Y-fork 站架 + 整 body 俯仰 + 双旋钮（multiplicity 母） |
| B0 | A(oval) / B(weighted_base_disc) | `rec_vintage-silver-desktop-vocal-microphone-with-a-r_20260605_161846_030934_4ebe60a8` | head `L50-L125, L242-L255`；mount `L128-L195, L208-L233, L262-L317` | Family B 基线：扁椭圆 Shure-55 头 + 加重圆盘 + swivel post + U-yoke + cable + 双自由度脊柱 |
| S_ball | A | `round_ball_windscreen` | `rec_vocal_microphone_var_head_ball` | `L72-L175, L263-L268, L300-L308` | A family 球形线笼 windscreen（锥形 body + 经纬肋大圆笼 + 颈环） |
| S_cylB | A | `cylindrical_mesh_basket`（B 实现） | `rec_vocal_microphone_var_head_cyl_on_vintage` | `L66-L141, L251-L266, L274-L287` | B family 直立圆柱网篮 capsule（竖肋 + 上下带 + dome + 暗内筒），桥接基线 B 端 |
| S_cradle | B | `elastic_shock_cradle` | `rec_vocal_microphone_var_mount_shockcradle` | `L122-L202, L219-L227, L240-L251, L271-L279` | A family 弹性 shock 站架（后弧 support arm + outer ring + cradle 环 + 8 悬挂带） |
| S_tripod | B | `folding_desk_tripod` | `rec_vocal_microphone_var_mount_tripod` | `L199-L326, L340-L371, L397-L453` | B family 折叠三脚站架（中央 hub + 3 splayed 锥腿 + 橡胶脚 + swivel + cable） |
| S_n3 | mult | `control_knob_count=3` | `rec_vocal_microphone_var_controls_n3` | `L170-L190, L267-L292` | 前面单列 3 旋钮（共享 helper + knob_{i}/marker_{i} + CONTINUOUS +X） |
| S_n4 | mult | `control_knob_count=4` | `rec_vocal_microphone_var_controls_n4` | `L53-L54, L173-L195, L266-L300` | 前面单列 4 旋钮 + body_tube 加长（确立 N=4 加高约束） |
