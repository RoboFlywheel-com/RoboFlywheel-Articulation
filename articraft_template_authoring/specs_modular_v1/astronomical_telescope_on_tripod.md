# Astronomical Telescope on Tripod Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `astronomical_telescope_on_tripod` |
| template path | `agent/templates/astronomical_telescope_on_tripod.py` |
| test path (optional) | `tests/agent/test_astronomical_telescope_on_tripod_template.py` |
| stage | `APPROVED` |
| status | `approved` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 34 |
| read_count | 34 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / prompt were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 28 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| tripod + equatorial fork / german RA-DEC | 11 | 三脚架 + 极轴 wedge + RA/DEC 链；含单叉臂 fork 与 polar_assembly + declination_head |
| tripod + alt-az single arm | 8 | 三脚架 + azimuth 转台 + 单臂 altitude bearing + OTA |
| tripod + photo pan-tilt head | 4 | 三脚架 + ball/socket pan head + tilt head + scope（FIXED 安装） |
| tripod + complex focuser chain | 4 | 在 equatorial/altaz 基础上增加 prismatic drawtube + focus knob |
| ground pier + parallelogram / az head | 2 | 固定 pier 替代 tripod，仍属观测 mount 族 |
| tabletop dobsonian | 2 | tabletop_disc + rocker_box + reflector（无 tripod，类别边缘） |
| binocular / misc mount naming | 3 | yoke_mount + binocular、tube_cradle 等，运动链仍是 altaz |

被采纳样本逐条标注：
- `rec_astronomical_telescope_on_tripod_0104cd9f066948909101400e0dee1324` — adopted：canonical equatorial fork on tripod；wedge + polar + RA + DEC + focus knob。
- `rec_astronomical_telescope_on_tripod_0003` — adopted：tripod + polar_assembly + declination_head + Newtonian mesh OTA；3 主关节 + tube_mount。
- `rec_astronomical_telescope_on_tripod_04695a93a8c248a582795380914fcc75` — adopted：spline-leg tripod + altaz mount_arm + refractor OTA；2-DOF az/alt。
- `rec_astronomical_telescope_on_tripod_89eee28637f34b68b433a17f4ced937f` — adopted：tripod + pan_head + tilt_head + annular refractor scope；photo pan-tilt 链。
- `rec_astronomical_telescope_on_tripod_09d7172669da4ae0951dc829664ce408` — adopted：tabletop dobsonian；azimuth + altitude，无 tripod（edge module）。
- `rec_astronomical_telescope_on_tripod_324ff74804384505b720dfc22f154c5b` — adopted：tripod + RA saddle + OTA + prismatic focuser/drawtube/focus_knob 链。
- Remaining 28 samples — read but not adopted：同一 mount 族内的 axis 符号、配色、finder scope、counterweight、scale plate 等装饰/尺度变体，已被上述模块覆盖。

## 核心身份

带三脚架（或等效 grounded support）的天文望远镜：必须有可指向天空的光学筒（OTA）和至少两级指向关节（典型 az+alt、pan+tilt、或 polar+RA+DEC）。默认成熟域是 **tripod-mounted equatorial fork or alt-az refractor**：root 为三脚架 hub，中间为 mount head（equatorial 或 altaz），末端为 optical tube assembly。可选 focus knob / drawtube focuser，但不得缺少 OTA 与 mount 指向语义。

