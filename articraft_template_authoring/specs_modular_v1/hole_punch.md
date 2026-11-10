# hole_punch — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `hole_punch` |
| template path | `agent/templates/hole_punch.py` |
| test path (optional) | `tests/agent/test_hole_punch_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: a single grounded `body` root carries the skeleton (frame/slab + dies + pivot/guide mount hardware); exactly one actuator sub-assembly (lever / plunger / lever+carriage) parents to it (parallel), and a punch-pin/die **multiplicity axis** `n_holes` copies the pin+die station N times in a linear Y row.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 8 ids in `picture_source_maps/Workspace__Hole_punch.md` (2 origin anchors A/B + 5 forks + 1 probe) |
| source_index_policy | only adopted module sources are indexed in the slot tables below (the `probe_adjustable` probe is read but NOT realized — see §8) |

Two source families:
- **Origin A family — handheld metal punch** (`rec_chrome-plier-style-single-hole-punch-two-polishe_…850c1c69`): FIXED arm `frame` (upper handle + lower jaw + perforated `die_block`) + MOVING arm `punch_lever`, crossing at a rivet; one REVOLUTE `punch_stroke` (axis +Y) drops a single `punch_pin` into the die bore. Fork `rec_hole_punch_var_skeleton_sprung_loop` replaces the crossing rivet + rear handle with a continuous bent spring-steel C-loop bridge (front pivot, REVOLUTE `punch_stroke` axis −Y). This is the `plier_frame` / `cloop_frame` skeleton lineage.
- **Origin B family — desktop office punch** (`rec_workspace__hole_punch__002_…964`): `base` slab (rubber pad, painted shell, top platform, loop-emitted `die_ring/die_hole/die_boss_{i}`, rear hinge) + rear-hinged `pressing_lever`; REVOLUTE `lever_pivot` (axis +Y); N `punch_pin_{i}` FIXED to the lever via `lever_to_pin_{i}`. Forks: `mechanism_plunger` (REVOLUTE→PRISMATIC vertical plunger in a guide column, single hole), `skeleton_lever_carriage` (compound REVOLUTE lever camming a PRISMATIC `plunger_carriage` on guide posts, pins FIXED to carriage), `n3`/`n4` (same skeleton, hole count 3/4 via the existing pin/die loop). This is the `desktop_base` skeleton + `pivot_lever`/`plunger`/`lever_carriage` mechanism lineage and the `n_holes` multiplicity axis.

## 核心身份

A **hole punch** is a hand tool that perforates sheets of paper by driving one or more punch pins straight through the paper into matching dies, actuated by a single hand squeeze/press DOF, producing round holes and collecting the chads. Every seed keeps: one or more punch pins aligned to matching die bores; a single press/squeeze articulation (revolute or prismatic) that drives the pins into the dies; an open paper throat/slot gap at rest that closes on actuation; a chad/waste path. Default mature domain spans the handheld plier/scissor punch, the one-hand sprung C-loop punch, and the desktop base+lever office punch (single- and multi-hole, plus a vertical push-plunger and a compound lever+carriage heavy-duty variant).

Must NOT drift into (see §11): eyelet/grommet setter, stapler, pliers/wire cutter, paper trimmer/guillotine, drill/hole-saw/bench press-drill, comb/spiral binding machine.

## 槽位 + 候选模块表

### Slot A：skeleton （① 骨架 / ③ 主体形态家族 — 主多样性槽，登记进 slot_choices）
The grounded `body` root: frame/slab + loop-emitted dies + the pivot/guide mount hardware. Also carries the ③ Primary Form Family read (handheld C-frame vs desktop slab).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `desktop_base` | origin_anchor | B `rec_workspace__hole_punch__002_…964` (+ plunger fork base) | L89-L209 (`base`: rubber pad, blue shell, top platform, `die_ring/die_hole/die_boss_{i}` L168-202, rear hinge) | eligible if compatible | flat rubber-footed painted slab; raised die platform; rear hinge / guide-column / head-casting mount emitted per mechanism; **Volumetric Envelope Form** (desk slab body) |
| `plier_frame` | origin_anchor | A `rec_chrome-…850c1c69` | L166-L200 (`frame` arm + `die_block` L96-123) | eligible if compatible (handheld → pivot_lever, N=1) | compact chrome C-frame: lower jaw / die plate + rising central pivot post + rear fixed handle + knurled grip + through pivot rivet; **Planar Boundary Form** (thin crossed-arm frame) |
| `cloop_frame` | forked_anchor | `rec_hole_punch_var_skeleton_sprung_loop` | L204-L232 (`frame` + `c_loop_bridge` tube L220-232, spline L77) | eligible if compatible (handheld → pivot_lever, N=1) | compact frame with a continuous bent spring-steel C-loop bridge behind the pivot (elastic-return identity); **Macro Surface Construction** (swept tube loop replaces the rear handle) |

### Slot B：mechanism （② 关节类型 — press/squeeze 机构）
The moving punch carrier chained to the skeleton. Exactly one per seed; each provides the guaranteed non-FIXED press DOF that drives the pins into the dies.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `pivot_lever` | origin_anchor | A `punch_stroke` / B `lever_pivot` | B L281-L293 (REVOLUTE `lever_pivot` +Y L281-287; FIXED `lever_to_pin_{i}` L291-293); A L125-155 | eligible (all skeletons) | `pressing_lever` REVOLUTE about +Y at the pivot; carries N pins FIXED at `lever_to_pin_{i}` on its underside |
| `plunger` | forked_anchor | `rec_hole_punch_var_mechanism_plunger` | L249-L346 (`plunger_head` L249-264; PRISMATIC `plunger_slide` −Z L328-334; FIXED `plunger_to_pin_0` L344-346) | eligible: desktop_base, N=1 | palm-press `plunger_head` slides straight down (PRISMATIC −Z) inside a guide column; single pin FIXED to the plunger |
| `lever_carriage` | forked_anchor | `rec_hole_punch_var_skeleton_lever_carriage` | L250-L369 (REVOLUTE `lever_pivot` +Y L337-343; PRISMATIC `carriage_guide` −Z L350-356; FIXED `carriage_to_pin_{i}` L367-369) | eligible: desktop_base, N∈{2,3,4} | compound: REVOLUTE `pressing_lever` cams a PRISMATIC `plunger_carriage` on guide posts; pins FIXED to the carriage travel straight down |

Every candidate in every slot is structurally distinct (part tree / joint topology / primitive family), not a re-skin. Palette/knurl/screw-count are NOT candidates (④/⑥ audit-only, ride via `palette_theme`).

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                         body (root: frame/slab + loop dies die_*_{i} + pivot/guide mount hardware)
   pivot_lever  ──[REVOLUTE +Y @ (pivot_x, pivot_z)]──────────> pressing_lever ──[FIXED ×N @ station]──> punch_pin_{i}
   plunger      ──[PRISMATIC −Z @ (pin_x, col_top)]───────────> plunger_head   ──[FIXED @ station]─────> punch_pin_0
   lever_carriage ┬[REVOLUTE +Y @ (pivot_x, lever_pivot_z)]──> pressing_lever  (cam nose contacts carriage)
                  └[PRISMATIC −Z @ (pin_x, pivot_z)]─────────> plunger_carriage ─[FIXED ×N @ station]─> punch_pin_{i}
```

