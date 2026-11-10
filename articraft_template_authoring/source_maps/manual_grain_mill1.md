# Manual grain mill 1 — SourceMap

export_category: manual_grain_mill1

Authoritative records live under
`<ARTI_SKILL_ROOT>/articraft_data/data/records`. This category is the
source-image stone rotary quern: a horizontal lower quern and upper runner carried
by exposed timberwork, with a vertical grinding axis and a detailed side crank.
The directed variants alter local components while preserving that identity, so
the template decomposes them into independent component slots rather than a
single whole-machine family.

sync_records:
  - rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07
  - rec_0611_manual_grain_mill1_var_faceted_runner_feed_profile
  - rec_0611_manual_grain_mill1_var_offset_counterweighted_crank
  - rec_0611_manual_grain_mill1_var_rim_profile_stepped
  - rec_0611_manual_grain_mill1_var_runner_profile_funnel
  - rec_0611_manual_grain_mill1_var_stand_braced
  - rec_0611_manual_grain_mill1_var_trestle_stand_splayed
  - rec_0611_manual_grain_mill_var_quern_stand_low_profile
  - rec_0611_manual_grain_mill_var_rim_count_10

## Accepted component candidates

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| support_frame | straight_four_leg | support skeleton | timber load path | rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07/rev_000001 | model.py:L103-L167 | accepted source-backed | four square legs and two upper timber rails directly carry the circular lower quern |
| support_frame | braced_four_leg | support skeleton | braced timber load path | rec_0611_manual_grain_mill1_var_stand_braced/rev_000001 | model.py:L84-L96; model.py:L117-L223 | accepted source-backed | source four-leg frame gains joined knee braces, pegged joints and a low transverse stretcher |
| support_frame | splayed_trestle | support skeleton | trestle load path | rec_0611_manual_grain_mill1_var_trestle_stand_splayed/rev_000001 | model.py:L84-L102; model.py:L124-L210 | accepted source-backed | outward-splayed legs, paired trestle heads/ties and a central stretcher form a visibly different timber skeleton |
| support_frame | low_skid_cradle | support skeleton | skid-and-bearer load path | rec_0611_manual_grain_mill_var_quern_stand_low_profile/rev_000001 | model.py:L103-L213 | accepted source-backed | two long skids and two cross-bearers support the same quern at workbench height |
| discharge_system | open_sloped_board | discharge path | open timber chute | rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07/rev_000001 | model.py:L20-L49; model.py:L143-L149 | accepted source-backed | connected lower-stone outlet notch/spout feeds an exposed sloped timber board |
| discharge_system | bridge_supported_chute | discharge path | lipped supported chute | rec_0611_manual_grain_mill_var_quern_stand_low_profile/rev_000001 | model.py:L162-L191 | accepted source-backed | sloped board is retained by a transverse support bridge and receives side lips |
| rim_profile | rough_segmented_blocks | catch-rim profile | repeated stone blocks | rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07/rev_000001 | model.py:L109-L123 | accepted source-backed | broad hand-dressed rectangular stone blocks form an interrupted catch rim around the runner |
| rim_profile | fitted_stepped_voussoirs | catch-rim profile | repeated tapered stone blocks | rec_0611_manual_grain_mill1_var_rim_profile_stepped/rev_000001 | model.py:L20-L103; model.py:L157-L231 | accepted source-backed | low tapered voussoirs derive from a shared inner/outer radius and preserve the rear discharge opening |
| runner_profile | shallow_circular_funnel | runner/feed profile | circular runner stone | rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07/rev_000001 | model.py:L52-L64 | accepted source-backed | thick circular runner with a true central eye and broad shallow conical feed depression |
| runner_profile | terraced_circular_feed | runner/feed profile | terraced circular runner | rec_0611_manual_grain_mill1_var_runner_profile_funnel/rev_000001 | model.py:L52-L132 | accepted source-backed | full-thickness shouldered runner with stepped hand-carved feed terraces, true throat and radial dressing marks |
| runner_profile | faceted_polygonal_feed | runner/feed profile | faceted runner stone | rec_0611_manual_grain_mill1_var_faceted_runner_feed_profile/rev_000001 | model.py:L52-L78 | accepted source-backed | fourteen-sided dressed runner and polygonal feed funnel visibly change both perimeter and inlet profile |
| drive | straight_socket_crank | hand-drive form | timber crank and spinning grip | rec_picturex_0611__manual_grain_mill__001__png_c673835d54464d63a16b129708043f07/rev_000001 | model.py:L67-L81; model.py:L169-L229 | accepted source-backed | timber arm, bored side socket, washer, real pin and tapered bored wooden grip preserve the source crank stack |
| drive | offset_counterweighted_crank | hand-drive form | offset balanced crank and spinning grip | rec_0611_manual_grain_mill1_var_offset_counterweighted_crank/rev_000001 | model.py:L67-L96; model.py:L187-L264 | accepted source-backed | laterally offset crank is balanced by an opposed forged arm and oval counterweight while retaining the free grip |

