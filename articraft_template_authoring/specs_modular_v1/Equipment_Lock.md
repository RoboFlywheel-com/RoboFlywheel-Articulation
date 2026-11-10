# padlock — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `padlock` |
| 大类/小类 | `Equipment/Lock` |
| source map | `articraft_data/picture_expansion/template_source_maps/Equipment__Lock.md` |
| parent A (picture) | `rec_build-a-realistic-articulated-3d-model-of-a-lock_20260609_180057_850280_fa3217d6` ← `picture/Equipment/Lock/001.png` (brass keyed padlock) |
| parent B (picture) | `rec_build-a-realistic-articulated-3d-model-of-a-lock_20260609_180101_520334_f96f0b30` ← `picture/Equipment/Lock/002.png` (4-dial combination padlock) |
| record naming note | converged variants are stored as `rec_lock_var_*`; record 大类/小类 = `Equipment/Lock` (slug `padlock` ≠ picture 小类 name `Lock`) |
| template path | `agent/templates/Equipment_Lock.py` |
| test path (optional) | `tests/agent/test_padlock_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel children hung off a root body + a multiplicity axis on the dial stack) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 parents + 6 `rec_lock_var_*` variants) |
| source_index_policy | only adopted module sources are indexed below |

**共享结构（所有 8 个样本）**：root part = `body`，承载一个释放运动的 `shackle`（或等价的 `hasp_bar`），外加前面板的 access 表征（keyway 或 dial 窗）。释放运动总是先 PRISMATIC（U-shackle 抬升 +Z，或 hasp 滑移 +X），长腿/keeper 保留插入（retained insertion）。body 为唯一 root，所有 access 视觉/dial 都直接挂到 body。

**两条不兼容的 kinematic spine（决定 compatibility matrix）**：

- **Keyed family（parent A + laminated + discus + shrouded + dust_cover）**：body 用 `cq.Workplane("XY").box(...)`（或 discus 的旋转圆柱），顶面打两孔捕获 shackle 双腿；shackle 在 **body frame** 中 author（`makeTorus` 半环 + 两直腿），`body_to_shackle` 原点 `(0,0,0)`、axis +Z。前面有 keyway 圆盘 + 暗 slot。
- **Combo family（parent B + straight_bar + three/five_dials）**：body 用 `cq.Workplane("XZ").polyline(...)` 八边形 orange shell，前面铣 dial 窗 pocket + 黑 faceplate + bezel + 角铆钉 + 内部 dial 轴；shackle 在 **long-leg local frame** author（`revolve` 半环 crown），`body_to_shackle` 原点 `(-LEG_X,0,TOP_Z)`、axis +Z；N 个 dial 各 CONTINUOUS about X，竖直堆叠。

**逐源差异**：
- parent A `fa3217d6`：rect brass body，长 U shackle（arch 高于 body ~72mm），keyway disc+slot，单 PRISMATIC。
- parent B `f96f0b30`：orange/black armored body，4 dial stack（CONTINUOUS×4），短 U shackle revolve crown，PRISMATIC。
- `rec_lock_var_laminated_body`：rect body 换成 5 层 plate 堆叠 + 4 个 through-rivet（双面 proud），shackle/keyway 不变。
- `rec_lock_var_round_disc_body`：body 换成旋转圆柱 discus（X/Z span≈直径、Y 薄），bore 在弧面顶；shackle/keyway 不变。
- `rec_lock_var_shrouded_shackle`：keyed body 顶加两块抬高 shoulder（shroud），短 shackle；引入 `shackle_lift`（PRISMATIC 帧）+ `shackle_rotate`（REVOLUTE about +Z 绕保留长腿）二段释放。
- `rec_lock_var_straight_bar_shackle`：combo body，U-shackle 换成直 hasp bar，沿 +X 滑移（`body_to_hasp` PRISMATIC axis +X），两 guide bracket 保留；dial stack 不变。
- `rec_lock_var_keyway_dust_cover`：keyed body + 长 shackle（带 lift+rotate 二段）+ 新增 `dust_cover`（REVOLUTE about -X 的铰接盖）遮 keyway。
- `rec_lock_var_three_dials` / `rec_lock_var_five_dials`：与 combo parent 同构，仅 `N_DIALS` = 3 / 5（dial 数 multiplicity 证据），其余 helper 完全一致；five_dials 把 `DIAL_STACK_CZ` 0.032→0.034 以容纳更高的堆叠。three_dials 另外多一个 `_shackle_boss_rings` 视觉（body 顶 bore 周围的小 collar）。

## 核心身份

padlock = 一个独立锁体（`body`，root），顶部或侧面携带一个**释放运动的可动闩**（U-shackle 抬升，或直 hasp bar 滑移），并在前面板呈现一种 **access 机制**（钥匙孔 keyway，或可旋转数字 dial 组合栈）。defining motion 永远是 shackle/hasp 的释放行程（PRISMATIC 主轴），长腿/keeper 在全行程仍保留插入。成熟域是手持便携挂锁尺度（body 量级 4–6cm）。

**不该混入**：固定在门/容器上的锁（门锁、保险箱、locker 的内置锁）——padlock 是 standalone、可拆卸、有暴露 shackle 的便携锁，不带门板/箱体/铰接门。也不该混入纯装饰钥匙串或无释放运动的实心锁形挂件。

## 槽位 + 候选模块表

三个 slot，全部挂到共同 root `body`。Slot A 决定 body shell + 它隐含的 kinematic family（keyed vs combo）；Slot B 决定释放闩形态；Slot C 决定 access 表征 + 可能的额外 access 运动。family 兼容性在第 9 节 compatibility matrix 中 gate。

### Slot A：body shell

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rect_brass_body | rec_build-...-lock_...850280_fa3217d6 (parent A) | L62-L81 (`_body_shape`) | eligible if compatible | XY box brass block，顶面两 bore 捕获 shackle 双腿，竖边 fillet。keyed family root。|
| armored_combo_body | rec_build-...-lock_...520334_f96f0b30 (parent B) | L96-L124 (`_orange_body_shell`) + L226-L231 (`_build_body_mesh_orange`) | eligible if compatible | XZ polyline 八边形 orange shell，前面 dial 窗 pocket，顶面 shackle bore。combo family root，承载 faceplate/bezel/rivets/axles。|
| laminated_steel_body | rec_lock_var_laminated_body | L88-L101 (`_plate_shape`) + L104-L139 (`_rivet_shape`) | eligible if compatible | keyed body 换成 5 层 plate 堆叠（沿 Y 站位）+ 4 through-rivet 双面 proud；part tree 多出 `plate_i`×5、`rivet_i`×4 视觉。|
| round_discus_body | rec_lock_var_round_disc_body | L67-L90 (`_body_shape`) | eligible if compatible | keyed body 换成旋转圆柱 discus（X/Z span≈直径、Y 薄），弧面顶 bore；圆形 front 面承载 keyway。|

### Slot B：shackle form / protection

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tall_u_shackle | rec_build-...-lock_...850280_fa3217d6 (parent A) | L126-L175 (`_shackle_shape`) + L214-L227 (`body_to_shackle`) | eligible if compatible | body-frame author 的高 U（makeTorus 半环 + 两直腿），单 PRISMATIC +Z 抬升释放，长腿保留插入。|
| short_u_shackle_revolve | rec_build-...-lock_...520334_f96f0b30 (parent B) | L257-L289 (`_build_shackle_mesh`) + L389-L398 (`body_to_shackle`) | eligible if compatible | long-leg local frame author 的短 U（revolve 半环 crown），joint 原点 `(-LEG_X,0,TOP_Z)`，PRISMATIC +Z。combo family 默认 shackle。|
| shrouded_u_shackle | rec_lock_var_shrouded_shackle | L81-L118 (`_make_shoulder`+`_body_shape` shroud) + L163-L213 (`_shackle_shape`) + L243-L284 (`shackle_lift`/`body_to_shackle`/`shackle_rotate`) | eligible if compatible | body 顶加两抬高 shoulder（shroud）；短 shackle；二段释放 `shackle_lift`(PRISMATIC +Z)→`shackle_rotate`(REVOLUTE +Z 绕保留长腿)。多一个 kinematic `shackle_lift` part。|
| straight_bar_hasp | rec_lock_var_straight_bar_shackle | L186-L235 (`_hasp_guide_channel`+`_build_hasp_guide_brackets`) + L255-L276 (`_build_hasp_bar_mesh`) + L370-L379 (`body_to_hasp`) | eligible if compatible | U-shackle 换成直 hasp bar，沿 **+X** 滑移（`body_to_hasp` PRISMATIC axis +X），两 guide bracket 保留；释放方向与轴不同于所有 U 形 shackle。|

### Slot C：access mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| keyway_access | rec_build-...-lock_...850280_fa3217d6 (parent A) | L90-L100 (`_keyway_disc_shape`) + L103-L123 (`_keyway_slot_shape`) | eligible if compatible | 前面 chrome 圆盘 escutcheon + 暗 keyhole slot（proud of disc），无 access 运动（纯 body visual）。|
| dial_stack_access | rec_build-...-lock_...520334_f96f0b30 (parent B) | L147-L193 (`_black_faceplate`+`_dial_window_frame`) + L234-L251 (`_build_dial_axles`) + L295-L339 (`_build_dial_mesh`) + L401-L423 (dial 复制循环) | eligible if compatible | 前面铣窗 pocket + faceplate + bezel；N 个 knurled dial 各 CONTINUOUS about X，竖直堆叠。multiplicity 轴 `dial_count` 仅作用于此 module。|
| keyway_dust_cover | rec_lock_var_keyway_dust_cover | L205-L238 (`_hinge_bracket_shape`) + L241-L274 (`_dust_cover_shape`) + L354-L378 (`dust_cover`/`body_to_dust_cover`) | eligible if compatible | keyway_access 之上加铰接 dust cover（`dust_cover` part，`body_to_dust_cover` REVOLUTE about -X），关闭遮 keyway、打开外摆暴露。叠加一个 access 运动。|

硬约束满足：每个 slot ≥3 candidate（A=4、B=4、C=3），全部有真实 `model.py:Lx-Ly`，candidate 间均为结构差异（part tree / joint topology / 主 primitive 不同），无单 candidate slot。

## 槽位图（slot graph）

pattern: `mixed`（parallel_children + multiplicity）

```
                 root = body  (Slot A: rect_brass / armored_combo / laminated / round_discus)
                   │
   ┌───────────────┼─────────────────────────────────────────────┐
   │ Slot B 释放闩                                                  │ Slot C access
   │                                                              │
 (U 形分支)                          (hasp 分支)              keyway_access  → body visual only (no joint)
 body --[PRISMATIC +Z @ shackle_origin]--> shackle           dial_stack    → body --[CONTINUOUS about X]×N--> dial_i
   或二段：                                                  keyway_dust_cover → keyway_access + body --[REVOLUTE -X]--> dust_cover
 body --[PRISMATIC +Z]--> shackle_lift --[REVOLUTE +Z]--> shackle
                                                            body --[PRISMATIC +X @ TOP_Z]--> hasp_bar  (straight_bar_hasp)
