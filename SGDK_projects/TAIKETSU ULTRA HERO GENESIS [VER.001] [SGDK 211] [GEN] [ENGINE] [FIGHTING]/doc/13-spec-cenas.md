# 13 - Especificacao Tecnica por Cena - TAIKETSU ULTRA HERO GENESIS [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e outras telas de front-end contam como cenas formais.

## Contexto de escala

Contexto do projeto: `technical_demo` (porta direta da engine TaiketsuUltraHeroGenesis). Teto de claim: `prototype`.
Os budgets abaixo sao os observados na engine upstream, NAO metas de producao AAA deste workspace.
Nao ha cenas autorais novas neste contexto; as cenas existem porque a engine upstream as define
(salas selecionadas por `gRoom` no loop principal de `src/main.c`).

## scene_roadmap

### Cena 0 - `ROOM_TELA_HAMOOPIG` (abertura)

- origem: engine upstream (main.c, funcao ROOM_TELA_HAMOOPIG)
- conteudo observado: salao de grade com logo, fade de paleta, avanca para descompressao/arena
- incidente corrigido nesta porta: stack overflow de palette[64] (ver `doc/10-memory-bank.md`)
- evidencia pre-fix do crash: `out/emulator_evidence/blastem-linux-manual-20260910T193317Z/screenshot.png`

### Cena 1 - `R_IN_GAME` (arena de combate 1v1)

- origem: engine upstream (main.c monolitico; XGM_setPCM para SFX; sprite engine via SPR_initEx(600))
- conteudo observado no BlastEm: arena deserto/montanha com dois lutadores a 60 fps
- paletas por lutador via truque HAMOOPIG de sprites-paleta; 28 simbolos spr_* sao placeholder (ver `doc/18-asset-register.json`)
- evidencia: `out/emulator_evidence/blastem-linux-manual-20260910T193902Z/screenshot.png`

## Contrato de evidencia desta porta

- build: `out/logs/linux_wine_build_report.json` (wine_bridge_status=buildado)
- boot: sessoes BlastEm em `out/emulator_evidence/` com screenshot + save.sram + log
- audio: NAO provado (placeholders silenciosos declarados em `doc/18-asset-register.json`)