- Slot resolve order: `skeleton` → `mechanism` (gated by skeleton) → `n_holes` (gated by skeleton+mechanism) → `palette_theme` → continuous scales, all in `resolve_config`. All geometric quantities (`pin_x`, `pivot_x`, `pivot_z`, `die_top_z`, `pin_ys`, gauges, `stroke_upper`) are single-sourced in `ResolvedHolePunchConfig` so the dies (skeleton) and the pins (mechanism) read the SAME `pin_x`/`pin_ys` layout → pin↔die alignment holds by construction (Contract 3c).
- Cross-slot connection points: the mechanism parents to `body`; the press-joint origin sits on real mount hardware emitted by the skeleton (`rear_hinge_block` / `pivot_post` / `guide_column` / `head_casting`+`guide_post_{i}`). `pivot_x < pin_x`; the pin-mount plane `pivot_z = die_top_z + paper_slot + pin_hang` ties rest clearance, paper gap and pin length together.
- Every non-FIXED joint is a captured mechanical pivot / sliding fit (hinge barrel in a hinge block, plunger stem in a guide column, guide posts through carriage bores): `MatingContract` cannot express two axis-aligned faces in contact, so these are **grandfathered** (omit `mating=`) and documented via element-scoped `allow_overlap` mirroring the source `run_tests` (identical pattern to `monitor_mount`).
- Mutual exclusion / gating: handheld skeletons (`plier_frame`,`cloop_frame`) ⇒ `pivot_lever` + N=1 only; `plunger` ⇒ `desktop_base` + N=1; `lever_carriage` ⇒ `desktop_base` + N∈{2,3,4}; `pivot_lever` on `desktop_base` ⇒ full N∈{1,2,3,4}.

