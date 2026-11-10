# pictureX_0611_Locker_box - Source Replay Transitional Spec

| field | value |
| --- | --- |
| template path | `agent/templates/pictureX_0611_Locker_box.py` |
| template mode | source replay transitional template |
| sweep report | `reports/pictureX_0611_Locker_box_pipeline_20260712.json` |
| latest verdict | pass, 36/36 seeds, pass_rate 1.0 |

## Scope

This template preserves the locker-box identity by replaying verified cabinet/locker source records. It does not yet expose door layout, drawer grid, latch, or interior as recombinable slots.

## Adopted Sources

- `rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc`

## Excluded Sources

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094918_538851_0832e6dc`: fixed drawer joint origins far from cabinet geometry.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095217_763786_0832e6dc`: not retained after verified-source narrowing.
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095547_901965_0832e6dc`: not retained after verified-source narrowing.

## Coverage Notes

The final sweep covers all three reachable source records. Corner-seed selection reported no extra uncovered tokens.