```

接口点位与策略：
- **Slot A → Slot B（mating/捕获接口）**：body 顶面两 bore（keyed: `_body_shape` 顶孔；combo: `_shackle_bores`）捕获 shackle 双腿。`body_to_shackle` joint 原点与 axis 由 family 决定：keyed = `(0,0,0)`/+Z（shackle 在 body frame author）；combo = `(-LEG_X,0,TOP_Z)`/+Z（shackle 在 long-leg local frame author）。straight_bar_hasp 接口换成顶面 guide channel + 两 bracket，joint 原点 `(0,0,TOP_Z)`/+X。
- **Slot A → Slot C（前面板接口）**：keyway 圆盘 embed 进 front 面（keyed: `FRONT_Y`；discus: 圆形 front 面 at body center Z）；dial 窗 pocket 铣穿 combo front + faceplate，dial 在 `DIAL_AXLE_Y` 深度绕 X 轴旋转、rim proud of faceplate。dust cover hinge bracket embed 进 keyed front 面 keyway 上方。
- **跨 slot joint type/axis/range**：PRISMATIC +Z（U lift，range `[0, SHACKLE_TRAVEL]` ≈ 0.018–0.026）；PRISMATIC +X（hasp，`[0, HASP_TRAVEL=0.022]`）；REVOLUTE +Z（shackle swing，`[0, ~2.05]`）；CONTINUOUS about X（dial，无限）；REVOLUTE -X（dust cover，`[0, ~2.1]`）。
- **互斥/派生**：family（keyed vs combo）由 Slot A 派生，gate 掉 Slot B/C 中跨 family 的组合（见第 9 节）。`dial_count` multiplicity 仅在 Slot C = dial_stack_access 时激活；其它 access 忽略它。

## 每槽位 Module Emits / Interfaces

### Slot A / module rect_brass_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`(root) | parent A L188 |
| visuals | `body_shell`(brass box, 顶两 bore) | parent A L62-L81, L189-L193 |
| internal joints | 无 | — |
| upstream interface | root，无 parent | parent A L188 |
| downstream interface | 顶面两 bore @ ±LEG_OFFSET 捕获 shackle；front 面 `FRONT_Y` 承载 keyway | parent A L74-L80, L84 |

