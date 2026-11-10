# Hurricane Lantern Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `hurricane_lantern` |
| template path | `agent/templates/Light_Latern.py` |
| test path | `tests/agent/test_hurricane_lantern_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13（1 parent baseline + 12 picture-subcat forks） |
| read_count | 13 |
| read_scope | parent baseline 加全部 12 个 fork 变体的 `revisions/rev_000001/model.py` 全读 |
| samples_adopted_as_module_sources | 13 |
| source_index_policy | only adopted module sources are indexed below |

**Dataset-root caveat**：本类别没有独立的 promoted dataset 目录。parent 是 picture-pipeline 生成的 5 星 hurricane lantern，12 个变体均 fork 自它、`collections=['workbench']`（workbench-only，未 promote，继承 `category_slug = hurricane_lantern_with_swinging_bail_handle`），并绑入 `Light__Latern` picture 子类分片。所有源码引用都根植于 `articraft_data` 仓库，按 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly` 引用，行号取自各 fork 的实际文件，而非某个统一 dataset 目录。

- parent baseline（三槽同源 + guard N=2 baseline）：`rec_model-a-vintage-hurricane-kerosene-lantern-about_20260610_081109_101773_5da4cb46`。
- Slot A type forks：`rec_lantern_var_typeA_railroad_cage`、`rec_lantern_var_typeA_candle_panel`、`rec_lantern_var_typeA_tubular_coldblast`。
- Slot B cap forks：`rec_lantern_var_topB_flat_pierced_crown`、`rec_lantern_var_topB_conical_louver`、`rec_lantern_var_topB_peaked_roof`。
- Slot C carry forks：`rec_lantern_var_carryC_top_ring`、`rec_lantern_var_carryC_folding_strap`、`rec_lantern_var_carryC_hook_hanger`。
- guard multiplicity forks（copy-logic 源）：`rec_lantern_var_guardN_2_loop`、`rec_lantern_var_guardN_6`、`rec_lantern_var_guardN_10`。

## 核心身份

Hurricane lantern 是手提式燃油（煤油）风灯：grounded 的 `lantern_body` 根件承载一只 stepped fount 燃料座 + 透光玻璃罩光腔（barrel globe / 方腔 / 护笼罩）+ 内部 burner/wick/flame，顶部一只排烟通风冠，并有一件顶部或侧部的提携件（提梁 / 吊环 / 折叠带 / S 钩）。核心运动语义固定为两条非 fixed joint：

- carry 提携件相对 body 的 REVOLUTE（轴和范围随 Slot C module 变化）；
- `fount_to_wick_knob` 的 CONTINUOUS 调芯旋钮（轴 = 局部 +Y，全变体不变，属固定附件，不进 slot）。