## 每槽位 Module Emits / Interfaces

### Slot A / skeleton
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (root). All frame/slab/die/mount detail is `body.visual(...)` — no FIXED-jointed decoration | B L89-209 / A L166-200 |
| internal joints | none | — |
| upstream interface | ground root; provides `die_top_z`/`base_top_z`, the die stack at `pin_x`/`pin_ys`, and the mechanism mount (`rear_hinge_block`/`pivot_post`/`guide_column`/`head_casting`+`guide_post_{i}`) | B L168-209 |
| downstream interface | press-joint origin on the mount hardware; die bores the pins descend into | B L281-293 |

### Slot B / mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pressing_lever` (pivot_lever/lever_carriage) or `plunger_head` (plunger); `plunger_carriage` (lever_carriage); N `punch_pin_{i}` | B L211-257 / plunger L249-298 / carriage L250-330 |
| internal joints | REVOLUTE `lever_pivot`/`punch_stroke` +Y (or −Y cloop) / PRISMATIC `plunger_slide`/`carriage_guide` −Z + FIXED `*_to_pin_{i}` | B L281-293 / plunger L328-346 / carriage L337-369 |
| upstream interface | parents to `body`; joint origin on skeleton mount hardware | B L281-287 |
| downstream interface | pins FIXED to the moving carrier at each `(pin_x, pin_ys[i])` station | B L291-293 |

