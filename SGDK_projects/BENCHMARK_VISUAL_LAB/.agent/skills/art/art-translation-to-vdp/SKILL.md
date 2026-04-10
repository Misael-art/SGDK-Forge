---
name: art-translation-to-vdp
description: Use quando houver uma imagem-fonte forte em PNG, concept art, mockup, crop high-res ou arte de IA que precise ser reinterpretada como sprite, sprite sheet, tilemap ou cena para o Mega Drive. Esta skill preserva a alma visual da imagem e a traduz para paleta, grid 8x8, contraste de planos, modularidade e limites reais do VDP. Nao use para apenas diagnosticar o cenario de arte, converter assets ja SGDK-validos sem reinterpretacao, ou buscar arte externa.
---

# Art Translation to VDP

Esta skill existe para o caso em que a imagem e boa, mas nao e hardware.

Ela nao trata o `.png` como asset final.
Ela trata a imagem-fonte como materia-prima.

## Missao

Transformar imagem-fonte em recurso visual de Mega Drive preservando:

- silhueta
- hierarquia visual
- material dominante
- foco da composicao
- impacto de leitura

sem tentar preservar, de forma ingenua, tudo o que o hardware nao suporta.

## Quando usar

Use esta skill quando:

- a IA gerou uma boa imagem-fonte em `.png`
- existe concept art que precisa virar sprite ou tilemap
- o asset parece forte no PC e fraco demais quando reduzido para o Mega Drive
- e preciso preservar a "alma" da imagem em vez de apenas quantizar

## Nao use

- para decidir se o projeto tem ou nao arte
- para buscar assets na web
- para converter automaticamente assets que ja foram desenhados para SGDK
- para validacao puramente pixel-rigida sem problema de traducao visual

## Entradas obrigatorias

- `source_image`
- `translation_target`
  - `sprite_single`
  - `sprite_sheet`
  - `tilemap`
  - `scene_slice`
- `reference_profile`
- `hardware_spec`
- `intent_notes`

## Curadoria e acuracia da skill

Esta skill deve ser treinada com casos canonicos, nao com impressao subjetiva de uma unica imagem.

Pacote minimo de curadoria:

- protocolo: `doc/03_art/04_art_translation_curation_protocol.md`
- sprint: `doc/03_art/03_ai_source_to_vdp_sprint.md`
- manifesto de caso: `tools/image-tools/specs/art_translation_case.template.json`
- avaliador: `tools/image-tools/analyze_translation_case.py`

Regra pratica:

- toda traducao importante deve nascer com `basic` e `elite`
- toda curadoria deve medir delta entre as duas
- toda falha recorrente deve virar heuristica no feedback bank
- toda validacao humana de arte deve apresentar `original + basic + elite` lado a lado
- toda traducao de `tilemap` ou `scene_slice` deve gerar artefatos de review de tileset e paleta por layer

## Checklist obrigatorio

1. Ler `doc/03_art/00_visual_quality_bar.md`
2. Ler `doc/03_art/01_visual_cohesion_system.md`
3. Ler `doc/03_art/02_visual_feedback_bank.md`
4. Aplicar `visual-excellence-standards`
5. Validar contra `megadrive-pixel-strict-rules`
6. Quando houver cena real, consultar `megadrive-vdp-budget-analyst`

## Processo

### 1. Extrair a alma da imagem

Identifique:

- forma dominante
- leitura em miniatura
- material dominante
- detalhe essencial
- detalhe descartavel
- ponto focal

Saida:

- `soul_summary`
- `must_keep`
- `can_simplify`
- `must_drop`

### 2. Traduzir para decisoes de hardware

Defina:

- plano de paleta
- plano de dithering
- plano de separacao de camadas
- plano de reuso de tile
- plano de sprite ou tilemap

Saida:

- `palette_plan`
- `dithering_plan`
- `layer_plan`
- `tile_reuse_plan`

### 3. Gerar duas leituras

Produza sempre:

- `basic_translation`
- `elite_translation`

`basic` serve de controle.
`elite` serve para provar que houve traducao inteligente.

### 4. Validar

O resultado deve passar por:

- `analyze_aesthetic.py`
- validacao pixel-rigida
- budget de VDP quando aplicavel
- prova em ROM com evidencia

### 5. Revisar como tileset, nao apenas como imagem

Toda traducao de `scene_slice` ou `tilemap` deve gerar um pacote de review estrutural:

- `palette_strip` por layer
- `tileset_sheet` por layer
- contagem de tiles totais
- estimativa de reuso por duplicata exata
- estimativa de reuso por `H-Flip`

Objetivo:

- inspecionar se a arte traduzida sobrevive como recurso de tilemap
- revelar desperdicio de VRAM e oportunidades de espelhamento
- separar julgamento estrutural de julgamento estetico

Regra importante:

- `tileset review` e tecnica de inspecao e estruturacao
- nao e permissao para achatar a cena, borrar o fundo ou sacrificar a alma visual so para melhorar a sheet
- se a passada `tile-first` reduzir leitura, material ou profundidade, preserve os artefatos de review e reverta a transformacao visual agressiva

## Outputs obrigatorios

- asset traduzido
- variante `basic`
- variante `elite`
- `translation_report`
- score do `Juiz Estetico`
- evidencia de emulador
- painel humano `original + basic + elite`
- pacote de review estrutural com `tileset_sheet`, `palette_strip` e resumo de reuso

## Comando de avaliacao

```bash
python tools/image-tools/analyze_translation_case.py --manifest <caso.json> --output <laudo.json>
```

O laudo deve sair acompanhado de um painel visual lado a lado para validacao humana:

- `ORIGINAL`
- `BASIC`
- `ELITE`

## Gates

- `input_ok`
  - imagem-fonte e spec existem
- `pixel_ok`
  - regras duras do VDP respeitadas
- `visual_ok`
  - leitura, contraste e material sobrevivem
- `delta_ok`
  - `elite > basic`
- `hardware_ok`
  - cabe no budget
- `emulator_ok`
  - foi visto rodando com evidencia

## Regra de Ouro

Se o feedback humano corrigir a traducao, o ajuste nao vai direto para o PNG.

Primeiro:

1. registrar em `doc/03_art/02_visual_feedback_bank.md`
2. transformar em heuristica preventiva
3. atualizar a skill geral se a regra for reaproveitavel
4. so entao corrigir o asset

## Anti-padroes

- quantizacao cega
- downscale sem redesenho
- excesso de detalhe fino
- dithering decorativo
- fidelidade servil a imagem-fonte
- chamar de "traduzido" o que so foi comprimido
- usar `tileset review` como desculpa para degradar contraste, material ou profundidade da cena
