# plank_ring_door — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `plank_ring_door` |
| template path | `agent/templates/Door_wooden_plank_door_with_a_ring_pull.py` |
| test path | `tests/agent/test_plank_ring_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（leaf-to-jamb hinge 主 spine + plank/stud multiplicity + 可替换 bracing/top/hardware slots） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 15 |
| read_count | 15 |
| read_scope | all 5-star samples in this category：2 parents + 13 variants（含 4 个 gap-fill 变体），`model.py` 全量逐行读取 |
| samples_adopted_as_module_sources | 14 |
| samples_read_but_not_adopted | 1（`rec_plank_ringpull_door_var_thumb_latch`：移除挂环，出本小类身份）|
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构观察（采纳的 14 个都是同一运动家族：stone_surround 固定 root → vertical-plank leaf 绕竖直 Z 铰链 REVOLUTE → 挂环 ring_pull 绕水平 Y 轴 REVOLUTE；第 15 个 `thumb_latch` 出此家族——无 ring_pull part，故未采纳）：

| 结构家族 | 样本数 | 说明 |
|---|---:|---|
| flat-square leaf top（方头）| 10 | 两 parent + 除 archtop/gothic/shoulder 外所有 variant；叶顶平 |
| arched leaf top（圆头）| 1 | archtop：plank 顶按 `arch_z_at` 做 graduated 半圆弧高 |
| pointed lancet leaf top（哥特尖头）| 1 | gothic_top：plank 顶按 `_lancet_arch_z` 两弧交于中点尖峰 |
| shouldered cambered leaf top（肩拱头）| 1 | shoulder_top：plank 顶 `_camber_z_at` 缓拱 + 两外板 shoulder chamfer 切角 |
| box-per-plank `plank_{i}` 循环 | 10 | closed parent 与所有 box-plank variant，干净 `for i in range(PLANK_COUNT)` |
| groove-cut single-box leaf | 1 | open parent：`for i in range(1, PLANK_COUNT)` 在单块 leaf box 上切 V 槽（非 box-per-plank）|
| 横向 iron ledge 铰链带 | 8 | closed parent + planks3/9 + vgroove + archtop + starplate + studgrid（两条平 ledge 带 hinge barrel）|
| 长 strap-hinge 铁带（spade/tapered tip）| 2 | open parent（tapered + diamond finial）、strapstud（spade-tip + 螺栓头排）|
| Z/diagonal 斜撑 | 1 | zbrace：`ledge_i` 循环 + 一条对角 `diagonal_brace` 板 |
| framed（竖向 stile + 横 ledge）| 1 | framedbrace：`stile_hinge`/`stile_free` 两竖铁条 + `ledge_i` 横档 |
| square-plate hung ring（pull）| 11 | 除 open parent / starplate 外都用方背板 `ring_backplate` + `ring_boss`；含 gothic/shoulder 两新顶变体（仍方背板拉环）|
| star/quatrefoil-plate hung ring | 2 | open parent（四角星 escutcheon）、starplate（quatrefoil 四瓣 mesh + rivets + collar）|
| square-plate knocker ring（向下摆击 strike boss）| 1 | knocker_ring：方背板 + boss + 新增 `strike_boss` 靶 + `leaf_to_ring` 双向 range（`lower=-1.0` 向下摆击 / `upper=1.2` 上抬）|
| 无 clavos | 9 | 大多数叶面裸露 |
| clavos 网格 | 1 | studgrid：`_make_clavo_stud` + 7×4 `stud_{row}_{col}` 嵌套网格 |
| strap 螺栓头排 | 1 | strapstud：`STUDS_PER_STRAP=6` 沿 strap `stud_{tag}_{i}` 单轴排 |
| 额外 prismatic slide bolt（门销）| 1 | open parent：`door_bolt` 绕 leaf-local X 滑动穿两 keeper |

被采纳样本逐条标注（14 个采纳，每个贡献一个 distinct slot module；1 个排除见下）：
- `rec_door_plank_ringpull_closed`（closed parent）— adopted：box-per-plank 5 板基线、两横 iron ledge + hinge barrel、方背板挂环、无 clavos、flat top。
- `rec_door_plank_ringpull_open`（open parent）— adopted：6 板 groove-cut leaf、tapered strap-hinge 铁带、四角星 escutcheon、prismatic slide bolt、flat top、arched stone surround。
- `rec_plank_ringpull_door_var_planks3` — adopted：3 宽板 box-per-plank（小 N）。
- `rec_plank_ringpull_door_var_planks9` — adopted：9 窄板 box-per-plank（大 N）。
- `rec_plank_ringpull_door_var_zbrace` — adopted：`_emit_ledge_assembly` + `ledge_i` 循环 + `diagonal_brace` 斜撑。
- `rec_plank_ringpull_door_var_framedbrace` — adopted：竖 stile + `ledge_i` 横档 framed 结构。
- `rec_plank_ringpull_door_var_archtop` — adopted：`arch_z_at` graduated 半圆弧叶顶。
- `rec_plank_ringpull_door_var_starplate` — adopted：quatrefoil mesh escutcheon + rivets + boss collar。
- `rec_plank_ringpull_door_var_studgrid` — adopted：`_make_clavo_stud` domed 头 + `stud_{row}_{col}` 网格。
- `rec_plank_ringpull_door_var_strapstud` — adopted：`_spade_strap_mesh` spade-tip strap + `STUDS_PER_STRAP` 螺栓头排。
- `rec_plank_ringpull_door_var_vgroove` — adopted：`_v_groove_plank_mesh` chamfer V-槽板。
- `rec_plank_ringpull_door_var_gothic_top` — adopted（gap-fill）：`_lancet_arch_z` 两弧 pointed lancet 哥特尖顶（`_make_arch_plank_solid` graduated 尖弧板 + `_make_arch_board_solid` 弧 backing），保留方背板 ring pull。
- `rec_plank_ringpull_door_var_shoulder_top` — adopted（gap-fill）：`_camber_z_at` 缓拱叶顶 + 两外板 shoulder chamfer 切角（per-plank `threePointArc`），保留方背板 ring pull。
- `rec_plank_ringpull_door_var_knocker_ring` — adopted（gap-fill）：方背板 + boss + `strike_boss` 靶；`leaf_to_ring` 双向 range（向下摆击 boss `lower=-1.0` / 上抬 `upper=1.2`），ring 保留并 animate。
- `rec_plank_ringpull_door_var_thumb_latch` — **not adopted**（gap-fill 但出本小类身份）：删除挂环（无 `ring_pull`/`ring`/`ring_backplate`/`ring_boss`、无 `leaf_to_ring`），改 Suffolk thumb-latch（`thumb_lever` part + `leaf_to_thumb_lever` REVOLUTE + `grip_handle`/`pivot_pin`/`latch_bar`）；丢失定义性挂环 hero，属相邻 generic plank-door 类别。

> 备注（gap-fill 已落地）：先前 source map 列为 `planned` 的 4 个候选现已 4 个全部建成、synced（rating=5）并 on-disk。逐条判定后 **3 个采纳为 candidate module**，1 个保持排除：
> - `gothic_pointed_top`（`rec_plank_ringpull_door_var_gothic_top`）→ 采纳为 Slot C `gothic_lancet_top`（pointed lancet 两弧叶顶，**保留 ring**）。
> - `shouldered_camber_top`（`rec_plank_ringpull_door_var_shoulder_top`）→ 采纳为 Slot C `shouldered_camber_top`（shouldered cambered head，**保留 ring**）。
> - `knocker_ring`（`rec_plank_ringpull_door_var_knocker_ring`）→ 采纳为 Slot D `knocker_ring_on_boss`（环成为 knocker，向下摆击 strike boss，**保留并 animate ring**）。
> - `thumb_latch`（`rec_plank_ringpull_door_var_thumb_latch`）→ **保持排除**：该样本**删除了挂环 part**（无 `ring_pull` / `ring` / `ring_backplate` / `ring_boss`，连 `leaf_to_ring` joint 一并移除），改用 Suffolk thumb-latch（独立 `thumb_lever` part + `leaf_to_thumb_lever` REVOLUTE + `grip_handle`/`pivot_pin`/`latch_bar`）。本小类身份是「带挂环拉手（with a ring pull）」的木板门，移除挂环即丢失定义性 hero（与「核心身份」§5、Reject cases「没有可摆动的 ring_pull part」直接冲突），它读作 generic plank-door / thumb-latch 类别而非本 ring-pull 小类，故不列为本 spec 的 candidate（其 model.py 真实存在于 `rec_plank_ringpull_door_var_thumb_latch`，但属相邻类别素材，记入「模板实现备注」与「相邻类别边界」）。

## 核心身份
`plank_ring_door` 是一扇**乡村 ledged-and-braced 竖向木板门叶（vertical-plank leaf）**，挂在石门洞（stone surround）一侧的**竖直（Z 轴）铰链**上摆动开合，叶面带一个**真实可转的铁挂环拉手（ring pull）**绕水平轴（与门面平行）作第二个 REVOLUTE 摆动。默认成熟域必须包含：

1. 一个固定 root **stone_surround**（两 jamb + lintel/header + 圆拱或方头石头 + 门槛 stoop + 嵌入 jamb 的 iron pintle 销）；
2. 一片**竖向木板叶**（box-per-plank 的 `plank_{i}` 或 groove-cut V 槽板），由 backing board 承载；
3. **front bracing**（横 ledge 带 / 长 strap 铁带 / Z 斜撑 / framed stile+ledge），每条 brace 终结于绕 jamb pintle 的 hinge barrel/knuckle，使叶被石 jamb 物理承载；
4. **leaf-to-jamb REVOLUTE 竖直铰链**（axis `(0,0,-1)`，closed pose q=0，向外摆开）；
5. **挂环硬件**（方背板 + boss，或四瓣星 escutcheon + boss，或 knocker 方背板 + boss + strike_boss 铁靶）+ 作为独立 part 的 **ring_pull**，绕水平 Y 轴 REVOLUTE 悬挂摆动（pull 单向上抬，或 knocker 双向：向下摆击靶 + 向上抬）。

可选扩展：clavos/stud 钉花（网格 or strap 螺栓排）、V 槽 plank seam、arched / gothic lancet / shouldered camber 叶顶轮廓、prismatic slide bolt（门销）。这些都不能替代主 leaf hinge + ring pivot 两个 REVOLUTE。

边界（详见末节「与相邻类别的边界」）：rustic 竖木板 + 锻铁挂环 + 石门洞，区别于现代 panel/glazed `door`、通透 `gate`、滑移/折叠/翻板门，以及金属保险箱门。

## 采用源码索引（Adopted Source Index）
所有路径前缀：`data/records/<id>/revisions/rev_000001/model.py`。

| source_id | record_id | 采纳用途（关键 Lx-Ly 见下方 slot 表）|
|---|---|---|
| S1 | `rec_door_plank_ringpull_closed` | box-per-plank 5 板基线、横 ledge+barrel、方背板挂环、stone surround+pintle、leaf hinge+ring pivot 双 REVOLUTE |
| S2 | `rec_door_plank_ringpull_open` | groove-cut 6 板 leaf、tapered strap-hinge、四角星 escutcheon、prismatic slide bolt |
| S3 | `rec_plank_ringpull_door_var_planks3` | 3 宽板 box-per-plank（小 N）|
| S4 | `rec_plank_ringpull_door_var_planks9` | 9 窄板 box-per-plank（大 N）|
| S5 | `rec_plank_ringpull_door_var_zbrace` | `_emit_ledge_assembly` + `ledge_i` 循环 + `diagonal_brace` |
| S6 | `rec_plank_ringpull_door_var_framedbrace` | 竖 stile + `ledge_i` 横档 framed |
| S7 | `rec_plank_ringpull_door_var_archtop` | `arch_z_at` graduated 半圆弧叶顶 |
| S8 | `rec_plank_ringpull_door_var_starplate` | quatrefoil mesh escutcheon + rivets + collar |
| S9 | `rec_plank_ringpull_door_var_studgrid` | `_make_clavo_stud` + `stud_{row}_{col}` 网格 |
| S10 | `rec_plank_ringpull_door_var_strapstud` | `_spade_strap_mesh` + `STUDS_PER_STRAP` 螺栓头排 |
| S11 | `rec_plank_ringpull_door_var_vgroove` | `_v_groove_plank_mesh` chamfer V 槽板 |
| S12 | `rec_plank_ringpull_door_var_gothic_top` | `_lancet_arch_z` 两弧 pointed lancet 哥特尖顶 graduated plank + 弧 backing（保留 ring）|
| S13 | `rec_plank_ringpull_door_var_shoulder_top` | `_camber_z_at` 缓拱 + 两外板 shoulder chamfer 切角叶顶（保留 ring）|
| S14 | `rec_plank_ringpull_door_var_knocker_ring` | 方背板 + boss + `strike_boss` knocker 靶；`leaf_to_ring` 双向 range 向下摆击 |

## 槽位 + 候选模块表

### Slot A：plank_field（竖板场 — multiplicity 主轴 plank_count）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `box_per_plank_5` | S1 | `model.py:L311-L318`（plank 循环）+ `L300-L305`（backing）| eligible if compatible | 5 板 box-per-plank 基线，flat 平板，`plank_{i}` Box，narrow gap 透 `dark_oak_groove` backing |
| `box_per_plank_3` | S3 | `model.py:L311-L318`（`PLANK_COUNT=3` L36）| eligible if compatible | 3 宽板，同 box-per-plank 循环，每板更宽 |
| `box_per_plank_9` | S4 | `model.py:L311-L318`（`PLANK_COUNT=9` L36，`PLANK_GAP=0.003`）| eligible if compatible | 9 窄板，密集竖板 |
| `groove_cut_single_box` | S2 | `model.py:L434-L466`（`_build_leaf_shape` 在单块 leaf box 上 `for i in range(1, PLANK_COUNT)` 切槽）| eligible if compatible | 单块 leaf box + V 槽划缝（非 box-per-plank），open parent 6 板写法 |

说明：A 槽是 multiplicity 主轴（`plank_count` ∈ {3,5,6,9} 已覆盖 4 distinct N）。`box_per_plank_*` 三者共享同一 `plank_{i}` 循环范式，N 不同即不同 topology equivalence class（板数改变 part 数）；`groove_cut_single_box` 是结构不同的实现（单 mesh + 切缝，板数靠槽线表达）。

### Slot B：front_bracing（叶面铁/木撑 + 铰链带）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `horizontal_ledges` | S1 | `model.py:L320-L358`（`ledge_{tag}` L335-L340 + `hinge_barrel_{tag}` L345-L350 + `hinge_stub_{tag}` L352-L358）| eligible if compatible | 两条横 iron ledge 带，各终结于绕 pintle 的 barrel knuckle（ledged 基线）|
| `strap_hinge_face` | S2 | `model.py:L469-L546`（`_build_strap_hinge_shape`：tapered root+tip L494-L505、diamond finial L507-L514、barrel knuckle L529-L537、neck L539-L546）+ emit `L734-L740`（`strap_hinge_{idx}`）| eligible if compatible | 两条长 tapered 锻铁 strap，spade/diamond 端，横跨叶面到 latch 边（ledged-and-braced 重型）|
| `z_brace_ledged` | S5 | `model.py:L282-L315`（`_emit_ledge_assembly` helper：`ledge_{i}` L297-L302 + `hinge_barrel_{i}` L303-L308 + `hinge_stub_{i}` L309-L315）+ `ledge_i` 循环 `L360-L362` + 对角 `diagonal_brace` `L364-L389` | eligible if compatible | 上下横 ledger（`range(2)` 循环）+ 一条 `atan2` 角度的对角斜撑板（Z/N brace）|
| `framed_and_braced` | S6 | `model.py:L325-L341`（竖 `stile_hinge`/`stile_free` 铁条）+ `ledge_i` 横档循环 `L343-L359`（`LEDGE_COUNT=2` L43）+ barrel/stub `L361-L382` | eligible if compatible | 两侧竖铁 stile + 之间 `ledge_{i}` 横档（framed 门），无对角 |

说明：四者 part tree 与 joint-外 visual topology 明显不同（横档 vs 长 strap vs 横档+对角 vs 竖 stile+横档）。每个都自带 hinge barrel/knuckle → 都能接 leaf-to-jamb 铰链。

### Slot C：leaf_top_profile（叶顶轮廓）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_top` | S1 | `model.py:L300-L318`（backing + plank 全高等高 Box，方头）| eligible if compatible | 平方头叶顶（两 parent + 8 个 variant 的默认）|
| `arched_top` | S7 | `model.py:L311-L315`（`arch_z_at` helper）+ arched backing `L317-L337`（`threePointArc`）+ graduated plank 循环 `L344-L374`（每板 `z_left/z_right/z_center` 按 `arch_z_at`，中板最高）+ arch 常量 `L90-L99` | eligible if compatible | 半圆 round-headed 叶顶：plank 顶按弧高 graduated，需配 arched stone surround soffit clearance |
| `gothic_lancet_top` | S12 | `model.py:L106-L129`（`_lancet_arch_z` 两弧交于中点尖峰 helper）+ `_make_arch_plank_solid` `L132-L172`（按 lancet 弧 sampled 顶的 graduated plank mesh）+ `_make_arch_board_solid` 弧 backing `L175-L214` + graduated plank emit `L429-L453` + lancet 常量 `L45-L49,L97-L99` | eligible if compatible | pointed lancet 哥特尖顶：两段圆弧交于中点尖峰，中板峰高于边板（>0.05m）；峰须低于 surround soffit，配 arched surround soffit clearance |
| `shouldered_camber_top` | S13 | `model.py:L105-L112`（`_camber_z_at` 缓拱 helper）+ shoulder/camber 常量 `L90-L102` + per-plank `threePointArc` 缓拱 + 两外板 shoulder chamfer 循环 `L336-L376`（i==0 / i==PLANK_COUNT-1 切外上角）+ 全高 backing `L324-L329` | eligible if compatible | shouldered cambered head：plank 顶缓拱（中板略高于边板），最外两板上外角 shoulder chamfer 切落（drop `SHOULDER_DROP`），低拱顶通常方 lintel surround 可容 |

