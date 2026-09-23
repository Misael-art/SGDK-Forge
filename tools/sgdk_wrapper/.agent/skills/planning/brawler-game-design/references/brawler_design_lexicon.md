# Brawler Belt-Scroll Design Lexicon

Termos canonicos usados em `brawler_belt_scroll_design_contract.json` e `brawler_enemy_archetype_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `frames` | 1/60 s; unidade de tempo canonica em belt-scroll | int >= 0 |
| `iframe_frames` | frames de invencibilidade apos receber dano | int 8-60 |
| `hit_stun_frames` | frames em que inimigo fica stunado apos hit | int 4-30 |
| `move_speed_px_per_second` | velocidade de movimento em pixels/s | int 8-200 |
| `knockback_px` | deslocamento horizontal em pixels no knockback | int 8-64 |
| `animation_idle_frames` | duracao de um loop idle do arquetipo | int 0-600 |
| `animation_attack_frames` | duracao de um ciclo de attack | int 0-60 |
| `animation_hit_frames` | duracao de um ciclo de hit reaction | int 0-30 |
| `animation_death_frames` | duracao de um ciclo de death | int 0-120 |

## Stat canonico de player (player_roster)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `starting_hp` | HP inicial do jogador | int 50-500 | 9999 (u16) |
| `iframe_frames` | janela de invencibilidade apos hit | int 8-60 | 255 (u8) |
| `super_bar_max` | tamanho maximo da super bar | int 50-200 | 255 (u8) |

## Stat canonico de enemy archetype (base_stats)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `hp` | HP do arquetipo | int 1-9999 | 9999 (u16) |
| `damage` | dano por hit do arquetipo | int 1-99 | 255 (u8) |
| `move_speed_px_per_second` | velocidade em pixels/s | int 8-200 | 255 (u8) |
| `score_reward` | pontos por kill | int 0-99999 | 65535 (u16) |
| `hit_stun_frames` | duracao do stun apos hit | int 4-30 | 255 (u8) |
| `iframe_frames` | janela de invincibilidade do arquetipo (0 = sem iframe) | int 0-30 | 255 (u8) |

## Roles de player

| `role` | Significado |
|---|---|
| `player_1` | jogador 1 (sempre presente) |
| `player_2` | jogador 2 (cooperativo) |
| `unlockable` | jogador destravavel (codex, score, etc) |
| `secret` | jogador escondido (referencia) |
| `boss_player` | jogador que vira boss em story mode |

## Archetypes de player

| `archetype` | Significado | HP range |
|---|---|---|
| `brawler` | classico soco + chute + grab | 100-150 |
| `speedster` | rapido, pouco HP, multi-hit combos | 80-120 |
| `heavy` | lento, muito HP, alto dano por hit | 150-250 |
| `balanced` | meio-termo, can use special | 100-150 |
| `ranged` | arma secundaria forte (1-2 hits) | 80-120 |
| `tactical` | usa items (pocoes, bombas) | 100-150 |

## Archetypes de enemy (enemy_archetypes)

| `archetype` | Significado | HP range | Damage |
|---|---|---|---|
| `grunt` | ataque basico, HP baixo, 1 hit | 5-15 | 3-5 |
| `heavy` | HP alto, ataque lento, alto dano | 30-60 | 8-12 |
| `thrower` | joga garrafas/facas a distancia | 15-25 | 5-8 |
| `runner` | rapido, pouca vida, knockback forte | 8-15 | 4-6 |
| `jumper` | pula e ataca de cima | 15-25 | 6-10 |
| `mini_boss` | mid-boss com 2-3 ataques | 80-150 | 12-18 |
| `boss` | boss de fim de stage, multi-phase | 200-500 | 15-25 |

Boss archetype: 2+ boss_phases obrigatorios (constraint allOf no schema).

## Boss phases (boss_phases)

| `phase_id` | `hp_threshold_pct` | `behavior` | Quando |
|---|---|---|---|
| 1 | 100-66% | `idle` + `attack_pattern_1` | HP > 66% |
| 2 | 66-33% | `attack_pattern_2` + `summon_adds` | HP entre 33-66% |
| 3 | 33-0% | `rage_mode` | HP < 33% |

## Pickup categories (pickup_catalog)

| `category` | Significado | drop_chance_pct tipico |
|---|---|---|
| `health` | pocao, sushi, fruta | 20-40% |
| `score` | $100, $500, $1000 | 30-50% |
| `weapon` | garrafa, taco, faca (durabilidade 5-20 hits) | 10-25% |
| `extra_life` | 1UP | 1-5% (raro) |
| `special_bar_refill` | refil parcial da super bar | 5-15% |

`max_on_screen` por pickup: 1-16 (acima polui a tela).

## Stages (stages)

| Campo | Significado | Range |
|---|---|---|
| `lane_count` | numero de lanes horizontais | 1-3 |
| `wave_count` | numero de waves de inimigos | 2-8 |
| `boss_phases` | fases do boss de fim de stage | 1-3 |
| `hazard_policy` | politica de hazards | no/soft/lethal |
| `bg_music_loop_seconds` | duracao do loop de BGM | 8-60 |

## Modos (modes)

| `kind` | Quando | `starting_lives` |
|---|---|---|
| `arcade` | progressao linear, score ranking | 3 |
| `story` | narrativa com cutscenes | 3-5 |
| `survival` | hordas infinitas ate perder | 1-3 |
| `boss_rush` | so bosses, score por tempo | 3-5 |
| `versus_coop` | 2 jogadores, mesmo stage | 5-9 |
| `time_attack` | completar stages rapido | 3-5 |

## Combat primitives (move_set)

| `move_set[]` | Significado | canonico? |
|---|---|---|
| `punch` | ataque basico | sim |
| `kick` | chute | sim |
| `grab` | agarra inimigo | sim |
| `throw` | joga inimigo pego | sim |
| `jump` | pula (com gravity) | sim |
| `dash` | dash curto | opcional |
| `special` | gasta super bar | sim |
| `ultimate` | ultimate move (gasta 100 super) | opcional |

## Limites VRAM e sprite

| Recurso | Cap MD | Notas |
|---|---|---|
| Sprites visiveis | 64 (4-paleta) ou 80 (1-paleta) | inimigos + players + projectiles |
| Sprites por scanline | 20 (4-paleta) ou 17 (1-paleta) | sem flicker |
| Tiles | 4096 (BG_A 32x32 + BG_B 32x32) | stages comecam BG_A so |
| Paletas | 4 paletas de 16 cores | players+enemies+UI+bg |