### Slot A / module armored_combo_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`(root) | parent B L350 |
| visuals | `body_shell`(orange shell), `faceplate`, `dial_frame`(bezel), `rivets`, `dial_axles` | parent B L351-L376 |
| internal joints | 无（dial joints 由 Slot C dial module 提供） | — |
| upstream interface | root | parent B L350 |
| downstream interface | 顶面 `_shackle_bores` @ ±LEG_X 捕获 shackle；front dial 窗 pocket + axles 承载 dial stack | parent B L212-L223, L234-L251 |

### Slot A / module laminated_steel_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`(root) | laminated L233 |
| visuals | `plate_0..4`(5 层 plate), `rivet_0..3`(4 through-rivet) + keyway visuals | laminated L234-L255 |
| internal joints | 无 | — |
| downstream interface | plate 堆叠内捕获 shackle 双腿（allow_overlap per plate）；rivet 轴可穿 shackle 腿（allow_overlap） | laminated L375-L387 |

### Slot A / module round_discus_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`(root) | round_disc L181 |
| visuals | `body_shell`(旋转圆柱 discus, 弧顶 bore) + keyway visuals | round_disc L182-L196 |
| downstream interface | 弧面顶两 bore 捕获 shackle；圆形 front 面 @ body center Z 承载 keyway | round_disc L80-L90, L97 |

