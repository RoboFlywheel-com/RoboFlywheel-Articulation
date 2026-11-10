# Modular Spec — Point-of-sale terminal

## 元信息
| 项 | 值 |
|---|---|
| slug | `point_of_sale_terminal` |
| template path | `agent/templates/point_of_sale_terminal.py` |
| test path (optional) | `tests/agent/test_point_of_sale_terminal_template.py` (skipped — acceptance is sweep) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children under one housing + an optional upstream support root + soft-key multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (2 origins + 6 verified forks) |
| source_index_policy | only adopted module sources are indexed below |

Read records (all `revisions/rev_000001/model.py`):
`rec_a-silver-...074f8840` (origin A), `rec_a-gray-...4430a86e` (origin B),
`rec_point_of_sale_terminal_var_display_tilt`, `..._var_base_dock_tilt`,
`..._var_base_pole_swivel`, `..._var_body_touchscreen`, `..._var_softkeys_n2`,
`..._var_softkeys_n6`.

## 核心身份

A self-contained electronic **payment terminal**: it reads a card (chip slot +
magnetic-stripe swipe groove, optionally an inserted card) and takes entry via a
physical keypad **or** a dominant touchscreen, shows a display, and prints a
receipt from a flip-cover roll printer. The hero body is a filleted **wedge
block** (flat front keypad deck rising over a sloped display face to a rear
printer deck). Every unit keeps a real card interface, a display, some entry
input, and at least one real non-fixed joint (key press / printer cover /
paper-roll spindle / card slide / display tilt / dock recline / pedestal swivel).

Frame convention (adopted from origin A / the silver hero, which owns 5 of the 6
forks): **+X = front** (keypad + chip-slot end, toward the user), **+Z = up**,
**+Y = user's right** (magstripe swipe-groove side). Device ≈ 0.185 m long ×
0.082 m wide.

Must **not** drift to: cash register / drawer POS, tablet/phone, self-checkout
kiosk/tower, barcode scanner, calculator, or a bare mPOS card-reader dongle (no
display/keypad/printer).

## 槽位 + 候选模块表

### Slot A：support_base （① 骨架 · 根槽 / root）
Selects the kinematic root and how the terminal is grounded. `flat_feet` makes
the housing itself the root; the other two insert a support part **above** which
the housing hangs as a revolute child.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_feet` | forked_anchor | origin A | L239-L248 | eligible if compatible | root = `housing`; 4 rubber-foot `Cylinder` visuals on the housing underside; no extra part / joint |
| `tilt_dock` | forked_anchor | var_base_dock_tilt | L60-L72, L188-L226, L246-L270, L321-L332 | eligible if compatible | root = `dock_base` (CadQuery tray+upstand+lip mesh); feet+contact-pad visuals on dock; `base_to_body` REVOLUTE (axis -Y, recline [0,0.35]); housing is child |
| `swivel_pedestal` | forked_anchor | var_base_pole_swivel | L86-L99, L189-L220, L242-L261, L311-L322 | eligible if compatible | root = `stand_base` (disk+pole+collar mesh + chrome weight-ring + feet); `stand_to_body` REVOLUTE (axis +Z yaw [-1.4,1.4]); housing is child |

### Slot B：body_form （③ 主体形态家族 / Primary Form Family）
The housing part is constant (wedge chassis), but the **top-face read** and the
input layer it carries switch between a keypad block and a screen-dominant slab.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `keypad_wedge` | forked_anchor | origin A / origin B | A L99-L144 / B L99-L156 | eligible if compatible | wedge `housing` mesh; carries sloped display + `menu_strip` + N menu keys + 3×4 numeric grid + 3 command keys (all PRISMATIC children). `form_subtype = Volumetric Envelope Form` |
| `touchscreen_slab` | forked_anchor | var_body_touchscreen | L177-L206, L299-L325 | eligible if compatible | same wedge `housing` mesh; a **large touchscreen** bezel+glass covering the top face, **no** numeric/command/menu keys; 2 side hard-buttons (PRISMATIC). `form_subtype = Planar Boundary Form` (dominant flat screen boundary) |

### Slot C：display_mount （② 关节类型）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_display` | forked_anchor | origin A / var_body_touchscreen | A L198-L212 / touch L177-L206 | eligible if compatible | bezel+screen `Box` visuals fused into `housing` on the sloped face (small, on keypad_wedge) or a top-face-dominant screen (on touchscreen_slab); no extra part/joint |
| `tilt_display` | forked_anchor | var_display_tilt | L215-L255 | eligible if compatible (keypad_wedge only) | separate `display_head` part (hinge boss barrel + bezel + screen); `housing_to_display_head` REVOLUTE (axis -Y, [0,0.6]) at the slope top-rear edge; `hinge_bracket` visual on housing anchors it |

