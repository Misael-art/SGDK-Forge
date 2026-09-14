# Memory Bank — FORGE_REFERENCE

## Atualizacao vigente — 2026-09-09: F01 instrumento migrado e E2E recertificado

- o instrumento local `.agent/scripts/vdp_scanline_simulator.py` foi migrado
  isoladamente de 1.1.0 para a versão canônica 1.2.0;
- SHA local e canônico agora coincidem em
  `5b0afd5b20d3993468a62c562f2cea2e14b767c5acfa7de12e2d7f880915b3ab`;
- `--self-check` passou com decomposição geométrica, os dois limites de
  scanline e H32;
- E2E canônico `20260909T140954873448Z` passou todos os passos, preservando a
  ROM `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`;
- FREF observado: frame 360, 319 amostras, zero violações, cobertura
  `observed/required=7`, bundle em
  `out/blastem_env_e2e_20260909T140954873448Z/blastem-linux-20260909T141046Z-2069272`;
- esta prova cobre somente `technical_fixture_contracts`; áudio, performance
  sustentada, qualidade de jogo e AAA continuam sem certificação.

## Estado operacional

- contexto: `technical_demo` / fixture canônica neutra;
- claim ceiling: `technical_fixture_contracts`;
- `ready_for_aaa`: `false`;
- arte ativa: primitives/texto do SGDK; nenhum IP ou asset de caso-fonte;
- código ROM-side `FREF`: `testado_em_emulador`, frame 270, 229 amostras e
  zero violações;
- regressão host: `test_canonical_fixture_contracts.py`, 10/10 em 2026-08-05;
- aprendizado com identidade de ROM: `test_project_learning_loop.py`, 36/36 em
  2026-08-05 usando dependências herméticas;
- build: `buildado` no Linux pelo bridge SGDK 2.11/Wine, sem warning de C e com
  `resources.res` em 0 KB;
- emulador: `testado_em_emulador` no BlastEm Linux, bundle selado sem blocker;
- ROM SHA-256: `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`;
- sessão: `blastem-linux-20260806T024237Z-253942`;
- playtest observado: `requested=0x0003`, `observed=required=0x0007`,
  `completed=true`;
- gate final: `passed`, sete contratos, um warning intencional de campo
  opcional ausente, `ready_for_aaa=false`.
- revisão formal: colisão entre o runtime probe e o bloco `VLAB` corrigida ao
  mover `MD_RUNTIME_PROBE_SRAM_OFFSET` para `0x0200`; a sessão atual foi
  recapturada somente depois dessa correção.

## Sete contratos promovidos

1. denominador zero nunca aprova gate amostrado;
2. telemetria versionada tolera campo opcional ausente e falha fechado no
   obrigatório;
3. playtest conta estados observados pela ROM, não pedidos do script;
4. CRAM/dump é autoridade para cor em raster, screenshot é informativo;
5. bundle, gate e aprendizado compartilham SHA-256 de ROM;
6. payload byte-idêntico não é reconstruído/enviado antes de degradar;
7. cada gate declara escopo e não extrapola `static_contract`.

## Próxima ação segura

Corrigir os blockers preexistentes do runner amplo no host (shim `powershell` e
cache do `uv`), capturar uma execução Windows real quando disponível e manter a
fixture pequena. Não declarar áudio, performance sustentada ou AAA: estas
grandezas não foram provadas por este escopo.


## Regressao da cadeia Linux — 2026-09-07

- Runner `tools/sgdk_wrapper/ci/run_reference_e2e.py`: `passed` nesta sessao.
- ROM SHA-256: `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`; 131072 bytes, reproduzindo o binario historico.
- Evidencia vigente da regressao: `out/blastem_env_e2e_20260907T202559306613Z/blastem-linux-20260907T202650Z-2364411/`.
- FREF: frame 390, 349 amostras, zero violacoes; observed/required=7, completed=true.
- Screenshot dedicado inspecionado, SRAM e VDP dump selados no mesmo hash.
- Escopo: `technical_fixture_contracts`; nao certifica visual, audio, estabilidade
  sustentada, campanha ou AAA. `ready_for_aaa=false`.
- As duas tentativas anteriores bloqueadas estao preservadas nos logs E2E;
  biblioteca em cold build teve hang de Wine nao atribuido a causa conclusiva.
- A instrumentacao local nao foi migrada nesta rodada; drift permanece visivel
  no meta-gate global. A prova FREF cobre somente os contratos observados.


## Atualizacao vigente — 2026-09-08: cold build observado

A execucao `20260907T203646582966Z` recompilou a biblioteca (`library_rebuild=true`)
e o jogo na mesma sessao Flatpak/Wine, depois fechou captura e FREF no BlastEm.
O log comprova os dois makes; o problema de passagem entre sessoes deixou de
se reproduzir nessa execucao. Nao e certificacao de todos os hosts.

ROM `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`, 131072 bytes, mesmo binario de referencia.
FREF: frame 360, 319 amostras, zero violacoes; observed/required=7, completed=true.
Screenshot inspecionado. Bundle vigente desta rodada:
`out/blastem_env_e2e_20260907T203646582966Z/blastem-linux-20260907T204142Z-2440026`.
Report historico preservado: `out/logs/reference_e2e_20260907T203646582966Z_report.json`.

A cura segura de caminhos ausentes foi executada por ensure_project_agent;
a `.agent` existente continua versao 2026.06.19 contra canonica 2026.09.05,
com `architecture_drift`. Arquivos existentes nao foram sobrescritos.
Prova de ROM nao apaga esse blocker da CI ampla.
