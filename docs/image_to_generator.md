# 从参考图构建新的 RFW-A generator

两套旧代码在这里共用一套 SDK、记录存储和构建工具。保留的链路是：
参考图 → 源资产 → 同类变体 → SourceMap → 类别蓝图 → generator → 检查与采样。
图像驱动的源资产生成可使用 provider，也可由外部 agent 完成；蓝图与 generator
仍需 agent 阅读源代码并编写，当前没有一条命令自动调度四个 agent。

以下命令均从本仓库根目录运行。环境准备见 [usage.md](usage.md)。

## 参考图与源资产

把图片放在 `picture/<大类>/<小类>/` 下，例如 `picture/Furniture/Folding chair/ref.png`。
图片与源记录属于数据，不提交 Git。也可用 `scripts/ingest_pictures.py` 从 Markdown
中的图片链接批量导入；用 `--help` 查看选项。

外部 agent 创建记录时先阅读 [EXTERNAL_AGENT_DATA.md](../EXTERNAL_AGENT_DATA.md)，然后执行：

```bash
uv run rfwa source external seed 'Furniture/Folding chair' \
  '根据参考图构建可折叠椅，保留结构与运动关系' \
  --agent codex --image ref.png
```

命令创建草稿，打印 `record_id` 和记录路径；**尚未生成三维模型**。参考图复制进
活动 revision 的 `inputs/`，`picture.json` 保存大类、小类及原图路径。agent 阅读参考图，
在该记录活动 revision 的 `model.py` 编写 SDK 程序，然后运行：

```bash
uv run rfwa source external check rec_example
uv run rfwa source external finalize rec_example
```

也可用 `rfwa source external init '<描述>' --agent codex --picture picture/<大类>/<小类>/<图片>`。
文本输入的 `external init` 继续支持不带图片。若使用 provider 直接从图合成资产，
参阅 `uv run rfwa source generate --help` 的 `--image` 参数；当图片位于上述规范目录时，
同样自动保存分类绑定。

## 同类变体

```bash
uv run rfwa source external fork rec_example \
  '增大座面宽度，改变腿部结构，保留折叠功能' --agent codex
```

fork 保留父记录，创建子记录并继承图片分类；父图像输入通过 revision 的
`inherited_inputs` 引用保留。agent 编辑命令打印的子记录 `model=` 路径，再 check/finalize。
seed 与变体都进入同一小类的来源池。不要求先凑满固定数量的变体。

从旧 workspace 搬入已有资产时：

```bash
uv run rfwa import-source --from-repo /path/to/source-checkout rec_example
```

导入保留评分、revision 与图片绑定，并复制绑定指向的参考图。源图缺失时仍导入记录，
在导入回执记录缺失；目标已有不同内容的同名图片时提示冲突。不会整库搬运图片与资产。

## 来源池、蓝图与 generator

```bash
uv run rfwa author source-map-init folding_chair \
  --records-root data/records \
  --picture-category Furniture --picture-subcategory 'Folding chair'
```

新建 seed、fork、导入后会刷新小类索引。SourceMap 以当前记录和分类绑定为准，
缓存索引未及时刷新也不会漏掉新增或恢复归档的来源。
阅读来源代码，填写 SourceMap 的审阅结果与可复用组件代码位置，再执行：

```bash
uv run rfwa author design-init folding_chair \
  --source-map articraft_template_authoring/source_maps/folding_chair.md \
  --records-root data/records
```

补全蓝图参数、组件替换、接口与关节规则，然后在 `agent/templates/` 编写并注册 generator。
具体接口见 [generator_construction.md](generator_construction.md)。SourceMap 审阅用于准确记录
代码来源，不设置固定的来源数量或变体数量门槛。

```bash
uv run rfwa check folding_chair --stage random-16
uv run rfwa sample folding_chair --seeds 0-19 --out /tmp/folding_chair
```

默认检查采用可配置的 90% 通过率，采样输出通过的资产并记录失败 seed。
已有 generator 的蓝图不完整、个别边界情况失败会保留为修复信息，默认不阻断全部产出。
`--strict` 仅用于需要完整来源与全案例通过的额外检查。

`uv run python scripts/picture_doctor.py` 可检查图像绑定；它是独立诊断工具，
不会作为普通采样的自动门禁。
