# Memory Bank — FORGE_REFERENCE

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
