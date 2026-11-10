# Agent 单文件模板制作流程

开始源资产分析前，完整阅读 `MECHANICAL_PRIORS.md`。它约束 Agent 如何保留源资产质量、
设计贴面/同轴接口和运动余隙，但不会被最终模板读取，也不形成新的运行时真源。

## 1. 产物和真源

每个新模板有三层产物：

1. `SourceMap`：完整审阅指定小类源池，并记录真实可用源组件及证据。
2. `TemplateDesign`：记录槽位、候选、参数、派生、接口、N、装配与宿主适配决策。
3. `agent/templates/<slug>.py`：包含完整生成逻辑的普通函数式单文件模板；
   PBR 标签不参与机械验收。

只有第 3 层是运行真源。SourceMap 和 TemplateDesign 帮助 Agent 做决策，不被
seed 运行时读取。

模板可以保留 `material_class_id` 和 `appearance_only` 作为 PBR 材质池索引标签，正式
PBR 库也继续保留逐材质物理属性；二者都不属于当前机械管线。现有 `target="full"`、
preflight、random-16、random-36 和 corner 不打开 PBR/physics 路径、不采样
`material_seed`、不根据材质计算质量属性，也不覆盖 authored/proxy `Part.inertial`。

模式由磁盘产物直接决定：没有 TemplateDesign 的存量模板保持 `legacy` 兼容；正式
`designs/<slug>.json` 一旦存在，就代表已经选择新管线。此时缺少有效
`TEMPLATE_DOMAIN` 的模板是 `incomplete_migration`，必须按本流程重做，不能退回 legacy
放行。迁移草稿不要写入正式 `designs/` 目录。

## 2. SourceMap

先发现小类当前的完整 active workbench 源池：

```bash
articraft template source-map-init <slug> \
  --records-root <records-root> \
  --picture-category <picture-category> \
  --picture-subcategory <picture-subcategory>
```

SourceMap 随后只回答源资产事实：

- `sync_records` 是否与当前小类源池完全一致；
- 每条 record/revision 是否已经审阅，决定是使用、参考、重复或无结构价值；
- 每个槽位的候选来自哪个 record/revision 和 `model.py` 行段；
- 候选是什么组件类型，结构或运动上为什么值得复用。

SourceMap 不复制源码，不列出 AST 闭包，不存 snapshot。它可以由人或 Agent 重写，
但 record、revision 和行段必须能在给定资产根目录下解析。它也不定义参数、派生、
interface、binding、multiplicity 或详细 category anchor；这些属于 TemplateDesign。

完成全部审阅后执行：

```bash
articraft template source-map-check \
  --source-map <source-map.md> \
  --records-root <records-root>
```

未审阅源资产、漏记/多记 record、过期 revision、越界代码行、没有候选贡献的 `used`
记录都会阻断 `design-init`。被判为重复或参考的源资产仍保留审阅记录，但不需要制造重复候选。

## 3. TemplateDesign

使用命令从 SourceMap 生成骨架：

```bash
articraft template design-init <slug> \
  --source-map <source-map.md> \
  --records-root <records-root>
```

默认写入 `articraft_template_authoring/designs/<slug>.json`。Agent 随后补全：

- SourceMap 候选的最终 slot 组织和每个 candidate 的实现函数；
- 真正改变结构或几何的独立参数；
- 独立参数的语义单位（例如 `m`、`rad`、`ratio`、`count`）；
- 只由其他参数计算的局部派生参数及其 DAG；
- 与其他组件装配所需的 plane/axis interface；
- N 的取值、spacing 与 host capacity。N 的上下界由机构规则是否 index-general、宿主容量
  和编译/位姿预算决定，**不由源池中出现过的整数限制**：源值只是该规则成立的证据，不是上界。
  若预算迫使 N 低于源池已建过的值，在 SourceMap 中写明被放弃了什么；
- 组件间 binding 和跨组件派生；
- 轮廓、容量或支承需求不同时，宿主如何派生过渡框、肩部、开口或承载边。
- 新建或重做模板的轻量 `category_anchors`：按候选声明类别识别所必需的
  `part.meta.role` 数量、父子 role/关节关系和命名作者测试。已有 Design 缺失 anchor
  只告警，不强制迁移。
