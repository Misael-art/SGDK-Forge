# 06 - Debug e Migracao — BENCHMARK_VISUAL_LAB

## Quebras que este projeto ja trata

- APIs deprecadas do SGDK 1.60 convertidas para 2.11 via `fix_migration_issues.ps1`
- exemplos comentados do template removidos de `resources.res`

## Se o build quebrar

Verifique nesta ordem:

1. `build_debug.log` dentro de `out/logs/`
2. chamadas SGDK deprecadas (ver `doc/migrations/`)
3. conflito de paleta ou registrador entre cena e callback
4. redraw excessivo em cenas

## Cuidados com H-Int

- restaurar a paleta no VBlank
- nao espalhar callbacks por varios arquivos
- proteger lotes grandes de escrita no VDP com `SYS_disableInts()`

## Cuidados com scroll

- `BG_A` e `BG_B` compartilham o budget de atualizacao
- deixe linhas fora da area de efeito zeradas
- column scroll deve ser usado com parcimonia para evitar ruido visual

