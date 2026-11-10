# Technology_Graphics_Card — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Graphics_Card` |
| template path | `agent/templates/Technology_Graphics_Card.py` |
| test path (optional) | `tests/agent/test_graphics_card_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` (dominant axis = number of cooling fans N; secondary named-slot enums for shroud form / backplate / power / support) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 (4 origins + 4 converged variants) |
| read_count | 8 |
| read_scope | all rating-5 samples adopted by the source map (data/records/) |
| source_index_policy | only adopted module sources are indexed below (see §14) |

阅读要点（每条附 real model.py:Lx-Ly）:

- MSI Trio (rec_...e43c8fd4, N=3) — `board` part fuses PCB (L169-183), PCIe fingers (L185-197), fin stack loop
  `for i in range(37)` (L199-218), heatpipes (L221-227), fan motor pods (L230-236), single `power_connector_8pin`
  block (L239-244), cadquery I/O bracket (`_build_bracket_mesh` L118-150, placed L247-253). `shroud` part is a
  cadquery `shroud_top_plate` (2 rect windows + 3 fan holes, `_build_shroud_plate_mesh` L83-113, placed L294-299)
  + skirt walls (L302-327) + angular gunmetal accent straps/wedges (L329-377) + RGB diffuser strip (L389-394).
  Fans looped `for i in range(3): _add_fan` (L440-441); rotor `FanRotorGeometry` (`_build_fan_rotor_mesh`
  L151-166) + red-ring/black-cap/white-dragon hub badge (L411-429); each `fan_{i}_spin` CONTINUOUS axis (0,0,1)
  (L450-459). `shroud_mount` FIXED (L443-449).
- Gigabyte dual-fan (rec_...c9301248, N=2, BACKPLATE PRESENT) — separate pcb/backplate/bracket/heatsink/shroud
  parts FIXED to pcb. `backplate.plate` cadquery holed plate w/ rect vent cutout (`_holed_plate` L59-76, plate
  L167-180) + `brand_plate` (L182-187) + `screw_{i}` loop (L188-196); `pcb_to_backplate` FIXED (L198-200). Bracket
  cadquery plate w/ DP/HDMI holes (L221-230). Shroud cadquery faceplate w/ 2 circle holes (L300-313) + corner
  ridge accents loop (L352-369). Fans looped `for i,fx in enumerate(FAN_X)` (L375-416), `FanRotorGeometry`
  rotor (L378-394), `heatsink_to_fan_{i}` CONTINUOUS axis (0,1,0) (L408-416).
- RTX 4090 Founders (rec_...ccf04675, N=2 flow-through) — `shroud.top_panel` cadquery plate-with-hole stops
  mid-card (L236-247) + `bottom_panel` (BOT_PANEL_X_MAX=0.045 open flow-through, L250-260) + finned `fin_tail_{i}`
  loop (L267-275); `_add_fan_bay` helper (L143-194) frames the two bays (L264-265). Fans hand-written
  `tail_fan`/`bracket_fan` parts (L353-372) on CONTINUOUS `tail_fan_spin`/`bracket_fan_spin` (L454-472, opposite
  face flipped axis). NO backplate.
- ZOTAC compact (rec_...b4e75c5b, N=1) — pcb/heatsink/shroud/bracket/fan_rotor parts. Shroud cadquery `face_plate`
  w/ real through-hole (L219-234) + `fan_well_ring` (L236-244) + copper accent strips & ZOTAC lettering
  (L262-265) + diagonal slat vent loop (`_slat_segments` L123-137, L268-280). Single `fan_rotor`, `LoftGeometry`
  blades looped `blade_{i}` (L110-120, L370-376); `fan_spin` CONTINUOUS axis (0,1,0) (L405-413). NO backplate.
