# Modular Spec — Astronomy / Astronaut helmet

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Astronaut_helmet` |
| template path | `agent/templates/Astronomy_Astronaut_helmet.py` |
| test path (optional) | `tests/agent/test_Astronomy_Astronaut_helmet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root shell + parallel-children visor + parallel-children neck_base + 2 multiplicity axes) |
| function stem | `astronomy_astronaut_helmet` (exports `build_astronomy_astronaut_helmet`, `config_from_seed`, `run_astronomy_astronaut_helmet_tests`) |

`pattern = mixed`: a single root `shell` part (the helmet dome) carries two
parallel-children slots — a movable **visor** (flip / slide / dual, parented to
the shell) and a **neck_base** (collar fused into the shell, or a separate
bayonet locking ring on a rotary joint). Each child manually parents its own
articulations to the shell (no serial chain joint). Two multiplicity axes ride
on top: `collar_rib_count` (rib notches around the neck ring) and
`eva_port_count` (ribbed EVA connector ports around the lower shell).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 9 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_costume-style-nasa-astronaut-helmet-glossy-white_...2b95133f` — ORIGIN 母本 (hollow SPHERE shell, small circular face opening, stepped ribbed neck collar (14 ribs) fused into shell, rear ribbed hose fitting, black interior chin lip, red NASA worm-logo + US flag decals, flip-up amber bubble VISOR on a REVOLUTE side pivot).
- `rec_astronaut_helmet_var_collar_ribs` — ④ decoration multiplicity: collar `n_notches` 14→24.
- `rec_astronaut_helmet_var_cyl_shell` — ③ Primary Form Family: sphere shell → cylindrical barrel + hemisphere dome (diving-bell). Volumetric Envelope Form.
- `rec_astronaut_helmet_var_dual_visor` — ① skeleton: adds a second independent inner clear visor part on its own REVOLUTE pivot (concentric nested LEVA pair).
- `rec_astronaut_helmet_var_full_bubble` — ③ aperture form: small circular opening (R=0.092) → large fishbowl opening (R=0.136) + full hemispherical dome visor.
- `rec_astronaut_helmet_var_neck_ports` — ④ decoration multiplicity: single rear hose fitting → N (=3) evenly spaced ribbed EVA connector port stubs around the lower shell.
- `rec_astronaut_helmet_var_rect_window` — ③ aperture form (Planar Boundary): circular opening → wide rectangular wraparound window + curved rectangular polycarbonate pane + rectangular bezel.
- `rec_astronaut_helmet_var_slide_visor` — ② joint type: visor pivot REVOLUTE → PRISMATIC (drops straight down the front / retracts up along +Z, riding in two vertical guide rails on the shell).
- `rec_astronaut_helmet_var_twist_lock_ring` — ① skeleton + ② joint: neck collar becomes a separate `locking_ring` part on a REVOLUTE (axis Z) quarter-turn bayonet joint.

## 核心身份

A **wearable astronaut / spacesuit helmet** (costume / EVA / pressure-suit
style): a hollow white **shell dome** (spherical, cylindrical-barrel "diving
bell", or big-opening "fishbowl") with a front face **aperture** (small circular
port, large hemispherical opening, or wide rectangular wraparound window),
carrying a movable transparent **visor** (amber sun-visor bubble / clear
pressure visor) that flips up on a side hinge, slides up in guide rails, or
nests as a dual inner+outer pair; a stepped **neck ring** at the base (with rib
notches, fused into the shell or a rotating bayonet lock ring), a black interior
chin lip, ribbed EVA hose/connector ports around the lower shell, and applied
NASA-style logo + flag decals. Neck ring always rests on the ground plane; at
least one real non-fixed joint (visor hinge/slide or bayonet lock) is always
present. Default mature domain: a ~0.30 m head-scale helmet with one visor and a
neck ring.

Not to be confused with the neighbouring subclass **Astronomy / Pressurised
module door** (a structural round EVA hatch set INTO a wall/bulkhead, whose main
body is the door leaf + frame, not a wearable head-scale dome) — the helmet is a
free-standing head-worn shell that rests on its neck ring, whose visor is a
secondary transparent flap, not the whole object.

## 槽位 + 候选模块表

### Slot A：shell (root · ③ Primary Form Family + face aperture)

The root helmet body. Same part tree across candidates (one `shell` part: shell
body mesh + interior lip + decals + EVA ports, all fused as shell visuals per
Rule 1). Only the body ENVELOPE prototype and the face APERTURE prototype
change; every candidate exposes the identical mounting semantics (a sphere
center at `CENTER_Z`, a face aperture the visor covers, a neck cut plane at
`NECK_CUT_Z` the collar mounts under) so the visor / neck_base slots are
form-independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `sphere_dome` | forked_anchor (origin) | `rec_costume-...2b95133f` | L78-L116, L119-L132 | eligible | hollow SPHERE shell, small circular face opening (`_x_cylinder` cut, R=0.092). **Volumetric Envelope Form** |
| `cyl_barrel` | forked_anchor | `rec_astronaut_helmet_var_cyl_shell` | L80-L143 | eligible | vertical CYLINDER wall + hemisphere dome top (diving-bell), circular opening cut through the wall; shoulder plate to the collar. **Volumetric Envelope Form** |
| `fishbowl` | forked_anchor | `rec_astronaut_helmet_var_full_bubble` | L29-L31, L120-L145 | eligible | sphere shell with a LARGE hemispherical face opening (R=0.136) revealing the interior; Mercury-style. **Volumetric Envelope Form** (large aperture) |
| `rect_window` | forked_anchor | `rec_astronaut_helmet_var_rect_window` | L40-L44, L92-L102 | eligible | sphere shell with a wide RECTANGULAR wraparound face window (`_box` cut, 0.200×0.150). **Planar Boundary Form** (aperture boundary) |

### Slot B：visor (parallel child on shell aperture · ① skeleton + ② joint)

The movable transparent flap. Carried on the shell aperture, parented directly
to the shell (no chain joint). The visor aperture SHAPE (bubble / dome / rect
pane) is DERIVED from the shell aperture (Contract 3c) so mechanism is
orthogonal to form. Hinge/slide barrels seat on the shell → grandfathered raw
joint (no MatingContract, captured-hinge Rule 2 exception) + element-scoped
`allow_overlap`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flip_visor` | forked_anchor (origin) | `rec_costume-...2b95133f` | L135-L164, L273-L303 | eligible | 1 `visor` part: bezel frame + curved arms + 2 round pivot disks + transparent bubble/dome/rect-pane + 2 gray pivot knobs; `visor_pivot` **REVOLUTE** axis (0,-1,0), `[0, flip_range]`. Works with every aperture. |
| ~~`slide_visor`~~ | forked_anchor | `rec_astronaut_helmet_var_slide_visor` | L41-L58, L132-L142, L161-L190, L317-L327 | **reviewed, NOT adopted** | PRISMATIC(Z) sliding sunshade on external shell guide rails. Withdrawn on category semantics: a helmet visor opens by ROTATION; an external vertical slide rail is not how this category reads. Source stays in the review table (审阅记录保留), no downstream candidate. Cost: the ② joint-type axis loses PRISMATIC — recorded, not hidden. |
| `dual_flip_visor` | forked_anchor | `rec_astronaut_helmet_var_dual_visor` | L39-L44, L173-L206, L346-L371 | eligible (every envelope + aperture; inner lens/frame follow both) | 2 independent parts: outer amber `visor` (flip) + inner clear `inner_visor` (`inner_visor_frame` + `inner_visor_lens`) on `inner_visor_pivot` **REVOLUTE** axis (0,-1,0); concentric LEVA nesting. |

