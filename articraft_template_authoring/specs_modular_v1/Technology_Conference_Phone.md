# Technology / Conference_Phone — desktop conference speakerphone — Modular Spec

> 来源小类：`picture/Technology/Conference_Phone`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Technology__Conference_Phone.md`。
> 参考图：`picture/Technology/Conference_Phone/00{1..5}.png`（tri_star 灰 Polycom / tri_star 三织物翼 / tri_star 穿孔 / winged 双荚银台 / hex 穹顶 tilted 台）。
> **同步/评级注记**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench 样本（5 origin + 8 已采纳 fork），已同步进 `articraft_data/data/records/`。引用以 part/joint/helper **名字** 为准（`body`/`base`/`_radial_profile`/`_body_profile`/`_body_solid`/`_add_button`/`_add_key`/`_keycap_mesh`/`speaker_grille`/`fabric_wing`/`speaker_dome`/`control_deck`/`keypad_console`），行号按各样本当前 `revisions/rev_000001/model.py` 计。
> **O5 名实注记（继承 source map）**：O5 记录 id/prompt 写 "tri-lobed" 系滞后文本，其**建成资产是 hex 六边体**——以建成资产为准（同理见下方 §9 对 winged×discrete_4 gate 的裁定）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Conference_Phone` |
| template path | `agent/templates/Technology_Conference_Phone.py`（stem `conference_phone`）|
| test path (optional) | `tests/agent/test_Technology_Conference_Phone_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（`body` 根 part 融合全部静态装饰 visual：喇叭格栅 / LCD / 控制台 / 脚垫 / LED / 徽标；`keypad_*` 按键为 root 的 prismatic parallel children——**全部非固定关节即按键**，loop 发射）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13（5 origin + 8 已采纳 fork；均 converged、compile 成功、有 URDF，workbench 样本；fork 均 EXIT=0 + 轴断言在 run_tests，source map 背书为采纳集）|
| read_count | 13（全部逐一全文读取，非抽样：每个 `model.py` 全文——5 origin 由主 agent 读，8 fork 由子 agent 逐行读，含 body helper / grille / console / key helper / run_tests 段全部 line-range）|
| read_scope | all adopted samples in this subcategory |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

样本分流说明（对齐 source map 六轴审计）：
- **13 个样本共享同一 skeleton 与同一关节拓扑**：一只**静置桌面机身**（root `body`/`base`）+ 融合其上的**喇叭格栅 + 静态 LCD + 控制台**，加**唯一一族 prismatic 按键**（loop 发射，全部非固定关节均为按键，press 沿 −Z 或沿倾斜台法向）。无拆分、无第二运动 spine。故 ① 骨架图与 ② 关节类型**无独立变化轴**（见 §8.5）；多样性来自 ③ 主体形态家族（body_form 5 态）+ B 喇叭排布（≡ multiplicity N∈{1,2,3,4}+ring）+ ④ grille_treatment（perforated/fabric/domed）+ D control_surface（flush/raised/tilted）+ ⑤ 尺寸行程 + ⑥ 涂装。
- 无 origin 排除（source map：5/5 上格）。8 fork 全采纳。

## 核心身份

桌面**会议扬声电话 / conference speakerphone**（Polycom SoundStation 一类）：主体是一只**低矮静置桌面机身**（tri_star 三臂 / winged 双翼梯形 / hex 六边 / round_puck 圆饼 / square_rounded 圆角方 五种形态家族之一），机身上表面融合一到多只**喇叭格栅**（穿孔金属 / 织物 / 穹顶）、一片**控制台面**（平贴 flush / 抬起 raised / 倾斜 tilted）承载一块**静态 LCD** 与一族**棱柱按键簇**（数字键盘 3×4 或 4×4 + 软键 + 绿接/红挂 + 音量键）。世界系：Z 向上、机身薄板贴桌面 z≈0、用户/键盘端 −Y（front）、喇叭/机身主体偏 +Y·中心（rear）、宽度 X。

活动语义（motion 主契约，全 13 样本一致）：**所有按键为 PRISMATIC 下压键——机身、喇叭格栅、LCD、控制台、脚垫、LED 全部静态（融进 root `body`）；按键是唯一的非固定关节**，flush/raised 台面沿 −Z 下压、tilted 台面沿倾斜法向（`rpy=(tilt,0,0)`, `axis=(0,0,−1)`）下压，行程 0.001–0.003 m。默认成熟域：单台桌面机，无喇叭以外可动件。

不该混入（详见 §11）：普通**台式话机 / desk phone**（有听筒 handset + 挂机叉簧 hook-switch + 旋转/摘挂机构，本类别无听筒、无叉簧，是全双工免提盒）、**对讲门口机 / intercom**（壁挂、单喇叭 + 摄像头 + 呼叫按钮，非桌面三臂/多喇叭免提机）、**桌面音箱 / smart speaker**（无电话键盘、无 LCD 拨号、无绿接红挂键）。

## 槽位 + 候选模块表

> **建模注记**：`body`（根 part）融合全部静态装饰（喇叭格栅 / LCD / 控制台 / 脚垫 / LED / 徽标）为其 visual（Rule 1：不动就不是 part）；`keypad_*` / `softkey_*` / `call_key` / `end_key` / `vol_*` 按键各自以 PRISMATIC 挂到 `body`（parallel children）。下面 4 个 slot（A body_form ③ / B speaker_arrangement≡N / C grille_treatment ④ / D control_surface）与按键阵列的组合构成拓扑多样性（见 §9）。所有 slot candidate **均不新增非按键关节、不改按键 PRISMATIC 语义**（motion-safety 硬契约）。

### Slot A：body_form（③ 主体形态家族 / Primary Form Family——机身主体，类别身份主承载）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| tri_star（基线锚） | forked_anchor | S1 `9bc5796c` / S13 `tilted_console_tri` | S1 `_body_solid` L79-L107（cadquery 盘+3臂 union+dome）；S13 `_radial_profile` L43-L51 + LoftGeometry L267-L280（`r=0.111+0.030cos3θ`）| eligible if compatible | Planar Boundary Form | 三臂放射星（120° 三瓣），中心 hub + 3 臂；plan 轮廓三瓣星。模板取 S13 的 LoftGeometry-over-radial-profile 作实现（primitive 保 Loft）|
| winged | forked_anchor | S4 `e395d9a0` / S10 `flush_console_winged` | outline 16 点 L56-L73 → `sample_catmull_rom_spline_2d` L74 → `section_loft` 4 loop L75-L83 | eligible if compatible | Planar Boundary Form | 双翼梯形：宽扁翼展 + 前收腰 + 后隆肩，catmull-rom 平滑闭合轮廓的 section_loft |
| hex | forked_anchor | S5 `ecc509b0` / S11 `flush_console_hex` | `_body_radius_sharp` L57-L69 + `_body_profile`（径向滑动平均圆角）L72-L80 → LoftGeometry L233-L242 | eligible if compatible | Planar Boundary Form | 角截三角六边体（3 主边 30/150/270 + 3 截角 90/210/330），圆角六边 plan |
| round_puck | forked_anchor | S6 `round_puck` | `_body_solid` L105-L141（cadquery circle.extrude + dome loft + 圆角）| eligible if compatible | Volumetric Envelope Form | 圆饼/圆鼓机身（轴对称圆盘 + 浅穹顶），plan 为圆；模板以 superellipse≈circle 的 LoftGeometry 实现 |
| square_rounded | forked_anchor | S7 `square_body` | `_rounded_box` L36-L41 + `_rounded_square_body` L49-L53（`.box(...).edges("|Z").fillet`）| eligible if compatible | Planar Boundary Form | 圆角正方机身（大圆角方板），plan 为圆角方；模板以 `rounded_rect_profile` 的 LoftGeometry 实现 |

硬约束记录：body_form 5 candidate（超 3-6 目标，形态主导类要求登记 ③ slot ✔）。五者共享同一 root part / 同一 LoftGeometry-over-planform 装配家族（模板把 5 种 plan 轮廓统一为 `_planform(form)` → `LoftGeometry([scaled@z0, scaled@mid, scaled@top])`，primitive 恒为 Loft，Rule 3 不降级）与同一 body→按键接口，安全。均标 form_subtype。

### Slot B：speaker_arrangement（≡ 喇叭 multiplicity N；喇叭排布层，见 §8）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | N | 结构特征 |
|---|---|---|---|---|---|---|
| central（基线） | forked_anchor | S1 `9bc5796c` / S5 `ecc509b0` / S6 `round_puck` / S11 `flush_console_hex` | S1 `_speaker_grille_mesh` L110-L122 + place L177-L187；S5 dome L246-L248 | eligible if compatible | 1 | 单只中央大格栅（hub 中心，偏 +Y·rear），最经典读法 |
| discrete_2 | forked_anchor | S4 `e395d9a0` / S10 `flush_console_winged` | 2× surround+grille loop over `(("0",−0.188,..),("1",0.188,..))` L97-L110 | eligible if compatible | 2 | 双侧荚（左右 ±X 大椭圆荚 + 穿孔面），winged 双翼读法 |
| discrete_3 | forked_anchor | S2 `0672d2af` / S3 `fe888f0f` / S7 `square_body` / S12 `raised_console_tri` | S3 grille loop over `(90,210,330)` L115-L122；S2 wings L224-L246 | eligible if compatible | 3 | 三瓣格栅（三臂/三角 120° 各一），tri_star/square 三织物翼或三穿孔 |
| discrete_4 | forked_anchor | S8 `quad_pods` | 4× surround+grille loop over `corner_speakers` L98-L117 | eligible if compatible | 4 | 四角荚（winged 四角穿孔荚），四喇叭免提读法 |
| perimeter_ring | forked_anchor | S9 `perimeter_ring` | 6 `band_segment_i` Box 沿 hex 边 + slot 标 L229-L268 | eligible if compatible | ring | 环周带格栅（沿机身边缘一圈连续带，无离散 N），hex 环带读法 |

硬约束记录：speaker_arrangement 5 candidate（超 3-6）。这是**同时承载 §8 multiplicity（N=喇叭数）与 B 排布结构**的轴：N 绑定 arrangement 不独立采样（central=1/d2=2/d3=3/d4=4/ring=无 N）。每只喇叭格栅几何随 Slot C grille_treatment 决定表面，随 Slot A body_form 决定落位半径（派生嵌入机身上表面）。所有离散喇叭**复用同一 grille `Mesh`**（放置 N 次），控 compile 成本（见 §7.5）。

### Slot C：grille_treatment（④ 表面装饰——喇叭面处理，跨族外推轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| perforated（基线） | forked_anchor | S1/S3/S4/S7/S8/S9/S10/S12 | S3 `PerforatedPanelGeometry` L103-L114；S1 L110-L122 | eligible if compatible | 穿孔金属格栅面（`PerforatedPanelGeometry`，圆角面板/圆盘），最常见 |
| fabric | forked_anchor | S2 `0672d2af` / S13 `tilted_console_tri` | `_wing_profile` L114-L132（superellipse 布垫）+ `_woven_threads` L50-L111（细交叉线，模板降密）| eligible if compatible | 织物喇叭垫（superellipse 布垫 + 稀疏织纹肋），黑织物读法 |
| domed | forked_anchor / record_only | S5 `ecc509b0` / S11 `flush_console_hex` | `_dome_vertex` L145-L149 → `LoftGeometry(dome_loops)` L246-L248 + 稀疏 perf dots(Sphere) L251-L257 | eligible if compatible（仅 central）| 穹顶穿孔格栅（中央隆起穹面 + 半嵌 perf 点），单中央喇叭专属 |

硬约束记录：grille_treatment 3 candidate（达 3-6）。④ 表面/形态处理轴，跨族移植走 world_knowledge（perforated/fabric 可上任一 body_form 与任一离散 arrangement；domed 仅 central——穹顶是单只中央隆起，见 §9 gate）。装饰几何由宿主喇叭落位面逐-z 派生、随 ③③⑤ 共形嵌入（派生顺序 ③body_form→⑤尺寸→④grille），不悬空。fabric 织纹密度模板显著降密（compile 预算）。

### Slot D：control_surface（控制台面层——键盘/LCD 承载面）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| flush（基线） | forked_anchor | S1 `9bc5796c` / S10 `flush_console_winged` / S11 `flush_console_hex` | S10 flush console L114-L128（面与机身顶共面 z=0.032）；S11 flat deck L291-L296 | eligible if compatible | 平贴台面：键盘/LCD 直接坐在机身顶面（或浅凹井），按键 **straight −Z**（`axis=(0,0,−1)` 无 pitch rpy）|
| raised | forked_anchor | S3/S4/S12 | S12 pedestal `_control_deck` L68-L81（`DECK_TOP_Z−BODY_TOP_Z>0.020`）；S4 trapezoid console L112-L133 | eligible if compatible | 抬起台面：一座抬高控制岛（银梯台/柱台），按键在岛顶 **straight −Z** |
| tilted | forked_anchor | S5 `ecc509b0` / S9 `perimeter_ring` / S13 `tilted_console_tri` | S5 `keypad_console` Box `rpy=(PANEL_TILT=0.35,0,0)` L291-L296 + `_add_key` `rpy=(PANEL_TILT,..)` L207；S13 wedge `RAKE=15°` L156-L194 | eligible if compatible | 倾斜台面：朝用户抬头的斜台（`rpy=(tilt,0,0)`），按键沿**倾斜法向**下压（`pressed[2]<rest`，`pressed[1]>rest`）|

硬约束记录：control_surface 3 candidate（达 3-6）。三者共享同一 keypad/LCD 装配与同一按键 PRISMATIC 语义，仅台面 z-抬高量与倾角不同（flush=0/无 tilt、raised=+0.020~0.030、tilted=0.35 rad 或 15°）。按键 origin/axis 随台面派生（flush/raised: `(x,y,deck_z)` axis −Z；tilted: `_panel_point(u,v)` + `rpy=(tilt,0,0)` axis −Z）。全 body_form 均支持三态（无 D×A gate）。

## 槽位图（slot graph）

```text
pattern: mixed（body 根融合全部静态装饰 + keypad_* PRISMATIC parallel children）

                    body (ROOT = Slot A body_form ③)
                      │ 几何身份：_planform(form) → LoftGeometry 低矮桌面机身
   ┌──────────────────┼───────────────────────┬───────────────────────────┐
   │(融合 visual)      │(融合 visual)          │(融合 visual)               │PRISMATIC ×K（唯一非固定关节）
   │Slot B speaker     │Slot C grille          │Slot D control_surface       │keypad_r_c / softkey_i /
   │_arrangement(≡N)   │_treatment(每喇叭面)   │(台面 + LCD 融进 body)       │call_key / end_key / vol_up/down
   ▼                   ▼                       ▼                            ▼
