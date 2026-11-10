# Controlled Morphology

这个目录是“可控变量空间”的任务专用实现。`generators/` 中的文件是从
`agent/templates/` 复制后独立改造的版本；实验和修复只能修改这里的副本，不修改生产模板。

源代码盘点、变量范围、联动约束和后续 generator 候选见
[`CAPABILITY_MATRIX.md`](CAPABILITY_MATRIX.md)。

## 当前范围

- `single_door_cabinet`：一个 `revolute` 侧铰门，可控铰链侧、把手类型、朝向、尺寸、间隙和位置。
- `single_drawer_cabinet`：一个 `prismatic` 抽屉，可控把手类型、朝向、尺寸、间隙和位置。
- `multi_door_cabinet`：1–4 扇侧铰门，输出全部门关节的 `articulations` metadata。
- `multi_drawer_cabinet`：1–6 个抽屉，支持全宽堆叠、成对网格和下宽上双布局。
- `kitchen_cabinet_access`：同一 kitchen host 上配对的单侧铰门 / 单上掀翻板。
- `pipeline.py`：从显式 JSON `Config` 生成 one-axis-at-a-time (OAT) 切片，不调用
  `config_from_seed`。

这里的单变量是“单一上游干预”：由该变量确定性派生出的门板尺寸、搁板宽度、把手绝对位置、
扫掠半径或抽屉实际行程允许同步变化，并会被记录；无关输入和随机性保持锁定。

两份 canonical 能力覆盖规格用于确认 generator 的可控空间：

- `specs/door_p0_space.json`：10 条门柜 P0 轴，共 28 个 OAT cell。
- `specs/drawer_control_space.json`：11 条单抽屉 P0 轴，共 32 个 OAT cell。

P1 不复用 `single_*` 的拓扑契约，而是按研究问题拆成独立规格：

- `door_p1_joint_range.json`、`drawer_p1_joint_range.json`：单目标关节范围。
- `door_p1_part_count.json`：1–4 扇侧铰门及其确定性布局。
- `drawer_p1_part_count.json`：1–6 个全宽、垂直堆叠抽屉。
- `drawer_p1_layout.json`：固定 4 个抽屉，比较全宽堆叠、成对网格和下宽上双布局。
- `cabinet_p1_hinge_axis.json`：同一厨房柜 host 上的垂直侧铰门与水平上翻板。

`single_door_cabinet` 和 `single_drawer_cabinet` 始终保留单活动部件限制；多部件 P1 通过单独的
`multi_door_cabinet`、`multi_drawer_cabinet` registry 入口和 `articulations` metadata 生成；
铰链轴 P1 使用独立的 `kitchen_cabinet_access`，避免改变两个 P0 generator 的任务语义。

## 已生成批次

当前持久资产统一位于 `generated_assets/<原始 generator>/<实验>/<变量>/`：

| 目录 | 变量切片 | 资产数 |
|---|---|---:|
| `pictureX_0611_Cabinet_with_doors/single_door_p0_space_v1` | 单门 P0 形态变量 | 28 |
| `pictureX_0611_kitchen_cabinet/single_drawer_p0_space_v1` | 单抽屉 P0 形态变量 | 32 |
| `pictureX_0611_Cabinet_with_doors/single_door_p1_joint_range_v1` | 门关节范围 | 5 |
| `pictureX_0611_kitchen_cabinet/single_drawer_p1_joint_range_v1` | 抽屉关节范围 | 5 |
| `pictureX_0611_Cabinet_with_doors/multi_door_cabinet_p1_part_count_v1` | 1--4 扇门 | 4 |
| `drawer_cabinet_with_sliding_drawers/multi_drawer_cabinet_p1_part_count_v1` | 1--6 个抽屉 | 6 |
| `drawer_cabinet_with_sliding_drawers/drawer_cabinet_p1_layout_v1` | 三种抽屉布局 | 3 |
| `pictureX_0611_kitchen_cabinet/cabinet_p1_hinge_axis_v1` | 侧铰门 / 上掀翻板 | 2 |

以上 85 个资产均通过默认轻量编译和 URDF / metadata 一致性检查。

## 使用

从 `arti-template` 仓库根目录运行：

```bash
.venv/bin/python -m controlled_morphology.pipeline \
  --spec controlled_morphology/specs/door_p0_space.json \
  --dry-run
```

