# Specific Editing

`specific_editing` 用于论文中的**定向 3D 编辑可视化**：从结构化 articulated generator
生成一个基准模型，只改变指定部位或指定参数，再以一致视角输出可直接比较的图片和 3D 文件。

这里的目标是展示“结构可编辑性”，不是做仿真实验。管线只执行配置解析、模型构建、视觉导出和
渲染，不运行物理仿真、碰撞检测、关节扫掠或复杂 QC。

## 四类编辑

| `kind` | 展示内容 | 典型例子 |
|---|---|---|
| `component` | 替换指定结构模块 | 平板门换成藤编门、叶片轮廓替换、转子模块替换 |
| `count` | 改变重复部件数量 | 抽屉数、柜门数、风扇或风机叶片数 |
| `material` | 只替换指定 surface 的视觉材质 | 门板木材换铝、红色烤漆或半透明玻璃 |
| `size` | 调整指定尺寸并让依赖几何同步重算 | 柜体宽度、铰链高度、叶片跨度 |

同一个 spec 中，每个 `values` 条目都是相对同一份 `base_config` 的独立编辑，不做多个编辑轴的
笛卡尔积。因此变体数是所有 `edits[*].values` 长度之和，适合制作 one-edit-at-a-time 论文对比图。

## 精选 Generator

这些文件是从 `agent/templates/` 复制出的任务内快照；定向改造不会修改生产模板。

| ID | 对象 | component 字段 | count 字段 | size 字段 | 常用材质目标 |
|---|---|---|---|---|---|
| `hinge` | 单自由度铰链 | `hinge_line_style` | `knuckle_count` | `leaf_height` | `moving_half`、`hinge_line`、`all_surfaces` |
| `cabinet` | 侧铰门柜 | `door_kind` | `door_count` | `carcass_width_m` | `door`、`carcass`、`all_surfaces` |
| `drawers` | 滑动抽屉柜 | `drawer_front` | `drawer_count` | `carcass_width_m` | `drawer_front`、`drawer`、`all_surfaces` |
| `fan` | 吊扇 | `blade_shape` | `blade_count` | `blade_span` | `blade`、`all_surfaces` |
| `turbine` | 风力机 | `rotor_module` | `blade_count` | `blade_span` | `rotor`、`blade`、`all_surfaces` |
| `parabolic_dish_on_azimuth_elevation_mount` | 方位/俯仰抛物面天线安装架 | `reflector_style` | `support_leg_count`、`feed_strut_count` | `dish_radius` | `reflector_surface`、`dish_reflector`、`all_surfaces` |
| `ferris_wheel` | 摩天轮 | `gondola_style` | `num_gondolas` | `rim_radius` | `gondola_body`、`gondola`、`all_surfaces` |
| `table_football` | 桌上足球 | `leg_form` | `rod_count` | `cabinet_length_scale` | `pitch`、`cabinet`、`all_surfaces` |
| `playground_chair_swing_carousel` | 旋转飞椅 | `seat_type_module` | `seat_count` | `seat_radius_scale` | `seat_surfaces`、`chairs`、`all_surfaces` |
| `fence` | 铰接级联围栏 | `panel_style` | `panel_count` | `panel_len_scale` | `panel_infill`、`panels`、`all_surfaces` |
| `playground_swing` | 游乐场秋千 | `seat_type` | `swing_count` | `frame_scale` | `seat_surface`、`swing`、`all_surfaces` |
| `monitor_mount` | 多段显示器墙装支臂 | `wall_style` | `arm_segment_count` | `arm_span` | `arm_links`、`wall_mount`、`all_surfaces` |

`--describe-generator <ID>` 会输出该 generator 的合法字段、推荐值、方向和源文件哈希。仓库已提供：

