# Design (Treino): SFF v1.01 -> SGDK Viewer (Showdown)

## Critério de sucesso

- Extrai `showdown.sff` (SFF v1.01) para um conjunto estruturado de sprites (pixels + paleta + axis) sem perdas.
- Reconstrói o stage a partir de `showdown.def` (camadas BG0/BG1/BG2(anim)/BG3) e gera uma sequência visualmente coerente.
- Gera um tileset 8×8 com deduplicação e detecção de flip H/V, mais tilemaps com flags (flip, prioridade, sub-paleta).
- Produz tabelas de ponteiros para reduzir draw calls no viewer SGDK (batch por plane/atributos).
- Entrega ROM de prova rodando no BlastEm (screenshot obrigatório) com a cena renderizada e a animação do BG2 tocando.

## Entradas e formatos

- `showdown.sff`: ElecbyteSpr, versão 1.01, subheaders 32 bytes, payload PCX; pode conter sprites “linked”.
- `showdown.def`: define sprites por `spriteno = group,index` e animações via `[Begin action N]`.

## Pipeline (fases)

1. Fixture
   - Copiar entradas para `rascunho/inputs/` e registrar hashes em `rascunho/inputs_manifest.json`.
2. Extração SFF
   - Ler header 512 bytes e iterar subfiles a partir de `first_offset`.
   - Para cada sprite: capturar `group/index`, `axis`, `data_len`, `linked_index`, e paleta (individual ou compartilhada).
   - Exportar:
     - `work/extracted_pcx/{group}_{index}.pcx`
     - `work/meta/sprites.json` (metadados necessários para reconstrução)
3. Reconstrução por DEF
   - Parsear `[BG x]` e `[Begin action N]`.
   - Construir uma timeline de frames e “composites” por camada.
   - Exportar reconstruções para revisão:
     - `work/reconstructed_layers/frame_####.png`
4. Otimização visual (8×8)
   - Quantizar/validar por sub-paleta (<=16 cores por tile, uma sub-paleta por tile).
   - Quebrar em tiles 8×8 e gerar assinaturas:
     - identidade exata
     - H-flip
     - V-flip
     - HV-flip
   - Produzir:
     - tiles únicos (dicionário)
     - tilemap por layer/frame com flags
     - relatórios de savings e violações
5. Saída SGDK
   - Gerar recursos consumíveis e tabelas de ponteiros para batches por plano.
   - Viewer SGDK:
     - Plane B: fundo distante
     - Plane A: cenário principal
     - Animação: BG2 (action 2) via atualização no VBlank
6. Evidência
   - Build ok + ROM gerada.
   - BlastEm: screenshot e logs/dumps pertinentes em `evidence/`.

## Artefatos e gates

- `analysis/tile_stats.json`: total/unique, savings por flip, top padrões.
- `analysis/palette_violations.json`: tiles fora do contrato.
- `analysis/reconstruction_diff.png`: comparação (entrada vs reconstruído) quando aplicável.
- `evidence/blastem_screenshot.png`: obrigatório para status `testado_em_emulador`.

## Não-objetivos (neste treino)

- H-Int para gradiente dinâmico.
- Sistema completo de level design/editing.
- Promoção automática para canônico.