降级理由解除（candidate=2 → 4，≥3 满足）：先前列为 planned 的 `gothic_pointed_top` / `shouldered_camber_top` 已 on-disk 建成（S12/S13，rating=5），各贡献一个真实结构不同的叶顶轮廓。四个 candidate 是四类不同 plank 顶几何：平 Box（flat）、graduated 半圆 mesh（arched）、两弧尖峰 mesh（gothic lancet）、缓拱 + shoulder chamfer mesh（shoulder）；各改变 plank part 顶部几何并与 surround soffit clearance 相关，属独立结构层（不折入相邻 slot）。其中 `arched_top` / `gothic_lancet_top` 须配 arched surround soffit（峰高），`flat_top` / `shouldered_camber_top` 低顶可配 square_header（见 compatibility matrix）。

### Slot D：ring_hardware（挂环 escutcheon 五金风格）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `ring_on_square_plate` | S1 | `model.py:L384-L389`（`ring_backplate` 方 Box）+ `L395-L403`（`ring_boss` 前凸柱）+ ring part `_build_ring_pull` `L426-L460`（torus revolve）| eligible if compatible | 方铁背板 + 前 boss，环挂其上、单向上抬 pull（基线；多数样本采用）|
| `ring_on_star_plate` | S8 | `model.py:L407-L426`（quatrefoil 四瓣 mesh `ring_escutcheon`）+ rivets 循环 `L432-L449`（`escutcheon_rivet_{i}`）+ boss collar `L454-L470` + boss `L478-L486` + ring part `_build_ring_pull` `L509-L543` | eligible if compatible | 锻铁四瓣星 quatrefoil escutcheon + 四角 rivets + collar + boss（open parent 用四角星变体 `model.py:L549-L591` `_build_ring_plate_shape`）|
| `knocker_ring_on_boss` | S14 | `model.py:L396-L401`（`ring_backplate` 方 Box）+ `L406-L415`（`ring_boss`）+ `strike_boss` 靶 `L420-L428` + strike 常量 `L68-L91` + ring part `_build_ring_pull` `L451-L485` + `leaf_to_ring` 双向 joint `L527-L535`（`lower=-1.0` 向下摆击 / `upper=1.2` 上抬）| eligible if compatible | 方背板 + boss + 下方新增 `strike_boss` 铁靶；ring 成为 knocker，向下摆击靶（rest 接触靶 allow_overlap）、向上抬离；保留并 animate ring，joint range 双向 |

