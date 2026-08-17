# Re-autoria de `img_forge_bg_b` — alvo medido

Motivo: `audit_tile_residency.py` mede **1093 tiles unicos de 1120 brutos — 2% de deduplicacao**.
O ato 2 fica com 4% de margem de VRAM e a linha `bg_forge_set` do contrato, orcada em 640,
esta em 1397.

Isto nao e pedido de "capricho": e o unico asset da cena que impede qualquer coisa nova de
caber.

---

## O diagnostico, e por que ele contradiz a sua percepcao

Voce escreveu que a parede "continua lendo como fiada", ou seja **modular demais** aos olhos.
A medicao diz o oposto na VRAM: **98% dos tiles sao unicos**.

Ela consegue as duas coisas ao mesmo tempo — parecer repetitiva e custar como arte unica. Isso
e a assinatura de arte **composta como imagem fotografica e quantizada**, e nao autorada como
conjunto de tiles: o olho ve o padrao de fiada da forma, e a VRAM ve ruido de quantizacao que
torna cada tile ligeiramente diferente do vizinho.

A prova esta no proprio pacote: `img_forge_bg_a_props`, feito com formas mais limpas, deduplica
**73%** (304 tiles de 1120 brutos). Mesma fonte, mesmo pipeline, mesmo artista. **O problema e
de metodo de composicao, nao de estilo nem de talento.**

---

## O alvo

| Margem do ato 2 | `bg_b` maximo | Dedup necessaria |
|---|---|---|
| 20% | 818 tiles | 27% |
| **30%** | **644 tiles** | **43%** |
| 40% | 470 tiles | 58% |
| 50% | 296 tiles | 74% |

**Alvo minimo aceitavel: 644 tiles unicos (43% de dedup).** Alvo desejavel: a mesma faixa que o
`bg_a_props` ja atinge, ~300 tiles, que devolveria 50% de margem e abriria espaco para a cena
crescer.

Hoje: 1093 tiles, 2%.

---

## Como se autora um fundo como conjunto de tiles

Nao e reduzir detalhe. E decidir o vocabulario antes de compor.

1. **Defina o vocabulario primeiro.** Desenhe o conjunto de tiles da alvenaria — pedra inteira,
   meia pedra, junta horizontal, junta vertical, canto, pedra trincada, pedra faltando, tijolo
   de topo. Vinte a quarenta tiles autorais resolvem uma parede inteira.
2. **Componha a parede com esse vocabulario**, variando a **ordem** e o **flip H/V**, nao o
   pixel. Irregularidade vem do arranjo, nao de cada tile ser diferente.
3. **O flip e seu aliado**: o gate deduplica com flip H/V, entao um tile espelhado sai de graca.
   Desenhe pedras assimetricas e espelhe-as para quebrar o ritmo sem custo.
4. **O gradiente de calor nao pode ser por pixel.** Se cada fiada tem uma cor levemente
   diferente por causa do banho de luz, cada tile vira unico. Resolva a variacao de calor com
   **troca de paleta por banda de H-Int** — que a cena ja usa no ato 1 — e mantenha os tiles
   iguais entre as bandas.
5. **A faixa inferior de 48 scanlines** continua com a restricao de cisalhamento: material
   continuo, sem aresta que dependa de alinhamento horizontal.

O item 4 e provavelmente a causa principal: um fundo lavado por luz continua ganha um degrade
suave que destroi a repeticao de tile. Na arquitetura desta cena, esse degrade e trabalho do
H-Int, nao da arte.

---

## Como saber que deu certo, antes de entregar

```bash
python3 tools/sgdk_wrapper/audit_tile_residency.py --project-root "<este projeto>"
```

Procure a linha do `img_forge_bg_b`. O aviso `low_tile_dedup_ratio` some acima de 30% de dedup,
mas o alvo do contrato e 43%.

O gate tambem mostra a margem do ato 2 recalculada — e o numero que decide se a cena pode
crescer.

## O que nao muda

Direcao, paleta, lei da luz, restricao da faixa inferior: tudo como esta em
`doc/branding_v2_art_direction.md`. Isto e re-autoria de **metodo de composicao**, nao de
direcao. A leitura da parede tem que continuar sendo a mesma; o que muda e como ela e montada.

E continua valendo: nenhum pixel nasce de primitiva. Codigo monta, recorta e paletiza arte
autoral, nunca a desenha.
