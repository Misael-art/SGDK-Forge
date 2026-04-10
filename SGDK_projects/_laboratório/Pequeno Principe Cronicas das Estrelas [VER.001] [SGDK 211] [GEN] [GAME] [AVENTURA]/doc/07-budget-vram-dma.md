# 07 - Budget VRAM e DMA

## VRAM do slice atual

- banco procedural base: `27` tiles
- marcos centrais via `rescomp`: `16` tiles
- total artistico carregado no boot: `43` tiles
- pressao de sprite em gameplay: `8` entradas SAT

Distribuicao do runtime:

- corpo do principe: `1` sprite `2x3`
- cachecol: `5` sprites `1x1`
- halo: `1` sprite `2x2`
- marco central do planeta: `1` sprite `2x2`

Isso deixa uma margem grande para:

- fontes do sistema
- tilemaps dos planos
- expansao futura com assets adicionais via `rescomp`

## DMA por frame

Estimativa de pico nas cenas:

- `B-612`: scroll por linha em 2 planos + troca curta de paleta
- `Rei`: scroll por linha + column scroll em colunas pontuais
- `Lampiao`: scroll por linha + H-Int de 6 cores
- `Deserto`: scroll por linha em bandas e travel controlado
- `Encontros`: audio curto `WAV/XGM2`, sem troca de tile por frame

Observacao:

- os `TileSet` dos marcos sao carregados no boot, nao durante o gameplay
- os encontros nao fazem stream de arte; so reutilizam tiles ja residentes

## Politica

- nao trocar tiles inteiros por frame sem necessidade
- preferir paleta e scroll para animacao de ambiente
- redraw de tilemap completo so em troca de estado ou mudanca estrutural
