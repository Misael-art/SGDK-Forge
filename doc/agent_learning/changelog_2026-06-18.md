# Changelog de aprendizado do agente — 2026-06-18

## Curadoria canonica de skills

Concluida a curadoria definida em
`docs/superpowers/plans/2026-06-18-canonical-skill-curation.md`.

### Mantidas e compactadas

- owners tecnicos: `game-state-transition-architect`,
  `camera-system-sgdk`, `collision-system-architect`,
  `entity-polymorphism-architect`, `input-system-sgdk`,
  `aaa-pipeline-guardian`, `shadow-highlight-scroll-fx` e
  `vram-streaming-dma-queue`;
- orchestrators: `brawler-game-design`, `platformer-puzzle-game-design`,
  `racing-sports-adventure-game-design`, `rpg-game-design` e
  `strategy-game-design`.

As 13 skills somam 2.615 palavras e possuem contrato operacional e policy de
invocacao coerente com seu papel.

### Quarentena reversivel

Foram registrados 13 payloads legados por hash: 12 `merged` e
`software-tile-rasterizer` como `experimental`. O auditor confirma exclusao da
descoberta ativa, substitutas existentes, hashes e restauracao em fixture
temporaria.

### Especializacoes

Ativas somente:

- `fighting_2d_traditional`;
- `brawler_belt_scroll`;
- `platformer_precision_2d`;
- `racing_arcade`;
- `rpg_turn_based_jrpg`;
- `strategy_tower_defense`.

Entradas sem implementacao completa foram rebaixadas para `deferred`.

### Evidencia de validacao

- `validate_skill_framework.py`: passed;
- `test_skill_lifecycle_registry.ps1`: passed;
- `test_active_skill_routing.ps1`: passed;
- `test_genre_specialization_registry.ps1`: passed;
- cinco testes de orchestrator: passed;
- `validate_aaa_video_curation.py`: passed;
- `assert_agent_environment.ps1`: ready/fresh.

`git diff --check` global continua apontando duas linhas em branco no EOF em
arquivos de treino alheios a esta curadoria. O escopo desta mudanca nao os
alterou.

### Claim ceiling

Nenhuma ROM foi buildada ou executada. A entrega valida governanca,
descoberta, contratos e reversibilidade; nao valida tecnica em hardware.

## Enforcement canonico de claims

- adicionado gate `audit_promotion_claims.ps1`;
- adicionado contrato claim/evidencia/hash da ROM;
- closeout manual deixou de substituir gate executado;
- MTR e MDRT foram formalmente separados;
- reachability deixou de ser inferida por inventario;
- conflito entre relatorios resolve pelo menor status consistente;
- dez fixtures de pressao passaram;
- propostas de aprendizado permanecem `not_applied`.