### Slot D：card_interface （② 关节类型 · 支付 I/O）
The chip slot + magstripe swipe groove are cut into the housing mesh for **every**
unit (identity floor). This slot chooses whether an inserted card slides.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `static_slot` | forked_anchor | origin A | L223-L237 | eligible if compatible | `chip_slot_liner` + `swipe_slot_liner` dark `Box` visuals fused into housing; no moving card |
| `sliding_card` | forked_anchor | origin B | L375-L411 | eligible if compatible | adds a `bank_card` PRISMATIC part (card body mesh + logo/band visuals) inserted in the front chip slot, sliding out toward the user along the front axis, [0,0.018] |

### Slot E：paper_roll （② 关节类型 · 打印机机构）
The flip-cover `printer_cover` (REVOLUTE hinge, tear bar) is present on **every**
unit (source-constant printer mechanism). This slot chooses the roll behaviour.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `continuous_spindle` | forked_anchor | origin A | L276-L297 | eligible if compatible | separate `paper_roll` part (paper `Cylinder` + axle `Cylinder`); `paper_roll_spindle` CONTINUOUS joint (axis +Y); axle ends captured in bay walls |
| `static_roll` | forked_anchor | origin B | L230-L237 | eligible if compatible | paper roll `Cylinder` fused as a housing visual resting in the bay; no spindle joint |

### Slot F：soft_key_row （① multiplicity）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `n2` | forked_anchor | var_softkeys_n2 | L340-L355 (N=2) | eligible if compatible (keypad_wedge only) | 2 loop-emitted `menu_key_{i}` PRISMATIC keys on `menu_strip` |
| `n4` | forked_anchor | origin A / origin B | A L340-L355 / B L339-L348 | eligible if compatible (keypad_wedge only) | 4 menu keys (both origins) |
| `n6` | forked_anchor | var_softkeys_n6 | L340-L355 (N=6) | eligible if compatible (keypad_wedge only) | 6 menu keys |

硬约束满足：每个 functional slot 达到 ≥2 结构不同 candidate（A=3, B=2, C=2, D=2,
E=2, F=3 N-values）。所有 candidate 均 `forked_anchor`，无凭空 skeleton。

## 槽位图（slot graph）

pattern: `mixed`

```
[Slot A support_base root]
   flat_feet:        housing == ROOT (feet visuals on housing)
   tilt_dock:        dock_base(ROOT) --[REVOLUTE -Y recline 0..0.35 @ tray-rear]--> housing
   swivel_pedestal:  stand_base(ROOT) --[REVOLUTE +Z yaw ±1.4 @ collar-top]--> housing

[Slot B body_form] == housing (wedge mesh; keypad_wedge | touchscreen_slab)
housing --[REVOLUTE -Y @ rear printer edge]--> printer_cover        (always)
housing --[Slot C: fixed=fused visuals | tilt=REVOLUTE -Y]--> display_head?
housing --[Slot E: continuous=CONTINUOUS +Y spindle | static=fused visual]--> paper_roll?
housing --[Slot D: static=fused liners | sliding=PRISMATIC +X]--> bank_card?
housing --[PRISMATIC -Z press] x (12 numeric + 3 command)           (keypad_wedge)
housing --[Slot F PRISMATIC -Z press] x N menu keys                 (keypad_wedge)
housing --[PRISMATIC +Y press] x 2 side buttons                     (touchscreen_slab)
```

