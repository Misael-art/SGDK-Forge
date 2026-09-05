# Forward-test consolidado de capacidade gráfica — 2026-09-02

## Raiz e método

- `root_resolved`: `/mnt/sdcard/Projects/Sgdk Forge`
- `project_root`: `/mnt/sdcard/Projects/Sgdk Forge/SGDK_projects`
- `canonical_framework_root`: `/mnt/sdcard/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent`
- `scope`: sete diretórios top-level contendo `[GAME]`, inventariados recursivamente; nenhum caminho da raiz `/mnt/sdcard/SGDKForge` foi misturado, pois ele resolve para a mesma raiz por symlink.
- `res_policy`: nenhum `res/` foi alterado pelo forward-test.

## Matriz de estado

| projeto | contexto | diagnóstico de arte | ROM existente | blockers de metodologia/higiene | avanço desta rodada |
|---|---|---|---:|---|---|
| `BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]` | `aaa_game` | `2_res_inadequate_check`; 9 ativos res, 12 fontes, 0 build blockers | sim | higiene 1 | auditado; sem mutação |
| `Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]` | `aaa_game` | `2_res_inadequate_check`; 11 ativos res, 4 fontes, 0 build blockers | sim | higiene 2 | auditado; sem mutação |
| `KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GAME] [ACTION_PLATFORMER]` | `unclassified` | `3_no_art`; 0 assets | não | contexto 1 | preservado como legado não classificável |
| `KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]` | `aaa_game` | `2_res_inadequate_check`; 23 ativos res, 78 fontes, 0 build blockers | sim | metodologia 3; higiene 3 | v05 bitmap temporal produzido, agregado `error`/claim `none`; lineart e revisão cega pendentes |
| `KIRBY_FAN GAME GROK AX ALPHA [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]` | `unclassified` | `3_no_art`; 0 assets | não | contexto 1 | preservado como legado não classificável |
| `KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]` | `aaa_game` | `2_res_inadequate_check`; 26 ativos res, 83 fontes, 0 build blockers | sim | metodologia 1; higiene 4 | auditado; pacote v02 `native_animation_candidate` pré-existente preservado |
| `MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]` | `aaa_game` | `2_res_inadequate_check`; 20 ativos res, 328 fontes, 0 build blockers | sim | nenhum reportado | auditado; sem mutação |

Os números acima são os reports `out/logs/forward_test_v02_art_diagnostic_report.json` de cada projeto. “Sem mutação” significa que o teste não fabricou assets, não promoveu fonte inadequada e não reescreveu `res/`.

## Kirby Cloude GEN — r1

Fonte visual prioritária: `data/source_art/r1/r1-01/concept.png`, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`. A análise de blocos uniformes testou fatores 1/2/4/8 e não provou escala inteira global; portanto o board foi classificado como `visual_source`, não como spritesheet para downscale.

Saída isolada: `out/forward_test_v03_r1/`. Strips separados e hashes estão no `forward_test_summary.md`. As três ações passaram os validadores canônicos de strip, semântica de movimento e integridade de sprite. O agregado passou com `maximum_proven_claim=motion_semantic_candidate`.

O pacote não foi integrado à ROM. O relatório dos 12 princípios está `needs_review`; não existem captura BlastEm, DMA/VRAM runtime ou prova de áudio para esses strips. Os challengers anteriores permanecem somente comparação/negative evidence; não alimentaram pixels novos.

## Kirby Cloude GEN — v04 native temporal

Os strips v03 foram reclassificados como probes mecânicos e não alimentaram o v04. A autoria nativa temporal está em `out/forward_test_v04_native_temporal/`, com quatro ações e quatro frames próprios por ação. Os quatro contratos passaram os gates de artifact, motion semantics e sprite integrity; o agregado validou `maximum_proven_claim=motion_semantic_candidate` e `human_gate_ready=false`.

O pacote permanece `technical_candidate`/`motion_semantic_candidate` de laboratório: `human_gate_status=pending`, `promotable=false`, `res_promotion=false`. O relatório de princípios está `needs_review`, o gate visual está bloqueado e não há ROM, BlastEm, áudio ou medição runtime vinculados. Nenhum `res/` foi alterado.

## Kirby Cloude GEN — v05 visual bitmap temporal

O pacote `out/forward_test_v05_visual_bitmap_temporal/` contém 16 bitmaps independentes, duas hipóteses por ação, quatro strips e evidência offline. Os strips têm hashes `idle=8839cf0677f5e78490aea2055fafa2fe0a23e3b7cbf9e8a9417eca95b5802f6b`, `run=9e927115c4b4cfd564f6c517721715dc9850549191695079a8df0f200b994d6e`, `inhale=baf28a663f3ec4c4257ea57d99c7cd5beb5d80ffbebca4b8817d074f9091ffd1`, `jump_float=4338d521ad07926028c3d4e0c5f33c24930160e96d8e6114cd0316f8617a8bb3`.

O candidato agregado está `error`, com `maximum_proven_claim=none`. Os quatro validadores por strip registram ausência deliberada de lineart nativa separada; a revisão cega ficou `needs_review` e não fechou reconhecimento de ação. O v04 permaneceu imutável, nenhum `res/` foi alterado e não há ROM/BlastEm/áudio/runtime nesta rodada.

## Próximo gap causal por projeto

Cada projeto mantém sua própria escala, paleta e solução; esta lista é apenas roteamento de evidência, não transporte de arte do Kirby.

| projeto | próximo gap causal observável |
|---|---|
| BLUE_CIRCUIT | fechar adequação/proveniência da próxima fonte visual antes de conversão |
| Celestial Chase Revive | fechar adequação dos assets de corrida e a leitura de pista em 4:3 |
| Kirby Cloude legado | classificar contexto e estabelecer uma fonte visual persistida |
| Kirby Cloude GEN | autorar lineart nativa independente e repetir revisão cega das quatro ações |
| Grok AX Alpha | classificar contexto e estabelecer uma fonte visual persistida |
| Grok BUILD | reabrir gate visual do pacote temporal existente com revisão independente |
| MARE_BRAVA | fechar adequação dos assets ativos e o próximo budget de cena, sem promover placeholders |