- blower variant (rec_graphics_card_var_blower, N=1) — enclosed cadquery face plate w/ rectangular top intake
  cutout (L172-201) + intake grille bar loop (L204-…) + tilted exhaust louver ribs loop (L237-252); rotor
  `BlowerWheelGeometry` squirrel-cage `cage_wheel` (L316-339) on CONTINUOUS `fan_spin`.
- power triple-8pin variant (rec_graphics_card_var_power_triple_8pin) — `_power_connector_8pin_geometry` helper
  (L169-171) + looped `for i in range(n_8pin=3): power_connector_8pin_{i}` at even pitch on the PCB top edge
  (L244-254).
- power 12VHPWR variant (rec_graphics_card_var_power_12vhpwr) — single wide `power_connector_12vhpwr` housing
  (L240-245) + small `power_connector_sense_band` (L246-252).
- support-bracket variant (rec_graphics_card_var_support_bracket, N=3) — `support_foot_hinge_lug` boss on the
  board tail (L285-291) + `support_foot` part (`_add_support_foot` L443-464: `foot_strut` + `foot_pad`) on a
  `support_foot_hinge` REVOLUTE joint axis (1,0,0) limits [0, π/2] (L500-510); deploy tested at q=π/2 (L682-692).
  The three fan CONTINUOUS joints are unchanged.

## 核心身份

A discrete PC add-in graphics card: a PCB board carrying a gold PCIe x16 edge connector (hangs below the board
bottom edge), a finned aluminum heatsink, an I/O bracket at the front (-X) end with DisplayPort/HDMI openings, an
axial-fan cooler shroud on the front face, and N spinning cooling fans (N∈{1,2,3}) — the defining kinematic
feature. Optional rear backplate, optional top-edge PCIe power connector, optional fold-out anti-sag support
foot. Default mature domain = consumer open-axial gaming card (1–3 fans). The N fans are always present as
CONTINUOUS spin joints, so every seed keeps ≥1 non-FIXED joint.

不该混入: fanless/passive cards (0 moving joints — excluded), AIO water-block cards (pump+tubes, out of category),
motherboards/other PCBs (no cooler shroud + fans), case fans (a fan alone is box_fan, not a card).

## 槽位 + 候选模块表

Non-moving structure (heatsink, shroud, bracket, backplate, power block, decorations) is fused into the single
grounded `card_body` part as named visuals (Rule 1). The only separate PARTS are `card_body`, the N `fan_{i}`
rotors (CONTINUOUS), and the optional `support_foot` (REVOLUTE). Slots A/C/D vary the ③ form / ④ decoration
visuals on `card_body`; slots B/E vary part+joint topology.

### Slot A：cooler_shroud_form  (③ Primary Form Family — Macro Surface Construction / Volumetric Envelope)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| open_axial_gaming | forked_anchor | rec_...e43c8fd4 (MSI) / rec_...c9301248 (Gigabyte) | e43c8fd4 L294-394 / c9301248 L300-369 | eligible if compatible | flat cadquery faceplate, N open circular fan windows, angular gunmetal accent straps/wedges + RGB diffuser strip |
| compact_itx_open_axial | forked_anchor | rec_...b4e75c5b (Zotac) | L219-280 | eligible if N==1 | short rounded-corner faceplate, 1 fan window + well ring, copper accent strips + diagonal slat vent flanks |
| flow_through_founders | forked_anchor | rec_...ccf04675 (Founders) | L236-275 | eligible if compatible | dual top/bottom panels, faceplate stops mid-card leaving OPEN finned flow-through tail duct, silver chevron trim |
| blower_radial | forked_anchor (converged) | rec_graphics_card_var_blower | L172-252 | eligible if N==1 | fully enclosed faceplate, top-edge rectangular intake grille bars + bracket-end tilted exhaust louvers |
| vapor_chamber_full_cover | world_knowledge_extrapolation (Macro Surface Construction) | anchors: MSI+Gigabyte+Founders + reviewer | template-side (full-cover flag) | eligible if compatible | same part tree/interface, full-cover unbroken faceplate skin; only macro surface read changes; form_subtype=Macro Surface Construction |