降级理由解除（candidate=2 → 3，≥3 满足）：先前列为 planned 的 `knocker_ring` 已 on-disk 建成（S14，rating=5），保留并 animate 挂环，仅在方背板 + boss 之外加 `strike_boss` 铁靶并把 `leaf_to_ring` joint range 改为双向（向下摆击 + 向上抬），是真实结构不同的硬件层（新增 part + 不同 joint 语义）。三个 candidate part tree / joint 语义不同：方 Box 单向 pull（square）、多瓣 mesh + rivets + collar（star）、方 Box + strike_boss 双向 knocker（knocker）。`thumb_latch` 虽 on-disk（`rec_plank_ringpull_door_var_thumb_latch`）但**移除挂环、出本小类身份**（无 `ring_pull` part），不列为 candidate（见「核心身份」§5 与 Reject cases）。不折入 Slot E 是因为 escutcheon/boss 是 ring_pull part 的 upstream mount，决定 boss pivot 位置，属独立硬件层。

### Slot E：clavos_field（钉花/螺栓头场 — 次级 multiplicity）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `no_clavos` | S1 | `model.py:L307-L318`（裸 plank 面，无钉花）| eligible if compatible | 叶面无钉花（9 个样本基线）|
| `clavos_grid` | S9 | `model.py:L289-L309`（`_make_clavo_stud`：shank 柱 L298-L302 + dome 半球 L303-L308）+ `_CLAVO_STUD` 预建 `L313` + 嵌套网格循环 `L357-L374`（`stud_{row}_{col}`，`STUD_ROWS=7`/`STUD_COLS=4` L55-L59）| eligible if compatible | 规则 row×col domed 钉花网格满铺叶面，避开 ledge/硬件足迹 |
| `strap_studs_row` | S10 | `model.py:L291-L315`（`_spade_strap_mesh` spade strap）+ `STUDS_PER_STRAP=6`（L74）+ 沿 strap 单轴循环 `L388-L398`（`stud_{tag}_{i}` 螺栓头 Cylinder）| eligible if compatible | 沿每条 spade-tip strap 等距 6 颗螺栓头排（铆 strap 到板）|

