# Racing Arcade Design Lexicon

Termos canonicos usados em `racing_arcade_design_contract.json` e `racing_vehicle_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `frames` | 1/60 s; unidade de tempo canonica em racing | int >= 0 |
| `acceleration_frames_to_top` | frames do zero ate top speed | int 60-600 |
| `duration_frames` | duracao de efeito (item, boost) | int 1-600 |
| `par_lap_time_frames` | tempo canonico para 1 volta em frames | int 3600-36000 (60s-600s) |
| `track_music_loop_seconds` | duracao do loop de BGM por track | int 30-120 |

## Stat canonico de vehicle (stats)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `top_speed_kmh` | velocidade maxima em km/h | int 100-256 | 255 (u8) |
| `acceleration_frames_to_top` | frames para atingir top speed | int 60-600 | 65535 (u16) |
| `handling_rad_per_sec` | rad/s de rotacao maxima | float 0.5-2.0 | n/a |
| `drift_factor` | fator de drift (0 = sem drift, 100 = drift total) | int 0-100 | 255 (u8) |
| `boost_consumption_pct_per_sec` | % de boost consumido por segundo em boost | int 0-100 | 255 (u8) |
| `weight_kg` | peso do veiculo em kg (afeta colisao e drift) | int 500-2000 | 65535 (u16) |
| `tire_grip_pct` | % de grip dos pneus (0 = drift facil, 100 = sem drift) | int 50-100 | 255 (u8) |
| `downforce_pct` | % de downforce (aerodinamica) | int 0-100 | 255 (u8) |

## Weight classes (weight_class)

| `weight_class` | Significado | drift_factor min |
|---|---|---|
| `light` | kart, bike; drift facil, top speed media | 30 |
| `medium` | carrapato; balanceado | (sem minimo explicito) |
| `heavy` | truck, tank; drift dificil, top speed baixa | 10 |
| `formula` | F1, formula; drift medio, top speed alta | 30 |

Constraints allOf no schema: light/formula >= 30, heavy >= 10.

## Item categories (item_catalog)

| `category` | Significado | stack_max canonico | duration_frames tipico |
|---|---|---|---|
| `rocket` | foguete contra carro a frente | 1 | 60 (1s) |
| `shield` | escudo contra items | 2 | 600 (10s) |
| `oil_slick` | poça de oleo atras do carro | 1 | 600 (10s) |
| `lightning` | lightning em todos a frente | 1 | 30 (0.5s) |
| `ghost` | invencibilidade temporaria | 2 | 300 (5s) |
| `machine_gun` | atira a frente | 3 | 300 (5s) |
| `boost` | boost extra | 3 | 60 (1s) |
| `trap` | mina atras | 1 | 60 (1s) |

## Track catalog (track_catalog)

| Campo | Significado | Range |
|---|---|---|
| `length_pixels` | comprimento da pista em pixels | 8000-65535 |
| `lane_count` | numero de lanes (geralmente 1-4) | 1-4 |
| `shortcut_count` | numero de atalhos | 0-4 |
| `weather_policy` | clear/rain/night/random | enum |
| `recommended_lap_count` | voltas sugeridas | 1-5 |
| `par_lap_time_frames` | tempo canonico para 1 volta em frames | 3600-36000 |
| `track_music_loop_seconds` | duracao do BGM em loop | 30-120 |

## Race modes (race_modes)

| `kind` | Quando | laps | ai_count |
|---|---|---|---|
| `grand_prix` | campeonato com 4-8 races progressivas | 3-5 | 5-7 |
| `single_race` | race unica rapida | 1-5 | 5-7 |
| `time_trial` | melhor volta sozinho | 3-5 | 0 (sem AI) |
| `battle` | 4-8 players, item battle, knockback | 3-5 | 5-7 |
| `endurance` | race longa, maior premio | 5 | 5-7 |
| `split_screen` | 2 jogadores local | 3-5 | 5 (1 AI + 1 humano) |

## AI profile (ai_profile)

| Campo | Significado | Range |
|---|---|---|
| `difficulty_levels[]` | 3-5 niveis pre-definidos | easy/normal/hard/expert/master |
| `drafting_enabled` | AI usa drafting (slipstream) | bool |
| `rubber_banding_enabled` | AI ajusta velocidade para manter corrida acirrada | bool |
| `rubber_band_strength_pct` | % de ajuste | 0-50 |
| `ai_top_speed_variance_pct` | variacao de top speed entre AIs | 0-30 |

## HUD config (hud_config)

| Campo | Significado | Default |
|---|---|---|
| `show_position` | mostra posicao 1st/2nd/.../8th | true (const) |
| `show_lap_counter` | mostra "Lap 2/5" | true (const) |
| `show_lap_time` | mostra tempo de volta + total | true (const) |
| `show_minimap` | minimapa da pista | false |
| `show_speed_kmh` | velocimetro em km/h | false |
| `show_boost_meter` | medidor de boost 0-100% | true |
| `show_item_slot` | item atual em uso | true |

## Limites VRAM e sprite

| Recurso | Cap MD | Notas |
|---|---|---|
| Sprites visiveis | 64 (4-paleta) | 5-7 AI cars + player + items + UI |
| Sprites por scanline | 20 (4-paleta) | sem flicker |
| Tiles | 4096 (BG_A 32x32 + BG_B 32x32) | track tiles + decoracao |
| Paletas | 4 paletas de 16 cores | cars+UI+hud+bg |
| SRAM | 32KB | best_lap + total_time + ghost_data (16 bytes/track) |
| Track length pixels | 8000-65535 (u16) | max 65535 (loop) |