### Slot B：fan_count_multiplicity (N)  — dominant axis; see §8

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| N=1 | forked_anchor | rec_...b4e75c5b (Zotac) | L348-413 | eligible | single central axial rotor + fan_spin CONTINUOUS |
| N=2 | forked_anchor | rec_...c9301248 (Gigabyte) | L375-416 | eligible | two side-by-side rotors, looped heatsink_to_fan_{i} CONTINUOUS |
| N=3 | forked_anchor | rec_...e43c8fd4 (MSI) | L440-459 | eligible | three rotors, looped fan_{i}_spin CONTINUOUS |
| N=4 | world_knowledge_extrapolation (multiplicity; N never counts toward distinctness) | anchors: N∈{1,2,3} | template-side (fan_count=4 same loop) | eligible if L≥0.34 | four rotors on a long card; upward extrapolation of the same copy loop |

### Slot C：backplate

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| absent | forked_anchor | rec_...e43c8fd4 / rec_...b4e75c5b / rec_...ccf04675 | (no backplate visual) | eligible | bare PCB rear face |
| present_with_cutout | forked_anchor | rec_...c9301248 (Gigabyte) | L156-196 | eligible | full metal backplate visual (rear -Z), rect vent cutout, brand strip + screw dots |
| present_solid | world_knowledge_extrapolation (④ host-conformal / remove cutout) | anchors: Gigabyte + reviewer | template-side (cutout=False) | eligible | same backplate visual, full coverage without vent cutout |

### Slot D：power_connector

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_8pin | forked_anchor | rec_...e43c8fd4 (MSI) | L239-244 | eligible | one PCIe 8-pin block on the top (+Y) edge |
| row_8pin (n_8pin∈{2,3}) | forked_anchor (converged) | rec_graphics_card_var_power_triple_8pin | L169-171, L244-254 | eligible if L≥0.24 | looped power_connector_8pin_{i} copy row at even pitch |
| 12vhpwr_16pin | forked_anchor (converged) | rec_graphics_card_var_power_12vhpwr | L240-252 | eligible | single wide 12V-2x6 housing + small sense sub-band |
| absent | record_only | Zotac/Gigabyte/Founders model no power block | template-side (power=none) | eligible if L<0.24 | low-power / slot-powered compact card |

### Slot E：articulation_mechanism (② joint type beyond the always-present fans)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fans_only | forked_anchor | all 4 origins | e43c8fd4 L450-459 | eligible | N fan_{i}_spin CONTINUOUS only |
| foldout_support_foot | forked_anchor (converged) | rec_graphics_card_var_support_bracket | L285-291, L443-464, L500-510 | eligible | support_foot_hinge_lug + support_foot part + support_foot_hinge REVOLUTE axis (1,0,0) [0,π/2]; keeps N fan CONTINUOUS joints |

硬约束满足: 每 slot ≥2 candidate; A=5, B=4, C=3, D=4, E=2. Slot A 是形态主导 ③ slot,登记进 slot_choices。

## 槽位图（slot graph）

pattern: multiplicity (+ parallel-children fused body)

```
card_body (ROOT, grounded)
  ├─ visuals: pcb + pcie_fingers + display_ports + heatsink fins/heatpipes/motor_bosses + io_bracket
  ├─ Slot A cooler_shroud_form  -> shroud faceplate + accents + vents  (VISUALS on card_body)
  ├─ Slot C backplate           -> backplate plate + brand + screws     (VISUALS on card_body, rear -Z)
  ├─ Slot D power_connector     -> power block(s)                       (VISUALS on card_body, top +Y edge)
  ├─ Slot B fan_count xN  --[CONTINUOUS spin, axis (0,0,1), origin on motor_boss_i]--> fan_{i} (rotor part)
  └─ Slot E support (optional) --[REVOLUTE, axis (1,0,0), [0,π/2], origin on support_foot_hinge_lug]--> support_foot
```

