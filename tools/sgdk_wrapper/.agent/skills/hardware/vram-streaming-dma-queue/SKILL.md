---
name: vram-streaming-dma-queue
description: Use quando cenas Mega Drive precisarem streamar tiles, atualizar dirty regions, trocar frames grandes ou coordenar uploads DMA dentro do VBlank.
---

# VRAM Streaming DMA Queue

Transforma uploads em uma fila mensuravel com prioridade e validade por cena.

## Contrato Operacional

### Entrada minima

- resident set e layout de VRAM
- uploads de preload e por frame
- velocidade de camera/animacao
- pior quadro de sprites, scroll, audio e FX

### Saida minima

- `dma_queue_contract`
- slots de VRAM e ownership
- prioridades, bytes por frame e invalidacao
- fixtures de overflow, seam e transicao

### Passa quando

- preload, load-time DMA e DMA por frame estao separados
- pior frame cabe no VBlank com margem
- fonte de `DMA_queueDma` permanece valida ate a transferencia
- troca de cena invalida jobs do owner anterior
- fallback reduz janela, cadence ou detalhe sem corrupcao

### Handoff para proxima etapa

- entregar fila e slots a `sgdk-runtime-coder`
- entregar bytes e residency a `megadrive-vdp-budget-analyst`
- entregar seams observaveis a `emulator-vdp-evidence-curator`

## Regras

- Confirmar APIs em SGDK 2.11: `VDP_loadTileData` e `DMA_queueDma`.
- Compressao de ROM nao reduz automaticamente VRAM residente.
- Stream por janela mede mundo total e resident set simultaneo separadamente.
- DMA seguro permanece coordenado com VBlank.

## Anti-padroes

- upload grande todo frame sem budget
- ponteiro temporario enfileirado
- contar todos os assets do jogo como residentes
- rebuild visual para esconder seam estrutural
