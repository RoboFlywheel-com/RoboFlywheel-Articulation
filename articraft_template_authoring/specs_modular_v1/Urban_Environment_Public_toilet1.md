# Furnished Public Toilet Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `furnished_public_toilet` |
| template path | `agent/templates/Urban_Environment_Public_toilet1.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `composite`(复用 `public_toilet` 外壳 + `toilet` 洁具,组合成连排带洁具的公厕) |

## 核心身份
A public-toilet cabin block where **each stall contains a full ceramic toilet fixture**. It is the composition of the two existing templates:
- `public_toilet` → 连排隔间外壳(floor/walls/roof/utility)+ 每间一扇外开门(REVOLUTE 竖铰链);
- `toilet` → 每间内放一个陶瓷洁具(bowl/tank + 座圈/盖 + 冲水五金),**FIXED 螺栓固定在隔间地板上、面朝门**。

复用方式(不重写几何):
- `public_toilet.build_public_toilet(shell_cfg)` 出 block + N 门;
- `toilet.build_toilet_fixture(model, tcfg, prefix=f"c{i}_", mount_parent=block, mount_origin=...)` 把第 i 个洁具(带前缀)建进同一模型并 FIXED 挂到 block。
> 为支持「一个模型里 N 个洁具」,`toilet.py` 的 `_build_body/_build_seat/_build_flush` 加了 `prefix=""` 形参(零件/关节/材质名加前缀);`prefix=""` 时 standalone toilet 行为不变(已回归验证)。

## 槽位 + 候选
| slot | 来源 | 候选 |
|---|---|---|
| roof / walls / utility / door | public_toilet | 4 / 3 / 3 / 2 |
| **stalls**(多重性,每间一门一洁具) | public_toilet | `1..3` |
| 每间洁具 body / flush / seat / palette | toilet(每间独立 seed → 不同变体) | 3 / 3 / 2 / 9 |
外加外壳 footprint `width_scale`(1.08–1.40,放大以容纳洁具)/ `height_scale`,每间洁具 footprint 受夹 `width_scale≤1.05` 保证不蹭墙。

## 布局约定(米,Z-up)
- 隔间沿 +Y 平铺,第 i 间中心 `cy = i*d`;门在各间 +X 面。
- 洁具水箱贴**后墙(-X)**、面朝门(+X):`mount_x = -w/2 + 0.465`(随外壳 w 缩放,水箱后沿距后墙 ~3cm);`mount_z = FLOOR_H`(底坐地板面)。

## 槽位图(composite)
```text
[block] (root, all stall shells, grounded)
  ├── cabin_i_to_door  REVOLUTE +Z      --> door_i           (i=0..N-1)
  └── c{i}_mount       FIXED            --> c{i}_body         (toilet bolted to floor)
         ├── c{i}_body_to_seat_ring  REVOLUTE ±Y  --> c{i}_seat_ring
         ├── c{i}_body_to_seat_lid   REVOLUTE ±Y  --> c{i}_seat_lid (if ring_lid)
         └── c{i}_body_to_flush_*    PRISMATIC/REVOLUTE --> c{i}_flush part
```

## 关节
| 关节 | 类型 | 说明 |
|---|---|---|
| `cabin_{i}_to_door` | REVOLUTE +Z | 隔间门(public_toilet 提供) |
| `c{i}_mount` | FIXED | 洁具固定在 block 地板 |
| `c{i}_body_to_seat_ring` / `_seat_lid` | REVOLUTE ±Y | 座圈 / 盖 |
| `c{i}_body_to_flush_*` | PRISMATIC / REVOLUTE | 双键 / 扳手 / 拉杆 |

## 拓扑多样性

## 采样/验收
`config_from_seed`:rng 选外壳各 enum + stalls(1–3)+ 缩放;每间洁具 = `toilet.config_from_seed(seed*1000+i*37)`(夹宽)。`compile-sweep 0-49 --quality-profile final`:**verdict=pass, pass_rate=1.0, diversity=49, failed_gates=None**(已通过)。

## Validator
- block 接地;door 数 == stall 数 == 洁具数;每间洁具 `c{i}_mount` 为 FIXED;座圈为 ±Y REVOLUTE 从 q=0。
- 复刻每间洁具内部 allow_overlap(座圈/盖/五金 vs 其 body),门 vs block,洁具 body vs block(坐地板)。

## Reject
- 洁具浮在隔间外/穿墙、洁具未固定(应 FIXED)、门轴非竖直、洁具尺寸蹭到隔间墙。

## 审核记录
| reviewer | pending(SPEC_ONLY_DRAFT;复用两个已通过模板组合,0–49 全过)|
