# Strategy Tower Defense Design Lexicon

Termos canonicos usados em `strategy_tower_defense_design_contract.json` e `strategy_tower_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `frames` | 1/60 s; unidade de tempo canonica em TD | int >= 0 |
| `fire_rate_frames` | frames entre dois ataques consecutivos da torre | int 6-600 |
| `projectile_speed_tiles_per_second` | velocidade do projetil em tiles/s | int 1-16 |
| `delay_between_spawns_frames` | frames entre spawns de inimigos do mesmo grupo | int 1-600 |
| `slow_duration_frames` | duracao do slow aplicado pela torre slow | int 0-600 |
| `animation_idle_frames` | duracao de um loop idle da torre | int 0-600 |
| `animation_fire_frames` | duracao da animacao de fire (1 ciclo) | int 0-60 |

## Stat canonico de torre (tier)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `cost` | gold/energy gasto para construir/melhorar | int 10-2000 | 65535 (u16) |
| `damage` | dano por hit | int 1-9999 | 65535 (u16) |
| `range_tiles` | alcance em tiles | int 1-12 | 255 (u8) |
| `fire_rate_frames` | frames entre hits | int 6-600 | 65535 (u16) |
| `splash_radius_tiles` | raio da area-of-effect (0 = sem splash) | int 0-4 | 255 (u8) |
| `slow_pct` | % de slow aplicado (0 = sem slow) | int 0-90 | 100 |
| `slow_duration_frames` | duracao do slow | int 0-600 | 65535 (u16) |
| `chain_targets` | numero de alvos adicionais em chain | int 0-8 | 255 (u8) |

## Categorias de torre

| Category | Significado | trade-off |
|---|---|---|
| `damage` | dano single-target, fogo rapido | alcance medio, sem utility |
| `slow` | dano baixo, aplica slow/freeze | utility alta, dano baixo |
| `splash` | dano em area, fogo lento | alto DPS burst, splash em grupos |
| `chain` | hit em multi-alvos por bounce | multi-target, dano cai por bounce |
| `support` | buffa torres vizinhas (+damage/range/firerate) | sem dano direto, requer posicionamento |
| `economy` | gera gold/energy por kill | sem dano, requer escala para pagar |
| `ultimate` | efeito especial (meteor, freeze all, nuke) | custo alto, cooldown longo |

## Tiers de upgrade

| `tier_id` | Custo base | Quando | Efeito |
|---|---|---|---|
| `basic` | 10-100 gold | construcao inicial | stats base |
| `advanced` | +50% a +100% do basic | upgrade 1 | +dano, +alcance, ou +special |
| `elite` | +200% a +400% do basic | upgrade 2 | +ultimate ou +splash/chefia |

Elite tier DEVE declarar `ultimate_unlocked_at_wave` (constraint allOf no schema).

## Categorias de inimigo

| `archetype` | HP | speed | resistencia | gold | special |
|---|---|---|---|---|---|
| `grunt` | baixo (10-50) | rapido (4-8) | 0% | 5-15 | none |
| `tank` | alto (200-500) | lento (1-3) | 50-90% | 30-60 | none |
| `swarm` | muito baixo (5-15) | medio (3-5) | 0% | 2-5 | none (mas vem em grupos) |
| `flyer` | medio (50-100) | medio (3-5) | 0% | 15-25 | ignora ground path |
| `boss` | muito alto (1000-9999) | lento (1-2) | 50-90% | 200-500 | heal_aura, spawn_adds, immolate, regen, shield, teleport |
| `stealth` | medio (50-100) | medio (3-5) | 0% | 20-30 | invisivel ate torre atackar |
| `healer` | medio (50-100) | medio (2-4) | 0% | 25-40 | cura aliados proximos |
| `splitter` | medio (50-100) | medio (3-5) | 0% | 15-25 | ao morrer, divide em 2 swarms |

## Wave composition

| Termo | Significado |
|---|---|
| `wave_count` | numero total de waves por run (5-50) |
| `goal_lives` | HP do goal; 0 = perdeu (5-30) |
| `boss_wave_interval` | a cada N waves, ha 1 boss_wave (3-10) |
| `spawn_group` | grupo de inimigos do mesmo tipo, com delay entre spawns |
| `delay_between_spawns_frames` | frames entre cada inimigo do grupo |

## Path geometry

| `path_geometry` | Significado | Pros | Cons |
|---|---|---|---|
| `linear` | 1 lane reta do spawn ao goal | simples, alto throughput | monotematico |
| `curved` | 1 lane com curvas | variacao visual | densidade maior em curvas |
| `branching` | 2-3 lanes convergindo | jogador precisa defender todas | mais slots necessarios |
| `loop` | path circular (spawn e goal no mesmo lado) | jogador pode loopear cobertura | curva de aprendizado alta |

## Modos

| `kind` | Quando | Save model |
|---|---|---|
| `campaign` | progressao linear de mapas com historia | save_station (entre mapas) |
| `endless` | waves infinitas ate perder | save_anywhere_with_confirm |
| `challenge` | condicoes restritivas (ex: so basic tower) | save_station |
| `puzzle_td` | mapa pre-definido com solucao otima | save_station |
| `daily_seed` | mesmo seed para todos jogadores, ranqueado | save_anywhere_with_confirm |

## Limites VRAM

| Recurso | Cap MD | Notas |
|---|---|---|
| Tiles visiveis | 64x64 = 4096 tiles | BG_A + BG_B = ate 32x32 cada |
| Tilemaps em VRAM | 64KB total | grid_layout.vram_budget_estimate_kb deve ser <=64 |
| Sprites | 64 visiveis, 256 total em tabela | inimigos + torres = 8-16 simultaneos |
| Paletas | 4 paletas de 16 cores | inimigos + torres + UI + bg |