### Slot B / module tall_u_shackle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shackle` | parent A L206 |
| visuals | `shackle_bar`(makeTorus 半环 + 两直腿) | parent A L126-L175, L207-L211 |
| internal joints | `body_to_shackle` PRISMATIC, axis +Z, origin `(0,0,0)`, range `[0, SHACKLE_TRAVEL]` | parent A L214-L227 |
| upstream interface | body 顶 bore；body frame author，joint 原点在 body origin | parent A L214-L219 |
| downstream interface | 长腿保留插入（locked/lifted 均 overlap body in Z） | parent A L307-L335 |

### Slot B / module short_u_shackle_revolve
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shackle` | parent B L379 |
| visuals | `shackle_bar`(revolve 半环 crown + 两直腿) | parent B L257-L289, L380-L384 |
| internal joints | `body_to_shackle` PRISMATIC, axis +Z, origin `(-LEG_X,0,TOP_Z)`, range `[0, SHACKLE_TRAVEL]` | parent B L389-L398 |
| upstream interface | combo body 顶 bore；long-leg local frame author | parent B L389-L394 |
| downstream interface | 长腿 captive、短腿全行程 clear | parent B L492-L505 |

### Slot B / module shrouded_u_shackle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shackle_lift`(kinematic), `shackle` | shrouded L244, L247 |
| visuals | `shackle_bar`(短 U) + body 多出 shroud shoulder（属 body_shell） | shrouded L81-L118, L248-L252 |
| internal joints | `body_to_shackle` PRISMATIC +Z（parent→shackle_lift）；`shackle_rotate` REVOLUTE +Z, origin `(-LEG_OFFSET,0,0)`（shackle_lift→shackle） | shrouded L254-L284 |
| upstream interface | body+shroud bore 捕获腿；lift 帧抬升后 revolve 释放 | shrouded L255-L268 |
| downstream interface | 长腿 swung-open 仍保留插入 | shrouded L442-L459 |

### Slot B / module straight_bar_hasp
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hasp_bar` | straight_bar L361 |
| visuals | `hasp_bar`(直 bar + latch notch) + body 多出 `hasp_brackets` + guide channel | straight_bar L186-L235, L255-L276, L362-L366 |
| internal joints | `body_to_hasp` PRISMATIC, axis **+X**, origin `(0,0,TOP_Z)`, range `[0, HASP_TRAVEL]` | straight_bar L370-L379 |
| upstream interface | body 顶 guide channel + 两 bracket 保留 bar | straight_bar L186-L235 |
| downstream interface | bar 全行程 latch 端 extends past body | straight_bar L486-L495 |

### Slot C / module keyway_access
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（叠加到 body 的 visual） | — |
| visuals | `keyway_disc`(chrome 圆盘), `keyway_slot`(暗 keyhole) | parent A L90-L123, L194-L203 |
| internal joints | 无（静态 access 表征） | — |
| upstream interface | embed 进 body front 面（disc/slot proud of front） | parent A L288-L296 |

### Slot C / module dial_stack_access
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dial_1..N`（multiplicity，见第 8 节） | parent B L401-L407 |
| visuals | per-dial `dial_i_wheel`(knurled) + `dial_i_band`；body 侧 faceplate/bezel/axles 由 Slot A combo body emit | parent B L295-L339, L403-L414 |
| internal joints | `dial_i` CONTINUOUS about X, origin `(0, DIAL_AXLE_Y, DIAL_ZS[i])`，每 dial 独立 | parent B L415-L423 |
| upstream interface | dial 在 front 窗 pocket 内绕自身 X 轴；rim proud of faceplate；nest on body axle（allow_overlap + retained insertion） | parent B L530-L552 |

