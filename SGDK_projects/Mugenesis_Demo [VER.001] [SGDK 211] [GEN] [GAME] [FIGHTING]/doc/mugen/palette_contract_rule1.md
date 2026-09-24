# REGRA 1 — Contrato de paletas da engine + registro de decisao do Ken (2026-09-24)

## 1. Contrato (vale para todo personagem e cenario)

| linha | dono estatico | emprestimo declarado (janela -> restauracao) |
|---|---|---|
| PAL0 | **cenario** (BG_A + BG_B), 15 cores + transparente; o slot 0 e a cor de fundo | fundo de super, enquanto cobre a tela -> `bgfx_end`, KO e fim de luta |
| PAL1 | **lutador P1**: corpo **e** efeitos | flash de impacto por tabela de swap pre-declarada, so nesta linha (etapa 3) |
| PAL2 | **lutador P2**: corpo **e** efeitos | idem |
| PAL3 | **HUD** (barras, tempo, mensagens) | — |

- Posse estatica por padrao. Todo emprestimo esta nesta tabela, com janela e restauracao; nao ha malabarismo temporal implicito.
- Validacao no conversor: `python3 -m mugen2sgdk_forge palette-check --project <proj> --id <char>`.
  - Reprova (rc=1) personagem cujo corpo + efeitos passem de 15 slots, com dE76 <= 10 como "mesma cor".
  - Excecao so com `--waiver "<motivo>"`, que fica registrada no relatorio.

### Estado atual contra o contrato (ainda NAO migrado)
- PAL0: fundo + palco 1-8 + HUD 9-15.
- PAL3: efeitos dos dois lutadores (paleta de efeitos do P1).

A migracao comeca pela linha dos lutadores, que depende da decisao de arte da secao 2. Depois vem o HUD em PAL3 e o cenario com PAL0 inteira.

## 2. Ken nao cabe: 20 slots para 15 (medido)

| parte | slots |
|---|---|
| corpo estavel (pele, cabelo, preto, branco; iguais nas 12 variantes) | 9 |
| rampa de roupa (varia entre as 12 variantes; calibrada em 6 degraus no P2) | 6 |
| cores de efeito sem par no corpo (dE > 10), ja agrupadas | 5 |
| **total** | **20 (estoura por 5)** |

`palette-check` hoje: Ken reprova (`needed` 20, `over_by` 5). E o resultado honesto, mantido ate a decisao.

### Opcoes registradas (prioridade definida pelo usuario: ajuste artistico por agente grafico dedicado)
1. **PRIORIDADE — reautoria dos efeitos por um agente com capacidade grafica** (entende e gera imagem).
   - Alvo: os efeitos usam os 9 slots estaveis + 1 livre + no maximo 5 dedicados, sem mexer na roupa.
   - Brief na secao 4. A saida entra como `technical_candidate`; `visually_approved` exige humano.
2. Roupa 6->3 degraus + efeitos 5->3 dedicados.
   - Perde profundidade de sombra no uniforme e desfaz parte da calibracao P2.
3. Efeitos so com cores do corpo (vizinho mais proximo).
   - dE medio ponderado 8,6; 34,7% dos pixels de efeito mudam > 10 dE.
   - A cor do efeito passaria a mudar com a variante de roupa.
   - So com os 9 estaveis: dE 22,0 e 78,6% dos pixels mudam.
4. Linha de efeitos compartilhada (desvio da REGRA 1).
   - O lutador nao perde nada, mas HUD e cenario dividem PAL0 e o cenario fica com 8 cores.

## 3. Avaliacao de dimensao (pedido do usuario: CPS2 384 contra MD/Neo Geo 320)

O Ken vem do SFA2 (CPS2, 384x224). No MD (320x224) o mesmo pixel ocupa 20% a mais da largura da tela. Um ajuste pequeno de escala pode aproximar a proporcao original e ainda economizar tiles.

Medida nos 263 quadros de corpo. O redimensionamento aqui e so instrumento de medicao (vizinho mais proximo), NUNCA pixel final.

| escala | maior quadro (tiles) | soma de todos os quadros | altura max |
|---|---|---|---|
| 1:1 (hoje) | 94 | 17 902 | 126 px (56% da tela) |
| x 15/16 | -9,6% | -5,8% | 126 |
| x 7/8 | -12,8% | -10,9% | 126 |
| **x 5/6 (proporcao do CPS2)** | **-17,0%** | **-14,3%** | 126 |
| x 15/16, y 15/16 | -9,6% | -11,2% | 118 |
| x 5/6, y 15/16 | -19,1% | -19,3% | 118 |

Leitura:
- So no eixo x, 5/6 devolve a proporcao que o artista desenhou para 384 de largura e reduz ~17% o slot fixo (102 -> ~85 tiles por lutador) e ~14% a ROM de sprites.
- Mexer no y reduz presenca na tela; so vale se a leitura do golpe nao cair.
- Reamostragem automatica quebra pixel art (linhas de 1 px somem ou dobram). A escala escolhida tem de ser **redesenhada pelo agente grafico** e comparada lado a lado com o 1:1 (silhueta, leitura dos golpes, hitbox).
- Hitboxes (Clsn) escalam junto. Isso muda o alcance em jogo, e e decisao de gameplay que precisa ser declarada.

## 4. Brief para o agente grafico (reautoria)
- Entrada: sheets `res/mugen/ken/sheets/*_fx.png`, paleta de corpo (12 variantes) e esta medicao.
- Paleta alvo, linha unica de 15:
  - slots estaveis 1,2,3,4,5,6,8,11,15 (nao mudar);
  - roupa 7,9,10,12,13,14 (nao usar em efeitos: mudam por variante);
  - livres para efeito: o que sobrar (hoje 0 alem do duplicado; cabem ate 5 so se a roupa ceder, o que e decisao).
- Preservar: a leitura do hadouken (azul/branco) e das chamas do shoryuken; o contraste contra o cenario.
- Opcional, com comparacao 1:1: variante x 5/6 dos quadros de corpo, para decisao humana.
- Saida: PNG indexado + relatorio. Entra no manifesto como derivado de terceiros reautorado. `palette-check` precisa passar sem `--waiver`.
