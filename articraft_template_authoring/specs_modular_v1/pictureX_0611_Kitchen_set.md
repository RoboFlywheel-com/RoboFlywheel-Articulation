# pictureX_0611_Kitchen_set - Source Replay Transitional Spec

| field | value |
| --- | --- |
| template path | `agent/templates/pictureX_0611_Kitchen_set.py` |
| template mode | source replay transitional template |
| sweep report | `reports/pictureX_0611_Kitchen_set_pipeline_20260712.json` |
| latest verdict | pass, 36/36 seeds, pass_rate 1.0 |

## Scope

This template keeps the `pictureX/0611/Kitchen_set` identity by replaying only verified source records. It is not a full modular recombination template; the current slot vocabulary is `source_record` / `source_index`.

## Adopted Sources

- `rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f`
- `rec_picturex_0611__kitchen_set__003__png_13615c53ca2c6416dfaa3996d`

## Excluded Sources

- `rec_picturex_0611__kitchen_set__001__png_c1970d9ce2634508b40ad70a6dbcea9d`: articulation origin far from parent geometry.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_091336_287900_df1e5b6c`: sink/countertop overlap and fixed joint origins far from geometry.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092024_594506_750f090f`: oven hinge origin far from parent geometry.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092024_589424_a073119f`: not retained after the verified-source sweep narrowed this class to two passing sources.

## Coverage Notes

The final sweep covers both reachable source records. Corner-seed selection reported no extra uncovered tokens.
