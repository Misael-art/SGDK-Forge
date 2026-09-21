# TDD - Shadow Dancer Revisitado

## Contexto tecnico

- SGDK: 2.11 do workspace (`sdk/sgdk-2.11`)
- Contexto: technical_demo; sem claim de release
- Regiao: NTSC como baseline; PAL ainda nao medido
- Resolucao: H40, 320x224

## Arquitetura

- Um estado de runtime com `main.c` e modulo de cache em `map_handler.c`.
- Input lido uma vez por frame com held/pressed; ordem: input, gameplay, camera, sprites, VBlank.
- Buffers do cache sao estaticos: 576 entradas de tile, lookup de 20480 tiles e cache de plano 42x32.
- Proibicoes: `float`, `double`, `malloc`, `free`, DMA imediato durante callback de mapa e API inventada.

## VDP, VRAM e DMA

- BG_A: `MAP_create` com mapa virtual; tiles de arte entram na janela de cache.
- PAL1: cenario. PAL2: player.
- Cache: 576 tiles ativos a partir de VRAM 1; o tileset e explicitamente `NONE`.
- Upload de tiles: `DMA_queueDma`, flush automatico por `SYS_doVBlankProcess`.
- A fila foi configurada para 10000 bytes; o pior caso de scroll ainda precisa de medicao no hardware/emulador.

## Gameplay

- `fix32` para posicao e velocidade.
- Colisao consulta a imagem de colisao com clamp de tile; fora do mapa e solido.
- Camera usa dead zone horizontal 140..180 e vertical 112..140, com clamp ao mapa.

## Audio e persistencia

Nao ha recurso de audio nem save no slice. Qualquer adicao exige atualizar GDD, TDD, manifestos e budget.

## Validacao

1. seletor de rota e wrapper SGDK;
2. rescomp e compilacao C com `sdk/sgdk-2.11`;
3. `validate_resources.ps1`;
4. captura BlastEm para promover `testado_em_emulador`.