边界（不该混入）：
- 不是固定台灯/吊灯：必须有真实可摆动的提携件 + 可旋调芯旋钮。
- 不是不透光实体外壳：Slot A 光腔必须保留透光玻璃语义（globe / pane / 罩内可见 flame）。
- 不是 windmill / waterwheel：没有连续主轴驱动的旋转主体；CONTINUOUS 只在小调芯旋钮上。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S0 | `rec_...5da4cb46`（parent） | `data/records/rec_model-a-vintage-hurricane-kerosene-lantern-about_20260610_081109_101773_5da4cb46/revisions/rev_000001/model.py:L84-L320` | baseline body/cap/bail/knob + 手镜像 side-tube N=2 |
| S1 | `rec_lantern_var_typeA_railroad_cage` | `data/records/rec_lantern_var_typeA_railroad_cage/revisions/rev_000001/model.py:L112-L155` | 圆柱直立钢丝护笼光腔（Slot A） |
| S2 | `rec_lantern_var_typeA_candle_panel` | `data/records/rec_lantern_var_typeA_candle_panel/revisions/rev_000001/model.py:L153-L179` | 方形烛笼角柱+横档夹平玻璃（Slot A） |
| S3 | `rec_lantern_var_typeA_tubular_coldblast` | `data/records/rec_lantern_var_typeA_tubular_coldblast/revisions/rev_000001/model.py:L106-L129` | 粗冷风管喂高烟囱大玻璃罩（Slot A） |
| S4 | `rec_lantern_var_topB_flat_pierced_crown` | `data/records/rec_lantern_var_topB_flat_pierced_crown/revisions/rev_000001/model.py:L85-L114` | 低矮平顶穿孔冠（Slot B） |
| S5 | `rec_lantern_var_topB_conical_louver` | `data/records/rec_lantern_var_topB_conical_louver/revisions/rev_000001/model.py:L84-L107` | 高锥百叶烟囱、敞口喉（Slot B） |
| S6 | `rec_lantern_var_topB_peaked_roof` | `data/records/rec_lantern_var_topB_peaked_roof/revisions/rev_000001/model.py:L107-L136` | 多面尖顶塔式宝顶 + 顶尖饰（Slot B） |
| S7 | `rec_lantern_var_carryC_top_ring` | `data/records/rec_lantern_var_carryC_top_ring/revisions/rev_000001/model.py:L283-L310` | 顶部竖轴旋转吊环（Slot C） |
| S8 | `rec_lantern_var_carryC_folding_strap` | `data/records/rec_lantern_var_carryC_folding_strap/revisions/rev_000001/model.py:L289-L315` | 侧面折叠提带（Slot C） |
| S9 | `rec_lantern_var_carryC_hook_hanger` | `data/records/rec_lantern_var_carryC_hook_hanger/revisions/rev_000001/model.py:L318-L334` | 顶部旋转 S 钩吊挂（Slot C） |
| S10 | `rec_lantern_var_guardN_2_loop` | `data/records/rec_lantern_var_guardN_2_loop/revisions/rev_000001/model.py:L105-L121` | guard 循环化 copy-logic（N=2） |
| S11 | `rec_lantern_var_guardN_6` | `data/records/rec_lantern_var_guardN_6/revisions/rev_000001/model.py:L135-L152` | guard wire + 上下 lug 接口（N=6） |
| S12 | `rec_lantern_var_guardN_10` | `data/records/rec_lantern_var_guardN_10/revisions/rev_000001/model.py:L107-L127` | `GUARD_COUNT` 参数化密集护笼（N=10） |

## 槽位 + 候选模块表

### Slot A：type / 光腔与挡风层主形（被 cap/carry 承托的主体）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `hurricane_side_tube`（基线） | `rec_...5da4cb46` | L105-L162 | eligible if compatible | barrel glass globe + 两根 curved 侧进气管（`_side_tube_solid` 手镜像）+ `_ear_solid` 枢轴耳；globe `_globe_solid` 罩住 burner/flame |
| `railroad_cage` | `rec_lantern_var_typeA_railroad_cage` | L112-L155 | eligible if compatible | 圆柱形直立钢丝护笼（`_guard_wire_solid` 循环 + 上下 `_guard_ring_solid` 圆环）罩住玻璃罩，取代侧管 |
| `candle_panel` | `rec_lantern_var_typeA_candle_panel` | L153-L179 | eligible if compatible（与 side-guard multiplicity 互斥，方腔无圆周护笼位） | 方形烛笼光腔，四面平玻璃 `_glass_pane_solid` 由 `_corner_post_solid` 角柱 + `_frame_rail_solid` 横档夹持 |
| `tubular_coldblast` | `rec_lantern_var_typeA_tubular_coldblast` | L106-L129 | eligible if compatible | 一对粗外冷风管 `_draft_tube_solid` 喂更高烟囱（BODY_TOP_Z=0.286）、更大玻璃罩 |

