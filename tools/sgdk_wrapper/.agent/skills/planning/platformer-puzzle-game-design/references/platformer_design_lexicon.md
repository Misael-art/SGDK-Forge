# Platformer Precision 2D Design Lexicon

Termos canonicos usados em `platformer_precision_2d_design_contract.json` e `platformer_level_segment_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `frames` | 1/60 s; unidade de tempo canonica em platformer | int >= 0 |
| `coyote_time_frames` | frames apos sair de plataforma em que jump ainda funciona | int 4-6 |
| `jump_buffer_frames` | frames antes de tocar chao em que jump eh registrado | int 4-6 |
| `frames_active` | duracao de uma ability (dash, wall_jump) | int 1-60 |
| `frames_cooldown` | cooldown entre ativacoes de ability | int 0-600 |
| `frames_to_apex` | frames do chao ate o apex do pulo | int 4-30 |
| `par_time_seconds` | tempo canonico para speedrun | int 15-120 |
| `best_time_path` | path para arquivo SRAM com best time | string |

## Stat canonico de player (player_profile)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `run_speed_px_per_frame` | velocidade horizontal em px/frame | int 2-6 | 255 (u8) |
| `walk_speed_px_per_frame` | velocidade de caminhada (1/2 de run) | int 1-4 | 255 (u8) |
| `jump_velocity_px_per_frame` | velocidade vertical inicial do pulo | int 6-18 | 255 (u8) |
| `gravity_px_per_frame_squared` | aceleracao da gravidade | int 1-4 | 255 (u8) |
| `max_jump_height_tiles` | altura maxima do pulo em tiles | int 3-6 | 8 |
| `coyote_time_frames` | janela de jump apos sair de plataforma | int 4-6 | 255 (u8) |
| `jump_buffer_frames` | janela de jump pre-chao | int 4-6 | 255 (u8) |
| `dash_duration_frames` | duracao do dash (se habilitado) | int 4-30 | 255 (u8) |
| `starting_lives` | vidas iniciais | int 1-9 | 255 (u8) |

## Ability categories (ability_set)

| `category` | Significado | frames_active tipico |
|---|---|---|
| `movement` | dash, wall_jump, double_jump | 4-15 |
| `combat` | sword swing, projectile | 6-20 |
| `special` | ultimate, freeze, time-slow | 15-30 |
| `utility` | grab, push, climb | 4-20 |

Em precision_2d, ability `frames_active` deve ser <= 30 (constraint phase-aware).

## Hazard categories (hazard_catalog)

| `category` | Significado | damage tipico | respawn_pattern |
|---|---|---|---|
| `spike` | espinhos no chao/parede | 99 (1-hit kill) | instant_on_death |
| `fire` | fogo em area | 50-99 | loop_forever |
| `water` | agua (afoga) | 99 (1-hit kill) | instant_on_death |
| `pit` | buraco (caindo) | 99 (1-hit kill) | instant_on_death |
| `saw` | serra movel | 99 (1-hit kill) | loop_forever |
| `moving` | plataforma movel hostil | 30-50 | loop_forever |
| `projectile` | projetil do inimigo | 40-99 | trigger_once / time_based |

## Collectible categories (collectible_catalog)

| `category` | Significado | respawn_pattern |
|---|---|---|
| `coin` | moeda (score) | on_death |
| `gem` | gema (score alto) | once_per_run |
| `key` | chave (destranca area) | persistent |
| `checkpoint_token` | token de checkpoint | persistent |
| `extra_life` | 1UP | once_per_run |
| `secret` | item escondido (speedrun bonus) | persistent |

## Level segment data (level_segment_frame_data)

| Campo | Significado | Range |
|---|---|---|
| `width_tiles` | largura do nivel em tiles | 30-600 |
| `height_tiles` | altura do nivel em tiles | 8-32 |
| `tile_size_px` | tamanho de cada tile em pixels | 8-32 (canonico 16) |
| `gravity_zone_count` | numero de zonas com gravity diferente | 1-4 |
| `ceiling_y_px` | limite Y do teto (em pixels) | 32-256 |
| `floor_y_px` | limite Y do chao (em pixels) | 32-256 |

## Parallax layers (parallax_layers)

| `layer_id` | Significado | parallax_factor tipico |
|---|---|---|
| `bg_far` | camadas distantes (montanhas, ceu) | 0.1-0.3 |
| `bg_mid` | camadas medias (arvores, predios) | 0.4-0.6 |
| `bg_near` | camadas proximas (arbustos, moveis) | 0.7-0.9 |
| `fg_overlay` | overlay (particulas, nevoa) | 0.9-1.0 |

## Jump arcs (jump_arcs)

| Campo | Significado | Range |
|---|---|---|
| `max_height_tiles` | altura maxima do pulo em tiles | 1-8 |
| `horizontal_distance_tiles` | distancia horizontal percorrida em 1 pulo | 1-12 |
| `frames_to_apex` | frames do chao ate o apex | 4-30 |

Boss level: 2+ jump_arcs (constraint allOf).

## Modes (modes)

| `kind` | Quando | `lives_policy` |
|---|---|---|
| `story` | progressao linear de levels | no_lives / limited_3 |
| `challenge` | levels bonus, alto desafio | no_lives |
| `speedrun` | speedrun canonico | no_lives |
| `practice` | practice mode (level editor / save states) | unlimited |
| `level_editor` | criar/compartilhar levels | unlimited |

## Limites VRAM e sprite

| Recurso | Cap MD | Notas |
|---|---|---|
| Sprites visiveis | 64 (4-paleta) | player + hazards + collectibles + UI |
| Sprites por scanline | 20 (4-paleta) | sem flicker |
| Tiles | 4096 (BG_A 32x32 + BG_B 32x32) | level background |
| Paletas | 4 paletas de 16 cores | player+UI+hazards+bg |
| SRAM | 32KB | best time per level (50-100 levels * 4 bytes = 200-400 bytes) |