- Fans: parent=card_body, child=fan_{i}; joint origin at each fan center on the motor boss; rotor hub seats on
  the boss (captured-pin -> allow_overlap + expect_contact, grandfathered no-mating per AUTHORING Rule 2 carve-out
  for axisymmetric captures).
- Support foot: parent=card_body, child=support_foot; joint origin on support_foot_hinge_lug at the tail (+X, -Y
  edge); captured-pin hinge (grandfathered, allow_overlap lug<->strut).
- Slots A/C/D are non-moving -> fused visuals; mutually independent given fan count / length gates (§9 matrix).

## 每槽位 Module Emits / Interfaces

### Slot A / module open_axial_gaming
| emits | 描述 | 来源 |
|---|---|---|
| parts | (visuals on card_body): shroud_faceplate (cadquery holed plate), top/bottom_shroud_rail, io_end_cap, tail_cap, accent_strap_*/accent_wedge_*, rgb_diffuser_strip | MSI L294-394 / Gigabyte L300-369 |
| internal joints | none (all fused) | — |
| upstream interface | fused to card_body top (+Z) face at shroud_z | MSI L294-299 |
| downstream interface | N fan windows at fan centers (radius=fan_r+margin) receive fan_{i} rotors | MSI L104-113 |

### Slot B / module fan_{i}
| emits | 描述 | 来源 |
|---|---|---|
| parts | fan_{i} rotor: FanRotorGeometry mesh (rotor_blades) + hub_ring + hub_cap + off-axis hub_badge chip | MSI L398-430 / Gigabyte L378-407 |
| internal joints | fan_{i}_spin CONTINUOUS, axis (0,0,1), origin on motor boss | MSI L450-459 |
| upstream interface | rotor hub seats on motor_boss_{i} (captured-pin, grandfathered) | MSI L230-236,477-492 |
| downstream interface | none | — |

### Slot C / module present_with_cutout
| emits | 描述 | 来源 |
|---|---|---|
| parts | (visuals on card_body): backplate_plate (cadquery, rect vent cutout), backplate_brand, backplate_screw_{i} | Gigabyte L156-196 |
| internal joints | none (fused; source uses FIXED, here fused per Rule 1) | Gigabyte L198-200 |

### Slot D / module row_8pin
| emits | 描述 | 来源 |
|---|---|---|
| parts | (visuals) looped power_connector_8pin_{i} at even pitch on top edge | triple_8pin L244-254 |
| internal joints | none | — |

