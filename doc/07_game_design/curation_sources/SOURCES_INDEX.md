# SOURCES INDEX

Curacao canonica de fontes secundarias usadas para subsidiar as 20 especializacoes `active` do v2. v1 cobria apenas `fighting_2d_traditional` com 2 bibles. v2 expande para 8 familias com 7 bibles placeholder pendentes (Wave 1+).

## Politica

- Toda fonte externa (biblia, livro, wiki, guia) usada como base precisa de copia local em `curation_sources/<sha256>_<descriptive>.txt`.
- O SHA-256 da copia local deve bater com o SHA-256 do arquivo de origem.
- `verification_status` pode ser:
  - `unverified_secondary_text`: texto bruto copiado. `promotion_allowed` deve ser `false`.
  - `verified_curated`: revisado por humano. `promotion_allowed` pode ser `true`.
- Nenhum caminho absoluto externo pode aparecer em material ativo. Referencias devem apontar para `curation_sources/<arquivo_local>`.
- `ip_policy_reference` deve apontar para `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` (fonte canonica de politica de IP do workspace).

## Fontes catalogadas

### `fighting_game_bible_1_subgenre_lexicon`

| Campo | Valor |
|---|---|
| `source_id` | fighting_game_bible_1_subgenre_lexicon |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `BC32F698C01CBB5FD565533F5D95483152932E32601A51D68B899956DF282122` |
| `byte_size` | 8460 |
| `local_path` | `doc/07_game_design/curation_sources/bc32f698c01cbb5fd565533f5d95483152932e32601a51d68b899956df282122_fighting_game_bible_1_subgenre_lexicon.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Lexicon pedagogico dos subgeneros fundamentais (2D Traditional, 3D, Air Dasher, Platform, Tag Team, Arena). Cobre Triangulo de Arquetipos (Zoner/Rushdown/Grappler), Anatomia Tecnica de Partida (Neutro, Spacing, Frame Data, Hitbox vs Hurtbox, Okizeme), Netcode (Delay-Based vs Rollback). |
| `usage` | Subsidia secoes `lore` (subgeneros), `modes` (treinamento, okizeme) e `frozen_design_axes.rollback_netcode=not_applicable` do design contract. Nao promove sozinho; precisa de revisao humana explicita. |

### `fighting_game_bible_2_advanced_systems_matrix`

| Campo | Valor |
|---|---|
| `source_id` | fighting_game_bible_2_advanced_systems_matrix |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `9E136527BD841B5E6FE1886BFCAF5D17972006FC4060DBD54C45D5E786244DCD` |
| `byte_size` | 10425 |
| `local_path` | `doc/07_game_design/curation_sources/9e136527bd841b5e6fe1886bfcaf5d17972006fc4060dbd54c45d5e786244dcd_fighting_game_bible_2_advanced_systems_matrix.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Matriz avancada por subgenero. Lista elementos universais (Neutro, Spacing, Whiff Punish, Frame Data, Hitbox/Hurtbox, Okizeme, Punish, Command Grab, Hit Confirm, Option Select) e elementos exclusivos por subgenero (Corner Management, Sidestep, Air Dash, Burst, Just Defend, Knockback, Edge-guarding, Assists, DHC, Lock-on). |
| `usage` | Subsidia `frozen_design_axes.archetype_policy=design_tool_not_law` e o cenario de `future_knowledge` (nao promove specialization). Nao promove sozinho; precisa de revisao humana explicita. |

## Verificacao de hash

Para revalidar as copias locais:

```powershell
Get-FileHash -LiteralPath "F:\Projects\Sgdk Forge\doc\07_game_design\curation_sources\bc32f698c01cbb5fd565533f5d95483152932e32601a51d68b899956df282122_fighting_game_bible_1_subgenre_lexicon.txt" -Algorithm SHA256
Get-FileHash -LiteralPath "F:\Projects\Sgdk Forge\doc\07_game_design\curation_sources\9e136527bd841b5e6fe1886bfcaf5d17972006fc4060dbd54c45d5e786244dcd_fighting_game_bible_2_advanced_systems_matrix.txt" -Algorithm SHA256
```

Ambos devem retornar o SHA-256 declarado acima.

## Promocoes

Nenhuma fonte em `verified_curated` no momento. Promocao exige:
1. Humano le o texto bruto.
2. Humano decide se ha conflito com a politica de IP do workspace (`art_style_catalog.json`).
3. Humano atualiza este `SOURCES_INDEX.md` com `verification_status=verified_curated` e `promotion_allowed=true`.
4. Humano registra a promocao em `doc/changelog/changelog.md` do wrapper.

## Fontes pendentes (placeholder Wave 1+)

Os 7 subgeneros abaixo ainda nao possuem biblia canonica copiada. Cada entrada sera preenchida em sua Wave respectiva (Wave 1 cobre 5: rpg, strategy, brawler, platformer, racing). Waves 2-4 cobrem horror. **Nenhuma skill/schema/validator pode ser declarado `active` para uma familia ate sua biblia ser catalogada com `verification_status` definido e SHA-256 batendo.**

### `rpg_game_bible_1_subgenre_taxonomy` (Wave 1)