### Slot B：cap / 顶部排烟冠

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `domed_vent_cap`（基线） | `rec_...5da4cb46` | L84-L102 | eligible if compatible | 穹顶烟囱 `_top_assembly_solid` + 穿孔通风带（`vent_slot_{i}` ×12 循环）+ 外翻顶盘 |
| `flat_pierced_crown` | `rec_lantern_var_topB_flat_pierced_crown` | L85-L114 | eligible if compatible | 低矮平顶穿孔冠（`_top_assembly_solid` 重写，BODY_TOP_Z=0.260）+ 短筒领 + 中央 chimney 开口 |
| `conical_louver` | `rec_lantern_var_topB_conical_louver` | L84-L107 | eligible if compatible | 高瘦锥形百叶烟囱（funnel profile）、敞口喉 + 12 斜百叶 `louver_slot`/`louver_lip` |
| `peaked_roof` | `rec_lantern_var_topB_peaked_roof` | L107-L136 | eligible if compatible | 多面尖顶/塔式宝顶（`_tent_roof_solid` polygon→polygon loft，TENT_ROOF_SIDES/EAVE_R/PEAK_R）+ `_top_finial_solid` 顶尖饰 |

### Slot C：carry / 提携件（本槽决定第二条非 fixed REVOLUTE joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `swinging_bail`（基线） | `rec_...5da4cb46` | L194-L296 | eligible if compatible | 顶部跨弧提梁 `_bail_solid`，part `bail_handle`，joint `body_to_bail_handle` REVOLUTE，axis=X(1,0,0)，±100°，绕侧管/cage ear boss 摆动 |
| `top_swivel_ring` | `rec_lantern_var_carryC_top_ring` | L283-L310 | eligible if compatible | 固定顶部旋转吊环，part `carry_ring`（`_carry_ring_wire_geometry`），joint `body_to_carry_ring` REVOLUTE，axis=Z(0,0,1)，±180°（CARRY_LIMIT=π），绕竖轴自由打转 |
| `folding_side_strap` | `rec_lantern_var_carryC_folding_strap` | L289-L315 | eligible if compatible | 侧面折叠提带，part `side_strap_handle`（hinge/barrel/loop/tab solids），joint `body_to_side_strap` REVOLUTE，axis=−Y(0,−1,0)，0..112°（STRAP_LIMIT），绕铰链向上翻折 |
| `swivel_hook_hanger` | `rec_lantern_var_carryC_hook_hanger` | L318-L334 | eligible if compatible | 顶部固定 eye ring（`top_eye_ring`，Y-Z 平面）上穿一只闭合提环 part `carry_hanger_ring`（`_hanger_ring_geometry`，与 eye ring 链节穿插），joint `body_to_hanger_ring` REVOLUTE，axis=Y(0,1,0)，±45°（HANGER_SWING_LIMIT），0°=竖直立起、左右摆动 |

## 槽位图（slot graph）

pattern: `mixed`（type/cap/carry 三个固定 named slot + side-guard 链式 multiplicity 轴）

```text
[Slot A type / light-chamber]  --top rim ring (z≈0.205, Z-axis center)--> [Slot B cap / vent]
[Slot A type / light-chamber]  --carry REVOLUTE pivot (ear boss / chimney rim / side hinge)--> [Slot C carry]
[Slot A type / light-chamber]  --fount wall socket (z≈0.055, +Y)--> {wick_knob CONTINUOUS, 固定附件}
[Slot A type / light-chamber]  --N× guard members (FIXED weld, no joint)--> [guard multiplicity axis]
```

说明：
- Slot A 是承载主体（root `lantern_body` 的主 visual），Slot B 与 Slot C 都挂在 Slot A 上，二者互不依赖（parallel children on a common chassis）。
- Slot A → Slot B：mating ring = Slot A 上领顶 rim（z≈0.205），anchor = Z 轴中心；cap 底缘坐在上领顶环，连接为 FIXED（cap 烧结进 body 还是单独 weld 由 module 决定，无 joint）。
- Slot A → Slot C：carry 提携件经 ear boss / chimney 顶领 / 侧壁铰链座提供枢轴；joint origin 贴各自承托面，consumer joint = REVOLUTE（轴/范围见 Slot C 表）。这是模板暴露的第二条非 fixed joint。
- Slot A → wick_knob：fount 壁 socket（scoped allow_overlap），CONTINUOUS，axis=+Y，origin=(0,KNOB_BASE_Y,KNOB_Z)；全变体不变，不进 slot，不计入拓扑组合。
- guard multiplicity 轴：N 根 guard member 焊在 Slot A body 上（FIXED，无 joint），只增减固定支撑数。与 `candle_panel`（方腔）互斥。

