# nutcracker — expanded reviewed SourceMap

export_category: nutcracker

sync_records:
  - rec_picturex_0611__nutcracker__001__png_72ea48d3b6864ac1bf2864aab225ca4d
  - rec_picturex_0611__nutcracker__002__png_ff76a040583c4f96bdf4d50be4fa4f16
  - rec_0611_nutcracker_var_mechanism_table_lever
  - rec_0611_nutcracker_var_mechanism_compound_link
  - rec_0611_nutcracker_var_mechanism_screw_press
  - rec_0611_nutcracker_var_jaw_form_deep_cup
  - rec_0611_nutcracker_var_jaw_form_tapered_serrated_cone
  - rec_0611_nutcracker_var_handle_long_curved
  - rec_0611_nutcracker_var_handle_ring_handle
  - rec_0611_nutcracker_var_capacity_indexed_jaw_stop
  - rec_0611_nutcracker_var_return_torsion_spring

## Accepted independent slots

The source pool contains complete mechanism families plus orthogonal jaw, handle,
capacity-stop and return-mechanism forks. The template keeps mechanism topology in
one structural slot and adapts the other source-backed interfaces locally, so every
combination remains buildable instead of being filtered by compatibility gates.

| slot | candidate | diversity_axis | source_type | record/revision | exact model.py:Lx-Ly | status | key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| mechanism | forged_wood_pliers | ①/③ forged plier | parent | `rec_picturex_0611__nutcracker__001__png_72ea48d3b6864ac1bf2864aab225ca4d/rev_000001` | `model.py:L1-L610` | accepted | forged arms, opposed jaws, walnut handles, transverse pivot |
| mechanism | stamped_serrated_pliers | ①/③ stamped lever | parent | `rec_picturex_0611__nutcracker__002__png_ff76a040583c4f96bdf4d50be4fa4f16/rev_000001` | `model.py:L1-L610` | accepted | stamped levers, serrated bowls and pivot hardware |
| mechanism | table_lever_press | ①/② table lever | forked_anchor | `rec_0611_nutcracker_var_mechanism_table_lever/rev_000001` | `model.py:L1-L518` | accepted | table base, lever arms and supported fulcrum |
| mechanism | compound_link_nutcracker | ①/② compound link | forked_anchor | `rec_0611_nutcracker_var_mechanism_compound_link/rev_000001` | `model.py:L1-L482` | accepted | paired links and offset load path |
| mechanism | screw_press | ①/② screw press | forked_anchor | `rec_0611_nutcracker_var_mechanism_screw_press/rev_000001` | `model.py:L1-L554` | accepted | stacked levers, screw press and captive pivot |
| jaw_profile | serrated_bowl | ③ serrated bowl | parent | `rec_picturex_0611__nutcracker__002__png_ff76a040583c4f96bdf4d50be4fa4f16/rev_000001` | `model.py:L1-L610` | accepted | inward serrated cavity |
| jaw_profile | deep_cup | ③ deep cup | forked_anchor | `rec_0611_nutcracker_var_jaw_form_deep_cup/rev_000001` | `model.py:L1-L399` | accepted | deeper rounded nut seat |
| jaw_profile | tapered_serrated_cone | ③ tapered cone | forked_anchor | `rec_0611_nutcracker_var_jaw_form_tapered_serrated_cone/rev_000001` | `model.py:L1-L491` | accepted | tapered serrated contact cone |
| handle_profile | standard_handle | ③ standard grip | parent | `rec_picturex_0611__nutcracker__001__png_72ea48d3b6864ac1bf2864aab225ca4d/rev_000001` | `model.py:L1-L610` | accepted | source walnut or stamped grip |
| handle_profile | long_curved_handle | ③ long curved grip | forked_anchor | `rec_0611_nutcracker_var_handle_long_curved/rev_000001` | `model.py:L1-L611` | accepted | long curved user handle |
| handle_profile | ring_handle | ③ ring grip | forked_anchor | `rec_0611_nutcracker_var_handle_ring_handle/rev_000001` | `model.py:L1-L397` | accepted | enclosed ring handle |
| capacity_stop | open_jaw | ② free opening | parent | `rec_picturex_0611__nutcracker__002__png_ff76a040583c4f96bdf4d50be4fa4f16/rev_000001` | `model.py:L1-L610` | accepted | open jaw shoulder |
| capacity_stop | indexed_jaw_stop | ② indexed capacity | forked_anchor | `rec_0611_nutcracker_var_capacity_indexed_jaw_stop/rev_000001` | `model.py:L1-L464` | accepted | indexed stop and contact shoulder |
| return_system | plain_pivot | ② manual return | parent | `rec_picturex_0611__nutcracker__001__png_72ea48d3b6864ac1bf2864aab225ca4d/rev_000001` | `model.py:L1-L610` | accepted | plain pivot hardware |
| return_system | torsion_spring | ② spring return | forked_anchor | `rec_0611_nutcracker_var_return_torsion_spring/rev_000001` | `model.py:L1-L503` | accepted | pivot torsion spring |

Representative source spans: parent `model.py:L1-L610`; mechanism forks use their
full `model.py:L1-L<end>` revisions (table 518, compound 482, screw 554), jaw
forks 399/491, handle forks 611/397, stop 464 and spring 503. These broad spans
are intentional because each fork changes both helpers and assembly code.

## Assembly and fidelity decisions

- All five mechanism families expose two cracking arms and a transverse Y pivot;
  local transition plates carry the jaw and handle candidates onto the selected
  family profile.
- Deep-cup and tapered-cone jaws are genuine cavity/profile changes, not material
  changes. Long-curved and ring handles remain connected to their arm bases.
- The indexed stop and torsion spring are fused into the fulcrum hardware part;
  they are not floating decorative parts and do not need compatibility exclusions.
- The complete structural domain is `5 × 3 × 3 × 2 × 2 = 180`. No multiplicity
  is used; continuous size/opening parameters remain outside core/raw accounting.