边界：
- 不包括无 OTA 的纯三脚架或 pier。
- 不混入 binocular-only 或 camera pan-tilt head 无 telescope tube 的样本作为默认域（可作为 edge module，默认 seed domain 不采样）。
- 不混入 dobsonian 作为默认 anchor；tabletop dob 仅作 root_support 边缘候选。
- 不混入 parabolic_dish / CCTV head：身份件必须是 astronomical OTA（objective/corrector/mirror cell）。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_astronomical_telescope_on_tripod_0104cd9f066948909101400e0dee1324` | `data/records/rec_astronomical_telescope_on_tripod_0104cd9f066948909101400e0dee1324/revisions/rev_000001/model.py:L21-L44,L58-L131,L133-L157,L159-L189,L191-L260,L262-L268,L270-L305` | equatorial fork：tripod+wedge helpers、polar_head、fork_arm、SCT annular OTA、focus_knob、polar/RA/DEC/focus joints |
| S2 | `rec_astronomical_telescope_on_tripod_0003` | `data/records/rec_astronomical_telescope_on_tripod_0003/revisions/rev_000001/model.py:L34-L147,L177-L248,L250-L297,L299-L388,L390-L500,L502-L527` | german-style EQ：mesh annular helpers、tripod、polar_assembly、declination_head、Newtonian OTA、3 articulations |
| S3 | `rec_astronomical_telescope_on_tripod_04695a93a8c248a582795380914fcc75` | `data/records/rec_astronomical_telescope_on_tripod_04695a93a8c248a582795380914fcc75/revisions/rev_000001/model.py:L42-L116,L118-L165,L167-L232,L234-L258` | altaz：spline-leg tripod_base、mount_arm、refractor telescope、az+alt joints |
| S4 | `rec_astronomical_telescope_on_tripod_89eee28637f34b68b433a17f4ced937f` | `data/records/rec_astronomical_telescope_on_tripod_89eee28637f34b68b433a17f4ced937f/revisions/rev_000001/model.py:L21-L60,L72-L129,L131-L172,L174-L216,L218-L280,L282-L306` | photo pan-tilt：tripod、pan_head、tilt_head、annular scope、pan+tilt+fixed mount |
| S5 | `rec_astronomical_telescope_on_tripod_09d7172669da4ae0951dc829664ce408` | `data/records/rec_astronomical_telescope_on_tripod_09d7172669da4ae0951dc829664ce408/revisions/rev_000001/model.py:L19-L36,L55-L73,L75-L117,L119-L213,L215-L232` | dobsonian edge：tabletop_disc、rocker_box、reflector_tube、az+alt |
| S6 | `rec_astronomical_telescope_on_tripod_324ff74804384505b720dfc22f154c5b` | `data/records/rec_astronomical_telescope_on_tripod_324ff74804384505b720dfc22f154c5b/revisions/rev_000001/model.py:L17-L55,L75-L125,L126-L157,L158-L213,L214-L270,L271-L366,L368-L416` | complex focuser：tripod、ra_axis、saddle、OTA、dovetail focuser chain、6 joints |

## 槽位 + 候选模块表

### Slot A：root_support

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `tripod_wedge_spreader` | S1 | `model.py:L58-L131` | **yes** | 中心柱 + 三腿 + spreader + wedge plate，顶部 polar seat |
| `tripod_spline_legs` | S3 | `model.py:L42-L116` | | tube_from_spline 三腿 + spreader hub + foot pads |
| `tripod_crown_head` | S2 | `model.py:L177-L248` | | 较高 crown/head + latitude seat，heavy equatorial tripod |
| `tabletop_dob_base` | S5 | `model.py:L55-L73` | | 圆形 tabletop_disc，无腿（edge；默认 seed domain 禁用） |

### Slot B：mount_head

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `equatorial_fork` | S1 | `model.py:L133-L189,L270-L296` | **yes** | polar_head + single fork_arm；polar(Y) + RA(Z) + DEC(-Y) |
| `german_ra_dec` | S2 | `model.py:L250-L297,L502-L520` | | polar_assembly + declination_head；tilted polar axis + DEC |
| `altaz_single_arm` | S3 | `model.py:L118-L165,L234-L258` | | azimuth drum + upright arm + alt bearing housing |
| `photo_pan_tilt` | S4 | `model.py:L131-L216,L282-L306` | | pan_head socket + tilt_head ball；pan(Z) + tilt(-Y) |

### Slot C：optical_assembly

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `sct_annular_ota` | S1 | `model.py:L191-L260` | **yes** | annular mesh tube shell + corrector + rear cell + finder |
| `newtonian_reflector_ota` | S2 | `model.py:L390-L500` | | mesh tube + mirror cell + spider + eyepiece focus |
| `refractor_altaz_ota` | S3 | `model.py:L167-L232` | | gold main tube + etalon + focuser black cell |
| `photo_refractor_scope` | S4 | `model.py:L218-L280` | | annular X tube + dew shield + dovetail foot + diagonal |

### Slot D：focus_auxiliary

| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `none` | S3/S4 | n/a | **yes** | OTA 自带 focus ring 或无独立 focus part |
| `focus_knob_continuous` | S1 | `model.py:L262-L268,L297-L305` | | 独立 focus_knob part + CONTINUOUS joint |
| `drawtube_focuser_chain` | S6 | `model.py:L271-L416` | | focuser_body + drawtube + focus_knob；2× PRISMATIC + pinion |

## 槽位图（slot graph）

pattern = `mixed`（linear_chain + optional side branch）

```
[Slot A root_support]
      -- mount interface (polar seat / az bearing / pan top plate) -->
