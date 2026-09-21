# Shadow Dancer Revisitado - notas do experimento

O projeto e um technical demo da base de mapa/locomocao de um beat 'em up para Mega Drive. O codigo original veio de um experimento de mapa virtual; a conversao atual esta documentada em `doc/` e usa SGDK 2.11.

- cache ativo: 576 tiles;
- lookup de mapa: ate 20480 tiles;
- cache de plano: 42 x 32 entradas;
- uploads de tiles: `DMA_queueDma` para VBlank;
- tilesets e mapas: sem compressao;
- movimento: `fix32`, sem float/double;
- camera: dead zone e clamp;
- fase inicial: mapa 1.

Fonte historica: https://github.com/spacebruce/SGDK-Experiments/tree/bigtilemap/Big-tile-map