Interface points:
- **support→housing**: dock tray-top plane / pedestal collar-top plane; joint
  origin on that plane; housing underside seats on it (contact + captured-seat
  `allow_overlap`). `flat_feet` needs no chain joint (housing is root).
- **housing→printer_cover**: rear-edge hinge line at `REAR_DECK_Z`, axis -Y.
- **housing→display_head** (tilt): slope top-rear edge, axis -Y; `hinge_bracket`
  + `hinge_boss` captured pivot.
- **housing→paper_roll** (continuous): roll centre in the bay, axis +Y; axle
  captured in bay walls.
- **housing→bank_card** (sliding): chip-slot floor at the front face, axis +X.
- **keys/buttons**: rest on the deck / side face; PRISMATIC press into the body.

Mutual-exclusion / derived:
- `tilt_display`, numeric keypad, command keys, `soft_key_row` exist **only** for
  `keypad_wedge`; `touchscreen_slab` forces `fixed_display` + side buttons and
  removes the keypad sub-tree (gated in `resolve_config`, §9).

## 每槽位 Module Emits / Interfaces

### Slot A / module flat_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (housing is root) | A L239-L248 |
| internal joints | none | — |
| upstream interface | none (root) | — |
| downstream interface | housing bottom rests on counter (z=0); 4 feet visuals | A L239-L248 |

### Slot A / module tilt_dock
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dock_base` (root) | dock L188-L226 |
| internal joints | `base_to_body` REVOLUTE parent=dock_base child=housing, axis (0,-1,0), origin (-0.005,0,CRADLE_HEIGHT), [0,0.35] | dock L321-L332 |
| upstream interface | root | — |
| downstream interface | tray-top plane @ z=CRADLE_HEIGHT carries the housing | dock L246-L270 |

### Slot A / module swivel_pedestal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stand_base` (root) | pedestal L189-L220 |
| internal joints | `stand_to_body` REVOLUTE parent=stand_base child=housing, axis (0,0,1), origin (0,0,STAND_TOP_Z), [-1.4,1.4] | pedestal L311-L322 |
| upstream interface | root | — |
| downstream interface | collar-top plane @ z=STAND_TOP_Z carries the housing | pedestal L242-L261 |

