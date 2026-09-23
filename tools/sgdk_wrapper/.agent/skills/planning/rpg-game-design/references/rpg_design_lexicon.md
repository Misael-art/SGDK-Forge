# RPG Turn-Based JRPG Design Lexicon

Termos canonicos usados em `rpg_turn_based_jrpg_design_contract.json` e `rpg_party_frame_data.json`. Apenas o sentido operacional. Conflitos com literatura externa NAO sao automaticamente absorvidos.

## Tempo

| Termo | Significado | Unidade |
|---|---|---|
| `ticks (turn)` | 1 turno de combate (1 acao por membro) | int >= 0 |
| `learned_at_level` | nivel em que a ability eh aprendida | int 1-99 |
| `mp_cost` | custo em MP por uso da ability | int 0-99 |
| `power` | potencia base da ability (dano ou cura) | int 0-999 |
| `xp_per_level` | XP cumulativa para subir de nivel | int >= 0 |
| `level_cap` | nivel maximo do membro | int 1-99 |

Frame 0 (overworld): toda movimento eh em `frames` (1/60 s). Em combate, a unidade eh `ticks` (1 turno). O design contract declara `time_unit = "ticks (turn)"` no top-level; campos derivados de overworld (movement speed) usam `frames` localmente.

## Stat canonico (base_stats)

| Stat | Significado | Range | Cap MD |
|---|---|---|---|
| `hp` | Hit Points (saude) | 1-9999 | 9999 |
| `mp` | Magic Points (recurso de spell) | 0-999 | 999 |
| `attack` | poder de ataque fisico | 1-255 | 255 |
| `defense` | reducao de dano recebido | 1-255 | 255 |
| `agility` | agilidade (define turn order) | 1-255 | 255 |
| `magic` | poder de spell | 1-255 | 255 |

Stat > cap eh overflow. NUNCA promover alem do cap (freezes de tipo `u16` em MD).

## Roles

| Role | Significado | min learned_abilities |
|---|---|---|
| `leader` | personagem principal; sempre em party | 3 (default) |
| `support` | char secundario generico | 1 |
| `mage` | white/black mage (curser) | 1 |
| `rogue` | thief/assassin (alta agility) | 1 |
| `tank` | char defensivo (alta defense) | 1 |
| `healer` | white mage especifico (heal+buff) | 1 |
| `summoner` | invoca entities (Summon/Espers) | 1 |
| `guest` | NPC temporario (joins e sai) | 1 |

## Combat primitives

| Categoria | Significado |
|---|---|
| `attack` | ataque fisico padrao |
| `white_magic` | cura/buff/regen (incluso `heal`) |
| `black_magic` | dano elemental (fire/ice/thunder) |
| `summon` | invoca entity (Espers/Aeons) |
| `buff` | aumenta stats aliados (haste/shield/regen) |
| `debuff` | reduz stats inimigos (slow/blind) |
| `heal` | cura HP/MP/Status |
| `ultimate` | spell final de alto custo (geralmente super) |
| `skill` | habilidade de classe (roubar, identificar, etc) |
| `item_use` | usa item fora de combate (in-battle item eh `item`) |

## Status effects

`poison`, `sleep`, `paralysis`, `silence`, `confusion`, `blind`, `stone`, `death`, `regen`, `shield`, `haste`, `slow`. Implementados como bitmask (max 12 efeitos). Cada efeito consome 1 bit em `u16` status field.

## Modos

| `kind` | Quando |
|---|---|
| `main_story` | campanha principal (default) |
| `side_quest` | missao lateral; pode ter save_model proprio |
| `arena` | combate 1v1v1v1 ou wave |
| `colosseum` | torneios e apostas (save_model varia) |
| `post_game` | conteudo pos-creditos |
| `new_game_plus` | recomeca com bonus carryover |

## Save models

| `save_model` | Quando | Risco de corruption |
|---|---|---|
| `save_station` | save so em igrejas/inns | baixo |
| `save_anywhere_with_confirm` | save a qualquer hora com dialogo de confirm | medio |
| `save_anywhere` | save a qualquer hora sem confirm | alto (rpg_save_corruption_risk dispara) |

Bloco `rpg_save_corruption_risk` exige `save_station` ou `save_anywhere_with_confirm` em pelo menos um mode. `save_anywhere` puro em todos os modos dispara o blocker.