### Slot C / module keyway_dust_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dust_cover`（+ 继承 keyway_access 的 disc/slot visual） | dust_cover L355 |
| visuals | `cover_flap`(brass 盖+grip lip), body 侧 `hinge_bracket` | dust_cover L205-L274, L316-L320, L356-L360 |
| internal joints | `body_to_dust_cover` REVOLUTE, axis **-X**, origin `(0, HINGE_Y, HINGE_Z)`, range `[0, COVER_OPEN_ANGLE≈2.1]` | dust_cover L365-L378 |
| upstream interface | hinge bracket embed 进 keyway 上方 front 面；关闭盖遮 keyway disc（expect_overlap xz） | dust_cover L543-L572 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_module | enum | rect_brass / armored_combo / laminated / round_discus | — | choice | deterministic procedural sampler；派生 family ∈ {keyed, combo} | Slot A 表 |
| shackle_module | enum | tall_u / short_u_revolve / shrouded_u / straight_bar_hasp | — | choice | sampler，受 family gate（见第 9 节 compatibility） | Slot B 表 |
| access_module | enum | keyway / dial_stack / keyway_dust_cover | — | choice | sampler，受 family gate | Slot C 表 |
| dial_count | int | [3, 5]（产品域）；测试偏小 | 4 | conditional | 仅 access_module=dial_stack 时激活；否则忽略 | parent B L54 / 第 8 节 |
| palette_style | enum | brass_classic / armored_orange / laminated_steel / brushed_discus / blackened_steel | brass_classic | choice | 每 seed 抽一种 colorway（见下） | 各源 material |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 范围内独立采样后 clamp；缩放 `BODY_H`/discus 直径 | 各 body 源 |
| shackle_clear_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 arch clear / U 高度 | parent A L52 / parent B L46 |
| shackle_travel | float | derived | — | equation | `= LEG_SEAT_DEPTH(或 SHORT_LEG_BURY) + margin`，随 body_height_scale 派生，不独立采样 | parent A L58 / parent B L49 |
| dial_pitch_scale | float | [0.95, 1.08] | 1.0 | independent | 缩放 `DIAL_PITCH`（dial 间距），仅 dial_stack | parent B L63 |
| (—) | constraint | — | — | inequality | dial 窗高 `POCKET_Z_HI−POCKET_Z_LO = dial_count·DIAL_PITCH·dial_pitch_scale + 2·(DIAL_R+clear)` 必须 `≤ BODY_H·body_height_scale − 2·ORANGE_LIP`；越界则回缩 dial_pitch_scale 或拒绝重采 | parent B L63-L76 |
| (—) | constraint | — | — | inequality | shackle 长腿 buried 深度 `≥ SHACKLE_TRAVEL + margin`（全行程保留插入）；违反按比例回缩 travel | parent A L327-L335 |
| (—) | constraint | — | — | conditional | shrouded/straight_bar 的额外 joint 仅在对应 shackle_module 选中时存在 | Slot B 表 |

palette 只表达材质/配色选择，不改拓扑。所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解。

### palette_style colorways（≥3，目标 4–6；均来自 5★ 源观测）
1. **brass_classic**（parent A / shrouded / dust_cover）：brass body `(0.83,0.66,0.18)` + hardened_steel shackle `(0.74,0.76,0.80)` + chrome keyway disc `(0.86,0.88,0.90)` + 暗 slot `(0.07,0.07,0.08)`。
2. **armored_orange**（parent B / straight_bar / dials）：orange body `(0.86,0.40,0.10)` + black faceplate `(0.10,0.10,0.11)` + steel shackle `(0.78,0.80,0.83)` + dial_black `(0.06,0.06,0.07)` + dial_band `(0.30,0.30,0.32)` + rivet_steel `(0.70,0.72,0.75)`。
3. **laminated_steel**（laminated_body）：交替 plate 调 dark `(0.36,0.38,0.42)`/mid `(0.46,0.48,0.52)` + rivet `(0.58,0.60,0.63)` + steel shackle + chrome keyway。
4. **brushed_discus**（round_disc_body）：brushed_steel body `(0.72,0.73,0.76)` + hardened_steel shackle `(0.74,0.76,0.80)` + chrome keyway。
5. **blackened_steel**（合成 colorway，源调暗化）：blackened body `(0.18,0.19,0.21)` + steel shackle `(0.74,0.76,0.80)` + chrome keyway——黑化挂锁常见配色，从 parent 材质族安全派生。

