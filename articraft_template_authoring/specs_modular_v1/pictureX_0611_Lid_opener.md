# pictureX_0611_Lid_opener - Source Replay Transitional Spec

| field | value |
| --- | --- |
| template path | `agent/templates/pictureX_0611_Lid_opener.py` |
| template mode | source replay transitional template |
| sweep report | `reports/pictureX_0611_Lid_opener_pipeline_20260712.json` |
| latest verdict | pass, 36/36 seeds, pass_rate 1.0 |

## Scope

This template keeps the lid-opener identity by replaying verified hand-tool source records. It does not yet split handle, clamp, cutter, and gear mechanisms into recombinable module slots.

## Adopted Sources

- `rec_picturex_0611__lid_opener__001__png_3629ffb09bed420e8847dce28465922d`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_036146_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_039038_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094513_583310_45e44262`

## Excluded Sources

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092525_105360_45e44262`: scalar movable joint used `meta qc_samples`, which neuters motion sampling.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094845_264861_45e44262`: not retained after verified-source narrowing.

## Coverage Notes

The final sweep covers all four reachable source records. The report contains one new captured-pivot overlap allowance for `body` / `upper_handle`; it is declared by the source and did not block the sweep.