- 对按钮、键帽或嵌件等局部表面关系，在对应 plane interface 的 `surface_relation`
  中记录 subject role、开孔/footprint 表达式、带符号法向露出带、可选运动表达式和
  最大行程最小凸出厚度，以及必须执行的类别作者测试；该 role 与测试名必须同时出现
  在适用的 category anchor。

TemplateDesign 不包含组件源码、类 Factory 中间产物、闭包 hash、snapshot 或
linker manifest。它的价值是把 Agent 的语义决策压缩成可检查的小对象。

当前正式流程优先充分利用已审阅的源组件，不增加独立的 `based_on`、派生候选或
candidate extension 层。新的结构候选应先成为可审阅的源资产，再进入 SourceMap。

## 4. 单文件模板

模板以普通私有函数表达组件生成逻辑。每个候选可以有自己的 profile、mesh、
helper 和局部派生，最后由 build 函数根据 Config 选择并装配。不要为缩短文件而把
源资产质量降级成简单 box/cylinder 占位符。

新模板至少导出：

- `Config` 和 `config_from_seed(seed)`；
- `resolve_config(config)`，对独立参数做范围检查并计算派生值；
- `build_<stem>(config, assets=...)`；
- `run_<stem>_tests(model, config)`；
- 新结构化模板导出 `TEMPLATE_DOMAIN`；
- 需额外连续边界或高风险组合时导出 `TEMPLATE_CORNERS`。
- 每个真实生成的 visual 在 part 内名称唯一；已有 PBR 标签不参与机械判定。

限制：

- `config_from_seed` 从组件候选和约束域采样，不将预建好的完整资产逐个塞入模板；
- `TemplateDomain` 中声明的槽位形成完整组合域，每个组合都必须可构建；
- N 是 multiplicity，不计入 `core_domain`，计入 `raw_domain`；
- 调色板、连续尺寸和装饰数量不计入 core/raw；
- 禁止导入 source runtime、snapshot `model.py`、其他组件文件或其他模板；
- SDK 承担稳定通用能力，模板承担对该类别有语义的几何和组合逻辑。
- 装配 allowance 的权威规则维护在 `agent/prompts/sections/sdk_base.md`；本文件不重复定义，
  模板作者和 Repair Agent 应以该 section 为准。当前不改变 `ctx.allow_isolated_part(...)`
  的兼容行为；legacy 模板也不强制迁移。

通用装配直接使用 SDK 的轻量接口：平面连接声明 `PlaneInterface`，同轴连接声明
`AxisInterface`，再由 `mate_planes` / `mate_axes` 求出确定性 `Origin`。接口对象只描述
局部坐标系和可选容量，不要求 adapter、component manifest、binding manifest 或整组件
graft。模板已有的 `MatingContract` 继续用于关节与几何的运动语义检查，两者可以独立使用。
现有模板不因 SDK 增加轻量接口而强制迁移。

`TEMPLATE_DOMAIN` 同时标记新模板的严格机械 contract。其每个 revolute/continuous 关节必须
使用 `register_interface_mate` 登记由 `mate_axes` 得到的结果；基础 QC 会拒绝缺失登记、用
plane mate 冒充 axis mate、装配原点漂移或实际关节轴不一致，避免轮子、齿轮或铰链绕错误的
表面切向轴旋转。legacy 模板没有 `TEMPLATE_DOMAIN` 时保持原有 opt-in 行为，不强制迁移。

层板、烤盘、面板等平面安装应把真实承载区写入 `PlaneInterface.extent`，由 `mate_planes`
在局部表面坐标中拒绝一半悬空或一半伸出内腔的 placement。旧字段
`MatingContract.tangential_containment` 是轴对齐平面的安装 footprint 兜底检查，不是旋转轴检查；
斜面、曲面和运动中的 containment 不应依赖世界坐标 AABB。

异形组件组合不能只做刚性拼接。组件的 interface dimensions 应暴露安装 footprint、边缘轮廓、
支承跨度或所需开口；assembly binding 的 derived 参数据此驱动宿主局部几何。例如方形柜身搭配
扇形顶板时，柜身顶部派生弧形过渡肩、顶框或承载边，柜身主体仍可保持方形。若某个候选必须
改变整个宿主拓扑、无法由局部适配表达，则它与宿主不是独立槽位，应合并为一个结构家族候选。
对这种高风险跨槽位组合补一个命名 `TEMPLATE_CORNERS`，并由作者测试检查接触、支承和净空。