### Slot E / module foldout_support_foot
| emits | 描述 | 来源 |
|---|---|---|
| parts | support_foot_hinge_lug (visual on card_body) + support_foot part (foot_strut + foot_pad) | support_bracket L285-291,443-464 |
| internal joints | support_foot_hinge REVOLUTE, axis (1,0,0), [0,π/2], origin on lug | support_bracket L500-510 |
| upstream interface | strut pivot bore captured on hinge lug barrel (grandfathered) | support_bracket L650-663 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cooler_shroud_form | enum | {open_axial_gaming, compact_itx_open_axial, flow_through_founders, blower_radial, vapor_chamber_full_cover} | open_axial_gaming | choice | weighted draw; blower/compact require N==1 | Slot A |
| fan_count (N) | int | [1, 4] | 3 | choice | weighted (§8); N=4 requires L≥0.34 | Slot B |
| backplate | enum | {absent, present_with_cutout, present_solid} | absent | choice | any | Slot C |
| power_connector | enum | {single_8pin, row_8pin, 12vhpwr_16pin, absent} | single_8pin | conditional | row_8pin/12vhpwr require L≥0.24 | Slot D |
| n_8pin | int | [2, 3] | 2 | conditional | only when power_connector==row_8pin | triple_8pin L244 |
| support_bracket | enum | {fans_only, foldout_support_foot} | fans_only | choice | any | Slot E |
| palette_style | enum | {all_black_gaming, gunmetal_gray, black_rgb, zotac_copper, founders_silver, white_rgb} | all_black_gaming | choice | drives every .visual material | ⑥ (§8.5) |
| card_length (L) | float | [0.165, 0.345] | derived | conditional | L ≥ 0.150 + 0.058·N (fan pitch); clamp | MSI L55 / Zotac L42-44 |
| card_height (H) | float | [0.100, 0.135] | 0.120 | independent | uniform sample + clamp | MSI L56 |
| pcb_thickness | float | [0.0016, 0.0024] | 0.0018 | independent | thin board | MSI L59 |
| cooler_thickness (Z) | float | [0.030, 0.058] | 0.045 | independent | 2-slot->3-slot envelope | MSI L67-68 |
| fan_radius | float | [0.030, 0.048] | derived | inequality | fan_r ≤ min(H/2 − 0.007, pitch/2 − 0.004); clamp | Zotac L58 / MSI L65 |
| blade_count | int | {9, 11, 13, 14} | 11 | independent | shared across the N rotors | MSI L155 / Gigabyte L381 |
| fin_count | int | [14, 37] | 24 | independent | dense fin stack | MSI L211 / Gigabyte L257 |
| (—) | constraint | — | — | inequality | Σ fan footprint along X ≤ L − margins; else shrink fan_radius then reduce N | interface/clearance |

连续尺寸采样契约: (1) 采 independent (H, pcb_t, cooler_t, fin_count, blade_count); (2) 派生 conditional L 下界 by
N and power; (3) 投影 fan_radius by height/pitch inequality; (4) 解析 power/shroud conditional by N/L. 全部在
resolve_config 内求解。

### 7.5 编译预算 / compile budget
Per-seed budget ≤ 20 s (typical ~8–14 s). Costs: one shared FanRotorGeometry rotor mesh reused across all N fans
(generated once); one cadquery shroud faceplate boolean (N circular hole cuts, tolerance 0.0004); optional
cadquery backplate (1 rect cut) and I/O bracket (few port cuts). Tessellation: faceplate/backplate cadquery
tolerance 0.0004; FanRotorGeometry default segments; N identical rotors share ONE mesh path. No per-seed O(n²).
Sweep --compile-timeout 120 is a 3x watchdog, not a quality bar.

## Multiplicity / Copy Logic

- Primary axis fan_count (N): count_param=fan_count, N_range=[1,4] (product域; test偏小). Sampling domain:
  weighted draw N∈{1:0.14, 2:0.36, 3:0.42, 4:0.08}. N samples covered by sources: 1 (Zotac), 2 (Gigabyte+Founders),
  3 (MSI). copied object = rotor part fan_{i}; naming fan_{i} + joint fan_{i}_spin; placement = equal pitch along
  +X across the fan face centered in height (y=0); joint policy = one CONTINUOUS joint per fan, axis (0,0,1),
  origin on motor_boss_{i}, independent spin; shared rotor mesh helper. Emitted via `for i in range(fan_count)`.
- Secondary axis n_8pin: only when power_connector==row_8pin; N_range=[2,3], samples {2, 3(triple_8pin)}; copied
  object power_connector_8pin_{i} (VISUAL on card_body), even pitch along the top edge, all fused (no joint).
  Gated behind card_length≥0.24.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Named skeleton: card_body (fused pcb+heatsink+shroud+bracket) + N fan_{i} rotors + optional support_foot. Topology varies by N (Slot B: 1/2/3/4 fan parts+joints) and Slot E (+1 part +1 revolute). forked_anchor: all 8 sources. |