## 部件（Parts）
| part | slot | visual_count | 描述 | 来源 |
|---|---|---:|---|---|
| `lantern_body`（root） | A/B + guard | ~6-30 | grounded 主体：fount + 光腔（globe/pane/cage）+ 上下领 + cap + N× guard + 内部 burner/wick/flame + vent slots | S0-S6/S10-S12 |
| `bail_handle` / `carry_ring` / `side_strap_handle` / `carry_hanger_ring` | C | 1-3 | 唯一的可摆动提携件（互斥 4 选 1） | S0/S7-S9 |
| `wick_knob` | 固定附件 | 2 | 调芯旋钮 + off-axis index nub，CONTINUOUS（全变体保留） | S0 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `body_to_<carry>` | REVOLUTE | A.lantern_body | C.carry part | X / Z / −Y（随 module） | ±100° / ±180° / 0..112° / ±85° | 唯一暴露的提携 REVOLUTE，由 Slot C 决定 |
| `fount_to_wick_knob` | CONTINUOUS | A.lantern_body | wick_knob | `(0,1,0)` +Y | unbounded | 固定调芯旋钮，所有变体不变；不进 slot |

## 每槽位 Module Emits / Interfaces

### Slot A / module `hurricane_side_tube`（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `green_body_shell`（fount+领+两侧管+ear union）、`globe_glass`、`burner_wick`、`flame` | S0 / model.py:L131-L162, L245-L265 |
| internal joints | 无（光腔全部 fixed 进 body 根件） | S0 / model.py:L131-L143 |
| upstream interface | grounded 于 z=0；fount 壁向 wick_knob 提供 +Y socket（z≈0.055） | S0 / model.py:L50-L67, L317 |
| downstream interface | 上领顶 rim（z≈0.205）承 cap；ear boss（world (0,0,PIVOT_Z=0.212)）承 carry 枢轴 | S0 / model.py:L122-L128, L84-L88 |

### Slot A / module `railroad_cage`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `green_body_shell`、`guard_rings`、`guard_wire_{i}`（×N 循环）、`globe_glass`、burner/flame | S1 / model.py:L112-L155, L264-L277 |
| internal joints | 无；护笼为 FIXED weld | S1 / model.py:L122-L130 |
| upstream interface | 下领 `GUARD_LOWER_Z=0.108`、上领 `GUARD_UPPER_Z=0.205` 承 guard wire 两端 | S1 / model.py:L52-L53, L112-L130 |
| downstream interface | ear boss 焊在 upper guard ring 承 carry；上领顶承 cap | S1 / model.py:L133-L140 |

### Slot A / module `candle_panel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `green_body_shell`、`corner_post_{i}`（×4）、`frame_rail_{level}_{side}`、`glass_pane_{i}`（×4）、burner/flame | S2 / model.py:L153-L179, L264-L325 |
| internal joints | 无；角柱/横档/玻璃全 FIXED | S2 / model.py:L161-L179 |
| upstream interface | 光腔区间 CHAMBER_Z0=0.108..CHAMBER_Z1=0.205 坐在上下领之间 | S2 / model.py:L48-L49 |
| downstream interface | 上领顶承 cap；ear boss 承 carry。**与 guard multiplicity 互斥** | S2 / model.py:L138-L150 |

### Slot A / module `tubular_coldblast`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fount_shell`、`lower_globe_collar`、`tall_chimney_cap`、`draft_tube_{i}`（×2 粗管）、`pivot_ear_{i}`、`globe_glass` | S3 / model.py:L106-L129, L261-L298 |
| internal joints | 无；冷风管 FIXED | S3 / model.py:L106-L129 |
| upstream interface | 更高 BODY_TOP_Z=0.286、更大 globe；fount socket 同基线 | S3 / model.py:L40, L155-L177 |
| downstream interface | pivot_ear 承 carry；上领承更高 cap | S3 / model.py:L131-L150 |