## Multiplicity / Copy Logic

本模板有 **1 根 multiplicity 轴**：`dial_count`。

- **count_param**：`dial_count`
- **N_range**：产品域 `[3, 5]`（紧凑组合挂锁实测范围；更宽需更多 dial 窗/body 高度证据，暂不外推）。测试偏小：sweep 主用 N∈{3,4}，N=5 稀疏覆盖（已有 five_dials 证据）。
- **sampling domain（权重档）**：N=4 最高频（parent 默认）、N=3 次之、N=5 稀有尾部。仅 `access_module = dial_stack_access` 时激活；其它 access（keyway / keyway_dust_cover）忽略 `dial_count`（视为 N/A）。
- **copied object**：一个编号 dial wheel（knurled rim + index flat + 轴 bore + 内 band 视觉），即 `_build_dial_mesh`。
- **naming**：part 与 joint 均 `dial_{i}`（i=1..N），视觉 `dial_{i}_wheel` / `dial_{i}_band`。
- **placement**：沿 +Z 规则竖直堆叠，`DIAL_ZS[i] = DIAL_STACK_CZ + (i−(N−1)/2)·DIAL_PITCH·dial_pitch_scale`，同 Y 深度 `DIAL_AXLE_Y`、同 X 中心；`DIAL_STACK_CZ` 随 N 上移（4→0.032、5→0.034）以居中堆叠。
- **joint policy**：每 dial 一个**独立 CONTINUOUS** 关节，绕同一水平 X 轴，parent=body，无限行程。dial 窗 pocket 与 axles 随 N 重算（pocket Z 上下墙 = 首/末 dial ± DIAL_R ± clear）。
- **source/gating**：N=3 ← `rec_lock_var_three_dials`、N=4 ← parent B、N=5 ← `rec_lock_var_five_dials`。gating：`dial_count` 只与 dial_stack_access 联动；body 必须为 armored_combo（dial 窗只在 combo front 实现）。

## 拓扑多样性审计


理由：Slot A 4 选 + Slot B 4 选（含 hasp 这一完全不同的滑移 spine、shrouded 这一二段 lift+revolve）+ Slot C 3 选（含 dial multiplicity 与 dust_cover 叠加运动）产生大量结构不同的 part-tree/joint-topology；keyed 与 combo 两条 spine 各自就 >10 distinct。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic procedural sampling 依序选 body_module → 派生 family → 在该 family 合法集内选 shackle_module 与 access_module → 若 access=dial_stack 则加权抽 dial_count∈{3,4,5} → 抽 independent scale 并按第 7 节契约 clamp/派生/回缩。compatibility matrix gate 掉跨 family 非法组合。少量 regression overrides 仅用于已知失败 seed（初版为空）。random sweep seeds 0-49（首轮）、0-999（成熟审计）；viewer 目检覆盖每条 family 的 closed/open pose。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别因 family gate（keyed/combo 两套接口）与 access 互斥，合法拓扑等价类约数十级，distinct 目标按合法组合×scale 分箱估 ≥60 即可接受（低于 300 由 family 互斥约束解释）。
若使用 regression overrides：初版无；如出现 dial 窗超高或 shackle 穿模回归再按 seed+原因记录。
Controlled local parameterization：初版关键连续 scale = `body_height_scale`（independent，缩放 body 高度/discus 直径，clamp [0.90,1.12]）、`shackle_clear_scale`（independent，缩放 U 高，[0.85,1.15]）、`dial_pitch_scale`（independent，仅 dial_stack，[0.95,1.08]）；派生 `shackle_travel = f(seat_depth, body_height_scale)`（equation）；inequality 投影：dial 窗高 ≤ body 可用高、长腿 buried ≥ travel+margin。这些 scale 只改安全比例/clearance，不改 slot 选择、joint 轴语义、family 接口或 dial_count multiplicity。遵循契约：先采 independent → 派生 travel → 投影回缩 dial 窗/buried → 解析 conditional（额外 joint 仅随 shackle_module 存在）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body→family→(shackle,access) 合法集内加权选→dial_count 加权(若 dial_stack)→scale 采样 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 见下方矩阵：keyed/combo family 互斥；hasp/straight_bar 仅 combo；dial_stack 仅 combo；keyway/dust_cover 仅 keyed | 无 floating、无穿模、shackle 轴正确、dial 窗不超体、长腿保留插入 |
| controlled local variation | body_height_scale / shackle_clear_scale / dial_pitch_scale，全部 clamp + inequality 投影 | 比例变化不破坏 bore 捕获、dial 窗 clearance、joint origin、类别 identity |
| regression overrides | none（初版） | 仅已知失败/审核指定 |
| random sweep | seeds 0-49 首轮，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A | 4 | yes | yes | rect_brass / armored_combo / laminated / round_discus |
| B | 4 | yes | yes | tall_u / short_u_revolve / shrouded_u / straight_bar_hasp |
| C | 3 | yes | yes | keyway / dial_stack(+multiplicity) / keyway_dust_cover |