现有 legacy 模板可以暂时导入旧 helper；preflight 会把它标为 `legacy_compatible`。
新建和重做的模板应当是 `self_contained`。

## 5. Preflight 与累计检查

```bash
articraft template check <slug> --stage random-16
articraft template check <slug> --stage random-36
articraft template check <slug> --stage corner
```

**Preflight 不构建任何几何。** 它是进入 random sweep 前的声明层门禁，报告拆成两个
phase：只读 AST 与 Design 的 `contract`（Tier 0-A），以及只跑
`config_from_seed`/`resolve_config` 的 `domain_resolution`（Tier 0-B）。两者都是穷尽的，
都不调用 build。全部 105 个 Design-backed 模板跑完平均 0.15 秒。

分工的依据是：一个候选**能不能建**，sweep 无论如何都会建它——random-16/36 抽样加上
corner 补齐未出现的 candidate 与 N min/max，覆盖是有保证的。让 preflight 先建一遍，89%
的情况下（fleet 1492 份缓存报告中 1324 份为 pass）是纯重复劳动。因此几何归 sweep，
声明归 preflight。

Tier 0-A（静态，零执行）：

- 阻断重复顶层函数/类和被后续定义或赋值覆盖的必需导出；不可达私有 helper 只告警；
- 对齐 TemplateDesign 与 `TEMPLATE_DOMAIN` 的组件槽位和候选；
  SourceMap hash、源码定位和实现函数漂移只告警；
- 声明的 derived DAG 自依赖/环，以及 binding 两端的 slot/interface 解析；
- `category_anchors` 声明的 `required_author_checks` 必须在模板源码里真实存在（字面量或
  f-string 骨架均可）。role 数量与 role/joint 关系的**语义**由这些作者检查本身保证，
  而 sweep 会在每个已构建 seed 上以真实几何执行它们，preflight 不再用 stub mesh 重算一遍；
- 每个在 Design 中声明了 `minimum`/`maximum` 的独立参数，必须有一条 `TEMPLATE_CORNERS`
  把它固定到某个声明边界上（`corner_numeric_boundary_unauthored`，告警）。数值边界现在
  由 corner 拥有——corner override 接受任意 Config 字段，不限于 domain 槽位。

Tier 0-B（穷尽解析，零 CAD）：走采样器扫描 seed，直到声明域饱和，并 resolve 每个 config。

- 每个声明候选都必须被采样器实际产出（`domain_candidate_unreachable`，阻断）；
- 每个跨槽位候选对都记录可达性（`domain_pair_unreachable`，告警——有界扫描无法区分
  "不可达"与"极稀有"）。这是全管线唯一读取 hard boundary 7「每个声明组合都必须成立」
  的地方；
- 采样器产出的任何 config 都不得让 `resolve_config` 抛异常
  （`domain_combination_unresolvable`，阻断）；
- multiplicity 的 `candidate × N` 组合必须全部被采样器覆盖
  （`multiplicity_sampler_missing_combination`，阻断）；
- 每个独立参数在**选中其所属 candidate 的那些 seed 上**必须取到一个以上的值，否则
  阻断（`parameter_resolution_no_effect`）。`resolve_config` 内部的静默强制转换正是长成
  这个样子。候选被抽到少于 4 次时不做判定——单次抽样会让所有参数看起来都是常量。

枚举必须走采样器，不能用 `dataclasses.replace` 硬换槽位：candidate-local 参数分带会让
手工拼装的组合变成采样器根本不会产出的东西（吉他弦钮 72 个 core 组合里有 36 个会因此
抛 `ValueError`，而没有任何 seed 能复现）。

没有 TemplateDesign 的 legacy 模板仍只执行 Tier 0-A 的兼容性检查，不强制迁移。

对于存在 TemplateDesign 的模板，preflight 还会阻断源码中的 `allow_overlap` 调用。
该策略不检查或阻断 `allow_isolated_part`。

Preflight 报告包含分组 `checks`、`phases.contract`、`phases.domain_resolution`（含
`scanned_seeds`、`saturated`、`reached_pairs/declared_pairs`，`builds` 恒为 0）、可操作
`findings`、`repair_gate` 和 `quality_contract.sha256`。失败时
`next_stage=preflight`，修复 finding 后重跑同一阶段；只有 preflight 通过
才会执行 random sweep。checker 不自动修改模板。