### Slot C：neck_base (parallel child at shell base · ① skeleton + ② joint + multiplicity `collar_rib_count`)

The stepped neck ring at the bottom. Two structurally distinct realizations
(pool yields exactly 2; degrade-to-2 justified below).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fused_collar` | forked_anchor (origin) | `rec_costume-...2b95133f` | L90-L105 | eligible | stepped 2-tier collar (upper 0.112 + wider bottom 0.118, hollow bore) with N rib notches, emitted as a STATIC `shell` visual (no new part, no joint); Rule 1. |
| `twist_lock_ring` | forked_anchor | `rec_astronaut_helmet_var_twist_lock_ring` | L104-L126, L313-L339 | eligible | the same stepped collar becomes a separate `locking_ring` PART on `shell_to_ring` **REVOLUTE** axis (0,0,1), `[0, bayonet_range]` (quarter-turn bayonet lock). |

硬约束满足：Slot A=4 candidates、Slot B=3 candidates（均结构不同 + forked_anchor
+ `model.py:Lx-Ly`）。Slot C=2 candidates（**degrade-to-2 justified**：5 星池里
颈环只有两种结构实现——融进壳体的静态领圈 vs. 独立可转的卡口锁环；没有第三种颈部
骨架样本，按 SPEC_TEMPLATE §4 硬约束"样本池不足时可降到 2 并说明理由"处理，不用
世界知识杜撰第三个未被样本支撑的 skeleton/joint candidate）。无
`world_knowledge_extrapolation` candidate。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel children + multiplicity)

```
shell (root; sphere_dome / cyl_barrel / fishbowl / rect_window)
   ├─[front aperture · visor_pivot REVOLUTE(0,-1,0) | visor_slide PRISMATIC(0,0,1); captured hinge/slider seat]→ visor  (×1 or ×2 nested)
   └─[base neck cut plane · fused (static shell visual) | shell_to_ring REVOLUTE(0,0,1); bayonet seat]→ neck_base
