# P5 — Sombra sob o personagem: memo comparativo (2026-09-23)

## Medicoes (host harness CPU x CPU, 36000 ticks; k-means nos pixels de efeito do Ken)
| medida | valor |
|---|---|
| sprites HW nas linhas do chao (y 188..207), pior caso / media | 20 / 5,9 (estimativa conservadora: celula inteira) |
| estouro de 20/linha se +2 sprites (1 sombra 32 px por lutador) | 0,20% dos ticks |
| estouro se +4 sprites (sombra 64 px por lutador) | 0,39% dos ticks |
| erro de cor dos efeitos com PAL3 15 -> 13 cores (S/H usa slots 14/15 como operadores) | 13,6 -> 19,9 (+46%) |
| deltaE roupa (P2) vs fundo, fundo normal / fundo em shadow (S/H escurece low-prio + backdrop) | 63,4 / 71,1 |

## Comparacao
| tecnica | sprites | paleta | VRAM | DMA/quadro | efeito colateral | resultado visual |
|---|---|---|---|---|---|---|
| Dither (xadrez 50%) em sprite | +1/lutador | 0 (cor escura da paleta do proprio lutador) | 4 tiles | 0 | nenhum | meia-tinta; em composite vira translucido (classico MD) |
| Flicker (sprite em quadros alternados) | +1 em media 0,5 | 0 | 4 tiles | 0 | tremulacao 30 Hz | **bloqueado pelo canon** como mascara de estouro |
| Hardware blinking (prioridade/cor alternada) | +1 | 0 | 4 tiles | CRAM/atributo por quadro | tremulacao | mesmo problema do flicker |
| Shadow/Highlight | +1/lutador (operador ainda e sprite) | -2 cores nos efeitos (+46% erro) | 4 tiles | 0 | escurece backdrop e TODOS os tiles low-priority: estagio (E4) teria de ser high-priority; muda contraste do P2 | translucido real |

## Recomendacao: DITHER em sprite (vencedora)
- Menor custo total: zero paleta, zero efeito global, sem DMA por quadro.
- S/H so vale se o estagio (E4) for projetado para ele (tiles high-priority) e se os efeitos aceitarem 13 cores:
  reavaliar no E4; hoje o custo supera o ganho.
- Estouro residual (0,20%): a sombra entra por ULTIMO na lista de sprites (maior profundidade), entao o VDP a
  descarta primeiro naquela linha, sem cortar pixels dos lutadores. Isto e prioridade deterministica, nao flicker.

## Arte (canon 8.2/17)
Nao ha sombra pronta nas artes (fightfx do SFA2 so tem poeira). A forma e DERIVADA da silhueta autoral do
personagem parado (MUGEN 0,0), achatada no chao em 32x8, como o motor MUGEN projeta sombras; o xadrez 50% e o
padrao de meia-tinta. Status: `technical_candidate` — requer aprovacao visual humana.

## Resultado (implementado)
- ROM 46a9cd65...: sombras pontilhadas visiveis sob os pes, acompanham o lutador; somem no fundo de super.
- Desempenho: 27,0% dos quadros acima do orcamento (faixa observada entre capturas desde o P4: 23-27%);
  pico 10 sprites/linha.
- Evidencia: out/mugenesis_evidence/p5_shadow/blastem-linux-20260923T224301Z-1479693.
