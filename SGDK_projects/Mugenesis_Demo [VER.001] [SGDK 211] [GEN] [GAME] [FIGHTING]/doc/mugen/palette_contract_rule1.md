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

## 2. Ken nao cabe (medicao CORRIGIDA)

> **Correcao (parecer `doc/curation/2026_09_24/palette_art_handoff/`):** a 1a versao deste doc decodificava a palavra VDP com mascara `0xE` depois do deslocamento. O bit baixo de cada canal se perdia, e o branco maximo virava 109. Os numeros "20 slots", "dE 8,6 / 34,7%" e "5 dedicados" eram invalidos. Agora a decodificacao e `converters.sprites.vdp_rgb`, a mesma grade do conversor, com teste de vetores de hardware.

| medida EXATA | valor |
|---|---|
| indices de corpo usados | 15 de 15 |
| classes de corpo (tupla de cores do slot nas 12 variantes) | **14** = 8 estaveis + 6 de roupa |
| fusao sem perda | slots **1 e 6** iguais em toda variante; provada pixel a pixel (`remap_lossless_verified`) |
| livre apos a fusao | **1** |
| cores exatas de efeito | 11; **9** sem classe estavel igual (nenhuma dentro de dE 10) |
| necessidade exata | **23** para 15 (estoura por 8) |

`palette-check`: `status: fail`, rc=1. O `--waiver` so registra a excecao (`fail_waived`), nunca aprova.

### Orcamento realizavel (base do piloto)
**8 estaveis + 6 de roupa + 1 de efeito = 15.**
- Os efeitos precisam ser redesenhados com as 8 cores estaveis, o 1 slot recuperado e a transparencia.
- Nao existem outros slots livres.
- As estaveis sao quase todas tons quentes de pele/cabelo e escuros. Manter o hadouken azul/branco com isso e desafio de direcao de arte, nao consequencia de quantizacao.

### Opcoes (prioridade do usuario: piloto com agente grafico)
1. **PRIORIDADE — piloto de UMA familia de FX** pelo agente grafico, no orcamento 8+6+1 (secao 4).
   - Se nao atingir a leitura: devolver alternativas medidas e pedir decisao de compromisso (rampas/materiais, estetica ou contrato).
2. Roupa 6 -> menos degraus para abrir slots de efeito.
   - Perde profundidade no uniforme e desfaz parte do P2. Precisa de decisao.
3. Efeitos remapeados para as cores do corpo por maquina (corrigido):
   - com os 15 do corpo: dE medio **20,7**, **67,0%** dos pixels > 10 dE, pior 46,4; e a cor do efeito mudaria com a roupa;
   - so com as estaveis: dE **37,2**, **93,2%** > 10 dE.
   - Perda visivel: descartado como solucao automatica.
4. Linha de efeitos compartilhada (desvio da REGRA 1): HUD e cenario dividem PAL0.

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

Leitura (com o limite do parecer, F4):
- Ocupacao horizontal na tela e aspecto de exibicao sao problemas distintos. x 5/6 e uma alternativa estetica medida, nao restauracao universal de proporcao.
- **Fora desta rodada:** nao escalar corpo nem hitbox enquanto a paleta estiver aberta.
- So no eixo x, 5/6 devolve a proporcao que o artista desenhou para 384 de largura e reduz ~17% o slot fixo (102 -> ~85 tiles por lutador) e ~14% a ROM de sprites.
- Mexer no y reduz presenca na tela; so vale se a leitura do golpe nao cair.
- Reamostragem automatica quebra pixel art (linhas de 1 px somem ou dobram). A escala escolhida tem de ser **redesenhada pelo agente grafico** e comparada lado a lado com o 1:1 (silhueta, leitura dos golpes, hitbox).
- Hitboxes (Clsn) escalam junto. Isso muda o alcance em jogo, e e decisao de gameplay que precisa ser declarada.

## 4. Brief para o agente grafico (corrigido; o pacote completo vai no handoff do piloto)
- Tarefa: piloto de **uma** familia de FX. Nao mexer em corpo, escala nem hitbox.
- Paleta alvo (linha do lutador, 15 slots):
  - estaveis 1,2,3,4,5,8,11,15 (o slot 6 e fundido no 1, sem perda);
  - roupa 7,9,10,12,13,14 (proibidos em efeito: mudam por variante);
  - **1** slot de efeito (o antigo 6);
  - nao inventar cores livres.
- Preservar funcao, trajetoria, ponto de origem, limites de quadro e timing do AIR.
- Entregar duas alternativas de direcao + um ciclo completo da escolhida, em tamanho nativo, com fundo claro e escuro.
- A saida e candidata: a indexacao e a conversao passam pelo pipeline tecnico; `visually_approved` exige revisao humana.
- `palette-check` deve passar sem `--waiver` depois da integracao.
