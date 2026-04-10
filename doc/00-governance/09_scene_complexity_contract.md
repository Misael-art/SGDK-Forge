# SCENE COMPLEXITY CONTRACT

Toda cena DEVE conter a seguinte estrutura obrigatoriamente para ser aprovada:

## Estrutura
- 3+ camadas visuais (ex: fundo longo, fundo médio, foreground)
- 1 FX principal
- 2–4 FX secundários
- 1 sistema reativo ao jogador

## Dinâmica Temporal
- Estado base (ex: vento leve)
- Estado intensificado (ex: vento forte)
- Estado de pico (ex: rajada + folhas)
- Retorno ao normal

## Uso de Hardware
- Uso de VRAM próximo ao limite
- Uso de DMA planejado
- Uso de pelo menos 1 técnica avançada obrigatória:
  - Line scroll / raster effects associados as camadas
  - Palette cycling para simular movimento ou luz
  - Raster split
  - Tile streaming dinâmico
  - Shadow/Highlight mode combinado com Sprites ou Planos

## Proibições
- Cena com comportamento estático do início ao fim
- FX constantes sem variação ao longo do tempo
