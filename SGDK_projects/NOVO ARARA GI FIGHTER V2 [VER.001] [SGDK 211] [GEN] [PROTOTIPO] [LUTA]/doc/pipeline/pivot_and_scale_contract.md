# pivot_and_scale_contract

character_id: caio_arara
frame_w: 96
frame_h: 112
pivot_x: 48
ground_y: 104
cell_contract_source: fixed_manifest_cell_safe_scale_lock

## Scale Contract

- Runtime cell is fixed at 96x112 because the source max bbox plus 8 px safety pad fits the declared fixed_manifest_cell.
- Builder locks scale once per declared action contract before normalizing frames; no frame may compute an independent scale.
- `doc/pipeline/scale_lock_report.json` stores source bboxes, safe scale and target body ruler for each state.
- Crouch, jump, knockdown and getup may change visible bbox only as pose/ground-contact transitions; attacks must preserve body scale.

## Measured QA

- `foot_contact_report.json` is measured from post-generation runtime PNG component bbox.
- `pivot_drift_px` is measured from bbox center against pivot_x=48.
- `frame_delta_report.json` is measured from post-generation runtime PNG pixels.
- Sprite island cleanup is recorded before promotion; remaining islands block `sprite_artifact_report`.
