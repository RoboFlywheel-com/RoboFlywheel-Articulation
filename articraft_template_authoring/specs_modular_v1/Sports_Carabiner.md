# Modular Spec — carabiner (Sports / Carabiner)

## 元信息
| 项 | 值 |
|---|---|
| slug | `carabiner` |
| template path | `agent/templates/Sports_Carabiner.py` |
| test path (optional) | `tests/agent/test_carabiner_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`parallel_children`：核心是一根弯曲圆棒做成的开口钩 `body`（root），`gate`（摆动闭合件）通过底部 hinge rivet 以 REVOLUTE 挂到 body 上。两根结构轴（body 外形 / gate 闭合机构）各自独立替换，gate 挂在 body 提供的 hinge 接口面上。screw-lock gate 候选额外挂一根 `lock_sleeve` 子件（PRISMATIC），仍属同一 gate slot 内部结构，不是第三根全局轴。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (1 parent + 6 variants) |
| source_index_policy | only adopted module sources are indexed below |

读取清单（全部 `revisions/rev_000001/model.py`）：
- S0 parent `rec_stainless-steel-spring-snap-hook-carabiner-with-_20260605_165816_513107_550acf8b`（pear body + straight solid gate）
- S1 `rec_carabiner_var_oval`（oval body）
- S2 `rec_carabiner_var_dshape`（D body）
- S3 `rec_carabiner_var_offsetd`（offset-D body）
- S4 `rec_carabiner_var_wiregate`（wire gate）
- S5 `rec_carabiner_var_bentgate`（bent key-lock gate）
- S6 `rec_carabiner_var_screwlock`（screw-lock sleeve gate）

## 核心身份

Carabiner = 一根粗圆钢棒弯成的**开口钩 (open hook)** 框 + 一个**弹簧回位的摆门 (gate)**，门补上框开口侧的缺口形成可临时闭合的环。框躺在 X-Z 平面（+Z 向上）：宽圆顶在高 +Z，小眼 (eye) 在低 +Z；门是 -X 直边，绕底部铆钉 (hinge rivet) 以 loop 法线 Y 轴 REVOLUTE 摆动，门顶 latch 闭合时搭在 body 的 nose lug/slot 上，开门时门顶向 +X（环内）摆入 ~0..28°。功能 = 快速可逆地把绳/挂点扣进环里再锁住。成熟域 = 攀岩/消防/通用 snap-hook 形态：单 body + 单 gate，钢质银面。screw-lock 候选额外有一根沿门轴滑动的锁套 (PRISMATIC) 桥接门-鼻缝以上锁。

不混入：钥匙环（无摆门、无铰接）、S-hook/挂钩（无闭合门）、皮带扣/D-ring 五金（不是 spring gate）。

## 槽位 + 候选模块表

### Slot A：body frame form（弯棒开口钩外形）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pear_teardrop | S0 parent | L56-L81（`_body_hook_mesh`，控制点列 L62-74 喂 `tube_from_spline_points`） | eligible if compatible | 非对称梨形：宽圆顶大弯 + 窄底眼；parent baseline；NOSE 在 -X 顶部，HINGE 在 -X 底部，-X 直边留空给 gate |
| oval_symmetric | S1 oval | L58-L116（`_oval_centerline_pts` L58-104 + `_body_hook_mesh` L107-116） | eligible if compatible | 左右对称卵形：顶/底等半径 `R=HALF_W` 两段 170°↔10° 圆弧 + +X 直脊 straight，高>宽 |
| d_shape | S2 dshape | L61-L120（`_body_hook_mesh`，四角紧 quarter-circle，长直脊微 bow） | eligible if compatible | 攀岩 D：gate 侧 -X 直背 + +X 微弓脊，四角 `CR=0.009` 紧弯，`SPINE_BOW=0.002` |
| offset_d | S3 offsetd | L63-L105（`_body_hook_mesh`，额外参数 `TOP_HALF_W/SPINE_BOW/BOT_HALF_W` L51-54） | eligible if compatible | 非对称 offset-D：宽顶承重弯 `TOP_HALF_W=0.030`、长弓脊 `SPINE_BOW=0.034`、底眼收窄 `BOT_HALF_W=0.010` |

Slot A 统一通过把不同中心点列 + bend 半径喂 `tube_from_spline_points` 实现，保持同一开口钩拓扑（NOSE 自由端 + HINGE 自由端 + -X 直 gate gap）；属外形族切换，非纯尺寸缩放。4 candidates，全 ≥3。

### Slot B：gate closure mechanism（摆动 REVOLUTE 门 + latch 接口）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_solid_gate | S0 parent | gate L97-L144（`_gate_body_mesh` L97-121 capsule bar+boss、`_gate_latch_mesh` L124-134、`_hinge_pin_mesh` L137-144）；body nose lug `_nose_lug_mesh` L84-94；joint `gate_hinge` L173-186 | eligible if compatible | 实心圆棒 capsule 平贴 -X 线，顶 latch lip 钩 +X 搭 nose lug；单 REVOLUTE 轴 Y，range 0..28°；parent baseline |
| wire_gate | S4 wiregate | `_wire_gate_mesh` L107-157（单连续 spline：左腿→U-bend→右腿 + 底 hinge_plate）、`_wire_gate_latch_mesh` L160-169、`_hinge_pin_mesh` L172-180；joint `gate_hinge` L211-224；常量 `WIRE_R/WIRE_LEG_SPACING/WIRE_BEND_R` L61-63 | eligible if compatible | 细弹簧钢丝发夹 U 环（两近距平行腿 Y 向 `WIRE_LEG_SPACING=0.0052`，顶 U-bend 连）替代粗棒；同 hinge 同 nose 搭接；更轻更细 |
| bent_gate | S5 bentgate | body `_nose_slot_mesh` L101-133（lug 开槽）；gate `_gate_body_mesh` L136-186（straight+bend+bent+tip+boss）、`_gate_key_mesh` L189-201；joint `gate_hinge` L249-262；bend 常量 L53-74 | eligible if compatible | 实心棒在 `BEND_Z`（68% 处）按 `BEND_ANGLE=40°` 向 +X 折，tip 伸出 key tongue 插入 body nose_slot 凹槽 = 正向 hook-and-slot；body nose 接口由 lug 改为 lug+slot |
| screw_lock_sleeve | S6 screwlock | gate 同 baseline `_gate_body_mesh` L106-130 / `_gate_latch_mesh` L133-143 / `_hinge_pin_mesh` L146-153；`_lock_sleeve_mesh` L156-191；joints `gate_hinge` REVOLUTE L220-233 + `sleeve_slide` PRISMATIC L250-263；sleeve 常量 L55-62 | eligible if compatible | 在 straight_solid_gate 上加第二个动件：knurled 空心套筒沿门轴 +Z 滑动 `SLEEVE_TRAVEL≈0.038`，从 home(low) 滑到 lock(high) 桥接 gate-nose 缝 = 锁；**两个非 fixed joint** |

Slot B 拥有 `gate` part、`gate_hinge` REVOLUTE joint（轴=loop 法线 Y，origin 在 body -X 底部 hinge rivet 接触点 `(GATE_X,0,GATE_HINGE_Z)`）、latch/nose 配合接口、以及任何额外锁定 joint。4 candidates，全 ≥3。

## 槽位图（slot graph）

pattern: parallel_children

```
body (root, Slot A: 弯棒开口钩 + nose lug/slot)
  └─[gate_hinge: REVOLUTE, axis=(0,1,0) loop法线Y, origin=(GATE_X,0,GATE_HINGE_Z), range 0..28°, spring-return closed@0]→ gate (Slot B)
        └─[sleeve_slide: PRISMATIC, axis=(0,0,1) gate-local+Z, origin=(0,0,SLEEVE_HOME_Z), range 0..SLEEVE_TRAVEL≈0.038]→ lock_sleeve  (仅 screw_lock_sleeve 候选存在)
