# Changelog — FORGE_REFERENCE

## 2026-09-09 — migração isolada do instrumento e E2E Linux

- migrado `.agent/scripts/vdp_scanline_simulator.py` local para a versão
  canônica 1.2.0, sem sobrescrever os demais arquivos `.agent` do projeto;
- hashes local e canônico reconciliados: `5b0afd5b20d3993468a62c562f2cea2e14b767c5acfa7de12e2d7f880915b3ab`;
- self-check passou com geometria de células, limites H40/H32 e headroom;
- `run_reference_e2e.py` passou em `20260909T140954873448Z`, com a ROM
  `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`;
- bundle BlastEm vigente: `out/blastem_env_e2e_20260909T140954873448Z/blastem-linux-20260909T141046Z-2069272`;
- escopo permanece `technical_fixture_contracts`, `ready_for_aaa=false`.

## 2026-08-05 — criação e promoção cirúrgica

- criado projeto neutro via bootstrap canônico;
- classificado como `technical_demo`, sem claim AAA;
- implementado bloco SRAM versionado `FREF`;
- implementado playtest determinístico com estados marcados pela ROM;
- implementada prova de elisão de trabalho byte-idêntico;
- adicionadas regressões canônicas para os sete contratos;
- reforçado loop de aprendizado: E4 exige bundle selado e gate aprovado com o
  mesmo SHA-256 da ROM;
- validação host inicial: 10/10 e 36/36; build/BlastEm ainda não registrados
  neste ponto do changelog.

## 2026-08-06 — prova em ROM

- removidos os diretórios herdados `res/branding` e `res/audio/branding`; são
  reproduzíveis pelo template, mas não pertencem à fixture neutra;
- rebuild Linux/Wine concluído sem warnings e sem recursos externos;
- primeira captura executável rejeitada por densidade visual baixa e VLAB
  ausente; o gate permaneceu inalterado;
- cena enriquecida com grid geométrico neutro e exportador `VLAB` real
  (24 métricas + 64 palavras de CRAM);
- bundle BlastEm `blastem-linux-20260806T023359Z-197827` selado sem blocker;
- gate `FREF` final: 7 contratos, status `passed`, 229 amostras, 0 violações,
  cobertura observada `0x0007`, frame 270;
- ROM e todos os relatórios: SHA-256
  `1167b7597491cf02f264c5031771925149eaba86c48d3d0747c8f18114b82dc3`;
- `ready_for_aaa=false`: a fixture prova contratos técnicos, não produto AAA.
- revisão formal detectou colisão de SRAM entre o runtime probe (`0x0000`) e o
  bloco `VLAB`; o probe foi movido para `0x0200` antes do fechamento;
- a evidência anterior foi invalidada após essa mudança de ROM e substituída
  pela sessão `blastem-linux-20260806T024237Z-253942`;
- ROM e gate finais recapturados: SHA-256
  `79020498f34d0ca4b8d2907659c82d4f605c77ecf5a8a650a09e478c1002f337`,
  bundle selado, sete contratos aprovados e nenhum blocker.


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
