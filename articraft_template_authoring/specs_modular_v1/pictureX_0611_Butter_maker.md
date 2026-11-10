# pictureX/0611/Butter_maker

Source: `articraft_data/picture/0611/Butter_maker/001.png`.

Identity boundary: manual butter churn/maker with container, support frame, and hand-operated agitator. Excludes blender, stand mixer, pasta maker, and sealed jar without mechanism.

Slots: `churn_body` = barrel_churn / upright_jar_churn / box_frame_churn; `drive_style` = side_crank_paddle / top_plunger / geared_side_crank; `palette_style` = oak / painted / industrial; drive radius is sampled.

Motion semantics: side-crank styles expose a revolute shaft driving the internal paddle; top plunger exposes a vertical prismatic dasher.

Sampling and validation: seed 0 is a horizontal barrel churn with side crank. Sweeps should cover revolute and prismatic mechanisms. Validator checks the active drive part and metadata.