[Slot B mount_head]
      -- declination / altitude / tilt interface -->
[Slot C optical_assembly]
      -- (optional) focus interface -->
[Slot D focus_auxiliary]
```

主约束基准：tripod hub 顶面 Z、mount RA/pan 竖轴、DEC/alt/tilt 水平 trunnion 线。OTA 长度、trunnion 间距、saddle clamp 必须从 mount 基准派生，禁止 OTA 与 fork tip 悬空。

## 部件（Parts）

### Slot A / tripod_wedge_spreader
| part | visual_count | 描述 | 来源 |
| `tripod` | ~12 | center_column、legs、foot pads、wedge plate/cheeks | S1 L58-L131 |

### Slot B / equatorial_fork
| part | visual_count | 描述 | 来源 |
| `polar_head` | ~4 | ra_bearing、tilt_base、latitude hinge bar | S1 L133-L157 |
| `fork_arm` | ~5 | single fork arm + declination cap/boss | S1 L159-L189 |

### Slot C / sct_annular_ota
| part | visual_count | 描述 | 来源 |
| `optical_tube` | ~10 | tube shell、corrector、rear cell、finder | S1 L191-L260 |

### Slot D / focus_knob_continuous
| part | visual_count | 描述 | 来源 |
| `focus_knob` | 1 | knob cap on rear focus socket | S1 L262-L268 |

## 关节（Joints）

| 关节 | 类型 | parent | child | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `polar_angle` | REVOLUTE | tripod | polar_head | (0,1,0) | ~[-0.22,0.30] | wedge 纬度角 | S1 |
| `right_ascension` | CONTINUOUS | polar_head | fork_arm | (0,0,1) | full | RA 跟踪 | S1 |
| `declination` | REVOLUTE | fork_arm | optical_tube | (0,-1,0) | ~[-0.75,1.15] | DEC 俯仰 | S1 |
| `focus` | CONTINUOUS | optical_tube | focus_knob | (1,0,0) | full | 调焦 | S1 |
| `tripod_to_mount` | CONTINUOUS/REVOLUTE | tripod_base | mount_arm | (0,0,1) | full/limited | azimuth | S3 |
| `mount_to_telescope` | REVOLUTE | mount_arm | telescope | (1,0,0) | alt range | altitude | S3 |
| `pan_bearing` | CONTINUOUS | tripod | pan_head | (0,0,1) | full | photo pan | S4 |
| `tilt_axis` | REVOLUTE | pan_head | tilt_head | (0,-1,0) | ~[-0.55,0.80] | photo tilt | S4 |
| `drawtube_slide` | PRISMATIC | focuser_body | drawtube | (1,0,0) | stroke | rack focuser | S6 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `mount_family` | enum | `equatorial_fork` / `german_eq` / `altaz` / `photo_pan_tilt` | `equatorial_fork` | 决定 Slot B 模块与 joint 链 | S1-S4 |
| `root_support_style` | enum | `tripod_wedge` / `tripod_spline` / `tripod_crown` / `tabletop_dob` | `tripod_wedge` | `tabletop_dob` 仅 edge seed | S1,S3,S5 |
| `ota_style` | enum | `sct_compact` / `newtonian` / `refractor` / `photo_refractor` | derived | 与 mount_family 兼容矩阵 | S1-S4 |
| `tripod_height` | float | 0.45–1.10 | sampled | 约束 leg length、hub Z | S1,S3 |
| `tripod_spread_radius` | float | 0.35–0.65 | sampled | foot radius | S1,S3 |
| `polar_wedge_tilt_deg` | float | 20–62 | 35 | equatorial 0 位 wedge 角 | S1,S2 |
| `ota_length` | float | 0.28–0.95 | sampled | 派生 tube mesh、DEC moment arm | S1-S4 |
| `ota_outer_radius` | float | 0.04–0.14 | sampled | annular shell 内外径 | S1,S4 |
| `focus_aux_style` | enum | `none` / `knob` / `drawtube_chain` | `knob` for eq fork | 启用 Slot D | S1,S6 |

## Multiplicity / Copy Logic

- 无模板级 `*_count` 随机采样。
- tripod 三腿、finder bracket 等为 module-local 固定循环（`leg_i`、`foot_pad_i`），不暴露为模板 count 参数。
- `tabletop_dob` 模块无 tripod leg 复制逻辑。

## 拓扑多样性审计

总组合数：4 × 4 × 4 × 3 = **192**（若禁用 `tabletop_dob` 则 root 候选有效为 3 → 144）


| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---:|---|---|
| root_support | 4 | yes | dob 为 edge |
| mount_head | 4 | yes | |
| optical_assembly | 4 | yes | |
| focus_auxiliary | 3 | yes | |

## 部件多样性审计（Part Diversity Audit）

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| root support | yes | no | yes | `root_support_style` | tripod vs tabletop 拓扑不同 |
| mount head | yes | no | yes | `mount_family` | EQ vs altaz vs pan-tilt joint 链互斥 |
| OTA profile | yes | partial | yes | `ota_style` | SCT/Newt/refractor part 树不同 |
| focus mechanism | yes | no | yes | `focus_aux_style` | 无/knob/drawtube 链 |
| finder / counterweight | partial | yes | no | n/a | 装饰，baked visuals |

## Validator（author_run_tests 必须覆盖的点）

- seed=0 anchor 复现 S1 equatorial fork 拓扑：5 parts、4 articulations（含 focus）。
- polar/RA/DEC 关节 type 与 axis 语义正确；positive DEC 抬高 tube nose。
- altaz 模块：positive alt 抬高 objective；az 旋转改变 tube XY。
- pan-tilt 模块：tilt 抬高 front_lens；pan 改变 scope XY。
- tripod feet 接触 ground plane（z≈0）；OTA trunnion 与 fork tip / saddle 接触。
- `tabletop_dob` 仅在显式 edge seed 启用；默认 seed domain 不采样。

## Reject cases（必须能识别并拒绝）

- 无 OTA 或 OTA 为 FIXED 且无 pointable mount DOF（纯装饰望远镜）。
- mount 链少于 2 个独立 pointing DOF（除 focus 外）。
- dob base 与 equatorial fork 模块非法组合（互斥 root+mount 矩阵）。
- DEC/alt joint axis 与 tube 长轴平行（语义错误）。

## 与相邻类别的边界

- 不该混入：`parabolic_dish_on_azimuth_elevation_mount`（射电/卫星 dish，非 OTA）。
- 不该混入：pan-tilt 相机/监控云台（camera barrel 非 astronomical OTA）。
- 不该混入：`binocular` 类别（双筒无 astronomical single OTA 语义；edge module only）。
- 不该混入：`camera_lens` / `camcorder`（消费光学，无 equatorial wedge）。

## 模板实现备注（可选）

- 类别过宽：实现阶段建议 `config_from_seed` 默认只采样 `{tripod_wedge + equatorial_fork + sct}` 与 `{tripod_spline + altaz + refractor}` 两个稳定子域；全 192 组合需 reviewer 扩域。
- pan-tilt 模块中 ball/socket 预期 overlap，需 `allow_overlap`（参考 S4 tests）。
- S1 annular mesh 与 S2 custom mesh 可共享 `_annular_cylinder_mesh` helper，但须保留 `# adopted: Sxx`。
- 若 QC 无法同时覆盖 EQ 与 altaz 全组合，应拆分 slug（如 `astronomical_telescope_equatorial` / `_altaz`）而非硬塞单模板。