喇叭格栅 ×N / 环带     穿孔/织物/穹顶面          flush/raised/tilted 台+LCD    按键（stem+cap+legend）
（落位半径随 A 派生）   （随喇叭落位面共形）      （台面 z/tilt 决定按键 origin）  press −Z 或沿斜法向
```

接口点位与关节策略：
- **body（root）**：world root part；上表面（`_planform` 顶 loop 的 z_top 面）是所有喇叭/台面的贴装母面。
- **body → 喇叭格栅（Slot B×C）**：融合 visual（非关节，Rule 1）；每喇叭格栅**凹嵌**机身上表面（overlap → 有支撑、无岛）。离散 N 只复用同一 `Mesh`。
- **body → 控制台 + LCD（Slot D）**：融合 visual；台面**基座嵌入**机身顶面（overlap 支撑）。
- **body → keypad_*（按键）**：PRISMATIC，唯一非固定关节族；origin 在台面（flush/raised: `(x,y,deck_z)` axis=(0,0,−1)；tilted: `_panel_point(u,v)` `rpy=(tilt,0,0)` axis=(0,0,−1)），键 cap 底浅嵌台面 well（scoped allow_overlap cap↔body_shell），行程 [0, travel]。**按键是唯一活动件。**

派生说明：Slot A 决定机身上表面尺寸/形状 → B（喇叭落位半径）、C（喇叭面共形）、D（台面落位 + 按键 origin）全部**依赖 A 的当前 envelope**（conditional，见 §7）。喇叭排布角度避开 −Y front 键盘扇区（B 落位在 rear/side 半区，键盘在 front-central，x/y 分离保 clearance）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form（tri_star / winged / hex / round_puck / square_rounded）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（根 part）：低矮桌面机身 LoftGeometry（+ 3 脚垫 visual）| S13 L267-L280 / S5 L233-L242 |
| internal joints | 无（root 无内部关节）| — |
| upstream interface | root（world，薄板贴桌面 z≈0）| S13 L276 |
| downstream interface | 机身上表面（喇叭贴装面 / 台面基座面 / 按键 origin 母面）| S13 `_radial_profile` L43-L51 |

### Slot B / speaker_arrangement（central / discrete_2/3/4 / perimeter_ring）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` 的 visual：`speaker_grille_*`（离散 ×N 复用 Mesh）/ `perimeter_band_*`（环带）| S3 L115-L122 / S9 L229-L268 |
| internal joints | 无（喇叭格栅静态融入 body）| — |
| upstream interface | 机身上表面落位半径（central=hub 中心 +Y offset；离散=lobe 角 ×N；ring=环周）| S4 L97-L110 / S8 L98-L117 |
| downstream interface | 无 | — |

