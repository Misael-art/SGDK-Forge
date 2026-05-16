# pivot_and_scale_contract

character_id: caio_arara
frame_w: 96
frame_h: 112
pivot_x: 48
ground_y: 104
feet_policy: grounded states align at ground_y; jump state declares arc_or_landing.

## Scale Contract

- Caio visual height target: 80-96 px within 96x112 frame.
- Davi uses identical frame and pivot.
- No state may shrink or grow the torso mass except crouch, jump arc compression, knockdown, and getup by intended pose.
- Face, lapel, belt, bare feet, and hand-tape identity must survive at native 320x224.

## Frame Envelope Rules

- No hands, feet, head, belt, or gi lapel may clip frame edges.
- Chroma-key/source matte must not survive as visible pixels after conversion.
- Index 0 in runtime PNGs is transparent/magenta.
- Sprites face right in source; runtime uses hardware horizontal flip for mirrored direction.

## Pivot QA

Each animation must produce:
- motion_phase_map
- frame_delta_report
- contact_sheet
- pivot_overlay
- foot_contact_report
- preview GIF