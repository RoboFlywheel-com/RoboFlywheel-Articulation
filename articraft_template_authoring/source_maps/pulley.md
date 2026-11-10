# Pulley — SourceMap

export_category: pulley

The authoritative source pool is `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
One reference-backed original establishes the compact fixed-plate pulley; nine fork records
contribute explicit frame, mounting, secondary-eye, sheave-profile, and multiplicity evidence.
This map records semantic choices only and contains no copied source or dependency closure.

sync_records:
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4
  - rec_0611_pulley_var_frame_enclosed_shell
  - rec_0611_pulley_var_frame_hinged_side_gate_v3
  - rec_0611_pulley_var_mount_clevis
  - rec_0611_pulley_var_mount_closed_eye
  - rec_0611_pulley_var_mount_swivel_hook
  - rec_0611_pulley_var_secondary_becket
  - rec_0611_pulley_var_sheave_count_2
  - rec_0611_pulley_var_sheave_count_3
  - rec_0611_pulley_var_sheave_profile_narrow_v

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|
| frame_construction | open_cheeks | fixed frame | `rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4/rev_000001` | `model.py:L36-L85` | accepted | One connected countersunk plate, twin rounded bearing cheeks, captured transverse axle and outside retainers. |
| frame_construction | enclosed_shell | fixed frame | `rec_0611_pulley_var_frame_enclosed_shell/rev_000001` | `model.py:L42-L112` | accepted | Rounded hollow shell with a true wheel chamber, integral bearing walls and opposed rope-entry windows. |
| frame_construction | hinged_gate | articulated frame | `rec_0611_pulley_var_frame_hinged_side_gate_v3/rev_000001` | `model.py:L39-L173`; `model.py:L205-L284` | accepted | One rigid cheek plus a full slotted side cheek, captured rear hinge, front latch and approximately 95-degree opening travel. |
| mount_interface | fixed_plate | fixed mounting interface | `rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4/rev_000001` | `model.py:L39-L49` | accepted | Elongated filleted plate with two real countersunk fastener holes. |
| mount_interface | clevis | pinned mounting interface | `rec_0611_pulley_var_mount_clevis/rev_000001` | `model.py:L37-L126` | accepted | Reinforced bridge, paired clevis ears, true rigging gap and visible transverse attachment pin. |
| mount_interface | closed_eye | fixed hanging interface | `rec_0611_pulley_var_mount_closed_eye/rev_000001` | `model.py:L37-L113` | accepted | Thick closed eye with a true through-opening and broad neck joining both load cheeks. |
| mount_interface | swivel_hook | articulated hanging interface | `rec_0611_pulley_var_mount_swivel_hook/rev_000001` | `model.py:L35-L137`; `model.py:L168-L229` | accepted | Captured vertical swivel stem, bearing bridge and curved load hook with a real open throat. |
| sheave_profile | deep_u | rope sheave | `rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4/rev_000001` | `model.py:L88-L115` | accepted | Seven-point lathed outer profile forms raised rims, a broad deep-U groove, solid web and true axle bore. |
| sheave_profile | narrow_v | cable sheave | `rec_0611_pulley_var_sheave_profile_narrow_v/rev_000001` | `model.py:L90-L117` | accepted | Symmetric narrow V trough with raised retaining flanges and the same true axle bore. |
| secondary_module | none | absent optional structure | `rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4/rev_000001` | `model.py:L118-L159` | accepted | Baseline pulley has no secondary rope anchor. |
| secondary_module | becket_eye | fixed rope anchor | `rec_0611_pulley_var_secondary_becket/rev_000001` | `model.py:L122-L175` | accepted | Reinforced neck and closed becket with a true opening, placed outside the wheel and rope-path envelope. |
| sheave_count | 1 | multiplicity evidence | `rec_use-the-attached-reference-image-as-the-primary-_20260712_064522_904114_797df9d4/rev_000001` | `model.py:L142-L157` | accepted | One independently rotating sheave on the captured X-axis pin. |
| sheave_count | 2 | multiplicity evidence | `rec_0611_pulley_var_sheave_count_2/rev_000001` | `model.py:L38-L96`; `model.py:L129-L174` | accepted | Two indexed sheaves at 14.9 mm pitch; cheek spacing, body width, axle and center washer adapt with N. |
| sheave_count | 3 | multiplicity evidence | `rec_0611_pulley_var_sheave_count_3/rev_000001` | `model.py:L38-L107`; `model.py:L140-L184` | accepted | Three indexed sheaves at 15.5 mm pitch with widened cheeks, longer axle and four thrust washers. |

## Semantic decisions

- `frame_construction`, `mount_interface`, `sheave_profile`, and `secondary_module` are the four
  non-N slots. Their interfaces are simple enough that every cross-product combination can be
  supported through derived bridge, shell, cheek, latch, and becket geometry; no gate is used.
- `sheave_count` is the only multiplicity axis. N controls stack width, cheek centers, shell cavity,
  axle length, retainer positions, thrust washers, gate offset, and one indexed X-axis joint per wheel.
- The original fixed mounting plate is not fused permanently into every frame candidate. Its
  countersunk-hole language is retained by the `fixed_plate` mount candidate, while the frame owns
  the wheel chamber and bearing support.
- All wheel joints rotate through their bore center about X. The hinged cheek rotates about its rear
  Z-axis, and the swivel hook rotates about its captured vertical Z-axis. New-template axis mates
  are mandatory for each of these joints.
- Independent dimensions are limited to a conservative overall scale and sheave proportion family.
  Bore, axle, clearances, host capacity and opening dimensions are derived rather than sampled
  independently.