不动细节（knurled grips, handle ribs, die rings, screw heads, cam nose, C-loop bridge, return-spring collar）都是宿主 part 的 `.visual(...)`，非 FIXED-jointed part（Rule 1）。唯一独立 part 是真正会动的件（lever/plunger/carriage/pins）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `skeleton` | enum | desktop_base / plier_frame / cloop_frame | desktop_base | choice | procedural sampler (weighted 0.55/0.23/0.22) | Slot A |
| `mechanism` | enum | pivot_lever / plunger / lever_carriage | pivot_lever | conditional | handheld⇒pivot_lever; desktop weighted 0.45/0.25/0.30 | Slot B |
| `n_holes` | int (mult.) | {1,2,3,4} | 2 | conditional | handheld/plunger⇒1; lever_carriage⇒{2,3,4}; desktop pivot_lever⇒{1,2,3,4} weighted | §8 |
| `palette_theme` | enum | 7 themes (§8.5 ⑥) | office_blue | conditional | handheld⇒metallic{chrome,nickel,gunmetal}; desktop⇒painted{office_blue,office_red,graphite,forest_green} | ⑥ |
| `reach_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform then clamp; scales `pin_x`,`pivot_x`,body length | ⑤ / B,A |
| `body_height_scale` | float | [0.88, 1.16] | 1.0 | independent | uniform then clamp; scales `die_top_z`,`base_top_z` | ⑤ |
| `hole_pitch_scale` | float | [0.88, 1.16] | 1.0 | independent | uniform then clamp; scales Y spacing (desktop only) | ⑤ / n3,n4 |
| `handle_len_scale` | float | [0.82, 1.25] | 1.0 | independent | uniform then clamp; handle/grip length | ⑤ |
| `pin_radius_scale` | float | [0.88, 1.18] | 1.0 | independent | uniform then clamp; pin gauge | ⑤ |
| (—) | constraint | — | — | equation | `die_hole_r=pin_body_r+0.0014`, `die_ring_r`,`die_boss_r`,`pin_cap_r`,`pin_tip_r` all derived from `pin_body_r` so the pin always fits its bore | interface |
| (—) | constraint | — | — | equation | `pivot_z=die_top_z+paper_slot(0.003)+pin_hang(0.018)`; `lever_pivot_z=pivot_z+0.035` for lever_carriage (lever clears the carriage through the stroke) | clearance |
| (—) | constraint | — | — | equation | `stroke_upper=clamp(asin(min(0.013,0.42·d)/d),0.10,0.50)`, `d=pin_x−pivot_x` (press drops the pin ~13 mm-arc into the die — derived, not tuned) | joint range |
| (—) | constraint | — | — | inequality | lever_carriage `head_casting` top `= pivot_z − slide_travel − 0.004` < carriage fully-descended underside so the carriage never bottoms into it | clearance |

所有 `equation`/`inequality`/`conditional` 在 `resolve_config` 内求解；builder 不再失败。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤8 s/seed**（实测：48-seed sweep-pipeline ≈7.5 s wall ⇒ well under 1 s/seed）。依据：几何全部为 `Box`/`Cylinder` 图元 + 一条 `tube_from_spline_points` C-loop（仅 cloop_frame，`samples_per_segment=12`,`radial_segments=12`）；N 个相同 pin 复用 `_build_pin` helper、N 个相同 die 复用 `_add_dies` 循环。分档 tessellation：小半径特征（pins/dies/rivets/posts）≤16 段；无重布尔雕刻。sweep `--compile-timeout` 作看门狗。

## Multiplicity / Copy Logic

- **Axis `n_holes` (punch-pin + matching-die pairs).**
  - `count_param` = `n_holes`; product `N_range` = [1,4] (real office standards 1/2/3/4-hole; not beyond 4 for hand punches). Sampling domain (weighted, small-N frequent): desktop `pivot_lever` {1:0.3,2:0.4,3:0.2,4:0.1}; `lever_carriage` {2:0.5,3:0.3,4:0.2}; handheld & `plunger` pinned to 1.
  - copied object: `punch_pin_{i}` (pin body + top cap + cutting tip, `_build_pin`) FIXED to the carrier via `lever_to_pin_{i}` / `carriage_to_pin_{i}`, plus the matching `die_boss_{i}`/`die_ring_{i}`/`die_hole_{i}` stack in the body (`_add_dies`).
  - naming: stable indexed `punch_pin_{i}` / `die_*_{i}`; placement: linear Y row `pin_ys[i]=(i−(N−1)/2)·hole_pitch`; base/lever widen along Y with N.
  - joint policy: one FIXED `*_to_pin_{i}` per pin under a single shared press DOF; multiplicity changes only count/spacing, never skeleton/mechanism.
  - source/gating: N=1 (A), N=2 (B), N=3 (`n3` L244-280), N=4 (`n4` L31,L270-310); gated to desktop skeletons per §5.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | 3 skeletons (desktop slab / plier C-frame / sprung C-loop) → distinct grounded part-and-mount graphs; mechanism adds `pressing_lever` / `plunger_head` / `pressing_lever`+`plunger_carriage`. source-backed: B, A, sprung_loop, mechanism_plunger, lever_carriage. |
| └ multiplicity | 同构件 ×N | 有 | `n_holes`∈{1,2,3,4}, weighted small-N; copied pin+die station; sources A(1)/B(2)/n3(3)/n4(4). See §8. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE +Y (`lever_pivot`, B) / −Y (`punch_stroke`, cloop) press pivot; PRISMATIC −Z (`plunger_slide`); compound REVOLUTE+PRISMATIC (`lever_carriage`). All source-backed; each realized in sweep (slot_value_counts: pivot_lever 25 / plunger 14 / lever_carriage 9 over 48 corner seeds). |
| ③ 主体形态家族 | 换核心几何原型 | 有（由 ① skeleton 承载，登记进 slot_choices） | 3 recognizable prototypes registered in `slot_choices` via the skeleton slot: `desktop_base` (Volumetric Envelope — desk slab), `plier_frame` (Planar Boundary — thin crossed-arm frame), `cloop_frame` (Macro Surface Construction — swept spring-steel loop). Mechanism-dominated tool 小类：no independent ③ vocabulary exists beyond the skeleton forms + ④/⑤ deltas, so ③ is source-backed via ① (no separate world-knowledge fork), per source-map §8.5. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only) | knurled grips, handle rib, die rings/bosses, side screws, pivot rivet, cam nose, C-loop bridge, plunger cap rim, return-spring collar — all host-conformal `body.visual(...)` derived from the frame/slab surface (derive order ③→⑤→④). Rides `palette_theme`. Not standalone candidates. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | reach [0.85,1.20], body_height [0.88,1.16], hole_pitch [0.88,1.16], handle_len [0.82,1.25], pin_radius [0.88,1.18] (all clamped in `resolve_config`). **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): revolute press `lever_pivot`/`punch_stroke` +Y or −Y [0, `stroke_upper`≈0.10–0.50 rad] (drops pins into dies); prismatic `plunger_slide`/`carriage_guide` −Z [0, `slide_travel`=0.012 m]. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` + targeted `ctx.pose(press_joints→upper)` proving each pin tip descends below the die top and below its rest z. No sampled-pose exemption. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes: polished metal (handheld) + painted metal (desktop) + black rubber pad/grip + steel dies/pins/spring. 7 themes ≥6: chrome/nickel/gunmetal (metallic, handheld) + office_blue/office_red/graphite/forest_green (painted, desktop). Material-class coverage ≥ ceil(0.5×7)=4 (metal + painted + rubber + steel present every seed). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——3 个 skeleton 拉得开、metallic/painted 涂装都出现、grips/screws/rivet 贴合宿主面不悬空、press 关节全程把 pin 压进 die 且不穿模。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- handheld: 2 skeletons × pivot_lever × N=1 = 2
- desktop: 1 skeleton × [pivot_lever×N{1,2,3,4}=4 + plunger×N{1}=1 + lever_carriage×N{2,3,4}=3] = 8
- ⇒ **10 distinct (skeleton,mechanism,N) tuples** × 7 palette_theme (gated 3 handheld / 4 desktop) × 5 continuous scales ⇒ topology target easily >300 over 1000 seeds (report-only). Honest structural space is small (a single-DOF squeeze/press tool); continuous scales do NOT carry primary diversity.