```

- **slot 顺序 / parent**：`shell` 是 root，唯一被复用的 parent。`visor` 与
  `neck_base` 都把各自 joint 的 `parent=shell`，互不串联（parallel children）。
  两者均只声明 `downstream`（re-export shell），不声明 `upstream`，所以 assembler
  不发射自动 chain joint（各模块发原始 joint，与 5 星源一致）。
- **接口点位**：visor → 绕球心 `(0,0,CENTER_Z*s)` 的侧向铰链（REVOLUTE 轴 Y）或
  沿 +Z 的滑轨（PRISMATIC 轴 Z）；铰链圆盘/滑块坐落在壳体外表面。neck_base →
  底部颈切面 `z=NECK_CUT_Z`（融进壳体）或卡口界面 `(0,0,BAYONET_Z*s)`（REVOLUTE 轴 Z）。
- **跨 slot joint type/axis/range**：visor_pivot REVOLUTE(Y, `[0,flip_range≤1.4]`) /
  visor_slide PRISMATIC(Z, `[0,slide_travel≤0.09]`) / inner_visor_pivot REVOLUTE(Y);
  shell_to_ring REVOLUTE(Z, `[0,bayonet_range≈π/2]`)。
- **互斥/派生**：**无 compatibility gate**。shell 形态与 visor 机构、neck_base 完全
  正交，4×3×2 全部组合可构建。原先把 `slide_visor` 限制在 circular-small、把
  `dual_flip_visor` 限制在 circular 的运行时回退已移除，改为局部参数派生
  （AUTHORING §4 / MECHANICAL_PRIORS §3）：
  - **visor 铰链按壳体的回转轴派生**（`visor_hinge`）。REVOLUTE 只有在宿主是
    *绕该轴* 的回转面时才可能保持贴合：sphere/fishbowl/rect_window 都是球，
    源母本的中心枢轴（轴 Y 过球心）全程同心，实测固实相交在整个行程恒定。
    `cyl_barrel` 是绕 **Z** 的回转面，且顶盖球心偏移 +`DOME_START_Z`，中心枢轴
    会把 visor 直接推进壁里（实测 10° 处埋掉 visor 体积的 13.8%，而球壳恒为 3.5%），
    且任何余量都救不了。故圆柱壳改用 **BROW HINGE**：轴移到 bezel 上沿、落在壳体
    表面（`hinge_x` 取铰耳中位 y 处的表面 X，取 y=0 会让铰耳悬空 10 mm），visor
    像真实翻盖头盔那样向前上方掀离壳体。铰耳为绕轴的圆柱，旋转下不变，因此全程
    保持嵌入壳体、提供 `fail_if_isolated_parts` 所需接触。
    注意：visor 几何按**壳体局部坐标**编写，而 URDF child link 的坐标系是关节原点；
    非中心铰必须用 `_visor_child_offset` 把 visual 平移回去，否则整个 visor 位移。
  - `dual_flip_visor`：内层清透镜片与内框走与外层气泡/bezel **相同的 envelope 分支
    （球带 / 圆柱带）和 aperture 分支（圆冠 / 矩形板）**。rect 开口得到嵌套矩形镜片
    （内缩 10 mm，对应圆形情形的 8 mm）；cyl_barrel 得到圆柱带 —— 球冠扣在圆柱壁上
    水平半径 `sqrt(r²-z²)` 随 |z| 收缩，z=0.08 处陷进壁内 22.5 mm，而 concentric-cap
    的 `allow_overlap` 会把它整个盖住（spec 自列 reject case）。

## 每槽位 Module Emits / Interfaces

### Slot A / module sphere_dome | cyl_barrel | fishbowl | rect_window
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shell` (single root part) | origin L203 |
| visuals | `shell_body` (cadquery mesh; sphere/cyl+dome/fishbowl/rect) + `interior_lip` + `nasa_logo_letter_{0..3}` + `flag_decal_{base,canton,stripe_0..2}` + `port_{0..N-1}` (EVA ports) | origin L204-L271, L107-L114; neck_ports L282-L301 |
| internal joints | none (root, static body) | — |
| downstream interface | `shell` part, `shell_body` visual, face `positive_z`, informational (children wire manually) | — |