- `specs/single_variable/cabinet_paper_showcase.json`：部件、数量、局部材质和尺寸四类编辑；
- `specs/single_variable/drawer_count.json`：抽屉数量及 closed/open 对比；
- `specs/single_variable/turbine_blade_count.json`：转子叶片数量对比。
- `specs/single_variable/parabolic_dish_on_azimuth_elevation_mount.json`：反射面部件、三/四支撑腿、二/三/四馈源支杆、反射面局部材质和口径尺寸；两个 count 目标分别输出到 `comparisons/count` 与 `comparisons/count_1`。
- `specs/single_variable/ferris_wheel.json`：座舱模块、座舱数量、座舱局部材质和轮缘半径；
- `specs/single_variable/table_football.json`：支撑腿模块、球杆数量、球场局部材质和柜体长度；
- `specs/single_variable/playground_chair_swing_carousel.json`：座椅模块、座椅数量、座椅局部材质和悬挂半径；
- `specs/single_variable/fence.json`：围挡模块、围栏段数、填充局部材质和单段长度；
- `specs/single_variable/playground_swing.json`：座椅模块、秋千数量、座椅局部材质和框架尺度。
- `specs/single_variable/monitor_mount.json`：墙装模块、2/5/20 段串联支臂、支臂局部材质和整体臂展。

两份卫星 source 均是对应 `agent/templates/` 文件的任务内快照。Astronomy 快照仅去掉一处无行为
影响的冗余 f-string；铰接太阳翼快照把原本埋入背板的 6 mm 电池片抬到背板外 1 mm，修正负 Y
镜像翼的电池面方向，并将前表面整理为每个结构段一块 PBR 电池板，段间增加前向银色分隔条。这样
两翼/四翼布局、局部材质与 1/2/3/4 段数量在前视渲染中都真实可见。四翼布局沿用 generator 的
兼容规则，在 +X/-X 翼根使用 `sensor_mast_cluster`，避免载荷与交叉翼根重叠。生产 generator 保持不变，也没有增加
仿真或复杂 QC；如后续论文版式需要
更夸张的形态差异，只在
`specific_editing/generators/source/` 的快照和 catalog 适配层中调整。新增的摩天轮、桌上足球、
旋转飞椅、围栏和秋千也遵循相同边界；其中快照只为论文图补足可控参数、目标 surface 和更清楚的
结构差异，生产 generator 保持不变。

`monitor_mount` 的生产模板忠实保持来源资产的固定两段 `primary_arm + secondary_arm`。展示快照
将中间支臂抽象为带稳定编号的可重复 link，并为每一段发出真实串联 REVOLUTE 关节，从而能在同一
对比图中展示 2、5、20 段。20 段采用轻微规则折线并按平方根缩放单段长度，既保留明显的数量差异，
又避免长直链让 2 段版本在共享画幅中缩成小点；这只是论文可视化适配，不回写生产模板，也不增加
运动包络或物理核验。

## 快速开始

在 `arti-template` 仓库根目录运行。以下三个命令分别用于查看能力、只校验计划和正式生成：

```bash
.venv/bin/python -m specific_editing.pipeline --describe-generator cabinet
```

```bash
.venv/bin/python -m specific_editing.pipeline \
  --spec specific_editing/specs/single_variable/cabinet_paper_showcase.json \
  --dry-run
```

```bash
.venv/bin/python -m specific_editing.pipeline \
  --spec specific_editing/specs/single_variable/cabinet_paper_showcase.json \
  --out specific_editing/outputs/single_variable
```

第三个命令的实际结果目录是
`specific_editing/outputs/single_variable/cabinet_paper_showcase/`。`--out` 是批次根目录，spec 的
`name` 会自动成为下一层目录名。仓库中的展示 spec 已按此方式生成在
`specific_editing/outputs/single_variable/` 下。

## 目录结构

代码、配置与生成结果分离，生成结果按**编辑变量数**组织：

```text
specific_editing/
  pipeline.py render.py export.py selectors.py blender_worker.py pbr_materials.py
  generators/            # 精选 generator 快照与 catalog 适配层
  specs/
    single_variable/     # 现有 one-edit-at-a-time 展示 spec
    bivariate/           # 预留：双变量编辑 spec（两个编辑轴的组合）
  outputs/
    single_variable/     # 现有 spec 的生成结果，每个 spec name 一个目录
    bivariate/           # 预留：双变量编辑生成结果
  tests/
  paper_figures/         # 论文图合成结果
  reference/             # 论文图参考素材
  archive/               # 不属于当前管线的历史打包件
```

