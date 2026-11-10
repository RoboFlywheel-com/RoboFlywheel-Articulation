# Technology_Audio_Device — SourceMap

source_map_schema: 1
export_category: Technology_Audio_Device
picture_category: Technology
picture_subcategory: Audio_Device
category_scope: Tabletop and portable radio-style audio devices built as one enclosure whose front face carries a speaker grille field and a control strip, plus optional carry-bail and telescoping-antenna mechanisms mounted on the enclosure top.

sync_records:
  - rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653
  - rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240
  - rec_audio_device_var_button_count_high
  - rec_audio_device_var_button_count_low
  - rec_audio_device_var_dual_stereo_speaker
  - rec_audio_device_var_tombstone_body
  - rec_audio_device_var_vertical_bar_grille
  - rec_retro-vintage-portable-transistor-radio-bronze-a_20260605_173810_150349_43796658
  - rec_silver-portable-cd-radio-boombox-oval-body-with-_20260605_173820_379190_c648725c

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653/rev_000001 | reviewed | used | Soft-cornered portable slab with a perforated black speaker mesh behind a rounded bezel, a fixed arched carry bail on two top saddles, and a side-swivelling telescoping whip antenna. |
| rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | reviewed | used | Wide wooden tabletop cabinet: one recessed front field with rails and horizontal cloth ribs above a tuning dial, two fluted rotary knobs on the lower strip, and an uninterrupted decorated top with no carry bail or antenna. |
| rec_audio_device_var_button_count_high/rev_000001 | reviewed | used | Same enclosure as the tan portable radio but the push-button strip is emitted by an index-general loop; it proves the button row is a repeat mechanism rather than five hand-placed keys. |
| rec_audio_device_var_button_count_low/rev_000001 | reviewed | reference_only | Low-count end of the identical push-button loop (three keys); it confirms the multiplicity range but adds no structurally distinct component. |
| rec_audio_device_var_dual_stereo_speaker/rev_000001 | reviewed | used | Replaces the single off-centre speaker with two symmetric recessed speaker fields, moving the key tray to the centre between them. |
| rec_audio_device_var_tombstone_body/rev_000001 | reviewed | used | Upright arched-top tombstone cabinet extruded from an XZ profile, taller than wide, with decorative side trim and no antenna socket. |
| rec_audio_device_var_vertical_bar_grille/rev_000001 | reviewed | used | Keeps the cabinet but replaces the horizontal cloth ribs with evenly pitched vertical bars spanning the grille opening. |
| rec_retro-vintage-portable-transistor-radio-bronze-a_20260605_173810_150349_43796658/rev_000001 | reviewed | used | Bronze transistor radio contributing a swept folding carry bail on two pivot bosses and a rear two-stage telescoping mast that rakes about a horizontal axis. |
| rec_silver-portable-cd-radio-boombox-oval-body-with-_20260605_173820_379190_c648725c/rev_000001 | reviewed | used | Rounded-square boombox slab standing on rubber feet, with a recessed transport tray of pressable playback keys and continuously spinning deck knobs. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| cabinet_form | landscape_cabinet | wide tabletop enclosure | rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | model.py:L32-L40; model.py:L72-L97 | structure | Wide softly radiused rectangular cabinet whose front face is set back behind a framed recess and whose top is a finished flat deck. |
| cabinet_form | portable_slab | portable rounded slab enclosure | rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653/rev_000001 | model.py:L32-L54; model.py:L96-L103 | structure | Small all-round filleted slab with a shallow raised control ledge on the top face, proportioned for one-hand carry rather than a shelf. |
| cabinet_form | tombstone_upright | upright arched-top cabinet | rec_audio_device_var_tombstone_body/rev_000001 | model.py:L26-L61; model.py:L95-L101 | structure | A rectangle capped by a semicircular arch is extruded along the depth axis, giving a cabinet taller than it is wide with a curved crown. |
| cabinet_form | boombox_slab | rounded-square boombox slab | rec_silver-portable-cd-radio-boombox-oval-body-with-_20260605_173820_379190_c648725c/rev_000001 | model.py:L119-L154; model.py:L185-L199 | structure | Plan-view rounded-square prism with heavily filleted vertical corners, a flat top deck, and four rubber feet lifting it off the ground. |
| grille_style | horizontal_ribbed | ribbed cloth grille field | rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | model.py:L140-L178 | structure | Perimeter rails enclose a stack of evenly pitched horizontal ribs whose count follows the field height. |
| grille_style | perforated_mesh | perforated metal grille field | rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653/rev_000001 | model.py:L56-L94 | structure | A dark backing plate, a rounded-rect bezel and a genuinely perforated panel with staggered holes replace the rib stack. |
| grille_style | vertical_bar | vertical slat grille field | rec_audio_device_var_vertical_bar_grille/rev_000001 | model.py:L140-L182 | structure | The same opening is filled by evenly pitched vertical bars running top to bottom, with the bar count derived from the field width. |
| speaker_layout | single_field | one full-width speaker field | rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | model.py:L132-L164 | structure | One circular cone shadow sits behind one wide grille opening that spans most of the front face. |
| speaker_layout | dual_stereo | two symmetric speaker fields | rec_audio_device_var_dual_stereo_speaker/rev_000001 | model.py:L201-L232 | structure | Two mirrored speaker bores, baskets, surrounds and bezels are emitted at symmetric offsets, halving each opening and freeing the centre. |
| control_deck | rotary_knob_bank | rotary control bank | rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | model.py:L244-L288 | structure+motion | Fluted skirted knob caps seat on the lower control strip and each turns about its own front-facing rotation axis. |
| control_deck | push_button_row | pressable button row | rec_audio_device_var_button_count_high/rev_000001 | model.py:L96-L103; model.py:L171-L191 | structure+motion | A darker control strip carries an index-general loop of rounded keycaps, each its own part on a short prismatic press joint. |
| control_deck | transport_key_deck | recessed transport key deck | rec_silver-portable-cd-radio-boombox-oval-body-with-_20260605_173820_379190_c648725c/rev_000001 | model.py:L299-L327; model.py:L362-L390 | structure+motion | Small playback keys press inward from the floor of a recessed tray, flanked by continuously spinning knobs on the same deck. |
| carry_handle | molded_top_lip | integrated top trim, no bail | rec_a-wooden-retro-tabletop-radio-a-horizontal-recta_20260624_122658_140987_c610b240/rev_000001 | model.py:L80-L88 | structure | The cabinet top is a finished decorated deck with raised trim strips and carries no separate handle link. |
| carry_handle | fixed_bail | fixed arched carry bail | rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653/rev_000001 | model.py:L136-L169 | structure | Two saddles on the top face carry a swept rounded-rect arch as one separate rigidly mounted link. |
| carry_handle | folding_bail | folding carry bail | rec_retro-vintage-portable-transistor-radio-bronze-a_20260605_173810_150349_43796658/rev_000001 | model.py:L190-L243; model.py:L403-L419 | structure+motion | The swept bail has real pivot knuckles seated on two top bosses and swings about a horizontal cabinet-width axis. |
| antenna_module | no_antenna | blank antenna position | rec_audio_device_var_tombstone_body/rev_000001 | model.py:L103-L123 | structure | The cabinet carries only trim on its shell; no socket, mast or moving antenna link exists. |
| antenna_module | side_swivel_whip | side-raking telescoping whip | rec_a-tan-beige-minimalist-retro-portable-radio-a-re_20260624_122658_140174_25291653/rev_000001 | model.py:L105-L116; model.py:L193-L253 | structure+motion | A brass boss carries a knuckle that rakes sideways about the depth axis and a thin rod that telescopes inside the sleeve. |
| antenna_module | rear_telescoping_mast | rear-raking telescoping mast | rec_retro-vintage-portable-transistor-radio-bronze-a_20260605_173810_150349_43796658/rev_000001 | model.py:L246-L269; model.py:L421-L455 | structure+motion | A socket block on the rear of the top deck carries a thick lower tube raking about the cabinet-width axis and a thinner upper segment sliding inside it. |
