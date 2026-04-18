# 04 - Recursos e Pipeline

## Estado atual

O slice agora e hibrido:

- base de cena, UI e varios tiles continuam procedurais em `src/render/render.c`
- os 4 marcos centrais entraram como `TILESET` via `rescomp`
- a paleta compartilhada de sprite entrou como `PALETTE`
- encontros usam `WAV` curtos no driver `XGM2`

Isso preserva a disciplina da Fase 1 e ja testa o pipeline real de recurso final.

## Pipeline em uso

Entradas declaradas hoje em `resources.res`:

- `PALETTE pal_sprite_stage`
- `TILESET` para `rose`, `throne`, `lamp` e `desert mark`
- `WAV` para voz curta e micro-SFX dos encontros

Entradas ainda previstas para fases seguintes:

- `SPRITE` para personagem final e FX mais ricos
- `IMAGE` para telas especiais
- `XGM2` para trilha de fundo

## Regras de asset

- 15 cores + 1 transparente por paleta
- multiplos de 8 pixels
- fundos pensados em tilemap
- degrade real substituido por cell shading e dithering

> **Regras completas de producao, validacao e checklist de assets visuais:**
> `doc/15-diretrizes-producao-assets.md` (leitura obrigatoria para agentes de arte)

## Estrutura sugerida

- `res/gfx/`
- `res/ui/`
- `res/audio/`
- `tmp/imagegen/inbox/pequeno_principe_v2/`

## Lotes externos

Assets vindos de geradores externos nao entram direto em `res/`. Para gerar o lote via agente de IA, use o skill **pequeno-principe-art-production** (ex.: "gerar lote de arte Pequeno Príncipe"); em seguida rode o validador e a promoção.

Fluxo adotado:

1. o lote chega em `tmp/imagegen/inbox/pequeno_principe_v2/`
2. a validacao roda via `tools/image-tools/validate_pequeno_principe_asset_batch.ps1`
3. a promocao segura roda via `tools/image-tools/promote_pequeno_principe_asset_batch.ps1`
4. so lotes com `PASS` podem ser promovidos para `res/`
5. lotes reprovados devem ser arquivados apenas como referencia visual

## Regra usada nos marcos centrais

1. arte desenhada em grid de `16x16`
2. conversao para BMP indexado com paleta mestre
3. declaracao como `TILESET ... NONE NONE ROW`
4. carga em VRAM no boot e uso como um unico sprite `2x2` por planeta

## Prompt-base para IA de imagem

`Little Prince, hand drawn crayon texture, thick ink outlines, flat pastel colors, no gradients, simple shapes, tile friendly, Sega Mega Drive palette discipline`

Depois da geracao:

1. reduzir para paleta valida
2. alinhar ao grid de 8x8
3. recortar em sprite sheet ou tilemap
4. declarar no `resources.res`
