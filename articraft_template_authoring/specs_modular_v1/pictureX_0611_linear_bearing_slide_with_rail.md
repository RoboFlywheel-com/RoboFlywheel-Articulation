# pictureX_0611_linear_bearing_slide_with_rail - Source Replay Transitional Spec

| field | value |
| --- | --- |
| template path | `agent/templates/pictureX_0611_linear_bearing_slide_with_rail.py` |
| template mode | source replay transitional template |
| sweep report | `reports/pictureX_0611_linear_bearing_slide_with_rail_pipeline_20260712.json` |
| latest verdict | pass, 35/36 seeds, pass_rate 0.972222 |

## Scope

This template keeps the linear-bearing-slide identity by replaying verified rail/carriage source records. It does not yet split rail profile, carriage block, guide rods, end stops, or screw drive into recombinable module slots.

## Adopted Sources

- `rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093549_584407_4387eb47`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101220_741681_83d08292`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47`

## Excluded Sources

- `rec_picturex_0611__linear_bearing_slide_with_rail__001__png_9c9598a488404d7a805a4da0e5dd43ff`: scalar prismatic joint used `meta qc_samples`, which neuters motion sampling.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093250_195206_83d08292`: scalar prismatic joint used `meta qc_samples`, which neuters motion sampling.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101504_669150_4387eb47`: not retained after verified-source narrowing.

## Coverage Notes

The final sweep covers all five reachable source records. Seed 28 timed out, but the final pass rate remained above the 0.9 gate and no coverage gate failed.