### Slot C / grille_treatment（perforated / fabric / domed）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每喇叭面：`PerforatedPanelGeometry` 盘 / superellipse 布垫+织纹 / `LoftGeometry` 穹顶+perf 点（body visual）| S1 L110-L122 / S2 L114-L132 / S5 L246-L257 |
| internal joints | 无 | — |
| upstream interface | 喇叭落位面（由 Slot B 落位、随 Slot A 形态共形，派生顺序 ③→⑤→④）| S2 `_wing_profile` L114-L132 |
| downstream interface | 无 | — |

### Slot D / control_surface（flush / raised / tilted）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` visual：`control_deck`/`keypad_console`（台面）+ `lcd_bezel`/`lcd_glass`/`lcd_segment_*`（LCD）| S10 L114-L128 / S5 L291-L339 |
| internal joints | 无（台面 + LCD 静态融入 body）| — |
| upstream interface | 机身前部（−Y）顶面（台面基座嵌入）| S12 `_control_deck` L68-L81 |
| downstream interface | 台面工作面（→ 按键 origin：flush/raised `deck_z`、tilted `_panel_point`）| S5 `_panel_point` L129-L135 |

### 按键族（body → keypad_* PRISMATIC，唯一非固定关节）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `keypad_{r}_{c}`（数字阵列 rows×cols）+ `softkey_{i}` + `call_key` + `end_key` + `vol_up`/`vol_down`：每键 stem(Cylinder)+cap(Box)+legend(Box)| S5 `_add_key` L169-L210 |
| internal joints | `body_to_{key}` PRISMATIC，axis=(0,0,−1)，flush/raised 直下 / tilted `rpy=(tilt,0,0)` 斜法向，limit=[0,travel] | S5 L202-L209 |
| upstream interface | 键 cap 底浅嵌台面 well（`elem_a="cap"` `elem_b="body_shell"` scoped allow_overlap）| S1 L317-L325 |
| downstream interface | 无（末端活动件）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | {tri_star, winged, hex, round_puck, square_rounded} | — | choice | deterministic sampler 选（③）| Slot A |
| speaker_arrangement | enum | {central, discrete_2, discrete_3, discrete_4, perimeter_ring} | — | choice | sampler 选（受 body_form gate，见 §9）；决定 N | Slot B / §8 |
| grille_treatment | enum | {perforated, fabric, domed} | — | choice | sampler 选（domed 仅 central，见 §9）| Slot C |
| control_surface | enum | {flush, raised, tilted} | — | choice | sampler 选（全 body_form 兼容）| Slot D |
| keypad_shape | enum | {"3x4", "4x4"} | "3x4" | choice | 数字阵列 rows×cols（§8 阵列 param）| S1/S2(3x4) / S3(4x4) |
| palette_style | enum | {graphite_gray, matte_black, black_silver, white_silver, charcoal_two_tone}（5）| graphite_gray | choice | 仅涂装，不改几何（⑥）| §8.5⑥ |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放机身特征半径 R_char；采样后 clamp | S13 L40 / S5 L26-L27 |
| body_height_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放机身板厚 BODY_TOP；clamp | S13 L23 / S5 L27 |
| speaker_radius_frac | float | [0.55, 0.68] | 0.62 | independent | 离散喇叭落位半径占 R_char 比；clamp | S2 L226 / S4 L97 |
| key_travel | float | [0.0010, 0.0030] | 0.0018 | independent | 按键行程；clamp | S3 L25 / S7 L26 |
| deck_rise | float | conditional | derived | conditional | flush=0 / raised∈[0.020,0.032] / tilted 台顶抬高由 tilt 派生；随 control_surface | S12 L68-L81 / S5 L39-L49 |
| panel_tilt | float | conditional | derived | conditional | flush/raised=0 / tilted∈[0.26,0.44] rad（贴 S5 0.35 / S13 15°）；随 control_surface | S5 L42 / S13 |
| speaker_lobe_radius | float | derived | — | equation | `= speaker_radius_frac · R_char`；随 A 派生，不独立采样 | S2 L226 |
| deck_z | float | derived | — | equation | `= BODY_TOP·body_height_scale + deck_rise`；按键 origin 高度单一来源 | S12 L70 |
| (—) | constraint | — | — | inequality | **喇叭 clear 键盘**：离散喇叭落位 xy-AABB 与 front-central 键盘 console AABB 不重叠（x 或 y 分离 ≥ margin）；违反→缩 keypad console 或抬 speaker_lobe_radius | S6 L455-L459 |
| (—) | constraint | — | — | inequality | **键 cap 坐台面**：cap 底浅嵌台面 well（embed≈0.002），不悬空不沉桌；每键 scoped allow_overlap cap↔body_shell | S1 L317-L325 / S3 L204-L213 |
| (—) | constraint | — | — | inequality | **perimeter_ring clear 键盘**：ring 内径 > 键盘 console front 最大 extent；ring 仅 hex/round/square（gate）| S9 L403-L420 |
| (—) | constraint | — | — | inequality | **tilted 按键全程不穿台**：press 沿斜法向，`pressed[2]<rest−ε` 且 `pressed[1]>rest`（S13 断言 dy≈travel·sinθ）| S13 L475-L488 |

