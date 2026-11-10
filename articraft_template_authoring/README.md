# Articraft template authoring

当前 Agent 造模板管线只有一条正式路径：

```text
SourceMap
→ TemplateDesign
→ 普通函数式单文件模板
→ preflight
→ random-16
→ random-36
→ corner
→ strict_ready / strict_ready_with_tolerance
```

这一个入口内部有两种模式：没有 TemplateDesign 的已有模板走 `legacy` 兼容检查；
正式 `designs/<slug>.json` 存在时即视为已选择新管线，模板必须同时导出
`TEMPLATE_DOMAIN`，否则状态为 `incomplete_migration` 并按新单文件流程重做。不要把尚未
决定迁移的草稿放进正式 `designs/` 目录。

`TemplateDesign` 是一份小型、可机读的设计说明，不是源码容器。它只记录无法从
SourceMap 机械推导的决策：槽位与候选、真实参数、局部派生、接口、N、装配绑定
和跨组件宿主适配。新建或重做模板还可声明轻量 `category_anchors`，把类别识别所需的
关键 role、关节关系与作者测试纳入 preflight 和 sweep 修复质量合同。
穿过局部表面的按钮、键帽或嵌件还应在对应 plane interface 上声明
`surface_relation`：记录开孔/footprint、沿局部法线的露出带、可选全行程约束，以及
最大行程时的最小凸出厚度和负责执行它的类别作者测试。

SourceMap 是完整源池的事实层，不是设计层。它必须逐条覆盖指定 picture 小类当前
workbench 中的全部 active record，记录每条源资产的审阅决定，并只为真正可利用的源组件
提供 record/revision、精确代码行和结构/运动证据。参数范围、派生、interface、binding、
multiplicity 和详细 category anchor 不写入 SourceMap。

最终模板是唯一运行真源。它必须包含自己的组件生成和装配逻辑，只允许依赖
Python 标准库、Articraft SDK 和可选的内容寻址二进制资产。正常 seed 构建不读取
SourceMap、TemplateDesign、source runtime、snapshot 或其他组件 Python 文件。
组件装配可直接使用 SDK 的 `PlaneInterface` / `AxisInterface` 与
`mate_planes` / `mate_axes`；当前流程不生成 adapter、component manifest 或 graft 中间层，
也不要求已有模板迁移到这些轻量接口。

模板可以保留用于索引 PBR 材质池的 `material_class_id` 和 `appearance_only` 标签，
但它们不参与机械管线。现有 `target="full"` 以及 preflight、random-16、random-36、
corner 都是纯机械检查：不打开 PBR/physics 库，不采样 `material_seed`，不根据材质
计算质量属性，也不改写机械阶段的 authored/proxy 惯量。

## 目录边界

- `AUTHORING.md`：当前的唯一实施流程和验收规则。
- `MECHANICAL_PRIORS.md`：造模板时使用的跨类别机械判断清单；不参与 seed 运行。
- `VISUAL_DIVERSITY_MODEL.md`：定义结构多样性口径和完整组合原则，不引入渲染检查。
- `source_maps/`：源资产到候选组件的高层语义映射。
- `designs/`：新流程的 `TemplateDesign` JSON。
- `legacy/`：旧模板的历史设计参考；仅供后续维护时查阅，不是当前管线输入。
- `specs_modular_v1/`：仅为已有 legacy 模板保留的旧设计参考；新模板不再写入这里。
- `category_template_registry.json`：仅为少量 v1 spec 保留的 legacy 结构轴/gate 配套数据。
- `picture_source_maps/`：仅为已有 picture 模板保留的旧来源参考；当前 SourceMap 写入
  `source_maps/`。

## 历史引用说明

现行 `AUTHORING.md` 使用数字章节 §1–§6。部分 legacy 模板注释中出现的
`AUTHORING.md §A / §B / §C`（例如 `§A Rule 3`、`allow_overlap per §B`、
`§C axis_realization`）指向的是**旧版 AUTHORING 的三段式结构**（设计规则 / 模块化契约 /
迭代循环），当前文档中已无对应章节，也**不对应** `build-template` skill 的 A–E 阶段
（A SourceMap、B TemplateDesign、C 单文件实现、D 累计检查、E 修复与完成）。遇到这类
注释时按当前 `AUTHORING.md` 与 skill 判断，不要按字母回查。这些注释是历史记录，不需要
为此批量改写 legacy 模板。

同样已废弃的还有旧命令 `articraft template sweep-pipeline`；当前每阶段的权威信号是
`articraft template check <slug> --stage random-16|random-36|corner`。

## 入口

```bash
articraft template source-map-init <slug> \
  --records-root <records-root> \
  --picture-category <picture-category> \
  --picture-subcategory <picture-subcategory>

# 人或 Agent 审阅 scaffold 中的每条源资产并填写真实候选后：
articraft template source-map-check \
  --source-map articraft_template_authoring/source_maps/<slug>.md \
  --records-root <records-root>

articraft template design-init <slug> \
  --source-map articraft_template_authoring/source_maps/<slug>.md \
  --records-root <records-root>

articraft template check <slug> --stage random-16
articraft template check <slug> --stage random-36
articraft template check <slug> --stage corner
```

CLI 与 HTTP API 共用 `TemplatePipelineService`，不会形成第二套管线。Viewer API 提供：

- `POST /api/template-pipeline/source-maps`：发现完整小类源池并创建待审阅 SourceMap；
- `GET /api/template-pipeline/{slug}`：检查产物状态并返回下一步；
- `POST /api/template-pipeline/{slug}/source-map/check`：执行严格源覆盖/证据检查；
- `POST /api/template-pipeline/{slug}/design`：从已通过的 SourceMap 创建 Design；
- `POST /api/template-pipeline/{slug}/checks`：按 idempotency key 调度机械检查；
- `GET /api/template-pipeline/jobs/{job_id}`：读取 job 状态和可选完整报告。

API job 仅在本机进程中调度，每个 slug 同时最多一个检查；报告写入
`.artifacts/template_pipeline/jobs/`。它不引入数据库、队列或新的模板真源。

失败报告包含轻量 `repair_findings`：在单次累计检查内归组相同机械问题，保留完整
per-seed 证据，并映射到 TemplateDesign 候选、普通组件函数和代码行。该诊断不恢复
跨迭代 cluster/streak，也不参与模板运行。

现有 legacy 单文件模板可以继续运行，不因新管线强制补齐 `TemplateDesign`
或 `TEMPLATE_DOMAIN`。新建和重做的模板使用新流程。

Strict 模式下 random-16 和 random-36 都使用不低于 0.90 的累计通过率阈值，并且该阈值
不能赦免单个候选：被抽到过却没有任何通过 seed 的候选直接阻断该阶段。Preflight
不构建任何几何，内部区分纯静态的 `contract` 与只做 `config_from_seed`/`resolve_config`
穷尽解析的 `domain_resolution`。Corner 根据 random-36 的
实际 Config 补未出现的 candidate、N min/max，再运行全部 authored risk corners（数值参数
边界现在也归这里）；corner 零失败。最终 36/36 为 `strict_ready`，33–35/36 为
`strict_ready_with_tolerance`。这是当前模板管线的终点；corner report 保留通过与失败证据，
但不再生成后置 receipt、材质物化模型或改写后的 URDF。PBR 材质池及其逐材质物理属性继续
独立维护，后续如何接入由新的方案定义。