### Slot B / module flip_visor | slide_visor | dual_flip_visor
| emits | 描述 | 来源 |
|---|---|---|
| parts | `visor` (+ `inner_visor` for dual) | origin L276; dual L349 |
| visuals | `visor_frame` + `visor_bubble` + `pivot_knob_{0,1}` (flip/dual outer); `+ slider blocks` fused in frame + `guide_rail_{pos,neg}` added to shell (slide); `inner_visor_frame` + `inner_visor_lens` (dual inner) | origin L277-L292; slide L161-L190, L132-L142; dual L173-L206, L353-L360 |
| internal joints | `visor_pivot` REVOLUTE(Y) / `visor_slide` PRISMATIC(Z); dual adds `inner_visor_pivot` REVOLUTE(Y) | origin L294-L303; slide L317-L327; dual L363-L371 |
| upstream interface | **none declared** (parallel-children; parents joints directly to `shell`) | — |
| downstream interface | re-export shell downstream (passthrough) | — |

### Slot C / module fused_collar | twist_lock_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (fused_collar → static shell visual) / `locking_ring` (twist) | origin L90-L105; twist L104-L126, L313 |
| visuals | `neck_collar` shell visual (fused) / `locking_ring_body` (twist) | origin L90-L105; twist L318 |
| internal joints | none (fused) / `shell_to_ring` REVOLUTE(Z) | twist L325-L339 |
| upstream interface | **none declared** (parallel-children) | — |
| downstream interface | re-export shell downstream (passthrough) | — |

活动件语义：visor_pivot 翻起遮阳镜；visor_slide 上滑收起遮阳镜；inner_visor_pivot
独立翻起内层压力镜；shell_to_ring 卡口锁环绕 Z 四分之一转。不动细节（tiles/collar/
ports/rails/decals/lip/knobs）写成宿主 part visual（Rule 1）。captured hinge/slider/
bayonet seat 用 element-scoped `allow_overlap`（Rule 2 例外），铰链原点落在球体对称
中心线 + 铰链圆盘硬件（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `shell_form` | enum | sphere_dome / cyl_barrel / fishbowl / rect_window | sphere_dome | choice | procedural sampler | Slot A |
| `visor_module` | enum | flip_visor / slide_visor / dual_flip_visor | flip_visor | choice | procedural sampler | Slot B |
| `neck_module` | enum | fused_collar / twist_lock_ring | fused_collar | choice | procedural sampler | Slot C |
| `collar_rib_count` | int | {12,14,18,24,30} (obs: 14 origin, 24 collar_ribs; rest by host capacity — notch pitch at r=0.114 stays above the 16 mm notch width to 30) | 14 | independent | weighted sample, clamp | origin L97, collar_ribs L97 |
| `eva_port_count` | int | {1,2,3,4,5,6} (obs: 1 rear hose origin, 3 neck_ports; rest by host capacity — stub pitch >= 52 mm once `port_arc` widens) | 1 | independent | weighted sample, clamp | origin L109-L114, neck_ports L40,L282 |
| `shell_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform, clamp; scales the whole shell/visor/collar uniformly about the sphere center; `CENTER_Z=0.160·shell_scale` keeps the neck ring on z=0 | origin L26-L37 |
| `flip_range` | float | [1.15, 1.35] | 1.31 | conditional | REVOLUTE flip upper (rad); only flip/dual visors | origin L302 |
| `slide_travel` | float | [0.06, 0.09] | 0.08 | conditional | PRISMATIC slide upper (m); only slide_visor | slide L58 |
| `bayonet_range` | float | [1.35, 1.60] | 1.5708 | conditional | REVOLUTE bayonet upper (rad); only twist_lock_ring | twist L336 |
| `rail_y` / `slider_x` / `rail_z_lo` / `rail_z_hi` | float | derived | — | derived | rail sits outboard of the REALIZED aperture (`opening_r + 13 mm`, or `win_half_w + 30 mm`); slider seats on the rail outer surface | slide L43 ("well outside the bubble radius") |
| `slide_arm_z_lo` | float | derived | — | derived | a spherical band translated +Z moves radially OUT (`r'^2 = r^2 + 2zq + q^2`), so the sliding arm's lower edge is solved from `slide_travel` to keep shell contact at full travel; cylinder walls keep their radius and keep the origin profile | MECHANICAL_PRIORS §7 |
| `port_arc` | float | derived | — | derived | rear arc widens with N: pitch floor `52 mm`, plus origin-honesty — a bunched rear bank pulls the shell centerline off the bayonet Z axis | neck_ports L40 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: ≤ 40 s** (hang-guard `--compile-timeout 120`).
Geometry is CadQuery boolean-heavy (`mesh_from_cadquery`, matching the 5-star
sources, Rule 3 — no downgrade to primitive Box/Cylinder placeholders). The
heaviest op is the collar rib-notch loop (`collar_rib_count` ≤ 24 sequential
`.cut()`); the shell hollow + opening cut + interior lip + visor frame/bubble
intersects are a fixed handful of booleans. One EVA-port stub mesh + one visor
bubble/frame mesh are each built ONCE and re-emitted as placed visuals (ports
via `Origin`), so `eva_port_count` does not multiply CadQuery cost. `shell_scale`
applies one uniform `transformGeometry` per emitted mesh (skipped when
`scale≈1.0`). Expect 10-30 s/seed; if over, cap `collar_rib_count` first.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 — `collar_rib_count`（颈环肋齿数）
- `count_param`: `collar_rib_count`; `N_range` product `[12,30]`, test `{12,14,18,24,30}`;
  sampling domain 加权：`{12: .12, 14: .3, 18: .16, 24: .22, 30: .2}`（origin 14 偏多）。
  上界由宿主容量定：notch 节距 `2π·0.114/N` 在 N=30 时为 23.9 mm > 16 mm 槽宽。
