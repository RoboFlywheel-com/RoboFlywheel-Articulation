# tube_cutter — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `tube_cutter` |
| template path | `agent/templates/tube_cutter.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`parallel_children`：一个 `frame` (root, C 型铸铁/钢板机身) 作为共同 chassis，
挂载所有活动件：`cutter_carriage` (PRISMATIC 进给) + N 个 `guide_roller_i`
(CONTINUOUS/REVOLUTE, side-支承) + `adjustment_knob` (REVOLUTE 螺纹旋钮) +
可选 `reamer` (REVOLUTE 折出去毛刺刀)。`cutting_wheel` 是 `cutter_carriage`
的 CONTINUOUS 子件。所有 11 个 5★ 样本 (3 origins + 8 forks) 都保持这一
"frame + carriage(+wheel) + N rollers + knob" 骨架；变体差异集中在骨架形状
(③)、roller 数量 (①-multiplicity)、feed 硬件形态 (③/②) 和可选 secondary (②)
四根轴上。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all workbench 5★ records under `articraft_data/data/records/rec_0611_tube_cutter_var_*` + `rec_picturex_0611__tube_cutter__001/002/003__*` (source-map–approved; per-record rating null but pool is workbench-only 5★ per `0611__tube_cutter.md`) |
| source_index_policy | only adopted module sources are indexed below |

- **P1** = `rec_picturex_0611__tube_cutter__001__png_2cdbda5a722043988b55f5c37497d26c`
  (`compact_handheld_tube_cutter`). Silver machined-aluminum C-frame with a
  hollow cylindrical handle housing that receives a long threaded feed screw;
  ADJUSTMENT_KNOB is a knurled `KnobGeometry` at the handle butt (REVOLUTE
  about handle axis X). Two vertically stacked guide rollers, one cutter wheel
  on the carriage yoke, cutter feed PRISMATIC along the handle axis. Blue
  elastomer side grip + collar. `revisions/rev_000001/model.py` L35-L689.
- **P2** = `rec_picturex_0611__tube_cutter__002__png_20317f26aa01480f9571cba45f69fada`
  (`compact_c_frame_tube_cutter`). Cast-aluminum ring C-frame with tapered
  cast stem to a red-lobed knob at the bottom; carriage runs UP through the
  frame guide slot (PRISMATIC, axis Z) driven by a threaded screw whose knob
  sits BELOW the throat. 2 rollers on one horizontal cross-pin above the
  cutter wheel; both stamped side plates capture the roller pins.
  `model.py` L33-L679.
- **P3** = `rec_picturex_0611__tube_cutter__003__png_8079a52cd8014a2181f7ab795e321303`
  (`blue_c_frame_tube_cutter`). Blue thick C-frame with a top thread-bridge,
  T-handle knob turning above the bridge, carriage sliding DOWN into the
  throat on two guide rails, cutter wheel spinning below the carriage.
  `model.py` L20-L546.
- **V1** = `rec_0611_tube_cutter_var_roller_count_3` — extends P2 to 3 guide
  rollers (`ROLLER_CENTERS` array grown), otherwise same topology. Source for
  Slot B N=3.
- **V2** = `rec_0611_tube_cutter_var_roller_count_4` — extends P3 to 4 guide
  rollers. Source for Slot B N=4.
- **V3** = `rec_0611_tube_cutter_var_feed_ratchet` — P1 with an added ratchet
  pawl visual and a longer feed screw travel; still a single REVOLUTE knob +
  PRISMATIC carriage. Ratchet visualized as pawl+ring on the knob visual set.
- **V4** = `rec_0611_tube_cutter_var_feed_quick_release` — P3 with a squeeze
  quick-release lever visualized as an extra grip visual on frame; feed
  PRISMATIC range shortened.
- **V5** = `rec_0611_tube_cutter_var_frame_open_c_frame` — P2 with a wider
  open C-throat; still `frame` + rollers + carriage + wheel + screw.
- **V6** = `rec_0611_tube_cutter_var_frame_chain_cutter` — P1 with a longer
  C-frame outer arm that visually reads as a chain-style outer jaw; kept
  identical part tree.
- **V7** = `rec_0611_tube_cutter_var_secondary_fold_out_reamer` — P2 with an
  added `reamer` REVOLUTE part (fold-out flat blade) on the frame stem. THIS
  is the only 5★ variant that introduces a new moving part; used for Slot D
  `secondary=fold_out_reamer`.
- **V8** = `rec_0611_tube_cutter_var_wheel_module_quick_change_cutter_wheel`
  — P1 with a quick-change cutter wheel visible as a larger hub cap; still
  same joints/parts. Source for ④ decoration + ③ wheel_hub variant.

All 11 records use exactly one `cutter_carriage`, one `cutting_wheel`, N∈{2,3,4}
`guide_roller_i`, one adjustment knob (REVOLUTE), and optionally one `reamer`
(REVOLUTE). No 5★ sample introduces additional independent moving parts.

## 核心身份

Tube cutter = a real-world hand tool that scores/cuts round metal tubing by
clamping the tube between opposed guide rollers and a sharp circular cutter
wheel, then advancing the cutter into the tube via a screw-driven carriage
while the tool is rotated around the tube. Physical spine: **C/O-frame chassis
holding an opposed set of guide rollers, a screw-advanced cutter carriage
with a spinning cutter wheel, and a hand-turned adjustment knob at the screw
end**. Default mature domain: hand tubing cutters up to ~40 mm capacity;
cast-aluminum or forged steel frame; knob or T-handle at the screw end.

Must NOT drift into:

- `pilers_cutting_pliers` / other pliers (opposed jaws with a hinge, no
  circular cutter wheel, no roller pair).
- Guillotine paper cutter (blade drops on a flat bed; here the cutter is a
  small opposed disc riding on a screw).
- Pipe wrench / chain wrench (no cutting wheel).
- Reamer / deburring tool (may be an optional fold-out addition here, but not
  the whole tool).

## 槽位 + 候选模块表

### Slot A：frame_form (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| compact_c_frame | forked_anchor | P2 (`rec_picturex_0611__tube_cutter__002__png_*`) | L33-L102 (`_frame_shape`) + L104-L129 (`_side_plate_shape`) | eligible if compatible | Cast ring C-frame with a circular throat centered above the stem; cast tapered stem connects the C-head to a bottom screw-collar. Volumetric Envelope Form (`form_subtype=Volumetric Envelope Form`): a solid revolved ring + tapered stem envelope. |
| handheld_c_frame | forked_anchor | P1 (`rec_picturex_0611__tube_cutter__001__png_*`) | L35-L167 (`_frame_shape`) | eligible if compatible | Broad C-head on the left (throat opens toward -X) + long cylindrical handle housing on the right (hollow tube receiving the feed screw). Silhouette reads as an in-line hand tool. Planar Boundary Form (`form_subtype=Planar Boundary Form`): the frame is a flat XZ profile extruded thin in Y. |
| blue_c_frame_top_bridge | forked_anchor | P3 (`rec_picturex_0611__tube_cutter__003__png_*`) | L31-L106 (`_c_ring`, `_build_frame_body`, `_build_top_bridge`) | eligible if compatible | Thick vertical C-frame with a raised top bridge that captures the threaded screw and receives the T-handle knob from above; carriage slides down between two guide rails. Macro Surface Construction (`form_subtype=Macro Surface Construction`): the tall body + top-bridge changes the tool's silhouette from the compact ring version. |

### Slot B：roller_count (①-multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rollers_2 | forked_anchor | P1/P2/P3 | P2 L227-L314 (`ROLLER_CENTERS=((..),(..))`) | eligible if compatible | Two guide rollers on one cross-pin plane; the classical compact configuration. |
| rollers_3 | forked_anchor | V1 (`rec_0611_tube_cutter_var_roller_count_3`) | L27-L28 (ROLLER_CENTERS list), body identical to P2 | eligible if compatible | Three guide rollers spread across a wider arc for better tube support; V1 grows the array from 2 to 3 while keeping the same frame + carriage + wheel. |
| rollers_4 | forked_anchor | V2 (`rec_0611_tube_cutter_var_roller_count_4`) | L27-L28 (roller centers), body based on P3 | eligible if compatible | Four guide rollers arranged in a square around the throat, for large-diameter tubing. |

### Slot C：feed_hardware (② + ③ 手柄形态/末端硬件)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rotating_knob | forked_anchor | P2 | L367-L419 (`adjustment_screw` + `KnobGeometry`) | eligible if compatible | Lobed / knurled rotary knob mounted on the frame's screw bore; REVOLUTE about the screw axis. Compact hand-fed style. |
| t_handle | forked_anchor | P3 | L329-L347, L386-L394 (`knob` part with crossbar + two `_build_t_grip` cylinders + hub) | eligible if compatible | T-shaped cross-handle: a horizontal bar with two knurled cylindrical grips on each end + a central hub attaching to the screw. REVOLUTE about the screw axis. |
| ratchet_screw | forked_anchor | V3 (`rec_0611_tube_cutter_var_feed_ratchet`) | reamer-style ratchet visuals added around a P1-style knob + screw shaft | eligible if compatible | P1-style knurled knob + an added ratchet pawl inline visual (ring gear + pawl bar) on the knob part. Still a single REVOLUTE joint; the ratchet is a decorative + functional-hardware overlay. |

### Slot D：secondary (② optional hardware)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | forked_anchor | P1 + P2 + P3 | (no extra part) | eligible if compatible | No secondary tool. The default configuration in every base sample. |
| fold_out_reamer | forked_anchor | V7 (`rec_0611_tube_cutter_var_secondary_fold_out_reamer`) | L165-L191 (`_reamer_blade_shape`), L502-L541 (`reamer` part + `reamer_fold` REVOLUTE joint) | eligible if compatible | Adds one `reamer` part joined to the frame stem via a REVOLUTE joint (axis Y); a flat tapered deburring blade that folds out from the handle. Only additional moving part; joint is source-backed and uses element-scoped allow_overlap for the captured pivot pin. |

## 槽位图（slot graph）

pattern: `parallel_children`

```
frame (root; holds guide-roller cross-pins, side plates, screw bore, ratchet
       ring / t-handle bridge decoration as inline visuals)
 ├─[REVOLUTE, axis (0,1,0), origin=roller_center_i]─▶ guide_roller_i  (i=0..N-1)
 ├─[PRISMATIC, axis=carriage_axis, origin=carriage_origin]─▶ cutter_carriage
 │                                                            └─[CONTINUOUS, axis (0,1,0)]─▶ cutting_wheel
 ├─[REVOLUTE, axis=screw_axis, origin=knob_seat]─▶ adjustment_knob
 └─[REVOLUTE, axis (0,1,0), origin=reamer_pivot]─▶ reamer   (only if Slot D = fold_out_reamer)