### Slot B / module `domed_vent_cap`（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `_top_assembly_solid`（穹顶+vent band+顶盘，烧结进 green_body_shell）、`vent_slot_{i}`（×12 dark box 循环） | S0 / model.py:L84-L102, L266-L277 |
| internal joints | 无 | S0 / model.py:L84-L102 |
| upstream interface | 底缘坐上领顶 rim（z≈0.205） | S0 / model.py:L84-L88 |
| downstream interface | dome 顶（BODY_TOP_Z=0.278）为 bail 上摆净空参照 | S0 / model.py:L96-L99 |

### Slot B / module `flat_pierced_crown`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 低平 crown（`_top_assembly_solid` 重写，中央 chimney 开口）+ `vent_slot_{i}`（×12 cut+dark insert） | S4 / model.py:L85-L114, L288 |
| internal joints | 无 | S4 / model.py:L85-L114 |
| upstream interface | 底缘坐上领顶；顶面 BODY_TOP_Z=0.260（低矮） | S4 / model.py:L40, L85-L96 |
| downstream interface | 矮顶改变 carry 上摆净空 | S4 / model.py:L95-L96 |

### Slot B / module `conical_louver`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 高锥 funnel（`_top_assembly_solid`，敞口喉）+ `louver_slot_{i}`/`louver_lip_{i}`（×12 斜百叶 + 雨檐） | S5 / model.py:L84-L107, L270-L295 |
| internal joints | 无 | S5 / model.py:L84-L107 |
| upstream interface | funnel 下缘（z≈0.222）坐上领 | S5 / model.py:L94-L98 |
| downstream interface | 锥顶 BODY_TOP_Z=0.278 为 carry 净空参照 | S5 / model.py:L97-L98 |

### Slot B / module `peaked_roof`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tent_roof_cap`（polygon→polygon loft）、`top_finial`、上领领口（`_top_assembly_solid`）、`vent_slot_{i}` | S6 / model.py:L107-L136, L285-L319 |
| internal joints | 无 | S6 / model.py:L107-L136 |
| upstream interface | 多面屋檐 TENT_EAVE_Z=0.253 坐上领顶 rim | S6 / model.py:L48-L51, L100-L101 |
| downstream interface | finial 顶 BODY_TOP_Z=0.278 为 carry 净空参照 | S6 / model.py:L118-L136 |

### Slot C / module `swinging_bail`（基线，owns 第二条非 fixed REVOLUTE）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bail_handle`：`bail_wire` 弧 + 两端 pin | S0 / model.py:L194-L214, L280-L285 |
| internal joints | `body_to_bail_handle` REVOLUTE，axis=X(1,0,0)，±100° | S0 / model.py:L286-L296 |
| upstream interface | joint origin = world (0,0,PIVOT_Z=0.212)，pin 坐进 ear boss（scoped allow_overlap） | S0 / model.py:L291, L335-L341 |
| downstream interface | 无（终端提携件） | S0 / model.py:L280-L296 |

### Slot C / module `top_swivel_ring`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carry_ring`：post + base + `swivel_ring_wire` | S7 / model.py:L196-L218, L283-L300 |
| internal joints | `body_to_carry_ring` REVOLUTE，axis=Z(0,0,1)，±π | S7 / model.py:L301-L310 |
| upstream interface | joint origin 贴 chimney 顶领；绕竖轴自由打转 | S7 / model.py:L301-L308 |
| downstream interface | 无 | S7 / model.py:L283-L310 |

### Slot C / module `folding_side_strap`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `side_strap_handle`：`strap_loop`/`strap_tab`/`strap_barrel`（+ body 侧 `_side_strap_hinge_solid`） | S8 / model.py:L122-L141, L204-L224, L289-L303 |
| internal joints | `body_to_side_strap` REVOLUTE，axis=−Y(0,−1,0)，0..112° | S8 / model.py:L305-L315 |
| upstream interface | barrel 绕侧壁铰链座；origin 贴 hinge 轴 | S8 / model.py:L305-L312 |
| downstream interface | 无 | S8 / model.py:L289-L315 |