当前所有 spec 都是**单变量编辑**：每个 `values` 条目相对同一份 `base_config` 独立变化，
变体数是各 `edits[*].values` 长度之和，对比图因此严格 one-edit-at-a-time（见“四类编辑”）。
后续加入**双变量编辑**时在 `specs/bivariate/` 新增 spec，管线输出到 `outputs/bivariate/`；
单变量结果与论文图脚本的默认路径不受影响。

## JSON Spec

下面的精简示例同时展示四种编辑。实际可直接参考
[`cabinet_paper_showcase.json`](specs/single_variable/cabinet_paper_showcase.json)。

```json
{
  "schema_version": 1,
  "name": "cabinet_edit_demo",
  "generator": "cabinet",
  "seed": null,
  "base_config": {
    "body_form": "rect_box",
    "door_kind": "flush_slab",
    "door_mechanism": "revolute_swing",
    "door_count": 2,
    "carcass_width_m": 1.0,
    "palette": 1
  },
  "edits": [
    {
      "kind": "component",
      "target": "door_kind",
      "label": "Door module",
      "values": ["flush_slab", "framed_cane"]
    },
    {
      "kind": "count",
      "target": "door_count",
      "label": "Door count",
      "values": [1, 2, 4]
    },
    {
      "kind": "material",
      "target": "door",
      "label": "Door material",
      "values": [
        {
          "name": "walnut veneer",
          "rgba": [0.29, 0.12, 0.055, 1.0],
          "metallic": 0.0,
          "roughness": 0.42
        },
        {
          "name": "brushed aluminum",
          "rgba": [0.63, 0.67, 0.71, 1.0],
          "metallic": 0.86,
          "roughness": 0.24
        }
      ]
    },
    {
      "kind": "size",
      "target": "carcass_width_m",
      "label": "Cabinet width",
      "values": [0.78, 1.0, 1.26],
      "highlight_parts": ["*carcass*"]
    }
  ],
  "render": {
    "backend": "blender",
    "views": ["front_iso"],
    "poses": ["closed"],
    "image_size": [1600, 1120],
    "supersample": 1,
    "shadow_strength": 0.6
  }
}
```

字段约定：

- `schema_version`：当前固定为 `1`。
- `name`：实验名，也是输出子目录名。
- `generator`：上表中的 ID；也接受对应模板长名别名。
- `seed`：可选整数；省略或设为 `null` 时从 generator 默认 config 开始。
- `base_config`：所有变体共享的基准配置。建议显式锁定论文中不希望变化的外观和结构项。
- `edits`：非空数组；`kind` 只能是 `component`、`count`、`material` 或 `size`。
- `target`：非材质编辑必须是 generator 为该 kind 声明的 config 字段；材质编辑必须是其材质目标名。
- `label`：comparison sheet 中的显示前缀；省略时使用 `target`。
- 同一 `kind` 下若有多个 `target`，comparison 目录按 target 稳定编号：第一个使用原名，后续依次为
  `<kind>_1`、`<kind>_2`；例如本卫星的分段数量在 `comparisons/count`，翼数量/布局在
  `comparisons/count_1`，不会覆盖已有对比图。
- `highlight_parts`：可选 surface selector 列表。仅在显式填写时，目标保持原颜色、非目标部件会被
  轻微弱化；未填写时所有未编辑部位保持与 base 完全一致的 PBR 外观。字段名为兼容既有 spec 保留。
- `values`：非材质编辑直接给配置值；材质编辑中的每项必须是对象，并包含 3 或 4 通道的
  `rgba`。建议提供 `name` 和统一材质库中的精确 `material_id`；`rgba`、`metallic`、`roughness`、
  `transmission`、`ior` 作为快速预览及无纹理回退，并可提供二选一的 `parts` 或 `surfaces`。

surface selector 默认不区分大小写；无前缀时兼容旧版，会同时搜索 part、visual、builder 和材质类别。
需要精确控制时可使用 `part:`、`visual:`、`surface:`、`builder:`、`class:`，例如
`surface:door_kind__*__door_leaf_*/door_kind__*__door_slab`。`parts` 是 part glob 的简写；catalog 的
默认材质目标已细化到门板、抽屉面板、扇叶表面和 `blade_shell`，不会顺带替换同一 part 内的把手、
托盘、轮毂或叶根五金。每个实际命中项以稳定的 `part/visual` key 写入 `edit_metadata.json`。