说明：三者真实结构不同（无钉 vs 二维网格 vs 沿 strap 一维排）；`clavos_grid` 与 `strap_studs_row` 各引入一个钉花 multiplicity 轴（见 Multiplicity 节）。`strap_studs_row` 与 Slot B 的 `strap_hinge_face` 共用铁件区，组合时把螺栓排打在 strap 上而非另叠 ledge（见 compatibility matrix）。

### Slot F：plank_seam（板缝外观 — 次级外观轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_butted` | S1 | `model.py:L307-L318`（`plank_{i}` 平 Box + `PLANK_GAP` 缝隙）| eligible if compatible | 平接板，narrow gap 透深色 backing 形成缝影（基线）|
| `v_groove` | S11 | `model.py:L118-L177`（`_v_groove_plank_mesh`：Box 板 + 两 chamfer cutter `cutter_top` L157-L164 / `cutter_bottom` L167-L174 + `plank.cut(...)` L176）+ emit 循环 `L382-L397`（`plank_{i}` mesh）| eligible if compatible | chamfer 倒角 V 形 tongue-and-groove 缝边 |

降级理由（candidate=2，未到 3）：板缝是次级外观轴，on-disk 仅 `flat_butted`（基线）与 `v_groove`（S11）两类真实几何差异（平 Box vs chamfer-cut mesh）。两者是不同 plank mesh 拓扑（Box vs cut mesh）。无更多 on-disk seam 结构样本，故保留 2 个。不折入 Slot A 是因为 seam 与 plank_count（A 的 multiplicity）正交：`v_groove` 与任意 N 自由组合，只要保持 `plank_{i}` box-per-plank 循环；故作独立外观 slot 表达。后续若需第三个 seam（如 shiplap 搭接）补样本再扩。

## 槽位图（slot graph）
pattern = `mixed`

```
[Slot C top + Slot F seam decide leaf geometry]
                 |
                 v
[stone_surround (FIXED root, on ground)]
   |  jamb_pintle_{tag} (iron pin in jamb)
   |
   +== REVOLUTE  surround_to_leaf  axis=(0,0,-1)  origin=(-Y jamb edge, z=0) ==>
                 |
                 v
        [Slot A plank_field + Slot B bracing + Slot E clavos]  =  door_leaf (moving part)
                 |   hinge_barrel/knuckle wraps jamb_pintle (captured pin, support path)
                 |
                 +== REVOLUTE  leaf_to_ring  axis=(0,-1,0)  origin=boss pivot line ==>
                 |        [Slot D escutcheon → boss (+ strike_boss if knocker)] → ring_pull (moving part)
                 |        (square/star: lower=0 上抬; knocker: lower≈-1.0 向下摆击 strike_boss)
                 |
                 +== (optional) PRISMATIC  door_to_bolt  axis=(±1,0,0)  through 2 keepers ==>
                                            door_bolt (moving part, open-parent S2 only)
```

接口点位与 joint 策略：
- **stone_surround → door_leaf**（主 spine）：竖直 Z 铰链。joint origin 在 -Y jamb 边沿、门槛上方 z=0（叶 part frame 坐在铰链线上，几何向 +Y 延伸）。`axis=(0,0,-1)` 使正 q 把自由（+Y）边向 +X 摆开。range 标称 `lower=0, upper≈2.0`（reviewer 可收到 1.2-2.4）。**support 路径**：Slot B 每条 brace 的 `hinge_barrel`/`hinge_stub` knuckle 包住嵌在 jamb 里的 `jamb_pintle_{tag}`（captured pin），叶被石 jamb 承载。
- **door_leaf → ring_pull**（hero 第二运动）：水平 Y 轴铰链。joint origin 在 Slot D escutcheon boss 的 pivot 线（环顶）。`axis=(0,-1,0)`，正 q 把环下缘抬离门面（+X）。range：square/star plate `lower=0, upper≈1.2`（仅上抬 pull）；knocker `lower≈-1.0, upper≈1.2`（负 q 把环下缘向下摆击 `strike_boss`，正 q 上抬）。环顶 tube 包住 boss（captured ring-on-boss，需局部 allow_overlap）；knocker 还需 ring vs `strike_boss` 的 rest-contact allow_overlap。
- **door_leaf → door_bolt**（可选，仅 open parent S2 子域）：水平 leaf-local X PRISMATIC，穿两 `bolt_keepers` loop。range `[0, BOLT_TRAVEL≈0.10]`，全程保持插入两 keeper。

互斥/可选关系：Slot C 高峰顶（`arched_top` / `gothic_lancet_top`）需配 arched stone surround soffit，低顶（`flat_top` / `shouldered_camber_top`）容 square_header（见 compatibility matrix）；Slot D 一次只一种 escutcheon，`knocker_ring_on_boss` 解析双向 ring joint range + 加 `strike_boss`；Slot E `strap_studs_row` 仅当 Slot B = `strap_hinge_face` 时合法（螺栓打在 strap 上）；可选 slide bolt 默认关闭，仅在采到 open-parent 子域时启用。三个 Slot D 选项都保留可摆动 ring_pull part（不像被排除的 thumb_latch 会移除环）。

## 每槽位 Module Emits / Interfaces