| └ multiplicity | 同构件 xN | 有 | fan_count N∈[1,4], weighted (§8). Secondary n_8pin∈[2,3]. |
| ② 关节类型 | 换 type/轴 | 有 | CONTINUOUS fan_{i}_spin axis (0,0,1) — every seed (MSI L450-459); REVOLUTE support_foot_hinge axis (1,0,0) [0,π/2] (support_bracket L500-510); FIXED absent (non-moving fused per Rule 1). Both types appear in the sweep. |
| ③ 主体形态家族 | 换核心 part 的可识别几何形态原型 | 有 | Slot A ≥3 forms: open_axial_gaming (form_subtype=Macro Surface Construction, MSI/Gigabyte), compact_itx_open_axial (Planar Boundary Form short rounded plate + slat flanks, Zotac), flow_through_founders (Volumetric Envelope Form split panels + open tail, Founders), blower_radial (Macro Surface Construction enclosed + grille/louver, blower), vapor_chamber_full_cover (Macro Surface Construction, world_knowledge_extrapolation). Registered in slot_choices. |
| ④ 表面装饰 | 叠加表面细节 | 有 | gunmetal angular accent straps/wedges (MSI L329-377), RGB diffuser strip (MSI L389-394), copper accent strips + ZOTAC lettering (Zotac L262-265), corner ridge accents (Gigabyte L352-369), backplate brand strip + screw dots (Gigabyte L182-196), hub badges. record_only + world_knowledge_extrapolation. 装饰随 shroud 面派生 (贴在 shroud_z 面/背板 -Z 面), 随 ③⑤ 共形。All parent .visual (Rule 1), never FIXED parts. |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | L∈[0.165,0.345], H∈[0.10,0.135], cooler_t∈[0.030,0.058], fan_r∈[0.030,0.048] (§7). 关节行程: fan_spin continuous (整圈不穿模 — hole radius>fan_r); support_foot_hinge axis(1,0,0) stow(-Y)->deploy(-Z) [0,π/2]. motion_test_plan: fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96) + targeted ctx.pose({fan_i_spin: π}) badge-displacement + ctx.pose({support_foot_hinge: π/2}) foot-extends-downward. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类: painted metal / plastic shroud / aluminum-nickel fins / gold PCIe / silver steel bracket / translucent RGB diffuser / black-green PCB. palette_style ≥6 colorways: all_black_gaming, gunmetal_gray, black_rgb, zotac_copper, founders_silver, white_rgb. 材质大类覆盖 ≥ ceil(0.5×6)=3. |

收尾自检: batch 0-9 渲染须肉眼见到不同 shroud 形态、不同 N、不同配色、装饰贴合面、fan 全圈不穿模、support foot 展开不穿模。

## 拓扑多样性审计

总组合数 (报告用): A(5) × B(4) × C(3) × D(4) × E(2) = 480 nominal, gated by compatibility (blower/compact require
N=1; row_8pin/12vhpwr require L≥0.24; N=4 requires L≥0.34). Realizable ≫ 100.

理由: A/B/C/D/E 每个在 0-35 seeds 里都实现 ≥2 值。

seed_domain_policy: procedural_first。config_from_seed(seed) uses random.Random(seed) weighted draws for every
slot + continuous scale; compatibility gates resolved in resolve_config (blower/compact->N=1; N drives L lower
bound; power gated by L). No curated/modulo table; seed 0 ordinary. Topology target: 1000-seed distinct ≥300. No（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
regression overrides. Controlled local parameterization: card_length, card_height, cooler_thickness, fan_radius,
fin_count, blade_count — all clamped/derived in resolve_config, none breaks fan-hole<->rotor clearance, motor-boss
seat, or joint origins.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted slot draws + continuous scales; gates in resolve_config | slot_choices_for_seed matches build choices |
| compatibility matrix | blower/compact->N=1; N=4->L≥0.34; row_8pin/12vhpwr->L≥0.24; blower×backplate & flow_through×solid_backplate flagged (airflow) | no floating / collision / axis / max-N / bulky failures |
| controlled local variation | 6 clamped scales above | proportions vary without breaking interface/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass + corner stage; 0-999 maturity | axis_realization / report |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A cooler_shroud_form | 5 | yes | yes | ③ primary form slot |
| B fan_count | 4 | yes | yes | multiplicity (N not counted for distinctness) |
| C backplate | 3 | yes | yes | |
| D power_connector | 4 | yes | yes | |
| E support_bracket | 2 | yes | no | ② joint-type axis; pool has exactly 2 |