理由：多样性主要来自离散 skeleton(①/③) + mechanism(②) + n_holes(mult) 槽；连续 scale 仅 clamp/derive。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；先 `skeleton`（weighted）→ 若 handheld 则 mechanism=pivot_lever,N=1,metallic palette；否则 mechanism（weighted）→ N（mechanism-gated weighted）→ painted palette；再采 5 个连续 scale。Compatibility gating = handheld⇒pivot_lever/N1、plunger⇒N1、lever_carriage⇒N≥2，defensively re-clamped in `resolve_config`. No regression overrides (procedural covers seed 0).
Topology target：≥300 over 1000-seed slot tuples (report-only, not a gate); the real combinatorial space is 10 discrete tuples × palette (§budget), bounded by the tool's single-DOF vocabulary.
Controlled local parameterization：reach_scale, body_height_scale, hole_pitch_scale, handle_len_scale, pin_radius_scale — all clamped in `resolve_config`; die bore + gauge derive from `pin_body_r`, `pivot_z`/`stroke_upper`/`head_casting` derive from the die plane so they never break pin↔die alignment, throat clearance, or the carriage/head-casting travel inequality.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | skeleton→(mechanism,N,palette gated)→scales | slot_choices_for_seed matches build choices (slot_choice_errors=0) |
| compatibility matrix | handheld⇒pivot_lever/N1; plunger⇒desktop/N1; lever_carriage⇒desktop/N≥2; re-clamped in resolve_config | no floating, collision, axis, closed-pose, alignment failures |
| controlled local variation | 5 continuous scales, clamped | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner 36-47), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| skeleton | 3 | yes | yes | ①/③ primary form slot |
| mechanism | 3 | yes | yes | ② (skeleton-gated) |
| n_holes (mult) | N∈{1,2,3,4} | yes | yes | sources A/B/n3/n4 |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (skeleton, mechanism, n_holes, palette_theme)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility gating (handheld⇒pivot_lever/N1, plunger⇒desktop/N1, lever_carriage⇒desktop/N≥2) prevents illegal combos, re-clamped in `resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped in `resolve_config`; die bore + gauge derive from pin radius; pivot_z / stroke_upper / head_casting derive from the die plane
- every non-FIXED joint is a captured pivot/slide with element-scoped `allow_overlap` + `expect_overlap`; no MatingContract phantom anchors; no FIXED-jointed decoration parts
- key joints have expected type/axis/range (REVOLUTE ±Y press; PRISMATIC −Z plunger/carriage; FIXED pin mounts)
- copied objects follow `punch_pin_{i}` / `die_*_{i}` naming + linear-Y placement; dies (body) and pins (carrier) share one `pin_ys` layout
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` proving each pin descends into its die