### Slot C / module `swivel_hook_hanger`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定件 `top_eye_ring`（body inline，Y-Z 平面 torus）+ 摆动件 `carry_hanger_ring`：`hanger_ring_wire`（`_hanger_ring_geometry`，闭合提环，下弧穿过 eye ring 孔=链节穿插） | S9 / model.py:L198-L233, L318-L322 |
| internal joints | `body_to_hanger_ring` REVOLUTE，axis=Y(0,1,0)，±45°（0°=竖直立起） | S9 / model.py:L324-L334 |
| upstream interface | joint origin=eye ring 中心；左右摆动（正面视角内 X-Z 平面摆动） | S9 / model.py:L324-L332 |
| downstream interface | 无 | S9 / model.py:L318-L334 |

### 固定附件 / `wick_knob`（不进 slot，所有变体保留）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knob_knurled_disk` + `knob_index_nub`（off-axis，证明 continuous 旋转） | S0 / model.py:L217-L230, L299-L311 |
| internal joints | `fount_to_wick_knob` CONTINUOUS，axis=+Y(0,1,0)，无限程 | S0 / model.py:L312-L320 |
| upstream interface | origin=(0,KNOB_BASE_Y=0.0565,KNOB_Z=0.055)，stem 穿 fount 壁（scoped allow_overlap） | S0 / model.py:L317, L342-L348 |
| downstream interface | 无 | S0 / model.py:L299-L320 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `type_style` | enum | `hurricane_side_tube` / `railroad_cage` / `candle_panel` / `tubular_coldblast` | `hurricane_side_tube` | choice | 由 deterministic procedural sampler 选择 | Slot A table |
| `cap_style` | enum | `domed_vent_cap` / `flat_pierced_crown` / `conical_louver` / `peaked_roof` | `domed_vent_cap` | choice | 由 sampler 选择；`tubular_coldblast` 偏向高 cap | Slot B table |
| `carry_style` | enum | `swinging_bail` / `top_swivel_ring` / `folding_side_strap` / `swivel_hook_hanger` | `swinging_bail` | choice | 由 sampler 选择；决定第二条非 fixed REVOLUTE 的轴/范围 | Slot C table |
| `guard_count` | int | `[2, 16]` | 2 | conditional | 仅当 `type_style ∈ {hurricane_side_tube, railroad_cage, tubular_coldblast}` 才启用；`candle_panel` 时强制无 guard 轴 | S10-S12 / model.py（见 Multiplicity） |
| `vent_slot_count` | int | `[8, 16]` | 12 | independent | cap module-local 通风孔/百叶数，绕 Z 等角 | S0 L267, S5 L270 |
| `body_height_scale` | float | `[0.92, 1.12]` | 1.0 | independent | 缩放 BODY_TOP_Z（基线 0.278；coldblast 0.286；flat crown 0.260） | S0 L41 / S3 L40 / S4 L40 |
| `globe_radius_scale` | float | `[0.9, 1.15]` | 1.0 | equation | `= f(type_style)`：coldblast 偏大、candle_panel 改 span 不改 radius；随 type 派生不独立采样 | S0 L146-L162 / S3 L155-L177 |
| `guard_radius_scale` | float | derived | 1.0 | inequality | `GUARD_R · scale > globe_max_radius + wire_r`（护笼必须包住玻璃罩不穿模）；违反则按比例回缩 | S11 L47 / S12 L107-L127 |
| `carry_pivot_z` | float | derived | PIVOT_Z=0.212 | equation | `= top_rim_z(cap_style) 附近`；origin 贴 carry 承托面，不独立采样 | S0 L291 / S7-S9 joint origin |
| (—) | constraint | — | — | inequality | carry 上摆 closed/open pose 不得穿 cap：`bail_apex(q) clearance ≥ 0` 对 BODY_TOP_Z(cap)；违反则缩 BAIL_RISE 或拒绝重采 | S0 L416-L427 / interface |

