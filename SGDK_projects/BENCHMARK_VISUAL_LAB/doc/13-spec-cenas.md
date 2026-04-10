# 13 - Especificacao Tecnica por Cena — BENCHMARK_VISUAL_LAB

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: [NOME]

Scene ID: `[scene_id]`

Tecnicas cobertas:

- `[technique_id_1]`
- `[technique_id_2]`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | [N] | [N] |
| DMA por frame | [N] words | [N] |
| Sprites SAT | [N] | [N] |
| Paletas | [N] | [N] |
| Efeito dominante | [line scroll / column scroll / H-Int / nenhum] | |

### Validation axes

- `boot_emulador`: [ok / falha / nao_testado]
- `gameplay_basico`: [funcional / com_bugs / nao_testado]
- `performance`: [estavel / com_drops / nao_testado]
- `visual_elite`: [ok / alerta / nao_testado]
- `audio`: [ok / com_glitches / nao_testado]

### Evidence bundle

- `benchmark_visual.png`
- `save.sram`
- `visual_vdp_dump.bin`

### Regression group

- `[fx_raster / sprite_engineering / pseudo3d / audio / cross_cutting]`

### Observacoes

- [restricao 1]
- [restricao 2]

---

## Cena: [OUTRA]

Scene ID: `[scene_id]`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | [N] | [N] |
| DMA por frame | [N] words | [N] |
| Sprites SAT | [N] | [N] |
| Paletas | [N] | [N] |