```

跨 slot 接口点：
- **hinge interface（A→B 主连接）**：body 提供 -X 底部 hinge-rivet boss 接触面（free end #2，世界 `(GATE_X,0,GATE_HINGE_Z)`）；gate 在其 local 原点放 hinge boss/plate 消费它。joint = REVOLUTE，轴 Y，range 0..28°。
- **nose-seat interface（A↔B latch 配合）**：body 顶部 -X 提供 nose lug（pear/oval/offsetd/screwlock/wire 候选）或 nose_slot 凹槽（bent_gate）；gate 顶 latch/key 闭合时搭/插入（captured overlap，非 joint）。
- **sleeve rail（B 内部）**：仅 screw_lock_sleeve；gate bar 作为滑轨，lock_sleeve 沿其 +Z 滑动。

互斥/派生：bent_gate 要求 body 的 nose 接口为 **nose_slot**（其余候选为 nose_lug）——属同一 closure 接口的配套面，由 Slot B choice 派生 body 端 nose 形态，不是独立轴。screw_lock_sleeve 要求 gate bar 为连续实心棒，故默认绑 straight_solid_gate baseline。

## 每槽位 Module Emits / Interfaces

### Slot A / module pear_teardrop（及 oval/d_shape/offset_d 同构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root：`body_loop`（tube_from_spline_points 弯棒）+ `nose_lug`（或 bent 时 `nose_slot`）visual | S0 / model.py:L154-156 |
| internal joints | 无（body 为刚性 root） | — |
| upstream interface | root，无 parent；inertial Box `(0.052,0.012,0.100)` mass 0.085 origin z=0.052 | S0 / model.py:L157-159 |
| downstream interface | -X 底 hinge-rivet boss 面 `(GATE_X,0,GATE_HINGE_Z)`（供 gate_hinge）；顶 nose lug/slot 搭接面（供 gate latch/key） | S0 / model.py:L84-94, L173-186 |

### Slot B / module straight_solid_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gate`：`gate_bar`(capsule+boss)、`gate_latch`、`hinge_pin` | S0 / model.py:L162-165 |
| internal joints | 无内部 joint（latch/pin 同属 gate visual） | — |
| upstream interface | hinge boss 在 gate local 原点消费 body hinge-rivet 面；inertial Box `(0.008,0.008,0.058)` mass 0.012 | S0 / model.py:L167-169 |
| downstream interface | `gate_hinge` REVOLUTE 轴 Y range 0..28° origin `(GATE_X,0,GATE_HINGE_Z)` | S0 / model.py:L173-186 |