连续尺寸采样契约：先采 independent（body_radius/body_height/speaker_radius_frac/key_travel）→ 按 equation 派生（speaker_lobe_radius=frac·R_char、deck_z）→ conditional 解析（deck_rise / panel_tilt 依 control_surface）→ inequality 投影/回缩（喇叭 clear 键盘、键坐台面、ring clear 键盘、tilted 不穿台）。全部在 `resolve_config` 求解，不留 builder。

## Multiplicity / Copy Logic

- **喇叭数 N ≡ Slot B speaker_arrangement，绑定不独立采样。** N∈{1,2,3,4}（central=1 / discrete_2=2 / discrete_3=3 / discrete_4=4），perimeter_ring 为连续带无 N。`count_param`：`speaker_count`（由 arrangement 派生）。`N_range`：本小类本轴 [1,4]（窄域，raw N；无大 N 尾部）。sampling domain：**不独立加权采样 N**——N 由 arrangement enum 决定，arrangement 采样即 N 采样（受 body_form gate，见 §9）。copied object：`speaker_grille_{i}`（i∈0..N−1），**全部复用同一 `Mesh`**（identical 几何，visual/bbox 随 N 成比例）；placement：lobe 角均匀分布避开 −Y front 键盘扇区；joint policy：无（喇叭静态融入 body，非关节）；source/gating：见 Slot B + §9 gate。`slot_choices` 单列 `speaker_count`（raw N；ring 记 "ring"）以供 §8 banding 可见性。
- **键盘阵列 N（次级 multiplicity 轴）：`keypad_shape ∈ {"3x4","4x4"}`。** 数字键阵列 rows×cols（12 或 16 键），for-loop 发射 PRISMATIC 按键；`N_range` 离散两态（源 S1/S2=3x4、S3=4x4）。copied object：`keypad_{r}_{c}`；placement：台面矩形网格；joint policy：每键 PRISMATIC（唯一活动件族）；不与 speaker N 耦合。
- 其余（软键 3 / 绿接 / 红挂 / 音量 ×2）为固定命名按键，非采样 multiplicity。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 无 | 13 样本共享同一 part-joint 图（body 根融合全部静态装饰 + 一族 PRISMATIC 按键）；无样本新增第二运动件（无听筒/无叉簧/无翻盖）。故无 ① 变化轴 |
| └ multiplicity | 同构件 ×N | **有** | 见 §8：喇叭 N∈{1,2,3,4}+ring（≡ Slot B，绑定 arrangement）+ 键盘阵列 {3x4,4x4}。均 loop 发射 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 无 | 全部非固定关节恒为 PRISMATIC 下压键（flush/raised 沿 −Z、tilted 沿斜法向仍是同一 prismatic axis=(0,0,−1) + rpy 座标系旋转）；无 revolute/continuous。故无 ② 轴（tilted 只改 origin rpy，非改关节 type） |
| ③ 主体形态家族 | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | **Slot A body_form（登记进 slot_choices）**：tri_star（Planar Boundary，S1/S13）、winged（Planar Boundary，S4/S10）、hex（Planar Boundary，S5/S11）、round_puck（Volumetric Envelope，S6）、square_rounded（Planar Boundary，S7）。5 可识别机身原型，均 forked_anchor、均标 form_subtype |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | **Slot C grille_treatment**（perforated S1/S3.. / fabric S2/S13 / domed S5/S11）+ **Slot B 喇叭排布面** + LCD 段/徽标/LED（S3/S5 status_led、S5 logo_badge）。装饰几何均由宿主喇叭落位面/机身顶面逐-z 派生、随 ③③⑤ 共形嵌入（派生顺序 ③→⑤→④），不悬空 |
| ⑤ 尺寸/行程 | 离散不变，只连续改尺寸/比例/行程 | **有** | 关键比例（见 §7）：body_radius_scale[0.90,1.12]、body_height_scale[0.90,1.15]、speaker_radius_frac[0.55,0.68]、key_travel[0.0010,0.0030]、deck_rise/panel_tilt(conditional 依 control_surface)。**关节运动包络 + motion_test_plan**：`body_to_{key}` PRISMATIC axis=(0,0,−1)、开启方向 −q（下压）、[0, key_travel]。targeted `ctx.pose({key:travel})` 验：(a) flush/raised 键 straight −Z（`pressed[2]<rest`，XY 稳定 |Δx|,|Δy|<1e-4）；(b) tilted 键沿斜法向（`pressed[2]<rest` 且 `pressed[1]>rest`，S13 L475-L488）。需 `fail_if_parts_overlap_in_sampled_poses`（多键 → cap max_pose_samples=32）+ 每台面型 ≥1 targeted pose |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 材质大类：metal(机身漆面/穿孔格栅/银台/LCD 玻璃) + plastic(键帽/机身壳) + fabric(织物喇叭垫)。配色 ≥5：graphite_gray（S1 灰 Polycom：灰机身+蓝灰键）、matte_black（S2/S4/S5 全黑）、black_silver（S4 黑机身+银 console）、white_silver（S7 白+银伴随）、charcoal_two_tone（S9 双色调）。材质大类覆盖 ≥ ceil(0.5×5)=3（metal+plastic+fabric，✔，fabric 仅 grille=fabric 时出现）|