| Campo | Valor |
|---|---|
| `source_id` | rpg_game_bible_1_subgenre_taxonomy |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `444A68E95C0844BAC5AC6F3FB836A76982BDD986FCEE45FB8CBCC2254751686A` |
| `byte_size` | 12800 |
| `local_path` | `doc/07_game_design/curation_sources/444a68e95c0844bac5ac6f3fb836a76982bdd986fcee45fb8cbcc2254751686a_rpg_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre JRPG turn-based, Action RPG topdown, cRPG classico, RPG narrativo. Subsidiar `rpg_turn_based_jrpg` e `rpg_action_topdown` em Wave 1; os outros 2 ficam em `future_knowledge`. |
| `usage` | Wave 1 (`rpg_turn_based_jrpg`). NAO emite design contract ate revisao humana. |

### `strategy_game_bible_1_subgenre_taxonomy` (Wave 1)

| Campo | Valor |
|---|---|
| `source_id` | strategy_game_bible_1_subgenre_taxonomy |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `4AC59CC048CF133996A3F94E99A65AA328A201242EEF56F39BFBB5DDB4DC8AF2` |
| `byte_size` | 13546 |
| `local_path` | `doc/07_game_design/curation_sources/4ac59cc048cf133996a3f94e99a65aa328a201242eef56f39bfbb5ddb4dc8af2_strategy_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Tower Defense, Tactical Turn-Based, RTS Compact, Grand Strategy, 4X. Subsidiar `strategy_tower_defense` e `strategy_tactical_turn_based` em Wave 1. Os outros 3 ficam em `future_knowledge`/`future_architetural`. |
| `usage` | Wave 1 (`strategy_tower_defense`). NAO emite design contract ate revisao humana. |

### `brawler_game_bible_1_subgenre_taxonomy` (Wave 1)

| Campo | Valor |
|---|---|
| `source_id` | brawler_game_bible_1_subgenre_taxonomy |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `36BC4E0683459772042B9BC6305CBDE5CC900BB7AF7D03D05C57EE603E55B25C` |
| `byte_size` | 13577 |
| `local_path` | `doc/07_game_design/curation_sources/36bc4e0683459772042b9bc6305cbde5cc900bb7af7d03d05c57ee603e55b25c_brawler_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Beat 'em Up (Belt-Scroll), Run and Gun 2D, Run and Gun Top-Down. Subsidiar `brawler_belt_scroll` em Wave 1; `brawler_run_and_gun_2d` e `brawler_run_and_gun_topdown` em Waves 2-3. |
| `usage` | Wave 1 (`brawler_belt_scroll`). NAO emite design contract ate revisao humana. |

### `platformer_puzzle_game_bible_1_subgenre_taxonomy` (Wave 1)

| Campo | Valor |
|---|---|
| `source_id` | platformer_puzzle_game_bible_1_subgenre_taxonomy |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `B0880ACA6572E40C714BFA5377A0EE4B95987E7AC22B34232CC3C822264F6D5D` |
| `byte_size` | 15269 |
| `local_path` | `doc/07_game_design/curation_sources/b0880aca6572e40c714bfa5377a0ee4b95987e7ac22b34232cc3c822264f6d5d_platformer_puzzle_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Plataforma de Precisao, Metroidvania, Puzzle de Fisica, Sokoban, Tile-Matching. Subsidiar `platformer_precision_2d` em Wave 1; `metroidvania_ability_gated`, `puzzle_sokoban_grid` e `puzzle_tile_matching` em Waves 2-3. |
| `usage` | Wave 1 (`platformer_precision_2d`). NAO emite design contract ate revisao humana. |

### `racing_sports_adventure_game_bible_1_subgenre_taxonomy` (Wave 1)

| Campo | Valor |
|---|---|
| `source_id` | racing_sports_adventure_game_bible_1_subgenre_taxonomy |
| `verification_status` | unverified_secondary_text |
| `promotion_allowed` | false |
| `captured_at` | 2026-06-05 |
| `curator` | unverified |
| `sha256` | `8B8ACB3E8A46B764862DBBFC6A50DA0DF6AF39F6018BE5C256B0C7DB36A8786D` |
| `byte_size` | 12127 |
| `local_path` | `doc/07_game_design/curation_sources/8b8acb3e8a46b764862dbbfc6a50da0df6af39f6018be5c256b0c7db36a8786d_racing_sports_adventure_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Simulador de Corrida, Corrida Arcade, Gestao Esportiva, Acao Esportiva Direta, Aventura de Acao. Subsidiar `racing_arcade` em Wave 1; `sports_action_direct` e `adventure_action_2d` em Wave 4. |
| `usage` | Wave 1 (`racing_arcade`). NAO emite design contract ate revisao humana. |

### `horror_game_bible_1_subgenre_taxonomy` (placeholder — Wave 2)

| Campo | Valor |
|---|---|
| `source_id` | horror_game_bible_1_subgenre_taxonomy |
| `verification_status` | pending |
| `promotion_allowed` | false |
| `sha256` | PENDENTE |
| `local_path` | `doc/07_game_design/curation_sources/PENDENTE_horror_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Survival Horror, Stealth Horror, Psychological Horror, Action Horror, Mascot Horror, Retro/Short Form. Subsidiar `horror_survival_inventory` em Wave 2; os outros 4 (Waves 3-4) ficam em fila. |
| `usage` | Planejado para Wave 2 (`horror_survival_inventory`). |

### `fps_game_bible_1_subgenre_taxonomy` (placeholder — Wave 3)

| Campo | Valor |
|---|---|
| `source_id` | fps_game_bible_1_subgenre_taxonomy |
| `verification_status` | pending |
| `promotion_allowed` | false |
| `sha256` | PENDENTE |
| `local_path` | `doc/07_game_design/curation_sources/PENDENTE_fps_game_bible_1_subgenre_taxonomy.txt` |
| `ip_policy_reference` | `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` |
| `summary` | Cobre Boomer Shooter, Shooter Tatito, Immersive Sim, FPS Puzzle. SEM subgenero `active` no v2; todavia biblia fica pronta para quando `fps_boomer_raycast` (Wave 3) ou `fps_tactical_simulation` (future_architetural — improvavel) for promovido. |
| `usage` | NAO emite design contract no v2. Pode ser copiada em Wave 3 para subsidiar eventual opt-in por `fps_boomer_raycast`. |
