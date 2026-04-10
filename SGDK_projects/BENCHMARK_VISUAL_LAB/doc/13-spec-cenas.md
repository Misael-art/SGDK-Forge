# 13 - Especificacao Tecnica por Cena — BENCHMARK_VISUAL_LAB

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: [NOME]

Scene ID: `[scene_id]`

Intencao da cena: `[intencao_da_cena]`

Signature moment: `[signature_moment]`

Causa de gameplay: `[causa_de_gameplay]`

Tecnicas cobertas:

- `[technique_id_1]`
- `[technique_id_2]`

Secondary FX pairings:

- `[secondary_fx_1]`
- `[secondary_fx_2]`

Operational policy: `[default_safe / advanced_tradeoff / special_scene_only / hazardous_experimental]`

hint_owner: `[none / system_name]`

hint_callback_contract: `[na / callback_name + reset_policy]`

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
- [por que a tecnica existe nesta cena]

---

## Cena: [OUTRA]

Scene ID: `[scene_id]`

Intencao da cena: `[intencao_da_cena]`

Signature moment: `[signature_moment]`

Causa de gameplay: `[causa_de_gameplay]`

Operational policy: `[default_safe / advanced_tradeoff / special_scene_only / hazardous_experimental]`

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| VRAM (tiles) | [N] | [N] |
| DMA por frame | [N] words | [N] |
| Sprites SAT | [N] | [N] |
| Paletas | [N] | [N] |