- `random-16`：累计 seed 0–15，通过率阈值 0.90，至少 15/16 通过。
- `random-36`：累计 seed 0–35，通过率阈值 0.90，至少 33/36 通过。模板机械 hash
  未改变时，复用 0–15 的 artifact，
  只构建缺失 seed。

**整体通过率阈值不能赦免单个候选。** 两个随机阶段都把同一批 outcome 按候选拆开
（`random_sweep.candidate_coverage`）：任何被抽到过、但**没有任何一个 seed 通过**的候选
直接阻断该阶段，不受 0.90 庇护。这不额外构建任何东西——统计的就是 sweep 已经建好的那些
seed。理由是阈值本身留了洞：seeds 0–15 只抽到一次的候选（实测
`pictureX_0611_guitar_tuning_peg_mechanism` 的 `open_plate`）即使 100% 失败，
15/16 = 0.9375 仍然过关；`Bag_Suitcase_Shopping_bucket` 在 0–15 里有 4 个候选被抽到 ≤1 次。
从未被抽到的候选记为 `uncovered` 而不是失败——那是 corner 的职责。
- `corner`：先确保 random-36 达标，再读取这 36 个实际 Config，只补其中没有出现的
  candidate 与 N min/max，并运行作者声明的全部高风险组合。Corner 任一失败都阻断。

所有随机 seed 和合法 corner 都运行 CAD、作者测试、URDF、拓扑、断裂几何、碰撞和
motion QC。continuous 关节使用 SDK 代表姿态；mimic 关节由驱动关节覆盖。

基线 QC 中，part 间接触或不超过 1 mm 的装配间隙视为有支承；真实穿入深度不超过
5 mm（含边界）不判失败，同时还需超过体积阈值才报告 overlap。世界 AABB 只做粗筛，
最终判定使用 FCL，并对可形成实体的 mesh 命中计算真实交集。类别作者测试中的
`expect_contact(...)` 默认使用 0.5 mm；只有机构语义与碰撞几何精度确实支持时才显式收紧。
Preflight 会对新写入的微米级 `contact_tol` 给出非阻断提醒。

每个新模板 seed 在进入 motion QC 前还会执行一次静态接口 contract：所有旋转关节必须具有
已登记的 axis mate，且实际 origin、orientation、axis 与接口求解一致。轴定义不随 pose 改变，
因此无需在每个运动姿态重复；运动后的穿模仍由 sampled-pose collision QC 负责。

Motion QC 的必需姿态不受可选采样预算截断：默认每个有界 revolute/prismatic 关节在其余
关节保持合法中性值时分别执行 lower/upper；continuous 的 0° 由全局 neutral 覆盖，
并额外执行 -90°、+90° 和 180°。coverage 只读取碰撞检查实际执行的 pose ID，不从
URDF limit 推断。

大量同构、同父级且具有相同轴和 limits 的重复机构（例如独立键帽）可在 articulation
metadata 中显式声明同一个 `motion_qc_repeat_group`。这不会减少 part、joint、轴向、limits
或作者测试的逐件校验，只把昂贵的 lower/upper 碰撞姿态改为每组最多 12 个确定性代表：
空间边缘、中心以及随 seed 轮换的成员。未声明的关节仍逐个完整执行，报告必须记录组内总数
和本 seed 实际执行的关节名；不得用该标记掩盖异构机构或 mimic 独立运动。

模板显式声明的 `risk_poses` 和 `coupled_joint_pairs` 同样完整执行。仅由拓扑相邻自动推断的
联合姿态采用小预算：每个相邻关节对约取两个边界组合、全局最多 8 个，再补最多 2 个由 seed
确定的随机联合姿态。报告分别统计 neutral、单关节边界、continuous、authored risk、显式
耦合、自动 pair 和随机姿态，避免用一个不透明的总姿态数衡量覆盖。

缓存位于 `.cache/template_check/<slug>/<mechanical-hash>/`。机械 hash 改变后旧缓存自动失效。
重复执行未改变的 random-36 应得到 36 hits / 0 misses，但这只是幂等性，不是新阶段。

## 6. 修复边界

检查失败时修复实际几何、拓扑、关节或参数约束。不得通过删除测试、冻结运动、
扩大 overlap allowance、特判 seed 或从采样域删除失败组合来绕过。

