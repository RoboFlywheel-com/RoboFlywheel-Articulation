# Legacy authoring references

这里保留旧模板在历史制作流程中形成的设计说明，目的是在已有模板需要维修或重做时，
能够查到当时的组件划分、参数意图和装配判断。

- `specs_reference_only/`：40 份只具参考价值的早期 spec。
- `specs_transitional/`：11 份过渡期 modular spec。

这些文件不是当前 `SourceMap → TemplateDesign → 单文件模板` 管线的输入，不参与 import、
seed 构建、preflight、random sweep 或 corner 检查。新模板不得在这里新增 spec，模板代码也
不得读取或导入这里的内容。

维护已有模板时，可以先查阅对应旧 spec 理解历史设计意图；如果模板正式进入当前重做流程，
仍应从源资产重新建立 `source_maps/<slug>.md` 和 `designs/<slug>.json`，旧 spec 仅作为辅助证据。
