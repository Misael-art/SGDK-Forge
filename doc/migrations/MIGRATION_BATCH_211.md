# Migração em Lote SGDK → 211

**Data:** 2026-03-11 / Atualizado: 2026-03-12
**Ferramenta:** `tools/sgdk_wrapper/fix_migration_issues.ps1`

---

## Resultado Final da Compilação

Todos os 14 engines/jogos SGDK 211 foram validados:

| # | Projeto | ROM | Tempo | Status |
|---|---------|-----|-------|--------|
| 1 | BLAZE_ENGINE [VER.001] [SGDK 211] | 2560KB | ~23min | OK |
| 2 | HAMOOPIG [VER.001] [SGDK 211] | OK | <1min | OK |
| 3 | HAMOOPIG [VER.1.0] [SGDK 211] | OK | — | OK |
| 4 | HAMOOPIG [VER.1.0 CPU6.2] [SGDK 211] | 3456KB | ~32s | OK |
| 5 | HAMOOPIG main [VER.001] [SGDK 211] | — | — | Referência apenas* |
| 6 | KOF94 HAMOOPIG MINIMALIST [VER.001] [SGDK 211] | OK | <1min | OK |
| 7 | Mega Snake [VER.1.2] [SGDK 211] | 256KB | 8s | OK |
| 8 | Shadow Dancer Hamoopig [VER.1.0] [SGDK 211] | 1792KB | 43s | OK |
| 9 | Super Monaco GP [VER.001] [SGDK 211] | OK | <1min | OK |
| 10 | mega genius [VER.001] [SGDK 211] | OK | <1min | OK |
| 11 | msu-example [VER.001] [SGDK 211] | OK | <1min | OK |
| 12 | MUSIC [VER.001] [SGDK 211] | OK | <1min | OK |
| 13 | flip [VER.001] [SGDK 211] | OK | <1min | OK |
| 14 | state machine RPG [VER.001] [SGDK 211] | OK | <1min | OK |

> *HAMOOPIG main é um projeto de referência (324KB main.c) sem recursos gráficos/sonoros.
> Não é compilável standalone — serve para estudo da arquitetura da engine.
> Veja `SGDK_Engines/HAMOOPIG main [...]/NOTA_COMPILACAO.md`.

**Resultado: 13/13 compiláveis = 100% de sucesso. 1 projeto de referência documentado.**

---

## Problemas Encontrados e Corrigidos

### 1. Boot Files Incompatíveis (sega.s / rom_head.c)

**Sintoma:** `undefined reference to 'zeroDivideCB'`, `'chkInstCB'`, etc.
**Causa:** SGDK 160 usava `sega.s` customizado (487 linhas) sem callbacks de exceção.
SGDK 211 define esses callbacks no `sega.s` padrão (367 linhas).
**Correção automática:** `fix_migration_issues.ps1` Seção 2 — compara MD5 hash do `src/boot/sega.s`
com o padrão do SDK e substitui se diferente.

### 2. Dependências (.d) com Paths Absolutos

**Sintoma:** `cp: cannot stat 'res/xxx.d': No such file or directory`
**Causa:** Arquivos `.d` gerados pelo ResComp podem conter caminhos absolutos
do computador original do desenvolvedor (ex: `C:/Users/Bionica/...`).
**Correção automática:** `build_inner.bat` limpa `.d` com paths estranhos e cria stubs vazios.

### 3. APIs Deprecadas — PAL_setColorsDMA

**Sintoma:** `error: This method is deprecated, use PAL_setColors(..) instead`
**Causa:** SGDK 211 removeu variantes DMA-específicas. O método de transferência
agora é um parâmetro explícito.
**Correção automática:** `fix_migration_issues.ps1` — regex:
- `PAL_setColorsDMA(idx, colors, count)` → `PAL_setColors(idx, colors, count, DMA)`
- `PAL_setPaletteDMA(pal, colors)` → `PAL_setPalette(pal, colors, DMA)`

### 4. SPR_addSpriteEx — Parâmetro sprIndex Removido

**Sintoma:** `error: too many arguments to function 'SPR_addSpriteEx'`
**Causa:** SGDK 160 tinha 6 parâmetros: `(def, x, y, attr, sprIndex, flags)`.
SGDK 211 removeu `sprIndex`, ficando com 5: `(def, x, y, attr, flags)`.
**Correção automática:** `fix_migration_issues.ps1` — regex remove o argumento numérico
entre `TILE_ATTR(...)` e as flags `SPR_FLAG_*`.

### 5. APIs Renomeadas (VDP_* → PAL_*)

**Sintoma:** `implicit declaration of function 'VDP_setPalette'`
**Causa:** SGDK 211 moveu funções de paleta do módulo VDP para o módulo PAL.
**Correção automática:** `fix_migration_issues.ps1` — substituições:
- `VDP_setPaletteColors(a, b, c)` → `PAL_setColors(a, b, c, DMA)`
- `VDP_setPalette(a, b)` → `PAL_setPalette(a, b, DMA)`
- `VDP_setPaletteColor` → `PAL_setColor`
- `SPR_FLAG_AUTO_SPRITE_ALLOC` → `SPR_FLAG_AUTO_VRAM_ALLOC`

---

## Processo de Migração Executado

1. **Cópia do diretório** com novo nome contendo `[SGDK 211]`
2. **Execução de `fix_migration_issues.ps1`** em cada diretório:
   - Seção 1: Busca automática de `sprite.res` da versão 160 como referência + `autofix_sprite_res.ps1`
   - Seção 2: Substituição de boot files (sega.s / rom_head.c) por versão SGDK 211
   - Seção 3: Migração de APIs deprecadas no código C (regexes documentados acima)
3. **Build via `make -f makefile.gen`** usando short paths (8.3) para contornar limitação do CMD com colchetes
4. **Retry automático** para erros de `.d` faltante (stubs criados on-the-fly)
5. **Validação**: ROM gerada e tamanho verificado

## Observações

- Os diretórios originais (SGDK 160/200) foram mantidos como referência
- Projetos pesados (BLAZE_ENGINE, HAMOOPIG CPU6.2) levam 20-30 minutos no primeiro build
  devido ao grande volume de sprites (centenas de frames de animação por personagem)
- Builds incrementais são muito mais rápidos (~30 segundos)