- copied object: rib notch = a `_box(0.016,0.016,0.030,...)` **cut** subtracted
  from the collar shape at even azimuth `ang = 2π·i/N`. naming: n/a (booleans on
  the collar mesh, not separate visuals). placement: even around the upper collar
  rim. joint policy: none (decoration).
- source/gating: origin (N=14) L97-L104, collar_ribs (N=24) L96-L104. Applies to
  whichever module builds the collar (`fused_collar` shell visual OR
  `twist_lock_ring` part).
- 数量变化不改颈环形态/机制（仍是同一 2-tier collar）。这是 ④ 表面装饰数量。

### 轴 2 — `eva_port_count`（EVA 连接口数）
- `count_param`: `eva_port_count`; `N_range` `[1,6]`, test `{1,2,3,4,5,6}`; sampling
  domain 加权：`{1: .3, 2: .16, 3: .18, 4: .12, 5: .12, 6: .12}`（origin 1 偏多）。
  上界由两条派生约束定：stub 节距 >= 52 mm，且后方端口组不得把壳体对称中心线
  拉离 bayonet REVOLUTE(Z) 轴超过 15 mm —— 二者共同决定 `port_arc`（见下）。
- copied object: ribbed connector stub `port_{i}` (one shared `_port_stub_shape`
  mesh, re-emitted as N placed `shell` visuals). naming: `port_{i}`. placement:
  N even azimuths centred on the rear (`az = π + port_arc·(i/(N-1) - 0.5)`) at
  `PORT_LOCAL_Z`, radially on the realized shell surface (sphere radius or cyl
  radius). `port_arc` is DERIVED from N: `min(2.6, max(1.6, 52mm·(N-1)/r_at,
  1.6·(N-1)/3))` — the pitch term keeps stubs apart, the balance term keeps the
  bank from tilting the bayonet centerline (worst case: the least axisymmetric
  `cyl_barrel`; measured 15.5 mm > 15 mm floor at N=6 before widening). N <= 4
  reproduces the source arc 1.6 rad exactly. joint policy: none (fused shell
  visuals, Rule 1 decoration).
- source/gating: origin (N=1 rear hose fitting) L109-L114, neck_ports (N=3) L40,
  L282-L301. Independent of shell form (surface radius derived per envelope).