### Compatibility matrix（跨 slot gating）
派生 family：`rect_brass / laminated / round_discus → keyed`；`armored_combo → combo`。

| (A family) | 合法 Slot B | 合法 Slot C | 非法 / 理由 |
|---|---|---|---|
| keyed (rect/laminated/discus) | tall_u, shrouded_u（讨论：shrouded 源于 rect brass，其它 keyed body 需重算 shroud bore；初版仅 rect_brass+shrouded 进采样，其它 keyed+shrouded 列 fallback 待实现） | keyway, keyway_dust_cover | short_u_revolve（combo local-frame author，依赖 combo bore 原点）、straight_bar_hasp（依赖 combo guide channel/bracket）、dial_stack（dial 窗只在 combo front 实现）→ 全部非法 |
| combo (armored) | short_u_revolve, straight_bar_hasp | dial_stack | tall_u（body-frame author，原点不匹配 combo）、shrouded_u（shroud shoulder 仅 keyed body）、keyway / keyway_dust_cover（combo front 已被 dial 窗占用）→ 非法 |

fallback/降级说明：
- `round_discus_body + keyway_dust_cover`：dust cover hinge bracket 在 keyed 平 front 面 author；discus front 为圆面，bracket embed 需重算（源未直接采样）。初版 gate 为 fallback（discus 仅配 plain keyway），待实现弧面 bracket 后再开放。
- `laminated/discus + shrouded_u`：shroud shoulder + bore 仅在 rect brass body 上验证。初版仅 `rect_brass + shrouded_u` 进 seed domain；其它 keyed+shrouded 标 fallback（reviewer 状态：暂不采样，阻塞原因 = shroud bore 未在 laminated/discus 上重算）。
- 单 candidate slot：无（每 slot ≥3）。上述 fallback 是跨 slot 组合层面的暂不采样，不是 slot 降级；每个 candidate 自身仍 eligible（在其合法 family 内）。

## Validator

- slot_choices_for_seed returns implemented module names（body/shackle/access + dial_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal cross-family combinations（keyed↔combo 互斥）
- optional regression overrides are sparse and justified（初版无）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params（body_height/shackle_clear/dial_pitch）clamped；不破坏 bore 捕获、dial 窗 clearance、joint origin、dial_count multiplicity
- cross-part scale dependencies（shackle_travel equation、dial 窗 / buried inequality、额外 joint conditional）resolved in `resolve_config`
- critical InterfaceSpec/MatingContract：顶 bore 捕获 shackle（retained insertion）、front 面 keyway embed / dial 窗 pocket
- key joints：`body_to_shackle` PRISMATIC +Z（或 hasp +X）；dial_i CONTINUOUS about X；shackle_rotate REVOLUTE +Z；dust_cover REVOLUTE -X
- copied objects（dial_i）follow naming `dial_{i}` 与竖直堆叠 placement

## Reject cases

- body_module=armored_combo 却配 keyway_access / keyway_dust_cover（combo front 被 dial 窗占用 → 穿模/冲突）。
- body_module∈{rect/laminated/discus}（keyed）却配 dial_stack_access 或 straight_bar_hasp（无 dial 窗 / 无 guide channel → 漂浮或穿模）。
- short_u_revolve 配 keyed body（local-frame author 原点 `(-LEG_X,0,TOP_Z)` 与 keyed bore 不匹配 → shackle 漂浮/错位）。
- dial_count > 5 或窗高超过 body 可用高度（dial 顶/底超出 body 或穿 faceplate）。
- shackle_travel 大于长腿 buried 深度（全行程长腿脱出 bore，失去 retained insertion）。
- shrouded_u 配 laminated/discus body 而未重算 shroud bore（shoulder bore 与 plate/弧面错位 → 穿模）。
- dust_cover hinge bracket 在 discus 圆 front 面未重算（bracket 悬空/穿模）。
- 任何 scale 未在 `resolve_config` clamp/投影，导致 builder 期 dial 窗/shackle 几何越界。

