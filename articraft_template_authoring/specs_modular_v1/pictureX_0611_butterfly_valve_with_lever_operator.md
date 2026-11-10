# pictureX/0611/butterfly_valve_with_lever_operator

Source: `articraft_data/picture/0611/butterfly_valve_with_lever_operator/001.png`.

Identity boundary: pipe-mounted butterfly valve body with central disc/stem and manual lever operator. Excludes ball valve, gate valve, faucet, and loose lever without valve body.

Slots: `body_style` = wafer_body / lugged_body / flanged_body; `lever_style` = straight_lever / notched_sector_lever / long_locking_lever; `palette_style` = industrial / painted; quarter-turn travel range is sampled.

Motion semantics: lever and butterfly disc share a visible revolute stem around the valve axis, with 0 to quarter-turn limits.

Sampling and validation: seed 0 is a wafer-body straight-lever valve. Validator checks the lever-and-disc part, revolute joint, and slot metadata.
