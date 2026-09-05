# 19 - Roadmap e Riscos - Celestial Chase Revive

## Milestones

### M0 - Specs Foundation

Status: em andamento.

Entregas:

- GDD, roteiro, TDD, spec de cenas, QA, asset register e manifests.
- Nenhum claim de build.

### M1 - Runtime Skeleton

Entregas:

- scene manager;
- title/menu simples com logo, fonte custom e creditos documentados;
- opening cutscene FSM com paineis placeholder marcados;
- race scene vazia com HUD seguro;
- build `out/rom.bin`.

### M2 - First Playable Race

Entregas:

- tres faixas;
- salto;
- Pulse;
- hazards;
- coleta Lumen;
- dano e resultado;
- BlastEm + metrics.

### M3 - Upgrade Slice

Entregas:

- intermissao de upgrade;
- aplicacao de dois upgrades;
- SRAM opcional ou stub documentado.

### M4 - Boss Approach

Entregas:

- Mestre Perseguidor como setpiece de aproximacao;
- telegraphs ligados a gameplay;
- budget de sprites/scanline.

### M5 - Final Boss Prototype

Entregas:

- weak points;
- fases;
- Pulse ofensivo;
- evidencia BlastEm.

## Riscos Principais

| Risco | Severidade | Mitigacao |
|---|---|---|
| Road visual repetir blockers do benchmark | alta | usar source art autoral, gates de matte, screenshots multi-frame e visual review |
| Boss gigante estourar scanline | alta | plane takeover, pre-rendered stages, partes reduzidas, simulator |
| Cutscene virar imagem estatica morta | media | FSM, motion beat map, blink/pan/flash e text timing |
| Upgrades parecerem menu decorativo | media | cada upgrade altera decisao de rota ou risco |
| Tecnica LABORATORIO entrar em entrega | alta | tecnica_usage_manifest e validators |
| HUD parecer debug | alta | ui_decision_card e glyph_manifest antes do runtime |
| Audio mascarar telegraphs | media | sfx_priority_matrix e audio_architecture_card |
| Persistencia quebrar SRAM | media | save_system_contract com magic/version/checksum |

## Criterio de Corte

Se o primeiro slice nao sustentar 60 FPS:

1. reduzir FX per-frame;
2. reduzir sprites simultaneos;
3. reduzir line scroll;
4. reduzir tiles de BG_A;
5. cortar tecnica avancada antes de cortar legibilidade.