## 与相邻类别的边界

- 不该混入：门锁 / locker 内置锁 / 保险箱锁（container_locker、freestanding_safe 等）——这些锁固定在门/箱体上，无独立暴露 shackle 与 standalone 锁体；padlock 是便携、可拆卸、shackle 外露。
- 不该混入：纯装饰锁形挂件 / 无释放运动的实心锁——padlock 必须有 defining 释放运动（PRISMATIC shackle/hasp + retained insertion）。
- 不该混入：拉链锁 / 缆索锁 / 链条锁（柔性 shackle）——本模板 shackle 为刚性 U 或刚性直 bar，不建模柔性缆索。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：(1) keyed+shrouded 仅 rect_brass 进 seed domain（laminated/discus+shrouded 列 fallback，待 shroud bore 重算）是否接受；(2) round_discus+dust_cover 弧面 bracket 暂 gate 为 fallback 是否接受；(3) dial_count N_range [3,5] 不外推是否接受；(4) palette colorway #5 blackened_steel 为合成派生（非直接源色），是否保留。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | rect_brass_body | rec_build-...-lock_...850280_fa3217d6 | L62-L81 | keyed body root + 顶 bore 接口 |
| S2 | A | armored_combo_body | rec_build-...-lock_...520334_f96f0b30 | L96-L124, L226-L231 | combo body root + dial 窗 + axles |
| S3 | A | laminated_steel_body | rec_lock_var_laminated_body | L88-L139 | plate 堆叠 + through-rivet |
| S4 | A | round_discus_body | rec_lock_var_round_disc_body | L67-L90 | discus 旋转圆柱 body |
| S5 | B | tall_u_shackle | rec_build-...-lock_...850280_fa3217d6 | L126-L175, L214-L227 | body-frame 长 U + PRISMATIC +Z |
| S6 | B | short_u_shackle_revolve | rec_build-...-lock_...520334_f96f0b30 | L257-L289, L389-L398 | local-frame 短 U + PRISMATIC +Z |
| S7 | B | shrouded_u_shackle | rec_lock_var_shrouded_shackle | L81-L118, L163-L213, L243-L284 | shroud shoulder + lift+revolve 二段 |
| S8 | B | straight_bar_hasp | rec_lock_var_straight_bar_shackle | L186-L235, L255-L276, L370-L379 | 直 hasp bar + PRISMATIC +X + brackets |
| S9 | C | keyway_access | rec_build-...-lock_...850280_fa3217d6 | L90-L123, L194-L203 | keyway disc + slot（静态） |
| S10 | C | dial_stack_access | rec_build-...-lock_...520334_f96f0b30 | L147-L193, L234-L251, L295-L339, L401-L423 | dial 窗 + N×CONTINUOUS dial（multiplicity） |
| S11 | C | keyway_dust_cover | rec_lock_var_keyway_dust_cover | L205-L274, L354-L378 | hinge bracket + dust_cover REVOLUTE -X |
| S12 | C(mult) | dial_count N=3 | rec_lock_var_three_dials | L54, L435-L457 | dial_count=3 证据 |
| S13 | C(mult) | dial_count N=5 | rec_lock_var_five_dials | L54, L64 (DIAL_STACK_CZ=0.034) | dial_count=5 证据 + 堆叠居中上移 |

## 模板实现备注（可选）

- keyed 与 combo 两条 spine 应各有独立 body/shackle builder helper；不要强行共享 shackle author 框架（一个 body-frame、一个 long-leg-local-frame，joint 原点不同）。
- dial_stack 的 dial 窗 pocket、axles、`DIAL_ZS`、`POCKET_Z_*` 必须随 `dial_count` 与 `dial_pitch_scale` 统一重算，否则 N=5 时窗高超体。
- allow_overlap 必须 per-combo 复制：keyed 顶 bore↔shackle（rect/discus 用 `body_shell`↔`shackle_bar`；laminated 用每个 `plate_i`↔`shackle_bar` + `rivet_i`↔`shackle_bar`）；combo dial↔body（每 dial）；hasp↔body channel；dust_cover↔keyway_disc（closed）。
- shrouded/dust_cover 的 `shackle_lift` 为不可见 kinematic part，二段释放 joint 链 body→shackle_lift→shackle 必须保留。
</content>
</invoke>
