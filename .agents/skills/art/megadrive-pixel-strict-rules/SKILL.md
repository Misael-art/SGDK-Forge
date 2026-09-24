---
name: megadrive-pixel-strict-rules
description: Use para validar ou corrigir conformidade absoluta de sprites, tilesets e backgrounds com as restricoes rigidas de pixel art do VDP do Mega Drive: paleta, index 0, grid 8x8, cores validas e limites por tile. Nao use para decidir sourcing de arte, analisar budget global da cena ou conduzir direcao estetica mais subjetiva.
---

# Mega Drive Pixel Strict Rules

Estas sao as restricoes absolutas do hardware grafico do Mega Drive. Nenhuma excecao e permitida. Todo asset, sprite, tileset ou cenario DEVE obedecer a cada regra abaixo antes de ser aceito no pipeline.

---

## 1. Cor indexada 4-bits

- Cada tile usa **exatamente 1 paleta** de 16 entradas.
- **Index 0 e obrigatoriamente transparente** (convencao: magenta `#FF00FF` no PNG fonte).
- Maximo de **15 cores visiveis** por paleta.
- O VDP possui **4 paletas** (PAL0-PAL3) = 64 entradas totais (60 cores visiveis + 4 transparentes).

## 2. Resolucao de cor 9-bits

Cada canal (R, G, B) tem 3 bits = 8 niveis. Os unicos valores validos em hexadecimal por canal sao:

```
0x00  0x22  0x44  0x66  0x88  0xAA  0xCC  0xEE
```

Qualquer cor fora deste grid de 512 cores sera rejeitada. Nao existe dithering automatico de paleta no hardware.

## 3. Grid 8x8 obrigatorio

- Todo tile tem **8x8 pixels**, sem excecao.
- Sprites sao compostos por blocos de tiles: 1x1, 1x2, 2x1, 2x2, 1x3, 3x1, 1x4, 4x1, 2x2, 2x3, 3x2, 2x4, 4x2, 3x3, 3x4, 4x3, 4x4.
- Tamanho maximo de sprite hardware: **4x4 tiles** = 32x32 pixels.
- Sprites maiores exigem metasprite (multiplas entradas na sprite table).

## 4. Escala 1x

- Todo pixel desenhado deve ser **1:1 com o pixel do VDP**.
- Nao existe scaling por hardware (sem Mode 7, sem zoom).
- Se precisar de escala, pre-renderize frames em diferentes tamanhos como tiles separados.

## 5. Bounding box justo

- Sprites devem ter o **menor retangulo possivel** que contenha os pixels visiveis.
- Area transparente desperdicada dentro do bounding box e VRAM perdida.
- Recorte bordas vazias antes de exportar.

## 6. Tile flipping via hardware

- O VDP suporta flip horizontal e vertical por tile.
- **Reutilize tiles espelhados** em vez de duplicar no tileset.
- Ao projetar cenarios simetricos, projete metade e espelhe via atributos do tilemap.

## 7. Economia de VRAM

- VRAM total: **64 KB** (2048 tiles de 32 bytes cada, dos quais ~1536 ficam disponiveis apos reserva de scroll tables e sprite table).
- Cada tile ocupa **32 bytes** (8x8 pixels x 4 bits).
- Compartilhe tiles entre sprites e cenarios sempre que possivel.
- Priorize reuso de tiles duplicados, espelhados ou com paleta alternada.

---

## Proibicoes absolutas

Estas tecnicas **nao existem** no hardware e devem ser bloqueadas em qualquer etapa do pipeline:

1. **Anti-Aliasing** — nao existe. Bordas de sprite sao hard-edge. Nunca suavize bordas com cores intermediarias pensando em blending.
2. **Canal Alpha / Opacidade parcial** — nao existe. Pixel e 100% visivel ou 100% transparente (index 0). Sem semi-transparencia.
3. **Baked Lighting complexo** — proibido assar iluminacao gradiente nos tiles. Use shadow/highlight do VDP (modo S/H) ou engine para simular. Dithering manual controlado e aceito.
4. **Sombras assadas na arte** — proibido pintar sombra como parte do sprite. Use shadow bit do VDP ou sprites de sombra simples via engine.
5. **Sub-pixels** — nao existem. Toda movimentacao e em incrementos de pixel inteiro no render final. Posicao sub-pixel e apenas logica interna (fixed-point), nunca visual.
6. **Gradientes suaves** — com 15 cores por paleta e 512 cores totais, gradientes suaves sao impossiveis. Use dithering manual de 2-3 cores ou ramp curto.
7. **Rotacao por hardware** — nao existe. Pre-renderize frames rotacionados como tiles individuais.

---

## Checklist de validacao de asset

Antes de aceitar qualquer imagem no pipeline:

- [ ] Formato PNG indexado (8-bit ou 4-bit)
- [ ] Index 0 da paleta = transparente (magenta no fonte)
- [ ] Maximo 15 cores visiveis na paleta do tile
- [ ] Todas as cores dentro do grid 9-bits (multiplos de 0x22)
- [ ] Dimensoes multiplas de 8 pixels (largura E altura)
- [ ] Bounding box sem bordas vazias desnecessarias
- [ ] Tiles duplicados ou espelhaveis identificados para reuso
- [ ] Nenhuma tecnica proibida presente (AA, alpha, baked light, sombra assada)