解析时会检查编辑字段是否属于 generator 的公开轴，并确认请求值没有被 `resolve_config` 静默
clamp 成另一个值。

## 渲染与共享尺度

未写 `render` 时使用以下默认值：

```json
{
  "backend": "blender",
  "views": ["front_iso"],
  "poses": ["closed"],
  "image_size": [720, 560]
}
```

- `blender` 是默认及正式论文渲染后端，使用 Blender 4.2.21 LTS 的 Cycles GPU；优先使用 OptiX，
  不可用时回退 CUDA。默认可执行文件为
  `/tmp/blender-4.2.21-linux-x64/blender`；需要使用其他安装位置时设置
  `SPECIFIC_EDITING_BLENDER=/path/to/blender`。
- `software` 仅用于快速开发测试，使用 numpy/trimesh/Pillow，无需 Blender、GPU 或 DISPLAY；其
  材质效果是轻量近似，不作为最终论文图的渲染结果。
- 常用 view 包括 `front`、`side`、`rear`、`top`、`front_iso` 和 `rear_iso`。仓库中的正式展示 spec
  统一使用 `front_iso`：物体正面朝画面右侧，相机位于物体左前方并轻微俯视；纯侧视只保留为
  调试能力。
- pose 可用 `closed`/`rest`、`mid`、`open`。图片 key 和文件名为 `<pose>__<view>`。
- `image_size` 是 `[width, height]`，两个值都必须至少为 128。
- `supersample` 是 1 到 4 的整数；正式高清资产可直接使用较大的 `image_size` 和 `1`，避免先以
  更高分辨率渲染再缩回低分辨率文件。
- `shadow_strength` 是 0 到 1 的数值，只控制 Cycles Shadow Catcher 合成到白底上的强度；论文展示
  资产统一使用 `0.6`，保留接触关系但避免阴影抢过物体本身。
- `frame_scope` 默认为 `global`，即整份 spec 共用一个世界空间 frame；当某一编辑轴包含极端长宽
  变体、会让其他编辑轴过度缩小时，可设为 `edit_group`，让每个 `kind + target` 比较组独立共享
  frame。组内仍严格保持真实相对尺度，不会逐个变体自动放大。
- `compact_comparison_kinds` 可列出需要紧凑排版的编辑类型（例如 `["count"]`）。它只在 comparison
  sheet 中裁去各格白边、将真实前景居中到标签上方并统一阴影基线；所有前景使用同一个缩放比例，
  不改变尺寸和单节长度的视觉可比性。
- `normalize_comparison_foreground` 默认为 `false`。设为 `true` 时，仅对启用紧凑排版的 comparison
  sheet 按每格前景独立放大，适合 2 段与 10 段这类跨度很大的数量对比；它只影响对比表排版，不改变
  单模型渲染图或模型几何。

正式 Blender 图使用固定的棚拍配置：60 mm 轻微透视相机、固定语义朝向、三点面积光、纯白
`#FFFFFF` 背景、Cycles Shadow Catcher 软阴影和小尺度边缘倒角。地面为无发光的哑光接影面，
不存在程序化椭圆或伪接触阴影。管线分别渲染有物体和无物体的 Shadow Catcher pass，用两者的
逐像素比值按 `shadow_strength` 合成真实灯光阴影到纯白背景，再叠加透明前景；因此远处背景保持精确白色，
同时物体仍有接触处较深、紧贴物体并柔和扩散的自然落地阴影。只有较高的主面积光参与接影，补光
和轮廓光只负责材质塑形，避免多个阴影叠成扇形。相机、灯光比例及世界空间 frame 在全局或同一
编辑比较组的 base 与变体之间保持一致；不会为单个变体重新找角度或自动放大，因此结构和尺寸
变化可直接比较。