### Slot A / plank_field
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_leaf` 内 `backing_board` + `plank_{i}` (i=0..N-1) box-per-plank，或 `groove_cut_single_box` 单 mesh `leaf_planks` | S1 `model.py:L300-L318` / S2 `model.py:L434-L466,L726-L730` |
| internal joints | 无（plank 是 leaf 的 inline visual，不单独 joint）| S1 |
| upstream interface | leaf part frame 坐在 -Y jamb 铰链线上（hinge edge 在 local y=0）| S1 `model.py:L288-L298` |
| downstream interface | plank 前面（`plate_x = -DOOR_T/2+BACK_T+PLANK_T`）是 Slot B/D/E 硬件挂载面；plank 中心列是 clavos 网格列对齐参考 | S1 `model.py:L360-L361` |

### Slot B / front_bracing
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ledge_{tag}`/`ledge_{i}` 或 `strap_hinge_{idx}`/`strap_{tag}` 或 `stile_hinge`/`stile_free` + `diagonal_brace`；每条带 `hinge_barrel_*` + `hinge_stub_*` knuckle | S1 L320-L358 / S2 L469-L546,L734-L740 / S5 L282-L315,L360-L389 / S6 L325-L382 |
| internal joints | 无（bracing 是 leaf inline visual）| 同上 |
| upstream interface | hinge barrel/knuckle 在 -Y 边沿外伸包 jamb pintle = leaf↔surround 真实承载接口 | S1 L344-L350 / S2 L529-L537 |
| downstream interface | brace 板面是 Slot E（strap_studs_row）的螺栓挂载基；ledge 高度为 clavos 网格避让带 | S10 L383-L398 |

### Slot C / leaf_top_profile
| emits | 描述 | 来源 |
|---|---|---|
| parts | flat：全高等高 `plank_{i}` Box；arched：`arch_z_at` graduated plank mesh + arched `backing_board`；gothic：`_lancet_arch_z` 两弧尖峰 graduated plank mesh + 弧 backing；shoulder：`_camber_z_at` 缓拱 + 两外板 shoulder chamfer 的 `plank_{i}` mesh | S1 L300-L318 / S7 L311-L374 / S12 L132-L214,L429-L453 / S13 L105-L112,L336-L376 |
| internal joints | 无 | S7 |
| upstream interface | 叶顶 z 上限必须低于 surround soffit（flat/shoulder→方 lintel 可容；arched/gothic 峰高→arch soffit）| S7 L90-L99 / S12 L92,L677-L688 |
| downstream interface | 顶轮廓不影响下游 joint（铰链在底/侧、ring 在面），仅约束 surround clearance | S7 |

### Slot D / ring_hardware
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定：`ring_backplate`(方) 或 `ring_escutcheon`+`escutcheon_rivet_{i}`+`boss_collar`(星) + `ring_boss`；knocker 另加 `strike_boss` 铁靶；活动：独立 part `ring_pull`(`ring` torus) | S1 L384-L460 / S8 L407-L543 / S14 L396-L428,L451-L485 |
| internal joints | `leaf_to_ring` REVOLUTE（boss pivot 线，axis Y）；square/star 单向 `lower=0,upper≈1.2`，knocker 双向 `lower=-1.0,upper=1.2`（向下摆击靶 + 上抬）| S1 L501-L509 / S8 L584-L592 / S14 L527-L535 |
| upstream interface | escutcheon 方/星背板 seat 在 plank 前面（proud +X）；boss 中心 = ring pivot 线；knocker 的 `strike_boss` 也 seat 在 plank 面、对齐 ring rest 底缘 | S1 L375-L403 / S14 L86-L91,L420-L428 |
| downstream interface | ring `ring` torus 顶 tube 包 boss（captured ring-on-boss，需 allow_overlap）；knocker 还需 ring vs `strike_boss` 的 rest-contact allow_overlap | S1 L654-L661 / S14 L697-L704 |

### Slot E / clavos_field
| emits | 描述 | 来源 |
|---|---|---|
| parts | none：无；grid：`stud_{row}_{col}` (R×C)；strap：`stud_{tag}_{i}` (2×K) domed/bolt 头 | S9 L289-L374 / S10 L388-L398 |
| internal joints | 无（钉花是 inline visual）| S9 |
| upstream interface | 钉 shank 嵌 plank 前面；网格避让 ledge/硬件足迹；高 N 时列对齐 plank 中心 | S9 L356-L374 |
| downstream interface | 无 | S9 |

### Slot F / plank_seam
| emits | 描述 | 来源 |
|---|---|---|
| parts | flat：`plank_{i}` 平 Box + gap；v_groove：`_v_groove_plank_mesh` chamfer 板 | S1 L307-L318 / S11 L118-L177,L382-L397 |
| internal joints | 无 | S11 |
| upstream interface | 与 Slot A `plank_{i}` 循环共用（替换板 mesh，不改板数/placement）| S11 L382-L397 |
| downstream interface | 无 | S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `plank_field_style` | enum | `box_per_plank` / `groove_cut_single_box` | `box_per_plank` | choice | 由 sampler 选 Slot A 实现方式 | S1 / S2 |
| `plank_count` | int | `[3, 9]`（产品域；测试偏小）| 5 | conditional | groove_cut 子域用 5-6；box_per_plank 全程 [3,9]；N 决定 `plank_{i}` 数 | S1/S3/S4/S2 |
| `bracing_style` | enum | `horizontal_ledges` / `strap_hinge_face` / `z_brace_ledged` / `framed_and_braced` | `horizontal_ledges` | choice | 选 Slot B module | S1/S2/S5/S6 |
| `top_profile` | enum | `flat_top` / `arched_top` / `gothic_lancet_top` / `shouldered_camber_top` | `flat_top` | conditional | 选 Slot C；高峰顶（arched/gothic）须 surround=arched_surround；低顶（flat/shoulder）容 square_header | S1 / S7 / S12 / S13 |
| `ring_hardware` | enum | `ring_on_square_plate` / `ring_on_star_plate` / `knocker_ring_on_boss` | `ring_on_square_plate` | choice | 选 Slot D escutcheon；knocker 加 strike_boss + 双向 ring joint range | S1 / S8 / S14 |
| `clavos_style` | enum | `no_clavos` / `clavos_grid` / `strap_studs_row` | `no_clavos` | conditional | strap_studs_row 仅当 bracing=strap_hinge_face | S1/S9/S10 |
| `plank_seam` | enum | `flat_butted` / `v_groove` | `flat_butted` | choice | 选 Slot F；与 N 正交 | S1 / S11 |
| `palette_style` | enum | `dark_oak_black_iron` / `weathered_grey_rust` / `light_timber_bronze` / `walnut_pewter` / `bleached_oak_blacksmith` / `redwood_castiron` | `weathered_grey_rust` | choice | 选 wood+iron+stone 配色组（见下表）| S1 `_wood` L91-L108 衍生 |
| `surround_style` | enum | `square_header` / `arched_surround` | `square_header` | conditional | arched_surround 须容高峰顶（arched_top / gothic_lancet_top）；square_header 容低顶（flat_top / shouldered_camber_top）| S1 / S2 |
| `slide_bolt` | enum | `none` / `present` | `none` | conditional | present 仅在 groove_cut/open-parent 子域，加 `door_bolt` PRISMATIC | S2 L624-L688,L822-L830 |
| `leaf_width` | float | `[0.78, 0.95]` | 0.85 | independent | 叶宽（Y），派生 plank_w 与 opening 宽 | S1 `DOOR_W` L32 |
| `leaf_height` | float | `[1.85, 2.10]` | 2.00 | independent | 叶高（Z），派生 opening 高与 brace z | S1 `DOOR_H` L33 |
| `plank_w` | float | derived | — | equation | `= (leaf_width - (plank_count-1)*PLANK_GAP) / plank_count` | S1 L308-L309 |
| `ring_radius` | float | `[0.050, 0.070]` | 0.058 | independent | 环外径，需 < escutcheon 留 clearance | S1 `RING_OUT_R` L55 |
| `clavos_rows` | int | `[4, 8]` | 7 | conditional | 仅 clavos_grid；随 leaf_height clamp | S9 `STUD_ROWS` L57 |
| `clavos_cols` | int | `[2, 5]` | 4 | conditional | 仅 clavos_grid；高 plank_count 时对齐板中心 | S9 `STUD_COLS` L58 |
| `studs_per_strap` | int | `[4, 8]` | 6 | conditional | 仅 strap_studs_row；沿 strap 等距 | S10 `STUDS_PER_STRAP` L74 |
| `ledge_count` | int | `[2, 3]` | 2 | conditional | 仅 framed_and_braced / z_brace 横档数 | S6 `LEDGE_COUNT` L43 |
| `hinge_upper` | float | `[1.2, 2.4]` | 2.0 | independent | leaf hinge 开角上限（rad）| S1 L492 |
| `ring_upper` | float | `[0.6, 1.4]` | 1.2 | independent | ring pivot 抬升上限（rad）| S1 L508 |
| `ring_lower` | float | `[-1.0, 0.0]` | 0.0 | conditional | ring pivot 下限：square/star=0（仅上抬），knocker=`[-1.0,-0.5]`（向下摆击 strike boss）| S14 L534 |
| (—) | constraint | — | — | inequality | `ring_radius + RING_TUBE_R ≤ escutcheon 半尺寸`；违反则缩 ring_radius | S1 / S8 escutcheon |
| (—) | constraint | — | — | inequality | 叶顶 z 上限 ≤ surround soffit − clearance（arched_top 用 arch soffit）| S7 L90-L99 |
| (—) | constraint | — | — | inequality | clavos 网格须避开 ledge/escutcheon/lock 足迹（投影回缩或丢该钉）| S9 L356-L363 |

