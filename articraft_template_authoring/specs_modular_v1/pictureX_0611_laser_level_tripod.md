# pictureX_0611_laser_level_tripod - Source Replay Transitional Spec

| field | value |
| --- | --- |
| template path | `agent/templates/pictureX_0611_laser_level_tripod.py` |
| template mode | source replay transitional template |
| sweep report | `reports/pictureX_0611_laser_level_tripod_pipeline_20260712.json` |
| latest verdict | pass, 36/36 seeds, pass_rate 1.0 |

## Scope

This template preserves the laser-level tripod identity by sampling verified tripod source records. It does not yet expose separate head, mast, leg, or brace module slots.

## Adopted Sources

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964`

## Excluded Sources

- `rec_picturex_0611__laser_level_tripod__001__png_42c26bf6cf4f4e838a5d8a4cdf4b502d`: lower leg / upper hub and pan / tilt head overlaps.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095712_384185_82e48964`: not retained after verified-source narrowing.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100114_495054_82e48964`: fixed leg joint origins far from geometry.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100144_545039_82e48964`: not retained after verified-source narrowing.

## Coverage Notes

The final sweep covers both reachable source records. Corner-seed selection reported no extra uncovered tokens.
