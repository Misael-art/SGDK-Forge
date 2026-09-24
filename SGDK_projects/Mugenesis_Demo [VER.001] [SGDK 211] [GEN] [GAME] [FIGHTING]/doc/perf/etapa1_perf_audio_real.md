# Etapa 1 — Desempenho com audio real (medido)

Toda captura aqui usa BlastEm com `--audio-driver disk`. O `audio.raw` de cada uma tem ~16 MB, com pico de 32511 e 99,8% das amostras diferentes de zero.

A luta e CPU x CPU com a mesma semente. Duas capturas da mesma ROM deram numeros identicos (a emulacao e deterministica).

## Metrica honesta
A sonda so conta `over_budget` **depois** do warmup de 90 quadros. Dividir pelo total de quadros **subestimava** o problema (e nao superestimava):
- `main` bruto: 457 de 1651 quadros = 27,7%;
- `main` sobre os quadros pos-warmup: 457 de 1561 = **29,3%**.

A sonda agora exporta o denominador pos-warmup em `[30]`.

## Resultado
| ROM (sha256) | mudanca | acima do orcamento | max CPU | sprites/linha | px/linha |
|---|---|---|---|---|---|
| `46a9cd65…` (main) | — | **29,3%** (457/1561) | 158 | 10 | nao medido |
| `9ba229c7…` | sonda por diferencas + px/linha | 22,3% (308/1381) | 156 | 10 | 288 |
| `483469e9…` | sonda so nas fronteiras + frente leve do VM | 9,5% (165/1741) | 145 | 10 | 288 |
| `6bbef58a…` | pilha do VM por ponteiro | **8,5%** (153/1801) | 144 | 10 | 288 (limite 320) |

- **Captura final:** `out/mugenesis_evidence/perf_fix2/blastem-linux-20260924T013351Z-2065068/`.
- **Limites do VDP em H40:** nenhum quadro passou de 20 sprites por linha, nem de 320 px por linha.

## Diagnostico (amostragem de PC no 68000, nao no host)
O perfil por `getSubTick` (`-DMG_PROFILE`) distorce: a propria ROM de perfil fica 77% acima do orcamento.

Por isso foi criado o `-DMG_PCPROF`: um H-Int a cada 8 linhas le o PC empilhado e soma num histograma (baldes de 64 B), exportado para a SRAM em 0x2000. Tambem guarda um histograma **so dos quadros acima do orcamento**.
- Leitura: `tools/mugen2sgdk_forge/perf/read_sram_metrics.py <captura> <symbol.txt>`.
- Vies conhecido: nao amostra o vblank nem trechos com interrupcao mascarada.

Antes (ROM `b5a1895d…`, 69 369 amostras):

| simbolo | % das amostras |
|---|---|
| `VDP_waitVBlank` (ocioso) | 33,9% |
| `MG_eval` | 13,9% |
| `MDRuntimeProbe_tick` | **12,2%** |
| `SPR_update` | 3,6% |

Nos quadros acima do orcamento, depois da primeira correcao (ROM `857462a7…`, 452 quadros), `eval_full` era o maior custo, com 16%.

## Correcoes (nada visivel mudou, nenhum limiar mudou)
1. **A sonda media a si mesma.** O laco por linha custava cerca de 13 mil ciclos por quadro.
   - Agora um bitmap marca as linhas de fronteira e so elas sao varridas.
   - O pico e exato, porque a contagem so muda nas fronteiras.
   - O px/linha foi acrescentado sem custo por linha.
   - Medido: com a mesma ROM de jogo, acrescentar o px/linha ao laco antigo levou a luta a 77,8%. Nao era o audio: com `dummy` deu os mesmos 77,8%.
2. **`MG_eval` gastava cerca de 1100 ciclos por chamada**, com cerca de 15 chamadas por quadro, o mesmo que o host mede.
   - Um terco das chamadas era constante (`PUSH8 0; END`, 3,4 por tick) e pagava o prologo de 11 registros.
   - Agora uma frente leve devolve constantes e `var(n)`; o interpretador (`eval_full`, `noinline`) so roda o resto.
3. **Pilha do interpretador por ponteiro**, em vez de indice recalculado a cada acesso.

Equivalencia: o trace completo do harness do host em 7200 ticks tem o mesmo md5 (`b47cfeef…`) antes e depois. Os 39 testes passam.

## Custo do audio real
Mudo so o `PlaySnd`, na mesma base da linha 2 da tabela: 18,2% (`a6f0938c…`) contra 22,3%. O PCM custa cerca de 4 pontos. Nada foi cortado no audio.

## O que sobra (8,5%)
Os quadros acima do orcamento tem a mesma composicao do quadro medio, com mais avaliacoes de condicao: estados com 15 a 24 controladores sem portao (1000/1005/1010, 5110, 10000).

O proximo ganho real e no **compilador**: portoes exatos para mais formas de trigger, e remover no build os controladores com trigger constante-falso. Isso fica para quando houver direcionamento; esta rodada nao mexe nisso.

## Aviso para o framework
`src/system/runtime_probe.c` e copia do template canonico. O custo de cerca de 10% do laco por linha **existe em todo projeto que copiou a sonda**, e infla o `over_budget` deles.

Recomendo levar esta versao ao template, com revisao propria.