### Slot B / module wire_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gate`：`wire_loop`(连续 spline 双腿+U-bend)、`wire_hinge_plate`、`wire_latch_tip`、`hinge_pin` | S4 / model.py:L198-203 |
| internal joints | 无（双腿是同一 spline，无独立 joint） | S4 / model.py:L107-157 |
| upstream interface | hinge_plate 桥接双腿供 pin 穿过，消费 body hinge 面；inertial mass 0.004 | S4 / model.py:L205-207 |
| downstream interface | `gate_hinge` REVOLUTE 轴 Y range 0..28°（同 baseline origin） | S4 / model.py:L211-224 |

### Slot B / module bent_gate
| emits | 描述 | 来源 |
|---|---|---|
| parts | body 端改 `nose_slot`（lug 开槽）；`gate`：`gate_bar`(straight+bend+bent+tip)、`gate_key`、`hinge_pin` | S5 / model.py:L227, L236-238 |
| internal joints | 无内部 joint | — |
| upstream interface | key tongue 插入 body nose_slot 凹槽（正向 hook-and-slot capture）；inertial Box `(0.014,0.008,0.058)` mass 0.013 | S5 / model.py:L101-133, L239-243 |
| downstream interface | `gate_hinge` REVOLUTE 轴 Y range 0..28° origin `(GATE_X,0,GATE_HINGE_Z)` | S5 / model.py:L249-262 |