## Multiplicity / Copy Logic

本类有 **1 根 multiplicity 轴**：side guard / 侧管护笼。

- `count_param`：`guard_count`
- `N_range`：`[2, 16]`（模板采样域；真实风灯护笼竖丝常 2–12，留余量到 16）。N 样本已覆盖 `{2 → guardN_2_loop, 6 → guardN_6, 10 → guardN_10}`。
- sampling domain：加权采样，小 N 高频（2–6 偏多），大 N（>10）稀有尾部。
- copied object：单根竖直 guard member / cage wire——`_guard_member_solid(angle)`（S10 / model.py:L105-L121，curved 侧管 sweep 后旋转就位）或 `_guard_wire_solid()`（S11 / model.py:L135-L152，含 bottom_lug + top_lug 两端略插入下/上绿领作真实固定支撑）。
- naming：`guard_member_{i}`（n2 loop）或 `guard_wire_{i}`（n6、n10），`for i in range(N)` 循环发射。
- placement：绕 Z 等角分布在玻璃罩外，`ang = 2.0*math.pi*i/N`，通过 `Origin(rpy=(0,0,ang))`（S11 L287-L294 / S12 L288-L295）或 solid `.rotate(...,angle)`（S10 L119-L121）摆位。
- joint policy：**无 joint** —— guard 是焊在 `lantern_body` 根件上的 FIXED 结构 visual（夹在下绿领 z≈0.102 与上领/`_top_assembly_solid` z≈0.206 之间），multiplicity 轴只增减固定支撑数，不产生新自由度。
- source/gating：copy-logic 源码取自 **三个 loop 变体（guardN_2_loop / guardN_6 / guardN_10）**，而非 parent。parent 基线 N=2 是手写镜像（`tube_r` + `tube_r.mirror("YZ")`，S0 / model.py:L131-L143），未循环化；guardN_2_loop 才把它重写成 `guard_member_{i}` 循环（S10 L249-L257），guardN_6/10 进一步参数化（`GUARD_COUNT`，S12 L48）。**与 `candle_panel` 互斥**（方腔无圆周护笼位）：sampler 选中 candle_panel 时 guard_count 轴关闭。

## 拓扑多样性审计

总组合数：`4 type × 4 cap × 4 carry = 64` module 组合；叠加 guard multiplicity 轴（N 至少 3 个采样档 {2,6,10}，模板域 [2,16]）后远超 64。
（candle_panel × guard 轴互斥会扣掉一小部分跨格组合，但 ≥10 门槛仍轻松满足。）

理由：carry slot 独立改变 REVOLUTE 轴模式（X / Z / −Y / ±range 四种），type slot 改变光腔部件树（侧管 / 圆护笼 / 方腔角柱+玻璃 / 粗冷风管），cap slot 改变顶部部件与 vent 模式，guard 轴改变 FIXED 复制数；任一维单独切换即产生 distinct 拓扑，4×4×4 已远超 10。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对普通 seed 先选 type（Slot A），再按 type 兼容性选 cap、carry 与 guard_count；`seed=0` 不特殊。compatibility gating：candle_panel 时关闭 guard_count 轴；tubular_coldblast 偏向高 cap（domed/conical/peaked），避免高烟囱配低 flat crown 比例失衡；carry origin 按所选 cap 顶领高度派生，避免提携件穿 cap。少量 regression overrides 默认无。random sweep 跑 0、0-4、0-19、0-49 cumulative，maturity 跑 0-999 看 与 contract failures。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 64 module 组合 × guard N 采样档按该口径观察。低于 300 时说明类别天然组合上限、guard_count 档位或互斥 gating 原因。
Controlled local parameterization：初版应包含 `body_height_scale`、`globe_radius_scale`、`guard_radius_scale`、`vent_slot_count`、`carry_pivot_z`，全部在 `resolve_config` 内 clamp / 派生（见第 7 节约束类型）：先采 independent（body_height_scale、vent_slot_count）→ 按 equation 派生（globe_radius_scale、carry_pivot_z）→ 用 inequality 投影/回缩（guard_radius 包络、carry 上摆净空）→ conditional（guard_count 随 type）。这些 scale 不破坏 InterfaceSpec / MatingContract / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | type→cap→carry→guard_count 顺序，加权 choice，小 N 偏多 | slot_choices_for_seed matches build choices |
| compatibility matrix | candle_panel 互斥 guard 轴；coldblast 偏高 cap；carry origin 派生自 cap 顶领 | no floating carry, cap/carry collision, guard 穿玻璃罩, bulky module |
| controlled local variation | body_height_scale / globe_radius_scale / guard_radius_scale / vent_slot_count / carry_pivot_z，全程 clamp/derive | 比例变化不破坏接口、净空、joint origin、类别 identity |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初验，0-999 maturity | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A type | 4 | yes | yes | |
| B cap | 4 | yes | yes | |
| C carry | 4 | yes | yes | |