`random_sweep.repair_findings` 会把当前累计 sweep 的失败按 check 与实际机械实体做
确定性归组，并报告：受影响 seed、part/joint/element/pair/pose、失败 Config 的共同值
与变化字段、最近的通过 Config、候选组件函数和模板代码行。Config 对比只作为相关性
证据，不自动断言根因。完整 `failed_outcomes` 仍然保留，归组不会隐藏单 seed 证据。

每个 finding 同时带有 `source_review_policy`。明确涉及 interface mate、旋转轴、关节原点
或关节拓扑的错误标记为 `decision=required`、`blocking=true`；Repair Agent 在修改模板前
必须读取 `source_targets` 中每个 record/revision 的精确 `model.py` 行段。若 Design-backed
模板缺少可解析的 record、revision 或 source span，先修 SourceMap/TemplateDesign 映射，
不得直接猜测并修改模板。motion collision、跨组件 overlap、isolated/disconnected geometry
及一般作者测试默认标记为 `recommended`：当 Design 不能消除机构意图歧义，或修复会改变
源结构、接口或主要比例时，Agent 必须升级为源码复查。compile/runtime、mesh asset、超时和
缺失 exact-name 等实现性错误不要求源码复查。

阶段报告中的 `repair_gate` 聚合所有 finding：`source_review_required` 表示仍有阻断项，
`repair_allowed` 表示可直接处理最高优先级 finding，`not_needed` 表示没有失败。该门禁是
单次报告中的机器可读 repair policy，不持久保存 review receipt、cluster 或 streak，也不让
SourceMap、TemplateDesign 或源 `model.py` 进入 seed 运行时。

Sweep 的 `repair_gate` 同时携带 preflight 生成的质量合同 digest 和强制的 random-16 重跑
参数。修复时使用：

```bash
articraft template check <slug> --stage random-16 \
  --expected-quality-contract-sha256 <repair_gate 中的 sha256>
```

质量合同规范化覆盖槽位候选域、multiplicity、独立参数范围、derived DAG、bindings 和接口
语义，但排除源码行段、SourceMap hash、实现函数名、注释和材质。若 sweep repair 删除参数、
缩小范围、移除候选/N 或删除派生关系，preflight 以
`quality_contract_changed_during_repair` 阻断。确需改变质量合同时，退出 repair 流程，把它
作为显式 Design 变更重新开始 preflight；不得在 sweep 修复中静默改变。

源码复查只恢复结构和机构意图，不能把已批准的参数化、组件内派生、跨槽位 binding 或 N
改回源 `model.py` 中无参数化的固定值。修改源码映射、实现函数名或内部代码组织不会改变
质量合同。

新模板宜把可诊断的 part/joint 名称写成
`<slot>__<candidate>__<local_name>`。checker 会结合该前缀、TemplateDesign 中的
`implementation_function`/interface part、模板函数中的实体字符串和 Python traceback，
定位普通单文件模板中的组件函数。legacy 模板没有 TemplateDesign 时仍可通过 traceback
和实体字符串获得退化定位结果。

这份 repair summary 只为当前运行提供导航，不持久维护 failure cluster/streak，不参与
seed 构建，不修改组合域，也不成为新的模板真源。Agent 应优先修复影响 seed 最多的 finding，
从代表性失败 Config 与最近通过 Config 入手，只阅读被定位的组件/装配函数。

当 `corner` 通过后，模板完成机械验收。可用已有预览脚本对代表性 seed 渲染 contact
sheet，人工确认关键轮廓、承载结构和机构仍具有类别识别度；这一步不写持久 receipt，
也不把图片或源资产引入 seed 运行时。除这项审看外，本管线不进行 source fidelity、
PBR/physics 物化、snapshot 复现或发布追溯签名。

Strict 的完成状态区分容差：random-36 为 36/36 且 corner 通过时是 `strict_ready`；
33–35/36 且 corner 通过时是 `strict_ready_with_tolerance`。失败 seed 和 repair findings
始终保留在 corner report 中。Strict 的 0.90 下限不能通过 CLI 调低；legacy 仍保留原有
诊断阈值能力。`strict_ready` / `strict_ready_with_tolerance` 是当前管线终态，不再派生
mechanical receipt、annotation receipt、材质驱动的质量属性或改写后的 URDF。