**收尾自检**：0-9 seed 渲染须肉眼可见——五种机身形态（三臂星/双翼/六边/圆饼/圆角方）拉得开、喇叭 1/2/3/4/环带都出现、格栅穿孔↔织物↔穹顶可辨、台面 flush↔raised↔tilted 可辨、LCD+绿接红挂键可辨、按键全程 −Z/斜法向不穿台、5 配色 metal/plastic/fabric 大类都出现。


## 拓扑多样性审计

总组合数（含 gate 后合法组合）：body_form(5) × speaker_arrangement(受 gate) × grille_treatment(受 domed gate) × control_surface(3) × keypad_shape(2)。
- 合法 (body_form × arrangement)：tri_star{central,discrete_3}=2 + winged{central,discrete_2,discrete_4}=3 + hex/round/square 各 5 = 2+3+15 = **20** 组 body×arrangement。
- grille：domed 仅 central（central 支持 perforated/fabric/domed=3；其余 arrangement 支持 perforated/fabric=2）。central 组 8 个（tri/winged/hex/round/square 的 central，共 5，另 hex/round/square 各已计）——逐组计：合法 (body×arr×grille) = Σ per组(central→3, 其它→2)。central 组数 = 5（每 body_form 一个 central）→ 5×3=15；非 central 合法组 = 20−5=15 → 15×2=30；合计 **45** 组 (body×arr×grille)。
- ×control_surface(3) ×keypad_shape(2) = 45×3×2 = **270** 个合法离散拓扑组合（palette 5 与连续 scale 不计结构 distinct）。

