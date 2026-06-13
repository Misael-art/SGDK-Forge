# 03 - AI Source to VDP Sprint

## Objetivo

Esta sprint existe para treinar o agente a fazer o trabalho que os geradores de imagem normalmente nao fazem bem: traduzir uma imagem-fonte forte em um asset que realmente sobreviva ao hardware do Mega Drive.

O alvo nao e "gerar arte Mega Drive pronta" direto da IA.
O alvo e:

1. usar a IA para gerar uma boa imagem-fonte em `.png`
2. identificar a alma visual dessa imagem
3. reinterpretar a imagem como recurso de VDP
4. provar em ROM que a traducao ficou legivel, eficiente e dramaticamente forte

## Quando esta sprint entra

Use esta sprint quando:

- o projeto possui uma imagem-fonte forte, mas nao um asset pronto para o Mega Drive
- a IA gerou um `.png` bonito, mas hardware-incompativel
- existe concept art, frame pintado, mockup, splash, crop high-res ou pintura de referencia que precisa virar sprite, sprite sheet, tilemap ou composicao de planos

Nao use esta sprint quando:

- o projeto ja tem assets SGDK validos e so precisa conversao tecnica
- o projeto ainda nao tem nenhuma arte e ainda esta decidindo entre gerar com IA ou buscar assets externos
- o trabalho for apenas auditoria pixel-rigida sem intencao de preservar a identidade visual da imagem-fonte

## O que a sprint valida

Esta sprint valida a capacidade do agente de separar:

- o que precisa ser preservado
- o que precisa ser simplificado
- o que precisa ser descartado
- o que precisa ser reinterpretado via paleta, dithering, massa, contraste e modularidade

## Entradas obrigatorias

Cada rodada da sprint deve ter:

- `source_image`
  - imagem-fonte principal em `.png`
- `translation_target`
  - `sprite_single`
  - `sprite_sheet`
  - `tilemap`
  - `scene_slice`
- `reference_profile`
  - perfil de referencia Mega Drive
- `hardware_spec`
  - tamanho alvo
  - limite de cores
  - papel de paleta
  - budget de tiles
  - restricoes de sprite ou plano
- `intent_notes`
  - o que nao pode se perder da imagem

## Checklist de leitura antes da traducao

1. Ler `doc/03_art/00_visual_quality_bar.md`
2. Ler `doc/03_art/01_visual_cohesion_system.md`
3. Ler `doc/03_art/02_visual_feedback_bank.md`
4. Ler a skill `visual-excellence-standards`
5. Ler a skill `megadrive-pixel-strict-rules`
6. Se a cena ja existir, conferir budget de VDP e papel do asset no gameplay

## Processo canonico

### Fase 1 - Extracao de alma visual

Antes de mexer na imagem, o agente deve responder:

- qual e a silhueta dominante?
- qual e o material dominante?
- onde esta o foco visual?
- o que comunica volume?
- o que e detalhe essencial?
- o que e detalhe descartavel?

Saida minima:

- `soul_summary`
- `must_keep`
- `can_simplify`
- `must_drop`

### Fase 2 - Mapa de traducao para hardware

O agente deve converter estetica em decisoes de VDP:

- paleta principal
- rampa tonal
- papel de cada cor
- areas candidatas a dithering
- estrategia de outline
- estrategia de separacao BG_A / BG_B / sprite
- oportunidades de reuso por tile ou flip

Saida minima:

- `palette_plan`
- `dithering_plan`
- `layer_plan`
- `tile_reuse_plan`

### Fase 3 - Basico vs Elite

Toda traducao importante deve gerar duas versoes:

- `basic_translation`
  - conversao mais direta e simples
- `elite_translation`
  - melhor interpretacao seguindo `visual-excellence-standards`

O objetivo nao e publicar a versao basica. O objetivo e medir o salto qualitativo.

### Fase 4 - Conversao real

O agente deve produzir o asset-alvo:

- sprite unico
- sprite sheet
- tileset
- tilemap
- ou slice de cena

Sempre com:

- grid 8x8 valido
- paleta controlada
- transparencia correta
- dimensoes compativeis com SGDK
- organizacao clara para o pipeline

### Fase 5 - Juizo tecnico e estetico

Rodar:

- `analyze_aesthetic.py`
- validacao pixel-rigida
- budget de VDP quando aplicavel

Comparar `basic` vs `elite`.

### Fase 6 - Prova em ROM

Se nao foi visto no emulador, nao existe.

O asset traduzido deve ser provado em:

- `BENCHMARK_VISUAL_LAB`
- ou projeto-alvo com captura rastreavel

Evidencia minima:

- screenshot
- `save.sram`
- `visual_vdp_dump.bin`
- `benchmark_quicksave.state` quando disponivel

## Outputs obrigatorios

Cada rodada da sprint deve produzir:

- asset traduzido
- variante `basic`
- variante `elite`
- `translation_report`
- score do `Juiz Estetico`
- evidencia de emulador
- heuristicas novas quando houver aprendizado real

## Formato minimo do translation_report

```json
{
  "source_image": "...",
  "translation_target": "sprite_sheet",
  "soul_summary": "...",
  "must_keep": [],
  "can_simplify": [],
  "must_drop": [],
  "palette_plan": {},
  "dithering_plan": {},
  "layer_plan": {},
  "tile_reuse_plan": {},
  "basic_asset": "...",
  "elite_asset": "...",
  "analysis_report": "...",
  "benchmark_status": "...",
  "evidence": {}
}
```

## Gates

### Gate 1 - Entrada valida

- existe imagem-fonte
- existe spec de hardware
- existe alvo de traducao

### Gate 2 - Conformidade pixel-rigida

- paleta valida
- grid 8x8 valido
- index 0 coerente
- limites por tile respeitados

### Gate 3 - Barra visual

- silhueta legivel
- contraste entre planos
- dithering funcional quando necessario
- material nao virou massa plastica
- o asset nao perdeu a alma da imagem-fonte

### Gate 4 - Delta real

- `elite > basic`
- delta minimo declarado no caso de benchmark

### Gate 5 - Hardware

- cabe em VRAM
- nao degrada scanline de forma indevida
- nao explode o custo de sprite sheet

### Gate 6 - Evidencia

- rom vista em emulador
- captura rastreavel preservada

## Regras de canonizacao

Quando a traducao falhar com feedback humano do tipo:

- "o metal parece plastico"
- "o rosto virou borrado"
- "o fundo engoliu o personagem"
- "ficou detalhado no PC e morto no Mega Drive"

o fluxo obrigatorio e:

1. registrar o sintoma em `doc/03_art/02_visual_feedback_bank.md`
2. escrever a heuristica preventiva
3. atualizar a skill mestra se a regra for geral
4. so entao refazer a traducao

## Anti-padroes

- quantizacao cega como substituto de direcao de arte
- reduzir resolucao sem redesenho estrutural
- preservar detalhe fino que nao sobrevive em 320x224
- usar dithering como ruido decorativo
- respeitar a imagem-fonte mais do que respeitar o gameplay
- chamar de "Mega Drive" um asset que so ficou menor

## Criterio de sucesso

Esta sprint so esta concluida quando:

- a versao `elite` vence a `basic`
- o asset traduzido funciona em ROM
- o agente explica o que preservou e o que sacrificou
- o aprendizado vira memoria reutilizavel