### palette_style 配色组（≥3，本表 6 组，wood / iron / stone 三色 + groove 暗色）
| palette_style | wood (weathered_oak) | iron (aged_iron) | stone (old_stone) | 说明 |
|---|---|---|---|---|
| `dark_oak_black_iron` | (0.28,0.20,0.13,1) | (0.06,0.06,0.07,1) | (0.50,0.49,0.47,1) | 深橡木 + 纯黑锻铁（古堡/教堂门）|
| `weathered_grey_rust` | (0.47,0.41,0.32,1) | (0.21,0.18,0.16,1) | (0.56,0.55,0.52,1) | 风化灰褐木 + 锈色铁（closed parent 基线）|
| `light_timber_bronze` | (0.74,0.66,0.50,1) | (0.40,0.30,0.16,1) | (0.62,0.60,0.55,1) | 浅木 + 青铜五金 |
| `walnut_pewter` | (0.33,0.24,0.18,1) | (0.42,0.42,0.45,1) | (0.52,0.51,0.50,1) | 胡桃木 + 锡灰金属 |
| `bleached_oak_blacksmith` | (0.80,0.77,0.70,1) | (0.10,0.10,0.11,1) | (0.60,0.60,0.58,1) | 漂白浅橡 + 黑铁（open parent 偏色）|
| `redwood_castiron` | (0.45,0.26,0.18,1) | (0.16,0.15,0.15,1) | (0.55,0.53,0.50,1) | 红木 + 深灰铸铁 |

palette_style 仅改材质 rgba，不改任何拓扑；在 `resolve_config` 选定后传给所有 `model.material(...)`。groove/keystone/step 等次级色在每组内按主色派生（如 wood_dark = wood × 0.62）。

## Multiplicity / Copy Logic

本类有 **3 根 multiplicity 轴**（主 1 + 次 2），均按小类按轴定 N_range 与权重，下游模板各做一次加权采样、各编进 `slot_choices`、各自 clamp、sweep 各设上限。

### 轴 1（主）：`plank_count`（竖板数）
- `count_param`：`plank_count`
- `N_range`：`[3, 9]`（产品全程；测试偏小 N=3,5,6）
- sampling domain：小 N 高频（3-6 占 ~80%），大 N（7-9）稀有 ~20%；样本已覆盖 {3,5,6,9}
- copied object：一根竖板 `plank_{i}` Box（或 `groove_cut` 中一条切槽缝）
- naming：`plank_{i}`（i=0..plank_count-1）
- placement：沿叶宽 Y 等距，`cy = plank_w/2 + i*(plank_w + PLANK_GAP)`，跨固定 leaf_width
- joint policy：plank 是 leaf inline visual，无独立 joint；叶整体走唯一 `surround_to_leaf` REVOLUTE
- source/gating：S1/S3/S4 box-per-plank 循环 + S2 groove-cut；`groove_cut_single_box` 子域 N 收到 5-6

### 轴 2（次）：`clavos_rows × clavos_cols`（钉花网格，仅 clavos_grid）
- `count_param`：`clavos_rows`（行）+ `clavos_cols`（列）二维
- `N_range`：rows `[4, 8]`，cols `[2, 5]`（样本 7×4）
- sampling domain：rows/cols 小值高频；高 plank_count 时 cols 对齐板中心避缝
- copied object：一颗 domed clavo（`_make_clavo_stud` 预建 `_CLAVO_STUD`）
- naming：`stud_{row}_{col}`
- placement：叶面 Y×Z 规则网格，避让 ledge/escutcheon/lock 足迹
- joint policy：inline visual，无 joint
- source/gating：S9；仅 `clavos_style=clavos_grid` 时启用

### 轴 3（次）：`studs_per_strap`（沿 strap 螺栓头，仅 strap_studs_row）
- `count_param`：`studs_per_strap`
- `N_range`：`[4, 8]`（样本 6）
- sampling domain：6 为众数，4-8 均匀
- copied object：一颗螺栓头 Cylinder
- naming：`stud_{tag}_{i}`（tag ∈ {bottom, top}，i=0..K-1）
- placement：沿每条 strap 长轴等距（`stud_y_start..stud_y_end`）
- joint policy：inline visual，无 joint
- source/gating：S10；仅 `bracing_style=strap_hinge_face` 且 `clavos_style=strap_studs_row` 时启用

### 模板级固定（非 count_param）复制
`ledge_{i}` 横档（z_brace/framed，由 `ledge_count∈[2,3]` 控）、`escutcheon_rivet_{i}`（star plate 固定 4 个）、hinge `barrel/stub` 对（bottom/top 固定 2 个）、coursing/voussoir 石块、bolt keepers（固定 2 个）都是 baked visual / 受限小整数，不作主 multiplicity 轴。

## 拓扑多样性审计

总组合数（仅 on-disk converged candidates，合法化前；gap-fill 后 C=2→4、D=2→3）：
Slot A=4 × Slot B=4 × Slot C=4 × Slot D=3 × Slot E=3 × Slot F=2 = **1152** 种 slot 组合。
乘 distinct `plank_count` ∈ {3,5,6,9} = 4 →（plank_count 改变 part 数，是 distinct topology equivalence class）→ **1152 × 4 = 4608** distinct topology 上界（远 ≥ 10）。
再叠 clavos 网格 N（rows×cols）与 studs_per_strap N 的 distinct 计数会进一步放大，但不计入即已充分。

