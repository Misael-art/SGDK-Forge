# animation_state_plan

character_id: caio_arara
asset_kind: animation_strip family
frame_envelope: 96x112
pivot: bottom_center x=48 y=104
fps_model: 60hz VBlank timing

## Required States

| State | Frames | Loop | Gameplay role | BJJ fantasy signal |
|---|---:|---|---|---|
| idle | 6 | yes | neutral stance | low grappler base, open hands |
| walk_forward | 6 | yes | advance | mat footwork, hands ready to grip |
| walk_back | 6 | yes | retreat | defensive base, no hopping karate step |
| dash | 4 | no | burst movement | shoulder-forward penetration step |
| crouch | 2 | yes | low guard | hip drop, elbows inside |
| jump | 6 | no | arc | compact athletic leap, landing base |
| guard | 3 | yes | block | forearm shield plus collar-grip readiness |
| jab | 4 | no | light poke | quick open-hand/posting jab |
| medium | 5 | no | palm or low kick | palm frame or low inside kick |
| grip | 5 | no | command entry | lapel/sleeve grip attempt |
| hip_throw | 8 | no | throw | hip turn, pull, load, reap/throw finish |
| hurt | 4 | no | damage reaction | torso recoil, hands stay grappler-like |
| knockdown | 6 | no | fall | controlled fall to mat |
| getup | 6 | no | recovery | technical stand-up |

## Production Rule

Each state is generated as its own source strip containing exactly one action. A multi-action board or key-pose sheet is rejected as animation input.