理由：A=5、C=3、D=3、keypad_shape=2 全 ≥2 且全 reachable；B 的 5 值全 reachable（central/discrete_3 经 tri_star 或 hex；discrete_2/discrete_4 经 winged 或 hex；ring 经 hex/round/square），无死轴。gate 只删非法 (body×arr) 对，不孤立任何 slot 值。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic RNG(seed)：先采 body_form（5 态近均匀）→ 采 speaker_arrangement（**从该 body_form 的合法集加权采样**，gate 见下）→ 采 grille_treatment（从该 arrangement 合法集：central→{perf,fabric,domed}，其它→{perf,fabric}）→ 采 control_surface（3 态均匀）→ keypad_shape（2 态）→ palette（5 态）→ 连续 scale（§7 契约）。compatibility gate 在采样时即约束（拒绝非法值域，非采后丢弃），seed=0 不特殊。random sweep：0-35 首轮（pipeline fast 0-15 + final 16-35 + corner），0-999 成熟审计。
**Compatibility matrix / gating（抄 source map 四态 cross 矩阵，裁定见下）**：
| body_form \ arrangement | central | discrete_2 | discrete_3 | discrete_4 | perimeter_ring |
|---|---|---|---|---|---|
| tri_star | ✅源 | ⛔gate(三臂放双荚不真实) | ✅源 | ⛔gate | ⛔gate(叶形轮廓断带) |
| winged | ✅(外推) | ✅源 | ⛔gate(无臂) | ✅源(quad_pods) | ⛔gate(翼荚断带) |
| hex | ✅源 | ✅外推 | ✅外推 | ✅外推 | ✅源 |
| round_puck | ✅源(携带) | ✅外推 | ✅外推 | ✅外推 | ✅外推 |
| square_rounded | ✅外推 | ✅外推 | ✅源(携带) | ✅外推 | ✅外推 |

  - grille gate：`domed` ⇒ 仅 `central`（穹顶=单只中央隆起；source domed 均 central，S5/S11）。
  - **winged×discrete_4 裁定**：source map 散文 gate（L55）写 "discrete_3/4 与 ring 不上 winged"，但其**四态 cross 矩阵**（L30）明列 winged×discrete_4 = `fork quad_pods`（S8 真实采纳资产，winged 四角荚 compile 成功 + 轴断言过）。依 O5 名实注记同理（以建成资产为准、散文滞后），**采信矩阵 + 采纳资产**：winged 合法集 = {central, discrete_2, discrete_4}，gate {discrete_3, ring}。此裁定保证 S8 quad_pods source 可达（不孤立采纳样本），且结构安全（四角荚在 winged 体上有实证 fork）。
