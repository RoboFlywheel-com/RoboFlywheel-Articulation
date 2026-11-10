# Urban_Environment_bucket1 — SourceMap

source_map_schema: 1
export_category: Urban_Environment_bucket1
picture_category: Urban Environment
picture_subcategory: bucket1
category_scope: A hand-carried open sheet-metal fire bucket / utility pail consisting of one hollow revolved shell, one structurally finished mouth edge, two opposed riveted pivot ears and one steel-wire swing bail on a horizontal REVOLUTE axis. The shell may have a flat standing floor, a small standing pad under a rounded bowl, or the pointed lower closure of a hanging fire bucket. Mouth-edge construction, bail silhouette and riveted-ear form may vary independently while preserving the same open bucket and pivot semantics. Excludes wall racks, cradle rings, support frames, hook mounts, lids, fixed side grips, wooden staves and structural barrel hoops; those additions change the host/use topology instead of the bucket's own outline.

sync_records:
  - rec_bucket1_var_bands_three
  - rec_bucket1_var_bands_two
  - rec_bucket1_var_body_deep_cone
  - rec_bucket1_var_body_hemispherical
  - rec_bucket1_var_body_straight_pail
  - rec_bucket1_var_handle_fixed_grips
  - rec_bucket1_var_handle_no_handle
  - rec_bucket1_var_mount_hook_ring
  - rec_bucket1_var_mount_wall_bracket
  - rec_red-painted-sheet-metal-conical-fire-bucket-with_20260608_164532_434098_8f71e941
  - rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_bucket1_var_bands_three/rev_000001 | reviewed | rejected_category_drift | Three large proud hoops are a fork-added structural treatment absent from the reference image; repeating them makes the sheet-metal pail read like a banded hopper/barrel and is specifically outside the rebuilt category boundary. |