## Validator
- slot_choices_for_seed returns implemented module names（type/cap/carry + guard_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility gating prevents illegal combos：candle_panel × guard_count 互斥；carry origin 必贴所选 cap 顶领
- 必须有 grounded（z≈0）lantern_body、透光玻璃光腔（globe/pane）、内部 burner/wick/flame、顶部 vent cap
- 唯一暴露的提携 REVOLUTE 必须接触真实 body 承托面（ear boss / chimney rim / side hinge），轴与所选 carry module 一致
- `fount_to_wick_knob` CONTINUOUS 必存在、axis≈+Y、无限程、off-axis nub 半转扫过轴线
- guard members 为 FIXED weld（无 joint），两端坐进上下绿领，绕 Z 等角；N 与 guard_count 一致
- controlled local scale params 在 `resolve_config` 内 clamp/derive（globe/guard 包络、carry 净空），不留到 builder 失败
- captured-pin / knob-stem overlap 用 element-scoped allow_overlap 声明

## Reject cases
- carry 提携件悬空或用不可见接口盘连接 body。
- 没有可旋 wick_knob，或把它做成 REVOLUTE/FIXED（失去调芯 continuous 语义）。
- 光腔做成不透光实体，罩内看不到 flame（不再读作 lantern）。
- 把 side guard 整成可动护笼（加 joint）——应为 FIXED 支撑。
- guard members 做成未连接的独立 FIXED 漂浮件，或穿透玻璃罩。
- 同时挂两件提携件（如 bail + ring），carry slot 必须互斥单选。
- candle_panel 仍强行加圆周 guard 轴（方腔无护笼位）。
- cap 与 carry 在 closed/open pose 穿模（提梁上摆撞穿 dome/finial）。

## 与相邻类别的边界
- 不该混入：`table_lamp` / `pendant_lamp`（固定灯具，无可摆动提携件 + 无可旋调芯旋钮）。
- 不该混入：`candle_holder` / `oil_lamp_open`（无玻璃挡风罩 + vent cap 的封闭风灯结构）。
- 不该混入：`windmill` / `waterwheel`（有连续主轴驱动的旋转主体；本类 CONTINUOUS 只在小调芯旋钮上）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；workbench-only picture-subcat forks（rooted in articraft_data）；等待人工审核 |

## 模板实现备注（可选）
- guard multiplicity 的 copy-logic 取自 guardN_2_loop / guardN_6 / guardN_10 三个 loop 变体，不取 parent 手镜像。
- guardN_6 的 `_guard_wire_solid` 含 bottom_lug/top_lug，是 guard↔body MatingContract 的实现参考（两端坐进上下绿领）。
- carry pin / wick_knob stem 的 overlap 需 element-scoped allow_overlap（参照 parent run_tests L335-L348）。
- candle_panel × guard 轴互斥；bail+ring 双提携件互斥——均留 compatibility matrix 裁决，不进 seed domain。