## Reject cases
- A die stack or guide column that floats above the body with no support path (disconnected island) — the plunger guide column MUST be carried by the rear C-throat frame; the carriage MUST ride captured guide posts.
- Pin misaligned to its die bore (dies and pins reading different `pin_x`/`pin_ys`) → expect_overlap fail.
- Press stroke that does NOT drive the pin tip below the die top / below its rest z (dead joint).
- lever_carriage where the carriage bottoms into `head_casting` at full descent, or the raised lever plate dips onto the carriage through the stroke.
- Handheld frame emitting a rear moving handle that clashes the fixed frame at the pivot, or rivet caps that don't touch the frame (island).
- Rotating-lever + added holes on a `plunger` (must stay single-hole prismatic), or a screw-press/helical drive (not a single URDF joint).
- Monochrome output (palette_theme not driving `.visual(material=...)`), or handheld rendered in painted-desktop palette.

## 与相邻类别的边界
- 不该混入：eyelet/grommet setter（sets rings, no chad-cutting die bore）。
- 不该混入：stapler（drives staples, no die perforation）。
- 不该混入：pliers / wire cutter（cutting jaws, no die bore / paper throat）。
- 不该混入：paper trimmer / guillotine（straight shear blade, not round-hole dies）。
- 不该混入：drill / hole-saw / bench press-drill（rotary/helical drive, not a single squeeze/press URDF joint）。
- 不该混入：comb / spiral binding machine（gang of rectangular slots + binding mechanism）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Origin-A handheld frame lineage (plier + sprung C-loop) + origin-B desktop slab lineage (pivot_lever / plunger / lever_carriage + n_holes mult). `probe_adjustable` (sliding heads on a Y rail) read but NOT realized — the per-head Y prismatic adjustment adds a second sliding DOF whose collision-through-range against neighbors/lever was not worth the risk for the honest small vocabulary; deferred as a probe, not counted. ③ carried by ① skeleton (mechanism-dominated tool, no independent form vocabulary). |

## 模板实现备注（可选）
- Shared helpers: `_add_dies` (loop-emitted die stack, source B L168-202), `_build_pin` (pin body+cap+tip, source A/carriage), `_emit_handle` (handheld handle+grip), `_add_mount` (per-mechanism pivot/guide hardware), `_build_handheld_frame` (plier/cloop shared).
- Captured element-scoped `allow_overlap`: hinge barrel↔mount (`rear_hinge_block`/`pivot_post`); `pivot_rivet`↔`hinge_barrel` (plier); pin stack↔die stack; plunger assembly↔guide column/bore/flange; carriage↔`guide_post_{i}` + cam_nose↔carriage + head_casting↔pins.
- Single-sourced geometry in `ResolvedHolePunchConfig` (Contract 3c): `pin_x`,`pivot_x`,`pivot_z`,`lever_pivot_z`,`die_top_z`,`pin_ys`,`stroke_upper`,`slide_travel`,gauges — read identically by skeleton (dies) and mechanism (pins).
- `probe_adjustable` deferred (not in seed domain); see reviewer notes.