默认情况下，同一 spec 的 base、所有变体和所需姿态使用一个世界空间共享 AABB；`edit_group`
模式则为每个编辑轴建立一个包含 base 的共享 AABB。Blender 针对语义视角投影对应共享边界来确定
相机距离，既避免细长物体因球形包围框产生过多留白，也不会对组内单个变体单独放大。因此
0.78 m 与 1.26 m 之类的尺寸变化仍以真实相对比例出现。generator 自带的 `front_axis` 决定语义
前视方向。

## 精选 PBR 主题

正式图不采用 generator 各部位独立随机抽样的材质组合。管线按 generator 的语义材质名应用固定的
人工精选主题，纹理来自 `pbr_material_library/unified/latest.json`，并按库中的 `tile_size_m` 做米制
cube UV：

| Generator | 固定主题 |
|---|---|
| Cabinet | 浅橡木柜体、深胡桃木暗部、黄铜五金、透明玻璃、米色织物 |
| Drawers | 深胡桃木柜体、黑化金属暗部、黄铜五金、胶合板托盘 |
| Turbine | 暖白涂层塔架/机舱、拉丝银钢件、黑化金属、暖白叶片 |
| Parabolic Dish Mount | 暖白反射面、拉丝银支架、黑化馈源/加强件、黄铜细节、黑色橡胶脚垫 |
| Ferris Wheel | 暖白主轮架、拉丝银副骨架、黑化平台、红色座舱、白色饰边与透明玻璃 |
| Table Football | 胡桃木柜体/支腿、黑化包边、绿色球台毡、拉丝银球杆、红白球员 |
| Chair-swing Carousel | 红色烤漆立柱/旋臂、拉丝银结构、黄铜饰带、橡木座椅、黑化底座 |
| Fence | 黑化钢框和底脚、红色围挡、拉丝银连接件 |
| Playground Swing | 红色烤漆主架、黑化斜撑、拉丝银悬挂件、黑色橡胶座椅及橡木/黄铜细节 |
| Monitor Mount | 黑化墙座/关节、拉丝银重复支臂、黄铜轴销、白色盖板和烟色显示屏 |

匹配优先使用 `visual.material.name`，不只依赖 `material_class_id`，以兼容模板中少量语义正确但类别
标注不准确的 surface。局部材质编辑通过精确 `material_id` 覆盖目标 surface；未命中的柜体、五金
和其他部件仍使用同一固定主题，不会跟随编辑重新抽样。最终选材 receipt 写入 `manifest.json` 的
`pbr_theme`。

## 输出目录

```text
<out>/<spec.name>/
  edit_spec.json
  generator_capabilities.json
  manifest.json
  base/
    assets/meshes/*.{obj,glb}  # generator 产生 mesh 时存在
    model.urdf
    scene.glb
    exports.json
    renders/<pose>__<view>.png
    comparison_renders/<edit-kind>/<pose>__<view>.png  # edit_group 模式下存在
  variants/<variant-id>/
    assets/meshes/*.{obj,glb}  # generator 产生 mesh 时存在
    edit_metadata.json
    model.urdf
    scene.glb
    exports.json
    renders/<pose>__<view>.png
  comparisons/
    <edit-kind>/<pose>__<view>.png
```

`manifest.json` 汇总基准配置、resolved config、每个编辑、目标 part/surface、导出文件和
comparison sheet。
其中也记录全局或各编辑组的共享相机 frame。`edit_metadata.json` 保存单个变体的请求值与最终解析值，便于
论文图追溯。comparison 按 `kind + target` 分组，避免同一编辑类型下不同目标混在同一张图中。

## 3D 导出边界

- `scene.glb`：将默认姿态烘焙成可直接检查的完整视觉场景，保留分 part 节点以及颜色、alpha、
  metallic/roughness 等标准 PBR 外观。额外的 `transmission/ior` 请求保留在编辑元数据中。
- `model.urdf`：保留 part/joint 结构的 **visual-only URDF**，不导出物理 collision；它用于查看和
  交付结构，不是仿真资产契约。
- `exports.json`：明确记录 `purpose: visualization_only` 和 `physics_exported: false`。

本任务不生成 `physics.json`，不估计质量、惯量、摩擦或材料力学参数，也不以碰撞、动力学稳定性
或完整模板 QC 作为通过条件。最终状态是 `build_and_render_only`：能按指定编辑构建、导出并清晰
渲染即可。
