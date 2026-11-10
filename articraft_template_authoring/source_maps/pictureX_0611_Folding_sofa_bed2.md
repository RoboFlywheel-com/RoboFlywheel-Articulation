# pictureX_0611_Folding_sofa_bed2 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_sofa_bed2
picture_category: 0611
picture_subcategory: Folding_sofa_bed2
category_scope: A reclining convertible sofa — one upholstered carcass with fixed arms, and per seat unit a backrest that reclines rearward plus a legrest that swings up and forward from under the seat front, with a recline control on the outer arm. The reclining back + pop-out legrest pair is the fixed category identity; carriage-borne sleeper mechanisms belong to pictureX_0611_Folding_sofa_bed1.

sync_records:
  - rec_picturex0611_folding_sofa_bed2_bifold_mattress_panels
  - rec_picturex0611_folding_sofa_bed2_chaise_extension
  - rec_picturex0611_folding_sofa_bed2_deployable_front_legs
  - rec_picturex0611_folding_sofa_bed2_metal_futon_frame
  - rec_picturex0611_folding_sofa_bed2_slatted_deck
  - rec_picturex0611_folding_sofa_bed2_split_ratchet_back
  - rec_picturex0611_folding_sofa_bed2_storage_base
  - rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36/rev_000001 | reviewed | used | Image-grounded base for 001.png: an upholstered two-seat recliner with a reclining backrest, a pop-out legrest and a recline control on the outer arm. Supplies the host mechanism plus single_back, plinth_base, upholstered_deck and pad_legrest, and shows the per-seat repetition that the multiplicity captures. |
| rec_picturex0611_folding_sofa_bed2_split_ratchet_back/rev_000001 | reviewed | used | Splits the back into independently hinged ratchet panels with visible side plates. Source for the split_ratchet back build. |
| rec_picturex0611_folding_sofa_bed2_bifold_mattress_panels/rev_000001 | reviewed | used | Rebuilds the back as two hinged mattress panels that flatten into one surface. Source for the bifold_panels back build. |
| rec_picturex0611_folding_sofa_bed2_metal_futon_frame/rev_000001 | reviewed | used | Replaces the upholstered plinth with an exposed tubular metal futon frame. Source for the metal_futon base style. |
| rec_picturex0611_folding_sofa_bed2_storage_base/rev_000001 | reviewed | used | Puts the seat on a boxy storage plinth with a front door panel. Source for the storage_base base style. |
| rec_picturex0611_folding_sofa_bed2_slatted_deck/rev_000001 | reviewed | used | Replaces the upholstered seat deck with loop-emitted slats over the frame. Source for the slatted_deck seat build. |
| rec_picturex0611_folding_sofa_bed2_chaise_extension/rev_000001 | reviewed | used | Lengthens the legrest into a full chaise pad with side bolsters. Source for the chaise_legrest style. |
| rec_picturex0611_folding_sofa_bed2_deployable_front_legs/rev_000001 | reviewed | reference_only | Adds fold-out front legs under the extended cushion. They only carry load once the seat converts to a flat bed, which this reclining host does not do — the legrest itself carries the front here — so they would be an unsupported slot. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| back_build | single_back | seat backrest | rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36/rev_000001 | model.py:L279-L329 | structure | One upholstered back pad with a piped top edge on a single hinge. |
| back_build | split_ratchet | seat backrest | rec_picturex0611_folding_sofa_bed2_split_ratchet_back/rev_000001 | model.py:L359-L432 | structure | Back split into stacked panels with exposed side ratchet plates and notches. |
| back_build | bifold_panels | seat backrest | rec_picturex0611_folding_sofa_bed2_bifold_mattress_panels/rev_000001 | model.py:L226-L300 | structure | Back built as two hinged mattress panels with a seam bead between them. |
| base_style | plinth_base | carcass base | rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36/rev_000001 | model.py:L126-L278 | structure | Upholstered plinth with a recessed toe kick and short block feet. |
| base_style | metal_futon | carcass base | rec_picturex0611_folding_sofa_bed2_metal_futon_frame/rev_000001 | model.py:L237-L381 | structure | Exposed tubular metal futon frame with open side rails and splayed tube legs. |
| base_style | storage_base | carcass base | rec_picturex0611_folding_sofa_bed2_storage_base/rev_000001 | model.py:L128-L315 | structure | Boxy storage plinth with a recessed front door panel and pull. |
| deck_build | upholstered_deck | seat deck | rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36/rev_000001 | model.py:L126-L278 | structure | Padded seat cushion with a welted front edge over a closed deck. |
| deck_build | slatted_deck | seat deck | rec_picturex0611_folding_sofa_bed2_slatted_deck/rev_000001 | model.py:L127-L291 | structure | Open deck of repeated transverse slats across the side rails. |
| legrest_style | pad_legrest | seat legrest | rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36/rev_000001 | model.py:L330-L399 | structure | Short padded legrest panel with a welted edge on its swing hinge. |
| legrest_style | chaise_legrest | seat legrest | rec_picturex0611_folding_sofa_bed2_chaise_extension/rev_000001 | model.py:L473-L543 | structure | Long chaise pad with raised side bolsters and a deeper cushion. |
