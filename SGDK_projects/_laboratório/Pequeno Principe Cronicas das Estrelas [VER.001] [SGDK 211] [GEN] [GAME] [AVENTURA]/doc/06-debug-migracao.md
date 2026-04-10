# 06 - Debug e Migracao

## Quebras que este projeto ja tratou

- `VSCROLL_2TILE` antigo substituido por `VSCROLL_COLUMN`
- exemplos comentados do template removidos de `resources.res`
- H-Int isolado em modulo proprio

## Se o build quebrar

Verifique nesta ordem:

1. `build_debug.log` dentro de `out/logs/`
2. chamadas SGDK deprecadas
3. conflito de paleta ou registrador entre cena e callback
4. redraw excessivo em planetas

## Cuidados com H-Int

- restaurar a paleta no VBlank
- nao espalhar callbacks por varios arquivos
- proteger lotes grandes de escrita no VDP com `SYS_disableInts()`

## Cuidados com scroll

- `BG_A` e `BG_B` compartilham o budget de atualizacao
- deixe linhas fora da area de efeito zeradas
- column scroll deve ser usado com parcimonia para evitar ruido visual