理由：plank_count（part 数）、bracing part tree（横档/长 strap/横档+对角/竖 stile+横档）、top profile（平 Box / graduated 半圆 mesh / 两弧尖峰 mesh / 缓拱+shoulder chamfer mesh 四类）、ring hardware part tree+joint 语义（方 Box 单向 / 多瓣 mesh+rivets+collar / 方 Box+strike_boss 双向 knocker 三类）、clavos 拓扑（无/二维网格/一维排）、seam mesh（Box vs cut mesh）每一个都改变 part/joint skeleton，单 bracing×top×hardware×plank_count 就远超 10。

seed_domain_policy：procedural_first
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 4608 slot 组合 + multiplicity N 足以达成（即使受 compatibility gating 排除部分组合，合法子集仍 ≥ 数百）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对普通 seed deterministic procedural sampling，`seed=0` 不特殊。采样顺序：(1) 先选上游 `plank_field_style` + `plank_count`（轴 1 加权）；(2) 选 `bracing_style`；(3) 选 `top_profile`（flat/arched/gothic_lancet/shoulder 四选）并据此解析 `surround_style`（高峰顶 arched_top/gothic_lancet_top→arched_surround；低顶 flat_top/shouldered_camber_top 容 square_header）；(4) 选 `ring_hardware`（square/star/knocker 三选）并据此解析 ring joint range（knocker→`ring_lower∈[-1.0,-0.5]` 双向 + 加 `strike_boss`；square/star→`ring_lower=0`）；(5) 据 bracing 解析 `clavos_style`（strap_studs_row 仅配 strap_hinge_face）并采轴 2/3 的 N；(6) 选 `plank_seam`、`palette_style`；(7) 采连续 scale（leaf_width/height/ring_radius/hinge_upper/ring_upper，independent），派生 plank_w，按 inequality 投影 ring_radius / 叶顶 clearance / clavos 避让。无 regression overrides（除非 sweep 发现稳定失败组合才加少量显式 seed 并注明）。

Controlled local parameterization：初版应含 `leaf_width`、`leaf_height`、`ring_radius`、`hinge_upper`、`ring_upper` 连续 scale，以及离散 `clavos_rows/cols`、`studs_per_strap`、`ledge_count`。全部在 `resolve_config` clamp/派生：`plank_w` 由 equation 派生；ring_radius、叶顶 z、clavos 网格位置由 inequality 投影回缩，不破坏 InterfaceSpec（pintle 捕获、boss 捕获、keeper 插入）/ MatingContract / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 槽序 A→B→C(+surround)→D(+ring range/strike_boss)→E(+轴2/3 N)→F→palette→连续 scale；C 四选、D 三选；轴 1/2/3 各加权采样 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 见下方矩阵：高峰顶（arched/gothic）↔arched_surround 绑定（低顶 flat/shoulder 容 square）；knocker→双向 ring range + strike_boss；strap_studs_row 仅配 strap_hinge_face；slide_bolt 仅 groove_cut 子域；一次一种 ring hardware；ring_pull 始终保留 | no floating、no collision、轴正确、max N、bulky module、optional child 失败 |
| controlled local variation | leaf_width/height/ring_radius/hinge_upper/ring_upper（+ knocker 时 ring_lower 双向）+ clavos/studs/ledge 整数；全 clamp/派生 | 比例变化不破 pintle/boss/strike/keeper 接口、clearance、joint origin、类别身份 |
| regression overrides | none（未来按需加，注明 seed+原因）| 仅已知失败回归或 reviewer 指定 |
| random sweep | seeds 0、0-4、0-19、0-49 初验；0-999 成熟审计 | 与 contract 失败 |

兼容矩阵（compatibility matrix，优先排除易坏组合）：
1. 高峰顶 `arched_top` / `gothic_lancet_top`（C）⇒ 必须 `arched_surround`（surround_style）：否则方 lintel soffit 会切到圆弧/尖峰叶顶；高峰顶配 square_header 拒绝/降级为 flat_top。低顶 `flat_top` / `shouldered_camber_top` 可配 square_header 或 arched_surround（shoulder 缓拱 + chamfer 顶不超方 lintel soffit）。
2. `strap_studs_row`（E）⇒ 必须 `strap_hinge_face`（B）：螺栓排打在 strap 上；其它 bracing 没有 strap，组合降级为 no_clavos 或 clavos_grid。
3. `strap_hinge_face`（B）+ `clavos_grid`（E）：允许，但网格须避开 strap 铁件足迹（投影回缩）；铁件已占面时优先 strap_studs_row。
4. 一次只一种 ring hardware（D 单选：square / star / knocker）；ring_pull 始终保留（不像被排除的 thumb_latch 会移除环）。`knocker_ring_on_boss` 时同时加 `strike_boss` part 并把 `leaf_to_ring` 解析为双向 range（`ring_lower<-0.5`），ring rest 接触 strike_boss（rest-contact allow_overlap）；square/star 时 `ring_lower=0`、无 strike_boss。
5. `slide_bolt=present`⇒ 仅在 `plank_field_style=groove_cut_single_box`（open-parent 子域）采，且默认 `none`；present 时加 `door_bolt` PRISMATIC + 2 keeper，rod 全程插两 keeper。
6. 高 `plank_count`（7-9）+ `clavos_grid`：cols 对齐 plank 中心而非缝，clamp cols ≤ plank_count。
7. `v_groove`（F）与任意 N/bracing/top/hardware 自由组合（保持 `plank_{i}` 循环）。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A plank_field | 4 | yes | yes | box-per-plank ×3 (N=3/5/9) + groove-cut |
| B front_bracing | 4 | yes | yes | ledges / strap / z-brace / framed |
| C leaf_top_profile | 4 | yes | yes | flat / arched / gothic_lancet / shouldered_camber（gap-fill 后降级解除）|
| D ring_hardware | 3 | yes | yes | square plate / star plate / knocker（gap-fill 后降级解除；thumb_latch 排除——移除环、出小类身份）|
| E clavos_field | 3 | yes | yes | none / grid / strap-row |
| F plank_seam | 2 | yes | no | flat / v-groove（待第三 seam 样本，降级理由见上）|

