# 0611 / elevator_button_panel — template source map
status: P3 confirmed; 8 HQ samples synced to downstream arti-template with rating=5
pattern: mounted panel enclosure + repeated selection controls + door/emergency controls
parents: 2 confirmed image-conditioned origins (`001.png`, `002.png`)
underfilled_reason: none — 2 origins + 6 accepted forks = 8 candidate anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: elevator_button_panel
  core_identity: mounted elevator control panel with repeated selectable controls and at least one physically articulated control
  must_keep: [panel enclosure, elevator control layout, supported actuators, door or emergency control]
  must_not_become: [generic keypad, industrial control cabinet, single hall-call plate]
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline layout | two image-backed portrait elevator panels | mixed | confirmed origins `001`, `002` | confirmed |
| actuator form | square tactile buttons in square guide wells | ③ | `rec_elevator_panel_var_square_buttons` | fork pass |
| floor-button count/layout | eight buttons in one vertical column | N | `rec_elevator_panel_var_single_column_8` | fork pass |
| enclosure form | low horizontal car console | ③ | `rec_elevator_panel_var_horizontal_console` | fork pass |
| selection topology | destination-entry keypad + confirm/cancel | ① | `rec_elevator_panel_var_destination_keypad` | fork pass |
| actuator mechanism | flush glass touch array + mechanical safety/door controls | ② | `rec_elevator_panel_var_glass_touch_hybrid` | fork pass |
| bank topology | separated low-zone/high-zone button banks | ① | `rec_elevator_panel_var_split_zone_banks` | fork pass |

## Multiplicity / Copy Logic
- count parameter: `floor_button_count`; explicit controlled sample `N=8` in a single column, supplemented by the two origin counts/layouts.
- repeated object: supported floor selector button; indexed naming and regular row/column placement; uniform prismatic actuation for mechanical buttons.
- suggested range: `N=4..24`, with row/column arrangement treated separately from raw count.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | direct floor grid, destination keypad, split zone banks |
| ② joint / mechanism | mechanical prismatic selectors versus touch-array hybrid retaining mechanical emergency/door controls |
| ③ primary form | round/square actuators and portrait/horizontal panel envelopes |
| ④ surface decoration | record-only: legends, braille, indicator rings, engraving |
| ⑤ proportion / travel | record-only: panel dimensions, button pitch, short actuator stroke |
| ⑥ material / finish | record-only: brushed stainless, black glass, illuminated polymer caps |

## Compatibility / Blocked
- No compatibility probe is needed for the eight-anchor pool.
- Generic keypad, industrial cabinet, and hall-call-only conversions are excluded as category drift.

## GATE P1 Verification (machine)
- accepted variants: 6; total candidate anchors: 8 (2 origins + 6 forks)
- independent compile: 6/6 success; `validation_level=full`; zero blocking signals
- articulation: 4–21 non-fixed joints per variant
- binding/promotion: all `workbench`; all bound to `0611 / elevator_button_panel`; parent lineage present
- human variant-pool confirmation: 2026-07-14
- downstream sync: 8/8 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
