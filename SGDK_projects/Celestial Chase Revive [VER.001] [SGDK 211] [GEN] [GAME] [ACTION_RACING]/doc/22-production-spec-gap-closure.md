# 22 - Fechamento de Lacunas de Producao

Status: `documentado`.

Data: 2026-06-16

Esta rodada responde as lacunas criticas levantadas apos a primeira fundacao de specs. O objetivo nao foi iniciar codigo jogavel, mas remover ambiguidades que fariam a implementacao inventar regras na hora.

## Decisoes Principais

| Lacuna | Decisao | Artefato |
|---|---|---|
| Formato de dados dos niveis | pista por eventos em faixas, nao matriz de tile collision | `track_data_format_contract.json`, `sector_01_track_plan.json` |
| Sistema de colisao | AABB por layers, hurtbox menor que sprite, tile visual nao e colisao | `collision_system_contract.json` |
| HUD | WINDOW 320x24, coordenadas fixas, Pressure/Pulse mapeados em pixels | `hud_layout_contract.json`, `hud_wireframe.md` |
| Animacao | Lio 24x32, run 6 frames, jump 6 frames, damage 3 frames, Pulse 4 frames | `sprite_animation_contract.json` |
| Curva numerica | velocidades Q8.8, pressao, spawn gaps, custos de upgrade | `progression_tuning_tables.json` |
| Asset production spec | tile targets, paletas, superficies e frames por asset | `asset_production_spec.json` |
| Build | wrapper central, sem Makefile local canonico, arquivos minimos declarados | `build_system_contract.json` |
| Boss | fases, ataques, weakpoints, hits e collision model | `boss_attack_pattern_contract.json` |
| Pause/game over/continue | estados formais, freeze rules, retry/title flow | `game_flow_contract.json` |
| Concept/reference art | mockups SVG locais com hashes, marcados como referencia apenas | `concept_art_brief.md`, `concept_art_pack_manifest.json` |

## Reflexao de Arquitetura

A decisao mais importante foi separar `visual road` de `gameplay track`.

O jogo quer parecer uma corrida celeste profunda, mas o primeiro slice nao deve depender de geometria livre. Track data por eventos em faixas reduz risco, facilita tuning, cabe em arrays estaticos e permite que arte/pista evoluam sem reescrever colisao.

Colisao por AABB tambem foi escolhida de forma conservadora. Slopes, tile material map e colisao por pixel nao sao necessarios para o primeiro slice e criariam custo sem payoff. O contrato ainda deixa caminho para mapas de material no futuro se o jogo ganhar exploracao lateral ou segmentos fora de faixas.

HUD em WINDOW foi mantido porque estabiliza leitura e reduz concorrencia com BG_A/B. O custo e a faixa de 24px no topo, aceito porque a corrida precisa de informacao constante: integridade, Lumen, pressao, Pulse e foco.

O boss foi mantido como setpiece de corrida, nao como criatura fisica livre. O corpo do Mestre Perseguidor e visual-only; ataques e weakpoints sao entidades testaveis. Isso evita que um boss monumental destrua leitura, scanline budget e colisao.

## O Que Ainda Nao Esta Provado

- Nenhum asset final existe.
- Nenhum `.res` existe.
- Nenhum tile count foi medido por res graph.
- Nenhuma captura BlastEm existe para o Revive.
- Nenhum wireframe foi convertido em pixel art final.
- Nenhum tuning foi testado com jogador real.
- Nenhum contrato acima promove `buildado`, `testado_em_emulador` ou `validado_budget`.

Status maximo permanece `documentado`.
