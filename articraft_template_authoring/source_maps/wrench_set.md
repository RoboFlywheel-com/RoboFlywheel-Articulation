# Wrench set — SourceMap

export_category: wrench_set

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
This rebuild treats each tool profile and its source-compatible carrier as one coherent
`set_family`. A wrench profile may vary, but the result must remain visibly and mechanically a
graduated wrench/key set rather than a generic tool placed in an arbitrary container.

sync_records:
  - rec_0611__wrench_set__001_png_867fcfc363504a5081e23c143d60d7fd
  - rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa
  - rec_0611_wrench_set_var_tool_family_ratcheting_combination
  - rec_0611_wrench_set_var_tool_family_flare_nut_set
  - rec_0611_wrench_set_var_tool_count_5
  - rec_0611_wrench_set_var_tool_count_8
  - rec_0611_wrench_set_var_tool_count_10

## Accepted coherent set families

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| set_family | l_hex_key_slot_holder | molded wedge slot set | rec_0611__wrench_set__001_png_867fcfc363504a5081e23c143d60d7fd/rev_000001 | model.py:L35-L135; model.py:L206-L291 | accepted | true hex sweeps, L bends, sloped molded carrier and one real hex socket per key |
| set_family | l_flare_nut_slot_holder | molded wedge flare-nut set | rec_0611_wrench_set_var_tool_family_flare_nut_set/rev_000001 | model.py:L35-L174; model.py:L245-L346 | accepted | source L sweep plus slotted through-bore flare-nut head in the source wedge carrier |
| set_family | combination_hanging_rack | handled hanging set | rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa/rev_000001 | model.py:L33-L158; model.py:L161-L258 | accepted | blue handle opening, molded socket beam, graduated fan and forged open/ring tools |
| set_family | ratcheting_combination_hanging_rack | handled hanging set | rec_0611_wrench_set_var_tool_family_ratcheting_combination/rev_000001 | model.py:L33-L195; model.py:L198-L298 | accepted | source blue carrier plus enlarged ratchet housing, through bore and reversal detail |
| set_family | double_open_end_hanging_rack | handled hanging set | rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa/rev_000001 | model.py:L33-L97; model.py:L100-L158 | accepted-derived | source forged shaft/open-jaw construction, adapted to two true open jaws and neck snap clips |
| set_family | double_box_end_hanging_rack | handled hanging set | rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa/rev_000001 | model.py:L33-L97; model.py:L100-L158 | accepted-derived | source ring construction used at both ends with real polygonal through bores |
| set_family | offset_ring_hanging_rack | handled hanging set | rec_0611__wrench_set__002_png_dc0b13c7c9ca4f21af11d049fae266fa/rev_000001 | model.py:L33-L97; model.py:L100-L158 | accepted-derived | source ring-ended forged tool adapted with visibly offset necks and two real bores |

## Multiplicity and source-derived layout

- `tool_count = 5 | 8 | 10`, applied to `set_family`.
- N is the total number of tools in the asset. Every family emits exactly N wrench/key parts,
  N independent extraction joints and N compatible seats, bosses or neck clips.
- The molded carrier width, socket/clip count, pitch, fan angles and graduated tool sizes derive
  from N. The N records provide the accepted capacities:
  `rec_0611_wrench_set_var_tool_count_5/rev_000001`,
  `rec_0611_wrench_set_var_tool_count_8/rev_000001`, and
  `rec_0611_wrench_set_var_tool_count_10/rev_000001`.

## Parameters and derivations

- `tool_length_m` is candidate-local and metre-valued.
- L-key families use 0.15–0.25 m long legs. Stock size, bend radius, short-arm reach, wedge height
  and extraction travel derive from length and size rank.
- Hanging families use 0.20–0.34 m forged tools. Head diameter, shaft taper, holder pitch, carrier
  width and fan spread derive from length, N and size rank.

## Category identity and motion

- L families require exactly one `slot_holder`, N `wrench` parts, N real hexagonal holder bores
  and N vertical prismatic extraction joints. No external universal base is added.
- Hanging families require exactly one blue `hanging_holder`, N `wrench` parts and N independent
  prismatic extraction joints along each tool's fanned long axis.
- Ring-ended families use a real through bore around a molded boss. Double-open tools use a neck
  snap clip on the same blue carrier and do not invent a ring socket.
- Open jaws are cut crescents, ring/box heads contain real polygonal through bores, ratchet heads
  retain a toothed bore and reversal feature, and offset-ring tools have visible offset necks.

## Rejected decompositions

- Independent `tool_system × holder_system` is rejected because it creates source-incoherent
  combinations.
- Roll pouch, clamshell, sliding tray, tilting rack and socket-set candidates are removed.
- Dark solid cylinders are not accepted as holes. Box-only fake jaws and decorative material-only
  tool variants are not accepted.
