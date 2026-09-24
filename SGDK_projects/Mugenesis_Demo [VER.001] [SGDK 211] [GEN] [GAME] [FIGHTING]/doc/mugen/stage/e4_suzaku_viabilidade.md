# E4.0 — Suzaku Castle (SSF2 Ryu): memo de viabilidade

> **Atualizacao 2026-09-24 (REGRA 1 + dieta de VRAM):** os numeros de orcamento abaixo sao do estado de ENTAO (90 tiles, 8 cores).
> - VRAM livre para cenario agora: **180 tiles**, **452** com o emprestimo do fundo de super (PR #17).
> - Paleta: pela REGRA 1, BG_A e BG_B **compartilham uma unica PAL0** (15 entradas visiveis para os dois planos juntos), nao 15 cada. O que se valida e a UNIAO das cores dos dois planos. O Suzaku bruto usa 56 cores MD no total; os planos compostos, 29 (BG_B) e 33 (BG_A), com sobreposicao.
> - Nao aplicar a escala 384->320 ao palco: a fonte ja e 320x240; o corte e vertical (240->224).
> - Reautoria: so uma faixa representativa pelo agente grafico, em paralelo, e o palco completo so depois do piloto de FX aceito e do orcamento fechado (largura 640, chao y=200, planos, tiles residentes, uploads e restauracao pos-super).

**Veredito: NO-GO para a E4.1 como "inclusao direta".** Mesmo a reducao mais agressiva medida estoura a VRAM livre da luta em 7,9x. A paleta estoura em 7x. Os caminhos de GO pedem decisao humana (secao 6).

Todos os numeros vem de `python3 -m mugen2sgdk_forge stage-measure` (saida em `suzaku_measure.json`, ao lado deste memo). A ROM medida esta citada pelo hash.

## 1. Fonte
- `rascunho/entrada_bruta/ssf2_01_ryu.zip`, sha256 `d781b8d5…`, com inventario em `imported_assets_sha256.json`.
- Rip de Dark Saviour (2002/2006) de Super Street Fighter II (Capcom). O `.def` pede "Please don't link these files".
- Uso local autorizado; redistribuicao NAO verificada. Registrado em `doc/project_hygiene_manifest.json`.
- Parser: `mugen2sgdk_forge/parsers/stage.py`, com 0 avisos no `.def` real e 9 testes (o `.def` real e fixtures de fronteira).

### Correcoes ao briefing
O briefing veio do inventario do acervo; o `.def` real diz outra coisa em quatro pontos.

| Briefing | `.def` real |
|---|---|
| ~23 secoes de BG, ~19 camadas | **10 secoes [BG]**: 5 estaticas, 1 parallax, 1 tile, 3 instancias de uma animacao |
| decisao 384->320 | nao existe: sem `localcoord` = 320x240, igual ao H40. O corte real e **vertical, 240->224** |
| bandeira animada (R2), chamas/velas (R3) | **nao existem**. A unica animacao (`Action 5`) e uma particula de 1 a 9 px que sobe 20 px |
| bounds em [StageInfo] | bounds em `[Camera]` (+-224) e `[Bound]` (40/40); `zoffset = 216` em [StageInfo] |

### Camadas medidas

| camada | papel | delta x | tamanho | cores MD | tiles unicos (com espelho) | pior tile |
|---|---|---|---|---|---|---|
| BG 0a (0,1) | ceu/nuvens, tile=1, velocity -0,25 | 0 | 480x144 | 7 | 440 | 8 |
| BG 0b (0,0) | ceu com lua, velocity -0,25 | 0 | 480x144 | 9 | 454 | 12 |
| BG 1 (1,0) | torre do castelo | 0,47 | 139x76 | 8 | 133 | 13 |
| BG 2 (2,0) | muro e cerca | 0,54 | 504x212 | 16 | 374 | 12 |
| BG 3 (3,0) | telhados laterais | 0,67 | 621x192 | 21 | 289 | **16 (> 15)** |
| BG 4a (4,0) | chao, **parallax** xscale 1->1,377 | 0,79 | 896x36 | 11 | 300 | 10 |
| BG 4b (4,1) | borda do chao | 1,10 | 894x12 | 10 | 113 | 10 |
| BG 5/5'/5'' | particula (`Action 5`, 51 quadros, 278 ticks) | 0,47 | 1..9 px | 1..4 | — | — |

- O stage inteiro usa **56 cores MD** (81 indices do SFF).
- O chao **nao e periodico** ate 448 px, entao nao da para repeti-lo na largura do plano.

## 2. Orcamento da luta hoje (lido da ROM)
ROM `main`, sha256 no `suzaku_measure.json` (`fight_rom_sha256`). Planos 64x32, mapas a partir de 0xC000.

| regiao | tiles |
|---|---|
| espaco de tiles | 1536 |
| fonte / pool de sprites (`FIGHT_SPR_VRAM`) / sistema | 96 / 600 / 16 |
| **area do usuario** | **824** |
| corpos fixos: 2 x 147 (a reserva e pelo maior sheet de EFEITO, `g760_fx`; o maior de corpo e 102) | 294 |
| fundo de super (`bgfx_730`, 1 copia para P1=P2) | 272 |
| HUD 136 + 2 retratos x 16 | 168 |
| **livre para o stage** | **90** |

## 3. Mapa de slots de CRAM, com dono no tempo

| linha | slots | dono na luta | dono temporario |
|---|---|---|---|
| PAL0 | 0 | cor de fundo | — |
| PAL0 | **1-8** | **stage (reservado; hoje vazio)** | fundo de super: 1-14 enquanto `bgfx_active` |
| PAL0 | 9-15 | HUD | fundo de super: 9-14. O HUD se esconde durante o super |
| PAL1 | 0-15 | corpo do P1 (e a barra do P1 no HUD) | flash de acerto (etapa 3, branch parado) |
| PAL2 | 0-15 | corpo do P2 (e a barra do P2) | flash de acerto |
| PAL3 | 0-15 | faiscas e efeitos dos dois lutadores | — |

- O stage tem **8 cores**. Um unico plano composto do Suzaku pede 24 a 33.
- Nao ha linha livre. Qualquer ganho de CRAM tira de lutador, FX ou HUD, e isso e decisao de direcao, nao detalhe tecnico.

## 4. Reducao para 2 planos, medida

A largura do plano e 320 + 448 x delta (a camera anda 448 px). O plano de 64 celulas mostra ate 512 px sem streaming.

| plano composto | largura | tiles unicos | cores MD |
|---|---|---|---|
| BG_B ceu+castelo+muro, delta 0,43 (maior delta que cabe em 512) | 520 | 739 | 29 |
| BG_B idem, delta 0,50 | 544 | 753 | 29 |
| BG_A telhados+chao, delta 0,67 | 624 | 673 | 32 |
| BG_A telhados+chao, delta 1,0 (1:1, como no briefing) | 768 | 540 | 33 |
| so a faixa do ceu (linhas 0-47 do BG_B) | 520 | 243 | 20 |
| so castelo+muro (linhas 48-223 do BG_B) | 520 | 496 | 29 |

- **Fiel em 2 planos:** 739 + 540 = **~1280 tiles** e ~56 cores, contra 90 tiles e 8 cores.

### Degrau seguinte, medido antes de fechar
- **S1, stage congelado em 320 px** (sem scroll, visto da camera central): BG_B 476 + BG_A 232 = **708 tiles**, com 29 + 24 cores. Ainda sao 7,9x a VRAM livre.

VRAM que da para recuperar sem perda visivel, por medir ou medida:

| recuperacao | ganho | estado |
|---|---|---|
| fundo de super carregado so durante o super (posse temporal: o stage se esconde, os tiles voltam depois; ~11 KB de DMA em 2 quadros) | +272 | calculado; precisa medir o custo de DMA na volta |
| reserva do corpo pelo maior sheet de corpo (102), nao de efeito (147) | +90 | nao verificado: os sheets `_fx` podem cair no slot fixo da parte 0 |
| pool de sprites de 600 -> pico real medido | ? | precisa medir no BlastEm |

- Com os dois primeiros: 90 + 272 + 90 = **452**. Nao cabe nem o S1 (708) sem medir o pool, e **nenhum** caso resolve a paleta.

## 5. Por feature: fica, adiada ou aproximada

| feature do .def | destino | tipo |
|---|---|---|
| ceu + lua (delta 0) | BG_B, linhas 0-47 com scroll proprio (HSCROLL por faixa de tile) | fica; a lua anda com o plano -> **aproximado** |
| nuvens `velocity -0,25` (R1) | hscroll da faixa do ceu | adiada para R1; viavel: e so a faixa 0-47 |
| torre 0,47 + muro 0,54 | BG_B com um delta unico (0,43 cabe em 512) | **aproximado**: um delta so para as duas |
| telhados 0,67 | BG_A, linhas acima do chao em delta proprio (line scroll) | fica com line scroll; com 1:1, anda 1,5x mais rapido -> **aproximado** |
| chao parallax 4a + borda 4b (R4) | BG_A, hscroll por linha de 0,79 a 1,10 | adiada para R4; e a tecnica que valida o catalogo |
| particula `Action 5` x3 com BGCtrl (R3/R5) | sprite de 1 a 9 px, 3 posicoes, 1x por ciclo de 3364 ticks | adiada; custo irrelevante; BGCtrl vira tabela de eventos, sem interpretador |
| bandeira / chamas (R2/R3 do briefing) | — | nao existem no stage |
| largura: BG_A precisa de 624 a 768 px | streaming de colunas ou plano de 128 celulas (-256 tiles de VRAM) | **decisao** |
| vertical 240->224 | corte de 8 px em cima e 8 embaixo; `zoffset` 216 -> chao em y=208 (hoje `FLOOR_Y` = 200) | **decisao**: o chao da luta desce 8 px |
| camera +-224 (mundo de 768) | hoje `STAGE_W` = 640 | **decisao**: muda a largura jogavel |
| `[Scaling]`, sombra `yscale .1`, `bgmusic` mp3 | nao se aplicam (sem escala por z; sombra propria; mp3 fora do zip) | ignorados, registrados |

Toda aproximacao acima entra no manifesto de proveniencia quando houver asset. Nesta rodada nenhum simbolo visual foi criado.

## 6. Caminhos de GO (precisam de decisao)
1. **Re-autoria do Suzaku para o MD**, com o rip como referencia (a conversao vira `technical_candidate`). Alvo medido por plano: <= 15 cores e um teto de tiles fechado com a VRAM recuperada do item 3. E o caminho do canon ("conversao automatica nao e arte").
2. **Redistribuir a CRAM**, por exemplo: HUD nas linhas dos lutadores, stage com PAL0 1-15, ou FX compartilhando linha. Cada opcao tem custo visivel e deve ser escolhida por direcao, nao pelo conversor.
3. **Enxugar a VRAM da luta** (item 4: +272, +90, pool medido). E tecnico, mensuravel e sem perda visivel. **Recomendo fazer primeiro**, porque qualquer caminho acima depende dele.

Nao cabe nenhuma ROM "direta" ate haver essas decisoes. Montar uma agora exigiria cortar cor e tile sem registro, que e exatamente o que as regras proibem.