dry-run 会加载 generator、构造每个 `Config`、执行 `resolve_config`、校验 metadata，并明确输出
`asset_count: 28`，但不创建资产。

查看 generator 自报的机器可读变量范围、单位、有效条件和预期派生结果：

```bash
.venv/bin/python -m controlled_morphology.pipeline \
  --describe-generator single_door_cabinet
```

正常生成资产：

```bash
.venv/bin/python -m controlled_morphology.pipeline \
  --spec controlled_morphology/specs/drawer_control_space.json \
  --out /tmp/controlled_morphology_out
```

`--out` 只指定分类根目录。管线根据 registry 自动追加原始 generator 名，根据 spec 自动追加
实验名，再按 controlled axis 建变量目录；不依赖调用者手工拼接分类路径。

默认流程做 generator 自带测试和基本编译校验，不启动额外仿真或渲染。需要检查完整关节行程时可
额外传入 `--motion-qc`。默认拒绝覆盖已有资产目录；显式传入
`--overwrite` 时，也只会替换当前 spec 精确规划出的 `assets/<变量>/<asset_id>` 目录，不清空
分类根目录。

## Spec 约定

```json
{
  "schema_version": 1,
  "name": "experiment_name",
  "generator": "single_door_cabinet",
  "base_config": {"door_count": 1},
  "axes": [
    {"name": "carcass_width_m", "levels": [0.72, 0.98, 1.42]}
  ],
  "nuisance_blocks": [
    {"id": "canonical", "overrides": {"carcass_depth_m": 0.42}}
  ]
}
```

生成数量为 `sum(axis 的 level 数) * nuisance block 数`。每个资产只应用一个 controlled
axis level；其余差异只来自明确记录的 nuisance block。若 controlled level 被
`resolve_config` clamp 或正规化为不同值，管线会拒绝整个 spec，防止错误实验标签静默进入数据集。

## 输出与复现

```text
<out-base>/
  <upstream-generator>/
    <experiment>/
      manifest.json
      experiment_spec.json
      variable_space.json
      assets/<controlled-variable>/
        l<index>-<actual-level>__<nuisance>__<hash>/
          model.py
          generator.py
          model.urdf
          physics.json
          compile_report.json
          parameters.json
          ... compiler 生成的 mesh/texture 文件
```

每个 `model.py` 只加载同目录的 `generator.py` 快照，并用 JSON 中的显式参数构造
`Config`。因此源码不依赖随机 seed，也不会随仓库里的 generator 后续修改而改变。

`parameters.json` 同时记录 requested/resolved config、base/override/nuisance、受控轴与
level、generator 路径/哈希/版本、原始模板路径/哈希/类别、目标 joint/link/type/axis/limits、opening endpoint、把手
frame、物体 front/up 约定，以及门板或抽屉的关键派生 `morphology`。`resolved_config_sha256`
标识几何等价配置，便于识别不同 OAT 轴共享的 canonical cell。输出根目录还冻结原始 spec 和
generator 的机器可读变量空间。`compile_report.json` 保存基本编译结果；启用 `--motion-qc` 时
也会保存 motion QC。`manifest.json` 汇总每个资产状态、路径和文件哈希。单个资产失败不会中断后续 cell，但命令
最终返回非零。

P2 材质、颜色和纹理永久不进入本项目的变量空间，也不生成 `appearance.json`。管线根据每个
surface 的 `material_class_id` 确定性写出 `physics.json`，包含密度、杨氏模量、泊松比、静/动摩擦
和恢复系数；这些属性不作为形态变量随机化。该步骤不读取或复制 PBR 纹理，URDF 只保留 generator
原有的简单平涂颜色。

## 接入新 Generator

新副本需在 `registry.py` 注册，并公开以下接口：

```python
Config
resolve_config(config)
build_*(config, assets=...)
run_*_tests(object_model, config)
benchmark_metadata(config)
```

`benchmark_metadata` 至少返回 `target_joint`、`target_link`、`joint_type`、`axis`、`limits`、
`opening_sign`、`opening_endpoint`、`handle_frame`、`front_axis` 和 `up_axis`。管线会把这些值与
最终 URDF 的 target joint/link/type/axis/limits 交叉校验。