## Validator
- `slot_choices_for_seed` 返回已实现 module 名（A-F 六槽 + palette）
- `config_from_seed` 对普通 seed 用 deterministic procedural sampling
- compatibility matrix / gating 阻止非法组合（arched_top 无 arched_surround、strap_studs_row 无 strap_hinge_face、双 escutcheon 等）
- optional regression overrides 稀疏且有理由（当前 none）
- 不无限轮换小型 curated/modulo 表作主 seed domain
- 受控局部 scale（leaf_width/height/ring_radius/hinge/ring upper）clamp，且不破坏 pintle 捕获 / boss 捕获 / keeper 插入接口、clearance、joint origin、plank/clavos multiplicity
- 跨部件 scale 依赖（plank_w equation、ring_radius / 叶顶 clearance / clavos 避让 inequality）在 `resolve_config` 求解，不留到 builder 失败
- 关键 InterfaceSpec / MatingContract 存在：(a) hinge barrel/knuckle 包 jamb pintle（captured pin，contact + allow_overlap）；(b) ring 顶 tube 包 boss（captured ring-on-boss）；(c) knocker 时 ring vs strike_boss 的 rest-contact allow_overlap；(d) slide bolt rod 全程穿两 keeper（若 present）
- 关键 joint 类型/轴/range：`surround_to_leaf` REVOLUTE 竖直 `(0,0,-1)` lower=0 / upper∈[1.2,2.4]；`leaf_to_ring` REVOLUTE 水平 `(0,-1,0)`：square/star lower=0、knocker lower∈[-1.0,-0.5]，upper∈[0.6,1.4]；`door_to_bolt`（可选）PRISMATIC 水平 X
- copied objects 命名/placement：`plank_{i}` 等距、`stud_{row}_{col}` 网格、`stud_{tag}_{i}` 沿 strap、`ledge_{i}` 等高
- identity：存在 stone_surround + 竖板 leaf + ≥1 bracing + 挂环 ring_pull（两 REVOLUTE）

## Reject cases
- 没有可摆动的 ring_pull part（环被画成固定装饰，缺第二 REVOLUTE）；或把挂环整个换成 thumb-latch/lever 等非环 hardware（移除挂环 = 出本小类身份，参 thumb_latch 排除）。
- 叶面是整块 raised panel / glazed / louvered（变成现代 `door`，丢失竖板身份）。
- leaf hinge 轴画成水平或 ring pivot 画成竖直（运动语义错）。
- hinge barrel/knuckle 不包 jamb pintle（叶漂浮，无承载路径），或 ring 顶不包 boss（环漂浮脱落）。
- 高峰顶（`arched_top` / `gothic_lancet_top`）配方头 surround，圆弧/尖峰叶顶被 lintel soffit 穿切。
- `knocker_ring_on_boss` 缺 `strike_boss`，或 ring joint 只单向（无法向下摆击靶），knocker 语义失效。
- `strap_studs_row` 配非 strap bracing（螺栓排无 strap 可铆，悬空）。
- 高 plank_count 时 clavos 网格列落在板缝/穿 ledge/穿 escutcheon。
- closed pose（q=0）叶体不落在 jamb 之间或穿门槛 stoop。
- 形态只靠 palette/尺寸变化，A-F 拓扑无区别。
- slide bolt rod 在行程中脱出 keeper（插入未保持）。

## 与相邻类别的边界
- 不该混入 `door` / `door_other`：现代平整 panel/glazed/louvered 门，把手是 knob/lever/bar-pull 绕 spindle；plank_ring_door 是 rustic 竖木板 + 锻铁挂环 + 石门洞。
- 不该混入 `gate` / `folding_gate` / `scifi_gate`：通透格栅 / 多扇 / sci-fi；本类单扇实木板叶竖轴摆动。
- 不该混入 `sliding_door` / `folding_door` / `trap_door`：主运动为竖轴 REVOLUTE，不是滑移/折叠/翻板。
- 不该混入 `double_door`：本类单叶。
- 不该混入 `wall_safe_with_hinged_door_and_dial`：金属箱 + 拨盘，非建筑石洞木门。
- 不该混入 generic plank-door / thumb-latch 类别：把挂环换成 Suffolk thumb-latch（`thumb_lever` + `grip_handle` + `latch_bar`，无 ring_pull part）的竖木板门虽与本类几乎同形，但**没有挂环拉手**，丢失本小类「with a ring pull」的定义性 hero（`rec_plank_ringpull_door_var_thumb_latch` 即此例，故未采纳为本类 candidate）。

## 模板实现备注（可选）
- 共享 helper：box-per-plank 循环（A）、`_v_groove_plank_mesh`（F）、`_make_clavo_stud`/`_CLAVO_STUD`（E grid）、`_spade_strap_mesh`（B strap + E strap-row）、`_emit_ledge_assembly`（B z-brace）、`_build_ring_pull` torus（D）、`_build_stone_surround` + `jamb_pintle_{tag}`（root）；新增叶顶 helper：`arch_z_at`（C arched）、`_lancet_arch_z` + `_make_arch_plank_solid` + `_make_arch_board_solid`（C gothic lancet）、`_camber_z_at` + per-plank shoulder-chamfer profile（C shoulder）；knocker 的 `strike_boss` 构造（D knocker）。
- 需特别注意的 InterfaceSpec / MatingContract：(1) leaf hinge barrel ↔ jamb pintle 的 captured-pin（element-scoped allow_overlap：barrel vs pintle、barrel vs jamb stone）；(2) ring vs boss 的 captured ring-on-boss allow_overlap；(3) knocker 时 ring vs `strike_boss` 的 rest-contact allow_overlap（knocker 机构的功能性接触）；(4) escutcheon/ledge/strap/keeper vs leaf 面的 mounted-flush allow_overlap；(5) slide bolt rod vs keeper 的 captured slide allow_overlap（present 时）。复制这些 allow_overlap 到组合后的所有相应 element。
- gap-fill 已落地：先前 planned 的 4 个候选已建成（rating=5）。`gothic_pointed_top`(S12) / `shouldered_camber_top`(S13) 已并入 Slot C（C=2→4），`knocker_ring`(S14) 已并入 Slot D（D=2→3），核心 slot 组合升至 1152（×N=4608）。`thumb_latch`（`rec_plank_ringpull_door_var_thumb_latch`）**有 on-disk model.py 但保持排除**：它移除挂环（无 `ring_pull`/`ring`/`ring_backplate`/`ring_boss`、无 `leaf_to_ring`）改 Suffolk thumb-latch（`thumb_lever` part + `leaf_to_thumb_lever` REVOLUTE + `grip_handle`/`pivot_pin`/`latch_bar`），属相邻 generic plank-door / thumb-latch 类别，不进本 spec seed domain；其 helper（`_build_thumb_lever`、grip/latch 构造）可作未来 generic-plank-door 模板素材，但不可在本类用作 ring 替代。
- open-parent 的四角星 escutcheon（`_build_ring_plate_shape` S2 `model.py:L549-L591`）与 starplate 的 quatrefoil（S8）是 `ring_on_star_plate` 的两个实现细节，模板可任选其一或都作 star 子风格。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；未进入模板实现阶段。gap-fill 更新（4 个新建 5★ 变体）：Slot C 2→4（加 `gothic_lancet_top` S12、`shouldered_camber_top` S13，降级解除）、Slot D 2→3（加 `knocker_ring_on_boss` S14，降级解除）；核心 slot 组合 384→1152、×N 1536→4608。`thumb_latch`（`rec_plank_ringpull_door_var_thumb_latch`）虽 on-disk 但**移除挂环、出本小类「with a ring pull」身份**，已逐条判定排除（记入相邻类别边界 + 模板实现备注，不进 seed domain）。仅 Slot F 仍 2 candidate（flat / v_groove，板缝次级外观轴，无更多 on-disk seam 样本，降级理由保留）。palette_style 6 组为设计扩展（样本仅 1 组配色）。|