## Validator
- slot_choices_for_seed returns implemented module names (cooler_shroud_form, fan_count band, backplate,
  power_connector, support_bracket)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds incl seed 0
- compatibility matrix prevents illegal combos (blower/compact×N>1, short card × wide power)
- no regression overrides
- controlled local scales clamped; fan_radius satisfies height + pitch inequalities
- N fans each on CONTINUOUS fan_{i}_spin axis (0,0,1); support_foot (if present) on REVOLUTE axis (1,0,0)
- rotor hub seats on motor boss (expect_contact); shroud fan windows clear the rotor over full rotation
- fail_if_parts_overlap_in_sampled_poses + targeted ctx.pose for fan spin and foot deploy

## Reject cases
- fanless (0 fans / no CONTINUOUS joint) — violates ≥1 active joint; excluded
- fan blades collide with the shroud faceplate hole edge over a full rotation (hole_r ≤ fan_r) — shrink fan_r
- adjacent rotors overlap (fan pitch < 2·fan_r) — reduce fan_r or N
- support foot swings into the PCB/tail at π/2 (wrong axis/origin) — fix axis (1,0,0)/origin on lug
- backplate penetrates the PCB or floats off the rear face — seat flush at -Z
- power block / bracket / accents modeled as FIXED-joint parts instead of visuals — Rule 1 violation
- decoration built at constant size over a scaled faceplate — derive from the final shroud face (Rule 4)
- N=4 on a short card (L<0.34) -> fan pitch collision — gate N by L

## 与相邻类别的边界
- 不该混入 box_fan / case fan (a standalone axial fan is box_fan; a graphics card is a PCB assembly with a cooler
  + PCIe bracket)
- 不该混入 motherboard / other PCBs (no cooler shroud + spinning fans + PCIe edge connector hanging below)
- 不该混入 AIO liquid cooler / water block (pump+tubes replace fans — out of category)

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Modular multiplicity template; 5 slots (A form / B fanN / C backplate / D power / E support). Fans looped fan_{i} on CONTINUOUS joints, support_foot REVOLUTE. Captured-pin joints grandfathered (no mating) per AUTHORING Rule 2 carve-out, as all 8 sources do. |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S_MSI | A/B/D/E-lug | open_axial_gaming, N=3, single_8pin | rec_...e43c8fd4 | L169-459 | board+shroud+fan loop+power+accents |
| S_GB | A/B/C | open_axial_gaming, N=2, backplate | rec_...c9301248 | L98-416 | backplate+bracket+fan loop |
| S_FE | A/B | flow_through_founders, N=2 | rec_...ccf04675 | L143-472 | flow-through shroud + fan bays |
| S_ZO | A/B | compact_itx_open_axial, N=1 | rec_...b4e75c5b | L144-413 | compact shroud + slat vents + rotor |
| S_BL | A | blower_radial | rec_graphics_card_var_blower | L172-339 | enclosed shroud + grille/louver + cage |
| S_P3 | D | row_8pin | rec_graphics_card_var_power_triple_8pin | L169-254 | looped 8-pin power row |
| S_PV | D | 12vhpwr_16pin | rec_graphics_card_var_power_12vhpwr | L240-252 | 12VHPWR housing + sense band |
| S_SB | E | foldout_support_foot | rec_graphics_card_var_support_bracket | L285-510 | hinge lug + support foot REVOLUTE |