- 这是 ④ 表面装饰数量，不新增会动 part。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构骨架 candidate：single flip `visor`（origin, forked_anchor）／dual nested `visor`+`inner_visor`（dual_visor, forked_anchor，+1 会动 part +1 REVOLUTE）；neck：fused collar（无独立 part）／独立可转 `locking_ring`（twist_lock_ring, forked_anchor，+1 part +1 REVOLUTE）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：collar_rib_count {12,14,18,24,30}（origin/collar_ribs + 宿主容量外推），eva_port_count {1,2,3,4,5,6}（origin/neck_ports + 派生 `port_arc`）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有（**已弱化**） | 另有**铰链拓扑**差异：球壳系为过球心的同心枢轴（侧铰圆盘+旋钮），`cyl_barrel` 为 bezel 上沿的翻盖眉线铰（铰耳+短带），两者外观与运动语义均不同。visor drive REVOLUTE **轴 Y**（flip / dual 内外两根独立铰）↔ neck REVOLUTE **轴 Z** bayonet（twist_lock_ring）：两根正交轴，但**只有 REVOLUTE 一种 joint type**。PRISMATIC 随 `slide_visor` 一并撤下（类别语义：头盔面罩靠转动开启）。这是本模板多样性上的已知缺口，report-only，不用 ④/⑤/⑥ 补数。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 的 Slot A**：sphere_dome（origin, Volumetric Envelope）/ cyl_barrel（cyl_shell, Volumetric Envelope, 圆柱+穹顶）/ fishbowl（full_bubble, Volumetric Envelope, 大口径）/ rect_window（rect_window, **Planar Boundary Form**, 矩形开口边界)。form_subtype 已标。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `neck_collar` 肋齿（collar_rib_count）、`port_{i}` EVA 口（eva_port_count）、`nasa_logo_letter_{i}` 红标、`flag_decal_*` 美国旗、`interior_lip` 黑唇 — 均为宿主 part visual；decals 由壳体表面逐-点派生（sphere tangent / cyl wall），随 ③ 形态 + ⑤ 缩放共形贴附。source_type=record_only（origin/collar_ribs/neck_ports）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：shell_scale[0.90,1.12]（整体保形，颈环落地不变）。关节运动包络（每个非-continuous joint）：visor_pivot REVOLUTE axis Y，翻起方向 +Z，[闭合 0, 可行 flip_range≤1.35]；visor_slide PRISMATIC axis +Z，[0, slide_travel≤0.09] m；inner_visor_pivot REVOLUTE Y [0,~1.22]；shell_to_ring REVOLUTE axis Z（纯转，位置不变）[0, bayonet_range≈π/2]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`；targeted `ctx.pose` — flip/dual 翻起 bubble 抬升(+Z)、slide 上滑 bubble 抬升、bayonet 绕 Z 转角(位置 z 不变、方位角变)。薄透明镜盖贴着壳体外表面 riding，声明 element-scoped allow_overlap（concentric surface-riding cap，非遮真穿模）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted(白/橙壳) + metal(银/金/黑金属) + glass(透明 visor amber/clear，alpha<0.9)；配色 ≥6 colorway：`nasa_white`、`mercury_silver`、`eva_orange`、`soviet_white`、`matte_black`、`lunar_gold`。材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：0–9 seed 渲染须肉眼见到 sphere/cyl/fishbowl/rect 四种壳体、flip/slide/
dual 三种镜机构、fused/twist 两种颈环、材质配色多样、visor 全程贴壳不深穿。

## 采样与覆盖审计

**声明域 == 可达域**（无 compatibility gate，所有声明组合均可构建）：

| 口径 | 计算 | 值 |
|---|---|---|
| core（结构槽位笛卡尔积） | shell 4 × visor 2 × neck 2 | **16** |
| raw（core × N multiplicity） | 16 × collar_rib 5 × eva_port 6 | **480** |
| 可见外观（不计入 core/raw） | raw × palette 6 | 2880 |

实测校验：8 个 (shell, visor) 配对全部可达；`resolve_config` 不改写任何槽位选择
（gate 已移除）。16 个 core 组合在最坏角点（`shell_scale∈{0.90,1.05}`、`ribs=30`、
`ports=6`）全部构建并通过作者测试。**不屏蔽任何 allowance** 重测真实相交体积：
4 个 flip 组合为 0；4 个 dual 组合只剩设计内的 `inner_visor_frame` 嵌入
（cyl 6.9e-5 m³ ≈ sphere 基准 3.7e-5 m³ 同量级），`inner_visor_lens` 已不再相交。

域的两次变动，都记在账上：
- 移除 compatibility gate（rect×slide / rect×dual / fishbowl×slide 由派生实现）
  → shell×visor 配对 9 → 12；
- 按类别语义撤下 `slide_visor`（见 Slot B）→ 配对 12 → 8。
净结果 core 18 → 16、raw 216 → 480（增量全部来自 N 上界外推与 gate 移除）。
声明值与可达值在两次变动后都保持一致。

N 上下界由机构 index-general 与宿主容量决定，不由源池出现过的整数限制
（AUTHORING §3）：collar_rib 到 30（肋齿节距 > 16 mm 槽宽），eva_port 到 6
（端口节距 > 52 mm，弧宽随 N 派生）。N 只计入 raw，不计入 core。

不硬凑组合空间（质量红线：不反推上游变体数量）。真实结构词汇仍收敛于同一
「壳体 + 前部可动 visor + 颈环」cell —— 24 个 core 组合来自 4 种壳体原型 × 3 种
镜机构 × 2 种颈环，没有为凑数新增无源候选。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用
`random.Random(seed)` 依次抽 shell_form、visor_module、neck_module，再抽
collar_rib_count / eva_port_count / palette / 连续 scale。`resolve_config` 只做范围
clamp 与派生（`face_zc` / `port_arc`），不改写任何槽位选择。seed 0 pinned 到 origin 母本组合
（sphere_dome + flip_visor + fused_collar, 14 ribs, 1 port, nasa_white）作为
documented regression anchor（sparse override，其余 seed 全 procedural）。random
sweep `0-15`（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界
480（见上）。report-only。

Controlled local parameterization：`shell_scale`（整体保形，`CENTER_Z` 由其派生
使颈环落地不变）、`flip_range` / `slide_travel` / `bayonet_range`（conditional，按
所选 visor/neck 解析）。全部在 `resolve_config` clamp / 派生；不破坏 captured-hinge
接口、铰链原点对称中心线、multiplicity。连续尺寸契约：先采 independent（shell_scale）
→ conditional 解析 flip_range/slide_travel/bayonet_range + visor gate。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 shell→visor→neck，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | slide→circular-small only；dual→circular only（非 rect）；否则 fallback flip；shell×neck 正交 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | shell_scale + 3 conditional 行程 scale，clamp | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| shell | 4 | yes | yes | sphere/cyl/fishbowl/rect |
| visor | 3 | yes | yes | flip/slide/dual |
| neck_base | 2 | yes | no | fused/twist（pool 仅 2 种颈部结构，degrade-to-2 justified） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ collar_rib_count/eva_port_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented母本 override only)
- compatibility gating prevents illegal combos (slide→circular-small; dual→circular; else fallback flip) in `resolve_config`
- controlled local scales clamped; cannot break captured-hinge interfaces, pivot origin honesty, or multiplicity
- `shell_scale` uniform (neck ring stays on z=0 via derived `CENTER_Z`)
- captured hinge/slider/bayonet overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: visor REVOLUTE(Y) / PRISMATIC(Z); bayonet REVOLUTE(Z)
- copied `port_{i}` follow naming + placement policy; collar rib count applied to the built collar
- `run_astronomy_astronaut_helmet_tests` calls `fail_if_parts_overlap_in_sampled_poses` + ≥1 targeted `ctx.pose` per mechanism

## Reject cases

- Visor flipped/slid pose plunges DEEP through the shell (not thin surface-riding) → cap flip_range/slide_travel; the concentric-cap allow_overlap must not mask a deep 穿模.
- Boolean `outer.cut(inner)` where the CUTTING solid is SHORTER than the outer one along the sweep axis → the difference leaves a FULL-RADIUS SOLID DISC capping each end of what was meant to be an open band. The cylinder bezel had this (inner z-range 8 mm short at each end): invisible while the visor lies closed on the shell, then two flat slabs fly off it the moment the visor opens. Every cutting solid must OVERRUN its outer solid. Audit rule: a band/annulus must contain NO material near its own axis — probe it, do not eyeball it.
- REVOLUTE visor on a host that is NOT a surface of revolution about the joint axis (`cyl_barrel` revolves about Z, the visor about Y; its dome centre is offset from the pivot) → the visor is driven through the wall at every angle and NO clearance value fixes it. Derive the hinge from the host's axis of revolution (brow hinge), and verify with a direct CAD boolean across the sweep, not with the harness (a blanket `allow_overlap(shell_body x visor_*)` hides it completely).
- Joint origin moved off the shell centre without re-expressing the child visuals in the joint frame → the whole visor is displaced by the hinge offset (`fail_if_isolated_parts` gap, `articulation_origin_far_from_geometry` on the child).
- An author invariant that encodes ONE mechanism's signature ("flip raises the bubble in Z") applied to a different mechanism (a brow lid travels mostly +X) → assert the shared invariant (clears the aperture: large displacement AND forward travel) per hinge kind; do not delete the check.
- `dual_flip_visor` inner lens/frame left as a SPHERICAL band on the `cyl_barrel` wall (h-radius `sqrt(r²-z²)` shrinks with |z| while the wall radius is constant → 22.5 mm buried at z=0.08, fully masked by the concentric-cap `allow_overlap`) → give the inner visor the same ENVELOPE branch as the outer bubble. Verify by re-running collision with NO allowances declared.
- `dual_flip_visor` inner lens left circular on a rect_window (lens overshoots the window edge and leaves the corners bare) → give the inner lens the same aperture branch as the outer bubble.
- High-N EVA port bank bunched at the rear tilts the bayonet REVOLUTE(Z) symmetry centerline past the 15 mm origin-honesty floor → widen `port_arc` with N.
- Any `allow_overlap` that turns a genuine envelope/aperture mismatch into a passing seed: the declared reason must be a real surface-riding contact, and the combination must still pass with the allowance removed.
- Shell-form swap leaves decals/ports floating off the new surface (constant sphere-radius decal on a cylinder wall) → derive decal/port placement from the realized envelope (sphere tangent vs cyl wall, Rule 4).
- `locking_ring` twist range so wide the ribbed rim sweeps into the shell wall → clamp bayonet_range near quarter-turn.
- Neck ring floats off the ground after `shell_scale` (constant CENTER_Z) → derive `CENTER_Z=0.160·shell_scale`.
- Downgrading the CadQuery sphere-shell / hemisphere-dome / lathe collar to crude Box/Cylinder placeholders (Rule 3 violation).

## 与相邻类别的边界

- 不该混入：**Astronomy / Pressurised module door**（嵌入舱壁的圆形 EVA 舱门，主体是门叶+门框结构件；头盔是可佩戴的头部尺度壳体，靠颈环落地）。
- 不该混入：**Astronomy / Return capsule**（钝头再入舱，整体载具；非头部尺度可佩戴壳）。
- 不该混入：一个纯装饰的球（无面窗、无可动 visor、无颈环身份特征）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot C 颈部只有 2 个 source-backed candidate（fused_collar / twist_lock_ring），按硬约束 degrade-to-2 并说明理由；无 world_knowledge_extrapolation candidate。待人工确认颈部是否需要补第三形态。 |

## 模板实现备注（可选）

- shell 几何用 `mesh_from_cadquery`（与 5 星源一致，Rule 3 不降级）；`shell_scale`
  用一次 uniform `transformGeometry` 施加，`CENTER_Z` 派生保颈环落地。
- captured hinge/slider/bayonet seat → 原始 joint（no MatingContract, grandfathered，
  Rule 2 例外）+ element-scoped `allow_overlap`，与全部 5 星源一致。
- 薄透明 visor cap 贴着壳体外表面 riding（同心壳盖），全程用 element-scoped
  `allow_overlap(shell_body, visor_bubble/visor_frame)`；理由写明是表面 riding，
  非遮真穿模；若 sampled-pose 出现 DEEP 穿模再收 flip_range/slide_travel 或 gate。
- 一个 `_port_stub_shape` mesh + 一个 visor bubble/frame mesh 各建一次复用；ports 用
  `Origin` 放置 —— 保编译预算。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：shell root 声明
  downstream；visor/neck_base 只声明 downstream（re-export shell）→ 无自动 chain
  joint，各模块发原始 joint 到 shell（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | sphere_dome + flip_visor + fused_collar | `rec_costume-...2b95133f` (origin 母本) | L44-L305 | shell part tree, sphere shell + circular opening, flip REVOLUTE visor (frame+bubble+knobs), fused collar (14 ribs), rear hose, decals, interior lip, 全部 test 语义 |
| S2 | C mult | collar_rib_count=24 | `rec_astronaut_helmet_var_collar_ribs` | L96-L104 | collar rib count multiplicity 上界 |
| S3 | A ③ | cyl_barrel | `rec_astronaut_helmet_var_cyl_shell` | L80-L143, L146-L156, L158-L169 | 圆柱+穹顶 barrel 壳体、cyl 内唇、cyl bubble/frame、cyl decal 放置 |
| S4 | B ① | dual_flip_visor | `rec_astronaut_helmet_var_dual_visor` | L39-L44, L173-L206, L346-L371 | 内层 clear visor part + 独立 REVOLUTE + concentric nesting allow_overlap |
| S5 | A ③ | fishbowl | `rec_astronaut_helmet_var_full_bubble` | L29-L31, L120-L153, L361-L433 | 大口径 fishbowl 开口 + 半球穹顶 visor + decals-inside-dome allow_overlap |
| S6 | A mult | eva_port_count=3 | `rec_astronaut_helmet_var_neck_ports` | L40-L43, L113-L136, L282-L301 | EVA 连接口 stub + N 均布放置 |
| S7 | A ③ | rect_window | `rec_astronaut_helmet_var_rect_window` | L40-L44, L92-L102, L143-L185 | 矩形环绕窗（Planar Boundary）+ 矩形 pane + 矩形 bezel |
| S8 | B ② | slide_visor | `rec_astronaut_helmet_var_slide_visor` | L41-L58, L132-L142, L161-L190, L317-L327 | PRISMATIC 滑动镜 + 壳体导轨 + 滑块 |
| S9 | C ①/② | twist_lock_ring | `rec_astronaut_helmet_var_twist_lock_ring` | L104-L126, L313-L339 | 独立 locking_ring part + REVOLUTE(Z) 卡口锁 |