```

- All non-FIXED joints have `MatingContract` referencing real host visuals on
  the frame (side plates, cross-pin bosses, screw bore boss, ratchet housing,
  handle bridge). Captured-pin geometries (guide-roller hubs around cross
  pins; cutter-wheel hub around the carriage axle; reamer bore around its
  pivot pin) use element-scoped `ctx.allow_overlap` and either a
  `MatingContract` (when a clean axis-aligned face exists) or the grand-
  fathered path (pin-through-sleeve) with a source-record justification.
- `cutting_wheel` is a CONTINUOUS child of `cutter_carriage` (not of frame),
  matching every 5★ sample; its origin is at the carriage axle and its axis
  is (0,1,0).
- `guide_roller_i` centers are procedurally placed on a source-derived arc
  around the throat center (`THROAT_CENTER`, `THROAT_RADIUS`) so all N stay
  on the frame's roller boss ring for any N∈{2,3,4}.
- The `adjustment_knob` axis is the screw axis:
  - `compact_c_frame` frame → axis (0,0,1), knob below throat.
  - `handheld_c_frame` frame → axis (1,0,0), knob at handle end.
  - `blue_c_frame_top_bridge` frame → axis (0,0,1), knob above bridge.
- `reamer` (Slot D=fold_out_reamer) is anchored to the frame stem with a
  REVOLUTE joint on axis (0,1,0); its blade folds ±60° in the XZ plane.

## 每槽位 Module Emits / Interfaces

### Slot A / module frame_form (all 3 candidates)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (single mesh from the frame-form helper), plus inline visuals for side plates, roller-boss cross-pins, screw boss/collar decoration, top bridge or T-handle bridge | P1 L273-L295 / P2 L197-L269 / P3 L236-L258 |
| internal joints | none (frame is the root) | — |
| upstream interface | frame's root origin at (0,0,0) | — |
| downstream interfaces (parent for other slots) | `frame.roller_boss_i` (guide-roller mount), `frame.carriage_guide` (carriage rail seat), `frame.screw_boss` (knob mount), `frame.reamer_boss` (reamer mount, only when D=fold_out_reamer) | P2 L69-L74 (guide slot), L76-L84 (screw bore), L112-L146 (roller pockets/pins) |

### Slot B / module roller_count (N ∈ {2, 3, 4})
| emits | 描述 | 来源 |
|---|---|---|
| parts | `guide_roller_0`, …, `guide_roller_{N-1}` | P2 L272-L314 |
| internal joints | `guide_roller_i_spin`: REVOLUTE/CONTINUOUS on axis (0,1,0), origin at roller center | P2 L305-L313 |
| upstream interface | roller hub cylinder sitting inside the frame's `roller_boss_i` cross-pin pocket | P2 L227-L256 |
| downstream interface | — (leaf) | — |

### Slot C / module feed_hardware
- **rotating_knob**: emits `adjustment_knob` part + one CONTINUOUS/REVOLUTE
  joint on the screw axis + inline `screw_shaft` visual pinned to the knob
  part (matching P2 layout where the screw shaft moves with the knob).
  Source: P2 L367-L419.
- **t_handle**: emits `adjustment_knob` part with a horizontal crossbar +
  two knurled ends + central hub + short screw stub inline visual;
  REVOLUTE about the screw axis. Source: P3 L329-L347, L386-L394.
- **ratchet_screw**: emits `adjustment_knob` part = rotating_knob geometry +
  additional ratchet-ring + pawl inline visuals on the knob. Same single
  REVOLUTE joint as `rotating_knob`. Source: V3 ratchet visuals overlaid on
  P1 knob.

All three candidates emit exactly one `adjustment_knob` part + one REVOLUTE
joint to the frame.

### Slot D / module secondary
- **none**: emits nothing extra.
- **fold_out_reamer**: emits `reamer` part (flat tapered blade mesh + hub
  boss inline visual) + one REVOLUTE joint `reamer_fold` on axis (0,1,0)
  anchored to the frame stem. Element-scoped allow_overlap for the reamer
  hub around the reamer pivot pin. Source: V7 L165-L191, L502-L541.

### Root joints (constant structure across candidates; per-candidate origin/axis details noted in slot graph)
| joint | type | axis | 来源 |
|---|---|---|---|
| `guide_roller_i_spin` (i=0..N-1) | CONTINUOUS or REVOLUTE | (0,1,0) | P2 L305-L313 |
| `cutter_carriage_slide` | PRISMATIC | frame-form–dependent (Z for compact/blue; X for handheld) | P2 L420-L432 |
| `cutting_wheel_spin` | CONTINUOUS | (0,1,0) | P2 L434-L441 |
| `adjustment_knob_spin` | REVOLUTE | screw axis (Z or X per frame_form) | P2 L406-L419 |
| `reamer_fold` | REVOLUTE | (0,1,0) | V7 L524-L536 |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | compact_c_frame / handheld_c_frame / blue_c_frame_top_bridge | — | choice | procedural sampler | Slot A |
| `roller_count` | int | {2, 3, 4} | 2 | choice | weighted procedural sampler (small-N heavy) | Slot B |
| `feed_hardware` | enum | rotating_knob / t_handle / ratchet_screw | — | choice | procedural sampler | Slot C |
| `secondary` | enum | none / fold_out_reamer | none | choice | procedural sampler (none plurality) | Slot D |
| `palette_style` | enum | red_cast_aluminum / blue_hand_tool / silver_machined / black_industrial / brass_classical | — | choice | ⑥ palette diversity | ⑥ audit |
| `overall_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform sample then clamp; drives frame footprint | P2 L23-L31 canonical dims |
| `frame_thickness_scale` | float | [0.9, 1.15] | 1.0 | independent | uniform sample; drives FRAME_THICKNESS | P2 L23 |
| `throat_radius_scale` | float | [0.9, 1.10] | 1.0 | independent | uniform sample; drives throat opening radius | P2 L26 |
| `feed_travel_scale` | float | [0.85, 1.15] | 1.0 | independent | drives PRISMATIC upper limit; clamped to [0.008 m, 0.020 m] absolute | P2 L432 |
| `knob_size_scale` | float | [0.85, 1.15] | 1.0 | conditional | knob geometry scaling; slightly different bounds per feed_hardware (T-handle can be longer) | P2 L367-L398 / P3 L329-L347 |
| (—) | constraint | — | — | inequality | `throat_radius_scale × THROAT_RADIUS < FRAME_OUTER_RADIUS × frame_thickness_scale − 0.006` so throat stays inside outer ring wall | frame geometry |
| (—) | constraint | — | — | inequality | `feed_travel_scale × FEED_TRAVEL_BASE ≤ throat_radius × 0.85` so carriage can never travel past the tube envelope | motion clearance |
| (—) | constraint | — | — | inequality | `roller_count ∈ {2,3,4}`; when `frame_form=handheld_c_frame`, `roller_count ≤ 3` (its throat is a stacked pair pattern; 4 rollers don't fit the compact silhouette) | Slot B×A compatibility |

**编译预算 (§7.5)** — 目标 ≤20s/seed。主要成本：一次 cadquery frame mesh
(loft/cut/union of ring + stem + pockets, ~8-14 boolean ops), N 个 roller
lofts + wheel mesh, 一个 carriage mesh, 一个 knob/T-handle mesh, 可选一个
reamer 平面 extrusion. Tessellation: 小半径 pin 特征 (roller pins,
cutter axle, ~0.002 m) tolerance≈0.0006, angular_tolerance≈0.10; frame
englobing mesh tolerance≈0.0004, angular_tolerance≈0.08. N 个 roller
共享同一 `_roller_shape()` 助手（cadquery workplane 结果做 mesh 缓存 by
name; 每个 roller visual 只在 origin 里位移，不重造 mesh key）。若单
seed >20s，先降 loft 采样 + tolerance→0.001, 再考虑替换 loft 为
lathe/lofted circle。

## Multiplicity / Copy Logic

**One multiplicity axis**: `roller_count` ∈ {2, 3, 4}.

- `count_param`: `roller_count`
- `N_range`: {2, 3, 4} (bounded by observed 5★ samples: base 2, V1 has 3,
  V2 has 4; no 5★ record uses N > 4)
- sampling domain: weighted `rng.choices([2,3,4], weights=[6,3,2])` — small
  N heavy, matching the compact-cutter product norm.
- copied object: `guide_roller_i` — one shared `_roller_shape()` helper +
  cadquery loft; N=2..4 identical roller meshes, each attached to a distinct
  cross-pin origin on the frame roller-boss arc.
- naming: `guide_roller_{i}`; joint `guide_roller_{i}_spin`.
- placement: procedurally arranged on a source-derived arc around the throat
  center; angles determined by `_roller_arc_angles(N)`.
- joint policy: uniform CONTINUOUS joints on axis (0,1,0), same
  MotionLimits per roller.
- source/gating: source-backed by V1/V2. Compatibility gate: when
  `frame_form == handheld_c_frame`, clamp N to ≤3 (its narrow silhouette
  doesn't fit 4).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 骨架有两种变体：(a) baseline `frame + N rollers + carriage + wheel + knob` (N ∈ {2,3,4}) 来自 P1/P2/P3/V1/V2; (b) baseline + `reamer` REVOLUTE 子件 (Slot D=fold_out_reamer) 来自 V7. 都 forked_anchor / source-backed. |
| └ multiplicity | 同构件 ×N | 有 | `roller_count` ∈ {2,3,4}, 权重 [6,3,2]. 详见 §Multiplicity. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 每个 5★ 样本都出现 PRISMATIC (cutter_carriage_slide) + REVOLUTE (adjustment_knob_spin, guide_roller_i_spin) + CONTINUOUS (cutting_wheel_spin, and sometimes guide rollers). Slot D=fold_out_reamer 再加一根 REVOLUTE. `feed_hardware` 三个 candidate (rotating_knob / t_handle / ratchet_screw) 都用 REVOLUTE，但在图的这一条边上换硬件外观 = ② 的 "边下硬件" 视觉多样性; forked_anchor / source-backed. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色） | 有 | Slot A (frame_form) 登记进 `slot_choices`，3 个 form subtypes: `compact_c_frame`=Volumetric Envelope Form (revolved ring + tapered stem) / `handheld_c_frame`=Planar Boundary Form (flat XZ silhouette extruded) / `blue_c_frame_top_bridge`=Macro Surface Construction (tall body + top-bridge构成). Slot C 也带 ③ 分量：`rotating_knob`/`t_handle`/`ratchet_screw` 分别是不同 knob primary form. |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Frame side plates, roller-boss cross-pin caps, screw-boss collar rings, thread crests (annular rings on `adjustment_screw`), knurling on knob (via `KnobGrip`), quick-change hub cap on `cutting_wheel` (source: V8) — all derived from host frame/carriage/knob surfaces (host-conformal, 派生顺序 ③→⑤→④). |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | Continuous scales: `overall_scale [0.85,1.15]`, `frame_thickness_scale [0.9,1.15]`, `throat_radius_scale [0.9,1.10]`, `feed_travel_scale [0.85,1.15]`, `knob_size_scale [0.85,1.15]`. **Motion envelopes per non-continuous joint**:<br>• `cutter_carriage_slide` — axis Z (compact/blue) or X (handheld); opening direction = feed toward rollers; `[closed, feasible-upper]=[0, feed_travel_scale × 0.014]`, clamped to ≤ 0.020 m.<br>• `adjustment_knob_spin` — axis Z/X (per frame); range `[0, 12·π]` (multi-turn, matching P2 L413-L418).<br>• `reamer_fold` (D=fold_out_reamer only) — axis Y; range `[0, π/2 + 0.2]` (~104° fold out; matches V7 L534-L541).<br>**motion_test_plan**: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`; targeted `ctx.pose({carriage_slide: upper})` asserts throat gap closes; `ctx.pose({knob_spin: 6·π})` asserts knob rotation is captive (no translation); `ctx.pose({reamer_fold: π/2})` when reamer present asserts blade clears the frame. No sampled-pose exemption. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 5 palettes covering ≥3 material families (metal + painted metal + optional wood/elastomer accent): `red_cast_aluminum` (cast Al + red grip + steel) / `blue_hand_tool` (blue enamel steel + polished steel + blue elastomer) / `silver_machined` (machined aluminum + polished steel + brass hub) / `black_industrial` (black tool steel + polished pins) / `brass_classical` (all-brass + walnut ferrule accent). Metal-family coverage 5/5, painted 2/5, natural/elastomer accent 3/5 — 覆盖 ceil(0.5×5)=3 ✓. Materials named per palette so ⑥ shows in material list. |

## 采样与覆盖审计

总组合数：3 (frame_form) × 3 (roller_count, N band) × 3 (feed_hardware) × 2
(secondary) = **54** discrete tuples (before compatibility gate). After
gate (handheld_c_frame allows N≤3): 3×3×3×2 − 1×1×3×2 = 54 − 6 = **48**
legal tuples. Well over 36-seed initial sweep coverage.

理由：3×3×3×2 slot 组合覆盖每个 candidate 至少 6 次 in 36 seeds. 每个
candidate 都来自具体 5★ 样本 (frame_form 三个 origins; roller_count 从
P1/P2/P3 + V1 + V2; feed_hardware 从 P2/P3 + V3; secondary 从 P1/P2/P3 +
V7). Palette ×5 与 5 个 continuous scales 不参与离散组合计数，但 axis
realization 里会全部出现。

seed_domain_policy: procedural_first (deterministic `random.Random(seed)`).

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` uses
`random.Random(seed)` + weighted `rng.choices` to select the four discrete
slots + palette, then `rng.uniform` to sample the five continuous scales.
`resolve_config` clamps every scale + applies the two compatibility
inequalities (throat inside outer ring; feed travel ≤ 85% throat radius)
+ the frame_form × roller_count compatibility clamp. No curated table
override. Topology target: 48 combos across 36 seeds → axis_realization
should see every slot value at least once; ≥300 tuples across 1000 seeds
for maturity audit (report-only). Regression overrides: none.

Controlled local parameterization:
- `overall_scale [0.85,1.15]` — independent.
- `frame_thickness_scale [0.9,1.15]` — independent; drives FRAME_THICKNESS.
- `throat_radius_scale [0.9,1.10]` — independent; drives THROAT_RADIUS;
  inequality with outer ring wall.
- `feed_travel_scale [0.85,1.15]` — independent; drives PRISMATIC upper
  limit; inequality with throat clearance.
- `knob_size_scale [0.85,1.15]` — conditional on `feed_hardware`
  (T-handle bounds [0.9,1.2] to allow slightly longer crossbars).

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | seed → rng.Random(seed); 4 weighted enum picks + 5 continuous scales | slot_choices_for_seed matches build choices |
| compatibility matrix | handheld_c_frame ↦ roller_count ≤ 3; throat radius ≤ outer ring − 6mm; feed travel ≤ 0.85 × throat | no floating parts; no closed-pose穿模; carriage stays within throat |
| controlled local variation | 5 scales in resolve_config, clamped | frame integrity + motion envelope + interface geometry maintained |
| regression overrides | none | — |
| random sweep | seeds 0-15 (fast), 0-35 (final), corner stage | axis_realization; motion QC across carriage + knob + reamer poses |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 3 | yes | yes | ③ Primary Form Family slot |
| roller_count | 3 | yes | yes | ①-multiplicity axis |
| feed_hardware | 3 | yes | yes | ② + ③ knob hardware/form |
| secondary | 2 | yes | no | 2 是允许的下限（fold_out_reamer 是唯一非-none 变体源自 V7） |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names in
  `(frame_form, roller_count, feed_hardware, secondary)` order (roller_count
  reported as string of the integer, e.g. `"2"`).
- `config_from_seed(0)` succeeds without curated table.
- `resolve_config` clamps every continuous scale; enforces throat ≤ outer
  ring − 6mm, feed travel ≤ 0.85 × throat, and roller-count ≤ 3 when
  handheld_c_frame.
- `cutter_carriage_slide` is PRISMATIC with `lower==0` and
  `upper == feed_travel_scale × 0.014` (or clamped absolute).
- `cutting_wheel_spin` is CONTINUOUS on axis (0,1,0), parented to
  `cutter_carriage`.
- `adjustment_knob_spin` is REVOLUTE on axis matching the frame's screw
  axis; `lower < upper` (multi-turn range).
- Every non-FIXED joint has a `MatingContract` referencing real frame /
  carriage / knob visuals (except captured-pin geometries which are
  grandfathered with element-scoped `ctx.allow_overlap` and a source-cited
  reason).
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48,
  ignore_fixed=True)`.
- Targeted `ctx.pose({carriage_slide: upper})`: throat gap between cutter
  wheel and nearest guide roller shrinks by ≥ 60% of the rest gap.
- Targeted `ctx.pose({knob_spin: 6·π})`: knob world position unchanged
  (rotational-only, captive).
- When `secondary == fold_out_reamer`: `object_model.get_part("reamer")`
  exists; `reamer_fold` REVOLUTE joint exists on axis (0,1,0);
  targeted `ctx.pose({reamer_fold: π/2})` puts the blade tip clear of the
  frame envelope.
- Materials list carries the palette-style tag so ⑥ palette diversity is
  reflected in `object_model.materials`.
- `slot_choices` recorded on `object_model.meta`.

## Reject cases

- Cutter wheel joined to `frame` instead of `cutter_carriage` (breaks the
  feed mechanism: wheel wouldn't move with the carriage).
- Guide roller pin origin far from any frame visual (isolated joint anchor).
- Adjustment knob PRISMATIC (a knob rotates, it does not translate).
- Feed range so long that the carriage exits the throat and floats in
  space at `upper` pose.
- Ratchet ring built as a separate FIXED-jointed part instead of an inline
  visual on the knob (Rule 1).
- Reamer blade parented to something other than the frame stem, or its
  motion axis not (0,1,0) (would be geometrically impossible to fold).
- Frame side plates or roller boss caps as separate FIXED-jointed parts
  (Rule 1).
- N=1 guide roller (no roller pair contradicts the "opposed rollers +
  cutter" identity).

## 与相邻类别的边界

- 不该混入：`pilers_cutting_pliers` / other pliers — plier's opposed jaws
  share a single revolute pivot; here we have PRISMATIC feed + spinning
  cutter wheel, no plier pivot.
- 不该混入：`paper_cutter_guillotine` — guillotine's blade drops on a flat
  bed; tube_cutter's cutter is a small opposed disc on a screw carriage.
- 不该混入：`Handtools_Clamp` — clamp is a single-jaw C-frame with a screw
  press, no cutter wheel, no guide rollers.
- 不该混入：`conduit_bender` — bender wraps conduit around a form; no
  cutter.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored by P3+P4 subagent; source-backed slot candidates only |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | compact_c_frame | P2 | L33-L102 (`_frame_shape`), L104-L129 (`_side_plate_shape`), L132-L159 (`_carriage_shape`) | ring C-frame helper + carriage silhouette |
| S2 | A | handheld_c_frame | P1 | L35-L167 (`_frame_shape`) | in-line C-head + hollow handle helper |
| S3 | A | blue_c_frame_top_bridge | P3 | L31-L106 (`_c_ring`, `_build_frame_body`, `_build_top_bridge`) | vertical C-frame + top bridge helper |
| S4 | B | rollers_N | P2 + V1 + V2 | P2 L272-L314 (roller loop), V1 L27-L28 (N=3 centers), V2 L27-L28 (N=4 centers) | roller_count multiplicity + roller shape |
| S5 | C | rotating_knob | P2 | L367-L419 (`adjustment_screw` + KnobGeometry) | lobed knob + screw shaft helper |
| S6 | C | t_handle | P3 | L329-L347, L386-L394 (`knob` part + `_build_t_grip`) | T-handle crossbar + knurled ends |
| S7 | C | ratchet_screw | V3 | L367-L419 base + added ratchet ring/pawl visuals | ratchet overlay on rotating_knob |
| S8 | D | fold_out_reamer | V7 | L165-L191 (`_reamer_blade_shape`), L502-L541 (part + `reamer_fold` joint) | reamer blade + REVOLUTE joint |