Topology target：1000-seed slot choice tuple distinct 上限 = 270（本类别离散结构轴天花板）。低于 300 时记录该类别空间上限；1000-seed 视觉 distinct 远高于 270（×5 palette ×连续 scale），但不计入 tuple。report-only，不设门。
Controlled local parameterization：body_radius_scale / body_height_scale / speaker_radius_frac / key_travel（独立，§7 范围/clamp）；deck_z / speaker_lobe_radius(equation)；deck_rise / panel_tilt(conditional 依 control_surface)；全在 `resolve_config` 求解，不破坏喇叭贴装面 / 台面基座 / 按键 origin / 键盘 clearance。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body_form→arrangement(gate)→grille(domed gate)→control_surface→keypad_shape→palette→连续 scale；顺序 independent→equation→conditional→inequality | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 上表 gate（tri_star{central,d3}；winged{central,d2,d4}；hex/round/square 全 5；domed 仅 central）；采样时约束合法值域，永不采非法组合 | 无悬空 / 无穿模 / 按键沿 −Z 或斜法向 / 喇叭 clear 键盘 |
| controlled local variation | §7 的 4 independent + 2 equation + 2 conditional + 4 inequality；全在 resolve_config clamp/派生 | 比例变化不破喇叭贴装 / 台面 / 按键 origin / 键盘 clearance / 类别身份 |
| regression overrides | none（首版不需；如后续 sweep 暴露特定失败 seed 再稀疏加，记 seed+理由）| 仅已知失败回归 |
| random sweep | seeds 0-35 首轮，0-999 成熟审计 | axis_realization + + contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form（③）| 5 | yes | yes | Planar×4 + Volumetric×1 |
| B speaker_arrangement（≡N）| 5 | yes | yes | central/d2/d3/d4/ring；受 body_form gate，全值 reachable |
| C grille_treatment（④）| 3 | yes | yes | perforated/fabric/domed(仅 central) |
| D control_surface | 3 | yes | yes | flush/raised/tilted，全 body_form 兼容 |
| keypad_shape（§8 阵列）| 2 | yes | no | 3x4/4x4；源仅两态，§8 记 |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（body_form/speaker_arrangement/speaker_count/grille_treatment/control_surface/keypad_shape）
- config_from_seed 对所有 ordinary seed 用 deterministic procedural sampling（seed=0 不特殊）
- compatibility gate 无非法组合：tri_star 只 central/discrete_3；winged 只 central/discrete_2/discrete_4；domed 只 central；采样时约束
- regression overrides 为空（或稀疏且注明理由）；主 seed domain 不是小型 curated/modulo 表
- 连续 scale（body_radius/body_height/speaker_radius_frac/key_travel）clamp，且 equation(deck_z, speaker_lobe_radius) / conditional(deck_rise, panel_tilt 依 control_surface) / inequality(喇叭 clear 键盘、键坐台面、ring clear 键盘、tilted 不穿台) 全在 resolve_config 求解，不留 builder 失败
- 关键接口：喇叭格栅凹嵌机身顶面（有支撑无岛）；台面基座嵌机身顶面；按键 cap 底浅嵌台面 well（scoped allow_overlap cap↔body_shell）
- 关键关节 type/axis/range：全部按键 PRISMATIC axis=(0,0,−1)，limit=[0,key_travel]；tilted 台面按键额外 `rpy=(panel_tilt,0,0)`（沿斜法向）；**按键是唯一非固定关节**（无 revolute/continuous/其它 fixed-child）
- multiplicity：喇叭 ×N 复用同一 Mesh，命名 speaker_grille_{i}；键盘 keypad_{r}_{c} 阵列 rows×cols
- Rule 5：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)` + 每 control_surface 型 ≥1 targeted `ctx.pose`

## Reject cases

- 新增非按键会动件（听筒 handset / 挂机叉簧 hook-switch / 翻盖 / 旋转喇叭）→ 违反 motion-safety 硬契约（本类别唯一活动件是下压按键）
- 按键非 PRISMATIC，或 flush/raised 台按键不沿 −Z、tilted 台按键不沿斜法向（`pressed[1]≤rest` 说明 rpy 座标错）
- 采到非法 (body×arrangement)：tri_star+discrete_2/4/ring、winged+discrete_3/ring、非 central+domed（gate 未拦截）
- 喇叭格栅或台面悬空（不嵌机身顶面 → 断连岛）；perf 点/织纹脱离喇叭面
- 离散喇叭撞进 front-central 键盘 console（xy-AABB 重叠，未回缩）；perimeter_ring 内径压住键盘
- 键 cap 悬空或沉到桌面（未浅嵌台面 well ±0.0025）
- 把机身做成非五形态之一 / 加听筒 → 飘向 desk phone；单喇叭无键盘无 LCD → 飘向 smart speaker
- 用小型 curated/modulo 表当主 seed domain，或只靠连续 scale/palette 撑多样性（③ body_form 必须离散出现）

## 与相邻类别的边界

- 不该混入 **台式话机 / desk phone**：desk phone 有**听筒 handset**（REVOLUTE/摘挂）+ **叉簧 hook-switch** + 曲线机身托听筒；本类别是**全双工免提盒**——无听筒、无叉簧，唯一活动件是拨号/功能**下压按键**，机身是三臂星/双翼/六边/圆饼/圆角方低矮盒。
- 不该混入 **对讲门口机 / intercom**：intercom 壁挂、单喇叭 + 摄像头 + 少量呼叫键；本类别桌面静置、多喇叭免提 + 完整电话键盘 + LCD 拨号。
- 不该混入 **桌面音箱 / smart speaker**：smart speaker 无电话键盘、无绿接/红挂键、无拨号 LCD；本类别核心身份是**电话键盘簇（数字+绿接红挂+音量）+ LCD + 多喇叭免提机身**。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。单骨架、单关节拓扑（唯一活动件=PRISMATIC 下压键）形态主导物：③ body_form（5，登记 slot）+ B speaker_arrangement（≡N，5，受 body_form gate）+ ④ C grille_treatment（3，domed 仅 central）+ D control_surface（3）+ keypad_shape（2）= gate 后 270 离散组合 + 5 palette。**winged×discrete_4 gate 裁定**：采信 source map 四态矩阵 + S8 quad_pods 采纳资产（散文 L55 滞后，同 O5 名实注记原则），winged 合法 {central,discrete_2,discrete_4}。**待模板阶段落实**：(1) slug 加入 `cli/template.py` TEMPLATE_REGISTRY（已加 `"Technology_Conference_Phone": "conference_phone"`）；(2) resolve_config 求解 §7 全部 equation/inequality/conditional；(3) 三台面型（flush/raised/tilted）各 targeted pose + sampled collision；(4) 离散喇叭复用同一 Mesh + 降密穿孔/织纹控 compile 预算。**开放问题**：keypad_shape 仅 2 candidate（源仅两态，§8 记）；round_puck/square_rounded 的部分 arrangement 与所有 grille 跨族外推，需 sweep + reviewer 复核类别忠实（勿飘向 smart speaker）。|

## 模板实现备注（可选）

- 深读参考模板（按 slot graph / 运动拓扑 / 接口选，不按类别名）：`Urban_Environment_Caster_Trolley2`（同 root-fuses-decor + parallel children + palette-per-seed + config/resolve/slot_choices/run_tests 骨架，本模板直接照它的文件结构）、`binocular`/`padlock`（memory：direct-build 范式，非 `_modular.py` assemble——本模板亦 direct build，因唯一关节是按键、无 slot-chain）。
- **compile 成本（§7.5）**：`PerforatedPanelGeometry` 布尔是成本大头（memory「container_locker PerforatedPanel boolean」）。缓解：(a) 离散 N 只喇叭**复用同一 grille Mesh**（`mesh_from_geometry` 一次、place N 次）；(b) 穿孔 pitch 放粗（≥0.008）、hole_diameter ≥0.004、corner_radius 圆盘化；(c) domed perf 点用稀疏 Sphere（≤~120 点，非 240）；(d) fabric 织纹降到 ≤~20 根 Box 或省略、以布垫 + 少量肋替代；(e) LoftGeometry 机身 segments ≤72、tri_star/hex profile samples ≤120。自报预算 **每-seed 10-25s**（重布尔类偏上界）；sweep `--compile-timeout 120`（~5x 上界，watchdog）。
- **captured/seated allow_overlap**（复刻 origin）：每按键 cap↔body_shell（`elem_a="{key}_cap"` `elem_b="body_shell"`，浅嵌 well，S1 L317-L325）；喇叭格栅 / 台面 / LCD 融入 body 同 part 无需 allow_overlap（同 part 内 visual），但若喇叭荚 surround 与机身顶面凹嵌触发 closed-pose overlap，按 elem 级 scoped allow_overlap。
- **按键 origin 单一来源**：`deck_z` = `BODY_TOP·body_height_scale + deck_rise`（Contract 3c，台面高度唯一来源）；tilted 台按键额外经 `_panel_point(u,v)` + `rpy=(panel_tilt,0,0)`（复刻 S5 L129-L135/L202-L209）。
- **stem / registry**：文件 stem `conference_phone`，registry key `Technology_Conference_Phone`（memory「arti-template new slug registry」：新 slug 必须加进 `cli/template.py` TEMPLATE_REGISTRY，importlib 文件名自动发现不够——已加）。
- **round_puck/square_rounded/跨族 grille** 为 forked_anchor（各有 fork）或 world_knowledge 外推：实现须保同 part tree（root LoftGeometry + 融合 grille/台/键）/ 同 primitive / 同按键 PRISMATIC 接口，过 Rule 4/5 sweep + reviewer 复核忠实。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D + 按键 + root | tri_star / central / perforated / flush / 4x3 键 | rec_gray-polycom-...-9bc5796c | L79-L122, L139-L155, L200-L292, L309-L421 | 全 skeleton 基线 + 中央穿孔 + flush deck + 键 cap 浅嵌 well + 全接口 |
| S2 | A/B/C | tri_star / discrete_3 / fabric | rec_a-black-tri-star-...-0672d2af | `_radial_profile` L34-L43, wings L114-L246, `_add_button`(stem+cap+legend) L135-L176 | tri_star Loft + 三织物翼 + 织纹 |
| S3 | A/B/C/D | tri_star(box) / discrete_3 / perforated / raised / 4x4 | rec_a-black-tri-star-...-fe888f0f | body L43-L60, grilles L103-L122, deck L63-L70, keys L162-L183 | 三穿孔 + raised deck + 4x4 阵列 |
| S4 | A/B/C/D | winged / discrete_2 / perforated / raised silver console | rec_a-black-conference-...-e395d9a0 | body L56-L84, pods L87-L109, console L112-L133, `add_button` L172-L217 | winged section_loft + 双荚 + 银梯台 |
| S5 | A/B/C/D + 按键 | hex / central / domed / tilted | rec_a-black-tri-lobed-...-ecc509b0 | body L57-L80/L233-L242, dome L145-L149/L246-L257, tilted console L290-L296, `_add_key`(stem+cap+legend, 斜法向) L169-L210 | hex Loft + 穹顶穿孔 + tilted 台 + 斜法向按键 |
| S6 | A/B/C/D | round_puck / central / perforated / flush(dome-conformal) | rec_conference_phone_var_round_puck | `_body_solid` L105-L141, grille L144-L155, keys L182-L196/L332-L351, tests L369-L511 | 圆饼机身 + 喇叭 clear 键盘断言 |
| S7 | A/B/C/D | square_rounded / discrete_3 / perforated / raised(slight) / 4x4 | rec_conference_phone_var_square_body | `_rounded_square_body` L36-L53, grilles L98-L117, keys L66-L68/L160-L178, tests L183-L241 | 圆角方机身 + 白+银伴随 palette |
| S8 | A/B | winged / discrete_4 | rec_conference_phone_var_quad_pods | outline+section_loft L56-L84, 4 pods L87-L117, `add_button` L180-L208, tests L277-L337 | 四角荚（winged×discrete_4 gate 裁定的采纳实证）|
| S9 | A/B/D | hex / perimeter_ring / tilted | rec_conference_phone_var_perimeter_ring | body L108-L116/L204-L212, band segs L229-L268, tilted console L299-L304, `_add_key` L138-L179, tests L386-L515 | 环带格栅 + ring clear 键盘断言 + 双色调 palette |
| S10 | A/B/D | winged / discrete_2 / flush(recessed) | rec_conference_phone_var_flush_console_winged | body L57-L85, 2 pods L88-L110, flush console L114-L128, tests L273-L331 | flush 凹台（面与机身顶共面）+ 全黑 palette |
| S11 | A/B/C/D | hex / central / domed / flush | rec_conference_phone_var_flush_console_hex | body L233-L242, dome L246-L257, flush deck L291-L296, `_add_key` L169-L210, tests L376-L477 | hex 穹顶 + flush 平台 + 直下按键断言 |
| S12 | A/B/D | tri_star(box) / discrete_3 / raised pedestal | rec_conference_phone_var_raised_console_tri | `_tri_star_body` L45-L62, deck pedestal L68-L81, grilles L114-L133, tests L199-L257 | raised 柱台（rise>0.020）+ LCD 抬高断言 |
| S13 | A/B/C/D + 按键 | tri_star(Loft) / discrete_3 / fabric / tilted wedge | rec_conference_phone_var_tilted_console_tri | `_radial_profile` L43-L51/L267-L280, fabric wings L299-L319, wedge console L156-L194, `_add_button`(斜法向) L197-L245, tests L395-L490 | tri_star Loft(模板取此实现) + 倾斜楔台 + 斜法向按键断言 dy≈travel·sinθ |
