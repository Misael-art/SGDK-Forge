# P3 — Memo: multiplexar os aneis do super (medido, sem implementacao)

Status: **NO-GO recomendado** — aguardando aprovacao humana. Nenhum codigo alterado.

## Estado atual (aneis = animacao 30100, grupo 8000, 17+ quadros de time 1)
Medido nos sheets gerados (`res/mugen/ken/sheets/g8000_*_fx.png`), contando tiles 8x8 nao vazios por quadro:

| sheet | quadro (px) | quadros | tiles/quadro |
|---|---|---|---|
| g8000_0 | 248x176 | 13 | 2..104 |
| g8000_1 | 248x192 | 3 | 45..51 |
| g8000_p1_0 | 248x144 | 6 | 24..107 |
| g8000_p1_1 | 232x112 | 2 | 32..42 |
| g8000_p2 | 240x232 | 6 | 24..47 |
| g8000_p3 | 56x32 | 2 | 9 |

- Pior quadro: 107 tiles, ou **3 424 B de DMA** num tick. O teto NTSC fica perto de 7,2 KB por vblank, e os corpos dos dois lutadores ainda precisam de DMA no mesmo tick.
- A VRAM vem do pool de sprites (600 tiles), sem reserva fixa: fica ocupado apenas o quadro vivo.
- Simulador (`vdp_scanline_simulator.py`), pior quadro, blocos 32x32 + 2 lutadores: **16 sprites por linha, 27 links, status ok**.
- Visto rodando: ROM P5 `46a9cd65...` (`out/mugenesis_evidence/p5_shadow`). O super roda com aneis sem estouro de linha.

## Alternativa: peca de arco autoral reutilizada ao redor da elipse
A elipse tem os raios do pior quadro (116x64 px).

| variante | pecas | pior linha | links | status do simulador | VRAM | DMA/quadro |
|---|---|---|---|---|---|---|
| peca 16x16 | 37 | **21** | 49 | **error** (>20 na linha 175) | ~4..16 tiles | 0 |
| peca 32x32 | 19 | 18 | 31 | ok, *near limit* | ~16..64 tiles | 0 |

## Leitura
1. **Ganho real:** apenas DMA e VRAM. O DMA atual cabe, e o super acontece com o jogo pausado (SuperPause), justamente quando o DMA dos corpos esta parado.
2. **Custo real:** a pressao de linha sobe (16 → 18 ou 21), e com 16x16 ja quebra o limite de 20 sprites por linha.
3. **Fidelidade:** os quadros autorais do anel mudam de espessura, forma e brilho a cada tick. Uma peca replicada vira uma elipse uniforme. Isso seria composicao procedural de arte final, que o canon veda sem aprovacao humana.
4. **CPU:** 19 a 37 `SPR_setPosition` por tick contra 1 a 4 partes hoje. O custo e baixo, mas nao e zero, num projeto que ainda tem cerca de 23–27% dos quadros acima do orcamento.

## Recomendacao
**NO-GO.** O metodo atual passa no simulador, cabe no DMA e preserva a arte. Reabrir este memo so se:
- um segundo lutador com super simultaneo estourar o DMA medido; ou
- o estagio (E4) consumir a folga de VRAM do pool.

Se isso acontecer, o plano e usar pecas 32x32 autorais (nao derivadas por maquina) e 4 quadros de rotacao, com gate de simulador abaixo de 20 por linha.

Reproducao: script de medicao no historico da sessao. Os JSON de entrada do simulador foram gerados a partir dos PNGs acima.