| rec_bucket1_var_bands_two/rev_000001 | reviewed | used | The full-height two-hoop treatment remains excluded, but its `_band_mesh` and repeated local-radius torus construction provide inspectable evidence for a compact double-bead mouth reinforcement confined to the bucket edge. |
| rec_bucket1_var_body_deep_cone/rev_000001 | reviewed | reference_only | Confirms that cone height and mouth radius can vary while the same shell/rim/ear/bail derivation remains valid, but its extreme aspect ratio is a continuous boundary of `pointed_fire_bucket`, not a second structural candidate. |
| rec_bucket1_var_body_hemispherical/rev_000001 | reviewed | used | Provides a genuinely curved quarter-circle wall profile with a small standing pad, distinct from every linear straight/tapered/conical wall family while retaining the common rim, ears and swing bail. |
| rec_bucket1_var_body_straight_pail/rev_000001 | reviewed | used | Provides an untapered vertical shell with equal mouth/base radius and flat floor, retaining the common rolled rim, opposed ears and swing bail. |
| rec_bucket1_var_handle_fixed_grips/rev_000001 | reviewed | used | The two-side-grip assembly remains excluded, but `_make_dloop_grip_mesh` provides inspectable evidence for a shouldered/angular wire path and its paired riveted lug construction; those local forms are reused while retaining one spanning swing bail. |
| rec_bucket1_var_handle_no_handle/rev_000001 | reviewed | rejected_category_drift | Replaces the open bucket and swing bail with a hinged lid mechanism, changing both mouth topology and motion identity. |
| rec_bucket1_var_mount_hook_ring/rev_000001 | reviewed | rejected_category_drift | Adds an axial suspension mount unrelated to the bucket shell outline. The rebuilt template intentionally emits no hook, hanger or external mounting system. |
| rec_bucket1_var_mount_wall_bracket/rev_000001 | reviewed | rejected_category_drift | Adds the wall plate, radial arms and external cradle ring responsible for the reported bad rack/hopper composition. The complete mounting assembly is intentionally excluded. |
| rec_red-painted-sheet-metal-conical-fire-bucket-with_20260608_164532_434098_8f71e941/rev_000001 | reviewed | used | Reference-image parent for the pointed hanging fire-bucket family: hollow apex-down conical shell, rolled rim, two riveted ears and one swing bail about the ear diameter. |
| rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | reviewed | used | Reference-image parent for the standing tapered-pail family: hollow linearly flared shell with a solid flat floor, rolled rim, two riveted ears and one swing bail. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_profile | tapered_pail | open sheet-metal pail shell | rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | L35-L87, L96-L137 | structure | `_revolved_shell_mesh` uses a wider mouth and narrower flat base, offsets an inner cavity by the sheet thickness and leaves a solid floor; the same root owns the rolled rim and the opposed riveted ears. |
| body_profile | straight_pail | open sheet-metal pail shell | rec_bucket1_var_body_straight_pail/rev_000001 | L35-L88, L97-L138 | structure | `TOP_R == BOT_R` makes the entire outer and inner wall vertical while retaining the solid flat floor; this changes the primary silhouette rather than only scaling it. |
| body_profile | rounded_bowl | open sheet-metal bowl pail | rec_bucket1_var_body_hemispherical/rev_000001 | L37-L120, L129-L169 | structure | `_bowl_outer_profile` and `_bowl_inner_profile` derive nonlinear quarter-circle outer/inner walls and a small flat standing pad, yielding a rounded silhouette distinct from all linear profiles. |
| body_profile | pointed_fire_bucket | open pointed fire-bucket shell | rec_red-painted-sheet-metal-conical-fire-bucket-with_20260608_164532_434098_8f71e941/rev_000001 | L39-L81, L90-L126 | structure | `_conical_shell_mesh` closes the hollow linear wall into a small apex instead of a standing floor; the original reference image shows this pointed bucket beside the flat-base pail. |
| rim_profile | rolled_wire | rolled sheet-metal mouth edge | rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | L41-L43, L102-L106 | structure | A single toroidal wire roll follows the open shell termination and produces the compact rounded mouth silhouette shown by the parent asset. |
| rim_profile | flared_fold | outward-folded sheet-metal mouth edge | rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | L58-L87, L96-L106 | structure | The source's revolved thin-sheet profile construction and finished top edge support a locally widened folded lip; the derived candidate changes the mouth cross-section without adding a body hoop. |
| rim_profile | double_bead | compact double-bead mouth reinforcement | rec_bucket1_var_bands_two/rev_000001 | L57-L84, L125-L135 | structure | `_band_mesh` demonstrates repeated toroidal sheet reinforcement following a local circular radius. Restricting two smaller beads to the immediate mouth edge yields a distinct reinforced rim without retaining the rejected full-height hoops. |
| bail_profile | round_arch | smoothly crowned swing bail | rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | L139-L183 | structure+motion | The source bail is a smooth symmetric spline from both pivot lugs to a centered crown and rotates about the real opposed-ear diameter. |
| bail_profile | shouldered_arch | angular-shouldered swing bail | rec_bucket1_var_handle_fixed_grips/rev_000001 | L91-L118, L202-L210 | structure+motion | `_make_dloop_grip_mesh` supplies a source-inspectable shouldered wire path. The derived candidate mirrors that bend language across the bucket while retaining the same single-bail REVOLUTE axis. |
| ear_style | riveted_strap | rectangular riveted pivot strap | rec_red-painted-sheet-metal-fire-bucket-a-tapered-cy_20260608_164512_348759_c25e8986/rev_000001 | L108-L131 | structure | Each long rectangular tab bridges from the shell to the pivot pin and is visibly capped by a rivet head. |
| ear_style | round_stamped_lug | round-headed stamped pivot lug | rec_bucket1_var_handle_fixed_grips/rev_000001 | L150-L177 | structure | The source side-grip assembly demonstrates compact paired wall tabs and circular rivet heads; the derived single-bail version uses a short neck and round stamped head around the same pivot datum. |