### Slot B / module keypad_wedge (housing) + touchscreen_slab
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing` (wedge CadQuery mesh; cavity, chip slot, swipe groove cut) | A L99-L144 |
| internal joints | none (all children parented externally) | — |
| upstream interface | housing underside (root, or child of support at support's downstream plane) | A L99-L144 |
| downstream interface | flat front deck (@FRONT_DECK_Z) + sloped face + bay for children | A L99-L144 |

### Slot C / module fixed_display / tilt_display
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed → none (bezel/screen fused into housing); tilt → `display_head` | A L198-L212 / tilt L223-L255 |
| internal joints | tilt → `housing_to_display_head` REVOLUTE axis (0,-1,0) [0,0.6] | tilt L245-L255 |
| upstream interface | slope face / slope top-rear hinge edge | tilt L215-L221 |
| downstream interface | screen surface (output) | A L206-L212 |

### Slot D / module static_slot / sliding_card
| emits | 描述 | 来源 |
|---|---|---|
| parts | static → none (liners fused); sliding → `bank_card` | A L223-L229 / B L375-L397 |
| internal joints | sliding → `housing_to_bank_card` PRISMATIC axis (1,0,0) [0,0.018] | B L402-L411 |
| upstream interface | chip-slot floor at front face | B L399-L407 |
| downstream interface | protruding card face | B L375-L397 |

### Slot E / module continuous_spindle / static_roll
| emits | 描述 | 来源 |
|---|---|---|
| parts | continuous → `paper_roll`; static → none (roll fused) | A L276-L288 / B L230-L237 |
| internal joints | continuous → `paper_roll_spindle` CONTINUOUS axis (0,1,0) | A L289-L297 |
| upstream interface | bay walls (axle bearing) | A L289-L297 |
| downstream interface | roll paper surface | A L276-L288 |

### Slot F / module n2 / n4 / n6 (menu keys) + fixed numeric/command/side-buttons
| emits | 描述 | 来源 |
|---|---|---|
| parts | `menu_key_{i}` ×N; (keypad_wedge also: `key_1..key_hash` ×12, `cancel/clear/enter_key`); (touchscreen: `power_button`,`function_button`) | A L340-L355, L299-L338 / touch L299-L325 |
| internal joints | each PRISMATIC press (keys axis -Z; side buttons axis +Y) | A L313-L355 |
| upstream interface | menu_strip / deck top / side face | A L340-L352 |
| downstream interface | keycap tops | A L344-L346 |

活动件均有 articulation 语义；不动细节（bezel, screen, liners, tear_bar, feet,
contact pads, weight ring, screen graphics）写成宿主 part visual，不作独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `support_base` | enum | flat_feet / tilt_dock / swivel_pedestal | flat_feet | choice | procedural sampler | Slot A |
| `body_form` | enum | keypad_wedge / touchscreen_slab | keypad_wedge | choice | procedural sampler | Slot B |
| `display_mount` | enum | fixed_display / tilt_display | fixed_display | conditional | tilt_display 仅 keypad_wedge；touchscreen 强制 fixed | Slot C |
| `card_interface` | enum | static_slot / sliding_card | static_slot | choice | procedural sampler | Slot D |
| `paper_roll` | enum | continuous_spindle / static_roll | continuous_spindle | choice | procedural sampler | Slot E |
| `soft_key_count` | int | {2,4,6} (keypad_wedge); 0 (touchscreen) | 4 | conditional | =0 when touchscreen_slab | Slot F |
| `body_len_half` | float | [0.083,0.100] | 0.0925 | independent | clamp | A L34 |
| `body_width_half` | float | [0.037,0.045] | 0.041 | independent | clamp | A L35 |
| `key_travel` | float | [0.0012,0.0022] | 0.0015 | independent | clamp | A L65 |
| `cover_open_upper` | float | [1.4,1.7] | 1.7 | independent | clamp; sampled-pose clears | A L272 |
| `card_slide_upper` | float | derived 0.018 | 0.018 | equation | fixed hardware travel | B L410 |
| `tilt_upper` | float | [0.45,0.6] | 0.6 | independent | clamp | tilt L253 |
| `recline_upper` | float | [0.25,0.35] | 0.35 | independent | clamp | dock L331 |
| `yaw_limit` | float | [1.0,1.4] | 1.4 | independent | clamp | pedestal L320 |
| `palette_theme` | enum | silver / gray / graphite | silver | choice | palette only | A/B materials |
| (—) | constraint | — | — | inequality | menu strip width ≥ N·(menu_key pitch)；N=6 时加宽 strip | A L69-L72 |

连续尺寸采样契约：先采 independent 主尺度 → 派生 equation → inequality 回缩
（menu strip 宽度随 N 派生）→ conditional（display/keys 依据 body_form 解析）。

## 7.5 编译预算 / compile budget
Per-seed budget **≤ 20 s**. Basis: origins A/B compile in the library's typical
5–20 s band; geometry is a handful of small CadQuery booleans (one wedge
intersect + ≤5 cuts on the housing; optional dock/stand union) plus Box/Cylinder
primitives and one cached keycap mesh reused across all keys. Tessellation:
housing fillets small; N identical keys share one `mesh_from_cadquery` keycap.
Sweep `--compile-timeout 60` (≈3× budget watchdog).

## Multiplicity / Copy Logic

- **soft/menu key row** — `count_param` = `soft_key_count`; `N_range` product
  domain [2,6], sampled from {2,4,6} (weighted: N=4 most common — both origins —
  N=2/N=6 rarer forks). copied_object: menu keycap (shared cached `menu_mesh`).
  naming `menu_key_{i}`. placement: evenly spaced across `menu_strip` width
  (strip widens for N=6). joint_policy: each an independent PRISMATIC press.
  gating: 0 for touchscreen_slab.
- **numeric keypad** — fixed 12 (3×4 dial pad), loop-emitted, **not** an N-sweep
  (payment pads are standardized at 12). keypad_wedge only.
- **command keys** — fixed semantic triad (red cancel / amber clear / green
  enter). keypad_wedge only. Not an N-sweep.
- **side buttons** — fixed 2 (power + function), touchscreen_slab only. Not an
  N-sweep.
- **rubber feet** — fixed 4, migrate to the support part in dock/pedestal. Not
  an N-sweep.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | flat monobody (A,B) / dock_base→housing recline / stand_base→housing yaw / +display_head sub-part / touchscreen removes keypad sub-tree + adds side buttons. all forked_anchor (Slot A/B/C). |
| └ multiplicity | 同构件 ×N | 有 | soft key row N∈{2,4,6} — 见 §8 (weighted, N=4 高频) |
| ② 关节类型 | 换 type/轴 | 有 | PRISMATIC key press (-Z), PRISMATIC card slide (+X), PRISMATIC side button (+Y), REVOLUTE printer cover (-Y), REVOLUTE display tilt (-Y), REVOLUTE dock recline (-Y), REVOLUTE pedestal yaw (+Z), CONTINUOUS paper-roll spindle (+Y). 每种都在 sweep 出现。source-backed (origins + forks). |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | keypad_wedge = Volumetric Envelope Form (wedge block); touchscreen_slab = Planar Boundary Form (dominant flat screen). 2 candidates: 源池仅 2 个真实主体形态 (payment terminals 内在形态窄——手持楔块 vs 平板触屏)，样本不足降到 2 并说明，登记进 `slot_choices` 的 `body_form` slot. source-backed (origin + var_body_touchscreen). |
| ④ 表面装饰 | 叠加表面细节 | 有 (record_only / companion) | screen graphics (AMOUNT/NFC glyph/status bar), key legends, serrated tear bar, card logo+band, dock contact pads, pedestal chrome weight-ring. 均由宿主表面派生的 fused visual，非独立 part/joint。不用于撑多样性预算。 |
| ⑤ 尺寸/行程 | 只改连续尺寸/行程 | 有 | body_len_half [0.083,0.100], width_half [0.037,0.045]; 运动包络: key press axis -Z [0,key_travel≤0.0022]; card slide axis +X [0,0.018]; side button axis +Y [0,0.0015]; printer cover axis -Y [0,cover_open_upper≤1.7]; display tilt axis -Y [0,≤0.6]; dock recline axis -Y [0,≤0.35]; pedestal yaw axis +Z [-1.4,1.4]; paper roll CONTINUOUS 整圈. `motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` per mechanism (key down, cover up, card out, tilt up, recline up, yaw lateral, spindle spin). captured pivots (roll axle, hinge boss, key seat, card-in-slot, body-on-tray) 用 element-scoped `allow_overlap`. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | silver plastic (A) / gray plastic (B) / graphite; charcoal deck, black keys, red/amber/green command keys, blue/pale screen, white paper, blue card. companion; ≥3 themes. |

①②③ + N 为 candidate-anchor 轴且 source-backed。④⑤⑥ record_only/companion，不撑预算。

## 采样与覆盖审计

总组合数 (topology slot tuples)：
- keypad_wedge: support(3) × display(2) × card(2) × roll(2) × N(3) = 72
- touchscreen_slab: support(3) × card(2) × roll(2) = 12
- 合计 **84** distinct slot tuples（display/keys gated on body_form）。

理由：small handheld electronic，deliberately low-normal band；84 >> 36 seeds，
report-only topology target 满足（well above 300 不适用于此窄形态类，实际组合空间
84 已覆盖全部真实源锚点，无兼容 padding）。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
先采所有 enum slot（加权：body_form 偏 keypad_wedge；N 偏 4），再采连续尺度并
clamp，最后按 body_form 解析 conditional（touchscreen → fixed_display,
soft_key_count=0, no numeric/command）。无 regression override。viewer 目检 seeds 0-2。
Topology target：84 真实 tuple；report-only。
Controlled local parameterization：`body_len_half`, `body_width_half`,
`key_travel`, `cover_open_upper`, `tilt_upper`, `recline_upper`, `yaw_limit`——
均在 `resolve_config` clamp/derive，menu strip 宽随 N 派生，不破坏 interface /
clearance / joint origin / identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order support→body→display→card→roll→N，weighted choice，conditional gates | slot_choices_for_seed matches build choices |
| compatibility matrix | tilt_display & keypad sub-tree & soft keys 仅 keypad_wedge；touchscreen 强制 fixed + side buttons；其余 slot 自由组合 | no floating / collision / axis / bulky-module / optional-child failures |
| controlled local variation | continuous scales clamped/derived in resolve_config | proportions vary without breaking interfaces/clearance/support/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass; 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 3 | yes | yes | |
| body_form | 2 | yes | no | 窄形态类，源池仅 2 真实主体形态；已说明 |
| display_mount | 2 | yes | no | tilt gated on keypad_wedge |
| card_interface | 2 | yes | no | |
| paper_roll | 2 | yes | no | |
| soft_key_row (N) | 3 | yes | yes | N∈{2,4,6} |

## Validator

- slot_choices_for_seed returns implemented module names + N encoding
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (incl. 0)
- compatibility gating in resolve_config prevents illegal combos (tilt on touchscreen, keys on touchscreen)
- no regression overrides
- controlled local scales clamped/derived in resolve_config
- critical joints present with expected type/axis/range (cover REVOLUTE -Y, spindle CONTINUOUS +Y, card PRISMATIC +X, tilt REVOLUTE -Y, recline REVOLUTE -Y, yaw REVOLUTE +Z, key PRISMATIC -Z)
- copied menu keys follow `menu_key_{i}` naming + even spacing

## Reject cases

- Numeric keypad count varied off 12 (unfaithful — standardized dial pad).
- Removing display OR all card interface OR printer → drifts to mPOS dongle / neighbor.
- A floating decoration (screen graphic / tear bar / logo) emitted as a FIXED part instead of a fused host visual.
- tilt_display or menu/numeric keys emitted on a touchscreen_slab body.
- Support part present but housing not seated on it (floating child).
- Printer cover / display tilt swept range that intersects the display or paper roll mid-travel.
- Continuous paper-roll spindle whose axle isn't captured in the bay walls (isolated part).

## 与相邻类别的边界

- 不该混入：cash register / drawer POS（收银抽屉是不同结构层，POS 终端无现金抽屉）。
- 不该混入：tablet / smartphone（无支付读卡/打印 I/O，纯消费电子）。
- 不该混入：self-checkout kiosk / floor tower（落地整机，不是手持/台面终端）。
- 不该混入：barcode / handheld scanner（无键盘/显示/支付，纯扫描枪）。
- 不该混入：bare mPOS card dongle（无 display/keypad/printer，退化为读卡狗）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | body_form 降到 2 candidate 已说明（窄形态类，源池 2 真实主体形态）；所有 candidate forked_anchor |

## 模板实现备注
- Frame = origin A (silver, +X front). touchscreen (origin-B frame) adapted into the A frame.
- All non-FIXED joints grandfathered on `MatingContract` (mechanical/captured/seated geometry — like `monitor_mount`); support path via real contact + element-scoped `allow_overlap` for captured pairs (roll axle↔bay, hinge boss↔bracket, key seat↔deck margin, card↔slot, housing↔tray/collar).
- Shared cached keycap mesh reused for all numeric/menu keys (compile budget).
- Support part vs housing: housing seats on tray/collar plane; joint origin on that plane.