### Slot B / module screw_lock_sleeve
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gate`(同 baseline gate_bar/latch/pin) + 子件 `lock_sleeve`（`lock_sleeve_barrel` 空心 knurled 套筒） | S6 / model.py:L210-212, L240-241 |
| internal joints | `sleeve_slide` PRISMATIC parent=gate child=lock_sleeve 轴 `(0,0,1)` range 0..`SLEEVE_TRAVEL≈0.038` origin `(0,0,SLEEVE_HOME_Z)` | S6 / model.py:L250-263 |
| upstream interface | gate bar 作滑轨；lock_sleeve bore 套在 bar 上（sliding-fit clearance allow_overlap） | S6 / model.py:L156-191 |
| downstream interface | `gate_hinge` REVOLUTE（同 baseline）；锁套随门一起摆 | S6 / model.py:L220-233 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | {pear_teardrop, oval_symmetric, d_shape, offset_d} | pear_teardrop | choice | deterministic procedural sampler 选择 | Slot A table |
| gate_mechanism | enum | {straight_solid_gate, wire_gate, bent_gate, screw_lock_sleeve} | straight_solid_gate | choice | sampler 选择；screw_lock_sleeve 仅与连续实心 gate body 兼容（见兼容矩阵） | Slot B table |
| palette_style | enum | {bright_satin_steel, dark_anodized_steel, polished_chrome, matte_black_tactical, anodized_red_accent, brass_gold} | bright_satin_steel | choice | 每 seed 采样；映射 (satin/body, dark/pin·sleeve) 两材质 rgba | S0 L150-151 + 全样本材质集 |
| body_height_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放 TOP_Z/EYE_Z 跨度，clamp；保持 body 高>宽 identity | S0 / L46-48 |
| body_width_scale | float | [0.82, 1.20] | 1.0 | independent | 缩放 HALF_W（及 offset_d 的 TOP/BOT_HALF_W、SPINE_BOW 按比例） | S0 L46 / S3 L51-54 |
| bar_radius_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 BAR_R/GATE_R | S0 / L43,53 |
| gate_open_angle | float | [22°, 32°] | 28° | independent | gate_hinge upper limit；下限固定 0（spring-return） | S0 / L181-184 |
| sleeve_travel_scale | float | [0.9, 1.1] | 1.0 | conditional | 仅 gate_mechanism=screw_lock_sleeve 时存在；缩放 SLEEVE_TRAVEL | S6 / L60-62 |
| (—) gate_len | float | derived | 0.054 | equation | `GATE_LEN = (GATE_NOSE_Z−GATE_HINGE_Z)·body_height_scale`；门长随框高 | S0 / L52 |
| (—) hinge/nose z | float | derived | — | equation | `GATE_HINGE_Z, GATE_NOSE_Z = base·body_height_scale`；hinge origin 与 nose-seat 联动 | S0 / L50-51 |
| (—) sleeve clearance | constraint | — | — | inequality | `SLEEVE_IR ≥ GATE_R·bar_radius_scale + 0.0004`；违反时放大套筒内径或拒绝重采 | S6 / L56 |
| (—) nose-seat reach | constraint | — | — | inequality | gate latch/key 顶端世界位置必须落在 body nose lug/slot 的 contact_tol(≤0.0015) 内；body_height_scale 与 gate_len 必须协同回缩 | S0 / L242-249 |

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots 表达（**一个 body + 一个 gate**），不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。Π = 4 (body) × 4 (gate) = 16 ≥ 10，无需 N 轴。
- 不存在 N-identical 子件。`N_range` 不适用。
- wire_gate 的两根平行 wire legs **不是** multiplicity 轴：源样本里它们本就是**一根连续 spline**（左腿→U-bend→右腿，S4 L127-135），固定 2-leg；若未来要显式拆，用局部 `for i in range(2)` helper（`gate_wire_leg_{i}`、镜像 placement、同一 gate part 无独立 joint），仍不当全局 N 轴。
- screw_lock_sleeve 的 `lock_sleeve` 是一个**命名固定子件**（恰 1 个），非复制 N。

## 拓扑多样性审计

总组合数：body_form(4) × gate_mechanism(4) = 16。扣除兼容矩阵排除（screw_lock_sleeve 仅绑连续实心 gate body —— 该排除作用在 gate↔gate-body 一致性上而非 body_form，故 body_form 仍全 4 合法）→ 合法拓扑 16（若 screw_lock 进一步限定特定 body，最坏退到 13，仍 ≥10）。无 multiplicity，N 采样数=1。

理由：仅 slot 选择就给 16（或最坏 13）个 distinct module 组合，远超 10。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 先对 body_form、gate_mechanism 各做一次加权采样（四候选近均匀，screw_lock_sleeve 略降权因其额外 joint 复杂度）；compatibility matrix 在采样后 gate（见下表）拦截非法组合并 fallback 到 straight_solid_gate。然后采 independent 连续 scale（body_height/width、bar_radius、gate_open_angle），按 equation 派生 gate_len 与 hinge/nose z，用 inequality 投影 nose-seat reach 与 sleeve clearance，conditional 解析 sleeve_travel_scale（仅 screw_lock）。无需 curated/modulo 主表；regression overrides=none。
Topology target：1000-seed slot choice tuple distinct 目标无法超 16（类别本身只有 16 个 slot 组合）—— 这是类别固有上限，<300 的原因是 carabiner 拓扑窄（双轴各 4），主要多样性来自 16 组合 + 连续比例/palette 变体；记为类别约束豁免。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：body_height_scale [0.85,1.18] indep、body_width_scale [0.82,1.20] indep、bar_radius_scale [0.85,1.20] indep、gate_open_angle [22°,32°] indep、sleeve_travel_scale [0.9,1.1] conditional；全部在 `resolve_config` clamp/派生，gate_len 与 hinge/nose z 用 equation 锁定，nose-seat reach 与 sleeve clearance 用 inequality 回缩，不破坏 hinge 接口、latch 搭接、PRISMATIC range 或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 body_form→gate_mechanism→continuous scales；近均匀加权（screw_lock 略降权） | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | screw_lock_sleeve × wire_gate / bent_gate = 非法（细 wire/异形 tip 无连续实心轨）→ fallback straight_solid_gate；bent_gate→body 端切换 nose_slot；其余 body×gate 全合法 | no floating, collision, axis, gate closed-pose, sleeve clearance, nose-seat contact |
| controlled local variation | 上列 5 个连续 scale + clamp/equation/inequality | 比例变化不破坏接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 4 | yes | yes | |
| B gate_mechanism | 4 | yes | yes | screw_lock 含第二 PRISMATIC joint |

## Validator

- slot_choices_for_seed returns implemented module names（body_form ∈ 4、gate_mechanism ∈ 4）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix gates screw_lock_sleeve 只配连续实心 gate body，bent_gate 配 nose_slot
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table（procedural 主域）
- controlled local scale params clamped；gate_len/hinge/nose z 用 equation 派生，nose-seat reach 与 sleeve clearance 用 inequality，不破坏接口/clearance/joint origin
- cross-part scale dependencies resolved in `resolve_config`（非 builder）
- critical InterfaceSpec/MatingContract 存在：hinge-rivet 面、nose-seat 搭接、sleeve rail
- key joints：`gate_hinge` REVOLUTE 轴 Y range 0..gate_open_angle；`sleeve_slide`（仅 screw_lock）PRISMATIC 轴 +Z range 0..travel
- copied objects follow naming/placement policy（无模板级复制；lock_sleeve 单命名子件）

## Reject cases

1. gate 闭合 (q=0) 时 gate latch/key 未搭到 nose lug/slot（contact_tol>0.0015）—— body_height_scale 与 gate_len 未协同，门补不上开口缝。
2. gate_hinge origin 不在 body -X 底 hinge-rivet 接触面 → gate 浮空/穿框，或开门方向不是门顶向 +X 摆入。
3. screw_lock_sleeve 配 wire_gate / bent_gate（无连续实心轨）→ 套筒穿模/脱轨；必须被兼容矩阵 fallback 拦截。
4. bent_gate 用了 nose_lug 而非 nose_slot（key tongue 无凹槽可插）→ 闭合无 capture。
5. lock_sleeve 内径 < gate bar 半径（SLEEVE_IR < GATE_R·scale）→ 套筒与门杆硬穿模而非滑动间隙。
6. body 退化为 closed loop（NOSE/HINGE 两自由端被连上）→ 失去 open-hook + gate gap identity。
7. gate 暴露为模板级 `*_count` 复制或 N 轴 → 违反“一 body 一 gate”固定结构。
8. body 高度 ≤ 宽度（identity 检查失败）或 body z-extent < 0.085（过矮，非 carabiner 比例）。

## 与相邻类别的边界

- 不该混入：钥匙环 / Key ring（无摆门、无 hinge，纯闭合圈——carabiner 必须有 spring gate REVOLUTE）。
- 不该混入：S-hook / 普通挂钩（开口钩无可闭合门，无 latch-nose 配合）。
- 不该混入：皮带扣 / D-ring 五金（D 形环但非 spring-gate snap-hook，无摆动闭合件）。
- 不该混入：弹簧锁扣门把/cam-lock（cam/dial 机构不同；carabiner 是单轴 gate + 可选滑动锁套）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待审：(1) screw_lock_sleeve 是否限定特定 body_form（当前仅限定 gate-body 为连续实心，body_form 仍全 4 合法，最坏退 13）；(2) palette_style 6 档是否保留 brass_gold/anodized_red 这类非纯钢 colorway（源样本只有 satin/dark 两钢材质，红/金/黑为合理扩展但非样本直采）；(3) slot choice tuple distinct 上限=16 属类别固有窄轴，确认豁免 ≥300 目标。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A+B | pear_teardrop + straight_solid_gate | rec_stainless-steel-spring-snap-hook-carabiner-with-_20260605_165816_513107_550acf8b | body L56-94, gate L97-144, joint L173-186 | parent baseline body + gate + hinge |
| S1 | A | oval_symmetric | rec_carabiner_var_oval | L58-116 | oval body 外形 |
| S2 | A | d_shape | rec_carabiner_var_dshape | L61-120 | D body 外形 |
| S3 | A | offset_d | rec_carabiner_var_offsetd | L51-105 | offset-D body 外形 + 额外宽度参数 |
| S4 | B | wire_gate | rec_carabiner_var_wiregate | L61-63, L107-180, joint L211-224 | wire gate part + hinge |
| S5 | B | bent_gate | rec_carabiner_var_bentgate | L53-74, nose_slot L101-133, gate L136-201, joint L249-262 | bent key-lock gate + nose_slot 接口 |
| S6 | B | screw_lock_sleeve | rec_carabiner_var_screwlock | L55-62, sleeve L156-191, joints L220-233 + L250-263 | 第二 PRISMATIC 锁套 joint |
