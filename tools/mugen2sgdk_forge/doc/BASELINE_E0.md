# Baseline E0 — 2026-09-22

## Referencia historica (release `hamoopig-original-v001-recovered-20260922`)

| Artefato | SHA-256 | Verificado |
|---|---|---|
| hamoopig-first-rom.bin (2.490.368 B) | 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f | ✅ bate com o publicado |
| hamoopig-first-tracked-source.tar.gz | 823952c48c0192f14a288427c768afacdecb7dd4dc17c8c4d5f7192b0ad10cea | ✅ bate com o publicado |
| commit 19eb8fae (primeira fonte rastreada) | — | ✅ existe no historico |

Vinculo fonte↔ROM **nao comprovado** (build_meta aponta e224af09, anterior ao HAMOOPIG).

## Estado do repositorio

- Worktree principal: branch `codex/taiketsu-ultra-rebirth-aaa`, HEAD `dee2356e`,
  21 arquivos modificados + nao rastreados do usuario (HAMOOPIG, skills, audiovisual_review,
  TAIKETSU ULTRA REBIRTH, `.zcode/`). Intocados.
- ROM atual `HAMOOPIG/out/rom.bin` = `9018c2c2…a9d` (build pos-P03), diferente da ROM historica.

## Riscos

| Risco | Nivel | Mitigacao |
|---|---|---|
| Licenca do acervo (ripagens SNK/Capcom) | alto | status unknown por padrao; conteudo fora do Git |
| CNS/CMD/IA nao traduziveis automaticamente | alto | relatorio de fidelidade; reimplementacao manual declarada |
| Orcamento VDP (sprites grandes, 256 cores) | alto | analysis/ antes de gerar; saida = technical_candidate |
| Tooling Linux quebrado (build.sh) | medio | ponte Wine para build |
| Pastas lixo de split de caminho no HAMOOPIG | baixo | removidas 2026-09-22 (vazias, nao rastreadas) |
| `tools/mugen2sgdk` legado sem fonte | baixo | nao reutilizar; apenas referencia |