## Multiplicity

- `rim_segment_count = 10 | 14 | 18`, applied to `rim_profile`.
- The explicit N source is
  `rec_0611_manual_grain_mill_var_rim_count_10/rev_000001`
  (`model.py:L20-L41; model.py:L127-L250`). Its variant intent marks the
  change as N multiplicity and records the source `range(14)` behavior.
- Every N emits exactly N indexed `rim_profile__<candidate>__segment_<index>`
  visuals. Segment angular width and centers derive from N over the usable arc;
  the rear discharge opening remains deterministic rather than being filled by
  a denser count.

## Parameters and derivations

- `quern_radius_m = 0.28–0.34 m` drives the lower stone, grinding bed, rim
  radii, timber footprint and discharge width.
- `runner_radius_ratio = 0.62–0.70 ratio` drives runner radius, feed profile,
  radial rim clearance and crank socket location.
- `support_height_scale = 0.90–1.10 ratio` scales each selected support
  candidate around its own source-like nominal height; the grinding surface,
  bearings, discharge and all timber contacts are re-derived.
- `crank_reach_ratio = 1.55–1.85 ratio` drives arm reach, pin location and
  opposed counterweight radius while maintaining clearance above the catch rim.
- The lower quern has a real central bore. A smaller fixed metal pivot and an
  annular bearing seat are derived from that bore; the runner eye remains
  larger than the bearing envelope.

## Interfaces and bindings

- `support_frame.grinding_axis` provides the vertical axis at the derived
  grinding-bed height; `runner_profile.rotation_axis` consumes it.
- `runner_profile.grip_axis` provides the vertical crank-pin axis;
  `drive.grip_axis` consumes it.
- Both continuous joints are solved with `AxisInterface`/`mate_axes` and
  registered. The actual hierarchy remains source-like
  `support frame -> runner -> crank grip`.
- Rim inner radius derives from runner radius plus radial running clearance.
  Support footprint derives from lower-quern radius, and discharge placement
  derives from the lower-stone outlet and selected support height.

## Category identity

- Exactly one exposed timber `support_frame`, one stone `runner_stone` and one
  wooden `crank_grip` part are present.
- The runner is coaxial with and seated over the lower quern; it has a true feed
  opening and remains radially inside the interrupted catch rim.
- The lower quern retains the connected rear outlet path. All support families
  visibly carry the stone rather than surrounding it with a cabinet or frame.
- The crank retains its arm, socket, washer, pin and tapered bored grip. The
  counterweighted candidate adds structure without deleting those details.

## Rejected decompositions

- The records are not accepted as nine complete-machine candidates. Their
  unchanged quern, runner, stand and crank sections are shared source context.
- Records descending from the separate `manual_grain_mill2` source image are
  excluded; its vertical wheel/burr housing is a different category.
- A closed rectangular machine body, unsupported floating stones, a shaft
  outside the central eye, solid fake holes, and overlap/isolated-part
  allowances are rejected.
